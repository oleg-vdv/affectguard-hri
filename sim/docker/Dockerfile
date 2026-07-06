# AffectGuard-HRI - Phase 1 sim image.
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
        python3-colcon-common-extensions \
        python3-pip \
        ros-jazzy-rmw-cyclonedds-cpp \
    && rm -rf /var/lib/apt/lists/*

ENV RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

# Phase 2 perception dependencies. Not resolvable via rosdep/apt as ROS
# packages, so installed via pip - see docs/models.md for the models
# these actually run.
RUN pip install --no-cache-dir --break-system-packages \
        onnxruntime \
        opencv-python-headless \
        librosa

WORKDIR /workspace
COPY interfaces/ src/interfaces/
COPY core/ src/core/
COPY actuation/ src/actuation/
COPY perception/ src/perception/
COPY sim/launch/ launch/

RUN . /opt/ros/jazzy/setup.sh \
    && colcon build --symlink-install

COPY sim/docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["ros2", "launch", "/workspace/launch/affectguard_sim.launch.py"]
