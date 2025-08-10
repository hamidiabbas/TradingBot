"""
ML Training Configuration
========================
Enterprise training configuration management
"""

import os
from typing import Dict, Any

class TrainingConfig:
    """Centralized training configuration"""
    
    # Data Configuration
    DATA_FILE_PATH = "data/training/mt5_historical_data.h5"
    MAX_SAMPLES = 75000
    MAX_SAMPLES_PER_DATASET = 12000
    
    # Feature Engineering
    LOOKBACK_WINDOW = 60
    FEATURE_COUNT = 28
    NORMALIZATION = "standard"
    
    # Model Configuration
    MODELS_TO_TRAIN = ['random_forest', 'lstm', 'svm', 'ensemble']
    MODEL_DIRECTORY = 'models/enterprise'
    SAVE_MODELS = True
    
    # Training Parameters
    TEST_SIZE = 0.3
    RANDOM_STATE = 42
    CROSS_VALIDATION_FOLDS = 5
    
    # Performance Thresholds
    MIN_ACCURACY = 0.55
    MAX_OVERFITTING_GAP = 0.10
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Get complete configuration dictionary"""
        return {
            'data_file_path': cls.DATA_FILE_PATH,
            'max_samples': cls.MAX_SAMPLES,
            'max_samples_per_dataset': cls.MAX_SAMPLES_PER_DATASET,
            'lookback_window': cls.LOOKBACK_WINDOW,
            'models_to_train': cls.MODELS_TO_TRAIN,
            'model_directory': cls.MODEL_DIRECTORY,
            'save_models': cls.SAVE_MODELS,
            'test_size': cls.TEST_SIZE,
            'random_state': cls.RANDOM_STATE
        }
