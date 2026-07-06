# tests/

Integration-style tests that span multiple nodes/packages live here
(package-local unit tests, if any, live under e.g. `core/test/`). These
need a sourced ROS 2 workspace (`rclpy` installed), so they run inside
the Docker image / a colcon workspace, e.g.:

```
docker compose run --rm sim bash -c "source install/setup.bash && python3 -m pytest /workspace/../tests"
```

They are not yet wired into CI (see the TODO in
`.github/workflows/ci.yml`) — CI currently only lints and builds the
image.

- `test_policy_engine_stub.py` — Phase 1: checks the stub node publishes
  the expected `core/cmd` message on its timer.
- Phase 3 adds the safety-envelope test required by the acceptance
  criteria (section 8 of the spec): a test showing the policy engine
  refuses to emit a command that violates the envelope even under an
  "extreme" input.
