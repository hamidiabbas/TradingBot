from strategies.unified_signals import *
#!/usr/bin/env python3
"""
===============================================================
UNIFIED SIGNALS MODULE - STRATEGY DEPENDENCY FIX
===============================================================
This module provides the missing unified_signals dependency
that many of your strategies require.
===============================================================
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class SignalType(Enum):
    """Standard signal types"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    STRONG_BUY = "STRONG_BUY"
    STRONG_SELL = "STRONG_SELL"

@dataclass
class UnifiedSignal:
    """Unified signal structure for all strategies"""
    signal: SignalType
    confidence: float  # 0.0 to 1.0
    strength: float = 0.0
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    reason: str = ""
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        
        # Ensure confidence is in valid range
        self.confidence = max(0.0, min(1.0, self.confidence))

class UnifiedSignalGenerator:
    """Base class for unified signal generation"""
    
    def __init__(self, name: str = "UnifiedStrategy"):
        self.name = name
        self.signals_generated = 0
        
    def generate_signal(self, data: pd.DataFrame, symbol: str = "EURUSD", 
                       timeframe: str = "H1") -> UnifiedSignal:
        """Generate unified signal - override in subclasses"""
        return UnifiedSignal(
            signal=SignalType.HOLD,
            confidence=0.0,
            reason="Base class - no signal logic"
        )
    
    def analyze(self, data: pd.DataFrame, symbol: str = "EURUSD") -> Dict[str, Any]:
        """Standard analyze method for Kelly system compatibility"""
        try:
            signal = self.generate_signal(data, symbol)
            
            return {
                'signal': signal.signal.value,
                'confidence': signal.confidence,
                'strength': signal.strength,
                'price': signal.entry_price or data['close'].iloc[-1] if not data.empty else 1.0,
                'stop_loss': signal.stop_loss,
                'take_profit': signal.take_profit,
                'reason': signal.reason or f"{self.name} signal",
                'timestamp': signal.timestamp
            }
        except Exception as e:
            return {
                'signal': 'HOLD',
                'confidence': 0.0,
                'strength': 0.0,
                'price': 1.0,
                'reason': f"Error: {str(e)}"
            }

# Technical Analysis Functions
def calculate_sma(data: pd.Series, period: int) -> pd.Series:
    """Simple Moving Average"""
    return data.rolling(window=period).mean()

def calculate_ema(data: pd.Series, period: int) -> pd.Series:
    """Exponential Moving Average"""
    return data.ewm(span=period).mean()

