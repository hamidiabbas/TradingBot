#!/usr/bin/env python3
"""
Recover Deleted/Moved Strategies - Emergency Recovery
"""

import shutil
from pathlib import Path

def recover_all_strategies():
    """Recover all moved/disabled strategies"""
    
    print("🔄 EMERGENCY STRATEGY RECOVERY")
    print("=" * 50)
    
    recovered = 0
    
    # Recovery locations
    strategies_dir = Path("strategies")
    backup_locations = [
        Path("templates_disabled"),
        Path("strategies_backup_templates"), 
        Path("strategies_backup_real")
    ]
    
    # 1. Recover from backup folders
    for backup_dir in backup_locations:
        if backup_dir.exists():
            print(f"\n📁 Checking: {backup_dir}")
            
            for file in backup_dir.glob("*.py"):
                if not file.name.startswith('__'):
                    original_name = file.name.replace('.DISABLED', '').replace('.FAKE_DISABLED', '')
                    target_path = strategies_dir / original_name
                    
                    shutil.copy2(file, target_path)
                    print(f"✅ Recovered: {original_name}")
                    recovered += 1
    
    # 2. Recover renamed files in strategies directory
    for file in strategies_dir.glob("*.FAKE_DISABLED"):
        original_name = file.name.replace('.FAKE_DISABLED', '')
        target_path = strategies_dir / original_name
        
        shutil.move(file, target_path)
        print(f"✅ Recovered: {original_name}")
        recovered += 1
    
    for file in strategies_dir.glob("*.DISABLED"):
        original_name = file.name.replace('.DISABLED', '')
        target_path = strategies_dir / original_name
        
        shutil.move(file, target_path)
        print(f"✅ Recovered: {original_name}")
        recovered += 1
    
    print(f"\n🎉 RECOVERED {recovered} STRATEGY FILES!")
    
    # List all current strategy files
    current_strategies = list(strategies_dir.glob("*.py"))
    current_strategies = [f for f in current_strategies if not f.name.startswith('__')]
    
    print(f"\n📋 CURRENT STRATEGY FILES ({len(current_strategies)}):")
    for strategy in current_strategies:
        print(f"   ✅ {strategy.name}")
    
    return recovered

if __name__ == "__main__":
    recover_all_strategies()
