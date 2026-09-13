import MetaTrader5 as mt5
import pandas as pd
from pathlib import Path
ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
ALL_ASSETS = ["EURUSDm","GBPUSDm","USDJPYm","AUDUSDm","NZDUSDm","USDCADm","USDCHFm","EURJPYm","GBPJPYm","EURAUDm","GBPCHFm","AUDJPYm","AUDCADm","AUDCHFm","CADCHFm","CADJPYm","CHFJPYm","EURGBPm","EURCHFm","EURCADm","EURNZDm","GBPAUDm","GBPCADm","GBPNZDm","AUDNZDm","NZDCADm","NZDCHFm","NZDJPYm","EURUSDa","GBPUSDa","USDJPYa","US30m","US500m","NAS100m","UK100m","GER40m","FR40m","STOXX50m","JP225m","AUS200m","HK50m","IN50m","USOILm","BTCUSDm","ETHUSDm","SOLUSDm","BNBUSDm","XRPUSDm","DOGEUSDm","LTCUSDm","LINKUSDm","ADAUSDm","MATICUSDm","BCHUSDm","DOTUSDm","UNIUSDm","AVAXUSDm","ATOMUSDm","ETCUSDm","XLMUSDm","TRXm","NEARUSDm","APTUSDm","ARBUSm","OPUSDm","INJUSDm","RNDRUSDm","STXUSDm","TIAUSDm","SEIUSDm"]
print("=== JARVIS FETCH 71 ATIVOS MT5 ===")
if not mt5.initialize():
    print("ERRO: Abre o MT5 antes!")
    print(mt5.last_error())
    exit()
print("MT5 conectado OK")
N_CANDLES = 6000
TIMEFRAME = mt5.TIMEFRAME_M15
baixados=0
for symbol in ALL_ASSETS:
    info=mt5.symbol_info(symbol)
    if info is None:
        print(f"[SKIP] {symbol}")
        continue
    mt5.symbol_select(symbol, True)
    rates = mt5.copy_rates_from_pos(symbol, TIMEFRAME, 0, N_CANDLES)
    if rates is None or len(rates)<100:
        print(f"[FALHA] {symbol}")
        continue
    df=pd.DataFrame(rates)
    df['time']=pd.to_datetime(df['time'], unit='s')
    df.rename(columns={'time':'timestamp','tick_volume':'volume'}, inplace=True)
    if 'spread' not in df.columns:
        df['spread']=info.spread if hasattr(info,'spread') else 20
    out=DATA / f"{symbol}_M15.csv"
    df[['timestamp','open','high','low','close','volume','spread']].to_csv(out, index=False)
    print(f"[OK] {symbol} -> {len(df)}")
    baixados+=1
mt5.shutdown()
print(f"FINALIZADO: {baixados} baixados em {DATA}")
