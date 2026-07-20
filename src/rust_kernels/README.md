# rocket-tools-kernels (experimental)

Optional Rust/PyO3 acceleration kernels for rocket-tools. **This crate is not
part of the published `rocket-tools` package.** The distributed wheel is pure
Python accelerated by Numba; these kernels are a scaffold for a future native
fast path and are built separately, if at all.

## Status

- Compiles cleanly: `cargo check` and `cargo build --release` pass, `cargo clippy`
  is warning-free.
- **Not wired into Python.** There is no import of this extension from
  `rocket_tools`, and no pure-Python fallback loader yet. Building the `.dylib`/
  `.so` here does not change how the installed package behaves.
- Not included in the sdist or wheel (setuptools packages only `src/rocket_tools`).

## Building

Requires a Rust toolchain. On macOS the linker flags in `.cargo/config.toml`
let a bare build resolve Python symbols at load time; on Linux the
`extension-module` feature handles that by default.

```bash
cargo build --release            # produces target/release/librocket_tools_kernels.*
```

To turn it into an importable extension module, use maturin (not required by the
package):

```bash
maturin develop --release
```

## Parity notes (before this is wired in)

- Beam, section, Reynolds, Mach, lift, and drag-polar kernels mirror the Python
  formulas (e.g. simply-supported deflection PL³/48EI, cantilever PL³/3EI).
- `isa_atmosphere_lookup` is still the **legacy 3-layer, 0–25 km** model. The
  Python `isa_atmosphere` is now the full 7-layer US Std Atm 1976 (0–86 km); this
  kernel must be brought to parity before it can back the Python tool.

See `docs/RELEASE_TODO.md` (Packaging / Release) for the remaining maturin +
cibuildwheel + pure-Python-fallback work required to ship native wheels.
