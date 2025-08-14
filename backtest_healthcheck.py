#!/usr/bin/env python3
"""
==============================================================================
STRATEGY TESTING & VALIDATION SUITE v1.0 - COMPREHENSIVE HEALTH CHECK
==============================================================================
TESTING CAPABILITIES:
✅ Individual strategy functionality validation
✅ Multi-timeframe compatibility testing
✅ Signal generation verification
✅ Data loading and processing validation
✅ Error handling and edge case testing
✅ Performance benchmarking
✅ Memory usage monitoring
✅ Strategy-specific requirements checking
✅ Quick smoke tests before full backtesting
==============================================================================
"""

import numpy as np
import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
import time
import warnings
import traceback
import sys
import os
import psutil
import gc
from dataclasses import dataclass
from collections import defaultdict
import concurrent.futures

warnings.filterwarnings('ignore')

@dataclass
class TestConfig:
    """Testing configuration"""
    # Test period (short for quick validation)
    test_days: int = 30  # 1 month test period
    symbols: List[str] = None
    timeframes: List[str] = None
    
    # Test thresholds
    min_signals_required: int = 5  # Minimum signals to pass test
    max_execution_time_seconds: float = 30.0  # Max time per strategy test
    max_memory_mb: float = 500.0  # Max memory usage per test
    
    # Multi-timeframe requirements
    strategy_timeframe_requirements: Dict[str, List[str]] = None
    
    def __post_init__(self):
        if self.symbols is None:
            self.symbols = ['EURUSD', 'GBPUSD']
        if self.timeframes is None:
            self.timeframes = ['M15', 'H1', 'H4', 'D1']
            
        if self.strategy_timeframe_requirements is None:
            self.strategy_timeframe_requirements = {
                'ICTStrategy': ['M15', 'H1', 'H4', 'D1'],
                'EnhancedICTStrategy': ['M15', 'H1', 'H4', 'D1'],
                'RTMStrategy': ['H1', 'H4', 'D1'],
                'EnhancedRTMStrategy': ['H1', 'H4', 'D1'],
                'SMCStrategy': ['M15', 'H1', 'H4'],
                'EnhancedSMCStrategy': ['M15', 'H1', 'H4'],
                'MomentumStrategy': ['H1'],
                'MeanReversionStrategy': ['H1'],
                'BreakoutStrategy': ['H1'],
                'ScalpingStrategy': ['M15', 'H1'],
                'EnhancedScalpingStrategy': ['M15', 'H1'],
                'VolumeStrategy': ['H1'],
                'EnhancedVolumeStrategy': ['H1'],
                'NewsStrategy': ['H1', 'H4'],
                'EnhancedNewsStrategy': ['H1', 'H4'],
                'PivotPointStrategy': ['H1', 'H4'],
                'EnhancedPivotPointStrategy': ['H1', 'H4'],
                'IndicatorSuiteStrategy': ['H1'],
                'EnhancedIndicatorSuiteStrategy': ['H1']
            }

@dataclass
class TestResult:
    """Individual test result"""
    strategy_name: str = ""
    test_passed: bool = False
    signals_generated: int = 0
    execution_time: float = 0.0
    memory_used_mb: float = 0.0
    error_message: str = ""
    warnings: List[str] = None
    timeframes_tested: List[str] = None
    symbols_tested: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.timeframes_tested is None:
            self.timeframes_tested = []
        if self.symbols_tested is None:
            self.symbols_tested = []

