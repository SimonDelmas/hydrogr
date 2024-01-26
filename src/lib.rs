use pyo3::prelude::*;
use pyo3::types::PyList;
use numpy::PyArray1;

mod s_curves;
mod gr1a;
mod gr2m;
mod gr4j;
mod gr5j;
mod gr6j;
mod gr4h;

// https://www.lpalmieri.com/posts/2019-02-23-scientific-computing-a-rust-adventure-part-0-vectors/
// https://itnext.io/how-to-bind-python-numpy-with-rust-ndarray-2efa5717ed21
// https://medium.com/@MatthieuL49/a-mixed-rust-python-project-24491e2af424 => For test and maturin


#[pyfunction]
#[pyo3(name = "gr1a")]
fn gr1a_py(parameters: &PyList, rainfall: &PyArray1<f64>, evapotranspiration: &PyArray1<f64>, flow: &PyArray1<f64>) {
    let v_param = parameters.extract::<Vec<f64>>().unwrap();
    let mut n_rainfall = unsafe { rainfall.as_array_mut() }; // Convert to ndarray type
    let mut n_evap = unsafe { evapotranspiration.as_array_mut() };
    let mut n_flow = unsafe { flow.as_array_mut() };
    gr1a::gr1a(&v_param, &mut n_rainfall, &mut n_evap, &mut n_flow);

}


#[pyfunction]
#[pyo3(name = "gr2m")]
fn gr2m_py(parameters: &PyList, rainfall: &PyArray1<f64>, evapotranspiration: &PyArray1<f64>, states: &PyArray1<f64>, flow: &PyArray1<f64>) {
    let v_param = parameters.extract::<Vec<f64>>().unwrap();
    let mut n_rainfall = unsafe { rainfall.as_array_mut() }; // Convert to ndarray type
    let mut n_evap = unsafe { evapotranspiration.as_array_mut() };
    let mut n_states = unsafe { states.as_array_mut() };
    let mut n_flow = unsafe { flow.as_array_mut() };
    gr2m::gr2m(&v_param, &mut n_rainfall, &mut n_evap, &mut n_states, &mut n_flow);

}


#[pyfunction]
#[pyo3(name = "gr4j")]
fn gr4j_py(parameters: &PyList, rainfall: &PyArray1<f64>, evapotranspiration: &PyArray1<f64>, states: &PyArray1<f64>, uh1: &PyArray1<f64>, uh2: &PyArray1<f64>, flow: &PyArray1<f64>) {

    let v_param = parameters.extract::<Vec<f64>>().unwrap();

    let mut n_rainfall = unsafe { rainfall.as_array_mut() }; // Convert to ndarray type
    let mut n_evap = unsafe { evapotranspiration.as_array_mut() };
    let mut n_states = unsafe { states.as_array_mut() };
    let mut n_uh1 = unsafe { uh1.as_array_mut() };
    let mut n_uh2 = unsafe { uh2.as_array_mut() };
    let mut n_flow = unsafe { flow.as_array_mut() };
    gr4j::gr4j(&v_param, &mut n_rainfall, &mut n_evap, &mut n_states, &mut n_uh1, &mut n_uh2, &mut n_flow);
}


#[pyfunction]
#[pyo3(name = "gr5j")]
fn gr5j_py(parameters: &PyList, rainfall: &PyArray1<f64>, evapotranspiration: &PyArray1<f64>, states: &PyArray1<f64>, uh2: &PyArray1<f64>, flow: &PyArray1<f64>) {

    let v_param = parameters.extract::<Vec<f64>>().unwrap();

    let mut n_rainfall = unsafe { rainfall.as_array_mut() }; // Convert to ndarray type
    let mut n_evap = unsafe { evapotranspiration.as_array_mut() };
    let mut n_states = unsafe { states.as_array_mut() };
    let mut n_uh2 = unsafe { uh2.as_array_mut() };
    let mut n_flow = unsafe { flow.as_array_mut() };
    gr5j::gr5j(&v_param, &mut n_rainfall, &mut n_evap, &mut n_states, &mut n_uh2, &mut n_flow);
}


#[pyfunction]
#[pyo3(name = "gr6j")]
fn gr6j_py(parameters: &PyList, rainfall: &PyArray1<f64>, evapotranspiration: &PyArray1<f64>, states: &PyArray1<f64>, uh1: &PyArray1<f64>, uh2: &PyArray1<f64>, flow: &PyArray1<f64>) {

    let v_param = parameters.extract::<Vec<f64>>().unwrap();

    let mut n_rainfall = unsafe { rainfall.as_array_mut() }; // Convert to ndarray type
    let mut n_evap = unsafe { evapotranspiration.as_array_mut() };
    let mut n_states = unsafe { states.as_array_mut() };
    let mut n_uh1 = unsafe { uh1.as_array_mut() };
    let mut n_uh2 = unsafe { uh2.as_array_mut() };
    let mut n_flow = unsafe { flow.as_array_mut() };
    gr6j::gr6j(&v_param, &mut n_rainfall, &mut n_evap, &mut n_states, &mut n_uh1, &mut n_uh2, &mut n_flow);
}


#[pyfunction]
#[pyo3(name = "gr4h")]
fn gr4h_py(parameters: &PyList, rainfall: &PyArray1<f64>, evapotranspiration: &PyArray1<f64>, states: &PyArray1<f64>, uh1: &PyArray1<f64>, uh2: &PyArray1<f64>, flow: &PyArray1<f64>) {

    let v_param = parameters.extract::<Vec<f64>>().unwrap();

    let mut n_rainfall = unsafe { rainfall.as_array_mut() }; // Convert to ndarray type
    let mut n_evap = unsafe { evapotranspiration.as_array_mut() };
    let mut n_states = unsafe { states.as_array_mut() };
    let mut n_uh1 = unsafe { uh1.as_array_mut() };
    let mut n_uh2 = unsafe { uh2.as_array_mut() };
    let mut n_flow = unsafe { flow.as_array_mut() };
    gr4h::gr4h(&v_param, &mut n_rainfall, &mut n_evap, &mut n_states, &mut n_uh1, &mut n_uh2, &mut n_flow);
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
