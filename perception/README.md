# perception/

Phase 2: `video_emotion_node`, `audio_emotion_node`, `fusion_node` ->
`fused_emotion_state`. See `docs/models.md` for the ONNX models these
nodes expect (not bundled), and `perception/perception/fusion_logic.py`
+ `tests/test_fusion_logic.py` for the fusion arbitration rule and its
test coverage.

No access to actuation topics/services — publishes only emotion state
(NFR-4). This is a code-level convention until Phase 4 turns it into an
enforced SROS2 access-control policy.
