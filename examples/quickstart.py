"""Quickstart: a handful of rocket-tools calculations from the Python library.

pip install rocket-tools
python examples/quickstart.py
"""

from rocket_tools.aerodynamics import normal_shock
from rocket_tools.design import orbital_velocity, rocket_delta_v
from rocket_tools.materials import isa_atmosphere, material_lookup
from rocket_tools.structural import beam_analysis


def main() -> None:
    # Material lookup (fuzzy name matching)
    mat = material_lookup("6061-T6")
    print(
        f"6061-T6: E = {mat['youngs_modulus_pa'] / 1e9:.0f} GPa, "
        f"yield = {mat['yield_strength_mpa']:.0f} MPa"
    )

    # Standard atmosphere at 11 km
    atm = isa_atmosphere(11000)
    print(
        f"At 11 km: {atm['temperature_k']:.1f} K, {atm['pressure_pa'] / 1000:.1f} kPa, "
        f"a = {atm['speed_of_sound_m_s']:.0f} m/s"
    )

    # Beam deflection under a mid-span point load
    beam = beam_analysis(
        load=500.0,
        length=2.0,
        youngs_modulus=mat["youngs_modulus_pa"],
        cross_section={"type": "rectangle", "width": 0.05, "height": 0.02},
    )
    print(f"Beam max deflection: {beam['max_deflection_m'] * 1000:.2f} mm")

    # Compressible flow: a normal shock at Mach 2.5
    ns = normal_shock(mach1=2.5)
    print(
        f"Normal shock M1 = 2.5: M2 = {ns['mach_downstream']:.3f}, "
        f"p2/p1 = {ns['pressure_ratio']:.2f}"
    )

    # Mission delta-v (Tsiolkovsky) and a circular orbit speed
    dv = rocket_delta_v(specific_impulse_s=320, initial_mass_kg=10000, final_mass_kg=2000)
    print(f"Delta-v (Isp 320, mass ratio 5): {dv['delta_v_ms']:.0f} m/s")

    orb = orbital_velocity(altitude_m=400000)
    print(f"Circular orbit at 400 km: {orb['circular_velocity_ms']:.0f} m/s")


if __name__ == "__main__":
    main()
