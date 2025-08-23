# strategy_debugger.py - FIXED VERSION WITH PROPER PATH HANDLING
import pandas as pd
import numpy as np
from pathlib import Path
import importlib.util
import inspect
import sys
import os

class StrategyDebugger:
    """Debug individual strategies with proper path management"""
    
    def __init__(self):
        self.test_data = self._create_test_data()
        self.results = {}
        
        # CRITICAL FIX: Add strategies directory to Python path
        self.strategies_dir = Path("strategies")
        if self.strategies_dir.exists():
            strategies_path = str(self.strategies_dir.absolute())
            if strategies_path not in sys.path:
                sys.path.insert(0, strategies_path)
                print(f"✅ Added to Python path: {strategies_path}")
        
        # Also add current directory
        current_dir = str(Path.cwd())
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
            print(f"✅ Added current directory to Python path: {current_dir}")
    
    def _create_test_data(self):
        """Create comprehensive test data that should trigger signals"""
        # Create multiple market scenarios
        scenarios = {}
        
        # Scenario 1: Strong uptrend (should trigger momentum/trend strategies)
        dates = pd.date_range('2024-01-01', periods=100, freq='1h')
        uptrend_data = pd.DataFrame({
            'open': 1.1000 + np.cumsum(np.random.randn(100) * 0.0005 + 0.0002),
            'high': 1.1000 + np.cumsum(np.random.randn(100) * 0.0005 + 0.0002) + 0.0010,
            'low': 1.1000 + np.cumsum(np.random.randn(100) * 0.0005 + 0.0002) - 0.0005,
            'close': 1.1000 + np.cumsum(np.random.randn(100) * 0.0005 + 0.0002),
            'volume': np.random.randint(1000, 5000, 100)
        }, index=dates)
        scenarios['uptrend'] = uptrend_data
        
        # Scenario 2: Range-bound (should trigger grid/mean reversion)
        range_base = 1.1000
        range_data = pd.DataFrame({
            'open': range_base + np.sin(np.arange(100) * 0.2) * 0.001,
            'high': range_base + np.sin(np.arange(100) * 0.2) * 0.001 + 0.0008,
            'low': range_base + np.sin(np.arange(100) * 0.2) * 0.001 - 0.0008,
            'close': range_base + np.sin(np.arange(100) * 0.2) * 0.001,
            'volume': np.random.randint(800, 3000, 100)
        }, index=dates)
        scenarios['ranging'] = range_data
        
        # Scenario 3: Volatile breakout (should trigger breakout strategies)
        breakout_data = uptrend_data.copy()
        breakout_data.loc[breakout_data.index[80:], 'close'] += 0.005
        breakout_data.loc[breakout_data.index[80:], 'high'] += 0.006
        scenarios['breakout'] = breakout_data
        
        return scenarios
    
    def _load_strategy_module(self, strategy_file):
        """Load strategy module with proper path handling"""
        try:
            module_name = strategy_file.stem
            
            # Use absolute path for the module
            module_path = strategy_file.absolute()
            
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if spec is None:
                print(f"   ❌ Could not create spec for {strategy_file.name}")
                return None
            
            module = importlib.util.module_from_spec(spec)
            
            # CRITICAL: Add to sys.modules before execution to handle internal imports
            sys.modules[module_name] = module
            
            # Execute the module
            spec.loader.exec_module(module)
            
            return module
            
        except ImportError as e:
            print(f"   ❌ Import error in {strategy_file.name}: {e}")
            return None
        except Exception as e:
            print(f"   ❌ Error loading module {strategy_file.name}: {e}")
            return None
    
    def _find_strategy_classes(self, strategy_module):
        """Find strategy classes in the loaded module"""
        strategy_instances = []
        
        if not strategy_module:
            return strategy_instances
        
        try:
            # Look for classes that might be strategies
            for name, obj in inspect.getmembers(strategy_module, inspect.isclass):
                # Skip private classes, base classes, and imports
                if (name.startswith('_') or 
                    name in ['BaseStrategy', 'SignalEvent', 'TradeSetup', 'StrategyState'] or
                    obj.__module__ != strategy_module.__name__):
                    continue
                
                # Look for strategy-like classes
                if (hasattr(obj, 'analyze') or 
                    'strategy' in name.lower() or 
                    'Strategy' in name):
                    
                    try:
                        # Try different instantiation methods
                        instance = None
                        
                        # Method 1: No arguments
                        try:
                            instance = obj()
                        except TypeError:
                            # Method 2: Empty dict config
                            try:
                                instance = obj({})
                            except TypeError:
                                # Method 3: Name and config
                                try:
                                    instance = obj(name=name, config={})
                                except:
                                    # Method 4: Just name
                                    try:
                                        instance = obj(name)
                                    except:
                                        continue
                        
                        if instance:
                            strategy_instances.append((name, instance))
                            print(f"   ✅ Found strategy class: {name}")
                        
                    except Exception as e:
                        print(f"   ⚠️ Could not instantiate {name}: {e}")
            
        except Exception as e:
            print(f"   ❌ Error finding strategy classes: {e}")
        
        return strategy_instances
    
    def debug_strategy(self, strategy_file):
        """Debug a single strategy file"""
        print(f"\n🔍 DEBUGGING: {strategy_file.name}")
        print("="*50)
        
        try:
            # Load strategy
            strategy_module = self._load_strategy_module(strategy_file)
            
            if strategy_module is None:
                return False
                
            strategy_instances = self._find_strategy_classes(strategy_module)
            
            if not strategy_instances:
                print(f"❌ No strategy classes found in {strategy_file.name}")
                return False
            
            total_working = 0
            
            for strategy_name, strategy_instance in strategy_instances:
                print(f"\n📊 Testing {strategy_name}...")
                
                total_signals = 0
                scenario_results = {}
                
                # Test each scenario
                for scenario_name, test_data in self.test_data.items():
                    signals = self._test_strategy_with_data(
                        strategy_instance, test_data, scenario_name
                    )
                    scenario_results[scenario_name] = signals
                    total_signals += len(signals)
                    
                    print(f"   {scenario_name}: {len(signals)} signals")
                
                # Analyze results
                if total_signals > 0:
                    print(f"✅ {strategy_name}: {total_signals} total signals generated")
                    self.results[strategy_name] = {
                        'status': 'working',
                        'total_signals': total_signals,
                        'scenarios': scenario_results
                    }
                    total_working += 1
                else:
                    print(f"❌ {strategy_name}: NO SIGNALS GENERATED")
                    print(f"   🔧 NEEDS FIXING")
                    self.results[strategy_name] = {
                        'status': 'broken',
                        'total_signals': 0,
                        'scenarios': scenario_results
                    }
                    
                    # Provide debugging suggestions
                    self._suggest_fixes(strategy_instance, strategy_name)
            
            return total_working > 0
            
        except Exception as e:
            print(f"❌ CRITICAL ERROR loading {strategy_file.name}: {e}")
            return False
    
    def _test_strategy_with_data(self, strategy, data, scenario):
        """Test strategy with specific data scenario"""
        signals = []
        try:
            # Test the analyze method with different interfaces
            result = None
            
            # Try different method signatures
            try:
                # Most common: analyze(data, symbol)
                result = strategy.analyze(data, 'EURUSD')
            except TypeError:
                try:
                    # Alternative: analyze(data)
                    result = strategy.analyze(data)
                except TypeError:
                    try:
                        # Alternative: generate_signals
                        if hasattr(strategy, 'generate_signals'):
                            result = strategy.generate_signals({'EURUSD': data})
                    except:
                        pass
            except Exception as e:
                print(f"     ⚠️ Strategy error in {scenario}: {e}")
                return signals
            
            # Process result
            if result:
                if isinstance(result, dict):
                    signal_type = result.get('signal', 'HOLD')
                    if signal_type in ['BUY', 'SELL', 'STRONG_BUY', 'STRONG_SELL']:
                        signals.append(result)
                elif isinstance(result, list):
                    for item in result:
                        if isinstance(item, dict) and item.get('signal') in ['BUY', 'SELL']:
                            signals.append(item)
            
        except Exception as e:
            print(f"     ⚠️ Critical error in {scenario}: {e}")
        
        return signals
    
    def _suggest_fixes(self, strategy, strategy_name):
        """Suggest fixes for broken strategies"""
        print(f"\n💡 SUGGESTED FIXES for {strategy_name}:")
        
        # Check method signature
        if hasattr(strategy, 'analyze'):
            try:
                sig = inspect.signature(strategy.analyze)
                params = list(sig.parameters.keys())
                print(f"   📝 Method signature: analyze({', '.join(params)})")
                
                if len(params) < 2:
                    print(f"   🔧 FIX: Add symbol parameter - def analyze(self, data, symbol='EURUSD')")
            except:
                print(f"   📝 Method signature: Could not inspect")
        else:
            print(f"   🔧 FIX: Add analyze method - def analyze(self, data, symbol='EURUSD')")
        
        # Standard fixes
        print(f"   🔧 FIX: Ensure returns dict with 'signal', 'confidence', 'price' keys")
        print(f"   🔧 FIX: Signal must be 'BUY' or 'SELL', confidence > 0.0")
        print(f"   🔧 FIX: Add data validation at start of analyze method")
        print(f"   🔧 FIX: Wrap calculations in try/except blocks")

