"""Phase 3 acceptance criterion: safety envelope covered by an automated
test showing refusal to execute an unsafe command, including an
"extreme" input.

Pure-Python, no rclpy required - runs with plain pytest.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "core"))

from core.safety_envelope import (  # noqa: E402
    MAX_ANGULAR_SPEED,
    MAX_LINEAR_SPEED,
    Movement,
    enforce,
)


def test_extreme_linear_speed_is_clamped():
    extreme = Movement(linear_x=1000.0, angular_z=0.0)
    result = enforce(extreme, task_is_critical=False)
    assert result.linear_x == MAX_LINEAR_SPEED


def test_extreme_negative_linear_speed_is_clamped():
    extreme = Movement(linear_x=-1000.0, angular_z=0.0)
    result = enforce(extreme, task_is_critical=False)
    assert result.linear_x == -MAX_LINEAR_SPEED


def test_extreme_angular_speed_is_clamped():
    extreme = Movement(linear_x=0.0, angular_z=999.0)
    result = enforce(extreme, task_is_critical=False)
    assert result.angular_z == MAX_ANGULAR_SPEED


def test_within_envelope_passes_through_unchanged():
    safe = Movement(linear_x=0.1, angular_z=0.2)
    result = enforce(safe, task_is_critical=False)
    assert result == safe


def test_critical_task_zeroes_extreme_command():
    extreme = Movement(linear_x=1000.0, angular_z=999.0)
    result = enforce(extreme, task_is_critical=True)
    assert result.linear_x == 0.0
    assert result.angular_z == 0.0


def test_critical_task_zeroes_even_a_safe_command():
    safe = Movement(linear_x=0.05, angular_z=0.05)
    result = enforce(safe, task_is_critical=True)
    assert result.linear_x == 0.0
    assert result.angular_z == 0.0
