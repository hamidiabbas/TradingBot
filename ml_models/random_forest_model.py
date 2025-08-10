"""
Enhanced Professional Random Forest Model for Trading Classification
==================================================================

A sophisticated Random Forest implementation for multi-class trading signal classification
with advanced feature engineering, real-time inference, and comprehensive performance
analytics designed for institutional-grade algorithmic trading systems.

Features:
- Multi-class classification (Strong Buy, Buy, Hold, Sell, Strong Sell)
- Advanced feature engineering with 200+ technical indicators
- Real-time prediction with confidence scoring
- Feature importance analysis and selection
- Model persistence and versioning
- Performance monitoring and drift detection
- Hyperparameter optimization using Optuna
- Professional error handling and logging
- Integration with trading strategies

Author: Enhanced Trading System
Version: 3.0 Professional
License: Proprietary
"""

import asyncio
import logging
import numpy as np
import pandas as pd
import warnings
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, field
from pathlib import Path
import pickle
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score,
    precision_score, recall_score, f1_score, roc_auc_score
)
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
import optuna
import ta
import pandas_ta as pta
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

from utils.logger import setup_logging

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

class TradingSignal:
    """Trading signal enumeration with confidence levels"""
    STRONG_SELL = 0
    SELL = 1
    HOLD = 2
    BUY = 3
    STRONG_BUY = 4
    
    @classmethod
    def get_signal_name(cls, signal_value: int) -> str:
        """Get signal name from numeric value"""
        signal_map = {
            0: "STRONG_SELL",
            1: "SELL", 
            2: "HOLD",
            3: "BUY",
            4: "STRONG_BUY"
        }
        return signal_map.get(signal_value, "UNKNOWN")
    
    @classmethod
    def from_return(cls, future_return: float, threshold_strong: float = 0.02, 
                   threshold_weak: float = 0.005) -> int:
        """Convert future return to signal classification"""
        if future_return >= threshold_strong:
            return cls.STRONG_BUY
        elif future_return >= threshold_weak:
            return cls.BUY
        elif future_return <= -threshold_strong:
            return cls.STRONG_SELL
        elif future_return <= -threshold_weak:
            return cls.SELL
        else:
            return cls.HOLD

@dataclass
class RandomForestConfig:
    """Random Forest model configuration with comprehensive parameters"""
    # Model architecture parameters
    n_estimators: int = 200
    max_depth: Optional[int] = 20
    min_samples_split: int = 5
    min_samples_leaf: int = 2
    max_features: str = 'sqrt'  # 'sqrt', 'log2', or int
    bootstrap: bool = True
    random_state: int = 42
    
    # Feature engineering parameters
    lookback_period: int = 30
    prediction_horizon: int = 5  # Periods to predict ahead
    use_technical_indicators: bool = True
    use_price_patterns: bool = True
    use_volume_features: bool = True
    use_volatility_features: bool = True
    use_momentum_features: bool = True
    use_trend_features: bool = True
    
    # Feature selection parameters
    feature_selection_method: str = 'importance'  # 'importance', 'statistical', 'mutual_info'
    max_features_selected: int = 50
    feature_importance_threshold: float = 0.001
    
    # Training parameters
    test_size: float = 0.2
    validation_size: float = 0.2
    cross_validation_folds: int = 5
    
    # Signal classification parameters
    strong_signal_threshold: float = 0.02  # 2% price movement
    weak_signal_threshold: float = 0.005   # 0.5% price movement
    
    # Model management
    model_save_path: str = "models/random_forest/"
    enable_optimization: bool = True
    optimization_trials: int = 100

@dataclass
class RandomForestPrediction:
    """Random Forest prediction result with comprehensive metadata"""
    signal: int
    signal_name: str
    confidence: float
    probabilities: Dict[str, float]
    feature_contributions: Dict[str, float]
    model_version: str
    prediction_time: datetime
    input_features: Dict[str, float]
    risk_score: float
    
