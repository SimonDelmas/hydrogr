use super::s_curves::{s_curves1, s_curves2};
use ndarray::{Array1, ArrayView1};

// https://wiki.ewater.org.au/display/SD50/GR4H

pub fn gr4h(
    parameters: &[f64; 4],
    rainfall: ArrayView1<'_, f64>,
    evapotranspiration: ArrayView1<'_, f64>,
    states: ArrayView1<'_, f64>,
    uh1: ArrayView1<'_, f64>,
    uh2: ArrayView1<'_, f64>,
) -> (Array1<f64>, Array1<f64>, Array1<f64>, Array1<f64>) {
    let mut states = states.to_owned();
    let mut uh1 = uh1.to_owned();
    let mut uh2 = uh2.to_owned();
    let mut flow = Array1::zeros(rainfall.len());

    let storage_fraction = 0.9;

    // Get parameters :
    let [x1, x2, x3, x4] = *parameters;
    assert!(x4 > 0.0, "x4 parameter must be strictly positive");

    // Initialize hydrograph :
    let exp: f64 = 1.25;
    let nuh1 = x4.ceil() as usize;
    let nuh2 = (2.0 * x4).ceil() as usize;
    let o_uh1: Vec<f64> = (1..=nuh1)
        .map(|i| s_curves1(i, x4, exp) - s_curves1(i - 1, x4, exp))
        .collect();
    let o_uh2: Vec<f64> = (1..=nuh2)
        .map(|i| s_curves2(i, x4, exp) - s_curves2(i - 1, x4, exp))
        .collect();

    // Main loop :
    let iter = rainfall.iter().zip(evapotranspiration.iter());
    for (t, (&rain, &evap)) in iter.enumerate() {
        let mut rout_input = 0.0;

        let psf = states[0] / x1; // production store filling percentage
        if rain <= evap {
            let scaled_net_rain = ((evap - rain) / x1).min(13.0).tanh();
            let prod_evap =
                states[0] * (2. - psf) * scaled_net_rain / (1. + (1. - psf) * scaled_net_rain); // evap from production store
            states[0] -= prod_evap;
        } else {
            let net_rainfall = rain - evap;
            let scaled_net_rain = (net_rainfall / x1).min(13.0).tanh();
            let prod_rainfall =
                x1 * (1. - psf * psf) * scaled_net_rain / (1. + psf * scaled_net_rain); // rainfall to production store

            rout_input = net_rainfall - prod_rainfall;
            states[0] += prod_rainfall;
        }
        states[0] = states[0].max(0.0);

        // Production store percolation :
        let psf_p4 = (states[0] / x1).powi(4);
        let percolation = states[0] * (1.0 - 1.0 / (1.0 + psf_p4 / 759.69140625).powf(0.25));
        states[0] -= percolation;
        rout_input += percolation;

        for i in 0..nuh1 - 1 {
            uh1[i] = uh1[i + 1] + o_uh1[i] * rout_input;
        }
        uh1[nuh1 - 1] = o_uh1[nuh1 - 1] * rout_input;
        
        for i in 0..nuh2 - 1 {
            uh2[i] = uh2[i + 1] + o_uh2[i] * rout_input;
        }
        uh2[nuh2 - 1] = o_uh2[nuh2 - 1] * rout_input;

        // Potential inter catchment semi-exchange :
        let groundwater_exchange = x2 * (states[1] / x3).powf(3.5);
        states[1] += uh1[0] * storage_fraction + groundwater_exchange;
        states[1] = states[1].max(0.0);

        // Flow :
        let rsf_p4 = (states[1] / x3).powi(4);
        let rout_flow = states[1] * (1. - 1. / (1. + rsf_p4).powf(0.25));
        states[1] -= rout_flow;

        let direct_flow = (uh2[0] * (1.0 - storage_fraction) + groundwater_exchange).max(0.0);

        flow[t] = rout_flow + direct_flow;
    }

    (states, uh1, uh2, flow)
}

#[cfg(test)]
mod tests {
    use super::*;
    extern crate ndarray;
    use ndarray::Array1;

    #[test]
    fn test_gr4h() {
        let parameters = [200.0, 1.0, 100.0, 2.0];
        let states = vec![0., 0.];
        let states = Array1::<f64>::from_vec(states);
        let rainfall = vec![0., 0., 0., 10., 10., 10., 10., 0., 0., 0.];
        let evapotranspiration = vec![0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1];
        let rainfall = Array1::<f64>::from_vec(rainfall);
        let evapotranspiration = Array1::<f64>::from_vec(evapotranspiration);
        let uh1 = Array1::<f64>::zeros(20);
        let uh2 = Array1::<f64>::zeros(40);

        let (_states, _uh1, _uh2, flow) = gr4h(
            &parameters,
            rainfall.view(),
            evapotranspiration.view(),
            states.view(),
            uh1.view(),
            uh2.view(),
        );

        let ref_flow = vec![
            0.0,
            0.0,
            0.0,
            0.00016981750514207867,
            0.0014188328018795034,
            0.0050621281264912315,
            0.012368862852729453,
            0.01408289101187942,
            0.011689660613822294,
            0.006163451427650927,
        ];
        for i in 0..10 {
            assert_eq!(flow[i], ref_flow[i]);
        }
    }
}
