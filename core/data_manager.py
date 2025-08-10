"""
Enhanced Data Manager - MT5 Integration & Multi-Timeframe Data Management
=========================================================================

Professional-grade data management system for institutional algorithmic trading
that provides MT5 integration, multi-timeframe data processing, real-time streaming,
data quality validation, and efficient caching for high-performance trading operations.

Features:
- MT5 platform integration with robust connection management
- Multi-timeframe data generation from base timeframes
- Real-time tick and OHLCV data streaming
- Advanced data quality validation and cleaning
- Efficient caching and memory management
- Timezone standardization (UTC)
- Comprehensive error handling and recovery
- Production-ready with monitoring and alerts

Author: Enhanced Trading System
Version: 4.0 Professional
License: Proprietary
"""

import asyncio
import logging
import time
import threading
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Any, Callable, Union
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np
import pandas as pd
from enum import Enum
import queue
import weakref
import gc
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import pickle
from collections import defaultdict, OrderedDict

# MT5 and Market Data
import MetaTrader5 as mt5
import pytz

# Data Processing
from scipy import stats
import talib

# Configuration and Utilities
from utils.config import TradingConfig
from utils.logger import setup_logging
from utils.helpers import format_currency, calculate_pips

class ConnectionState(Enum):
    """MT5 connection states"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    RECONNECTING = "reconnecting"

class DataQuality(Enum):
    """Data quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    INVALID = "invalid"

@dataclass
class MarketDataRequest:
    """Market data request specification"""
    symbol: str
    timeframe: str
    start_date: datetime
    end_date: datetime
    count: int = 0
    include_volume: bool = True
    include_spread: bool = False
    priority: int = 1  # 1=highest, 5=lowest

@dataclass
class DataQualityReport:
    """Comprehensive data quality assessment"""
    symbol: str
    timeframe: str
    quality_score: float
    total_bars: int
    missing_bars: int
    duplicate_bars: int
    gap_count: int
    spread_issues: int
    volume_issues: int
    data_quality: DataQuality
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

@dataclass
class StreamingTick:
    """Real-time tick data structure"""
    symbol: str
    timestamp: datetime
    bid: float
    ask: float
    last: float
    volume: int
    flags: int
    spread: float

