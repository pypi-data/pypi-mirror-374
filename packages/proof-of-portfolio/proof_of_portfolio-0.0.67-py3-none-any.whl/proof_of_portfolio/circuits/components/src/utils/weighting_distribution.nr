use crate::utils::constants::ARRAY_SIZE;

unconstrained fn compute_exp_decay_unconstrained(neg_x_scaled: i64) -> i64 {
    let scale: i64 = 100000;

    let is_beyond_threshold = neg_x_scaled < -300000;

    if is_beyond_threshold {
        let reduced_weight = (-neg_x_scaled / 100000);
        if reduced_weight > 10 {
            1
        } else {
            scale / reduced_weight
        }
    } else {
        let x = neg_x_scaled;
        let x_over_scale = x / scale;

        let term1 = x;
        let term2 = (x * x_over_scale) / 2;
        let term3 = (x * x_over_scale * x_over_scale) / 6;
        let x_squared_over_scale = x * x_over_scale;
        let term4 = (x_squared_over_scale * x_squared_over_scale) / (24 * scale);

        scale + term1 + term2 + term3 + term4
    }
}

pub fn weighting_distribution(actual_len: u32) -> [i64; ARRAY_SIZE] {
    let mut weights = [0; ARRAY_SIZE];
    let decay_rate: i64 = 10000;
    let scale: i64 = 100000;

    let EXP_MINUS_01 = 90484;
    let TOLERANCE = 500;

    let EXPECTED_SUM_25 = 926511;
    let EXPECTED_SUM_50 = 993262;
    let EXPECTED_SUM_100 = 999955;
    let EXPECTED_SUM_200 = 1000000;

    let mut running_sum: i64 = 0;

    for i in 0..ARRAY_SIZE {
        if (i as u32) < actual_len {
            let neg_x_scaled = -decay_rate * (i as i64);
            // safety: constrained below
            let exp_val = unsafe { compute_exp_decay_unconstrained(neg_x_scaled) };

            if i == 0 {
                assert(exp_val == scale);
            } else {
                let expected = (weights[i - 1] * EXP_MINUS_01 + scale / 2) / scale;
                assert(exp_val >= expected - TOLERANCE);
                assert(exp_val <= expected + TOLERANCE);
            }

            assert(exp_val > 0);
            assert(exp_val <= scale);

            weights[i] = exp_val;
            running_sum += exp_val;
        }
    }

    if actual_len == 25 {
        assert(running_sum >= EXPECTED_SUM_25 - 500);
        assert(running_sum <= EXPECTED_SUM_25 + 500);
    } else if actual_len == 50 {
        assert(running_sum >= EXPECTED_SUM_50 - 700);
        assert(running_sum <= EXPECTED_SUM_50 + 700);
    } else if actual_len == 100 {
        assert(running_sum >= EXPECTED_SUM_100 - 1000);
        assert(running_sum <= EXPECTED_SUM_100 + 1000);
    } else if actual_len == 200 {
        assert(running_sum >= EXPECTED_SUM_200 - 1000);
        assert(running_sum <= EXPECTED_SUM_200 + 1000);
    }

    let mut final_weights = [0; ARRAY_SIZE];
    let max_weight: i64 = 100000;
    let min_weight: i64 = 10000;
    let weight_range = max_weight - min_weight;

    for i in 0..ARRAY_SIZE {
        if (i as u32) < actual_len {
            let weighted_val = (weight_range * weights[i]) / scale;
            final_weights[actual_len - 1 - i] = min_weight + weighted_val;
        }
    }

    final_weights
}
