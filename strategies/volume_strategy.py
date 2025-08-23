"""
Enhanced Volume Strategy Implementation
======================================
Professional-grade volume-based trading strategy with advanced analytics,
multi-timeframe analysis, and comprehensive risk management.

Features:
- Multiple volume analysis methodologies (OBV, VWAP, Volume Profile, etc.)
- Advanced volume pattern recognition and validation
- Multi-timeframe volume confluence analysis
- Market maker vs retail volume detection
- Volume-based support/resistance identification
- Institutional flow analysis and smart money tracking
- Advanced signal filtering and validation
- Comprehensive risk management integration
- Real-time performance monitoring and analytics
"""

# CRITICAL FIX: Add all missing typing imports
from typing import Dict, Any, Optional, List, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import logging
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import warnings
from collections import defaultdict, deque
from scipy import stats
import math

# Import base strategy and event system
from base_strategy import BaseStrategy, SignalEvent, register_strategy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')

class VolumeAnalysisType(Enum):
    """Types of volume analysis methodologies"""
    ON_BALANCE_VOLUME = "on_balance_volume"
    VOLUME_WEIGHTED_AVERAGE_PRICE = "vwap"
    VOLUME_PROFILE = "volume_profile"
    ACCUMULATION_DISTRIBUTION = "accumulation_distribution"
    VOLUME_OSCILLATOR = "volume_oscillator"
    MONEY_FLOW_INDEX = "money_flow_index"
    CHAIKIN_MONEY_FLOW = "chaikin_money_flow"
    VOLUME_SPREAD_ANALYSIS = "volume_spread_analysis"
    INSTITUTIONAL_FLOW = "institutional_flow"

class VolumeCondition(Enum):
    """Volume market conditions"""
    HIGH_VOLUME = "high_volume"
    LOW_VOLUME = "low_volume"
    VOLUME_SURGE = "volume_surge"
    VOLUME_CLIMAX = "volume_climax"
    VOLUME_DRYING_UP = "volume_drying_up"
    VOLUME_CONFIRMATION = "volume_confirmation"
    VOLUME_DIVERGENCE = "volume_divergence"

class VolumeSignalType(Enum):
    """Types of volume-based signals"""
    VOLUME_BREAKOUT = "volume_breakout"
    VOLUME_REVERSAL = "volume_reversal"
    INSTITUTIONAL_ACCUMULATION = "institutional_accumulation"
    INSTITUTIONAL_DISTRIBUTION = "institutional_distribution"
    SMART_MONEY_FLOW = "smart_money_flow"
    RETAIL_EXHAUSTION = "retail_exhaustion"

class VolumeDataType(Enum):
    """Volume data types available"""
    TICK_VOLUME = "tick_volume"
    REAL_VOLUME = "real_volume"
    MIXED_VOLUME = "mixed_volume"

@dataclass
class VolumeAnalysis:
    """Enhanced volume analysis with comprehensive metadata"""
    timestamp: datetime
    symbol: str
    timeframe: str
    volume_type: VolumeDataType
    current_volume: float
    average_volume: float
    volume_ratio: float
    volume_trend: str
    volume_condition: VolumeCondition
    obv_value: float
    vwap_value: float
    money_flow: float
    accumulation_distribution: float
    volume_oscillator: float
    institutional_flow_score: float
    retail_flow_score: float
    volume_profile_poc: float  # Point of Control
    volume_profile_vah: float  # Value Area High
    volume_profile_val: float  # Value Area Low
    support_levels: List[float]
    resistance_levels: List[float]
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class VolumeSignal:
    """Enhanced volume signal with comprehensive analysis"""
    timestamp: datetime
    symbol: str
    timeframe: str
    direction: str  # 'bullish', 'bearish'
    strength: float  # 0.0 to 1.0
    signal_type: VolumeSignalType
    analysis_type: VolumeAnalysisType
    entry_price: float
    target_price: float
    stop_loss: float
    volume_confirmation: bool
    institutional_backing: bool
    retail_sentiment: str
    expected_move: float
    confidence: float
    risk_reward_ratio: float
    volume_analysis: VolumeAnalysis
    supporting_factors: List[str]
    risk_factors: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

