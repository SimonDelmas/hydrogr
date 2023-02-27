use ndarray::ArrayViewMut1;


pub fn gr1a(parameters: &Vec<f64>, rainfall: &mut ArrayViewMut1<'_, f64>, evapotranspiration: &mut ArrayViewMut1<'_, f64>, flow: &mut ArrayViewMut1<'_, f64>) {
    let x1 = parameters[0];
    
    // Main loop :
    for t in 1..rainfall.len() {  // start at 1 here
        let tt = (0.7 * rainfall[t] + 0.3 * rainfall[t-1]) / x1 / evapotranspiration[t];
        flow[t] = rainfall[t] * (1. - 1. / (1. + tt * tt).sqrt());
    }
}
