#!/usr/bin/env python3
"""
===============================================================
TradingBot v2.2 - PROFESSIONAL Trading System - ULTIMATE FIXED VERSION
===============================================================
ULTIMATE FIXES APPLIED:
- Advanced Signal Factory timeframe errors COMPLETELY FIXED
- StrategyDiscoverer class added and working
- Dynamic Kelly Position Sizing integrated
- Real signal confidence calculation (no more fake 0.95)
- Intelligent signal validation and filtering
- ML model integration framework
- Professional risk management system
- Multi-filling mode MT5 execution (FIXED)

Version: 2.2.2 - Ultimate Production Ready System
===============================================================
"""

import argparse
import importlib
import inspect
import json
import logging
import os
import signal
import sys
import threading
import time
import traceback
import warnings
import uuid
import math
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque

# SECURITY: Load environment variables from config/.env file
try:
    from dotenv import load_dotenv
    # CRITICAL FIX: Load .env from config folder
    env_path = Path("config/.env")
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"[SECURITY] Environment variables loaded from {env_path}")
    else:
        # Fallback: try root directory .env
        load_dotenv()
        print("[SECURITY] Environment variables loaded from root .env file")
except ImportError:
    print("[WARNING] python-dotenv not installed. Install with: pip install python-dotenv")
    print("[WARNING] Using system environment variables only")

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        import codecs
        import locale
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        try:
            os.system('chcp 65001 > nul 2>&1')
        except:
            pass
    except:
        pass

# Core dependencies
import pandas as pd
import numpy as np
import MetaTrader5 as mt5
import yaml

# Advanced Signal Factory Integration
try:
    from signal_factory import (
        process_market_data_for_main_py, 
        get_signal_factory,
        SignalFactory,
        SignalType,
        StrategyType
    )
    ADVANCED_SIGNAL_FACTORY_AVAILABLE = True
    print("[FACTORY] Advanced Signal Factory imported successfully")
except ImportError as e:
    ADVANCED_SIGNAL_FACTORY_AVAILABLE = False
    print(f"[WARN] Advanced Signal Factory not available: {e}")

# Professional Position Sizing Import (Kelly Criterion)
try:
    from dynamic_kelly_position_sizing import (
        KellyPositionSizer,
        calculate_dynamic_kelly_size,
        PortfolioRiskManager
    )
    KELLY_POSITION_SIZING_AVAILABLE = True
    print("[KELLY] Professional Kelly Position Sizing imported successfully")
except ImportError as e:
    KELLY_POSITION_SIZING_AVAILABLE = False
    print(f"[WARN] Kelly Position Sizing not available: {e}")
    print("[INFO] Using advanced dynamic position sizing instead")

# ML Model Integration (Framework Ready)
try:
    from ml_models import (
        MLSignalGenerator,
        load_trained_models,
        get_ml_predictions
    )
    ML_MODELS_AVAILABLE = True
    print("[ML] ML Models framework imported successfully")
except ImportError as e:
    ML_MODELS_AVAILABLE = False
    print(f"[WARN] ML Models not available: {e}")
    print("[INFO] ML integration framework ready for implementation")

# Suppress warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

# Safe Windows-compatible logging
EMOJIS = {
    'rocket': '[START]', 'gear': '[INIT]', 'success': '[OK]', 'error': '[ERROR]',
    'warning': '[WARN]', 'info': '[INFO]', 'chart': '[CHART]', 'brain': '[ML]',
    'target': '[TARGET]', 'stop': '[STOP]', 'disconnect': '[DISC]', 'finish': '[DONE]',
    'trade': '[TRADE]', 'signal': '[SIGNAL]', 'money': '[MONEY]', 'check': '[CHECK]',
    'factory': '[FACTORY]', 'process': '[PROCESS]', 'live': '[LIVE]', 'demo': '[DEMO]',
    'security': '[SECURITY]', 'kelly': '[KELLY]', 'ml': '[ML]', 'validation': '[VALID]',
    'quality': '[QUALITY]', 'confidence': '[CONF]', 'fixed': '[FIXED]'
}

# ============================================================================
# PROFESSIONAL DATA STRUCTURES
# ============================================================================

class TradingMode(Enum):
    """Trading execution modes - LIVE and DEMO only"""
    LIVE = "live"
    DEMO = "demo"

class SignalQuality(Enum):
    """Professional signal quality classification"""
    EXCELLENT = "excellent"     # >0.8 confidence, multiple strategies, high validation
    GOOD = "good"              # >0.6 confidence, good validation
    FAIR = "fair"              # >0.4 confidence, basic validation
    POOR = "poor"              # <0.4 confidence, single strategy
    REJECTED = "rejected"       # Failed validation

@dataclass
class TradeExecution:
    """Enhanced trade execution result tracking with professional metrics"""
    symbol: str
    action: str  # BUY/SELL
    volume: float
    entry_price: float
    stop_loss: float
    take_profit: float
    timestamp: datetime
    strategy_names: List[str]
    timeframes: List[str]
    signal_strength: float
    signal_id: str = ""
    factory_processed: bool = False
    advanced_factory_processed: bool = False
    ticket: Optional[int] = None
    status: str = "PENDING"
    pnl: float = 0.0

@dataclass
class SystemMetrics:
    """Enhanced system performance metrics with professional tracking"""
    strategies_loaded: int = 0
    ml_models_loaded: int = 0
    advanced_factory_signals: int = 0
    signals_generated: int = 0
    signals_validated: int = 0
    signals_rejected: int = 0
    trades_executed: int = 0
    successful_trades: int = 0
    failed_trades: int = 0
    total_pnl: float = 0.0
    daily_pnl: float = 0.0
    open_positions: int = 0
    win_rate: float = 0.0
    avg_signal_quality: float = 0.0
    kelly_efficiency: float = 0.0
    avg_confidence: float = 0.0
    avg_validation_score: float = 0.0
    uptime_hours: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class ProfessionalTradingConfig:
    """Professional trading configuration with advanced features"""
    # MT5 Configuration (LOADED FROM config/.env - SECURE)
    mt5_login: int = 0
    mt5_password: str = ""
    mt5_server: str = ""
    mt5_path: str = ""
    
    # Trading Parameters
    symbols: List[str] = field(default_factory=lambda: ["EURUSD", "GBPUSD", "USDJPY"])
    timeframes: List[str] = field(default_factory=lambda: ["M15", "H1", "H4"])
    max_positions: int = 5
    base_position_size: float = 0.01
    
    # Professional Risk Management
    max_risk_per_trade: float = 0.02
    max_daily_loss: float = 0.05
    stop_loss_pips: int = 50
    take_profit_pips: int = 100
    min_signal_confidence: float = 0.4  # More realistic than 0.3
    min_validation_score: float = 0.3
    min_risk_reward_ratio: float = 1.5
    
    # Kelly Position Sizing Configuration
    kelly_enabled: bool = True
    kelly_fraction: float = 0.25  # Conservative Kelly fraction (max 25%)
    max_kelly_size: float = 0.1   # Maximum 10% of capital per trade
    min_kelly_size: float = 0.001 # Minimum position size
    kelly_lookback_trades: int = 50  # Trades to analyze for Kelly calculation
    
    # Professional Signal Validation
    enable_signal_validation: bool = True
    enable_ml_validation: bool = True
    enable_market_condition_check: bool = True
    signal_consensus_required: int = 2  # Minimum strategies for consensus
    max_signal_age_minutes: int = 5
    quality_filter_enabled: bool = True
    
    # Strategy Configuration  
    strategy_weights: Dict[str, float] = field(default_factory=dict)
    enabled_strategies: List[str] = field(default_factory=list)
    
    # Signal Factory Configuration
    signal_factory_enabled: bool = True
    advanced_signal_factory_enabled: bool = True
    signal_processing_interval: int = 2
    signal_aggregation_method: str = "weighted_consensus"
    max_signal_age_minutes: int = 10
    
    # Advanced Signal Factory Settings (FIXED for timeframe errors)
    advanced_factory_config: Dict[str, Any] = field(default_factory=lambda: {
        'min_confidence_threshold': 0.25,
        'high_confidence_threshold': 0.7,
        'enable_signal_aggregation': True,
        'enable_quality_filtering': True,
        'max_workers': 8,
        'timeframe_validation': True,  # FIX: Enable timeframe validation
        'handle_timeframe_errors': True  # FIX: Handle timeframe dict errors
    })
    
    # System Configuration
    trading_mode: TradingMode = TradingMode.DEMO  # Default to DEMO for safety
    log_level: str = "INFO"
    signal_processing_interval_legacy: int = 5

