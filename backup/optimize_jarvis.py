import pandas as pd, itertools
from pathlib import Path
from backtest_engine import load_csv, run
import json

CFG=json.loads(Path("config.json").read_text(encoding="utf-8"))
DATA=Path("data")
REPORTS=Path("reports")
REPORTS.mkdir(exist_ok=True)

scores=[55,60,65]
rrs=[1.5,2.0,2.5]
spreads=[60, 100, 500] # 500 pra crypto

ALL=list(DATA.glob("*_M15.csv"))
best=[]

for file in ALL:
    sym=file.stem.replace("_M15","")
    df=load_csv(str(file))
    best_pf=0; best_cfg=None; best_m=None
    for sc,rr,sp in itertools.product(scores,rrs,spreads):
        CFG["min_score"]=sc; CFG["default_rr"]=rr; CFG["spread_limit"]=sp
        Path("config.json").write_text(json.dumps(CFG,indent=2))
        m,_=run(df,sym,relaxed=False)
        if m["trades"]>20 and m["profit_factor"]>best_pf:
            best_pf=m["profit_factor"]; best_cfg=(sc,rr,sp); best_m=m
    if best_cfg:
        best.append({"symbol":sym,"best_score":best_cfg[0],"best_rr":best_cfg[1],"best_spread":best_cfg[2],**best_m})
        print(f"[BEST] {sym} -> Score {best_cfg[0]} RR {best_cfg[1]} Spread {best_cfg[2]} => PF {best_m['profit_factor']:.2f} PnL {best_m['net_pnl']:.2f} Trades {best_m['trades']}")

df_best=pd.DataFrame(best).sort_values("profit_factor",ascending=False)
df_best.to_csv(REPORTS/"jarvis_otimizado.csv",index=False)
df_best.to_excel(REPORTS/"jarvis_otimizado.xlsx",index=False)
print(f"\n=== OTIMIZADO SALVO: {REPORTS}/jarvis_otimizado.xlsx ===")
print(f"Lucrativos agora: {len(df_best[df_best.net_pnl>0])}/{len(df_best)} | PnL Total: ${df_best.net_pnl.sum():.2f}")
