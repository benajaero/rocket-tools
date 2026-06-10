"""International Standard Atmosphere with pre-computed cache.

References:
    - ISO 2533:1975: Standard Atmosphere.
    - NASA-TM-X-74335: U.S. Standard Atmosphere, 1976.
"""

from functools import lru_cache

import numpy as np

from rocket_tools.config import settings

G_STD = settings.isa_g_std
R_AIR = settings.isa_r_air
T0 = settings.isa_t0
P0 = settings.isa_p0
_ISA_MAX = int(settings.isa_max_altitude_m)
_ISA_STEP = int(settings.isa_altitude_step_m)

_ISA_ALTITUDES = np.arange(0, _ISA_MAX + 1, _ISA_STEP, dtype=np.float64)
_ISA_TEMPERATURES = np.empty_like(_ISA_ALTITUDES)
_ISA_PRESSURES = np.empty_like(_ISA_ALTITUDES)

for i, h in enumerate(_ISA_ALTITUDES):
    if h <= 11000.0:
        lapse = -0.0065
        t = T0 + lapse * h
        p = P0 * (t / T0) ** (-G_STD / (lapse * R_AIR))
    elif h <= 20000.0:
        t = 216.65  # type: ignore[assignment]
        p11 = 22632.0
        p = p11 * np.exp(-G_STD * (h - 11000.0) / (R_AIR * t))
    else:
        lapse = 0.001
        t = 216.65 + lapse * (h - 20000.0)
        p20 = 5474.9
        p = p20 * (t / 216.65) ** (-G_STD / (lapse * R_AIR))

    _ISA_TEMPERATURES[i] = t
    _ISA_PRESSURES[i] = p


@lru_cache(maxsize=settings.isa_cache_size)
def isa_atmosphere(altitude_m: float) -> dict:
    if altitude_m < 0 or altitude_m > _ISA_MAX:
        raise ValueError(f"Altitude must be 0-{_ISA_MAX} m")

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
