"""Phase 5: differential-drive kinematics tests.

Pure-Python, no gpiozero/rclpy required - this is what makes
GPIODifferentialDriveMotorDriver's actual math testable without a
Raspberry Pi.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "actuation"))

from actuation.motor_drivers import differential_drive_wheel_power  # noqa: E402


def test_straight_forward_drives_both_wheels_equally():
    left, right = differential_drive_wheel_power(
        linear_x=0.15, angular_z=0.0, wheel_base_m=0.16, max_speed_mps=0.3
    )
    assert left == right
    assert left == 0.5


def test_pure_rotation_drives_wheels_in_opposite_directions():
    left, right = differential_drive_wheel_power(
        linear_x=0.0, angular_z=2.0, wheel_base_m=0.16, max_speed_mps=0.3
    )
    assert left < 0
    assert right > 0
    assert left == -right


def test_extreme_speed_request_is_clamped_to_full_power():
    left, right = differential_drive_wheel_power(
        linear_x=1000.0, angular_z=0.0, wheel_base_m=0.16, max_speed_mps=0.3
    )
    assert left == 1.0
    assert right == 1.0


def test_extreme_negative_speed_is_clamped():
    left, right = differential_drive_wheel_power(
        linear_x=-1000.0, angular_z=0.0, wheel_base_m=0.16, max_speed_mps=0.3
    )
    assert left == -1.0
    assert right == -1.0


def test_zero_command_stops_both_wheels():
    left, right = differential_drive_wheel_power(
        linear_x=0.0, angular_z=0.0, wheel_base_m=0.16, max_speed_mps=0.3
    )
    assert left == 0.0
    assert right == 0.0
