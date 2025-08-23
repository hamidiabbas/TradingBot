#!/usr/bin/env python3
"""
Nuclear Cache Clear - Remove ALL Python cache
"""

import os
import shutil
import sys
from pathlib import Path

def nuclear_cache_clear():
    """Remove ALL Python cache files and directories"""
    
    print("🧹 NUCLEAR CACHE CLEAR - REMOVING ALL PYTHON CACHE")
    print("=" * 60)
    
    cleared_items = []
    
    # 1. Remove all __pycache__ directories
    print("🔍 Searching for __pycache__ directories...")
    for root, dirs, files in os.walk('.'):
        for dirname in dirs[:]:  # Use slice to avoid modifying while iterating
            if dirname == '__pycache__':
                cache_path = Path(root) / dirname
                try:
                    shutil.rmtree(cache_path)
                    cleared_items.append(f"📁 {cache_path}")
                    print(f"✅ Deleted: {cache_path}")
                except Exception as e:
                    print(f"❌ Failed to delete {cache_path}: {e}")
    
    # 2. Remove all .pyc files
    print("\n🔍 Searching for .pyc files...")
    for root, dirs, files in os.walk('.'):
        for filename in files:
            if filename.endswith('.pyc'):
                pyc_path = Path(root) / filename
                try:
                    pyc_path.unlink()
                    cleared_items.append(f"📄 {pyc_path}")
                    print(f"✅ Deleted: {pyc_path}")
                except Exception as e:
                    print(f"❌ Failed to delete {pyc_path}: {e}")
    
    # 3. Remove all .pyo files (optimized bytecode)
    print("\n🔍 Searching for .pyo files...")
    for root, dirs, files in os.walk('.'):
        for filename in files:
            if filename.endswith('.pyo'):
                pyo_path = Path(root) / filename
                try:
                    pyo_path.unlink()
                    cleared_items.append(f"📄 {pyo_path}")
                    print(f"✅ Deleted: {pyo_path}")
                except Exception as e:
                    print(f"❌ Failed to delete {pyo_path}: {e}")
    
    # 4. Clear Python's import cache in memory
    print("\n🧠 Clearing Python import cache...")
    modules_to_clear = []
    for module_name in list(sys.modules.keys()):
        if any(name in module_name.lower() for name in ['main', 'signal', 'position', 'trading']):
            modules_to_clear.append(module_name)
    
    for module_name in modules_to_clear:
        try:
            del sys.modules[module_name]
            print(f"✅ Cleared from memory: {module_name}")
        except Exception as e:
            print(f"❌ Failed to clear {module_name}: {e}")
    
    # 5. Summary
    print(f"\n🎉 NUCLEAR CACHE CLEAR COMPLETE!")
    print(f"📊 Total items cleared: {len(cleared_items)}")
    print(f"🧠 Modules cleared from memory: {len(modules_to_clear)}")
    
    if cleared_items:
        print(f"\n📋 Cleared items:")
        for item in cleared_items[:10]:  # Show first 10
            print(f"   {item}")
        if len(cleared_items) > 10:
            print(f"   ... and {len(cleared_items) - 10} more")
    
    print(f"\n🚀 NOW RESTART YOUR BOT - CACHE IS COMPLETELY CLEARED!")

if __name__ == "__main__":
    nuclear_cache_clear()
