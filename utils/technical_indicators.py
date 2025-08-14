"""
Technical indicators utilities for TradingBot v1.0
Provides common technical analysis indicators
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple

def calculate_sma(data: pd.Series, window: int = 20) -> pd.Series:
    """Calculate Simple Moving Average"""
    return data.rolling(window=window, min_periods=1).mean()

def calculate_ema(data: pd.Series, window: int = 20, alpha: Optional[float] = None) -> pd.Series:
    """Calculate Exponential Moving Average"""
    if alpha is None:
        alpha = 2 / (window + 1)
    return data.ewm(alpha=alpha, adjust=False).mean()

def calculate_rsi(data: pd.Series, window: int = 14) -> pd.Series:
    """Calculate Relative Strength Index"""
    try:
        delta = data.diff()
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)
        
        avg_gains = gains.rolling(window=window, min_periods=1).mean()
        avg_losses = losses.rolling(window=window, min_periods=1).mean()
        
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.fillna(50)  # Default neutral RSI
    except Exception as e:
        print(f"Error calculating RSI: {e}")
        return pd.Series([50] * len(data), index=data.index)

def calculate_bollinger_bands(data: pd.Series, window: int = 20, num_std: float = 2) -> Dict[str, pd.Series]:
    """Calculate Bollinger Bands"""
    try:
        sma = calculate_sma(data, window)
        std = data.rolling(window=window, min_periods=1).std()
        
        upper_band = sma + (std * num_std)
        lower_band = sma - (std * num_std)
        
        return {
            'upper': upper_band,
            'middle': sma,
            'lower': lower_band
        }
    except Exception as e:
        print(f"Error calculating Bollinger Bands: {e}")
        return {
            'upper': data,
            'middle': data,
            'lower': data
        }

def calculate_macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
    """Calculate MACD (Moving Average Convergence Divergence)"""
    try:
        ema_fast = calculate_ema(data, fast)
        ema_slow = calculate_ema(data, slow)
        
        macd_line = ema_fast - ema_slow
        signal_line = calculate_ema(macd_line, signal)
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    except Exception as e:
        print(f"Error calculating MACD: {e}")
        return {
            'macd': pd.Series([0] * len(data), index=data.index),
            'signal': pd.Series([0] * len(data), index=data.index),
            'histogram': pd.Series([0] * len(data), index=data.index)
        }

def calculate_stochastic(high: pd.Series, low: pd.Series, close: pd.Series, 
                        k_period: int = 14, d_period: int = 3) -> Dict[str, pd.Series]:
    """Calculate Stochastic Oscillator"""
    try:
        lowest_low = low.rolling(window=k_period, min_periods=1).min()
        highest_high = high.rolling(window=k_period, min_periods=1).max()
        
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_period, min_periods=1).mean()
        
        return {
            '%K': k_percent.fillna(50),
            '%D': d_percent.fillna(50)
        }
    except Exception as e:
        print(f"Error calculating Stochastic: {e}")
        return {
            '%K': pd.Series([50] * len(close), index=close.index),
            '%D': pd.Series([50] * len(close), index=close.index)
        }

def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
    """Calculate Average True Range"""
    try:
        high_low = high - low
        high_close_prev = np.abs(high - close.shift(1))
        low_close_prev = np.abs(low - close.shift(1))
        
        true_range = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
        atr = true_range.rolling(window=window, min_periods=1).mean()
        
        return atr.fillna(0)
    except Exception as e:
        print(f"Error calculating ATR: {e}")
        return pd.Series([0] * len(high), index=high.index)

def calculate_williams_r(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
    """Calculate Williams %R"""
    try:
        highest_high = high.rolling(window=window, min_periods=1).max()
        lowest_low = low.rolling(window=window, min_periods=1).min()
        
        williams_r = -100 * ((highest_high - close) / (highest_high - lowest_low))
        
        return williams_r.fillna(-50)
    except Exception as e:
        print(f"Error calculating Williams %R: {e}")
        return pd.Series([-50] * len(close), index=close.index)

def calculate_momentum(data: pd.Series, window: int = 10) -> pd.Series:
    """Calculate Momentum"""
    try:
        momentum = data.diff(window)
        return momentum.fillna(0)
    except Exception as e:
        print(f"Error calculating Momentum: {e}")
        return pd.Series([0] * len(data), index=data.index)

def calculate_roc(data: pd.Series, window: int = 10) -> pd.Series:
    """Calculate Rate of Change"""
    try:
        roc = ((data - data.shift(window)) / data.shift(window)) * 100
        return roc.fillna(0)
    except Exception as e:
        print(f"Error calculating ROC: {e}")
        return pd.Series([0] * len(data), index=data.index)

def calculate_cci(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 20) -> pd.Series:
    """Calculate Commodity Channel Index"""
    try:
        typical_price = (high + low + close) / 3
        sma_tp = typical_price.rolling(window=window, min_periods=1).mean()
        mean_deviation = typical_price.rolling(window=window, min_periods=1).apply(
            lambda x: np.mean(np.abs(x - np.mean(x)))
        )
        
        cci = (typical_price - sma_tp) / (0.015 * mean_deviation)
        return cci.fillna(0)
    except Exception as e:
        print(f"Error calculating CCI: {e}")
        return pd.Series([0] * len(close), index=close.index)

def calculate_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """Calculate On-Balance Volume"""
    try:
        obv = pd.Series(index=close.index, dtype=float)
        obv.iloc[0] = volume.iloc[0]
        
        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
            elif close.iloc[i] < close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]
        
        return obv
    except Exception as e:
        print(f"Error calculating OBV: {e}")
        return volume.cumsum()

def calculate_vwap(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series) -> pd.Series:
    """Calculate Volume Weighted Average Price"""
    try:
        typical_price = (high + low + close) / 3
        vwap = (typical_price * volume).cumsum() / volume.cumsum()
        return vwap.fillna(typical_price)
    except Exception as e:
        print(f"Error calculating VWAP: {e}")
        return close

def calculate_adx(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
    """Calculate Average Directional Index (simplified)"""
    try:
        # Simplified ADX calculation
        up_move = high - high.shift(1)
        down_move = low.shift(1) - low
        
        plus_dm = pd.Series(np.where((up_move > down_move) & (up_move > 0), up_move, 0), index=high.index)
        minus_dm = pd.Series(np.where((down_move > up_move) & (down_move > 0), down_move, 0), index=high.index)
        
        tr = calculate_atr(high, low, close, window)
        
        plus_di = 100 * (plus_dm.rolling(window=window).sum() / tr)
        minus_di = 100 * (minus_dm.rolling(window=window).sum() / tr)
        
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=window).mean()
        
        return adx.fillna(25)  # Neutral ADX
    except Exception as e:
        print(f"Error calculating ADX: {e}")
        return pd.Series([25] * len(close), index=close.index)

# Export all functions
__all__ = [
    'calculate_sma', 'calculate_ema', 'calculate_rsi', 'calculate_bollinger_bands',
    'calculate_macd', 'calculate_stochastic', 'calculate_atr', 'calculate_williams_r',
    'calculate_momentum', 'calculate_roc', 'calculate_cci', 'calculate_obv',
    'calculate_vwap', 'calculate_adx'
]
# Add this to your existing utils/technical_indicators.py file

class AdvancedTechnicalIndicators:
    """Advanced technical indicators class with comprehensive calculations"""
    
    @staticmethod
    def calculate_ichimoku(high: pd.Series, low: pd.Series, close: pd.Series) -> Dict[str, pd.Series]:
        """Calculate Ichimoku Cloud components"""
        try:
            # Tenkan-sen (9-period high-low average)
            tenkan_high = high.rolling(window=9, min_periods=1).max()
            tenkan_low = low.rolling(window=9, min_periods=1).min()
            tenkan_sen = (tenkan_high + tenkan_low) / 2
            
            # Kijun-sen (26-period high-low average)
            kijun_high = high.rolling(window=26, min_periods=1).max()
            kijun_low = low.rolling(window=26, min_periods=1).min()
            kijun_sen = (kijun_high + kijun_low) / 2
            
            # Senkou Span A (Tenkan + Kijun)/2 shifted forward 26 periods
            senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)
            
            # Senkou Span B (52-period high-low average) shifted forward 26 periods
            senkou_high = high.rolling(window=52, min_periods=1).max()
            senkou_low = low.rolling(window=52, min_periods=1).min()
            senkou_span_b = ((senkou_high + senkou_low) / 2).shift(26)
            
            # Chikou Span (close shifted back 26 periods)
            chikou_span = close.shift(-26)
            
            return {
                'tenkan_sen': tenkan_sen,
                'kijun_sen': kijun_sen,
                'senkou_span_a': senkou_span_a,
                'senkou_span_b': senkou_span_b,
                'chikou_span': chikou_span
            }
            
        except Exception as e:
            print(f"Error calculating Ichimoku: {e}")
            return {k: pd.Series([0] * len(close), index=close.index) 
                   for k in ['tenkan_sen', 'kijun_sen', 'senkou_span_a', 'senkou_span_b', 'chikou_span']}
    
    @staticmethod
    def calculate_supertrend(high: pd.Series, low: pd.Series, close: pd.Series, 
                           period: int = 10, multiplier: float = 3.0) -> Dict[str, pd.Series]:
        """Calculate SuperTrend indicator"""
        try:
            # Calculate ATR
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = true_range.rolling(window=period, min_periods=1).mean()
            
            # Calculate basic bands
            hl2 = (high + low) / 2
            upper_band = hl2 + (multiplier * atr)
            lower_band = hl2 - (multiplier * atr)
            
            # Calculate SuperTrend
            supertrend = pd.Series(index=close.index, dtype=float)
            direction = pd.Series(index=close.index, dtype=int)
            
            for i in range(len(close)):
                if i == 0:
                    supertrend.iloc[i] = lower_band.iloc[i]
                    direction.iloc[i] = 1
                else:
                    if close.iloc[i] <= supertrend.iloc[i-1]:
                        supertrend.iloc[i] = upper_band.iloc[i]
                        direction.iloc[i] = -1
                    else:
                        supertrend.iloc[i] = lower_band.iloc[i]
                        direction.iloc[i] = 1
            
            return {
                'supertrend': supertrend,
                'direction': direction,
                'upper_band': upper_band,
                'lower_band': lower_band
            }
            
        except Exception as e:
            print(f"Error calculating SuperTrend: {e}")
            return {k: pd.Series([0] * len(close), index=close.index) 
                   for k in ['supertrend', 'direction', 'upper_band', 'lower_band']}
    
    @staticmethod
    def calculate_donchian_channels(high: pd.Series, low: pd.Series, period: int = 20) -> Dict[str, pd.Series]:
        """Calculate Donchian Channels"""
        try:
            upper_channel = high.rolling(window=period, min_periods=1).max()
            lower_channel = low.rolling(window=period, min_periods=1).min()
            middle_channel = (upper_channel + lower_channel) / 2
            
            return {
                'upper': upper_channel,
                'middle': middle_channel,
                'lower': lower_channel
            }
            
        except Exception as e:
            print(f"Error calculating Donchian Channels: {e}")
            return {k: pd.Series([0] * len(high), index=high.index) 
                   for k in ['upper', 'middle', 'lower']}
    
    @staticmethod
    def calculate_parabolic_sar(high: pd.Series, low: pd.Series, close: pd.Series,
                               af_start: float = 0.02, af_increment: float = 0.02, af_max: float = 0.2) -> pd.Series:
        """Calculate Parabolic SAR"""
        try:
            sar = pd.Series(index=close.index, dtype=float)
            af = af_start
            ep = high.iloc[0]
            trend = 1  # 1 for uptrend, -1 for downtrend
            
            sar.iloc[0] = low.iloc[0]
            
            for i in range(1, len(close)):
                if trend == 1:  # Uptrend
                    sar.iloc[i] = sar.iloc[i-1] + af * (ep - sar.iloc[i-1])
                    
                    if high.iloc[i] > ep:
                        ep = high.iloc[i]
                        af = min(af + af_increment, af_max)
                    
                    if low.iloc[i] <= sar.iloc[i]:
                        trend = -1
                        sar.iloc[i] = ep
                        af = af_start
                        ep = low.iloc[i]
                        
                else:  # Downtrend
                    sar.iloc[i] = sar.iloc[i-1] + af * (ep - sar.iloc[i-1])
                    
                    if low.iloc[i] < ep:
                        ep = low.iloc[i]
                        af = min(af + af_increment, af_max)
                    
                    if high.iloc[i] >= sar.iloc[i]:
                        trend = 1
                        sar.iloc[i] = ep
                        af = af_start
                        ep = high.iloc[i]
            
            return sar.fillna(method='ffill')
            
        except Exception as e:
            print(f"Error calculating Parabolic SAR: {e}")
            return pd.Series([0] * len(close), index=close.index)

# Export the class
__all__.append('AdvancedTechnicalIndicators')