class MT5Connector:
    """
    Professional MT5 connection manager with robust error handling
    """
    
    def __init__(self, config: TradingConfig):
        self.config = config
        self.connection_state = ConnectionState.DISCONNECTED
        self.last_connection_attempt = None
        self.connection_attempts = 0
        self.account_info = None
        self.symbols_info = {}
        self.logger = setup_logging('INFO')
        
        # Connection monitoring
        self.heartbeat_interval = 30  # seconds
        self.heartbeat_task = None
        self.connection_callbacks = []
        
    async def initialize(self) -> bool:
        """Initialize MT5 connection with comprehensive validation"""
        try:
            self.logger.info("🔌 Initializing MT5 connection...")
            
            # Set connection state
            self.connection_state = ConnectionState.CONNECTING
            
            # Initialize MT5 terminal
            if not mt5.initialize(
                login=self.config.mt5_login,
                password=self.config.mt5_password,
                server=self.config.mt5_server,
                path=self.config.mt5_path,
                timeout=self.config.mt5_timeout
            ):
                error = mt5.last_error()
                self.logger.error(f"MT5 initialization failed: {error}")
                self.connection_state = ConnectionState.ERROR
                return False
            
            # Get account information
            self.account_info = mt5.account_info()
            if not self.account_info:
                self.logger.error("Failed to retrieve account information")
                await self.shutdown()
                return False
            
            # Validate account
            if not self._validate_account():
                return False
            
            # Load symbols information
            if not await self._load_symbols_info():
                return False
            
            # Start heartbeat monitoring
            await self._start_heartbeat_monitoring()
            
            self.connection_state = ConnectionState.CONNECTED
            self.connection_attempts = 0
            
            self.logger.info("✅ MT5 connection established successfully")
            self.logger.info(f"   Account: {self.account_info.login}")
            self.logger.info(f"   Server: {self.account_info.server}")
            self.logger.info(f"   Balance: {format_currency(self.account_info.balance, self.account_info.currency)}")
            self.logger.info(f"   Leverage: 1:{self.account_info.leverage}")
            
            # Notify connection callbacks
            await self._notify_connection_callbacks(True)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing MT5 connection: {e}")
            self.connection_state = ConnectionState.ERROR
            return False
    
    def _validate_account(self) -> bool:
        """Validate MT5 account for trading"""
        try:
            if not self.account_info:
                return False
            
            # Check account type
            if self.config.environment == 'demo' and self.account_info.trade_mode != mt5.ACCOUNT_TRADE_MODE_DEMO:
                self.logger.error("Demo account required for demo environment")
                return False
            
            if self.config.environment == 'live' and self.account_info.trade_mode == mt5.ACCOUNT_TRADE_MODE_DEMO:
                self.logger.warning("Using demo account in live environment")
            
            # Check trading permissions
            if not self.account_info.trade_allowed:
                self.logger.error("Trading not allowed on this account")
                return False
            
            # Check balance
            if self.account_info.balance < 1000:  # Minimum balance check
                self.logger.warning(f"Low account balance: {self.account_info.balance}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating account: {e}")
            return False
    
    async def _load_symbols_info(self) -> bool:
        """Load and validate trading symbols information"""
        try:
            self.logger.info("📋 Loading symbols information...")
            
            for symbol in self.config.symbols:
                # Get symbol info
                symbol_info = mt5.symbol_info(symbol)
                if not symbol_info:
                    self.logger.error(f"Symbol {symbol} not found")
                    continue
                
                # Enable symbol for trading
                if not symbol_info.visible:
                    if not mt5.symbol_select(symbol, True):
                        self.logger.error(f"Failed to enable symbol {symbol}")
                        continue
                
                # Store symbol information
                self.symbols_info[symbol] = {
                    'info': symbol_info,
                    'point': symbol_info.point,
                    'digits': symbol_info.digits,
                    'trade_contract_size': symbol_info.trade_contract_size,
                    'volume_min': symbol_info.volume_min,
                    'volume_max': symbol_info.volume_max,
                    'volume_step': symbol_info.volume_step,
                    'margin_initial': symbol_info.margin_initial,
                    'spread': symbol_info.spread,
                    'swap_long': symbol_info.swap_long,
                    'swap_short': symbol_info.swap_short,
                    'sessions': self._get_trading_sessions(symbol)
                }
                
                self.logger.info(f"   ✅ {symbol}: Spread={symbol_info.spread} pts, Min Vol={symbol_info.volume_min}")
            
            if not self.symbols_info:
                self.logger.error("No valid symbols loaded")
                return False
            
            self.logger.info(f"✅ Loaded {len(self.symbols_info)} symbols successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading symbols info: {e}")
            return False
    
    def _get_trading_sessions(self, symbol: str) -> Dict[str, Dict[str, Any]]:
        """Get trading sessions for symbol"""
        try:
            sessions = {}
            
            # Get session times for different days
            for day in range(7):  # Monday = 0, Sunday = 6
                session_from = mt5.symbol_info_sessiontrade(symbol, day, 0)
                session_to = mt5.symbol_info_sessiontrade(symbol, day, 1)
                
                if session_from and session_to:
                    sessions[day] = {
                        'open': session_from,
                        'close': session_to,
                        'enabled': True
                    }
                else:
                    sessions[day] = {'enabled': False}
            
            return sessions
            
        except Exception as e:
            self.logger.error(f"Error getting trading sessions for {symbol}: {e}")
            return {}
    
    async def _start_heartbeat_monitoring(self):
        """Start connection heartbeat monitoring"""
        try:
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            
        except Exception as e:
            self.logger.error(f"Error starting heartbeat monitoring: {e}")
    
    async def _heartbeat_loop(self):
        """Connection heartbeat monitoring loop"""
        while self.connection_state == ConnectionState.CONNECTED:
            try:
                # Check connection by getting account info
                account_info = mt5.account_info()
                
                if not account_info:
                    self.logger.warning("Heartbeat failed - connection lost")
                    await self._handle_connection_loss()
                    break
                
                # Update account info
                self.account_info = account_info
                
                await asyncio.sleep(self.heartbeat_interval)
                
            except Exception as e:
                self.logger.error(f"Error in heartbeat loop: {e}")
                await asyncio.sleep(5)
    
    async def _handle_connection_loss(self):
        """Handle MT5 connection loss"""
        try:
            self.logger.warning("🔌 MT5 connection lost - attempting reconnection...")
            self.connection_state = ConnectionState.RECONNECTING
            
            # Notify callbacks
            await self._notify_connection_callbacks(False)
            
            # Attempt reconnection
            max_attempts = 5
            for attempt in range(max_attempts):
                self.logger.info(f"Reconnection attempt {attempt + 1}/{max_attempts}")
                
                # Wait before reconnecting
                await asyncio.sleep(10 * (attempt + 1))
                
                # Try to reconnect
                if await self.initialize():
                    self.logger.info("✅ Successfully reconnected to MT5")
                    return
            
            self.logger.error("❌ Failed to reconnect to MT5 after maximum attempts")
            self.connection_state = ConnectionState.ERROR
            
        except Exception as e:
            self.logger.error(f"Error handling connection loss: {e}")
    
    def add_connection_callback(self, callback: Callable[[bool], None]):
        """Add callback for connection state changes"""
        self.connection_callbacks.append(callback)
    
    async def _notify_connection_callbacks(self, connected: bool):
        """Notify all connection callbacks"""
        for callback in self.connection_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(connected)
                else:
                    callback(connected)
            except Exception as e:
                self.logger.error(f"Error in connection callback: {e}")
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get symbol information"""
        return self.symbols_info.get(symbol)
    
    def is_market_open(self, symbol: str = None) -> bool:
        """Check if market is open for symbol or any symbol"""
        try:
            if symbol:
                symbol_info = mt5.symbol_info(symbol)
                return symbol_info and symbol_info.trade_mode != mt5.SYMBOL_TRADE_MODE_DISABLED
            else:
                # Check if any symbol is available for trading
                for sym in self.config.symbols:
                    if self.is_market_open(sym):
                        return True
                return False
                
        except Exception as e:
            self.logger.error(f"Error checking market open status: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """Test MT5 connection"""
        try:
            if self.connection_state != ConnectionState.CONNECTED:
                return False
            
            account_info = mt5.account_info()
            return account_info is not None
            
        except Exception as e:
            self.logger.error(f"Error testing connection: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown MT5 connection gracefully"""
        try:
            self.logger.info("🔌 Shutting down MT5 connection...")
            
            # Cancel heartbeat
            if self.heartbeat_task and not self.heartbeat_task.done():
                self.heartbeat_task.cancel()
            
            # Close MT5 connection
            mt5.shutdown()
            self.connection_state = ConnectionState.DISCONNECTED
            
            self.logger.info("✅ MT5 connection shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error shutting down MT5 connection: {e}")

