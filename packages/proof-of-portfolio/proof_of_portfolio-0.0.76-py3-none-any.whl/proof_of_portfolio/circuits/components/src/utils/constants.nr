pub global ARRAY_SIZE: u32 = 256;
pub global SCALE: i64 = 10_000_000;
pub global DAYS_IN_YEAR: i64 = 365;
pub global STATISTICAL_CONFIDENCE_MINIMUM_N: u32 = 60;

// Risk-free rate (as basis points, 419 = 4.19%
pub global ANNUAL_RISK_FREE_RATE_BP: i64 = 419;
pub global DAILY_LOG_RISK_FREE_RATE: i64 = 2351; // (0.0419 / 365) * SCALE

// Minimum values for ratio calculations (scaled for integer math)
pub global SHARPE_STDDEV_MINIMUM: i64 = 100000; // 0.01 * 10^7
pub global OMEGA_LOSS_MINIMUM: i64 = 100000; // 0.01 * 10^7
pub global SORTINO_DOWNSIDE_MINIMUM: i64 = 100000; // 0.01 * 10^7

// Scaling factors for precision in integer calculations
pub global OMEGA_SCALE_FACTOR: i64 = 1000000000; // 1B for Omega precision
pub global SHARPE_SCALE_FACTOR: i64 = 1000000; // 1M for Sharpe precision
pub global LARGE_POSITIVE_VALUE: i64 = 1000000000; // Used for ratios when denominator is zero/minimal
pub global RATIO_SCALE_FACTOR: i64 = 1000000; // Standard 1M scaling for ratios

// Default return values for insufficient confidence (will be divided by RATIO_SCALE_FACTOR)
pub global CALMAR_NOCONFIDENCE_VALUE: i64 = -100000000; // -100 * 10^6 -> -100 after scaling
pub global SHARPE_NOCONFIDENCE_VALUE: i64 = -100000000; // -100 * 10^6 -> -100 after scaling
pub global OMEGA_NOCONFIDENCE_VALUE: i64 = 0; // Omega uses 0.0 in subnet
pub global SORTINO_NOCONFIDENCE_VALUE: i64 = -100000000; // -100 * 10^6 -> -100 after scaling
pub global STATISTICAL_CONFIDENCE_NOCONFIDENCE_VALUE: i64 = -100000000; // -100 * 10^6 -> -100 after scaling
