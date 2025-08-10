"""
Enhanced Strategy Manager - ML-Enhanced Trading Strategy Orchestration
=====================================================================

Professional strategy orchestration system that coordinates multiple trading strategies,
integrates ML model predictions, manages signal confluence, and provides dynamic
strategy allocation for institutional algorithmic trading systems.

Features:
- Multi-strategy orchestration with dynamic weighting
- ML model integration with ensemble predictions
- Advanced signal confluence engine with scoring
- Real-time strategy performance monitoring
- Adaptive strategy allocation based on market conditions
- Professional risk integration and position sizing
- Comprehensive strategy analytics and reporting

Author: Enhanced Trading System
Version: 4.0 Professional
License: Proprietary
"""

import asyncio
import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable, Union
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np
import pandas as pd
from enum import Enum
import queue
import json
from abc import ABC, abstractmethod
from collections import defaultdict, deque
import weakref

# Core System Components
from core.data_manager import EnhancedDataManager
from core.risk_manager import EnhancedRiskManager  # Will implement next
from core.execution_engine import EnhancedExecutionEngine  # Will implement next

# ML Models Integration
from ml_models.ensemble_model import EnhancedEnsembleModel, EnsemblePrediction
from ml_models.lstm_model import InstitutionalLSTMModel, InstitutionalLSTMPrediction
from ml_models.random_forest_model import EnhancedRandomForestModel, RandomForestPrediction
from ml_models.svm_model import EnhancedSVMModel, SVMPrediction

# Configuration and Utilities
from utils.config import TradingConfig
from utils.logger import setup_logging
from utils.helpers import format_currency, calculate_pips

class StrategyState(Enum):
    """Strategy operational states"""
    INACTIVE = "inactive"
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    SUSPENDED = "suspended"

class SignalStrength(Enum):
    """Signal strength classification"""
    VERY_WEAK = 1
    WEAK = 2
    MODERATE = 3
    STRONG = 4
    VERY_STRONG = 5

class MarketCondition(Enum):
    """Market condition classification"""
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    RANGING = "ranging"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    BREAKOUT = "breakout"
    REVERSAL = "reversal"

@dataclass
class TradingSignal:
    """Comprehensive trading signal with metadata"""
    symbol: str
    action: str  # BUY, SELL, HOLD
    strength: SignalStrength
    confidence: float
    entry_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    position_size: Optional[float] = None
    
    # Strategy context
    strategy_name: str = ""
    strategy_version: str = ""
    timeframe: str = ""
    
    # ML context
    ml_confidence: Optional[float] = None
    ensemble_agreement: Optional[float] = None
    
    # Signal metadata
    signal_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    expiry: Optional[datetime] = None
    priority: int = 1
    
    # Risk parameters
    risk_reward_ratio: Optional[float] = None
    max_risk_per_trade: Optional[float] = None
    
    # Additional context
    market_condition: Optional[MarketCondition] = None
    confluence_score: float = 0.0
    supporting_indicators: List[str] = field(default_factory=list)
    conflicting_indicators: List[str] = field(default_factory=list)

@dataclass
class StrategyPerformance:
    """Strategy performance tracking"""
    strategy_name: str
    total_signals: int = 0
    successful_signals: int = 0
    failed_signals: int = 0
    total_pnl: float = 0.0
    win_rate: float = 0.0
    avg_return: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    last_signal_time: Optional[datetime] = None
    performance_score: float = 0.0
    
    # Recent performance (last N signals)
    recent_performance_window: int = 50
    recent_win_rate: float = 0.0
    recent_avg_return: float = 0.0
    
    # Market condition performance
    condition_performance: Dict[MarketCondition, Dict[str, float]] = field(default_factory=dict)

class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies
    
    This class defines the standard interface that all strategies must implement
    to ensure consistent interaction with the Strategy Manager.
    """
    
    def __init__(self, name: str, config: TradingConfig):
        self.name = name
        self.config = config
        self.state = StrategyState.INACTIVE
        self.performance = StrategyPerformance(strategy_name=name)
        self.logger = setup_logging('INFO')
        
        # Strategy parameters
        self.parameters = {}
        self.weight = 1.0
        self.enabled = True
        
        # Performance tracking
        self.signal_history = deque(maxlen=1000)
        self.last_update = None
        
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize strategy with required resources"""
        pass
    
    @abstractmethod
    async def generate_signals(self, data: Dict[str, pd.DataFrame], 
                             ml_predictions: Optional[Dict[str, Any]] = None) -> List[TradingSignal]:
        """Generate trading signals based on market data and ML predictions"""
        pass
    
    @abstractmethod
    def get_required_data(self) -> Dict[str, List[str]]:
        """Get required data specifications (symbols and timeframes)"""
        pass
    
    @abstractmethod
    def validate_signal(self, signal: TradingSignal) -> bool:
        """Validate signal before execution"""
        pass
    
    def update_performance(self, signal: TradingSignal, result: Dict[str, Any]):
        """Update strategy performance metrics"""
        self.performance.total_signals += 1
        
        if result.get('success', False):
            self.performance.successful_signals += 1
            pnl = result.get('pnl', 0.0)
            self.performance.total_pnl += pnl
        else:
            self.performance.failed_signals += 1
        
        # Update rates
        if self.performance.total_signals > 0:
            self.performance.win_rate = self.performance.successful_signals / self.performance.total_signals
            self.performance.avg_return = self.performance.total_pnl / self.performance.total_signals
        
        self.performance.last_signal_time = datetime.utcnow()
        
        # Store signal for history
        self.signal_history.append({
            'signal': signal,
            'result': result,
            'timestamp': datetime.utcnow()
        })
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        return {
            'name': self.name,
            'state': self.state.value,
            'performance': self.performance,
            'recent_signals': len(self.signal_history),
            'weight': self.weight,
            'enabled': self.enabled
        }

