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
        pass
        pass
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
        pass
        pass
    from numpy_compatibility import NaN
except ImportError:
    NaN = np.nan

# PrimaryStrategy import with fallback
try:
        pass
        pass
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
        pass
        pass
    from strategies.unified_signals import UnifiedTradingSignal, generate_basic_signal
except ImportError:
    class UnifiedTradingSignal:
        def __init__(self, signal="HOLD", confidence=0.5, price=1.0, reason=""):
            self.signal = signal
            self.confidence = confidence
            self.price = price
            self.reason = reason

try:
        pass
        pass
    from strategies.numpy_compatibility import NaN
except ImportError:
    NaN = np.nan

try:
        pass
        pass
    from utils.logger import setup_logging, logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    def setup_logging(*args, **kwargs):
        return logger

try:
        pass
        pass
    from utils.price_action import calculate_fibonacci_retracements, identify_support_resistance
except ImportError:
    def calculate_fibonacci_retracements(high, low):
        return {'level_0': high, 'level_100': low}
    def identify_support_resistance(df, window=20):
        return {'support': 1.0, 'resistance': 1.0}

# NumPy compatibility
try:
        pass
        pass
        pass
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
        pass
        pass
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
Strategy Compatibility Layer
===========================
Bridges naming conflicts in your existing strategies
"""

from typing import Dict, Any, Optional, List
import importlib
import sys

class StrategyRegistry:
        pass
        pass
        pass

    def analyze(self, data, symbol="EURUSD"):
        """Kelly-compatible analyze method for Compatibility"""
        try:
        pass
        pass
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
                        'reason': f'Compatibility bullish trend'
                    }
                elif current_price < ma_20 < ma_50:
                    return {
                        'signal': 'SELL', 
                        'confidence': 0.65,
                        'price': current_price,
                        'reason': f'Compatibility bearish trend'
                    }
            
            return {
                'signal': 'HOLD',
                'confidence': 0.4,
                'price': current_price,
                'reason': f'Compatibility neutral'
            }
            
        except Exception as e:
            return {
                'signal': 'HOLD',
                'confidence': 0.0,
                'price': 1.0,
                'reason': f'Compatibility error: {str(e)}'
            }

    """Registry to handle strategy name conflicts"""
    
    def __init__(self):
        self.strategies = {}
        self.aliases = {}
    
    def register_strategy(self, name: str, strategy_class, aliases: List[str] = None):
        """Register a strategy with optional aliases"""
        self.strategies[name] = strategy_class
        
        if aliases:
            for alias in aliases:
                self.aliases[alias] = name
    
    def get_strategy(self, name: str):
        """Get strategy by name or alias"""
        # Check direct name first
        if name in self.strategies:
            return self.strategies[name]
        
        # Check aliases
        if name in self.aliases:
            return self.strategies[self.aliases[name]]
        
        return None
    
    def list_strategies(self) -> List[str]:
        """List all available strategies"""
        return list(self.strategies.keys()) + list(self.aliases.keys())

# Global registry
strategy_registry = StrategyRegistry()

def auto_discover_strategies():
    """Auto-discover strategies in your existing files"""
    strategy_modules = [
        'momentum_strategy',
        'rtm_strategy', 
        'ict_strategy',
        'indicator_suite'
    ]
    
    for module_name in strategy_modules:
        try:
        pass
        pass
            module = importlib.import_module(f'.{module_name}', package='strategies')
            
            # Look for strategy classes
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                
                if (isinstance(attr, type) and 
                    hasattr(attr, 'generate_signals') and
                    attr_name != 'BaseStrategy'):
                    
                    # Register with multiple possible names
                    strategy_registry.register_strategy(
                        attr_name, 
                        attr,
                        aliases=[
                            attr_name.replace('Enhanced', ''),
                            attr_name.replace('Strategy', ''),
                            module_name.replace('_strategy', '').upper()
                        ]
                    )
                    print(f"✅ Registered strategy: {attr_name}")
                    
        except Exception as e:
            print(f"⚠️ Could not load {module_name}: {e}")

# Auto-discover on import
auto_discover_strategies()

def get_strategy_class(name: str):
    """Get strategy class by any name"""
    return strategy_registry.get_strategy(name)

def list_available_strategies():
    """List all available strategies"""
    return strategy_registry.list_strategies()
