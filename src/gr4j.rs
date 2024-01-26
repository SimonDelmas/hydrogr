use ndarray::ArrayViewMut1;
use super::s_curves::{s_curves1, s_curves2};


pub fn gr4j(parameters: &Vec<f64>, rainfall: &mut ArrayViewMut1<'_, f64>, evapotranspiration: &mut ArrayViewMut1<'_, f64>, states: &mut ArrayViewMut1<'_, f64>, uh1: &mut ArrayViewMut1<'_, f64>, uh2: &mut ArrayViewMut1<'_, f64>, flow: &mut ArrayViewMut1<'_, f64>) {
    let storage_fraction = 0.9;

    // Get parameters :
    let x1 = parameters[0];
    let x2 = parameters[1];
    let x3 = parameters[2];
    let x4 = parameters[3];

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
        let percolation = states[0] * (1.0 - 1.0 / (1.0 + psf_p4 / 25.62891).powf(0.25));

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
        let groundwater_exchange = x2 * (states[1] / x3).powf(3.5);
        states[1] += uh1[0] * storage_fraction + groundwater_exchange;
        if states[1] < 0. {states[1] = 0.;}

        // Flow :
        let rsf_p4 = (states[1] / x3).powf(4.0);
        let rout_flow = states[1] * (1. - 1. / (1. + rsf_p4).powf(0.25));
        let mut direct_flow = uh2[0] * (1.0 - storage_fraction) + groundwater_exchange;
        if direct_flow < 0. {direct_flow = 0.};

        states[1] -= rout_flow;
        flow[t] = rout_flow + direct_flow;
    }
}


#[cfg(test)]
mod tests {
    use super::*;
    extern crate ndarray;
    use ndarray::Array1;

