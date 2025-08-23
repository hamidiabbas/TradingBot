#!/usr/bin/env python3
"""
Debug Strategy Loading Process - FIXED VERSION
Let's see exactly what's happening
"""

import os
import sys
import importlib
import importlib.util  # THIS WAS MISSING!
import inspect
from pathlib import Path

def debug_strategy_loading():
    """Debug the exact loading process"""
    
    strategies_path = Path("strategies")
    
    print("🔍 DEBUGGING STRATEGY LOADING PROCESS")
    print("=" * 60)
    
    # Step 1: Check if strategies folder exists
    print(f"📁 Strategies folder exists: {strategies_path.exists()}")
    
    if not strategies_path.exists():
        print("❌ Strategies folder not found!")
        return
    
    # Step 2: List all files in strategies folder
    all_files = list(strategies_path.glob("*"))
    python_files = [f for f in strategies_path.glob("*.py") 
                   if not f.name.startswith("_") 
                   and f.name not in ["unified_signals.py", "numpy_compatibility.py"]]
    
    print(f"📂 Total files in strategies/: {len(all_files)}")
    print(f"📄 Python files to process: {len(python_files)}")
    
    for f in python_files:
        print(f"   📄 {f.name}")
    
    print("\n" + "=" * 60)
    
    # Step 3: Try to import each file
    print("🔍 ATTEMPTING TO IMPORT EACH STRATEGY FILE:")
    print("-" * 60)
    
    # Add strategies to path
    if str(strategies_path) not in sys.path:
        sys.path.append(str(strategies_path))
    
    successful_imports = []
    failed_imports = []
    
    for strategy_file in python_files:
        print(f"\n📄 Processing: {strategy_file.name}")
        
        try:
            # Import strategy module
            module_name = strategy_file.stem
            print(f"   🔍 Attempting to import module: {module_name}")
            
            # Method 1: importlib with spec (same as signal_factory.py)
            spec = importlib.util.spec_from_file_location(module_name, strategy_file)
            if spec is None:
                print(f"   ❌ Could not create spec for {module_name}")
                failed_imports.append((strategy_file.name, "Could not create spec"))
                continue
                
            module = importlib.util.module_from_spec(spec)
            if module is None:
                print(f"   ❌ Could not create module for {module_name}")
                failed_imports.append((strategy_file.name, "Could not create module"))
                continue
                
            print(f"   ✅ Spec and module created successfully")
            
            # Execute module
            spec.loader.exec_module(module)
            print(f"   ✅ Module executed successfully")
                
        except Exception as import_error:
            print(f"   ❌ Import failed: {import_error}")
            print(f"   📄 Error details: {type(import_error).__name__}: {str(import_error)}")
            
            # Try to show the problematic line
            if hasattr(import_error, 'lineno'):
                print(f"   📍 Error at line: {import_error.lineno}")
            
            failed_imports.append((strategy_file.name, str(import_error)))
            continue
        
        # Step 4: Look for strategy classes
        print(f"   🔍 Looking for strategy classes in {module_name}...")
        
        found_classes = []
        all_members = inspect.getmembers(module, inspect.isclass)
        
        print(f"   📊 Total classes found: {len(all_members)}")
        
        for name, obj in all_members:
            print(f"     🔍 Checking class: {name}")
            
            # Check if it has analyze method
            has_analyze = hasattr(obj, 'analyze')
            is_strategy_class = 'strategy' in name.lower()
            not_private = not name.startswith('_')
            
            print(f"       - Has analyze method: {has_analyze}")
            print(f"       - Name contains 'strategy': {is_strategy_class}")
            print(f"       - Not private: {not_private}")
            
            if has_analyze and not_private and is_strategy_class:
                print(f"     ✅ VALID STRATEGY CLASS: {name}")
                
                # Try to instantiate
                try:
                    strategy_instance = obj()
                    print(f"     ✅ Successfully instantiated {name}")
                    found_classes.append(name)
                    
                    # Test analyze method
                    import pandas as pd
                    import numpy as np
                    
                    # Create test data
                    test_data = pd.DataFrame({
                        'open': [1.1000] * 50,
                        'high': [1.1010] * 50,
                        'low': [1.0990] * 50,
                        'close': [1.1000] * 50,
                        'tick_volume': [100] * 50
                    })
                    
                    result = strategy_instance.analyze(test_data, "EURUSD")
                    print(f"     ✅ Analyze method works: {result.get('signal', 'Unknown')}")
                    
                except Exception as inst_error:
                    print(f"     ❌ Could not instantiate {name}: {inst_error}")
                    print(f"     📄 Instantiation error: {type(inst_error).__name__}")
            else:
                reason = []
                if not has_analyze: reason.append("no analyze method")
                if not is_strategy_class: reason.append("name doesn't contain 'strategy'")
                if not not_private: reason.append("private class")
                print(f"     ❌ Not valid: {', '.join(reason)}")
        
        if found_classes:
            successful_imports.append((strategy_file.name, found_classes))
            print(f"   ✅ SUCCESS: Found {len(found_classes)} strategy classes")
        else:
            failed_imports.append((strategy_file.name, "No valid strategy classes found"))
            print(f"   ❌ FAILED: No valid strategy classes found")
    
    # Step 5: Summary
    print("\n" + "=" * 60)
    print("📊 LOADING SUMMARY:")
    print("=" * 60)
    
    print(f"✅ Successful imports: {len(successful_imports)}")
    for filename, classes in successful_imports:
        print(f"   📄 {filename}: {', '.join(classes)}")
    
    print(f"\n❌ Failed imports: {len(failed_imports)}")
    for filename, error in failed_imports:
        print(f"   📄 {filename}: {error}")
    
    total_files = len(successful_imports) + len(failed_imports)
    success_rate = len(successful_imports) / total_files * 100 if total_files > 0 else 0
    print(f"\n📈 Success Rate: {success_rate:.1f}%")

if __name__ == "__main__":
    debug_strategy_loading()
