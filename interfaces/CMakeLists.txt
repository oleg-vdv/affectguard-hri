cmake_minimum_required(VERSION 3.8)
project(interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(geometry_msgs REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/EmotionState.msg"
  "msg/AudioChunk.msg"
  "msg/CurrentTask.msg"
  "msg/BehaviorCommand.msg"
  DEPENDENCIES builtin_interfaces geometry_msgs
)

ament_package()