class SafeLogger:
    """Windows-safe logger without Unicode issues - Enhanced"""
    
    def __init__(self, name: str, level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Clear existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Safe formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        try:
            os.makedirs('logs', exist_ok=True)
            file_handler = logging.FileHandler(
                f'logs/professional_trading_{datetime.now().strftime("%Y%m%d_%H%M")}.log',
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not create file handler: {e}")
    
    def _safe_message(self, msg: str) -> str:
        """Convert message to safe format"""
        for emoji, safe in EMOJIS.items():
            msg = msg.replace('🚀', safe).replace('🔧', safe).replace('✅', safe)
            msg = msg.replace('❌', safe).replace('⚠️', safe).replace('ℹ️', safe)
            msg = msg.replace('📊', safe).replace('🧠', safe).replace('🎯', safe)
            msg = msg.replace('🛑', safe).replace('🔌', safe).replace('🏁', safe)
            msg = msg.replace('💰', safe).replace('🏭', safe).replace('⚡', safe)
            msg = msg.replace('🔒', safe).replace('🔐', safe)
        return msg
    
    def info(self, msg: str, *args):
        self.logger.info(self._safe_message(msg), *args)
    
    def error(self, msg: str, *args):
        self.logger.error(self._safe_message(msg), *args)
    
    def warning(self, msg: str, *args):
        self.logger.warning(self._safe_message(msg), *args)
    
    def debug(self, msg: str, *args):
        self.logger.debug(self._safe_message(msg), *args)

# ============================================================================
# PROFESSIONAL SIGNAL CONFIDENCE CALCULATOR (NO MORE FAKE 0.95!)
# ============================================================================

class RealSignalConfidenceCalculator:
    """Calculate REAL signal confidence based on multiple technical factors"""
    
    @staticmethod
    def calculate_real_confidence(data: pd.DataFrame, signal_type: str, 
                                analysis: Dict[str, Any], symbol: str) -> float:
        """
        Calculate REAL confidence based on technical analysis factors
        FIXES the fake 0.95 confidence issue
        """
        try:
            if data.empty or len(data) < 20:
                return 0.3  # Low confidence for insufficient data
            
            confidence_factors = []
            
            # FACTOR 1: Trend Strength (25% weight)
            trend_factor = RealSignalConfidenceCalculator._analyze_trend_strength(data, signal_type)
            confidence_factors.append(('trend', trend_factor, 0.25))
            
            # FACTOR 2: Momentum Indicators (20% weight)
            momentum_factor = RealSignalConfidenceCalculator._analyze_momentum(data, signal_type)
            confidence_factors.append(('momentum', momentum_factor, 0.20))
            
            # FACTOR 3: Volatility Analysis (15% weight)
            volatility_factor = RealSignalConfidenceCalculator._analyze_volatility(data)
            confidence_factors.append(('volatility', volatility_factor, 0.15))
            
            # FACTOR 4: Support/Resistance (20% weight)
            sr_factor = RealSignalConfidenceCalculator._analyze_support_resistance(data, signal_type)
            confidence_factors.append(('support_resistance', sr_factor, 0.20))
            
            # FACTOR 5: Volume Confirmation (10% weight)
            volume_factor = RealSignalConfidenceCalculator._analyze_volume(data, signal_type)
            confidence_factors.append(('volume', volume_factor, 0.10))
            
            # FACTOR 6: Price Action (10% weight)
            price_action_factor = RealSignalConfidenceCalculator._analyze_price_action(data, signal_type)
            confidence_factors.append(('price_action', price_action_factor, 0.10))
            
            # Calculate weighted confidence
            weighted_confidence = sum(factor * weight for _, factor, weight in confidence_factors)
            
            # Apply symbol-specific adjustments
            symbol_multiplier = RealSignalConfidenceCalculator._get_symbol_multiplier(symbol)
            adjusted_confidence = weighted_confidence * symbol_multiplier
            
            # Normalize to realistic range (0.15 - 0.90)
            final_confidence = max(0.15, min(0.90, adjusted_confidence))
            
            return round(final_confidence, 3)
            
        except Exception as e:
            # Return moderate confidence on error, never fake 0.95
            return 0.45
    
    @staticmethod
    def _analyze_trend_strength(data: pd.DataFrame, signal_type: str) -> float:
        """Analyze trend strength for confidence calculation"""
        try:
            if len(data) < 50:
                return 0.5
            
            # Calculate multiple timeframe moving averages
            ma_10 = data['close'].rolling(window=10).mean()
            ma_20 = data['close'].rolling(window=20).mean()
            ma_50 = data['close'].rolling(window=50).mean()
            
            current_price = data['close'].iloc[-1]
            ma_10_current = ma_10.iloc[-1]
            ma_20_current = ma_20.iloc[-1]
            ma_50_current = ma_50.iloc[-1]
            
            if signal_type == 'BUY':
                # For buy signals, check for bullish trend alignment
                if current_price > ma_10_current > ma_20_current > ma_50_current:
                    return 0.9  # Perfect trend alignment
                elif current_price > ma_10_current > ma_20_current:
                    return 0.75  # Good trend alignment
                elif current_price > ma_20_current:
                    return 0.6  # Moderate bullish
                else:
                    return 0.3  # Against trend
            else:  # SELL
                # For sell signals, check for bearish trend alignment
                if current_price < ma_10_current < ma_20_current < ma_50_current:
                    return 0.9  # Perfect bearish alignment
                elif current_price < ma_10_current < ma_20_current:
                    return 0.75  # Good bearish alignment
                elif current_price < ma_20_current:
                    return 0.6  # Moderate bearish
                else:
                    return 0.3  # Against trend
                    
        except:
            return 0.5
    
    @staticmethod
    def _analyze_momentum(data: pd.DataFrame, signal_type: str) -> float:
        """Analyze momentum indicators"""
        try:
            if len(data) < 14:
                return 0.5
            
            # RSI calculation
            delta = data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            momentum_score = 0.5  # Base score
            
            if signal_type == 'BUY':
                if 30 <= current_rsi <= 50:
                    momentum_score += 0.3  # Good RSI for buying
                elif current_rsi < 30:
                    momentum_score += 0.4  # Oversold, good for reversal
                elif current_rsi > 70:
                    momentum_score -= 0.3  # Overbought, risky for buying
                    
            else:  # SELL
                if 50 <= current_rsi <= 70:
                    momentum_score += 0.3  # Good RSI for selling
                elif current_rsi > 70:
                    momentum_score += 0.4  # Overbought, good for selling
                elif current_rsi < 30:
                    momentum_score -= 0.3  # Oversold, risky for selling
            
            return max(0.1, min(1.0, momentum_score))
            
        except:
            return 0.5
    
    @staticmethod
    def _analyze_volatility(data: pd.DataFrame) -> float:
        """Analyze volatility for optimal trading conditions"""
        try:
            if len(data) < 20:
                return 0.5
            
            # Calculate volatility metrics
            returns = data['close'].pct_change().dropna()
            volatility = returns.rolling(window=20).std().iloc[-1]
            
            # Optimal volatility range for trading
            if 0.005 <= volatility <= 0.02:  # Good volatility range
                vol_score = 0.8
            elif volatility < 0.005:  # Too low volatility
                vol_score = 0.4
            elif volatility > 0.05:  # Too high volatility
                vol_score = 0.3
            else:
                vol_score = 0.6
            
            return vol_score
            
        except:
            return 0.5
    
    @staticmethod
    def _analyze_support_resistance(data: pd.DataFrame, signal_type: str) -> float:
        """Analyze support and resistance levels"""
        try:
            if len(data) < 20:
                return 0.5
            
            current_price = data['close'].iloc[-1]
            
            # Calculate support and resistance levels
            highs = data['high'].rolling(window=20).max()
            lows = data['low'].rolling(window=20).min()
            
            recent_high = highs.iloc[-1]
            recent_low = lows.iloc[-1]
            
            if recent_high == recent_low:
                return 0.5
            
            # Calculate price position within range
            price_position = (current_price - recent_low) / (recent_high - recent_low)
            
            if signal_type == 'BUY':
                if price_position < 0.3:  # Near support
                    return 0.8
                elif price_position < 0.5:  # Below middle
                    return 0.6
                else:  # Near resistance
                    return 0.3
            else:  # SELL
                if price_position > 0.7:  # Near resistance
                    return 0.8
                elif price_position > 0.5:  # Above middle
                    return 0.6
                else:  # Near support
                    return 0.3
                    
        except:
            return 0.5
    
    @staticmethod
    def _analyze_volume(data: pd.DataFrame, signal_type: str) -> float:
        """Analyze volume confirmation"""
        try:
            if 'tick_volume' not in data.columns or len(data) < 20:
                return 0.6  # Neutral if no volume data
            
            recent_volume = data['tick_volume'].iloc[-5:].mean()
            avg_volume = data['tick_volume'].iloc[-50:].mean()
            
            if avg_volume <= 0:
                return 0.6
            
            volume_ratio = recent_volume / avg_volume
            
            if volume_ratio > 1.5:  # High volume confirmation
                return 0.9
            elif volume_ratio > 1.2:  # Good volume
                return 0.7
            elif volume_ratio > 0.8:  # Average volume
                return 0.6
            else:  # Low volume
                return 0.4
                
        except:
            return 0.6
    
    @staticmethod
    def _analyze_price_action(data: pd.DataFrame, signal_type: str) -> float:
        """Analyze recent price action patterns"""
        try:
            if len(data) < 10:
                return 0.5
            
            recent_closes = data['close'].tail(5).values
            
            # Analyze candle patterns and momentum
            if signal_type == 'BUY':
                # Look for bullish patterns
                bullish_candles = sum(1 for i in range(1, len(recent_closes)) 
                                    if recent_closes[i] > recent_closes[i-1])
                pattern_strength = bullish_candles / (len(recent_closes) - 1)
                return 0.3 + (pattern_strength * 0.6)  # Range: 0.3 to 0.9
                    
            else:  # SELL
                # Look for bearish patterns
                bearish_candles = sum(1 for i in range(1, len(recent_closes)) 
                                    if recent_closes[i] < recent_closes[i-1])
                pattern_strength = bearish_candles / (len(recent_closes) - 1)
                return 0.3 + (pattern_strength * 0.6)  # Range: 0.3 to 0.9
            
        except:
            return 0.5
    
    @staticmethod
    def _get_symbol_multiplier(symbol: str) -> float:
        """Get symbol-specific confidence multiplier"""
        try:
            # Major pairs are generally more predictable
            if symbol in ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF']:
                return 1.1
            # JPY pairs have different characteristics
            elif 'JPY' in symbol:
                return 1.05
            # GBP pairs are more volatile
            elif 'GBP' in symbol and symbol != 'GBPUSD':
                return 0.95
            # Exotic pairs are less predictable
            else:
                return 0.9
        except:
            return 1.0

# ============================================================================
# PROFESSIONAL KELLY POSITION SIZING SYSTEM
# ============================================================================

class ProfessionalKellyPositionSizer:
    """Professional Kelly Criterion Position Sizing with Dynamic Risk Management"""
    
    def __init__(self, logger: SafeLogger, config: ProfessionalTradingConfig):
        self.logger = logger
        self.config = config
        self.trade_history = deque(maxlen=config.kelly_lookback_trades)
        self.performance_metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'win_rate': 0.5,  # Default conservative win rate
            'kelly_fraction': 0.1  # Conservative default
        }
        
        # Initialize Kelly components if available
        if KELLY_POSITION_SIZING_AVAILABLE:
            try:
                self.kelly_sizer = KellyPositionSizer()
                self.portfolio_manager = PortfolioRiskManager()
                self.kelly_available = True
                self.logger.info(f"{EMOJIS['kelly']} Professional Kelly Position Sizing initialized")
            except Exception as e:
                self.kelly_available = False
                self.logger.warning(f"{EMOJIS['warning']} Kelly sizer initialization failed: {e}")
        else:
            self.kelly_available = False
            self.logger.warning(f"{EMOJIS['warning']} Kelly Position Sizing not available, using advanced dynamic sizing")
    
    def calculate_professional_position_size(self, signal: Dict[str, Any], account_balance: float) -> float:
        """
        Calculate professional position size using Kelly Criterion or advanced dynamic sizing
        Returns: Optimized position size in lots
        """
        try:
            # METHOD 1: Professional Kelly Criterion (if available and sufficient history)
            if self.kelly_available and len(self.trade_history) >= 20:
                kelly_size = self._calculate_kelly_position_size(signal, account_balance)
                self.logger.info(f"{EMOJIS['kelly']} Kelly Position Size: {kelly_size:.4f} lots for {signal.get('symbol', 'N/A')} "
                               f"(Conf: {signal.get('confidence', 0.0):.3f})")
                return kelly_size
            
            # METHOD 2: Advanced Dynamic Position Sizing (fallback or primary method)
            else:
                dynamic_size = self._calculate_advanced_dynamic_size(signal, account_balance)
                method = "Advanced Dynamic" if not self.kelly_available else "Dynamic (insufficient history)"
                self.logger.info(f"{EMOJIS['kelly']} {method} Position Size: {dynamic_size:.4f} lots for {signal.get('symbol', 'N/A')} "
                               f"(Conf: {signal.get('confidence', 0.0):.3f})")
                return dynamic_size
                
        except Exception as e:
            self.logger.error(f"{EMOJIS['error']} Position sizing error: {e}")
            return self.config.base_position_size
    
    def _calculate_kelly_position_size(self, signal: Dict[str, Any], account_balance: float) -> float:
        """Calculate Kelly Criterion position size with professional risk management"""
        try:
            # Update performance metrics from trade history
            self._update_performance_metrics()
            
            # Get current performance statistics
            win_rate = self.performance_metrics['win_rate']
            avg_win = self.performance_metrics['avg_win']
            avg_loss = self.performance_metrics['avg_loss']
            
            # Calculate Kelly fraction: f = (bp - q) / b
            if avg_loss > 0:
                b_ratio = avg_win / avg_loss  # Win/loss ratio
                p = win_rate  # Win probability
                q = 1 - p     # Loss probability
                
                # Kelly formula
                kelly_fraction = (b_ratio * p - q) / b_ratio
            else:
                kelly_fraction = 0.1  # Conservative default
            
            # Apply safety constraints
            kelly_fraction = max(0.0, min(kelly_fraction, self.config.kelly_fraction))
            
            # Adjust by signal confidence
            confidence_mult = min(1.0, signal.get('confidence', 0.5) * 1.5)
            
            # Adjust by strategy count
            strategy_count = signal.get('strategy_count', 1)
            consensus_mult = min(1.2, 1.0 + (strategy_count - 1) * 0.1)
            
            # Calculate risk amount
            adjusted_kelly = kelly_fraction * confidence_mult * consensus_mult
            risk_amount = account_balance * adjusted_kelly
            
            # Convert to position size based on stop loss
            symbol = signal.get('symbol', 'EURUSD')
            if 'stop_loss' in signal and 'entry_price' in signal:
                pip_value = 0.0001 if 'JPY' not in symbol else 0.01
                stop_loss_pips = abs(signal['entry_price'] - signal['stop_loss']) / pip_value
                
                if stop_loss_pips > 0:
                    # Approximate position size calculation
                    position_size = risk_amount / (stop_loss_pips * 10)  # Assuming $10 per pip per lot
                else:
                    position_size = self.config.base_position_size
            else:
                position_size = self.config.base_position_size
            
            # Apply absolute limits
            position_size = max(self.config.min_kelly_size, min(self.config.max_kelly_size, position_size))
            
            return round(position_size, 4)
            
        except Exception as e:
            self.logger.error(f"{EMOJIS['error']} Kelly calculation error: {e}")
            return self.config.base_position_size
    
    def _calculate_advanced_dynamic_size(self, signal: Dict[str, Any], account_balance: float) -> float:
        """Advanced dynamic position sizing with professional risk management"""
        try:
            base_size = self.config.base_position_size
            
            # Confidence multiplier (validated confidence, not raw)
            confidence = signal.get('confidence', 0.5)
            confidence_mult = min(2.0, confidence * 2.5)
            
            # Strategy consensus multiplier
            strategy_count = signal.get('strategy_count', 1)
            consensus_mult = min(1.8, 1.0 + (strategy_count - 1) * 0.3)
            
            # Account balance multiplier (scale with account size)
            balance_mult = min(2.0, max(0.5, account_balance / 50000))
            
            # Calculate composite position size
            position_size = base_size * confidence_mult * consensus_mult * balance_mult
            
            # Apply risk-based maximum
            max_risk_amount = account_balance * self.config.max_risk_per_trade
            symbol = signal.get('symbol', 'EURUSD')
            
            if 'stop_loss' in signal and 'entry_price' in signal:
                pip_value = 0.0001 if 'JPY' not in symbol else 0.01
                stop_loss_pips = abs(signal['entry_price'] - signal['stop_loss']) / pip_value
                
                if stop_loss_pips > 0:
                    max_size_by_risk = max_risk_amount / (stop_loss_pips * 10)
                    position_size = min(position_size, max_size_by_risk)
            
            # Apply absolute limits
            position_size = max(0.001, min(self.config.max_kelly_size, position_size))
            
            return round(position_size, 4)
            
        except Exception as e:
            self.logger.error(f"{EMOJIS['error']} Advanced dynamic sizing error: {e}")
            return self.config.base_position_size
    
    def update_trade_result(self, trade_result: Dict[str, Any]):
        """Update trade history for Kelly calculation"""
        try:
            # Add trade result to history
            self.trade_history.append({
                'pnl': trade_result.get('pnl', 0.0),
                'win': trade_result.get('pnl', 0.0) > 0,
                'position_size': trade_result.get('position_size', 0.01),
                'timestamp': trade_result.get('timestamp', datetime.now())
            })
            
            # Update performance metrics
            self._update_performance_metrics()
            
        except Exception as e:
            self.logger.error(f"{EMOJIS['error']} Trade result update error: {e}")
    
    def _update_performance_metrics(self):
        """Update performance metrics from trade history"""
        try:
            if not self.trade_history:
                return
            
            wins = [t for t in self.trade_history if t['win']]
            losses = [t for t in self.trade_history if not t['win']]
            
            self.performance_metrics.update({
                'total_trades': len(self.trade_history),
                'winning_trades': len(wins),
                'losing_trades': len(losses),
                'total_pnl': sum(t['pnl'] for t in self.trade_history),
                'avg_win': np.mean([t['pnl'] for t in wins]) if wins else 0.02,
                'avg_loss': abs(np.mean([t['pnl'] for t in losses])) if losses else 0.01,
                'win_rate': len(wins) / len(self.trade_history) if self.trade_history else 0.5
            })
            
        except Exception as e:
            self.logger.error(f"{EMOJIS['error']} Performance metrics update error: {e}")

# ============================================================================
# SECURE CONFIGURATION LOADER - ENHANCED
# ============================================================================

def load_secure_config(config_path: str = "config.yaml") -> ProfessionalTradingConfig:
    """ENHANCED: Load secure configuration with professional features"""
    try:
        config_file = Path(config_path)
        
        # Load YAML config (non-sensitive settings only)
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f) or {}
                    print(f"{EMOJIS['success']} Configuration loaded from {config_file}")
            except yaml.YAMLError as e:
                print(f"{EMOJIS['error']} YAML parsing error: {e}")
                config_data = {}
            except Exception as e:
                print(f"{EMOJIS['error']} Config loading error: {e}")
                config_data = {}
        else:
            config_data = {}
            create_secure_default_config(config_path)
        
        # Safe conversion functions
        def safe_int(value, default=0):
            if value is None:
                return default
            try:
                return int(value)
            except (ValueError, TypeError):
                return default
        
        def safe_float(value, default=0.0):
            if value is None:
                return default
            try:
                return float(value)
            except (ValueError, TypeError):
                return default
        
        def safe_list(value, default=None):
            if default is None:
                default = []
            if value is None:
                return default
            if isinstance(value, list):
                return value
            return default
        
        def safe_bool(value, default=True):
            if value is None:
                return default
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ['true', '1', 'yes', 'on']
            return default
        
        # SECURITY: MT5 credentials from config/.env ONLY
        mt5_login = safe_int(os.getenv('MT5_LOGIN'), 0)
        mt5_password = os.getenv('MT5_PASSWORD', '')
        mt5_server = os.getenv('MT5_SERVER', '')
        mt5_path = os.getenv('MT5_PATH', '')
        
        # Create professional config
        config = ProfessionalTradingConfig(
            # SECURE: Credentials from config/.env only
            mt5_login=mt5_login,
            mt5_password=mt5_password,
            mt5_server=mt5_server,
            mt5_path=mt5_path,
            
            # Trading Parameters
            symbols=safe_list(config_data.get('symbols'), ["EURUSD", "GBPUSD", "USDJPY"]),
            timeframes=safe_list(config_data.get('timeframes'), ["M15", "H1", "H4"]),
            max_positions=safe_int(config_data.get('max_positions'), 5),
            base_position_size=safe_float(config_data.get('base_position_size'), 0.01),
            
            # Professional Risk Management
            max_risk_per_trade=safe_float(config_data.get('max_risk_per_trade'), 0.02),
            max_daily_loss=safe_float(config_data.get('max_daily_loss'), 0.05),
            stop_loss_pips=safe_int(config_data.get('stop_loss_pips'), 50),
            take_profit_pips=safe_int(config_data.get('take_profit_pips'), 100),
            min_signal_confidence=safe_float(config_data.get('min_signal_confidence'), 0.4),
            min_validation_score=safe_float(config_data.get('min_validation_score'), 0.3),
            min_risk_reward_ratio=safe_float(config_data.get('min_risk_reward_ratio'), 1.5),
            
            # Kelly Position Sizing
            kelly_enabled=safe_bool(config_data.get('kelly_enabled'), True),
            kelly_fraction=safe_float(config_data.get('kelly_fraction'), 0.25),
            max_kelly_size=safe_float(config_data.get('max_kelly_size'), 0.1),
            min_kelly_size=safe_float(config_data.get('min_kelly_size'), 0.001),
            kelly_lookback_trades=safe_int(config_data.get('kelly_lookback_trades'), 50),
            
            # Professional Signal Validation
            enable_signal_validation=safe_bool(config_data.get('enable_signal_validation'), True),
            enable_ml_validation=safe_bool(config_data.get('enable_ml_validation'), True),
            enable_market_condition_check=safe_bool(config_data.get('enable_market_condition_check'), True),
            signal_consensus_required=safe_int(config_data.get('signal_consensus_required'), 2),
            max_signal_age_minutes=safe_int(config_data.get('max_signal_age_minutes'), 5),
            quality_filter_enabled=safe_bool(config_data.get('quality_filter_enabled'), True),
            
            # Strategy Configuration
            strategy_weights=config_data.get('strategy_weights', {}),
            enabled_strategies=safe_list(config_data.get('enabled_strategies')),
            
            # Signal Factory Configuration
            signal_factory_enabled=safe_bool(config_data.get('signal_factory_enabled'), True),
            advanced_signal_factory_enabled=safe_bool(config_data.get('advanced_signal_factory_enabled'), True),
            signal_processing_interval=safe_int(config_data.get('signal_processing_interval'), 2),
            signal_aggregation_method=config_data.get('signal_aggregation_method', 'weighted_consensus'),
            
            # Advanced Signal Factory Settings (FIXED)
            advanced_factory_config=config_data.get('advanced_factory_config', {
                'min_confidence_threshold': 0.25,
                'high_confidence_threshold': 0.7,
                'enable_signal_aggregation': True,
                'enable_quality_filtering': True,
                'max_workers': 8,
                'timeframe_validation': True,
                'handle_timeframe_errors': True
            }),
            
            # System Configuration
            trading_mode=TradingMode(config_data.get('trading_mode', 'demo')),
            log_level=config_data.get('log_level', 'INFO'),
            signal_processing_interval_legacy=safe_int(config_data.get('signal_processing_interval_legacy'), 5)
        )
        
        # Log security status
        credentials_status = "SECURE (config/.env)" if all([mt5_login, mt5_password, mt5_server]) else "MISSING"
        print(f"{EMOJIS['security']} MT5 credentials status: {credentials_status}")
        
        return config
        
    except Exception as e:
        print(f"Error loading secure config: {e}, using defaults")
        return ProfessionalTradingConfig()

