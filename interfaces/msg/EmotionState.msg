# A single-modality or fused emotion reading (FR-1).
#
# label is intentionally a free string rather than an enum: video and
# audio models don't necessarily share the same label set (e.g. FER+'s
# 8 classes vs an arbitrary speech-emotion model's label list), and the
# fusion node's job is exactly to reconcile that, not to hide it earlier.

builtin_interfaces/Time stamp
string label
float32 confidence
