"""
Complete Strategy Base Classes with All Missing Components - OPTIMIZED
=====================================================================
This file provides all the base classes and functions that strategies import
"""
from abc import ABC, abstractmethod
import logging 
from typing import Dict, List, Any, Optional, Union
import pandas as pd
import numpy as np
from datetime import datetime


class BaseStrategy(ABC):
    """Base strategy class with proper initialization"""
    
    def __init__(self, name: str = None, config: Dict = None, **kwargs):
        self.name = name or self.__class__.__name__
        self.config = config or {}
        self.timeframe = kwargs.get('timeframe', 'H1')
        self.period = kwargs.get('period', 20)
        self.threshold = kwargs.get('threshold', 0.5)
        
        # Handle any additional parameters
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def analyze(self, data: pd.DataFrame, symbol: str = None) -> Dict[str, Any]:
        """Default analyze method - should be overridden by strategies"""
        try:
            if data is None or data.empty or len(data) < 10:
                return {
                    'signal': 'HOLD',
                    'confidence': 0.0,
                    'price': 1.0,
                    'reason': 'Insufficient data'
                }
            
            # Simple default logic that will generate some signals
            current_price = data['close'].iloc[-1]
            
            return {
                'signal': 'HOLD',
                'confidence': 0.5,
                'price': current_price,
                'reason': 'Base strategy default'
            }
        except Exception as e:
            return {
                'signal': 'HOLD',
                'confidence': 0.0,
                'price': 1.0,
                'reason': f'Error: {str(e)}'
            }


class PrimaryStrategy(BaseStrategy):
    """Primary strategy class"""
    
    def __init__(self, name: str = None, config: Dict = None, **kwargs):
        super().__init__(name, config, **kwargs)
        self.strategy_type = 'primary'
    
    def analyze(self, data: pd.DataFrame, symbol: str = None) -> Dict[str, Any]:
        """Enhanced default analyze method"""
        try:
            if data is None or data.empty or len(data) < 20:
                return {'signal': 'HOLD', 'confidence': 0.0, 'price': 1.0, 'reason': 'Insufficient data'}
            
            # Simple momentum-based signal
            current_price = data['close'].iloc[-1]
            ma_20 = data['close'].rolling(20).mean().iloc[-1]
            
            if current_price > ma_20 * 1.002:  # 0.2% above MA
                return {
                    'signal': 'BUY',
                    'confidence': 0.6,
                    'price': current_price,
                    'reason': 'Primary: Above MA20'
                }
            elif current_price < ma_20 * 0.998:  # 0.2% below MA
                return {
                    'signal': 'SELL',
                    'confidence': 0.6,
                    'price': current_price,
                    'reason': 'Primary: Below MA20'
                }
            
            return {'signal': 'HOLD', 'confidence': 0.0, 'price': current_price, 'reason': 'No signal'}
            
        except Exception as e:
            return {'signal': 'HOLD', 'confidence': 0.0, 'price': 1.0, 'reason': f'Error: {e}'}


class SecondaryStrategy(BaseStrategy):
    """Secondary strategy class"""
    
    def __init__(self, name: str = None, config: Dict = None, **kwargs):
        super().__init__(name, config, **kwargs)
        self.strategy_type = 'secondary'
    
    def analyze(self, data: pd.DataFrame, symbol: str = None) -> Dict[str, Any]:
        """Secondary strategy with different logic"""
        try:
            if data is None or data.empty or len(data) < 10:
                return {'signal': 'HOLD', 'confidence': 0.0, 'price': 1.0, 'reason': 'Insufficient data'}
            
            # Simple volatility-based signal
            current_price = data['close'].iloc[-1]
            recent_high = data['high'].rolling(10).max().iloc[-1]
            recent_low = data['low'].rolling(10).min().iloc[-1]
            
            if current_price > recent_high * 0.999:  # Near recent high
                return {
                    'signal': 'BUY',
                    'confidence': 0.55,
                    'price': current_price,
                    'reason': 'Secondary: Near high'
                }
            elif current_price < recent_low * 1.001:  # Near recent low
                return {
                    'signal': 'SELL',
                    'confidence': 0.55,
                    'price': current_price,
                    'reason': 'Secondary: Near low'
                }
            
            return {'signal': 'HOLD', 'confidence': 0.0, 'price': current_price, 'reason': 'No signal'}
            
        except Exception as e:
            return {'signal': 'HOLD', 'confidence': 0.0, 'price': 1.0, 'reason': f'Error: {e}'}


