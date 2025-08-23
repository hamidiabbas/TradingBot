"""
Base strategy classes and interfaces for the trading system.
All strategies must inherit from BaseStrategy to ensure uniform interface.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
import numpy as np

@dataclass
class SignalEvent:
    """Structured signal event for the confluence engine"""
    event_type: str  # e.g., 'RTM_DEMAND_ZONE_ENTERED', 'ICT_MSS_CONFIRMED'
    symbol: str
    timeframe: str
    timestamp: datetime
    direction: str  # 'bullish', 'bearish', 'neutral'
    strength: float  # 0.0 to 1.0
    level: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class TradeSetup:
    """Complete trade setup with entry, exit, and risk parameters"""
    symbol: str
    direction: str  # 'long', 'short'
    entry_price: float
    stop_loss: float
    take_profit: Optional[float]
    position_size: float
    confluence_score: float
    strategy_source: str
    timeframe: str
    timestamp: datetime
    metadata: Dict[str, Any]

class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    Enforces standardized interface for strategy implementation.
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.enabled = config.get('enabled', True)
        self.signal_events: List[SignalEvent] = []
        self.last_update = None
        
    @abstractmethod
    def generate_signals(self, data: Dict[str, pd.DataFrame]) -> List[SignalEvent]:
        """
        Generate trading signals based on market data.
        
        Args:
            data: Dictionary with timeframe as key and OHLCV DataFrame as value
            
        Returns:
            List of SignalEvent objects
        """
        pass
    
    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get strategy parameters for optimization and configuration.
        
        Returns:
            Dictionary of strategy parameters
        """
        pass
    
    @abstractmethod
    def validate_setup(self, setup: TradeSetup) -> bool:
        """
        Validate a trade setup according to strategy rules.
        
        Args:
            setup: TradeSetup object to validate
            
        Returns:
            True if setup is valid, False otherwise
        """
        pass
    
    def update_parameters(self, new_params: Dict[str, Any]) -> None:
        """Update strategy parameters"""
        self.config.update(new_params)
    
    def reset_signals(self) -> None:
        """Clear accumulated signal events"""
        self.signal_events = []
    
    def get_signal_events(self) -> List[SignalEvent]:
        """Get current signal events"""
        return self.signal_events.copy()

class PrimaryStrategy(BaseStrategy):
    """
    Base class for primary signal generators (ICT, RTM).
    These strategies identify core trading opportunities.
    """
    
    @abstractmethod
    def identify_trading_zones(self, data: Dict[str, pd.DataFrame]) -> List[Dict[str, Any]]:
        """
        Identify high-probability trading zones or levels.
        
        Args:
            data: Market data across multiple timeframes
            
        Returns:
            List of trading zone dictionaries
        """
        pass
    
    @abstractmethod
    def scan_for_entry_models(self, data: Dict[str, pd.DataFrame], zones: List[Dict[str, Any]]) -> List[TradeSetup]:
        """
        Scan for specific entry patterns within identified zones.
        
        Args:
            data: Market data
            zones: Previously identified trading zones
            
        Returns:
            List of complete trade setups
        """
        pass

class SecondaryStrategy(BaseStrategy):
    """
    Base class for secondary confirmation strategies (Indicator Suite).
    These strategies provide additional evidence for existing setups.
    """
    
    @abstractmethod
    def calculate_indicators(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        Calculate technical indicators.
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            Dictionary of indicator series
        """
        pass
    
    @abstractmethod
    def generate_confirmation_signals(self, indicators: Dict[str, pd.Series]) -> List[SignalEvent]:
        """
        Generate confirmation signals based on indicators.
        
        Args:
            indicators: Dictionary of calculated indicators
            
        Returns:
            List of confirmation signal events
        """
        pass

class StrategyState:
    """Enumeration for strategy states"""
    AWAITING_CONTEXT = "AWAITING_CONTEXT"
    MONITORING_POI = "MONITORING_POI"
    SCANNING_ENTRY = "SCANNING_ENTRY"
    POSITION_MANAGEMENT = "POSITION_MANAGEMENT"
    PAUSED = "PAUSED"
    ERROR = "ERROR"

class StatefulStrategy(PrimaryStrategy):
    """
    Base class for strategies with state machines (mainly for ICT implementation).
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.state = StrategyState.AWAITING_CONTEXT
        self.state_data: Dict[str, Any] = {}
    
    @abstractmethod
    def transition_state(self, new_state: str, **kwargs) -> None:
        """
        Transition to a new strategy state.
        
        Args:
            new_state: Target state
            **kwargs: Additional state data
        """
        pass
    
    def get_state(self) -> Tuple[str, Dict[str, Any]]:
        """Get current state and state data"""
        return self.state, self.state_data.copy()

# Strategy registry for dynamic loading
STRATEGY_REGISTRY: Dict[str, type] = {}

def register_strategy(strategy_class: type) -> type:
    """Decorator to register strategy classes"""
    STRATEGY_REGISTRY[strategy_class.__name__] = strategy_class
    return strategy_class

def get_strategy_class(name: str) -> Optional[type]:
    """Get strategy class by name"""
    return STRATEGY_REGISTRY.get(name)

def list_available_strategies() -> List[str]:
    """List all registered strategy names"""
    return list(STRATEGY_REGISTRY.keys())
"""
Strategies Package Initialization
=================================
"""

from .base_strategy import (
    BaseStrategy, PrimaryStrategy, SecondaryStrategy, StatefulStrategy,
    SignalEvent, TradeSetup, StrategyState, register_strategy
)

from .momentum_strategy import MomentumStrategy
from .mean_reversion_strategy import MeanReversionStrategy  
from .breakout_strategy import BreakoutStrategy

# Import your sophisticated strategies
try:
    from .indicator_suite_strategy import EnhancedIndicatorSuiteStrategy
except ImportError:
    pass

try:
    from .rtm_strategy import EnhancedRTMStrategy
except ImportError:
    pass

try:
    from .ict_strategy import EnhancedICTStrategy
except ImportError:
    pass

__all__ = [
    'BaseStrategy', 'PrimaryStrategy', 'SecondaryStrategy', 'StatefulStrategy',
    'SignalEvent', 'TradeSetup', 'StrategyState', 'register_strategy',
    'MomentumStrategy', 'MeanReversionStrategy', 'BreakoutStrategy'
]