class RandomForestFeatureEngineering:
    """Advanced feature engineering for Random Forest model"""
    
    def __init__(self, config: RandomForestConfig):
        self.config = config
        self.scaler = StandardScaler()
        self.feature_names = []
        self.feature_groups = {}
        self.logger = setup_logging('INFO')
        
    def engineer_comprehensive_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Engineer comprehensive feature set for Random Forest training"""
        try:
            self.logger.info("Starting comprehensive feature engineering...")
            
            features_df = data.copy()
            original_columns = set(features_df.columns)
            
            # Basic price features
            features_df = self._add_basic_price_features(features_df)
            
            # Technical indicators
            if self.config.use_technical_indicators:
                features_df = self._add_technical_indicators(features_df)
            
            # Price patterns
            if self.config.use_price_patterns:
                features_df = self._add_price_patterns(features_df)
            
            # Volume features
            if self.config.use_volume_features and 'volume' in features_df.columns:
                features_df = self._add_volume_features(features_df)
            
            # Volatility features
            if self.config.use_volatility_features:
                features_df = self._add_volatility_features(features_df)
            
            # Momentum features
            if self.config.use_momentum_features:
                features_df = self._add_momentum_features(features_df)
            
            # Trend features
            if self.config.use_trend_features:
                features_df = self._add_trend_features(features_df)
            
            # Statistical features
            features_df = self._add_statistical_features(features_df)
            
            # Market microstructure features
            features_df = self._add_microstructure_features(features_df)
            
            # Time-based features
            features_df = self._add_temporal_features(features_df)
            
            # Cross-sectional features
            features_df = self._add_cross_sectional_features(features_df)
            
            # Clean and prepare data
            features_df = self._clean_and_prepare_data(features_df)
            
            # Store feature names and groups
            new_features = set(features_df.columns) - original_columns - {'target'}
            self.feature_names = list(new_features)
            self._categorize_features()
            
            self.logger.info(f"Feature engineering completed. Generated {len(self.feature_names)} features")
            
            return features_df
            
        except Exception as e:
            self.logger.error(f"Error in comprehensive feature engineering: {e}")
            return data
    
    def _add_basic_price_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add basic price-based features"""
        try:
            # Returns
            data['returns_1'] = data['close'].pct_change(1)
            data['returns_5'] = data['close'].pct_change(5)
            data['returns_20'] = data['close'].pct_change(20)
            
            # Log returns
            data['log_returns_1'] = np.log(data['close'] / data['close'].shift(1))
            data['log_returns_5'] = np.log(data['close'] / data['close'].shift(5))
            
            # Price ratios
            data['high_low_ratio'] = data['high'] / data['low']
            data['close_open_ratio'] = data['close'] / data['open']
            
            # Gap analysis
            data['gap'] = (data['open'] - data['close'].shift(1)) / data['close'].shift(1)
            data['gap_filled'] = (data['gap'] > 0) & (data['low'] <= data['close'].shift(1))
            
            # Price position within range
            data['price_position'] = (data['close'] - data['low']) / (data['high'] - data['low'])
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error adding basic price features: {e}")
            return data
    
    def _add_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add comprehensive technical indicators"""
        try:
            # Trend indicators
            for period in [10, 20, 50, 100, 200]:
                data[f'sma_{period}'] = ta.trend.sma_indicator(data['close'], window=period)
                data[f'ema_{period}'] = ta.trend.ema_indicator(data['close'], window=period)
                data[f'price_above_sma_{period}'] = (data['close'] > data[f'sma_{period}']).astype(int)
                data[f'price_above_ema_{period}'] = (data['close'] > data[f'ema_{period}']).astype(int)
            
            # Moving average slopes
            for period in [10, 20, 50]:
                ma_col = f'sma_{period}'
                data[f'{ma_col}_slope'] = data[ma_col].diff(5) / data[ma_col].shift(5)
            
            # MACD variations
            data['macd'] = ta.trend.macd_diff(data['close'])
            data['macd_signal'] = ta.trend.macd_signal(data['close'])
            data['macd_histogram'] = ta.trend.macd_diff(data['close']) - ta.trend.macd_signal(data['close'])
            
            # Multiple MACD timeframes
            for fast, slow, signal in [(5, 13, 9), (12, 26, 9), (19, 39, 9)]:
                macd_line = ta.trend.ema_indicator(data['close'], window=fast) - ta.trend.ema_indicator(data['close'], window=slow)
                signal_line = ta.trend.ema_indicator(macd_line, window=signal)
                data[f'macd_{fast}_{slow}'] = macd_line - signal_line
            
            # Momentum indicators
            for period in [7, 14, 21]:
                data[f'rsi_{period}'] = ta.momentum.rsi(data['close'], window=period)
                data[f'roc_{period}'] = ta.momentum.roc(data['close'], window=period)
            
            # Stochastic oscillator variations
            for k_period, d_period in [(14, 3), (21, 5), (5, 3)]:
                data[f'stoch_k_{k_period}_{d_period}'] = ta.momentum.stoch(data['high'], data['low'], data['close'], window=k_period, smooth_window=d_period)
                data[f'stoch_d_{k_period}_{d_period}'] = ta.momentum.stoch_signal(data['high'], data['low'], data['close'], window=k_period, smooth_window=d_period)
            
            # Williams %R
            for period in [14, 21]:
                data[f'williams_r_{period}'] = ta.momentum.williams_r(data['high'], data['low'], data['close'], lbp=period)
            
            # Commodity Channel Index
            for period in [14, 20]:
                data[f'cci_{period}'] = ta.trend.cci(data['high'], data['low'], data['close'], window=period)
            
            # Volatility indicators
            for period in [10, 20, 30]:
                data[f'bb_upper_{period}'] = ta.volatility.bollinger_hband(data['close'], window=period)
                data[f'bb_lower_{period}'] = ta.volatility.bollinger_lband(data['close'], window=period)
                data[f'bb_width_{period}'] = data[f'bb_upper_{period}'] - data[f'bb_lower_{period}']
                data[f'bb_position_{period}'] = (data['close'] - data[f'bb_lower_{period}']) / data[f'bb_width_{period}']
            
            # Average True Range
            for period in [7, 14, 21]:
                data[f'atr_{period}'] = ta.volatility.average_true_range(data['high'], data['low'], data['close'], window=period)
                data[f'atr_ratio_{period}'] = data[f'atr_{period}'] / data['close']
            
            # Keltner Channels
            data['keltner_upper'] = ta.volatility.keltner_channel_hband(data['high'], data['low'], data['close'])
            data['keltner_lower'] = ta.volatility.keltner_channel_lband(data['high'], data['low'], data['close'])
            data['keltner_position'] = (data['close'] - data['keltner_lower']) / (data['keltner_upper'] - data['keltner_lower'])
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error adding technical indicators: {e}")
            return data
    
    def _add_price_patterns(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add price pattern recognition features"""
        try:
            # Candlestick patterns
            data['doji'] = self._detect_doji(data)
            data['hammer'] = self._detect_hammer(data)
            data['shooting_star'] = self._detect_shooting_star(data)
            data['engulfing_bullish'] = self._detect_engulfing_bullish(data)
            data['engulfing_bearish'] = self._detect_engulfing_bearish(data)
            data['morning_star'] = self._detect_morning_star(data)
            data['evening_star'] = self._detect_evening_star(data)
            
            # Chart patterns
            data['higher_highs'] = self._detect_higher_highs(data['high'])
            data['lower_lows'] = self._detect_lower_lows(data['low'])
            data['double_top'] = self._detect_double_top(data)
            data['double_bottom'] = self._detect_double_bottom(data)
            
            # Support and resistance
            data['support_strength'] = self._calculate_support_strength(data)
            data['resistance_strength'] = self._calculate_resistance_strength(data)
            data['distance_to_support'] = self._calculate_distance_to_support(data)
            data['distance_to_resistance'] = self._calculate_distance_to_resistance(data)
            
            # Fibonacci levels
            data = self._add_fibonacci_features(data)
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error adding price patterns: {e}")
            return data
    
    def _add_volume_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add volume-based features"""
        try:
            volume = data['volume']
            close = data['close']
            
            # Basic volume features
            for period in [5, 10, 20]:
                data[f'volume_sma_{period}'] = volume.rolling(period).mean()
                data[f'volume_ratio_{period}'] = volume / data[f'volume_sma_{period}']
                data[f'volume_std_{period}'] = volume.rolling(period).std()
            
            # Volume indicators
            data['obv'] = ta.volume.on_balance_volume(close, volume)
            data['obv_ema'] = ta.trend.ema_indicator(data['obv'], window=20)
            
            # Accumulation/Distribution Line
            data['ad_line'] = ta.volume.acc_dist_index(data['high'], data['low'], close, volume)
            
            # Chaikin Money Flow
            data['cmf'] = ta.volume.chaikin_money_flow(data['high'], data['low'], close, volume)
            
            # Money Flow Index
            data['mfi'] = ta.volume.money_flow_index(data['high'], data['low'], close, volume)
            
            # Volume Price Trend
            data['vpt'] = ta.volume.volume_price_trend(close, volume)
            
            # Volume-Price analysis
            data['price_volume_corr'] = close.rolling(20).corr(volume)
            data['volume_price_trend'] = (close.diff() * volume).rolling(10).sum()
            
            # Volume surge detection
            data['volume_surge'] = (volume > volume.rolling(20).mean() + 2 * volume.rolling(20).std()).astype(int)
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error adding volume features: {e}")
            return data
    
    def _add_volatility_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add volatility-based features"""
        try:
            # Historical volatility
            returns = data['close'].pct_change()
            for period in [5, 10, 20, 30]:
                data[f'volatility_{period}'] = returns.rolling(period).std() * np.sqrt(252)
                data[f'volatility_rank_{period}'] = data[f'volatility_{period}'].rolling(252).rank(pct=True)
            
            # GARCH-like features
            data['volatility_clustering'] = returns.abs().rolling(5).mean()
            
            # Parkinson estimator (using high/low)
            data['parkinson_volatility'] = np.sqrt(
                (1/(4*np.log(2))) * np.log(data['high']/data['low'])**2
            ).rolling(20).mean()
            
            # Garman-Klass estimator
            data['gk_volatility'] = np.sqrt(
                0.5 * np.log(data['high']/data['low'])**2 - 
                (2*np.log(2)-1) * np.log(data['close']/data['open'])**2
            ).rolling(20).mean()
            
            # Volatility ratios
            data['volatility_ratio_5_20'] = data['volatility_5'] / data['volatility_20']
            data['volatility_ratio_10_30'] = data['volatility_10'] / data['volatility_30']
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error adding volatility features: {e}")
            return data
    
    def _add_momentum_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add momentum-based features"""
        try:
            close = data['close']
            
            # Price momentum
            for period in [1, 3, 5, 10, 20]:
                data[f'momentum_{period}'] = close / close.shift(period) - 1
            
            # Acceleration (second derivative)
            data['acceleration_5'] = data['momentum_5'].diff()
            data['acceleration_10'] = data['momentum_10'].diff()
            
            # Momentum oscillators
            data['awesome_oscillator'] = ta.momentum.awesome_oscillator(data['high'], data['low'])
            data['ultimate_oscillator'] = ta.momentum.ultimate_oscillator(data['high'], data['low'], close)
            
            # Custom momentum indicators
            data['momentum_divergence'] = self._calculate_momentum_divergence(data)
            data['momentum_strength'] = self._calculate_momentum_strength(data)
            
            # Relative strength vs market (if benchmark available)
            # data['relative_strength'] = self._calculate_relative_strength(data)
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error adding momentum features: {e}")
            return data
    
    def _add_trend_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add trend-based features"""
        try:
            close = data['close']
            
            # ADX - Average Directional Index
            data['adx'] = ta.trend.adx(data['high'], data['low'], close)
            data['adx_pos'] = ta.trend.adx_pos(data['high'], data['low'], close)
            data['adx_neg'] = ta.trend.adx_neg(data['high'], data['low'], close)
            
            # Parabolic SAR
            data['psar'] = ta.trend.psar_down(data['high'], data['low'], close)
            data['psar_signal'] = (close > data['psar']).astype(int)
            
            # Trend strength
            for period in [10, 20, 50]:
                slope, _, r_value, _, _ = stats.linregress(
                    range(period), close.rolling(period).apply(
                        lambda x: stats.linregress(range(len(x)), x)[0] if len(x) == period else np.nan
                    )
                )
                data[f'trend_strength_{period}'] = abs(r_value) if not np.isnan(r_value) else 0
                data[f'trend_direction_{period}'] = np.sign(slope) if not np.isnan(slope) else 0
            
            # Trendline analysis
            data['upper_trendline'] = self._calculate_upper_trendline(data)
            data['lower_trendline'] = self._calculate_lower_trendline(data)
            data['trendline_position'] = (close - data['lower_trendline']) / (data['upper_trendline'] - data['lower_trendline'])
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error adding trend features: {e}")
            return data
    
    def _add_statistical_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add statistical features"""
        try:
            close = data['close']
            
            # Rolling statistics
            for period in [5, 10, 20]:
                data[f'mean_{period}'] = close.rolling(period).mean()
                data[f'std_{period}'] = close.rolling(period).std()
                data[f'skew_{period}'] = close.rolling(period).skew()
                data[f'kurt_{period}'] = close.rolling(period).kurt()
                data[f'z_score_{period}'] = (close - data[f'mean_{period}']) / data[f'std_{period}']
            
            # Percentile ranks
            for period in [20, 50, 100]:
                data[f'percentile_rank_{period}'] = close.rolling(period).rank(pct=True)
            
            # Mean reversion features
            data['mean_reversion_5'] = (close - close.rolling(5).mean()) / close.rolling(5).std()
            data['mean_reversion_20'] = (close - close.rolling(20).mean()) / close.rolling(20).std()
            
            # Autocorrelation
            for lag in [1, 5, 10]:
                data[f'autocorr_{lag}'] = close.rolling(50).apply(
                    lambda x: x.autocorr(lag) if len(x) >= 50 else np.nan
                )
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error adding statistical features: {e}")
            return data
    
    def _add_microstructure_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add market microstructure features"""
        try:
            # Spread analysis
            data['hl_spread'] = (data['high'] - data['low']) / data['close']
            data['oc_spread'] = abs(data['open'] - data['close']) / data['close']
            
            # Intraday patterns
            if isinstance(data.index, pd.DatetimeIndex):
                data['hour_of_day'] = data.index.hour
                data['day_of_week'] = data.index.dayofweek
                data['is_monday'] = (data.index.dayofweek == 0).astype(int)
                data['is_friday'] = (data.index.dayofweek == 4).astype(int)
            
            # Price efficiency
            data['price_efficiency'] = self._calculate_price_efficiency(data)
            
            # Order flow approximation
            data['buying_pressure'] = (data['close'] - data['low']) / (data['high'] - data['low'])
            data['selling_pressure'] = (data['high'] - data['close']) / (data['high'] - data['low'])
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error adding microstructure features: {e}")
            return data
    
    def _add_temporal_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add time-based features"""
        try:
            if isinstance(data.index, pd.DatetimeIndex):
                # Calendar features
                data['month'] = data.index.month
                data['quarter'] = data.index.quarter
                data['is_month_end'] = data.index.is_month_end.astype(int)
                data['is_quarter_end'] = data.index.is_quarter_end.astype(int)
                
                # Cyclical encoding
                data['hour_sin'] = np.sin(2 * np.pi * data.index.hour / 24)
                data['hour_cos'] = np.cos(2 * np.pi * data.index.hour / 24)
                data['day_sin'] = np.sin(2 * np.pi * data.index.dayofweek / 7)
                data['day_cos'] = np.cos(2 * np.pi * data.index.dayofweek / 7)
                data['month_sin'] = np.sin(2 * np.pi * data.index.month / 12)
                data['month_cos'] = np.cos(2 * np.pi * data.index.month / 12)
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error adding temporal features: {e}")
            return data
    
    def _add_cross_sectional_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add cross-sectional analysis features"""
        try:
            # Regime detection
            data['regime_volatility'] = self._detect_volatility_regime(data)
            data['regime_trend'] = self._detect_trend_regime(data)
            
            # Market stress indicators
            data['stress_indicator'] = self._calculate_stress_indicator(data)
            
            # Correlation with lagged values
            for lag in [1, 5, 20]:
                data[f'price_lag_{lag}'] = data['close'].shift(lag)
                data[f'volume_lag_{lag}'] = data['volume'].shift(lag) if 'volume' in data.columns else 0
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error adding cross-sectional features: {e}")
            return data
    
    def _clean_and_prepare_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare data for model training"""
        try:
            # Handle infinite values
            data = data.replace([np.inf, -np.inf], np.nan)
            
            # Forward fill then backward fill
            data = data.fillna(method='ffill').fillna(method='bfill')
            
            # Fill remaining NaN with 0
            data = data.fillna(0)
            
            # Remove highly correlated features
            data = self._remove_highly_correlated_features(data)
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error cleaning and preparing data: {e}")
            return data
    
    def _remove_highly_correlated_features(self, data: pd.DataFrame, threshold: float = 0.95) -> pd.DataFrame:
        """Remove highly correlated features"""
        try:
            # Calculate correlation matrix for numeric columns only
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) <= 1:
                return data
                
            corr_matrix = data[numeric_cols].corr().abs()
            
            # Find highly correlated pairs
            upper_tri = corr_matrix.where(
                np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
            )
            
            # Find features to drop
            to_drop = [column for column in upper_tri.columns if any(upper_tri[column] > threshold)]
            
            # Keep the first feature in each highly correlated pair
            data_cleaned = data.drop(columns=to_drop)
            
            if len(to_drop) > 0:
                self.logger.info(f"Removed {len(to_drop)} highly correlated features")
            
            return data_cleaned
            
        except Exception as e:
            self.logger.error(f"Error removing correlated features: {e}")
            return data
    
    def _categorize_features(self):
        """Categorize features into groups for analysis"""
        try:
            self.feature_groups = {
                'price': [f for f in self.feature_names if any(x in f for x in ['returns', 'ratio', 'gap', 'position'])],
                'technical': [f for f in self.feature_names if any(x in f for x in ['sma', 'ema', 'macd', 'rsi', 'stoch', 'bb', 'atr'])],
                'volume': [f for f in self.feature_names if any(x in f for x in ['volume', 'obv', 'cmf', 'mfi', 'vpt'])],
                'volatility': [f for f in self.feature_names if any(x in f for x in ['volatility', 'parkinson', 'gk'])],
                'momentum': [f for f in self.feature_names if any(x in f for x in ['momentum', 'roc', 'acceleration'])],
                'trend': [f for f in self.feature_names if any(x in f for x in ['adx', 'psar', 'trend'])],
                'patterns': [f for f in self.feature_names if any(x in f for x in ['doji', 'hammer', 'engulfing', 'higher', 'lower'])],
                'statistical': [f for f in self.feature_names if any(x in f for x in ['mean', 'std', 'skew', 'kurt', 'z_score'])],
                'temporal': [f for f in self.feature_names if any(x in f for x in ['hour', 'day', 'month', 'sin', 'cos'])],
                'microstructure': [f for f in self.feature_names if any(x in f for x in ['spread', 'efficiency', 'pressure'])]
            }
            
        except Exception as e:
            self.logger.error(f"Error categorizing features: {e}")
    
    # Helper methods for pattern detection
    def _detect_doji(self, data: pd.DataFrame) -> pd.Series:
        """Detect Doji candlestick pattern"""
        try:
            body = abs(data['close'] - data['open'])
            range_size = data['high'] - data['low']
            return (body / range_size < 0.1).astype(int)
        except:
            return pd.Series(0, index=data.index)
    
    def _detect_hammer(self, data: pd.DataFrame) -> pd.Series:
        """Detect Hammer pattern"""
        try:
            body = abs(data['close'] - data['open'])
            lower_shadow = np.minimum(data['open'], data['close']) - data['low']
            upper_shadow = data['high'] - np.maximum(data['open'], data['close'])
            return ((lower_shadow > body * 2) & (upper_shadow < body * 0.5)).astype(int)
        except:
            return pd.Series(0, index=data.index)
    
    def _detect_shooting_star(self, data: pd.DataFrame) -> pd.Series:
        """Detect Shooting Star pattern"""
        try:
            body = abs(data['close'] - data['open'])
            upper_shadow = data['high'] - np.maximum(data['open'], data['close'])
            lower_shadow = np.minimum(data['open'], data['close']) - data['low']
            return ((upper_shadow > body * 2) & (lower_shadow < body * 0.5)).astype(int)
        except:
            return pd.Series(0, index=data.index)
    
    def _detect_engulfing_bullish(self, data: pd.DataFrame) -> pd.Series:
        """Detect Bullish Engulfing pattern"""
        try:
            curr_bullish = data['close'] > data['open']
            prev_bearish = data['close'].shift(1) < data['open'].shift(1)
            curr_open_below_prev_close = data['open'] < data['close'].shift(1)
            curr_close_above_prev_open = data['close'] > data['open'].shift(1)
            
            return (curr_bullish & prev_bearish & curr_open_below_prev_close & curr_close_above_prev_open).astype(int)
        except:
            return pd.Series(0, index=data.index)
    
    def _detect_engulfing_bearish(self, data: pd.DataFrame) -> pd.Series:
        """Detect Bearish Engulfing pattern"""
        try:
            curr_bearish = data['close'] < data['open']
            prev_bullish = data['close'].shift(1) > data['open'].shift(1)
            curr_open_above_prev_close = data['open'] > data['close'].shift(1)
            curr_close_below_prev_open = data['close'] < data['open'].shift(1)
            
            return (curr_bearish & prev_bullish & curr_open_above_prev_close & curr_close_below_prev_open).astype(int)
        except:
            return pd.Series(0, index=data.index)
    
    def _detect_morning_star(self, data: pd.DataFrame) -> pd.Series:
        """Detect Morning Star pattern"""
        try:
            # Simplified 3-candle morning star detection
            first_bearish = data['close'].shift(2) < data['open'].shift(2)
            second_small = abs(data['close'].shift(1) - data['open'].shift(1)) < (data['high'].shift(1) - data['low'].shift(1)) * 0.3
            third_bullish = data['close'] > data['open']
            gap_down = data['open'].shift(1) < data['close'].shift(2)
            gap_up = data['open'] > data['close'].shift(1)
            
            return (first_bearish & second_small & third_bullish & gap_down & gap_up).astype(int)
        except:
            return pd.Series(0, index=data.index)
    
    def _detect_evening_star(self, data: pd.DataFrame) -> pd.Series:
        """Detect Evening Star pattern"""
        try:
            # Simplified 3-candle evening star detection
            first_bullish = data['close'].shift(2) > data['open'].shift(2)
            second_small = abs(data['close'].shift(1) - data['open'].shift(1)) < (data['high'].shift(1) - data['low'].shift(1)) * 0.3
            third_bearish = data['close'] < data['open']
            gap_up = data['open'].shift(1) > data['close'].shift(2)
            gap_down = data['open'] < data['close'].shift(1)
            
            return (first_bullish & second_small & third_bearish & gap_up & gap_down).astype(int)
        except:
            return pd.Series(0, index=data.index)
    
    def _detect_higher_highs(self, highs: pd.Series, window: int = 5) -> pd.Series:
        """Detect higher highs pattern"""
        try:
            rolling_max = highs.rolling(window).max()
            return (highs > rolling_max.shift(1)).astype(int)
        except:
            return pd.Series(0, index=highs.index)
    
    def _detect_lower_lows(self, lows: pd.Series, window: int = 5) -> pd.Series:
        """Detect lower lows pattern"""
        try:
            rolling_min = lows.rolling(window).min()
            return (lows < rolling_min.shift(1)).astype(int)
        except:
            return pd.Series(0, index=lows.index)
    
    def _detect_double_top(self, data: pd.DataFrame) -> pd.Series:
        """Detect double top pattern"""
        try:
            # Simplified double top detection
            high_20 = data['high'].rolling(20).max()
            is_peak = data['high'] == high_20
            prev_peak = is_peak.shift(10)
            similar_level = abs(data['high'] - data['high'].shift(10)) / data['high'] < 0.02
            
            return (is_peak & prev_peak & similar_level).astype(int)
        except:
            return pd.Series(0, index=data.index)
    
    def _detect_double_bottom(self, data: pd.DataFrame) -> pd.Series:
        """Detect double bottom pattern"""
        try:
            # Simplified double bottom detection
            low_20 = data['low'].rolling(20).min()
            is_trough = data['low'] == low_20
            prev_trough = is_trough.shift(10)
            similar_level = abs(data['low'] - data['low'].shift(10)) / data['low'] < 0.02
            
            return (is_trough & prev_trough & similar_level).astype(int)
        except:
            return pd.Series(0, index=data.index)
    
    # Additional helper methods
    def _calculate_support_strength(self, data: pd.DataFrame) -> pd.Series:
        """Calculate support level strength"""
        try:
            low_20 = data['low'].rolling(20).min()
            touches = (abs(data['low'] - low_20) / data['low'] < 0.005).rolling(20).sum()
            return touches
        except:
            return pd.Series(0, index=data.index)
    
    def _calculate_resistance_strength(self, data: pd.DataFrame) -> pd.Series:
        """Calculate resistance level strength"""
        try:
            high_20 = data['high'].rolling(20).max()
            touches = (abs(data['high'] - high_20) / data['high'] < 0.005).rolling(20).sum()
            return touches
        except:
            return pd.Series(0, index=data.index)
    
    def _calculate_distance_to_support(self, data: pd.DataFrame) -> pd.Series:
        """Calculate distance to nearest support"""
        try:
            support_level = data['low'].rolling(20).min()
            return (data['close'] - support_level) / data['close']
        except:
            return pd.Series(0, index=data.index)
    
    def _calculate_distance_to_resistance(self, data: pd.DataFrame) -> pd.Series:
        """Calculate distance to nearest resistance"""
        try:
            resistance_level = data['high'].rolling(20).max()
            return (resistance_level - data['close']) / data['close']
        except:
            return pd.Series(0, index=data.index)
    
    def _add_fibonacci_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add Fibonacci retracement features"""
        try:
            # Calculate recent swing high and low
            swing_high = data['high'].rolling(20).max()
            swing_low = data['low'].rolling(20).min()
            swing_range = swing_high - swing_low
            
            # Fibonacci levels
            fib_levels = [0.236, 0.382, 0.5, 0.618, 0.786]
            
            for level in fib_levels:
                data[f'fib_{int(level*1000)}'] = swing_low + swing_range * level
                data[f'fib_{int(level*1000)}_distance'] = abs(data['close'] - data[f'fib_{int(level*1000)}']) / data['close']
            
            return data
        except:
            return data
    
    def _calculate_momentum_divergence(self, data: pd.DataFrame) -> pd.Series:
        """Calculate momentum divergence"""
        try:
            price_peaks = data['high'].rolling(5).max() == data['high']
            rsi = ta.momentum.rsi(data['close'], window=14)
            rsi_peaks = rsi.rolling(5).max() == rsi
            
            # Simplified divergence detection
            divergence = price_peaks & ~rsi_peaks
            return divergence.astype(int)
        except:
            return pd.Series(0, index=data.index)
    
    def _calculate_momentum_strength(self, data: pd.DataFrame) -> pd.Series:
        """Calculate overall momentum strength"""
        try:
            # Combine multiple momentum indicators
            rsi = ta.momentum.rsi(data['close'], window=14)
            roc = ta.momentum.roc(data['close'], window=10)
            
            # Normalize and combine
            rsi_norm = (rsi - 50) / 50
            roc_norm = np.tanh(roc * 100)
            
            momentum_strength = (rsi_norm + roc_norm) / 2
            return momentum_strength
        except:
            return pd.Series(0, index=data.index)
    
    def _calculate_upper_trendline(self, data: pd.DataFrame) -> pd.Series:
        """Calculate upper trendline"""
        try:
            return data['high'].rolling(20).max()
        except:
            return pd.Series(data['high'].iloc[0], index=data.index)
    
    def _calculate_lower_trendline(self, data: pd.DataFrame) -> pd.Series:
        """Calculate lower trendline"""
        try:
            return data['low'].rolling(20).min()
        except:
            return pd.Series(data['low'].iloc[0], index=data.index)
    
    def _calculate_price_efficiency(self, data: pd.DataFrame) -> pd.Series:
        """Calculate price movement efficiency"""
        try:
            price_change = abs(data['close'] - data['close'].shift(10))
            path_length = abs(data['close'].diff()).rolling(10).sum()
            
            efficiency = price_change / path_length
            return efficiency.fillna(0)
        except:
            return pd.Series(0, index=data.index)
    
    def _detect_volatility_regime(self, data: pd.DataFrame) -> pd.Series:
        """Detect volatility regime"""
        try:
            volatility = data['close'].pct_change().rolling(20).std()
            vol_median = volatility.rolling(100).median()
            
            regime = (volatility > vol_median).astype(int)  # 1 = high vol, 0 = low vol
            return regime
        except:
            return pd.Series(0, index=data.index)
    
    def _detect_trend_regime(self, data: pd.DataFrame) -> pd.Series:
        """Detect trend regime"""
        try:
            adx = ta.trend.adx(data['high'], data['low'], data['close'])
            regime = (adx > 25).astype(int)  # 1 = trending, 0 = ranging
            return regime
        except:
            return pd.Series(0, index=data.index)
    
    def _calculate_stress_indicator(self, data: pd.DataFrame) -> pd.Series:
        """Calculate market stress indicator"""
        try:
            # Combine volatility and gap analysis
            volatility = data['close'].pct_change().rolling(5).std()
            gaps = abs(data['open'] - data['close'].shift(1)) / data['close'].shift(1)
            
            stress = (volatility + gaps).rolling(5).mean()
            return stress.fillna(0)
        except:
            return pd.Series(0, index=data.index)

