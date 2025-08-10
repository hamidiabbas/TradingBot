"""
Enhanced Bot Engine - Main Trading Orchestration
==============================================

Professional-grade trading bot engine that orchestrates all system components
including ML models, data management, strategy execution, risk management,
and order execution for institutional algorithmic trading.

Features:
- Asynchronous multi-strategy execution
- ML model integration with ensemble predictions
- Real-time performance monitoring
- Advanced error handling and recovery
- Dynamic configuration management
- Professional logging and audit trails

Author: Enhanced Trading System
Version: 4.0 Professional
License: Proprietary
"""

import asyncio
import logging
import signal
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path
import json
import yaml
import numpy as np
import pandas as pd
from enum import Enum
import queue
import psutil
import gc
from contextlib import asynccontextmanager

# Core Components
from core.data_manager import EnhancedDataManager
from core.strategy_manager import EnhancedStrategyManager  
from core.risk_manager import EnhancedRiskManager
from core.execution_engine import EnhancedExecutionEngine

# ML Models Integration
from ml_models.ensemble_model import EnhancedEnsembleModel
from ml_models.lstm_model import InstitutionalLSTMModel
from ml_models.random_forest_model import EnhancedRandomForestModel
from ml_models.svm_model import EnhancedSVMModel

# Utilities
from utils.logger import setup_logging
from utils.config import TradingConfig
from utils.metrics import PerformanceTracker
from utils.helpers import format_currency, calculate_pnl

class BotState(Enum):
    """Bot operational states"""
    INITIALIZING = "initializing"
    RUNNING = "running"  
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    EMERGENCY_SHUTDOWN = "emergency_shutdown"

@dataclass
class BotMetrics:
    """Comprehensive bot performance metrics"""
    start_time: datetime = field(default_factory=datetime.utcnow)
    total_trades: int = 0
    successful_trades: int = 0
    failed_trades: int = 0
    total_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    win_rate: float = 0.0
    avg_trade_duration: float = 0.0
    system_uptime: float = 0.0
    ml_predictions_count: int = 0
    ml_accuracy: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0

