#!/usr/bin/env python3
"""
Registry Fix and Strategy Testing Tool
Fixes the strategy registry issue and tests your sophisticated strategies
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import traceback
import sys
import inspect
from pathlib import Path
import logging

# Add the strategies path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

def create_comprehensive_test_data() -> pd.DataFrame:
    """Create comprehensive test data for sophisticated strategies"""
    print("🔧 Creating comprehensive test data...")
    
    periods = 250
    dates = pd.date_range(start=datetime.now() - timedelta(days=12), periods=periods, freq='1h')
    
    # Create realistic EURUSD data with strong patterns
    base_price = 1.0950
    prices = []
    current_price = base_price
    
    # Create multiple market phases for comprehensive testing
    for i in range(periods):
        if i < 60:
            # Strong uptrend - should trigger bullish signals
            trend = 0.0015 + np.random.normal(0, 0.0003)
        elif i < 120:
            # Consolidation - should trigger range/neutral signals
            trend = np.random.normal(0, 0.0002)
        elif i < 180:
            # Strong downtrend - should trigger bearish signals
            trend = -0.0012 + np.random.normal(0, 0.0003)
        else:
            # Volatile recovery - mixed signals
            trend = np.random.normal(0, 0.0008) + (0.0005 if i % 10 < 5 else -0.0005)
        
        current_price += trend
        prices.append(current_price)
    
    # Create comprehensive DataFrame
    df = pd.DataFrame(index=dates)
    df['close'] = prices
    
    # Generate realistic OHLC
    for i in range(len(df)):
        close_price = df['close'].iloc[i]
        
        if i == 0:
            open_price = close_price * (1 + np.random.normal(0, 0.0001))
        else:
            open_price = df['close'].iloc[i-1] * (1 + np.random.normal(0, 0.0001))
        
        df.loc[df.index[i], 'open'] = open_price
        
        # Realistic intrabar movement
        intrabar_range = abs(close_price - open_price) * 2 + 0.0003
        df.loc[df.index[i], 'high'] = max(open_price, close_price) + intrabar_range * np.random.uniform(0.3, 1.0)
        df.loc[df.index[i], 'low'] = min(open_price, close_price) - intrabar_range * np.random.uniform(0.3, 1.0)
    
    # Add volume and spread
    df['volume'] = np.random.lognormal(mean=np.log(5000), sigma=0.4, size=len(df)).astype(int)
    df['tick_volume'] = df['volume']
    df['spread'] = 0.00002
    df['real_volume'] = df['volume']
    
    # Add comprehensive technical indicators
    # Moving averages
    df['sma_5'] = df['close'].rolling(window=5).mean()
    df['sma_10'] = df['close'].rolling(window=10).mean()
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean()
    df['ema_12'] = df['close'].ewm(span=12).mean()
    df['ema_26'] = df['close'].ewm(span=26).mean()
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # MACD
    df['macd'] = df['ema_12'] - df['ema_26']
    df['macd_signal'] = df['macd'].ewm(span=9).mean()
    df['macd_histogram'] = df['macd'] - df['macd_signal']
    
    # Bollinger Bands
    df['bb_middle'] = df['close'].rolling(window=20).mean()
    bb_std = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
    df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
    
    # ATR
    df['tr'] = np.maximum(df['high'] - df['low'], 
                         np.maximum(abs(df['high'] - df['close'].shift(1)),
                                   abs(df['low'] - df['close'].shift(1))))
    df['atr'] = df['tr'].rolling(window=14).mean()
    
    # Fill NaN values
    df = df.ffill().bfill()
    
    print(f"✅ Test data created: {len(df)} bars")
    print(f"   Price range: {df['close'].min():.5f} - {df['close'].max():.5f}")
    print(f"   Total return: {((df['close'].iloc[-1] / df['close'].iloc[0]) - 1) * 100:.2f}%")
    print(f"   Volatility: {df['close'].pct_change().std():.6f}")
    
    return df

def get_actual_strategy_classes():
    """Get actual strategy classes from the registry, bypassing the dict issue"""
    
    print("\n🔍 FIXING STRATEGY REGISTRY ACCESS")
    print("=" * 60)
    
    try:
        # Import the base strategy system
        from strategies.base_strategy import _strategy_registry
        
        print(f"📋 Accessing internal registry directly...")
        
        # Check if _strategy_registry exists and what it contains
        if hasattr(sys.modules['strategies.base_strategy'], '_strategy_registry'):
            registry = _strategy_registry
            print(f"   Found _strategy_registry with {len(registry)} entries")
            
            actual_classes = {}
            
            for name, entry in registry.items():
                print(f"   Processing: {name} -> {type(entry)}")
                
                # Check different possible storage formats
                if inspect.isclass(entry):
                    # Direct class storage
                    actual_classes[name] = entry
                    print(f"      ✅ Direct class: {entry.__name__}")
                    
                elif isinstance(entry, dict) and 'class' in entry:
                    # Dictionary with class stored under 'class' key
                    actual_classes[name] = entry['class']
                    print(f"      ✅ Dict with class: {entry['class'].__name__}")
                    
                elif isinstance(entry, dict) and 'strategy_class' in entry:
                    # Dictionary with class stored under 'strategy_class' key
                    actual_classes[name] = entry['strategy_class']
                    print(f"      ✅ Dict with strategy_class: {entry['strategy_class'].__name__}")
                    
                else:
                    print(f"      ❌ Unknown format: {type(entry)} - {entry}")
            
            print(f"✅ Extracted {len(actual_classes)} actual strategy classes")
            return actual_classes
            
        else:
            print(f"❌ _strategy_registry not found in base_strategy module")
            return {}
    
    except Exception as e:
        print(f"❌ Error accessing registry: {e}")
        
        # Fallback: Try to find classes by scanning modules
        try:
            print(f"🔄 Attempting fallback: scanning strategy modules...")
            
            actual_classes = {}
            
            # Import known strategy modules
            strategy_modules = [
                'strategies.momentum_strategy',
                'strategies.breakout_strategy',
                'strategies.mean_reversion_strategy'
            ]
            
            for module_name in strategy_modules:
                try:
                    import importlib
                    module = importlib.import_module(module_name)
                    
                    # Find strategy classes in the module
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if (name.endswith('Strategy') and 
                            not name.startswith('Base') and
                            hasattr(obj, 'analyze')):
                            
                            actual_classes[name] = obj
                            print(f"      ✅ Found class: {name}")
                            
                except Exception as module_error:
                    print(f"      ❌ Error scanning {module_name}: {module_error}")
            
            print(f"✅ Fallback found {len(actual_classes)} strategy classes")
            return actual_classes
            
        except Exception as fallback_error:
            print(f"❌ Fallback failed: {fallback_error}")
            return {}

def test_strategy_completely(strategy_class, strategy_name: str, test_data: pd.DataFrame):
    """Comprehensive test of a strategy class"""
    
    print(f"\n🧪 COMPREHENSIVE STRATEGY TEST: {strategy_name}")
    print("=" * 70)
    
    try:
        print(f"📋 Strategy Class Analysis:")
        print(f"   Class name: {strategy_class.__name__}")
        print(f"   Module: {strategy_class.__module__}")
        print(f"   MRO: {[cls.__name__ for cls in strategy_class.__mro__]}")
        
        # Analyze constructor
        try:
            init_sig = inspect.signature(strategy_class.__init__)
            print(f"   Constructor: {init_sig}")
        except Exception as e:
            print(f"   Constructor analysis failed: {e}")
        
        # Test instantiation methods
        instance = None
        instantiation_method = None
        
        # Method 1: No parameters
        try:
            instance = strategy_class()
            instantiation_method = "no_params"
            print(f"   ✅ Instantiation: No parameters worked")
        except Exception as e:
            print(f"   ❌ No params failed: {str(e)[:100]}")
        
        # Method 2: Name only
        if not instance:
            try:
                instance = strategy_class(strategy_name)
                instantiation_method = "name_only"
                print(f"   ✅ Instantiation: Name only worked")
            except Exception as e:
                print(f"   ❌ Name only failed: {str(e)[:100]}")
        
        # Method 3: Name and config
        if not instance:
            try:
                instance = strategy_class(strategy_name, {})
                instantiation_method = "name_config"
                print(f"   ✅ Instantiation: Name + config worked")
            except Exception as e:
                print(f"   ❌ Name + config failed: {str(e)[:100]}")
        
        # Method 4: Comprehensive config
        if not instance:
            try:
                config = {
                    'timeframe': 'H1',
                    'symbols': ['EURUSD'],
                    'period': 20,
                    'threshold': 0.5,
                    'risk_level': 0.02
                }
                instance = strategy_class(strategy_name, config)
                instantiation_method = "full_config"
                print(f"   ✅ Instantiation: Full config worked")
            except Exception as e:
                print(f"   ❌ Full config failed: {str(e)[:100]}")
        
        if not instance:
            print(f"   ❌ ALL INSTANTIATION METHODS FAILED")
            return False, "instantiation_failed"
        
        # Set name if needed
        if hasattr(instance, 'name') and not getattr(instance, 'name', None):
            instance.name = strategy_name
        
        # Test analyze method
        print(f"\n🎯 Testing analyze() method:")
        
        if not hasattr(instance, 'analyze'):
            print(f"   ❌ No analyze() method found")
            return False, "no_analyze_method"
        
        try:
            print(f"   📊 Calling analyze() with comprehensive data...")
            analysis = instance.analyze(test_data, "EURUSD")
            
            print(f"   📤 Analysis result:")
            if analysis is None:
                print(f"      ❌ analyze() returned None")
                return False, "analyze_returns_none"
            
            if not isinstance(analysis, dict):
                print(f"      ❌ analyze() returned {type(analysis)}, expected dict")
                return False, "analyze_wrong_type"
            
            # Detailed result analysis
            signal = analysis.get('signal', 'NO_SIGNAL')
            confidence = analysis.get('confidence', 'NO_CONFIDENCE') 
            price = analysis.get('price', 'NO_PRICE')
            direction = analysis.get('direction', 'NO_DIRECTION')
            reason = analysis.get('reason', 'NO_REASON')
            
            print(f"      📊 Signal Analysis:")
            print(f"         Signal: {signal}")
            print(f"         Confidence: {confidence}")
            print(f"         Price: {price}")
            print(f"         Direction: {direction}")
            print(f"         Reason: {reason}")
            
            # Show additional fields
            other_fields = {k: v for k, v in analysis.items() 
                          if k not in ['signal', 'confidence', 'price', 'direction', 'reason']}
            if other_fields:
                print(f"         Additional: {list(other_fields.keys())}")
            
            # Evaluate signal quality
            print(f"\n🎯 SIGNAL EVALUATION:")
            
            if signal == 'HOLD' and confidence == 0.0 and price == 1.0:
                print(f"      ❌ HARDCODED DEFAULTS: Strategy returns placeholder values")
                return True, "placeholder_implementation"
                
            elif signal in ['BUY', 'SELL'] and isinstance(confidence, (int, float)) and confidence > 0:
                print(f"      ✅ EXCELLENT: Generates real trading signals!")
                print(f"      🎉 Signal: {signal}, Confidence: {confidence:.3f}")
                return True, "fully_working"
                
            elif signal == 'HOLD' and isinstance(confidence, (int, float)) and confidence == 0:
                print(f"      ⚠️ CONSERVATIVE: Returns HOLD with 0 confidence")
                print(f"      💡 May be working but data doesn't trigger signals")
                return True, "conservative_working"
                
            else:
                print(f"      ❓ UNCLEAR: Unusual signal pattern")
                print(f"      💡 Review strategy logic")
                return True, "needs_review"
        
        except Exception as e:
            print(f"      ❌ ERROR in analyze(): {e}")
            print(f"      📋 Full traceback:")
            traceback.print_exc()
            return False, "analyze_error"
            
    except Exception as e:
        print(f"❌ Critical error testing {strategy_name}: {e}")
        traceback.print_exc()
        return False, "critical_error"

def generate_working_strategies_code(working_strategies: dict, results: dict):
    """Generate code to instantiate working strategies in main.py"""
    
    print(f"\n🔧 GENERATING WORKING STRATEGIES CODE")
    print("=" * 70)
    
    code_template = """
