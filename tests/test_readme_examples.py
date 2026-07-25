"""Execute the runnable code in README.md and examples/, so docs can't silently rot.

The README's headline examples had drifted badly from the real API (wrong keys,
renamed functions, non-existent kwargs). This test runs each self-contained Python
block and each example script so a broken example fails CI instead of a new user.
"""

import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _readme_blocks() -> list[str]:
    md = (ROOT / "README.md").read_text(encoding="utf-8")
    blocks = re.findall(r"```python\n(.*?)```", md, re.S)
    # Skip blocks that need an external file or a long-lived object we can't provide.
    return [b for b in blocks if "load_workflow" not in b and "my_workflow" not in b]


@pytest.mark.parametrize("code", _readme_blocks())
def test_readme_python_block_runs(code: str) -> None:
    exec(compile(code, "<readme>", "exec"), {})


@pytest.mark.parametrize(
    "script",
    [
        "quickstart.py",
        "ascent_and_sizing.py",
        "sounding_rocket_flight.py",
        "orbit_determination.py",
    ],
)
def test_example_script_runs(script: str) -> None:
    src = (ROOT / "examples" / script).read_text(encoding="utf-8")
    exec(compile(src, script, "exec"), {"__name__": "__main__"})
