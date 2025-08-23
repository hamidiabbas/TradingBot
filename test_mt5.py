import MetaTrader5 as mt5
from dotenv import load_dotenv
import os
from pathlib import Path

# Load credentials
config_env_path = Path('config') / '.env'
if config_env_path.exists():
    load_dotenv(config_env_path)
    print(f"✅ Loaded .env from: {config_env_path}")
else:
    print(f"❌ .env file not found at: {config_env_path}")
    exit()

# Get credentials
login = int(os.getenv('MT5_LOGIN', 0))
password = os.getenv('MT5_PASSWORD', '')
server = os.getenv('MT5_SERVER', '')

print(f"Testing MT5 connection...")
print(f"Login: {login}")
print(f"Server: {server}")

# Test connection
if mt5.initialize():
    print("✅ MT5 initialized successfully")
    
    if mt5.login(login, password=password, server=server):
        print("✅ MT5 login successful")
        account_info = mt5.account_info()
        if account_info:
            print(f"✅ Account: {account_info.login}")
            print(f"✅ Balance: ${account_info.balance:,.2f}")
    else:
        error = mt5.last_error()
        print(f"❌ MT5 login failed: {error}")
    
    mt5.shutdown()
else:
    error = mt5.last_error()
    print(f"❌ MT5 initialization failed: {error}")
