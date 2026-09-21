# ◈ Event Lens — NIFTY Event-Driven Research Lab

> **AlgoChowk Quant Engineer Intern Challenge**  
> Research question: *After a significant one-day fall in NIFTY, does the market tend to recover over the next few trading days?*

![Research Console](https://dummyimage.com/1600x760/0b1020/56e0e8&text=Event+Lens+%7C+NIFTY+Research+Console)

## Why this project is different

This is intentionally **not a return-maximisation dashboard**. The UI is built around the research loop: **define → detect → compare → stress → validate → challenge**. Every important assumption is visible in the sidebar, and the dashboard shows the event sample alongside a calendar-matched baseline.

The visual system uses an **Obsidian + Electric Cyan + Violet + Coral** palette to separate research state, uncertainty, events and experiment controls without turning the project into a generic trading terminal.

## Research design

| Decision | Definition |
|---|---|
| Event | NIFTY close-to-close return ≤ **-2.0%** |
| Signal timing | Event is only known after the event-day close |
| Entry | **Next trading day's open** |
| Holding periods | 1, 3 and 5 trading days for research; configurable backtest |
| Recovery measure | Forward close return from executable next-open entry |
| Baseline | Ordinary NIFTY forward returns over the same sample period |
| Event dependence | Events must be separated by a configurable minimum gap; default 1 day |
| Costs | Default 5 bps/side transaction cost + 5 bps/side slippage |
| OOS split | First 70% of observations = development; final 30% = unseen OOS |
| Primary uncertainty | Bootstrap 95% CI for mean event return |
| Statistical comparison | One-sample t-test vs 0 and Welch test vs baseline |

The -2% event threshold is deliberately simple and chosen **before** robustness testing. The robustness panel checks -1.5%, -2.0%, -2.5% and -3.0% rather than searching for a threshold that maximises returns.

## Data source

Primary downloadable source used by the application: **Yahoo Finance, ticker `^NSEI` (NIFTY 50)**. The source exposes daily Open, High, Low and Close fields. The assignment explicitly permits sourcing the NIFTY data independently and asks the source, date range, fields and cleaning steps to be documented.

NSE's own documentation confirms that NIFTY 50 historical data is available through NSE/Index Statistics and that the historical series is intended for research. See the source links in `reports/data_sources.md`.

Run:

```bash
python scripts/download_data.py
```

This downloads from Yahoo Finance and creates `data/nifty50_daily.csv`. The repository deliberately does **not** pretend a generated local CSV is immutable: the download date and actual coverage are recorded in the generated research report.

## Validation / cleaning

The engine checks:

- duplicate dates
- chronological ordering
- missing Date/OHLC values
- non-positive OHLC values
- impossible OHLC ranges (`High` below Open/Close or `Low` above Open/Close)
- actual start/end coverage

Rows failing required-field validation are excluded and the counts are recorded. No interpolation is used for price data.

## Reproduce

### 1. Create environment

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Download data

```bash
python scripts/download_data.py
```

### 3. Launch the research console

```bash
streamlit run app.py
```

### 4. Run tests

```bash
pytest -q
```

### 5. Generate the reproducible research note

```bash
python scripts/generate_report.py
```

## Project structure

```text
algochowk_quant/
├── app.py                         # polished Streamlit research UI
├── requirements.txt
├── README.md
├── data/
│   ├── README.md
│   └── nifty50_daily.csv          # generated locally by download script
├── reports/
│   ├── research_note.md           # max-2-page submission note
│   ├── ai_usage_note.md           # max-1-page AI usage note
│   └── data_sources.md
├── scripts/
│   ├── download_data.py
│   └── generate_report.py
├── src/
│   ├── data.py                    # download + validation
│   ├── research.py                 # events + statistics
│   └── backtest.py                 # simple event-driven backtest
└── tests/
    └── test_research.py
```

## Statistical reasoning

The project does not treat a positive average as proof. For each holding period it reports:

- number of observations
- mean and median
- win rate
- standard deviation
- bootstrap confidence interval
- test against zero
- excess return relative to the matched baseline
- Welch comparison against the baseline

A statistically significant difference can still be economically irrelevant after costs, and an apparently attractive historical result can disappear out-of-sample. Those are explicit parts of the analysis rather than footnotes.

## Bias / falsification checklist

The analysis specifically challenges:

1. **Look-ahead bias:** the event uses the close, but entry is delayed to the next open.
2. **Overlapping events:** a minimum event gap is enforced.
3. **Multiple testing:** threshold/holding changes are shown as robustness checks, not selected for the best result.
4. **Post-hoc selection:** the primary threshold is fixed at -2% before the robustness panel.
5. **Costs/slippage:** included in the tradable extension.
6. **Regime dependence:** development and final out-of-sample periods are reported separately.
7. **Sample size:** event counts are always displayed beside summary statistics.

## Submission package

The assignment asks for a GitHub repository, a max-2-page Research Note, README, max-1-page AI Usage Note, and a 2–3 minute walkthrough video. This repository contains the written components and a reproducible application; the video should demonstrate the experiment controls, evidence matrix, robustness table, OOS split and backtest rather than simply scrolling through code.

## Important limitation

This is an index-level event study using daily OHLC data. It is not a complete execution model, does not model market impact, does not use intraday information, and does not establish a causal mechanism for any recovery. A negative or unstable result is a valid research outcome.

## Source links

- Yahoo Finance NIFTY 50 historical data: https://finance.yahoo.com/quote/%5ENSEI/history/
- NSE NIFTY 50 historical-data documentation: https://www.nseindia.com/static/products-services/indices-faqs
- NSE NIFTY 50 index page: https://www.nseindia.com/static/products-services/indices-nifty50-index
