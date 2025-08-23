import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

@dataclass
class ProfessionalLevel:
    """Professional S&R level with metadata"""
    price: float
    strength: float
    touches: int
    age: int
    volume_confirmation: float
    level_type: str  # 'support', 'resistance', 'pivot'

class ProfessionalSupportResistanceStrategy:
    """
    INSTITUTIONAL-GRADE SUPPORT/RESISTANCE STRATEGY
    ==============================================
    
    Professional features:
    ✅ Multi-timeframe level detection
    ✅ Statistical strength validation
    ✅ Volume-confirmed breakouts
    ✅ False breakout filtering
    ✅ Dynamic risk management
    ✅ Market structure analysis
    ✅ Institutional-grade filtering
    """
    
    def __init__(self):
        self.name = "ProfessionalSupportResistanceStrategy"
        
        # Professional Parameters
        self.min_level_strength = 0.70      # Minimum level quality
        self.min_breakout_strength = 0.75   # Minimum breakout confidence
        self.min_confidence = 0.72          # High-quality signals only
        self.false_breakout_filter = True   # Advanced breakout validation
        
        # Multi-timeframe Analysis
        self.timeframes = [20, 35, 50]      # Multiple lookback periods
        self.volume_confirmation = True      # Volume-based validation
        
        # Risk Management
        self.min_risk_reward = 2.5          # Minimum 2.5:1 RR
        self.max_risk_per_trade = 0.02      # 2% max risk
        
        # Professional Features
        self.market_structure_analysis = True
        self.session_filtering = True
        self.volatility_adaptation = True
        
        logging.info("🚀 Professional S&R Strategy initialized")
    
    def analyze(self, data: pd.DataFrame, symbol: str = "EURUSD") -> Dict[str, Any]:
        """
        PROFESSIONAL S&R ANALYSIS PIPELINE
        =================================
        Institutional-grade breakout detection
        """
        try:
            if len(data) < 60:
                return self._no_signal(data, "Insufficient data for professional analysis")
            
            # Stage 1: Multi-timeframe Level Detection
            professional_levels = self._detect_professional_levels(data)
            
            if not professional_levels:
                return self._no_signal(data, "No professional-grade levels detected")
            
            # Stage 2: Market Structure Analysis
            market_structure = self._analyze_market_structure(data)
            
            # Stage 3: Breakout Detection & Validation
            breakout_analysis = self._detect_professional_breakout(data, professional_levels)
            
            if not breakout_analysis['is_breakout']:
                return self._no_signal(data, breakout_analysis['reason'])
            
            # Stage 4: Volume Confirmation
            volume_confirmation = self._analyze_breakout_volume(data, breakout_analysis)
            
            # Stage 5: False Breakout Filter
            if self.false_breakout_filter:
                false_breakout_risk = self._assess_false_breakout_risk(data, breakout_analysis)
                if false_breakout_risk > 0.4:
                    return self._no_signal(data, f"High false breakout risk: {false_breakout_risk:.3f}")
            
            # Stage 6: Professional Signal Generation
            signal = self._generate_professional_breakout_signal(
                data, breakout_analysis, market_structure, volume_confirmation
            )
            
            # Stage 7: Risk-Reward Optimization
            if signal['signal'] != 'HOLD':
                signal = self._optimize_professional_risk_reward(signal, data, breakout_analysis)
            
            # Stage 8: Final Validation
            return self._apply_institutional_filters(signal, data)
            
        except Exception as e:
            logging.error(f"Professional S&R analysis error: {e}")
            return self._no_signal(data, f"Analysis error: {str(e)}")
    
    def _detect_professional_levels(self, data: pd.DataFrame) -> List[ProfessionalLevel]:
        """
        MULTI-TIMEFRAME LEVEL DETECTION
        ===============================
        Advanced level detection with strength validation
        """
        try:
            all_levels = []
            current_price = data['close'].iloc[-1]
            
            for timeframe in self.timeframes:
                if len(data) >= timeframe * 2:
                    # Detect pivot points
                    highs = data['high'].values
                    lows = data['low'].values
                    volumes = data.get('volume', pd.Series([1000] * len(data))).values
                    
                    # Find peaks and troughs
                    peak_indices = argrelextrema(highs, np.greater, order=max(3, timeframe//10))
                    trough_indices = argrelextrema(lows, np.less, order=max(3, timeframe//10))
                    
                    # Process resistance levels
                    for idx in peak_indices:
                        if idx < len(highs) - 5:  # Not too recent
                            level_price = highs[idx]
                            level_strength = self._calculate_level_strength(data, level_price, 'resistance')
                            touches = self._count_level_touches(data, level_price, 'resistance')
                            
                            if level_strength >= self.min_level_strength and touches >= 2:
                                age = len(data) - idx
                                volume_conf = self._calculate_volume_confirmation(data, idx, volumes)
                                
                                all_levels.append(ProfessionalLevel(
                                    price=level_price,
                                    strength=level_strength,
                                    touches=touches,
                                    age=age,
                                    volume_confirmation=volume_conf,
                                    level_type='resistance'
                                ))
                    
                    # Process support levels
                    for idx in trough_indices:
                        if idx < len(lows) - 5:
                            level_price = lows[idx]
                            level_strength = self._calculate_level_strength(data, level_price, 'support')
                            touches = self._count_level_touches(data, level_price, 'support')
                            
                            if level_strength >= self.min_level_strength and touches >= 2:
                                age = len(data) - idx
                                volume_conf = self._calculate_volume_confirmation(data, idx, volumes)
                                
                                all_levels.append(ProfessionalLevel(
                                    price=level_price,
                                    strength=level_strength,
                                    touches=touches,
                                    age=age,
                                    volume_confirmation=volume_conf,
                                    level_type='support'
                                ))
            
            # Remove duplicate levels and sort by strength
            unique_levels = self._consolidate_levels(all_levels, current_price)
            return sorted(unique_levels, key=lambda x: x.strength, reverse=True)[:10]  # Top 10 levels
            
        except Exception as e:
            logging.error(f"Level detection error: {e}")
            return []
    
    def _calculate_level_strength(self, data: pd.DataFrame, level_price: float, level_type: str) -> float:
        """Calculate professional level strength"""
        try:
            strength = 0.0
            recent_data = data.tail(50)  # Last 50 bars
            
            # Factor 1: Touch count and quality
            touches = 0
            touch_quality = 0.0
            
            for _, row in recent_data.iterrows():
                if level_type == 'resistance':
                    distance = abs(row['high'] - level_price) / level_price
                    if distance <= 0.002:  # Within 20 pips for major pairs
                        touches += 1
                        touch_quality += (0.002 - distance) / 0.002  # Closer = better
                else:  # support
                    distance = abs(row['low'] - level_price) / level_price
                    if distance <= 0.002:
                        touches += 1
                        touch_quality += (0.002 - distance) / 0.002
            
            if touches > 0:
                strength += min(0.4, touches * 0.1)  # Up to 0.4 from touches
                strength += min(0.3, touch_quality / touches)  # Up to 0.3 from quality
            
            # Factor 2: Reaction strength at level
            reactions = 0
            reaction_strength = 0.0
            
            for i in range(1, min(len(recent_data), 30)):
                if level_type == 'resistance':
                    if abs(recent_data.iloc[i]['high'] - level_price) / level_price <= 0.002:
                        # Check for rejection (price moved down after touching)
                        if i < len(recent_data) - 3:
                            price_change = (recent_data.iloc[i+3]['close'] - recent_data.iloc[i]['close']) / recent_data.iloc[i]['close']
                            if price_change < -0.005:  # 50 pips rejection
                                reactions += 1
                                reaction_strength += abs(price_change)
                else:  # support
                    if abs(recent_data.iloc[i]['low'] - level_price) / level_price <= 0.002:
                        if i < len(recent_data) - 3:
                            price_change = (recent_data.iloc[i+3]['close'] - recent_data.iloc[i]['close']) / recent_data.iloc[i]['close']
                            if price_change > 0.005:  # 50 pips bounce
                                reactions += 1
                                reaction_strength += price_change
            
            if reactions > 0:
                strength += min(0.3, reaction_strength / reactions * 10)  # Up to 0.3 from reactions
            
            return min(1.0, strength)
            
        except Exception:
            return 0.0
    
    def _count_level_touches(self, data: pd.DataFrame, level_price: float, level_type: str) -> int:
        """Count significant touches of the level"""
        try:
            touches = 0
            recent_data = data.tail(50)
            
            for _, row in recent_data.iterrows():
                if level_type == 'resistance':
                    if abs(row['high'] - level_price) / level_price <= 0.002:
                        touches += 1
                else:  # support
                    if abs(row['low'] - level_price) / level_price <= 0.002:
                        touches += 1
            
            return touches
            
        except Exception:
            return 0
    
    def _calculate_volume_confirmation(self, data: pd.DataFrame, level_index: int, volumes: np.ndarray) -> float:
        """Calculate volume confirmation score"""
        if not self.volume_confirmation or 'volume' not in data.columns:
            return 1.0
        
        try:
            if level_index >= len(volumes) - 10:
                return 1.0
            
            level_volume = volumes[level_index]
            avg_volume = np.mean(volumes[max(0, level_index-20):level_index+20])
            
            volume_ratio = level_volume / (avg_volume + 1e-6)
            
            # Higher volume at level = better confirmation
            return min(1.5, max(0.5, volume_ratio))
            
        except Exception:
            return 1.0
    
    def _consolidate_levels(self, levels: List[ProfessionalLevel], current_price: float) -> List[ProfessionalLevel]:
        """Remove duplicate and merge nearby levels"""
        if not levels:
            return []
        
        consolidated = []
        sorted_levels = sorted(levels, key=lambda x: x.price)
        
        for level in sorted_levels:
            # Only consider levels within reasonable distance
            if abs(level.price - current_price) / current_price <= 0.05:  # Within 5%
                
                # Check if similar level already exists
                merged = False
                for i, existing in enumerate(consolidated):
                    if abs(level.price - existing.price) / existing.price <= 0.001:  # Very close
                        # Merge levels - keep the stronger one
                        if level.strength > existing.strength:
                            consolidated[i] = level
                        merged = True
                        break
                
                if not merged:
                    consolidated.append(level)
        
        return consolidated
    
    def _analyze_market_structure(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Professional market structure analysis"""
        try:
            # Higher highs, higher lows analysis
            highs = data['high'].rolling(10).max()
            lows = data['low'].rolling(10).min()
            
            recent_highs = highs.tail(20)
            recent_lows = lows.tail(20)
            
            # Count structure patterns
            hh_count = sum(1 for i in range(1, len(recent_highs)) 
                          if recent_highs.iloc[i] > recent_highs.iloc[i-1])
            ll_count = sum(1 for i in range(1, len(recent_lows)) 
                          if recent_lows.iloc[i] < recent_lows.iloc[i-1])
            hl_count = sum(1 for i in range(1, len(recent_lows)) 
                          if recent_lows.iloc[i] > recent_lows.iloc[i-1])
            lh_count = sum(1 for i in range(1, len(recent_highs)) 
                          if recent_highs.iloc[i] < recent_highs.iloc[i-1])
            
            # Determine trend
            uptrend_strength = (hh_count + hl_count) / 20
            downtrend_strength = (ll_count + lh_count) / 20
            
            if uptrend_strength > 0.6:
                trend = 'uptrend'
                strength = uptrend_strength
            elif downtrend_strength > 0.6:
                trend = 'downtrend'
                strength = downtrend_strength
            else:
                trend = 'sideways'
                strength = 1.0 - abs(uptrend_strength - downtrend_strength)
            
            return {
                'trend': trend,
                'strength': strength,
                'uptrend_strength': uptrend_strength,
                'downtrend_strength': downtrend_strength
            }
            
        except Exception:
            return {'trend': 'unknown', 'strength': 0.5}
    
    def _detect_professional_breakout(self, data: pd.DataFrame, 
                                    levels: List[ProfessionalLevel]) -> Dict[str, Any]:
        """
        PROFESSIONAL BREAKOUT DETECTION
        ===============================
        Advanced breakout validation with multiple confirmations
        """
        try:
            current_price = data['close'].iloc[-1]
            current_bar = data.iloc[-1]
            
            # Find the most relevant level
            nearby_levels = [level for level in levels 
                           if abs(level.price - current_price) / current_price <= 0.01]  # Within 1%
            
            if not nearby_levels:
                return {'is_breakout': False, 'reason': 'No nearby professional levels'}
            
            # Check for breakouts
            for level in nearby_levels:
                if level.level_type == 'resistance':
                    # Resistance breakout (BUY signal)
                    if current_price > level.price * 1.0008:  # 8 pips above
                        breakout_strength = self._calculate_breakout_strength(
                            data, level, 'resistance_break'
                        )
                        
                        if breakout_strength >= self.min_breakout_strength:
                            return {
                                'is_breakout': True,
                                'direction': 'BUY',
                                'level': level,
                                'breakout_strength': breakout_strength,
                                'breakout_distance': (current_price - level.price) / level.price,
                                'reason': f'Resistance breakout at {level.price:.5f}'
                            }
                
                elif level.level_type == 'support':
                    # Support breakdown (SELL signal)
                    if current_price < level.price * 0.9992:  # 8 pips below
                        breakout_strength = self._calculate_breakout_strength(
                            data, level, 'support_break'
                        )
                        
                        if breakout_strength >= self.min_breakout_strength:
                            return {
                                'is_breakout': True,
                                'direction': 'SELL',
                                'level': level,
                                'breakout_strength': breakout_strength,
                                'breakout_distance': (level.price - current_price) / level.price,
                                'reason': f'Support breakdown at {level.price:.5f}'
                            }
            
            return {'is_breakout': False, 'reason': 'No valid breakouts detected'}
            
        except Exception as e:
            return {'is_breakout': False, 'reason': f'Breakout detection error: {e}'}
    
    def _calculate_breakout_strength(self, data: pd.DataFrame, level: ProfessionalLevel, 
                                   breakout_type: str) -> float:
        """Calculate breakout strength score"""
        try:
            strength = 0.0
            recent_data = data.tail(10)
            
            # Factor 1: Momentum (30%)
            momentum = self._calculate_momentum(data, 5)
            if breakout_type == 'resistance_break' and momentum > 0:
                strength += min(0.3, momentum * 30)
            elif breakout_type == 'support_break' and momentum < 0:
                strength += min(0.3, abs(momentum) * 30)
            
            # Factor 2: Level strength (25%)
            strength += level.strength * 0.25
            
            # Factor 3: Volume confirmation (25%)
            if 'volume' in data.columns:
                current_volume = data['volume'].iloc[-1]
                avg_volume = data['volume'].rolling(20).mean().iloc[-1]
                volume_ratio = current_volume / (avg_volume + 1e-6)
                strength += min(0.25, (volume_ratio - 1) * 0.25) if volume_ratio > 1 else 0
            else:
                strength += 0.15  # Neutral if no volume data
            
            # Factor 4: Breakout decisiveness (20%)
            current_price = data['close'].iloc[-1]
            breakout_distance = abs(current_price - level.price) / level.price
            strength += min(0.2, breakout_distance * 100)  # Larger breakout = more decisive
            
            return min(1.0, strength)
            
        except Exception:
            return 0.0
    
    def _analyze_breakout_volume(self, data: pd.DataFrame, breakout_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze volume confirmation for breakout"""
        if not self.volume_confirmation or 'volume' not in data.columns:
            return {'confirmed': True, 'volume_ratio': 1.0}
        
        try:
            current_volume = data['volume'].iloc[-1]
            avg_volume = data['volume'].rolling(20).mean().iloc[-1]
            volume_ratio = current_volume / (avg_volume + 1e-6)
            
            # Volume should be above average for confirmed breakout
            volume_confirmed = volume_ratio > 1.2  # 20% above average
            
            return {
                'confirmed': volume_confirmed,
                'volume_ratio': volume_ratio,
                'volume_score': min(2.0, volume_ratio) if volume_confirmed else 0.5
            }
            
        except Exception:
            return {'confirmed': True, 'volume_ratio': 1.0, 'volume_score': 1.0}
    
    def _assess_false_breakout_risk(self, data: pd.DataFrame, breakout_analysis: Dict[str, Any]) -> float:
        """Assess risk of false breakout"""
        try:
            risk_score = 0.0
            
            # Factor 1: Recent false breakouts
            level = breakout_analysis['level']
            recent_data = data.tail(20)
            
            false_breakouts = 0
            for i, row in recent_data.iterrows():
                if breakout_analysis['direction'] == 'BUY':
                    if row['high'] > level.price * 1.0005 and row['close'] < level.price:
                        false_breakouts += 1
                else:  # SELL
                    if row['low'] < level.price * 0.9995 and row['close'] > level.price:
                        false_breakouts += 1
            
            risk_score += min(0.4, false_breakouts * 0.1)
            
            # Factor 2: Market volatility
            volatility = data['close'].pct_change().tail(20).std()
            avg_volatility = data['close'].pct_change().std()
            vol_ratio = volatility / (avg_volatility + 1e-6)
            
            if vol_ratio > 1.5:  # High volatility increases false breakout risk
                risk_score += 0.2
            
            # Factor 3: Time of day (if applicable)
            # During low liquidity hours, false breakouts are more common
            current_hour = datetime.now().hour
            if current_hour in [22, 23, 0, 1, 2, 3]:  # Low liquidity hours
                risk_score += 0.2
            
            return min(1.0, risk_score)
            
        except Exception:
            return 0.3  # Default moderate risk
    
    def _generate_professional_breakout_signal(self, data: pd.DataFrame,
                                             breakout_analysis: Dict[str, Any],
                                             market_structure: Dict[str, Any],
                                             volume_confirmation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate professional breakout signal"""
        try:
            direction = breakout_analysis['direction']
            level = breakout_analysis['level']
            current_price = data['close'].iloc[-1]
            
            # Base confidence from breakout strength
            confidence = breakout_analysis['breakout_strength']
            
            # Market structure alignment bonus
            if ((direction == 'BUY' and market_structure['trend'] == 'uptrend') or
                (direction == 'SELL' and market_structure['trend'] == 'downtrend')):
                confidence *= 1.2  # 20% bonus for trend alignment
            
            # Volume confirmation multiplier
            confidence *= volume_confirmation['volume_score']
            
            # Level quality multiplier
            confidence *= level.strength
            
            # Cap confidence
            confidence = min(0.90, confidence)
            
            # Generate signal reasons
            reasons = [
                f"Level: {level.level_type} at {level.price:.5f}",
                f"Strength: {level.strength:.3f}",
                f"Touches: {level.touches}",
                f"Volume: {volume_confirmation['volume_ratio']:.2f}x"
            ]
            
            if market_structure['trend'] != 'sideways':
                reasons.append(f"Trend: {market_structure['trend']}")
            
            return {
                'signal': direction,
                'confidence': confidence,
                'price': current_price,
                'reason': f"Professional {direction} breakout: {'; '.join(reasons)}",
                'level_price': level.price,
                'level_strength': level.strength,
                'level_touches': level.touches,
                'breakout_strength': breakout_analysis['breakout_strength'],
                'volume_confirmation': volume_confirmation['confirmed'],
                'market_structure': market_structure['trend']
            }
            
        except Exception as e:
            return self._no_signal(data, f"Signal generation error: {e}")
    
    def _optimize_professional_risk_reward(self, signal: Dict[str, Any], data: pd.DataFrame,
                                         breakout_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Professional risk-reward optimization"""
        try:
            current_price = signal['price']
            direction = signal['signal']
            level = breakout_analysis['level']
            
            # ATR for dynamic stops
            atr = self._calculate_atr(data)
            
            if direction == 'BUY':
                # Stop below the broken level
                stop_buffer = max(atr * 0.8, level.price * 0.0015)  # 15 pips or 0.8 ATR
                stop_loss = level.price - stop_buffer
                
                # Target based on ATR and level strength
                target_multiplier = 2.0 + level.strength  # Stronger levels = bigger targets
                take_profit = current_price + (atr * target_multiplier)
                
            else:  # SELL
                # Stop above the broken level
                stop_buffer = max(atr * 0.8, level.price * 0.0015)
                stop_loss = level.price + stop_buffer
                
                # Target based on ATR and level strength
                target_multiplier = 2.0 + level.strength
                take_profit = current_price - (atr * target_multiplier)
            
            # Calculate risk-reward
            risk = abs(current_price - stop_loss)
            reward = abs(take_profit - current_price)
            risk_reward = reward / risk if risk > 0 else 0
            
            # Adjust if RR is insufficient
            if risk_reward < self.min_risk_reward:
                if direction == 'BUY':
                    take_profit = current_price + (risk * self.min_risk_reward)
                else:
                    take_profit = current_price - (risk * self.min_risk_reward)
                
                risk_reward = self.min_risk_reward
            
            # Add risk management data
            signal.update({
                'stop_loss': round(stop_loss, 5),
                'take_profit': round(take_profit, 5),
                'risk_reward_ratio': risk_reward,
                'risk_amount': risk,
                'reward_amount': reward,
                'atr': atr
            })
            
            return signal
            
        except Exception as e:
            logging.error(f"Risk-reward optimization error: {e}")
            return signal
    
    def _apply_institutional_filters(self, signal: Dict[str, Any], data: pd.DataFrame) -> Dict[str, Any]:
        """Apply institutional-grade filters"""
        if signal['signal'] == 'HOLD':
            return signal
        
        # Filter 1: Minimum confidence
        if signal['confidence'] < self.min_confidence:
            return self._no_signal(data, f"Below confidence threshold: {signal['confidence']:.3f}")
        
        # Filter 2: Risk-reward ratio
        if signal.get('risk_reward_ratio', 0) < self.min_risk_reward:
            return self._no_signal(data, f"Insufficient RR: {signal.get('risk_reward_ratio', 0):.2f}")
        
        # Filter 3: Level strength
        if signal.get('level_strength', 0) < self.min_level_strength:
            return self._no_signal(data, f"Weak level: {signal.get('level_strength', 0):.3f}")
        
        # Filter 4: Volume confirmation (if enabled)
        if self.volume_confirmation and not signal.get('volume_confirmation', True):
            return self._no_signal(data, "No volume confirmation")
        
        # All filters passed
        signal.update({
            'professional_grade': True,
            'institutional_validated': True,
            'validation_timestamp': datetime.now(),
            'strategy_version': '3.0'
        })
        
        logging.info(f"✅ Professional S&R Signal: {signal['signal']} "
                    f"conf:{signal['confidence']:.3f} RR:{signal.get('risk_reward_ratio', 0):.2f} "
                    f"level:{signal.get('level_strength', 0):.3f}")
        
        return signal
    
    # Utility Methods
    def _calculate_momentum(self, data: pd.DataFrame, periods: int = 5) -> float:
        """Calculate price momentum"""
        try:
            if len(data) < periods:
                return 0.0
            
            current = data['close'].iloc[-1]
            past = data['close'].iloc[-periods]
            return (current - past) / past
        except Exception:
            return 0.0
    
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range"""
        try:
            high = data['high']
            low = data['low']
            close = data['close']
            
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            
            true_range = np.maximum(tr1, np.maximum(tr2, tr3))
            return true_range.rolling(window=period).mean().iloc[-1]
        except Exception:
            return 0.001
    
    def _no_signal(self, data: pd.DataFrame, reason: str) -> Dict[str, Any]:
        """Professional no-signal response"""
        return {
            'signal': 'HOLD',
            'confidence': 0.0,
            'price': data['close'].iloc[-1] if not data.empty else 1.0,
            'reason': f"Professional S&R: {reason}",
            'professional_grade': True
        }

# Backward compatibility
SupportResistanceBreakoutStrategy = ProfessionalSupportResistanceStrategy
