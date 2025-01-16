# Contributing to the package

## Development stack

We recommend using [uv](https://docs.astral.sh/uv/) as project manager.
For compiling Rust code and produce a Python module you will need :

### Rust

Install a Rust compiler using [rustup](https://www.rust-lang.org/tools/install)

### Maturin

To install [Maturin](https://github.com/PyO3/maturin) simply do :

```batch
uv tool install maturin
```

## Edit the project

### Get the project

```bash
git clone https://github.com/SimonDelmas/hydrogr.git
```

### Initialize environment and Python module

To initialize or update the Python virtual environment use :

```bash
uv sync
```

To produce the Python module from Rust code in development mode do :

```bash
maturin.exe develop --uv
```

It will produce a `_hydrogr` Python module located in the `python/hydrogr` directory and which is called by the different models.

### Edit Rust code

- Write Rust function and unit tests
- Test with `cargo test`
- Produce Python module from Rust code with `maturin.exe develop --uv`

### Edit Python Code

- Write Python code
- Test with pytest : `uv run pytest`

## Compiling

```bash
uv build
```

Or alternatively :

```bash
maturin.exe build --release --out dist --find-interpreter
```

Note that the github pipeline is configured to target multiple architecture when a new release is triggered.
