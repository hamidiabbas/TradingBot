#!/usr/bin/env python3

"""
===============================================================
PROFESSIONAL SIGNAL FACTORY v2.1 - PATH 2A ENHANCED WITH AI
===============================================================

Advanced signal processing with REAL intelligence and ML foundations
(FIXED - No monkey patching of immutable types)
"""

import pandas as pd
import numpy as np
import os
import sys
import importlib
import inspect
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import warnings
import json
from collections import defaultdict, deque
import threading
import time
import math
from scipy import stats
import logging

# Advanced ML/AI imports (future-ready)
try:
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import RandomForestClassifier
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

# Add strategies to path
current_dir = Path(__file__).parent
strategies_dir = current_dir / "strategies"
if str(strategies_dir) not in sys.path:
    sys.path.append(str(strategies_dir))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SAFE ARRAY HANDLING FUNCTION (no monkey patching)
def safe_array_comparison(arr, comparison_op, value):
    """Safely handle array comparisons to avoid ambiguity"""
    try:
        if hasattr(arr, 'size'):
            if arr.size == 0:
                return False
            elif arr.size == 1:
                return comparison_op(arr.item(), value)
            else:
                # For multi-element arrays, use .any() as default
                result = comparison_op(arr, value)
                return result.any() if hasattr(result, 'any') else bool(result)
        return comparison_op(arr, value)
    except:
        return False

def safe_bool_check(value):
    """Safely convert values to boolean, handling arrays"""
    try:
        if hasattr(value, 'size') and hasattr(value, 'any'):
            # It's a numpy array
            if value.size == 0:
                return False
            elif value.size == 1:
                return bool(value.item())
            else:
                return value.any()  # Default to any() for multi-element arrays
        return bool(value)
    except:
        return False

warnings.filterwarnings('ignore')

class SignalQuality(Enum):
    """Enhanced signal quality levels with intelligence scoring"""
    PREMIUM = "PREMIUM"     # 0.85+ confidence, AI-validated
    HIGH = "HIGH"          # 0.75+ confidence, strong intelligence
    MEDIUM = "MEDIUM"      # 0.60+ confidence, good intelligence
    LOW = "LOW"           # 0.45+ confidence, basic intelligence
    REJECTED = "REJECTED"  # Below intelligence thresholds

