"""Load workflows from YAML files."""

from importlib.resources import files
from pathlib import Path

import yaml

from rocket_tools.utils.validation import ValidationError

from .engine import Workflow, WorkflowStep


def load_workflow(path: str | Path) -> Workflow:
    path = Path(path)
    with open(path) as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValidationError(
            f"Workflow file '{path}' must contain a YAML mapping",
            "workflow",
            "mapping",
        )
    if "name" not in data:
        raise ValidationError("Workflow is missing required field: name", "name", "required")
    if "steps" not in data or not isinstance(data["steps"], list):
        raise ValidationError("Workflow must define a list of steps", "steps", "list")

    steps = []
    for idx, step_data in enumerate(data["steps"]):
        if not isinstance(step_data, dict):
            raise ValidationError(
                f"Workflow step {idx} must be a mapping",
                f"steps[{idx}]",
                "mapping",
            )
        for field in ("id", "tool", "save_as"):
            if field not in step_data:
                raise ValidationError(
                    f"Workflow step {idx} is missing required field: {field}",
                    f"steps[{idx}].{field}",
                    "required",
                )
        params = step_data.get("params", {})
        if not isinstance(params, dict):
            raise ValidationError(
                f"Workflow step {idx} params must be a mapping",
                f"steps[{idx}].params",
                "mapping",
            )
        steps.append(
            WorkflowStep(
                id=step_data["id"],
                tool=step_data["tool"],
                params=params,
                save_as=step_data["save_as"],
            )
        )

    return Workflow(
        name=data["name"],
        version=data.get("version", "0.1.0"),
        description=data.get("description", ""),
        inputs=data.get("inputs", {}),
        steps=steps,
        outputs=data.get("outputs", []),
    )


def load_all_workflows(built_in_dir: Path, custom_dir: Path | None = None) -> dict[str, Workflow]:
    workflows = {}
    for path in built_in_dir.glob("*.yaml"):
        wf = load_workflow(path)
        workflows[wf.name] = wf
    if custom_dir and custom_dir.exists():
        for path in custom_dir.glob("*.yaml"):
            wf = load_workflow(path)
            workflows[wf.name] = wf
    return workflows


def built_in_workflow_dir() -> Path:
    """Return the package directory containing built-in workflow YAML files."""
    return Path(str(files("rocket_tools.workflows") / "built_in"))


def list_builtin_workflows() -> list[str]:
    """List built-in workflow names available in the installed package."""
    return sorted(path.stem for path in built_in_workflow_dir().glob("*.yaml"))


def load_builtin_workflow(name: str) -> Workflow:
    """Load a built-in workflow by name, with or without the .yaml suffix."""
    workflow_name = name[:-5] if name.endswith(".yaml") else name
    path = built_in_workflow_dir() / f"{workflow_name}.yaml"
    if not path.exists():
        available = ", ".join(list_builtin_workflows())
        raise ValueError(f"Unknown built-in workflow '{name}'. Available workflows: {available}")
    return load_workflow(path)
