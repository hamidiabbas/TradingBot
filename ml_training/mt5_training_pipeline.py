"""
Real MT5 Market Data Collection & ML Training Pipeline
=====================================================
Professional ML training pipeline that collects real historical market data
from MetaTrader 5 and trains institutional-grade ML models for algorithmic trading.
"""

import asyncio
import os
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import joblib
import MetaTrader5 as mt5
import pytz
import h5py
from pathlib import Path
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# Create directories
os.makedirs('models/lstm', exist_ok=True)
os.makedirs('models/random_forest', exist_ok=True) 
os.makedirs('models/svm', exist_ok=True)
os.makedirs('models/ensemble', exist_ok=True)
os.makedirs('data/training', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)

class MT5DataCollector:
    """Professional MT5 data collection for ML training"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.symbols = config.get('symbols', ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD'])
        self.timeframes = config.get('timeframes', ['M1', 'M5', 'M15', 'H1', 'H4', 'D1'])
        self.start_date = config.get('start_date', datetime(2020, 1, 1))
        self.end_date = config.get('end_date', datetime.utcnow())
        
        # MT5 connection settings
        self.mt5_login = config.get('mt5_login')
        self.mt5_password = config.get('mt5_password')
        self.mt5_server = config.get('mt5_server')
        
        self.timezone = pytz.timezone("Etc/UTC")
        self.collected_data = {}
        
    async def initialize_mt5(self) -> bool:
        """Initialize MT5 connection for data collection"""
        try:
            print("🔌 Initializing MT5 connection for data collection...")
            
            # Initialize MT5
            if not mt5.initialize():
                if self.mt5_login and self.mt5_password and self.mt5_server:
                    # Try with credentials
                    if not mt5.initialize(
                        login=self.mt5_login,
                        password=self.mt5_password,
                        server=self.mt5_server
                    ):
                        error = mt5.last_error()
                        print(f"❌ MT5 initialization failed: {error}")
                        return False
                else:
                    print("❌ MT5 initialization failed. Please provide valid credentials.")
                    return False
            
            # Get account info
            account_info = mt5.account_info()
            if account_info:
                print(f"✅ Connected to MT5")
                print(f"   Account: {account_info.login}")
                print(f"   Server: {account_info.server}")
                print(f"   Company: {account_info.company}")
                return True
            else:
                print("❌ Failed to get account information")
                return False
                
        except Exception as e:
            print(f"❌ Error initializing MT5: {e}")
            return False
    
    def convert_timeframe_to_mt5(self, timeframe: str) -> int:
        """Convert string timeframe to MT5 timeframe constant"""
        timeframe_map = {
            'M1': mt5.TIMEFRAME_M1,
            'M5': mt5.TIMEFRAME_M5,
            'M15': mt5.TIMEFRAME_M15,
            'M30': mt5.TIMEFRAME_M30,
            'H1': mt5.TIMEFRAME_H1,
            'H4': mt5.TIMEFRAME_H4,
            'D1': mt5.TIMEFRAME_D1,
            'W1': mt5.TIMEFRAME_W1,
            'MN1': mt5.TIMEFRAME_MN1
        }
        return timeframe_map.get(timeframe, mt5.TIMEFRAME_H1)
    
    async def collect_symbol_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """Collect historical data for a specific symbol and timeframe"""
        try:
            print(f"📊 Collecting {symbol} {timeframe} data...")
            
            # Convert timeframe
            mt5_timeframe = self.convert_timeframe_to_mt5(timeframe)
            
            # Prepare UTC timestamps
            utc_from = self.start_date.replace(tzinfo=self.timezone)
            utc_to = self.end_date.replace(tzinfo=self.timezone)
            
            # Get historical data[25][46]
            rates = mt5.copy_rates_range(symbol, mt5_timeframe, utc_from, utc_to)
            
            if rates is None or len(rates) == 0:
                print(f"⚠️ No data available for {symbol} {timeframe}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s', utc=True)
            df.set_index('time', inplace=True)
            
            # Add symbol and timeframe columns
            df['symbol'] = symbol
            df['timeframe'] = timeframe
            
            print(f"   ✅ Collected {len(df)} bars for {symbol} {timeframe}")
            return df
            
        except Exception as e:
            print(f"❌ Error collecting data for {symbol} {timeframe}: {e}")
            return pd.DataFrame()
    
    async def collect_all_data(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        """Collect historical data for all symbols and timeframes"""
        try:
            print("🚀 === STARTING REAL MARKET DATA COLLECTION ===")
            print(f"📅 Period: {self.start_date} to {self.end_date}")
            print(f"📈 Symbols: {self.symbols}")
            print(f"⏰ Timeframes: {self.timeframes}")
            
            collected_data = {}
            total_combinations = len(self.symbols) * len(self.timeframes)
            current_combination = 0
            
            for symbol in self.symbols:
                collected_data[symbol] = {}
                
                # Check if symbol is available
                symbol_info = mt5.symbol_info(symbol)
                if not symbol_info:
                    print(f"⚠️ Symbol {symbol} not available, skipping...")
                    continue
                
                # Enable symbol in Market Watch
                if not symbol_info.visible:
                    if not mt5.symbol_select(symbol, True):
                        print(f"⚠️ Failed to enable {symbol}, skipping...")
                        continue
                
                for timeframe in self.timeframes:
                    current_combination += 1
                    progress = (current_combination / total_combinations) * 100
                    
                    print(f"\n🔄 Progress: {progress:.1f}% ({current_combination}/{total_combinations})")
                    
                    # Collect data for this combination
                    data = await self.collect_symbol_data(symbol, timeframe)
                    
                    if not data.empty:
                        collected_data[symbol][timeframe] = data
                        
                        # Save individual files for backup
                        filename = f"data/training/{symbol}_{timeframe}_raw.csv"
                        data.to_csv(filename)
                        print(f"   💾 Saved backup: {filename}")
                    
                    # Small delay to avoid overwhelming MT5
                    await asyncio.sleep(0.1)
            
            self.collected_data = collected_data
            print(f"\n✅ Data collection completed!")
            print(f"📊 Total symbols collected: {len(collected_data)}")
            
            return collected_data
            
        except Exception as e:
            print(f"❌ Error during data collection: {e}")
            return {}
    
    def save_collected_data(self, filename: str = "data/training/mt5_historical_data.h5"):
        """Save collected data to HDF5 format for efficient storage"""
        try:
            print(f"💾 Saving collected data to {filename}...")
            
            with h5py.File(filename, 'w') as f:
                # Save metadata
                metadata_group = f.create_group('metadata')
                metadata_group.attrs['collection_date'] = datetime.utcnow().isoformat()
                metadata_group.attrs['start_date'] = self.start_date.isoformat()
                metadata_group.attrs['end_date'] = self.end_date.isoformat()
                metadata_group.attrs['symbols'] = [s.encode('utf-8') for s in self.symbols]
                metadata_group.attrs['timeframes'] = [tf.encode('utf-8') for tf in self.timeframes]
                
                # Save data
                data_group = f.create_group('data')
                
                for symbol, timeframe_data in self.collected_data.items():
                    symbol_group = data_group.create_group(symbol)
                    
                    for timeframe, df in timeframe_data.items():
                        if not df.empty:
                            # Convert DataFrame to numpy arrays for HDF5 storage
                            tf_group = symbol_group.create_group(timeframe)
                            
                            # Store OHLCV data
                            tf_group.create_dataset('time', data=df.index.astype(np.int64))
                            tf_group.create_dataset('open', data=df['open'].values)
                            tf_group.create_dataset('high', data=df['high'].values)
                            tf_group.create_dataset('low', data=df['low'].values)
                            tf_group.create_dataset('close', data=df['close'].values)
                            tf_group.create_dataset('tick_volume', data=df['tick_volume'].values)
                            tf_group.create_dataset('spread', data=df['spread'].values)
                            tf_group.create_dataset('real_volume', data=df['real_volume'].values)
            
            print(f"✅ Data saved successfully to {filename}")
            
        except Exception as e:
            print(f"❌ Error saving data: {e}")

class RealMarketDataProcessor:
    """Process real market data for ML training"""
    
    def __init__(self, data: Dict[str, Dict[str, pd.DataFrame]]):
        self.raw_data = data
        self.processed_data = {}
        self.feature_data = {}
        
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate comprehensive technical indicators[25][27]"""
        try:
            # Make a copy to avoid modifying original data
            data = df.copy()
            
            # Price-based indicators
            data['sma_20'] = data['close'].rolling(20).mean()
            data['sma_50'] = data['close'].rolling(50).mean()
            data['ema_12'] = data['close'].ewm(span=12).mean()
            data['ema_26'] = data['close'].ewm(span=26).mean()
            
            # MACD
            data['macd'] = data['ema_12'] - data['ema_26']
            data['macd_signal'] = data['macd'].ewm(span=9).mean()
            data['macd_histogram'] = data['macd'] - data['macd_signal']
            
            # RSI
            delta = data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            data['rsi'] = 100 - (100 / (1 + rs))
            
            # Bollinger Bands
            data['bb_middle'] = data['close'].rolling(20).mean()
            bb_std = data['close'].rolling(20).std()
            data['bb_upper'] = data['bb_middle'] + (bb_std * 2)
            data['bb_lower'] = data['bb_middle'] - (bb_std * 2)
            data['bb_width'] = data['bb_upper'] - data['bb_lower']
            data['bb_position'] = (data['close'] - data['bb_lower']) / data['bb_width']
            
            # Stochastic
            high_14 = data['high'].rolling(14).max()
            low_14 = data['low'].rolling(14).min()
            data['stoch_k'] = 100 * (data['close'] - low_14) / (high_14 - low_14)
            data['stoch_d'] = data['stoch_k'].rolling(3).mean()
            
            # ATR
            hl = data['high'] - data['low']
            hc = np.abs(data['high'] - data['close'].shift())
            lc = np.abs(data['low'] - data['close'].shift())
            tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
            data['atr'] = tr.rolling(14).mean()
            
            # Volume indicators
            data['volume_sma'] = data['tick_volume'].rolling(20).mean()
            data['volume_ratio'] = data['tick_volume'] / data['volume_sma']
            
            # Price patterns
            data['price_change'] = data['close'].pct_change()
            data['high_low_ratio'] = data['high'] / data['low']
            data['close_open_ratio'] = data['close'] / data['open']
            
            # Volatility measures
            data['volatility'] = data['price_change'].rolling(20).std()
            data['log_return'] = np.log(data['close'] / data['close'].shift(1))
            
            return data
            
        except Exception as e:
            print(f"❌ Error calculating technical indicators: {e}")
            return df
    
    def create_ml_features(self, df: pd.DataFrame, lookback: int = 60) -> Tuple[np.ndarray, np.ndarray]:
        """Create ML features and targets from processed data"""
        try:
            # Define feature columns
            feature_columns = [
                'open', 'high', 'low', 'close', 'tick_volume',
                'sma_20', 'sma_50', 'ema_12', 'ema_26',
                'macd', 'macd_signal', 'macd_histogram',
                'rsi', 'bb_middle', 'bb_upper', 'bb_lower', 'bb_width', 'bb_position',
                'stoch_k', 'stoch_d', 'atr', 'volume_sma', 'volume_ratio',
                'price_change', 'high_low_ratio', 'close_open_ratio', 'volatility', 'log_return'
            ]
            
            # Filter available columns
            available_columns = [col for col in feature_columns if col in df.columns]
            
            # Get feature data
            feature_data = df[available_columns].dropna()
            
            if len(feature_data) < lookback + 1:
                return np.array([]), np.array([])
            
            # Create sequences for LSTM
            X, y = [], []
            
            for i in range(lookback, len(feature_data)):
                # Features: lookback window of all indicators
                X.append(feature_data.iloc[i-lookback:i].values)
                
                # Target: next period price direction and magnitude
                current_close = feature_data['close'].iloc[i-1]
                next_close = feature_data['close'].iloc[i]
                
                # Price direction (0 = down, 1 = up)
                direction = 1 if next_close > current_close else 0
                
                # Price change magnitude (normalized)
                magnitude = (next_close - current_close) / current_close
                
                y.append([direction, magnitude])
            
            return np.array(X), np.array(y)
            
        except Exception as e:
            print(f"❌ Error creating ML features: {e}")
            return np.array([]), np.array([])
    
    async def process_all_data(self) -> Dict[str, Any]:
        """Process all collected data for ML training"""
        try:
            print("🔄 === PROCESSING REAL MARKET DATA FOR ML TRAINING ===")
            
            all_features = []
            all_targets = []
            symbol_data = {}
            
            for symbol, timeframe_data in self.raw_data.items():
                symbol_data[symbol] = {}
                
                for timeframe, df in timeframe_data.items():
                    if df.empty:
                        continue
                    
                    print(f"⚙️ Processing {symbol} {timeframe}...")
                    
                    # Calculate technical indicators
                    processed_df = self.calculate_technical_indicators(df)
                    
                    # Create ML features
                    X, y = self.create_ml_features(processed_df)
                    
                    if X.size > 0 and y.size > 0:
                        all_features.append(X)
                        all_targets.append(y)
                        
                        symbol_data[symbol][timeframe] = {
                            'processed_data': processed_df,
                            'features': X,
                            'targets': y
                        }
                        
                        print(f"   ✅ Created {len(X)} training samples")
            
            # Combine all features and targets
            if all_features:
                combined_features = np.vstack(all_features)
                combined_targets = np.vstack(all_targets)
                
                print(f"\n📊 TOTAL TRAINING DATA SUMMARY:")
                print(f"   Features shape: {combined_features.shape}")
                print(f"   Targets shape: {combined_targets.shape}")
                print(f"   Total samples: {len(combined_features)}")
                
                return {
                    'features': combined_features,
                    'targets': combined_targets,
                    'symbol_data': symbol_data,
                    'feature_columns': list(range(combined_features.shape[2]))
                }
            else:
                print("❌ No valid training data created")
                return {}
                
        except Exception as e:
            print(f"❌ Error processing data: {e}")
            return {}

