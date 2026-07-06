"""Gazebo sim backend for the actuation layer.

Bridges the policy engine's BehaviorCommand (core/cmd) onto the
simulated robot's concrete outputs: movement -> /cmd_vel, plus MVP
stand-ins for the other two FR-3 sim-backend duties (voice, face):
voice_text is logged as if spoken through TTS, and face_pattern is
republished on a small String topic as the "текстовый/иконочный
индикатор" the spec calls for in Phase 1 MVP - a full 3D face model is
an explicitly allowed later upgrade, not required here.

This is the only node allowed to write to /cmd_vel: perception and
policy nodes never touch actuation topics directly (NFR-4), they only
ever publish to core/cmd, which this node translates for the concrete
backend (simulation here, real hardware in the optional Phase 5
backend).

/cmd_vel is published as geometry_msgs/TwistStamped, not plain Twist:
confirmed on a real run that turtlebot3_gazebo/ros_gz_bridge on Jazzy
expects TwistStamped there (`ros2 topic echo /cmd_vel` reported two
incompatible types on the topic until this was fixed - a real, verified
fact now, not a guess). core/cmd itself still carries a plain
geometry_msgs/Twist (see interfaces/msg/BehaviorCommand.msg) - wrapping
it in a stamped header is exactly this translation layer's job, not a
reason to change the internal policy<->actuation interface.
"""

import rclpy
from geometry_msgs.msg import TwistStamped
from interfaces.msg import BehaviorCommand
from rclpy.node import Node
from std_msgs.msg import String

from actuation.audit import audit_log

DEFAULT_INPUT_TOPIC = "core/cmd"
DEFAULT_CMD_VEL_TOPIC = "/cmd_vel"
DEFAULT_FACE_TOPIC = "face_indicator"


class SimBackend(Node):
    def __init__(self) -> None:
        super().__init__("sim_backend")

        self.declare_parameter("input_topic", DEFAULT_INPUT_TOPIC)
        self.declare_parameter("cmd_vel_topic", DEFAULT_CMD_VEL_TOPIC)
        self.declare_parameter("face_topic", DEFAULT_FACE_TOPIC)

        input_topic = self.get_parameter("input_topic").get_parameter_value().string_value
        cmd_vel_topic = self.get_parameter("cmd_vel_topic").get_parameter_value().string_value
        face_topic = self.get_parameter("face_topic").get_parameter_value().string_value

        self._cmd_vel_publisher = self.create_publisher(TwistStamped, cmd_vel_topic, 10)
        self._face_publisher = self.create_publisher(String, face_topic, 10)
        self._subscription = self.create_subscription(
            BehaviorCommand, input_topic, self._on_cmd, 10
        )
        self.get_logger().info(
            f"sim_backend: '{input_topic}' -> '{cmd_vel_topic}' (TwistStamped) "
            f"+ '{face_topic}' (+ TTS log)"
        )

    def _on_cmd(self, msg: BehaviorCommand) -> None:
        stamped = TwistStamped()
        stamped.header.stamp = self.get_clock().now().to_msg()
        stamped.twist = msg.movement
        self._cmd_vel_publisher.publish(stamped)

        if msg.voice_text:
            self.get_logger().info(
                f"[sim TTS] (volume={msg.voice_volume:.2f}) \"{msg.voice_text}\""
            )

        face = String()
        face.data = msg.face_pattern
        self._face_publisher.publish(face)

        audit_log(
            self.get_logger(),
            "actuation_command",
            linear_x=msg.movement.linear.x,
            angular_z=msg.movement.angular.z,
            voice_text=msg.voice_text,
            face_pattern=msg.face_pattern,
        )


def main(args: list = None) -> None:
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
