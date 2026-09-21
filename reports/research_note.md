# Research Note — NIFTY Post-Fall Recovery

## Hypothesis

**H:** After a significant one-day fall in NIFTY 50, the index has a positive forward return over the next few trading days that is larger than its normal forward return over the same period.

The primary event is a close-to-close NIFTY return of **≤ -2.0%**. The threshold is fixed before robustness analysis: -2% is large enough to represent an unusual daily move while still producing a usable event sample. The experiment also checks nearby thresholds rather than choosing the threshold with the strongest historical result.

## Event, entry, exit and costs

The event return is calculated from the event day's close versus the previous trading day's close. Because the event is only observable after that close, the tradable experiment enters at the **next trading day's open**, avoiding look-ahead. Research forward returns are measured for 1, 3 and 5 trading days from that executable entry. The event-driven extension uses the selected holding period, 5 bps/side transaction cost and 5 bps/side slippage by default. Closely occurring events are separated by a configurable one-day minimum gap to reduce dependence from the same sell-off episode.

## Data and validation

Daily NIFTY 50 OHLC data are downloaded from Yahoo Finance ticker `^NSEI`; the exact download date and coverage are recorded by the reproducibility script. NSE documentation independently identifies historical NIFTY data as available for research. Required fields are Date, Open, High, Low and Close. The cleaning layer checks duplicate dates, ordering, missing/invalid OHLC values and impossible high/low relationships. It does not interpolate price observations.

## Statistical evidence

For each horizon I report sample size, mean, median, win rate, dispersion and a bootstrap 95% confidence interval for the event mean. A one-sample test against zero is supplementary; the more relevant comparison is against normal NIFTY forward returns over the same calendar period. A Welch test is used for the event-versus-baseline comparison because the two samples can have different variances and sizes. Statistical significance is not treated as economic significance: costs, slippage, drawdown and out-of-sample behavior are considered separately.

## Baseline and robustness

The baseline is the ordinary forward NIFTY return for the same holding period and calendar sample, rather than a zero-return benchmark. Robustness changes the event threshold to **-1.5%, -2.0%, -2.5% and -3.0%** and checks 1/3/5-day horizons. These are sensitivity checks, not an optimisation exercise. If the effect only exists for one narrowly chosen parameter, that is evidence against a stable relationship.

## Out-of-sample validation

The first 70% of chronological observations is treated as development data and the final 30% as unseen out-of-sample data. The same event definition is then applied without re-selection. The key question is whether the sign and magnitude of the event-minus-baseline relationship persist, not whether the OOS period produces a positive backtest by itself.

## Falsification / limitations

The hypothesis should be weakened if event returns do not beat the matched baseline, if the effect changes materially across nearby thresholds/holding periods, or if it disappears in the unseen period. Important limitations include regime changes, event clustering, sample size, daily-bar execution assumptions, slippage, and the possibility that any apparent effect is a historical pattern rather than a causal or persistent mechanism.

**Reproducible results:** run `python scripts/download_data.py`, then `python scripts/generate_report.py`. The generated section records the actual event counts, means, confidence intervals, OOS results and backtest metrics from the downloaded dataset rather than hard-coding numbers into this note.
