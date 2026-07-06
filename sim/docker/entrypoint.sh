#!/bin/bash
set -e

source /opt/ros/jazzy/setup.sh
source /workspace/install/setup.bash

# turtlebot3_gazebo's stock launch file may try to start a GUI client
# (gzclient) regardless of whether one is wanted. On a headless host
# (no DISPLAY passed in - the default, see docker-compose.yml), that
# would otherwise fail to connect to an X server. Xvfb gives it a
# virtual display to render into instead, so headless `docker compose
# up` doesn't depend on guessing turtlebot3_gazebo's exact headless
# launch argument (unverified in this repo - see README's "Known
# limitation"). If DISPLAY is already set (real X11 forwarding
# enabled), this is skipped and the real display is used untouched.
if [ -z "$DISPLAY" ]; then
    exec xvfb-run --auto-servernum --server-args="-screen 0 1280x1024x24" "$@"
else
    exec "$@"
fi
