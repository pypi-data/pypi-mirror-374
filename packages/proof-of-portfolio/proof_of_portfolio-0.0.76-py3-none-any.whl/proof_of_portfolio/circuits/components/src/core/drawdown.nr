use crate::utils::constants::{ARRAY_SIZE, SCALE};

fn exp_scaled(x_scaled: i64) -> i64 {
    let scale: i64 = 10_000_000;
    let mut abs_x = x_scaled;
    if x_scaled < 0 {
        abs_x = -x_scaled;
    }

    if abs_x > scale * 3 {
        if x_scaled > 0 {
            scale * 20
        } else {
            0
        }
    } else {
        let x_pow_2 = (x_scaled * x_scaled) / scale;
        let x_pow_3 = (x_pow_2 * x_scaled) / scale;
        let x_pow_4 = (x_pow_3 * x_scaled) / scale;
        let x_pow_5 = (x_pow_4 * x_scaled) / scale;

        let term0 = scale;
        let term1 = x_scaled;
        let term2 = x_pow_2 / 2;
        let term3 = x_pow_3 / 6;
        let term4 = x_pow_4 / 24;
        let term5 = x_pow_5 / 120;

        term0 + term1 + term2 + term3 + term4 + term5
    }
}

pub fn daily_max_drawdown(log_returns: [i64; ARRAY_SIZE], actual_len: u32) -> i64 {
    let mut max_drawdown_factor = SCALE;

    if actual_len > 0 {
        let mut cumulative_sum: i64 = 0;
        let mut running_max: i64 = 0;

        for i in 0..ARRAY_SIZE {
            if (i as u32) < actual_len {
                cumulative_sum += log_returns[i];

                if cumulative_sum > running_max {
                    running_max = cumulative_sum;
                }

                if running_max > 0 {
                    let cumulative_value = exp_scaled(cumulative_sum);
                    let max_value = exp_scaled(running_max);

                    let drawdown_pct = ((cumulative_value - max_value) * SCALE) / max_value;

                    let drawdown_factor = SCALE + drawdown_pct;

                    if drawdown_factor < max_drawdown_factor {
                        max_drawdown_factor = drawdown_factor;
                    }
                }
            }
        }
    }

    max_drawdown_factor
}

#[test]
fn test_drawdown_all_positive() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..10 {
        returns[i] = 100;
    }

    let result = daily_max_drawdown(returns, 10);
    assert(result == SCALE);
}

#[test]
fn test_drawdown_simple_case() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 1000;
    returns[1] = -500;
    returns[2] = -300;
    returns[3] = 200;

    let result = daily_max_drawdown(returns, 4);
    assert(result == 800);
}

#[test]
fn test_drawdown_multiple_peaks() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 1000;
    returns[1] = -500;
    returns[2] = 800;
    returns[3] = -1200;
    returns[4] = 400;

    let result = daily_max_drawdown(returns, 5);
    assert(result == 1200);
}

#[test]
fn test_drawdown_all_negative() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..5 {
        returns[i] = -100;
    }

    let result = daily_max_drawdown(returns, 5);
    assert(result == 500);
}
