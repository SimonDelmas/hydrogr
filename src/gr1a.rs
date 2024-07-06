use ndarray::{Array1, ArrayView1};

pub fn gr1a(
    parameters: &Vec<f64>,
    rainfall: ArrayView1<'_, f64>,
    evapotranspiration: ArrayView1<'_, f64>,
) -> Array1<f64> {
    let x1 = parameters[0];
    let mut flow = Array1::zeros(rainfall.len());

    // Main loop :
    for t in 1..rainfall.len() {
        // start at 1 here
        let tt = (0.7 * rainfall[t] + 0.3 * rainfall[t - 1]) / x1 / evapotranspiration[t];
        flow[t] = rainfall[t] * (1. - 1. / (1. + tt * tt).sqrt());
    }

    flow
}
