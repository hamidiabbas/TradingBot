"""
Enhanced Low Memory Training Pipeline
===================================
Optimized approach that maximizes performance within memory constraints
"""

import asyncio
import os
import numpy as np
import pandas as pd
from datetime import datetime
import joblib
import h5py
import gc
import warnings
from typing import Tuple, Dict, Any
warnings.filterwarnings('ignore')

class EnhancedLowMemoryTrainer:
    """Enhanced trainer for memory-constrained systems with better performance"""
    
    def __init__(self, max_memory_mb: int = 800):
        self.max_memory_mb = max_memory_mb
        self.feature_columns = [
            'open', 'high', 'low', 'close', 'tick_volume',
            'sma_10', 'sma_20', 'ema_10', 'ema_20',
            'rsi', 'macd', 'bb_position', 'atr',
            'price_change', 'volatility'
        ]
        
    def load_optimized_data(self, h5_file_path: str, max_samples: int = 15000) -> pd.DataFrame:
        """Load optimized subset with better symbol/timeframe selection"""
        print(f"🔧 Loading enhanced dataset (max {max_samples:,} samples)...")
        
        try:
            all_data = []
            total_loaded = 0
            
            with h5py.File(h5_file_path, 'r') as f:
                symbols = list(f['data'].keys())
                
                # Prioritize major pairs for better patterns
                priority_symbols = ['EURUSD', 'GBPUSD', 'USDJPY']
                symbol_order = [s for s in priority_symbols if s in symbols] + [s for s in symbols if s not in priority_symbols]
                
                for symbol in symbol_order:
                    if total_loaded >= max_samples:
                        break
                        
                    symbol_group = f['data'][symbol]
                    
                    # Use H1 and H4 data for better patterns
                    for timeframe in ['H1', 'H4']:
                        if timeframe in symbol_group and total_loaded < max_samples:
                            tf_group = symbol_group[timeframe]
                            
                            # Load recent data (more relevant patterns)
                            data_length = len(tf_group['close'][:])
                            start_idx = max(0, data_length - 8000)  # Last 8000 bars
                            end_idx = data_length
                            
                            samples_needed = min(max_samples - total_loaded, end_idx - start_idx)
                            
                            # Convert nanoseconds to seconds for proper timestamps
                            time_data = tf_group['time'][start_idx:start_idx + samples_needed]
                            timestamps = pd.to_datetime(time_data // 1_000_000_000, unit='s', utc=True)
                            
                            data = {
                                'open': tf_group['open'][start_idx:start_idx + samples_needed],
                                'high': tf_group['high'][start_idx:start_idx + samples_needed],
                                'low': tf_group['low'][start_idx:start_idx + samples_needed],
                                'close': tf_group['close'][start_idx:start_idx + samples_needed],
                                'tick_volume': tf_group['tick_volume'][start_idx:start_idx + samples_needed],
                                'symbol': symbol,
                                'timeframe': timeframe
                            }
                            
                            df = pd.DataFrame(data, index=timestamps)
                            all_data.append(df)
                            total_loaded += len(df)
                            
                            print(f"   📊 {symbol} {timeframe}: {len(df)} samples")
                            
                            if total_loaded >= max_samples:
                                break
                
                if all_data:
                    combined_df = pd.concat(all_data, ignore_index=True)
                    combined_df = combined_df.sort_index()  # Sort by timestamp
                    print(f"✅ Total enhanced samples: {len(combined_df):,}")
                    return combined_df
                else:
                    return pd.DataFrame()
                    
        except Exception as e:
            print(f"❌ Enhanced data loading failed: {e}")
            return pd.DataFrame()
    
    def calculate_enhanced_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate enhanced technical indicators optimized for memory"""
        try:
            print("🔧 Calculating enhanced technical indicators...")
            
            # Ensure numeric data
            numeric_cols = ['open', 'high', 'low', 'close', 'tick_volume']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Fill missing values
            df = df.fillna(method='ffill').fillna(method='bfill').fillna(0)
            
            # Moving averages
            df['sma_10'] = df['close'].rolling(10, min_periods=1).mean()
            df['sma_20'] = df['close'].rolling(20, min_periods=1).mean()
            df['ema_10'] = df['close'].ewm(span=10, min_periods=1).mean()
            df['ema_20'] = df['close'].ewm(span=20, min_periods=1).mean()
            
            # MACD
            ema_12 = df['close'].ewm(span=12, min_periods=1).mean()
            ema_26 = df['close'].ewm(span=26, min_periods=1).mean()
            df['macd'] = ema_12 - ema_26
            
            # RSI
            delta = df['close'].diff()
            gain = delta.where(delta > 0, 0).rolling(14, min_periods=1).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14, min_periods=1).mean()
            rs = gain / loss.replace(0, np.inf)
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # Bollinger Bands position
            bb_middle = df['close'].rolling(20, min_periods=1).mean()
            bb_std = df['close'].rolling(20, min_periods=1).std()
            bb_upper = bb_middle + (bb_std * 2)
            bb_lower = bb_middle - (bb_std * 2)
            df['bb_position'] = (df['close'] - bb_lower) / (bb_upper - bb_lower).replace(0, 1)
            
            # ATR
            hl = df['high'] - df['low']
            hc = np.abs(df['high'] - df['close'].shift(1))
            lc = np.abs(df['low'] - df['close'].shift(1))
            tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
            df['atr'] = tr.rolling(14, min_periods=1).mean()
            
            # Price patterns
            df['price_change'] = df['close'].pct_change().fillna(0)
            df['volatility'] = df['price_change'].rolling(10, min_periods=1).std()
            
            # Clean data
            df = df.replace([np.inf, -np.inf], 0)
            df = df.fillna(0)
            
            print(f"   ✅ Enhanced indicators calculated")
            return df
            
        except Exception as e:
            print(f"❌ Enhanced feature calculation failed: {e}")
            return df
    
    def create_enhanced_features(self, df: pd.DataFrame, lookback: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """Create enhanced feature arrays with minimal lookback for memory efficiency"""
        try:
            print("🔧 Creating enhanced ML features...")
            
            # Calculate technical indicators
            df_processed = self.calculate_enhanced_features(df)
            
            # Get available features
            available_features = [col for col in self.feature_columns if col in df_processed.columns]
            
            if len(available_features) < 8:
                print(f"⚠️ Only {len(available_features)} features available")
                return np.array([]), np.array([])
            
            feature_data = df_processed[available_features].fillna(0)
            
            if len(feature_data) < lookback + 1:
                print(f"⚠️ Insufficient data: {len(feature_data)} rows")
                return np.array([]), np.array([])
            
            # Create samples with mini lookback window
            max_samples = min(len(feature_data) - lookback, 12000)  # Increased sample limit
            
            # Use 2D features with mini-sequence (memory efficient)
            X = np.zeros((max_samples, len(available_features) * lookback), dtype=np.float32)
            y = np.zeros((max_samples, 2), dtype=np.float32)  # Direction + magnitude
            
            print(f"   📊 Creating {max_samples} enhanced samples...")
            
            for i in range(max_samples):
                # Flatten mini-sequence for current sample
                sequence = feature_data.iloc[i:i + lookback].values.flatten()
                X[i] = sequence.astype(np.float32)
                
                # Enhanced target: direction and magnitude
                current_close = feature_data.iloc[i + lookback - 1]['close']
                next_close = feature_data.iloc[i + lookback]['close']
                
                # Direction (classification)
                direction = 1.0 if next_close > current_close else 0.0
                
                # Magnitude (for confidence weighting)
                magnitude = abs(next_close - current_close) / current_close if current_close != 0 else 0.0
                
                y[i] = [direction, magnitude]
            
            memory_mb = X.nbytes / 1024 / 1024
            print(f"✅ Enhanced features created: {X.shape}, Memory: {memory_mb:.1f} MB")
            
            if memory_mb > self.max_memory_mb:
                print(f"⚠️ Memory usage ({memory_mb:.1f} MB) exceeds limit ({self.max_memory_mb} MB)")
                # Reduce samples if needed
                target_samples = int(max_samples * self.max_memory_mb / memory_mb)
                X = X[:target_samples]
                y = y[:target_samples]
                print(f"   🔧 Reduced to {len(X)} samples for memory efficiency")
            
            return X, y
            
        except Exception as e:
            print(f"❌ Enhanced feature creation failed: {e}")
            return np.array([]), np.array([])
    
    def train_enhanced_models(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Train multiple enhanced models optimized for low memory"""
        try:
            print("🧠 Training Enhanced Model Suite...")
            
            from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
            from sklearn.linear_model import LogisticRegression
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import accuracy_score, classification_report
            
            # Prepare data
            y_direction = y[:, 0].astype(int)
            y_magnitude = y[:, 1]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_direction, test_size=0.25, random_state=42, stratify=y_direction
            )
            
            models = {}
            results = {}
            
            # Enhanced Random Forest
            print("   🌳 Training Enhanced Random Forest...")
            rf_model = RandomForestClassifier(
                n_estimators=50,          # Increased from 10
                max_depth=8,              # Increased from 5
                min_samples_split=10,     # Better generalization
                min_samples_leaf=5,       # Better generalization
                max_features='sqrt',      # Feature subsampling
                bootstrap=True,
                oob_score=True,
                random_state=42,
                n_jobs=1
            )
            
            rf_model.fit(X_train, y_train)
            
            rf_train_acc = rf_model.score(X_train, y_train)
            rf_test_acc = rf_model.score(X_test, y_test)
            rf_oob_score = rf_model.oob_score_
            
            models['random_forest'] = rf_model
            results['random_forest'] = {
                'train_accuracy': rf_train_acc,
                'test_accuracy': rf_test_acc,
                'oob_score': rf_oob_score,
                'overfitting_gap': rf_train_acc - rf_test_acc
            }
            
            print(f"      📊 RF Train: {rf_train_acc:.4f}, Test: {rf_test_acc:.4f}, OOB: {rf_oob_score:.4f}")
            
            # Gradient Boosting (powerful but memory efficient)
            print("   🚀 Training Gradient Boosting...")
            gb_model = GradientBoostingClassifier(
                n_estimators=30,          # Memory efficient
                max_depth=4,              # Prevent overfitting
                learning_rate=0.1,
                subsample=0.8,            # Stochastic boosting
                random_state=42
            )
            
            gb_model.fit(X_train, y_train)
            
            gb_train_acc = gb_model.score(X_train, y_train)
            gb_test_acc = gb_model.score(X_test, y_test)
            
            models['gradient_boosting'] = gb_model
            results['gradient_boosting'] = {
                'train_accuracy': gb_train_acc,
                'test_accuracy': gb_test_acc,
                'overfitting_gap': gb_train_acc - gb_test_acc
            }
            
            print(f"      📊 GB Train: {gb_train_acc:.4f}, Test: {gb_test_acc:.4f}")
            
            # Logistic Regression (baseline)
            print("   📈 Training Logistic Regression...")
            lr_model = LogisticRegression(
                random_state=42,
                max_iter=1000,
                solver='liblinear'  # Memory efficient
            )
            
            lr_model.fit(X_train, y_train)
            
            lr_train_acc = lr_model.score(X_train, y_train)
            lr_test_acc = lr_model.score(X_test, y_test)
            
            models['logistic_regression'] = lr_model
            results['logistic_regression'] = {
                'train_accuracy': lr_train_acc,
                'test_accuracy': lr_test_acc,
                'overfitting_gap': lr_train_acc - lr_test_acc
            }
            
            print(f"      📊 LR Train: {lr_train_acc:.4f}, Test: {lr_test_acc:.4f}")
            
            # Find best model
            best_model_name = max(results.keys(), key=lambda x: results[x]['test_accuracy'])
            best_model = models[best_model_name]
            best_accuracy = results[best_model_name]['test_accuracy']
            
            print(f"   🏆 Best model: {best_model_name} ({best_accuracy:.1%} accuracy)")
            
            # Save models
            os.makedirs('models/enhanced_low_memory', exist_ok=True)
            
            for model_name, model in models.items():
                model_path = f'models/enhanced_low_memory/{model_name}.pkl'
                joblib.dump(model, model_path)
                print(f"      💾 Saved: {model_path}")
            
            # Create ensemble prediction (simple voting)
            ensemble_predictions = []
            for model in models.values():
                pred = model.predict(X_test)
                ensemble_predictions.append(pred)
            
            # Majority voting
            ensemble_pred = np.array(ensemble_predictions).mean(axis=0)
            ensemble_pred = (ensemble_pred > 0.5).astype(int)
            ensemble_accuracy = accuracy_score(y_test, ensemble_pred)
            
            results['ensemble'] = {
                'test_accuracy': ensemble_accuracy,
                'voting_method': 'majority'
            }
            
            print(f"   🎭 Ensemble accuracy: {ensemble_accuracy:.4f}")
            
            # Overall summary
            summary = {
                'training_completed': True,
                'best_model': best_model_name,
                'best_accuracy': best_accuracy,
                'models_trained': list(results.keys()),
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'feature_count': X.shape[1],
                'results': results
            }
            
            return summary
            
        except Exception as e:
            print(f"❌ Enhanced model training failed: {e}")
            return {}

