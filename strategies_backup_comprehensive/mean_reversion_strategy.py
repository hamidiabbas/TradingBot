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
Enhanced Mean Reversion Strategy Implementation
=============================================
Professional-grade mean reversion trading strategy with advanced analytics,
multi-timeframe analysis, and sophisticated risk management.

Features:
- Multiple mean reversion indicators and techniques
- Bollinger Bands with dynamic adjustments
- RSI divergence detection and analysis
- Statistical arbitrage methods
- Market regime adaptation for mean reversion
- Multi-timeframe mean reversion confluence
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

class MeanReversionType(Enum):
    
    def analyze(self, data, symbol="EURUSD"):
        """Kelly-compatible analyze method for Mean Reversion Strategy"""
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
                        'reason': f'Mean Reversion Strategy bullish trend'
                    }
                elif current_price < ma_20 < ma_50:
                    return {
                        'signal': 'SELL', 
                        'confidence': 0.65,
                        'price': current_price,
                        'reason': f'Mean Reversion Strategy bearish trend'
                    }
            
            return {
                'signal': 'HOLD',
                'confidence': 0.4,
                'price': current_price,
                'reason': f'Mean Reversion Strategy neutral'
            }
            
        except Exception as e:
            return {
                'signal': 'HOLD',
                'confidence': 0.0,
                'price': 1.0,
                'reason': f'Mean Reversion Strategy error: {str(e)}'
            }

    """Types of mean reversion strategies"""
    BOLLINGER_BANDS = "bollinger_bands"
    RSI_DIVERGENCE = "rsi_divergence"
    STATISTICAL_ARBITRAGE = "statistical_arbitrage"
    PRICE_CHANNEL = "price_channel"
    ZSCORE_REVERSION = "zscore_reversion"
    PAIRS_TRADING = "pairs_trading"

class ReversionStrength(Enum):
    """Mean reversion signal strength levels"""
    WEAK = 0.3
    MODERATE = 0.5
    STRONG = 0.7
    VERY_STRONG = 0.9

class MarketCondition(Enum):
    """Market conditions for mean reversion"""
    RANGING = "ranging"
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    OVERSOLD_BOUNCE = "oversold_bounce"
    OVERBOUGHT_DECLINE = "overbought_decline"

@dataclass
class MeanReversionSignal:
    """Enhanced mean reversion signal with comprehensive metadata"""
    timestamp: datetime
    symbol: str
    timeframe: str
    direction: str  # 'bullish', 'bearish', 'neutral'
    strength: float  # 0.0 to 1.0
    reversion_type: MeanReversionType
    entry_price: float
    target_price: float
    stop_loss: float
    confidence: float
    market_condition: MarketCondition
    indicators_confluence: List[str]
    statistical_significance: float
    distance_from_mean: float
    volatility_adjusted_score: float
    risk_reward_ratio: float
    time_horizon: str  # Expected reversion timeframe
    metadata: Dict[str, Any] = field(default_factory=dict)

