"""
Base Strategy Abstract Class
===========================
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
from enum import Enum

class StrategyState(Enum):
    """Strategy operational states"""
    INACTIVE = "inactive"
    ACTIVE = "active"
    AWAITING_CONTEXT = "awaiting_context"
    SIGNAL_GENERATED = "signal_generated"
    POSITION_OPEN = "position_open"
    PAUSED = "paused"
    ERROR = "error"

@dataclass
class SignalEvent:
    """Trading signal event structure"""
    event_type: str
    symbol: str
    timeframe: str
    timestamp: datetime
    direction: str
    strength: float
    level: float
    metadata: Dict[str, Any]

@dataclass  
class TradeSetup:
    """Trade setup structure"""
    symbol: str
    direction: str
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float
    confluence_score: float
    strategy_source: str
    timeframe: str
    timestamp: datetime
    metadata: Dict[str, Any]

class BaseStrategy(ABC):
    """Abstract base class for all trading strategies"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.enabled = True
        self.state = StrategyState.INACTIVE
        
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize strategy"""
        pass
        
    @abstractmethod
    def generate_signals(self, data: Dict[str, pd.DataFrame]) -> List[SignalEvent]:
        """Generate trading signals"""
        pass
        
    @abstractmethod
    def get_required_data(self) -> Dict[str, List[str]]:
        """Get required data specifications"""
        pass
        
    @abstractmethod
    def validate_signal(self, signal) -> bool:
        """Validate signal before execution"""
        pass

# Strategy registration system
_strategy_registry = {}

def register_strategy(strategy_class):
    """Decorator to register strategy classes"""
    _strategy_registry[strategy_class.__name__] = strategy_class
    return strategy_class

class PrimaryStrategy(BaseStrategy):
    """Base class for primary strategies"""
    pass

class SecondaryStrategy(BaseStrategy):
    """Base class for secondary strategies"""
    pass

class StatefulStrategy(BaseStrategy):
    """Base class for stateful strategies"""
    
    def transition_state(self, new_state: StrategyState):
        """Transition to new state"""
        self.state = new_state