def debug_all_strategies():
    """Debug all strategy files with improved path handling"""
    print(f"🔍 DEBUGGING STRATEGY FILES WITH PROPER PATH HANDLING")
    print("="*70)
    
    debugger = StrategyDebugger()
    strategies_dir = Path("strategies")
    
    if not strategies_dir.exists():
        print("❌ Strategies folder not found!")
        return
    
    # Filter strategy files
    strategy_files = []
    for f in strategies_dir.glob("*.py"):
        if (not f.name.startswith("_") and 
            f.stem not in ['base_strategy', 'unified_signals', '__pycache__', 
                          'utils', '__init__', 'compatibility', 'numpy_compatibility',
                          'smc_indicators', 'strategy_lock', 'technical_indicators']):
            strategy_files.append(f)
    
    print(f"📁 Found {len(strategy_files)} strategy files to test")
    
    working_strategies = []
    broken_strategies = []
    
    for strategy_file in strategy_files:
        is_working = debugger.debug_strategy(strategy_file)
        if is_working:
            working_strategies.append(strategy_file.stem)
        else:
            broken_strategies.append(strategy_file.stem)
    
    # Enhanced Summary
    print(f"\n📊 COMPREHENSIVE DEBUGGING SUMMARY:")
    print(f"   ✅ Working: {len(working_strategies)} strategies")
    print(f"   ❌ Broken: {len(broken_strategies)} strategies")
    print(f"   📊 Success Rate: {len(working_strategies)}/{len(strategy_files)} ({len(working_strategies)/len(strategy_files)*100:.1f}%)")
    print(f"   🎯 Target: 15+ working strategies for profitable trading")
    
    if working_strategies:
        print(f"\n✅ WORKING STRATEGIES:")
        for i, strategy in enumerate(working_strategies, 1):
            print(f"   {i}. {strategy}")
    
    if broken_strategies:
        print(f"\n❌ BROKEN STRATEGIES (need fixing):")
        for i, strategy in enumerate(broken_strategies, 1):
            print(f"   {i}. {strategy}")
        
        print(f"\n🔧 NEXT STEPS:")
        print(f"   1. Fix import errors first (base_strategy issues)")
        print(f"   2. Fix signal generation logic")
        print(f"   3. Test individual strategies")
        print(f"   4. Integrate with signal factory")
    
    return debugger.results

if __name__ == "__main__":
    debug_all_strategies()
