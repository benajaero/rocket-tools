# rocket-tools

Aerospace engineering intelligence for AI agents.

## Installation

```bash
pip install rocket-tools
```

Or install from source with Rust kernels (recommended):

```bash
pip install maturin
maturin develop --release
```

## Quick Start

```python
from rocket_tools.materials.isa import isa_atmosphere

result = isa_atmosphere(altitude_m=10000)
print(result["temperature_k"])  # 223.15
```

## MCP Server

```bash
python -m rocket_tools.server
```

## Performance

All tools complete in < 1ms when using Rust kernels.

## License

MIT
