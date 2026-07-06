"""The safety envelope (FR-2): the one thing the rule engine cannot override.

Pure Python, no rclpy dependency, so it can be unit tested without a
ROS 2 environment (see tests/test_safety_envelope.py) - this is the
piece the Phase 3 acceptance criteria calls out specifically ("safety
envelope covered by at least one automated test showing refusal to
execute an unsafe command").

The limits below are project-defined conservative caps for the pet-
project MVP, not a specific chassis's datasheet limits - the spec
doesn't pin an exact number, only that a cap must exist and be
unconditionally enforced.
"""

from dataclasses import dataclass

MAX_LINEAR_SPEED = 0.2  # m/s
MAX_ANGULAR_SPEED = 1.0  # rad/s


@dataclass(frozen=True)
class Movement:
    linear_x: float
    angular_z: float


def enforce(movement: Movement, task_is_critical: bool) -> Movement:
    """Clamp to the speed envelope; zero out entirely during a critical task.

    task_is_critical=True means "do not let any emotion-driven behavior
    change interrupt what the robot is currently doing" - the envelope
    refuses to publish a movement override at all in that case,
    regardless of what the rule engine proposed.
    """
    if task_is_critical:
        return Movement(linear_x=0.0, angular_z=0.0)

    clamped_linear = max(-MAX_LINEAR_SPEED, min(MAX_LINEAR_SPEED, movement.linear_x))
    clamped_angular = max(-MAX_ANGULAR_SPEED, min(MAX_ANGULAR_SPEED, movement.angular_z))
    return Movement(linear_x=clamped_linear, angular_z=clamped_angular)
