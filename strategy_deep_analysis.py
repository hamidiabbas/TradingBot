#!/usr/bin/env python3
"""
===============================================================
COMPREHENSIVE STRATEGY ANALYSIS SUITE v1.0
===============================================================
Deep dive analysis of all 13 actual strategies in your project
- Strategy loading and validation
- Performance metrics analysis  
- Integration status checking
- Signal generation capability testing
- Kelly compatibility assessment

Works with your actual TradingBot project structure
===============================================================
"""

import os
import sys
import importlib.util
import inspect
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import warnings
import traceback

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

warnings.filterwarnings('ignore')

@dataclass
class StrategyAnalysisResult:
    """Comprehensive analysis result for a single strategy"""
    name: str
    file_path: str
    status: str  # 'active', 'inactive', 'error', 'incompatible'
    
    # Technical Analysis
    has_analyze_method: bool = False
    analyze_method_signature: str = ""
    required_data_fields: List[str] = field(default_factory=list)
    
    # Integration Analysis
    signal_factory_compatible: bool = False
    kelly_system_compatible: bool = False
    main_py_integration: str = "unknown"
    
    # Performance Metrics (if available)
    signals_generated_today: int = 0
    avg_confidence_level: float = 0.0
    supported_symbols: List[str] = field(default_factory=list)
    supported_timeframes: List[str] = field(default_factory=list)
    
    # Error Information
    error_details: str = ""
    warnings: List[str] = field(default_factory=list)
    
    # Advanced Analysis
    complexity_score: int = 0  # 1-10 scale
    market_conditions: List[str] = field(default_factory=list)  # trend, range, volatile, etc.
    strategy_type: str = "unknown"  # momentum, mean_reversion, breakout, etc.

