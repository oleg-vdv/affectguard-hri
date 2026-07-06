"""Rule-based policy (FR-2): fused emotion label -> behavior command.

Pure Python, no rclpy dependency (see tests/test_rule_engine.py). The
output here is a *proposal* - core/policy_engine.py always runs it
through safety_envelope.enforce() before publishing, so nothing in this
module needs to reason about safety limits itself.

Label vocabulary note: perception/'s video and audio models don't share
one label set (FER+'s 8 classes vs. whatever the audio model uses -
see docs/models.md). Rather than force perception to agree on a single
vocabulary, this module maps *any* recognized label from either set
down to one of three canonical stress levels, and falls back to
"medium" (a middle-ground response, neither the fastest nor the most
cautious) for anything unrecognized rather than guessing.
"""

from dataclasses import dataclass

BASE_LINEAR_SPEED = 0.15  # m/s, before the stress-level scale factor

STRESS_LEVEL_BY_LABEL = {
    "neutral": "low",
    "calm": "low",
    "happiness": "low",
    "happy": "low",
    "surprise": "medium",
    "surprised": "medium",
    "sadness": "medium",
    "sad": "medium",
    "disgust": "medium",
    "contempt": "medium",
    "anger": "high",
    "angry": "high",
    "fear": "high",
    "fearful": "high",
}
DEFAULT_STRESS_LEVEL = "medium"

SPEED_SCALE_BY_LEVEL = {"low": 1.0, "medium": 0.7, "high": 0.3}
FACE_PATTERN_BY_LEVEL = {"low": "neutral", "medium": "attentive", "high": "concerned"}
VOICE_VOLUME_BY_LEVEL = {"low": 0.6, "medium": 0.5, "high": 0.3}
VOICE_TEXT_BY_LEVEL = {
    "low": "",
    "medium": "",
    "high": "I notice you seem stressed, slowing down.",
}


@dataclass(frozen=True)
class Behavior:
    linear_x: float
    angular_z: float
    voice_text: str
    voice_volume: float
    face_pattern: str


def stress_level(label: str) -> str:
    return STRESS_LEVEL_BY_LABEL.get(label, DEFAULT_STRESS_LEVEL)


def decide(label: str) -> Behavior:
    level = stress_level(label)
    return Behavior(
        linear_x=BASE_LINEAR_SPEED * SPEED_SCALE_BY_LEVEL[level],
        angular_z=0.0,
        voice_text=VOICE_TEXT_BY_LEVEL[level],
        voice_volume=VOICE_VOLUME_BY_LEVEL[level],
        face_pattern=FACE_PATTERN_BY_LEVEL[level],
    )