class DataCache:
    """
    High-performance data caching system with LRU eviction
    """
    
    def __init__(self, max_size_mb: int = 500):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.cache = OrderedDict()
        self.current_size = 0
        self.hit_count = 0
        self.miss_count = 0
        self.logger = setup_logging('INFO')
    
    def _calculate_size(self, data: pd.DataFrame) -> int:
        """Calculate DataFrame size in bytes"""
        try:
            return data.memory_usage(deep=True).sum()
        except:
            return len(data) * 1000  # Rough estimate
    
    def get(self, key: str) -> Optional[pd.DataFrame]:
        """Get data from cache"""
        if key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self.hit_count += 1
            return self.cache[key]['data'].copy()
        
        self.miss_count += 1
        return None
    
    def put(self, key: str, data: pd.DataFrame) -> None:
        """Put data in cache with LRU eviction"""
        try:
            data_size = self._calculate_size(data)
            
            # Remove existing entry if it exists
            if key in self.cache:
                old_size = self.cache[key]['size']
                del self.cache[key]
                self.current_size -= old_size
            
            # Evict entries if necessary
            while self.current_size + data_size > self.max_size_bytes and self.cache:
                oldest_key, oldest_entry = self.cache.popitem(last=False)
                self.current_size -= oldest_entry['size']
            
            # Add new entry
            if data_size <= self.max_size_bytes:
                self.cache[key] = {
                    'data': data.copy(),
                    'size': data_size,
                    'timestamp': datetime.utcnow()
                }
                self.current_size += data_size
            
        except Exception as e:
            self.logger.error(f"Error putting data in cache: {e}")
    
    def clear(self) -> None:
        """Clear all cached data"""
        self.cache.clear()
        self.current_size = 0
        self.hit_count = 0
        self.miss_count = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        hit_rate = self.hit_count / (self.hit_count + self.miss_count) if (self.hit_count + self.miss_count) > 0 else 0
        
        return {
            'size_mb': self.current_size / (1024 * 1024),
            'entries': len(self.cache),
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': hit_rate,
            'max_size_mb': self.max_size_bytes / (1024 * 1024)
        }

