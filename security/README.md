# security/

Reserved for Phase 4 (see repo root README and the ТЗ roadmap, section 7):
SROS2 keystore/certificate generation scripts and ROS 2 access control
policies enforcing NFR-2 (encrypted, authenticated inter-node transport)
and NFR-4 (perception nodes technically unable to reach actuation
topics/services).

Not implemented in Phase 1. Introducing the security layer before there
are multiple real nodes to isolate from each other would add complexity
without anything meaningful to test against yet.
