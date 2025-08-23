"""
Enhanced Momentum Strategy Implementation
========================================
Professional-grade momentum trading strategy with advanced analytics,
multi-timeframe analysis, and comprehensive risk management.

Features:
- Multiple momentum indicators and calculations
- Market regime detection and adaptation
- Multi-timeframe momentum analysis
- Advanced signal filtering and validation
- Risk management integration
- Real-time performance monitoring
- Comprehensive logging and analytics
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

# Import base strategy and event system
from .base_strategy import BaseStrategy, SignalEvent, register_strategy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')

class MomentumType(Enum):
    """Types of momentum calculations"""
    PRICE_MOMENTUM = "price_momentum"
    VOLUME_MOMENTUM = "volume_momentum"
    COMPOSITE_MOMENTUM = "composite_momentum"
    RELATIVE_MOMENTUM = "relative_momentum"
    RISK_ADJUSTED_MOMENTUM = "risk_adjusted_momentum"

class MarketRegime(Enum):
    """Market regime classifications"""
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    SIDEWAYS = "sideways"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    BREAKOUT = "breakout"

@dataclass
class MomentumSignal:
    """Enhanced momentum signal with comprehensive metadata"""
    timestamp: datetime
    symbol: str
    timeframe: str
    direction: str  # 'bullish', 'bearish', 'neutral'
    strength: float  # 0.0 to 1.0
    momentum_type: MomentumType
    raw_momentum: float
    normalized_momentum: float
    confidence: float
    market_regime: MarketRegime
    supporting_indicators: List[str]
    risk_score: float
    entry_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    position_size: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@register_strategy
class EnhancedMomentumStrategy(BaseStrategy):
    """
    Enhanced Momentum Strategy with Professional Features
    
    This strategy implements multiple momentum calculation methods,
    market regime detection, and advanced signal processing for
    institutional-grade trading applications.
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize enhanced momentum strategy
        
        Args:
            name: Strategy name
            config: Configuration dictionary with strategy parameters
        """
        super().__init__(name, config)
        
        # Core momentum parameters
        self.momentum_lookback = config.get('momentum_lookback', 14)
        self.momentum_threshold = config.get('momentum_threshold', 0.02)
        self.signal_smoothing = config.get('signal_smoothing', 3)
        
        # Multi-timeframe analysis
        self.timeframes = config.get('timeframes', ['M15', 'H1', 'H4'])
        self.primary_timeframe = config.get('primary_timeframe', 'H1')
        
        # Advanced momentum calculations
        self.momentum_types = config.get('momentum_types', [
            MomentumType.PRICE_MOMENTUM,
            MomentumType.VOLUME_MOMENTUM,
            MomentumType.COMPOSITE_MOMENTUM
        ])
        
        # Market regime detection
        self.regime_detection_enabled = config.get('regime_detection', True)
        self.regime_lookback = config.get('regime_lookback', 50)
        self.volatility_threshold = config.get('volatility_threshold', 0.02)
        
        # Signal filtering and validation
        self.min_signal_strength = config.get('min_signal_strength', 0.6)
        self.max_correlation_filter = config.get('max_correlation_filter', 0.8)
        self.confirmation_required = config.get('confirmation_required', True)
        
        # Risk management
        self.max_position_size = config.get('max_position_size', 0.02)
        self.stop_loss_atr_multiple = config.get('stop_loss_atr_multiple', 2.0)
        self.take_profit_ratio = config.get('take_profit_ratio', 2.0)
        
        # Performance tracking
        self.signal_history = deque(maxlen=1000)
        self.performance_metrics = defaultdict(list)
        self.market_regime_history = deque(maxlen=100)
        
        # Technical indicator parameters
        self.rsi_period = config.get('rsi_period', 14)
        self.macd_fast = config.get('macd_fast', 12)
        self.macd_slow = config.get('macd_slow', 26)
        self.macd_signal = config.get('macd_signal', 9)
        self.atr_period = config.get('atr_period', 14)
        
        # Volume analysis
        self.volume_momentum_enabled = config.get('volume_momentum', True)
        self.volume_lookback = config.get('volume_lookback', 20)
        
        logger.info(f"Enhanced Momentum Strategy '{name}' initialized successfully")
        logger.info(f"Configuration: {self._log_safe_config()}")
    
    def _log_safe_config(self) -> Dict[str, Any]:
        """Create logging-safe configuration summary"""
        return {
            'momentum_lookback': self.momentum_lookback,
            'momentum_threshold': self.momentum_threshold,
            'timeframes': len(self.timeframes),
            'momentum_types': len(self.momentum_types),
            'regime_detection': self.regime_detection_enabled,
            'min_signal_strength': self.min_signal_strength
        }
    
    async def initialize(self) -> bool:
        """Initialize strategy with enhanced setup"""
        try:
            logger.info(f"Initializing Enhanced Momentum Strategy: {self.name}")
            
            # Validate configuration
            if not self._validate_configuration():
                logger.error("Configuration validation failed")
                return False
            
            # Initialize technical indicators
            self._initialize_indicators()
            
            # Setup performance monitoring
            self._setup_performance_monitoring()
            
            logger.info("Enhanced Momentum Strategy initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing Enhanced Momentum Strategy: {e}")
            return False
    
    def _validate_configuration(self) -> bool:
        """Validate strategy configuration parameters"""
        try:
            # Validate momentum parameters
            if self.momentum_lookback < 1 or self.momentum_lookback > 100:
                logger.error(f"Invalid momentum_lookback: {self.momentum_lookback}")
                return False
            
            if self.momentum_threshold < 0.001 or self.momentum_threshold > 0.5:
                logger.error(f"Invalid momentum_threshold: {self.momentum_threshold}")
                return False
            
            # Validate timeframes
            if not self.timeframes:
                logger.error("No timeframes specified")
                return False
            
            if self.primary_timeframe not in self.timeframes:
                logger.error(f"Primary timeframe {self.primary_timeframe} not in timeframes list")
                return False
            
            # Validate signal parameters
            if self.min_signal_strength < 0.0 or self.min_signal_strength > 1.0:
                logger.error(f"Invalid min_signal_strength: {self.min_signal_strength}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating configuration: {e}")
            return False
    
    def _initialize_indicators(self):
        """Initialize technical indicators for momentum calculation"""
        self.indicators = {
            'rsi': {},
            'macd': {},
            'atr': {},
            'volume_profile': {},
            'momentum_oscillators': {}
        }
        logger.info("Technical indicators initialized")
    
    def _setup_performance_monitoring(self):
        """Setup performance monitoring and analytics"""
        self.performance_monitor = {
            'signals_generated': 0,
            'signals_executed': 0,
            'winning_signals': 0,
            'losing_signals': 0,
            'total_pnl': 0.0,
            'max_drawdown': 0.0,
            'regime_accuracy': defaultdict(list)
        }
        logger.info("Performance monitoring setup complete")
    
    def generate_signals(self, data: Dict[str, pd.DataFrame]) -> List[SignalEvent]:
        """
        Generate enhanced momentum signals with comprehensive analysis
        
        Args:
            data: Dictionary of market data by symbol and timeframe
            
        Returns:
            List of enhanced momentum signals
        """
        try:
            signals = []
            
            for symbol, timeframe_data in data.items():
                if isinstance(timeframe_data, dict):
                    # Multi-timeframe analysis
                    symbol_signals = self._analyze_multi_timeframe_momentum(
                        symbol, timeframe_data
                    )
                    signals.extend(symbol_signals)
                else:
                    # Single timeframe analysis
                    symbol_signals = self._analyze_single_timeframe_momentum(
                        symbol, self.primary_timeframe, timeframe_data
                    )
                    signals.extend(symbol_signals)
            
            # Apply signal filtering and validation
            filtered_signals = self._filter_and_validate_signals(signals)
            
            # Update performance tracking
            self._update_signal_history(filtered_signals)
            
            logger.info(f"Generated {len(filtered_signals)} momentum signals from {len(signals)} candidates")
            return filtered_signals
            
        except Exception as e:
            logger.error(f"Error generating momentum signals: {e}")
            return []
    
    def _analyze_multi_timeframe_momentum(self, symbol: str, 
                                        timeframe_data: Dict[str, pd.DataFrame]) -> List[SignalEvent]:
        """Analyze momentum across multiple timeframes"""
        try:
            timeframe_signals = {}
            timeframe_momentum = {}
            
            # Calculate momentum for each timeframe
            for timeframe, df in timeframe_data.items():
                if timeframe in self.timeframes and len(df) >= self.momentum_lookback:
                    momentum_data = self._calculate_comprehensive_momentum(df)
                    market_regime = self._detect_market_regime(df)
                    
                    timeframe_momentum[timeframe] = momentum_data
                    timeframe_signals[timeframe] = self._generate_timeframe_signals(
                        symbol, timeframe, df, momentum_data, market_regime
                    )
            
            # Combine multi-timeframe analysis
            combined_signals = self._combine_timeframe_signals(
                symbol, timeframe_signals, timeframe_momentum
            )
            
            return combined_signals
            
        except Exception as e:
            logger.error(f"Error in multi-timeframe momentum analysis for {symbol}: {e}")
            return []
    
    def _analyze_single_timeframe_momentum(self, symbol: str, timeframe: str, 
                                         df: pd.DataFrame) -> List[SignalEvent]:
        """Analyze momentum for single timeframe"""
        try:
            if len(df) < self.momentum_lookback:
                return []
            
            # Calculate comprehensive momentum
            momentum_data = self._calculate_comprehensive_momentum(df)
            
            # Detect market regime
            market_regime = self._detect_market_regime(df)
            
            # Generate signals
            signals = self._generate_timeframe_signals(
                symbol, timeframe, df, momentum_data, market_regime
            )
            
            return signals
            
        except Exception as e:
            logger.error(f"Error in single timeframe momentum analysis: {e}")
            return []
    
    def _calculate_comprehensive_momentum(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate multiple types of momentum indicators"""
        try:
            momentum_data = {}
            
            # Price momentum calculations
            momentum_data['price_momentum'] = self._calculate_price_momentum(df)
            
            # Volume momentum (if available)
            if 'volume' in df.columns and self.volume_momentum_enabled:
                momentum_data['volume_momentum'] = self._calculate_volume_momentum(df)
            
            # Technical indicator momentum
            momentum_data['rsi_momentum'] = self._calculate_rsi_momentum(df)
            momentum_data['macd_momentum'] = self._calculate_macd_momentum(df)
            
            # Composite momentum score
            momentum_data['composite_score'] = self._calculate_composite_momentum(momentum_data)
            
            # Risk-adjusted momentum
            momentum_data['risk_adjusted'] = self._calculate_risk_adjusted_momentum(df, momentum_data)
            
            return momentum_data
            
        except Exception as e:
            logger.error(f"Error calculating comprehensive momentum: {e}")
            return {}
    
    def _calculate_price_momentum(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate various price momentum metrics"""
        try:
            price_momentum = {}
            
            # Simple price momentum
            current_price = df['close'].iloc[-1]
            past_price = df['close'].iloc[-self.momentum_lookback]
            price_momentum['simple'] = (current_price - past_price) / past_price
            
            # Rate of change (ROC)
            price_momentum['roc'] = df['close'].pct_change(self.momentum_lookback).iloc[-1]
            
            # Momentum oscillator
            price_momentum['oscillator'] = (current_price - df['close'].rolling(self.momentum_lookback).mean().iloc[-1]) / df['close'].rolling(self.momentum_lookback).std().iloc[-1]
            
            # Relative strength
            gains = df['close'].diff().clip(lower=0)
            losses = -df['close'].diff().clip(upper=0)
            avg_gain = gains.rolling(self.momentum_lookback).mean().iloc[-1]
            avg_loss = losses.rolling(self.momentum_lookback).mean().iloc[-1]
            price_momentum['relative_strength'] = avg_gain / (avg_gain + avg_loss) if avg_loss > 0 else 1.0
            
            # Trend strength
            sma_short = df['close'].rolling(self.momentum_lookback // 2).mean()
            sma_long = df['close'].rolling(self.momentum_lookback).mean()
            price_momentum['trend_strength'] = (sma_short.iloc[-1] - sma_long.iloc[-1]) / sma_long.iloc[-1]
            
            return price_momentum
            
        except Exception as e:
            logger.error(f"Error calculating price momentum: {e}")
            return {}
    
    def _calculate_volume_momentum(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate volume-based momentum indicators"""
        try:
            volume_momentum = {}
            
            # Volume rate of change
            current_volume = df['volume'].iloc[-1]
            avg_volume = df['volume'].rolling(self.volume_lookback).mean().iloc[-1]
            volume_momentum['volume_roc'] = (current_volume - avg_volume) / avg_volume if avg_volume > 0 else 0
            
            # On-Balance Volume (OBV) momentum
            obv = self._calculate_obv(df)
            obv_momentum = obv.pct_change(self.momentum_lookback).iloc[-1]
            volume_momentum['obv_momentum'] = obv_momentum if not pd.isna(obv_momentum) else 0
            
            # Volume-Price Trend (VPT)
            vpt = self._calculate_vpt(df)
            vpt_momentum = vpt.pct_change(self.momentum_lookback).iloc[-1]
            volume_momentum['vpt_momentum'] = vpt_momentum if not pd.isna(vpt_momentum) else 0
            
            # Accumulation/Distribution momentum
            ad = self._calculate_accumulation_distribution(df)
            ad_momentum = ad.pct_change(self.momentum_lookback).iloc[-1]
            volume_momentum['ad_momentum'] = ad_momentum if not pd.isna(ad_momentum) else 0
            
            return volume_momentum
            
        except Exception as e:
            logger.error(f"Error calculating volume momentum: {e}")
            return {}
    
    def _calculate_rsi_momentum(self, df: pd.DataFrame) -> float:
        """Calculate RSI-based momentum"""
        try:
            delta = df['close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            
            avg_gain = gain.rolling(self.rsi_period).mean()
            avg_loss = loss.rolling(self.rsi_period).mean()
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            # RSI momentum (rate of change of RSI)
            rsi_momentum = rsi.pct_change(self.momentum_lookback).iloc[-1]
            return rsi_momentum if not pd.isna(rsi_momentum) else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating RSI momentum: {e}")
            return 0.0
    
    def _calculate_macd_momentum(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate MACD-based momentum indicators"""
        try:
            # Calculate MACD
            ema_fast = df['close'].ewm(span=self.macd_fast).mean()
            ema_slow = df['close'].ewm(span=self.macd_slow).mean()
            macd = ema_fast - ema_slow
            signal_line = macd.ewm(span=self.macd_signal).mean()
            histogram = macd - signal_line
            
            macd_momentum = {}
            
            # MACD line momentum
            macd_momentum['macd_momentum'] = macd.pct_change(self.momentum_lookback).iloc[-1] if not pd.isna(macd.pct_change(self.momentum_lookback).iloc[-1]) else 0
            
            # Signal line momentum
            macd_momentum['signal_momentum'] = signal_line.pct_change(self.momentum_lookback).iloc[-1] if not pd.isna(signal_line.pct_change(self.momentum_lookback).iloc[-1]) else 0
            
            # Histogram momentum
            macd_momentum['histogram_momentum'] = histogram.pct_change(self.momentum_lookback).iloc[-1] if not pd.isna(histogram.pct_change(self.momentum_lookback).iloc[-1]) else 0
            
            # MACD crossover strength
            current_macd = macd.iloc[-1]
            current_signal = signal_line.iloc[-1]
            macd_momentum['crossover_strength'] = (current_macd - current_signal) / abs(current_signal) if current_signal != 0 else 0
            
            return macd_momentum
            
        except Exception as e:
            logger.error(f"Error calculating MACD momentum: {e}")
            return {}
    
    def _calculate_composite_momentum(self, momentum_data: Dict[str, Any]) -> float:
        """Calculate composite momentum score from multiple indicators"""
        try:
            scores = []
            weights = {
                'price_momentum': 0.4,
                'volume_momentum': 0.2,
                'rsi_momentum': 0.2,
                'macd_momentum': 0.2
            }
            
            # Price momentum component
            if 'price_momentum' in momentum_data:
                price_score = np.mean([
                    momentum_data['price_momentum'].get('simple', 0),
                    momentum_data['price_momentum'].get('roc', 0),
                    momentum_data['price_momentum'].get('trend_strength', 0)
                ])
                scores.append(price_score * weights['price_momentum'])
            
            # Volume momentum component
            if 'volume_momentum' in momentum_data and momentum_data['volume_momentum']:
                volume_score = np.mean(list(momentum_data['volume_momentum'].values()))
                scores.append(volume_score * weights['volume_momentum'])
            
            # RSI momentum component
            if 'rsi_momentum' in momentum_data:
                scores.append(momentum_data['rsi_momentum'] * weights['rsi_momentum'])
            
            # MACD momentum component
            if 'macd_momentum' in momentum_data and momentum_data['macd_momentum']:
                macd_score = np.mean(list(momentum_data['macd_momentum'].values()))
                scores.append(macd_score * weights['macd_momentum'])
            
            # Calculate weighted composite score
            composite_score = np.sum(scores) if scores else 0.0
            
            # Normalize to [-1, 1] range
            composite_score = np.tanh(composite_score * 10)  # Scaling factor for better distribution
            
            return float(composite_score)
            
        except Exception as e:
            logger.error(f"Error calculating composite momentum: {e}")
            return 0.0
    
    def _calculate_risk_adjusted_momentum(self, df: pd.DataFrame, 
                                        momentum_data: Dict[str, Any]) -> float:
        """Calculate risk-adjusted momentum score"""
        try:
            # Calculate volatility (ATR-based)
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift(1))
            low_close = np.abs(df['low'] - df['close'].shift(1))
            
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(self.atr_period).mean().iloc[-1]
            
            # Get composite momentum
            composite_momentum = momentum_data.get('composite_score', 0)
            
            # Adjust momentum by volatility
            current_price = df['close'].iloc[-1]
            volatility_ratio = atr / current_price if current_price > 0 else 0
            
            # Risk-adjusted momentum (higher volatility reduces momentum strength)
            risk_adjusted = composite_momentum / (1 + volatility_ratio * 10) if volatility_ratio > 0 else composite_momentum
            
            return float(risk_adjusted)
            
        except Exception as e:
            logger.error(f"Error calculating risk-adjusted momentum: {e}")
            return 0.0
    
    def _detect_market_regime(self, df: pd.DataFrame) -> MarketRegime:
        """Detect current market regime for context-aware trading"""
        try:
            if len(df) < self.regime_lookback:
                return MarketRegime.SIDEWAYS
            
            # Calculate trend indicators
            sma_short = df['close'].rolling(self.regime_lookback // 4).mean()
            sma_long = df['close'].rolling(self.regime_lookback).mean()
            
            # Calculate volatility
            returns = df['close'].pct_change()
            volatility = returns.rolling(self.regime_lookback).std().iloc[-1]
            
            # Current values
            current_price = df['close'].iloc[-1]
            current_sma_short = sma_short.iloc[-1]
            current_sma_long = sma_long.iloc[-1]
            
            # Trend detection
            trend_strength = (current_sma_short - current_sma_long) / current_sma_long
            price_position = (current_price - current_sma_long) / current_sma_long
            
            # Volatility regime
            high_vol = volatility > self.volatility_threshold
            
            # Determine regime
            if high_vol:
                return MarketRegime.HIGH_VOLATILITY
            elif abs(trend_strength) < 0.01 and abs(price_position) < 0.02:
                return MarketRegime.SIDEWAYS
            elif trend_strength > 0.02 and price_position > 0.01:
                return MarketRegime.TRENDING_UP
            elif trend_strength < -0.02 and price_position < -0.01:
                return MarketRegime.TRENDING_DOWN
            elif volatility < self.volatility_threshold * 0.5:
                return MarketRegime.LOW_VOLATILITY
            else:
                return MarketRegime.SIDEWAYS
                
        except Exception as e:
            logger.error(f"Error detecting market regime: {e}")
            return MarketRegime.SIDEWAYS
    
    def _generate_timeframe_signals(self, symbol: str, timeframe: str, df: pd.DataFrame,
                                  momentum_data: Dict[str, Any], 
                                  market_regime: MarketRegime) -> List[SignalEvent]:
        """Generate signals for specific timeframe"""
        try:
            signals = []
            
            # Get momentum scores
            composite_momentum = momentum_data.get('composite_score', 0)
            risk_adjusted_momentum = momentum_data.get('risk_adjusted', 0)
            
            # Determine signal direction and strength
            if abs(risk_adjusted_momentum) < self.momentum_threshold:
                return signals  # No signal if momentum too weak
            
            direction = 'bullish' if risk_adjusted_momentum > 0 else 'bearish'
            strength = min(abs(risk_adjusted_momentum) / self.momentum_threshold, 1.0)
            
            # Apply regime-based adjustments
            strength = self._adjust_strength_for_regime(strength, market_regime, direction)
            
            # Skip if adjusted strength too low
            if strength < self.min_signal_strength:
                return signals
            
            # Calculate risk management levels
            current_price = df['close'].iloc[-1]
            atr = self._calculate_atr(df)
            
            stop_loss = None
            take_profit = None
            
            if direction == 'bullish':
                stop_loss = current_price - (atr * self.stop_loss_atr_multiple)
                take_profit = current_price + (atr * self.stop_loss_atr_multiple * self.take_profit_ratio)
            else:
                stop_loss = current_price + (atr * self.stop_loss_atr_multiple)
                take_profit = current_price - (atr * self.stop_loss_atr_multiple * self.take_profit_ratio)
            
            # Create signal event
            signal = SignalEvent(
                event_type='MOMENTUM_SIGNAL',
                symbol=symbol,
                timeframe=timeframe,
                timestamp=datetime.utcnow(),
                direction=direction,
                strength=strength,
                level=current_price,
                metadata={
                    'momentum_type': 'enhanced_composite',
                    'composite_score': composite_momentum,
                    'risk_adjusted_score': risk_adjusted_momentum,
                    'market_regime': market_regime.value,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'atr': atr,
                    'momentum_components': momentum_data,
                    'confidence': self._calculate_signal_confidence(momentum_data, market_regime)
                }
            )
            
            signals.append(signal)
            return signals
            
        except Exception as e:
            logger.error(f"Error generating timeframe signals: {e}")
            return []
    
    def _adjust_strength_for_regime(self, base_strength: float, 
                                   market_regime: MarketRegime, direction: str) -> float:
        """Adjust signal strength based on market regime"""
        try:
            adjustment_factors = {
                MarketRegime.TRENDING_UP: {'bullish': 1.2, 'bearish': 0.7},
                MarketRegime.TRENDING_DOWN: {'bullish': 0.7, 'bearish': 1.2},
                MarketRegime.SIDEWAYS: {'bullish': 0.8, 'bearish': 0.8},
                MarketRegime.HIGH_VOLATILITY: {'bullish': 0.9, 'bearish': 0.9},
                MarketRegime.LOW_VOLATILITY: {'bullish': 1.1, 'bearish': 1.1},
                MarketRegime.BREAKOUT: {'bullish': 1.3, 'bearish': 1.3}
            }
            
            factor = adjustment_factors.get(market_regime, {}).get(direction, 1.0)
            adjusted_strength = base_strength * factor
            
            return min(adjusted_strength, 1.0)  # Cap at 1.0
            
        except Exception as e:
            logger.error(f"Error adjusting strength for regime: {e}")
            return base_strength
    
    def _calculate_signal_confidence(self, momentum_data: Dict[str, Any], 
                                   market_regime: MarketRegime) -> float:
        """Calculate confidence score for signal"""
        try:
            confidence_factors = []
            
            # Momentum consistency across indicators
            momentum_scores = []
            if 'price_momentum' in momentum_data:
                momentum_scores.extend(momentum_data['price_momentum'].values())
            if 'volume_momentum' in momentum_data and momentum_data['volume_momentum']:
                momentum_scores.extend(momentum_data['volume_momentum'].values())
            
            if momentum_scores:
                consistency = 1.0 - np.std(momentum_scores) / (np.mean(np.abs(momentum_scores)) + 1e-6)
                confidence_factors.append(max(0, consistency))
            
            # Market regime confidence
            regime_confidence = {
                MarketRegime.TRENDING_UP: 0.9,
                MarketRegime.TRENDING_DOWN: 0.9,
                MarketRegime.BREAKOUT: 0.8,
                MarketRegime.HIGH_VOLATILITY: 0.6,
                MarketRegime.LOW_VOLATILITY: 0.7,
                MarketRegime.SIDEWAYS: 0.5
            }
            confidence_factors.append(regime_confidence.get(market_regime, 0.5))
            
            # Composite momentum strength
            composite_score = abs(momentum_data.get('composite_score', 0))
            confidence_factors.append(min(composite_score / self.momentum_threshold, 1.0))
            
            # Calculate overall confidence
            overall_confidence = np.mean(confidence_factors) if confidence_factors else 0.5
            
            return float(overall_confidence)
            
        except Exception as e:
            logger.error(f"Error calculating signal confidence: {e}")
            return 0.5
    
    def _combine_timeframe_signals(self, symbol: str, timeframe_signals: Dict[str, List[SignalEvent]],
                                 timeframe_momentum: Dict[str, Dict[str, Any]]) -> List[SignalEvent]:
        """Combine signals from multiple timeframes"""
        try:
            if not timeframe_signals:
                return []
            
            # Weights for different timeframes (higher timeframes get more weight)
            timeframe_weights = {
                'M15': 0.2,
                'H1': 0.3,
                'H4': 0.5,
                'D1': 0.7
            }
            
            combined_signals = []
            
            # Check for signal alignment across timeframes
            directions = {}
            weighted_strengths = {}
            
            for timeframe, signals in timeframe_signals.items():
                if signals:
                    signal = signals[0]  # Take first signal from timeframe
                    weight = timeframe_weights.get(timeframe, 0.3)
                    
                    if signal.direction not in directions:
                        directions[signal.direction] = 0
                        weighted_strengths[signal.direction] = 0
                    
                    directions[signal.direction] += weight
                    weighted_strengths[signal.direction] += signal.strength * weight
            
            # Find dominant direction
            if directions:
                dominant_direction = max(directions.keys(), key=directions.get)
                dominant_weight = directions[dominant_direction]
                
                # Only create signal if there's sufficient alignment
                if dominant_weight >= 0.6:  # At least 60% weight alignment
                    avg_strength = weighted_strengths[dominant_direction] / dominant_weight
                    
                    # Use primary timeframe for price and metadata
                    primary_signal = timeframe_signals.get(self.primary_timeframe, [None])[0]
                    if primary_signal:
                        combined_signal = SignalEvent(
                            event_type='MULTI_TIMEFRAME_MOMENTUM',
                            symbol=symbol,
                            timeframe='MULTI',
                            timestamp=datetime.utcnow(),
                            direction=dominant_direction,
                            strength=avg_strength,
                            level=primary_signal.level,
                            metadata={
                                **primary_signal.metadata,
                                'timeframe_alignment': dominant_weight,
                                'timeframes_analyzed': list(timeframe_signals.keys()),
                                'momentum_data': timeframe_momentum
                            }
                        )
                        combined_signals.append(combined_signal)
            
            return combined_signals
            
        except Exception as e:
            logger.error(f"Error combining timeframe signals: {e}")
            return []
    
    def _filter_and_validate_signals(self, signals: List[SignalEvent]) -> List[SignalEvent]:
        """Apply advanced filtering and validation to signals"""
        try:
            if not signals:
                return signals
            
            filtered_signals = []
            
            for signal in signals:
                # Strength filter
                if signal.strength < self.min_signal_strength:
                    continue
                
                # Confidence filter
                confidence = signal.metadata.get('confidence', 0.5)
                if confidence < 0.6:
                    continue
                
                # Correlation filter (avoid highly correlated signals)
                if self._is_signal_correlated(signal, filtered_signals):
                    continue
                
                # Market condition filter
                if not self._validate_market_conditions(signal):
                    continue
                
                filtered_signals.append(signal)
            
            return filtered_signals
            
        except Exception as e:
            logger.error(f"Error filtering signals: {e}")
            return signals
    
    def _is_signal_correlated(self, new_signal: SignalEvent, 
                            existing_signals: List[SignalEvent]) -> bool:
        """Check if signal is too correlated with existing signals"""
        try:
            if not existing_signals:
                return False
            
            # Check correlation with recent signals (last 5)
            recent_signals = existing_signals[-5:]
            
            for existing_signal in recent_signals:
                # Same symbol correlation check
                if (new_signal.symbol == existing_signal.symbol and
                    new_signal.direction == existing_signal.direction):
                    
                    # Time correlation (within 1 hour)
                    time_diff = abs((new_signal.timestamp - existing_signal.timestamp).total_seconds())
                    if time_diff < 3600:  # 1 hour
                        return True
                    
                    # Price correlation (within 0.5%)
                    price_diff = abs(new_signal.level - existing_signal.level) / existing_signal.level
                    if price_diff < 0.005:  # 0.5%
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking signal correlation: {e}")
            return False
    
    def _validate_market_conditions(self, signal: SignalEvent) -> bool:
        """Validate signal against current market conditions"""
        try:
            # Market regime validation
            market_regime = signal.metadata.get('market_regime')
            
            # Skip signals in unfavorable regimes
            unfavorable_regimes = ['high_volatility'] if signal.strength < 0.8 else []
            
            if market_regime in unfavorable_regimes:
                return False
            
            # Risk-reward validation
            stop_loss = signal.metadata.get('stop_loss')
            take_profit = signal.metadata.get('take_profit')
            
            if stop_loss and take_profit:
                if signal.direction == 'bullish':
                    risk = signal.level - stop_loss
                    reward = take_profit - signal.level
                else:
                    risk = stop_loss - signal.level
                    reward = signal.level - take_profit
                
                risk_reward_ratio = reward / risk if risk > 0 else 0
                if risk_reward_ratio < 1.5:  # Minimum 1.5:1 risk-reward
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating market conditions: {e}")
            return True  # Default to valid if error
    
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
                    'market_regime': signal.metadata.get('market_regime')
                })
                
                self.performance_monitor['signals_generated'] += 1
            
        except Exception as e:
            logger.error(f"Error updating signal history: {e}")
    
    # Helper methods for technical indicators
    
    def _calculate_atr(self, df: pd.DataFrame) -> float:
        """Calculate Average True Range"""
        try:
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift(1))
            low_close = np.abs(df['low'] - df['close'].shift(1))
            
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(self.atr_period).mean().iloc[-1]
            
            return float(atr) if not pd.isna(atr) else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating ATR: {e}")
            return 0.0
    
    def _calculate_obv(self, df: pd.DataFrame) -> pd.Series:
        """Calculate On-Balance Volume"""
        try:
            obv = []
            obv_val = 0
            
            for i in range(len(df)):
                if i == 0:
                    obv.append(df['volume'].iloc[i])
                else:
                    if df['close'].iloc[i] > df['close'].iloc[i-1]:
                        obv_val += df['volume'].iloc[i]
                    elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                        obv_val -= df['volume'].iloc[i]
                    # If close prices are equal, OBV remains the same
                    obv.append(obv_val)
            
            return pd.Series(obv, index=df.index)
            
        except Exception as e:
            logger.error(f"Error calculating OBV: {e}")
            return pd.Series(0, index=df.index)
    
    def _calculate_vpt(self, df: pd.DataFrame) -> pd.Series:
        """Calculate Volume-Price Trend"""
        try:
            vpt = [0]
            
            for i in range(1, len(df)):
                price_change = (df['close'].iloc[i] - df['close'].iloc[i-1]) / df['close'].iloc[i-1]
                vpt_value = vpt[-1] + (df['volume'].iloc[i] * price_change)
                vpt.append(vpt_value)
            
            return pd.Series(vpt, index=df.index)
            
        except Exception as e:
            logger.error(f"Error calculating VPT: {e}")
            return pd.Series(0, index=df.index)
    
    def _calculate_accumulation_distribution(self, df: pd.DataFrame) -> pd.Series:
        """Calculate Accumulation/Distribution Line"""
        try:
            mfv = []  # Money Flow Volume
            ad = [0]  # Accumulation/Distribution
            
            for i in range(len(df)):
                if df['high'].iloc[i] != df['low'].iloc[i]:
                    mf_multiplier = ((df['close'].iloc[i] - df['low'].iloc[i]) - 
                                   (df['high'].iloc[i] - df['close'].iloc[i])) / (df['high'].iloc[i] - df['low'].iloc[i])
                else:
                    mf_multiplier = 0
                
                mfv_value = mf_multiplier * df['volume'].iloc[i]
                mfv.append(mfv_value)
                
                if i > 0:
                    ad_value = ad[-1] + mfv_value
                    ad.append(ad_value)
            
            return pd.Series(ad, index=df.index)
            
        except Exception as e:
            logger.error(f"Error calculating A/D Line: {e}")
            return pd.Series(0, index=df.index)
    
    def get_required_data(self) -> Dict[str, List[str]]:
        """Return required data specification"""
        return {
            '*': self.timeframes  # All symbols need specified timeframes
        }
    
    def validate_signal(self, signal: SignalEvent) -> bool:
        """Validate individual signal"""
        try:
            # Basic validation
            if not signal or signal.strength < self.min_signal_strength:
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
            logger.error(f"Error validating signal: {e}")
            return False
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        try:
            return {
                'signals_generated': self.performance_monitor['signals_generated'],
                'signals_executed': self.performance_monitor['signals_executed'],
                'win_rate': (self.performance_monitor['winning_signals'] / 
                           max(1, self.performance_monitor['signals_executed'])),
                'total_pnl': self.performance_monitor['total_pnl'],
                'max_drawdown': self.performance_monitor['max_drawdown'],
                'signal_history_length': len(self.signal_history),
                'regime_history_length': len(self.market_regime_history),
                'strategy_name': self.name,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {}

    async def cleanup(self):
        """Cleanup strategy resources"""
        try:
            logger.info(f"Cleaning up Enhanced Momentum Strategy: {self.name}")
            
            # Clear history and caches
            self.signal_history.clear()
            self.market_regime_history.clear()
            self.performance_metrics.clear()
            
            # Reset performance monitor
            self.performance_monitor = defaultdict(list)
            
            logger.info("Enhanced Momentum Strategy cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Export the enhanced strategy
__all__ = ['EnhancedMomentumStrategy', 'MomentumType', 'MarketRegime', 'MomentumSignal']
 
 

from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
import numpy as np
import logging

from .base_strategy import BaseStrategy, SignalEvent, register_strategy

logger = logging.getLogger(__name__)

@register_strategy
class MomentumStrategy(BaseStrategy):
    """Professional Momentum Strategy - FIXED CLASS NAME"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.lookback_period = config.get('momentum_lookback', 14)
        self.threshold = config.get('momentum_threshold', 0.02)
        self.signal_smoothing = config.get('signal_smoothing', 3)
        
        logger.info(f"MomentumStrategy '{name}' initialized successfully")
        
    async def initialize(self) -> bool:
        """Initialize strategy"""
        try:
            logger.info(f"Initializing MomentumStrategy: {self.name}")
            return True
        except Exception as e:
            logger.error(f"Error initializing MomentumStrategy: {e}")
            return False
        
    def generate_signals(self, data: Dict[str, pd.DataFrame]) -> List[SignalEvent]:
        """Generate momentum signals"""
        signals = []
        
        try:
            for symbol, timeframe_data in data.items():
                if isinstance(timeframe_data, dict):
                    for timeframe, df in timeframe_data.items():
                        if len(df) < self.lookback_period:
                            continue
                            
                        # Calculate momentum
                        momentum = self._calculate_momentum(df)
                        
                        if abs(momentum) > self.threshold:
                            direction = 'bullish' if momentum > 0 else 'bearish'
                            strength = min(1.0, abs(momentum) / (self.threshold * 2))
                            
                            signal = SignalEvent(
                                event_type='MOMENTUM_SIGNAL',
                                symbol=symbol,
                                timeframe=timeframe,
                                timestamp=datetime.utcnow(),
                                direction=direction,
                                strength=strength,
                                level=df['close'].iloc[-1],
                                metadata={
                                    'momentum_value': momentum,
                                    'lookback_period': self.lookback_period
                                }
                            )
                            signals.append(signal)
                            
        except Exception as e:
            logger.error(f"Error generating momentum signals: {e}")
        
        return signals
    
    def _calculate_momentum(self, df: pd.DataFrame) -> float:
        """Calculate momentum indicator"""
        try:
            if len(df) < self.lookback_period:
                return 0.0
                
            # Simple price momentum
            current_price = df['close'].iloc[-1]
            past_price = df['close'].iloc[-self.lookback_period]
            
            if past_price > 0:
                momentum = (current_price - past_price) / past_price
            else:
                momentum = 0.0
                
            return float(momentum)
            
        except Exception as e:
            logger.error(f"Error calculating momentum: {e}")
            return 0.0
    
    def get_required_data(self) -> Dict[str, List[str]]:
        """Return required data specification"""
        return {'*': ['M15', 'H1']}
        
    def validate_signal(self, signal) -> bool:
        """Validate signal"""
        return signal.strength > 0.5

# Export for compatibility
EnhancedMomentumStrategy = MomentumStrategy  # Alias for backward compatibility