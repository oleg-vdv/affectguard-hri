# Architecture

See the diagram and summary in the [root README](../README.md#architecture-5-layers)
for the current, canonical version of the 5-layer diagram — it's kept in
one place to avoid the two drifting apart.

## Layers

1. **Perception** (Phase 2) — one node per modality (video, audio), each
   publishing only an `emotion_state` (label + confidence + timestamp);
   a fusion node combines them into `fused_emotion_state`. Perception
   nodes have no subscription or publish access to actuation topics —
   this is a hard requirement (NFR-4), enforced by SROS2 access-control
   policy from Phase 4 on, not just a code-review convention.
2. **Policy engine / arbitration** (Phase 3) — subscribes to
   `fused_emotion_state` and `current_task`; rule-based on MVP. Wraps a
   separate, immutable safety envelope: the envelope can veto or clamp
   any command the rules produce (e.g., max speed, no interrupting
   `critical`-tagged tasks), and this check cannot be bypassed by the
   rule layer itself.
3. **Actuation** — Phase 1 ships the Gazebo sim backend
   (`actuation/sim_backend`), which is the only node forwarding commands
   to `/cmd_vel`. A real-hardware backend (Phase 5) implements the same
   `core/cmd` -> device interface for Raspberry Pi 5 / Jetson Orin Nano.
4. **Security** (Phase 4) — SROS2: X.509 certificates per node,
   encrypted DDS topic traffic between perception and policy engine,
   and access-control policies that make layer 1 -> layer 3 direct access
   technically impossible, not just discouraged.
5. **Logging/audit** — every state transition (raw emotion -> fused state
   -> policy decision -> actuation command) is logged with a timestamp
   in structured JSON, plus `rosbag2` recording of the topics, so a full
   decision trace can be replayed and audited (FR-4).

## Status (through Phase 3)

Layers 1, 2, 3 and 5 have real implementations; layer 4 (SROS2) is
Phase 4. `core/policy_engine` subscribes to `fused_emotion_state` and
`current_task`, runs `core/rule_engine.decide()` (a fused emotion
label -> movement/voice/face proposal), and unconditionally passes the
result through `core/safety_envelope.enforce()` before publishing on
`core/cmd` — there is no code path in `policy_engine.py` that skips
this. `enforce()` and `decide()` are both plain Python with no rclpy
dependency, specifically so they're unit-testable without a ROS 2
environment (`tests/test_safety_envelope.py`,
`tests/test_rule_engine.py`; same pattern as perception's
`fusion_logic.py`). The topic boundary between "policy" and
"actuation" (`core/cmd` vs `/cmd_vel`) that Phase 1 established is what
Phase 4 turns into an enforced SROS2 access-control policy.
