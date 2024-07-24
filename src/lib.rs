use numpy::{IntoPyArray, PyArray1, PyReadonlyArray1};
use pyo3::prelude::*;
use pyo3::types::PyList;

mod gr1a;
mod gr2m;
mod gr4h;
mod gr4j;
mod gr5j;
mod gr6j;
mod s_curves;

#[pyfunction]
#[pyo3(name = "gr1a")]
fn gr1a_py<'py>(
    py: Python<'py>,
    parameters: &PyList,
    rainfall: PyReadonlyArray1<f64>,
    evapotranspiration: PyReadonlyArray1<f64>,
) -> &'py PyArray1<f64> {
    let v_param = parameters.extract::<Vec<f64>>().unwrap();
    let n_rainfall = rainfall.as_array();
    let n_evap = evapotranspiration.as_array();

    let flow = gr1a::gr1a(&v_param, n_rainfall, n_evap);
    flow.into_pyarray(py)
}

#[pyfunction]
#[pyo3(name = "gr2m")]
fn gr2m_py<'py>(
    py: Python<'py>,
    parameters: &PyList,
    rainfall: PyReadonlyArray1<f64>,
    evapotranspiration: PyReadonlyArray1<f64>,
    states: PyReadonlyArray1<f64>,
) -> (&'py PyArray1<f64>, &'py PyArray1<f64>) {
    let v_param = parameters.extract::<Vec<f64>>().unwrap();
    let n_rainfall = rainfall.as_array(); // Convert to ndarray type
    let n_evap = evapotranspiration.as_array();
    let n_states = states.as_array();

    let (states, flow) = gr2m::gr2m(&v_param, n_rainfall, n_evap, n_states);
    (states.into_pyarray(py), flow.into_pyarray(py))
}

#[pyfunction]
#[pyo3(name = "gr4j")]
fn gr4j_py<'py>(
    py: Python<'py>,
    parameters: &PyList,
    rainfall: PyReadonlyArray1<f64>,
    evapotranspiration: PyReadonlyArray1<f64>,
    states: PyReadonlyArray1<f64>,
    uh1: PyReadonlyArray1<f64>,
    uh2: PyReadonlyArray1<f64>,
) -> (
    &'py PyArray1<f64>,
    &'py PyArray1<f64>,
    &'py PyArray1<f64>,
    &'py PyArray1<f64>,
) {
    let v_param = parameters.extract::<Vec<f64>>().unwrap();
    let n_rainfall = rainfall.as_array(); // Convert to ndarray type
    let n_evap = evapotranspiration.as_array();
    let n_states = states.as_array();
    let n_uh1 = uh1.as_array();
    let n_uh2 = uh2.as_array();

    let (states, uh1, uh2, flow) = gr4j::gr4j(&v_param, n_rainfall, n_evap, n_states, n_uh1, n_uh2);
    (
        states.into_pyarray(py),
        uh1.into_pyarray(py),
        uh2.into_pyarray(py),
        flow.into_pyarray(py),
    )
}

#[pyfunction]
#[pyo3(name = "gr5j")]
fn gr5j_py<'py>(
    py: Python<'py>,
    parameters: &PyList,
    rainfall: PyReadonlyArray1<f64>,
    evapotranspiration: PyReadonlyArray1<f64>,
    states: PyReadonlyArray1<f64>,
    uh2: PyReadonlyArray1<f64>,
) -> (&'py PyArray1<f64>, &'py PyArray1<f64>, &'py PyArray1<f64>) {
    let v_param = parameters.extract::<Vec<f64>>().unwrap();

    let n_rainfall = rainfall.as_array(); // Convert to ndarray type
    let n_evap = evapotranspiration.as_array();
    let n_states = states.as_array();
    let n_uh2 = uh2.as_array();
    let (states, uh2, flow) = gr5j::gr5j(&v_param, n_rainfall, n_evap, n_states, n_uh2);
    (
        states.into_pyarray(py),
        uh2.into_pyarray(py),
        flow.into_pyarray(py),
    )
}

#[pyfunction]
#[pyo3(name = "gr6j")]
fn gr6j_py<'py>(
    py: Python<'py>,
    parameters: &PyList,
    rainfall: PyReadonlyArray1<f64>,
    evapotranspiration: PyReadonlyArray1<f64>,
    states: PyReadonlyArray1<f64>,
    uh1: PyReadonlyArray1<f64>,
    uh2: PyReadonlyArray1<f64>,
) -> (
    &'py PyArray1<f64>,
    &'py PyArray1<f64>,
    &'py PyArray1<f64>,
    &'py PyArray1<f64>,
) {
    let v_param = parameters.extract::<Vec<f64>>().unwrap();

    let n_rainfall = rainfall.as_array(); // Convert to ndarray type
    let n_evap = evapotranspiration.as_array();
    let n_states = states.as_array();
    let n_uh1 = uh1.as_array();
    let n_uh2 = uh2.as_array();
    let (states, uh1, uh2, flow) = gr6j::gr6j(&v_param, n_rainfall, n_evap, n_states, n_uh1, n_uh2);
    (
        states.into_pyarray(py),
        uh1.into_pyarray(py),
        uh2.into_pyarray(py),
        flow.into_pyarray(py),
    )
}

#[pyfunction]
#[pyo3(name = "gr4h")]
fn gr4h_py<'py>(
    py: Python<'py>,
    parameters: &PyList,
    rainfall: PyReadonlyArray1<f64>,
    evapotranspiration: PyReadonlyArray1<f64>,
    states: PyReadonlyArray1<f64>,
    uh1: PyReadonlyArray1<f64>,
    uh2: PyReadonlyArray1<f64>,
) -> (
    &'py PyArray1<f64>,
    &'py PyArray1<f64>,
    &'py PyArray1<f64>,
    &'py PyArray1<f64>,
) {
    let v_param = parameters.extract::<Vec<f64>>().unwrap();

    let n_rainfall = rainfall.as_array(); // Convert to ndarray type
    let n_evap = evapotranspiration.as_array();
    let n_states = states.as_array();
    let n_uh1 = uh1.as_array();
    let n_uh2 = uh2.as_array();
    let (states, uh1, uh2, flow) = gr4h::gr4h(&v_param, n_rainfall, n_evap, n_states, n_uh1, n_uh2);
    (
        states.into_pyarray(py),
        uh1.into_pyarray(py),
        uh2.into_pyarray(py),
        flow.into_pyarray(py),
    )
}

/// A Python module implemented in Rust.
#[pymodule]
fn _hydrogr(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(gr1a_py, m)?)?;
    m.add_function(wrap_pyfunction!(gr2m_py, m)?)?;
    m.add_function(wrap_pyfunction!(gr4j_py, m)?)?;
    m.add_function(wrap_pyfunction!(gr5j_py, m)?)?;
    m.add_function(wrap_pyfunction!(gr6j_py, m)?)?;
    m.add_function(wrap_pyfunction!(gr4h_py, m)?)?;
    Ok(())
}
