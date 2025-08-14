"""
Real Market Trading Implementation System
========================================

Professional-grade real trading system implementing all strategies
with live market data, risk management, and execution capabilities.

Features:
- Live market data integration
- Multi-strategy execution
- Real-time risk management
- Order management system
- Performance monitoring
- Error handling and recovery
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import time
from concurrent.futures import ThreadPoolExecutor
import yfinance as yf
import MetaTrader5 as mt5
import warnings

# Import all your strategies
from enhanced_momentum_strategy import EnhancedMomentumStrategy
from enhanced_mean_reversion_strategy import EnhancedMeanReversionStrategy
from enhanced_breakout_strategy import EnhancedBreakoutStrategy
from enhanced_ict_strategy import EnhancedICTStrategy
from enhanced_rtm_strategy import EnhancedRTMStrategy
from enhanced_scalping_strategy import EnhancedScalpingStrategy
from enhanced_volume_strategy import EnhancedVolumeStrategy
from enhanced_pivot_point_strategy import EnhancedPivotPointStrategy
from enhanced_news_strategy import EnhancedNewsStrategy
from enhanced_indicator_suite_strategy import EnhancedIndicatorSuiteStrategy

warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingMode(Enum):
    """Trading modes"""
    PAPER_TRADING = "paper_trading"
    LIVE_TRADING = "live_trading"
    SIMULATION = "simulation"

class OrderType(Enum):
    """Order types"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

class OrderStatus(Enum):
    """Order status"""
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    PARTIAL = "partial"

@dataclass
class TradingConfig:
    """Complete trading system configuration"""
    # Trading Mode
    trading_mode: TradingMode = TradingMode.PAPER_TRADING
    
    # Capital Management
    initial_capital: float = 100000.0
    max_risk_per_trade: float = 0.02  # 2%
    max_portfolio_risk: float = 0.10  # 10%
    max_positions: int = 10
    
    # Data Sources
    data_source: str = "yahoo"  # yahoo, mt5, alpaca
    symbols: List[str] = field(default_factory=lambda: ['EURUSD', 'GBPUSD', 'USDJPY'])
    timeframes: List[str] = field(default_factory=lambda: ['M15', 'H1', 'H4'])
    
    # Strategy Configuration
    enabled_strategies: List[str] = field(default_factory=lambda: [
        'EnhancedMomentumStrategy',
        'EnhancedMeanReversionStrategy',
        'EnhancedBreakoutStrategy',
        'EnhancedICTStrategy',
        'EnhancedVolumeStrategy'
    ])
    
    # Risk Management
    stop_loss_pips: int = 20
    take_profit_pips: int = 40
    trailing_stop: bool = True
    max_drawdown: float = 0.15  # 15%
    
    # Execution
    slippage_tolerance: float = 0.0002  # 2 pips
    execution_timeout: int = 30  # seconds
    
    # Monitoring
    update_frequency: int = 60  # seconds
    save_performance: bool = True
    performance_file: str = "live_performance.json"

@dataclass
class LiveTrade:
    """Live trade tracking"""
    trade_id: str
    strategy: str
    symbol: str
    direction: str
    entry_price: float
    quantity: float
    stop_loss: float
    take_profit: float
    entry_time: datetime
    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    pnl: float = 0.0
    status: str = "open"
    metadata: Dict[str, Any] = field(default_factory=dict)

