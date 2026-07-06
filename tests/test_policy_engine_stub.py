"""Phase 1 smoke test: the policy engine stub publishes on core/cmd.

Requires rclpy (run inside the ROS 2 workspace / docker image — see
tests/README.md). Not currently invoked by CI.
"""

import rclpy
from geometry_msgs.msg import Twist

from core.policy_engine_stub import DEFAULT_LINEAR_X, PolicyEngineStub


def test_publishes_expected_linear_x():
    rclpy.init()
    received = []
    try:
        node = PolicyEngineStub()
        listener = rclpy.create_node("test_listener")
        listener.create_subscription(Twist, "core/cmd", received.append, 10)

        deadline = node.get_clock().now().nanoseconds + int(2e9)
        while not received and node.get_clock().now().nanoseconds < deadline:
            rclpy.spin_once(node, timeout_sec=0.1)
            rclpy.spin_once(listener, timeout_sec=0.1)

        assert received, "expected at least one message on core/cmd"
        assert received[0].linear.x == DEFAULT_LINEAR_X
    finally:
        rclpy.shutdown()
