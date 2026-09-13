import pandas as pd, json
from pathlib import Path
df=pd.read_csv("reports/jarvis_otimizado.csv")
lucrativos=df[(df.profit_factor>1.0) & (df.net_pnl>0)].sort_values("profit_factor", ascending=False)
lucrativos.to_csv("reports/jarvis_LUCRATIVOS.csv", index=False)
try: lucrativos.to_excel("reports/jarvis_LUCRATIVOS.xlsx", index=False)
except: pass

# Gera o config_por_ativo.json que o bot vai usar
config={}
for _,r in lucrativos.iterrows():
    config[r.symbol]={"min_score":int(r.best_score),"default_rr":float(r.best_rr),"spread_limit":int(r.best_spread)}

Path("config_por_ativo.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
print(f"PORTFOLIO FINAL: {len(lucrativos)} ativos | PnL Total: ${lucrativos.net_pnl.sum():.2f}")
print("Arquivo gerado: config_por_ativo.json")
print(lucrativos[["symbol","profit_factor","net_pnl","best_score","best_rr","best_spread"]].to_string())
