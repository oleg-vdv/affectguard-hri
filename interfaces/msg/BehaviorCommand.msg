# Policy engine output (FR-2): movement + voice + face, already passed
# through the safety envelope by the time it's published on core/cmd.
# actuation/ backends translate this for their concrete output (Gazebo
# /cmd_vel + simulated TTS/face indicator in Phase 1-3; real
# motors/speaker/display in the optional Phase 5 hardware backend).

builtin_interfaces/Time stamp
geometry_msgs/Twist movement
string voice_text
float32 voice_volume
string face_pattern
