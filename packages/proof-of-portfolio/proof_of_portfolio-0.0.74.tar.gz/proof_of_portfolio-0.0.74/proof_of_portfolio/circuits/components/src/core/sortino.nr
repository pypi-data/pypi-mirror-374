use crate::utils::{
    ann_excess_return::ann_excess_return,
    constants::{
        ARRAY_SIZE, DAILY_LOG_RISK_FREE_RATE, DAYS_IN_YEAR, LARGE_POSITIVE_VALUE,
        RATIO_SCALE_FACTOR, SORTINO_DOWNSIDE_MINIMUM, SORTINO_NOCONFIDENCE_VALUE,
        STATISTICAL_CONFIDENCE_MINIMUM_N,
    },
    sqrt::sqrt,
};

pub fn sortino(
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
        SORTINO_NOCONFIDENCE_VALUE
    } else {
        let excess_return = ann_excess_return_val;

        let mut downside_variance_sum: u64 = 0;
        let mut negative_count: u32 = 0;
        let mut downside_returns_sum: i64 = 0;

        for i in 0..ARRAY_SIZE {
            if (i as u32) < actual_len {
                if log_returns[i] < DAILY_LOG_RISK_FREE_RATE {
                    downside_returns_sum += log_returns[i];
                    negative_count = negative_count + 1;
                }
            }
        }

        if negative_count > 1 {
            let downside_mean = downside_returns_sum / (negative_count as i64);

            for i in 0..ARRAY_SIZE {
                if (i as u32) < actual_len {
                    if log_returns[i] < DAILY_LOG_RISK_FREE_RATE {
                        let diff = log_returns[i] - downside_mean;
                        downside_variance_sum += ((diff * diff) as u64);
                    }
                }
            }

            let downside_variance = downside_variance_sum / ((negative_count - 1) as u64);
            let downside_volatility = sqrt(downside_variance * (DAYS_IN_YEAR as u64)) as i64;

            let effective_downside_volatility = if downside_volatility > SORTINO_DOWNSIDE_MINIMUM {
                downside_volatility
            } else {
                SORTINO_DOWNSIDE_MINIMUM
            };

            (excess_return * RATIO_SCALE_FACTOR) / effective_downside_volatility
        } else {
            LARGE_POSITIVE_VALUE
        }
    }
}

#[test]
fn test_sortino_normal_case() {
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
    let result = sortino(
        returns,
        5,
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
fn test_sortino_no_negative_returns() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..5 {
        returns[i] = 1000;
    }

    let weights = [100000; ARRAY_SIZE];
    let avg = 1000;
    let variance_val = 0;
    let ann_excess = 365000;
    let result = sortino(
        returns,
        5,
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
fn test_sortino_all_negative_returns() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..5 {
        returns[i] = -500;
    }

    let weights = [100000; ARRAY_SIZE];
    let avg = -500;
    let variance_val = 0;
    let ann_excess = -182500;
    let result = sortino(
        returns,
        5,
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

#[test]
fn test_sortino_high_downside_volatility() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 2000;
    returns[1] = -1500;
    returns[2] = 1800;
    returns[3] = -1200;
    returns[4] = 1600;

    let weights = [100000; ARRAY_SIZE];
    let avg = 600;
    let variance_val = 450000;
    let ann_excess = 218800;
    let result = sortino(
        returns,
        5,
        200,
        weights,
        false,
        false,
        avg,
        variance_val,
        ann_excess,
    );
    assert(result != 0);
}
