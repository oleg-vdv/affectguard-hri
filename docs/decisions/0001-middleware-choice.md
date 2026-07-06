# ADR 0001: Middleware — ROS 2 + SROS2, not custom middleware or a kernel-level RTOS

## Status

Accepted (Phase 1).

## Context

The project needs inter-process communication between perception,
policy, and actuation nodes that are developed and potentially deployed
independently, plus (from Phase 4 on) authenticated, encrypted transport
between them, and a path to real hardware (Raspberry Pi 5 / Jetson Orin
Nano) without rewriting the node graph.

Three options were on the table:

1. **A custom middleware** (hand-rolled pub/sub over sockets or shared
   memory).
2. **A kernel-level RTOS built from scratch.**
3. **ROS 2**, with SROS2 (DDS-Security) for the security requirements.

## Decision

Use ROS 2 as the middleware, with SROS2 layered on top starting in
Phase 4. This project is explicitly *not* an RTOS or kernel effort (see
ТЗ section 2): "OS" in the name refers to a system stack at the
middleware + security layer atop Linux, the same sense ROS 2 itself uses
the phrase.

Reasoning, directly from the tech spec's technology section (section 5):

- **Pub/sub + node lifecycle already solved.** ROS 2's DDS-based
  transport, QoS policies, and launch/lifecycle tooling are exactly what
  FR-1 through FR-4 need (topics between perception → policy →
  actuation, `current_task`, structured logging via node loggers). A
  custom middleware would mean re-implementing discovery, QoS, and
  serialization before writing a single emotion-recognition line — cost
  with no corresponding benefit for a pet-project scope.
- **Security requirement maps onto an existing, audited mechanism.**
  NFR-2 (X.509 node authentication, encrypted topic traffic) and NFR-4
  (perception nodes technically unable to reach actuation topics) are
  exactly what SROS2's DDS-Security plugin and access-control XML
  policies provide out of the box. Hand-rolling equivalent auth/encryption
  over custom sockets would mean building and maintaining a
  security-critical component ourselves — the opposite of what a
  "security-first" pet-project should optimize for.
- **A kernel/RTOS is solving a different problem.** Nothing in the
  functional requirements needs hard real-time scheduling guarantees or
  kernel-space drivers; the 300ms end-to-end latency budget (NFR-1) is
  comfortably a soft-real-time, user-space concern. Building an RTOS
  would spend the project's entire time budget on infrastructure that
  the spec doesn't actually require, and would still need a
  perception/policy/actuation stack built on top of it.
- **Ecosystem reuse.** Off-the-shelf ONNX facial/speech emotion models,
  turtlebot3 simulation assets, and Gazebo integration all assume ROS 2
  as the integration layer. Picking anything else would mean re-doing
  integration work the ecosystem already provides.

## ROS 2 distribution and simulator version (Phase 1 addendum)

The spec left the exact distro open ("Humble или Jazzy — LTS-релиз на
момент старта"). This repo pins **ROS 2 Jazzy Jalisco** (LTS, supported
until 2029) with **Gazebo Harmonic**, because:

- Jazzy is the current LTS release as of when Phase 1 was implemented.
- Jazzy dropped Gazebo Classic support entirely, so "Gazebo
  (Ignition/Harmonic)" from the spec's tech stack table and Jazzy's own
  default simulator land on the same choice — there's no classic-vs-new
  Gazebo decision left to make once Jazzy is picked.

**Caveat (partially resolved):** this choice was made and documented
without a working Docker daemon in the environment that authored
Phase 1, so the `ros-jazzy-turtlebot3*` apt package names in
`sim/docker/Dockerfile` started as a best-effort assumption, not a
verified fact. They're verified now: CI's `docker-build` job actually
builds the image on every push (see `.github/workflows/ci.yml`), and
all of them resolved correctly on the first real attempt. The one bug
that *did* surface was unrelated to the package names — pip trying to
uninstall the base image's debian-managed `numpy` while installing
librosa, fixed with `--ignore-installed` — which is exactly the "small,
mechanical fix" this ADR anticipated, just in a different spot than
expected. What's still unverified is runtime behavior (Gazebo/
turtlebot3 actually launching and moving the robot), since CI only
builds the image, it doesn't run `docker compose up`.

## Consequences

- Every node (present and future) must be written against `rclpy`/ROS 2
  message/topic conventions rather than a bespoke IPC API.
- SROS2 keystore generation and access-control policy authoring
  (`security/`) is deferred to Phase 4 by design — see that folder's
  README for why introducing it earlier would add complexity with
  nothing yet to protect.
- The Phase 5 hardware port (Raspberry Pi 5 / Jetson Orin Nano) is
  expected to reuse the same topic interfaces with a different
  actuation-layer implementation, which is only possible because the
  layers already communicate over ROS 2 topics rather than
  process-specific IPC.
