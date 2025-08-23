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

# Import unified signals with fallback
try:
    from unified_signals import *
except ImportError:
    # Fallback functions if import fails
    def generate_basic_signal(data, symbol="EURUSD"):
        if data is None or data.empty:
            return {'signal': 'HOLD', 'confidence': 0.5, 'price': 1.0}
        return {'signal': 'HOLD', 'confidence': 0.5, 'price': data['close'].iloc[-1]}
    
    def calculate_sma(data, period):
        return data.rolling(window=period).mean()
    
    def calculate_ema(data, period):
        return data.ewm(span=period).mean()

# Numpy compatibility
try:
    from numpy_compatibility import NaN
except ImportError:
    NaN = np.nan

# PrimaryStrategy import with fallback
try:
    from strategies import PrimaryStrategy
except ImportError:
    class PrimaryStrategy:
        def analyze(self, data, symbol): 
            return {"signal": "HOLD", "confidence": 0.5, "price": 1.0}


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
Enhanced Breakout Strategy Implementation
========================================
Professional-grade breakout trading strategy with advanced analytics,
multi-timeframe analysis, and comprehensive risk management.

Features:
- Multiple breakout detection methodologies
- Volume profile analysis and confirmation
- False breakout filtering and validation
- Multi-timeframe breakout confluence
- Market structure analysis (support/resistance)
- Volatility-based breakout thresholds
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

class BreakoutType(Enum):
    
    def analyze(self, data, symbol="EURUSD"):
        """Kelly-compatible analyze method for Breakout Strategy"""
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
                        'reason': f'Breakout Strategy bullish trend'
                    }
                elif current_price < ma_20 < ma_50:
                    return {
                        'signal': 'SELL', 
                        'confidence': 0.65,
                        'price': current_price,
                        'reason': f'Breakout Strategy bearish trend'
                    }
            
            return {
                'signal': 'HOLD',
                'confidence': 0.4,
                'price': current_price,
                'reason': f'Breakout Strategy neutral'
            }
            
        except Exception as e:
            return {
                'signal': 'HOLD',
                'confidence': 0.0,
                'price': 1.0,
                'reason': f'Breakout Strategy error: {str(e)}'
            }

    """Types of breakout strategies"""
    RESISTANCE_BREAKOUT = "resistance_breakout"
    SUPPORT_BREAKDOWN = "support_breakdown"
    RANGE_BREAKOUT = "range_breakout"
    CHANNEL_BREAKOUT = "channel_breakout"
    VOLATILITY_BREAKOUT = "volatility_breakout"
    VOLUME_BREAKOUT = "volume_breakout"
    MOMENTUM_BREAKOUT = "momentum_breakout"

class BreakoutStrength(Enum):
    """Breakout signal strength levels"""
    WEAK = 0.3
    MODERATE = 0.5
    STRONG = 0.7
    VERY_STRONG = 0.9

class MarketStructure(Enum):
    """Market structure states for breakout analysis"""
    ACCUMULATION = "accumulation"
    DISTRIBUTION = "distribution"
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    RANGING = "ranging"
    CONSOLIDATION = "consolidation"
    BREAKOUT_PENDING = "breakout_pending"

@dataclass
class BreakoutSignal:
    """Enhanced breakout signal with comprehensive metadata"""
    timestamp: datetime
    symbol: str
    timeframe: str
    direction: str  # 'bullish', 'bearish'
    strength: float  # 0.0 to 1.0
    breakout_type: BreakoutType
    breakout_level: float
    entry_price: float
    target_price: float
    stop_loss: float
    confidence: float
    market_structure: MarketStructure
    volume_confirmation: bool
    volatility_expansion: bool
    false_breakout_probability: float
    breakout_distance: float
    time_at_level: int  # How long price was at the breakout level
    previous_tests: int  # Number of previous tests of this level
    level_strength: float  # Strength of the breakout level
    metadata: Dict[str, Any] = field(default_factory=dict)

