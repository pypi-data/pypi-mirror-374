use crate::utils::constants::ARRAY_SIZE;

fn exp_decay_scaled(neg_x_scaled: i64) -> i64 {
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
