"""
Strategy Compatibility Layer
===========================
Bridges naming conflicts in your existing strategies
"""

from typing import Dict, Any, Optional, List
import importlib
import sys

class StrategyRegistry:
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
