"""
Quick System Integration Test
============================
"""

import asyncio
import sys

async def test_imports():
    """Test all critical imports"""
    try:
        # Core system
        from core.bot_engine import EnhancedTradingBotEngine
        from core.data_manager import EnhancedDataManager
        from core.strategy_manager import EnhancedStrategyManager
        from core.risk_manager import EnhancedRiskManager
        from core.execution_engine import EnhancedExecutionEngine
        
        # Configuration
        from utils.config import TradingConfig
        
        # Strategies
        from strategies import MomentumStrategy, MeanReversionStrategy, BreakoutStrategy
        
        print("✅ All core imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

async def test_configuration():
    """Test configuration system"""
    try:
        from utils.config import TradingConfig
        
        config = TradingConfig()
        is_valid = config.validate()
        
        print(f"✅ Configuration system: {'VALID' if is_valid else 'INVALID'}")
        return is_valid
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

async def main():
    print("🚀 === QUICK SYSTEM TEST ===\n")
    
    imports_ok = await test_imports()
    config_ok = await test_configuration()
    
    if imports_ok and config_ok:
        print("\n🎉 SYSTEM READY FOR FULL TESTING!")
        print("Next steps:")
        print("1. Configure your MT5 credentials in .env file")
        print("2. Run the complete system integration tests")
        print("3. Start with paper trading mode")
    else:
        print("\n❌ System has issues that need resolution")

if __name__ == "__main__":
    asyncio.run(main())
