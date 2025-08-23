import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os
from pathlib import Path

# Add project paths
current_dir = Path(__file__).parent.parent
sys.path.append(str(current_dir))

# Import compatibility modules
try:
    from strategies.unified_signals import UnifiedTradingSignal, generate_basic_signal
except ImportError:
    class UnifiedTradingSignal:
        def __init__(self, signal="HOLD", confidence=0.5, price=1.0, reason=""):
            self.signal = signal
            self.confidence = confidence
            self.price = price
            self.reason = reason

try:
    from strategies.numpy_compatibility import NaN
except ImportError:
    NaN = np.nan

try:
    from utils.logger import setup_logging, logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    def setup_logging(*args, **kwargs):
        return logger

try:
    from utils.price_action import calculate_fibonacci_retracements, identify_support_resistance
except ImportError:
    def calculate_fibonacci_retracements(high, low):
        return {'level_0': high, 'level_100': low}
    def identify_support_resistance(df, window=20):
        return {'support': 1.0, 'resistance': 1.0}

# NumPy compatibility
try:
    from numpy import NaN
except ImportError:
    NaN = np.nan


import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os
from pathlib import Path

# Add strategies folder to path for imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

try:
    from unified_signals import generate_basic_signal, calculate_sma, calculate_ema, calculate_rsi
except ImportError:
    # Fallback functions if unified_signals not available
    def generate_basic_signal(data, symbol="EURUSD"):
        return {'signal': 'HOLD', 'confidence': 0.5, 'price': 1.0, 'reason': 'Fallback'}
    def calculate_sma(data, period):
        return data.rolling(window=period).mean()
    def calculate_ema(data, period):
        return data.ewm(span=period).mean()
    def calculate_rsi(data, period=14):
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

# Numpy compatibility
NaN = np.nan

"""
Enhanced Pivot Point Strategy Implementation
==========================================
Professional-grade pivot point trading strategy with advanced analytics,
multi-timeframe analysis, and comprehensive risk management.

Features:
- Multiple pivot point calculation methods (Standard, Fibonacci, Camarilla, Woodie's, DeMark)
- Advanced support/resistance level detection and validation
- Multi-timeframe pivot point confluence analysis
- Market structure integration with pivot levels
- Volume profile analysis at key pivot levels
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
from strategies.base_strategy import BaseStrategy, SignalEvent, register_strategy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')

class PivotType(Enum):
    
    def analyze(self, data, symbol="EURUSD"):
        """Kelly-compatible analyze method for Pivot Point Strategy"""
        try:
            if data is None or data.empty or len(data) < 20:
                return {
                    'signal': 'HOLD',
                    'confidence': 0.0,
                    'price': 1.0,
                    'reason': 'Insufficient data'
                }
            
            # Use existing strategy logic if available
            if hasattr(self, 'generate_signal'):
                result = self.generate_signal(data, symbol)
                if isinstance(result, dict):
                    return result
            
            # Default implementation based on strategy type
            current_price = data['close'].iloc[-1]
            
            # Simple trend-following logic as fallback
            if len(data) >= 50:
                ma_20 = data['close'].rolling(20).mean().iloc[-1]
                ma_50 = data['close'].rolling(50).mean().iloc[-1]
                
                if current_price > ma_20 > ma_50:
                    return {
                        'signal': 'BUY',
                        'confidence': 0.65,
                        'price': current_price,
                        'reason': f'Pivot Point Strategy bullish trend'
                    }
                elif current_price < ma_20 < ma_50:
                    return {
                        'signal': 'SELL', 
                        'confidence': 0.65,
                        'price': current_price,
                        'reason': f'Pivot Point Strategy bearish trend'
                    }
            
            return {
                'signal': 'HOLD',
                'confidence': 0.4,
                'price': current_price,
                'reason': f'Pivot Point Strategy neutral'
            }
            
        except Exception as e:
            return {
                'signal': 'HOLD',
                'confidence': 0.0,
                'price': 1.0,
                'reason': f'Pivot Point Strategy error: {str(e)}'
            }

    """Types of pivot point calculations"""
    STANDARD = "standard"
    FIBONACCI = "fibonacci"
    CAMARILLA = "camarilla"
    WOODIE = "woodie"
    DEMARK = "demark"
    CLASSIC = "classic"

class PivotLevel(Enum):
    """Pivot point levels"""
    PP = "pivot_point"      # Main pivot point
    R1 = "resistance_1"     # First resistance
    R2 = "resistance_2"     # Second resistance  
    R3 = "resistance_3"     # Third resistance
    S1 = "support_1"        # First support
    S2 = "support_2"        # Second support
    S3 = "support_3"        # Third support

class PivotAction(Enum):
    """Pivot-based trading actions"""
    BOUNCE_BUY = "bounce_buy"           # Buy on support bounce
    BOUNCE_SELL = "bounce_sell"         # Sell on resistance bounce
    BREAKOUT_BUY = "breakout_buy"       # Buy on resistance breakout
    BREAKDOWN_SELL = "breakdown_sell"   # Sell on support breakdown
    RETEST_BUY = "retest_buy"          # Buy on successful retest
    RETEST_SELL = "retest_sell"        # Sell on successful retest

class MarketSession(Enum):
    """Market trading sessions for pivot calculation"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SESSION_BASED = "session_based"

@dataclass
class PivotPointData:
    """Enhanced pivot point data structure"""
    timestamp: datetime
    pivot_type: PivotType
    session_type: MarketSession
    pivot_point: float
    resistance_1: float
    resistance_2: float
    resistance_3: float
    support_1: float
    support_2: float
    support_3: float
    high: float
    low: float
    close: float
    volume: Optional[float] = None
    strength_score: float = 0.0
    confidence: float = 0.0
    market_structure: str = "neutral"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PivotSignal:
    """Enhanced pivot signal with comprehensive analysis"""
    timestamp: datetime
    symbol: str
    timeframe: str
    direction: str  # 'bullish', 'bearish'
    strength: float  # 0.0 to 1.0
    pivot_action: PivotAction
    pivot_level: PivotLevel
    pivot_value: float
    entry_price: float
    target_price: float
    stop_loss: float
    confidence: float
    pivot_data: PivotPointData
    volume_confirmation: bool
    multi_timeframe_alignment: bool
    risk_reward_ratio: float
    expected_move: float
    level_strength: float
    touches_count: int
    age_hours: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@register_strategy
