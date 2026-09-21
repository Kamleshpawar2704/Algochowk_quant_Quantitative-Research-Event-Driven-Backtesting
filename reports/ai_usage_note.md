# AI Usage Note

## Tools used

ChatGPT was used as a research and engineering assistant during the project. Python, Pandas, NumPy, SciPy, statsmodels, Plotly and Streamlit were used for implementation.

## How AI was used

AI assistance was used to structure the repository, draft the research-engine architecture, explain bootstrap confidence intervals and Welch tests, identify common backtesting biases, generate initial Python/Streamlit code, and improve the dashboard information hierarchy and visual design.

## My decisions

The research decisions were kept explicit rather than delegated to an optimiser. I selected the primary **-2% event threshold**, next-open entry, 1/3/5-day research horizons, minimum event gap, 70/30 chronological OOS split, calendar-matched baseline and the cost/slippage assumptions. I also chose to treat robustness as a falsification exercise rather than search for the best historical return.

## Suggestions changed or challenged

Generic strategy-building suggestions were deliberately constrained when they risked turning the task into a return-optimisation exercise. The project does not add technical indicators, parameter sweeps for maximum Sharpe, or a complex backtesting framework because those additions would increase the risk of overfitting without answering the stated research question.

## Incorrect / risky AI suggestions to watch for

AI-generated quantitative code can silently introduce look-ahead bias, especially by entering at the same close used to define an event. The implementation therefore uses the **next trading day's open**. Another risk is interpreting a statistically significant mean as proof of a tradable edge; the project explicitly compares against a normal-return baseline and includes costs, slippage and out-of-sample validation.

## What I learned

The main lesson is that a backtest is evidence, not an explanation. The important work is defining the event before seeing the result, choosing an executable entry, selecting a meaningful baseline, checking uncertainty and trying to break the conclusion. A negative or unstable result would still be useful because it tells us the evidence is not strong enough for the original hypothesis.