@register_strategy
class EnhancedVolumeStrategy(BaseStrategy):
    """
    Enhanced Volume Strategy - Professional Implementation
    
    Advanced volume-driven strategy incorporating multiple volume analysis
    methodologies, institutional flow detection, and sophisticated pattern
    recognition for institutional-grade trading applications.
    
    Key Features:
    - Multi-dimensional volume analysis
    - Institutional vs retail flow detection
    - Volume-based support/resistance
    - Smart money tracking
    - Advanced pattern recognition
    - Comprehensive risk management
    - Real-time performance tracking
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize enhanced volume strategy
        
        Args:
            name: Strategy name
            config: Configuration dictionary with strategy parameters
        """
        super().__init__(name, config)
        
        # Core volume analysis parameters
        self.analysis_types = config.get('analysis_types', [
            VolumeAnalysisType.ON_BALANCE_VOLUME,
            VolumeAnalysisType.VOLUME_WEIGHTED_AVERAGE_PRICE,
            VolumeAnalysisType.VOLUME_PROFILE,
            VolumeAnalysisType.INSTITUTIONAL_FLOW
        ])
        self.primary_analysis_type = config.get('primary_analysis_type', VolumeAnalysisType.ON_BALANCE_VOLUME)
        
        # Volume data configuration
        self.volume_data_type = config.get('volume_data_type', VolumeDataType.TICK_VOLUME)
        self.prefer_real_volume = config.get('prefer_real_volume', True)
        self.fallback_to_tick_volume = config.get('fallback_to_tick_volume', True)
        
        # Volume threshold parameters
        self.high_volume_threshold = config.get('high_volume_threshold', 2.0)  # 2x average
        self.low_volume_threshold = config.get('low_volume_threshold', 0.5)   # 0.5x average
        self.volume_surge_threshold = config.get('volume_surge_threshold', 3.0)  # 3x average
        self.min_volume_confirmation = config.get('min_volume_confirmation', 1.2)  # 1.2x average
        
        # Multi-timeframe analysis
        self.timeframes = config.get('timeframes', ['M15', 'H1', 'H4', 'D1'])
        self.primary_timeframe = config.get('primary_timeframe', 'H1')
        self.volume_lookback = config.get('volume_lookback', 50)
        
        # VWAP parameters
        self.vwap_period = config.get('vwap_period', 20)
        self.vwap_bands_multiplier = config.get('vwap_bands_multiplier', 2.0)
        
        # OBV parameters
        self.obv_smoothing_period = config.get('obv_smoothing_period', 10)
        self.obv_signal_period = config.get('obv_signal_period', 5)
        
        # Money Flow parameters
        self.mfi_period = config.get('mfi_period', 14)
        self.mfi_overbought = config.get('mfi_overbought', 80)
        self.mfi_oversold = config.get('mfi_oversold', 20)
        
        # Volume Profile parameters
        self.vp_sessions = config.get('vp_sessions', 24)  # 24-hour sessions
        self.vp_value_area = config.get('vp_value_area', 0.70)  # 70% value area
        
        # Institutional flow detection
        self.large_order_threshold = config.get('large_order_threshold', 5.0)  # 5x average
        self.institutional_window = config.get('institutional_window', 20)
        self.smart_money_threshold = config.get('smart_money_threshold', 0.7)
        
        # Signal generation parameters
        self.min_signal_strength = config.get('min_signal_strength', 0.6)
        self.volume_divergence_threshold = config.get('volume_divergence_threshold', 0.3)
        self.confluence_requirement = config.get('confluence_requirement', 2)  # Min 2 confirmations
        
        # Risk management parameters
        self.max_position_size = config.get('max_position_size', 0.02)
        self.volume_stop_loss_multiplier = config.get('volume_stop_loss_multiplier', 1.5)
        self.volume_take_profit_ratio = config.get('volume_take_profit_ratio', 2.0)
        
        # Advanced features
        self.enable_institutional_detection = config.get('enable_institutional_detection', True)
        self.enable_volume_profile = config.get('enable_volume_profile', True)
        self.enable_smart_money_tracking = config.get('enable_smart_money_tracking', True)
        self.enable_retail_sentiment = config.get('enable_retail_sentiment', True)
        
        # Performance tracking
        self.volume_history = deque(maxlen=5000)
        self.signal_history = deque(maxlen=1000)
        self.performance_metrics = defaultdict(list)
        self.institutional_flow_tracking = defaultdict(list)
        
        # Signal filtering parameters
        self.max_signals_per_day = config.get('max_signals_per_day', 5)
        self.min_time_between_signals = config.get('min_time_between_signals', 120)  # minutes
        
        logger.info(f"Enhanced Volume Strategy '{name}' initialized successfully")
        logger.info(f"Configuration: {self._log_safe_config()}")
    
    def _log_safe_config(self) -> Dict[str, Any]:
        """Create logging-safe configuration summary"""
        return {
            'analysis_types': len(self.analysis_types),
            'volume_data_type': self.volume_data_type.value,
            'high_volume_threshold': self.high_volume_threshold,
            'timeframes': len(self.timeframes),
            'enable_institutional_detection': self.enable_institutional_detection,
            'min_signal_strength': self.min_signal_strength
        }
    
    async def initialize(self) -> bool:
        """Initialize strategy with enhanced setup"""
        try:
            logger.info(f"Initializing Enhanced Volume Strategy: {self.name}")
            
            # Validate configuration
            if not self._validate_configuration():
                logger.error("Configuration validation failed")
                return False
            
            # Initialize volume analyzers
            self._initialize_volume_analyzers()
            
            # Setup institutional flow detection
            self._setup_institutional_detection()
            
            # Initialize volume profile
            self._setup_volume_profile()
            
            # Setup performance monitoring
            self._setup_performance_monitoring()
            
            logger.info("Enhanced Volume Strategy initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing Enhanced Volume Strategy: {e}")
            return False
    
    def _validate_configuration(self) -> bool:
        """Validate strategy configuration parameters"""
        try:
            # Validate analysis types
            if not self.analysis_types:
                logger.error("No analysis types specified")
                return False
            
            if self.primary_analysis_type not in self.analysis_types:
                logger.error(f"Primary analysis type {self.primary_analysis_type} not in analysis types list")
                return False
            
            # Validate volume thresholds
            if self.high_volume_threshold <= 1.0:
                logger.error(f"Invalid high_volume_threshold: {self.high_volume_threshold}")
                return False
            
            if not (0.1 <= self.low_volume_threshold < 1.0):
                logger.error(f"Invalid low_volume_threshold: {self.low_volume_threshold}")
                return False
            
            if self.volume_surge_threshold <= self.high_volume_threshold:
                logger.error(f"Invalid volume_surge_threshold: {self.volume_surge_threshold}")
                return False
            
            # Validate timeframes
            if not self.timeframes:
                logger.error("No timeframes specified")
                return False
            
            if self.primary_timeframe not in self.timeframes:
                logger.error(f"Primary timeframe {self.primary_timeframe} not in timeframes list")
                return False
            
            # Validate signal strength
            if not (0.1 <= self.min_signal_strength <= 1.0):
                logger.error(f"Invalid min_signal_strength: {self.min_signal_strength}")
                return False
            
            # Validate lookback periods
            if self.volume_lookback < 10 or self.volume_lookback > 200:
                logger.error(f"Invalid volume_lookback: {self.volume_lookback}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating configuration: {e}")
            return False
    
    def _initialize_volume_analyzers(self):
        """Initialize volume analysis engines"""
        self.volume_analyzers = {
            VolumeAnalysisType.ON_BALANCE_VOLUME: self._analyze_obv,
            VolumeAnalysisType.VOLUME_WEIGHTED_AVERAGE_PRICE: self._analyze_vwap,
            VolumeAnalysisType.VOLUME_PROFILE: self._analyze_volume_profile,
            VolumeAnalysisType.ACCUMULATION_DISTRIBUTION: self._analyze_accumulation_distribution,
            VolumeAnalysisType.VOLUME_OSCILLATOR: self._analyze_volume_oscillator,
            VolumeAnalysisType.MONEY_FLOW_INDEX: self._analyze_money_flow_index,
            VolumeAnalysisType.CHAIKIN_MONEY_FLOW: self._analyze_chaikin_money_flow,
            VolumeAnalysisType.VOLUME_SPREAD_ANALYSIS: self._analyze_volume_spread,
            VolumeAnalysisType.INSTITUTIONAL_FLOW: self._analyze_institutional_flow
        }
        logger.info("Volume analyzers initialized")
    
    def _setup_institutional_detection(self):
        """Setup institutional flow detection system"""
        if self.enable_institutional_detection:
            self.institutional_detector = {
                'large_order_tracker': deque(maxlen=1000),
                'flow_patterns': defaultdict(list),
                'smart_money_indicators': {},
                'retail_sentiment_tracker': defaultdict(float)
            }
            logger.info("Institutional detection system initialized")
    
    def _setup_volume_profile(self):
        """Setup volume profile analysis"""
        if self.enable_volume_profile:
            self.volume_profile_data = {
                'price_levels': defaultdict(float),
                'volume_distribution': defaultdict(float),
                'poc_history': deque(maxlen=100),
                'value_area_history': deque(maxlen=100)
            }
            logger.info("Volume profile system initialized")
    
    def _setup_performance_monitoring(self):
        """Setup performance monitoring and analytics"""
        self.performance_monitor = {
            'signals_generated': 0,
            'volume_confirmed_signals': 0,
            'institutional_signals': 0,
            'successful_volume_trades': 0,
            'failed_volume_trades': 0,
            'avg_volume_accuracy': 0.0,
            'best_volume_profit': 0.0,
            'worst_volume_loss': 0.0,
            'volume_analysis_effectiveness': defaultdict(list)
        }
        logger.info("Performance monitoring setup complete")
    
    def generate_signals(self, data: Dict[str, pd.DataFrame]) -> List[SignalEvent]:
        """
        Generate enhanced volume-driven signals
        
        Args:
            data: Dictionary of market data by symbol and timeframe
            
        Returns:
            List of enhanced volume signals
        """
        try:
            signals = []
            
            for symbol, timeframe_data in data.items():
                if isinstance(timeframe_data, dict):
                    # Multi-timeframe volume analysis
                    symbol_signals = self._analyze_multi_timeframe_volume(
                        symbol, timeframe_data
                    )
                    signals.extend(symbol_signals)
                else:
                    # Single timeframe analysis
                    symbol_signals = self._analyze_single_timeframe_volume(
                        symbol, self.primary_timeframe, timeframe_data
                    )
                    signals.extend(symbol_signals)
            
            # Apply advanced filtering
            filtered_signals = self._filter_and_validate_volume_signals(signals)
            
            # Update performance tracking
            self._update_signal_history(filtered_signals)
            
            logger.info(f"Generated {len(filtered_signals)} volume signals from {len(signals)} candidates")
            return filtered_signals
            
        except Exception as e:
            logger.error(f"Error generating volume signals: {e}")
            return []
    
    def _analyze_multi_timeframe_volume(self, symbol: str, 
                                      timeframe_data: Dict[str, pd.DataFrame]) -> List[SignalEvent]:
        """Analyze volume patterns across multiple timeframes"""
        try:
            timeframe_analyses = {}
            timeframe_signals = {}
            
            # Analyze each timeframe for volume patterns
            for timeframe, df in timeframe_data.items():
                if timeframe in self.timeframes and len(df) >= self.volume_lookback:
                    volume_analysis = self._calculate_comprehensive_volume_analysis(df, timeframe, symbol)
                    timeframe_analyses[timeframe] = volume_analysis
                    
                    # Generate signals for this timeframe
                    tf_signals = self._generate_timeframe_volume_signals(
                        symbol, timeframe, df, volume_analysis
                    )
                    timeframe_signals[timeframe] = tf_signals
            
            # Combine multi-timeframe analysis
            combined_signals = self._combine_timeframe_volume_signals(
                symbol, timeframe_signals, timeframe_analyses
            )
            
            return combined_signals
            
        except Exception as e:
            logger.error(f"Error in multi-timeframe volume analysis for {symbol}: {e}")
            return []
    
    def _analyze_single_timeframe_volume(self, symbol: str, timeframe: str, 
                                       df: pd.DataFrame) -> List[SignalEvent]:
        """Analyze volume patterns for single timeframe"""
        try:
            if len(df) < self.volume_lookback:
                return []
            
            # Calculate comprehensive volume analysis
            volume_analysis = self._calculate_comprehensive_volume_analysis(df, timeframe, symbol)
            
            # Generate signals
            signals = self._generate_timeframe_volume_signals(
                symbol, timeframe, df, volume_analysis
            )
            
            return signals
            
        except Exception as e:
            logger.error(f"Error in single timeframe volume analysis: {e}")
            return []
    
    def _calculate_comprehensive_volume_analysis(self, df: pd.DataFrame, 
                                               timeframe: str, symbol: str) -> VolumeAnalysis:
        """Calculate comprehensive volume analysis"""
        try:
            # Determine volume data type and availability
            volume_type, volume_data = self._get_volume_data(df)
            
            if volume_data is None or volume_data.sum() == 0:
                logger.warning(f"No volume data available for {symbol} {timeframe}")
                return self._create_default_volume_analysis(df, timeframe, symbol)
            
            # Basic volume metrics
            current_volume = volume_data.iloc[-1]
            average_volume = volume_data.rolling(self.volume_lookback).mean().iloc[-1]
            volume_ratio = current_volume / average_volume if average_volume > 0 else 1.0
            
            # Volume trend analysis
            volume_trend = self._analyze_volume_trend(volume_data)
            volume_condition = self._determine_volume_condition(volume_ratio, volume_data)
            
            # Advanced volume indicators
            obv_value = self._calculate_obv(df, volume_data)
            vwap_value = self._calculate_vwap(df, volume_data)
            money_flow = self._calculate_money_flow_index(df, volume_data)
            accumulation_distribution = self._calculate_accumulation_distribution(df, volume_data)
            volume_oscillator = self._calculate_volume_oscillator(volume_data)
            
            # Institutional flow analysis
            institutional_flow_score = 0.0
            retail_flow_score = 0.0
            if self.enable_institutional_detection:
                institutional_flow_score, retail_flow_score = self._detect_institutional_flow(
                    df, volume_data, volume_ratio
                )
            
            # Volume profile analysis
            vp_poc, vp_vah, vp_val = 0.0, 0.0, 0.0
            if self.enable_volume_profile:
                vp_poc, vp_vah, vp_val = self._calculate_volume_profile_levels(df, volume_data)
            
            # Support/resistance from volume
            support_levels, resistance_levels = self._identify_volume_levels(df, volume_data)
            
            # Calculate confidence
            confidence = self._calculate_volume_analysis_confidence(
                volume_ratio, volume_condition, institutional_flow_score
            )
            
            # Create comprehensive analysis
            volume_analysis = VolumeAnalysis(
                timestamp=datetime.utcnow(),
                symbol=symbol,
                timeframe=timeframe,
                volume_type=volume_type,
                current_volume=current_volume,
                average_volume=average_volume,
                volume_ratio=volume_ratio,
                volume_trend=volume_trend,
                volume_condition=volume_condition,
                obv_value=obv_value,
                vwap_value=vwap_value,
                money_flow=money_flow,
                accumulation_distribution=accumulation_distribution,
                volume_oscillator=volume_oscillator,
                institutional_flow_score=institutional_flow_score,
                retail_flow_score=retail_flow_score,
                volume_profile_poc=vp_poc,
                volume_profile_vah=vp_vah,
                volume_profile_val=vp_val,
                support_levels=support_levels,
                resistance_levels=resistance_levels,
                confidence=confidence
            )
            
            return volume_analysis
            
        except Exception as e:
            logger.error(f"Error calculating comprehensive volume analysis: {e}")
            return self._create_default_volume_analysis(df, timeframe, symbol)
    
    def _get_volume_data(self, df: pd.DataFrame) -> Tuple[VolumeDataType, Optional[pd.Series]]:
        """Get appropriate volume data based on availability and preference"""
        try:
            # Check for real volume first if preferred
            if self.prefer_real_volume and 'real_volume' in df.columns:
                real_volume = df['real_volume']
                if real_volume.sum() > 0:  # Has actual volume data
                    return VolumeDataType.REAL_VOLUME, real_volume
            
            # Check for standard volume column
            if 'volume' in df.columns:
                volume = df['volume']
                if volume.sum() > 0:
                    # Determine if this is tick or real volume based on values
                    if volume.max() < 10000 and volume.mean() < 1000:
                        return VolumeDataType.TICK_VOLUME, volume
                    else:
                        return VolumeDataType.REAL_VOLUME, volume
            
            # Check for tick volume specifically
            if 'tick_volume' in df.columns:
                tick_volume = df['tick_volume']
                if tick_volume.sum() > 0:
                    return VolumeDataType.TICK_VOLUME, tick_volume
            
            # Fallback: estimate volume from price movement if enabled
            if self.fallback_to_tick_volume:
                estimated_volume = self._estimate_volume_from_price(df)
                return VolumeDataType.TICK_VOLUME, estimated_volume
            
            return VolumeDataType.TICK_VOLUME, None
            
        except Exception as e:
            logger.error(f"Error getting volume data: {e}")
            return VolumeDataType.TICK_VOLUME, None
    
    def _estimate_volume_from_price(self, df: pd.DataFrame) -> pd.Series:
        """Estimate volume from price movement (fallback method)"""
        try:
            # Simple estimation based on price range and volatility
            price_range = df['high'] - df['low']
            price_change = abs(df['close'] - df['open'])
            volatility = df['close'].pct_change().abs()
            
            # Combine factors to estimate relative volume
            estimated_volume = (price_range + price_change) * (1 + volatility)
            estimated_volume = estimated_volume.fillna(1.0)
            
            # Normalize to reasonable range
            estimated_volume = (estimated_volume / estimated_volume.mean()) * 100
            
            return estimated_volume
            
        except Exception as e:
            logger.error(f"Error estimating volume from price: {e}")
            return pd.Series(100, index=df.index)
    
    def _create_default_volume_analysis(self, df: pd.DataFrame, timeframe: str, symbol: str) -> VolumeAnalysis:
        """Create default volume analysis when data is not available"""
        return VolumeAnalysis(
            timestamp=datetime.utcnow(),
            symbol=symbol,
            timeframe=timeframe,
            volume_type=VolumeDataType.TICK_VOLUME,
            current_volume=100.0,
            average_volume=100.0,
            volume_ratio=1.0,
            volume_trend='neutral',
            volume_condition=VolumeCondition.LOW_VOLUME,
            obv_value=0.0,
            vwap_value=df['close'].iloc[-1],
            money_flow=50.0,
            accumulation_distribution=0.0,
            volume_oscillator=0.0,
            institutional_flow_score=0.0,
            retail_flow_score=0.0,
            volume_profile_poc=df['close'].iloc[-1],
            volume_profile_vah=df['high'].iloc[-1],
            volume_profile_val=df['low'].iloc[-1],
            support_levels=[],
            resistance_levels=[],
            confidence=0.3
        )
    
    def _analyze_volume_trend(self, volume_data: pd.Series) -> str:
        """Analyze volume trend direction"""
        try:
            if len(volume_data) < 10:
                return 'neutral'
            
            # Compare recent vs older volume
            recent_avg = volume_data.tail(5).mean()
            older_avg = volume_data.tail(20).head(15).mean()
            
            if recent_avg > older_avg * 1.2:
                return 'increasing'
            elif recent_avg < older_avg * 0.8:
                return 'decreasing'
            else:
                return 'neutral'
                
        except Exception as e:
            logger.error(f"Error analyzing volume trend: {e}")
            return 'neutral'
    
    def _determine_volume_condition(self, volume_ratio: float, volume_data: pd.Series) -> VolumeCondition:
        """Determine current volume condition"""
        try:
            if volume_ratio >= self.volume_surge_threshold:
                return VolumeCondition.VOLUME_SURGE
            elif volume_ratio >= self.high_volume_threshold:
                return VolumeCondition.HIGH_VOLUME
            elif volume_ratio <= self.low_volume_threshold:
                return VolumeCondition.LOW_VOLUME
            elif volume_ratio <= 0.3:
                return VolumeCondition.VOLUME_DRYING_UP
            else:
                # Check for specific patterns
                recent_volumes = volume_data.tail(5)
                if recent_volumes.max() > recent_volumes.mean() * 3:
                    return VolumeCondition.VOLUME_CLIMAX
                elif volume_ratio >= self.min_volume_confirmation:
                    return VolumeCondition.VOLUME_CONFIRMATION
                else:
                    return VolumeCondition.LOW_VOLUME
                    
        except Exception as e:
            logger.error(f"Error determining volume condition: {e}")
            return VolumeCondition.LOW_VOLUME
    
    def _calculate_obv(self, df: pd.DataFrame, volume_data: pd.Series) -> float:
        """Calculate On-Balance Volume"""
        try:
            obv = 0.0
            obv_values = []
            
            for i in range(len(df)):
                if i == 0:
                    obv_values.append(volume_data.iloc[i])
                else:
                    close_current = df['close'].iloc[i]
                    close_previous = df['close'].iloc[i-1]
                    volume_current = volume_data.iloc[i]
                    
                    if close_current > close_previous:
                        obv += volume_current
                    elif close_current < close_previous:
                        obv -= volume_current
                    # If equal, OBV unchanged
                    
                    obv_values.append(obv)
            
            return float(obv_values[-1])
            
        except Exception as e:
            logger.error(f"Error calculating OBV: {e}")
            return 0.0
    
    def _calculate_vwap(self, df: pd.DataFrame, volume_data: pd.Series) -> float:
        """Calculate Volume Weighted Average Price"""
        try:
            # Typical price
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            
            # VWAP calculation
            price_volume = typical_price * volume_data
            cumulative_pv = price_volume.rolling(self.vwap_period).sum()
            cumulative_volume = volume_data.rolling(self.vwap_period).sum()
            
            vwap = cumulative_pv / cumulative_volume
            return float(vwap.iloc[-1]) if not vwap.empty else float(df['close'].iloc[-1])
            
        except Exception as e:
            logger.error(f"Error calculating VWAP: {e}")
            return float(df['close'].iloc[-1])
    
    def _calculate_money_flow_index(self, df: pd.DataFrame, volume_data: pd.Series) -> float:
        """Calculate Money Flow Index"""
        try:
            # Typical price and money flow
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            money_flow = typical_price * volume_data
            
            # Positive and negative money flows
            positive_flow = []
            negative_flow = []
            
            for i in range(1, len(typical_price)):
                if typical_price.iloc[i] > typical_price.iloc[i-1]:
                    positive_flow.append(money_flow.iloc[i])
                    negative_flow.append(0)
                elif typical_price.iloc[i] < typical_price.iloc[i-1]:
                    positive_flow.append(0)
                    negative_flow.append(money_flow.iloc[i])
                else:
                    positive_flow.append(0)
                    negative_flow.append(0)
            
            # Add initial value
            positive_flow = [0] + positive_flow
            negative_flow = [0] + negative_flow
            
            positive_flow = pd.Series(positive_flow, index=df.index)
            negative_flow = pd.Series(negative_flow, index=df.index)
            
            # Money Flow Index
            pmf = positive_flow.rolling(self.mfi_period).sum()
            nmf = negative_flow.rolling(self.mfi_period).sum()
            
            money_ratio = pmf / nmf
            mfi = 100 - (100 / (1 + money_ratio))
            
            return float(mfi.iloc[-1]) if not mfi.empty else 50.0
            
        except Exception as e:
            logger.error(f"Error calculating Money Flow Index: {e}")
            return 50.0
    
    def _calculate_accumulation_distribution(self, df: pd.DataFrame, volume_data: pd.Series) -> float:
        """Calculate Accumulation/Distribution Line"""
        try:
            ad_line = 0.0
            ad_values = []
            
            for i in range(len(df)):
                high = df['high'].iloc[i]
                low = df['low'].iloc[i]
                close = df['close'].iloc[i]
                volume = volume_data.iloc[i]
                
                if high != low:  # Avoid division by zero
                    money_flow_multiplier = ((close - low) - (high - close)) / (high - low)
                    money_flow_volume = money_flow_multiplier * volume
                    ad_line += money_flow_volume
                
                ad_values.append(ad_line)
            
            return float(ad_values[-1])
            
        except Exception as e:
            logger.error(f"Error calculating Accumulation/Distribution: {e}")
            return 0.0
    
    def _calculate_volume_oscillator(self, volume_data: pd.Series) -> float:
        """Calculate Volume Oscillator"""
        try:
            # Short and long period moving averages
            short_ma = volume_data.rolling(5).mean()
            long_ma = volume_data.rolling(20).mean()
            
            # Volume Oscillator
            vo = ((short_ma - long_ma) / long_ma) * 100
            
            return float(vo.iloc[-1]) if not vo.empty else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating Volume Oscillator: {e}")
            return 0.0
    
    def _detect_institutional_flow(self, df: pd.DataFrame, volume_data: pd.Series, 
                                 volume_ratio: float) -> Tuple[float, float]:
        """Detect institutional vs retail flow"""
        try:
            if not self.enable_institutional_detection:
                return 0.0, 0.0
            
            # Large order detection
            large_volume_threshold = volume_data.mean() * self.large_order_threshold
            large_orders = volume_data[volume_data > large_volume_threshold]
            
            # Institutional flow score
            institutional_score = 0.0
            retail_score = 0.0
            
            # Recent large orders
            recent_large_orders = len(large_orders.tail(self.institutional_window))
            if recent_large_orders > 0:
                institutional_score += min(1.0, recent_large_orders / 5.0)
            
            # Volume pattern analysis
            if volume_ratio > self.high_volume_threshold:
                # High volume with price movement suggests institutional activity
                price_change = abs(df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2]
                if price_change > 0.005:  # 0.5% price move with high volume
                    institutional_score += 0.3
            
            # Retail exhaustion signals
            if volume_ratio > self.volume_surge_threshold:
                # Very high volume might indicate retail exhaustion
                retail_score += 0.4
            
            # Smart money indicators
            if self.enable_smart_money_tracking:
                smart_money_score = self._calculate_smart_money_score(df, volume_data)
                institutional_score += smart_money_score * 0.3
            
            # Normalize scores
            institutional_score = min(1.0, institutional_score)
            retail_score = min(1.0, retail_score)
            
            return institutional_score, retail_score
            
        except Exception as e:
            logger.error(f"Error detecting institutional flow: {e}")
            return 0.0, 0.0
    
    def _calculate_smart_money_score(self, df: pd.DataFrame, volume_data: pd.Series) -> float:
        """Calculate smart money activity score"""
        try:
            score = 0.0
            
            # Volume-price relationship
            price_changes = df['close'].pct_change().abs()
            volume_changes = volume_data.pct_change().abs()
            
            # Correlation between volume and price moves
            correlation = price_changes.tail(20).corr(volume_changes.tail(20))
            if not np.isnan(correlation) and correlation > 0.5:
                score += 0.3
            
            # Off-hours volume (if timestamp available)
            # This would require actual timestamp analysis
            # For now, use volume patterns
            volume_std = volume_data.tail(20).std()
            volume_mean = volume_data.tail(20).mean()
            
            if volume_std / volume_mean < 0.5:  # Consistent volume
                score += 0.2
            
            # Volume leading price
            if len(df) > 5:
                recent_volume_increase = volume_data.iloc[-1] > volume_data.iloc[-3]
                subsequent_price_move = abs(df['close'].iloc[-1] - df['close'].iloc[-2]) > abs(df['close'].iloc[-2] - df['close'].iloc[-3])
                
                if recent_volume_increase and subsequent_price_move:
                    score += 0.3
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Error calculating smart money score: {e}")
            return 0.0
    
    def _calculate_volume_profile_levels(self, df: pd.DataFrame, 
                                       volume_data: pd.Series) -> Tuple[float, float, float]:
        """Calculate Volume Profile levels (POC, VAH, VAL)"""
        try:
            if not self.enable_volume_profile:
                current_price = df['close'].iloc[-1]
                return current_price, current_price * 1.01, current_price * 0.99
            
            # Create price bins
            price_min = df['low'].min()
            price_max = df['high'].max()
            price_range = price_max - price_min
            bin_size = price_range / 100  # 100 price levels
            
            # Volume distribution
            volume_at_price = defaultdict(float)
            
            for i in range(len(df)):
                # Distribute volume across price range of the bar
                bar_low = df['low'].iloc[i]
                bar_high = df['high'].iloc[i]
                bar_volume = volume_data.iloc[i]
                
                # Simple distribution - can be made more sophisticated
                price_levels = int((bar_high - bar_low) / bin_size) + 1
                volume_per_level = bar_volume / price_levels
                
                current_price = bar_low
                while current_price <= bar_high:
                    price_bin = int((current_price - price_min) / bin_size)
                    volume_at_price[price_bin] += volume_per_level
                    current_price += bin_size
            
            # Find Point of Control (highest volume price)
            if volume_at_price:
                poc_bin = max(volume_at_price.keys(), key=lambda x: volume_at_price[x])
                poc = price_min + (poc_bin * bin_size)
                
                # Calculate Value Area (70% of volume)
                total_volume = sum(volume_at_price.values())
                target_volume = total_volume * self.vp_value_area
                
                # Find value area around POC
                cumulative_volume = volume_at_price[poc_bin]
                vah_bin = poc_bin
                val_bin = poc_bin
                
                while cumulative_volume < target_volume and (vah_bin < max(volume_at_price.keys()) or val_bin > min(volume_at_price.keys())):
                    # Expand both ways
                    if vah_bin + 1 in volume_at_price:
                        vah_bin += 1
                        cumulative_volume += volume_at_price[vah_bin]
                    
                    if cumulative_volume < target_volume and val_bin - 1 in volume_at_price:
                        val_bin -= 1
                        cumulative_volume += volume_at_price[val_bin]
                
                vah = price_min + (vah_bin * bin_size)
                val = price_min + (val_bin * bin_size)
                
                return poc, vah, val
            
            # Fallback to current price
            current_price = df['close'].iloc[-1]
            return current_price, current_price * 1.01, current_price * 0.99
            
        except Exception as e:
            logger.error(f"Error calculating volume profile levels: {e}")
            current_price = df['close'].iloc[-1]
            return current_price, current_price * 1.01, current_price * 0.99
    
    def _identify_volume_levels(self, df: pd.DataFrame, 
                              volume_data: pd.Series) -> Tuple[List[float], List[float]]:
        """Identify support and resistance levels based on volume"""
        try:
            support_levels = []
            resistance_levels = []
            
            # Find high volume areas that acted as support/resistance
            high_volume_threshold = volume_data.quantile(0.8)
            high_volume_bars = volume_data[volume_data > high_volume_threshold]
            
            for idx in high_volume_bars.index:
                price_level = df.loc[idx, 'close']
                
                # Check if this level held multiple times
                touches = 0
                for i in range(len(df)):
                    if abs(df['close'].iloc[i] - price_level) < price_level * 0.005:  # Within 0.5%
                        touches += 1
                
                if touches >= 2:
                    # Determine if support or resistance based on price action
                    if price_level < df['close'].iloc[-1]:
                        support_levels.append(price_level)
                    else:
                        resistance_levels.append(price_level)
            
            # Remove duplicates and sort
            support_levels = sorted(list(set(support_levels)))
            resistance_levels = sorted(list(set(resistance_levels)), reverse=True)
            
            # Keep only top 3 levels each
            return support_levels[:3], resistance_levels[:3]
            
        except Exception as e:
            logger.error(f"Error identifying volume levels: {e}")
            return [], []
    
    def _calculate_volume_analysis_confidence(self, volume_ratio: float, 
                                            volume_condition: VolumeCondition,
                                            institutional_score: float) -> float:
        """Calculate confidence in volume analysis"""
        try:
            confidence_factors = []
            
            # Volume ratio factor
            if volume_ratio > self.high_volume_threshold:
                confidence_factors.append(0.8)
            elif volume_ratio > self.min_volume_confirmation:
                confidence_factors.append(0.6)
            else:
                confidence_factors.append(0.3)
            
            # Volume condition factor
            condition_weights = {
                VolumeCondition.VOLUME_SURGE: 0.9,
                VolumeCondition.HIGH_VOLUME: 0.8,
                VolumeCondition.VOLUME_CONFIRMATION: 0.7,
                VolumeCondition.VOLUME_CLIMAX: 0.8,
                VolumeCondition.LOW_VOLUME: 0.3,
                VolumeCondition.VOLUME_DRYING_UP: 0.4,
                VolumeCondition.VOLUME_DIVERGENCE: 0.6
            }
            confidence_factors.append(condition_weights.get(volume_condition, 0.5))
            
            # Institutional flow factor
            if institutional_score > 0.7:
                confidence_factors.append(0.9)
            elif institutional_score > 0.4:
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.5)
            
            # Calculate overall confidence
            overall_confidence = np.mean(confidence_factors) if confidence_factors else 0.5
            
            return float(overall_confidence)
            
        except Exception as e:
            logger.error(f"Error calculating volume analysis confidence: {e}")
            return 0.5
    
    def _generate_timeframe_volume_signals(self, symbol: str, timeframe: str, df: pd.DataFrame,
                                         volume_analysis: VolumeAnalysis) -> List[SignalEvent]:
        """Generate volume signals for specific timeframe"""
        try:
            signals = []
            
            # Skip if confidence too low
            if volume_analysis.confidence < self.min_signal_strength:
                return signals
            
            current_price = df['close'].iloc[-1]
            
            # Generate signals based on different analysis types
            for analysis_type in self.analysis_types:
                try:
                    analyzer = self.volume_analyzers.get(analysis_type)
                    if analyzer:
                        type_signals = analyzer(symbol, timeframe, df, volume_analysis)
                        signals.extend(type_signals)
                        
                except Exception as e:
                    logger.warning(f"Error in {analysis_type} analyzer: {e}")
                    continue
            
            # Filter and enhance signals
            enhanced_signals = []
            for signal in signals:
                enhanced_signal = self._enhance_volume_signal(signal, volume_analysis, df)
                if enhanced_signal and self._validate_volume_signal(enhanced_signal):
                    enhanced_signals.append(enhanced_signal)
            
            return enhanced_signals
            
        except Exception as e:
            logger.error(f"Error generating timeframe volume signals: {e}")
            return []
    
    def _analyze_obv(self, symbol: str, timeframe: str, df: pd.DataFrame,
                   volume_analysis: VolumeAnalysis) -> List[SignalEvent]:
        """Analyze OBV for trading signals"""
        try:
            signals = []
            
            # Check OBV trend vs price trend
            price_change = df['close'].iloc[-1] - df['close'].iloc[-5]
            obv_value = volume_analysis.obv_value
            
            # Get previous OBV values for trend comparison
            volume_type, volume_data = self._get_volume_data(df)
            if volume_data is None:
                return signals
            
            # Calculate OBV trend
            obv_values = []
            obv = 0
            for i in range(len(df)):
                if i == 0:
                    obv_values.append(volume_data.iloc[i])
                else:
                    if df['close'].iloc[i] > df['close'].iloc[i-1]:
                        obv += volume_data.iloc[i]
                    elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                        obv -= volume_data.iloc[i]
                    obv_values.append(obv)
            
            if len(obv_values) >= 5:
                obv_trend = obv_values[-1] - obv_values[-5]
                
                # OBV divergence signals
                if price_change > 0 and obv_trend < 0:  # Bearish divergence
                    signal = self._create_volume_signal(
                        symbol, timeframe, VolumeSignalType.VOLUME_REVERSAL,
                        VolumeAnalysisType.ON_BALANCE_VOLUME, 'bearish',
                        df['close'].iloc[-1], volume_analysis
                    )
                    if signal:
                        signals.append(signal)
                
                elif price_change < 0 and obv_trend > 0:  # Bullish divergence
                    signal = self._create_volume_signal(
                        symbol, timeframe, VolumeSignalType.VOLUME_REVERSAL,
                        VolumeAnalysisType.ON_BALANCE_VOLUME, 'bullish',
                        df['close'].iloc[-1], volume_analysis
                    )
                    if signal:
                        signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error analyzing OBV: {e}")
            return []
    
    def _analyze_vwap(self, symbol: str, timeframe: str, df: pd.DataFrame,
                    volume_analysis: VolumeAnalysis) -> List[SignalEvent]:
        """Analyze VWAP for trading signals"""
        try:
            signals = []
            
            current_price = df['close'].iloc[-1]
            vwap_value = volume_analysis.vwap_value
            
            # VWAP signals
            price_vs_vwap = (current_price - vwap_value) / vwap_value
            
            # Strong volume confirmation at VWAP
            if (volume_analysis.volume_condition in [VolumeCondition.HIGH_VOLUME, VolumeCondition.VOLUME_SURGE] and
                abs(price_vs_vwap) < 0.002):  # Within 0.2% of VWAP
                
                if current_price > vwap_value:
                    direction = 'bullish'
                else:
                    direction = 'bearish'
                
                signal = self._create_volume_signal(
                    symbol, timeframe, VolumeSignalType.VOLUME_BREAKOUT,
                    VolumeAnalysisType.VOLUME_WEIGHTED_AVERAGE_PRICE, direction,
                    current_price, volume_analysis
                )
                if signal:
                    signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error analyzing VWAP: {e}")
            return []
    
    def _analyze_volume_profile(self, symbol: str, timeframe: str, df: pd.DataFrame,
                              volume_analysis: VolumeAnalysis) -> List[SignalEvent]:
        """Analyze Volume Profile for trading signals"""
        try:
            signals = []
            
            if not self.enable_volume_profile:
                return signals
            
            current_price = df['close'].iloc[-1]
            poc = volume_analysis.volume_profile_poc
            vah = volume_analysis.volume_profile_vah
            val = volume_analysis.volume_profile_val
            
            # Volume Profile signals
            if volume_analysis.volume_condition in [VolumeCondition.HIGH_VOLUME, VolumeCondition.VOLUME_SURGE]:
                
                # Price near POC with high volume
                if abs(current_price - poc) < poc * 0.005:  # Within 0.5% of POC
                    # Determine direction based on recent price action
                    recent_trend = df['close'].iloc[-1] - df['close'].iloc[-3]
                    direction = 'bullish' if recent_trend > 0 else 'bearish'
                    
                    signal = self._create_volume_signal(
                        symbol, timeframe, VolumeSignalType.INSTITUTIONAL_ACCUMULATION,
                        VolumeAnalysisType.VOLUME_PROFILE, direction,
                        current_price, volume_analysis
                    )
                    if signal:
                        signals.append(signal)
                
                # Break of Value Area with volume
                elif current_price > vah and volume_analysis.volume_ratio > self.high_volume_threshold:
                    signal = self._create_volume_signal(
                        symbol, timeframe, VolumeSignalType.VOLUME_BREAKOUT,
                        VolumeAnalysisType.VOLUME_PROFILE, 'bullish',
                        current_price, volume_analysis
                    )
                    if signal:
                        signals.append(signal)
                
                elif current_price < val and volume_analysis.volume_ratio > self.high_volume_threshold:
                    signal = self._create_volume_signal(
                        symbol, timeframe, VolumeSignalType.VOLUME_BREAKOUT,
                        VolumeAnalysisType.VOLUME_PROFILE, 'bearish',
                        current_price, volume_analysis
                    )
                    if signal:
                        signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error analyzing Volume Profile: {e}")
            return []
    
    def _analyze_accumulation_distribution(self, symbol: str, timeframe: str, df: pd.DataFrame,
                                         volume_analysis: VolumeAnalysis) -> List[SignalEvent]:
        """Analyze Accumulation/Distribution for signals"""
        try:
            signals = []
            
            ad_value = volume_analysis.accumulation_distribution
            
            # A/D Line trend analysis
            if len(df) >= 10:
                # Calculate A/D for trend comparison
                ad_values = []
                ad_line = 0
                
                volume_type, volume_data = self._get_volume_data(df)
                if volume_data is None:
                    return signals
                
                for i in range(len(df)):
                    high = df['high'].iloc[i]
                    low = df['low'].iloc[i]
                    close = df['close'].iloc[i]
                    volume = volume_data.iloc[i]
                    
                    if high != low:
                        mfm = ((close - low) - (high - close)) / (high - low)
                        ad_line += mfm * volume
                    
                    ad_values.append(ad_line)
                
                # Check for divergences
                price_trend = df['close'].iloc[-1] - df['close'].iloc[-10]
                ad_trend = ad_values[-1] - ad_values[-10]
                
                # Bullish divergence: price down, A/D up
                if price_trend < 0 and ad_trend > 0 and volume_analysis.volume_ratio > self.min_volume_confirmation:
                    signal = self._create_volume_signal(
                        symbol, timeframe, VolumeSignalType.INSTITUTIONAL_ACCUMULATION,
                        VolumeAnalysisType.ACCUMULATION_DISTRIBUTION, 'bullish',
                        df['close'].iloc[-1], volume_analysis
                    )
                    if signal:
                        signals.append(signal)
                
                # Bearish divergence: price up, A/D down
                elif price_trend > 0 and ad_trend < 0 and volume_analysis.volume_ratio > self.min_volume_confirmation:
                    signal = self._create_volume_signal(
                        symbol, timeframe, VolumeSignalType.INSTITUTIONAL_DISTRIBUTION,
                        VolumeAnalysisType.ACCUMULATION_DISTRIBUTION, 'bearish',
                        df['close'].iloc[-1], volume_analysis
                    )
                    if signal:
                        signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error analyzing Accumulation/Distribution: {e}")
            return []
    
    def _analyze_volume_oscillator(self, symbol: str, timeframe: str, df: pd.DataFrame,
                                 volume_analysis: VolumeAnalysis) -> List[SignalEvent]:
        """Analyze Volume Oscillator for signals"""
        try:
            signals = []
            
            vo_value = volume_analysis.volume_oscillator
            
            # Volume Oscillator signals
            if abs(vo_value) > 20:  # Significant deviation
                if vo_value > 20 and volume_analysis.volume_condition == VolumeCondition.HIGH_VOLUME:
                    # High positive VO with high volume - potential reversal
                    signal = self._create_volume_signal(
                        symbol, timeframe, VolumeSignalType.VOLUME_REVERSAL,
                        VolumeAnalysisType.VOLUME_OSCILLATOR, 'bearish',
                        df['close'].iloc[-1], volume_analysis
                    )
                    if signal:
                        signals.append(signal)
                
                elif vo_value < -20 and volume_analysis.volume_condition == VolumeCondition.LOW_VOLUME:
                    # Low negative VO with low volume - potential reversal
                    signal = self._create_volume_signal(
                        symbol, timeframe, VolumeSignalType.VOLUME_REVERSAL,
                        VolumeAnalysisType.VOLUME_OSCILLATOR, 'bullish',
                        df['close'].iloc[-1], volume_analysis
                    )
                    if signal:
                        signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error analyzing Volume Oscillator: {e}")
            return []
    
    def _analyze_money_flow_index(self, symbol: str, timeframe: str, df: pd.DataFrame,
                                volume_analysis: VolumeAnalysis) -> List[SignalEvent]:
        """Analyze Money Flow Index for signals"""
        try:
            signals = []
            
            mfi_value = volume_analysis.money_flow
            
            # MFI overbought/oversold with volume confirmation
            if mfi_value > self.mfi_overbought and volume_analysis.volume_ratio > self.high_volume_threshold:
                signal = self._create_volume_signal(
                    symbol, timeframe, VolumeSignalType.RETAIL_EXHAUSTION,
                    VolumeAnalysisType.MONEY_FLOW_INDEX, 'bearish',
                    df['close'].iloc[-1], volume_analysis
                )
                if signal:
                    signals.append(signal)
            
            elif mfi_value < self.mfi_oversold and volume_analysis.volume_ratio > self.high_volume_threshold:
                signal = self._create_volume_signal(
                    symbol, timeframe, VolumeSignalType.RETAIL_EXHAUSTION,
                    VolumeAnalysisType.MONEY_FLOW_INDEX, 'bullish',
                    df['close'].iloc[-1], volume_analysis
                )
                if signal:
                    signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error analyzing Money Flow Index: {e}")
            return []
    
    def _analyze_chaikin_money_flow(self, symbol: str, timeframe: str, df: pd.DataFrame,
                                  volume_analysis: VolumeAnalysis) -> List[SignalEvent]:
        """Analyze Chaikin Money Flow for signals"""
        try:
            signals = []
            
            # Calculate CMF
            volume_type, volume_data = self._get_volume_data(df)
            if volume_data is None:
                return signals
            
            cmf_values = []
            for i in range(len(df)):
                high = df['high'].iloc[i]
                low = df['low'].iloc[i]
                close = df['close'].iloc[i]
                volume = volume_data.iloc[i]
                
                if high != low:
                    mfm = ((close - low) - (high - close)) / (high - low)
                    cmf_values.append(mfm * volume)
                else:
                    cmf_values.append(0)
            
            if len(cmf_values) >= 20:
                cmf_sum = sum(cmf_values[-20:])
                volume_sum = volume_data.tail(20).sum()
                cmf = cmf_sum / volume_sum if volume_sum > 0 else 0
                
                # CMF signals with volume confirmation
                if cmf > 0.2 and volume_analysis.volume_ratio > self.min_volume_confirmation:
                    signal = self._create_volume_signal(
                        symbol, timeframe, VolumeSignalType.SMART_MONEY_FLOW,
                        VolumeAnalysisType.CHAIKIN_MONEY_FLOW, 'bullish',
                        df['close'].iloc[-1], volume_analysis
                    )
                    if signal:
                        signals.append(signal)
                
                elif cmf < -0.2 and volume_analysis.volume_ratio > self.min_volume_confirmation:
                    signal = self._create_volume_signal(
                        symbol, timeframe, VolumeSignalType.SMART_MONEY_FLOW,
                        VolumeAnalysisType.CHAIKIN_MONEY_FLOW, 'bearish',
                        df['close'].iloc[-1], volume_analysis
                    )
                    if signal:
                        signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error analyzing Chaikin Money Flow: {e}")
            return []
    
    def _analyze_volume_spread(self, symbol: str, timeframe: str, df: pd.DataFrame,
                             volume_analysis: VolumeAnalysis) -> List[SignalEvent]:
        """Analyze Volume Spread Analysis for signals"""
        try:
            signals = []
            
            # VSA analysis based on volume, spread (range), and close position
            current_bar = df.iloc[-1]
            spread = current_bar['high'] - current_bar['low']
            close_position = (current_bar['close'] - current_bar['low']) / spread if spread > 0 else 0.5
            
            # High volume, narrow spread, close up - potential accumulation
            if (volume_analysis.volume_ratio > self.high_volume_threshold and
                spread < df['high'].rolling(20).max().iloc[-1] - df['low'].rolling(20).min().iloc[-1] and
                close_position > 0.7):
                
                signal = self._create_volume_signal(
                    symbol, timeframe, VolumeSignalType.INSTITUTIONAL_ACCUMULATION,
                    VolumeAnalysisType.VOLUME_SPREAD_ANALYSIS, 'bullish',
                    current_bar['close'], volume_analysis
                )
                if signal:
                    signals.append(signal)
            
            # High volume, wide spread, close down - potential distribution
            elif (volume_analysis.volume_ratio > self.high_volume_threshold and
                  spread > df['high'].rolling(20).max().iloc[-1] - df['low'].rolling(20).min().iloc[-1] and
                  close_position < 0.3):
                
                signal = self._create_volume_signal(
                    symbol, timeframe, VolumeSignalType.INSTITUTIONAL_DISTRIBUTION,
                    VolumeAnalysisType.VOLUME_SPREAD_ANALYSIS, 'bearish',
                    current_bar['close'], volume_analysis
                )
                if signal:
                    signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error analyzing Volume Spread Analysis: {e}")
            return []
    
    def _analyze_institutional_flow(self, symbol: str, timeframe: str, df: pd.DataFrame,
                                  volume_analysis: VolumeAnalysis) -> List[SignalEvent]:
        """Analyze Institutional Flow for signals"""
        try:
            signals = []
            
            if not self.enable_institutional_detection:
                return signals
            
            institutional_score = volume_analysis.institutional_flow_score
            retail_score = volume_analysis.retail_flow_score
            
            # Strong institutional flow signals
            if institutional_score > self.smart_money_threshold:
                # Determine direction based on price action and volume
                price_momentum = df['close'].iloc[-1] - df['close'].iloc[-5]
                
                if price_momentum > 0 and volume_analysis.volume_ratio > self.high_volume_threshold:
                    signal = self._create_volume_signal(
                        symbol, timeframe, VolumeSignalType.SMART_MONEY_FLOW,
                        VolumeAnalysisType.INSTITUTIONAL_FLOW, 'bullish',
                        df['close'].iloc[-1], volume_analysis
                    )
                    if signal:
                        signals.append(signal)
                
                elif price_momentum < 0 and volume_analysis.volume_ratio > self.high_volume_threshold:
                    signal = self._create_volume_signal(
                        symbol, timeframe, VolumeSignalType.SMART_MONEY_FLOW,
                        VolumeAnalysisType.INSTITUTIONAL_FLOW, 'bearish',
                        df['close'].iloc[-1], volume_analysis
                    )
                    if signal:
                        signals.append(signal)
            
            # Retail exhaustion signals
            elif retail_score > 0.7 and volume_analysis.volume_condition == VolumeCondition.VOLUME_SURGE:
                # High retail activity often precedes reversals
                recent_trend = df['close'].iloc[-1] - df['close'].iloc[-10]
                direction = 'bearish' if recent_trend > 0 else 'bullish'  # Counter-trend
                
                signal = self._create_volume_signal(
                    symbol, timeframe, VolumeSignalType.RETAIL_EXHAUSTION,
                    VolumeAnalysisType.INSTITUTIONAL_FLOW, direction,
                    df['close'].iloc[-1], volume_analysis
                )
                if signal:
                    signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error analyzing Institutional Flow: {e}")
            return []
    
    def _create_volume_signal(self, symbol: str, timeframe: str, signal_type: VolumeSignalType,
                            analysis_type: VolumeAnalysisType, direction: str,
                            entry_price: float, volume_analysis: VolumeAnalysis) -> Optional[SignalEvent]:
        """Create enhanced volume signal"""
        try:
            # Calculate targets and stop loss based on volume analysis
            volatility_estimate = entry_price * 0.02  # 2% default
            
            if direction == 'bullish':
                target_price = entry_price + (volatility_estimate * self.volume_take_profit_ratio)
                stop_loss = entry_price - (volatility_estimate * self.volume_stop_loss_multiplier)
            else:
                target_price = entry_price - (volatility_estimate * self.volume_take_profit_ratio)
                stop_loss = entry_price + (volatility_estimate * self.volume_stop_loss_multiplier)
            
            # Calculate risk-reward ratio
            risk = abs(entry_price - stop_loss)
            reward = abs(target_price - entry_price)
            risk_reward_ratio = reward / risk if risk > 0 else 0
            
            # Skip if poor risk-reward
            if risk_reward_ratio < 1.0:
                return None
            
            # Calculate signal strength
            strength = self._calculate_volume_signal_strength(signal_type, volume_analysis)
            
            # Skip if strength too low
            if strength < self.min_signal_strength:
                return None
            
            # Determine institutional backing
            institutional_backing = volume_analysis.institutional_flow_score > 0.5
            
            # Determine retail sentiment
            retail_sentiment = 'bullish' if volume_analysis.retail_flow_score > 0.6 else 'bearish'
            
            # Calculate expected move
            expected_move = abs(target_price - entry_price)
            
            # Get supporting and risk factors
            supporting_factors, risk_factors = self._analyze_signal_factors(signal_type, volume_analysis)
            
            # Create signal event
            signal = SignalEvent(
                event_type='VOLUME_SIGNAL',
                symbol=symbol,
                timeframe=timeframe,
                timestamp=datetime.utcnow(),
                direction=direction,
                strength=strength,
                level=entry_price,
                metadata={
                    'signal_type': signal_type.value,
                    'analysis_type': analysis_type.value,
                    'target_price': target_price,
                    'stop_loss': stop_loss,
                    'risk_reward_ratio': risk_reward_ratio,
                    'volume_confirmation': volume_analysis.volume_ratio > self.min_volume_confirmation,
                    'institutional_backing': institutional_backing,
                    'retail_sentiment': retail_sentiment,
                    'expected_move': expected_move,
                    'confidence': volume_analysis.confidence,
                    'volume_condition': volume_analysis.volume_condition.value,
                    'volume_ratio': volume_analysis.volume_ratio,
                    'obv_value': volume_analysis.obv_value,
                    'vwap_value': volume_analysis.vwap_value,
                    'money_flow': volume_analysis.money_flow,
                    'institutional_score': volume_analysis.institutional_flow_score,
                    'supporting_factors': supporting_factors,
                    'risk_factors': risk_factors,
                    'volume_analysis_summary': self._create_volume_analysis_summary(volume_analysis)
                }
            )
            
            return signal
            
        except Exception as e:
            logger.error(f"Error creating volume signal: {e}")
            return None
    
    def _calculate_volume_signal_strength(self, signal_type: VolumeSignalType,
                                        volume_analysis: VolumeAnalysis) -> float:
        """Calculate signal strength based on volume analysis"""
        try:
            strength_factors = []
            
            # Base strength from volume condition
            condition_weights = {
                VolumeCondition.VOLUME_SURGE: 0.9,
                VolumeCondition.HIGH_VOLUME: 0.8,
                VolumeCondition.VOLUME_CONFIRMATION: 0.7,
                VolumeCondition.VOLUME_CLIMAX: 0.8,
                VolumeCondition.LOW_VOLUME: 0.3,
                VolumeCondition.VOLUME_DRYING_UP: 0.4,
                VolumeCondition.VOLUME_DIVERGENCE: 0.6
            }
            strength_factors.append(condition_weights.get(volume_analysis.volume_condition, 0.5))
            
            # Volume ratio factor
            volume_strength = min(1.0, volume_analysis.volume_ratio / self.high_volume_threshold)
            strength_factors.append(volume_strength)
            
            # Institutional flow factor
            institutional_factor = volume_analysis.institutional_flow_score
            strength_factors.append(institutional_factor)
            
            # Signal type specific adjustments
            type_weights = {
                VolumeSignalType.SMART_MONEY_FLOW: 0.9,
                VolumeSignalType.INSTITUTIONAL_ACCUMULATION: 0.8,
                VolumeSignalType.INSTITUTIONAL_DISTRIBUTION: 0.8,
                VolumeSignalType.VOLUME_BREAKOUT: 0.7,
                VolumeSignalType.VOLUME_REVERSAL: 0.6,
                VolumeSignalType.RETAIL_EXHAUSTION: 0.7
            }
            strength_factors.append(type_weights.get(signal_type, 0.6))
            
            # Confidence factor
            strength_factors.append(volume_analysis.confidence)
            
            # Calculate overall strength
            overall_strength = np.mean(strength_factors) if strength_factors else 0.5
            
            return min(1.0, float(overall_strength))
            
        except Exception as e:
            logger.error(f"Error calculating volume signal strength: {e}")
            return 0.5
    
    def _analyze_signal_factors(self, signal_type: VolumeSignalType, 
                              volume_analysis: VolumeAnalysis) -> Tuple[List[str], List[str]]:
        """Analyze supporting and risk factors for the signal"""
        try:
            supporting_factors = []
            risk_factors = []
            
            # Volume-based supporting factors
            if volume_analysis.volume_ratio > self.high_volume_threshold:
                supporting_factors.append("High volume confirmation")
            
            if volume_analysis.institutional_flow_score > 0.6:
                supporting_factors.append("Institutional flow detected")
            
            if volume_analysis.volume_condition == VolumeCondition.VOLUME_SURGE:
                supporting_factors.append("Volume surge detected")
            
            if abs(volume_analysis.money_flow - 50) > 20:
                supporting_factors.append("Strong money flow reading")
            
            # Risk factors
            if volume_analysis.volume_ratio < self.min_volume_confirmation:
                risk_factors.append("Low volume confirmation")
            
            if volume_analysis.retail_flow_score > 0.8:
                risk_factors.append("High retail sentiment (contrarian risk)")
            
            if volume_analysis.volume_condition == VolumeCondition.LOW_VOLUME:
                risk_factors.append("Overall low volume environment")
            
            if volume_analysis.confidence < 0.6:
                risk_factors.append("Low analysis confidence")
            
            return supporting_factors, risk_factors
            
        except Exception as e:
            logger.error(f"Error analyzing signal factors: {e}")
            return [], []
    
    def _enhance_volume_signal(self, signal: SignalEvent, volume_analysis: VolumeAnalysis,
                             df: pd.DataFrame) -> Optional[SignalEvent]:
        """Enhance volume signal with additional analysis"""
        try:
            # Add volume profile information if available
            if self.enable_volume_profile:
                signal.metadata['volume_profile_poc'] = volume_analysis.volume_profile_poc
                signal.metadata['volume_profile_vah'] = volume_analysis.volume_profile_vah
                signal.metadata['volume_profile_val'] = volume_analysis.volume_profile_val
            
            # Add support/resistance levels
            signal.metadata['volume_support_levels'] = volume_analysis.support_levels
            signal.metadata['volume_resistance_levels'] = volume_analysis.resistance_levels
            
            # Add market timing information
            signal.metadata['volume_trend'] = volume_analysis.volume_trend
            
            # Enhance with price context
            current_price = df['close'].iloc[-1]
            signal.metadata['price_vs_vwap'] = (current_price - volume_analysis.vwap_value) / volume_analysis.vwap_value
            
            return signal
            
        except Exception as e:
            logger.error(f"Error enhancing volume signal: {e}")
            return signal
    
    def _validate_volume_signal(self, signal: SignalEvent) -> bool:
        """Validate volume signal meets criteria"""
        try:
            # Basic validation
            if signal.strength < self.min_signal_strength:
                return False
            
            # Volume confirmation validation
            volume_confirmed = signal.metadata.get('volume_confirmation', False)
            if not volume_confirmed:
                return False
            
            # Risk-reward validation
            risk_reward = signal.metadata.get('risk_reward_ratio', 0)
            if risk_reward < 1.0:
                return False
            
            # Confidence validation
            confidence = signal.metadata.get('confidence', 0.5)
            if confidence < 0.6:
                return False
            
            # Direction validation
            if signal.direction not in ['bullish', 'bearish']:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating volume signal: {e}")
            return False
    
    def _combine_timeframe_volume_signals(self, symbol: str,
                                        timeframe_signals: Dict[str, List[SignalEvent]],
                                        timeframe_analyses: Dict[str, VolumeAnalysis]) -> List[SignalEvent]:
        """Combine volume signals from multiple timeframes"""
        try:
            if not timeframe_signals:
                return []
            
            # Timeframe weights for volume analysis
            timeframe_weights = {
                'M15': 0.3,
                'H1': 0.5,
                'H4': 0.8,
                'D1': 1.0
            }
            
            combined_signals = []
            
            # Group signals by direction and type
            signal_groups = defaultdict(list)
            
            for timeframe, signals in timeframe_signals.items():
                weight = timeframe_weights.get(timeframe, 0.5)
                for signal in signals:
                    key = f"{signal.direction}_{signal.metadata.get('signal_type')}"
                    signal_groups[key].append((timeframe, signal, weight))
            
            # Create combined signals for groups with sufficient confluence
            for key, signal_group in signal_groups.items():
                if len(signal_group) >= self.confluence_requirement:
                    # Calculate weighted confidence
                    total_weight = sum(weight for _, _, weight in signal_group)
                    weighted_strength = sum(signal.strength * weight for _, signal, weight in signal_group) / total_weight
                    
                    # Use highest timeframe signal as base
                    best_signal = max(signal_group, key=lambda x: timeframe_weights.get(x[0], 0))[1]
                    
                    # Create enhanced combined signal
                    combined_signal = SignalEvent(
                        event_type='MULTI_TIMEFRAME_VOLUME',
                        symbol=symbol,
                        timeframe='MULTI',
                        timestamp=datetime.utcnow(),
                        direction=best_signal.direction,
                        strength=min(0.95, weighted_strength),
                        level=best_signal.level,
                        metadata={
                            **best_signal.metadata,
                            'timeframe_confluence': total_weight,
                            'confirming_timeframes': [tf for tf, _, _ in signal_group],
                            'timeframe_count': len(signal_group),
                            'multi_timeframe_analysis': {
                                tf: {
                                    'volume_ratio': analysis.volume_ratio,
                                    'volume_condition': analysis.volume_condition.value,
                                    'institutional_score': analysis.institutional_flow_score
                                }
                                for tf, analysis in timeframe_analyses.items()
                            }
                        }
                    )
                    combined_signals.append(combined_signal)
            
            return combined_signals
            
        except Exception as e:
            logger.error(f"Error combining timeframe volume signals: {e}")
            return []
    
    def _filter_and_validate_volume_signals(self, signals: List[SignalEvent]) -> List[SignalEvent]:
        """Apply advanced filtering to volume signals"""
        try:
            if not signals:
                return signals
            
            filtered_signals = []
            current_time = datetime.utcnow()
            
            for signal in signals:
                # Strength filter
                if signal.strength < self.min_signal_strength:
                    continue
                
                # Volume confirmation filter
                volume_confirmed = signal.metadata.get('volume_confirmation', False)
                if not volume_confirmed:
                    continue
                
                # Confidence filter
                confidence = signal.metadata.get('confidence', 0.5)
                if confidence < 0.6:
                    continue
                
                # Risk-reward filter
                risk_reward = signal.metadata.get('risk_reward_ratio', 0)
                if risk_reward < 1.0:
                    continue
                
                # Time-based filter
                if self._is_signal_too_frequent(signal, current_time):
                    continue
                
                filtered_signals.append(signal)
            
            # Limit daily signals
            return filtered_signals[:self.max_signals_per_day]
            
        except Exception as e:
            logger.error(f"Error filtering volume signals: {e}")
            return signals
    
    def _is_signal_too_frequent(self, new_signal: SignalEvent, current_time: datetime) -> bool:
        """Check if signal is too frequent based on recent signals"""
        try:
            if not self.signal_history:
                return False
            
            recent_cutoff = current_time - timedelta(minutes=self.min_time_between_signals)
            
            recent_signals = [
                s for s in self.signal_history
                if (s.get('timestamp', current_time) > recent_cutoff and
                    s.get('symbol') == new_signal.symbol and
                    s.get('direction') == new_signal.direction)
            ]
            
            return len(recent_signals) > 0
            
        except Exception as e:
            logger.error(f"Error checking signal frequency: {e}")
            return False
    
    def _update_signal_history(self, signals: List[SignalEvent]):
        """Update signal history for performance tracking"""
        try:
            for signal in signals:
                self.signal_history.append({
                    'timestamp': signal.timestamp,
                    'symbol': signal.symbol,
                    'direction': signal.direction,
                    'strength': signal.strength,
                    'signal_type': signal.metadata.get('signal_type'),
                    'analysis_type': signal.metadata.get('analysis_type'),
                    'volume_ratio': signal.metadata.get('volume_ratio', 1.0),
                    'institutional_backing': signal.metadata.get('institutional_backing', False),
                    'confidence': signal.metadata.get('confidence', 0.5)
                })
                
                self.performance_monitor['signals_generated'] += 1
                
                if signal.metadata.get('volume_confirmation', False):
                    self.performance_monitor['volume_confirmed_signals'] += 1
                
                if signal.metadata.get('institutional_backing', False):
                    self.performance_monitor['institutional_signals'] += 1
            
        except Exception as e:
            logger.error(f"Error updating signal history: {e}")
    
    def _create_volume_analysis_summary(self, volume_analysis: VolumeAnalysis) -> Dict[str, Any]:
        """Create summary of volume analysis for metadata"""
        try:
            return {
                'volume_type': volume_analysis.volume_type.value,
                'volume_ratio': volume_analysis.volume_ratio,
                'volume_condition': volume_analysis.volume_condition.value,
                'volume_trend': volume_analysis.volume_trend,
                'obv_value': volume_analysis.obv_value,
                'vwap_value': volume_analysis.vwap_value,
                'money_flow': volume_analysis.money_flow,
                'institutional_score': volume_analysis.institutional_flow_score,
                'retail_score': volume_analysis.retail_flow_score,
                'confidence': volume_analysis.confidence
            }
            
        except Exception as e:
            logger.error(f"Error creating volume analysis summary: {e}")
            return {}
    
    def get_required_data(self) -> Dict[str, List[str]]:
        """Return required data specification"""
        return {
            '*': self.timeframes  # All symbols need specified timeframes
        }
    
    def validate_signal(self, signal: SignalEvent) -> bool:
        """Validate individual volume signal"""
        try:
            # Basic validation
            if not signal or signal.strength < self.min_signal_strength:
                return False
            
            # Direction validation
            if signal.direction not in ['bullish', 'bearish']:
                return False
            
            # Volume-specific validation
            signal_type = signal.metadata.get('signal_type')
            if not signal_type:
                return False
            
            analysis_type = signal.metadata.get('analysis_type')
            if not analysis_type:
                return False
            
            # Volume confirmation validation
            volume_confirmed = signal.metadata.get('volume_confirmation', False)
            if not volume_confirmed:
                return False
            
            # Risk-reward validation
            risk_reward = signal.metadata.get('risk_reward_ratio', 0)
            if risk_reward < 1.0:
                return False
            
            # Confidence validation
            confidence = signal.metadata.get('confidence', 0.5)
            if confidence < 0.6:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating signal: {e}")
            return False
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive volume strategy performance summary"""
        try:
            return {
                'signals_generated': self.performance_monitor['signals_generated'],
                'volume_confirmed_signals': self.performance_monitor['volume_confirmed_signals'],
                'institutional_signals': self.performance_monitor['institutional_signals'],
                'successful_volume_trades': self.performance_monitor['successful_volume_trades'],
                'failed_volume_trades': self.performance_monitor['failed_volume_trades'],
                'volume_confirmation_rate': (
                    self.performance_monitor['volume_confirmed_signals'] / 
                    max(1, self.performance_monitor['signals_generated'])
                ),
                'institutional_signal_rate': (
                    self.performance_monitor['institutional_signals'] / 
                    max(1, self.performance_monitor['signals_generated'])
                ),
                'volume_success_rate': (
                    self.performance_monitor['successful_volume_trades'] / 
                    max(1, self.performance_monitor['signals_generated'])
                ),
                'avg_volume_accuracy': self.performance_monitor['avg_volume_accuracy'],
                'best_volume_profit': self.performance_monitor['best_volume_profit'],
                'worst_volume_loss': self.performance_monitor['worst_volume_loss'],
                'volume_history_length': len(self.volume_history),
                'signal_history_length': len(self.signal_history),
                'strategy_name': self.name,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {}
    
    async def cleanup(self):
        """Cleanup strategy resources"""
        try:
            logger.info(f"Cleaning up Enhanced Volume Strategy: {self.name}")
            
            # Clear history and caches
            self.volume_history.clear()
            self.signal_history.clear()
            self.performance_metrics.clear()
            self.institutional_flow_tracking.clear()
            
            # Clear institutional detection data
            if hasattr(self, 'institutional_detector'):
                self.institutional_detector['large_order_tracker'].clear()
                self.institutional_detector['flow_patterns'].clear()
                self.institutional_detector['smart_money_indicators'].clear()
                self.institutional_detector['retail_sentiment_tracker'].clear()
            
            # Clear volume profile data
            if hasattr(self, 'volume_profile_data'):
                self.volume_profile_data['price_levels'].clear()
                self.volume_profile_data['volume_distribution'].clear()
                self.volume_profile_data['poc_history'].clear()
                self.volume_profile_data['value_area_history'].clear()
            
            # Reset performance monitor
            self.performance_monitor = {
                'signals_generated': 0,
                'volume_confirmed_signals': 0,
                'institutional_signals': 0,
                'successful_volume_trades': 0,
                'failed_volume_trades': 0,
                'avg_volume_accuracy': 0.0,
                'best_volume_profit': 0.0,
                'worst_volume_loss': 0.0,
                'volume_analysis_effectiveness': defaultdict(list)
            }
            
            logger.info("Enhanced Volume Strategy cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Export the enhanced strategy
__all__ = ['EnhancedVolumeStrategy', 'VolumeAnalysisType', 'VolumeCondition', 'VolumeSignalType', 'VolumeAnalysis']

# Compatibility alias
VolumeStrategy = EnhancedVolumeStrategy