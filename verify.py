#!/usr/bin/env python3
"""
Strategy Differentiation Validator
Checks if strategies are actually different
"""

def investigate_identical_results():
    """Investigate why strategies have identical results"""
    
    print("🔍 INVESTIGATING IDENTICAL STRATEGY RESULTS")
    print("="*60)
    
    # Import your signal factory
    try:
        from signal_factory import get_signal_factory
        
        factory = get_signal_factory()
        factory.initialize()
        
        # Get the specific strategies
        ict_strategy = None
        indicator_strategy = None
        
        # Look in rule-based strategies
        for name, strategy in factory.rule_based_strategies.items():
            if 'ICTStrategy' in name and 'Enhanced' not in name:
                ict_strategy = strategy
                print(f"✅ Found ICTStrategy: {name}")
            elif 'EnhancedIndicatorSuiteStrategy' in name:
                indicator_strategy = strategy  
                print(f"✅ Found EnhancedIndicatorSuiteStrategy: {name}")
        
        if not ict_strategy or not indicator_strategy:
            print("❌ Could not find both strategies")
            return False
        
        # Test 1: Check if they're the same object
        if ict_strategy is indicator_strategy:
            print("🚨 CRITICAL: Both strategies are the SAME OBJECT!")
            return False
        
        # Test 2: Check class names
        ict_class = ict_strategy.__class__.__name__
        indicator_class = indicator_strategy.__class__.__name__
        
        print(f"\n📊 CLASS ANALYSIS:")
        print(f"   ICTStrategy class: {ict_class}")
        print(f"   IndicatorSuite class: {indicator_class}")
        
        if ict_class == indicator_class:
            print("🚨 CRITICAL: Both strategies use the SAME CLASS!")
            return False
        
        # Test 3: Check method signatures
        ict_methods = [method for method in dir(ict_strategy) if not method.startswith('_')]
        indicator_methods = [method for method in dir(indicator_strategy) if not method.startswith('_')]
        
        common_methods = set(ict_methods) & set(indicator_methods)
        unique_ict = set(ict_methods) - set(indicator_methods)
        unique_indicator = set(indicator_methods) - set(ict_methods)
        
        print(f"\n🔧 METHOD ANALYSIS:")
        print(f"   Common methods: {len(common_methods)}")
        print(f"   ICT unique methods: {len(unique_ict)}")
        print(f"   Indicator unique methods: {len(unique_indicator)}")
        
        if len(unique_ict) == 0 and len(unique_indicator) == 0:
            print("🚨 CRITICAL: Strategies have IDENTICAL METHODS!")
            return False
        
        # Test 4: Quick signal generation test
        print(f"\n🧪 SIGNAL GENERATION TEST:")
        
        # Create dummy data
        import pandas as pd
        import numpy as np
        
        dates = pd.date_range('2024-01-01', periods=100, freq='H')
        dummy_data = pd.DataFrame({
            'open': np.random.uniform(1.1000, 1.1100, 100),
            'high': np.random.uniform(1.1050, 1.1150, 100),
            'low': np.random.uniform(0.9950, 1.0950, 100),
            'close': np.random.uniform(1.1000, 1.1100, 100),
            'tick_volume': np.random.randint(100, 1000, 100)
        }, index=dates)
        
        # Test signals from both strategies
        try:
            ict_signal = ict_strategy.analyze(dummy_data, 'EURUSD')
            indicator_signal = indicator_strategy.analyze(dummy_data, 'EURUSD')
            
            print(f"   ICT signal: {ict_signal}")
            print(f"   Indicator signal: {indicator_signal}")
            
            if ict_signal == indicator_signal:
                print("🚨 CRITICAL: Strategies produce IDENTICAL SIGNALS!")
                print("   This confirms they're using the same logic")
                return False
            else:
                print("✅ Strategies produce different signals - implementation may be OK")
                print("   Problem might be in backtesting execution")
        
        except Exception as e:
            print(f"❌ Error testing signals: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Investigation failed: {e}")
        return False

if __name__ == "__main__":
    investigate_identical_results()
 
def check_mtf_implementation():
    """Check if multi-timeframe methods are properly implemented"""
    
    print("\n🔍 CHECKING MULTI-TIMEFRAME IMPLEMENTATION")
    print("="*50)
    
    try:
        from signal_factory import get_signal_factory
        
        factory = get_signal_factory()
        factory.initialize()
        
        strategies_to_check = ['ICTStrategy', 'EnhancedIndicatorSuiteStrategy']
        
        for strategy_name in strategies_to_check:
            print(f"\n📊 Checking {strategy_name}:")
            
            # Find strategy
            strategy = None
            for name, strat in factory.rule_based_strategies.items():
                if strategy_name in name:
                    strategy = strat
                    break
            
            if not strategy:
                print(f"   ❌ Strategy {strategy_name} not found")
                continue
            
            # Check if it has analyze_multi_timeframe
            has_mtf = hasattr(strategy, 'analyze_multi_timeframe')
            print(f"   Has analyze_multi_timeframe: {'✅' if has_mtf else '❌'}")
            
            if has_mtf:
                # Check if it's just a fallback
                import inspect
                mtf_source = inspect.getsource(strategy.analyze_multi_timeframe)
                
                # Look for fallback patterns
                fallback_indicators = [
                    'self.analyze(',
                    'mtf_data.get(\'H1\'',
                    'list(mtf_data.values())[0]',
                    'return self.analyze'
                ]
                
                is_fallback = any(indicator in mtf_source for indicator in fallback_indicators)
                
                if is_fallback:
                    print(f"   ⚠️ analyze_multi_timeframe appears to be a simple fallback")
                    print(f"   This could explain identical results")
                else:
                    print(f"   ✅ analyze_multi_timeframe has custom implementation")
            
            # Check analyze method
            has_analyze = hasattr(strategy, 'analyze')
            print(f"   Has analyze method: {'✅' if has_analyze else '❌'}")
            
            if has_analyze:
                try:
                    analyze_source = inspect.getsource(strategy.analyze)
                    print(f"   Analyze method length: {len(analyze_source)} characters")
                except:
                    print(f"   ❌ Could not inspect analyze method")
        
    except Exception as e:
        print(f"❌ MTF check failed: {e}")

check_mtf_implementation()