import json, MetaTrader5 as mt5, pandas as pd
from pathlib import Path

ATIVOS = ["CADJPYm","NZDCADm","GBPNZDm","GBPCADm","CADCHFm","NZDJPYm","AUDCADm","EURAUDm","HK50m"]
CONFIG = json.loads(Path("config_por_ativo.json").read_text(encoding="utf-8"))

# OTIMIZA - abaixa min_score dos que deram 0 trade
ZERADOS = ["CADJPYm","GBPNZDm","GBPCADm","NZDJPYm","AUDCADm","HK50m"]
for sym in ZERADOS:
    if sym in CONFIG:
        CONFIG[sym]['min_score'] = 40 # era 60, agora 40
        CONFIG[sym]['default_rr'] = 1.5

Path("config_9_otimizado.json").write_text(json.dumps(CONFIG, indent=2), encoding="utf-8")
print("=== CONFIG OTIMIZADA - 9 ATIVOS ===")
for k in ATIVOS: print(f"{k} -> min_score {CONFIG[k]['min_score']} RR {CONFIG[k]['default_rr']}")

QTD=35040
if not mt5.initialize():
    print("Abre o MT5!")
    exit()
for s in ATIVOS: mt5.symbol_select(s, True)

total=0
print("\n=== RE-BACKTEST 1 ANO COM CONFIG OTIMIZADA ===\n")
for sym in ATIVOS:
    rates = mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_M15, 0, QTD)
    if rates is None: continue
    df = pd.DataFrame(rates)
    df['time']=pd.to_datetime(df['time'], unit='s')
    df['ema9']=df['close'].ewm(9).mean()
    df['ema21']=df['close'].ewm(21).mean()
    df['ema50']=df['close'].ewm(50).mean()

    cfg=CONFIG[sym]
    trades=wins=pnl=0
    for i in range(50, len(df)-20):
        score=0
        if df.ema9.iloc[i] > df.ema21.iloc[i] > df.ema50.iloc[i]: score+=40
        if df.ema9.iloc[i] < df.ema21.iloc[i] < df.ema50.iloc[i]: score+=40
        body=abs(df.close.iloc[i]-df.open.iloc[i])
        rng=df.high.iloc[i]-df.low.iloc[i]
        if rng>0 and body/rng>0.3: score+=20 # abaixei de 0.4 pra 0.3

        if score >= cfg['min_score']:
            trades+=1
            entry=df.close.iloc[i]
            # TP/SL
            is_buy = df.ema9.iloc[i] > df.ema21.iloc[i]
            future=df.iloc[i+1:i+20]
            if is_buy:
                tp=entry+(rng*cfg['default_rr'] if rng>0 else entry*0.001)
                if (future.high>=tp).any():
                    wins+=1
                    pnl+=10*cfg['default_rr']
                else: pnl-=10
            else:
                tp=entry-(rng*cfg['default_rr'] if rng>0 else entry*0.001)
                if (future.low<=tp).any():
                    wins+=1
                    pnl+=10*cfg['default_rr']
                else: pnl-=10

    wr=(wins/trades*100) if trades>0 else 0
    total+=pnl
    status="✅" if pnl>0 else "❌"
    print(f"{status} {sym}: {trades} trades | WR {wr:.1f}% | PnL ${pnl:.2f}")

print(f"\n============================")
print(f"TOTAL 1 ANO - 9 ATIVOS OTIMIZADOS: ${total:.2f}")
print(f"MEDIA MENSAL: ${total/12:.2f}")
mt5.shutdown()
