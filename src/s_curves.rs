pub fn s_curves1(t: usize, x4: f64, exp: f64) -> f64 {
    // Unit hydrograph ordinates for UH1 derived from S-curves.
    let t = t as f64;
    if t < x4 {
        (t/x4).powf(exp)
    }
    else {
        1.
    }
}


pub fn s_curves2(t: usize, x4: f64, exp: f64) -> f64 {
    // Unit hydrograph ordinates for UH2 derived from S-curves.
    let t = t as f64;
    if t < x4 {
        0.5 *(t/x4).powf(exp)
    }
    else if t < 2.0 * x4 {
        1. - 0.5 * (2.0 - t/x4).powf(exp)
    }
    else {
        1.
    }
}


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_s_curves1() {
        let res = s_curves1(1, 2.0, 1.0);
        assert_eq!(res, 0.5);
        let res = s_curves1(2, 1.0, 1.0);
        assert_eq!(res, 1.);
    }

    #[test]
    fn test_s_curves2() {
        let res = s_curves2(1, 2.0, 1.0);
        assert_eq!(res, 0.25);
        let res = s_curves2(3, 2.0, 1.0);
        assert_eq!(res, 0.75);
        let res = s_curves2(2, 1.0, 1.0);
        assert_eq!(res, 1.);
    }
}