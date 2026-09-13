from pathlib import Path
import json, glob
import pandas as pd
import numpy as np
ROOT=Path(__file__).resolve().parent
REPORTS=ROOT/"reports"
DATA=ROOT/"data"
REPORTS.mkdir(exist_ok=True)

ALL_ASSETS = ["EURUSDm","GBPUSDm","USDJPYm","AUDUSDm","NZDUSDm","USDCADm","USDCHFm","EURJPYm","GBPJPYm","EURAUDm","GBPCHFm","AUDJPYm","AUDCADm","AUDCHFm","CADCHFm","CADJPYm","CHFJPYm","EURGBPm","EURCHFm","EURCADm","EURNZDm","GBPAUDm","GBPCADm","GBPNZDm","AUDNZDm","NZDCADm","NZDCHFm","NZDJPYm","EURUSDa","GBPUSDa","USDJPYa","US30m","US500m","NAS100m","UK100m","GER40m","FR40m","STOXX50m","JP225m","AUS200m","HK50m","IN50m","USOILm","BTCUSDm","ETHUSDm","SOLUSDm","BNBUSDm","XRPUSDm","DOGEUSDm","LTCUSDm","LINKUSDm","ADAUSDm","MATICUSDm","BCHUSDm","DOTUSDm","UNIUSDm","AVAXUSDm","ATOMUSDm","ETCUSDm","XLMUSDm","TRXm","NEARUSDm","APTUSDm","ARBUSm","OPUSDm","INJUSDm","RNDRUSDm","STXUSDm","TIAUSDm","SEIUSDm"]

CFG=json.loads((ROOT/"config.json").read_text(encoding="utf-8")) if (ROOT/"config.json").exists() else {"initial_equity":10000,"risk_per_trade":0.02,"max_trades_per_day":5,"daily_stop_pct":0.05,"cooldown_bars":3,"max_open_positions":1,"ema_fast":9,"ema_mid":21,"ema_slow":50,"atr_period":14,"volume_period":20,"macd_fast":12,"macd_slow":26,"macd_signal":9,"min_score":65,"spread_limit":50,"default_rr":2.0,"sl_atr_buffer":0.3}

def load_csv(path):
    df=pd.read_csv(path)
    df.columns=[str(c).lower() for c in df.columns]
    rename={"time":"timestamp","datetime":"timestamp","date":"timestamp","tick_volume":"volume","real_volume":"volume","vol":"volume"}
    df=df.rename(columns={k:rename.get(k,k) for k in df.columns})
    df["timestamp"]=pd.to_datetime(df["timestamp"],errors="coerce")
    for c in ["open","high","low","close","volume","spread"]:
        if c in df: df[c]=pd.to_numeric(df[c],errors="coerce")
    if "volume" not in df: df["volume"]=1.0
    if "spread" not in df: df["spread"]=20
    return df.dropna(subset=["timestamp","open","high","low","close"]).sort_values("timestamp").reset_index(drop=True)

def ema(s,p): return s.ewm(span=p,adjust=False).mean()
def atr(df,p):
    pc=df.close.shift(1)
    tr=pd.concat([df.high-df.low,(df.high-pc).abs(),(df.low-pc).abs()],axis=1).max(axis=1)
    return tr.rolling(p).mean()

def run_simple(df,symbol):
    df=df.copy()
    df["ema9"]=ema(df.close,9); df["ema21"]=ema(df.close,21); df["ema50"]=ema(df.close,50)
    df["atr"]=atr(df,14)
    equity=CFG["initial_equity"]; peak=equity; maxdd=0; trades=[]
    for i in range(60,len(df)):
        r=df.iloc[i]; p=df.iloc[i-1]
        # filtro simples tendencia
        bull=r.ema9>r.ema21>r.ema50
        bear=r.ema9<r.ema21<r.ema50
        if not (bull or bear): continue
        body=abs(r.close-r.open); rng=max(r.high-r.low,1e-6)
        if body/rng<0.3: continue
        d="BUY" if bull and r.close>r.open else "SELL" if bear and r.close<r.open else None
        if not d: continue
        entry=float(r.close); a=float(r.atr) if not pd.isna(r.atr) else 1.0
        if d=="BUY":
            sl=float(df.iloc[max(0,i-15):i].low.min())-0.3*a; risk=entry-sl; tp=entry+2*risk
        else:
            sl=float(df.iloc[max(0,i-15):i].high.max())+0.3*a; risk=sl-entry; tp=entry-2*risk
        if risk<=0: continue
        # simula saida
        future=df.iloc[i+1:i+20]
        win=False; loss=False
        for _,fr in future.iterrows():
            if d=="BUY":
                if fr.high>=tp: win=True; break
                if fr.low<=sl: loss=True; break
            else:
                if fr.low<=tp: win=True; break
                if fr.high>=sl: loss=True; break
        if win: pnl=equity*0.02*2; result="WIN"; Rm=2.0
        elif loss: pnl=-equity*0.02; result="LOSS"; Rm=-1.0
        else: continue
        equity+=pnl; peak=max(peak,equity); maxdd=min(maxdd,(equity-peak)/peak)
        trades.append({"pnl":pnl,"R":Rm,"result":result})
    closed=pd.DataFrame(trades)
    wins=closed[closed.pnl>0] if not closed.empty else pd.DataFrame()
    losses=closed[closed.pnl<0] if not closed.empty else pd.DataFrame()
    gp=wins.pnl.sum() if not wins.empty else 0
    gl=abs(losses.pnl.sum()) if not losses.empty else 0
    return {"symbol":symbol,"initial_equity":CFG["initial_equity"],"final_equity":equity,"net_pnl":equity-CFG["initial_equity"],"trades":len(closed),"wins":len(wins),"losses":len(losses),"win_rate_pct":len(wins)/len(closed)*100 if len(closed) else 0,"profit_factor":gp/gl if gl else None,"expectancy_R":closed.R.mean() if len(closed) else 0,"max_drawdown_pct":maxdd*100}

print("=== JARVIS MULTI 71 - VERSAO SIMPLES ===")
results=[]
for sym in ALL_ASSETS:
    files=glob.glob(f"data/{sym}*.csv")+glob.glob(f"data/*{sym}*.csv")
    if not files:
        print(f"[SKIP] {sym}")
        continue
    try:
        df=load_csv(files[0])
        m=run_simple(df,sym)
        results.append(m)
        print(f"[OK] {sym} WR {m['win_rate_pct']:.1f}% PF {m.get('profit_factor') or 0:.2f} PnL {m['net_pnl']:.2f} Trades {m['trades']}")
    except Exception as e:
        print(f"[ERRO] {sym}: {e}")

if results:
    df_res=pd.DataFrame(results).sort_values("profit_factor", ascending=False, na_position='last')
    df_res.to_csv(REPORTS/"backtest_multi_71.csv", index=False)
    df_res.to_json(REPORTS/"backtest_multi_71.json", orient="records", indent=2)
    try: df_res.to_excel(REPORTS/"backtest_multi_71.xlsx", index=False)
    except: pass
    total=df_res["net_pnl"].sum()
    avg_wr=df_res["win_rate_pct"].mean()
    lucrativos=len(df_res[df_res["net_pnl"]>0])
    print("")
    print("==================================================")
    print(f"Portfolio: {len(df_res)} ativos | PnL Total: ${total:.2f} | WR Medio: {avg_wr:.1f}% | Lucrativos: {lucrativos}/{len(df_res)}")
    print("==================================================")
else:
    print("Nenhum CSV encontrado em data/")
