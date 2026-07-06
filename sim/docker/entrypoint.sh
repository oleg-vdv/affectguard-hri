#!/bin/bash
set -e

source /opt/ros/jazzy/setup.sh
source /workspace/install/setup.bash

exec "$@"