class RealMLModelTrainer:
    """Train ML models with real market data"""
    
    def __init__(self, training_data: Dict[str, Any]):
        self.training_data = training_data
        self.trained_models = {}
        
    async def train_lstm_model(self):
        """Train LSTM model with real market data"""
        try:
            print("🔮 Training LSTM Model with Real Market Data...")
            
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import LSTM, Dense, Dropout
            from tensorflow.keras.optimizers import Adam
            from sklearn.model_selection import train_test_split
            from sklearn.preprocessing import StandardScaler
            
            # Get training data
            X = self.training_data['features']
            y = self.training_data['targets']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, shuffle=False
            )
            
            # Normalize features
            scaler = StandardScaler()
            X_train_scaled = np.zeros_like(X_train)
            X_test_scaled = np.zeros_like(X_test)
            
            for i in range(X_train.shape[2]):  # For each feature
                X_train_scaled[:, :, i] = scaler.fit_transform(X_train[:, :, i])
                X_test_scaled[:, :, i] = scaler.transform(X_test[:, :, i])
            
            # Build LSTM model
            model = Sequential([
                LSTM(128, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])),
                Dropout(0.2),
                LSTM(64, return_sequences=True),
                Dropout(0.2),
                LSTM(32),
                Dropout(0.2),
                Dense(16, activation='relu'),
                Dense(2)  # Direction and magnitude
            ])
            
            model.compile(
                optimizer=Adam(learning_rate=0.001),
                loss='mse',
                metrics=['mae']
            )
            
            # Train model
            print("   🏋️ Training LSTM...")
            history = model.fit(
                X_train_scaled, y_train,
                epochs=50,
                batch_size=32,
                validation_data=(X_test_scaled, y_test),
                verbose=1
            )
            
            # Evaluate model
            train_loss = model.evaluate(X_train_scaled, y_train, verbose=0)
            test_loss = model.evaluate(X_test_scaled, y_test, verbose=0)
            
            # Save model
            model.save('models/lstm/institutional_lstm_model.h5')
            joblib.dump(scaler, 'models/lstm/feature_scaler.pkl')
            
            lstm_results = {
                'model': model,
                'scaler': scaler,
                'model_type': 'LSTM',
                'training_completed': True,
                'model_version': '4.0_real_data',
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'training_date': datetime.utcnow().isoformat(),
                'sequence_length': X_train.shape[1],
                'features_count': X_train.shape[2],
                'epochs_trained': 50,
                'train_loss': float(train_loss[0]),
                'test_loss': float(test_loss[0]),
                'train_mae': float(train_loss[1]),
                'test_mae': float(test_loss[1])
            }
            
            self.trained_models['lstm'] = lstm_results
            
            print(f"   ✅ LSTM Training Complete!")
            print(f"      Training Loss: {train_loss[0]:.6f}")
            print(f"      Test Loss: {test_loss[0]:.6f}")
            print(f"      Training MAE: {train_loss[1]:.6f}")
            print(f"      Test MAE: {test_loss[1]:.6f}")
            
            return lstm_results
            
        except Exception as e:
            print(f"❌ Error training LSTM model: {e}")
            return None
    
    async def train_random_forest_model(self):
        """Train Random Forest model with real market data"""
        try:
            print("🌳 Training Random Forest Model with Real Market Data...")
            
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import accuracy_score, classification_report
            
            # Prepare data for Random Forest (2D format)
            X = self.training_data['features']
            y = self.training_data['targets']
            
            # Flatten features for Random Forest
            X_flat = X.reshape(X.shape[0], -1)
            y_direction = y[:, 0]  # Use direction as target for classification
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_flat, y_direction, test_size=0.2, random_state=42, stratify=y_direction
            )
            
            # Train Random Forest
            rf_model = RandomForestClassifier(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
            
            print("   🏋️ Training Random Forest...")
            rf_model.fit(X_train, y_train)
            
            # Evaluate model
            train_accuracy = rf_model.score(X_train, y_train)
            test_accuracy = rf_model.score(X_test, y_test)
            
            # Predictions
            y_pred = rf_model.predict(X_test)
            
            # Save model
            joblib.dump(rf_model, 'models/random_forest/rf_model.pkl')
            
            rf_results = {
                'model': rf_model,
                'model_type': 'RandomForest',
                'training_completed': True,
                'model_version': '4.0_real_data',
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'training_date': datetime.utcnow().isoformat(),
                'n_estimators': 200,
                'max_depth': 15,
                'features_count': X_train.shape[1],
                'train_accuracy': float(train_accuracy),
                'test_accuracy': float(test_accuracy),
                'classes': rf_model.classes_.tolist()
            }
            
            self.trained_models['random_forest'] = rf_results
            
            print(f"   ✅ Random Forest Training Complete!")
            print(f"      Training Accuracy: {train_accuracy:.4f}")
            print(f"      Test Accuracy: {test_accuracy:.4f}")
            
            return rf_results
            
        except Exception as e:
            print(f"❌ Error training Random Forest model: {e}")
            return None
    
    async def train_svm_model(self):
        """Train SVM model with real market data"""
        try:
            print("📈 Training SVM Model with Real Market Data...")
            
            from sklearn.svm import SVC
            from sklearn.model_selection import train_test_split
            from sklearn.preprocessing import StandardScaler
            from sklearn.metrics import accuracy_score
            
            # Prepare data
            X = self.training_data['features']
            y = self.training_data['targets']
            
            # Flatten features and use subset for SVM (SVM is computationally expensive)
            X_flat = X.reshape(X.shape[0], -1)
            y_direction = y[:, 0]
            
            # Use subset of data for SVM training (last 10000 samples)
            if len(X_flat) > 10000:
                X_flat = X_flat[-10000:]
                y_direction = y_direction[-10000:]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_flat, y_direction, test_size=0.2, random_state=42, stratify=y_direction
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train SVM
            svm_model = SVC(
                kernel='rbf',
                C=1.0,
                gamma='scale',
                probability=True,
                random_state=42
            )
            
            print("   🏋️ Training SVM...")
            svm_model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            train_accuracy = svm_model.score(X_train_scaled, y_train)
            test_accuracy = svm_model.score(X_test_scaled, y_test)
            
            # Save model
            joblib.dump(svm_model, 'models/svm/svm_model.pkl')
            joblib.dump(scaler, 'models/svm/svm_scaler.pkl')
            
            svm_results = {
                'model': svm_model,
                'scaler': scaler,
                'model_type': 'SVM',
                'training_completed': True,
                'model_version': '4.0_real_data',
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'training_date': datetime.utcnow().isoformat(),
                'kernel': 'rbf',
                'C': 1.0,
                'features_count': X_train.shape[1],
                'train_accuracy': float(train_accuracy),
                'test_accuracy': float(test_accuracy),
                'classes': svm_model.classes_.tolist()
            }
            
            self.trained_models['svm'] = svm_results
            
            print(f"   ✅ SVM Training Complete!")
            print(f"      Training Accuracy: {train_accuracy:.4f}")
            print(f"      Test Accuracy: {test_accuracy:.4f}")
            
            return svm_results
            
        except Exception as e:
            print(f"❌ Error training SVM model: {e}")
            return None
    
    async def train_ensemble_model(self):
        """Create ensemble model from trained base models"""
        try:
            print("🎭 Creating Ensemble Model...")
            
            # Calculate ensemble weights based on individual model performance
            weights = {}
            total_accuracy = 0
            
            if 'lstm' in self.trained_models:
                # For LSTM, use inverse of test loss as weight
                lstm_weight = 1.0 / (1.0 + self.trained_models['lstm']['test_loss'])
                weights['lstm'] = lstm_weight
                total_accuracy += lstm_weight
            
            if 'random_forest' in self.trained_models:
                rf_weight = self.trained_models['random_forest']['test_accuracy']
                weights['random_forest'] = rf_weight
                total_accuracy += rf_weight
            
            if 'svm' in self.trained_models:
                svm_weight = self.trained_models['svm']['test_accuracy']
                weights['svm'] = svm_weight
                total_accuracy += svm_weight
            
            # Normalize weights
            if total_accuracy > 0:
                for model in weights:
                    weights[model] = weights[model] / total_accuracy
            
            ensemble_results = {
                'model_type': 'Ensemble',
                'training_completed': True,
                'model_version': '4.0_real_data',
                'base_models': list(weights.keys()),
                'training_date': datetime.utcnow().isoformat(),
                'model_weights': weights,
                'confidence_threshold': 0.6,
                'agreement_threshold': 0.7,
                'ensemble_method': 'weighted_voting'
            }
            
            # Save ensemble configuration
            with open('models/ensemble/ensemble_config.pkl', 'wb') as f:
                pickle.dump(ensemble_results, f)
            
            self.trained_models['ensemble'] = ensemble_results
            
            print(f"   ✅ Ensemble Model Created!")
            print(f"      Base Models: {list(weights.keys())}")
            print(f"      Model Weights: {weights}")
            
            return ensemble_results
            
        except Exception as e:
            print(f"❌ Error creating ensemble model: {e}")
            return None

async def run_real_mt5_training_pipeline():
    """Run complete real MT5 training pipeline"""
    print("🚀 === REAL MT5 MARKET DATA ML TRAINING PIPELINE ===")
    print(f"📅 Started at: {datetime.utcnow()}")
    
    # Configuration
    config = {
        'symbols': ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD'],
        'timeframes': ['M15', 'H1', 'H4', 'D1'],
        'start_date': datetime(2020, 1, 1),  # 4+ years of data
        'end_date': datetime.utcnow(),
        # Add your MT5 credentials here
        'mt5_login': None,  # Your MT5 login
        'mt5_password': None,  # Your MT5 password  
        'mt5_server': None  # Your MT5 server
    }
    
    try:
        # Phase 1: Data Collection
        print("\n📊 PHASE 1: REAL MARKET DATA COLLECTION")
        data_collector = MT5DataCollector(config)
        
        if not await data_collector.initialize_mt5():
            print("❌ Failed to initialize MT5. Please check your connection and credentials.")
            return False
        
        # Collect real market data
        collected_data = await data_collector.collect_all_data()
        
        if not collected_data:
            print("❌ No data collected. Cannot proceed with training.")
            return False
        
        # Save collected data
        data_collector.save_collected_data()
        
        # Phase 2: Data Processing
        print("\n⚙️ PHASE 2: DATA PROCESSING FOR ML")
        data_processor = RealMarketDataProcessor(collected_data)
        training_data = await data_processor.process_all_data()
        
        if not training_data:
            print("❌ No training data created. Cannot proceed with ML training.")
            return False
        
        # Phase 3: ML Model Training
        print("\n🧠 PHASE 3: ML MODEL TRAINING WITH REAL DATA")
        model_trainer = RealMLModelTrainer(training_data)
        
        # Train all models
        lstm_results = await model_trainer.train_lstm_model()
        rf_results = await model_trainer.train_random_forest_model()
        svm_results = await model_trainer.train_svm_model()
        ensemble_results = await model_trainer.train_ensemble_model()
        
        # Create comprehensive training summary
        training_summary = {
            'training_completed': True,
            'training_date': datetime.utcnow().isoformat(),
            'training_type': 'REAL_MT5_DATA',
            'data_source': 'MetaTrader5',
            'symbols': config['symbols'],
            'timeframes': config['timeframes'],
            'data_period': f"{config['start_date']} to {config['end_date']}",
            'total_samples': len(training_data['features']) if training_data else 0,
            'models_trained': list(model_trainer.trained_models.keys()),
            'model_performance': {
                'lstm': {
                    'test_loss': lstm_results['test_loss'] if lstm_results else None,
                    'test_mae': lstm_results['test_mae'] if lstm_results else None
                } if lstm_results else None,
                'random_forest': {
                    'test_accuracy': rf_results['test_accuracy'] if rf_results else None
                } if rf_results else None,
                'svm': {
                    'test_accuracy': svm_results['test_accuracy'] if svm_results else None
                } if svm_results else None,
                'ensemble': {
                    'model_weights': ensemble_results['model_weights'] if ensemble_results else None
                } if ensemble_results else None
            },
            'model_files': {
                'lstm': 'models/lstm/institutional_lstm_model.h5',
                'random_forest': 'models/random_forest/rf_model.pkl',
                'svm': 'models/svm/svm_model.pkl',
                'ensemble': 'models/ensemble/ensemble_config.pkl'
            }
        }
        
        # Save training summary
        with open('models/real_training_summary.json', 'w') as f:
            import json
            json.dump(training_summary, f, indent=2)
        
        # Final Results
        print("\n🏆 === REAL ML TRAINING PIPELINE COMPLETED ===")
        print(f"✅ Data Source: Real MT5 Market Data")
        print(f"✅ Total Training Samples: {training_summary['total_samples']:,}")
        print(f"✅ Models Trained: {len(model_trainer.trained_models)}/4")
        
        if lstm_results:
            print(f"✅ LSTM Model: Test Loss {lstm_results['test_loss']:.6f}")
        if rf_results:
            print(f"✅ Random Forest: Test Accuracy {rf_results['test_accuracy']:.4f}")
        if svm_results:
            print(f"✅ SVM Model: Test Accuracy {svm_results['test_accuracy']:.4f}")
        if ensemble_results:
            print(f"✅ Ensemble Model: {len(ensemble_results['base_models'])} base models")
        
        print(f"\n📁 Model files saved in models/ directory")
        print(f"📋 Training summary: models/real_training_summary.json")
        
        print("\n🎉 REAL ML TRAINING PIPELINE COMPLETED SUCCESSFULLY!")
        print("🚀 Your trading system now has ML models trained on REAL market data!")
        
        return True
        
    except Exception as e:
        print(f"❌ Training pipeline failed: {e}")
        return False
    
    finally:
        # Shutdown MT5
        mt5.shutdown()

if __name__ == "__main__":
    # Run the real training pipeline
    success = asyncio.run(run_real_mt5_training_pipeline())
    
    if success:
        print("\n🎯 NEXT STEPS:")
        print("1. Verify trained model files in models/ directory")
        print("2. Run system integration tests with real ML models")
        print("3. Start paper trading with ML-enhanced signals")
        print("4. Monitor performance and retrain models periodically")
    else:
        print("\n🛠️ Please resolve the issues before proceeding")