def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
    """Relative Strength Index"""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_bollinger_bands(data: pd.Series, period: int = 20, std: float = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Bollinger Bands"""
    sma = calculate_sma(data, period)
    std_dev = data.rolling(window=period).std()
    upper_band = sma + (std_dev * std)
    lower_band = sma - (std_dev * std)
    return upper_band, sma, lower_band

def calculate_macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """MACD Indicator"""
    ema_fast = calculate_ema(data, fast)
    ema_slow = calculate_ema(data, slow)
    macd_line = ema_fast - ema_slow
    signal_line = calculate_ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Average True Range"""
    high_low = high - low
    high_close = np.abs(high - close.shift())
    low_close = np.abs(low - close.shift())
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return true_range.rolling(window=period).mean()

def calculate_stochastic(high: pd.Series, low: pd.Series, close: pd.Series, 
                        k_period: int = 14, d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
    """Stochastic Oscillator"""
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()
    k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
    d_percent = k_percent.rolling(window=d_period).mean()
    return k_percent, d_percent

# Signal Processing Utilities
def normalize_confidence(value: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
    """Normalize value to 0-1 confidence range"""
    normalized = (value - min_val) / (max_val - min_val)
    return max(0.0, min(1.0, normalized))

def combine_signals(signals: List[UnifiedSignal], weights: Optional[List[float]] = None) -> UnifiedSignal:
    """Combine multiple signals into one"""
    if not signals:
        return UnifiedSignal(signal=SignalType.HOLD, confidence=0.0)
    
    if weights is None:
        weights = [1.0] * len(signals)
    
    # Weight signals
    buy_weight = sum(w for s, w in zip(signals, weights) if s.signal in [SignalType.BUY, SignalType.STRONG_BUY])
    sell_weight = sum(w for s, w in zip(signals, weights) if s.signal in [SignalType.SELL, SignalType.STRONG_SELL])
    hold_weight = sum(w for s, w in zip(signals, weights) if s.signal == SignalType.HOLD)
    
    total_weight = buy_weight + sell_weight + hold_weight
    
    if total_weight == 0:
        return UnifiedSignal(signal=SignalType.HOLD, confidence=0.0)
    
    # Determine final signal
    if buy_weight > sell_weight and buy_weight > hold_weight:
        final_signal = SignalType.BUY
        confidence = buy_weight / total_weight
    elif sell_weight > buy_weight and sell_weight > hold_weight:
        final_signal = SignalType.SELL
        confidence = sell_weight / total_weight
    else:
        final_signal = SignalType.HOLD
        confidence = hold_weight / total_weight if hold_weight > 0 else 0.1
    
    # Average other properties
    avg_strength = np.mean([s.strength for s in signals if s.strength > 0])
    reasons = [s.reason for s in signals if s.reason]
    
    return UnifiedSignal(
        signal=final_signal,
        confidence=confidence,
        strength=avg_strength if not np.isnan(avg_strength) else 0.0,
        reason=" + ".join(reasons[:3])  # Combine first 3 reasons
    )

# Market Condition Detection
def detect_market_trend(data: pd.DataFrame, period: int = 50) -> str:
    """Detect market trend"""
    if len(data) < period:
        return "insufficient_data"
    
    sma = calculate_sma(data['close'], period)
    current_price = data['close'].iloc[-1]
    sma_current = sma.iloc[-1]
    
    if current_price > sma_current * 1.01:
        return "bullish"
    elif current_price < sma_current * 0.99:
        return "bearish"
    else:
        return "sideways"

def detect_volatility_regime(data: pd.DataFrame, period: int = 20) -> str:
    """Detect volatility regime"""
    if len(data) < period:
        return "normal"
    
    returns = data['close'].pct_change().dropna()
    volatility = returns.rolling(window=period).std().iloc[-1]
    
    if volatility > 0.02:
        return "high"
    elif volatility < 0.005:
        return "low"
    else:
        return "normal"

# Compatibility Functions for Legacy Code
def get_signal_strength(signal_type: str, confidence: float) -> float:
    """Convert signal to strength for legacy compatibility"""
    if signal_type in ['BUY', 'SELL']:
        return confidence
    return 0.0

def convert_legacy_signal(signal_dict: Dict[str, Any]) -> UnifiedSignal:
    """Convert legacy signal format to UnifiedSignal"""
    signal_type = signal_dict.get('signal', 'HOLD')
    
    if signal_type == 'BUY':
        unified_signal = SignalType.BUY
    elif signal_type == 'SELL':
        unified_signal = SignalType.SELL
    else:
        unified_signal = SignalType.HOLD
    
    return UnifiedSignal(
        signal=unified_signal,
        confidence=signal_dict.get('confidence', 0.0),
        strength=signal_dict.get('strength', 0.0),
        entry_price=signal_dict.get('price'),
        reason=signal_dict.get('reason', '')
    )

# Export all necessary components
__all__ = [
    'SignalType', 'UnifiedSignal', 'UnifiedSignalGenerator',
    'calculate_sma', 'calculate_ema', 'calculate_rsi', 'calculate_bollinger_bands',
    'calculate_macd', 'calculate_atr', 'calculate_stochastic',
    'normalize_confidence', 'combine_signals',
    'detect_market_trend', 'detect_volatility_regime',
    'get_signal_strength', 'convert_legacy_signal'
]
