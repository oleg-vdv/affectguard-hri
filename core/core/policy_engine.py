"""Phase 3 policy engine (FR-2): replaces the Phase 1 policy_engine_stub.

Subscribes to fused_emotion_state and current_task, runs the rule
engine (core.rule_engine) to propose a behavior, then unconditionally
runs that proposal through the safety envelope (core.safety_envelope)
before publishing on core/cmd. The envelope check is not optional and
not skippable from here - there is no code path in this node that
publishes a movement command without going through enforce() first.
"""

import rclpy
from interfaces.msg import BehaviorCommand, CurrentTask, EmotionState
from rclpy.node import Node

from core.rule_engine import decide
from core.safety_envelope import Movement, enforce

DEFAULT_PERIOD_SEC = 0.5


class PolicyEngine(Node):
    def __init__(self) -> None:
        super().__init__("policy_engine")

        self.declare_parameter("emotion_topic", "fused_emotion_state")
        self.declare_parameter("task_topic", "current_task")
        self.declare_parameter("output_topic", "core/cmd")
        self.declare_parameter("period_sec", DEFAULT_PERIOD_SEC)

        emotion_topic = self.get_parameter("emotion_topic").get_parameter_value().string_value
        task_topic = self.get_parameter("task_topic").get_parameter_value().string_value
        output_topic = self.get_parameter("output_topic").get_parameter_value().string_value
        period_sec = self.get_parameter("period_sec").get_parameter_value().double_value

        # Sensible defaults until the first real message arrives: a
        # neutral emotional state and a non-critical task, so the robot
        # starts in its calmest, most interruptible mode rather than
        # assuming stress or criticality it hasn't observed yet.
        self._latest_label = "neutral"
        self._task_critical = False

        self._publisher = self.create_publisher(BehaviorCommand, output_topic, 10)
        self.create_subscription(EmotionState, emotion_topic, self._on_emotion, 10)
        self.create_subscription(CurrentTask, task_topic, self._on_task, 10)
        self._timer = self.create_timer(period_sec, self._on_timer)

        self.get_logger().info(
            f"policy_engine: '{emotion_topic}' + '{task_topic}' -> '{output_topic}'"
        )

    def _on_emotion(self, msg: EmotionState) -> None:
        self._latest_label = msg.label

    def _on_task(self, msg: CurrentTask) -> None:
        self._task_critical = msg.critical

    def _on_timer(self) -> None:
        behavior = decide(self._latest_label)
        movement = enforce(
            Movement(linear_x=behavior.linear_x, angular_z=behavior.angular_z),
            task_is_critical=self._task_critical,
        )

        out = BehaviorCommand()
        out.stamp = self.get_clock().now().to_msg()
        out.movement.linear.x = movement.linear_x
        out.movement.angular.z = movement.angular_z
        out.voice_text = behavior.voice_text
        out.voice_volume = behavior.voice_volume
        out.face_pattern = behavior.face_pattern
        self._publisher.publish(out)


def main(args: list = None) -> None:
    rclpy.init(args=args)
    node = PolicyEngine()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
