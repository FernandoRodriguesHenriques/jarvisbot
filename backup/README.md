# JARVIS V10.5 — Backtest Engine

Motor inicial de validação das regras do JARVIS.

Testa OHLC, EMA 9/21/50, ATR 21, Volume Ratio, Contextos 4/8,
MACD 12/26/9, padrões básicos, Ignition Bar, HTF H1/H4,
Market Guard básico, Score, SL/TP estrutural, risco percentual,
cooldown, limite diário, equity, drawdown e métricas.

## Instalação
Python 3.10+
pip install -r requirements.txt

## Teste rápido
run_backtest.bat

## Histórico próprio
Coloque o CSV em data/, por exemplo:
data/XAUUSDm_M15.csv

Colunas obrigatórias:
timestamp,open,high,low,close

Opcionais:
volume,spread

Execute:
python backtest_engine.py --csv data/XAUUSDm_M15.csv --symbol XAUUSDm

Relatórios:
reports/