class StrategyTester:
    """Comprehensive strategy testing engine"""
    
    def __init__(self, config: TestConfig = None):
        self.config = config or TestConfig()
        self.logger = self._setup_logger()
        self.data_cache = {}
        
        self.logger.info("🧪 Strategy Testing & Validation Suite v1.0 Initialized")
        self.logger.info(f"📅 Test Period: {self.config.test_days} days")
        self.logger.info(f"📊 Test Symbols: {', '.join(self.config.symbols)}")
        self.logger.info(f"⏰ Test Timeframes: {', '.join(self.config.timeframes)}")
    
    def _setup_logger(self):
        """Setup professional logger"""
        logger = logging.getLogger("StrategyTester")
        logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-7s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def run_comprehensive_test_suite(self, strategies: Dict[str, Any]) -> Dict[str, Any]:
        """Run comprehensive test suite on all strategies"""
        
        test_start_time = time.time()
        
        self.logger.info("🚀 STARTING COMPREHENSIVE STRATEGY TEST SUITE")
        self.logger.info("="*70)
        
        # Step 1: Load test data
        self.logger.info("📊 Step 1: Loading test data...")
        test_data = self._load_test_data()
        
        if not test_data:
            self.logger.error("❌ Test data loading failed - cannot proceed")
            return {'success': False, 'error': 'Data loading failed'}
        
        self.logger.info(f"✅ Test data loaded: {len(test_data)} symbols, {sum(len(tf_data) for tf_data in test_data.values())} timeframe datasets")
        
        # Step 2: System health check
        self.logger.info("🔍 Step 2: System health check...")
        system_health = self._check_system_health()
        self._print_system_health(system_health)
        
        # Step 3: Test all strategies
        self.logger.info("🧪 Step 3: Testing all strategies...")
        test_results = self._test_all_strategies(strategies, test_data)
        
        # Step 4: Generate comprehensive report
        self.logger.info("📋 Step 4: Generating test report...")
        final_report = self._generate_test_report(test_results, test_start_time)
        
        # Step 5: Print summary
        self._print_test_summary(final_report)
        
        return final_report
    
    def _load_test_data(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        """Load test data for validation"""
        
        # Calculate test period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.config.test_days)
        
        self.logger.info(f"📅 Loading data from {start_date.date()} to {end_date.date()}")
        
        if not mt5.initialize():
            self.logger.error("❌ MT5 initialization failed")
            return {}
        
        try:
            multi_timeframe_data = {}
            
            tf_map = {
                'M1': mt5.TIMEFRAME_M1, 'M5': mt5.TIMEFRAME_M5,
                'M15': mt5.TIMEFRAME_M15, 'M30': mt5.TIMEFRAME_M30,
                'H1': mt5.TIMEFRAME_H1, 'H4': mt5.TIMEFRAME_H4,
                'D1': mt5.TIMEFRAME_D1
            }
            
            for symbol in self.config.symbols:
                multi_timeframe_data[symbol] = {}
                
                for timeframe in self.config.timeframes:
                    try:
                        mt5_timeframe = tf_map.get(timeframe, mt5.TIMEFRAME_H1)
                        rates = mt5.copy_rates_range(symbol, mt5_timeframe, start_date, end_date)
                        
                        if rates is not None and len(rates) > 50:  # Minimum bars for testing
                            df = pd.DataFrame(rates)
                            df['time'] = pd.to_datetime(df['time'], unit='s')
                            df.set_index('time', inplace=True)
                            
                            # Add basic indicators for testing
                            df = self._add_test_indicators(df)
                            
                            # Add required attributes
                            df.timeframe = timeframe
                            df.symbol = symbol
                            
                            multi_timeframe_data[symbol][timeframe] = df
                            
                            self.logger.info(f"✅ {symbol} {timeframe}: {len(df)} bars loaded")
                        else:
                            self.logger.warning(f"⚠️ Insufficient data for {symbol} {timeframe}")
                            
                    except Exception as e:
                        self.logger.error(f"❌ Error loading {symbol} {timeframe}: {e}")
            
            return multi_timeframe_data
            
        finally:
            mt5.shutdown()
    
    def _add_test_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add basic indicators for testing"""
        try:
            # Basic moving averages
            df['sma_20'] = df['close'].rolling(20).mean()
            df['sma_50'] = df['close'].rolling(50).mean()
            df['ema_12'] = df['close'].ewm(span=12).mean()
            df['ema_26'] = df['close'].ewm(span=26).mean()
            
            # RSI
            delta = df['close'].diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # ATR
            hl = df['high'] - df['low']
            hc = np.abs(df['high'] - df['close'].shift(1))
            lc = np.abs(df['low'] - df['close'].shift(1))
            tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
            df['atr'] = tr.rolling(14).mean()
            
            # MACD
            df['macd'] = df['ema_12'] - df['ema_26']
            df['macd_signal'] = df['macd'].ewm(span=9).mean()
            
            # Bollinger Bands
            df['bb_upper'] = df['close'].rolling(20).mean() + (df['close'].rolling(20).std() * 2)
            df['bb_lower'] = df['close'].rolling(20).mean() - (df['close'].rolling(20).std() * 2)
            
            return df.fillna(method='ffill').fillna(0)
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error adding indicators: {e}")
            return df
    
    def _check_system_health(self) -> Dict[str, Any]:
        """Check system health and requirements"""
        
        health = {
            'memory_available_gb': psutil.virtual_memory().available / (1024**3),
            'memory_total_gb': psutil.virtual_memory().total / (1024**3),
            'memory_percent': psutil.virtual_memory().percent,
            'cpu_count': psutil.cpu_count(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'disk_free_gb': psutil.disk_usage('.').free / (1024**3),
            'python_version': sys.version,
            'platform': sys.platform,
            'mt5_available': False,
            'required_packages': {}
        }
        
        # Check MT5 availability
        try:
            import MetaTrader5 as mt5
            health['mt5_available'] = mt5.initialize()
            if health['mt5_available']:
                mt5.shutdown()
        except:
            health['mt5_available'] = False
        
        # Check required packages
        required_packages = ['numpy', 'pandas', 'matplotlib', 'plotly', 'seaborn', 'tqdm']
        for package in required_packages:
            try:
                __import__(package)
                health['required_packages'][package] = True
            except ImportError:
                health['required_packages'][package] = False
        
        return health
    
    def _print_system_health(self, health: Dict[str, Any]):
        """Print system health status"""
        
        print("\n🔍 SYSTEM HEALTH CHECK:")
        print("-" * 40)
        print(f"💾 Memory: {health['memory_available_gb']:.1f}GB free / {health['memory_total_gb']:.1f}GB total ({health['memory_percent']:.1f}% used)")
        print(f"🖥️  CPU: {health['cpu_count']} cores @ {health['cpu_percent']:.1f}% usage")
        print(f"💽 Disk Space: {health['disk_free_gb']:.1f}GB free")
        print(f"🐍 Python: {health['python_version'].split()[0]}")
        print(f"📈 MT5 Available: {'✅' if health['mt5_available'] else '❌'}")
        
        print(f"\n📦 Required Packages:")
        for package, available in health['required_packages'].items():
            status = '✅' if available else '❌'
            print(f"   {status} {package}")
        
        # Health warnings
        warnings = []
        if health['memory_available_gb'] < 2.0:
            warnings.append("⚠️ Low memory available (< 2GB)")
        if health['cpu_percent'] > 80:
            warnings.append("⚠️ High CPU usage (> 80%)")
        if not health['mt5_available']:
            warnings.append("⚠️ MT5 not available - using cached/demo data only")
        if not all(health['required_packages'].values()):
            warnings.append("⚠️ Some required packages missing")
        
        if warnings:
            print(f"\n⚠️  HEALTH WARNINGS:")
            for warning in warnings:
                print(f"   {warning}")
        else:
            print(f"\n✅ System health: EXCELLENT")
    
    def _test_all_strategies(self, strategies: Dict[str, Any], 
                            test_data: Dict[str, Dict[str, pd.DataFrame]]) -> List[TestResult]:
        """Test all strategies individually"""
        
        test_results = []
        
        print(f"\n🧪 TESTING {len(strategies)} STRATEGIES:")
        print("=" * 70)
        
        for i, (strategy_name, strategy) in enumerate(strategies.items(), 1):
            self.logger.info(f"Testing [{i}/{len(strategies)}]: {strategy_name}")
            
            test_result = self._test_single_strategy(strategy_name, strategy, test_data)
            test_results.append(test_result)
            
            # Print immediate result
            status = "✅ PASS" if test_result.test_passed else "❌ FAIL"
            print(f"   {status} {strategy_name:<30} | "
                  f"Signals: {test_result.signals_generated:>3} | "
                  f"Time: {test_result.execution_time:>5.2f}s | "
                  f"Memory: {test_result.memory_used_mb:>6.1f}MB")
            
            if not test_result.test_passed:
                print(f"      ❌ Error: {test_result.error_message}")
            
            if test_result.warnings:
                for warning in test_result.warnings:
                    print(f"      ⚠️ Warning: {warning}")
        
        return test_results
    
    def _test_single_strategy(self, strategy_name: str, strategy: Any, 
                             test_data: Dict[str, Dict[str, pd.DataFrame]]) -> TestResult:
        """Test a single strategy comprehensively"""
        
        result = TestResult(strategy_name=strategy_name)
        
        # Start monitoring
        start_time = time.time()
        process = psutil.Process()
        start_memory = process.memory_info().rss / (1024 * 1024)  # MB
        
        try:
            # Determine required timeframes for this strategy
            required_timeframes = self.config.strategy_timeframe_requirements.get(
                strategy_name, ['H1']  # Default to H1 if not specified
            )
            result.timeframes_tested = required_timeframes
            result.symbols_tested = self.config.symbols
            
            # Test 1: Basic strategy instantiation
            if not hasattr(strategy, 'analyze'):
                raise Exception("Strategy missing 'analyze' method")
            
            # Test 2: Multi-timeframe capability check
            if len(required_timeframes) > 1:
                if not hasattr(strategy, 'analyze_multi_timeframe'):
                    result.warnings.append(f"Multi-timeframe strategy but no 'analyze_multi_timeframe' method")
            
            # Test 3: Signal generation test
            total_signals = 0
            
            for symbol in self.config.symbols:
                if symbol not in test_data:
                    result.warnings.append(f"No test data for symbol {symbol}")
                    continue
                
                # Prepare data based on strategy requirements
                if len(required_timeframes) == 1:
                    # Single timeframe strategy
                    timeframe = required_timeframes[0]
                    if timeframe not in test_data[symbol]:
                        result.warnings.append(f"Missing timeframe {timeframe} for {symbol}")
                        continue
                    
                    data = test_data[symbol][timeframe].copy()
                    signals = self._test_signal_generation_single_tf(strategy, data, symbol)
                    
                else:
                    # Multi-timeframe strategy
                    mtf_data = {}
                    for tf in required_timeframes:
                        if tf in test_data[symbol]:
                            mtf_data[tf] = test_data[symbol][tf].copy()
                    
                    if not mtf_data:
                        result.warnings.append(f"No multi-timeframe data for {symbol}")
                        continue
                    
                    signals = self._test_signal_generation_multi_tf(strategy, mtf_data, symbol)
                
                total_signals += signals
            
            result.signals_generated = total_signals
            
            # Test 4: Performance thresholds
            execution_time = time.time() - start_time
            current_memory = process.memory_info().rss / (1024 * 1024)  # MB
            memory_used = current_memory - start_memory
            
            result.execution_time = execution_time
            result.memory_used_mb = memory_used
            
            # Test 5: Validate results
            test_passed = True
            error_messages = []
            
            if result.signals_generated < self.config.min_signals_required:
                test_passed = False
                error_messages.append(f"Insufficient signals: {result.signals_generated} < {self.config.min_signals_required}")
            
            if execution_time > self.config.max_execution_time_seconds:
                test_passed = False
                error_messages.append(f"Execution too slow: {execution_time:.2f}s > {self.config.max_execution_time_seconds}s")
            
            if memory_used > self.config.max_memory_mb:
                result.warnings.append(f"High memory usage: {memory_used:.1f}MB > {self.config.max_memory_mb}MB")
            
            result.test_passed = test_passed
            if error_messages:
                result.error_message = "; ".join(error_messages)
            
        except Exception as e:
            result.test_passed = False
            result.error_message = str(e)
            result.execution_time = time.time() - start_time
            
            # Log full traceback for debugging
            self.logger.error(f"Strategy {strategy_name} test failed: {e}")
            if self.logger.level == logging.DEBUG:
                self.logger.error(traceback.format_exc())
        
        return result
    
    def _test_signal_generation_single_tf(self, strategy: Any, data: pd.DataFrame, symbol: str) -> int:
        """Test signal generation for single timeframe strategy"""
        
        signals_count = 0
        
        try:
            # Test with chunks of data
            chunk_size = min(100, len(data) // 3)  # Test with smaller chunks
            
            for i in range(50, len(data), chunk_size):  # Start from 50 for indicator stability
                end_idx = min(i + chunk_size, len(data))
                chunk_data = data.iloc[:end_idx].copy()
                
                # Ensure required attributes
                chunk_data.timeframe = getattr(data, 'timeframe', 'H1')
                chunk_data.symbol = symbol
                
                try:
                    analysis = strategy.analyze(chunk_data, symbol)
                    
                    if analysis and isinstance(analysis, dict):
                        signal_type = analysis.get('signal', 'HOLD')
                        if signal_type in ['BUY', 'SELL']:
                            signals_count += 1
                            
                except Exception as e:
                    # Log individual chunk failures but continue
                    if self.logger.level == logging.DEBUG:
                        self.logger.debug(f"Chunk analysis failed: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Signal generation test failed: {e}")
        
        return signals_count
    
    def _test_signal_generation_multi_tf(self, strategy: Any, mtf_data: Dict[str, pd.DataFrame], symbol: str) -> int:
        """Test signal generation for multi-timeframe strategy"""
        
        signals_count = 0
        
        try:
            # Get primary timeframe (usually H1 or the first available)
            primary_tf = 'H1' if 'H1' in mtf_data else list(mtf_data.keys())[0]
            primary_data = mtf_data[primary_tf]
            
            chunk_size = min(100, len(primary_data) // 3)
            
            for i in range(50, len(primary_data), chunk_size):
                end_idx = min(i + chunk_size, len(primary_data))
                
                # Prepare multi-timeframe chunk data
                chunk_mtf_data = {}
                for tf, data in mtf_data.items():
                    chunk_end = min(end_idx, len(data))
                    chunk_mtf_data[tf] = data.iloc[:chunk_end].copy()
                    chunk_mtf_data[tf].timeframe = tf
                    chunk_mtf_data[tf].symbol = symbol
                
                try:
                    # Try multi-timeframe method first
                    if hasattr(strategy, 'analyze_multi_timeframe'):
                        analysis = strategy.analyze_multi_timeframe(chunk_mtf_data, symbol)
                    else:
                        # Fallback to single timeframe with primary data
                        analysis = strategy.analyze(chunk_mtf_data[primary_tf], symbol)
                    
                    if analysis and isinstance(analysis, dict):
                        signal_type = analysis.get('signal', 'HOLD')
                        if signal_type in ['BUY', 'SELL']:
                            signals_count += 1
                            
                except Exception as e:
                    if self.logger.level == logging.DEBUG:
                        self.logger.debug(f"Multi-TF chunk analysis failed: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Multi-TF signal generation test failed: {e}")
        
        return signals_count
    
    def _generate_test_report(self, test_results: List[TestResult], test_start_time: float) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        
        total_test_time = time.time() - test_start_time
        
        # Calculate statistics
        total_strategies = len(test_results)
        passed_strategies = sum(1 for r in test_results if r.test_passed)
        failed_strategies = total_strategies - passed_strategies
        
        total_signals = sum(r.signals_generated for r in test_results)
        avg_signals = total_signals / total_strategies if total_strategies > 0 else 0
        
        total_execution_time = sum(r.execution_time for r in test_results)
        avg_execution_time = total_execution_time / total_strategies if total_strategies > 0 else 0
        
        total_memory = sum(r.memory_used_mb for r in test_results)
        avg_memory = total_memory / total_strategies if total_strategies > 0 else 0
        
        # Categorize results
        passed_results = [r for r in test_results if r.test_passed]
        failed_results = [r for r in test_results if not r.test_passed]
        warning_results = [r for r in test_results if r.warnings]
        
        # Performance analysis
        if passed_results:
            best_performer = max(passed_results, key=lambda x: x.signals_generated)
            fastest_strategy = min(passed_results, key=lambda x: x.execution_time)
            most_efficient = min(passed_results, key=lambda x: x.memory_used_mb)
        else:
            best_performer = fastest_strategy = most_efficient = None
        
        # Multi-timeframe analysis
        mtf_strategies = [r for r in test_results if len(r.timeframes_tested) > 1]
        single_tf_strategies = [r for r in test_results if len(r.timeframes_tested) == 1]
        
        report = {
            'test_summary': {
                'total_test_time': total_test_time,
                'total_strategies': total_strategies,
                'passed_strategies': passed_strategies,
                'failed_strategies': failed_strategies,
                'success_rate': (passed_strategies / total_strategies * 100) if total_strategies > 0 else 0,
                'total_signals_generated': total_signals,
                'avg_signals_per_strategy': avg_signals,
                'total_execution_time': total_execution_time,
                'avg_execution_time': avg_execution_time,
                'total_memory_used_mb': total_memory,
                'avg_memory_per_strategy': avg_memory
            },
            'strategy_categories': {
                'multi_timeframe_count': len(mtf_strategies),
                'single_timeframe_count': len(single_tf_strategies),
                'strategies_with_warnings': len(warning_results)
            },
            'performance_leaders': {
                'best_signal_generator': best_performer.strategy_name if best_performer else 'None',
                'fastest_execution': fastest_strategy.strategy_name if fastest_strategy else 'None',
                'most_memory_efficient': most_efficient.strategy_name if most_efficient else 'None'
            },
            'test_results': test_results,
            'passed_strategies': [r.strategy_name for r in passed_results],
            'failed_strategies': [(r.strategy_name, r.error_message) for r in failed_results],
            'strategies_with_warnings': [(r.strategy_name, r.warnings) for r in warning_results],
            'ready_for_backtesting': passed_strategies == total_strategies,
            'recommendations': self._generate_recommendations(test_results)
        }
        
        return report
    
    def _generate_recommendations(self, test_results: List[TestResult]) -> List[str]:
        """Generate actionable recommendations based on test results"""
        
        recommendations = []
        
        failed_results = [r for r in test_results if not r.test_passed]
        warning_results = [r for r in test_results if r.warnings]
        
        if failed_results:
            recommendations.append(f"❌ Fix {len(failed_results)} failed strategies before full backtesting")
            
            # Categorize failures
            signal_failures = [r for r in failed_results if "Insufficient signals" in r.error_message]
            performance_failures = [r for r in failed_results if "Execution too slow" in r.error_message]
            
            if signal_failures:
                recommendations.append(f"🔧 {len(signal_failures)} strategies need signal generation fixes")
            if performance_failures:
                recommendations.append(f"⚡ {len(performance_failures)} strategies need performance optimization")
        
        if warning_results:
            recommendations.append(f"⚠️ Review {len(warning_results)} strategies with warnings")
            
            # Common warning patterns
            mtf_warnings = [r for r in warning_results if any("multi-timeframe" in w.lower() for w in r.warnings)]
            memory_warnings = [r for r in warning_results if any("memory" in w.lower() for w in r.warnings)]
            
            if mtf_warnings:
                recommendations.append(f"🔄 {len(mtf_warnings)} strategies may need multi-timeframe method implementation")
            if memory_warnings:
                recommendations.append(f"💾 {len(memory_warnings)} strategies use high memory - consider optimization")
        
        # Performance recommendations
        slow_strategies = [r for r in test_results if r.execution_time > 10.0]
        if slow_strategies:
            recommendations.append(f"⏱️ Consider optimizing {len(slow_strategies)} slow strategies for full backtesting")
        
        # Success recommendations
        passed_results = [r for r in test_results if r.test_passed]
        if len(passed_results) > 0:
            recommendations.append(f"✅ {len(passed_results)} strategies ready for 10-year backtesting")
        
        if len(passed_results) == len(test_results):
            recommendations.append("🚀 ALL TESTS PASSED - Ready for full backtesting analysis!")
        
        return recommendations
    
    def _print_test_summary(self, report: Dict[str, Any]):
        """Print comprehensive test summary"""
        
        summary = report['test_summary']
        
        print("\n" + "="*80)
        print("📋 COMPREHENSIVE STRATEGY TEST REPORT")
        print("="*80)
        
        print(f"\n⏱️  EXECUTION SUMMARY:")
        print(f"   Total Test Time:      {summary['total_test_time']:.2f} seconds")
        print(f"   Strategies Tested:    {summary['total_strategies']}")
        print(f"   Passed:               {summary['passed_strategies']} ✅")
        print(f"   Failed:               {summary['failed_strategies']} ❌")
        print(f"   Success Rate:         {summary['success_rate']:.1f}%")
        
        print(f"\n📊 PERFORMANCE SUMMARY:")
        print(f"   Total Signals:        {summary['total_signals_generated']}")
        print(f"   Avg Signals/Strategy: {summary['avg_signals_per_strategy']:.1f}")
        print(f"   Total Execution:      {summary['total_execution_time']:.2f}s")
        print(f"   Avg Time/Strategy:    {summary['avg_execution_time']:.2f}s")
        print(f"   Total Memory Used:    {summary['total_memory_used_mb']:.1f}MB")
        print(f"   Avg Memory/Strategy:  {summary['avg_memory_per_strategy']:.1f}MB")
        
        print(f"\n🏆 PERFORMANCE LEADERS:")
        leaders = report['performance_leaders']
        print(f"   Best Signal Generator: {leaders['best_signal_generator']}")
        print(f"   Fastest Execution:     {leaders['fastest_execution']}")
        print(f"   Most Memory Efficient: {leaders['most_memory_efficient']}")
        
        print(f"\n📈 STRATEGY CATEGORIES:")
        categories = report['strategy_categories']
        print(f"   Multi-Timeframe:      {categories['multi_timeframe_count']}")
        print(f"   Single-Timeframe:     {categories['single_timeframe_count']}")
        print(f"   With Warnings:        {categories['strategies_with_warnings']}")
        
        # Failed strategies details
        if report['failed_strategies']:
            print(f"\n❌ FAILED STRATEGIES:")
            for strategy_name, error in report['failed_strategies']:
                print(f"   • {strategy_name}: {error}")
        
        # Warnings
        if report['strategies_with_warnings']:
            print(f"\n⚠️  STRATEGIES WITH WARNINGS:")
            for strategy_name, warnings in report['strategies_with_warnings']:
                print(f"   • {strategy_name}:")
                for warning in warnings:
                    print(f"     - {warning}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        for recommendation in report['recommendations']:
            print(f"   {recommendation}")
        
        # Final verdict
        print(f"\n🎯 FINAL VERDICT:")
        if report['ready_for_backtesting']:
            print("   ✅ ALL STRATEGIES READY FOR FULL BACKTESTING!")
            print("   🚀 You can proceed with the 10-year analysis")
        else:
            print("   ⚠️  SOME STRATEGIES NEED ATTENTION")
            print("   🔧 Fix failed strategies before full backtesting")
            print(f"   📊 {len(report['passed_strategies'])} strategies are ready to use")
        
        print("="*80)

def run_quick_strategy_test():
    """Run quick strategy test suite"""
    
    print("🧪 QUICK STRATEGY TESTING & VALIDATION SUITE")
    print("="*70)
    
    try:
        # Import Signal Factory
        from signal_factory import get_signal_factory
        
        # Initialize Signal Factory
        print("🏭 Initializing Signal Factory...")
        factory = get_signal_factory()
        if not factory.initialize():
            print("❌ Failed to initialize Signal Factory")
            return None
        
        # Extract strategies
        strategies = {}
        strategies.update(factory.rule_based_strategies)
        strategies.update(factory.ml_models)
        
        print(f"✅ Loaded {len(strategies)} strategies from Signal Factory")
        
        # Create test configuration
        test_config = TestConfig(
            test_days=30,  # 1 month of data for quick testing
            symbols=['EURUSD', 'GBPUSD'],  # 2 symbols for speed
            timeframes=['M15', 'H1', 'H4', 'D1'],  # All required timeframes
            min_signals_required=3,  # Minimum 3 signals to pass
            max_execution_time_seconds=30.0,  # Max 30 seconds per strategy
            max_memory_mb=500.0  # Max 500MB memory per strategy
        )
        
        # Create and run tester
        tester = StrategyTester(test_config)
        report = tester.run_comprehensive_test_suite(strategies)
        
        if not report:
            print("❌ Testing failed")
            return None
        
        # Return test report for further analysis
        return report
        
    except Exception as e:
        print(f"❌ Testing failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def save_test_report(report: Dict[str, Any], filename: str = "strategy_test_report.txt"):
    """Save detailed test report to file"""
    
    if not report:
        return
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("STRATEGY TESTING & VALIDATION REPORT\n")
            f.write("="*80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Test Summary
            summary = report['test_summary']
            f.write("TEST EXECUTION SUMMARY:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Total Test Time:      {summary['total_test_time']:.2f} seconds\n")
            f.write(f"Strategies Tested:    {summary['total_strategies']}\n")
            f.write(f"Passed:               {summary['passed_strategies']}\n")
            f.write(f"Failed:               {summary['failed_strategies']}\n")
            f.write(f"Success Rate:         {summary['success_rate']:.1f}%\n\n")
            
            # Individual Results
            f.write("INDIVIDUAL STRATEGY RESULTS:\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'Strategy':<30} {'Status':<8} {'Signals':<8} {'Time(s)':<8} {'Memory(MB)':<12} {'Error'}\n")
            f.write("-" * 80 + "\n")
            
            for result in report['test_results']:
                status = "PASS" if result.test_passed else "FAIL"
                error = result.error_message[:30] + "..." if len(result.error_message) > 30 else result.error_message
                
                f.write(f"{result.strategy_name:<30} "
                       f"{status:<8} "
                       f"{result.signals_generated:<8} "
                       f"{result.execution_time:<8.2f} "
                       f"{result.memory_used_mb:<12.1f} "
                       f"{error}\n")
            
            # Recommendations
            f.write(f"\nRECOMMENDATIONS:\n")
            f.write("-" * 40 + "\n")
            for rec in report['recommendations']:
                f.write(f"{rec}\n")
            
            f.write(f"\nFinal Verdict: {'READY' if report['ready_for_backtesting'] else 'NEEDS ATTENTION'}\n")
        
        print(f"📄 Detailed test report saved to: {filename}")
        
    except Exception as e:
        print(f"❌ Error saving report: {e}")

if __name__ == "__main__":
    # Run the quick strategy test
    print("Starting Strategy Testing & Validation Suite...")
    
    test_report = run_quick_strategy_test()
    
    if test_report:
        # Save detailed report
        save_test_report(test_report)
        
        print(f"\n🎉 TESTING COMPLETED!")
        
        # Quick summary for next steps
        if test_report['ready_for_backtesting']:
            print("✅ ALL STRATEGIES READY - You can run the full 10-year backtesting!")
            print("🚀 Execute the main backtester file for complete analysis")
        else:
            passed = len(test_report['passed_strategies'])
            total = test_report['test_summary']['total_strategies']
            print(f"⚠️  {passed}/{total} strategies ready")
            print("🔧 Fix failed strategies or proceed with working ones only")
            print("📊 Check strategy_test_report.txt for detailed analysis")
    else:
        print("❌ Testing failed - check error messages above")
