from __future__ import annotations
import numpy as np
import pandas as pd


def run_event_backtest(df, threshold=-0.02, holding=3, cost_bps=5, slippage_bps=5, gap=1):
    x = df.reset_index(drop=True).copy()
    x["ret"] = x["Close"].pct_change()
    event_idx = np.flatnonzero(x["ret"].le(threshold).to_numpy())
    selected=[]; last=-10**9
    for i in event_idx:
        if i + holding >= len(x): continue
        if i > last + gap:
            selected.append(i); last=i
    trades=[]
    for i in selected:
        entry_i=i+1
        exit_i=entry_i+holding-1
        entry=float(x.loc[entry_i,"Open"])
        exitp=float(x.loc[exit_i,"Close"])
        gross=exitp/entry-1
        friction=2*(cost_bps+slippage_bps)/10000
        net=gross-friction
        trades.append({"event_date":x.loc[i,"Date"],"entry_date":x.loc[entry_i,"Date"],"exit_date":x.loc[exit_i,"Date"],"entry":entry,"exit":exitp,"gross_return":gross,"net_return":net})
    t=pd.DataFrame(trades)
    if t.empty:
        return t, {"trades":0,"cum_return":0.0,"max_drawdown":0.0}
    t["equity"]=(1+t["net_return"]).cumprod()
    peak=t["equity"].cummax()
    dd=t["equity"]/peak-1
    return t, {"trades":len(t),"cum_return":float(t["equity"].iloc[-1]-1),"max_drawdown":float(dd.min()),"win_rate":float((t["net_return"]>0).mean()),"mean_trade":float(t["net_return"].mean())}
