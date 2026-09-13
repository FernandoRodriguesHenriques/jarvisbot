import MetaTrader5 as mt5, time, pandas as pd
from pathlib import Path
from datetime import datetime

ATIVOS = ["CADJPYm","NZDCADm","GBPNZDm","GBPCADm","CADCHFm","NZDJPYm","AUDCADm","EURAUDm","HK50m"]

if not mt5.initialize():
    print("Abra o MT5!")
    exit()

for s in ATIVOS: mt5.symbol_select(s, True)

print("=== JARVIS FINAL 9 - COLETOR DE HISTORICO AO VIVO ===")
print("Ele NAO opera, so vai salvando historico a cada 15min")
print("Pode deixar minimizado, nao atrapalha nada\n")

try:
    while True:
        for sym in ATIVOS:
            rates = mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_M15, 0, 1)
            if rates is None: continue
            # Append no csv
            df_new = pd.DataFrame(rates)
            df_new['time'] = pd.to_datetime(df_new['time'], unit='s')
            path = f"data/{sym}_M15.csv"
            if Path(path).exists():
                df_old = pd.read_csv(path)
                # so adiciona se for candle novo
                if df_new['time'].iloc[0].isoformat() not in df_old['time'].astype(str).values:
                    df_new.to_csv(path, mode='a', header=False, index=False)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] {sym} -> novo candle salvo {df_new['time'].iloc[0]}")
        time.sleep(60)
except KeyboardInterrupt:
    mt5.shutdown()