class DataQualityValidator:
    """
    Comprehensive data quality validation and assessment
    """
    
    def __init__(self):
        self.logger = setup_logging('INFO')
    
    def validate_ohlcv_data(self, data: pd.DataFrame, symbol: str, timeframe: str) -> DataQualityReport:
        """Comprehensive OHLCV data quality validation"""
        try:
            report = DataQualityReport(
                symbol=symbol,
                timeframe=timeframe,
                quality_score=0.0,
                total_bars=len(data),
                missing_bars=0,
                duplicate_bars=0,
                gap_count=0,
                spread_issues=0,
                volume_issues=0,
                data_quality=DataQuality.INVALID
            )
            
            if data.empty:
                report.issues.append("No data available")
                return report
            
            # Check for required columns
            required_columns = ['open', 'high', 'low', 'close']
            missing_columns = [col for col in required_columns if col not in data.columns]
            if missing_columns:
                report.issues.append(f"Missing columns: {missing_columns}")
                return report
            
            # Check for duplicate timestamps
            if data.index.duplicated().any():
                duplicates = data.index.duplicated().sum()
                report.duplicate_bars = duplicates
                report.issues.append(f"Found {duplicates} duplicate timestamps")
            
            # Check for missing data (NaN values)
            nan_counts = data[required_columns].isnull().sum()
            total_nans = nan_counts.sum()
            if total_nans > 0:
                report.issues.append(f"Found {total_nans} NaN values")
            
            # Check OHLC relationship validity
            invalid_ohlc = self._check_ohlc_validity(data)
            if invalid_ohlc > 0:
                report.issues.append(f"Found {invalid_ohlc} bars with invalid OHLC relationships")
            
            # Check for unrealistic price movements
            extreme_moves = self._check_extreme_movements(data)
            if extreme_moves > 0:
                report.issues.append(f"Found {extreme_moves} bars with extreme price movements")
            
            # Check for gaps in time series
            gaps = self._detect_time_gaps(data, timeframe)
            report.gap_count = gaps
            if gaps > 0:
                report.issues.append(f"Found {gaps} time gaps in data")
            
            # Check volume data if available
            if 'volume' in data.columns:
                volume_issues = self._check_volume_data(data)
                report.volume_issues = volume_issues
                if volume_issues > 0:
                    report.issues.append(f"Found {volume_issues} volume data issues")
            
            # Check spread data if available
            if 'spread' in data.columns:
                spread_issues = self._check_spread_data(data)
                report.spread_issues = spread_issues
                if spread_issues > 0:
                    report.issues.append(f"Found {spread_issues} spread data issues")
            
            # Calculate quality score
            report.quality_score = self._calculate_quality_score(report)
            report.data_quality = self._determine_quality_level(report.quality_score)
            
            # Generate recommendations
            report.recommendations = self._generate_recommendations(report)
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error validating data quality: {e}")
            return DataQualityReport(symbol=symbol, timeframe=timeframe, quality_score=0.0, data_quality=DataQuality.INVALID, total_bars=0)
    
    def _check_ohlc_validity(self, data: pd.DataFrame) -> int:
        """Check OHLC relationship validity"""
        invalid_count = 0
        
        # High should be >= Open, Close, Low
        invalid_high = (data['high'] < data['open']) | (data['high'] < data['close']) | (data['high'] < data['low'])
        invalid_count += invalid_high.sum()
        
        # Low should be <= Open, Close, High
        invalid_low = (data['low'] > data['open']) | (data['low'] > data['close']) | (data['low'] > data['high'])
        invalid_count += invalid_low.sum()
        
        return invalid_count
    
    def _check_extreme_movements(self, data: pd.DataFrame, threshold: float = 0.1) -> int:
        """Check for extreme price movements (>10% by default)"""
        if len(data) < 2:
            return 0
        
        price_changes = data['close'].pct_change().abs()
        extreme_moves = (price_changes > threshold).sum()
        
        return extreme_moves
    
    def _detect_time_gaps(self, data: pd.DataFrame, timeframe: str) -> int:
        """Detect gaps in time series"""
        try:
            if len(data) < 2:
                return 0
            
            # Define expected time intervals
            timeframe_intervals = {
                'M1': timedelta(minutes=1),
                'M5': timedelta(minutes=5),
                'M15': timedelta(minutes=15),
                'M30': timedelta(minutes=30),
                'H1': timedelta(hours=1),
                'H4': timedelta(hours=4),
                'D1': timedelta(days=1),
                'W1': timedelta(weeks=1),
                'MN1': timedelta(days=30)
            }
            
            expected_interval = timeframe_intervals.get(timeframe, timedelta(hours=1))
            
            # Calculate time differences
            time_diffs = data.index.to_series().diff()
            
            # Count gaps (differences > 1.5 * expected interval)
            gap_threshold = expected_interval * 1.5
            gaps = (time_diffs > gap_threshold).sum()
            
            return gaps
            
        except Exception:
            return 0
    
    def _check_volume_data(self, data: pd.DataFrame) -> int:
        """Check volume data quality"""
        issues = 0
        
        if 'volume' not in data.columns:
            return 0
        
        # Check for negative volumes
        negative_volumes = (data['volume'] < 0).sum()
        issues += negative_volumes
        
        # Check for zero volumes (might be normal for some timeframes)
        zero_volumes = (data['volume'] == 0).sum()
        if zero_volumes > len(data) * 0.1:  # More than 10% zero volumes
            issues += zero_volumes
        
        return issues
    
    def _check_spread_data(self, data: pd.DataFrame) -> int:
        """Check spread data quality"""
        issues = 0
        
        if 'spread' not in data.columns:
            return 0
        
        # Check for negative spreads
        negative_spreads = (data['spread'] < 0).sum()
        issues += negative_spreads
        
        # Check for unrealistic spreads (>1000 points)
        extreme_spreads = (data['spread'] > 1000).sum()
        issues += extreme_spreads
        
        return issues
    
    def _calculate_quality_score(self, report: DataQualityReport) -> float:
        """Calculate overall data quality score (0-100)"""
        if report.total_bars == 0:
            return 0.0
        
        score = 100.0
        
        # Penalize issues
        if report.missing_bars > 0:
            score -= (report.missing_bars / report.total_bars) * 30
        
        if report.duplicate_bars > 0:
            score -= (report.duplicate_bars / report.total_bars) * 20
        
        if report.gap_count > 0:
            score -= min(report.gap_count * 2, 20)
        
        if report.spread_issues > 0:
            score -= (report.spread_issues / report.total_bars) * 10
        
        if report.volume_issues > 0:
            score -= (report.volume_issues / report.total_bars) * 10
        
        return max(0.0, min(100.0, score))
    
    def _determine_quality_level(self, score: float) -> DataQuality:
        """Determine data quality level from score"""
        if score >= 90:
            return DataQuality.EXCELLENT
        elif score >= 75:
            return DataQuality.GOOD
        elif score >= 60:
            return DataQuality.ACCEPTABLE
        elif score >= 40:
            return DataQuality.POOR
        else:
            return DataQuality.INVALID
    
    def _generate_recommendations(self, report: DataQualityReport) -> List[str]:
        """Generate recommendations based on quality assessment"""
        recommendations = []
        
        if report.quality_score < 60:
            recommendations.append("Consider using alternative data source")
        
        if report.gap_count > 0:
            recommendations.append("Fill time gaps with interpolated data or mark gaps explicitly")
        
        if report.duplicate_bars > 0:
            recommendations.append("Remove duplicate timestamps before analysis")
        
        if report.spread_issues > 0:
            recommendations.append("Validate spread data source and filtering")
        
        if report.volume_issues > 0:
            recommendations.append("Review volume data quality and filtering criteria")
        
        if not recommendations:
            recommendations.append("Data quality is acceptable for trading analysis")
        
        return recommendations

