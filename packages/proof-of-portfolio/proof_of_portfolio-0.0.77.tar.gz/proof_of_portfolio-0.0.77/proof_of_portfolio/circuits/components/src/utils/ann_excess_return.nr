use crate::utils::{average::average, constants::{ARRAY_SIZE, DAYS_IN_YEAR}};

pub fn ann_excess_return(
    log_returns: [i64; ARRAY_SIZE],
    actual_len: u32,
    RISK_FREE_RATE: i64,
    weights: [i64; ARRAY_SIZE],
    use_weighting: bool,
) -> i64 {
    let sum_of_weights = if use_weighting {
        let mut sum: i64 = 0;
        for i in 0..ARRAY_SIZE {
            if (i as u32) < actual_len {
                sum += weights[i];
            }
        }
        sum
    } else {
        actual_len as i64
    };
    let avg = average(
        log_returns,
        actual_len,
        weights,
        use_weighting,
        sum_of_weights,
    );
    let annualized = avg * DAYS_IN_YEAR;
    annualized - RISK_FREE_RATE
}

#[test]
fn test_ann_excess_return_positive() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 100;
    returns[1] = 200;
    returns[2] = 150;

    let weights = [100000; ARRAY_SIZE];
    let result = ann_excess_return(returns, 3, 10000, weights, false);
    assert(result > 0);
}

#[test]
fn test_ann_excess_return_negative() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = -100;
    returns[1] = -200;
    returns[2] = -150;

    let weights = [100000; ARRAY_SIZE];
    let result = ann_excess_return(returns, 3, 10000, weights, false);
    assert(result < 0);
}

#[test]
fn test_ann_excess_return_equal_to_risk_free() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 100;
    returns[1] = 100;
    returns[2] = 100;

    let weights = [100000; ARRAY_SIZE];
    let result = ann_excess_return(returns, 3, 36500, weights, false);
    assert(result == 0);
}

#[test]
fn test_ann_excess_return_zero_risk_free() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 100;
    returns[1] = 200;

    let weights = [100000; ARRAY_SIZE];
    let result = ann_excess_return(returns, 2, 0, weights, false);
    assert(result == 54750);
}
