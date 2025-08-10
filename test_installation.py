"""
Installation Verification Script
==============================
"""

def test_core_imports():
    """Test core library imports"""
    try:
        import pandas as pd
        import numpy as np
        import sklearn
        import tensorflow as tf
        import MetaTrader5 as mt5
        import asyncio
        import yaml
        import psutil
        
        print("✅ Core libraries imported successfully")
        print(f"   📊 Pandas: {pd.__version__}")
        print(f"   🔢 NumPy: {np.__version__}")
        print(f"   🤖 Scikit-learn: {sklearn.__version__}")
        print(f"   🧠 TensorFlow: {tf.__version__}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_trading_specific():
    """Test trading-specific imports"""
    try:
        import pandas_ta as ta
        print(f"✅ Pandas-TA: {ta.version}")
        
        # Test TA-Lib
        import talib
        print("✅ TA-Lib imported successfully")
        
        # Test Smart Money Concepts
        import smartmoneyconcepts as smc
        print("✅ Smart Money Concepts imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"⚠️ Trading library error: {e}")
        return False

async def test_async_functionality():
    """Test async functionality"""
    try:
        await asyncio.sleep(0.1)
        print("✅ Async functionality working")
        return True
    except Exception as e:
        print(f"❌ Async test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 === INSTALLATION VERIFICATION ===\n")
    
    core_success = test_core_imports()
    trading_success = test_trading_specific()
    
    print("\n⚡ Testing async functionality...")
    async_success = asyncio.run(test_async_functionality())
    
    print(f"\n📊 === VERIFICATION RESULTS ===")
    print(f"✅ Core Libraries: {'PASSED' if core_success else 'FAILED'}")
    print(f"📈 Trading Libraries: {'PASSED' if trading_success else 'FAILED'}")
    print(f"⚡ Async Support: {'PASSED' if async_success else 'FAILED'}")
    
    if core_success and async_success:
        print("\n🎉 INSTALLATION VERIFICATION SUCCESSFUL!")
        print("🚀 Your environment is ready for the trading system!")
        return True
    else:
        print("\n⚠️ Some issues found. Please resolve before proceeding.")
        return False

if __name__ == "__main__":
    main()
