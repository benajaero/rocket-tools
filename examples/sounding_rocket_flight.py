"""End-to-end sounding-rocket check: motor, static stability, ascent, and recovery.

Chains the newer stability, trajectory, recovery, and structural tools into one
preliminary design pass for a small solid-motor sounding rocket.

    pip install rocket-tools
    python examples/sounding_rocket_flight.py
"""

import math

from rocket_tools.aerodynamics import center_of_pressure, motor_thrust_curve_analysis, static_margin
from rocket_tools.structural import thermal_stress
from rocket_tools.trajectory import parachute_area_for_descent_rate, simulate_ascent

BODY_DIAMETER_M = 0.054


def main() -> None:
    # 1. Motor: reduce a measured thrust-time curve to performance figures.
    motor = motor_thrust_curve_analysis(
        times_s=[0.0, 0.1, 0.3, 0.8, 1.2, 1.5],
        thrusts_n=[0.0, 55.0, 40.0, 32.0, 20.0, 0.0],
        propellant_mass_kg=0.050,
    )
    print(
        f"Motor {motor['motor_designation']}: {motor['total_impulse_ns']:.1f} N*s total impulse, "
        f"Isp {motor['specific_impulse_s']:.0f} s, burn {motor['burn_time_s']:.1f} s"
    )

    # 2. Static stability: Barrowman center of pressure vs the CG.
    cp = center_of_pressure(
        nose_shape="ogive",
        nose_length_m=0.20,
        body_diameter_m=BODY_DIAMETER_M,
        fin_count=3,
        fin_root_chord_m=0.10,
        fin_tip_chord_m=0.05,
        fin_semi_span_m=0.06,
        fin_sweep_length_m=0.06,
        fin_position_from_nose_m=0.85,
    )
    margin = static_margin(
        cp["cp_from_nose_m"], cg_from_nose_m=0.62, reference_diameter_m=BODY_DIAMETER_M
    )
    verdict = "stable" if margin["stable"] else "UNSTABLE"
    print(
        f"CP {cp['cp_from_nose_m'] * 100:.1f} cm from nose | static margin "
        f"{margin['static_margin_calibers']:.2f} cal ({verdict})"
    )

    # 3. Ascent through the ISA atmosphere.
    flight = simulate_ascent(
        initial_mass_kg=0.80,
        dry_mass_kg=0.75,
        specific_impulse_s=motor["specific_impulse_s"],
        mass_flow_rate_kg_s=motor["propellant_mass_kg"] / motor["burn_time_s"],
        reference_area_m2=math.pi * (BODY_DIAMETER_M / 2) ** 2,
        drag_coefficient=0.5,
    )
    max_q_kpa = flight["max_dynamic_pressure_pa"] / 1000
    print(f"Apogee {flight['apogee_km']:.2f} km | max-q {max_q_kpa:.1f} kPa")

    # 4. Recovery: size the parachute for a gentle landing.
    chute = parachute_area_for_descent_rate(mass_kg=0.75, target_descent_rate_ms=4.5)
    print(
        f"Parachute: {chute['canopy_diameter_m'] * 100:.0f} cm canopy for a "
        f"{chute['target_descent_rate_ms']:.1f} m/s landing"
    )

    # 5. Airframe thermal check: a +40 K aero-heating soak on a half-restrained Al coupler.
    th = thermal_stress(
        youngs_modulus_pa=70e9, cte_per_k=23.6e-6, delta_temperature_k=40.0, constraint_factor=0.5
    )
    print(
        f"Thermal stress (+40 K, half-restrained Al): "
        f"{th['thermal_stress_mpa']:.1f} MPa ({th['stress_type']})"
    )


if __name__ == "__main__":
    main()
