# Perception models (Phase 2)

Neither perception node ships model weights. Both refuse to start
(`RuntimeError` at node construction) if `model_path` doesn't point at
an existing file — that's deliberate: silently falling back to mock
inference would contradict what FR-1 actually asks for, and would be
easy to miss in a demo.

## Video: facial emotion (`video_emotion_node`)

Targets the **FER+ (emotion-ferplus)** model from the ONNX Model Zoo:
grayscale 64x64 input `(N, 1, 64, 64)`, 8-class output in the order
`neutral, happiness, surprise, sadness, anger, disgust, fear, contempt`
(`perception/perception/video_emotion_node.py:FER_PLUS_LABELS`). The
node reads input/output tensor names off the loaded model at runtime
(`session.get_inputs()/get_outputs()`) rather than hardcoding them, so
it isn't sensitive to the exact export's internal naming — only to the
input shape and the 8-class label order above.

Search the ONNX Model Zoo (`onnx/models` on GitHub) for
`vision/body_analysis/emotion_ferplus` to find a compatible `.onnx`
file; place it anywhere and point `model_path` at it (see
`sim/launch/affectguard_sim.launch.py`).

## Audio: speech emotion recognition (`audio_emotion_node`)

There's no single de facto standard model here the way FER+ is for
video, so this node's feature extraction is parameterized instead of
hardcoded:

- `n_mfcc` (default 40) and `expected_frames` (default 130) control the
  MFCC tensor shape fed to the model, as `(1, 1, n_mfcc,
  expected_frames)`.
- `labels` (default: `neutral, calm, happy, sad, angry, fearful,
  disgust, surprised` — the RAVDESS label ordering) must match the
  model's output class order.

A reasonable starting point: a small CNN trained on RAVDESS
(Ryerson Audio-Visual Database of Emotional Speech and Song) over MFCC
features, exported to ONNX. Any model matching that input/output
contract works — adjust `n_mfcc`/`expected_frames`/`labels` to fit
whatever you actually plug in; the node does not assume a specific
model beyond that.

## Not verified end-to-end

This environment had no working Docker daemon, no `rclpy`, and no
verified network access to actually download and run either model (see
the README's "Known limitation" note carried over from Phase 1). The
node code is real, working inference code — tensor shapes, softmax,
argmax — not a mock, but it has not been exercised against a real
model file. If a shape or preprocessing assumption is off once you run
it against a real `.onnx` file, that should show up immediately as an
onnxruntime shape-mismatch error, not a silent wrong answer.