class EnhancedPivotPointStrategy(BaseStrategy):
    """
    Enhanced Pivot Point Strategy - Professional Implementation
    
    Advanced pivot point strategy incorporating multiple calculation methods,
    multi-timeframe analysis, and sophisticated level validation
    for institutional-grade trading applications.
    
    Key Features:
    - Multiple pivot point methodologies
    - Multi-timeframe pivot confluence
    - Advanced level strength analysis
    - Market structure integration
    - Volume confirmation at levels
    - Advanced risk management
    - Comprehensive performance tracking
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize enhanced pivot point strategy
        
        Args:
            name: Strategy name
            config: Configuration dictionary with strategy parameters
        """
        super().__init__(name, config)
        
        # Core pivot point parameters
        self.pivot_types = config.get('pivot_types', [
            PivotType.STANDARD, 
            PivotType.FIBONACCI, 
            PivotType.CAMARILLA
        ])
        self.primary_pivot_type = config.get('primary_pivot_type', PivotType.STANDARD)
        self.session_types = config.get('session_types', [MarketSession.DAILY, MarketSession.WEEKLY])
        
        # Level detection parameters
        self.level_proximity_threshold = config.get('level_proximity_threshold', 0.0005)  # 5 pips
        self.min_level_strength = config.get('min_level_strength', 0.6)
        self.level_age_limit_hours = config.get('level_age_limit_hours', 168)  # 1 week
        
        # Multi-timeframe analysis
        self.timeframes = config.get('timeframes', ['M15', 'H1', 'H4', 'D1'])
        self.primary_timeframe = config.get('primary_timeframe', 'H1')
        self.confluence_required = config.get('confluence_required', True)
        
        # Signal generation parameters
        self.bounce_threshold = config.get('bounce_threshold', 0.0003)  # 3 pips
        self.breakout_threshold = config.get('breakout_threshold', 0.0005)  # 5 pips
        self.min_signal_strength = config.get('min_signal_strength', 0.6)
        
        # Volume analysis parameters
        self.volume_confirmation_required = config.get('volume_confirmation_required', True)
        self.volume_threshold_multiplier = config.get('volume_threshold_multiplier', 1.5)
        self.volume_lookback = config.get('volume_lookback', 20)
        
        # Risk management parameters
        self.max_position_size = config.get('max_position_size', 0.02)
        self.stop_loss_atr_multiple = config.get('stop_loss_atr_multiple', 2.0)
        self.take_profit_ratio = config.get('take_profit_ratio', 2.0)
        
        # Advanced features
        self.enable_fibonacci_extensions = config.get('enable_fibonacci_extensions', True)
        self.enable_camarilla_levels = config.get('enable_camarilla_levels', True)
        self.enable_market_structure_filter = config.get('enable_market_structure_filter', True)
        
        # Performance tracking
        self.pivot_history = deque(maxlen=5000)
        self.signal_history = deque(maxlen=1000)
        self.performance_metrics = defaultdict(list)
        self.level_touch_history = defaultdict(list)
        
        # Technical parameters
        self.atr_period = config.get('atr_period', 14)
        self.rsi_period = config.get('rsi_period', 14)
        self.stoch_period = config.get('stoch_period', 14)
        
        # Signal filtering parameters
        self.max_signals_per_day = config.get('max_signals_per_day', 3)
        self.min_time_between_signals = config.get('min_time_between_signals', 60)  # minutes
        
        logger.info(f"Enhanced Pivot Point Strategy '{name}' initialized successfully")
        logger.info(f"Configuration: {self._log_safe_config()}")
    
    def _log_safe_config(self) -> Dict[str, Any]:
        """Create logging-safe configuration summary"""
        return {
            'pivot_types': len(self.pivot_types),
            'primary_pivot_type': self.primary_pivot_type.value,
            'session_types': len(self.session_types),
            'timeframes': len(self.timeframes),
            'confluence_required': self.confluence_required,
            'volume_confirmation_required': self.volume_confirmation_required
        }
    
    async def initialize(self) -> bool:
        """Initialize strategy with enhanced setup"""
        try:
            logger.info(f"Initializing Enhanced Pivot Point Strategy: {self.name}")
            
            # Validate configuration
            if not self._validate_configuration():
                logger.error("Configuration validation failed")
                return False
            
            # Initialize pivot calculators
            self._initialize_pivot_calculators()
            
            # Setup level detection
            self._setup_level_detection()
            
            # Initialize performance monitoring
            self._setup_performance_monitoring()
            
            logger.info("Enhanced Pivot Point Strategy initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing Enhanced Pivot Point Strategy: {e}")
            return False
    
    def _validate_configuration(self) -> bool:
        """Validate strategy configuration parameters"""
        try:
            # Validate pivot types
            if not self.pivot_types:
                logger.error("No pivot types specified")
                return False
            
            if self.primary_pivot_type not in self.pivot_types:
                logger.error(f"Primary pivot type {self.primary_pivot_type} not in pivot types list")
                return False
            
            # Validate thresholds
            if not (0.0001 <= self.level_proximity_threshold <= 0.01):
                logger.error(f"Invalid level_proximity_threshold: {self.level_proximity_threshold}")
                return False
            
            if not (0.0001 <= self.bounce_threshold <= 0.01):
                logger.error(f"Invalid bounce_threshold: {self.bounce_threshold}")
                return False
            
            if not (0.0001 <= self.breakout_threshold <= 0.01):
                logger.error(f"Invalid breakout_threshold: {self.breakout_threshold}")
                return False
            
            # Validate timeframes
            if not self.timeframes:
                logger.error("No timeframes specified")
                return False
            
            if self.primary_timeframe not in self.timeframes:
                logger.error(f"Primary timeframe {self.primary_timeframe} not in timeframes list")
                return False
            
            # Validate strength parameters
            if not (0.1 <= self.min_level_strength <= 1.0):
                logger.error(f"Invalid min_level_strength: {self.min_level_strength}")
                return False
            
            if not (0.1 <= self.min_signal_strength <= 1.0):
                logger.error(f"Invalid min_signal_strength: {self.min_signal_strength}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating configuration: {e}")
            return False
    
    def _initialize_pivot_calculators(self):
        """Initialize pivot point calculators"""
        self.pivot_calculators = {
            PivotType.STANDARD: self._calculate_standard_pivots,
            PivotType.FIBONACCI: self._calculate_fibonacci_pivots,
            PivotType.CAMARILLA: self._calculate_camarilla_pivots,
            PivotType.WOODIE: self._calculate_woodie_pivots,
            PivotType.DEMARK: self._calculate_demark_pivots
        }
        logger.info("Pivot point calculators initialized")
    
    def _setup_level_detection(self):
        """Setup level detection and validation"""
        self.level_validators = {
            'strength': self._calculate_level_strength,
            'age': self._calculate_level_age,
            'touches': self._count_level_touches,
            'volume': self._validate_volume_at_level
        }
        logger.info("Level detection setup complete")
    
    def _setup_performance_monitoring(self):
        """Setup performance monitoring and analytics"""
        self.performance_monitor = {
            'signals_generated': 0,
            'successful_bounces': 0,
            'successful_breakouts': 0,
            'failed_signals': 0,
            'avg_signal_accuracy': 0.0,
            'best_pivot_profit': 0.0,
            'worst_pivot_loss': 0.0,
            'level_effectiveness': defaultdict(list)
        }
        logger.info("Performance monitoring setup complete")
    
    def generate_signals(self, data: Dict[str, pd.DataFrame]) -> List[SignalEvent]:
        """
        Generate enhanced pivot point signals
        
        Args:
            data: Dictionary of market data by symbol and timeframe
            
        Returns:
            List of enhanced pivot point signals
        """
        try:
            signals = []
            
            for symbol, timeframe_data in data.items():
                if isinstance(timeframe_data, dict):
                    # Multi-timeframe pivot analysis
                    symbol_signals = self._analyze_multi_timeframe_pivots(
                        symbol, timeframe_data
                    )
                    signals.extend(symbol_signals)
                else:
                    # Single timeframe analysis
                    symbol_signals = self._analyze_single_timeframe_pivots(
                        symbol, self.primary_timeframe, timeframe_data
                    )
                    signals.extend(symbol_signals)
            
            # Apply advanced filtering
            filtered_signals = self._filter_and_validate_pivot_signals(signals)
            
            # Update performance tracking
            self._update_signal_history(filtered_signals)
            
            logger.info(f"Generated {len(filtered_signals)} pivot signals from {len(signals)} candidates")
            return filtered_signals
            
        except Exception as e:
            logger.error(f"Error generating pivot signals: {e}")
            return []
    
    def _analyze_multi_timeframe_pivots(self, symbol: str, 
                                      timeframe_data: Dict[str, pd.DataFrame]) -> List[SignalEvent]:
        """Analyze pivot points across multiple timeframes"""
        try:
            timeframe_pivots = {}
            timeframe_signals = {}
            
            # Calculate pivots for each timeframe
            for timeframe, df in timeframe_data.items():
                if timeframe in self.timeframes and len(df) >= 50:
                    pivots = self._calculate_all_pivot_types(df, timeframe)
                    timeframe_pivots[timeframe] = pivots
                    
                    # Generate signals for this timeframe
                    tf_signals = self._generate_timeframe_pivot_signals(
                        symbol, timeframe, df, pivots
                    )
                    timeframe_signals[timeframe] = tf_signals
            
            # Combine multi-timeframe analysis
            combined_signals = self._combine_timeframe_pivot_signals(
                symbol, timeframe_signals, timeframe_pivots
            )
            
            return combined_signals
            
        except Exception as e:
            logger.error(f"Error in multi-timeframe pivot analysis for {symbol}: {e}")
            return []
    
    def _analyze_single_timeframe_pivots(self, symbol: str, timeframe: str, 
                                       df: pd.DataFrame) -> List[SignalEvent]:
        """Analyze pivot points for single timeframe"""
        try:
            if len(df) < 50:
                return []
            
            # Calculate all pivot types
            pivots = self._calculate_all_pivot_types(df, timeframe)
            
            # Generate signals
            signals = self._generate_timeframe_pivot_signals(
                symbol, timeframe, df, pivots
            )
            
            return signals
            
        except Exception as e:
            logger.error(f"Error in single timeframe pivot analysis: {e}")
            return []
    
    def _calculate_all_pivot_types(self, df: pd.DataFrame, timeframe: str) -> Dict[PivotType, PivotPointData]:
        """Calculate all configured pivot point types"""
        try:
            all_pivots = {}
            
            for pivot_type in self.pivot_types:
                try:
                    calculator = self.pivot_calculators.get(pivot_type)
                    if calculator:
                        pivot_data = calculator(df, timeframe)
                        if pivot_data:
                            all_pivots[pivot_type] = pivot_data
                            
                except Exception as e:
                    logger.warning(f"Error calculating {pivot_type} pivots: {e}")
                    continue
            
            return all_pivots
            
        except Exception as e:
            logger.error(f"Error calculating pivot types: {e}")
            return {}
    
    def _calculate_standard_pivots(self, df: pd.DataFrame, timeframe: str) -> Optional[PivotPointData]:
        """Calculate standard pivot points"""
        try:
            if len(df) < 2:
                return None
            
            # Get previous day's data
            prev_day = self._get_previous_session_data(df, timeframe)
            if not prev_day:
                return None
            
            high = prev_day['high']
            low = prev_day['low']
            close = prev_day['close']
            volume = prev_day.get('volume', 0)
            
            # Standard pivot calculation
            pivot_point = (high + low + close) / 3
            
            # Standard support and resistance levels
            r1 = (2 * pivot_point) - low
            s1 = (2 * pivot_point) - high
            r2 = pivot_point + (high - low)
            s2 = pivot_point - (high - low)
            r3 = high + 2 * (pivot_point - low)
            s3 = low - 2 * (high - pivot_point)
            
            pivot_data = PivotPointData(
                timestamp=datetime.utcnow(),
                pivot_type=PivotType.STANDARD,
                session_type=self._determine_session_type(timeframe),
                pivot_point=pivot_point,
                resistance_1=r1,
                resistance_2=r2,
                resistance_3=r3,
                support_1=s1,
                support_2=s2,
                support_3=s3,
                high=high,
                low=low,
                close=close,
                volume=volume
            )
            
            # Calculate additional metrics
            pivot_data.strength_score = self._calculate_pivot_strength(pivot_data, df)
            pivot_data.confidence = self._calculate_pivot_confidence(pivot_data, df)
            
            return pivot_data
            
        except Exception as e:
            logger.error(f"Error calculating standard pivots: {e}")
            return None
    
    def _calculate_fibonacci_pivots(self, df: pd.DataFrame, timeframe: str) -> Optional[PivotPointData]:
        """Calculate Fibonacci pivot points"""
        try:
            if len(df) < 2:
                return None
            
            prev_day = self._get_previous_session_data(df, timeframe)
            if not prev_day:
                return None
            
            high = prev_day['high']
            low = prev_day['low']
            close = prev_day['close']
            volume = prev_day.get('volume', 0)
            
            # Fibonacci pivot calculation
            pivot_point = (high + low + close) / 3
            range_val = high - low
            
            # Fibonacci levels
            r1 = pivot_point + 0.382 * range_val
            r2 = pivot_point + 0.618 * range_val
            r3 = pivot_point + 1.000 * range_val
            s1 = pivot_point - 0.382 * range_val
            s2 = pivot_point - 0.618 * range_val
            s3 = pivot_point - 1.000 * range_val
            
            pivot_data = PivotPointData(
                timestamp=datetime.utcnow(),
                pivot_type=PivotType.FIBONACCI,
                session_type=self._determine_session_type(timeframe),
                pivot_point=pivot_point,
                resistance_1=r1,
                resistance_2=r2,
                resistance_3=r3,
                support_1=s1,
                support_2=s2,
                support_3=s3,
                high=high,
                low=low,
                close=close,
                volume=volume
            )
            
            pivot_data.strength_score = self._calculate_pivot_strength(pivot_data, df)
            pivot_data.confidence = self._calculate_pivot_confidence(pivot_data, df)
            
            return pivot_data
            
        except Exception as e:
            logger.error(f"Error calculating Fibonacci pivots: {e}")
            return None
    
    def _calculate_camarilla_pivots(self, df: pd.DataFrame, timeframe: str) -> Optional[PivotPointData]:
        """Calculate Camarilla pivot points"""
        try:
            if len(df) < 2:
                return None
            
            prev_day = self._get_previous_session_data(df, timeframe)
            if not prev_day:
                return None
            
            high = prev_day['high']
            low = prev_day['low']
            close = prev_day['close']
            volume = prev_day.get('volume', 0)
            
            # Camarilla pivot calculation (pivot point is previous close)
            pivot_point = close
            range_val = high - low
            
            # Camarilla levels
            r1 = close + (range_val * 1.1 / 12)
            r2 = close + (range_val * 1.1 / 6)
            r3 = close + (range_val * 1.1 / 4)
            s1 = close - (range_val * 1.1 / 12)
            s2 = close - (range_val * 1.1 / 6)
            s3 = close - (range_val * 1.1 / 4)
            
            pivot_data = PivotPointData(
                timestamp=datetime.utcnow(),
                pivot_type=PivotType.CAMARILLA,
                session_type=self._determine_session_type(timeframe),
                pivot_point=pivot_point,
                resistance_1=r1,
                resistance_2=r2,
                resistance_3=r3,
                support_1=s1,
                support_2=s2,
                support_3=s3,
                high=high,
                low=low,
                close=close,
                volume=volume
            )
            
            pivot_data.strength_score = self._calculate_pivot_strength(pivot_data, df)
            pivot_data.confidence = self._calculate_pivot_confidence(pivot_data, df)
            
            return pivot_data
            
        except Exception as e:
            logger.error(f"Error calculating Camarilla pivots: {e}")
            return None
    
    def _calculate_woodie_pivots(self, df: pd.DataFrame, timeframe: str) -> Optional[PivotPointData]:
        """Calculate Woodie's pivot points"""
        try:
            if len(df) < 2:
                return None
            
            prev_day = self._get_previous_session_data(df, timeframe)
            if not prev_day:
                return None
            
            high = prev_day['high']
            low = prev_day['low']
            close = prev_day['close']
            volume = prev_day.get('volume', 0)
            
            # Woodie's pivot calculation (emphasizes current day's open)
            current_open = df['open'].iloc[-1]
            pivot_point = (high + low + 2 * current_open) / 4
            
            # Woodie's levels
            r1 = (2 * pivot_point) - low
            s1 = (2 * pivot_point) - high
            r2 = pivot_point + (high - low)
            s2 = pivot_point - (high - low)
            r3 = high + 2 * (pivot_point - low)
            s3 = low - 2 * (high - pivot_point)
            
            pivot_data = PivotPointData(
                timestamp=datetime.utcnow(),
                pivot_type=PivotType.WOODIE,
                session_type=self._determine_session_type(timeframe),
                pivot_point=pivot_point,
                resistance_1=r1,
                resistance_2=r2,
                resistance_3=r3,
                support_1=s1,
                support_2=s2,
                support_3=s3,
                high=high,
                low=low,
                close=close,
                volume=volume
            )
            
            pivot_data.strength_score = self._calculate_pivot_strength(pivot_data, df)
            pivot_data.confidence = self._calculate_pivot_confidence(pivot_data, df)
            
            return pivot_data
            
        except Exception as e:
            logger.error(f"Error calculating Woodie pivots: {e}")
            return None
    
    def _calculate_demark_pivots(self, df: pd.DataFrame, timeframe: str) -> Optional[PivotPointData]:
        """Calculate DeMark pivot points"""
        try:
            if len(df) < 2:
                return None
            
            prev_day = self._get_previous_session_data(df, timeframe)
            if not prev_day:
                return None
            
            high = prev_day['high']
            low = prev_day['low']
            close = prev_day['close']
            open_price = prev_day.get('open', close)
            volume = prev_day.get('volume', 0)
            
            # DeMark pivot calculation
            if close < open_price:
                x = high + (2 * low) + close
            elif close > open_price:
                x = (2 * high) + low + close
            else:
                x = high + low + (2 * close)
            
            pivot_point = x / 4
            
            # DeMark levels (simplified)
            r1 = x / 2 - low
            s1 = x / 2 - high
            r2 = pivot_point + (high - low)
            s2 = pivot_point - (high - low)
            r3 = high + 2 * (pivot_point - low)
            s3 = low - 2 * (high - pivot_point)
            
            pivot_data = PivotPointData(
                timestamp=datetime.utcnow(),
                pivot_type=PivotType.DEMARK,
                session_type=self._determine_session_type(timeframe),
                pivot_point=pivot_point,
                resistance_1=r1,
                resistance_2=r2,
                resistance_3=r3,
                support_1=s1,
                support_2=s2,
                support_3=s3,
                high=high,
                low=low,
                close=close,
                volume=volume
            )
            
            pivot_data.strength_score = self._calculate_pivot_strength(pivot_data, df)
            pivot_data.confidence = self._calculate_pivot_confidence(pivot_data, df)
            
            return pivot_data
            
        except Exception as e:
            logger.error(f"Error calculating DeMark pivots: {e}")
            return None
    
    def _get_previous_session_data(self, df: pd.DataFrame, timeframe: str) -> Optional[Dict[str, float]]:
        """Get previous session's OHLC data"""
        try:
            if len(df) < 2:
                return None
            
            # For simplicity, use previous bar data
            # In production, this would be more sophisticated based on trading sessions
            prev_bar = df.iloc[-2]
            
            return {
                'open': prev_bar.get('open', prev_bar['close']),
                'high': prev_bar['high'],
                'low': prev_bar['low'],
                'close': prev_bar['close'],
                'volume': prev_bar.get('volume', 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting previous session data: {e}")
            return None
    
    def _determine_session_type(self, timeframe: str) -> MarketSession:
        """Determine session type based on timeframe"""
        try:
            timeframe_session_map = {
                'M1': MarketSession.SESSION_BASED,
                'M5': MarketSession.SESSION_BASED,
                'M15': MarketSession.SESSION_BASED,
                'M30': MarketSession.SESSION_BASED,
                'H1': MarketSession.DAILY,
                'H4': MarketSession.DAILY,
                'D1': MarketSession.WEEKLY,
                'W1': MarketSession.MONTHLY
            }
            
            return timeframe_session_map.get(timeframe, MarketSession.DAILY)
            
        except Exception as e:
            logger.error(f"Error determining session type: {e}")
            return MarketSession.DAILY
    
    def _calculate_pivot_strength(self, pivot_data: PivotPointData, df: pd.DataFrame) -> float:
        """Calculate strength of pivot levels based on historical interaction"""
        try:
            strength_factors = []
            current_price = df['close'].iloc[-1]
            
            # Range factor (wider range = stronger levels)
            price_range = pivot_data.high - pivot_data.low
            avg_range = df['high'].rolling(20).max() - df['low'].rolling(20).min()
            range_factor = min(1.0, price_range / avg_range.iloc[-1]) if avg_range.iloc[-1] > 0 else 0.5
            strength_factors.append(range_factor)
            
            # Volume factor
            if pivot_data.volume and pivot_data.volume > 0:
                avg_volume = df['volume'].rolling(20).mean().iloc[-1] if 'volume' in df.columns else 1
                volume_factor = min(1.0, pivot_data.volume / avg_volume) if avg_volume > 0 else 0.5
                strength_factors.append(volume_factor)
            
            # Proximity to round numbers (psychological levels)
            levels = [
                pivot_data.pivot_point, pivot_data.resistance_1, pivot_data.resistance_2,
                pivot_data.support_1, pivot_data.support_2
            ]
            
            round_number_strength = 0.0
            for level in levels:
                # Check proximity to round numbers (00, 50 levels)
                level_str = f"{level:.5f}"
                if level_str.endswith('00000') or level_str.endswith('50000'):
                    round_number_strength += 0.2
                elif level_str.endswith('0000') or level_str.endswith('5000'):
                    round_number_strength += 0.1
            
            strength_factors.append(min(1.0, round_number_strength))
            
            # Calculate overall strength
            overall_strength = np.mean(strength_factors) if strength_factors else 0.5
            
            return float(overall_strength)
            
        except Exception as e:
            logger.error(f"Error calculating pivot strength: {e}")
            return 0.5
    
    def _calculate_pivot_confidence(self, pivot_data: PivotPointData, df: pd.DataFrame) -> float:
        """Calculate confidence in pivot levels"""
        try:
            confidence_factors = []
            
            # Data quality factor
            if len(df) >= 50:
                confidence_factors.append(0.9)
            elif len(df) >= 20:
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.5)
            
            # Volatility consistency factor
            returns = df['close'].pct_change().dropna()
            if len(returns) > 10:
                volatility = returns.std()
                recent_volatility = returns.tail(5).std()
                
                if abs(volatility - recent_volatility) / volatility < 0.5:
                    confidence_factors.append(0.8)
                else:
                    confidence_factors.append(0.6)
            
            # Pivot type reliability factor
            type_reliability = {
                PivotType.STANDARD: 0.8,
                PivotType.FIBONACCI: 0.7,
                PivotType.CAMARILLA: 0.6,
                PivotType.WOODIE: 0.7,
                PivotType.DEMARK: 0.6
            }
            confidence_factors.append(type_reliability.get(pivot_data.pivot_type, 0.6))
            
            # Calculate overall confidence
            overall_confidence = np.mean(confidence_factors) if confidence_factors else 0.5
            
            return float(overall_confidence)
            
        except Exception as e:
            logger.error(f"Error calculating pivot confidence: {e}")
            return 0.5
    
    def _generate_timeframe_pivot_signals(self, symbol: str, timeframe: str, df: pd.DataFrame,
                                        pivots: Dict[PivotType, PivotPointData]) -> List[SignalEvent]:
        """Generate pivot signals for specific timeframe"""
        try:
            signals = []
            
            if not pivots:
                return signals
            
            # Use primary pivot type for signal generation
            primary_pivot = pivots.get(self.primary_pivot_type)
            if not primary_pivot:
                return signals
            
            current_price = df['close'].iloc[-1]
            current_time = datetime.utcnow()
            
            # Check all pivot levels for signal opportunities
            levels_to_check = [
                (PivotLevel.R1, primary_pivot.resistance_1, 'resistance'),
                (PivotLevel.R2, primary_pivot.resistance_2, 'resistance'),
                (PivotLevel.R3, primary_pivot.resistance_3, 'resistance'),
                (PivotLevel.S1, primary_pivot.support_1, 'support'),
                (PivotLevel.S2, primary_pivot.support_2, 'support'),
                (PivotLevel.S3, primary_pivot.support_3, 'support'),
                (PivotLevel.PP, primary_pivot.pivot_point, 'pivot')
            ]
            
            for level_type, level_price, level_category in levels_to_check:
                # Check for bounce signals
                bounce_signal = self._check_bounce_signal(
                    current_price, level_price, level_category, df
                )
                
                if bounce_signal:
                    signal = self._create_pivot_signal(
                        symbol, timeframe, bounce_signal, level_type, level_price,
                        primary_pivot, df, current_time
                    )
                    if signal:
                        signals.append(signal)
                
                # Check for breakout signals
                breakout_signal = self._check_breakout_signal(
                    current_price, level_price, level_category, df
                )
                
                if breakout_signal:
                    signal = self._create_pivot_signal(
                        symbol, timeframe, breakout_signal, level_type, level_price,
                        primary_pivot, df, current_time
                    )
                    if signal:
                        signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error generating timeframe pivot signals: {e}")
            return []
    
    def _check_bounce_signal(self, current_price: float, level_price: float, 
                           level_category: str, df: pd.DataFrame) -> Optional[str]:
        """Check for bounce signal at pivot level"""
        try:
            if len(df) < 3:
                return None
            
            # Get recent price action
            recent_lows = df['low'].tail(3)
            recent_highs = df['high'].tail(3)
            
            # Check for support bounce
            if level_category in ['support', 'pivot']:
                # Price touched or came close to support and is now moving up
                min_low = recent_lows.min()
                if (abs(min_low - level_price) <= self.bounce_threshold and 
                    current_price > min_low + self.bounce_threshold):
                    
                    # Additional confirmation: price should be above level now
                    if current_price > level_price:
                        return 'bounce_buy'
            
            # Check for resistance bounce
            elif level_category == 'resistance':
                # Price touched or came close to resistance and is now moving down
                max_high = recent_highs.max()
                if (abs(max_high - level_price) <= self.bounce_threshold and 
                    current_price < max_high - self.bounce_threshold):
                    
                    # Additional confirmation: price should be below level now
                    if current_price < level_price:
                        return 'bounce_sell'
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking bounce signal: {e}")
            return None
    
    def _check_breakout_signal(self, current_price: float, level_price: float,
                             level_category: str, df: pd.DataFrame) -> Optional[str]:
        """Check for breakout signal at pivot level"""
        try:
            if len(df) < 5:
                return None
            
            # Get recent price action
            recent_closes = df['close'].tail(5)
            
            # Check for resistance breakout
            if level_category == 'resistance':
                # Previous closes should be below level, current close above
                prev_closes_below = all(close <= level_price + self.bounce_threshold 
                                      for close in recent_closes.iloc[:-1])
                current_breakout = current_price > level_price + self.breakout_threshold
                
                if prev_closes_below and current_breakout:
                    return 'breakout_buy'
            
            # Check for support breakdown
            elif level_category in ['support', 'pivot']:
                # Previous closes should be above level, current close below
                prev_closes_above = all(close >= level_price - self.bounce_threshold 
                                      for close in recent_closes.iloc[:-1])
                current_breakdown = current_price < level_price - self.breakout_threshold
                
                if prev_closes_above and current_breakdown:
                    return 'breakdown_sell'
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking breakout signal: {e}")
            return None
    
    def _create_pivot_signal(self, symbol: str, timeframe: str, signal_type: str,
                           level_type: PivotLevel, level_price: float,
                           pivot_data: PivotPointData, df: pd.DataFrame,
                           timestamp: datetime) -> Optional[SignalEvent]:
        """Create enhanced pivot signal"""
        try:
            current_price = df['close'].iloc[-1]
            
            # Determine direction and action
            direction_map = {
                'bounce_buy': ('bullish', PivotAction.BOUNCE_BUY),
                'bounce_sell': ('bearish', PivotAction.BOUNCE_SELL),
                'breakout_buy': ('bullish', PivotAction.BREAKOUT_BUY),
                'breakdown_sell': ('bearish', PivotAction.BREAKDOWN_SELL)
            }
            
            if signal_type not in direction_map:
                return None
            
            direction, pivot_action = direction_map[signal_type]
            
            # Calculate ATR for stop loss and target
            atr = self._calculate_atr(df)
            current_atr = atr.iloc[-1] if atr is not None else current_price * 0.01
            
            # Calculate stop loss and target
            if direction == 'bullish':
                stop_loss = current_price - (current_atr * self.stop_loss_atr_multiple)
                target_price = current_price + (current_atr * self.stop_loss_atr_multiple * self.take_profit_ratio)
            else:
                stop_loss = current_price + (current_atr * self.stop_loss_atr_multiple)
                target_price = current_price - (current_atr * self.stop_loss_atr_multiple * self.take_profit_ratio)
            
            # Calculate signal strength
            strength = self._calculate_signal_strength(
                signal_type, current_price, level_price, df, pivot_data
            )
            
            # Skip if strength too low
            if strength < self.min_signal_strength:
                return None
            
            # Volume confirmation
            volume_confirmed = self._check_volume_confirmation(df) if self.volume_confirmation_required else True
            
            # Risk-reward validation
            risk = abs(current_price - stop_loss)
            reward = abs(target_price - current_price)
            risk_reward_ratio = reward / risk if risk > 0 else 0
            
            if risk_reward_ratio < 1.0:  # Minimum 1:1 risk-reward
                return None
            
            # Calculate additional metrics
            level_strength = self._calculate_level_strength_at_price(level_price, df)
            touches_count = self._count_level_touches_at_price(level_price, df)
            age_hours = self._calculate_level_age_hours(pivot_data.timestamp)
            
            # Multi-timeframe alignment (simplified)
            multi_tf_alignment = True  # Would be calculated from other timeframes
            
            # Create enhanced signal
            signal = SignalEvent(
                event_type='PIVOT_POINT_SIGNAL',
                symbol=symbol,
                timeframe=timeframe,
                timestamp=timestamp,
                direction=direction,
                strength=strength,
                level=current_price,
                metadata={
                    'pivot_action': pivot_action.value,
                    'pivot_level': level_type.value,
                    'pivot_value': level_price,
                    'target_price': target_price,
                    'stop_loss': stop_loss,
                    'risk_reward_ratio': risk_reward_ratio,
                    'volume_confirmed': volume_confirmed,
                    'multi_timeframe_alignment': multi_tf_alignment,
                    'level_strength': level_strength,
                    'touches_count': touches_count,
                    'age_hours': age_hours,
                    'pivot_type': pivot_data.pivot_type.value,
                    'session_type': pivot_data.session_type.value,
                    'atr': current_atr,
                    'confidence': pivot_data.confidence,
                    'expected_move': abs(target_price - current_price),
                    'signal_reason': f"{signal_type} at {level_type.value}",
                    'pivot_data_summary': self._create_pivot_summary(pivot_data)
                }
            )
            
            return signal
            
        except Exception as e:
            logger.error(f"Error creating pivot signal: {e}")
            return None
    
    def _calculate_signal_strength(self, signal_type: str, current_price: float,
                                 level_price: float, df: pd.DataFrame,
                                 pivot_data: PivotPointData) -> float:
        """Calculate signal strength based on multiple factors"""
        try:
            strength_factors = []
            
            # Distance from level factor (closer = stronger)
            distance = abs(current_price - level_price)
            max_distance = self.breakout_threshold * 2
            distance_factor = max(0.3, 1.0 - (distance / max_distance))
            strength_factors.append(distance_factor)
            
            # Pivot strength factor
            strength_factors.append(pivot_data.strength_score)
            
            # Pivot confidence factor
            strength_factors.append(pivot_data.confidence)
            
            # Volume factor
            if self._check_volume_confirmation(df):
                strength_factors.append(0.8)
            else:
                strength_factors.append(0.4)
            
            # Signal type factor
            signal_type_weights = {
                'bounce_buy': 0.8,
                'bounce_sell': 0.8,
                'breakout_buy': 0.7,
                'breakdown_sell': 0.7
            }
            strength_factors.append(signal_type_weights.get(signal_type, 0.6))
            
            # Market condition factor
            market_condition = self._assess_market_condition(df)
            condition_weights = {
                'trending': 0.7,  # Breakouts work better in trending markets
                'ranging': 0.9,   # Bounces work better in ranging markets
                'volatile': 0.6
            }
            strength_factors.append(condition_weights.get(market_condition, 0.6))
            
            # Calculate overall strength
            overall_strength = np.mean(strength_factors) if strength_factors else 0.5
            
            return min(1.0, float(overall_strength))
            
        except Exception as e:
            logger.error(f"Error calculating signal strength: {e}")
            return 0.5
    
    def _check_volume_confirmation(self, df: pd.DataFrame) -> bool:
        """Check for volume confirmation"""
        try:
            if 'volume' not in df.columns or df['volume'].sum() == 0:
                return True  # Skip volume check if not available
            
            current_volume = df['volume'].iloc[-1]
            avg_volume = df['volume'].rolling(self.volume_lookback).mean().iloc[-1]
            
            return current_volume > avg_volume * self.volume_threshold_multiplier
            
        except Exception as e:
            logger.error(f"Error checking volume confirmation: {e}")
            return True
    
    def _calculate_level_strength_at_price(self, price: float, df: pd.DataFrame) -> float:
        """Calculate strength of a specific price level"""
        try:
            # This would analyze historical touches, bounces, and reactions at this level
            # Simplified implementation
            return 0.7  # Placeholder
            
        except Exception as e:
            logger.error(f"Error calculating level strength: {e}")
            return 0.5
    
    def _count_level_touches_at_price(self, price: float, df: pd.DataFrame) -> int:
        """Count how many times price has touched this level"""
        try:
            tolerance = self.level_proximity_threshold
            touches = 0
            
            for _, row in df.iterrows():
                if (abs(row['high'] - price) <= tolerance or 
                    abs(row['low'] - price) <= tolerance):
                    touches += 1
            
            return touches
            
        except Exception as e:
            logger.error(f"Error counting level touches: {e}")
            return 0
    
    def _calculate_level_age_hours(self, pivot_timestamp: datetime) -> float:
        """Calculate age of pivot level in hours"""
        try:
            age_delta = datetime.utcnow() - pivot_timestamp
            return age_delta.total_seconds() / 3600
            
        except Exception as e:
            logger.error(f"Error calculating level age: {e}")
            return 0.0
    
    def _assess_market_condition(self, df: pd.DataFrame) -> str:
        """Assess current market condition"""
        try:
            if len(df) < 20:
                return 'ranging'
            
            # Simple trend assessment
            sma_short = df['close'].rolling(10).mean()
            sma_long = df['close'].rolling(20).mean()
            
            if sma_short.iloc[-1] > sma_long.iloc[-1] * 1.01:
                return 'trending'
            elif sma_short.iloc[-1] < sma_long.iloc[-1] * 0.99:
                return 'trending'
            else:
                return 'ranging'
                
        except Exception as e:
            logger.error(f"Error assessing market condition: {e}")
            return 'ranging'
    
    def _create_pivot_summary(self, pivot_data: PivotPointData) -> Dict[str, Any]:
        """Create summary of pivot data for metadata"""
        try:
            return {
                'pivot_type': pivot_data.pivot_type.value,
                'pivot_point': pivot_data.pivot_point,
                'resistance_levels': [
                    pivot_data.resistance_1,
                    pivot_data.resistance_2,
                    pivot_data.resistance_3
                ],
                'support_levels': [
                    pivot_data.support_1,
                    pivot_data.support_2,
                    pivot_data.support_3
                ],
                'strength_score': pivot_data.strength_score,
                'confidence': pivot_data.confidence,
                'session_type': pivot_data.session_type.value
            }
            
        except Exception as e:
            logger.error(f"Error creating pivot summary: {e}")
            return {}
    
    def _combine_timeframe_pivot_signals(self, symbol: str,
                                       timeframe_signals: Dict[str, List[SignalEvent]],
                                       timeframe_pivots: Dict[str, Dict[PivotType, PivotPointData]]) -> List[SignalEvent]:
        """Combine pivot signals from multiple timeframes"""
        try:
            if not timeframe_signals:
                return []
            
            # If confluence not required, return all signals
            if not self.confluence_required:
                all_signals = []
                for signals in timeframe_signals.values():
                    all_signals.extend(signals)
                return all_signals
            
            # Timeframe weights for confluence analysis
            timeframe_weights = {
                'M15': 0.2,
                'H1': 0.4,
                'H4': 0.7,
                'D1': 1.0
            }
            
            combined_signals = []
            
            # Look for confluence across timeframes
            for primary_tf, primary_signals in timeframe_signals.items():
                for signal in primary_signals:
                    confluence_score = timeframe_weights.get(primary_tf, 0.5)
                    supporting_timeframes = [primary_tf]
                    
                    # Check for supporting signals in other timeframes
                    for other_tf, other_signals in timeframe_signals.items():
                        if other_tf == primary_tf:
                            continue
                        
                        # Look for similar signals in other timeframes
                        for other_signal in other_signals:
                            if (other_signal.direction == signal.direction and
                                abs(other_signal.level - signal.level) / signal.level < 0.01):  # 1% tolerance
                                
                                confluence_score += timeframe_weights.get(other_tf, 0.3)
                                supporting_timeframes.append(other_tf)
                    
                    # Only include signals with sufficient confluence
                    if confluence_score >= 0.8:  # Minimum confluence threshold
                        # Enhance signal with confluence information
                        signal.metadata['confluence_score'] = confluence_score
                        signal.metadata['supporting_timeframes'] = supporting_timeframes
                        signal.metadata['timeframe_count'] = len(supporting_timeframes)
                        
                        # Adjust strength based on confluence
                        signal.strength = min(1.0, signal.strength * (1 + confluence_score * 0.2))
                        
                        combined_signals.append(signal)
            
            return combined_signals
            
        except Exception as e:
            logger.error(f"Error combining timeframe pivot signals: {e}")
            return []
    
    def _filter_and_validate_pivot_signals(self, signals: List[SignalEvent]) -> List[SignalEvent]:
        """Apply advanced filtering to pivot signals"""
        try:
            if not signals:
                return signals
            
            filtered_signals = []
            current_time = datetime.utcnow()
            
            for signal in signals:
                # Strength filter
                if signal.strength < self.min_signal_strength:
                    continue
                
                # Confidence filter
                confidence = signal.metadata.get('confidence', 0.5)
                if confidence < 0.6:
                    continue
                
                # Risk-reward filter
                risk_reward = signal.metadata.get('risk_reward_ratio', 0)
                if risk_reward < 1.0:
                    continue
                
                # Volume confirmation filter
                if self.volume_confirmation_required:
                    volume_confirmed = signal.metadata.get('volume_confirmed', False)
                    if not volume_confirmed:
                        continue
                
                # Level age filter
                age_hours = signal.metadata.get('age_hours', 0)
                if age_hours > self.level_age_limit_hours:
                    continue
                
                # Rate limiting
                if self._is_signal_too_frequent(signal, current_time):
                    continue
                
                filtered_signals.append(signal)
            
            # Limit daily signals
            return filtered_signals[:self.max_signals_per_day]
            
        except Exception as e:
            logger.error(f"Error filtering pivot signals: {e}")
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
                    'pivot_action': signal.metadata.get('pivot_action'),
                    'pivot_level': signal.metadata.get('pivot_level'),
                    'confluence_score': signal.metadata.get('confluence_score', 0),
                    'confidence': signal.metadata.get('confidence', 0.5)
                })
                
                self.performance_monitor['signals_generated'] += 1
            
        except Exception as e:
            logger.error(f"Error updating signal history: {e}")
    
    # Helper methods for technical indicators
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> Optional[pd.Series]:
        """Calculate Average True Range"""
        try:
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift(1))
            low_close = np.abs(df['low'] - df['close'].shift(1))
            
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(period).mean()
            
            return atr
            
        except Exception as e:
            logger.error(f"Error calculating ATR: {e}")
            return None
    
    def _calculate_level_strength(self, level_price: float, df: pd.DataFrame) -> float:
        """Calculate strength of a price level"""
        try:
            # Placeholder implementation
            return 0.7
            
        except Exception as e:
            logger.error(f"Error calculating level strength: {e}")
            return 0.5
    
    def _calculate_level_age(self, level_timestamp: datetime) -> float:
        """Calculate age of level in hours"""
        try:
            age_delta = datetime.utcnow() - level_timestamp
            return age_delta.total_seconds() / 3600
            
        except Exception as e:
            logger.error(f"Error calculating level age: {e}")
            return 0.0
    
    def _count_level_touches(self, level_price: float, df: pd.DataFrame) -> int:
        """Count touches at price level"""
        try:
            return self._count_level_touches_at_price(level_price, df)
            
        except Exception as e:
            logger.error(f"Error counting level touches: {e}")
            return 0
    
    def _validate_volume_at_level(self, level_price: float, df: pd.DataFrame) -> bool:
        """Validate volume at price level"""
        try:
            return self._check_volume_confirmation(df)
            
        except Exception as e:
            logger.error(f"Error validating volume at level: {e}")
            return True
    
    def get_required_data(self) -> Dict[str, List[str]]:
        """Return required data specification"""
        return {
            '*': self.timeframes  # All symbols need specified timeframes
        }
    
    def validate_signal(self, signal: SignalEvent) -> bool:
        """Validate individual pivot signal"""
        try:
            # Basic validation
            if not signal or signal.strength < self.min_signal_strength:
                return False
            
            # Direction validation
            if signal.direction not in ['bullish', 'bearish']:
                return False
            
            # Pivot-specific validation
            pivot_action = signal.metadata.get('pivot_action')
            if not pivot_action:
                return False
            
            pivot_level = signal.metadata.get('pivot_level')
            if not pivot_level:
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
        """Get comprehensive performance summary"""
        try:
            return {
                'signals_generated': self.performance_monitor['signals_generated'],
                'successful_bounces': self.performance_monitor['successful_bounces'],
                'successful_breakouts': self.performance_monitor['successful_breakouts'],
                'failed_signals': self.performance_monitor['failed_signals'],
                'pivot_success_rate': (
                    (self.performance_monitor['successful_bounces'] + 
                     self.performance_monitor['successful_breakouts']) /
                    max(1, self.performance_monitor['signals_generated'])
                ),
                'avg_signal_accuracy': self.performance_monitor['avg_signal_accuracy'],
                'best_pivot_profit': self.performance_monitor['best_pivot_profit'],
                'worst_pivot_loss': self.performance_monitor['worst_pivot_loss'],
                'pivot_history_length': len(self.pivot_history),
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
            logger.info(f"Cleaning up Enhanced Pivot Point Strategy: {self.name}")
            
            # Clear history and caches
            self.pivot_history.clear()
            self.signal_history.clear()
            self.performance_metrics.clear()
            self.level_touch_history.clear()
            
            # Reset performance monitor
            self.performance_monitor = {
                'signals_generated': 0,
                'successful_bounces': 0,
                'successful_breakouts': 0,
                'failed_signals': 0,
                'avg_signal_accuracy': 0.0,
                'best_pivot_profit': 0.0,
                'worst_pivot_loss': 0.0,
                'level_effectiveness': defaultdict(list)
            }
            
            logger.info("Enhanced Pivot Point Strategy cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Export the enhanced strategy
__all__ = ['EnhancedPivotPointStrategy', 'PivotType', 'PivotLevel', 'PivotAction', 'PivotPointData', 'PivotSignal']

# Compatibility alias
PivotPointStrategy = EnhancedPivotPointStrategy
