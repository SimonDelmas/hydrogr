# hydrogr

hydrogr is a python language software package for hydrological modelling, that implement several conceptual rainfall-runoff models (GR4H, GR4J, GR5J, GR6J, GR2M, GR1A).
It is inspired from Irstea R language package: [airGR](https://cran.r-project.org/web/packages/airGR/index.html).

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

hydrogr requires :

* Python 3
* [Numpy](https://github.com/numpy/numpy) for fortran integration and array manipulation.
* [Pandas](https://github.com/pandas-dev/pandas) for dataset and time series handling.

### Installing

To install the package, clone or download the repository and use the setup.py :

```bash
git clone https://github.com/SimonDelmas/hydrogr.git
cd hydrogr
python ./setup.py install
```

### Running the tests

After installation, you can launch the test suite with pytest :

```bash
pytest
```

## Getting started

Examples based on the examples in the airGR package are available in the repository.

<img src="https://user-images.githubusercontent.com/54593457/63867945-0795cf00-c9b6-11e9-9fef-18c0fc564d3e.png" alt="GR4H example" width="600   "/>

## License

This project is licensed under the GLP-2.0 License - see the [LICENSE.md](LICENSE.md) file for details.
