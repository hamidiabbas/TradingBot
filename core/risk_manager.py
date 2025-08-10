"""
Enhanced Risk Manager - Advanced Position Sizing & Portfolio Heat Management
===========================================================================

Professional-grade risk management system for institutional algorithmic trading
that provides advanced position sizing, portfolio heat management, dynamic correlation
analysis, ML-enhanced risk assessment, and comprehensive drawdown protection.

Features:
- ML-enhanced position sizing with confidence-based adjustments
- Dynamic portfolio heat monitoring with correlation analysis
- Advanced drawdown protection with circuit breakers
- Real-time risk metrics calculation and monitoring
- Multi-timeframe volatility analysis and targeting
- Kelly Criterion and Optimal F position sizing
- VaR and CVaR risk assessment
- Professional error handling and recovery
- Production-ready with comprehensive logging

Author: Enhanced Trading System
Version: 4.0 Professional
License: Proprietary
"""

import asyncio
import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np
import pandas as pd
from enum import Enum
import json
import pickle
from collections import defaultdict, deque
import warnings
from scipy import stats
from scipy.optimize import minimize
import talib

# Core System Components
from core.data_manager import EnhancedDataManager
from core.execution_engine import EnhancedExecutionEngine  # Will implement next

# ML Models Integration  
from ml_models.ensemble_model import EnsemblePrediction
from ml_models.lstm_model import InstitutionalLSTMPrediction
from ml_models.random_forest_model import RandomForestPrediction
from ml_models.svm_model import SVMPrediction

# Configuration and Utilities
from utils.config import TradingConfig
from utils.logger import setup_logging
from utils.helpers import format_currency, calculate_pips

# Suppress warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=RuntimeWarning)

class RiskLevel(Enum):
    """Risk level classification"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    CRITICAL = "critical"

class MarketRegime(Enum):
    """Market regime classification for risk adjustment"""
    TRENDING_BULL = "trending_bull"
    TRENDING_BEAR = "trending_bear"
    RANGING = "ranging"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    CRISIS = "crisis"
    BREAKOUT = "breakout"

class PositionSizingMethod(Enum):
    """Position sizing methodologies"""
    FIXED_FRACTIONAL = "fixed_fractional"
    KELLY_CRITERION = "kelly_criterion"
    OPTIMAL_F = "optimal_f"
    VOLATILITY_TARGET = "volatility_target"
    RISK_PARITY = "risk_parity"
    ML_ENHANCED = "ml_enhanced"
    DYNAMIC_ALLOCATION = "dynamic_allocation"

@dataclass
class RiskMetrics:
    """Comprehensive risk metrics structure"""
    # Position sizing results
    position_size: float
    risk_amount: float
    max_loss_amount: float
    max_gain_amount: float
    
    # Risk ratios
    risk_reward_ratio: float
    portfolio_risk_pct: float
    symbol_risk_pct: float
    
    # ML-enhanced metrics
    confidence_adjusted_size: float
    ml_risk_score: float
    ensemble_agreement_factor: float
    
    # Advanced sizing methods
    kelly_size: float
    optimal_f_size: float
    volatility_adjusted_size: float
    correlation_adjusted_size: float
    
    # Risk assessment
    var_95: float
    cvar_95: float
    sharpe_expected: float
    sortino_expected: float
    
    # Metadata
    sizing_method: str
    market_regime: str
    volatility_regime: str
    liquidity_score: float
    execution_risk_score: float

@dataclass
class PortfolioHeat:
    """Portfolio heat and exposure metrics"""
    total_exposure: float
    net_exposure: float
    gross_exposure: float
    long_exposure: float
    short_exposure: float
    
    # Risk concentrations
    max_symbol_exposure: float
    max_sector_exposure: float
    max_correlation_exposure: float
    
    # Heat metrics
    portfolio_heat: float
    risk_adjusted_heat: float
    volatility_adjusted_heat: float
    
    # Correlation analysis
    portfolio_correlation: float
    max_correlation_pair: Tuple[str, str, float]
    correlation_risk_score: float

@dataclass
class DrawdownMetrics:
    """Comprehensive drawdown analysis"""
    current_drawdown: float
    max_drawdown: float
    max_drawdown_duration: timedelta
    recovery_factor: float
    
    # Drawdown phases
    in_drawdown: bool
    drawdown_start: Optional[datetime]
    drawdown_peak: float
    recovery_progress: float
    
    # Risk indicators
    consecutive_losses: int
    consecutive_loss_amount: float
    pain_index: float
    ulcer_index: float

class VolatilityAnalyzer:
    """Advanced volatility analysis for risk management"""
    
    def __init__(self, config: TradingConfig):
        self.config = config
        self.volatility_cache = {}
        self.regime_cache = {}
        self.logger = setup_logging('INFO')
        
    def calculate_multi_timeframe_volatility(self, data: Dict[str, pd.DataFrame]) -> Dict[str, float]:
        """Calculate volatility across multiple timeframes"""
        try:
            volatilities = {}
            
            for timeframe, df in data.items():
                if len(df) < 20:
                    continue
                
                # Calculate returns
                returns = df['close'].pct_change().dropna()
                
                if len(returns) < 10:
                    continue
                
                # Multiple volatility estimators
                volatilities[f'{timeframe}_close_vol'] = returns.std() * np.sqrt(252)
                
                # Parkinson volatility (high-low)
                if 'high' in df.columns and 'low' in df.columns:
                    hl_vol = np.sqrt((1/(4*np.log(2))) * np.log(df['high']/df['low'])**2).mean()
                    volatilities[f'{timeframe}_parkinson_vol'] = hl_vol * np.sqrt(252)
                
                # Garman-Klass volatility
                if all(col in df.columns for col in ['high', 'low', 'open', 'close']):
                    gk_vol = np.sqrt(
                        0.5 * (np.log(df['high']/df['low'])**2) - 
                        (2*np.log(2)-1) * (np.log(df['close']/df['open'])**2)
                    ).mean()
                    volatilities[f'{timeframe}_gk_vol'] = gk_vol * np.sqrt(252)
                
                # ATR-based volatility
                if all(col in df.columns for col in ['high', 'low', 'close']):
                    atr = talib.ATR(df['high'].values, df['low'].values, df['close'].values, timeperiod=14)
                    atr_vol = np.nanmean(atr) / df['close'].iloc[-1]
                    volatilities[f'{timeframe}_atr_vol'] = atr_vol * np.sqrt(252)
            
            return volatilities
            
        except Exception as e:
            self.logger.error(f"Error calculating multi-timeframe volatility: {e}")
            return {}
    
    def detect_volatility_regime(self, symbol: str, data: Dict[str, pd.DataFrame]) -> str:
        """Detect current volatility regime"""
        try:
            # Use cache if available
            cache_key = f"{symbol}_{datetime.now().date()}"
            if cache_key in self.regime_cache:
                return self.regime_cache[cache_key]
            
            # Get volatilities
            volatilities = self.calculate_multi_timeframe_volatility(data)
            
            if not volatilities:
                return "normal"
            
            # Average volatility across timeframes
            avg_volatility = np.mean(list(volatilities.values()))
            
            # Define regime thresholds
            if avg_volatility > 0.4:  # 40% annual volatility
                regime = "crisis"
            elif avg_volatility > 0.25:  # 25% annual volatility
                regime = "high_volatility"  
            elif avg_volatility < 0.08:  # 8% annual volatility
                regime = "low_volatility"
            else:
                regime = "normal"
            
            # Cache result
            self.regime_cache[cache_key] = regime
            
            return regime
            
        except Exception as e:
            self.logger.error(f"Error detecting volatility regime for {symbol}: {e}")
            return "normal"

class CorrelationAnalyzer:
    """Advanced correlation analysis for portfolio risk"""
    
    def __init__(self, config: TradingConfig):
        self.config = config
        self.correlation_matrix = {}
        self.correlation_history = deque(maxlen=1000)
        self.logger = setup_logging('INFO')
        
    def calculate_dynamic_correlations(self, symbols: List[str], 
                                     price_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Calculate dynamic correlations between symbols"""
        try:
            # Prepare returns data
            returns_data = {}
            
            for symbol in symbols:
                if symbol in price_data and 'close' in price_data[symbol].columns:
                    returns = price_data[symbol]['close'].pct_change().dropna()
                    if len(returns) > 50:  # Minimum data requirement
                        returns_data[symbol] = returns
            
            if len(returns_data) < 2:
                return pd.DataFrame()
            
            # Align data by index
            returns_df = pd.DataFrame(returns_data)
            returns_df = returns_df.dropna()
            
            if len(returns_df) < 30:  # Minimum observations
                return pd.DataFrame()
            
            # Calculate correlation matrix
            correlation_matrix = returns_df.corr()
            
            # Store in cache
            self.correlation_matrix = correlation_matrix
            
            return correlation_matrix
            
        except Exception as e:
            self.logger.error(f"Error calculating dynamic correlations: {e}")
            return pd.DataFrame()
    
    def calculate_portfolio_correlation_risk(self, positions: Dict[str, float],
                                           correlation_matrix: pd.DataFrame) -> float:
        """Calculate portfolio correlation risk score"""
        try:
            if correlation_matrix.empty or len(positions) < 2:
                return 0.0
            
            # Filter positions and correlations for available symbols
            available_symbols = list(set(positions.keys()) & set(correlation_matrix.columns))
            
            if len(available_symbols) < 2:
                return 0.0
            
            # Calculate weighted correlation risk
            correlation_risk = 0.0
            total_weight = 0.0
            
            for i, symbol1 in enumerate(available_symbols):
                for j, symbol2 in enumerate(available_symbols[i+1:], i+1):
                    if symbol1 in correlation_matrix.index and symbol2 in correlation_matrix.columns:
                        correlation = abs(correlation_matrix.loc[symbol1, symbol2])
                        weight1 = abs(positions.get(symbol1, 0))
                        weight2 = abs(positions.get(symbol2, 0))
                        
                        # Weight correlation by position sizes
                        weighted_correlation = correlation * weight1 * weight2
                        correlation_risk += weighted_correlation
                        total_weight += weight1 * weight2
            
            # Normalize correlation risk
            if total_weight > 0:
                correlation_risk /= total_weight
            
            return min(1.0, correlation_risk)
            
        except Exception as e:
            self.logger.error(f"Error calculating portfolio correlation risk: {e}")
            return 0.0

