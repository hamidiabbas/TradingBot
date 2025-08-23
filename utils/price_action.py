"""
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
        
        swing_highs = []
        swing_lows = []
        
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