async def run_enhanced_low_memory_training():
    """Run enhanced low memory training pipeline"""
    print("🚀 === ENHANCED LOW MEMORY TRAINING PIPELINE ===")
    print("Optimized for better performance within memory constraints")
    print(f"📅 Started at: {datetime.utcnow()}")
    
    try:
        trainer = EnhancedLowMemoryTrainer(max_memory_mb=900)  # Slightly higher limit
        
        # Load enhanced dataset
        data_file = "data/training/mt5_historical_data.h5"
        
        if not os.path.exists(data_file):
            print(f"❌ Data file not found: {data_file}")
            return False
        
        df = trainer.load_optimized_data(data_file, max_samples=15000)
        
        if df.empty:
            print("❌ No data loaded")
            return False
        
        # Create enhanced features
        X, y = trainer.create_enhanced_features(df, lookback=8)  # Mini-lookback
        
        if X.size == 0:
            print("❌ No features created")
            return False
        
        # Train enhanced models
        results = trainer.train_enhanced_models(X, y)
        
        if results and results.get('training_completed'):
            # Save training summary
            summary_path = 'models/enhanced_low_memory/training_summary.json'
            with open(summary_path, 'w') as f:
                import json
                json.dump(results, f, indent=2)
            
            print("\n🏆 === ENHANCED TRAINING COMPLETED ===")
            print(f"✅ Best Model: {results['best_model']}")
            print(f"✅ Best Accuracy: {results['best_accuracy']:.1%}")
            print(f"✅ Models Trained: {len(results['models_trained'])}")
            print(f"✅ Training Samples: {results['training_samples']:,}")
            print(f"✅ Enhanced Features: {results['feature_count']}")
            
            print("\n📊 DETAILED RESULTS:")
            for model_name, model_results in results['results'].items():
                if 'test_accuracy' in model_results:
                    accuracy = model_results['test_accuracy']
                    gap = model_results.get('overfitting_gap', 0)
                    print(f"   {model_name}: {accuracy:.1%} accuracy (gap: {gap:.3f})")
            
            print(f"\n📁 Models saved in: models/enhanced_low_memory/")
            print(f"📋 Summary saved: {summary_path}")
            
            print("\n🎉 ENHANCED LOW MEMORY TRAINING SUCCESSFUL!")
            print("🚀 Your trading system now has improved ML models!")
            
            return True
        else:
            print("❌ Enhanced training failed")
            return False
            
    except Exception as e:
        print(f"❌ Enhanced training pipeline failed: {e}")
        return False
    
    finally:
        # Memory cleanup
        gc.collect()

if __name__ == "__main__":
    success = asyncio.run(run_enhanced_low_memory_training())
    
    if success:
        print("\n🎯 NEXT STEPS:")
        print("1. Test your enhanced models")
        print("2. Deploy to your powerful server for full enterprise training")
        print("3. Integrate with your trading strategies")
        print("4. Start paper trading to validate performance")
    else:
        print("\n🔧 Please resolve issues and try again")
