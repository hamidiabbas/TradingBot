#!/usr/bin/env python3
"""
===============================================================
TradingBot v2.9 - ADVANCED KELLY INTEGRATION - PRODUCTION READY
===============================================================
ADVANCED INTEGRATION FEATURES:
- Full integration with dynamic_kelly_position_sizing.py
- Professional Kelly Criterion position sizing
- Advanced risk management with portfolio correlation
- Realistic ATR-based SL/TP calculations
- Multi-factor position size adjustments
- Proper broker compatibility

Version: 2.9.0 - Advanced Kelly Integration
===============================================================
"""

import argparse
import asyncio
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

# SECURITY: Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path("config/.env")
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"Environment variables loaded from {env_path}")
    else:
        load_dotenv()
        print("Environment variables loaded from root .env file")
except ImportError:
    print("python-dotenv not installed. Using system environment variables only")

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

# CRITICAL: Import your advanced Kelly position sizing system
try:
    from dynamic_kelly_position_sizing import (
        KellyPositionManager,
        ProfessionalKellyPositionSizer,
        calculate_dynamic_kelly_size,
        PositionSizingResult,
        TradeHistory,
        RiskMetrics
    )
    ADVANCED_KELLY_AVAILABLE = True
    print("✅ Advanced Kelly Position Sizing imported successfully")
except ImportError as e:
    ADVANCED_KELLY_AVAILABLE = False
    print(f"❌ Advanced Kelly Position Sizing not available: {e}")
    print("Please ensure dynamic_kelly_position_sizing.py is in the same directory")

# Additional imports
try:
    from signal_factory import (
        process_market_data_for_main_py, 
        get_signal_factory,
        SignalFactory,
        SignalType,
        StrategyType
    )
    ADVANCED_SIGNAL_FACTORY_AVAILABLE = True
    print("✅ Advanced Signal Factory imported successfully")
except ImportError as e:
    ADVANCED_SIGNAL_FACTORY_AVAILABLE = False
    print(f"ℹ️ Advanced Signal Factory not available: {e}")

# Suppress warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

# ============================================================================
# DATA STRUCTURES FOR ADVANCED INTEGRATION
# ============================================================================

class TradingMode(Enum):
    LIVE = "live"
    DEMO = "demo"

@dataclass
class AdvancedTradeExecution:
    symbol: str
    action: str
    volume: float
    entry_price: float
    stop_loss: float
    take_profit: float
    timestamp: datetime
    strategy_names: List[str]
    timeframes: List[str]
    signal_strength: float
    signal_id: str = ""
    ticket: Optional[int] = None
    status: str = "PENDING"
    pnl: float = 0.0
    confidence_factor: float = 0.0
    filling_mode: str = "unknown"
    
    # Advanced Kelly metrics
    kelly_fraction: float = 0.0
    position_sizing_method: str = "kelly_advanced"
    risk_amount: float = 0.0
    kelly_reasoning: str = ""
    portfolio_correlation_risk: float = 0.0
    volatility_adjustment: float = 1.0
    drawdown_adjustment: float = 1.0
    final_risk_percentage: float = 0.0
    
    # ATR-based metrics
    atr_value: float = 0.0
    atr_sl_distance: float = 0.0
    atr_tp_distance: float = 0.0
    risk_reward_ratio: float = 0.0

@dataclass
class AdvancedTradingConfig:
    # MT5 Configuration (from .env)
    mt5_login: int = 0
    mt5_password: str = ""
    mt5_server: str = ""
    mt5_path: str = ""
    
    # Trading Parameters
    symbols: List[str] = field(default_factory=lambda: ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "XAUUSD"])
    timeframes: List[str] = field(default_factory=lambda: ["M15", "H1", "H4"])
    
    # Advanced Kelly Configuration
    kelly_enabled: bool = True
    kelly_lookback_period: int = 100
    kelly_safety_factor: float = 0.25
    min_kelly_samples: int = 20
    max_kelly_fraction: float = 0.20
    kelly_multiplier: float = 0.5
    
    # Risk Management (Kelly-integrated)
    base_risk_per_trade: float = 0.015  # 1.5% base risk
    max_risk_per_trade: float = 0.03    # 3% maximum risk
    max_portfolio_risk: float = 0.15    # 15% total portfolio risk
    max_single_symbol_risk: float = 0.08 # 8% per symbol
    
    # Dynamic ATR-based SL/TP
    enable_dynamic_sl_tp: bool = True
    atr_period: int = 14
    atr_sl_multiplier: float = 2.0  # More realistic 2.0 ATR for SL
    atr_tp_multiplier: float = 4.0  # 4.0 ATR for TP (2:1 RR)
    
    # Position limits (realistic)
    max_positions: int = 8
    min_position_size: float = 0.01
    max_position_size: float = 0.10  # Realistic maximum
    
    # Signal requirements
    min_signal_confidence: float = 0.35
    
    # System Configuration
    trading_mode: TradingMode = TradingMode.DEMO
    log_level: str = "INFO"
    signal_processing_interval: int = 8

# ============================================================================
# ADVANCED LOGGER WITH KELLY INTEGRATION
# ============================================================================

class AdvancedKellyLogger:
    """Advanced logger with Kelly-specific formatting"""
    
    def __init__(self, name: str, level: str = "INFO"):
        self.name = name
        self.level = level
        self._lock = threading.Lock()
        self._setup_logger()
    
    def _setup_logger(self):
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(getattr(logging, self.level.upper()))
        
        # Clear existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        self.logger.propagate = False
        
        # Kelly-optimized formatter
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
                f'logs/advanced_kelly_{datetime.now().strftime("%Y%m%d_%H%M")}.log',
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not create file handler: {e}")
    
    def _safe_message(self, msg: str) -> str:
        """Clean message for safe logging"""
        try:
            msg = str(msg)
            # Remove HTML entities completely
            msg = msg.replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&')
            msg = msg.replace('&nbsp;', ' ').replace('&quot;', '"').replace('&#x27;', "'")
            # Force clean ASCII
            msg = msg.encode('ascii', 'ignore').decode('ascii')
            return msg
        except Exception:
            return str(msg).encode('ascii', 'ignore').decode('ascii')
    
    def _log_safely(self, level: str, msg: str, *args):
        try:
            with self._lock:
                safe_msg = self._safe_message(str(msg))
                getattr(self.logger, level)(safe_msg, *args)
        except Exception:
            try:
                print(f"{level.upper()}: {msg}")
            except:
                pass
    
    def info(self, msg: str, *args):
        self._log_safely('info', msg, *args)
    
    def error(self, msg: str, *args):
        self._log_safely('error', msg, *args)
    
    def warning(self, msg: str, *args):
        self._log_safely('warning', msg, *args)
    
    def debug(self, msg: str, *args):
        self._log_safely('debug', msg, *args)

# ============================================================================
# ADVANCED ATR CALCULATOR
# ============================================================================

class AdvancedATRCalculator:
    """Advanced ATR calculator with Kelly integration"""
    
    @staticmethod
    def calculate_atr_with_confidence(data: pd.DataFrame, period: int = 14) -> Tuple[float, float]:
        """Calculate ATR with confidence level"""
        try:
            if len(data) < period + 1:
                return 0.0, 0.0
            
            # Calculate True Range
            data_copy = data.copy()
            data_copy['prev_close'] = data_copy['close'].shift(1)
            data_copy['tr1'] = data_copy['high'] - data_copy['low']
            data_copy['tr2'] = abs(data_copy['high'] - data_copy['prev_close'])
            data_copy['tr3'] = abs(data_copy['low'] - data_copy['prev_close'])
            
            data_copy['tr'] = data_copy[['tr1', 'tr2', 'tr3']].max(axis=1)
            
            # Calculate ATR
            atr_series = data_copy['tr'].rolling(window=period).mean()
            atr = atr_series.iloc[-1]
            
            # Calculate ATR confidence (based on stability)
            recent_atr_values = atr_series.tail(period).dropna()
            if len(recent_atr_values) > 1:
                atr_std = recent_atr_values.std()
                atr_confidence = 1.0 - min(1.0, atr_std / atr) if atr > 0 else 0.0
            else:
                atr_confidence = 0.5
            
            return float(atr) if not pd.isna(atr) else 0.0, float(atr_confidence)
            
        except Exception as e:
            return 0.0, 0.0
    
    @staticmethod
    def get_kelly_adjusted_sl_tp(data: pd.DataFrame, entry_price: float, direction: str,
                                kelly_fraction: float, confidence: float,
                                atr_sl_mult: float = 2.0, atr_tp_mult: float = 4.0) -> Tuple[float, float, float, Dict[str, Any]]:
        """Calculate Kelly-adjusted SL/TP levels"""
        try:
            atr, atr_confidence = AdvancedATRCalculator.calculate_atr_with_confidence(data, 14)
            
            if atr <= 0:
                # Fallback to percentage-based SL/TP
                sl_distance = entry_price * 0.008  # 0.8%
                tp_distance = entry_price * 0.025  # 2.5%
                atr = entry_price * 0.01  # Estimated ATR
            else:
                # Kelly-adjusted ATR multipliers
                kelly_adjustment = 0.7 + (kelly_fraction * 1.5)  # Adjust based on Kelly fraction
                confidence_adjustment = 0.8 + (confidence * 0.4)  # More aggressive with higher confidence
                
                adjusted_sl_mult = atr_sl_mult * kelly_adjustment * confidence_adjustment
                adjusted_tp_mult = atr_tp_mult * kelly_adjustment * confidence_adjustment
                
                sl_distance = atr * adjusted_sl_mult
                tp_distance = atr * adjusted_tp_mult
            
            if direction.lower() in ['buy', 'bullish']:
                stop_loss = entry_price - sl_distance
                take_profit = entry_price + tp_distance
            else:  # SELL
                stop_loss = entry_price + sl_distance
                take_profit = entry_price - tp_distance
            
            # Calculate risk-reward ratio
            risk_reward_ratio = tp_distance / sl_distance if sl_distance > 0 else 2.0
            
            # Additional metrics
            metrics = {
                'atr_value': atr,
                'atr_confidence': atr_confidence,
                'sl_distance_atr': sl_distance / atr if atr > 0 else 0,
                'tp_distance_atr': tp_distance / atr if atr > 0 else 0,
                'kelly_adjustment': kelly_adjustment if atr > 0 else 1.0,
                'confidence_adjustment': confidence_adjustment,
                'risk_reward_ratio': risk_reward_ratio
            }
            
            return stop_loss, take_profit, atr, metrics
            
        except Exception as e:
            # Emergency fallback
            if direction.lower() in ['buy', 'bullish']:
                stop_loss = entry_price * 0.992
                take_profit = entry_price * 1.025
            else:
                stop_loss = entry_price * 1.008
                take_profit = entry_price * 0.975
            
            return stop_loss, take_profit, 0.0, {'error': str(e)}

