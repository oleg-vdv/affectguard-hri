"""Phase 3: rule engine unit tests. Pure-Python, no rclpy required."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "core"))

from core.rule_engine import BASE_LINEAR_SPEED, decide, stress_level


def test_calm_labels_map_to_low_stress():
    assert stress_level("neutral") == "low"
    assert stress_level("happiness") == "low"


def test_negative_high_arousal_labels_map_to_high_stress():
    assert stress_level("anger") == "high"
    assert stress_level("fear") == "high"


def test_unknown_label_defaults_to_medium_not_low():
    assert stress_level("some_unrecognized_label") == "medium"


def test_higher_stress_means_slower_and_quieter():
    calm = decide("neutral")
    stressed = decide("anger")
    assert stressed.linear_x < calm.linear_x
    assert stressed.voice_volume < calm.voice_volume
    assert stressed.face_pattern != calm.face_pattern


def test_decide_never_exceeds_base_speed():
    for label in ["neutral", "happiness", "anger", "fear", "unknown"]:
        assert decide(label).linear_x <= BASE_LINEAR_SPEED
