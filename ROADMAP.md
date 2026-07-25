# Roadmap

Where rocket-tools is now, what the next release contains, and the larger pieces we
want to build after that. Versions describe intent, not a promise. A release ships when
its tools are implemented, validated against a published reference, and green in CI, not
on a calendar date.

The guiding rule is the one the project was built on: a number is only worth shipping if
you can trace it to a source and check it against a known answer. That is why the "later"
sections below stay honest about what does not exist yet. A half-finished CEA or FEM would
be worse than no CEA or FEM, because it would look trustworthy and be wrong.

## Now: 0.4.1 (published)

On PyPI. 68 tools across structures, materials, aerodynamics, compressible flow,
propulsion, mission design, orbital mechanics, trajectory, optimization, visualization,
and standards. Every tool validates its inputs, rejects NaN and infinity at the boundary,
and carries a provenance entry you can query with `cite_tool`.

## Next: 0.5.0 (ready to cut)

Twelve new tools since 0.4.1 (68 to 80) plus a round of correctness fixes that made the
existing tools trustworthy for real design work. This is staged on `main` and passing;
the version bump and tag are the only steps left, and those wait for a maintainer's go.

New tools, each pinned to a textbook value or an exact hand computation:

- **Static stability.** `center_of_pressure` (Barrowman) and `static_margin`. A rocket
  with its center of pressure ahead of its center of gravity will not fly, so this is the
  first check any airframe needs.
- **Recovery.** `parachute_descent_rate` and `parachute_area_for_descent_rate`, so you can
  size a canopy to a landing speed or read the landing speed off a canopy.
- **Two-body astrodynamics, end to end.** `lambert_solver` (targeting),
  `orbital_elements_from_state` and `state_from_orbital_elements` (orbit determination both
  ways), and `kepler_propagate` (move a state vector forward or backward in time). All four
  match their Curtis worked examples. `bi_elliptic_transfer` rounds out the impulsive
  maneuvers next to Hohmann.
- **Propulsion.** `motor_thrust_curve_analysis` turns a measured thrust-time curve into
  total impulse, burn time, delivered specific impulse, and a NAR motor class.
- **Structures.** `thermal_stress` for a restrained member and `pressure_vessel_stress`
  for a thin-wall tank.

The fixes are the more important half. Truss reactions, beam shear, Breguet range, the
nozzle separation model, tank sizing, and two miscited material properties were all wrong
in ways that produced plausible but incorrect numbers. They are corrected and pinned by
tests. The full list is in the changelog.

Also in 0.5.0: two runnable worked examples that chain the new tools into real workflows,
a synced `scientific-validity.md` that describes the new capabilities and their limits,
and this roadmap plus the feature list.

## After that: themed minor releases

Each of these is a focused batch of bounded, validatable tools rather than a grab bag. The
order is a preference, not a commitment, and any of them can move if a user needs it sooner.

**Deeper propulsion.** The propulsion tools currently ask you to bring chamber temperature,
gamma, and molecular weight from a CEA or RPA run done elsewhere. A chemical-equilibrium
front end would let you supply a propellant and mixture ratio and get those properties
back, so the whole propulsion chain closes inside the library. This is the single most
requested gap for real use, and also the hardest of the near-term items to do correctly.

**Fuller trajectory.** `simulate_ascent` today is single stage, planar, point mass, with a
constant drag coefficient and sea-level specific impulse. The next steps are staging
events, a drag coefficient that varies with Mach, a specific impulse that varies with
altitude, and Earth rotation. Each is a discrete, testable addition against a published
sounding-rocket or launch case.

**Broader structures.** Thin-wall vessels and restrained thermal stress are in. Natural
follow-ups are thick-wall (Lame) vessels, bolted-joint and lug analysis, and a first pass
at composite laminate (ABD) stiffness. A general beam or frame FEM is a larger effort and
sits further out.

**More astrodynamics.** Multi-revolution Lambert, a J2 secular perturbation model (which is
what you need for sun-synchronous design), and simple maneuver planning build directly on
the two-body core already in place.

## Toward 1.0

1.0 is about the product being stable, not about adding more tools. The work is a hosted
documentation site, a published entry in the MCP registry, an API that we commit not to
break, and a promotion pass once the maintainer decides the time is right. Promotion is on
hold by request until then.

## Larger, research-grade pieces (no committed version)

These are real subsystems, not single functions, and each is weeks of careful work. They
are on the map because people ask for them, and off the near-term plan because doing them
badly would undermine the project's whole reason for existing.

- A general finite-element engine for structures beyond trusses and beams.
- Panel-method or CFD aerodynamics that predicts coefficients from geometry rather than
  normalizing forces you already have.
- A full six-degree-of-freedom flight simulation with wind and dynamic stability.
- Fatigue and damage-tolerance analysis.

When one of these lands, it will arrive validated against a reference case and clearly
scoped, the same as every tool before it.

## Out of scope

rocket-tools is a preliminary-design and education library, not certification software. It
will not become a flight-safety or regulatory-compliance tool, a real-time guidance and
control system, or a replacement for NASTRAN, Ansys, CEA, or STK. The docs say this plainly
in `docs/scientific-validity.md`, and that boundary is not going to move.
