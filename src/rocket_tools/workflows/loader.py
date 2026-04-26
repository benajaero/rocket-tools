"""Load workflows from YAML files."""

import yaml
from pathlib import Path

from .engine import Workflow, WorkflowStep


def load_workflow(path: Path) -> Workflow:
    with open(path) as f:
        data = yaml.safe_load(f)

    steps = []
    for step_data in data["steps"]:
        steps.append(WorkflowStep(
            id=step_data["id"],
            tool=step_data["tool"],
            params=step_data.get("params", {}),
            save_as=step_data["save_as"],
        ))

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
