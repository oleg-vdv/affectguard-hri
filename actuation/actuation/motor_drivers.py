"""Pluggable motor driver abstraction for the Phase 5 hardware backend.

The spec doesn't pin a specific chassis/motor controller for the
optional Raspberry Pi 5 / Jetson Orin Nano port, so this stays a thin,
swappable interface: implement MotorDriver for your actual wiring and
select it via hardware_backend's `driver` parameter.
LoggingMotorDriver (the default) touches no hardware at all and is
safe to run anywhere, including a plain dev machine with no robot
attached.
"""


def differential_drive_wheel_power(
    linear_x: float, angular_z: float, wheel_base_m: float, max_speed_mps: float
) -> tuple:
    """Standard differential-drive kinematics, converted to a [-1, 1]
    motor-power fraction. Pure function (no gpiozero/hardware
    dependency) so it's unit-testable without a Pi - see
    tests/test_motor_drivers.py.
    """
    left_mps = linear_x - angular_z * wheel_base_m / 2.0
    right_mps = linear_x + angular_z * wheel_base_m / 2.0

    left_power = max(-1.0, min(1.0, left_mps / max_speed_mps))
    right_power = max(-1.0, min(1.0, right_mps / max_speed_mps))
    return left_power, right_power


class MotorDriver:
    def drive(self, linear_x: float, angular_z: float) -> None:
        raise NotImplementedError

    def stop(self) -> None:
        self.drive(0.0, 0.0)


class LoggingMotorDriver(MotorDriver):
    """Default: logs the command it would send, touches no hardware."""

    def __init__(self, logger) -> None:
        self._logger = logger

    def drive(self, linear_x: float, angular_z: float) -> None:
        self._logger.info(
            f"[hw driver: log-only] linear_x={linear_x:.3f} angular_z={angular_z:.3f}"
        )


class GPIODifferentialDriveMotorDriver(MotorDriver):
    """Example real implementation for a two-motor differential-drive
    chassis on Raspberry Pi, using gpiozero.Robot.

    The default pin numbers (see hardware_backend's ROS parameters) are
    placeholders, not a wiring recommendation - set left_motor_pins/
    right_motor_pins to match your actual H-bridge/motor driver board.
    Speed is converted from m/s to gpiozero's [-1, 1] motor-power
    fraction via max_speed_mps, which should be calibrated to your
    chassis's real top speed; it is deliberately not derived from
    core.safety_envelope.MAX_LINEAR_SPEED, which is a separate,
    conservative software bound applied upstream in the policy engine,
    not a hardware calibration constant.

    Not applicable to Jetson Orin Nano - gpiozero is Raspberry-Pi
    specific. A Jetson port would implement this same MotorDriver
    interface with Jetson.GPIO or a PWM motor-controller library
    instead; that hasn't been written here since it depends on motor
    controller hardware the spec doesn't specify.
    """

    def __init__(
        self,
        left_pins,
        right_pins,
        wheel_base_m: float,
        max_speed_mps: float,
        logger,
    ) -> None:
        try:
            from gpiozero import Robot
        except ImportError as exc:
            raise RuntimeError(
                "GPIODifferentialDriveMotorDriver requires gpiozero, which is "
                "Raspberry-Pi-specific and not installed here. Install it on "
                "the target Pi, or implement your own MotorDriver subclass for "
                "your actual hardware (see docs/hardware.md)."
            ) from exc

        self._robot = Robot(left=tuple(left_pins), right=tuple(right_pins))
        self._wheel_base_m = wheel_base_m
        self._max_speed_mps = max_speed_mps
        self._logger = logger

    def drive(self, linear_x: float, angular_z: float) -> None:
        self._robot.value = differential_drive_wheel_power(
            linear_x, angular_z, self._wheel_base_m, self._max_speed_mps
        )
