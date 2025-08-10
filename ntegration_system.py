"""
Complete Trading System Integration
==================================
Integrates ICT Strategy, RTM Strategy, SMC Indicators, ML Models, and Fixed Backtesting Engine
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import warnings
from datetime import datetime, timedelta
import sys
import os
from concurrent.futures import ThreadPoolExecutor
import asyncio

# Configure logging to handle Unicode properly
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('trading_system.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Remove emoji characters from log messages to prevent encoding errors
class UnicodeLogFilter(logging.Filter):
    def filter(self, record):
        if hasattr(record, 'msg'):
            # Replace problematic Unicode characters
            record.msg = str(record.msg).encode('ascii', 'ignore').decode('ascii')
        return True

# Apply the filter to all loggers
for handler in logging.root.handlers:
    handler.addFilter(UnicodeLogFilter())

warnings.filterwarnings('ignore')

# =============================================================================
# UNIFIED SIGNAL STRUCTURE
# =============================================================================

class SignalType(Enum):
    """Unified signal types across all strategies"""
    BUY = 1
    SELL = -1
    HOLD = 0
    STRONG_BUY = 2
    STRONG_SELL = -2

class StrategyType(Enum):
    """Strategy classification"""
    ICT = "ict"
    RTM = "rtm"
    SMC = "smc"
    ML = "machine_learning"
    COMPOSITE = "composite"

@dataclass
class UnifiedTradingSignal:
    """Unified signal structure for all strategies"""
    signal_type: SignalType
    strategy_type: StrategyType
    strategy_name: str
    timestamp: pd.Timestamp
    price: float
    confidence: float  # 0.0 to 1.0
    strength: float   # 0.0 to 1.0
    
    # Additional metadata
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    risk_reward_ratio: Optional[float] = None
    confluence_score: float = 0.0
    ml_probability: Optional[float] = None
    
    # SMC specific data
    smc_data: Optional[Dict[str, Any]] = None
    
    # ICT specific data
    ict_data: Optional[Dict[str, Any]] = None
    
    # RTM specific data  
    rtm_data: Optional[Dict[str, Any]] = None
    
    def to_backtest_signal(self) -> int:
        """Convert to backtesting engine format"""
        return int(self.signal_type.value)

# =============================================================================
# ENHANCED SMC INDICATORS INTEGRATION
# =============================================================================

class EnhancedSMCIntegrator:
    """Enhanced SMC indicators with ML integration"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.smc_indicators = None
        self._initialize_smc()
        
    def _initialize_smc(self):
        """Initialize SMC indicators (using your previous implementation)"""
        try:
            # Import your existing SMC implementation
            from your_smc_module import AdvancedSMCIndicators  # Adjust import path
            self.smc_indicators = AdvancedSMCIndicators(self.config)
            logger.info("SMC Indicators initialized successfully")
        except ImportError:
            logger.warning("SMC module not found, using placeholder")
            self.smc_indicators = None
    
    def analyze_smc_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze SMC patterns and generate signals"""
        try:
            if self.smc_indicators is None:
                return self._generate_placeholder_smc_analysis(data)
            
            # Use your existing SMC analysis
            analysis = self.smc_indicators.analyze_complete_smc(
                data, symbol="UNKNOWN", timeframe="H1"
            )
            
            return {
                'order_blocks': analysis.order_blocks,
                'fair_value_gaps': analysis.fair_value_gaps,
                'liquidity_sweeps': analysis.liquidity_sweeps,
                'market_structure': analysis.market_structure,
                'confluence_zones': analysis.confluence_zones,
                'overall_bias': analysis.overall_bias,
                'signal_strength': analysis.signal_strength,
                'confidence_score': analysis.confidence_score
            }
            
        except Exception as e:
            logger.error(f"Error in SMC analysis: {e}")
            return self._generate_placeholder_smc_analysis(data)
    
    def _generate_placeholder_smc_analysis(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Placeholder SMC analysis when main module unavailable"""
        return {
            'order_blocks': [],
            'fair_value_gaps': [],
            'liquidity_sweeps': [],
            'market_structure': [],
            'confluence_zones': [],
            'overall_bias': 'neutral',
            'signal_strength': 0.5,
            'confidence_score': 0.5
        }
    
    def generate_smc_signals(self, data: pd.DataFrame) -> List[UnifiedTradingSignal]:
        """Generate trading signals from SMC analysis"""
        signals = []
        
        try:
            smc_analysis = self.analyze_smc_patterns(data)
            current_price = data['close'].iloc[-1]
            current_time = data.index[-1]
            
            # Generate signals based on SMC bias
            if smc_analysis['overall_bias'] == 'bullish' and smc_analysis['signal_strength'] > 0.6:
                signal = UnifiedTradingSignal(
                    signal_type=SignalType.BUY,
                    strategy_type=StrategyType.SMC,
                    strategy_name="SMC_Analysis",
                    timestamp=current_time,
                    price=current_price,
                    confidence=smc_analysis['confidence_score'],
                    strength=smc_analysis['signal_strength'],
                    smc_data=smc_analysis
                )
                signals.append(signal)
            
            elif smc_analysis['overall_bias'] == 'bearish' and smc_analysis['signal_strength'] > 0.6:
                signal = UnifiedTradingSignal(
                    signal_type=SignalType.SELL,
                    strategy_type=StrategyType.SMC,
                    strategy_name="SMC_Analysis",
                    timestamp=current_time,
                    price=current_price,
                    confidence=smc_analysis['confidence_score'],
                    strength=smc_analysis['signal_strength'],
                    smc_data=smc_analysis
                )
                signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error generating SMC signals: {e}")
            return []

