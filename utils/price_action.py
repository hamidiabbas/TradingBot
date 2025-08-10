"""
Shared price action primitives for ICT and RTM strategies.
Common functions for swing point detection, market structure analysis, etc.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class SwingPoint:
    """Represents a swing high or swing low point"""
    index: int
    price: float
    timestamp: pd.Timestamp
    swing_type: str  # 'high' or 'low'
    strength: int  # lookback period used for detection

@dataclass
class MarketStructure:
    """Market structure analysis result"""
    trend: str  # 'uptrend', 'downtrend', 'sideways'
    structure_type: str  # 'HH_HL', 'LH_LL', 'range'
    last_structure_break: Optional[pd.Timestamp]
    confidence: float  # 0.0 to 1.0

def find_swing_points(data: pd.DataFrame, lookback: int = 5) -> pd.DataFrame:
    """
    Identify significant swing highs and swing lows in price data.
    
    A swing high is a high that is higher than the highs of 'lookback' candles 
    before and after it. A swing low is the inverse.
    
    Args:
        data: OHLCV DataFrame with 'high' and 'low' columns
        lookback: Number of candles to look back and forward
        
    Returns:
        DataFrame with swing points including columns:
        - swing_type: 'high' or 'low'
        - price: swing point price
        - strength: confirmation strength
    """
    if len(data) < (2 * lookback + 1):
        return pd.DataFrame(columns=['swing_type', 'price', 'strength'])
    
    highs = data['high'].values
    lows = data['low'].values
    swing_points = []
    
    # Find swing highs
    for i in range(lookback, len(highs) - lookback):
        is_swing_high = True
        current_high = highs[i]
        
        # Check if current high is higher than previous and next 'lookback' candles
        for j in range(i - lookback, i + lookback + 1):
            if j != i and highs[j] >= current_high:
                is_swing_high = False
                break
        
        if is_swing_high:
            swing_points.append({
                'index': i,
                'swing_type': 'high',
                'price': current_high,
                'strength': lookback,
                'timestamp': data.index[i]
            })
    
    # Find swing lows
    for i in range(lookback, len(lows) - lookback):
        is_swing_low = True
        current_low = lows[i]
        
        # Check if current low is lower than previous and next 'lookback' candles
        for j in range(i - lookback, i + lookback + 1):
            if j != i and lows[j] <= current_low:
                is_swing_low = False
                break
        
        if is_swing_low:
            swing_points.append({
                'index': i,
                'swing_type': 'low',
                'price': current_low,
                'strength': lookback,
                'timestamp': data.index[i]
            })
    
    if not swing_points:
        return pd.DataFrame(columns=['swing_type', 'price', 'strength', 'timestamp'])
    
    swing_df = pd.DataFrame(swing_points)
    swing_df.set_index('timestamp', inplace=True)
    swing_df.sort_index(inplace=True)
    
    return swing_df

def detect_market_structure(swing_points: pd.DataFrame) -> MarketStructure:
    """
    Analyze sequence of swing points to determine market structure.
    
    Args:
        swing_points: DataFrame from find_swing_points()
        
    Returns:
        MarketStructure object with trend analysis
    """
    if len(swing_points) < 4:
        return MarketStructure(
            trend='sideways',
            structure_type='insufficient_data',
            last_structure_break=None,
            confidence=0.0
        )
    
    # Separate highs and lows
    highs = swing_points[swing_points['swing_type'] == 'high'].copy()
    lows = swing_points[swing_points['swing_type'] == 'low'].copy()
    
    if len(highs) < 2 or len(lows) < 2:
        return MarketStructure(
            trend='sideways',
            structure_type='insufficient_swings',
            last_structure_break=None,
            confidence=0.0
        )
    
    # Analyze recent swing highs (last 3)
    recent_highs = highs.tail(3)['price'].values
    recent_lows = lows.tail(3)['price'].values
    
    # Check for Higher Highs and Higher Lows (HH/HL)
    hh_hl_score = 0
    if len(recent_highs) >= 2:
        if recent_highs[-1] > recent_highs[-2]:
            hh_hl_score += 1
        if len(recent_highs) >= 3 and recent_highs[-2] > recent_highs[-3]:
            hh_hl_score += 1
    
    if len(recent_lows) >= 2:
        if recent_lows[-1] > recent_lows[-2]:
            hh_hl_score += 1
        if len(recent_lows) >= 3 and recent_lows[-2] > recent_lows[-3]:
            hh_hl_score += 1
    
    # Check for Lower Highs and Lower Lows (LH/LL)
    lh_ll_score = 0
    if len(recent_highs) >= 2:
        if recent_highs[-1] < recent_highs[-2]:
            lh_ll_score += 1
        if len(recent_highs) >= 3 and recent_highs[-2] < recent_highs[-3]:
            lh_ll_score += 1
    
    if len(recent_lows) >= 2:
        if recent_lows[-1] < recent_lows[-2]:
            lh_ll_score += 1
        if len(recent_lows) >= 3 and recent_lows[-2] < recent_lows[-3]:
            lh_ll_score += 1
    
    # Determine trend based on scores
    max_score = 4  # Maximum possible score
    hh_hl_confidence = hh_hl_score / max_score
    lh_ll_confidence = lh_ll_score / max_score
    
    if hh_hl_confidence >= 0.5 and hh_hl_confidence > lh_ll_confidence:
        trend = 'uptrend'
        structure_type = 'HH_HL'
        confidence = hh_hl_confidence
    elif lh_ll_confidence >= 0.5 and lh_ll_confidence > hh_hl_confidence:
        trend = 'downtrend'
        structure_type = 'LH_LL'
        confidence = lh_ll_confidence
    else:
        trend = 'sideways'
        structure_type = 'range'
        confidence = 1.0 - max(hh_hl_confidence, lh_ll_confidence)
    
    return MarketStructure(
        trend=trend,
        structure_type=structure_type,
        last_structure_break=None,  # TODO: Implement structure break detection
        confidence=confidence
    )

def detect_break_of_structure(data: pd.DataFrame, swing_points: pd.DataFrame) -> pd.Series:
    """
    Identify Break of Structure (BOS) - price closing beyond previous swing in trend direction.
    
    Args:
        data: OHLCV DataFrame
        swing_points: DataFrame from find_swing_points()
        
    Returns:
        Series with BOS signals (1 for bullish BOS, -1 for bearish BOS, 0 for none)
    """
    bos_signals = pd.Series(0, index=data.index, name='BOS')
    
    if len(swing_points) < 2:
        return bos_signals
    
    # Get market structure
    market_structure = detect_market_structure(swing_points)
    
    # Separate highs and lows
    highs = swing_points[swing_points['swing_type'] == 'high']
    lows = swing_points[swing_points['swing_type'] == 'low']
    
    # In uptrend, look for breaks above recent swing highs
    if market_structure.trend == 'uptrend' and len(highs) >= 1:
        last_swing_high = highs.iloc[-1]
        last_high_price = last_swing_high['price']
        last_high_time = last_swing_high.name
        
        # Check for closes above the last swing high after its formation
        after_swing = data[data.index > last_high_time]
        bullish_breaks = after_swing['close'] > last_high_price
        
        for timestamp, is_break in bullish_breaks.items():
            if is_break:
                bos_signals[timestamp] = 1
                break  # Only mark the first break
    
    # In downtrend, look for breaks below recent swing lows
    elif market_structure.trend == 'downtrend' and len(lows) >= 1:
        last_swing_low = lows.iloc[-1]
        last_low_price = last_swing_low['price']
        last_low_time = last_swing_low.name
        
        # Check for closes below the last swing low after its formation
        after_swing = data[data.index > last_low_time]
        bearish_breaks = after_swing['close'] < last_low_price
        
        for timestamp, is_break in bearish_breaks.items():
            if is_break:
                bos_signals[timestamp] = -1
                break  # Only mark the first break
    
    return bos_signals

def detect_change_of_character(data: pd.DataFrame, swing_points: pd.DataFrame) -> pd.Series:
    """
    Identify Change of Character (ChoCH) - price closing beyond previous swing against trend direction.
    
    Args:
        data: OHLCV DataFrame
        swing_points: DataFrame from find_swing_points()
        
    Returns:
        Series with ChoCH signals (1 for bullish ChoCH, -1 for bearish ChoCH, 0 for none)
    """
    choch_signals = pd.Series(0, index=data.index, name='ChoCH')
    
    if len(swing_points) < 2:
        return choch_signals
    
    # Get market structure
    market_structure = detect_market_structure(swing_points)
    
    # Separate highs and lows
    highs = swing_points[swing_points['swing_type'] == 'high']
    lows = swing_points[swing_points['swing_type'] == 'low']
    
    # In uptrend, look for breaks below recent swing lows (against trend)
    if market_structure.trend == 'uptrend' and len(lows) >= 1:
        last_swing_low = lows.iloc[-1]
        last_low_price = last_swing_low['price']
        last_low_time = last_swing_low.name
        
        # Check for closes below the last swing low after its formation
        after_swing = data[data.index > last_low_time]
        bearish_breaks = after_swing['close'] < last_low_price
        
        for timestamp, is_break in bearish_breaks.items():
            if is_break:
                choch_signals[timestamp] = -1  # Bearish ChoCH in uptrend
                break  # Only mark the first break
    
    # In downtrend, look for breaks above recent swing highs (against trend)
    elif market_structure.trend == 'downtrend' and len(highs) >= 1:
        last_swing_high = highs.iloc[-1]
        last_high_price = last_swing_high['price']
        last_high_time = last_swing_high.name
        
        # Check for closes above the last swing high after its formation
        after_swing = data[data.index > last_high_time]
        bullish_breaks = after_swing['close'] > last_high_price
        
        for timestamp, is_break in bullish_breaks.items():
            if is_break:
                choch_signals[timestamp] = 1  # Bullish ChoCH in downtrend
                break  # Only mark the first break
    
    return choch_signals

def identify_liquidity_levels(swing_points: pd.DataFrame, min_touch_count: int = 2) -> pd.DataFrame:
    """
    Identify key liquidity levels based on swing points.
    
    Args:
        swing_points: DataFrame from find_swing_points()
        min_touch_count: Minimum number of touches to consider a level significant
        
    Returns:
        DataFrame with liquidity levels and their properties
    """
    if len(swing_points) < min_touch_count:
        return pd.DataFrame(columns=['level', 'type', 'strength', 'touch_count'])
    
    levels = []
    
    # Group nearby swing points (within small price range)
    highs = swing_points[swing_points['swing_type'] == 'high']['price'].values
    lows = swing_points[swing_points['swing_type'] == 'low']['price'].values
    
    # Find resistance levels from swing highs
    for i, high in enumerate(highs):
        touches = 1
        nearby_highs = []
        
        for j, other_high in enumerate(highs):
            if i != j:
                # Consider levels within 0.1% of each other as the same level
                price_diff = abs(high - other_high) / high
                if price_diff <= 0.001:  # 0.1%
                    touches += 1
                    nearby_highs.append(other_high)
        
        if touches >= min_touch_count:
            avg_level = np.mean([high] + nearby_highs)
            levels.append({
                'level': avg_level,
                'type': 'resistance',
                'strength': touches,
                'touch_count': touches
            })
    
    # Find support levels from swing lows
    for i, low in enumerate(lows):
        touches = 1
        nearby_lows = []
        
        for j, other_low in enumerate(lows):
            if i != j:
                # Consider levels within 0.1% of each other as the same level
                price_diff = abs(low - other_low) / low
                if price_diff <= 0.001:  # 0.1%
                    touches += 1
                    nearby_lows.append(other_low)
        
        if touches >= min_touch_count:
            avg_level = np.mean([low] + nearby_lows)
            levels.append({
                'level': avg_level,
                'type': 'support',
                'strength': touches,
                'touch_count': touches
            })
    
    if not levels:
        return pd.DataFrame(columns=['level', 'type', 'strength', 'touch_count'])
    
    levels_df = pd.DataFrame(levels)
    levels_df = levels_df.drop_duplicates('level').sort_values('strength', ascending=False)
    
    return levels_df

def calculate_fibonacci_levels(swing_high: float, swing_low: float) -> Dict[str, float]:
    """
    Calculate Fibonacci retracement levels between swing high and low.
    
    Args:
        swing_high: Higher price point
        swing_low: Lower price point
        
    Returns:
        Dictionary with Fibonacci levels
    """
    price_range = swing_high - swing_low
    
    fib_levels = {
        '0.0': swing_high,
        '23.6': swing_high - (price_range * 0.236),
        '38.2': swing_high - (price_range * 0.382),
        '50.0': swing_high - (price_range * 0.5),
        '61.8': swing_high - (price_range * 0.618),
        '78.6': swing_high - (price_range * 0.786),
        '100.0': swing_low
    }
    
    return fib_levels

def detect_divergence(price_data: pd.Series, indicator_data: pd.Series, swing_points: pd.DataFrame) -> pd.DataFrame:
    """
    Detect bullish and bearish divergences between price and an indicator.
    
    Args:
        price_data: Price series (typically 'close')
        indicator_data: Indicator series (e.g., RSI, MACD)
        swing_points: DataFrame from find_swing_points()
        
    Returns:
        DataFrame with divergence signals
    """
    divergences = []
    
    # Get swing highs and lows separately
    swing_highs = swing_points[swing_points['swing_type'] == 'high']
    swing_lows = swing_points[swing_points['swing_type'] == 'low']
    
    # Check for bearish divergence at swing highs
    if len(swing_highs) >= 2:
        for i in range(1, len(swing_highs)):
            current_high = swing_highs.iloc[i]
            previous_high = swing_highs.iloc[i-1]
            
            current_time = current_high.name
            previous_time = previous_high.name
            
            # Price makes higher high, but indicator makes lower high
            price_higher = current_high['price'] > previous_high['price']
            indicator_lower = indicator_data[current_time] < indicator_data[previous_time]
            
            if price_higher and indicator_lower:
                divergences.append({
                    'timestamp': current_time,
                    'type': 'bearish',
                    'price_level': current_high['price'],
                    'strength': abs(indicator_data[current_time] - indicator_data[previous_time])
                })
    
    # Check for bullish divergence at swing lows
    if len(swing_lows) >= 2:
        for i in range(1, len(swing_lows)):
            current_low = swing_lows.iloc[i]
            previous_low = swing_lows.iloc[i-1]
            
            current_time = current_low.name
            previous_time = previous_low.name
            
            # Price makes lower low, but indicator makes higher low
            price_lower = current_low['price'] < previous_low['price']
            indicator_higher = indicator_data[current_time] > indicator_data[previous_time]
            
            if price_lower and indicator_higher:
                divergences.append({
                    'timestamp': current_time,
                    'type': 'bullish',
                    'price_level': current_low['price'],
                    'strength': abs(indicator_data[current_time] - indicator_data[previous_time])
                })
    
    if not divergences:
        return pd.DataFrame(columns=['timestamp', 'type', 'price_level', 'strength'])
    
    divergence_df = pd.DataFrame(divergences)
    divergence_df.set_index('timestamp', inplace=True)
    
    return divergence_df
