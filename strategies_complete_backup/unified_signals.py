"""
Unified Signals Module - Complete Professional Version
Provides all necessary functions and classes for strategy integration
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

class SignalType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    STRONG_BUY = "STRONG_BUY"
    STRONG_SELL = "STRONG_SELL"

class UnifiedSignalGenerator:
    """Base signal generator for strategy compatibility"""
    
    def __init__(self, name: str = "UnifiedStrategy"):
        self.name = name
        
    def analyze(self, data: pd.DataFrame, symbol: str = "EURUSD") -> Dict[str, Any]:
        """Standard analyze method for Kelly compatibility"""
        try:
            if data is None or data.empty or len(data) < 10:
                return {
                    'signal': 'HOLD',
                    'confidence': 0.0,
                    'price': 1.0,
                    'reason': 'Insufficient data'
                }
            
            current_price = data['close'].iloc[-1]
            
            # Basic trend analysis
            if len(data) >= 20:
                ma_20 = data['close'].rolling(20).mean().iloc[-1]
                
                if current_price > ma_20 * 1.005:
                    return {
                        'signal': 'BUY',
                        'confidence': 0.65,
                        'price': current_price,
                        'reason': f'{self.name} bullish trend'
                    }
                elif current_price < ma_20 * 0.995:
                    return {
                        'signal': 'SELL',
                        'confidence': 0.65,
                        'price': current_price,
                        'reason': f'{self.name} bearish trend'
                    }
            
            return {
                'signal': 'HOLD',
                'confidence': 0.5,
                'price': current_price,
                'reason': f'{self.name} neutral'
            }
            
        except Exception as e:
            return {
                'signal': 'HOLD',
                'confidence': 0.0,
                'price': 1.0,
                'reason': f'Error: {str(e)}'
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
    try:
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    except:
        return pd.Series([50] * len(data), index=data.index)

def calculate_bollinger_bands(data: pd.Series, period: int = 20, std: float = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Bollinger Bands"""
    try:
        sma = calculate_sma(data, period)
        std_dev = data.rolling(window=period).std()
        upper_band = sma + (std_dev * std)
        lower_band = sma - (std_dev * std)
        return upper_band, sma, lower_band
    except:
        return data, data, data

def calculate_macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """MACD Indicator"""
    try:
        ema_fast = calculate_ema(data, fast)
        ema_slow = calculate_ema(data, slow)
        macd_line = ema_fast - ema_slow
        signal_line = calculate_ema(macd_line, signal)
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    except:
        return data, data, data

def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Average True Range"""
    try:
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return true_range.rolling(window=period).mean()
    except:
        return pd.Series([0.001] * len(high), index=high.index)

def calculate_stochastic(high: pd.Series, low: pd.Series, close: pd.Series, 
                        k_period: int = 14, d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
    """Stochastic Oscillator"""
    try:
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_period).mean()
        return k_percent, d_percent
    except:
        return pd.Series([50] * len(high), index=high.index), pd.Series([50] * len(high), index=high.index)

# Utility Functions
def generate_basic_signal(data: pd.DataFrame, symbol: str = "EURUSD") -> Dict[str, Any]:
    """Generate basic signal for fallback"""
    try:
        if data is None or data.empty or len(data) < 10:
            return {
                'signal': 'HOLD',
                'confidence': 0.0,
                'price': 1.0,
                'reason': 'Insufficient data'
            }
        
        current_price = data['close'].iloc[-1]
        
        # Simple moving average crossover
        if len(data) >= 20:
            ma_10 = calculate_sma(data['close'], 10).iloc[-1]
            ma_20 = calculate_sma(data['close'], 20).iloc[-1]
            
            if ma_10 > ma_20 and current_price > ma_10:
                return {
                    'signal': 'BUY',
                    'confidence': 0.60,
                    'price': current_price,
                    'reason': 'MA crossover bullish'
                }
            elif ma_10 < ma_20 and current_price < ma_10:
                return {
                    'signal': 'SELL',
                    'confidence': 0.60,
                    'price': current_price,
                    'reason': 'MA crossover bearish'
                }
        
        return {
            'signal': 'HOLD',
            'confidence': 0.4,
            'price': current_price,
            'reason': 'No clear signal'
        }
        
    except Exception as e:
        return {
            'signal': 'HOLD',
            'confidence': 0.0,
            'price': 1.0,
            'reason': f'Error: {str(e)}'
        }

# Compatibility functions for legacy code
def normalize_confidence(value: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
    """Normalize value to 0-1 confidence range"""
    try:
        normalized = (value - min_val) / (max_val - min_val)
        return max(0.0, min(1.0, normalized))
    except:
        return 0.5

# Export all necessary components
__all__ = [
    'SignalType', 'UnifiedSignalGenerator',
    'calculate_sma', 'calculate_ema', 'calculate_rsi', 'calculate_bollinger_bands',
    'calculate_macd', 'calculate_atr', 'calculate_stochastic',
    'generate_basic_signal', 'normalize_confidence'
]
