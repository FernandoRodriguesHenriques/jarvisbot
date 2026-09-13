import json
from pathlib import Path

# Esses sao os 12 que seu proprio otimizador achou LUCRATIVO no print
config = {
  "ADAUSDm": {"min_score": 55, "default_rr": 1.5, "spread_limit": 500},
  "DOGEUSDm": {"min_score": 65, "default_rr": 1.5, "spread_limit": 500},
  "CADJPYm": {"min_score": 65, "default_rr": 1.5, "spread_limit": 100},
  "NZDCADm": {"min_score": 55, "default_rr": 1.5, "spread_limit": 60},
  "GBPNZDm": {"min_score": 65, "default_rr": 1.5, "spread_limit": 60},
  "GBPCADm": {"min_score": 65, "default_rr": 1.5, "spread_limit": 60},
  "CADCHFm": {"min_score": 55, "default_rr": 1.5, "spread_limit": 60},
  "NZDJPYm": {"min_score": 65, "default_rr": 1.5, "spread_limit": 100},
  "LINKUSDm": {"min_score": 65, "default_rr": 1.5, "spread_limit": 100},
  "AUDCADm": {"min_score": 65, "default_rr": 1.5, "spread_limit": 100},
  "EURAUDm": {"min_score": 55, "default_rr": 1.5, "spread_limit": 500},
  "HK50m": {"min_score": 65, "default_rr": 1.5, "spread_limit": 500}
}

Path("config_por_ativo.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
Path("reports").mkdir(exist_ok=True)
Path("reports/jarvis_LUCRATIVOS_12.txt").write_text(json.dumps(config, indent=2), encoding="utf-8")

print("=== PORTFOLIO FINAL 12 ATIVOS LUCRATIVOS GERADO ===")
print(f"PnL Total estimado: +$20.967 (soma do seu print)")
print("Arquivo: config_por_ativo.json")
for k,v in config.items():
    print(f"{k}: Score {v['min_score']} RR {v['default_rr']} Spread {v['spread_limit']}")
