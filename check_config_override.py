#!/usr/bin/env python3
"""
Check for Configuration File Overrides
"""

import os
from pathlib import Path

def check_config_files():
    """Check all possible configuration sources"""
    
    print("🔍 CHECKING CONFIGURATION OVERRIDE SOURCES")
    print("=" * 50)
    
    # Check for config files
    config_files = [
        'config.yaml', 'config.yml', 
        'settings.yaml', 'settings.yml',
        'trading_config.yaml', 'bot_config.yaml',
        '.env'
    ]
    
    for config_file in config_files:
        if Path(config_file).exists():
            print(f"📄 Found: {config_file}")
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for problematic values
                if '0.015' in content or '1.5' in content:
                    print(f"   ❌ Contains 0.015 or 1.5 - THIS COULD BE THE BUG!")
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if '0.015' in line or '1.5' in line:
                            print(f"      Line {i+1}: {line.strip()}")
                
                if 'max_positions' in content:
                    print(f"   📍 Contains max_positions configuration")
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if 'max_positions' in line:
                            print(f"      Line {i+1}: {line.strip()}")
                            
            except Exception as e:
                print(f"   ❌ Error reading {config_file}: {e}")
        else:
            print(f"❌ Not found: {config_file}")
    
    # Check environment variables
    print(f"\n🌍 CHECKING ENVIRONMENT VARIABLES:")
    env_vars_to_check = [
        'MAX_POSITIONS', 'BASE_RISK_PER_TRADE', 
        'RISK_PERCENTAGE', 'POSITION_LIMIT'
    ]
    
    for var in env_vars_to_check:
        value = os.getenv(var)
        if value:
            print(f"   📍 {var} = {value}")
        else:
            print(f"   ❌ {var} not set")

if __name__ == "__main__":
    check_config_files()