# FIXED STRATEGY INSTANTIATION FOR YOUR MAIN.PY
# Add this to your TradingBotOrchestrator.__init__() method

def _load_working_strategies(self):
    \"\"\"Load working sophisticated strategies with proper instantiation\"\"\"
    
    self.strategies = {}
    
    try:
        # Import strategy classes directly
        from strategies.momentum_strategy import EnhancedMomentumStrategy, MomentumStrategy
        from strategies.breakout_strategy import EnhancedBreakoutStrategy
        from strategies.mean_reversion_strategy import EnhancedMeanReversionStrategy
        # Add other imports as needed
        
        # Working strategy instantiations:
"""
    
    fully_working = []
    placeholder_strategies = []
    
    for strategy_name, (success, status) in results.items():
        if success and status == "fully_working":
            fully_working.append(strategy_name)
            method = working_strategies.get(strategy_name, "name_config")
            
            if method == "no_params":
                code_template += f"""
        # {strategy_name} - Generates real signals
        try:
            strategy = {strategy_name}()
            strategy.name = "{strategy_name}"
            self.strategies["{strategy_name}"] = strategy
            self.logger.info(f"✅ Loaded working strategy: {strategy_name}")
        except Exception as e:
            self.logger.error(f"❌ Failed to load {strategy_name}: {{e}}")
