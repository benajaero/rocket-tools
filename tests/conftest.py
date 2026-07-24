"""Pytest configuration.

Disable Numba JIT during the test run. Numba-compiled functions are invisible to
coverage.py (the bytecode never executes), which understates real coverage of the
JIT hot paths. Running them as pure Python exercises the same logic, lets coverage
measure it honestly, and keeps numerical results identical. Set before numba is first
imported so ``@njit`` decorations become no-ops.
"""

import os

os.environ.setdefault("NUMBA_DISABLE_JIT", "1")
