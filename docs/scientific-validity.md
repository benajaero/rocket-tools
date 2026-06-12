# Scientific Validity

rocket-tools provides preliminary engineering calculations. Results are intended for design exploration, education, automation, and agent/tool integration. They are not certification artifacts.

## Scope

- ISA atmosphere covers 0 to 25,000 m.
- Beam analysis covers common Euler-Bernoulli beam cases and Euler column buckling.
- Aerodynamics utilities cover Reynolds number, Mach number, dynamic pressure, coefficient normalization, and Blasius skin-friction estimates.
- Material properties are representative values and can vary with supplier, heat treatment, process history, and standard revision.

## Assumptions

- Calculations use SI units internally.
- Beam deflection assumes small deflections and linear elastic behavior.
- Euler buckling uses an effective column length factor based on support type.
- Skin friction uses simple Blasius-style correlations and does not replace CFD, wind-tunnel data, or standards-driven design methods.

## Validation Expectations

For release readiness, add tests that compare:

- ISA sea-level and layer-boundary values against a published standard atmosphere reference.
- Beam moments, stresses, and deflections against closed-form reference cases.
- Unit conversions against exact NIST-defined conversion constants where available.
- Aerodynamic nondimensional numbers against hand-calculated examples.

## Certification

Do not use rocket-tools outputs as the sole basis for flight safety, regulatory compliance, or production release. Independent verification by a qualified engineer is required.