@register_strategy
class EnhancedBreakoutStrategy(BaseStrategy):
    """
    Enhanced Breakout Strategy - Professional Implementation
    
    Advanced breakout strategy incorporating multiple detection methods,
    volume analysis, and sophisticated market structure understanding
    for institutional-grade trading applications.
    
    Key Features:
    - Multi-timeframe breakout analysis
    - Volume profile confirmation
    - False breakout filtering
    - Market structure analysis
    - Volatility-based thresholds
    - Advanced risk management
    - Comprehensive performance tracking
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize enhanced breakout strategy
        
        Args:
            name: Strategy name
            config: Configuration dictionary with strategy parameters
        """
        super().__init__(name, config)
        
        # Core breakout parameters
        self.lookback_period = config.get('breakout_lookback', 20)
        self.min_breakout_distance = config.get('min_breakout_distance', 0.001)  # 10 pips
        self.breakout_threshold = config.get('breakout_threshold', 0.5)  # Minimum strength
        
        # Volume analysis parameters
        self.volume_threshold = config.get('volume_threshold', 1.5)  # 1.5x average volume
        self.volume_confirmation_required = config.get('volume_confirmation_required', True)
        self.volume_lookback = config.get('volume_lookback', 20)
        
        # Support/Resistance detection
        self.sr_sensitivity = config.get('sr_sensitivity', 0.02)  # 2% price level tolerance
        self.min_touches = config.get('min_touches', 2)  # Minimum touches to confirm level
        self.level_age_limit = config.get('level_age_limit', 50)  # Maximum bars for level validity
        
        # Multi-timeframe analysis
        self.timeframes = config.get('timeframes', ['M15', 'H1', 'H4'])
        self.primary_timeframe = config.get('primary_timeframe', 'H1')
        
        # Volatility and momentum parameters
        self.atr_period = config.get('atr_period', 14)
        self.volatility_expansion_threshold = config.get('volatility_expansion_threshold', 1.3)
        self.momentum_period = config.get('momentum_period', 10)
        
        # False breakout filtering
        self.false_breakout_filter = config.get('false_breakout_filter', True)
        self.min_breakout_hold_bars = config.get('min_breakout_hold_bars', 3)
        self.retest_tolerance = config.get('retest_tolerance', 0.0005)  # 5 pips
        
        # Risk management parameters
        self.max_position_size = config.get('max_position_size', 0.02)
        self.stop_loss_atr_multiple = config.get('stop_loss_atr_multiple', 2.0)
        self.take_profit_ratio = config.get('take_profit_ratio', 2.0)
        
        # Signal filtering parameters
        self.min_confluence_factors = config.get('min_confluence_factors', 2)
        self.max_signals_per_session = config.get('max_signals_per_session', 3)
        
        # Performance tracking
        self.signal_history = deque(maxlen=1000)
        self.performance_metrics = defaultdict(list)
        self.breakout_success_rates = defaultdict(float)
        self.level_history = deque(maxlen=500)  # Track support/resistance levels
        
        # Technical parameters
        self.rsi_period = config.get('rsi_period', 14)
        self.macd_fast = config.get('macd_fast', 12)
        self.macd_slow = config.get('macd_slow', 26)
        self.bb_period = config.get('bb_period', 20)
        self.bb_std = config.get('bb_std', 2.0)
        
        # Advanced features
        self.enable_volume_profile = config.get('enable_volume_profile', True)
        self.enable_market_structure = config.get('enable_market_structure', True)
        self.enable_volatility_filter = config.get('enable_volatility_filter', True)
        
        logger.info(f"Enhanced Breakout Strategy '{name}' initialized successfully")
        logger.info(f"Configuration: {self._log_safe_config()}")
    
    def _log_safe_config(self) -> Dict[str, Any]:
        """Create logging-safe configuration summary"""
        return {
            'lookback_period': self.lookback_period,
            'volume_threshold': self.volume_threshold,
            'sr_sensitivity': self.sr_sensitivity,
            'timeframes': len(self.timeframes),
            'false_breakout_filter': self.false_breakout_filter,
            'volume_confirmation_required': self.volume_confirmation_required
        }
    
    async def initialize(self) -> bool:
        """Initialize strategy with enhanced setup"""
        try:
            logger.info(f"Initializing Enhanced Breakout Strategy: {self.name}")
            
            # Validate configuration
            if not self._validate_configuration():
                logger.error("Configuration validation failed")
                return False
            
            # Initialize technical indicators
            self._initialize_indicators()
            
            # Setup performance monitoring
            self._setup_performance_monitoring()
            
            # Initialize market structure analysis
            self._initialize_market_structure_analysis()
            
            logger.info("Enhanced Breakout Strategy initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing Enhanced Breakout Strategy: {e}")
            return False
    
    def _validate_configuration(self) -> bool:
        """Validate strategy configuration parameters"""
        try:
            # Validate lookback periods
            if self.lookback_period < 5 or self.lookback_period > 100:
                logger.error(f"Invalid lookback_period: {self.lookback_period}")
                return False
            
            # Validate volume parameters
            if self.volume_threshold < 1.0 or self.volume_threshold > 5.0:
                logger.error(f"Invalid volume_threshold: {self.volume_threshold}")
                return False
            
            # Validate support/resistance parameters
            if not (0.001 <= self.sr_sensitivity <= 0.1):
                logger.error(f"Invalid sr_sensitivity: {self.sr_sensitivity}")
                return False
            
            if self.min_touches < 1 or self.min_touches > 10:
                logger.error(f"Invalid min_touches: {self.min_touches}")
                return False
            
            # Validate breakout parameters
            if not (0.0001 <= self.min_breakout_distance <= 0.01):
                logger.error(f"Invalid min_breakout_distance: {self.min_breakout_distance}")
                return False
            
            # Validate timeframes
            if not self.timeframes:
                logger.error("No timeframes specified")
                return False
            
            if self.primary_timeframe not in self.timeframes:
                logger.error(f"Primary timeframe {self.primary_timeframe} not in timeframes list")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating configuration: {e}")
            return False
    
    def _initialize_indicators(self):
        """Initialize technical indicators for breakout analysis"""
        self.indicators = {
            'support_resistance': {},
            'volume_profile': {},
            'volatility': {},
            'momentum': {},
            'trend': {}
        }
        logger.info("Breakout indicators initialized")
    
    def _setup_performance_monitoring(self):
        """Setup performance monitoring and analytics"""
        self.performance_monitor = {
            'signals_generated': 0,
            'successful_breakouts': 0,
            'false_breakouts': 0,
            'avg_breakout_distance': 0.0,
            'best_breakout_profit': 0.0,
            'worst_breakout_loss': 0.0,
            'breakout_accuracy_by_type': defaultdict(list)
        }
        logger.info("Performance monitoring setup complete")
    
    def _initialize_market_structure_analysis(self):
        """Initialize market structure analysis components"""
        self.market_structure = {
            'current_structure': MarketStructure.RANGING,
            'support_levels': [],
            'resistance_levels': [],
            'trend_lines': [],
            'consolidation_zones': []
        }
        logger.info("Market structure analysis initialized")
    
    def generate_signals(self, data: Dict[str, pd.DataFrame]) -> List[SignalEvent]:
        """
        Generate enhanced breakout signals
        
        Args:
            data: Dictionary of market data by symbol and timeframe
            
        Returns:
            List of enhanced breakout signals
        """
        try:
            signals = []
            
            for symbol, timeframe_data in data.items():
                if isinstance(timeframe_data, dict):
                    # Multi-timeframe breakout analysis
                    symbol_signals = self._analyze_multi_timeframe_breakouts(
                        symbol, timeframe_data
                    )
                    signals.extend(symbol_signals)
                else:
                    # Single timeframe analysis
                    symbol_signals = self._analyze_single_timeframe_breakouts(
                        symbol, self.primary_timeframe, timeframe_data
                    )
                    signals.extend(symbol_signals)
            
            # Apply advanced filtering and validation
            filtered_signals = self._filter_and_validate_breakout_signals(signals)
            
            # Update performance tracking
            self._update_signal_history(filtered_signals)
            
            logger.info(f"Generated {len(filtered_signals)} breakout signals from {len(signals)} candidates")
            return filtered_signals
            
        except Exception as e:
            logger.error(f"Error generating breakout signals: {e}")
            return []
    
    def _analyze_multi_timeframe_breakouts(self, symbol: str, 
                                         timeframe_data: Dict[str, pd.DataFrame]) -> List[SignalEvent]:
        """Analyze breakouts across multiple timeframes"""
        try:
            timeframe_signals = {}
            timeframe_analysis = {}
            
            # Analyze each timeframe
            for timeframe, df in timeframe_data.items():
                if timeframe in self.timeframes and len(df) >= self.lookback_period:
                    breakout_analysis = self._calculate_comprehensive_breakout_analysis(df)
                    market_structure = self._analyze_market_structure(df)
                    
                    timeframe_analysis[timeframe] = breakout_analysis
                    timeframe_signals[timeframe] = self._generate_timeframe_breakout_signals(
                        symbol, timeframe, df, breakout_analysis, market_structure
                    )
            
            # Combine multi-timeframe analysis
            combined_signals = self._combine_timeframe_breakout_signals(
                symbol, timeframe_signals, timeframe_analysis
            )
            
            return combined_signals
            
        except Exception as e:
            logger.error(f"Error in multi-timeframe breakout analysis for {symbol}: {e}")
            return []
    
    def _analyze_single_timeframe_breakouts(self, symbol: str, timeframe: str, 
                                          df: pd.DataFrame) -> List[SignalEvent]:
        """Analyze breakouts for single timeframe"""
        try:
            if len(df) < self.lookback_period:
                return []
            
            # Calculate comprehensive breakout analysis
            breakout_analysis = self._calculate_comprehensive_breakout_analysis(df)
            
            # Analyze market structure
            market_structure = self._analyze_market_structure(df)
            
            # Generate signals
            signals = self._generate_timeframe_breakout_signals(
                symbol, timeframe, df, breakout_analysis, market_structure
            )
            
            return signals
            
        except Exception as e:
            logger.error(f"Error in single timeframe breakout analysis: {e}")
            return []
    
    def _calculate_comprehensive_breakout_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate comprehensive breakout analysis"""
        try:
            analysis = {}
            
            # Support and resistance levels
            analysis['support_resistance'] = self._identify_support_resistance_levels(df)
            
            # Volume analysis
            analysis['volume_analysis'] = self._analyze_volume_patterns(df)
            
            # Volatility analysis
            analysis['volatility_analysis'] = self._analyze_volatility_patterns(df)
            
            # Momentum analysis
            analysis['momentum_analysis'] = self._analyze_momentum_patterns(df)
            
            # Market structure analysis
            analysis['market_structure'] = self._analyze_detailed_market_structure(df)
            
            # Breakout probability calculation
            analysis['breakout_probability'] = self._calculate_breakout_probability(df, analysis)
            
            # False breakout risk assessment
            analysis['false_breakout_risk'] = self._assess_false_breakout_risk(df, analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error calculating comprehensive breakout analysis: {e}")
            return {}
    
    def _identify_support_resistance_levels(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify key support and resistance levels"""
        try:
            sr_analysis = {}
            
            # Calculate pivot points
            pivot_highs = self._find_pivot_highs(df)
            pivot_lows = self._find_pivot_lows(df)
            
            # Cluster similar price levels
            resistance_levels = self._cluster_price_levels(pivot_highs)
            support_levels = self._cluster_price_levels(pivot_lows)
            
            # Calculate level strength based on touches and volume
            sr_analysis['resistance_levels'] = self._calculate_level_strength(
                resistance_levels, df, 'resistance'
            )
            sr_analysis['support_levels'] = self._calculate_level_strength(
                support_levels, df, 'support'
            )
            
            # Current price position relative to levels
            current_price = df['close'].iloc[-1]
            sr_analysis['nearest_resistance'] = self._find_nearest_level(
                current_price, sr_analysis['resistance_levels'], 'above'
            )
            sr_analysis['nearest_support'] = self._find_nearest_level(
                current_price, sr_analysis['support_levels'], 'below'
            )
            
            # Level age and validity
            sr_analysis['level_ages'] = self._calculate_level_ages(df)
            
            return sr_analysis
            
        except Exception as e:
            logger.error(f"Error identifying support/resistance levels: {e}")
            return {}
    
    def _find_pivot_highs(self, df: pd.DataFrame, window: int = 5) -> List[Tuple[int, float]]:
        """Find pivot high points in price data"""
        try:
            pivot_highs = []
            highs = df['high'].values
            
            for i in range(window, len(highs) - window):
                is_pivot = True
                current_high = highs[i]
                
                # Check if current point is higher than surrounding points
                for j in range(i - window, i + window + 1):
                    if j != i and highs[j] >= current_high:
                        is_pivot = False
                        break
                
                if is_pivot:
                    pivot_highs.append((i, current_high))
            
            return pivot_highs
            
        except Exception as e:
            logger.error(f"Error finding pivot highs: {e}")
            return []
    
    def _find_pivot_lows(self, df: pd.DataFrame, window: int = 5) -> List[Tuple[int, float]]:
        """Find pivot low points in price data"""
        try:
            pivot_lows = []
            lows = df['low'].values
            
            for i in range(window, len(lows) - window):
                is_pivot = True
                current_low = lows[i]
                
                # Check if current point is lower than surrounding points
                for j in range(i - window, i + window + 1):
                    if j != i and lows[j] <= current_low:
                        is_pivot = False
                        break
                
                if is_pivot:
                    pivot_lows.append((i, current_low))
            
            return pivot_lows
            
        except Exception as e:
            logger.error(f"Error finding pivot lows: {e}")
            return []
    
    def _cluster_price_levels(self, pivots: List[Tuple[int, float]]) -> List[Dict[str, Any]]:
        """Cluster similar price levels together"""
        try:
            if not pivots:
                return []
            
            # Sort pivots by price
            sorted_pivots = sorted(pivots, key=lambda x: x[1])
            clusters = []
            current_cluster = [sorted_pivots[0]]
            
            for i in range(1, len(sorted_pivots)):
                current_price = sorted_pivots[i][1]
                cluster_avg = np.mean([p[1] for p in current_cluster])
                
                # If price is within sensitivity range, add to current cluster
                if abs(current_price - cluster_avg) / cluster_avg <= self.sr_sensitivity:
                    current_cluster.append(sorted_pivots[i])
                else:
                    # Start new cluster
                    if len(current_cluster) >= self.min_touches:
                        clusters.append({
                            'level': np.mean([p[1] for p in current_cluster]),
                            'touches': len(current_cluster),
                            'indices': [p[0] for p in current_cluster],
                            'prices': [p[1] for p in current_cluster]
                        })
                    current_cluster = [sorted_pivots[i]]
            
            # Add last cluster
            if len(current_cluster) >= self.min_touches:
                clusters.append({
                    'level': np.mean([p[1] for p in current_cluster]),
                    'touches': len(current_cluster),
                    'indices': [p[0] for p in current_cluster],
                    'prices': [p[1] for p in current_cluster]
                })
            
            return clusters
            
        except Exception as e:
            logger.error(f"Error clustering price levels: {e}")
            return []
    
    def _calculate_level_strength(self, levels: List[Dict[str, Any]], 
                                df: pd.DataFrame, level_type: str) -> List[Dict[str, Any]]:
        """Calculate strength of support/resistance levels"""
        try:
            for level in levels:
                # Base strength from number of touches
                touch_strength = min(1.0, level['touches'] / 5.0)
                
                # Volume strength at level
                volume_strength = 0.0
                if 'volume' in df.columns:
                    level_volumes = []
                    for idx in level['indices']:
                        if idx < len(df):
                            level_volumes.append(df['volume'].iloc[idx])
                    
                    if level_volumes:
                        avg_level_volume = np.mean(level_volumes)
                        avg_total_volume = df['volume'].mean()
                        volume_strength = min(1.0, avg_level_volume / avg_total_volume)
                
                # Age factor (newer levels are stronger)
                if level['indices']:
                    latest_touch = max(level['indices'])
                    age = len(df) - latest_touch
                    age_factor = max(0.3, 1.0 - (age / self.level_age_limit))
                else:
                    age_factor = 0.5
                
                # Combined strength
                level['strength'] = (touch_strength * 0.5 + volume_strength * 0.3 + age_factor * 0.2)
                level['age'] = age if 'age' in locals() else 0
                level['type'] = level_type
            
            # Sort by strength
            levels.sort(key=lambda x: x['strength'], reverse=True)
            
            return levels
            
        except Exception as e:
            logger.error(f"Error calculating level strength: {e}")
            return levels
    
    def _find_nearest_level(self, price: float, levels: List[Dict[str, Any]], 
                          direction: str) -> Optional[Dict[str, Any]]:
        """Find nearest support or resistance level"""
        try:
            if not levels:
                return None
            
            if direction == 'above':
                # Find nearest resistance above current price
                above_levels = [l for l in levels if l['level'] > price]
                return min(above_levels, key=lambda x: x['level'] - price) if above_levels else None
            else:
                # Find nearest support below current price
                below_levels = [l for l in levels if l['level'] < price]
                return max(below_levels, key=lambda x: price - x['level']) if below_levels else None
                
        except Exception as e:
            logger.error(f"Error finding nearest level: {e}")
            return None
    
    def _calculate_level_ages(self, df: pd.DataFrame) -> Dict[str, int]:
        """Calculate age of support/resistance levels"""
        try:
            # Simplified age calculation
            return {
                'avg_resistance_age': 10,  # Placeholder
                'avg_support_age': 10,     # Placeholder
                'oldest_level_age': 20     # Placeholder
            }
            
        except Exception as e:
            logger.error(f"Error calculating level ages: {e}")
            return {}
    
    def _analyze_volume_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze volume patterns for breakout confirmation"""
        try:
            volume_analysis = {}
            
            if 'volume' not in df.columns or df['volume'].sum() == 0:
                volume_analysis['volume_available'] = False
                return volume_analysis
            
            volume_analysis['volume_available'] = True
            
            # Current vs average volume
            current_volume = df['volume'].iloc[-1]
            avg_volume = df['volume'].rolling(self.volume_lookback).mean().iloc[-1]
            
            volume_analysis['current_volume'] = current_volume
            volume_analysis['average_volume'] = avg_volume
            volume_analysis['volume_ratio'] = current_volume / avg_volume if avg_volume > 0 else 1.0
            volume_analysis['volume_surge'] = volume_analysis['volume_ratio'] > self.volume_threshold
            
            # Volume trend
            recent_volume = df['volume'].tail(5).mean()
            older_volume = df['volume'].tail(20).head(15).mean()
            volume_analysis['volume_trend'] = 'increasing' if recent_volume > older_volume else 'decreasing'
            
            # Volume at key levels (simplified)
            volume_analysis['breakout_volume_confirmation'] = current_volume > avg_volume * 1.2
            
            # On-Balance Volume (OBV) for institutional flow
            if self.enable_volume_profile:
                volume_analysis['obv_analysis'] = self._calculate_obv_analysis(df)
            
            return volume_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing volume patterns: {e}")
            return {'volume_available': False}
    
    def _calculate_obv_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate On-Balance Volume analysis"""
        try:
            obv_values = []
            obv = 0
            
            for i in range(len(df)):
                if i == 0:
                    obv_values.append(df['volume'].iloc[i])
                else:
                    if df['close'].iloc[i] > df['close'].iloc[i-1]:
                        obv += df['volume'].iloc[i]
                    elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                        obv -= df['volume'].iloc[i]
                    obv_values.append(obv)
            
            obv_series = pd.Series(obv_values, index=df.index)
            
            # OBV trend
            obv_sma = obv_series.rolling(10).mean()
            obv_trend = 'bullish' if obv_sma.iloc[-1] > obv_sma.iloc[-5] else 'bearish'
            
            return {
                'obv_trend': obv_trend,
                'obv_divergence': False,  # Simplified
                'obv_strength': 0.7 if obv_trend == 'bullish' else 0.3
            }
            
        except Exception as e:
            logger.error(f"Error calculating OBV analysis: {e}")
            return {'obv_trend': 'neutral', 'obv_strength': 0.5}
    
    def _analyze_volatility_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze volatility patterns for breakout prediction"""
        try:
            volatility_analysis = {}
            
            # Calculate ATR
            atr = self._calculate_atr(df)
            current_atr = atr.iloc[-1]
            avg_atr = atr.rolling(20).mean().iloc[-1]
            
            volatility_analysis['current_atr'] = current_atr
            volatility_analysis['average_atr'] = avg_atr
            volatility_analysis['atr_ratio'] = current_atr / avg_atr if avg_atr > 0 else 1.0
            volatility_analysis['volatility_expansion'] = volatility_analysis['atr_ratio'] > self.volatility_expansion_threshold
            
            # Bollinger Bands squeeze
            if self.enable_volatility_filter:
                bb_analysis = self._calculate_bollinger_bands_squeeze(df)
                volatility_analysis.update(bb_analysis)
            
            # Volatility regime
            if volatility_analysis['atr_ratio'] > 1.5:
                volatility_analysis['regime'] = 'high_volatility'
            elif volatility_analysis['atr_ratio'] < 0.7:
                volatility_analysis['regime'] = 'low_volatility'
            else:
                volatility_analysis['regime'] = 'normal_volatility'
            
            return volatility_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing volatility patterns: {e}")
            return {}
    
    def _calculate_bollinger_bands_squeeze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate Bollinger Bands squeeze indicator"""
        try:
            # Calculate Bollinger Bands
            sma = df['close'].rolling(self.bb_period).mean()
            std = df['close'].rolling(self.bb_period).std()
            upper_band = sma + (std * self.bb_std)
            lower_band = sma - (std * self.bb_std)
            
            # Band width
            band_width = (upper_band - lower_band) / sma
            avg_band_width = band_width.rolling(20).mean()
            
            # Squeeze detection
            current_width = band_width.iloc[-1]
            avg_width = avg_band_width.iloc[-1]
            
            squeeze = current_width < avg_width * 0.8  # 20% below average
            
            return {
                'bb_squeeze': squeeze,
                'band_width': current_width,
                'avg_band_width': avg_width,
                'squeeze_intensity': (avg_width - current_width) / avg_width if avg_width > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating BB squeeze: {e}")
            return {}
    
    def _analyze_momentum_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze momentum patterns for breakout confirmation"""
        try:
            momentum_analysis = {}
            
            # Price momentum
            current_price = df['close'].iloc[-1]
            past_price = df['close'].iloc[-self.momentum_period]
            price_momentum = (current_price - past_price) / past_price
            
            momentum_analysis['price_momentum'] = price_momentum
            momentum_analysis['momentum_strength'] = abs(price_momentum)
            momentum_analysis['momentum_direction'] = 'bullish' if price_momentum > 0 else 'bearish'
            
            # RSI momentum
            rsi = self._calculate_rsi(df)
            momentum_analysis['rsi'] = rsi.iloc[-1]
            momentum_analysis['rsi_momentum'] = 'bullish' if rsi.iloc[-1] > 50 else 'bearish'
            
            # MACD momentum
            macd_data = self._calculate_macd(df)
            momentum_analysis.update(macd_data)
            
            # Rate of Change (ROC)
            roc = df['close'].pct_change(10).iloc[-1]
            momentum_analysis['rate_of_change'] = roc
            
            return momentum_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing momentum patterns: {e}")
            return {}
    
    def _analyze_market_structure(self, df: pd.DataFrame) -> MarketStructure:
        """Analyze current market structure"""
        try:
            if not self.enable_market_structure:
                return MarketStructure.RANGING
            
            # Simple market structure analysis
            sma_20 = df['close'].rolling(20).mean()
            sma_50 = df['close'].rolling(50).mean()
            
            current_price = df['close'].iloc[-1]
            current_sma_20 = sma_20.iloc[-1]
            current_sma_50 = sma_50.iloc[-1]
            
            # Trend determination
            if current_sma_20 > current_sma_50 and current_price > current_sma_20:
                if df['close'].rolling(10).std().iloc[-1] < df['close'].rolling(20).std().mean():
                    return MarketStructure.CONSOLIDATION
                else:
                    return MarketStructure.TRENDING_UP
            elif current_sma_20 < current_sma_50 and current_price < current_sma_20:
                if df['close'].rolling(10).std().iloc[-1] < df['close'].rolling(20).std().mean():
                    return MarketStructure.CONSOLIDATION
                else:
                    return MarketStructure.TRENDING_DOWN
            else:
                return MarketStructure.RANGING
                
        except Exception as e:
            logger.error(f"Error analyzing market structure: {e}")
            return MarketStructure.RANGING
    
    def _analyze_detailed_market_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detailed market structure analysis"""
        try:
            structure_analysis = {}
            
            # Higher highs and higher lows (uptrend)
            highs = df['high'].rolling(5).max()
            lows = df['low'].rolling(5).min()
            
            recent_highs = highs.tail(3)
            recent_lows = lows.tail(3)
            
            higher_highs = all(recent_highs.iloc[i] >= recent_highs.iloc[i-1] for i in range(1, len(recent_highs)))
            higher_lows = all(recent_lows.iloc[i] >= recent_lows.iloc[i-1] for i in range(1, len(recent_lows)))
            lower_highs = all(recent_highs.iloc[i] <= recent_highs.iloc[i-1] for i in range(1, len(recent_highs)))
            lower_lows = all(recent_lows.iloc[i] <= recent_lows.iloc[i-1] for i in range(1, len(recent_lows)))
            
            if higher_highs and higher_lows:
                structure_analysis['trend_structure'] = 'uptrend'
            elif lower_highs and lower_lows:
                structure_analysis['trend_structure'] = 'downtrend'
            else:
                structure_analysis['trend_structure'] = 'sideways'
            
            # Consolidation detection
            price_range = df['high'].rolling(20).max() - df['low'].rolling(20).min()
            avg_range = price_range.rolling(10).mean()
            structure_analysis['consolidation'] = price_range.iloc[-1] < avg_range.iloc[-1] * 0.7
            
            return structure_analysis
            
        except Exception as e:
            logger.error(f"Error in detailed market structure analysis: {e}")
            return {}
    
    def _calculate_breakout_probability(self, df: pd.DataFrame, 
                                      analysis: Dict[str, Any]) -> float:
        """Calculate probability of successful breakout"""
        try:
            probability_factors = []
            
            # Volume factor
            volume_analysis = analysis.get('volume_analysis', {})
            if volume_analysis.get('volume_surge', False):
                probability_factors.append(0.8)
            elif volume_analysis.get('volume_ratio', 1.0) > 1.1:
                probability_factors.append(0.6)
            else:
                probability_factors.append(0.4)
            
            # Volatility factor
            volatility_analysis = analysis.get('volatility_analysis', {})
            if volatility_analysis.get('volatility_expansion', False):
                probability_factors.append(0.7)
            elif volatility_analysis.get('bb_squeeze', False):
                probability_factors.append(0.8)  # Squeeze often precedes breakout
            else:
                probability_factors.append(0.5)
            
            # Momentum factor
            momentum_analysis = analysis.get('momentum_analysis', {})
            momentum_strength = momentum_analysis.get('momentum_strength', 0)
            if momentum_strength > 0.02:  # 2% momentum
                probability_factors.append(0.7)
            elif momentum_strength > 0.01:
                probability_factors.append(0.6)
            else:
                probability_factors.append(0.4)
            
            # Support/resistance strength factor
            sr_analysis = analysis.get('support_resistance', {})
            nearest_resistance = sr_analysis.get('nearest_resistance')
            nearest_support = sr_analysis.get('nearest_support')
            
            # Stronger levels are harder to break but more significant when broken
            if nearest_resistance and nearest_resistance.get('strength', 0) > 0.7:
                probability_factors.append(0.4)  # Hard to break
            elif nearest_support and nearest_support.get('strength', 0) > 0.7:
                probability_factors.append(0.4)  # Hard to break
            else:
                probability_factors.append(0.6)  # Easier to break
            
            # Calculate overall probability
            overall_probability = np.mean(probability_factors) if probability_factors else 0.5
            
            return float(overall_probability)
            
        except Exception as e:
            logger.error(f"Error calculating breakout probability: {e}")
            return 0.5
    
    def _assess_false_breakout_risk(self, df: pd.DataFrame, 
                                  analysis: Dict[str, Any]) -> float:
        """Assess risk of false breakout"""
        try:
            risk_factors = []
            
            # Low volume increases false breakout risk
            volume_analysis = analysis.get('volume_analysis', {})
            volume_ratio = volume_analysis.get('volume_ratio', 1.0)
            if volume_ratio < 0.8:
                risk_factors.append(0.8)  # High risk
            elif volume_ratio < 1.2:
                risk_factors.append(0.6)  # Medium risk
            else:
                risk_factors.append(0.3)  # Low risk
            
            # Market structure risk
            structure_analysis = analysis.get('market_structure', {})
            if structure_analysis.get('consolidation', False):
                risk_factors.append(0.7)  # Higher risk in consolidation
            else:
                risk_factors.append(0.4)
            
            # Time of day / session risk (simplified)
            # In real implementation, you'd check actual market sessions
            risk_factors.append(0.5)  # Neutral
            
            # Volatility risk
            volatility_analysis = analysis.get('volatility_analysis', {})
            if volatility_analysis.get('regime') == 'low_volatility':
                risk_factors.append(0.7)  # Higher risk in low volatility
            else:
                risk_factors.append(0.4)
            
            # Calculate overall false breakout risk
            overall_risk = np.mean(risk_factors) if risk_factors else 0.5
            
            return float(overall_risk)
            
        except Exception as e:
            logger.error(f"Error assessing false breakout risk: {e}")
            return 0.5
    
    def _generate_timeframe_breakout_signals(self, symbol: str, timeframe: str, df: pd.DataFrame,
                                           analysis: Dict[str, Any], 
                                           market_structure: MarketStructure) -> List[SignalEvent]:
        """Generate breakout signals for specific timeframe"""
        try:
            signals = []
            
            # Extract analysis components
            sr_analysis = analysis.get('support_resistance', {})
            volume_analysis = analysis.get('volume_analysis', {})
            volatility_analysis = analysis.get('volatility_analysis', {})
            momentum_analysis = analysis.get('momentum_analysis', {})
            
            current_price = df['close'].iloc[-1]
            
            # Check for resistance breakout
            nearest_resistance = sr_analysis.get('nearest_resistance')
            if nearest_resistance and self._is_breakout_occurring(
                current_price, nearest_resistance['level'], 'resistance', df
            ):
                signal_data = {
                    'type': BreakoutType.RESISTANCE_BREAKOUT,
                    'direction': 'bullish',
                    'breakout_level': nearest_resistance['level'],
                    'level_strength': nearest_resistance['strength'],
                    'distance': current_price - nearest_resistance['level']
                }
                
                breakout_signal = self._create_breakout_signal(
                    symbol, timeframe, signal_data, df, analysis, market_structure
                )
                
                if breakout_signal:
                    signals.append(breakout_signal)
            
            # Check for support breakdown
            nearest_support = sr_analysis.get('nearest_support')
            if nearest_support and self._is_breakout_occurring(
                current_price, nearest_support['level'], 'support', df
            ):
                signal_data = {
                    'type': BreakoutType.SUPPORT_BREAKDOWN,
                    'direction': 'bearish',
                    'breakout_level': nearest_support['level'],
                    'level_strength': nearest_support['strength'],
                    'distance': nearest_support['level'] - current_price
                }
                
                breakout_signal = self._create_breakout_signal(
                    symbol, timeframe, signal_data, df, analysis, market_structure
                )
                
                if breakout_signal:
                    signals.append(breakout_signal)
            
            # Check for volatility breakout
            if volatility_analysis.get('bb_squeeze') and volatility_analysis.get('volatility_expansion'):
                direction = 'bullish' if momentum_analysis.get('momentum_direction') == 'bullish' else 'bearish'
                
                signal_data = {
                    'type': BreakoutType.VOLATILITY_BREAKOUT,
                    'direction': direction,
                    'breakout_level': current_price,
                    'level_strength': 0.6,
                    'distance': volatility_analysis.get('current_atr', 0) * 0.5
                }
                
                breakout_signal = self._create_breakout_signal(
                    symbol, timeframe, signal_data, df, analysis, market_structure
                )
                
                if breakout_signal:
                    signals.append(breakout_signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error generating timeframe breakout signals: {e}")
            return []
    
    def _is_breakout_occurring(self, current_price: float, level: float, 
                             level_type: str, df: pd.DataFrame) -> bool:
        """Check if a breakout is currently occurring"""
        try:
            # Calculate minimum breakout distance
            atr = self._calculate_atr(df).iloc[-1]
            min_distance = max(self.min_breakout_distance, atr * 0.5)
            
            if level_type == 'resistance':
                # Price must be above resistance by minimum distance
                breakout_distance = current_price - level
                is_breakout = breakout_distance > min_distance
                
                # Check if this is a fresh breakout (not already broken)
                recent_prices = df['close'].tail(3)
                was_below = all(price <= level + min_distance * 0.5 for price in recent_prices.iloc[:-1])
                
                return is_breakout and was_below
                
            else:  # support
                # Price must be below support by minimum distance
                breakout_distance = level - current_price
                is_breakout = breakout_distance > min_distance
                
                # Check if this is a fresh breakout
                recent_prices = df['close'].tail(3)
                was_above = all(price >= level - min_distance * 0.5 for price in recent_prices.iloc[:-1])
                
                return is_breakout and was_above
                
        except Exception as e:
            logger.error(f"Error checking breakout occurrence: {e}")
            return False
    
    def _create_breakout_signal(self, symbol: str, timeframe: str, signal_data: Dict[str, Any],
                              df: pd.DataFrame, analysis: Dict[str, Any], 
                              market_structure: MarketStructure) -> Optional[SignalEvent]:
        """Create enhanced breakout signal"""
        try:
            current_price = df['close'].iloc[-1]
            atr = self._calculate_atr(df).iloc[-1]
            
            # Calculate confidence
            confidence = self._calculate_breakout_confidence(signal_data, analysis, market_structure)
            
            # Skip if confidence too low
            if confidence < self.breakout_threshold:
                return None
            
            # Calculate stop loss and take profit
            if signal_data['direction'] == 'bullish':
                stop_loss = current_price - (atr * self.stop_loss_atr_multiple)
                target_distance = atr * self.stop_loss_atr_multiple * self.take_profit_ratio
                take_profit = current_price + target_distance
            else:
                stop_loss = current_price + (atr * self.stop_loss_atr_multiple)
                target_distance = atr * self.stop_loss_atr_multiple * self.take_profit_ratio
                take_profit = current_price - target_distance
            
            # Risk-reward validation
            risk = abs(current_price - stop_loss)
            reward = abs(take_profit - current_price)
            risk_reward_ratio = reward / risk if risk > 0 else 0
            
            # Skip if risk-reward is poor
            if risk_reward_ratio < 1.0:
                return None
            
            # Volume confirmation
            volume_analysis = analysis.get('volume_analysis', {})
            volume_confirmed = volume_analysis.get('breakout_volume_confirmation', False)
            
            # Create signal event
            signal = SignalEvent(
                event_type='BREAKOUT_SIGNAL',
                symbol=symbol,
                timeframe=timeframe,
                timestamp=datetime.utcnow(),
                direction=signal_data['direction'],
                strength=confidence,
                level=current_price,
                metadata={
                    'breakout_type': signal_data['type'].value,
                    'breakout_level': signal_data['breakout_level'],
                    'target_price': take_profit,
                    'stop_loss': stop_loss,
                    'confidence': confidence,
                    'market_structure': market_structure.value,
                    'volume_confirmed': volume_confirmed,
                    'level_strength': signal_data['level_strength'],
                    'breakout_distance': signal_data['distance'],
                    'risk_reward_ratio': risk_reward_ratio,
                    'atr': atr,
                    'false_breakout_risk': analysis.get('false_breakout_risk', 0.5),
                    'breakout_probability': analysis.get('breakout_probability', 0.5),
                    'analysis_summary': self._create_breakout_analysis_summary(analysis)
                }
            )
            
            return signal
            
        except Exception as e:
            logger.error(f"Error creating breakout signal: {e}")
            return None
    
    def _calculate_breakout_confidence(self, signal_data: Dict[str, Any],
                                     analysis: Dict[str, Any], 
                                     market_structure: MarketStructure) -> float:
        """Calculate confidence score for breakout signal"""
        try:
            confidence_factors = []
            
            # Base confidence from level strength
            level_strength = signal_data.get('level_strength', 0.5)
            confidence_factors.append(level_strength)
            
            # Volume confirmation factor
            volume_analysis = analysis.get('volume_analysis', {})
            if volume_analysis.get('volume_surge', False):
                confidence_factors.append(0.9)
            elif volume_analysis.get('volume_ratio', 1.0) > 1.2:
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.4)
            
            # Volatility factor
            volatility_analysis = analysis.get('volatility_analysis', {})
            if volatility_analysis.get('volatility_expansion', False):
                confidence_factors.append(0.8)
            elif volatility_analysis.get('bb_squeeze', False):
                confidence_factors.append(0.9)  # Squeeze before expansion
            else:
                confidence_factors.append(0.5)
            
            # Momentum alignment factor
            momentum_analysis = analysis.get('momentum_analysis', {})
            momentum_direction = momentum_analysis.get('momentum_direction', 'neutral')
            signal_direction = signal_data['direction']
            
            if (momentum_direction == 'bullish' and signal_direction == 'bullish') or \
               (momentum_direction == 'bearish' and signal_direction == 'bearish'):
                confidence_factors.append(0.8)
            else:
                confidence_factors.append(0.4)
                
            # Market structure factor
            structure_multipliers = {
                MarketStructure.CONSOLIDATION: 1.2,  # Breakouts from consolidation are strong
                MarketStructure.RANGING: 1.1,
                MarketStructure.TRENDING_UP: 0.9 if signal_direction == 'bullish' else 0.7,
                MarketStructure.TRENDING_DOWN: 0.9 if signal_direction == 'bearish' else 0.7,
                MarketStructure.ACCUMULATION: 1.1,
                MarketStructure.DISTRIBUTION: 1.1
            }
            
            structure_multiplier = structure_multipliers.get(market_structure, 1.0)
            
            # Distance factor (closer to level = higher confidence for breakout)
            breakout_distance = signal_data.get('distance', 0)
            atr_estimate = breakout_distance * 50  # Rough ATR estimate
            distance_factor = min(1.0, breakout_distance / (atr_estimate * 0.5)) if atr_estimate > 0 else 0.7
            confidence_factors.append(distance_factor)
            
            # Calculate base confidence
            base_confidence = np.mean(confidence_factors) if confidence_factors else 0.5
            
            # Apply structure multiplier
            final_confidence = min(0.95, base_confidence * structure_multiplier)
            
            return float(final_confidence)
            
        except Exception as e:
            logger.error(f"Error calculating breakout confidence: {e}")
            return 0.5
    
    def _combine_timeframe_breakout_signals(self, symbol: str,
                                          timeframe_signals: Dict[str, List[SignalEvent]],
                                          timeframe_analysis: Dict[str, Dict[str, Any]]) -> List[SignalEvent]:
        """Combine breakout signals from multiple timeframes"""
        try:
            if not timeframe_signals:
                return []
            
            # Timeframe weights for breakout analysis
            timeframe_weights = {
                'M15': 0.3,
                'H1': 0.5,
                'H4': 0.8,
                'D1': 1.0
            }
            
            combined_signals = []
            
            # Group signals by direction
            direction_groups = defaultdict(list)
            
            for timeframe, signals in timeframe_signals.items():
                weight = timeframe_weights.get(timeframe, 0.5)
                for signal in signals:
                    direction_groups[signal.direction].append((timeframe, signal, weight))
            
            # Create combined signals for aligned directions
            for direction, signal_group in direction_groups.items():
                if len(signal_group) >= 2:  # Require at least 2 timeframe confirmations
                    # Calculate weighted confidence
                    total_weight = sum(weight for _, _, weight in signal_group)
                    weighted_confidence = sum(signal.strength * weight for _, signal, weight in signal_group) / total_weight
                    
                    # Use highest timeframe signal as base
                    best_signal = max(signal_group, key=lambda x: timeframe_weights.get(x[0], 0))[1]
                    
                    # Create enhanced combined signal
                    combined_signal = SignalEvent(
                        event_type='MULTI_TIMEFRAME_BREAKOUT',
                        symbol=symbol,
                        timeframe='MULTI',
                        timestamp=datetime.utcnow(),
                        direction=direction,
                        strength=min(0.95, weighted_confidence),
                        level=best_signal.level,
                        metadata={
                            **best_signal.metadata,
                            'timeframe_alignment': total_weight,
                            'confirming_timeframes': [tf for tf, _, _ in signal_group],
                            'timeframe_count': len(signal_group),
                            'multi_timeframe_analysis': timeframe_analysis
                        }
                    )
                    combined_signals.append(combined_signal)
            
            return combined_signals
            
        except Exception as e:
            logger.error(f"Error combining timeframe breakout signals: {e}")
            return []
    
    def _filter_and_validate_breakout_signals(self, signals: List[SignalEvent]) -> List[SignalEvent]:
        """Apply advanced filtering to breakout signals"""
        try:
            if not signals:
                return signals
            
            filtered_signals = []
            
            for signal in signals:
                # Strength filter
                if signal.strength < self.breakout_threshold:
                    continue
                
                # Confidence filter
                confidence = signal.metadata.get('confidence', 0.5)
                if confidence < 0.6:
                    continue
                
                # Risk-reward filter
                risk_reward = signal.metadata.get('risk_reward_ratio', 0)
                if risk_reward < 1.0:
                    continue
                
                # False breakout risk filter
                false_breakout_risk = signal.metadata.get('false_breakout_risk', 0.5)
                if false_breakout_risk > 0.7:
                    continue
                
                # Volume confirmation filter (if required)
                if self.volume_confirmation_required:
                    volume_confirmed = signal.metadata.get('volume_confirmed', False)
                    if not volume_confirmed:
                        continue
                
                # Level strength filter
                level_strength = signal.metadata.get('level_strength', 0.5)
                if level_strength < 0.4:
                    continue
                
                filtered_signals.append(signal)
            
            # Limit signals per session
            return filtered_signals[:self.max_signals_per_session]
            
        except Exception as e:
            logger.error(f"Error filtering breakout signals: {e}")
            return signals
    
    def _update_signal_history(self, signals: List[SignalEvent]):
        """Update signal history for performance tracking"""
        try:
            for signal in signals:
                self.signal_history.append({
                    'timestamp': signal.timestamp,
                    'symbol': signal.symbol,
                    'direction': signal.direction,
                    'strength': signal.strength,
                    'confidence': signal.metadata.get('confidence', 0.5),
                    'breakout_type': signal.metadata.get('breakout_type'),
                    'market_structure': signal.metadata.get('market_structure'),
                    'volume_confirmed': signal.metadata.get('volume_confirmed', False)
                })
                
                self.performance_monitor['signals_generated'] += 1
            
        except Exception as e:
            logger.error(f"Error updating signal history: {e}")
    
    def _create_breakout_analysis_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create summary of breakout analysis for metadata"""
        try:
            summary = {}
            
            # Support/resistance summary
            sr_data = analysis.get('support_resistance', {})
            if sr_data:
                summary['nearest_resistance_strength'] = sr_data.get('nearest_resistance', {}).get('strength', 0)
                summary['nearest_support_strength'] = sr_data.get('nearest_support', {}).get('strength', 0)
            
            # Volume summary
            volume_data = analysis.get('volume_analysis', {})
            if volume_data:
                summary['volume_ratio'] = volume_data.get('volume_ratio', 1.0)
                summary['volume_surge'] = volume_data.get('volume_surge', False)
            
            # Volatility summary
            volatility_data = analysis.get('volatility_analysis', {})
            if volatility_data:
                summary['volatility_expansion'] = volatility_data.get('volatility_expansion', False)
                summary['bb_squeeze'] = volatility_data.get('bb_squeeze', False)
            
            # Momentum summary
            momentum_data = analysis.get('momentum_analysis', {})
            if momentum_data:
                summary['momentum_direction'] = momentum_data.get('momentum_direction', 'neutral')
                summary['momentum_strength'] = momentum_data.get('momentum_strength', 0)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error creating breakout analysis summary: {e}")
            return {}
    
    # Helper methods for technical indicators
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
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
            return pd.Series(0, index=df.index)
    
    def _calculate_rsi(self, df: pd.DataFrame) -> pd.Series:
        """Calculate RSI indicator"""
        try:
            delta = df['close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            
            avg_gain = gain.rolling(self.rsi_period).mean()
            avg_loss = loss.rolling(self.rsi_period).mean()
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi.fillna(50)
            
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return pd.Series(50, index=df.index)
    
    def _calculate_macd(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate MACD indicator"""
        try:
            ema_fast = df['close'].ewm(span=self.macd_fast).mean()
            ema_slow = df['close'].ewm(span=self.macd_slow).mean()
            macd = ema_fast - ema_slow
            signal_line = macd.ewm(span=9).mean()
            histogram = macd - signal_line
            
            return {
                'macd': macd.iloc[-1],
                'macd_signal': signal_line.iloc[-1],
                'macd_histogram': histogram.iloc[-1],
                'macd_momentum': 'bullish' if macd.iloc[-1] > signal_line.iloc[-1] else 'bearish'
            }
            
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return {'macd': 0, 'macd_signal': 0, 'macd_histogram': 0, 'macd_momentum': 'neutral'}
    
    def get_required_data(self) -> Dict[str, List[str]]:
        """Return required data specification"""
        return {
            '*': self.timeframes  # All symbols need specified timeframes
        }
    
    def validate_signal(self, signal: SignalEvent) -> bool:
        """Validate individual breakout signal"""
        try:
            # Basic validation
            if not signal or signal.strength < self.breakout_threshold:
                return False
            
            # Confidence validation
            confidence = signal.metadata.get('confidence', 0.5)
            if confidence < 0.6:
                return False
            
            # Direction validation
            if signal.direction not in ['bullish', 'bearish']:
                return False
            
            # Risk-reward validation
            risk_reward = signal.metadata.get('risk_reward_ratio', 0)
            if risk_reward < 1.0:
                return False
            
            # Breakout-specific validation
            breakout_level = signal.metadata.get('breakout_level')
            if not breakout_level:
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
                'successful_breakouts': self.performance_monitor['successful_breakouts'],
                'false_breakouts': self.performance_monitor['false_breakouts'],
                'breakout_success_rate': (self.performance_monitor['successful_breakouts'] / 
                                        max(1, self.performance_monitor['signals_generated'])),
                'avg_breakout_distance': self.performance_monitor['avg_breakout_distance'],
                'best_breakout_profit': self.performance_monitor['best_breakout_profit'],
                'worst_breakout_loss': self.performance_monitor['worst_breakout_loss'],
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
            logger.info(f"Cleaning up Enhanced Breakout Strategy: {self.name}")
            
            # Clear history and caches
            self.signal_history.clear()
            self.performance_metrics.clear()
            self.breakout_success_rates.clear()
            self.level_history.clear()
            
            # Reset performance monitor
            self.performance_monitor = defaultdict(list)
            
            # Clear market structure data
            self.market_structure = {
                'current_structure': MarketStructure.RANGING,
                'support_levels': [],
                'resistance_levels': [],
                'trend_lines': [],
                'consolidation_zones': []
            }
            
            logger.info("Enhanced Breakout Strategy cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Export the enhanced strategy
__all__ = ['EnhancedBreakoutStrategy', 'BreakoutType', 'MarketStructure', 'BreakoutSignal']

# Compatibility alias
BreakoutStrategy = EnhancedBreakoutStrategy
