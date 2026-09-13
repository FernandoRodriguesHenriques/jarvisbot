import json, sys
from pathlib import Path
from backtest_engine import load_csv, run_backtest

ATIVOS_BONS = ["CADJPYm","NZDCADm","GBPNZDm","GBPCADm","CADCHFm","NZDJPYm","AUDCADm","EURAUDm","HK50m"]
CONFIG = json.loads(Path("config_por_ativo.json").read_text(encoding="utf-8"))

total_profit=0
print("=== BACKTEST COM HISTORICO NOVO - 9 ATIVOS ===")
for sym in ATIVOS_BONS:
    df = load_csv(f"data/{sym}_M15.csv")
    if df is None: continue
    cfg = CONFIG.get(sym)
    trades = run_backtest(df, min_score=cfg['min_score'], rr=cfg['default_rr'])
    profit = sum([t['pnl'] for t in trades])
    total_profit+=profit
    print(f"{sym}: {len(trades)} trades | ${profit:.2f}")

print(f"\nTOTAL 9 ATIVOS (historico novo): ${total_profit:.2f}")
