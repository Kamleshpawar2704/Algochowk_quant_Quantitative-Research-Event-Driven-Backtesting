from __future__ import annotations
import numpy as np
import pandas as pd
from scipy import stats


def detect_events(df: pd.DataFrame, threshold=-0.02, min_gap=1, entry="next_open") -> pd.DataFrame:
    x = df.copy().reset_index(drop=True)
    x["event_return"] = x["Close"].pct_change()
    idx = np.flatnonzero(x["event_return"].le(threshold).to_numpy())
    selected = []
    last = -10**9
    for i in idx:
        if i > last + min_gap:
            selected.append(i)
            last = i
    rows = []
    for i in selected:
        if i + 5 >= len(x):
            continue
        entry_i = i + 1 if entry == "next_open" else i
        entry_price = float(x.loc[entry_i, "Open"] if entry == "next_open" else x.loc[i, "Close"])
        row = {"event_idx": i, "event_date": x.loc[i, "Date"], "event_return": x.loc[i, "event_return"], "entry_date": x.loc[entry_i, "Date"], "entry_price": entry_price}
        for h in [1, 3, 5]:
            exit_i = entry_i + h - 1
            if exit_i < len(x):
                row[f"fwd_{h}d"] = x.loc[exit_i, "Close"] / entry_price - 1
        rows.append(row)
    return pd.DataFrame(rows)


def bootstrap_ci(values, n=10000, seed=42, alpha=0.05):
    v = np.asarray(values, dtype=float)
    v = v[np.isfinite(v)]
    if len(v) < 2:
        return (np.nan, np.nan)
    rng = np.random.default_rng(seed)
    samples = rng.choice(v, size=(n, len(v)), replace=True).mean(axis=1)
    return tuple(np.quantile(samples, [alpha / 2, 1 - alpha / 2]))


def summarize(event_returns: pd.Series, baseline_returns: pd.Series) -> dict:
    e = pd.Series(event_returns).dropna().astype(float)
    b = pd.Series(baseline_returns).dropna().astype(float)
    ci_lo, ci_hi = bootstrap_ci(e)
    t = stats.ttest_1samp(e, 0.0, nan_policy="omit") if len(e) > 1 else (np.nan, np.nan)
    # Difference in means is tested against the baseline distribution with Welch's t-test.
    welch = stats.ttest_ind(e, b, equal_var=False, nan_policy="omit") if len(e) > 1 and len(b) > 1 else (np.nan, np.nan)
    return {
        "n": int(len(e)),
        "mean": float(e.mean()) if len(e) else np.nan,
        "median": float(e.median()) if len(e) else np.nan,
        "win_rate": float((e > 0).mean()) if len(e) else np.nan,
        "std": float(e.std(ddof=1)) if len(e) > 1 else np.nan,
        "bootstrap_ci_low": float(ci_lo),
        "bootstrap_ci_high": float(ci_hi),
        "t_stat_vs_zero": float(t.statistic),
        "p_value_vs_zero": float(t.pvalue),
        "baseline_mean": float(b.mean()) if len(b) else np.nan,
        "excess_mean": float(e.mean() - b.mean()) if len(e) and len(b) else np.nan,
        "welch_p_value": float(welch.pvalue),
    }


def event_table(df, threshold=-0.02, gap=1):
    events = detect_events(df, threshold, gap)
    if events.empty:
        return events
    for h in [1,3,5]:
        baseline = df["Close"].shift(-(h)).div(df["Close"]).sub(1).dropna()
        events.attrs[f"summary_{h}"] = summarize(events[f"fwd_{h}d"], baseline)
    return events
