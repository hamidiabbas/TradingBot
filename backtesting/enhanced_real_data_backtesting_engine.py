"""
Complete Enhanced Real Data Backtesting Engine
============================================
Professional institutional-grade backtesting engine with ALL advanced features
while maintaining STRICT real data priority - NO synthetic data generation.

Features:
- Complete real MT5 data integration
- Advanced performance metrics (50+ metrics)
- Professional risk management
- Multiple strategy support (RTM, ICT, ML models)
- Portfolio-level analysis
- Walk-forward testing capabilities
- Monte Carlo simulation framework
- Interactive visualization
- Professional reporting
- Multi-timeframe analysis
- Advanced position sizing
- Comprehensive trade analysis
- Real-time performance tracking
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, field
from enum import Enum
import warnings
import os
import json
import pickle
import h5py
from pathlib import Path
import concurrent.futures
from scipy import stats
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.io as pio
from matplotlib.patches import Rectangle
import gc
from collections import defaultdict
import psutil
import time
from abc import ABC, abstractmethod

warnings.filterwarnings('ignore')

# Configure professional logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_backtesting.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DataSource(Enum):
    """Data source types for transparency"""
    REAL_MT5 = "real_mt5_data"
    REAL_CSV = "real_csv_data" 
    REAL_API = "real_api_data"
    NO_DATA = "no_data_available"

class OrderType(Enum):
    """Order types for trade execution"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

class PositionType(Enum):
    """Position types"""
    LONG = "long"
    SHORT = "short"
    FLAT = "flat"

class SignalStrength(Enum):
    """Signal strength levels"""
    VERY_WEAK = 0.2
    WEAK = 0.4
    MODERATE = 0.6
    STRONG = 0.8
    VERY_STRONG = 1.0

@dataclass
class Trade:
    """Complete trade record with all professional details"""
    # Basic trade info
    trade_id: str
    entry_time: datetime
    exit_time: Optional[datetime] = None
    entry_price: float = 0.0
    exit_price: Optional[float] = None
    direction: str = "long"  # 'long' or 'short'
    size: float = 0.0
    profit_loss: Optional[float] = None
    profit_loss_pct: Optional[float] = None
    
    # Strategy and symbol info
    strategy: str = "unknown"
    symbol: str = "UNKNOWN"
    timeframe: str = "UNKNOWN"
    
    # Order and execution details
    order_type: OrderType = OrderType.MARKET
    is_open: bool = True
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    commission: float = 0.0
    slippage: float = 0.0
    
    # Performance tracking
    max_favorable_excursion: float = 0.0  # MFE
    max_adverse_excursion: float = 0.0    # MAE
    trade_duration: Optional[timedelta] = None
    bars_held: int = 0
    
    # Signal and confidence info
    entry_signal_strength: float = 0.0
    exit_signal_strength: float = 0.0
    confidence_level: float = 0.0
    signal_source: str = "unknown"
    
    # Market context
    market_regime: str = "unknown"
    volatility_regime: str = "unknown"
    trend_direction: str = "unknown"
    entry_spread: float = 0.0
    exit_spread: float = 0.0
    
    # Risk metrics
    risk_reward_ratio: Optional[float] = None
    position_size_pct: float = 0.0
    
    # Execution quality
    execution_delay: float = 0.0  # seconds
    price_improvement: float = 0.0
    
    # Additional metadata
    notes: str = ""
    tags: List[str] = field(default_factory=list)

@dataclass 
class PortfolioMetrics:
    """Comprehensive portfolio performance metrics"""
    # Basic Performance
    total_return: float = 0.0
    annualized_return: float = 0.0
    compound_annual_growth_rate: float = 0.0
    absolute_return: float = 0.0
    
    # Risk Metrics
    volatility: float = 0.0
    downside_deviation: float = 0.0
    max_drawdown: float = 0.0
    max_drawdown_duration: int = 0
    calmar_ratio: float = 0.0
    sterling_ratio: float = 0.0
    burke_ratio: float = 0.0
    
    # Risk-Adjusted Returns
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    treynor_ratio: float = 0.0
    information_ratio: float = 0.0
    modigliani_ratio: float = 0.0
    
    # Statistical Measures
    alpha: float = 0.0
    beta: float = 0.0
    correlation: float = 0.0
    r_squared: float = 0.0
    tracking_error: float = 0.0
    
    # Advanced Risk Metrics
    value_at_risk_95: float = 0.0
    value_at_risk_99: float = 0.0
    conditional_var_95: float = 0.0
    conditional_var_99: float = 0.0
    expected_shortfall: float = 0.0
    maximum_loss: float = 0.0
    
    # Trade Statistics
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    loss_rate: float = 0.0
    
    # Profit/Loss Analysis
    gross_profit: float = 0.0
    gross_loss: float = 0.0
    net_profit: float = 0.0
    profit_factor: float = 0.0
    payoff_ratio: float = 0.0
    
    # Trade Performance
    avg_winning_trade: float = 0.0
    avg_losing_trade: float = 0.0
    avg_trade: float = 0.0
    median_trade: float = 0.0
    largest_winning_trade: float = 0.0
    largest_losing_trade: float = 0.0
    
    # Consecutive Statistics
    max_consecutive_wins: int = 0
    max_consecutive_losses: int = 0
    avg_bars_in_trade: float = 0.0
    avg_trade_duration_hours: float = 0.0
    
    # Efficiency Metrics
    expectancy: float = 0.0
    system_quality_number: float = 0.0  # SQN
    profit_to_max_dd_ratio: float = 0.0
    recovery_factor: float = 0.0
    
    # Execution Quality
    total_commission: float = 0.0
    total_slippage: float = 0.0
    avg_commission_per_trade: float = 0.0
    avg_slippage_per_trade: float = 0.0
    
    # Data Quality
    data_source: str = "unknown"
    data_quality_score: float = 0.0
    bars_analyzed: int = 0
    missing_data_pct: float = 0.0

class StrategyInterface(ABC):
    """Abstract interface that ALL strategies must implement"""
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> Union[pd.Series, pd.DataFrame]:
        """Generate trading signals from market data"""
        pass
    
    def get_strategy_name(self) -> str:
        """Return strategy name"""
        return self.__class__.__name__
    
    def get_required_columns(self) -> List[str]:
        """Return list of required data columns"""
        return ['open', 'high', 'low', 'close', 'volume']
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate that data contains required columns"""
        required = self.get_required_columns()
        return all(col in data.columns for col in required)

class UniversalStrategyAdapter:
    """Universal adapter for ANY strategy to work with the backtesting engine"""
    
    def __init__(self, strategy_instance, **kwargs):
        self.strategy = strategy_instance
        self.kwargs = kwargs
        self.strategy_name = self._determine_strategy_name()
        
    def _determine_strategy_name(self) -> str:
        """Determine strategy name from various possible sources"""
        if hasattr(self.strategy, 'get_strategy_name'):
            return self.strategy.get_strategy_name()
        elif hasattr(self.strategy, 'name'):
            return self.strategy.name
        elif hasattr(self.strategy, '__name__'):
            return self.strategy.__name__
        else:
            return self.strategy.__class__.__name__
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate signals using the adapted strategy with comprehensive error handling"""
        try:
            logger.debug(f"Generating signals for {self.strategy_name}")
            
            # Try multiple method names that strategies might use
            methods_to_try = [
                'generate_signals', 'get_signals', 'analyze', 'run', 'calculate',
                'predict', 'forecast', 'evaluate', 'process', 'execute'
            ]
            
            result = None
            method_used = None
            
            for method_name in methods_to_try:
                if hasattr(self.strategy, method_name):
                    method = getattr(self.strategy, method_name)
                    if callable(method):
                        try:
                            result = method(data.copy(), **self.kwargs)
                            method_used = method_name
                            break
                        except Exception as e:
                            logger.debug(f"Method {method_name} failed: {e}")
                            continue
            
            if result is None:
                logger.warning(f"No suitable method found for {self.strategy_name}")
                return pd.Series(0, index=data.index, name='signal')
            
            # Handle different return types with comprehensive processing
            signals = self._process_strategy_output(result, data.index)
            
            # Validate and clean signals
            signals = self._validate_and_clean_signals(signals, data.index)
            
            logger.debug(f"Signals generated using method: {method_used}")
            return signals
            
        except Exception as e:
            logger.error(f"Error in strategy adapter for {self.strategy_name}: {e}")
            return pd.Series(0, index=data.index, name='signal')
    
    def _process_strategy_output(self, result: Any, index: pd.DatetimeIndex) -> pd.Series:
        """Process various types of strategy outputs"""
        
        if isinstance(result, pd.DataFrame):
            # Look for signal columns in order of preference
            signal_columns = [
                'signal', 'signals', 'direction', 'action', 'trade_signal',
                'buy_sell', 'position', 'recommendation', 'decision'
            ]
            
            for col in signal_columns:
                if col in result.columns:
                    return pd.Series(result[col].values, index=index, name='signal')
            
            # Look for numeric columns
            numeric_cols = result.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                return pd.Series(result[numeric_cols[0]].values, index=index, name='signal')
            
            # Default to first column
            if len(result.columns) > 0:
                return pd.Series(result.iloc[:, 0].values, index=index, name='signal')
        
        elif isinstance(result, pd.Series):
            if len(result) == len(index):
                return pd.Series(result.values, index=index, name='signal')
            else:
                # Truncate or pad to match index length
                if len(result) > len(index):
                    return pd.Series(result.iloc[:len(index)].values, index=index, name='signal')
                else:
                    # Pad with zeros
                    padded = np.zeros(len(index))
                    padded[:len(result)] = result.values
                    return pd.Series(padded, index=index, name='signal')
        
        elif isinstance(result, dict):
            # Extract signals from dictionary
            if 'signal' in result:
                return self._process_strategy_output(result['signal'], index)
            elif 'signals' in result:
                return self._process_strategy_output(result['signals'], index)
            elif 'predictions' in result:
                return self._process_strategy_output(result['predictions'], index)
            else:
                # Use first numeric value
                for key, value in result.items():
                    if isinstance(value, (list, np.ndarray, pd.Series)):
                        return self._process_strategy_output(value, index)
        
        elif isinstance(result, (list, np.ndarray)):
            result_array = np.array(result)
            if len(result_array) == len(index):
                return pd.Series(result_array, index=index, name='signal')
            elif len(result_array) > len(index):
                return pd.Series(result_array[:len(index)], index=index, name='signal')
            else:
                # Pad with zeros
                padded = np.zeros(len(index))
                padded[:len(result_array)] = result_array
                return pd.Series(padded, index=index, name='signal')
        
        elif isinstance(result, (int, float)):
            # Single value - broadcast to entire series
            return pd.Series(result, index=index, name='signal')
        
        else:
            logger.warning(f"Unsupported strategy output type: {type(result)}")
            return pd.Series(0, index=index, name='signal')
        
        # Fallback
        return pd.Series(0, index=index, name='signal')
    
    def _validate_and_clean_signals(self, signals: pd.Series, index: pd.DatetimeIndex) -> pd.Series:
        """Validate and clean trading signals"""
        
        # Ensure proper index
        if len(signals) != len(index):
            logger.warning(f"Signal length mismatch. Expected {len(index)}, got {len(signals)}")
            # Resize to match
            if len(signals) > len(index):
                signals = signals.iloc[:len(index)]
            else:
                # Extend with zeros
                extended = pd.Series(0, index=index, name='signal')
                extended.iloc[:len(signals)] = signals.values
                signals = extended
        
        # Set proper index
        signals.index = index
        
        # Clean invalid values
        signals = signals.fillna(0)
        signals = signals.replace([np.inf, -np.inf], 0)
        
        # Ensure signals are numeric
        signals = pd.to_numeric(signals, errors='coerce').fillna(0)
        
        # Normalize extreme values
        signals = np.clip(signals, -10, 10)  # Reasonable range
        
        # Convert to standard signal format (-1, 0, 1) if needed
        if signals.abs().max() > 1.0:
            # Normalize to [-1, 1] range
            max_val = signals.abs().max()
            if max_val > 0:
                signals = signals / max_val
        
        return signals