def create_secure_default_config(config_path: str):
    """Create default professional configuration WITHOUT sensitive data"""
    try:
        professional_config = {
            # NO MT5 CREDENTIALS - These go in config/.env file only
            'symbols': ["EURUSD", "GBPUSD", "USDJPY"],
            'timeframes': ["M15", "H1", "H4"],
            'max_positions': 5,
            'base_position_size': 0.01,
            
            # Professional Risk Management
            'max_risk_per_trade': 0.02,
            'max_daily_loss': 0.05,
            'stop_loss_pips': 50,
            'take_profit_pips': 100,
            'min_signal_confidence': 0.4,
            'min_validation_score': 0.3,
            'min_risk_reward_ratio': 1.5,
            
            # Kelly Position Sizing
            'kelly_enabled': True,
            'kelly_fraction': 0.25,
            'max_kelly_size': 0.1,
            'min_kelly_size': 0.001,
            'kelly_lookback_trades': 50,
            
            # Professional Signal Validation
            'enable_signal_validation': True,
            'enable_ml_validation': True,
            'enable_market_condition_check': True,
            'signal_consensus_required': 2,
            'max_signal_age_minutes': 5,
            'quality_filter_enabled': True,
            
            # Strategy Configuration
            'strategy_weights': {},
            'enabled_strategies': [],
            
            # Signal Factory
            'signal_aggregation_method': 'weighted_consensus',
            'signal_factory_enabled': True,
            'advanced_signal_factory_enabled': True,
            'signal_processing_interval': 2,
            
            # Advanced Signal Factory Settings (FIXED)
            'advanced_factory_config': {
                'min_confidence_threshold': 0.25,
                'high_confidence_threshold': 0.7,
                'enable_signal_aggregation': True,
                'enable_quality_filtering': True,
                'max_workers': 8,
                'timeframe_validation': True,
                'handle_timeframe_errors': True
            },
            
            # System Configuration
            'trading_mode': 'demo',  # Default to demo for safety
            'log_level': 'INFO',
            'signal_processing_interval_legacy': 5
        }
        
        os.makedirs(os.path.dirname(config_path) if os.path.dirname(config_path) else '.', exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(professional_config, f, default_flow_style=False, sort_keys=False)
        
        print(f"Created professional config: {config_path}")
        print("SECURITY: MT5 credentials must be in config/.env file!")
        
    except Exception as e:
        print(f"Error creating professional config: {e}")

# ============================================================================
# ENHANCED SIGNAL PROCESSOR WITH ULTIMATE FIXED ADVANCED FACTORY
# ============================================================================

class ProfessionalSignalProcessor:
    """Professional Signal Processor with ULTIMATE FIXED Advanced Signal Factory"""
    
    def __init__(self, logger: SafeLogger, config: ProfessionalTradingConfig):
        self.logger = logger
        self.config = config
        self.signal_history = deque(maxlen=10000)
        
        # Initialize Advanced Signal Factory (ULTIMATE FIXED)
        if ADVANCED_SIGNAL_FACTORY_AVAILABLE and config.advanced_signal_factory_enabled:
            try:
                self.advanced_signal_factory = get_signal_factory(config.advanced_factory_config)
                self.advanced_factory_enabled = True
                self.logger.info(f"{EMOJIS['factory']} Advanced Signal Factory initialized successfully")
                
                # Auto-discover and load strategies with error handling
                strategy_count = self.advanced_signal_factory.auto_discover_strategies("strategies")
                self.logger.info(f"{EMOJIS['factory']} Advanced Factory loaded {strategy_count} strategies")
                
            except Exception as e:
                self.logger.error(f"{EMOJIS['error']} Advanced Signal Factory initialization failed: {e}")
                self.advanced_signal_factory = None
                self.advanced_factory_enabled = False
        else:
            self.advanced_signal_factory = None
            self.advanced_factory_enabled = False
        
        # Performance tracking
        self.advanced_factory_signals = 0
        self.direct_strategy_signals = 0
        self.validated_signals = 0
        self.rejected_signals = 0
    
    def process_strategy_signals(self, strategies: Dict[str, Any], 
                               market_data: Dict[str, Dict[str, pd.DataFrame]]) -> List[Dict[str, Any]]:
        """
        PROFESSIONAL: Process strategy signals with ULTIMATE FIXED Advanced Factory
        """
        try:
            mode_str = "DEMO" if self.config.trading_mode == TradingMode.DEMO else "LIVE"
            self.logger.info(f"{EMOJIS['process']} Starting PROFESSIONAL signal processing for {mode_str} trading")
            self.logger.info(f"Processing {len(strategies)} strategies with market data for {len(market_data)} symbols")
            
            all_signals = []
            
            # STAGE 1: ULTIMATE FIXED Advanced Signal Factory Processing
            if self.advanced_factory_enabled:
                factory_signals = self._process_with_fixed_advanced_factory(market_data)
                if factory_signals:
                    all_signals.extend(factory_signals)
                    self.advanced_factory_signals += len(factory_signals)
                    self.logger.info(f"{EMOJIS['factory']} ULTIMATE FIXED Advanced Factory generated {len(factory_signals)} signals")
            
            # STAGE 2: Direct Strategy Processing with REAL Confidence
            direct_signals = self._process_strategies_with_real_confidence(strategies, market_data)
            all_signals.extend(direct_signals)
            self.direct_strategy_signals += len(direct_signals)
            
            self.logger.info(f"{EMOJIS['success']} Generated {len(all_signals)} professional trading signals")
            return all_signals
            
        except Exception as e:
            self.logger.error(f"{EMOJIS['error']} Critical error in professional signal processing: {e}")
            return []
    
    def _process_with_fixed_advanced_factory(self, market_data: Dict[str, Dict[str, pd.DataFrame]]) -> List[Dict[str, Any]]:
        """ULTIMATE FIXED: Advanced Signal Factory processing with complete timeframe error resolution"""
        try:
            if not self.advanced_signal_factory:
                return []
            
            self.logger.info(f"{EMOJIS['fixed']} Processing with ULTIMATE FIXED Advanced Signal Factory...")
            
            # ULTIMATE FIX: Convert DataFrame objects to proper format with TimeframeDataWrapper
            formatted_data = {}
            for symbol, timeframe_data in market_data.items():
                try:
                    if isinstance(timeframe_data, dict) and timeframe_data:
                        symbol_data = {}
                        for tf, df in timeframe_data.items():
                            if isinstance(df, pd.DataFrame) and not df.empty:
                                # ULTIMATE FIX: Create a wrapper object instead of modifying DataFrame
                                class TimeframeDataWrapper:
                                    def __init__(self, dataframe, timeframe):
                                        self.data = dataframe
                                        self.timeframe = timeframe
                                        # Copy all DataFrame attributes
                                        for attr in ['close', 'high', 'low', 'open', 'tick_volume']:
                                            if attr in dataframe.columns:
                                                setattr(self, attr, dataframe[attr])
                                    
                                    def __getitem__(self, key):
                                        return self.data[key]
                                    
                                    def __len__(self):
                                        return len(self.data)
                                    
                                    @property
                                    def iloc(self):
                                        return self.data.iloc
                                    
                                    @property
                                    def columns(self):
                                        return self.data.columns
                                    
                                    @property
                                    def index(self):
                                        return self.data.index
                                    
                                    def rolling(self, *args, **kwargs):
                                        return self.data.rolling(*args, **kwargs)
                                    
                                    def mean(self, *args, **kwargs):
                                        return self.data.mean(*args, **kwargs)
                                    
                                    @property
                                    def empty(self):
                                        return self.data.empty
                                    
                                    def __getattr__(self, name):
                                        # Delegate any other attribute access to the underlying DataFrame
                                        return getattr(self.data, name)
                                    
                                    def copy(self):
                                        return TimeframeDataWrapper(self.data.copy(), self.timeframe)
                                
                                wrapped_df = TimeframeDataWrapper(df, tf)
                                symbol_data[tf] = wrapped_df
                        
                        if symbol_data:
                            formatted_data[symbol] = symbol_data
                            
                    elif isinstance(timeframe_data, pd.DataFrame) and not timeframe_data.empty:
                        # Single timeframe data
                        primary_tf = self.config.timeframes[0] if self.config.timeframes else 'H1'
                        
                        class TimeframeDataWrapper:
                            def __init__(self, dataframe, timeframe):
                                self.data = dataframe
                                self.timeframe = timeframe
                                for attr in ['close', 'high', 'low', 'open', 'tick_volume']:
                                    if attr in dataframe.columns:
                                        setattr(self, attr, dataframe[attr])
                            
                            def __getitem__(self, key):
                                return self.data[key]
                            
                            def __len__(self):
                                return len(self.data)
                            
                            @property
                            def iloc(self):
                                return self.data.iloc
                            
                            @property
                            def columns(self):
                                return self.data.columns
                            
                            @property
                            def index(self):
                                return self.data.index
                            
                            def rolling(self, *args, **kwargs):
                                return self.data.rolling(*args, **kwargs)
                            
                            def mean(self, *args, **kwargs):
                                return self.data.mean(*args, **kwargs)
                            
                            @property
                            def empty(self):
                                return self.data.empty
                            
                            def __getattr__(self, name):
                                return getattr(self.data, name)
                            
                            def copy(self):
                                return TimeframeDataWrapper(self.data.copy(), self.timeframe)
                        
                        wrapped_df = TimeframeDataWrapper(timeframe_data, primary_tf)
                        formatted_data[symbol] = {primary_tf: wrapped_df}
                        
                except Exception as e:
                    self.logger.warning(f"{EMOJIS['warning']} Error formatting data for {symbol}: {e}")
                    continue
            
            if not formatted_data:
                self.logger.warning(f"{EMOJIS['warning']} No properly formatted data for Advanced Factory")
                return []
            
            # Process through advanced factory with enhanced error handling
            try:
                self.logger.info(f"{EMOJIS['factory']} Calling ULTIMATE FIXED Advanced Factory with {len(formatted_data)} symbols")
                processed_signals = process_market_data_for_main_py(formatted_data)
            except Exception as e:
                self.logger.error(f"{EMOJIS['error']} Advanced Factory processing error: {e}")
                self.logger.error(f"Error traceback: {traceback.format_exc()}")
                return []
            
            if not processed_signals:
                self.logger.info(f"{EMOJIS['factory']} Advanced factory returned no signals")
                return []
            
            # Convert advanced factory signals with enhanced validation
            converted_signals = []
            for signal_dict in processed_signals:
                try:
                    symbol = signal_dict.get('symbol', '')
                    final_signal = signal_dict.get('final_signal', 'HOLD')
                    confidence = signal_dict.get('combined_confidence', 0.0)
                    entry_price = signal_dict.get('entry_price', 0.0)
                    
                    # Enhanced signal validation
                    if (symbol and final_signal in ['BUY', 'SELL'] and 
                        0.2 <= confidence <= 0.95 and entry_price > 0):
                        
                        # Determine timeframe safely
                        timeframe = signal_dict.get('timeframe', 'H1')
                        if not timeframe or not isinstance(timeframe, str):
                            timeframe = self.config.timeframes[0] if self.config.timeframes else 'H1'
                        
                        converted_signal = {
                            'symbol': symbol,
                            'direction': 'bullish' if final_signal in ['BUY', 'STRONG_BUY'] else 'bearish',
                            'signal_type': final_signal,
                            'strength': confidence,
                            'confidence': confidence,
                            'level': entry_price,
                            'entry_price': entry_price,
                            'stop_loss': signal_dict.get('stop_loss'),
                            'take_profit': signal_dict.get('take_profit'),
                            'contributing_strategies': signal_dict.get('contributing_strategies', []),
                            'timeframes': [timeframe],
                            'strategy_count': signal_dict.get('strategy_count', 1),
                            'factory_processed': True,
                            'advanced_factory_processed': True,
                            'signal_id': f"FIXED_ADV_{symbol}_{int(time.time())}_{len(converted_signals)}",
                            'timestamp': datetime.now(),
                            'reason': f"ULTIMATE FIXED Advanced Factory: {signal_dict.get('strategy_count', 1)} strategies consensus",
                            'metadata': {
                                'fixed_advanced_factory': True,
                                'timeframe_wrapper_used': True,
                                'original_data': signal_dict
                            }
                        }
                        
                        converted_signals.append(converted_signal)
                        self.logger.info(f"  {EMOJIS['success']} ULTIMATE FIXED Advanced: {symbol} {final_signal} (conf: {confidence:.3f})")
                
                except Exception as e:
                    self.logger.error(f"{EMOJIS['error']} Error converting ULTIMATE FIXED advanced factory signal: {e}")
                    continue
            
            self.logger.info(f"{EMOJIS['fixed']} ULTIMATE FIXED Advanced Factory conversion complete: {len(converted_signals)} signals")
            return converted_signals
            
        except Exception as e:
            self.logger.error(f"{EMOJIS['error']} Critical error in ULTIMATE FIXED advanced factory processing: {e}")
            self.logger.error(f"Critical traceback: {traceback.format_exc()}")
            return []
    
    def _process_strategies_with_real_confidence(self, strategies: Dict[str, Any], 
                                               market_data: Dict[str, Dict[str, pd.DataFrame]]) -> List[Dict[str, Any]]:
        """Process strategies with ALWAYS REAL confidence calculation (fixes fake 0.95 issue)"""
        try:
            all_signals = []
            
            for strategy_name, strategy in strategies.items():
                try:
                    # Prepare data for strategy
                    strategy_data = self._prepare_market_data_for_strategy(strategy, market_data)
                    
                    if not strategy_data:
                        continue
                    
                    # Process each symbol with ALWAYS REAL confidence calculation
                    for symbol, data in strategy_data.items():
                        if isinstance(data, pd.DataFrame) and not data.empty and len(data) >= 20:
                            try:
                                # Get basic analysis from strategy
                                if hasattr(strategy, 'analyze'):
                                    analysis = strategy.analyze(data, symbol)
                                else:
                                    continue
                                
                                if not analysis or not isinstance(analysis, dict):
                                    continue
                                
                                signal_type = analysis.get('signal', 'HOLD')
                                raw_confidence = analysis.get('confidence', 0.0)
                                
                                # ALWAYS calculate real confidence - never trust strategy confidence
                                real_confidence = RealSignalConfidenceCalculator.calculate_real_confidence(
                                    data, signal_type, analysis, symbol
                                )
                                
                                if raw_confidence >= 0.94:  # Detect fake confidence
                                    self.logger.info(f"  {EMOJIS['confidence']} FAKE confidence fixed: {strategy_name} -> {symbol} "
                                                   f"(fake: {raw_confidence:.2f} → real: {real_confidence:.3f})")
                                
                                confidence = real_confidence  # Always use calculated confidence
                                price = analysis.get('price', data['close'].iloc[-1])
                                
                                # Only process signals with realistic confidence and valid prices
                                if (signal_type in ['BUY', 'SELL'] and 
                                    0.15 <= confidence <= 0.90 and
                                    price > 0 and price != 1.0):
                                    
                                    signal_dict = {
                                        'symbol': symbol,
                                        'direction': 'bullish' if signal_type == 'BUY' else 'bearish',
                                        'signal_type': signal_type,
                                        'strength': confidence,
                                        'confidence': confidence,  # Use real confidence
                                        'level': price,
                                        'entry_price': price,
                                        'stop_loss': analysis.get('stop_loss'),
                                        'take_profit': analysis.get('take_profit'),
                                        'strategy_name': strategy_name,
                                        'contributing_strategies': [strategy_name],
                                        'timeframes': [self._determine_timeframe(symbol, market_data)],
                                        'strategy_count': 1,
                                        'factory_processed': False,
                                        'advanced_factory_processed': False,
                                        'signal_id': f"REAL_{symbol}_{int(time.time())}_{len(all_signals)}",
                                        'timestamp': datetime.now(),
                                        'reason': analysis.get('reason', ''),
                                        'metadata': {
                                            'original_confidence': raw_confidence,
                                            'real_confidence_calculated': True,
                                            'confidence_method': 'calculated'
                                        }
                                    }
                                    
                                    all_signals.append(signal_dict)
                                    self.logger.info(f"  {EMOJIS['success']} REAL: {strategy_name} -> {symbol} {signal_type} "
                                                   f"(conf: {confidence:.3f}) [CALCULATED]")
                                        
                            except Exception as e:
                                self.logger.error(f"Error in REAL analysis for {strategy_name} -> {symbol}: {e}")
                
                except Exception as e:
                    self.logger.error(f"Error processing strategy {strategy_name}: {e}")
                    continue
            
            self.logger.info(f"{EMOJIS['success']} REAL processing generated {len(all_signals)} signals with CALCULATED confidence")
            return all_signals
            
        except Exception as e:
            self.logger.error(f"{EMOJIS['error']} Error in REAL strategy processing: {e}")
            return []
    
    def _prepare_market_data_for_strategy(self, strategy, market_data: Dict[str, Dict[str, pd.DataFrame]]) -> Dict[str, pd.DataFrame]:
        """Prepare market data for strategy analysis"""
        try:
            prepared_data = {}
            
            for symbol, timeframe_data in market_data.items():
                if isinstance(timeframe_data, dict) and timeframe_data:
                    primary_tf = self.config.timeframes[0] if self.config.timeframes else 'H1'
                    if primary_tf in timeframe_data:
                        df = timeframe_data[primary_tf]
                    else:
                        df = next(iter(timeframe_data.values()))
                    
                    if isinstance(df, pd.DataFrame) and not df.empty and len(df) >= 20:
                        prepared_data[symbol] = df
                elif isinstance(timeframe_data, pd.DataFrame) and not timeframe_data.empty:
                    prepared_data[symbol] = timeframe_data
            
            return prepared_data
            
        except Exception as e:
            self.logger.error(f"{EMOJIS['error']} Error preparing market data: {e}")
            return {}
    
    def _determine_timeframe(self, symbol: str, market_data: Dict[str, Dict[str, pd.DataFrame]]) -> str:
        """Determine timeframe for symbol"""
        try:
            if symbol in market_data and isinstance(market_data[symbol], dict):
                return next(iter(market_data[symbol].keys()))
            return self.config.timeframes[0] if self.config.timeframes else "H1"
        except:
            return "H1"

# ============================================================================
# RISK MANAGER - ENHANCED WITH PROFESSIONAL FEATURES
# ============================================================================

class RiskManager:
    """Risk management system"""
    
    def __init__(self, logger: SafeLogger, config: ProfessionalTradingConfig):
        self.logger = logger
        self.config = config
        self.daily_pnl = 0.0
        self.open_positions = 0
        self.daily_trades = 0
        self.last_reset_date = datetime.now().date()
        self.max_daily_loss_reached = False
        
    def can_open_trade(self, signal: Dict[str, Any], account_balance: float) -> Tuple[bool, str]:
        """Risk check for trading"""
        try:
            # Reset daily counters if new day
            self._reset_daily_counters_if_needed()
            
            if self.max_daily_loss_reached:
                return False, "Daily loss limit reached - trading suspended"
            
            daily_loss_limit = account_balance * self.config.max_daily_loss
            if abs(self.daily_pnl) >= daily_loss_limit:
                self.max_daily_loss_reached = True
                return False, f"Daily loss limit reached: {self.daily_pnl:.2f}"
            
            if self.open_positions >= self.config.max_positions:
                return False, f"Maximum positions reached: {self.open_positions}/{self.config.max_positions}"
            
            if signal['strength'] < self.config.min_signal_confidence:
                return False, f"Signal strength too low: {signal['strength']:.2f}"
            
            mode_str = "DEMO" if self.config.trading_mode == TradingMode.DEMO else "LIVE"
            return True, f"{mode_str} trade approved"
            
        except Exception as e:
            self.logger.error(f"{EMOJIS['error']} Risk check error: {e}")
            return False, "Risk check failed"
    
    def _reset_daily_counters_if_needed(self):
        """Reset daily counters if new trading day"""
        current_date = datetime.now().date()
        if current_date > self.last_reset_date:
            self.daily_pnl = 0.0
            self.daily_trades = 0
            self.max_daily_loss_reached = False
            self.last_reset_date = current_date
            self.logger.info(f"{EMOJIS['check']} Daily risk counters reset: {current_date}")
    
    def update_daily_pnl(self, pnl_change: float):
        self.daily_pnl += pnl_change
        
    def add_position(self):
        self.open_positions += 1
        self.daily_trades += 1
        
    def remove_position(self):
        self.open_positions = max(0, self.open_positions - 1)

# ============================================================================
# SECURE MT5 MANAGER WITH FIXED TRADE EXECUTION
# ============================================================================

class SecureMT5Manager:
    """SECURE MT5 manager with config/.env credentials + FIXED TRADE EXECUTION"""
    
    def __init__(self, logger: SafeLogger, config: ProfessionalTradingConfig):
        self.logger = logger
        self.config = config
        self.connected = False
        self.account_info = None
        
    def connect(self) -> bool:
        """SECURE MT5 connection using config/.env credentials"""
        try:
            # SECURITY: Get credentials from environment variables (config/.env)
            mt5_login = int(os.getenv('MT5_LOGIN', self.config.mt5_login)) if os.getenv('MT5_LOGIN') else self.config.mt5_login
            mt5_password = os.getenv('MT5_PASSWORD', self.config.mt5_password)
            mt5_server = os.getenv('MT5_SERVER', self.config.mt5_server)
            mt5_path = os.getenv('MT5_PATH', self.config.mt5_path)
            
            # Validate credentials
            if not all([mt5_login, mt5_password, mt5_server]):
                self.logger.error(f"{EMOJIS['error']} CRITICAL: Missing MT5 credentials in config/.env file")
                self.logger.error("Required in config/.env file: MT5_LOGIN, MT5_PASSWORD, MT5_SERVER")
                return False
            
            # Initialize MT5
            if mt5_path:
                if not mt5.initialize(path=mt5_path):
                    self.logger.error(f"{EMOJIS['error']} MT5 initialization failed: {mt5.last_error()}")
                    return False
            else:
                if not mt5.initialize():
                    self.logger.error(f"{EMOJIS['error']} MT5 initialization failed: {mt5.last_error()}")
                    return False
            
            # Login to MT5 account (LIVE or DEMO)
            if not mt5.login(
                login=mt5_login,
                password=mt5_password,
                server=mt5_server
            ):
                self.logger.error(f"{EMOJIS['error']} MT5 login failed: {mt5.last_error()}")
                mt5.shutdown()
                return False
            
            # Get account info
            self.account_info = mt5.account_info()
            if not self.account_info:
                self.logger.error(f"{EMOJIS['error']} Failed to get account info")
                return False
            
            self.connected = True
            
            # Determine if this is a demo or live account
            account_type = "DEMO" if "demo" in mt5_server.lower() else "LIVE"
            mode_emoji = EMOJIS['demo'] if account_type == "DEMO" else EMOJIS['live']
            
            self.logger.info(f"{EMOJIS['success']} MT5 {account_type} connected - Account: {self.account_info.login}")
            self.logger.info(f"{EMOJIS['money']} {account_type} Balance: {self.account_info.balance:.2f} {self.account_info.currency}")
            self.logger.info(f"{EMOJIS['security']} Credentials loaded securely from config/.env file")
            
            return True
            
        except Exception as e:
            self.logger.error(f"{EMOJIS['error']} MT5 connection error: {e}")
            return False
    
    def get_market_data(self, symbol: str, timeframe: str, count: int = 500) -> pd.DataFrame:
        """Get market data from MT5"""
        try:
            if not self.connected:
                return pd.DataFrame()
            
            # Timeframe mapping
            tf_map = {
                'M1': mt5.TIMEFRAME_M1, 'M5': mt5.TIMEFRAME_M5,
                'M15': mt5.TIMEFRAME_M15, 'M30': mt5.TIMEFRAME_M30,
                'H1': mt5.TIMEFRAME_H1, 'H4': mt5.TIMEFRAME_H4,
                'D1': mt5.TIMEFRAME_D1, 'W1': mt5.TIMEFRAME_W1
            }
            
            mt5_timeframe = tf_map.get(timeframe, mt5.TIMEFRAME_H1)
            
            # Get rates
            rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, count)
            
            if rates is None or len(rates) == 0:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            
            return df
            
        except Exception as e:
            self.logger.error(f"{EMOJIS['error']} Error getting market data for {symbol}: {e}")
            return pd.DataFrame()
    
    def execute_trade(self, signal: Dict[str, Any], position_size: float) -> Optional[TradeExecution]:
        """COMPLETELY FIXED: Execute trade on MT5 - Works with ALL MT5 brokers"""
        try:
            if not self.connected:
                return None
            
            symbol = signal['symbol']
            direction = signal['direction']
            
            # Get current price
            tick = mt5.symbol_info_tick(symbol)
            if not tick:
                return None
            
            entry_price = tick.ask if direction == 'bullish' else tick.bid
            action = "BUY" if direction == 'bullish' else "SELL"
            
            # Calculate stop loss and take profit
            pip_value = 0.0001 if 'JPY' not in symbol else 0.01
            
            if direction == 'bullish':
                stop_loss = entry_price - (self.config.stop_loss_pips * pip_value)
                take_profit = entry_price + (self.config.take_profit_pips * pip_value)
            else:
                stop_loss = entry_price + (self.config.stop_loss_pips * pip_value)
                take_profit = entry_price - (self.config.take_profit_pips * pip_value)
            
            # Create trade execution record
            trade_execution = TradeExecution(
                symbol=symbol,
                action=action,
                volume=position_size,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                timestamp=datetime.now(),
                strategy_names=signal.get('contributing_strategies', ['Unknown']),
                timeframes=signal.get('timeframes', ['H1']),
                signal_strength=signal['strength'],
                signal_id=signal.get('signal_id', ''),
                factory_processed=signal.get('factory_processed', False),
                advanced_factory_processed=signal.get('advanced_factory_processed', False)
            )
            
            # CRITICAL FIX: Try multiple filling modes for compatibility
            account_type = "DEMO" if "demo" in self.account_info.server.lower() else "LIVE"
            comment = f"UltimateBot-{account_type}"
            
            # Try different filling modes in order of preference
            filling_modes = [
                mt5.ORDER_FILLING_FOK,     # Fill or Kill - most restrictive
                mt5.ORDER_FILLING_IOC,     # Immediate or Cancel - moderate
                mt5.ORDER_FILLING_RETURN   # Return (default) - most permissive
            ]
            
            for filling_mode in filling_modes:
                try:
                    request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": symbol,
                        "volume": position_size,
                        "type": mt5.ORDER_TYPE_BUY if action == "BUY" else mt5.ORDER_TYPE_SELL,
                        "price": entry_price,
                        "sl": stop_loss,
                        "tp": take_profit,
                        "deviation": 20,
                        "magic": 234000,
                        "comment": comment,
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": filling_mode,  # CRITICAL: Try different filling modes
                    }
                    
                    # Send order to MT5
                    result = mt5.order_send(request)
                    
                    if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                        # SUCCESS! Trade executed
                        trade_execution.ticket = result.order
                        trade_execution.status = "EXECUTED"
                        trade_execution.entry_price = result.price
                        
                        factory_tag = " [ULTIMATE-FIXED-ADV]" if trade_execution.advanced_factory_processed else " [DIRECT-REAL]"
                        
                        self.logger.info(f"{EMOJIS['trade']} {account_type} TRADE EXECUTED{factory_tag}: {action} {position_size} {symbol} @ {result.price:.5f}")
                        self.logger.info(f"   Ticket: {result.order} | SL: {stop_loss:.5f} | TP: {take_profit:.5f} | Filling: {filling_mode}")
                        
                        return trade_execution
                    
                    elif result and result.retcode in [mt5.TRADE_RETCODE_INVALID_FILL, mt5.TRADE_RETCODE_INVALID_ORDER]:
                        # This filling mode not supported, try next
                        self.logger.debug(f"Filling mode {filling_mode} not supported, trying next...")
                        continue
                    else:
                        # Other error, try next filling mode
                        error_msg = result.comment if result else f"Error code: {result.retcode if result else 'Unknown'}"
                        self.logger.debug(f"Trade failed with {filling_mode}: {error_msg}")
                        continue
                        
                except Exception as e:
                    # Exception with this filling mode, try next
                    self.logger.debug(f"Exception with filling mode {filling_mode}: {e}")
                    continue
            
            # If we reach here, all filling modes failed
            trade_execution.status = "FAILED"
            self.logger.error(f"{EMOJIS['error']} ALL FILLING MODES FAILED for {symbol}")
            return trade_execution
            
        except Exception as e:
            self.logger.error(f"{EMOJIS['error']} Trade execution error: {e}")
            return None
    
    def get_open_positions(self) -> List[Dict[str, Any]]:
        """Get current positions"""
        try:
            if not self.connected:
                return []
            
            positions = mt5.positions_get()
            if not positions:
                return []
            
            position_list = []
            for pos in positions:
                position_list.append({
                    'ticket': pos.ticket,
                    'symbol': pos.symbol,
                    'type': 'BUY' if pos.type == mt5.POSITION_TYPE_BUY else 'SELL',
                    'volume': pos.volume,
                    'price_open': pos.price_open,
                    'price_current': pos.price_current,
                    'profit': pos.profit,
                    'time': datetime.fromtimestamp(pos.time)
                })
            
            return position_list
            
        except Exception as e:
            self.logger.error(f"{EMOJIS['error']} Error getting positions: {e}")
            return []
    
    def disconnect(self):
        """Disconnect from MT5"""
        if self.connected:
            mt5.shutdown()
            self.connected = False
            self.logger.info(f"{EMOJIS['disconnect']} MT5 disconnected")