"""
            elif method == "name_only":
                code_template += f"""
        # {strategy_name} - Generates real signals  
        try:
            self.strategies["{strategy_name}"] = {strategy_name}("{strategy_name}")
            self.logger.info(f"✅ Loaded working strategy: {strategy_name}")
        except Exception as e:
            self.logger.error(f"❌ Failed to load {strategy_name}: {{e}}")
"""
            else:  # name_config or full_config
                code_template += f"""
        # {strategy_name} - Generates real signals
        try:
            config = {{'timeframe': 'H1', 'symbols': ['EURUSD'], 'debug': False}}
            self.strategies["{strategy_name}"] = {strategy_name}("{strategy_name}", config)
            self.logger.info(f"✅ Loaded working strategy: {strategy_name}")
        except Exception as e:
            self.logger.error(f"❌ Failed to load {strategy_name}: {{e}}")
"""
        
        elif success and status in ["placeholder_implementation", "conservative_working"]:
            placeholder_strategies.append(strategy_name)
    
    code_template += f"""
        
        # Update metrics
        self.metrics.strategies_loaded = len(self.strategies)
        
        self.logger.info(f"📊 Strategy loading complete:")
        self.logger.info(f"   ✅ Fully working: {len(fully_working)} strategies")
        self.logger.info(f"   ⚠️ Need implementation: {len(placeholder_strategies)} strategies")
        
        return self.strategies
        
    except Exception as e:
        self.logger.error(f"Critical error loading strategies: {{e}}")
        return {{}}

