import pandas as pd
import numpy as np
from src.data import clean_ohlc
from src.research import detect_events, summarize
from src.backtest import run_event_backtest


def fixture():
    dates = pd.bdate_range('2024-01-01', periods=20)
    close = np.array([100,101,102,103,104,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114], dtype=float)
    return pd.DataFrame({'Date':dates,'Open':close,'High':close+1,'Low':close-1,'Close':close})


def test_clean_ohlc_sorts_and_removes_duplicates():
    x = fixture().iloc[[3,2,2,1]].copy()
    cleaned, meta = clean_ohlc(x)
    assert cleaned.Date.is_monotonic_increasing
    assert meta['duplicate_dates'] == 1


def test_event_detection_uses_next_open():
    x = fixture()
    x.loc[5,'Close'] = 90
    x.loc[6,'Open'] = 91
    ev = detect_events(x, threshold=-0.02)
    assert len(ev) >= 1
    assert ev.iloc[0].entry_date == x.loc[6,'Date']
    assert ev.iloc[0].entry_price == 91


def test_summary_contains_baseline_and_ci():
    s = summarize(pd.Series([.01,.02,-.01,.03]), pd.Series([.005,.01,.00,.01]))
    assert s['n'] == 4
    assert 'bootstrap_ci_low' in s and 'bootstrap_ci_high' in s
    assert 'excess_mean' in s


def test_backtest_returns_metrics():
    x=fixture(); x.loc[5,'Close']=90; x.loc[6,'Open']=91
    trades, stats=run_event_backtest(x, threshold=-.02, holding=3)
    assert stats['trades'] >= 1
    assert 'max_drawdown' in stats