class ConfluenceEngine:
    """
    Advanced signal confluence engine for multi-strategy signal synthesis
    """
    
    def __init__(self, config: TradingConfig):
        self.config = config
        self.confluence_rules = config.confluence_engine_config.get('confluence_rules', {})
        self.min_confluence_score = config.confluence_engine_config.get('min_confluence_score', 5.0)
        self.max_confluence_score = config.confluence_engine_config.get('max_confluence_score', 20.0)
        self.logger = setup_logging('INFO')
        
        # Active confluences tracking
        self.active_confluences = {}  # symbol -> confluence data
        self.confluence_history = deque(maxlen=1000)
        
    def evaluate_confluence(self, signals: List[TradingSignal], 
                           market_data: Dict[str, pd.DataFrame],
                           ml_predictions: Optional[Dict[str, Any]] = None) -> Dict[str, TradingSignal]:
        """
        Evaluate signal confluence and generate high-conviction signals
        """
        try:
            confluence_signals = {}
            
            # Group signals by symbol
            symbol_signals = defaultdict(list)
            for signal in signals:
                symbol_signals[signal.symbol].append(signal)
            
            # Evaluate confluence for each symbol
            for symbol, symbol_signal_list in symbol_signals.items():
                confluence_signal = self._evaluate_symbol_confluence(
                    symbol, symbol_signal_list, market_data.get(symbol, {}), ml_predictions
                )
                
                if confluence_signal:
                    confluence_signals[symbol] = confluence_signal
                    
                    # Track confluence
                    self.confluence_history.append({
                        'symbol': symbol,
                        'confluence_score': confluence_signal.confluence_score,
                        'signal_count': len(symbol_signal_list),
                        'timestamp': datetime.utcnow()
                    })
            
            return confluence_signals
            
        except Exception as e:
            self.logger.error(f"Error evaluating confluence: {e}")
            return {}
    
    def _evaluate_symbol_confluence(self, symbol: str, signals: List[TradingSignal],
                                   symbol_data: Dict[str, pd.DataFrame],
                                   ml_predictions: Optional[Dict[str, Any]] = None) -> Optional[TradingSignal]:
        """Evaluate confluence for a specific symbol"""
        try:
            if len(signals) < 2:
                return None
            
            # Initialize confluence scoring
            confluence_score = 0.0
            bullish_signals = []
            bearish_signals = []
            supporting_indicators = []
            conflicting_indicators = []
            
            # Categorize signals
            for signal in signals:
                if signal.action == 'BUY':
                    bullish_signals.append(signal)
                elif signal.action == 'SELL':
                    bearish_signals.append(signal)
            
            # Must have agreement in direction
            if len(bullish_signals) > 0 and len(bearish_signals) > 0:
                # Conflicting signals - check if one side is significantly stronger
                bullish_strength = sum(s.strength.value * s.confidence for s in bullish_signals)
                bearish_strength = sum(s.strength.value * s.confidence for s in bearish_signals)
                
                strength_difference = abs(bullish_strength - bearish_strength)
                if strength_difference < 2.0:  # Too close to call
                    return None
            
            # Determine consensus direction
            if len(bullish_signals) > len(bearish_signals):
                consensus_action = 'BUY'
                primary_signals = bullish_signals
                opposing_signals = bearish_signals
            elif len(bearish_signals) > len(bullish_signals):
                consensus_action = 'SELL'
                primary_signals = bearish_signals
                opposing_signals = bullish_signals
            else:
                return None  # No clear consensus
            
            # Calculate base confluence score
            for signal in primary_signals:
                strategy_weight = self.confluence_rules.get(f"{signal.strategy_name}_signal", 1.0)
                confluence_score += strategy_weight * signal.strength.value * signal.confidence
                supporting_indicators.append(signal.strategy_name)
            
            # Penalty for opposing signals
            for signal in opposing_signals:
                strategy_penalty = self.confluence_rules.get(f"{signal.strategy_name}_opposing", -1.0)
                confluence_score += strategy_penalty
                conflicting_indicators.append(signal.strategy_name)
            
            # ML predictions bonus
            if ml_predictions:
                ml_score = self._evaluate_ml_confluence(symbol, consensus_action, ml_predictions)
                confluence_score += ml_score
                if ml_score > 0:
                    supporting_indicators.append("ML_Ensemble")
            
            # Market condition adjustments
            market_condition_adjustment = self._evaluate_market_conditions(symbol, symbol_data, consensus_action)
            confluence_score += market_condition_adjustment
            
            # Time decay (if enabled)
            if self.config.confluence_engine_config.get('time_decay_enabled', True):
                confluence_score *= self._apply_time_decay(signals)
            
            # Check minimum threshold
            if confluence_score < self.min_confluence_score:
                return None
            
            # Create confluence signal
            confluence_signal = self._create_confluence_signal(
                symbol, consensus_action, primary_signals, confluence_score,
                supporting_indicators, conflicting_indicators
            )
            
            return confluence_signal
            
        except Exception as e:
            self.logger.error(f"Error evaluating symbol confluence for {symbol}: {e}")
            return None
    
    def _evaluate_ml_confluence(self, symbol: str, action: str, ml_predictions: Dict[str, Any]) -> float:
        """Evaluate ML model confluence contribution"""
        try:
            ml_score = 0.0
            
            # Ensemble prediction
            if 'ensemble' in ml_predictions:
                ensemble_pred = ml_predictions['ensemble']
                if hasattr(ensemble_pred, 'final_prediction'):
                    # Convert ML prediction to trading action
                    ml_action = 'BUY' if ensemble_pred.final_prediction > 0.5 else 'SELL'
                    
                    if ml_action == action:
                        confidence_bonus = ensemble_pred.confidence * 2.0
                        agreement_bonus = ensemble_pred.model_agreement * 1.5
                        ml_score = confidence_bonus + agreement_bonus
                    else:
                        # ML disagrees - apply penalty
                        ml_score = -1.5
            
            # Individual model agreements
            for model_name in ['lstm', 'random_forest', 'svm']:
                if model_name in ml_predictions:
                    model_pred = ml_predictions[model_name]
                    model_score = self._evaluate_individual_ml_model(model_name, model_pred, action)
                    ml_score += model_score * 0.5  # Weight individual models less than ensemble
            
            return min(5.0, max(-3.0, ml_score))  # Cap ML contribution
            
        except Exception as e:
            self.logger.error(f"Error evaluating ML confluence: {e}")
            return 0.0
    
    def _evaluate_individual_ml_model(self, model_name: str, prediction: Any, action: str) -> float:
        """Evaluate individual ML model contribution"""
        try:
            if model_name == 'lstm':
                if hasattr(prediction, 'predictions') and hasattr(prediction, 'directional_probabilities'):
                    # Check directional probabilities
                    if action == 'BUY' and prediction.directional_probabilities.get('up', 0) > 0.6:
                        return prediction.directional_probabilities['up']
                    elif action == 'SELL' and prediction.directional_probabilities.get('down', 0) > 0.6:
                        return prediction.directional_probabilities['down']
            
            elif model_name == 'random_forest':
                if hasattr(prediction, 'signal') and hasattr(prediction, 'confidence'):
                    if (action == 'BUY' and prediction.signal >= 3) or (action == 'SELL' and prediction.signal <= 1):
                        return prediction.confidence
            
            elif model_name == 'svm':
                if hasattr(prediction, 'regime_name') and hasattr(prediction, 'confidence'):
                    # Bullish regimes support BUY, bearish regimes support SELL
                    if action == 'BUY' and 'trending_up' in prediction.regime_name.lower():
                        return prediction.confidence
                    elif action == 'SELL' and 'trending_down' in prediction.regime_name.lower():
                        return prediction.confidence
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error evaluating {model_name} model: {e}")
            return 0.0
    
    def _evaluate_market_conditions(self, symbol: str, symbol_data: Dict[str, pd.DataFrame], action: str) -> float:
        """Evaluate market condition impact on confluence"""
        try:
            adjustment = 0.0
            
            if not symbol_data:
                return adjustment
            
            # Get recent data for analysis
            recent_data = None
            for timeframe in ['M15', 'H1', 'H4']:
                if timeframe in symbol_data and len(symbol_data[timeframe]) > 50:
                    recent_data = symbol_data[timeframe].tail(50)
                    break
            
            if recent_data is None:
                return adjustment
            
            # Trend analysis
            sma_20 = recent_data['close'].rolling(20).mean()
            sma_50 = recent_data['close'].rolling(50).mean()
            
            if len(sma_20) > 0 and len(sma_50) > 0:
                current_price = recent_data['close'].iloc[-1]
                
                # Trend alignment bonus
                if action == 'BUY':
                    if current_price > sma_20.iloc[-1] > sma_50.iloc[-1]:
                        adjustment += self.confluence_rules.get('ma_trend_alignment', 2.0)
                    else:
                        adjustment += self.confluence_rules.get('against_daily_trend', -3.0)
                
                elif action == 'SELL':
                    if current_price < sma_20.iloc[-1] < sma_50.iloc[-1]:
                        adjustment += self.confluence_rules.get('ma_trend_alignment', 2.0)
                    else:
                        adjustment += self.confluence_rules.get('against_daily_trend', -3.0)
            
            # Volatility considerations
            returns = recent_data['close'].pct_change().dropna()
            if len(returns) > 10:
                volatility = returns.std()
                if volatility > 0.02:  # High volatility
                    adjustment += self.confluence_rules.get('high_spread_environment', -1.0)
            
            return adjustment
            
        except Exception as e:
            self.logger.error(f"Error evaluating market conditions: {e}")
            return 0.0
    
    def _apply_time_decay(self, signals: List[TradingSignal]) -> float:
        """Apply time decay to confluence score"""
        try:
            half_life_minutes = self.config.confluence_engine_config.get('time_decay_half_life', 30)
            current_time = datetime.utcnow()
            
            # Find oldest signal
            oldest_signal_time = min(signal.timestamp for signal in signals)
            time_elapsed = (current_time - oldest_signal_time).total_seconds() / 60  # minutes
            
            # Exponential decay
            decay_factor = 0.5 ** (time_elapsed / half_life_minutes)
            return max(0.1, decay_factor)  # Minimum 10% of original strength
            
        except Exception as e:
            self.logger.error(f"Error applying time decay: {e}")
            return 1.0
    
    def _create_confluence_signal(self, symbol: str, action: str, primary_signals: List[TradingSignal],
                                 confluence_score: float, supporting_indicators: List[str],
                                 conflicting_indicators: List[str]) -> TradingSignal:
        """Create a confluence signal from multiple signals"""
        try:
            # Calculate weighted averages
            total_weight = sum(s.confidence for s in primary_signals)
            
            if total_weight == 0:
                return None
            
            # Weighted average entry price
            weighted_entry = sum(s.entry_price * s.confidence for s in primary_signals) / total_weight
            
            # Weighted average stop loss
            weighted_stop = None
            stop_signals = [s for s in primary_signals if s.stop_loss is not None]
            if stop_signals:
                stop_weight = sum(s.confidence for s in stop_signals)
                weighted_stop = sum(s.stop_loss * s.confidence for s in stop_signals) / stop_weight
            
            # Weighted average take profit
            weighted_tp = None
            tp_signals = [s for s in primary_signals if s.take_profit is not None]
            if tp_signals:
                tp_weight = sum(s.confidence for s in tp_signals)
                weighted_tp = sum(s.take_profit * s.confidence for s in tp_signals) / tp_weight
            
            # Overall confidence
            avg_confidence = sum(s.confidence for s in primary_signals) / len(primary_signals)
            confluence_confidence = min(0.95, avg_confidence * (confluence_score / 10.0))
            
            # Signal strength
            if confluence_score >= 15.0:
                strength = SignalStrength.VERY_STRONG
            elif confluence_score >= 12.0:
                strength = SignalStrength.STRONG
            elif confluence_score >= 8.0:
                strength = SignalStrength.MODERATE
            elif confluence_score >= 5.0:
                strength = SignalStrength.WEAK
            else:
                strength = SignalStrength.VERY_WEAK
            
            # Create confluence signal
            confluence_signal = TradingSignal(
                symbol=symbol,
                action=action,
                strength=strength,
                confidence=confluence_confidence,
                entry_price=weighted_entry,
                stop_loss=weighted_stop,
                take_profit=weighted_tp,
                strategy_name="Confluence_Engine",
                strategy_version="4.0",
                timeframe="MULTI",
                signal_id=f"CONF_{symbol}_{int(time.time())}",
                timestamp=datetime.utcnow(),
                confluence_score=confluence_score,
                supporting_indicators=supporting_indicators,
                conflicting_indicators=conflicting_indicators
            )
            
            return confluence_signal
            
        except Exception as e:
            self.logger.error(f"Error creating confluence signal: {e}")
            return None

