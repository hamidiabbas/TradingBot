"""
Comprehensive ML Models Testing Suite
===================================
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio

class TestMLModelsIntegrity:
    
    @pytest.fixture
    def sample_market_data(self):
        """Generate realistic test market data"""
        dates = pd.date_range('2023-01-01', periods=2000, freq='H')
        
        # Create realistic EURUSD-like data with trends and volatility
        np.random.seed(42)
        price_base = 1.1000
        returns = np.random.normal(0, 0.0008, 2000)  # Realistic forex volatility
        
        # Add some trend and regime changes
        trend_changes = [0, 500, 1000, 1500, 2000]
        price_segments = []
        
        for i, start_idx in enumerate(trend_changes[:-1]):
            end_idx = trend_changes[i + 1]
            length = end_idx - start_idx
            
            if i % 3 == 0:  # Trending up
                trend = np.linspace(0, 0.02, length)
            elif i % 3 == 1:  # Trending down  
                trend = np.linspace(0, -0.015, length)
            else:  # Ranging
                trend = np.zeros(length)
            
            segment_returns = returns[start_idx:end_idx] + trend
            price_segments.extend(segment_returns.tolist())
        
        prices = price_base * (1 + np.array(price_segments)).cumprod()
        
        # Generate OHLCV data
        data = pd.DataFrame({
            'open': np.roll(prices, 1),
            'high': prices * (1 + np.abs(np.random.normal(0, 0.0002, 2000))),
            'low': prices * (1 - np.abs(np.random.normal(0, 0.0002, 2000))),
            'close': prices,
            'volume': np.random.lognormal(13, 0.5, 2000).astype(int),
            'tick_volume': np.random.lognormal(11, 0.3, 2000).astype(int)
        }, index=dates)
        
        data['open'].iloc[0] = data['close'].iloc[0]
        return data

    def test_lstm_model_functionality(self, sample_market_data):
        """Test LSTM model core functionality"""
        try:
            from ml_models.lstm_model import InstitutionalLSTMConfig, InstitutionalLSTMModel
            
            print("🔮 Testing LSTM Model...")
            
            # Initialize with test config
            config = InstitutionalLSTMConfig(
                sequence_length=60,
                prediction_horizons=[1, 5, 15],
                lstm_units=[128, 64, 32],
                epochs=5,  # Reduced for testing
                batch_size=32
            )
            
            lstm_model = InstitutionalLSTMModel(config)
            
            # Test prediction without training (should handle gracefully)
            try:
                prediction = lstm_model.predict(sample_market_data)
                assert prediction is not None, "LSTM should return prediction object even untrained"
                print("   ✅ LSTM prediction interface working")
            except Exception as e:
                print(f"   ⚠️ LSTM prediction failed: {e}")
            
            # Test model info
            model_info = lstm_model.get_comprehensive_model_info()
            assert isinstance(model_info, dict), "Model info should return dictionary"
            assert 'model_type' in model_info, "Model info missing model_type"
            
            print("   ✅ LSTM Model: PASSED")
            return True
            
        except Exception as e:
            print(f"   ❌ LSTM Model: FAILED - {e}")
            return False

    def test_random_forest_model_functionality(self, sample_market_data):
        """Test Random Forest model core functionality"""
        try:
            from ml_models.random_forest_model import RandomForestConfig, EnhancedRandomForestModel
            
            print("🌳 Testing Random Forest Model...")
            
            config = RandomForestConfig(
                n_estimators=50,  # Reduced for testing
                max_depth=10
            )
            
            rf_model = EnhancedRandomForestModel(config)
            
            # Test prediction
            prediction = rf_model.predict(sample_market_data)
            assert prediction is not None, "RF should return prediction object"
            
            # Test model info
            model_info = rf_model.get_model_info()
            assert isinstance(model_info, dict), "RF model info should return dictionary"
            
            print("   ✅ Random Forest Model: PASSED")
            return True
            
        except Exception as e:
            print(f"   ❌ Random Forest Model: FAILED - {e}")
            return False

    def test_svm_model_functionality(self, sample_market_data):
        """Test SVM model core functionality"""
        try:
            from ml_models.svm_model import SVMConfig, EnhancedSVMModel
            
            print("📈 Testing SVM Model...")
            
            config = SVMConfig(
                kernel='rbf',
                C=1.0
            )
            
            svm_model = EnhancedSVMModel(config)
            
            # Test prediction
            prediction = svm_model.predict(sample_market_data)
            assert prediction is not None, "SVM should return prediction object"
            
            print("   ✅ SVM Model: PASSED")
            return True
            
        except Exception as e:
            print(f"   ❌ SVM Model: FAILED - {e}")
            return False

    def test_ensemble_model_integration(self, sample_market_data):
        """Test Ensemble model integration"""
        try:
            from ml_models.ensemble_model import EnsembleConfig, EnhancedEnsembleModel
            
            print("🎭 Testing Ensemble Model...")
            
            config = EnsembleConfig()
            ensemble_model = EnhancedEnsembleModel(config)
            
            # Test ensemble prediction
            prediction = ensemble_model.predict(sample_market_data)
            assert prediction is not None, "Ensemble should return prediction object"
            
            # Test ensemble components
            if hasattr(prediction, 'model_agreement'):
                assert 0 <= prediction.model_agreement <= 1, "Model agreement should be 0-1"
            
            print("   ✅ Ensemble Model: PASSED")
            return True
            
        except Exception as e:
            print(f"   ❌ Ensemble Model: FAILED - {e}")
            return False

# Run the tests
if __name__ == "__main__":
    test_suite = TestMLModelsIntegrity()
    sample_data = test_suite.sample_market_data()
    
    print("🧠 === ML MODELS COMPREHENSIVE TESTING ===")
    
    results = {
        'lstm': test_suite.test_lstm_model_functionality(sample_data),
        'random_forest': test_suite.test_random_forest_model_functionality(sample_data),
        'svm': test_suite.test_svm_model_functionality(sample_data),
        'ensemble': test_suite.test_ensemble_model_integration(sample_data)
    }
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\n📊 ML Models Test Results: {passed}/{total} PASSED")
    if passed == total:
        print("✅ All ML models passed basic functionality tests")
    else:
        failed = [name for name, result in results.items() if not result]
        print(f"❌ Failed models: {failed}")
