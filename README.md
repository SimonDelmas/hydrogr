# hydrogr

Hydrogr is a python language software package for hydrological modelling, that implement several conceptual rainfall-runoff models (GR4H, GR4J, GR5J, GR6J, GR2M, GR1A).
It is inspired from Irstea R language package: [airGR](https://cran.r-project.org/web/packages/airGR/index.html).

## Getting Started

### Installation

The package can be installed with pip :

```bash
python -m pip install hydrogr
```

Test the installation by importing the package in Python :

```python
import hydrogr
print(hydrogr.__version__)
```

### Examples

Examples based on the examples in the airGR package are available in the example folder for the different models.

An example for calibrating models using [spotpy](https://github.com/thouska/spotpy) is also available.

<img src="https://user-images.githubusercontent.com/54593457/63867945-0795cf00-c9b6-11e9-9fef-18c0fc564d3e.png" alt="GR4H example" width="600   "/>

## License

This project is licensed under the GLP-2.0 License - see the [LICENSE.md](LICENSE.md) file for details.
