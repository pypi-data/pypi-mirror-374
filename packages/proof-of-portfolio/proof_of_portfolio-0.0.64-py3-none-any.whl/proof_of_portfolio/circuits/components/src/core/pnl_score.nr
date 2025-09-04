use crate::core::cps_to_log_returns::MAX_CHECKPOINTS;
use crate::utils::{average::average, constants::ARRAY_SIZE};

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

#[test]
fn test_pnl_score_basic() {
    let mut gains = [0; MAX_CHECKPOINTS];
    let mut losses = [0; MAX_CHECKPOINTS];
    let mut last_update_times = [0; MAX_CHECKPOINTS];
    let mut accum_times = [0; MAX_CHECKPOINTS];

    // Day 1: +100 gain, -50 loss = +50 PnL
    gains[0] = 100;
    losses[0] = -50;
    accum_times[0] = 86400; // 1 day in seconds

    // Day 2: +200 gain, -100 loss = +100 PnL
    gains[1] = 200;
    losses[1] = -100;
    accum_times[1] = 86400;

    let result = pnl_score(
        gains,
        losses,
        last_update_times,
        accum_times,
        2,
        86400,
        false,
    );

    // Average: (50 + 100) / 2 = 75
    assert(result == 75);
}

#[test]
fn test_pnl_score_incomplete_days() {
    let mut gains = [0; MAX_CHECKPOINTS];
    let mut losses = [0; MAX_CHECKPOINTS];
    let mut last_update_times = [0; MAX_CHECKPOINTS];
    let mut accum_times = [0; MAX_CHECKPOINTS];

    // Complete day: +100 gain, -50 loss = +50 PnL
    gains[0] = 100;
    losses[0] = -50;
    accum_times[0] = 86400;

    // Incomplete day (should be ignored)
    gains[1] = 200;
    losses[1] = -100;
    accum_times[1] = 43200; // 12 hours, less than target

    let result = pnl_score(
        gains,
        losses,
        last_update_times,
        accum_times,
        2,
        86400,
        false,
    );

    // Only complete day counted: 50
    assert(result == 50);
}
