# rocket-tools Skills Library

Human-readable engineering skills with MCP cross-references.

## Skills

| Skill | Tools | Description |
|-------|-------|-------------|
| [Structural Analysis](./structural-analysis.md) | `beam_analysis`, `section_properties`, `column_buckling`, `plate_buckling_coefficient`, `margin_of_safety`, `von_mises_stress`, `combined_margin_of_safety`, `deflection_margin`, `truss_analysis`, `material_lookup`, `unit_convert` | Beams, sections, columns, plates, MS, trusses, material selection |
| [Aerodynamics](./aerodynamics.md) | `reynolds_number`, `mach_number`, `dynamic_pressure`, `lift_coefficient`, `drag_coefficient`, `skin_friction_coefficient`, `aero_analysis`, `isa_atmosphere` | Flow characterization, ISA lookups |
| [Compressible Flow](./compressible-flow.md) | `isentropic_flow`, `normal_shock`, `oblique_shock`, `prandtl_meyer`, `prandtl_meyer_from_angle` | Supersonic/hypersonic flow relations |
| [Aircraft Performance](./aircraft-performance.md) | `lift_curve_slope`, `drag_polar`, `breguet_range`, `breguet_endurance`, `wing_loading` | Fixed-wing aircraft aerodynamics and mission analysis |
| [Rocket Nozzle Design](./rocket-nozzle.md) | `nozzle_performance`, `optimal_area_ratio` | C-D nozzle thrust, Isp, expansion optimization |
| [Mission Design](./mission-design.md) | `rocket_delta_v`, `multi_stage_delta_v`, `orbital_velocity`, `payload_fraction`, `thrust_to_weight`, `composite_cg`, `propellant_tank_sizing` | Rocket staging, orbits, mass properties |
| [Validation & Benchmarks](./validation.md) | All tools | Curated test cases with references |
| [Unit Conversion & Imperial Support](./units.md) | `unit_convert`, `convert_to_si` | SI ↔ Imperial, aerospace units, auto-conversion |
| [Router](./router.md) | `route_query` | Natural-language intent classification, parameter extraction, confidence scoring |
| [Schemas & Validation](./schemas.md) | All tools | Pydantic input/output models, structured errors, field validators |

## Using Skills

Skills are `.md` files with:
- YAML frontmatter (metadata)
- Concept explanations with LaTeX math
- MCP tool reference tables
- Worked examples in Python
- Common pitfalls

Read the skill file, then call the corresponding MCP tools in your agent.

## Contributing

Add a new skill:
1. Create `skills/<name>.md`
2. Add YAML frontmatter with `title`, `skill_type`, `layer`, `tools`, `version`
3. Include concepts, tool reference, worked example, pitfalls
4. Update this README
