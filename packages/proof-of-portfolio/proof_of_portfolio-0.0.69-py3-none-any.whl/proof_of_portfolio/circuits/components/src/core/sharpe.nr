use crate::utils::{
    ann_excess_return::ann_excess_return,
    ann_volatility::ann_volatility,
    sqrt::sqrt,
    constants::{
        ARRAY_SIZE, SHARPE_NOCONFIDENCE_VALUE, SHARPE_STDDEV_MINIMUM, STATISTICAL_CONFIDENCE_MINIMUM_N, SCALE, RATIO_SCALE_FACTOR
    },
};

pub fn sharpe(
    daily_returns: [i64; ARRAY_SIZE],
    actual_len: u32,
    risk_free_rate: i64,
    weights: [i64; ARRAY_SIZE],
    use_weighting: bool,
    bypass_confidence: bool,
    avg_daily_return: i64,
    variance_val: i64,
    ann_excess_return_val: i64,
) -> i64 {
    let result = if !bypass_confidence & actual_len < STATISTICAL_CONFIDENCE_MINIMUM_N {
        SHARPE_NOCONFIDENCE_VALUE
    } else {
        let excess_return = ann_excess_return_val;
        let volatility = if actual_len < 2 {
            SCALE
        } else {
            let annualized_variance = variance_val * 365;
            sqrt(annualized_variance as u64) as i64
        };
        let effective_volatility = if volatility < SHARPE_STDDEV_MINIMUM {
            SHARPE_STDDEV_MINIMUM
        } else {
            volatility
        };

        (excess_return * RATIO_SCALE_FACTOR) / effective_volatility
    };
    result
}

#[test]
fn test_sharpe_normal_case() {
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
    let result = sharpe(returns, 5, 100, weights, false, false, avg, variance_val, ann_excess);
    assert(result != 0);
}

#[test]
fn test_sharpe_low_volatility() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..10 {
        returns[i] = 50;
    }

    let weights = [100000; ARRAY_SIZE];
    let avg = 50;
    let variance_val = 0;
    let ann_excess = 18240;
    let result = sharpe(returns, 10, 10, weights, false, false, avg, variance_val, ann_excess);
    assert(result == 0);
}

#[test]
fn test_sharpe_high_volatility() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 5000;
    returns[1] = -4000;
    returns[2] = 3000;
    returns[3] = -2000;
    returns[4] = 1000;

    let weights = [100000; ARRAY_SIZE];
    let avg = 600;
    let variance_val = 8400000;
    let ann_excess = 218800;
    let result = sharpe(returns, 5, 200, weights, false, false, avg, variance_val, ann_excess);
    assert(result != 0);
}
