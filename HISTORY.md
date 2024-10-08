# History

## 1.2.1 (2024-08)

Fix GR6J exponential store flow (issue #2), thanks to @Dr-Jamie-Brown

## 1.2.0 (2024-07)

Technical change : avoid using unsafe as_array_mut. Function now return a new array instead of modifying the existing one.
This should simplify retrieving of intermediate states.

## 1.1.0  (2024-01)

Windows x86 is no more supported as Pandas do not produce wheel for this architecture : https://github.com/pandas-dev/pandas/issues/54979

## 1.0.1  (2024-01)

Fix deprecated offset alias in [pandas 2.2.0](https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases)

## 1.0.0  (2023-02)

Change model API to simplify the use of the package :

* Each model now expose getter and setter for static parameters and state vector. They are defined using dictionary to improve clarity.
* Input time series are pass to the model at execution time instead of during instantiation.

## 0.2.0 (2023-02)

Change model implementation from Fortran to Rust to :

* Get rid of the dependency on Numpy for compilation and use maturin and github actions for cross compilation.
* To have a more readable and maintainable code.
* To discover RUST.

## 0.1.0 (2019-08)

First release of the package, based on Irstea Fortran code wrapped with Python using numpy distutils.