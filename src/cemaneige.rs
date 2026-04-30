use ndarray::{Array1, ArrayView1};

pub fn cemaneige(
    parameters: &Vec<f64>,
    inputs_precip: ArrayView1<'_, f64>,
    inputs_frac_solid_precip: ArrayView1<'_, f64>,
    inputs_temp: ArrayView1<'_, f64>,
    mean_an_solid_precip: f64,
    state_start: ArrayView1<'_, f64>,
    is_hyst: bool,
) -> (Array1<f64>, Array1<f64>) {
    let l_inputs = inputs_precip.len();
    let mut flow = Array1::zeros(l_inputs);
    let mut state_end = Array1::zeros(4); // [G, eTG, Gthreshold, Glocalmax]

    let t_melt = 0.0_f64;
    let min_speed = 0.1_f64;

    let ctg = parameters[0];
    let kf = parameters[1];

    let mut g = state_start[0];
    let mut etg = state_start[1];
    // Gratio is not a persistent state: resets to 0 at the start of each run
    let mut gratio = 0.0_f64;

    if is_hyst {
        let gacc = parameters[2]; // accumulation threshold [mm] — controls rate of SCA rebuild
        let prct = parameters[3]; // fraction of mean annual solid precip defining melt threshold

        // Fixed threshold, never changes during the run
        let gthreshold = if state_start[2] != 0.0 {
            state_start[2]
        } else {
            prct * mean_an_solid_precip
        };
        let mut glocalmax = if state_start[3] != 0.0 {
            state_start[3]
        } else {
            gthreshold
        };

        for k in 0..l_inputs {
            let pliq = (1.0 - inputs_frac_solid_precip[k]) * inputs_precip[k];
            let psol = inputs_frac_solid_precip[k] * inputs_precip[k];

            let ginit = g;
            g += psol;

            etg = ctg * etg + (1.0 - ctg) * inputs_temp[k];
            if etg > 0.0 {
                etg = 0.0;
            }

            let pot_melt = if etg == 0.0 && inputs_temp[k] > t_melt {
                (kf * (inputs_temp[k] - t_melt)).min(g)
            } else {
                0.0
            };

            // First Gratio update: only when potential melt exists (melt phase onset)
            if pot_melt > 0.0 {
                if g < glocalmax && gratio == 1.0 {
                    glocalmax = g;
                }
                gratio = (g / glocalmax).min(1.0);
            }

            let melt = (((1.0 - min_speed) * gratio + min_speed) * pot_melt).min(g);
            g -= melt;

            // Second Gratio update based on whether the timestep is net accumulation or net melt
            let dg = g - ginit;
            if dg > 0.0 {
                // Net accumulation: SCA rebuilds incrementally via Gacc
                gratio = (gratio + (psol - melt) / gacc).min(1.0);
                if gratio == 1.0 {
                    glocalmax = gthreshold;
                }
            } else {
                // Net melt: SCA tracks G/Glocalmax
                gratio = (g / glocalmax).min(1.0);
            }

            flow[k] = pliq + melt;
        }

        state_end[2] = gthreshold;
        state_end[3] = glocalmax;
    } else {
        let gthreshold = 0.9 * mean_an_solid_precip;

        for k in 0..l_inputs {
            let pliq = (1.0 - inputs_frac_solid_precip[k]) * inputs_precip[k];
            let psol = inputs_frac_solid_precip[k] * inputs_precip[k];

            g += psol;

            etg = ctg * etg + (1.0 - ctg) * inputs_temp[k];
            if etg > 0.0 {
                etg = 0.0;
            }

            let pot_melt = if etg == 0.0 && inputs_temp[k] > t_melt {
                (kf * (inputs_temp[k] - t_melt)).min(g)
            } else {
                0.0
            };

            gratio = if g < gthreshold { g / gthreshold } else { 1.0 };

            let melt = (((1.0 - min_speed) * gratio + min_speed) * pot_melt).min(g);
            g -= melt;

            flow[k] = pliq + melt;
        }

        state_end[2] = gthreshold;
        state_end[3] = -999.999; // sentinel: Glocalmax not used without hysteresis
    }

    state_end[0] = g;
    state_end[1] = etg;

    (state_end, flow)
}
