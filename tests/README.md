# tests/

Pure-Python unit tests for the logic that doesn't need a ROS 2
environment to exercise: perception fusion arbitration, the rule
engine, and the safety envelope. Each ROS node (fusion_node,
policy_engine, ...) is a thin wrapper around one of these modules -
see the corresponding `*_logic.py` / `rule_engine.py` /
`safety_envelope.py` files for what's actually being tested.

Run with `pytest tests/` from the repo root.

- `test_fusion_logic.py` (Phase 2) — perception's video/audio fusion
  rule: staleness handling, agreement vs. conflict, missing modalities.
- `test_safety_envelope.py` (Phase 3) — the acceptance-criteria test:
  proves the safety envelope clamps an extreme movement command and
  zeroes it entirely during a critical task, regardless of what the
  rule engine proposed.
- `test_rule_engine.py` (Phase 3) — the emotion-label -> stress-level
  -> behavior mapping, including the "unrecognized label" fallback.
- `test_motor_drivers.py` (Phase 5) — the differential-drive kinematics
  used by the optional real-hardware backend's gpiozero driver:
  straight/rotation/stop cases and extreme-speed clamping. No
  gpiozero/GPIO dependency, so it runs the same everywhere the other
  three do.

These four files are wired into CI (`.github/workflows/ci.yml`) since
they have no ROS/onnxruntime/opencv/gpiozero dependency. Anything that does
need a sourced ROS 2 workspace (rclpy, onnxruntime, ...) is exercised
inside the Docker image instead, e.g.:

```
docker compose run --rm sim bash -c "source install/setup.bash && python3 -m pytest /workspace/../tests"
```

That full-stack run (headless Gazebo + real node graph) is still the
TODO noted in `ci.yml` — not run automatically yet.
