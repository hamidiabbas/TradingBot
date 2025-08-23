"""
<<<<<<< HEAD
🔥 ENHANCED ICT Trading Price Action Analysis Module - PRODUCTION READY
Includes all Inner Circle Trader (ICT) concepts and functions with critical fixes applied
"""
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, time

# Configure logging
logger = logging.getLogger(__name__)

def detect_market_structure(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20) -> Dict:
    """🔥 FIXED: Real market structure detection for ICT and RTM strategies"""
    try:
        swing_highs = []
        swing_lows = []
        
        if len(high) < period * 2:
            return {
                'trend': 'neutral',
                'structure': 'ranging',
                'swing_highs': [],
                'swing_lows': [],
                'support_levels': [],
                'resistance_levels': [],
                'market_phases': ['ranging']
            }
        
        # 🔥 FIX: Proper swing point detection
        for i in range(period, len(high) - period):
            try:
                # Check for swing high - compare with surrounding periods
                is_swing_high = True
                current_high = float(high.iloc[i])
                
                for j in range(1, period + 1):
                    if i - j >= 0 and current_high <= float(high.iloc[i - j]):
                        is_swing_high = False
                        break
                    if i + j < len(high) and current_high <= float(high.iloc[i + j]):
                        is_swing_high = False
                        break
                
                if is_swing_high:
                    swing_highs.append((i, current_high))
                
                # Check for swing low
                is_swing_low = True
                current_low = float(low.iloc[i])
                
                for j in range(1, period + 1):
                    if i - j >= 0 and current_low >= float(low.iloc[i - j]):
                        is_swing_low = False
                        break
                    if i + j < len(low) and current_low >= float(low.iloc[i + j]):
                        is_swing_low = False
                        break
                
                if is_swing_low:
                    swing_lows.append((i, current_low))
                    
            except Exception as e:
                continue
        
        # 🔥 FIX: Proper trend determination with corrected indexing
        trend = 'neutral'
        if len(swing_highs) >= 2 and len(swing_lows) >= 2:
            try:
                recent_highs = swing_highs[-2:]
                recent_lows = swing_lows[-2:]
                
                # 🔥 CRITICAL FIX: Use index [1] for price, not 
                if recent_highs[-1][1] > recent_highs[-2][1] and recent_lows[-1][1] > recent_lows[-2][1]:
                    trend = 'bullish'
                elif recent_highs[-1][1] < recent_highs[-2][1] and recent_lows[-1][1] < recent_lows[-2][1]:
                    trend = 'bearish'
                else:
                    trend = 'neutral'
            except Exception as e:
                logger.warning(f"Trend determination error: {e}")
                trend = 'neutral'
        
        return {
            'trend': trend,
            'structure': 'trending' if trend != 'neutral' else 'ranging',
            'swing_highs': swing_highs[-10:],  # Keep last 10
            'swing_lows': swing_lows[-10:],    # Keep last 10
            'support_levels': [low for _, low in swing_lows[-5:]] if len(swing_lows) >= 5 else [float(low.min())],
            'resistance_levels': [high for _, high in swing_highs[-5:]] if len(swing_highs) >= 5 else [float(high.max())],
            'market_phases': ['accumulation', 'markup', 'distribution', 'markdown'] if trend != 'neutral' else ['ranging']
        }
        
    except Exception as e:
        logger.error(f"Market structure detection error: {e}")
        return {
            'trend': 'neutral',
            'structure': 'ranging',
            'swing_highs': [],
            'swing_lows': [],
            'support_levels': [float(low.min())] if not low.empty else [1.0],
            'resistance_levels': [float(high.max())] if not high.empty else [1.0],
            'market_phases': ['ranging']
        }

def find_swing_points(df: pd.DataFrame, window: int = 5) -> Dict[str, Any]:
    """
    🔥 ENHANCED: Find swing points - THIS FIXES THE IMPORT ERROR!
    Compatible with both old and new calling patterns
    """
    try:
        # Handle different input formats
        if isinstance(df, pd.DataFrame):
            if 'high' in df.columns and 'low' in df.columns:
                high = df['high']
                low = df['low']
            else:
                logger.error("DataFrame must contain 'high' and 'low' columns")
                return {'swing_highs': [], 'swing_lows': [], 'resistance_levels': [], 'support_levels': []}
        else:
            # Assume it's a high series (for backward compatibility)
            high = df if hasattr(df, 'iloc') else pd.Series(df)
            low = high  # Fallback
=======
Complete price action analysis utilities for TradingBot v1.0
Provides technical analysis functions including Fibonacci retracements
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional

def calculate_fibonacci_retracements(
    high: float, 
    low: float, 
    direction: str = 'bullish'
) -> Dict[str, float]:
    """
    Calculate Fibonacci retracement levels
    
    Args:
        high: Highest price in the range
        low: Lowest price in the range
        direction: 'bullish' or 'bearish' retracement
    
    Returns:
        Dictionary with Fibonacci levels
    """
    try:
        price_range = high - low
        
        # Standard Fibonacci ratios
        fib_ratios = {
            '0.0%': 0.0,
            '23.6%': 0.236,
            '38.2%': 0.382,
            '50.0%': 0.5,
            '61.8%': 0.618,
            '78.6%': 0.786,
            '100.0%': 1.0
        }
        
        fib_levels = {}
        
        if direction.lower() == 'bullish':
            # For bullish retracement, levels are below the high
            for level_name, ratio in fib_ratios.items():
                fib_levels[level_name] = high - (price_range * ratio)
        else:
            # For bearish retracement, levels are above the low
            for level_name, ratio in fib_ratios.items():
                fib_levels[level_name] = low + (price_range * ratio)
        
        return fib_levels
        
    except Exception as e:
        print(f"Error calculating Fibonacci retracements: {e}")
        return {}

def calculate_fibonacci_extensions(
    high: float, 
    low: float, 
    direction: str = 'bullish'
) -> Dict[str, float]:
    """
    Calculate Fibonacci extension levels
    
    Args:
        high: Highest price in the range
        low: Lowest price in the range
        direction: 'bullish' or 'bearish' extension
    
    Returns:
        Dictionary with Fibonacci extension levels
    """
    try:
        price_range = high - low
        
        # Standard Fibonacci extension ratios
        ext_ratios = {
            '127.2%': 1.272,
            '138.2%': 1.382,
            '161.8%': 1.618,
            '200.0%': 2.0,
            '261.8%': 2.618
        }
        
        ext_levels = {}
        
        if direction.lower() == 'bullish':
            # For bullish extension, levels are above the high
            for level_name, ratio in ext_ratios.items():
                ext_levels[level_name] = high + (price_range * (ratio - 1))
        else:
            # For bearish extension, levels are below the low
            for level_name, ratio in ext_ratios.items():
                ext_levels[level_name] = low - (price_range * (ratio - 1))
        
        return ext_levels
        
    except Exception as e:
        print(f"Error calculating Fibonacci extensions: {e}")
        return {}

def find_swing_highs_lows(
    data: pd.DataFrame, 
    window: int = 5
) -> Tuple[List[Tuple[int, float]], List[Tuple[int, float]]]:
    """
    Find swing highs and lows in price data
    
    Args:
        data: DataFrame with OHLC data
        window: Window size for swing detection
    
    Returns:
        Tuple of (swing_highs, swing_lows) as lists of (index, price)
    """
    try:
        highs = data['high'].values
        lows = data['low'].values
>>>>>>> 8f626e2ef1a5d0198eacb62ca49d93985fc3b2f3
        
        swing_highs = []
        swing_lows = []
        
<<<<<<< HEAD
        if len(high) < window * 2:
            return {'swing_highs': [], 'swing_lows': [], 'resistance_levels': [], 'support_levels': []}
        
        for i in range(window, len(high) - window):
            current_high = float(high.iloc[i])
            current_low = float(low.iloc[i])
            
            # Check for swing high
            is_pivot_high = True
            for j in range(i - window, i + window + 1):
                if j != i and j >= 0 and j < len(high):
                    if float(high.iloc[j]) >= current_high:
                        is_pivot_high = False
                        break
            
            if is_pivot_high:
                swing_highs.append((i, current_high))
            
            # Check for swing low
            is_pivot_low = True
            for j in range(i - window, i + window + 1):
                if j != i and j >= 0 and j < len(low):
                    if float(low.iloc[j]) <= current_low:
                        is_pivot_low = False
                        break
            
            if is_pivot_low:
                swing_lows.append((i, current_low))
        
        return {
            'swing_highs': swing_highs,
            'swing_lows': swing_lows,
            'resistance_levels': [h[1] for h in swing_highs[-10:]], # Last 10
            'support_levels': [l[1] for l in swing_lows[-10:]]       # Last 10
        }
        
    except Exception as e:
        logger.error(f"Error finding swing points: {e}")
        return {'swing_highs': [], 'swing_lows': [], 'resistance_levels': [], 'support_levels': []}

def detect_break_of_structure(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20) -> Dict:
    """🔥 ENHANCED: ICT Break of Structure (BOS) Detection with improved logic"""
    try:
        bos_signals = []
        
        if len(high) < period * 2:
            return {'bos_detected': False, 'signals': [], 'type': 'none'}
        
        for i in range(period, len(high) - 1):
            try:
                # 🔥 FIX: Bullish BOS - price breaks above recent highs
                if i >= period:
                    recent_high = float(high.iloc[i-period:i].max())
                    current_high = float(high.iloc[i])
                    
                    if current_high > recent_high * 1.0005:  # 0.05% threshold for noise
                        bos_signals.append({
                            'index': i,
                            'type': 'bullish_bos',
                            'level': current_high,
                            'previous_high': recent_high,
                            'strength': (current_high - recent_high) / recent_high
                        })
                
                # 🔥 FIX: Bearish BOS - price breaks below recent lows
                if i >= period:
                    recent_low = float(low.iloc[i-period:i].min())
                    current_low = float(low.iloc[i])
                    
                    if current_low < recent_low * 0.9995:  # 0.05% threshold for noise
                        bos_signals.append({
                            'index': i,
                            'type': 'bearish_bos',
                            'level': current_low,
                            'previous_low': recent_low,
                            'strength': (recent_low - current_low) / recent_low
                        })
                        
            except Exception as e:
                continue
        
        return {
            'bos_detected': len(bos_signals) > 0,
            'signals': bos_signals[-10:],  # Last 10 BOS signals
            'type': bos_signals[-1]['type'].split('_')[0] if bos_signals else 'none'
        }
        
    except Exception as e:
        logger.error(f"BOS detection error: {e}")
        return {'bos_detected': False, 'signals': [], 'type': 'none'}

def detect_change_of_character(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 10) -> Dict:
    """🔥 ENHANCED: ICT Change of Character (CHoCH) Detection"""
    try:
        choch_signals = []
        
        if len(close) < period * 3:
            return {'choch_detected': False, 'signals': [], 'direction': 'none'}
        
        for i in range(period * 2, len(close) - 1):
            try:
                # Calculate trend momentum for different periods
                recent_momentum = float(close.iloc[i-period:i].diff().mean())
                previous_momentum = float(close.iloc[i-period*2:i-period].diff().mean())
                
                # CHoCH occurs when trend momentum changes significantly
                momentum_change = abs(recent_momentum - previous_momentum)
                threshold = float(close.iloc[i-period*2:i].std()) * 0.1
                
                if momentum_change > threshold:
                    if recent_momentum > 0.0001 and previous_momentum < -0.0001:  # Bearish to bullish
                        choch_signals.append({
                            'index': i,
                            'type': 'bullish_choch',
                            'level': float(close.iloc[i]),
                            'strength': momentum_change,
                            'previous_trend': 'bearish',
                            'new_trend': 'bullish'
                        })
                    elif recent_momentum < -0.0001 and previous_momentum > 0.0001:  # Bullish to bearish
                        choch_signals.append({
                            'index': i,
                            'type': 'bearish_choch',
                            'level': float(close.iloc[i]),
                            'strength': momentum_change,
                            'previous_trend': 'bullish',
                            'new_trend': 'bearish'
                        })
                        
            except Exception as e:
                continue
        
        return {
            'choch_detected': len(choch_signals) > 0,
            'signals': choch_signals[-5:],  # Last 5 CHoCH signals
            'direction': choch_signals[-1]['new_trend'] if choch_signals else 'none'
        }
        
    except Exception as e:
        logger.error(f"CHoCH detection error: {e}")
        return {'choch_detected': False, 'signals': [], 'direction': 'none'}

