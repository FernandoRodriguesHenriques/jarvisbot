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
        score = 0
        direcao = None
        if e9>e21>e50>e200 and price>e9: score=75; direcao="BUY"
        elif e9<e21<e50<e200 and price<e9: score=75; direcao="SELL"
        else: return None
        return {"ativo":symbol,"score":score,"sinal":direcao,"preco":round(float(price),2)}
    except: return None

@app.route("/")
def home():
    return jsonify({"status":"JARVIS ONLINE","mensagem":"acesse /scanner"})

@app.route("/scanner")
def scanner():
    res=[]
    for a in ATIVOS:
        s=calc_score(a)
        if s: res.append(s)
    res = sorted(res, key=lambda x: x['score'], reverse=True)
    return jsonify(res)

if __name__=="__main__":
    app.run(host="0.0.0.0", port=10000)
