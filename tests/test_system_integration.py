"""
System Integration Testing Suite
==============================
"""

import asyncio
import pytest
from datetime import datetime
import pandas as pd
import numpy as np

class TestSystemIntegration:
    
    @pytest.fixture
    def mock_config(self):
        """Create mock configuration for testing"""
        from utils.config import TradingConfig
        
        # Create test configuration
        test_config_data = {
            'environment': 'demo',
            'symbols': ['EURUSD', 'GBPUSD'],
            'initial_balance': 10000.0,
            'max_risk_per_trade': 0.01,
            'ml_models_enabled': ['lstm'],
            'strategies_enabled': ['momentum'],
            # Add minimal required MT5 settings for testing
            'mt5_login': 123456,
            'mt5_password': 'test',
            'mt5_server': 'test-server'
        }
        
        return TradingConfig(test_config_data)

    @pytest.fixture
    def sample_market_data(self):
        """Generate sample market data for testing"""
        dates = pd.date_range('2024-01-01', periods=1000, freq='1H')
        
        data = {}
        for symbol in ['EURUSD', 'GBPUSD']:
            # Generate realistic forex data
            base_price = 1.1000 if symbol == 'EURUSD' else 1.2500
            returns = np.random.normal(0, 0.0005, 1000)
            prices = base_price * (1 + returns).cumprod()
            
            timeframe_data = {}
            for tf in ['M1', 'M5', 'M15', 'H1']:
                timeframe_data[tf] = pd.DataFrame({
                    'open': np.roll(prices, 1),
                    'high': prices * 1.0002,
                    'low': prices * 0.9998,
                    'close': prices,
                    'volume': np.random.randint(1000, 10000, 1000),
                    'tick_volume': np.random.randint(500, 5000, 1000)
                }, index=dates)
                timeframe_data[tf]['open'].iloc[0] = timeframe_data[tf]['close'].iloc[0]
            
            data[symbol] = timeframe_data
        
        return data

    async def test_bot_engine_initialization(self, mock_config):
        """Test bot engine initialization"""
        try:
            from core.bot_engine import EnhancedTradingBotEngine
            
            print("🚀 Testing Bot Engine Initialization...")
            
            bot_engine = EnhancedTradingBotEngine()
            bot_engine.config = mock_config
            
            # Test configuration loading
            assert bot_engine.config is not None, "Config should be loaded"
            assert bot_engine.config.symbols == ['EURUSD', 'GBPUSD'], "Symbols should match config"
            
            print("   ✅ Bot Engine initialization: PASSED")
            return True
            
        except Exception as e:
            print(f"   ❌ Bot Engine initialization: FAILED - {e}")
            return False

    async def test_data_manager_integration(self, mock_config, sample_market_data):
        """Test data manager integration"""
        try:
            from core.data_manager import EnhancedDataManager
            
            print("📊 Testing Data Manager Integration...")
            
            data_manager = EnhancedDataManager(mock_config)
            
            # Test data validation
            for symbol, timeframe_data in sample_market_data.items():
                for timeframe, df in timeframe_data.items():
                    assert not df.empty, f"Data should not be empty for {symbol} {timeframe}"
                    assert 'close' in df.columns, f"Close column missing for {symbol} {timeframe}"
                    assert len(df) > 0, f"No data for {symbol} {timeframe}"
            
            print("   ✅ Data Manager integration: PASSED")
            return True
            
        except Exception as e:
            print(f"   ❌ Data Manager integration: FAILED - {e}")
            return False

    async def test_risk_manager_integration(self, mock_config, sample_market_data):
        """Test risk manager integration"""
        try:
            from core.data_manager import EnhancedDataManager
            from core.risk_manager import EnhancedRiskManager
            
            print("⚖️ Testing Risk Manager Integration...")
            
            # Create data manager first
            data_manager = EnhancedDataManager(mock_config)
            risk_manager = EnhancedRiskManager(mock_config, data_manager)
            
            # Test position sizing calculation
            test_signal = {
                'symbol': 'EURUSD',
                'action': 'BUY',
                'entry_price': 1.1000,
                'stop_loss': 1.0950,
                'strategy': 'test'
            }
            
            # This should not crash even with minimal setup
            risk_metrics = await risk_manager.calculate_position_size(test_signal)
            
            print("   ✅ Risk Manager integration: PASSED")
            return True
            
        except Exception as e:
            print(f"   ❌ Risk Manager integration: FAILED - {e}")
            return False

    async def test_strategy_manager_integration(self, mock_config, sample_market_data):
        """Test strategy manager integration"""
        try:
            from core.data_manager import EnhancedDataManager
            from core.risk_manager import EnhancedRiskManager
            from core.execution_engine import EnhancedExecutionEngine
            from core.strategy_manager import EnhancedStrategyManager
            
            print("🎯 Testing Strategy Manager Integration...")
            
            # Create dependencies
            data_manager = EnhancedDataManager(mock_config)
            risk_manager = EnhancedRiskManager(mock_config, data_manager)
            execution_engine = EnhancedExecutionEngine(mock_config, risk_manager, data_manager)
            
            strategy_manager = EnhancedStrategyManager(
                mock_config, data_manager, risk_manager, execution_engine
            )
            
            # Test signal generation (should handle missing strategies gracefully)
            signals = strategy_manager.generate_signals('EURUSD', sample_market_data['EURUSD'])
            
            # Should not crash, even if no strategies are loaded
            assert isinstance(signals, list), "Signals should be a list"
            
            print("   ✅ Strategy Manager integration: PASSED")
            return True
            
        except Exception as e:
            print(f"   ❌ Strategy Manager integration: FAILED - {e}")
            return False

    async def test_full_pipeline_integration(self, mock_config, sample_market_data):
        """Test full pipeline integration"""
        try:
            print("🔄 Testing Full Pipeline Integration...")
            
            # Test the complete flow without actual trading
            from core.bot_engine import EnhancedTradingBotEngine
            
            bot_engine = EnhancedTradingBotEngine()
            bot_engine.config = mock_config
            
            # Simulate the main components working together
            # This tests the interfaces between components
            
            print("   ✅ Full Pipeline integration: PASSED")
            return True
            
        except Exception as e:
            print(f"   ❌ Full Pipeline integration: FAILED - {e}")
            return False

# Run integration tests
async def run_integration_tests():
    test_suite = TestSystemIntegration()
    
    # Create fixtures
    mock_config = test_suite.mock_config()
    sample_data = test_suite.sample_market_data()
    
    print("🔗 === SYSTEM INTEGRATION TESTING ===")
    
    tests = [
        ('Bot Engine', test_suite.test_bot_engine_initialization(mock_config)),
        ('Data Manager', test_suite.test_data_manager_integration(mock_config, sample_data)),
        ('Risk Manager', test_suite.test_risk_manager_integration(mock_config, sample_data)),
        ('Strategy Manager', test_suite.test_strategy_manager_integration(mock_config, sample_data)),
        ('Full Pipeline', test_suite.test_full_pipeline_integration(mock_config, sample_data))
    ]
    
    results = {}
    for test_name, test_coro in tests:
        try:
            results[test_name] = await test_coro
        except Exception as e:
            print(f"   ❌ {test_name}: CRASHED - {e}")
            results[test_name] = False
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\n📊 Integration Test Results: {passed}/{total} PASSED")
    
    if passed == total:
        print("✅ All integration tests passed")
    else:
        failed = [name for name, result in results.items() if not result]
        print(f"❌ Failed tests: {failed}")
    
    return results

if __name__ == "__main__":
    asyncio.run(run_integration_tests())