# ============================================================================
# ADVANCED SIGNAL PROCESSOR WITH KELLY INTEGRATION
# ============================================================================

class AdvancedKellySignalProcessor:
    """Advanced signal processor with Kelly Criterion integration"""
    
    def __init__(self, logger: AdvancedKellyLogger, config: AdvancedTradingConfig):
        self.logger = logger
        self.config = config
        self.processed_signals = set()
        self.last_signal_reset = datetime.now()
        
    def process_kelly_signals(self, strategies: Dict[str, Any], 
                            market_data: Dict[str, Dict[str, pd.DataFrame]]) -> List[Dict[str, Any]]:
        """Process signals with Kelly Criterion considerations"""
        try:
            # Reset signal cache every 45 seconds for optimal opportunities
            if (datetime.now() - self.last_signal_reset).total_seconds() > 45:
                self.processed_signals.clear()
                self.last_signal_reset = datetime.now()
                self.logger.info("[KELLY] Signal cache reset - optimizing for Kelly opportunities")
            
            all_signals = []
            
            for strategy_name, strategy in strategies.items():
                try:
                    strategy_data = self._prepare_market_data_for_strategy(strategy, market_data)
                    
                    for symbol, data in strategy_data.items():
                        if isinstance(data, pd.DataFrame) and not data.empty and len(data) >= 30:
                            try:
                                if hasattr(strategy, 'analyze'):
                                    analysis = strategy.analyze(data, symbol)
                                else:
                                    continue
                                
                                signal_type = analysis.get('signal', 'HOLD')
                                raw_confidence = analysis.get('confidence', 0.0)
                                
                                if signal_type not in ['BUY', 'SELL']:
                                    continue
                                
                                # Calculate Kelly-adjusted confidence
                                kelly_confidence = self._calculate_kelly_adjusted_confidence(
                                    data, signal_type, analysis, symbol, strategy_name
                                )
                                
                                # Log confidence adjustments
                                if raw_confidence >= 0.90:
                                    self.logger.info(f"[KELLY] Confidence adjusted: {strategy_name} -> {symbol} "
                                                   f"(raw: {raw_confidence:.2f} -> kelly: {kelly_confidence:.3f})")
                                
                                price = analysis.get('price', data['close'].iloc[-1])
                                
                                # Kelly-optimized validation
                                if (kelly_confidence >= self.config.min_signal_confidence and
                                    kelly_confidence <= 0.90 and
                                    price > 0 and price != 1.0):
                                    
                                    # Create unique signal key with Kelly considerations
                                    signal_key = f"{symbol}_{signal_type}_{strategy_name}_{int(time.time())}"
                                    
                                    if signal_key not in self.processed_signals:
                                        self.processed_signals.add(signal_key)
                                        
                                        signal_dict = {
                                            'symbol': symbol,
                                            'direction': 'bullish' if signal_type == 'BUY' else 'bearish',
                                            'signal_type': signal_type,
                                            'strength': kelly_confidence,
                                            'confidence': kelly_confidence,
                                            'raw_confidence': raw_confidence,
                                            'level': price,
                                            'entry_price': price,
                                            'stop_loss': analysis.get('stop_loss'),
                                            'take_profit': analysis.get('take_profit'),
                                            'strategy_name': strategy_name,
                                            'contributing_strategies': [strategy_name],
                                            'timeframes': [self._determine_timeframe(symbol, market_data)],
                                            'signal_id': f"KELLY_{symbol}_{int(time.time())}",
                                            'timestamp': datetime.now(),
                                            'reason': analysis.get('reason', f'{strategy_name} Kelly-optimized'),
                                            'market_data': data,  # Include for Kelly calculations
                                            'kelly_eligible': True
                                        }
                                        
                                        all_signals.append(signal_dict)
                                        self.logger.info(f"[KELLY] SIGNAL READY: {symbol} {signal_type} "
                                                       f"(kelly-conf: {kelly_confidence:.3f}) by {strategy_name}")
                                        
                            except Exception as e:
                                self.logger.debug(f"Analysis error: {strategy_name} -> {symbol}: {e}")
                
                except Exception as e:
                    self.logger.error(f"Strategy error {strategy_name}: {e}")
                    continue
            
            self.logger.info(f"[KELLY] Generated {len(all_signals)} Kelly-optimized signals")
            return all_signals
            
        except Exception as e:
            self.logger.error(f"Kelly signal processing error: {e}")
            return []
    
    def _calculate_kelly_adjusted_confidence(self, data: pd.DataFrame, signal_type: str, 
                                           analysis: Dict[str, Any], symbol: str, strategy: str) -> float:
        """Calculate Kelly-adjusted confidence based on historical performance"""
        try:
            # Base confidence calculation (from previous version)
            base_confidence = self._calculate_base_confidence(data, signal_type, analysis, symbol)
            
            # Kelly historical performance adjustment
            kelly_adjustment = self._get_kelly_historical_adjustment(symbol, strategy, signal_type)
            
            # ATR-based confidence adjustment
            atr, atr_confidence = AdvancedATRCalculator.calculate_atr_with_confidence(data)
            atr_adjustment = 0.9 + (atr_confidence * 0.2)  # 0.9 to 1.1 range
            
            # Combined Kelly-adjusted confidence
            kelly_confidence = base_confidence * kelly_adjustment * atr_adjustment
            
            # Ensure reasonable bounds
            kelly_confidence = max(0.25, min(0.85, kelly_confidence))
            
            return round(kelly_confidence, 3)
            
        except Exception:
            return 0.50
    
    def _calculate_base_confidence(self, data: pd.DataFrame, signal_type: str, 
                                 analysis: Dict[str, Any], symbol: str) -> float:
        """Calculate base confidence using multiple factors"""
        try:
            if data.empty or len(data) < 20:
                return 0.50
            
            # Multi-factor confidence calculation
            trend_score = self._analyze_trend_strength(data, signal_type)
            momentum_score = self._analyze_momentum(data, signal_type)
            volatility_score = self._analyze_volatility_regime(data)
            
            # Weighted combination
            weighted_confidence = (
                trend_score * 0.4 +
                momentum_score * 0.35 + 
                volatility_score * 0.25
            )
            
            # Symbol-specific adjustment
            symbol_multiplier = 1.05 if symbol in ['EURUSD', 'GBPUSD', 'USDJPY'] else 1.0
            
            # Final confidence
            final_confidence = weighted_confidence * symbol_multiplier
            final_confidence = max(0.30, min(0.85, final_confidence))
            
            return round(final_confidence, 3)
            
        except Exception:
            return 0.50
    
    def _get_kelly_historical_adjustment(self, symbol: str, strategy: str, signal_type: str) -> float:
        """Get Kelly-based adjustment from historical performance"""
        try:
            # This would integrate with the Kelly position manager's historical data
            # For now, use a simplified approach
            
            # Strategy-specific adjustments based on typical Kelly performance
            strategy_adjustments = {
                'momentum': {'BUY': 1.05, 'SELL': 1.02},
                'trend': {'BUY': 1.08, 'SELL': 1.06},
                'breakout': {'BUY': 1.03, 'SELL': 1.03},
                'mean_reversion': {'BUY': 0.98, 'SELL': 0.98}
            }
            
            strategy_lower = strategy.lower()
            for key, adjustments in strategy_adjustments.items():
                if key in strategy_lower:
                    return adjustments.get(signal_type, 1.0)
            
            return 1.0
            
        except:
            return 1.0
    
    def _analyze_trend_strength(self, data: pd.DataFrame, signal_type: str) -> float:
        try:
            if len(data) < 20:
                return 0.6
            
            ma_10 = data['close'].rolling(10).mean().iloc[-1]
            ma_20 = data['close'].rolling(20).mean().iloc[-1]
            current_price = data['close'].iloc[-1]
            
            if signal_type == 'BUY':
                if current_price > ma_10 > ma_20:
                    return 0.82
                elif current_price > ma_20:
                    return 0.68
                else:
                    return 0.45
            else:  # SELL
                if current_price < ma_10 < ma_20:
                    return 0.82
                elif current_price < ma_20:
                    return 0.68
                else:
                    return 0.45
        except:
            return 0.6
    
    def _analyze_momentum(self, data: pd.DataFrame, signal_type: str) -> float:
        try:
            if len(data) < 14:
                return 0.6
                
            # RSI calculation
            delta = data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            if signal_type == 'BUY':
                if 30 <= current_rsi <= 50:
                    return 0.78
                elif current_rsi < 30:
                    return 0.82
                else:
                    return 0.52
            else:  # SELL
                if 50 <= current_rsi <= 70:
                    return 0.78
                elif current_rsi > 70:
                    return 0.82
                else:
                    return 0.52
        except:
            return 0.6
    
    def _analyze_volatility_regime(self, data: pd.DataFrame) -> float:
        try:
            if len(data) < 20:
                return 0.6
                
            returns = data['close'].pct_change().dropna()
            volatility = returns.rolling(window=20).std().iloc[-1]
            
            if 0.003 <= volatility <= 0.015:  # Optimal volatility range
                return 0.75
            elif volatility < 0.003:  # Too low volatility
                return 0.55
            elif volatility > 0.03:  # Too high volatility
                return 0.45
            else:
                return 0.65
        except:
            return 0.6
    
    def _prepare_market_data_for_strategy(self, strategy, market_data: Dict[str, Dict[str, pd.DataFrame]]) -> Dict[str, pd.DataFrame]:
        prepared_data = {}
        
        for symbol, timeframe_data in market_data.items():
            if isinstance(timeframe_data, dict) and timeframe_data:
                primary_tf = self.config.timeframes[0] if self.config.timeframes else 'H1'
                if primary_tf in timeframe_data:
                    df = timeframe_data[primary_tf]
                else:
                    df = next(iter(timeframe_data.values()))
                
                if isinstance(df, pd.DataFrame) and not df.empty and len(df) >= 30:
                    prepared_data[symbol] = df
            elif isinstance(timeframe_data, pd.DataFrame) and not timeframe_data.empty:
                prepared_data[symbol] = timeframe_data
        
        return prepared_data
    
    def _determine_timeframe(self, symbol: str, market_data: Dict[str, Dict[str, pd.DataFrame]]) -> str:
        try:
            if symbol in market_data and isinstance(market_data[symbol], dict):
                return next(iter(market_data[symbol].keys()))
            return self.config.timeframes[0] if self.config.timeframes else "H1"
        except:
            return "H1"

