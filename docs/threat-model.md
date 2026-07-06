# Threat model

**Status: not written yet.** Per the roadmap (README, section "Roadmap"),
the threat model is Phase 4 work, done alongside SROS2 and the audit
log — that's deliberate: describing mitigations for a security layer
that doesn't exist yet would be guesswork, not a threat model.

NFR-3 requires this document to cover, at minimum, three threats once
Phase 4 lands:

- [ ] Unauthorized access to the raw video/audio stream (biometric data
      privacy).
- [ ] Adversarial attack on the emotion classifier (crafted input that
      provokes a false policy-engine trigger).
- [ ] Compromise of a perception node attempting to send commands
      directly to the actuation layer, bypassing the policy engine.

Each will need: the attack surface it targets, the assumed attacker
capability, and the concrete mitigation implemented in `security/`
(SROS2 access-control policy, encryption, etc.) — verified against the
running system, not just described.
