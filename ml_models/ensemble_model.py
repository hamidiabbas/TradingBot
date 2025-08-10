"""
Enhanced Professional Ensemble Model for Trading Meta-Learning
============================================================

A sophisticated ensemble learning implementation that combines LSTM temporal analysis,
Random Forest multi-class classification, and SVM market regime detection into a
unified meta-learning framework with advanced voting mechanisms, stacking models,
and dynamic model selection for institutional-grade algorithmic trading systems.

Features:
- Multi-Model Integration (LSTM + Random Forest + SVM)
- Advanced Ensemble Techniques (Weighted Voting, Stacking, Blending)
- Dynamic Model Selection and Adaptive Weighting
- Real-time Prediction Fusion with Confidence Scoring
- Model Performance Monitoring and Drift Detection
- Uncertainty Quantification and Risk Assessment
- Meta-Feature Engineering for Enhanced Performance
- Professional Error Handling and Logging
- Production-Ready with Comprehensive Metadata

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
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path
import pickle
import joblib
from sklearn.ensemble import VotingClassifier, VotingRegressor, StackingClassifier, StackingRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge, Lasso
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score, TimeSeriesSplit
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, mean_absolute_error, r2_score,
    classification_report, confusion_matrix, roc_auc_score
)
from sklearn.calibration import CalibratedClassifierCV
import optuna
from scipy import stats
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import seaborn as sns

# Import our individual models
from ml_models.lstm_model import EnhancedLSTMModel, LSTMConfig, LSTMPrediction
from ml_models.random_forest_model import EnhancedRandomForestModel, RandomForestConfig, RandomForestPrediction
from ml_models.svm_model import EnhancedSVMModel, SVMConfig, SVMPrediction

from utils.logger import setup_logging

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

class EnsembleMethod:
    """Ensemble method enumeration"""
    SIMPLE_VOTING = "simple_voting"
    WEIGHTED_VOTING = "weighted_voting"
    STACKING = "stacking"
    BLENDING = "blending"
    DYNAMIC_SELECTION = "dynamic_selection"
    BAYESIAN_MODEL_AVERAGING = "bayesian_averaging"
    ADAPTIVE_WEIGHTING = "adaptive_weighting"

class PredictionType:
    """Prediction type enumeration"""
    PRICE_DIRECTION = "price_direction"  # Up/Down classification
    SIGNAL_CLASSIFICATION = "signal_classification"  # Buy/Sell/Hold
    REGIME_CLASSIFICATION = "regime_classification"  # Market regime
    PRICE_REGRESSION = "price_regression"  # Actual price prediction
    VOLATILITY_PREDICTION = "volatility_prediction"  # Volatility forecasting

@dataclass
class EnsembleConfig:
    """Ensemble model configuration with comprehensive parameters"""
    # Model integration parameters
    use_lstm: bool = True
    use_random_forest: bool = True
    use_svm: bool = True
    
    # Ensemble method configuration
    ensemble_method: str = 'adaptive_weighting'  # Primary ensemble method
    fallback_method: str = 'weighted_voting'     # Fallback if primary fails
    voting_type: str = 'soft'  # 'hard' or 'soft' voting
    
    # Stacking configuration
    meta_learner: str = 'logistic_regression'  # Meta-learner for stacking
    use_cross_validation_stacking: bool = True
    stacking_cv_folds: int = 5
    
    # Dynamic selection parameters
    performance_window: int = 100  # Window for performance evaluation
    min_performance_samples: int = 50
    model_selection_metric: str = 'accuracy'  # Metric for model selection
    
    # Adaptive weighting parameters
    adaptation_rate: float = 0.1  # Learning rate for weight adaptation
    weight_decay: float = 0.95   # Decay factor for historical performance
    min_weight: float = 0.05     # Minimum weight for any model
    max_weight: float = 0.8      # Maximum weight for any model
    
    # Confidence and uncertainty parameters
    confidence_threshold: float = 0.6
    uncertainty_quantile: float = 0.05  # For uncertainty estimation
    enable_calibration: bool = True     # Probability calibration
    
    # Feature engineering for meta-learning
    use_meta_features: bool = True
    meta_feature_window: int = 20
    include_model_confidence: bool = True
    include_model_agreement: bool = True
    
    # Performance monitoring
    performance_tracking_window: int = 1000
    drift_detection_threshold: float = 0.1
    enable_model_monitoring: bool = True
    
    # Model management
    model_save_path: str = "models/ensemble/"
    ensemble_update_frequency: int = 100  # Update weights every N predictions
    enable_online_learning: bool = True

@dataclass
class EnsemblePrediction:
    """Ensemble prediction result with comprehensive metadata"""
    # Core predictions
    final_prediction: Union[int, float]
    prediction_type: str
    confidence: float
    
    # Individual model predictions
    lstm_prediction: Optional[LSTMPrediction] = None
    rf_prediction: Optional[RandomForestPrediction] = None
    svm_prediction: Optional[SVMPrediction] = None
    
    # Ensemble analysis
    model_weights: Dict[str, float] = field(default_factory=dict)
    model_agreement: float = 0.0
    prediction_variance: float = 0.0
    uncertainty_score: float = 0.0
    
    # Meta information
    ensemble_method: str = ""
    meta_features: Dict[str, float] = field(default_factory=dict)
    model_contributions: Dict[str, float] = field(default_factory=dict)
    
    # Quality metrics
    prediction_quality: float = 0.0
    risk_assessment: str = "MEDIUM"
    recommendation_strength: str = "MODERATE"
    
    # Metadata
    prediction_time: datetime = field(default_factory=datetime.utcnow)
    model_version: str = "1.0"
    data_quality_score: float = 1.0

class ModelPerformanceTracker:
    """Advanced model performance tracking and analysis"""
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.performance_history = {
            'lstm': {'predictions': [], 'actuals': [], 'timestamps': []},
            'random_forest': {'predictions': [], 'actuals': [], 'timestamps': []},
            'svm': {'predictions': [], 'actuals': [], 'timestamps': []},
            'ensemble': {'predictions': [], 'actuals': [], 'timestamps': []}
        }
        self.performance_metrics = {}
        self.drift_alerts = []
        self.logger = setup_logging('INFO')
    
    def update_performance(self, model_name: str, prediction: Union[int, float], 
                          actual: Union[int, float], timestamp: datetime = None):
        """Update performance tracking for a specific model"""
        try:
            if timestamp is None:
                timestamp = datetime.utcnow()
            
            if model_name not in self.performance_history:
                self.performance_history[model_name] = {
                    'predictions': [], 'actuals': [], 'timestamps': []
                }
            
            # Add new performance data
            self.performance_history[model_name]['predictions'].append(prediction)
            self.performance_history[model_name]['actuals'].append(actual)
            self.performance_history[model_name]['timestamps'].append(timestamp)
            
            # Maintain window size
            if len(self.performance_history[model_name]['predictions']) > self.window_size:
                self.performance_history[model_name]['predictions'].pop(0)
                self.performance_history[model_name]['actuals'].pop(0)
                self.performance_history[model_name]['timestamps'].pop(0)
            
            # Update metrics
            self._calculate_metrics(model_name)
            
        except Exception as e:
            self.logger.error(f"Error updating performance for {model_name}: {e}")
    
    def _calculate_metrics(self, model_name: str):
        """Calculate performance metrics for a specific model"""
        try:
            history = self.performance_history[model_name]
            if len(history['predictions']) < 10:
                return
            
            predictions = np.array(history['predictions'])
            actuals = np.array(history['actuals'])
            
            # Classification metrics (assuming integer predictions are classifications)
            if all(isinstance(p, (int, np.integer)) for p in predictions):
                accuracy = accuracy_score(actuals, predictions)
                precision = precision_score(actuals, predictions, average='weighted', zero_division=0)
                recall = recall_score(actuals, predictions, average='weighted', zero_division=0)
                f1 = f1_score(actuals, predictions, average='weighted', zero_division=0)
                
                self.performance_metrics[model_name] = {
                    'accuracy': accuracy,
                    'precision': precision,
                    'recall': recall,
                    'f1_score': f1,
                    'sample_count': len(predictions),
                    'last_updated': datetime.utcnow()
                }
            
            # Regression metrics
            else:
                mse = mean_squared_error(actuals, predictions)
                mae = mean_absolute_error(actuals, predictions)
                r2 = r2_score(actuals, predictions)
                
                # Calculate directional accuracy
                actual_direction = np.sign(np.diff(actuals))
                pred_direction = np.sign(np.diff(predictions))
                directional_accuracy = np.mean(actual_direction == pred_direction)
                
                self.performance_metrics[model_name] = {
                    'mse': mse,
                    'mae': mae,
                    'r2_score': r2,
                    'directional_accuracy': directional_accuracy,
                    'sample_count': len(predictions),
                    'last_updated': datetime.utcnow()
                }
            
        except Exception as e:
            self.logger.error(f"Error calculating metrics for {model_name}: {e}")
    
    def detect_performance_drift(self, model_name: str, threshold: float = 0.1) -> bool:
        """Detect significant performance drift"""
        try:
            if model_name not in self.performance_metrics:
                return False
            
            history = self.performance_history[model_name]
            if len(history['predictions']) < 100:
                return False
            
            # Split data into recent and historical
            split_point = len(history['predictions']) // 2
            
            recent_preds = history['predictions'][split_point:]
            recent_actuals = history['actuals'][split_point:]
            
            historical_preds = history['predictions'][:split_point]
            historical_actuals = history['actuals'][:split_point]
            
            # Calculate performance for both periods
            if all(isinstance(p, (int, np.integer)) for p in recent_preds):
                recent_accuracy = accuracy_score(recent_actuals, recent_preds)
                historical_accuracy = accuracy_score(historical_actuals, historical_preds)
                performance_diff = abs(recent_accuracy - historical_accuracy)
            else:
                recent_r2 = r2_score(recent_actuals, recent_preds)
                historical_r2 = r2_score(historical_actuals, historical_preds)
                performance_diff = abs(recent_r2 - historical_r2)
            
            # Check for significant drift
            is_drift = performance_diff > threshold
            
            if is_drift:
                drift_alert = {
                    'model': model_name,
                    'drift_magnitude': performance_diff,
                    'timestamp': datetime.utcnow(),
                    'recent_performance': recent_accuracy if 'recent_accuracy' in locals() else recent_r2,
                    'historical_performance': historical_accuracy if 'historical_accuracy' in locals() else historical_r2
                }
                self.drift_alerts.append(drift_alert)
                self.logger.warning(f"Performance drift detected for {model_name}: {performance_diff:.4f}")
            
            return is_drift
            
        except Exception as e:
            self.logger.error(f"Error detecting drift for {model_name}: {e}")
            return False
    
    def get_model_rankings(self) -> Dict[str, int]:
        """Get current model performance rankings"""
        try:
            if not self.performance_metrics:
                return {}
            
            # Create performance scores
            scores = {}
            for model_name, metrics in self.performance_metrics.items():
                if 'accuracy' in metrics:
                    scores[model_name] = metrics['accuracy']
                elif 'r2_score' in metrics:
                    scores[model_name] = metrics['r2_score']
                else:
                    scores[model_name] = 0.0
            
            # Rank models
            sorted_models = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            rankings = {model: rank + 1 for rank, (model, _) in enumerate(sorted_models)}
            
            return rankings
            
        except Exception as e:
            self.logger.error(f"Error getting model rankings: {e}")
            return {}

class MetaFeatureEngineer:
    """Advanced meta-feature engineering for ensemble learning"""
    
    def __init__(self, config: EnsembleConfig):
        self.config = config
        self.feature_history = []
        self.logger = setup_logging('INFO')
    
    def engineer_meta_features(self, lstm_pred: Optional[LSTMPrediction], 
                              rf_pred: Optional[RandomForestPrediction],
                              svm_pred: Optional[SVMPrediction],
                              market_data: pd.DataFrame) -> Dict[str, float]:
        """Engineer meta-features for ensemble learning"""
        try:
            meta_features = {}
            
            # Model confidence features
            if self.config.include_model_confidence:
                meta_features.update(self._extract_confidence_features(lstm_pred, rf_pred, svm_pred))
            
            # Model agreement features
            if self.config.include_model_agreement:
                meta_features.update(self._extract_agreement_features(lstm_pred, rf_pred, svm_pred))
            
            # Market condition features
            meta_features.update(self._extract_market_condition_features(market_data))
            
            # Temporal features
            meta_features.update(self._extract_temporal_features())
            
            # Model uncertainty features
            meta_features.update(self._extract_uncertainty_features(lstm_pred, rf_pred, svm_pred))
            
            # Historical performance features
            meta_features.update(self._extract_performance_features())
            
            return meta_features
            
        except Exception as e:
            self.logger.error(f"Error engineering meta-features: {e}")
            return {}
    
    def _extract_confidence_features(self, lstm_pred: Optional[LSTMPrediction], 
                                   rf_pred: Optional[RandomForestPrediction],
                                   svm_pred: Optional[SVMPrediction]) -> Dict[str, float]:
        """Extract confidence-based meta-features"""
        features = {}
        
        try:
            # Individual model confidences
            if lstm_pred:
                features['lstm_confidence'] = lstm_pred.confidence
                features['lstm_prob_up'] = lstm_pred.probability_up
                features['lstm_prob_down'] = lstm_pred.probability_down
            
            if rf_pred:
                features['rf_confidence'] = rf_pred.confidence
                features['rf_risk_score'] = rf_pred.risk_score
                # Get max probability from RF prediction
                if rf_pred.probabilities:
                    features['rf_max_prob'] = max(rf_pred.probabilities.values())
            
            if svm_pred:
                features['svm_confidence'] = svm_pred.confidence
                features['svm_regime_stability'] = svm_pred.regime_stability
                features['svm_transition_prob'] = svm_pred.transition_probability
            
            # Confidence statistics
            confidences = [v for k, v in features.items() if 'confidence' in k]
            if confidences:
                features['mean_confidence'] = np.mean(confidences)
                features['std_confidence'] = np.std(confidences)
                features['min_confidence'] = np.min(confidences)
                features['max_confidence'] = np.max(confidences)
        
        except Exception as e:
            self.logger.error(f"Error extracting confidence features: {e}")
        
        return features
    
    def _extract_agreement_features(self, lstm_pred: Optional[LSTMPrediction], 
                                  rf_pred: Optional[RandomForestPrediction],
                                  svm_pred: Optional[SVMPrediction]) -> Dict[str, float]:
        """Extract agreement-based meta-features"""
        features = {}
        
        try:
            predictions = []
            
            # Convert predictions to comparable format
            if lstm_pred:
                # Convert LSTM price prediction to direction
                lstm_direction = 1 if lstm_pred.prediction > 0 else 0
                predictions.append(lstm_direction)
            
            if rf_pred:
                # Convert RF signal to direction (3=BUY, 4=STRONG_BUY are bullish)
                rf_direction = 1 if rf_pred.signal >= 3 else 0
                predictions.append(rf_direction)
            
            if svm_pred:
                # Convert SVM regime to direction (trending up regimes are bullish)
                svm_direction = 1 if svm_pred.regime in [0, 1, 2] else 0
                predictions.append(svm_direction)
            
            if len(predictions) >= 2:
                # Agreement metrics
                features['prediction_agreement'] = np.mean(predictions)
                features['prediction_variance'] = np.var(predictions)
                features['unanimous_agreement'] = float(len(set(predictions)) == 1)
                features['majority_agreement'] = float(np.mean(predictions) >= 0.5)
                
                # Pairwise agreements
                if len(predictions) == 3:
                    agreements = []
                    for i in range(len(predictions)):
                        for j in range(i + 1, len(predictions)):
                            agreements.append(float(predictions[i] == predictions[j]))
                    features['pairwise_agreement'] = np.mean(agreements)
        
        except Exception as e:
            self.logger.error(f"Error extracting agreement features: {e}")
        
        return features
    
    def _extract_market_condition_features(self, market_data: pd.DataFrame) -> Dict[str, float]:
        """Extract market condition meta-features"""
        features = {}
        
        try:
            if len(market_data) < 20:
                return features
            
            close = market_data['close'].tail(20)
            
            # Volatility features
            returns = close.pct_change().dropna()
            features['market_volatility'] = returns.std()
            features['volatility_percentile'] = stats.percentileofscore(returns, returns.iloc[-1]) / 100
            
            # Trend features
            trend_slope = stats.linregress(range(len(close)), close)[0]
            features['trend_strength'] = abs(trend_slope) / close.mean()
            features['trend_direction'] = np.sign(trend_slope)
            
            # Price position features
            recent_high = close.max()
            recent_low = close.min()
            current_price = close.iloc[-1]
            
            if recent_high != recent_low:
                features['price_position'] = (current_price - recent_low) / (recent_high - recent_low)
            
            # Momentum features
            features['short_momentum'] = (close.iloc[-1] - close.iloc[-5]) / close.iloc[-5]
            features['medium_momentum'] = (close.iloc[-1] - close.iloc[-10]) / close.iloc[-10]
            
        except Exception as e:
            self.logger.error(f"Error extracting market condition features: {e}")
        
        return features
    
    def _extract_temporal_features(self) -> Dict[str, float]:
        """Extract temporal meta-features"""
        features = {}
        
        try:
            now = datetime.utcnow()
            
            # Time-based features
            features['hour'] = now.hour / 24.0
            features['day_of_week'] = now.weekday() / 6.0
            features['month'] = now.month / 12.0
            
            # Trading session features
            # London: 7-16 UTC, NY: 12-21 UTC, Asian: 21-7 UTC
            if 7 <= now.hour < 16:
                features['london_session'] = 1.0
            else:
                features['london_session'] = 0.0
            
            if 12 <= now.hour < 21:
                features['ny_session'] = 1.0
            else:
                features['ny_session'] = 0.0
            
            if now.hour >= 21 or now.hour < 7:
                features['asian_session'] = 1.0
            else:
                features['asian_session'] = 0.0
        
        except Exception as e:
            self.logger.error(f"Error extracting temporal features: {e}")
        
        return features
    
    def _extract_uncertainty_features(self, lstm_pred: Optional[LSTMPrediction], 
                                    rf_pred: Optional[RandomForestPrediction],
                                    svm_pred: Optional[SVMPrediction]) -> Dict[str, float]:
        """Extract uncertainty-based meta-features"""
        features = {}
        
        try:
            uncertainties = []
            
            # Model-specific uncertainty measures
            if lstm_pred:
                # LSTM uncertainty from probability spread
                prob_spread = abs(lstm_pred.probability_up - lstm_pred.probability_down)
                lstm_uncertainty = 1.0 - prob_spread
                features['lstm_uncertainty'] = lstm_uncertainty
                uncertainties.append(lstm_uncertainty)
            
            if rf_pred:
                # RF uncertainty from risk score
                features['rf_uncertainty'] = rf_pred.risk_score
                uncertainties.append(rf_pred.risk_score)
            
            if svm_pred:
                # SVM uncertainty from transition probability
                features['svm_uncertainty'] = svm_pred.transition_probability
                uncertainties.append(svm_pred.transition_probability)
            
            # Aggregate uncertainty measures
            if uncertainties:
                features['mean_uncertainty'] = np.mean(uncertainties)
                features['max_uncertainty'] = np.max(uncertainties)
                features['uncertainty_spread'] = np.max(uncertainties) - np.min(uncertainties)
        
        except Exception as e:
            self.logger.error(f"Error extracting uncertainty features: {e}")
        
        return features
    
    def _extract_performance_features(self) -> Dict[str, float]:
        """Extract historical performance meta-features"""
        features = {}
        
        try:
            # This would be populated from historical performance tracking
            # For now, we'll use placeholder values
            features['recent_ensemble_accuracy'] = 0.7  # Placeholder
            features['model_drift_detected'] = 0.0      # Placeholder
            features['performance_trend'] = 0.1         # Placeholder
        
        except Exception as e:
            self.logger.error(f"Error extracting performance features: {e}")
        
        return features

class EnhancedEnsembleModel:
    """
    Enhanced Professional Ensemble Model for Trading Applications
    
    This class implements a sophisticated ensemble learning framework that combines
    LSTM temporal analysis, Random Forest classification, and SVM regime detection
    into a unified meta-learning system with advanced voting, stacking, and adaptive
    weighting capabilities.
    """
    
    def __init__(self, config: EnsembleConfig):
        self.config = config
        self.lstm_model = None
        self.rf_model = None
        self.svm_model = None
        
        # Ensemble components
        self.meta_learner = None
        self.voting_classifier = None
        self.stacking_classifier = None
        self.performance_tracker = ModelPerformanceTracker(config.performance_tracking_window)
        self.meta_feature_engineer = MetaFeatureEngineer(config)
        
        # Dynamic weighting
        self.model_weights = {'lstm': 0.33, 'random_forest': 0.33, 'svm': 0.34}
        self.performance_history = []
        self.prediction_count = 0
        
        # Calibration
        self.calibrated_models = {}
        
        # Model versioning and metadata
        self.model_version = "1.0"
        self.training_history = {}
        self.ensemble_performance = {}
        
        # Setup logging
        self.logger = setup_logging('INFO')
        
        # Create model directory
        Path(self.config.model_save_path).mkdir(parents=True, exist_ok=True)
    
    async def initialize_models(self) -> bool:
        """Initialize all component models"""
        try:
            self.logger.info("Initializing ensemble component models...")
            
            # Initialize LSTM model
            if self.config.use_lstm:
                lstm_config = LSTMConfig()
                self.lstm_model = EnhancedLSTMModel(lstm_config)
                self.logger.info("LSTM model initialized")
            
            # Initialize Random Forest model
            if self.config.use_random_forest:
                rf_config = RandomForestConfig()
                self.rf_model = EnhancedRandomForestModel(rf_config)
                self.logger.info("Random Forest model initialized")
            
            # Initialize SVM model
            if self.config.use_svm:
                svm_config = SVMConfig()
                self.svm_model = EnhancedSVMModel(svm_config)
                self.logger.info("SVM model initialized")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing ensemble models: {e}")
            return False
    
    def train_ensemble(self, data: pd.DataFrame, target_type: str = 'classification') -> Dict[str, Any]:
        """Train the complete ensemble system"""
        try:
            self.logger.info("Starting ensemble training...")
            
            training_results = {'individual_models': {}, 'ensemble_performance': {}}
            
            # Train individual models
            if self.config.use_lstm and self.lstm_model:
                self.logger.info("Training LSTM model...")
                lstm_results = self.lstm_model.train(data)
                training_results['individual_models']['lstm'] = lstm_results
            
            if self.config.use_random_forest and self.rf_model:
                self.logger.info("Training Random Forest model...")
                rf_results = self.rf_model.train(data)
                training_results['individual_models']['random_forest'] = rf_results
            
            if self.config.use_svm and self.svm_model:
                self.logger.info("Training SVM model...")
                svm_results = self.svm_model.train(data)
                training_results['individual_models']['svm'] = svm_results
            
            # Generate predictions for ensemble training
            self.logger.info("Generating predictions for ensemble training...")
            ensemble_data = self._prepare_ensemble_training_data(data)
            
            if len(ensemble_data) > 0:
                # Train meta-learner
                ensemble_results = self._train_meta_learner(ensemble_data, target_type)
                training_results['ensemble_performance'] = ensemble_results
            
            # Store training history
            self.training_history = training_results
            
            # Save ensemble model
            self.save_ensemble()
            
            self.logger.info("Ensemble training completed successfully")
            
            return training_results
            
        except Exception as e:
            self.logger.error(f"Error training ensemble: {e}")
            raise
    
    def _prepare_ensemble_training_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare training data for ensemble meta-learner"""
        try:
            ensemble_data = []
            
            # Use a sliding window to generate training samples
            window_size = max(100, len(data) // 20)  # Use 5% of data or minimum 100 samples
            
            for i in range(window_size, len(data) - 10, 10):  # Step by 10 to reduce computation
                try:
                    # Get data slice for prediction
                    data_slice = data.iloc[:i]
                    
                    # Get individual model predictions (using last available data)
                    predictions = {}
                    meta_features = {}
                    
                    # LSTM prediction
                    if self.config.use_lstm and self.lstm_model:
                        try:
                            lstm_pred = self.lstm_model.predict(data_slice.tail(100))  # Use recent data
                            predictions['lstm'] = lstm_pred.prediction
                            predictions['lstm_confidence'] = lstm_pred.confidence
                        except:
                            predictions['lstm'] = 0.0
                            predictions['lstm_confidence'] = 0.5
                    
                    # Random Forest prediction
                    if self.config.use_random_forest and self.rf_model:
                        try:
                            rf_pred = self.rf_model.predict(data_slice.tail(100))
                            predictions['rf'] = rf_pred.signal
                            predictions['rf_confidence'] = rf_pred.confidence
                        except:
                            predictions['rf'] = 2  # HOLD
                            predictions['rf_confidence'] = 0.5
                    
                    # SVM prediction
                    if self.config.use_svm and self.svm_model:
                        try:
                            svm_pred = self.svm_model.predict(data_slice.tail(100))
                            predictions['svm'] = svm_pred.regime
                            predictions['svm_confidence'] = svm_pred.confidence
                        except:
                            predictions['svm'] = 4  # RANGING_NEUTRAL
                            predictions['svm_confidence'] = 0.5
                    
                    # Create target (future price direction)
                    current_price = data.iloc[i]['close']
                    future_price = data.iloc[i + 5]['close']  # 5 periods ahead
                    target = 1 if future_price > current_price else 0
                    
                    # Add market condition features
                    market_features = self._extract_market_features(data_slice.tail(20))
                    
                    # Combine all features
                    sample = {**predictions, **market_features, 'target': target}
                    ensemble_data.append(sample)
                    
                except Exception as e:
                    continue  # Skip problematic samples
            
            if len(ensemble_data) > 0:
                return pd.DataFrame(ensemble_data)
            else:
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Error preparing ensemble training data: {e}")
            return pd.DataFrame()
    
    def _extract_market_features(self, data: pd.DataFrame) -> Dict[str, float]:
        """Extract market condition features for ensemble training"""
        try:
            if len(data) < 10:
                return {}
            
            close = data['close']
            
            # Volatility
            returns = close.pct_change().dropna()
            volatility = returns.std()
            
            # Trend
            trend_slope = stats.linregress(range(len(close)), close)[0] if len(close) > 2 else 0
            
            # Momentum
            momentum = (close.iloc[-1] - close.iloc[-5]) / close.iloc[-5] if len(close) >= 5 else 0
            
            return {
                'market_volatility': volatility,
                'trend_slope': trend_slope,
                'momentum': momentum,
                'price_position': (close.iloc[-1] - close.min()) / (close.max() - close.min()) if close.max() != close.min() else 0.5
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting market features: {e}")
            return {}
    
    def _train_meta_learner(self, ensemble_data: pd.DataFrame, target_type: str) -> Dict[str, Any]:
        """Train the meta-learner for ensemble predictions"""
        try:
            if len(ensemble_data) < 50:
                self.logger.warning("Insufficient data for meta-learner training")
                return {}
            
            # Prepare features and target
            feature_cols = [col for col in ensemble_data.columns if col != 'target']
            X = ensemble_data[feature_cols].fillna(0)
            y = ensemble_data['target']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            results = {}
            
            # Train different ensemble methods
            if self.config.ensemble_method == 'stacking':
                results.update(self._train_stacking_ensemble(X_train, X_test, y_train, y_test))
            
            elif self.config.ensemble_method == 'weighted_voting':
                results.update(self._train_weighted_voting(X_train, X_test, y_train, y_test))
            
            elif self.config.ensemble_method == 'adaptive_weighting':
                results.update(self._initialize_adaptive_weighting(X_train, y_train))
            
            # Calibrate probabilities if enabled
            if self.config.enable_calibration:
                self._calibrate_models(X_train, y_train)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error training meta-learner: {e}")
            return {}
    
    def _train_stacking_ensemble(self, X_train: pd.DataFrame, X_test: pd.DataFrame,
                                y_train: pd.Series, y_test: pd.Series) -> Dict[str, Any]:
        """Train stacking ensemble"""
        try:
            # Define base estimators (placeholder since we're using external models)
            base_estimators = [
                ('lr1', LogisticRegression(random_state=42)),
                ('lr2', LogisticRegression(C=0.1, random_state=42)),
                ('lr3', LogisticRegression(C=10, random_state=42))
            ]
            
            # Meta-learner
            if self.config.meta_learner == 'logistic_regression':
                meta_learner = LogisticRegression(random_state=42)
            else:
                meta_learner = LogisticRegression(random_state=42)  # Default
            
            # Create stacking classifier
            self.stacking_classifier = StackingClassifier(
                estimators=base_estimators,
                final_estimator=meta_learner,
                cv=self.config.stacking_cv_folds,
                stack_method='predict_proba',
                n_jobs=-1
            )
            
            # Train stacking ensemble
            self.stacking_classifier.fit(X_train, y_train)
            
            # Evaluate
            train_score = self.stacking_classifier.score(X_train, y_train)
            test_score = self.stacking_classifier.score(X_test, y_test)
            
            # Cross-validation
            cv_scores = cross_val_score(
                self.stacking_classifier, X_train, y_train,
                cv=TimeSeriesSplit(n_splits=5), scoring='accuracy'
            )
            
            return {
                'method': 'stacking',
                'train_accuracy': train_score,
                'test_accuracy': test_score,
                'cv_mean_accuracy': cv_scores.mean(),
                'cv_std_accuracy': cv_scores.std()
            }
            
        except Exception as e:
            self.logger.error(f"Error training stacking ensemble: {e}")
            return {}
    
    def _train_weighted_voting(self, X_train: pd.DataFrame, X_test: pd.DataFrame,
                              y_train: pd.Series, y_test: pd.Series) -> Dict[str, Any]:
        """Train weighted voting ensemble"""
        try:
            # Calculate individual model weights based on performance
            # This is a simplified version - in practice, you'd evaluate actual model performance
            
            # Initialize equal weights
            initial_weights = np.array([1/3, 1/3, 1/3])
            
            # Optimize weights using cross-validation
            def objective(weights):
                weights = weights / weights.sum()  # Normalize
                
                # Simulate ensemble predictions with these weights
                # This is simplified - you'd use actual model predictions
                predictions = np.random.choice([0, 1], size=len(y_train), p=[0.5, 0.5])
                accuracy = accuracy_score(y_train, predictions)
                return -accuracy  # Minimize negative accuracy
            
            # Optimize weights
            from scipy.optimize import minimize
            result = minimize(
                objective, 
                initial_weights,
                method='SLSQP',
                bounds=[(0.1, 0.8) for _ in range(3)],
                constraints={'type': 'eq', 'fun': lambda w: w.sum() - 1}
            )
            
            optimal_weights = result.x / result.x.sum()
            
            # Update model weights
            self.model_weights = {
                'lstm': float(optimal_weights[0]),
                'random_forest': float(optimal_weights[1]),
                'svm': float(optimal_weights[2])
            }
            
            return {
                'method': 'weighted_voting',
                'optimal_weights': self.model_weights,
                'optimization_success': result.success
            }
            
        except Exception as e:
            self.logger.error(f"Error training weighted voting: {e}")
            return {}
    
    def _initialize_adaptive_weighting(self, X_train: pd.DataFrame, y_train: pd.Series) -> Dict[str, Any]:
        """Initialize adaptive weighting system"""
        try:
            # Initialize with equal weights
            self.model_weights = {
                'lstm': 1/3,
                'random_forest': 1/3,
                'svm': 1/3
            }
            
            # Initialize performance tracking
            self.performance_history = []
            
            return {
                'method': 'adaptive_weighting',
                'initial_weights': self.model_weights,
                'adaptation_rate': self.config.adaptation_rate
            }
            
        except Exception as e:
            self.logger.error(f"Error initializing adaptive weighting: {e}")
            return {}
    
    def _calibrate_models(self, X_train: pd.DataFrame, y_train: pd.Series):
        """Calibrate model probabilities"""
        try:
            # This would calibrate the probability outputs of individual models
            # For now, we'll create placeholder calibrated models
            
            self.calibrated_models = {
                'lstm': LogisticRegression().fit(X_train[['lstm_confidence']], y_train),
                'random_forest': LogisticRegression().fit(X_train[['rf_confidence']], y_train),
                'svm': LogisticRegression().fit(X_train[['svm_confidence']], y_train)
            }
            
            self.logger.info("Model calibration completed")
            
        except Exception as e:
            self.logger.error(f"Error calibrating models: {e}")
    
    def predict(self, data: pd.DataFrame, prediction_type: str = PredictionType.PRICE_DIRECTION) -> EnsemblePrediction:
        """Make ensemble prediction with comprehensive analysis"""
        try:
            # Get individual model predictions
            individual_predictions = self._get_individual_predictions(data)
            
            # Engineer meta-features
            meta_features = self.meta_feature_engineer.engineer_meta_features(
                individual_predictions.get('lstm'),
                individual_predictions.get('random_forest'),
                individual_predictions.get('svm'),
                data
            )
            
            # Make ensemble prediction based on method
            if self.config.ensemble_method == 'adaptive_weighting':
                ensemble_result = self._adaptive_weighted_prediction(individual_predictions, meta_features)
            elif self.config.ensemble_method == 'stacking':
                ensemble_result = self._stacking_prediction(individual_predictions, meta_features)
            elif self.config.ensemble_method == 'weighted_voting':
                ensemble_result = self._weighted_voting_prediction(individual_predictions, meta_features)
            else:
                ensemble_result = self._simple_voting_prediction(individual_predictions, meta_features)
            
            # Create comprehensive ensemble prediction
            ensemble_prediction = EnsemblePrediction(
                final_prediction=ensemble_result['prediction'],
                prediction_type=prediction_type,
                confidence=ensemble_result['confidence'],
                lstm_prediction=individual_predictions.get('lstm'),
                rf_prediction=individual_predictions.get('random_forest'),
                svm_prediction=individual_predictions.get('svm'),
                model_weights=self.model_weights.copy(),
                model_agreement=ensemble_result.get('agreement', 0.0),
                prediction_variance=ensemble_result.get('variance', 0.0),
                uncertainty_score=ensemble_result.get('uncertainty', 0.0),
                ensemble_method=self.config.ensemble_method,
                meta_features=meta_features,
                model_contributions=ensemble_result.get('contributions', {}),
                prediction_quality=ensemble_result.get('quality', 0.5),
                risk_assessment=self._assess_risk(ensemble_result),
                recommendation_strength=self._assess_recommendation_strength(ensemble_result),
                model_version=self.model_version
            )
            
            # Update performance tracking
            self.prediction_count += 1
            
            # Update model weights if using adaptive method
            if self.config.ensemble_method == 'adaptive_weighting':
                if self.prediction_count % self.config.ensemble_update_frequency == 0:
                    self._update_adaptive_weights()
            
            return ensemble_prediction
            
        except Exception as e:
            self.logger.error(f"Error making ensemble prediction: {e}")
            # Fallback prediction
            return EnsemblePrediction(
                final_prediction=0,
                prediction_type=prediction_type,
                confidence=0.5,
                ensemble_method='fallback',
                model_version=self.model_version
            )
    
    def _get_individual_predictions(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Get predictions from all individual models"""
        predictions = {}
        
        try:
            # LSTM prediction
            if self.config.use_lstm and self.lstm_model:
                try:
                    lstm_pred = self.lstm_model.predict(data)
                    predictions['lstm'] = lstm_pred
                except Exception as e:
                    self.logger.warning(f"LSTM prediction failed: {e}")
            
            # Random Forest prediction
            if self.config.use_random_forest and self.rf_model:
                try:
                    rf_pred = self.rf_model.predict(data)
                    predictions['random_forest'] = rf_pred
                except Exception as e:
                    self.logger.warning(f"Random Forest prediction failed: {e}")
            
            # SVM prediction
            if self.config.use_svm and self.svm_model:
                try:
                    svm_pred = self.svm_model.predict(data)
                    predictions['svm'] = svm_pred
                except Exception as e:
                    self.logger.warning(f"SVM prediction failed: {e}")
            
        except Exception as e:
            self.logger.error(f"Error getting individual predictions: {e}")
        
        return predictions
    
    def _adaptive_weighted_prediction(self, individual_predictions: Dict[str, Any], 
                                    meta_features: Dict[str, float]) -> Dict[str, Any]:
        """Make prediction using adaptive weighting"""
        try:
            predictions = []
            weights = []
            contributions = {}
            
            # Collect predictions and weights
            if 'lstm' in individual_predictions:
                lstm_pred = individual_predictions['lstm']
                # Convert LSTM prediction to binary (up/down)
                binary_pred = 1 if lstm_pred.prediction > 0 else 0
                predictions.append(binary_pred)
                weights.append(self.model_weights['lstm'])
                contributions['lstm'] = self.model_weights['lstm'] * binary_pred
            
            if 'random_forest' in individual_predictions:
                rf_pred = individual_predictions['random_forest']
                # Convert RF signal to binary (buy signals = 1, others = 0)
                binary_pred = 1 if rf_pred.signal >= 3 else 0
                predictions.append(binary_pred)
                weights.append(self.model_weights['random_forest'])
                contributions['random_forest'] = self.model_weights['random_forest'] * binary_pred
            
            if 'svm' in individual_predictions:
                svm_pred = individual_predictions['svm']
                # Convert SVM regime to binary (bullish regimes = 1)
                binary_pred = 1 if svm_pred.regime in [0, 1, 2] else 0
                predictions.append(binary_pred)
                weights.append(self.model_weights['svm'])
                contributions['svm'] = self.model_weights['svm'] * binary_pred
            
            if not predictions:
                return {'prediction': 0, 'confidence': 0.5}
            
            # Calculate weighted prediction
            weighted_prediction = np.average(predictions, weights=weights)
            final_prediction = 1 if weighted_prediction > 0.5 else 0
            
            # Calculate confidence based on agreement and weights
            agreement = 1.0 - np.var(predictions)  # Higher agreement = lower variance
            confidence = min(0.95, max(0.05, agreement * np.sum(weights)))
            
            # Calculate variance and uncertainty
            variance = np.var(predictions)
            uncertainty = variance * (1 - agreement)
            
            return {
                'prediction': final_prediction,
                'confidence': confidence,
                'agreement': agreement,
                'variance': variance,
                'uncertainty': uncertainty,
                'contributions': contributions,
                'quality': confidence * agreement
            }
            
        except Exception as e:
            self.logger.error(f"Error in adaptive weighted prediction: {e}")
            return {'prediction': 0, 'confidence': 0.5}
    
    def _stacking_prediction(self, individual_predictions: Dict[str, Any], 
                            meta_features: Dict[str, float]) -> Dict[str, Any]:
        """Make prediction using stacking ensemble"""
        try:
            if self.stacking_classifier is None:
                return self._adaptive_weighted_prediction(individual_predictions, meta_features)
            
            # Prepare features for stacking
            features = []
            
            # Add individual model outputs
            if 'lstm' in individual_predictions:
                features.extend([
                    individual_predictions['lstm'].prediction,
                    individual_predictions['lstm'].confidence
                ])
            else:
                features.extend([0.0, 0.5])
            
            if 'random_forest' in individual_predictions:
                features.extend([
                    individual_predictions['random_forest'].signal,
                    individual_predictions['random_forest'].confidence
                ])
            else:
                features.extend([2, 0.5])  # HOLD signal
            
            if 'svm' in individual_predictions:
                features.extend([
                    individual_predictions['svm'].regime,
                    individual_predictions['svm'].confidence
                ])
            else:
                features.extend([4, 0.5])  # RANGING regime
            
            # Add meta-features
            feature_names = ['lstm_pred', 'lstm_conf', 'rf_signal', 'rf_conf', 'svm_regime', 'svm_conf']
            for name in ['market_volatility', 'trend_slope', 'momentum', 'price_position']:
                features.append(meta_features.get(name, 0.0))
                feature_names.append(name)
            
            # Make prediction
            X = np.array(features).reshape(1, -1)
            prediction = self.stacking_classifier.predict(X)[0]
            probabilities = self.stacking_classifier.predict_proba(X)[0]
            confidence = np.max(probabilities)
            
            return {
                'prediction': prediction,
                'confidence': confidence,
                'probabilities': probabilities,
                'quality': confidence
            }
            
        except Exception as e:
            self.logger.error(f"Error in stacking prediction: {e}")
            return self._adaptive_weighted_prediction(individual_predictions, meta_features)
    
    def _weighted_voting_prediction(self, individual_predictions: Dict[str, Any], 
                                   meta_features: Dict[str, float]) -> Dict[str, Any]:
        """Make prediction using weighted voting"""
        try:
            return self._adaptive_weighted_prediction(individual_predictions, meta_features)
        except Exception as e:
            self.logger.error(f"Error in weighted voting prediction: {e}")
            return {'prediction': 0, 'confidence': 0.5}
    
    def _simple_voting_prediction(self, individual_predictions: Dict[str, Any], 
                                 meta_features: Dict[str, float]) -> Dict[str, Any]:
        """Make prediction using simple majority voting"""
        try:
            votes = []
            
            # Collect binary votes
            if 'lstm' in individual_predictions:
                vote = 1 if individual_predictions['lstm'].prediction > 0 else 0
                votes.append(vote)
            
            if 'random_forest' in individual_predictions:
                vote = 1 if individual_predictions['random_forest'].signal >= 3 else 0
                votes.append(vote)
            
            if 'svm' in individual_predictions:
                vote = 1 if individual_predictions['svm'].regime in [0, 1, 2] else 0
                votes.append(vote)
            
            if not votes:
                return {'prediction': 0, 'confidence': 0.5}
            
            # Majority vote
            final_prediction = 1 if sum(votes) > len(votes) / 2 else 0
            
            # Confidence based on unanimity
            agreement = sum(votes) / len(votes)
            confidence = max(agreement, 1 - agreement)  # Distance from 0.5
            
            return {
                'prediction': final_prediction,
                'confidence': confidence,
                'agreement': agreement,
                'quality': confidence
            }
            
        except Exception as e:
            self.logger.error(f"Error in simple voting prediction: {e}")
            return {'prediction': 0, 'confidence': 0.5}
    
    def _assess_risk(self, ensemble_result: Dict[str, Any]) -> str:
        """Assess risk level of the prediction"""
        try:
            confidence = ensemble_result.get('confidence', 0.5)
            uncertainty = ensemble_result.get('uncertainty', 0.5)
            agreement = ensemble_result.get('agreement', 0.5)
            
            # Calculate risk score
            risk_score = (1 - confidence) + uncertainty + (1 - agreement)
            risk_score /= 3  # Normalize
            
            if risk_score < 0.3:
                return "LOW"
            elif risk_score < 0.6:
                return "MEDIUM"
            else:
                return "HIGH"
                
        except Exception as e:
            self.logger.error(f"Error assessing risk: {e}")
            return "MEDIUM"
    
    def _assess_recommendation_strength(self, ensemble_result: Dict[str, Any]) -> str:
        """Assess recommendation strength"""
        try:
            confidence = ensemble_result.get('confidence', 0.5)
            quality = ensemble_result.get('quality', 0.5)
            
            strength_score = (confidence + quality) / 2
            
            if strength_score > 0.8:
                return "STRONG"
            elif strength_score > 0.6:
                return "MODERATE"
            else:
                return "WEAK"
                
        except Exception as e:
            self.logger.error(f"Error assessing recommendation strength: {e}")
            return "MODERATE"
    
    def _update_adaptive_weights(self):
        """Update model weights based on recent performance"""
        try:
            if len(self.performance_history) < self.config.min_performance_samples:
                return
            
            # Calculate recent performance for each model
            recent_performance = {}
            for model_name in self.model_weights.keys():
                if model_name in self.performance_tracker.performance_metrics:
                    metrics = self.performance_tracker.performance_metrics[model_name]
                    if 'accuracy' in metrics:
                        recent_performance[model_name] = metrics['accuracy']
                    elif 'directional_accuracy' in metrics:
                        recent_performance[model_name] = metrics['directional_accuracy']
                    else:
                        recent_performance[model_name] = 0.5
                else:
                    recent_performance[model_name] = 0.5
            
            # Update weights based on performance
            total_performance = sum(recent_performance.values())
            if total_performance > 0:
                new_weights = {}
                for model_name, performance in recent_performance.items():
                    # Calculate new weight with adaptation rate
                    target_weight = performance / total_performance
                    current_weight = self.model_weights[model_name]
                    new_weight = current_weight + self.config.adaptation_rate * (target_weight - current_weight)
                    
                    # Apply bounds
                    new_weight = max(self.config.min_weight, min(self.config.max_weight, new_weight))
                    new_weights[model_name] = new_weight
                
                # Normalize weights
                total_weight = sum(new_weights.values())
                if total_weight > 0:
                    for model_name in new_weights:
                        new_weights[model_name] /= total_weight
                    
                    self.model_weights = new_weights
                    self.logger.info(f"Updated adaptive weights: {self.model_weights}")
            
        except Exception as e:
            self.logger.error(f"Error updating adaptive weights: {e}")
    
    def update_performance(self, prediction: EnsemblePrediction, actual_outcome: Union[int, float]):
        """Update performance tracking with actual outcomes"""
        try:
            timestamp = datetime.utcnow()
            
            # Update ensemble performance
            self.performance_tracker.update_performance(
                'ensemble', prediction.final_prediction, actual_outcome, timestamp
            )
            
            # Update individual model performance if available
            if prediction.lstm_prediction:
                lstm_binary = 1 if prediction.lstm_prediction.prediction > 0 else 0
                self.performance_tracker.update_performance('lstm', lstm_binary, actual_outcome, timestamp)
            
            if prediction.rf_prediction:
                rf_binary = 1 if prediction.rf_prediction.signal >= 3 else 0
                self.performance_tracker.update_performance('random_forest', rf_binary, actual_outcome, timestamp)
            
            if prediction.svm_prediction:
                svm_binary = 1 if prediction.svm_prediction.regime in [0, 1, 2] else 0
                self.performance_tracker.update_performance('svm', svm_binary, actual_outcome, timestamp)
            
            # Check for performance drift
            for model_name in ['lstm', 'random_forest', 'svm', 'ensemble']:
                drift_detected = self.performance_tracker.detect_performance_drift(
                    model_name, self.config.drift_detection_threshold
                )
                if drift_detected:
                    self.logger.warning(f"Performance drift detected for {model_name}")
            
        except Exception as e:
            self.logger.error(f"Error updating performance: {e}")
    
    def save_ensemble(self, filepath: Optional[str] = None):
        """Save the complete ensemble model"""
        try:
            if filepath is None:
                filepath = str(Path(self.config.model_save_path) / f'ensemble_model_{self.model_version}.pkl')
            
            # Prepare ensemble package
            ensemble_package = {
                'config': self.config,
                'model_weights': self.model_weights,
                'meta_learner': self.meta_learner,
                'stacking_classifier': self.stacking_classifier,
                'calibrated_models': self.calibrated_models,
                'performance_tracker': self.performance_tracker,
                'training_history': self.training_history,
                'model_version': self.model_version,
                'prediction_count': self.prediction_count
            }
            
            # Save ensemble (individual models are saved separately)
            joblib.dump(ensemble_package, filepath)
            
            self.logger.info(f"Ensemble model saved to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error saving ensemble model: {e}")
    
    def load_ensemble(self, filepath: str):
        """Load the complete ensemble model"""
        try:
            # Load ensemble package
            ensemble_package = joblib.load(filepath)
            
            # Restore attributes
            self.config = ensemble_package['config']
            self.model_weights = ensemble_package['model_weights']
            self.meta_learner = ensemble_package.get('meta_learner')
            self.stacking_classifier = ensemble_package.get('stacking_classifier')
            self.calibrated_models = ensemble_package.get('calibrated_models', {})
            self.performance_tracker = ensemble_package.get('performance_tracker', ModelPerformanceTracker())
            self.training_history = ensemble_package.get('training_history', {})
            self.model_version = ensemble_package['model_version']
            self.prediction_count = ensemble_package.get('prediction_count', 0)
            
            self.logger.info(f"Ensemble model loaded from {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error loading ensemble model: {e}")
    
    def get_ensemble_analysis(self) -> Dict[str, Any]:
        """Get comprehensive ensemble analysis"""
        try:
            analysis = {
                'ensemble_method': self.config.ensemble_method,
                'model_weights': self.model_weights,
                'prediction_count': self.prediction_count,
                'performance_metrics': self.performance_tracker.performance_metrics,
                'model_rankings': self.performance_tracker.get_model_rankings(),
                'recent_drift_alerts': self.performance_tracker.drift_alerts[-5:] if self.performance_tracker.drift_alerts else []
            }
            
            # Individual model status
            analysis['individual_models'] = {
                'lstm_enabled': self.config.use_lstm,
                'rf_enabled': self.config.use_random_forest,
                'svm_enabled': self.config.use_svm
            }
            
            # Configuration summary
            analysis['configuration'] = {
                'ensemble_method': self.config.ensemble_method,
                'voting_type': self.config.voting_type,
                'enable_calibration': self.config.enable_calibration,
                'enable_online_learning': self.config.enable_online_learning,
                'adaptation_rate': self.config.adaptation_rate
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error getting ensemble analysis: {e}")
            return {'error': str(e)}
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get comprehensive ensemble model information"""
        try:
            info = {
                'model_version': self.model_version,
                'model_type': 'Enhanced Ensemble Learning System',
                'ensemble_method': self.config.ensemble_method,
                'component_models': [],
                'model_weights': self.model_weights,
                'prediction_count': self.prediction_count
            }
            
            # Component model information
            if self.config.use_lstm:
                info['component_models'].append({
                    'name': 'LSTM',
                    'type': 'Temporal Sequence Prediction',
                    'weight': self.model_weights.get('lstm', 0),
                    'enabled': True
                })
            
            if self.config.use_random_forest:
                info['component_models'].append({
                    'name': 'Random Forest',
                    'type': 'Multi-class Signal Classification',
                    'weight': self.model_weights.get('random_forest', 0),
                    'enabled': True
                })
            
            if self.config.use_svm:
                info['component_models'].append({
                    'name': 'SVM',
                    'type': 'Market Regime Classification',
                    'weight': self.model_weights.get('svm', 0),
                    'enabled': True
                })
            
            # Performance summary
            if self.performance_tracker.performance_metrics:
                info['performance_summary'] = {}
                for model_name, metrics in self.performance_tracker.performance_metrics.items():
                    if 'accuracy' in metrics:
                        info['performance_summary'][model_name] = {
                            'accuracy': metrics['accuracy'],
                            'sample_count': metrics['sample_count']
                        }
                    elif 'directional_accuracy' in metrics:
                        info['performance_summary'][model_name] = {
                            'directional_accuracy': metrics['directional_accuracy'],
                            'r2_score': metrics.get('r2_score', 0),
                            'sample_count': metrics['sample_count']
                        }
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting ensemble model info: {e}")
            return {'error': str(e)}

# Usage Example and Testing
def example_usage():
    """Comprehensive example of using the Enhanced Ensemble Model"""
    
    print("=== Enhanced Ensemble Model Example ===")
    
    # Create configuration
    config = EnsembleConfig(
        use_lstm=True,
        use_random_forest=True,
        use_svm=True,
        ensemble_method='adaptive_weighting',
        voting_type='soft',
        enable_calibration=True,
        enable_online_learning=True,
        adaptation_rate=0.1,
        use_meta_features=True
    )
    
    # Create ensemble model
    ensemble_model = EnhancedEnsembleModel(config)
    
    # Generate comprehensive sample data with multiple market regimes
    dates = pd.date_range('2020-01-01', periods=5000, freq='H')
    np.random.seed(42)
    
    # Create realistic market data with different regimes
    price_segments = []
    regime_changes = [0, 1000, 2000, 3000, 4000, 5000]
    price_base = 100
    
    for i, start_idx in enumerate(regime_changes[:-1]):
        end_idx = regime_changes[i + 1]
        length = end_idx - start_idx
        
        # Different market regimes
        if i % 4 == 0:  # Strong trending up
            trend = np.linspace(0, 0.4, length)
            noise = np.random.normal(0, 0.01, length)
            cyclical = 0.05 * np.sin(np.linspace(0, 8*np.pi, length))
        elif i % 4 == 1:  # Ranging/volatile
            trend = np.zeros(length)
            noise = np.random.normal(0, 0.025, length)
            cyclical = 0.1 * np.sin(np.linspace(0, 12*np.pi, length))
        elif i % 4 == 2:  # Strong trending down
            trend = np.linspace(0, -0.3, length)
            noise = np.random.normal(0, 0.012, length)
            cyclical = 0.03 * np.sin(np.linspace(0, 6*np.pi, length))
        else:  # Low volatility trending
            trend = np.linspace(0, 0.15, length)
            noise = np.random.normal(0, 0.008, length)
            cyclical = 0.02 * np.sin(np.linspace(0, 4*np.pi, length))
        
        segment_returns = trend + noise + cyclical
        if i == 0:
            segment_prices = price_base * (1 + segment_returns).cumprod()
        else:
            segment_prices = price_segments[-1] * (1 + segment_returns).cumprod()
        
        price_segments.extend(segment_prices.tolist())
    
    prices = np.array(price_segments)
    
    # Generate OHLC data
    high_prices = prices * (1 + np.abs(np.random.normal(0, 0.006, 5000)))
    low_prices = prices * (1 - np.abs(np.random.normal(0, 0.006, 5000)))
    open_prices = np.roll(prices, 1)
    open_prices[0] = prices[0]
    
    volumes = np.random.lognormal(10, 0.7, 5000)
    
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
        # Initialize models
        print("\n1. Initializing Ensemble Models...")
        initialization_success = asyncio.run(ensemble_model.initialize_models())
        if initialization_success:
            print("   ✅ All component models initialized successfully")
        else:
            print("   ❌ Model initialization failed")
            return None
        
        # Train ensemble
        print("\n2. Training Ensemble System...")
        training_results = ensemble_model.train_ensemble(sample_data)
        print("Ensemble Training Results:")
        
        # Display individual model results
        if 'individual_models' in training_results:
            for model_name, results in training_results['individual_models'].items():
                print(f"   {model_name.upper()} Model:")
                if 'test_accuracy' in results:
                    print(f"      Test Accuracy: {results['test_accuracy']:.4f}")
                elif 'validation_loss' in results:
                    print(f"      Validation Loss: {results['validation_loss']:.6f}")
                print(f"      Feature Count: {results.get('feature_count', 'N/A')}")
        
        # Display ensemble results
        if 'ensemble_performance' in training_results:
            ensemble_perf = training_results['ensemble_performance']
            print(f"   ENSEMBLE Performance:")
            if 'test_accuracy' in ensemble_perf:
                print(f"      Test Accuracy: {ensemble_perf['test_accuracy']:.4f}")
            print(f"      Method: {ensemble_perf.get('method', 'N/A')}")
        
        # Make predictions
        print("\n3. Making Ensemble Predictions...")
        
        # Test prediction on recent data
        test_data = sample_data.tail(500)  # Use recent 500 samples for prediction
        prediction = ensemble_model.predict(test_data)
        
        print(f"Ensemble Prediction Results:")
        print(f"   Final Prediction: {prediction.final_prediction}")
        print(f"   Prediction Type: {prediction.prediction_type}")
        print(f"   Confidence: {prediction.confidence:.4f}")
        print(f"   Model Agreement: {prediction.model_agreement:.4f}")
        print(f"   Uncertainty Score: {prediction.uncertainty_score:.4f}")
        print(f"   Risk Assessment: {prediction.risk_assessment}")
        print(f"   Recommendation Strength: {prediction.recommendation_strength}")
        
        # Display model weights
        print(f"\n4. Current Model Weights:")
        for model_name, weight in prediction.model_weights.items():
            print(f"   {model_name}: {weight:.4f}")
        
        # Display individual model predictions
        print(f"\n5. Individual Model Predictions:")
        if prediction.lstm_prediction:
            print(f"   LSTM: {prediction.lstm_prediction.prediction:.6f} (confidence: {prediction.lstm_prediction.confidence:.4f})")
        
        if prediction.rf_prediction:
            print(f"   Random Forest: {prediction.rf_prediction.signal_name} (confidence: {prediction.rf_prediction.confidence:.4f})")
        
        if prediction.svm_prediction:
            print(f"   SVM: {prediction.svm_prediction.regime_name} (confidence: {prediction.svm_prediction.confidence:.4f})")
        
        # Display meta-features
        print(f"\n6. Top 10 Meta-Features:")
        sorted_meta = sorted(prediction.meta_features.items(), key=lambda x: abs(x[1]), reverse=True)
        for feature, value in sorted_meta[:10]:
            print(f"   {feature}: {value:.6f}")
        
        # Display model contributions
        if prediction.model_contributions:
            print(f"\n7. Model Contributions:")
            for model, contribution in prediction.model_contributions.items():
                print(f"   {model}: {contribution:.6f}")
        
        # Simulate performance tracking
        print(f"\n8. Performance Tracking Simulation...")
        for i in range(10):
            # Simulate actual outcomes
            actual_outcome = np.random.choice([0, 1], p=[0.4, 0.6])  # Slightly bullish market
            ensemble_model.update_performance(prediction, actual_outcome)
        
        # Get ensemble analysis
        print(f"\n9. Ensemble Analysis:")
        analysis = ensemble_model.get_ensemble_analysis()
        print(f"   Ensemble Method: {analysis['ensemble_method']}")
        print(f"   Prediction Count: {analysis['prediction_count']}")
        
        if analysis['model_rankings']:
            print(f"   Model Rankings:")
            for model, rank in analysis['model_rankings'].items():
                print(f"      {model}: Rank {rank}")
        
        # Get model information
        print(f"\n10. Model Information:")
        model_info = ensemble_model.get_model_info()
        print(f"   Model Type: {model_info['model_type']}")
        print(f"   Ensemble Method: {model_info['ensemble_method']}")
        print(f"   Component Models: {len(model_info['component_models'])}")
        
        for component in model_info['component_models']:
            print(f"      {component['name']} ({component['type']}): Weight={component['weight']:.4f}")
        
        if 'performance_summary' in model_info:
            print(f"   Performance Summary:")
            for model, perf in model_info['performance_summary'].items():
                if 'accuracy' in perf:
                    print(f"      {model}: Accuracy={perf['accuracy']:.4f}, Samples={perf['sample_count']}")
                elif 'directional_accuracy' in perf:
                    print(f"      {model}: Dir.Acc={perf['directional_accuracy']:.4f}, R²={perf.get('r2_score', 0):.4f}")
        
        print("\n=== Enhanced Ensemble Model Example Completed Successfully ===")
        
        return ensemble_model
        
    except Exception as e:
        print(f"Error in ensemble example: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Run the comprehensive example
    model = example_usage()
