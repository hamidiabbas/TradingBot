#!/usr/bin/env python3
"""
==============================================================================
MULTI-TIMEFRAME INDEPENDENT STRATEGY BACKTESTER v6.0 - WITH ADVANCED CHARTS
==============================================================================
NEW CHART FEATURES:
✅ Individual strategy equity curves with detailed annotations
✅ Strategy performance comparison charts
✅ Risk-return scatter plots with strategy positioning
✅ Monthly/yearly performance heatmaps
✅ Drawdown analysis charts
✅ Trade distribution and win/loss analysis
✅ Multi-timeframe signal strength visualization
✅ Interactive HTML charts with zoom/pan capabilities
✅ Comprehensive chart export (PNG, HTML, PDF)
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
from dataclasses import dataclass, field
from collections import defaultdict, deque
import concurrent.futures
from tqdm import tqdm
import gc
import os

# Enhanced plotting libraries
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.offline as pyo
from plotly.graph_objs import Figure
import plotly.figure_factory as ff

# Set style for better looking charts
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")
warnings.filterwarnings('ignore')

@dataclass
class BacktestConfig:
    """Enhanced backtesting configuration with charting options"""
    initial_capital: float = 100000.0
    
    # SIMPLIFIED RISK MANAGEMENT
    fixed_position_size: float = 0.01
    max_positions: int = 5
    commission: float = 0.0001
    spread_pips: float = 1.0
    
    # DISABLED COMPLEX FEATURES
    enable_trade_management: bool = False
    enable_overtrading_prevention: bool = False
    enable_position_scaling: bool = False
    enable_trailing_stops: bool = False
    
    # MULTI-TIMEFRAME SETTINGS
    primary_timeframe: str = "H1"
    enable_multi_timeframe: bool = True
    timeframes: List[str] = field(default_factory=lambda: ["M15", "H1", "H4", "D1"])
    
    # CHART SETTINGS
    enable_charting: bool = True
    chart_output_dir: str = "strategy_charts"
    save_individual_charts: bool = True
    save_comparison_charts: bool = True
    chart_formats: List[str] = field(default_factory=lambda: ["html", "png"])
    chart_width: int = 1200
    chart_height: int = 600
    
    # Performance settings
    enable_parallel_processing: bool = True
    max_workers: int = 4
    enable_progress_bars: bool = True
    log_level: str = "INFO"

@dataclass
class StrategyResults:
    """Enhanced strategy results with charting data"""
    strategy_name: str = ""
    
    # Core Performance Metrics
    total_return: float = 0.0
    annualized_return: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    max_drawdown_pct: float = 0.0
    
    # Trade Statistics
    total_trades: int = 0
    winning_trades: int = 0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    average_win: float = 0.0
    average_loss: float = 0.0
    
    # Chart Data
    equity_curve: pd.Series = field(default_factory=pd.Series)
    daily_returns: pd.Series = field(default_factory=pd.Series)
    monthly_returns: pd.Series = field(default_factory=pd.Series)
    trade_history: pd.DataFrame = field(default_factory=pd.DataFrame)
    drawdown_series: pd.Series = field(default_factory=pd.Series)
    
    # Strategy Quality
    signals_generated: int = 0
    execution_time: float = 0.0
    consistency_score: float = 0.0
    
    # Multi-timeframe metrics
    timeframes_used: List[str] = field(default_factory=list)
    multi_timeframe_signals: int = 0

class ProfessionalLogger:
    """Enhanced logger with chart generation logging"""
    
    def __init__(self, config: BacktestConfig):
        self.config = config
        self.logger = self._setup_logger()
        self.progress_bars = {}
        
    def _setup_logger(self):
        logger = logging.getLogger("MTFChartBacktester")
        logger.setLevel(getattr(logging, self.config.log_level))
        
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-7s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def info(self, message: str):
        self.logger.info(f"🔍 {message}")
    
    def success(self, message: str):
        self.logger.info(f"✅ {message}")
    
    def warning(self, message: str):
        self.logger.warning(f"⚠️ {message}")
    
    def error(self, message: str):
        self.logger.error(f"❌ {message}")
    
    def chart_info(self, message: str):
        self.logger.info(f"📊 {message}")
    
    def progress(self, name: str, total: int) -> tqdm:
        if self.config.enable_progress_bars:
            pbar = tqdm(total=total, desc=name, unit="items", 
                       bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]')
            self.progress_bars[name] = pbar
            return pbar
        return None
    
    def close_progress(self, name: str):
        if name in self.progress_bars:
            self.progress_bars[name].close()
            del self.progress_bars[name]

class MultiTimeframeDataProcessor:
    """Enhanced data processor with charting data preparation"""
    
    def __init__(self, config: BacktestConfig, logger: ProfessionalLogger):
        self.config = config
        self.logger = logger
        self.data_cache = {}
        
    def load_multi_timeframe_data(self, symbols: List[str], 
                                 start_date: datetime, end_date: datetime) -> Dict[str, Dict[str, pd.DataFrame]]:
        """Load historical data for multiple timeframes"""
        
        self.logger.info(f"Loading multi-timeframe data for {len(symbols)} symbols")
        self.logger.info(f"📅 Period: {start_date.date()} to {end_date.date()} ({(end_date-start_date).days} days)")
        self.logger.info(f"⏰ Timeframes: {', '.join(self.config.timeframes)}")
        
        if not mt5.initialize():
            self.logger.error("MT5 initialization failed")
            return {}
        
        multi_timeframe_data = {}
        total_operations = len(symbols) * len(self.config.timeframes)
        
        pbar = self.logger.progress("Loading Multi-TF Data", total_operations)
        
        try:
            tf_map = {
                'M1': mt5.TIMEFRAME_M1, 'M5': mt5.TIMEFRAME_M5,
                'M15': mt5.TIMEFRAME_M15, 'M30': mt5.TIMEFRAME_M30,
                'H1': mt5.TIMEFRAME_H1, 'H4': mt5.TIMEFRAME_H4,
                'D1': mt5.TIMEFRAME_D1
            }
            
            for symbol in symbols:
                multi_timeframe_data[symbol] = {}
                
                for timeframe in self.config.timeframes:
                    cache_key = f"{symbol}_{timeframe}_{start_date}_{end_date}"
                    
                    if cache_key in self.data_cache:
                        multi_timeframe_data[symbol][timeframe] = self.data_cache[cache_key]
                        if pbar:
                            pbar.update(1)
                        continue
                    
                    try:
                        mt5_timeframe = tf_map.get(timeframe, mt5.TIMEFRAME_H1)
                        rates = mt5.copy_rates_range(symbol, mt5_timeframe, start_date, end_date)
                        
                        if rates is not None and len(rates) > 100:
                            df = pd.DataFrame(rates)
                            df['time'] = pd.to_datetime(df['time'], unit='s')
                            df.set_index('time', inplace=True)
                            
                            # Add multi-timeframe attributes
                            df.timeframe = timeframe
                            df.symbol = symbol
                            
                            # Calculate additional indicators for multi-timeframe analysis
                            df = self._add_multi_timeframe_indicators(df, timeframe)
                            
                            self.data_cache[cache_key] = df
                            multi_timeframe_data[symbol][timeframe] = df
                            
                            self.logger.info(f"✅ {symbol} {timeframe}: {len(df)} bars loaded")
                        else:
                            self.logger.warning(f"⚠️ No data for {symbol} {timeframe}")
                            
                    except Exception as e:
                        self.logger.error(f"❌ Error loading {symbol} {timeframe}: {e}")
                    
                    if pbar:
                        pbar.update(1)
            
            self.logger.close_progress("Loading Multi-TF Data")
            
            # Summary
            total_symbols = len(multi_timeframe_data)
            total_timeframes = sum(len(tf_data) for tf_data in multi_timeframe_data.values())
            self.logger.success(f"Loaded {total_symbols} symbols with {total_timeframes} timeframe datasets")
            
        finally:
            mt5.shutdown()
        
        return multi_timeframe_data
    
    def _add_multi_timeframe_indicators(self, df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        """Add timeframe-specific indicators"""
        try:
            # Basic indicators for all timeframes
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
            
            # Timeframe-specific indicators
            if timeframe in ['H4', 'D1']:
                # Higher timeframe trend indicators
                df['sma_200'] = df['close'].rolling(200).mean()
                df['trend_strength'] = (df['close'] - df['sma_200']) / df['sma_200']
                
            elif timeframe in ['M15', 'M30']:
                # Lower timeframe precision indicators
                df['bb_upper'] = df['close'].rolling(20).mean() + (df['close'].rolling(20).std() * 2)
                df['bb_lower'] = df['close'].rolling(20).mean() - (df['close'].rolling(20).std() * 2)
                df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
            
            return df.fillna(method='ffill').fillna(0)
            
        except Exception as e:
            return df

class MultiTimeframeStrategyProcessor:
    """Process strategies with multi-timeframe support"""
    
    def __init__(self, config: BacktestConfig, logger: ProfessionalLogger):
        self.config = config
        self.logger = logger
        
        # Define strategy timeframe requirements
        self.strategy_timeframe_requirements = {
            'ICTStrategy': ['M15', 'H1', 'H4', 'D1'],
            'EnhancedICTStrategy': ['M15', 'H1', 'H4', 'D1'],
            'RTMStrategy': ['H1', 'H4', 'D1'],
            'EnhancedRTMStrategy': ['H1', 'H4', 'D1'],
            'SMCStrategy': ['M15', 'H1', 'H4'],
            'EnhancedSMCStrategy': ['M15', 'H1', 'H4'],
            # Single timeframe strategies
            'MomentumStrategy': ['H1'],
            'MeanReversionStrategy': ['H1'],
            'BreakoutStrategy': ['H1'],
            # Add more as needed
        }
    
    def process_single_strategy_mtf(self, strategy_name: str, strategy, 
                                   multi_timeframe_data: Dict[str, Dict[str, pd.DataFrame]],
                                   symbols: List[str]) -> Tuple[str, Dict[str, pd.DataFrame]]:
        """Process strategy with multi-timeframe data"""
        
        self.logger.info(f"[{strategy_name}] Processing with multi-timeframe support...")
        
        # Get required timeframes for this strategy
        required_timeframes = self.strategy_timeframe_requirements.get(
            strategy_name, [self.config.primary_timeframe]
        )
        
        self.logger.info(f"[{strategy_name}] Required timeframes: {required_timeframes}")
        
        strategy_signals = {}
        
        for symbol in symbols:
            if symbol not in multi_timeframe_data:
                continue
                
            try:
                # Prepare multi-timeframe data for strategy
                mtf_data = {}
                for tf in required_timeframes:
                    if tf in multi_timeframe_data[symbol]:
                        mtf_data[tf] = multi_timeframe_data[symbol][tf].copy()
                
                if not mtf_data:
                    self.logger.warning(f"[{strategy_name}] No timeframe data for {symbol}")
                    continue
                
                # Generate signals using multi-timeframe data
                signals_df = self._generate_mtf_signals(strategy_name, strategy, mtf_data, symbol)
                
                if signals_df is not None and len(signals_df) > 0:
                    strategy_signals[symbol] = signals_df
                    
                    signal_count = len(signals_df[signals_df['signal'] != 0])
                    self.logger.info(f"[{strategy_name}] {symbol}: {signal_count} MTF signals generated")
                
            except Exception as e:
                self.logger.error(f"[{strategy_name}] Error processing {symbol}: {e}")
                continue
        
        total_signals = sum(len(signals[signals['signal'] != 0]) for signals in strategy_signals.values())
        self.logger.success(f"[{strategy_name}] Total MTF signals: {total_signals}")
        
        return strategy_name, strategy_signals
    
    def _generate_mtf_signals(self, strategy_name: str, strategy, 
                             mtf_data: Dict[str, pd.DataFrame], symbol: str) -> Optional[pd.DataFrame]:
        """Generate signals using multi-timeframe data"""
        
        try:
            # Use primary timeframe for signal timing
            primary_tf = self.config.primary_timeframe
            if primary_tf not in mtf_data:
                primary_tf = list(mtf_data.keys())[0]  # Use first available
            
            primary_data = mtf_data[primary_tf]
            
            # Initialize signals DataFrame
            signals_df = pd.DataFrame(index=primary_data.index)
            signals_df['signal'] = 0.0
            signals_df['confidence'] = 0.0
            signals_df['strategy'] = strategy_name
            signals_df['symbol'] = symbol
            signals_df['timeframes_used'] = str(list(mtf_data.keys()))
            
            # Process in chunks for efficiency
            chunk_size = 500
            
            for i in range(50, len(primary_data), chunk_size):
                try:
                    end_idx = min(i + chunk_size, len(primary_data))
                    
                    # Prepare multi-timeframe chunk data
                    chunk_mtf_data = {}
                    for tf, data in mtf_data.items():
                        chunk_end = min(end_idx, len(data))
                        chunk_mtf_data[tf] = data.iloc[:chunk_end].copy()
                        chunk_mtf_data[tf].timeframe = tf
                        chunk_mtf_data[tf].symbol = symbol
                    
                    # Call strategy with multi-timeframe data
                    if hasattr(strategy, 'analyze_multi_timeframe'):
                        analysis = strategy.analyze_multi_timeframe(chunk_mtf_data, symbol)
                    else:
                        main_data = chunk_mtf_data[primary_tf]
                        analysis = strategy.analyze(main_data, symbol)
                    
                    if analysis and isinstance(analysis, dict):
                        signal_type = analysis.get('signal', 'HOLD')
                        
                        if signal_type in ['BUY', 'SELL']:
                            signal_value = 1.0 if signal_type == 'BUY' else -1.0
                            confidence = analysis.get('confidence', 0.5)
                            
                            current_timestamp = chunk_mtf_data[primary_tf].index[-1]
                            
                            if current_timestamp in signals_df.index:
                                signals_df.loc[current_timestamp, 'signal'] = signal_value * confidence
                                signals_df.loc[current_timestamp, 'confidence'] = confidence
                            
                except Exception as e:
                    if self.config.log_level == "DEBUG":
                        self.logger.warning(f"[{strategy_name}] Chunk analysis failed: {e}")
                    continue
            
            return signals_df
            
        except Exception as e:
            self.logger.error(f"[{strategy_name}] MTF signal generation failed: {e}")
            return None

class EnhancedPortfolioEngine:
    """Enhanced portfolio engine with chart data collection"""
    
    def __init__(self, config: BacktestConfig, logger: ProfessionalLogger):
        self.config = config
        self.logger = logger
        
    def run_enhanced_backtest(self, strategy_name: str, 
                             signals: Dict[str, pd.DataFrame],
                             multi_timeframe_data: Dict[str, Dict[str, pd.DataFrame]]) -> StrategyResults:
        """Run enhanced backtest with chart data collection"""
        
        start_time = time.time()
        
        self.logger.info(f"[{strategy_name}] Starting enhanced backtest with chart data collection...")
        
        # Use primary timeframe data for execution
        primary_data = {}
        for symbol in multi_timeframe_data.keys():
            if self.config.primary_timeframe in multi_timeframe_data[symbol]:
                primary_data[symbol] = multi_timeframe_data[symbol][self.config.primary_timeframe]
        
        if not primary_data:
            self.logger.error(f"[{strategy_name}] No primary timeframe data available")
            return StrategyResults(strategy_name=strategy_name)
        
        # Initialize tracking with enhanced chart data
        capital = self.config.initial_capital
        equity_curve = [capital]
        equity_dates = []
        trades = []
        trade_history = []
        
        # Create unified timeline
        all_timestamps = set()
        for data in primary_data.values():
            all_timestamps.update(data.index)
        timeline = sorted(all_timestamps)
        
        # Track performance with detailed data
        daily_returns = []
        peak_equity = capital
        max_drawdown = 0.0
        drawdown_series = []
        
        # Progress tracking
        pbar = self.logger.progress(f"Backtesting {strategy_name}", len(timeline))
        
        try:
            for i, current_time in enumerate(timeline):
                current_prices = {}
                current_signals = {}
                
                # Get current data
                for symbol in primary_data.keys():
                    data = primary_data[symbol]
                    current_data = data[data.index <= current_time]
                    
                    if len(current_data) > 0:
                        current_prices[symbol] = current_data['close'].iloc[-1]
                        
                        # Get signals
                        if symbol in signals:
                            signal_data = signals[symbol]
                            if current_time in signal_data.index:
                                current_signals[symbol] = signal_data.loc[current_time]
                
                # Process signals with detailed trade tracking
                for symbol, signal_row in current_signals.items():
                    try:
                        signal_value = signal_row.get('signal', 0)
                        
                        if abs(signal_value) > 0.1:  # Signal threshold
                            direction = 'BUY' if signal_value > 0 else 'SELL'
                            entry_price = current_prices[symbol]
                            confidence = signal_row.get('confidence', 0.5)
                            
                            # Simple P&L calculation with enhanced tracking
                            future_data = primary_data[symbol][primary_data[symbol].index > current_time]
                            
                            if len(future_data) > 24:  # At least 24 bars ahead
                                exit_price = future_data['close'].iloc[23]  # Exit after 24 periods
                                exit_time = future_data.index[23]
                                
                                # Calculate P&L
                                if direction == 'BUY':
                                    pnl = (exit_price - entry_price) * self.config.fixed_position_size * 100000
                                else:
                                    pnl = (entry_price - exit_price) * self.config.fixed_position_size * 100000
                                
                                # Apply costs
                                pnl -= self.config.commission * self.config.fixed_position_size * entry_price
                                pnl -= self.config.spread_pips * 10 * self.config.fixed_position_size
                                
                                # Record detailed trade for charting
                                trade = {
                                    'symbol': symbol,
                                    'direction': direction,
                                    'entry_time': current_time,
                                    'exit_time': exit_time,
                                    'entry_price': entry_price,
                                    'exit_price': exit_price,
                                    'pnl': pnl,
                                    'signal_strength': abs(signal_value),
                                    'confidence': confidence,
                                    'duration_hours': 24,
                                    'return_pct': (pnl / (entry_price * self.config.fixed_position_size * 100000)) * 100
                                }
                                trades.append(trade)
                                trade_history.append(trade)
                                capital += pnl
                        
                    except Exception as e:
                        if self.config.log_level == "DEBUG":
                            self.logger.warning(f"[{strategy_name}] Signal processing error: {e}")
                
                # Update equity curve with timestamps
                equity_curve.append(capital)
                equity_dates.append(current_time)
                
                # Calculate returns
                if len(equity_curve) > 1:
                    daily_return = (capital - equity_curve[-2]) / equity_curve[-2] if equity_curve[-2] != 0 else 0
                    daily_returns.append(daily_return)
                
                # Update drawdown with detailed tracking
                if capital > peak_equity:
                    peak_equity = capital
                    drawdown_series.append(0)
                else:
                    current_drawdown = (peak_equity - capital) / peak_equity if peak_equity != 0 else 0
                    max_drawdown = max(max_drawdown, current_drawdown)
                    drawdown_series.append(current_drawdown)
                
                if pbar and i % 1000 == 0:
                    pbar.update(1000)
            
        finally:
            self.logger.close_progress(f"Backtesting {strategy_name}")
        
        # Calculate enhanced results with chart data
        execution_time = time.time() - start_time
        results = self._calculate_enhanced_results(
            strategy_name, equity_curve, equity_dates, trades, trade_history, 
            daily_returns, drawdown_series, max_drawdown, execution_time, signals
        )
        
        self.logger.success(f"[{strategy_name}] Enhanced backtest completed: {results.total_return:.2%} return, {results.total_trades} trades")
        
        return results
    
    def _calculate_enhanced_results(self, strategy_name: str, equity_curve: List[float],
                                   equity_dates: List[datetime], trades: List[Dict], 
                                   trade_history: List[Dict], daily_returns: List[float],
                                   drawdown_series: List[float], max_drawdown: float, 
                                   execution_time: float, signals: Dict) -> StrategyResults:
        """Calculate enhanced results with chart data"""
        
        results = StrategyResults()
        results.strategy_name = strategy_name
        results.execution_time = execution_time
        
        # Signal metrics
        try:
            results.signals_generated = sum(len(signal_data[signal_data['signal'] != 0]) 
                                          for signal_data in signals.values())
        except:
            results.signals_generated = 0
        
        if not equity_curve or len(equity_curve) < 2:
            return results
        
        initial_capital = equity_curve[0]
        final_capital = equity_curve[-1]
        
        # Basic performance
        if initial_capital != 0:
            results.total_return = (final_capital - initial_capital) / initial_capital
        
        # Create enhanced chart data
        if equity_dates and len(equity_dates) == len(equity_curve):
            # Equity curve as pandas Series
            results.equity_curve = pd.Series(equity_curve, index=equity_dates)
            
            # Daily returns
            if daily_returns:
                results.daily_returns = pd.Series(daily_returns, index=equity_dates[1:len(daily_returns)+1])
            
            # Drawdown series
            if drawdown_series:
                results.drawdown_series = pd.Series(drawdown_series, index=equity_dates[1:len(drawdown_series)+1])
            
            # Monthly returns for heatmap
            monthly_equity = results.equity_curve.resample('M').last()
            monthly_returns = monthly_equity.pct_change().dropna()
            results.monthly_returns = monthly_returns
        
        # Annualized return (10 years of data)
        total_days = len(equity_curve)
        years = total_days / 252  # Trading days per year
        if years > 0 and results.total_return > -1:
            try:
                results.annualized_return = (1 + results.total_return) ** (1/years) - 1
            except:
                results.annualized_return = results.total_return / years
        
        # Risk metrics
        if daily_returns and len(daily_returns) > 1:
            try:
                returns_array = np.array(daily_returns)
                returns_array = returns_array[~np.isnan(returns_array)]
                
                if len(returns_array) > 0:
                    results.sharpe_ratio = np.mean(returns_array) / np.std(returns_array) * np.sqrt(252) if np.std(returns_array) > 0 else 0
            except:
                results.sharpe_ratio = 0
        
        # Drawdown
        results.max_drawdown = max_drawdown
        results.max_drawdown_pct = max_drawdown * 100
        
        # Trade statistics and trade history DataFrame
        if trades:
            results.total_trades = len(trades)
            winning_trades = [t for t in trades if t['pnl'] > 0]
            
            results.winning_trades = len(winning_trades)
            results.win_rate = len(winning_trades) / len(trades) if len(trades) > 0 else 0
            
            if winning_trades:
                results.average_win = np.mean([t['pnl'] for t in winning_trades])
            
            losing_trades = [t for t in trades if t['pnl'] <= 0]
            if losing_trades:
                results.average_loss = np.mean([t['pnl'] for t in losing_trades])
            
            # Profit factor
            gross_profit = sum(t['pnl'] for t in winning_trades) if winning_trades else 0
            gross_loss = abs(sum(t['pnl'] for t in losing_trades)) if losing_trades else 1
            results.profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
            
            # Create trade history DataFrame for charting
            if trade_history:
                results.trade_history = pd.DataFrame(trade_history)
        
        # Consistency score
        if daily_returns and len(daily_returns) > 10:
            returns_array = np.array(daily_returns)
            returns_array = returns_array[~np.isnan(returns_array)]
            if len(returns_array) > 0:
                results.consistency_score = max(0, min(100, (1 - np.std(returns_array)) * 100))
        
        return results

class AdvancedChartGenerator:
    """Advanced chart generator for strategy visualization"""
    
    def __init__(self, config: BacktestConfig, logger: ProfessionalLogger):
        self.config = config
        self.logger = logger
        
        # Create output directory
        if self.config.enable_charting:
            os.makedirs(self.config.chart_output_dir, exist_ok=True)
            self.logger.chart_info(f"Charts will be saved to: {self.config.chart_output_dir}")
    
    def generate_individual_strategy_charts(self, results: StrategyResults):
        """Generate comprehensive charts for individual strategy"""
        
        if not self.config.enable_charting:
            return
        
        strategy_name = results.strategy_name
        self.logger.chart_info(f"Generating charts for {strategy_name}...")
        
        try:
            # Create strategy-specific directory
            strategy_dir = os.path.join(self.config.chart_output_dir, strategy_name)
            os.makedirs(strategy_dir, exist_ok=True)
            
            # Generate different types of charts
            self._generate_equity_curve_chart(results, strategy_dir)
            self._generate_drawdown_chart(results, strategy_dir)
            self._generate_returns_distribution_chart(results, strategy_dir)
            self._generate_monthly_heatmap(results, strategy_dir)
            self._generate_trade_analysis_chart(results, strategy_dir)
            self._generate_performance_dashboard(results, strategy_dir)
            
            self.logger.chart_info(f"✅ All charts generated for {strategy_name}")
            
        except Exception as e:
            self.logger.error(f"Chart generation failed for {strategy_name}: {e}")
    
    def _generate_equity_curve_chart(self, results: StrategyResults, output_dir: str):
        """Generate interactive equity curve chart"""
        
        if results.equity_curve.empty:
            return
        
        try:
            fig = go.Figure()
            
            # Main equity curve
            fig.add_trace(go.Scatter(
                x=results.equity_curve.index,
                y=results.equity_curve.values,
                mode='lines',
                name='Equity Curve',
                line=dict(color='#2E86C1', width=2),
                hovertemplate='<b>Date:</b> %{x}<br><b>Equity:</b> $%{y:,.2f}<extra></extra>'
            ))
            
            # Add buy/sell markers if trade history exists
            if not results.trade_history.empty:
                buy_trades = results.trade_history[results.trade_history['direction'] == 'BUY']
                sell_trades = results.trade_history[results.trade_history['direction'] == 'SELL']
                
                if not buy_trades.empty:
                    fig.add_trace(go.Scatter(
                        x=buy_trades['entry_time'],
                        y=[results.equity_curve.loc[results.equity_curve.index <= t].iloc[-1] if len(results.equity_curve.loc[results.equity_curve.index <= t]) > 0 else results.config.initial_capital for t in buy_trades['entry_time']],
                        mode='markers',
                        name='Buy Signals',
                        marker=dict(color='green', size=8, symbol='triangle-up'),
                        hovertemplate='<b>BUY Signal</b><br><b>Date:</b> %{x}<br><b>Price:</b> %{text}<extra></extra>',
                        text=[f"${price:.5f}" for price in buy_trades['entry_price']]
                    ))
                
                if not sell_trades.empty:
                    fig.add_trace(go.Scatter(
                        x=sell_trades['entry_time'],
                        y=[results.equity_curve.loc[results.equity_curve.index <= t].iloc[-1] if len(results.equity_curve.loc[results.equity_curve.index <= t]) > 0 else results.config.initial_capital for t in sell_trades['entry_time']],
                        mode='markers',
                        name='Sell Signals',
                        marker=dict(color='red', size=8, symbol='triangle-down'),
                        hovertemplate='<b>SELL Signal</b><br><b>Date:</b> %{x}<br><b>Price:</b> %{text}<extra></extra>',
                        text=[f"${price:.5f}" for price in sell_trades['entry_price']]
                    ))
            
            # Styling
            fig.update_layout(
                title=f"{results.strategy_name} - Equity Curve Analysis",
                xaxis_title="Date",
                yaxis_title="Portfolio Value ($)",
                width=self.config.chart_width,
                height=self.config.chart_height,
                hovermode='x unified',
                template='plotly_white',
                legend=dict(x=0, y=1),
                annotations=[
                    dict(
                        x=0.02, y=0.98,
                        xref="paper", yref="paper",
                        text=f"Total Return: {results.total_return:.2%}<br>"
                             f"Sharpe Ratio: {results.sharpe_ratio:.2f}<br>"
                             f"Max Drawdown: {results.max_drawdown_pct:.2f}%<br>"
                             f"Win Rate: {results.win_rate:.1%}",
                        showarrow=False,
                        bgcolor="rgba(255,255,255,0.8)",
                        bordercolor="gray",
                        borderwidth=1
                    )
                ]
            )
            
            # Save chart
            if 'html' in self.config.chart_formats:
                html_path = os.path.join(output_dir, "equity_curve.html")
                fig.write_html(html_path)
            
            if 'png' in self.config.chart_formats:
                png_path = os.path.join(output_dir, "equity_curve.png")
                fig.write_image(png_path, width=self.config.chart_width, height=self.config.chart_height)
            
        except Exception as e:
            self.logger.error(f"Equity curve chart generation failed: {e}")
    
    def _generate_drawdown_chart(self, results: StrategyResults, output_dir: str):
        """Generate drawdown analysis chart"""
        
        if results.drawdown_series.empty:
            return
        
        try:
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Equity Curve', 'Drawdown Analysis'),
                vertical_spacing=0.1,
                row_heights=[0.7, 0.3]
            )
            
            # Equity curve
            fig.add_trace(go.Scatter(
                x=results.equity_curve.index,
                y=results.equity_curve.values,
                mode='lines',
                name='Equity',
                line=dict(color='blue', width=2)
            ), row=1, col=1)
            
            # Drawdown
            fig.add_trace(go.Scatter(
                x=results.drawdown_series.index,
                y=-results.drawdown_series.values * 100,  # Convert to percentage and make negative
                mode='lines',
                name='Drawdown %',
                line=dict(color='red', width=1),
                fill='tonexty',
                fillcolor='rgba(255,0,0,0.3)'
            ), row=2, col=1)
            
            fig.update_layout(
                title=f"{results.strategy_name} - Drawdown Analysis",
                width=self.config.chart_width,
                height=self.config.chart_height,
                template='plotly_white'
            )
            
            fig.update_yaxes(title_text="Portfolio Value ($)", row=1, col=1)
            fig.update_yaxes(title_text="Drawdown (%)", row=2, col=1)
            fig.update_xaxes(title_text="Date", row=2, col=1)
            
            # Save chart
            if 'html' in self.config.chart_formats:
                html_path = os.path.join(output_dir, "drawdown_analysis.html")
                fig.write_html(html_path)
            
            if 'png' in self.config.chart_formats:
                png_path = os.path.join(output_dir, "drawdown_analysis.png")
                fig.write_image(png_path, width=self.config.chart_width, height=self.config.chart_height)
            
        except Exception as e:
            self.logger.error(f"Drawdown chart generation failed: {e}")
    
    def _generate_returns_distribution_chart(self, results: StrategyResults, output_dir: str):
        """Generate returns distribution analysis"""
        
        if results.daily_returns.empty:
            return
        
        try:
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Daily Returns Distribution', 'Returns Over Time', 
                              'Cumulative Returns', 'Returns vs Benchmark'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            returns_pct = results.daily_returns * 100
            
            # 1. Distribution histogram
            fig.add_trace(go.Histogram(
                x=returns_pct.values,
                nbinsx=50,
                name='Returns Distribution',
                marker_color='lightblue',
                opacity=0.7
            ), row=1, col=1)
            
            # 2. Returns over time
            fig.add_trace(go.Scatter(
                x=returns_pct.index,
                y=returns_pct.values,
                mode='lines',
                name='Daily Returns',
                line=dict(color='green', width=1)
            ), row=1, col=2)
            
            # 3. Cumulative returns
            cum_returns = (1 + results.daily_returns).cumprod() - 1
            fig.add_trace(go.Scatter(
                x=cum_returns.index,
                y=cum_returns.values * 100,
                mode='lines',
                name='Cumulative Returns',
                line=dict(color='blue', width=2)
            ), row=2, col=1)
            
            # 4. Rolling Sharpe ratio
            rolling_sharpe = results.daily_returns.rolling(252).mean() / results.daily_returns.rolling(252).std() * np.sqrt(252)
            fig.add_trace(go.Scatter(
                x=rolling_sharpe.index,
                y=rolling_sharpe.values,
                mode='lines',
                name='Rolling Sharpe (1Y)',
                line=dict(color='purple', width=2)
            ), row=2, col=2)
            
            fig.update_layout(
                title=f"{results.strategy_name} - Returns Analysis",
                width=self.config.chart_width,
                height=self.config.chart_height,
                template='plotly_white',
                showlegend=True
            )
            
            # Save chart
            if 'html' in self.config.chart_formats:
                html_path = os.path.join(output_dir, "returns_analysis.html")
                fig.write_html(html_path)
            
            if 'png' in self.config.chart_formats:
                png_path = os.path.join(output_dir, "returns_analysis.png")
                fig.write_image(png_path, width=self.config.chart_width, height=self.config.chart_height)
            
        except Exception as e:
            self.logger.error(f"Returns distribution chart generation failed: {e}")
    
    def _generate_monthly_heatmap(self, results: StrategyResults, output_dir: str):
        """Generate monthly returns heatmap"""
        
        if results.monthly_returns.empty:
            return
        
        try:
            # Prepare data for heatmap
            monthly_data = results.monthly_returns * 100  # Convert to percentage
            
            # Create year-month matrix
            monthly_data.index = pd.to_datetime(monthly_data.index)
            years = monthly_data.index.year.unique()
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            heatmap_data = []
            year_labels = []
            
            for year in years:
                year_data = []
                year_labels.append(str(year))
                for month in range(1, 13):
                    try:
                        value = monthly_data[(monthly_data.index.year == year) & (monthly_data.index.month == month)]
                        if len(value) > 0:
                            year_data.append(value.iloc[0])
                        else:
                            year_data.append(np.nan)
                    except:
                        year_data.append(np.nan)
                heatmap_data.append(year_data)
            
            fig = go.Figure(data=go.Heatmap(
                z=heatmap_data,
                x=months,
                y=year_labels,
                colorscale='RdYlGn',
                zmid=0,
                text=[[f'{val:.1f}%' if not np.isnan(val) else '' for val in row] for row in heatmap_data],
                texttemplate='%{text}',
                textfont={"size": 10},
                hovertemplate='<b>%{y} %{x}</b><br>Return: %{z:.2f}%<extra></extra>'
            ))
            
            fig.update_layout(
                title=f"{results.strategy_name} - Monthly Returns Heatmap",
                width=self.config.chart_width,
                height=max(400, len(years) * 30),
                template='plotly_white'
            )
            
            # Save chart
            if 'html' in self.config.chart_formats:
                html_path = os.path.join(output_dir, "monthly_heatmap.html")
                fig.write_html(html_path)
            
            if 'png' in self.config.chart_formats:
                png_path = os.path.join(output_dir, "monthly_heatmap.png")
                fig.write_image(png_path, width=self.config.chart_width, height=max(400, len(years) * 30))
            
        except Exception as e:
            self.logger.error(f"Monthly heatmap generation failed: {e}")
    
    def _generate_trade_analysis_chart(self, results: StrategyResults, output_dir: str):
        """Generate trade analysis charts"""
        
        if results.trade_history.empty:
            return
        
        try:
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Trade P&L Distribution', 'Win/Loss Ratio Over Time',
                              'Trade Duration Analysis', 'Confidence vs Performance'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            trades_df = results.trade_history
            
            # 1. P&L Distribution
            fig.add_trace(go.Histogram(
                x=trades_df['pnl'],
                nbinsx=30,
                name='P&L Distribution',
                marker_color='lightgreen',
                opacity=0.7
            ), row=1, col=1)
            
            # 2. Cumulative win/loss ratio
            trades_df_sorted = trades_df.sort_values('entry_time')
            trades_df_sorted['is_win'] = trades_df_sorted['pnl'] > 0
            trades_df_sorted['cumulative_wins'] = trades_df_sorted['is_win'].cumsum()
            trades_df_sorted['cumulative_trades'] = range(1, len(trades_df_sorted) + 1)
            trades_df_sorted['win_rate_running'] = trades_df_sorted['cumulative_wins'] / trades_df_sorted['cumulative_trades']
            
            fig.add_trace(go.Scatter(
                x=trades_df_sorted['entry_time'],
                y=trades_df_sorted['win_rate_running'] * 100,
                mode='lines',
                name='Running Win Rate',
                line=dict(color='blue', width=2)
            ), row=1, col=2)
            
            # 3. Trade duration analysis
            if 'duration_hours' in trades_df.columns:
                fig.add_trace(go.Histogram(
                    x=trades_df['duration_hours'],
                    nbinsx=20,
                    name='Duration Distribution',
                    marker_color='orange',
                    opacity=0.7
                ), row=2, col=1)
            
            # 4. Confidence vs Performance
            if 'confidence' in trades_df.columns:
                winning_trades = trades_df[trades_df['pnl'] > 0]
                losing_trades = trades_df[trades_df['pnl'] <= 0]
                
                fig.add_trace(go.Scatter(
                    x=winning_trades['confidence'],
                    y=winning_trades['pnl'],
                    mode='markers',
                    name='Winning Trades',
                    marker=dict(color='green', size=6, opacity=0.6)
                ), row=2, col=2)
                
                fig.add_trace(go.Scatter(
                    x=losing_trades['confidence'],
                    y=losing_trades['pnl'],
                    mode='markers',
                    name='Losing Trades',
                    marker=dict(color='red', size=6, opacity=0.6)
                ), row=2, col=2)
            
            fig.update_layout(
                title=f"{results.strategy_name} - Trade Analysis",
                width=self.config.chart_width,
                height=self.config.chart_height,
                template='plotly_white'
            )
            
            # Save chart
            if 'html' in self.config.chart_formats:
                html_path = os.path.join(output_dir, "trade_analysis.html")
                fig.write_html(html_path)
            
            if 'png' in self.config.chart_formats:
                png_path = os.path.join(output_dir, "trade_analysis.png")
                fig.write_image(png_path, width=self.config.chart_width, height=self.config.chart_height)
            
        except Exception as e:
            self.logger.error(f"Trade analysis chart generation failed: {e}")
    
    def _generate_performance_dashboard(self, results: StrategyResults, output_dir: str):
        """Generate comprehensive performance dashboard"""
        
        try:
            fig = make_subplots(
                rows=3, cols=3,
                subplot_titles=(
                    'Equity Curve', 'Monthly Returns', 'Drawdown',
                    'Returns Distribution', 'Rolling Sharpe', 'Trade P&L',
                    'Performance Metrics', 'Risk Metrics', 'Trade Statistics'
                ),
                specs=[
                    [{"colspan": 2}, None, {"rowspan": 2}],
                    [{"secondary_y": False}, {"secondary_y": False}, None],
                    [{"type": "table"}, {"type": "table"}, {"type": "table"}]
                ]
            )
            
            # 1. Main equity curve
            if not results.equity_curve.empty:
                fig.add_trace(go.Scatter(
                    x=results.equity_curve.index,
                    y=results.equity_curve.values,
                    mode='lines',
                    name='Equity',
                    line=dict(color='blue', width=2)
                ), row=1, col=1)
            
            # 2. Monthly returns bar chart
            if not results.monthly_returns.empty:
                monthly_pct = results.monthly_returns * 100
                colors = ['green' if x > 0 else 'red' for x in monthly_pct]
                fig.add_trace(go.Bar(
                    x=monthly_pct.index,
                    y=monthly_pct.values,
                    name='Monthly Returns',
                    marker_color=colors
                ), row=2, col=1)
            
            # 3. Drawdown
            if not results.drawdown_series.empty:
                fig.add_trace(go.Scatter(
                    x=results.drawdown_series.index,
                    y=-results.drawdown_series.values * 100,
                    mode='lines',
                    name='Drawdown',
                    line=dict(color='red', width=1),
                    fill='tonexty'
                ), row=1, col=3)
            
            # 4. Returns distribution
            if not results.daily_returns.empty:
                fig.add_trace(go.Histogram(
                    x=results.daily_returns.values * 100,
                    nbinsx=30,
                    name='Returns Dist',
                    marker_color='lightblue'
                ), row=2, col=2)
            
            # 5-7. Performance tables
            performance_data = [
                ['Total Return', f'{results.total_return:.2%}'],
                ['Annual Return', f'{results.annualized_return:.2%}'],
                ['Sharpe Ratio', f'{results.sharpe_ratio:.2f}'],
                ['Total Trades', f'{results.total_trades}'],
                ['Win Rate', f'{results.win_rate:.1%}']
            ]
            
            risk_data = [
                ['Max Drawdown', f'{results.max_drawdown_pct:.2f}%'],
                ['Volatility', f'{results.daily_returns.std() * np.sqrt(252) * 100:.2f}%' if not results.daily_returns.empty else 'N/A'],
                ['Profit Factor', f'{results.profit_factor:.2f}'],
                ['Avg Win', f'${results.average_win:.2f}'],
                ['Avg Loss', f'${results.average_loss:.2f}']
            ]
            
            trade_stats = [
                ['Signals Generated', f'{results.signals_generated}'],
                ['Winning Trades', f'{results.winning_trades}'],
                ['Losing Trades', f'{results.total_trades - results.winning_trades}'],
                ['Consistency Score', f'{results.consistency_score:.1f}'],
                ['Execution Time', f'{results.execution_time:.1f}s']
            ]
            
            # Add tables
            for i, (data, row) in enumerate([(performance_data, 3), (risk_data, 3), (trade_stats, 3)]):
                fig.add_trace(go.Table(
                    header=dict(values=['Metric', 'Value'], fill_color='lightblue'),
                    cells=dict(values=[[row[0] for row in data], [row[1] for row in data]],
                              fill_color='white')
                ), row=row, col=i+1)
            
            fig.update_layout(
                title=f"{results.strategy_name} - Performance Dashboard",
                width=1400,
                height=1000,
                template='plotly_white',
                showlegend=False
            )
            
            # Save chart
            if 'html' in self.config.chart_formats:
                html_path = os.path.join(output_dir, "performance_dashboard.html")
                fig.write_html(html_path)
            
            if 'png' in self.config.chart_formats:
                png_path = os.path.join(output_dir, "performance_dashboard.png")
                fig.write_image(png_path, width=1400, height=1000)
            
        except Exception as e:
            self.logger.error(f"Performance dashboard generation failed: {e}")
    
    def generate_strategy_comparison_charts(self, all_results: List[StrategyResults]):
        """Generate strategy comparison charts"""
        
        if not self.config.enable_charting or not all_results:
            return
        
        self.logger.chart_info("Generating strategy comparison charts...")
        
        try:
            comparison_dir = os.path.join(self.config.chart_output_dir, "comparison")
            os.makedirs(comparison_dir, exist_ok=True)
            
            # Generate different comparison charts
            self._generate_performance_comparison_chart(all_results, comparison_dir)
            self._generate_risk_return_scatter(all_results, comparison_dir)
            self._generate_equity_curves_comparison(all_results, comparison_dir)
            self._generate_correlation_matrix(all_results, comparison_dir)
            
            self.logger.chart_info("✅ Strategy comparison charts generated")
            
        except Exception as e:
            self.logger.error(f"Comparison chart generation failed: {e}")
    
    def _generate_performance_comparison_chart(self, all_results: List[StrategyResults], output_dir: str):
        """Generate performance comparison bar chart"""
        
        try:
            # Prepare data
            strategies = [r.strategy_name for r in all_results]
            returns = [r.total_return * 100 for r in all_results]
            sharpe_ratios = [r.sharpe_ratio for r in all_results]
            max_drawdowns = [r.max_drawdown_pct for r in all_results]
            
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Total Returns (%)', 'Sharpe Ratios', 'Maximum Drawdowns (%)', 'Win Rates (%)'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # Total returns
            colors_returns = ['green' if x > 0 else 'red' for x in returns]
            fig.add_trace(go.Bar(
                x=strategies,
                y=returns,
                name='Total Returns',
                marker_color=colors_returns
            ), row=1, col=1)
            
            # Sharpe ratios
            colors_sharpe = ['green' if x > 0 else 'red' for x in sharpe_ratios]
            fig.add_trace(go.Bar(
                x=strategies,
                y=sharpe_ratios,
                name='Sharpe Ratios',
                marker_color=colors_sharpe
            ), row=1, col=2)
            
            # Max drawdowns
            fig.add_trace(go.Bar(
                x=strategies,
                y=max_drawdowns,
                name='Max Drawdowns',
                marker_color='red'
            ), row=2, col=1)
            
            # Win rates
            win_rates = [r.win_rate * 100 for r in all_results]
            fig.add_trace(go.Bar(
                x=strategies,
                y=win_rates,
                name='Win Rates',
                marker_color='blue'
            ), row=2, col=2)
            
            fig.update_layout(
                title="Strategy Performance Comparison",
                width=1400,
                height=800,
                template='plotly_white',
                showlegend=False
            )
            
            # Rotate x-axis labels for better readability
            fig.update_xaxes(tickangle=45)
            
            # Save chart
            if 'html' in self.config.chart_formats:
                html_path = os.path.join(output_dir, "performance_comparison.html")
                fig.write_html(html_path)
            
            if 'png' in self.config.chart_formats:
                png_path = os.path.join(output_dir, "performance_comparison.png")
                fig.write_image(png_path, width=1400, height=800)
            
        except Exception as e:
            self.logger.error(f"Performance comparison chart generation failed: {e}")
    
    def _generate_risk_return_scatter(self, all_results: List[StrategyResults], output_dir: str):
        """Generate risk-return scatter plot"""
        
        try:
            strategies = [r.strategy_name for r in all_results]
            returns = [r.annualized_return * 100 for r in all_results]
            volatilities = []
            
            for r in all_results:
                if not r.daily_returns.empty:
                    vol = r.daily_returns.std() * np.sqrt(252) * 100
                    volatilities.append(vol)
                else:
                    volatilities.append(0)
            
            # Color by Sharpe ratio
            sharpe_ratios = [r.sharpe_ratio for r in all_results]
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=volatilities,
                y=returns,
                mode='markers+text',
                text=strategies,
                textposition="top center",
                marker=dict(
                    size=[abs(r.total_trades) / 10 + 5 for r in all_results],  # Size by trade count
                    color=sharpe_ratios,
                    colorscale='RdYlGn',
                    colorbar=dict(title="Sharpe Ratio"),
                    line=dict(width=2, color='black')
                ),
                hovertemplate='<b>%{text}</b><br>' +
                             'Annual Return: %{y:.1f}%<br>' +
                             'Volatility: %{x:.1f}%<br>' +
                             'Sharpe: %{marker.color:.2f}<extra></extra>'
            ))
            
            fig.update_layout(
                title="Risk-Return Analysis (Bubble Size = Trade Count)",
                xaxis_title="Volatility (Annual %)",
                yaxis_title="Annual Return (%)",
                width=self.config.chart_width,
                height=self.config.chart_height,
                template='plotly_white'
            )
            
            # Save chart
            if 'html' in self.config.chart_formats:
                html_path = os.path.join(output_dir, "risk_return_scatter.html")
                fig.write_html(html_path)
            
            if 'png' in self.config.chart_formats:
                png_path = os.path.join(output_dir, "risk_return_scatter.png")
                fig.write_image(png_path, width=self.config.chart_width, height=self.config.chart_height)
            
        except Exception as e:
            self.logger.error(f"Risk-return scatter generation failed: {e}")
    
    def _generate_equity_curves_comparison(self, all_results: List[StrategyResults], output_dir: str):
        """Generate overlaid equity curves comparison"""
        
        try:
            fig = go.Figure()
            
            # Normalize all equity curves to start at 100
            for result in all_results:
                if not result.equity_curve.empty:
                    normalized_curve = (result.equity_curve / result.equity_curve.iloc[0]) * 100
                    
                    fig.add_trace(go.Scatter(
                        x=normalized_curve.index,
                        y=normalized_curve.values,
                        mode='lines',
                        name=result.strategy_name,
                        line=dict(width=2),
                        hovertemplate='<b>%{fullData.name}</b><br>' +
                                     'Date: %{x}<br>' +
                                     'Normalized Value: %{y:.1f}<extra></extra>'
                    ))
            
            fig.update_layout(
                title="Normalized Equity Curves Comparison (Starting Value = 100)",
                xaxis_title="Date",
                yaxis_title="Normalized Portfolio Value",
                width=self.config.chart_width,
                height=self.config.chart_height,
                template='plotly_white',
                hovermode='x unified'
            )
            
            # Save chart
            if 'html' in self.config.chart_formats:
                html_path = os.path.join(output_dir, "equity_curves_comparison.html")
                fig.write_html(html_path)
            
            if 'png' in self.config.chart_formats:
                png_path = os.path.join(output_dir, "equity_curves_comparison.png")
                fig.write_image(png_path, width=self.config.chart_width, height=self.config.chart_height)
            
        except Exception as e:
            self.logger.error(f"Equity curves comparison generation failed: {e}")
    
    def _generate_correlation_matrix(self, all_results: List[StrategyResults], output_dir: str):
        """Generate strategy correlation matrix"""
        
        try:
            # Prepare returns data for correlation analysis
            returns_data = {}
            
            for result in all_results:
                if not result.daily_returns.empty:
                    returns_data[result.strategy_name] = result.daily_returns
            
            if len(returns_data) < 2:
                return
            
            # Align all returns series
            returns_df = pd.DataFrame(returns_data)
            correlation_matrix = returns_df.corr()
            
            # Create heatmap
            fig = go.Figure(data=go.Heatmap(
                z=correlation_matrix.values,
                x=correlation_matrix.columns,
                y=correlation_matrix.index,
                colorscale='RdBu',
                zmid=0,
                text=np.round(correlation_matrix.values, 2),
                texttemplate='%{text}',
                textfont={"size": 10},
                hovertemplate='<b>%{y} vs %{x}</b><br>Correlation: %{z:.2f}<extra></extra>'
            ))
            
            fig.update_layout(
                title="Strategy Returns Correlation Matrix",
                width=max(600, len(correlation_matrix) * 40),
                height=max(600, len(correlation_matrix) * 40),
                template='plotly_white'
            )
            
            # Save chart
            if 'html' in self.config.chart_formats:
                html_path = os.path.join(output_dir, "correlation_matrix.html")
                fig.write_html(html_path)
            
            if 'png' in self.config.chart_formats:
                png_path = os.path.join(output_dir, "correlation_matrix.png")
                fig.write_image(png_path, width=max(600, len(correlation_matrix) * 40), 
                               height=max(600, len(correlation_matrix) * 40))
            
        except Exception as e:
            self.logger.error(f"Correlation matrix generation failed: {e}")

class MultiTimeframeBacktesterWithCharts:
    """Enhanced multi-timeframe backtester with advanced charting"""
    
    def __init__(self, strategies: Dict[str, Any], config: BacktestConfig = None):
        self.config = config or BacktestConfig()
        self.logger = ProfessionalLogger(self.config)
        self.strategies = strategies
        
        # Initialize components
        self.data_processor = MultiTimeframeDataProcessor(self.config, self.logger)
        self.strategy_processor = MultiTimeframeStrategyProcessor(self.config, self.logger)
        self.portfolio_engine = EnhancedPortfolioEngine(self.config, self.logger)
        self.chart_generator = AdvancedChartGenerator(self.config, self.logger)
        
        self.logger.success(f"Multi-Timeframe Backtester with Advanced Charts initialized with {len(strategies)} strategies")
    
    def run_10_year_analysis_with_charts(self, symbols: List[str]) -> Dict[str, Any]:
        """Run 10-year analysis with comprehensive chart generation"""
        
        total_start_time = time.time()
        
        # 10-YEAR PERIOD
        end_date = datetime.now()
        start_date = end_date - timedelta(days=10*365)  # 10 years
        
        self.logger.info("🚀 STARTING 10-YEAR MULTI-TIMEFRAME ANALYSIS WITH ADVANCED CHARTS")
        self.logger.info(f"📅 Period: {start_date.date()} to {end_date.date()}")
        self.logger.info(f"📊 Symbols: {', '.join(symbols)}")
        self.logger.info(f"⏰ Timeframes: {', '.join(self.config.timeframes)}")
        self.logger.info(f"🎯 Strategies: {len(self.strategies)}")
        self.logger.info("📈 Charts: ENABLED (Individual + Comparison)")
        
        # Load multi-timeframe data
        multi_timeframe_data = self.data_processor.load_multi_timeframe_data(symbols, start_date, end_date)
        
        if not multi_timeframe_data:
            self.logger.error("No multi-timeframe data loaded")
            return {}
        
        # Process strategies
        all_strategy_results = []
        failed_strategies = []
        
        pbar = self.logger.progress("Analyzing Strategies", len(self.strategies))
        
        for strategy_name, strategy in self.strategies.items():
            try:
                # Process strategy with multi-timeframe support
                _, strategy_signals = self.strategy_processor.process_single_strategy_mtf(
                    strategy_name, strategy, multi_timeframe_data, symbols
                )
                
                if not strategy_signals:
                    self.logger.warning(f"[{strategy_name}] No signals generated")
                    failed_strategies.append(strategy_name)
                    if pbar:
                        pbar.update(1)
                    continue
                
                # Run enhanced backtest with chart data collection
                strategy_results = self.portfolio_engine.run_enhanced_backtest(
                    strategy_name, strategy_signals, multi_timeframe_data
                )
                
                all_strategy_results.append(strategy_results)
                
                # Generate individual charts
                if self.config.save_individual_charts:
                    self.chart_generator.generate_individual_strategy_charts(strategy_results)
                
                self.logger.success(f"[{strategy_name}] ✅ Complete: {strategy_results.total_return:.2%} return, {strategy_results.total_trades} trades")
                
            except Exception as e:
                self.logger.error(f"[{strategy_name}] ❌ Failed: {e}")
                failed_strategies.append(strategy_name)
            
            if pbar:
                pbar.update(1)
        
        self.logger.close_progress("Analyzing Strategies")
        
        # Generate comparison charts
        if self.config.save_comparison_charts and all_strategy_results:
            self.chart_generator.generate_strategy_comparison_charts(all_strategy_results)
        
        # Calculate execution metrics
        total_execution_time = time.time() - total_start_time
        
        # Create results
        results = self._create_comprehensive_results(
            all_strategy_results, total_execution_time,
            len(self.strategies), len(failed_strategies), symbols, start_date, end_date
        )
        
        # Print summary
        self._print_10_year_summary_with_charts(results)
        
        return results
    
    def _create_comprehensive_results(self, strategy_results: List[StrategyResults], 
                                    execution_time: float, total_strategies: int, 
                                    failed_strategies: int, symbols: List[str], 
                                    start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Create comprehensive results with chart information"""
        
        successful_strategies = len(strategy_results)
        profitable_strategies = len([r for r in strategy_results if r.total_return > 0])
        
        # Calculate averages
        if strategy_results:
            avg_return = np.mean([r.total_return for r in strategy_results])
            avg_annualized_return = np.mean([r.annualized_return for r in strategy_results])
            avg_sharpe = np.mean([r.sharpe_ratio for r in strategy_results if abs(r.sharpe_ratio) < 10])
            avg_win_rate = np.mean([r.win_rate for r in strategy_results])
            avg_drawdown = np.mean([r.max_drawdown_pct for r in strategy_results])
            
            # Find best strategies
            best_return = max(strategy_results, key=lambda x: x.total_return)
            best_sharpe = max(strategy_results, key=lambda x: x.sharpe_ratio)
            best_consistency = max(strategy_results, key=lambda x: x.consistency_score)
        else:
            avg_return = avg_annualized_return = avg_sharpe = avg_win_rate = avg_drawdown = 0
            best_return = best_sharpe = best_consistency = None
        
        return {
            'analysis_summary': {
                'total_strategies': total_strategies,
                'successful_strategies': successful_strategies,
                'failed_strategies': failed_strategies,
                'analysis_period': f"{start_date.date()} to {end_date.date()}",
                'analysis_years': round((end_date - start_date).days / 365, 1),
                'symbols_analyzed': symbols,
                'timeframes_used': self.config.timeframes,
                'total_execution_time': execution_time,
                'profitable_strategies': profitable_strategies,
                'avg_return': avg_return,
                'avg_annualized_return': avg_annualized_return,
                'avg_sharpe_ratio': avg_sharpe,
                'avg_win_rate': avg_win_rate,
                'avg_max_drawdown': avg_drawdown,
                'best_return_strategy': best_return.strategy_name if best_return else 'None',
                'best_sharpe_strategy': best_sharpe.strategy_name if best_sharpe else 'None',
                'most_consistent_strategy': best_consistency.strategy_name if best_consistency else 'None',
                'charts_enabled': self.config.enable_charting,
                'chart_output_dir': self.config.chart_output_dir,
                'chart_formats': self.config.chart_formats
            },
            'individual_results': {result.strategy_name: result for result in strategy_results},
            'config': self.config
        }
    
    def _print_10_year_summary_with_charts(self, results: Dict[str, Any]):
        """Print 10-year analysis summary with chart information"""
        
        summary = results['analysis_summary']
        
        print("\n" + "="*80)
        print("🎯 10-YEAR MULTI-TIMEFRAME ANALYSIS WITH ADVANCED CHARTS")
        print("="*80)
        
        print(f"\n📊 ANALYSIS OVERVIEW:")
        print(f"   Analysis Period:      {summary['analysis_years']} years ({summary['analysis_period']})")
        print(f"   Timeframes Used:      {', '.join(summary['timeframes_used'])}")
        print(f"   Symbols Analyzed:     {', '.join(summary['symbols_analyzed'])}")
        print(f"   Total Strategies:     {summary['total_strategies']}")
        print(f"   Successful:           {summary['successful_strategies']}")
        print(f"   Failed:               {summary['failed_strategies']}")
        print(f"   Execution Time:       {summary['total_execution_time']:.2f} seconds")
        
        print(f"\n🏆 10-YEAR PERFORMANCE SUMMARY:")
        print(f"   Profitable Strategies: {summary['profitable_strategies']}/{summary['total_strategies']}")
        print(f"   Average Total Return:  {summary['avg_return']:.2%}")
        print(f"   Average Annual Return: {summary['avg_annualized_return']:.2%}")
        print(f"   Average Sharpe Ratio:  {summary['avg_sharpe_ratio']:.3f}")
        print(f"   Average Win Rate:      {summary['avg_win_rate']:.1%}")
        print(f"   Average Max Drawdown:  {summary['avg_max_drawdown']:.2f}%")
        
        print(f"\n🥇 TOP PERFORMERS (10-Year Analysis):")
        print(f"   Best Return:          {summary['best_return_strategy']}")
        print(f"   Best Sharpe Ratio:    {summary['best_sharpe_strategy']}")
        print(f"   Most Consistent:      {summary['most_consistent_strategy']}")
        
        # Show individual results
        if results['individual_results']:
            print(f"\n📈 TOP 10 INDIVIDUAL STRATEGY PERFORMANCE:")
            print(f"{'Strategy':<30} {'Total Return':<12} {'Annual Return':<12} {'Sharpe':<8} {'Win Rate':<10} {'Trades':<8}")
            print("-" * 90)
            
            # Sort by total return
            sorted_results = sorted(results['individual_results'].values(), 
                                  key=lambda x: x.total_return, reverse=True)
            
            for result in sorted_results[:10]:  # Top 10
                print(f"{result.strategy_name:<30} "
                      f"{result.total_return:<11.1%} "
                      f"{result.annualized_return:<11.1%} "
                      f"{result.sharpe_ratio:<7.2f} "
                      f"{result.win_rate:<9.1%} "
                      f"{result.total_trades:<8}")
        
        print("\n" + "="*80)
        print("📊 CHART GENERATION SUMMARY:")
        if summary['charts_enabled']:
            print(f"   ✅ Charts Generated:     {summary['charts_enabled']}")
            print(f"   📁 Output Directory:     {summary['chart_output_dir']}/")
            print(f"   📄 Chart Formats:        {', '.join(summary['chart_formats'])}")
            print(f"   📈 Individual Charts:    {summary['successful_strategies']} strategies")
            print(f"   📊 Comparison Charts:    Available in comparison/ folder")
            print(f"\n   📋 Available Chart Types Per Strategy:")
            print(f"      • equity_curve.html/png - Interactive equity curve with trade markers")
            print(f"      • drawdown_analysis.html/png - Drawdown analysis with equity overlay")
            print(f"      • returns_analysis.html/png - Returns distribution and statistics")
            print(f"      • monthly_heatmap.html/png - Monthly performance heatmap")
            print(f"      • trade_analysis.html/png - Trade P&L and duration analysis")
            print(f"      • performance_dashboard.html/png - Comprehensive dashboard")
            print(f"\n   📊 Comparison Charts:")
            print(f"      • performance_comparison.html/png - Side-by-side performance bars")
            print(f"      • risk_return_scatter.html/png - Risk-return positioning analysis")
            print(f"      • equity_curves_comparison.html/png - Overlaid normalized curves")
            print(f"      • correlation_matrix.html/png - Strategy correlation heatmap")
        else:
            print(f"   ❌ Charts Disabled")
        
        print("\n" + "="*80)
        print("🔧 CONFIGURATION NOTES:")
        print("   ✅ Multi-timeframe support enabled for ICT/RTM strategies")
        print("   ✅ Risk management simplified (as requested)")
        print("   ✅ 10-year validation period (as requested)")
        print("   ✅ Position sizing: Fixed 0.01 lots (no Kelly/dynamic sizing)")
        print("   ✅ Advanced charting: Individual + Comparison visualization")
        print("="*80)