class DataProvider:
    """Multi-source market data provider"""
    
    def __init__(self, source: str = "yahoo"):
        self.source = source
        self.data_cache = {}
        
    async def get_live_data(self, symbols: List[str], timeframes: List[str]) -> Dict[str, Dict[str, pd.DataFrame]]:
        """Get live market data"""
        try:
            data = {}
            
            for symbol in symbols:
                data[symbol] = {}
                for timeframe in timeframes:
                    if self.source == "yahoo":
                        df = await self._get_yahoo_data(symbol, timeframe)
                    elif self.source == "mt5":
                        df = await self._get_mt5_data(symbol, timeframe)
                    else:
                        df = await self._get_yahoo_data(symbol, timeframe)
                    
                    if df is not None and not df.empty:
                        data[symbol][timeframe] = df
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting live data: {e}")
            return {}
    
    async def _get_yahoo_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """Get data from Yahoo Finance"""
        try:
            # Convert forex symbols to Yahoo format
            if len(symbol) == 6 and symbol.isalpha():
                yahoo_symbol = f"{symbol[:3]}{symbol[3:]}=X"
            else:
                yahoo_symbol = symbol
            
            # Map timeframes
            interval_map = {
                'M1': '1m', 'M5': '5m', 'M15': '15m', 'M30': '30m',
                'H1': '1h', 'H4': '4h', 'D1': '1d'
            }
            
            interval = interval_map.get(timeframe, '1h')
            
            # Get data for last 500 periods
            ticker = yf.Ticker(yahoo_symbol)
            df = ticker.history(period="5d", interval=interval)
            
            if df.empty:
                return None
            
            # Standardize columns
            df.columns = [col.lower() for col in df.columns]
            df = df.rename(columns={'adj close': 'adj_close'})
            
            # Add volume if missing
            if 'volume' not in df.columns:
                df['volume'] = 1000
            
            return df.dropna()
            
        except Exception as e:
            logger.error(f"Error getting Yahoo data for {symbol}: {e}")
            return None
    
    async def _get_mt5_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """Get data from MetaTrader 5"""
        try:
            if not mt5.initialize():
                logger.error("MT5 initialization failed")
                return None
            
            # Map timeframes
            timeframe_map = {
                'M1': mt5.TIMEFRAME_M1, 'M5': mt5.TIMEFRAME_M5,
                'M15': mt5.TIMEFRAME_M15, 'M30': mt5.TIMEFRAME_M30,
                'H1': mt5.TIMEFRAME_H1, 'H4': mt5.TIMEFRAME_H4,
                'D1': mt5.TIMEFRAME_D1
            }
            
            tf = timeframe_map.get(timeframe, mt5.TIMEFRAME_H1)
            
            # Get rates
            rates = mt5.copy_rates_from_pos(symbol, tf, 0, 500)
            
            if rates is None:
                return None
            
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting MT5 data for {symbol}: {e}")
            return None

