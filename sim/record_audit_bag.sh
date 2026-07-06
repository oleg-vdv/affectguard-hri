#!/bin/bash
# FR-4: rosbag2 recording of the full perception -> policy -> actuation
# trail, alongside the structured JSON Lines audit_log() calls each
# node already makes to its own ROS logger. Run inside the sim
# container, e.g.:
#   docker compose exec sim /workspace/sim/record_audit_bag.sh
set -euo pipefail

OUT_DIR="${1:-audit_bag_$(date +%Y%m%d_%H%M%S)}"

exec ros2 bag record -o "$OUT_DIR" \
    /perception/video/emotion_state \
    /perception/audio/emotion_state \
    /fused_emotion_state \
    /current_task \
    /core/cmd \
    /cmd_vel \
    /face_indicator
