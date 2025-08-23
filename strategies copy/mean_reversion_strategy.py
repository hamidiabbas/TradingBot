"""
Mean Reversion Strategy Implementation
=====================================
"""

from strategies.base_strategy import BaseStrategy, SignalEvent, register_strategy
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List

@register_strategy
class MeanReversionStrategy(BaseStrategy):
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.bollinger_period = config.get('bb_period', 20)
        self.bollinger_std = config.get('bb_std', 2.0)
        self.rsi_period = config.get('rsi_period', 14)
        
    async def initialize(self) -> bool:
        return True
        
    def generate_signals(self, data: Dict[str, pd.DataFrame]) -> List[SignalEvent]:
        signals = []
        
        for symbol, timeframe_data in data.items():
            if isinstance(timeframe_data, dict):
                for timeframe, df in timeframe_data.items():
                    if len(df) < max(self.bollinger_period, self.rsi_period):
                        continue
                        
                    # Calculate Bollinger Bands
                    sma = df['close'].rolling(self.bollinger_period).mean()
                    std = df['close'].rolling(self.bollinger_period).std()
                    upper_band = sma + (std * self.bollinger_std)
                    lower_band = sma - (std * self.bollinger_std)
                    
                    # Calculate RSI
                    delta = df['close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(self.rsi_period).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(self.rsi_period).mean()
                    rs = gain / loss
                    rsi = 100 - (100 / (1 + rs))
                    
                    current_price = df['close'].iloc[-1]
                    current_rsi = rsi.iloc[-1]
                    
                    # Mean reversion signals
                    if current_price < lower_band.iloc[-1] and current_rsi < 30:
                        signal = SignalEvent(
                            event_type='MEAN_REVERSION_BUY',
                            symbol=symbol,
                            timeframe=timeframe,
                            timestamp=datetime.utcnow(),
                            direction='bullish',
                            strength=0.7,
                            level=current_price,
                            metadata={'rsi': current_rsi, 'bb_position': 'oversold'}
                        )
                        signals.append(signal)
                        
                    elif current_price > upper_band.iloc[-1] and current_rsi > 70:
                        signal = SignalEvent(
                            event_type='MEAN_REVERSION_SELL',
                            symbol=symbol,
                            timeframe=timeframe,
                            timestamp=datetime.utcnow(),
                            direction='bearish',
                            strength=0.7,
                            level=current_price,
                            metadata={'rsi': current_rsi, 'bb_position': 'overbought'}
                        )
                        signals.append(signal)
        
        return signals
        
    def get_required_data(self) -> Dict[str, List[str]]:
        return {'*': ['M15', 'H1']}
        
    def validate_signal(self, signal) -> bool:
        return signal.strength > 0.5