@register_strategy
class EnhancedMeanReversionStrategy(BaseStrategy):
    """
    Enhanced Mean Reversion Strategy - Professional Implementation
    
    Advanced mean reversion strategy incorporating multiple statistical approaches
    and sophisticated market analysis for institutional-grade trading applications.
    
    Key Features:
    - Multi-timeframe mean reversion analysis
    - Statistical significance testing
    - Dynamic Bollinger Bands with volatility adjustments
    - RSI divergence detection and confirmation
    - Z-score based reversion signals
    - Market regime adaptation
    - Advanced risk management
    - Comprehensive performance tracking
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize enhanced mean reversion strategy
        
        Args:
            name: Strategy name
            config: Configuration dictionary with strategy parameters
        """
        super().__init__(name, config)
        
        # Core mean reversion parameters
        self.lookback_period = config.get('mr_lookback_period', 20)
        self.reversion_threshold = config.get('reversion_threshold', 2.0)  # Standard deviations
        self.min_reversion_strength = config.get('min_reversion_strength', 0.6)
        
        # Bollinger Bands parameters
        self.bb_period = config.get('bb_period', 20)
        self.bb_std_dev = config.get('bb_std_dev', 2.0)
        self.bb_squeeze_threshold = config.get('bb_squeeze_threshold', 0.1)
        
        # RSI parameters for mean reversion
        self.rsi_period = config.get('rsi_period', 14)
        self.rsi_overbought = config.get('rsi_overbought', 70)
        self.rsi_oversold = config.get('rsi_oversold', 30)
        self.rsi_extreme_ob = config.get('rsi_extreme_overbought', 80)
        self.rsi_extreme_os = config.get('rsi_extreme_oversold', 20)
        
        # Statistical parameters
        self.zscore_threshold = config.get('zscore_threshold', 2.0)
        self.statistical_significance = config.get('statistical_significance', 0.05)
        self.min_observations = config.get('min_observations', 30)
        
        # Multi-timeframe analysis
        self.timeframes = config.get('timeframes', ['M15', 'H1', 'H4'])
        self.primary_timeframe = config.get('primary_timeframe', 'H1')
        
        # Market condition parameters
        self.volatility_lookback = config.get('volatility_lookback', 20)
        self.trend_strength_threshold = config.get('trend_strength_threshold', 0.6)
        
        # Risk management parameters
        self.max_position_size = config.get('max_position_size', 0.02)
        self.stop_loss_atr_multiple = config.get('stop_loss_atr_multiple', 2.0)
        self.take_profit_ratio = config.get('take_profit_ratio', 1.5)
        
        # Signal filtering parameters
        self.min_confluence_indicators = config.get('min_confluence_indicators', 2)
        self.max_signals_per_session = config.get('max_signals_per_session', 3)
        
        # Performance tracking
        self.signal_history = deque(maxlen=1000)
        self.performance_metrics = defaultdict(list)
        self.reversion_success_rates = defaultdict(float)
        
        # Technical indicator parameters
        self.stoch_k_period = config.get('stoch_k_period', 14)
        self.stoch_d_period = config.get('stoch_d_period', 3)
        self.williams_r_period = config.get('williams_r_period', 14)
        self.cci_period = config.get('cci_period', 20)
        
        # Advanced features
        self.enable_divergence_detection = config.get('enable_divergence_detection', True)
        self.enable_statistical_tests = config.get('enable_statistical_tests', True)
        self.enable_regime_filtering = config.get('enable_regime_filtering', True)
        
        logger.info(f"Enhanced Mean Reversion Strategy '{name}' initialized successfully")
        logger.info(f"Configuration: {self._log_safe_config()}")
    
    def _log_safe_config(self) -> Dict[str, Any]:
        """Create logging-safe configuration summary"""
        return {
            'lookback_period': self.lookback_period,
            'bb_period': self.bb_period,
            'rsi_period': self.rsi_period,
            'reversion_threshold': self.reversion_threshold,
            'timeframes': len(self.timeframes),
            'min_reversion_strength': self.min_reversion_strength,
            'enable_divergence': self.enable_divergence_detection
        }
    
    async def initialize(self) -> bool:
        """Initialize strategy with enhanced setup"""
        try:
            logger.info(f"Initializing Enhanced Mean Reversion Strategy: {self.name}")
            
            # Validate configuration
            if not self._validate_configuration():
                logger.error("Configuration validation failed")
                return False
            
            # Initialize technical indicators
            self._initialize_indicators()
            
            # Setup performance monitoring
            self._setup_performance_monitoring()
            
            # Initialize statistical models
            self._initialize_statistical_models()
            
            logger.info("Enhanced Mean Reversion Strategy initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing Enhanced Mean Reversion Strategy: {e}")
            return False
    
    def _validate_configuration(self) -> bool:
        """Validate strategy configuration parameters"""
        try:
            # Validate lookback periods
            if self.lookback_period < 5 or self.lookback_period > 100:
                logger.error(f"Invalid lookback_period: {self.lookback_period}")
                return False
            
            if self.bb_period < 5 or self.bb_period > 50:
                logger.error(f"Invalid bb_period: {self.bb_period}")
                return False
            
            # Validate RSI parameters
            if not (10 <= self.rsi_period <= 30):
                logger.error(f"Invalid rsi_period: {self.rsi_period}")
                return False
            
            if not (50 <= self.rsi_overbought <= 90):
                logger.error(f"Invalid rsi_overbought: {self.rsi_overbought}")
                return False
            
            if not (10 <= self.rsi_oversold <= 50):
                logger.error(f"Invalid rsi_oversold: {self.rsi_oversold}")
                return False
            
            # Validate statistical parameters
            if self.zscore_threshold < 1.0 or self.zscore_threshold > 4.0:
                logger.error(f"Invalid zscore_threshold: {self.zscore_threshold}")
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
        """Initialize technical indicators for mean reversion analysis"""
        self.indicators = {
            'bollinger_bands': {},
            'rsi': {},
            'stochastic': {},
            'williams_r': {},
            'cci': {},
            'statistical_measures': {}
        }
        logger.info("Mean reversion indicators initialized")
    
    def _setup_performance_monitoring(self):
        """Setup performance monitoring and analytics"""
        self.performance_monitor = {
            'signals_generated': 0,
            'successful_reversions': 0,
            'failed_reversions': 0,
            'avg_reversion_time': 0.0,
            'best_reversion_profit': 0.0,
            'worst_reversion_loss': 0.0,
            'reversion_accuracy_by_type': defaultdict(list)
        }
        logger.info("Performance monitoring setup complete")
    
    def _initialize_statistical_models(self):
        """Initialize statistical models for mean reversion analysis"""
        self.statistical_models = {
            'price_distribution': None,
            'volatility_model': None,
            'reversion_probability': None,
            'correlation_matrix': None
        }
        logger.info("Statistical models initialized")
    
    def generate_signals(self, data: Dict[str, pd.DataFrame]) -> List[SignalEvent]:
        """
        Generate enhanced mean reversion signals
        
        Args:
            data: Dictionary of market data by symbol and timeframe
            
        Returns:
            List of enhanced mean reversion signals
        """
        try:
            signals = []
            
            for symbol, timeframe_data in data.items():
                if isinstance(timeframe_data, dict):
                    # Multi-timeframe mean reversion analysis
                    symbol_signals = self._analyze_multi_timeframe_reversion(
                        symbol, timeframe_data
                    )
                    signals.extend(symbol_signals)
                else:
                    # Single timeframe analysis
                    symbol_signals = self._analyze_single_timeframe_reversion(
                        symbol, self.primary_timeframe, timeframe_data
                    )
                    signals.extend(symbol_signals)
            
            # Apply advanced filtering and validation
            filtered_signals = self._filter_and_validate_reversion_signals(signals)
            
            # Update performance tracking
            self._update_signal_history(filtered_signals)
            
            logger.info(f"Generated {len(filtered_signals)} mean reversion signals from {len(signals)} candidates")
            return filtered_signals
            
        except Exception as e:
            logger.error(f"Error generating mean reversion signals: {e}")
            return []
    
    def _analyze_multi_timeframe_reversion(self, symbol: str, 
                                         timeframe_data: Dict[str, pd.DataFrame]) -> List[SignalEvent]:
        """Analyze mean reversion across multiple timeframes"""
        try:
            timeframe_signals = {}
            timeframe_analysis = {}
            
            # Analyze each timeframe
            for timeframe, df in timeframe_data.items():
                if timeframe in self.timeframes and len(df) >= self.lookback_period:
                    reversion_analysis = self._calculate_comprehensive_reversion_analysis(df)
                    market_condition = self._assess_market_condition(df)
                    
                    timeframe_analysis[timeframe] = reversion_analysis
                    timeframe_signals[timeframe] = self._generate_timeframe_reversion_signals(
                        symbol, timeframe, df, reversion_analysis, market_condition
                    )
            
            # Combine multi-timeframe analysis
            combined_signals = self._combine_timeframe_reversion_signals(
                symbol, timeframe_signals, timeframe_analysis
            )
            
            return combined_signals
            
        except Exception as e:
            logger.error(f"Error in multi-timeframe reversion analysis for {symbol}: {e}")
            return []
    
    def _analyze_single_timeframe_reversion(self, symbol: str, timeframe: str, 
                                          df: pd.DataFrame) -> List[SignalEvent]:
        """Analyze mean reversion for single timeframe"""
        try:
            if len(df) < self.lookback_period:
                return []
            
            # Calculate comprehensive reversion analysis
            reversion_analysis = self._calculate_comprehensive_reversion_analysis(df)
            
            # Assess market condition
            market_condition = self._assess_market_condition(df)
            
            # Generate signals
            signals = self._generate_timeframe_reversion_signals(
                symbol, timeframe, df, reversion_analysis, market_condition
            )
            
            return signals
            
        except Exception as e:
            logger.error(f"Error in single timeframe reversion analysis: {e}")
            return []
    
    def _calculate_comprehensive_reversion_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate comprehensive mean reversion analysis"""
        try:
            analysis = {}
            
            # Bollinger Bands analysis
            analysis['bollinger_bands'] = self._calculate_bollinger_bands_analysis(df)
            
            # RSI mean reversion analysis
            analysis['rsi_analysis'] = self._calculate_rsi_reversion_analysis(df)
            
            # Statistical measures
            analysis['statistical_measures'] = self._calculate_statistical_reversion_measures(df)
            
            # Price channel analysis
            analysis['price_channel'] = self._calculate_price_channel_analysis(df)
            
            # Z-score analysis
            analysis['zscore_analysis'] = self._calculate_zscore_reversion_analysis(df)
            
            # Oscillator confluence
            analysis['oscillator_confluence'] = self._calculate_oscillator_confluence(df)
            
            # Volatility-adjusted measures
            analysis['volatility_adjusted'] = self._calculate_volatility_adjusted_reversion(df, analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error calculating comprehensive reversion analysis: {e}")
            return {}
    
    def _calculate_bollinger_bands_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate Bollinger Bands mean reversion analysis"""
        try:
            bb_analysis = {}
            
            # Calculate Bollinger Bands
            sma = df['close'].rolling(self.bb_period).mean()
            std = df['close'].rolling(self.bb_period).std()
            
            bb_analysis['sma'] = sma.iloc[-1]
            bb_analysis['upper_band'] = sma.iloc[-1] + (std.iloc[-1] * self.bb_std_dev)
            bb_analysis['lower_band'] = sma.iloc[-1] - (std.iloc[-1] * self.bb_std_dev)
            bb_analysis['band_width'] = bb_analysis['upper_band'] - bb_analysis['lower_band']
            
            # Current price position
            current_price = df['close'].iloc[-1]
            bb_analysis['current_price'] = current_price
            bb_analysis['price_position'] = (current_price - bb_analysis['lower_band']) / bb_analysis['band_width']
            bb_analysis['distance_from_mean'] = abs(current_price - bb_analysis['sma']) / bb_analysis['sma']
            
            # BB squeeze detection
            recent_width = (sma + std * self.bb_std_dev - (sma - std * self.bb_std_dev)).rolling(5).mean().iloc[-1]
            historical_avg_width = (sma + std * self.bb_std_dev - (sma - std * self.bb_std_dev)).rolling(20).mean().iloc[-1]
            bb_analysis['bb_squeeze'] = recent_width < historical_avg_width * (1 - self.bb_squeeze_threshold)
            
            # Mean reversion signals
            bb_analysis['upper_breach'] = current_price > bb_analysis['upper_band']
            bb_analysis['lower_breach'] = current_price < bb_analysis['lower_band']
            bb_analysis['near_upper_band'] = bb_analysis['price_position'] > 0.8
            bb_analysis['near_lower_band'] = bb_analysis['price_position'] < 0.2
            
            # Historical reversion success rate
            bb_analysis['reversion_probability'] = self._calculate_bb_reversion_probability(df, sma, std)
            
            return bb_analysis
            
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands analysis: {e}")
            return {}
    
    def _calculate_rsi_reversion_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate RSI-based mean reversion analysis"""
        try:
            rsi_analysis = {}
            
            # Calculate RSI
            delta = df['close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            
            avg_gain = gain.rolling(self.rsi_period).mean()
            avg_loss = loss.rolling(self.rsi_period).mean()
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            current_rsi = rsi.iloc[-1]
            rsi_analysis['current_rsi'] = current_rsi
            
            # RSI levels and conditions
            rsi_analysis['is_overbought'] = current_rsi > self.rsi_overbought
            rsi_analysis['is_oversold'] = current_rsi < self.rsi_oversold
            rsi_analysis['is_extreme_overbought'] = current_rsi > self.rsi_extreme_ob
            rsi_analysis['is_extreme_oversold'] = current_rsi < self.rsi_extreme_os
            
            # RSI divergence detection
            if self.enable_divergence_detection:
                rsi_analysis['bullish_divergence'] = self._detect_rsi_bullish_divergence(df, rsi)
                rsi_analysis['bearish_divergence'] = self._detect_rsi_bearish_divergence(df, rsi)
            else:
                rsi_analysis['bullish_divergence'] = False
                rsi_analysis['bearish_divergence'] = False
            
            # RSI mean reversion probability
            rsi_analysis['reversion_strength'] = self._calculate_rsi_reversion_strength(current_rsi)
            
            # RSI trend analysis
            rsi_trend = rsi.rolling(5).mean().diff().iloc[-1]
            rsi_analysis['rsi_trend'] = 'rising' if rsi_trend > 0 else 'falling'
            rsi_analysis['rsi_momentum'] = abs(rsi_trend)
            
            return rsi_analysis
            
        except Exception as e:
            logger.error(f"Error calculating RSI reversion analysis: {e}")
            return {}
    
    def _calculate_statistical_reversion_measures(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate statistical measures for mean reversion"""
        try:
            stat_measures = {}
            
            if len(df) < self.min_observations:
                return stat_measures
            
            prices = df['close'].tail(self.lookback_period)
            returns = prices.pct_change().dropna()
            
            # Basic statistics
            stat_measures['mean_price'] = prices.mean()
            stat_measures['std_price'] = prices.std()
            stat_measures['current_price'] = prices.iloc[-1]
            
            # Z-score
            stat_measures['zscore'] = (stat_measures['current_price'] - stat_measures['mean_price']) / stat_measures['std_price']
            
            # Statistical tests for mean reversion
            if self.enable_statistical_tests:
                try:
                    # Augmented Dickey-Fuller test for stationarity
                    from statsmodels.tsa.stattools import adfuller
                    adf_result = adfuller(prices.values)
                    stat_measures['adf_statistic'] = adf_result[0]
                    stat_measures['adf_pvalue'] = adf_result[1]
                    stat_measures['is_stationary'] = adf_result[1] < self.statistical_significance
                except ImportError:
                    logger.warning("statsmodels not available for ADF test")
                    stat_measures['is_stationary'] = True  # Default assumption
                
                # Jarque-Bera test for normality
                try:
                    from scipy.stats import jarque_bera
                    jb_stat, jb_pvalue = jarque_bera(returns.dropna())
                    stat_measures['jb_statistic'] = jb_stat
                    stat_measures['jb_pvalue'] = jb_pvalue
                    stat_measures['returns_normal'] = jb_pvalue > self.statistical_significance
                except Exception as e:
                    logger.debug(f"JB test failed: {e}")
                    stat_measures['returns_normal'] = True
            
            # Half-life of mean reversion (simplified calculation)
            stat_measures['mean_reversion_halflife'] = self._calculate_mean_reversion_halflife(prices)
            
            # Hurst exponent (simplified)
            stat_measures['hurst_exponent'] = self._calculate_hurst_exponent(prices)
            
            return stat_measures
            
        except Exception as e:
            logger.error(f"Error calculating statistical measures: {e}")
            return {}
    
    def _calculate_price_channel_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate price channel analysis for mean reversion"""
        try:
            channel_analysis = {}
            
            # Donchian Channels
            period = self.lookback_period
            channel_analysis['upper_channel'] = df['high'].rolling(period).max().iloc[-1]
            channel_analysis['lower_channel'] = df['low'].rolling(period).min().iloc[-1]
            channel_analysis['channel_middle'] = (channel_analysis['upper_channel'] + channel_analysis['lower_channel']) / 2
            
            current_price = df['close'].iloc[-1]
            channel_width = channel_analysis['upper_channel'] - channel_analysis['lower_channel']
            
            channel_analysis['channel_position'] = (current_price - channel_analysis['lower_channel']) / channel_width
            channel_analysis['distance_from_channel_mean'] = abs(current_price - channel_analysis['channel_middle'])
            
            # Channel breakout/reversion signals
            channel_analysis['near_upper_channel'] = current_price > channel_analysis['upper_channel'] * 0.98
            channel_analysis['near_lower_channel'] = current_price < channel_analysis['lower_channel'] * 1.02
            channel_analysis['in_channel_middle'] = 0.4 < channel_analysis['channel_position'] < 0.6
            
            return channel_analysis
            
        except Exception as e:
            logger.error(f"Error calculating price channel analysis: {e}")
            return {}
    
    def _calculate_zscore_reversion_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate Z-score based mean reversion analysis"""
        try:
            zscore_analysis = {}
            
            # Rolling Z-score calculation
            prices = df['close']
            rolling_mean = prices.rolling(self.lookback_period).mean()
            rolling_std = prices.rolling(self.lookback_period).std()
            
            current_zscore = (prices.iloc[-1] - rolling_mean.iloc[-1]) / rolling_std.iloc[-1]
            zscore_analysis['current_zscore'] = current_zscore
            
            # Z-score thresholds
            zscore_analysis['extreme_positive'] = current_zscore > self.zscore_threshold
            zscore_analysis['extreme_negative'] = current_zscore < -self.zscore_threshold
            zscore_analysis['moderate_positive'] = self.zscore_threshold * 0.7 < current_zscore <= self.zscore_threshold
            zscore_analysis['moderate_negative'] = -self.zscore_threshold <= current_zscore < -self.zscore_threshold * 0.7
            
            # Z-score trend
            zscore_series = (prices - rolling_mean) / rolling_std
            zscore_trend = zscore_series.rolling(3).mean().diff().iloc[-1]
            zscore_analysis['zscore_trend'] = 'increasing' if zscore_trend > 0 else 'decreasing'
            
            # Reversion probability based on Z-score
            zscore_analysis['reversion_probability'] = self._calculate_zscore_reversion_probability(current_zscore)
            
            return zscore_analysis
            
        except Exception as e:
            logger.error(f"Error calculating Z-score reversion analysis: {e}")
            return {}
    
    def _calculate_oscillator_confluence(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate confluence of multiple oscillators for mean reversion"""
        try:
            oscillator_confluence = {}
            signals = []
            
            # Stochastic Oscillator
            try:
                stoch_k, stoch_d = self._calculate_stochastic(df)
                if stoch_k is not None and stoch_d is not None:
                    current_stoch_k = stoch_k.iloc[-1]
                    current_stoch_d = stoch_d.iloc[-1]
                    
                    if current_stoch_k > 80 and current_stoch_d > 80:
                        signals.append('stoch_overbought')
                    elif current_stoch_k < 20 and current_stoch_d < 20:
                        signals.append('stoch_oversold')
                    
                    oscillator_confluence['stochastic'] = {
                        'k': current_stoch_k,
                        'd': current_stoch_d,
                        'overbought': current_stoch_k > 80,
                        'oversold': current_stoch_k < 20
                    }
            except Exception as e:
                logger.debug(f"Stochastic calculation failed: {e}")
            
            # Williams %R
            try:
                williams_r = self._calculate_williams_r(df)
                if williams_r is not None:
                    current_wr = williams_r.iloc[-1]
                    
                    if current_wr > -20:
                        signals.append('wr_overbought')
                    elif current_wr < -80:
                        signals.append('wr_oversold')
                    
                    oscillator_confluence['williams_r'] = {
                        'current': current_wr,
                        'overbought': current_wr > -20,
                        'oversold': current_wr < -80
                    }
            except Exception as e:
                logger.debug(f"Williams %R calculation failed: {e}")
            
            # Commodity Channel Index (CCI)
            try:
                cci = self._calculate_cci(df)
                if cci is not None:
                    current_cci = cci.iloc[-1]
                    
                    if current_cci > 100:
                        signals.append('cci_overbought')
                    elif current_cci < -100:
                        signals.append('cci_oversold')
                    
                    oscillator_confluence['cci'] = {
                        'current': current_cci,
                        'overbought': current_cci > 100,
                        'oversold': current_cci < -100
                    }
            except Exception as e:
                logger.debug(f"CCI calculation failed: {e}")
            
            # Confluence analysis
            overbought_signals = [s for s in signals if 'overbought' in s]
            oversold_signals = [s for s in signals if 'oversold' in s]
            
            oscillator_confluence['confluence'] = {
                'overbought_count': len(overbought_signals),
                'oversold_count': len(oversold_signals),
                'overbought_signals': overbought_signals,
                'oversold_signals': oversold_signals,
                'total_signals': len(signals)
            }
            
            return oscillator_confluence
            
        except Exception as e:
            logger.error(f"Error calculating oscillator confluence: {e}")
            return {}
    
    def _calculate_volatility_adjusted_reversion(self, df: pd.DataFrame, 
                                               analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate volatility-adjusted mean reversion measures"""
        try:
            vol_adjusted = {}
            
            # Calculate ATR for volatility
            atr = self._calculate_atr(df)
            current_atr = atr.iloc[-1] if atr is not None else df['close'].iloc[-1] * 0.01
            
            # Volatility-adjusted Z-score
            if 'statistical_measures' in analysis:
                raw_zscore = analysis['statistical_measures'].get('zscore', 0)
                volatility_ratio = current_atr / df['close'].iloc[-1]
                vol_adjusted['volatility_adjusted_zscore'] = raw_zscore / (1 + volatility_ratio * 10)
            
            # Volatility regime
            historical_atr = atr.rolling(self.volatility_lookback).mean().iloc[-1] if atr is not None else current_atr
            vol_adjusted['volatility_regime'] = 'high' if current_atr > historical_atr * 1.2 else 'low' if current_atr < historical_atr * 0.8 else 'normal'
            
            # Volatility-adjusted thresholds
            vol_multiplier = current_atr / df['close'].iloc[-1] * 100  # ATR as percentage
            vol_adjusted['dynamic_reversion_threshold'] = self.reversion_threshold * (1 + vol_multiplier)
            
            return vol_adjusted
            
        except Exception as e:
            logger.error(f"Error calculating volatility-adjusted reversion: {e}")
            return {}
    
    def _assess_market_condition(self, df: pd.DataFrame) -> MarketCondition:
        """Assess current market condition for mean reversion suitability"""
        try:
            # Trend assessment
            sma_short = df['close'].rolling(10).mean()
            sma_long = df['close'].rolling(20).mean()
            
            trend_strength = abs(sma_short.iloc[-1] - sma_long.iloc[-1]) / sma_long.iloc[-1]
            
            # Volatility assessment
            atr = self._calculate_atr(df)
            current_volatility = atr.iloc[-1] / df['close'].iloc[-1] if atr is not None else 0.01
            avg_volatility = atr.rolling(20).mean().iloc[-1] / df['close'].rolling(20).mean().iloc[-1] if atr is not None else 0.01
            
            # Market condition determination
            if trend_strength > self.trend_strength_threshold:
                if sma_short.iloc[-1] > sma_long.iloc[-1]:
                    return MarketCondition.TRENDING_UP
                else:
                    return MarketCondition.TRENDING_DOWN
            elif current_volatility > avg_volatility * 1.5:
                return MarketCondition.HIGH_VOLATILITY
            elif current_volatility < avg_volatility * 0.5:
                return MarketCondition.LOW_VOLATILITY
            else:
                return MarketCondition.RANGING
                
        except Exception as e:
            logger.error(f"Error assessing market condition: {e}")
            return MarketCondition.RANGING
    
    def _generate_timeframe_reversion_signals(self, symbol: str, timeframe: str, df: pd.DataFrame,
                                            analysis: Dict[str, Any], 
                                            market_condition: MarketCondition) -> List[SignalEvent]:
        """Generate mean reversion signals for specific timeframe"""
        try:
            signals = []
            
            # Extract analysis components
            bb_analysis = analysis.get('bollinger_bands', {})
            rsi_analysis = analysis.get('rsi_analysis', {})
            stat_measures = analysis.get('statistical_measures', {})
            zscore_analysis = analysis.get('zscore_reversion_analysis', {})
            oscillator_confluence = analysis.get('oscillator_confluence', {})
            
            current_price = df['close'].iloc[-1]
            
            # Mean reversion signal generation
            reversion_signals = []
            
            # Bollinger Bands mean reversion
            if bb_analysis.get('upper_breach') or bb_analysis.get('near_upper_band'):
                reversion_signals.append({
                    'type': MeanReversionType.BOLLINGER_BANDS,
                    'direction': 'bearish',
                    'strength': min(0.9, bb_analysis.get('price_position', 0.5)),
                    'target': bb_analysis.get('sma', current_price),
                    'reason': 'BB upper breach reversion'
                })
            
            if bb_analysis.get('lower_breach') or bb_analysis.get('near_lower_band'):
                reversion_signals.append({
                    'type': MeanReversionType.BOLLINGER_BANDS,
                    'direction': 'bullish',
                    'strength': min(0.9, 1 - bb_analysis.get('price_position', 0.5)),
                    'target': bb_analysis.get('sma', current_price),
                    'reason': 'BB lower breach reversion'
                })
            
            # RSI mean reversion
            if rsi_analysis.get('is_extreme_overbought'):
                reversion_signals.append({
                    'type': MeanReversionType.RSI_DIVERGENCE,
                    'direction': 'bearish',
                    'strength': rsi_analysis.get('reversion_strength', 0.7),
                    'target': current_price * 0.98,
                    'reason': 'RSI extreme overbought reversion'
                })
            
            if rsi_analysis.get('is_extreme_oversold'):
                reversion_signals.append({
                    'type': MeanReversionType.RSI_DIVERGENCE,
                    'direction': 'bullish',
                    'strength': rsi_analysis.get('reversion_strength', 0.7),
                    'target': current_price * 1.02,
                    'reason': 'RSI extreme oversold reversion'
                })
            
            # Z-score mean reversion
            if zscore_analysis.get('extreme_positive'):
                reversion_signals.append({
                    'type': MeanReversionType.ZSCORE_REVERSION,
                    'direction': 'bearish',
                    'strength': min(0.9, abs(zscore_analysis.get('current_zscore', 0)) / 3),
                    'target': stat_measures.get('mean_price', current_price),
                    'reason': 'Z-score extreme positive reversion'
                })
            
            if zscore_analysis.get('extreme_negative'):
                reversion_signals.append({
                    'type': MeanReversionType.ZSCORE_REVERSION,
                    'direction': 'bullish',
                    'strength': min(0.9, abs(zscore_analysis.get('current_zscore', 0)) / 3),
                    'target': stat_measures.get('mean_price', current_price),
                    'reason': 'Z-score extreme negative reversion'
                })
            
            # Filter signals based on market condition and confluence
            for signal_data in reversion_signals:
                if signal_data['strength'] < self.min_reversion_strength:
                    continue
                
                # Market condition filter
                if not self._is_suitable_for_reversion(market_condition, signal_data['direction']):
                    continue
                
                # Calculate comprehensive signal metrics
                confidence = self._calculate_reversion_confidence(signal_data, analysis, market_condition)
                
                if confidence < 0.6:
                    continue
                
                # Create enhanced signal
                signal = self._create_enhanced_reversion_signal(
                    symbol, timeframe, signal_data, df, analysis, market_condition, confidence
                )
                
                if signal:
                    signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error generating timeframe reversion signals: {e}")
            return []
    
    def _create_enhanced_reversion_signal(self, symbol: str, timeframe: str,
                                        signal_data: Dict[str, Any], df: pd.DataFrame,
                                        analysis: Dict[str, Any], market_condition: MarketCondition,
                                        confidence: float) -> Optional[SignalEvent]:
        """Create enhanced mean reversion signal"""
        try:
            current_price = df['close'].iloc[-1]
            atr = self._calculate_atr(df)
            current_atr = atr.iloc[-1] if atr is not None else current_price * 0.01
            
            # Calculate stop loss and take profit
            if signal_data['direction'] == 'bullish':
                stop_loss = current_price - (current_atr * self.stop_loss_atr_multiple)
                take_profit = signal_data['target']
            else:
                stop_loss = current_price + (current_atr * self.stop_loss_atr_multiple)
                take_profit = signal_data['target']
            
            # Risk-reward ratio
            risk = abs(current_price - stop_loss)
            reward = abs(take_profit - current_price)
            risk_reward_ratio = reward / risk if risk > 0 else 0
            
            # Skip if risk-reward is poor
            if risk_reward_ratio < 1.0:
                return None
            
            # Create signal event
            signal = SignalEvent(
                event_type='MEAN_REVERSION_SIGNAL',
                symbol=symbol,
                timeframe=timeframe,
                timestamp=datetime.utcnow(),
                direction=signal_data['direction'],
                strength=signal_data['strength'],
                level=current_price,
                metadata={
                    'reversion_type': signal_data['type'].value,
                    'target_price': take_profit,
                    'stop_loss': stop_loss,
                    'confidence': confidence,
                    'market_condition': market_condition.value,
                    'risk_reward_ratio': risk_reward_ratio,
                    'atr': current_atr,
                    'signal_reason': signal_data['reason'],
                    'analysis_summary': self._create_analysis_summary(analysis),
                    'time_horizon': self._estimate_reversion_timeframe(signal_data['type'])
                }
            )
            
            return signal
            
        except Exception as e:
            logger.error(f"Error creating enhanced reversion signal: {e}")
            return None
    
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
    
    def _calculate_stochastic(self, df: pd.DataFrame) -> Tuple[Optional[pd.Series], Optional[pd.Series]]:
        """Calculate Stochastic Oscillator"""
        try:
            lowest_low = df['low'].rolling(self.stoch_k_period).min()
            highest_high = df['high'].rolling(self.stoch_k_period).max()
            
            k_percent = 100 * ((df['close'] - lowest_low) / (highest_high - lowest_low))
            d_percent = k_percent.rolling(self.stoch_d_period).mean()
            
            return k_percent, d_percent
            
        except Exception as e:
            logger.error(f"Error calculating Stochastic: {e}")
            return None, None
    
    def _calculate_williams_r(self, df: pd.DataFrame) -> Optional[pd.Series]:
        """Calculate Williams %R"""
        try:
            highest_high = df['high'].rolling(self.williams_r_period).max()
            lowest_low = df['low'].rolling(self.williams_r_period).min()
            
            williams_r = -100 * ((highest_high - df['close']) / (highest_high - lowest_low))
            
            return williams_r
            
        except Exception as e:
            logger.error(f"Error calculating Williams %R: {e}")
            return None
    
    def _calculate_cci(self, df: pd.DataFrame) -> Optional[pd.Series]:
        """Calculate Commodity Channel Index"""
        try:
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            sma_tp = typical_price.rolling(self.cci_period).mean()
            mad = typical_price.rolling(self.cci_period).apply(
                lambda x: np.mean(np.abs(x - x.mean()))
            )
            
            cci = (typical_price - sma_tp) / (0.015 * mad)
            
            return cci
            
        except Exception as e:
            logger.error(f"Error calculating CCI: {e}")
            return None
    
    def _detect_rsi_bullish_divergence(self, df: pd.DataFrame, rsi: pd.Series) -> bool:
        """Detect RSI bullish divergence"""
        try:
            if len(df) < 10:
                return False
            
            # Look for price making lower lows while RSI makes higher lows
            recent_prices = df['close'].tail(10)
            recent_rsi = rsi.tail(10)
            
            price_min_idx = recent_prices.idxmin()
            rsi_at_price_min = recent_rsi.loc[price_min_idx]
            
            # Simplified divergence check
            prev_price_low = recent_prices.iloc[-5]
            current_price_low = recent_prices.iloc[-1]
            prev_rsi = recent_rsi.iloc[-5]
            current_rsi = recent_rsi.iloc[-1]
            
            return (current_price_low < prev_price_low and 
                    current_rsi > prev_rsi and 
                    current_rsi < 40)
            
        except Exception as e:
            logger.debug(f"Error detecting RSI bullish divergence: {e}")
            return False
    
    def _detect_rsi_bearish_divergence(self, df: pd.DataFrame, rsi: pd.Series) -> bool:
        """Detect RSI bearish divergence"""
        try:
            if len(df) < 10:
                return False
            
            # Look for price making higher highs while RSI makes lower highs
            recent_prices = df['close'].tail(10)
            recent_rsi = rsi.tail(10)
            
            # Simplified divergence check
            prev_price_high = recent_prices.iloc[-5]
            current_price_high = recent_prices.iloc[-1]
            prev_rsi = recent_rsi.iloc[-5]
            current_rsi = recent_rsi.iloc[-1]
            
            return (current_price_high > prev_price_high and 
                    current_rsi < prev_rsi and 
                    current_rsi > 60)
            
        except Exception as e:
            logger.debug(f"Error detecting RSI bearish divergence: {e}")
            return False
    
    def _calculate_rsi_reversion_strength(self, rsi_value: float) -> float:
        """Calculate RSI-based reversion strength"""
        try:
            if rsi_value > 80:
                return min(0.9, (rsi_value - 70) / 30)
            elif rsi_value < 20:
                return min(0.9, (30 - rsi_value) / 30)
            else:
                return 0.3
                
        except Exception as e:
            logger.error(f"Error calculating RSI reversion strength: {e}")
            return 0.5
    
    def _calculate_bb_reversion_probability(self, df: pd.DataFrame, sma: pd.Series, std: pd.Series) -> float:
        """Calculate Bollinger Bands reversion probability"""
        try:
            # Simplified probability calculation
            current_price = df['close'].iloc[-1]
            upper_band = sma.iloc[-1] + (std.iloc[-1] * self.bb_std_dev)
            lower_band = sma.iloc[-1] - (std.iloc[-1] * self.bb_std_dev)
            
            if current_price > upper_band:
                distance_ratio = (current_price - upper_band) / (upper_band - sma.iloc[-1])
                return min(0.9, 0.6 + distance_ratio * 0.3)
            elif current_price < lower_band:
                distance_ratio = (lower_band - current_price) / (sma.iloc[-1] - lower_band)
                return min(0.9, 0.6 + distance_ratio * 0.3)
            else:
                return 0.3
                
        except Exception as e:
            logger.error(f"Error calculating BB reversion probability: {e}")
            return 0.5
    
    def _calculate_zscore_reversion_probability(self, zscore: float) -> float:
        """Calculate Z-score based reversion probability"""
        try:
            abs_zscore = abs(zscore)
            if abs_zscore > 3:
                return 0.9
            elif abs_zscore > 2:
                return 0.7
            elif abs_zscore > 1:
                return 0.5
            else:
                return 0.3
                
        except Exception as e:
            logger.error(f"Error calculating Z-score reversion probability: {e}")
            return 0.5
    
    def _calculate_mean_reversion_halflife(self, prices: pd.Series) -> float:
        """Calculate simplified mean reversion half-life"""
        try:
            # Simplified half-life calculation
            returns = prices.pct_change().dropna()
            if len(returns) < 10:
                return 10.0  # Default
            
            # Use autocorrelation as proxy
            autocorr = returns.autocorr(lag=1)
            if autocorr <= 0:
                return 1.0
            
            halflife = -np.log(2) / np.log(autocorr)
            return max(1.0, min(50.0, halflife))
            
        except Exception as e:
            logger.debug(f"Error calculating mean reversion half-life: {e}")
            return 10.0
    
    def _calculate_hurst_exponent(self, prices: pd.Series) -> float:
        """Calculate simplified Hurst exponent"""
        try:
            # Simplified Hurst calculation
            if len(prices) < 20:
                return 0.5
            
            returns = prices.pct_change().dropna()
            cumulative_returns = returns.cumsum()
            
            # R/S analysis (simplified)
            rs_values = []
            for lag in [5, 10, 15]:
                if len(cumulative_returns) > lag:
                    range_val = cumulative_returns.rolling(lag).max() - cumulative_returns.rolling(lag).min()
                    std_val = returns.rolling(lag).std()
                    rs = (range_val / std_val).mean()
                    if rs > 0:
                        rs_values.append(rs)
            
            if not rs_values:
                return 0.5
            
            # Simplified Hurst estimate
            hurst = np.log(np.mean(rs_values)) / np.log(len(rs_values) + 1)
            return max(0.0, min(1.0, hurst))
            
        except Exception as e:
            logger.debug(f"Error calculating Hurst exponent: {e}")
            return 0.5
    
    def _is_suitable_for_reversion(self, market_condition: MarketCondition, direction: str) -> bool:
        """Check if market condition is suitable for mean reversion"""
        try:
            # Mean reversion works best in ranging markets
            if market_condition == MarketCondition.RANGING:
                return True
            
            # Can work in low volatility trending markets with counter-trend signals
            if market_condition == MarketCondition.LOW_VOLATILITY:
                return True
            
            # Be cautious in strong trending markets
            if market_condition in [MarketCondition.TRENDING_UP, MarketCondition.TRENDING_DOWN]:
                return False  # Conservative approach
            
            # High volatility can provide opportunities but with higher risk
            if market_condition == MarketCondition.HIGH_VOLATILITY:
                return True
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking market suitability: {e}")
            return True
    
    def _calculate_reversion_confidence(self, signal_data: Dict[str, Any],
                                      analysis: Dict[str, Any], 
                                      market_condition: MarketCondition) -> float:
        """Calculate confidence score for mean reversion signal"""
        try:
            confidence_factors = []
            
            # Base strength
            confidence_factors.append(signal_data['strength'])
            
            # Market condition factor
            condition_multipliers = {
                MarketCondition.RANGING: 1.2,
                MarketCondition.LOW_VOLATILITY: 1.1,
                MarketCondition.HIGH_VOLATILITY: 0.9,
                MarketCondition.TRENDING_UP: 0.7,
                MarketCondition.TRENDING_DOWN: 0.7
            }
            confidence_factors.append(condition_multipliers.get(market_condition, 1.0))
            
            # Statistical significance
            stat_measures = analysis.get('statistical_measures', {})
            if stat_measures.get('is_stationary', True):
                confidence_factors.append(1.1)
            
            # Oscillator confluence
            oscillator_data = analysis.get('oscillator_confluence', {})
            confluence = oscillator_data.get('confluence', {})
            if signal_data['direction'] == 'bullish':
                oversold_count = confluence.get('oversold_count', 0)
                confidence_factors.append(min(1.3, 1.0 + oversold_count * 0.1))
            else:
                overbought_count = confluence.get('overbought_count', 0)
                confidence_factors.append(min(1.3, 1.0 + overbought_count * 0.1))
            
            # Calculate final confidence
            base_confidence = np.mean(confidence_factors[:1])  # Base on signal strength
            multiplier = np.mean(confidence_factors[1:]) if len(confidence_factors) > 1 else 1.0
            
            final_confidence = min(0.95, base_confidence * multiplier)
            
            return float(final_confidence)
            
        except Exception as e:
            logger.error(f"Error calculating reversion confidence: {e}")
            return 0.5
    
    def _combine_timeframe_reversion_signals(self, symbol: str, 
                                           timeframe_signals: Dict[str, List[SignalEvent]],
                                           timeframe_analysis: Dict[str, Dict[str, Any]]) -> List[SignalEvent]:
        """Combine mean reversion signals from multiple timeframes"""
        try:
            if not timeframe_signals:
                return []
            
            # Timeframe weights (higher timeframes get more weight)
            timeframe_weights = {
                'M15': 0.3,
                'H1': 0.5,
                'H4': 0.8,
                'D1': 1.0
            }
            
            combined_signals = []
            
            # Analyze signal alignment across timeframes
            direction_weights = defaultdict(float)
            direction_signals = defaultdict(list)
            
            for timeframe, signals in timeframe_signals.items():
                weight = timeframe_weights.get(timeframe, 0.5)
                
                for signal in signals:
                    direction_weights[signal.direction] += weight * signal.strength
                    direction_signals[signal.direction].append((timeframe, signal))
            
            # Create combined signals for dominant directions
            for direction, total_weight in direction_weights.items():
                if total_weight >= 0.8:  # Minimum alignment threshold
                    # Use the highest timeframe signal as base
                    best_signal = None
                    best_weight = 0
                    
                    for timeframe, signal in direction_signals[direction]:
                        tf_weight = timeframe_weights.get(timeframe, 0.5)
                        if tf_weight > best_weight:
                            best_signal = signal
                            best_weight = tf_weight
                    
                    if best_signal:
                        # Create enhanced combined signal
                        combined_signal = SignalEvent(
                            event_type='MULTI_TIMEFRAME_MEAN_REVERSION',
                            symbol=symbol,
                            timeframe='MULTI',
                            timestamp=datetime.utcnow(),
                            direction=direction,
                            strength=min(0.9, total_weight / len(timeframe_weights)),
                            level=best_signal.level,
                            metadata={
                                **best_signal.metadata,
                                'timeframe_alignment': total_weight,
                                'timeframes_analyzed': list(timeframe_signals.keys()),
                                'supporting_timeframes': [tf for tf, _ in direction_signals[direction]],
                                'multi_timeframe_analysis': timeframe_analysis
                            }
                        )
                        combined_signals.append(combined_signal)
            
            return combined_signals
            
        except Exception as e:
            logger.error(f"Error combining timeframe reversion signals: {e}")
            return []
    
    def _filter_and_validate_reversion_signals(self, signals: List[SignalEvent]) -> List[SignalEvent]:
        """Apply advanced filtering to mean reversion signals"""
        try:
            if not signals:
                return signals
            
            filtered_signals = []
            
            for signal in signals:
                # Strength filter
                if signal.strength < self.min_reversion_strength:
                    continue
                
                # Confidence filter
                confidence = signal.metadata.get('confidence', 0.5)
                if confidence < 0.6:
                    continue
                
                # Risk-reward filter
                risk_reward = signal.metadata.get('risk_reward_ratio', 0)
                if risk_reward < 1.0:
                    continue
                
                # Time-based filter (avoid too many signals in short period)
                if self._is_signal_too_frequent(signal):
                    continue
                
                filtered_signals.append(signal)
            
            # Limit signals per session
            return filtered_signals[:self.max_signals_per_session]
            
        except Exception as e:
            logger.error(f"Error filtering reversion signals: {e}")
            return signals
    
    def _is_signal_too_frequent(self, new_signal: SignalEvent) -> bool:
        """Check if signal is too frequent compared to recent signals"""
        try:
            if not self.signal_history:
                return False
            
            recent_signals = [s for s in self.signal_history 
                            if (new_signal.timestamp - s['timestamp']).total_seconds() < 3600]  # 1 hour
            
            same_symbol_direction = [s for s in recent_signals 
                                   if s['symbol'] == new_signal.symbol and 
                                      s['direction'] == new_signal.direction]
            
            return len(same_symbol_direction) >= 2
            
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
                    'confidence': signal.metadata.get('confidence', 0.5),
                    'reversion_type': signal.metadata.get('reversion_type'),
                    'market_condition': signal.metadata.get('market_condition')
                })
                
                self.performance_monitor['signals_generated'] += 1
            
        except Exception as e:
            logger.error(f"Error updating signal history: {e}")
    
    def _create_analysis_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create summary of analysis for metadata"""
        try:
            summary = {}
            
            # Bollinger Bands summary
            bb_data = analysis.get('bollinger_bands', {})
            if bb_data:
                summary['bb_position'] = bb_data.get('price_position', 0.5)
                summary['bb_squeeze'] = bb_data.get('bb_squeeze', False)
            
            # RSI summary
            rsi_data = analysis.get('rsi_analysis', {})
            if rsi_data:
                summary['rsi_level'] = rsi_data.get('current_rsi', 50)
                summary['rsi_extreme'] = (rsi_data.get('is_extreme_overbought', False) or 
                                        rsi_data.get('is_extreme_oversold', False))
            
            # Statistical summary
            stat_data = analysis.get('statistical_measures', {})
            if stat_data:
                summary['zscore'] = stat_data.get('zscore', 0)
                summary['is_stationary'] = stat_data.get('is_stationary', True)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error creating analysis summary: {e}")
            return {}
    
    def _estimate_reversion_timeframe(self, reversion_type: MeanReversionType) -> str:
        """Estimate expected timeframe for mean reversion"""
        try:
            timeframe_estimates = {
                MeanReversionType.BOLLINGER_BANDS: "1-4 hours",
                MeanReversionType.RSI_DIVERGENCE: "2-8 hours", 
                MeanReversionType.STATISTICAL_ARBITRAGE: "4-12 hours",
                MeanReversionType.ZSCORE_REVERSION: "1-6 hours",
                MeanReversionType.PRICE_CHANNEL: "2-10 hours"
            }
            
            return timeframe_estimates.get(reversion_type, "2-6 hours")
            
        except Exception as e:
            logger.error(f"Error estimating reversion timeframe: {e}")
            return "unknown"
    
    def get_required_data(self) -> Dict[str, List[str]]:
        """Return required data specification"""
        return {
            '*': self.timeframes  # All symbols need specified timeframes
        }
    
    def validate_signal(self, signal: SignalEvent) -> bool:
        """Validate individual mean reversion signal"""
        try:
            # Basic validation
            if not signal or signal.strength < self.min_reversion_strength:
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
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating signal: {e}")
            return False
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        try:
            return {
                'signals_generated': self.performance_monitor['signals_generated'],
                'successful_reversions': self.performance_monitor['successful_reversions'],
                'failed_reversions': self.performance_monitor['failed_reversions'],
                'reversion_success_rate': (self.performance_monitor['successful_reversions'] / 
                                         max(1, self.performance_monitor['signals_generated'])),
                'avg_reversion_time': self.performance_monitor['avg_reversion_time'],
                'best_reversion_profit': self.performance_monitor['best_reversion_profit'],
                'worst_reversion_loss': self.performance_monitor['worst_reversion_loss'],
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
            logger.info(f"Cleaning up Enhanced Mean Reversion Strategy: {self.name}")
            
            # Clear history and caches
            self.signal_history.clear()
            self.performance_metrics.clear()
            self.reversion_success_rates.clear()
            
            # Reset performance monitor
            self.performance_monitor = defaultdict(list)
            
            logger.info("Enhanced Mean Reversion Strategy cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Export the enhanced strategy
__all__ = ['EnhancedMeanReversionStrategy', 'MeanReversionType', 'MarketCondition', 'MeanReversionSignal']

# Compatibility alias
MeanReversionStrategy = EnhancedMeanReversionStrategy