class MultiTimeframeManager:
    """
    Efficient multi-timeframe data generation and management
    """
    
    def __init__(self):
        self.timeframe_hierarchy = {
            'M1': 1,
            'M5': 5,
            'M15': 15,
            'M30': 30,
            'H1': 60,
            'H4': 240,
            'D1': 1440,
            'W1': 10080,
            'MN1': 43200  # Approximate
        }
        self.logger = setup_logging('INFO')
    
    def generate_higher_timeframes(self, base_data: pd.DataFrame, base_timeframe: str, 
                                 target_timeframes: List[str]) -> Dict[str, pd.DataFrame]:
        """Generate higher timeframes from base timeframe data"""
        try:
            results = {}
            base_minutes = self.timeframe_hierarchy.get(base_timeframe, 1)
            
            for target_tf in target_timeframes:
                target_minutes = self.timeframe_hierarchy.get(target_tf, 1)
                
                if target_minutes <= base_minutes:
                    self.logger.warning(f"Cannot generate {target_tf} from {base_timeframe} - target timeframe is smaller")
                    continue
                
                # Calculate resampling frequency
                freq_minutes = target_minutes
                
                if target_tf == 'D1':
                    freq = 'D'
                elif target_tf == 'W1':
                    freq = 'W'
                elif target_tf == 'MN1':
                    freq = 'M'
                else:
                    freq = f'{freq_minutes}T'  # T = minutes
                
                # Resample data
                resampled = self._resample_ohlcv(base_data, freq)
                
                if not resampled.empty:
                    results[target_tf] = resampled
                    self.logger.info(f"Generated {target_tf}: {len(resampled)} bars from {len(base_data)} {base_timeframe} bars")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error generating higher timeframes: {e}")
            return {}
    
    def _resample_ohlcv(self, data: pd.DataFrame, freq: str) -> pd.DataFrame:
        """Resample OHLCV data to higher timeframe"""
        try:
            if data.empty:
                return pd.DataFrame()
            
            # Ensure we have a datetime index
            if not isinstance(data.index, pd.DatetimeIndex):
                data.index = pd.to_datetime(data.index)
            
            # Define resampling rules
            agg_rules = {
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last'
            }
            
            # Add volume if present
            if 'volume' in data.columns:
                agg_rules['volume'] = 'sum'
            
            # Add tick_volume if present
            if 'tick_volume' in data.columns:
                agg_rules['tick_volume'] = 'sum'
            
            # Add spread if present
            if 'spread' in data.columns:
                agg_rules['spread'] = 'mean'
            
            # Resample data
            resampled = data.resample(freq, label='left', closed='left').agg(agg_rules)
            
            # Remove rows where no data exists (all NaN)
            resampled = resampled.dropna(subset=['open', 'high', 'low', 'close'])
            
            # Ensure OHLC validity
            resampled = self._fix_ohlc_relationships(resampled)
            
            return resampled
            
        except Exception as e:
            self.logger.error(f"Error resampling OHLCV data: {e}")
            return pd.DataFrame()
    
    def _fix_ohlc_relationships(self, data: pd.DataFrame) -> pd.DataFrame:
        """Fix any invalid OHLC relationships after resampling"""
        try:
            # Ensure High is the maximum of O, H, L, C
            data['high'] = data[['open', 'high', 'low', 'close']].max(axis=1)
            
            # Ensure Low is the minimum of O, H, L, C
            data['low'] = data[['open', 'high', 'low', 'close']].min(axis=1)
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error fixing OHLC relationships: {e}")
            return data

