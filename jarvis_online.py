import pandas as pd, yfinance as yf
from flask import Flask, jsonify
app = Flask(__name__)

ATIVOS = ["EURUSD=X","GBPUSD=X","USDJPY=X","XAUUSD=X","BTC-USD","ETH-USD","^GSPC","^DJI"]

def calc_score(symbol):
    try:
        df = yf.download(symbol, period="60d", interval="15m", progress=False)
        if len(df) < 200: return None
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        close = df['Close']
        e9 = close.ewm(span=9).mean().iloc[-1]
        e21 = close.ewm(span=21).mean().iloc[-1]
        e50 = close.ewm(span=50).mean().iloc[-1]
        e200 = close.ewm(span=200).mean().iloc[-1]
        price = close.iloc[-1]
        if e9>e21>e50>e200 and price>e9: return {"ativo":symbol,"score":75,"sinal":"BUY","preco":round(float(price),2)}
        if e9<e21<e50<e200 and price<e9: return {"ativo":symbol,"score":75,"sinal":"SELL","preco":round(float(price),2)}
        return None
    except: return None

@app.route("/")
def home(): return jsonify({"status":"JARVIS ONLINE","link":"/scanner"})

@app.route("/scanner")
def scanner():
    res=[]
    for a in ATIVOS:
        s=calc_score(a)
        if s: res.append(s)
    return jsonify(sorted(res, key=lambda x: x['score'], reverse=True))

# pra gunicorn achar
application = app
