"""Command-line interface for rocket-tools."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

TOOL_NAMES = [
    "unit_convert",
    "material_lookup",
    "list_materials",
    "isa_atmosphere",
    "beam_analysis",
    "reynolds_number",
    "mach_number",
    "dynamic_pressure",
    "lift_coefficient",
    "drag_coefficient",
    "skin_friction_coefficient",
    "aero_analysis",
]


def _print_json(data: Any) -> None:
    print(json.dumps(data, indent=2, sort_keys=True))


def _json_arg(value: str) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise argparse.ArgumentTypeError(f"Invalid JSON: {exc.msg}") from exc


def _load_inputs_file(path: str) -> dict:
    input_path = Path(path)
    try:
        text = input_path.read_text()
    except OSError as exc:
        raise argparse.ArgumentTypeError(f"Cannot read inputs file: {exc}") from exc

    try:
        if input_path.suffix.lower() in {".yaml", ".yml"}:
            data = yaml.safe_load(text)
        else:
            data = json.loads(text)
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise argparse.ArgumentTypeError(f"Invalid inputs file: {exc}") from exc

    if not isinstance(data, dict):
        raise argparse.ArgumentTypeError("Inputs file must contain a JSON/YAML object")
    return data


def _add_common_aero_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--velocity", type=float, required=True, help="Velocity in m/s")
    parser.add_argument("--altitude", type=float, required=True, help="Altitude in m")


def _cmd_serve(args: argparse.Namespace) -> None:
    if args.transport == "stdio":
        from rocket_tools.server import main as server_main

        server_main()
        return

    import uvicorn

    uvicorn.run("rocket_tools.asgi:app", host=args.host, port=args.port)


def _cmd_convert(args: argparse.Namespace) -> None:
    from rocket_tools.utils import unit_convert

    _print_json(unit_convert(args.value, args.from_unit, args.to_unit))


def _cmd_tools(args: argparse.Namespace) -> None:
    _print_json({"count": len(TOOL_NAMES), "tools": TOOL_NAMES})


def _cmd_isa(args: argparse.Namespace) -> None:
    from rocket_tools.materials import isa_atmosphere

    _print_json(isa_atmosphere(args.altitude))


def _cmd_material(args: argparse.Namespace) -> None:
    from rocket_tools.materials import material_lookup

    _print_json(material_lookup(args.name, args.property))


def _cmd_materials(args: argparse.Namespace) -> None:
    from rocket_tools.materials import list_materials

    materials = list_materials(args.category)
    _print_json({"count": len(materials), "materials": materials})


def _cmd_aero(args: argparse.Namespace) -> None:
    from rocket_tools.aerodynamics import aero_analysis

    _print_json(
        aero_analysis(
            velocity=args.velocity,
            altitude_m=args.altitude,
            characteristic_length=args.characteristic_length,
            reference_area=args.reference_area,
            lift=args.lift,
            drag=args.drag,
        )
    )


def _cmd_beam(args: argparse.Namespace) -> None:
    from rocket_tools.structural import beam_analysis

    _print_json(
        beam_analysis(
            load=args.load,
            length=args.length,
            youngs_modulus=args.youngs_modulus,
            cross_section=args.cross_section,
            load_type=args.load_type,
            support_type=args.support_type,
            yield_strength=args.yield_strength,
        )
    )


def _cmd_route(args: argparse.Namespace) -> None:
    from rocket_tools.router import ClarificationRequest, ToolCall, route_query

    result = route_query(args.query)
    if isinstance(result, ToolCall):
        _print_json(
            {
                "type": "tool_call",
                "tool_name": result.tool_name,
                "params": result.params,
                "confidence": result.confidence,
                "reasoning": result.reasoning,
            }
        )
    elif isinstance(result, ClarificationRequest):
        _print_json(
            {
                "type": "clarification",
                "message": result.message,
                "possible_tools": result.possible_tools,
                "missing_params": result.missing_params,
            }
        )


def _cmd_workflow_list(args: argparse.Namespace) -> None:
    from rocket_tools.workflows import list_builtin_workflows

    _print_json({"workflows": list_builtin_workflows()})


def _cmd_workflow_run(args: argparse.Namespace) -> None:
    from rocket_tools.workflows import load_builtin_workflow, load_workflow, run_workflow

    workflow = (
        load_workflow(Path(args.file))
        if args.file is not None
        else load_builtin_workflow(args.workflow)
    )
    inputs = args.inputs_file if args.inputs_file is not None else args.inputs
    result = run_workflow(workflow, inputs)
    _print_json({"outputs": result.outputs, "trace": result.trace if args.trace else None})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rocket-tools",
        description="Aerospace engineering calculations, workflows, and MCP server.",
    )
    subparsers = parser.add_subparsers(dest="command")

    serve = subparsers.add_parser("serve", help="Run the MCP server")
    serve.add_argument("--transport", choices=("stdio", "sse"), default="stdio")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    serve.set_defaults(func=_cmd_serve)

    convert = subparsers.add_parser("convert", help="Convert engineering units")
    convert.add_argument("value", type=float)
    convert.add_argument("from_unit")
    convert.add_argument("to_unit")
    convert.set_defaults(func=_cmd_convert)

    tools = subparsers.add_parser("tools", help="List available calculation tools")
    tools.set_defaults(func=_cmd_tools)

    isa = subparsers.add_parser("isa", help="Evaluate ISA atmosphere properties")
    isa.add_argument("altitude", type=float)
    isa.set_defaults(func=_cmd_isa)

    material = subparsers.add_parser("material", help="Look up material properties")
    material.add_argument("name")
    material.add_argument("--property", default="all")
    material.set_defaults(func=_cmd_material)

    materials = subparsers.add_parser("materials", help="List bundled materials")
    materials.add_argument("--category", help="Optional material family or application category")
    materials.set_defaults(func=_cmd_materials)

    aero = subparsers.add_parser("aero", help="Run a combined aerodynamic analysis")
    _add_common_aero_args(aero)
    aero.add_argument("--characteristic-length", type=float, required=True)
    aero.add_argument("--reference-area", type=float, required=True)
    aero.add_argument("--lift", type=float, default=0.0)
    aero.add_argument("--drag", type=float, default=0.0)
    aero.set_defaults(func=_cmd_aero)

    beam = subparsers.add_parser("beam", help="Run beam analysis")
    beam.add_argument("--load", type=float, required=True)
    beam.add_argument("--length", type=float, required=True)
    beam.add_argument("--youngs-modulus", type=float, required=True)
    beam.add_argument("--cross-section", type=_json_arg, required=True)
    beam.add_argument("--load-type", default="point_midspan")
    beam.add_argument("--support-type", default="simply_supported")
    beam.add_argument("--yield-strength", type=float)
    beam.set_defaults(func=_cmd_beam)

    route = subparsers.add_parser("route", help="Route a natural-language query")
    route.add_argument("query")
    route.set_defaults(func=_cmd_route)

    workflow = subparsers.add_parser("workflow", help="List or run workflows")
    workflow_subparsers = workflow.add_subparsers(dest="workflow_command", required=True)

    workflow_list = workflow_subparsers.add_parser("list", help="List built-in workflows")
    workflow_list.set_defaults(func=_cmd_workflow_list)

    workflow_run = workflow_subparsers.add_parser("run", help="Run a workflow")
    workflow_run.add_argument("workflow", nargs="?", help="Built-in workflow name")
    workflow_run.add_argument("--file", help="Path to a custom workflow YAML file")
    inputs_group = workflow_run.add_mutually_exclusive_group(required=True)
    inputs_group.add_argument("--inputs", type=_json_arg, help="Input object as JSON")
    inputs_group.add_argument(
        "--inputs-file",
        type=_load_inputs_file,
        help="Path to a JSON or YAML file containing workflow inputs",
    )
    workflow_run.add_argument("--trace", action="store_true", help="Include step trace")
    workflow_run.set_defaults(func=_cmd_workflow_run)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help()
        return

    if getattr(args, "workflow_command", None) == "run" and not args.file and not args.workflow:
        parser.error("workflow run requires a built-in workflow name or --file")

    args.func(args)


if __name__ == "__main__":
    main()
