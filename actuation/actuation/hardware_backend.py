"""Phase 5 (optional): real-hardware actuation backend.

Same core/cmd -> BehaviorCommand interface as actuation/sim_backend.py
(per FR-3, "тот же топик-интерфейс, другая реализация ноды"), so
sim/launch/affectguard_sim.launch.py can select this node instead of
sim_backend via the `backend:=hardware` launch argument without
touching anything upstream of core/cmd. Movement goes through the
pluggable MotorDriver abstraction (actuation/motor_drivers.py) instead
of Gazebo's /cmd_vel, since there's no simulated robot to drive here.

Not run against real hardware - there's no physical robot in the
environment that wrote this (see docs/hardware.md for what's verified
vs. best-effort, same pattern as the rest of this repo's Docker/SROS2
work).
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from actuation.audit import audit_log
from actuation.motor_drivers import GPIODifferentialDriveMotorDriver, LoggingMotorDriver
from interfaces.msg import BehaviorCommand

DEFAULT_INPUT_TOPIC = "core/cmd"
DEFAULT_FACE_TOPIC = "face_indicator"


class HardwareBackend(Node):
    def __init__(self) -> None:
        super().__init__("hardware_backend")

        self.declare_parameter("input_topic", DEFAULT_INPUT_TOPIC)
        self.declare_parameter("face_topic", DEFAULT_FACE_TOPIC)
        self.declare_parameter("driver", "log")
        self.declare_parameter("left_motor_pins", [17, 27])
        self.declare_parameter("right_motor_pins", [22, 23])
        self.declare_parameter("wheel_base_m", 0.16)
        self.declare_parameter("max_speed_mps", 0.3)
        self.declare_parameter("voice_backend", "log")

        driver_name = self.get_parameter("driver").get_parameter_value().string_value
        if driver_name == "gpiozero":
            left_pins = list(
                self.get_parameter("left_motor_pins").get_parameter_value().integer_array_value
            )
            right_pins = list(
                self.get_parameter("right_motor_pins").get_parameter_value().integer_array_value
            )
            wheel_base_m = self.get_parameter("wheel_base_m").get_parameter_value().double_value
            max_speed_mps = (
                self.get_parameter("max_speed_mps").get_parameter_value().double_value
            )
            self._motor_driver = GPIODifferentialDriveMotorDriver(
                left_pins, right_pins, wheel_base_m, max_speed_mps, self.get_logger()
            )
        else:
            self._motor_driver = LoggingMotorDriver(self.get_logger())

        self._voice_backend = (
            self.get_parameter("voice_backend").get_parameter_value().string_value
        )
        self._tts_engine = None
        if self._voice_backend == "pyttsx3":
            try:
                import pyttsx3

                self._tts_engine = pyttsx3.init()
            except ImportError:
                self.get_logger().warning(
                    "voice_backend=pyttsx3 requested but pyttsx3 isn't installed; "
                    "falling back to log-only voice"
                )
                self._voice_backend = "log"

        input_topic = self.get_parameter("input_topic").get_parameter_value().string_value
        face_topic = self.get_parameter("face_topic").get_parameter_value().string_value

        self._face_publisher = self.create_publisher(String, face_topic, 10)
        self.create_subscription(BehaviorCommand, input_topic, self._on_cmd, 10)
        self.get_logger().info(
            f"hardware_backend: '{input_topic}' -> "
            f"driver={driver_name}, voice={self._voice_backend}"
        )

    def _on_cmd(self, msg: BehaviorCommand) -> None:
        self._motor_driver.drive(msg.movement.linear.x, msg.movement.angular.z)

        if msg.voice_text:
            if self._voice_backend == "pyttsx3" and self._tts_engine is not None:
                self._tts_engine.say(msg.voice_text)
                self._tts_engine.runAndWait()
            else:
                self.get_logger().info(
                    f"[hw TTS log-only] (volume={msg.voice_volume:.2f}) \"{msg.voice_text}\""
                )

        face = String()
        face.data = msg.face_pattern
        self._face_publisher.publish(face)

        audit_log(
            self.get_logger(),
            "actuation_command",
            backend="hardware",
            linear_x=msg.movement.linear.x,
            angular_z=msg.movement.angular.z,
            voice_text=msg.voice_text,
            face_pattern=msg.face_pattern,
        )


def main(args: list | None = None) -> None:
    rclpy.init(args=args)
    node = HardwareBackend()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
