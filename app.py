from pathlib import Path
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from src.data import clean_ohlc
from src.research import event_table, summarize, detect_events
from src.backtest import run_event_backtest

st.set_page_config(page_title="Event Lens · NIFTY Research Lab", page_icon="◈", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
:root{--ink:#0b1020;--panel:#11182b;--panel2:#17213a;--cyan:#56e0e8;--violet:#a78bfa;--coral:#ff7b72;--paper:#eef3f7;--muted:#94a3b8}
.stApp{background:radial-gradient(circle at 80% 0%,rgba(86,224,232,.10),transparent 32%),radial-gradient(circle at 10% 20%,rgba(167,139,250,.08),transparent 28%),#080c17;color:var(--paper);font-family:Manrope,sans-serif}
.block-container{max-width:1500px;padding:2rem 3rem 4rem}
section[data-testid="stSidebar"]{background:#0b1020;border-right:1px solid #1d2942}
h1,h2,h3{letter-spacing:-.035em} h1{font-size:3.2rem!important;line-height:1.02}
.hero{padding:1.5rem 0 1rem}.eyebrow{font:500 .72rem 'DM Mono';letter-spacing:.18em;color:var(--cyan);text-transform:uppercase}.sub{color:#aeb9cc;max-width:760px;font-size:1rem;line-height:1.65}
.card{background:linear-gradient(145deg,rgba(23,33,58,.92),rgba(13,18,34,.92));border:1px solid #22304d;border-radius:20px;padding:1.1rem 1.2rem;box-shadow:0 18px 50px rgba(0,0,0,.16)}
.metric-label{color:#8290a8;font:500 .68rem 'DM Mono';text-transform:uppercase;letter-spacing:.11em}.metric-value{font-size:1.65rem;font-weight:800;margin-top:.25rem}.metric-note{font-size:.75rem;color:#8290a8;margin-top:.15rem}
.badge{display:inline-flex;padding:.3rem .55rem;border-radius:999px;background:rgba(86,224,232,.09);border:1px solid rgba(86,224,232,.25);color:var(--cyan);font:500 .68rem 'DM Mono'}
.research-note{border-left:3px solid var(--cyan);padding:.8rem 1rem;background:rgba(86,224,232,.04);border-radius:0 12px 12px 0;color:#c7d2e2;line-height:1.6}
[data-testid="stDataFrame"]{border:1px solid #22304d;border-radius:14px;overflow:hidden}
button[kind="primary"]{background:linear-gradient(90deg,#56e0e8,#a78bfa)!important;color:#08101c!important;border:0!important}
small{color:#8190a9!important}
</style>
""", unsafe_allow_html=True)

DATA = Path("data/nifty50_daily.csv")

@st.cache_data(show_spinner=False)
def load_data(path: str):
    df=pd.read_csv(path)
    df,meta=clean_ohlc(df)
    return df,meta

st.sidebar.markdown("### ◈ EVENT LENS")
st.sidebar.caption("NIFTY mean-reversion research console")
if not DATA.exists():
    st.sidebar.warning("No local dataset found.")
    st.sidebar.code("python scripts/download_data.py")
    st.stop()

df, meta = load_data(str(DATA))

st.sidebar.markdown("---")
st.sidebar.markdown("**Experiment controls**")
threshold = st.sidebar.slider("Event threshold", -0.06, -0.01, -0.02, 0.005, format="%.1f%%")
holding = st.sidebar.select_slider("Backtest holding", options=[1,3,5], value=3)
gap = st.sidebar.slider("Minimum event gap (days)", 0, 10, 1)
cost_bps = st.sidebar.number_input("Transaction cost / side (bps)", 0.0, 50.0, 5.0, 1.0)
slippage_bps = st.sidebar.number_input("Slippage / side (bps)", 0.0, 50.0, 5.0, 1.0)

st.markdown('<div class="hero"><div class="eyebrow">Quantitative Research · Event Study · NIFTY 50</div><h1>Does a sharp fall<br>actually mean <i>reversion</i>?</h1><p class="sub">An evidence-first research console for testing the hypothesis that a significant one-day NIFTY fall is followed by recovery. The interface exposes assumptions instead of hiding them behind a single backtest score.</p></div>', unsafe_allow_html=True)
st.markdown('<span class="badge">NO PARAMETER OPTIMISATION</span> &nbsp; <span class="badge">NEXT-OPEN ENTRY</span> &nbsp; <span class="badge">OUT-OF-SAMPLE AWARE</span>', unsafe_allow_html=True)

# Split first 70% / last 30% by date.
split_idx=int(len(df)*0.70)
train=df.iloc[:split_idx].copy(); test=df.iloc[split_idx:].copy()
events=detect_events(df, threshold, gap)
train_events=detect_events(train, threshold, gap)
test_events=detect_events(test, threshold, gap)

bt, btstats=run_event_backtest(df, threshold, holding, cost_bps, slippage_bps, gap)

c1,c2,c3,c4,c5=st.columns(5)
metrics=[("EVENTS",len(events),f"≤ {threshold:.1%}"),("MEAN 3D", events["fwd_3d"].mean() if not events.empty else np.nan,"forward return"),("WIN RATE",(events["fwd_3d"]>0).mean() if not events.empty else np.nan,"positive 3D outcomes"),("OOS EVENTS",len(test_events),f"{test.Date.min():%b %Y} → {test.Date.max():%b %Y}"),("MAX DD",btstats.get("max_drawdown",0),"event backtest")]
for col,(label,val,note) in zip([c1,c2,c3,c4,c5],metrics):
    with col:
        display = "—" if pd.isna(val) else (f"{val:.1%}" if isinstance(val,(float,np.floating)) and abs(val)<2 else f"{val:,.0f}" if isinstance(val,(int,np.integer)) else f"{val:.2f}")
        st.markdown(f'<div class="card"><div class="metric-label">{label}</div><div class="metric-value">{display}</div><div class="metric-note">{note}</div></div>',unsafe_allow_html=True)

st.markdown("## Market tape")
fig=go.Figure(go.Scatter(x=df.Date,y=df.Close,mode="lines",line=dict(color="#56e0e8",width=2),name="NIFTY 50"))
if not events.empty:
    fig.add_trace(go.Scatter(x=events.event_date,y=df.set_index("Date").reindex(events.event_date).Close,mode="markers",marker=dict(color="#ff7b72",size=8,line=dict(color="#fff",width=1)),name="fall events"))
fig.update_layout(height=390,margin=dict(l=0,r=0,t=10,b=0),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#aeb9cc",xaxis=dict(gridcolor="#1c2942"),yaxis=dict(gridcolor="#1c2942"),legend=dict(orientation="h",y=1.08))
st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

left,right=st.columns([1.2,.8])
with left:
    st.markdown("## Evidence matrix")
    rows=[]
    for h in [1,3,5]:
        if events.empty: continue
        base=df["Close"].shift(-h).div(df["Close"]).sub(1).dropna()
        s=summarize(events[f"fwd_{h}d"],base)
        rows.append({"Horizon":f"{h} trading day","N":s["n"],"Event mean":s["mean"],"Baseline mean":s["baseline_mean"],"Excess":s["excess_mean"],"Win rate":s["win_rate"],"Bootstrap 95% CI":f"[{s['bootstrap_ci_low']:.2%}, {s['bootstrap_ci_high']:.2%}]","Welch p":s["welch_p_value"]})
    edf=pd.DataFrame(rows)
    st.dataframe(edf.style.format({"Event mean":"{:.2%}","Baseline mean":"{:.2%}","Excess":"{:.2%}","Win rate":"{:.1%}","Welch p":"{:.3f}"}),use_container_width=True,hide_index=True)
    st.markdown('<div class="research-note"><b>How to read this:</b> the event sample is compared with ordinary forward NIFTY returns over the same calendar period. A positive mean alone is not enough: the baseline, uncertainty, costs and out-of-sample behavior all matter.</div>',unsafe_allow_html=True)
with right:
    st.markdown("## Distribution")
    if not events.empty:
        plotdf=events[["fwd_1d","fwd_3d","fwd_5d"]].melt(var_name="Horizon",value_name="Return")
        plotdf["Horizon"]=plotdf.Horizon.str.replace("fwd_"," ").str.replace("d", "D")
        fig2=px.box(plotdf,x="Horizon",y="Return",points="outliers",height=340)
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#aeb9cc",yaxis_tickformat=".1%",margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig2,use_container_width=True,config={"displayModeBar":False})

st.markdown("## Robustness, not optimisation")
rob=[]
for th in [-0.015,-0.02,-0.025,-0.03]:
    ev=detect_events(df,th,gap)
    if ev.empty: continue
    base=df["Close"].shift(-3).div(df["Close"]).sub(1).dropna()
    s=summarize(ev["fwd_3d"],base)
    rob.append({"Threshold":th,"Events":s["n"],"Mean 3D":s["mean"],"Baseline":s["baseline_mean"],"Excess":s["excess_mean"],"Win rate":s["win_rate"]})
rdf=pd.DataFrame(rob)
st.dataframe(rdf.style.format({"Threshold":"{:.1%}","Mean 3D":"{:.2%}","Baseline":"{:.2%}","Excess":"{:.2%}","Win rate":"{:.1%}"}),use_container_width=True,hide_index=True)

st.markdown("## Out-of-sample check")
oos=[]
for name,part in [("Development",train),("Out-of-sample",test)]:
    ev=detect_events(part,threshold,gap)
    if ev.empty: continue
    base=part["Close"].shift(-holding).div(part["Close"]).sub(1).dropna()
    s=summarize(ev[f"fwd_{holding}d"],base)
    oos.append({"Period":name,"Start":part.Date.min().date(),"End":part.Date.max().date(),"Events":s["n"],"Mean":s["mean"],"Baseline":s["baseline_mean"],"Excess":s["excess_mean"],"Win rate":s["win_rate"]})
st.dataframe(pd.DataFrame(oos).style.format({"Mean":"{:.2%}","Baseline":"{:.2%}","Excess":"{:.2%}","Win rate":"{:.1%}"}),use_container_width=True,hide_index=True)

st.markdown("## Event-driven backtest")
b1,b2,b3,b4=st.columns(4)
for col,(lab,val) in zip([b1,b2,b3,b4],[("TRADES",btstats.get("trades",0)),("NET CUM",btstats.get("cum_return",0)),("MAX DD",btstats.get("max_drawdown",0)),("COST MODEL",f"{cost_bps+slippage_bps:.0f} bps/side")]):
    with col: st.markdown(f'<div class="card"><div class="metric-label">{lab}</div><div class="metric-value">{val if isinstance(val,str) else (f"{val:.1%}" if isinstance(val,float) else f"{val:,}")}</div></div>',unsafe_allow_html=True)
if not bt.empty:
    f3=go.Figure(go.Scatter(x=bt.exit_date,y=bt.equity,mode="lines+markers",line=dict(color="#a78bfa",width=2),marker=dict(size=5)))
    f3.update_layout(height=300,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#aeb9cc",yaxis_title="Growth of ₹1",xaxis=dict(gridcolor="#1c2942"),yaxis=dict(gridcolor="#1c2942"),margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(f3,use_container_width=True,config={"displayModeBar":False})

st.markdown("## Researcher's challenge log")
q1,q2=st.columns(2)
with q1:
    st.markdown("**What could make this result look better than it is?**")
    st.markdown("• threshold selection after seeing results  • overlapping events  • regime changes  • small event samples  • close-to-close signal with next-open execution  • costs and slippage  • non-stationarity")
with q2:
    st.markdown("**What would falsify the hypothesis?**")
    st.markdown("A weak or negative excess return versus the calendar-matched baseline, unstable results across reasonable thresholds/holding periods, or failure to persist in the unseen period would materially weaken the claim of a repeatable recovery effect.")

st.caption(f"Data coverage: {meta['start']:%d %b %Y} → {meta['end']:%d %b %Y} · {meta['rows_after']:,} cleaned rows · Source: Yahoo Finance ^NSEI · Research console is for reproducible investigation, not investment advice.")
