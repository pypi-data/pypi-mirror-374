use crate::utils::{
    ann_excess_return::ann_excess_return,
    constants::{
        ARRAY_SIZE, CALMAR_NOCONFIDENCE_VALUE, LARGE_POSITIVE_VALUE, RATIO_SCALE_FACTOR, SCALE,
        STATISTICAL_CONFIDENCE_MINIMUM_N,
    },
};
use super::drawdown::daily_max_drawdown;

pub fn calmar(
    log_returns: [i64; ARRAY_SIZE],
    actual_len: u32,
    RISK_FREE_RATE: i64,
    weights: [i64; ARRAY_SIZE],
    use_weighting: bool,
    bypass_confidence: bool,
    avg_daily_return: i64,
    variance_val: i64,
    ann_excess_return_val: i64,
) -> i64 {
    if !bypass_confidence & actual_len < STATISTICAL_CONFIDENCE_MINIMUM_N {
        CALMAR_NOCONFIDENCE_VALUE
    } else {
        let ann_excess_return = ann_excess_return_val;
        let drawdown_factor = daily_max_drawdown(log_returns, actual_len);

        let max_drawdown = SCALE - drawdown_factor;

        if max_drawdown <= 0 {
            LARGE_POSITIVE_VALUE
        } else {
            (ann_excess_return * RATIO_SCALE_FACTOR) / max_drawdown
        }
    }
}

#[test]
fn test_calmar_normal_case() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 1000;
    returns[1] = -500;
    returns[2] = 2000;
    returns[3] = -1000;
    returns[4] = 500;
    for i in 5..40 {
        returns[i] = if i % 2 == 0 { 200 } else { -150 };
    }

    let weights = [100000; ARRAY_SIZE];
    let avg = 25;
    let variance_val = 30625;
    let ann_excess = 9025;
    let result = calmar(
        returns,
        40,
        100,
        weights,
        false,
        false,
        avg,
        variance_val,
        ann_excess,
    );
    assert(result != 0);
}

#[test]
fn test_calmar_insufficient_data() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 1000;
    returns[1] = -500;

    let weights = [100000; ARRAY_SIZE];
    let avg = 250;
    let variance_val = 1125000;
    let ann_excess = 91150;
    let result = calmar(
        returns,
        2,
        100,
        weights,
        false,
        false,
        avg,
        variance_val,
        ann_excess,
    );
    assert(result == 0);
}

#[test]
fn test_calmar_exactly_30_days() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..30 {
        returns[i] = 100;
    }

    let weights = [100000; ARRAY_SIZE];
    let avg = 100;
    let variance_val = 0;
    let ann_excess = 36450;
    let result = calmar(
        returns,
        30,
        50,
        weights,
        false,
        false,
        avg,
        variance_val,
        ann_excess,
    );
    assert(result != 0);
}

#[test]
fn test_calmar_negative_returns() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..50 {
        returns[i] = -100;
    }

    let weights = [100000; ARRAY_SIZE];
    let avg = -100;
    let variance_val = 0;
    let ann_excess = -36500;
    let result = calmar(
        returns,
        50,
        0,
        weights,
        false,
        false,
        avg,
        variance_val,
        ann_excess,
    );
    assert(result != 0);
}
