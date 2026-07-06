"""FR-1 audio perception node (speech emotion recognition).

Unlike video (where FER+ is a well-known, de facto standard ONNX model),
there is no single standard pretrained speech-emotion-recognition ONNX
model, so this node's feature extraction is parameterized rather than
hardcoded: `n_mfcc` and `expected_frames` must match whatever model is
supplied via `model_path`, and `labels` must match its output classes
in order. See docs/models.md for a concrete starting point.

Buffers incoming interfaces/AudioChunk samples and runs inference once
`window_sec` worth of audio has accumulated, then clears the buffer
(non-overlapping windows - simpler than a sliding window, and no
functional requirement here calls for the extra complexity).
"""

import os

import librosa
import numpy as np
import onnxruntime as ort
import rclpy
from interfaces.msg import AudioChunk, EmotionState
from rclpy.node import Node

from perception.audit import audit_log
from perception.logits import argmax_label, softmax

DEFAULT_LABELS = [
    "neutral",
    "calm",
    "happy",
    "sad",
    "angry",
    "fearful",
    "disgust",
    "surprised",
]


class AudioEmotionNode(Node):
    def __init__(self) -> None:
        super().__init__("audio_emotion_node")

        self.declare_parameter("audio_topic", "audio_raw")
        self.declare_parameter("output_topic", "perception/audio/emotion_state")
        self.declare_parameter("model_path", "")
        self.declare_parameter("window_sec", 3.0)
        self.declare_parameter("n_mfcc", 40)
        self.declare_parameter("expected_frames", 130)
        self.declare_parameter("labels", DEFAULT_LABELS)

        model_path = self.get_parameter("model_path").get_parameter_value().string_value
        if not model_path or not os.path.isfile(model_path):
            raise RuntimeError(
                "audio_emotion_node requires the 'model_path' parameter to point at "
                "an existing speech-emotion-recognition ONNX model file, with "
                "n_mfcc/expected_frames/labels parameters matching it. See "
                f"docs/models.md. Got: {model_path!r}"
            )

        self._session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
        self._input_name = self._session.get_inputs()[0].name
        self._output_name = self._session.get_outputs()[0].name

        self._window_sec = self.get_parameter("window_sec").get_parameter_value().double_value
        self._n_mfcc = self.get_parameter("n_mfcc").get_parameter_value().integer_value
        self._expected_frames = (
            self.get_parameter("expected_frames").get_parameter_value().integer_value
        )
        self._labels = (
            self.get_parameter("labels").get_parameter_value().string_array_value
            or DEFAULT_LABELS
        )

        self._buffer: list = []
        self._sample_rate: int = 0

        output_topic = self.get_parameter("output_topic").get_parameter_value().string_value
        audio_topic = self.get_parameter("audio_topic").get_parameter_value().string_value

        self._publisher = self.create_publisher(EmotionState, output_topic, 10)
        self._subscription = self.create_subscription(
            AudioChunk, audio_topic, self._on_audio, 10
        )
        self.get_logger().info(
            f"audio_emotion_node: '{audio_topic}' -> '{output_topic}' (model: {model_path})"
        )

    def _on_audio(self, msg: AudioChunk) -> None:
        self._sample_rate = msg.sample_rate
        self._buffer.extend(msg.samples)

        window_len = int(self._window_sec * self._sample_rate)
        if window_len <= 0 or len(self._buffer) < window_len:
            return

        window = self._buffer[:window_len]
        self._buffer = self._buffer[window_len:]
        self._infer(window)

    def _infer(self, samples: list) -> None:
        y = np.array(samples, dtype=np.float32) / 32768.0
        mfcc = librosa.feature.mfcc(y=y, sr=self._sample_rate, n_mfcc=self._n_mfcc)

        frames = mfcc.shape[1]
        if frames < self._expected_frames:
            mfcc = np.pad(mfcc, ((0, 0), (0, self._expected_frames - frames)))
        else:
            mfcc = mfcc[:, : self._expected_frames]

        tensor = mfcc.astype(np.float32).reshape(1, 1, self._n_mfcc, self._expected_frames)

        logits = self._session.run([self._output_name], {self._input_name: tensor})[0][0]
        probs = softmax(logits.tolist())
        label, confidence = argmax_label(probs, list(self._labels))

        out = EmotionState()
        out.stamp = self.get_clock().now().to_msg()
        out.label = label
        out.confidence = float(confidence)
        self._publisher.publish(out)
        audit_log(
            self.get_logger(),
            "raw_emotion",
            modality="audio",
            label=label,
            confidence=float(confidence),
        )


def main(args: list = None) -> None:
    rclpy.init(args=args)
    node = AudioEmotionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
