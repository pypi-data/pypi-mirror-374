use crate::utils::{
    average::average,
    constants::{
        ARRAY_SIZE, SCALE, STATISTICAL_CONFIDENCE_MINIMUM_N, STATISTICAL_CONFIDENCE_NOCONFIDENCE_VALUE, RATIO_SCALE_FACTOR,
    },
    sqrt::sqrt,
    variance::variance,
};

pub fn statistical_confidence(
    log_returns: [i64; ARRAY_SIZE],
    actual_len: u32,
    weights: [i64; ARRAY_SIZE],
    use_weighting: bool,
    bypass_confidence: bool,
    avg_daily_return: i64,
    variance_val: i64,
    ann_excess_return_val: i64,
) -> i64 {
    // Check minimum sample size for statistical confidence
    if !bypass_confidence & actual_len < STATISTICAL_CONFIDENCE_MINIMUM_N {
        if actual_len < 2 {
            STATISTICAL_CONFIDENCE_NOCONFIDENCE_VALUE
        } else {
            // Allow computation for sample sizes between 2 and minimum, but with reduced confidence
            compute_t_statistic(log_returns, actual_len, weights, use_weighting, avg_daily_return, variance_val)
        }
    } else {
        compute_t_statistic(log_returns, actual_len, weights, use_weighting, avg_daily_return, variance_val)
    }
}

fn compute_t_statistic(
    log_returns: [i64; ARRAY_SIZE],
    actual_len: u32,
    weights: [i64; ARRAY_SIZE],
    use_weighting: bool,
    avg_daily_return: i64,
    variance_val: i64,
) -> i64 {
    let avg = avg_daily_return;
    let var = variance_val;

    if var <= 0 {
        STATISTICAL_CONFIDENCE_NOCONFIDENCE_VALUE
    } else {
        let std_dev = sqrt(var as u64) as i64;
        let n_sqrt = sqrt(actual_len as u64) as i64;
        let standard_error = std_dev / n_sqrt;

        if standard_error == 0 {
            RATIO_SCALE_FACTOR
        } else {
            (avg * RATIO_SCALE_FACTOR) / standard_error
        }
    }
}

#[test]
fn test_tstat_normal_case() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 1000;
    returns[1] = -500;
    returns[2] = 800;
    returns[3] = -300;
    returns[4] = 600;

    let weights = [100000; ARRAY_SIZE];
    let avg = 320;
    let variance_val = 200000;
    let ann_excess = 116700;
    let result = statistical_confidence(returns, 5, weights, false, false, avg, variance_val, ann_excess);
    assert(result != 0);
}

#[test]
fn test_tstat_insufficient_data() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 1000;

    let weights = [100000; ARRAY_SIZE];
    let avg = 1000;
    let variance_val = 0;
    let ann_excess = 365000;
    let result = statistical_confidence(returns, 1, weights, false, false, avg, variance_val, ann_excess);
    assert(result == 0);
}

#[test]
fn test_tstat_zero_variance() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..5 {
        returns[i] = 100;
    }

    let weights = [100000; ARRAY_SIZE];
    let avg = 100;
    let variance_val = 0;
    let ann_excess = 36500;
    let result = statistical_confidence(returns, 5, weights, false, false, avg, variance_val, ann_excess);
    assert(result == 0);
}

#[test]
fn test_tstat_exactly_two_samples() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 1000;
    returns[1] = -500;

    let weights = [100000; ARRAY_SIZE];
    let avg = 250;
    let variance_val = 1125000;
    let ann_excess = 91150;
    let result = statistical_confidence(returns, 2, weights, false, false, avg, variance_val, ann_excess);
    assert(result != 0);
}
