"""
Breakout Strategy Implementation
===============================
"""

from strategies.base_strategy import BaseStrategy, SignalEvent, register_strategy
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List

@register_strategy
class BreakoutStrategy(BaseStrategy):
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.lookback_period = config.get('breakout_lookback', 20)
        self.volume_threshold = config.get('volume_threshold', 1.5)
        
    async def initialize(self) -> bool:
        return True
        
    def generate_signals(self, data: Dict[str, pd.DataFrame]) -> List[SignalEvent]:
        signals = []
        
        for symbol, timeframe_data in data.items():
            if isinstance(timeframe_data, dict):
                for timeframe, df in timeframe_data.items():
                    if len(df) < self.lookback_period:
                        continue
                        
                    # Calculate breakout levels
                    resistance = df['high'].rolling(self.lookback_period).max()
                    support = df['low'].rolling(self.lookback_period).min()
                    
                    current_price = df['close'].iloc[-1]
                    current_resistance = resistance.iloc[-1]
                    current_support = support.iloc[-1]
                    
                    # Volume confirmation
                    volume_confirmed = True
                    if 'volume' in df.columns:
                        avg_volume = df['volume'].rolling(20).mean().iloc[-1]
                        current_volume = df['volume'].iloc[-1]
                        volume_confirmed = current_volume > avg_volume * self.volume_threshold
                    
                    # Breakout signals
                    if current_price > current_resistance and volume_confirmed:
                        signal = SignalEvent(
                            event_type='BREAKOUT_BUY',
                            symbol=symbol,
                            timeframe=timeframe,
                            timestamp=datetime.utcnow(),
                            direction='bullish',
                            strength=0.8,
                            level=current_price,
                            metadata={
                                'resistance_level': current_resistance,
                                'volume_confirmed': volume_confirmed
                            }
                        )
                        signals.append(signal)
                        
                    elif current_price < current_support and volume_confirmed:
                        signal = SignalEvent(
                            event_type='BREAKOUT_SELL',
                            symbol=symbol,
                            timeframe=timeframe,
                            timestamp=datetime.utcnow(),
                            direction='bearish',
                            strength=0.8,
                            level=current_price,
                            metadata={
                                'support_level': current_support,
                                'volume_confirmed': volume_confirmed
                            }
                        )
                        signals.append(signal)
        
        return signals
        
    def get_required_data(self) -> Dict[str, List[str]]:
        return {'*': ['M15', 'H1']}
        
    def validate_signal(self, signal) -> bool:
        return signal.strength > 0.6