# =============================================================================
# ICT STRATEGY INTEGRATION
# =============================================================================

class ICTStrategyIntegrator:
    """ICT Strategy with SMC integration"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.smc_integrator = EnhancedSMCIntegrator(config)
        
    def analyze_ict_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze ICT patterns"""
        try:
            # Get SMC analysis first
            smc_data = self.smc_integrator.analyze_smc_patterns(data)
            
            # ICT-specific analysis
            ict_analysis = {
                'market_structure_breaks': self._detect_structure_breaks(data),
                'order_blocks': smc_data['order_blocks'],  # Use SMC order blocks
                'fair_value_gaps': smc_data['fair_value_gaps'],  # Use SMC FVGs
                'liquidity_zones': self._identify_liquidity_zones(data),
                'institutional_candles': self._find_institutional_candles(data),
                'trend_direction': self._determine_trend_direction(data)
            }
            
            return ict_analysis
            
        except Exception as e:
            logger.error(f"Error in ICT analysis: {e}")
            return {}
    
    def _detect_structure_breaks(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect market structure breaks"""
        try:
            # Simplified structure break detection
            structure_breaks = []
            lookback = 20
            
            for i in range(lookback, len(data)):
                recent_highs = data['high'].iloc[i-lookback:i]
                recent_lows = data['low'].iloc[i-lookback:i]
                
                current_high = data['high'].iloc[i]
                current_low = data['low'].iloc[i]
                
                # Bullish structure break
                if current_high > recent_highs.max():
                    structure_breaks.append({
                        'type': 'bullish_break',
                        'index': i,
                        'price': current_high,
                        'timestamp': data.index[i]
                    })
                
                # Bearish structure break
                if current_low < recent_lows.min():
                    structure_breaks.append({
                        'type': 'bearish_break',
                        'index': i,
                        'price': current_low,
                        'timestamp': data.index[i]
                    })
            
            return structure_breaks
            
        except Exception as e:
            logger.error(f"Error detecting structure breaks: {e}")
            return []
    
    def _identify_liquidity_zones(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identify liquidity zones"""
        try:
            liquidity_zones = []
            lookback = 50
            
            # Find equal highs and lows
            for i in range(lookback, len(data)):
                recent_data = data.iloc[i-lookback:i]
                
                # Equal highs (resistance)
                high_levels = recent_data['high'].rolling(5).max()
                equal_highs = high_levels[high_levels.duplicated()].unique()
                
                for level in equal_highs:
                    liquidity_zones.append({
                        'type': 'equal_highs',
                        'price': level,
                        'strength': len(recent_data[recent_data['high'] >= level * 0.999])
                    })
            
            return liquidity_zones
            
        except Exception as e:
            logger.error(f"Error identifying liquidity zones: {e}")
            return []
    
    def _find_institutional_candles(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Find institutional candles (high volume, significant moves)"""
        try:
            institutional_candles = []
            
            if 'volume' not in data.columns:
                return institutional_candles
            
            # Calculate volume and price movement thresholds
            volume_threshold = data['volume'].quantile(0.8)
            price_movement_threshold = (data['high'] - data['low']).quantile(0.8)
            
            for i in range(len(data)):
                volume = data['volume'].iloc[i]
                price_range = data['high'].iloc[i] - data['low'].iloc[i]
                
                if volume > volume_threshold and price_range > price_movement_threshold:
                    institutional_candles.append({
                        'index': i,
                        'timestamp': data.index[i],
                        'volume': volume,
                        'range': price_range,
                        'type': 'bullish' if data['close'].iloc[i] > data['open'].iloc[i] else 'bearish'
                    })
            
            return institutional_candles
            
        except Exception as e:
            logger.error(f"Error finding institutional candles: {e}")
            return []
    
    def _determine_trend_direction(self, data: pd.DataFrame) -> str:
        """Determine overall trend direction"""
        try:
            # Use moving averages to determine trend
            short_ma = data['close'].rolling(20).mean()
            long_ma = data['close'].rolling(50).mean()
            
            if short_ma.iloc[-1] > long_ma.iloc[-1]:
                return 'bullish'
            elif short_ma.iloc[-1] < long_ma.iloc[-1]:
                return 'bearish'
            else:
                return 'neutral'
                
        except Exception as e:
            logger.error(f"Error determining trend direction: {e}")
            return 'neutral'
    
    def generate_ict_signals(self, data: pd.DataFrame) -> List[UnifiedTradingSignal]:
        """Generate ICT trading signals"""
        signals = []
        
        try:
            ict_analysis = self.analyze_ict_patterns(data)
            current_price = data['close'].iloc[-1]
            current_time = data.index[-1]
            
            # Generate signals based on ICT analysis
            trend = ict_analysis.get('trend_direction', 'neutral')
            recent_breaks = [b for b in ict_analysis.get('market_structure_breaks', []) 
                           if b['index'] > len(data) - 10]  # Recent breaks only
            
            if trend == 'bullish' and any(b['type'] == 'bullish_break' for b in recent_breaks):
                signal = UnifiedTradingSignal(
                    signal_type=SignalType.BUY,
                    strategy_type=StrategyType.ICT,
                    strategy_name="ICT_Strategy",
                    timestamp=current_time,
                    price=current_price,
                    confidence=0.7,
                    strength=0.8,
                    ict_data=ict_analysis
                )
                signals.append(signal)
            
            elif trend == 'bearish' and any(b['type'] == 'bearish_break' for b in recent_breaks):
                signal = UnifiedTradingSignal(
                    signal_type=SignalType.SELL,
                    strategy_type=StrategyType.ICT,
                    strategy_name="ICT_Strategy",
                    timestamp=current_time,
                    price=current_price,
                    confidence=0.7,
                    strength=0.8,
                    ict_data=ict_analysis
                )
                signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error generating ICT signals: {e}")
            return []

# =============================================================================
# RTM STRATEGY INTEGRATION
# =============================================================================

class RTMStrategyIntegrator:
    """RTM Strategy with SMC integration"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.momentum_threshold_pips = config.get('momentum_threshold_pips', 20)
        
    def analyze_rtm_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze RTM patterns"""
        try:
            rtm_analysis = {
                'zones': self._detect_rtm_zones(data),
                'qml_patterns': self._detect_qml_patterns(data),
                'momentum_shifts': self._detect_momentum_shifts(data),
                'trend_strength': self._calculate_trend_strength(data)
            }
            
            return rtm_analysis
            
        except Exception as e:
            logger.error(f"Error in RTM analysis: {e}")
            return {}
    
    def _detect_rtm_zones(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect RTM zones"""
        try:
            zones = []
            lookback = 20
            
            for i in range(lookback, len(data)):
                # Find potential reversal zones
                recent_data = data.iloc[i-lookback:i]
                
                # Support zones (where price bounced up)
                support_level = recent_data['low'].min()
                if data['low'].iloc[i] <= support_level * 1.001:  # Near support
                    zones.append({
                        'type': 'support',
                        'level': support_level,
                        'strength': self._calculate_zone_strength(recent_data, support_level, 'support'),
                        'index': i
                    })
                
                # Resistance zones (where price bounced down)
                resistance_level = recent_data['high'].max()
                if data['high'].iloc[i] >= resistance_level * 0.999:  # Near resistance
                    zones.append({
                        'type': 'resistance',
                        'level': resistance_level,
                        'strength': self._calculate_zone_strength(recent_data, resistance_level, 'resistance'),
                        'index': i
                    })
            
            return zones
            
        except Exception as e:
            logger.error(f"Error detecting RTM zones: {e}")
            return []
    
    def _calculate_zone_strength(self, data: pd.DataFrame, level: float, zone_type: str) -> float:
        """Calculate zone strength based on touches and reactions"""
        try:
            touches = 0
            reactions = 0
            
            if zone_type == 'support':
                # Count how many times price touched this level
                touches = len(data[data['low'] <= level * 1.002])
                # Count significant reactions upward
                reactions = len(data[(data['low'] <= level * 1.002) & 
                                   (data['close'] > data['open'])])
            else:  # resistance
                touches = len(data[data['high'] >= level * 0.998])
                reactions = len(data[(data['high'] >= level * 0.998) & 
                                   (data['close'] < data['open'])])
            
            return min(1.0, (reactions / max(touches, 1)) * (touches / 10))
            
        except Exception as e:
            logger.error(f"Error calculating zone strength: {e}")
            return 0.5
    
    def _detect_qml_patterns(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Quasimodo (QML) patterns"""
        try:
            qml_patterns = []
            lookback = 30
            
            for i in range(lookback, len(data) - 5):
                # Look for head and shoulders pattern (simplified QML)
                window_data = data.iloc[i-lookback:i+5]
                
                # Find potential left shoulder, head, right shoulder
                highs = window_data['high']
                high_indices = highs.argsort()[-3:]  # Top 3 highs
                
                if len(high_indices) == 3:
                    # Check if middle high is the highest (head)
                    sorted_indices = sorted(high_indices)
                    if highs.iloc[sorted_indices[1]] > highs.iloc[sorted_indices[0]] and \
                       highs.iloc[sorted_indices[1]] > highs.iloc[sorted_indices[2]]:
                        
                        qml_patterns.append({
                            'type': 'bearish_qml',
                            'head_index': sorted_indices[1],
                            'head_price': highs.iloc[sorted_indices[1]],
                            'strength': 0.7
                        })
            
            return qml_patterns
            
        except Exception as e:
            logger.error(f"Error detecting QML patterns: {e}")
            return []
    
    def _detect_momentum_shifts(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect momentum shifts"""
        try:
            momentum_shifts = []
            
            # Calculate momentum using price velocity
            price_velocity = data['close'].pct_change(5) * 10000  # In pips
            
            for i in range(5, len(data)):
                current_momentum = price_velocity.iloc[i]
                previous_momentum = price_velocity.iloc[i-5]
                
                # Detect significant momentum changes
                if abs(current_momentum - previous_momentum) > self.momentum_threshold_pips:
                    momentum_shifts.append({
                        'index': i,
                        'from_momentum': previous_momentum,
                        'to_momentum': current_momentum,
                        'shift_type': 'bullish' if current_momentum > previous_momentum else 'bearish',
                        'strength': min(1.0, abs(current_momentum - previous_momentum) / (self.momentum_threshold_pips * 2))
                    })
            
            return momentum_shifts
            
        except Exception as e:
            logger.error(f"Error detecting momentum shifts: {e}")
            return []
    
    def _calculate_trend_strength(self, data: pd.DataFrame) -> float:
        """Calculate overall trend strength"""
        try:
            # Use ADX-like calculation for trend strength
            high_low = data['high'] - data['low']
            high_close_prev = abs(data['high'] - data['close'].shift(1))
            low_close_prev = abs(data['low'] - data['close'].shift(1))
            
            true_range = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
            atr = true_range.rolling(14).mean()
            
            # Calculate directional movement
            up_move = data['high'] - data['high'].shift(1)
            down_move = data['low'].shift(1) - data['low']
            
            plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
            minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0)
            
            plus_di = (plus_dm.rolling(14).sum() / atr).rolling(14).mean() * 100
            minus_di = (minus_dm.rolling(14).sum() / atr).rolling(14).mean() * 100
            
            adx = abs(plus_di - minus_di) / (plus_di + minus_di) * 100
            
            return min(1.0, adx.iloc[-1] / 50) if not pd.isna(adx.iloc[-1]) else 0.5
            
        except Exception as e:
            logger.error(f"Error calculating trend strength: {e}")
            return 0.5
    
    def generate_rtm_signals(self, data: pd.DataFrame) -> List[UnifiedTradingSignal]:
        """Generate RTM trading signals"""
        signals = []
        
        try:
            rtm_analysis = self.analyze_rtm_patterns(data)
            current_price = data['close'].iloc[-1]
            current_time = data.index[-1]
            
            # Get recent zones and momentum shifts
            zones = rtm_analysis.get('zones', [])
            recent_zones = [z for z in zones if z['index'] > len(data) - 5]
            
            momentum_shifts = rtm_analysis.get('momentum_shifts', [])
            recent_shifts = [s for s in momentum_shifts if s['index'] > len(data) - 10]
            
            trend_strength = rtm_analysis.get('trend_strength', 0.5)
            
            # Generate signals based on zone reactions and momentum
            for zone in recent_zones:
                if zone['strength'] > 0.6 and trend_strength > 0.5:
                    if zone['type'] == 'support' and any(s['shift_type'] == 'bullish' for s in recent_shifts):
                        signal = UnifiedTradingSignal(
                            signal_type=SignalType.BUY,
                            strategy_type=StrategyType.RTM,
                            strategy_name="RTM_Strategy",
                            timestamp=current_time,
                            price=current_price,
                            confidence=zone['strength'],
                            strength=trend_strength,
                            rtm_data=rtm_analysis
                        )
                        signals.append(signal)
                    
                    elif zone['type'] == 'resistance' and any(s['shift_type'] == 'bearish' for s in recent_shifts):
                        signal = UnifiedTradingSignal(
                            signal_type=SignalType.SELL,
                            strategy_type=StrategyType.RTM,
                            strategy_name="RTM_Strategy",
                            timestamp=current_time,
                            price=current_price,
                            confidence=zone['strength'],
                            strength=trend_strength,
                            rtm_data=rtm_analysis
                        )
                        signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error generating RTM signals: {e}")
            return []

# =============================================================================
# MACHINE LEARNING INTEGRATION
# =============================================================================

class MLModelIntegrator:
    """Machine Learning model integration for trading signals"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.model = None
        self.feature_columns = []
        self._initialize_model()
        
    def _initialize_model(self):
        """Initialize ML model"""
        try:
            # Try to load existing model or create simple one
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.preprocessing import StandardScaler
            
            self.model = RandomForestClassifier(
                n_estimators=100, 
                max_depth=10, 
                random_state=42
            )
            self.scaler = StandardScaler()
            self.is_trained = False
            
            logger.info("ML Model initialized successfully")
            
        except ImportError:
            logger.warning("Scikit-learn not available, ML features disabled")
            self.model = None
    
    def extract_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Extract features for ML model"""
        try:
            features = pd.DataFrame(index=data.index)
            
            # Technical indicators as features
            features['sma_10'] = data['close'].rolling(10).mean()
            features['sma_20'] = data['close'].rolling(20).mean()
            features['sma_50'] = data['close'].rolling(50).mean()
            
            # RSI
            delta = data['close'].diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            features['rsi'] = 100 - (100 / (1 + rs))
            
            # MACD
            ema_12 = data['close'].ewm(span=12).mean()
            ema_26 = data['close'].ewm(span=26).mean()
            features['macd'] = ema_12 - ema_26
            features['macd_signal'] = features['macd'].ewm(span=9).mean()
            
            # Bollinger Bands
            sma_20 = data['close'].rolling(20).mean()
            std_20 = data['close'].rolling(20).std()
            features['bb_upper'] = sma_20 + (std_20 * 2)
            features['bb_lower'] = sma_20 - (std_20 * 2)
            features['bb_position'] = (data['close'] - features['bb_lower']) / (features['bb_upper'] - features['bb_lower'])
            
            # Volume features (if available)
            if 'volume' in data.columns:
                features['volume_sma'] = data['volume'].rolling(20).mean()
                features['volume_ratio'] = data['volume'] / features['volume_sma']
            else:
                features['volume_sma'] = 1
                features['volume_ratio'] = 1
            
            # Price momentum
            features['price_change_1'] = data['close'].pct_change(1)
            features['price_change_5'] = data['close'].pct_change(5)
            features['price_change_10'] = data['close'].pct_change(10)
            
            # Volatility
            features['volatility'] = data['close'].rolling(20).std()
            
            self.feature_columns = features.columns.tolist()
            return features.fillna(method='ffill').fillna(0)
            
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return pd.DataFrame()
    
    def train_model(self, data: pd.DataFrame, signals: pd.Series):
        """Train the ML model"""
        try:
            if self.model is None:
                return False
            
            features = self.extract_features(data)
            
            # Align features and signals
            aligned_features = features.iloc[:-1]  # Remove last row (no future signal)
            aligned_signals = signals.iloc[1:]    # Remove first row (no past features)
            
            # Remove NaN values
            valid_indices = ~(aligned_features.isnull().any(axis=1) | aligned_signals.isnull())
            
            X = aligned_features[valid_indices]
            y = aligned_signals[valid_indices]
            
            if len(X) < 50:  # Minimum samples for training
                logger.warning("Insufficient data for ML training")
                return False
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model.fit(X_scaled, y)
            self.is_trained = True
            
            logger.info(f"ML Model trained on {len(X)} samples")
            return True
            
        except Exception as e:
            logger.error(f"Error training ML model: {e}")
            return False
    
    def predict_signals(self, data: pd.DataFrame) -> List[UnifiedTradingSignal]:
        """Generate ML-based trading signals"""
        signals = []
        
        try:
            if self.model is None or not self.is_trained:
                return signals
            
            features = self.extract_features(data)
            
            if len(features) < 50:  # Need minimum data
                return signals
            
            # Get latest features
            latest_features = features.iloc[-1:][self.feature_columns]
            
            if latest_features.isnull().any().any():
                return signals
            
            # Scale and predict
            X_scaled = self.scaler.transform(latest_features)
            prediction = self.model.predict(X_scaled)[0]
            prediction_proba = self.model.predict_proba(X_scaled)[0]
            
            # Convert prediction to signal
            if prediction != 0:  # Non-zero prediction
                confidence = max(prediction_proba)
                
                signal = UnifiedTradingSignal(
                    signal_type=SignalType.BUY if prediction > 0 else SignalType.SELL,
                    strategy_type=StrategyType.ML,
                    strategy_name="ML_Model",
                    timestamp=data.index[-1],
                    price=data['close'].iloc[-1],
                    confidence=confidence,
                    strength=abs(prediction),
                    ml_probability=confidence
                )
                signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error generating ML signals: {e}")
            return []

# =============================================================================
# MULTI-STRATEGY SIGNAL COMBINER
# =============================================================================

class MultiStrategySignalCombiner:
    """Combines signals from multiple strategies"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.strategy_weights = {
            StrategyType.ICT: config.get('ict_weight', 0.3),
            StrategyType.RTM: config.get('rtm_weight', 0.3),
            StrategyType.SMC: config.get('smc_weight', 0.25),
            StrategyType.ML: config.get('ml_weight', 0.15)
        }
        
        # Initialize strategy integrators
        self.ict_integrator = ICTStrategyIntegrator(config)
        self.rtm_integrator = RTMStrategyIntegrator(config)
        self.smc_integrator = EnhancedSMCIntegrator(config)
        self.ml_integrator = MLModelIntegrator(config)
        
    def generate_all_signals(self, data: pd.DataFrame) -> List[UnifiedTradingSignal]:
        """Generate signals from all strategies"""
        all_signals = []
        
        try:
            # Generate signals from each strategy
            ict_signals = self.ict_integrator.generate_ict_signals(data)
            rtm_signals = self.rtm_integrator.generate_rtm_signals(data)
            smc_signals = self.smc_integrator.generate_smc_signals(data)
            ml_signals = self.ml_integrator.predict_signals(data)
            
            # Combine all signals
            all_signals.extend(ict_signals)
            all_signals.extend(rtm_signals)
            all_signals.extend(smc_signals)
            all_signals.extend(ml_signals)
            
            logger.info(f"Generated {len(all_signals)} total signals")
            return all_signals
            
        except Exception as e:
            logger.error(f"Error generating signals: {e}")
            return []
    
    def calculate_consensus_signal(self, signals: List[UnifiedTradingSignal]) -> Optional[UnifiedTradingSignal]:
        """Calculate consensus signal from multiple strategies"""
        try:
            if not signals:
                return None
            
            # Group signals by type
            buy_signals = [s for s in signals if s.signal_type in [SignalType.BUY, SignalType.STRONG_BUY]]
            sell_signals = [s for s in signals if s.signal_type in [SignalType.SELL, SignalType.STRONG_SELL]]
            
            # Calculate weighted scores
            buy_score = sum(s.strength * s.confidence * self.strategy_weights.get(s.strategy_type, 0.25) 
                          for s in buy_signals)
            sell_score = sum(s.strength * s.confidence * self.strategy_weights.get(s.strategy_type, 0.25) 
                           for s in sell_signals)
            
            # Determine consensus
            if buy_score > sell_score and buy_score > 0.5:
                consensus_type = SignalType.BUY
                consensus_strength = buy_score
                consensus_confidence = sum(s.confidence for s in buy_signals) / len(buy_signals) if buy_signals else 0
            elif sell_score > buy_score and sell_score > 0.5:
                consensus_type = SignalType.SELL
                consensus_strength = sell_score
                consensus_confidence = sum(s.confidence for s in sell_signals) / len(sell_signals) if sell_signals else 0
            else:
                return None  # No consensus
            
            # Create consensus signal
            consensus_signal = UnifiedTradingSignal(
                signal_type=consensus_type,
                strategy_type=StrategyType.COMPOSITE,
                strategy_name="Multi_Strategy_Consensus",
                timestamp=signals[0].timestamp,
                price=signals[0].price,
                confidence=consensus_confidence,
                strength=min(1.0, consensus_strength),
                confluence_score=len(signals)
            )
            
            return consensus_signal
            
        except Exception as e:
            logger.error(f"Error calculating consensus signal: {e}")
            return None

# =============================================================================
# FIXED BACKTESTING ENGINE
# =============================================================================

class FixedEnhancedBacktestingEngine:
    """Fixed version of the enhanced backtesting engine"""
    
    def __init__(self, initial_capital: float = 100000, 
                 risk_per_trade: float = 0.02, 
                 leverage: int = 100):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.risk_per_trade = risk_per_trade
        self.leverage = leverage
        
        # Initialize trading records
        self.trades = []
        self.closed_trades = []  # Fix: Initialize closed_trades
        self.portfolio_values = []
        self.position = 0  # Current position size
        self.entry_price = None
        
        # Initialize signal combiner
        self.signal_combiner = MultiStrategySignalCombiner()
        
        logger.info("Fixed Enhanced Backtesting Engine initialized")
        logger.info(f"    Initial Capital: ${initial_capital:,.2f}")
        logger.info(f"    Risk per Trade: {risk_per_trade:.1%}")
        logger.info(f"    Leverage: {leverage}x")
    
    def reset(self):
        """Reset engine state"""
        self.current_capital = self.initial_capital
        self.trades = []
        self.closed_trades = []  # Fix: Reset closed_trades
        self.portfolio_values = []
        self.position = 0
        self.entry_price = None
        logger.info("Engine state reset - ready for backtesting")
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate trading signals using multi-strategy approach"""
        try:
            signals = pd.Series(0, index=data.index)  # Initialize with HOLD signals
            
            # Generate signals for each bar
            for i in range(50, len(data)):  # Start from 50 to have enough data
                current_data = data.iloc[:i+1]
                
                # Get signals from all strategies
                strategy_signals = self.signal_combiner.generate_all_signals(current_data)
                
                if strategy_signals:
                    # Calculate consensus signal
                    consensus = self.signal_combiner.calculate_consensus_signal(strategy_signals)
                    if consensus:
                        signals.iloc[i] = consensus.to_backtest_signal()
            
            return signals
            
        except Exception as e:
            logger.error(f"Error generating signals: {e}")
            return pd.Series(0, index=data.index)
    
    def run_backtest(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Run complete backtest"""
        try:
            logger.info("Starting comprehensive backtest")
            
            # Reset state
            self.reset()
            
            # Generate signals
            logger.info("Generating trading signals...")
            signals = self.generate_signals(data)
            
            signal_counts = signals.value_counts()
            logger.info(f"Signal distribution: {signal_counts.to_dict()}")
            
            # Run simulation
            logger.info("Running backtest simulation...")
            self._run_simulation(data, signals)
            
            # Calculate metrics
            logger.info("Calculating performance metrics...")
            metrics = self._calculate_metrics()
            
            logger.info("Comprehensive backtest completed!")
            logger.info(f"Total Return: {metrics.get('total_return', 0):.2%}")
            logger.info(f"Total Trades: {metrics.get('total_trades', 0)}")
            logger.info(f"Win Rate: {metrics.get('win_rate', 0):.1%}")
            
            return {
                'trades': self.trades,
                'closed_trades': self.closed_trades,
                'portfolio_values': self.portfolio_values,
                'metrics': metrics,
                'signals': signals
            }
            
        except Exception as e:
            logger.error(f"Error in backtest: {e}")
            return {}
    
    def _run_simulation(self, data: pd.DataFrame, signals: pd.Series):
        """Run the trading simulation"""
        try:
            logger.info(f"Running simulation with {len(data)} bars...")
            
            for i in range(len(data)):
                current_bar = data.iloc[i]
                signal = signals.iloc[i]
                current_price = current_bar['close']
                current_time = data.index[i]
                
                # Record portfolio value
                portfolio_value = self.current_capital
                if self.position != 0 and self.entry_price:
                    unrealized_pnl = (current_price - self.entry_price) * self.position
                    portfolio_value += unrealized_pnl
                
                self.portfolio_values.append({
                    'timestamp': current_time,
                    'value': portfolio_value
                })
                
                # Process signals
                if signal != 0 and self.position == 0:  # New entry
                    self._enter_position(signal, current_price, current_time)
                elif signal != 0 and self.position != 0:  # Exit existing position
                    self._exit_position(current_price, current_time, "signal_exit")
                    # Enter new position
                    self._enter_position(signal, current_price, current_time)
                
                # Check for stop loss or take profit
                if self.position != 0:
                    self._check_exit_conditions(current_bar, current_time)
            
            # Close any remaining position
            if self.position != 0:
                final_bar = data.iloc[-1]
                self._exit_position(final_bar['close'], data.index[-1], "final_exit")
            
            logger.info(f"Simulation completed with {len(self.trades)} total trades")
            
        except Exception as e:
            logger.error(f"Error in simulation: {e}")
    
    def _enter_position(self, signal: int, price: float, timestamp: pd.Timestamp):
        """Enter a new position"""
        try:
            # Calculate position size based on risk management
            risk_amount = self.current_capital * self.risk_per_trade
            position_size = risk_amount * self.leverage / price
            
            if signal > 0:  # Buy
                self.position = position_size
            else:  # Sell
                self.position = -position_size
            
            self.entry_price = price
            
            # Record trade
            trade = {
                'entry_time': timestamp,
                'entry_price': price,
                'position_size': self.position,
                'signal_type': 'BUY' if signal > 0 else 'SELL',
                'capital_at_entry': self.current_capital
            }
            self.trades.append(trade)
            
        except Exception as e:
            logger.error(f"Error entering position: {e}")
    
    def _exit_position(self, price: float, timestamp: pd.Timestamp, exit_reason: str):
        """Exit current position"""
        try:
            if self.position == 0:
                return
            
            # Calculate P&L
            pnl = (price - self.entry_price) * self.position
            self.current_capital += pnl
            
            # Record closed trade
            if self.trades:
                last_trade = self.trades[-1].copy()
                last_trade.update({
                    'exit_time': timestamp,
                    'exit_price': price,
                    'exit_reason': exit_reason,
                    'pnl': pnl,
                    'capital_after_exit': self.current_capital,
                    'return_pct': pnl / last_trade['capital_at_entry']
                })
                self.closed_trades.append(last_trade)
            
            # Reset position
            self.position = 0
            self.entry_price = None
            
        except Exception as e:
            logger.error(f"Error exiting position: {e}")
    
    def _check_exit_conditions(self, current_bar: pd.Series, timestamp: pd.Timestamp):
        """Check for stop loss or take profit conditions"""
        try:
            if self.position == 0 or not self.entry_price:
                return
            
            current_price = current_bar['close']
            
            # Simple stop loss and take profit (2% risk, 4% reward)
            if self.position > 0:  # Long position
                stop_loss = self.entry_price * 0.98
                take_profit = self.entry_price * 1.04
                
                if current_price <= stop_loss:
                    self._exit_position(current_price, timestamp, "stop_loss")
                elif current_price >= take_profit:
                    self._exit_position(current_price, timestamp, "take_profit")
            
            else:  # Short position
                stop_loss = self.entry_price * 1.02
                take_profit = self.entry_price * 0.96
                
                if current_price >= stop_loss:
                    self._exit_position(current_price, timestamp, "stop_loss")
                elif current_price <= take_profit:
                    self._exit_position(current_price, timestamp, "take_profit")
                    
        except Exception as e:
            logger.error(f"Error checking exit conditions: {e}")
    
    def _calculate_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics"""
        try:
            if not self.closed_trades:
                return {
                    'total_return': 0.0,
                    'total_trades': 0,
                    'win_rate': 0.0,
                    'avg_return': 0.0,
                    'max_drawdown': 0.0,
                    'sharpe_ratio': 0.0
                }
            
            # Fix: Use closed_trades instead of undefined returns_returns
            trade_returns = [trade['return_pct'] for trade in self.closed_trades]
            
            # Calculate basic metrics
            total_return = (self.current_capital - self.initial_capital) / self.initial_capital
            total_trades = len(self.closed_trades)
            winning_trades = len([t for t in self.closed_trades if t['pnl'] > 0])
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            avg_return = np.mean(trade_returns) if trade_returns else 0
            
            # Calculate drawdown
            portfolio_values = [pv['value'] for pv in self.portfolio_values]
            running_max = np.maximum.accumulate(portfolio_values)
            drawdown = (portfolio_values - running_max) / running_max
            max_drawdown = np.min(drawdown) if len(drawdown) > 0 else 0
            
            # Calculate Sharpe ratio
            if len(trade_returns) > 1:
                returns_std = np.std(trade_returns)
                sharpe_ratio = avg_return / returns_std if returns_std > 0 else 0
            else:
                sharpe_ratio = 0
            
            return {
                'total_return': total_return,
                'total_trades': total_trades,
                'win_rate': win_rate,
                'avg_return': avg_return,
                'max_drawdown': abs(max_drawdown),
                'sharpe_ratio': sharpe_ratio,
                'final_capital': self.current_capital
            }
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            return {}

# =============================================================================
# DEMO AND TESTING
# =============================================================================

def demo_integrated_system():
    """Demo the complete integrated system"""
    try:
        logger.info("Enhanced Real Data Trading System Demo")
        logger.info("=" * 60)
        
        # Generate sample data
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=1000, freq='H')
        
        # Generate more realistic price data
        returns = np.random.normal(0, 0.001, 1000)
        prices = 1.1000 + np.cumsum(returns)
        
        data = pd.DataFrame({
            'open': prices + np.random.normal(0, 0.0002, 1000),
            'high': prices + np.abs(np.random.normal(0, 0.0005, 1000)),
            'low': prices - np.abs(np.random.normal(0, 0.0005, 1000)),
            'close': prices,
            'volume': np.random.randint(1000, 10000, 1000)
        }, index=dates)
        
        # Ensure OHLC consistency
        data['high'] = np.maximum(data['high'], np.maximum(data['open'], data['close']))
        data['low'] = np.minimum(data['low'], np.minimum(data['open'], data['close']))
        
        logger.info(f"Generated sample data: {len(data)} bars")
        
        # Initialize and run backtest
        engine = FixedEnhancedBacktestingEngine(
            initial_capital=100000,
            risk_per_trade=0.02,
            leverage=100
        )
        
        results = engine.run_backtest(data)
        
        # Display results
        metrics = results.get('metrics', {})
        logger.info("=" * 60)
        logger.info("BACKTEST RESULTS:")
        logger.info(f"Total Return: {metrics.get('total_return', 0):.2%}")
        logger.info(f"Total Trades: {metrics.get('total_trades', 0)}")
        logger.info(f"Win Rate: {metrics.get('win_rate', 0):.1%}")
        logger.info(f"Average Return per Trade: {metrics.get('avg_return', 0):.2%}")
        logger.info(f"Max Drawdown: {metrics.get('max_drawdown', 0):.2%}")
        logger.info(f"Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.3f}")
        logger.info(f"Final Capital: ${metrics.get('final_capital', 0):,.2f}")
        
        logger.info("Demo completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        return False

if __name__ == "__main__":
    success = demo_integrated_system()
    
    if success:
        print("Demo completed successfully - all components integrated!")
    else:
        print("Demo failed - please check error messages above")
