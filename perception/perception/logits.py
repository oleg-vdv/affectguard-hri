"""Pure-Python softmax/argmax helpers shared by both perception nodes.

Deliberately stdlib-only (no numpy) so this module can be unit tested
without a ROS 2 / onnxruntime environment installed.
"""

import math


def softmax(logits: list) -> list:
    if not logits:
        return []
    m = max(logits)
    exps = [math.exp(x - m) for x in logits]
    total = sum(exps)
    return [e / total for e in exps]


def argmax_label(probs: list, labels: list) -> tuple:
    if len(probs) != len(labels):
        raise ValueError(
            f"probs has {len(probs)} entries but labels has {len(labels)}"
        )
    if not probs:
        raise ValueError("probs must be non-empty")
    best_index = max(range(len(probs)), key=lambda i: probs[i])
    return labels[best_index], probs[best_index]