class OrderManager:
    """Order execution and management"""
    
    def __init__(self, trading_mode: TradingMode):
        self.trading_mode = trading_mode
        self.orders = {}
        self.trade_id_counter = 0
        
    async def place_order(self, symbol: str, direction: str, quantity: float,
                         order_type: OrderType = OrderType.MARKET,
                         price: Optional[float] = None,
                         stop_loss: Optional[float] = None,
                         take_profit: Optional[float] = None) -> str:
        """Place trading order"""
        try:
            self.trade_id_counter += 1
            trade_id = f"TRADE_{self.trade_id_counter:06d}"
            
            if self.trading_mode == TradingMode.PAPER_TRADING:
                return await self._place_paper_order(
                    trade_id, symbol, direction, quantity, order_type,
                    price, stop_loss, take_profit
                )
            elif self.trading_mode == TradingMode.LIVE_TRADING:
                return await self._place_live_order(
                    trade_id, symbol, direction, quantity, order_type,
                    price, stop_loss, take_profit
                )
            else:
                return await self._place_simulation_order(
                    trade_id, symbol, direction, quantity, order_type,
                    price, stop_loss, take_profit
                )
                
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return ""
    
    async def _place_paper_order(self, trade_id: str, symbol: str, direction: str,
                                quantity: float, order_type: OrderType,
                                price: Optional[float], stop_loss: Optional[float],
                                take_profit: Optional[float]) -> str:
        """Place paper trading order"""
        try:
            # Get current market price (simplified)
            current_price = price or 1.1000  # Would get from live data
            
            order = {
                'trade_id': trade_id,
                'symbol': symbol,
                'direction': direction,
                'quantity': quantity,
                'order_type': order_type.value,
                'entry_price': current_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'timestamp': datetime.now(),
                'status': OrderStatus.FILLED.value
            }
            
            self.orders[trade_id] = order
            logger.info(f"Paper order placed: {trade_id}")
            return trade_id
            
        except Exception as e:
            logger.error(f"Error placing paper order: {e}")
            return ""
    
    async def _place_live_order(self, trade_id: str, symbol: str, direction: str,
                               quantity: float, order_type: OrderType,
                               price: Optional[float], stop_loss: Optional[float],
                               take_profit: Optional[float]) -> str:
        """Place live trading order"""
        try:
            # This would integrate with your broker's API
            # Example for MT5 integration
            if not mt5.initialize():
                logger.error("MT5 not initialized")
                return ""
            
            # Prepare order request
            action = mt5.TRADE_ACTION_DEAL
            type_buy = mt5.ORDER_TYPE_BUY if direction == 'long' else mt5.ORDER_TYPE_SELL
            
            request = {
                "action": action,
                "symbol": symbol,
                "volume": quantity,
                "type": type_buy,
                "deviation": 20,
                "magic": 234000,
                "comment": f"Strategy order {trade_id}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            if stop_loss:
                request["sl"] = stop_loss
            if take_profit:
                request["tp"] = take_profit
            
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"Order failed: {result.comment}")
                return ""
            
            self.orders[trade_id] = {
                'trade_id': trade_id,
                'mt5_order': result.order,
                'symbol': symbol,
                'direction': direction,
                'quantity': quantity,
                'entry_price': result.price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'timestamp': datetime.now(),
                'status': OrderStatus.FILLED.value
            }
            
            logger.info(f"Live order placed: {trade_id}")
            return trade_id
            
        except Exception as e:
            logger.error(f"Error placing live order: {e}")
            return ""
    
    async def _place_simulation_order(self, trade_id: str, symbol: str, direction: str,
                                     quantity: float, order_type: OrderType,
                                     price: Optional[float], stop_loss: Optional[float],
                                     take_profit: Optional[float]) -> str:
        """Place simulation order"""
        # Similar to paper trading but with more realistic simulation
        return await self._place_paper_order(
            trade_id, symbol, direction, quantity, order_type,
            price, stop_loss, take_profit
        )
    
    async def close_order(self, trade_id: str, price: Optional[float] = None) -> bool:
        """Close existing order"""
        try:
            if trade_id not in self.orders:
                logger.error(f"Order not found: {trade_id}")
                return False
            
            order = self.orders[trade_id]
            
            if self.trading_mode == TradingMode.LIVE_TRADING:
                # Close live order using MT5
                if not mt5.initialize():
                    return False
                
                # Get position
                positions = mt5.positions_get(symbol=order['symbol'])
                if not positions:
                    return False
                
                position = positions[0]
                
                # Close position
                close_request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": order['symbol'],
                    "volume": position.volume,
                    "type": mt5.ORDER_TYPE_SELL if position.type == 0 else mt5.ORDER_TYPE_BUY,
                    "position": position.ticket,
                    "deviation": 20,
                    "magic": 234000,
                    "comment": f"Close {trade_id}",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
                
                result = mt5.order_send(close_request)
                success = result.retcode == mt5.TRADE_RETCODE_DONE
            else:
                # Paper/simulation close
                success = True
            
            if success:
                order['status'] = OrderStatus.FILLED.value
                order['exit_time'] = datetime.now()
                if price:
                    order['exit_price'] = price
                logger.info(f"Order closed: {trade_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error closing order: {e}")
            return False

