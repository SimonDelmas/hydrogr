use super::s_curves::s_curves2;
use ndarray::{Array1, ArrayView1};

pub fn gr5j(
    parameters: &Vec<f64>,
    rainfall: ArrayView1<'_, f64>,
    evapotranspiration: ArrayView1<'_, f64>,
    states: ArrayView1<'_, f64>,
    uh2: ArrayView1<'_, f64>,
) -> (Array1<f64>, Array1<f64>, Array1<f64>) {
    let mut states = states.to_owned();
    let mut uh2 = uh2.to_owned();
    let mut flow = Array1::zeros(rainfall.len());

    let storage_fraction = 0.9;

    // Get parameters :
    let x1 = parameters[0];
    let x2 = parameters[1];
    let x3 = parameters[2];
    let x4 = parameters[3];
    let x5 = parameters[4];

    // Initialize hydrogramme :
    let nuh2 = (2.0 * x4).ceil() as usize;
    let mut o_uh2 = vec![0.; nuh2];
    let exp: f64 = 2.5;
    for i in 1..nuh2 + 1 {
        o_uh2[i - 1] = s_curves2(i, x4, exp) - s_curves2(i - 1, x4, exp);
    }

    // Main loop :
    let iter = rainfall.iter().zip(evapotranspiration.iter());
    for (t, (rain, evap)) in iter.enumerate() {
        let mut rout_input = 0.0;
        let psf = states[0] / x1; // production store filling percentage
        if rain <= evap {
            let mut scaled_net_rain: f64 = (evap - rain) / x1;
            if scaled_net_rain > 13.0 {
                scaled_net_rain = 13.0;
            }
            scaled_net_rain = scaled_net_rain.tanh();
            let prod_evap =
                states[0] * (2. - psf) * scaled_net_rain / (1. + (1. - psf) * scaled_net_rain); // evap from production store

            states[0] -= prod_evap;
        } else {
            let net_rainfall = rain - evap;
            let mut scaled_net_rain: f64 = net_rainfall / x1;
            if scaled_net_rain > 13.0 {
                scaled_net_rain = 13.0;
            }
            scaled_net_rain = scaled_net_rain.tanh();
            let prod_rainfall =
                x1 * (1. - psf * psf) * scaled_net_rain / (1. + psf * scaled_net_rain); // rainfall to production store

            rout_input = net_rainfall - prod_rainfall;
            states[0] += prod_rainfall;
        }
        if states[0] < 0. {
            states[0] = 0.;
        }

        // Production store percolation :
        let psf_p4 = (states[0] / x1).powf(4.0);
        let percolation = states[0] * (1.0 - 1.0 / (1.0 + psf_p4 / 25.62890625).powf(0.25));

        states[0] -= percolation;
        rout_input += percolation;

        for i in 0..nuh2 - 1 {
            uh2[i] = uh2[i + 1] + o_uh2[i] * rout_input;
        }
        uh2[nuh2 - 1] = o_uh2[nuh2 - 1] * rout_input;

        // Potential inter catchment semi-exchange :
        let groundwater_exchange = x2 * (states[1] / x3 - x5);
        states[1] += uh2[0] * storage_fraction + groundwater_exchange;
        if states[1] < 0. {
            states[1] = 0.;
        }

        // Flow :
        let rsf_p4 = (states[1] / x3).powf(4.0);
        let rout_flow = states[1] * (1. - 1. / (1. + rsf_p4).powf(0.25));
        let mut direct_flow = uh2[0] * (1.0 - storage_fraction) + groundwater_exchange;
        if direct_flow < 0. {
            direct_flow = 0.
        };

        states[1] -= rout_flow;
        flow[t] = rout_flow + direct_flow;
    }

    (states, uh2, flow)
}
