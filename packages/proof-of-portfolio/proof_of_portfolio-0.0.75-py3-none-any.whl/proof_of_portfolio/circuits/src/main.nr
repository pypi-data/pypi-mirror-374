use components::core::{
    calmar::calmar, drawdown::daily_max_drawdown, omega::omega, pnl_score::pnl_score,
    sharpe::sharpe, sortino::sortino, tstat::statistical_confidence,
};
use components::core::cps_to_log_returns::{cps_to_log_returns, MAX_CHECKPOINTS, MAX_DAYS};
use components::core::merkle::{
    build_merkle_root, hash_return, hash_signal, MAX_RETURNS, MAX_SIGNALS, MERKLE_DEPTH,
    merkle_inclusion_check, TradingSignal,
};
use components::utils::{
    ann_excess_return::ann_excess_return, average::average, constants::ARRAY_SIZE,
    variance::variance, weighting_distribution::weighting_distribution,
};

fn main(
    gains: [i64; MAX_CHECKPOINTS],
    losses: [i64; MAX_CHECKPOINTS],
    last_update_times: [u64; MAX_CHECKPOINTS],
    accum_times: [u64; MAX_CHECKPOINTS],
    checkpoint_count: u32,
    target_duration: u64,
    signals: [TradingSignal; MAX_SIGNALS],
    signals_count: u32,
    path_elements: [[Field; MERKLE_DEPTH]; MAX_SIGNALS],
    path_indices: [[Field; MERKLE_DEPTH]; MAX_SIGNALS],
    signals_merkle_root: pub Field,
    returns_merkle_root: pub Field,
    risk_free_rate: i64,
    use_weighting: bool,
    bypass_confidence: bool,
    account_size: i64,
) -> pub [Field; 8] {
    // Convert checkpoints to log returns
    let (log_returns, valid_days) = cps_to_log_returns(
        gains,
        losses,
        last_update_times,
        accum_times,
        checkpoint_count,
        target_duration,
    );
    let n_returns = valid_days;

    // Verify all trading signals are included in the merkle tree
    let mut all_verified = true;
    for i in 0..MAX_SIGNALS {
        if (i as u32) < signals_count {
            let signal_hash = hash_signal(signals[i]);
            let verified = merkle_inclusion_check(
                signal_hash,
                signals_merkle_root,
                path_elements[i],
                path_indices[i],
            );
            all_verified = all_verified & verified;
        }
    }
    assert(all_verified);

    // Build root from returns
    let mut leaves = [0; MAX_RETURNS];
    for i in 0..MAX_RETURNS {
        if (i as u32) < n_returns {
            leaves[i] = hash_return(log_returns[i]);
        }
    }
    let _computed_returns_root = build_merkle_root(leaves, n_returns);
    // Check that the computed root matches the expected root
    assert(_computed_returns_root == returns_merkle_root);

    // Build array from returns
    let mut returns_array = [0; ARRAY_SIZE];
    for i in 0..MAX_DAYS {
        if (i as u32) < n_returns {
            returns_array[i] = log_returns[i];
        }
    }

    let weights = if use_weighting {
        weighting_distribution(n_returns)
    } else {
        // Equal weights when weighting is disabled
        let mut equal_weights = [0; ARRAY_SIZE];
        for i in 0..ARRAY_SIZE {
            equal_weights[i] = 100000; // Scale value for equal weighting
        }
        equal_weights
    };

    let sum_of_weights = if use_weighting {
        let mut sum: i64 = 0;
        for i in 0..ARRAY_SIZE {
            if (i as u32) < n_returns {
                sum += weights[i];
            }
        }
        sum
    } else {
        n_returns as i64
    };

    let avg_daily_return = average(
        returns_array,
        n_returns,
        weights,
        use_weighting,
        sum_of_weights,
    );
    let variance_val = variance(
        returns_array,
        n_returns,
        1,
        weights,
        use_weighting,
        sum_of_weights,
    );
    let ann_excess_return_val = ann_excess_return(
        returns_array,
        n_returns,
        risk_free_rate,
        weights,
        use_weighting,
    );

    let avg_daily_pnl = avg_daily_return;

    let sharpe_ratio = sharpe(
        returns_array,
        n_returns,
        risk_free_rate,
        weights,
        use_weighting,
        bypass_confidence,
        avg_daily_return,
        variance_val,
        ann_excess_return_val,
    );
    let dmd = daily_max_drawdown(returns_array, n_returns);
    let calmar_ratio = calmar(
        returns_array,
        n_returns,
        risk_free_rate,
        weights,
        use_weighting,
        bypass_confidence,
        avg_daily_return,
        variance_val,
        ann_excess_return_val,
    );
    let omega_ratio = omega(
        returns_array,
        n_returns,
        weights,
        use_weighting,
        bypass_confidence,
    );
    let sortino_ratio = sortino(
        returns_array,
        n_returns,
        risk_free_rate,
        weights,
        use_weighting,
        bypass_confidence,
        avg_daily_return,
        variance_val,
        ann_excess_return_val,
    );
    let stat_confidence = statistical_confidence(
        returns_array,
        n_returns,
        weights,
        use_weighting,
        bypass_confidence,
        avg_daily_return,
        variance_val,
        ann_excess_return_val,
    );
    let pnl_score_result = pnl_score(
        gains,
        losses,
        last_update_times,
        accum_times,
        checkpoint_count,
        target_duration,
        weights,
        use_weighting,
        account_size,
    );

    [
        (avg_daily_pnl as u64) as Field,
        (sharpe_ratio as u64) as Field,
        (dmd as u64) as Field,
        (calmar_ratio as u64) as Field,
        (omega_ratio as u64) as Field,
        (sortino_ratio as u64) as Field,
        (stat_confidence as u64) as Field,
        (pnl_score_result as u64) as Field,
    ]
}
