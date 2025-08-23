from typing import Dict, Any, Optional

"""
Enhanced Professional Indicator Suite Strategy
===============================================

A comprehensive technical indicator-based trading strategy implementing multiple confirmation
signals, advanced pattern recognition, and sophisticated risk management integration.

This strategy serves as a secondary confirmation system within the broader trading framework,
providing confluence scoring and signal validation for primary strategies.

Features:
- 15+ Professional Technical Indicators
- Multi-timeframe Analysis
- Divergence Detection Algorithms
- Dynamic Signal Strength Calculation
- Advanced Confluence Scoring
- Real-time Performance Analytics
- Institutional-grade Error Handling

Author: Enhanced Trading System
Version: 3.0 Professional
License: Proprietary
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import warnings
from concurrent.futures import ThreadPoolExecutor
import pandas_ta as ta
from scipy import stats

from strategies import SecondaryStrategy, SignalEvent, TradeSetup, register_strategy
from utils.technical_indicators import AdvancedTechnicalIndicators
from utils.logger import setup_logging

# Suppress pandas warnings for cleaner output
warnings.filterwarnings('ignore', category=FutureWarning)

class IndicatorSignalType(Enum):
    """Enumeration for indicator signal types"""
    MOMENTUM = "momentum"
    TREND = "trend"
    VOLATILITY = "volatility"
    VOLUME = "volume"
    OSCILLATOR = "oscillator"
    DIVERGENCE = "divergence"

class SignalStrength(Enum):
    """Signal strength classification"""
    VERY_WEAK = 0.2
    WEAK = 0.4
    MODERATE = 0.6
    STRONG = 0.8
    VERY_STRONG = 1.0

@dataclass
class IndicatorSignal:
    """Individual indicator signal with detailed metadata"""
    indicator_name: str
    signal_type: IndicatorSignalType
    direction: str  # 'bullish', 'bearish', 'neutral'
    strength: float
    confidence: float
    timeframe: str
    timestamp: datetime
    level: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        self.strength = max(0.0, min(1.0, self.strength))
        self.confidence = max(0.0, min(1.0, self.confidence))

@dataclass
class IndicatorConfiguration:
    """Configuration for individual indicators"""
    enabled: bool = True
    parameters: Dict[str, Any] = field(default_factory=dict)
    confluence_weight: float = 1.0
    signal_threshold: float = 0.5
    use_divergence: bool = True
    timeframes: List[str] = field(default_factory=lambda: ['M15', 'H1'])

@register_strategy
class EnhancedIndicatorSuiteStrategy(SecondaryStrategy):
    """
    Enhanced Professional Indicator Suite Strategy
    
    This comprehensive technical analysis strategy implements multiple indicators
    with advanced signal processing, divergence detection, and multi-timeframe
    confluence analysis. Designed for institutional-grade algorithmic trading.
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.logger = setup_logging('INFO')
        
        # Enhanced configuration
        self.trading_timeframe = config.get('trading_timeframe', 'M15')
        self.confirmation_timeframes = config.get('confirmation_timeframes', ['H1', 'H4'])
        self.signal_timeout_minutes = config.get('signal_timeout_minutes', 60)
        
        # Indicator configurations
        self.indicator_configs = self._initialize_indicator_configs(config)
        
        # Advanced technical indicators library
        self.tech_indicators = AdvancedTechnicalIndicators(enable_profiling=True)
        
        # Signal processing
        self.min_confluence_score = config.get('min_confluence_score', 3.0)
        self.max_signals_per_timeframe = config.get('max_signals_per_timeframe', 10)
        self.signal_aggregation_method = config.get('signal_aggregation_method', 'weighted_average')
        
        # Performance tracking
        self.performance_metrics = {
            'signals_generated': 0,
            'signals_confirmed': 0,
            'successful_signals': 0,
            'average_signal_strength': 0.0,
            'divergence_signals': 0,
            'multi_tf_confirmations': 0
        }
        
        # Signal history and caching
        self.signal_history: Dict[str, List[IndicatorSignal]] = {}
        self.indicator_cache: Dict[str, Any] = {}
        self.cache_expiry_seconds = 30
        
        # Threading for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Divergence detection settings
        self.divergence_lookback = config.get('divergence_lookback', 20)
        self.divergence_threshold = config.get('divergence_threshold', 0.7)
        
        self.logger.info("Enhanced Indicator Suite Strategy initialized")
    
    def _initialize_indicator_configs(self, config: Dict[str, Any]) -> Dict[str, IndicatorConfiguration]:
        """Initialize indicator configurations from config"""
        try:
            indicator_configs = {}
            
            # RSI Configuration
            rsi_config = config.get('indicators', {}).get('rsi', {})
            indicator_configs['rsi'] = IndicatorConfiguration(
                enabled=rsi_config.get('enabled', True),
                parameters={
                    'period': rsi_config.get('period', 14),
                    'overbought': rsi_config.get('overbought', 70),
                    'oversold': rsi_config.get('oversold', 30),
                    'smoothing': rsi_config.get('smoothing', 'wilder')
                },
                confluence_weight=rsi_config.get('confluence_weight', 1.0),
                use_divergence=rsi_config.get('use_divergence', True)
            )
            
            # MACD Configuration
            macd_config = config.get('indicators', {}).get('macd', {})
            indicator_configs['macd'] = IndicatorConfiguration(
                enabled=macd_config.get('enabled', True),
                parameters={
                    'fast': macd_config.get('fast', 12),
                    'slow': macd_config.get('slow', 26),
                    'signal': macd_config.get('signal', 9),
                    'macd_type': macd_config.get('type', 'ema')
                },
                confluence_weight=macd_config.get('confluence_weight', 1.5)
            )
            
            # Stochastic Configuration
            stoch_config = config.get('indicators', {}).get('stochastic', {})
            indicator_configs['stochastic'] = IndicatorConfiguration(
                enabled=stoch_config.get('enabled', True),
                parameters={
                    'k_period': stoch_config.get('k_period', 14),
                    'd_period': stoch_config.get('d_period', 3),
                    'smooth_k': stoch_config.get('smooth_k', 3),
                    'overbought': stoch_config.get('overbought', 80),
                    'oversold': stoch_config.get('oversold', 20)
                },
                confluence_weight=stoch_config.get('confluence_weight', 0.8)
            )
            
            # Moving Averages Configuration
            ma_config = config.get('indicators', {}).get('moving_averages', {})
            indicator_configs['moving_averages'] = IndicatorConfiguration(
                enabled=ma_config.get('enabled', True),
                parameters={
                    'periods': ma_config.get('periods', [10, 20, 50, 100, 200]),
                    'types': ma_config.get('types', ['ema', 'sma']),
                    'trend_filter_period': ma_config.get('trend_filter_period', 200)
                },
                confluence_weight=ma_config.get('confluence_weight', 1.2)
            )
            
            # Bollinger Bands Configuration
            bb_config = config.get('indicators', {}).get('bollinger_bands', {})
            indicator_configs['bollinger_bands'] = IndicatorConfiguration(
                enabled=bb_config.get('enabled', True),
                parameters={
                    'period': bb_config.get('period', 20),
                    'std': bb_config.get('std', 2.0),
                    'squeeze_threshold': bb_config.get('squeeze_threshold', 0.1)
                },
                confluence_weight=bb_config.get('confluence_weight', 0.9)
            )
            
            # Volume Indicators Configuration
            volume_config = config.get('indicators', {}).get('volume', {})
            indicator_configs['volume'] = IndicatorConfiguration(
                enabled=volume_config.get('enabled', True),
                parameters={
                    'obv_period': volume_config.get('obv_period', 20),
                    'mfi_period': volume_config.get('mfi_period', 14),
                    'volume_threshold': volume_config.get('volume_threshold', 1.5)
                },
                confluence_weight=volume_config.get('confluence_weight', 0.7)
            )
            
            return indicator_configs
            
        except Exception as e:
            self.logger.error(f"Error initializing indicator configs: {e}")
            return {}
    
    async def initialize(self) -> bool:
        """Initialize the enhanced indicator suite strategy"""
        try:
            self.logger.info("Initializing Enhanced Indicator Suite Strategy...")
            
            # Initialize technical indicators library
            if not await self.tech_indicators.initialize():
                self.logger.error("Failed to initialize technical indicators library")
                return False
            
            # Initialize signal history for tracking
            for timeframe in [self.trading_timeframe] + self.confirmation_timeframes:
                self.signal_history[timeframe] = []
            
            # Validate indicator configurations
            enabled_indicators = [name for name, config in self.indicator_configs.items() if config.enabled]
            self.logger.info(f"Enabled indicators: {enabled_indicators}")
            
            if len(enabled_indicators) < 3:
                self.logger.warning("Less than 3 indicators enabled - reduced signal quality expected")
            
            self.logger.info("Enhanced Indicator Suite Strategy initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing Enhanced Indicator Suite Strategy: {e}")
            return False
    
    def generate_signals(self, data: Dict[str, pd.DataFrame]) -> List[SignalEvent]:
        """
        Generate comprehensive indicator signals with advanced processing
        
        Args:
            data: Multi-timeframe market data
            
        Returns:
            List of enhanced signal events
        """
        try:
            all_signals = []
            
            # Process each symbol's data
            for symbol, timeframe_data in data.items():
                if not isinstance(timeframe_data, dict):
                    continue
                
                # Generate signals for primary timeframe
                primary_signals = self._process_timeframe_indicators(
                    symbol, timeframe_data, self.trading_timeframe
                )
                
                # Generate confirmation signals from higher timeframes
                confirmation_signals = []
                for tf in self.confirmation_timeframes:
                    if tf in timeframe_data:
                        tf_signals = self._process_timeframe_indicators(symbol, timeframe_data, tf)
                        confirmation_signals.extend(tf_signals)
                
                # Perform multi-timeframe confluence analysis
                confluent_signals = self._analyze_multi_timeframe_confluence(
                    symbol, primary_signals, confirmation_signals
                )
                
                # Add symbol to signals
                for signal in confluent_signals:
                    signal.symbol = symbol
                
                all_signals.extend(confluent_signals)
            
            # Update performance metrics
            self._update_performance_metrics(all_signals)
            
            # Clean old signals from history
            self._cleanup_signal_history()
            
            return all_signals
            
        except Exception as e:
            self.logger.error(f"Error generating indicator signals: {e}")
            return []
    
    def _process_timeframe_indicators(self, symbol: str, data: Dict[str, pd.DataFrame], 
                                    timeframe: str) -> List[IndicatorSignal]:
        """Process all indicators for a specific timeframe"""
        try:
            if timeframe not in data:
                return []
            
            df = data[timeframe]
            if len(df) < 50:  # Need sufficient data for indicators
                return []
            
            timeframe_signals = []
            current_time = datetime.utcnow()
            
            # Process each enabled indicator
            for indicator_name, config in self.indicator_configs.items():
                if not config.enabled:
                    continue
                
                try:
                    # Generate signals based on indicator type
                    if indicator_name == 'rsi':
                        signals = self._process_rsi_signals(df, config, timeframe, current_time)
                    elif indicator_name == 'macd':
                        signals = self._process_macd_signals(df, config, timeframe, current_time)
                    elif indicator_name == 'stochastic':
                        signals = self._process_stochastic_signals(df, config, timeframe, current_time)
                    elif indicator_name == 'moving_averages':
                        signals = self._process_ma_signals(df, config, timeframe, current_time)
                    elif indicator_name == 'bollinger_bands':
                        signals = self._process_bollinger_signals(df, config, timeframe, current_time)
                    elif indicator_name == 'volume':
                        signals = self._process_volume_signals(df, config, timeframe, current_time)
                    else:
                        continue
                    
                    timeframe_signals.extend(signals)
                    
                except Exception as e:
                    self.logger.error(f"Error processing {indicator_name} for {timeframe}: {e}")
                    continue
            
            # Store signals in history
            if timeframe in self.signal_history:
                self.signal_history[timeframe].extend(timeframe_signals)
                # Limit history size
                if len(self.signal_history[timeframe]) > 1000:
                    self.signal_history[timeframe] = self.signal_history[timeframe][-500:]
            
            return timeframe_signals
            
        except Exception as e:
            self.logger.error(f"Error processing timeframe {timeframe}: {e}")
            return []
    
    def _process_rsi_signals(self, df: pd.DataFrame, config: IndicatorConfiguration,
                           timeframe: str, timestamp: datetime) -> List[IndicatorSignal]:
        """Process RSI signals with advanced analysis"""
        try:
            signals = []
            params = config.parameters
            
            # Calculate RSI using advanced method
            rsi_result = self.tech_indicators.calculate_advanced_rsi(
                df['close'],
                period=params['period'],
                smoothing=params['smoothing'],
                calculate_divergence=config.use_divergence
            )
            
            if rsi_result.values.empty:
                return signals
            
            rsi_values = rsi_result.values
            current_rsi = rsi_values.iloc[-1]
            
            # Generate basic RSI signals
            if current_rsi > params['overbought']:
                signals.append(IndicatorSignal(
                    indicator_name='rsi',
                    signal_type=IndicatorSignalType.OSCILLATOR,
                    direction='bearish',
                    strength=min(1.0, (current_rsi - params['overbought']) / (100 - params['overbought'])),
                    confidence=rsi_result.confidence,
                    timeframe=timeframe,
                    timestamp=timestamp,
                    level=current_rsi,
                    metadata={'rsi_value': current_rsi, 'threshold': 'overbought'}
                ))
            elif current_rsi < params['oversold']:
                signals.append(IndicatorSignal(
                    indicator_name='rsi',
                    signal_type=IndicatorSignalType.OSCILLATOR,
                    direction='bullish',
                    strength=min(1.0, (params['oversold'] - current_rsi) / params['oversold']),
                    confidence=rsi_result.confidence,
                    timeframe=timeframe,
                    timestamp=timestamp,
                    level=current_rsi,
                    metadata={'rsi_value': current_rsi, 'threshold': 'oversold'}
                ))
            
            # Process divergence signals if available
            if config.use_divergence and rsi_result.signals is not None:
                divergence_strength = abs(rsi_result.signals.iloc[-1])
                if divergence_strength > 0:
                    direction = 'bullish' if rsi_result.signals.iloc[-1] > 0 else 'bearish'
                    signals.append(IndicatorSignal(
                        indicator_name='rsi_divergence',
                        signal_type=IndicatorSignalType.DIVERGENCE,
                        direction=direction,
                        strength=divergence_strength,
                        confidence=rsi_result.confidence * 1.2,  # Divergence signals are stronger
                        timeframe=timeframe,
                        timestamp=timestamp,
                        level=current_rsi,
                        metadata={'divergence_type': 'rsi', 'divergence_strength': divergence_strength}
                    ))
                    self.performance_metrics['divergence_signals'] += 1
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Error processing RSI signals: {e}")
            return []
    
    def _process_macd_signals(self, df: pd.DataFrame, config: IndicatorConfiguration,
                            timeframe: str, timestamp: datetime) -> List[IndicatorSignal]:
        """Process MACD signals with advanced analysis"""
        try:
            signals = []
            params = config.parameters
            
            # Calculate advanced MACD
            macd_result = self.tech_indicators.calculate_advanced_macd(
                df['close'],
                fast=params['fast'],
                slow=params['slow'],
                signal_period=params['signal'],
                macd_type=params['macd_type']
            )
            
            if macd_result.values.empty:
                return signals
            
            macd_data = macd_result.values
            current_macd = macd_data['macd_line'].iloc[-1]
            current_signal = macd_data['signal_line'].iloc[-1]
            current_histogram = macd_data['histogram'].iloc[-1]
            
            # MACD Line crossovers
            if len(macd_data) >= 2:
                prev_macd = macd_data['macd_line'].iloc[-2]
                prev_signal = macd_data['signal_line'].iloc[-2]
                
                # Bullish crossover
                if prev_macd <= prev_signal and current_macd > current_signal:
                    strength = min(1.0, abs(current_macd - current_signal) / 0.001)
                    # Stronger signal if below zero line
                    if current_macd < 0:
                        strength *= 1.3
                    
                    signals.append(IndicatorSignal(
                        indicator_name='macd',
                        signal_type=IndicatorSignalType.MOMENTUM,
                        direction='bullish',
                        strength=strength,
                        confidence=macd_result.confidence,
                        timeframe=timeframe,
                        timestamp=timestamp,
                        level=current_macd,
                        metadata={
                            'macd_line': current_macd,
                            'signal_line': current_signal,
                            'histogram': current_histogram,
                            'crossover_type': 'bullish'
                        }
                    ))
                
                # Bearish crossover
                elif prev_macd >= prev_signal and current_macd < current_signal:
                    strength = min(1.0, abs(current_macd - current_signal) / 0.001)
                    # Stronger signal if above zero line
                    if current_macd > 0:
                        strength *= 1.3
                    
                    signals.append(IndicatorSignal(
                        indicator_name='macd',
                        signal_type=IndicatorSignalType.MOMENTUM,
                        direction='bearish',
                        strength=strength,
                        confidence=macd_result.confidence,
                        timeframe=timeframe,
                        timestamp=timestamp,
                        level=current_macd,
                        metadata={
                            'macd_line': current_macd,
                            'signal_line': current_signal,
                            'histogram': current_histogram,
                            'crossover_type': 'bearish'
                        }
                    ))
            
            # Histogram momentum signals
            if len(macd_data) >= 3:
                histogram_trend = (macd_data['histogram'].iloc[-1] - 
                                 macd_data['histogram'].iloc[-3]) / 2
                
                if abs(histogram_trend) > 0.0001:  # Significant momentum change
                    direction = 'bullish' if histogram_trend > 0 else 'bearish'
                    signals.append(IndicatorSignal(
                        indicator_name='macd_momentum',
                        signal_type=IndicatorSignalType.MOMENTUM,
                        direction=direction,
                        strength=min(1.0, abs(histogram_trend) * 1000),
                        confidence=macd_result.confidence * 0.8,
                        timeframe=timeframe,
                        timestamp=timestamp,
                        level=current_histogram,
                        metadata={
                            'histogram_trend': histogram_trend,
                            'momentum_type': 'histogram'
                        }
                    ))
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Error processing MACD signals: {e}")
            return []
    
    def _process_stochastic_signals(self, df: pd.DataFrame, config: IndicatorConfiguration,
                                  timeframe: str, timestamp: datetime) -> List[IndicatorSignal]:
        """Process Stochastic signals with advanced analysis"""
        try:
            signals = []
            params = config.parameters
            
            # Calculate advanced stochastic
            stoch_result = self.tech_indicators.calculate_advanced_stochastic(
                df['high'], df['low'], df['close'],
                k_period=params['k_period'],
                d_period=params['d_period'],
                smooth_k=params['smooth_k'],
                stoch_type='slow'
            )
            
            if stoch_result.values.empty:
                return signals
            
            stoch_data = stoch_result.values
            current_k = stoch_data['k'].iloc[-1]
            current_d = stoch_data['d'].iloc[-1]
            
            # Stochastic crossover signals
            if len(stoch_data) >= 2:
                prev_k = stoch_data['k'].iloc[-2]
                prev_d = stoch_data['d'].iloc[-2]
                
                # Bullish crossover in oversold region
                if (prev_k <= prev_d and current_k > current_d and 
                    current_k < params['oversold']):
                    
                    signals.append(IndicatorSignal(
                        indicator_name='stochastic',
                        signal_type=IndicatorSignalType.OSCILLATOR,
                        direction='bullish',
                        strength=min(1.0, (params['oversold'] - current_k) / params['oversold']),
                        confidence=stoch_result.confidence,
                        timeframe=timeframe,
                        timestamp=timestamp,
                        level=current_k,
                        metadata={
                            'k_value': current_k,
                            'd_value': current_d,
                            'crossover_region': 'oversold'
                        }
                    ))
                
                # Bearish crossover in overbought region
                elif (prev_k >= prev_d and current_k < current_d and 
                      current_k > params['overbought']):
                    
                    signals.append(IndicatorSignal(
                        indicator_name='stochastic',
                        signal_type=IndicatorSignalType.OSCILLATOR,
                        direction='bearish',
                        strength=min(1.0, (current_k - params['overbought']) / (100 - params['overbought'])),
                        confidence=stoch_result.confidence,
                        timeframe=timeframe,
                        timestamp=timestamp,
                        level=current_k,
                        metadata={
                            'k_value': current_k,
                            'd_value': current_d,
                            'crossover_region': 'overbought'
                        }
                    ))
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Error processing Stochastic signals: {e}")
            return []
    
    def _process_ma_signals(self, df: pd.DataFrame, config: IndicatorConfiguration,
                          timeframe: str, timestamp: datetime) -> List[IndicatorSignal]:
        """Process Moving Average signals with trend analysis"""
        try:
            signals = []
            params = config.parameters
            
            # Calculate multiple moving averages
            ma_data = {}
            for period in params['periods']:
                for ma_type in params['types']:
                    if ma_type == 'sma':
                        ma_data[f'{ma_type}_{period}'] = df['close'].rolling(period).mean()
                    elif ma_type == 'ema':
                        ma_data[f'{ma_type}_{period}'] = df['close'].ewm(span=period).mean()
            
            current_price = df['close'].iloc[-1]
            
            # MA crossover signals (20/50 EMA)
            if 'ema_20' in ma_data and 'ema_50' in ma_data:
                ema_20 = ma_data['ema_20']
                ema_50 = ma_data['ema_50']
                
                if len(ema_20) >= 2 and len(ema_50) >= 2:
                    current_20 = ema_20.iloc[-1]
                    current_50 = ema_50.iloc[-1]
                    prev_20 = ema_20.iloc[-2]
                    prev_50 = ema_50.iloc[-2]
                    
                    # Bullish crossover
                    if prev_20 <= prev_50 and current_20 > current_50:
                        signals.append(IndicatorSignal(
                            indicator_name='ma_crossover',
                            signal_type=IndicatorSignalType.TREND,
                            direction='bullish',
                            strength=0.8,
                            confidence=0.7,
                            timeframe=timeframe,
                            timestamp=timestamp,
                            level=current_price,
                            metadata={
                                'crossover_type': 'ema_20_50',
                                'ema_20': current_20,
                                'ema_50': current_50
                            }
                        ))
                    
                    # Bearish crossover
                    elif prev_20 >= prev_50 and current_20 < current_50:
                        signals.append(IndicatorSignal(
                            indicator_name='ma_crossover',
                            signal_type=IndicatorSignalType.TREND,
                            direction='bearish',
                            strength=0.8,
                            confidence=0.7,
                            timeframe=timeframe,
                            timestamp=timestamp,
                            level=current_price,
                            metadata={
                                'crossover_type': 'ema_20_50',
                                'ema_20': current_20,
                                'ema_50': current_50
                            }
                        ))
            
            # Trend filter signal
            trend_filter_period = params.get('trend_filter_period', 200)
            if f'sma_{trend_filter_period}' in ma_data:
                trend_ma = ma_data[f'sma_{trend_filter_period}'].iloc[-1]
                
                # Strong trend signal
                if current_price > trend_ma * 1.02:  # 2% above trend line
                    signals.append(IndicatorSignal(
                        indicator_name='trend_filter',
                        signal_type=IndicatorSignalType.TREND,
                        direction='bullish',
                        strength=0.6,
                        confidence=0.8,
                        timeframe=timeframe,
                        timestamp=timestamp,
                        level=current_price,
                        metadata={'trend_ma': trend_ma, 'distance_pct': (current_price - trend_ma) / trend_ma}
                    ))
                elif current_price < trend_ma * 0.98:  # 2% below trend line
                    signals.append(IndicatorSignal(
                        indicator_name='trend_filter',
                        signal_type=IndicatorSignalType.TREND,
                        direction='bearish',
                        strength=0.6,
                        confidence=0.8,
                        timeframe=timeframe,
                        timestamp=timestamp,
                        level=current_price,
                        metadata={'trend_ma': trend_ma, 'distance_pct': (current_price - trend_ma) / trend_ma}
                    ))
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Error processing MA signals: {e}")
            return []
    
    def _process_bollinger_signals(self, df: pd.DataFrame, config: IndicatorConfiguration,
                                 timeframe: str, timestamp: datetime) -> List[IndicatorSignal]:
        """Process Bollinger Bands signals"""
        try:
            signals = []
            params = config.parameters
            
            # Calculate Bollinger Bands
            bb_data = ta.bbands(df['close'], length=params['period'], std=params['std'])
            
            if bb_data is None or bb_data.empty:
                return signals
            
            current_price = df['close'].iloc[-1]
            bb_upper = bb_data[f'BBU_{params["period"]}_{params["std"]}'].iloc[-1]
            bb_lower = bb_data[f'BBL_{params["period"]}_{params["std"]}'].iloc[-1]
            bb_middle = bb_data[f'BBM_{params["period"]}_{params["std"]}'].iloc[-1]
            
            # Bollinger Band position
            bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)
            
            # Oversold signal (price near lower band)
            if bb_position < 0.1:
                signals.append(IndicatorSignal(
                    indicator_name='bollinger_bands',
                    signal_type=IndicatorSignalType.VOLATILITY,
                    direction='bullish',
                    strength=min(1.0, (0.1 - bb_position) * 10),
                    confidence=0.7,
                    timeframe=timeframe,
                    timestamp=timestamp,
                    level=current_price,
                    metadata={
                        'bb_position': bb_position,
                        'bb_upper': bb_upper,
                        'bb_lower': bb_lower,
                        'signal_type': 'oversold'
                    }
                ))
            
            # Overbought signal (price near upper band)
            elif bb_position > 0.9:
                signals.append(IndicatorSignal(
                    indicator_name='bollinger_bands',
                    signal_type=IndicatorSignalType.VOLATILITY,
                    direction='bearish',
                    strength=min(1.0, (bb_position - 0.9) * 10),
                    confidence=0.7,
                    timeframe=timeframe,
                    timestamp=timestamp,
                    level=current_price,
                    metadata={
                        'bb_position': bb_position,
                        'bb_upper': bb_upper,
                        'bb_lower': bb_lower,
                        'signal_type': 'overbought'
                    }
                ))
            
            # Bollinger Band squeeze detection
            if len(bb_data) >= 2:
                current_width = bb_upper - bb_lower
                prev_width = (bb_data[f'BBU_{params["period"]}_{params["std"]}'].iloc[-2] - 
                             bb_data[f'BBL_{params["period"]}_{params["std"]}'].iloc[-2])
                
                if current_width < prev_width * (1 - params.get('squeeze_threshold', 0.1)):
                    signals.append(IndicatorSignal(
                        indicator_name='bb_squeeze',
                        signal_type=IndicatorSignalType.VOLATILITY,
                        direction='neutral',
                        strength=0.5,
                        confidence=0.6,
                        timeframe=timeframe,
                        timestamp=timestamp,
                        level=current_price,
                        metadata={
                            'bb_width': current_width,
                            'width_change': (current_width - prev_width) / prev_width,
                            'signal_type': 'squeeze'
                        }
                    ))
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Error processing Bollinger Bands signals: {e}")
            return []
    
    def _process_volume_signals(self, df: pd.DataFrame, config: IndicatorConfiguration,
                              timeframe: str, timestamp: datetime) -> List[IndicatorSignal]:
        """Process volume-based signals"""
        try:
            signals = []
            
            if 'volume' not in df.columns:
                return signals
            
            params = config.parameters
            volume = df['volume']
            current_volume = volume.iloc[-1]
            
            # Volume surge detection
            volume_ma = volume.rolling(20).mean().iloc[-1]
            volume_ratio = current_volume / volume_ma if volume_ma > 0 else 1.0
            
            if volume_ratio > params.get('volume_threshold', 1.5):
                # Determine direction based on price action
                price_change = (df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2]
                direction = 'bullish' if price_change > 0 else 'bearish'
                
                signals.append(IndicatorSignal(
                    indicator_name='volume_surge',
                    signal_type=IndicatorSignalType.VOLUME,
                    direction=direction,
                    strength=min(1.0, volume_ratio / 3.0),
                    confidence=0.6,
                    timeframe=timeframe,
                    timestamp=timestamp,
                    level=current_volume,
                    metadata={
                        'volume_ratio': volume_ratio,
                        'volume_ma': volume_ma,
                        'price_change': price_change
                    }
                ))
            
            # On Balance Volume analysis
            if len(df) >= params.get('obv_period', 20):
                obv = ta.obv(df['close'], df['volume'])
                if obv is not None and not obv.empty:
                    obv_trend = obv.iloc[-1] - obv.iloc[-10]  # 10-period trend
                    
                    if abs(obv_trend) > obv.std():
                        direction = 'bullish' if obv_trend > 0 else 'bearish'
                        signals.append(IndicatorSignal(
                            indicator_name='obv',
                            signal_type=IndicatorSignalType.VOLUME,
                            direction=direction,
                            strength=min(1.0, abs(obv_trend) / (obv.std() * 2)),
                            confidence=0.5,
                            timeframe=timeframe,
                            timestamp=timestamp,
                            level=obv.iloc[-1],
                            metadata={'obv_trend': obv_trend, 'obv_current': obv.iloc[-1]}
                        ))
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Error processing volume signals: {e}")
            return []
    
    def _analyze_multi_timeframe_confluence(self, symbol: str, primary_signals: List[IndicatorSignal],
                                          confirmation_signals: List[IndicatorSignal]) -> List[SignalEvent]:
        """Analyze multi-timeframe confluence and generate final signals"""
        try:
            confluent_signals = []
            
            # Group signals by direction
            bullish_signals = [s for s in primary_signals + confirmation_signals if s.direction == 'bullish']
            bearish_signals = [s for s in primary_signals + confirmation_signals if s.direction == 'bearish']
            
            # Calculate confluence scores
            for direction, signals in [('bullish', bullish_signals), ('bearish', bearish_signals)]:
                if not signals:
                    continue
                
                confluence_score = self._calculate_confluence_score(signals)
                
                if confluence_score >= self.min_confluence_score:
                    # Create aggregated signal event
                    signal_event = self._create_signal_event(
                        symbol, direction, signals, confluence_score
                    )
                    
                    if signal_event:
                        confluent_signals.append(signal_event)
                        self.performance_metrics['signals_confirmed'] += 1
                        
                        if len([s for s in signals if s.timeframe != self.trading_timeframe]) > 0:
                            self.performance_metrics['multi_tf_confirmations'] += 1
            
            return confluent_signals
            
        except Exception as e:
            self.logger.error(f"Error analyzing multi-timeframe confluence: {e}")
            return []
    
    def _calculate_confluence_score(self, signals: List[IndicatorSignal]) -> float:
        """Calculate confluence score from multiple signals"""
        try:
            if not signals:
                return 0.0
            
            total_score = 0.0
            total_weight = 0.0
            
            # Weight signals by indicator importance and timeframe
            timeframe_multipliers = {
                'M1': 0.5, 'M5': 0.7, 'M15': 1.0, 'M30': 1.1,
                'H1': 1.3, 'H4': 1.5, 'D1': 1.8
            }
            
            signal_type_weights = {
                IndicatorSignalType.MOMENTUM: 1.2,
                IndicatorSignalType.TREND: 1.5,
                IndicatorSignalType.OSCILLATOR: 1.0,
                IndicatorSignalType.VOLATILITY: 0.8,
                IndicatorSignalType.VOLUME: 0.9,
                IndicatorSignalType.DIVERGENCE: 1.8
            }
            
            for signal in signals:
                # Get indicator config for weight
                indicator_config = self.indicator_configs.get(signal.indicator_name.split('_')[0])
                base_weight = indicator_config.confluence_weight if indicator_config else 1.0
                
                # Apply multipliers
                tf_multiplier = timeframe_multipliers.get(signal.timeframe, 1.0)
                type_weight = signal_type_weights.get(signal.signal_type, 1.0)
                
                # Calculate weighted score
                signal_weight = base_weight * tf_multiplier * type_weight
                signal_score = signal.strength * signal.confidence * signal_weight
                
                total_score += signal_score
                total_weight += signal_weight
            
            # Normalize and apply bonus for signal diversity
            if total_weight > 0:
                base_score = total_score / total_weight
                
                # Diversity bonus
                unique_indicators = len(set(s.indicator_name.split('_')[0] for s in signals))
                diversity_bonus = min(0.3, unique_indicators * 0.1)
                
                return min(5.0, base_score + diversity_bonus)
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating confluence score: {e}")
            return 0.0
    
    def _create_signal_event(self, symbol: str, direction: str, signals: List[IndicatorSignal],
                           confluence_score: float) -> SignalEvent:
        """Create a signal event from confluent indicator signals"""
        try:
            # Get representative values
            current_time = datetime.utcnow()
            primary_signal = max(signals, key=lambda s: s.strength * s.confidence)
            
            # Calculate aggregate strength and confidence
            avg_strength = sum(s.strength for s in signals) / len(signals)
            avg_confidence = sum(s.confidence for s in signals) / len(signals)
            
            # Prepare metadata
            metadata = {
                'confluence_score': confluence_score,
                'signal_count': len(signals),
                'primary_indicator': primary_signal.indicator_name,
                'timeframes': list(set(s.timeframe for s in signals)),
                'indicators': list(set(s.indicator_name for s in signals)),
                'signal_types': list(set(s.signal_type.value for s in signals)),
                'avg_strength': avg_strength,
                'avg_confidence': avg_confidence,
                'strategy_source': 'indicator_suite'
            }
            
            # Add individual signal details
            signal_details = []
            for signal in signals:
                signal_details.append({
                    'indicator': signal.indicator_name,
                    'type': signal.signal_type.value,
                    'timeframe': signal.timeframe,
                    'strength': signal.strength,
                    'confidence': signal.confidence,
                    'metadata': signal.metadata
                })
            metadata['signal_details'] = signal_details
            
            # Determine event type
            event_type = f'INDICATOR_CONFLUENCE_{direction.upper()}'
            
            return SignalEvent(
                event_type=event_type,
                symbol=symbol,
                timeframe=primary_signal.timeframe,
                timestamp=current_time,
                direction=direction,
                strength=min(1.0, confluence_score / 5.0),  # Normalize to 0-1
                level=primary_signal.level,
                metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(f"Error creating signal event: {e}")
            return None
    
    def _update_performance_metrics(self, signals: List[SignalEvent]):
        """Update strategy performance metrics"""
        try:
            self.performance_metrics['signals_generated'] += len(signals)
            
            if signals:
                avg_strength = sum(s.strength for s in signals) / len(signals)
                # Update running average
                current_avg = self.performance_metrics['average_signal_strength']
                total_signals = self.performance_metrics['signals_generated']
                
                if total_signals > 1:
                    self.performance_metrics['average_signal_strength'] = (
                        (current_avg * (total_signals - len(signals)) + avg_strength * len(signals)) / total_signals
                    )
                else:
                    self.performance_metrics['average_signal_strength'] = avg_strength
            
        except Exception as e:
            self.logger.error(f"Error updating performance metrics: {e}")
    
    def _cleanup_signal_history(self):
        """Clean up old signals from history"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(minutes=self.signal_timeout_minutes * 2)
            
            for timeframe in self.signal_history:
                old_count = len(self.signal_history[timeframe])
                self.signal_history[timeframe] = [
                    s for s in self.signal_history[timeframe] 
                    if s.timestamp >= cutoff_time
                ]
                
                if len(self.signal_history[timeframe]) < old_count:
                    self.logger.debug(f"Cleaned {old_count - len(self.signal_history[timeframe])} old signals from {timeframe}")
                    
        except Exception as e:
            self.logger.error(f"Error cleaning signal history: {e}")
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get strategy parameters for optimization"""
        return {
            'trading_timeframe': self.trading_timeframe,
            'confirmation_timeframes': self.confirmation_timeframes,
            'min_confluence_score': self.min_confluence_score,
            'signal_timeout_minutes': self.signal_timeout_minutes,
            'indicator_configs': {name: {
                'enabled': config.enabled,
                'parameters': config.parameters,
                'confluence_weight': config.confluence_weight
            } for name, config in self.indicator_configs.items()},
            'performance_metrics': self.performance_metrics
        }
    
    def validate_setup(self, setup: TradeSetup) -> bool:
        """Validate a trade setup according to indicator rules"""
        try:
            # Check confluence score threshold
            if setup.confluence_score < self.min_confluence_score:
                return False
            
            # Check for supporting indicator signals
            if 'signal_details' not in setup.metadata:
                return False
            
            signal_details = setup.metadata['signal_details']
            
            # Require at least 2 different indicator types
            indicator_types = set(detail['type'] for detail in signal_details)
            if len(indicator_types) < 2:
                return False
            
            # Check average signal strength
            avg_strength = sum(detail['strength'] for detail in signal_details) / len(signal_details)
            if avg_strength < 0.4:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating setup: {e}")
            return False
    
    def get_strategy_status(self) -> Dict[str, Any]:
        """Get comprehensive strategy status"""
        try:
            enabled_indicators = [name for name, config in self.indicator_configs.items() if config.enabled]
            
            return {
                'strategy_name': 'Enhanced Indicator Suite Strategy',
                'enabled': self.enabled,
                'trading_timeframe': self.trading_timeframe,
                'confirmation_timeframes': self.confirmation_timeframes,
                'enabled_indicators': enabled_indicators,
                'min_confluence_score': self.min_confluence_score,
                'performance_metrics': self.performance_metrics.copy(),
                'cache_size': len(self.indicator_cache),
                'signal_history_size': {tf: len(signals) for tf, signals in self.signal_history.items()}
            }
            
        except Exception as e:
            self.logger.error(f"Error getting strategy status: {e}")
            return {'error': str(e)}
    
    async def shutdown(self) -> None:
        """Shutdown strategy with cleanup"""
        try:
            self.logger.info("Shutting down Enhanced Indicator Suite Strategy...")
            
            # Shutdown thread executor
            if hasattr(self, 'executor'):
                self.executor.shutdown(wait=True)
            
            # Clear caches and history
            self.indicator_cache.clear()
            self.signal_history.clear()
            
            # Final performance report
            self.logger.info(f"Final Performance Metrics: {self.performance_metrics}")
            
            self.logger.info("Enhanced Indicator Suite Strategy shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")

    # === HELPER METHODS ===
    def _calculate_momentum(self, prices, period):
        """Calculate momentum over specified period"""
        if len(prices) <= period:
            return 0.0
        return (prices[-1] - prices[-period-1]) / prices[-period-1]
    
    def _calculate_ema(self, prices, period):
        """Calculate Exponential Moving Average"""
        if len(prices) == 0:
            return 0.0
        if len(prices) == 1:
            return prices[0]
        
        multiplier = 2.0 / (period + 1)
        ema = prices[0]
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        return ema
    
    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = np.diff(prices[-period-1:])
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains)
        avg_loss = np.mean(losses)
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_williams_r(self, highs, lows, closes, period=14):
        """Calculate Williams %R"""
        if len(closes) < period:
            return -50.0
        
        highest_high = np.max(highs[-period:])
        lowest_low = np.min(lows[-period:])
        current_close = closes[-1]
        
        if highest_high == lowest_low:
            return -50.0
        
        williams_r = -100 * ((highest_high - current_close) / (highest_high - lowest_low))
        return williams_r
    
    def _calculate_stochastic(self, highs, lows, closes, period=14):
        """Calculate Stochastic %K"""
        if len(closes) < period:
            return 50.0
        
        lowest_low = np.min(lows[-period:])
        highest_high = np.max(highs[-period:])
        current_close = closes[-1]
        
        if highest_high == lowest_low:
            return 50.0
        
        stoch_k = 100 * ((current_close - lowest_low) / (highest_high - lowest_low))
        return stoch_k
    
    def _calculate_atr(self, highs, lows, closes, period=14):
        """Calculate Average True Range"""
        if len(highs) < period + 1:
            return 0.001
        
        true_ranges = []
        for i in range(1, min(period + 1, len(highs))):
            tr1 = highs[-i] - lows[-i]
            tr2 = abs(highs[-i] - closes[-i-1])
            tr3 = abs(lows[-i] - closes[-i-1])
            true_ranges.append(max(tr1, tr2, tr3))
        
        return np.mean(true_ranges) if true_ranges else 0.001
    
    def _create_default_result(self, data, symbol, reason):
        """Create default result for insufficient data"""
        current_price = data['close'].iloc[-1] if not data.empty else 1.0
        return {
            'signal': 'HOLD',
            'confidence': 0.0,
            'direction': 'neutral',
            'price': float(current_price),
            'entry_price': float(current_price),
            'reason': f'{self.__class__.__name__}: {reason}',
            'stop_loss': None,
            'take_profit': None,
            'metadata': {'strategy_type': self.__class__.__name__.lower(), 'data_points': len(data)}
        }
    
    def _create_analysis_result(self, signal_type, confidence, direction, current_price, reasons, metadata):
        """Create comprehensive analysis result"""
        return {
            'signal': signal_type,
            'confidence': confidence,
            'direction': direction,
            'price': current_price,
            'entry_price': current_price,
            'reason': f'{self.__class__.__name__}: {", ".join(reasons)}' if reasons else f'{self.__class__.__name__}: No clear signal',
            'stop_loss': current_price * 0.995 if signal_type == "BUY" else current_price * 1.005 if signal_type == "SELL" else None,
            'take_profit': current_price * 1.015 if signal_type == "BUY" else current_price * 0.985 if signal_type == "SELL" else None,
            'metadata': {**metadata, 'data_points': len(data) if 'data' in locals() else 0}
        }
    
    def _handle_analysis_error(self, error, data, symbol):
        """Handle analysis errors gracefully"""
        current_price = data['close'].iloc[-1] if not data.empty else 1.0
        if hasattr(self, 'logger'):
            self.logger.error(f"Error in {self.__class__.__name__} analysis: {error}")
        return {
            'signal': 'HOLD',
            'confidence': 0.0,
            'direction': 'neutral',
            'price': float(current_price),
            'entry_price': float(current_price),
            'reason': f'{self.__class__.__name__}: Analysis error',
            'stop_loss': None,
            'take_profit': None,
            'metadata': {'strategy_type': self.__class__.__name__.lower(), 'error': str(error)}
        }


    # === MAIN ANALYZE METHOD ===
    def analyze(self, data: pd.DataFrame, symbol: str = None) -> Optional[Dict[str, Any]]:
        """
        Multi-indicator suite analysis combining multiple technical indicators
        """
        try:
            if data is None or data.empty or len(data) < 30:
                return self._create_default_result(data, symbol, "Insufficient data for indicator suite analysis")

            current_price = float(data['close'].iloc[-1])
            closes = data['close'].values
            highs = data.get('high', data['close']).values
            lows = data.get('low', data['close']).values
            
            # Moving averages
            sma_20 = np.mean(closes[-20:]) if len(closes) >= 20 else current_price
            ema_12 = self._calculate_ema(closes, 12)
            ema_26 = self._calculate_ema(closes, 26)
            
            # MACD
            macd = ema_12 - ema_26
            macd_signal = self._calculate_ema([macd] * 9, 9) if len(closes) >= 9 else macd
            macd_histogram = macd - macd_signal
            
            # RSI
            rsi = self._calculate_rsi(closes, 14)
            
            # Bollinger Bands
            bb_std = np.std(closes[-20:]) if len(closes) >= 20 else 0.001
            bb_upper = sma_20 + (2 * bb_std)
            bb_lower = sma_20 - (2 * bb_std)
            bb_position = (current_price - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) > 0 else 0.5
            
            # Stochastic
            stoch_k = self._calculate_stochastic(highs, lows, closes, 14)
            
            # Williams %R
            williams_r = self._calculate_williams_r(highs, lows, closes, 14)
            
            # ATR for volatility
            atr = self._calculate_atr(highs, lows, closes, 14)
            
            # Momentum
            momentum_5 = self._calculate_momentum(closes, 5)
            
            # Indicator scoring system
            bullish_score = 0
            bearish_score = 0
            reasons = []
            
            # MACD signals
            if macd > macd_signal and macd_histogram > 0:
                bullish_score += 1
                reasons.append("MACD bullish")
            elif macd < macd_signal and macd_histogram < 0:
                bearish_score += 1
                reasons.append("MACD bearish")
            
            # RSI signals
            if 30 < rsi < 70 and momentum_5 > 0.002:
                bullish_score += 1
                reasons.append(f"RSI neutral-bullish: {rsi:.1f}")
            elif 30 < rsi < 70 and momentum_5 < -0.002:
                bearish_score += 1
                reasons.append(f"RSI neutral-bearish: {rsi:.1f}")
            elif rsi < 30:
                bullish_score += 0.5  # Oversold
            elif rsi > 70:
                bearish_score += 0.5  # Overbought
            
            # Moving average signals
            if current_price > ema_12 > ema_26:
                bullish_score += 1
                reasons.append("EMA alignment bullish")
            elif current_price < ema_12 < ema_26:
                bearish_score += 1
                reasons.append("EMA alignment bearish")
            
            if current_price > sma_20:
                bullish_score += 0.5
            else:
                bearish_score += 0.5
            
            # Bollinger Bands signals
            if bb_position < 0.2 and momentum_5 > 0.001:
                bullish_score += 1
                reasons.append("BB oversold with momentum")
            elif bb_position > 0.8 and momentum_5 < -0.001:
                bearish_score += 1
                reasons.append("BB overbought with momentum")
            
            # Stochastic signals
            if stoch_k < 20 and momentum_5 > 0.001:
                bullish_score += 0.5
                reasons.append("Stochastic oversold")
            elif stoch_k > 80 and momentum_5 < -0.001:
                bearish_score += 0.5
                reasons.append("Stochastic overbought")
            
            # Williams %R signals
            if williams_r < -80 and momentum_5 > 0.001:
                bullish_score += 0.5
            elif williams_r > -20 and momentum_5 < -0.001:
                bearish_score += 0.5
            
            # Signal generation based on total scores
            signal_type = "HOLD"
            confidence = 0.0
            direction = "neutral"
            
            total_indicators = 5  # Adjust based on indicators used
            
            if bullish_score >= 3.0:
                signal_type = "BUY"
                direction = "bullish"
                confidence = min(0.9, 0.4 + (bullish_score / total_indicators) * 0.5)
            elif bearish_score >= 3.0:
                signal_type = "SELL"
                direction = "bearish"
                confidence = min(0.9, 0.4 + (bearish_score / total_indicators) * 0.5)
            elif bullish_score >= 2.0 and bullish_score > bearish_score:
                signal_type = "BUY"
                direction = "bullish"
                confidence = 0.6
            elif bearish_score >= 2.0 and bearish_score > bullish_score:
                signal_type = "SELL"
                direction = "bearish"
                confidence = 0.6
            
            return self._create_analysis_result(
                signal_type, confidence, direction, current_price, reasons,
                {
                    'sma_20': sma_20, 'ema_12': ema_12, 'ema_26': ema_26,
                    'macd': macd, 'macd_signal': macd_signal, 'macd_histogram': macd_histogram,
                    'rsi': rsi, 'bb_upper': bb_upper, 'bb_lower': bb_lower, 'bb_position': bb_position,
                    'stoch_k': stoch_k, 'williams_r': williams_r, 'atr': atr,
                    'bullish_score': bullish_score, 'bearish_score': bearish_score,
                    'momentum_5': momentum_5, 'strategy_type': 'indicator_suite'
                }
            )
            
        except Exception as e:
            return self._handle_analysis_error(e, data, symbol)