class RealTimeRiskManager:
    """Real-time risk management system"""
    
    def __init__(self, config: TradingConfig):
        self.config = config
        self.current_capital = config.initial_capital
        self.active_trades = {}
        self.daily_pnl = 0.0
        self.max_drawdown = 0.0
        self.peak_capital = config.initial_capital
        
    def can_open_position(self, symbol: str, direction: str, quantity: float,
                         entry_price: float, stop_loss: float) -> Tuple[bool, str]:
        """Check if position can be opened"""
        try:
            # Check maximum positions
            if len(self.active_trades) >= self.config.max_positions:
                return False, "Maximum positions reached"
            
            # Calculate position risk
            risk_per_trade = abs(entry_price - stop_loss) * quantity
            risk_percentage = risk_per_trade / self.current_capital
            
            # Check risk per trade
            if risk_percentage > self.config.max_risk_per_trade:
                return False, f"Risk per trade too high: {risk_percentage:.2%}"
            
            # Check portfolio risk
            total_risk = sum(
                abs(trade['entry_price'] - trade['stop_loss']) * trade['quantity']
                for trade in self.active_trades.values()
            ) + risk_per_trade
            
            portfolio_risk = total_risk / self.current_capital
            if portfolio_risk > self.config.max_portfolio_risk:
                return False, f"Portfolio risk too high: {portfolio_risk:.2%}"
            
            # Check maximum drawdown
            current_drawdown = (self.peak_capital - self.current_capital) / self.peak_capital
            if current_drawdown > self.config.max_drawdown:
                return False, f"Maximum drawdown exceeded: {current_drawdown:.2%}"
            
            return True, "Position approved"
            
        except Exception as e:
            logger.error(f"Error checking position: {e}")
            return False, "Risk check failed"
    
    def add_trade(self, trade: LiveTrade):
        """Add trade to tracking"""
        self.active_trades[trade.trade_id] = {
            'trade_id': trade.trade_id,
            'symbol': trade.symbol,
            'direction': trade.direction,
            'entry_price': trade.entry_price,
            'quantity': trade.quantity,
            'stop_loss': trade.stop_loss,
            'take_profit': trade.take_profit,
            'entry_time': trade.entry_time
        }
    
    def remove_trade(self, trade_id: str, exit_price: float):
        """Remove trade and update capital"""
        try:
            if trade_id in self.active_trades:
                trade = self.active_trades[trade_id]
                
                # Calculate PnL
                if trade['direction'] == 'long':
                    pnl = (exit_price - trade['entry_price']) * trade['quantity']
                else:
                    pnl = (trade['entry_price'] - exit_price) * trade['quantity']
                
                # Update capital
                self.current_capital += pnl
                self.daily_pnl += pnl
                
                # Update peak capital
                if self.current_capital > self.peak_capital:
                    self.peak_capital = self.current_capital
                
                # Calculate current drawdown
                current_drawdown = (self.peak_capital - self.current_capital) / self.peak_capital
                if current_drawdown > self.max_drawdown:
                    self.max_drawdown = current_drawdown
                
                del self.active_trades[trade_id]
                logger.info(f"Trade removed: {trade_id}, PnL: {pnl:.2f}")
                
        except Exception as e:
            logger.error(f"Error removing trade: {e}")
    
    def get_risk_summary(self) -> Dict[str, Any]:
        """Get current risk summary"""
        try:
            total_exposure = sum(
                trade['entry_price'] * trade['quantity']
                for trade in self.active_trades.values()
            )
            
            total_risk = sum(
                abs(trade['entry_price'] - trade['stop_loss']) * trade['quantity']
                for trade in self.active_trades.values()
            )
            
            return {
                'current_capital': self.current_capital,
                'daily_pnl': self.daily_pnl,
                'active_trades': len(self.active_trades),
                'total_exposure': total_exposure,
                'total_risk': total_risk,
                'portfolio_risk_percentage': total_risk / self.current_capital if self.current_capital > 0 else 0,
                'current_drawdown': (self.peak_capital - self.current_capital) / self.peak_capital,
                'max_drawdown': self.max_drawdown,
                'available_capital': self.current_capital - total_exposure
            }
            
        except Exception as e:
            logger.error(f"Error getting risk summary: {e}")
            return {}

