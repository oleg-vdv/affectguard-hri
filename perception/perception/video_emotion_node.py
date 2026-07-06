"""FR-1 video perception node.

Subscribes to a sensor_msgs/Image stream (a real camera driver node or
`ros2 bag play` of a recorded dataset publish the same message type, so
this node doesn't care which is feeding it - matching the spec's "веб-
камера или rosbag с датасетом" requirement without an if/else on the
source). Runs face detection, then a facial-emotion ONNX model, and
publishes an interfaces/EmotionState.

Preprocessing (grayscale, resize to 64x64, no pixel-value rescaling)
and the label table match the FER+ (emotion-ferplus) model published in
the ONNX Model Zoo - see docs/models.md for where to get a compatible
.onnx file. This node does not ship any model weights; `model_path`
must point at one, or the node refuses to start.
"""

import os

import cv2
import numpy as np
import onnxruntime as ort
import rclpy
from cv_bridge import CvBridge
from interfaces.msg import EmotionState
from rclpy.node import Node
from sensor_msgs.msg import Image

from perception.audit import audit_log
from perception.logits import argmax_label, softmax

FER_PLUS_LABELS = [
    "neutral",
    "happiness",
    "surprise",
    "sadness",
    "anger",
    "disgust",
    "fear",
    "contempt",
]


class VideoEmotionNode(Node):
    def __init__(self) -> None:
        super().__init__("video_emotion_node")

        self.declare_parameter("image_topic", "camera/image_raw")
        self.declare_parameter("output_topic", "perception/video/emotion_state")
        self.declare_parameter("model_path", "")

        model_path = self.get_parameter("model_path").get_parameter_value().string_value
        if not model_path or not os.path.isfile(model_path):
            raise RuntimeError(
                "video_emotion_node requires the 'model_path' parameter to point at "
                "an existing FER+-compatible ONNX model file. See docs/models.md "
                f"for where to get one. Got: {model_path!r}"
            )

        self._session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
        self._input_name = self._session.get_inputs()[0].name
        self._output_name = self._session.get_outputs()[0].name

        self._face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self._bridge = CvBridge()

        output_topic = self.get_parameter("output_topic").get_parameter_value().string_value
        image_topic = self.get_parameter("image_topic").get_parameter_value().string_value

        self._publisher = self.create_publisher(EmotionState, output_topic, 10)
        self._subscription = self.create_subscription(
            Image, image_topic, self._on_image, 10
        )
        self.get_logger().info(
            f"video_emotion_node: '{image_topic}' -> '{output_topic}' (model: {model_path})"
        )

    def _on_image(self, msg: Image) -> None:
        frame = self._bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self._face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        if len(faces) == 0:
            self.get_logger().debug("no face detected in frame, skipping")
            return

        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
        face = cv2.resize(gray[y : y + h, x : x + w], (64, 64))
        tensor = face.astype(np.float32).reshape(1, 1, 64, 64)

        logits = self._session.run([self._output_name], {self._input_name: tensor})[0][0]
        probs = softmax(logits.tolist())
        label, confidence = argmax_label(probs, FER_PLUS_LABELS)

        out = EmotionState()
        out.stamp = self.get_clock().now().to_msg()
        out.label = label
        out.confidence = float(confidence)
        self._publisher.publish(out)
        audit_log(
            self.get_logger(),
            "raw_emotion",
            modality="video",
            label=label,
            confidence=float(confidence),
        )


def main(args: list = None) -> None:
    rclpy.init(args=args)
    node = VideoEmotionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
