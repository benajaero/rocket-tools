# Examples

Runnable scripts using the public API. Install the package first, then run any of them:

```bash
pip install rocket-tools
python examples/quickstart.py
python examples/ascent_and_sizing.py
python examples/sounding_rocket_flight.py
python examples/orbit_determination.py
```

- **`quickstart.py`** — materials, beam deflection, standard atmosphere, a normal shock, and mission delta-v.
- **`ascent_and_sizing.py`** — size a vehicle from a delta-v budget, simulate its ascent through the atmosphere, and optimize the staging (new in 0.4.0).
- **`sounding_rocket_flight.py`** — a full preliminary pass on a small solid-motor rocket: reduce its thrust curve, check Barrowman static margin, fly the ascent, size the parachute, and run an airframe thermal check.
- **`orbit_determination.py`** — solve Lambert's problem for a transfer, read off the classical orbital elements, propagate the state forward, and rebuild the state vector from the elements.

To use the tools from an AI agent instead, see the MCP server and Claude Desktop
setup in the main [README](../README.md#4-mcp-server).
