# Raw PCM audio chunk (FR-1 audio input).
#
# There is no single de facto ROS 2 core message for raw audio, and
# pulling in a community audio_common_msgs dependency of uncertain
# availability wasn't worth it for one field. samples are mono,
# little-endian int16, in [-32768, 32767].

builtin_interfaces/Time stamp
int32 sample_rate
int16[] samples
