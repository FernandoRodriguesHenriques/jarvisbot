import pandas as pd, numpy as np, json
from pathlib import Path

def load_csv(path):
    df=pd.read_csv(path)
    df.columns=[str(c).lower() for c in df.columns]
    m={"time":"timestamp","datetime":"timestamp","date":"timestamp","tick_volume":"volume","real_volume":"volume","vol":"volume"}
    df=df.rename(columns={k:m.get(k,k) for k in df.columns})
    df["timestamp"]=pd.to_datetime(df["timestamp"],errors="coerce")
    for c in ["open","high","low","close","volume","spread"]:
        if c in df: df[c]=pd.to_numeric(df[c],errors="coerce")
    if "volume" not in df: df["volume"]=1.0
    if "spread" not in df: df["spread"]=20
    return df.dropna(subset=["timestamp","open","high","low","close"]).sort_values("timestamp").reset_index(drop=True)

def ema(s,p): return s.ewm(span=p,adjust=False).mean()
def rsi(s,p=14):
    d=s.diff(); g=d.clip(lower=0); l=-d.clip(upper=0)
    rs=g.ewm(alpha=1/p,adjust=False).mean()/(l.ewm(alpha=1/p,adjust=False).mean()+1e-9)
    return 100-(100/(1+rs))
def atr(df,p):
    pc=df.close.shift(1)
    tr=pd.concat([df.high-df.low,(df.high-pc).abs(),(df.low-pc).abs()],axis=1).max(axis=1)
    return tr.rolling(p).mean()

def run(df,symbol,relaxed=False):
    cfg_path=Path("config.json")
    CFG=json.loads(cfg_path.read_text(encoding="utf-8")) if cfg_path.exists() else {}
    def gv(k,d): return CFG.get(k,d)
    min_score = 45 if relaxed else gv("min_score",65)
    rr = gv("default_rr",2.0)
    spread_limit = 80 if relaxed else gv("spread_limit",50)
    risk_per = gv("risk_per_trade",0.02)
    max_day = gv("max_trades_per_day",5)

    df=df.copy()
    df["ema9"]=ema(df.close,gv("ema_fast",9)); df["ema21"]=ema(df.close,gv("ema_mid",21)); df["ema50"]=ema(df.close,gv("ema_slow",50))
    df["atr"]=atr(df,gv("atr_period",14)); df["rsi"]=rsi(df.close,14)
    df["vol_ma"]=df.volume.rolling(gv("volume_period",20)).mean()
    df["macd"] = ema(df.close,12)-ema(df.close,26)
    df["macd_sig"]=ema(df["macd"],9)

    equity=gv("initial_equity",10000); peak=equity; maxdd=0; trades=[]; day_count={}

    for i in range(80,len(df)):
        r=df.iloc[i]
        date_key=str(r.timestamp.date())
        if day_count.get(date_key,0)>=max_day: continue
        if r.spread>spread_limit: continue
        if pd.isna(r.atr) or r.atr<=0: continue
        # SCORE
        score=0
        if r.ema9>r.ema21>r.ema50: score+=30
        elif r.ema9<r.ema21<r.ema50: score+=30
        else: continue
        if r.volume > (r.vol_ma*1.2 if not pd.isna(r.vol_ma) else 0): score+=20
        if r.macd>r.macd_sig: score+=15 if r.ema9>r.ema21 else 0
        else: score+=15 if r.ema9<r.ema21 else 0
        if 30<r.rsi<70: score+=15
        body=abs(r.close-r.open); rng=r.high-r.low
        if rng>0 and body/rng>0.4: score+=20
        if score<min_score: continue

        d="BUY" if r.ema9>r.ema21 and r.close>r.open else "SELL" if r.ema9<r.ema21 and r.close<r.open else None
        if not d: continue

        entry=float(r.close); a=float(r.atr)
        look=df.iloc[max(0,i-20):i]
        if d=="BUY":
            sl=float(look.low.min())-0.3*a; risk=entry-sl; tp=entry+rr*risk
        else:
            sl=float(look.high.max())+0.3*a; risk=sl-entry; tp=entry-rr*risk
        if risk<=0: continue

        future=df.iloc[i+1:i+50]
        win=False; loss=False; exit_price=entry
        for _,fr in future.iterrows():
            if d=="BUY":
                if fr.high>=tp: win=True; exit_price=tp; break
                if fr.low<=sl: loss=True; exit_price=sl; break
            else:
                if fr.low<=tp: win=True; exit_price=tp; break
                if fr.high>=sl: loss=True; exit_price=sl; break
        if not (win or loss): continue
        pnl = equity*risk_per*rr if win else -equity*risk_per
        equity+=pnl; peak=max(peak,equity); dd=(equity-peak)/peak; maxdd=min(maxdd,dd)
        day_count[date_key]=day_count.get(date_key,0)+1
        trades.append({"pnl":pnl,"R":rr if win else -1,"result":"WIN" if win else "LOSS","entry":entry,"exit":exit_price,"type":d,"score":score,"timestamp":r.timestamp})

    closed=pd.DataFrame(trades)
    if closed.empty:
        return {"win_rate_pct":0,"profit_factor":0,"net_pnl":0,"trades":0,"wins":0,"losses":0,"expectancy_R":0,"max_drawdown_pct":0,"final_equity":equity,"initial_equity":gv("initial_equity",10000)}, closed
    wins=closed[closed.pnl>0]; losses=closed[closed.pnl<0]
    gp=wins.pnl.sum(); gl=abs(losses.pnl.sum())
    return {"win_rate_pct":len(wins)/len(closed)*100,"profit_factor":gp/gl if gl else 0,"net_pnl":equity-gv("initial_equity",10000),"trades":len(closed),"wins":len(wins),"losses":len(losses),"expectancy_R":closed.R.mean(),"max_drawdown_pct":maxdd*100,"final_equity":equity,"initial_equity":gv("initial_equity",10000)}, closed
