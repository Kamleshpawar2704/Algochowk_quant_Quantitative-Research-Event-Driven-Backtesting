# Data Source Record

**Primary source:** Yahoo Finance, NIFTY 50 (`^NSEI`) Historical Data.

**Source page:** https://finance.yahoo.com/quote/%5ENSEI/history/

**Fields used:** Date, Open, High, Low, Close. Volume is retained by Yahoo when available but is not required by the research hypothesis.

**Download method:** `scripts/download_data.py` uses `yfinance` to request daily `^NSEI` data from 2010-01-01 through the latest available trading session at download time.

**Independent reference:** NSE's index FAQ states that NIFTY 50 historical data is available from NSE's Indices / Statistics resources and that the historical series is useful for research. NSE's current NIFTY 50 page also describes the index and its methodology.

**Cleaning:** parse dates; flatten multi-index columns returned by yfinance; coerce OHLC numeric values; remove missing required OHLC rows, duplicate dates and non-positive prices; flag impossible OHLC relationships; sort chronologically; calculate returns only after cleaning.

**Reproducibility:** the actual start/end dates and cleaned row count are printed by `scripts/download_data.py` and surfaced in the Streamlit footer.