class EnhancedTradingBotEngine:
    """
    Enhanced Professional Trading Bot Engine
    
    Central orchestrator for the complete algorithmic trading system that
    coordinates data management, ML predictions, strategy execution, risk
    management, and order execution with institutional-grade reliability.
    """
    
    def __init__(self, config_path: str = "config/trading_config.yaml"):
        self.config_path = config_path
        self.config = None
        
        # Core Components
        self.data_manager = None
        self.strategy_manager = None
        self.risk_manager = None
        self.execution_engine = None
        
        # ML Models
        self.ensemble_model = None
        self.lstm_model = None
        self.rf_model = None
        self.svm_model = None
        
        # State Management
        self.state = BotState.INITIALIZING
        self.metrics = BotMetrics()
        self.is_running = False
        self.shutdown_event = asyncio.Event()
        
        # Performance Tracking
        self.performance_tracker = None
        self.trade_history = []
        self.signal_history = []
        
        # Threading and Async
        self.main_loop_task = None
        self.monitoring_task = None
        self.data_update_task = None
        
        # Error Handling
        self.error_count = 0
        self.last_error_time = None
        self.recovery_attempts = 0
        
        # Logging
        self.logger = setup_logging('INFO')
        self.logger.info("🚀 Enhanced Trading Bot Engine initialized")
    
    async def initialize(self) -> bool:
        """Initialize all bot components with comprehensive error handling"""
        try:
            self.logger.info("🔧 Initializing Trading Bot Engine components...")
            self.state = BotState.INITIALIZING
            
            # Load configuration
            if not await self._load_configuration():
                return False
            
            # Initialize core components
            if not await self._initialize_core_components():
                return False
            
            # Initialize ML models
            if not await self._initialize_ml_models():
                return False
            
            # Setup monitoring and performance tracking
            if not await self._setup_monitoring():
                return False
            
            # Validate system readiness
            if not await self._validate_system_readiness():
                return False
            
            self.logger.info("✅ Trading Bot Engine initialization completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Critical error during initialization: {e}")
            self.state = BotState.ERROR
            return False
    
    async def _load_configuration(self) -> bool:
        """Load and validate trading configuration"""
        try:
            self.logger.info("📋 Loading trading configuration...")
            
            if not Path(self.config_path).exists():
                self.logger.error(f"Configuration file not found: {self.config_path}")
                return False
            
            with open(self.config_path, 'r') as f:
                if self.config_path.endswith('.yaml'):
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)
            
            self.config = TradingConfig(config_data)
            
            # Validate critical parameters
            if not self.config.validate():
                self.logger.error("Configuration validation failed")
                return False
            
            self.logger.info(f"✅ Configuration loaded successfully")
            self.logger.info(f"   Trading Symbols: {self.config.symbols}")
            self.logger.info(f"   Strategies Enabled: {self.config.strategies_enabled}")
            self.logger.info(f"   ML Models: {self.config.ml_models_enabled}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            return False
    
    async def _initialize_core_components(self) -> bool:
        """Initialize core trading system components"""
        try:
            self.logger.info("🏗️ Initializing core components...")
            
            # Initialize Data Manager
            self.logger.info("   📊 Initializing Data Manager...")
            self.data_manager = EnhancedDataManager(self.config)
            if not await self.data_manager.initialize():
                self.logger.error("Data Manager initialization failed")
                return False
            
            # Initialize Risk Manager
            self.logger.info("   ⚖️ Initializing Risk Manager...")
            self.risk_manager = EnhancedRiskManager(self.config)
            if not await self.risk_manager.initialize():
                self.logger.error("Risk Manager initialization failed")
                return False
            
            # Initialize Execution Engine
            self.logger.info("   ⚡ Initializing Execution Engine...")
            self.execution_engine = EnhancedExecutionEngine(self.config, self.risk_manager)
            if not await self.execution_engine.initialize():
                self.logger.error("Execution Engine initialization failed")
                return False
            
            # Initialize Strategy Manager
            self.logger.info("   🎯 Initializing Strategy Manager...")
            self.strategy_manager = EnhancedStrategyManager(
                self.config,
                self.data_manager,
                self.risk_manager,
                self.execution_engine
            )
            if not await self.strategy_manager.initialize():
                self.logger.error("Strategy Manager initialization failed")
                return False
            
            self.logger.info("✅ Core components initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing core components: {e}")
            return False
    
    async def _initialize_ml_models(self) -> bool:
        """Initialize ML models with ensemble integration"""
        try:
            self.logger.info("🧠 Initializing ML Models...")
            
            # Initialize individual models if enabled
            models_initialized = []
            
            if 'lstm' in self.config.ml_models_enabled:
                self.logger.info("   🔮 Loading LSTM Model...")
                try:
                    from ml_models.lstm_model import InstitutionalLSTMConfig, InstitutionalLSTMModel
                    lstm_config = InstitutionalLSTMConfig()
                    self.lstm_model = InstitutionalLSTMModel(lstm_config)
                    
                    # Try to load pre-trained model
                    model_path = self.config.get('models', {}).get('lstm_path')
                    if model_path and Path(model_path).exists():
                        self.lstm_model.load_model(model_path)
                        self.logger.info("     ✅ Pre-trained LSTM model loaded")
                    else:
                        self.logger.warning("     ⚠️ No pre-trained LSTM model found - will use untrained model")
                    
                    models_initialized.append('lstm')
                    
                except Exception as e:
                    self.logger.error(f"Failed to initialize LSTM model: {e}")
                    if self.config.require_all_ml_models:
                        return False
            
            if 'random_forest' in self.config.ml_models_enabled:
                self.logger.info("   🌳 Loading Random Forest Model...")
                try:
                    from ml_models.random_forest_model import RandomForestConfig, EnhancedRandomForestModel
                    rf_config = RandomForestConfig()
                    self.rf_model = EnhancedRandomForestModel(rf_config)
                    
                    # Try to load pre-trained model
                    model_path = self.config.get('models', {}).get('rf_path')
                    if model_path and Path(model_path).exists():
                        self.rf_model.load_model(model_path)
                        self.logger.info("     ✅ Pre-trained Random Forest model loaded")
                    else:
                        self.logger.warning("     ⚠️ No pre-trained Random Forest model found")
                    
                    models_initialized.append('random_forest')
                    
                except Exception as e:
                    self.logger.error(f"Failed to initialize Random Forest model: {e}")
                    if self.config.require_all_ml_models:
                        return False
            
            if 'svm' in self.config.ml_models_enabled:
                self.logger.info("   📈 Loading SVM Model...")
                try:
                    from ml_models.svm_model import SVMConfig, EnhancedSVMModel
                    svm_config = SVMConfig()
                    self.svm_model = EnhancedSVMModel(svm_config)
                    
                    # Try to load pre-trained model
                    model_path = self.config.get('models', {}).get('svm_path')
                    if model_path and Path(model_path).exists():
                        self.svm_model.load_model(model_path)
                        self.logger.info("     ✅ Pre-trained SVM model loaded")
                    else:
                        self.logger.warning("     ⚠️ No pre-trained SVM model found")
                    
                    models_initialized.append('svm')
                    
                except Exception as e:
                    self.logger.error(f"Failed to initialize SVM model: {e}")
                    if self.config.require_all_ml_models:
                        return False
            
            # Initialize Ensemble Model if multiple models available
            if len(models_initialized) > 1:
                self.logger.info("   🎭 Initializing Ensemble Model...")
                try:
                    from ml_models.ensemble_model import EnsembleConfig, EnhancedEnsembleModel
                    ensemble_config = EnsembleConfig()
                    self.ensemble_model = EnhancedEnsembleModel(ensemble_config)
                    
                    # Initialize with available models
                    await self.ensemble_model.initialize_models()
                    self.logger.info("     ✅ Ensemble Model initialized successfully")
                    
                except Exception as e:
                    self.logger.error(f"Failed to initialize Ensemble model: {e}")
                    if self.config.require_ensemble:
                        return False
            
            self.logger.info(f"✅ ML Models initialized: {models_initialized}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing ML models: {e}")
            return False
    
    async def _setup_monitoring(self) -> bool:
        """Setup performance monitoring and tracking"""
        try:
            self.logger.info("📊 Setting up performance monitoring...")
            
            # Initialize performance tracker
            self.performance_tracker = PerformanceTracker(
                initial_balance=self.config.initial_balance,
                benchmark_symbol=self.config.get('benchmark_symbol', 'SPY')
            )
            
            # Setup system monitoring
            self.metrics.start_time = datetime.utcnow()
            
            self.logger.info("✅ Performance monitoring setup completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting up monitoring: {e}")
            return False
    
    async def _validate_system_readiness(self) -> bool:
        """Validate all systems are ready for trading"""
        try:
            self.logger.info("🔍 Validating system readiness...")
            
            # Check MT5 connection
            if not await self.data_manager.test_connection():
                self.logger.error("MT5 connection test failed")
                return False
            
            # Check market data availability
            if not await self.data_manager.validate_market_data():
                self.logger.error("Market data validation failed")
                return False
            
            # Check risk management parameters
            if not self.risk_manager.validate_risk_parameters():
                self.logger.error("Risk parameters validation failed")
                return False
            
            # Check execution engine readiness
            if not await self.execution_engine.test_execution():
                self.logger.error("Execution engine test failed")
                return False
            
            # Check strategy readiness
            if not await self.strategy_manager.validate_strategies():
                self.logger.error("Strategy validation failed")
                return False
            
            self.logger.info("✅ System readiness validation completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during system validation: {e}")
            return False
    
    async def start_trading(self) -> None:
        """Start the main trading loop with comprehensive orchestration"""
        try:
            if self.state != BotState.INITIALIZING:
                self.logger.error("Bot must be initialized before starting trading")
                return
            
            self.logger.info("🚀 Starting Enhanced Trading Bot...")
            self.logger.info("=" * 80)
            self.logger.info(f"🎯 Trading Symbols: {self.config.symbols}")
            self.logger.info(f"💰 Initial Balance: ${self.config.initial_balance:,.2f}")
            self.logger.info(f"⚖️ Max Risk per Trade: {self.config.max_risk_per_trade * 100:.1f}%")
            self.logger.info(f"🧠 ML Models: {self.config.ml_models_enabled}")
            self.logger.info(f"📈 Strategies: {self.config.strategies_enabled}")
            self.logger.info("=" * 80)
            
            self.state = BotState.RUNNING
            self.is_running = True
            self.metrics.start_time = datetime.utcnow()
            
            # Start main trading loop
            self.main_loop_task = asyncio.create_task(self._main_trading_loop())
            
            # Start monitoring task
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            # Start data update task
            self.data_update_task = asyncio.create_task(self._data_update_loop())
            
            # Wait for shutdown signal
            await self.shutdown_event.wait()
            
        except Exception as e:
            self.logger.error(f"Critical error in trading loop: {e}")
            await self.emergency_shutdown()
    
    async def _main_trading_loop(self) -> None:
        """Main trading loop with ML integration and strategy coordination"""
        try:
            self.logger.info("🔄 Starting main trading loop...")
            
            while self.is_running and self.state == BotState.RUNNING:
                try:
                    loop_start_time = time.time()
                    
                    # Update system metrics
                    await self._update_system_metrics()
                    
                    # Check market session and trading hours
                    if not await self._check_trading_conditions():
                        await asyncio.sleep(60)  # Wait 1 minute if not trading hours
                        continue
                    
                    # Get latest market data for all symbols
                    market_data = await self.data_manager.get_latest_data()
                    if not market_data:
                        self.logger.warning("No market data available, skipping cycle")
                        await asyncio.sleep(30)
                        continue
                    
                    # Process each trading symbol
                    for symbol in self.config.symbols:
                        try:
                            if symbol not in market_data:
                                continue
                            
                            await self._process_symbol(symbol, market_data[symbol])
                            
                        except Exception as e:
                            self.logger.error(f"Error processing {symbol}: {e}")
                            continue
                    
                    # Risk management checks
                    await self._perform_risk_checks()
                    
                    # Update performance metrics
                    await self._update_performance_metrics()
                    
                    # Calculate loop execution time
                    loop_time = time.time() - loop_start_time
                    
                    # Adaptive sleep based on market volatility and loop performance
                    sleep_time = max(1, self.config.trading_loop_interval - loop_time)
                    await asyncio.sleep(sleep_time)
                    
                except Exception as e:
                    self.logger.error(f"Error in main trading loop iteration: {e}")
                    self.error_count += 1
                    
                    # Exponential backoff for errors
                    if self.error_count > 5:
                        self.logger.error("Too many consecutive errors, pausing trading")
                        await self.pause_trading()
                        break
                    
                    await asyncio.sleep(min(30, 2 ** self.error_count))
            
        except Exception as e:
            self.logger.critical(f"Critical error in main trading loop: {e}")
            await self.emergency_shutdown()
    
    async def _process_symbol(self, symbol: str, data: pd.DataFrame) -> None:
        """Process trading signals for a specific symbol"""
        try:
            # Get ML predictions if models are available
            ml_predictions = await self._get_ml_predictions(symbol, data)
            
            # Get strategy signals
            strategy_signals = await self.strategy_manager.generate_signals(symbol, data, ml_predictions)
            
            # Combine and evaluate signals
            if strategy_signals:
                # Process each signal through risk management
                for signal in strategy_signals:
                    # Validate signal with risk manager
                    validated_signal = await self.risk_manager.validate_signal(signal, ml_predictions)
                    
                    if validated_signal:
                        # Execute trade through execution engine
                        execution_result = await self.execution_engine.execute_signal(validated_signal)
                        
                        # Track execution
                        if execution_result:
                            self.metrics.total_trades += 1
                            if execution_result.success:
                                self.metrics.successful_trades += 1
                            else:
                                self.metrics.failed_trades += 1
                            
                            # Store trade history
                            self.trade_history.append({
                                'timestamp': datetime.utcnow(),
                                'symbol': symbol,
                                'signal': signal,
                                'ml_predictions': ml_predictions,
                                'execution_result': execution_result
                            })
                            
                            self.logger.info(
                                f"📊 Trade executed: {symbol} | "
                                f"Signal: {signal.action} | "
                                f"ML Confidence: {ml_predictions.get('confidence', 'N/A') if ml_predictions else 'N/A'} | "
                                f"Result: {'✅' if execution_result.success else '❌'}"
                            )
            
        except Exception as e:
            self.logger.error(f"Error processing symbol {symbol}: {e}")
    
    async def _get_ml_predictions(self, symbol: str, data: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Get ML model predictions for trading decisions"""
        try:
            if not any([self.lstm_model, self.rf_model, self.svm_model, self.ensemble_model]):
                return None
            
            predictions = {}
            
            # Get ensemble prediction if available
            if self.ensemble_model:
                try:
                    ensemble_pred = self.ensemble_model.predict(data)
                    predictions['ensemble'] = {
                        'prediction': ensemble_pred.final_prediction,
                        'confidence': ensemble_pred.confidence,
                        'model_agreement': ensemble_pred.model_agreement,
                        'risk_assessment': ensemble_pred.risk_assessment
                    }
                    self.metrics.ml_predictions_count += 1
                    
                except Exception as e:
                    self.logger.warning(f"Ensemble prediction failed for {symbol}: {e}")
            
            # Get individual model predictions for backup/comparison
            if self.lstm_model:
                try:
                    lstm_pred = self.lstm_model.predict(data)
                    predictions['lstm'] = {
                        'predictions': lstm_pred.predictions,
                        'confidence_scores': lstm_pred.confidence_scores,
                        'directional_probabilities': lstm_pred.directional_probabilities
                    }
                except Exception as e:
                    self.logger.warning(f"LSTM prediction failed for {symbol}: {e}")
            
            if self.rf_model:
                try:
                    rf_pred = self.rf_model.predict(data)
                    predictions['random_forest'] = {
                        'signal': rf_pred.signal_name,
                        'confidence': rf_pred.confidence,
                        'probabilities': rf_pred.probabilities
                    }
                except Exception as e:
                    self.logger.warning(f"Random Forest prediction failed for {symbol}: {e}")
            
            if self.svm_model:
                try:
                    svm_pred = self.svm_model.predict(data)
                    predictions['svm'] = {
                        'regime': svm_pred.regime_name,
                        'confidence': svm_pred.confidence,
                        'regime_stability': svm_pred.regime_stability
                    }
                except Exception as e:
                    self.logger.warning(f"SVM prediction failed for {symbol}: {e}")
            
            return predictions if predictions else None
            
        except Exception as e:
            self.logger.error(f"Error getting ML predictions for {symbol}: {e}")
            return None
    
    async def _check_trading_conditions(self) -> bool:
        """Check if current conditions allow trading"""
        try:
            # Check trading hours
            current_time = datetime.utcnow()
            if not self._is_trading_hours(current_time):
                return False
            
            # Check if market is open for any of our symbols
            if not await self.data_manager.is_market_open():
                return False
            
            # Check system health
            if self.state != BotState.RUNNING:
                return False
            
            # Check risk limits
            if not await self.risk_manager.can_trade():
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking trading conditions: {e}")
            return False
    
    def _is_trading_hours(self, current_time: datetime) -> bool:
        """Check if current time is within trading hours"""
        try:
            trading_hours = self.config.get('trading_hours', {})
            
            # Default to 24/7 if no restrictions
            if not trading_hours:
                return True
            
            # Check day of week
            if 'exclude_weekends' in trading_hours and trading_hours['exclude_weekends']:
                if current_time.weekday() >= 5:  # Saturday = 5, Sunday = 6
                    return False
            
            # Check specific hours
            if 'start_hour' in trading_hours and 'end_hour' in trading_hours:
                current_hour = current_time.hour
                start_hour = trading_hours['start_hour']
                end_hour = trading_hours['end_hour']
                
                if start_hour <= end_hour:
                    return start_hour <= current_hour < end_hour
                else:  # Overnight session
                    return current_hour >= start_hour or current_hour < end_hour
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking trading hours: {e}")
            return True  # Default to allowing trading
    
    async def _perform_risk_checks(self) -> None:
        """Perform comprehensive risk management checks"""
        try:
            # Check portfolio heat
            portfolio_risk = await self.risk_manager.calculate_portfolio_heat()
            
            if portfolio_risk > self.config.max_portfolio_risk:
                self.logger.warning(f"Portfolio risk too high: {portfolio_risk:.2%}")
                await self.risk_manager.reduce_exposure()
            
            # Check drawdown
            current_drawdown = await self.performance_tracker.get_current_drawdown()
            
            if current_drawdown > self.config.max_drawdown:
                self.logger.error(f"Maximum drawdown exceeded: {current_drawdown:.2%}")
                await self.pause_trading()
            
            # Check daily loss limit
            daily_pnl = await self.performance_tracker.get_daily_pnl()
            
            if daily_pnl < -abs(self.config.max_daily_loss * self.config.initial_balance):
                self.logger.error(f"Daily loss limit exceeded: ${daily_pnl:,.2f}")
                await self.pause_trading()
            
        except Exception as e:
            self.logger.error(f"Error in risk checks: {e}")
    
    async def _update_system_metrics(self) -> None:
        """Update comprehensive system performance metrics"""
        try:
            # System metrics
            self.metrics.memory_usage_mb = psutil.Process().memory_info().rss / 1024 / 1024
            self.metrics.cpu_usage_percent = psutil.cpu_percent()
            
            # Trading metrics
            if self.metrics.total_trades > 0:
                self.metrics.win_rate = self.metrics.successful_trades / self.metrics.total_trades
            
            # Uptime
            if self.metrics.start_time:
                uptime_delta = datetime.utcnow() - self.metrics.start_time
                self.metrics.system_uptime = uptime_delta.total_seconds() / 3600  # Hours
            
            # ML accuracy (simplified)
            if self.metrics.ml_predictions_count > 0:
                # This would need actual prediction vs outcome tracking
                self.metrics.ml_accuracy = self.metrics.successful_trades / max(1, self.metrics.total_trades)
            
        except Exception as e:
            self.logger.error(f"Error updating system metrics: {e}")
    
    async def _update_performance_metrics(self) -> None:
        """Update trading performance metrics"""
        try:
            if self.performance_tracker:
                # Update performance tracking
                current_balance = await self.execution_engine.get_account_balance()
                self.performance_tracker.update_balance(current_balance)
                
                # Calculate key metrics
                self.metrics.total_pnl = current_balance - self.config.initial_balance
                self.metrics.unrealized_pnl = await self.execution_engine.get_unrealized_pnl()
                self.metrics.max_drawdown = await self.performance_tracker.get_max_drawdown()
                self.metrics.sharpe_ratio = await self.performance_tracker.get_sharpe_ratio()
            
        except Exception as e:
            self.logger.error(f"Error updating performance metrics: {e}")
    
    async def _monitoring_loop(self) -> None:
        """Background monitoring and reporting loop"""
        try:
            while self.is_running:
                try:
                    # Log periodic status
                    await self._log_status_report()
                    
                    # Check for alerts
                    await self._check_alerts()
                    
                    # Cleanup old data
                    await self._cleanup_old_data()
                    
                    # Memory management
                    if self.metrics.memory_usage_mb > 1000:  # 1GB threshold
                        gc.collect()
                    
                    await asyncio.sleep(300)  # 5 minutes
                    
                except Exception as e:
                    self.logger.error(f"Error in monitoring loop: {e}")
                    await asyncio.sleep(60)
            
        except Exception as e:
            self.logger.error(f"Critical error in monitoring loop: {e}")
    
    async def _data_update_loop(self) -> None:
        """Background data update and maintenance loop"""
        try:
            while self.is_running:
                try:
                    # Update market data
                    await self.data_manager.update_all_data()
                    
                    # Retrain models if needed
                    await self._check_model_retraining()
                    
                    # Update risk parameters
                    await self.risk_manager.update_risk_parameters()
                    
                    await asyncio.sleep(self.config.get('data_update_interval', 3600))  # 1 hour
                    
                except Exception as e:
                    self.logger.error(f"Error in data update loop: {e}")
                    await asyncio.sleep(300)
            
        except Exception as e:
            self.logger.error(f"Critical error in data update loop: {e}")
    
    async def _log_status_report(self) -> None:
        """Log comprehensive status report"""
        try:
            uptime_hours = self.metrics.system_uptime
            
            self.logger.info("📊 === TRADING BOT STATUS REPORT ===")
            self.logger.info(f"🕐 Uptime: {uptime_hours:.1f} hours")
            self.logger.info(f"🎯 State: {self.state.value.upper()}")
            self.logger.info(f"💹 Total Trades: {self.metrics.total_trades}")
            self.logger.info(f"✅ Successful: {self.metrics.successful_trades}")
            self.logger.info(f"❌ Failed: {self.metrics.failed_trades}")
            self.logger.info(f"🏆 Win Rate: {self.metrics.win_rate:.1%}")
            self.logger.info(f"💰 Total P&L: ${self.metrics.total_pnl:,.2f}")
            self.logger.info(f"📉 Max Drawdown: {self.metrics.max_drawdown:.1%}")
            self.logger.info(f"📈 Sharpe Ratio: {self.metrics.sharpe_ratio:.2f}")
            self.logger.info(f"🧠 ML Predictions: {self.metrics.ml_predictions_count}")
            self.logger.info(f"🎯 ML Accuracy: {self.metrics.ml_accuracy:.1%}")
            self.logger.info(f"💾 Memory: {self.metrics.memory_usage_mb:.1f} MB")
            self.logger.info(f"🖥️ CPU: {self.metrics.cpu_usage_percent:.1f}%")
            self.logger.info("=" * 40)
            
        except Exception as e:
            self.logger.error(f"Error logging status report: {e}")
    
    async def _check_alerts(self) -> None:
        """Check for alert conditions and send notifications"""
        try:
            alerts = []
            
            # Performance alerts
            if self.metrics.win_rate < 0.4 and self.metrics.total_trades > 10:
                alerts.append(f"Low win rate: {self.metrics.win_rate:.1%}")
            
            if self.metrics.max_drawdown > 0.1:
                alerts.append(f"High drawdown: {self.metrics.max_drawdown:.1%}")
            
            # System alerts
            if self.metrics.memory_usage_mb > 2000:
                alerts.append(f"High memory usage: {self.metrics.memory_usage_mb:.1f} MB")
            
            if self.metrics.cpu_usage_percent > 80:
                alerts.append(f"High CPU usage: {self.metrics.cpu_usage_percent:.1f}%")
            
            # Send alerts if any
            if alerts:
                alert_message = "🚨 TRADING BOT ALERTS:\n" + "\n".join(f"• {alert}" for alert in alerts)
                self.logger.warning(alert_message)
                
                # Send notifications (email, Slack, etc.)
                # Implementation would depend on notification system
                
        except Exception as e:
            self.logger.error(f"Error checking alerts: {e}")
    
    async def _cleanup_old_data(self) -> None:
        """Clean up old data to prevent memory leaks"""
        try:
            current_time = datetime.utcnow()
            
            # Clean trade history (keep last 1000 trades)
            if len(self.trade_history) > 1000:
                self.trade_history = self.trade_history[-1000:]
            
            # Clean signal history (keep last 24 hours)
            cutoff_time = current_time - timedelta(hours=24)
            self.signal_history = [
                signal for signal in self.signal_history 
                if signal.get('timestamp', current_time) > cutoff_time
            ]
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {e}")
    
    async def _check_model_retraining(self) -> None:
        """Check if ML models need retraining"""
        try:
            if not self.config.enable_model_retraining:
                return
            
            # Check if enough time has passed since last training
            last_training = self.config.get('last_model_training')
            if last_training:
                last_training_time = datetime.fromisoformat(last_training)
                if datetime.utcnow() - last_training_time < timedelta(days=7):
                    return
            
            # Check if model performance has degraded
            if self.metrics.ml_accuracy < 0.5 and self.metrics.ml_predictions_count > 100:
                self.logger.info("🔄 Model performance degraded, scheduling retraining...")
                # Schedule retraining (implementation depends on model management system)
            
        except Exception as e:
            self.logger.error(f"Error checking model retraining: {e}")
    
    async def pause_trading(self) -> None:
        """Pause trading operations"""
        try:
            self.logger.warning("⏸️ Pausing trading operations...")
            self.state = BotState.PAUSED
            
            # Close all positions if configured to do so
            if self.config.get('close_positions_on_pause', True):
                await self.execution_engine.close_all_positions()
            
        except Exception as e:
            self.logger.error(f"Error pausing trading: {e}")
    
    async def resume_trading(self) -> None:
        """Resume trading operations"""
        try:
            self.logger.info("▶️ Resuming trading operations...")
            
            # Validate system readiness
            if await self._validate_system_readiness():
                self.state = BotState.RUNNING
                self.error_count = 0  # Reset error count
                self.logger.info("✅ Trading resumed successfully")
            else:
                self.logger.error("❌ System validation failed, cannot resume trading")
                
        except Exception as e:
            self.logger.error(f"Error resuming trading: {e}")
    
    async def stop_trading(self) -> None:
        """Gracefully stop trading operations"""
        try:
            self.logger.info("🛑 Stopping trading operations...")
            self.state = BotState.STOPPING
            self.is_running = False
            
            # Cancel all pending orders
            await self.execution_engine.cancel_all_orders()
            
            # Close positions if configured
            if self.config.get('close_positions_on_stop', False):
                await self.execution_engine.close_all_positions()
            
            # Stop all tasks
            if self.main_loop_task and not self.main_loop_task.done():
                self.main_loop_task.cancel()
            
            if self.monitoring_task and not self.monitoring_task.done():
                self.monitoring_task.cancel()
            
            if self.data_update_task and not self.data_update_task.done():
                self.data_update_task.cancel()
            
            # Signal shutdown
            self.shutdown_event.set()
            self.state = BotState.STOPPED
            
            self.logger.info("✅ Trading stopped gracefully")
            
        except Exception as e:
            self.logger.error(f"Error stopping trading: {e}")
    
    async def emergency_shutdown(self) -> None:
        """Emergency shutdown with immediate position closure"""
        try:
            self.logger.critical("🚨 EMERGENCY SHUTDOWN INITIATED!")
            self.state = BotState.EMERGENCY_SHUTDOWN
            self.is_running = False
            
            # Immediately close all positions
            await self.execution_engine.emergency_close_all_positions()
            
            # Cancel all orders
            await self.execution_engine.cancel_all_orders()
            
            # Stop all tasks immediately
            for task in [self.main_loop_task, self.monitoring_task, self.data_update_task]:
                if task and not task.done():
                    task.cancel()
            
            # Signal shutdown
            self.shutdown_event.set()
            
            self.logger.critical("🚨 EMERGENCY SHUTDOWN COMPLETED")
            
        except Exception as e:
            self.logger.critical(f"Error in emergency shutdown: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current bot status and metrics"""
        return {
            'state': self.state.value,
            'is_running': self.is_running,
            'metrics': self.metrics,
            'config': {
                'symbols': self.config.symbols,
                'strategies_enabled': self.config.strategies_enabled,
                'ml_models_enabled': self.config.ml_models_enabled,
                'max_risk_per_trade': self.config.max_risk_per_trade
            },
            'component_status': {
                'data_manager': bool(self.data_manager),
                'strategy_manager': bool(self.strategy_manager), 
                'risk_manager': bool(self.risk_manager),
                'execution_engine': bool(self.execution_engine),
                'ml_models': {
                    'lstm': bool(self.lstm_model),
                    'random_forest': bool(self.rf_model),
                    'svm': bool(self.svm_model),
                    'ensemble': bool(self.ensemble_model)
                }
            }
        }

# Signal handlers for graceful shutdown
def signal_handler(bot_engine: EnhancedTradingBotEngine):
    """Handle shutdown signals"""
    def handler(signum, frame):
        asyncio.create_task(bot_engine.stop_trading())
    return handler
