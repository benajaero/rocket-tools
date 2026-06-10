---
title: Unit Conversion & Imperial Support
skill_type: engineering
layer: utilities
tools:
  - unit_convert
  - convert_to_si
version: 0.3.0
---

# Unit Conversion & Imperial Support

Comprehensive unit conversion for aerospace engineering with NIST-traceable constants.

## When to Use

- Converting between SI and US customary units
- Normalizing imperial inputs to SI for tool calls
- Working with mixed-unit specifications (common in aerospace)
- Converting results back to imperial for reporting

## Supported Dimensions

### Length
| Unit | Symbol | Notes |
|------|--------|-------|
| Meter | `m` | SI base |
| Millimeter | `mm` | |
| Centimeter | `cm` | |
| Kilometer | `km` | |
| Inch | `inch`, `in` | Exact: 0.0254 m |
| Foot | `ft` | Exact: 0.3048 m |
| Yard | `yd` | Exact: 0.9144 m |
| Mile | `mi` | Statute mile |
| Nautical mile | `nm`, `nmi` | Exact: 1852 m |

### Pressure
| Unit | Symbol | Notes |
|------|--------|-------|
| Pascal | `pa` | SI base |
| Kilopascal | `kpa` | |
| Megapascal | `mpa` | |
| Gigapascal | `gpa` | |
| PSI | `psi` | lbf/in² |
| PSF | `psf` | lbf/ft² |
| KSI | `ksi` | kip/in² |
| Atmosphere | `atm` | Standard atm |
| Bar | `bar` | |
| Torr | `torr` | |

### Force
| Unit | Symbol | Notes |
|------|--------|-------|
| Newton | `n` | SI base |
| Kilonewton | `kn` | |
| Pound-force | `lbf` | |
| Kip | `kip` | 1000 lbf |
| Ton-force | `tonf` | 2000 lbf |

### Speed
| Unit | Symbol | Notes |
|------|--------|-------|
| m/s | `m/s` | SI base |
| mph | `mph` | |
| ft/s | `fps` | |
| Knot | `knot`, `kt` | Nautical mph |
| km/h | `km/h`, `kmh` | |

### Area
| Unit | Symbol | Notes |
|------|--------|-------|
| m² | `m2` | SI base |
| sq ft | `sqft` | |
| sq in | `sqin` | |

### Density
| Unit | Symbol | Notes |
|------|--------|-------|
| kg/m³ | `kg/m3` | SI base |
| slug/ft³ | `slug/ft3` | |
| lb/ft³ | `lb/ft3` | |

### Temperature
| Unit | Symbol | Notes |
|------|--------|-------|
| Celsius | `c` | |
| Kelvin | `k` | SI base |
| Fahrenheit | `f` | |
| Rankine | `r` | |

### Energy
| Unit | Symbol | Notes |
|------|--------|-------|
| Joule | `j` | SI base |
| ft·lbf | `ftlbf` | |
| BTU | `btu` | |

## MCP Tool Reference

### `unit_convert`

Convert between any two supported units.

```python
from rocket_tools.utils import unit_convert

# Length
result = unit_convert(10, "ft", "m")
# -> {"converted_value": 3.048, "conversion_factor": 0.3048}

# Pressure
result = unit_convert(14.7, "psi", "kpa")
# -> {"converted_value": 101.3529...}

# Temperature
result = unit_convert(68, "f", "c")
# -> {"converted_value": 20.0}
```

### `convert_to_si`

Convert any supported unit to its SI base automatically.

```python
from rocket_tools.utils.units import convert_to_si

value, si_unit = convert_to_si(10, "ft")
# -> (3.048, "m")

value, si_unit = convert_to_si(1000, "lbf")
# -> (4448.2216, "n")

value, si_unit = convert_to_si(14.7, "psi")
# -> (101352.93, "pa")
```

### Convenience Helpers

```python
from rocket_tools.utils.units import ft_to_m, lbf_to_n, psi_to_pa, mph_to_mps, knots_to_mps

ft_to_m(10)        # -> 3.048
lbf_to_n(1000)     # -> 4448.2216
psi_to_pa(14.7)    # -> 101352.93
mph_to_mps(60)     # -> 26.8224
knots_to_mps(100)  # -> 51.4444
```

## Worked Example: Mixed-Unit Wing Load

**Problem:** A wing section has:
- Span: 20 ft
- Chord: 3 ft
- Load: 500 lbf/ft (distributed)
- Material: 6061-T6 (E = 10 Msi)

Find the maximum deflection in inches.

**Solution:**
```python
from rocket_tools.utils.units import convert_to_si, ft_to_m, lbf_to_n, psi_to_pa
from rocket_tools.structural import beam_analysis

# Convert all inputs to SI
length_m = ft_to_m(20)
load_n_per_m = lbf_to_n(500) / ft_to_m(1)  # lbf/ft -> N/m
E_pa = psi_to_pa(10e6)  # 10 Msi -> Pa

result = beam_analysis(
    load=load_n_per_m,
    length=length_m,
    youngs_modulus=E_pa,
    cross_section={"type": "rectangle", "width": ft_to_m(3), "height": ft_to_m(0.25)},
    load_type="distributed",
    support_type="simply_supported",
)

# Convert deflection back to inches
deflection_in = result["max_deflection_m"] / 0.0254
print(f"Max deflection: {deflection_in:.3f} in")
print(f"Bending stress: {result['bending_stress_pa']/1e6:.2f} MPa")
```

## Common Pitfalls

1. **Mass vs Weight** — `lbm` is mass, `lbf` is force. In Earth's gravity, 1 lbm ≈ 1 lbf, but they're different dimensions.
2. **Temperature offsets** — Fahrenheit and Celsius conversions involve offsets, not just scaling. Use `unit_convert`, not manual math.
3. **Nautical vs statute miles** — `nm` = nautical mile (1852 m), `mi` = statute mile (1609.34 m).
4. **Area units** — `sqft` is square feet, not `ft2`. Use the canonical symbols from the table above.
