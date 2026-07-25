"""Provenance registry: the authoritative source, formula, and assumptions per tool.

Research use of a computed number requires knowing where it comes from. This
module maps every MCP tool to its primary reference(s), governing equation, and
modelling assumptions, and cross-links the curated validation benchmarks that
pin the tool to published values. Exposed through the ``cite_tool`` and
``list_references`` MCP tools so an agent can defend or trace any result.
"""

from typing import Any

from rocket_tools.validation.benchmarks import _BENCHMARKS

# Per-tool provenance. Keys must match the registered MCP tool names.
_PROVENANCE: dict[str, dict[str, Any]] = {
    # ---- Aerodynamics: fundamentals ----
    "reynolds_number": {
        "domain": "aerodynamics",
        "references": ["Anderson, Fundamentals of Aerodynamics, 6th Ed."],
        "formula": "Re = rho*V*L/mu = V*L/nu",
        "assumptions": ["continuum flow", "constant fluid properties along L"],
    },
    "mach_number": {
        "domain": "aerodynamics",
        "references": ["Anderson, Fundamentals of Aerodynamics, 6th Ed."],
        "formula": "M = V/a, a = sqrt(gamma*R*T)",
        "assumptions": ["perfect gas", "local speed of sound from static temperature"],
    },
    "dynamic_pressure": {
        "domain": "aerodynamics",
        "references": ["Anderson, Fundamentals of Aerodynamics, 6th Ed."],
        "formula": "q = 0.5*rho*V^2",
        "assumptions": ["incompressible definition; use with care above ~M0.3"],
    },
    "lift_coefficient": {
        "domain": "aerodynamics",
        "references": ["Anderson, Fundamentals of Aerodynamics, 6th Ed."],
        "formula": "C_L = L/(q*S)",
        "assumptions": ["reference area S consistent with L"],
    },
    "drag_coefficient": {
        "domain": "aerodynamics",
        "references": ["Anderson, Fundamentals of Aerodynamics, 6th Ed."],
        "formula": "C_D = D/(q*S)",
        "assumptions": ["reference area S consistent with D"],
    },
    "skin_friction_coefficient": {
        "domain": "aerodynamics",
        "references": ["Blasius (1908), ZAMM", "Anderson, Fundamentals of Aerodynamics, 6th Ed."],
        "formula": "cf = 1.328/sqrt(Re) (laminar); cf = 0.0592/Re^0.2 (turbulent, local)",
        "assumptions": ["flat plate", "zero pressure gradient", "incompressible"],
    },
    "aero_analysis": {
        "domain": "aerodynamics",
        "references": ["Anderson, Fundamentals of Aerodynamics, 6th Ed."],
        "formula": "composite: Re, M, q, C_L, C_D from free-stream and geometry",
        "assumptions": ["ISA atmosphere for density/viscosity", "perfect gas"],
    },
    # ---- Aerodynamics: compressible ----
    "isentropic_flow": {
        "domain": "compressible flow",
        "references": [
            "Anderson, Fundamentals of Aerodynamics, 6th Ed., Ch. 4",
            "NACA Report 1135 (1953)",
        ],
        "formula": "T/T0=(1+(g-1)/2 M^2)^-1; P/P0=(...)^(g/(g-1)); A/A* area-Mach relation",
        "assumptions": ["adiabatic, reversible (isentropic)", "calorically perfect gas"],
    },
    "normal_shock": {
        "domain": "compressible flow",
        "references": [
            "Anderson, Fundamentals of Aerodynamics, 6th Ed., Ch. 4",
            "NACA Report 1135 (1953), Eq. 100 for p02/p01",
        ],
        "formula": (
            "Rankine-Hugoniot; p02/p01 = [(g+1)M1^2/((g-1)M1^2+2)]^(g/(g-1))"
            " * [(g+1)/(2g M1^2-(g-1))]^(1/(g-1))"
        ),
        "assumptions": ["1-D steady shock", "calorically perfect gas", "M1 > 1"],
    },
    "oblique_shock": {
        "domain": "compressible flow",
        "references": ["Anderson, Fundamentals of Aerodynamics, 6th Ed., Ch. 9"],
        "formula": "theta-beta-M relation; weak (attached) solution; detaches above theta_max",
        "assumptions": ["straight attached shock", "weak solution", "calorically perfect gas"],
    },
    "prandtl_meyer": {
        "domain": "compressible flow",
        "references": ["Anderson, Fundamentals of Aerodynamics, 6th Ed., Eq. 4.104"],
        "formula": "nu(M) = sqrt((g+1)/(g-1))*atan(sqrt((g-1)/(g+1)(M^2-1))) - atan(sqrt(M^2-1))",
        "assumptions": ["isentropic expansion fan", "M >= 1"],
    },
    "prandtl_meyer_from_angle": {
        "domain": "compressible flow",
        "references": ["Anderson, Fundamentals of Aerodynamics, 6th Ed., Eq. 4.104"],
        "formula": "invert nu(M) for M given the Prandtl-Meyer angle",
        "assumptions": ["isentropic expansion fan"],
    },
    # ---- Aerodynamics: aircraft ----
    "lift_curve_slope": {
        "domain": "aircraft performance",
        "references": ["Anderson, Aircraft Performance and Design"],
        "formula": "a = a0/(1 + a0/(pi*e*AR)) (finite-wing, lifting-line)",
        "assumptions": ["thin airfoil a0~2*pi/rad", "elliptic-ish loading via span efficiency e"],
    },
    "drag_polar": {
        "domain": "aircraft performance",
        "references": ["Anderson, Aircraft Performance and Design, Ch. 6"],
        "formula": "C_D = C_D0 + k*C_L^2, k = 1/(pi*e*AR)",
        "assumptions": ["parabolic drag polar", "fixed C_D0 and e"],
    },
    "breguet_range": {
        "domain": "aircraft performance",
        "references": ["Anderson, Aircraft Performance and Design, Ch. 6"],
        "formula": "R = (V/c)*(L/D)*ln(Wi/Wf) (jet, thrust SFC)",
        "assumptions": ["cruise at constant L/D", "constant SFC and speed"],
    },
    "breguet_endurance": {
        "domain": "aircraft performance",
        "references": ["Anderson, Aircraft Performance and Design, Ch. 6"],
        "formula": "E = (1/c)*(L/D)*ln(Wi/Wf) (jet)",
        "assumptions": ["constant L/D and SFC"],
    },
    "wing_loading": {
        "domain": "aircraft performance",
        "references": ["Anderson, Aircraft Performance and Design"],
        "formula": "W/S; V_stall = sqrt(2*(W/S)/(rho*C_Lmax))",
        "assumptions": ["steady level flight for stall speed"],
    },
    # ---- Propulsion: nozzle & thermochemistry ----
    "nozzle_performance": {
        "domain": "propulsion",
        "references": [
            "Sutton & Biblarz, Rocket Propulsion Elements, 9th Ed., Ch. 3",
            "Hill & Peterson, Mechanics and Thermodynamics of Propulsion, 2nd Ed.",
        ],
        "formula": "thrust, C_F, Isp, c*, exit conditions for a De Laval nozzle",
        "assumptions": ["1-D isentropic, calorically perfect gas", "frozen composition"],
    },
    "optimal_area_ratio": {
        "domain": "propulsion",
        "references": ["Sutton & Biblarz, Rocket Propulsion Elements, 9th Ed., Ch. 3"],
        "formula": "A/A* where exit pressure equals ambient (optimum expansion)",
        "assumptions": ["1-D isentropic", "perfectly expanded design point"],
    },
    "characteristic_velocity": {
        "domain": "propulsion",
        "references": ["Sutton & Biblarz, Rocket Propulsion Elements, 9th Ed., Eq. 3-32"],
        "formula": "c* = sqrt(R*Tc)/Gamma, Gamma = sqrt(g)*(2/(g+1))^((g+1)/(2(g-1)))",
        "assumptions": ["choked throat", "calorically perfect gas"],
    },
    "ideal_specific_impulse": {
        "domain": "propulsion",
        "references": ["Sutton & Biblarz, Rocket Propulsion Elements, 9th Ed., Eq. 3-16"],
        "formula": "v_e = sqrt(2g/(g-1)*R*Tc*(1-(pe/pc)^((g-1)/g))); Isp = v_e/g0",
        "assumptions": ["1-D isentropic ideal expansion", "frozen flow (upper bound)"],
    },
    "throat_mass_flux": {
        "domain": "propulsion",
        "references": ["Sutton & Biblarz, Rocket Propulsion Elements, 9th Ed., Eq. 3-24"],
        "formula": "mdot/At = pc*Gamma/sqrt(R*Tc)",
        "assumptions": ["choked throat", "calorically perfect gas"],
    },
    # ---- Motor ballistics ----
    "motor_thrust_curve_analysis": {
        "domain": "propulsion",
        "references": [
            "NAR/TRA motor certification (total-impulse letter classes)",
            "Sutton & Biblarz, Rocket Propulsion Elements, 9th Ed. (total impulse, Isp)",
        ],
        "formula": (
            "I_total = integral F dt (trapezoidal); avg thrust = I/t_burn; "
            "Isp = I/(m_prop*g0); class from I doubling every letter (A: 2.5 N*s)"
        ),
        "assumptions": [
            "thrust curve sampled finely enough for trapezoidal integration",
            "propellant mass fully consumed",
        ],
    },
    # ---- Static stability ----
    "center_of_pressure": {
        "domain": "stability",
        "references": [
            "Barrowman, J. S., The Practical Calculation of the Aerodynamic "
            "Characteristics of Slender Finned Vehicles, NASA (1966)"
        ],
        "formula": "X_cp = sum(CNa_i*X_i)/sum(CNa_i); nose CNa=2, fin CNa via Barrowman",
        "assumptions": [
            "subsonic",
            "small angle of attack",
            "straight body (negligible body normal force)",
            "trapezoidal fins",
        ],
    },
    "static_margin": {
        "domain": "stability",
        "references": ["Barrowman, J. S., NASA (1966); standard rocketry stability convention"],
        "formula": "SM = (X_cp - X_cg)/d (calibers)",
        "assumptions": ["reference diameter = one caliber", "static (rigid-body) margin"],
    },
    # ---- Aerothermodynamics ----
    "stagnation_temperature": {
        "domain": "aerothermodynamics",
        "references": ["Anderson, Hypersonic and High-Temperature Gas Dynamics, 2nd Ed."],
        "formula": "T0 = T*(1 + (g-1)/2*M^2)",
        "assumptions": ["adiabatic", "calorically perfect gas"],
    },
    "recovery_temperature": {
        "domain": "aerothermodynamics",
        "references": ["Anderson, Hypersonic and High-Temperature Gas Dynamics, 2nd Ed."],
        "formula": "Tr = T*(1 + r*(g-1)/2*M^2), r = Pr^0.5 (lam) or Pr^(1/3) (turb)",
        "assumptions": ["boundary-layer recovery factor from Prandtl number"],
    },
    "sutton_graves_heat_flux": {
        "domain": "aerothermodynamics",
        "references": ["Sutton, K. & Graves, R. A., NASA TR R-376 (1971)"],
        "formula": "q = 1.7415e-4*sqrt(rho/Rn)*V^3 (W/m^2, Earth air)",
        "assumptions": ["stagnation point", "convective only (no radiation)", "cold wall"],
    },
    "ballistic_entry_peak_deceleration": {
        "domain": "aerothermodynamics",
        "references": ["Allen, H. J. & Eggers, A. J., NACA TR 1381 (1958)"],
        "formula": "a_max = V_e^2*sin(gamma)/(2*e*H); V at peak = V_e/sqrt(e)",
        "assumptions": ["steep non-lifting entry", "exponential atmosphere", "constant Cd"],
    },
    # ---- Structural ----
    "beam_analysis": {
        "domain": "structural",
        "references": ["Roark's Formulas for Stress and Strain, 8th Ed., Table 8.1"],
        "formula": "deflection & bending stress per support/load case (e.g. PL^3/48EI, PL/4*c/I)",
        "assumptions": ["linear-elastic Euler-Bernoulli beam", "small deflections"],
    },
    "section_properties": {
        "domain": "structural",
        "references": ["Roark's Formulas for Stress and Strain, 8th Ed., Table A.1"],
        "formula": "A, I, S for standard cross-sections (I=bh^3/12, S=bh^2/6, ...)",
        "assumptions": ["prismatic section", "thin-wall where noted"],
    },
    "column_buckling": {
        "domain": "structural",
        "references": [
            "Timoshenko & Gere, Theory of Elastic Stability, 2nd Ed.",
            "Bruhn, Analysis and Design of Flight Vehicle Structures",
        ],
        "formula": "Euler Pcr = pi^2 EI/(KL)^2 with Johnson parabola below transition slenderness",
        "assumptions": ["ideal column", "end-fixity factor K", "elastic buckling above transition"],
    },
    "plate_buckling_coefficient": {
        "domain": "structural",
        "references": ["Bruhn, Analysis and Design of Flight Vehicle Structures, Fig. C5.2/C5.3"],
        "formula": "sigma_cr = k*pi^2*E/(12(1-nu^2))*(t/b)^2",
        "assumptions": ["flat plate", "specified edge boundary conditions"],
    },
    "margin_of_safety": {
        "domain": "structural",
        "references": [
            "Shigley's Mechanical Engineering Design, 11th Ed.",
            "FAA AC 25.571-1D",
        ],
        "formula": "MS = allowable/(FS*applied) - 1",
        "assumptions": ["static strength", "chosen factor of safety FS"],
    },
    "combined_margin_of_safety": {
        "domain": "structural",
        "references": ["Shigley's Mechanical Engineering Design, 11th Ed."],
        "formula": "von Mises equivalent stress vs allowable; MS = allowable/(FS*sigma_vm) - 1",
        "assumptions": ["ductile material", "distortion-energy (von Mises) criterion"],
    },
    "von_mises_stress": {
        "domain": "structural",
        "references": ["Shigley's Mechanical Engineering Design, 11th Ed."],
        "formula": "sigma_vm = sqrt(sx^2 - sx*sy + sy^2 + 3*txy^2)",
        "assumptions": ["plane stress unless 3-D components supplied"],
    },
    "deflection_margin": {
        "domain": "structural",
        "references": ["Shigley's Mechanical Engineering Design, 11th Ed."],
        "formula": "MS = allowable_deflection/actual - 1 (e.g. L/360, L/500 limits)",
        "assumptions": ["serviceability limit, not strength"],
    },
    "truss_analysis": {
        "domain": "structural",
        "references": ["Megson, Aircraft Structures for Engineering Students, 6th Ed."],
        "formula": "direct stiffness method for pin-jointed trusses",
        "assumptions": ["pin joints (axial members only)", "linear-elastic", "small displacement"],
    },
    "thermal_stress": {
        "domain": "structural",
        "references": [
            "Boresi & Schmidt, Advanced Mechanics of Materials, 6th Ed.",
            "Roark's Formulas for Stress and Strain (restrained thermal expansion)",
        ],
        "formula": "sigma = -constraint*E*alpha*dT; free strain = alpha*dT",
        "assumptions": [
            "uniaxial, linear-elastic",
            "constant E and alpha over dT",
            "uniform temperature change",
        ],
    },
    "pressure_vessel_stress": {
        "domain": "structural",
        "references": [
            "Boresi & Schmidt, Advanced Mechanics of Materials, 6th Ed. (thin-wall vessels)",
            "Roark's Formulas for Stress and Strain (membrane theory of shells)",
        ],
        "formula": (
            "cylinder: hoop=p*r/t, long=p*r/(2t); sphere: p*r/(2t); von Mises with radial ~ 0"
        ),
        "assumptions": [
            "thin wall (r/t >= 10)",
            "membrane (no bending) stresses",
            "closed ends",
        ],
    },
    "thick_wall_pressure_vessel_stress": {
        "domain": "structural",
        "references": [
            "Boresi & Schmidt, Advanced Mechanics of Materials, 6th Ed. (Lame thick-wall)",
            "Roark's Formulas for Stress and Strain (thick-wall pressure vessels)",
        ],
        "formula": (
            "Lame: cylinder hoop_i=p(b^2+a^2)/(b^2-a^2), radial_i=-p; "
            "sphere hoop_i=p(2a^3+b^3)/(2(b^3-a^3)); von Mises at the inner surface"
        ),
        "assumptions": [
            "linear-elastic, isotropic",
            "internal pressure only",
            "stresses largest at the inner surface",
        ],
    },
    # ---- Materials & atmosphere ----
    "material_lookup": {
        "domain": "materials",
        "references": ["MIL-HDBK-5J", "MMPDS-15", "MIL-HDBK-17"],
        "formula": "table lookup of mechanical/thermal properties by name",
        "assumptions": ["room-temperature allowables unless noted", "typical/handbook values"],
    },
    "list_materials": {
        "domain": "materials",
        "references": ["MIL-HDBK-5J", "MMPDS-15", "MIL-HDBK-17"],
        "formula": "enumerate bundled materials database",
        "assumptions": ["curated subset of common aerospace alloys/composites"],
    },
    "isa_atmosphere": {
        "domain": "atmosphere",
        "references": ["NASA-TM-X-74335 (US Standard Atmosphere 1976)", "ISO 2533:1975"],
        "formula": "7-layer barometric model, 0-84852 m geopotential",
        "assumptions": ["geopotential altitude input", "static, dry air", "perfect gas"],
    },
    # ---- Design & mission ----
    "rocket_delta_v": {
        "domain": "mission design",
        "references": ["Sutton & Biblarz, Rocket Propulsion Elements, 9th Ed., Eq. 4-6"],
        "formula": "delta_v = Isp*g0*ln(m0/mf) (Tsiolkovsky)",
        "assumptions": ["constant Isp", "no gravity/drag losses"],
    },
    "multi_stage_delta_v": {
        "domain": "mission design",
        "references": ["Sutton & Biblarz, Rocket Propulsion Elements, 9th Ed."],
        "formula": "sum of per-stage Tsiolkovsky delta-v",
        "assumptions": ["instantaneous staging", "per-stage constant Isp"],
    },
    "payload_fraction": {
        "domain": "mission design",
        "references": ["Sutton & Biblarz, Rocket Propulsion Elements, 9th Ed."],
        "formula": "payload fraction from rocket equation and inert-mass fraction",
        "assumptions": ["single stage", "given structural (inert) fraction"],
    },
    "thrust_to_weight": {
        "domain": "mission design",
        "references": ["Sutton & Biblarz, Rocket Propulsion Elements, 9th Ed."],
        "formula": "T/W = thrust/(mass*g)",
        "assumptions": ["local gravitational acceleration g"],
    },
    "composite_cg": {
        "domain": "mission design",
        "references": ["Hibbeler, Engineering Mechanics: Statics"],
        "formula": "r_cg = sum(m_i*r_i)/sum(m_i)",
        "assumptions": ["rigid assembly", "point-mass components"],
    },
    "propellant_tank_sizing": {
        "domain": "mission design",
        "references": ["Sutton & Biblarz, Rocket Propulsion Elements, 9th Ed."],
        "formula": "tank volume with ullage; wall mass from thin-wall geometry",
        "assumptions": ["specified ullage fraction and wall thickness", "thin-wall tank"],
    },
    # ---- Orbital mechanics ----
    "orbital_velocity": {
        "domain": "orbital mechanics",
        "references": ["Vallado, Fundamentals of Astrodynamics and Applications, 4th Ed., Ch. 1"],
        "formula": "v_c = sqrt(mu/r); v_esc = sqrt(2)*v_c; period = 2*pi*r/v_c",
        "assumptions": ["two-body", "circular orbit"],
    },
    "hohmann_transfer": {
        "domain": "orbital mechanics",
        "references": ["Curtis, Orbital Mechanics for Engineering Students, 3rd Ed., Ch. 6"],
        "formula": "two-impulse coplanar transfer; delta-v1, delta-v2, half-ellipse time",
        "assumptions": ["two-body", "coplanar circular orbits", "impulsive burns"],
    },
    "bi_elliptic_transfer": {
        "domain": "orbital mechanics",
        "references": ["Curtis, Orbital Mechanics for Engineering Students, 3rd Ed., Ch. 6.4"],
        "formula": (
            "three-impulse via intermediate apoapsis rb; vis-viva at each burn; "
            "time = pi*sqrt(a1^3/mu) + pi*sqrt(a2^3/mu)"
        ),
        "assumptions": [
            "two-body",
            "coplanar circular start/end orbits",
            "impulsive burns",
            "rb >= both orbit radii",
        ],
    },
    "vis_viva_velocity": {
        "domain": "orbital mechanics",
        "references": [
            "Vallado, Fundamentals of Astrodynamics and Applications, 4th Ed., Eq. 2-70"
        ],
        "formula": "v = sqrt(mu*(2/r - 1/a))",
        "assumptions": ["two-body Keplerian orbit"],
    },
    "plane_change_delta_v": {
        "domain": "orbital mechanics",
        "references": [
            "Vallado, Fundamentals of Astrodynamics and Applications, 4th Ed., Eq. 6-19"
        ],
        "formula": "delta_v = 2*v*sin(delta_i/2)",
        "assumptions": ["simple (speed-preserving) plane change"],
    },
    "orbital_period": {
        "domain": "orbital mechanics",
        "references": ["Vallado, Fundamentals of Astrodynamics and Applications, 4th Ed."],
        "formula": "T = 2*pi*sqrt(a^3/mu) (Kepler's third law)",
        "assumptions": ["two-body Keplerian orbit"],
    },
    "lambert_solver": {
        "domain": "orbital mechanics",
        "references": [
            "Curtis, Orbital Mechanics for Engineering Students, 3rd Ed., Algorithm 5.2",
            "Bate, Mueller & White, Fundamentals of Astrodynamics (universal variables)",
        ],
        "formula": (
            "universal-variable Lambert: y=r1+r2+A(zS-1)/sqrt(C), Newton-solve "
            "F(z)=(y/C)^1.5 S + A sqrt(y) - sqrt(mu) dt = 0; v from Lagrange f,g"
        ),
        "assumptions": [
            "two-body Keplerian transfer",
            "single revolution",
            "prograde/retrograde per input",
            "undefined for a 0 or 180 deg transfer angle",
        ],
    },
    "orbital_elements_from_state": {
        "domain": "orbital mechanics",
        "references": [
            "Curtis, Orbital Mechanics for Engineering Students, 3rd Ed., Algorithm 4.2",
            "Vallado, Fundamentals of Astrodynamics and Applications, 4th Ed. (RV2COE)",
        ],
        "formula": (
            "h=RxV; i=acos(hz/h); N=KxH; e-vector from ((v^2-mu/r)R - r*vr*V)/mu; "
            "RAAN, arg perigee, true anomaly from N, e, R; a from vis-viva energy"
        ),
        "assumptions": [
            "two-body Keplerian orbit",
            "inertial equatorial frame",
            "circular/equatorial angles collapse to 0",
        ],
    },
    "state_from_orbital_elements": {
        "domain": "orbital mechanics",
        "references": [
            "Curtis, Orbital Mechanics for Engineering Students, 3rd Ed., Algorithm 4.5",
            "Vallado, Fundamentals of Astrodynamics and Applications, 4th Ed. (COE2RV)",
        ],
        "formula": (
            "perifocal r=(h^2/mu)/(1+e cos th)[cos th,sin th,0], v=(mu/h)[-sin th,e+cos th,0]; "
            "rotate to ECI by R3(-RAAN)R1(-i)R3(-argp); h=sqrt(mu*a(1-e^2))"
        ),
        "assumptions": [
            "two-body Keplerian orbit",
            "inertial equatorial frame",
            "parabolic e == 1 unsupported via (a, e)",
        ],
    },
    "kepler_propagate": {
        "domain": "orbital mechanics",
        "references": [
            "Curtis, Orbital Mechanics for Engineering Students, 3rd Ed., Algorithm 3.4",
            "Bate, Mueller & White, Fundamentals of Astrodynamics (universal variables)",
        ],
        "formula": (
            "universal Kepler eq. in chi (Newton) with alpha=2/r0-v0^2/mu; "
            "new state from Lagrange f,g,fdot,gdot"
        ),
        "assumptions": [
            "two-body Keplerian orbit",
            "elliptical or hyperbolic",
            "time of flight may be negative (backward propagation)",
        ],
    },
    # ---- Trajectory & vehicle sizing ----
    "simulate_ascent": {
        "domain": "trajectory",
        "references": [
            "Curtis, Orbital Mechanics for Engineering Students, 3rd Ed. (Ch. 11)",
            "Sutton & Biblarz, Rocket Propulsion Elements, 9th Ed. (Ch. 4)",
            "NASA-TM-X-74335: U.S. Standard Atmosphere 1976",
        ],
        "formula": (
            "Planar point-mass gravity turn: dv/dt=(T-D)/m - g*sin(gamma), "
            "dgamma/dt=-(g/v - v/(R+h))*cos(gamma); T=mdot*Isp*g0, D=0.5*rho*V^2*Cd*A; "
            "fixed-step RK4"
        ),
        "assumptions": [
            "point mass, no lift, thrust along velocity vector",
            "ISA 1976 density; inverse-square (or constant) gravity",
            "constant Cd and mass flow rate during burn",
        ],
    },
    "size_vehicle": {
        "domain": "trajectory",
        "references": [
            "Sutton & Biblarz, Rocket Propulsion Elements, 9th Ed. (Ch. 4)",
            "Curtis, Orbital Mechanics for Engineering Students, 3rd Ed. (Ch. 11)",
        ],
        "formula": (
            "MR=exp(dv/(Isp*g0)); m0=ml*(eps-1)/(eps-1/MR) with structural fraction "
            "eps=inert/(inert+propellant)"
        ),
        "assumptions": [
            "single stage",
            "structural fraction epsilon fixed",
            "feasible only when epsilon < 1/MR",
        ],
    },
    # ---- Recovery ----
    "parachute_descent_rate": {
        "domain": "trajectory",
        "references": [
            "Knacke, T. W., Parachute Recovery Systems Design Manual, NWC TP 6575 (1992)"
        ],
        "formula": "V = sqrt(2*m*g/(rho*Cd*S)), S = pi*D^2/4 (steady-descent drag balance)",
        "assumptions": [
            "terminal (steady) descent",
            "Cd referenced to flat canopy area",
            "constant air density over descent",
        ],
    },
    "parachute_area_for_descent_rate": {
        "domain": "trajectory",
        "references": [
            "Knacke, T. W., Parachute Recovery Systems Design Manual, NWC TP 6575 (1992)"
        ],
        "formula": "S = 2*m*g/(rho*Cd*V_target^2), D = sqrt(4*S/pi)",
        "assumptions": [
            "terminal (steady) descent",
            "Cd referenced to flat canopy area",
            "constant air density",
        ],
    },
    # ---- Optimization ----
    "optimize_staging": {
        "domain": "optimization",
        "references": [
            "Curtis, Orbital Mechanics for Engineering Students, 3rd Ed. (Ch. 11, optimal staging)",
            "Hill & Peterson, Mechanics and Thermodynamics of Propulsion, 2nd Ed.",
        ],
        "formula": (
            "Maximize payload fraction s.t. sum c_i ln(n_i)=dv; Lagrange: "
            "n_i=(c_i*lambda-1)/(c_i*lambda*eps_i), single scalar lambda by bisection"
        ),
        "assumptions": [
            "restricted staging problem",
            "fixed per-stage Isp and structural ratio",
            "serial staging with instantaneous separation",
        ],
    },
    "optimize_design": {
        "domain": "optimization",
        "references": ["Kiefer (1953), golden-section search; Press et al., Numerical Recipes"],
        "formula": "golden-section search over one input variable of any dispatch tool",
        "assumptions": ["objective unimodal on the interval", "single continuous variable"],
    },
    # ---- Standards & reliability ----
    "design_review_report": {
        "domain": "standards",
        "references": [
            "FAR 25.303 (factor of safety); MIL-HDBK-5J / MMPDS-15 (allowables)",
            "NASA-STD-5001B (spaceflight factors of safety)",
        ],
        "formula": "MS = allowable/(FoS*actual) - 1; governing margin = min over items",
        "assumptions": ["linear margins", "items independent", "worst-case governs"],
    },
    "fmea_report": {
        "domain": "reliability",
        "references": [
            "MIL-STD-1629A (FMECA)",
            "SAE J1739 (FMEA, RPN convention)",
        ],
        "formula": "RPN = Severity x Occurrence x Detection (each 1-10)",
        "assumptions": [
            "ordinal 1-10 severity/occurrence/detection scales",
            "RPN used only for relative ranking",
        ],
    },
    # ---- Units ----
    "unit_convert": {
        "domain": "units",
        "references": ["NIST SP 811", "ASME Y14.5"],
        "formula": "exact SI<->imperial conversion factors",
        "assumptions": ["NIST-traceable exact factors"],
    },
}


