import MetaTrader5 as mt5
mt5.initialize()
pos = mt5.positions_get()
for p in pos:
    tipo = mt5.ORDER_TYPE_SELL if p.type==0 else mt5.ORDER_TYPE_BUY
    tick = mt5.symbol_info_tick(p.symbol)
    price = tick.bid if p.type==0 else tick.ask
    req = {"action": mt5.TRADE_ACTION_DEAL, "position": p.ticket, "symbol": p.symbol, "volume": p.volume, "type": tipo, "price": price, "deviation": 20, "magic": 0, "comment": "fecha", "type_time": mt5.ORDER_TIME_GTC, "type_filling": mt5.ORDER_FILLING_IOC}
    mt5.order_send(req)
    print(f"Fechada {p.ticket}")
print("TUDO FECHADO!")