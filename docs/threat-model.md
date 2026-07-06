# Threat model

Covers the three threats NFR-3 requires at minimum. Each entry: attack
surface, assumed attacker capability, and the concrete mitigation
actually implemented (not just planned) as of Phase 4.

## 1. Unauthorized access to the raw video/audio stream

**Attack surface:** `camera/image_raw` (sensor_msgs/Image) and
`audio_raw` (interfaces/AudioChunk) — the two topics carrying
unprocessed biometric data, consumed only by `video_emotion_node` and
`audio_emotion_node` respectively.

**Assumed attacker capability:** network access to the DDS multicast/
unicast traffic between nodes (e.g. another process on the same host or
LAN segment), without valid SROS2 credentials.

**Mitigation:**
- DDS-Security (SROS2) authenticates every participant by X.509
  certificate and encrypts topic traffic between them (NFR-2). An
  attacker without a valid enclave key/cert from
  `security/keystore/` cannot join the secured DDS domain at all, let
  alone subscribe to `camera/image_raw` or `audio_raw`.
- Even with a stolen credential for an unrelated enclave (say,
  `/sim_backend`), `security/policies/policy.xml` gives that enclave no
  `subscribe="ALLOW"` entry for either raw stream — only
  `video_emotion_node`'s and `audio_emotion_node`'s own enclaves can
  read them.
- Residual risk: this only protects the DDS transport. It does not
  cover access to a video/audio *file* if a dataset is stored on disk
  for testing (e.g. a rosbag) — that's ordinary filesystem
  permissions, out of scope for SROS2 and not addressed here.

## 2. Adversarial attack on the emotion classifier

**Attack surface:** crafted input to `video_emotion_node` or
`audio_emotion_node` (an adversarial image/audio sample) designed to
force a specific `EmotionState.label`/`confidence` output and, through
it, provoke an unwanted policy-engine reaction (e.g. forcing a
"stressed" reading to make the robot slow to a crawl, or a false-calm
reading to suppress an appropriate slowdown).

**Assumed attacker capability:** control over what the camera/
microphone captures (e.g. holding up a printed adversarial pattern, or
playing a crafted audio clip) — not network/DDS access, which is
covered by threat 1.

**Mitigation:**
- The safety envelope (`core/safety_envelope.py`) is the actual
  backstop here, and it is deliberately *not* a function of the
  emotion label at all: `MAX_LINEAR_SPEED`/`MAX_ANGULAR_SPEED` clamp
  every proposed command regardless of what emotion triggered it, and
  a `critical`-tagged `current_task` zeroes movement outright. A
  successful adversarial attack can make the robot appear to
  "misjudge" the person's state, but it cannot make the robot exceed
  the speed envelope or interrupt a critical task — those two
  properties hold for every possible `(label, confidence)` pair, not
  just the ones an honest classifier would produce. This is exactly
  what `tests/test_safety_envelope.py`'s "extreme input" tests check:
  an extreme/adversarial-shaped proposal still gets clamped.
- The `logged_at`/`fused_label`/`enforced_linear_x` fields in
  `policy_engine`'s audit log (FR-4) mean an adversarial-triggered
  behavior change is visible after the fact even if it isn't prevented
  in the moment — `proposed_linear_x` vs. `enforced_linear_x` in the
  same log line shows whether the envelope actually intervened.
- Residual risk: nothing here detects or rejects the adversarial input
  itself (no input-sanitization/anomaly-detection layer on the ONNX
  inference path) — that would be a real mitigation to add before any
  deployment beyond this pet-project's scope, not something the
  current MVP claims to do.

## 3. Compromised perception node sending commands directly to actuation

**Attack surface:** a compromised `video_emotion_node`,
`audio_emotion_node`, or `fusion_node` attempting to publish directly
to `core/cmd`, `/cmd_vel`, or `face_indicator`, bypassing
`policy_engine` (and therefore bypassing the safety envelope entirely).

**Assumed attacker capability:** full code execution within one
perception node's process (e.g. via a dependency-confusion or
malicious-model-file compromise of `video_emotion_node`), but no
separate access to another enclave's private key.

**Mitigation:** this is the one NFR-4 is written for, and it's enforced
two ways, not one:
- **Structurally, in `policy.xml`:** none of the three perception
  enclaves (`/perception/video_emotion_node`,
  `/perception/audio_emotion_node`, `/perception/fusion_node`) has a
  `<topics publish="ALLOW">` entry naming `core/cmd`, `/cmd_vel`, or
  `face_indicator` at all. Even a fully compromised perception process
  attempting to publish on those topics gets rejected by DDS-Security
  at the middleware level, before the message reaches any subscriber —
  this is enforced by the RTPS/DDS permissions check, not by
  `sim_backend`'s or `policy_engine`'s own code choosing to ignore it.
- **Defense in depth, in code:** even without SROS2 enabled (Phases
  1-3, or SROS2 disabled at runtime), no perception node's source
  imports a `Twist`/`BehaviorCommand` publisher at all — there is no
  code path to call, compromised or not, that would let a perception
  node publish to an actuation topic, because the publisher object
  simply doesn't exist in that process.
- Residual risk: a compromised node *can* still publish garbage on the
  topics it *is* allowed to write (e.g. `fusion_node` spamming a fake
  high-stress `fused_emotion_state`) — that's threat 2's territory
  (the safety envelope bounds the consequences), not this one's.
