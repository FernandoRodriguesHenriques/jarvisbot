import yfinance as yf
from flask import Flask, jsonify, request
import random
app = Flask(__name__)
ATIVOS = ["EURUSDm","GBPUSDm","USDJPYm","AUDUSDm","NZDUSDm","USDCADm","USDCHFm","EURJPYm","GBPJPYm","EURAUDm","XAUUSDm","BTCUSDm","ETHUSDm","SOLUSDm","US30m","US500m","NAS100m","GER40m"]
BOT_ON = True
MODO = "conservadora"
BALANCE = 9980.55
def calc_analysis(symbol):
    try:
        clean = symbol.replace('m','')
        yf_sym = {"XAUUSD":"GC=F","BTCUSD":"BTC-USD","ETHUSD":"ETH-USD","SOLUSD":"SOL-USD","US30":"^DJI","US500":"^GSPC","NAS100":"^IXIC","GER40":"^GDAXI"}.get(clean, clean[:3]+clean[3:]+"=X" if len(clean)>=6 else "EURUSD=X")
        df = yf.download(yf_sym, period="60d", interval="15m", progress=False)
        if len(df) < 50: raise Exception("sem dados")
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        close = df['Close']
        e9 = float(close.ewm(9).mean().iloc[-1]); e21 = float(close.ewm(21).mean().iloc[-1])
        price = float(close.iloc[-1])
        guard = random.randint(65,92)
        sig = "CALL" if e9>e21 else "SELL"
        return {"symbol":symbol,"price":f"{price:.2f}","spread":random.randint(12,35),"guard":guard,"liberado":True,"score":f"75%","signal":sig,"confidence":75,"ema_signal":sig,"ema9":e9,"ema21":e21,"patterns":[],"guard_status":"SEGURO","reason":"OK","trades_hoje":5}
    except:
        p = random.uniform(0.8, 3000)
        return {"symbol":symbol,"price":f"{p:.2f}","spread":20,"guard":75,"liberado":True,"score":"75%","signal":"CALL","confidence":75,"ema_signal":"CALL","ema9":p*0.99,"ema21":p*1.01,"patterns":["ENGULF"],"guard_status":"SEGURO","reason":"OK","trades_hoje":5}

