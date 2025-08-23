# unified_signals.py
"""
Unified Trading Signals Module for TradingBot v1.0
Provides common signal types, data structures, and utilities for all strategies
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime
import pandas as pd
import numpy as np

class SignalType(Enum):
    """Trading signal types"""
    BUY = "buy"
    SELL = "sell" 
    HOLD = "hold"
    CLOSE = "close"
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"

class StrategyType(Enum):
    """Strategy classification types"""
    SCALPING = "scalping"
    SWING = "swing"
    TREND_FOLLOWING = "trend_following"
    MEAN_REVERSION = "mean_reversion"
    BREAKOUT = "breakout"
    MOMENTUM = "momentum"
    VOLUME = "volume"
    NEWS = "news"
    ARBITRAGE = "arbitrage"
    ICT = "ict"
    RTM = "rtm"
    SMC = "smc"

@dataclass
class UnifiedTradingSignal:
    """Unified trading signal structure used across all strategies"""
    
    # Core signal information
    symbol: str
    direction: str  # 'bullish', 'bearish', 'neutral'
    signal_type: SignalType = SignalType.HOLD
    strength: float = 0.0  # 0.0 to 1.0
    confidence: float = 0.0  # 0.0 to 1.0
    
    # Price levels
    level: float = 0.0
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    # Timing information
    timestamp: datetime = None
    timeframe: str = "H1"
    
    # Strategy information
    strategy_name: str = ""
    strategy_type: StrategyType = StrategyType.TREND_FOLLOWING
    
    # Signal metadata
    reason: str = ""
    metadata: Dict[str, Any] = None
    
    # Risk and position sizing
    risk_reward_ratio: float = 0.0
    position_size: float = 0.0
    
    # Additional flags
    is_entry_signal: bool = True
    is_exit_signal: bool = False
    requires_confirmation: bool = False
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.now()
        
        # Ensure consistency between direction and signal_type
        if self.direction in ['bullish', 'buy'] and self.signal_type == SignalType.HOLD:
            self.signal_type = SignalType.BUY
        elif self.direction in ['bearish', 'sell'] and self.signal_type == SignalType.HOLD:
            self.signal_type = SignalType.SELL
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert signal to dictionary for serialization"""
        return {
            'symbol': self.symbol,
            'direction': self.direction,
            'signal_type': self.signal_type.value,
            'strength': self.strength,
            'confidence': self.confidence,
            'level': self.level,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'timeframe': self.timeframe,
            'strategy_name': self.strategy_name,
            'strategy_type': self.strategy_type.value,
            'reason': self.reason,
            'metadata': self.metadata,
            'risk_reward_ratio': self.risk_reward_ratio,
            'position_size': self.position_size
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UnifiedTradingSignal':
        """Create signal from dictionary"""
        timestamp = None
        if data.get('timestamp'):
            timestamp = datetime.fromisoformat(data['timestamp'])
        
        return cls(
            symbol=data['symbol'],
            direction=data['direction'],
            signal_type=SignalType(data.get('signal_type', 'hold')),
            strength=data.get('strength', 0.0),
            confidence=data.get('confidence', 0.0),
            level=data.get('level', 0.0),
            entry_price=data.get('entry_price'),
            stop_loss=data.get('stop_loss'),
            take_profit=data.get('take_profit'),
            timestamp=timestamp,
            timeframe=data.get('timeframe', 'H1'),
            strategy_name=data.get('strategy_name', ''),
            strategy_type=StrategyType(data.get('strategy_type', 'trend_following')),
            reason=data.get('reason', ''),
            metadata=data.get('metadata', {}),
            risk_reward_ratio=data.get('risk_reward_ratio', 0.0),
            position_size=data.get('position_size', 0.0)
        )

# Utility functions for signal processing
def calculate_signal_strength(indicators: Dict[str, float], weights: Dict[str, float] = None) -> float:
    """Calculate overall signal strength from multiple indicators"""
    if not indicators:
        return 0.0
    
    if weights is None:
        weights = {k: 1.0 for k in indicators.keys()}
    
    total_weight = sum(weights.values())
    if total_weight == 0:
        return 0.0
    
    weighted_sum = sum(indicators.get(k, 0) * weights.get(k, 1.0) for k in indicators.keys())
    return min(1.0, max(0.0, weighted_sum / total_weight))

def normalize_direction(direction: str) -> str:
    """Normalize direction string to standard format"""
    direction = direction.lower().strip()
    
    bullish_terms = ['bullish', 'buy', 'long', 'up', 'positive']
    bearish_terms = ['bearish', 'sell', 'short', 'down', 'negative']
    
    if direction in bullish_terms:
        return 'bullish'
    elif direction in bearish_terms:
        return 'bearish'
    else:
        return 'neutral'

def combine_signals(signals: List[UnifiedTradingSignal], method: str = 'weighted_average') -> UnifiedTradingSignal:
    """Combine multiple signals into one consolidated signal"""
    if not signals:
        return UnifiedTradingSignal(symbol="", direction="neutral")
    
    if len(signals) == 1:
        return signals[0]
    
    # Get the most common symbol
    symbol = max(set(s.symbol for s in signals), key=lambda x: sum(1 for s in signals if s.symbol == x))
    
    if method == 'weighted_average':
        total_weight = sum(s.strength for s in signals)
        if total_weight == 0:
            return UnifiedTradingSignal(symbol=symbol, direction="neutral")
        
        # Calculate weighted averages
        avg_strength = sum(s.strength * s.strength for s in signals) / total_weight
        avg_confidence = sum(s.confidence * s.strength for s in signals) / total_weight
        
        # Determine overall direction
        bullish_weight = sum(s.strength for s in signals if s.direction in ['bullish', 'buy'])
        bearish_weight = sum(s.strength for s in signals if s.direction in ['bearish', 'sell'])
        
        if bullish_weight > bearish_weight:
            direction = 'bullish'
        elif bearish_weight > bullish_weight:
            direction = 'bearish'
        else:
            direction = 'neutral'
        
        return UnifiedTradingSignal(
            symbol=symbol,
            direction=direction,
            strength=avg_strength,
            confidence=avg_confidence,
            strategy_name="Combined",
            reason=f"Combined from {len(signals)} signals",
            metadata={'component_signals': len(signals)}
        )
    
    else:  # majority vote
        directions = [s.direction for s in signals]
        most_common_direction = max(set(directions), key=directions.count)
        
        relevant_signals = [s for s in signals if s.direction == most_common_direction]
        avg_strength = sum(s.strength for s in relevant_signals) / len(relevant_signals)
        avg_confidence = sum(s.confidence for s in relevant_signals) / len(relevant_signals)
        
        return UnifiedTradingSignal(
            symbol=symbol,
            direction=most_common_direction,
            strength=avg_strength,
            confidence=avg_confidence,
            strategy_name="Majority",
            reason=f"Majority vote from {len(signals)} signals"
        )

# Technical analysis utilities
def calculate_pip_value(symbol: str, price: float) -> float:
    """Calculate pip value for a given symbol"""
    if 'JPY' in symbol:
        return 0.01
    else:
        return 0.0001

def calculate_position_risk(entry_price: float, stop_loss: float, position_size: float, account_balance: float) -> float:
    """Calculate position risk as percentage of account"""
    if not all([entry_price, stop_loss, position_size, account_balance]) or account_balance <= 0:
        return 0.0
    
    risk_amount = abs(entry_price - stop_loss) * position_size
    return (risk_amount / account_balance) * 100

# Signal validation functions
def validate_signal(signal: UnifiedTradingSignal) -> bool:
    """Validate signal for basic consistency"""
    if not signal.symbol:
        return False
    
    if signal.strength < 0 or signal.strength > 1:
        return False
    
    if signal.confidence < 0 or signal.confidence > 1:
        return False
    
    if signal.direction not in ['bullish', 'bearish', 'neutral']:
        return False
    
    return True

def filter_signals_by_strength(signals: List[UnifiedTradingSignal], min_strength: float = 0.5) -> List[UnifiedTradingSignal]:
    """Filter signals by minimum strength threshold"""
    return [s for s in signals if s.strength >= min_strength]

def filter_signals_by_confidence(signals: List[UnifiedTradingSignal], min_confidence: float = 0.6) -> List[UnifiedTradingSignal]:
    """Filter signals by minimum confidence threshold"""
    return [s for s in signals if s.confidence >= min_confidence]

# Export all commonly used classes and functions
__all__ = [
    'SignalType',
    'StrategyType', 
    'UnifiedTradingSignal',
    'calculate_signal_strength',
    'normalize_direction',
    'combine_signals',
    'calculate_pip_value',
    'calculate_position_risk',
    'validate_signal',
    'filter_signals_by_strength',
    'filter_signals_by_confidence'
]
