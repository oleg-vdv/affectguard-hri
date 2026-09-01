"""Phase 2: fusion arbitration tests.

Pure-Python, no rclpy/numpy required - runs with plain pytest.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "perception"))

from perception.fusion_logic import Reading, fuse


def test_both_fresh_agree_averages_confidence():
    video = Reading(label="happiness", confidence=0.8, stamp_sec=10.0)
    audio = Reading(label="happiness", confidence=0.6, stamp_sec=10.0)
    fused = fuse(video, audio, now_sec=10.0, max_age_sec=2.0)
    assert fused.label == "happiness"
    assert fused.confidence == 0.7


def test_disagreement_picks_higher_confidence():
    video = Reading(label="anger", confidence=0.9, stamp_sec=10.0)
    audio = Reading(label="neutral", confidence=0.4, stamp_sec=10.0)
    fused = fuse(video, audio, now_sec=10.0, max_age_sec=2.0)
    assert fused.label == "anger"
    assert fused.confidence == 0.9


def test_stale_modality_is_dropped():
    video = Reading(label="sadness", confidence=0.7, stamp_sec=0.0)
    audio = Reading(label="calm", confidence=0.5, stamp_sec=10.0)
    fused = fuse(video, audio, now_sec=10.0, max_age_sec=2.0)
    assert fused.label == "calm"


def test_only_one_modality_present():
    video = Reading(label="fear", confidence=0.55, stamp_sec=10.0)
    fused = fuse(video, None, now_sec=10.0, max_age_sec=2.0)
    assert fused.label == "fear"
    assert fused.confidence == 0.55


def test_both_missing_returns_none():
    assert fuse(None, None, now_sec=10.0, max_age_sec=2.0) is None


def test_both_stale_returns_none():
    video = Reading(label="fear", confidence=0.55, stamp_sec=0.0)
    audio = Reading(label="sad", confidence=0.55, stamp_sec=0.0)
    assert fuse(video, audio, now_sec=10.0, max_age_sec=2.0) is None
