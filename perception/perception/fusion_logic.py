"""Pure fusion arbitration logic, decoupled from rclpy/ROS messages.

fusion_node.py wraps this in the ROS glue (subscriptions, EmotionState
messages, wall-clock time). Kept dependency-free so it can be unit
tested without a ROS 2 environment installed (see
tests/test_fusion_logic.py).
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Reading:
    label: str
    confidence: float
    stamp_sec: float


def _is_fresh(reading: Optional[Reading], now_sec: float, max_age_sec: float) -> bool:
    if reading is None:
        return False
    return (now_sec - reading.stamp_sec) <= max_age_sec


def fuse(
    video: Optional[Reading],
    audio: Optional[Reading],
    now_sec: float,
    max_age_sec: float = 2.0,
) -> Optional[Reading]:
    """Combine the latest video/audio readings with a simple confidence rule.

    - Stale or missing modalities (older than max_age_sec) are dropped.
    - If only one modality is fresh, it passes through unchanged.
    - If both are fresh and agree on the label, the fused confidence is
      their average (agreement should increase, not just average out,
      but we don't want to overclaim beyond what a simple rule
      justifies, so max_age_sec is offered as the outlier-elimination
      mechanism and this stays a plain average).
    - If both are fresh and disagree, the higher-confidence reading
      wins outright: this is a rule-based MVP fusion, not a learned
      one (per the spec's tech stack table, ML fusion is optional
      future work).
    - If neither is fresh, returns None (no fused state to publish).
    """
    video_fresh = video if _is_fresh(video, now_sec, max_age_sec) else None
    audio_fresh = audio if _is_fresh(audio, now_sec, max_age_sec) else None

    if video_fresh is None and audio_fresh is None:
        return None
    if video_fresh is None:
        return audio_fresh
    if audio_fresh is None:
        return video_fresh

    if video_fresh.label == audio_fresh.label:
        return Reading(
            label=video_fresh.label,
            confidence=(video_fresh.confidence + audio_fresh.confidence) / 2.0,
            stamp_sec=max(video_fresh.stamp_sec, audio_fresh.stamp_sec),
        )

    return max(video_fresh, audio_fresh, key=lambda r: r.confidence)
