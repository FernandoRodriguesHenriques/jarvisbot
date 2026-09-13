from pathlib import Path
import argparse, json, math
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
CFG=json.loads((ROOT/"config.json").read_text(encoding="utf-8"))
REPORTS=ROOT/"reports"

def load_csv(path):
    df=pd.read_csv(path)
    aliases={"time":"timestamp","datetime":"timestamp","date":"timestamp",
             "tick_volume":"volume","real_volume":"volume","vol":"volume"}
    df=df.rename(columns={c:aliases.get(str(c).lower(),str(c).lower()) for c in df.columns})
    req=["timestamp","open","high","low","close"]
    miss=[x for x in req if x not in df.columns]
    if miss: raise ValueError(f"CSV sem colunas: {miss}")
    df["timestamp"]=pd.to_datetime(df["timestamp"],errors="coerce")
    for c in ["open","high","low","close","volume","spread"]:
        if c in df: df[c]=pd.to_numeric(df[c],errors="coerce")
    if "volume" not in df: df["volume"]=1.0
    if "spread" not in df: df["spread"]=np.nan
    return df.dropna(subset=req).sort_values("timestamp").drop_duplicates("timestamp").reset_index(drop=True)

def ema(s,p): return s.ewm(span=p,adjust=False).mean()

def atr(df,p):
    pc=df.close.shift(1)
    tr=pd.concat([df.high-df.low,(df.high-pc).abs(),(df.low-pc).abs()],axis=1).max(axis=1)
    return tr.rolling(p).mean()

def prepare(df):
    df=df.copy()
    df["ema9"]=ema(df.close,CFG["ema_fast"])
    df["ema21"]=ema(df.close,CFG["ema_mid"])
    df["ema50"]=ema(df.close,CFG["ema_slow"])
    df["atr"]=atr(df,CFG["atr_period"])
    df["vavg"]=df.volume.rolling(CFG["volume_period"]).mean()
    df["vr"]=df.volume/df.vavg.replace(0,np.nan)
    m=ema(df.close,CFG["macd_fast"])-ema(df.close,CFG["macd_slow"])
    s=m.ewm(span=CFG["macd_signal"],adjust=False).mean()
    df["mh"]=m-s
    df["mh_prev"]=df.mh.shift(1)
    return df

def pattern(r,p):
    rng=max(r.high-r.low,1e-12); body=abs(r.close-r.open)
    upper=r.high-max(r.open,r.close); lower=min(r.open,r.close)-r.low
    if lower>=body*2 and upper<=rng*.25 and r.close>r.open: return "HAMMER"
    if body/rng<=.10: return "DOJI"
    if body/rng>=.80: return "MARUBOZU"
    if r.close>r.open and p.close<p.open and r.open<=p.close and r.close>=p.open: return "ENGULFING_BULL"
    if r.close<r.open and p.close>p.open and r.open>=p.close and r.close<=p.open: return "ENGULFING_BEAR"
    return "NONE"

def context(df,i):
    if i<55:return "NONE"
    r=df.iloc[i]
    a=df.iloc[i-6:i].close.mean(); b=df.iloc[i-13:i-6].close.mean()
    if r.ema21>r.ema50 and a<b:return "4"
    if r.ema21<r.ema50 and a>b:return "8"
    return "NONE"

def htf(df,t,rule):
    x=df[df.timestamp<=t].set_index("timestamp").close.resample(rule).last().dropna()
    if len(x)<55:return "NEUTRAL"
    e21,e50=ema(x,21).iloc[-1],ema(x,50).iloc[-1]
    return "BULL" if e21>e50 else "BEAR" if e21<e50 else "NEUTRAL"

def htf_bias(df,t):
    a,b=htf(df,t,"1h"),htf(df,t,"4h")
    return a if a==b and a!="NEUTRAL" else "NEUTRAL"

def macd_state(r):
    if pd.isna(r.mh) or pd.isna(r.mh_prev):return "WEAK"
    if r.mh_prev<=0<r.mh:return "CROSS_UP"
    if r.mh_prev>=0>r.mh:return "CROSS_DOWN"
    return "BULL" if r.mh>0 else "BEAR" if r.mh<0 else "WEAK"

def ignition(r,d):
    rng=max(r.high-r.low,1e-12); body=abs(r.close-r.open)
    return (body/rng>=CFG["min_body_ratio"] and r.vr>=CFG["min_ignition_volume"]
            and body>=CFG["min_ignition_atr"]*r.atr
            and ((r.close>r.open) if d=="BUY" else (r.close<r.open)))