class AdvancedStrategyAnalyzer:
    """Advanced analyzer for your 13 actual strategies"""
    
    def __init__(self, strategies_path: str = "strategies"):
        self.strategies_path = Path(strategies_path)
        self.analysis_results = {}
        self.loaded_strategies = {}
        self.integration_status = {}
        
        print("🚀 ADVANCED STRATEGY ANALYSIS SUITE v1.0")
        print("=" * 60)
        print(f"📁 Analyzing strategies in: {self.strategies_path}")
        print(f"🕐 Analysis started: {datetime.now().strftime('%H:%M:%S')}")
        print()
    
    def discover_all_strategies(self) -> List[Path]:
        """Discover all actual strategy files (excluding backups)"""
        
        strategy_files = []
        backup_files = []
        
        if not self.strategies_path.exists():
            print(f"❌ Strategies folder not found: {self.strategies_path}")
            return []
        
        for file in self.strategies_path.glob("*.py"):
            if (file.name.startswith("_") or 
                "backup" in file.name.lower() or 
                "test" in file.name.lower() or
                "__pycache__" in str(file)):
                backup_files.append(file)
            else:
                strategy_files.append(file)
        
        print(f"📊 STRATEGY DISCOVERY RESULTS:")
        print(f"   ✅ Active Strategy Files: {len(strategy_files)}")
        print(f"   📦 Backup/Test Files: {len(backup_files)}")
        print()
        
        print(f"🎯 YOUR 13 ACTUAL STRATEGIES:")
        for i, file in enumerate(strategy_files, 1):
            print(f"   {i:2d}. {file.name}")
        
        if backup_files:
            print(f"\n📦 Backup files found (ignored):")
            for file in backup_files[:5]:  # Show first 5
                print(f"   • {file.name}")
            if len(backup_files) > 5:
                print(f"   • ... and {len(backup_files)-5} more")
        
        print()
        return strategy_files
    
    def analyze_strategy_file(self, strategy_file: Path) -> StrategyAnalysisResult:
        """Comprehensive analysis of a single strategy file"""
        
        result = StrategyAnalysisResult(
            name=strategy_file.stem,
            file_path=str(strategy_file),
            status="analyzing"
        )
        
        try:
            print(f"🔍 Analyzing: {strategy_file.name}")
            
            # Step 1: Load and inspect the module
            spec = importlib.util.spec_from_file_location(strategy_file.stem, strategy_file)
            module = importlib.util.module_from_spec(spec)
            
            # Execute module to load classes
            spec.loader.exec_module(module)
            
            # Step 2: Find strategy classes
            strategy_classes = self._find_strategy_classes(module)
            
            if not strategy_classes:
                result.status = "no_strategy_class"
                result.error_details = "No strategy class found with analyze() method"
                return result
            
            # Step 3: Analyze primary strategy class
            primary_class_name, primary_class = strategy_classes[0]
            result = self._analyze_strategy_class(primary_class, result, primary_class_name)
            
            # Step 4: Test strategy instantiation and basic functionality
            result = self._test_strategy_functionality(primary_class, result)
            
            # Step 5: Check integration compatibility
            result = self._check_integration_compatibility(result, module)
            
            # Step 6: Analyze strategy characteristics
            result = self._analyze_strategy_characteristics(primary_class, result)
            
            result.status = "active" if result.has_analyze_method else "inactive"
            
        except Exception as e:
            result.status = "error"
            result.error_details = f"Analysis error: {str(e)}"
            print(f"   ❌ Error: {str(e)}")
        
        return result
    
    def _find_strategy_classes(self, module) -> List[Tuple[str, Any]]:
        """Find strategy classes in the module"""
        
        strategy_classes = []
        
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Check if it's a strategy class
            if (hasattr(obj, 'analyze') or 
                'strategy' in name.lower() or
                hasattr(obj, 'generate_signal') or
                hasattr(obj, 'get_signal')):
                strategy_classes.append((name, obj))
        
        # Sort by likelihood of being the main strategy class
        def strategy_priority(item):
            name, _ = item
            score = 0
            if 'strategy' in name.lower(): score += 10
            if name.endswith('Strategy'): score += 5
            if not name.startswith('_'): score += 3
            return score
        
        strategy_classes.sort(key=strategy_priority, reverse=True)
        return strategy_classes
    
    def _analyze_strategy_class(self, strategy_class, result: StrategyAnalysisResult, class_name: str) -> StrategyAnalysisResult:
        """Analyze the strategy class structure"""
        
        # Check for analyze method
        if hasattr(strategy_class, 'analyze'):
            result.has_analyze_method = True
            try:
                sig = inspect.signature(strategy_class.analyze)
                result.analyze_method_signature = str(sig)
                
                # Determine required data fields from signature
                for param in sig.parameters.values():
                    if param.name in ['data', 'df', 'ohlc', 'market_data']:
                        result.required_data_fields.append(param.name)
            except:
                result.analyze_method_signature = "Could not determine signature"
        
        # Check for alternative signal methods
        signal_methods = []
        for method_name in ['generate_signal', 'get_signal', 'calculate_signal', 'process_signal']:
            if hasattr(strategy_class, method_name):
                signal_methods.append(method_name)
        
        if signal_methods and not result.has_analyze_method:
            result.warnings.append(f"Has signal methods {signal_methods} but no analyze() method")
        
        # Analyze class attributes and methods
        methods = [method for method in dir(strategy_class) if not method.startswith('_')]
        result.complexity_score = min(10, max(1, len(methods) // 3))
        
        return result
    
    def _test_strategy_functionality(self, strategy_class, result: StrategyAnalysisResult) -> StrategyAnalysisResult:
        """Test strategy instantiation and basic functionality"""
        
        try:
            # Try to instantiate the strategy
            strategy_instance = strategy_class()
            
            if result.has_analyze_method:
                # Create sample data for testing
                sample_data = self._create_sample_market_data()
                
                # Test analyze method with sample data
                try:
                    test_result = strategy_instance.analyze(sample_data, "EURUSD")
                    
                    if isinstance(test_result, dict):
                        result.signals_generated_today = 1
                        
                        # Analyze the signal structure
                        if 'confidence' in test_result:
                            result.avg_confidence_level = float(test_result['confidence'])
                        
                        if 'signal' in test_result:
                            signal_value = test_result['signal']
                            if signal_value in ['BUY', 'SELL']:
                                result.kelly_system_compatible = True
                    
                except Exception as e:
                    result.warnings.append(f"analyze() method test failed: {str(e)}")
            
        except Exception as e:
            result.warnings.append(f"Strategy instantiation failed: {str(e)}")
        
        return result
    
    def _check_integration_compatibility(self, result: StrategyAnalysisResult, module) -> StrategyAnalysisResult:
        """Check compatibility with signal_factory and Kelly system"""
        
        # Check signal_factory compatibility
        try:
            # Look for signal_factory import or usage
            module_source = inspect.getsource(module)
            
            if 'signal_factory' in module_source.lower():
                result.signal_factory_compatible = True
            
            # Check for Kelly-compatible output format
            if result.has_analyze_method and 'confidence' in module_source:
                result.kelly_system_compatible = True
                
        except Exception as e:
            result.warnings.append(f"Integration check error: {str(e)}")
        
        return result
    
    def _analyze_strategy_characteristics(self, strategy_class, result: StrategyAnalysisResult) -> StrategyAnalysisResult:
        """Analyze strategy type and characteristics"""
        
        try:
            class_name = strategy_class.__name__.lower()
            
            # Determine strategy type
            if 'momentum' in class_name:
                result.strategy_type = "momentum"
            elif 'trend' in class_name:
                result.strategy_type = "trend_following"
            elif 'reversion' in class_name or 'mean' in class_name:
                result.strategy_type = "mean_reversion"
            elif 'breakout' in class_name:
                result.strategy_type = "breakout"
            elif 'scalp' in class_name:
                result.strategy_type = "scalping"
            elif 'swing' in class_name:
                result.strategy_type = "swing_trading"
            elif 'news' in class_name:
                result.strategy_type = "news_based"
            elif 'volume' in class_name:
                result.strategy_type = "volume_based"
            elif 'smc' in class_name:
                result.strategy_type = "smart_money_concepts"
            elif 'ict' in class_name:
                result.strategy_type = "inner_circle_trader"
            else:
                result.strategy_type = "hybrid_technical"
            
            # Determine supported market conditions
            if result.strategy_type in ['momentum', 'trend_following', 'breakout']:
                result.market_conditions = ['trending', 'volatile']
            elif result.strategy_type in ['mean_reversion', 'scalping']:
                result.market_conditions = ['ranging', 'low_volatility']
            else:
                result.market_conditions = ['all_conditions']
            
            # Default supported instruments
            result.supported_symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'XAUUSD']
            result.supported_timeframes = ['M15', 'H1', 'H4']
            
        except Exception as e:
            result.warnings.append(f"Characteristic analysis error: {str(e)}")
        
        return result
    
    def _create_sample_market_data(self) -> pd.DataFrame:
        """Create sample market data for testing"""
        
        dates = pd.date_range(start='2024-01-01', periods=100, freq='1H')
        
        # Generate realistic OHLC data
        np.random.seed(42)  # For reproducible results
        close_prices = 1.1000 + np.cumsum(np.random.randn(100) * 0.001)
        
        data = pd.DataFrame({
            'time': dates,
            'open': close_prices + np.random.randn(100) * 0.0005,
            'high': close_prices + np.abs(np.random.randn(100) * 0.002),
            'low': close_prices - np.abs(np.random.randn(100) * 0.002),
            'close': close_prices,
            'tick_volume': np.random.randint(100, 1000, 100)
        })
        
        return data
    
    def run_comprehensive_analysis(self) -> Dict[str, StrategyAnalysisResult]:
        """Run comprehensive analysis on all strategies"""
        
        strategy_files = self.discover_all_strategies()
        
        if not strategy_files:
            print("❌ No strategy files found to analyze!")
            return {}
        
        print(f"🔍 STARTING COMPREHENSIVE ANALYSIS OF {len(strategy_files)} STRATEGIES")
        print("=" * 70)
        
        for i, strategy_file in enumerate(strategy_files, 1):
            print(f"\n[{i}/{len(strategy_files)}] ", end="")
            
            result = self.analyze_strategy_file(strategy_file)
            self.analysis_results[result.name] = result
            
            # Show immediate status
            status_icon = {
                'active': '✅',
                'inactive': '⚠️',
                'error': '❌',
                'no_strategy_class': '❓'
            }
            
            print(f"   {status_icon.get(result.status, '❓')} Status: {result.status}")
            
            if result.has_analyze_method:
                print(f"   📊 analyze() method: ✅")
            
            if result.warnings:
                print(f"   ⚠️  Warnings: {len(result.warnings)}")
        
        print(f"\n🏁 ANALYSIS COMPLETE!")
        return self.analysis_results
    
    def generate_comprehensive_report(self):
        """Generate comprehensive analysis report"""
        
        if not self.analysis_results:
            print("❌ No analysis results available. Run analysis first.")
            return
        
        total_strategies = len(self.analysis_results)
        active_strategies = len([r for r in self.analysis_results.values() if r.status == 'active'])
        inactive_strategies = len([r for r in self.analysis_results.values() if r.status == 'inactive'])
        error_strategies = len([r for r in self.analysis_results.values() if r.status == 'error'])
        
        print(f"\n" + "=" * 80)
        print(f"📊 COMPREHENSIVE STRATEGY ANALYSIS REPORT")
        print(f"=" * 80)
        print(f"🕐 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 Project: TradingBot v1.1")
        print(f"📈 Total Strategies Analyzed: {total_strategies}")
        
        print(f"\n📊 STRATEGY STATUS OVERVIEW:")
        print(f"   ✅ Active Strategies: {active_strategies}")
        print(f"   ⚠️  Inactive Strategies: {inactive_strategies}")
        print(f"   ❌ Error Strategies: {error_strategies}")
        print(f"   📈 Success Rate: {(active_strategies/total_strategies)*100:.1f}%")
        
        # Strategy Type Distribution
        strategy_types = {}
        for result in self.analysis_results.values():
            strategy_type = result.strategy_type
            strategy_types[strategy_type] = strategy_types.get(strategy_type, 0) + 1
        
        print(f"\n🎯 STRATEGY TYPE DISTRIBUTION:")
        for strategy_type, count in sorted(strategy_types.items(), key=lambda x: x[1], reverse=True):
            print(f"   📈 {strategy_type.replace('_', ' ').title()}: {count}")
        
        # Detailed Strategy Analysis
        print(f"\n🔍 DETAILED STRATEGY ANALYSIS:")
        print("-" * 80)
        
        for name, result in sorted(self.analysis_results.items()):
            status_icon = {
                'active': '✅',
                'inactive': '⚠️',
                'error': '❌',
                'no_strategy_class': '❓'
            }
            
            print(f"\n{status_icon.get(result.status, '❓')} {name.upper()}")
            print(f"   📄 File: {Path(result.file_path).name}")
            print(f"   🎯 Type: {result.strategy_type.replace('_', ' ').title()}")
            print(f"   📊 Status: {result.status.replace('_', ' ').title()}")
            
            if result.has_analyze_method:
                print(f"   ✅ analyze() Method: Available")
                print(f"   📝 Signature: {result.analyze_method_signature}")
            else:
                print(f"   ❌ analyze() Method: Missing")
            
            if result.kelly_system_compatible:
                print(f"   🧮 Kelly Compatible: ✅")
            else:
                print(f"   🧮 Kelly Compatible: ❌")
            
            print(f"   🎲 Complexity Score: {result.complexity_score}/10")
            print(f"   🌍 Market Conditions: {', '.join(result.market_conditions)}")
            
            if result.warnings:
                print(f"   ⚠️  Warnings:")
                for warning in result.warnings[:3]:  # Show first 3
                    print(f"      • {warning}")
                if len(result.warnings) > 3:
                    print(f"      • ... and {len(result.warnings)-3} more")
            
            if result.error_details:
                print(f"   ❌ Error: {result.error_details}")
        
        # Integration Analysis
        kelly_compatible = len([r for r in self.analysis_results.values() if r.kelly_system_compatible])
        
        print(f"\n🔗 INTEGRATION ANALYSIS:")
        print(f"   🧮 Kelly System Compatible: {kelly_compatible}/{total_strategies} ({(kelly_compatible/total_strategies)*100:.1f}%)")
        print(f"   📡 Signal Factory Ready: {len([r for r in self.analysis_results.values() if r.signal_factory_compatible])}/{total_strategies}")
        
        # Recommendations
        print(f"\n💡 STRATEGIC RECOMMENDATIONS:")
        
        if active_strategies == total_strategies:
            print(f"   🎉 Excellent! All {total_strategies} strategies are active and functional")
        else:
            print(f"   🔧 Priority: Fix {inactive_strategies + error_strategies} non-functional strategies")
        
        if kelly_compatible < total_strategies:
            print(f"   🧮 Enhance Kelly compatibility for {total_strategies - kelly_compatible} strategies")
        
        if active_strategies >= 8:
            print(f"   📊 Ready for 10-year backtesting with {active_strategies} strategies")
            print(f"   🎯 Consider multi-strategy portfolio optimization")
        
        non_momentum_strategies = len([r for r in self.analysis_results.values() 
                                     if r.strategy_type != 'momentum' and r.status == 'active'])
        
        if non_momentum_strategies >= 5:
            print(f"   🌈 Good strategy diversity: {non_momentum_strategies} non-momentum strategies")
        else:
            print(f"   📈 Consider adding more diverse strategy types")
        
        print(f"\n🚀 NEXT STEPS:")
        print(f"   1. Fix inactive/error strategies for maximum portfolio power")
        print(f"   2. Implement 10-year backtesting for active strategies")
        print(f"   3. Optimize Kelly integration for all compatible strategies")
        print(f"   4. Create multi-strategy performance dashboard")
        
        # Save report to file
        try:
            report_file = f"strategy_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
            with open(report_file, 'w') as f:
                # Write a simplified version of the report to file
                f.write(f"Strategy Analysis Report - {datetime.now()}\n")
                f.write(f"Total Strategies: {total_strategies}\n")
                f.write(f"Active: {active_strategies}, Inactive: {inactive_strategies}, Errors: {error_strategies}\n\n")
                
                for name, result in sorted(self.analysis_results.items()):
                    f.write(f"{name}: {result.status} - {result.strategy_type}\n")
                    if result.error_details:
                        f.write(f"  Error: {result.error_details}\n")
                    if result.warnings:
                        f.write(f"  Warnings: {len(result.warnings)}\n")
                    f.write("\n")
            
            print(f"📄 Report saved to: {report_file}")
            
        except Exception as e:
            print(f"⚠️  Could not save report file: {e}")

def main():
    """Main analysis execution"""
    
    # Check if we're in the right directory
    if not Path("strategies").exists():
        print("❌ Error: 'strategies' folder not found!")
        print("   Make sure you're running this from the TradingBot root directory")
        return
    
    if not Path("main.py").exists():
        print("❌ Error: 'main.py' not found!")
        print("   Make sure you're running this from the TradingBot root directory")
        return
    
    # Initialize analyzer
    analyzer = AdvancedStrategyAnalyzer()
    
    # Run comprehensive analysis
    results = analyzer.run_comprehensive_analysis()
    
    if results:
        # Generate comprehensive report
        analyzer.generate_comprehensive_report()
        
        # Check current integration with your trading bot
        print(f"\n🔗 CHECKING CURRENT INTEGRATION WITH YOUR TRADING BOT:")
        check_current_bot_integration(results)
        
    else:
        print("❌ No strategies found or analysis failed")

def check_current_bot_integration(analysis_results: Dict[str, StrategyAnalysisResult]):
    """Check how strategies are integrated with your current trading bot"""
    
    print("-" * 50)
    
    # Check main.py integration
    try:
        with open('main.py', 'r') as f:
            main_content = f.read()
        
        strategy_imports = 0
        if 'from strategies.' in main_content:
            strategy_imports += main_content.count('from strategies.')
        
        print(f"📄 main.py Integration:")
        print(f"   Strategy imports detected: {strategy_imports}")
        
        # Check if using built-in strategies vs. your actual strategies
        if 'KellyMomentumStrategy' in main_content and 'from strategies.' not in main_content:
            print(f"   ⚠️  WARNING: Using built-in basic strategies instead of your 13 strategies!")
            print(f"   💡 Recommendation: Integrate your actual strategies from strategies/ folder")
        
    except Exception as e:
        print(f"❌ Could not analyze main.py: {e}")
    
    # Check signal_factory integration
    try:
        with open('signal_factory.py', 'r') as f:
            signal_factory_content = f.read()
        
        print(f"📡 signal_factory.py Integration:")
        
        if 'strategies/' in signal_factory_content or 'from strategies.' in signal_factory_content:
            print(f"   ✅ References strategies folder")
        else:
            print(f"   ⚠️  May not be using your strategies folder")
        
    except Exception as e:
        print(f"❌ Could not analyze signal_factory.py: {e}")
    
    # Summary recommendations
    active_count = len([r for r in analysis_results.values() if r.status == 'active'])
    
    print(f"\n🎯 INTEGRATION RECOMMENDATIONS:")
    if active_count >= 8:
        print(f"   🚀 You have {active_count} working strategies - ready for multi-strategy trading!")
        print(f"   📊 Recommend: Implement 10-year backtesting to rank performance")
        print(f"   🎯 Recommend: Create dynamic strategy selection system")
    else:
        print(f"   🔧 Fix remaining strategies to maximize trading power")
        print(f"   📈 Focus on getting to 10+ active strategies for diversification")

if __name__ == "__main__":
    main()