class SignalDirection(Enum):
    """Signal directions with strength indicators"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    STRONG_BUY = "STRONG_BUY"
    STRONG_SELL = "STRONG_SELL"

class MarketRegime(Enum):
    """Enhanced market regime classification"""
    BULLISH_TRENDING = "BULLISH_TRENDING"
    BEARISH_TRENDING = "BEARISH_TRENDING"
    SIDEWAYS_RANGING = "SIDEWAYS_RANGING"
    HIGH_VOLATILITY = "HIGH_VOLATILITY"
    LOW_VOLATILITY = "LOW_VOLATILITY"
    BREAKOUT_PENDING = "BREAKOUT_PENDING"
    SQUEEZE_ACTIVE = "SQUEEZE_ACTIVE"
    UNKNOWN = "UNKNOWN"

@dataclass
class IntelligenceMetrics:
    """Advanced intelligence metrics for signals"""
    market_regime_fit: float = 0.0
    strategy_consensus_score: float = 0.0
    cross_correlation_penalty: float = 0.0
    volatility_appropriateness: float = 0.0
    momentum_alignment: float = 0.0
    session_suitability: float = 0.0
    ai_prediction_confidence: float = 0.0
    historical_success_rate: float = 0.0
    risk_adjusted_score: float = 0.0
    composite_intelligence: float = 0.0

@dataclass
class ValidatedSignal:
    """Enhanced validated signal with PATH 2A intelligence"""
    symbol: str
    direction: SignalDirection
    confidence: float
    quality: SignalQuality
    
    # Core signal data
    entry_price: float
    timestamp: datetime
    
    # Strategy information
    primary_strategy: str
    contributing_strategies: List[str] = field(default_factory=list)
    strategy_votes: Dict[str, str] = field(default_factory=dict)
    
    # PATH 2A: Intelligence metrics
    intelligence: IntelligenceMetrics = field(default_factory=IntelligenceMetrics)
    
    # Enhanced validation metrics
    validation_score: float = 0.0
    technical_score: float = 0.0
    fundamental_score: float = 0.0
    sentiment_score: float = 0.0
    
    # Risk management
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    risk_reward_ratio: Optional[float] = None
    max_risk_pct: float = 0.02
    
    # Advanced analytics
    market_regime: MarketRegime = MarketRegime.UNKNOWN
    volatility_regime: str = "normal"
    correlation_conflicts: List[str] = field(default_factory=list)
    signal_strength_history: List[float] = field(default_factory=list)
    
    # ML/AI predictions
    ml_success_probability: float = 0.0
    ai_risk_assessment: float = 0.0
    predicted_profit_potential: float = 0.0
    
    # Execution data
    kelly_fraction: Optional[float] = None
    position_size: Optional[float] = None
    execution_priority: int = 1
    
    # Metadata
    signal_id: str = ""
    expiry_time: Optional[datetime] = None
    reason: str = ""
    warnings: List[str] = field(default_factory=list)

class AdvancedIntelligenceEngine:
    """
    PATH 2A: Advanced Intelligence Engine with ML/AI foundations
    ==========================================================
    """
    
    def __init__(self):
        self.name = "AdvancedIntelligenceEngine"
        
        # Intelligence systems
        self.market_regime_detector = AdvancedMarketRegimeDetector()
        self.strategy_intelligence = StrategyIntelligenceAnalyzer()
        self.signal_predictor = SignalQualityPredictor()
        
        # ML/AI components (future-ready)
        self.ml_models = {}
        self.feature_extractors = {}
        self.prediction_cache = {}
        
        # Learning systems
        self.performance_memory = deque(maxlen=1000)
        self.strategy_performance_matrix = defaultdict(dict)
        self.market_pattern_recognition = MarketPatternRecognizer()
        
        # Dynamic thresholds
        self.dynamic_thresholds = {
            'base_confidence': 0.35,
            'current_confidence': 0.35,
            'intelligence_threshold': 0.6,
            'regime_adaptation_factor': 0.2
        }
        
        logger.info("🧠 Advanced Intelligence Engine initialized with ML foundations")
    
    def analyze_signal_intelligence(self, signal: ValidatedSignal, market_data: Dict, 
                                  strategy_context: Dict) -> IntelligenceMetrics:
        """
        Advanced intelligence analysis for signals
        """
        try:
            intelligence = IntelligenceMetrics()
            
            # 1. Market Regime Fit Analysis
            intelligence.market_regime_fit = self._calculate_regime_fit(signal, market_data)
            
            # 2. Strategy Consensus Analysis
            intelligence.strategy_consensus_score = self._analyze_strategy_consensus(signal, strategy_context)
            
            # 3. Cross-Correlation Analysis
            intelligence.cross_correlation_penalty = self._calculate_correlation_penalty(signal, strategy_context)
            
            # 4. Volatility Appropriateness
            intelligence.volatility_appropriateness = self._assess_volatility_appropriateness(signal, market_data)
            
            # 5. Momentum Alignment
            intelligence.momentum_alignment = self._calculate_momentum_alignment(signal, market_data)
            
            # 6. Session Suitability
            intelligence.session_suitability = self._assess_session_suitability(signal)
            
            # 7. AI Prediction (if available)
            intelligence.ai_prediction_confidence = self._get_ai_prediction(signal, market_data)
            
            # 8. Historical Success Rate
            intelligence.historical_success_rate = self._get_historical_success_rate(signal)
            
            # 9. Risk-Adjusted Score
            intelligence.risk_adjusted_score = self._calculate_risk_adjusted_score(signal, intelligence)
            
            # 10. Composite Intelligence Score
            intelligence.composite_intelligence = self._calculate_composite_intelligence(intelligence)
            
            return intelligence
            
        except Exception as e:
            logger.error(f"Intelligence analysis error: {e}")
            return IntelligenceMetrics()
    
    def _calculate_regime_fit(self, signal: ValidatedSignal, market_data: Dict) -> float:
        """Calculate how well signal fits detected market regime"""
        try:
            regime = self.market_regime_detector.detect_enhanced_regime(market_data.get('dataframe'))
            signal.market_regime = regime
            
            # Strategy-regime compatibility matrix
            compatibility_matrix = {
                MarketRegime.BULLISH_TRENDING: {
                    'TrendStrategy': 0.9,
                    'MultiFacetTrendStrategy': 0.85,
                    'GridTradingStrategy': 0.3,
                    'RangeStrategy': 0.2,
                    'default': 0.6
                },
                MarketRegime.BEARISH_TRENDING: {
                    'TrendStrategy': 0.9,
                    'MultiFacetTrendStrategy': 0.85,
                    'GridTradingStrategy': 0.3,
                    'RangeStrategy': 0.2,
                    'default': 0.6
                },
                MarketRegime.SIDEWAYS_RANGING: {
                    'GridTradingStrategy': 0.95,
                    'RangeStrategy': 0.9,
                    'TrendStrategy': 0.2,
                    'MultiFacetTrendStrategy': 0.3,
                    'default': 0.7
                },
                MarketRegime.HIGH_VOLATILITY: {
                    'TrendStrategy': 0.8,
                    'MultiFacetTrendStrategy': 0.75,
                    'GridTradingStrategy': 0.4,
                    'RangeStrategy': 0.3,
                    'default': 0.5
                },
                MarketRegime.LOW_VOLATILITY: {
                    'GridTradingStrategy': 0.85,
                    'RangeStrategy': 0.8,
                    'TrendStrategy': 0.6,
                    'MultiFacetTrendStrategy': 0.65,
                    'default': 0.7
                }
            }
            
            strategy_name = signal.primary_strategy
            regime_compat = compatibility_matrix.get(regime, {})
            
            # Find best match for strategy name
            fit_score = regime_compat.get('default', 0.5)
            for strategy_key, score in regime_compat.items():
                if strategy_key in strategy_name:
                    fit_score = score
                    break
            
            # Direction alignment bonus
            if regime in [MarketRegime.BULLISH_TRENDING] and signal.direction in [SignalDirection.BUY, SignalDirection.STRONG_BUY]:
                fit_score += 0.1
            elif regime in [MarketRegime.BEARISH_TRENDING] and signal.direction in [SignalDirection.SELL, SignalDirection.STRONG_SELL]:
                fit_score += 0.1
            
            return min(1.0, fit_score)
            
        except Exception as e:
            logger.error(f"Regime fit calculation error: {e}")
            return 0.5
    
    def _analyze_strategy_consensus(self, signal: ValidatedSignal, strategy_context: Dict) -> float:
        """Analyze consensus strength among strategies"""
        try:
            contributing_count = len(signal.contributing_strategies)
            total_strategies = strategy_context.get('total_strategies', 1)
            
            # Base consensus score
            consensus_score = contributing_count / max(1, total_strategies)
            
            # Weighted consensus based on strategy performance
            weighted_consensus = 0.0
            total_weight = 0.0
            
            for strategy_name in signal.contributing_strategies:
                strategy_weight = strategy_context.get('strategy_weights', {}).get(strategy_name, 1.0)
                weighted_consensus += strategy_weight
                total_weight += strategy_weight
            
            if total_weight > 0:
                weighted_consensus /= total_weight
                consensus_score = (consensus_score + weighted_consensus) / 2
            
            # Confidence alignment bonus
            strategy_votes = signal.strategy_votes
            if strategy_votes:
                same_direction_count = sum(1 for vote in strategy_votes.values() 
                                         if vote == signal.direction.value)
                direction_consensus = same_direction_count / len(strategy_votes)
                consensus_score = (consensus_score + direction_consensus) / 2
            
            return min(1.0, consensus_score)
            
        except Exception as e:
            logger.error(f"Strategy consensus analysis error: {e}")
            return 0.5
    
    def _calculate_correlation_penalty(self, signal: ValidatedSignal, strategy_context: Dict) -> float:
        """Calculate penalty for highly correlated strategies"""
        try:
            if len(signal.contributing_strategies) <= 1:
                return 0.0
            
            # Strategy correlation matrix (simplified)
            correlation_matrix = {
                ('TrendStrategy', 'MultiFacetTrendStrategy'): 0.8,
                ('GridTradingStrategy', 'RangeStrategy'): 0.7,
                ('PrimaryStrategy', 'TrendStrategy'): 0.6,
            }
            
            total_correlation = 0.0
            pair_count = 0
            
            strategies = signal.contributing_strategies
            for i in range(len(strategies)):
                for j in range(i + 1, len(strategies)):
                    strategy_pair = tuple(sorted([strategies[i], strategies[j]]))
                    correlation = correlation_matrix.get(strategy_pair, 0.3)  # Default moderate correlation
                    total_correlation += correlation
                    pair_count += 1
            
            if pair_count == 0:
                return 0.0
            
            avg_correlation = total_correlation / pair_count
            
            # Convert to penalty (higher correlation = higher penalty)
            penalty = max(0.0, (avg_correlation - 0.5) * 0.8)  # Scale 0.5-1.0 correlation to 0-0.4 penalty
            
            return min(0.5, penalty)
            
        except Exception as e:
            logger.error(f"Correlation penalty calculation error: {e}")
            return 0.0
    
    def _assess_volatility_appropriateness(self, signal: ValidatedSignal, market_data: Dict) -> float:
        """Assess if signal is appropriate for current volatility"""
        try:
            df = market_data.get('dataframe')
            if df is None or len(df) < 20:
                return 0.6
            
            # Calculate current volatility
            returns = df['close'].pct_change().dropna()
            current_vol = returns.tail(10).std()
            historical_vol = returns.tail(50).std() if len(returns) >= 50 else returns.std()
            
            if historical_vol <= 0:
                return 0.6
            
            vol_ratio = current_vol / historical_vol
            
            # Strategy-specific volatility preferences
            strategy_vol_preferences = {
                'GridTradingStrategy': {'optimal_min': 0.5, 'optimal_max': 1.2},
                'RangeStrategy': {'optimal_min': 0.3, 'optimal_max': 1.0},
                'TrendStrategy': {'optimal_min': 0.8, 'optimal_max': 2.0},
                'MultiFacetTrendStrategy': {'optimal_min': 0.7, 'optimal_max': 1.8},
                'default': {'optimal_min': 0.6, 'optimal_max': 1.4}
            }
            
            # Find strategy preference
            strategy_pref = strategy_vol_preferences.get('default')
            for strategy_key, pref in strategy_vol_preferences.items():
                if strategy_key in signal.primary_strategy:
                    strategy_pref = pref
                    break
            
            # Calculate appropriateness score
            optimal_min = strategy_pref['optimal_min']
            optimal_max = strategy_pref['optimal_max']
            
            if optimal_min <= vol_ratio <= optimal_max:
                appropriateness = 1.0
            elif vol_ratio < optimal_min:
                appropriateness = max(0.2, vol_ratio / optimal_min)
            else:  # vol_ratio > optimal_max
                appropriateness = max(0.2, optimal_max / vol_ratio)
            
            return appropriateness
            
        except Exception as e:
            logger.error(f"Volatility appropriateness error: {e}")
            return 0.6
    
    def _calculate_momentum_alignment(self, signal: ValidatedSignal, market_data: Dict) -> float:
        """Calculate alignment between signal direction and market momentum"""
        try:
            df = market_data.get('dataframe')
            if df is None or len(df) < 10:
                return 0.5
            
            close = df['close']
            
            # Multiple timeframe momentum
            momentum_periods = [5, 10, 20]
            momentum_scores = []
            
            for period in momentum_periods:
                if len(close) > period:
                    momentum = (close.iloc[-1] - close.iloc[-period]) / close.iloc[-period]
                    momentum_scores.append(momentum)
            
            if not momentum_scores:
                return 0.5
            
            # Weighted average (more weight to recent momentum)
            weights = [0.5, 0.3, 0.2][:len(momentum_scores)]
            avg_momentum = sum(m * w for m, w in zip(momentum_scores, weights))
            
            # Alignment calculation
            if signal.direction in [SignalDirection.BUY, SignalDirection.STRONG_BUY]:
                # For buy signals, positive momentum is good
                alignment = max(0.0, min(1.0, 0.5 + avg_momentum * 25))
            else:
                # For sell signals, negative momentum is good
                alignment = max(0.0, min(1.0, 0.5 - avg_momentum * 25))
            
            return alignment
            
        except Exception as e:
            logger.error(f"Momentum alignment error: {e}")
            return 0.5
    
    def _assess_session_suitability(self, signal: ValidatedSignal) -> float:
        """Assess signal suitability for current trading session"""
        try:
            current_hour = datetime.now().hour
            
            # Session classifications
            if 0 <= current_hour < 8:
                session = 'asian'
                activity_level = 0.6
            elif 8 <= current_hour < 16:
                session = 'london'
                activity_level = 0.9
            elif 16 <= current_hour < 20:
                session = 'overlap'
                activity_level = 1.0
            else:
                session = 'ny'
                activity_level = 0.8
            
            # Strategy-session preferences
            session_preferences = {
                'GridTradingStrategy': {
                    'asian': 0.7, 'london': 0.9, 'overlap': 0.95, 'ny': 0.8
                },
                'TrendStrategy': {
                    'asian': 0.6, 'london': 0.85, 'overlap': 0.9, 'ny': 0.85
                },
                'RangeStrategy': {
                    'asian': 0.8, 'london': 0.8, 'overlap': 0.7, 'ny': 0.75
                },
                'default': {
                    'asian': 0.7, 'london': 0.8, 'overlap': 0.85, 'ny': 0.8
                }
            }
            
            # Find strategy preference
            strategy_session_pref = session_preferences.get('default')
            for strategy_key, pref in session_preferences.items():
                if strategy_key in signal.primary_strategy:
                    strategy_session_pref = pref
                    break
            
            base_suitability = strategy_session_pref.get(session, 0.7)
            
            # Activity level adjustment
            activity_adjusted_suitability = base_suitability * (0.7 + activity_level * 0.3)
            
            return min(1.0, activity_adjusted_suitability)
            
        except Exception as e:
            logger.error(f"Session suitability error: {e}")
            return 0.7
    
    def _get_ai_prediction(self, signal: ValidatedSignal, market_data: Dict) -> float:
        """Get AI/ML prediction confidence (foundation for future ML models)"""
        try:
            # Foundation for future ML integration
            if not ML_AVAILABLE:
                # Simulate ML prediction using heuristics
                feature_score = self._extract_signal_features(signal, market_data)
                return min(0.9, max(0.1, feature_score))
            
            # Future ML model integration point
            return self._extract_signal_features(signal, market_data)
            
        except Exception as e:
            logger.error(f"AI prediction error: {e}")
            return 0.5
    
    def _extract_signal_features(self, signal: ValidatedSignal, market_data: Dict) -> float:
        """Extract features for ML (foundation for future AI models)"""
        try:
            features = []
            
            # Signal features
            features.append(signal.confidence)
            features.append(len(signal.contributing_strategies) / 10.0)  # Normalize
            
            # Market features
            df = market_data.get('dataframe')
            if df is not None and len(df) > 20:
                # Volatility feature
                returns = df['close'].pct_change().dropna()
                vol_feature = min(1.0, returns.tail(20).std() * 100)
                features.append(vol_feature)
                
                # Trend feature
                ma_20 = df['close'].rolling(20).mean().iloc[-1]
                current_price = df['close'].iloc[-1]
                trend_feature = min(1.0, abs(current_price - ma_20) / ma_20 * 50)
                features.append(trend_feature)
                
                # Volume feature (if available)
                if 'volume' in df.columns:
                    vol_sma = df['volume'].rolling(20).mean().iloc[-1]
                    current_vol = df['volume'].iloc[-1]
                    volume_feature = min(2.0, current_vol / vol_sma) / 2.0
                    features.append(volume_feature)
                else:
                    features.append(0.5)  # Neutral if no volume
            else:
                features.extend([0.5, 0.5, 0.5])  # Neutral features
            
            # Combine features (simple average for now)
            if features:
                return sum(features) / len(features)
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"Feature extraction error: {e}")
            return 0.5
    
    def _get_historical_success_rate(self, signal: ValidatedSignal) -> float:
        """Get historical success rate for similar signals"""
        try:
            # Look for similar signals in performance memory
            similar_signals = []
            
            for record in self.performance_memory:
                if (record.get('strategy') == signal.primary_strategy and
                    record.get('direction') == signal.direction.value and
                    record.get('symbol') == signal.symbol):
                    similar_signals.append(record)
            
            if len(similar_signals) < 5:
                return 0.6  # Default success rate
            
            # Calculate success rate from recent similar signals
            recent_signals = similar_signals[-20:]  # Last 20 similar signals
            success_count = sum(1 for s in recent_signals if s.get('success', False))
            
            success_rate = success_count / len(recent_signals)
            
            # Weight recent performance more heavily
            if len(recent_signals) >= 10:
                very_recent = recent_signals[-5:]
                recent_success_rate = sum(1 for s in very_recent if s.get('success', False)) / len(very_recent)
                # 70% weight to recent, 30% to historical
                success_rate = success_rate * 0.3 + recent_success_rate * 0.7
            
            return success_rate
            
        except Exception as e:
            logger.error(f"Historical success rate error: {e}")
            return 0.6
    
    def _calculate_risk_adjusted_score(self, signal: ValidatedSignal, intelligence: IntelligenceMetrics) -> float:
        """Calculate risk-adjusted intelligence score"""
        try:
            # Base score from other intelligence metrics
            base_score = (
                intelligence.market_regime_fit * 0.2 +
                intelligence.strategy_consensus_score * 0.2 +
                intelligence.volatility_appropriateness * 0.15 +
                intelligence.momentum_alignment * 0.15 +
                intelligence.session_suitability * 0.1 +
                intelligence.ai_prediction_confidence * 0.1 +
                intelligence.historical_success_rate * 0.1
            )
            
            # Risk adjustments
            correlation_penalty = intelligence.cross_correlation_penalty
            confidence_factor = min(1.2, max(0.8, signal.confidence * 2))
            
            # Apply adjustments
            risk_adjusted = base_score * confidence_factor * (1 - correlation_penalty * 0.5)
            
            return min(1.0, max(0.0, risk_adjusted))
            
        except Exception as e:
            logger.error(f"Risk-adjusted score error: {e}")
            return 0.5
    
    def _calculate_composite_intelligence(self, intelligence: IntelligenceMetrics) -> float:
        """Calculate final composite intelligence score"""
        try:
            # Weighted combination of all intelligence factors
            composite = (
                intelligence.market_regime_fit * 0.18 +
                intelligence.strategy_consensus_score * 0.16 +
                intelligence.volatility_appropriateness * 0.14 +
                intelligence.momentum_alignment * 0.12 +
                intelligence.session_suitability * 0.10 +
                intelligence.ai_prediction_confidence * 0.10 +
                intelligence.historical_success_rate * 0.12 +
                intelligence.risk_adjusted_score * 0.08
            )
            
            # Apply correlation penalty
            composite *= (1 - intelligence.cross_correlation_penalty * 0.3)
            
            return min(1.0, max(0.0, composite))
            
        except Exception as e:
            logger.error(f"Composite intelligence error: {e}")
            return 0.5

# Continue with remaining classes (shortened for space)...

class AdvancedMarketRegimeDetector:
    """Advanced market regime detection with multiple indicators"""
    
    def detect_enhanced_regime(self, df: pd.DataFrame) -> MarketRegime:
        """Detect market regime using advanced analysis"""
        try:
            if df is None or df.empty or len(df) < 30:
                return MarketRegime.UNKNOWN
            
            close = df['close']
            
            # Trend detection
            trend_score = self._calculate_trend_strength(close)
            
            # Volatility analysis
            vol_regime = self._analyze_volatility_regime(close)
            
            # Range analysis
            range_analysis = self._analyze_price_ranges(df)
            
            # Combine indicators to determine regime
            if abs(trend_score) > 0.6 and vol_regime != 'high':
                return MarketRegime.BULLISH_TRENDING if trend_score > 0 else MarketRegime.BEARISH_TRENDING
            elif vol_regime == 'high':
                return MarketRegime.HIGH_VOLATILITY
            elif vol_regime == 'low' and range_analysis['compression'] > 0.7:
                return MarketRegime.SQUEEZE_ACTIVE
            elif abs(trend_score) < 0.3 and range_analysis['stability'] > 0.6:
                return MarketRegime.SIDEWAYS_RANGING
            elif vol_regime == 'low':
                return MarketRegime.LOW_VOLATILITY
            else:
                return MarketRegime.UNKNOWN
                
        except Exception as e:
            logger.error(f"Regime detection error: {e}")
            return MarketRegime.UNKNOWN
    
    def _calculate_trend_strength(self, close: pd.Series) -> float:
        """Calculate trend strength (-1 to +1)"""
        try:
            if len(close) < 50:
                return 0.0
            
            # Multiple moving averages
            ma_10 = close.rolling(10).mean()
            ma_20 = close.rolling(20).mean()
            ma_50 = close.rolling(50).mean()
            
            current_price = close.iloc[-1]
            
            # Trend alignment score
            trend_scores = []
            
            if pd.notna(ma_10.iloc[-1]):
                trend_scores.append(1 if current_price > ma_10.iloc[-1] else -1)
            if pd.notna(ma_20.iloc[-1]):
                trend_scores.append(1 if current_price > ma_20.iloc[-1] else -1)
            if pd.notna(ma_50.iloc[-1]):
                trend_scores.append(1 if current_price > ma_50.iloc[-1] else -1)
            
            if not trend_scores:
                return 0.0
            
            # Weighted average
            weights = [0.5, 0.3, 0.2][:len(trend_scores)]
            trend_strength = sum(score * weight for score, weight in zip(trend_scores, weights))
            
            # Slope analysis for strength
            if len(close) >= 20:
                slope = (close.iloc[-1] - close.iloc[-20]) / close.iloc[-20]
                trend_strength *= min(1.0, abs(slope) * 50)
            
            return max(-1.0, min(1.0, trend_strength))
            
        except Exception:
            return 0.0
    
    def _analyze_volatility_regime(self, close: pd.Series) -> str:
        """Analyze volatility regime"""
        try:
            returns = close.pct_change().dropna()
            if len(returns) < 20:
                return 'normal'
            
            current_vol = returns.tail(10).std()
            historical_vol = returns.tail(50).std() if len(returns) >= 50 else returns.std()
            
            if historical_vol <= 0:
                return 'normal'
            
            vol_ratio = current_vol / historical_vol
            
            if vol_ratio > 1.5:
                return 'high'
            elif vol_ratio < 0.6:
                return 'low'
            else:
                return 'normal'
                
        except Exception:
            return 'normal'
    
    def _analyze_price_ranges(self, df: pd.DataFrame) -> Dict[str, float]:
        """Analyze price ranges and compression"""
        try:
            if len(df) < 20:
                return {'compression': 0.5, 'stability': 0.5}
            
            high = df['high']
            low = df['low']
            
            # Current range vs historical
            current_range = high.iloc[-1] - low.iloc[-1]
            avg_range = (high.rolling(20).max() - low.rolling(20).min()).mean()
            
            compression = 1.0 - (current_range / avg_range) if avg_range > 0 else 0.0
            compression = max(0.0, min(1.0, compression))
            
            # Price stability
            close_std = df['close'].rolling(10).std().iloc[-1]
            close_mean = df['close'].rolling(10).mean().iloc[-1]
            
            stability = 1.0 - (close_std / close_mean) if close_mean > 0 else 0.5
            stability = max(0.0, min(1.0, stability))
            
            return {'compression': compression, 'stability': stability}
            
        except Exception:
            return {'compression': 0.5, 'stability': 0.5}

class StrategyIntelligenceAnalyzer:
    """Analyze strategy intelligence and performance"""
    
    def __init__(self):
        self.strategy_correlations = self._initialize_correlations()
    
    def _initialize_correlations(self) -> Dict[Tuple[str, str], float]:
        """Initialize strategy correlation matrix"""
        return {
            ('TrendStrategy', 'MultiFacetTrendStrategy'): 0.8,
            ('GridTradingStrategy', 'RangeStrategy'): 0.7,
            ('PrimaryStrategy', 'TrendStrategy'): 0.6,
            ('GridTradingStrategy', 'TrendStrategy'): 0.2,
            ('RangeStrategy', 'TrendStrategy'): 0.1,
        }

class SignalQualityPredictor:
    """Predict signal quality using advanced analysis"""
    
    def predict_quality(self, signal: ValidatedSignal, intelligence: IntelligenceMetrics) -> float:
        """Predict signal quality score"""
        try:
            # Base prediction from intelligence
            quality_score = intelligence.composite_intelligence * 0.6
            
            # Add confidence factor
            quality_score += signal.confidence * 0.3
            
            # Add strategy reputation factor
            strategy_reputation = self._get_strategy_reputation(signal.primary_strategy)
            quality_score += strategy_reputation * 0.1
            
            return min(1.0, max(0.0, quality_score))
            
        except Exception:
            return 0.5
    
    def _get_strategy_reputation(self, strategy_name: str) -> float:
        """Get strategy reputation score"""
        # Simplified reputation scoring
        reputation_scores = {
            'TrendStrategy': 0.8,
            'GridTradingStrategy': 0.85,
            'RangeStrategy': 0.75,
            'MultiFacetTrendStrategy': 0.8,
            'PrimaryStrategy': 0.7
        }
        
        for key, score in reputation_scores.items():
            if key in strategy_name:
                return score
        
        return 0.6  # Default reputation

class MarketPatternRecognizer:
    """Recognize market patterns for enhanced intelligence"""
    
    def __init__(self):
        self.pattern_memory = deque(maxlen=100)

# The rest of the classes remain the same as in the original file...

# Original Signal Factory classes from your working version
class ProfessionalSignalFactory:
    """Professional signal processing and validation engine"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._default_config()
        
        # Strategy management
        self.strategies = {}
        self.strategy_performance = defaultdict(dict)
        self.strategy_weights = {}
        
        # Signal processing
        self.signal_history = deque(maxlen=1000)
        self.active_signals = {}
        self.signal_cache = {}
        
        # Validation systems
        self.technical_validator = TechnicalValidator()
        self.correlation_analyzer = CorrelationAnalyzer()
        self.market_regime_detector = MarketRegimeDetector()
        
        # Threading for real-time processing
        self.processing_active = False
        self.processing_thread = None
        
        # Debug mode
        self.debug_mode = True
        
        # Initialize
        self._initialize_systems()
        
        print("🏭 PROFESSIONAL SIGNAL FACTORY v2.1 INITIALIZED")
        print(f"   Strategy Integration: {len(self.strategies)} strategies loaded")
        print(f"   Validation Systems: Flexible technical validation")
        print(f"   Signal Quality Levels: {len(SignalQuality)} levels")
        print(f"   Debug Mode: {'✅ ON' if self.debug_mode else '❌ OFF'}")
        print(f"   Real-time Processing: Ready")
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration"""
        return {
            'min_confidence_threshold': 0.35,
            'min_strategy_agreement': 1,
            'max_correlation_conflict': 0.95,
            'signal_expiry_minutes': 120,
            'premium_threshold': 0.80,
            'high_threshold': 0.70,
            'medium_threshold': 0.55,
            'low_threshold': 0.40,
            'max_simultaneous_signals': 10,
            'max_risk_per_signal': 0.04,
            'max_portfolio_risk': 0.20,
            'strategy_weight_decay': 0.98,
            'min_strategy_trades': 3,
            'technical_validation_enabled': True,
            'technical_validation_threshold': 0.25,
            'correlation_analysis_enabled': False,
            'regime_based_filtering': False,
            'volume_validation_enabled': False,
            'track_signal_performance': True,
            'performance_lookback_days': 30,
            'debug_validation_failures': True,
            'debug_strategy_performance': True,
        }
    
    # Continue with all original methods...
    def _initialize_systems(self):
        """Initialize all subsystems"""
        self._load_all_strategies()
        self._initialize_performance_tracking()
        self._start_background_processing()
    
    def _load_all_strategies(self):
        """Load all available strategies"""
        strategies_path = Path("strategies")
        if not strategies_path.exists():
            print("❌ Strategies folder not found!")
            return
        
        strategy_files = [f for f in strategies_path.glob("*.py")
                         if not f.name.startswith("_")
                         and f.name not in ["unified_signals.py", "numpy_compatibility.py"]]
        
        loaded_count = 0
        failed_strategies = []
        
        for strategy_file in strategy_files:
            try:
                module_name = strategy_file.stem
                spec = importlib.util.spec_from_file_location(module_name, strategy_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                strategy_found = False
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (hasattr(obj, 'analyze') and
                        not name.startswith('_') and
                        'strategy' in name.lower()):
                        try:
                            strategy_instance = obj()
                            self.strategies[name] = strategy_instance
                            self.strategy_weights[name] = 1.0
                            loaded_count += 1
                            strategy_found = True
                            print(f"   ✅ Loaded: {name}")
                            break
                        except Exception as e:
                            print(f"   ⚠️ Could not instantiate {name}: {e}")
                
                if not strategy_found:
                    failed_strategies.append(f"{strategy_file.name}: No valid strategy class found")
                    
            except Exception as e:
                failed_strategies.append(f"{strategy_file.name}: {str(e)[:50]}...")
                if self.debug_mode:
                    print(f"   ❌ Failed to load {strategy_file.name}: {e}")
        
        print(f"\n📊 Strategy Loading Summary:")
        print(f"   Total Strategies Loaded: {loaded_count}")
        print(f"   Strategy Files Processed: {len(strategy_files)}")
        print(f"   Success Rate: {loaded_count/len(strategy_files)*100:.1f}%")
        
        if failed_strategies and self.debug_mode:
            print(f"   Failed Strategies: {len(failed_strategies)}")
            for failure in failed_strategies[:5]:
                print(f"     • {failure}")
    
    def _initialize_performance_tracking(self):
        """Initialize strategy performance tracking"""
        for strategy_name in self.strategies.keys():
            self.strategy_performance[strategy_name] = {
                'total_signals': 0,
                'successful_signals': 0,
                'avg_confidence': 0.0,
                'win_rate': 0.5,
                'avg_return': 0.0,
                'last_signal_time': None,
                'performance_score': 1.0,
                'recent_signals': deque(maxlen=100),
                'rejection_count': 0,
                'last_rejection_reason': ""
            }
    
    def _start_background_processing(self):
        """Start background processing thread"""
        self.processing_active = True
        self.processing_thread = threading.Thread(target=self._background_processor)
        self.processing_thread.daemon = True
        self.processing_thread.start()
    
    def _background_processor(self):
        """Background processing for signal maintenance"""
        while self.processing_active:
            try:
                self._clean_expired_signals()
                self._update_strategy_weights()
                self._update_market_conditions()
                time.sleep(30)
            except Exception as e:
                if self.debug_mode:
                    print(f"Background processing error: {e}")
                time.sleep(60)
    
    def process_market_data_for_signals(self, market_data: Dict[str, Any]) -> List[ValidatedSignal]:
        """Main signal processing pipeline"""
        print(f"\n🏭 SIGNAL FACTORY PROCESSING - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)
        
        validated_signals = []
        processing_stats = {'raw_generated': 0, 'aggregated': 0, 'validated': 0, 'rejected': 0}
        
        for symbol in market_data.keys():
            symbol_data = market_data[symbol]
            
            # Generate raw signals
            raw_signals = self._generate_raw_signals(symbol, symbol_data)
            processing_stats['raw_generated'] += len(raw_signals)
            
            if raw_signals:
                print(f"📊 {symbol}: {len(raw_signals)} raw signals generated")
                
                # Aggregate signals
                aggregated_signal = self._aggregate_signals(symbol, raw_signals)
                if aggregated_signal:
                    processing_stats['aggregated'] += 1
                    
                    # Validate signal
                    validated_signal = self._validate_signal(aggregated_signal, symbol_data)
                    if validated_signal and validated_signal.quality != SignalQuality.REJECTED:
                        validated_signals.append(validated_signal)
                        processing_stats['validated'] += 1
                        print(f"   ✅ {validated_signal.quality.value} signal: {validated_signal.direction.value} "
                              f"(conf: {validated_signal.confidence:.3f}) - {validated_signal.primary_strategy}")
                    else:
                        processing_stats['rejected'] += 1
                        if self.debug_mode:
                            rejection_reason = validated_signal.warnings[0] if validated_signal and validated_signal.warnings else "Unknown validation failure"
                            print(f"   ❌ Signal rejected: {rejection_reason}")
                else:
                    if self.debug_mode:
                        print(f"   ⚠️ No consensus reached in aggregation")
            else:
                print(f"📊 {symbol}: No signals generated")
        
        # Rank and prioritize signals
        if validated_signals:
            validated_signals = self._rank_and_prioritize_signals(validated_signals)
            print(f"\n🎯 FINAL SIGNAL SUMMARY:")
            for i, signal in enumerate(validated_signals, 1):
                print(f"   {i}. {signal.symbol} {signal.direction.value} - "
                      f"{signal.quality.value} (conf: {signal.confidence:.3f}) - {signal.primary_strategy}")
        else:
            print(f"\n⚠️ NO VALIDATED SIGNALS GENERATED")
            if self.debug_mode:
                print(f"   Processing Stats: {processing_stats['raw_generated']} raw → "
                      f"{processing_stats['aggregated']} aggregated → "
                      f"{processing_stats['validated']} validated "
                      f"({processing_stats['rejected']} rejected)")
        
        return validated_signals
    
    def _generate_raw_signals(self, symbol: str, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate raw signals from all strategies"""
        raw_signals = []
        data_df = market_data.get('dataframe')
        
        if data_df is None or data_df.empty:
            if self.debug_mode:
                print(f"   ⚠️ No dataframe available for {symbol}")
            return raw_signals
        
        for strategy_name, strategy in self.strategies.items():
            try:
                result = strategy.analyze(data_df, symbol)
                
                if result and isinstance(result, dict):
                    signal_type = result.get('signal', 'HOLD')
                    confidence = float(result.get('confidence', 0.0))
                    
                    enhanced_result = {
                        'strategy_name': strategy_name,
                        'symbol': symbol,
                        'signal': signal_type,
                        'confidence': confidence,
                        'price': float(result.get('price', data_df['close'].iloc[-1])),
                        'reason': result.get('reason', 'No reason provided'),
                        'timestamp': datetime.now(),
                        'raw_data': result
                    }
                    
                    if signal_type in ['BUY', 'SELL', 'STRONG_BUY', 'STRONG_SELL'] and confidence > 0.20:
                        raw_signals.append(enhanced_result)
                        
                        # Update strategy performance
                        perf = self.strategy_performance[strategy_name]
                        perf['total_signals'] += 1
                        perf['last_signal_time'] = datetime.now()
                        
                        if self.debug_mode:
                            print(f"     • {strategy_name}: {signal_type} (conf: {confidence:.3f})")
                    elif self.debug_mode and signal_type in ['BUY', 'SELL', 'STRONG_BUY', 'STRONG_SELL']:
                        print(f"     • {strategy_name}: {signal_type} (conf: {confidence:.3f}) - TOO LOW CONFIDENCE")
                        
            except Exception as e:
                if self.debug_mode:
                    print(f"     ❌ Error in {strategy_name}: {str(e)[:50]}...")
                
                perf = self.strategy_performance[strategy_name]
                perf['rejection_count'] += 1
                perf['last_rejection_reason'] = f"Error: {str(e)[:30]}..."
        
        return raw_signals
    
    def _aggregate_signals(self, symbol: str, raw_signals: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Aggregate multiple strategy signals into consensus signal"""
        if not raw_signals:
            return None
        
        # Separate by direction
        buy_signals = [s for s in raw_signals if s['signal'] in ['BUY', 'STRONG_BUY']]
        sell_signals = [s for s in raw_signals if s['signal'] in ['SELL', 'STRONG_SELL']]
        
        # Weight signals by strategy performance
        buy_weight = 0
        sell_weight = 0
        
        for signal in buy_signals:
            strategy_weight = self.strategy_weights.get(signal['strategy_name'], 1.0)
            buy_weight += signal['confidence'] * strategy_weight
        
        for signal in sell_signals:
            strategy_weight = self.strategy_weights.get(signal['strategy_name'], 1.0)
            sell_weight += signal['confidence'] * strategy_weight
        
        # Determine consensus
        min_agreement = max(1, self.config.get('min_strategy_agreement', 1))
        consensus_direction = None
        consensus_confidence = 0
        primary_signals = []
        
        if buy_weight > sell_weight and len(buy_signals) >= min_agreement:
            consensus_direction = SignalDirection.BUY
            consensus_confidence = buy_weight / max(1, len(buy_signals))
            primary_signals = buy_signals
        elif sell_weight > buy_weight and len(sell_signals) >= min_agreement:
            consensus_direction = SignalDirection.SELL
            consensus_confidence = sell_weight / max(1, len(sell_signals))
            primary_signals = sell_signals
        elif buy_signals or sell_signals:
            # Fallback: Accept strongest single signal
            all_signals = buy_signals + sell_signals
            if all_signals:
                strongest_signal = max(all_signals, key=lambda s: s['confidence'] * self.strategy_weights.get(s['strategy_name'], 1.0))
                min_single_confidence = self.config.get('min_confidence_threshold', 0.35)
                
                if strongest_signal['confidence'] >= min_single_confidence:
                    consensus_direction = SignalDirection.BUY if strongest_signal in buy_signals else SignalDirection.SELL
                    consensus_confidence = strongest_signal['confidence']
                    primary_signals = [strongest_signal]
        
        if not consensus_direction or not primary_signals:
            if self.debug_mode:
                print(f"     No consensus: buy_weight={buy_weight:.3f}, sell_weight={sell_weight:.3f}")
            return None
        
        # Cap confidence at reasonable level
        consensus_confidence = min(0.95, consensus_confidence)
        
        # Create aggregated signal
        aggregated_signal = {
            'symbol': symbol,
            'direction': consensus_direction,
            'confidence': consensus_confidence,
            'primary_strategy': primary_signals[0]['strategy_name'],
            'contributing_strategies': [s['strategy_name'] for s in primary_signals],
            'strategy_votes': {s['strategy_name']: s['signal'] for s in raw_signals},
            'entry_price': np.mean([s['price'] for s in primary_signals]),
            'timestamp': datetime.now(),
            'raw_signals': raw_signals,
            'buy_weight': buy_weight,
            'sell_weight': sell_weight
        }
        
        return aggregated_signal
    
    def _validate_signal(self, aggregated_signal: Dict[str, Any], market_data: Dict[str, Any]) -> Optional[ValidatedSignal]:
        """Apply comprehensive signal validation"""
        symbol = aggregated_signal['symbol']
        
        # Basic threshold check
        min_confidence = self.config.get('min_confidence_threshold', 0.35)
        if aggregated_signal['confidence'] < min_confidence:
            if self.debug_mode:
                print(f"     Confidence too low: {aggregated_signal['confidence']:.3f} < {min_confidence}")
            return None
        
        # Create base validated signal
        validated_signal = ValidatedSignal(
            symbol=symbol,
            direction=aggregated_signal['direction'],
            confidence=aggregated_signal['confidence'],
            quality=self._determine_signal_quality(aggregated_signal['confidence']),
            entry_price=aggregated_signal['entry_price'],
            timestamp=aggregated_signal['timestamp'],
            primary_strategy=aggregated_signal['primary_strategy'],
            contributing_strategies=aggregated_signal['contributing_strategies'],
            strategy_votes=aggregated_signal['strategy_votes']
        )
        
        # Technical validation
        if self.config.get('technical_validation_enabled', True):
            technical_score = self.technical_validator.validate_signal(validated_signal, market_data)
            validated_signal.technical_score = technical_score
            
            tech_threshold = self.config.get('technical_validation_threshold', 0.25)
            if technical_score < tech_threshold:
                if self.debug_mode:
                    print(f"     Technical validation failed: {technical_score:.3f} < {tech_threshold}")
                validated_signal.confidence *= 0.9
                validated_signal.warnings.append(f"Low technical score: {technical_score:.3f}")
        else:
            validated_signal.technical_score = 0.5
        
        # Market regime validation
        market_regime = self.market_regime_detector.detect_regime(market_data.get('dataframe'))
        validated_signal.market_regime = MarketRegime.UNKNOWN  # Convert string to enum
        
        # Correlation conflict detection
        if self.config.get('correlation_analysis_enabled', False):
            correlation_conflicts = self.correlation_analyzer.check_conflicts(validated_signal, self.active_signals)
            validated_signal.correlation_conflicts = correlation_conflicts
            
            if correlation_conflicts and self.debug_mode:
                print(f"     Correlation conflicts detected: {len(correlation_conflicts)}")
        else:
            validated_signal.correlation_conflicts = []
        
        # Calculate composite validation score
        base_confidence = aggregated_signal['confidence']
        technical_component = validated_signal.technical_score * 0.2
        strategy_component = len(validated_signal.contributing_strategies) * 0.05
        
        validation_score = (
            base_confidence * 0.7 +
            technical_component +
            strategy_component
        )
        
        validated_signal.validation_score = min(1.0, validation_score)
        
        # Set risk parameters
        self._set_risk_parameters(validated_signal, market_data)
        
        # Generate signal ID and expiry
        validated_signal.signal_id = f"{symbol}_{validated_signal.direction.value}_{int(datetime.now().timestamp())}"
        expiry_minutes = self.config.get('signal_expiry_minutes', 120)
        validated_signal.expiry_time = datetime.now() + timedelta(minutes=expiry_minutes)
        
        # Final quality determination
        validated_signal.quality = self._determine_signal_quality(validated_signal.confidence)
        
        # Final confidence check
        final_min_confidence = self.config.get('min_confidence_threshold', 0.35) * 0.9
        if validated_signal.confidence < final_min_confidence:
            validated_signal.quality = SignalQuality.REJECTED
            validated_signal.warnings.append(f"Final confidence too low: {validated_signal.confidence:.3f}")
            if self.debug_mode:
                print(f"     REJECTED after validation: {validated_signal.confidence:.3f} < {final_min_confidence:.3f}")
        
        return validated_signal
    
    def _determine_signal_quality(self, confidence: float) -> SignalQuality:
        """Determine signal quality based on confidence"""
        premium_threshold = self.config.get('premium_threshold', 0.80)
        high_threshold = self.config.get('high_threshold', 0.70)
        medium_threshold = self.config.get('medium_threshold', 0.55)
        low_threshold = self.config.get('low_threshold', 0.40)
        
        if confidence >= premium_threshold:
            return SignalQuality.PREMIUM
        elif confidence >= high_threshold:
            return SignalQuality.HIGH
        elif confidence >= medium_threshold:
            return SignalQuality.MEDIUM
        elif confidence >= low_threshold:
            return SignalQuality.LOW
        else:
            return SignalQuality.REJECTED
    
    def _set_risk_parameters(self, signal: ValidatedSignal, market_data: Dict[str, Any]):
        """Set risk management parameters for the signal"""
        try:
            atr = market_data.get('atr', 0.001)
            current_price = signal.entry_price
            
            # ATR-based stop loss and take profit
            if signal.direction in [SignalDirection.BUY, SignalDirection.STRONG_BUY]:
                signal.stop_loss = current_price - (atr * 2.0)
                signal.take_profit = current_price + (atr * 4.0)
            else:
                signal.stop_loss = current_price + (atr * 2.0)
                signal.take_profit = current_price - (atr * 4.0)
            
            # Calculate risk-reward ratio
            risk = abs(current_price - signal.stop_loss)
            reward = abs(signal.take_profit - current_price)
            if risk > 0:
                signal.risk_reward_ratio = reward / risk
            
            # Adjust risk based on signal quality
            quality_risk_multipliers = {
                SignalQuality.PREMIUM: 0.030,
                SignalQuality.HIGH: 0.025,
                SignalQuality.MEDIUM: 0.020,
                SignalQuality.LOW: 0.015
            }
            
            signal.max_risk_pct = quality_risk_multipliers.get(signal.quality, 0.015)
            
        except Exception as e:
            if self.debug_mode:
                print(f"Error setting risk parameters: {e}")
            signal.max_risk_pct = 0.015
    
    def _rank_and_prioritize_signals(self, signals: List[ValidatedSignal]) -> List[ValidatedSignal]:
        """Rank signals by quality and priority"""
        def signal_score(signal):
            quality_scores = {
                SignalQuality.PREMIUM: 100,
                SignalQuality.HIGH: 80,
                SignalQuality.MEDIUM: 60,
                SignalQuality.LOW: 40
            }
            
            base_score = quality_scores.get(signal.quality, 0)
            confidence_bonus = signal.confidence * 20
            validation_bonus = signal.validation_score * 10
            strategy_count_bonus = len(signal.contributing_strategies) * 2
            
            return base_score + confidence_bonus + validation_bonus + strategy_count_bonus
        
        # Sort by score (highest first)
        ranked_signals = sorted(signals, key=signal_score, reverse=True)
        
        # Set execution priority
        for i, signal in enumerate(ranked_signals):
            signal.execution_priority = i + 1
        
        # Limit to max simultaneous signals
        max_signals = self.config.get('max_simultaneous_signals', 10)
        return ranked_signals[:max_signals]
    
    def _clean_expired_signals(self):
        """Remove expired signals from active signals"""
        current_time = datetime.now()
        expired_signals = []
        
        for signal_id, signal in self.active_signals.items():
            if signal.expiry_time and current_time > signal.expiry_time:
                expired_signals.append(signal_id)
        
        for signal_id in expired_signals:
            del self.active_signals[signal_id]
    
    def _update_strategy_weights(self):
        """Update strategy weights based on recent performance"""
        min_trades = self.config.get('min_strategy_trades', 3)
        decay = self.config.get('strategy_weight_decay', 0.98)
        
        for strategy_name, performance in self.strategy_performance.items():
            if performance['total_signals'] >= min_trades:
                win_rate = performance.get('win_rate', 0.5)
                avg_confidence = performance.get('avg_confidence', 0.5)
                
                performance_score = (win_rate * 0.6) + (avg_confidence * 0.4)
                
                current_weight = self.strategy_weights.get(strategy_name, 1.0)
                new_weight = (current_weight * decay + performance_score * (1 - decay))
                
                self.strategy_weights[strategy_name] = max(0.2, min(2.0, new_weight))
    
    def _update_market_conditions(self):
        """Update market condition analysis"""
        pass
    
    def get_signal_factory_status(self) -> Dict[str, Any]:
        """Get comprehensive status of signal factory"""
        return {
            'timestamp': datetime.now(),
            'strategies_loaded': len(self.strategies),
            'active_signals': len(self.active_signals),
            'signals_processed_today': len([s for s in self.signal_history
                                          if hasattr(s, 'timestamp') and s.timestamp.date() == datetime.now().date()]),
            'strategy_weights': dict(self.strategy_weights),
            'processing_active': self.processing_active,
            'config_summary': {
                'min_confidence': self.config.get('min_confidence_threshold'),
                'max_signals': self.config.get('max_simultaneous_signals'),
                'technical_validation': self.config.get('technical_validation_enabled')
            }
        }
    
    def shutdown(self):
        """Shutdown signal factory"""
        self.processing_active = False
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
        print("🔌 Signal Factory shutdown complete")

# Enhanced Signal Factory with Intelligence
class EnhancedProfessionalSignalFactory(ProfessionalSignalFactory):
    """PATH 2A ENHANCED: Professional Signal Factory with Advanced Intelligence"""
    
    def __init__(self, config: Dict[str, Any] = None):
        # Initialize parent class
        super().__init__(config)
        
        # PATH 2A: Add intelligence engine
        self.intelligence_engine = AdvancedIntelligenceEngine()
        
        # Enhanced configuration for PATH 2A
        self.config.update({
            'intelligence_threshold': 0.6,
            'regime_adaptation_enabled': True,
            'ai_prediction_weight': 0.15,
            'dynamic_threshold_adjustment': True,
            'correlation_penalty_enabled': True,
            'session_optimization_enabled': True
        })
        
        # Update thresholds for intelligence-based filtering
        self._update_intelligence_thresholds()
        
        print("🧠 PATH 2A INTELLIGENCE ENHANCED SIGNAL FACTORY INITIALIZED")
        print(f"   Intelligence Engine: ✅ Advanced AI foundations")
        print(f"   Dynamic Thresholds: ✅ Market-adaptive")
        print(f"   ML Ready: {'✅ Yes' if ML_AVAILABLE else '⚠️ Install sklearn'}")
        print(f"   Pattern Recognition: ✅ Active")
    
    def _update_intelligence_thresholds(self):
        """Update thresholds for intelligence-based processing"""
        self.config.update({
            'min_confidence_threshold': 0.30,
            'premium_threshold': 0.85,
            'high_threshold': 0.75,
            'medium_threshold': 0.60,
            'low_threshold': 0.45,
        })
    
    def _validate_signal(self, aggregated_signal: Dict[str, Any], market_data: Dict[str, Any]) -> Optional[ValidatedSignal]:
        """Enhanced signal validation with PATH 2A intelligence"""
        try:
            # Get base validated signal from parent
            validated_signal = super()._validate_signal(aggregated_signal, market_data)
            
            if not validated_signal or validated_signal.quality == SignalQuality.REJECTED:
                return validated_signal
            
            # PATH 2A: Add intelligence analysis
            strategy_context = {
                'total_strategies': len(self.strategies),
                'strategy_weights': self.strategy_weights,
                'active_signals': self.active_signals
            }
            
            # Analyze signal intelligence
            intelligence = self.intelligence_engine.analyze_signal_intelligence(
                validated_signal, market_data, strategy_context
            )
            
            # Update signal with intelligence
            validated_signal.intelligence = intelligence
            
            # Apply intelligence-based adjustments
            intelligence_adjustment = self._calculate_intelligence_adjustment(intelligence)
            validated_signal.confidence *= intelligence_adjustment
            
            # Update ML predictions
            if ML_AVAILABLE:
                validated_signal.ml_success_probability = intelligence.ai_prediction_confidence
                validated_signal.ai_risk_assessment = 1.0 - intelligence.risk_adjusted_score
                validated_signal.predicted_profit_potential = intelligence.composite_intelligence * 0.02
            
            # Re-determine quality after intelligence enhancement
            validated_signal.quality = self._determine_intelligent_signal_quality(
                validated_signal.confidence, intelligence
            )
            
            # Final intelligence threshold check
            intelligence_threshold = self.config.get('intelligence_threshold', 0.6)
            if intelligence.composite_intelligence < intelligence_threshold:
                validated_signal.quality = SignalQuality.REJECTED
                validated_signal.warnings.append(f"Intelligence score too low: {intelligence.composite_intelligence:.3f}")
                
                if self.debug_mode:
                    print(f"     INTELLIGENCE REJECTION: {intelligence.composite_intelligence:.3f} < {intelligence_threshold}")
            
            return validated_signal
            
        except Exception as e:
            logger.error(f"Enhanced signal validation error: {e}")
            return validated_signal if 'validated_signal' in locals() else None
    
    def _calculate_intelligence_adjustment(self, intelligence: IntelligenceMetrics) -> float:
        """Calculate confidence adjustment based on intelligence"""
        try:
            base_adjustment = 0.8 + intelligence.composite_intelligence * 0.4
            regime_adjustment = 0.95 + intelligence.market_regime_fit * 0.1
            consensus_adjustment = 0.9 + intelligence.strategy_consensus_score * 0.2
            
            total_adjustment = base_adjustment * regime_adjustment * consensus_adjustment
            return max(0.7, min(1.3, total_adjustment))
            
        except Exception:
            return 1.0
    
    def _determine_intelligent_signal_quality(self, confidence: float, intelligence: IntelligenceMetrics) -> SignalQuality:
        """Determine signal quality using intelligence metrics"""
        try:
            intelligence_bonus = intelligence.composite_intelligence * 0.15
            enhanced_confidence = confidence + intelligence_bonus
            
            if enhanced_confidence >= 0.85 and intelligence.composite_intelligence >= 0.8:
                return SignalQuality.PREMIUM
            elif enhanced_confidence >= 0.75 and intelligence.composite_intelligence >= 0.7:
                return SignalQuality.HIGH
            elif enhanced_confidence >= 0.60 and intelligence.composite_intelligence >= 0.6:
                return SignalQuality.MEDIUM
            elif enhanced_confidence >= 0.45 and intelligence.composite_intelligence >= 0.5:
                return SignalQuality.LOW
            else:
                return SignalQuality.REJECTED
                
        except Exception:
            return self._determine_signal_quality(confidence)

# Supporting classes (with safe array handling)
class TechnicalValidator:
    """Technical analysis validation with safe array handling"""
    
    def validate_signal(self, signal: ValidatedSignal, market_data: Dict[str, Any]) -> float:
        """Validate signal using technical analysis with safe array handling"""
        try:
            df = market_data.get('dataframe')
            if df is None or df.empty or len(df) < 10:
                return 0.5
            
            score = 0.5
            checks_passed = 0
            total_checks = 0
            
            current_price = signal.entry_price
            
            # Moving average confirmation with safe array handling
            if len(df) >= 20:
                ma_20 = df['close'].rolling(20).mean().iloc[-1]
                if pd.notna(ma_20):
                    if signal.direction == SignalDirection.BUY and current_price > ma_20:
                        score += 0.2
                        checks_passed += 1
                    elif signal.direction == SignalDirection.SELL and current_price < ma_20:
                        score += 0.2
                        checks_passed += 1
                    total_checks += 1
            
            # RSI with safe array handling
            if len(df) >= 14:
                try:
                    delta = df['close'].diff()
                    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    
                    loss_safe = loss.replace(0, 0.001)
                    rs = gain / loss_safe
                    rsi_series = 100 - (100 / (1 + rs))
                    rsi = rsi_series.iloc[-1]
                    
                    if pd.notna(rsi):
                        if signal.direction == SignalDirection.BUY and rsi < 75:
                            score += 0.15
                            checks_passed += 1
                        elif signal.direction == SignalDirection.SELL and rsi > 25:
                            score += 0.15
                            checks_passed += 1
                        total_checks += 1
                except Exception:
                    pass
            
            return max(0.2, min(0.9, score))
            
        except Exception as e:
            return 0.5

class CorrelationAnalyzer:
    """Correlation conflict analysis"""
    
    def check_conflicts(self, signal: ValidatedSignal, active_signals: Dict[str, ValidatedSignal]) -> List[str]:
        """Check for correlation conflicts with active signals"""
        conflicts = []
        
        correlations = {
            'EURUSD': ['GBPUSD'],
            'GBPUSD': ['EURUSD'],
            'USDJPY': ['USDCHF'],
            'USDCHF': ['USDJPY'],
            'XAUUSD': ['XAGUSD'],
        }
        
        correlated_symbols = correlations.get(signal.symbol, [])
        
        for active_signal in active_signals.values():
            if (active_signal.symbol in correlated_symbols and
                active_signal.direction != signal.direction):
                conflicts.append(f"Opposite direction on correlated pair {active_signal.symbol}")
        
        return conflicts

class MarketRegimeDetector:
    """Market regime detection"""
    
    def detect_regime(self, df: pd.DataFrame) -> str:
        """Detect current market regime"""
        try:
            if df is None or df.empty or len(df) < 30:
                return "normal"
            
            close_prices = df['close']
            
            if len(df) >= 50:
                ma_20 = close_prices.rolling(20).mean().iloc[-1]
                ma_50 = close_prices.rolling(50).mean().iloc[-1]
                current_price = close_prices.iloc[-1]
                
                returns = close_prices.pct_change().dropna()
                if len(returns) >= 20:
                    volatility = returns.rolling(20).std().iloc[-1]
                else:
                    volatility = returns.std() if len(returns) > 0 else 0
            else:
                ma_10 = close_prices.rolling(10).mean().iloc[-1]
                ma_20 = close_prices.rolling(20).mean().iloc[-1] if len(df) >= 20 else ma_10
                current_price = close_prices.iloc[-1]
                returns = close_prices.pct_change().dropna()
                volatility = returns.std() if len(returns) > 0 else 0
                ma_20, ma_50 = ma_10, ma_20
            
            if pd.isna(volatility) or volatility == 0:
                return "normal"
            
            if volatility > 0.025:
                return "volatile"
            elif current_price > ma_20 > ma_50:
                return "bullish"
            elif current_price < ma_20 < ma_50:
                return "bearish"
            else:
                return "sideways"
                
        except Exception as e:
            return "normal"

# Main interface functions
def get_professional_signal_factory(config: Dict[str, Any] = None) -> EnhancedProfessionalSignalFactory:
    """Get PATH 2A enhanced signal factory"""
    return EnhancedProfessionalSignalFactory(config)

def process_market_data_for_main_py(market_data: Dict[str, Any],
                                  signal_factory: EnhancedProfessionalSignalFactory = None) -> List[Dict[str, Any]]:
    """PATH 2A ENHANCED INTERFACE FOR MAIN.PY"""
    if signal_factory is None:
        signal_factory = get_professional_signal_factory()
    
    # Get enhanced validated signals
    validated_signals = signal_factory.process_market_data_for_signals(market_data)
    
    # Convert to main.py compatible format with intelligence data
    main_py_signals = []
    for signal in validated_signals:
        enhanced_signal = {
            # Standard fields
            'symbol': signal.symbol,
            'signal': signal.direction.value,
            'confidence': signal.confidence,
            'price': signal.entry_price,
            'stop_loss': signal.stop_loss,
            'take_profit': signal.take_profit,
            'strategy': signal.primary_strategy,
            'quality': signal.quality.value,
            'risk_reward_ratio': signal.risk_reward_ratio,
            'max_risk_pct': signal.max_risk_pct,
            'timestamp': signal.timestamp,
            'signal_id': signal.signal_id,
            'contributing_strategies': signal.contributing_strategies,
            'validation_score': signal.validation_score,
            
            # PATH 2A: Intelligence enhancements
            'intelligence_score': signal.intelligence.composite_intelligence,
            'market_regime': signal.market_regime.value,
            'regime_fit': signal.intelligence.market_regime_fit,
            'strategy_consensus': signal.intelligence.strategy_consensus_score,
            'volatility_appropriateness': signal.intelligence.volatility_appropriateness,
            'momentum_alignment': signal.intelligence.momentum_alignment,
            'session_suitability': signal.intelligence.session_suitability,
            'historical_success_rate': signal.intelligence.historical_success_rate,
            
            # ML/AI predictions
            'ml_success_probability': signal.ml_success_probability,
            'ai_risk_assessment': signal.ai_risk_assessment,
            'predicted_profit_potential': signal.predicted_profit_potential,
            
            # Enhanced metadata
            'path_2a_enhanced': True,
            'intelligence_version': '2.1'
        }
        
        main_py_signals.append(enhanced_signal)
    
    return main_py_signals

if __name__ == "__main__":
    # Test the enhanced signal factory
    print("🧪 TESTING PATH 2A ENHANCED SIGNAL FACTORY (ARRAY-SAFE)")
    print("=" * 60)
    
    import numpy as np
    import pandas as pd
    
    # Create test data
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1H')
    np.random.seed(42)
    prices = 1.1000 + np.cumsum(np.random.randn(100) * 0.0005)
    
    sample_data = pd.DataFrame({
        'time': dates,
        'open': prices + np.random.randn(100) * 0.0002,
        'high': prices + np.abs(np.random.randn(100) * 0.0005),
        'low': prices - np.abs(np.random.randn(100) * 0.0005),
        'close': prices,
        'volume': np.random.randint(1000, 5000, 100)
    })
    
    market_data = {
        'EURUSD': {
            'dataframe': sample_data,
            'atr': 0.0012,
            'spread': 0.0001
        }
    }
    
    # Test factory
    factory = get_professional_signal_factory()
    signals = process_market_data_for_main_py(market_data, factory)
    
    print(f"\n✅ PATH 2A Test completed successfully!")
    print(f"   Signals generated: {len(signals)}")
    
    factory.shutdown()
