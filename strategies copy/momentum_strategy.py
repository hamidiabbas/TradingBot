"""
Momentum Strategy Implementation
===============================
"""

from strategies.base_strategy import BaseStrategy, SignalEvent, register_strategy
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List

@register_strategy
class MomentumStrategy(BaseStrategy):
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.lookback_period = config.get('momentum_lookback', 14)
        self.threshold = config.get('momentum_threshold', 0.02)
        
    async def initialize(self) -> bool:
        return True
        
    def generate_signals(self, data: Dict[str, pd.DataFrame]) -> List[SignalEvent]:
        signals = []
        
        for symbol, timeframe_data in data.items():
            if isinstance(timeframe_data, dict):
                for timeframe, df in timeframe_data.items():
                    if len(df) < self.lookback_period:
                        continue
                        
                    # Calculate momentum
                    returns = df['close'].pct_change(self.lookback_period)
                    current_momentum = returns.iloc[-1]
                    
                    if abs(current_momentum) > self.threshold:
                        direction = 'bullish' if current_momentum > 0 else 'bearish'
                        
                        signal = SignalEvent(
                            event_type='MOMENTUM_SIGNAL',
                            symbol=symbol,
                            timeframe=timeframe,
                            timestamp=datetime.utcnow(),
                            direction=direction,
                            strength=min(1.0, abs(current_momentum) / (self.threshold * 2)),
                            level=df['close'].iloc[-1],
                            metadata={'momentum_value': current_momentum}
                        )
                        signals.append(signal)
        
        return signals
        
    def get_required_data(self) -> Dict[str, List[str]]:
        return {'*': ['M15', 'H1']}
        
    def validate_signal(self, signal) -> bool:
        return signal.strength > 0.5
