from __future__ import annotations
import pandas as pd
import numpy as np

REQUIRED = ["Date", "Open", "High", "Low", "Close"]


def clean_ohlc(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    x = df.copy()
    # Flatten yfinance MultiIndex columns if present.
    if isinstance(x.columns, pd.MultiIndex):
        x.columns = [c[0] for c in x.columns]
    x.columns = [str(c).strip().title() for c in x.columns]
    if "Date" not in x.columns and x.index.name:
        x = x.reset_index()
    missing = [c for c in REQUIRED if c not in x.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    x["Date"] = pd.to_datetime(x["Date"], errors="coerce").dt.tz_localize(None)
    for c in REQUIRED[1:]:
        x[c] = pd.to_numeric(x[c], errors="coerce")
    before = len(x)
    duplicate_dates = int(x["Date"].duplicated().sum())
    invalid_ohlc = int((x[REQUIRED[1:]].isna().any(axis=1)).sum())
    bad_ranges = int(((x["High"] < x[["Open", "Close", "Low"]].max(axis=1)) | (x["Low"] > x[["Open", "Close", "High"]].min(axis=1))).sum())
    x = x.dropna(subset=REQUIRED).drop_duplicates("Date").sort_values("Date").reset_index(drop=True)
    x = x[(x["Open"] > 0) & (x["High"] > 0) & (x["Low"] > 0) & (x["Close"] > 0)]
    x["daily_return"] = x["Close"].pct_change()
    x["next_open_return"] = x["Open"].shift(-1) / x["Close"] - 1
    meta = {
        "rows_before": before,
        "rows_after": len(x),
        "duplicate_dates": duplicate_dates,
        "invalid_ohlc_rows": invalid_ohlc,
        "bad_ohlc_range_rows": bad_ranges,
        "start": x["Date"].min(),
        "end": x["Date"].max(),
    }
    return x, meta


def download_nifty(start="2010-01-01", end=None) -> pd.DataFrame:
    import yfinance as yf
    if end is None:
        end = (pd.Timestamp.today().normalize() + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    raw = yf.download("^NSEI", start=start, end=end, auto_adjust=False, progress=False)
    if raw.empty:
        raise RuntimeError("No NIFTY data returned. Check internet access or Yahoo Finance availability.")
    raw = raw.reset_index()
    clean, _ = clean_ohlc(raw)
    return clean