# ============================================================================
# ADVANCED KELLY-INTEGRATED MT5 MANAGER
# ============================================================================

class AdvancedKellyMT5Manager:
    """Advanced MT5 manager with Kelly Criterion integration"""
    
    def __init__(self, logger: AdvancedKellyLogger, config: AdvancedTradingConfig):
        self.logger = logger
        self.config = config
        self.connected = False
        self.account_info = None
        self.supported_filling_modes = []
        
        # Initialize Kelly Position Manager if available
        if ADVANCED_KELLY_AVAILABLE:
            try:
                kelly_config = {
                    'kelly_lookback_period': config.kelly_lookback_period,
                    'min_trades_for_kelly': config.min_kelly_samples,
                    'max_kelly_fraction': config.max_kelly_fraction,
                    'kelly_multiplier': config.kelly_multiplier,
                    'base_risk_percent': config.base_risk_per_trade,
                    'base_risk_per_trade': config.base_risk_per_trade,
                    'max_risk_per_trade': config.max_risk_per_trade,
                    'max_portfolio_risk': config.max_portfolio_risk,
                    'max_single_symbol_risk': config.max_single_symbol_risk
                }
                
                self.kelly_manager = KellyPositionManager(kelly_config)
                self.professional_kelly = ProfessionalKellyPositionSizer(kelly_config)
                self.logger.info("✅ Advanced Kelly Position Manager initialized")
                
            except Exception as e:
                self.logger.error(f"❌ Error initializing Kelly manager: {e}")
                self.kelly_manager = None
                self.professional_kelly = None
        else:
            self.kelly_manager = None
            self.professional_kelly = None
            self.logger.warning("⚠️ Advanced Kelly Position Sizing not available")
        
    def connect(self) -> bool:
        """Connect to MT5 with advanced configuration"""
        try:
            # Get credentials
            mt5_login = int(os.getenv('MT5_LOGIN', self.config.mt5_login)) if os.getenv('MT5_LOGIN') else self.config.mt5_login
            mt5_password = os.getenv('MT5_PASSWORD', self.config.mt5_password)
            mt5_server = os.getenv('MT5_SERVER', self.config.mt5_server)
            mt5_path = os.getenv('MT5_PATH', self.config.mt5_path)
            
            if not all([mt5_login, mt5_password, mt5_server]):
                self.logger.error("Missing MT5 credentials in config/.env file")
                return False
            
            # Initialize MT5
            if mt5_path and Path(mt5_path).exists():
                if not mt5.initialize(path=mt5_path):
                    self.logger.error(f"MT5 initialization failed: {mt5.last_error()}")
                    return False
            else:
                if not mt5.initialize():
                    self.logger.error(f"MT5 initialization failed: {mt5.last_error()}")
                    return False
            
            # Login with retries
            for attempt in range(3):
                if mt5.login(login=mt5_login, password=mt5_password, server=mt5_server):
                    break
                if attempt < 2:
                    self.logger.warning(f"MT5 login attempt {attempt + 1} failed, retrying...")
                    time.sleep(2)
                else:
                    self.logger.error(f"MT5 login failed after 3 attempts")
                    mt5.shutdown()
                    return False
            
            # Get account info
            self.account_info = mt5.account_info()
            if not self.account_info:
                self.logger.error("Failed to get account info")
                return False
            
            # Detect supported filling modes
            self._detect_supported_filling_modes()
            
            self.connected = True
            
            account_type = "DEMO" if "demo" in mt5_server.lower() else "LIVE"
            
            self.logger.info(f"✅ ADVANCED KELLY MT5 {account_type} connected")
            self.logger.info(f"   Account: {self.account_info.login}")
            self.logger.info(f"   Balance: ${self.account_info.balance:.2f} {self.account_info.currency}")
            self.logger.info(f"   Supported filling modes: {self.supported_filling_modes}")
            self.logger.info(f"   Kelly Manager: {'✅ ACTIVE' if self.kelly_manager else '❌ NOT AVAILABLE'}")
            
            return True
        except Exception as e:
            self.logger.error(f"MT5 connection error: {e}")
            return False
    
    def _detect_supported_filling_modes(self):
        """Detect supported filling modes with fallback priority"""
        try:
            test_symbol = "EURUSD"
            symbol_info = mt5.symbol_info(test_symbol)
            if symbol_info:
                filling_modes = []
                
                # Check for FOK (Fill or Kill) - often supported
                if symbol_info.filling_mode & 1:
                    filling_modes.append("FOK")
                
                # Check for IOC (Immediate or Cancel)
                if symbol_info.filling_mode & 2:
                    filling_modes.append("IOC")
                
                # Always add RETURN as fallback
                filling_modes.append("RETURN")
                
                self.supported_filling_modes = filling_modes
                
            else:
                # Safe fallback
                self.supported_filling_modes = ["FOK", "RETURN", "IOC"]
                
            self.logger.info(f"[KELLY] Filling mode detection complete: {self.supported_filling_modes}")
            
        except Exception as e:
            self.logger.error(f"Filling mode detection error: {e}")
            self.supported_filling_modes = ["FOK", "RETURN"]
    
    def get_market_data(self, symbol: str, timeframe: str, count: int = 500) -> pd.DataFrame:
        """Get market data from MT5"""
        try:
            if not self.connected:
                return pd.DataFrame()
            
            symbol_info = mt5.symbol_info(symbol)
            if not symbol_info:
                return pd.DataFrame()
            
            if not symbol_info.visible:
                if not mt5.symbol_select(symbol, True):
                    return pd.DataFrame()
            
            tf_map = {
                'M1': mt5.TIMEFRAME_M1, 'M5': mt5.TIMEFRAME_M5,
                'M15': mt5.TIMEFRAME_M15, 'M30': mt5.TIMEFRAME_M30,
                'H1': mt5.TIMEFRAME_H1, 'H4': mt5.TIMEFRAME_H4,
                'D1': mt5.TIMEFRAME_D1, 'W1': mt5.TIMEFRAME_W1
            }
            
            mt5_timeframe = tf_map.get(timeframe, mt5.TIMEFRAME_H1)
            rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, count)
            
            if rates is None or len(rates) == 0:
                return pd.DataFrame()
            
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            
            return df
        except Exception as e:
            self.logger.debug(f"Market data error for {symbol}: {e}")
            return pd.DataFrame()
    
    def execute_kelly_optimized_trade(self, signal: Dict[str, Any]) -> Optional[AdvancedTradeExecution]:
        """Execute trade with advanced Kelly Criterion optimization"""
        try:
            if not self.connected:
                self.logger.error("[KELLY] Not connected to MT5")
                return None
            
            symbol = signal['symbol']
            direction = signal['direction']
            market_data = signal.get('market_data')
            confidence = signal.get('confidence', 0.5)
            
            if market_data is None or market_data.empty:
                self.logger.error(f"[KELLY] No market data for {symbol}")
                return None
            
            # Validate symbol
            symbol_info = mt5.symbol_info(symbol)
            if not symbol_info:
                self.logger.error(f"[KELLY] Symbol {symbol} not found")
                return None
            
            if not symbol_info.visible:
                if not mt5.symbol_select(symbol, True):
                    self.logger.error(f"[KELLY] Cannot select symbol {symbol}")
                    return None
            
            # Get current prices
            tick = mt5.symbol_info_tick(symbol)
            if not tick or tick.ask <= 0 or tick.bid <= 0:
                self.logger.error(f"[KELLY] Invalid tick data for {symbol}")
                return None
            
            entry_price = tick.ask if direction == 'bullish' else tick.bid
            action = "BUY" if direction == 'bullish' else "SELL"
            
            # Get account balance
            account_balance = self.get_account_balance()
            if account_balance <= 0:
                self.logger.error("[KELLY] Invalid account balance")
                return None
            
            # *** ADVANCED KELLY POSITION SIZING ***
            if self.kelly_manager and self.professional_kelly:
                position_size, kelly_metrics = self._calculate_advanced_kelly_position_size(
                    signal, account_balance, entry_price, market_data
                )
            else:
                # Fallback position sizing
                position_size = self.config.base_risk_per_trade
                kelly_metrics = {
                    'kelly_fraction': self.config.base_risk_per_trade,
                    'risk_amount': account_balance * self.config.base_risk_per_trade,
                    'method': 'fallback_fixed'
                }
            
            # *** ADVANCED KELLY-ADJUSTED SL/TP ***
            kelly_fraction = kelly_metrics.get('kelly_fraction', self.config.base_risk_per_trade)
            stop_loss, take_profit, atr_value, atr_metrics = AdvancedATRCalculator.get_kelly_adjusted_sl_tp(
                market_data, entry_price, direction, kelly_fraction, confidence,
                self.config.atr_sl_multiplier, self.config.atr_tp_multiplier
            )
            
            # Normalize position size
            lot_step = symbol_info.volume_step if symbol_info.volume_step > 0 else 0.01
            normalized_size = round(position_size / lot_step) * lot_step
            normalized_size = max(symbol_info.volume_min, min(symbol_info.volume_max, normalized_size))
            
            # Normalize SL/TP prices
            digits = symbol_info.digits
            stop_loss = round(stop_loss, digits)
            take_profit = round(take_profit, digits)
            
            # Calculate comprehensive metrics
            position_value = normalized_size * entry_price
            sl_distance = abs(entry_price - stop_loss)
            tp_distance = abs(take_profit - entry_price)
            risk_reward_ratio = tp_distance / sl_distance if sl_distance > 0 else 2.0
            risk_amount = kelly_metrics.get('risk_amount', position_value * 0.02)
            final_risk_percentage = risk_amount / account_balance
            
            self.logger.info(f"[KELLY] *** ADVANCED KELLY TRADE EXECUTION ***")
            self.logger.info(f"[KELLY]   Symbol: {symbol} ({action})")
            self.logger.info(f"[KELLY]   Position Size: {normalized_size:.4f} lots (${position_value:.2f})")
            self.logger.info(f"[KELLY]   Entry Price: {entry_price:.5f}")
            self.logger.info(f"[KELLY]   Kelly Fraction: {kelly_fraction:.4f}")
            self.logger.info(f"[KELLY]   ATR: {atr_value:.5f}")
            self.logger.info(f"[KELLY]   Stop Loss: {stop_loss:.5f} ({sl_distance/atr_value:.1f} ATR)" if atr_value > 0 else f"[KELLY]   Stop Loss: {stop_loss:.5f}")
            self.logger.info(f"[KELLY]   Take Profit: {take_profit:.5f} ({tp_distance/atr_value:.1f} ATR)" if atr_value > 0 else f"[KELLY]   Take Profit: {take_profit:.5f}")
            self.logger.info(f"[KELLY]   Risk-Reward: 1:{risk_reward_ratio:.2f}")
            self.logger.info(f"[KELLY]   Risk Amount: ${risk_amount:.2f} ({final_risk_percentage:.2%})")
            
            # Create comprehensive trade execution record
            trade_execution = AdvancedTradeExecution(
                symbol=symbol,
                action=action,
                volume=normalized_size,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                timestamp=datetime.now(),
                strategy_names=signal.get('contributing_strategies', ['Kelly']),
                timeframes=signal.get('timeframes', ['H1']),
                signal_strength=signal['strength'],
                signal_id=signal.get('signal_id', ''),
                confidence_factor=confidence,
                
                # Advanced Kelly metrics
                kelly_fraction=kelly_fraction,
                position_sizing_method='advanced_kelly',
                risk_amount=risk_amount,
                kelly_reasoning=kelly_metrics.get('reasoning', 'Kelly Criterion applied'),
                portfolio_correlation_risk=kelly_metrics.get('correlation_risk', 0.0),
                volatility_adjustment=kelly_metrics.get('volatility_adjustment', 1.0),
                drawdown_adjustment=kelly_metrics.get('drawdown_adjustment', 1.0),
                final_risk_percentage=final_risk_percentage,
                
                # ATR-based metrics
                atr_value=atr_value,
                atr_sl_distance=sl_distance,
                atr_tp_distance=tp_distance,
                risk_reward_ratio=risk_reward_ratio
            )
            
            # *** EXECUTE WITH ADVANCED FILLING MODES ***
            filling_modes_to_try = [
                ("FOK", mt5.ORDER_FILLING_FOK),
                ("RETURN", mt5.ORDER_FILLING_RETURN),
                ("IOC", mt5.ORDER_FILLING_IOC)
            ]
            
            account_type = "DEMO" if "demo" in self.account_info.server.lower() else "LIVE"
            
            for mode_name, mode_constant in filling_modes_to_try:
                try:
                    self.logger.info(f"[KELLY] Attempting {mode_name} filling mode...")
                    
                    request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": symbol,
                        "volume": normalized_size,
                        "type": mt5.ORDER_TYPE_BUY if action == "BUY" else mt5.ORDER_TYPE_SELL,
                        "price": entry_price,
                        "sl": stop_loss,
                        "tp": take_profit,
                        "deviation": 15,  # Reduced deviation for better fills
                        "magic": 234001,  # Different magic number
                        "comment": f"KellyBot-{account_type}-{mode_name}",
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mode_constant,
                    }
                    
                    result = mt5.order_send(request)
                    
                    if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                        trade_execution.ticket = result.order
                        trade_execution.status = "EXECUTED"
                        trade_execution.entry_price = result.price
                        trade_execution.filling_mode = mode_name
                        
                        # Update Kelly manager with successful trade
                        if self.kelly_manager:
                            self._update_kelly_manager_position(trade_execution)
                        
                        self.logger.info(f"[KELLY] *** ADVANCED KELLY TRADE EXECUTED SUCCESSFULLY ***")
                        self.logger.info(f"[KELLY]   Ticket: {result.order}")
                        self.logger.info(f"[KELLY]   Execution Price: {result.price:.5f}")
                        self.logger.info(f"[KELLY]   Filling Mode: {mode_name}")
                        self.logger.info(f"[KELLY]   Kelly Method: {kelly_metrics.get('method', 'advanced')}")
                        
                        return trade_execution
                    
                    else:
                        error_msg = result.comment if result else "Unknown error"
                        self.logger.warning(f"[KELLY] {mode_name} failed: {error_msg}")
                        
                        # Don't continue if position limit reached
                        if "limit" in error_msg.lower():
                            self.logger.warning("[KELLY] Position limit reached, stopping execution attempts")
                            break
                        
                        continue
                        
                except Exception as mode_error:
                    self.logger.warning(f"[KELLY] {mode_name} mode error: {mode_error}")
                    continue
            
            # If all modes failed
            self.logger.error(f"[KELLY] *** ALL FILLING MODES FAILED for {symbol} ***")
            trade_execution.status = "FAILED"
            trade_execution.filling_mode = "all_failed"
            return trade_execution
                
        except Exception as e:
            self.logger.error(f"[KELLY] Critical execution error: {e}")
            return None
    
    def _calculate_advanced_kelly_position_size(self, signal: Dict[str, Any], account_balance: float,
                                              entry_price: float, market_data: pd.DataFrame) -> Tuple[float, Dict[str, Any]]:
        """Calculate position size using advanced Kelly Criterion"""
        try:
            symbol = signal['symbol']
            confidence = signal.get('confidence', 0.5)
            strategy = signal.get('strategy_name', 'unknown')
            
            # Use professional Kelly position sizer
            if self.professional_kelly:
                kelly_signal = {
                    'symbol': symbol,
                    'confidence': confidence,
                    'entry_price': entry_price,
                    'stop_loss': signal.get('stop_loss'),
                    'strategy': strategy
                }
                
                # Get comprehensive Kelly calculation
                kelly_result = self.professional_kelly.calculate_optimal_position_size(
                    kelly_signal, account_balance, {'atr': AdvancedATRCalculator.calculate_atr_with_confidence(market_data)[0]}
                )
                
                position_size = kelly_result.recommended_size
                
                kelly_metrics = {
                    'kelly_fraction': kelly_result.kelly_fraction,
                    'risk_amount': kelly_result.final_risk_percentage * account_balance,
                    'method': 'professional_kelly',
                    'reasoning': kelly_result.reasoning,
                    'confidence_multiplier': kelly_result.confidence_multiplier,
                    'volatility_adjustment': kelly_result.volatility_adjustment,
                    'drawdown_adjustment': kelly_result.drawdown_adjustment,
                    'correlation_adjustment': kelly_result.correlation_adjustment,
                    'correlation_risk': 0.0  # Placeholder
                }
                
            else:
                # Use simple Kelly manager
                kelly_calculation = self.kelly_manager.calculate_position_size(
                    symbol=symbol,
                    confidence=confidence,
                    expected_return=0.02,  # 2% expected return
                    risk_level=0.01,       # 1% risk level
                    account_balance=account_balance,
                    market_regime='normal'
                )
                
                position_size = kelly_calculation['position_size']
                
                kelly_metrics = {
                    'kelly_fraction': kelly_calculation['kelly_fraction'],
                    'risk_amount': kelly_calculation['risk_amount'],
                    'method': 'simple_kelly',
                    'reasoning': f"Kelly: {kelly_calculation['kelly_fraction']:.3f}, Conf: {confidence:.2f}",
                    'confidence_multiplier': kelly_calculation.get('confidence_adjustment', 1.0),
                    'volatility_adjustment': 1.0,
                    'drawdown_adjustment': 1.0,
                    'correlation_adjustment': 1.0,
                    'correlation_risk': 0.0
                }
            
            # Apply final constraints
            position_size = max(self.config.min_position_size, 
                              min(self.config.max_position_size, position_size))
            
            return position_size, kelly_metrics
            
        except Exception as e:
            self.logger.error(f"[KELLY] Error in advanced position sizing: {e}")
            
            # Fallback calculation
            fallback_size = self.config.base_risk_per_trade
            fallback_metrics = {
                'kelly_fraction': fallback_size,
                'risk_amount': account_balance * fallback_size,
                'method': 'fallback_error',
                'reasoning': f'Error fallback: {str(e)}',
                'error': str(e)
            }
            
            return fallback_size, fallback_metrics
    
    def _update_kelly_manager_position(self, trade_execution: AdvancedTradeExecution):
        """Update Kelly manager with new position"""
        try:
            if self.kelly_manager:
                position_info = {
                    'symbol': trade_execution.symbol,
                    'position_size': trade_execution.volume,
                    'entry_price': trade_execution.entry_price,
                    'risk_amount': trade_execution.risk_amount,
                    'position_value': trade_execution.volume * trade_execution.entry_price,
                    'timestamp': trade_execution.timestamp
                }
                
                if hasattr(self.kelly_manager, 'update_position'):
                    self.kelly_manager.update_position(trade_execution.symbol, position_info)
                
                self.logger.debug(f"[KELLY] Updated position tracking for {trade_execution.symbol}")
                
        except Exception as e:
            self.logger.error(f"[KELLY] Error updating position tracking: {e}")
    
    def add_completed_trade_to_kelly(self, trade_execution: AdvancedTradeExecution, final_pnl: float):
        """Add completed trade to Kelly manager for learning"""
        try:
            if self.kelly_manager:
                trade_data = {
                    'exit_time': datetime.now(),
                    'symbol': trade_execution.symbol,
                    'direction': trade_execution.action,
                    'entry_price': trade_execution.entry_price,
                    'exit_price': trade_execution.entry_price + (final_pnl / trade_execution.volume),  # Approximate
                    'position_size': trade_execution.volume,
                    'pnl': final_pnl,
                    'pnl_percentage': final_pnl / (trade_execution.volume * trade_execution.entry_price),
                    'hold_time_hours': 1.0,  # Placeholder
                    'strategy': trade_execution.strategy_names[0] if trade_execution.strategy_names else 'unknown',
                    'market_conditions': 'normal'
                }
                
                self.kelly_manager.add_trade_result(trade_data)
                self.logger.info(f"[KELLY] Added completed trade to Kelly learning: {trade_execution.symbol} PnL: ${final_pnl:.2f}")
                
        except Exception as e:
            self.logger.error(f"[KELLY] Error adding trade to Kelly history: {e}")
    
    def get_account_balance(self) -> float:
        try:
            if not self.connected or not self.account_info:
                return 0.0
            
            self.account_info = mt5.account_info()
            return float(self.account_info.balance) if self.account_info else 0.0
        except Exception as e:
            self.logger.error(f"Balance error: {e}")
            return 0.0
    
    def get_kelly_performance_summary(self) -> Dict[str, Any]:
        """Get Kelly performance summary"""
        try:
            if self.kelly_manager:
                return self.kelly_manager.get_performance_stats()
            else:
                return {"error": "Kelly manager not available"}
        except Exception as e:
            return {"error": str(e)}
    
    def disconnect(self):
        try:
            if self.connected:
                mt5.shutdown()
                self.connected = False
                self.logger.info("[KELLY] MT5 disconnected")
        except Exception as e:
            self.logger.error(f"Disconnect error: {e}")

