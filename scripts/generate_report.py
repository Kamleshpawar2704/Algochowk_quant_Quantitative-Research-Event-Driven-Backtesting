from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
from src.data import clean_ohlc
from src.research import detect_events, summarize
from src.backtest import run_event_backtest

root=Path(__file__).resolve().parents[1]
df,_=clean_ohlc(pd.read_csv(root/'data'/'nifty50_daily.csv'))
threshold=-.02
events=detect_events(df,threshold,1)
lines=[]
lines.append('# Generated Results Snapshot\n')
lines.append(f'- Data coverage: **{df.Date.min():%Y-%m-%d} → {df.Date.max():%Y-%m-%d}**')
lines.append(f'- Clean observations: **{len(df):,}**')
lines.append(f'- Primary event definition: **daily return ≤ {threshold:.1%}**')
lines.append(f'- Events: **{len(events):,}**\n')
lines.append('| Horizon | N | Event mean | Baseline mean | Excess | Win rate | Bootstrap 95% CI | Welch p |')
lines.append('|---|---:|---:|---:|---:|---:|---|---:|')
for h in [1,3,5]:
    base=df['Close'].shift(-h).div(df['Close']).sub(1).dropna()
    s=summarize(events[f'fwd_{h}d'],base)
    lines.append(f"| {h}D | {s['n']} | {s['mean']:.2%} | {s['baseline_mean']:.2%} | {s['excess_mean']:.2%} | {s['win_rate']:.1%} | [{s['bootstrap_ci_low']:.2%}, {s['bootstrap_ci_high']:.2%}] | {s['welch_p_value']:.3f} |")
train=df.iloc[:int(len(df)*.7)]; test=df.iloc[int(len(df)*.7):]
lines.append('\n## OOS snapshot\n')
for name,part in [('Development',train),('Out-of-sample',test)]:
    ev=detect_events(part,threshold,1)
    base=part['Close'].shift(-3).div(part['Close']).sub(1).dropna()
    s=summarize(ev['fwd_3d'],base)
    lines.append(f"- **{name}:** {len(ev)} events; mean 3D {s['mean']:.2%}; baseline {s['baseline_mean']:.2%}; excess {s['excess_mean']:.2%}; win rate {s['win_rate']:.1%}.")
trades,stats=run_event_backtest(df,threshold,3,5,5,1)
lines.append('\n## Backtest snapshot\n')
lines.append(f"- Trades: **{stats['trades']}**")
lines.append(f"- Net cumulative return: **{stats['cum_return']:.2%}**")
lines.append(f"- Maximum drawdown: **{stats['max_drawdown']:.2%}**")
lines.append('\n> This generated snapshot is intentionally separate from the fixed research design. It records the output produced by the downloaded dataset at run time.\n')
(root/'reports'/'generated_results.md').write_text('\n'.join(lines),encoding='utf-8')
print(root/'reports'/'generated_results.md')
