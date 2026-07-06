"""FR-4: structured JSON Lines audit logging.

One line per state transition (raw emotion -> fused state -> policy
decision -> actuation command), routed through the node's own rclpy
logger so it lands wherever ROS 2 logging is already configured to go,
in a format a later audit tool can parse without ambiguity. Kept as a
tiny duplicated module per package (see core/core/audit.py,
actuation/actuation/audit.py) rather than a new shared package - it's
one function, and perception/core/actuation are already separate
installable ROS packages with no other reason to share a dependency.
"""

import json
import time


def audit_log(logger, stage: str, **fields) -> None:
    record = {"stage": stage, "logged_at": time.time(), **fields}
    logger.info(json.dumps(record))