class LiveTradingSystem:
    """Main live trading system"""
    
    def __init__(self, config: TradingConfig):
        self.config = config
        self.data_provider = DataProvider(config.data_source)
        self.order_manager = OrderManager(config.trading_mode)
        self.risk_manager = RealTimeRiskManager(config)
        
        # Initialize strategies
        self.strategies = {}
        self._initialize_strategies()
        
        # Performance tracking
        self.performance_data = []
        self.last_update = datetime.now()
        
        # Control flags
        self.running = False
        self.paused = False
        
    def _initialize_strategies(self):
        """Initialize all enabled strategies"""
        try:
            strategy_classes = {
                'EnhancedMomentumStrategy': EnhancedMomentumStrategy,
                'EnhancedMeanReversionStrategy': EnhancedMeanReversionStrategy,
                'EnhancedBreakoutStrategy': EnhancedBreakoutStrategy,
                'EnhancedICTStrategy': EnhancedICTStrategy,
                'EnhancedRTMStrategy': EnhancedRTMStrategy,
                'EnhancedScalpingStrategy': EnhancedScalpingStrategy,
                'EnhancedVolumeStrategy': EnhancedVolumeStrategy,
                'EnhancedPivotPointStrategy': EnhancedPivotPointStrategy,
                'EnhancedNewsStrategy': EnhancedNewsStrategy,
                'EnhancedIndicatorSuiteStrategy': EnhancedIndicatorSuiteStrategy
            }
            
            for strategy_name in self.config.enabled_strategies:
                if strategy_name in strategy_classes:
                    strategy_class = strategy_classes[strategy_name]
                    
                    # Default configuration for each strategy
                    strategy_config = {
                        'timeframes': self.config.timeframes,
                        'symbols': self.config.symbols,
                        'risk_per_trade': self.config.max_risk_per_trade
                    }
                    
                    strategy = strategy_class(strategy_name, strategy_config)
                    self.strategies[strategy_name] = strategy
                    
                    logger.info(f"Initialized strategy: {strategy_name}")
            
        except Exception as e:
            logger.error(f"Error initializing strategies: {e}")
    
    async def start_trading(self):
        """Start the live trading system"""
        try:
            logger.info("Starting Live Trading System...")
            self.running = True
            
            # Initialize all strategies
            for name, strategy in self.strategies.items():
                try:
                    await strategy.initialize()
                    logger.info(f"Strategy {name} initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize strategy {name}: {e}")
            
            # Main trading loop
            while self.running:
                if not self.paused:
                    await self._trading_cycle()
                
                # Wait for next update
                await asyncio.sleep(self.config.update_frequency)
            
            logger.info("Live Trading System stopped")
            
        except Exception as e:
            logger.error(f"Error in trading system: {e}")
            self.running = False
    
    async def _trading_cycle(self):
        """Single trading cycle"""
        try:
            # Get live market data
            market_data = await self.data_provider.get_live_data(
                self.config.symbols, self.config.timeframes
            )
            
            if not market_data:
                logger.warning("No market data received")
                return
            
            # Generate signals from all strategies
            all_signals = []
            for name, strategy in self.strategies.items():
                try:
                    signals = strategy.generate_signals(market_data)
                    for signal in signals:
                        signal.metadata['strategy'] = name
                    all_signals.extend(signals)
                except Exception as e:
                    logger.error(f"Error generating signals from {name}: {e}")
            
            # Process signals and execute trades
            await self._process_signals(all_signals)
            
            # Update performance tracking
            self._update_performance()
            
            # Check for exit conditions on existing trades
            await self._check_exit_conditions(market_data)
            
            # Log system status
            risk_summary = self.risk_manager.get_risk_summary()
            logger.info(f"Capital: {risk_summary['current_capital']:.2f}, "
                       f"Active Trades: {risk_summary['active_trades']}, "
                       f"Daily PnL: {risk_summary['daily_pnl']:.2f}")
            
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}")
    
    async def _process_signals(self, signals: List[Any]):
        """Process trading signals and execute orders"""
        try:
            # Filter and rank signals
            valid_signals = [s for s in signals if s.strength > 0.6]
            valid_signals.sort(key=lambda x: x.strength, reverse=True)
            
            for signal in valid_signals[:5]:  # Limit to top 5 signals
                await self._execute_signal(signal)
                
        except Exception as e:
            logger.error(f"Error processing signals: {e}")
    
    async def _execute_signal(self, signal):
        """Execute individual signal"""
        try:
            symbol = signal.symbol
            direction = 'long' if signal.direction == 'bullish' else 'short'
            
            # Get current price
            current_price = signal.level
            
            # Calculate position size based on risk
            risk_amount = self.risk_manager.current_capital * self.config.max_risk_per_trade
            
            # Calculate stop loss and take profit
            if direction == 'long':
                stop_loss = current_price - (self.config.stop_loss_pips * 0.0001)
                take_profit = current_price + (self.config.take_profit_pips * 0.0001)
            else:
                stop_loss = current_price + (self.config.stop_loss_pips * 0.0001)
                take_profit = current_price - (self.config.take_profit_pips * 0.0001)
            
            # Calculate position size
            risk_per_unit = abs(current_price - stop_loss)
            quantity = risk_amount / risk_per_unit if risk_per_unit > 0 else 0
            
            # Check if position can be opened
            can_open, reason = self.risk_manager.can_open_position(
                symbol, direction, quantity, current_price, stop_loss
            )
            
            if not can_open:
                logger.warning(f"Cannot open position: {reason}")
                return
            
            # Place order
            trade_id = await self.order_manager.place_order(
                symbol=symbol,
                direction=direction,
                quantity=quantity,
                order_type=OrderType.MARKET,
                stop_loss=stop_loss,
                take_profit=take_profit
            )
            
            if trade_id:
                # Create trade record
                trade = LiveTrade(
                    trade_id=trade_id,
                    strategy=signal.metadata.get('strategy', 'Unknown'),
                    symbol=symbol,
                    direction=direction,
                    entry_price=current_price,
                    quantity=quantity,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    entry_time=datetime.now(),
                    metadata=signal.metadata
                )
                
                # Add to risk manager
                self.risk_manager.add_trade(trade)
                
                logger.info(f"Trade executed: {trade_id} - {symbol} {direction} @ {current_price}")
            
        except Exception as e:
            logger.error(f"Error executing signal: {e}")
    
    async def _check_exit_conditions(self, market_data):
        """Check exit conditions for active trades"""
        try:
            for trade_id, trade_info in list(self.risk_manager.active_trades.items()):
                symbol = trade_info['symbol']
                
                # Get current price
                if symbol in market_data and self.config.timeframes[0] in market_data[symbol]:
                    current_data = market_data[symbol][self.config.timeframes[0]]
                    current_price = current_data['close'].iloc[-1]
                    
                    # Check stop loss and take profit
                    should_exit = False
                    exit_reason = ""
                    
                    if trade_info['direction'] == 'long':
                        if current_price <= trade_info['stop_loss']:
                            should_exit = True
                            exit_reason = "Stop Loss"
                        elif current_price >= trade_info['take_profit']:
                            should_exit = True
                            exit_reason = "Take Profit"
                    else:
                        if current_price >= trade_info['stop_loss']:
                            should_exit = True
                            exit_reason = "Stop Loss"
                        elif current_price <= trade_info['take_profit']:
                            should_exit = True
                            exit_reason = "Take Profit"
                    
                    if should_exit:
                        success = await self.order_manager.close_order(trade_id, current_price)
                        if success:
                            self.risk_manager.remove_trade(trade_id, current_price)
                            logger.info(f"Trade closed: {trade_id} - {exit_reason}")
                        
        except Exception as e:
            logger.error(f"Error checking exit conditions: {e}")
    
    def _update_performance(self):
        """Update performance tracking"""
        try:
            if self.config.save_performance:
                risk_summary = self.risk_manager.get_risk_summary()
                performance_snapshot = {
                    'timestamp': datetime.now().isoformat(),
                    'capital': risk_summary['current_capital'],
                    'daily_pnl': risk_summary['daily_pnl'],
                    'active_trades': risk_summary['active_trades'],
                    'drawdown': risk_summary['current_drawdown'],
                    'portfolio_risk': risk_summary['portfolio_risk_percentage']
                }
                
                self.performance_data.append(performance_snapshot)
                
                # Save to file periodically
                if len(self.performance_data) % 10 == 0:
                    with open(self.config.performance_file, 'w') as f:
                        json.dump(self.performance_data, f, indent=2)
                        
        except Exception as e:
            logger.error(f"Error updating performance: {e}")
    
    def stop_trading(self):
        """Stop the trading system"""
        self.running = False
        logger.info("Trading system stop requested")
    
    def pause_trading(self):
        """Pause trading"""
        self.paused = True
        logger.info("Trading system paused")
    
    def resume_trading(self):
        """Resume trading"""
        self.paused = False
        logger.info("Trading system resumed")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        try:
            risk_summary = self.risk_manager.get_risk_summary()
            return {
                'running': self.running,
                'paused': self.paused,
                'trading_mode': self.config.trading_mode.value,
                'enabled_strategies': list(self.strategies.keys()),
                'risk_summary': risk_summary,
                'last_update': self.last_update.isoformat(),
                'performance_snapshots': len(self.performance_data)
            }
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return {}

# Example usage
async def main():
    """Main function to start live trading"""
    
    # Configuration
    config = TradingConfig(
        trading_mode=TradingMode.PAPER_TRADING,  # Start with paper trading
        initial_capital=100000.0,
        max_risk_per_trade=0.02,
        symbols=['EURUSD', 'GBPUSD', 'USDJPY'],
        timeframes=['M15', 'H1', 'H4'],
        enabled_strategies=[
            'EnhancedMomentumStrategy',
            'EnhancedMeanReversionStrategy',
            'EnhancedBreakoutStrategy',
            'EnhancedICTStrategy',
            'EnhancedVolumeStrategy'
        ]
    )
    
    # Create and start trading system
    trading_system = LiveTradingSystem(config)
    
    try:
        # Start trading
        await trading_system.start_trading()
    except KeyboardInterrupt:
        print("Stopping trading system...")
        trading_system.stop_trading()

if __name__ == "__main__":
    asyncio.run(main())