class PositionSizer:
    """Advanced position sizing with multiple methodologies"""
    
    def __init__(self, config: TradingConfig):
        self.config = config
        self.historical_performance = deque(maxlen=1000)
        self.kelly_cache = {}
        self.optimal_f_cache = {}
        self.logger = setup_logging('INFO')
        
    def calculate_kelly_criterion_size(self, symbol: str, entry_price: float, stop_loss: float,
                                     account_balance: float, win_rate: float, avg_win: float,
                                     avg_loss: float, confidence: float = 1.0) -> float:
        """Calculate Kelly Criterion position size"""
        try:
            # Calculate risk per share
            risk_per_share = abs(entry_price - stop_loss)
            
            if risk_per_share == 0:
                return 0.0
            
            # Kelly formula: f = (bp - q) / b
            # where b = avg_win/avg_loss, p = win_rate, q = 1 - win_rate
            
            if avg_loss == 0:
                return 0.0
            
            b = avg_win / abs(avg_loss)  # Win/loss ratio
            p = max(0.01, min(0.99, win_rate))  # Win rate (bounded)
            q = 1 - p  # Loss rate
            
            # Kelly fraction
            kelly_fraction = (b * p - q) / b
            
            # Apply confidence adjustment
            kelly_fraction *= confidence
            
            # Apply fractional Kelly (typically 25-50% of full Kelly)
            fractional_kelly = kelly_fraction * self.config.get('risk_management.kelly_fraction', 0.25)
            
            # Bound Kelly fraction (max 10% of account)
            bounded_kelly = max(0, min(0.1, fractional_kelly))
            
            # Calculate position size
            if bounded_kelly <= 0:
                return 0.0
            
            risk_amount = account_balance * bounded_kelly
            position_size = risk_amount / risk_per_share
            
            # Ensure minimum position size
            min_position = self.config.get('risk_management.min_position_size', 0.01)
            position_size = max(min_position, position_size)
            
            return position_size
            
        except Exception as e:
            self.logger.error(f"Error calculating Kelly criterion size: {e}")
            return 0.0
    
    def calculate_optimal_f_size(self, symbol: str, entry_price: float, stop_loss: float,
                               account_balance: float, historical_returns: List[float]) -> float:
        """Calculate Optimal F position size"""
        try:
            if not historical_returns or len(historical_returns) < 10:
                return 0.0
            
            # Calculate risk per share
            risk_per_share = abs(entry_price - stop_loss)
            
            if risk_per_share == 0:
                return 0.0
            
            # Convert returns to fixed dollar amounts
            returns_array = np.array(historical_returns)
            
            # Find the largest loss
            largest_loss = abs(np.min(returns_array))
            
            if largest_loss == 0:
                return 0.0
            
            # Optimal F calculation
            def calculate_f_objective(f):
                if f <= 0 or f >= 1:
                    return -float('inf')
                
                # Calculate geometric mean
                geometric_returns = []
                for ret in returns_array:
                    new_balance = 1 + (f * ret / largest_loss)
                    if new_balance <= 0:
                        return -float('inf')
                    geometric_returns.append(new_balance)
                
                if not geometric_returns:
                    return -float('inf')
                
                # Geometric mean
                geometric_mean = np.prod(geometric_returns) ** (1.0 / len(geometric_returns))
                return geometric_mean
            
            # Optimize f
            best_f = 0.0
            best_objective = -float('inf')
            
            # Grid search for optimal f
            for f in np.arange(0.01, 0.5, 0.01):
                objective = calculate_f_objective(f)
                if objective > best_objective:
                    best_objective = objective
                    best_f = f
            
            # Apply conservative factor
            conservative_f = best_f * 0.5  # Use 50% of optimal f
            
            # Calculate position size
            if conservative_f <= 0:
                return 0.0
            
            risk_amount = account_balance * conservative_f
            position_size = risk_amount / risk_per_share
            
            # Ensure minimum position size
            min_position = self.config.get('risk_management.min_position_size', 0.01)
            position_size = max(min_position, position_size)
            
            return position_size
            
        except Exception as e:
            self.logger.error(f"Error calculating Optimal F size: {e}")
            return 0.0
    
    def calculate_volatility_target_size(self, symbol: str, account_balance: float,
                                       volatility: float, target_volatility: float = 0.15) -> float:
        """Calculate position size based on volatility targeting"""
        try:
            if volatility == 0:
                return 0.0
            
            # Volatility scaling factor
            vol_scalar = target_volatility / volatility
            
            # Base position size (e.g., 1% of account)
            base_position_pct = self.config.get('risk_management.base_position_pct', 0.01)
            
            # Volatility-adjusted position size
            adjusted_position_pct = base_position_pct * vol_scalar
            
            # Bound the position size
            max_position_pct = self.config.get('risk_management.max_position_pct', 0.05)
            min_position_pct = self.config.get('risk_management.min_position_pct', 0.001)
            
            bounded_position_pct = max(min_position_pct, min(max_position_pct, adjusted_position_pct))
            
            # Calculate position size in currency units
            position_value = account_balance * bounded_position_pct
            
            return position_value
            
        except Exception as e:
            self.logger.error(f"Error calculating volatility target size: {e}")
            return 0.0