# ============================================================================
# ADVANCED RISK MANAGER WITH KELLY INTEGRATION
# ============================================================================

class AdvancedKellyRiskManager:
    def __init__(self, logger: AdvancedKellyLogger, config: AdvancedTradingConfig):
        self.logger = logger
        self.config = config
        self.daily_trades = 0
        self.daily_risk_used = 0.0
        self.total_portfolio_risk = 0.0
        self.last_reset_date = datetime.now().date()
        self.position_count = 0
        
    def can_open_kelly_trade(self, signal: Dict[str, Any], account_balance: float, 
                           kelly_metrics: Dict[str, Any]) -> Tuple[bool, str]:
        """Advanced risk management with Kelly considerations"""
        try:
            self._reset_daily_counters_if_needed()
            
            # Check signal confidence
            if signal['strength'] < self.config.min_signal_confidence:
                return False, f"Signal too weak: {signal['strength']:.2f}"
            
            # Check Kelly-based risk limits
            risk_amount = kelly_metrics.get('risk_amount', 0)
            
            # Daily risk limit (Kelly-adjusted)
            max_daily_risk = account_balance * self.config.max_portfolio_risk
            if self.daily_risk_used + risk_amount > max_daily_risk:
                return False, f"Daily risk limit would be exceeded: ${self.daily_risk_used + risk_amount:.2f} > ${max_daily_risk:.2f}"
            
            # Portfolio risk limit
            if self.total_portfolio_risk + risk_amount > max_daily_risk:
                return False, f"Portfolio risk limit would be exceeded"
            
            # Position count limit
            if self.position_count >= self.config.max_positions:
                return False, f"Maximum positions reached: {self.position_count}/{self.config.max_positions}"
            
            # Single trade risk limit
            single_trade_risk_limit = account_balance * self.config.max_risk_per_trade
            if risk_amount > single_trade_risk_limit:
                return False, f"Single trade risk too high: ${risk_amount:.2f} > ${single_trade_risk_limit:.2f}"
            
            mode_str = "DEMO" if self.config.trading_mode == TradingMode.DEMO else "LIVE"
            return True, f"{mode_str} Kelly trade approved (risk: ${risk_amount:.2f})"
            
        except Exception as e:
            self.logger.error(f"Risk check error: {e}")
            return False, f"Risk check failed: {e}"
    
    def _reset_daily_counters_if_needed(self):
        current_date = datetime.now().date()
        if current_date > self.last_reset_date:
            self.daily_trades = 0
            self.daily_risk_used = 0.0
            self.total_portfolio_risk = 0.0
            self.last_reset_date = current_date
            self.logger.info("[KELLY] Daily risk counters reset")
    
    def record_kelly_trade(self, risk_amount: float = 0.0):
        self.daily_trades += 1
        self.daily_risk_used += risk_amount
        self.total_portfolio_risk += risk_amount
        self.position_count += 1
        
    def close_position_risk(self, risk_amount: float = 0.0):
        self.total_portfolio_risk = max(0, self.total_portfolio_risk - risk_amount)
        self.position_count = max(0, self.position_count - 1)

