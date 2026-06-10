# rocket-tools Skills Library

Human-readable engineering skills with MCP cross-references.

## Skills

| Skill | Tools | Description |
|-------|-------|-------------|
| [Structural Analysis](./structural-analysis.md) | `beam_analysis`, `material_lookup`, `unit_convert` | Beams, columns, material selection |
| [Aerodynamics](./aerodynamics.md) | `reynolds_number`, `mach_number`, `dynamic_pressure`, `aero_analysis`, `isa_atmosphere` | Flow characterization, ISA lookups |
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
