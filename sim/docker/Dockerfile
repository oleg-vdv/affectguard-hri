# AffectGuard-HRI - sim image (Phases 1-4).
#
# Base: ROS 2 Jazzy Jalisco (current LTS at project start, supported
# until 2029) + Gazebo Harmonic, which is the Gazebo release officially
# paired with Jazzy (Gazebo Classic is not supported on Jazzy at all).
# See docs/decisions/0001-middleware-choice.md for the full rationale.
#
# NOTE: this was authored without a working Docker daemon / package-index
# access in the dev sandbox, so the exact `ros-jazzy-turtlebot3*` package
# names are assumed from the turtlebot3 project's usual naming, not
# verified against the live apt index. If `docker compose up` fails on
# an apt package name, that's the first thing to check.
FROM osrf/ros:jazzy-desktop

ENV DEBIAN_FRONTEND=noninteractive \
    TURTLEBOT3_MODEL=burger \
    ROS_DISTRO=jazzy

RUN apt-get update && apt-get install -y --no-install-recommends \
        ros-jazzy-turtlebot3 \
        ros-jazzy-turtlebot3-simulations \
        ros-jazzy-turtlebot3-msgs \
        ros-jazzy-ros-gz \
        ros-jazzy-cv-bridge \
        ros-jazzy-sros2 \
        python3-colcon-common-extensions \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Phase 4 (SROS2): DDS-Security's most consistently documented RMW
# pairing is Fast-DDS (rclpy's default), not Cyclone DDS, so the
# Cyclone override from earlier phases is dropped once security/ is in
# the picture - see security/README.md.

# Phase 2 perception dependencies. Not resolvable via rosdep/apt as ROS
# packages, so installed via pip - see docs/models.md for the models
# these actually run. --ignore-installed is required because the base
# image's numpy is a debian-managed package with no pip RECORD file,
# which librosa's dependency chain otherwise tries (and fails) to
# uninstall (confirmed by an actual CI run - see git history for this
# line).
RUN pip install --no-cache-dir --break-system-packages --ignore-installed \
        onnxruntime \
        opencv-python-headless \
        librosa

WORKDIR /workspace
COPY interfaces/ src/interfaces/
COPY core/ src/core/
COPY actuation/ src/actuation/
COPY perception/ src/perception/
COPY sim/launch/ launch/
COPY security/ security/

RUN . /opt/ros/jazzy/setup.sh \
    && colcon build --symlink-install

COPY sim/docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["ros2", "launch", "/workspace/launch/affectguard_sim.launch.py"]