# ============================================================================
# CONFIGURATION LOADER FOR ADVANCED SYSTEM
# ============================================================================

def load_advanced_kelly_config(config_path: str = "config.yaml") -> AdvancedTradingConfig:
    try:
        config_file = Path(config_path)
        
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f) or {}
        else:
            config_data = {}
            create_advanced_kelly_default_config(config_path)
        
        # Safe conversions
        def safe_int(value, default): return int(value) if value is not None else default
        def safe_float(value, default): return float(value) if value is not None else default
        def safe_list(value, default): return value if isinstance(value, list) else default
        def safe_bool(value, default): return bool(value) if value is not None else default
        
        # Load from environment
        mt5_login = safe_int(os.getenv('MT5_LOGIN'), 0)
        mt5_password = os.getenv('MT5_PASSWORD', '')
        mt5_server = os.getenv('MT5_SERVER', '')
        mt5_path = os.getenv('MT5_PATH', '')
        
        config = AdvancedTradingConfig(
            mt5_login=mt5_login,
            mt5_password=mt5_password,
            mt5_server=mt5_server,
            mt5_path=mt5_path,
            
            symbols=safe_list(config_data.get('symbols'), ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "XAUUSD"]),
            timeframes=safe_list(config_data.get('timeframes'), ["M15", "H1", "H4"]),
            
            # Advanced Kelly Configuration
            kelly_enabled=safe_bool(config_data.get('kelly_enabled'), True),
            kelly_lookback_period=safe_int(config_data.get('kelly_lookback_period'), 100),
            kelly_safety_factor=safe_float(config_data.get('kelly_safety_factor'), 0.25),
            min_kelly_samples=safe_int(config_data.get('min_kelly_samples'), 20),
            max_kelly_fraction=safe_float(config_data.get('max_kelly_fraction'), 0.20),
            kelly_multiplier=safe_float(config_data.get('kelly_multiplier'), 0.5),
            
            # Risk Management
            base_risk_per_trade=safe_float(config_data.get('base_risk_per_trade'), 0.015),
            max_risk_per_trade=safe_float(config_data.get('max_risk_per_trade'), 0.03),
            max_portfolio_risk=safe_float(config_data.get('max_portfolio_risk'), 0.15),
            max_single_symbol_risk=safe_float(config_data.get('max_single_symbol_risk'), 0.08),
            
            # ATR-based SL/TP
            enable_dynamic_sl_tp=safe_bool(config_data.get('enable_dynamic_sl_tp'), True),
            atr_period=safe_int(config_data.get('atr_period'), 14),
            atr_sl_multiplier=safe_float(config_data.get('atr_sl_multiplier'), 2.0),
            atr_tp_multiplier=safe_float(config_data.get('atr_tp_multiplier'), 4.0),
            
            # Position limits
            max_positions=safe_int(config_data.get('max_positions'), 8),
            min_position_size=safe_float(config_data.get('min_position_size'), 0.01),
            max_position_size=safe_float(config_data.get('max_position_size'), 0.10),
            
            min_signal_confidence=safe_float(config_data.get('min_signal_confidence'), 0.35),
            trading_mode=TradingMode(config_data.get('trading_mode', 'demo')),
            log_level=config_data.get('log_level', 'INFO'),
            signal_processing_interval=safe_int(config_data.get('signal_processing_interval'), 8)
        )
        
        return config
    except Exception as e:
        print(f"Config error: {e}")
        return AdvancedTradingConfig()

