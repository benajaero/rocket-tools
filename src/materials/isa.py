"""International Standard Atmosphere with pre-computed cache."""

import numpy as np
from functools import lru_cache

G_STD = 9.80665
R_AIR = 287.05
T0 = 288.15
P0 = 101325.0

# Pre-compute ISA at 1-meter intervals (0 to 25,000m for MVP)
_ISA_ALTITUDES = np.arange(0, 25001, 1, dtype=np.float64)
_ISA_TEMPERATURES = np.empty_like(_ISA_ALTITUDES)
_ISA_PRESSURES = np.empty_like(_ISA_ALTITUDES)

for i, h in enumerate(_ISA_ALTITUDES):
    if h <= 11000.0:
        lapse = -0.0065
        t = T0 + lapse * h
        p = P0 * (t / T0) ** (-G_STD / (lapse * R_AIR))
    elif h <= 20000.0:
        t = 216.65
        p11 = 22632.0
        p = p11 * np.exp(-G_STD * (h - 11000.0) / (R_AIR * t))
    else:
        lapse = 0.001
        t = 216.65 + lapse * (h - 20000.0)
        p20 = 5474.9
        p = p20 * (t / 216.65) ** (-G_STD / (lapse * R_AIR))

    _ISA_TEMPERATURES[i] = t
    _ISA_PRESSURES[i] = p


@lru_cache(maxsize=1024)
def isa_atmosphere(altitude_m: float) -> dict:
    if altitude_m < 0 or altitude_m > 25000:
        raise ValueError("Altitude must be 0-25000 m for MVP")

    # Linear interpolation between nearest pre-computed points
    idx = int(altitude_m)
    frac = altitude_m - idx

    if idx >= len(_ISA_ALTITUDES) - 1:
        t = float(_ISA_TEMPERATURES[-1])
        p = float(_ISA_PRESSURES[-1])
    else:
        t = float(_ISA_TEMPERATURES[idx] * (1 - frac) + _ISA_TEMPERATURES[idx + 1] * frac)
        p = float(_ISA_PRESSURES[idx] * (1 - frac) + _ISA_PRESSURES[idx + 1] * frac)

    density = p / (R_AIR * t)
    speed_of_sound = (1.4 * R_AIR * t) ** 0.5

    return {
        "altitude_m": altitude_m,
        "temperature_k": round(t, 2),
        "temperature_c": round(t - 273.15, 2),
        "pressure_pa": round(p, 1),
        "pressure_kpa": round(p / 1000, 3),
        "density_kg_m3": round(density, 4),
        "speed_of_sound_m_s": round(speed_of_sound, 1),
    }