class StrategyAnalytics:
    """Advanced strategy analytics and performance monitoring"""
    
    def __init__(self):
        self.performance_history = defaultdict(list)
        self.signal_analytics = defaultdict(list)
        self.market_condition_performance = defaultdict(dict)
        self.logger = setup_logging('INFO')
        
    def update_strategy_performance(self, strategy_name: str, performance: StrategyPerformance):
        """Update strategy performance tracking"""
        self.performance_history[strategy_name].append({
            'timestamp': datetime.utcnow(),
            'performance': performance,
            'win_rate': performance.win_rate,
            'total_pnl': performance.total_pnl,
            'sharpe_ratio': performance.sharpe_ratio
        })
    
    def analyze_strategy_correlation(self, strategies: Dict[str, BaseStrategy]) -> Dict[str, Dict[str, float]]:
        """Analyze correlation between strategies"""
        try:
            correlation_matrix = {}
            
            for strategy1_name, strategy1 in strategies.items():
                correlation_matrix[strategy1_name] = {}
                
                for strategy2_name, strategy2 in strategies.items():
                    if strategy1_name == strategy2_name:
                        correlation_matrix[strategy1_name][strategy2_name] = 1.0
                    else:
                        correlation = self._calculate_strategy_correlation(strategy1, strategy2)
                        correlation_matrix[strategy1_name][strategy2_name] = correlation
            
            return correlation_matrix
            
        except Exception as e:
            self.logger.error(f"Error analyzing strategy correlation: {e}")
            return {}
    
    def _calculate_strategy_correlation(self, strategy1: BaseStrategy, strategy2: BaseStrategy) -> float:
        """Calculate correlation between two strategies"""
        try:
            # Get signal histories
            signals1 = list(strategy1.signal_history)
            signals2 = list(strategy2.signal_history)
            
            if len(signals1) < 10 or len(signals2) < 10:
                return 0.0
            
            # Align signals by time and calculate correlation
            # This is a simplified version - in production, you'd want more sophisticated alignment
            
            returns1 = [s['result'].get('pnl', 0.0) for s in signals1[-50:]]
            returns2 = [s['result'].get('pnl', 0.0) for s in signals2[-50:]]
            
            min_length = min(len(returns1), len(returns2))
            if min_length < 5:
                return 0.0
            
            returns1 = returns1[-min_length:]
            returns2 = returns2[-min_length:]
            
            correlation = np.corrcoef(returns1, returns2)[0, 1]
            return float(correlation) if not np.isnan(correlation) else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating strategy correlation: {e}")
            return 0.0
    
    def generate_strategy_report(self, strategies: Dict[str, BaseStrategy]) -> Dict[str, Any]:
        """Generate comprehensive strategy performance report"""
        try:
            report = {
                'report_time': datetime.utcnow(),
                'strategies': {},
                'overall_metrics': {},
                'correlations': self.analyze_strategy_correlation(strategies),
                'recommendations': []
            }
            
            total_signals = 0
            total_successful = 0
            total_pnl = 0.0
            
            # Individual strategy analysis
            for strategy_name, strategy in strategies.items():
                perf = strategy.performance
                
                strategy_report = {
                    'name': strategy_name,
                    'state': strategy.state.value,
                    'enabled': strategy.enabled,
                    'weight': strategy.weight,
                    'performance': {
                        'total_signals': perf.total_signals,
                        'win_rate': perf.win_rate,
                        'total_pnl': perf.total_pnl,
                        'avg_return': perf.avg_return,
                        'sharpe_ratio': perf.sharpe_ratio,
                        'max_drawdown': perf.max_drawdown
                    },
                    'recent_activity': len(strategy.signal_history),
                    'last_signal': perf.last_signal_time.isoformat() if perf.last_signal_time else None
                }
                
                report['strategies'][strategy_name] = strategy_report
                
                # Aggregate metrics
                total_signals += perf.total_signals
                total_successful += perf.successful_signals
                total_pnl += perf.total_pnl
            
            # Overall metrics
            if total_signals > 0:
                overall_win_rate = total_successful / total_signals
                overall_avg_return = total_pnl / total_signals
            else:
                overall_win_rate = 0.0
                overall_avg_return = 0.0
            
            report['overall_metrics'] = {
                'total_signals': total_signals,
                'overall_win_rate': overall_win_rate,
                'total_pnl': total_pnl,
                'overall_avg_return': overall_avg_return,
                'active_strategies': len([s for s in strategies.values() if s.state == StrategyState.ACTIVE]),
                'enabled_strategies': len([s for s in strategies.values() if s.enabled])
            }
            
            # Generate recommendations
            report['recommendations'] = self._generate_recommendations(strategies)
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating strategy report: {e}")
            return {'error': str(e)}
    
    def _generate_recommendations(self, strategies: Dict[str, BaseStrategy]) -> List[str]:
        """Generate strategy optimization recommendations"""
        recommendations = []
        
        try:
            for strategy_name, strategy in strategies.items():
                perf = strategy.performance
                
                # Performance-based recommendations
                if perf.total_signals > 50:
                    if perf.win_rate < 0.45:
                        recommendations.append(
                            f"Consider reviewing {strategy_name} - win rate below 45%"
                        )
                    
                    if perf.sharpe_ratio < 0.5:
                        recommendations.append(
                            f"Consider optimizing {strategy_name} - poor risk-adjusted returns"
                        )
                    
                    if perf.max_drawdown > 0.15:
                        recommendations.append(
                            f"Consider reducing exposure to {strategy_name} - high drawdown"
                        )
                
                # Activity-based recommendations
                if perf.last_signal_time:
                    time_since_signal = datetime.utcnow() - perf.last_signal_time
                    if time_since_signal > timedelta(hours=24):
                        recommendations.append(
                            f"{strategy_name} has been inactive for {time_since_signal.days} days"
                        )
            
            # Overall system recommendations
            active_count = len([s for s in strategies.values() if s.state == StrategyState.ACTIVE])
            if active_count < 2:
                recommendations.append("Consider activating more strategies for diversification")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return []