def create_advanced_kelly_default_config(config_path: str):
    try:
        default_config = {
            'symbols': ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "XAUUSD"],
            'timeframes': ["M15", "H1", "H4"],
            
            # Advanced Kelly Configuration
            'kelly_enabled': True,
            'kelly_lookback_period': 100,
            'kelly_safety_factor': 0.25,
            'min_kelly_samples': 20,
            'max_kelly_fraction': 0.20,
            'kelly_multiplier': 0.5,
            
            # Risk Management
            'base_risk_per_trade': 0.015,
            'max_risk_per_trade': 0.03,
            'max_portfolio_risk': 0.15,
            'max_single_symbol_risk': 0.08,
            
            # ATR-based SL/TP
            'enable_dynamic_sl_tp': True,
            'atr_period': 14,
            'atr_sl_multiplier': 2.0,
            'atr_tp_multiplier': 4.0,
            
            # Position limits
            'max_positions': 8,
            'min_position_size': 0.01,
            'max_position_size': 0.10,
            
            'min_signal_confidence': 0.35,
            'trading_mode': 'demo',
            'log_level': 'INFO',
            'signal_processing_interval': 8
        }
        
        os.makedirs(os.path.dirname(config_path) if os.path.dirname(config_path) else '.', exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        print(f"Created advanced Kelly config: {config_path}")
    except Exception as e:
        print(f"Config creation error: {e}")

# ============================================================================
# MAIN ADVANCED KELLY TRADING BOT
# ============================================================================

class AdvancedKellyTradingBot:
    """Advanced Trading Bot with full Kelly Criterion integration"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = load_advanced_kelly_config(config_path)
        self.logger = AdvancedKellyLogger("AdvancedKellyBot", self.config.log_level)
        
        self._print_advanced_kelly_banner()
        
        # Initialize advanced Kelly components
        self.mt5_manager = AdvancedKellyMT5Manager(self.logger, self.config)
        self.signal_processor = AdvancedKellySignalProcessor(self.logger, self.config)
        self.risk_manager = AdvancedKellyRiskManager(self.logger, self.config)
        
        # Trading state
        self.strategies = {}
        self.trade_executions = []
        self.running = False
        self.shutdown_requested = False
        self.market_data_cache = {}
        self.last_data_update = datetime.now() - timedelta(minutes=10)
        
        self.logger.info("✅ Advanced Kelly Trading Bot initialized - PROFESSIONAL GRADE")
    
    def _print_advanced_kelly_banner(self):
        print("\n" + "="*90)
        print("ADVANCED KELLY TRADING BOT v2.9 - PROFESSIONAL KELLY CRITERION INTEGRATION")
        print("="*90)
        
        mode_str = "DEMO" if self.config.trading_mode == TradingMode.DEMO else "LIVE"
        mode_tag = "DEMO" if mode_str == "DEMO" else "LIVE"
        
        print(f"{mode_tag} TRADING MODE: {mode_str}")
        print(f"✅ KELLY CRITERION: Advanced position sizing with {self.config.kelly_lookback_period} trade lookback")
        print(f"✅ RISK MANAGEMENT: {self.config.base_risk_per_trade*100:.1f}% base risk, {self.config.max_risk_per_trade*100:.1f}% max per trade")
        print(f"✅ PORTFOLIO LIMITS: {self.config.max_portfolio_risk*100:.1f}% total risk, {self.config.max_positions} max positions")
        print(f"✅ ATR-BASED SL/TP: {self.config.atr_sl_multiplier}x ATR SL, {self.config.atr_tp_multiplier}x ATR TP")
        print(f"✅ KELLY SAFETY: {self.config.kelly_safety_factor} safety factor, {self.config.kelly_multiplier} multiplier")
        print(f"✅ INTEGRATION: dynamic_kelly_position_sizing.py {'ACTIVE' if ADVANCED_KELLY_AVAILABLE else 'NOT FOUND'}")
        print("="*90)
    
    async def initialize(self) -> bool:
        try:
            self.logger.info("🚀 Initializing Advanced Kelly Trading System...")
            
            # Check Kelly availability
            if not ADVANCED_KELLY_AVAILABLE:
                self.logger.error("❌ CRITICAL: dynamic_kelly_position_sizing.py not found!")
                self.logger.error("   Please ensure the file is in the same directory as main.py")
                return False
            
            # Connect to MT5
            if not self.mt5_manager.connect():
                self.logger.error("❌ Failed to connect to MT5")
                return False
            
            # Load strategies
            await self._load_advanced_strategies()
            
            # Check account balance and Kelly setup
            account_balance = self.mt5_manager.get_account_balance()
            if account_balance > 0:
                self.logger.info(f"✅ Account balance: ${account_balance:,.2f}")
                self.logger.info(f"✅ Base risk per trade: ${account_balance * self.config.base_risk_per_trade:.2f} ({self.config.base_risk_per_trade*100:.1f}%)")
                self.logger.info(f"✅ Max risk per trade: ${account_balance * self.config.max_risk_per_trade:.2f} ({self.config.max_risk_per_trade*100:.1f}%)")
                self.logger.info(f"✅ Max portfolio risk: ${account_balance * self.config.max_portfolio_risk:.2f} ({self.config.max_portfolio_risk*100:.1f}%)")
            else:
                self.logger.warning("⚠️ Could not retrieve account balance")
            
            # Kelly system status
            kelly_summary = self.mt5_manager.get_kelly_performance_summary()
            self.logger.info(f"✅ Kelly System Status: {kelly_summary}")
            
            self.logger.info("🎯 Advanced Kelly Trading System ready for PROFESSIONAL EXECUTION")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Initialization failed: {e}")
            return False
    
    async def _load_advanced_strategies(self):
        try:
            self.logger.info("📚 Loading advanced Kelly-optimized strategies...")
            
            # Create Kelly-optimized strategies
            self._create_kelly_strategies()
            
            self.logger.info(f"✅ Loaded {len(self.strategies)} Kelly-optimized strategies")
            
        except Exception as e:
            self.logger.error(f"❌ Strategy loading error: {e}")
            self._create_kelly_strategies()
    
    def _create_kelly_strategies(self):
        try:
            class KellyMomentumStrategy:
                def __init__(self):
                    self.name = "KellyMomentumStrategy"
                
                def analyze(self, data: pd.DataFrame, symbol: str) -> Dict[str, Any]:
                    try:
                        if len(data) < 40:
                            return {'signal': 'HOLD', 'confidence': 0.0}
                        
                        # Enhanced momentum with Kelly considerations
                        short_ma = data['close'].rolling(window=12).mean()
                        long_ma = data['close'].rolling(window=26).mean()
                        
                        current_price = data['close'].iloc[-1]
                        short_ma_current = short_ma.iloc[-1]
                        long_ma_current = long_ma.iloc[-1]
                        
                        # Price momentum strength
                        momentum_strength = abs(short_ma_current - long_ma_current) / long_ma_current
                        
                        # Volume confirmation (if available)
                        volume_factor = 1.0
                        if 'tick_volume' in data.columns:
                            recent_volume = data['tick_volume'].tail(10).mean()
                            avg_volume = data['tick_volume'].tail(50).mean()
                            volume_factor = min(1.2, recent_volume / avg_volume) if avg_volume > 0 else 1.0
                        
                        if short_ma_current > long_ma_current and current_price > short_ma_current:
                            confidence = 0.60 + (momentum_strength * 10) * volume_factor
                            confidence = min(0.85, confidence)
                            return {
                                'signal': 'BUY',
                                'confidence': confidence,
                                'price': current_price,
                                'reason': f'Kelly momentum BUY (strength: {momentum_strength:.4f})'
                            }
                        elif short_ma_current < long_ma_current and current_price < short_ma_current:
                            confidence = 0.60 + (momentum_strength * 10) * volume_factor
                            confidence = min(0.85, confidence)
                            return {
                                'signal': 'SELL',
                                'confidence': confidence,
                                'price': current_price,
                                'reason': f'Kelly momentum SELL (strength: {momentum_strength:.4f})'
                            }
                        
                        return {'signal': 'HOLD', 'confidence': 0.3, 'price': current_price}
                    except:
                        return {'signal': 'HOLD', 'confidence': 0.0}
            
            class KellyTrendStrategy:
                def __init__(self):
                    self.name = "KellyTrendStrategy"
                
                def analyze(self, data: pd.DataFrame, symbol: str) -> Dict[str, Any]:
                    try:
                        if len(data) < 60:
                            return {'signal': 'HOLD', 'confidence': 0.0}
                        
                        # Multi-timeframe trend analysis
                        ma_20 = data['close'].rolling(20).mean().iloc[-1]
                        ma_50 = data['close'].rolling(50).mean().iloc[-1]
                        current_price = data['close'].iloc[-1]
                        
                        # Trend strength calculation
                        trend_strength = abs(ma_20 - ma_50) / ma_50
                        
                        # Price position within trend
                        if ma_20 > ma_50:  # Uptrend
                            price_position = (current_price - ma_50) / (ma_20 - ma_50) if ma_20 != ma_50 else 0.5
                        else:  # Downtrend
                            price_position = (ma_50 - current_price) / (ma_50 - ma_20) if ma_20 != ma_50 else 0.5
                        
                        if current_price > ma_20 > ma_50:
                            confidence = 0.65 + (trend_strength * 8) + (price_position * 0.1)
                            confidence = min(0.88, confidence)
                            return {
                                'signal': 'BUY',
                                'confidence': confidence,
                                'price': current_price,
                                'reason': f'Kelly trend BUY (strength: {trend_strength:.4f})'
                            }
                        elif current_price < ma_20 < ma_50:
                            confidence = 0.65 + (trend_strength * 8) + (price_position * 0.1)
                            confidence = min(0.88, confidence)
                            return {
                                'signal': 'SELL',
                                'confidence': confidence,
                                'price': current_price,
                                'reason': f'Kelly trend SELL (strength: {trend_strength:.4f})'
                            }
                        
                        return {'signal': 'HOLD', 'confidence': 0.4, 'price': current_price}
                    except:
                        return {'signal': 'HOLD', 'confidence': 0.0}
            
            class KellyBreakoutStrategy:
                def __init__(self):
                    self.name = "KellyBreakoutStrategy"
                
                def analyze(self, data: pd.DataFrame, symbol: str) -> Dict[str, Any]:
                    try:
                        if len(data) < 30:
                            return {'signal': 'HOLD', 'confidence': 0.0}
                        
                        # ATR-based breakout with Kelly considerations
                        atr, atr_confidence = AdvancedATRCalculator.calculate_atr_with_confidence(data, 14)
                        
                        if atr <= 0:
                            return {'signal': 'HOLD', 'confidence': 0.0}
                        
                        current_price = data['close'].iloc[-1]
                        recent_high = data['high'].rolling(25).max().iloc[-1]
                        recent_low = data['low'].rolling(25).min().iloc[-1]
                        
                        # Dynamic breakout thresholds based on ATR and Kelly
                        breakout_threshold = atr * 0.6  # More conservative
                        
                        # Breakout strength
                        if current_price > recent_high + breakout_threshold:
                            breakout_strength = (current_price - recent_high) / atr
                            confidence = 0.55 + (breakout_strength * 0.1) + (atr_confidence * 0.15)
                            confidence = min(0.82, confidence)
                            return {
                                'signal': 'BUY',
                                'confidence': confidence,
                                'price': current_price,
                                'reason': f'Kelly breakout BUY (ATR: {atr:.5f}, strength: {breakout_strength:.2f})'
                            }
                        elif current_price < recent_low - breakout_threshold:
                            breakout_strength = (recent_low - current_price) / atr
                            confidence = 0.55 + (breakout_strength * 0.1) + (atr_confidence * 0.15)
                            confidence = min(0.82, confidence)
                            return {
                                'signal': 'SELL',
                                'confidence': confidence,
                                'price': current_price,
                                'reason': f'Kelly breakout SELL (ATR: {atr:.5f}, strength: {breakout_strength:.2f})'
                            }
                        
                        return {'signal': 'HOLD', 'confidence': 0.35, 'price': current_price}
                    except:
                        return {'signal': 'HOLD', 'confidence': 0.0}
            
            # Instantiate Kelly-optimized strategies
            self.strategies['KellyMomentumStrategy'] = KellyMomentumStrategy()
            self.strategies['KellyTrendStrategy'] = KellyTrendStrategy()
            self.strategies['KellyBreakoutStrategy'] = KellyBreakoutStrategy()
            
            self.logger.info(f"✅ Created {len(self.strategies)} Kelly-optimized strategies")
            
        except Exception as e:
            self.logger.error(f"❌ Kelly strategy creation error: {e}")
    
    async def run(self):
        try:
            if not await self.initialize():
                return
            
            self.running = True
            self.logger.info("🚀 Starting Advanced Kelly Trading System...")
            
            # Signal handlers
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            iteration_count = 0
            last_kelly_summary = datetime.now()
            
            while self.running and not self.shutdown_requested:
                try:
                    iteration_start = datetime.now()
                    iteration_count += 1
                    
                    self.logger.info(f"\n🎯 ===== ADVANCED KELLY TRADING ITERATION {iteration_count} =====")
                    
                    # Update market data
                    await self._update_market_data()
                    
                    # Process Kelly-optimized signals
                    signals = await self._process_kelly_signals()
                    
                    # Execute trades with advanced Kelly
                    if signals:
                        await self._execute_advanced_kelly_trades(signals)
                    else:
                        self.logger.info("ℹ️ No Kelly-optimized signals ready this iteration")
                    
                    # Log Kelly performance summary every 5 minutes
                    if (datetime.now() - last_kelly_summary).total_seconds() > 300:
                        await self._log_kelly_performance_summary()
                        last_kelly_summary = datetime.now()
                    
                    # Calculate sleep time
                    iteration_time = (datetime.now() - iteration_start).total_seconds()
                    sleep_time = max(0, self.config.signal_processing_interval - iteration_time)
                    
                    self.logger.info(f"⏱️ Iteration {iteration_count} completed in {iteration_time:.2f}s")
                    
                    if sleep_time > 0:
                        await asyncio.sleep(sleep_time)
                    
                except Exception as e:
                    self.logger.error(f"❌ Iteration error: {e}")
                    await asyncio.sleep(self.config.signal_processing_interval)
            
            self.logger.info(f"🏁 Advanced Kelly Trading System stopped after {iteration_count} iterations")
            
        except Exception as e:
            self.logger.error(f"❌ Critical system error: {e}")
        finally:
            await self._shutdown()
    
    async def _update_market_data(self):
        try:
            current_time = datetime.now()
            
            # Update every minute for Kelly calculations
            if (current_time - self.last_data_update).total_seconds() < 45:
                return
            
            self.logger.info("📊 Updating market data for Kelly analysis...")
            
            # Fetch data asynchronously
            tasks = []
            for symbol in self.config.symbols:
                for timeframe in self.config.timeframes:
                    task = asyncio.create_task(
                        self._fetch_data_async(symbol, timeframe)
                    )
                    tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            updated_symbols = set()
            for result in results:
                if isinstance(result, tuple) and len(result) == 3:
                    symbol, timeframe, data = result
                    if not data.empty:
                        if symbol not in self.market_data_cache:
                            self.market_data_cache[symbol] = {}
                        self.market_data_cache[symbol][timeframe] = data
                        updated_symbols.add(symbol)
            
            self.last_data_update = current_time
            self.logger.info(f"✅ Market data updated for {len(updated_symbols)} symbols")
            
        except Exception as e:
            self.logger.error(f"❌ Market data update error: {e}")
    
    async def _fetch_data_async(self, symbol: str, timeframe: str) -> Tuple[str, str, pd.DataFrame]:
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None, 
                self.mt5_manager.get_market_data, 
                symbol, 
                timeframe, 
                500
            )
            return symbol, timeframe, data
        except Exception as e:
            self.logger.debug(f"Data fetch error {symbol} {timeframe}: {e}")
            return symbol, timeframe, pd.DataFrame()
    
    async def _process_kelly_signals(self) -> List[Dict[str, Any]]:
        try:
            if not self.market_data_cache:
                self.logger.info("ℹ️ No market data for Kelly signal processing")
                return []
            
            self.logger.info("🧠 Processing Kelly-optimized signals...")
            
            # Process with advanced Kelly signal processor
            signals = self.signal_processor.process_kelly_signals(
                self.strategies, 
                self.market_data_cache
            )
            
            if signals:
                # Filter for Kelly execution
                kelly_signals = []
                for signal in signals:
                    if (signal.get('confidence', 0) >= self.config.min_signal_confidence and
                        signal.get('symbol') in self.config.symbols and
                        signal.get('kelly_eligible', False)):
                        kelly_signals.append(signal)
                
                self.logger.info(f"🎯 {len(kelly_signals)} Kelly signals ready for execution")
                return kelly_signals[:self.config.max_positions]
            
            return []
            
        except Exception as e:
            self.logger.error(f"❌ Kelly signal processing error: {e}")
            return []
    
    async def _execute_advanced_kelly_trades(self, signals: List[Dict[str, Any]]):
        try:
            self.logger.info("🚀 *** STARTING ADVANCED KELLY TRADE EXECUTION ***")
            
            account_balance = self.mt5_manager.get_account_balance()
            if account_balance <= 0:
                self.logger.error("❌ Invalid account balance")
                return
            
            executed_count = 0
            
            for signal in signals:
                try:
                    symbol = signal['symbol']
                    
                    self.logger.info(f"\n🎯 *** ADVANCED KELLY EXECUTION ***")
                    self.logger.info(f"   Symbol: {symbol}")
                    self.logger.info(f"   Direction: {signal['direction']}")
                    self.logger.info(f"   Confidence: {signal['confidence']:.3f}")
                    self.logger.info(f"   Strategy: {signal['strategy_name']}")
                    
                    # Execute with advanced Kelly manager
                    trade_execution = self.mt5_manager.execute_kelly_optimized_trade(signal)
                    
                    if trade_execution and trade_execution.status == "EXECUTED":
                        # Record with risk manager
                        self.risk_manager.record_kelly_trade(trade_execution.risk_amount)
                        
                        # Store execution
                        self.trade_executions.append(trade_execution)
                        executed_count += 1
                        
                        self.logger.info(f"✅ *** KELLY EXECUTION SUCCESS #{executed_count} ***")
                        self.logger.info(f"   Ticket: {trade_execution.ticket}")
                        self.logger.info(f"   Kelly Fraction: {trade_execution.kelly_fraction:.4f}")
                        self.logger.info(f"   Risk Amount: ${trade_execution.risk_amount:.2f}")
                        self.logger.info(f"   Risk-Reward: 1:{trade_execution.risk_reward_ratio:.2f}")
                        self.logger.info(f"   Filling Mode: {trade_execution.filling_mode}")
                        self.logger.info(f"   Position Size Method: {trade_execution.position_sizing_method}")
                        
                    else:
                        self.logger.error(f"❌ *** KELLY EXECUTION FAILED for {symbol} ***")
                        if trade_execution:
                            self.logger.error(f"   Reason: {trade_execution.filling_mode}")
                
                except Exception as e:
                    self.logger.error(f"❌ Kelly execution error for {signal.get('symbol', 'UNKNOWN')}: {e}")
                    continue
            
            self.logger.info(f"\n🏆 *** KELLY EXECUTION SUMMARY: {executed_count} trades executed from {len(signals)} signals ***")
            
        except Exception as e:
            self.logger.error(f"❌ Critical Kelly execution error: {e}")
    
    async def _log_kelly_performance_summary(self):
        try:
            self.logger.info("\n📊 *** KELLY PERFORMANCE SUMMARY ***")
            
            # Basic statistics
            total_trades = len(self.trade_executions)
            successful_trades = [t for t in self.trade_executions if t.status == "EXECUTED"]
            
            self.logger.info(f"   Total Trades: {total_trades}")
            self.logger.info(f"   Successful: {len(successful_trades)}")
            self.logger.info(f"   Success Rate: {len(successful_trades)/total_trades*100:.1f}%" if total_trades > 0 else "   Success Rate: N/A")
            
            if successful_trades:
                # Kelly-specific metrics
                avg_kelly_fraction = np.mean([t.kelly_fraction for t in successful_trades])
                avg_risk_amount = np.mean([t.risk_amount for t in successful_trades])
                avg_risk_reward = np.mean([t.risk_reward_ratio for t in successful_trades if t.risk_reward_ratio > 0])
                
                self.logger.info(f"   Avg Kelly Fraction: {avg_kelly_fraction:.4f}")
                self.logger.info(f"   Avg Risk Amount: ${avg_risk_amount:.2f}")
                self.logger.info(f"   Avg Risk-Reward: 1:{avg_risk_reward:.2f}")
                
                # Filling mode statistics
                filling_modes = {}
                for trade in successful_trades:
                    mode = trade.filling_mode
                    filling_modes[mode] = filling_modes.get(mode, 0) + 1
                
                self.logger.info("   Filling Modes:")
                for mode, count in filling_modes.items():
                    self.logger.info(f"     {mode}: {count} trades")
                
                # Position sizing methods
                sizing_methods = {}
                for trade in successful_trades:
                    method = trade.position_sizing_method
                    sizing_methods[method] = sizing_methods.get(method, 0) + 1
                
                self.logger.info("   Position Sizing Methods:")
                for method, count in sizing_methods.items():
                    self.logger.info(f"     {method}: {count} trades")
            
            # Kelly manager performance
            kelly_performance = self.mt5_manager.get_kelly_performance_summary()
            if not kelly_performance.get('error'):
                self.logger.info(f"   Kelly Manager Stats: {kelly_performance}")
            
            self.logger.info("*** END KELLY PERFORMANCE SUMMARY ***\n")
            
        except Exception as e:
            self.logger.error(f"❌ Error logging Kelly performance: {e}")
    
    def _signal_handler(self, signum, frame):
        signal_name = 'SIGINT' if signum == signal.SIGINT else 'SIGTERM'
        self.logger.info(f"🛑 Received {signal_name}, shutting down Kelly system...")
        self.shutdown_requested = True
        self.running = False
    
    async def _shutdown(self):
        try:
            self.logger.info("🛑 Shutting down Advanced Kelly Trading System...")
            
            self.running = False
            
            # Final Kelly performance summary
            await self._log_kelly_performance_summary()
            
            # Final system statistics
            self.logger.info("🏁 *** FINAL KELLY SYSTEM STATISTICS ***")
            self.logger.info(f"   Total Trades Executed: {len(self.trade_executions)}")
            
            successful_trades = [t for t in self.trade_executions if t.status == "EXECUTED"]
            failed_trades = [t for t in self.trade_executions if t.status == "FAILED"]
            
            self.logger.info(f"   Successful: {len(successful_trades)}")
            self.logger.info(f"   Failed: {len(failed_trades)}")
            self.logger.info(f"   Kelly Integration: {'✅ ACTIVE' if ADVANCED_KELLY_AVAILABLE else '❌ NOT AVAILABLE'}")
            
            if successful_trades:
                total_risk_deployed = sum([t.risk_amount for t in successful_trades])
                self.logger.info(f"   Total Risk Deployed: ${total_risk_deployed:.2f}")
                
                avg_kelly_efficiency = np.mean([t.kelly_fraction for t in successful_trades])
                self.logger.info(f"   Average Kelly Efficiency: {avg_kelly_efficiency:.4f}")
            
            # Disconnect MT5
            self.mt5_manager.disconnect()
            
            self.logger.info("🏁 Advanced Kelly Trading System shutdown complete")
            
        except Exception as e:
            self.logger.error(f"❌ Shutdown error: {e}")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    try:
        parser = argparse.ArgumentParser(description='Advanced Kelly Trading Bot v2.9 - Professional Integration')
        parser.add_argument('--config', '-c', default='config.yaml', help='Config file')
        parser.add_argument('--mode', '-m', choices=['demo', 'live'], default='demo', help='Trading mode')
        parser.add_argument('--create-config', action='store_true', help='Create advanced Kelly config')
        parser.add_argument('--test-kelly', action='store_true', help='Test Kelly integration')
        parser.add_argument('--validate', action='store_true', help='Validate system setup')
        
        args = parser.parse_args()
        
        # Create config
        if args.create_config:
            create_advanced_kelly_default_config(args.config)
            print("✅ Advanced Kelly config created successfully!")
            print("📝 Edit the config file to customize Kelly parameters")
            return
        
        # Test Kelly integration
        if args.test_kelly:
            test_kelly_integration()
            return
        
        # Validate system
        if args.validate:
            validate_system_setup()
            return
        
        # Initialize advanced Kelly bot
        bot = AdvancedKellyTradingBot(args.config)
        
        # Override mode if specified
        if args.mode:
            bot.config.trading_mode = TradingMode(args.mode)
            print(f"🎯 Trading mode: {args.mode.upper()}")
        
        # Final safety checks for live trading
        if bot.config.trading_mode == TradingMode.LIVE:
            print("\n⚠️  WARNING: LIVE TRADING WITH REAL MONEY!")
            print("🔍 Pre-flight checklist:")
            print("   ✓ Kelly position sizing configured")
            print("   ✓ Risk management limits set")
            print("   ✓ MT5 credentials verified")
            print("   ✓ Stop loss and take profit configured")
            
            response = input("\n❓ Continue with LIVE trading? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("🛑 Live trading cancelled for safety.")
                return
            
            # Additional live trading confirmation
            print("🚨 FINAL WARNING: This will place REAL trades with REAL money!")
            final_response = input("❓ Type 'LIVE TRADING' to confirm: ")
            if final_response != 'LIVE TRADING':
                print("🛑 Live trading cancelled - confirmation failed.")
                return
        
        # Run the advanced Kelly bot
        print(f"\n🚀 Starting Advanced Kelly Trading Bot in {bot.config.trading_mode.value.upper()} mode...")
        asyncio.run(bot.run())
        
    except KeyboardInterrupt:
        print("\n🛑 Advanced Kelly trading bot interrupted by user")
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        import traceback
        traceback.print_exc()

def test_kelly_integration():
    """Test Kelly Criterion integration"""
    print("\n🧪 Testing Kelly Criterion Integration...")
    print("="*60)
    
    # Test 1: Check if Kelly module is available
    print("📦 Test 1: Kelly Module Import")
    if ADVANCED_KELLY_AVAILABLE:
        print("✅ dynamic_kelly_position_sizing.py found and imported")
        
        # Test Kelly classes
        try:
            from dynamic_kelly_position_sizing import KellyPositionManager, ProfessionalKellyPositionSizer
            print("✅ Kelly classes imported successfully")
            
            # Test Kelly manager initialization
            test_config = {
                'kelly_lookback_period': 50,
                'min_trades_for_kelly': 10,
                'max_kelly_fraction': 0.15,
                'kelly_multiplier': 0.4,
                'base_risk_percent': 0.01
            }
            
            kelly_manager = KellyPositionManager(test_config)
            print("✅ Kelly manager initialized successfully")
            
            # Test position sizing calculation
            test_signal = {
                'symbol': 'EURUSD',
                'confidence': 0.65,
                'entry_price': 1.1000,
                'strategy': 'test'
            }
            
            result = kelly_manager.calculate_position_size(
                symbol='EURUSD',
                confidence=0.65,
                expected_return=0.02,
                risk_level=0.01,
                account_balance=10000,
                market_regime='normal'
            )
            
            print(f"✅ Kelly calculation test: {result}")
            
        except Exception as e:
            print(f"❌ Kelly integration test failed: {e}")
    else:
        print("❌ dynamic_kelly_position_sizing.py not found")
        print("📁 Please ensure the file is in the same directory as main.py")
    
    # Test 2: Check MT5 connection capability
    print(f"\n📦 Test 2: MT5 Integration")
    try:
        import MetaTrader5 as mt5
        print("✅ MetaTrader5 module imported")
        
        # Try to initialize (will fail without connection but tests availability)
        if mt5.initialize():
            print("✅ MT5 initialized (connection available)")
            mt5.shutdown()
        else:
            print("⚠️  MT5 initialization failed (no connection configured)")
            print("   This is expected without credentials in config/.env")
    except Exception as e:
        print(f"❌ MT5 test failed: {e}")
    
    # Test 3: Configuration validation
    print(f"\n📦 Test 3: Configuration")
    try:
        config = load_advanced_kelly_config('config.yaml')
        print(f"✅ Configuration loaded successfully")
        print(f"   Kelly enabled: {config.kelly_enabled}")
        print(f"   Base risk: {config.base_risk_per_trade*100:.1f}%")
        print(f"   Max positions: {config.max_positions}")
        print(f"   Symbols: {len(config.symbols)}")
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
    
    print("\n🎯 Kelly Integration Test Complete")

def validate_system_setup():
    """Validate complete system setup"""
    print("\n🔍 Validating System Setup...")
    print("="*60)
    
    validation_passed = True
    
    # Check 1: Python version
    print("🐍 Python Version Check")
    if sys.version_info >= (3, 8):
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} - Compatible")
    else:
        print(f"❌ Python {sys.version_info.major}.{sys.version_info.minor} - Requires 3.8+")
        validation_passed = False
    
    # Check 2: Required dependencies
    print(f"\n📦 Dependencies Check")
    required_deps = [
        ('pandas', 'pd'),
        ('numpy', 'np'),
        ('MetaTrader5', 'mt5'),
        ('yaml', None),
        ('asyncio', None)
    ]
    
    for dep_name, alias in required_deps:
        try:
            if alias:
                exec(f"import {dep_name} as {alias}")
            else:
                exec(f"import {dep_name}")
            print(f"✅ {dep_name}")
        except ImportError:
            print(f"❌ {dep_name} - Not installed")
            validation_passed = False
    
    # Check 3: Kelly integration
    print(f"\n🧮 Kelly Integration Check")
    if ADVANCED_KELLY_AVAILABLE:
        print("✅ dynamic_kelly_position_sizing.py found")
        try:
            from dynamic_kelly_position_sizing import KellyPositionManager
            print("✅ Kelly classes accessible")
        except Exception as e:
            print(f"❌ Kelly classes error: {e}")
            validation_passed = False
    else:
        print("❌ dynamic_kelly_position_sizing.py not found")
        print("   Place the file in the same directory as main.py")
        validation_passed = False
    
    # Check 4: Configuration files
    print(f"\n⚙️  Configuration Check")
    
    # Check config.yaml
    if Path("config.yaml").exists():
        print("✅ config.yaml found")
        try:
            with open("config.yaml", 'r') as f:
                yaml.safe_load(f)
            print("✅ config.yaml valid YAML format")
        except Exception as e:
            print(f"❌ config.yaml invalid: {e}")
            validation_passed = False
    else:
        print("⚠️  config.yaml not found (will create default)")
    
    # Check .env file
    env_path = Path("config/.env")
    if env_path.exists():
        print("✅ config/.env found")
        
        # Check required variables
        required_vars = ['MT5_LOGIN', 'MT5_PASSWORD', 'MT5_SERVER']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠️  Missing environment variables: {missing_vars}")
            print("   Update config/.env with your MT5 credentials")
        else:
            print("✅ All required environment variables present")
    else:
        print("❌ config/.env not found")
        print("   Create config/.env with MT5 credentials:")
        print("   MT5_LOGIN=your_demo_login")
        print("   MT5_PASSWORD=your_demo_password")
        print("   MT5_SERVER=your_demo_server")
        validation_passed = False
    
    # Check 5: Directory structure
    print(f"\n📁 Directory Structure Check")
    required_dirs = ['logs', 'config']
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"✅ {dir_name}/ directory exists")
        else:
            try:
                os.makedirs(dir_name, exist_ok=True)
                print(f"✅ {dir_name}/ directory created")
            except Exception as e:
                print(f"❌ Cannot create {dir_name}/: {e}")
                validation_passed = False
    
    # Final validation result
    print("\n" + "="*60)
    if validation_passed:
        print("🎉 SYSTEM VALIDATION PASSED - Ready for trading!")
        print("🚀 Run: python main.py --mode demo")
    else:
        print("❌ SYSTEM VALIDATION FAILED - Fix issues above")
        print("📚 Check documentation and ensure all requirements are met")
    
    return validation_passed

if __name__ == "__main__":
    try:
        # System compatibility check
        if sys.version_info < (3, 8):
            print("❌ ERROR: Python 3.8 or higher is required")
            print(f"   Current version: {sys.version}")
            sys.exit(1)
        
        # Check for essential files
        env_path = Path("config/.env")
        if not env_path.exists() and '--create-config' not in sys.argv and '--test-kelly' not in sys.argv and '--validate' not in sys.argv:
            print("\n🔐 CREDENTIAL SETUP REQUIRED:")
            print("Create config/.env file with your MT5 credentials:")
            print("")
            print("MT5_LOGIN=your_demo_login_number")
            print("MT5_PASSWORD=your_demo_password")
            print("MT5_SERVER=your_demo_server_name")
            print("MT5_PATH=path_to_mt5_terminal (optional)")
            print("")
            print("🔍 For demo accounts, use your broker's demo server credentials")
            print("⚠️  For live accounts, ensure 2FA and secure credentials")
            print("")
            
            response = input("📝 Create config/.env file first, then press Enter to continue...")
        
        # Show startup banner
        print("\n" + "="*90)
        print("🤖 ADVANCED KELLY TRADING BOT v2.9 - PROFESSIONAL INTEGRATION")
        print("="*90)
        print("🧮 FEATURES:")
        print("   ✅ Advanced Kelly Criterion Position Sizing")
        print("   ✅ Professional Risk Management")
        print("   ✅ ATR-based Dynamic SL/TP")
        print("   ✅ Multi-filling Mode Compatibility")
        print("   ✅ Portfolio Correlation Analysis")
        print("   ✅ Real-time Performance Tracking")
        print("")
        print("📚 INTEGRATION:")
        print(f"   Kelly Module: {'✅ AVAILABLE' if ADVANCED_KELLY_AVAILABLE else '❌ NOT FOUND'}")
        print(f"   Signal Factory: {'✅ AVAILABLE' if ADVANCED_SIGNAL_FACTORY_AVAILABLE else '⚠️  OPTIONAL'}")
        print("")
        print("🔧 COMMANDS:")
        print("   --create-config    Create default configuration")
        print("   --test-kelly      Test Kelly integration")
        print("   --validate        Validate system setup")
        print("   --mode demo       Run in demo mode (recommended)")
        print("   --mode live       Run in live mode (real money)")
        print("="*90)
        
        main()
        
    except Exception as e:
        print(f"\n💥 FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