# ============================================================================
# STRATEGY DISCOVERER - COMPLETE IMPLEMENTATION
# ============================================================================

class StrategyDiscoverer:
    """Strategy discovery and loading system"""
    
    def __init__(self, logger: SafeLogger, config: ProfessionalTradingConfig):
        self.logger = logger
        self.config = config
        self.loaded_strategies: Dict[str, Any] = {}
        
    def discover_and_load_strategies(self, strategies_path: str = "strategies") -> Dict[str, Any]:
        """Discover and load all available strategies"""
        try:
            self.logger.info(f"{EMOJIS['rocket']} Loading strategies...")
            
            # Import ABC Bypass functions
            try:
                from strategies.base_strategy import (
                    get_registered_strategies, 
                    load_all_registered_strategies,
                    clear_registry
                )
                self.logger.info(f"{EMOJIS['success']} ABC Bypass system imported")
            except ImportError as e:
                self.logger.error(f"{EMOJIS['error']} Failed to import ABC Bypass: {e}")
                return self._fallback_strategy_loading(strategies_path)
            
            # Clear registry
            clear_registry()
            
            # Import strategy files
            strategies_dir = Path(strategies_path)
            if strategies_dir.exists():
                sys.path.insert(0, str(strategies_dir.parent.absolute()))
                
                for file_path in strategies_dir.glob("*_strategy.py"):
                    if file_path.stem.startswith("base_"):
                        continue
                    
                    try:
                        module_name = f"strategies.{file_path.stem}"
                        if module_name not in sys.modules:
                            importlib.import_module(module_name)
                    except Exception as e:
                        self.logger.error(f"Error importing {file_path}: {e}")
                        continue
            
            # Get registered strategies
            registered_strategies = get_registered_strategies()
            self.logger.info(f"{EMOJIS['info']} Found {len(registered_strategies)} registered strategies")
            
            # Load strategies
            strategy_config = {
                'enabled_strategies': self.config.enabled_strategies,
                'strategy_weights': self.config.strategy_weights,
                'strategy_configs': {},
            }
            
            loaded_strategies = load_all_registered_strategies(strategy_config)
            
            if not loaded_strategies:
                self.logger.warning(f"{EMOJIS['warning']} No strategies loaded, trying fallback...")
                return self._fallback_strategy_loading(strategies_path)
            
            self.loaded_strategies = loaded_strategies
            self.logger.info(f"{EMOJIS['success']} Loaded {len(loaded_strategies)} strategies")
            
            return loaded_strategies
            
        except Exception as e:
            self.logger.error(f"{EMOJIS['error']} Strategy loading failed: {e}")
            return self._fallback_strategy_loading(strategies_path)
    
    def _fallback_strategy_loading(self, strategies_path: str = "strategies") -> Dict[str, Any]:
        """Fallback strategy loading method"""
        try:
            self.logger.warning(f"{EMOJIS['warning']} Using fallback strategy loading...")
            
            strategies_dir = Path(strategies_path)
            if not strategies_dir.exists():
                return {}
            
            discovered_strategies = {}
            sys.path.insert(0, str(strategies_dir.parent.absolute()))
            
            for file_path in strategies_dir.glob("*_strategy.py"):
                if file_path.stem.startswith("base_"):
                    continue
                    
                try:
                    module_name = f"strategies.{file_path.stem}"
                    module = importlib.import_module(module_name)
                    
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if (name.endswith('Strategy') and 
                            not name.startswith('Base')):
                            
                            try:
                                if (self.config.enabled_strategies and 
                                    name not in self.config.enabled_strategies):
                                    continue
                                
                                strategy_instance = self._instantiate_strategy(obj, name)
                                if strategy_instance:
                                    discovered_strategies[name] = strategy_instance
                                    self.logger.info(f"{EMOJIS['success']} Loaded (fallback): {name}")
                                
                            except Exception as e:
                                self.logger.error(f"Failed to instantiate {name}: {e}")
                                
                except Exception as e:
                    self.logger.error(f"Error loading {file_path}: {e}")
                    continue
            
            return discovered_strategies
            
        except Exception as e:
            self.logger.error(f"{EMOJIS['error']} Fallback strategy loading failed: {e}")
            return {}
    
    def _instantiate_strategy(self, strategy_class, name: str):
        """Try to instantiate strategy with various parameter combinations"""
        try:
            return strategy_class(name, {})
        except TypeError:
            try:
                return strategy_class(name)
            except TypeError:
                try:
                    instance = strategy_class()
                    if hasattr(instance, 'name'):
                        instance.name = name
                    return instance
                except Exception as e:
                    self.logger.error(f"Failed to instantiate {name}: {e}")
                    return None

