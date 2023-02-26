use ndarray::ArrayViewMut1;
use super::s_curves::{s_curves1, s_curves2};


pub fn gr6j(parameters: &Vec<f64>, rainfall: &mut ArrayViewMut1<'_, f64>, evapotranspiration: &mut ArrayViewMut1<'_, f64>, states: &mut ArrayViewMut1<'_, f64>, uh1: &mut ArrayViewMut1<'_, f64>, uh2: &mut ArrayViewMut1<'_, f64>, flow: &mut ArrayViewMut1<'_, f64>) {
    let storage_fraction = 0.9;
    let exp_fraction = 0.4;

    // Get parameters :
    let x1 = parameters[0];
    let x2 = parameters[1];
    let x3 = parameters[2];
    let x4 = parameters[3];
    let x5 = parameters[4];
    let x6 = parameters[5];

    // Initialize hydrogramme :
    let nuh1 = x4.ceil() as usize;
    let nuh2 = (2.0 * x4).ceil() as usize;
    let mut o_uh1 = vec![0.; nuh1];
    let mut o_uh2 = vec![0.; nuh2];
    let exp: f64 = 2.5;
    for i in 1..nuh1 + 1 {
        o_uh1[i-1] = s_curves1(i, x4, exp) - s_curves1(i-1, x4, exp);
    }
    for i in 1..nuh2 + 1 {
        o_uh2[i-1] = s_curves2(i, x4, exp) - s_curves2(i-1, x4, exp);
    }
    // println!("{:?}", o_uh1);
    // println!("{:?}", o_uh2);
    // [0.13803916620160606, 0.6428282777223341, 0.21913255607605986]
    // [0.06901958310080303, 0.32141413886116704, 0.44489021900358455, 0.15697224734804904, 0.0077038116863963335]

    // Main loop :
    let iter = rainfall.iter()
    .zip(evapotranspiration.iter());
    for (t, (rain, evap)) in iter.enumerate() {
        let mut rout_input = 0.0;
        let psf = states[0] / x1;  // production store filling percentage
        if rain <= evap {
            let mut scaled_net_rain: f64 = (evap - rain) / x1;
            if scaled_net_rain > 13.0 {scaled_net_rain = 13.0;}
            scaled_net_rain = scaled_net_rain.tanh();
            let prod_evap = states[0] * (2. - psf) * scaled_net_rain / (1. + (1. - psf) * scaled_net_rain);  // evap from production store
            
            states[0] -= prod_evap;
        }
        else {
            let net_rainfall = rain - evap;
            let mut scaled_net_rain: f64 = net_rainfall / x1;
            if scaled_net_rain > 13.0 {scaled_net_rain = 13.0;}
            scaled_net_rain = scaled_net_rain.tanh();
            let prod_rainfall = x1 * (1. - psf * psf) * scaled_net_rain / (1. + psf * scaled_net_rain); // rainfall to production store
            
            rout_input = net_rainfall - prod_rainfall;
            states[0] += prod_rainfall;
        }
        if states[0] < 0. {states[0] = 0.;}

        // Production store percolation :
        let psf_p4 = (states[0] / x1).powf(4.0);
        let percolation = states[0] * (1.0 - 1.0 / (1.0 + psf_p4 / 25.62890625).powf(0.25));

        states[0] -= percolation;
        rout_input += percolation;

        for i in 0..nuh1-1 {
            uh1[i] = uh1[i + 1] + o_uh1[i] * rout_input;
        }
        uh1[nuh1-1] = o_uh1[nuh1-1] * rout_input;
        for i in 0..nuh2-1 {
            uh2[i] = uh2[i + 1] + o_uh2[i] * rout_input;
        }
        uh2[nuh2-1] = o_uh2[nuh2-1] * rout_input;

        // Potential inter catchment semi-exchange :
        let groundwater_exchange = x2 * (states[1] / x3 - x5);
        states[1] += uh1[0] * storage_fraction * (1.0 - exp_fraction) + groundwater_exchange;
        if states[1] < 0. {states[1] = 0.;}

        // Flow :
        let rsf_p4 = (states[1] / x3).powf(4.0);
        let rout_flow = states[1] * (1. - 1. / (1. + rsf_p4).powf(0.25));
        states[1] -= rout_flow;
        
        // Exponential store :
        states[2] += uh1[0] * storage_fraction * exp_fraction + groundwater_exchange;
        let mut ar: f64 = states[2] / x6;
        if ar > 33. {ar = 33.;}
        if ar < -33. {ar = -33.;}

        let mut exp_flow: f64 = 0.;
        if ar > 7. {
            exp_flow = states[2] + x6 / ar.exp();
        }
        else if ar < -7. {
            exp_flow = x6 / ar.exp();
        }
        else {
            exp_flow = x6 * (ar.exp() + 1.).ln();
        }
        states[2] -= exp_flow;

        let mut direct_flow = uh2[0] * (1.0 - storage_fraction) + groundwater_exchange;
        if direct_flow < 0. {direct_flow = 0.};

        
        flow[t] = rout_flow + direct_flow + exp_flow;
    }
}
