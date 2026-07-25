"""End-to-end orbit determination and propagation (astrodynamics tools).

Solve Lambert's problem for a transfer, read off the resulting orbit's classical
elements, propagate the state forward in time, and rebuild a state vector from the
elements as a round-trip check.

    pip install rocket-tools
    python examples/orbit_determination.py
"""

from rocket_tools.design import (
    kepler_propagate,
    lambert_solver,
    orbital_elements_from_state,
    state_from_orbital_elements,
)


def main() -> None:
    r1 = [5.0e6, 1.0e7, 2.1e6]
    r2 = [-1.46e7, 2.5e6, 7.0e6]

    # 1. Lambert: the orbit joining r1 and r2 in one hour (Curtis Example 5.2).
    lam = lambert_solver(r1_m=r1, r2_m=r2, time_of_flight_s=3600.0)
    v1 = [lam["v1_x_ms"], lam["v1_y_ms"], lam["v1_z_ms"]]
    print(
        f"Lambert: departure speed {lam['v1_speed_ms']:.1f} m/s, "
        f"transfer angle {lam['transfer_angle_deg']:.1f} deg"
    )

    # 2. Classical orbital elements of that transfer orbit.
    coe = orbital_elements_from_state(position_m=r1, velocity_ms=v1)
    print(
        f"Transfer orbit: a={coe['semi_major_axis_m'] / 1e3:.0f} km, "
        f"e={coe['eccentricity']:.4f}, i={coe['inclination_deg']:.2f} deg, "
        f"RAAN={coe['raan_deg']:.1f} deg"
    )

    # 3. Propagate the state 20 minutes forward on that orbit.
    prop = kepler_propagate(position_m=r1, velocity_ms=v1, time_of_flight_s=1200.0)
    print(f"After 20 min: r={prop['radius_m'] / 1e3:.0f} km, v={prop['speed_ms']:.1f} m/s")

    # 4. Rebuild a state vector from the elements and check the round-trip error.
    st = state_from_orbital_elements(
        semi_major_axis_m=coe["semi_major_axis_m"],
        eccentricity=coe["eccentricity"],
        inclination_deg=coe["inclination_deg"],
        raan_deg=coe["raan_deg"],
        argument_of_perigee_deg=coe["argument_of_perigee_deg"],
        true_anomaly_deg=coe["true_anomaly_deg"],
    )
    err = max(
        abs(st["position_x_m"] - r1[0]),
        abs(st["position_y_m"] - r1[1]),
        abs(st["position_z_m"] - r1[2]),
    )
    print(f"COE -> state round-trip position error: {err:.2f} m")


if __name__ == "__main__":
    main()