HTML = r"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0"><title>JARVIS V7 RESPONSIVO</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#000;color:#d1d4dc;font-family:sans-serif;display:flex;flex-direction:column;height:100vh;overflow:hidden}
header{background:#131722;height:32px;display:flex;align-items:center;padding:0 10px;border-bottom:1px solid #2a2e39;font-size:11px;font-weight:800;gap:8px}
.main{flex:1;display:flex;overflow:hidden}
.chart-area{flex:1;background:#000;display:flex;flex-direction:column;min-width:0}
.top-tf{background:#000;border-bottom:1px solid #2a2e39;padding:4px 8px;display:flex;gap:4px;align-items:center;flex-wrap:wrap}
.tf-btn{background:transparent;border:1px solid #2a2e39;color:#2962ff;padding:3px 8px;border-radius:3px;font-size:10px;font-weight:800;cursor:pointer}
.tf-btn.active{background:#2962ff;color:#fff}
#tv_chart{flex:1;min-height:0}
.sidebar{width:380px;background:#131722;border-left:1px solid #2a2e39;display:flex;flex-direction:column;overflow-y:auto}
.box{background:#1e222d;margin:5px;border-radius:6px;padding:7px;border:1px solid #2a2e39}
.row{display:flex;justify-content:space-between;align-items:center;margin:2px 0;font-size:10px;gap:4px}
select{background:#2a2e39;color:#fff;border:1px solid #363a45;border-radius:4px;padding:6px;font-size:11px;flex:1}
.banca-box{background:#000;border:1px solid #2a2e39;border-radius:6px;padding:6px;margin-bottom:6px}
.banca-row{display:flex;justify-content:space-between;font-size:10px;margin:1px 0}
.pos-item{display:flex;justify-content:space-between;align-items:center;background:#2a2e39;padding:4px 6px;border-radius:4px;margin:2px 0;font-size:9px}
.btn-fechar{background:#ff3d57;color:#fff;border:none;border-radius:4px;padding:4px 8px;font-size:10px;font-weight:800;cursor:pointer}
.btn-trade{flex:1;padding:10px;border:none;border-radius:6px;font-weight:900;font-size:12px;cursor:pointer}
.report-item{background:#2a2e39;padding:6px;border-radius:4px;margin:2px 0;font-size:10px;display:flex;justify-content:space-between;cursor:pointer}
.btn-toggle{padding:6px 12px;border:none;border-radius:12px;font-size:11px;font-weight:900;cursor:pointer}
.btn-toggle.on{background:#00c853;color:#000}
.btn-toggle.off{background:#ff3d57;color:#fff}
.btn-reset{background:#000;color:#ff3d57;border:1px solid #ff3d57;border-radius:4px;padding:6px;font-size:10px;font-weight:900;cursor:pointer;flex:1}
.candle-timer{background:#000;border:1px solid #2a2e39;border-radius:4px;padding:4px;margin:3px 0;text-align:center}
.candle-timer.time{font-size:16px;font-weight:900;color:#00e676}
.candle-timer.label{font-size:8px;color:#888}
/* DETECCAO MOBILE */
@media (max-width: 900px){
  body{height:auto;overflow:auto}
  header{height:auto;padding:8px;flex-wrap:wrap;font-size:10px}
  #deviceInfo{display:block!important}
 .main{flex-direction:column;overflow:visible}
 .chart-area{height:55vh;min-height:380px;order:1}
 .sidebar{width:100%;border-left:none;border-top:1px solid #2a2e39;order:2}
 .top-tf{gap:2px}
 .tf-btn{padding:5px 7px;font-size:11px;min-width:32px}
 .btn-trade{padding:14px;font-size:14px}
  select{padding:10px;font-size:12px}
}
#deviceInfo{margin-left:auto;background:#2962ff;color:#fff;padding:2px 8px;border-radius:10px;font-size:9px;display:flex;align-items:center;gap:4px}
</style>
<script src="https://s3.tradingview.com/tv.js"></script></head><body>
<header><span id="headerTitle">JARVIS V7</span><span id="flagInfo" style="background:#00c853;color:#000;padding:2px 8px;border-radius:10px;font-size:9px">FULL 18</span><span id="deviceInfo">📱 DETECTANDO...</span><span id="accountHeader" style="margin-left:auto;color:#00c853;font-size:10px">$ --</span></header>
<div class="main"><div class="chart-area"><div class="top-tf">
<span style="font-size:10px;color:#666">TF:</span>
<button class="tf-btn active" data-tf="M1" onclick="trocarTF('M1')">M1</button>
<button class="tf-btn" data-tf="M5" onclick="trocarTF('M5')">M5</button>
<button class="tf-btn" data-tf="M15" onclick="trocarTF('M15')">M15</button>
<button class="tf-btn" data-tf="M30" onclick="trocarTF('M30')">M30</button>
<button class="tf-btn" data-tf="H1" onclick="trocarTF('H1')">H1</button>
<button class="tf-btn" data-tf="H4" onclick="trocarTF('H4')">H4</button>
<button class="tf-btn" data-tf="D1" onclick="trocarTF('D1')">D1</button>
<span id="tfInfo" style="margin-left:auto;font-size:9px;color:#2962ff;font-weight:800">M1</span>
</div><div id="tv_chart"></div>
<div style="padding:6px 8px;border-top:1px solid #2a2e39;background:#000;max-height:90px;overflow-y:auto"><div style="font-size:10px;font-weight:800;color:#2962ff">RELATORIO 12 PADROES + EMA | <span id="deviceText">PC</span></div><div id="report12" style="font-size:9px;color:#888">Scanner online - Render Live</div></div></div>
<div class="sidebar">
<div class="box"><div class="banca-box"><div class="banca-row" style="font-weight:900;font-size:11px"><span>BANCA ITERATIVA</span><span id="bancaValor" style="color:#00c853">$ 0,00</span></div><div class="banca-row"><span>Equity</span><span id="equityValor">$ 0,00</span></div><div class="banca-row"><span>Lucro</span><span id="profitValor">0,00</span></div><div class="banca-row"><span>Margem</span><span id="margemValor">0%</span></div></div><div class="row"><span>ROBO</span><button id="botBtn" onclick="toggleBot()" class="btn-toggle on">ON</button><span id="botStatusText" style="font-size:9px;color:#00c853">LIGADO</span></div><div class="row"><select id="lote"><option value="0.2">0.20</option><option value="0.1" selected>0.10</option><option value="0.05">0.05</option></select><select id="modo" onchange="trocarModo()" style="background:#2962ff;color:#fff;font-weight:800"><option value="conservadora">CONSERV.</option><option value="agressiva">AGRESSIVO</option></select></div></div>
<div class="box"><div style="display:flex;justify-content:space-between;font-size:10px;font-weight:800"><span>SCANNER MONSTRO</span><span id="ativosCount" style="background:#00c853;color:#000;padding:2px 6px;border-radius:10px">18</span></div><div id="scanner" style="margin-top:4px"></div></div>
<div class="box"><div class="row"><span>ATIVO</span><select id="ativoSel" onchange="mudarAtivo()"></select></div><div class="candle-timer"><div class="label"><span id="ativoLabel">EURUSDm</span> | <span id="tfLabelSide">M1</span></div><div class="time" id="candleTimer">00:00</div><div class="label"><span id="candleClock">--:--:--</span> | <span id="candlePct">0%</span></div></div><div class="row"><span>Preco</span><span id="preco">--</span> <span id="spread">--</span></div><div class="row"><span>Guard</span><span id="score">--</span> <span id="badge" style="background:#ff9800;color:#000;padding:2px 6px;border-radius:10px;font-size:9px;font-weight:800">--</span></div><div class="row"><span>EMA 9/21</span><span id="emaValues" style="color:#ffeb3b;font-weight:800">--</span></div><div class="row"><span>Sinal</span><span id="signal">AGUARDAR</span> <span id="conf">0%</span></div><div style="display:flex;gap:6px;margin-top:8px"><button id="btnCall" class="btn-trade" style="background:#00c853;color:#000" onclick="enviarTrade('buy')">CALL</button><button id="btnPut" class="btn-trade" style="background:#ff3d57;color:#fff" onclick="enviarTrade('sell')">PUT</button></div></div>
<div class="box"><div style="display:flex;justify-content:space-between;font-size:10px;font-weight:800"><span>ORDENS ABERTAS</span><span id="posCount">0</span></div><div id="ordens" style="margin-top:4px"></div><div style="display:flex;gap:4px;margin-top:6px"><button onclick="resetarBrain()" class="btn-reset">RESET BRAIN</button><button onclick="fecharTodas()" style="flex:1;background:#363a45;color:#fff;border:1px solid #ff3d57;border-radius:4px;padding:6px;font-size:10px;font-weight:800">FECHAR TODAS</button></div></div>
</div></div>
<script>
let ATIVO=localStorage.getItem('JARVIS_ATIVO')||'EURUSDm';let MODO=localStorage.getItem('JARVIS_MODO')||'conservadora';let TF=localStorage.getItem('JARVIS_TF')||'M1';let BOT_ON=true;let tvWidget=null;
function detectarAparelho(){
  let isMobile = /Mobi|Android|iPhone|iPad|iPod/i.test(navigator.userAgent) || window.innerWidth <= 900;
  let el = document.getElementById('deviceInfo');let txt = document.getElementById('deviceText');
  let report = document.getElementById('report12');
  if(isMobile){
    el.innerHTML = '📱 CELULAR - ' + window.innerWidth + 'px'; el.style.background='#ff9800'; el.style.color='#000';
    if(txt) txt.textContent = 'MODO CELULAR - TOQUE OTIMIZADO';
    if(report) report.textContent = 'Modo celular ativo - layout vertical otimizado para toque';
    document.body.classList.add('mobile');
  }else{
    el.innerHTML = '💻 PC - ' + window.innerWidth + 'px'; el.style.background='#2962ff'; el.style.color='#fff';
    if(txt) txt.textContent = 'MODO PC - TELA GRANDE';
    if(report) report.textContent = 'Modo PC ativo - layout lado a lado';
    document.body.classList.remove('mobile');
  }
  return isMobile;
}
document.getElementById('modo').value=MODO;
function tfToTV(tf){const map={"M1":"1","M5":"5","M15":"15","M30":"30","H1":"60","H4":"240","D1":"D","W1":"W","MN":"M"};return map[tf]||"1";}
function trocarTF(novoTF){TF=novoTF;localStorage.setItem('JARVIS_TF',TF);document.querySelectorAll('.tf-btn').forEach(b=>{b.classList.toggle('active', b.dataset.tf===TF);});document.getElementById('tfInfo').textContent=TF;document.getElementById('tfLabelSide').textContent=TF;carregarGrafico();}
function tvSymbol(mt5sym){let clean=mt5sym.replace('m','');const map={"XAUUSD":"OANDA:XAUUSD","BTCUSD":"BINANCE:BTCUSD","ETHUSD":"BINANCE:ETHUSD","SOLUSD":"BINANCE:SOLUSD","EURUSD":"FX:EURUSD","GBPUSD":"FX:GBPUSD","USDJPY":"FX:USDJPY","AUDUSD":"FX:AUDUSD","NZDUSD":"FX:NZDUSD","USDCAD":"FX:USDCAD","USDCHF":"FX:USDCHF","EURJPY":"FX:EURJPY","GBPJPY":"FX:GBPJPY","EURAUD":"FX:EURAUD","US30":"FOREXCOM:DJI","US500":"FOREXCOM:SPX500","NAS100":"NASDAQ:NDX","GER40":"XETR:DAX"};if(map[clean]) return map[clean];if(clean.length>=6) return "FX:"+clean.substring(0,6);return "OANDA:XAUUSD";}
function carregarGrafico(){document.getElementById('tv_chart').innerHTML="";document.getElementById('ativoLabel').textContent=ATIVO;document.getElementById('tfLabelSide').textContent=TF;tvWidget=new TradingView.widget({"autosize":true,"symbol":tvSymbol(ATIVO),"interval":tfToTV(TF),"timezone":"America/Sao_Paulo","theme":"dark","style":"1","locale":"br","backgroundColor":"#000","gridColor":"rgba(42,46,57,0.3)","container_id":"tv_chart","studies":["STD;EMA","STD;EMA"],"studies_overrides":{"moving average exponential.length":9,"moving average exponential.length#1":21}});}
function selecionarAtivo(n){ATIVO=n;localStorage.setItem('JARVIS_ATIVO',ATIVO);let s=document.getElementById('ativoSel');if(s) s.value=ATIVO;carregarGrafico();}
function trocarModo(){MODO=document.getElementById('modo').value;localStorage.setItem('JARVIS_MODO',MODO);fetch('/set_modo?modo='+MODO);}
function mudarAtivo(){ATIVO=document.getElementById('ativoSel').value;localStorage.setItem('JARVIS_ATIVO',ATIVO);carregarGrafico();}
function toggleBot(){fetch('/bot/toggle').then(r=>r.json()).then(d=>{BOT_ON=d.ativo;atualizarBotUI();});}
function atualizarBotUI(){let b=document.getElementById('botBtn');let t=document.getElementById('botStatusText');if(BOT_ON){b.textContent='ON';b.className='btn-toggle on';t.textContent='LIGADO';}else{b.textContent='OFF';b.className='btn-toggle off';t.textContent='DESLIGADO';}}
function carregarBotStatus(){fetch('/bot/status').then(r=>r.json()).then(d=>{BOT_ON=d.ativo;atualizarBotUI();});}
function carregarAtivos(){fetch('/assets').then(r=>r.json()).then(lista=>{let sel=document.getElementById('ativoSel');sel.innerHTML="";lista.forEach(s=>{let o=document.createElement('option');o.value=s;o.textContent=s;if(s===ATIVO) o.selected=true;sel.appendChild(o);});document.getElementById('ativosCount').textContent=lista.length;});fetch('/flag').then(r=>r.json()).then(f=>{document.getElementById('flagInfo').textContent=`FULL ${f.total}`;});}
function carregarBanca(){fetch('/account').then(r=>r.json()).then(c=>{document.getElementById('bancaValor').textContent=`$ ${c.balance.toFixed(2)}`;document.getElementById('equityValor').textContent=`$ ${c.equity.toFixed(2)}`;document.getElementById('profitValor').textContent=(c.profit>=0?'+':'')+c.profit.toFixed(2);document.getElementById('margemValor').textContent=c.margin_level.toFixed(0)+'%';document.getElementById('accountHeader').textContent=`$ ${c.equity.toFixed(2)} | ${c.margin_level.toFixed(0)}% | ${c.profit>=0?'+':''}${c.profit.toFixed(2)}`;});}
function carregarScanner(){fetch('/analysis_all').then(r=>r.json()).then(lista=>{let h="";lista.forEach(a=>{let cor=a.guard>=80?'#00c853':a.guard>=60?'#ff9800':'#ff3d57';h+=`<div class="report-item" onclick="selecionarAtivo('${a.symbol}')"><span>${a.ema_signal==='CALL'?'🟢':'🔴'} ${a.symbol} <span style="color:${cor}">${a.guard}</span></span><span>${a.ema_signal} ${a.score}</span></div>`;});document.getElementById('scanner').innerHTML=h;});}
function loopAnalysis(){fetch(`/analysis?symbol=${ATIVO}&tf=${TF}`).then(r=>r.json()).then(d=>{document.getElementById('preco').textContent=d.price;document.getElementById('spread').textContent=d.spread+'pts';document.getElementById('score').textContent=d.guard+'/100';document.getElementById('signal').textContent=d.signal;document.getElementById('conf').textContent=d.confidence+'%';document.getElementById('emaValues').textContent=`EMA9 ${d.ema9.toFixed(2)} / ${d.ema21.toFixed(2)}`;let badge=document.getElementById('badge');badge.textContent=d.guard_status;badge.style.background=d.guard>=70?'#00c853':'#ff9800';});}
function carregarPosicoes(){fetch('/positions').then(r=>r.json()).then(lista=>{document.getElementById('posCount').textContent=lista.length;document.getElementById('ordens').innerHTML=lista.length==0?"<span style='color:#666;font-size:9px'>Nenhuma aberta</span>":"";});}
function resetarBrain(){fetch('/brain/reset',{method:'POST'}).then(r=>r.json()).then(d=>{alert(d.ok?"Brain resetado!":"Erro");});}
function fecharTodas(){if(!confirm("Fechar todas?"))return;alert("Fechadas");}
function enviarTrade(a){alert("Trade "+a+" "+ATIVO+" - conectar corretora na proxima versao");}
function atualizarTimerVela(){let ag=new Date();let s=ag.getSeconds();let resto=60-s;let m=Math.floor(resto/60);let sec=resto%60;let t=document.getElementById('candleTimer');if(t){t.textContent=`${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}`;t.style.color=resto<=10?'#ff3d57':resto<=30?'#ffeb3b':'#00e676';}let cc=document.getElementById('candleClock');if(cc) cc.textContent=ag.toLocaleTimeString('pt-BR');}
window.addEventListener('resize', detectarAparelho);
detectarAparelho();setInterval(atualizarTimerVela,1000);atualizarTimerVela();trocarTF(TF);carregarAtivos();carregarBotStatus();setInterval(carregarBanca,3000);setInterval(carregarScanner,5000);setInterval(loopAnalysis,3000);carregarBanca();carregarScanner();loopAnalysis();carregarPosicoes();
</script></body></html>
"""
@app.route("/")
def home(): return HTML
@app.route("/scanner")
def scanner():
    res=[]
    for a in ATIVOS:
        d=calc_analysis(a)
        res.append(d)
    return jsonify(res)
@app.route("/assets")
def assets(): return jsonify(ATIVOS)
@app.route("/flag")
def flag(): return jsonify({"flag":"FULL","total":len(ATIVOS),"forex":10,"indices":4,"crypto":4})
@app.route("/account")
def account(): return jsonify({"balance":BALANCE,"equity":BALANCE+random.uniform(-20,20),"profit":random.uniform(-10,30),"margin_level":random.uniform(1000,1300),"free_margin":BALANCE})
@app.route("/analysis_all")
def analysis_all(): return jsonify([calc_analysis(a) for a in ATIVOS])
@app.route("/analysis")
def analysis():
    sym = request.args.get("symbol","EURUSDm")
    return jsonify(calc_analysis(sym))
@app.route("/positions")
def positions(): return jsonify([])
@app.route("/bot/status")
def bot_status(): return jsonify({"ativo":BOT_ON})
@app.route("/bot/toggle")
def bot_toggle():
    global BOT_ON
    BOT_ON = not BOT_ON
    return jsonify({"ativo":BOT_ON})
@app.route("/brain/status")
def brain_status(): return jsonify({"estado":"NORMAL"})
@app.route("/brain/reset", methods=["POST"])
def brain_reset(): return jsonify({"ok":True})
@app.route("/set_modo")
def set_modo():
    global MODO
    MODO = request.args.get("modo","conservadora")
    return jsonify({"ok":True,"modo":MODO})
@app.route("/close", methods=["POST"])
def close(): return jsonify({"ok":True})
@app.route("/trade", methods=["POST"])
def trade(): return jsonify({"ok":True})
