"""Gazebo sim backend for the actuation layer.

Bridges the abstract `core/cmd` topic (published by core/, see
policy_engine_stub) onto the simulated robot's `/cmd_vel`. This is the
only node allowed to write to `/cmd_vel`: perception and policy nodes
never touch actuation topics directly (NFR-4), they only ever publish to
`core/cmd`, which this node translates for the concrete backend
(simulation here, real hardware in the optional Phase 5 backend).
"""

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node

DEFAULT_INPUT_TOPIC = "core/cmd"
DEFAULT_OUTPUT_TOPIC = "/cmd_vel"


class SimBackend(Node):
    def __init__(self) -> None:
        super().__init__("sim_backend")

        self.declare_parameter("input_topic", DEFAULT_INPUT_TOPIC)
        self.declare_parameter("output_topic", DEFAULT_OUTPUT_TOPIC)

        input_topic = self.get_parameter("input_topic").get_parameter_value().string_value
        output_topic = self.get_parameter("output_topic").get_parameter_value().string_value

        self._publisher = self.create_publisher(Twist, output_topic, 10)
        self._subscription = self.create_subscription(
            Twist, input_topic, self._on_cmd, 10
        )
        self.get_logger().info(f"sim_backend bridging '{input_topic}' -> '{output_topic}'")

    def _on_cmd(self, msg: Twist) -> None:
        self._publisher.publish(msg)


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = SimBackend()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