def _benchmarks_for(tool_name: str) -> list[dict[str, Any]]:
    """Curated validation benchmarks (with references) that pin this tool."""
    out = []
    for name, bm in _BENCHMARKS.items():
        if bm["tool_name"] == tool_name:
            out.append(
                {
                    "benchmark": name,
                    "expected": bm["expected"],
                    "tolerance": bm["tolerance"],
                    "reference": bm["reference"],
                }
            )
    return sorted(out, key=lambda b: b["benchmark"])


def list_documented_tools() -> list[str]:
    """Tool names that have a provenance entry."""
    return sorted(_PROVENANCE)


def get_provenance(tool_name: str) -> dict[str, Any]:
    """Return the source, formula, assumptions, and validation status for a tool.

    Raises:
        ValueError: if the tool has no provenance entry.
    """
    if tool_name not in _PROVENANCE:
        available = ", ".join(list_documented_tools())
        raise ValueError(f"No provenance for tool '{tool_name}'. Documented tools: {available}")
    entry = _PROVENANCE[tool_name]
    benchmarks = _benchmarks_for(tool_name)
    return {
        "tool": tool_name,
        "domain": entry["domain"],
        "references": list(entry["references"]),
        "formula": entry["formula"],
        "assumptions": list(entry["assumptions"]),
        "validation_benchmarks": benchmarks,
        "validated": bool(benchmarks),
    }


def list_references() -> list[str]:
    """De-duplicated, sorted bibliography across every documented tool."""
    refs: set[str] = set()
    for entry in _PROVENANCE.values():
        refs.update(entry["references"])
    return sorted(refs)