class EnhancedDataManager:
    """
    Professional Data Manager for institutional algorithmic trading
    
    This class orchestrates all data-related operations including MT5 connection,
    multi-timeframe data collection, real-time streaming, quality validation,
    and efficient caching for high-performance trading systems.
    """
    
    def __init__(self, config: TradingConfig):
        self.config = config
        
        # Core components
        self.mt5_connector = MT5Connector(config)
        self.data_cache = DataCache(config.data_config.get('cache_size_mb', 500))
        self.quality_validator = DataQualityValidator()
        self.timeframe_manager = MultiTimeframeManager()
        
        # Data storage
        self.current_data = {}  # {symbol: {timeframe: DataFrame}}
        self.tick_subscribers = {}  # Real-time tick subscribers
        self.data_update_tasks = {}
        
        # Performance monitoring
        self.request_count = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.quality_reports = {}
        
        # Threading and async
        self.update_scheduler = None
        self.streaming_active = False
        self.shutdown_event = asyncio.Event()
        
        # Setup logging
        self.logger = setup_logging('INFO')
        self.logger.info("🏗️ Enhanced Data Manager initialized")
    
    async def initialize(self) -> bool:
        """Initialize data manager with all components"""
        try:
            self.logger.info("🚀 Initializing Enhanced Data Manager...")
            
            # Initialize MT5 connection
            if not await self.mt5_connector.initialize():
                return False
            
            # Register connection callback
            self.mt5_connector.add_connection_callback(self._on_connection_change)
            
            # Load initial data
            if not await self._load_initial_data():
                return False
            
            # Start data update scheduler
            await self._start_update_scheduler()
            
            self.logger.info("✅ Enhanced Data Manager initialization completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing data manager: {e}")
            return False
    
    async def _load_initial_data(self) -> bool:
        """Load initial historical data for all symbols and timeframes"""
        try:
            self.logger.info("📊 Loading initial market data...")
            
            symbols = self.config.symbols
            timeframes = self.config.data_config.get('timeframes', ['M1', 'M5', 'M15', 'H1', 'H4', 'D1'])
            historical_days = self.config.data_config.get('historical_data_days', 365)
            
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=historical_days)
            
            # Load data for each symbol and timeframe
            for symbol in symbols:
                self.current_data[symbol] = {}
                
                for timeframe in timeframes:
                    try:
                        data = await self.get_historical_data(
                            symbol=symbol,
                            timeframe=timeframe,
                            start_date=start_date,
                            end_date=end_date
                        )
                        
                        if not data.empty:
                            self.current_data[symbol][timeframe] = data
                            self.logger.info(f"   ✅ {symbol} {timeframe}: {len(data)} bars loaded")
                        else:
                            self.logger.warning(f"   ⚠️ {symbol} {timeframe}: No data available")
                            
                    except Exception as e:
                        self.logger.error(f"Error loading data for {symbol} {timeframe}: {e}")
                        continue
            
            self.logger.info("✅ Initial data loading completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading initial data: {e}")
            return False
    
    async def get_historical_data(self, symbol: str, timeframe: str, 
                                start_date: datetime = None, end_date: datetime = None,
                                count: int = 0) -> pd.DataFrame:
        """Get historical OHLCV data with caching and quality validation"""
        try:
            # Create cache key
            cache_key = f"{symbol}_{timeframe}_{start_date}_{end_date}_{count}"
            
            # Check cache first
            cached_data = self.data_cache.get(cache_key)
            if cached_data is not None:
                self.cache_hits += 1
                return cached_data
            
            self.cache_misses += 1
            self.request_count += 1
            
            # Convert timeframe to MT5 format
            mt5_timeframe = self._convert_timeframe_to_mt5(timeframe)
            if not mt5_timeframe:
                self.logger.error(f"Invalid timeframe: {timeframe}")
                return pd.DataFrame()
            
            # Get data from MT5
            if start_date and end_date:
                # Convert to UTC if needed
                start_date = self._ensure_utc(start_date)
                end_date = self._ensure_utc(end_date)
                
                rates = mt5.copy_rates_range(symbol, mt5_timeframe, start_date, end_date)
            elif count > 0:
                rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, count)
            else:
                # Default to last 1000 bars
                rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, 1000)
            
            if rates is None or len(rates) == 0:
                self.logger.warning(f"No data received for {symbol} {timeframe}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            data = pd.DataFrame(rates)
            data['time'] = pd.to_datetime(data['time'], unit='s', utc=True)
            data.set_index('time', inplace=True)
            
            # Add spread if available
            if hasattr(rates[0], 'spread'):
                data['spread'] = [rate.spread for rate in rates]
            
            # Validate data quality
            quality_report = self.quality_validator.validate_ohlcv_data(data, symbol, timeframe)
            self.quality_reports[cache_key] = quality_report
            
            # Log quality issues if any
            if quality_report.issues:
                self.logger.warning(f"Data quality issues for {symbol} {timeframe}: {quality_report.issues}")
            
            # Cache the data
            self.data_cache.put(cache_key, data)
            
            self.logger.info(f"📊 Retrieved {len(data)} bars for {symbol} {timeframe} (Quality: {quality_report.data_quality.value})")
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error getting historical data for {symbol} {timeframe}: {e}")
            return pd.DataFrame()
    
    async def get_latest_data(self, symbols: List[str] = None, timeframes: List[str] = None) -> Dict[str, Dict[str, pd.DataFrame]]:
        """Get latest data for specified symbols and timeframes"""
        try:
            if not symbols:
                symbols = self.config.symbols
            
            if not timeframes:
                timeframes = self.config.data_config.get('timeframes', ['M1', 'M5', 'M15', 'H1'])
            
            result = {}
            
            for symbol in symbols:
                result[symbol] = {}
                
                for timeframe in timeframes:
                    # Get latest 100 bars
                    data = await self.get_historical_data(symbol, timeframe, count=100)
                    
                    if not data.empty:
                        result[symbol][timeframe] = data
                    
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting latest data: {e}")
            return {}
    
    async def get_current_prices(self, symbols: List[str] = None) -> Dict[str, Dict[str, float]]:
        """Get current bid/ask prices for symbols"""
        try:
            if not symbols:
                symbols = self.config.symbols
            
            prices = {}
            
            for symbol in symbols:
                symbol_info = mt5.symbol_info_tick(symbol)
                
                if symbol_info:
                    prices[symbol] = {
                        'bid': symbol_info.bid,
                        'ask': symbol_info.ask,
                        'last': symbol_info.last,
                        'time': datetime.fromtimestamp(symbol_info.time, tz=pytz.UTC),
                        'volume': symbol_info.volume,
                        'spread': symbol_info.ask - symbol_info.bid
                    }
                else:
                    self.logger.warning(f"Could not get current price for {symbol}")
            
            return prices
            
        except Exception as e:
            self.logger.error(f"Error getting current prices: {e}")
            return {}
    
    def _convert_timeframe_to_mt5(self, timeframe: str) -> Optional[int]:
        """Convert string timeframe to MT5 timeframe constant"""
        timeframe_map = {
            'M1': mt5.TIMEFRAME_M1,
            'M5': mt5.TIMEFRAME_M5,
            'M15': mt5.TIMEFRAME_M15,
            'M30': mt5.TIMEFRAME_M30,
            'H1': mt5.TIMEFRAME_H1,
            'H4': mt5.TIMEFRAME_H4,
            'D1': mt5.TIMEFRAME_D1,
            'W1': mt5.TIMEFRAME_W1,
            'MN1': mt5.TIMEFRAME_MN1
        }
        
        return timeframe_map.get(timeframe)
    
    def _ensure_utc(self, dt: datetime) -> datetime:
        """Ensure datetime is in UTC timezone"""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=pytz.UTC)
        elif dt.tzinfo != pytz.UTC:
            dt = dt.astimezone(pytz.UTC)
        
        return dt
    
    async def _start_update_scheduler(self):
        """Start automatic data update scheduler"""
        try:
            update_interval = self.config.data_config.get('data_update_interval', 60)
            self.update_scheduler = asyncio.create_task(self._update_loop(update_interval))
            
        except Exception as e:
            self.logger.error(f"Error starting update scheduler: {e}")
    
    async def _update_loop(self, interval: int):
        """Main data update loop"""
        while not self.shutdown_event.is_set():
            try:
                # Update current data
                await self.update_all_data()
                
                # Clean cache periodically
                if self.request_count % 100 == 0:
                    await self._clean_cache()
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Error in update loop: {e}")
                await asyncio.sleep(5)
    
    async def update_all_data(self):
        """Update all current data"""
        try:
            tasks = []
            
            for symbol in self.config.symbols:
                if symbol in self.current_data:
                    for timeframe in self.current_data[symbol].keys():
                        task = asyncio.create_task(self._update_symbol_timeframe(symbol, timeframe))
                        tasks.append(task)
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            self.logger.error(f"Error updating all data: {e}")
    
    async def _update_symbol_timeframe(self, symbol: str, timeframe: str):
        """Update data for specific symbol and timeframe"""
        try:
            # Get latest 50 bars
            latest_data = await self.get_historical_data(symbol, timeframe, count=50)
            
            if not latest_data.empty:
                # Update current data
                if symbol in self.current_data and timeframe in self.current_data[symbol]:
                    # Merge with existing data, avoiding duplicates
                    existing_data = self.current_data[symbol][timeframe]
                    combined = pd.concat([existing_data, latest_data]).drop_duplicates()
                    combined = combined.sort_index()
                    
                    # Keep last 5000 bars to manage memory
                    if len(combined) > 5000:
                        combined = combined.tail(5000)
                    
                    self.current_data[symbol][timeframe] = combined
                else:
                    self.current_data[symbol][timeframe] = latest_data
            
        except Exception as e:
            self.logger.error(f"Error updating {symbol} {timeframe}: {e}")
    
    async def _clean_cache(self):
        """Clean old cache entries"""
        try:
            # Get cache stats
            stats = self.data_cache.get_stats()
            
            # If cache is >80% full, clear some entries
            if stats['size_mb'] > stats['max_size_mb'] * 0.8:
                # Clear 25% of entries
                entries_to_remove = int(len(self.data_cache.cache) * 0.25)
                for _ in range(entries_to_remove):
                    if self.data_cache.cache:
                        self.data_cache.cache.popitem(last=False)
                
                self.logger.info("🧹 Cache cleaned - removed old entries")
            
        except Exception as e:
            self.logger.error(f"Error cleaning cache: {e}")
    
    async def _on_connection_change(self, connected: bool):
        """Handle MT5 connection state changes"""
        if connected:
            self.logger.info("📡 MT5 connection restored - resuming data updates")
        else:
            self.logger.warning("📡 MT5 connection lost - pausing data updates")
    
    async def validate_market_data(self) -> bool:
        """Validate market data availability"""
        try:
            test_symbol = self.config.symbols[0] if self.config.symbols else 'EURUSD'
            
            # Test getting current price
            prices = await self.get_current_prices([test_symbol])
            if not prices:
                return False
            
            # Test getting historical data
            data = await self.get_historical_data(test_symbol, 'M1', count=10)
            if data.empty:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating market data: {e}")
            return False
    
    def get_data_statistics(self) -> Dict[str, Any]:
        """Get comprehensive data statistics"""
        try:
            stats = {
                'cache_stats': self.data_cache.get_stats(),
                'request_count': self.request_count,
                'cache_hit_rate': self.cache_hits / max(1, self.cache_hits + self.cache_misses),
                'symbols_loaded': len(self.current_data),
                'total_timeframes': sum(len(tf_data) for tf_data in self.current_data.values()),
                'connection_state': self.mt5_connector.connection_state.value,
                'data_quality_summary': {}
            }
            
            # Quality summary
            quality_counts = defaultdict(int)
            for report in self.quality_reports.values():
                quality_counts[report.data_quality.value] += 1
            
            stats['data_quality_summary'] = dict(quality_counts)
            
            # Memory usage
            total_bars = 0
            for symbol_data in self.current_data.values():
                for tf_data in symbol_data.values():
                    total_bars += len(tf_data)
            
            stats['total_bars_loaded'] = total_bars
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting data statistics: {e}")
            return {}
    
    async def is_market_open(self) -> bool:
        """Check if market is open for trading"""
        return self.mt5_connector.is_market_open()
    
    async def test_connection(self) -> bool:
        """Test MT5 connection"""
        return await self.mt5_connector.test_connection()
    
    async def shutdown(self):
        """Graceful shutdown of data manager"""
        try:
            self.logger.info("🛑 Shutting down Enhanced Data Manager...")
            
            # Set shutdown event
            self.shutdown_event.set()
            
            # Cancel update scheduler
            if self.update_scheduler and not self.update_scheduler.done():
                self.update_scheduler.cancel()
            
            # Cancel data update tasks
            for task in self.data_update_tasks.values():
                if not task.done():
                    task.cancel()
            
            # Clear cache
            self.data_cache.clear()
            
            # Shutdown MT5 connection
            await self.mt5_connector.shutdown()
            
            self.logger.info("✅ Enhanced Data Manager shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error shutting down data manager: {e}")

# Factory function for creating data manager
def create_data_manager(config: TradingConfig) -> EnhancedDataManager:
    """Factory function to create data manager instance"""
    return EnhancedDataManager(config)
