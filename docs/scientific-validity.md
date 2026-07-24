# Scientific validity

rocket-tools provides preliminary, closed-form engineering calculations for design
exploration, education, automation, and AI-agent/tool integration. It is a
textbook-companion and MCP dispatch layer, not an analysis suite. Results are not
certification artifacts, and the tools are one to two fidelity tiers below dedicated
software (OpenRocket/RASAero for stability and recovery, NASA CEA/RPA for combustion,
NASTRAN/Ansys for structures, GMAT/STK for missions). Independent verification by a
qualified engineer is required before any result informs a real design or flight.

## What "validated" means here

The curated benchmarks (`rocket-tools://benchmarks`) check each tool against a value
**hand-computed from the same governing equation** the tool implements, or against a
published table (NACA 1135, Anderson App. A, Roark, Sutton & Biblarz, Curtis, Vallado).
This confirms the code is a correct implementation of its formula. It is **not**
validation against experiment, flight data, or a higher-fidelity code. Treat the outputs
as "correct evaluations of a stated model," not as "measured or flight-correlated truth."

## Model fidelity and assumptions

- **Gas model.** Compressible-flow, nozzle, and aerothermodynamic tools assume a
  calorically-perfect gas with constant `gamma`. This breaks down at high temperature and
  hypersonic Mach (real air dissociates/ionizes); `stagnation_temperature` flags
  `perfect_gas_valid=False` above M5. The nozzle tool defaults to combustion-gas properties
  (gamma=1.2, MW=22), not air.
- **Combustion.** There is no chemical-equilibrium thermochemistry. `characteristic_velocity`,
  `ideal_specific_impulse`, and `nozzle_performance` require the user to supply chamber
  temperature, `gamma`, and molecular weight (i.e. a CEA/RPA run done elsewhere). Isp is the
  ideal value; no combustion, cooling, or real-nozzle losses.
- **Aerodynamics.** `lift_coefficient`/`drag_coefficient` normalize a force you supply; they
  predict nothing from geometry. Skin friction is an incompressible flat-plate correlation
  (no compressibility/Van Driest correction). `drag_polar` wave drag uses the Korn
  drag-divergence equation (a preliminary-design estimate). The transonic band
  (0.8 < M < 1.2) is not modeled and is rejected by `lift_curve_slope`.
- **Structures.** Euler-Bernoulli beams (small-deflection, linear-elastic), ideal
  Euler-Johnson columns (no imperfection/eccentricity/local buckling), pin-jointed trusses
  (axial only, no member buckling check), and approximate plate-buckling coefficients. There
  is no FEM, no fatigue/damage tolerance, no joints/fasteners, no composites (ABD), no thermal
  stress, and no modal/vibration analysis.
- **Trajectory.** `simulate_ascent` is a single-stage, planar, point-mass gravity-turn RK4
  integration with constant Cd and sea-level Isp, no Earth rotation, and no staging events.
  It is suitable for feasibility studies, not orbital launch design. `apogee_reached` flags
  when a run is truncated before apogee.
- **Astrodynamics.** Two-body / impulsive / patched-conic only: no J2 or other perturbations
  (so no sun-synchronous design), no Lambert solver, no low-thrust, no ephemeris.
- **Materials.** Single representative room-temperature isotropic values per material, not
  statistical A/B/S-basis allowables and not temperature-dependent. Composites are listed as
  isotropic approximations. Do not use for detailed sizing or certification.
- **Uncertainty.** `propagate_uncertainty` is Monte-Carlo over user-supplied input
  distributions. It reports how the output moves with the inputs; it does not estimate the
  tool's own model error.

## What is genuinely reliable

The classical closed-form kernels are correct and benchmark-pinned: ISA 1976 (0-86 km),
isentropic and normal/oblique-shock relations, Prandtl-Meyer, ideal 1-D nozzle relations,
Tsiolkovsky and multi-stage delta-v, Hohmann/vis-viva/period, section properties, and the
Lagrange-multiplier optimal-staging solver. Units are SI throughout, NaN/inf are rejected at
the boundary, and results are deterministic and reproducible.

## Do not use for

Flight safety, regulatory compliance, structural certification, detailed propulsion or
trajectory design, or as the sole basis for any production decision.
