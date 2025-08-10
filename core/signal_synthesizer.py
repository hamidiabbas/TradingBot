"""
Signal Synthesizer - Confluence Engine for combining signals from multiple strategies.
Implements sophisticated signal scoring, filtering, and trade setup generation.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import pandas as pd
import numpy as np

from config import TradingConfig
from strategies import SignalEvent, TradeSetup
from utils.logger import setup_logging

@dataclass
class ConfluenceRule:
    """Defines a confluence scoring rule"""
    event_pattern: str  # Pattern to match against event_type
    direction_filter: Optional[str]  # 'bullish', 'bearish', or None for any
    score_value: float  # Points to add to confluence score
    symbol_specific: bool = False  # Whether rule applies to specific symbols only
    timeframe_filter: Optional[str] = None  # Specific timeframe filter
    max_age_minutes: int = 60  # Maximum age of signal in minutes
    description: str = ""

@dataclass
class PotentialTrade:
    """Represents a developing trade setup"""
    symbol: str
    direction: str  # 'long' or 'short'
    confluence_score: float
    contributing_signals: List[SignalEvent]
    primary_signal: SignalEvent  # The main signal that initiated this setup
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    position_size: float = 0.0
    created_timestamp: datetime = None
    last_updated: datetime = None
    trade_reasoning: List[str] = None
    risk_reward_ratio: Optional[float] = None
    
    def __post_init__(self):
        if self.created_timestamp is None:
            self.created_timestamp = datetime.utcnow()
        if self.last_updated is None:
            self.last_updated = datetime.utcnow()
        if self.trade_reasoning is None:
            self.trade_reasoning = []

class SignalSynthesizer:
    """
    Advanced confluence engine that combines signals from multiple strategies
    into high-conviction trade setups using sophisticated scoring rules.
    """
    
    def __init__(self, config: TradingConfig):
        self.config = config
        self.logger = setup_logging(config.LOG_LEVEL)
        
        # Confluence scoring system
        self.confluence_rules: List[ConfluenceRule] = []
        self.min_confluence_score = config.MIN_CONFLUENCE_SCORE
        self.max_signals_per_symbol = config.MAX_SIGNALS_PER_SYMBOL
        self.signal_timeout_minutes = config.SIGNAL_TIMEOUT_MINUTES
        
        # Trade setup tracking
        self.potential_trades: Dict[str, List[PotentialTrade]] = {}  # symbol -> list of setups
        self.completed_setups: List[TradeSetup] = []
        self.signal_buffer: List[SignalEvent] = []
        
        # Performance tracking
        self.synthesis_stats = {
            'total_signals_processed': 0,
            'setups_generated': 0,
            'setups_triggered': 0,
            'average_confluence_score': 0.0,
            'last_synthesis_time': None
        }
        
    async def initialize(self) -> bool:
        """
        Initialize signal synthesizer and confluence rules.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info("Initializing Signal Synthesizer...")
            
            # Initialize confluence rules based on configuration
            self._initialize_confluence_rules()
            
            # Initialize potential trades tracking for all symbols
            for symbol in self.config.SYMBOLS:
                self.potential_trades[symbol] = []
            
            self.logger.info(f"Signal Synthesizer initialized with {len(self.confluence_rules)} confluence rules")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Signal Synthesizer: {e}")
            return False
    
    def _initialize_confluence_rules(self) -> None:
        """Initialize confluence scoring rules based on configuration"""
        
        # ICT Strategy Rules
        if self.config.ict.enabled:
            self.confluence_rules.extend([
                ConfluenceRule(
                    event_pattern="ICT_POI_ENTERED",
                    direction_filter=None,
                    score_value=self.config.ict.poi_confluence_score,
                    max_age_minutes=30,
                    description="Price entered ICT Point of Interest"
                ),
                ConfluenceRule(
                    event_pattern="ICT_MSS_CONFIRMED",
                    direction_filter=None,
                    score_value=self.config.ict.mss_confluence_score,
                    max_age_minutes=15,
                    description="Market Structure Shift confirmed"
                ),
                ConfluenceRule(
                    event_pattern="ICT_FVG_FORMED",
                    direction_filter=None,
                    score_value=self.config.ict.fvg_confluence_score,
                    max_age_minutes=20,
                    description="Fair Value Gap formed"
                ),
                ConfluenceRule(
                    event_pattern="ICT_OB_MITIGATED",
                    direction_filter=None,
                    score_value=self.config.ict.ob_confluence_score,
                    max_age_minutes=25,
                    description="Order Block mitigation"
                )
            ])
        
        # RTM Strategy Rules
        if self.config.rtm.enabled:
            self.confluence_rules.extend([
                ConfluenceRule(
                    event_pattern="RTM_DEMAND_ZONE_ENTERED",
                    direction_filter="bullish",
                    score_value=self.config.rtm.zone_confluence_score,
                    max_age_minutes=45,
                    description="Price entered RTM Demand Zone"
                ),
                ConfluenceRule(
                    event_pattern="RTM_SUPPLY_ZONE_ENTERED",
                    direction_filter="bearish",
                    score_value=self.config.rtm.zone_confluence_score,
                    max_age_minutes=45,
                    description="Price entered RTM Supply Zone"
                ),
                ConfluenceRule(
                    event_pattern="RTM_QML_PATTERN_CONFIRMED",
                    direction_filter=None,
                    score_value=self.config.rtm.qml_confluence_score,
                    max_age_minutes=20,
                    description="Quasimodo pattern confirmed"
                )
            ])
        
        # Indicator Suite Rules
        if self.config.indicator_suite.enabled:
            self.confluence_rules.extend([
                ConfluenceRule(
                    event_pattern="RSI_DIVERGENCE_BULLISH",
                    direction_filter="bullish",
                    score_value=self.config.indicator_suite.rsi_confluence_score,
                    max_age_minutes=120,
                    description="Bullish RSI divergence detected"
                ),
                ConfluenceRule(
                    event_pattern="RSI_DIVERGENCE_BEARISH",
                    direction_filter="bearish",
                    score_value=self.config.indicator_suite.rsi_confluence_score,
                    max_age_minutes=120,
                    description="Bearish RSI divergence detected"
                ),
                ConfluenceRule(
                    event_pattern="MACD_CROSSOVER_BULLISH",
                    direction_filter="bullish",
                    score_value=self.config.indicator_suite.macd_confluence_score,
                    max_age_minutes=60,
                    description="Bullish MACD crossover"
                ),
                ConfluenceRule(
                    event_pattern="MACD_CROSSOVER_BEARISH",
                    direction_filter="bearish",
                    score_value=self.config.indicator_suite.macd_confluence_score,
                    max_age_minutes=60,
                    description="Bearish MACD crossover"
                ),
                ConfluenceRule(
                    event_pattern="MA_TREND_AGAINST",
                    direction_filter=None,
                    score_value=-4.0,  # Penalty for counter-trend trades
                    max_age_minutes=240,
                    description="Trade against major moving average trend"
                )
            ])
    
    async def synthesize_signals(self, signals: List[SignalEvent]) -> List[TradeSetup]:
        """
        Main synthesis function - converts raw signals into trade setups.
        
        Args:
            signals: List of SignalEvent objects from all strategies
            
        Returns:
            List of TradeSetup objects ready for execution
        """
        try:
            synthesis_start = datetime.utcnow()
            
            # Update statistics
            self.synthesis_stats['total_signals_processed'] += len(signals)
            
            # Add new signals to buffer
            self.signal_buffer.extend(signals)
            
            # Clean up old signals
            self._cleanup_old_signals()
            
            # Process signals for each symbol
            new_trade_setups = []
            
            for symbol in self.config.SYMBOLS:
                symbol_signals = [s for s in self.signal_buffer if s.symbol == symbol]
                symbol_setups = await self._process_symbol_signals(symbol, symbol_signals)
                new_trade_setups.extend(symbol_setups)
            
            # Update synthesis statistics
            self.synthesis_stats['setups_generated'] += len(new_trade_setups)
            self.synthesis_stats['last_synthesis_time'] = synthesis_start
            
            if new_trade_setups:
                avg_score = sum(setup.confluence_score for setup in new_trade_setups) / len(new_trade_setups)
                self.synthesis_stats['average_confluence_score'] = avg_score
                
                self.logger.info(f"Generated {len(new_trade_setups)} trade setups with average confluence score: {avg_score:.2f}")
            
            return new_trade_setups
            
        except Exception as e:
            self.logger.error(f"Error synthesizing signals: {e}")
            return []
    
    def _cleanup_old_signals(self) -> None:
        """Remove signals that are too old to be useful"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(minutes=self.signal_timeout_minutes * 2)
            
            # Clean signal buffer
            old_count = len(self.signal_buffer)
            self.signal_buffer = [s for s in self.signal_buffer if s.timestamp >= cutoff_time]
            
            # Clean potential trades
            for symbol in self.potential_trades:
                old_trades = self.potential_trades[symbol]
                self.potential_trades[symbol] = [
                    trade for trade in old_trades 
                    if trade.last_updated >= cutoff_time
                ]
            
            if len(self.signal_buffer) < old_count:
                self.logger.debug(f"Cleaned up {old_count - len(self.signal_buffer)} old signals")
                
        except Exception as e:
            self.logger.error(f"Error cleaning up old signals: {e}")
    
    async def _process_symbol_signals(self, symbol: str, signals: List[SignalEvent]) -> List[TradeSetup]:
        """
        Process signals for a specific symbol to generate trade setups.
        
        Args:
            symbol: Trading symbol
            signals: Signals for this symbol
            
        Returns:
            List of TradeSetup objects
        """
        try:
            if not signals:
                return []
            
            # Update existing potential trades with new signals
            await self._update_potential_trades(symbol, signals)
            
            # Check for new trade opportunities
            new_setups = await self._identify_new_setups(symbol, signals)
            
            # Convert high-confidence potential trades to trade setups
            completed_setups = await self._finalize_trade_setups(symbol)
            
            return completed_setups
            
        except Exception as e:
            self.logger.error(f"Error processing signals for {symbol}: {e}")
            return []
    
    async def _update_potential_trades(self, symbol: str, signals: List[SignalEvent]) -> None:
        """Update existing potential trades with new signals"""
        try:
            for trade in self.potential_trades[symbol]:
                # Check if any new signals add confluence to existing trade
                for signal in signals:
                    if self._signal_supports_trade(signal, trade):
                        # Calculate additional confluence score
                        additional_score = self._calculate_signal_score(signal, trade.direction)
                        
                        if additional_score > 0:
                            trade.confluence_score += additional_score
                            trade.contributing_signals.append(signal)
                            trade.last_updated = datetime.utcnow()
                            trade.trade_reasoning.append(f"Added {signal.event_type} (+{additional_score:.1f})")
                            
        except Exception as e:
            self.logger.error(f"Error updating potential trades: {e}")
    
    async def _identify_new_setups(self, symbol: str, signals: List[SignalEvent]) -> List[PotentialTrade]:
        """Identify new trade setup opportunities from primary signals"""
        try:
            new_setups = []
            
            # Look for primary signals that can initiate new trades
            primary_signals = [s for s in signals if self._is_primary_signal(s)]
            
            for primary_signal in primary_signals:
                # Check if we already have a similar setup
                if self._has_similar_setup(symbol, primary_signal):
                    continue
                
                # Check if we've reached maximum signals per symbol
                if len(self.potential_trades[symbol]) >= self.max_signals_per_symbol:
                    continue
                
                # Create new potential trade
                trade_direction = 'long' if primary_signal.direction == 'bullish' else 'short'
                
                new_trade = PotentialTrade(
                    symbol=symbol,
                    direction=trade_direction,
                    confluence_score=self._calculate_signal_score(primary_signal, trade_direction),
                    contributing_signals=[primary_signal],
                    primary_signal=primary_signal,
                    trade_reasoning=[f"Initiated by {primary_signal.event_type}"]
                )
                
                # Add supporting signals that align with this trade
                for signal in signals:
                    if signal != primary_signal and self._signal_supports_trade(signal, new_trade):
                        additional_score = self._calculate_signal_score(signal, trade_direction)
                        if additional_score != 0:  # Can be negative (penalty)
                            new_trade.confluence_score += additional_score
                            new_trade.contributing_signals.append(signal)
                            new_trade.trade_reasoning.append(f"Added {signal.event_type} ({additional_score:+.1f})")
                
                # Add to potential trades if it has potential
                if new_trade.confluence_score > 0:
                    self.potential_trades[symbol].append(new_trade)
                    new_setups.append(new_trade)
            
            return new_setups
            
        except Exception as e:
            self.logger.error(f"Error identifying new setups: {e}")
            return []
    
    def _is_primary_signal(self, signal: SignalEvent) -> bool:
        """Check if a signal is a primary signal that can initiate trades"""
        primary_patterns = [
            'ICT_POI_ENTERED',
            'ICT_MSS_CONFIRMED', 
            'RTM_DEMAND_ZONE_ENTERED',
            'RTM_SUPPLY_ZONE_ENTERED',
            'RTM_QML_PATTERN_CONFIRMED'
        ]
        
        return any(pattern in signal.event_type for pattern in primary_patterns)
    
    def _has_similar_setup(self, symbol: str, signal: SignalEvent) -> bool:
        """Check if we already have a similar setup for this symbol"""
        try:
            for trade in self.potential_trades[symbol]:
                # Check if same direction and primary signal type
                trade_direction = 'bullish' if trade.direction == 'long' else 'bearish'
                
                if (signal.direction == trade_direction and 
                    signal.event_type == trade.primary_signal.event_type):
                    
                    # Check if signals are close in time (within 30 minutes)
                    time_diff = abs((signal.timestamp - trade.primary_signal.timestamp).total_seconds())
                    if time_diff < (30 * 60):  # 30 minutes
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking similar setup: {e}")
            return False
    
    def _signal_supports_trade(self, signal: SignalEvent, trade: PotentialTrade) -> bool:
        """Check if a signal supports an existing trade setup"""
        try:
            # Convert trade direction to signal direction
            expected_direction = 'bullish' if trade.direction == 'long' else 'bearish'
            
            # Check basic compatibility
            if signal.symbol != trade.symbol:
                return False
            
            # Check if signal direction aligns (or is neutral)
            if signal.direction != 'neutral' and signal.direction != expected_direction:
                # Check for penalty signals (counter-trend)
                if not self._is_penalty_signal(signal):
                    return False
            
            # Check if we already have this signal
            for existing_signal in trade.contributing_signals:
                if (existing_signal.event_type == signal.event_type and
                    existing_signal.timestamp == signal.timestamp):
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking signal support: {e}")
            return False
    
    def _is_penalty_signal(self, signal: SignalEvent) -> bool:
        """Check if a signal is a penalty signal (counter-trend, etc.)"""
        penalty_patterns = ['MA_TREND_AGAINST', 'RISK_WARNING', 'COUNTER_TREND']
        return any(pattern in signal.event_type for pattern in penalty_patterns)
    
    def _calculate_signal_score(self, signal: SignalEvent, trade_direction: str) -> float:
        """
        Calculate confluence score contribution from a signal.
        
        Args:
            signal: SignalEvent to score
            trade_direction: Direction of the trade ('long' or 'short')
            
        Returns:
            float: Score contribution (can be negative for penalties)
        """
        try:
            total_score = 0.0
            expected_signal_direction = 'bullish' if trade_direction == 'long' else 'bearish'
            
            # Find matching confluence rules
            for rule in self.confluence_rules:
                if not self._rule_matches_signal(rule, signal):
                    continue
                
                # Check direction compatibility
                if rule.direction_filter is not None:
                    if rule.direction_filter != signal.direction:
                        continue
                
                # Check signal age
                signal_age_minutes = (datetime.utcnow() - signal.timestamp).total_seconds() / 60
                if signal_age_minutes > rule.max_age_minutes:
                    continue
                
                # Apply score with strength weighting
                weighted_score = rule.score_value * signal.strength
                total_score += weighted_score
                
                self.logger.debug(f"Applied rule '{rule.description}': {weighted_score:.2f} points")
                
                # Only apply one rule per signal to avoid double-counting
                break
            
            return total_score
            
        except Exception as e:
            self.logger.error(f"Error calculating signal score: {e}")
            return 0.0
    
    def _rule_matches_signal(self, rule: ConfluenceRule, signal: SignalEvent) -> bool:
        """Check if a confluence rule matches a signal"""
        try:
            # Check event pattern match
            if rule.event_pattern not in signal.event_type:
                return False
            
            # Check timeframe filter if specified
            if rule.timeframe_filter and rule.timeframe_filter != signal.timeframe:
                return False
            
            # Check symbol-specific rules
            if rule.symbol_specific:
                # This would require additional logic based on specific symbol rules
                pass
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error matching rule to signal: {e}")
            return False
    
    async def _finalize_trade_setups(self, symbol: str) -> List[TradeSetup]:
        """
        Convert high-confidence potential trades into executable trade setups.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            List of TradeSetup objects ready for execution
        """
        try:
            finalized_setups = []
            trades_to_remove = []
            
            for i, trade in enumerate(self.potential_trades[symbol]):
                # Check if confluence score meets minimum threshold
                if trade.confluence_score >= self.min_confluence_score:
                    # Create trade setup
                    trade_setup = self._create_trade_setup(trade)
                    
                    if trade_setup:
                        finalized_setups.append(trade_setup)
                        trades_to_remove.append(i)
                        
                        self.logger.info(
                            f"Finalized trade setup for {symbol}: {trade.direction} "
                            f"with confluence score {trade.confluence_score:.2f}"
                        )
                
                # Remove trades that are too old or have very low scores
                elif (trade.confluence_score < 0 or 
                      (datetime.utcnow() - trade.created_timestamp).total_seconds() > (self.signal_timeout_minutes * 60)):
                    trades_to_remove.append(i)
            
            # Remove processed/expired trades
            for i in reversed(trades_to_remove):
                del self.potential_trades[symbol][i]
            
            return finalized_setups
            
        except Exception as e:
            self.logger.error(f"Error finalizing trade setups: {e}")
            return []
    
    def _create_trade_setup(self, potential_trade: PotentialTrade) -> Optional[TradeSetup]:
        """
        Create a TradeSetup object from a PotentialTrade.
        
        Args:
            potential_trade: PotentialTrade to convert
            
        Returns:
            TradeSetup object or None if creation fails
        """
        try:
            # Extract price levels from primary signal
            entry_price = potential_trade.primary_signal.level
            if entry_price is None:
                # If no specific level provided, we'll let the risk manager determine entry
                entry_price = 0.0  # Placeholder for market entry
            
            # Create trade setup
            trade_setup = TradeSetup(
                symbol=potential_trade.symbol,
                direction=potential_trade.direction,
                entry_price=entry_price,
                stop_loss=0.0,  # To be calculated by risk manager
                take_profit=None,  # To be calculated by risk manager
                position_size=0.0,  # To be calculated by risk manager
                confluence_score=potential_trade.confluence_score,
                strategy_source='confluence_engine',
                timeframe=potential_trade.primary_signal.timeframe,
                timestamp=datetime.utcnow(),
                metadata={
                    'contributing_signals': len(potential_trade.contributing_signals),
                    'primary_signal_type': potential_trade.primary_signal.event_type,
                    'trade_reasoning': potential_trade.trade_reasoning,
                    'signal_strength_avg': np.mean([s.strength for s in potential_trade.contributing_signals]),
                    'setup_age_minutes': (datetime.utcnow() - potential_trade.created_timestamp).total_seconds() / 60
                }
            )
            
            return trade_setup
            
        except Exception as e:
            self.logger.error(f"Error creating trade setup: {e}")
            return None
    
    def get_synthesis_statistics(self) -> Dict[str, Any]:
        """Get current synthesis statistics"""
        return self.synthesis_stats.copy()
    
    def get_potential_trades_status(self) -> Dict[str, Any]:
        """Get status of all potential trades"""
        try:
            status = {}
            
            for symbol, trades in self.potential_trades.items():
                status[symbol] = []
                
                for trade in trades:
                    status[symbol].append({
                        'direction': trade.direction,
                        'confluence_score': trade.confluence_score,
                        'contributing_signals': len(trade.contributing_signals),
                        'age_minutes': (datetime.utcnow() - trade.created_timestamp).total_seconds() / 60,
                        'primary_signal_type': trade.primary_signal.event_type,
                        'ready_for_execution': trade.confluence_score >= self.min_confluence_score
                    })
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting potential trades status: {e}")
            return {}
    
    async def shutdown(self) -> None:
        """Shutdown signal synthesizer"""
        try:
            self.logger.info("Shutting down Signal Synthesizer...")
            
            # Clear all data
            self.signal_buffer.clear()
            self.potential_trades.clear()
            self.completed_setups.clear()
            
            self.logger.info("Signal Synthesizer shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during Signal Synthesizer shutdown: {e}")
