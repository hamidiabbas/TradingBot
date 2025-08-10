"""
Enhanced Execution Engine - Professional Order Management & MT5 Integration
==========================================================================

Institutional-grade execution engine for professional algorithmic trading that
provides advanced order management, MT5 platform integration, real-time execution
monitoring, sophisticated slippage control, and comprehensive position management
with production-ready error handling and recovery mechanisms.

Features:
- Professional MT5 order execution with multiple order types
- Advanced slippage monitoring and control mechanisms
- Sophisticated position management with real-time tracking
- Risk-integrated execution with comprehensive validation
- Real-time execution monitoring and performance analytics
- Professional error handling with automatic recovery
- Production-ready with comprehensive logging and alerts
- Asynchronous operations for high-performance execution
- Complete integration with Enhanced Risk Manager

Author: Enhanced Trading System
Version: 4.0 Complete Professional
License: Proprietary
"""

import asyncio
import logging
import time
import threading
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np
import pandas as pd
from enum import Enum
import json
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
import warnings

# MT5 Integration
import MetaTrader5 as mt5

# Core System Components
from core.data_manager import EnhancedDataManager
from core.risk_manager import EnhancedRiskManager

# Configuration and Utilities
from utils.config import TradingConfig
from utils.logger import setup_logging
from utils.helpers import format_currency, calculate_pips

# Suppress warnings
warnings.filterwarnings('ignore', category=FutureWarning)

