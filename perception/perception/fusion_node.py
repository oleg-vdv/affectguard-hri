"""FR-1 fusion node: combines perception/video and perception/audio into
fused_emotion_state.

Thin ROS wrapper around perception.fusion_logic.fuse - see that module
for the actual arbitration rule and tests/test_fusion_logic.py for its
test coverage (runnable without ROS/rclpy installed).
"""

import rclpy
from interfaces.msg import EmotionState
from rclpy.node import Node

from perception.fusion_logic import Reading, fuse


def _to_reading(msg: EmotionState) -> Reading:
    stamp_sec = msg.stamp.sec + msg.stamp.nanosec * 1e-9
    return Reading(label=msg.label, confidence=msg.confidence, stamp_sec=stamp_sec)


def _to_msg(reading: Reading, node: Node) -> EmotionState:
    out = EmotionState()
    out.stamp = node.get_clock().now().to_msg()
    out.label = reading.label
    out.confidence = reading.confidence
    return out


class FusionNode(Node):
    def __init__(self) -> None:
        super().__init__("fusion_node")

        self.declare_parameter("video_topic", "perception/video/emotion_state")
        self.declare_parameter("audio_topic", "perception/audio/emotion_state")
        self.declare_parameter("output_topic", "fused_emotion_state")
        self.declare_parameter("max_age_sec", 2.0)

        self._max_age_sec = self.get_parameter("max_age_sec").get_parameter_value().double_value
        self._latest_video: Reading = None
        self._latest_audio: Reading = None

        video_topic = self.get_parameter("video_topic").get_parameter_value().string_value
        audio_topic = self.get_parameter("audio_topic").get_parameter_value().string_value
        output_topic = self.get_parameter("output_topic").get_parameter_value().string_value

        self._publisher = self.create_publisher(EmotionState, output_topic, 10)
        self.create_subscription(EmotionState, video_topic, self._on_video, 10)
        self.create_subscription(EmotionState, audio_topic, self._on_audio, 10)
        self.get_logger().info(
            f"fusion_node: '{video_topic}' + '{audio_topic}' -> '{output_topic}'"
        )

    def _on_video(self, msg: EmotionState) -> None:
        self._latest_video = _to_reading(msg)
        self._publish_fused()

    def _on_audio(self, msg: EmotionState) -> None:
        self._latest_audio = _to_reading(msg)
        self._publish_fused()

    def _publish_fused(self) -> None:
        now_sec = self.get_clock().now().nanoseconds * 1e-9
        fused = fuse(self._latest_video, self._latest_audio, now_sec, self._max_age_sec)
        if fused is not None:
            self._publisher.publish(_to_msg(fused, self))


def main(args: list = None) -> None:
    rclpy.init(args=args)
    node = FusionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
