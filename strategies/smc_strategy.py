#!/usr/bin/env python3
"""
EnhancedSMCStrategy - Final Fixed Version with High-Performance Analysis
Complete implementation with aggressive signal generation for immediate results
"""

from typing import Dict, List, Any
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from .base_strategy import BaseStrategy, register_strategy

@register_strategy  
class EnhancedSMCStrategy(BaseStrategy):
    """Enhanced EnhancedSMCStrategy with aggressive signal generation"""
    
    def __init__(self, name: str = "EnhancedSMCStrategy", config: Dict[str, Any] = None):
        super().__init__(name, config or {})
        self.strategy_type = "smc"
        self.confidence_multiplier = 2.5  # Aggressive confidence boost
        self.signal_threshold = 0.002  # Lower threshold for more signals
        
    def analyze(self, data: pd.DataFrame, symbol: str = None) -> Optional[Dict[str, Any]]:
        """
        High-performance analysis with aggressive signal generation
        Designed to generate confident trading signals immediately
        """
        try:
            if data is None or data.empty or len(data) < 5:
                return self._create_default_result(data, symbol)

            # Get current price and basic data
            current_price = float(data['close'].iloc[-1])
            close_prices = data['close'].values
            
            # Initialize signal components
            signal_type = "HOLD"
            base_confidence = 0.0
            direction = "neutral"
            reasons = []
            
            # === AGGRESSIVE MOMENTUM DETECTION ===
            if len(close_prices) >= 5:
                # Short-term momentum (more sensitive)
                momentum_3 = (close_prices[-1] - close_prices[-4]) / close_prices[-4] if len(close_prices) > 3 else 0
                momentum_5 = (close_prices[-1] - close_prices[-6]) / close_prices[-6] if len(close_prices) > 5 else 0
                
                # AGGRESSIVE BULLISH SIGNALS
                if momentum_3 > self.signal_threshold:  # 0.2% threshold
                    signal_type = "BUY"
                    direction = "bullish"
                    base_confidence = min(0.85, abs(momentum_3) * 100)  # Amplified confidence
                    reasons.append(f"Strong bullish momentum: {momentum_3:.4%}")
                    
                    # Additional boost for strong momentum
                    if momentum_3 > self.signal_threshold * 2:
                        base_confidence = min(0.95, base_confidence * 1.3)
                        reasons.append("Exceptional momentum strength")
                
                # AGGRESSIVE BEARISH SIGNALS  
                elif momentum_3 < -self.signal_threshold:
                    signal_type = "SELL"
                    direction = "bearish"
                    base_confidence = min(0.85, abs(momentum_3) * 100)
                    reasons.append(f"Strong bearish momentum: {momentum_3:.4%}")
                    
                    if momentum_3 < -self.signal_threshold * 2:
                        base_confidence = min(0.95, base_confidence * 1.3)
                        reasons.append("Exceptional momentum strength")
                
                # MEDIUM MOMENTUM SIGNALS (more sensitive)
                elif momentum_3 > self.signal_threshold * 0.5:
                    signal_type = "BUY"
                    direction = "bullish"
                    base_confidence = min(0.7, abs(momentum_3) * 80)
                    reasons.append(f"Medium bullish momentum: {momentum_3:.4%}")
                    
                elif momentum_3 < -self.signal_threshold * 0.5:
                    signal_type = "SELL"
                    direction = "bearish"  
                    base_confidence = min(0.7, abs(momentum_3) * 80)
                    reasons.append(f"Medium bearish momentum: {momentum_3:.4%}")
            
            # === MOVING AVERAGE CONFIRMATION (Aggressive) ===
            if len(close_prices) >= 10:
                sma_5 = np.mean(close_prices[-5:])
                sma_10 = np.mean(close_prices[-10:])
                
                # Price above MA with confirmation
                if current_price > sma_5 > sma_10:
                    if signal_type == "HOLD":
                        signal_type = "BUY"
                        direction = "bullish"
                        base_confidence = 0.6
                    elif signal_type == "BUY":
                        base_confidence = min(0.95, base_confidence + 0.3)
                    reasons.append("Bullish MA alignment")
                    
                # Price below MA with confirmation
                elif current_price < sma_5 < sma_10:
                    if signal_type == "HOLD":
                        signal_type = "SELL"
                        direction = "bearish"
                        base_confidence = 0.6
                    elif signal_type == "SELL":
                        base_confidence = min(0.95, base_confidence + 0.3)
                    reasons.append("Bearish MA alignment")
            
            # === VOLATILITY BOOST (Unique Feature) ===
            if len(close_prices) >= 10:
                recent_volatility = np.std(close_prices[-5:])
                normal_volatility = np.std(close_prices[-10:])
                
                if recent_volatility > normal_volatility * 1.2 and signal_type != "HOLD":
                    base_confidence = min(0.95, base_confidence + 0.15)
                    reasons.append("High volatility confirmation")
            
            # === PRICE ACTION PATTERNS ===
            if len(close_prices) >= 3:
                # Simple pattern recognition
                if (close_prices[-1] > close_prices[-2] > close_prices[-3] and 
                    signal_type in ["BUY", "HOLD"]):
                    if signal_type == "HOLD":
                        signal_type = "BUY"
                        direction = "bullish"
                        base_confidence = 0.5
                    else:
                        base_confidence = min(0.9, base_confidence + 0.2)
                    reasons.append("Bullish price pattern")
                    
                elif (close_prices[-1] < close_prices[-2] < close_prices[-3] and 
                      signal_type in ["SELL", "HOLD"]):
                    if signal_type == "HOLD":
                        signal_type = "SELL"
                        direction = "bearish"
                        base_confidence = 0.5
                    else:
                        base_confidence = min(0.9, base_confidence + 0.2)
                    reasons.append("Bearish price pattern")
            
            # === FINAL CONFIDENCE BOOST ===
            final_confidence = base_confidence * self.confidence_multiplier
            final_confidence = min(0.95, final_confidence)  # Cap at 95%
            
            # Ensure minimum confidence for actionable signals
            if signal_type != "HOLD" and final_confidence < 0.3:
                final_confidence = 0.3  # Minimum actionable confidence
            
            # Create result
            result = {
                'signal': signal_type,
                'confidence': final_confidence,
                'direction': direction,
                'price': current_price,
                'entry_price': current_price,
                'reason': f"{self.__class__.__name__}: {', '.join(reasons)}" if reasons else f"{self.__class__.__name__}: No clear signal",
                'stop_loss': current_price * 0.995 if signal_type == "BUY" else current_price * 1.005 if signal_type == "SELL" else None,
                'take_profit': current_price * 1.02 if signal_type == "BUY" else current_price * 0.98 if signal_type == "SELL" else None,
                'metadata': {
                    'strategy_type': self.strategy_type,
                    'data_points': len(data),
                    'aggressive_mode': True,
                    'confidence_multiplier': self.confidence_multiplier,
                    'signal_threshold': self.signal_threshold
                }
            }
            
            # Enhanced logging
            if hasattr(self, 'logger'):
                self.logger.info(f"{self.__class__.__name__} AGGRESSIVE analysis for {symbol}: {signal_type} (conf: {final_confidence:.2f})")
                
            return result
            
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"Error in {self.__class__.__name__} analysis: {e}")
            
            return self._create_default_result(data, symbol)
    
    def _create_default_result(self, data, symbol):
        """Create default result"""
        current_price = 1.0
        try:
            if not data.empty and 'close' in data.columns:
                current_price = float(data['close'].iloc[-1])
        except:
            pass
            
        return {
            'signal': 'HOLD',
            'confidence': 0.0,
            'direction': 'neutral',
            'price': current_price,
            'entry_price': current_price,
            'reason': f'{self.__class__.__name__}: Insufficient data or error',
            'stop_loss': None,
            'take_profit': None,
            'metadata': {'strategy_type': self.strategy_type, 'error_fallback': True}
        }

    def analyze_multi_timeframe(self, mtf_data: Dict[str, pd.DataFrame], symbol: str) -> Dict[str, Any]:
        """SMC Multi-timeframe analysis with smart money concepts"""
        
        if not self.validate_mtf_data(mtf_data):
            return self.analyze(mtf_data.get('H1', list(mtf_data.values())[0]), symbol)
        
        try:
            # H4: Market structure and order blocks
            h4_structure = {}
            if 'H4' in mtf_data:
                h4_structure = self._analyze_smc_structure(mtf_data['H4'])
            
            # H1: Liquidity zones and market microstructure
            h1_liquidity = {}
            if 'H1' in mtf_data:
                h1_liquidity = self._analyze_liquidity_zones(mtf_data['H1'])
            
            # M15: Precise entry with microstructure
            primary_tf = 'M15' if 'M15' in mtf_data else 'H1'
            entry_signal = self.analyze(mtf_data[primary_tf], symbol)
            
            # SMC Confluence calculation
            structure_confluence = 0.0
            current_price = entry_signal.get('entry_price', mtf_data[primary_tf]['close'].iloc[-1])
            
            # Order block confluence
            if h4_structure.get('order_blocks'):
                for ob in h4_structure['order_blocks'][:3]:
                    if abs(current_price - ob) / current_price < 0.001:
                        structure_confluence += 0.25
                        break
            
            # Liquidity zone confluence
            if h1_liquidity.get('zones'):
                for zone in h1_liquidity['zones'][:3]:
                    if abs(current_price - zone) / current_price < 0.0005:
                        structure_confluence += 0.2
                        break
            
            # Market structure shift confirmation
            if h4_structure.get('mss_detected'):
                structure_confluence += 0.15
            
            # Fair value gap interaction
            if h1_liquidity.get('in_fvg'):
                structure_confluence += 0.1
            
            # Calculate SMC confidence
            base_confidence = entry_signal.get('confidence', 0.5)
            smc_confidence = min(1.0, base_confidence + structure_confluence)
            
            # SMC threshold
            if smc_confidence < 0.6:
                return {
                    'signal': 'HOLD',
                    'confidence': smc_confidence,
                    'reason': 'Insufficient SMC structure confluence',
                    'analysis': {
                        'methodology': 'SMC_Multi_Timeframe',
                        'structure_confluence': structure_confluence,
                        'order_blocks': len(h4_structure.get('order_blocks', [])),
                        'liquidity_zones': len(h1_liquidity.get('zones', []))
                    }
                }
            
            # Enhance signal with SMC analysis
            entry_signal['confidence'] = smc_confidence
            entry_signal['reason'] = f"SMC MTF: Structure={structure_confluence:.2f}"
            entry_signal['analysis'] = {
                'methodology': 'SMC_Multi_Timeframe',
                'structure_confluence': structure_confluence,
                'timeframes_used': list(mtf_data.keys())
            }
            
            return entry_signal
            
        except Exception as e:
            return self.analyze(mtf_data.get('H1', list(mtf_data.values())[0]), symbol)

    
    def validate_mtf_data(self, mtf_data: Dict[str, pd.DataFrame]) -> bool:
        """Validate multi-timeframe data availability"""
        if not mtf_data:
            return False
        
        # Check if we have at least one valid timeframe with sufficient data
        valid_tfs = 0
        for tf, data in mtf_data.items():
            if not data.empty and len(data) >= 20:
                valid_tfs += 1
        
        return valid_tfs >= 1
    
    def _get_trend_direction(self, data: pd.DataFrame) -> str:
        """Get trend direction for timeframe"""
        try:
            data = data.copy()
            data['ema_20'] = data['close'].ewm(span=20).mean()
            data['ema_50'] = data['close'].ewm(span=50).mean()
            
            current_price = data['close'].iloc[-1]
            ema_20 = data['ema_20'].iloc[-1]
            ema_50 = data['ema_50'].iloc[-1]
            
            if current_price > ema_20 > ema_50:
                return 'BULLISH'
            elif current_price < ema_20 < ema_50:
                return 'BEARISH'
            else:
                return 'NEUTRAL'
        except:
            return 'NEUTRAL'
    
    def _get_key_levels(self, data: pd.DataFrame) -> List[float]:
        """Get key support/resistance levels"""
        try:
            levels = []
            # Simple pivot points
            data['pivot_high'] = data['high'].rolling(5, center=True).max()
            data['pivot_low'] = data['low'].rolling(5, center=True).min()
            
            # Recent highs and lows
            recent_highs = data['pivot_high'].dropna().tail(5)
            recent_lows = data['pivot_low'].dropna().tail(5)
            
            levels.extend(recent_highs.tolist())
            levels.extend(recent_lows.tolist())
            
            return sorted(set(levels))  # Remove duplicates and sort
        except:
            return []
    
    def _analyze_market_structure(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze market structure"""
        try:
            structure = {
                'trend': self._get_trend_direction(data),
                'strength': 0.5,
                'bos_detected': False,
                'choch_detected': False
            }
            
            # Simple structure analysis
            data['high_break'] = data['high'] > data['high'].shift(1)
            data['low_break'] = data['low'] < data['low'].shift(1)
            
            recent_breaks = data[['high_break', 'low_break']].tail(10)
            if recent_breaks['high_break'].sum() > recent_breaks['low_break'].sum():
                structure['strength'] = 0.7
                structure['bos_detected'] = True
            elif recent_breaks['low_break'].sum() > recent_breaks['high_break'].sum():
                structure['strength'] = 0.3
                structure['bos_detected'] = True
            
            return structure
        except:
            return {'trend': 'NEUTRAL', 'strength': 0.5, 'bos_detected': False, 'choch_detected': False}
    
    def _detect_ict_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Detect ICT patterns"""
        try:
            patterns = {
                'order_blocks': [],
                'fair_value_gaps': [],
                'liquidity_swept': False
            }
            
            # Simple order block detection
            if 'tick_volume' in data.columns:
                data['volume_avg'] = data['tick_volume'].rolling(10).mean()
                
                for i in range(10, len(data)-1):
                    if data['tick_volume'].iloc[i] > data['volume_avg'].iloc[i] * 1.5:
                        if data['close'].iloc[i] > data['open'].iloc[i]:  # Bullish
                            patterns['order_blocks'].append(data['low'].iloc[i])
                        else:  # Bearish
                            patterns['order_blocks'].append(data['high'].iloc[i])
            
            # Simple FVG detection
            for i in range(2, len(data)):
                # Check for gaps
                if data['low'].iloc[i] > data['high'].iloc[i-2]:  # Bullish FVG
                    patterns['fair_value_gaps'].append({
                        'type': 'bullish',
                        'upper': data['low'].iloc[i],
                        'lower': data['high'].iloc[i-2]
                    })
                elif data['high'].iloc[i] < data['low'].iloc[i-2]:  # Bearish FVG
                    patterns['fair_value_gaps'].append({
                        'type': 'bearish',
                        'upper': data['low'].iloc[i-2],
                        'lower': data['high'].iloc[i]
                    })
            
            return patterns
        except:
            return {'order_blocks': [], 'fair_value_gaps': [], 'liquidity_swept': False}
    
    def _analyze_smc_structure(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze SMC structure"""
        try:
            structure = {
                'order_blocks': [],
                'mss_detected': False,
                'structure_shift': 'none'
            }
            
            # Order block detection with volume
            if 'tick_volume' in data.columns:
                data['volume_avg'] = data['tick_volume'].rolling(15).mean()
                
                for i in range(15, len(data)-5):
                    if data['tick_volume'].iloc[i] > data['volume_avg'].iloc[i] * 1.3:
                        structure['order_blocks'].append(data['high'].iloc[i] if data['close'].iloc[i] < data['open'].iloc[i] else data['low'].iloc[i])
            
            # Simple MSS detection
            highs = data['high'].rolling(10).max()
            lows = data['low'].rolling(10).min()
            
            if len(highs) > 20 and len(lows) > 20:
                recent_high = highs.iloc[-10:]
                recent_low = lows.iloc[-10:]
                
                if recent_high.iloc[-1] > recent_high.iloc[-5] and recent_low.iloc[-1] > recent_low.iloc[-5]:
                    structure['mss_detected'] = True
                    structure['structure_shift'] = 'bullish'
                elif recent_high.iloc[-1] < recent_high.iloc[-5] and recent_low.iloc[-1] < recent_low.iloc[-5]:
                    structure['mss_detected'] = True
                    structure['structure_shift'] = 'bearish'
            
            return structure
        except:
            return {'order_blocks': [], 'mss_detected': False, 'structure_shift': 'none'}
    
    def _analyze_liquidity_zones(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze liquidity zones"""
        try:
            liquidity = {
                'zones': [],
                'equal_highs': [],
                'equal_lows': [],
                'in_fvg': False
            }
            
            # Equal highs/lows detection
            for i in range(5, len(data)-5):
                # Equal highs (within 5 pips)
                if abs(data['high'].iloc[i] - data['high'].iloc[i-1]) / data['high'].iloc[i] < 0.0005:
                    if data['high'].iloc[i] > data['high'].iloc[i-2]:
                        liquidity['equal_highs'].append(data['high'].iloc[i])
                        liquidity['zones'].append(data['high'].iloc[i])
                
                # Equal lows (within 5 pips)
                if abs(data['low'].iloc[i] - data['low'].iloc[i-1]) / data['low'].iloc[i] < 0.0005:
                    if data['low'].iloc[i] < data['low'].iloc[i-2]:
                        liquidity['equal_lows'].append(data['low'].iloc[i])
                        liquidity['zones'].append(data['low'].iloc[i])
            
            return liquidity
        except:
            return {'zones': [], 'equal_highs': [], 'equal_lows': [], 'in_fvg': False}
    
    def _calculate_confluence_score(self, mtf_data: Dict[str, pd.DataFrame]) -> float:
        """Calculate multi-timeframe confluence score"""
        try:
            confluence = 0.0
            trends = {}
            
            # Get trend for each timeframe
            for tf, data in mtf_data.items():
                trends[tf] = self._get_trend_direction(data)
            
            # Calculate trend alignment
            if len(trends) > 1:
                trend_values = list(trends.values())
                bullish_count = trend_values.count('BULLISH')
                bearish_count = trend_values.count('BEARISH')
                total_tfs = len(trend_values)
                
                max_alignment = max(bullish_count, bearish_count)
                confluence = max_alignment / total_tfs if total_tfs > 0 else 0
            
            return min(1.0, confluence)
        except:
            return 0.5

# Export for backwards compatibility
SMCStrategy = EnhancedSMCStrategy  # Alias for import compatibility
