"""Rendering backend for visualization tools: lazy matplotlib + dual-return contract.

Visualization is optional. matplotlib is not a core dependency; it lives in the
``viz`` extra (``pip install rocket-tools[viz]``). ``require_matplotlib`` imports it
lazily with the non-interactive Agg backend and raises a structured ToolError if it is
missing, so the core install stays lightweight and errors stay uniform.

``figure_to_result`` implements the dual-return contract used by every viz tool:
``render="data"`` (default) returns a JSON-safe dict with a base64 PNG plus the
underlying data ``series``; ``render="image"`` returns FastMCP ``ImageContent`` for
clients that render native MCP images. Errors always return the dict error, never an
image, so the server's uniform error handling still applies.
"""

import base64
import io
from typing import Any

from rocket_tools.utils.validation import ToolError


def require_matplotlib() -> Any:
    """Import matplotlib with the Agg backend, or raise a structured MISSING_DEPENDENCY."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        return plt
    except ImportError as e:  # pragma: no cover - exercised via monkeypatch in tests
        raise ToolError(
            "matplotlib is required for visualization tools",
            error_code="MISSING_DEPENDENCY",
            parameter="",
            constraint="matplotlib installed",
            suggestion="Install the visualization extra: pip install rocket-tools[viz]",
        ) from e


def _to_native(series: dict) -> dict:
    """Convert numpy arrays / scalars in ``series`` to JSON-safe Python lists/floats."""
    out: dict[str, Any] = {}
    for key, val in series.items():
        if hasattr(val, "tolist"):
            out[key] = [round(float(x), 6) for x in val.tolist()]
        elif isinstance(val, (list, tuple)):
            out[key] = [round(float(x), 6) for x in val]
        else:
            out[key] = val
    return out


def figure_to_result(
    fig: Any,
    series: dict,
    meta: dict,
    render: str,
    output_path: str | None = None,
) -> dict:
    """Render ``fig`` to PNG and return per the dual-return contract.

    Returns the data dict, or (render="image") FastMCP ``ImageContent`` — typed as
    ``dict`` so the whole viz chain stays uniformly typed; FastMCP handles the image
    object at the protocol boundary. Always closes the figure; writes to
    ``output_path`` if given.
    """
    plt = require_matplotlib()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    plt.close(fig)
    png_bytes = buf.getvalue()

    if output_path:
        with open(output_path, "wb") as f:
            f.write(png_bytes)

    if render == "image":
        from mcp.server.fastmcp import Image

        return Image(data=png_bytes, format="png").to_image_content()  # type: ignore[return-value]

    return {
        "image_base64": base64.b64encode(png_bytes).decode("ascii"),
        "mime_type": "image/png",
        "format": "png",
        "series": _to_native(series),
        "meta": meta,
        "output_path": output_path,
    }
