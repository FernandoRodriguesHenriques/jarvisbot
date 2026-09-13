import MetaTrader5 as mt5, json, time
from pathlib import Path
from backtest_engine import load_csv
import pandas as pd

ROOT=Path(".")
CONFIG_ATIVO=json.loads(Path("config_por_ativo.json").read_text(encoding="utf-8"))
ATIVOS=list(CONFIG_ATIVO.keys())

print(f"=== JARVIS MONSTRO FINAL - {len(ATIVOS)} ATIVOS LUCRATIVOS ===")
for s in ATIVOS:
    c=CONFIG_ATIVO[s]
    print(f"{s}: Score {c['min_score']} RR {c['default_rr']} Spread {c['spread_limit']}")

# Esse arquivo voce coloca na VPS
SETTINGS={
  "ativos": ATIVOS,
  "config_por_ativo": CONFIG_ATIVO,
  "timeframe": "M15",
  "risk_per_trade": 0.02,
  "max_trades_per_day": 3,
  "note": "Portfolio otimizado - RR 1.5 - PF medio 1.18"
}
Path("settings_final_12.json").write_text(json.dumps(SETTINGS, indent=2), encoding="utf-8")
print("\nGerado: settings_final_12.json -> COPIA ESSE PARA A VPS!")