    #[test]
    fn test_gr4j() {
        let input_len = 370;

        let parameters = vec![257.238, 1.012, 88.235, 2.208];
        let states = vec![77.1714, 44.1175];
        let mut states = Array1::<f64>::from_vec(states);
        let rainfall = vec![12.1, 0.7, 0.3, 0.1, 0.8, 0.0, 0.0, 0.0, 0.0, 0.2, 1.6, 0.2, 0.1, 1.9, 1.4, 1.2, 0.1, 8.0, 0.2, 0.0, 3.8, 13.0, 0.8, 1.8, 13.4, 2.3, 1.1, 11.5, 5.9, 3.0, 0.0, 0.0, 0.0, 7.4, 10.7, 9.1, 5.6, 0.0, 17.5, 11.7, 4.3, 2.1, 0.9, 1.9, 6.9, 6.1, 25.5, 2.8, 0.1, 0.2, 29.0, 1.6, 1.3, 0.2, 1.9, 0.4, 0.0, 0.4, 0.0, 9.7, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1, 0.0, 0.0, 0.9, 6.6, 1.9, 3.5, 0.3, 0.0, 0.0, 7.9, 2.5, 6.1, 0.2, 12.0, 19.3, 5.2, 0.0, 0.0, 2.7, 8.9, 10.5, 1.4, 0.0, 1.9, 2.9, 6.6, 0.2, 5.2, 0.0, 0.1, 14.1, 1.6, 0.3, 1.0, 7.7, 8.0, 2.0, 0.3, 0.0, 0.0, 3.5, 2.6, 1.2, 0.0, 0.0, 0.0, 0.4, 1.3, 0.0, 0.1, 1.3, 5.6, 0.8, 0.4, 0.7, 0.4, 36.3, 14.7, 0.1, 1.7, 0.3, 5.3, 2.6, 3.5, 0.0, 6.3, 1.7, 0.7, 7.1, 0.2, 7.1, 3.8, 7.6, 3.4, 2.7, 7.3, 5.5, 2.6, 18.6, 47.0, 7.3, 0.0, 0.0, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 2.4, 0.1, 7.2, 21.3, 0.5, 5.7, 0.0, 0.0, 5.3, 0.7, 1.4, 0.0, 0.4, 1.2, 1.4, 15.7, 7.2, 35.6, 8.9, 0.0, 6.4, 1.0, 0.0, 9.8, 12.6, 0.0, 0.0, 0.0, 9.5, 2.4, 0.0, 0.1, 2.1, 7.7, 1.4, 0.0, 1.1, 7.5, 11.6, 5.4, 0.0, 0.0, 0.0, 0.0, 0.0, 0.2, 0.0, 0.0, 0.0, 0.3, 12.9, 5.6, 2.6, 14.1, 21.3, 59.9, 8.3, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 10.4, 0.0, 0.3, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 23.1, 40.9, 7.8, 5.7, 2.1, 4.7, 4.8, 1.7, 0.0, 23.1, 10.5, 1.2, 1.4, 22.6, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.1, 1.1, 0.0, 0.0, 0.5, 1.4, 0.0, 4.5, 13.2, 0.0, 0.0, 0.1, 37.3, 12.1, 0.0, 5.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.4, 0.1, 5.6, 2.5, 0.8, 22.1, 6.0, 1.4, 0.4, 0.0, 0.0, 0.0, 7.0, 0.2, 1.2, 2.7, 2.7, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 4.2, 18.5, 12.2, 10.4, 6.2, 2.5, 0.1, 0.0, 1.4, 2.2, 3.1, 0.2, 10.2, 2.5, 1.2, 0.8, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 7.3, 4.7, 12.7, 4.8, 0.0, 0.0, 0.2, 6.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 3.6, 0.8, 3.9, 6.4, 0.0, 2.0, 7.7, 6.1, 0.3, 3.6, 2.7, 0.0, 9.3, 3.2, 7.3, 0.0];
        let mut rainfall = Array1::<f64>::from_vec(rainfall);
        let evapotranspiration = vec![0.5, 0.4, 0.2, 0.2, 0.1, 0.2, 0.1, 0.2, 0.2, 0.3, 0.3, 0.1, 0.3, 0.4, 0.3, 0.2, 0.2, 0.3, 0.4, 0.4, 0.6, 0.6, 0.5, 0.6, 0.7, 0.7, 0.6, 0.5, 0.4, 0.4, 0.3, 0.2, 0.2, 0.5, 0.8, 0.9, 0.8, 0.8, 0.8, 1.0, 0.8, 0.7, 0.6, 0.6, 0.6, 0.5, 0.5, 0.9, 0.9, 1.1, 1.1, 0.8, 0.6, 0.9, 0.9, 0.7, 0.6, 0.5, 0.6, 0.7, 1.2, 1.3, 1.3, 1.2, 1.2, 1.5, 1.5, 1.5, 1.4, 1.1, 0.9, 1.1, 1.2, 1.2, 1.8, 1.5, 1.2, 1.1, 1.0, 1.0, 1.2, 1.3, 1.1, 1.3, 1.9, 1.6, 0.9, 0.4, 0.3, 0.7, 1.6, 1.7, 1.4, 1.2, 1.1, 1.4, 1.1, 0.6, 0.4, 0.4, 0.6, 1.0, 1.7, 1.4, 1.1, 1.1, 1.7, 1.8, 1.5, 1.5, 1.9, 2.6, 2.6, 2.2, 2.3, 2.9, 2.1, 2.1, 1.5, 1.7, 1.8, 2.0, 1.5, 1.3, 1.7, 1.9, 2.1, 1.9, 2.0, 2.3, 3.0, 2.8, 2.2, 2.2, 2.4, 2.5, 2.6, 2.7, 2.8, 3.0, 2.8, 2.9, 3.1, 3.3, 3.2, 2.7, 2.8, 3.1, 3.1, 3.2, 3.1, 3.0, 3.1, 3.0, 2.9, 3.2, 3.1, 3.4, 3.1, 3.8, 3.1, 3.2, 4.0, 3.4, 2.6, 2.8, 3.3, 3.8, 3.6, 3.6, 3.2, 3.0, 2.6, 2.9, 3.2, 3.4, 3.1, 3.1, 3.6, 2.9, 3.1, 3.3, 4.0, 4.3, 3.9, 4.1, 4.4, 4.5, 3.8, 3.6, 4.0, 4.3, 3.9, 3.8, 3.6, 3.1, 2.9, 3.2, 3.6, 3.7, 3.4, 2.9, 3.1, 3.7, 4.1, 3.3, 2.8, 2.9, 3.0, 2.8, 2.7, 3.0, 2.7, 2.8, 3.4, 3.6, 3.7, 3.8, 3.1, 3.2, 3.0, 3.0, 2.9, 2.9, 3.0, 3.2, 3.4, 3.6, 2.8, 2.8, 2.7, 2.7, 2.5, 2.4, 2.4, 2.7, 3.0, 2.6, 2.5, 2.4, 2.3, 2.5, 2.8, 2.6, 2.5, 2.7, 2.7, 2.5, 2.4, 2.6, 2.7, 2.2, 2.0, 2.4, 2.7, 2.4, 1.9, 2.0, 1.9, 1.4, 1.2, 1.1, 1.1, 1.1, 1.3, 1.4, 1.5, 1.8, 1.8, 1.7, 1.9, 1.8, 1.8, 1.7, 1.3, 1.3, 1.5, 1.8, 2.1, 1.3, 1.5, 1.4, 1.1, 1.0, 1.1, 1.1, 1.3, 1.3, 1.2, 1.3, 1.5, 1.6, 1.6, 1.7, 1.5, 1.3, 1.4, 1.2, 1.0, 1.1, 0.9, 0.9, 0.9, 1.0, 0.8, 0.9, 1.2, 1.0, 0.9, 0.9, 0.8, 0.8, 0.8, 0.8, 0.8, 0.9, 0.5, 0.6, 0.6, 0.4, 0.4, 0.3, 0.2, 0.4, 0.5, 0.3, 0.3, 0.5, 0.3, 0.2, 0.1, 0.1, 0.1, 0.0, 0.0, 0.0, 0.0, 0.2, 0.4, 0.5, 0.6, 0.5, 0.4, 0.4, 0.6, 0.5, 0.4, 0.3, 0.2, 0.2, 0.3, 0.3, 0.2, 0.3, 0.5, 0.5, 0.6, 0.7, 0.4, 0.3, 0.4, 0.2, 0.2, 0.3, 0.3, 0.3, 0.4, 0.4, 0.3, 0.1];
        let mut evapotranspiration = Array1::<f64>::from_vec(evapotranspiration);
        let mut flow = Array1::<f64>::zeros(input_len);
        let mut uh1 = Array1::<f64>::zeros(20);
        let mut uh2 = Array1::<f64>::zeros(40);

        gr4j(&parameters, &mut rainfall.view_mut(), &mut evapotranspiration.view_mut(), &mut states.view_mut(), &mut uh1.view_mut(), &mut uh2.view_mut(), &mut flow.view_mut());

        let ref_flow = vec![1.992, 1.8, 2.856, 2.4, 3.312];

        let mut rmse = 0.;
        for i in 0..5 {
            rmse += (flow[365 + i] - ref_flow[i]).powf(2.0);
        }
        rmse = (rmse/5.0).sqrt();

        assert_eq!(rmse, 0.4602862058994086);
    }
}