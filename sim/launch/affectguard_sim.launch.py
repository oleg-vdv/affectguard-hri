"""Phase 1 bring-up: turtlebot3 in Gazebo + core policy engine stub + actuation sim backend.

Reuses the stock turtlebot3_gazebo world/robot rather than inventing a
custom robot model, per the spec. This assumes the turtlebot3 packages
available for the ROS 2 distro/Gazebo version pinned in
sim/docker/Dockerfile (see docs/decisions/0001-middleware-choice.md for
the version choice and its rationale). If the turtlebot3_gazebo launch
file name or package layout differs from what's assumed here, adjust the
IncludeLaunchDescription target below accordingly.
"""

import os

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description() -> LaunchDescription:
    turtlebot3_gazebo_share = get_package_share_directory("turtlebot3_gazebo")
    turtlebot3_world_launch = os.path.join(
        turtlebot3_gazebo_share, "launch", "turtlebot3_world.launch.py"
    )

    return LaunchDescription(
        [
            SetEnvironmentVariable(
                name="TURTLEBOT3_MODEL", value=os.environ.get("TURTLEBOT3_MODEL", "burger")
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(turtlebot3_world_launch)
            ),
            Node(
                package="core",
                executable="policy_engine_stub",
                name="policy_engine_stub",
                output="screen",
            ),
            Node(
                package="actuation",
                executable="sim_backend",
                name="sim_backend",
                output="screen",
            ),
        ]
    )
