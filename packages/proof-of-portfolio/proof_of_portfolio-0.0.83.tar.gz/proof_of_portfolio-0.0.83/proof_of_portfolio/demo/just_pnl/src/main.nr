global MAX_CHECKPOINTS: u32 = 200;
global ARRAY_SIZE: u32 = 120;
global PNL_NOCONFIDENCE_VALUE: i64 = -100;

global SCALE: i64 = 10_000_000;

fn exp_decay_scaled(neg_x_scaled: i64) -> i64 {
    let scale: i64 = 100000;
    let x_pow_2 = neg_x_scaled * neg_x_scaled;
    let x_pow_3 = x_pow_2 * neg_x_scaled;

    let term1 = neg_x_scaled;
    let term2 = x_pow_2 / (2 * scale);
    let term3 = x_pow_3 / (6 * scale * scale);
    let term4 = (x_pow_3 * neg_x_scaled) / (24 * scale * scale * scale);

    scale + term1 + term2 + term3 + term4
}

pub fn weighting_distribution(actual_len: u32) -> [i64; ARRAY_SIZE] {
    let mut weights = [0; ARRAY_SIZE];
    let max_weight: i64 = 100000;
    let min_weight: i64 = 10000;
    let decay_rate: i64 = 10000;
    let weight_range = max_weight - min_weight;
    let scale: i64 = 100000;

    for i in 0..ARRAY_SIZE {
        if (i as u32) < actual_len {
            let neg_x_scaled = -decay_rate * (i as i64);
            let exp_val_scaled = exp_decay_scaled(neg_x_scaled);

            let weighted_val = (weight_range * exp_val_scaled) / scale;
            weights[actual_len - 1 - i] = min_weight + weighted_val;
        }
    }

    weights
}

pub fn average(daily_values: [i64; ARRAY_SIZE], actual_len: u32, use_weighting: bool) -> i64 {
    let mut result = 0;
    if actual_len > 0 {
        if use_weighting {
            let weights = weighting_distribution(actual_len);
            let mut weighted_sum: i64 = 0;
            let mut sum_of_weights: i64 = 0;

            for i in 0..ARRAY_SIZE {
                if (i as u32) < actual_len {
                    weighted_sum += daily_values[i] * weights[i];
                    sum_of_weights += weights[i];
                }
            }
            if sum_of_weights != 0 {
                result = weighted_sum / sum_of_weights;
            }
        } else {
            let mut sum: i64 = 0;
            for i in 0..ARRAY_SIZE {
                if (i as u32) < actual_len {
                    sum += daily_values[i];
                }
            }
            result = sum / (actual_len as i64);
        }
    }
    result
}

pub fn pnl_score(
    gains: [i64; MAX_CHECKPOINTS],
    losses: [i64; MAX_CHECKPOINTS],
    last_update_times: [u64; MAX_CHECKPOINTS],
    accum_times: [u64; MAX_CHECKPOINTS],
    checkpoint_count: u32,
    target_duration: u64,
    use_weighting: bool,
) -> i64 {
    // Group checkpoints by complete days and sum daily PnL
    let mut daily_pnl = [0; ARRAY_SIZE];
    let mut daily_count = 0;

    for i in 0..MAX_CHECKPOINTS {
        if (i as u32) < checkpoint_count & daily_count < ARRAY_SIZE {
            // Check if this checkpoint represents a complete day
            if accum_times[i] >= target_duration {
                daily_pnl[daily_count] = gains[i] + losses[i];
                daily_count += 1;
            }
        }
    }

    // Return average of daily PnL values
    average(daily_pnl, daily_count, use_weighting)
}

fn main(
    gains: [i64; MAX_CHECKPOINTS],
    losses: [i64; MAX_CHECKPOINTS],
    last_update_times: [u64; MAX_CHECKPOINTS],
    accum_times: [u64; MAX_CHECKPOINTS],
    checkpoint_count: u32,
    target_duration: u64,
    use_weighting: bool,
) -> pub i64 {
    pnl_score(
        gains,
        losses,
        last_update_times,
        accum_times,
        checkpoint_count,
        target_duration,
        use_weighting,
    )
}