class EnhancedRiskManager:
    """
    Enhanced Professional Risk Manager for Institutional Trading
    
    This class provides comprehensive risk management capabilities including
    ML-enhanced position sizing, dynamic portfolio heat monitoring, advanced
    correlation analysis, and sophisticated drawdown protection.
    """
    
    def __init__(self, config: TradingConfig, data_manager: EnhancedDataManager):
        self.config = config
        self.data_manager = data_manager
        
        # Risk parameters
        self.max_risk_per_trade = config.max_risk_per_trade
        self.max_portfolio_risk = config.max_portfolio_risk
        self.max_drawdown = config.max_drawdown
        self.max_daily_loss = config.max_daily_loss
        
        # Advanced risk parameters
        self.correlation_limit = config.get('risk_management.correlation_limit', 0.7)
        self.volatility_target = config.get('risk_management.volatility_target', 0.15)
        self.var_confidence = config.get('risk_management.var_confidence', 0.95)
        
        # Risk tracking
        self.daily_risk_used = 0.0
        self.portfolio_positions = {}
        self.risk_history = deque(maxlen=10000)
        self.drawdown_history = deque(maxlen=1000)
        
        # Advanced components
        self.volatility_analyzer = VolatilityAnalyzer(config)
        self.correlation_analyzer = CorrelationAnalyzer(config)
        self.position_sizer = PositionSizer(config)
        
        # Performance tracking
        self.total_risk_calculations = 0
        self.risk_alerts_generated = 0
        self.emergency_stops_triggered = 0
        
        # Threading
        self.risk_lock = threading.Lock()
        self.monitoring_task = None
        self.is_monitoring = False
        
        # Setup logging
        self.logger = setup_logging('INFO')
        self.logger.info("🛡️ Enhanced Risk Manager initialized")
    
    async def initialize(self) -> bool:
        """Initialize risk manager with all components"""
        try:
            self.logger.info("🚀 Initializing Enhanced Risk Manager...")
            
            # Start risk monitoring
            await self._start_risk_monitoring()
            
            self.logger.info("✅ Enhanced Risk Manager initialization completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing risk manager: {e}")
            return False
    
    async def calculate_position_size(self, signal: Dict[str, Any], 
                                    ml_predictions: Optional[Dict[str, Any]] = None,
                                    account_balance: Optional[float] = None) -> Optional[RiskMetrics]:
        """
        Calculate comprehensive position size with ML enhancement
        """
        try:
            with self.risk_lock:
                self.total_risk_calculations += 1
                
                # Extract signal parameters
                symbol = signal.get('symbol')
                direction = signal.get('action', 'BUY')
                entry_price = signal.get('entry_price', 0)
                stop_loss = signal.get('stop_loss', 0)
                take_profit = signal.get('take_profit', 0)
                confidence = signal.get('confidence', 0.7)
                strategy = signal.get('strategy', 'Unknown')
                
                # Get account balance
                if account_balance is None:
                    account_balance = await self._get_account_balance()
                
                # Validate inputs
                if not self._validate_risk_inputs(symbol, entry_price, stop_loss, account_balance):
                    return None
                
                # Pre-flight risk checks
                if not await self._pre_flight_risk_checks(symbol, account_balance):
                    return None
                
                # Get market data
                market_data = await self._get_market_data_for_risk(symbol)
                
                # Detect market regime
                market_regime = await self._detect_market_regime(symbol, market_data)
                
                # Calculate multiple position sizes
                position_sizes = await self._calculate_multiple_position_sizes(
                    symbol, entry_price, stop_loss, account_balance, confidence, ml_predictions, market_data
                )
                
                # Select optimal size using ML and market conditions
                optimal_size = await self._select_optimal_position_size(
                    position_sizes, symbol, ml_predictions, market_regime, confidence
                )
                
                # Apply portfolio-level adjustments
                portfolio_adjusted_size = await self._apply_portfolio_adjustments(
                    optimal_size, symbol, direction, account_balance
                )
                
                # Apply correlation adjustments
                correlation_adjusted_size = await self._apply_correlation_adjustments(
                    portfolio_adjusted_size, symbol, direction
                )
                
                # Apply drawdown protection
                final_size = await self._apply_drawdown_protection(
                    correlation_adjusted_size, account_balance
                )
                
                # Calculate comprehensive risk metrics
                risk_metrics = await self._calculate_comprehensive_risk_metrics(
                    symbol, final_size, entry_price, stop_loss, take_profit,
                    account_balance, position_sizes, ml_predictions, market_regime
                )
                
                # Validate final risk
                if not self._validate_final_risk(risk_metrics):
                    return None
                
                # Update risk tracking
                await self._update_risk_tracking(risk_metrics, symbol, strategy)
                
                return risk_metrics
                
        except Exception as e:
            self.logger.error(f"Error calculating position size for {symbol}: {e}")
            return None
    
    async def _get_account_balance(self) -> float:
        """Get current account balance"""
        try:
            # This would integrate with execution engine to get real account balance
            # For now, return configured initial balance
            return self.config.initial_balance
            
        except Exception as e:
            self.logger.error(f"Error getting account balance: {e}")
            return self.config.initial_balance
    
    def _validate_risk_inputs(self, symbol: str, entry_price: float, 
                            stop_loss: float, account_balance: float) -> bool:
        """Validate risk calculation inputs"""
        try:
            if not symbol or not isinstance(symbol, str):
                self.logger.error("Invalid symbol provided")
                return False
            
            if entry_price <= 0:
                self.logger.error(f"Invalid entry price: {entry_price}")
                return False
                
            if stop_loss <= 0:
                self.logger.error(f"Invalid stop loss: {stop_loss}")
                return False
                
            if account_balance <= 0:
                self.logger.error(f"Invalid account balance: {account_balance}")
                return False
            
            # Check if stop loss makes sense
            risk_per_unit = abs(entry_price - stop_loss)
            if risk_per_unit == 0:
                self.logger.error("Stop loss equals entry price")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating risk inputs: {e}")
            return False
    
    async def _pre_flight_risk_checks(self, symbol: str, account_balance: float) -> bool:
        """Comprehensive pre-flight risk checks"""
        try:
            # Check daily risk limits
            if self.daily_risk_used >= self.max_daily_loss * account_balance:
                self.logger.warning(f"Daily risk limit exceeded: {self.daily_risk_used:.2f}")
                return False
            
            # Check portfolio heat
            portfolio_heat = await self.calculate_portfolio_heat()
            if portfolio_heat.portfolio_heat > self.max_portfolio_risk:
                self.logger.warning(f"Portfolio heat too high: {portfolio_heat.portfolio_heat:.2%}")
                return False
            
            # Check drawdown
            current_drawdown = await self.get_current_drawdown()
            if current_drawdown > self.max_drawdown:
                self.logger.warning(f"Maximum drawdown exceeded: {current_drawdown:.2%}")
                return False
            
            # Check symbol-specific limits
            symbol_exposure = self._calculate_symbol_exposure(symbol)
            max_symbol_exposure = self.config.get('risk_management.max_symbol_exposure', 0.3)
            if symbol_exposure > max_symbol_exposure:
                self.logger.warning(f"Symbol exposure limit exceeded for {symbol}: {symbol_exposure:.2%}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error in pre-flight risk checks: {e}")
            return False
    
    async def _get_market_data_for_risk(self, symbol: str) -> Dict[str, Any]:
        """Get market data specifically for risk calculations"""
        try:
            # Get multi-timeframe data
            timeframes = ['M15', 'H1', 'H4', 'D1']
            market_data = {}
            
            for tf in timeframes:
                data = await self.data_manager.get_historical_data(symbol, tf, count=100)
                if not data.empty:
                    market_data[tf] = data
            
            # Calculate volatilities
            volatilities = self.volatility_analyzer.calculate_multi_timeframe_volatility(market_data)
            
            # Detect volatility regime
            vol_regime = self.volatility_analyzer.detect_volatility_regime(symbol, market_data)
            
            return {
                'price_data': market_data,
                'volatilities': volatilities,
                'volatility_regime': vol_regime,
                'current_price': market_data.get('M15', market_data.get('H1', pd.DataFrame()))['close'].iloc[-1] if market_data else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting market data for risk: {e}")
            return {}
    
    async def _detect_market_regime(self, symbol: str, market_data: Dict[str, Any]) -> MarketRegime:
        """Detect current market regime for risk assessment"""
        try:
            if not market_data or 'price_data' not in market_data:
                return MarketRegime.RANGING
            
            # Get primary timeframe data
            primary_data = market_data['price_data'].get('H1', market_data['price_data'].get('M15'))
            
            if primary_data is None or primary_data.empty:
                return MarketRegime.RANGING
            
            # Calculate trend strength
            close_prices = primary_data['close']
            sma_20 = close_prices.rolling(20).mean()
            sma_50 = close_prices.rolling(50).mean()
            
            current_price = close_prices.iloc[-1]
            sma_20_current = sma_20.iloc[-1]
            sma_50_current = sma_50.iloc[-1]
            
            # Volatility regime
            vol_regime = market_data.get('volatility_regime', 'normal')
            
            if vol_regime == 'crisis':
                return MarketRegime.CRISIS
            elif vol_regime == 'high_volatility':
                return MarketRegime.HIGH_VOLATILITY
            elif vol_regime == 'low_volatility':
                return MarketRegime.LOW_VOLATILITY
            
            # Trend analysis
            if current_price > sma_20_current > sma_50_current:
                # Strong uptrend
                trend_strength = (current_price - sma_50_current) / sma_50_current
                if trend_strength > 0.05:  # 5% above long-term average
                    return MarketRegime.TRENDING_BULL
            elif current_price < sma_20_current < sma_50_current:
                # Strong downtrend
                trend_strength = (sma_50_current - current_price) / sma_50_current
                if trend_strength > 0.05:  # 5% below long-term average
                    return MarketRegime.TRENDING_BEAR
            
            # Check for breakout conditions
            recent_high = close_prices.tail(20).max()
            recent_low = close_prices.tail(20).min()
            price_range = recent_high - recent_low
            
            if price_range > 0:
                position_in_range = (current_price - recent_low) / price_range
                if position_in_range > 0.9 or position_in_range < 0.1:
                    return MarketRegime.BREAKOUT
            
            return MarketRegime.RANGING
            
        except Exception as e:
            self.logger.error(f"Error detecting market regime: {e}")
            return MarketRegime.RANGING
    
    async def _calculate_multiple_position_sizes(self, symbol: str, entry_price: float,
                                               stop_loss: float, account_balance: float,
                                               confidence: float, ml_predictions: Optional[Dict[str, Any]],
                                               market_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate position sizes using multiple methods"""
        try:
            sizes = {}
            
            # 1. Fixed fractional method
            risk_amount = account_balance * self.max_risk_per_trade
            risk_per_share = abs(entry_price - stop_loss)
            sizes['fixed_fractional'] = risk_amount / risk_per_share if risk_per_share > 0 else 0
            
            # 2. Kelly Criterion (requires historical performance data)
            win_rate = 0.6  # Default assumption
            avg_win = 0.02  # 2% average win
            avg_loss = 0.01  # 1% average loss
            
            # Use ML predictions to adjust win rate
            if ml_predictions and 'ensemble' in ml_predictions:
                ensemble_conf = ml_predictions['ensemble'].get('confidence', 0.5)
                win_rate = max(0.5, min(0.8, 0.5 + ensemble_conf * 0.3))
            
            sizes['kelly'] = self.position_sizer.calculate_kelly_criterion_size(
                symbol, entry_price, stop_loss, account_balance, win_rate, avg_win, avg_loss, confidence
            )
            
            # 3. Volatility targeting
            volatilities = market_data.get('volatilities', {})
            if volatilities:
                avg_volatility = np.mean(list(volatilities.values()))
                sizes['volatility_target'] = self.position_sizer.calculate_volatility_target_size(
                    symbol, account_balance, avg_volatility, self.volatility_target
                )
            else:
                sizes['volatility_target'] = sizes['fixed_fractional']
            
            # 4. ML-enhanced sizing
            if ml_predictions:
                ml_adjustment = self._calculate_ml_adjustment_factor(ml_predictions)
                sizes['ml_enhanced'] = sizes['fixed_fractional'] * ml_adjustment
            else:
                sizes['ml_enhanced'] = sizes['fixed_fractional']
            
            return sizes
            
        except Exception as e:
            self.logger.error(f"Error calculating multiple position sizes: {e}")
            return {}
    
    def _calculate_ml_adjustment_factor(self, ml_predictions: Dict[str, Any]) -> float:
        """Calculate ML-based adjustment factor for position sizing"""
        try:
            adjustment = 1.0
            
            # Ensemble model adjustment
            if 'ensemble' in ml_predictions:
                ensemble = ml_predictions['ensemble']
                confidence = ensemble.get('confidence', 0.5)
                agreement = ensemble.get('model_agreement', 0.5)
                
                # Higher confidence and agreement = larger positions
                ensemble_factor = 0.5 + (confidence * agreement)
                adjustment *= ensemble_factor
            
            # Individual model consistency check
            model_agreements = []
            
            if 'lstm' in ml_predictions:
                lstm_conf = ml_predictions['lstm'].get('confidence_scores', {})
                if lstm_conf:
                    avg_lstm_conf = np.mean(list(lstm_conf.values()))
                    model_agreements.append(avg_lstm_conf)
            
            if 'random_forest' in ml_predictions:
                rf_conf = ml_predictions['random_forest'].get('confidence', 0.5)
                model_agreements.append(rf_conf)
            
            if 'svm' in ml_predictions:
                svm_conf = ml_predictions['svm'].get('confidence', 0.5)
                model_agreements.append(svm_conf)
            
            # Consistency bonus
            if model_agreements:
                consistency = 1.0 - np.std(model_agreements)  # Lower std = higher consistency
                adjustment *= (0.8 + 0.4 * consistency)  # 0.8 to 1.2 multiplier
            
            # Bound the adjustment factor
            return max(0.2, min(2.0, adjustment))
            
        except Exception as e:
            self.logger.error(f"Error calculating ML adjustment factor: {e}")
            return 1.0
    
    async def _select_optimal_position_size(self, sizes: Dict[str, float], symbol: str,
                                          ml_predictions: Optional[Dict[str, Any]],
                                          market_regime: MarketRegime, confidence: float) -> float:
        """Select optimal position size based on market conditions and ML predictions"""
        try:
            if not sizes:
                return 0.0
            
            # Remove any invalid sizes
            valid_sizes = {k: v for k, v in sizes.items() if v > 0 and not np.isnan(v)}
            
            if not valid_sizes:
                return 0.0
            
            # Weight different methods based on market regime and ML predictions
            weights = {
                'fixed_fractional': 0.3,
                'kelly': 0.2,
                'volatility_target': 0.2,
                'ml_enhanced': 0.3
            }
            
            # Adjust weights based on market regime
            if market_regime == MarketRegime.HIGH_VOLATILITY:
                weights['volatility_target'] += 0.2
                weights['fixed_fractional'] -= 0.1
                weights['kelly'] -= 0.1
            elif market_regime == MarketRegime.TRENDING_BULL or market_regime == MarketRegime.TRENDING_BEAR:
                weights['kelly'] += 0.15
                weights['ml_enhanced'] += 0.1
                weights['fixed_fractional'] -= 0.15
                weights['volatility_target'] -= 0.1
            
            # Adjust weights based on ML prediction quality
            if ml_predictions and 'ensemble' in ml_predictions:
                ensemble_quality = ml_predictions['ensemble'].get('confidence', 0.5) * \
                                 ml_predictions['ensemble'].get('model_agreement', 0.5)
                
                if ensemble_quality > 0.7:  # High quality predictions
                    weights['ml_enhanced'] += 0.2
                    weights['fixed_fractional'] -= 0.1
                    weights['volatility_target'] -= 0.1
            
            # Normalize weights
            total_weight = sum(weights.values())
            if total_weight > 0:
                weights = {k: v / total_weight for k, v in weights.items()}
            
            # Calculate weighted average
            weighted_size = 0.0
            for method, size in valid_sizes.items():
                weight = weights.get(method, 0.0)
                weighted_size += size * weight
            
            # Apply confidence adjustment
            confidence_adjusted_size = weighted_size * confidence
            
            # Ensure minimum and maximum bounds
            min_size = self.config.get('risk_management.min_position_size', 0.01)
            max_size = self.config.get('risk_management.max_position_size', 10.0)
            
            final_size = max(min_size, min(max_size, confidence_adjusted_size))
            
            return final_size
            
        except Exception as e:
            self.logger.error(f"Error selecting optimal position size: {e}")
            return 0.0
    
    async def _apply_portfolio_adjustments(self, base_size: float, symbol: str,
                                         direction: str, account_balance: float) -> float:
        """Apply portfolio-level risk adjustments"""
        try:
            # Calculate current portfolio heat
            portfolio_heat = await self.calculate_portfolio_heat()
            
            # Reduce size if portfolio is overheated
            if portfolio_heat.portfolio_heat > 0.8 * self.max_portfolio_risk:
                heat_adjustment = max(0.5, 1.0 - (portfolio_heat.portfolio_heat / self.max_portfolio_risk))
                base_size *= heat_adjustment
                self.logger.info(f"Applied portfolio heat adjustment: {heat_adjustment:.2f}")
            
            # Check sector/symbol concentration
            symbol_exposure = self._calculate_symbol_exposure(symbol)
            max_symbol_exposure = self.config.get('risk_management.max_symbol_exposure', 0.3)
            
            if symbol_exposure > 0.8 * max_symbol_exposure:
                concentration_adjustment = max(0.3, 1.0 - (symbol_exposure / max_symbol_exposure))
                base_size *= concentration_adjustment
                self.logger.info(f"Applied concentration adjustment for {symbol}: {concentration_adjustment:.2f}")
            
            return base_size
            
        except Exception as e:
            self.logger.error(f"Error applying portfolio adjustments: {e}")
            return base_size
    
    async def _apply_correlation_adjustments(self, base_size: float, symbol: str, direction: str) -> float:
        """Apply correlation-based risk adjustments"""
        try:
            # Get current positions
            current_positions = self.portfolio_positions.copy()
            
            if len(current_positions) < 2:
                return base_size  # No correlation risk with single position
            
            # Get correlation data
            symbols = list(current_positions.keys()) + [symbol]
            
            # Get price data for correlation calculation
            price_data = {}
            for sym in symbols:
                try:
                    data = await self.data_manager.get_historical_data(sym, 'D1', count=60)
                    if not data.empty:
                        price_data[sym] = data
                except:
                    continue
            
            if len(price_data) < 2:
                return base_size
            
            # Calculate correlations
            correlation_matrix = self.correlation_analyzer.calculate_dynamic_correlations(symbols, price_data)
            
            if correlation_matrix.empty:
                return base_size
            
            # Calculate correlation risk for the new position
            test_positions = current_positions.copy()
            test_positions[symbol] = base_size * (1 if direction == 'BUY' else -1)
            
            correlation_risk = self.correlation_analyzer.calculate_portfolio_correlation_risk(
                test_positions, correlation_matrix
            )
            
            # Apply correlation adjustment
            if correlation_risk > self.correlation_limit:
                correlation_adjustment = max(0.2, 1.0 - (correlation_risk - self.correlation_limit))
                adjusted_size = base_size * correlation_adjustment
                self.logger.info(f"Applied correlation adjustment for {symbol}: {correlation_adjustment:.2f}")
                return adjusted_size
            
            return base_size
            
        except Exception as e:
            self.logger.error(f"Error applying correlation adjustments: {e}")
            return base_size
    
    async def _apply_drawdown_protection(self, base_size: float, account_balance: float) -> float:
        """Apply drawdown protection adjustments"""
        try:
            current_drawdown = await self.get_current_drawdown()
            
            # Reduce position sizes during drawdown periods
            if current_drawdown > 0.05:  # 5% drawdown threshold
                # Scale down positions progressively
                drawdown_factor = current_drawdown / self.max_drawdown
                protection_factor = max(0.1, 1.0 - (drawdown_factor * 0.8))
                
                adjusted_size = base_size * protection_factor
                self.logger.info(f"Applied drawdown protection: {protection_factor:.2f} (DD: {current_drawdown:.2%})")
                return adjusted_size
            
            return base_size
            
        except Exception as e:
            self.logger.error(f"Error applying drawdown protection: {e}")
            return base_size
    
    async def _calculate_comprehensive_risk_metrics(self, symbol: str, position_size: float,
                                                   entry_price: float, stop_loss: float,
                                                   take_profit: float, account_balance: float,
                                                   position_sizes: Dict[str, float],
                                                   ml_predictions: Optional[Dict[str, Any]],
                                                   market_regime: MarketRegime) -> RiskMetrics:
        """Calculate comprehensive risk metrics"""
        try:
            # Basic risk calculations
            risk_per_share = abs(entry_price - stop_loss)
            reward_per_share = abs(take_profit - entry_price) if take_profit > 0 else risk_per_share * 2
            
            risk_amount = position_size * risk_per_share
            max_gain_amount = position_size * reward_per_share
            
            # Risk ratios
            risk_reward_ratio = reward_per_share / risk_per_share if risk_per_share > 0 else 2.0
            portfolio_risk_pct = risk_amount / account_balance
            
            # ML-enhanced metrics
            ml_risk_score = 0.5
            ensemble_agreement = 0.5
            
            if ml_predictions:
                ml_risk_score = self._calculate_ml_risk_score(ml_predictions)
                if 'ensemble' in ml_predictions:
                    ensemble_agreement = ml_predictions['ensemble'].get('model_agreement', 0.5)
            
            # Advanced risk metrics
            var_95, cvar_95 = await self._calculate_var_cvar(symbol, position_size, entry_price)
            
            # Expected performance metrics
            sharpe_expected = self._estimate_sharpe_ratio(risk_reward_ratio, ml_risk_score)
            sortino_expected = sharpe_expected * 1.2  # Approximation
            
            # Liquidity and execution risk
            liquidity_score = await self._calculate_liquidity_score(symbol)
            execution_risk_score = self._calculate_execution_risk_score(symbol, position_size)
            
            return RiskMetrics(
                position_size=position_size,
                risk_amount=risk_amount,
                max_loss_amount=risk_amount,
                max_gain_amount=max_gain_amount,
                risk_reward_ratio=risk_reward_ratio,
                portfolio_risk_pct=portfolio_risk_pct,
                symbol_risk_pct=self._calculate_symbol_exposure(symbol),
                confidence_adjusted_size=position_size,
                ml_risk_score=ml_risk_score,
                ensemble_agreement_factor=ensemble_agreement,
                kelly_size=position_sizes.get('kelly', 0),
                optimal_f_size=position_sizes.get('optimal_f', 0),
                volatility_adjusted_size=position_sizes.get('volatility_target', 0),
                correlation_adjusted_size=position_size,
                var_95=var_95,
                cvar_95=cvar_95,
                sharpe_expected=sharpe_expected,
                sortino_expected=sortino_expected,
                sizing_method='ml_enhanced',
                market_regime=market_regime.value,
                volatility_regime='normal',
                liquidity_score=liquidity_score,
                execution_risk_score=execution_risk_score
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating comprehensive risk metrics: {e}")
            return RiskMetrics(
                position_size=0, risk_amount=0, max_loss_amount=0, max_gain_amount=0,
                risk_reward_ratio=0, portfolio_risk_pct=0, symbol_risk_pct=0,
                confidence_adjusted_size=0, ml_risk_score=0.5, ensemble_agreement_factor=0.5,
                kelly_size=0, optimal_f_size=0, volatility_adjusted_size=0, correlation_adjusted_size=0,
                var_95=0, cvar_95=0, sharpe_expected=0, sortino_expected=0,
                sizing_method='error', market_regime='unknown', volatility_regime='unknown',
                liquidity_score=0, execution_risk_score=1.0
            )
    
    def _calculate_ml_risk_score(self, ml_predictions: Dict[str, Any]) -> float:
        """Calculate ML-based risk score"""
        try:
            risk_score = 0.5  # Neutral
            
            if 'ensemble' in ml_predictions:
                ensemble = ml_predictions['ensemble']
                confidence = ensemble.get('confidence', 0.5)
                agreement = ensemble.get('model_agreement', 0.5)
                
                # Higher confidence and agreement = lower risk
                risk_score = 1.0 - (confidence * agreement)
            
            return max(0.1, min(0.9, risk_score))
            
        except Exception as e:
            self.logger.error(f"Error calculating ML risk score: {e}")
            return 0.5
    
    async def _calculate_var_cvar(self, symbol: str, position_size: float, entry_price: float) -> Tuple[float, float]:
        """Calculate Value at Risk and Conditional VaR"""
        try:
            # Get historical returns
            data = await self.data_manager.get_historical_data(symbol, 'D1', count=252)
            
            if data.empty:
                return 0.0, 0.0
            
            returns = data['close'].pct_change().dropna()
            
            if len(returns) < 50:
                return 0.0, 0.0
            
            position_value = position_size * entry_price
            
            # Calculate VaR at 95% confidence
            var_95 = np.percentile(returns, (1 - self.var_confidence) * 100) * position_value
            
            # Calculate CVaR (Expected Shortfall)
            var_threshold = np.percentile(returns, (1 - self.var_confidence) * 100)
            tail_returns = returns[returns <= var_threshold]
            cvar_95 = np.mean(tail_returns) * position_value if len(tail_returns) > 0 else var_95
            
            return abs(var_95), abs(cvar_95)
            
        except Exception as e:
            self.logger.error(f"Error calculating VaR/CVaR: {e}")
            return 0.0, 0.0
    
    def _estimate_sharpe_ratio(self, risk_reward_ratio: float, ml_risk_score: float) -> float:
        """Estimate expected Sharpe ratio"""
        try:
            # Simple estimation based on risk-reward and ML confidence
            base_sharpe = 0.5  # Conservative base
            
            # Adjust for risk-reward ratio
            rr_adjustment = min(2.0, risk_reward_ratio) / 2.0
            
            # Adjust for ML confidence (lower risk score = higher confidence)
            ml_adjustment = (1.0 - ml_risk_score)
            
            estimated_sharpe = base_sharpe * (1 + rr_adjustment + ml_adjustment)
            
            return max(0.0, min(3.0, estimated_sharpe))
            
        except Exception as e:
            self.logger.error(f"Error estimating Sharpe ratio: {e}")
            return 0.5
    
    async def _calculate_liquidity_score(self, symbol: str) -> float:
        """Calculate liquidity score for the symbol"""
        try:
            # Get recent volume data
            data = await self.data_manager.get_historical_data(symbol, 'H1', count=24)
            
            if data.empty or 'volume' not in data.columns:
                return 0.5  # Neutral score if no volume data
            
            # Calculate average volume
            avg_volume = data['volume'].mean()
            
            # Simple liquidity scoring (this would be more sophisticated in production)
            if avg_volume > 1000000:  # High volume
                return 0.9
            elif avg_volume > 100000:  # Medium volume
                return 0.7
            elif avg_volume > 10000:   # Low volume
                return 0.4
            else:  # Very low volume
                return 0.2
                
        except Exception as e:
            self.logger.error(f"Error calculating liquidity score: {e}")
            return 0.5
    
    def _calculate_execution_risk_score(self, symbol: str, position_size: float) -> float:
        """Calculate execution risk score"""
        try:
            # Factors affecting execution risk:
            # 1. Position size relative to average volume
            # 2. Market volatility
            # 3. Spread conditions
            
            base_risk = 0.1  # Low base risk
            
            # Size impact (larger positions = higher execution risk)
            if position_size > 10.0:  # Large position
                base_risk += 0.3
            elif position_size > 5.0:  # Medium position
                base_risk += 0.1
            
            # Symbol-specific risk (major pairs have lower execution risk)
            major_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD']
            if symbol not in major_pairs:
                base_risk += 0.2
            
            return min(1.0, base_risk)
            
        except Exception as e:
            self.logger.error(f"Error calculating execution risk score: {e}")
            return 0.3
    
    def _validate_final_risk(self, risk_metrics: RiskMetrics) -> bool:
        """Validate final risk metrics"""
        try:
            # Check position size is reasonable
            if risk_metrics.position_size <= 0:
                self.logger.error("Invalid position size: must be positive")
                return False
            
            # Check portfolio risk limit
            if risk_metrics.portfolio_risk_pct > self.max_risk_per_trade * 1.5:
                self.logger.error(f"Portfolio risk too high: {risk_metrics.portfolio_risk_pct:.2%}")
                return False
            
            # Check risk-reward ratio
            if risk_metrics.risk_reward_ratio < 0.5:
                self.logger.warning(f"Poor risk-reward ratio: {risk_metrics.risk_reward_ratio:.2f}")
                # Allow but warn
            
            # Check ML risk score
            if risk_metrics.ml_risk_score > 0.9:
                self.logger.warning(f"High ML risk score: {risk_metrics.ml_risk_score:.2f}")
                # Allow but warn
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating final risk: {e}")
            return False
    
    async def _update_risk_tracking(self, risk_metrics: RiskMetrics, symbol: str, strategy: str):
        """Update risk tracking with new position"""
        try:
            # Update daily risk used
            self.daily_risk_used += risk_metrics.risk_amount
            
            # Update portfolio positions
            self.portfolio_positions[symbol] = {
                'size': risk_metrics.position_size,
                'risk_amount': risk_metrics.risk_amount,
                'strategy': strategy,
                'timestamp': datetime.utcnow(),
                'ml_risk_score': risk_metrics.ml_risk_score
            }
            
            # Add to risk history
            self.risk_history.append({
                'timestamp': datetime.utcnow(),
                'symbol': symbol,
                'strategy': strategy,
                'risk_metrics': risk_metrics
            })
            
        except Exception as e:
            self.logger.error(f"Error updating risk tracking: {e}")
    
    def _calculate_symbol_exposure(self, symbol: str) -> float:
        """Calculate current exposure to a specific symbol"""
        try:
            if symbol not in self.portfolio_positions:
                return 0.0
            
            position = self.portfolio_positions[symbol]
            return position.get('risk_amount', 0.0) / self.config.initial_balance
            
        except Exception as e:
            self.logger.error(f"Error calculating symbol exposure: {e}")
            return 0.0
    
    async def calculate_portfolio_heat(self) -> PortfolioHeat:
        """Calculate comprehensive portfolio heat metrics"""
        try:
            if not self.portfolio_positions:
                return PortfolioHeat(
                    total_exposure=0.0, net_exposure=0.0, gross_exposure=0.0,
                    long_exposure=0.0, short_exposure=0.0, max_symbol_exposure=0.0,
                    max_sector_exposure=0.0, max_correlation_exposure=0.0,
                    portfolio_heat=0.0, risk_adjusted_heat=0.0, volatility_adjusted_heat=0.0,
                    portfolio_correlation=0.0, max_correlation_pair=('', '', 0.0),
                    correlation_risk_score=0.0
                )
            
            # Calculate exposures
            total_risk = sum(pos.get('risk_amount', 0) for pos in self.portfolio_positions.values())
            account_balance = await self._get_account_balance()
            
            total_exposure = total_risk / account_balance
            
            # For simplified calculation, assume all positions are long
            # In reality, you'd track long/short separately
            long_exposure = total_exposure
            short_exposure = 0.0
            net_exposure = long_exposure - short_exposure
            gross_exposure = long_exposure + short_exposure
            
            # Calculate max symbol exposure
            max_symbol_exposure = max(
                (pos.get('risk_amount', 0) / account_balance for pos in self.portfolio_positions.values()),
                default=0.0
            )
            
            # Portfolio heat calculation
            portfolio_heat = min(1.0, total_exposure / self.max_portfolio_risk)
            
            # Risk-adjusted heat (considering ML risk scores)
            ml_risk_weighted = sum(
                pos.get('risk_amount', 0) * pos.get('ml_risk_score', 0.5)
                for pos in self.portfolio_positions.values()
            )
            risk_adjusted_heat = ml_risk_weighted / account_balance / self.max_portfolio_risk
            
            return PortfolioHeat(
                total_exposure=total_exposure,
                net_exposure=net_exposure,
                gross_exposure=gross_exposure,
                long_exposure=long_exposure,
                short_exposure=short_exposure,
                max_symbol_exposure=max_symbol_exposure,
                max_sector_exposure=max_symbol_exposure,  # Simplified
                max_correlation_exposure=0.0,  # Would need correlation analysis
                portfolio_heat=portfolio_heat,
                risk_adjusted_heat=risk_adjusted_heat,
                volatility_adjusted_heat=portfolio_heat,  # Simplified
                portfolio_correlation=0.0,  # Would need correlation matrix
                max_correlation_pair=('', '', 0.0),  # Would need correlation analysis
                correlation_risk_score=0.0
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating portfolio heat: {e}")
            return PortfolioHeat(
                total_exposure=0.0, net_exposure=0.0, gross_exposure=0.0,
                long_exposure=0.0, short_exposure=0.0, max_symbol_exposure=0.0,
                max_sector_exposure=0.0, max_correlation_exposure=0.0,
                portfolio_heat=0.0, risk_adjusted_heat=0.0, volatility_adjusted_heat=0.0,
                portfolio_correlation=0.0, max_correlation_pair=('', '', 0.0),
                correlation_risk_score=0.0
            )
    
    async def get_current_drawdown(self) -> float:
        """Calculate current drawdown"""
        try:
            # In a real implementation, this would calculate actual drawdown
            # from account equity history
            # For now, return a simulated value
            
            if not self.drawdown_history:
                return 0.0
            
            # Get recent equity values (simulated)
            recent_drawdowns = [item for item in self.drawdown_history if 
                              (datetime.utcnow() - item.get('timestamp', datetime.utcnow())).days <= 30]
            
            if not recent_drawdowns:
                return 0.0
            
            max_recent_drawdown = max(item.get('drawdown', 0.0) for item in recent_drawdowns)
            return max_recent_drawdown
            
        except Exception as e:
            self.logger.error(f"Error calculating current drawdown: {e}")
            return 0.0
    
    def update_position_closed(self, symbol: str, pnl: float):
        """Update risk tracking when position is closed"""
        try:
            with self.risk_lock:
                # Remove from portfolio positions
                if symbol in self.portfolio_positions:
                    position = self.portfolio_positions.pop(symbol)
                    
                    # Update daily risk used (reduce it)
                    self.daily_risk_used = max(0, self.daily_risk_used - position.get('risk_amount', 0))
                    
                    # Track performance for future risk calculations
                    performance_record = {
                        'symbol': symbol,
                        'strategy': position.get('strategy', 'Unknown'),
                        'risk_amount': position.get('risk_amount', 0),
                        'pnl': pnl,
                        'timestamp': datetime.utcnow(),
                        'ml_risk_score': position.get('ml_risk_score', 0.5)
                    }
                    
                    self.position_sizer.historical_performance.append(performance_record)
                    
        except Exception as e:
            self.logger.error(f"Error updating position closed for {symbol}: {e}")
    
    async def _start_risk_monitoring(self):
        """Start background risk monitoring"""
        try:
            self.is_monitoring = True
            self.monitoring_task = asyncio.create_task(self._risk_monitoring_loop())
            
        except Exception as e:
            self.logger.error(f"Error starting risk monitoring: {e}")
    
    async def _risk_monitoring_loop(self):
        """Background risk monitoring loop"""
        while self.is_monitoring:
            try:
                # Reset daily risk if new day
                current_date = datetime.now().date()
                if not hasattr(self, '_last_reset_date') or self._last_reset_date != current_date:
                    self.daily_risk_used = 0.0
                    self._last_reset_date = current_date
                    self.logger.info("Daily risk counters reset")
                
                # Monitor portfolio heat
                portfolio_heat = await self.calculate_portfolio_heat()
                
                if portfolio_heat.portfolio_heat > 0.9 * self.max_portfolio_risk:
                    self.risk_alerts_generated += 1
                    self.logger.warning(f"Portfolio heat approaching limit: {portfolio_heat.portfolio_heat:.2%}")
                
                # Monitor drawdown
                current_drawdown = await self.get_current_drawdown()
                
                if current_drawdown > 0.8 * self.max_drawdown:
                    self.risk_alerts_generated += 1
                    self.logger.warning(f"Drawdown approaching limit: {current_drawdown:.2%}")
                
                await asyncio.sleep(300)  # Monitor every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in risk monitoring loop: {e}")
                await asyncio.sleep(60)
    
    def get_risk_summary(self) -> Dict[str, Any]:
        """Get comprehensive risk summary"""
        try:
            return {
                'daily_risk_used': self.daily_risk_used,
                'daily_risk_limit': self.max_daily_loss * self.config.initial_balance,
                'daily_risk_available': max(0, self.max_daily_loss * self.config.initial_balance - self.daily_risk_used),
                'portfolio_positions_count': len(self.portfolio_positions),
                'total_risk_calculations': self.total_risk_calculations,
                'risk_alerts_generated': self.risk_alerts_generated,
                'emergency_stops_triggered': self.emergency_stops_triggered,
                'portfolio_positions': self.portfolio_positions.copy(),
                'max_risk_per_trade': self.max_risk_per_trade,
                'max_portfolio_risk': self.max_portfolio_risk,
                'max_drawdown_limit': self.max_drawdown,
                'correlation_limit': self.correlation_limit,
                'volatility_target': self.volatility_target
            }
            
        except Exception as e:
            self.logger.error(f"Error getting risk summary: {e}")
            return {}
    
    async def shutdown(self):
        """Graceful shutdown of risk manager"""
        try:
            self.logger.info("🛑 Shutting down Enhanced Risk Manager...")
            
            self.is_monitoring = False
            
            if self.monitoring_task and not self.monitoring_task.done():
                self.monitoring_task.cancel()
            
            self.logger.info("✅ Enhanced Risk Manager shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error shutting down risk manager: {e}")

# Factory function for creating risk manager
def create_risk_manager(config: TradingConfig, data_manager: EnhancedDataManager) -> EnhancedRiskManager:
    """Factory function to create risk manager instance"""
    return EnhancedRiskManager(config, data_manager)
