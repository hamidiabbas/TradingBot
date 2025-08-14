#!/usr/bin/env python3
"""
===============================================================
POSITION MANAGEMENT & DIAGNOSTIC TOOL - COMPLETE FIX
===============================================================
This script will:
1. Diagnose your current position situation
2. Show all open positions
3. Close old/unwanted positions if needed
4. Check broker limits
5. Fix your trading bot configuration

Version: 1.0.0 - Complete Position Fix
===============================================================
"""

import MetaTrader5 as mt5
import os
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path("config/.env")
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

class PositionManager:
    def __init__(self):
        self.connected = False
        self.account_info = None
        
    def connect(self):
        """Connect to MT5"""
        try:
            # Get credentials
            mt5_login = int(os.getenv('MT5_LOGIN', 0))
            mt5_password = os.getenv('MT5_PASSWORD', '')
            mt5_server = os.getenv('MT5_SERVER', '')
            mt5_path = os.getenv('MT5_PATH', '')
            
            if not all([mt5_login, mt5_password, mt5_server]):
                print("❌ ERROR: Missing MT5 credentials in config/.env")
                return False
            
            # Initialize MT5
            if mt5_path and Path(mt5_path).exists():
                if not mt5.initialize(path=mt5_path):
                    print(f"❌ MT5 initialization failed: {mt5.last_error()}")
                    return False
            else:
                if not mt5.initialize():
                    print(f"❌ MT5 initialization failed: {mt5.last_error()}")
                    return False
            
            # Login
            if not mt5.login(login=mt5_login, password=mt5_password, server=mt5_server):
                print(f"❌ MT5 login failed: {mt5.last_error()}")
                mt5.shutdown()
                return False
            
            # Get account info
            self.account_info = mt5.account_info()
            if not self.account_info:
                print("❌ Failed to get account info")
                return False
            
            self.connected = True
            account_type = "DEMO" if "demo" in mt5_server.lower() else "LIVE"
            print(f"✅ Connected to MT5 {account_type} account: {self.account_info.login}")
            print(f"✅ Balance: ${self.account_info.balance:.2f} {self.account_info.currency}")
            
            return True
            
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def diagnose_positions(self):
        """Complete position diagnosis"""
        if not self.connected:
            print("❌ Not connected to MT5")
            return
        
        print("\n" + "="*60)
        print("🔍 COMPLETE POSITION DIAGNOSIS")
        print("="*60)
        
        # Get all positions
        positions = mt5.positions_get()
        print(f"📊 Total Open Positions: {len(positions)}")
        
        if len(positions) == 0:
            print("✅ No open positions found")
            print("❓ This means the position limit error might be a broker configuration issue")
            self._check_broker_limits()
            return
        
        # Analyze positions
        print(f"\n📋 POSITION DETAILS:")
        print("-" * 60)
        
        total_profit = 0.0
        positions_by_symbol = {}
        old_positions = []
        
        for i, pos in enumerate(positions):
            # Calculate position age
            position_age = datetime.now() - datetime.fromtimestamp(pos.time)
            age_hours = position_age.total_seconds() / 3600
            
            # Categorize positions
            if pos.symbol not in positions_by_symbol:
                positions_by_symbol[pos.symbol] = []
            positions_by_symbol[pos.symbol].append(pos)
            
            # Check for old positions (older than 24 hours)
            if age_hours > 24:
                old_positions.append(pos)
            
            total_profit += pos.profit
            
            print(f"{i+1:2d}. Ticket: {pos.ticket}")
            print(f"     Symbol: {pos.symbol}")
            print(f"     Type: {'BUY' if pos.type == 0 else 'SELL'}")
            print(f"     Volume: {pos.volume} lots")
            print(f"     Open Price: {pos.price_open}")
            print(f"     Current Price: {pos.price_current}")
            print(f"     Profit: ${pos.profit:.2f}")
            print(f"     Age: {age_hours:.1f} hours")
            print(f"     Comment: {pos.comment}")
            print("-" * 60)
        
        print(f"\n💰 Total Unrealized P&L: ${total_profit:.2f}")
        print(f"📈 Positions by Symbol:")
        for symbol, symbol_positions in positions_by_symbol.items():
            total_volume = sum(p.volume for p in symbol_positions)
            symbol_profit = sum(p.profit for p in symbol_positions)
            print(f"   {symbol}: {len(symbol_positions)} positions, {total_volume:.2f} lots, ${symbol_profit:.2f}")
        
        if old_positions:
            print(f"\n⚠️  OLD POSITIONS DETECTED: {len(old_positions)} positions older than 24 hours")
            print("   These might be from previous bot runs and could be blocking new trades")
        
        # Check broker limits
        self._check_broker_limits()
        
        return positions, old_positions
    
    def _check_broker_limits(self):
        """Check broker-specific limits"""
        print(f"\n🏦 BROKER LIMIT ANALYSIS:")
        print("-" * 30)
        
        # Try to get symbol info for major pairs
        test_symbols = ['EURUSD', 'GBPUSD', 'USDJPY']
        
        for symbol in test_symbols:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info:
                print(f"✅ {symbol}: Available")
                print(f"   Min volume: {symbol_info.volume_min}")
                print(f"   Max volume: {symbol_info.volume_max}")
                print(f"   Volume step: {symbol_info.volume_step}")
            else:
                print(f"❌ {symbol}: Not available")
        
        # Check account limits
        if self.account_info:
            print(f"\n📊 Account Limits:")
            print(f"   Trade allowed: {self.account_info.trade_allowed}")
            print(f"   Trade expert: {self.account_info.trade_expert}")
            print(f"   Margin mode: {self.account_info.margin_mode}")
            print(f"   Leverage: 1:{self.account_info.leverage}")
    
    def close_old_positions(self, hours_threshold=24, confirm=True):
        """Close positions older than specified hours"""
        if not self.connected:
            print("❌ Not connected to MT5")
            return False
        
        positions = mt5.positions_get()
        if not positions:
            print("✅ No positions to close")
            return True
        
        old_positions = []
        for pos in positions:
            position_age = datetime.now() - datetime.fromtimestamp(pos.time)
            age_hours = position_age.total_seconds() / 3600
            
            if age_hours > hours_threshold:
                old_positions.append(pos)
        
        if not old_positions:
            print(f"✅ No positions older than {hours_threshold} hours")
            return True
        
        print(f"\n⚠️  FOUND {len(old_positions)} OLD POSITIONS TO CLOSE:")
        total_profit = 0.0
        
        for pos in old_positions:
            age_hours = (datetime.now() - datetime.fromtimestamp(pos.time)).total_seconds() / 3600
            total_profit += pos.profit
            print(f"   Ticket {pos.ticket}: {pos.symbol} {pos.volume} lots, ${pos.profit:.2f}, {age_hours:.1f}h old")
        
        print(f"   Total P&L if closed: ${total_profit:.2f}")
        
        if confirm:
            response = input(f"\n❓ Close these {len(old_positions)} old positions? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("❌ Position closing cancelled")
                return False
        
        # Close positions
        closed_count = 0
        failed_count = 0
        
        for pos in old_positions:
            try:
                # Determine close price
                tick = mt5.symbol_info_tick(pos.symbol)
                if not tick:
                    print(f"❌ Cannot get tick for {pos.symbol}")
                    failed_count += 1
                    continue
                
                close_price = tick.bid if pos.type == 0 else tick.ask  # BUY positions close at bid, SELL at ask
                
                # Create close request
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": pos.symbol,
                    "volume": pos.volume,
                    "type": mt5.ORDER_TYPE_SELL if pos.type == 0 else mt5.ORDER_TYPE_BUY,
                    "position": pos.ticket,
                    "price": close_price,
                    "deviation": 20,
                    "magic": 0,
                    "comment": "Closed by position manager",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_FOK,
                }
                
                result = mt5.order_send(request)
                
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    print(f"✅ Closed position {pos.ticket}: ${pos.profit:.2f}")
                    closed_count += 1
                else:
                    error_msg = result.comment if result else "Unknown error"
                    print(f"❌ Failed to close {pos.ticket}: {error_msg}")
                    failed_count += 1
                    
            except Exception as e:
                print(f"❌ Error closing position {pos.ticket}: {e}")
                failed_count += 1
        
        print(f"\n📋 CLOSING SUMMARY:")
        print(f"   ✅ Successfully closed: {closed_count}")
        print(f"   ❌ Failed to close: {failed_count}")
        
        return closed_count > 0
    
    def close_all_positions(self, confirm=True):
        """Close ALL positions (use with caution)"""
        if not self.connected:
            print("❌ Not connected to MT5")
            return False
        
        positions = mt5.positions_get()
        if not positions:
            print("✅ No positions to close")
            return True
        
        total_profit = sum(pos.profit for pos in positions)
        
        print(f"\n🚨 WARNING: CLOSE ALL {len(positions)} POSITIONS")
        print(f"   Total current P&L: ${total_profit:.2f}")
        
        if confirm:
            print(f"   This will close ALL open positions immediately!")
            response = input(f"❓ Are you absolutely sure? Type 'CLOSE ALL' to confirm: ")
            if response != 'CLOSE ALL':
                print("❌ Cancelled - positions remain open")
                return False
        
        return self.close_old_positions(hours_threshold=0, confirm=False)
    
    def disconnect(self):
        """Disconnect from MT5"""
        if self.connected:
            mt5.shutdown()
            self.connected = False
            print("✅ Disconnected from MT5")

