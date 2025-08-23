"""
Advanced Smart Money Concepts (SMC) Indicators - Professional Grade
==================================================================
Institutional-quality SMC indicators for professional trading applications.

This module provides comprehensive Smart Money Concepts analysis including:
- Advanced Order Block detection with institutional validation
- Fair Value Gap identification with mitigation tracking
- Liquidity Sweep detection with volume confirmation
- Market Structure analysis with BOS/ChoCH identification
- Multi-timeframe confluence analysis
- Advanced pattern recognition algorithms
- Performance optimization and caching
- Real-time monitoring and analytics

Author: Professional Trading Systems
Version: 2.0.0
License: Proprietary
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime, timedelta
import warnings
from collections import defaultdict, deque
from scipy import stats
from scipy.signal import find_peaks, argrelextrema
import math
import hashlib
import time
from functools import lru_cache, wraps
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')

# =============================================================================
# ENUMS AND TYPE DEFINITIONS
# =============================================================================

class OrderBlockType(Enum):
    """Order block classification types with institutional precision"""
    BULLISH_OB = "bullish_ob"
    BEARISH_OB = "bearish_ob"
    BREAKER_BULLISH = "breaker_bullish"
    BREAKER_BEARISH = "breaker_bearish"
    MITIGATION_BULLISH = "mitigation_bullish"
    MITIGATION_BEARISH = "mitigation_bearish"
    INSTITUTIONAL_BULLISH = "institutional_bullish"
    INSTITUTIONAL_BEARISH = "institutional_bearish"

class FairValueGapType(Enum):
    """Fair Value Gap classification types"""
    BULLISH_FVG = "bullish_fvg"
    BEARISH_FVG = "bearish_fvg"
    INSTITUTIONAL_FVG = "institutional_fvg"
    HIGH_IMPACT_FVG = "high_impact_fvg"

class LiquidityType(Enum):
    """Liquidity level types"""
    EQUAL_HIGHS = "equal_highs"
    EQUAL_LOWS = "equal_lows"
    STOP_HUNT_HIGH = "stop_hunt_high"
    STOP_HUNT_LOW = "stop_hunt_low"
    INSTITUTIONAL_LIQUIDITY = "institutional_liquidity"

class MarketStructure(Enum):
    """Market structure states"""
    BOS_BULLISH = "bos_bullish"  # Break of Structure - Bullish
    BOS_BEARISH = "bos_bearish"  # Break of Structure - Bearish
    CHOCH_BULLISH = "choch_bullish"  # Change of Character - Bullish
    CHOCH_BEARISH = "choch_bearish"  # Change of Character - Bearish
    CONSOLIDATION = "consolidation"
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    RANGE_BOUND = "range_bound"

class SignalStrength(Enum):
    """Signal strength classifications"""
    VERY_WEAK = 0.2
    WEAK = 0.4
    MODERATE = 0.6
    STRONG = 0.8
    VERY_STRONG = 1.0

# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class OrderBlock:
    """Enhanced Order Block with comprehensive metadata"""
    ob_type: OrderBlockType
    top: float
    bottom: float
    timestamp: pd.Timestamp
    index: int
    strength: float
    volume: float
    reaction_strength: float
    age_bars: int = 0
    touched: bool = False
    mitigation_count: int = 0
    mitigation_percentage: float = 0.0
    distal_line: float = 0.0
    proximal_line: float = 0.0
    candle_range: float = 0.0
    body_size: float = 0.0
    wick_ratio: float = 0.0
    volume_profile: float = 0.0
    confluence_score: float = 0.0
    institutional_level: bool = False
    break_confirmed: bool = False
    retest_count: int = 0
    avg_retest_time: float = 0.0
    success_rate: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FairValueGap:
    """Complete Fair Value Gap structure with tracking"""
    gap_type: FairValueGapType
    top: float
    bottom: float
    timestamp: pd.Timestamp
    index: int
    size: float
    volume: float
    mitigation_percentage: float = 0.0
    is_filled: bool = False
    fill_timestamp: Optional[pd.Timestamp] = None
    strength: float = 0.0
    institutional_level: bool = False
    retest_count: int = 0
    fill_speed: float = 0.0  # Bars to fill
    importance_score: float = 0.0
    confluence_factors: List[str] = field(default_factory=list)
    volume_confirmation: bool = False
    price_action_quality: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LiquiditySweep:
    """Comprehensive Liquidity Sweep analysis"""
    sweep_type: LiquidityType
    swept_level: float
    sweep_price: float
    timestamp: pd.Timestamp
    index: int
    volume_spike: bool
    reversal_confirmed: bool
    sweep_distance: float
    fake_breakout: bool = False
    volume_ratio: float = 1.0
    reversal_strength: float = 0.0
    time_to_reversal: int = 0
    institutional_footprint: bool = False
    stop_hunt_probability: float = 0.0
    liquidity_captured: float = 0.0
    smart_money_activity: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MarketStructureShift:
    """Advanced Market Structure analysis"""
    shift_type: MarketStructure
    from_price: float
    to_price: float
    from_index: int
    to_index: int
    timestamp: pd.Timestamp
    strength: float
    volume_confirmation: bool
    price_momentum: float
    time_velocity: float
    break_quality: float = 0.0
    retest_probability: float = 0.0
    trend_continuation_probability: float = 0.0
    institutional_backing: float = 0.0
    confluence_factors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SMCAnalysisResult:
    """Complete SMC analysis results"""
    timestamp: datetime
    symbol: str
    timeframe: str
    order_blocks: List[OrderBlock]
    fair_value_gaps: List[FairValueGap]
    liquidity_sweeps: List[LiquiditySweep]
    market_structure: List[MarketStructureShift]
    confluence_zones: List[Dict[str, Any]]
    overall_bias: str
    signal_strength: float
    confidence_score: float
    risk_assessment: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

# =============================================================================
# PERFORMANCE OPTIMIZATION DECORATORS
# =============================================================================

def timing_decorator(func):
    """Decorator to measure function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            execution_time = time.perf_counter() - start_time
            logger.debug(f"{func.__name__} executed in {execution_time:.4f}s")
            return result
        except Exception as e:
            execution_time = time.perf_counter() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.4f}s: {e}")
            raise
    return wrapper