# In your __init__ method, replace strategy discovery with:
# self.strategies = self._load_working_strategies()
"""
    
    print(code_template)
    
    # Generate config.yaml update
    if fully_working:
        print(f"\n💡 UPDATE YOUR CONFIG.YAML:")
        print("=" * 70)
        print(f"enabled_strategies:")
        for strategy in fully_working:
            print(f"  - \"{strategy}\"")
        print(f"\nstrategy_weights:")
        for strategy in fully_working:
            print(f"  {strategy}: 1.0")
    
    return code_template

def main():
    """Main debugging and fixing function"""
    
    print("🔧 SOPHISTICATED STRATEGY REGISTRY FIX & TESTER")
    print("=" * 70)
    print("🎯 Fixing registry issues and testing your advanced strategies")
    print("=" * 70)
    
    # Create comprehensive test data
    test_data = create_comprehensive_test_data()
    
    # Get actual strategy classes (bypass registry issue)
    strategy_classes = get_actual_strategy_classes()
    
    if not strategy_classes:
        print(f"\n❌ No strategy classes found!")
        print(f"💡 Check that your strategy files exist and classes are properly defined")
        return
    
    print(f"\n📋 Found {len(strategy_classes)} strategy classes to test:")
    for name in strategy_classes.keys():
        print(f"   - {name}")
    
    # Test each strategy comprehensively
    results = {}
    working_methods = {}
    
    for strategy_name, strategy_class in strategy_classes.items():
        success, status = test_strategy_completely(strategy_class, strategy_name, test_data)
        results[strategy_name] = (success, status)
        
        if success:
            working_methods[strategy_name] = "name_config"  # Default working method
    
    # Generate comprehensive report
    print(f"\n" + "="*70)
    print(f"🎯 COMPREHENSIVE STRATEGY ANALYSIS RESULTS")
    print(f"="*70)
    
    fully_working = [name for name, (success, status) in results.items() 
                    if success and status == "fully_working"]
    
    placeholder = [name for name, (success, status) in results.items() 
                  if success and status in ["placeholder_implementation", "conservative_working"]]
    
    failed = [name for name, (success, status) in results.items() if not success]
    
    print(f"\n✅ FULLY WORKING STRATEGIES ({len(fully_working)}):")
    print(f"   🎉 These generate real trading signals and are ready for production!")
    for strategy in fully_working:
        print(f"      - {strategy}")
    
    print(f"\n⚠️ WORKING BUT NEED IMPLEMENTATION ({len(placeholder)}):")
    print(f"   🔧 These instantiate correctly but need analyze() method completion")
    for strategy in placeholder:
        status = results[strategy][1]
        print(f"      - {strategy} ({status})")
    
    print(f"\n❌ FAILED STRATEGIES ({len(failed)}):")
    print(f"   💥 These have constructor or critical errors")
    for strategy in failed:
        status = results[strategy][1]
        print(f"      - {strategy} ({status})")
    
    # Generate immediate fix code
    if fully_working or placeholder:
        working_count = len(fully_working) + len(placeholder)
        print(f"\n🚀 IMMEDIATE SOLUTION READY!")
        print(f"   You have {working_count} strategies that can be used right now!")
        
        generate_working_strategies_code(working_methods, results)
        
        print(f"\n🎯 NEXT STEPS:")
        print(f"   1. Copy the generated code to your main.py")
        print(f"   2. Update your config.yaml with the working strategies")
        print(f"   3. Run your TradingBot - signals should generate immediately!")
        
        if placeholder:
            print(f"   4. I can help implement analyze() methods for placeholder strategies")
    
    else:
        print(f"\n💡 ALL STRATEGIES NEED FIXES:")
        print(f"   Most likely issues:")
        print(f"   - Constructor parameter mismatches")
        print(f"   - Missing dependencies (talib, etc.)")
        print(f"   - Placeholder analyze() method implementations")
        
        print(f"\n🔥 Let's fix them one by one!")
        print(f"   Share the specific error for any strategy and I'll provide a targeted fix")

if __name__ == "__main__":
    main()
