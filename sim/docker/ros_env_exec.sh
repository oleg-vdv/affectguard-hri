#!/bin/bash
# `docker compose exec` bypasses the image ENTRYPOINT entirely, so the
# ROS 2 environment entrypoint.sh sources for the main launch process
# (PID 1) isn't there for ad-hoc exec sessions - plain
# `docker compose exec sim ros2 ...` fails with "ros2: executable file
# not found in $PATH". Wrap any command with this instead:
#   docker compose exec sim ros-env-exec ros2 topic echo /cmd_vel
set -e

source /opt/ros/jazzy/setup.sh
source /workspace/install/setup.bash

exec "$@"