class ProfessionalDataManager:
    """Professional data manager with STRICT real data priority"""
    
    def __init__(self):
        self.data_cache = {}
        self.data_quality_cache = {}
        
    def load_real_market_data(self, symbol: str, timeframe: str, 
                             data_sources: List[str]) -> Tuple[pd.DataFrame, DataSource, Dict[str, Any]]:
        """
        Load ONLY real market data with comprehensive validation
        
        Returns:
            Tuple of (DataFrame, DataSource, QualityMetrics) 
            Raises exception if NO real data found
        """
        logger.info(f"🔍 Loading REAL market data: {symbol} {timeframe}")
        
        cache_key = f"{symbol}_{timeframe}"
        if cache_key in self.data_cache:
            logger.info(f"📋 Using cached data for {cache_key}")
            return self.data_cache[cache_key]
        
        # Try data sources in priority order
        for source_path in data_sources:
            try:
                if source_path.endswith('.h5'):
                    data, source, quality = self._load_from_h5(source_path, symbol, timeframe)
                elif source_path.endswith('.csv'):
                    data, source, quality = self._load_from_csv(source_path, symbol, timeframe)
                elif source_path.startswith('http'):
                    data, source, quality = self._load_from_api(source_path, symbol, timeframe)
                else:
                    continue
                
                if not data.empty and quality['data_quality_score'] > 0.5:
                    # Cache the result
                    self.data_cache[cache_key] = (data, source, quality)
                    self.data_quality_cache[cache_key] = quality
                    
                    logger.info(f"✅ REAL data loaded: {len(data):,} bars")
                    logger.info(f"📊 Source: {source.value}")
                    logger.info(f"📈 Quality score: {quality['data_quality_score']:.3f}")
                    logger.info(f"📅 Date range: {data.index[0]} to {data.index[-1]}")
                    
                    return data, source, quality
                
            except Exception as e:
                logger.warning(f"Failed to load from {source_path}: {e}")
                continue
        
        # NO REAL DATA FOUND - REFUSE to generate synthetic data
        error_msg = (
            f"❌ NO REAL MARKET DATA FOUND for {symbol} {timeframe}\n"
            f"Searched sources: {data_sources}\n\n"
            f"🛠️ SOLUTIONS:\n"
            f"1. Ensure MT5 data exists: data/training/mt5_historical_data.h5\n"
            f"2. Run MT5 data collection script\n"
            f"3. Provide CSV files with real historical data\n"
            f"4. Use financial data APIs (Alpha Vantage, Yahoo Finance)\n\n"
            f"⚠️ This professional engine will NOT generate fake synthetic data\n"
            f"Real backtesting requires real market data for meaningful results"
        )
        
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    def _load_from_h5(self, h5_path: str, symbol: str, timeframe: str) -> Tuple[pd.DataFrame, DataSource, Dict[str, Any]]:
        """Load real data from MT5 HDF5 file"""
        if not os.path.exists(h5_path):
            raise FileNotFoundError(f"H5 file not found: {h5_path}")
        
        try:
            with h5py.File(h5_path, 'r') as f:
                if 'data' not in f or symbol not in f['data'] or timeframe not in f['data'][symbol]:
                    raise ValueError(f"Data path not found: data/{symbol}/{timeframe}")
                
                group = f['data'][symbol][timeframe]
                
                # Load all available data arrays
                time_data = group['time'][:]
                open_data = group['open'][:]
                high_data = group['high'][:]
                low_data = group['low'][:]
                close_data = group['close'][:]
                
                # Handle volume data
                if 'tick_volume' in group:
                    volume_data = group['tick_volume'][:]
                elif 'volume' in group:
                    volume_data = group['volume'][:]
                else:
                    volume_data = np.ones(len(time_data)) * 1000
                
                # Convert timestamps properly (MT5 uses nanoseconds)
                if np.max(time_data) > 1e10:  # Nanoseconds
                    timestamps = pd.to_datetime(time_data // 1_000_000_000, unit='s', utc=True)
                else:  # Seconds
                    timestamps = pd.to_datetime(time_data, unit='s', utc=True)
                
                # Create DataFrame
                data = pd.DataFrame({
                    'open': open_data,
                    'high': high_data, 
                    'low': low_data,
                    'close': close_data,
                    'volume': volume_data
                }, index=timestamps)
                
                # Add spread if available
                if 'spread' in group:
                    data['spread'] = group['spread'][:]
                
                # Validate and clean
                data, quality_metrics = self._validate_market_data(data, symbol, DataSource.REAL_MT5)
                
                return data, DataSource.REAL_MT5, quality_metrics
                
        except Exception as e:
            logger.error(f"Error loading H5 data: {e}")
            raise
    
    def _load_from_csv(self, csv_path: str, symbol: str, timeframe: str) -> Tuple[pd.DataFrame, DataSource, Dict[str, Any]]:
        """Load real data from CSV file"""
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        try:
            # Try different CSV formats
            separators = [',', ';', '\t', '|']
            
            for sep in separators:
                try:
                    # Try different date column positions
                    for date_col in [0, 'Date', 'Datetime', 'Time', 'date', 'datetime', 'time']:
                        try:
                            if isinstance(date_col, int):
                                data = pd.read_csv(csv_path, sep=sep, index_col=date_col, parse_dates=True)
                            else:
                                data = pd.read_csv(csv_path, sep=sep)
                                if date_col in data.columns:
                                    data[date_col] = pd.to_datetime(data[date_col])
                                    data = data.set_index(date_col)
                                else:
                                    continue
                            
                            # Standardize column names
                            data.columns = [col.lower().strip() for col in data.columns]
                            
                            # Check for required columns
                            required_cols = ['open', 'high', 'low', 'close']
                            
                            # Map alternative column names
                            column_mapping = {
                                'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close',
                                'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close',
                                'OPEN': 'open', 'HIGH': 'high', 'LOW': 'low', 'CLOSE': 'close'
                            }
                            
                            for old_name, new_name in column_mapping.items():
                                if old_name in data.columns and new_name not in data.columns:
                                    data[new_name] = data[old_name]
                            
                            # Check if we have the required columns now
                            if all(col in data.columns for col in required_cols):
                                # Add volume if missing
                                if 'volume' not in data.columns:
                                    if 'vol' in data.columns:
                                        data['volume'] = data['vol']
                                    elif 'Volume' in data.columns:
                                        data['volume'] = data['Volume'] 
                                    else:
                                        data['volume'] = 1000  # Default volume
                                
                                # Validate and clean
                                data, quality_metrics = self._validate_market_data(data, symbol, DataSource.REAL_CSV)
                                
                                if quality_metrics['data_quality_score'] > 0.5:
                                    return data, DataSource.REAL_CSV, quality_metrics
                            
                        except Exception:
                            continue
                            
                except Exception:
                    continue
            
            raise ValueError("Could not parse CSV file with any format")
            
        except Exception as e:
            logger.error(f"Error loading CSV data: {e}")
            raise
    
    def _load_from_api(self, api_url: str, symbol: str, timeframe: str) -> Tuple[pd.DataFrame, DataSource, Dict[str, Any]]:
        """Load real data from financial API"""
        # Placeholder for API integration
        # You can integrate with Yahoo Finance, Alpha Vantage, etc.
        raise NotImplementedError("API data loading not yet implemented")
    
    def _validate_market_data(self, data: pd.DataFrame, symbol: str, source: DataSource) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Comprehensive validation of real market data"""
        
        original_length = len(data)
        quality_metrics = {
            'source': source.value,
            'symbol': symbol,
            'original_bars': original_length,
            'data_quality_score': 0.0,
            'completeness': 0.0,
            'consistency': 0.0,
            'validity': 0.0,
            'issues_found': []
        }
        
        if data.empty:
            quality_metrics['data_quality_score'] = 0.0
            return data, quality_metrics
        
        # Remove duplicates
        data = data[~data.index.duplicated(keep='first')]
        
        # Sort by timestamp
        data = data.sort_index()
        
        # Data completeness check
        missing_values = data.isnull().sum().sum()
        total_values = data.shape[0] * data.shape[1]
        completeness = 1.0 - (missing_values / total_values) if total_values > 0 else 0.0
        
        # Data consistency checks
        consistency_checks = []
        
        # Price relationship checks
        if all(col in data.columns for col in ['high', 'low', 'open', 'close']):
            consistency_checks.extend([
                (data['high'] >= data['low']).mean(),      # High >= Low
                (data['high'] >= data['open']).mean(),     # High >= Open  
                (data['high'] >= data['close']).mean(),    # High >= Close
                (data['low'] <= data['open']).mean(),      # Low <= Open
                (data['low'] <= data['close']).mean(),     # Low <= Close
                (data['open'] > 0).mean(),                 # Positive prices
                (data['close'] > 0).mean(),                # Positive prices
                (data['high'] > 0).mean(),                 # Positive prices
                (data['low'] > 0).mean()                   # Positive prices
            ])
        
        consistency = np.mean(consistency_checks) if consistency_checks else 0.0
        
        # Remove invalid data points
        if 'high' in data.columns and 'low' in data.columns:
            invalid_mask = data['high'] < data['low']
            if invalid_mask.any():
                quality_metrics['issues_found'].append(f"Removed {invalid_mask.sum()} bars with high < low")
                data = data[~invalid_mask]
        
        # Remove zero prices
        price_cols = ['open', 'high', 'low', 'close']
        for col in price_cols:
            if col in data.columns:
                zero_mask = data[col] <= 0
                if zero_mask.any():
                    quality_metrics['issues_found'].append(f"Removed {zero_mask.sum()} bars with zero {col}")
                    data = data[~zero_mask]
        
        # Remove extreme outliers (potential data errors)
        for col in price_cols:
            if col in data.columns:
                Q1 = data[col].quantile(0.25)
                Q3 = data[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 5 * IQR  # Very conservative
                upper_bound = Q3 + 5 * IQR
                
                outlier_mask = (data[col] < lower_bound) | (data[col] > upper_bound)
                if outlier_mask.any():
                    quality_metrics['issues_found'].append(f"Removed {outlier_mask.sum()} extreme outliers in {col}")
                    data = data[~outlier_mask]
        
        # Validity checks
        validity_score = 1.0
        if len(data) == 0:
            validity_score = 0.0
        elif len(data) < 100:
            validity_score = 0.5
            quality_metrics['issues_found'].append("Very limited data available")
        
        # Calculate gaps in data
        if len(data) > 1:
            time_diff = data.index.to_series().diff()
            median_diff = time_diff.median()
            large_gaps = (time_diff > median_diff * 5).sum()
            if large_gaps > len(data) * 0.05:  # More than 5% gaps
                validity_score *= 0.8
                quality_metrics['issues_found'].append(f"Found {large_gaps} large time gaps")
        
        # Final quality metrics
        quality_metrics.update({
            'final_bars': len(data),
            'bars_removed': original_length - len(data),
            'completeness': completeness,
            'consistency': consistency,
            'validity': validity_score,
            'data_quality_score': (completeness + consistency + validity_score) / 3
        })
        
        # Log quality assessment
        if quality_metrics['data_quality_score'] >= 0.9:
            logger.info(f"📊 Data quality: EXCELLENT ({quality_metrics['data_quality_score']:.3f})")
        elif quality_metrics['data_quality_score'] >= 0.8:
            logger.info(f"📊 Data quality: GOOD ({quality_metrics['data_quality_score']:.3f})")
        elif quality_metrics['data_quality_score'] >= 0.6:
            logger.info(f"📊 Data quality: ACCEPTABLE ({quality_metrics['data_quality_score']:.3f})")
        else:
            logger.warning(f"📊 Data quality: POOR ({quality_metrics['data_quality_score']:.3f})")
        
        if quality_metrics['issues_found']:
            logger.info(f"🔧 Issues resolved: {'; '.join(quality_metrics['issues_found'])}")
        
        return data, quality_metrics

class EnhancedRealDataBacktestingEngine:
    """
    Complete Enhanced Real Data Backtesting Engine
    
    The most comprehensive backtesting engine combining:
    - STRICT real data priority (NO synthetic data)
    - Professional-grade performance metrics
    - Advanced risk management
    - Multi-strategy support
    - Portfolio analysis
    - Walk-forward capabilities
    - Monte Carlo framework
    - Interactive visualization
    """
    
    def __init__(self, 
                 initial_capital: float = 100000,
                 commission: float = 0.0001,
                 slippage: float = 0.0001,
                 leverage: float = 100,
                 risk_per_trade: float = 0.02,
                 margin_requirement: float = 0.01,
                 risk_free_rate: float = 0.02,
                 benchmark_symbol: str = "SPY"):
        """
        Initialize enhanced real data backtesting engine
        
        Args:
            initial_capital: Starting capital
            commission: Commission per trade (decimal)
            slippage: Market slippage (decimal)  
            leverage: Trading leverage
            risk_per_trade: Maximum risk per trade (decimal)
            margin_requirement: Margin requirement (decimal)
            risk_free_rate: Risk-free rate for Sharpe calculation
            benchmark_symbol: Benchmark for beta calculation
        """
        # Core parameters
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.leverage = leverage
        self.risk_per_trade = risk_per_trade
        self.margin_requirement = margin_requirement
        self.risk_free_rate = risk_free_rate
        self.benchmark_symbol = benchmark_symbol
        
        # Initialize components
        self.data_manager = ProfessionalDataManager()
        
        # Reset trading state
        self.reset()
        
        logger.info("🏛️ Enhanced Real Data Backtesting Engine initialized")
        logger.info(f"    💰 Initial Capital: ${initial_capital:,.2f}")
        logger.info(f"    📊 Risk per Trade: {risk_per_trade:.1%}")
        logger.info(f"    ⚡ Leverage: {leverage}x")
        logger.info(f"    🔒 REAL DATA ONLY - No synthetic data generation")
    
    def reset(self):
        """Reset engine state for new backtest"""
        # Trading state
        self.capital = self.initial_capital
        self.available_capital = self.initial_capital
        self.equity = self.initial_capital
        self.margin_used = 0.0
        
        # Position tracking
        self.positions = {}  # symbol -> position details
        self.open_orders = {}  # order_id -> order details
        
        # Records
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = []
        self.timestamps: List[datetime] = []
        self.daily_returns: List[float] = []
        self.positions_history: List[Dict] = []
        self.drawdown_series: List[float] = []
        
        # Performance tracking
        self.peak_equity = self.initial_capital
        self.valley_equity = self.initial_capital
        self.drawdown_start = None
        self.max_drawdown = 0.0
        self.max_drawdown_duration = 0
        self.current_drawdown_duration = 0
        
        # Strategy tracking
        self.current_strategy = None
        self.signals_history = []
        
        # Execution tracking
        self.total_commission_paid = 0.0
        self.total_slippage_cost = 0.0
        self.order_id_counter = 0
        
        logger.info("🔄 Engine state reset - ready for backtesting")
    
    def run_comprehensive_backtest(self,
                                 symbol: str,
                                 timeframe: str, 
                                 strategy: Any,
                                 data_sources: List[str] = None,
                                 start_date: Optional[datetime] = None,
                                 end_date: Optional[datetime] = None,
                                 position_sizing_method: str = "fixed_risk",
                                 enable_short_selling: bool = True,
                                 enable_stop_loss: bool = True,
                                 enable_take_profit: bool = True,
                                 max_positions: int = 1) -> Dict[str, Any]:
        """
        Run comprehensive backtest with all professional features
        
        Args:
            symbol: Trading symbol (e.g., EURUSD)
            timeframe: Data timeframe (e.g., H1, H4, D1)
            strategy: Strategy instance or adapter
            data_sources: List of data source paths
            start_date: Backtest start date
            end_date: Backtest end date
            position_sizing_method: Position sizing method
            enable_short_selling: Allow short positions
            enable_stop_loss: Enable stop loss orders
            enable_take_profit: Enable take profit orders
            max_positions: Maximum concurrent positions
            
        Returns:
            Comprehensive backtest results dictionary
        """
        logger.info(f"🚀 Starting comprehensive backtest: {symbol} {timeframe}")
        
        # Default data sources
        if data_sources is None:
            data_sources = [
                "data/training/mt5_historical_data.h5",
                f"data/historical/{symbol}_{timeframe}.csv",
                f"data/csv/{symbol}_{timeframe}.csv",
                f"data/{symbol}_{timeframe}.csv"
            ]
        
        # Load ONLY real market data
        try:
            data, data_source, quality_metrics = self.data_manager.load_real_market_data(
                symbol, timeframe, data_sources
            )
        except ValueError as e:
            logger.error(f"Failed to load real data: {e}")
            raise
        
        # Filter by date range if specified
        if start_date:
            data = data[data.index >= start_date]
        if end_date:
            data = data[data.index <= end_date]
        
        if data.empty:
            raise ValueError("No data available for specified date range")
        
        logger.info(f"📊 Backtest data: {len(data):,} bars from {data.index[0]} to {data.index[-1]}")
        
        # Reset engine state
        self.reset()
        
        # Wrap strategy if needed
        if not isinstance(strategy, UniversalStrategyAdapter):
            strategy = UniversalStrategyAdapter(strategy)
        
        self.current_strategy = strategy.strategy_name
        
        # Generate trading signals
        logger.info("🔮 Generating trading signals from REAL data...")
        try:
            signals = strategy.generate_signals(data.copy())
            data['signal'] = signals
            data['signal'] = data['signal'].fillna(0)
            
            # Log signal distribution
            signal_counts = data['signal'].value_counts().sort_index()
            logger.info(f"📊 Signal distribution: {signal_counts.to_dict()}")
            
        except Exception as e:
            logger.error(f"❌ Error generating signals: {e}")
            raise
        
        # Add technical indicators for strategy analysis
        data = self._add_technical_indicators(data)
        
        # Run the backtest simulation
        logger.info("🔄 Running backtest simulation...")
        self._run_enhanced_simulation(
            data=data, 
            symbol=symbol,
            timeframe=timeframe,
            position_sizing_method=position_sizing_method,
            enable_short_selling=enable_short_selling,
            enable_stop_loss=enable_stop_loss,
            enable_take_profit=enable_take_profit,
            max_positions=max_positions
        )
        
        # Calculate comprehensive performance metrics
        logger.info("📊 Calculating comprehensive performance metrics...")
        portfolio_metrics = self._calculate_comprehensive_metrics(data_source, quality_metrics)
        
        # Create comprehensive results
        results = self._create_comprehensive_results(
            symbol=symbol,
            timeframe=timeframe,
            data=data,
            data_source=data_source,
            quality_metrics=quality_metrics,
            portfolio_metrics=portfolio_metrics,
            backtest_config={
                'position_sizing_method': position_sizing_method,
                'enable_short_selling': enable_short_selling,
                'enable_stop_loss': enable_stop_loss,
                'enable_take_profit': enable_take_profit,
                'max_positions': max_positions,
                'commission': self.commission,
                'slippage': self.slippage,
                'leverage': self.leverage,
                'risk_per_trade': self.risk_per_trade
            }
        )
        
        logger.info(f"✅ Comprehensive backtest completed!")
        logger.info(f"📊 Total Return: {portfolio_metrics.total_return:.2%}")
        logger.info(f"📊 Sharpe Ratio: {portfolio_metrics.sharpe_ratio:.3f}")
        logger.info(f"📊 Max Drawdown: {portfolio_metrics.max_drawdown:.2%}")
        logger.info(f"📊 Total Trades: {portfolio_metrics.total_trades}")
        logger.info(f"📊 Win Rate: {portfolio_metrics.win_rate:.1%}")
        logger.info(f"📈 Data Source: {data_source.value}")
        logger.info(f"✨ Data Quality: {quality_metrics['data_quality_score']:.3f}")
        
        return results
    
    def _add_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators for enhanced analysis"""
        try:
            df = data.copy()
            
            # Price-based indicators
            df['sma_20'] = df['close'].rolling(20).mean()
            df['sma_50'] = df['close'].rolling(50).mean()
            df['ema_12'] = df['close'].ewm(span=12).mean()
            df['ema_26'] = df['close'].ewm(span=26).mean()
            
            # MACD
            df['macd'] = df['ema_12'] - df['ema_26']
            df['macd_signal'] = df['macd'].ewm(span=9).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']
            
            # RSI
            delta = df['close'].diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # Bollinger Bands
            df['bb_middle'] = df['close'].rolling(20).mean()
            bb_std = df['close'].rolling(20).std()
            df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
            df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
            df['bb_width'] = df['bb_upper'] - df['bb_lower']
            df['bb_position'] = (df['close'] - df['bb_lower']) / df['bb_width']
            
            # ATR for volatility
            hl = df['high'] - df['low']
            hc = np.abs(df['high'] - df['close'].shift(1))
            lc = np.abs(df['low'] - df['close'].shift(1))
            tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
            df['atr'] = tr.rolling(14).mean()
            
            # Volume indicators
            df['volume_sma'] = df['volume'].rolling(20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            
            # Price patterns
            df['price_change'] = df['close'].pct_change()
            df['volatility'] = df['price_change'].rolling(20).std()
            
            # Clean up
            df = df.fillna(method='ffill').fillna(0)
            
            return df
            
        except Exception as e:
            logger.warning(f"Error adding technical indicators: {e}")
            return data
    
    def _run_enhanced_simulation(self, data: pd.DataFrame, symbol: str, timeframe: str,
                               position_sizing_method: str, enable_short_selling: bool,
                               enable_stop_loss: bool, enable_take_profit: bool, 
                               max_positions: int):
        """Run enhanced backtesting simulation with all professional features"""
        
        logger.info(f"🎮 Running simulation with {len(data)} bars...")
        
        for i, (timestamp, row) in enumerate(data.iterrows()):
            # Update portfolio equity
            current_equity = self._calculate_portfolio_equity(row['close'], symbol)
            self.equity_curve.append(current_equity)
            self.timestamps.append(timestamp)
            
            # Calculate returns
            if len(self.equity_curve) > 1:
                daily_return = (current_equity - self.equity_curve[-2]) / self.equity_curve[-2]
                self.daily_returns.append(daily_return)
            
            # Update drawdown tracking
            self._update_drawdown_tracking(current_equity)
            
            # Process stop loss and take profit orders first
            self._process_exit_conditions(timestamp, row, symbol)
            
            # Process trading signal
            signal = row.get('signal', 0)
            signal_strength = abs(signal)
            
            if abs(signal) > 0.1:  # Minimum signal threshold
                self._process_trading_signal(
                    timestamp=timestamp,
                    row=row,
                    signal=signal,
                    signal_strength=signal_strength,
                    symbol=symbol,
                    timeframe=timeframe,
                    position_sizing_method=position_sizing_method,
                    enable_short_selling=enable_short_selling,
                    enable_stop_loss=enable_stop_loss,
                    enable_take_profit=enable_take_profit,
                    max_positions=max_positions
                )
            
            # Record position history
            self.positions_history.append({
                'timestamp': timestamp,
                'equity': current_equity,
                'available_capital': self.available_capital,
                'margin_used': self.margin_used,
                'positions': len(self.positions),
                'unrealized_pnl': self._calculate_unrealized_pnl(row['close'], symbol)
            })
            
            # Record signal history
            self.signals_history.append({
                'timestamp': timestamp,
                'signal': signal,
                'signal_strength': signal_strength,
                'price': row['close'],
                'volume': row.get('volume', 0),
                'volatility': row.get('atr', 0),
                'rsi': row.get('rsi', 50)
            })
        
        # Close all remaining positions at the end
        final_row = data.iloc[-1]
        self._close_all_positions(final_row['close'], data.index[-1], symbol, "backtest_end")
        
        logger.info(f"✅ Simulation completed with {len(self.trades)} total trades")
    
    def _process_trading_signal(self, timestamp: datetime, row: pd.Series, signal: float,
                              signal_strength: float, symbol: str, timeframe: str,
                              position_sizing_method: str, enable_short_selling: bool,
                              enable_stop_loss: bool, enable_take_profit: bool,
                              max_positions: int):
        """Process trading signal with advanced logic"""
        
        current_position = self.positions.get(symbol, {'size': 0, 'direction': 'flat'})
        
        # Signal interpretation
        if signal > 0.5:  # Strong buy signal
            if current_position['size'] <= 0:  # Not long or flat
                if current_position['size'] < 0:  # Close short position
                    self._close_position(symbol, row['close'], timestamp, "signal_reversal")
                
                # Open long position
                if len(self.positions) < max_positions:
                    self._open_position(
                        symbol=symbol,
                        direction='long', 
                        price=row['close'],
                        timestamp=timestamp,
                        timeframe=timeframe,
                        signal_strength=signal_strength,
                        position_sizing_method=position_sizing_method,
                        market_data=row,
                        enable_stop_loss=enable_stop_loss,
                        enable_take_profit=enable_take_profit
                    )
        
        elif signal < -0.5 and enable_short_selling:  # Strong sell signal
            if current_position['size'] >= 0:  # Not short or flat
                if current_position['size'] > 0:  # Close long position
                    self._close_position(symbol, row['close'], timestamp, "signal_reversal")
                
                # Open short position
                if len(self.positions) < max_positions:
                    self._open_position(
                        symbol=symbol,
                        direction='short',
                        price=row['close'],
                        timestamp=timestamp,
                        timeframe=timeframe,
                        signal_strength=signal_strength,
                        position_sizing_method=position_sizing_method,
                        market_data=row,
                        enable_stop_loss=enable_stop_loss,
                        enable_take_profit=enable_take_profit
                    )
        
        elif abs(signal) < 0.1:  # Exit signal (close to zero)
            if symbol in self.positions and self.positions[symbol]['size'] != 0:
                self._close_position(symbol, row['close'], timestamp, "exit_signal")
    
    def _open_position(self, symbol: str, direction: str, price: float, timestamp: datetime,
                      timeframe: str, signal_strength: float, position_sizing_method: str,
                      market_data: pd.Series, enable_stop_loss: bool, enable_take_profit: bool):
        """Open new position with advanced risk management"""
        
        try:
            # Calculate position size
            position_size = self._calculate_position_size(
                symbol=symbol,
                price=price,
                direction=direction,
                method=position_sizing_method,
                market_data=market_data,
                signal_strength=signal_strength
            )
            
            if position_size <= 0:
                return
            
            # Apply slippage
            execution_price = self._apply_execution_slippage(price, direction)
            
            # Calculate costs
            commission_cost = self._calculate_commission(position_size, execution_price)
            margin_required = position_size * execution_price * self.margin_requirement
            
            # Check margin requirements
            if margin_required > self.available_capital:
                logger.debug(f"Insufficient margin for {symbol}: required ${margin_required:.2f}, available ${self.available_capital:.2f}")
                return
            
            # Calculate stop loss and take profit levels
            stop_loss = None
            take_profit = None
            
            if enable_stop_loss:
                stop_loss = self._calculate_stop_loss(execution_price, direction, market_data)
            
            if enable_take_profit:
                take_profit = self._calculate_take_profit(execution_price, direction, market_data)
            
            # Update capital and margin
            self.available_capital -= (commission_cost + margin_required)
            self.total_commission_paid += commission_cost
            self.margin_used += margin_required
            
            # Create position record
            position_info = {
                'size': position_size if direction == 'long' else -position_size,
                'direction': direction,
                'entry_price': execution_price,
                'entry_time': timestamp,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'margin_used': margin_required
            }
            
            self.positions[symbol] = position_info
            
            # Create trade record
            trade_id = f"{symbol}_{timestamp.strftime('%Y%m%d_%H%M%S')}_{self.order_id_counter}"
            self.order_id_counter += 1
            
            trade = Trade(
                trade_id=trade_id,
                entry_time=timestamp,
                entry_price=execution_price,
                direction=direction,
                size=position_size,
                strategy=self.current_strategy,
                symbol=symbol,
                timeframe=timeframe,
                stop_loss=stop_loss,
                take_profit=take_profit,
                commission=commission_cost,
                slippage=abs(execution_price - price),
                entry_signal_strength=signal_strength,
                confidence_level=signal_strength,
                signal_source=self.current_strategy,
                market_regime=self._determine_market_regime(market_data),
                volatility_regime=self._determine_volatility_regime(market_data),
                trend_direction=self._determine_trend_direction(market_data),
                entry_spread=market_data.get('spread', 0),
                position_size_pct=(position_size * execution_price) / self.equity,
                notes=f"Opened via {position_sizing_method} sizing"
            )
            
            self.trades.append(trade)
            
            logger.debug(f"📈 Opened {direction} position: {symbol} {position_size:.4f} @ {execution_price:.5f}")
            
        except Exception as e:
            logger.error(f"Error opening position for {symbol}: {e}")
    
    def _close_position(self, symbol: str, price: float, timestamp: datetime, reason: str):
        """Close position with comprehensive tracking"""
        
        if symbol not in self.positions or self.positions[symbol]['size'] == 0:
            return
        
        try:
            position = self.positions[symbol]
            direction = "sell" if position['size'] > 0 else "buy"
            
            # Apply slippage
            execution_price = self._apply_execution_slippage(price, direction)
            
            # Calculate P&L
            if position['size'] > 0:  # Long position
                pnl = (execution_price - position['entry_price']) * abs(position['size'])
            else:  # Short position  
                pnl = (position['entry_price'] - execution_price) * abs(position['size'])
            
            # Calculate costs
            commission_cost = self._calculate_commission(abs(position['size']), execution_price)
            net_pnl = pnl - commission_cost
            
            # Update capital and margin
            self.capital += net_pnl
            self.available_capital += position['margin_used']  # Release margin
            self.total_commission_paid += commission_cost
            self.total_slippage_cost += abs(execution_price - price) * abs(position['size'])
            self.margin_used -= position['margin_used']
            
            # Find and update the corresponding trade
            for trade in reversed(self.trades):
                if trade.symbol == symbol and trade.is_open:
                    # Update trade record
                    trade.exit_time = timestamp
                    trade.exit_price = execution_price
                    trade.profit_loss = net_pnl
                    trade.profit_loss_pct = net_pnl / (position['entry_price'] * abs(position['size'])) * 100
                    trade.is_open = False
                    trade.commission += commission_cost
                    trade.slippage += abs(execution_price - price)
                    trade.trade_duration = timestamp - trade.entry_time
                    trade.bars_held = max(1, (timestamp - position['entry_time']).total_seconds() / 3600)  # Rough estimate
                    trade.exit_signal_strength = 1.0  # Could be enhanced with actual signal strength
                    trade.notes += f" | Closed: {reason}"
                    
                    # Calculate risk-reward ratio
                    if position['stop_loss'] and position['take_profit']:
                        if position['direction'] == 'long':
                            risk = position['entry_price'] - position['stop_loss']
                            reward = position['take_profit'] - position['entry_price']
                        else:
                            risk = position['stop_loss'] - position['entry_price']
                            reward = position['entry_price'] - position['take_profit']
                        
                        if risk > 0:
                            trade.risk_reward_ratio = reward / risk
                    
                    break
            
            # Remove position
            del self.positions[symbol]
            
            logger.debug(f"📉 Closed {position['direction']} position: {symbol} P&L ${net_pnl:.2f} ({reason})")
            
        except Exception as e:
            logger.error(f"Error closing position for {symbol}: {e}")
    
    def _close_all_positions(self, price: float, timestamp: datetime, symbol: str, reason: str):
        """Close all open positions"""
        positions_to_close = list(self.positions.keys())
        for pos_symbol in positions_to_close:
            self._close_position(pos_symbol, price, timestamp, reason)
    
    def _process_exit_conditions(self, timestamp: datetime, row: pd.Series, symbol: str):
        """Process stop loss and take profit conditions"""
        
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        current_price = row['close']
        high_price = row['high']
        low_price = row['low']
        
        # Check stop loss
        if position['stop_loss']:
            if position['direction'] == 'long' and low_price <= position['stop_loss']:
                self._close_position(symbol, position['stop_loss'], timestamp, "stop_loss")
                return
            elif position['direction'] == 'short' and high_price >= position['stop_loss']:
                self._close_position(symbol, position['stop_loss'], timestamp, "stop_loss")
                return
        
        # Check take profit
        if position['take_profit']:
            if position['direction'] == 'long' and high_price >= position['take_profit']:
                self._close_position(symbol, position['take_profit'], timestamp, "take_profit")
                return
            elif position['direction'] == 'short' and low_price <= position['take_profit']:
                self._close_position(symbol, position['take_profit'], timestamp, "take_profit")
                return
    
    def _calculate_position_size(self, symbol: str, price: float, direction: str, method: str,
                               market_data: pd.Series, signal_strength: float) -> float:
        """Calculate position size using various methods"""
        
        try:
            if method == "fixed_risk":
                # Risk-based position sizing
                risk_amount = self.equity * self.risk_per_trade
                atr = market_data.get('atr', price * 0.02)  # Default to 2% of price
                stop_distance = atr * 2  # 2 ATR stop
                
                if stop_distance > 0:
                    position_size = risk_amount / stop_distance
                else:
                    position_size = risk_amount / (price * 0.02)
                
                # Adjust for signal strength
                position_size *= signal_strength
                
            elif method == "fixed_amount":
                # Fixed dollar amount
                fixed_amount = min(10000, self.equity * 0.1)  # 10% of equity or $10k
                position_size = (fixed_amount / price) * signal_strength
                
            elif method == "volatility_target":
                # Volatility-based sizing
                target_vol = 0.02  # 2% daily volatility target
                current_vol = market_data.get('volatility', 0.01)
                
                if current_vol > 0:
                    vol_multiplier = target_vol / current_vol
                    position_size = (self.equity * 0.1 / price) * vol_multiplier * signal_strength
                else:
                    position_size = (self.equity * 0.1 / price) * signal_strength
                
            elif method == "kelly_criterion":
                # Simplified Kelly criterion
                win_rate = 0.6  # Estimated based on historical performance
                avg_win = 0.02
                avg_loss = 0.01
                
                kelly_f = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
                kelly_f = max(0, min(0.25, kelly_f))  # Cap at 25%
                
                position_size = (kelly_f * self.equity / price) * signal_strength
                
            else:
                # Default to fixed risk
                position_size = self._calculate_position_size(
                    symbol, price, direction, "fixed_risk", market_data, signal_strength
                )
            
            # Apply leverage and constraints
            max_position_value = self.equity * self.leverage * 0.8  # 80% of max leverage
            max_position_size = max_position_value / price
            
            position_size = min(position_size, max_position_size)
            position_size = max(0, position_size)  # Ensure positive
            
            return position_size
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0.0
    
    def _apply_execution_slippage(self, price: float, direction: str) -> float:
        """Apply realistic execution slippage"""
        slippage_factor = self.slippage
        
        # Increase slippage for large positions or volatile markets
        # This could be enhanced with market impact models
        
        if direction in ["buy", "long"]:
            return price * (1 + slippage_factor)
        else:
            return price * (1 - slippage_factor)
    
    def _calculate_commission(self, size: float, price: float) -> float:
        """Calculate trading commission"""
        return size * price * self.commission
    
    def _calculate_stop_loss(self, entry_price: float, direction: str, market_data: pd.Series) -> float:
        """Calculate stop loss level"""
        atr = market_data.get('atr', entry_price * 0.01)
        stop_multiplier = 2.0  # 2 ATR stop
        
        if direction == 'long':
            return entry_price - (atr * stop_multiplier)
        else:
            return entry_price + (atr * stop_multiplier)
    
    def _calculate_take_profit(self, entry_price: float, direction: str, market_data: pd.Series) -> float:
        """Calculate take profit level"""
        atr = market_data.get('atr', entry_price * 0.01)
        profit_multiplier = 3.0  # 3 ATR target (1:1.5 risk:reward)
        
        if direction == 'long':
            return entry_price + (atr * profit_multiplier)
        else:
            return entry_price - (atr * profit_multiplier)
    
    def _calculate_portfolio_equity(self, current_price: float, symbol: str) -> float:
        """Calculate current portfolio equity including unrealized P&L"""
        unrealized_pnl = self._calculate_unrealized_pnl(current_price, symbol)
        return self.capital + unrealized_pnl
    
    def _calculate_unrealized_pnl(self, current_price: float, symbol: str) -> float:
        """Calculate unrealized P&L for all positions"""
        unrealized_pnl = 0.0
        
        for pos_symbol, position in self.positions.items():
            if position['size'] != 0:
                if position['size'] > 0:  # Long position
                    pnl = (current_price - position['entry_price']) * abs(position['size'])
                else:  # Short position
                    pnl = (position['entry_price'] - current_price) * abs(position['size'])
                
                unrealized_pnl += pnl
        
        return unrealized_pnl
    
    def _update_drawdown_tracking(self, current_equity: float):
        """Update drawdown tracking metrics"""
        if current_equity > self.peak_equity:
            self.peak_equity = current_equity
            
            # End of drawdown period
            if self.drawdown_start is not None:
                self.max_drawdown_duration = max(
                    self.max_drawdown_duration, 
                    self.current_drawdown_duration
                )
                self.drawdown_start = None
                self.current_drawdown_duration = 0
        
        else:
            # In drawdown
            if self.drawdown_start is None:
                self.drawdown_start = len(self.equity_curve)
            
            self.current_drawdown_duration += 1
            
            # Update max drawdown
            current_dd = (self.peak_equity - current_equity) / self.peak_equity
            self.max_drawdown = max(self.max_drawdown, current_dd)
        
        # Record drawdown series
        current_dd = (self.peak_equity - current_equity) / self.peak_equity if self.peak_equity > 0 else 0
        self.drawdown_series.append(current_dd)
    
    def _determine_market_regime(self, market_data: pd.Series) -> str:
        """Determine current market regime"""
        try:
            sma_20 = market_data.get('sma_20', 0)
            sma_50 = market_data.get('sma_50', 0)
            current_price = market_data.get('close', 0)
            
            if sma_20 > sma_50 and current_price > sma_20:
                return "bullish_trending"
            elif sma_20 < sma_50 and current_price < sma_20:
                return "bearish_trending"
            else:
                return "ranging"
        except:
            return "unknown"
    
    def _determine_volatility_regime(self, market_data: pd.Series) -> str:
        """Determine current volatility regime"""
        try:
            volatility = market_data.get('volatility', 0)
            atr = market_data.get('atr', 0)
            
            if volatility > 0.02 or atr > market_data.get('close', 1) * 0.02:
                return "high_volatility"
            elif volatility < 0.005 or atr < market_data.get('close', 1) * 0.005:
                return "low_volatility"
            else:
                return "normal_volatility"
        except:
            return "unknown"
    
    def _determine_trend_direction(self, market_data: pd.Series) -> str:
        """Determine current trend direction"""
        try:
            sma_20 = market_data.get('sma_20', 0)
            sma_50 = market_data.get('sma_50', 0)
            
            if sma_20 > sma_50:
                return "uptrend"
            elif sma_20 < sma_50:
                return "downtrend"
            else:
                return "sideways"
        except:
            return "unknown"
    
    def _calculate_comprehensive_metrics(self, data_source: DataSource, quality_metrics: Dict[str, Any]) -> PortfolioMetrics:
        """Calculate comprehensive portfolio performance metrics"""
        
        try:
            logger.info("📊 Calculating comprehensive performance metrics...")
            
            # Initialize metrics
            metrics = PortfolioMetrics()
            
            # Basic data info
            metrics.data_source = data_source.value
            metrics.data_quality_score = quality_metrics.get('data_quality_score', 0.0)
            metrics.bars_analyzed = quality_metrics.get('final_bars', 0)
            
            if not self.equity_curve or len(self.equity_curve) < 2:
                logger.warning("Insufficient data for metrics calculation")
                return metrics
            
            final_equity = self.equity_curve[-1]
            
            # Basic performance metrics
            metrics.total_return = (final_equity - self.initial_capital) / self.initial_capital
            metrics.absolute_return = final_equity - self.initial_capital
            
            # Annualized return
            days = len(self.equity_curve)
            years = days / 252  # Trading days per year
            if years > 0:
                metrics.annualized_return = (1 + metrics.total_return) ** (1/years) - 1
                metrics.compound_annual_growth_rate = metrics.annualized_return
            
            # Risk metrics
            if self.daily_returns:
                returns_array = np.array(self.daily_returns)
                
                # Volatility
                metrics.volatility = np.std(returns_array) * np.sqrt(252)
                
                # Downside deviation
                negative_returns = returns_array[returns_returns < 0]
                metrics.downside_deviation = np.std(negative_returns) * np.sqrt(252) if len(negative_returns) > 0 else 0
                
                # Risk-adjusted returns
                if metrics.volatility > 0:
                    excess_returns = returns_array - (self.risk_free_rate / 252)
                    metrics.sharpe_ratio = np.mean(excess_returns) / np.std(returns_array) * np.sqrt(252)
                
                if metrics.downside_deviation > 0:
                    excess_returns = returns_array - (self.risk_free_rate / 252)
                    metrics.sortino_ratio = np.mean(excess_returns) / metrics.downside_deviation * np.sqrt(252)
                
                # VaR calculations
                metrics.value_at_risk_95 = np.percentile(returns_array, 5)
                metrics.value_at_risk_99 = np.percentile(returns_array, 1)
                metrics.conditional_var_95 = np.mean(returns_array[returns_array <= metrics.value_at_risk_95])
                metrics.conditional_var_99 = np.mean(returns_array[returns_array <= metrics.value_at_risk_99])
                metrics.expected_shortfall = metrics.conditional_var_95
                metrics.maximum_loss = np.min(returns_array)
            
            # Drawdown metrics
            metrics.max_drawdown = self.max_drawdown
            metrics.max_drawdown_duration = self.max_drawdown_duration
            
            # Risk ratios
            if metrics.max_drawdown > 0:
                metrics.calmar_ratio = metrics.annualized_return / metrics.max_drawdown
                metrics.sterling_ratio = metrics.annualized_return / np.mean([abs(dd) for dd in self.drawdown_series if dd > 0.05])
            
            # Trade statistics
            closed_trades = [t for t in self.trades if not t.is_open and t.profit_loss is not None]
            metrics.total_trades = len(closed_trades)
            
            if closed_trades:
                profits = [t.profit_loss for t in closed_trades]
                winning_trades = [t for t in closed_trades if t.profit_loss > 0]
                losing_trades = [t for t in closed_trades if t.profit_loss <= 0]
                
                # Basic trade stats
                metrics.winning_trades = len(winning_trades)
                metrics.losing_trades = len(losing_trades)
                metrics.win_rate = len(winning_trades) / len(closed_trades)
                metrics.loss_rate = 1 - metrics.win_rate
                
                # P&L analysis
                metrics.gross_profit = sum(t.profit_loss for t in winning_trades)
                metrics.gross_loss = sum(t.profit_loss for t in losing_trades)  # Already negative
                metrics.net_profit = sum(profits)
                
                if abs(metrics.gross_loss) > 0:
                    metrics.profit_factor = metrics.gross_profit / abs(metrics.gross_loss)
                
                # Trade performance
                metrics.avg_winning_trade = metrics.gross_profit / len(winning_trades) if winning_trades else 0
                metrics.avg_losing_trade = metrics.gross_loss / len(losing_trades) if losing_trades else 0
                metrics.avg_trade = np.mean(profits)
                metrics.median_trade = np.median(profits)
                metrics.largest_winning_trade = max(profits) if profits else 0
                metrics.largest_losing_trade = min(profits) if profits else 0
                
                if metrics.avg_losing_trade != 0:
                    metrics.payoff_ratio = abs(metrics.avg_winning_trade / metrics.avg_losing_trade)
                
                # Consecutive statistics
                metrics.max_consecutive_wins = self._calculate_max_consecutive_wins(closed_trades)
                metrics.max_consecutive_losses = self._calculate_max_consecutive_losses(closed_trades)
                
                # Duration analysis
                durations = []
                bars_held = []
                for trade in closed_trades:
                    if trade.trade_duration:
                        durations.append(trade.trade_duration.total_seconds() / 3600)  # Hours
                    if trade.bars_held > 0:
                        bars_held.append(trade.bars_held)
                
                metrics.avg_trade_duration_hours = np.mean(durations) if durations else 0
                metrics.avg_bars_in_trade = np.mean(bars_held) if bars_held else 0
                
                # Advanced metrics
                if len(profits) > 1:
                    profit_std = np.std(profits)
                    if profit_std > 0:
                        metrics.expectancy = metrics.avg_trade
                        metrics.system_quality_number = np.sqrt(len(closed_trades)) * metrics.avg_trade / profit_std
                
                if metrics.max_drawdown > 0:
                    metrics.profit_to_max_dd_ratio = metrics.net_profit / (metrics.max_drawdown * self.initial_capital)
                    
                    valley_equity = self.initial_capital * (1 - metrics.max_drawdown)
                    if valley_equity > 0:
                        metrics.recovery_factor = (final_equity - valley_equity) / valley_equity
            
            # Execution quality
            metrics.total_commission = self.total_commission_paid
            metrics.total_slippage = self.total_slippage_cost
            metrics.avg_commission_per_trade = metrics.total_commission / max(1, metrics.total_trades)
            metrics.avg_slippage_per_trade = metrics.total_slippage / max(1, metrics.total_trades)
            
            logger.info("✅ Comprehensive metrics calculated successfully")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating comprehensive metrics: {e}")
            return PortfolioMetrics()
    
    def _calculate_max_consecutive_wins(self, trades: List[Trade]) -> int:
        """Calculate maximum consecutive winning trades"""
        max_consecutive = 0
        current_consecutive = 0
        
        for trade in trades:
            if trade.profit_loss and trade.profit_loss > 0:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        return max_consecutive
    
    def _calculate_max_consecutive_losses(self, trades: List[Trade]) -> int:
        """Calculate maximum consecutive losing trades"""
        max_consecutive = 0
        current_consecutive = 0
        
        for trade in trades:
            if trade.profit_loss and trade.profit_loss <= 0:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        return max_consecutive
    
    def _create_comprehensive_results(self, symbol: str, timeframe: str, data: pd.DataFrame,
                                    data_source: DataSource, quality_metrics: Dict[str, Any],
                                    portfolio_metrics: PortfolioMetrics, 
                                    backtest_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive backtest results dictionary"""
        
        return {
            # Basic info
            'symbol': symbol,
            'timeframe': timeframe,
            'strategy': self.current_strategy,
            'start_date': data.index[0],
            'end_date': data.index[-1],
            'total_bars': len(data),
            
            # Capital info
            'initial_capital': self.initial_capital,
            'final_capital': self.equity_curve[-1] if self.equity_curve else self.initial_capital,
            'peak_capital': max(self.equity_curve) if self.equity_curve else self.initial_capital,
            
            # Data quality
            'data_source': data_source.value,
            'data_quality_metrics': quality_metrics,
            
            # Performance metrics
            'performance_metrics': portfolio_metrics,
            
            # Trading records
            'trades': self.trades,
            'total_trades': len([t for t in self.trades if not t.is_open]),
            'open_trades': len([t for t in self.trades if t.is_open]),
            
            # Time series data
            'equity_curve': pd.Series(self.equity_curve, index=self.timestamps[:len(self.equity_curve)]),
            'drawdown_series': pd.Series(self.drawdown_series, index=self.timestamps[:len(self.drawdown_series)]),
            'daily_returns': self.daily_returns,
            'positions_history': self.positions_history,
            'signals_history': self.signals_history,
            
            # Configuration
            'backtest_config': backtest_config,
            
            # Summary statistics
            'summary_stats': {
                'total_return': portfolio_metrics.total_return,
                'annualized_return': portfolio_metrics.annualized_return,
                'sharpe_ratio': portfolio_metrics.sharpe_ratio,
                'sortino_ratio': portfolio_metrics.sortino_ratio,
                'max_drawdown': portfolio_metrics.max_drawdown,
                'volatility': portfolio_metrics.volatility,
                'win_rate': portfolio_metrics.win_rate,
                'profit_factor': portfolio_metrics.profit_factor,
                'expectancy': portfolio_metrics.expectancy,
                'total_commission': portfolio_metrics.total_commission,
                'data_quality_score': portfolio_metrics.data_quality_score
            },
            
            # Risk analysis
            'risk_analysis': {
                'value_at_risk_95': portfolio_metrics.value_at_risk_95,
                'conditional_var_95': portfolio_metrics.conditional_var_95,
                'maximum_loss': portfolio_metrics.maximum_loss,
                'downside_deviation': portfolio_metrics.downside_deviation,
                'calmar_ratio': portfolio_metrics.calmar_ratio,
                'sterling_ratio': portfolio_metrics.sterling_ratio
            },
            
            # Execution analysis
            'execution_analysis': {
                'total_commission_paid': self.total_commission_paid,
                'total_slippage_cost': self.total_slippage_cost,
                'avg_commission_per_trade': portfolio_metrics.avg_commission_per_trade,
                'avg_slippage_per_trade': portfolio_metrics.avg_slippage_per_trade,
                'execution_efficiency': 1.0 - (self.total_commission_paid + self.total_slippage_cost) / abs(portfolio_metrics.net_profit) if portfolio_metrics.net_profit != 0 else 0
            }
        }
    
    def generate_professional_report(self, results: Dict[str, Any], save_path: Optional[str] = None) -> str:
        """Generate comprehensive professional backtest report"""
        
        report_lines = []
        
        # Header
        report_lines.extend([
            "=" * 100,
            "🏛️ ENHANCED REAL DATA BACKTESTING REPORT",
            "=" * 100,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Engine: Enhanced Real Data Backtesting Engine v2.0",
            "",
            "📊 BACKTEST OVERVIEW",
            "-" * 50,
            f"Strategy:           {results['strategy']}",
            f"Symbol:             {results['symbol']} ({results['timeframe']})",
            f"Period:             {results['start_date'].strftime('%Y-%m-%d')} to {results['end_date'].strftime('%Y-%m-%d')}",
            f"Total Bars:         {results['total_bars']:,}",
            f"Data Source:        {results['data_source']}",
            f"Data Quality:       {results['data_quality_metrics']['data_quality_score']:.3f}",
            ""
        ])
        
        # Performance summary
        perf = results['performance_metrics']
        summary = results['summary_stats']
        
        report_lines.extend([
            "💰 PERFORMANCE SUMMARY",
            "-" * 50,
            f"Initial Capital:    ${results['initial_capital']:,.2f}",
            f"Final Capital:      ${results['final_capital']:,.2f}",
            f"Peak Capital:       ${results['peak_capital']:,.2f}",
            f"Net Profit:         ${perf.net_profit:,.2f}",
            f"Total Return:       {perf.total_return:.2%}",
            f"Annualized Return:  {perf.annualized_return:.2%}",
            f"CAGR:              {perf.compound_annual_growth_rate:.2%}",
            ""
        ])
        
        # Risk metrics
        report_lines.extend([
            "⚠️ RISK METRICS",
            "-" * 50,
            f"Maximum Drawdown:   {perf.max_drawdown:.2%}",
            f"Max DD Duration:    {perf.max_drawdown_duration} periods",
            f"Volatility:         {perf.volatility:.2%}",
            f"Downside Deviation: {perf.downside_deviation:.2%}",
            f"VaR (95%):         {perf.value_at_risk_95:.2%}",
            f"CVaR (95%):        {perf.conditional_var_95:.2%}",
            f"Maximum Loss:       {perf.maximum_loss:.2%}",
            ""
        ])
        
        # Risk-adjusted returns
        report_lines.extend([
            "📈 RISK-ADJUSTED RETURNS",
            "-" * 50,
            f"Sharpe Ratio:       {perf.sharpe_ratio:.3f}",
            f"Sortino Ratio:      {perf.sortino_ratio:.3f}",
            f"Calmar Ratio:       {perf.calmar_ratio:.3f}",
            f"Sterling Ratio:     {perf.sterling_ratio:.3f}",
            f"Information Ratio:  {perf.information_ratio:.3f}",
            ""
        ])
        
        # Trade statistics
        report_lines.extend([
            "🎯 TRADING STATISTICS",
            "-" * 50,
            f"Total Trades:       {perf.total_trades}",
            f"Winning Trades:     {perf.winning_trades} ({perf.win_rate:.1%})",
            f"Losing Trades:      {perf.losing_trades} ({perf.loss_rate:.1%})",
            f"Gross Profit:       ${perf.gross_profit:,.2f}",
            f"Gross Loss:         ${perf.gross_loss:,.2f}",
            f"Profit Factor:      {perf.profit_factor:.2f}",
            f"Payoff Ratio:       {perf.payoff_ratio:.2f}",
            f"Expectancy:         ${perf.expectancy:.2f}",
            ""
        ])
        
        # Trade analysis
        report_lines.extend([
            "💼 TRADE ANALYSIS",
            "-" * 50,
            f"Average Trade:      ${perf.avg_trade:.2f}",
            f"Median Trade:       ${perf.median_trade:.2f}",
            f"Best Trade:         ${perf.largest_winning_trade:.2f}",
            f"Worst Trade:        ${perf.largest_losing_trade:.2f}",
            f"Avg Winning Trade:  ${perf.avg_winning_trade:.2f}",
            f"Avg Losing Trade:   ${perf.avg_losing_trade:.2f}",
            f"Avg Trade Duration: {perf.avg_trade_duration_hours:.1f} hours",
            f"Avg Bars Held:      {perf.avg_bars_in_trade:.1f}",
            ""
        ])
        
        # Consistency metrics
        report_lines.extend([
            "📊 CONSISTENCY METRICS",
            "-" * 50,
            f"Max Consecutive Wins:   {perf.max_consecutive_wins}",
            f"Max Consecutive Losses: {perf.max_consecutive_losses}",
            f"System Quality Number:  {perf.system_quality_number:.2f}",
            f"Recovery Factor:        {perf.recovery_factor:.2f}",
            f"Profit/MaxDD Ratio:     {perf.profit_to_max_dd_ratio:.2f}",
            ""
        ])
        
        # Execution quality
        exec_analysis = results['execution_analysis']
        report_lines.extend([
            "⚡ EXECUTION QUALITY",
            "-" * 50,
            f"Total Commission:       ${perf.total_commission:.2f}",
            f"Total Slippage:         ${perf.total_slippage:.2f}",
            f"Avg Commission/Trade:   ${perf.avg_commission_per_trade:.2f}",
            f"Avg Slippage/Trade:     ${perf.avg_slippage_per_trade:.2f}",
            f"Execution Efficiency:   {exec_analysis['execution_efficiency']:.1%}",
            ""
        ])
        
        # Continue from line 1939 - Complete the report generation
        
        # Data quality assessment
        data_quality = results['data_quality_metrics']
        report_lines.extend([
            "✅ DATA QUALITY ASSESSMENT",
            "-" * 50,
            f"Data Source:        {results['data_source']}",
            f"Quality Score:      {data_quality['data_quality_score']:.3f}",
            f"Completeness:       {data_quality['completeness']:.1%}",
            f"Consistency:        {data_quality['consistency']:.1%}",
            f"Validity:           {data_quality['validity']:.1%}",
            f"Original Bars:      {data_quality['original_bars']:,}",
            f"Final Bars:         {data_quality['final_bars']:,}",
            f"Bars Removed:       {data_quality['bars_removed']:,}",
            ""
        ])
        
        # Configuration details
        config = results['backtest_config']
        report_lines.extend([
            "⚙️ BACKTEST CONFIGURATION",
            "-" * 50,
            f"Commission:         {config['commission']:.6f}",
            f"Slippage:           {config['slippage']:.6f}",
            f"Leverage:           {config['leverage']}x",
            f"Risk per Trade:     {config['risk_per_trade']:.1%}",
            f"Position Sizing:    {config['position_sizing_method']}",
            f"Short Selling:      {config['enable_short_selling']}",
            f"Stop Loss:          {config['enable_stop_loss']}",
            f"Take Profit:        {config['enable_take_profit']}",
            ""
        ])
        
        # Trade details table
        if closed_trades:
            report_lines.extend([
                "📋 RECENT TRADES SAMPLE",
                "-" * 50
            ])
            
            # Show last 10 trades
            recent_trades = closed_trades[-10:] if len(closed_trades) > 10 else closed_trades
            
            for i, trade in enumerate(recent_trades, 1):
                entry_date = trade.entry_time.strftime('%Y-%m-%d %H:%M')
                exit_date = trade.exit_time.strftime('%Y-%m-%d %H:%M') if trade.exit_time else "Open"
                duration = str(trade.trade_duration).split('.')[0] if trade.trade_duration else "N/A"
                
                report_lines.append(
                    f"Trade {i}: {trade.direction.upper()} | "
                    f"Entry: {entry_date} @ {trade.entry_price:.5f} | "
                    f"Exit: {exit_date} @ {trade.exit_price:.5f} | "
                    f"P&L: ${trade.profit_loss:.2f} | "
                    f"Duration: {duration}"
                )
            
            report_lines.append("")
        
        # Risk warnings
        report_lines.extend([
            "⚠️ RISK WARNINGS & DISCLAIMERS",
            "-" * 50,
            "• Past performance does not guarantee future results",
            "• This backtest uses historical data and may not reflect live trading conditions",
            "• Real trading involves slippage, latency, and execution risks not fully modeled",
            "• Market conditions can change rapidly and affect strategy performance",
            "• Use appropriate position sizing and risk management in live trading",
            "• Consider transaction costs and tax implications",
            ""
        ])
        
        # Footer
        report_lines.extend([
            "🏛️ ENHANCED REAL DATA BACKTESTING ENGINE v2.0",
            f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "Professional backtesting with REAL market data only",
            "=" * 100
        ])
        
        report_text = "\n".join(report_lines)
        
        # Save report if path provided
        if save_path:
            os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(report_text)
            logger.info(f"📄 Professional report saved: {save_path}")
        
        return report_text
    
    def create_interactive_dashboard(self, results: Dict[str, Any], save_path: Optional[str] = None):
        """Create interactive HTML dashboard for backtest results"""
        try:
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
            import plotly.offline as pyo
        except ImportError:
            logger.error("Plotly not available for interactive dashboard")
            return None
        
        logger.info("📊 Creating interactive dashboard...")
        
        # Create subplots
        fig = make_subplots(
            rows=4, cols=2,
            subplot_titles=(
                'Equity Curve', 'Drawdown',
                'Trade P&L Distribution', 'Monthly Returns',
                'Trade Duration Distribution', 'Signal Strength Over Time',
                'Rolling Sharpe Ratio', 'Performance Metrics'
            ),
            specs=[
                [{"secondary_y": False}, {"secondary_y": False}],
                [{"secondary_y": False}, {"secondary_y": False}],
                [{"secondary_y": False}, {"secondary_y": False}],
                [{"secondary_y": False}, {"type": "table"}]
            ],
            vertical_spacing=0.05
        )
        
        equity_curve = results['equity_curve']
        trades = results['trades']
        perf = results['performance_metrics']
        
        # 1. Equity Curve
        fig.add_trace(
            go.Scatter(
                x=equity_curve.index,
                y=equity_curve.values,
                mode='lines',
                name='Equity',
                line=dict(color='blue', width=2)
            ),
            row=1, col=1
        )
        
        # Add benchmark line
        fig.add_hline(
            y=results['initial_capital'],
            line_dash="dash",
            line_color="gray",
            annotation_text="Initial Capital",
            row=1, col=1
        )
        
        # 2. Drawdown
        if hasattr(results, 'drawdown_series') and results.get('drawdown_series'):
            drawdown_series = results['drawdown_series']
            fig.add_trace(
                go.Scatter(
                    x=equity_curve.index[:len(drawdown_series)],
                    y=[-dd * 100 for dd in drawdown_series],  # Convert to percentage
                    mode='lines',
                    name='Drawdown',
                    line=dict(color='red', width=1),
                    fill='tonexty'
                ),
                row=1, col=2
            )
        
        # 3. Trade P&L Distribution
        closed_trades = [t for t in trades if not t.is_open and t.profit_loss is not None]
        if closed_trades:
            pnl_values = [t.profit_loss for t in closed_trades]
            fig.add_trace(
                go.Histogram(
                    x=pnl_values,
                    name='Trade P&L',
                    nbinsx=30,
                    marker_color='green'
                ),
                row=2, col=1
            )
        
        # 4. Monthly Returns (simplified)
        try:
            monthly_equity = equity_curve.resample('M').last()
            monthly_returns = monthly_equity.pct_change().dropna() * 100
            
            fig.add_trace(
                go.Bar(
                    x=monthly_returns.index,
                    y=monthly_returns.values,
                    name='Monthly Returns (%)',
                    marker_color=['green' if x > 0 else 'red' for x in monthly_returns.values]
                ),
                row=2, col=2
            )
        except Exception as e:
            logger.warning(f"Could not create monthly returns chart: {e}")
        
        # 5. Trade Duration Distribution
        if closed_trades:
            durations = []
            for trade in closed_trades:
                if trade.trade_duration:
                    duration_hours = trade.trade_duration.total_seconds() / 3600
                    durations.append(duration_hours)
            
            if durations:
                fig.add_trace(
                    go.Histogram(
                        x=durations,
                        name='Duration (Hours)',
                        nbinsx=20,
                        marker_color='blue'
                    ),
                    row=3, col=1
                )
        
        # 6. Signal Strength Over Time (if available)
        if 'signals_history' in results:
            signals_hist = results['signals_history']
            if signals_hist:
                timestamps = [s['timestamp'] for s in signals_hist]
                strengths = [s.get('signal_strength', 0) for s in signals_hist]
                
                fig.add_trace(
                    go.Scatter(
                        x=timestamps,
                        y=strengths,
                        mode='markers',
                        name='Signal Strength',
                        marker=dict(
                            size=4,
                            color=strengths,
                            colorscale='RdYlGn',
                            showscale=True
                        )
                    ),
                    row=3, col=2
                )
        
        # 7. Rolling Sharpe Ratio
        if len(results['daily_returns']) > 30:
            returns_series = pd.Series(results['daily_returns'], 
                                     index=equity_curve.index[1:len(results['daily_returns'])+1])
            rolling_sharpe = returns_series.rolling(30).mean() / returns_series.rolling(30).std() * np.sqrt(252)
            rolling_sharpe = rolling_sharpe.dropna()
            
            if len(rolling_sharpe) > 0:
                fig.add_trace(
                    go.Scatter(
                        x=rolling_sharpe.index,
                        y=rolling_sharpe.values,
                        mode='lines',
                        name='30-Day Rolling Sharpe',
                        line=dict(color='purple', width=2)
                    ),
                    row=4, col=1
                )
        
        # 8. Performance Metrics Table
        metrics_data = [
            ['Total Return', f"{perf.total_return:.2%}"],
            ['Annualized Return', f"{perf.annualized_return:.2%}"],
            ['Sharpe Ratio', f"{perf.sharpe_ratio:.3f}"],
            ['Sortino Ratio', f"{perf.sortino_ratio:.3f}"],
            ['Max Drawdown', f"{perf.max_drawdown:.2%}"],
            ['Win Rate', f"{perf.win_rate:.1%}"],
            ['Profit Factor', f"{perf.profit_factor:.2f}"],
            ['Total Trades', f"{perf.total_trades}"]
        ]
        
        fig.add_trace(
            go.Table(
                header=dict(
                    values=['Metric', 'Value'],
                    fill_color='lightblue',
                    align='left',
                    font=dict(size=12, color='black')
                ),
                cells=dict(
                    values=[[row[0] for row in metrics_data],
                           [row[1] for row in metrics_data]],
                    fill_color='white',
                    align='left',
                    font=dict(size=11, color='black')
                )
            ),
            row=4, col=2
        )
        
        # Update layout
        fig.update_layout(
            height=1200,
            title={
                'text': f"Interactive Backtest Dashboard - {results['strategy']} on {results['symbol']}",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            showlegend=True,
            template='plotly_white'
        )
        
        # Show the dashboard
        if save_path:
            fig.write_html(save_path, include_plotlyjs=True)
            logger.info(f"📊 Interactive dashboard saved: {save_path}")
        else:
            pyo.plot(fig, filename='backtest_dashboard.html', auto_open=True)
        
        return fig
    
    def export_trades_to_csv(self, results: Dict[str, Any], file_path: str):
        """Export trades to CSV file for further analysis"""
        try:
            trades_data = []
            for trade in results['trades']:
                trades_data.append({
                    'trade_id': trade.trade_id,
                    'symbol': trade.symbol,
                    'strategy': trade.strategy,
                    'direction': trade.direction,
                    'entry_time': trade.entry_time,
                    'exit_time': trade.exit_time,
                    'entry_price': trade.entry_price,
                    'exit_price': trade.exit_price,
                    'size': trade.size,
                    'profit_loss': trade.profit_loss,
                    'profit_loss_pct': trade.profit_loss_pct,
                    'commission': trade.commission,
                    'slippage': trade.slippage,
                    'trade_duration': trade.trade_duration,
                    'stop_loss': trade.stop_loss,
                    'take_profit': trade.take_profit,
                    'entry_signal_strength': trade.entry_signal_strength,
                    'market_regime': trade.market_regime,
                    'is_open': trade.is_open
                })
            
            trades_df = pd.DataFrame(trades_data)
            trades_df.to_csv(file_path, index=False)
            logger.info(f"📊 Trades exported to CSV: {file_path}")
            
            return trades_df
            
        except Exception as e:
            logger.error(f"Error exporting trades to CSV: {e}")
            return None
    
    def compare_strategies(self, strategy_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare multiple strategy backtest results"""
        logger.info(f"📊 Comparing {len(strategy_results)} strategies...")
        
        comparison_data = []
        
        for result in strategy_results:
            perf = result['performance_metrics']
            comparison_data.append({
                'strategy': result['strategy'],
                'symbol': result['symbol'],
                'total_return': perf.total_return,
                'annualized_return': perf.annualized_return,
                'sharpe_ratio': perf.sharpe_ratio,
                'sortino_ratio': perf.sortino_ratio,
                'max_drawdown': perf.max_drawdown,
                'win_rate': perf.win_rate,
                'profit_factor': perf.profit_factor,
                'total_trades': perf.total_trades,
                'data_quality_score': result['data_quality_metrics']['data_quality_score']
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        
        # Rank strategies
        comparison_df['rank_return'] = comparison_df['total_return'].rank(ascending=False)
        comparison_df['rank_sharpe'] = comparison_df['sharpe_ratio'].rank(ascending=False)
        comparison_df['rank_drawdown'] = comparison_df['max_drawdown'].rank(ascending=True)
        
        # Calculate composite score
        comparison_df['composite_score'] = (
            comparison_df['rank_return'] * 0.4 +
            comparison_df['rank_sharpe'] * 0.3 +
            comparison_df['rank_drawdown'] * 0.3
        )
        
        comparison_df = comparison_df.sort_values('composite_score')
        
        comparison_summary = {
            'comparison_table': comparison_df,
            'best_strategy': comparison_df.iloc[0]['strategy'],
            'best_return': comparison_df.loc[comparison_df['total_return'].idxmax(), 'strategy'],
            'best_sharpe': comparison_df.loc[comparison_df['sharpe_ratio'].idxmax(), 'strategy'],
            'lowest_drawdown': comparison_df.loc[comparison_df['max_drawdown'].idxmin(), 'strategy']
        }
        
        logger.info(f"✅ Strategy comparison completed")
        logger.info(f"🏆 Best overall strategy: {comparison_summary['best_strategy']}")
        logger.info(f"📈 Best return: {comparison_summary['best_return']}")
        logger.info(f"📊 Best Sharpe: {comparison_summary['best_sharpe']}")
        
        return comparison_summary


# Example usage and testing functions
def demo_backtest():
    """Demonstration of the enhanced backtesting engine"""
    
    print("🚀 Enhanced Real Data Backtesting Engine Demo")
    print("=" * 60)
    
    # Initialize engine
    engine = EnhancedRealDataBacktestingEngine(
        initial_capital=100000,
        commission=0.0001,
        slippage=0.0001,
        risk_per_trade=0.02
    )
    
    # Test with simple moving average strategy
    class SimpleMAStrategy:
        def generate_signals(self, data: pd.DataFrame) -> pd.Series:
            data = data.copy()
            data['sma_fast'] = data['close'].rolling(10).mean()
            data['sma_slow'] = data['close'].rolling(20).mean()
            
            signals = pd.Series(0, index=data.index)
            signals[(data['sma_fast'] > data['sma_slow']) & 
                    (data['sma_fast'].shift(1) <= data['sma_slow'].shift(1))] = 1
            signals[(data['sma_fast'] < data['sma_slow']) & 
                    (data['sma_fast'].shift(1) >= data['sma_slow'].shift(1))] = -1
            
            return signals
        
        def get_strategy_name(self):
            return "Simple_MA_Crossover"
    
    try:
        # Run backtest
        strategy = SimpleMAStrategy()
        results = engine.run_comprehensive_backtest(
            symbol="EURUSD",
            timeframe="H1",
            strategy=strategy,
            data_sources=[
                "data/training/mt5_historical_data.h5",
                "data/historical/EURUSD_H1.csv"
            ]
        )
        
        # Generate report
        report = engine.generate_professional_report(results)
        print(report)
        
        # Create interactive dashboard
        engine.create_interactive_dashboard(results, "demo_dashboard.html")
        
        # Export trades
        engine.export_trades_to_csv(results, "demo_trades.csv")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False


if __name__ == "__main__":
    # Run demo
    success = demo_backtest()
    
    if success:
        print("\n🎉 Enhanced Real Data Backtesting Engine Demo Completed Successfully!")
        print("✅ Professional backtesting with REAL market data")
        print("✅ Comprehensive performance analysis")
        print("✅ Interactive dashboard created") 
        print("✅ Professional reporting generated")
        print("✅ Ready for RTM and ICT strategy testing")
    else:
        print("\n❌ Demo failed - please check data availability and dependencies")