class StatefulStrategy(BaseStrategy):
    """Stateful strategy with memory"""
    
    def __init__(self, name: str = None, config: Dict = None, **kwargs):
        super().__init__(name, config, **kwargs)
        self.state = StrategyState()
    
    def analyze(self, data: pd.DataFrame, symbol: str = None) -> Dict[str, Any]:
        """Stateful analysis"""
        try:
            if data is None or data.empty or len(data) < 5:
                return {'signal': 'HOLD', 'confidence': 0.0, 'price': 1.0, 'reason': 'Insufficient data'}
            
            current_price = data['close'].iloc[-1]
            prev_price = data['close'].iloc[-2]
            
            # Simple trend following with state
            if current_price > prev_price and self.state.state != 'bullish':
                self.state.state = 'bullish'
                return {
                    'signal': 'BUY',
                    'confidence': 0.65,
                    'price': current_price,
                    'reason': 'Stateful: Trend change to bullish'
                }
            elif current_price < prev_price and self.state.state != 'bearish':
                self.state.state = 'bearish'
                return {
                    'signal': 'SELL',
                    'confidence': 0.65,
                    'price': current_price,
                    'reason': 'Stateful: Trend change to bearish'
                }
            
            return {'signal': 'HOLD', 'confidence': 0.0, 'price': current_price, 'reason': 'No state change'}
            
        except Exception as e:
            return {'signal': 'HOLD', 'confidence': 0.0, 'price': 1.0, 'reason': f'Error: {e}'}


class StrategyState:
    """Strategy state management"""
    
    def __init__(self, **kwargs):
        self.state = 'neutral'
        self.last_signal = None
        self.position = None
        self.entry_time = None
        
        # Handle additional parameters
        for key, value in kwargs.items():
            setattr(self, key, value)


class SignalEvent:
    """Signal event class for compatibility"""
    
    def __init__(self, event_type: str = 'SIGNAL', symbol: str = 'EURUSD', 
                 direction: str = 'neutral', strength: float = 0.5, 
                 level: float = 1.0, timestamp: pd.Timestamp = None, 
                 metadata: Dict = None, **kwargs):
        self.event_type = event_type
        self.symbol = symbol
        self.direction = direction
        self.strength = strength
        self.level = level
        self.timestamp = timestamp or pd.Timestamp.now()
        self.metadata = metadata or {}
        
        # Handle additional parameters
        for key, value in kwargs.items():
            setattr(self, key, value)


class TradeSetup:
    """Trade setup class for strategy compatibility"""
    
    def __init__(self, entry_price: float = 1.0, stop_loss: float = 0.99, 
                 take_profit: float = 1.01, direction: str = 'BUY', 
                 confidence: float = 0.7, quantity: int = 1, 
                 symbol: str = 'EURUSD', **kwargs):
        self.entry_price = entry_price
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.direction = direction
        self.confidence = confidence
        self.quantity = quantity
        self.symbol = symbol
        self.timestamp = pd.Timestamp.now()
        
        # Handle additional parameters
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'direction': self.direction,
            'confidence': self.confidence,
            'quantity': self.quantity,
            'symbol': self.symbol,
            'timestamp': self.timestamp
        }


# CRITICAL: The register_strategy function that many strategies use
def register_strategy(strategy_class):
    """
    Strategy registration decorator/function
    Used by many strategies for registration with the system
    """
    # Initialize registry if it doesn't exist
    if not hasattr(register_strategy, 'registered_strategies'):
        register_strategy.registered_strategies = []
    
    # Add to registry
    register_strategy.registered_strategies.append(strategy_class)
    
    # Return the class unchanged (it's a decorator)
    return strategy_class


# Additional compatibility classes
class TradingSignal:
    """Trading signal class for compatibility"""
    
    def __init__(self, signal_type: str = 'HOLD', strength: float = 0.5, 
                 price: float = 1.0, timestamp: pd.Timestamp = None, **kwargs):
        self.signal_type = signal_type
        self.strength = strength
        self.price = price
        self.timestamp = timestamp or pd.Timestamp.now()
        
        for key, value in kwargs.items():
            setattr(self, key, value)


class StrategyConfig:
    """Strategy configuration class"""
    
    def __init__(self, **kwargs):
        # Set default values
        self.timeframe = kwargs.get('timeframe', 'H1')
        self.period = kwargs.get('period', 20)
        self.threshold = kwargs.get('threshold', 0.5)
        
        # Set all provided parameters
        for key, value in kwargs.items():
            setattr(self, key, value)


# Registry management functions
def get_registered_strategies() -> List[Any]:
    """Get list of all registered strategies"""
    strategies = []
    
    # Get strategies from registry
    if hasattr(register_strategy, 'registered_strategies'):
        strategies.extend(register_strategy.registered_strategies)
    
    # Add base strategy classes
    base_classes = [BaseStrategy, PrimaryStrategy, SecondaryStrategy, StatefulStrategy]
    strategies.extend(base_classes)
    
    return strategies


def get_strategy_registry() -> Dict[str, Any]:
    """Get strategy registry as dictionary"""
    strategies = get_registered_strategies()
    return {cls.__name__: cls for cls in strategies if hasattr(cls, '__name__')}


# Export everything for easy importing
__all__ = [
    'BaseStrategy', 'PrimaryStrategy', 'SecondaryStrategy', 'StatefulStrategy',
    'StrategyState', 'SignalEvent', 'TradeSetup', 'register_strategy',
    'TradingSignal', 'StrategyConfig', 'get_registered_strategies', 'get_strategy_registry'
]

# Logging setup for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("✅ BaseStrategy module loaded with all classes and functions")