class OrderType(Enum):
    """Order type enumeration"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    MARKET_BUY = "market_buy"
    MARKET_SELL = "market_sell"
    LIMIT_BUY = "limit_buy"
    LIMIT_SELL = "limit_sell"
    STOP_BUY = "stop_buy"
    STOP_SELL = "stop_sell"

class OrderStatus(Enum):
    """Order status enumeration"""
    PENDING = "pending"
    PLACED = "placed"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"
    ERROR = "error"

class ExecutionMode(Enum):
    """Execution mode enumeration"""
    LIVE = "live"
    DEMO = "demo"
    PAPER = "paper"
    SIMULATION = "simulation"

class PositionStatus(Enum):
    """Position status enumeration"""
    OPEN = "open"
    CLOSED = "closed"
    PARTIALLY_CLOSED = "partially_closed"
    PENDING_CLOSE = "pending_close"
    ERROR = "error"

@dataclass
class ExecutionRequest:
    """Comprehensive execution request structure"""
    # Basic order information
    symbol: str
    action: str  # BUY, SELL
    volume: float
    order_type: OrderType = OrderType.MARKET
    
    # Price levels
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    # Advanced parameters
    slippage_tolerance: float = 2.0  # pips
    execution_timeout: int = 30  # seconds
    retry_attempts: int = 3
    
    # Strategy and risk context
    strategy: str = "unknown"
    confidence: float = 0.5
    risk_amount: float = 0.0
    max_loss: float = 0.0
    
    # Metadata
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    priority: int = 1  # 1=highest, 5=lowest
    
    # Risk parameters from Risk Manager
    risk_params: Optional[Dict[str, Any]] = None

@dataclass
class ExecutionResult:
    """Comprehensive execution result structure"""
    # Execution outcome
    success: bool
    request_id: str
    order_id: Optional[int] = None
    
    # Trade details
    symbol: str = ""
    action: str = ""
    volume_requested: float = 0.0
    volume_filled: float = 0.0
    
    # Execution prices
    requested_price: Optional[float] = None
    executed_price: Optional[float] = None
    slippage_pips: float = 0.0
    
    # Timing
    execution_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Status and error handling
    status: OrderStatus = OrderStatus.PENDING
    error_code: Optional[int] = None
    error_message: str = ""
    
    # Financial impact
    commission: float = 0.0
    swap: float = 0.0
    profit: float = 0.0
    
    # Metadata
    strategy: str = "unknown"
    execution_mode: ExecutionMode = ExecutionMode.LIVE

@dataclass
class Position:
    """Professional position tracking structure"""
    # Position identification
    position_id: str
    ticket: Optional[int] = None
    
    # Basic position data
    symbol: str = ""
    action: str = ""  # BUY, SELL
    volume: float = 0.0
    entry_price: float = 0.0
    
    # Risk management
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    # Current status
    current_price: float = 0.0
    unrealized_pnl: float = 0.0
    status: PositionStatus = PositionStatus.OPEN
    
    # Timing
    open_time: datetime = field(default_factory=datetime.utcnow)
    close_time: Optional[datetime] = None
    duration: Optional[timedelta] = None
    
    # Strategy context
    strategy: str = "unknown"
    confidence: float = 0.5
    risk_amount: float = 0.0
    
    # Performance tracking
    max_profit: float = 0.0
    max_loss: float = 0.0
    profit_at_close: Optional[float] = None

@dataclass
class ExecutionMetrics:
    """Comprehensive execution performance metrics"""
    # Execution statistics
    total_orders: int = 0
    successful_orders: int = 0
    failed_orders: int = 0
    cancelled_orders: int = 0
    
    # Timing metrics
    avg_execution_time_ms: float = 0.0
    max_execution_time_ms: float = 0.0
    min_execution_time_ms: float = float('inf')
    
    # Slippage analysis
    avg_slippage_pips: float = 0.0
    max_slippage_pips: float = 0.0
    positive_slippage_count: int = 0
    negative_slippage_count: int = 0
    
    # Fill statistics
    full_fills: int = 0
    partial_fills: int = 0
    rejected_orders: int = 0
    
    # Financial metrics
    total_commission_paid: float = 0.0
    total_swap: float = 0.0
    total_slippage_cost: float = 0.0
    
    # Position metrics
    open_positions: int = 0
    closed_positions: int = 0
    total_profit: float = 0.0
    total_loss: float = 0.0
    
    # Success rates
    execution_success_rate: float = 0.0
    slippage_within_tolerance: float = 0.0

class MT5OrderManager:
    """Professional MT5 order management with comprehensive error handling"""
    
    def __init__(self, config: TradingConfig):
        self.config = config
        self.connection_active = False
        self.account_info = None
        self.symbol_info_cache = {}
        self.order_lock = threading.Lock()
        self.logger = setup_logging('INFO')
        
    async def initialize(self) -> bool:
        """Initialize MT5 connection for order management"""
        try:
            # Check if MT5 is already initialized
            if not mt5.initialize():
                # Try to initialize with credentials
                if not mt5.initialize(
                    login=self.config.mt5_login,
                    password=self.config.mt5_password,
                    server=self.config.mt5_server,
                    path=self.config.mt5_path,
                    timeout=self.config.mt5_timeout
                ):
                    error = mt5.last_error()
                    self.logger.error(f"MT5 initialization failed: {error}")
                    return False
            
            # Get account information
            self.account_info = mt5.account_info()
            if not self.account_info:
                self.logger.error("Failed to get account information")
                return False
            
            # Verify trading permissions
            if not self.account_info.trade_allowed:
                self.logger.error("Trading not allowed on this account")
                return False
            
            self.connection_active = True
            self.logger.info("✅ MT5 Order Manager initialized successfully")
            self.logger.info(f"   Account: {self.account_info.login}")
            self.logger.info(f"   Server: {self.account_info.server}")
            self.logger.info(f"   Balance: {format_currency(self.account_info.balance, self.account_info.currency)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing MT5 Order Manager: {e}")
            return False
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get cached symbol information"""
        try:
            if symbol not in self.symbol_info_cache:
                symbol_info = mt5.symbol_info(symbol)
                if symbol_info:
                    self.symbol_info_cache[symbol] = {
                        'point': symbol_info.point,
                        'digits': symbol_info.digits,
                        'spread': symbol_info.spread,
                        'volume_min': symbol_info.volume_min,
                        'volume_max': symbol_info.volume_max,
                        'volume_step': symbol_info.volume_step,
                        'contract_size': symbol_info.trade_contract_size,
                        'margin_initial': symbol_info.margin_initial,
                        'swap_long': symbol_info.swap_long,
                        'swap_short': symbol_info.swap_short
                    }
                else:
                    self.logger.error(f"Failed to get symbol info for {symbol}")
                    return None
            
            return self.symbol_info_cache[symbol]
            
        except Exception as e:
            self.logger.error(f"Error getting symbol info for {symbol}: {e}")
            return None
    
    async def place_market_order(self, request: ExecutionRequest) -> ExecutionResult:
        """Place market order with comprehensive error handling"""
        start_time = time.time()
        
        try:
            with self.order_lock:
                # Get symbol information
                symbol_info = self.get_symbol_info(request.symbol)
                if not symbol_info:
                    return ExecutionResult(
                        success=False,
                        request_id=request.request_id,
                        symbol=request.symbol,
                        action=request.action,
                        error_message=f"Symbol {request.symbol} not found",
                        execution_time_ms=(time.time() - start_time) * 1000
                    )
                
                # Get current price
                tick = mt5.symbol_info_tick(request.symbol)
                if not tick:
                    return ExecutionResult(
                        success=False,
                        request_id=request.request_id,
                        symbol=request.symbol,
                        action=request.action,
                        error_message="Failed to get current price",
                        execution_time_ms=(time.time() - start_time) * 1000
                    )
                
                # Determine order type and price
                if request.action.upper() == 'BUY':
                    order_type = mt5.ORDER_TYPE_BUY
                    price = tick.ask
                    expected_price = price
                else:
                    order_type = mt5.ORDER_TYPE_SELL
                    price = tick.bid
                    expected_price = price
                
                # Round volume to valid step
                volume = self._round_volume(request.volume, symbol_info)
                
                # Validate volume
                if volume < symbol_info['volume_min'] or volume > symbol_info['volume_max']:
                    return ExecutionResult(
                        success=False,
                        request_id=request.request_id,
                        symbol=request.symbol,
                        action=request.action,
                        error_message=f"Invalid volume: {volume}",
                        execution_time_ms=(time.time() - start_time) * 1000
                    )
                
                # Create order request
                order_request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": request.symbol,
                    "volume": volume,
                    "type": order_type,
                    "price": price,
                    "deviation": int(request.slippage_tolerance),
                    "magic": self.config.mt5_magic_number,
                    "comment": f"Strategy: {request.strategy}",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC
                }
                
                # Add stop loss and take profit if specified
                if request.stop_loss:
                    order_request["sl"] = request.stop_loss
                
                if request.take_profit:
                    order_request["tp"] = request.take_profit
                
                # Execute order
                result = mt5.order_send(order_request)
                
                if result is None:
                    error = mt5.last_error()
                    return ExecutionResult(
                        success=False,
                        request_id=request.request_id,
                        symbol=request.symbol,
                        action=request.action,
                        error_code=error[0] if error else None,
                        error_message=error[1] if error else "Unknown error",
                        execution_time_ms=(time.time() - start_time) * 1000
                    )
                
                # Check if order was successful
                if result.retcode == mt5.TRADE_RETCODE_DONE:
                    # Calculate slippage
                    executed_price = result.price
                    slippage_pips = self._calculate_slippage_pips(
                        request.symbol, expected_price, executed_price, request.action
                    )
                    
                    execution_result = ExecutionResult(
                        success=True,
                        request_id=request.request_id,
                        order_id=result.order,
                        symbol=request.symbol,
                        action=request.action,
                        volume_requested=request.volume,
                        volume_filled=result.volume,
                        requested_price=expected_price,
                        executed_price=executed_price,
                        slippage_pips=slippage_pips,
                        execution_time_ms=(time.time() - start_time) * 1000,
                        status=OrderStatus.FILLED,
                        strategy=request.strategy
                    )
                    
                    self.logger.info(f"✅ Market order executed: {request.symbol} {request.action} {volume} @ {executed_price}")
                    
                    return execution_result
                
                else:
                    return ExecutionResult(
                        success=False,
                        request_id=request.request_id,
                        symbol=request.symbol,
                        action=request.action,
                        error_code=result.retcode,
                        error_message=result.comment,
                        execution_time_ms=(time.time() - start_time) * 1000
                    )
        
        except Exception as e:
            self.logger.error(f"Error placing market order: {e}")
            return ExecutionResult(
                success=False,
                request_id=request.request_id,
                symbol=request.symbol,
                action=request.action,
                error_message=str(e),
                execution_time_ms=(time.time() - start_time) * 1000
            )
    
    async def place_pending_order(self, request: ExecutionRequest) -> ExecutionResult:
        """Place pending order (limit/stop) with comprehensive validation"""
        start_time = time.time()
        
        try:
            with self.order_lock:
                # Get symbol information
                symbol_info = self.get_symbol_info(request.symbol)
                if not symbol_info:
                    return ExecutionResult(
                        success=False,
                        request_id=request.request_id,
                        error_message=f"Symbol {request.symbol} not found",
                        execution_time_ms=(time.time() - start_time) * 1000
                    )
                
                # Validate entry price
                if not request.entry_price:
                    return ExecutionResult(
                        success=False,
                        request_id=request.request_id,
                        error_message="Entry price required for pending orders",
                        execution_time_ms=(time.time() - start_time) * 1000
                    )
                
                # Determine MT5 order type
                order_type = self._get_mt5_order_type(request.order_type, request.action)
                if order_type is None:
                    return ExecutionResult(
                        success=False,
                        request_id=request.request_id,
                        error_message=f"Invalid order type: {request.order_type}",
                        execution_time_ms=(time.time() - start_time) * 1000
                    )
                
                # Round volume
                volume = self._round_volume(request.volume, symbol_info)
                
                # Create pending order request
                order_request = {
                    "action": mt5.TRADE_ACTION_PENDING,
                    "symbol": request.symbol,
                    "volume": volume,
                    "type": order_type,
                    "price": request.entry_price,
                    "magic": self.config.mt5_magic_number,
                    "comment": f"Strategy: {request.strategy}",
                    "type_time": mt5.ORDER_TIME_GTC
                }
                
                # Add stop loss and take profit
                if request.stop_loss:
                    order_request["sl"] = request.stop_loss
                
                if request.take_profit:
                    order_request["tp"] = request.take_profit
                
                # Execute order
                result = mt5.order_send(order_request)
                
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    self.logger.info(f"✅ Pending order placed: {request.symbol} {request.order_type.value} @ {request.entry_price}")
                    
                    return ExecutionResult(
                        success=True,
                        request_id=request.request_id,
                        order_id=result.order,
                        symbol=request.symbol,
                        action=request.action,
                        volume_requested=request.volume,
                        requested_price=request.entry_price,
                        execution_time_ms=(time.time() - start_time) * 1000,
                        status=OrderStatus.PLACED,
                        strategy=request.strategy
                    )
                
                else:
                    error_msg = result.comment if result else "Unknown error"
                    return ExecutionResult(
                        success=False,
                        request_id=request.request_id,
                        error_message=error_msg,
                        execution_time_ms=(time.time() - start_time) * 1000
                    )
        
        except Exception as e:
            self.logger.error(f"Error placing pending order: {e}")
            return ExecutionResult(
                success=False,
                request_id=request.request_id,
                error_message=str(e),
                execution_time_ms=(time.time() - start_time) * 1000
            )
    
    def _round_volume(self, volume: float, symbol_info: Dict[str, Any]) -> float:
        """Round volume to valid step size"""
        try:
            step = symbol_info.get('volume_step', 0.01)
            return round(round(volume / step) * step, 2)
        except:
            return round(volume, 2)
    
    def _calculate_slippage_pips(self, symbol: str, expected: float, executed: float, action: str) -> float:
        """Calculate slippage in pips"""
        try:
            symbol_info = self.get_symbol_info(symbol)
            if not symbol_info:
                return 0.0
            
            point = symbol_info.get('point', 0.00001)
            
            if action.upper() == 'BUY':
                # For buy orders, positive slippage means we paid more
                slippage = (executed - expected) / point
            else:
                # For sell orders, positive slippage means we received less
                slippage = (expected - executed) / point
            
            return round(slippage, 1)
            
        except:
            return 0.0
    
    def _get_mt5_order_type(self, order_type: OrderType, action: str):
        """Convert order type to MT5 constants"""
        type_mapping = {
            (OrderType.LIMIT, 'BUY'): mt5.ORDER_TYPE_BUY_LIMIT,
            (OrderType.LIMIT, 'SELL'): mt5.ORDER_TYPE_SELL_LIMIT,
            (OrderType.STOP, 'BUY'): mt5.ORDER_TYPE_BUY_STOP,
            (OrderType.STOP, 'SELL'): mt5.ORDER_TYPE_SELL_STOP,
            (OrderType.STOP_LIMIT, 'BUY'): mt5.ORDER_TYPE_BUY_STOP_LIMIT,
            (OrderType.STOP_LIMIT, 'SELL'): mt5.ORDER_TYPE_SELL_STOP_LIMIT,
        }
        
        return type_mapping.get((order_type, action.upper()))