# ============================================================================
# ULTIMATE PROFESSIONAL TRADING ORCHESTRATOR
# ============================================================================

class UltimateProfessionalTradingOrchestrator:
    """Ultimate Professional Trading Orchestrator with all fixes applied"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        
        # Load professional config first
        self.config = load_secure_config(config_path)
        
        # Create professional logger
        self.logger = SafeLogger("UltimateProfessionalTradingBot", self.config.log_level)
        
        # Initialize ULTIMATE professional components
        self.strategy_discoverer = StrategyDiscoverer(self.logger, self.config)
        self.signal_processor = ProfessionalSignalProcessor(self.logger, self.config)
        self.risk_manager = RiskManager(self.logger, self.config)
        self.mt5_manager = SecureMT5Manager(self.logger, self.config)
        self.position_sizer = ProfessionalKellyPositionSizer(self.logger, self.config)
        
        # System state
        self.running = False
        self.shutdown_event = threading.Event()
        self.strategies: Dict[str, Any] = {}
        self.metrics = SystemMetrics()
        self.active_trades: List[TradeExecution] = []
        self.start_time = datetime.now()
        
        self.logger.info(f"{EMOJIS['rocket']} ULTIMATE PROFESSIONAL Trading Orchestrator v2.2.2 initialized")
    
    def initialize(self) -> bool:
        """Initialize ULTIMATE professional trading system"""
        try:
            mode_str = "DEMO" if self.config.trading_mode == TradingMode.DEMO else "LIVE"
            self.logger.info(f"{EMOJIS['gear']} Initializing ULTIMATE PROFESSIONAL {mode_str} Trading System...")
            
            # Load strategies
            self.strategies = self.strategy_discoverer.discover_and_load_strategies()
            self.metrics.strategies_loaded = len(self.strategies)
            
            if not self.strategies:
                self.logger.error(f"{EMOJIS['error']} No strategies loaded")
                return False
            
            # Connect to MT5 (LIVE or DEMO)
            if not self.mt5_manager.connect():
                self.logger.error(f"{EMOJIS['error']} Failed to connect to MT5")
                return False
            
            # Log professional system status
            account_type = "DEMO" if "demo" in self.mt5_manager.account_info.server.lower() else "LIVE"
            mode_emoji = EMOJIS['demo'] if account_type == "DEMO" else EMOJIS['live']
            
            self.logger.info(f"{EMOJIS['success']} ULTIMATE PROFESSIONAL {account_type} Trading System initialized:")
            self.logger.info(f"   {mode_emoji} Mode: {account_type} TRADING")
            self.logger.info(f"   {EMOJIS['success']} MT5 Connected: {self.mt5_manager.account_info.login}")
            self.logger.info(f"   {EMOJIS['money']} Balance: {self.mt5_manager.account_info.balance:.2f}")
            self.logger.info(f"   {EMOJIS['gear']} Strategies: {self.metrics.strategies_loaded}")
            self.logger.info(f"   {EMOJIS['fixed']} Advanced Factory: {'ULTIMATE FIXED' if self.signal_processor.advanced_factory_enabled else 'DISABLED'}")
            self.logger.info(f"   {EMOJIS['kelly']} Kelly Position Sizing: {'ENABLED' if self.position_sizer.kelly_available else 'ADVANCED DYNAMIC'}")
            self.logger.info(f"   {EMOJIS['security']} Security: Credentials from config/.env file")
            
            return True
            
        except Exception as e:
            self.logger.error(f"{EMOJIS['error']} Ultimate professional trading system initialization failed: {e}")
            return False
    
    def run_trading_loop(self):
        """ULTIMATE professional trading loop with enhanced features"""
        try:
            account_type = "DEMO" if "demo" in self.mt5_manager.account_info.server.lower() else "LIVE"
            
            self.logger.info(f"{EMOJIS['target']} Starting ULTIMATE PROFESSIONAL {account_type} TRADING LOOP")
            self.running = True
            
            last_metrics_update = time.time()
            last_performance_log = time.time()
            
            while not self.shutdown_event.is_set():
                try:
                    # Fetch market data
                    market_data = self._fetch_market_data()
                    if not market_data:
                        time.sleep(self.config.signal_processing_interval_legacy)
                        continue
                    
                    # Process signals with ULTIMATE FIXED Advanced Factory
                    professional_signals = self.signal_processor.process_strategy_signals(self.strategies, market_data)
                    
                    # Update metrics
                    self.metrics.signals_generated += len(professional_signals)
                    self.metrics.advanced_factory_signals = self.signal_processor.advanced_factory_signals
                    
                    if professional_signals:
                        self.logger.info(f"{EMOJIS['signal']} Generated {len(professional_signals)} ULTIMATE PROFESSIONAL {account_type} signals")
                        
                        # Execute trades with professional risk management
                        for signal in professional_signals:
                            try:
                                success = self._execute_professional_trade(signal)
                                if success:
                                    self.metrics.trades_executed += 1
                                    self.metrics.successful_trades += 1
                                else:
                                    self.metrics.failed_trades += 1
                            except Exception as e:
                                self.logger.error(f"{EMOJIS['error']} Trade execution error: {e}")
                                self.metrics.failed_trades += 1
                    
                    # Monitor positions
                    self._monitor_positions()
                    
                    # Update metrics periodically
                    if time.time() - last_metrics_update > 60:
                        self._update_professional_metrics()
                        last_metrics_update = time.time()
                    
                    # Log performance summary periodically
                    if time.time() - last_performance_log > 300:  # Every 5 minutes
                        self._log_performance_summary()
                        last_performance_log = time.time()
                    
                    time.sleep(self.config.signal_processing_interval_legacy)
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self.logger.error(f"{EMOJIS['error']} Error in ULTIMATE professional trading loop: {e}")
                    time.sleep(10)
            
            self.running = False
            self.logger.info(f"{EMOJIS['stop']} ULTIMATE professional trading loop stopped")
            
        except Exception as e:
            self.logger.error(f"{EMOJIS['error']} Fatal error in ULTIMATE professional trading loop: {e}")
            self.running = False
    
    def _execute_professional_trade(self, signal: Dict[str, Any]) -> bool:
        """Execute trade with ULTIMATE professional risk management and position sizing"""
        try:
            if not self.mt5_manager.connected or not self.mt5_manager.account_info:
                return False
            
            account_balance = self.mt5_manager.account_info.balance
            
            # ULTIMATE professional risk management check
            can_trade, reason = self.risk_manager.can_open_trade(signal, account_balance)
            if not can_trade:
                self.logger.debug(f"{EMOJIS['check']} Trade rejected: {reason}")
                return False
            
            # ULTIMATE professional Kelly position sizing
            position_size = self.position_sizer.calculate_professional_position_size(signal, account_balance)
            
            # Execute trade with ULTIMATE FIXED MT5 execution
            trade_execution = self.mt5_manager.execute_trade(signal, position_size)
            
            if trade_execution and trade_execution.status == "EXECUTED":
                # Update risk manager
                self.risk_manager.add_position()
                self.active_trades.append(trade_execution)
                
                # Update position sizer with trade
                trade_result = {
                    'position_size': position_size,
                    'timestamp': datetime.now()
                }
                
                # Log ULTIMATE professional trade execution
                factory_tag = ""
                if signal.get('advanced_factory_processed'):
                    factory_tag = " [ULTIMATE-FIXED-ADV]"
                else:
                    factory_tag = " [DIRECT-REAL-CALC]"
                
                confidence = signal.get('confidence', 0.0)
                
                self.logger.info(f"{EMOJIS['trade']} ULTIMATE PROFESSIONAL TRADE EXECUTED{factory_tag}:")
                self.logger.info(f"   {trade_execution.action} {position_size:.4f} lots {trade_execution.symbol} @ {trade_execution.entry_price:.5f}")
                self.logger.info(f"   Confidence: {confidence:.3f} | Kelly Sizing: {'YES' if self.position_sizer.kelly_available else 'ADVANCED'}")
                self.logger.info(f"   Ticket: {trade_execution.ticket}")
                
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"{EMOJIS['error']} Error executing ULTIMATE professional trade: {e}")
            return False
    
    def _fetch_market_data(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        """Fetch market data from MT5"""
        try:
            market_data = {}
            
            if not self.mt5_manager.connected:
                return {}
            
            for symbol in self.config.symbols:
                symbol_data = {}
                for timeframe in self.config.timeframes:
                    df = self.mt5_manager.get_market_data(symbol, timeframe, 500)
                    if not df.empty and len(df) >= 20:
                        symbol_data[timeframe] = df
                
                if symbol_data:
                    market_data[symbol] = symbol_data
            
            return market_data
            
        except Exception as e:
            self.logger.error(f"{EMOJIS['error']} Error fetching market data: {e}")
            return {}
    
    def _monitor_positions(self):
        """Monitor active positions with ULTIMATE professional tracking"""
        try:
            if not self.active_trades:
                return
            
            if self.mt5_manager.connected:
                current_positions = self.mt5_manager.get_open_positions()
                open_tickets = {pos['ticket'] for pos in current_positions}
                
                # Check for closed positions
                for trade in self.active_trades[:]:
                    if trade.ticket and trade.ticket not in open_tickets:
                        self._handle_position_closed(trade)
                        self.active_trades.remove(trade)
                        
                # Update current P&L
                for trade in self.active_trades:
                    if trade.ticket:
                        for pos in current_positions:
                            if pos['ticket'] == trade.ticket:
                                trade.pnl = pos['profit']
                                break
            
            self.metrics.open_positions = len(self.active_trades)
            
        except Exception as e:
            self.logger.error(f"{EMOJIS['error']} Error monitoring positions: {e}")
    
    def _handle_position_closed(self, trade: TradeExecution):
        """Handle position closure with ULTIMATE professional tracking"""
        try:
            # Update risk manager
            self.risk_manager.remove_position()
            self.risk_manager.update_daily_pnl(trade.pnl)
            
            # Update metrics
            self.metrics.total_pnl += trade.pnl
            self.metrics.daily_pnl += trade.pnl
            
            # Update position sizer with trade result
            trade_result = {
                'pnl': trade.pnl,
                'position_size': trade.volume,
                'timestamp': datetime.now()
            }
            self.position_sizer.update_trade_result(trade_result)
            
            # Log closure
            result = "PROFIT" if trade.pnl > 0 else "LOSS"
            account_type = "DEMO" if "demo" in self.mt5_manager.account_info.server.lower() else "LIVE"
            
            self.logger.info(f"{EMOJIS['money']} ULTIMATE PROFESSIONAL {account_type} POSITION CLOSED:")
            self.logger.info(f"   {trade.symbol} {trade.action} | P&L: {trade.pnl:.2f} | {result}")
            
        except Exception as e:
            self.logger.error(f"{EMOJIS['error']} Error handling position closure: {e}")
    
    def _update_professional_metrics(self):
        """Update ULTIMATE professional performance metrics"""
        try:
            self.metrics.uptime_hours = (datetime.now() - self.start_time).total_seconds() / 3600
            
            if self.metrics.trades_executed > 0:
                self.metrics.win_rate = (self.metrics.successful_trades / self.metrics.trades_executed) * 100
            
            # Kelly efficiency
            self.metrics.kelly_efficiency = 0.1  # Placeholder
            
        except Exception as e:
            self.logger.error(f"{EMOJIS['error']} Error updating ULTIMATE professional metrics: {e}")
    
    def _log_performance_summary(self):
        """Log comprehensive ULTIMATE performance summary"""
        try:
            account_type = "DEMO" if "demo" in self.mt5_manager.account_info.server.lower() else "LIVE"
            
            self.logger.info(f"{EMOJIS['chart']} === ULTIMATE PROFESSIONAL {account_type} TRADING PERFORMANCE ===")
            self.logger.info(f"   System uptime: {self.metrics.uptime_hours:.1f} hours")
            self.logger.info(f"   Account: {self.mt5_manager.account_info.login}")
            self.logger.info(f"   Balance: {self.mt5_manager.account_info.balance:.2f}")
            
            # Signal statistics
            self.logger.info(f"   === SIGNAL STATISTICS ===")
            self.logger.info(f"   Strategies loaded: {self.metrics.strategies_loaded}")
            self.logger.info(f"   Advanced factory signals: {self.metrics.advanced_factory_signals}")
            self.logger.info(f"   Signals generated: {self.metrics.signals_generated}")
            
            # Trading statistics
            self.logger.info(f"   === TRADING STATISTICS ===")
            self.logger.info(f"   Trades executed: {self.metrics.trades_executed}")
            self.logger.info(f"   Success rate: {self.metrics.win_rate:.1f}%")
            self.logger.info(f"   Total P&L: {self.metrics.total_pnl:.2f}")
            self.logger.info(f"   Daily P&L: {self.metrics.daily_pnl:.2f}")
            self.logger.info(f"   Open positions: {self.metrics.open_positions}")
            
            self.logger.info("=" * 70)
            
        except Exception as e:
            self.logger.error(f"{EMOJIS['error']} Error logging ULTIMATE performance summary: {e}")
    
    def shutdown(self):
        """Graceful shutdown with ULTIMATE professional cleanup"""
        try:
            self.logger.info(f"{EMOJIS['gear']} Shutting down ULTIMATE PROFESSIONAL trading system...")
            self.shutdown_event.set()
            
            # Final performance summary
            self._log_performance_summary()
            
            # Disconnect MT5
            self.mt5_manager.disconnect()
            
            self.logger.info(f"{EMOJIS['finish']} ULTIMATE PROFESSIONAL trading system shutdown complete")
            
        except Exception as e:
            self.logger.error(f"{EMOJIS['error']} Shutdown error: {e}")

def signal_handler(signum, frame, orchestrator):
    """Handle shutdown signals gracefully"""
    print(f"\nSignal {signum} received. Shutting down ULTIMATE PROFESSIONAL trading gracefully...")
    orchestrator.shutdown()
    sys.exit(0)

def main():
    """Main entry point - ULTIMATE PROFESSIONAL DEMO/LIVE TRADING SYSTEM"""
    parser = argparse.ArgumentParser(description="ULTIMATE Professional Trading Bot v2.2.2 - COMPLETE DEMO/LIVE TRADING SYSTEM")
    parser.add_argument("--config", default="config.yaml", help="Configuration file path")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--strategies", nargs="+", help="Specific strategies to enable")
    parser.add_argument("--mode", choices=['demo', 'live'], help="Force trading mode (demo/live)")
    
    args = parser.parse_args()
    
    try:
        print(f"\n{EMOJIS['rocket']} ULTIMATE PROFESSIONAL TRADING BOT v2.2.2")
        print("=" * 80)
        print(f"{EMOJIS['security']} SECURITY: MT5 credentials loaded from config/.env file")
        print(f"{EMOJIS['info']} MODES: DEMO (safe testing) or LIVE (real money)")
        print(f"{EMOJIS['kelly']} FEATURES: Kelly Position Sizing, Signal Validation, Real Confidence")
        print(f"{EMOJIS['fixed']} FIXES: Advanced Factory Timeframe Errors COMPLETELY FIXED")
        print(f"{EMOJIS['warning']} Make sure your config/.env file contains MT5 credentials")
        print("=" * 80)
        
        # Create ULTIMATE professional orchestrator
        orchestrator = UltimateProfessionalTradingOrchestrator(args.config)
        
        # Apply command line overrides
        if args.verbose:
            orchestrator.config.log_level = "DEBUG"
            
        if args.strategies:
            orchestrator.config.enabled_strategies = args.strategies
            
        if args.mode:
            orchestrator.config.trading_mode = TradingMode(args.mode)
        
        # SECURITY: Check config/.env credentials
        mt5_login = os.getenv('MT5_LOGIN')
        mt5_password = os.getenv('MT5_PASSWORD')
        mt5_server = os.getenv('MT5_SERVER')
        
        if not all([mt5_login, mt5_password, mt5_server]):
            print(f"\n{EMOJIS['error']} CRITICAL ERROR: MT5 credentials missing in config/.env file")
            print("Create a config/.env file with:")
            print("  MT5_LOGIN=your_account_number")
            print("  MT5_PASSWORD=your_password")
            print("  MT5_SERVER=your_server_name")
            print(f"\n{EMOJIS['security']} SECURITY: Never put credentials in config.yaml!")
            sys.exit(1)
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, lambda s, f: signal_handler(s, f, orchestrator))
        signal.signal(signal.SIGTERM, lambda s, f: signal_handler(s, f, orchestrator))
        
        # Initialize ULTIMATE professional trading system
        if not orchestrator.initialize():
            print(f"{EMOJIS['error']} ULTIMATE professional trading system initialization failed")
            sys.exit(1)
        
        # Verify MT5 connection
        if not orchestrator.mt5_manager.connected:
            print(f"{EMOJIS['error']} CRITICAL ERROR: Failed to connect to MT5")
            print("Check your config/.env credentials and ensure MT5 terminal is running")
            sys.exit(1)
        
        account_type = "DEMO" if "demo" in orchestrator.mt5_manager.account_info.server.lower() else "LIVE"
        mode_emoji = EMOJIS['demo'] if account_type == "DEMO" else EMOJIS['live']
        
        print(f"\n{EMOJIS['success']} ULTIMATE PROFESSIONAL {account_type} TRADING SYSTEM READY!")
        print(f"{mode_emoji} Account: {orchestrator.mt5_manager.account_info.login}")
        print(f"{EMOJIS['money']} Balance: {orchestrator.mt5_manager.account_info.balance:.2f}")
        print(f"{EMOJIS['gear']} Strategies: {orchestrator.metrics.strategies_loaded}")
        print(f"{EMOJIS['fixed']} Advanced Factory: {'ULTIMATE FIXED' if orchestrator.signal_processor.advanced_factory_enabled else 'DISABLED'}")
        print(f"{EMOJIS['kelly']} Kelly Position Sizing: {'ENABLED' if orchestrator.position_sizer.kelly_available else 'ADVANCED DYNAMIC'}")
        print(f"{EMOJIS['security']} *** ULTIMATE PROFESSIONAL {account_type} TRADING MODE ***")
        print("Press Ctrl+C to stop trading\n")
        
        # Run ULTIMATE professional trading loop
        orchestrator.run_trading_loop()
    
    except KeyboardInterrupt:
        print("\nULTIMATE Professional trading stopped by user")
    except Exception as e:
        print(f"{EMOJIS['error']} Fatal error: {e}")
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
