# Contributing to the package

## Development stack

### Python

Install [python](https://www.python.org/) with pylauncher.

### Pipx

[Pipx](https://pypa.github.io/pipx/installation/) is a tool to install and run Python application in isolated environnements.
It also ensure application are added to the PATH environnement variable to be use everywhere.
To install pipx do :

``` batch
py.exe -m pip install --user pipx
py.exe -m pipx ensurepath
```

### Rust

Install a Rust compiler using [rustup](https://www.rust-lang.org/tools/install)

### Maturin

Finally to install [Maturin](https://github.com/PyO3/maturin) do

```batch
pipx install maturin
```

### (Optional) Rye

We recommend using [Rye](https://rye.astral.sh/) to manage the project.
Simply install the software by following the instruction and refers to the [rust module](https://rye.astral.sh/guide/rust/) section for building the project.

## Edit the project

### Get the project

```bash
git clone https://github.com/SimonDelmas/hydrogr.git
```

### Using Rye

Simply do :

```bash
rye sync
```

You still can use `maturin.exe develop` for Rust module development.

### Without Rye

#### Virtual environment

Create a virtual environnement. I recommend to create it into the project directory so Maturin can find it easily. For example :

```bash
cd hydrogr
py.exe -m venv .venv
```

#### Development install

Simply do :

```bash
.venv\Scripts\python.exe -m pip install -e .[test]
maturin.exe develop
```

This will install the python package and its dependencies in editable mode in the virtual env.
`maturin.exe develop` will compile and deploy the Rust Python module in debug mode.

### Edit Rust code

- Write Rust function and unit tests
- Test with `cargo test`

### Edit Python Code

- Write Python code
- Test with pytest : `.venv\Scripts\pytest.exe`

## Compiling

If you are using *Rye* :

`rye build`

Else :

`maturin.exe build --release --out dist --find-interpreter`

Note that the github pipeline is configured to target multiple architecture when a new release is triggered.
