# Phase 5 (optional): real-hardware port

Target platforms per the spec: Raspberry Pi 5 (8GB) or Jetson Orin
Nano. Neither the spec nor this repo pins a specific chassis, motor
controller, or wiring — that's a real per-build decision the spec
deliberately left open, so `actuation/hardware_backend.py` stays a
thin, swappable interface instead of guessing at hardware nobody has
specified.

## What's actually implemented

- `actuation/motor_drivers.py`: a `MotorDriver` abstract interface,
  a `LoggingMotorDriver` default (logs the command it would send,
  touches no hardware — safe to run anywhere), and one concrete
  example, `GPIODifferentialDriveMotorDriver`, for a two-motor
  differential-drive chassis on Raspberry Pi using `gpiozero.Robot`.
- `actuation/hardware_backend.py`: same `core/cmd` -> `BehaviorCommand`
  interface as `sim_backend` (FR-3's "same topic interface, different
  node implementation"). Selects a driver via the `driver` ROS
  parameter (`log` default, or `gpiozero`). Voice is log-only by
  default, or `pyttsx3` (offline, cross-platform TTS) if installed and
  selected via `voice_backend:=pyttsx3`. Face pattern republishes on
  `face_indicator`, same as sim — no display hardware is assumed.
- `sim/launch/affectguard_sim.launch.py`'s `backend:=hardware` argument
  runs `hardware_backend` instead of `sim_backend` and skips the
  Gazebo/turtlebot3 world — the roadmap's Phase 5 criterion is that the
  *same launch file* works on real hardware, not a separate one.

## What you have to supply

1. **A chassis and motor controller.** `GPIODifferentialDriveMotorDriver`
   assumes two motors, each driven by a pin pair `gpiozero.Robot`
   understands (a common H-bridge setup) — if your controller is
   different (e.g. an I2C PWM HAT, a CAN-bus controller, Jetson.GPIO
   instead of gpiozero), implement your own `MotorDriver` subclass; the
   interface is one method (`drive(linear_x, angular_z)`).
2. **Pin numbers and calibration**, via a ROS 2 parameters YAML file
   (not launch CLI arguments — these are per-robot constants you set
   once, not something you'd vary run to run):

   ```yaml
   /hardware_backend:
     ros__parameters:
       driver: gpiozero
       left_motor_pins: [17, 27]
       right_motor_pins: [22, 23]
       wheel_base_m: 0.16          # distance between wheels, meters
       max_speed_mps: 0.3          # your chassis's real top speed
   ```

   Run with `ros2 launch ... backend:=hardware --params-file your_robot.yaml`.
   `max_speed_mps` is a hardware calibration constant, not the same
   thing as `core.safety_envelope.MAX_LINEAR_SPEED` (a separate,
   conservative software bound applied upstream in the policy engine —
   see `docs/architecture.md`).
3. **A real camera/microphone driver node** publishing
   `sensor_msgs/Image` / `interfaces/AudioChunk` on whatever topics you
   pass as `image_topic`/`audio_topic` — perception nodes don't
   distinguish a real camera from a rosbag replay (Phase 2), so nothing
   there needs to change for real hardware.

## Jetson Orin Nano

`gpiozero` is Raspberry-Pi-specific. A Jetson port needs its own
`MotorDriver` subclass (e.g. via `Jetson.GPIO` or a PWM
motor-controller library) — not written here, since it depends on
motor-controller hardware the spec doesn't specify, and guessing at
wiring for hardware nobody has would be worse than leaving the
extension point documented instead.

## Not verified

There is no physical robot in the environment that wrote this (same
limitation as the rest of this repo's Docker/Gazebo/SROS2 work — see
the root README). `hardware_backend`'s log-only default has no
hardware dependency and needs nothing to "work" in that sense; the
`gpiozero` path is a documented reference implementation, not one
that's been run against a real motor.
