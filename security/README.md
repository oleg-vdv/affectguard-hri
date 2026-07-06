# security/

Phase 4: SROS2 (DDS-Security) keystore generation and access-control
policy, implementing NFR-2 (authenticated, encrypted inter-node
transport) and NFR-4 (perception technically unable to reach actuation
topics — see `policies/policy.xml`'s comments for exactly how).

- `policies/policy.xml` — the access-control policy: one enclave per
  node, plus a `/test_cli` debug enclave for the manual `ros2 topic
  pub/echo` commands in the root README. The property that matters for
  NFR-4 is structural, not just careful writing: no perception enclave
  has *any* permission entry for `core/cmd`, `/cmd_vel`, or
  `face_indicator`.
- `generate_keystore.sh` — creates the keystore and, per enclave, a
  key/cert and a `permissions.p7s` derived from `policy.xml`. Keystore
  output (`security/keystore/`) is gitignored — it's generated key
  material, not source.

## Enabling it

```
docker compose exec sim /workspace/security/generate_keystore.sh
docker compose run --rm sim ros2 launch /workspace/launch/affectguard_sim.launch.py \
    enable_security:=true
```

Each node in the launch file gets `ROS_SECURITY_ENCLAVE_OVERRIDE` set to
its own enclave path unconditionally; `ROS_SECURITY_ENABLE` is what
actually turns SROS2 on, gated by the `enable_security` launch argument
(default `false`, so the plain `docker compose up` path keeps working
without a keystore — same reasoning as `enable_perception` in Phase 2).

Once enabled, plain unauthenticated `ros2 topic pub`/`echo` from a shell
can no longer reach the secured domain — that's the point. Authenticate
as the `/test_cli` enclave to run the manual verification commands from
the root README under security. Open a shell in the container first
(`docker compose exec` doesn't go through the image's ROS-sourcing
ENTRYPOINT, hence `ros-env-exec`):

```
docker compose exec sim ros-env-exec bash
```

Then, inside that shell:

```
export ROS_SECURITY_ENABLE=true
export ROS_SECURITY_STRATEGY=Enforce
export ROS_SECURITY_KEYSTORE=/workspace/security/keystore
export ROS_SECURITY_ENCLAVE_OVERRIDE=/test_cli
ros2 topic pub /fused_emotion_state interfaces/msg/EmotionState "{label: 'anger', confidence: 0.9}" --once
```

## What's verified and what isn't

This was authored without a running ROS 2 / SROS2 toolchain in the
environment that wrote it (no `ros2 security` CLI, no Docker daemon —
same limitation noted in the root README and ADR 0001). Two specific
risks worth knowing about before relying on this:

1. **`policy.xml`'s exact schema** is written from memory of the SROS2
   access-control XSD, not validated against it. `ros2 security
   create_permission` (called by `generate_keystore.sh`) validates
   against the real schema and fails loudly on a mismatch — that's
   expected to be a small, mechanical fix, not a silent gap.
2. **RMW choice**: the Dockerfile now runs on Fast-DDS (rclpy's
   default) rather than Cyclone DDS, because Fast-DDS is the more
   consistently documented DDS-Security pairing for ROS 2 tutorials.
   Cyclone DDS does have a security plugin too, but pairing it with
   SROS2 here is unverified, so Fast-DDS was the safer default.

What *is* structurally guaranteed regardless of the above two risks:
the perception enclaves in `policy.xml` simply have no permission
entries naming `core/cmd`, `/cmd_vel`, or `face_indicator` — fixing any
XSD mistake elsewhere in the file doesn't change that fact, since it's
an absence, not a misconfigured rule.
