#!/bin/bash
set -e

source /opt/ros/jazzy/setup.sh
source /workspace/install/setup.bash

# turtlebot3_gazebo's stock launch file may try to start a GUI client
# (gzclient) regardless of whether one is wanted. On a headless host
# (no DISPLAY passed in - the default, see docker-compose.yml), that
# would otherwise fail to connect to an X server. Start a virtual
# display directly instead of via xvfb-run: Xvfb itself was confirmed
# to start fine, but xvfb-run's own wrapper script was observed (on a
# real headless server) to hang indefinitely without ever exec'ing the
# wrapped command - root cause not chased down further, the wrapper is
# just not used. If DISPLAY is already set (real X11 forwarding
# enabled), this is skipped and the real display is used untouched.
if [ -z "$DISPLAY" ]; then
    Xvfb :99 -screen 0 1280x1024x24 -nolisten tcp &
    export DISPLAY=:99
    sleep 2
fi

exec "$@"
