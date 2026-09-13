import MetaTrader5 as mt5
import pandas as pd
from pathlib import Path

ATIVOS = ["ADAUSDm","DOGEUSDm","CADJPYm","NZDCADm","GBPNZDm","GBPCADm","CADCHFm","NZDJPYm","LINKUSDm","AUDCADm","EURAUDm","HK50m"]
Path("data").mkdir(exist_ok=True)

if not mt5.initialize():
    print("Abre o MT5 e loga na conta!")
    exit()

print("=== GERANDO HISTORICO PARA O JARVIS - 12 ATIVOS ===")
for sym in ATIVOS:
    mt5.symbol_select(sym, True)
    # FIX: usa copy_rates_from_pos pra versao antiga
    rates = mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_M15, 0, 10000)
    if rates is None or len(rates)==0:
        print(f"{sym} -> sem dados")
        continue
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.to_csv(f"data/{sym}_M15.csv", index=False)
    print(f"{sym} -> {len(df)} candles | {df.time.iloc[0]} ate {df.time.iloc[-1]}")

mt5.shutdown()
print("\nPronto! Historico gerado em C:\\jarvis\\data\\")
