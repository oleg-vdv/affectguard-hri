"""Phase 1-3 bring-up: turtlebot3 in Gazebo + policy engine + actuation + (optional) perception.

Reuses the stock turtlebot3_gazebo world/robot rather than inventing a
custom robot model, per the spec. This assumes the turtlebot3 packages
available for the ROS 2 distro/Gazebo version pinned in
sim/docker/Dockerfile (see docs/decisions/0001-middleware-choice.md for
the version choice and its rationale). If the turtlebot3_gazebo launch
file name or package layout differs from what's assumed here, adjust the
IncludeLaunchDescription target below accordingly.

Perception nodes (Phase 2) are off by default: the default turtlebot3
model ("burger") has no camera, there's no bundled microphone source in
sim, and both perception nodes refuse to start without a real model
file (see docs/models.md). Turn them on with
`enable_perception:=true video_model_path:=... audio_model_path:=...`
once you have models and an image/audio source (a real camera/mic node,
or `ros2 bag play` of a recorded dataset) publishing on image_topic /
audio_topic. Leaving them off by default keeps the plain
`docker compose up` path (NFR-5) working without requiring model files
nobody has yet.

SROS2 (Phase 4) is likewise off by default (`enable_security:=false`).
Each node gets ROS_SECURITY_ENCLAVE_OVERRIDE set to its own enclave path
from security/policies/policy.xml regardless, but ROS_SECURITY_ENABLE
only turns SROS2 on when the launch argument is true, after running
security/generate_keystore.sh - see ../../security/README.md.

Phase 5 (optional, real hardware): `backend:=hardware` swaps
actuation/sim_backend for actuation/hardware_backend and skips the
Gazebo/turtlebot3 world entirely - this is the "same launch file works
on real hardware" criterion from the roadmap (section 7), not a
separate launch file. `hardware_backend` defaults to a log-only motor
driver (see actuation/motor_drivers.py); pass `hardware_driver:=gpiozero`
once you have a real chassis wired up, and tune pins/wheel_base_m/
max_speed_mps via a ROS 2 parameters YAML file for that chassis (see
docs/hardware.md - those aren't exposed as launch arguments since
they're per-robot calibration constants, not run-to-run choices). Real
camera/mic still come from whatever driver nodes publish on
image_topic/audio_topic - same as Phase 2's simulated
`enable_perception` path, since perception nodes never knew the
difference between a real camera and a rosbag to begin with.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    SetEnvironmentVariable,
)
from launch.conditions import IfCondition, LaunchConfigurationEquals
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    turtlebot3_gazebo_share = get_package_share_directory("turtlebot3_gazebo")
    turtlebot3_world_launch = os.path.join(
        turtlebot3_gazebo_share, "launch", "turtlebot3_world.launch.py"
    )

    enable_perception = LaunchConfiguration("enable_perception")
    video_model_path = LaunchConfiguration("video_model_path")
    audio_model_path = LaunchConfiguration("audio_model_path")
    image_topic = LaunchConfiguration("image_topic")
    audio_topic = LaunchConfiguration("audio_topic")

    enable_security = LaunchConfiguration("enable_security")
    security_keystore = LaunchConfiguration("security_keystore")

    hardware_driver = LaunchConfiguration("hardware_driver")

    def sros2_env(enclave: str) -> dict:
        return {
            "ROS_SECURITY_ENABLE": enable_security,
            "ROS_SECURITY_STRATEGY": "Enforce",
            "ROS_SECURITY_KEYSTORE": security_keystore,
            "ROS_SECURITY_ENCLAVE_OVERRIDE": enclave,
        }

    return LaunchDescription(
        [
            DeclareLaunchArgument("enable_perception", default_value="false"),
            DeclareLaunchArgument("video_model_path", default_value=""),
            DeclareLaunchArgument("audio_model_path", default_value=""),
            DeclareLaunchArgument("image_topic", default_value="camera/image_raw"),
            DeclareLaunchArgument("audio_topic", default_value="audio_raw"),
            DeclareLaunchArgument("enable_security", default_value="false"),
            DeclareLaunchArgument(
                "security_keystore", default_value="/workspace/security/keystore"
            ),
            DeclareLaunchArgument(
                "backend",
                default_value="sim",
                description="'sim' (Gazebo/turtlebot3) or 'hardware' (Phase 5, real robot)",
            ),
            DeclareLaunchArgument(
                "hardware_driver",
                default_value="log",
                description=(
                    "'log' (default, no hardware) or 'gpiozero' (Raspberry Pi "
                    "differential drive - tune pins/wheel_base_m/max_speed_mps "
                    "via a ROS 2 parameters YAML file for your chassis, see "
                    "docs/hardware.md)"
                ),
            ),
            SetEnvironmentVariable(
                name="TURTLEBOT3_MODEL", value=os.environ.get("TURTLEBOT3_MODEL", "burger")
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(turtlebot3_world_launch),
                condition=LaunchConfigurationEquals("backend", "sim"),
            ),
            Node(
                package="core",
                executable="policy_engine",
                name="policy_engine",
                output="screen",
                additional_env=sros2_env("/policy_engine"),
            ),
            Node(
                package="actuation",
                executable="sim_backend",
                name="sim_backend",
                output="screen",
                condition=LaunchConfigurationEquals("backend", "sim"),
                additional_env=sros2_env("/actuation_backend"),
            ),
            Node(
                package="actuation",
                executable="hardware_backend",
                name="hardware_backend",
                output="screen",
                parameters=[{"driver": hardware_driver}],
                condition=LaunchConfigurationEquals("backend", "hardware"),
                additional_env=sros2_env("/actuation_backend"),
            ),
            Node(
                package="perception",
                executable="video_emotion_node",
                name="video_emotion_node",
                output="screen",
                parameters=[{"model_path": video_model_path, "image_topic": image_topic}],
                condition=IfCondition(enable_perception),
                additional_env=sros2_env("/perception/video_emotion_node"),
            ),
            Node(
                package="perception",
                executable="audio_emotion_node",
                name="audio_emotion_node",
                output="screen",
                parameters=[{"model_path": audio_model_path, "audio_topic": audio_topic}],
                condition=IfCondition(enable_perception),
                additional_env=sros2_env("/perception/audio_emotion_node"),
            ),
            Node(
                package="perception",
                executable="fusion_node",
                name="fusion_node",
                output="screen",
                condition=IfCondition(enable_perception),
                additional_env=sros2_env("/perception/fusion_node"),
            ),
        ]
    )
