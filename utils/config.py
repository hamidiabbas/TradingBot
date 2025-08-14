# utils/config.py
"""
Enhanced Configuration Management - COMPLETE VERSION
=================================================

Professional configuration management system with validation,
environment support, and dynamic updates for the institutional-grade trading bot.
Includes comprehensive settings for ML models, strategies, risk management,
MT5 integration, and production deployment.

Author: Enhanced Trading System
Version: 4.0 Complete Professional
License: Proprietary
"""

import os
import yaml
import json
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

@dataclass
class TradingConfig:
    """
    Comprehensive trading configuration with complete institutional-grade settings
    """
    
    # ========================================
    # CORE SYSTEM SETTINGS
    # ========================================
    environment: str = 'demo'  # demo, live, sandbox, paper
    system_name: str = 'EnhancedTradingBot'
    system_version: str = '4.0'
    timezone: str = 'UTC'
    log_level: str = 'INFO'
    
    # ========================================
    # MT5 CONNECTION CONFIGURATION
    # ========================================
    # MT5 Connection Details
    mt5_login: int = int(os.getenv('MT5_LOGIN', '0'))
    mt5_password: str = os.getenv('MT5_PASSWORD', '')
    mt5_server: str = os.getenv('MT5_SERVER', '')
    mt5_path: str = os.getenv('MT5_PATH', r'C:\Program Files\MetaTrader 5\terminal64.exe')
    mt5_timeout: int = 10000  # Connection timeout in milliseconds
    
    # MT5 Trading Settings
    mt5_magic_number: int = 12345
    mt5_deviation: int = 20  # Price deviation in points
    mt5_fill_type: str = 'FOK'  # FOK, IOC, RETURN
    mt5_type_time: str = 'GTC'  # GTC, DAY, SPECIFIED
    
    # ========================================
    # TRADING SYMBOLS AND INSTRUMENTS
    # ========================================
    symbols: List[str] = field(default_factory=lambda: [
        'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD',
        'XAUUSD', 'XAGUSD', 'USOIL', 'UK100', 'US30', 'NAS100', 'SPX500'
    ])
    
    # Symbol-specific settings
    symbol_configs: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        'EURUSD': {'pip_size': 0.0001, 'min_lot': 0.01, 'max_lot': 100.0, 'spread_filter': 3.0},
        'GBPUSD': {'pip_size': 0.0001, 'min_lot': 0.01, 'max_lot': 100.0, 'spread_filter': 3.0},
        'USDJPY': {'pip_size': 0.01, 'min_lot': 0.01, 'max_lot': 100.0, 'spread_filter': 3.0},
        'XAUUSD': {'pip_size': 0.01, 'min_lot': 0.01, 'max_lot': 100.0, 'spread_filter': 50.0},
        'USOIL': {'pip_size': 0.01, 'min_lot': 0.01, 'max_lot': 100.0, 'spread_filter': 10.0}
    })
    
    # ========================================
    # ACCOUNT AND CAPITAL MANAGEMENT
    # ========================================
    initial_balance: float = 100000.0
    base_currency: str = 'USD'
    leverage: float = 100.0
    account_currency: str = 'USD'
    
    # Account Protection
    account_protection_enabled: bool = True
    emergency_stop_loss: float = 50000.0  # Emergency account stop loss
    daily_loss_limit: float = 5000.0      # Daily loss limit
    weekly_loss_limit: float = 15000.0    # Weekly loss limit
    monthly_loss_limit: float = 25000.0   # Monthly loss limit
    
    # ========================================
    # RISK MANAGEMENT CONFIGURATION
    # ========================================
    # Position Risk
    max_risk_per_trade: float = 0.02      # 2% max risk per trade
    max_portfolio_risk: float = 0.10      # 10% max total portfolio risk
    max_correlation_risk: float = 0.15    # 15% max correlated positions
    max_drawdown: float = 0.15            # 15% maximum drawdown
    max_daily_loss: float = 0.05          # 5% daily loss limit
    
    # Position Sizing
    position_sizing_method: str = 'kelly'  # kelly, fixed_fractional, volatility_target, ml_confidence
    kelly_fraction: float = 0.25          # Kelly criterion fraction
    fixed_lot_size: float = 0.1           # Fixed lot size for fixed method
    volatility_target: float = 0.16       # 16% annual volatility target
    
    # Stop Loss and Take Profit
    stop_loss_method: str = 'atr'         # atr, fixed, support_resistance, ml_adaptive
    take_profit_method: str = 'risk_reward' # risk_reward, fibonacci, resistance, ml_target
    atr_period: int = 14
    atr_multiplier: float = 2.5
    risk_reward_ratio: float = 2.0        # 1:2 risk/reward
    
    # Advanced Risk Controls
    max_open_positions: int = 10
    max_positions_per_symbol: int = 2
    correlation_threshold: float = 0.7
    heat_threshold: float = 0.08          # Portfolio heat threshold
    
    # ========================================
    # ML MODELS CONFIGURATION
    # ========================================
    ml_models_enabled: List[str] = field(default_factory=lambda: ['lstm', 'random_forest', 'svm', 'ensemble'])
    require_all_ml_models: bool = False
    require_ensemble: bool = True
    enable_model_retraining: bool = True
    model_retraining_frequency: str = 'weekly'  # daily, weekly, monthly
    
    # Model Paths
    models_base_path: str = 'models/'
    lstm_model_path: str = 'models/lstm/institutional_lstm_model.pkl'
    rf_model_path: str = 'models/random_forest/rf_model.pkl'
    svm_model_path: str = 'models/svm/svm_model.pkl'
    ensemble_model_path: str = 'models/ensemble/ensemble_model.pkl'
    
    # Model Performance Thresholds
    min_model_accuracy: float = 0.55      # Minimum required accuracy
    model_confidence_threshold: float = 0.6  # Minimum prediction confidence
    ensemble_agreement_threshold: float = 0.7  # Model agreement threshold
    
    # ========================================
    # STRATEGY CONFIGURATION
    # ========================================
    strategies_enabled: List[str] = field(default_factory=lambda: [
        'indicator_suite', 'ict_strategy', 'rtm_strategy', 
        'momentum', 'mean_reversion', 'breakout'
    ])
    
    # Strategy Weights and Priorities
    strategy_weights: Dict[str, float] = field(default_factory=lambda: {
        'indicator_suite': 0.15,
        'ict_strategy': 0.25,
        'rtm_strategy': 0.25,
        'momentum': 0.15,
        'mean_reversion': 0.10,
        'breakout': 0.10
    })
    
    # Primary vs Secondary Strategies
    primary_strategies: List[str] = field(default_factory=lambda: ['ict_strategy', 'rtm_strategy'])
    secondary_strategies: List[str] = field(default_factory=lambda: ['indicator_suite', 'momentum'])
    
    # ========================================
    # INDICATOR SUITE STRATEGY CONFIG
    # ========================================
    indicator_suite_config: Dict[str, Any] = field(default_factory=lambda: {
        'enabled': True,
        'weight': 0.15,
        'indicators': {
            'rsi': {
                'period': 14, 
                'overbought': 70, 
                'oversold': 30, 
                'enabled': True, 
                'confluence_score': 1.0
            },
            'macd': {
                'fast': 12, 
                'slow': 26, 
                'signal': 9, 
                'enabled': True, 
                'confluence_score': 1.5
            },
            'bollinger_bands': {
                'period': 20, 
                'std_dev': 2.0, 
                'enabled': True, 
                'confluence_score': 1.0
            },
            'stochastic': {
                'k_period': 14, 
                'd_period': 3, 
                'enabled': True, 
                'confluence_score': 1.0
            },
            'moving_averages': {
                'periods': [10, 20, 30, 50, 100, 200],
                'types': ['sma', 'ema'],
                'enabled': True,
                'trend_filter_period': 200,
                'confluence_score': 2.0
            },
            'atr': {
                'period': 14, 
                'enabled': True
            },
            'awesome_oscillator': {
                'enabled': True, 
                'confluence_score': 0.5
            }
        }
    })
    
    # ========================================
    # ICT STRATEGY CONFIGURATION
    # ========================================
    ict_config: Dict[str, Any] = field(default_factory=lambda: {
        'enabled': True,
        'weight': 0.25,
        'trading_timeframe': 'M15',
        'entry_timeframe': 'M5',
        'bias_timeframe': 'H4',
        'daily_bias_timeframe': 'D1',
        'swing_length': 10,
        'entry_models': ['2022_mentorship', 'fvg_entry', 'order_block_entry'],
        'use_fvg_entry': True,
        'use_ob_entry': True,
        'use_breaker_blocks': True,
        'use_mitigation_blocks': True,
        'poi_confluence_score': 3.0,
        'mss_confluence_score': 3.0,
        'liquidity_sweep_confluence': 2.0,
        'displacement_min_pips': 20,
        'fvg_min_size_pips': 5,
        'ob_min_strength': 0.6,
        'session_times': {
            'london_open': '08:00',
            'london_close': '17:00',
            'ny_open': '13:00',
            'ny_close': '22:00',
            'asian_open': '00:00',
            'asian_close': '09:00'
        }
    })
    
    # ========================================
    # RTM STRATEGY CONFIGURATION
    # ========================================
    rtm_config: Dict[str, Any] = field(default_factory=lambda: {
        'enabled': True,
        'weight': 0.25,
        'trading_timeframe': 'M15',
        'confirmation_timeframe': 'M5',
        'zone_timeframe': 'H4',
        'momentum_threshold_pips': 20,
        'base_candle_max_body_ratio': 0.3,
        'use_qml_confirmation': True,
        'use_supply_demand_zones': True,
        'zone_confluence_score': 3.0,
        'qml_confluence_score': 4.0,
        'zone_freshness_periods': 100,
        'min_zone_strength': 3,
        'zone_test_buffer_pips': 2,
        'qml_shoulder_tolerance_pips': 3
    })
    
    # ========================================
    # CONFLUENCE ENGINE CONFIGURATION
    # ========================================
    confluence_engine_config: Dict[str, Any] = field(default_factory=lambda: {
        'enabled': True,
        'min_confluence_score': 5.0,
        'max_confluence_score': 20.0,
        'confluence_rules': {
            # Primary signals
            'rtm_demand_zone_entered': 3.0,
            'rtm_supply_zone_entered': 3.0,
            'ict_order_block_reaction': 2.5,
            'ict_fvg_reaction': 2.0,
            'ict_mss_confirmed': 3.0,
            'qml_pattern_formed': 4.0,
            
            # Secondary confirmations
            'rsi_oversold_bounce': 1.0,
            'rsi_overbought_rejection': 1.0,
            'macd_bullish_cross': 1.5,
            'macd_bearish_cross': 1.5,
            'ma_trend_alignment': 2.0,
            'bollinger_band_squeeze': 1.0,
            'volume_surge': 1.5,
            
            # Negative confluence (penalties)
            'against_daily_trend': -3.0,
            'high_spread_environment': -1.0,
            'low_liquidity_session': -1.0,
            'news_event_proximity': -2.0
        },
        'time_decay_enabled': True,
        'time_decay_half_life': 30  # minutes
    })
    
    # ========================================
    # DATA MANAGEMENT CONFIGURATION
    # ========================================
    data_config: Dict[str, Any] = field(default_factory=lambda: {
        'base_timeframe': 'M1',
        'timeframes': ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1', 'W1', 'MN1'],
        'historical_data_days': 365,
        'data_update_interval': 60,    # seconds
        'tick_data_enabled': False,
        'volume_data_enabled': True,
        'spread_data_enabled': True,
        
        # Data Quality
        'max_spread_filter': 10.0,     # pips
        'min_volume_filter': 100,
        'gap_detection_enabled': True,
        'weekend_gap_threshold': 50,   # pips
        
        # Caching
        'enable_data_cache': True,
        'cache_size_mb': 500,
        'cache_expiry_minutes': 15
    })
    
    # ========================================
    # NEWS AND SENTIMENT CONFIGURATION
    # ========================================
    news_config: Dict[str, Any] = field(default_factory=lambda: {
        'enabled': True,
        'sources': [
            'forexfactory', 'investing.com', 'bloomberg', 'reuters', 
            'marketwatch', 'fxstreet', 'dailyfx'
        ],
        'update_frequency': 300,       # 5 minutes
        'sentiment_analysis_enabled': True,
        'impact_levels': ['high', 'medium', 'low'],
        'currencies_tracked': ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'NZD'],
        
        # Event Filtering
        'high_impact_events': [
            'NFP', 'FOMC', 'CPI', 'GDP', 'ECB', 'BOE', 'BOJ', 'RBA'
        ],
        'pre_news_stop_minutes': 15,
        'post_news_wait_minutes': 5,
        'news_trading_enabled': False,  # Conservative approach
        
        # Sentiment Thresholds
        'sentiment_threshold': 0.7,
        'sentiment_weight': 0.5
    })
    
    # ========================================
    # EXECUTION ENGINE CONFIGURATION
    # ========================================
    execution_config: Dict[str, Any] = field(default_factory=lambda: {
        'execution_method': 'mt5',     # mt5, paper, simulation
        'order_types_enabled': ['market', 'limit', 'stop', 'stop_limit'],
        'default_order_type': 'market',
        'slippage_tolerance': 2.0,     # pips
        'max_execution_time': 5.0,     # seconds
        'retry_attempts': 3,
        'retry_delay': 1.0,            # seconds
        
        # Order Management
        'partial_fill_handling': 'accept',  # accept, reject, cancel
        'order_expiry_minutes': 60,
        'modify_order_enabled': True,
        'cancel_order_timeout': 10,    # seconds
        
        # Position Management
        'auto_close_on_margin_call': True,
        'auto_hedge_enabled': False,
        'netting_enabled': True,       # True for netting, False for hedging
        'position_monitoring_interval': 5  # seconds
    })
    
    # ========================================
    # PERFORMANCE MONITORING CONFIG
    # ========================================
    monitoring_config: Dict[str, Any] = field(default_factory=lambda: {
        'enabled': True,
        'update_interval': 10,         # seconds
        'metrics_calculation_interval': 60,  # seconds
        'performance_tracking_enabled': True,
        'real_time_pnl_tracking': True,
        
        # Alert Thresholds
        'drawdown_alert_threshold': 0.10,    # 10%
        'daily_loss_alert': 0.03,            # 3%
        'win_rate_alert_threshold': 0.40,    # Below 40%
        'consecutive_losses_alert': 5,
        'system_error_alert_enabled': True,
        
        # Performance Metrics
        'calculate_sharpe_ratio': True,
        'calculate_sortino_ratio': True,
        'calculate_calmar_ratio': True,
        'calculate_max_drawdown': True,
        'calculate_var': True,
        'var_confidence_level': 0.05,        # 5% VaR
        
        # Benchmarking
        'benchmark_symbol': 'SPY',
        'benchmark_enabled': False
    })
    
    # ========================================
    # TRADING HOURS AND SESSIONS
    # ========================================
    trading_hours_config: Dict[str, Any] = field(default_factory=lambda: {
        'timezone': 'UTC',
        'auto_detect_sessions': True,
        'exclude_weekends': True,
        'exclude_holidays': True,
        'holiday_calendar': 'FOREX',   # FOREX, NYSE, LSE
        
        # Session Trading Windows
        'sessions': {
            'asian': {
                'enabled': True,
                'start_hour': 0,
                'end_hour': 9,
                'volatility_adjustment': 0.8
            },
            'london': {
                'enabled': True,
                'start_hour': 8,
                'end_hour': 17,
                'volatility_adjustment': 1.2
            },
            'new_york': {
                'enabled': True,
                'start_hour': 13,
                'end_hour': 22,
                'volatility_adjustment': 1.3
            },
            'overlap_london_ny': {
                'enabled': True,
                'start_hour': 13,
                'end_hour': 17,
                'volatility_adjustment': 1.5
            }
        },
        
        # Daily Trading Windows
        'daily_start_hour': 0,
        'daily_end_hour': 24,
        'friday_close_early': True,
        'friday_close_hour': 21,
        'sunday_open_delay_hours': 1
    })
    
    # ========================================
    # BACKTESTING CONFIGURATION
    # ========================================
    backtesting_config: Dict[str, Any] = field(default_factory=lambda: {
        'enabled': True,
        'start_date': '2020-01-01',
        'end_date': '2024-12-31',
        'initial_balance': 100000.0,
        'commission_per_trade': 0.0,
        'spread_simulation': 'realistic',  # fixed, realistic, historical
        'slippage_simulation': 'realistic',
        
        # Walk Forward Analysis
        'walk_forward_enabled': True,
        'in_sample_months': 12,
        'out_sample_months': 3,
        'reoptimization_frequency': 'quarterly',
        
        # Monte Carlo
        'monte_carlo_enabled': True,
        'monte_carlo_runs': 1000,
        'random_seed': 42,
        
        # Performance Analysis
        'calculate_all_metrics': True,
        'benchmark_comparison': True,
        'detailed_trade_analysis': True,
        'correlation_analysis': True
    })
    
    # ========================================
    # LOGGING AND AUDIT CONFIGURATION
    # ========================================
    logging_config: Dict[str, Any] = field(default_factory=lambda: {
        'log_level': 'INFO',
        'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'log_to_file': True,
        'log_to_console': True,
        'log_rotation': 'daily',
        'max_log_files': 30,
        'log_file_max_size': '100MB',
        
        # Log Categories
        'log_trades': True,
        'log_signals': True,
        'log_ml_predictions': True,
        'log_risk_events': True,
        'log_system_events': True,
        'log_errors': True,
        'log_performance': True,
        
        # Audit Trail
        'audit_trail_enabled': True,
        'audit_all_decisions': True,
        'audit_retention_days': 2555,  # 7 years for regulatory compliance
        
        # Log Paths
        'log_directory': 'logs/',
        'trade_log_file': 'logs/trades.log',
        'system_log_file': 'logs/system.log',
        'error_log_file': 'logs/errors.log',
        'audit_log_file': 'logs/audit.log'
    })
    
    # ========================================
    # ALERT AND NOTIFICATION CONFIG
    # ========================================
    alerts_config: Dict[str, Any] = field(default_factory=lambda: {
        'enabled': True,
        'channels': ['email', 'slack', 'webhook', 'file'],
        
        # Email Configuration
        'email': {
            'enabled': True,
            'smtp_server': os.getenv('SMTP_SERVER', ''),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'username': os.getenv('EMAIL_USERNAME', ''),
            'password': os.getenv('EMAIL_PASSWORD', ''),
            'from_address': os.getenv('ALERT_FROM_EMAIL', ''),
            'to_addresses': [os.getenv('ALERT_TO_EMAIL', '')],
            'use_tls': True
        },
        
        # Slack Configuration
        'slack': {
            'enabled': False,
            'webhook_url': os.getenv('SLACK_WEBHOOK_URL', ''),
            'channel': '#trading-alerts',
            'username': 'TradingBot',
            'emoji': ':robot_face:'
        },
        
        # Webhook Configuration
        'webhook': {
            'enabled': False,
            'url': os.getenv('WEBHOOK_URL', ''),
            'method': 'POST',
            'headers': {'Content-Type': 'application/json'},
            'timeout': 10
        },
        
        # Alert Priorities
        'alert_levels': {
            'critical': ['system_error', 'emergency_shutdown', 'margin_call'],
            'high': ['drawdown_exceeded', 'daily_loss_limit', 'connection_lost'],
            'medium': ['trade_executed', 'signal_generated', 'performance_alert'],
            'low': ['system_status', 'heartbeat', 'routine_update']
        }
    })
    
    # ========================================
    # DATABASE CONFIGURATION
    # ========================================
    database_config: Dict[str, Any] = field(default_factory=lambda: {
        'enabled': True,
        'type': 'postgresql',  # postgresql, mysql, sqlite
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '5432')),
        'database': os.getenv('DB_NAME', 'trading_bot'),
        'username': os.getenv('DB_USERNAME', 'postgres'),
        'password': os.getenv('DB_PASSWORD', ''),
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 30,
        'pool_recycle': 3600,
        
        # Tables
        'tables': {
            'trades': True,
            'signals': True,
            'performance': True,
            'ml_predictions': True,
            'market_data': False,  # Usually too large for DB
            'audit_log': True
        },
        
        # Data Retention
        'trade_retention_days': 2555,     # 7 years
        'signal_retention_days': 365,     # 1 year
        'performance_retention_days': 2555, # 7 years
        'audit_retention_days': 2555      # 7 years
    })
    
    # ========================================
    # OPTIMIZATION CONFIGURATION
    # ========================================
    optimization_config: Dict[str, Any] = field(default_factory=lambda: {
        'enabled': True,
        'method': 'genetic_algorithm',  # grid_search, genetic_algorithm, bayesian
        'optimization_frequency': 'monthly',
        'parameters_to_optimize': [
            'risk_per_trade', 'stop_loss_atr_multiplier', 'take_profit_ratio',
            'confluence_threshold', 'strategy_weights'
        ],
        
        # Genetic Algorithm Settings
        'ga_population_size': 50,
        'ga_generations': 100,
        'ga_mutation_rate': 0.1,
        'ga_crossover_rate': 0.8,
        'ga_elite_size': 5,
        
        # Optimization Objectives
        'primary_objective': 'sharpe_ratio',
        'secondary_objectives': ['max_drawdown', 'profit_factor'],
        'multi_objective_enabled': True,
        
        # Constraints
        'max_risk_per_trade_range': [0.005, 0.03],
        'stop_loss_range': [1.5, 4.0],
        'take_profit_range': [1.0, 5.0]
    })
    
    # ========================================
    # SYSTEM PERFORMANCE CONFIG
    # ========================================
    system_config: Dict[str, Any] = field(default_factory=lambda: {
        'max_memory_usage_gb': 8.0,
        'max_cpu_usage_percent': 80.0,
        'gc_frequency_minutes': 30,
        'thread_pool_size': 4,
        'async_enabled': True,
        'multiprocessing_enabled': False,
        
        # Trading Loop
        'main_loop_interval': 1.0,      # seconds
        'signal_processing_timeout': 5.0,  # seconds
        'order_processing_timeout': 10.0,  # seconds
        'ml_prediction_timeout': 15.0,     # seconds
        
        # Connection Management
        'connection_pool_size': 10,
        'connection_timeout': 30,
        'reconnection_attempts': 5,
        'reconnection_delay': 5.0,      # seconds
        
        # Caching
        'redis_enabled': False,
        'redis_host': 'localhost',
        'redis_port': 6379,
        'redis_db': 0,
        'cache_ttl_minutes': 15
    })
    
    def __init__(self, config_data: Optional[Dict[str, Any]] = None):
        """Initialize configuration with optional external data"""
        if config_data:
            self._load_from_dict(config_data)
        
        # Validate configuration after loading
        self._post_init_validation()
    
    def _load_from_dict(self, config_data: Dict[str, Any]) -> None:
        """Load configuration from dictionary with nested support"""
        for key, value in config_data.items():
            if hasattr(self, key):
                current_value = getattr(self, key)
                if isinstance(current_value, dict) and isinstance(value, dict):
                    # Merge nested dictionaries
                    merged_dict = current_value.copy()
                    merged_dict.update(value)
                    setattr(self, key, merged_dict)
                else:
                    setattr(self, key, value)
    
    def _post_init_validation(self) -> None:
        """Validate configuration after initialization"""
        # Ensure strategy weights sum to 1.0
        total_weight = sum(self.strategy_weights.values())
        if abs(total_weight - 1.0) > 0.01:  # Allow small floating point errors
            # Normalize weights
            for strategy in self.strategy_weights:
                self.strategy_weights[strategy] /= total_weight
    
    def validate(self) -> bool:
        """Comprehensive configuration validation"""
        try:
            # MT5 Connection Validation
            if not all([self.mt5_login, self.mt5_password, self.mt5_server]):
                raise ValueError("MT5 connection credentials must be provided")
            
            # Risk Management Validation
            if self.max_risk_per_trade > 0.1:
                raise ValueError("Max risk per trade cannot exceed 10%")
            
            if self.max_portfolio_risk > 0.25:
                raise ValueError("Max portfolio risk cannot exceed 25%")
            
            if self.max_drawdown > 0.5:
                raise ValueError("Max drawdown cannot exceed 50%")
            
            # Symbol Validation
            if not self.symbols:
                raise ValueError("At least one trading symbol must be specified")
            
            # Strategy Validation
            if not self.strategies_enabled:
                raise ValueError("At least one strategy must be enabled")
            
            # ML Model Validation
            if self.require_all_ml_models and not all(
                model in self.ml_models_enabled 
                for model in ['lstm', 'random_forest', 'svm']
            ):
                raise ValueError("All ML models required but not all enabled")
            
            # Account Protection Validation
            if self.daily_loss_limit >= self.initial_balance * 0.2:
                raise ValueError("Daily loss limit too high relative to account size")
            
            # Confluence Engine Validation
            if self.confluence_engine_config['min_confluence_score'] >= self.confluence_engine_config['max_confluence_score']:
                raise ValueError("Min confluence score must be less than max confluence score")
            
            # Trading Hours Validation
            sessions = self.trading_hours_config.get('sessions', {})
            for session_name, session_config in sessions.items():
                if session_config.get('enabled', False):
                    start_hour = session_config.get('start_hour', 0)
                    end_hour = session_config.get('end_hour', 24)
                    if not (0 <= start_hour < 24 and 0 <= end_hour <= 24):
                        raise ValueError(f"Invalid trading hours for session {session_name}")
            
            return True
            
        except Exception as e:
            logging.error(f"Configuration validation failed: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with default"""
        if '.' in key:
            # Handle nested keys like 'ict_config.swing_length'
            keys = key.split('.')
            value = self
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k, default)
                else:
                    value = getattr(value, k, default)
                if value is None:
                    return default
            return value
        return getattr(self, key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value with nested support"""
        if '.' in key:
            # Handle nested keys
            keys = key.split('.')
            obj = self
            for k in keys[:-1]:
                if isinstance(obj, dict):
                    if k not in obj:
                        obj[k] = {}
                    obj = obj[k]
                else:
                    if not hasattr(obj, k):
                        setattr(obj, k, {})
                    obj = getattr(obj, k)
            
            if isinstance(obj, dict):
                obj[keys[-1]] = value
            else:
                setattr(obj, keys[-1], value)
        else:
            setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        result = {}
        for field_name, field_obj in self.__dataclass_fields__.items():
            value = getattr(self, field_name)
            if isinstance(value, dict):
                result[field_name] = value.copy()
            else:
                result[field_name] = value
        return result
    
    def save_to_file(self, filepath: str) -> None:
        """Save configuration to file (YAML or JSON)"""
        config_dict = self.to_dict()
        
        if filepath.endswith('.yaml') or filepath.endswith('.yml'):
            with open(filepath, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
        elif filepath.endswith('.json'):
            with open(filepath, 'w') as f:
                json.dump(config_dict, f, indent=2, default=str)
        else:
            raise ValueError("Configuration file must be .yaml, .yml, or .json")
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'TradingConfig':
        """Load configuration from file"""
        if not Path(filepath).exists():
            raise FileNotFoundError(f"Configuration file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            if filepath.endswith('.yaml') or filepath.endswith('.yml'):
                config_data = yaml.safe_load(f)
            elif filepath.endswith('.json'):
                config_data = json.load(f)
            else:
                raise ValueError("Configuration file must be .yaml, .yml, or .json")
        
        return cls(config_data)
    
    def get_environment_specific_config(self) -> 'TradingConfig':
        """Get configuration adjusted for current environment"""
        config_copy = self.__class__(self.to_dict())
        
        if self.environment == 'demo':
            # Demo environment adjustments
            config_copy.initial_balance = 10000.0
            config_copy.max_risk_per_trade = 0.01  # More conservative
            config_copy.leverage = 50.0
            
        elif self.environment == 'live':
            # Live environment adjustments
            config_copy.logging_config['log_level'] = 'INFO'
            config_copy.alerts_config['enabled'] = True
            
        elif self.environment == 'paper':
            # Paper trading adjustments
            config_copy.execution_config['execution_method'] = 'paper'
            config_copy.alerts_config['enabled'] = False
            
        return config_copy
    
    def __str__(self) -> str:
        """String representation of configuration"""
        return f"TradingConfig(environment={self.environment}, symbols={len(self.symbols)}, strategies={len(self.strategies_enabled)})"
    
    def __repr__(self) -> str:
        """Detailed string representation"""
        return (
            f"TradingConfig(\n"
            f"  environment='{self.environment}',\n"
            f"  symbols={self.symbols},\n"
            f"  strategies={self.strategies_enabled},\n"
            f"  ml_models={self.ml_models_enabled},\n"
            f"  initial_balance={self.initial_balance},\n"
            f"  max_risk_per_trade={self.max_risk_per_trade}\n"
            f")"
        )

# Configuration Factory Functions
def create_demo_config() -> TradingConfig:
    """Create a demo/testing configuration"""
    return TradingConfig({
        'environment': 'demo',
        'initial_balance': 10000.0,
        'symbols': ['EURUSD', 'GBPUSD'],
        'strategies_enabled': ['momentum', 'mean_reversion'],
        'ml_models_enabled': ['lstm'],
        'max_risk_per_trade': 0.01,
        'logging_config': {'log_level': 'DEBUG'}
    })

def create_live_config() -> TradingConfig:
    """Create a live trading configuration"""
    return TradingConfig({
        'environment': 'live',
        'initial_balance': 100000.0,
        'alerts_config': {'enabled': True},
        'monitoring_config': {'enabled': True},
        'database_config': {'enabled': True}
    })

def create_paper_config() -> TradingConfig:
    """Create a paper trading configuration"""
    return TradingConfig({
        'environment': 'paper',
        'execution_config': {'execution_method': 'paper'},
        'alerts_config': {'enabled': False}
    })

# Configuration Validation Utilities
def validate_mt5_connection(config: TradingConfig) -> bool:
    """Validate MT5 connection settings"""
    try:
        import MetaTrader5 as mt5
        
        if not mt5.initialize(
            login=config.mt5_login,
            server=config.mt5_server,
            password=config.mt5_password,
            path=config.mt5_path,
            timeout=config.mt5_timeout
        ):
            return False
        
        mt5.shutdown()
        return True
        
    except Exception:
        return False

def validate_symbols(config: TradingConfig) -> Dict[str, bool]:
    """Validate trading symbols availability"""
    try:
        import MetaTrader5 as mt5
        
        if not mt5.initialize():
            return {symbol: False for symbol in config.symbols}
        
        results = {}
        for symbol in config.symbols:
            symbol_info = mt5.symbol_info(symbol)
            results[symbol] = symbol_info is not None and symbol_info.visible
        
        mt5.shutdown()
        return results
        
    except Exception:
        return {symbol: False for symbol in config.symbols}

# Environment Variable Loading
def load_environment_variables():
    """Load environment variables for configuration"""
    from dotenv import load_dotenv
    load_dotenv()

# Configuration Loading with Environment Variables
def load_configuration_from_env() -> TradingConfig:
    """Load configuration from environment variables"""
    config = TradingConfig()
    config.mt5_login = int(os.getenv("MT5_LOGIN", config.mt5_login))
    config.mt5_password = os.getenv("MT5_PASSWORD", config.mt5_password)
    config.mt5_server = os.getenv("MT5_SERVER", config.mt5_server)
    config.mt5_path = os.getenv("MT5_PATH", config.mt5_path)
    config.mt5_timeout = int(os.getenv("MT5_TIMEOUT", config.mt5_timeout))
    config.trading_mode = os.getenv("TRADING_MODE", config.trading_mode)
    config.trading_symbols = os.getenv("TRADING_SYMBOLS", config.trading_symbols)
    config.trading_timeframe = os.getenv("TRADING_TIMEFRAME", config.trading_timeframe)
    config.trading_initial_capital = float(os.getenv("TRADING_INITIAL_CAPITAL", config.trading_initial_capital))
    config.trading_risk_per_trade = float(os.getenv("TRADING_RISK_PER_TRADE", config.trading_risk_per_trade))
    config.trading_max_positions = int(os.getenv("TRADING_MAX_POSITIONS", config.trading_max_positions))
    config.trading_report_dir = os.getenv("TRADING_REPORT_DIR", config.trading_report_dir)
    return config