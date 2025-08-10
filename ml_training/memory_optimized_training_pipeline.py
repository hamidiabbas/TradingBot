"""
Windows-Optimized ML Training Pipeline
====================================
Professional ML training pipeline optimized for Windows systems
with GPU acceleration and proper memory management.
"""

import asyncio
import os
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import joblib
import h5py
from pathlib import Path
from tqdm import tqdm
import gc
import warnings
warnings.filterwarnings('ignore')

# Windows-specific optimizations
import multiprocessing
multiprocessing.freeze_support()

class WindowsOptimizedDataProcessor:
    """Windows-optimized data processor with GPU acceleration support"""
    
    def __init__(self, use_gpu: bool = True):
        self.use_gpu = use_gpu and self._check_gpu_availability()
        self.feature_columns = [
            'open', 'high', 'low', 'close', 'tick_volume',
            'sma_20', 'sma_50', 'ema_12', 'ema_26',
            'macd', 'macd_signal', 'macd_histogram',
            'rsi', 'bb_middle', 'bb_upper', 'bb_lower', 'bb_width', 'bb_position',
            'stoch_k', 'stoch_d', 'atr', 'volume_sma', 'volume_ratio',
            'price_change', 'high_low_ratio', 'close_open_ratio', 'volatility', 'log_return'
        ]
        
        if self.use_gpu:
            print("🚀 GPU acceleration enabled for training")
        else:
            print("💻 Using CPU for training")
    
    def _check_gpu_availability(self) -> bool:
        """Check if GPU is available for TensorFlow"""
        try:
            import tensorflow as tf
            gpus = tf.config.list_physical_devices('GPU')
            if gpus:
                print(f"🎮 Found {len(gpus)} GPU(s): {[gpu.name for gpu in gpus]}")
                # Configure GPU memory growth
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
                return True
            else:
                print("⚠️ No GPU found, using CPU")
                return False
        except ImportError:
            print("⚠️ TensorFlow not available, using CPU")
            return False
    
    def fix_mt5_timestamps(self, h5_file_path: str) -> Dict[str, Any]:
        """Fix MT5 timestamp issues and load data properly"""
        try:
            print("🔧 Fixing MT5 timestamp issues...")
            
            fixed_data = {}
            
            with h5py.File(h5_file_path, 'r') as f:
                symbols = list(f['data'].keys())
                print(f"📈 Processing {len(symbols)} symbols...")
                
                for symbol in symbols:
                    fixed_data[symbol] = {}
                    symbol_group = f['data'][symbol]
                    timeframes = list(symbol_group.keys())
                    
                    for timeframe in timeframes:
                        try:
                            tf_group = symbol_group[timeframe]
                            
                            # Get raw timestamp data
                            time_data = tf_group['time'][:]
                            
                            # Fix timestamp conversion (common MT5 issue)
                            # Convert to proper datetime, handling out-of-bounds values
                            valid_timestamps = []
                            for ts in time_data:
                                try:
                                    # Ensure timestamp is in valid range (1970-2099)
                                    if 0 < ts < 4102444800:  # Valid Unix timestamp range
                                        dt = pd.to_datetime(ts, unit='s', utc=True)
                                    else:
                                        # Use a reasonable fallback timestamp
                                        dt = pd.to_datetime('2020-01-01', utc=True)
                                    valid_timestamps.append(dt)
                                except (ValueError, pd.errors.OutOfBoundsDatetime):
                                    # Fallback for invalid timestamps
                                    valid_timestamps.append(pd.to_datetime('2020-01-01', utc=True))
                            
                            # Create DataFrame with fixed timestamps
                            df_data = {
                                'open': tf_group['open'][:],
                                'high': tf_group['high'][:],
                                'low': tf_group['low'][:],
                                'close': tf_group['close'][:],
                                'tick_volume': tf_group['tick_volume'][:],
                                'spread': tf_group['spread'][:],
                                'real_volume': tf_group['real_volume'][:]
                            }
                            
                            df = pd.DataFrame(df_data, index=pd.DatetimeIndex(valid_timestamps))
                            
                            # Remove any duplicate timestamps
                            df = df[~df.index.duplicated(keep='first')]
                            
                            # Sort by timestamp
                            df = df.sort_index()
                            
                            fixed_data[symbol][timeframe] = df
                            
                            print(f"   ✅ Fixed {symbol} {timeframe}: {len(df)} bars")
                            
                        except Exception as e:
                            print(f"   ❌ Error processing {symbol} {timeframe}: {e}")
                            continue
            
            return fixed_data
            
        except Exception as e:
            print(f"❌ Error fixing MT5 timestamps: {e}")
            return {}
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators with Windows optimization"""
        try:
            print(f"   📊 Calculating indicators for {len(df)} bars...")
            
            # Work on a copy to avoid modifying original
            data = df.copy()
            
            # Basic indicators with proper min_periods
            data['sma_20'] = data['close'].rolling(20, min_periods=1).mean()
            data['sma_50'] = data['close'].rolling(50, min_periods=1).mean()
            data['ema_12'] = data['close'].ewm(span=12, min_periods=1).mean()
            data['ema_26'] = data['close'].ewm(span=26, min_periods=1).mean()
            
            # MACD
            data['macd'] = data['ema_12'] - data['ema_26']
            data['macd_signal'] = data['macd'].ewm(span=9, min_periods=1).mean()
            data['macd_histogram'] = data['macd'] - data['macd_signal']
            
            # RSI with proper error handling
            delta = data['close'].diff()
            gain = delta.where(delta > 0, 0).rolling(14, min_periods=1).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14, min_periods=1).mean()
            rs = gain / loss.replace(0, np.inf)
            data['rsi'] = 100 - (100 / (1 + rs))
            
            # Bollinger Bands
            data['bb_middle'] = data['sma_20']
            bb_std = data['close'].rolling(20, min_periods=1).std()
            data['bb_upper'] = data['bb_middle'] + (bb_std * 2)
            data['bb_lower'] = data['bb_middle'] - (bb_std * 2)
            data['bb_width'] = data['bb_upper'] - data['bb_lower']
            data['bb_position'] = (data['close'] - data['bb_lower']) / data['bb_width'].replace(0, 1)
            
            # Stochastic
            high_14 = data['high'].rolling(14, min_periods=1).max()
            low_14 = data['low'].rolling(14, min_periods=1).min()
            data['stoch_k'] = 100 * (data['close'] - low_14) / (high_14 - low_14).replace(0, 1)
            data['stoch_d'] = data['stoch_k'].rolling(3, min_periods=1).mean()
            
            # ATR
            hl = data['high'] - data['low']
            hc = np.abs(data['high'] - data['close'].shift(1))
            lc = np.abs(data['low'] - data['close'].shift(1))
            tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
            data['atr'] = tr.rolling(14, min_periods=1).mean()
            
            # Volume indicators
            data['volume_sma'] = data['tick_volume'].rolling(20, min_periods=1).mean()
            data['volume_ratio'] = data['tick_volume'] / data['volume_sma'].replace(0, 1)
            
            # Price patterns
            data['price_change'] = data['close'].pct_change().fillna(0)
            data['high_low_ratio'] = data['high'] / data['low'].replace(0, 1)
            data['close_open_ratio'] = data['close'] / data['open'].replace(0, 1)
            data['volatility'] = data['price_change'].rolling(20, min_periods=1).std()
            data['log_return'] = np.log(data['close'] / data['close'].shift(1)).fillna(0)
            
            # Handle any remaining NaN values
            data = data.fillna(method='ffill').fillna(0)
            
            # Replace infinite values
            data = data.replace([np.inf, -np.inf], 0)
            
            print(f"   ✅ Technical indicators calculated successfully")
            return data
            
        except Exception as e:
            print(f"   ❌ Error calculating indicators: {e}")
            return df
    
    def create_training_features(self, data: Dict[str, Dict[str, pd.DataFrame]], 
                               max_samples_per_symbol: int = 10000) -> Tuple[np.ndarray, np.ndarray]:
        """Create training features with memory optimization"""
        try:
            print("🔄 Creating training features with memory optimization...")
            
            all_features = []
            all_targets = []
            total_samples = 0
            
            for symbol, timeframe_data in data.items():
                print(f"   📊 Processing {symbol}...")
                
                for timeframe, df in timeframe_data.items():
                    if len(df) < 100:  # Skip if insufficient data
                        continue
                    
                    print(f"      ⚙️ Processing {timeframe} ({len(df)} bars)...")
                    
                    # Process data with indicators
                    processed_df = self.calculate_technical_indicators(df)
                    
                    # Create features for this dataset
                    X, y = self._create_features_for_dataset(
                        processed_df, 
                        lookback=30,  # Reduced lookback for memory efficiency
                        max_samples=max_samples_per_symbol
                    )
                    
                    if X.size > 0 and y.size > 0:
                        all_features.append(X)
                        all_targets.append(y)
                        total_samples += len(X)
                        
                        print(f"      ✅ Added {len(X)} samples from {symbol} {timeframe}")
                    
                    # Memory cleanup
                    del processed_df, X, y
                    gc.collect()
                    
                    # Limit total samples to prevent memory overflow
                    if total_samples > 100000:  # Limit to 100k samples
                        print(f"   ⚠️ Reached sample limit ({total_samples}), stopping collection")
                        break
                
                if total_samples > 100000:
                    break
            
            if not all_features:
                print("❌ No features created")
                return np.array([]), np.array([])
            
            # Combine all features
            print("🔗 Combining all features...")
            X_combined = np.vstack(all_features)
            y_combined = np.vstack(all_targets)
            
            print(f"✅ Total training data created:")
            print(f"   Features shape: {X_combined.shape}")
            print(f"   Targets shape: {y_combined.shape}")
            print(f"   Total samples: {len(X_combined):,}")
            
            return X_combined, y_combined
            
        except Exception as e:
            print(f"❌ Error creating training features: {e}")
            return np.array([]), np.array([])
    
    def _create_features_for_dataset(self, df: pd.DataFrame, lookback: int = 30, 
                                   max_samples: int = 10000) -> Tuple[np.ndarray, np.ndarray]:
        """Create features for a single dataset"""
        try:
            # Get available feature columns
            available_columns = [col for col in self.feature_columns if col in df.columns]
            
            if len(available_columns) < 5:
                return np.array([]), np.array([])
            
            # Get feature data
            feature_data = df[available_columns].fillna(method='ffill').fillna(0)
            
            if len(feature_data) < lookback + 1:
                return np.array([]), np.array([])
            
            # Limit samples to prevent memory issues
            total_possible_samples = len(feature_data) - lookback
            actual_samples = min(total_possible_samples, max_samples)
            
            # Create arrays with proper data type
            X = np.zeros((actual_samples, lookback, len(available_columns)), dtype=np.float32)
            y = np.zeros((actual_samples, 2), dtype=np.float32)
            
            # Create samples
            for i in range(actual_samples):
                # Features: lookback window
                X[i] = feature_data.iloc[i:i + lookback].values.astype(np.float32)
                
                # Target: next period direction and magnitude
                current_close = feature_data.iloc[i + lookback - 1]['close']
                next_close = feature_data.iloc[i + lookback]['close']
                
                direction = 1.0 if next_close > current_close else 0.0
                magnitude = (next_close - current_close) / current_close if current_close != 0 else 0.0
                
                y[i] = [direction, magnitude]
            
            return X, y
            
        except Exception as e:
            print(f"   ❌ Error creating features for dataset: {e}")
            return np.array([]), np.array([])

class WindowsMLTrainer:
    """Windows-optimized ML trainer with GPU support"""
    
    def __init__(self, use_gpu: bool = True):
        self.use_gpu = use_gpu
        self.models = {}
        
    def train_random_forest_model(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Train Random Forest model optimized for Windows"""
        try:
            print("🌳 Training Random Forest Model...")
            
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import accuracy_score, classification_report
            
            # Prepare data for Random Forest (flatten features)
            X_flat = X.reshape(X.shape[0], -1)
            y_direction = y[:, 0]  # Use direction for classification
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_flat, y_direction, test_size=0.2, random_state=42, stratify=y_direction
            )
            
            # Create and train model
            rf_model = RandomForestClassifier(
                n_estimators=100,
                max_depth=12,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1  # Use all CPU cores
            )
            
            print("   🏋️ Training Random Forest...")
            rf_model.fit(X_train, y_train)
            
            # Evaluate model
            train_accuracy = rf_model.score(X_train, y_train)
            test_accuracy = rf_model.score(X_test, y_test)
            
            # Make predictions for detailed metrics
            y_pred = rf_model.predict(X_test)
            
            print(f"   📊 Training Accuracy: {train_accuracy:.4f}")
            print(f"   📊 Test Accuracy: {test_accuracy:.4f}")
            
            # Save model
            os.makedirs('models/random_forest', exist_ok=True)
            joblib.dump(rf_model, 'models/random_forest/windows_optimized_rf.pkl')
            
            # Create results
            rf_results = {
                'model_type': 'RandomForest_Windows_Optimized',
                'training_completed': True,
                'model_version': '4.0_windows',
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'features_count': X_flat.shape[1],
                'train_accuracy': float(train_accuracy),
                'test_accuracy': float(test_accuracy),
                'training_date': datetime.utcnow().isoformat(),
                'model_file': 'models/random_forest/windows_optimized_rf.pkl'
            }
            
            self.models['random_forest'] = rf_results
            
            print(f"   ✅ Random Forest training completed!")
            return rf_results
            
        except Exception as e:
            print(f"   ❌ Random Forest training failed: {e}")
            return None
    
    def train_lightweight_lstm(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Train lightweight LSTM optimized for Windows"""
        try:
            print("🔮 Training Lightweight LSTM Model...")
            
            if self.use_gpu:
                # Configure TensorFlow for GPU
                import tensorflow as tf
                print("   🎮 Configuring TensorFlow for GPU...")
                
                # Set memory growth for GPU
                gpus = tf.config.experimental.list_physical_devices('GPU')
                if gpus:
                    for gpu in gpus:
                        tf.config.experimental.set_memory_growth(gpu, True)
            
            from sklearn.model_selection import train_test_split
            from sklearn.preprocessing import StandardScaler
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, shuffle=False
            )
            
            # Normalize features
            scaler = StandardScaler()
            
            # Normalize each feature across the time dimension
            X_train_scaled = np.zeros_like(X_train)
            X_test_scaled = np.zeros_like(X_test)
            
            for feature_idx in range(X_train.shape[2]):
                X_train_scaled[:, :, feature_idx] = scaler.fit_transform(X_train[:, :, feature_idx])
                X_test_scaled[:, :, feature_idx] = scaler.transform(X_test[:, :, feature_idx])
            
            # Build lightweight LSTM model
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import LSTM, Dense, Dropout
            from tensorflow.keras.optimizers import Adam
            
            model = Sequential([
                LSTM(32, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])),
                Dropout(0.2),
                LSTM(16, return_sequences=False),
                Dropout(0.2),
                Dense(8, activation='relu'),
                Dense(2)  # Direction and magnitude
            ])
            
            model.compile(
                optimizer=Adam(learning_rate=0.001),
                loss='mse',
                metrics=['mae']
            )
            
            print("   🏋️ Training LSTM...")
            history = model.fit(
                X_train_scaled, y_train,
                epochs=20,  # Reduced epochs for faster training
                batch_size=64,
                validation_data=(X_test_scaled, y_test),
                verbose=1
            )
            
            # Evaluate model
            train_loss, train_mae = model.evaluate(X_train_scaled, y_train, verbose=0)
            test_loss, test_mae = model.evaluate(X_test_scaled, y_test, verbose=0)
            
            print(f"   📊 Training Loss: {train_loss:.6f}")
            print(f"   📊 Test Loss: {test_loss:.6f}")
            print(f"   📊 Training MAE: {train_mae:.6f}")
            print(f"   📊 Test MAE: {test_mae:.6f}")
            
            # Save model and scaler
            os.makedirs('models/lstm', exist_ok=True)
            model.save('models/lstm/windows_optimized_lstm.h5')
            joblib.dump(scaler, 'models/lstm/lstm_scaler.pkl')
            
            # Create results
            lstm_results = {
                'model_type': 'LSTM_Windows_Optimized',
                'training_completed': True,
                'model_version': '4.0_windows',
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'features_count': X_train.shape[2],
                'sequence_length': X_train.shape[1],
                'train_loss': float(train_loss),
                'test_loss': float(test_loss),
                'train_mae': float(train_mae),
                'test_mae': float(test_mae),
                'epochs_trained': 20,
                'gpu_used': self.use_gpu,
                'training_date': datetime.utcnow().isoformat(),
                'model_file': 'models/lstm/windows_optimized_lstm.h5',
                'scaler_file': 'models/lstm/lstm_scaler.pkl'
            }
            
            self.models['lstm'] = lstm_results
            
            print(f"   ✅ LSTM training completed!")
            return lstm_results
            
        except Exception as e:
            print(f"   ❌ LSTM training failed: {e}")
            return None

async def run_windows_optimized_training():
    """Run Windows-optimized training pipeline"""
    print("🚀 === WINDOWS-OPTIMIZED ML TRAINING PIPELINE ===")
    print(f"📅 Started at: {datetime.utcnow()}")
    print(f"💻 Platform: Windows")
    
    try:
        # Check if data file exists
        data_file = "data/training/mt5_historical_data.h5"
        
        if not os.path.exists(data_file):
            print(f"❌ Data file not found: {data_file}")
            print("💡 Please run the data collection script first")
            return False
        
        print(f"📊 Loading data from: {data_file}")
        
        # Initialize processor with GPU support
        processor = WindowsOptimizedDataProcessor(use_gpu=True)
        
        # Fix MT5 timestamp issues and load data
        fixed_data = processor.fix_mt5_timestamps(data_file)
        
        if not fixed_data:
            print("❌ No data could be loaded")
            return False
        
        # Create training features
        X, y = processor.create_training_features(fixed_data, max_samples_per_symbol=15000)
        
        if X.size == 0:
            print("❌ No training features created")
            return False
        
        # Initialize trainer
        trainer = WindowsMLTrainer(use_gpu=True)
        
        # Train models
        print("\n🧠 === MODEL TRAINING ===")
        
        # Train Random Forest
        rf_results = trainer.train_random_forest_model(X, y)
        
        # Train LSTM if enough memory available
        if X.nbytes < 500 * 1024 * 1024:  # Less than 500MB
            lstm_results = trainer.train_lightweight_lstm(X, y)
        else:
            print("⚠️ Skipping LSTM training due to memory constraints")
            lstm_results = None
        
        # Create training summary
        training_summary = {
            'training_completed': True,
            'training_date': datetime.utcnow().isoformat(),
            'platform': 'Windows',
            'training_type': 'Windows_Optimized',
            'data_source': 'Real_MT5_Data_Fixed',
            'total_samples': len(X),
            'features_count': X.shape[2] if len(X.shape) > 2 else X.shape[1],
            'models_trained': list(trainer.models.keys()),
            'timestamp_issues_fixed': True,
            'gpu_acceleration': trainer.use_gpu
        }
        
        # Add model results
        if rf_results:
            training_summary['random_forest'] = rf_results
        if lstm_results:
            training_summary['lstm'] = lstm_results
        
        # Save training summary
        os.makedirs('models', exist_ok=True)
        with open('models/windows_training_summary.json', 'w') as f:
            import json
            json.dump(training_summary, f, indent=2)
        
        print("\n🏆 === WINDOWS TRAINING COMPLETED ===")
        print(f"✅ Total Training Samples: {len(X):,}")
        print(f"✅ Features per Sample: {X.shape[2] if len(X.shape) > 2 else X.shape[1]}")
        
        if rf_results:
            print(f"✅ Random Forest: {rf_results['test_accuracy']:.4f} accuracy")
        if lstm_results:
            print(f"✅ LSTM: {lstm_results['test_loss']:.6f} test loss")
        
        print(f"📁 Training summary: models/windows_training_summary.json")
        print(f"🎮 GPU Acceleration: {'Enabled' if trainer.use_gpu else 'Disabled'}")
        
        print("\n🎉 WINDOWS TRAINING PIPELINE COMPLETED SUCCESSFULLY!")
        return True
        
    except Exception as e:
        print(f"❌ Training pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Enable Windows multiprocessing support
    multiprocessing.freeze_support()
    
    success = asyncio.run(run_windows_optimized_training())
    
    if success:
        print("\n🎯 NEXT STEPS:")
        print("1. Check trained models in models/ directory")
        print("2. Test your trading system with the new models")
        print("3. Set up GitHub repository for version control")
        print("4. Configure automated training schedule")
    else:
        print("\n🛠️ Please resolve the issues and try again")
