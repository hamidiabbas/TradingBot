# =============================================================================
# BASE STRATEGY INTERFACE
# File: core/base_strategy.py
# =============================================================================

"""
Abstract base class for all trading strategies
Ensures consistent interface across ICT, RTM, SMC, and ML strategies
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass
import logging

# Import unified signals (fix import path)
try:
    from core.unified_signals import UnifiedTradingSignal, SignalType, StrategyType
except ImportError:
    from unified_signals import UnifiedTradingSignal, SignalType, StrategyType

logger = logging.getLogger(__name__)


@dataclass
class StrategyConfig:
    
    def analyze(self, data, symbol="EURUSD"):
        """Kelly-compatible analyze method for Base Strategy"""
        try:
            if data is None or data.empty or len(data) < 20:
                return {
                    'signal': 'HOLD',
                    'confidence': 0.0,
                    'price': 1.0,
                    'reason': 'Insufficient data'
                }
            
            # Use existing strategy logic if available
            if hasattr(self, 'generate_signal'):
                result = self.generate_signal(data, symbol)
                if isinstance(result, dict):
                    return result
            
            # Default implementation based on strategy type
            current_price = data['close'].iloc[-1]
            
            # Simple trend-following logic as fallback
            if len(data) >= 50:
                ma_20 = data['close'].rolling(20).mean().iloc[-1]
                ma_50 = data['close'].rolling(50).mean().iloc[-1]
                
                if current_price > ma_20 > ma_50:
                    return {
                        'signal': 'BUY',
                        'confidence': 0.65,
                        'price': current_price,
                        'reason': f'Base Strategy bullish trend'
                    }
                elif current_price < ma_20 < ma_50:
                    return {
                        'signal': 'SELL', 
                        'confidence': 0.65,
                        'price': current_price,
                        'reason': f'Base Strategy bearish trend'
                    }
            
            return {
                'signal': 'HOLD',
                'confidence': 0.4,
                'price': current_price,
                'reason': f'Base Strategy neutral'
            }
            
        except Exception as e:
            return {
                'signal': 'HOLD',
                'confidence': 0.0,
                'price': 1.0,
                'reason': f'Base Strategy error: {str(e)}'
            }

    """Configuration for strategy parameters"""
    name: str
    timeframe: str = "H1"
    symbol: str = "EURUSD"
    lookback_period: int = 20
    confidence_threshold: float = 0.6
    strength_threshold: float = 0.5
    risk_per_trade: float = 0.02
    max_positions: int = 1
    custom_params: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.custom_params is None:
            self.custom_params = {}


@dataclass
class MarketContext:
    """Shared market context for all strategies"""
    current_price: float
    timestamp: pd.Timestamp
    timeframe: str
    symbol: str
    volatility: float = 0.0
    trend_direction: str = "neutral"  # bullish, bearish, neutral
    market_session: str = "unknown"  # london, new_york, asia, overlap
    news_impact: str = "low"  # low, medium, high
    liquidity: str = "normal"  # low, normal, high
    support_levels: List[float] = None
    resistance_levels: List[float] = None
    
    def __post_init__(self):
        if self.support_levels is None:
            self.support_levels = []
        if self.resistance_levels is None:
            self.resistance_levels = []


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies
    
    All strategies must implement:
    1. analyze_market() - Perform market analysis
    2. generate_signals() - Generate trading signals
    3. update_parameters() - Update strategy parameters
    """
    
    def __init__(self, config: StrategyConfig):
        self.config = config
        self.name = config.name
        self.strategy_type = StrategyType.ICT  # Override in subclasses
        self.market_context: Optional[MarketContext] = None
        self.last_analysis: Optional[Dict[str, Any]] = None
        self.performance_metrics: Dict[str, float] = {}
        self.is_active = True
        
        # Logging
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.logger.info(f"Initialized {self.name} strategy")
    
    @abstractmethod
    def analyze_market(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze market conditions and patterns
        
        Args:
            data: OHLCV market data
            
        Returns:
            Dictionary containing analysis results
        """
        pass
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame, 
                        market_context: Optional[MarketContext] = None) -> List[UnifiedTradingSignal]:
        """
        Generate trading signals based on analysis
        
        Args:
            data: OHLCV market data
            market_context: Optional market context from other strategies
            
        Returns:
            List of UnifiedTradingSignal objects
        """
        pass
    
    @abstractmethod
    def update_parameters(self, new_params: Dict[str, Any]) -> bool:
        """
        Update strategy parameters
        
        Args:
            new_params: Dictionary of parameter updates
            
        Returns:
            True if update successful, False otherwise
        """
        pass
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Validate input data quality
        
        Args:
            data: OHLCV market data
            
        Returns:
            True if data is valid, False otherwise
        """
        try:
            # Check required columns
            required_columns = ['open', 'high', 'low', 'close']
            if not all(col in data.columns for col in required_columns):
                self.logger.error(f"Missing required columns: {required_columns}")
                return False
            
            # Check for sufficient data
            if len(data) < self.config.lookback_period:
                self.logger.warning(f"Insufficient data: {len(data)} < {self.config.lookback_period}")
                return False
            
            # Check OHLC consistency
            ohlc_valid = (
                (data['high'] >= data['low']) &
                (data['high'] >= data['open']) &
                (data['high'] >= data['close']) &
                (data['low'] <= data['open']) &
                (data['low'] <= data['close'])
            ).all()
            
            if not ohlc_valid:
                self.logger.error("OHLC data consistency check failed")
                return False
            
            # Check for excessive gaps or outliers
            price_changes = data['close'].pct_change().abs()
            if (price_changes > 0.1).any():  # 10% price changes
                self.logger.warning("Detected excessive price movements")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Data validation error: {e}")
            return False
    
    def calculate_position_size(self, entry_price: float, stop_loss: float, 
                              account_balance: float) -> float:
        """
        Calculate position size based on risk management
        
        Args:
            entry_price: Entry price for the trade
            stop_loss: Stop loss price
            account_balance: Current account balance
            
        Returns:
            Position size
        """
        try:
            risk_amount = account_balance * self.config.risk_per_trade
            price_diff = abs(entry_price - stop_loss)
            
            if price_diff == 0:
                return 0
            
            position_size = risk_amount / price_diff
            return position_size
            
        except Exception as e:
            self.logger.error(f"Position size calculation error: {e}")
            return 0
    
    def update_market_context(self, context: MarketContext) -> None:
        """Update shared market context"""
        self.market_context = context
        self.logger.debug(f"Updated market context: {context.trend_direction} trend")
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get strategy performance metrics"""
        return self.performance_metrics.copy()
    
    def update_performance_metrics(self, metrics: Dict[str, float]) -> None:
        """Update strategy performance metrics"""
        self.performance_metrics.update(metrics)
        self.logger.info(f"Updated performance metrics: {metrics}")
    
    def set_active(self, active: bool) -> None:
        """Enable/disable strategy"""
        self.is_active = active
        status = "activated" if active else "deactivated"
        self.logger.info(f"Strategy {status}")
    
    def create_signal(self, signal_type: SignalType, price: float, timestamp: pd.Timestamp,
                     confidence: float, strength: float, 
                     strategy_data: Optional[Dict[str, Any]] = None,
                     stop_loss: Optional[float] = None,
                     take_profit: Optional[float] = None) -> UnifiedTradingSignal:
        """
        Create a unified trading signal
        
        Args:
            signal_type: Type of signal (BUY/SELL/HOLD)
            price: Current market price
            timestamp: Signal timestamp
            confidence: Signal confidence (0.0-1.0)
            strength: Signal strength (0.0-1.0)
            strategy_data: Strategy-specific data
            stop_loss: Optional stop loss price
            take_profit: Optional take profit price
            
        Returns:
            UnifiedTradingSignal object
        """
        
        # Calculate risk-reward ratio if prices provided
        risk_reward_ratio = None
        if stop_loss and take_profit:
            if signal_type == SignalType.BUY:
                risk = abs(price - stop_loss)
                reward = abs(take_profit - price)
            else:  # SELL
                risk = abs(stop_loss - price)
                reward = abs(price - take_profit)
            
            if risk > 0:
                risk_reward_ratio = reward / risk
        
        signal = UnifiedTradingSignal(
            signal_type=signal_type,
            strategy_type=self.strategy_type,
            strategy_name=self.name,
            timestamp=timestamp,
            price=price,
            confidence=confidence,
            strength=strength,
            entry_price=price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_reward_ratio=risk_reward_ratio,
            timeframe=self.config.timeframe,
            symbol=self.config.symbol
        )
        
        # Add strategy-specific data
        if self.strategy_type == StrategyType.ICT:
            signal.ict_data = strategy_data
        elif self.strategy_type == StrategyType.RTM:
            signal.rtm_data = strategy_data
        elif self.strategy_type == StrategyType.SMC:
            signal.smc_data = strategy_data
        elif self.strategy_type == StrategyType.ML:
            signal.ml_data = strategy_data
        
        return signal
    
    def __str__(self) -> str:
        """String representation"""
        return f"{self.name} ({self.strategy_type.value})"
    
    def __repr__(self) -> str:
        """Detailed representation"""
        return f"{self.__class__.__name__}(name='{self.name}', active={self.is_active})"


class StrategyManager:
    """
    Manages multiple trading strategies
    """
    
    def __init__(self):
        self.strategies: Dict[str, BaseStrategy] = {}
        self.market_context: Optional[MarketContext] = None
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def add_strategy(self, strategy: BaseStrategy) -> bool:
        """
        Add a strategy to the manager
        
        Args:
            strategy: BaseStrategy instance
            
        Returns:
            True if added successfully, False otherwise
        """
        try:
            if strategy.name in self.strategies:
                self.logger.warning(f"Strategy '{strategy.name}' already exists, replacing")
            
            self.strategies[strategy.name] = strategy
            self.logger.info(f"Added strategy: {strategy.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding strategy: {e}")
            return False
    
    def remove_strategy(self, strategy_name: str) -> bool:
        """Remove a strategy from the manager"""
        try:
            if strategy_name in self.strategies:
                del self.strategies[strategy_name]
                self.logger.info(f"Removed strategy: {strategy_name}")
                return True
            else:
                self.logger.warning(f"Strategy '{strategy_name}' not found")
                return False
                
        except Exception as e:
            self.logger.error(f"Error removing strategy: {e}")
            return False
    
    def get_all_signals(self, data: pd.DataFrame) -> List[UnifiedTradingSignal]:
        """
        Get signals from all active strategies
        
        Args:
            data: Market data
            
        Returns:
            List of all signals from active strategies
        """
        all_signals = []
        
        # Update market context
        if len(data) > 0:
            self.update_market_context(data)
        
        for name, strategy in self.strategies.items():
            if strategy.is_active:
                try:
                    signals = strategy.generate_signals(data, self.market_context)
                    all_signals.extend(signals)
                    self.logger.debug(f"Got {len(signals)} signals from {name}")
                    
                except Exception as e:
                    self.logger.error(f"Error getting signals from {name}: {e}")
        
        self.logger.info(f"Generated {len(all_signals)} total signals")
        return all_signals
    
    def update_market_context(self, data: pd.DataFrame) -> None:
        """Update shared market context based on current data"""
        try:
            if len(data) == 0:
                return
            
            current_price = data['close'].iloc[-1]
            timestamp = data.index[-1]
            
            # Calculate basic market metrics
            returns = data['close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252) if len(returns) > 1 else 0
            
            # Determine trend direction using simple moving averages
            if len(data) >= 50:
                short_ma = data['close'].rolling(20).mean().iloc[-1]
                long_ma = data['close'].rolling(50).mean().iloc[-1]
                
                if short_ma > long_ma:
                    trend = "bullish"
                elif short_ma < long_ma:
                    trend = "bearish"
                else:
                    trend = "neutral"
            else:
                trend = "neutral"
            
            # Create market context
            self.market_context = MarketContext(
                current_price=current_price,
                timestamp=timestamp,
                timeframe="H1",  # Default, should be configurable
                symbol="UNKNOWN",  # Should be passed from data source
                volatility=volatility,
                trend_direction=trend
            )
            
            # Update context in all strategies
            for strategy in self.strategies.values():
                strategy.update_market_context(self.market_context)
                
        except Exception as e:
            self.logger.error(f"Error updating market context: {e}")
    
    def get_active_strategies(self) -> List[BaseStrategy]:
        """Get list of active strategies"""
        return [s for s in self.strategies.values() if s.is_active]
    
    def get_strategy_performance(self) -> Dict[str, Dict[str, float]]:
        """Get performance metrics for all strategies"""
        performance = {}
        for name, strategy in self.strategies.items():
            performance[name] = strategy.get_performance_metrics()
        return performance