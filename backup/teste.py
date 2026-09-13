import MetaTrader5 as mt5
mt5.initialize()
print("Símbolos com EUR:")
for s in mt5.symbols_get():
    if "EURUSD" in s.name:
        print(s.name, "-> visivel?", s.visible)

# Testa pegar candles
for nome in ["EURUSD", "EURUSDm", "EURUSD.r", "EURUSDs"]:
    mt5.symbol_select(nome, True)
    rates = mt5.copy_rates(nome, mt5.TIMEFRAME_M1, 0, 5)
    print(f"{nome}: rates={rates is not None} qtd={len(rates) if rates is not None else 0}")