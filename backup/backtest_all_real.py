from pathlib import Path
import glob, pandas as pd
from backtest_engine import load_csv, run
ROOT=Path(".")
REPORTS=ROOT/"reports"
REPORTS.mkdir(exist_ok=True)
ALL= [p.stem.replace("_M15","") for p in Path("data").glob("*_M15.csv")]
print(f"=== JARVIS V10.6.1 REAL - {len(ALL)} ATIVOS ===")
res=[]
for sym in ALL:
    f=glob.glob(f"data/{sym}_M15.csv")[0]
    df=load_csv(f)
    m,t=run(df,sym,relaxed=False)
    res.append({**m,"symbol":sym})
    print(f"[OK] {sym} WR {m['win_rate_pct']:.1f}% PF {m['profit_factor']:.2f} PnL {m['net_pnl']:.2f} Trades {m['trades']}")
df=pd.DataFrame(res).sort_values("profit_factor",ascending=False)
df.to_csv(REPORTS/"backtest_REAL_51.csv",index=False)
try: df.to_excel(REPORTS/"backtest_REAL_51.xlsx",index=False)
except: pass
print(f"\nTOTAL PnL REAL: ${df['net_pnl'].sum():.2f} | Medio WR {df['win_rate_pct'].mean():.1f}% | Lucrativos {len(df[df.net_pnl>0])}/{len(df)}")
