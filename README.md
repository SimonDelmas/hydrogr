[![PyPi version](https://img.shields.io/pypi/v/hydrogr.svg)](https://pypi.python.org/pypi/hydrogr/)
[![](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/SimonDelmas/hydrogr/build_all.yml)
![GitHub issues](https://img.shields.io/github/issues/SimonDelmas/hydrogr)
![GitHub License](https://img.shields.io/github/license/SimonDelmas/hydrogr)
![PyPI - Downloads](https://img.shields.io/pypi/dm/hydrogr)

# HydroGR ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Rust](https://img.shields.io/badge/rust-%23000000.svg?style=for-the-badge&logo=rust&logoColor=white)

HydroGR is a Python package for hydrological modeling that implements several conceptual rainfall-runoff models for watershed simulation and streamflow prediction:

- **GR4H**: 4-parameter hourly model
- **GR4J**: 4-parameter daily model  
- **GR5J**: 5-parameter daily model
- **GR6J**: 6-parameter daily model
- **GR2M**: 2-parameter monthly model
- **GR1A**: 1-parameter annual model

This package is inspired by the INRAE R language package: [airGR](https://cran.r-project.org/web/packages/airGR/index.html).

## Getting Started

### Installation

The package can be installed with pip:

```bash
python -m pip install hydrogr
```

Test the installation by importing the package in Python:

```python
import hydrogr
print(hydrogr.__version__)
```

### Examples

Examples based on the examples in the airGR package are available in the [example folder](example/) for the different models.

An example for calibrating models using [spotpy](https://github.com/thouska/spotpy) is also available in the [calibrating_gr4j.ipynb](example/calibrating_gr4j.ipynb) notebook.

![gr4h](https://github.com/SimonDelmas/hydrogr/assets/28869386/3c980461-42d7-4de9-bae7-6bb127c978f1)

## License

This project is licensed under the GPL-2.0 License - see the [LICENSE.txt](LICENSE.txt) file for details.
