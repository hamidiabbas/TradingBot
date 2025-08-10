"""
Enhanced Professional SVM Model for Market Regime Classification
==============================================================

A sophisticated Support Vector Machine implementation for market regime detection,
volatility classification, and trading environment analysis with advanced feature
engineering, kernel optimization, and real-time inference capabilities designed
for institutional-grade algorithmic trading systems.

Features:
- Multi-class Market Regime Detection (Trending, Ranging, Volatile, etc.)
- Advanced Kernel Selection and Optimization (RBF, Polynomial, Linear)
- Sophisticated Feature Engineering for Market Microstructure
- Real-time Regime Classification with Confidence Scoring
- Hyperparameter Optimization using Optuna and Grid Search
- Model Persistence and Versioning with Metadata
- Performance Monitoring and Drift Detection
- Professional Error Handling and Logging
- Integration with Trading Strategy Selection

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
from sklearn.svm import SVC, SVR
from sklearn.preprocessing import StandardScaler, RobustScaler, LabelEncoder, MinMaxScaler
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, StratifiedKFold
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score,
    precision_score, recall_score, f1_score, roc_auc_score,
    silhouette_score, adjusted_rand_score
)
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif, RFE
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
import optuna
import ta
import pandas_ta as pta
from scipy import stats
from scipy.signal import savgol_filter
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture

from utils.logger import setup_logging

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

class MarketRegime:
    """Market regime enumeration with detailed classifications"""
    STRONG_TRENDING_UP = 0
    TRENDING_UP = 1
    WEAK_TRENDING_UP = 2
    RANGING_BULLISH = 3
    RANGING_NEUTRAL = 4
    RANGING_BEARISH = 5
    WEAK_TRENDING_DOWN = 6
    TRENDING_DOWN = 7
    STRONG_TRENDING_DOWN = 8
    HIGH_VOLATILITY = 9
    LOW_VOLATILITY = 10
    BREAKOUT = 11
    REVERSAL = 12
    CONSOLIDATION = 13
    
    @classmethod
    def get_regime_name(cls, regime_value: int) -> str:
        """Get regime name from numeric value"""
        regime_map = {
            0: "STRONG_TRENDING_UP", 1: "TRENDING_UP", 2: "WEAK_TRENDING_UP",
            3: "RANGING_BULLISH", 4: "RANGING_NEUTRAL", 5: "RANGING_BEARISH",
            6: "WEAK_TRENDING_DOWN", 7: "TRENDING_DOWN", 8: "STRONG_TRENDING_DOWN",
            9: "HIGH_VOLATILITY", 10: "LOW_VOLATILITY", 11: "BREAKOUT",
            12: "REVERSAL", 13: "CONSOLIDATION"
        }
        return regime_map.get(regime_value, "UNKNOWN")
    
    @classmethod
    def get_regime_category(cls, regime_value: int) -> str:
        """Get general regime category"""
        if regime_value in [0, 1, 2]:
            return "BULLISH_TREND"
        elif regime_value in [6, 7, 8]:
            return "BEARISH_TREND"
        elif regime_value in [3, 4, 5, 13]:
            return "RANGING"
        elif regime_value in [9, 10]:
            return "VOLATILITY"
        elif regime_value in [11, 12]:
            return "TRANSITION"
        else:
            return "UNKNOWN"

@dataclass
class SVMConfig:
    """SVM model configuration with comprehensive parameters"""
    # Model architecture parameters
    kernel: str = 'rbf'  # 'linear', 'poly', 'rbf', 'sigmoid'
    C: float = 1.0
    gamma: str = 'scale'  # 'scale', 'auto', or float
    degree: int = 3  # For polynomial kernel
    coef0: float = 0.0  # For polynomial and sigmoid kernels
    
    # Classification parameters
    classification_type: str = 'regime'  # 'regime', 'volatility', 'trend_strength'
    n_classes: int = 14  # Number of market regimes
    multiclass_strategy: str = 'ovr'  # 'ovr' (one-vs-rest) or 'ovo' (one-vs-one)
    
    # Feature engineering parameters
    lookback_period: int = 50
    volatility_window: int = 20
    trend_window: int = 30
    use_technical_indicators: bool = True
    use_market_microstructure: bool = True
    use_volatility_features: bool = True
    use_momentum_features: bool = True
    use_regime_transition_features: bool = True
    
    # Feature selection parameters
    feature_selection_method: str = 'rfe'  # 'rfe', 'kbest', 'pca', 'none'
    max_features_selected: int = 30
    pca_variance_threshold: float = 0.95
    
    # Training parameters
    test_size: float = 0.2
    validation_size: float = 0.2
    cross_validation_folds: int = 5
    class_weight: str = 'balanced'  # 'balanced', None, or dict
    
    # Optimization parameters
    enable_hyperparameter_optimization: bool = True
    optimization_trials: int = 100
    optimization_timeout: int = 3600  # 1 hour
    
    # Model management
    model_save_path: str = "models/svm/"
    enable_ensemble: bool = True
    ensemble_voting: str = 'soft'  # 'hard' or 'soft'

@dataclass
class SVMPrediction:
    """SVM prediction result with comprehensive metadata"""
    regime: int
    regime_name: str
    regime_category: str
    confidence: float
    probabilities: Dict[str, float]
    decision_scores: Dict[str, float]
    feature_contributions: Dict[str, float]
    model_version: str
    prediction_time: datetime
    input_features: Dict[str, float]
    regime_stability: float
    transition_probability: float

class SVMFeatureEngineering:
    """Advanced feature engineering for SVM market regime classification"""
    
    def __init__(self, config: SVMConfig):
        self.config = config
        self.scaler = RobustScaler()
        self.feature_names = []
        self.feature_groups = {}
        self.regime_transitions = {}
        self.logger = setup_logging('INFO')
        
    def engineer_regime_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Engineer comprehensive features for market regime classification"""
        try:
            self.logger.info("Starting comprehensive feature engineering for SVM...")
            
            features_df = data.copy()
            original_columns = set(features_df.columns)
            
            # Basic market structure features
            features_df = self._add_market_structure_features(features_df)
            
            # Trend analysis features
            features_df = self._add_trend_analysis_features(features_df)
            
            # Volatility regime features
            features_df = self._add_volatility_regime_features(features_df)
            
            # Momentum and mean reversion features
            features_df = self._add_momentum_features(features_df)
            
            # Technical indicators for regime detection
            if self.config.use_technical_indicators:
                features_df = self._add_technical_indicators(features_df)
            
            # Market microstructure features
            if self.config.use_market_microstructure:
                features_df = self._add_microstructure_features(features_df)
            
            # Regime transition features
            if self.config.use_regime_transition_features:
                features_df = self._add_regime_transition_features(features_df)
            
            # Statistical features for regime detection
            features_df = self._add_statistical_regime_features(features_df)
            
            # Cross-sectional features
            features_df = self._add_cross_sectional_features(features_df)
            
            # Frequency domain features
            features_df = self._add_frequency_domain_features(features_df)
            
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
    
    def _add_market_structure_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add market structure analysis features"""
        try:
            close = data['close']
            high = data['high']
            low = data['low']
            
            # Trend strength using linear regression
            for window in [10, 20, 30]:
                trend_slope = close.rolling(window).apply(
                    lambda x: stats.linregress(range(len(x)), x)[0] if len(x) == window else np.nan
                )
                trend_r2 = close.rolling(window).apply(
                    lambda x: stats.linregress(range(len(x)), x)[2]**2 if len(x) == window else np.nan
                )
                data[f'trend_slope_{window}'] = trend_slope
                data[f'trend_strength_{window}'] = trend_r2
                data[f'trend_direction_{window}'] = np.sign(trend_slope)
            
            # Higher highs and lower lows detection
            for window in [5, 10, 20]:
                rolling_max = high.rolling(window).max()
                rolling_min = low.rolling(window).min()
                
                data[f'higher_highs_{window}'] = (high > rolling_max.shift(1)).astype(int)
                data[f'lower_lows_{window}'] = (low < rolling_min.shift(1)).astype(int)
                
                # Structure breaks
                data[f'structure_break_up_{window}'] = (
                    (close > rolling_max.shift(window)) & 
                    (close.shift(1) <= rolling_max.shift(window + 1))
                ).astype(int)
                
                data[f'structure_break_down_{window}'] = (
                    (close < rolling_min.shift(window)) & 
                    (close.shift(1) >= rolling_min.shift(window + 1))
                ).astype(int)
            
            # Market efficiency (price vs straight line)
            for window in [10, 20]:
                actual_path = close.diff().abs().rolling(window).sum()
                straight_line = abs(close - close.shift(window))
                data[f'market_efficiency_{window}'] = straight_line / actual_path
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error adding market structure features: {e}")
            return data
    
    def _add_trend_analysis_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add advanced trend analysis features"""
        try:
            close = data['close']
            
            # ADX-based trend strength
            adx = ta.trend.adx(data['high'], data['low'], close, window=14)
            adx_pos = ta.trend.adx_pos(data['high'], data['low'], close, window=14)
            adx_neg = ta.trend.adx_neg(data['high'], data['low'], close, window=14)
            
            data['adx'] = adx
            data['adx_pos'] = adx_pos
            data['adx_neg'] = adx_neg
            data['adx_trend_strength'] = adx / 50  # Normalize
            data['adx_directional_bias'] = (adx_pos - adx_neg) / (adx_pos + adx_neg + 1e-8)
            
            # Multiple timeframe trend alignment
            for fast, slow in [(5, 21), (10, 30), (20, 50)]:
                ema_fast = ta.trend.ema_indicator(close, window=fast)
                ema_slow = ta.trend.ema_indicator(close, window=slow)
                
                data[f'ema_alignment_{fast}_{slow}'] = (ema_fast > ema_slow).astype(int)
                data[f'ema_distance_{fast}_{slow}'] = (ema_fast - ema_slow) / ema_slow
                
                # EMA slope
                data[f'ema_slope_{fast}'] = ema_fast.diff(5) / ema_fast.shift(5)
                data[f'ema_slope_{slow}'] = ema_slow.diff(5) / ema_slow.shift(5)
            
            # Parabolic SAR analysis
            psar = ta.trend.psar_down(data['high'], data['low'], close)
            data['psar'] = psar
            data['psar_trend'] = (close > psar).astype(int)
            data['psar_distance'] = abs(close - psar) / close
            
            # Trend consistency
            for window in [10, 20]:
                price_changes = close.diff().rolling(window)
                data[f'trend_consistency_{window}'] = (
                    price_changes.apply(lambda x: (x > 0).sum() / len(x))
                )
                
                # Trend persistence
                returns = close.pct_change()
                data[f'trend_persistence_{window}'] = returns.rolling(window).apply(
                    lambda x: x.autocorr() if len(x.dropna()) > 5 else 0
                )
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error adding trend analysis features: {e}")
            return data
    
    def _add_volatility_regime_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add volatility regime classification features"""
        try:
            close = data['close']
            high = data['high']
            low = data['low']
            
            # Multiple volatility measures
            returns = close.pct_change()
            
            # Historical volatility with different windows
            for window in [5, 10, 20, 30]:
                vol = returns.rolling(window).std() * np.sqrt(252)
                data[f'volatility_{window}'] = vol
                
                # Volatility percentile
                data[f'vol_percentile_{window}'] = vol.rolling(252).rank(pct=True)
                
                # Volatility regime (relative to historical)
                vol_median = vol.rolling(100).median()
                vol_75th = vol.rolling(100).quantile(0.75)
                vol_25th = vol.rolling(100).quantile(0.25)
                
                data[f'vol_regime_{window}'] = pd.cut(
                    vol, 
                    bins=[0, vol_25th, vol_75th, float('inf')],
                    labels=[0, 1, 2]  # Low, Medium, High
                ).astype(float)
            
            # Parkinson volatility estimator
            parkinson_vol = np.sqrt(
                (1/(4*np.log(2))) * (np.log(high/low)**2)
            ).rolling(20).mean()
            data['parkinson_volatility'] = parkinson_vol
            
            # Garman-Klass volatility estimator
            gk_vol = np.sqrt(
                0.5 * (np.log(high/low)**2) - 
                (2*np.log(2)-1) * (np.log(close/data['open'])**2)
            ).rolling(20).mean()
            data['gk_volatility'] = gk_vol
            
            # GARCH-like volatility clustering
            data['vol_clustering'] = returns.abs().rolling(10).mean()
            
            # Volatility-of-volatility
            for window in [10, 20]:
                vol_base = returns.rolling(window).std()
                data[f'vol_of_vol_{window}'] = vol_base.rolling(window).std()
            
            # Volatility skewness and kurtosis
            for window in [30, 50]:
                vol_returns = returns.rolling(window)
                data[f'vol_skewness_{window}'] = vol_returns.skew()
                data[f'vol_kurtosis_{window}'] = vol_returns.kurt()
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error adding volatility regime features: {e}")
            return data
    
    def _add_momentum_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add momentum and mean reversion features"""
        try:
            close = data['close']
            
            # RSI with multiple periods
            for period in [7, 14, 21]:
                rsi = ta.momentum.rsi(close, window=period)
                data[f'rsi_{period}'] = rsi
                data[f'rsi_regime_{period}'] = pd.cut(
                    rsi, bins=[0, 30, 70, 100], labels=[0, 1, 2]
                ).astype(float)
                
                # RSI divergence approximation
                rsi_slope = rsi.diff(5)
                price_slope = close.diff(5)
                data[f'rsi_divergence_{period}'] = np.sign(rsi_slope) != np.sign(price_slope)
            
            # Stochastic oscillator regimes
            stoch_k = ta.momentum.stoch(data['high'], data['low'], close)
            stoch_d = ta.momentum.stoch_signal(data['high'], data['low'], close)
            
            data['stoch_k'] = stoch_k
            data['stoch_d'] = stoch_d
            data['stoch_regime'] = pd.cut(
                stoch_k, bins=[0, 20, 80, 100], labels=[0, 1, 2]
            ).astype(float)
            
            # Williams %R
            williams_r = ta.momentum.williams_r(data['high'], data['low'], close)
            data['williams_r'] = williams_r
            data['williams_regime'] = pd.cut(
                williams_r, bins=[-100, -80, -20, 0], labels=[0, 1, 2]
            ).astype(float)
            
            # CCI (Commodity Channel Index)
            cci = ta.trend.cci(data['high'], data['low'], close)
            data['cci'] = cci
            data['cci_regime'] = pd.cut(
                cci, bins=[-float('inf'), -100, 100, float('inf')], labels=[0, 1, 2]
            ).astype(float)
            
            # Rate of Change with multiple periods
            for period in [5, 10, 20]:
                roc = ta.momentum.roc(close, window=period)
                data[f'roc_{period}'] = roc
                
                # ROC regime
                roc_std = roc.rolling(50).std()
                data[f'roc_regime_{period}'] = pd.cut(
                    roc, bins=[-float('inf'), -roc_std, roc_std, float('inf')], 
                    labels=[0, 1, 2]
                ).astype(float)
            
            # Money Flow Index (if volume available)
            if 'volume' in data.columns:
                mfi = ta.volume.money_flow_index(data['high'], data['low'], close, data['volume'])
                data['mfi'] = mfi
                data['mfi_regime'] = pd.cut(
                    mfi, bins=[0, 20, 80, 100], labels=[0, 1, 2]
                ).astype(float)
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error adding momentum features: {e}")
            return data
    
    def _add_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators for regime detection"""
        try:
            close = data['close']
            high = data['high']
            low = data['low']
            
            # Bollinger Bands regime analysis
            for period in [20, 30]:
                bb_upper = ta.volatility.bollinger_hband(close, window=period)
                bb_lower = ta.volatility.bollinger_lband(close, window=period)
                bb_middle = ta.volatility.bollinger_mavg(close, window=period)
                
                data[f'bb_position_{period}'] = (close - bb_lower) / (bb_upper - bb_lower)
                data[f'bb_width_{period}'] = (bb_upper - bb_lower) / bb_middle
                data[f'bb_regime_{period}'] = pd.cut(
                    data[f'bb_position_{period}'], 
                    bins=[0, 0.2, 0.8, 1.0], labels=[0, 1, 2]
                ).astype(float)
                
                # Bollinger Band squeeze detection
                bb_width_ma = data[f'bb_width_{period}'].rolling(20).mean()
                data[f'bb_squeeze_{period}'] = (
                    data[f'bb_width_{period}'] < bb_width_ma * 0.8
                ).astype(int)
            
            # Keltner Channels
            keltner_upper = ta.volatility.keltner_channel_hband(high, low, close)
            keltner_lower = ta.volatility.keltner_channel_lband(high, low, close)
            
            data['keltner_position'] = (close - keltner_lower) / (keltner_upper - keltner_lower)
            data['keltner_regime'] = pd.cut(
                data['keltner_position'], 
                bins=[0, 0.2, 0.8, 1.0], labels=[0, 1, 2]
            ).astype(float)
            
            # Donchian Channels
            for period in [20, 30]:
                donchian_upper = high.rolling(period).max()
                donchian_lower = low.rolling(period).min()
                
                data[f'donchian_position_{period}'] = (
                    (close - donchian_lower) / (donchian_upper - donchian_lower)
                )
                
                # Breakout detection
                data[f'donchian_breakout_up_{period}'] = (close == donchian_upper).astype(int)
                data[f'donchian_breakout_down_{period}'] = (close == donchian_lower).astype(int)
            
            # Aroon indicator for trend identification
            aroon_up = ta.trend.aroon_up(high, low, window=14)
            aroon_down = ta.trend.aroon_down(high, low, window=14)
            
            data['aroon_up'] = aroon_up
            data['aroon_down'] = aroon_down
            data['aroon_oscillator'] = aroon_up - aroon_down
            data['aroon_regime'] = pd.cut(
                data['aroon_oscillator'], 
                bins=[-100, -20, 20, 100], labels=[0, 1, 2]
            ).astype(float)
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error adding technical indicators: {e}")
            return data
    
    def _add_microstructure_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add market microstructure features"""
        try:
            close = data['close']
            high = data['high']
            low = data['low']
            open_price = data['open']
            
            # Intraday patterns
            data['range_ratio'] = (high - low) / close
            data['body_ratio'] = abs(close - open_price) / (high - low + 1e-8)
            
            # Wick analysis
            upper_wick = high - np.maximum(close, open_price)
            lower_wick = np.minimum(close, open_price) - low
            total_range = high - low
            
            data['upper_wick_ratio'] = upper_wick / (total_range + 1e-8)
            data['lower_wick_ratio'] = lower_wick / (total_range + 1e-8)
            data['wick_balance'] = (upper_wick - lower_wick) / (total_range + 1e-8)
            
            # Gap analysis
            data['gap'] = (open_price - close.shift(1)) / close.shift(1)
            data['gap_filled'] = (
                (data['gap'] > 0) & (low <= close.shift(1))
            ).astype(int)
            
            # Price action efficiency
            for window in [5, 10]:
                price_change = abs(close - close.shift(window))
                path_length = abs(close.diff()).rolling(window).sum()
                data[f'efficiency_{window}'] = price_change / path_length
            
            # Order flow approximation
            if 'volume' in data.columns:
                volume = data['volume']
                
                # Accumulation/Distribution approximation
                clv = ((close - low) - (high - close)) / (high - low + 1e-8)
                data['clv'] = clv
                data['ad_approx'] = (clv * volume).cumsum()
                
                # Volume-price trend
                data['vpt'] = ((close.diff() / close.shift(1)) * volume).cumsum()
                
                # Ease of Movement
                distance_moved = (high + low) / 2 - (high.shift(1) + low.shift(1)) / 2
                box_height = volume / (high - low + 1e-8)
                data['ease_of_movement'] = distance_moved / box_height
                
                # Force Index
                data['force_index'] = volume * close.diff()
                
                # Buying/Selling pressure
                data['buying_pressure'] = (close - low) / (high - low + 1e-8)
                data['selling_pressure'] = (high - close) / (high - low + 1e-8)
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error adding microstructure features: {e}")
            return data
    
    def _add_regime_transition_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add regime transition probability features"""
        try:
            close = data['close']
            
            # Regime change indicators
            for window in [10, 20]:
                # Variance change detection
                returns = close.pct_change()
                vol_current = returns.rolling(window).std()
                vol_previous = returns.rolling(window).std().shift(window)
                
                data[f'regime_change_vol_{window}'] = (
                    abs(vol_current - vol_previous) / vol_previous
                )
                
                # Mean change detection
                mean_current = returns.rolling(window).mean()
                mean_previous = returns.rolling(window).mean().shift(window)
                
                data[f'regime_change_mean_{window}'] = (
                    abs(mean_current - mean_previous) / abs(mean_previous + 1e-8)
                )
            
            # Structural break detection using CUSUM
            returns = close.pct_change().fillna(0)
            cumsum_pos = np.maximum(0, (returns - returns.mean()).cumsum())
            cumsum_neg = np.minimum(0, (returns - returns.mean()).cumsum())
            
            data['cusum_pos'] = cumsum_pos
            data['cusum_neg'] = abs(cumsum_neg)
            data['cusum_regime_signal'] = (
                (cumsum_pos > 2 * returns.std()) | 
                (abs(cumsum_neg) > 2 * returns.std())
            ).astype(int)
            
            # Market phase detection
            # Using Hilbert Transform for cycle analysis
            try:
                from scipy.signal import hilbert
                analytic_signal = hilbert(returns.fillna(0))
                amplitude_envelope = np.abs(analytic_signal)
                instantaneous_phase = np.unwrap(np.angle(analytic_signal))
                
                data['cycle_amplitude'] = amplitude_envelope
                data['cycle_phase'] = instantaneous_phase
                data['cycle_frequency'] = np.gradient(instantaneous_phase)
            except:
                # Fallback if scipy.signal.hilbert is not available
                data['cycle_amplitude'] = returns.rolling(20).std()
                data['cycle_phase'] = 0
                data['cycle_frequency'] = 0
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error adding regime transition features: {e}")
            return data
    
    def _add_statistical_regime_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add statistical features for regime detection"""
        try:
            close = data['close']
            returns = close.pct_change()
            
            # Rolling statistical moments
            for window in [20, 30, 50]:
                # Mean and standard deviation
                data[f'returns_mean_{window}'] = returns.rolling(window).mean()
                data[f'returns_std_{window}'] = returns.rolling(window).std()
                
                # Skewness and kurtosis
                data[f'returns_skew_{window}'] = returns.rolling(window).skew()
                data[f'returns_kurt_{window}'] = returns.rolling(window).kurt()
                
                # Jarque-Bera test statistic (normality test)
                def jarque_bera_stat(x):
                    if len(x) < 10:
                        return 0
                    n = len(x)
                    s = stats.skew(x)
                    k = stats.kurtosis(x)
                    jb = n/6 * (s**2 + 1/4*(k**2))
                    return jb
                
                data[f'jarque_bera_{window}'] = returns.rolling(window).apply(jarque_bera_stat)
                
                # Ljung-Box test statistic (autocorrelation test)
                def ljung_box_stat(x):
                    try:
                        if len(x) < 10:
                            return 0
                        # Simplified Ljung-Box statistic
                        autocorr = [x.autocorr(lag=i) for i in range(1, min(6, len(x)//4)) if not pd.isna(x.autocorr(lag=i))]
                        if not autocorr:
                            return 0
                        return sum([ac**2 for ac in autocorr]) * len(x)
                    except:
                        return 0
                
                data[f'ljung_box_{window}'] = returns.rolling(window).apply(ljung_box_stat)
            
            # Z-score for regime detection
            for window in [20, 50]:
                mean = returns.rolling(window).mean()
                std = returns.rolling(window).std()
                data[f'z_score_{window}'] = (returns - mean) / (std + 1e-8)
                
                # Regime based on Z-score
                data[f'z_regime_{window}'] = pd.cut(
                    data[f'z_score_{window}'], 
                    bins=[-float('inf'), -2, 2, float('inf')], 
                    labels=[0, 1, 2]
                ).astype(float)
            
            # Hurst exponent approximation for trend persistence
            def hurst_exponent(ts, max_lag=20):
                try:
                    if len(ts) < max_lag * 2:
                        return 0.5
                    
                    lags = range(2, max_lag)
                    tau = [np.sqrt(np.std(np.subtract(ts[lag:], ts[:-lag]))) for lag in lags]
                    poly = np.polyfit(np.log(lags), np.log(tau), 1)
                    return poly[0] * 2.0
                except:
                    return 0.5
            
            data['hurst_exponent'] = close.rolling(100).apply(
                lambda x: hurst_exponent(x.values) if len(x) >= 50 else 0.5
            )
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error adding statistical regime features: {e}")
            return data
    
    def _add_cross_sectional_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add cross-sectional analysis features"""
        try:
            close = data['close']
            
            # Relative strength (assuming we have a benchmark)
            # This would typically be implemented with multiple assets
            # For now, we'll use internal relative strength measures
            
            # Price momentum vs volatility regime
            returns = close.pct_change()
            for window in [10, 20]:
                momentum = returns.rolling(window).mean()
                volatility = returns.rolling(window).std()
                
                data[f'momentum_vol_ratio_{window}'] = momentum / (volatility + 1e-8)
                
                # Risk-adjusted momentum
                data[f'sharpe_ratio_{window}'] = momentum / (volatility + 1e-8) * np.sqrt(252)
            
            # Regime persistence
            for window in [5, 10]:
                trend_direction = np.sign(close.diff())
                data[f'trend_persistence_{window}'] = trend_direction.rolling(window).mean()
                
                # Regime stability
                regime_changes = (trend_direction != trend_direction.shift(1)).astype(int)
                data[f'regime_stability_{window}'] = 1 - regime_changes.rolling(window).mean()
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error adding cross-sectional features: {e}")
            return data
    
    def _add_frequency_domain_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add frequency domain analysis features"""
        try:
            close = data['close']
            returns = close.pct_change().fillna(0)
            
            # Spectral analysis features
            try:
                # FFT-based features
                window_size = 64
                if len(returns) >= window_size:
                    # Rolling spectral features
                    def spectral_features(x):
                        try:
                            if len(x) < window_size:
                                return pd.Series([0, 0, 0, 0])
                            
                            fft = np.fft.fft(x.values)
                            power_spectrum = np.abs(fft)**2
                            
                            # Spectral centroid (frequency center of mass)
                            freqs = np.fft.fftfreq(len(x))
                            spectral_centroid = np.sum(freqs * power_spectrum) / np.sum(power_spectrum)
                            
                            # Spectral bandwidth
                            spectral_bandwidth = np.sqrt(
                                np.sum(((freqs - spectral_centroid)**2) * power_spectrum) / 
                                np.sum(power_spectrum)
                            )
                            
                            # Spectral rolloff (frequency below which 85% of energy is contained)
                            cumsum_power = np.cumsum(power_spectrum)
                            rolloff_idx = np.where(cumsum_power >= 0.85 * cumsum_power[-1])[0]
                            spectral_rolloff = freqs[rolloff_idx[0]] if len(rolloff_idx) > 0 else 0
                            
                            # Spectral contrast (difference between peaks and valleys)
                            spectral_contrast = np.max(power_spectrum) / (np.mean(power_spectrum) + 1e-8)
                            
                            return pd.Series([spectral_centroid, spectral_bandwidth, 
                                            spectral_rolloff, spectral_contrast])
                        except:
                            return pd.Series([0, 0, 0, 0])
                    
                    spectral_df = returns.rolling(window_size).apply(
                        spectral_features, raw=False
                    )
                    
                    if len(spectral_df.columns) >= 4:
                        data['spectral_centroid'] = spectral_df.iloc[:, 0]
                        data['spectral_bandwidth'] = spectral_df.iloc[:, 1]
                        data['spectral_rolloff'] = spectral_df.iloc[:, 2]
                        data['spectral_contrast'] = spectral_df.iloc[:, 3]
                    else:
                        data['spectral_centroid'] = 0
                        data['spectral_bandwidth'] = 0
                        data['spectral_rolloff'] = 0
                        data['spectral_contrast'] = 0
                
            except Exception as e:
                self.logger.warning(f"Could not compute spectral features: {e}")
                data['spectral_centroid'] = 0
                data['spectral_bandwidth'] = 0
                data['spectral_rolloff'] = 0
                data['spectral_contrast'] = 0
            
            # Wavelet-like features using rolling windows
            for window in [8, 16, 32]:
                # High frequency component (short-term variations)
                high_freq = returns - returns.rolling(window).mean()
                data[f'high_freq_energy_{window}'] = high_freq.rolling(window).apply(
                    lambda x: np.sum(x**2)
                )
                
                # Low frequency component (trend)
                low_freq = returns.rolling(window).mean()
                data[f'low_freq_energy_{window}'] = low_freq.rolling(window).apply(
                    lambda x: np.sum(x**2)
                )
                
                # Frequency ratio
                data[f'freq_ratio_{window}'] = (
                    data[f'high_freq_energy_{window}'] / 
                    (data[f'low_freq_energy_{window}'] + 1e-8)
                )
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error adding frequency domain features: {e}")
            return data
    
    def _clean_and_prepare_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare data for SVM training"""
        try:
            # Handle infinite values
            data = data.replace([np.inf, -np.inf], np.nan)
            
            # Forward fill then backward fill
            data = data.fillna(method='ffill').fillna(method='bfill')
            
            # Fill remaining NaN with appropriate values
            numeric_columns = data.select_dtypes(include=[np.number]).columns
            data[numeric_columns] = data[numeric_columns].fillna(0)
            
            # Remove highly correlated features
            data = self._remove_highly_correlated_features(data)
            
            # Remove constant features
            data = self._remove_constant_features(data)
            
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
    
    def _remove_constant_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Remove constant or near-constant features"""
        try:
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            constant_features = []
            
            for col in numeric_cols:
                if data[col].nunique() <= 1 or data[col].std() < 1e-8:
                    constant_features.append(col)
            
            if constant_features:
                data = data.drop(columns=constant_features)
                self.logger.info(f"Removed {len(constant_features)} constant features")
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error removing constant features: {e}")
            return data
    
    def _categorize_features(self):
        """Categorize features into groups for analysis"""
        try:
            self.feature_groups = {
                'market_structure': [f for f in self.feature_names if any(x in f for x in ['trend_slope', 'trend_strength', 'higher_highs', 'lower_lows', 'structure_break', 'efficiency'])],
                'trend_analysis': [f for f in self.feature_names if any(x in f for x in ['adx', 'ema_', 'psar', 'trend_consistency', 'trend_persistence'])],
                'volatility': [f for f in self.feature_names if any(x in f for x in ['volatility_', 'vol_', 'parkinson', 'gk_volatility', 'vol_clustering'])],
                'momentum': [f for f in self.feature_names if any(x in f for x in ['rsi_', 'stoch_', 'williams_r', 'cci', 'roc_', 'mfi'])],
                'technical': [f for f in self.feature_names if any(x in f for x in ['bb_', 'keltner', 'donchian', 'aroon'])],
                'microstructure': [f for f in self.feature_names if any(x in f for x in ['range_ratio', 'body_ratio', 'wick_', 'gap', 'clv', 'vpt', 'force_index', 'pressure'])],
                'regime_transition': [f for f in self.feature_names if any(x in f for x in ['regime_change', 'cusum', 'cycle_'])],
                'statistical': [f for f in self.feature_names if any(x in f for x in ['returns_mean', 'returns_std', 'returns_skew', 'returns_kurt', 'jarque_bera', 'ljung_box', 'z_score', 'hurst'])],
                'cross_sectional': [f for f in self.feature_names if any(x in f for x in ['momentum_vol_ratio', 'sharpe_ratio', 'trend_persistence', 'regime_stability'])],
                'frequency_domain': [f for f in self.feature_names if any(x in f for x in ['spectral_', 'freq_', 'high_freq', 'low_freq'])]
            }
            
        except Exception as e:
            self.logger.error(f"Error categorizing features: {e}")

class EnhancedSVMModel:
    """
    Enhanced Professional SVM Model for Market Regime Classification
    
    This class implements a sophisticated SVM-based classification model for identifying
    market regimes, volatility states, and trading environments with advanced features
    including kernel optimization, feature selection, and real-time inference.
    """
    
    def __init__(self, config: SVMConfig):
        self.config = config
        self.model = None
        self.feature_engineer = SVMFeatureEngineering(config)
        self.scaler = RobustScaler()
        self.label_encoder = LabelEncoder()
        self.feature_selector = None
        self.selected_features = []
        self.model_version = "1.0"
        self.training_history = {}
        self.feature_importance = {}
        self.decision_function_weights = {}
        
        # Setup logging
        self.logger = setup_logging('INFO')
        
        # Create model directory
        Path(self.config.model_save_path).mkdir(parents=True, exist_ok=True)
    
    def create_regime_labels(self, data: pd.DataFrame) -> pd.Series:
        """Create sophisticated regime labels using multiple criteria"""
        try:
            close = data['close']
            high = data['high']
            low = data['low']
            returns = close.pct_change()
            
            # Calculate trend strength
            trend_window = self.config.trend_window
            trend_slope = close.rolling(trend_window).apply(
                lambda x: stats.linregress(range(len(x)), x)[0] if len(x) == trend_window else 0
            )
            trend_r2 = close.rolling(trend_window).apply(
                lambda x: stats.linregress(range(len(x)), x)[2]**2 if len(x) == trend_window else 0
            )
            
            # Calculate volatility
            vol_window = self.config.volatility_window
            volatility = returns.rolling(vol_window).std() * np.sqrt(252)
            vol_percentile = volatility.rolling(252).rank(pct=True)
            
            # Initialize regime labels
            regimes = pd.Series(MarketRegime.RANGING_NEUTRAL, index=data.index)
            
            # Trend classification
            strong_trend_threshold = 0.7
            weak_trend_threshold = 0.3
            
            # Volatility classification
            high_vol_threshold = 0.75
            low_vol_threshold = 0.25
            
            # Trend-based regime classification
            strong_uptrend = (trend_slope > 0) & (trend_r2 > strong_trend_threshold)
            weak_uptrend = (trend_slope > 0) & (trend_r2 > weak_trend_threshold) & (trend_r2 <= strong_trend_threshold)
            strong_downtrend = (trend_slope < 0) & (trend_r2 > strong_trend_threshold)
            weak_downtrend = (trend_slope < 0) & (trend_r2 > weak_trend_threshold) & (trend_r2 <= strong_trend_threshold)
            
            # Volatility-based adjustments
            high_volatility = vol_percentile > high_vol_threshold
            low_volatility = vol_percentile < low_vol_threshold
            
            # Assign regime labels
            regimes.loc[strong_uptrend & ~high_volatility] = MarketRegime.STRONG_TRENDING_UP
            regimes.loc[strong_uptrend & high_volatility] = MarketRegime.TRENDING_UP
            regimes.loc[weak_uptrend & low_volatility] = MarketRegime.WEAK_TRENDING_UP
            regimes.loc[weak_uptrend & ~low_volatility] = MarketRegime.RANGING_BULLISH
            
            regimes.loc[strong_downtrend & ~high_volatility] = MarketRegime.STRONG_TRENDING_DOWN
            regimes.loc[strong_downtrend & high_volatility] = MarketRegime.TRENDING_DOWN
            regimes.loc[weak_downtrend & low_volatility] = MarketRegime.WEAK_TRENDING_DOWN
            regimes.loc[weak_downtrend & ~low_volatility] = MarketRegime.RANGING_BEARISH
            
            # Volatility regimes
            regimes.loc[high_volatility & (trend_r2 <= weak_trend_threshold)] = MarketRegime.HIGH_VOLATILITY
            regimes.loc[low_volatility & (trend_r2 <= weak_trend_threshold)] = MarketRegime.LOW_VOLATILITY
            
            # Breakout detection (simple version)
            price_range = high.rolling(20).max() - low.rolling(20).min()
            current_position = (close - low.rolling(20).min()) / price_range
            
            breakout_up = (current_position > 0.95) & (close > close.shift(1))
            breakout_down = (current_position < 0.05) & (close < close.shift(1))
            
            regimes.loc[breakout_up] = MarketRegime.BREAKOUT
            regimes.loc[breakout_down] = MarketRegime.BREAKOUT
            
            # Reversal detection (simple version based on momentum divergence)
            short_ma = close.rolling(5).mean()
            long_ma = close.rolling(20).mean()
            ma_cross_up = (short_ma > long_ma) & (short_ma.shift(1) <= long_ma.shift(1))
            ma_cross_down = (short_ma < long_ma) & (short_ma.shift(1) >= long_ma.shift(1))
            
            regimes.loc[ma_cross_up & (trend_slope.shift(5) < 0)] = MarketRegime.REVERSAL
            regimes.loc[ma_cross_down & (trend_slope.shift(5) > 0)] = MarketRegime.REVERSAL
            
            # Consolidation detection
            bb_width = (
                ta.volatility.bollinger_hband(close) - ta.volatility.bollinger_lband(close)
            ) / ta.volatility.bollinger_mavg(close)
            
            consolidation = bb_width < bb_width.rolling(50).quantile(0.2)
            regimes.loc[consolidation] = MarketRegime.CONSOLIDATION
            
            self.logger.info(f"Created regime labels with distribution: {regimes.value_counts().to_dict()}")
            
            return regimes
            
        except Exception as e:
            self.logger.error(f"Error creating regime labels: {e}")
            return pd.Series(MarketRegime.RANGING_NEUTRAL, index=data.index)
    
    def prepare_training_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare comprehensive training data for SVM model"""
        try:
            self.logger.info("Preparing training data with comprehensive feature engineering...")
            
            # Engineer features
            featured_data = self.feature_engineer.engineer_regime_features(data)
            
            # Create regime labels
            regime_labels = self.create_regime_labels(featured_data)
            featured_data['target'] = regime_labels
            
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
            regime_distribution = np.bincount(y_data)
            self.logger.info(f"Regime distribution: {dict(enumerate(regime_distribution))}")
            
            return X_scaled, y_data.values
            
        except Exception as e:
            self.logger.error(f"Error preparing training data: {e}")
            raise
    
    def _select_features(self, X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
        """Select best features using specified method"""
        try:
            if self.config.feature_selection_method == 'rfe':
                # Recursive Feature Elimination
                from sklearn.feature_selection import RFE
                from sklearn.svm import SVC
                
                estimator = SVC(kernel='linear', C=1.0, random_state=42)
                self.feature_selector = RFE(
                    estimator, 
                    n_features_to_select=min(self.config.max_features_selected, X.shape[1]),
                    step=1
                )
                X_selected = self.feature_selector.fit_transform(X, y)
                selected_features = X.columns[self.feature_selector.support_].tolist()
                
            elif self.config.feature_selection_method == 'kbest':
                # K-Best features using mutual information
                self.feature_selector = SelectKBest(
                    score_func=mutual_info_classif,
                    k=min(self.config.max_features_selected, X.shape[1])
                )
                X_selected = self.feature_selector.fit_transform(X, y)
                selected_features = X.columns[self.feature_selector.get_support()].tolist()
                
            elif self.config.feature_selection_method == 'pca':
                # Principal Component Analysis
                self.feature_selector = PCA(n_components=self.config.pca_variance_threshold)
                X_selected = self.feature_selector.fit_transform(X)
                
                # Create feature names for PCA components
                n_components = self.feature_selector.n_components_
                selected_features = [f'PC_{i+1}' for i in range(n_components)]
                
                # Convert back to DataFrame for consistency
                X = pd.DataFrame(X_selected, columns=selected_features, index=X.index)
                
            else:
                selected_features = X.columns.tolist()
                X = X
            
            # Store selected features
            self.selected_features = selected_features
            
            self.logger.info(f"Selected {len(selected_features)} features using {self.config.feature_selection_method} method")
            
            return X[selected_features] if self.config.feature_selection_method != 'pca' else X
            
        except Exception as e:
            self.logger.error(f"Error in feature selection: {e}")
            return X
    
    def train(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Train the SVM model with comprehensive evaluation"""
        try:
            self.logger.info("Starting SVM model training...")
            
            # Prepare data
            X, y = self.prepare_training_data(data)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y,
                test_size=self.config.test_size,
                random_state=42,
                stratify=y
            )
            
            # Further split training data for validation
            X_train, X_val, y_train, y_val = train_test_split(
                X_train, y_train,
                test_size=self.config.validation_size,
                random_state=42,
                stratify=y_train
            )
            
            # Hyperparameter optimization
            if self.config.enable_hyperparameter_optimization:
                best_params = self._optimize_hyperparameters(X_train, y_train)
                self._update_config_with_best_params(best_params)
            
            # Train model with best parameters
            self.model = SVC(
                kernel=self.config.kernel,
                C=self.config.C,
                gamma=self.config.gamma,
                degree=self.config.degree,
                coef0=self.config.coef0,
                class_weight=self.config.class_weight,
                probability=True,  # Enable probability estimates
                random_state=42
            )
            
            self.model.fit(X_train, y_train)
            
            # Evaluate model
            training_results = self._evaluate_model(X_train, X_val, X_test, y_train, y_val, y_test)
            
            # Calculate feature importance (for linear kernel)
            if self.config.kernel == 'linear':
                self._calculate_feature_importance()
            
            # Cross-validation
            cv_scores = cross_val_score(
                self.model, X_train, y_train,
                cv=StratifiedKFold(n_splits=self.config.cross_validation_folds, shuffle=True, random_state=42),
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
            self.logger.error(f"Error training SVM model: {e}")
            raise
    
    def _optimize_hyperparameters(self, X_train: np.ndarray, y_train: np.ndarray) -> Dict[str, Any]:
        """Optimize SVM hyperparameters using Optuna"""
        try:
            self.logger.info("Starting hyperparameter optimization...")
            
            def objective(trial):
                # Suggest hyperparameters
                kernel = trial.suggest_categorical('kernel', ['linear', 'rbf', 'poly', 'sigmoid'])
                C = trial.suggest_float('C', 0.01, 100, log=True)
                
                if kernel == 'rbf' or kernel == 'poly' or kernel == 'sigmoid':
                    gamma = trial.suggest_categorical('gamma', ['scale', 'auto'])
                else:
                    gamma = 'scale'
                
                if kernel == 'poly':
                    degree = trial.suggest_int('degree', 2, 5)
                else:
                    degree = 3
                
                if kernel == 'poly' or kernel == 'sigmoid':
                    coef0 = trial.suggest_float('coef0', -1.0, 1.0)
                else:
                    coef0 = 0.0
                
                # Create temporary model
                temp_model = SVC(
                    kernel=kernel,
                    C=C,
                    gamma=gamma,
                    degree=degree,
                    coef0=coef0,
                    class_weight=self.config.class_weight,
                    random_state=42
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
            study.optimize(objective, n_trials=self.config.optimization_trials, timeout=self.config.optimization_timeout)
            
            best_params = study.best_params
            
            self.logger.info(f"Hyperparameter optimization completed. Best accuracy: {study.best_value:.4f}")
            self.logger.info(f"Best parameters: {best_params}")
            
            return best_params
            
        except Exception as e:
            self.logger.error(f"Error in hyperparameter optimization: {e}")
            return {}
    
    def _update_config_with_best_params(self, best_params: Dict[str, Any]):
        """Update configuration with best hyperparameters"""
        try:
            if 'kernel' in best_params:
                self.config.kernel = best_params['kernel']
            if 'C' in best_params:
                self.config.C = best_params['C']
            if 'gamma' in best_params:
                self.config.gamma = best_params['gamma']
            if 'degree' in best_params:
                self.config.degree = best_params['degree']
            if 'coef0' in best_params:
                self.config.coef0 = best_params['coef0']
                
        except Exception as e:
            self.logger.error(f"Error updating config with best params: {e}")
    
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
            
            # Decision function scores
            decision_scores = self.model.decision_function(X_test)
            
            # Metrics
            results = {
                'train_accuracy': accuracy_score(y_train, y_train_pred),
                'val_accuracy': accuracy_score(y_val, y_val_pred),
                'test_accuracy': accuracy_score(y_test, y_test_pred),
                'train_precision': precision_score(y_train, y_train_pred, average='weighted', zero_division=0),
                'val_precision': precision_score(y_val, y_val_pred, average='weighted', zero_division=0),
                'test_precision': precision_score(y_test, y_test_pred, average='weighted', zero_division=0),
                'train_recall': recall_score(y_train, y_train_pred, average='weighted', zero_division=0),
                'val_recall': recall_score(y_val, y_val_pred, average='weighted', zero_division=0),
                'test_recall': recall_score(y_test, y_test_pred, average='weighted', zero_division=0),
                'train_f1': f1_score(y_train, y_train_pred, average='weighted', zero_division=0),
                'val_f1': f1_score(y_val, y_val_pred, average='weighted', zero_division=0),
                'test_f1': f1_score(y_test, y_test_pred, average='weighted', zero_division=0),
                'feature_count': X_train.shape[1],
                'training_samples': X_train.shape[0],
                'validation_samples': X_val.shape[0],
                'test_samples': X_test.shape[0]
            }
            
            # Classification report
            results['classification_report'] = classification_report(
                y_test, y_test_pred,
                target_names=[MarketRegime.get_regime_name(i) for i in range(self.config.n_classes)],
                output_dict=True,
                zero_division=0
            )
            
            # Confusion matrix
            results['confusion_matrix'] = confusion_matrix(y_test, y_test_pred).tolist()
            
            # Store decision function weights for interpretation
            if hasattr(self.model, 'coef_'):
                self.decision_function_weights = {
                    f'class_{i}': self.model.coef_[i].tolist() if len(self.model.coef_) > i else []
                    for i in range(len(self.model.coef_))
                }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error evaluating model: {e}")
            return {}
    
    def _calculate_feature_importance(self):
        """Calculate feature importance for linear SVM"""
        try:
            if self.config.kernel != 'linear' or not hasattr(self.model, 'coef_'):
                self.logger.warning("Feature importance calculation only available for linear kernel")
                return
            
            # For linear SVM, feature importance is the absolute value of coefficients
            coef = np.abs(self.model.coef_)
            
            # Average across classes for multi-class
            if len(coef.shape) > 1:
                feature_importance = np.mean(coef, axis=0)
            else:
                feature_importance = coef
            
            # Normalize to sum to 1
            feature_importance = feature_importance / np.sum(feature_importance)
            
            # Create feature importance dictionary
            self.feature_importance = dict(zip(self.selected_features, feature_importance))
            
            # Sort by importance
            self.feature_importance = dict(sorted(
                self.feature_importance.items(),
                key=lambda x: x[1],
                reverse=True
            ))
            
            self.logger.info(f"Calculated feature importance for {len(self.feature_importance)} features")
            
        except Exception as e:
            self.logger.error(f"Error calculating feature importance: {e}")
    
    def predict(self, data: pd.DataFrame, return_probabilities: bool = True) -> Union[SVMPrediction, int]:
        """Make prediction with comprehensive metadata"""
        try:
            if self.model is None:
                raise ValueError("Model not trained or loaded")
            
            # Engineer features for input data
            featured_data = self.feature_engineer.engineer_regime_features(data)
            
            # Select the same features used in training
            if self.selected_features:
                if self.config.feature_selection_method == 'pca':
                    # For PCA, we need to transform the original features
                    feature_cols = [col for col in featured_data.columns 
                                   if col not in ['close', 'open', 'high', 'low', 'volume']]
                    X_data = featured_data[feature_cols]
                    X_data = X_data.fillna(0)
                    X_transformed = self.feature_selector.transform(X_data.tail(1))
                    X_scaled = self.scaler.transform(X_transformed)
                else:
                    X_data = featured_data[self.selected_features]
                    X_scaled = self.scaler.transform(X_data.tail(1))
            else:
                feature_cols = [col for col in featured_data.columns 
                               if col not in ['close', 'open', 'high', 'low', 'volume']]
                X_data = featured_data[feature_cols]
                X_scaled = self.scaler.transform(X_data.tail(1))
            
            # Make prediction
            prediction = self.model.predict(X_scaled)[0]
            probabilities = self.model.predict_proba(X_scaled)[0]
            
            if not return_probabilities:
                return prediction
            
            # Calculate confidence (max probability)
            confidence = float(np.max(probabilities))
            
            # Create probability dictionary
            prob_dict = {}
            for i, prob in enumerate(probabilities):
                if i < self.config.n_classes:
                    regime_name = MarketRegime.get_regime_name(i)
                    prob_dict[regime_name] = float(prob)
            
            # Decision function scores
            decision_scores = {}
            if hasattr(self.model, 'decision_function'):
                try:
                    decision_vals = self.model.decision_function(X_scaled)[0]
                    if len(decision_vals.shape) == 0:
                        decision_vals = [decision_vals]
                    
                    for i, score in enumerate(decision_vals):
                        if i < len(self.model.classes_):
                            regime_name = MarketRegime.get_regime_name(self.model.classes_[i])
                            decision_scores[regime_name] = float(score)
                except:
                    decision_scores = {}
            
            # Calculate feature contributions (for linear kernel)
            feature_contributions = self._calculate_feature_contributions(X_scaled[0])
            
            # Calculate regime stability and transition probability
            regime_stability, transition_probability = self._calculate_regime_stability(data, prediction)
            
            # Create prediction object
            svm_prediction = SVMPrediction(
                regime=int(prediction),
                regime_name=MarketRegime.get_regime_name(prediction),
                regime_category=MarketRegime.get_regime_category(prediction),
                confidence=confidence,
                probabilities=prob_dict,
                decision_scores=decision_scores,
                feature_contributions=feature_contributions,
                model_version=self.model_version,
                prediction_time=datetime.utcnow(),
                input_features=dict(zip(self.selected_features, X_scaled[0])) if len(X_scaled[0]) == len(self.selected_features) else {},
                regime_stability=regime_stability,
                transition_probability=transition_probability
            )
            
            return svm_prediction
            
        except Exception as e:
            self.logger.error(f"Error making prediction: {e}")
            raise
    
    def _calculate_feature_contributions(self, feature_values: np.ndarray) -> Dict[str, float]:
        """Calculate feature contributions to prediction"""
        try:
            if (self.config.kernel != 'linear' or 
                not hasattr(self.model, 'coef_') or 
                not self.feature_importance or 
                len(feature_values) != len(self.selected_features)):
                return {}
            
            # For linear SVM, contribution is feature_value * weight * importance
            contributions = {}
            for i, feature_name in enumerate(self.selected_features):
                importance = self.feature_importance.get(feature_name, 0)
                contribution = float(feature_values[i] * importance)
                contributions[feature_name] = contribution
            
            # Sort by absolute contribution
            contributions = dict(sorted(
                contributions.items(), 
                key=lambda x: abs(x[1]), 
                reverse=True
            ))
            
            return dict(list(contributions.items())[:10])  # Top 10 contributions
            
        except Exception as e:
            self.logger.error(f"Error calculating feature contributions: {e}")
            return {}
    
    def _calculate_regime_stability(self, data: pd.DataFrame, current_regime: int) -> Tuple[float, float]:
        """Calculate regime stability and transition probability"""
        try:
            if len(data) < 20:
                return 0.5, 0.5
            
            # Create regime labels for recent data
            recent_regimes = self.create_regime_labels(data.tail(20))
            
            # Calculate stability as the percentage of time in current regime
            current_regime_count = (recent_regimes == current_regime).sum()
            stability = current_regime_count / len(recent_regimes)
            
            # Calculate transition probability as the rate of regime changes
            regime_changes = (recent_regimes != recent_regimes.shift(1)).sum()
            transition_probability = regime_changes / (len(recent_regimes) - 1)
            
            return float(stability), float(transition_probability)
            
        except Exception as e:
            self.logger.error(f"Error calculating regime stability: {e}")
            return 0.5, 0.5
    
    def save_model(self, filepath: Optional[str] = None):
        """Save the complete model with metadata"""
        try:
            if self.model is None:
                raise ValueError("No model to save")
            
            if filepath is None:
                filepath = str(Path(self.config.model_save_path) / f'svm_model_{self.model_version}.pkl')
            
            # Prepare complete model package
            model_package = {
                'model': self.model,
                'config': self.config,
                'scaler': self.scaler,
                'feature_engineer': self.feature_engineer,
                'feature_selector': self.feature_selector,
                'selected_features': self.selected_features,
                'feature_importance': self.feature_importance,
                'decision_function_weights': self.decision_function_weights,
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
            self.feature_selector = model_package.get('feature_selector')
            self.selected_features = model_package['selected_features']
            self.feature_importance = model_package['feature_importance']
            self.decision_function_weights = model_package.get('decision_function_weights', {})
            self.model_version = model_package['model_version']
            self.training_history = model_package['training_history']
            
            self.logger.info(f"Model loaded from {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
            raise
    
    def get_regime_analysis(self) -> Dict[str, Any]:
        """Get comprehensive regime analysis"""
        try:
            if not self.training_history:
                return {'status': 'No training history available'}
            
            # Regime performance analysis
            regime_performance = {}
            if 'classification_report' in self.training_history:
                for regime_name, metrics in self.training_history['classification_report'].items():
                    if isinstance(metrics, dict) and 'precision' in metrics:
                        regime_performance[regime_name] = {
                            'precision': metrics['precision'],
                            'recall': metrics['recall'],
                            'f1_score': metrics['f1-score'],
                            'support': metrics['support']
                        }
            
            # Feature group importance
            group_importance = {}
            if self.feature_importance:
                for group_name, features in self.feature_engineer.feature_groups.items():
                    group_score = sum(self.feature_importance.get(f, 0) for f in features)
                    group_importance[group_name] = group_score
                
                # Sort groups by importance
                group_importance = dict(sorted(group_importance.items(), key=lambda x: x[1], reverse=True))
            
            analysis = {
                'regime_count': self.config.n_classes,
                'regime_performance': regime_performance,
                'feature_groups_importance': group_importance,
                'kernel_used': self.config.kernel,
                'feature_selection_method': self.config.feature_selection_method,
                'hyperparameters': {
                    'C': self.config.C,
                    'gamma': self.config.gamma,
                    'kernel': self.config.kernel,
                    'degree': self.config.degree if self.config.kernel == 'poly' else None,
                    'coef0': self.config.coef0 if self.config.kernel in ['poly', 'sigmoid'] else None
                }
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error getting regime analysis: {e}")
            return {'error': str(e)}
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get comprehensive model information"""
        try:
            if self.model is None:
                return {'status': 'No model loaded'}
            
            info = {
                'model_version': self.model_version,
                'model_type': 'Support Vector Machine',
                'classification_type': self.config.classification_type,
                'architecture': {
                    'kernel': self.config.kernel,
                    'C': self.config.C,
                    'gamma': self.config.gamma,
                    'degree': self.config.degree,
                    'n_classes': self.config.n_classes,
                    'feature_count': len(self.selected_features),
                    'support_vectors': self.model.n_support_.tolist() if hasattr(self.model, 'n_support_') else []
                },
                'training_config': {
                    'feature_selection_method': self.config.feature_selection_method,
                    'max_features_selected': self.config.max_features_selected,
                    'cross_validation_folds': self.config.cross_validation_folds,
                    'class_weight': self.config.class_weight
                },
                'regime_classes': {
                    i: MarketRegime.get_regime_name(i) 
                    for i in range(self.config.n_classes)
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
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting model info: {e}")
            return {'error': str(e)}

# Usage Example and Testing
def example_usage():
    """Comprehensive example of using the Enhanced SVM Model"""
    
    print("=== Enhanced SVM Model Example ===")
    
    # Create configuration
    config = SVMConfig(
        kernel='rbf',
        C=1.0,
        gamma='scale',
        classification_type='regime',
        n_classes=14,
        use_technical_indicators=True,
        use_market_microstructure=True,
        use_volatility_features=True,
        use_momentum_features=True,
        use_regime_transition_features=True,
        feature_selection_method='rfe',
        max_features_selected=30,
        enable_hyperparameter_optimization=True
    )
    
    # Create model
    svm_model = EnhancedSVMModel(config)
    
    # Generate sample data with realistic market regimes
    dates = pd.date_range('2020-01-01', periods=3000, freq='H')
    np.random.seed(42)
    
    # Generate different market regimes
    regime_changes = [0, 500, 1000, 1500, 2000, 2500]
    price_base = 100
    prices = []
    
    for i, start_idx in enumerate(regime_changes[:-1]):
        end_idx = regime_changes[i + 1]
        length = end_idx - start_idx
        
        if i % 3 == 0:  # Trending up
            trend = np.linspace(0, 0.3, length)
            noise = np.random.normal(0, 0.015, length)
        elif i % 3 == 1:  # Trending down
            trend = np.linspace(0, -0.3, length)
            noise = np.random.normal(0, 0.015, length)
        else:  # Ranging/volatile
            trend = np.zeros(length)
            noise = np.random.normal(0, 0.025, length)
        
        segment_returns = trend + noise
        if i == 0:
            segment_prices = price_base * (1 + segment_returns).cumprod()
        else:
            segment_prices = prices[-1] * (1 + segment_returns).cumprod()
        
        prices.extend(segment_prices.tolist())
    
    # Complete the series
    remaining = 3000 - len(prices)
    if remaining > 0:
        final_returns = np.random.normal(0, 0.02, remaining)
        final_prices = prices[-1] * (1 + final_returns).cumprod()
        prices.extend(final_prices.tolist())
    
    prices = np.array(prices[:3000])
    
    # Generate OHLC from prices
    high_prices = prices * (1 + np.abs(np.random.normal(0, 0.008, 3000)))
    low_prices = prices * (1 - np.abs(np.random.normal(0, 0.008, 3000)))
    open_prices = np.roll(prices, 1)
    open_prices[0] = prices[0]
    
    volumes = np.random.lognormal(10, 0.6, 3000)
    
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
        print("\n1. Training SVM Model...")
        training_results = svm_model.train(sample_data)
        print("Training Results:")
        for key, value in training_results.items():
            if key not in ['classification_report', 'confusion_matrix']:
                print(f"   {key}: {value}")
        
        # Show classification report for key regimes
        if 'classification_report' in training_results:
            print("\n2. Classification Report (Top Regimes):")
            report = training_results['classification_report']
            key_regimes = ['STRONG_TRENDING_UP', 'TRENDING_DOWN', 'RANGING_NEUTRAL', 'HIGH_VOLATILITY']
            for regime in key_regimes:
                if regime in report and isinstance(report[regime], dict):
                    metrics = report[regime]
                    print(f"   {regime}: Precision={metrics.get('precision', 0):.3f}, "
                          f"Recall={metrics.get('recall', 0):.3f}, F1={metrics.get('f1-score', 0):.3f}")
        
        # Make predictions
        print("\n3. Making Predictions...")
        prediction = svm_model.predict(sample_data.tail(200))
        print(f"Regime Prediction: {prediction.regime_name}")
        print(f"Regime Category: {prediction.regime_category}")
        print(f"Confidence: {prediction.confidence:.4f}")
        print(f"Regime Stability: {prediction.regime_stability:.4f}")
        print(f"Transition Probability: {prediction.transition_probability:.4f}")
        
        # Show top regime probabilities
        print("\n4. Top 5 Regime Probabilities:")
        sorted_probs = sorted(prediction.probabilities.items(), key=lambda x: x[1], reverse=True)
        for regime_name, prob in sorted_probs[:5]:
            print(f"   {regime_name}: {prob:.4f}")
        
        # Show decision scores (if available)
        if prediction.decision_scores:
            print("\n5. Top 5 Decision Scores:")
            sorted_scores = sorted(prediction.decision_scores.items(), key=lambda x: x[1], reverse=True)
            for regime_name, score in sorted_scores[:5]:
                print(f"   {regime_name}: {score:.4f}")
        
        # Show feature contributions
        if prediction.feature_contributions:
            print("\n6. Top 10 Feature Contributions:")
            for feature, contribution in list(prediction.feature_contributions.items())[:10]:
                print(f"   {feature}: {contribution:.6f}")
        
        # Regime analysis
        print("\n7. Regime Analysis:")
        regime_analysis = svm_model.get_regime_analysis()
        print(f"   Total Regimes: {regime_analysis['regime_count']}")
        print(f"   Kernel Used: {regime_analysis['kernel_used']}")
        print(f"   Feature Selection: {regime_analysis['feature_selection_method']}")
        
        if 'feature_groups_importance' in regime_analysis:
            print("\n8. Top 5 Feature Group Importance:")
            for group, importance in list(regime_analysis['feature_groups_importance'].items())[:5]:
                print(f"   {group}: {importance:.4f}")
        
        # Model information
        print("\n9. Model Information:")
        model_info = svm_model.get_model_info()
        print(f"   Model Type: {model_info['model_type']}")
        print(f"   Kernel: {model_info['architecture']['kernel']}")
        print(f"   C Parameter: {model_info['architecture']['C']}")
        print(f"   Feature Count: {model_info['architecture']['feature_count']}")
        print(f"   Support Vectors: {sum(model_info['architecture']['support_vectors'])}")
        
        if 'performance' in model_info:
            print(f"   Test Accuracy: {model_info['performance']['test_accuracy']:.4f}")
            print(f"   Test F1 Score: {model_info['performance']['test_f1']:.4f}")
            print(f"   CV Mean Accuracy: {model_info['performance']['cv_mean_accuracy']:.4f}")
        
        print("\n=== SVM Model Example Completed Successfully ===")
        return svm_model
        
    except Exception as e:
        print(f"Error in example: {e}")
        return None

if __name__ == "__main__":
    # Run the comprehensive example
    model = example_usage()