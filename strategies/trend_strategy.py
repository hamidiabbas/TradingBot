import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple

class MultiFacetTrendStrategy:
    """Multi-indicator trend following strategy"""
    
    def __init__(self):
        self.name = "MultiFacetTrendStrategy"
        self.fast_ma = 12
        self.slow_ma = 26
        self.signal_ma = 9
        self.rsi_period = 14
        self.adx_period = 14
        self.min_trend_strength = 25
        
    def analyze(self, data: pd.DataFrame, symbol: str = "EURUSD") -> Dict[str, Any]:
        try:
            if len(data) < max(self.slow_ma, self.adx_period) + 10:
                return self._no_signal(data, "Insufficient data for trend analysis")
                
            current_price = data['close'].iloc[-1]
            
            # Multiple trend confirmations
            macd_signal = self._calculate_macd_signal(data)
            rsi_trend = self._calculate_rsi_trend(data)
            adx_strength = self._calculate_adx(data)
            ema_alignment = self._check_ema_alignment(data)
            price_momentum = self._calculate_momentum(data)
            
            # Volume confirmation
            volume_trend = self._analyze_volume_trend(data)
            
            # Combine all signals
            bullish_signals = sum([
                macd_signal > 0,
                rsi_trend == 'bullish',
                adx_strength > self.min_trend_strength,
                ema_alignment == 'bullish',
                price_momentum > 0.002,
                volume_trend == 'increasing'
            ])
            
            bearish_signals = sum([
                macd_signal < 0,
                rsi_trend == 'bearish',
                adx_strength > self.min_trend_strength,
                ema_alignment == 'bearish',
                price_momentum < -0.002,
                volume_trend == 'increasing'
            ])
            
            # Signal strength based on confluence
            if bullish_signals >= 4:  # Need at least 4/6 confirmations
                confidence = 0.6 + (bullish_signals - 4) * 0.05
                atr = self._calculate_atr(data)
                
                return {
                    'signal': 'BUY',
                    'confidence': min(confidence, 0.9),
                    'price': current_price,
                    'reason': f'Strong bullish confluence: {bullish_signals}/6 signals, ADX: {adx_strength:.1f}',
                    'stop_loss': current_price - atr * 2.0,
                    'take_profit': current_price + atr * 3.0,
                    'adx_strength': adx_strength,
                    'momentum': price_momentum
                }
                
            elif bearish_signals >= 4:
                confidence = 0.6 + (bearish_signals - 4) * 0.05
                atr = self._calculate_atr(data)
                
                return {
                    'signal': 'SELL',
                    'confidence': min(confidence, 0.9),
                    'price': current_price,
                    'reason': f'Strong bearish confluence: {bearish_signals}/6 signals, ADX: {adx_strength:.1f}',
                    'stop_loss': current_price + atr * 2.0,
                    'take_profit': current_price - atr * 3.0,
                    'adx_strength': adx_strength,
                    'momentum': price_momentum
                }
            
            return self._no_signal(data, f"Insufficient confluence: Bull={bullish_signals}, Bear={bearish_signals}")
            
        except Exception as e:
            return self._no_signal(data, f"Trend analysis error: {str(e)}")
    
    def _calculate_macd_signal(self, data):
        """Calculate MACD signal"""
        exp1 = data['close'].ewm(span=self.fast_ma).mean()
        exp2 = data['close'].ewm(span=self.slow_ma).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=self.signal_ma).mean()
        histogram = macd - signal
        return histogram.iloc[-1]
    
    def _calculate_rsi_trend(self, data):
        """Calculate RSI trend"""
        delta = data['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=self.rsi_period).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=self.rsi_period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = rsi.iloc[-1]
        prev_rsi = rsi.iloc[-2]
        
        if current_rsi > prev_rsi and current_rsi > 50:
            return 'bullish'
        elif current_rsi < prev_rsi and current_rsi < 50:
            return 'bearish'
        else:
            return 'neutral'
    
    def _calculate_adx(self, data):
        """Calculate ADX for trend strength"""
        high = data['high']
        low = data['low']
        close = data['close']
        
        # True Range
        tr1 = high - low
        tr2 = np.abs(high - close.shift(1))
        tr3 = np.abs(low - close.shift(1))
        tr = np.maximum(tr1, np.maximum(tr2, tr3))
        
        # Directional Movement
        plus_dm = np.where((high - high.shift(1)) > (low.shift(1) - low), 
                          np.maximum(high - high.shift(1), 0), 0)
        minus_dm = np.where((low.shift(1) - low) > (high - high.shift(1)), 
                           np.maximum(low.shift(1) - low, 0), 0)
        
        # Smoothed values
        tr_smooth = tr.rolling(window=self.adx_period).mean()
        plus_di = 100 * (plus_dm.rolling(window=self.adx_period).mean() / tr_smooth)
        minus_di = 100 * (minus_dm.rolling(window=self.adx_period).mean() / tr_smooth)
        
        # ADX calculation
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=self.adx_period).mean()
        
        return adx.iloc[-1]
    
    def _check_ema_alignment(self, data):
        """Check EMA alignment for trend direction"""
        ema_short = data['close'].ewm(span=8).mean()
        ema_medium = data['close'].ewm(span=21).mean()
        ema_long = data['close'].ewm(span=50).mean()
        
        current_short = ema_short.iloc[-1]
        current_medium = ema_medium.iloc[-1]
        current_long = ema_long.iloc[-1]
        
        if current_short > current_medium > current_long:
            return 'bullish'
        elif current_short < current_medium < current_long:
            return 'bearish'
        else:
            return 'mixed'
    
    def _calculate_momentum(self, data, period=10):
        """Calculate price momentum"""
        if len(data) < period:
            return 0.0
        current = data['close'].iloc[-1]
        past = data['close'].iloc[-period]
        return (current - past) / past
    
    def _analyze_volume_trend(self, data, period=10):
        """Analyze volume trend"""
        if 'volume' not in data.columns:
            return 'neutral'
            
        recent_volume = data['volume'].rolling(period//2).mean().iloc[-1]
        older_volume = data['volume'].rolling(period).mean().iloc[-period//2]
        
        if recent_volume > older_volume * 1.2:
            return 'increasing'
        elif recent_volume < older_volume * 0.8:
            return 'decreasing'
        else:
            return 'stable'
    
    def _calculate_atr(self, data, period=14):
        """Calculate Average True Range"""
        high = data['high']
        low = data['low']
        close = data['close']
        
        tr1 = high - low
        tr2 = np.abs(high - close.shift(1))
        tr3 = np.abs(low - close.shift(1))
        
        true_range = np.maximum(tr1, np.maximum(tr2, tr3))
        return true_range.rolling(window=period).mean().iloc[-1]
    
    def _no_signal(self, data, reason):
        return {
            'signal': 'BUY' if data['close'].iloc[-1] > data['close'].rolling(10).mean().iloc[-1] else 'SELL',
            'confidence': 0.0,
            'price': data['close'].iloc[-1] if not data.empty else 1.0,
            'reason': reason
        }
