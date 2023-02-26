use ndarray::ArrayViewMut1;


pub fn gr2m(parameters: &Vec<f64>, rainfall: &mut ArrayViewMut1<'_, f64>, evapotranspiration: &mut ArrayViewMut1<'_, f64>, states: &mut ArrayViewMut1<'_, f64>, flow: &mut ArrayViewMut1<'_, f64>) {
    let x1 = parameters[0];
    let x2 = parameters[1];

    let iter = rainfall.iter()
    .zip(evapotranspiration.iter());
    for (t, (rain, evap)) in iter.enumerate() {
        
        // Production store
        let mut scaled_rain: f64 = rain / x1;
        if scaled_rain > 13.0 {scaled_rain = 13.0;}
        scaled_rain = scaled_rain.tanh();
        let s1 = (states[0] + x1 * scaled_rain) / (1. + states[0] / x1 * scaled_rain);
    
        let p1 = rain + states[0] - s1;
        let mut scaled_evap: f64 = evap / x1;
        if scaled_evap > 13.0 {scaled_evap = 13.0;}
        scaled_evap = scaled_evap.tanh();
        let s2 = s1 * (1. - scaled_evap) / (1. + (1. - s1 / x1) * scaled_evap);
    
        // Percolation :
        let mut sr = s2 / x1;
        sr = sr * sr * sr + 1.;
        states[0] = s2 / sr.powf(1. / 3.);
    
        // Routing store :
        let p3 = p1 + s2 - states[0];
        let routing = x2 * (states[1] + p3);
    
        // flow
        flow[t] = routing * routing / (routing + 60.);
        states[1] = routing - flow[t];
    }

}