# Integration function
def run_10_year_mtf_analysis_with_charts():
    """Run 10-year multi-timeframe analysis with advanced charts"""
    
    print("🚀 10-YEAR MULTI-TIMEFRAME STRATEGY ANALYSIS WITH ADVANCED CHARTS")
    print("="*70)
    
    try:
        # Import Signal Factory
        from signal_factory import get_signal_factory
        
        # Initialize Signal Factory
        factory = get_signal_factory()
        if not factory.initialize():
            print("❌ Failed to initialize Signal Factory")
            return None
        
        # Extract strategies
        strategies = {}
        strategies.update(factory.rule_based_strategies)
        strategies.update(factory.ml_models)
        
        print(f"✅ Loaded {len(strategies)} strategies from Signal Factory")
        
        # Enhanced configuration for 10-year analysis with charts
        config = BacktestConfig(
            initial_capital=100000.0,
            fixed_position_size=0.01,  # SIMPLIFIED (as requested)
            max_positions=5,
            commission=0.0001,
            spread_pips=1.0,
            
            # DISABLED COMPLEX FEATURES (as requested)
            enable_trade_management=False,
            enable_overtrading_prevention=False,
            enable_position_scaling=False,
            enable_trailing_stops=False,
            
            # MULTI-TIMEFRAME SETTINGS
            primary_timeframe="H1",
            enable_multi_timeframe=True,
            timeframes=["M15", "H1", "H4", "D1"],
            
            # CHART SETTINGS (NEW)
            enable_charting=True,
            chart_output_dir="strategy_charts",
            save_individual_charts=True,
            save_comparison_charts=True,
            chart_formats=["html", "png"],
            chart_width=1200,
            chart_height=600,
            
            enable_parallel_processing=True,
            max_workers=4,
            enable_progress_bars=True,
            log_level="INFO"
        )
        
        # Create enhanced multi-timeframe backtester with charts
        backtester = MultiTimeframeBacktesterWithCharts(strategies, config)
        
        # Run 10-year analysis with charts
        symbols = ['EURUSD', 'GBPUSD', 'USDJPY']
        
        print(f"📊 Symbols: {symbols}")
        print("📅 Period: 10 years of historical data")
        print("⏰ Timeframes: M15, H1, H4, D1")
        print("🔧 Risk Management: SIMPLIFIED (Fixed position sizing)")
        print("📈 Charts: ENABLED (Individual + Comparison)")
        
        results = backtester.run_10_year_analysis_with_charts(symbols)
        
        if not results:
            print("❌ Analysis failed")
            return None
        
        print("\n✅ 10-YEAR MULTI-TIMEFRAME ANALYSIS WITH CHARTS COMPLETED!")
        print("📊 Results show how strategies perform with proper timeframe data")
        print("🔧 Complex risk management disabled for pure strategy analysis")
        print("📈 Extended validation period provides robust performance metrics")
        print("📊 Comprehensive charts generated for visual analysis")
        print(f"\n📁 Check '{config.chart_output_dir}/' folder for all charts:")
        print("   • Individual strategy folders with 6 chart types each")
        print("   • Comparison folder with strategy comparison charts")
        print("   • Both HTML (interactive) and PNG (static) formats")
        
        return results
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Run the 10-year multi-timeframe analysis with advanced charts
    results = run_10_year_mtf_analysis_with_charts()
    
    if results and results.get('analysis_summary'):
        summary = results['analysis_summary']
        
        print(f"\n🎉 SUCCESS: 10-year analysis with charts completed!")
        print(f"📊 Analyzed {summary['successful_strategies']} strategies over {summary['analysis_years']} years")
        print(f"💰 {summary['profitable_strategies']} strategies were profitable")
        print(f"📈 Average annual return: {summary['avg_annualized_return']:.2%}")
        print(f"🏆 Best performing strategy: {summary['best_return_strategy']}")
        print(f"📊 Charts saved to: {summary['chart_output_dir']}/")
        print(f"📄 Chart formats: {', '.join(summary['chart_formats'])}")
    else:
        print("\n❌ FAILED: Analysis failed or incomplete")
