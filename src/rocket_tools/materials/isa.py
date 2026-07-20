"""International Standard Atmosphere (0-86 km) with a cached lookup.

Implements the full 7-layer U.S. Standard Atmosphere 1976 barometric model.
Altitude is interpreted as geopotential altitude H (the convention used by the
ISO 2533 / US Standard Atmosphere tables); the model ceiling is H = 84 852 m,
which corresponds to 86 km geometric altitude and the top of the homosphere.

References:
    - ISO 2533:1975: Standard Atmosphere (geopotential altitude tables).
    - NASA-TM-X-74335: U.S. Standard Atmosphere, 1976 (7 base layers to 86 km).
"""

from functools import lru_cache
from math import exp, floor, log10

from rocket_tools.config import settings

G_STD = settings.isa_g_std
R_AIR = settings.isa_r_air
GAMMA = 1.4

# U.S. Standard Atmosphere 1976 base layers: (geopotential base H_b [m],
# base temperature T_b [K], lapse rate L [K/m]). The final entry is the model
# ceiling (H = 84 852 m = 86 km geometric); its lapse rate is unused.
_LAYERS: tuple[tuple[float, float, float], ...] = (
    (0.0, 288.15, -0.0065),
    (11000.0, 216.65, 0.0),
    (20000.0, 216.65, 0.001),
    (32000.0, 228.65, 0.0028),
    (47000.0, 270.65, 0.0),
    (51000.0, 270.65, -0.0028),
    (71000.0, 214.65, -0.002),
)
_ISA_MAX = 84852.0

# Base pressure at the bottom of each layer, chained upward from sea level (Pa).
_P_BASE: list[float] = [settings.isa_p0]
for _i in range(1, len(_LAYERS)):
    _h_b, _t_b, _lapse = _LAYERS[_i - 1]
    _h_top = _LAYERS[_i][0]
    if _lapse == 0.0:
        _p = _P_BASE[_i - 1] * exp(-G_STD * (_h_top - _h_b) / (R_AIR * _t_b))
    else:
        _t_top = _t_b + _lapse * (_h_top - _h_b)
        _p = _P_BASE[_i - 1] * (_t_top / _t_b) ** (-G_STD / (_lapse * R_AIR))
    _P_BASE.append(_p)


def _sig(x: float, digits: int = 6) -> float:
    """Round to a number of significant figures (handles the 1e5-to-1e-6 range)."""
    if x == 0.0:
        return 0.0
    return round(x, -int(floor(log10(abs(x)))) + (digits - 1))


@lru_cache(maxsize=settings.isa_cache_size)
def isa_atmosphere(altitude_m: float) -> dict:
    if altitude_m != altitude_m or altitude_m in (float("inf"), float("-inf")):
        raise ValueError("Altitude must be finite")
    if altitude_m < 0 or altitude_m > _ISA_MAX:
        raise ValueError(f"Altitude must be 0-{_ISA_MAX:.0f} m (geopotential)")

    # Select the base layer containing this geopotential altitude.
    layer = 0
    for i in range(len(_LAYERS)):
        if altitude_m >= _LAYERS[i][0]:
            layer = i
        else:
            break
    h_b, t_b, lapse = _LAYERS[layer]

    t = t_b + lapse * (altitude_m - h_b)
    if lapse == 0.0:
        p = _P_BASE[layer] * exp(-G_STD * (altitude_m - h_b) / (R_AIR * t_b))
    else:
        p = _P_BASE[layer] * (t / t_b) ** (-G_STD / (lapse * R_AIR))

    density = p / (R_AIR * t)
    speed_of_sound = (GAMMA * R_AIR * t) ** 0.5

    return {
        "altitude_m": altitude_m,
        "temperature_k": round(t, 2),
        "temperature_c": round(t - 273.15, 2),
        "pressure_pa": _sig(p, 6),
        "pressure_kpa": _sig(p / 1000, 6),
        "density_kg_m3": _sig(density, 6),
        "speed_of_sound_m_s": round(speed_of_sound, 2),
    }
