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
Enhanced Scalping Strategy Implementation
========================================
Professional-grade scalping trading strategy with advanced analytics,
high-frequency signal generation, and comprehensive risk management.

Features:
- Multi-timeframe scalping analysis (1M, 5M, 15M)
- High-frequency signal generation and filtering
- Market microstructure analysis and spread monitoring
- Advanced momentum and oscillator indicators
- Volume profile analysis for scalping opportunities
- Rapid execution optimization and latency management
- Advanced signal filtering and validation
- Comprehensive risk management for high-frequency trading
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
import time

# Import base strategy and event system
from strategies.base_strategy import BaseStrategy, SignalEvent, register_strategy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')

class ScalpingType(Enum):
    
    def analyze(self, data, symbol="EURUSD"):
        """Kelly-compatible analyze method for Scalping Strategy"""
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
                        'reason': f'Scalping Strategy bullish trend'
                    }
                elif current_price < ma_20 < ma_50:
                    return {
                        'signal': 'SELL', 
                        'confidence': 0.65,
                        'price': current_price,
                        'reason': f'Scalping Strategy bearish trend'
                    }
            
            return {
                'signal': 'HOLD',
                'confidence': 0.4,
                'price': current_price,
                'reason': f'Scalping Strategy neutral'
            }
            
        except Exception as e:
            return {
                'signal': 'HOLD',
                'confidence': 0.0,
                'price': 1.0,
                'reason': f'Scalping Strategy error: {str(e)}'
            }

    """Types of scalping strategies"""
    MOMENTUM_SCALPING = "momentum_scalping"
    MEAN_REVERSION_SCALPING = "mean_reversion_scalping"
    BREAKOUT_SCALPING = "breakout_scalping"
    NEWS_SCALPING = "news_scalping"
    SPREAD_SCALPING = "spread_scalping"
    VOLUME_SCALPING = "volume_scalping"
    ARBITRAGE_SCALPING = "arbitrage_scalping"

class ScalpingTimeframe(Enum):
    """Scalping timeframes"""
    TICK = "tick"
    M1 = "1min"
    M5 = "5min"
    M15 = "15min"

class MarketMicrostructure(Enum):
    """Market microstructure states"""
    TIGHT_SPREAD = "tight_spread"
    WIDE_SPREAD = "wide_spread"
    HIGH_VOLUME = "high_volume"
    LOW_VOLUME = "low_volume"
    VOLATILE = "volatile"
    STABLE = "stable"
    TRENDING = "trending"
    RANGING = "ranging"

class ScalpingSignalQuality(Enum):
    """Quality levels for scalping signals"""
    EXCELLENT = 0.9
    GOOD = 0.7
    AVERAGE = 0.5
    POOR = 0.3

@dataclass
class ScalpingOpportunity:
    """Enhanced scalping opportunity with comprehensive metadata"""
    timestamp: datetime
    symbol: str
    timeframe: str
    scalping_type: ScalpingType
    direction: str  # 'bullish', 'bearish'
    strength: float  # 0.0 to 1.0
    entry_price: float
    target_price: float
    stop_loss: float
    spread: float
    expected_profit_pips: float
    expected_hold_time_seconds: int
    volume_confirmation: bool
    momentum_score: float
    volatility_score: float
    liquidity_score: float
    execution_urgency: str  # 'immediate', 'fast', 'normal'
    risk_reward_ratio: float
    confidence: float
    market_microstructure: MarketMicrostructure
    supporting_indicators: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ScalpingMetrics:
    """Real-time scalping performance metrics"""
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_pips: float = 0.0
    total_profit: float = 0.0
    avg_hold_time: float = 0.0
    avg_profit_per_trade: float = 0.0
    max_consecutive_wins: int = 0
    max_consecutive_losses: int = 0
    current_streak: int = 0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    trades_per_hour: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)