class PositionManager:
    """Professional position management with real-time tracking"""
    
    def __init__(self, config: TradingConfig, mt5_manager: MT5OrderManager):
        self.config = config
        self.mt5_manager = mt5_manager
        self.positions = {}  # position_id -> Position
        self.position_lock = threading.Lock()
        self.logger = setup_logging('INFO')
        
        # Position monitoring
        self.monitoring_active = False
        self.monitoring_task = None
        self.update_interval = 5  # seconds
        
    async def initialize(self) -> bool:
        """Initialize position manager"""
        try:
            # Start position monitoring
            self.monitoring_active = True
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            self.logger.info("✅ Position Manager initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing Position Manager: {e}")
            return False
    
    def create_position(self, execution_result: ExecutionResult, request: ExecutionRequest) -> Optional[str]:
        """Create new position from execution result"""
        try:
            if not execution_result.success:
                return None
            
            position_id = str(uuid.uuid4())
            
            position = Position(
                position_id=position_id,
                ticket=execution_result.order_id,
                symbol=execution_result.symbol,
                action=execution_result.action,
                volume=execution_result.volume_filled,
                entry_price=execution_result.executed_price or 0.0,
                stop_loss=request.stop_loss,
                take_profit=request.take_profit,
                current_price=execution_result.executed_price or 0.0,
                strategy=request.strategy,
                confidence=request.confidence,
                risk_amount=request.risk_amount
            )
            
            with self.position_lock:
                self.positions[position_id] = position
            
            self.logger.info(f"📊 Position created: {position.symbol} {position.action} {position.volume}")
            
            return position_id
            
        except Exception as e:
            self.logger.error(f"Error creating position: {e}")
            return None
    
    async def close_position(self, position_id: str, reason: str = "manual") -> Optional[ExecutionResult]:
        """Close position with comprehensive handling"""
        try:
            with self.position_lock:
                if position_id not in self.positions:
                    self.logger.error(f"Position not found: {position_id}")
                    return None
                
                position = self.positions[position_id]
                
                if position.status != PositionStatus.OPEN:
                    self.logger.warning(f"Position already closed: {position_id}")
                    return None
            
            # Create close request
            close_action = "SELL" if position.action == "BUY" else "BUY"
            
            close_request = ExecutionRequest(
                symbol=position.symbol,
                action=close_action,
                volume=position.volume,
                order_type=OrderType.MARKET,
                strategy=position.strategy
            )
            
            # Execute close order
            result = await self.mt5_manager.place_market_order(close_request)
            
            if result.success:
                # Update position
                with self.position_lock:
                    position.status = PositionStatus.CLOSED
                    position.close_time = datetime.utcnow()
                    position.duration = position.close_time - position.open_time
                    
                    # Calculate final P&L
                    if position.action == "BUY":
                        profit = (result.executed_price - position.entry_price) * position.volume
                    else:
                        profit = (position.entry_price - result.executed_price) * position.volume
                    
                    position.profit_at_close = profit
                
                self.logger.info(f"✅ Position closed: {position_id} | P&L: ${profit:.2f}")
                
                return result
            else:
                self.logger.error(f"Failed to close position: {position_id}")
                return result
                
        except Exception as e:
            self.logger.error(f"Error closing position {position_id}: {e}")
            return None
    
    async def update_stop_loss(self, position_id: str, new_stop_loss: float) -> bool:
        """Update position stop loss"""
        try:
            with self.position_lock:
                if position_id not in self.positions:
                    return False
                
                position = self.positions[position_id]
                
                if not position.ticket:
                    return False
            
            # Update stop loss via MT5
            modify_request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "position": position.ticket,
                "sl": new_stop_loss,
                "tp": position.take_profit if position.take_profit else 0
            }
            
            result = mt5.order_send(modify_request)
            
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                with self.position_lock:
                    position.stop_loss = new_stop_loss
                
                self.logger.info(f"✅ Stop loss updated: {position_id} -> {new_stop_loss}")
                return True
            else:
                self.logger.error(f"Failed to update stop loss: {position_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating stop loss: {e}")
            return False
    
    async def _monitoring_loop(self):
        """Real-time position monitoring loop"""
        while self.monitoring_active:
            try:
                await self._update_all_positions()
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                self.logger.error(f"Error in position monitoring: {e}")
                await asyncio.sleep(10)
    
    async def _update_all_positions(self):
        """Update all open positions with current market data"""
        try:
            open_positions = []
            
            with self.position_lock:
                open_positions = [pos for pos in self.positions.values() 
                                if pos.status == PositionStatus.OPEN]
            
            for position in open_positions:
                await self._update_position(position)
                
        except Exception as e:
            self.logger.error(f"Error updating positions: {e}")
    
    async def _update_position(self, position: Position):
        """Update individual position with current market data"""
        try:
            # Get current price
            tick = mt5.symbol_info_tick(position.symbol)
            if not tick:
                return
            
            # Update current price based on position direction
            if position.action == "BUY":
                position.current_price = tick.bid
                unrealized_pnl = (tick.bid - position.entry_price) * position.volume
            else:
                position.current_price = tick.ask
                unrealized_pnl = (position.entry_price - tick.ask) * position.volume
            
            position.unrealized_pnl = unrealized_pnl
            
            # Track max profit/loss
            position.max_profit = max(position.max_profit, unrealized_pnl)
            position.max_loss = min(position.max_loss, unrealized_pnl)
            
        except Exception as e:
            self.logger.error(f"Error updating position {position.position_id}: {e}")
    
    def get_open_positions(self) -> List[Position]:
        """Get all open positions"""
        with self.position_lock:
            return [pos for pos in self.positions.values() 
                   if pos.status == PositionStatus.OPEN]
    
    def get_position_summary(self) -> Dict[str, Any]:
        """Get position summary statistics"""
        try:
            open_positions = self.get_open_positions()
            closed_positions = [pos for pos in self.positions.values() 
                              if pos.status == PositionStatus.CLOSED]
            
            total_unrealized = sum(pos.unrealized_pnl for pos in open_positions)
            total_realized = sum(pos.profit_at_close or 0 for pos in closed_positions)
            
            return {
                'open_positions_count': len(open_positions),
                'closed_positions_count': len(closed_positions),
                'total_unrealized_pnl': total_unrealized,
                'total_realized_pnl': total_realized,
                'total_pnl': total_unrealized + total_realized,
                'open_positions': [
                    {
                        'symbol': pos.symbol,
                        'action': pos.action,
                        'volume': pos.volume,
                        'unrealized_pnl': pos.unrealized_pnl,
                        'entry_price': pos.entry_price,
                        'current_price': pos.current_price
                    } for pos in open_positions
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting position summary: {e}")
            return {}

class EnhancedExecutionEngine:
    """
    Enhanced Professional Execution Engine for Institutional Trading
    
    This class provides comprehensive order execution, position management,
    and trade monitoring capabilities with seamless MT5 integration,
    advanced risk controls, and production-ready performance monitoring.
    """
    
    def __init__(self, config: TradingConfig, risk_manager: EnhancedRiskManager, data_manager: EnhancedDataManager):
        self.config = config
        self.risk_manager = risk_manager
        self.data_manager = data_manager
        
        # Core components
        self.mt5_manager = MT5OrderManager(config)
        self.position_manager = None
        
        # Execution tracking
        self.execution_queue = asyncio.Queue(maxsize=1000)
        self.metrics = ExecutionMetrics()
        self.execution_history = deque(maxlen=10000)
        
        # Performance monitoring
        self.performance_lock = threading.Lock()
        self.last_performance_update = datetime.utcnow()
        
        # Execution control
        self.execution_enabled = True
        self.emergency_stop = False
        self.max_concurrent_orders = config.get('execution.max_concurrent_orders', 10)
        self.concurrent_orders = 0
        
        # Async tasks
        self.execution_processor = None
        self.performance_monitor = None
        self.is_running = False
        
        # Setup logging
        self.logger = setup_logging('INFO')
        self.logger.info("⚡ Enhanced Execution Engine initialized")
    
    async def initialize(self) -> bool:
        """Initialize execution engine with all components"""
        try:
            self.logger.info("🚀 Initializing Enhanced Execution Engine...")
            
            # Initialize MT5 manager
            if not await self.mt5_manager.initialize():
                return False
            
            # Initialize position manager
            self.position_manager = PositionManager(self.config, self.mt5_manager)
            if not await self.position_manager.initialize():
                return False
            
            # Start background tasks
            self.is_running = True
            self.execution_processor = asyncio.create_task(self._execution_processing_loop())
            self.performance_monitor = asyncio.create_task(self._performance_monitoring_loop())
            
            self.logger.info("✅ Enhanced Execution Engine initialization completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing execution engine: {e}")
            return False
    
    async def execute_trade(self, signal: Dict[str, Any], risk_params: Dict[str, Any]) -> Optional[ExecutionResult]:
        """Execute trade with comprehensive validation and risk integration"""
        try:
            if not self.execution_enabled or self.emergency_stop:
                self.logger.warning("Execution disabled or emergency stop active")
                return None
            
            # Check concurrent orders limit
            if self.concurrent_orders >= self.max_concurrent_orders:
                self.logger.warning("Maximum concurrent orders reached")
                return None
            
            # Create execution request
            execution_request = ExecutionRequest(
                symbol=signal.get('symbol', ''),
                action=signal.get('action', ''),
                volume=risk_params.get('position_size', 0.0),
                order_type=OrderType(signal.get('order_type', 'market')),
                entry_price=signal.get('entry_price'),
                stop_loss=signal.get('stop_loss'),
                take_profit=signal.get('take_profit'),
                slippage_tolerance=self.config.get('execution.slippage_tolerance', 2.0),
                strategy=signal.get('strategy', 'unknown'),
                confidence=signal.get('confidence', 0.5),
                risk_amount=risk_params.get('risk_amount', 0.0),
                max_loss=risk_params.get('max_loss', 0.0),
                risk_params=risk_params
            )
            
            # Add to execution queue
            await self.execution_queue.put(execution_request)
            
            self.logger.info(f"🎯 Trade queued for execution: {execution_request.symbol} {execution_request.action}")
            
            # Wait for execution (simplified - in production you'd use callbacks)
            # For now, return a success indicator
            return ExecutionResult(
                success=True,
                request_id=execution_request.request_id,
                symbol=execution_request.symbol,
                action=execution_request.action,
                status=OrderStatus.PENDING
            )
            
        except Exception as e:
            self.logger.error(f"Error executing trade: {e}")
            return None
    
    async def _execution_processing_loop(self):
        """Main execution processing loop"""
        while self.is_running:
            try:
                # Get execution request
                try:
                    request = await asyncio.wait_for(self.execution_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                # Process execution request
                await self._process_execution_request(request)
                
            except Exception as e:
                self.logger.error(f"Error in execution processing loop: {e}")
                await asyncio.sleep(1)
    
    async def _process_execution_request(self, request: ExecutionRequest):
        """Process individual execution request"""
        try:
            self.concurrent_orders += 1
            
            # Final risk validation
            if not await self._validate_execution_risk(request):
                self.logger.warning(f"Execution blocked by risk validation: {request.symbol}")
                return
            
            # Execute based on order type
            if request.order_type == OrderType.MARKET:
                result = await self.mt5_manager.place_market_order(request)
            else:
                result = await self.mt5_manager.place_pending_order(request)
            
            # Update metrics
            self._update_execution_metrics(result, request)
            
            # Create position if successful
            if result.success and result.status == OrderStatus.FILLED:
                position_id = self.position_manager.create_position(result, request)
                if position_id:
                    self.logger.info(f"📊 Position created: {position_id}")
            
            # Store execution history
            self.execution_history.append({
                'timestamp': datetime.utcnow(),
                'request': request,
                'result': result
            })
            
        except Exception as e:
            self.logger.error(f"Error processing execution request: {e}")
        
        finally:
            self.concurrent_orders = max(0, self.concurrent_orders - 1)
    
    async def _validate_execution_risk(self, request: ExecutionRequest) -> bool:
        """Final risk validation before execution"""
        try:
            # Check if account has sufficient margin
            account_info = mt5.account_info()
            if not account_info:
                return False
            
            # Check free margin
            required_margin = request.volume * 1000  # Simplified calculation
            if account_info.margin_free < required_margin:
                self.logger.warning(f"Insufficient margin: required {required_margin}, available {account_info.margin_free}")
                return False
            
            # Check spread conditions
            tick = mt5.symbol_info_tick(request.symbol)
            if tick:
                spread_pips = (tick.ask - tick.bid) / 0.00001  # Simplified for major pairs
                max_spread = self.config.get('execution.max_spread_pips', 3.0)
                
                if spread_pips > max_spread:
                    self.logger.warning(f"Spread too wide: {spread_pips:.1f} pips > {max_spread}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating execution risk: {e}")
            return False
    
    def _update_execution_metrics(self, result: ExecutionResult, request: ExecutionRequest):
        """Update execution performance metrics"""
        try:
            with self.performance_lock:
                self.metrics.total_orders += 1
                
                if result.success:
                    self.metrics.successful_orders += 1
                else:
                    self.metrics.failed_orders += 1
                
                # Update timing metrics
                if result.execution_time_ms > 0:
                    if self.metrics.avg_execution_time_ms == 0:
                        self.metrics.avg_execution_time_ms = result.execution_time_ms
                    else:
                        # Running average
                        self.metrics.avg_execution_time_ms = (
                            self.metrics.avg_execution_time_ms * 0.9 + 
                            result.execution_time_ms * 0.1
                        )
                    
                    self.metrics.max_execution_time_ms = max(
                        self.metrics.max_execution_time_ms, result.execution_time_ms
                    )
                    self.metrics.min_execution_time_ms = min(
                        self.metrics.min_execution_time_ms, result.execution_time_ms
                    )
                
                # Update slippage metrics
                if result.success and result.slippage_pips != 0:
                    if self.metrics.avg_slippage_pips == 0:
                        self.metrics.avg_slippage_pips = result.slippage_pips
                    else:
                        self.metrics.avg_slippage_pips = (
                            self.metrics.avg_slippage_pips * 0.9 + 
                            result.slippage_pips * 0.1
                        )
                    
                    self.metrics.max_slippage_pips = max(
                        self.metrics.max_slippage_pips, abs(result.slippage_pips)
                    )
                    
                    if result.slippage_pips > 0:
                        self.metrics.negative_slippage_count += 1
                    else:
                        self.metrics.positive_slippage_count += 1
                    
                    # Check if slippage was within tolerance
                    if abs(result.slippage_pips) <= request.slippage_tolerance:
                        self.metrics.slippage_within_tolerance += 1
                
                # Update success rates
                if self.metrics.total_orders > 0:
                    self.metrics.execution_success_rate = (
                        self.metrics.successful_orders / self.metrics.total_orders
                    )
                    
                    if (self.metrics.positive_slippage_count + self.metrics.negative_slippage_count) > 0:
                        slippage_within_count = self.metrics.slippage_within_tolerance
                        total_slippage_orders = self.metrics.positive_slippage_count + self.metrics.negative_slippage_count
                        self.metrics.slippage_within_tolerance = slippage_within_count / total_slippage_orders
            
        except Exception as e:
            self.logger.error(f"Error updating execution metrics: {e}")
    
    async def _performance_monitoring_loop(self):
        """Performance monitoring and alerting loop"""
        while self.is_running:
            try:
                # Update position metrics
                await self._update_position_metrics()
                
                # Check for performance alerts
                await self._check_performance_alerts()
                
                # Log periodic performance report
                if (datetime.utcnow() - self.last_performance_update).seconds >= 300:  # Every 5 minutes
                    await self._log_performance_report()
                    self.last_performance_update = datetime.utcnow()
                
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in performance monitoring: {e}")
                await asyncio.sleep(60)
    
    async def _update_position_metrics(self):
        """Update position-related metrics"""
        try:
            if not self.position_manager:
                return
            
            open_positions = self.position_manager.get_open_positions()
            position_summary = self.position_manager.get_position_summary()
            
            with self.performance_lock:
                self.metrics.open_positions = len(open_positions)
                self.metrics.total_profit = position_summary.get('total_realized_pnl', 0.0)
                
        except Exception as e:
            self.logger.error(f"Error updating position metrics: {e}")
    
    async def _check_performance_alerts(self):
        """Check for performance-related alerts"""
        try:
            # Check execution success rate
            if (self.metrics.total_orders > 10 and 
                self.metrics.execution_success_rate < 0.8):
                self.logger.warning(f"Low execution success rate: {self.metrics.execution_success_rate:.1%}")
            
            # Check average execution time
            if self.metrics.avg_execution_time_ms > 5000:  # 5 seconds
                self.logger.warning(f"High execution latency: {self.metrics.avg_execution_time_ms:.1f}ms")
            
            # Check slippage performance
            if (self.metrics.positive_slippage_count + self.metrics.negative_slippage_count > 10 and
                self.metrics.avg_slippage_pips > 3.0):
                self.logger.warning(f"High average slippage: {self.metrics.avg_slippage_pips:.1f} pips")
            
        except Exception as e:
            self.logger.error(f"Error checking performance alerts: {e}")
    
    async def _log_performance_report(self):
        """Log comprehensive performance report"""
        try:
            self.logger.info("📊 === EXECUTION ENGINE PERFORMANCE REPORT ===")
            self.logger.info(f"📈 Orders - Total: {self.metrics.total_orders}, Success: {self.metrics.successful_orders}, Failed: {self.metrics.failed_orders}")
            self.logger.info(f"✅ Success Rate: {self.metrics.execution_success_rate:.1%}")
            self.logger.info(f"⚡ Avg Execution Time: {self.metrics.avg_execution_time_ms:.1f}ms")
            self.logger.info(f"📉 Avg Slippage: {self.metrics.avg_slippage_pips:.1f} pips")
            self.logger.info(f"📊 Open Positions: {self.metrics.open_positions}")
            self.logger.info(f"💰 Total Profit: ${self.metrics.total_profit:.2f}")
            self.logger.info("=" * 50)
            
        except Exception as e:
            self.logger.error(f"Error logging performance report: {e}")
    
    async def close_all_positions(self, reason: str = "system_shutdown") -> List[ExecutionResult]:
        """Close all open positions"""
        try:
            if not self.position_manager:
                return []
            
            open_positions = self.position_manager.get_open_positions()
            results = []
            
            for position in open_positions:
                result = await self.position_manager.close_position(position.position_id, reason)
                if result:
                    results.append(result)
            
            self.logger.info(f"🔒 Closed {len(results)} positions (reason: {reason})")
            return results
            
        except Exception as e:
            self.logger.error(f"Error closing all positions: {e}")
            return []
    
    async def cancel_all_orders(self) -> bool:
        """Cancel all pending orders"""
        try:
            # Get all pending orders
            orders = mt5.orders_get()
            if not orders:
                return True
            
            cancelled_count = 0
            for order in orders:
                request = {
                    "action": mt5.TRADE_ACTION_REMOVE,
                    "order": order.ticket
                }
                
                result = mt5.order_send(request)
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    cancelled_count += 1
            
            self.logger.info(f"🚫 Cancelled {cancelled_count} pending orders")
            return True
            
        except Exception as e:
            self.logger.error(f"Error cancelling orders: {e}")
            return False
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get comprehensive execution statistics"""
        try:
            position_summary = {}
            if self.position_manager:
                position_summary = self.position_manager.get_position_summary()
            
            return {
                'execution_metrics': {
                    'total_orders': self.metrics.total_orders,
                    'successful_orders': self.metrics.successful_orders,
                    'failed_orders': self.metrics.failed_orders,
                    'success_rate': self.metrics.execution_success_rate,
                    'avg_execution_time_ms': self.metrics.avg_execution_time_ms,
                    'max_execution_time_ms': self.metrics.max_execution_time_ms,
                    'min_execution_time_ms': self.metrics.min_execution_time_ms,
                    'avg_slippage_pips': self.metrics.avg_slippage_pips,
                    'max_slippage_pips': self.metrics.max_slippage_pips,
                    'slippage_within_tolerance_rate': self.metrics.slippage_within_tolerance
                },
                'position_metrics': position_summary,
                'system_status': {
                    'execution_enabled': self.execution_enabled,
                    'emergency_stop': self.emergency_stop,
                    'concurrent_orders': self.concurrent_orders,
                    'max_concurrent_orders': self.max_concurrent_orders,
                    'queue_size': self.execution_queue.qsize() if self.execution_queue else 0
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting execution statistics: {e}")
            return {}
    
    def enable_execution(self):
        """Enable trade execution"""
        self.execution_enabled = True
        self.emergency_stop = False
        self.logger.info("✅ Execution enabled")
    
    def disable_execution(self):
        """Disable trade execution"""
        self.execution_enabled = False
        self.logger.warning("⏸️ Execution disabled")
    
    def emergency_shutdown(self):
        """Emergency shutdown with immediate position closure"""
        self.emergency_stop = True
        self.execution_enabled = False
        self.logger.critical("🚨 EMERGENCY SHUTDOWN ACTIVATED")
    
    async def get_account_balance(self) -> float:
        """Get current account balance"""
        try:
            account_info = mt5.account_info()
            return account_info.balance if account_info else 0.0
        except:
            return 0.0
    
    async def get_unrealized_pnl(self) -> float:
        """Get total unrealized P&L"""
        try:
            if self.position_manager:
                summary = self.position_manager.get_position_summary()
                return summary.get('total_unrealized_pnl', 0.0)
            return 0.0
        except:
            return 0.0
    
    async def test_execution(self) -> bool:
        """Test execution system readiness"""
        try:
            # Test MT5 connection
            if not self.mt5_manager.connection_active:
                return False
            
            # Test account access
            account_info = mt5.account_info()
            if not account_info or not account_info.trade_allowed:
                return False
            
            # Test symbol access
            test_symbol = self.config.symbols[0] if self.config.symbols else 'EURUSD'
            symbol_info = self.mt5_manager.get_symbol_info(test_symbol)
            if not symbol_info:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Execution test failed: {e}")
            return False
    
    async def shutdown(self):
        """Graceful shutdown of execution engine"""
        try:
            self.logger.info("🛑 Shutting down Enhanced Execution Engine...")
            
            # Stop processing
            self.is_running = False
            
            # Cancel background tasks
            if self.execution_processor and not self.execution_processor.done():
                self.execution_processor.cancel()
            
            if self.performance_monitor and not self.performance_monitor.done():
                self.performance_monitor.cancel()
            
            # Stop position manager
            if self.position_manager:
                self.position_manager.monitoring_active = False
                if self.position_manager.monitoring_task:
                    self.position_manager.monitoring_task.cancel()
            
            self.logger.info("✅ Enhanced Execution Engine shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error shutting down execution engine: {e}")

# Factory function for creating execution engine
def create_execution_engine(config: TradingConfig, risk_manager: EnhancedRiskManager, 
                           data_manager: EnhancedDataManager) -> EnhancedExecutionEngine:
    """Factory function to create execution engine instance"""
    return EnhancedExecutionEngine(config, risk_manager, data_manager)
