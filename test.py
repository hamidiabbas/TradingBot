#!/usr/bin/env python3
"""
Position Sizing Diagnostic Tool - Identify 0.01 Lot Issue
"""

import MetaTrader5 as mt5
import os
from pathlib import Path
from dotenv import load_dotenv

def diagnose_position_sizing():
    """Diagnose why all positions are 0.01 lots"""
    
    # Load credentials
    env_path = Path("config/.env")
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    
    # Connect to MT5
    mt5_login = int(os.getenv('MT5_LOGIN', 0))
    mt5_password = os.getenv('MT5_PASSWORD', '')
    mt5_server = os.getenv('MT5_SERVER', '')
    
    if not mt5.initialize():
        print("❌ MT5 initialization failed")
        return
    
    if not mt5.login(login=mt5_login, password=mt5_password, server=mt5_server):
        print("❌ MT5 login failed")
        return
    
    print("🔍 POSITION SIZING DIAGNOSTIC REPORT")
    print("=" * 50)
    
    # Check account info
    account_info = mt5.account_info()
    if account_info:
        balance = account_info.balance
        equity = account_info.equity
        leverage = account_info.leverage
        
        print(f"💰 Account Balance: ${balance:.2f}")
        print(f"💰 Account Equity: ${equity:.2f}")
        print(f"📊 Leverage: 1:{leverage}")
    
    # Check symbol specifications
    test_symbols = ['EURUSD', 'GBPUSD', 'USDJPY']
    
    print(f"\n📋 SYMBOL SPECIFICATIONS:")
    for symbol in test_symbols:
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info:
            print(f"\n{symbol}:")
            print(f"  Min Volume: {symbol_info.volume_min}")
            print(f"  Max Volume: {symbol_info.volume_max}")
            print(f"  Volume Step: {symbol_info.volume_step}")
            
            # Test Kelly calculations manually
            test_kelly_calculation(symbol, balance if account_info else 10000)
    
    # Check recent trades
    print(f"\n📈 RECENT TRADES ANALYSIS:")
    positions = mt5.positions_get()
    history = mt5.history_orders_get()
    
    if positions:
        print(f"Current Open Positions: {len(positions)}")
        for pos in positions[-5:]:  # Last 5 positions
            print(f"  {pos.symbol}: {pos.volume} lots, Profit: ${pos.profit:.2f}")
    
    if history:
        recent_orders = [order for order in history if hasattr(order, 'volume')][-10:]
        print(f"Last 10 Orders:")
        for order in recent_orders:
            print(f"  {order.symbol}: {order.volume} lots")
    
    mt5.shutdown()

def test_kelly_calculation(symbol: str, balance: float):
    """Test Kelly calculation manually"""
    print(f"\n🧮 MANUAL KELLY TEST for {symbol}:")
    
    # Simulate your Kelly parameters
    confidence = 0.65
    base_risk_per_trade = 0.015  # 1.5%
    kelly_multiplier = 0.5
    
    # Basic Kelly calculation
    risk_amount = balance * base_risk_per_trade * confidence * kelly_multiplier
    print(f"  Calculated Risk Amount: ${risk_amount:.2f}")
    
    # Convert to position size (simplified)
    estimated_position_size = risk_amount / 100000  # Rough conversion
    print(f"  Estimated Position Size: {estimated_position_size:.4f} lots")
    
    # Apply minimum bounds
    final_size = max(0.01, min(0.10, estimated_position_size))
    print(f"  Final Size (with bounds): {final_size:.4f} lots")
    
    if final_size == 0.01:
        print(f"  ⚠️  WARNING: Hitting minimum bound!")
        print(f"     Calculated size too small: {estimated_position_size:.6f}")
        
        # Suggest fixes
        if estimated_position_size < 0.005:
            print(f"  💡 SOLUTION: Increase base_risk_per_trade or balance")

if __name__ == "__main__":
    diagnose_position_sizing()