@register_strategy
class EnhancedScalpingStrategy(BaseStrategy):
    """
    Enhanced Scalping Strategy - Professional Implementation
    
    Advanced high-frequency scalping strategy incorporating multiple scalping
    methodologies, market microstructure analysis, and ultra-fast execution
    for institutional-grade trading applications.
    
    Key Features:
    - Multi-timeframe scalping analysis
    - High-frequency signal generation
    - Market microstructure monitoring
    - Advanced momentum detection
    - Rapid execution optimization
    - Comprehensive risk management
    - Real-time performance tracking
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize enhanced scalping strategy
        
        Args:
            name: Strategy name
            config: Configuration dictionary with strategy parameters
        """
        super().__init__(name, config)
        
        # Core scalping parameters
        self.scalping_types = config.get('scalping_types', [
            ScalpingType.MOMENTUM_SCALPING,
            ScalpingType.MEAN_REVERSION_SCALPING,
            ScalpingType.BREAKOUT_SCALPING
        ])
        self.primary_scalping_type = config.get('primary_scalping_type', ScalpingType.MOMENTUM_SCALPING)
        
        # Timeframe parameters
        self.scalping_timeframes = config.get('scalping_timeframes', ['1min', '5min', '15min'])
        self.primary_timeframe = config.get('primary_timeframe', '1min')
        self.confirmation_timeframe = config.get('confirmation_timeframe', '5min')
        
        # Signal generation parameters
        self.min_signal_strength = config.get('min_signal_strength', 0.7)
        self.max_spread_threshold = config.get('max_spread_threshold', 0.0003)  # 3 pips
        self.min_profit_target_pips = config.get('min_profit_target_pips', 2)
        self.max_hold_time_minutes = config.get('max_hold_time_minutes', 5)
        
        # Market microstructure parameters
        self.min_volume_threshold = config.get('min_volume_threshold', 1.5)
        self.liquidity_requirement = config.get('liquidity_requirement', 0.7)
        self.volatility_threshold = config.get('volatility_threshold', 0.0002)  # 2 pips
        
        # Technical indicator parameters
        self.fast_ema_period = config.get('fast_ema_period', 5)
        self.slow_ema_period = config.get('slow_ema_period', 13)
        self.rsi_period = config.get('rsi_period', 14)
        self.stoch_k_period = config.get('stoch_k_period', 5)
        self.stoch_d_period = config.get('stoch_d_period', 3)
        self.macd_fast = config.get('macd_fast', 5)
        self.macd_slow = config.get('macd_slow', 13)
        self.macd_signal = config.get('macd_signal', 5)
        
        # Risk management parameters
        self.max_position_size = config.get('max_position_size', 0.01)
        self.stop_loss_pips = config.get('stop_loss_pips', 5)
        self.take_profit_pips = config.get('take_profit_pips', 8)
        self.max_daily_loss = config.get('max_daily_loss', 0.02)  # 2% of account
        self.max_concurrent_trades = config.get('max_concurrent_trades', 3)
        
        # Execution parameters
        self.execution_delay_threshold = config.get('execution_delay_threshold', 100)  # milliseconds
        self.slippage_tolerance = config.get('slippage_tolerance', 0.0001)  # 1 pip
        self.requote_tolerance = config.get('requote_tolerance', 2)
        
        # Signal filtering parameters
        self.signal_timeout_seconds = config.get('signal_timeout_seconds', 30)
        self.max_signals_per_minute = config.get('max_signals_per_minute', 10)
        self.consecutive_loss_limit = config.get('consecutive_loss_limit', 3)
        
        # Performance tracking
        self.scalping_metrics = ScalpingMetrics()
        self.signal_history = deque(maxlen=10000)  # Large buffer for high-frequency
        self.trade_history = deque(maxlen=5000)
        self.performance_snapshots = deque(maxlen=1000)
        
        # Market microstructure tracking
        self.spread_history = deque(maxlen=1000)
        self.volume_profile = defaultdict(list)
        self.execution_latency = deque(maxlen=100)
        
        # Advanced features
        self.enable_tick_analysis = config.get('enable_tick_analysis', True)
        self.enable_order_flow_analysis = config.get('enable_order_flow_analysis', True)
        self.enable_spread_monitoring = config.get('enable_spread_monitoring', True)
        self.enable_latency_optimization = config.get('enable_latency_optimization', True)
        
        # Dynamic parameters that adjust based on market conditions
        self.dynamic_spread_threshold = self.max_spread_threshold
        self.dynamic_signal_strength = self.min_signal_strength
        
        logger.info(f"Enhanced Scalping Strategy '{name}' initialized successfully")
        logger.info(f"Configuration: {self._log_safe_config()}")
    
    def _log_safe_config(self) -> Dict[str, Any]:
        """Create logging-safe configuration summary"""
        return {
            'scalping_types': len(self.scalping_types),
            'primary_scalping_type': self.primary_scalping_type.value,
            'timeframes': len(self.scalping_timeframes),
            'min_signal_strength': self.min_signal_strength,
            'max_spread_threshold': self.max_spread_threshold,
            'stop_loss_pips': self.stop_loss_pips,
            'take_profit_pips': self.take_profit_pips
        }
    
    async def initialize(self) -> bool:
        """Initialize strategy with enhanced setup"""
        try:
            logger.info(f"Initializing Enhanced Scalping Strategy: {self.name}")
            
            # Validate configuration
            if not self._validate_configuration():
                logger.error("Configuration validation failed")
                return False
            
            # Initialize scalping engines
            self._initialize_scalping_engines()
            
            # Setup market microstructure monitoring
            self._setup_microstructure_monitoring()
            
            # Initialize technical indicators
            self._initialize_technical_indicators()
            
            # Setup execution optimization
            self._setup_execution_optimization()
            
            # Initialize performance monitoring
            self._setup_performance_monitoring()
            
            logger.info("Enhanced Scalping Strategy initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing Enhanced Scalping Strategy: {e}")
            return False
    
    def _validate_configuration(self) -> bool:
        """Validate strategy configuration parameters"""
        try:
            # Validate scalping types
            if not self.scalping_types:
                logger.error("No scalping types specified")
                return False
            
            if self.primary_scalping_type not in self.scalping_types:
                logger.error(f"Primary scalping type {self.primary_scalping_type} not in scalping types list")
                return False
            
            # Validate timeframes
            if not self.scalping_timeframes:
                logger.error("No scalping timeframes specified")
                return False
            
            if self.primary_timeframe not in self.scalping_timeframes:
                logger.error(f"Primary timeframe {self.primary_timeframe} not in timeframes list")
                return False
            
            # Validate signal parameters
            if not (0.5 <= self.min_signal_strength <= 1.0):
                logger.error(f"Invalid min_signal_strength: {self.min_signal_strength}")
                return False
            
            # Validate spread parameters
            if not (0.0001 <= self.max_spread_threshold <= 0.01):
                logger.error(f"Invalid max_spread_threshold: {self.max_spread_threshold}")
                return False
            
            # Validate profit/loss parameters
            if self.min_profit_target_pips < 1 or self.min_profit_target_pips > 20:
                logger.error(f"Invalid min_profit_target_pips: {self.min_profit_target_pips}")
                return False
            
            if self.stop_loss_pips < 1 or self.stop_loss_pips > 50:
                logger.error(f"Invalid stop_loss_pips: {self.stop_loss_pips}")
                return False
            
            # Validate risk parameters
            if not (0.001 <= self.max_position_size <= 0.1):
                logger.error(f"Invalid max_position_size: {self.max_position_size}")
                return False
            
            if not (0.01 <= self.max_daily_loss <= 0.2):
                logger.error(f"Invalid max_daily_loss: {self.max_daily_loss}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating configuration: {e}")
            return False
    
    def _initialize_scalping_engines(self):
        """Initialize different scalping engines"""
        self.scalping_engines = {
            ScalpingType.MOMENTUM_SCALPING: self._momentum_scalping_engine,
            ScalpingType.MEAN_REVERSION_SCALPING: self._mean_reversion_scalping_engine,
            ScalpingType.BREAKOUT_SCALPING: self._breakout_scalping_engine,
            ScalpingType.NEWS_SCALPING: self._news_scalping_engine,
            ScalpingType.SPREAD_SCALPING: self._spread_scalping_engine,
            ScalpingType.VOLUME_SCALPING: self._volume_scalping_engine,
            ScalpingType.ARBITRAGE_SCALPING: self._arbitrage_scalping_engine
        }
        logger.info("Scalping engines initialized")
    
    def _setup_microstructure_monitoring(self):
        """Setup market microstructure monitoring"""
        self.microstructure_monitor = {
            'spread_tracker': self._track_spread_changes,
            'volume_analyzer': self._analyze_volume_patterns,
            'liquidity_monitor': self._monitor_liquidity_levels,
            'volatility_tracker': self._track_volatility_changes
        }
        logger.info("Market microstructure monitoring setup complete")
    
    def _initialize_technical_indicators(self):
        """Initialize technical indicators for scalping"""
        self.indicators = {
            'ema_fast': {},
            'ema_slow': {},
            'rsi': {},
            'stochastic': {},
            'macd': {},
            'bollinger_bands': {},
            'momentum': {},
            'williams_r': {}
        }
        logger.info("Technical indicators initialized")
    
    def _setup_execution_optimization(self):
        """Setup execution optimization components"""
        self.execution_optimizer = {
            'latency_monitor': deque(maxlen=100),
            'slippage_tracker': deque(maxlen=100),
            'requote_counter': defaultdict(int),
            'execution_quality_score': 1.0
        }
        logger.info("Execution optimization setup complete")
    
    def _setup_performance_monitoring(self):
        """Setup performance monitoring and analytics"""
        self.performance_monitor = {
            'real_time_pnl': 0.0,
            'daily_pnl': 0.0,
            'trades_today': 0,
            'win_streak': 0,
            'loss_streak': 0,
            'max_drawdown_today': 0.0,
            'total_fees_paid': 0.0,
            'execution_metrics': defaultdict(list)
        }
        logger.info("Performance monitoring setup complete")
    
    def generate_signals(self, data: Dict[str, pd.DataFrame]) -> List[SignalEvent]:
        """
        Generate enhanced scalping signals with high-frequency analysis
        
        Args:
            data: Dictionary of market data by symbol and timeframe
            
        Returns:
            List of enhanced scalping signals
        """
        try:
            signals = []
            current_time = datetime.utcnow()
            
            # Check if we should continue scalping (risk management)
            if not self._should_continue_scalping():
                logger.info("Scalping paused due to risk management rules")
                return signals
            
            for symbol, timeframe_data in data.items():
                if isinstance(timeframe_data, dict):
                    # Multi-timeframe scalping analysis
                    symbol_signals = self._analyze_multi_timeframe_scalping(
                        symbol, timeframe_data, current_time
                    )
                    signals.extend(symbol_signals)
                else:
                    # Single timeframe analysis
                    symbol_signals = self._analyze_single_timeframe_scalping(
                        symbol, self.primary_timeframe, timeframe_data, current_time
                    )
                    signals.extend(symbol_signals)
            
            # Apply high-frequency signal filtering
            filtered_signals = self._filter_scalping_signals(signals, current_time)
            
            # Optimize signal execution order
            optimized_signals = self._optimize_signal_execution(filtered_signals)
            
            # Update performance tracking
            self._update_signal_history(optimized_signals)
            
            logger.info(f"Generated {len(optimized_signals)} scalping signals from {len(signals)} candidates")
            return optimized_signals
            
        except Exception as e:
            logger.error(f"Error generating scalping signals: {e}")
            return []
    
    def _should_continue_scalping(self) -> bool:
        """Check if scalping should continue based on risk management"""
        try:
            # Check daily loss limit
            if abs(self.performance_monitor['daily_pnl']) > self.max_daily_loss:
                return False
            
            # Check consecutive losses
            if self.performance_monitor['loss_streak'] >= self.consecutive_loss_limit:
                return False
            
            # Check maximum trades per day
            if self.performance_monitor['trades_today'] > 200:  # Scalping limit
                return False
            
            # Check execution quality
            if self.execution_optimizer['execution_quality_score'] < 0.5:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking scalping continuation: {e}")
            return True
    
    def _analyze_multi_timeframe_scalping(self, symbol: str, 
                                        timeframe_data: Dict[str, pd.DataFrame],
                                        current_time: datetime) -> List[SignalEvent]:
        """Analyze scalping opportunities across multiple timeframes"""
        try:
            timeframe_analysis = {}
            scalping_opportunities = []
            
            # Analyze each timeframe for scalping signals
            for timeframe, df in timeframe_data.items():
                if timeframe in self.scalping_timeframes and len(df) >= 20:
                    analysis = self._analyze_scalping_timeframe(df, timeframe, symbol)
                    timeframe_analysis[timeframe] = analysis
                    
                    # Generate scalping opportunities for this timeframe
                    tf_opportunities = self._generate_timeframe_scalping_opportunities(
                        symbol, timeframe, df, analysis, current_time
                    )
                    scalping_opportunities.extend(tf_opportunities)
            
            # Combine and validate multi-timeframe opportunities
            validated_signals = self._validate_multi_timeframe_scalping(
                symbol, scalping_opportunities, timeframe_analysis
            )
            
            return validated_signals
            
        except Exception as e:
            logger.error(f"Error in multi-timeframe scalping analysis for {symbol}: {e}")
            return []
    
    def _analyze_single_timeframe_scalping(self, symbol: str, timeframe: str, 
                                         df: pd.DataFrame, current_time: datetime) -> List[SignalEvent]:
        """Analyze scalping opportunities for single timeframe"""
        try:
            if len(df) < 20:
                return []
            
            # Analyze timeframe for scalping
            analysis = self._analyze_scalping_timeframe(df, timeframe, symbol)
            
            # Generate scalping opportunities
            opportunities = self._generate_timeframe_scalping_opportunities(
                symbol, timeframe, df, analysis, current_time
            )
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error in single timeframe scalping analysis: {e}")
            return []
    
    def _analyze_scalping_timeframe(self, df: pd.DataFrame, timeframe: str, symbol: str) -> Dict[str, Any]:
        """Comprehensive scalping analysis for a timeframe"""
        try:
            analysis = {}
            
            # Market microstructure analysis
            analysis['microstructure'] = self._analyze_market_microstructure(df)
            
            # Technical indicator analysis
            analysis['indicators'] = self._calculate_scalping_indicators(df)
            
            # Momentum analysis
            analysis['momentum'] = self._analyze_scalping_momentum(df)
            
            # Volume analysis
            analysis['volume'] = self._analyze_scalping_volume(df)
            
            # Volatility analysis
            analysis['volatility'] = self._analyze_scalping_volatility(df)
            
            # Price action analysis
            analysis['price_action'] = self._analyze_scalping_price_action(df)
            
            # Spread analysis (if available)
            analysis['spread'] = self._analyze_spread_conditions(df, symbol)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing scalping timeframe: {e}")
            return {}
    
    def _analyze_market_microstructure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze market microstructure for scalping"""
        try:
            microstructure = {}
            
            # Price movement characteristics
            price_changes = df['close'].diff().dropna()
            microstructure['avg_price_change'] = price_changes.mean()
            microstructure['price_change_volatility'] = price_changes.std()
            
            # Tick-level analysis (simulated)
            microstructure['price_precision'] = self._estimate_price_precision(df)
            microstructure['liquidity_score'] = self._estimate_liquidity_score(df)
            
            # Market state
            microstructure['market_state'] = self._determine_market_state(df)
            
            return microstructure
            
        except Exception as e:
            logger.error(f"Error analyzing market microstructure: {e}")
            return {}
    
    def _calculate_scalping_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate technical indicators optimized for scalping"""
        try:
            indicators = {}
            
            # Fast EMAs for scalping
            ema_fast = df['close'].ewm(span=self.fast_ema_period).mean()
            ema_slow = df['close'].ewm(span=self.slow_ema_period).mean()
            
            indicators['ema_fast'] = ema_fast.iloc[-1]
            indicators['ema_slow'] = ema_slow.iloc[-1]
            indicators['ema_signal'] = 'bullish' if ema_fast.iloc[-1] > ema_slow.iloc[-1] else 'bearish'
            indicators['ema_strength'] = abs(ema_fast.iloc[-1] - ema_slow.iloc[-1]) / ema_slow.iloc[-1]
            
            # Fast RSI
            rsi = self._calculate_rsi(df, self.rsi_period)
            indicators['rsi'] = rsi.iloc[-1]
            indicators['rsi_signal'] = self._interpret_rsi_for_scalping(rsi.iloc[-1])
            
            # Fast Stochastic
            stoch_k, stoch_d = self._calculate_stochastic(df)
            indicators['stoch_k'] = stoch_k.iloc[-1]
            indicators['stoch_d'] = stoch_d.iloc[-1]
            indicators['stoch_signal'] = self._interpret_stochastic_for_scalping(stoch_k.iloc[-1], stoch_d.iloc[-1])
            
            # Fast MACD
            macd_line, macd_signal, macd_histogram = self._calculate_macd(df)
            indicators['macd'] = macd_line.iloc[-1]
            indicators['macd_signal_line'] = macd_signal.iloc[-1]
            indicators['macd_histogram'] = macd_histogram.iloc[-1]
            indicators['macd_signal'] = 'bullish' if macd_histogram.iloc[-1] > 0 else 'bearish'
            
            # Williams %R for scalping
            williams_r = self._calculate_williams_r(df)
            indicators['williams_r'] = williams_r.iloc[-1]
            indicators['williams_signal'] = self._interpret_williams_r_for_scalping(williams_r.iloc[-1])
            
            return indicators
            
        except Exception as e:
            logger.error(f"Error calculating scalping indicators: {e}")
            return {}
    
    def _analyze_scalping_momentum(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze momentum for scalping opportunities"""
        try:
            momentum = {}
            
            # Short-term momentum
            momentum_1 = df['close'].pct_change(1).iloc[-1]
            momentum_3 = df['close'].pct_change(3).iloc[-1]
            momentum_5 = df['close'].pct_change(5).iloc[-1]
            
            momentum['momentum_1bar'] = momentum_1
            momentum['momentum_3bar'] = momentum_3
            momentum['momentum_5bar'] = momentum_5
            
            # Momentum strength and direction
            momentum['current_momentum'] = momentum_1
            momentum['momentum_direction'] = 'bullish' if momentum_1 > 0 else 'bearish'
            momentum['momentum_strength'] = abs(momentum_1)
            momentum['momentum_acceleration'] = momentum_1 - df['close'].pct_change(1).iloc[-2]
            
            # Momentum consistency
            recent_momentum = df['close'].pct_change(1).tail(5)
            momentum['momentum_consistency'] = (recent_momentum > 0).sum() / len(recent_momentum)
            
            return momentum
            
        except Exception as e:
            logger.error(f"Error analyzing scalping momentum: {e}")
            return {}
    
    def _analyze_scalping_volume(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze volume for scalping validation"""
        try:
            volume = {}
            
            if 'volume' not in df.columns or df['volume'].sum() == 0:
                volume['volume_available'] = False
                return volume
            
            volume['volume_available'] = True
            
            # Current vs average volume
            current_volume = df['volume'].iloc[-1]
            avg_volume = df['volume'].rolling(10).mean().iloc[-1]
            
            volume['current_volume'] = current_volume
            volume['average_volume'] = avg_volume
            volume['volume_ratio'] = current_volume / avg_volume if avg_volume > 0 else 1.0
            volume['volume_surge'] = volume['volume_ratio'] > self.min_volume_threshold
            
            # Volume trend
            volume_trend = df['volume'].rolling(3).mean().diff().iloc[-1]
            volume['volume_trend'] = 'increasing' if volume_trend > 0 else 'decreasing'
            
            # Volume-price analysis
            price_change = df['close'].pct_change(1).iloc[-1]
            volume_change = df['volume'].pct_change(1).iloc[-1]
            volume['volume_price_alignment'] = (price_change > 0 and volume_change > 0) or (price_change < 0 and volume_change > 0)
            
            return volume
            
        except Exception as e:
            logger.error(f"Error analyzing scalping volume: {e}")
            return {'volume_available': False}
    
    def _analyze_scalping_volatility(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze volatility for scalping opportunities"""
        try:
            volatility = {}
            
            # Calculate different volatility measures
            returns = df['close'].pct_change().dropna()
            
            # Recent volatility
            recent_vol = returns.tail(10).std()
            historical_vol = returns.tail(50).std()
            
            volatility['recent_volatility'] = recent_vol
            volatility['historical_volatility'] = historical_vol
            volatility['volatility_ratio'] = recent_vol / historical_vol if historical_vol > 0 else 1.0
            
            # Volatility state
            if volatility['volatility_ratio'] > 1.5:
                volatility['volatility_state'] = 'high'
            elif volatility['volatility_ratio'] < 0.7:
                volatility['volatility_state'] = 'low'
            else:
                volatility['volatility_state'] = 'normal'
            
            # ATR for position sizing
            atr = self._calculate_atr(df)
            volatility['atr'] = atr.iloc[-1] if atr is not None else df['close'].iloc[-1] * 0.001
            
            return volatility
            
        except Exception as e:
            logger.error(f"Error analyzing scalping volatility: {e}")
            return {}
    
    def _analyze_scalping_price_action(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze price action patterns for scalping"""
        try:
            price_action = {}
            
            # Recent bars analysis
            recent_bars = df.tail(5)
            
            # Bar patterns
            price_action['bullish_bars'] = (recent_bars['close'] > recent_bars['open']).sum()
            price_action['bearish_bars'] = (recent_bars['close'] < recent_bars['open']).sum()
            price_action['doji_bars'] = (abs(recent_bars['close'] - recent_bars['open']) < 
                                       (recent_bars['high'] - recent_bars['low']) * 0.1).sum()
            
            # Current bar analysis
            current_bar = df.iloc[-1]
            price_action['current_bar_type'] = self._classify_bar_type(current_bar)
            price_action['current_bar_strength'] = self._calculate_bar_strength(current_bar)
            
            # Support/resistance levels (simplified)
            recent_highs = df['high'].tail(20)
            recent_lows = df['low'].tail(20)
            
            price_action['near_resistance'] = current_bar['close'] > recent_highs.quantile(0.9)
            price_action['near_support'] = current_bar['close'] < recent_lows.quantile(0.1)
            
            return price_action
            
        except Exception as e:
            logger.error(f"Error analyzing scalping price action: {e}")
            return {}
    
    def _analyze_spread_conditions(self, df: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """Analyze spread conditions for scalping viability"""
        try:
            spread = {}
            
            # Estimate spread (simplified - in real implementation would use bid/ask data)
            estimated_spread = df['close'].iloc[-1] * 0.0002  # Assume 2 pip spread
            
            spread['estimated_spread'] = estimated_spread
            spread['spread_in_pips'] = estimated_spread * 10000  # Convert to pips
            spread['spread_acceptable'] = estimated_spread <= self.max_spread_threshold
            
            # Spread trend (estimated)
            spread['spread_trend'] = 'stable'  # Would be calculated from real bid/ask data
            spread['spread_volatility'] = 'low'  # Would be calculated from real data
            
            return spread
            
        except Exception as e:
            logger.error(f"Error analyzing spread conditions: {e}")
            return {}
    
    def _generate_timeframe_scalping_opportunities(self, symbol: str, timeframe: str, df: pd.DataFrame,
                                                 analysis: Dict[str, Any], current_time: datetime) -> List[SignalEvent]:
        """Generate scalping opportunities for specific timeframe"""
        try:
            opportunities = []
            
            # Extract analysis components
            indicators = analysis.get('indicators', {})
            momentum = analysis.get('momentum', {})
            volume = analysis.get('volume', {})
            volatility = analysis.get('volatility', {})
            spread = analysis.get('spread', {})
            
            current_price = df['close'].iloc[-1]
            
            # Check if spread conditions are acceptable
            if not spread.get('spread_acceptable', True):
                return opportunities
            
            # Generate different types of scalping signals
            for scalping_type in self.scalping_types:
                try:
                    engine = self.scalping_engines.get(scalping_type)
                    if engine:
                        type_opportunities = engine(
                            symbol, timeframe, df, analysis, current_time
                        )
                        opportunities.extend(type_opportunities)
                        
                except Exception as e:
                    logger.warning(f"Error in {scalping_type} engine: {e}")
                    continue
            
            # Filter and validate opportunities
            validated_opportunities = []
            for opportunity in opportunities:
                if self._validate_scalping_opportunity(opportunity, df, analysis):
                    validated_opportunities.append(opportunity)
            
            return validated_opportunities
            
        except Exception as e:
            logger.error(f"Error generating timeframe scalping opportunities: {e}")
            return []
    
    def _momentum_scalping_engine(self, symbol: str, timeframe: str, df: pd.DataFrame,
                                analysis: Dict[str, Any], current_time: datetime) -> List[SignalEvent]:
        """Generate momentum-based scalping signals"""
        try:
            signals = []
            
            indicators = analysis.get('indicators', {})
            momentum = analysis.get('momentum', {})
            volume = analysis.get('volume', {})
            
            current_price = df['close'].iloc[-1]
            
            # Momentum scalping conditions
            ema_signal = indicators.get('ema_signal')
            momentum_strength = momentum.get('momentum_strength', 0)
            volume_surge = volume.get('volume_surge', False)
            
            # Strong momentum with EMA alignment
            if (ema_signal in ['bullish', 'bearish'] and 
                momentum_strength > 0.0005 and  # 5 pips minimum
                volume_surge):
                
                direction = ema_signal
                strength = min(1.0, momentum_strength * 1000)  # Scale for strength
                
                # Calculate targets
                atr = analysis.get('volatility', {}).get('atr', current_price * 0.001)
                
                if direction == 'bullish':
                    target_price = current_price + (self.take_profit_pips * 0.0001)
                    stop_loss = current_price - (self.stop_loss_pips * 0.0001)
                else:
                    target_price = current_price - (self.take_profit_pips * 0.0001)
                    stop_loss = current_price + (self.stop_loss_pips * 0.0001)
                
                # Create signal
                signal = self._create_scalping_signal(
                    symbol, timeframe, ScalpingType.MOMENTUM_SCALPING,
                    direction, strength, current_price, target_price, stop_loss,
                    analysis, current_time
                )
                
                if signal:
                    signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error in momentum scalping engine: {e}")
            return []
    
    def _mean_reversion_scalping_engine(self, symbol: str, timeframe: str, df: pd.DataFrame,
                                      analysis: Dict[str, Any], current_time: datetime) -> List[SignalEvent]:
        """Generate mean reversion scalping signals"""
        try:
            signals = []
            
            indicators = analysis.get('indicators', {})
            
            current_price = df['close'].iloc[-1]
            rsi = indicators.get('rsi', 50)
            stoch_k = indicators.get('stoch_k', 50)
            
            # Mean reversion conditions
            if rsi < 30 and stoch_k < 20:  # Oversold
                direction = 'bullish'
                strength = (30 - rsi) / 30 + (20 - stoch_k) / 20
                strength = min(1.0, strength / 2)
                
                target_price = current_price + (self.take_profit_pips * 0.0001)
                stop_loss = current_price - (self.stop_loss_pips * 0.0001)
                
            elif rsi > 70 and stoch_k > 80:  # Overbought
                direction = 'bearish'
                strength = (rsi - 70) / 30 + (stoch_k - 80) / 20
                strength = min(1.0, strength / 2)
                
                target_price = current_price - (self.take_profit_pips * 0.0001)
                stop_loss = current_price + (self.stop_loss_pips * 0.0001)
                
            else:
                return signals
            
            # Create signal
            signal = self._create_scalping_signal(
                symbol, timeframe, ScalpingType.MEAN_REVERSION_SCALPING,
                direction, strength, current_price, target_price, stop_loss,
                analysis, current_time
            )
            
            if signal:
                signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error in mean reversion scalping engine: {e}")
            return []
    
    def _breakout_scalping_engine(self, symbol: str, timeframe: str, df: pd.DataFrame,
                                analysis: Dict[str, Any], current_time: datetime) -> List[SignalEvent]:
        """Generate breakout scalping signals"""
        try:
            signals = []
            
            volume = analysis.get('volume', {})
            volatility = analysis.get('volatility', {})
            
            current_price = df['close'].iloc[-1]
            
            # Simple breakout detection
            recent_high = df['high'].tail(10).max()
            recent_low = df['low'].tail(10).min()
            
            volume_surge = volume.get('volume_surge', False)
            high_volatility = volatility.get('volatility_state') == 'high'
            
            # Breakout conditions
            if current_price > recent_high and volume_surge and high_volatility:
                direction = 'bullish'
                strength = 0.8
                
                target_price = current_price + (self.take_profit_pips * 0.0001)
                stop_loss = recent_high - (self.stop_loss_pips * 0.0001)
                
            elif current_price < recent_low and volume_surge and high_volatility:
                direction = 'bearish'
                strength = 0.8
                
                target_price = current_price - (self.take_profit_pips * 0.0001)
                stop_loss = recent_low + (self.stop_loss_pips * 0.0001)
                
            else:
                return signals
            
            # Create signal
            signal = self._create_scalping_signal(
                symbol, timeframe, ScalpingType.BREAKOUT_SCALPING,
                direction, strength, current_price, target_price, stop_loss,
                analysis, current_time
            )
            
            if signal:
                signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error in breakout scalping engine: {e}")
            return []
    
    def _news_scalping_engine(self, symbol: str, timeframe: str, df: pd.DataFrame,
                            analysis: Dict[str, Any], current_time: datetime) -> List[SignalEvent]:
        """Generate news-based scalping signals"""
        try:
            # Placeholder for news scalping
            # In real implementation, would integrate with news feeds
            return []
            
        except Exception as e:
            logger.error(f"Error in news scalping engine: {e}")
            return []
    
    def _spread_scalping_engine(self, symbol: str, timeframe: str, df: pd.DataFrame,
                              analysis: Dict[str, Any], current_time: datetime) -> List[SignalEvent]:
        """Generate spread-based scalping signals"""
        try:
            # Placeholder for spread scalping
            # In real implementation, would analyze bid/ask spreads
            return []
            
        except Exception as e:
            logger.error(f"Error in spread scalping engine: {e}")
            return []
    
    def _volume_scalping_engine(self, symbol: str, timeframe: str, df: pd.DataFrame,
                              analysis: Dict[str, Any], current_time: datetime) -> List[SignalEvent]:
        """Generate volume-based scalping signals"""
        try:
            signals = []
            
            volume = analysis.get('volume', {})
            if not volume.get('volume_available', False):
                return signals
            
            # Volume spike with price movement
            volume_ratio = volume.get('volume_ratio', 1.0)
            momentum = analysis.get('momentum', {})
            momentum_strength = momentum.get('momentum_strength', 0)
            
            if volume_ratio > 2.0 and momentum_strength > 0.0003:  # High volume + movement
                direction = momentum.get('momentum_direction', 'neutral')
                if direction != 'neutral':
                    current_price = df['close'].iloc[-1]
                    strength = min(1.0, volume_ratio / 3.0)
                    
                    if direction == 'bullish':
                        target_price = current_price + (self.take_profit_pips * 0.0001)
                        stop_loss = current_price - (self.stop_loss_pips * 0.0001)
                    else:
                        target_price = current_price - (self.take_profit_pips * 0.0001)
                        stop_loss = current_price + (self.stop_loss_pips * 0.0001)
                    
                    signal = self._create_scalping_signal(
                        symbol, timeframe, ScalpingType.VOLUME_SCALPING,
                        direction, strength, current_price, target_price, stop_loss,
                        analysis, current_time
                    )
                    
                    if signal:
                        signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error in volume scalping engine: {e}")
            return []
    
    def _arbitrage_scalping_engine(self, symbol: str, timeframe: str, df: pd.DataFrame,
                                 analysis: Dict[str, Any], current_time: datetime) -> List[SignalEvent]:
        """Generate arbitrage-based scalping signals"""
        try:
            # Placeholder for arbitrage scalping
            # In real implementation, would compare prices across exchanges
            return []
            
        except Exception as e:
            logger.error(f"Error in arbitrage scalping engine: {e}")
            return []
    
    def _create_scalping_signal(self, symbol: str, timeframe: str, scalping_type: ScalpingType,
                              direction: str, strength: float, entry_price: float,
                              target_price: float, stop_loss: float,
                              analysis: Dict[str, Any], current_time: datetime) -> Optional[SignalEvent]:
        """Create enhanced scalping signal"""
        try:
            # Calculate metrics
            if direction == 'bullish':
                profit_pips = (target_price - entry_price) * 10000
                loss_pips = (entry_price - stop_loss) * 10000
            else:
                profit_pips = (entry_price - target_price) * 10000
                loss_pips = (stop_loss - entry_price) * 10000
            
            risk_reward_ratio = profit_pips / loss_pips if loss_pips > 0 else 0
            
            # Skip if risk-reward is poor
            if risk_reward_ratio < 1.0:
                return None
            
            # Calculate confidence
            confidence = self._calculate_scalping_confidence(analysis, strength, scalping_type)
            
            # Skip if confidence too low
            if confidence < 0.6:
                return None
            
            # Estimate hold time
            volatility = analysis.get('volatility', {})
            atr = volatility.get('atr', entry_price * 0.001)
            expected_hold_time = max(30, min(300, profit_pips / (atr * 10000) * 60))  # seconds
            
            # Create signal event
            signal = SignalEvent(
                event_type='SCALPING_SIGNAL',
                symbol=symbol,
                timeframe=timeframe,
                timestamp=current_time,
                direction=direction,
                strength=strength,
                level=entry_price,
                metadata={
                    'scalping_type': scalping_type.value,
                    'target_price': target_price,
                    'stop_loss': stop_loss,
                    'profit_pips': profit_pips,
                    'loss_pips': loss_pips,
                    'risk_reward_ratio': risk_reward_ratio,
                    'confidence': confidence,
                    'expected_hold_time_seconds': expected_hold_time,
                    'execution_urgency': 'immediate',
                    'spread_acceptable': analysis.get('spread', {}).get('spread_acceptable', True),
                    'volume_confirmed': analysis.get('volume', {}).get('volume_surge', False),
                    'market_microstructure': analysis.get('microstructure', {}).get('market_state', 'normal'),
                    'signal_quality': self._assess_signal_quality(analysis, strength),
                    'analysis_summary': self._create_scalping_analysis_summary(analysis)
                }
            )
            
            return signal
            
        except Exception as e:
            logger.error(f"Error creating scalping signal: {e}")
            return None
    
    def _calculate_scalping_confidence(self, analysis: Dict[str, Any], 
                                     strength: float, scalping_type: ScalpingType) -> float:
        """Calculate confidence in scalping signal"""
        try:
            confidence_factors = []
            
            # Base strength factor
            confidence_factors.append(strength)
            
            # Volume confirmation factor
            volume = analysis.get('volume', {})
            if volume.get('volume_surge', False):
                confidence_factors.append(0.9)
            elif volume.get('volume_ratio', 1.0) > 1.2:
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.5)
            
            # Spread factor
            spread = analysis.get('spread', {})
            if spread.get('spread_acceptable', True):
                confidence_factors.append(0.8)
            else:
                confidence_factors.append(0.3)
            
            # Volatility factor
            volatility = analysis.get('volatility', {})
            vol_state = volatility.get('volatility_state', 'normal')
            if vol_state == 'normal':
                confidence_factors.append(0.8)
            elif vol_state == 'high':
                confidence_factors.append(0.6)  # Higher risk
            else:
                confidence_factors.append(0.4)  # Low volatility
            
            # Momentum consistency factor
            momentum = analysis.get('momentum', {})
            momentum_consistency = momentum.get('momentum_consistency', 0.5)
            confidence_factors.append(momentum_consistency)
            
            # Scalping type factor
            type_confidence = {
                ScalpingType.MOMENTUM_SCALPING: 0.8,
                ScalpingType.MEAN_REVERSION_SCALPING: 0.7,
                ScalpingType.BREAKOUT_SCALPING: 0.6,
                ScalpingType.VOLUME_SCALPING: 0.7,
                ScalpingType.NEWS_SCALPING: 0.9,
                ScalpingType.SPREAD_SCALPING: 0.8,
                ScalpingType.ARBITRAGE_SCALPING: 0.9
            }
            confidence_factors.append(type_confidence.get(scalping_type, 0.6))
            
            # Calculate overall confidence
            overall_confidence = np.mean(confidence_factors) if confidence_factors else 0.5
            
            return float(overall_confidence)
            
        except Exception as e:
            logger.error(f"Error calculating scalping confidence: {e}")
            return 0.5
    
    def _assess_signal_quality(self, analysis: Dict[str, Any], strength: float) -> str:
        """Assess the quality of scalping signal"""
        try:
            quality_score = 0.0
            
            # Strength component
            quality_score += strength * 0.3
            
            # Volume component
            volume = analysis.get('volume', {})
            if volume.get('volume_surge', False):
                quality_score += 0.3
            
            # Spread component
            spread = analysis.get('spread', {})
            if spread.get('spread_acceptable', True):
                quality_score += 0.2
            
            # Momentum component
            momentum = analysis.get('momentum', {})
            if momentum.get('momentum_strength', 0) > 0.0005:
                quality_score += 0.2
            
            # Determine quality level
            if quality_score >= 0.9:
                return ScalpingSignalQuality.EXCELLENT.name
            elif quality_score >= 0.7:
                return ScalpingSignalQuality.GOOD.name
            elif quality_score >= 0.5:
                return ScalpingSignalQuality.AVERAGE.name
            else:
                return ScalpingSignalQuality.POOR.name
                
        except Exception as e:
            logger.error(f"Error assessing signal quality: {e}")
            return ScalpingSignalQuality.AVERAGE.name
    
    def _validate_scalping_opportunity(self, opportunity: SignalEvent, 
                                     df: pd.DataFrame, analysis: Dict[str, Any]) -> bool:
        """Validate scalping opportunity"""
        try:
            # Basic validation
            if opportunity.strength < self.min_signal_strength:
                return False
            
            # Confidence validation
            confidence = opportunity.metadata.get('confidence', 0.5)
            if confidence < 0.6:
                return False
            
            # Risk-reward validation
            risk_reward = opportunity.metadata.get('risk_reward_ratio', 0)
            if risk_reward < 1.0:
                return False
            
            # Spread validation
            spread_acceptable = opportunity.metadata.get('spread_acceptable', False)
            if not spread_acceptable:
                return False
            
            # Profit target validation
            profit_pips = opportunity.metadata.get('profit_pips', 0)
            if profit_pips < self.min_profit_target_pips:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating scalping opportunity: {e}")
            return False
    
    def _validate_multi_timeframe_scalping(self, symbol: str, opportunities: List[SignalEvent],
                                         timeframe_analysis: Dict[str, Dict[str, Any]]) -> List[SignalEvent]:
        """Validate scalping opportunities across multiple timeframes"""
        try:
            if len(opportunities) < 2:  # Need multiple timeframe confirmation
                return opportunities  # Return as-is if only one timeframe
            
            validated_signals = []
            
            # Group by direction
            bullish_signals = [s for s in opportunities if s.direction == 'bullish']
            bearish_signals = [s for s in opportunities if s.direction == 'bearish']
            
            # Require confirmation from at least 2 timeframes
            if len(bullish_signals) >= 2:
                best_bullish = max(bullish_signals, key=lambda x: x.strength)
                best_bullish.metadata['multi_timeframe_confirmed'] = True
                best_bullish.metadata['confirming_signals'] = len(bullish_signals)
                validated_signals.append(best_bullish)
            
            if len(bearish_signals) >= 2:
                best_bearish = max(bearish_signals, key=lambda x: x.strength)
                best_bearish.metadata['multi_timeframe_confirmed'] = True
                best_bearish.metadata['confirming_signals'] = len(bearish_signals)
                validated_signals.append(best_bearish)
            
            return validated_signals
            
        except Exception as e:
            logger.error(f"Error validating multi-timeframe scalping: {e}")
            return opportunities
    
    def _filter_scalping_signals(self, signals: List[SignalEvent], current_time: datetime) -> List[SignalEvent]:
        """Apply high-frequency filtering to scalping signals"""
        try:
            if not signals:
                return signals
            
            filtered_signals = []
            
            # Rate limiting - max signals per minute
            recent_signals = [
                s for s in self.signal_history 
                if (current_time - s.get('timestamp', current_time)).total_seconds() < 60
            ]
            
            if len(recent_signals) >= self.max_signals_per_minute:
                return []  # Too many signals recently
            
            # Quality filtering
            for signal in signals:
                # Signal quality filter
                signal_quality = signal.metadata.get('signal_quality', 'POOR')
                if signal_quality in ['POOR']:
                    continue
                
                # Execution urgency filter
                if signal.metadata.get('execution_urgency') != 'immediate':
                    continue
                
                # Duplicate signal filter
                if self._is_duplicate_signal(signal, current_time):
                    continue
                
                filtered_signals.append(signal)
            
            # Limit concurrent trades
            if len(filtered_signals) > self.max_concurrent_trades:
                # Sort by strength and take top N
                filtered_signals.sort(key=lambda x: x.strength, reverse=True)
                filtered_signals = filtered_signals[:self.max_concurrent_trades]
            
            return filtered_signals
            
        except Exception as e:
            logger.error(f"Error filtering scalping signals: {e}")
            return signals
    
    def _is_duplicate_signal(self, new_signal: SignalEvent, current_time: datetime) -> bool:
        """Check if signal is duplicate of recent signal"""
        try:
            # Check last 30 seconds for similar signals
            recent_cutoff = current_time - timedelta(seconds=30)
            
            for recent_signal in self.signal_history:
                if recent_signal.get('timestamp', current_time) < recent_cutoff:
                    continue
                
                # Same symbol and direction
                if (recent_signal.get('symbol') == new_signal.symbol and
                    recent_signal.get('direction') == new_signal.direction):
                    
                    # Similar price level (within 2 pips)
                    price_diff = abs(recent_signal.get('level', 0) - new_signal.level)
                    if price_diff < 0.0002:  # 2 pips
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking duplicate signal: {e}")
            return False
    
    def _optimize_signal_execution(self, signals: List[SignalEvent]) -> List[SignalEvent]:
        """Optimize signal execution order for scalping"""
        try:
            if not signals:
                return signals
            
            # Sort by execution priority
            def execution_priority(signal):
                priority_score = 0.0
                
                # Higher strength gets priority
                priority_score += signal.strength * 100
                
                # Better risk-reward gets priority
                rr = signal.metadata.get('risk_reward_ratio', 1.0)
                priority_score += min(rr, 5.0) * 20
                
                # Higher confidence gets priority
                confidence = signal.metadata.get('confidence', 0.5)
                priority_score += confidence * 50
                
                # Signal quality bonus
                quality = signal.metadata.get('signal_quality', 'AVERAGE')
                quality_bonus = {
                    'EXCELLENT': 30,
                    'GOOD': 20,
                    'AVERAGE': 10,
                    'POOR': 0
                }
                priority_score += quality_bonus.get(quality, 0)
                
                return priority_score
            
            # Sort by priority (highest first)
            optimized_signals = sorted(signals, key=execution_priority, reverse=True)
            
            return optimized_signals
            
        except Exception as e:
            logger.error(f"Error optimizing signal execution: {e}")
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
                    'scalping_type': signal.metadata.get('scalping_type'),
                    'confidence': signal.metadata.get('confidence', 0.5),
                    'profit_pips': signal.metadata.get('profit_pips', 0),
                    'signal_quality': signal.metadata.get('signal_quality'),
                    'level': signal.level
                })
                
                # Update performance metrics
                self.scalping_metrics.total_trades += 1
                self.performance_monitor['trades_today'] += 1
            
        except Exception as e:
            logger.error(f"Error updating signal history: {e}")
    
    def _create_scalping_analysis_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create summary of scalping analysis for metadata"""
        try:
            summary = {}
            
            # Indicators summary
            indicators = analysis.get('indicators', {})
            if indicators:
                summary['ema_signal'] = indicators.get('ema_signal')
                summary['rsi'] = indicators.get('rsi', 50)
                summary['stoch_signal'] = indicators.get('stoch_signal')
                summary['macd_signal'] = indicators.get('macd_signal')
            
            # Volume summary
            volume = analysis.get('volume', {})
            if volume.get('volume_available', False):
                summary['volume_ratio'] = volume.get('volume_ratio', 1.0)
                summary['volume_surge'] = volume.get('volume_surge', False)
            
            # Momentum summary
            momentum = analysis.get('momentum', {})
            if momentum:
                summary['momentum_direction'] = momentum.get('momentum_direction')
                summary['momentum_strength'] = momentum.get('momentum_strength', 0)
            
            # Volatility summary
            volatility = analysis.get('volatility', {})
            if volatility:
                summary['volatility_state'] = volatility.get('volatility_state')
                summary['atr'] = volatility.get('atr', 0)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error creating scalping analysis summary: {e}")
            return {}
    
    # Helper methods for technical indicators
    
    def _calculate_rsi(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Calculate RSI indicator"""
        try:
            delta = df['close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            
            avg_gain = gain.rolling(period).mean()
            avg_loss = loss.rolling(period).mean()
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi.fillna(50)
            
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return pd.Series(50, index=df.index)
    
    def _calculate_stochastic(self, df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """Calculate Stochastic Oscillator"""
        try:
            lowest_low = df['low'].rolling(self.stoch_k_period).min()
            highest_high = df['high'].rolling(self.stoch_k_period).max()
            
            k_percent = 100 * ((df['close'] - lowest_low) / (highest_high - lowest_low))
            d_percent = k_percent.rolling(self.stoch_d_period).mean()
            
            return k_percent.fillna(50), d_percent.fillna(50)
            
        except Exception as e:
            logger.error(f"Error calculating Stochastic: {e}")
            return pd.Series(50, index=df.index), pd.Series(50, index=df.index)
    
    def _calculate_macd(self, df: pd.DataFrame) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD indicator"""
        try:
            ema_fast = df['close'].ewm(span=self.macd_fast).mean()
            ema_slow = df['close'].ewm(span=self.macd_slow).mean()
            macd = ema_fast - ema_slow
            signal = macd.ewm(span=self.macd_signal).mean()
            histogram = macd - signal
            
            return macd.fillna(0), signal.fillna(0), histogram.fillna(0)
            
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            zero_series = pd.Series(0, index=df.index)
            return zero_series, zero_series, zero_series
    
    def _calculate_williams_r(self, df: pd.DataFrame) -> pd.Series:
        """Calculate Williams %R"""
        try:
            highest_high = df['high'].rolling(14).max()
            lowest_low = df['low'].rolling(14).min()
            
            williams_r = -100 * ((highest_high - df['close']) / (highest_high - lowest_low))
            
            return williams_r.fillna(-50)
            
        except Exception as e:
            logger.error(f"Error calculating Williams %R: {e}")
            return pd.Series(-50, index=df.index)
    
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
    
    def _interpret_rsi_for_scalping(self, rsi_value: float) -> str:
        """Interpret RSI for scalping signals"""
        if rsi_value > 70:
            return 'bearish'
        elif rsi_value < 30:
            return 'bullish'
        else:
            return 'neutral'
    
    def _interpret_stochastic_for_scalping(self, stoch_k: float, stoch_d: float) -> str:
        """Interpret Stochastic for scalping signals"""
        if stoch_k > 80 and stoch_d > 80:
            return 'bearish'
        elif stoch_k < 20 and stoch_d < 20:
            return 'bullish'
        else:
            return 'neutral'
    
    def _interpret_williams_r_for_scalping(self, williams_r: float) -> str:
        """Interpret Williams %R for scalping signals"""
        if williams_r > -20:
            return 'bearish'
        elif williams_r < -80:
            return 'bullish'
        else:
            return 'neutral'
    
    def _estimate_price_precision(self, df: pd.DataFrame) -> int:
        """Estimate price precision from data"""
        try:
            # Count decimal places in price data
            price_str = str(df['close'].iloc[-1])
            if '.' in price_str:
                return len(price_str.split('.')[1])
            return 0
            
        except Exception as e:
            logger.error(f"Error estimating price precision: {e}")
            return 5  # Default for forex
    
    def _estimate_liquidity_score(self, df: pd.DataFrame) -> float:
        """Estimate liquidity score from available data"""
        try:
            # Simplified liquidity estimation based on volume and spread
            if 'volume' in df.columns and df['volume'].sum() > 0:
                volume_consistency = 1.0 - df['volume'].std() / df['volume'].mean()
                return max(0.3, min(1.0, volume_consistency))
            return 0.7  # Default
            
        except Exception as e:
            logger.error(f"Error estimating liquidity score: {e}")
            return 0.7
    
    def _determine_market_state(self, df: pd.DataFrame) -> str:
        """Determine current market state"""
        try:
            # Simple market state determination
            volatility = df['close'].pct_change().std()
            volume_available = 'volume' in df.columns and df['volume'].sum() > 0
            
            if volatility > 0.002:  # High volatility
                return MarketMicrostructure.VOLATILE.value
            elif volume_available and df['volume'].iloc[-1] > df['volume'].mean() * 2:
                return MarketMicrostructure.HIGH_VOLUME.value
            else:
                return MarketMicrostructure.STABLE.value
                
        except Exception as e:
            logger.error(f"Error determining market state: {e}")
            return MarketMicrostructure.STABLE.value
    
    def _classify_bar_type(self, bar: pd.Series) -> str:
        """Classify bar type for price action analysis"""
        try:
            body_size = abs(bar['close'] - bar['open'])
            total_size = bar['high'] - bar['low']
            
            if total_size == 0:
                return 'doji'
            
            body_ratio = body_size / total_size
            
            if body_ratio > 0.7:
                return 'strong_trend' if bar['close'] > bar['open'] else 'strong_reversal'
            elif body_ratio < 0.3:
                return 'doji'
            else:
                return 'normal'
                
        except Exception as e:
            logger.error(f"Error classifying bar type: {e}")
            return 'normal'
    
    def _calculate_bar_strength(self, bar: pd.Series) -> float:
        """Calculate strength of price bar"""
        try:
            body_size = abs(bar['close'] - bar['open'])
            total_size = bar['high'] - bar['low']
            
            if total_size == 0:
                return 0.0
            
            return body_size / total_size
            
        except Exception as e:
            logger.error(f"Error calculating bar strength: {e}")
            return 0.5
    
    def get_required_data(self) -> Dict[str, List[str]]:
        """Return required data specification"""
        return {
            '*': self.scalping_timeframes  # All symbols need scalping timeframes
        }
    
    def validate_signal(self, signal: SignalEvent) -> bool:
        """Validate individual scalping signal"""
        try:
            # Basic validation
            if not signal or signal.strength < self.min_signal_strength:
                return False
            
            # Direction validation
            if signal.direction not in ['bullish', 'bearish']:
                return False
            
            # Scalping-specific validation
            scalping_type = signal.metadata.get('scalping_type')
            if not scalping_type:
                return False
            
            # Profit target validation
            profit_pips = signal.metadata.get('profit_pips', 0)
            if profit_pips < self.min_profit_target_pips:
                return False
            
            # Risk-reward validation
            risk_reward = signal.metadata.get('risk_reward_ratio', 0)
            if risk_reward < 1.0:
                return False
            
            # Execution urgency validation
            urgency = signal.metadata.get('execution_urgency')
            if urgency != 'immediate':
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
        """Get comprehensive scalping performance summary"""
        try:
            current_time = datetime.utcnow()
            
            # Update real-time metrics
            if self.scalping_metrics.total_trades > 0:
                self.scalping_metrics.win_rate = (
                    self.scalping_metrics.winning_trades / 
                    self.scalping_metrics.total_trades
                )
                
                self.scalping_metrics.avg_profit_per_trade = (
                    self.scalping_metrics.total_profit / 
                    self.scalping_metrics.total_trades
                )
            
            # Calculate trades per hour
            if self.signal_history:
                oldest_signal = min(self.signal_history, key=lambda x: x.get('timestamp', current_time))
                time_diff_hours = (current_time - oldest_signal.get('timestamp', current_time)).total_seconds() / 3600
                if time_diff_hours > 0:
                    self.scalping_metrics.trades_per_hour = len(self.signal_history) / time_diff_hours
            
            return {
                'total_trades': self.scalping_metrics.total_trades,
                'winning_trades': self.scalping_metrics.winning_trades,
                'losing_trades': self.scalping_metrics.losing_trades,
                'win_rate': self.scalping_metrics.win_rate,
                'total_pips': self.scalping_metrics.total_pips,
                'total_profit': self.scalping_metrics.total_profit,
                'avg_profit_per_trade': self.scalping_metrics.avg_profit_per_trade,
                'avg_hold_time_seconds': self.scalping_metrics.avg_hold_time,
                'max_consecutive_wins': self.scalping_metrics.max_consecutive_wins,
                'max_consecutive_losses': self.scalping_metrics.max_consecutive_losses,
                'current_streak': self.scalping_metrics.current_streak,
                'trades_per_hour': self.scalping_metrics.trades_per_hour,
                'max_drawdown': self.scalping_metrics.max_drawdown,
                'daily_pnl': self.performance_monitor['daily_pnl'],
                'trades_today': self.performance_monitor['trades_today'],
                'execution_quality_score': self.execution_optimizer['execution_quality_score'],
                'signal_history_length': len(self.signal_history),
                'strategy_name': self.name,
                'last_updated': current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {}
    
    async def cleanup(self):
        """Cleanup strategy resources"""
        try:
            logger.info(f"Cleaning up Enhanced Scalping Strategy: {self.name}")
            
            # Clear history and caches
            self.signal_history.clear()
            self.trade_history.clear()
            self.performance_snapshots.clear()
            self.spread_history.clear()
            self.volume_profile.clear()
            self.execution_latency.clear()
            
            # Reset performance metrics
            self.scalping_metrics = ScalpingMetrics()
            self.performance_monitor = {
                'real_time_pnl': 0.0,
                'daily_pnl': 0.0,
                'trades_today': 0,
                'win_streak': 0,
                'loss_streak': 0,
                'max_drawdown_today': 0.0,
                'total_fees_paid': 0.0,
                'execution_metrics': defaultdict(list)
            }
            
            # Reset execution optimizer
            self.execution_optimizer = {
                'latency_monitor': deque(maxlen=100),
                'slippage_tracker': deque(maxlen=100),
                'requote_counter': defaultdict(int),
                'execution_quality_score': 1.0
            }
            
            logger.info("Enhanced Scalping Strategy cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Export the enhanced strategy
__all__ = ['EnhancedScalpingStrategy', 'ScalpingType', 'ScalpingTimeframe', 'ScalpingOpportunity', 'ScalpingMetrics']

# Compatibility alias
ScalpingStrategy = EnhancedScalpingStrategy
