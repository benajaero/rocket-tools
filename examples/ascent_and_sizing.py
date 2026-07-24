"""End to end: size a vehicle, fly its ascent, and optimize the staging (new in 0.4.0).

pip install rocket-tools
python examples/ascent_and_sizing.py
"""

from rocket_tools.optimization import optimize_staging
from rocket_tools.trajectory import simulate_ascent, size_vehicle


def main() -> None:
    # 1. Preliminary sizing from a delta-v budget.
    veh = size_vehicle(
        payload_mass_kg=500.0,
        delta_v_target_ms=6000.0,
        specific_impulse_s=330.0,
        inert_mass_fraction=0.08,
    )
    print(
        f"Gross mass: {veh['gross_liftoff_mass_kg']:.0f} kg | "
        f"propellant: {veh['propellant_mass_kg']:.0f} kg | "
        f"payload fraction: {veh['payload_fraction']:.3f}"
    )

    # 2. Simulate the ascent through the ISA atmosphere (near-vertical launch).
    flight = simulate_ascent(
        initial_mass_kg=50000.0,
        dry_mass_kg=15000.0,
        specific_impulse_s=280.0,
        mass_flow_rate_kg_s=350.0,
        reference_area_m2=1.2,
        launch_angle_deg=89.0,
    )
    print(
        f"Apogee: {flight['apogee_km']:.1f} km | "
        f"max-q: {flight['max_dynamic_pressure_pa'] / 1000:.0f} kPa | "
        f"peak accel: {flight['max_accel_g']:.1f} g"
    )

    # 3. Optimal staging: the payload-maximizing delta-v split across two stages.
    opt = optimize_staging(
        delta_v_target_ms=9400.0,
        stages=[
            {"specific_impulse_s": 282.0, "structural_ratio": 0.08},
            {"specific_impulse_s": 348.0, "structural_ratio": 0.07},
        ],
    )
    split = [s["delta_v_ms"] for s in opt["stages"]]
    print(
        f"Optimal stage split: {split} m/s | "
        f"payload fraction: {opt['optimal_payload_fraction']:.4f}"
    )


if __name__ == "__main__":
    main()