class EnhancedStrategyManager:
    """
    Enhanced Professional Strategy Manager for ML-Integrated Trading
    
    This class orchestrates multiple trading strategies, integrates ML model predictions,
    manages strategy performance, and provides advanced signal confluence analysis
    for institutional algorithmic trading systems.
    """
    
    def __init__(self, config: TradingConfig, data_manager: EnhancedDataManager,
                 risk_manager: 'EnhancedRiskManager', execution_engine: 'EnhancedExecutionEngine'):
        self.config = config
        self.data_manager = data_manager
        self.risk_manager = risk_manager
        self.execution_engine = execution_engine
        
        # Strategy management
        self.strategies = {}  # strategy_name -> BaseStrategy
        self.strategy_states = {}
        self.strategy_weights = {}
        
        # ML Models
        self.ensemble_model = None
        self.lstm_model = None
        self.rf_model = None
        self.svm_model = None
        
        # Signal processing
        self.confluence_engine = ConfluenceEngine(config)
        self.signal_queue = queue.Queue(maxsize=1000)
        self.processed_signals = deque(maxlen=5000)
        
        # Analytics and monitoring
        self.analytics = StrategyAnalytics()
        self.performance_tracker = {}
        
        # Threading and async
        self.signal_processing_task = None
        self.strategy_monitoring_task = None
        self.is_running = False
        self.shutdown_event = asyncio.Event()
        
        # Setup logging
        self.logger = setup_logging('INFO')
        self.logger.info("🎯 Enhanced Strategy Manager initialized")
    
    async def initialize(self) -> bool:
        """Initialize strategy manager with all components"""
        try:
            self.logger.info("🚀 Initializing Enhanced Strategy Manager...")
            
            # Initialize ML models (if available)
            await self._initialize_ml_models()
            
            # Initialize strategies
            if not await self._initialize_strategies():
                return False
            
            # Start background tasks
            await self._start_background_tasks()
            
            self.is_running = True
            self.logger.info("✅ Enhanced Strategy Manager initialization completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing strategy manager: {e}")
            return False
    
    async def _initialize_ml_models(self):
        """Initialize ML models for strategy enhancement"""
        try:
            if 'ensemble' in self.config.ml_models_enabled:
                # The ensemble model should already be initialized by the bot engine
                # We can access it through the bot engine reference or load it separately
                self.logger.info("   🧠 ML ensemble model integration ready")
            
            if 'lstm' in self.config.ml_models_enabled:
                self.logger.info("   🔮 LSTM model integration ready")
            
            if 'random_forest' in self.config.ml_models_enabled:
                self.logger.info("   🌳 Random Forest model integration ready")
            
            if 'svm' in self.config.ml_models_enabled:
                self.logger.info("   📈 SVM model integration ready")
                
        except Exception as e:
            self.logger.error(f"Error initializing ML models: {e}")
    
    async def _initialize_strategies(self) -> bool:
        """Initialize all enabled trading strategies"""
        try:
            self.logger.info("   📊 Initializing trading strategies...")
            
            # Get strategy weights from configuration
            self.strategy_weights = self.config.strategy_weights.copy()
            
            # Initialize enabled strategies
            for strategy_name in self.config.strategies_enabled:
                try:
                    strategy = await self._create_strategy(strategy_name)
                    if strategy and await strategy.initialize():
                        self.strategies[strategy_name] = strategy
                        self.strategy_states[strategy_name] = StrategyState.ACTIVE
                        self.logger.info(f"     ✅ {strategy_name} strategy initialized (weight: {self.strategy_weights.get(strategy_name, 1.0)})")
                    else:
                        self.logger.error(f"     ❌ Failed to initialize {strategy_name} strategy")
                        
                except Exception as e:
                    self.logger.error(f"Error initializing {strategy_name} strategy: {e}")
                    continue
            
            if not self.strategies:
                self.logger.error("No strategies were successfully initialized")
                return False
            
            self.logger.info(f"   ✅ {len(self.strategies)} strategies initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing strategies: {e}")
            return False
    
    async def _create_strategy(self, strategy_name: str) -> Optional[BaseStrategy]:
        """Factory method to create strategy instances"""
        try:
            # This is where we would import and instantiate specific strategy classes
            # For now, we'll create placeholder implementations
            
            if strategy_name == 'momentum':
                from strategies.momentum_strategy import MomentumStrategy
                return MomentumStrategy(strategy_name, self.config)
            
            elif strategy_name == 'mean_reversion':
                from strategies.mean_reversion_strategy import MeanReversionStrategy
                return MeanReversionStrategy(strategy_name, self.config)
            
            elif strategy_name == 'breakout':
                from strategies.breakout_strategy import BreakoutStrategy
                return BreakoutStrategy(strategy_name, self.config)
            
            elif strategy_name == 'indicator_suite':
                from strategies.indicator_suite_strategy import IndicatorSuiteStrategy
                return IndicatorSuiteStrategy(strategy_name, self.config)
            
            elif strategy_name == 'ict_strategy':
                from strategies.ict_strategy import ICTStrategy
                return ICTStrategy(strategy_name, self.config)
            
            elif strategy_name == 'rtm_strategy':
                from strategies.rtm_strategy import RTMStrategy
                return RTMStrategy(strategy_name, self.config)
            
            else:
                self.logger.warning(f"Unknown strategy type: {strategy_name}")
                return None
                
        except ImportError as e:
            self.logger.error(f"Could not import strategy {strategy_name}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error creating strategy {strategy_name}: {e}")
            return None
    
    async def _start_background_tasks(self):
        """Start background monitoring and processing tasks"""
        try:
            # Start signal processing task
            self.signal_processing_task = asyncio.create_task(self._signal_processing_loop())
            
            # Start strategy monitoring task
            self.strategy_monitoring_task = asyncio.create_task(self._strategy_monitoring_loop())
            
            self.logger.info("   🔄 Background tasks started")
            
        except Exception as e:
            self.logger.error(f"Error starting background tasks: {e}")
    
    async def generate_signals(self, symbol: str, data: Dict[str, pd.DataFrame], 
                             ml_predictions: Optional[Dict[str, Any]] = None) -> List[TradingSignal]:
        """
        Generate trading signals from all active strategies with ML integration
        """
        try:
            all_signals = []
            
            # Generate signals from each active strategy
            for strategy_name, strategy in self.strategies.items():
                if strategy.state != StrategyState.ACTIVE or not strategy.enabled:
                    continue
                
                try:
                    # Get strategy-specific data requirements
                    required_data = strategy.get_required_data()
                    strategy_data = {}
                    
                    # Filter data based on strategy requirements
                    if symbol in required_data:
                        for timeframe in required_data[symbol]:
                            if timeframe in data:
                                strategy_data[timeframe] = data[timeframe]
                    
                    if not strategy_data:
                        continue
                    
                    # Generate signals from strategy
                    strategy_signals = await strategy.generate_signals(
                        {symbol: strategy_data}, ml_predictions
                    )
                    
                    # Apply strategy weight and validate signals
                    for signal in strategy_signals:
                        if strategy.validate_signal(signal):
                            # Apply strategy weight to confidence
                            strategy_weight = self.strategy_weights.get(strategy_name, 1.0)
                            signal.confidence *= strategy_weight
                            signal.strategy_name = strategy_name
                            
                            all_signals.append(signal)
                            
                except Exception as e:
                    self.logger.error(f"Error generating signals from {strategy_name}: {e}")
                    continue
            
            # Process signals through confluence engine
            if len(all_signals) > 1:
                confluence_signals = self.confluence_engine.evaluate_confluence(
                    all_signals, {symbol: data}, ml_predictions
                )
                
                if symbol in confluence_signals:
                    # Return confluence signal if it meets threshold
                    return [confluence_signals[symbol]]
            
            # Return individual signals if no confluence or below threshold
            return all_signals
            
        except Exception as e:
            self.logger.error(f"Error generating signals for {symbol}: {e}")
            return []
    
    async def _signal_processing_loop(self):
        """Background signal processing and validation loop"""
        while self.is_running and not self.shutdown_event.is_set():
            try:
                # Process queued signals
                processed_count = 0
                
                while not self.signal_queue.empty() and processed_count < 10:
                    try:
                        signal_data = self.signal_queue.get_nowait()
                        await self._process_queued_signal(signal_data)
                        processed_count += 1
                    except queue.Empty:
                        break
                    except Exception as e:
                        self.logger.error(f"Error processing queued signal: {e}")
                
                await asyncio.sleep(1)  # Process every second
                
            except Exception as e:
                self.logger.error(f"Error in signal processing loop: {e}")
                await asyncio.sleep(5)
    
    async def _process_queued_signal(self, signal_data: Dict[str, Any]):
        """Process a queued signal"""
        try:
            # This would handle post-processing of signals
            # Update performance tracking, analytics, etc.
            pass
            
        except Exception as e:
            self.logger.error(f"Error processing queued signal: {e}")
    
    async def _strategy_monitoring_loop(self):
        """Background strategy performance monitoring loop"""
        while self.is_running and not self.shutdown_event.is_set():
            try:
                # Update strategy analytics
                for strategy_name, strategy in self.strategies.items():
                    self.analytics.update_strategy_performance(strategy_name, strategy.performance)
                
                # Check for strategy state changes
                await self._check_strategy_health()
                
                # Adaptive weight adjustment based on performance
                await self._adjust_strategy_weights()
                
                await asyncio.sleep(300)  # Monitor every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in strategy monitoring loop: {e}")
                await asyncio.sleep(60)
    
    async def _check_strategy_health(self):
        """Check strategy health and adjust states if necessary"""
        try:
            for strategy_name, strategy in self.strategies.items():
                perf = strategy.performance
                
                # Check for poor performance
                if perf.total_signals > 20:
                    if perf.win_rate < 0.3:
                        self.logger.warning(f"Strategy {strategy_name} has low win rate: {perf.win_rate:.1%}")
                        # Could automatically pause strategy
                        
                    if perf.max_drawdown > 0.2:
                        self.logger.warning(f"Strategy {strategy_name} has high drawdown: {perf.max_drawdown:.1%}")
                
                # Check for inactivity
                if perf.last_signal_time:
                    time_since_signal = datetime.utcnow() - perf.last_signal_time
                    if time_since_signal > timedelta(hours=48):
                        self.logger.info(f"Strategy {strategy_name} has been inactive for {time_since_signal}")
            
        except Exception as e:
            self.logger.error(f"Error checking strategy health: {e}")
    
    async def _adjust_strategy_weights(self):
        """Dynamically adjust strategy weights based on performance"""
        try:
            if not self.config.get('enable_adaptive_weights', True):
                return
            
            # Calculate performance scores
            performance_scores = {}
            for strategy_name, strategy in self.strategies.items():
                perf = strategy.performance
                
                if perf.total_signals < 10:
                    performance_scores[strategy_name] = 1.0  # Default weight
                    continue
                
                # Calculate composite performance score
                win_rate_score = perf.win_rate
                return_score = max(0, min(2, perf.avg_return / 0.01))  # Normalize to 0-2
                sharpe_score = max(0, min(2, perf.sharpe_ratio / 1.0))  # Normalize to 0-2
                
                composite_score = (win_rate_score + return_score + sharpe_score) / 3
                performance_scores[strategy_name] = composite_score
            
            # Adjust weights based on performance
            total_score = sum(performance_scores.values())
            if total_score > 0:
                for strategy_name, score in performance_scores.items():
                    new_weight = score / total_score * len(performance_scores)  # Normalize
                    new_weight = max(0.1, min(3.0, new_weight))  # Bound between 0.1 and 3.0
                    
                    if abs(new_weight - self.strategy_weights.get(strategy_name, 1.0)) > 0.1:
                        self.logger.info(f"Adjusting {strategy_name} weight: {self.strategy_weights.get(strategy_name, 1.0):.2f} -> {new_weight:.2f}")
                        self.strategy_weights[strategy_name] = new_weight
                        self.strategies[strategy_name].weight = new_weight
            
        except Exception as e:
            self.logger.error(f"Error adjusting strategy weights: {e}")
    
    def update_strategy_performance(self, strategy_name: str, signal: TradingSignal, result: Dict[str, Any]):
        """Update strategy performance after trade execution"""
        try:
            if strategy_name in self.strategies:
                self.strategies[strategy_name].update_performance(signal, result)
                
                # Store processed signal
                self.processed_signals.append({
                    'strategy': strategy_name,
                    'signal': signal,
                    'result': result,
                    'timestamp': datetime.utcnow()
                })
            
        except Exception as e:
            self.logger.error(f"Error updating strategy performance: {e}")
    
    async def validate_strategies(self) -> bool:
        """Validate all strategies are ready for trading"""
        try:
            if not self.strategies:
                return False
            
            valid_strategies = 0
            for strategy_name, strategy in self.strategies.items():
                if strategy.state == StrategyState.ACTIVE and strategy.enabled:
                    valid_strategies += 1
            
            return valid_strategies > 0
            
        except Exception as e:
            self.logger.error(f"Error validating strategies: {e}")
            return False
    
    def get_strategy_status(self) -> Dict[str, Any]:
        """Get comprehensive strategy status"""
        try:
            status = {
                'total_strategies': len(self.strategies),
                'active_strategies': len([s for s in self.strategies.values() if s.state == StrategyState.ACTIVE]),
                'enabled_strategies': len([s for s in self.strategies.values() if s.enabled]),
                'strategies': {},
                'performance_summary': {}
            }
            
            # Individual strategy status
            for strategy_name, strategy in self.strategies.items():
                status['strategies'][strategy_name] = strategy.get_performance_summary()
            
            # Generate analytics report
            status['analytics_report'] = self.analytics.generate_strategy_report(self.strategies)
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting strategy status: {e}")
            return {'error': str(e)}
    
    async def shutdown(self):
        """Graceful shutdown of strategy manager"""
        try:
            self.logger.info("🛑 Shutting down Enhanced Strategy Manager...")
            
            self.is_running = False
            self.shutdown_event.set()
            
            # Cancel background tasks
            if self.signal_processing_task and not self.signal_processing_task.done():
                self.signal_processing_task.cancel()
            
            if self.strategy_monitoring_task and not self.strategy_monitoring_task.done():
                self.strategy_monitoring_task.cancel()
            
            # Shutdown individual strategies
            for strategy_name, strategy in self.strategies.items():
                try:
                    if hasattr(strategy, 'shutdown'):
                        await strategy.shutdown()
                except Exception as e:
                    self.logger.error(f"Error shutting down {strategy_name}: {e}")
            
            self.logger.info("✅ Enhanced Strategy Manager shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error shutting down strategy manager: {e}")

# Factory function for creating strategy manager
def create_strategy_manager(config: TradingConfig, data_manager: EnhancedDataManager,
                           risk_manager: 'EnhancedRiskManager', 
                           execution_engine: 'EnhancedExecutionEngine') -> EnhancedStrategyManager:
    """Factory function to create strategy manager instance"""
    return EnhancedStrategyManager(config, data_manager, risk_manager, execution_engine)
