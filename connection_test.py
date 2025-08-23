import MetaTrader5 as mt5

# Test connection
if mt5.initialize():
    print("✅ MT5 Connected!")
    print(f"MT5 Version: {mt5.version()}")
    
    # Test data retrieval
    rates = mt5.copy_rates_from_pos("EURUSD", mt5.TIMEFRAME_H1, 0, 100)
    if rates is not None:
        print(f"✅ Got {len(rates)} bars")
        print("Columns:", rates.dtype.names)  # Should show: ('time', 'open', 'high', 'low', 'close', 'tick_volume', 'spread', 'real_volume')
    else:
        print("❌ No data retrieved")
        
    mt5.shutdown()
else:
    print("❌ MT5 Connection failed")
    print(f"Error: {mt5.last_error()}")