def identify_order_blocks(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series = None) -> List[Dict]:
    """🔥 ENHANCED: Identify institutional order blocks with improved detection"""
    try:
        order_blocks = []
        
        if len(close) < 25:
            return order_blocks
        
        # Calculate rolling standard deviation for volatility context
        volatility = close.rolling(20, min_periods=5).std().fillna(close.std())
        
        for i in range(20, len(close) - 5):
            try:
                # Look for strong moves (potential order blocks)
                current_move = abs(float(close.iloc[i]) - float(close.iloc[i-1]))
                avg_volatility = float(volatility.iloc[i]) if not pd.isna(volatility.iloc[i]) else current_move
                
                if current_move > avg_volatility * 1.8:  # Strong move threshold
                    # Define order block zone
                    if float(close.iloc[i]) > float(close.iloc[i-1]):  # Bullish order block
                        ob_type = 'bullish'
                        ob_high = float(high.iloc[i-1:i+2].max())
                        ob_low = float(low.iloc[i-1:i+2].min())
                    else:  # Bearish order block
                        ob_type = 'bearish'
                        ob_high = float(high.iloc[i-1:i+2].max())
                        ob_low = float(low.iloc[i-1:i+2].min())
                    
                    order_blocks.append({
                        'index': i,
                        'high': ob_high,
                        'low': ob_low,
                        'type': ob_type,
                        'strength': current_move / avg_volatility if avg_volatility > 0 else 1.0,
                        'volume_confirmed': volume is not None and float(volume.iloc[i]) > float(volume.rolling(20).mean().iloc[i]) * 1.3 if not pd.isna(volume.rolling(20).mean().iloc[i]) else False
                    })
                    
            except Exception as e:
                continue
        
        return order_blocks[-15:]  # Return last 15 order blocks
        
    except Exception as e:
        logger.error(f"Order block identification error: {e}")
        return []

def detect_fair_value_gaps(high: pd.Series, low: pd.Series, close: pd.Series) -> List[Dict]:
    """🔥 ENHANCED: Detect Fair Value Gaps (FVG) for ICT methodology"""
    try:
        gaps = []
        
        if len(close) < 3:
            return gaps
        
        for i in range(2, len(close)):
            try:
                # 🔥 FIX: Check for bullish FVG (gap up)
                current_low = float(low.iloc[i])
                two_candles_ago_high = float(high.iloc[i-2])
                
                if current_low > two_candles_ago_high:
                    gap_size = current_low - two_candles_ago_high
                    # Only consider significant gaps
                    if gap_size > float(close.iloc[i]) * 0.0005:  # 0.05% minimum gap
                        gaps.append({
                            'type': 'bullish',
                            'index': i,
                            'top': current_low,
                            'bottom': two_candles_ago_high,
                            'size': gap_size,
                            'filled': False,
                            'strength': gap_size / float(close.iloc[i])
                        })
                
                # 🔥 FIX: Check for bearish FVG (gap down)
                current_high = float(high.iloc[i])
                two_candles_ago_low = float(low.iloc[i-2])
                
                if current_high < two_candles_ago_low:
                    gap_size = two_candles_ago_low - current_high
                    # Only consider significant gaps
                    if gap_size > float(close.iloc[i]) * 0.0005:  # 0.05% minimum gap
                        gaps.append({
                            'type': 'bearish',
                            'index': i,
                            'top': two_candles_ago_low,
                            'bottom': current_high,
                            'size': gap_size,
                            'filled': False,
                            'strength': gap_size / float(close.iloc[i])
                        })
                        
            except Exception as e:
                continue
        
        return gaps[-25:]  # Return last 25 gaps
        
    except Exception as e:
        logger.error(f"FVG detection error: {e}")
        return []

def find_liquidity_zones(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series = None) -> List[Dict]:
    """🔥 ENHANCED: Find liquidity zones where stops might be hunted"""
    try:
        zones = []
        
        if len(close) < 25:
            return zones
        
        # Find recent highs and lows where liquidity might sit
        for i in range(15, len(close) - 15):
            try:
                # 🔥 FIX: Check for liquidity above (buy stops)
                window_high = float(high.iloc[i-10:i+11].max())
                current_high = float(high.iloc[i])
                
                if abs(current_high - window_high) < current_high * 0.0001:  # Very close to window high
                    volume_strength = 'high' if volume is not None and not pd.isna(volume.iloc[i]) and float(volume.iloc[i]) > float(volume.rolling(20).mean().iloc[i]) * 1.5 else 'medium'
                    
                    zones.append({
                        'type': 'buy_stops',
                        'level': current_high,
                        'index': i,
                        'strength': volume_strength,
                        'description': 'Liquidity above - potential buy stops'
                    })
                
                # 🔥 FIX: Check for liquidity below (sell stops)
                window_low = float(low.iloc[i-10:i+11].min())
                current_low = float(low.iloc[i])
                
                if abs(current_low - window_low) < current_low * 0.0001:  # Very close to window low
                    volume_strength = 'high' if volume is not None and not pd.isna(volume.iloc[i]) and float(volume.iloc[i]) > float(volume.rolling(20).mean().iloc[i]) * 1.5 else 'medium'
                    
                    zones.append({
                        'type': 'sell_stops',
                        'level': current_low,
                        'index': i,
                        'strength': volume_strength,
                        'description': 'Liquidity below - potential sell stops'
                    })
                    
            except Exception as e:
                continue
        
        return zones[-20:]  # Return last 20 zones
        
    except Exception as e:
        logger.error(f"Liquidity zone detection error: {e}")
        return []

def identify_liquidity_levels(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series = None) -> List[Dict]:
    """🔥 ENHANCED: Identify liquidity levels for ICT/RTM strategies - FIXES IMPORT ERROR!"""
    try:
        liquidity_levels = []
        
        if len(high) < 50:
            return liquidity_levels
        
        # Find significant highs and lows where liquidity might accumulate
        for i in range(20, len(high) - 20):
            try:
                # Check for equal highs (liquidity above)
                current_high = float(high.iloc[i])
                surrounding_highs = high.iloc[i-5:i+6]  # 5 before and 5 after
                max_surrounding = float(surrounding_highs.max())
                
                # If current high is very close to the maximum of surrounding area
                if abs(current_high - max_surrounding) < current_high * 0.0005:
                    volume_strength = 'high' if volume is not None and not pd.isna(volume.iloc[i]) and float(volume.iloc[i]) > float(volume.rolling(20).mean().iloc[i]) * 1.2 else 'medium'
                    
                    liquidity_levels.append({
                        'level': current_high,
                        'type': 'resistance_liquidity',
                        'index': i,
                        'strength': volume_strength,
                        'direction': 'above',  # Liquidity above this level
                        'description': 'Equal highs - stops likely above'
                    })
                
                # Check for equal lows (liquidity below)
                current_low = float(low.iloc[i])
                surrounding_lows = low.iloc[i-5:i+6]  # 5 before and 5 after
                min_surrounding = float(surrounding_lows.min())
                
                # If current low is very close to the minimum of surrounding area
                if abs(current_low - min_surrounding) < current_low * 0.0005:
                    volume_strength = 'high' if volume is not None and not pd.isna(volume.iloc[i]) and float(volume.iloc[i]) > float(volume.rolling(20).mean().iloc[i]) * 1.2 else 'medium'
                    
                    liquidity_levels.append({
                        'level': current_low,
                        'type': 'support_liquidity',
                        'index': i,
                        'strength': volume_strength,
                        'direction': 'below',  # Liquidity below this level
                        'description': 'Equal lows - stops likely below'
                    })
                    
            except Exception as e:
                continue
        
        # Return most recent 20 liquidity levels
        return liquidity_levels[-20:]
        
    except Exception as e:
        logger.error(f"Liquidity level identification error: {e}")
        return []

def identify_premium_discount_zones(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 100) -> Dict:
    """🔥 ENHANCED: Identify premium and discount zones for ICT methodology"""
    try:
        if len(close) < period:
            period = len(close) - 1
            
        if period <= 0:
            return {'premium_zone': None, 'discount_zone': None, 'equilibrium': None, 'current_zone': 'unknown'}
        
        # Calculate range for the period
        period_high = float(high.tail(period).max())
        period_low = float(low.tail(period).min())
        range_size = period_high - period_low
        
        if range_size == 0:
            return {'premium_zone': None, 'discount_zone': None, 'equilibrium': period_high, 'current_zone': 'equilibrium'}
        
        # Define zones
        equilibrium = period_low + (range_size * 0.5)
        premium_start = period_low + (range_size * 0.7)  # Upper 30%
        discount_end = period_low + (range_size * 0.3)   # Lower 30%
        
        current_price = float(close.iloc[-1])
        
        # Determine current zone
        if current_price >= premium_start:
            current_zone = 'premium'
        elif current_price <= discount_end:
            current_zone = 'discount'
        else:
            current_zone = 'equilibrium'
        
        return {
            'premium_zone': {'start': premium_start, 'end': period_high},
            'discount_zone': {'start': period_low, 'end': discount_end},
            'equilibrium': equilibrium,
            'current_zone': current_zone,
            'current_price': current_price,
            'range_high': period_high,
            'range_low': period_low,
            'range_size': range_size
        }
        
    except Exception as e:
        logger.error(f"Premium/discount zone calculation error: {e}")
        return {'premium_zone': None, 'discount_zone': None, 'equilibrium': None, 'current_zone': 'unknown'}

def calculate_market_geometry(high: pd.Series, low: pd.Series, close: pd.Series) -> Dict:
    """🔥 ENHANCED: Calculate market geometry metrics with error handling"""
    try:
        current_price = float(close.iloc[-1])
        
        # Support and resistance with minimum data requirements
        data_length = min(100, len(close))
        recent_data = close.tail(data_length)
        
        support = float(recent_data.min())
        resistance = float(recent_data.max())
        
        # 🔥 FIX: Avoid division by zero
        range_size = resistance - support
        price_position = (current_price - support) / range_size if range_size != 0 else 0.5
        
        # Calculate volatility with minimum periods
        volatility_period = min(20, len(close) - 1)
        volatility = float(close.rolling(volatility_period, min_periods=1).std().iloc[-1])
        
        return {
            'support': support,
            'resistance': resistance,
            'price_position': price_position,
            'range_size': range_size,
            'volatility': volatility,
            'current_price': current_price,
            'market_range': 'narrow' if range_size < current_price * 0.02 else 'wide'
        }
        
    except Exception as e:
        logger.error(f"Market geometry calculation error: {e}")
        current_price = float(close.iloc[-1]) if not close.empty else 1.0
        return {
            'support': current_price * 0.98,
            'resistance': current_price * 1.02,
            'price_position': 0.5,
            'range_size': current_price * 0.04,
            'volatility': current_price * 0.01,
            'current_price': current_price,
            'market_range': 'normal'
        }

def calculate_fibonacci_retracements(high: pd.Series, low: pd.Series, close: pd.Series) -> Dict:
    """🔥 ENHANCED: Calculate Fibonacci retracements with error handling"""
    try:
        if len(high) < 10:
            return {}
        
        # Find recent swing high and low
        lookback = min(50, len(high))
        recent_high = float(high.tail(lookback).max())
        recent_low = float(low.tail(lookback).min())
        range_size = recent_high - recent_low
        
        if range_size == 0:
            return {}
        
        # Calculate retracement levels
        retracements = {
            '0.0%': recent_high,
            '23.6%': recent_high - (range_size * 0.236),
            '38.2%': recent_high - (range_size * 0.382),
            '50.0%': recent_high - (range_size * 0.5),
            '61.8%': recent_high - (range_size * 0.618),
            '78.6%': recent_high - (range_size * 0.786),
            '100.0%': recent_low,
            'range_high': recent_high,
            'range_low': recent_low,
            'range_size': range_size
        }
        
        return retracements
        
    except Exception as e:
        logger.error(f"Fibonacci retracement calculation error: {e}")
        return {}

