"""Phase 1 placeholder for the policy engine (core/ package).

Real policy logic (fused_emotion_state + current_task -> behavior, subject
to a safety envelope) lands in Phase 3. This stub only proves the
core -> actuation topic contract: it publishes a fixed, low-speed
geometry_msgs/Twist on a timer so the rest of the launch stack (sim
backend, Gazebo, turtlebot3) can be wired up and verified end-to-end
before any perception or policy code exists.
"""

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node

DEFAULT_TOPIC = "core/cmd"
DEFAULT_PERIOD_SEC = 0.5
DEFAULT_LINEAR_X = 0.15


class PolicyEngineStub(Node):
    def __init__(self) -> None:
        super().__init__("policy_engine_stub")

        self.declare_parameter("topic", DEFAULT_TOPIC)
        self.declare_parameter("period_sec", DEFAULT_PERIOD_SEC)
        self.declare_parameter("linear_x", DEFAULT_LINEAR_X)

        topic = self.get_parameter("topic").get_parameter_value().string_value
        period_sec = self.get_parameter("period_sec").get_parameter_value().double_value
        self._linear_x = self.get_parameter("linear_x").get_parameter_value().double_value

        self._publisher = self.create_publisher(Twist, topic, 10)
        self._timer = self.create_timer(period_sec, self._on_timer)
        self.get_logger().info(
            f"policy_engine_stub publishing on '{topic}' every {period_sec}s "
            f"(linear_x={self._linear_x})"
        )

    def _on_timer(self) -> None:
        msg = Twist()
        msg.linear.x = self._linear_x
        self._publisher.publish(msg)


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = PolicyEngineStub()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
