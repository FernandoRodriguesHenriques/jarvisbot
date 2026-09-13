import MetaTrader5 as mt5, pandas as pd, json
from pathlib import Path
from datetime import datetime

ATIVOS = ["CADJPYm","NZDCADm","GBPNZDm","GBPCADm","CADCHFm","NZDJPYm","AUDCADm","EURAUDm","HK50m"]
CONFIG = json.loads(Path("config_por_ativo.json").read_text(encoding="utf-8"))

# 1 ANO = 35.040 candles M15
QTD_CANDLES = 35040
Path("data_1ano").mkdir(exist_ok=True)

if not mt5.initialize():
    print("Abra o MT5!")
    exit()

for s in ATIVOS: mt5.symbol_select(s, True)

total_ano = 0
print(f"=== BACKTEST 1 ANO - {QTD_CANDLES} CANDLES POR ATIVO ===\n")

for sym in ATIVOS:
    print(f"Baixando {sym} 1 ano...")
    rates = mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_M15, 0, QTD_CANDLES)
    if rates is None or len(rates) < 1000:
        print(f"{sym} -> FALHOU ou sem historico de 1 ano")
        continue

    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.to_csv(f"data_1ano/{sym}_M15_1ANO.csv", index=False)

    # BACKTEST SIMPLES COM SUA ESTRATEGIA RR 1.5
    df['ema9'] = df['close'].ewm(9).mean()
    df['ema21'] = df['close'].ewm(21).mean()
    df['ema50'] = df['close'].ewm(50).mean()

    cfg = CONFIG.get(sym, {"min_score":60,"default_rr":1.5})
    rr = cfg['default_rr']

    trades = 0
    wins = 0
    pnl = 0

    for i in range(50, len(df)-20):
        # SCORE
        score = 0
        if df.ema9.iloc[i] > df.ema21.iloc[i] > df.ema50.iloc[i]: score+=40
        if df.ema9.iloc[i] < df.ema21.iloc[i] < df.ema50.iloc[i]: score+=40
        body = abs(df.close.iloc[i] - df.open.iloc[i])
        rng = df.high.iloc[i] - df.low.iloc[i]
        if rng>0 and body/rng>0.4: score+=20

        if score >= cfg['min_score']:
            trades+=1
            # Simula saida com RR
            entry = df.close.iloc[i]
            # Se for compra
            if df.ema9.iloc[i] > df.ema21.iloc[i]:
                tp = entry + (rng * rr if rng>0 else entry*0.001)
                sl = entry - (rng if rng>0 else entry*0.001)
                # verifica proximos candles
                future = df.iloc[i+1:i+20]
                hit_tp = (future.high >= tp).any()
                if hit_tp:
                    wins+=1
                    pnl+= 10 * rr
                else:
                    pnl-=10
            else:
                tp = entry - (rng * rr if rng>0 else entry*0.001)
                sl = entry + (rng if rng>0 else entry*0.001)
                future = df.iloc[i+1:i+20]
                hit_tp = (future.low <= tp).any()
                if hit_tp:
                    wins+=1
                    pnl+= 10 * rr
                else:
                    pnl-=10

    wr = (wins/trades*100) if trades>0 else 0
    total_ano+=pnl
    print(f"{sym}: {trades} trades | WR {wr:.1f}% | PnL ${pnl:.2f} | {df.time.iloc[0].date()} ate {df.time.iloc[-1].date()}\n")

print(f"============================")
print(f"TOTAL 1 ANO - 9 ATIVOS: ${total_ano:.2f}")
print(f"MEDIA MENSAL: ${total_ano/12:.2f}")
if total_ano>0:
    print("ESTRATEGIA APROVADA ✅ LUCRATIVA NO ULTIMO ANO")
else:
    print("ESTRATEGIA REPROVADA ❌")

mt5.shutdown()
