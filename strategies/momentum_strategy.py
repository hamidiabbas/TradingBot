#!/usr/bin/env python3
"""
EnhancedMomentumStrategy - Final Fixed Version with High-Performance Analysis
Complete implementation with aggressive signal generation for immediate results
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from .base_strategy import BaseStrategy, register_strategy

<<<<<<< HEAD
# Import base strategy and event system
from base_strategy import BaseStrategy, SignalEvent, register_strategy

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
=======
@register_strategy  
>>>>>>> 8f626e2ef1a5d0198eacb62ca49d93985fc3b2f3
class EnhancedMomentumStrategy(BaseStrategy):
    """Enhanced EnhancedMomentumStrategy with aggressive signal generation"""
    
    def __init__(self, name: str = "EnhancedMomentumStrategy", config: Dict[str, Any] = None):
        super().__init__(name, config or {})
        self.strategy_type = "momentum"
        self.confidence_multiplier = 2.5  # Aggressive confidence boost
        self.signal_threshold = 0.002  # Lower threshold for more signals
        
    def analyze(self, data: pd.DataFrame, symbol: str = None) -> Optional[Dict[str, Any]]:
        """
        High-performance analysis with aggressive signal generation
        Designed to generate confident trading signals immediately
        """
        try:
            if data is None or data.empty or len(data) < 5:
                return self._create_default_result(data, symbol)

            # Get current price and basic data
            current_price = float(data['close'].iloc[-1])
            close_prices = data['close'].values
            
            # Initialize signal components
            signal_type = "HOLD"
            base_confidence = 0.0
            direction = "neutral"
            reasons = []
            
            # === AGGRESSIVE MOMENTUM DETECTION ===
            if len(close_prices) >= 5:
                # Short-term momentum (more sensitive)
                momentum_3 = (close_prices[-1] - close_prices[-4]) / close_prices[-4] if len(close_prices) > 3 else 0
                momentum_5 = (close_prices[-1] - close_prices[-6]) / close_prices[-6] if len(close_prices) > 5 else 0
                
                # AGGRESSIVE BULLISH SIGNALS
                if momentum_3 > self.signal_threshold:  # 0.2% threshold
                    signal_type = "BUY"
                    direction = "bullish"
                    base_confidence = min(0.85, abs(momentum_3) * 100)  # Amplified confidence
                    reasons.append(f"Strong bullish momentum: {momentum_3:.4%}")
                    
                    # Additional boost for strong momentum
                    if momentum_3 > self.signal_threshold * 2:
                        base_confidence = min(0.95, base_confidence * 1.3)
                        reasons.append("Exceptional momentum strength")
                
                # AGGRESSIVE BEARISH SIGNALS  
                elif momentum_3 < -self.signal_threshold:
                    signal_type = "SELL"
                    direction = "bearish"
                    base_confidence = min(0.85, abs(momentum_3) * 100)
                    reasons.append(f"Strong bearish momentum: {momentum_3:.4%}")
                    
                    if momentum_3 < -self.signal_threshold * 2:
                        base_confidence = min(0.95, base_confidence * 1.3)
                        reasons.append("Exceptional momentum strength")
                
                # MEDIUM MOMENTUM SIGNALS (more sensitive)
                elif momentum_3 > self.signal_threshold * 0.5:
                    signal_type = "BUY"
                    direction = "bullish"
                    base_confidence = min(0.7, abs(momentum_3) * 80)
                    reasons.append(f"Medium bullish momentum: {momentum_3:.4%}")
                    
                elif momentum_3 < -self.signal_threshold * 0.5:
                    signal_type = "SELL"
                    direction = "bearish"  
                    base_confidence = min(0.7, abs(momentum_3) * 80)
                    reasons.append(f"Medium bearish momentum: {momentum_3:.4%}")
            
            # === MOVING AVERAGE CONFIRMATION (Aggressive) ===
            if len(close_prices) >= 10:
                sma_5 = np.mean(close_prices[-5:])
                sma_10 = np.mean(close_prices[-10:])
                
                # Price above MA with confirmation
                if current_price > sma_5 > sma_10:
                    if signal_type == "HOLD":
                        signal_type = "BUY"
                        direction = "bullish"
                        base_confidence = 0.6
                    elif signal_type == "BUY":
                        base_confidence = min(0.95, base_confidence + 0.3)
                    reasons.append("Bullish MA alignment")
                    
                # Price below MA with confirmation
                elif current_price < sma_5 < sma_10:
                    if signal_type == "HOLD":
                        signal_type = "SELL"
                        direction = "bearish"
                        base_confidence = 0.6
                    elif signal_type == "SELL":
                        base_confidence = min(0.95, base_confidence + 0.3)
                    reasons.append("Bearish MA alignment")
            
            # === VOLATILITY BOOST (Unique Feature) ===
            if len(close_prices) >= 10:
                recent_volatility = np.std(close_prices[-5:])
                normal_volatility = np.std(close_prices[-10:])
                
                if recent_volatility > normal_volatility * 1.2 and signal_type != "HOLD":
                    base_confidence = min(0.95, base_confidence + 0.15)
                    reasons.append("High volatility confirmation")
            
            # === PRICE ACTION PATTERNS ===
            if len(close_prices) >= 3:
                # Simple pattern recognition
                if (close_prices[-1] > close_prices[-2] > close_prices[-3] and 
                    signal_type in ["BUY", "HOLD"]):
                    if signal_type == "HOLD":
                        signal_type = "BUY"
                        direction = "bullish"
                        base_confidence = 0.5
                    else:
                        base_confidence = min(0.9, base_confidence + 0.2)
                    reasons.append("Bullish price pattern")
                    
                elif (close_prices[-1] < close_prices[-2] < close_prices[-3] and 
                      signal_type in ["SELL", "HOLD"]):
                    if signal_type == "HOLD":
                        signal_type = "SELL"
                        direction = "bearish"
                        base_confidence = 0.5
                    else:
                        base_confidence = min(0.9, base_confidence + 0.2)
                    reasons.append("Bearish price pattern")
            
            # === FINAL CONFIDENCE BOOST ===
            final_confidence = base_confidence * self.confidence_multiplier
            final_confidence = min(0.95, final_confidence)  # Cap at 95%
            
            # Ensure minimum confidence for actionable signals
            if signal_type != "HOLD" and final_confidence < 0.3:
                final_confidence = 0.3  # Minimum actionable confidence
            
            # Create result
            result = {
                'signal': signal_type,
                'confidence': final_confidence,
                'direction': direction,
                'price': current_price,
                'entry_price': current_price,
                'reason': f"{self.__class__.__name__}: {', '.join(reasons)}" if reasons else f"{self.__class__.__name__}: No clear signal",
                'stop_loss': current_price * 0.995 if signal_type == "BUY" else current_price * 1.005 if signal_type == "SELL" else None,
                'take_profit': current_price * 1.02 if signal_type == "BUY" else current_price * 0.98 if signal_type == "SELL" else None,
                'metadata': {
                    'strategy_type': self.strategy_type,
                    'data_points': len(data),
                    'aggressive_mode': True,
                    'confidence_multiplier': self.confidence_multiplier,
                    'signal_threshold': self.signal_threshold
                }
            }
            
            # Enhanced logging
            if hasattr(self, 'logger'):
                self.logger.info(f"{self.__class__.__name__} AGGRESSIVE analysis for {symbol}: {signal_type} (conf: {final_confidence:.2f})")
                
            return result
            
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"Error in {self.__class__.__name__} analysis: {e}")
            
            return self._create_default_result(data, symbol)
    
    def _create_default_result(self, data, symbol):
        """Create default result"""
        current_price = 1.0
        try:
            if not data.empty and 'close' in data.columns:
                current_price = float(data['close'].iloc[-1])
        except:
            pass
            
        return {
            'signal': 'HOLD',
            'confidence': 0.0,
            'direction': 'neutral',
            'price': current_price,
            'entry_price': current_price,
            'reason': f'{self.__class__.__name__}: Insufficient data or error',
            'stop_loss': None,
            'take_profit': None,
            'metadata': {'strategy_type': self.strategy_type, 'error_fallback': True}
        }

<<<<<<< HEAD
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

from base_strategy import BaseStrategy, SignalEvent, register_strategy

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
=======
# Export for backwards compatibility
MomentumStrategy = EnhancedMomentumStrategy  # Alias for import compatibility
>>>>>>> 8f626e2ef1a5d0198eacb62ca49d93985fc3b2f3