def signal(df,i):
    if i<60:return None
    r,p=df.iloc[i],df.iloc[i-1]
    c=context(df,i)
    if c not in ("4","8"):return None
    pat=pattern(r,p)
    d="BUY" if c=="4" and pat in ("HAMMER","ENGULFING_BULL","MARUBOZU") else None
    if c=="8" and pat in ("ENGULFING_BEAR","MARUBOZU"):d="SELL"
    if not d:return None
    h=htf_bias(df,r.timestamp); m=macd_state(r); ig=ignition(r,d)
    score=20
    score+=18 if (d=="BUY" and h=="BULL") or (d=="SELL" and h=="BEAR") else 0
    score+=14 if (d=="BUY" and m in ("CROSS_UP","BULL")) or (d=="SELL" and m in ("CROSS_DOWN","BEAR")) else -12
    score+=14 if ig else 0
    score+=10 if r.vr>=1.5 else 5 if r.vr>=1 else 0
    score+=8 if abs(r.close-r.ema21)<=max(r.atr,1e-12) else 3
    spread_ok=pd.isna(r.spread) or r.spread<=CFG["spread_limit"]
    score+=8 if spread_ok else -30
    if score<CFG["min_score"] or h=="NEUTRAL" or not spread_ok:return None
    if d=="BUY" and h!="BULL":return None
    if d=="SELL" and h!="BEAR":return None
    a=float(r.atr); entry=float(df.iloc[i+1].open) if i+1<len(df) else float(r.close)
    if d=="BUY":
        sl=float(df.iloc[max(0,i-20):i].low.min())-CFG["sl_atr_buffer"]*a
        tp=entry+CFG["default_rr"]*(entry-sl)
    else:
        sl=float(df.iloc[max(0,i-20):i].high.max())+CFG["sl_atr_buffer"]*a
        tp=entry-CFG["default_rr"]*(sl-entry)
    risk=abs(entry-sl)
    if risk<=0:return None
    return dict(direction=d,entry=entry,sl=sl,tp=tp,risk=risk,score=score,
                pattern=pat,context=c,htf=h,macd=m,ignition="YES" if ig else "NO",vr=float(r.vr),atr=a)

def run(df,symbol):
    df=prepare(df); equity=CFG["initial_equity"]; peak=equity; maxdd=0
    positions=[]; trades=[]; last_trade=-99999; daily={}
    for i in range(60,len(df)):
        r=df.iloc[i]; day=r.timestamp.date(); daily.setdefault(day,{"start":equity,"n":0})
        for pos in positions[:]:
            hit_sl=(r.low<=pos["sl"]) if pos["direction"]=="BUY" else (r.high>=pos["sl"])
            hit_tp=(r.high>=pos["tp"]) if pos["direction"]=="BUY" else (r.low<=pos["tp"])
            if hit_sl or hit_tp:
                ex=pos["sl"] if hit_sl else pos["tp"]
                rm=(ex-pos["entry"])/pos["risk"] if pos["direction"]=="BUY" else (pos["entry"]-ex)/pos["risk"]
                pnl=pos["risk_money"]*rm; equity+=pnl; positions.remove(pos)
                trades.append({**pos,"exit_time":str(r.timestamp),"exit":ex,"pnl":pnl,"R":rm,"result":"LOSS" if hit_sl else "WIN"})
                last_trade=i
        peak=max(peak,equity); maxdd=min(maxdd,(equity-peak)/peak)
        if daily[day]["n"]>=CFG["max_trades_per_day"] or equity-daily[day]["start"]<=-daily[day]["start"]*CFG["daily_stop_pct"]: continue
        if i-last_trade<CFG["cooldown_bars"] or len(positions)>=CFG["max_open_positions"]: continue
        if any(p["symbol"]==symbol for p in positions): continue
        s=signal(df,i)
        if not s:continue
        s["symbol"]=symbol;s["entry_time"]=str(df.iloc[i+1].timestamp);s["risk_money"]=equity*CFG["risk_per_trade"]
        positions.append(s);daily[day]["n"]+=1
    closed=pd.DataFrame(trades)
    wins=closed[closed.pnl>0] if not closed.empty else pd.DataFrame()
    losses=closed[closed.pnl<0] if not closed.empty else pd.DataFrame()
    gp=wins.pnl.sum() if not wins.empty else 0
    gl=abs(losses.pnl.sum()) if not losses.empty else 0
    metrics={"initial_equity":CFG["initial_equity"],"final_equity":equity,
             "net_pnl":equity-CFG["initial_equity"],"trades":len(closed),
             "wins":len(wins),"losses":len(losses),
             "win_rate_pct":len(wins)/len(closed)*100 if len(closed) else 0,
             "profit_factor":gp/gl if gl else None,
             "expectancy_R":closed.R.mean() if len(closed) else 0,
             "payoff":wins.pnl.mean()/abs(losses.pnl.mean()) if len(wins) and len(losses) else None,
             "max_drawdown_pct":maxdd*100}
    return metrics,closed

def sample(path,n=6000):
    rng=np.random.default_rng(7); ts=pd.date_range("2025-01-01",periods=n,freq="15min")
    c=3000+np.cumsum(rng.normal(0,3,n)); o=np.r_[c[0],c[:-1]]
    df=pd.DataFrame({"timestamp":ts,"open":o,"high":np.maximum(o,c)+rng.uniform(.2,4,n),
                     "low":np.minimum(o,c)-rng.uniform(.2,4,n),"close":c,
                     "volume":rng.integers(500,2500,n),"spread":rng.integers(15,60,n)})
    path.parent.mkdir(parents=True,exist_ok=True);df.to_csv(path,index=False)

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--csv");ap.add_argument("--symbol",default="XAUUSDm");ap.add_argument("--generate-sample",action="store_true")
    a=ap.parse_args()
    if a.generate_sample: sample(ROOT/"data/sample_M15.csv"); print("Sample criado."); raise SystemExit
    if not a.csv: ap.error("Use --csv arquivo.csv ou --generate-sample")
    m,t=run(load_csv(a.csv),a.symbol); REPORTS.mkdir(exist_ok=True)
    (REPORTS/f"backtest_{a.symbol}.json").write_text(json.dumps(m,indent=2,default=str),encoding="utf-8")
    t.to_csv(REPORTS/f"backtest_{a.symbol}_trades.csv",index=False)
    pd.DataFrame([m]).to_excel(REPORTS/f"backtest_{a.symbol}.xlsx",index=False)
    print("\n=== JARVIS BACKTEST ===")
    for k,v in m.items(): print(f"{k}: {v}")
    print(f"\nRelatórios: {REPORTS}")
