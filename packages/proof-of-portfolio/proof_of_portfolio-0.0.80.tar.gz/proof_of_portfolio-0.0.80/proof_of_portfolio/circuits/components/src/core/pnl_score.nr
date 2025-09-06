use crate::utils::{average::average, constants::{ARRAY_SIZE, MAX_CHECKPOINTS}};

pub fn pnl_score(
    gains: [i64; MAX_CHECKPOINTS],
    losses: [i64; MAX_CHECKPOINTS],
    last_update_times: [u64; MAX_CHECKPOINTS],
    accum_times: [u64; MAX_CHECKPOINTS],
    checkpoint_count: u32,
    target_duration: u64,
    weights: [i64; ARRAY_SIZE],
    use_weighting: bool,
    account_size: i64,
) -> i64 {
    let mut daily_pnl = [0; ARRAY_SIZE];
    let mut daily_count = 0;

    for i in 0..MAX_CHECKPOINTS {
        if (i as u32) < checkpoint_count & daily_count < ARRAY_SIZE {
            if accum_times[i] >= target_duration {
                let log_return = gains[i] + losses[i];

                daily_pnl[daily_count] = (log_return * account_size) / 10000000;
                daily_count += 1;
            }
        }
    }

    let sum_of_weights = if use_weighting {
        let mut sum: i64 = 0;
        for i in 0..ARRAY_SIZE {
            if (i as u32) < daily_count {
                sum += weights[i];
            }
        }
        sum
    } else {
        daily_count as i64
    };

    average(
        daily_pnl,
        daily_count,
        weights,
        use_weighting,
        sum_of_weights,
    )
}

#[test]
fn test_pnl_score_basic() {
    let mut gains = [0; MAX_CHECKPOINTS];
    let mut losses = [0; MAX_CHECKPOINTS];
    let mut last_update_times = [0; MAX_CHECKPOINTS];
    let mut accum_times = [0; MAX_CHECKPOINTS];

    gains[0] = 100;
    losses[0] = -50;
    accum_times[0] = 86400;

    gains[1] = 200;
    losses[1] = -100;
    accum_times[1] = 86400;

    let weights = [100000; ARRAY_SIZE];
    let result = pnl_score(
        gains,
        losses,
        last_update_times,
        accum_times,
        2,
        86400,
        weights,
        false,
        1000000,
    );

    assert(result == 75);
}

#[test]
fn test_pnl_score_incomplete_days() {
    let mut gains = [0; MAX_CHECKPOINTS];
    let mut losses = [0; MAX_CHECKPOINTS];
    let mut last_update_times = [0; MAX_CHECKPOINTS];
    let mut accum_times = [0; MAX_CHECKPOINTS];

    gains[0] = 100;
    losses[0] = -50;
    accum_times[0] = 86400;

    gains[1] = 200;
    losses[1] = -100;
    accum_times[1] = 43200;

    let weights = [100000; ARRAY_SIZE];
    let result = pnl_score(
        gains,
        losses,
        last_update_times,
        accum_times,
        2,
        86400,
        weights,
        false,
        1000000,
    );

    assert(result == 50);
}
