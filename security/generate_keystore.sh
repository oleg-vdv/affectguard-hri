#!/bin/bash
# NFR-2/NFR-4: generate an SROS2 keystore + per-enclave keys/certs and
# derive DDS-Security permissions from policies/policy.xml. Run inside
# a container/environment with `ros2 security` available (part of the
# sim image's ROS 2 install), e.g.:
#   docker compose exec sim /workspace/security/generate_keystore.sh
#
# Not run/verified in the environment that authored this script - no
# ROS 2 install was available there (see the README's "Known
# limitation" note). `ros2 security create_permission` validates
# policies/policy.xml against the real SROS2 XSD and will fail loudly
# on any schema mistake, which is the intended way to catch one.
set -euo pipefail

# Self-sourcing: `docker compose exec` doesn't go through the image's
# ENTRYPOINT (which sources these for the main launch process), so
# `ros2` wouldn't otherwise be on PATH here either. Harmless if already
# sourced.
if [ -f /opt/ros/jazzy/setup.sh ]; then
    # shellcheck disable=SC1091
    source /opt/ros/jazzy/setup.sh
    # shellcheck disable=SC1091
    source /workspace/install/setup.bash
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KEYSTORE_DIR="${1:-$SCRIPT_DIR/keystore}"
POLICY_FILE="$SCRIPT_DIR/policies/policy.xml"

ENCLAVES=(
    "/perception/video_emotion_node"
    "/perception/audio_emotion_node"
    "/perception/fusion_node"
    "/policy_engine"
    "/actuation_backend"
    "/test_cli"
)

if [ ! -d "$KEYSTORE_DIR" ]; then
    echo "Creating keystore at $KEYSTORE_DIR"
    ros2 security create_keystore "$KEYSTORE_DIR"
fi

for enclave in "${ENCLAVES[@]}"; do
    echo "== $enclave =="
    ros2 security create_key "$KEYSTORE_DIR" "$enclave"
    ros2 security create_permission "$KEYSTORE_DIR" "$enclave" "$POLICY_FILE"
done

echo
echo "Done. To run a node under one of these enclaves, set:"
echo "  ROS_SECURITY_ENABLE=true"
echo "  ROS_SECURITY_STRATEGY=Enforce"
echo "  ROS_SECURITY_KEYSTORE=$KEYSTORE_DIR"
echo "  ROS_SECURITY_ENCLAVE_OVERRIDE=<one of the enclave paths above>"
echo "(see ../README.md and sim/launch/affectguard_sim.launch.py for how"
echo " these are wired per-node via launch_ros additional_env)."
