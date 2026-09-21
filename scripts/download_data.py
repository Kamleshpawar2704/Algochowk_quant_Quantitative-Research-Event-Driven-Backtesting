from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data import download_nifty

out = Path(__file__).resolve().parents[1] / "data" / "nifty50_daily.csv"
out.parent.mkdir(exist_ok=True)
df = download_nifty("2010-01-01")
df.to_csv(out, index=False)
print(f"Saved {len(df):,} rows to {out}")
print(f"Coverage: {df.Date.min().date()} → {df.Date.max().date()}")
