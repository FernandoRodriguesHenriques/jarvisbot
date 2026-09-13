import MetaTrader5 as mt5
mt5.initialize()
print([x for x in dir(mt5) if 'rate' in x.lower() or 'copy' in x.lower()])
# tenta outro nome
for nome in ["EURUSDm"]:
    mt5.symbol_select(nome, True)
    try:
        r = mt5.copy_rates_from_pos(nome, mt5.TIMEFRAME_M1, 0, 10)
        print(f"copy_rates_from_pos {nome}: {r is not None} {len(r) if r is not None else 0}")
    except Exception as e:
        print(f"erro from_pos: {e}")
    try:
        import datetime
        r = mt5.copy_rates_range(nome, mt5.TIMEFRAME_M1, datetime.datetime.now()-datetime.timedelta(minutes=100), datetime.datetime.now())
        print(f"copy_rates_range {nome}: {r is not None}")
    except Exception as e:
        print(f"erro range: {e}")