class EnhancedRandomForestModel:
    """
    Enhanced Professional Random Forest Model for Trading Applications
    
    This class implements a sophisticated Random Forest-based classification model
    for multi-class trading signal prediction with advanced features including
    feature selection, hyperparameter optimization, and real-time inference.
    """
    
    def __init__(self, config: RandomForestConfig):
        self.config = config
        self.model = None
        self.feature_engineer = RandomForestFeatureEngineering(config)
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_selector = None
        self.selected_features = []
        self.model_version = "1.0"
        self.training_history = {}
        self.feature_importance = {}
        
        # Setup logging
        self.logger = setup_logging('INFO')
        
        # Create model directory
        Path(self.config.model_save_path).mkdir(parents=True, exist_ok=True)
    
    def prepare_training_data(self, data: pd.DataFrame, target_col: str = 'close') -> Tuple[np.ndarray, np.ndarray]:
        """Prepare comprehensive training data for Random Forest model"""
        try:
            self.logger.info("Preparing training data with comprehensive feature engineering...")
            
            # Engineer features
            featured_data = self.feature_engineer.engineer_comprehensive_features(data)
            
            # Create target variable (future returns classification)
            future_returns = featured_data[target_col].shift(-self.config.prediction_horizon) / featured_data[target_col] - 1
            featured_data['target'] = future_returns.apply(
                lambda x: TradingSignal.from_return(
                    x, 
                    self.config.strong_signal_threshold, 
                    self.config.weak_signal_threshold
                ) if not pd.isna(x) else TradingSignal.HOLD
            )
            
            # Remove rows with NaN targets
            featured_data = featured_data.dropna(subset=['target'])
            
            if len(featured_data) < 100:
                raise ValueError("Insufficient data after feature engineering and target creation")
            
            # Separate features and target
            feature_cols = [col for col in featured_data.columns 
                           if col not in ['target', 'close', 'open', 'high', 'low', 'volume']]
            
            X_data = featured_data[feature_cols]
            y_data = featured_data['target'].astype(int)
            
            # Feature selection
            if self.config.feature_selection_method != 'none':
                X_data = self._select_features(X_data, y_data)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X_data)
            
            self.logger.info(f"Prepared training data: {X_scaled.shape[0]} samples, {X_scaled.shape[1]} features")
            self.logger.info(f"Target distribution: {np.bincount(y_data)}")
            
            return X_scaled, y_data.values
            
        except Exception as e:
            self.logger.error(f"Error preparing training data: {e}")
            raise
    
    def _select_features(self, X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
        """Select best features using specified method"""
        try:
            if self.config.feature_selection_method == 'importance':
                # Use a quick Random Forest to get feature importance
                quick_rf = RandomForestClassifier(
                    n_estimators=50, 
                    random_state=self.config.random_state,
                    n_jobs=-1
                )
                quick_rf.fit(X, y)
                
                # Get feature importance
                importance_scores = quick_rf.feature_importances_
                feature_importance_df = pd.DataFrame({
                    'feature': X.columns,
                    'importance': importance_scores
                }).sort_values('importance', ascending=False)
                
                # Select top features
                selected_features = feature_importance_df.head(self.config.max_features_selected)['feature'].tolist()
                
            elif self.config.feature_selection_method == 'statistical':
                # Use statistical tests
                self.feature_selector = SelectKBest(
                    score_func=f_classif,
                    k=min(self.config.max_features_selected, X.shape[1])
                )
                X_selected = self.feature_selector.fit_transform(X, y)
                selected_features = X.columns[self.feature_selector.get_support()].tolist()
                
            elif self.config.feature_selection_method == 'mutual_info':
                # Use mutual information
                self.feature_selector = SelectKBest(
                    score_func=mutual_info_classif,
                    k=min(self.config.max_features_selected, X.shape[1])
                )
                X_selected = self.feature_selector.fit_transform(X, y)
                selected_features = X.columns[self.feature_selector.get_support()].tolist()
            
            else:
                selected_features = X.columns.tolist()
            
            # Store selected features
            self.selected_features = selected_features
            
            self.logger.info(f"Selected {len(selected_features)} features using {self.config.feature_selection_method} method")
            
            return X[selected_features]
            
        except Exception as e:
            self.logger.error(f"Error in feature selection: {e}")
            return X
    
    def train(self, data: pd.DataFrame, target_col: str = 'close') -> Dict[str, Any]:
        """Train the Random Forest model with comprehensive evaluation"""
        try:
            self.logger.info("Starting Random Forest model training...")
            
            # Prepare data
            X, y = self.prepare_training_data(data, target_col)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, 
                test_size=self.config.test_size,
                random_state=self.config.random_state,
                stratify=y
            )
            
            # Further split training data for validation
            X_train, X_val, y_train, y_val = train_test_split(
                X_train, y_train,
                test_size=self.config.validation_size,
                random_state=self.config.random_state,
                stratify=y_train
            )
            
            # Train model
            self.model = RandomForestClassifier(
                n_estimators=self.config.n_estimators,
                max_depth=self.config.max_depth,
                min_samples_split=self.config.min_samples_split,
                min_samples_leaf=self.config.min_samples_leaf,
                max_features=self.config.max_features,
                bootstrap=self.config.bootstrap,
                random_state=self.config.random_state,
                n_jobs=-1,
                class_weight='balanced'  # Handle class imbalance
            )
            
            self.model.fit(X_train, y_train)
            
            # Evaluate model
            training_results = self._evaluate_model(X_train, X_val, X_test, y_train, y_val, y_test)
            
            # Calculate feature importance
            self._calculate_feature_importance()
            
            # Cross-validation
            cv_scores = cross_val_score(
                self.model, X_train, y_train, 
                cv=self.config.cross_validation_folds,
                scoring='accuracy',
                n_jobs=-1
            )
            
            training_results['cv_mean_accuracy'] = cv_scores.mean()
            training_results['cv_std_accuracy'] = cv_scores.std()
            
            # Store training history
            self.training_history = training_results
            
            # Save model
            self.save_model()
            
            self.logger.info(f"Training completed. Accuracy: {training_results['test_accuracy']:.4f}")
            
            return training_results
            
        except Exception as e:
            self.logger.error(f"Error training Random Forest model: {e}")
            raise
    
    def _evaluate_model(self, X_train: np.ndarray, X_val: np.ndarray, X_test: np.ndarray,
                       y_train: np.ndarray, y_val: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        """Comprehensive model evaluation"""
        try:
            # Predictions
            y_train_pred = self.model.predict(X_train)
            y_val_pred = self.model.predict(X_val)
            y_test_pred = self.model.predict(X_test)
            
            # Probabilities
            y_test_prob = self.model.predict_proba(X_test)
            
            # Metrics
            results = {
                'train_accuracy': accuracy_score(y_train, y_train_pred),
                'val_accuracy': accuracy_score(y_val, y_val_pred),
                'test_accuracy': accuracy_score(y_test, y_test_pred),
                'train_precision': precision_score(y_train, y_train_pred, average='weighted'),
                'val_precision': precision_score(y_val, y_val_pred, average='weighted'),
                'test_precision': precision_score(y_test, y_test_pred, average='weighted'),
                'train_recall': recall_score(y_train, y_train_pred, average='weighted'),
                'val_recall': recall_score(y_val, y_val_pred, average='weighted'),
                'test_recall': recall_score(y_test, y_test_pred, average='weighted'),
                'train_f1': f1_score(y_train, y_train_pred, average='weighted'),
                'val_f1': f1_score(y_val, y_val_pred, average='weighted'),
                'test_f1': f1_score(y_test, y_test_pred, average='weighted'),
                'feature_count': X_train.shape[1],
                'training_samples': X_train.shape[0],
                'validation_samples': X_val.shape[0],
                'test_samples': X_test.shape[0]
            }
            
            # Classification report
            results['classification_report'] = classification_report(
                y_test, y_test_pred, 
                target_names=[TradingSignal.get_signal_name(i) for i in range(5)],
                output_dict=True
            )
            
            # Confusion matrix
            results['confusion_matrix'] = confusion_matrix(y_test, y_test_pred).tolist()
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error evaluating model: {e}")
            return {}
    
    def _calculate_feature_importance(self):
        """Calculate and store feature importance"""
        try:
            if self.model is None or not self.selected_features:
                return
            
            # Get feature importance from the model
            importance_scores = self.model.feature_importances_
            
            # Create feature importance dictionary
            self.feature_importance = dict(zip(self.selected_features, importance_scores))
            
            # Sort by importance
            self.feature_importance = dict(sorted(
                self.feature_importance.items(), 
                key=lambda x: x[1], 
                reverse=True
            ))
            
            self.logger.info(f"Calculated feature importance for {len(self.feature_importance)} features")
            
        except Exception as e:
            self.logger.error(f"Error calculating feature importance: {e}")
    
    def predict(self, data: pd.DataFrame, return_probabilities: bool = True) -> Union[RandomForestPrediction, int]:
        """Make prediction with comprehensive metadata"""
        try:
            if self.model is None:
                raise ValueError("Model not trained or loaded")
            
            # Engineer features for input data
            featured_data = self.feature_engineer.engineer_comprehensive_features(data)
            
            # Select the same features used in training
            if self.selected_features:
                X_data = featured_data[self.selected_features]
            else:
                feature_cols = [col for col in featured_data.columns 
                               if col not in ['close', 'open', 'high', 'low', 'volume']]
                X_data = featured_data[feature_cols]
            
            # Scale features
            X_scaled = self.scaler.transform(X_data.tail(1))
            
            # Make prediction
            prediction = self.model.predict(X_scaled)[0]
            probabilities = self.model.predict_proba(X_scaled)[0]
            
            if not return_probabilities:
                return prediction
            
            # Calculate confidence (max probability)
            confidence = float(np.max(probabilities))
            
            # Create probability dictionary
            prob_dict = {
                TradingSignal.get_signal_name(i): float(prob) 
                for i, prob in enumerate(probabilities)
            }
            
            # Calculate feature contributions (simplified)
            feature_contributions = self._calculate_feature_contributions(X_scaled[0])
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(probabilities, confidence)
            
            # Create prediction object
            rf_prediction = RandomForestPrediction(
                signal=int(prediction),
                signal_name=TradingSignal.get_signal_name(prediction),
                confidence=confidence,
                probabilities=prob_dict,
                feature_contributions=feature_contributions,
                model_version=self.model_version,
                prediction_time=datetime.utcnow(),
                input_features=dict(zip(self.selected_features, X_scaled[0])),
                risk_score=risk_score
            )
            
            return rf_prediction
            
        except Exception as e:
            self.logger.error(f"Error making prediction: {e}")
            raise
    
    def _calculate_feature_contributions(self, feature_values: np.ndarray) -> Dict[str, float]:
        """Calculate feature contributions to prediction (simplified)"""
        try:
            if not self.feature_importance or len(feature_values) != len(self.selected_features):
                return {}
            
            # Normalize feature values
            normalized_values = np.abs(feature_values) / (np.abs(feature_values).sum() + 1e-8)
            
            # Weight by feature importance
            contributions = {}
            for i, feature_name in enumerate(self.selected_features):
                importance = self.feature_importance.get(feature_name, 0)
                contribution = normalized_values[i] * importance
                contributions[feature_name] = float(contribution)
            
            # Sort by contribution
            contributions = dict(sorted(contributions.items(), key=lambda x: x[1], reverse=True))
            
            return dict(list(contributions.items())[:10])  # Top 10 contributions
            
        except Exception as e:
            self.logger.error(f"Error calculating feature contributions: {e}")
            return {}
    
    def _calculate_risk_score(self, probabilities: np.ndarray, confidence: float) -> float:
        """Calculate risk score based on prediction uncertainty"""
        try:
            # Calculate entropy (uncertainty)
            entropy = -np.sum(probabilities * np.log(probabilities + 1e-8))
            max_entropy = np.log(len(probabilities))  # Maximum possible entropy
            
            # Normalize entropy to [0, 1]
            normalized_entropy = entropy / max_entropy
            
            # Risk score: higher entropy and lower confidence = higher risk
            risk_score = (normalized_entropy + (1 - confidence)) / 2
            
            return float(risk_score)
            
        except Exception as e:
            self.logger.error(f"Error calculating risk score: {e}")
            return 0.5
    
    def optimize_hyperparameters(self, data: pd.DataFrame, n_trials: int = 100) -> Dict[str, Any]:
        """Optimize hyperparameters using Optuna"""
        try:
            self.logger.info(f"Starting hyperparameter optimization with {n_trials} trials...")
            
            # Prepare data for optimization
            X, y = self.prepare_training_data(data)
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=self.config.random_state, stratify=y
            )
            
            def objective(trial):
                # Suggest hyperparameters
                n_estimators = trial.suggest_int('n_estimators', 50, 500, step=50)
                max_depth = trial.suggest_int('max_depth', 3, 30)
                min_samples_split = trial.suggest_int('min_samples_split', 2, 20)
                min_samples_leaf = trial.suggest_int('min_samples_leaf', 1, 10)
                max_features = trial.suggest_categorical('max_features', ['sqrt', 'log2', 0.3, 0.5, 0.7])
                
                # Create temporary model
                temp_model = RandomForestClassifier(
                    n_estimators=n_estimators,
                    max_depth=max_depth,
                    min_samples_split=min_samples_split,
                    min_samples_leaf=min_samples_leaf,
                    max_features=max_features,
                    random_state=self.config.random_state,
                    n_jobs=-1,
                    class_weight='balanced'
                )
                
                try:
                    # Cross-validation score
                    cv_scores = cross_val_score(
                        temp_model, X_train, y_train,
                        cv=3, scoring='accuracy', n_jobs=-1
                    )
                    return cv_scores.mean()
                except:
                    return 0.0
            
            # Create study and optimize
            study = optuna.create_study(direction='maximize')
            study.optimize(objective, n_trials=n_trials)
            
            # Update config with best parameters
            best_params = study.best_params
            self.config.n_estimators = best_params['n_estimators']
            self.config.max_depth = best_params['max_depth']
            self.config.min_samples_split = best_params['min_samples_split']
            self.config.min_samples_leaf = best_params['min_samples_leaf']
            self.config.max_features = best_params['max_features']
            
            optimization_results = {
                'best_accuracy': study.best_value,
                'best_params': best_params,
                'n_trials': len(study.trials),
                'optimization_history': [(trial.number, trial.value) for trial in study.trials]
            }
            
            self.logger.info(f"Hyperparameter optimization completed. Best accuracy: {study.best_value:.4f}")
            
            return optimization_results
            
        except Exception as e:
            self.logger.error(f"Error in hyperparameter optimization: {e}")
            raise
    
    def save_model(self, filepath: Optional[str] = None):
        """Save the complete model with metadata"""
        try:
            if self.model is None:
                raise ValueError("No model to save")
            
            if filepath is None:
                filepath = str(Path(self.config.model_save_path) / f'random_forest_model_{self.model_version}.pkl')
            
            # Prepare complete model package
            model_package = {
                'model': self.model,
                'config': self.config,
                'scaler': self.scaler,
                'feature_engineer': self.feature_engineer,
                'selected_features': self.selected_features,
                'feature_importance': self.feature_importance,
                'model_version': self.model_version,
                'training_history': self.training_history
            }
            
            # Save using joblib for sklearn models
            joblib.dump(model_package, filepath)
            
            self.logger.info(f"Model saved to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error saving model: {e}")
            raise
    
    def load_model(self, filepath: str):
        """Load the complete model with metadata"""
        try:
            # Load model package
            model_package = joblib.load(filepath)
            
            # Restore attributes
            self.model = model_package['model']
            self.config = model_package['config']
            self.scaler = model_package['scaler']
            self.feature_engineer = model_package['feature_engineer']
            self.selected_features = model_package['selected_features']
            self.feature_importance = model_package['feature_importance']
            self.model_version = model_package['model_version']
            self.training_history = model_package['training_history']
            
            self.logger.info(f"Model loaded from {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
            raise
    
    def get_feature_analysis(self) -> Dict[str, Any]:
        """Get comprehensive feature analysis"""
        try:
            if not self.feature_importance:
                return {'status': 'No feature importance available'}
            
            # Top features by importance
            top_features = dict(list(self.feature_importance.items())[:20])
            
            # Feature groups analysis
            group_importance = {}
            for group_name, features in self.feature_engineer.feature_groups.items():
                group_score = sum(self.feature_importance.get(f, 0) for f in features)
                group_importance[group_name] = group_score
            
            # Sort groups by importance
            group_importance = dict(sorted(group_importance.items(), key=lambda x: x[1], reverse=True))
            
            analysis = {
                'total_features': len(self.selected_features),
                'top_20_features': top_features,
                'feature_groups_importance': group_importance,
                'feature_selection_method': self.config.feature_selection_method,
                'feature_engineering_config': {
                    'use_technical_indicators': self.config.use_technical_indicators,
                    'use_price_patterns': self.config.use_price_patterns,
                    'use_volume_features': self.config.use_volume_features,
                    'use_volatility_features': self.config.use_volatility_features,
                    'use_momentum_features': self.config.use_momentum_features,
                    'use_trend_features': self.config.use_trend_features
                }
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error getting feature analysis: {e}")
            return {'error': str(e)}
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get comprehensive model information"""
        try:
            if self.model is None:
                return {'status': 'No model loaded'}
            
            info = {
                'model_version': self.model_version,
                'model_type': 'Random Forest Classifier',
                'architecture': {
                    'n_estimators': self.config.n_estimators,
                    'max_depth': self.config.max_depth,
                    'min_samples_split': self.config.min_samples_split,
                    'min_samples_leaf': self.config.min_samples_leaf,
                    'max_features': self.config.max_features,
                    'feature_count': len(self.selected_features)
                },
                'training_config': {
                    'prediction_horizon': self.config.prediction_horizon,
                    'strong_signal_threshold': self.config.strong_signal_threshold,
                    'weak_signal_threshold': self.config.weak_signal_threshold,
                    'feature_selection_method': self.config.feature_selection_method,
                    'max_features_selected': self.config.max_features_selected
                },
                'signal_classes': {
                    0: 'STRONG_SELL',
                    1: 'SELL',
                    2: 'HOLD',
                    3: 'BUY',
                    4: 'STRONG_BUY'
                }
            }
            
            if self.training_history:
                info['performance'] = {
                    'test_accuracy': self.training_history.get('test_accuracy', 0),
                    'test_precision': self.training_history.get('test_precision', 0),
                    'test_recall': self.training_history.get('test_recall', 0),
                    'test_f1': self.training_history.get('test_f1', 0),
                    'cv_mean_accuracy': self.training_history.get('cv_mean_accuracy', 0),
                    'cv_std_accuracy': self.training_history.get('cv_std_accuracy', 0)
                }
                
                if 'classification_report' in self.training_history:
                    info['class_performance'] = self.training_history['classification_report']
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting model info: {e}")
            return {'error': str(e)}

# Usage Example and Testing
def example_usage():
    """Comprehensive example of using the Enhanced Random Forest Model"""
    
    print("=== Enhanced Random Forest Model Example ===")
    
    # Create configuration
    config = RandomForestConfig(
        n_estimators=200,
        max_depth=20,
        prediction_horizon=5,
        use_technical_indicators=True,
        use_price_patterns=True,
        use_volume_features=True,
        use_volatility_features=True,
        use_momentum_features=True,
        use_trend_features=True,
        feature_selection_method='importance',
        max_features_selected=50
    )
    
    # Create model
    rf_model = EnhancedRandomForestModel(config)
    
    # Generate sample data (in real usage, this would come from your data source)
    dates = pd.date_range('2020-01-01', periods=2000, freq='H')
    np.random.seed(42)
    
    # Generate realistic OHLCV data with trends and patterns
    price_base = 100
    trend = np.linspace(0, 0.5, 2000)  # Upward trend
    noise = np.random.normal(0, 0.02, 2000)
    cyclical = 0.1 * np.sin(np.linspace(0, 20*np.pi, 2000))  # Cyclical pattern
    
    returns = trend + noise + cyclical
    prices = price_base * (1 + returns).cumprod()
    
    # Generate OHLC from prices
    high_prices = prices * (1 + np.abs(np.random.normal(0, 0.01, 2000)))
    low_prices = prices * (1 - np.abs(np.random.normal(0, 0.01, 2000)))
    open_prices = np.roll(prices, 1)
    open_prices[0] = prices[0]
    
    volumes = np.random.lognormal(10, 0.8, 2000)
    
    sample_data = pd.DataFrame({
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': prices,
        'volume': volumes
    }, index=dates)
    
    print(f"Sample data shape: {sample_data.shape}")
    print(f"Sample data head:\n{sample_data.head()}")
    
    try:
        # Train model
        print("\n1. Training Random Forest Model...")
        training_results = rf_model.train(sample_data)
        print("Training Results:")
        for key, value in training_results.items():
            if key not in ['classification_report', 'confusion_matrix']:
                print(f"   {key}: {value}")
        
        # Show classification report
        if 'classification_report' in training_results:
            print("\n2. Classification Report:")
            for class_name, metrics in training_results['classification_report'].items():
                if isinstance(metrics, dict):
                    print(f"   {class_name}: Precision={metrics.get('precision', 0):.3f}, "
                          f"Recall={metrics.get('recall', 0):.3f}, F1={metrics.get('f1-score', 0):.3f}")
        
        # Make predictions
        print("\n3. Making Predictions...")
        prediction = rf_model.predict(sample_data.tail(100))
        print(f"Prediction: {prediction.signal_name}")
        print(f"Confidence: {prediction.confidence:.4f}")
        print(f"Risk Score: {prediction.risk_score:.4f}")
        
        # Show probabilities
        print("\n4. Class Probabilities:")
        for signal_name, prob in prediction.probabilities.items():
            print(f"   {signal_name}: {prob:.4f}")
        
        # Show top feature contributions
        print("\n5. Top 10 Feature Contributions:")
        for feature, contribution in list(prediction.feature_contributions.items())[:10]:
            print(f"   {feature}: {contribution:.4f}")
        
        # Feature analysis
        print("\n6. Feature Analysis:")
        feature_analysis = rf_model.get_feature_analysis()
        print(f"   Total Features: {feature_analysis['total_features']}")
        print(f"   Feature Selection Method: {feature_analysis['feature_selection_method']}")
        
        print("\n7. Top 10 Most Important Features:")
        for feature, importance in list(feature_analysis['top_20_features'].items())[:10]:
            print(f"   {feature}: {importance:.4f}")
        
        print("\n8. Feature Group Importance:")
        for group, importance in feature_analysis['feature_groups_importance'].items():
            print(f"   {group}: {importance:.4f}")
        
        # Model information
        print("\n9. Model Information:")
        model_info = rf_model.get_model_info()
        print(f"   Model Type: {model_info['model_type']}")
        print(f"   N Estimators: {model_info['architecture']['n_estimators']}")
        print(f"   Max Depth: {model_info['architecture']['max_depth']}")
        print(f"   Feature Count: {model_info['architecture']['feature_count']}")
        
        if 'performance' in model_info:
            print(f"   Test Accuracy: {model_info['performance']['test_accuracy']:.4f}")
            print(f"   Test F1 Score: {model_info['performance']['test_f1']:.4f}")
            print(f"   CV Mean Accuracy: {model_info['performance']['cv_mean_accuracy']:.4f}")
        
        print("\n=== Random Forest Model Example Completed Successfully ===")
        return rf_model
        
    except Exception as e:
        print(f"Error in example: {e}")
        return None

if __name__ == "__main__":
    # Run the comprehensive example
    model = example_usage()