def update_bot_config():
    """Update trading bot configuration to prevent position limit issues"""
    print("\n🔧 UPDATING BOT CONFIGURATION...")
    
    config_path = "config.yaml"
    
    try:
        # Load existing config
        if Path(config_path).exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f) or {}
        else:
            config = {}
        
        # Update with safe position limits
        config.update({
            'max_positions': 3,  # Reduced from 8 to 3
            'min_position_size': 0.01,
            'max_position_size': 0.05,  # Reduced from 0.20 to 0.05
            'signal_processing_interval': 10,  # Slower processing
            'base_risk_per_trade': 0.01,  # Reduced risk
            'max_risk_per_trade': 0.02,  # Reduced max risk
            
            # Add position management settings
            'position_management': {
                'auto_close_old_positions': True,
                'max_position_age_hours': 48,
                'max_concurrent_positions_per_symbol': 1
            }
        })
        
        # Save updated config
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        print(f"✅ Updated {config_path} with safe position limits:")
        print(f"   Max positions: {config['max_positions']}")
        print(f"   Max position size: {config['max_position_size']}")
        print(f"   Base risk per trade: {config['base_risk_per_trade']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating config: {e}")
        return False

def main():
    """Main position management workflow"""
    print("🚀 TRADING BOT POSITION MANAGER & FIXER")
    print("="*50)
    
    manager = PositionManager()
    
    # Step 1: Connect
    if not manager.connect():
        print("❌ Cannot connect to MT5. Check your config/.env file.")
        return
    
    # Step 2: Diagnose
    try:
        positions, old_positions = manager.diagnose_positions()
        
        # Step 3: Offer solutions
        if positions:
            print(f"\n🎯 RECOMMENDED ACTIONS:")
            
            if old_positions:
                print(f"1. Close {len(old_positions)} old positions (recommended)")
                print(f"2. Close ALL {len(positions)} positions (if needed)")
                print(f"3. Update bot configuration for lower limits")
                print(f"4. Do nothing and just update config")
                
                choice = input(f"\nChoose action (1-4): ").strip()
                
                if choice == "1":
                    manager.close_old_positions()
                elif choice == "2":
                    manager.close_all_positions()
                elif choice in ["3", "4"]:
                    print("Skipping position closure...")
                else:
                    print("Invalid choice, updating config only...")
            else:
                print(f"1. Close ALL {len(positions)} positions")
                print(f"2. Update bot configuration only")
                
                choice = input(f"\nChoose action (1-2): ").strip()
                
                if choice == "1":
                    manager.close_all_positions()
        
        # Step 4: Update configuration
        update_bot_config()
        
        # Step 5: Final check
        print(f"\n✅ FINAL STATUS CHECK:")
        remaining_positions = mt5.positions_get()
        print(f"   Remaining positions: {len(remaining_positions) if remaining_positions else 0}")
        print(f"   Bot config updated: ✅")
        
        if not remaining_positions or len(remaining_positions) <= 3:
            print(f"\n🎉 SUCCESS! Your trading bot should now work properly.")
            print(f"   Run: python main.py --mode demo")
        else:
            print(f"\n⚠️  You still have {len(remaining_positions)} positions.")
            print(f"   Consider closing more positions or reducing max_positions in config.yaml")
        
    except Exception as e:
        print(f"❌ Error during diagnosis: {e}")
    
    finally:
        manager.disconnect()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
