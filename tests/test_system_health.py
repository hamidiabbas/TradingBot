"""
System Health Check Suite
========================
"""

import sys
import importlib
import pandas as pd
import numpy as np

class SystemHealthChecker:
    
    def check_python_version(self):
        """Check Python version compatibility"""
        print("🐍 Checking Python Version...")
        
        version = sys.version_info
        if version.major == 3 and version.minor >= 8:
            print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
            return True
        else:
            print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
            return False
    
    def check_required_libraries(self):
        """Check all required libraries are installed"""
        print("📚 Checking Required Libraries...")
        
        required_libs = {
            'pandas': 'Data manipulation',
            'numpy': 'Numerical computing',
            'scikit-learn': 'Machine learning',
            'tensorflow': 'Deep learning',
            'MetaTrader5': 'MT5 integration',
            'asyncio': 'Async operations',
            'logging': 'System logging',
            'datetime': 'Time handling',
            'concurrent.futures': 'Parallel processing',
            'threading': 'Threading support'
        }
        
        results = {}
        for lib, description in required_libs.items():
            try:
                if lib == 'scikit-learn':
                    importlib.import_module('sklearn')
                else:
                    importlib.import_module(lib)
                print(f"   ✅ {lib} - {description}")
                results[lib] = True
            except ImportError:
                print(f"   ❌ {lib} - {description} - NOT INSTALLED")
                results[lib] = False
        
        passed = sum(results.values())
        total = len(results)
        print(f"   📊 Libraries: {passed}/{total} available")
        
        return passed == total
    
    def check_ml_libraries_compatibility(self):
        """Check ML libraries work together"""
        print("🧠 Checking ML Libraries Compatibility...")
        
        try:
            # Test pandas operations
            df = pd.DataFrame({'test': [1, 2, 3, 4, 5]})
            assert len(df) == 5, "Pandas not working correctly"
            
            # Test numpy operations
            arr = np.array([1, 2, 3, 4, 5])
            assert np.mean(arr) == 3.0, "Numpy not working correctly"
            
            # Test scikit-learn basic functionality
            from sklearn.linear_model import LinearRegression
            model = LinearRegression()
            
            # Test tensorflow basic functionality
            import tensorflow as tf
            tensor = tf.constant([1, 2, 3, 4, 5])
            
            print("   ✅ ML Libraries compatibility verified")
            return True
            
        except Exception as e:
            print(f"   ❌ ML Libraries compatibility failed: {e}")
            return False
    
    def check_file_structure(self):
        """Check required file structure exists"""
        print("📁 Checking File Structure...")
        
        required_paths = [
            'core/',
            'core/__init__.py',
            'core/bot_engine.py',
            'core/data_manager.py',
            'core/strategy_manager.py',
            'core/risk_manager.py',
            'core/execution_engine.py',
            'ml_models/',
            'ml_models/__init__.py',
            'ml_models/lstm_model.py',
            'ml_models/random_forest_model.py',
            'ml_models/svm_model.py',
            'ml_models/ensemble_model.py',
            'strategies/',
            'strategies/__init__.py',
            'utils/',
            'utils/__init__.py',
            'utils/config.py',
            'utils/logger.py'
        ]
        
        missing_files = []
        for path in required_paths:
            try:
                import os
                if os.path.exists(path):
                    print(f"   ✅ {path}")
                else:
                    print(f"   ❌ {path} - MISSING")
                    missing_files.append(path)
            except:
                missing_files.append(path)
        
        if missing_files:
            print(f"   📊 Missing files: {len(missing_files)}/{len(required_paths)}")
            return False
        else:
            print(f"   📊 File structure: Complete")
            return True
    
    def check_configuration_validity(self):
        """Check configuration system works"""
        print("⚙️ Checking Configuration System...")
        
        try:
            from utils.config import TradingConfig
            
            # Test default configuration
            config = TradingConfig()
            
            # Check required attributes exist
            required_attrs = [
                'symbols', 'initial_balance', 'max_risk_per_trade',
                'ml_models_enabled', 'strategies_enabled'
            ]
            
            for attr in required_attrs:
                if not hasattr(config, attr):
                    print(f"   ❌ Missing config attribute: {attr}")
                    return False
            
            # Test configuration validation
            is_valid = config.validate()
            if not is_valid:
                print("   ❌ Configuration validation failed")
                return False
            
            print("   ✅ Configuration system working")
            return True
            
        except Exception as e:
            print(f"   ❌ Configuration system failed: {e}")
            return False
    
    def run_comprehensive_health_check(self):
        """Run complete system health check"""
        print("🏥 === SYSTEM HEALTH CHECK ===")
        
        checks = [
            ('Python Version', self.check_python_version()),
            ('Required Libraries', self.check_required_libraries()),
            ('ML Libraries Compatibility', self.check_ml_libraries_compatibility()),
            ('File Structure', self.check_file_structure()),
            ('Configuration System', self.check_configuration_validity())
        ]
        
        results = {name: result for name, result in checks}
        passed = sum(results.values())
        total = len(results)
        
        print(f"\n🏥 === HEALTH CHECK SUMMARY ===")
        print(f"📊 Overall Health: {passed}/{total} checks passed")
        
        if passed == total:
            print("✅ System is healthy and ready for testing")
            return True
        else:
            failed_checks = [name for name, result in results.items() if not result]
            print(f"❌ Failed checks: {failed_checks}")
            print("⚠️ Please resolve these issues before running the system")
            return False

# Run health check
if __name__ == "__main__":
    health_checker = SystemHealthChecker()
    is_healthy = health_checker.run_comprehensive_health_check()
    
    if is_healthy:
        print("\n🚀 System is ready for integration testing!")
    else:
        print("\n🛠️ Please fix the identified issues first.")