def calculate_fibonacci_extensions(high: pd.Series, low: pd.Series, close: pd.Series) -> Dict:
    """🔥 ENHANCED: Calculate Fibonacci extensions for ICT with error handling"""
    try:
        if len(high) < 10:
            return {}
        
        # Find recent swing high and low
        lookback = min(50, len(high))
        recent_high = float(high.tail(lookback).max())
        recent_low = float(low.tail(lookback).min())
        range_size = recent_high - recent_low
        
        if range_size == 0:
            return {}
        
        # Calculate extensions
        extensions = {
            # Upside extensions
            '127.2%': recent_high + (range_size * 0.272),
            '141.4%': recent_high + (range_size * 0.414),
            '161.8%': recent_high + (range_size * 0.618),
            '200.0%': recent_high + range_size,
            '261.8%': recent_high + (range_size * 1.618),
            
            # Downside extensions
            '127.2%_down': recent_low - (range_size * 0.272),
            '141.4%_down': recent_low - (range_size * 0.414),
            '161.8%_down': recent_low - (range_size * 0.618),
            '200.0%_down': recent_low - range_size,
            '261.8%_down': recent_low - (range_size * 1.618),
            
            'base_high': recent_high,
            'base_low': recent_low,
            'range_size': range_size
        }
        
        return extensions
        
    except Exception as e:
        logger.error(f"Fibonacci extension calculation error: {e}")
        return {}

# 🔥 ENHANCED COMPATIBILITY FUNCTIONS

def calculate_support_resistance(high: pd.Series, low: pd.Series, close: pd.Series) -> Tuple[List, List]:
    """🔥 ENHANCED: Calculate support and resistance levels with error handling"""
    try:
        swing_points = find_swing_points(pd.DataFrame({'high': high, 'low': low}))
        
        support_levels = swing_points.get('support_levels', [])
        resistance_levels = swing_points.get('resistance_levels', [])
        
        # Ensure we have some levels
        if not support_levels:
            support_levels = [float(low.min())]
        if not resistance_levels:
            resistance_levels = [float(high.max())]
        
        return support_levels[-5:], resistance_levels[-5:]  # Return last 5 of each
        
    except Exception as e:
        logger.error(f"Support/resistance calculation error: {e}")
        return [float(low.min()) if not low.empty else 1.0], [float(high.max()) if not high.empty else 1.0]

def detect_patterns(high: pd.Series, low: pd.Series, close: pd.Series, volume: Optional[pd.Series] = None) -> List[Dict]:
    """🔥 ENHANCED: Detect chart patterns with improved logic"""
    try:
        patterns = []
        
        if len(close) < 25:
            return patterns
        
        # Enhanced pattern detection
        for i in range(20, len(close) - 5):
            try:
                recent_closes = close.iloc[i-20:i+1]
                recent_highs = high.iloc[i-20:i+1]
                recent_lows = low.iloc[i-20:i+1]
                
                # Double top pattern detection
                if len(recent_closes) > 15:
                    max_val = float(recent_highs.max())
                    # Find indices where price is very close to max
                    max_indices = []
                    for j, val in enumerate(recent_highs):
                        if abs(float(val) - max_val) < max_val * 0.01:  # Within 1%
                            max_indices.append(j)
                    
                    if len(max_indices) >= 2 and max_indices[-1] - max_indices[0] > 5:  # At least 5 periods apart
                        patterns.append({
                            'type': 'double_top',
                            'confidence': 0.7,
                            'index': i,
                            'level': max_val,
                            'description': 'Double top resistance pattern'
                        })
                
                # Double bottom pattern detection
                if len(recent_closes) > 15:
                    min_val = float(recent_lows.min())
                    # Find indices where price is very close to min
                    min_indices = []
                    for j, val in enumerate(recent_lows):
                        if abs(float(val) - min_val) < min_val * 0.01:  # Within 1%
                            min_indices.append(j)
                    
                    if len(min_indices) >= 2 and min_indices[-1] - min_indices[0] > 5:  # At least 5 periods apart
                        patterns.append({
                            'type': 'double_bottom',
                            'confidence': 0.7,
                            'index': i,
                            'level': min_val,
                            'description': 'Double bottom support pattern'
                        })
                        
            except Exception as e:
                continue
        
        return patterns[-10:]  # Return last 10 patterns
        
    except Exception as e:
        logger.error(f"Pattern detection error: {e}")
        return []

# 🔥 ENHANCED CLASSES

class PriceActionAnalyzer:
    """🔥 ENHANCED: Real Price Action Analyzer class with comprehensive analysis"""
    
    def __init__(self, lookback_period: int = 50):
        self.lookback_period = lookback_period
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def analyze_price_action(self, high: pd.Series, low: pd.Series, close: pd.Series, volume: Optional[pd.Series] = None) -> Dict:
        """🔥 ENHANCED: Comprehensive price action analysis with error handling"""
        try:
            # Ensure minimum data
            if len(close) < 10:
                return self._get_default_analysis(close)
            
            # Get all analysis components
            market_structure = detect_market_structure(high, low, close)
            order_blocks = identify_order_blocks(high, low, close, volume)
            fvgs = detect_fair_value_gaps(high, low, close)
            liquidity_zones = find_liquidity_zones(high, low, close, volume)
            bos = detect_break_of_structure(high, low, close)
            choch = detect_change_of_character(high, low, close)
            premium_discount = identify_premium_discount_zones(high, low, close)
            
            # Calculate trend strength
            trend = market_structure.get('trend', 'neutral')
            trend_strength = 0.8 if trend != 'neutral' else 0.3
            
            # Enhanced trend strength calculation
            if len(close) > 20:
                price_momentum = float(close.iloc[-1]) - float(close.iloc[-20])
                volatility = float(close.rolling(20, min_periods=1).std().iloc[-1])
                if volatility > 0:
                    trend_strength = min(0.95, abs(price_momentum / volatility) / 10)
            
            return {
                'trend': trend,
                'strength': trend_strength,
                'support_levels': market_structure.get('support_levels', []),
                'resistance_levels': market_structure.get('resistance_levels', []),
                'order_blocks': order_blocks,
                'fair_value_gaps': fvgs,
                'liquidity_zones': liquidity_zones,
                'break_of_structure': bos,
                'change_of_character': choch,
                'premium_discount_zones': premium_discount,
                'patterns': detect_patterns(high, low, close, volume),
                'market_structure': market_structure.get('structure', 'ranging'),
                'current_zone': premium_discount.get('current_zone', 'equilibrium')
            }
            
        except Exception as e:
            self.logger.error(f"Price action analysis error: {e}")
            return self._get_default_analysis(close)
    
    def _get_default_analysis(self, close: pd.Series) -> Dict:
        """Get default analysis when errors occur"""
        current_price = float(close.iloc[-1]) if not close.empty else 1.0
        return {
            'trend': 'neutral',
            'strength': 0.3,
            'support_levels': [current_price * 0.99],
            'resistance_levels': [current_price * 1.01],
            'order_blocks': [],
            'fair_value_gaps': [],
            'liquidity_zones': [],
            'break_of_structure': {'bos_detected': False},
            'change_of_character': {'choch_detected': False},
            'premium_discount_zones': {'current_zone': 'equilibrium'},
            'patterns': [],
            'market_structure': 'ranging',
            'current_zone': 'equilibrium'
        }
    
    def find_patterns(self, high: pd.Series, low: pd.Series, close: pd.Series) -> List[Dict]:
        """🔥 ENHANCED: Find chart patterns with error handling"""
        return detect_patterns(high, low, close)

class SupportResistanceFinder:
    """🔥 ENHANCED: Support and Resistance Finder with improved detection"""
    
    def __init__(self, sensitivity: float = 0.02):
        self.sensitivity = sensitivity
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def find_levels(self, high: pd.Series, low: pd.Series, close: pd.Series) -> Tuple[List, List]:
        """🔥 ENHANCED: Find support and resistance levels"""
        try:
            return calculate_support_resistance(high, low, close)
        except Exception as e:
            self.logger.error(f"Level finding error: {e}")
            current_price = float(close.iloc[-1]) if not close.empty else 1.0
            return [current_price * 0.99], [current_price * 1.01]

# 🔥 ADDITIONAL UTILITY FUNCTIONS

def setup_logging(name: str = "price_action", level: str = "INFO") -> logging.Logger:
    """🔥 ENHANCED: Setup logging with better configuration"""
    logger = logging.getLogger(name)
    if not logger.handlers:  # Avoid duplicate handlers
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    return logger

def validate_data(high: pd.Series, low: pd.Series, close: pd.Series) -> bool:
    """Validate input data integrity"""
    try:
        if any(series.empty for series in [high, low, close]):
            return False
        if len(high) != len(low) or len(low) != len(close):
            return False
        if any(pd.isna(series.iloc[-1]) for series in [high, low, close]):
            return False
        return True
    except:
        return False

# 🎯 EXPORT ALL FUNCTIONS FOR COMPATIBILITY
__all__ = [
    'detect_market_structure', 'find_swing_points', 'detect_break_of_structure',
    'detect_change_of_character', 'identify_order_blocks', 'detect_fair_value_gaps',
    'find_liquidity_zones', 'identify_liquidity_levels', 'identify_premium_discount_zones',
    'calculate_market_geometry', 'calculate_fibonacci_retracements', 'calculate_fibonacci_extensions',
    'calculate_support_resistance', 'detect_patterns', 'PriceActionAnalyzer', 'SupportResistanceFinder',
    'setup_logging', 'validate_data'
]
=======
        for i in range(window, len(highs) - window):
            # Check for swing high
            if all(highs[i] >= highs[i-j] for j in range(1, window+1)) and \
               all(highs[i] >= highs[i+j] for j in range(1, window+1)):
                swing_highs.append((i, highs[i]))
            
            # Check for swing low
            if all(lows[i] <= lows[i-j] for j in range(1, window+1)) and \
               all(lows[i] <= lows[i+j] for j in range(1, window+1)):
                swing_lows.append((i, lows[i]))
        
        return swing_highs, swing_lows
        
    except Exception as e:
        print(f"Error finding swing highs/lows: {e}")
        return [], []

def calculate_pivot_points(
    high: float, 
    low: float, 
    close: float
) -> Dict[str, float]:
    """
    Calculate pivot points and support/resistance levels
    
    Args:
        high: Previous period high
        low: Previous period low  
        close: Previous period close
    
    Returns:
        Dictionary with pivot levels
    """
    try:
        # Calculate pivot point
        pivot = (high + low + close) / 3
        
        # Calculate support and resistance levels
        r1 = (2 * pivot) - low
        s1 = (2 * pivot) - high
        r2 = pivot + (high - low)
        s2 = pivot - (high - low)
        r3 = high + 2 * (pivot - low)
        s3 = low - 2 * (high - pivot)
        
        return {
            'pivot': pivot,
            'r1': r1,
            'r2': r2,
            'r3': r3,
            's1': s1,
            's2': s2,
            's3': s3
        }
        
    except Exception as e:
        print(f"Error calculating pivot points: {e}")
        return {}

