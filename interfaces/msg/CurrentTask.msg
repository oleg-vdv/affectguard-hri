# The robot's currently active task (FR-2 input).
#
# Published by whatever task manager/scheduler the robot runs - out of
# scope for this project (the spec only requires the policy engine to
# subscribe to it). critical=true means the safety envelope must not
# let any emotion-driven behavior change interrupt it (NFR: safety
# envelope, "запрет прерывания задач, помеченных как critical").

string task_id
bool critical