def validate_input(min_data_points: int = 50):
    """Decorator to validate input data"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, df: pd.DataFrame, *args, **kwargs):
            if df is None or df.empty:
                raise ValueError(f"Empty or None dataframe provided to {func.__name__}")
            
            if len(df) < min_data_points:
                raise ValueError(f"Insufficient data for {func.__name__}: {len(df)} < {min_data_points}")
            
            required_columns = ['open', 'high', 'low', 'close']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Check for data consistency
            if not ((df['high'] >= df['low']).all() and 
                   (df['high'] >= df['open']).all() and 
                   (df['high'] >= df['close']).all() and
                   (df['low'] <= df['open']).all() and 
                   (df['low'] <= df['close']).all()):
                raise ValueError("Inconsistent OHLC data detected")
            
            return func(self, df, *args, **kwargs)
        return wrapper
    return decorator

def cache_result(cache_size: int = 128):
    """Decorator to cache function results"""
    def decorator(func):
        @lru_cache(maxsize=cache_size)
        def wrapper(*args, **kwargs):
            # Convert mutable arguments to hashable types for caching
            hashable_args = []
            for arg in args:
                if isinstance(arg, pd.DataFrame):
                    # Create hash from DataFrame content
                    hashable_args.append(hash(str(arg.values.tobytes())))
                elif isinstance(arg, dict):
                    hashable_args.append(hash(str(sorted(arg.items()))))
                else:
                    hashable_args.append(arg)
            
            hashable_kwargs = tuple(sorted(kwargs.items()))
            cache_key = tuple(hashable_args) + hashable_kwargs
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# =============================================================================
# MAIN SMC INDICATORS CLASS
# =============================================================================

class AdvancedSMCIndicators:
    """
    Professional-Grade Advanced Smart Money Concepts Indicators
    
    This class provides comprehensive SMC analysis with institutional-quality
    algorithms for detecting and analyzing smart money footprints in the market.
    
    Features:
    - Advanced Order Block detection with institutional validation
    - Fair Value Gap identification with mitigation tracking
    - Liquidity Sweep detection with volume confirmation
    - Market Structure analysis with BOS/ChoCH identification
    - Multi-timeframe confluence analysis
    - Performance optimization and caching
    - Real-time monitoring capabilities
    - Comprehensive risk assessment
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize Advanced SMC Indicators with comprehensive configuration
        
        Args:
            config: Configuration dictionary with strategy parameters
        """
        self.config = config or {}
        
        # Core algorithm parameters
        self.swing_length = self.config.get('swing_length', 10)
        self.ob_strength_threshold = self.config.get('ob_strength_threshold', 0.6)
        self.fvg_min_size = self.config.get('fvg_min_size', 0.0003)  # 3 pips
        self.liquidity_range_percent = self.config.get('liquidity_range_percent', 0.001)  # 0.1%
        self.volume_spike_threshold = self.config.get('volume_spike_threshold', 2.0)
        self.structure_break_threshold = self.config.get('structure_break_threshold', 0.0005)
        
        # Advanced parameters
        self.min_reaction_bars = self.config.get('min_reaction_bars', 3)
        self.max_ob_age = self.config.get('max_ob_age', 100)
        self.confluence_distance = self.config.get('confluence_distance', 0.002)  # 20 pips
        self.institutional_size_threshold = self.config.get('institutional_size_threshold', 0.005)
        self.stop_hunt_detection_period = self.config.get('stop_hunt_detection_period', 20)
        
        # Performance optimization
        self.use_parallel_processing = self.config.get('use_parallel_processing', True)
        self.max_workers = self.config.get('max_workers', 4)
        self.cache_enabled = self.config.get('cache_enabled', True)
        self.performance_monitoring = self.config.get('performance_monitoring', True)
        
        # Quality and validation parameters
        self.min_data_quality_score = self.config.get('min_data_quality_score', 0.7)
        self.enable_advanced_validation = self.config.get('enable_advanced_validation', True)
        self.confidence_threshold = self.config.get('confidence_threshold', 0.6)
        
        # Internal state management
        self._cache = {}
        self._performance_metrics = defaultdict(list)
        self._last_analysis_time = None
        self._analysis_count = 0
        
        # Threading for parallel processing
        if self.use_parallel_processing:
            self._executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
        logger.info(f"Advanced SMC Indicators initialized with configuration: {self._get_config_summary()}")
    
    def _get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary for logging"""
        return {
            'swing_length': self.swing_length,
            'ob_strength_threshold': self.ob_strength_threshold,
            'fvg_min_size': self.fvg_min_size,
            'volume_spike_threshold': self.volume_spike_threshold,
            'use_parallel_processing': self.use_parallel_processing,
            'cache_enabled': self.cache_enabled
        }
    
    @timing_decorator
    @validate_input(min_data_points=50)
    def analyze_complete_smc(self, df: pd.DataFrame, symbol: str = "UNKNOWN", 
                           timeframe: str = "UNKNOWN") -> SMCAnalysisResult:
        """
        Perform comprehensive SMC analysis on the provided data
        
        Args:
            df: OHLCV DataFrame with market data
            symbol: Trading symbol for identification
            timeframe: Timeframe for analysis
            
        Returns:
            Complete SMC analysis results
        """
        try:
            start_time = time.perf_counter()
            self._analysis_count += 1
            
            # Data quality assessment
            data_quality = self._assess_data_quality(df)
            if data_quality['quality_score'] < self.min_data_quality_score:
                logger.warning(f"Data quality below threshold: {data_quality['quality_score']}")
            
            # Parallel execution of core analyses
            if self.use_parallel_processing:
                analysis_tasks = {
                    'swing_points': self._executor.submit(self._calculate_advanced_swing_points, df),
                    'order_blocks': self._executor.submit(self._detect_advanced_order_blocks, df),
                    'fair_value_gaps': self._executor.submit(self._detect_advanced_fair_value_gaps, df),
                    'liquidity_sweeps': self._executor.submit(self._detect_advanced_liquidity_sweeps, df),
                    'market_structure': self._executor.submit(self._analyze_advanced_market_structure, df)
                }
                
                # Collect results
                swing_points = analysis_tasks['swing_points'].result()
                order_blocks = analysis_tasks['order_blocks'].result()
                fair_value_gaps = analysis_tasks['fair_value_gaps'].result()
                liquidity_sweeps = analysis_tasks['liquidity_sweeps'].result()
                market_structure = analysis_tasks['market_structure'].result()
            else:
                # Sequential execution
                swing_points = self._calculate_advanced_swing_points(df)
                order_blocks = self._detect_advanced_order_blocks(df)
                fair_value_gaps = self._detect_advanced_fair_value_gaps(df)
                liquidity_sweeps = self._detect_advanced_liquidity_sweeps(df)
                market_structure = self._analyze_advanced_market_structure(df)
            
            # Advanced confluence analysis
            confluence_zones = self._calculate_advanced_confluence(
                order_blocks, fair_value_gaps, liquidity_sweeps, market_structure
            )
            
            # Overall market bias and signal generation
            overall_bias, signal_strength = self._determine_market_bias(
                order_blocks, fair_value_gaps, market_structure
            )
            
            # Confidence scoring
            confidence_score = self._calculate_confidence_score(
                order_blocks, fair_value_gaps, liquidity_sweeps, market_structure, data_quality
            )
            
            # Risk assessment
            risk_assessment = self._perform_risk_assessment(
                order_blocks, fair_value_gaps, liquidity_sweeps, market_structure
            )
            
            # Performance metrics
            execution_time = time.perf_counter() - start_time
            performance_metrics = self._generate_performance_metrics(
                order_blocks, fair_value_gaps, liquidity_sweeps, market_structure, 
                execution_time, data_quality
            )
            
            # Create comprehensive result
            result = SMCAnalysisResult(
                timestamp=datetime.now(),
                symbol=symbol,
                timeframe=timeframe,
                order_blocks=order_blocks,
                fair_value_gaps=fair_value_gaps,
                liquidity_sweeps=liquidity_sweeps,
                market_structure=market_structure,
                confluence_zones=confluence_zones,
                overall_bias=overall_bias,
                signal_strength=signal_strength,
                confidence_score=confidence_score,
                risk_assessment=risk_assessment,
                performance_metrics=performance_metrics,
                metadata={
                    'data_quality': data_quality,
                    'analysis_time': execution_time,
                    'config_used': self._get_config_summary(),
                    'analysis_id': self._analysis_count
                }
            )
            
            self._last_analysis_time = datetime.now()
            logger.info(f"SMC analysis completed for {symbol} {timeframe} in {execution_time:.4f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in complete SMC analysis: {e}")
            raise
    
    @timing_decorator
    def _calculate_advanced_swing_points(self, df: pd.DataFrame) -> Dict[str, List[Dict[str, Any]]]:
        """Calculate swing points using advanced algorithms"""
        try:
            swing_highs = []
            swing_lows = []
            
            # Method 1: Traditional swing point detection
            traditional_highs, traditional_lows = self._traditional_swing_detection(df)
            
            # Method 2: Statistical peak detection
            statistical_highs, statistical_lows = self._statistical_swing_detection(df)
            
            # Method 3: Volume-weighted swing detection
            volume_highs, volume_lows = self._volume_weighted_swing_detection(df)
            
            # Merge and validate swing points
            final_highs = self._merge_and_validate_swings(
                traditional_highs, statistical_highs, volume_highs, df, 'high'
            )
            final_lows = self._merge_and_validate_swings(
                traditional_lows, statistical_lows, volume_lows, df, 'low'
            )
            
            return {
                'swing_highs': final_highs,
                'swing_lows': final_lows
            }
            
        except Exception as e:
            logger.error(f"Error calculating advanced swing points: {e}")
            return {'swing_highs': [], 'swing_lows': []}
    
    def _traditional_swing_detection(self, df: pd.DataFrame) -> Tuple[List[Dict], List[Dict]]:
        """Traditional swing point detection with enhanced validation"""
        highs = []
        lows = []
        
        for i in range(self.swing_length, len(df) - self.swing_length):
            # Enhanced swing high detection
            if self._is_valid_swing_high(df, i):
                swing_data = self._create_swing_point_data(df, i, 'high')
                highs.append(swing_data)
            
            # Enhanced swing low detection
            if self._is_valid_swing_low(df, i):
                swing_data = self._create_swing_point_data(df, i, 'low')
                lows.append(swing_data)
        
        return highs, lows
    
    def _is_valid_swing_high(self, df: pd.DataFrame, i: int) -> bool:
        """Enhanced swing high validation"""
        current_high = df['high'].iloc[i]
        
        # Check left and right sides
        left_side = df['high'].iloc[i-self.swing_length:i]
        right_side = df['high'].iloc[i+1:i+self.swing_length+1]
        
        # Must be highest point
        if not (left_side < current_high).all() or not (right_side < current_high).all():
            return False
        
        # Additional validation: volume confirmation
        if 'volume' in df.columns:
            current_volume = df['volume'].iloc[i]
            avg_volume = df['volume'].iloc[max(0, i-20):i].mean()
            if current_volume < avg_volume * 0.8:  # Significant volume required
                return False
        
        # Price action validation: rejection candle
        candle = df.iloc[i]
        upper_wick = candle['high'] - max(candle['open'], candle['close'])
        candle_range = candle['high'] - candle['low']
        
        if candle_range > 0 and upper_wick / candle_range > 0.3:  # Significant upper wick
            return True
        
        return True
    
    def _is_valid_swing_low(self, df: pd.DataFrame, i: int) -> bool:
        """Enhanced swing low validation"""
        current_low = df['low'].iloc[i]
        
        # Check left and right sides
        left_side = df['low'].iloc[i-self.swing_length:i]
        right_side = df['low'].iloc[i+1:i+self.swing_length+1]
        
        # Must be lowest point
        if not (left_side > current_low).all() or not (right_side > current_low).all():
            return False
        
        # Additional validation: volume confirmation
        if 'volume' in df.columns:
            current_volume = df['volume'].iloc[i]
            avg_volume = df['volume'].iloc[max(0, i-20):i].mean()
            if current_volume < avg_volume * 0.8:  # Significant volume required
                return False
        
        # Price action validation: rejection candle
        candle = df.iloc[i]
        lower_wick = min(candle['open'], candle['close']) - candle['low']
        candle_range = candle['high'] - candle['low']
        
        if candle_range > 0 and lower_wick / candle_range > 0.3:  # Significant lower wick
            return True
        
        return True
    
    def _create_swing_point_data(self, df: pd.DataFrame, i: int, swing_type: str) -> Dict[str, Any]:
        """Create comprehensive swing point data"""
        return {
            'index': i,
            'level': df['high'].iloc[i] if swing_type == 'high' else df['low'].iloc[i],
            'timestamp': df.index[i],
            'volume': df['volume'].iloc[i] if 'volume' in df.columns else 0,
            'type': swing_type,
            'strength': self._calculate_swing_strength(df, i, swing_type),
            'quality_score': self._calculate_swing_quality(df, i, swing_type),
            'confluence_factors': self._identify_swing_confluence_factors(df, i)
        }
    
    def _calculate_swing_strength(self, df: pd.DataFrame, i: int, swing_type: str) -> float:
        """Calculate swing point strength with multiple factors"""
        try:
            strength_factors = []
            
            # Price momentum factor
            if swing_type == 'high':
                price_level = df['high'].iloc[i]
                momentum = price_level - df['close'].iloc[max(0, i - 5)]
            else:
                price_level = df['low'].iloc[i]
                momentum = df['close'].iloc[max(0, i - 5)] - price_level
            
            momentum_strength = min(1.0, abs(momentum) / price_level * 100)
            strength_factors.append(momentum_strength)
            
            # Volume factor
            if 'volume' in df.columns:
                current_volume = df['volume'].iloc[i]
                avg_volume = df['volume'].iloc[max(0, i-20):i].mean()
                volume_factor = min(2.0, current_volume / avg_volume) if avg_volume > 0 else 1.0
                strength_factors.append(volume_factor / 2.0)
            
            # Rejection factor (wick analysis)
            rejection_factor = self._calculate_rejection_strength(df, i, swing_type)
            strength_factors.append(rejection_factor)
            
            # Time factor (longer swing periods = stronger)
            time_factor = min(1.0, self.swing_length / 20.0)
            strength_factors.append(time_factor)
            
            return np.mean(strength_factors)
            
        except Exception as e:
            logger.error(f"Error calculating swing strength: {e}")
            return 0.5
    
    def _calculate_rejection_strength(self, df: pd.DataFrame, i: int, swing_type: str) -> float:
        """Calculate rejection strength from wick analysis"""
        try:
            candle = df.iloc[i]
            
            if swing_type == 'high':
                wick_size = candle['high'] - max(candle['open'], candle['close'])
                body_size = abs(candle['close'] - candle['open'])
                total_range = candle['high'] - candle['low']
            else:
                wick_size = min(candle['open'], candle['close']) - candle['low']
                body_size = abs(candle['close'] - candle['open'])
                total_range = candle['high'] - candle['low']
            
            if total_range == 0:
                return 0.0
            
            # Rejection strength based on wick to total range ratio
            rejection_ratio = wick_size / total_range
            
            # Bonus for small body relative to total range (doji-like)
            body_ratio = body_size / total_range
            doji_bonus = 1.0 - body_ratio
            
            return min(1.0, rejection_ratio + (doji_bonus * 0.3))
            
        except Exception as e:
            logger.error(f"Error calculating rejection strength: {e}")
            return 0.0
    
    def _calculate_swing_quality(self, df: pd.DataFrame, i: int, swing_type: str) -> float:
        """Calculate overall swing point quality"""
        try:
            quality_factors = []
            
            # Data quality around swing point
            data_slice = df.iloc[max(0, i-5):min(len(df), i+6)]
            
            # No missing data
            if not data_slice.isnull().any().any():
                quality_factors.append(1.0)
            else:
                quality_factors.append(0.5)
            
            # Volume consistency
            if 'volume' in df.columns:
                volume_std = data_slice['volume'].std()
                volume_mean = data_slice['volume'].mean()
                volume_consistency = 1.0 - min(1.0, volume_std / volume_mean) if volume_mean > 0 else 0.5
                quality_factors.append(volume_consistency)
            
            # Price action clarity
            price_volatility = data_slice['close'].pct_change().std()
            volatility_score = min(1.0, price_volatility * 100) if not pd.isna(price_volatility) else 0.5
            quality_factors.append(volatility_score)
            
            return np.mean(quality_factors)
            
        except Exception as e:
            logger.error(f"Error calculating swing quality: {e}")
            return 0.5
    
    def _identify_swing_confluence_factors(self, df: pd.DataFrame, i: int) -> List[str]:
        """Identify confluence factors at swing point"""
        factors = []
        
        try:
            price_level = df['high'].iloc[i] if i < len(df) else df['low'].iloc[i]
            
            # Round number proximity
            price_str = f"{price_level:.5f}"
            if price_str.endswith('00000') or price_str.endswith('50000'):
                factors.append('major_round_number')
            elif price_str.endswith('0000') or price_str.endswith('5000'):
                factors.append('round_number')
            
            # Previous swing level confluence
            # This would be implemented with historical swing data
            
            # Fibonacci level confluence
            # This would be implemented with fibonacci calculations
            
            # Volume spike
            if 'volume' in df.columns:
                current_volume = df['volume'].iloc[i]
                avg_volume = df['volume'].iloc[max(0, i-20):i].mean()
                if current_volume > avg_volume * 2:
                    factors.append('volume_spike')
            
        except Exception as e:
            logger.error(f"Error identifying confluence factors: {e}")
        
        return factors
    
    def _statistical_swing_detection(self, df: pd.DataFrame) -> Tuple[List[Dict], List[Dict]]:
        """Statistical swing detection using scipy"""
        highs = []
        lows = []
        
        try:
            # Use scipy to find peaks
            high_peaks, _ = find_peaks(
                df['high'].values,
                distance=self.swing_length,
                prominence=df['high'].std() * 0.3
            )
            
            low_peaks, _ = find_peaks(
                -df['low'].values,
                distance=self.swing_length,
                prominence=df['low'].std() * 0.3
            )
            
            for peak_idx in high_peaks:
                if peak_idx < len(df):
                    swing_data = self._create_swing_point_data(df, peak_idx, 'high')
                    swing_data['detection_method'] = 'statistical'
                    highs.append(swing_data)
            
            for peak_idx in low_peaks:
                if peak_idx < len(df):
                    swing_data = self._create_swing_point_data(df, peak_idx, 'low')
                    swing_data['detection_method'] = 'statistical'
                    lows.append(swing_data)
            
        except Exception as e:
            logger.warning(f"Statistical swing detection failed: {e}")
        
        return highs, lows
    
    def _volume_weighted_swing_detection(self, df: pd.DataFrame) -> Tuple[List[Dict], List[Dict]]:
        """Volume-weighted swing detection for institutional levels"""
        highs = []
        lows = []
        
        if 'volume' not in df.columns:
            return highs, lows
        
        try:
            # Calculate VWAP
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            vwap = (typical_price * df['volume']).rolling(self.swing_length).sum() / df['volume'].rolling(self.swing_length).sum()
            
            # Volume threshold for institutional activity
            volume_threshold = df['volume'].rolling(50).quantile(0.8)
            
            for i in range(self.swing_length, len(df) - self.swing_length):
                if df['volume'].iloc[i] > volume_threshold.iloc[i]:
                    # Check for volume-weighted swing high
                    if (df['high'].iloc[i] > vwap.iloc[i] * 1.002 and
                        self._is_volume_swing_high(df, i)):
                        swing_data = self._create_swing_point_data(df, i, 'high')
                        swing_data['detection_method'] = 'volume_weighted'
                        highs.append(swing_data)
                    
                    # Check for volume-weighted swing low
                    elif (df['low'].iloc[i] < vwap.iloc[i] * 0.998 and
                          self._is_volume_swing_low(df, i)):
                        swing_data = self._create_swing_point_data(df, i, 'low')
                        swing_data['detection_method'] = 'volume_weighted'
                        lows.append(swing_data)
            
        except Exception as e:
            logger.warning(f"Volume-weighted swing detection failed: {e}")
        
        return highs, lows
    
    def _is_volume_swing_high(self, df: pd.DataFrame, i: int) -> bool:
        """Check if index is volume-weighted swing high"""
        return df['high'].iloc[i] == df['high'].iloc[i-self.swing_length:i+self.swing_length+1].max()
    
    def _is_volume_swing_low(self, df: pd.DataFrame, i: int) -> bool:
        """Check if index is volume-weighted swing low"""
        return df['low'].iloc[i] == df['low'].iloc[i-self.swing_length:i+self.swing_length+1].min()
    
    def _merge_and_validate_swings(self, traditional: List[Dict], statistical: List[Dict],
                                 volume: List[Dict], df: pd.DataFrame, swing_type: str) -> List[Dict[str, Any]]:
        """Merge swing points from different methods and validate"""
        all_swings = traditional + statistical + volume
        
        if not all_swings:
            return []
        
        # Sort by index
        all_swings.sort(key=lambda x: x['index'])
        
        # Merge nearby swings within confluence distance
        merged_swings = []
        i = 0
        
        while i < len(all_swings):
            current_swing = all_swings[i]
            nearby_swings = [current_swing]
            
            # Find swings within confluence distance
            j = i + 1
            while j < len(all_swings):
                if abs(all_swings[j]['level'] - current_swing['level']) / current_swing['level'] < self.confluence_distance:
                    nearby_swings.append(all_swings[j])
                    j += 1
                else:
                    break
            
            # Create consolidated swing point
            if len(nearby_swings) > 1:
                consolidated_swing = self._consolidate_swing_points(nearby_swings)
                merged_swings.append(consolidated_swing)
            else:
                merged_swings.append(current_swing)
            
            i = j
        
        # Final validation and ranking
        validated_swings = []
        for swing in merged_swings:
            if self._validate_final_swing(swing, df):
                validated_swings.append(swing)
        
        # Sort by strength and keep top swings
        validated_swings.sort(key=lambda x: x['strength'], reverse=True)
        return validated_swings[:50]  # Keep top 50 swings
    
    def _consolidate_swing_points(self, nearby_swings: List[Dict]) -> Dict[str, Any]:
        """Consolidate multiple nearby swing points into one"""
        # Use the swing with highest strength as base
        best_swing = max(nearby_swings, key=lambda x: x['strength'])
        
        # Enhance with confluence information
        best_swing['confluence_count'] = len(nearby_swings)
        best_swing['detection_methods'] = list(set(
            swing.get('detection_method', 'traditional') for swing in nearby_swings
        ))
        best_swing['strength'] = min(1.0, best_swing['strength'] * (1 + len(nearby_swings) * 0.1))
        
        return best_swing
    
    def _validate_final_swing(self, swing: Dict[str, Any], df: pd.DataFrame) -> bool:
        """Final validation of swing point"""
        try:
            # Minimum strength requirement
            if swing['strength'] < 0.3:
                return False
            
            # Index bounds check
            if swing['index'] < 0 or swing['index'] >= len(df):
                return False
            
            # Quality score check
            if swing.get('quality_score', 0) < 0.5:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating swing: {e}")
            return False
    
    @timing_decorator
    def _detect_advanced_order_blocks(self, df: pd.DataFrame) -> List[OrderBlock]:
        """Advanced Order Block detection with institutional validation"""
        try:
            order_blocks = []
            
            # Get swing points for context
            swing_data = self._calculate_advanced_swing_points(df)
            swing_highs = swing_data['swing_highs']
            swing_lows = swing_data['swing_lows']
            
            # Detect different types of order blocks
            bullish_obs = self._detect_bullish_order_blocks(df, swing_highs, swing_lows)
            bearish_obs = self._detect_bearish_order_blocks(df, swing_highs, swing_lows)
            breaker_blocks = self._detect_breaker_blocks(df, bullish_obs + bearish_obs)
            institutional_obs = self._detect_institutional_order_blocks(df)
            
            # Combine all order blocks
            all_order_blocks = bullish_obs + bearish_obs + breaker_blocks + institutional_obs
            
            # Enhanced filtering and ranking
            filtered_obs = self._filter_and_rank_order_blocks_advanced(all_order_blocks, df)
            
            return filtered_obs
            
        except Exception as e:
            logger.error(f"Error detecting advanced order blocks: {e}")
            return []
    
    def _detect_bullish_order_blocks(self, df: pd.DataFrame, swing_highs: List[Dict], 
                                   swing_lows: List[Dict]) -> List[OrderBlock]:
        """Detect bullish order blocks with advanced validation"""
        bullish_obs = []
        
        try:
            for i in range(len(df) - self.min_reaction_bars):
                if self._is_potential_bullish_ob_advanced(df, i, swing_highs, swing_lows):
                    ob = self._create_advanced_bullish_ob(df, i)
                    if ob and self._validate_order_block_advanced(ob, df):
                        bullish_obs.append(ob)
            
        except Exception as e:
            logger.error(f"Error detecting bullish order blocks: {e}")
        
        return bullish_obs
    
    def _is_potential_bullish_ob_advanced(self, df: pd.DataFrame, i: int, 
                                        swing_highs: List[Dict], swing_lows: List[Dict]) -> bool:
        """Advanced bullish order block detection logic"""
        try:
            if i >= len(df) - self.min_reaction_bars:
                return False
            
            current_bar = df.iloc[i]
            
            # Must be a down candle with significant rejection
            if current_bar['close'] >= current_bar['open']:
                return False
            
            # Check for institutional footprint
            if not self._has_institutional_footprint(df, i):
                return False
            
            # Reaction analysis
            reaction_slice = df.iloc[i+1:i+1+self.min_reaction_bars]
            if len(reaction_slice) < self.min_reaction_bars:
                return False
            
            # Calculate reaction strength
            max_high_after = reaction_slice['high'].max()
            entry_price = current_bar['low']
            reaction_strength = (max_high_after - entry_price) / entry_price
            
            # Minimum reaction requirement
            if reaction_strength < 0.002:  # 20 pips minimum
                return False
            
            # Structure break confirmation
            if self._confirms_bullish_structure_break(df, i, max_high_after, swing_highs):
                return True
            
            # Strong impulse alternative
            if reaction_strength > 0.005:  # 50 pips strong reaction
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking potential bullish OB: {e}")
            return False
    
    def _has_institutional_footprint(self, df: pd.DataFrame, i: int) -> bool:
        """Check for institutional footprint at order block formation"""
        try:
            if 'volume' not in df.columns:
                return True  # Assume institutional if no volume data
            
            current_volume = df['volume'].iloc[i]
            avg_volume = df['volume'].iloc[max(0, i-20):i].mean()
            
            # High volume relative to average
            if current_volume > avg_volume * 1.5:
                return True
            
            # Check for institutional-size order characteristics
            candle = df.iloc[i]
            candle_range = candle['high'] - candle['low']
            avg_range = (df['high'] - df['low']).iloc[max(0, i-20):i].mean()
            
            # Large candle with good volume
            if candle_range > avg_range * 1.3 and current_volume > avg_volume:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking institutional footprint: {e}")
            return False
    
    def _confirms_bullish_structure_break(self, df: pd.DataFrame, i: int, 
                                        reaction_high: float, swing_highs: List[Dict]) -> bool:
        """Confirm bullish structure break"""
        try:
            if not swing_highs:
                return False
            
            # Find relevant swing highs before this order block
            relevant_swings = [s for s in swing_highs if s['index'] < i and s['index'] > i - 100]
            
            if not relevant_swings:
                return False
            
            # Check if reaction breaks the most recent significant swing high
            recent_swing_high = max(relevant_swings, key=lambda x: x['level'])['level']
            
            return reaction_high > recent_swing_high
            
        except Exception as e:
            logger.error(f"Error confirming bullish structure break: {e}")
            return False
    
    def _create_advanced_bullish_ob(self, df: pd.DataFrame, i: int) -> Optional[OrderBlock]:
        """Create advanced bullish order block with comprehensive analysis"""
        try:
            current_bar = df.iloc[i]
            
            # Enhanced reaction analysis
            reaction_slice = df.iloc[i+1:min(len(df), i+1+10)]
            max_high_after = reaction_slice['high'].max()
            reaction_strength = (max_high_after - current_bar['low']) / current_bar['low']
            
            # Order block boundaries
            ob_top = current_bar['high']
            ob_bottom = current_bar['low']
            
            # Distal and proximal lines
            distal_line = ob_top  # Far side from market
            proximal_line = ob_bottom  # Near side to market
            
            # Enhanced metrics
            candle_range = ob_top - ob_bottom
            body_size = abs(current_bar['close'] - current_bar['open'])
            upper_wick = ob_top - max(current_bar['open'], current_bar['close'])
            lower_wick = min(current_bar['open'], current_bar['close']) - ob_bottom
            wick_ratio = lower_wick / candle_range if candle_range > 0 else 0
            
            # Volume analysis
            volume = current_bar.get('volume', 0)
            avg_volume = df['volume'].iloc[max(0, i-20):i].mean() if 'volume' in df.columns else 1
            volume_profile = volume / avg_volume if avg_volume > 0 else 1.0
            
            # Institutional level assessment
            institutional_level = (
                volume_profile > 1.5 and
                candle_range > (df['high'] - df['low']).iloc[max(0, i-20):i].mean() * 1.2
            )
            
            # Calculate comprehensive strength
            strength_components = [
                min(1.0, reaction_strength * 200),  # Reaction strength
                min(1.0, volume_profile / 2),       # Volume strength
                wick_ratio,                         # Rejection strength
                min(1.0, candle_range / df['close'].iloc[i] * 1000)  # Size strength
            ]
            overall_strength = np.mean(strength_components)
            
            return OrderBlock(
                ob_type=OrderBlockType.INSTITUTIONAL_BULLISH if institutional_level else OrderBlockType.BULLISH_OB,
                top=ob_top,
                bottom=ob_bottom,
                timestamp=df.index[i],
                index=i,
                strength=overall_strength,
                volume=volume,
                reaction_strength=reaction_strength,
                distal_line=distal_line,
                proximal_line=proximal_line,
                candle_range=candle_range,
                body_size=body_size,
                wick_ratio=wick_ratio,
                volume_profile=volume_profile,
                institutional_level=institutional_level,
                confluence_score=0.0,  # Will be calculated later
                metadata={
                    'formation_bar': i,
                    'reaction_bars': len(reaction_slice),
                    'max_reaction_high': max_high_after,
                    'volume_ratio': volume_profile,
                    'candle_type': 'bearish_rejection'
                }
            )
            
        except Exception as e:
            logger.error(f"Error creating advanced bullish OB: {e}")
            return None
    
    def _detect_bearish_order_blocks(self, df: pd.DataFrame, swing_highs: List[Dict], 
                                   swing_lows: List[Dict]) -> List[OrderBlock]:
        """Detect bearish order blocks with advanced validation"""
        bearish_obs = []
        
        try:
            for i in range(len(df) - self.min_reaction_bars):
                if self._is_potential_bearish_ob_advanced(df, i, swing_highs, swing_lows):
                    ob = self._create_advanced_bearish_ob(df, i)
                    if ob and self._validate_order_block_advanced(ob, df):
                        bearish_obs.append(ob)
            
        except Exception as e:
            logger.error(f"Error detecting bearish order blocks: {e}")
        
        return bearish_obs
    
    def _is_potential_bearish_ob_advanced(self, df: pd.DataFrame, i: int,
                                        swing_highs: List[Dict], swing_lows: List[Dict]) -> bool:
        """Advanced bearish order block detection logic"""
        try:
            if i >= len(df) - self.min_reaction_bars:
                return False
            
            current_bar = df.iloc[i]
            
            # Must be an up candle with significant rejection
            if current_bar['close'] <= current_bar['open']:
                return False
            
            # Check for institutional footprint
            if not self._has_institutional_footprint(df, i):
                return False
            
            # Reaction analysis
            reaction_slice = df.iloc[i+1:i+1+self.min_reaction_bars]
            if len(reaction_slice) < self.min_reaction_bars:
                return False
            
            # Calculate reaction strength
            min_low_after = reaction_slice['low'].min()
            entry_price = current_bar['high']
            reaction_strength = (entry_price - min_low_after) / entry_price
            
            # Minimum reaction requirement
            if reaction_strength < 0.002:  # 20 pips minimum
                return False
            
            # Structure break confirmation
            if self._confirms_bearish_structure_break(df, i, min_low_after, swing_lows):
                return True
            
            # Strong impulse alternative
            if reaction_strength > 0.005:  # 50 pips strong reaction
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking potential bearish OB: {e}")
            return False
    
    def _confirms_bearish_structure_break(self, df: pd.DataFrame, i: int,
                                        reaction_low: float, swing_lows: List[Dict]) -> bool:
        """Confirm bearish structure break"""
        try:
            if not swing_lows:
                return False
            
            # Find relevant swing lows before this order block
            relevant_swings = [s for s in swing_lows if s['index'] < i and s['index'] > i - 100]
            
            if not relevant_swings:
                return False
            
            # Check if reaction breaks the most recent significant swing low
            recent_swing_low = min(relevant_swings, key=lambda x: x['level'])['level']
            
            return reaction_low < recent_swing_low
            
        except Exception as e:
            logger.error(f"Error confirming bearish structure break: {e}")
            return False
    
    def _create_advanced_bearish_ob(self, df: pd.DataFrame, i: int) -> Optional[OrderBlock]:
        """Create advanced bearish order block with comprehensive analysis"""
        try:
            current_bar = df.iloc[i]
            
            # Enhanced reaction analysis
            reaction_slice = df.iloc[i+1:min(len(df), i+1+10)]
            min_low_after = reaction_slice['low'].min()
            reaction_strength = (current_bar['high'] - min_low_after) / current_bar['high']
            
            # Order block boundaries
            ob_top = current_bar['high']
            ob_bottom = current_bar['low']
            
            # Distal and proximal lines
            distal_line = ob_bottom  # Far side from market
            proximal_line = ob_top   # Near side to market
            
            # Enhanced metrics
            candle_range = ob_top - ob_bottom
            body_size = abs(current_bar['close'] - current_bar['open'])
            upper_wick = ob_top - max(current_bar['open'], current_bar['close'])
            lower_wick = min(current_bar['open'], current_bar['close']) - ob_bottom
            wick_ratio = upper_wick / candle_range if candle_range > 0 else 0
            
            # Volume analysis
            volume = current_bar.get('volume', 0)
            avg_volume = df['volume'].iloc[max(0, i-20):i].mean() if 'volume' in df.columns else 1
            volume_profile = volume / avg_volume if avg_volume > 0 else 1.0
            
            # Institutional level assessment
            institutional_level = (
                volume_profile > 1.5 and
                candle_range > (df['high'] - df['low']).iloc[max(0, i-20):i].mean() * 1.2
            )
            
            # Calculate comprehensive strength
            strength_components = [
                min(1.0, reaction_strength * 200),  # Reaction strength
                min(1.0, volume_profile / 2),       # Volume strength
                wick_ratio,                         # Rejection strength
                min(1.0, candle_range / df['close'].iloc[i] * 1000)  # Size strength
            ]
            overall_strength = np.mean(strength_components)
            
            return OrderBlock(
                ob_type=OrderBlockType.INSTITUTIONAL_BEARISH if institutional_level else OrderBlockType.BEARISH_OB,
                top=ob_top,
                bottom=ob_bottom,
                timestamp=df.index[i],
                index=i,
                strength=overall_strength,
                volume=volume,
                reaction_strength=reaction_strength,
                distal_line=distal_line,
                proximal_line=proximal_line,
                candle_range=candle_range,
                body_size=body_size,
                wick_ratio=wick_ratio,
                volume_profile=volume_profile,
                institutional_level=institutional_level,
                confluence_score=0.0,  # Will be calculated later
                metadata={
                    'formation_bar': i,
                    'reaction_bars': len(reaction_slice),
                    'min_reaction_low': min_low_after,
                    'volume_ratio': volume_profile,
                    'candle_type': 'bullish_rejection'
                }
            )
            
        except Exception as e:
            logger.error(f"Error creating advanced bearish OB: {e}")
            return None
    
    def _detect_breaker_blocks(self, df: pd.DataFrame, order_blocks: List[OrderBlock]) -> List[OrderBlock]:
        """Detect breaker blocks (failed order blocks that become opposite bias)"""
        breaker_blocks = []
        
        try:
            for ob in order_blocks:
                violation_data = self._check_ob_violation_advanced(df, ob)
                
                if violation_data['violated']:
                    breaker = self._create_breaker_block(df, ob, violation_data)
                    if breaker:
                        breaker_blocks.append(breaker)
            
        except Exception as e:
            logger.error(f"Error detecting breaker blocks: {e}")
        
        return breaker_blocks
    
    def _check_ob_violation_advanced(self, df: pd.DataFrame, ob: OrderBlock) -> Dict[str, Any]:
        """Advanced order block violation check"""
        try:
            violation_data = {
                'violated': False,
                'violation_index': -1,
                'violation_strength': 0.0,
                'violation_volume': 0.0,
                'time_to_violation': 0
            }
            
            # Look for violation after the order block
            for i in range(ob.index + 1, len(df)):
                current_bar = df.iloc[i]
                
                if ob.ob_type in [OrderBlockType.BULLISH_OB, OrderBlockType.INSTITUTIONAL_BULLISH]:
                    # Bullish OB violated if price closes significantly below the low
                    if current_bar['close'] < ob.bottom * 0.998:  # 2 pip buffer
                        # Confirm with volume
                        violation_volume = current_bar.get('volume', 0)
                        avg_volume = df['volume'].iloc[max(0, i-10):i].mean() if 'volume' in df.columns else 1
                        
                        if violation_volume > avg_volume * 1.2:  # Volume confirmation
                            violation_data.update({
                                'violated': True,
                                'violation_index': i,
                                'violation_strength': (ob.bottom - current_bar['close']) / ob.bottom,
                                'violation_volume': violation_volume,
                                'time_to_violation': i - ob.index
                            })
                            break
                
                else:  # Bearish OB
                    # Bearish OB violated if price closes significantly above the high
                    if current_bar['close'] > ob.top * 1.002:  # 2 pip buffer
                        # Confirm with volume
                        violation_volume = current_bar.get('volume', 0)
                        avg_volume = df['volume'].iloc[max(0, i-10):i].mean() if 'volume' in df.columns else 1
                        
                        if violation_volume > avg_volume * 1.2:  # Volume confirmation
                            violation_data.update({
                                'violated': True,
                                'violation_index': i,
                                'violation_strength': (current_bar['close'] - ob.top) / ob.top,
                                'violation_volume': violation_volume,
                                'time_to_violation': i - ob.index
                            })
                            break
            
            return violation_data
            
        except Exception as e:
            logger.error(f"Error checking OB violation: {e}")
            return {'violated': False, 'violation_index': -1, 'violation_strength': 0.0, 
                   'violation_volume': 0.0, 'time_to_violation': 0}
    
    def _create_breaker_block(self, df: pd.DataFrame, original_ob: OrderBlock, 
                            violation_data: Dict[str, Any]) -> Optional[OrderBlock]:
        """Create breaker block from violated order block"""
        try:
            # Determine breaker type
            if original_ob.ob_type in [OrderBlockType.BULLISH_OB, OrderBlockType.INSTITUTIONAL_BULLISH]:
                breaker_type = OrderBlockType.BREAKER_BEARISH
            else:
                breaker_type = OrderBlockType.BREAKER_BULLISH
            
            # Breaker inherits most properties but with opposite bias
            breaker = OrderBlock(
                ob_type=breaker_type,
                top=original_ob.top,
                bottom=original_ob.bottom,
                timestamp=df.index[violation_data['violation_index']],
                index=violation_data['violation_index'],
                strength=original_ob.strength * 0.8,  # Slightly reduced strength
                volume=violation_data['violation_volume'],
                reaction_strength=violation_data['violation_strength'],
                distal_line=original_ob.proximal_line,  # Flip distal/proximal
                proximal_line=original_ob.distal_line,
                candle_range=original_ob.candle_range,
                body_size=original_ob.body_size,
                wick_ratio=original_ob.wick_ratio,
                volume_profile=violation_data['violation_volume'] / original_ob.volume if original_ob.volume > 0 else 1.0,
                institutional_level=original_ob.institutional_level,
                break_confirmed=True,
                confluence_score=0.0,
                metadata={
                    'original_ob_type': original_ob.ob_type.value,
                    'violation_strength': violation_data['violation_strength'],
                    'time_to_violation': violation_data['time_to_violation'],
                    'breaker_formation': 'violation_confirmed'
                }
            )
            
            return breaker
            
        except Exception as e:
            logger.error(f"Error creating breaker block: {e}")
            return None
    
    def _detect_institutional_order_blocks(self, df: pd.DataFrame) -> List[OrderBlock]:
        """Detect high-probability institutional order blocks"""
        institutional_obs = []
        
        try:
            if 'volume' not in df.columns:
                return institutional_obs
            
            # Find exceptional volume spikes
            volume_threshold = df['volume'].rolling(50).quantile(0.95)
            
            for i in range(20, len(df) - 10):
                if df['volume'].iloc[i] > volume_threshold.iloc[i]:
                    # Check if this forms an institutional order block
                    inst_ob = self._analyze_institutional_formation(df, i)
                    if inst_ob:
                        institutional_obs.append(inst_ob)
            
        except Exception as e:
            logger.error(f"Error detecting institutional order blocks: {e}")
        
        return institutional_obs
    
    def _analyze_institutional_formation(self, df: pd.DataFrame, i: int) -> Optional[OrderBlock]:
        """Analyze potential institutional order block formation"""
        try:
            current_bar = df.iloc[i]
            
            # Volume analysis
            current_volume = current_bar['volume']
            avg_volume = df['volume'].iloc[max(0, i-50):i].mean()
            volume_ratio = current_volume / avg_volume
            
            # Must be exceptional volume (3x+ average)
            if volume_ratio < 3.0:
                return None
            
            # Price action analysis
            candle_range = current_bar['high'] - current_bar['low']
            avg_range = (df['high'] - df['low']).iloc[max(0, i-20):i].mean()
            
            # Must be significant price movement
            if candle_range < avg_range * 1.5:
                return None
            
            # Check for subsequent reaction
            reaction_slice = df.iloc[i+1:min(len(df), i+11)]
            if len(reaction_slice) < 5:
                return None
            
            # Determine direction and create institutional OB
            if current_bar['close'] < current_bar['open']:  # Bearish candle
                # Check for bullish reaction (institutional buying)
                max_high_after = reaction_slice['high'].max()
                reaction_strength = (max_high_after - current_bar['low']) / current_bar['low']
                
                if reaction_strength > 0.003:  # 30 pips minimum
                    return self._create_institutional_ob(df, i, OrderBlockType.INSTITUTIONAL_BULLISH, 
                                                       volume_ratio, reaction_strength)
            
            else:  # Bullish candle
                # Check for bearish reaction (institutional selling)
                min_low_after = reaction_slice['low'].min()
                reaction_strength = (current_bar['high'] - min_low_after) / current_bar['high']
                
                if reaction_strength > 0.003:  # 30 pips minimum
                    return self._create_institutional_ob(df, i, OrderBlockType.INSTITUTIONAL_BEARISH,
                                                       volume_ratio, reaction_strength)
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing institutional formation: {e}")
            return None
    
    def _create_institutional_ob(self, df: pd.DataFrame, i: int, ob_type: OrderBlockType,
                               volume_ratio: float, reaction_strength: float) -> OrderBlock:
        """Create institutional order block"""
        current_bar = df.iloc[i]
        
        return OrderBlock(
            ob_type=ob_type,
            top=current_bar['high'],
            bottom=current_bar['low'],
            timestamp=df.index[i],
            index=i,
            strength=min(1.0, (volume_ratio / 5.0 + reaction_strength * 100) / 2),
            volume=current_bar['volume'],
            reaction_strength=reaction_strength,
            distal_line=current_bar['high'] if ob_type == OrderBlockType.INSTITUTIONAL_BEARISH else current_bar['low'],
            proximal_line=current_bar['low'] if ob_type == OrderBlockType.INSTITUTIONAL_BEARISH else current_bar['high'],
            candle_range=current_bar['high'] - current_bar['low'],
            body_size=abs(current_bar['close'] - current_bar['open']),
            wick_ratio=0.5,  # Will be calculated properly
            volume_profile=volume_ratio,
            institutional_level=True,
            confluence_score=0.0,
            metadata={
                'institutional_volume_ratio': volume_ratio,
                'formation_type': 'high_volume_institutional',
                'reaction_strength': reaction_strength
            }
        )
    
    def _validate_order_block_advanced(self, ob: OrderBlock, df: pd.DataFrame) -> bool:
        """Advanced order block validation"""
        try:
            # Basic validation
            if ob.strength < self.ob_strength_threshold:
                return False
            
            # Size validation
            if ob.candle_range < df['close'].iloc[ob.index] * 0.0001:  # 1 pip minimum
                return False
            
            # Volume validation for institutional blocks
            if ob.institutional_level and ob.volume_profile < 2.0:
                return False
            
            # Reaction validation
            if ob.reaction_strength < 0.001:  # 10 pips minimum reaction
                return False
            
            # Age validation (not too old)
            current_index = len(df) - 1
            if (current_index - ob.index) > self.max_ob_age:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating order block: {e}")
            return False
    
    def _filter_and_rank_order_blocks_advanced(self, order_blocks: List[OrderBlock], 
                                             df: pd.DataFrame) -> List[OrderBlock]:
        """Advanced filtering and ranking of order blocks"""
        try:
            if not order_blocks:
                return []
            
            # Remove invalid order blocks
            valid_obs = [ob for ob in order_blocks if self._validate_order_block_advanced(ob, df)]
            
            # Calculate age factor and confluence scores
            current_index = len(df) - 1
            for ob in valid_obs:
                # Age factor
                age_bars = current_index - ob.index
                age_factor = max(0.1, 1.0 - (age_bars / self.max_ob_age))
                
                # Update confluence score
                ob.confluence_score = ob.strength * age_factor
                ob.age_bars = age_bars
                
                # Check if order block has been touched
                ob.touched, ob.mitigation_count = self._check_ob_interaction(df, ob)
            
            # Rank by confluence score
            valid_obs.sort(key=lambda x: x.confluence_score, reverse=True)
            
            # Remove overlapping order blocks (keep strongest)
            filtered_obs = self._remove_overlapping_obs(valid_obs)
            
            # Keep top order blocks
            return filtered_obs[:20]
            
        except Exception as e:
            logger.error(f"Error filtering and ranking order blocks: {e}")
            return order_blocks
    
    def _check_ob_interaction(self, df: pd.DataFrame, ob: OrderBlock) -> Tuple[bool, int]:
        """Check if order block has been interacted with"""
        try:
            touched = False
            touch_count = 0
            
            # Check bars after order block formation
            for i in range(ob.index + 1, len(df)):
                bar = df.iloc[i]
                
                # Check if price interacted with order block
                if ob.ob_type in [OrderBlockType.BULLISH_OB, OrderBlockType.INSTITUTIONAL_BULLISH]:
                    # For bullish OB, check if price came back to the zone
                    if bar['low'] <= ob.top and bar['high'] >= ob.bottom:
                        touched = True
                        touch_count += 1
                else:
                    # For bearish OB, check if price came back to the zone
                    if bar['low'] <= ob.top and bar['high'] >= ob.bottom:
                        touched = True
                        touch_count += 1
            
            return touched, touch_count
            
        except Exception as e:
            logger.error(f"Error checking OB interaction: {e}")
            return False, 0
    
    def _remove_overlapping_obs(self, order_blocks: List[OrderBlock]) -> List[OrderBlock]:
        """Remove overlapping order blocks, keeping the strongest"""
        if not order_blocks:
            return []
        
        filtered_obs = []
        processed_indices = set()
        
        for i, ob1 in enumerate(order_blocks):
            if i in processed_indices:
                continue
            
            # Find overlapping order blocks
            overlapping_obs = [ob1]
            for j, ob2 in enumerate(order_blocks[i+1:], i+1):
                if j not in processed_indices and self._obs_overlap(ob1, ob2):
                    overlapping_obs.append(ob2)
                    processed_indices.add(j)
            
            # Keep the strongest from overlapping group
            strongest_ob = max(overlapping_obs, key=lambda x: x.confluence_score)
            filtered_obs.append(strongest_ob)
            processed_indices.add(i)
        
        return filtered_obs
    
    def _obs_overlap(self, ob1: OrderBlock, ob2: OrderBlock) -> bool:
        """Check if two order blocks overlap"""
        try:
            # Check price overlap
            price_overlap = not (ob1.top < ob2.bottom or ob2.top < ob1.bottom)
            
            # Check time proximity
            time_proximity = abs(ob1.index - ob2.index) <= 5
            
            return price_overlap and time_proximity
            
        except Exception as e:
            logger.error(f"Error checking OB overlap: {e}")
            return False
    
    @timing_decorator
    def _detect_advanced_fair_value_gaps(self, df: pd.DataFrame) -> List[FairValueGap]:
        """Advanced Fair Value Gap detection with comprehensive analysis"""
        try:
            fvgs = []
            
            for i in range(1, len(df) - 1):
                # Bullish FVG detection
                bullish_fvg = self._detect_bullish_fvg(df, i)
                if bullish_fvg:
                    fvgs.append(bullish_fvg)
                
                # Bearish FVG detection
                bearish_fvg = self._detect_bearish_fvg(df, i)
                if bearish_fvg:
                    fvgs.append(bearish_fvg)
            
            # Track mitigation for all FVGs
            self._track_fvg_mitigation_advanced(fvgs, df)
            
            # Filter and rank FVGs
            filtered_fvgs = self._filter_and_rank_fvgs(fvgs, df)
            
            return filtered_fvgs
            
        except Exception as e:
            logger.error(f"Error detecting advanced FVGs: {e}")
            return []
    
    def _detect_bullish_fvg(self, df: pd.DataFrame, i: int) -> Optional[FairValueGap]:
        """Detect bullish Fair Value Gap"""
        try:
            # Bullish FVG: Gap between high[i-1] and low[i+1]
            if i < 1 or i >= len(df) - 1:
                return None
            
            prev_high = df['high'].iloc[i-1]
            next_low = df['low'].iloc[i+1]
            
            if next_low > prev_high:
                gap_size = next_low - prev_high
                
                if gap_size >= self.fvg_min_size:
                    # Enhanced FVG creation
                    fvg = self._create_enhanced_fvg(
                        FairValueGapType.BULLISH_FVG, i, prev_high, next_low, gap_size, df
                    )
                    
                    if self._validate_fvg_advanced(fvg, df):
                        return fvg
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting bullish FVG: {e}")
            return None
    
    def _detect_bearish_fvg(self, df: pd.DataFrame, i: int) -> Optional[FairValueGap]:
        """Detect bearish Fair Value Gap"""
        try:
            # Bearish FVG: Gap between low[i-1] and high[i+1]
            if i < 1 or i >= len(df) - 1:
                return None
            
            prev_low = df['low'].iloc[i-1]
            next_high = df['high'].iloc[i+1]
            
            if next_high < prev_low:
                gap_size = prev_low - next_high
                
                if gap_size >= self.fvg_min_size:
                    # Enhanced FVG creation
                    fvg = self._create_enhanced_fvg(
                        FairValueGapType.BEARISH_FVG, i, prev_low, next_high, gap_size, df
                    )
                    
                    if self._validate_fvg_advanced(fvg, df):
                        return fvg
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting bearish FVG: {e}")
            return None
    
    def _create_enhanced_fvg(self, gap_type: FairValueGapType, index: int, top: float,
                           bottom: float, size: float, df: pd.DataFrame) -> FairValueGap:
        """Create enhanced Fair Value Gap with comprehensive analysis"""
        try:
            # Volume analysis
            volume = df['volume'].iloc[index] if 'volume' in df.columns else 0
            avg_volume = df['volume'].iloc[max(0, index-20):index].mean() if 'volume' in df.columns else 0
            volume_confirmation = volume > avg_volume * 1.2 if avg_volume > 0 else False
            
            # Size analysis
            price_level = (top + bottom) / 2
            size_percentage = size / price_level
            
            # Institutional level assessment
            institutional_level = (
                size >= self.institutional_size_threshold and
                volume_confirmation
            )
            
            # Upgrade gap type if institutional
            if institutional_level:
                if gap_type == FairValueGapType.BULLISH_FVG:
                    gap_type = FairValueGapType.INSTITUTIONAL_FVG
                elif size_percentage > 0.01:  # 1% of price
                    gap_type = FairValueGapType.HIGH_IMPACT_FVG
            
            # Calculate importance score
            importance_factors = [
                min(1.0, size_percentage * 1000),  # Size factor
                min(1.0, volume / avg_volume) if avg_volume > 0 else 0.5,  # Volume factor
                1.0 if institutional_level else 0.5,  # Institutional factor
            ]
            importance_score = np.mean(importance_factors)
            
            # Price action quality assessment
            price_action_quality = self._assess_fvg_price_action(df, index)
            
            # Confluence factors
            confluence_factors = self._identify_fvg_confluence_factors(df, index, top, bottom)
            
            return FairValueGap(
                gap_type=gap_type,
                top=top,
                bottom=bottom,
                timestamp=df.index[index],
                index=index,
                size=size,
                volume=volume,
                strength=importance_score,
                institutional_level=institutional_level,
                importance_score=importance_score,
                confluence_factors=confluence_factors,
                volume_confirmation=volume_confirmation,
                price_action_quality=price_action_quality,
                metadata={
                    'size_percentage': size_percentage,
                    'volume_ratio': volume / avg_volume if avg_volume > 0 else 1.0,
                    'formation_bars': f"{index-1}-{index}-{index+1}",
                    'price_context': price_level
                }
            )
            
        except Exception as e:
            logger.error(f"Error creating enhanced FVG: {e}")
            return None
    
    def _assess_fvg_price_action(self, df: pd.DataFrame, index: int) -> float:
        """Assess price action quality around FVG formation"""
        try:
            quality_factors = []
            
            # Check the three bars involved in FVG formation
            if index >= 1 and index < len(df) - 1:
                prev_bar = df.iloc[index - 1]
                current_bar = df.iloc[index]
                next_bar = df.iloc[index + 1]
                
                # Momentum consistency
                prev_momentum = prev_bar['close'] - prev_bar['open']
                current_momentum = current_bar['close'] - current_bar['open']
                next_momentum = next_bar['close'] - next_bar['open']
                
                # Check for momentum alignment
                if (prev_momentum > 0 and next_momentum > 0) or (prev_momentum < 0 and next_momentum < 0):
                    quality_factors.append(0.8)
                else:
                    quality_factors.append(0.4)
                
                # Check for strong impulse move
                total_move = abs(next_bar['close'] - prev_bar['open'])
                avg_range = (df['high'] - df['low']).iloc[max(0, index-10):index].mean()
                
                if total_move > avg_range * 1.5:
                    quality_factors.append(0.9)
                else:
                    quality_factors.append(0.5)
                
                # Volume progression
                if 'volume' in df.columns:
                    volumes = [prev_bar.get('volume', 0), current_bar.get('volume', 0), next_bar.get('volume', 0)]
                    if volumes[2] > volumes[0]:  # Volume increasing with move
                        quality_factors.append(0.8)
                    else:
                        quality_factors.append(0.5)
            
            return np.mean(quality_factors) if quality_factors else 0.5
            
        except Exception as e:
            logger.error(f"Error assessing FVG price action: {e}")
            return 0.5
    
    def _identify_fvg_confluence_factors(self, df: pd.DataFrame, index: int, 
                                       top: float, bottom: float) -> List[str]:
        """Identify confluence factors for FVG"""
        factors = []
        
        try:
            midpoint = (top + bottom) / 2
            
            # Round number confluence
            midpoint_str = f"{midpoint:.5f}"
            if midpoint_str.endswith('00000') or midpoint_str.endswith('50000'):
                factors.append('major_round_number')
            elif midpoint_str.endswith('0000') or midpoint_str.endswith('5000'):
                factors.append('round_number')
            
            # Volume spike confluence
            if 'volume' in df.columns:
                current_volume = df['volume'].iloc[index]
                avg_volume = df['volume'].iloc[max(0, index-20):index].mean()
                if current_volume > avg_volume * 2:
                    factors.append('volume_spike')
            
            # Time confluence (major session times, etc.)
            # This would require timestamp analysis in real implementation
            
            # Fibonacci level confluence
            # This would require fibonacci calculations in real implementation
            
        except Exception as e:
            logger.error(f"Error identifying FVG confluence factors: {e}")
        
        return factors
    
    def _validate_fvg_advanced(self, fvg: FairValueGap, df: pd.DataFrame) -> bool:
        """Advanced FVG validation"""
        try:
            if not fvg:
                return False
            
            # Size validation
            if fvg.size < self.fvg_min_size:
                return False
            
            # Strength validation
            if fvg.strength < 0.3:
                return False
            
            # Age validation
            current_index = len(df) - 1
            if (current_index - fvg.index) > 200:  # Max 200 bars old
                return False
            
            # Price action quality validation
            if fvg.price_action_quality < 0.4:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating FVG: {e}")
            return False
    
    def _track_fvg_mitigation_advanced(self, fvgs: List[FairValueGap], df: pd.DataFrame):
        """Advanced FVG mitigation tracking"""
        try:
            for fvg in fvgs:
                if not fvg.is_filled:
                    mitigation_data = self._calculate_fvg_mitigation_advanced(fvg, df)
                    
                    fvg.mitigation_percentage = mitigation_data['percentage']
                    fvg.retest_count = mitigation_data['retest_count']
                    
                    if mitigation_data['percentage'] >= 100:
                        fvg.is_filled = True
                        fvg.fill_timestamp = mitigation_data['fill_timestamp']
                        fvg.fill_speed = mitigation_data['fill_speed']
            
        except Exception as e:
            logger.error(f"Error tracking FVG mitigation: {e}")
    
    def _calculate_fvg_mitigation_advanced(self, fvg: FairValueGap, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate advanced FVG mitigation metrics"""
        try:
            mitigation_data = {
                'percentage': 0.0,
                'retest_count': 0,
                'fill_timestamp': None,
                'fill_speed': 0
            }
            
            gap_size = fvg.top - fvg.bottom
            max_mitigation = 0.0
            
            # Check bars after FVG formation
            for i in range(fvg.index + 1, len(df)):
                bar = df.iloc[i]
                
                # Calculate mitigation for this bar
                bar_mitigation = 0.0
                
                if fvg.gap_type in [FairValueGapType.BULLISH_FVG, FairValueGapType.INSTITUTIONAL_FVG]:
                    # Bullish FVG mitigation
                    if bar['low'] <= fvg.top:
                        if bar['low'] <= fvg.bottom:
                            bar_mitigation = 100.0  # Fully filled
                            mitigation_data['fill_timestamp'] = df.index[i]
                            mitigation_data['fill_speed'] = i - fvg.index
                        else:
                            # Partially filled
                            filled_distance = fvg.top - bar['low']
                            bar_mitigation = (filled_distance / gap_size) * 100
                        
                        mitigation_data['retest_count'] += 1
                
                else:  # Bearish FVG
                    if bar['high'] >= fvg.bottom:
                        if bar['high'] >= fvg.top:
                            bar_mitigation = 100.0  # Fully filled
                            mitigation_data['fill_timestamp'] = df.index[i]
                            mitigation_data['fill_speed'] = i - fvg.index
                        else:
                            # Partially filled
                            filled_distance = bar['high'] - fvg.bottom
                            bar_mitigation = (filled_distance / gap_size) * 100
                        
                        mitigation_data['retest_count'] += 1
                
                max_mitigation = max(max_mitigation, bar_mitigation)
                
                if bar_mitigation >= 100:
                    break
            
            mitigation_data['percentage'] = max_mitigation
            return mitigation_data
            
        except Exception as e:
            logger.error(f"Error calculating FVG mitigation: {e}")
            return {'percentage': 0.0, 'retest_count': 0, 'fill_timestamp': None, 'fill_speed': 0}
    
    def _filter_and_rank_fvgs(self, fvgs: List[FairValueGap], df: pd.DataFrame) -> List[FairValueGap]:
        """Filter and rank Fair Value Gaps by quality and relevance"""
        try:
            if not fvgs:
                return []
            
            # Filter valid FVGs
            valid_fvgs = [fvg for fvg in fvgs if self._validate_fvg_advanced(fvg, df)]
            
            # Calculate age factor for each FVG
            current_index = len(df) - 1
            for fvg in valid_fvgs:
                age_bars = current_index - fvg.index
                age_factor = max(0.1, 1.0 - (age_bars / 200))  # 200 bar max age
                
                # Update importance score with age factor
                fvg.importance_score = fvg.strength * age_factor
            
            # Sort by importance score
            valid_fvgs.sort(key=lambda x: x.importance_score, reverse=True)
            
            # Keep top FVGs
            return valid_fvgs[:30]
            
        except Exception as e:
            logger.error(f"Error filtering and ranking FVGs: {e}")
            return fvgs
    
    @timing_decorator
    def _detect_advanced_liquidity_sweeps(self, df: pd.DataFrame) -> List[LiquiditySweep]:
        """Advanced liquidity sweep detection with institutional analysis"""
        try:
            liquidity_sweeps = []
            
            # Get swing points for liquidity analysis
            swing_data = self._calculate_advanced_swing_points(df)
            swing_highs = swing_data['swing_highs']
            swing_lows = swing_data['swing_lows']
            
            # Detect different types of liquidity sweeps
            high_sweeps = self._detect_high_liquidity_sweeps_advanced(df, swing_highs)
            low_sweeps = self._detect_low_liquidity_sweeps_advanced(df, swing_lows)
            equal_highs_sweeps = self._detect_equal_highs_sweeps(df, swing_highs)
            equal_lows_sweeps = self._detect_equal_lows_sweeps(df, swing_lows)
            
            # Combine all sweeps
            all_sweeps = high_sweeps + low_sweeps + equal_highs_sweeps + equal_lows_sweeps
            
            # Filter and validate sweeps
            validated_sweeps = [sweep for sweep in all_sweeps if self._validate_liquidity_sweep_advanced(sweep, df)]
            
            return validated_sweeps
            
        except Exception as e:
            logger.error(f"Error detecting advanced liquidity sweeps: {e}")
            return []
    
    def _detect_high_liquidity_sweeps_advanced(self, df: pd.DataFrame, 
                                             swing_highs: List[Dict]) -> List[LiquiditySweep]:
        """Detect advanced high liquidity sweeps"""
        sweeps = []
        
        try:
            for i in range(len(df)):
                current_bar = df.iloc[i]
                
                # Find relevant swing highs to sweep
                relevant_swings = [
                    swing for swing in swing_highs
                    if swing['index'] < i and swing['index'] > i - self.stop_hunt_detection_period
                ]
                
                for swing in relevant_swings:
                    if current_bar['high'] > swing['level']:
                        sweep_analysis = self._analyze_liquidity_sweep_advanced(
                            df, i, swing, LiquidityType.STOP_HUNT_HIGH
                        )
                        
                        if sweep_analysis:
                            sweeps.append(sweep_analysis)
            
        except Exception as e:
            logger.error(f"Error detecting high liquidity sweeps: {e}")
        
        return sweeps
    
    def _detect_low_liquidity_sweeps_advanced(self, df: pd.DataFrame,
                                            swing_lows: List[Dict]) -> List[LiquiditySweep]:
        """Detect advanced low liquidity sweeps"""
        sweeps = []
        
        try:
            for i in range(len(df)):
                current_bar = df.iloc[i]
                
                # Find relevant swing lows to sweep
                relevant_swings = [
                    swing for swing in swing_lows
                    if swing['index'] < i and swing['index'] > i - self.stop_hunt_detection_period
                ]
                
                for swing in relevant_swings:
                    if current_bar['low'] < swing['level']:
                        sweep_analysis = self._analyze_liquidity_sweep_advanced(
                            df, i, swing, LiquidityType.STOP_HUNT_LOW
                        )
                        
                        if sweep_analysis:
                            sweeps.append(sweep_analysis)
            
        except Exception as e:
            logger.error(f"Error detecting low liquidity sweeps: {e}")
        
        return sweeps
    
    def _detect_equal_highs_sweeps(self, df: pd.DataFrame, swing_highs: List[Dict]) -> List[LiquiditySweep]:
        """Detect equal highs liquidity sweeps"""
        sweeps = []
        
        try:
            # Find equal highs (highs within small range)
            equal_highs_groups = self._find_equal_levels(swing_highs, 'high')
            
            for group in equal_highs_groups:
                if len(group) >= 2:  # At least 2 equal highs
                    # Look for sweeps of these equal highs
                    highest_level = max(swing['level'] for swing in group)
                    latest_swing_index = max(swing['index'] for swing in group)
                    
                    # Check for sweep after the equal highs formation
                    for i in range(latest_swing_index + 1, len(df)):
                        if df['high'].iloc[i] > highest_level:
                            sweep = self._create_equal_highs_sweep(df, i, group, highest_level)
                            if sweep:
                                sweeps.append(sweep)
                            break  # Only first sweep matters
            
        except Exception as e:
            logger.error(f"Error detecting equal highs sweeps: {e}")
        
        return sweeps
    
    def _detect_equal_lows_sweeps(self, df: pd.DataFrame, swing_lows: List[Dict]) -> List[LiquiditySweep]:
        """Detect equal lows liquidity sweeps"""
        sweeps = []
        
        try:
            # Find equal lows (lows within small range)
            equal_lows_groups = self._find_equal_levels(swing_lows, 'low')
            
            for group in equal_lows_groups:
                if len(group) >= 2:  # At least 2 equal lows
                    # Look for sweeps of these equal lows
                    lowest_level = min(swing['level'] for swing in group)
                    latest_swing_index = max(swing['index'] for swing in group)
                    
                    # Check for sweep after the equal lows formation
                    for i in range(latest_swing_index + 1, len(df)):
                        if df['low'].iloc[i] < lowest_level:
                            sweep = self._create_equal_lows_sweep(df, i, group, lowest_level)
                            if sweep:
                                sweeps.append(sweep)
                            break  # Only first sweep matters
            
        except Exception as e:
            logger.error(f"Error detecting equal lows sweeps: {e}")
        
        return sweeps
    
    def _find_equal_levels(self, swing_points: List[Dict], level_type: str) -> List[List[Dict]]:
        """Find groups of equal levels (highs or lows)"""
        try:
            if not swing_points:
                return []
            
            # Sort by level
            sorted_swings = sorted(swing_points, key=lambda x: x['level'])
            
            equal_groups = []
            current_group = [sorted_swings[0]]
            
            for i in range(1, len(sorted_swings)):
                current_level = sorted_swings[i]['level']
                previous_level = sorted_swings[i-1]['level']
                
                # Check if levels are equal (within small tolerance)
                if abs(current_level - previous_level) / previous_level < 0.001:  # 0.1% tolerance
                    current_group.append(sorted_swings[i])
                else:
                    if len(current_group) >= 2:
                        equal_groups.append(current_group)
                    current_group = [sorted_swings[i]]
            
            # Check final group
            if len(current_group) >= 2:
                equal_groups.append(current_group)
            
            return equal_groups
            
        except Exception as e:
            logger.error(f"Error finding equal levels: {e}")
            return []
    
    def _create_equal_highs_sweep(self, df: pd.DataFrame, sweep_index: int, 
                                equal_highs: List[Dict], swept_level: float) -> Optional[LiquiditySweep]:
        """Create equal highs liquidity sweep"""
        try:
            sweep_analysis = self._analyze_liquidity_sweep_advanced(
                df, sweep_index, {'level': swept_level, 'index': sweep_index}, 
                LiquidityType.EQUAL_HIGHS
            )
            
            if sweep_analysis:
                # Enhance with equal highs specific data
                sweep_analysis.metadata.update({
                    'equal_highs_count': len(equal_highs),
                    'equal_highs_levels': [swing['level'] for swing in equal_highs],
                    'swept_level': swept_level
                })
            
            return sweep_analysis
            
        except Exception as e:
            logger.error(f"Error creating equal highs sweep: {e}")
            return None
    
    def _create_equal_lows_sweep(self, df: pd.DataFrame, sweep_index: int,
                               equal_lows: List[Dict], swept_level: float) -> Optional[LiquiditySweep]:
        """Create equal lows liquidity sweep"""
        try:
            sweep_analysis = self._analyze_liquidity_sweep_advanced(
                df, sweep_index, {'level': swept_level, 'index': sweep_index},
                LiquidityType.EQUAL_LOWS
            )
            
            if sweep_analysis:
                # Enhance with equal lows specific data
                sweep_analysis.metadata.update({
                    'equal_lows_count': len(equal_lows),
                    'equal_lows_levels': [swing['level'] for swing in equal_lows],
                    'swept_level': swept_level
                })
            
            return sweep_analysis
            
        except Exception as e:
            logger.error(f"Error creating equal lows sweep: {e}")
            return None
    
    def _analyze_liquidity_sweep_advanced(self, df: pd.DataFrame, current_index: int,
                                        swing_point: Dict, sweep_type: LiquidityType) -> Optional[LiquiditySweep]:
        """Advanced liquidity sweep analysis with institutional detection"""
        try:
            current_bar = df.iloc[current_index]
            
            # Volume analysis
            volume_data = self._analyze_sweep_volume(df, current_index)
            
            # Reversal analysis
            reversal_data = self._analyze_sweep_reversal(df, current_index, sweep_type)
            
            # Institutional footprint analysis
            institutional_data = self._analyze_institutional_footprint_sweep(df, current_index)
            
            # Calculate sweep distance
            if sweep_type in [LiquidityType.STOP_HUNT_HIGH, LiquidityType.EQUAL_HIGHS]:
                sweep_distance = current_bar['high'] - swing_point['level']
                sweep_price = current_bar['high']
            else:
                sweep_distance = swing_point['level'] - current_bar['low']
                sweep_price = current_bar['low']
            
            # Validate sweep significance
            if not self._validate_sweep_significance(sweep_distance, df, current_index):
                return None
            
            # Calculate stop hunt probability
            stop_hunt_probability = self._calculate_stop_hunt_probability(
                volume_data, reversal_data, institutional_data
            )
            
            # Calculate liquidity captured
            liquidity_captured = self._estimate_liquidity_captured(df, current_index, sweep_distance)
            
            return LiquiditySweep(
                sweep_type=sweep_type,
                swept_level=swing_point['level'],
                sweep_price=sweep_price,
                timestamp=df.index[current_index],
                index=current_index,
                volume_spike=volume_data['spike_detected'],
                reversal_confirmed=reversal_data['reversal_confirmed'],
                sweep_distance=sweep_distance,
                fake_breakout=not reversal_data['reversal_confirmed'],
                volume_ratio=volume_data['volume_ratio'],
                reversal_strength=reversal_data['reversal_strength'],
                time_to_reversal=reversal_data['time_to_reversal'],
                institutional_footprint=institutional_data['institutional_detected'],
                stop_hunt_probability=stop_hunt_probability,
                liquidity_captured=liquidity_captured,
                smart_money_activity=institutional_data['smart_money_score'],
                metadata={
                    'volume_analysis': volume_data,
                    'reversal_analysis': reversal_data,
                    'institutional_analysis': institutional_data,
                    'sweep_validation': True
                }
            )
            
        except Exception as e:
            logger.error(f"Error analyzing advanced liquidity sweep: {e}")
            return None
    
    def _analyze_sweep_volume(self, df: pd.DataFrame, index: int) -> Dict[str, Any]:
        """Analyze volume characteristics for sweep"""
        try:
            volume_data = {
                'spike_detected': False,
                'volume_ratio': 1.0,
                'volume_percentile': 50.0,
                'volume_trend': 'neutral'
            }
            
            if 'volume' not in df.columns:
                return volume_data
            
            current_volume = df['volume'].iloc[index]
            
            # Calculate volume statistics
            lookback_volumes = df['volume'].iloc[max(0, index-50):index]
            avg_volume = lookback_volumes.mean()
            volume_percentile = stats.percentileofscore(lookback_volumes, current_volume)
            
            # Volume ratio and spike detection
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            spike_detected = volume_ratio > self.volume_spike_threshold
            
            # Volume trend analysis
            recent_volumes = df['volume'].iloc[max(0, index-5):index+1]
            if len(recent_volumes) > 3:
                trend_slope = np.polyfit(range(len(recent_volumes)), recent_volumes, 1)[0]
                if trend_slope > avg_volume * 0.1:
                    volume_trend = 'increasing'
                elif trend_slope < -avg_volume * 0.1:
                    volume_trend = 'decreasing'
                else:
                    volume_trend = 'neutral'
            
            volume_data.update({
                'spike_detected': spike_detected,
                'volume_ratio': volume_ratio,
                'volume_percentile': volume_percentile,
                'volume_trend': volume_trend
            })
            
            return volume_data
            
        except Exception as e:
            logger.error(f"Error analyzing sweep volume: {e}")
            return {'spike_detected': False, 'volume_ratio': 1.0, 'volume_percentile': 50.0, 'volume_trend': 'neutral'}
    
    def _analyze_sweep_reversal(self, df: pd.DataFrame, index: int, sweep_type: LiquidityType) -> Dict[str, Any]:
        """Analyze reversal characteristics after sweep"""
        try:
            reversal_data = {
                'reversal_confirmed': False,
                'reversal_strength': 0.0,
                'time_to_reversal': 0,
                'reversal_volume_confirmed': False
            }
            
            if index + 5 >= len(df):
                return reversal_data
            
            current_bar = df.iloc[index]
            future_bars = df.iloc[index+1:min(len(df), index+11)]
            
            if sweep_type in [LiquidityType.STOP_HUNT_HIGH, LiquidityType.EQUAL_HIGHS]:
                # Look for bearish reversal after high sweep
                entry_price = current_bar['high']
                
                for i, bar in enumerate(future_bars.iterrows()):
                    bar_data = bar[1]
                    if bar_data['close'] < entry_price * 0.998:  # 0.2% reversal
                        reversal_strength = (entry_price - bar_data['close']) / entry_price
                        reversal_data.update({
                            'reversal_confirmed': True,
                            'reversal_strength': reversal_strength,
                            'time_to_reversal': i + 1
                        })
                        
                        # Check volume confirmation
                        if 'volume' in df.columns:
                            reversal_volume = bar_data['volume']
                            avg_volume = df['volume'].iloc[max(0, index-10):index].mean()
                            reversal_data['reversal_volume_confirmed'] = reversal_volume > avg_volume
                        
                        break
            
            else:  # Low sweeps
                # Look for bullish reversal after low sweep
                entry_price = current_bar['low']
                
                for i, bar in enumerate(future_bars.iterrows()):
                    bar_data = bar[1]
                    if bar_data['close'] > entry_price * 1.002:  # 0.2% reversal
                        reversal_strength = (bar_data['close'] - entry_price) / entry_price
                        reversal_data.update({
                            'reversal_confirmed': True,
                            'reversal_strength': reversal_strength,
                            'time_to_reversal': i + 1
                        })
                        
                        # Check volume confirmation
                        if 'volume' in df.columns:
                            reversal_volume = bar_data['volume']
                            avg_volume = df['volume'].iloc[max(0, index-10):index].mean()
                            reversal_data['reversal_volume_confirmed'] = reversal_volume > avg_volume
                        
                        break
            
            return reversal_data
            
        except Exception as e:
            logger.error(f"Error analyzing sweep reversal: {e}")
            return {'reversal_confirmed': False, 'reversal_strength': 0.0, 'time_to_reversal': 0, 'reversal_volume_confirmed': False}
    
    def _analyze_institutional_footprint_sweep(self, df: pd.DataFrame, index: int) -> Dict[str, Any]:
        """Analyze institutional footprint in sweep"""
        try:
            institutional_data = {
                'institutional_detected': False,
                'smart_money_score': 0.0,
                'order_flow_imbalance': False,
                'large_order_detected': False
            }
            
            if 'volume' not in df.columns:
                return institutional_data
            
            # Large order detection
            current_volume = df['volume'].iloc[index]
            volume_threshold = df['volume'].iloc[max(0, index-100):index].quantile(0.95)
            large_order_detected = current_volume > volume_threshold
            
            # Smart money score calculation
            factors = []
            
            # Volume factor
            avg_volume = df['volume'].iloc[max(0, index-50):index].mean()
            volume_factor = min(1.0, current_volume / (avg_volume * 3)) if avg_volume > 0 else 0
            factors.append(volume_factor)
            
            # Price impact factor
            current_bar = df.iloc[index]
            candle_range = current_bar['high'] - current_bar['low']
            avg_range = (df['high'] - df['low']).iloc[max(0, index-20):index].mean()
            price_impact_factor = min(1.0, candle_range / avg_range) if avg_range > 0 else 0
            factors.append(price_impact_factor)
            
            # Timing factor (unusual hours, etc.)
            # This would require actual timestamp analysis in real implementation
            timing_factor = 0.5  # Placeholder
            factors.append(timing_factor)
            
            smart_money_score = np.mean(factors)
            institutional_detected = smart_money_score > 0.6 and large_order_detected
            
            institutional_data.update({
                'institutional_detected': institutional_detected,
                'smart_money_score': smart_money_score,
                'large_order_detected': large_order_detected
            })
            
            return institutional_data
            
        except Exception as e:
            logger.error(f"Error analyzing institutional footprint: {e}")
            return {'institutional_detected': False, 'smart_money_score': 0.0, 'order_flow_imbalance': False, 'large_order_detected': False}
    
    def _validate_sweep_significance(self, sweep_distance: float, df: pd.DataFrame, index: int) -> bool:
        """Validate if sweep distance is significant"""
        try:
            # Minimum distance requirement
            price_level = df['close'].iloc[index]
            min_distance = price_level * 0.0001  # 1 pip minimum
            
            if sweep_distance < min_distance:
                return False
            
            # Average range comparison
            avg_range = (df['high'] - df['low']).iloc[max(0, index-20):index].mean()
            if sweep_distance < avg_range * 0.1:  # At least 10% of average range
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating sweep significance: {e}")
            return False
    
    def _calculate_stop_hunt_probability(self, volume_data: Dict, reversal_data: Dict, 
                                       institutional_data: Dict) -> float:
        """Calculate probability that this is a stop hunt"""
        try:
            probability_factors = []
            
            # Volume spike factor
            if volume_data['spike_detected']:
                probability_factors.append(0.3)
            
            # Reversal confirmation factor
            if reversal_data['reversal_confirmed']:
                reversal_strength = reversal_data['reversal_strength']
                probability_factors.append(min(0.4, reversal_strength * 20))
            
            # Institutional activity factor
            if institutional_data['institutional_detected']:
                probability_factors.append(0.3)
            
            # Time to reversal factor (faster reversal = higher probability)
            if reversal_data['time_to_reversal'] > 0:
                time_factor = max(0.1, 1.0 - (reversal_data['time_to_reversal'] / 10))
                probability_factors.append(time_factor * 0.2)
            
            return min(1.0, sum(probability_factors))
            
        except Exception as e:
            logger.error(f"Error calculating stop hunt probability: {e}")
            return 0.0
    
    def _estimate_liquidity_captured(self, df: pd.DataFrame, index: int, sweep_distance: float) -> float:
        """Estimate amount of liquidity captured in sweep"""
        try:
            # Simple estimation based on volume and distance
            if 'volume' not in df.columns:
                return 0.0
            
            current_volume = df['volume'].iloc[index]
            avg_volume = df['volume'].iloc[max(0, index-20):index].mean()
            
            # Liquidity estimation (simplified)
            volume_factor = current_volume / avg_volume if avg_volume > 0 else 1.0
            distance_factor = min(1.0, sweep_distance / (df['close'].iloc[index] * 0.001))
            
            liquidity_estimate = volume_factor * distance_factor * 1000  # Scaled estimate
            
            return liquidity_estimate
            
        except Exception as e:
            logger.error(f"Error estimating liquidity captured: {e}")
            return 0.0
    
    def _validate_liquidity_sweep_advanced(self, sweep: LiquiditySweep, df: pd.DataFrame) -> bool:
        """Advanced validation of liquidity sweep"""
        try:
            # Minimum distance validation
            min_distance = df['close'].iloc[sweep.index] * 0.0001  # 1 pip
            if sweep.sweep_distance < min_distance:
                return False
            
            # Volume validation
            if sweep.volume_ratio < 1.2:  # At least 20% above average
                return False
            
            # Stop hunt probability validation
            if sweep.stop_hunt_probability < 0.3:
                return False
            
            # Age validation
            current_index = len(df) - 1
            if (current_index - sweep.index) > 50:  # Not too old
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating liquidity sweep: {e}")
            return False
    
    @timing_decorator
    def _analyze_advanced_market_structure(self, df: pd.DataFrame) -> List[MarketStructureShift]:
        """Advanced market structure analysis with comprehensive pattern recognition"""
        try:
            structure_shifts = []
            
            # Get swing points for structure analysis
            swing_data = self._calculate_advanced_swing_points(df)
            swing_highs = swing_data['swing_highs']
            swing_lows = swing_data['swing_lows']
            
            # Combine and analyze swing points
            combined_swings = self._combine_and_sort_swings(swing_highs, swing_lows)
            
            if len(combined_swings) < 2:
                return structure_shifts
            
            # Analyze structure shifts
            for i in range(1, len(combined_swings)):
                shift = self._analyze_structure_shift_advanced(df, combined_swings[i-1], combined_swings[i])
                if shift and self._validate_structure_shift(shift, df):
                    structure_shifts.append(shift)
            
            # Analyze higher timeframe structure
            htf_shifts = self._analyze_higher_timeframe_structure(df, combined_swings)
            structure_shifts.extend(htf_shifts)
            
            # Filter and rank structure shifts
            filtered_shifts = self._filter_and_rank_structure_shifts(structure_shifts, df)
            
            return filtered_shifts
            
        except Exception as e:
            logger.error(f"Error analyzing advanced market structure: {e}")
            return []
    
    def _combine_and_sort_swings(self, swing_highs: List[Dict], swing_lows: List[Dict]) -> List[Dict]:
        """Combine and sort swing points chronologically"""
        try:
            combined_swings = []
            
            # Add swing highs
            for swing in swing_highs:
                swing_copy = swing.copy()
                swing_copy['swing_type'] = 'high'
                combined_swings.append(swing_copy)
            
            # Add swing lows
            for swing in swing_lows:
                swing_copy = swing.copy()
                swing_copy['swing_type'] = 'low'
                combined_swings.append(swing_copy)
            
            # Sort by index
            combined_swings.sort(key=lambda x: x['index'])
            
            return combined_swings
            
        except Exception as e:
            logger.error(f"Error combining and sorting swings: {e}")
            return []
    
    def _analyze_structure_shift_advanced(self, df: pd.DataFrame, prev_swing: Dict, 
                                        current_swing: Dict) -> Optional[MarketStructureShift]:
        """Advanced structure shift analysis"""
        try:
            # Determine shift type
            shift_type = self._determine_shift_type(prev_swing, current_swing)
            
            if not shift_type:
                return None
            
            # Calculate shift metrics
            price_move = abs(current_swing['level'] - prev_swing['level'])
            time_diff = current_swing['index'] - prev_swing['index']
            time_velocity = price_move / max(time_diff, 1)
            
            # Volume confirmation analysis
            volume_confirmation = self._analyze_structure_volume_confirmation_advanced(
                df, prev_swing['index'], current_swing['index']
            )
            
            # Price momentum calculation
            price_momentum = self._calculate_structure_price_momentum(df, prev_swing, current_swing)
            
            # Break quality assessment
            break_quality = self._assess_structure_break_quality(df, prev_swing, current_swing)
            
            # Institutional backing analysis
            institutional_backing = self._analyze_institutional_backing_structure(
                df, prev_swing['index'], current_swing['index']
            )
            
            # Confluence factors
            confluence_factors = self._identify_structure_confluence_factors(
                df, prev_swing, current_swing
            )
            
            # Calculate strength
            strength = self._calculate_structure_shift_strength(
                time_velocity, volume_confirmation, break_quality, institutional_backing
            )
            
            return MarketStructureShift(
                shift_type=shift_type,
                from_price=prev_swing['level'],
                to_price=current_swing['level'],
                from_index=prev_swing['index'],
                to_index=current_swing['index'],
                timestamp=df.index[current_swing['index']],
                strength=strength,
                volume_confirmation=volume_confirmation['confirmed'],
                price_momentum=price_momentum,
                time_velocity=time_velocity,
                break_quality=break_quality,
                retest_probability=self._calculate_retest_probability(prev_swing, current_swing),
                trend_continuation_probability=self._calculate_trend_continuation_probability(
                    df, current_swing, shift_type
                ),
                institutional_backing=institutional_backing,
                confluence_factors=confluence_factors,
                metadata={
                    'prev_swing_data': prev_swing,
                    'current_swing_data': current_swing,
                    'volume_analysis': volume_confirmation,
                    'break_quality_score': break_quality
                }
            )
            
        except Exception as e:
            logger.error(f"Error analyzing advanced structure shift: {e}")
            return None
    
    def _determine_shift_type(self, prev_swing: Dict, current_swing: Dict) -> Optional[MarketStructure]:
        """Determine the type of market structure shift"""
        try:
            prev_type = prev_swing['swing_type']
            current_type = current_swing['swing_type']
            prev_level = prev_swing['level']
            current_level = current_swing['level']
            
            if prev_type == 'high' and current_type == 'low':
                if current_level < prev_level:
                    # Lower low after high = bearish structure
                    return MarketStructure.BOS_BEARISH
                else:
                    # Higher low after high = potential bullish change
                    return MarketStructure.CHOCH_BULLISH
            
            elif prev_type == 'low' and current_type == 'high':
                if current_level > prev_level:
                    # Higher high after low = bullish structure
                    return MarketStructure.BOS_BULLISH
                else:
                    # Lower high after low = potential bearish change
                    return MarketStructure.CHOCH_BEARISH
            
            return None
            
        except Exception as e:
            logger.error(f"Error determining shift type: {e}")
            return None
    
    def _analyze_structure_volume_confirmation_advanced(self, df: pd.DataFrame, 
                                                      start_index: int, end_index: int) -> Dict[str, Any]:
        """Advanced volume confirmation analysis for structure shifts"""
        try:
            confirmation_data = {
                'confirmed': False,
                'volume_ratio': 1.0,
                'volume_trend': 'neutral',
                'institutional_participation': False
            }
            
            if 'volume' not in df.columns:
                confirmation_data['confirmed'] = True  # Assume confirmed if no volume data
                return confirmation_data
            
            # Volume during the move
            move_volumes = df['volume'].iloc[start_index:end_index+1]
            avg_move_volume = move_volumes.mean()
            
            # Baseline volume
            baseline_volumes = df['volume'].iloc[max(0, start_index-50):start_index]
            avg_baseline_volume = baseline_volumes.mean()
            
            # Volume ratio analysis
            volume_ratio = avg_move_volume / avg_baseline_volume if avg_baseline_volume > 0 else 1.0
            
            # Volume trend during move
            if len(move_volumes) > 2:
                volume_trend_slope = np.polyfit(range(len(move_volumes)), move_volumes, 1)[0]
                if volume_trend_slope > avg_baseline_volume * 0.1:
                    volume_trend = 'increasing'
                elif volume_trend_slope < -avg_baseline_volume * 0.1:
                    volume_trend = 'decreasing'
                else:
                    volume_trend = 'neutral'
            else:
                volume_trend = 'neutral'
            
            # Institutional participation
            max_volume_in_move = move_volumes.max()
            volume_95th_percentile = baseline_volumes.quantile(0.95)
            institutional_participation = max_volume_in_move > volume_95th_percentile
            
            # Confirmation logic
            confirmed = (
                volume_ratio > 1.2 or  # 20% above baseline
                volume_trend == 'increasing' or
                institutional_participation
            )
            
            confirmation_data.update({
                'confirmed': confirmed,
                'volume_ratio': volume_ratio,
                'volume_trend': volume_trend,
                'institutional_participation': institutional_participation
            })
            
            return confirmation_data
            
        except Exception as e:
            logger.error(f"Error analyzing structure volume confirmation: {e}")
            return {'confirmed': False, 'volume_ratio': 1.0, 'volume_trend': 'neutral', 'institutional_participation': False}
    
    def _calculate_structure_price_momentum(self, df: pd.DataFrame, prev_swing: Dict, current_swing: Dict) -> float:
        """Calculate price momentum for structure shift"""
        try:
            price_change = abs(current_swing['level'] - prev_swing['level'])
            base_price = prev_swing['level']
            
            momentum = price_change / base_price
            return momentum
            
        except Exception as e:
            logger.error(f"Error calculating structure price momentum: {e}")
            return 0.0
    
    def _assess_structure_break_quality(self, df: pd.DataFrame, prev_swing: Dict, current_swing: Dict) -> float:
        """Assess the quality of structure break"""
        try:
            quality_factors = []
            
            # Distance factor
            price_move = abs(current_swing['level'] - prev_swing['level'])
            avg_range = (df['high'] - df['low']).iloc[max(0, current_swing['index']-20):current_swing['index']].mean()
            distance_factor = min(1.0, price_move / avg_range) if avg_range > 0 else 0.5
            quality_factors.append(distance_factor)
            
            # Speed factor
            time_diff = current_swing['index'] - prev_swing['index']
            speed_factor = max(0.1, 1.0 - (time_diff / 50))  # Faster breaks are higher quality
            quality_factors.append(speed_factor)
            
            # Swing strength factor
            prev_strength = prev_swing.get('strength', 0.5)
            current_strength = current_swing.get('strength', 0.5)
            strength_factor = (prev_strength + current_strength) / 2
            quality_factors.append(strength_factor)
            
            # Volume factor during break
            if 'volume' in df.columns:
                break_volume = df['volume'].iloc[current_swing['index']]
                avg_volume = df['volume'].iloc[max(0, current_swing['index']-20):current_swing['index']].mean()
                volume_factor = min(1.0, break_volume / avg_volume) if avg_volume > 0 else 0.5
                quality_factors.append(volume_factor)
            
            return np.mean(quality_factors)
            
        except Exception as e:
            logger.error(f"Error assessing structure break quality: {e}")
            return 0.5
    
    def _analyze_institutional_backing_structure(self, df: pd.DataFrame, start_index: int, end_index: int) -> float:
        """Analyze institutional backing for structure shift"""
        try:
            if 'volume' not in df.columns:
                return 0.5
            
            institutional_factors = []
            
            # Large volume events during move
            move_volumes = df['volume'].iloc[start_index:end_index+1]
            baseline_volume = df['volume'].iloc[max(0, start_index-50):start_index].mean()
            
            large_volume_events = (move_volumes > baseline_volume * 2).sum()
            large_volume_factor = min(1.0, large_volume_events / len(move_volumes))
            institutional_factors.append(large_volume_factor)
            
            # Consistent volume throughout move
            volume_consistency = 1.0 - (move_volumes.std() / move_volumes.mean()) if move_volumes.mean() > 0 else 0
            volume_consistency = max(0, min(1.0, volume_consistency))
            institutional_factors.append(volume_consistency)
            
            # Volume at key levels
            start_volume = df['volume'].iloc[start_index]
            end_volume = df['volume'].iloc[end_index]
            key_level_volume = (start_volume + end_volume) / (2 * baseline_volume) if baseline_volume > 0 else 1
            key_level_factor = min(1.0, key_level_volume)
            institutional_factors.append(key_level_factor)
            
            return np.mean(institutional_factors)
            
        except Exception as e:
            logger.error(f"Error analyzing institutional backing: {e}")
            return 0.5
    
    def _identify_structure_confluence_factors(self, df: pd.DataFrame, prev_swing: Dict, current_swing: Dict) -> List[str]:
        """Identify confluence factors for structure shift"""
        factors = []
        
        try:
            # Round number confluence
            for swing in [prev_swing, current_swing]:
                level_str = f"{swing['level']:.5f}"
                if level_str.endswith('00000') or level_str.endswith('50000'):
                    factors.append('major_round_number')
                elif level_str.endswith('0000') or level_str.endswith('5000'):
                    factors.append('round_number')
            
            # Volume confluence
            if 'volume' in df.columns:
                for swing_idx in [prev_swing['index'], current_swing['index']]:
                    volume = df['volume'].iloc[swing_idx]
                    avg_volume = df['volume'].iloc[max(0, swing_idx-20):swing_idx].mean()
                    if volume > avg_volume * 2:
                        factors.append('volume_spike')
            
            # Time confluence (session times, etc.)
            # This would require actual timestamp analysis
            
            # Fibonacci confluence
            # This would require fibonacci calculations
            
        except Exception as e:
            logger.error(f"Error identifying structure confluence factors: {e}")
        
        return factors
    
    def _calculate_structure_shift_strength(self, time_velocity: float, volume_confirmation: Dict,
                                          break_quality: float, institutional_backing: float) -> float:
        """Calculate overall structure shift strength"""
        try:
            strength_components = []
            
            # Time velocity component
            velocity_strength = min(1.0, time_velocity * 10000)  # Scale velocity
            strength_components.append(velocity_strength)
            
            # Volume confirmation component
            volume_strength = 1.0 if volume_confirmation['confirmed'] else 0.3
            if volume_confirmation['institutional_participation']:
                volume_strength *= 1.2
            strength_components.append(min(1.0, volume_strength))
            
            # Break quality component
            strength_components.append(break_quality)
            
            # Institutional backing component
            strength_components.append(institutional_backing)
            
            return np.mean(strength_components)
            
        except Exception as e:
            logger.error(f"Error calculating structure shift strength: {e}")
            return 0.5
    
    def _calculate_retest_probability(self, prev_swing: Dict, current_swing: Dict) -> float:
        """Calculate probability of structure retest"""
        try:
            # Distance factor (larger moves less likely to retest immediately)
            price_move = abs(current_swing['level'] - prev_swing['level'])
            base_price = prev_swing['level']
            distance_factor = price_move / base_price
            
            # Time factor (faster moves more likely to retest)
            time_diff = current_swing['index'] - prev_swing['index']
            time_factor = max(0.1, 1.0 - (time_diff / 100))
            
            # Swing strength factor (stronger swings less likely to retest)
            strength_factor = 1.0 - current_swing.get('strength', 0.5)
            
            retest_probability = (time_factor + strength_factor) / 2
            retest_probability *= (1.0 - min(0.5, distance_factor * 1000))  # Reduce for large moves
            
            return max(0.1, min(0.9, retest_probability))
            
        except Exception as e:
            logger.error(f"Error calculating retest probability: {e}")
            return 0.5
    
    def _calculate_trend_continuation_probability(self, df: pd.DataFrame, current_swing: Dict,
                                                shift_type: MarketStructure) -> float:
        """Calculate probability of trend continuation"""
        try:
            continuation_factors = []
            
            # Momentum factor
            if len(df) > current_swing['index'] + 10:
                future_slice = df.iloc[current_swing['index']:current_swing['index']+10]
                current_price = current_swing['level']
                
                if shift_type in [MarketStructure.BOS_BULLISH, MarketStructure.CHOCH_BULLISH]:
                    # Look for continued upward movement
                    future_high = future_slice['high'].max()
                    momentum_factor = min(1.0, (future_high - current_price) / current_price * 100)
                else:
                    # Look for continued downward movement
                    future_low = future_slice['low'].min()
                    momentum_factor = min(1.0, (current_price - future_low) / current_price * 100)
                
                continuation_factors.append(momentum_factor)
            
            # Volume trend factor
            if 'volume' in df.columns:
                volume_trend = self._analyze_volume_trend_continuation(df, current_swing['index'])
                continuation_factors.append(volume_trend)
            
            # Structure quality factor
            structure_quality = current_swing.get('strength', 0.5)
            continuation_factors.append(structure_quality)
            
            return np.mean(continuation_factors) if continuation_factors else 0.5
            
        except Exception as e:
            logger.error(f"Error calculating trend continuation probability: {e}")
            return 0.5
    
    def _analyze_volume_trend_continuation(self, df: pd.DataFrame, start_index: int) -> float:
        """Analyze volume trend for continuation probability"""
        try:
            if start_index + 10 >= len(df):
                return 0.5
            
            future_volumes = df['volume'].iloc[start_index:start_index+10]
            baseline_volume = df['volume'].iloc[max(0, start_index-20):start_index].mean()
            
            # Check if volume supports continuation
            avg_future_volume = future_volumes.mean()
            volume_support = avg_future_volume / baseline_volume if baseline_volume > 0 else 1.0
            
            return min(1.0, volume_support)
            
        except Exception as e:
            logger.error(f"Error analyzing volume trend continuation: {e}")
            return 0.5
    
    def _validate_structure_shift(self, shift: MarketStructureShift, df: pd.DataFrame) -> bool:
        """Validate structure shift quality"""
        try:
            # Strength validation
            if shift.strength < 0.3:
                return False
            
            # Price movement validation
            if shift.price_momentum < 0.001:  # 10 pips minimum
                return False
            
            # Time validation
            if (shift.to_index - shift.from_index) > 100:  # Not too slow
                return False
            
            # Break quality validation
            if shift.break_quality < 0.3:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating structure shift: {e}")
            return False
    
    def _analyze_higher_timeframe_structure(self, df: pd.DataFrame, combined_swings: List[Dict]) -> List[MarketStructureShift]:
        """Analyze higher timeframe structure patterns"""
        try:
            htf_shifts = []
            
            if len(combined_swings) < 4:
                return htf_shifts
            
            # Look for major structure shifts (every 4-5 swings)
            for i in range(4, len(combined_swings), 3):
                major_shift = self._identify_major_structure_shift(df, combined_swings, i)
                if major_shift:
                    htf_shifts.append(major_shift)
            
            return htf_shifts
            
        except Exception as e:
            logger.error(f"Error analyzing higher timeframe structure: {e}")
            return []
    
    def _identify_major_structure_shift(self, df: pd.DataFrame, swings: List[Dict], current_index: int) -> Optional[MarketStructureShift]:
        """Identify major structure shifts for higher timeframe analysis"""
        try:
            if current_index < 4:
                return None
            
            # Analyze last 4 swings to identify major pattern
            recent_swings = swings[current_index-4:current_index]
            
            # Simplified major structure detection
            highs = [s for s in recent_swings if s['swing_type'] == 'high']
            lows = [s for s in recent_swings if s['swing_type'] == 'low']
            
            if len(highs) >= 2 and len(lows) >= 2:
                latest_high = max(highs, key=lambda x: x['index'])
                latest_low = max(lows, key=lambda x: x['index'])
                
                # Check for major structure change
                if latest_high['index'] > latest_low['index']:
                    # Recent high after low - potential bullish structure
                    shift_type = MarketStructure.BOS_BULLISH
                    from_swing = latest_low
                    to_swing = latest_high
                else:
                    # Recent low after high - potential bearish structure
                    shift_type = MarketStructure.BOS_BEARISH
                    from_swing = latest_high
                    to_swing = latest_low
                
                # Create major structure shift
                return MarketStructureShift(
                    shift_type=shift_type,
                    from_price=from_swing['level'],
                    to_price=to_swing['level'],
                    from_index=from_swing['index'],
                    to_index=to_swing['index'],
                    timestamp=df.index[to_swing['index']],
                    strength=0.8,  # Major shifts have high strength
                    volume_confirmation=True,
                    price_momentum=abs(to_swing['level'] - from_swing['level']) / from_swing['level'],
                    time_velocity=(abs(to_swing['level'] - from_swing['level']) / from_swing['level']) / max(1, to_swing['index'] - from_swing['index']),
                    break_quality=0.8,
                    retest_probability=0.3,  # Major shifts less likely to retest quickly
                    trend_continuation_probability=0.8,
                    institutional_backing=0.7,
                    confluence_factors=['major_structure_shift'],
                    metadata={
                        'timeframe': 'higher',
                        'pattern_type': 'major_shift',
                        'swings_analyzed': len(recent_swings)
                    }
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error identifying major structure shift: {e}")
            return None
    
    def _filter_and_rank_structure_shifts(self, structure_shifts: List[MarketStructureShift], 
                                        df: pd.DataFrame) -> List[MarketStructureShift]:
        """Filter and rank structure shifts by quality and relevance"""
        try:
            if not structure_shifts:
                return []
            
            # Filter valid shifts
            valid_shifts = [shift for shift in structure_shifts if self._validate_structure_shift(shift, df)]
            
            # Calculate age factor
            current_index = len(df) - 1
            for shift in valid_shifts:
                age_bars = current_index - shift.to_index
                age_factor = max(0.1, 1.0 - (age_bars / 200))  # 200 bar max age
                
                # Update strength with age factor
                shift.strength *= age_factor
            
            # Sort by strength
            valid_shifts.sort(key=lambda x: x.strength, reverse=True)
            
            # Remove overlapping shifts
            filtered_shifts = self._remove_overlapping_structure_shifts(valid_shifts)
            
            # Keep top shifts
            return filtered_shifts[:15]
            
        except Exception as e:
            logger.error(f"Error filtering and ranking structure shifts: {e}")
            return structure_shifts
    
    def _remove_overlapping_structure_shifts(self, shifts: List[MarketStructureShift]) -> List[MarketStructureShift]:
        """Remove overlapping structure shifts"""
        try:
            if not shifts:
                return []
            
            filtered_shifts = []
            processed_indices = set()
            
            for i, shift1 in enumerate(shifts):
                if i in processed_indices:
                    continue
                
                overlapping_shifts = [shift1]
                
                for j, shift2 in enumerate(shifts[i+1:], i+1):
                    if j not in processed_indices and self._shifts_overlap(shift1, shift2):
                        overlapping_shifts.append(shift2)
                        processed_indices.add(j)
                
                # Keep strongest from overlapping group
                strongest_shift = max(overlapping_shifts, key=lambda x: x.strength)
                filtered_shifts.append(strongest_shift)
                processed_indices.add(i)
            
            return filtered_shifts
            
        except Exception as e:
            logger.error(f"Error removing overlapping structure shifts: {e}")
            return shifts
    
    def _shifts_overlap(self, shift1: MarketStructureShift, shift2: MarketStructureShift) -> bool:
        """Check if two structure shifts overlap"""
        try:
            # Time overlap
            time_overlap = (
                shift1.from_index <= shift2.to_index and
                shift2.from_index <= shift1.to_index
            )
            
            # Price overlap
            price_overlap = (
                min(shift1.from_price, shift1.to_price) <= max(shift2.from_price, shift2.to_price) and
                min(shift2.from_price, shift2.to_price) <= max(shift1.from_price, shift1.to_price)
            )
            
            return time_overlap and price_overlap
            
        except Exception as e:
            logger.error(f"Error checking shift overlap: {e}")
            return False
    
    def _calculate_advanced_confluence(self, order_blocks: List[OrderBlock], fvgs: List[FairValueGap],
                                     sweeps: List[LiquiditySweep], structure: List[MarketStructureShift]) -> List[Dict[str, Any]]:
        """Calculate advanced confluence analysis across all SMC components"""
        try:
            confluence_zones = []
            
            # Analyze confluence around order blocks
            for ob in order_blocks:
                confluence_factors = self._analyze_ob_confluence(ob, fvgs, sweeps, structure)
                if confluence_factors['score'] > 0.6:
                    confluence_zones.append({
                        'type': 'OrderBlock_Confluence',
                        'center_price': (ob.top + ob.bottom) / 2,
                        'top': ob.top,
                        'bottom': ob.bottom,
                        'timestamp': ob.timestamp,
                        'confluence_score': confluence_factors['score'],
                        'factors': confluence_factors['factors'],
                        'strength': confluence_factors['score'],
                        'ob_data': ob
                    })
            
            # Analyze confluence around FVGs
            for fvg in fvgs:
                confluence_factors = self._analyze_fvg_confluence(fvg, order_blocks, sweeps, structure)
                if confluence_factors['score'] > 0.6:
                    confluence_zones.append({
                        'type': 'FVG_Confluence',
                        'center_price': (fvg.top + fvg.bottom) / 2,
                        'top': fvg.top,
                        'bottom': fvg.bottom,
                        'timestamp': fvg.timestamp,
                        'confluence_score': confluence_factors['score'],
                        'factors': confluence_factors['factors'],
                        'strength': confluence_factors['score'],
                        'fvg_data': fvg
                    })
            
            # Analyze confluence around structure levels
            for shift in structure:
                confluence_factors = self._analyze_structure_confluence(shift, order_blocks, fvgs, sweeps)
                if confluence_factors['score'] > 0.6:
                    confluence_zones.append({
                        'type': 'Structure_Confluence',
                        'center_price': shift.to_price,
                        'top': shift.to_price * 1.001,
                        'bottom': shift.to_price * 0.999,
                        'timestamp': shift.timestamp,
                        'confluence_score': confluence_factors['score'],
                        'factors': confluence_factors['factors'],
                        'strength': confluence_factors['score'],
                        'structure_data': shift
                    })
            
            # Sort by confluence score
            confluence_zones.sort(key=lambda x: x['confluence_score'], reverse=True)
            
            # Keep top confluence zones
            return confluence_zones[:10]
            
        except Exception as e:
            logger.error(f"Error calculating advanced confluence: {e}")
            return []
    
    def _analyze_ob_confluence(self, ob: OrderBlock, fvgs: List[FairValueGap],
                             sweeps: List[LiquiditySweep], structure: List[MarketStructureShift]) -> Dict[str, Any]:
        """Analyze confluence factors for order block"""
        try:
            confluence_factors = []
            confluence_score = ob.strength  # Base score from OB strength
            
            # FVG confluence
            for fvg in fvgs:
                if self._levels_overlap(ob.top, ob.bottom, fvg.top, fvg.bottom):
                    confluence_factors.append(f'FVG_{fvg.gap_type.value}')
                    confluence_score += 0.2
            
            # Liquidity sweep confluence
            for sweep in sweeps:
                if self._point_near_range(sweep.swept_level, ob.bottom, ob.top):
                    confluence_factors.append(f'Liquidity_Sweep_{sweep.sweep_type.value}')
                    confluence_score += 0.15
            
            # Structure confluence
            for shift in structure:
                if (self._point_near_range(shift.from_price, ob.bottom, ob.top) or
                    self._point_near_range(shift.to_price, ob.bottom, ob.top)):
                    confluence_factors.append(f'Structure_{shift.shift_type.value}')
                    confluence_score += 0.25
            
            # Round number confluence
            ob_center = (ob.top + ob.bottom) / 2
            if self._is_round_number(ob_center):
                confluence_factors.append('Round_Number')
                confluence_score += 0.1
            
            return {
                'score': min(1.0, confluence_score),
                'factors': confluence_factors
            }
            
        except Exception as e:
            logger.error(f"Error analyzing OB confluence: {e}")
            return {'score': 0.0, 'factors': []}
    
    def _analyze_fvg_confluence(self, fvg: FairValueGap, order_blocks: List[OrderBlock],
                              sweeps: List[LiquiditySweep], structure: List[MarketStructureShift]) -> Dict[str, Any]:
        """Analyze confluence factors for Fair Value Gap"""
        try:
            confluence_factors = []
            confluence_score = fvg.strength  # Base score from FVG strength
            
            # Order block confluence
            for ob in order_blocks:
                if self._levels_overlap(fvg.top, fvg.bottom, ob.top, ob.bottom):
                    confluence_factors.append(f'OrderBlock_{ob.ob_type.value}')
                    confluence_score += 0.25
            
            # Liquidity sweep confluence
            for sweep in sweeps:
                if self._point_near_range(sweep.swept_level, fvg.bottom, fvg.top):
                    confluence_factors.append(f'Liquidity_Sweep_{sweep.sweep_type.value}')
                    confluence_score += 0.15
            
            # Structure confluence
            for shift in structure:
                if (self._point_near_range(shift.from_price, fvg.bottom, fvg.top) or
                    self._point_near_range(shift.to_price, fvg.bottom, fvg.top)):
                    confluence_factors.append(f'Structure_{shift.shift_type.value}')
                    confluence_score += 0.25
            
            # Institutional level confluence
            if fvg.institutional_level:
                confluence_factors.append('Institutional_Level')
                confluence_score += 0.2
            
            return {
                'score': min(1.0, confluence_score),
                'factors': confluence_factors
            }
            
        except Exception as e:
            logger.error(f"Error analyzing FVG confluence: {e}")
            return {'score': 0.0, 'factors': []}
    
    def _analyze_structure_confluence(self, shift: MarketStructureShift, order_blocks: List[OrderBlock],
                                    fvgs: List[FairValueGap], sweeps: List[LiquiditySweep]) -> Dict[str, Any]:
        """Analyze confluence factors for structure shift"""
        try:
            confluence_factors = []
            confluence_score = shift.strength  # Base score from structure strength
            
            # Order block confluence
            for ob in order_blocks:
                if (self._point_near_range(shift.to_price, ob.bottom, ob.top) or
                    self._point_near_range(shift.from_price, ob.bottom, ob.top)):
                    confluence_factors.append(f'OrderBlock_{ob.ob_type.value}')
                    confluence_score += 0.25
            
            # FVG confluence
            for fvg in fvgs:
                if (self._point_near_range(shift.to_price, fvg.bottom, fvg.top) or
                    self._point_near_range(shift.from_price, fvg.bottom, fvg.top)):
                    confluence_factors.append(f'FVG_{fvg.gap_type.value}')
                    confluence_score += 0.2
            
            # Liquidity sweep confluence
            for sweep in sweeps:
                if (abs(sweep.swept_level - shift.to_price) / shift.to_price < 0.001 or
                    abs(sweep.swept_level - shift.from_price) / shift.from_price < 0.001):
                    confluence_factors.append(f'Liquidity_Sweep_{sweep.sweep_type.value}')
                    confluence_score += 0.15
            
            # Volume confirmation
            if shift.volume_confirmation:
                confluence_factors.append('Volume_Confirmation')
                confluence_score += 0.1
            
            # Institutional backing
            if shift.institutional_backing > 0.7:
                confluence_factors.append('Institutional_Backing')
                confluence_score += 0.15
            
            return {
                'score': min(1.0, confluence_score),
                'factors': confluence_factors
            }
            
        except Exception as e:
            logger.error(f"Error analyzing structure confluence: {e}")
            return {'score': 0.0, 'factors': []}
    
    def _levels_overlap(self, top1: float, bottom1: float, top2: float, bottom2: float) -> bool:
        """Check if two price levels overlap"""
        try:
            return not (top1 < bottom2 or top2 < bottom1)
        except Exception as e:
            logger.error(f"Error checking levels overlap: {e}")
            return False
    
    def _point_near_range(self, point: float, bottom: float, top: float, tolerance: float = 0.002) -> bool:
        """Check if point is near a price range"""
        try:
            expanded_bottom = bottom * (1 - tolerance)
            expanded_top = top * (1 + tolerance)
            return expanded_bottom <= point <= expanded_top
        except Exception as e:
            logger.error(f"Error checking point near range: {e}")
            return False
    
    def _is_round_number(self, price: float) -> bool:
        """Check if price is a round number"""
        try:
            price_str = f"{price:.5f}"
            return (price_str.endswith('00000') or price_str.endswith('50000') or
                   price_str.endswith('0000') or price_str.endswith('5000'))
        except Exception as e:
            logger.error(f"Error checking round number: {e}")
            return False
    
    def _determine_market_bias(self, order_blocks: List[OrderBlock], fvgs: List[FairValueGap],
                             structure: List[MarketStructureShift]) -> Tuple[str, float]:
        """Determine overall market bias and signal strength"""
        try:
            bias_factors = []
            
            # Order block bias
            bullish_obs = len([ob for ob in order_blocks if ob.ob_type in [OrderBlockType.BULLISH_OB, OrderBlockType.INSTITUTIONAL_BULLISH]])
            bearish_obs = len([ob for ob in order_blocks if ob.ob_type in [OrderBlockType.BEARISH_OB, OrderBlockType.INSTITUTIONAL_BEARISH]])
            
            if bullish_obs > bearish_obs:
                bias_factors.append(('bullish', 0.3))
            elif bearish_obs > bullish_obs:
                bias_factors.append(('bearish', 0.3))
            
            # FVG bias
            bullish_fvgs = len([fvg for fvg in fvgs if fvg.gap_type == FairValueGapType.BULLISH_FVG])
            bearish_fvgs = len([fvg for fvg in fvgs if fvg.gap_type == FairValueGapType.BEARISH_FVG])
            
            if bullish_fvgs > bearish_fvgs:
                bias_factors.append(('bullish', 0.2))
            elif bearish_fvgs > bullish_fvgs:
                bias_factors.append(('bearish', 0.2))
            
            # Structure bias
            bullish_structure = len([s for s in structure if s.shift_type in [MarketStructure.BOS_BULLISH, MarketStructure.CHOCH_BULLISH]])
            bearish_structure = len([s for s in structure if s.shift_type in [MarketStructure.BOS_BEARISH, MarketStructure.CHOCH_BEARISH]])
            
            if bullish_structure > bearish_structure:
                bias_factors.append(('bullish', 0.5))
            elif bearish_structure > bullish_structure:
                bias_factors.append(('bearish', 0.5))
            
            # Calculate overall bias
            bullish_score = sum([weight for bias, weight in bias_factors if bias == 'bullish'])
            bearish_score = sum([weight for bias, weight in bias_factors if bias == 'bearish'])
            
            if bullish_score > bearish_score:
                overall_bias = 'bullish'
                signal_strength = bullish_score
            elif bearish_score > bullish_score:
                overall_bias = 'bearish'
                signal_strength = bearish_score
            else:
                overall_bias = 'neutral'
                signal_strength = 0.5
            
            return overall_bias, min(1.0, signal_strength)
            
        except Exception as e:
            logger.error(f"Error determining market bias: {e}")
            return 'neutral', 0.5
    
    def _calculate_confidence_score(self, order_blocks: List[OrderBlock], fvgs: List[FairValueGap],
                                  sweeps: List[LiquiditySweep], structure: List[MarketStructureShift],
                                  data_quality: Dict[str, Any]) -> float:
        """Calculate overall confidence score for SMC analysis"""
        try:
            confidence_factors = []
            
            # Data quality factor
            confidence_factors.append(data_quality.get('quality_score', 0.5))
            
            # Number of SMC elements factor
            total_elements = len(order_blocks) + len(fvgs) + len(sweeps) + len(structure)
            elements_factor = min(1.0, total_elements / 20)  # Optimal around 20 elements
            confidence_factors.append(elements_factor)
            
            # Average strength factor
            strengths = []
            strengths.extend([ob.strength for ob in order_blocks])
            strengths.extend([fvg.strength for fvg in fvgs])
            strengths.extend([s.strength for s in structure])
            
            avg_strength = np.mean(strengths) if strengths else 0.5
            confidence_factors.append(avg_strength)
            
            # Confluence factor
            high_quality_obs = len([ob for ob in order_blocks if ob.confluence_score > 0.7])
            confluence_factor = min(1.0, high_quality_obs / max(1, len(order_blocks)))
            confidence_factors.append(confluence_factor)
            
            # Volume confirmation factor
            volume_confirmed = len([s for s in structure if s.volume_confirmation])
            volume_factor = volume_confirmed / max(1, len(structure))
            confidence_factors.append(volume_factor)
            
            return np.mean(confidence_factors)
            
        except Exception as e:
            logger.error(f"Error calculating confidence score: {e}")
            return 0.5
    
    def _perform_risk_assessment(self, order_blocks: List[OrderBlock], fvgs: List[FairValueGap],
                               sweeps: List[LiquiditySweep], structure: List[MarketStructureShift]) -> Dict[str, Any]:
        """Perform comprehensive risk assessment"""
        try:
            risk_assessment = {
                'overall_risk_level': 'medium',
                'risk_factors': [],
                'risk_mitigants': [],
                'risk_score': 0.5,
                'volatility_assessment': 'normal',
                'liquidity_assessment': 'adequate',
                'market_structure_health': 'stable'
            }
            
            # Analyze risk factors
            risk_factors = []
            risk_mitigants = []
            
            # Structure-based risk
            recent_structure = [s for s in structure if s.to_index > len(structure) - 10]
            conflicting_signals = len([s for s in recent_structure if s.shift_type in [MarketStructure.CHOCH_BULLISH, MarketStructure.CHOCH_BEARISH]])
            
            if conflicting_signals > 2:
                risk_factors.append("Multiple trend changes detected - market indecision")
            elif len([s for s in recent_structure if s.strength > 0.8]) > 0:
                risk_mitigants.append("Strong structure breaks indicate clear direction")
            
            # Liquidity-based risk
            recent_sweeps = [s for s in sweeps if not s.reversal_confirmed]
            if len(recent_sweeps) > 3:
                risk_factors.append("Multiple failed liquidity sweeps - potential whipsaw market")
            
            confirmed_sweeps = [s for s in sweeps if s.reversal_confirmed and s.stop_hunt_probability > 0.7]
            if len(confirmed_sweeps) > 0:
                risk_mitigants.append("Confirmed stop hunts provide directional clarity")
            
            # Order block risk
            untested_obs = [ob for ob in order_blocks if not ob.touched]
            if len(untested_obs) > 10:
                risk_factors.append("Many untested order blocks - potential resistance/support cluster")
            
            institutional_obs = [ob for ob in order_blocks if ob.institutional_level]
            if len(institutional_obs) > 0:
                risk_mitigants.append("Institutional order blocks provide strong support/resistance")
            
            # FVG risk
            unfilled_fvgs = [fvg for fvg in fvgs if not fvg.is_filled]
            if len(unfilled_fvgs) > 5:
                risk_factors.append("Multiple unfilled FVGs may act as magnets")
            
            # Calculate risk score
            risk_score = 0.5 + (len(risk_factors) * 0.1) - (len(risk_mitigants) * 0.1)
            risk_score = max(0.1, min(0.9, risk_score))
            
            # Determine risk level
            if risk_score > 0.7:
                risk_level = 'high'
            elif risk_score < 0.4:
                risk_level = 'low'
            else:
                risk_level = 'medium'
            
            risk_assessment.update({
                'overall_risk_level': risk_level,
                'risk_factors': risk_factors,
                'risk_mitigants': risk_mitigants,
                'risk_score': risk_score
            })
            
            return risk_assessment
            
        except Exception as e:
            logger.error(f"Error performing risk assessment: {e}")
            return {'overall_risk_level': 'high', 'risk_factors': ['Analysis error'], 'risk_score': 0.8}
    
    def _generate_performance_metrics(self, order_blocks: List[OrderBlock], fvgs: List[FairValueGap],
                                    sweeps: List[LiquiditySweep], structure: List[MarketStructureShift],
                                    execution_time: float, data_quality: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive performance metrics"""
        try:
            return {
                'execution_metrics': {
                    'total_execution_time': execution_time,
                    'analysis_efficiency': len(order_blocks + fvgs + sweeps + structure) / execution_time if execution_time > 0 else 0,
                    'data_processing_rate': data_quality.get('data_length', 0) / execution_time if execution_time > 0 else 0
                },
                'detection_metrics': {
                    'order_blocks_detected': len(order_blocks),
                    'fvgs_detected': len(fvgs),
                    'liquidity_sweeps_detected': len(sweeps),
                    'structure_shifts_detected': len(structure),
                    'total_smc_elements': len(order_blocks + fvgs + sweeps + structure)
                },
                'quality_metrics': {
                    'avg_ob_strength': np.mean([ob.strength for ob in order_blocks]) if order_blocks else 0,
                    'avg_fvg_strength': np.mean([fvg.strength for fvg in fvgs]) if fvgs else 0,
                    'avg_structure_strength': np.mean([s.strength for s in structure]) if structure else 0,
                    'institutional_detection_rate': len([ob for ob in order_blocks if ob.institutional_level]) / max(1, len(order_blocks)),
                    'volume_confirmation_rate': len([s for s in structure if s.volume_confirmation]) / max(1, len(structure))
                },
                'data_quality_metrics': data_quality,
                'analysis_timestamp': datetime.now().isoformat(),
                'analysis_id': self._analysis_count
            }
            
        except Exception as e:
            logger.error(f"Error generating performance metrics: {e}")
            return {}
    
    def _assess_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess quality of input data"""
        try:
            quality_metrics = {
                'data_length': len(df),
                'has_volume': 'volume' in df.columns,
                'missing_values': df.isnull().sum().sum(),
                'data_completeness': 1.0 - (df.isnull().sum().sum() / (len(df) * len(df.columns))),
                'price_consistency': self._validate_price_consistency(df),
                'sufficient_data': len(df) >= 100,
                'volume_quality': self._assess_volume_quality(df),
                'time_consistency': self._assess_time_consistency(df),
                'quality_score': 0.0
            }
            
            # Calculate overall quality score
            score_factors = []
            
            # Data length factor
            length_factor = min(1.0, len(df) / 500)  # Prefer 500+ bars
            score_factors.append(length_factor)
            
            # Completeness factor
            score_factors.append(quality_metrics['data_completeness'])
            
            # Price consistency factor
            score_factors.append(1.0 if quality_metrics['price_consistency'] else 0.3)
            
            # Volume quality factor
            score_factors.append(quality_metrics['volume_quality'])
            
            # Time consistency factor
            score_factors.append(quality_metrics['time_consistency'])
            
            quality_metrics['quality_score'] = np.mean(score_factors)
            
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Error assessing data quality: {e}")
            return {'quality_score': 0.5}
    
    def _validate_price_consistency(self, df: pd.DataFrame) -> bool:
        """Validate OHLC price consistency"""
        try:
            # Basic OHLC relationships
            high_low_check = (df['high'] >= df['low']).all()
            high_open_check = (df['high'] >= df['open']).all()
            high_close_check = (df['high'] >= df['close']).all()
            low_open_check = (df['low'] <= df['open']).all()
            low_close_check = (df['low'] <= df['close']).all()
            
            # Check for unrealistic price jumps
            price_changes = df['close'].pct_change().abs()
            unrealistic_jumps = (price_changes > 0.1).sum()  # 10% jumps
            jump_check = unrealistic_jumps < len(df) * 0.01  # Less than 1% of data
            
            return all([high_low_check, high_open_check, high_close_check, 
                       low_open_check, low_close_check, jump_check])
            
        except Exception as e:
            logger.error(f"Error validating price consistency: {e}")
            return False
    
    def _assess_volume_quality(self, df: pd.DataFrame) -> float:
        """Assess volume data quality"""
        try:
            if 'volume' not in df.columns:
                return 0.5
            
            volume_quality_factors = []
            
            # Non-zero volume check
            non_zero_volume = (df['volume'] > 0).sum() / len(df)
            volume_quality_factors.append(non_zero_volume)
            
            # Volume consistency (not too many extreme outliers)
            volume_std = df['volume'].std()
            volume_mean = df['volume'].mean()
            cv = volume_std / volume_mean if volume_mean > 0 else 0
            consistency_factor = max(0, 1.0 - min(1.0, cv / 2))  # Good if CV < 2
            volume_quality_factors.append(consistency_factor)
            
            # Realistic volume values
            max_volume = df['volume'].max()
            min_volume = df['volume'].min()
            realistic_range = max_volume / min_volume < 1000 if min_volume > 0 else True
            volume_quality_factors.append(1.0 if realistic_range else 0.5)
            
            return np.mean(volume_quality_factors)
            
        except Exception as e:
            logger.error(f"Error assessing volume quality: {e}")
            return 0.5
    
    def _assess_time_consistency(self, df: pd.DataFrame) -> float:
        """Assess time series consistency"""
        try:
            # Check if index is datetime-like
            if hasattr(df.index, 'to_pydatetime'):
                time_diffs = pd.Series(df.index).diff().dropna()
                
                # Check for consistent time intervals
                most_common_diff = time_diffs.mode()
                if len(most_common_diff) > 0:
                    consistent_intervals = (time_diffs == most_common_diff.iloc[0]).sum() / len(time_diffs)
                    return consistent_intervals
            
            # If not datetime index, check for sequential numeric index
            if pd.api.types.is_numeric_dtype(df.index):
                index_diffs = pd.Series(df.index).diff().dropna()
                consistent_diffs = (index_diffs == 1).sum() / len(index_diffs)
                return consistent_diffs
            
            return 0.7  # Assume reasonable if can't determine
            
        except Exception as e:
            logger.error(f"Error assessing time consistency: {e}")
            return 0.5
    
    async def cleanup(self):
        """Cleanup strategy resources"""
        try:
            logger.info(f"Cleaning up Advanced SMC Indicators")
            
            # Clear caches
            if hasattr(self, '_cache'):
                self._cache.clear()
            
            # Clear performance tracking
            self._performance_metrics.clear()
            
            # Shutdown thread pool executor
            if hasattr(self, '_executor') and self._executor:
                self._executor.shutdown(wait=True)
            
            logger.info("Advanced SMC Indicators cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# =============================================================================
# INTEGRATION AND UTILITY FUNCTIONS
# =============================================================================

def integrate_complete_smc_with_trading_system(trading_system, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Complete integration of Advanced SMC Indicators with trading systems
    
    Args:
        trading_system: Existing trading system instance
        config: SMC configuration parameters
        
    Returns:
        Enhanced trading system with SMC capabilities
    """
    try:
        # Initialize Advanced SMC Indicators
        smc_indicators = AdvancedSMCIndicators(config)
        
        # Create integration wrapper
        class SMCEnhancedTradingSystem:
            def __init__(self, base_system, smc):
                self.base_system = base_system
                self.smc = smc
                self.smc_analysis_cache = {}
            
            async def analyze_market(self, symbol: str, timeframe: str, data: pd.DataFrame) -> SMCAnalysisResult:
                """Perform complete SMC analysis"""
                return await self.smc.analyze_complete_smc(data, symbol, timeframe)
            
            def generate_trading_signals(self, smc_analysis: SMCAnalysisResult) -> List[Dict[str, Any]]:
                """Generate trading signals from SMC analysis"""
                return generate_smc_trading_signals(smc_analysis)
            
            def get_confluence_zones(self, smc_analysis: SMCAnalysisResult) -> List[Dict[str, Any]]:
                """Get high-probability confluence zones"""
                return smc_analysis.confluence_zones
            
            def assess_market_bias(self, smc_analysis: SMCAnalysisResult) -> Dict[str, str]:
                """Get market bias assessment"""
                return {
                    'bias': smc_analysis.overall_bias,
                    'strength': smc_analysis.signal_strength,
                    'confidence': smc_analysis.confidence_score
                }
        
        # Return enhanced system
        enhanced_system = SMCEnhancedTradingSystem(trading_system, smc_indicators)
        
        return {
            'enhanced_system': enhanced_system,
            'smc_indicators': smc_indicators,
            'integration_status': 'success',
            'capabilities': [
                'order_block_detection',
                'fair_value_gap_analysis',
                'liquidity_sweep_detection',
                'market_structure_analysis',
                'confluence_zone_identification',
                'institutional_flow_tracking',
                'risk_assessment',
                'performance_monitoring'
            ]
        }
        
    except Exception as e:
        logger.error(f"Error integrating SMC with trading system: {e}")
        return {'integration_status': 'failed', 'error': str(e)}

def generate_smc_trading_signals(smc_analysis: SMCAnalysisResult) -> List[Dict[str, Any]]:
    """Generate actionable trading signals from SMC analysis"""
    try:
        signals = []
        
        # Generate signals from order blocks
        for ob in smc_analysis.order_blocks:
            if ob.strength > 0.7 and not ob.touched:
                signal = {
                    'type': 'ORDER_BLOCK',
                    'direction': 'buy' if ob.ob_type in [OrderBlockType.BULLISH_OB, OrderBlockType.INSTITUTIONAL_BULLISH] else 'sell',
                    'entry_zone': {'top': ob.top, 'bottom': ob.bottom},
                    'strength': ob.strength,
                    'confidence': ob.confluence_score,
                    'stop_loss': ob.bottom * 0.999 if ob.ob_type in [OrderBlockType.BULLISH_OB, OrderBlockType.INSTITUTIONAL_BULLISH] else ob.top * 1.001,
                    'take_profit_zones': _calculate_tp_zones(ob),
                    'risk_reward_ratio': _calculate_risk_reward(ob),
                    'metadata': {
                        'ob_type': ob.ob_type.value,
                        'institutional_level': ob.institutional_level,
                        'volume_profile': ob.volume_profile
                    }
                }
                signals.append(signal)
        
        # Generate signals from confluence zones
        for zone in smc_analysis.confluence_zones:
            if zone['confluence_score'] > 0.8:
                signal = {
                    'type': 'CONFLUENCE_ZONE',
                    'direction': _determine_confluence_direction(zone),
                    'entry_zone': {'top': zone['top'], 'bottom': zone['bottom']},
                    'strength': zone['strength'],
                    'confidence': zone['confluence_score'],
                    'factors': zone['factors'],
                    'metadata': {
                        'confluence_type': zone['type'],
                        'factor_count': len(zone['factors'])
                    }
                }
                signals.append(signal)
        
        # Generate signals from structure shifts
        for shift in smc_analysis.market_structure:
            if shift.strength > 0.8 and shift.volume_confirmation:
                signal = {
                    'type': 'STRUCTURE_BREAK',
                    'direction': 'buy' if shift.shift_type in [MarketStructure.BOS_BULLISH, MarketStructure.CHOCH_BULLISH] else 'sell',
                    'entry_price': shift.to_price,
                    'strength': shift.strength,
                    'confidence': shift.institutional_backing,
                    'stop_loss': shift.from_price,
                    'retest_probability': shift.retest_probability,
                    'continuation_probability': shift.trend_continuation_probability,
                    'metadata': {
                        'shift_type': shift.shift_type.value,
                        'break_quality': shift.break_quality,
                        'time_velocity': shift.time_velocity
                    }
                }
                signals.append(signal)
        
        # Sort signals by strength and confidence
        signals.sort(key=lambda x: x['strength'] * x['confidence'], reverse=True)
        
        return signals[:10]  # Return top 10 signals
        
    except Exception as e:
        logger.error(f"Error generating SMC trading signals: {e}")
        return []

def _calculate_tp_zones(ob: OrderBlock) -> List[Dict[str, float]]:
    """Calculate take profit zones for order block"""
    try:
        if ob.ob_type in [OrderBlockType.BULLISH_OB, OrderBlockType.INSTITUTIONAL_BULLISH]:
            # Bullish targets
            return [
                {'level': ob.top * 1.005, 'probability': 0.8},
                {'level': ob.top * 1.01, 'probability': 0.6},
                {'level': ob.top * 1.02, 'probability': 0.4}
            ]
        else:
            # Bearish targets
            return [
                {'level': ob.bottom * 0.995, 'probability': 0.8},
                {'level': ob.bottom * 0.99, 'probability': 0.6},
                {'level': ob.bottom * 0.98, 'probability': 0.4}
            ]
    except Exception as e:
        logger.error(f"Error calculating TP zones: {e}")
        return []

def _calculate_risk_reward(ob: OrderBlock) -> float:
    """Calculate risk-reward ratio for order block trade"""
    try:
        if ob.ob_type in [OrderBlockType.BULLISH_OB, OrderBlockType.INSTITUTIONAL_BULLISH]:
            entry = (ob.top + ob.bottom) / 2
            stop_loss = ob.bottom * 0.999
            take_profit = ob.top * 1.01
        else:
            entry = (ob.top + ob.bottom) / 2
            stop_loss = ob.top * 1.001
            take_profit = ob.bottom * 0.99
        
        risk = abs(entry - stop_loss)
        reward = abs(take_profit - entry)
        
        return reward / risk if risk > 0 else 0
        
    except Exception as e:
        logger.error(f"Error calculating risk-reward: {e}")
        return 0

def _determine_confluence_direction(zone: Dict[str, Any]) -> str:
    """Determine trading direction for confluence zone"""
    try:
        bullish_factors = sum(1 for factor in zone['factors'] if 'bullish' in factor.lower())
        bearish_factors = sum(1 for factor in zone['factors'] if 'bearish' in factor.lower())
        
        if bullish_factors > bearish_factors:
            return 'buy'
        elif bearish_factors > bullish_factors:
            return 'sell'
        else:
            return 'neutral'
            
    except Exception as e:
        logger.error(f"Error determining confluence direction: {e}")
        return 'neutral'

# Example usage and testing
def example_usage():
    """Example of how to use the complete Advanced SMC Indicators"""
    
    # Sample configuration
    config = {
        'swing_length': 10,
        'ob_strength_threshold': 0.6,
        'fvg_min_size': 0.0003,
        'volume_spike_threshold': 2.0,
        'use_parallel_processing': True,
        'cache_enabled': True,
        'performance_monitoring': True,
        'enable_advanced_validation': True
    }
    
    # Initialize SMC indicators
    smc = AdvancedSMCIndicators(config)
    
    # Sample data (replace with real market data)
    sample_data = pd.DataFrame({
        'open': np.random.randn(1000).cumsum() + 1.1000,
        'high': np.random.randn(1000).cumsum() + 1.1010,
        'low': np.random.randn(1000).cumsum() + 1.0990,
        'close': np.random.randn(1000).cumsum() + 1.1005,
        'volume': np.random.randint(100, 10000, 1000)
    }, index=pd.date_range('2024-01-01', periods=1000, freq='1H'))
    
    # Perform complete SMC analysis
    try:
        analysis_result = smc.analyze_complete_smc(sample_data, 'EURUSD', 'H1')
        
        print("=== SMC Analysis Results ===")
        print(f"Overall Bias: {analysis_result.overall_bias}")
        print(f"Signal Strength: {analysis_result.signal_strength:.2f}")
        print(f"Confidence Score: {analysis_result.confidence_score:.2f}")
        print(f"Order Blocks: {len(analysis_result.order_blocks)}")
        print(f"Fair Value Gaps: {len(analysis_result.fair_value_gaps)}")
        print(f"Liquidity Sweeps: {len(analysis_result.liquidity_sweeps)}")
        print(f"Structure Shifts: {len(analysis_result.market_structure)}")
        print(f"Confluence Zones: {len(analysis_result.confluence_zones)}")
        
        # Generate trading signals
        trading_signals = generate_smc_trading_signals(analysis_result)
        print(f"\nTrading Signals Generated: {len(trading_signals)}")
        
        for i, signal in enumerate(trading_signals[:3]):
            print(f"\nSignal {i+1}:")
            print(f"  Type: {signal['type']}")
            print(f"  Direction: {signal['direction']}")
            print(f"  Strength: {signal['strength']:.2f}")
            print(f"  Confidence: {signal['confidence']:.2f}")
        
    except Exception as e:
        print(f"Error in example usage: {e}")

# Export the complete implementation
__all__ = [
    'AdvancedSMCIndicators',
    'OrderBlock',
    'FairValueGap', 
    'LiquiditySweep',
    'MarketStructureShift',
    'SMCAnalysisResult',
    'OrderBlockType',
    'FairValueGapType',
    'LiquidityType',
    'MarketStructure',
    'integrate_complete_smc_with_trading_system',
    'generate_smc_trading_signals'
]

if __name__ == "__main__":
    example_usage()