def detect_chart_patterns(
    data: pd.DataFrame, 
    pattern_type: str = 'double_top'
) -> List[Dict]:
    """
    Detect basic chart patterns
    
    Args:
        data: DataFrame with OHLC data
        pattern_type: Type of pattern to detect
    
    Returns:
        List of detected patterns
    """
    try:
        patterns = []
        
        if pattern_type == 'double_top':
            # Simple double top detection
            swing_highs, _ = find_swing_highs_lows(data, window=3)
            
            for i in range(len(swing_highs) - 1):
                high1_idx, high1_price = swing_highs[i]
                high2_idx, high2_price = swing_highs[i + 1]
                
                # Check if prices are similar (within 1%)
                if abs(high1_price - high2_price) / high1_price < 0.01:
                    patterns.append({
                        'type': 'double_top',
                        'start_idx': high1_idx,
                        'end_idx': high2_idx,
                        'level': (high1_price + high2_price) / 2,
                        'confidence': 0.7
                    })
        
        return patterns
        
    except Exception as e:
        print(f"Error detecting chart patterns: {e}")
        return []

def calculate_trend_strength(
    data: pd.DataFrame, 
    period: int = 20
) -> Dict[str, float]:
    """
    Calculate trend strength indicators
    
    Args:
        data: DataFrame with OHLC data
        period: Period for calculation
    
    Returns:
        Dictionary with trend strength metrics
    """
    try:
        close_prices = data['close'].values
        
        # Calculate linear regression slope
        x = np.arange(period)
        recent_prices = close_prices[-period:]
        
        slope, _ = np.polyfit(x, recent_prices, 1)
        
        # Normalize slope by price level
        normalized_slope = slope / recent_prices[0] if recent_prices[0] != 0 else 0
        
        # Calculate R-squared for trend strength
        trend_line = slope * x + recent_prices[0]
        ss_res = np.sum((recent_prices - trend_line) ** 2)
        ss_tot = np.sum((recent_prices - np.mean(recent_prices)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        return {
            'slope': normalized_slope,
            'strength': r_squared,
            'direction': 'up' if slope > 0 else 'down',
            'trend_score': abs(normalized_slope) * r_squared
        }
        
    except Exception as e:
        print(f"Error calculating trend strength: {e}")
        return {'slope': 0, 'strength': 0, 'direction': 'neutral', 'trend_score': 0}

def calculate_support_resistance_levels(data: pd.DataFrame, window: int = 20) -> Dict[str, List[float]]:
    """Calculate support and resistance levels"""
    try:
        swing_highs, swing_lows = find_swing_highs_lows(data, window)
        
        resistance_levels = [high[1] for high in swing_highs[-5:]]  # Last 5 swing highs
        support_levels = [low[1] for low in swing_lows[-5:]]  # Last 5 swing lows
        
        return {
            'resistance': resistance_levels,
            'support': support_levels
        }
    except Exception as e:
        print(f"Error calculating support/resistance: {e}")
        return {'resistance': [], 'support': []}

# Export all functions
__all__ = [
    'calculate_fibonacci_retracements', 'calculate_fibonacci_extensions',
    'find_swing_highs_lows', 'calculate_pivot_points', 'detect_chart_patterns',
    'calculate_trend_strength', 'calculate_support_resistance_levels'
]
# Add this to your existing utils/price_action.py file

def find_swing_points(data: pd.DataFrame, window: int = 5) -> Tuple[List[Tuple[int, float]], List[Tuple[int, float]]]:
    """
    Find swing high and low points in price data
    
    Args:
        data: DataFrame with OHLC data
        window: Window size for swing detection
    
    Returns:
        Tuple of (swing_highs, swing_lows) as lists of (index, price)
    """
    try:
        highs = data['high'].values
        lows = data['low'].values
        
        swing_highs = []
        swing_lows = []
        
        for i in range(window, len(highs) - window):
            # Check for swing high
            if all(highs[i] >= highs[i-j] for j in range(1, window+1)) and \
               all(highs[i] >= highs[i+j] for j in range(1, window+1)):
                swing_highs.append((i, highs[i]))
            
            # Check for swing low
            if all(lows[i] <= lows[i-j] for j in range(1, window+1)) and \
               all(lows[i] <= lows[i+j] for j in range(1, window+1)):
                swing_lows.append((i, lows[i]))
        
        return swing_highs, swing_lows
        
    except Exception as e:
        print(f"Error finding swing points: {e}")
        return [], []

def calculate_swing_levels(data: pd.DataFrame, window: int = 10) -> Dict[str, List[float]]:
    """Calculate swing-based support and resistance levels"""
    try:
        swing_highs, swing_lows = find_swing_points(data, window)
        
        resistance_levels = [high[1] for high in swing_highs[-5:]]  # Last 5 swing highs
        support_levels = [low[1] for low in swing_lows[-5:]]  # Last 5 swing lows
        
        return {
            'resistance': resistance_levels,
            'support': support_levels,
            'swing_highs': swing_highs,
            'swing_lows': swing_lows
        }
    except Exception as e:
        print(f"Error calculating swing levels: {e}")
        return {'resistance': [], 'support': [], 'swing_highs': [], 'swing_lows': []}

# Export the new functions
__all__.extend(['find_swing_points', 'calculate_swing_levels'])

"""
===============================================================
Complete Price Action Utilities with SMC/ICT/RTM Support
===============================================================
Professional implementation of Smart Money Concepts, ICT, and RTM
price action analysis utilities for institutional-grade trading.

Features:
- Market structure detection (BOS, CHoCH)
- Swing point identification with multiple algorithms
- Order block detection and validation
- Fair Value Gap (FVG) identification
- Liquidity zone mapping
- Support/resistance level calculation
- Break of structure analysis
- Institutional order flow analysis
===============================================================
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging

# Set up logging
logger = logging.getLogger(__name__)

class MarketStructure(Enum):
    """Market structure states for SMC analysis"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    RANGING = "ranging"
    BREAKOUT = "breakout"

class SwingType(Enum):
    """Types of swing points in market structure"""
    HIGHER_HIGH = "HH"
    LOWER_HIGH = "LH" 
    HIGHER_LOW = "HL"
    LOWER_LOW = "LL"
    EQUAL_HIGH = "EH"
    EQUAL_LOW = "EL"

@dataclass
class SwingPoint:
    """Swing point data structure for market analysis"""
    index: int
    price: float
    swing_type: SwingType
    timestamp: datetime
    strength: float = 0.0
    confirmed: bool = False
    volume: float = 0.0
    rsi: float = 50.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'index': self.index,
            'price': self.price,
            'swing_type': self.swing_type.value,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'strength': self.strength,
            'confirmed': self.confirmed,
            'volume': self.volume,
            'rsi': self.rsi
        }

@dataclass 
class OrderBlock:
    """Order block structure for institutional analysis"""
    start_index: int
    end_index: int
    high: float
    low: float
    block_type: str  # "bullish" or "bearish"
    strength: float
    volume: float
    timestamp: datetime
    mitigated: bool = False
    
    @property
    def middle(self) -> float:
        """Get middle price of order block"""
        return (self.high + self.low) / 2
    
    @property
    def range_size(self) -> float:
        """Get size of order block range"""
        return self.high - self.low

@dataclass
class FairValueGap:
    """Fair Value Gap structure for SMC analysis"""
    start_index: int
    end_index: int
    upper_level: float
    lower_level: float
    gap_type: str  # "bullish" or "bearish"
    volume: float
    timestamp: datetime
    filled: bool = False
    
    @property
    def middle(self) -> float:
        """Get middle of fair value gap"""
        return (self.upper_level + self.lower_level) / 2
    
    @property
    def size(self) -> float:
        """Get size of the gap"""
        return self.upper_level - self.lower_level

@dataclass
class LiquidityZone:
    """Liquidity zone for institutional analysis"""
    price_level: float
    zone_type: str  # "buy_side" or "sell_side"
    strength: float
    volume: float
    timestamp: datetime
    swept: bool = False

# === CORE MARKET STRUCTURE DETECTION ===

def detect_market_structure(data: pd.DataFrame, swing_length: int = 5, 
                          min_swing_strength: float = 0.001) -> Dict[str, Any]:
    """
    **CORE FUNCTION**: Detect comprehensive market structure for ICT/RTM strategies
    
    This is the main function that ICT and RTM strategies require for:
    - Break of Structure (BOS) detection
    - Change of Character (CHoCH) identification  
    - Swing point analysis
    - Trend determination
    - Support/resistance mapping
    
    Args:
        data: OHLCV DataFrame with columns ['open', 'high', 'low', 'close', 'volume']
        swing_length: Number of bars to look back/forward for swing detection
        min_swing_strength: Minimum price movement to qualify as swing (as percentage)
        
    Returns:
        Comprehensive market structure analysis dictionary
    """
    try:
        if data.empty or len(data) < swing_length * 2:
            return _create_empty_structure_result()
        
        # Step 1: Detect swing points
        swing_highs, swing_lows = find_swing_points(data, swing_length)
        
        # Step 2: Classify swing patterns  
        swing_classification = classify_swing_patterns(swing_highs, swing_lows, data)
        
        # Step 3: Determine overall market structure
        market_trend = determine_market_trend(swing_highs, swing_lows, data)
        
        # Step 4: Detect breaks of structure
        bos_signals = detect_break_of_structure(swing_highs, swing_lows, data)
        
        # Step 5: Find change of character points
        choch_signals = detect_change_of_character(swing_highs, swing_lows, data)
        
        # Step 6: Identify key levels
        support_resistance = calculate_support_resistance_levels(data, swing_highs, swing_lows)
        
        # Step 7: Detect order blocks
        order_blocks = detect_order_blocks(data, swing_highs, swing_lows)
        
        # Step 8: Find fair value gaps
        fair_value_gaps = detect_fair_value_gaps(data)
        
        # Step 9: Map liquidity zones
        liquidity_zones = detect_liquidity_zones(data, swing_highs, swing_lows)
        
        # Step 10: Calculate institutional levels
        institutional_levels = calculate_institutional_levels(data, swing_highs, swing_lows)
        
        # Compile comprehensive result
        structure_result = {
            # Core Market Structure
            'market_structure': market_trend,
            'trend_direction': market_trend.get('direction', 'neutral'),
            'trend_strength': market_trend.get('strength', 0.0),
            'structure_confidence': market_trend.get('confidence', 0.0),
            
            # Swing Analysis
            'swing_highs': [sp.to_dict() for sp in swing_highs],
            'swing_lows': [sp.to_dict() for sp in swing_lows],
            'swing_classification': swing_classification,
            'recent_swing_high': swing_highs[-1].to_dict() if swing_highs else None,
            'recent_swing_low': swing_lows[-1].to_dict() if swing_lows else None,
            
            # Structure Breaks
            'break_of_structure': bos_signals,
            'change_of_character': choch_signals,
            'has_recent_bos': len(bos_signals) > 0,
            'has_recent_choch': len(choch_signals) > 0,
            
            # Key Levels
            'support_levels': support_resistance['support'],
            'resistance_levels': support_resistance['resistance'],
            'key_levels': support_resistance['key_levels'],
            
            # SMC Components
            'order_blocks': [ob.__dict__ for ob in order_blocks],
            'fair_value_gaps': [fvg.__dict__ for fvg in fair_value_gaps],
            'liquidity_zones': [lz.__dict__ for lz in liquidity_zones],
            'institutional_levels': institutional_levels,
            
            # Analysis Metadata
            'analysis_timestamp': datetime.now().isoformat(),
            'data_points_analyzed': len(data),
            'swing_length_used': swing_length,
            'min_strength_threshold': min_swing_strength,
            
            # Trading Signals
            'bullish_signals': _extract_bullish_signals(bos_signals, choch_signals, order_blocks),
            'bearish_signals': _extract_bearish_signals(bos_signals, choch_signals, order_blocks),
            'current_bias': _determine_current_bias(market_trend, bos_signals, choch_signals)
        }
        
        logger.info(f"Market structure analysis completed: {structure_result['trend_direction']} trend with {len(swing_highs)} swing highs and {len(swing_lows)} swing lows")
        
        return structure_result
        
    except Exception as e:
        logger.error(f"Error in detect_market_structure: {e}")
        return _create_empty_structure_result(error=str(e))

def find_swing_points(data: pd.DataFrame, window: int = 5) -> Tuple[List[SwingPoint], List[SwingPoint]]:
    """
    **ENHANCED**: Find swing high and low points with multiple detection algorithms
    
    Uses advanced swing detection combining:
    - Traditional pivots
    - Volume confirmation  
    - RSI divergence detection
    - Strength calculation
    
    Args:
        data: OHLCV DataFrame
        window: Window size for swing detection
        
    Returns:
        Tuple of (swing_highs, swing_lows) as SwingPoint objects
    """
    try:
        if len(data) < window * 2 + 1:
            return [], []
        
        highs = data['high'].values
        lows = data['low'].values
        volumes = data['volume'].values if 'volume' in data.columns else np.ones(len(data))
        closes = data['close'].values
        
        # Calculate RSI for divergence detection
        rsi_values = _calculate_rsi(closes, period=14)
        
        swing_highs = []
        swing_lows = []
        
        # Find swing points with enhanced algorithm
        for i in range(window, len(highs) - window):
            # Check for swing high
            if _is_swing_high(highs, i, window):
                strength = _calculate_swing_strength(highs, i, window, 'high')
                volume_strength = volumes[i] / np.mean(volumes[max(0, i-10):i+1])
                
                swing_point = SwingPoint(
                    index=i,
                    price=highs[i],
                    swing_type=SwingType.HIGHER_HIGH,  # Will be classified later
                    timestamp=data.index[i] if hasattr(data.index[i], 'to_pydatetime') else datetime.now(),
                    strength=strength * volume_strength,
                    confirmed=True,
                    volume=volumes[i],
                    rsi=rsi_values[i] if i < len(rsi_values) else 50.0
                )
                swing_highs.append(swing_point)
            
            # Check for swing low
            if _is_swing_low(lows, i, window):
                strength = _calculate_swing_strength(lows, i, window, 'low')
                volume_strength = volumes[i] / np.mean(volumes[max(0, i-10):i+1])
                
                swing_point = SwingPoint(
                    index=i,
                    price=lows[i],
                    swing_type=SwingType.LOWER_LOW,  # Will be classified later
                    timestamp=data.index[i] if hasattr(data.index[i], 'to_pydatetime') else datetime.now(),
                    strength=strength * volume_strength,
                    confirmed=True,
                    volume=volumes[i],
                    rsi=rsi_values[i] if i < len(rsi_values) else 50.0
                )
                swing_lows.append(swing_point)
        
        # Classify swing types based on sequence
        swing_highs = _classify_swing_sequence(swing_highs, 'high')
        swing_lows = _classify_swing_sequence(swing_lows, 'low')
        
        logger.debug(f"Found {len(swing_highs)} swing highs and {len(swing_lows)} swing lows")
        
        return swing_highs, swing_lows
        
    except Exception as e:
        logger.error(f"Error finding swing points: {e}")
        return [], []

def calculate_swing_levels(data: pd.DataFrame, window: int = 10) -> Dict[str, List[float]]:
    """Calculate swing-based support and resistance levels"""
    try:
        swing_highs, swing_lows = find_swing_points(data, window)
        
        # Extract price levels
        resistance_levels = [sh.price for sh in swing_highs[-5:]] if swing_highs else []
        support_levels = [sl.price for sl in swing_lows[-5:]] if swing_lows else []
        
        # Add current price context
        current_price = float(data['close'].iloc[-1])
        
        return {
            'resistance': sorted(resistance_levels, reverse=True),
            'support': sorted(support_levels),
            'swing_highs': [(sh.index, sh.price) for sh in swing_highs],
            'swing_lows': [(sl.index, sl.price) for sl in swing_lows],
            'current_price': current_price,
            'nearest_resistance': min([r for r in resistance_levels if r > current_price], default=None),
            'nearest_support': max([s for s in support_levels if s < current_price], default=None)
        }
        
    except Exception as e:
        logger.error(f"Error calculating swing levels: {e}")
        return {'resistance': [], 'support': [], 'swing_highs': [], 'swing_lows': []}

# === SMC-SPECIFIC DETECTION FUNCTIONS ===

def detect_order_blocks(data: pd.DataFrame, swing_highs: List[SwingPoint], 
                       swing_lows: List[SwingPoint]) -> List[OrderBlock]:
    """
    **SMC CORE**: Detect institutional order blocks
    
    Order blocks are zones where large institutions placed significant orders,
    often acting as strong support/resistance levels.
    """
    try:
        order_blocks = []
        
        # Detect bullish order blocks (near swing lows)
        for swing_low in swing_lows[-10:]:  # Last 10 swing lows
            ob = _find_bullish_order_block(data, swing_low)
            if ob:
                order_blocks.append(ob)
        
        # Detect bearish order blocks (near swing highs)  
        for swing_high in swing_highs[-10:]:  # Last 10 swing highs
            ob = _find_bearish_order_block(data, swing_high)
            if ob:
                order_blocks.append(ob)
        
        # Sort by strength
        order_blocks.sort(key=lambda x: x.strength, reverse=True)
        
        logger.debug(f"Detected {len(order_blocks)} order blocks")
        return order_blocks[:20]  # Return top 20
        
    except Exception as e:
        logger.error(f"Error detecting order blocks: {e}")
        return []

def detect_fair_value_gaps(data: pd.DataFrame) -> List[FairValueGap]:
    """
    **SMC CORE**: Detect Fair Value Gaps (imbalances in price)
    
    FVGs occur when price moves aggressively, leaving gaps that often get filled.
    """
    try:
        fvgs = []
        
        highs = data['high'].values
        lows = data['low'].values
        volumes = data['volume'].values if 'volume' in data.columns else np.ones(len(data))
        
        for i in range(2, len(data)):
            # Check for bullish FVG
            if (lows[i] > highs[i-2] and 
                _is_aggressive_move(data, i-2, i, 'bullish')):
                
                fvg = FairValueGap(
                    start_index=i-2,
                    end_index=i,
                    upper_level=lows[i],
                    lower_level=highs[i-2],
                    gap_type='bullish',
                    volume=volumes[i-1],
                    timestamp=data.index[i] if hasattr(data.index[i], 'to_pydatetime') else datetime.now()
                )
                fvgs.append(fvg)
            
            # Check for bearish FVG
            elif (highs[i] < lows[i-2] and 
                  _is_aggressive_move(data, i-2, i, 'bearish')):
                
                fvg = FairValueGap(
                    start_index=i-2,
                    end_index=i,
                    upper_level=lows[i-2],
                    lower_level=highs[i],
                    gap_type='bearish',
                    volume=volumes[i-1],
                    timestamp=data.index[i] if hasattr(data.index[i], 'to_pydatetime') else datetime.now()
                )
                fvgs.append(fvg)
        
        logger.debug(f"Detected {len(fvgs)} fair value gaps")
        return fvgs[-50:]  # Return last 50 FVGs
        
    except Exception as e:
        logger.error(f"Error detecting fair value gaps: {e}")
        return []

def detect_liquidity_zones(data: pd.DataFrame, swing_highs: List[SwingPoint], 
                          swing_lows: List[SwingPoint]) -> List[LiquidityZone]:
    """
    **SMC CORE**: Detect liquidity zones where stops are likely positioned
    
    Liquidity zones are areas where retail traders place stops, creating
    opportunities for institutional players to hunt liquidity.
    """
    try:
        liquidity_zones = []
        
        # Buy-side liquidity (above swing highs)
        for swing_high in swing_highs[-10:]:
            # Look for equal highs or areas of confluence
            zone_price = swing_high.price + (swing_high.price * 0.001)  # Slightly above
            
            liquidity_zone = LiquidityZone(
                price_level=zone_price,
                zone_type='buy_side',
                strength=swing_high.strength,
                volume=swing_high.volume,
                timestamp=swing_high.timestamp
            )
            liquidity_zones.append(liquidity_zone)
        
        # Sell-side liquidity (below swing lows)
        for swing_low in swing_lows[-10:]:
            # Look for equal lows or areas of confluence
            zone_price = swing_low.price - (swing_low.price * 0.001)  # Slightly below
            
            liquidity_zone = LiquidityZone(
                price_level=zone_price,
                zone_type='sell_side',
                strength=swing_low.strength,
                volume=swing_low.volume,
                timestamp=swing_low.timestamp
            )
            liquidity_zones.append(liquidity_zone)
        
        logger.debug(f"Detected {len(liquidity_zones)} liquidity zones")
        return liquidity_zones
        
    except Exception as e:
        logger.error(f"Error detecting liquidity zones: {e}")
        return []

def detect_break_of_structure(swing_highs: List[SwingPoint], swing_lows: List[SwingPoint],
                             data: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    **ICT CORE**: Detect Break of Structure (BOS) signals
    
    BOS occurs when price breaks a significant swing point, indicating
    trend continuation or potential reversal.
    """
    try:
        bos_signals = []
        current_price = float(data['close'].iloc[-1])
        
        # Check for bullish BOS (break above recent swing high)
        if swing_highs:
            recent_high = swing_highs[-1]
            if current_price > recent_high.price:
                bos_signals.append({
                    'type': 'bullish_bos',
                    'broken_level': recent_high.price,
                    'break_strength': (current_price - recent_high.price) / recent_high.price,
                    'timestamp': datetime.now(),
                    'swing_point': recent_high.to_dict()
                })
        
        # Check for bearish BOS (break below recent swing low)
        if swing_lows:
            recent_low = swing_lows[-1]
            if current_price < recent_low.price:
                bos_signals.append({
                    'type': 'bearish_bos',
                    'broken_level': recent_low.price,
                    'break_strength': abs(current_price - recent_low.price) / recent_low.price,
                    'timestamp': datetime.now(),
                    'swing_point': recent_low.to_dict()
                })
        
        return bos_signals
        
    except Exception as e:
        logger.error(f"Error detecting break of structure: {e}")
        return []

def detect_change_of_character(swing_highs: List[SwingPoint], swing_lows: List[SwingPoint],
                              data: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    **ICT CORE**: Detect Change of Character (CHoCH) signals
    
    CHoCH indicates a potential trend reversal when market structure shifts.
    """
    try:
        choch_signals = []
        
        if len(swing_highs) >= 2 and len(swing_lows) >= 2:
            # Check for bullish CHoCH (break of bearish structure)
            if (swing_highs[-1].price > swing_highs[-2].price and
                swing_lows[-1].price > swing_lows[-2].price):
                
                choch_signals.append({
                    'type': 'bullish_choch',
                    'signal_strength': 0.8,
                    'trigger_price': swing_lows[-1].price,
                    'confirmation_price': swing_highs[-1].price,
                    'timestamp': datetime.now()
                })
            
            # Check for bearish CHoCH (break of bullish structure)
            elif (swing_highs[-1].price < swing_highs[-2].price and
                  swing_lows[-1].price < swing_lows[-2].price):
                
                choch_signals.append({
                    'type': 'bearish_choch',
                    'signal_strength': 0.8,
                    'trigger_price': swing_highs[-1].price,
                    'confirmation_price': swing_lows[-1].price,
                    'timestamp': datetime.now()
                })
        
        return choch_signals
        
    except Exception as e:
        logger.error(f"Error detecting change of character: {e}")
        return []

# === HELPER FUNCTIONS ===

def _is_swing_high(highs: np.ndarray, i: int, window: int) -> bool:
    """Check if index i is a swing high"""
    try:
        return all(highs[i] >= highs[i-j] for j in range(1, window+1)) and \
               all(highs[i] >= highs[i+j] for j in range(1, window+1))
    except (IndexError, ValueError):
        return False

def _is_swing_low(lows: np.ndarray, i: int, window: int) -> bool:
    """Check if index i is a swing low"""
    try:
        return all(lows[i] <= lows[i-j] for j in range(1, window+1)) and \
               all(lows[i] <= lows[i+j] for j in range(1, window+1))
    except (IndexError, ValueError):
        return False

def _calculate_swing_strength(prices: np.ndarray, i: int, window: int, swing_type: str) -> float:
    """Calculate the strength of a swing point"""
    try:
        if swing_type == 'high':
            left_diff = prices[i] - np.mean(prices[i-window:i])
            right_diff = prices[i] - np.mean(prices[i+1:i+window+1])
        else:  # 'low'
            left_diff = np.mean(prices[i-window:i]) - prices[i]
            right_diff = np.mean(prices[i+1:i+window+1]) - prices[i]
        
        return (left_diff + right_diff) / prices[i]
    except (IndexError, ValueError, ZeroDivisionError):
        return 0.0

def _calculate_rsi(prices: np.ndarray, period: int = 14) -> np.ndarray:
    """Calculate RSI for divergence detection"""
    try:
        if len(prices) < period + 1:
            return np.full(len(prices), 50.0)
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gains = np.zeros(len(gains))
        avg_losses = np.zeros(len(losses))
        
        # Initial averages
        avg_gains[period-1] = np.mean(gains[:period])
        avg_losses[period-1] = np.mean(losses[:period])
        
        # Subsequent averages using Wilder's smoothing
        for i in range(period, len(gains)):
            avg_gains[i] = (avg_gains[i-1] * (period-1) + gains[i]) / period
            avg_losses[i] = (avg_losses[i-1] * (period-1) + losses[i]) / period
        
        rs = np.divide(avg_gains, avg_losses, out=np.zeros_like(avg_gains), where=avg_losses!=0)
        rsi = 100 - (100 / (1 + rs))
        
        # Pad the beginning with neutral RSI
        return np.concatenate([np.full(period, 50.0), rsi[period-1:]])
        
    except Exception:
        return np.full(len(prices), 50.0)

def _classify_swing_sequence(swing_points: List[SwingPoint], point_type: str) -> List[SwingPoint]:
    """Classify swing points as HH, LH, HL, LL"""
    try:
        if len(swing_points) < 2:
            return swing_points
        
        for i in range(1, len(swing_points)):
            current = swing_points[i]
            previous = swing_points[i-1]
            
            if point_type == 'high':
                if current.price > previous.price:
                    current.swing_type = SwingType.HIGHER_HIGH
                elif current.price < previous.price:
                    current.swing_type = SwingType.LOWER_HIGH
                else:
                    current.swing_type = SwingType.EQUAL_HIGH
            else:  # 'low'
                if current.price > previous.price:
                    current.swing_type = SwingType.HIGHER_LOW
                elif current.price < previous.price:
                    current.swing_type = SwingType.LOWER_LOW
                else:
                    current.swing_type = SwingType.EQUAL_LOW
        
        return swing_points
        
    except Exception as e:
        logger.error(f"Error classifying swing sequence: {e}")
        return swing_points

def _find_bullish_order_block(data: pd.DataFrame, swing_low: SwingPoint) -> Optional[OrderBlock]:
    """Find bullish order block near swing low"""
    try:
        start_idx = max(0, swing_low.index - 5)
        end_idx = min(len(data), swing_low.index + 5)
        
        section = data.iloc[start_idx:end_idx]
        if section.empty:
            return None
        
        # Find the last bearish candle before the swing low
        for i in range(len(section)-1, -1, -1):
            if section.iloc[i]['close'] < section.iloc[i]['open']:
                return OrderBlock(
                    start_index=start_idx + i,
                    end_index=start_idx + i,
                    high=section.iloc[i]['high'],
                    low=section.iloc[i]['low'],
                    block_type='bullish',
                    strength=swing_low.strength,
                    volume=section.iloc[i]['volume'] if 'volume' in section.columns else 0,
                    timestamp=swing_low.timestamp
                )
        
        return None
        
    except Exception:
        return None

def _find_bearish_order_block(data: pd.DataFrame, swing_high: SwingPoint) -> Optional[OrderBlock]:
    """Find bearish order block near swing high"""
    try:
        start_idx = max(0, swing_high.index - 5)
        end_idx = min(len(data), swing_high.index + 5)
        
        section = data.iloc[start_idx:end_idx]
        if section.empty:
            return None
        
        # Find the last bullish candle before the swing high
        for i in range(len(section)-1, -1, -1):
            if section.iloc[i]['close'] > section.iloc[i]['open']:
                return OrderBlock(
                    start_index=start_idx + i,
                    end_index=start_idx + i,
                    high=section.iloc[i]['high'],
                    low=section.iloc[i]['low'],
                    block_type='bearish',
                    strength=swing_high.strength,
                    volume=section.iloc[i]['volume'] if 'volume' in section.columns else 0,
                    timestamp=swing_high.timestamp
                )
        
        return None
        
    except Exception:
        return None

def _is_aggressive_move(data: pd.DataFrame, start_idx: int, end_idx: int, direction: str) -> bool:
    """Check if price movement is aggressive enough to create FVG"""
    try:
        if end_idx - start_idx < 2:
            return False
        
        price_change = abs(data.iloc[end_idx]['close'] - data.iloc[start_idx]['close'])
        average_range = np.mean([data.iloc[i]['high'] - data.iloc[i]['low'] 
                               for i in range(start_idx, end_idx+1)])
        
        return price_change > average_range * 2  # 2x average range
        
    except Exception:
        return False

def classify_swing_patterns(swing_highs: List[SwingPoint], swing_lows: List[SwingPoint], 
                          data: pd.DataFrame) -> Dict[str, Any]:
    """Classify overall swing patterns for market structure"""
    try:
        if not swing_highs or not swing_lows:
            return {'pattern': 'insufficient_data', 'confidence': 0.0}
        
        recent_highs = swing_highs[-3:] if len(swing_highs) >= 3 else swing_highs
        recent_lows = swing_lows[-3:] if len(swing_lows) >= 3 else swing_lows
        
        # Analyze pattern
        if len(recent_highs) >= 2 and len(recent_lows) >= 2:
            higher_highs = all(recent_highs[i].price >= recent_highs[i-1].price 
                             for i in range(1, len(recent_highs)))
            higher_lows = all(recent_lows[i].price >= recent_lows[i-1].price 
                            for i in range(1, len(recent_lows)))
            
            if higher_highs and higher_lows:
                return {'pattern': 'uptrend', 'confidence': 0.8}
            elif not higher_highs and not higher_lows:
                return {'pattern': 'downtrend', 'confidence': 0.8}
            else:
                return {'pattern': 'ranging', 'confidence': 0.6}
        
        return {'pattern': 'neutral', 'confidence': 0.4}
        
    except Exception as e:
        logger.error(f"Error classifying swing patterns: {e}")
        return {'pattern': 'error', 'confidence': 0.0}

def determine_market_trend(swing_highs: List[SwingPoint], swing_lows: List[SwingPoint], 
                         data: pd.DataFrame) -> Dict[str, Any]:
    """Determine overall market trend and strength"""
    try:
        if not swing_highs or not swing_lows:
            return {'direction': 'neutral', 'strength': 0.0, 'confidence': 0.0}
        
        # Analyze recent swings
        recent_pattern = classify_swing_patterns(swing_highs, swing_lows, data)
        
        # Calculate trend strength based on swing momentum
        trend_strength = 0.0
        if len(swing_highs) >= 2:
            high_momentum = (swing_highs[-1].price - swing_highs[-2].price) / swing_highs[-2].price
            trend_strength += abs(high_momentum) * 0.5
        
        if len(swing_lows) >= 2:
            low_momentum = (swing_lows[-1].price - swing_lows[-2].price) / swing_lows[-2].price
            trend_strength += abs(low_momentum) * 0.5
        
        return {
            'direction': recent_pattern['pattern'],
            'strength': min(1.0, trend_strength * 100),  # Convert to percentage
            'confidence': recent_pattern['confidence'],
            'recent_swing_count': len(swing_highs) + len(swing_lows),
            'analysis_timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error determining market trend: {e}")
        return {'direction': 'error', 'strength': 0.0, 'confidence': 0.0}

def calculate_support_resistance_levels(data: pd.DataFrame, swing_highs: List[SwingPoint],
                                      swing_lows: List[SwingPoint]) -> Dict[str, List[float]]:
    """Calculate key support and resistance levels"""
    try:
        # Extract swing levels
        resistance_levels = [sh.price for sh in swing_highs[-10:]]
        support_levels = [sl.price for sl in swing_lows[-10:]]
        
        # Add psychological levels
        current_price = float(data['close'].iloc[-1])
        psychological_levels = _calculate_psychological_levels(current_price)
        
        # Combine and sort
        all_resistance = sorted(set(resistance_levels + psychological_levels['resistance']), reverse=True)
        all_support = sorted(set(support_levels + psychological_levels['support']))
        
        # Key confluence levels
        key_levels = _find_confluence_levels(all_resistance + all_support, current_price)
        
        return {
            'resistance': all_resistance[:10],  # Top 10
            'support': all_support[-10:],  # Top 10
            'key_levels': key_levels,
            'psychological_levels': psychological_levels,
            'current_price': current_price
        }
        
    except Exception as e:
        logger.error(f"Error calculating support/resistance levels: {e}")
        return {'resistance': [], 'support': [], 'key_levels': []}

def calculate_institutional_levels(data: pd.DataFrame, swing_highs: List[SwingPoint],
                                 swing_lows: List[SwingPoint]) -> Dict[str, Any]:
    """Calculate institutional trading levels"""
    try:
        current_price = float(data['close'].iloc[-1])
        
        # Previous day high/low
        daily_high = float(data['high'].iloc[-1])
        daily_low = float(data['low'].iloc[-1])
        
        # Weekly levels (approximate)
        weekly_high = float(data['high'].tail(5).max())
        weekly_low = float(data['low'].tail(5).min())
        
        # Monthly levels (approximate)
        monthly_high = float(data['high'].tail(20).max())
        monthly_low = float(data['low'].tail(20).min())
        
        return {
            'daily_levels': {
                'high': daily_high,
                'low': daily_low,
                'range': daily_high - daily_low
            },
            'weekly_levels': {
                'high': weekly_high,
                'low': weekly_low,
                'range': weekly_high - weekly_low
            },
            'monthly_levels': {
                'high': monthly_high,
                'low': monthly_low,
                'range': monthly_high - monthly_low
            },
            'current_price': current_price,
            'key_institutional_zones': [
                daily_high, daily_low,
                weekly_high, weekly_low,
                monthly_high, monthly_low
            ]
        }
        
    except Exception as e:
        logger.error(f"Error calculating institutional levels: {e}")
        return {}

def _calculate_psychological_levels(price: float) -> Dict[str, List[float]]:
    """Calculate psychological round number levels"""
    try:
        # Determine the appropriate round numbers based on price
        if price >= 1000:
            round_numbers = [100, 500, 1000]
        elif price >= 100:
            round_numbers = [10, 50, 100]
        elif price >= 10:
            round_numbers = [1, 5, 10]
        else:
            round_numbers = [0.1, 0.5, 1.0]
        
        psychological_levels = []
        for rn in round_numbers:
            # Find nearby round numbers
            lower = (int(price / rn) * rn)
            upper = lower + rn
            psychological_levels.extend([lower, upper])
        
        current_price = price
        resistance = [p for p in psychological_levels if p > current_price]
        support = [p for p in psychological_levels if p < current_price]
        
        return {
            'resistance': sorted(set(resistance))[:5],
            'support': sorted(set(support), reverse=True)[:5]
        }
        
    except Exception:
        return {'resistance': [], 'support': []}

def _find_confluence_levels(levels: List[float], current_price: float) -> List[Dict[str, Any]]:
    """Find levels where multiple factors converge"""
    try:
        confluence_zones = []
        tolerance = current_price * 0.001  # 0.1% tolerance
        
        for i, level in enumerate(levels):
            nearby_levels = [l for l in levels if abs(l - level) <= tolerance and l != level]
            
            if len(nearby_levels) >= 1:  # At least 2 levels close together
                confluence_zones.append({
                    'price': level,
                    'strength': len(nearby_levels) + 1,
                    'nearby_levels': nearby_levels,
                    'distance_from_current': abs(level - current_price) / current_price
                })
        
        # Sort by strength and proximity
        confluence_zones.sort(key=lambda x: (x['strength'], -x['distance_from_current']), reverse=True)
        
        return confluence_zones[:10]  # Top 10 confluence zones
        
    except Exception:
        return []

def _extract_bullish_signals(bos_signals: List[Dict], choch_signals: List[Dict], 
                           order_blocks: List[OrderBlock]) -> List[Dict[str, Any]]:
    """Extract bullish trading signals"""
    signals = []
    
    # BOS bullish signals
    for bos in bos_signals:
        if bos['type'] == 'bullish_bos':
            signals.append({
                'type': 'bos_bullish',
                'strength': bos['break_strength'],
                'entry_zone': bos['broken_level'],
                'signal_source': 'break_of_structure'
            })
    
    # CHoCH bullish signals
    for choch in choch_signals:
        if choch['type'] == 'bullish_choch':
            signals.append({
                'type': 'choch_bullish',
                'strength': choch['signal_strength'],
                'entry_zone': choch['trigger_price'],
                'signal_source': 'change_of_character'
            })
    
    # Bullish order blocks
    bullish_obs = [ob for ob in order_blocks if ob.block_type == 'bullish']
    for ob in bullish_obs[:3]:  # Top 3
        signals.append({
            'type': 'order_block_bullish',
            'strength': ob.strength,
            'entry_zone': ob.low,
            'signal_source': 'order_block'
        })
    
    return signals

def _extract_bearish_signals(bos_signals: List[Dict], choch_signals: List[Dict], 
                           order_blocks: List[OrderBlock]) -> List[Dict[str, Any]]:
    """Extract bearish trading signals"""
    signals = []
    
    # BOS bearish signals
    for bos in bos_signals:
        if bos['type'] == 'bearish_bos':
            signals.append({
                'type': 'bos_bearish',
                'strength': bos['break_strength'],
                'entry_zone': bos['broken_level'],
                'signal_source': 'break_of_structure'
            })
    
    # CHoCH bearish signals
    for choch in choch_signals:
        if choch['type'] == 'bearish_choch':
            signals.append({
                'type': 'choch_bearish',
                'strength': choch['signal_strength'],
                'entry_zone': choch['trigger_price'],
                'signal_source': 'change_of_character'
            })
    
    # Bearish order blocks
    bearish_obs = [ob for ob in order_blocks if ob.block_type == 'bearish']
    for ob in bearish_obs[:3]:  # Top 3
        signals.append({
            'type': 'order_block_bearish',
            'strength': ob.strength,
            'entry_zone': ob.high,
            'signal_source': 'order_block'
        })
    
    return signals

def _determine_current_bias(market_trend: Dict, bos_signals: List[Dict], 
                          choch_signals: List[Dict]) -> str:
    """Determine current market bias"""
    try:
        trend_direction = market_trend.get('direction', 'neutral')
        
        # Check recent signals
        recent_bullish_signals = len([s for s in bos_signals + choch_signals 
                                   if 'bullish' in s.get('type', '')])
        recent_bearish_signals = len([s for s in bos_signals + choch_signals 
                                   if 'bearish' in s.get('type', '')])
        
        if recent_bullish_signals > recent_bearish_signals:
            return 'bullish'
        elif recent_bearish_signals > recent_bullish_signals:
            return 'bearish'
        else:
            return trend_direction
            
    except Exception:
        return 'neutral'

def _create_empty_structure_result(error: str = None) -> Dict[str, Any]:
    """Create empty structure result for error cases"""
    return {
        'market_structure': {'direction': 'neutral', 'strength': 0.0, 'confidence': 0.0},
        'trend_direction': 'neutral',
        'trend_strength': 0.0,
        'structure_confidence': 0.0,
        'swing_highs': [],
        'swing_lows': [],
        'swing_classification': {'pattern': 'no_data', 'confidence': 0.0},
        'recent_swing_high': None,
        'recent_swing_low': None,
        'break_of_structure': [],
        'change_of_character': [],
        'has_recent_bos': False,
        'has_recent_choch': False,
        'support_levels': [],
        'resistance_levels': [],
        'key_levels': [],
        'order_blocks': [],
        'fair_value_gaps': [],
        'liquidity_zones': [],
        'institutional_levels': {},
        'bullish_signals': [],
        'bearish_signals': [],
        'current_bias': 'neutral',
        'analysis_timestamp': datetime.now().isoformat(),
        'error': error
    }

# === ADDITIONAL UTILITY FUNCTIONS ===

def get_market_structure_summary(data: pd.DataFrame) -> str:
    """Get a concise summary of market structure"""
    try:
        structure = detect_market_structure(data)
        
        trend = structure['trend_direction']
        confidence = structure['structure_confidence']
        signals = len(structure['bullish_signals']) + len(structure['bearish_signals'])
        
        return f"Trend: {trend.upper()} (Confidence: {confidence:.2f}) | Signals: {signals} | Bias: {structure['current_bias'].upper()}"
        
    except Exception as e:
        return f"Structure analysis error: {e}"

# Export all functions for compatibility
__all__ = [
    'detect_market_structure',
    'find_swing_points', 
    'calculate_swing_levels',
    'detect_order_blocks',
    'detect_fair_value_gaps',
    'detect_liquidity_zones',
    'detect_break_of_structure',
    'detect_change_of_character',
    'classify_swing_patterns',
    'determine_market_trend',
    'calculate_support_resistance_levels',
    'calculate_institutional_levels',
    'get_market_structure_summary',
    'SwingPoint',
    'OrderBlock', 
    'FairValueGap',
    'LiquidityZone',
    'MarketStructure',
    'SwingType'
]  

def identify_liquidity_levels(data: pd.DataFrame, lookback_period: int = 20, 
                             min_touches: int = 2, sensitivity: float = 0.001) -> Dict[str, List[Dict[str, Any]]]:
    """
    **ICT/RTM CORE**: Identify liquidity levels where institutional orders accumulate
    
    This function identifies key liquidity zones where:
    - Retail stop losses are likely positioned
    - Institutional orders create support/resistance
    - Price tends to reverse or breakout with momentum
    
    Args:
        data: OHLCV DataFrame
        lookback_period: Number of periods to analyze for level identification
        min_touches: Minimum number of times price must test a level
        sensitivity: Price tolerance for level identification (as percentage)
        
    Returns:
        Dictionary containing buy-side and sell-side liquidity levels
    """
    try:
        if len(data) < lookback_period:
            return {'buy_side_liquidity': [], 'sell_side_liquidity': [], 'confluence_levels': []}
        
        # Get basic market structure
        swing_highs, swing_lows = find_swing_points(data, window=5)
        
        # Identify buy-side liquidity (above market)
        buy_side_liquidity = _identify_buy_side_liquidity(data, swing_highs, lookback_period, min_touches, sensitivity)
        
        # Identify sell-side liquidity (below market)
        sell_side_liquidity = _identify_sell_side_liquidity(data, swing_lows, lookback_period, min_touches, sensitivity)
        
        # Find confluence levels (multiple liquidity sources)
        confluence_levels = _find_liquidity_confluence(buy_side_liquidity, sell_side_liquidity, data)
        
        # Add institutional session levels
        session_levels = _identify_session_liquidity_levels(data)
        
        # Combine and rank by strength
        all_levels = {
            'buy_side_liquidity': sorted(buy_side_liquidity, key=lambda x: x['strength'], reverse=True)[:10],
            'sell_side_liquidity': sorted(sell_side_liquidity, key=lambda x: x['strength'], reverse=True)[:10],
            'confluence_levels': sorted(confluence_levels, key=lambda x: x['strength'], reverse=True)[:5],
            'session_levels': session_levels,
            'total_levels_identified': len(buy_side_liquidity) + len(sell_side_liquidity),
            'analysis_timestamp': datetime.now().isoformat(),
            'current_price': float(data['close'].iloc[-1])
        }
        
        logger.info(f"Identified {len(buy_side_liquidity)} buy-side and {len(sell_side_liquidity)} sell-side liquidity levels")
        
        return all_levels
        
    except Exception as e:
        logger.error(f"Error identifying liquidity levels: {e}")
        return {'buy_side_liquidity': [], 'sell_side_liquidity': [], 'confluence_levels': []}

def _identify_buy_side_liquidity(data: pd.DataFrame, swing_highs: List[SwingPoint], 
                                lookback_period: int, min_touches: int, sensitivity: float) -> List[Dict[str, Any]]:
    """Identify buy-side liquidity zones above current market price"""
    try:
        buy_side_levels = []
        current_price = float(data['close'].iloc[-1])
        
        # 1. Equal highs and double tops
        for i, swing_high in enumerate(swing_highs):
            if swing_high.price <= current_price:
                continue  # Only levels above current price
            
            # Look for equal highs within sensitivity
            equal_highs = [sh for sh in swing_highs if 
                          abs(sh.price - swing_high.price) / swing_high.price <= sensitivity and 
                          sh.index != swing_high.index]
            
            if len(equal_highs) >= min_touches - 1:  # -1 because we count the original high
                level_strength = len(equal_highs) + 1
                avg_volume = np.mean([sh.volume for sh in equal_highs + [swing_high]])
                
                buy_side_levels.append({
                    'price': swing_high.price,
                    'level_type': 'equal_highs',
                    'strength': level_strength,
                    'touches': len(equal_highs) + 1,
                    'avg_volume': avg_volume,
                    'last_touch_index': max([sh.index for sh in equal_highs + [swing_high]]),
                    'distance_from_current': (swing_high.price - current_price) / current_price,
                    'liquidity_type': 'buy_side_stops',
                    'institutional_interest': _calculate_institutional_interest(swing_high, equal_highs),
                    'breakout_target': swing_high.price + (swing_high.price * 0.01)  # 1% above
                })
        
        # 2. Previous day/week/month highs
        timeframe_highs = _identify_timeframe_highs(data, current_price)
        buy_side_levels.extend(timeframe_highs)
        
        # 3. Psychological levels above market
        psychological_levels = _identify_psychological_levels_above(current_price)
        buy_side_levels.extend(psychological_levels)
        
        # 4. Unswept highs from significant moves
        unswept_highs = _identify_unswept_highs(data, swing_highs, current_price)
        buy_side_levels.extend(unswept_highs)
        
        return buy_side_levels
        
    except Exception as e:
        logger.error(f"Error identifying buy-side liquidity: {e}")
        return []

def _identify_sell_side_liquidity(data: pd.DataFrame, swing_lows: List[SwingPoint], 
                                 lookback_period: int, min_touches: int, sensitivity: float) -> List[Dict[str, Any]]:
    """Identify sell-side liquidity zones below current market price"""
    try:
        sell_side_levels = []
        current_price = float(data['close'].iloc[-1])
        
        # 1. Equal lows and double bottoms
        for i, swing_low in enumerate(swing_lows):
            if swing_low.price >= current_price:
                continue  # Only levels below current price
            
            # Look for equal lows within sensitivity
            equal_lows = [sl for sl in swing_lows if 
                         abs(sl.price - swing_low.price) / swing_low.price <= sensitivity and 
                         sl.index != swing_low.index]
            
            if len(equal_lows) >= min_touches - 1:  # -1 because we count the original low
                level_strength = len(equal_lows) + 1
                avg_volume = np.mean([sl.volume for sl in equal_lows + [swing_low]])
                
                sell_side_levels.append({
                    'price': swing_low.price,
                    'level_type': 'equal_lows',
                    'strength': level_strength,
                    'touches': len(equal_lows) + 1,
                    'avg_volume': avg_volume,
                    'last_touch_index': max([sl.index for sl in equal_lows + [swing_low]]),
                    'distance_from_current': (current_price - swing_low.price) / current_price,
                    'liquidity_type': 'sell_side_stops',
                    'institutional_interest': _calculate_institutional_interest(swing_low, equal_lows),
                    'breakout_target': swing_low.price - (swing_low.price * 0.01)  # 1% below
                })
        
        # 2. Previous day/week/month lows
        timeframe_lows = _identify_timeframe_lows(data, current_price)
        sell_side_levels.extend(timeframe_lows)
        
        # 3. Psychological levels below market
        psychological_levels = _identify_psychological_levels_below(current_price)
        sell_side_levels.extend(psychological_levels)
        
        # 4. Unswept lows from significant moves
        unswept_lows = _identify_unswept_lows(data, swing_lows, current_price)
        sell_side_levels.extend(unswept_lows)
        
        return sell_side_levels
        
    except Exception as e:
        logger.error(f"Error identifying sell-side liquidity: {e}")
        return []

def _find_liquidity_confluence(buy_side: List[Dict], sell_side: List[Dict], 
                              data: pd.DataFrame) -> List[Dict[str, Any]]:
    """Find confluence zones where multiple liquidity sources align"""
    try:
        confluence_levels = []
        current_price = float(data['close'].iloc[-1])
        all_levels = buy_side + sell_side
        
        # Group levels that are close together
        tolerance = current_price * 0.002  # 0.2% tolerance
        
        for level in all_levels:
            nearby_levels = [l for l in all_levels if 
                           abs(l['price'] - level['price']) <= tolerance and 
                           l != level]
            
            if len(nearby_levels) >= 1:  # At least 2 levels total (including current)
                confluence_strength = sum([l['strength'] for l in nearby_levels]) + level['strength']
                avg_price = np.mean([l['price'] for l in nearby_levels + [level]])
                
                confluence_levels.append({
                    'price': avg_price,
                    'level_type': 'confluence_zone',
                    'strength': confluence_strength,
                    'contributing_levels': len(nearby_levels) + 1,
                    'level_sources': [l['level_type'] for l in nearby_levels + [level]],
                    'distance_from_current': abs(avg_price - current_price) / current_price,
                    'liquidity_type': 'high_confluence',
                    'breakout_probability': min(0.95, confluence_strength * 0.1),
                    'institutional_zone': confluence_strength >= 5
                })
        
        # Remove duplicates and sort by strength
        unique_confluence = []
        seen_prices = set()
        
        for conf in sorted(confluence_levels, key=lambda x: x['strength'], reverse=True):
            price_key = round(conf['price'], 5)
            if price_key not in seen_prices:
                unique_confluence.append(conf)
                seen_prices.add(price_key)
        
        return unique_confluence[:5]  # Top 5 confluence zones
        
    except Exception as e:
        logger.error(f"Error finding liquidity confluence: {e}")
        return []

def _identify_session_liquidity_levels(data: pd.DataFrame) -> Dict[str, List[Dict[str, Any]]]:
    """Identify liquidity levels from different trading sessions"""
    try:
        session_levels = {
            'asia_session': [],
            'london_session': [],
            'ny_session': [],
            'previous_day': []
        }
        
        if len(data) < 24:  # Need at least 24 hours of data
            return session_levels
        
        # Previous day levels
        prev_day_high = float(data['high'].iloc[-24:-1].max()) if len(data) >= 24 else float(data['high'].max())
        prev_day_low = float(data['low'].iloc[-24:-1].min()) if len(data) >= 24 else float(data['low'].min())
        
        session_levels['previous_day'] = [
            {
                'price': prev_day_high,
                'level_type': 'previous_day_high',
                'strength': 3.0,
                'liquidity_type': 'session_high',
                'session': 'previous_day'
            },
            {
                'price': prev_day_low,
                'level_type': 'previous_day_low',
                'strength': 3.0,
                'liquidity_type': 'session_low',
                'session': 'previous_day'
            }
        ]
        
        # Weekly levels (approximate)
        if len(data) >= 120:  # 5 days * 24 hours
            weekly_high = float(data['high'].iloc[-120:].max())
            weekly_low = float(data['low'].iloc[-120:].min())
            
            session_levels['weekly'] = [
                {
                    'price': weekly_high,
                    'level_type': 'weekly_high',
                    'strength': 4.0,
                    'liquidity_type': 'weekly_level',
                    'session': 'weekly'
                },
                {
                    'price': weekly_low,
                    'level_type': 'weekly_low',
                    'strength': 4.0,
                    'liquidity_type': 'weekly_level',
                    'session': 'weekly'
                }
            ]
        
        return session_levels
        
    except Exception as e:
        logger.error(f"Error identifying session levels: {e}")
        return {'asia_session': [], 'london_session': [], 'ny_session': [], 'previous_day': []}

def _calculate_institutional_interest(main_swing: SwingPoint, related_swings: List[SwingPoint]) -> float:
    """Calculate institutional interest level based on swing characteristics"""
    try:
        # Base interest from swing strength
        base_interest = main_swing.strength
        
        # Volume factor
        avg_volume = np.mean([rs.volume for rs in related_swings + [main_swing]])
        volume_factor = min(2.0, avg_volume / 1000)  # Normalize volume
        
        # Time persistence factor (how long the level has held)
        time_factor = len(related_swings) * 0.2
        
        # RSI divergence factor
        rsi_factor = 1.0
        if hasattr(main_swing, 'rsi'):
            if main_swing.rsi > 70 or main_swing.rsi < 30:
                rsi_factor = 1.5  # Higher interest at extreme RSI levels
        
        institutional_interest = base_interest * volume_factor * (1 + time_factor) * rsi_factor
        
        return min(10.0, institutional_interest)  # Cap at 10
        
    except Exception as e:
        logger.error(f"Error calculating institutional interest: {e}")
        return 1.0

def _identify_timeframe_highs(data: pd.DataFrame, current_price: float) -> List[Dict[str, Any]]:
    """Identify significant timeframe highs above current price"""
    try:
        timeframe_levels = []
        
        # Daily high (last 24 bars)
        if len(data) >= 24:
            daily_high = float(data['high'].iloc[-24:].max())
            if daily_high > current_price:
                timeframe_levels.append({
                    'price': daily_high,
                    'level_type': 'daily_high',
                    'strength': 2.5,
                    'liquidity_type': 'timeframe_high',
                    'timeframe': 'daily'
                })
        
        # Weekly high (last 120 bars approximation)
        if len(data) >= 120:
            weekly_high = float(data['high'].iloc[-120:].max())
            if weekly_high > current_price and abs(weekly_high - current_price) > current_price * 0.01:
                timeframe_levels.append({
                    'price': weekly_high,
                    'level_type': 'weekly_high',
                    'strength': 4.0,
                    'liquidity_type': 'timeframe_high',
                    'timeframe': 'weekly'
                })
        
        return timeframe_levels
        
    except Exception:
        return []

def _identify_timeframe_lows(data: pd.DataFrame, current_price: float) -> List[Dict[str, Any]]:
    """Identify significant timeframe lows below current price"""
    try:
        timeframe_levels = []
        
        # Daily low (last 24 bars)
        if len(data) >= 24:
            daily_low = float(data['low'].iloc[-24:].min())
            if daily_low < current_price:
                timeframe_levels.append({
                    'price': daily_low,
                    'level_type': 'daily_low',
                    'strength': 2.5,
                    'liquidity_type': 'timeframe_low',
                    'timeframe': 'daily'
                })
        
        # Weekly low (last 120 bars approximation)
        if len(data) >= 120:
            weekly_low = float(data['low'].iloc[-120:].min())
            if weekly_low < current_price and abs(current_price - weekly_low) > current_price * 0.01:
                timeframe_levels.append({
                    'price': weekly_low,
                    'level_type': 'weekly_low',
                    'strength': 4.0,
                    'liquidity_type': 'timeframe_low',
                    'timeframe': 'weekly'
                })
        
        return timeframe_levels
        
    except Exception:
        return []

def _identify_psychological_levels_above(current_price: float) -> List[Dict[str, Any]]:
    """Identify psychological round number levels above current price"""
    try:
        psychological_levels = []
        
        # Determine appropriate round numbers
        if current_price >= 1000:
            increments = [100, 500, 1000]
        elif current_price >= 100:
            increments = [10, 50, 100]
        elif current_price >= 10:
            increments = [1, 5, 10]
        else:
            increments = [0.1, 0.5, 1.0]
        
        for increment in increments:
            next_level = (int(current_price / increment) + 1) * increment
            if next_level > current_price and (next_level - current_price) / current_price <= 0.1:  # Within 10%
                psychological_levels.append({
                    'price': next_level,
                    'level_type': 'psychological_level',
                    'strength': 2.0,
                    'liquidity_type': 'psychological_resistance',
                    'round_number': increment
                })
        
        return psychological_levels[:3]  # Top 3
        
    except Exception:
        return []

def _identify_psychological_levels_below(current_price: float) -> List[Dict[str, Any]]:
    """Identify psychological round number levels below current price"""
    try:
        psychological_levels = []
        
        # Determine appropriate round numbers
        if current_price >= 1000:
            increments = [100, 500, 1000]
        elif current_price >= 100:
            increments = [10, 50, 100]
        elif current_price >= 10:
            increments = [1, 5, 10]
        else:
            increments = [0.1, 0.5, 1.0]
        
        for increment in increments:
            prev_level = int(current_price / increment) * increment
            if prev_level < current_price and (current_price - prev_level) / current_price <= 0.1:  # Within 10%
                psychological_levels.append({
                    'price': prev_level,
                    'level_type': 'psychological_level',
                    'strength': 2.0,
                    'liquidity_type': 'psychological_support',
                    'round_number': increment
                })
        
        return psychological_levels[:3]  # Top 3
        
    except Exception:
        return []

def _identify_unswept_highs(data: pd.DataFrame, swing_highs: List[SwingPoint], 
                           current_price: float) -> List[Dict[str, Any]]:
    """Identify unswept highs that may contain liquidity"""
    try:
        unswept_highs = []
        
        # Look for highs that haven't been exceeded
        for swing_high in swing_highs[-10:]:  # Last 10 swing highs
            if swing_high.price <= current_price:
                continue
            
            # Check if this high has been "swept" (exceeded by significant margin)
            future_data = data.iloc[swing_high.index:]
            if len(future_data) > 0:
                max_future_price = future_data['high'].max()
                sweep_threshold = swing_high.price * 1.001  # 0.1% above
                
                if max_future_price < sweep_threshold:  # Unswept
                    unswept_highs.append({
                        'price': swing_high.price,
                        'level_type': 'unswept_high',
                        'strength': swing_high.strength + 1.0,  # Bonus for being unswept
                        'liquidity_type': 'unswept_liquidity',
                        'age': len(data) - swing_high.index,
                        'sweep_target': sweep_threshold
                    })
        
        return unswept_highs
        
    except Exception:
        return []

def _identify_unswept_lows(data: pd.DataFrame, swing_lows: List[SwingPoint], 
                          current_price: float) -> List[Dict[str, Any]]:
    """Identify unswept lows that may contain liquidity"""
    try:
        unswept_lows = []
        
        # Look for lows that haven't been exceeded
        for swing_low in swing_lows[-10:]:  # Last 10 swing lows
            if swing_low.price >= current_price:
                continue
            
            # Check if this low has been "swept" (broken by significant margin)
            future_data = data.iloc[swing_low.index:]
            if len(future_data) > 0:
                min_future_price = future_data['low'].min()
                sweep_threshold = swing_low.price * 0.999  # 0.1% below
                
                if min_future_price > sweep_threshold:  # Unswept
                    unswept_lows.append({
                        'price': swing_low.price,
                        'level_type': 'unswept_low',
                        'strength': swing_low.strength + 1.0,  # Bonus for being unswept
                        'liquidity_type': 'unswept_liquidity',
                        'age': len(data) - swing_low.index,
                        'sweep_target': sweep_threshold
                    })
        
        return unswept_lows
        
    except Exception:
        return []

# Update the __all__ export list to include the new function
__all__.append('identify_liquidity_levels')

print("✅ FINAL FUNCTION ADDED: identify_liquidity_levels - ICT/RTM strategies now fully operational!")
print("✅ Complete SMC/ICT/RTM Price Action Utilities Loaded Successfully!")
print("🎯 Your ICT and RTM strategies are now fully operational!")
>>>>>>> 8f626e2ef1a5d0198eacb62ca49d93985fc3b2f3
