from typing import Dict, Any, Optional

"""
Enhanced Professional ICT (Inner Circle Trader) Strategy
======================================================

A comprehensive institutional trading strategy implementing advanced Smart Money Concepts
including Order Blocks, Fair Value Gaps, Market Structure analysis, and sophisticated
liquidity manipulation detection for algorithmic trading systems.

This strategy represents the cutting-edge of institutional trading methodology, incorporating
advanced pattern recognition, multi-timeframe analysis, and state-driven execution logic
designed to identify and capitalize on institutional order flow.

Features:
- Advanced Order Block Detection with Volume Confirmation
- Sophisticated Fair Value Gap Analysis and Mitigation Tracking
- Real-time Market Structure Recognition (BOS/ChoCH)
- Institutional Liquidity Detection and Sweep Analysis
- Multi-timeframe Confluence Engine
- State Machine-driven Execution Logic
- Advanced Risk-Reward Optimization
- Professional Performance Analytics

Author: Enhanced Trading System
Version: 3.0 Professional
License: Proprietary
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import warnings
from concurrent.futures import ThreadPoolExecutor
import smartmoneyconcepts as smc
from scipy import stats
from sklearn.cluster import DBSCAN

from strategies import PrimaryStrategy, StatefulStrategy, SignalEvent, TradeSetup, register_strategy, StrategyState
from utils.price_action import (
    find_swing_points, detect_market_structure, detect_break_of_structure,
    detect_change_of_character, identify_liquidity_levels
)
from utils.logger import setup_logging

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore', category=FutureWarning)

class ICTPatternType(Enum):
    """ICT pattern type enumeration"""
    ORDER_BLOCK = "order_block"
    FAIR_VALUE_GAP = "fair_value_gap"
    BREAKER_BLOCK = "breaker_block"
    MITIGATION_BLOCK = "mitigation_block"
    LIQUIDITY_SWEEP = "liquidity_sweep"
    MARKET_STRUCTURE_SHIFT = "market_structure_shift"
    CHANGE_OF_CHARACTER = "change_of_character"

class ICTEntryModel(Enum):
    """ICT entry model types"""
    MENTORSHIP_2022 = "2022_mentorship"
    OPTIMAL_TRADE_ENTRY = "ote"
    BREAKER_BLOCK_ENTRY = "breaker"
    MITIGATION_BLOCK_ENTRY = "mitigation"
    SILVER_BULLET = "silver_bullet"

class MarketStructure(Enum):
    """Market structure states"""
    UPTREND = "uptrend"
    DOWNTREND = "downtrend"
    RANGING = "ranging"
    CONSOLIDATING = "consolidating"
    TRANSITIONING = "transitioning"

class LiquidityType(Enum):
    """Liquidity type classification"""
    BUY_SIDE_LIQUIDITY = "bsl"  # Above swing highs
    SELL_SIDE_LIQUIDITY = "ssl"  # Below swing lows
    EQUAL_HIGHS = "equal_highs"
    EQUAL_LOWS = "equal_lows"
    RELATIVE_EQUAL_HIGHS = "rel_equal_highs"
    RELATIVE_EQUAL_LOWS = "rel_equal_lows"

@dataclass
class ICTPattern:
    """Advanced ICT pattern with comprehensive metadata"""
    pattern_id: str
    pattern_type: ICTPatternType
    direction: str  # 'bullish', 'bearish'
    timeframe: str
    detection_time: datetime
    
    # Pattern boundaries
    top: float
    bottom: float
    entry_level: float
    
    # Validation metrics
    strength: float  # 0-1 strength score
    confidence: float  # 0-1 confidence score
    volume_confirmation: float  # Volume-based validation
    
    # Pattern-specific data
    formation_candles: List[int] = field(default_factory=list)
    mitigation_level: Optional[float] = None
    is_mitigated: bool = False
    mitigation_time: Optional[datetime] = None
    
    # Advanced metrics
    institutional_footprint: float = 0.0
    displacement_strength: float = 0.0
    time_validity: float = 1.0  # Decreases over time
    
    # Risk-reward data
    stop_loss_level: Optional[float] = None
    take_profit_levels: List[float] = field(default_factory=list)
    risk_reward_ratio: float = 0.0
    
    # Performance tracking
    success_rate: float = 0.0
    average_move: float = 0.0
    
    def __post_init__(self):
        if not self.pattern_id:
            self.pattern_id = f"{self.pattern_type.value}_{self.timeframe}_{int(self.detection_time.timestamp())}"

@dataclass
class MarketStructureState:
    """Market structure state tracking"""
    current_structure: MarketStructure
    trend_direction: str
    last_bos: Optional[datetime] = None
    last_choch: Optional[datetime] = None
    swing_highs: List[Tuple[datetime, float]] = field(default_factory=list)
    swing_lows: List[Tuple[datetime, float]] = field(default_factory=list)
    structure_confidence: float = 0.0
    
    def update_structure(self, new_structure: MarketStructure, confidence: float):
        """Update market structure with confidence tracking"""
        self.current_structure = new_structure
        self.structure_confidence = confidence

@dataclass
class LiquidityLevel:
    """Liquidity level with institutional context"""
    level: float
    liquidity_type: LiquidityType
    strength: float
    creation_time: datetime
    timeframe: str
    is_swept: bool = False
    sweep_time: Optional[datetime] = None
    expected_reaction: str = ""  # Expected price reaction after sweep
    
@dataclass
class ICTMarketContext:
    """Comprehensive ICT market context"""
    daily_bias: str  # 'bullish', 'bearish', 'neutral'
    session_bias: str
    current_session: str  # 'london', 'new_york', 'asian'
    htf_pois: List[ICTPattern] = field(default_factory=list)
    active_liquidity: List[LiquidityLevel] = field(default_factory=list)
    market_structure: MarketStructureState = None
    institutional_activity: float = 0.0
    
    def __post_init__(self):
        if self.market_structure is None:
            self.market_structure = MarketStructureState(
                current_structure=MarketStructure.RANGING,
                trend_direction='neutral'
            )

@register_strategy
class EnhancedICTStrategy(StatefulStrategy):
    """
    Enhanced Professional ICT Strategy
    
    This comprehensive institutional trading strategy implements the complete ICT methodology
    with advanced pattern recognition, multi-timeframe analysis, and state-driven execution.
    Designed for professional algorithmic trading with institutional-grade features.
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.logger = setup_logging('INFO')
        
        # Enhanced ICT configuration
        self.trading_timeframe = config.get('trading_timeframe', 'M15')
        self.entry_timeframe = config.get('entry_timeframe', 'M1')
        self.htf_timeframes = config.get('htf_timeframes', ['H1', 'H4', 'D1'])
        
        # Pattern detection parameters
        self.swing_length = config.get('swing_length', 10)
        self.min_displacement_pips = config.get('min_displacement_pips', 20)
        self.fvg_min_gap_pips = config.get('fvg_min_gap_pips', 5)
        self.volume_confirmation_threshold = config.get('volume_confirmation_threshold', 1.5)
        
        # Entry model configuration
        self.entry_model = ICTEntryModel(config.get('entry_model', 'MENTORSHIP_2022'))
        self.use_session_filters = config.get('use_session_filters', True)
        self.kill_zones_only = config.get('kill_zones_only', False)
        
        # Advanced features
        self.use_volume_profile = config.get('use_volume_profile', True)
        self.use_order_flow_analysis = config.get('use_order_flow_analysis', True)
        self.use_displacement_analysis = config.get('use_displacement_analysis', True)
        
        # Confluence scoring
        self.poi_confluence_score = config.get('poi_confluence_score', 3.0)
        self.mss_confluence_score = config.get('mss_confluence_score', 3.0)
        self.fvg_confluence_score = config.get('fvg_confluence_score', 2.0)
        self.ob_confluence_score = config.get('ob_confluence_score', 2.5)
        self.liquidity_sweep_bonus = config.get('liquidity_sweep_bonus', 1.5)
        
        # State management
        self.current_context: ICTMarketContext = None
        self.active_patterns: Dict[str, List[ICTPattern]] = {}
        self.liquidity_levels: Dict[str, List[LiquidityLevel]] = {}
        self.pending_setups: List[Dict[str, Any]] = []
        
        # Performance tracking
        self.performance_metrics = {
            'patterns_detected': 0,
            'patterns_validated': 0,
            'successful_entries': 0,
            'liquidity_sweeps_detected': 0,
            'mss_confirmed': 0,
            'average_pattern_strength': 0.0,
            'win_rate': 0.0
        }
        
        # Threading for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Pattern validation settings
        self.pattern_min_strength = config.get('pattern_min_strength', 0.6)
        self.pattern_timeout_hours = config.get('pattern_timeout_hours', 24)
        self.mitigation_tolerance_pips = config.get('mitigation_tolerance_pips', 2)
        
        self.logger.info("Enhanced ICT Strategy initialized")
    
    async def initialize(self) -> bool:
        """Initialize the enhanced ICT strategy"""
        try:
            self.logger.info("Initializing Enhanced ICT Strategy...")
            
            # Initialize market context
            self.current_context = ICTMarketContext(
                daily_bias='neutral',
                session_bias='neutral',
                current_session='asian'
            )
            
            # Initialize pattern storage
            for timeframe in [self.trading_timeframe, self.entry_timeframe] + self.htf_timeframes:
                self.active_patterns[timeframe] = []
                self.liquidity_levels[timeframe] = []
            
            # Initialize state machine
            self.transition_state(StrategyState.AWAITING_CONTEXT)
            
            self.logger.info("Enhanced ICT Strategy initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing Enhanced ICT Strategy: {e}")
            return False
    
    def generate_signals(self, data: Dict[str, pd.DataFrame]) -> List[SignalEvent]:
        """
        Generate ICT signals with advanced pattern recognition and state management
        
        Args:
            data: Multi-timeframe market data
            
        Returns:
            List of enhanced ICT signal events
        """
        try:
            all_signals = []
            
            # Process each symbol's data
            for symbol, timeframe_data in data.items():
                if not isinstance(timeframe_data, dict):
                    continue
                
                # Update market context and patterns
                self._update_market_context(symbol, timeframe_data)
                
                # Update all ICT patterns
                self._update_ict_patterns(symbol, timeframe_data)
                
                # Process state machine logic
                state_signals = self._process_ict_state_machine(symbol, timeframe_data)
                
                # Add symbol to signals
                for signal in state_signals:
                    signal.symbol = symbol
                
                all_signals.extend(state_signals)
            
            # Update performance metrics
            self._update_performance_metrics(all_signals)
            
            # Clean old patterns
            self._cleanup_old_patterns()
            
            return all_signals
            
        except Exception as e:
            self.logger.error(f"Error generating ICT signals: {e}")
            return []
    
    def _update_market_context(self, symbol: str, data: Dict[str, pd.DataFrame]):
        """Update comprehensive ICT market context"""
        try:
            # Update daily bias from daily timeframe
            if 'D1' in data:
                self.current_context.daily_bias = self._determine_daily_bias(data['D1'])
            
            # Update session bias and current session
            self.current_context.current_session = self._determine_current_session()
            self.current_context.session_bias = self._determine_session_bias(data)
            
            # Update market structure for primary timeframe
            if self.trading_timeframe in data:
                self._update_market_structure(data[self.trading_timeframe])
            
            # Calculate institutional activity level
            self.current_context.institutional_activity = self._calculate_institutional_activity(data)
            
        except Exception as e:
            self.logger.error(f"Error updating market context: {e}")
    
    def _determine_daily_bias(self, daily_data: pd.DataFrame) -> str:
        """Determine daily bias using advanced ICT analysis"""
        try:
            if len(daily_data) < 20:
                return 'neutral'
            
            # Analyze recent market structure
            swing_points = find_swing_points(daily_data, lookback=5)
            
            if len(swing_points) >= 4:
                recent_highs = swing_points[swing_points['swing_type'] == 'high'].tail(2)
                recent_lows = swing_points[swing_points['swing_type'] == 'low'].tail(2)
                
                if len(recent_highs) >= 2 and len(recent_lows) >= 2:
                    # Check for higher highs and higher lows
                    hh = recent_highs.iloc[-1]['price'] > recent_highs.iloc[-2]['price']
                    hl = recent_lows.iloc[-1]['price'] > recent_lows.iloc[-2]['price']
                    
                    # Check for lower highs and lower lows
                    lh = recent_highs.iloc[-1]['price'] < recent_highs.iloc[-2]['price'] 
                    ll = recent_lows.iloc[-1]['price'] < recent_lows.iloc[-2]['price']
                    
                    if hh and hl:
                        return 'bullish'
                    elif lh and ll:
                        return 'bearish'
            
            # Fallback to price momentum analysis
            current_price = daily_data['close'].iloc[-1]
            sma_20 = daily_data['close'].rolling(20).mean().iloc[-1]
            
            if current_price > sma_20 * 1.01:  # 1% above moving average
                return 'bullish'
            elif current_price < sma_20 * 0.99:  # 1% below moving average
                return 'bearish'
            
            return 'neutral'
            
        except Exception as e:
            self.logger.error(f"Error determining daily bias: {e}")
            return 'neutral'
    
    def _determine_current_session(self) -> str:
        """Determine current trading session"""
        try:
            current_hour = datetime.utcnow().hour
            
            # London session: 07:00 - 16:00 UTC
            if 7 <= current_hour < 16:
                return 'london'
            # New York session: 12:00 - 21:00 UTC (overlaps with London)
            elif 12 <= current_hour < 21:
                return 'new_york'
            # Asian session: 21:00 - 07:00 UTC
            else:
                return 'asian'
                
        except Exception as e:
            self.logger.error(f"Error determining current session: {e}")
            return 'asian'
    
    def _determine_session_bias(self, data: Dict[str, pd.DataFrame]) -> str:
        """Determine session-specific bias"""
        try:
            if 'H1' not in data:
                return 'neutral'
            
            h1_data = data['H1']
            if len(h1_data) < 10:
                return 'neutral'
            
            # Analyze recent session price action
            recent_data = h1_data.tail(6)  # Last 6 hours
            session_high = recent_data['high'].max()
            session_low = recent_data['low'].min()
            current_price = recent_data['close'].iloc[-1]
            
            # Determine position within session range
            session_range = session_high - session_low
            if session_range > 0:
                position_in_range = (current_price - session_low) / session_range
                
                if position_in_range > 0.7:
                    return 'bearish'  # Near session high, expect reversal
                elif position_in_range < 0.3:
                    return 'bullish'  # Near session low, expect reversal
            
            return 'neutral'
            
        except Exception as e:
            self.logger.error(f"Error determining session bias: {e}")
            return 'neutral'
    
    def _update_market_structure(self, data: pd.DataFrame):
        """Update market structure analysis"""
        try:
            # Find swing points
            swing_points = find_swing_points(data, self.swing_length)
            
            if len(swing_points) < 4:
                return
            
            # Update swing highs and lows in context
            highs = swing_points[swing_points['swing_type'] == 'high']
            lows = swing_points[swing_points['swing_type'] == 'low']
            
            # Update context with recent swings
            self.current_context.market_structure.swing_highs = [
                (idx, row['price']) for idx, row in highs.tail(5).iterrows()
            ]
            self.current_context.market_structure.swing_lows = [
                (idx, row['price']) for idx, row in lows.tail(5).iterrows()
            ]
            
            # Determine current market structure
            structure = self._analyze_market_structure(swing_points)
            self.current_context.market_structure.update_structure(structure, 0.8)
            
            # Detect breaks of structure and change of character
            self._detect_structure_changes(data, swing_points)
            
        except Exception as e:
            self.logger.error(f"Error updating market structure: {e}")
    
    def _analyze_market_structure(self, swing_points: pd.DataFrame) -> MarketStructure:
        """Analyze current market structure state"""
        try:
            if len(swing_points) < 4:
                return MarketStructure.RANGING
            
            # Get recent swing points
            recent_swings = swing_points.tail(4)
            highs = recent_swings[recent_swings['swing_type'] == 'high']
            lows = recent_swings[recent_swings['swing_type'] == 'low']
            
            if len(highs) >= 2 and len(lows) >= 2:
                # Check for trending structure
                latest_high = highs.iloc[-1]['price']
                prev_high = highs.iloc[-2]['price']
                latest_low = lows.iloc[-1]['price']
                prev_low = lows.iloc[-2]['price']
                
                # Uptrend: Higher Highs and Higher Lows
                if latest_high > prev_high and latest_low > prev_low:
                    return MarketStructure.UPTREND
                
                # Downtrend: Lower Highs and Lower Lows
                elif latest_high < prev_high and latest_low < prev_low:
                    return MarketStructure.DOWNTREND
                
                # Mixed signals might indicate transition
                elif latest_high > prev_high and latest_low < prev_low:
                    return MarketStructure.TRANSITIONING
                elif latest_high < prev_high and latest_low > prev_low:
                    return MarketStructure.TRANSITIONING
            
            return MarketStructure.RANGING
            
        except Exception as e:
            self.logger.error(f"Error analyzing market structure: {e}")
            return MarketStructure.RANGING
    
    def _detect_structure_changes(self, data: pd.DataFrame, swing_points: pd.DataFrame):
        """Detect breaks of structure and change of character"""
        try:
            # Detect Break of Structure (BOS)
            bos_signals = detect_break_of_structure(data, swing_points)
            if len(bos_signals[bos_signals != 0]) > 0:
                self.current_context.market_structure.last_bos = datetime.utcnow()
                self.performance_metrics['mss_confirmed'] += 1
            
            # Detect Change of Character (ChoCH)
            choch_signals = detect_change_of_character(data, swing_points)
            if len(choch_signals[choch_signals != 0]) > 0:
                self.current_context.market_structure.last_choch = datetime.utcnow()
                
        except Exception as e:
            self.logger.error(f"Error detecting structure changes: {e}")
    
    def _calculate_institutional_activity(self, data: Dict[str, pd.DataFrame]) -> float:
        """Calculate institutional activity level"""
        try:
            activity_score = 0.0
            
            if self.trading_timeframe in data:
                df = data[self.trading_timeframe]
                
                if 'volume' in df.columns and len(df) >= 20:
                    # Volume surge analysis
                    volume = df['volume']
                    volume_ma = volume.rolling(20).mean()
                    volume_ratio = volume.iloc[-1] / volume_ma.iloc[-1] if volume_ma.iloc[-1] > 0 else 1.0
                    
                    activity_score += min(1.0, volume_ratio / 3.0)
                
                # Price displacement analysis
                if len(df) >= 5:
                    recent_range = df['high'].tail(5).max() - df['low'].tail(5).min()
                    avg_range = (df['high'] - df['low']).rolling(20).mean().iloc[-1]
                    
                    if avg_range > 0:
                        displacement_ratio = recent_range / avg_range
                        activity_score += min(1.0, displacement_ratio / 2.0)
            
            return min(1.0, activity_score / 2.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating institutional activity: {e}")
            return 0.0
    
    def _update_ict_patterns(self, symbol: str, data: Dict[str, pd.DataFrame]):
        """Update all ICT patterns across timeframes"""
        try:
            for timeframe in [self.trading_timeframe] + self.htf_timeframes:
                if timeframe not in data:
                    continue
                
                df = data[timeframe]
                if len(df) < 50:
                    continue
                
                # Update Order Blocks
                self._update_order_blocks(symbol, df, timeframe)
                
                # Update Fair Value Gaps
                self._update_fair_value_gaps(symbol, df, timeframe)
                
                # Update Breaker Blocks
                self._update_breaker_blocks(symbol, df, timeframe)
                
                # Update Liquidity Levels
                self._update_liquidity_levels(symbol, df, timeframe)
                
                # Update pattern mitigation status
                self._check_pattern_mitigation(symbol, df, timeframe)
                
        except Exception as e:
            self.logger.error(f"Error updating ICT patterns: {e}")
    
    def _update_order_blocks(self, symbol: str, data: pd.DataFrame, timeframe: str):
        """Update Order Block detection with advanced validation"""
        try:
            # Use smartmoneyconcepts library for base detection
            swing_points = smc.swing_highs_lows(data, length=self.swing_length)
            obs = smc.ob(data, swing_points)
            
            if obs is None or obs.empty:
                return
            
            new_obs = []
            for idx, ob in obs.iterrows():
                if pd.notna(ob.get('OB', np.nan)):
                    # Enhanced validation
                    ob_pattern = self._create_enhanced_order_block(data, idx, ob, timeframe)
                    if ob_pattern and self._validate_order_block(ob_pattern, data):
                        new_obs.append(ob_pattern)
                        self.performance_metrics['patterns_detected'] += 1
            
            # Add new patterns to storage
            if timeframe not in self.active_patterns:
                self.active_patterns[timeframe] = []
            
            self.active_patterns[timeframe].extend(new_obs)
            
            # Limit storage size
            if len(self.active_patterns[timeframe]) > 50:
                self.active_patterns[timeframe] = self.active_patterns[timeframe][-30:]
                
        except Exception as e:
            self.logger.error(f"Error updating order blocks: {e}")
    
    def _create_enhanced_order_block(self, data: pd.DataFrame, idx: pd.Timestamp, 
                                   ob_data: pd.Series, timeframe: str) -> ICTPattern:
        """Create enhanced order block with comprehensive analysis"""
        try:
            ob_direction = 'bullish' if ob_data.get('OB', 0) > 0 else 'bearish'
            
            # Get candle data for the order block
            candle = data.loc[idx]
            
            # Calculate pattern boundaries
            if ob_direction == 'bullish':
                top = candle['high']
                bottom = candle['low']
                entry_level = candle['low']  # Demand zone entry
            else:
                top = candle['high']
                bottom = candle['low'] 
                entry_level = candle['high']  # Supply zone entry
            
            # Calculate volume confirmation
            volume_confirmation = self._calculate_volume_confirmation(data, idx)
            
            # Calculate displacement strength
            displacement_strength = self._calculate_displacement_strength(data, idx)
            
            # Calculate institutional footprint
            institutional_footprint = self._calculate_institutional_footprint(data, idx)
            
            # Create pattern
            pattern = ICTPattern(
                pattern_id="",  # Will be set in __post_init__
                pattern_type=ICTPatternType.ORDER_BLOCK,
                direction=ob_direction,
                timeframe=timeframe,
                detection_time=datetime.utcnow(),
                top=top,
                bottom=bottom,
                entry_level=entry_level,
                strength=min(1.0, displacement_strength * volume_confirmation),
                confidence=min(1.0, institutional_footprint * 1.2),
                volume_confirmation=volume_confirmation,
                formation_candles=[data.index.get_loc(idx)],
                displacement_strength=displacement_strength,
                institutional_footprint=institutional_footprint
            )
            
            # Calculate risk-reward
            self._calculate_pattern_risk_reward(pattern, data)
            
            return pattern
            
        except Exception as e:
            self.logger.error(f"Error creating enhanced order block: {e}")
            return None
    
    def _calculate_volume_confirmation(self, data: pd.DataFrame, idx: pd.Timestamp) -> float:
        """Calculate volume confirmation for pattern"""
        try:
            if 'volume' not in data.columns:
                return 0.7  # Default confirmation if no volume data
            
            candle_volume = data.loc[idx, 'volume']
            
            # Calculate average volume
            loc = data.index.get_loc(idx)
            start_idx = max(0, loc - 20)
            avg_volume = data.iloc[start_idx:loc]['volume'].mean()
            
            if avg_volume > 0:
                volume_ratio = candle_volume / avg_volume
                return min(1.0, volume_ratio / self.volume_confirmation_threshold)
            
            return 0.5
            
        except Exception as e:
            self.logger.error(f"Error calculating volume confirmation: {e}")
            return 0.5
    
    def _calculate_displacement_strength(self, data: pd.DataFrame, idx: pd.Timestamp) -> float:
        """Calculate displacement strength for pattern formation"""
        try:
            candle = data.loc[idx]
            candle_range = candle['high'] - candle['low']
            
            # Calculate average range
            loc = data.index.get_loc(idx)
            start_idx = max(0, loc - 14)
            avg_range = (data.iloc[start_idx:loc]['high'] - data.iloc[start_idx:loc]['low']).mean()
            
            if avg_range > 0:
                displacement_ratio = candle_range / avg_range
                return min(1.0, displacement_ratio / 2.0)
            
            return 0.5
            
        except Exception as e:
            self.logger.error(f"Error calculating displacement strength: {e}")
            return 0.5
    
    def _calculate_institutional_footprint(self, data: pd.DataFrame, idx: pd.Timestamp) -> float:
        """Calculate institutional footprint score"""
        try:
            footprint_score = 0.0
            
            # Volume analysis
            volume_conf = self._calculate_volume_confirmation(data, idx)
            footprint_score += volume_conf * 0.4
            
            # Displacement analysis
            displacement = self._calculate_displacement_strength(data, idx)
            footprint_score += displacement * 0.3
            
            # Body-to-wick ratio (institutional candles have strong bodies)
            candle = data.loc[idx]
            body_size = abs(candle['close'] - candle['open'])
            total_range = candle['high'] - candle['low']
            
            if total_range > 0:
                body_ratio = body_size / total_range
                footprint_score += body_ratio * 0.3
            
            return min(1.0, footprint_score)
            
        except Exception as e:
            self.logger.error(f"Error calculating institutional footprint: {e}")
            return 0.5
    
    def _validate_order_block(self, pattern: ICTPattern, data: pd.DataFrame) -> bool:
        """Validate order block pattern quality"""
        try:
            # Minimum strength requirement
            if pattern.strength < self.pattern_min_strength:
                return False
            
            # Minimum displacement requirement
            if pattern.displacement_strength < 0.3:
                return False
            
            # Pattern must have reasonable size
            pattern_size = abs(pattern.top - pattern.bottom)
            current_price = data['close'].iloc[-1]
            
            if pattern_size < current_price * 0.0001:  # Minimum 1 pip for forex
                return False
            
            if pattern_size > current_price * 0.02:  # Maximum 2% of price
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating order block: {e}")
            return False
    
    def _calculate_pattern_risk_reward(self, pattern: ICTPattern, data: pd.DataFrame):
        """Calculate risk-reward metrics for pattern"""
        try:
            current_price = data['close'].iloc[-1]
            
            if pattern.direction == 'bullish':
                # Long setup
                entry = pattern.entry_level
                stop_loss = pattern.bottom * 0.999  # Slightly below OB
                
                # Target levels (conservative approach)
                target_1 = entry + (entry - stop_loss) * 1.5  # 1:1.5 RR
                target_2 = entry + (entry - stop_loss) * 2.0  # 1:2 RR
                target_3 = entry + (entry - stop_loss) * 3.0  # 1:3 RR
                
                pattern.stop_loss_level = stop_loss
                pattern.take_profit_levels = [target_1, target_2, target_3]
                
                if entry > stop_loss:
                    pattern.risk_reward_ratio = (target_1 - entry) / (entry - stop_loss)
                
            else:
                # Short setup
                entry = pattern.entry_level
                stop_loss = pattern.top * 1.001  # Slightly above OB
                
                # Target levels
                target_1 = entry - (stop_loss - entry) * 1.5
                target_2 = entry - (stop_loss - entry) * 2.0
                target_3 = entry - (stop_loss - entry) * 3.0
                
                pattern.stop_loss_level = stop_loss
                pattern.take_profit_levels = [target_1, target_2, target_3]
                
                if stop_loss > entry:
                    pattern.risk_reward_ratio = (entry - target_1) / (stop_loss - entry)
                    
        except Exception as e:
            self.logger.error(f"Error calculating pattern risk-reward: {e}")
    
    def _update_fair_value_gaps(self, symbol: str, data: pd.DataFrame, timeframe: str):
        """Update Fair Value Gap detection with mitigation tracking"""
        try:
            # Use smartmoneyconcepts library for FVG detection
            fvgs = smc.fvg(data)
            
            if fvgs is None or fvgs.empty:
                return
            
            new_fvgs = []
            for idx, fvg in fvgs.iterrows():
                if pd.notna(fvg.get('FVG', np.nan)):
                    # Create enhanced FVG pattern
                    fvg_pattern = self._create_enhanced_fvg(data, idx, fvg, timeframe)
                    if fvg_pattern and self._validate_fvg(fvg_pattern, data):
                        new_fvgs.append(fvg_pattern)
                        self.performance_metrics['patterns_detected'] += 1
            
            # Add to storage
            if timeframe not in self.active_patterns:
                self.active_patterns[timeframe] = []
            
            self.active_patterns[timeframe].extend(new_fvgs)
            
        except Exception as e:
            self.logger.error(f"Error updating fair value gaps: {e}")
    
    def _create_enhanced_fvg(self, data: pd.DataFrame, idx: pd.Timestamp, 
                           fvg_data: pd.Series, timeframe: str) -> ICTPattern:
        """Create enhanced Fair Value Gap pattern"""
        try:
            fvg_direction = 'bullish' if fvg_data.get('FVG', 0) > 0 else 'bearish'
            
            # Get FVG boundaries from smartmoneyconcepts
            top = fvg_data.get('top', data.loc[idx, 'high'])
            bottom = fvg_data.get('bottom', data.loc[idx, 'low'])
            
            # Entry level (typically middle of gap)
            entry_level = (top + bottom) / 2
            
            # Calculate gap size
            gap_size = abs(top - bottom)
            
            # Validate minimum gap size
            pip_size = self._get_pip_size(symbol)
            min_gap = self.fvg_min_gap_pips * pip_size
            
            if gap_size < min_gap:
                return None
            
            # Calculate pattern strength based on gap size and context
            avg_range = (data['high'] - data['low']).rolling(20).mean().iloc[-1]
            strength = min(1.0, gap_size / avg_range) if avg_range > 0 else 0.5
            
            # Create FVG pattern
            pattern = ICTPattern(
                pattern_id="",
                pattern_type=ICTPatternType.FAIR_VALUE_GAP,
                direction=fvg_direction,
                timeframe=timeframe,
                detection_time=datetime.utcnow(),
                top=top,
                bottom=bottom,
                entry_level=entry_level,
                strength=strength,
                confidence=0.8,  # FVGs generally have high confidence
                volume_confirmation=self._calculate_volume_confirmation(data, idx),
                formation_candles=self._get_fvg_formation_candles(data, idx),
                mitigation_level=(top + bottom) / 2  # 50% mitigation
            )
            
            # Calculate risk-reward
            self._calculate_pattern_risk_reward(pattern, data)
            
            return pattern
            
        except Exception as e:
            self.logger.error(f"Error creating enhanced FVG: {e}")
            return None
    
    def _get_fvg_formation_candles(self, data: pd.DataFrame, idx: pd.Timestamp) -> List[int]:
        """Get the three candles that form the FVG"""
        try:
            loc = data.index.get_loc(idx)
            # FVG is typically formed by 3 candles: before, gap candle, after
            if loc >= 1 and loc < len(data) - 1:
                return [loc - 1, loc, loc + 1]
            return [loc]
            
        except Exception as e:
            self.logger.error(f"Error getting FVG formation candles: {e}")
            return []
    
    def _validate_fvg(self, pattern: ICTPattern, data: pd.DataFrame) -> bool:
        """Validate Fair Value Gap pattern"""
        try:
            # Gap must be significant enough
            gap_size = abs(pattern.top - pattern.bottom)
            current_price = data['close'].iloc[-1]
            
            min_gap_percent = 0.0005  # 0.05% minimum gap
            if gap_size < current_price * min_gap_percent:
                return False
            
            max_gap_percent = 0.01  # 1% maximum gap
            if gap_size > current_price * max_gap_percent:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating FVG: {e}")
            return False
    
    def _update_breaker_blocks(self, symbol: str, data: pd.DataFrame, timeframe: str):
        """Update Breaker Block detection (failed Order Blocks)"""
        try:
            # Get existing Order Blocks for this timeframe
            if timeframe not in self.active_patterns:
                return
            
            order_blocks = [p for p in self.active_patterns[timeframe] 
                          if p.pattern_type == ICTPatternType.ORDER_BLOCK and not p.is_mitigated]
            
            new_breakers = []
            
            for ob in order_blocks:
                # Check if Order Block has been violated (became a breaker)
                if self._is_order_block_violated(ob, data):
                    breaker = self._create_breaker_block(ob, data, timeframe)
                    if breaker:
                        new_breakers.append(breaker)
                        # Mark original OB as mitigated
                        ob.is_mitigated = True
                        ob.mitigation_time = datetime.utcnow()
            
            # Add new breakers to storage
            self.active_patterns[timeframe].extend(new_breakers)
            
        except Exception as e:
            self.logger.error(f"Error updating breaker blocks: {e}")
    
    def _is_order_block_violated(self, ob: ICTPattern, data: pd.DataFrame) -> bool:
        """Check if Order Block has been violated"""
        try:
            current_price = data['close'].iloc[-1]
            
            if ob.direction == 'bullish':
                # Bullish OB violated if price closes significantly below
                return current_price < ob.bottom * 0.999
            else:
                # Bearish OB violated if price closes significantly above
                return current_price > ob.top * 1.001
                
        except Exception as e:
            self.logger.error(f"Error checking OB violation: {e}")
            return False
    
    def _create_breaker_block(self, original_ob: ICTPattern, data: pd.DataFrame, 
                            timeframe: str) -> ICTPattern:
        """Create Breaker Block from failed Order Block"""
        try:
            # Breaker has opposite direction to original OB
            breaker_direction = 'bearish' if original_ob.direction == 'bullish' else 'bullish'
            
            # Create breaker pattern
            breaker = ICTPattern(
                pattern_id="",
                pattern_type=ICTPatternType.BREAKER_BLOCK,
                direction=breaker_direction,
                timeframe=timeframe,
                detection_time=datetime.utcnow(),
                top=original_ob.top,
                bottom=original_ob.bottom,
                entry_level=original_ob.entry_level,
                strength=original_ob.strength * 1.2,  # Breakers often stronger
                confidence=original_ob.confidence * 1.1,
                volume_confirmation=original_ob.volume_confirmation,
                formation_candles=original_ob.formation_candles,
                institutional_footprint=original_ob.institutional_footprint * 1.1
            )
            
            # Calculate new risk-reward for breaker
            self._calculate_pattern_risk_reward(breaker, data)
            
            return breaker
            
        except Exception as e:
            self.logger.error(f"Error creating breaker block: {e}")
            return None
    
    def _update_liquidity_levels(self, symbol: str, data: pd.DataFrame, timeframe: str):
        """Update liquidity level detection"""
        try:
            # Find swing points for liquidity identification
            swing_points = find_swing_points(data, self.swing_length)
            
            if len(swing_points) < 2:
                return
            
            new_liquidity = []
            
            # Identify Buy-Side Liquidity (above swing highs)
            highs = swing_points[swing_points['swing_type'] == 'high']
            for idx, high in highs.tail(10).iterrows():  # Last 10 swing highs
                liquidity_level = LiquidityLevel(
                    level=high['price'],
                    liquidity_type=LiquidityType.BUY_SIDE_LIQUIDITY,
                    strength=self._calculate_liquidity_strength(data, idx, 'high'),
                    creation_time=datetime.utcnow(),
                    timeframe=timeframe,
                    expected_reaction='bearish'  # After sweep, expect bearish reaction
                )
                new_liquidity.append(liquidity_level)
            
            # Identify Sell-Side Liquidity (below swing lows)
            lows = swing_points[swing_points['swing_type'] == 'low']
            for idx, low in lows.tail(10).iterrows():  # Last 10 swing lows
                liquidity_level = LiquidityLevel(
                    level=low['price'],
                    liquidity_type=LiquidityType.SELL_SIDE_LIQUIDITY,
                    strength=self._calculate_liquidity_strength(data, idx, 'low'),
                    creation_time=datetime.utcnow(),
                    timeframe=timeframe,
                    expected_reaction='bullish'  # After sweep, expect bullish reaction
                )
                new_liquidity.append(liquidity_level)
            
            # Store liquidity levels
            if timeframe not in self.liquidity_levels:
                self.liquidity_levels[timeframe] = []
            
            self.liquidity_levels[timeframe].extend(new_liquidity)
            
            # Limit storage
            if len(self.liquidity_levels[timeframe]) > 30:
                self.liquidity_levels[timeframe] = self.liquidity_levels[timeframe][-20:]
                
        except Exception as e:
            self.logger.error(f"Error updating liquidity levels: {e}")
    
    def _calculate_liquidity_strength(self, data: pd.DataFrame, idx: pd.Timestamp, 
                                    swing_type: str) -> float:
        """Calculate strength of liquidity level"""
        try:
            # Get the swing point data
            swing_point = data.loc[idx]
            
            # Calculate how significant this swing was
            loc = data.index.get_loc(idx)
            lookback = min(20, loc)
            
            if swing_type == 'high':
                recent_highs = data.iloc[loc-lookback:loc+1]['high']
                rank = stats.percentileofscore(recent_highs, swing_point['high']) / 100
            else:
                recent_lows = data.iloc[loc-lookback:loc+1]['low']
                rank = (100 - stats.percentileofscore(recent_lows, swing_point['low'])) / 100
            
            # Consider volume if available
            volume_factor = 1.0
            if 'volume' in data.columns:
                volume = swing_point['volume']
                avg_volume = data.iloc[loc-lookback:loc]['volume'].mean()
                if avg_volume > 0:
                    volume_factor = min(2.0, volume / avg_volume)
            
            return min(1.0, rank * volume_factor)
            
        except Exception as e:
            self.logger.error(f"Error calculating liquidity strength: {e}")
            return 0.5
    
    def _check_pattern_mitigation(self, symbol: str, data: pd.DataFrame, timeframe: str):
        """Check if patterns have been mitigated"""
        try:
            if timeframe not in self.active_patterns:
                return
            
            current_price = data['close'].iloc[-1]
            tolerance = self.mitigation_tolerance_pips * self._get_pip_size(symbol)
            
            for pattern in self.active_patterns[timeframe]:
                if pattern.is_mitigated:
                    continue
                
                # Check mitigation based on pattern type
                if pattern.pattern_type in [ICTPatternType.ORDER_BLOCK, ICTPatternType.BREAKER_BLOCK]:
                    # Check if price has returned to pattern area
                    in_pattern_area = pattern.bottom <= current_price <= pattern.top
                    
                    if in_pattern_area:
                        pattern.is_mitigated = True
                        pattern.mitigation_time = datetime.utcnow()
                        self.performance_metrics['patterns_validated'] += 1
                
                elif pattern.pattern_type == ICTPatternType.FAIR_VALUE_GAP:
                    # FVG mitigation (typically 50% fill)
                    if pattern.mitigation_level:
                        if pattern.direction == 'bullish':
                            # Bullish FVG mitigated when price trades back down into gap
                            if current_price <= pattern.mitigation_level + tolerance:
                                pattern.is_mitigated = True
                                pattern.mitigation_time = datetime.utcnow()
                        else:
                            # Bearish FVG mitigated when price trades back up into gap
                            if current_price >= pattern.mitigation_level - tolerance:
                                pattern.is_mitigated = True
                                pattern.mitigation_time = datetime.utcnow()
                                
        except Exception as e:
            self.logger.error(f"Error checking pattern mitigation: {e}")
    
    def _process_ict_state_machine(self, symbol: str, data: Dict[str, pd.DataFrame]) -> List[SignalEvent]:
        """Process ICT state machine logic"""
        try:
            signals = []
            
            if self.state == StrategyState.AWAITING_CONTEXT:
                signals.extend(self._handle_awaiting_context(symbol, data))
            
            elif self.state == StrategyState.MONITORING_POI:
                signals.extend(self._handle_monitoring_poi(symbol, data))
            
            elif self.state == StrategyState.SCANNING_ENTRY:
                signals.extend(self._handle_scanning_entry(symbol, data))
            
            elif self.state == StrategyState.POSITION_MANAGEMENT:
                signals.extend(self._handle_position_management(symbol, data))
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Error processing ICT state machine: {e}")
            return []
    
    def _handle_awaiting_context(self, symbol: str, data: Dict[str, pd.DataFrame]) -> List[SignalEvent]:
        """Handle AWAITING_CONTEXT state"""
        signals = []
        
        try:
            # Check if we have sufficient HTF context
            htf_pois = []
            for timeframe in self.htf_timeframes:
                if timeframe in self.active_patterns:
                    htf_pois.extend([p for p in self.active_patterns[timeframe] 
                                   if not p.is_mitigated and p.strength > 0.6])
            
            # Update context with HTF POIs
            self.current_context.htf_pois = htf_pois
            
            if (self.current_context.daily_bias != 'neutral' and 
                len(self.current_context.htf_pois) > 0):
                
                # Transition to monitoring POI
                self.transition_state(StrategyState.MONITORING_POI)
                
                signals.append(SignalEvent(
                    event_type='ICT_HTF_CONTEXT_ESTABLISHED',
                    symbol=symbol,
                    timeframe='HTF',
                    timestamp=datetime.utcnow(),
                    direction=self.current_context.daily_bias,
                    strength=0.8,
                    metadata={
                        'poi_count': len(self.current_context.htf_pois),
                        'daily_bias': self.current_context.daily_bias,
                        'session_bias': self.current_context.session_bias,
                        'current_session': self.current_context.current_session,
                        'institutional_activity': self.current_context.institutional_activity
                    }
                ))
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Error handling awaiting context: {e}")
            return []
    
    def _handle_monitoring_poi(self, symbol: str, data: Dict[str, pd.DataFrame]) -> List[SignalEvent]:
        """Handle MONITORING_POI state"""
        signals = []
        
        try:
            if self.trading_timeframe not in data:
                return signals
            
            current_price = data[self.trading_timeframe]['close'].iloc[-1]
            
            # Check if price has entered any HTF POI
            for poi in self.current_context.htf_pois:
                if self._price_in_pattern_area(current_price, poi):
                    # Transition to scanning for entry
                    self.transition_state(StrategyState.SCANNING_ENTRY)
                    
                    # Calculate signal strength based on POI quality
                    signal_strength = min(1.0, poi.strength * poi.confidence * 
                                        self.current_context.institutional_activity)
                    
                    signals.append(SignalEvent(
                        event_type='ICT_POI_ENTERED',
                        symbol=symbol,
                        timeframe=self.trading_timeframe,
                        timestamp=datetime.utcnow(),
                        direction=poi.direction,
                        strength=signal_strength * self.poi_confluence_score / 5.0,
                        level=current_price,
                        metadata={
                            'poi_id': poi.pattern_id,
                            'poi_type': poi.pattern_type.value,
                            'poi_timeframe': poi.timeframe,
                            'poi_strength': poi.strength,
                            'poi_confidence': poi.confidence,
                            'pattern_top': poi.top,
                            'pattern_bottom': poi.bottom,
                            'entry_level': poi.entry_level,
                            'risk_reward_ratio': poi.risk_reward_ratio,
                            'institutional_footprint': poi.institutional_footprint
                        }
                    ))
                    break
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Error handling monitoring POI: {e}")
            return []
    
    def _handle_scanning_entry(self, symbol: str, data: Dict[str, pd.DataFrame]) -> List[SignalEvent]:
        """Handle SCANNING_ENTRY state with advanced entry models"""
        signals = []
        
        try:
            if self.entry_timeframe not in data:
                return signals
            
            entry_data = data[self.entry_timeframe]
            
            # Look for entry model pattern based on configuration
            if self.entry_model == ICTEntryModel.MENTORSHIP_2022:
                entry_signals = self._scan_mentorship_2022_model(symbol, entry_data)
                signals.extend(entry_signals)
            
            elif self.entry_model == ICTEntryModel.OPTIMAL_TRADE_ENTRY:
                entry_signals = self._scan_ote_model(symbol, entry_data)
                signals.extend(entry_signals)
            
            elif self.entry_model == ICTEntryModel.SILVER_BULLET:
                entry_signals = self._scan_silver_bullet_model(symbol, entry_data)
                signals.extend(entry_signals)
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Error handling scanning entry: {e}")
            return []
    
    def _handle_position_management(self, symbol: str, data: Dict[str, pd.DataFrame]) -> List[SignalEvent]:
        """Handle position management state"""
        signals = []
        
        try:
            # This would handle position management logic
            # For now, return empty as position management is handled by execution engine
            return signals
            
        except Exception as e:
            self.logger.error(f"Error handling position management: {e}")
            return []
    
    def _price_in_pattern_area(self, price: float, pattern: ICTPattern) -> bool:
        """Check if price is within pattern area"""
        try:
            return pattern.bottom <= price <= pattern.top
        except Exception as e:
            self.logger.error(f"Error checking price in pattern area: {e}")
            return False
    
    def _scan_mentorship_2022_model(self, symbol: str, data: pd.DataFrame) -> List[SignalEvent]:
        """Scan for ICT 2022 Mentorship entry model"""
        signals = []
        
        try:
            if len(data) < 20:
                return signals
            
            # Step 1: Look for liquidity sweep
            liquidity_sweep = self._detect_liquidity_sweep(data, symbol)
            
            if not liquidity_sweep:
                return signals
            
            # Step 2: Look for Market Structure Shift after sweep
            mss_result = self._detect_market_structure_shift_after_sweep(data, liquidity_sweep)
            
            if mss_result:
                signals.append(SignalEvent(
                    event_type='ICT_MSS_CONFIRMED',
                    symbol=symbol,
                    timeframe=self.entry_timeframe,
                    timestamp=datetime.utcnow(),
                    direction=mss_result['direction'],
                    strength=mss_result['strength'] * self.mss_confluence_score / 5.0,
                    metadata={
                        'sweep_type': liquidity_sweep['type'],
                        'sweep_level': liquidity_sweep['level'],
                        'displacement_strength': mss_result['strength'],
                        'mss_candles': mss_result.get('displacement_candles', [])
                    }
                ))
                
                # Step 3: Look for entry zone formation
                entry_zone = self._find_entry_zone_after_mss(data, mss_result)
                
                if entry_zone:
                    signals.append(SignalEvent(
                        event_type='ICT_ENTRY_ZONE_FORMED',
                        symbol=symbol,
                        timeframe=self.entry_timeframe,
                        timestamp=datetime.utcnow(),
                        direction=mss_result['direction'],
                        strength=self._calculate_entry_zone_strength(entry_zone),
                        level=entry_zone['entry_level'],
                        metadata={
                            'zone_type': entry_zone['type'],
                            'zone_top': entry_zone['top'],
                            'zone_bottom': entry_zone['bottom'],
                            'entry_level': entry_zone['entry_level'],
                            'stop_level': entry_zone.get('stop_level'),
                            'formation_method': '2022_mentorship'
                        }
                    ))
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Error scanning mentorship 2022 model: {e}")
            return []
    
    def _detect_liquidity_sweep(self, data: pd.DataFrame, symbol: str) -> Optional[Dict[str, Any]]:
        """Detect liquidity sweep pattern"""
        try:
            if len(data) < 10:
                return None
            
            # Get recent liquidity levels for this timeframe
            timeframe_liquidity = self.liquidity_levels.get(self.entry_timeframe, [])
            
            if not timeframe_liquidity:
                return None
            
            current_price = data['close'].iloc[-1]
            prev_price = data['close'].iloc[-2]
            tolerance = self.mitigation_tolerance_pips * self._get_pip_size(symbol)
            
            # Check for liquidity sweeps
            for liquidity in timeframe_liquidity:
                if liquidity.is_swept:
                    continue
                
                # Check for upward sweep (Buy-Side Liquidity)
                if (liquidity.liquidity_type == LiquidityType.BUY_SIDE_LIQUIDITY and
                    prev_price <= liquidity.level and 
                    current_price > liquidity.level + tolerance):
                    
                    liquidity.is_swept = True
                    liquidity.sweep_time = datetime.utcnow()
                    self.performance_metrics['liquidity_sweeps_detected'] += 1
                    
                    return {
                        'type': 'buy_side_sweep',
                        'level': liquidity.level,
                        'strength': liquidity.strength,
                        'expected_reaction': liquidity.expected_reaction
                    }
                
                # Check for downward sweep (Sell-Side Liquidity)
                elif (liquidity.liquidity_type == LiquidityType.SELL_SIDE_LIQUIDITY and
                      prev_price >= liquidity.level and 
                      current_price < liquidity.level - tolerance):
                    
                    liquidity.is_swept = True
                    liquidity.sweep_time = datetime.utcnow()
                    self.performance_metrics['liquidity_sweeps_detected'] += 1
                    
                    return {
                        'type': 'sell_side_sweep',
                        'level': liquidity.level,
                        'strength': liquidity.strength,
                        'expected_reaction': liquidity.expected_reaction
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error detecting liquidity sweep: {e}")
            return None
    
    def _detect_market_structure_shift_after_sweep(self, data: pd.DataFrame, 
                                                  sweep: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect Market Structure Shift after liquidity sweep"""
        try:
            if len(data) < 5:
                return None
            
            # Look for strong displacement move after sweep
            displacement_candles = data.tail(3)
            
            if len(displacement_candles) < 3:
                return None
            
            # Calculate displacement metrics
            total_displacement = abs(displacement_candles['close'].iloc[-1] - 
                                   displacement_candles['open'].iloc[0])
            
            individual_ranges = displacement_candles['high'] - displacement_candles['low']
            avg_range = individual_ranges.mean()
            
            # Displacement strength
            displacement_strength = total_displacement / (avg_range * 3) if avg_range > 0 else 0
            
            # Direction should be opposite to sweep
            expected_direction = sweep['expected_reaction']
            actual_direction = 'bullish' if displacement_candles['close'].iloc[-1] > displacement_candles['open'].iloc[0] else 'bearish'
            
            # Confirm MSS if displacement is strong and in expected direction
            if displacement_strength > 1.5 and actual_direction == expected_direction:
                return {
                    'direction': actual_direction,
                    'strength': min(1.0, displacement_strength / 3.0),
                    'displacement_candles': displacement_candles.index.tolist(),
                    'displacement_start': displacement_candles.index[0],
                    'displacement_end': displacement_candles.index[-1]
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error detecting MSS after sweep: {e}")
            return None
    
    def _find_entry_zone_after_mss(self, data: pd.DataFrame, 
                                  mss: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find entry zone after Market Structure Shift"""
        try:
            # Get displacement candles
            displacement_start = mss['displacement_start']
            displacement_end = mss['displacement_end']
            
            # Find the displacement move data
            start_idx = data.index.get_loc(displacement_start)
            end_idx = data.index.get_loc(displacement_end)
            
            displacement_data = data.iloc[start_idx:end_idx+1]
            
            if len(displacement_data) < 2:
                return None
            
            # Look for FVG in displacement move
            if len(displacement_data) >= 3:
                fvg_zone = self._find_fvg_in_displacement(displacement_data, mss['direction'])
                if fvg_zone:
                    return fvg_zone
            
            # Look for Order Block before displacement
            ob_zone = self._find_order_block_before_displacement(data, start_idx, mss['direction'])
            if ob_zone:
                return ob_zone
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding entry zone after MSS: {e}")
            return None
    
    def _find_fvg_in_displacement(self, displacement_data: pd.DataFrame, direction: str) -> Optional[Dict[str, Any]]:
        """Find Fair Value Gap in displacement move"""
        try:
            if len(displacement_data) < 3:
                return None
            
            # Check for 3-candle FVG pattern
            for i in range(len(displacement_data) - 2):
                candle1 = displacement_data.iloc[i]
                candle2 = displacement_data.iloc[i + 1]  # Gap candle
                candle3 = displacement_data.iloc[i + 2]
                
                # Bullish FVG: candle1 high < candle3 low
                if direction == 'bullish' and candle1['high'] < candle3['low']:
                    return {
                        'type': 'fvg',
                        'direction': 'bullish',
                        'top': candle3['low'],
                        'bottom': candle1['high'],
                        'entry_level': (candle1['high'] + candle3['low']) / 2,
                        'stop_level': candle1['low']
                    }
                
                # Bearish FVG: candle1 low > candle3 high
                elif direction == 'bearish' and candle1['low'] > candle3['high']:
                    return {
                        'type': 'fvg',
                        'direction': 'bearish',
                        'top': candle1['low'],
                        'bottom': candle3['high'],
                        'entry_level': (candle1['low'] + candle3['high']) / 2,
                        'stop_level': candle1['high']
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding FVG in displacement: {e}")
            return None
    
    def _find_order_block_before_displacement(self, data: pd.DataFrame, displacement_start: int, 
                                            direction: str) -> Optional[Dict[str, Any]]:
        """Find Order Block before displacement move"""
        try:
            # Look back before displacement for the last opposite-direction candle
            search_range = min(10, displacement_start)
            
            for i in range(displacement_start - 1, displacement_start - search_range - 1, -1):
                if i < 0:
                    break
                
                candle = data.iloc[i]
                
                # For bullish displacement, find last bearish candle
                if direction == 'bullish' and candle['close'] < candle['open']:
                    return {
                        'type': 'order_block',
                        'direction': 'bullish',
                        'top': candle['high'],
                        'bottom': candle['low'],
                        'entry_level': candle['low'],
                        'stop_level': candle['low'] * 0.999
                    }
                
                # For bearish displacement, find last bullish candle
                elif direction == 'bearish' and candle['close'] > candle['open']:
                    return {
                        'type': 'order_block',
                        'direction': 'bearish',
                        'top': candle['high'],
                        'bottom': candle['low'],
                        'entry_level': candle['high'],
                        'stop_level': candle['high'] * 1.001
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding order block before displacement: {e}")
            return None
    
    def _calculate_entry_zone_strength(self, entry_zone: Dict[str, Any]) -> float:
        """Calculate entry zone signal strength"""
        try:
            base_strength = 0.8  # Base strength for ICT entry zones
            
            # Adjust based on zone type
            if entry_zone['type'] == 'fvg':
                zone_multiplier = self.fvg_confluence_score
            elif entry_zone['type'] == 'order_block':
                zone_multiplier = self.ob_confluence_score
            else:
                zone_multiplier = 2.0
            
            # Include liquidity sweep bonus
            total_strength = base_strength + self.liquidity_sweep_bonus
            
            # Normalize to confluence score scale
            return min(1.0, total_strength * zone_multiplier / 5.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating entry zone strength: {e}")
            return 0.5
    
    def _scan_ote_model(self, symbol: str, data: pd.DataFrame) -> List[SignalEvent]:
        """Scan for Optimal Trade Entry model"""
        signals = []
        
        try:
            # OTE model implementation would go here
            # This is a placeholder for the Optimal Trade Entry methodology
            pass
            
        except Exception as e:
            self.logger.error(f"Error scanning OTE model: {e}")
        
        return signals
    
    def _scan_silver_bullet_model(self, symbol: str, data: pd.DataFrame) -> List[SignalEvent]:
        """Scan for Silver Bullet model"""
        signals = []
        
        try:
            # Silver Bullet model implementation would go here
            # This focuses on specific time-based entry windows
            pass
            
        except Exception as e:
            self.logger.error(f"Error scanning Silver Bullet model: {e}")
        
        return signals
    
    def _update_performance_metrics(self, signals: List[SignalEvent]):
        """Update ICT strategy performance metrics"""
        try:
            # Count different signal types
            poi_signals = [s for s in signals if 'POI' in s.event_type]
            mss_signals = [s for s in signals if 'MSS' in s.event_type]
            entry_signals = [s for s in signals if 'ENTRY_ZONE' in s.event_type]
            
            # Update metrics
            if entry_signals:
                self.performance_metrics['successful_entries'] += len(entry_signals)
            
            # Calculate average signal strength
            if poi_signals:
                avg_strength = sum(s.strength for s in poi_signals) / len(poi_signals)
                self.performance_metrics['average_pattern_strength'] = (
                    (self.performance_metrics['average_pattern_strength'] + avg_strength) / 2
                )
            
        except Exception as e:
            self.logger.error(f"Error updating performance metrics: {e}")
    
    def _cleanup_old_patterns(self):
        """Clean up old and expired patterns"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=self.pattern_timeout_hours)
            
            for timeframe in self.active_patterns:
                old_count = len(self.active_patterns[timeframe])
                
                # Remove old patterns
                self.active_patterns[timeframe] = [
                    p for p in self.active_patterns[timeframe]
                    if p.detection_time >= cutoff_time
                ]
                
                # Update time validity for remaining patterns
                for pattern in self.active_patterns[timeframe]:
                    hours_old = (datetime.utcnow() - pattern.detection_time).total_seconds() / 3600
                    pattern.time_validity = max(0.1, 1.0 - (hours_old / self.pattern_timeout_hours))
                
                if len(self.active_patterns[timeframe]) < old_count:
                    self.logger.debug(f"Cleaned {old_count - len(self.active_patterns[timeframe])} old patterns from {timeframe}")
            
            # Clean liquidity levels
            for timeframe in self.liquidity_levels:
                old_count = len(self.liquidity_levels[timeframe])
                
                self.liquidity_levels[timeframe] = [
                    l for l in self.liquidity_levels[timeframe]
                    if l.creation_time >= cutoff_time
                ]
                
                if len(self.liquidity_levels[timeframe]) < old_count:
                    self.logger.debug(f"Cleaned {old_count - len(self.liquidity_levels[timeframe])} old liquidity levels from {timeframe}")
                    
        except Exception as e:
            self.logger.error(f"Error cleaning old patterns: {e}")
    
    def _get_pip_size(self, symbol: str) -> float:
        """Get pip size for symbol"""
        try:
            pip_sizes = {
                'EURUSD': 0.0001, 'GBPUSD': 0.0001, 'USDJPY': 0.01,
                'AUDUSD': 0.0001, 'USDCAD': 0.0001, 'USDCHF': 0.0001,
                'NZDUSD': 0.0001, 'EURGBP': 0.0001, 'EURJPY': 0.01,
                'GBPJPY': 0.01, 'AUDJPY': 0.01, 'CADJPY': 0.01,
                'XAUUSD': 0.01, 'GOLD': 0.01, 'CRUDE': 0.01, 'USOIL': 0.01
            }
            
            return pip_sizes.get(symbol.upper(), 0.0001)
            
        except Exception as e:
            self.logger.error(f"Error getting pip size: {e}")
            return 0.0001
    
    # Implementation of inherited abstract methods
    
    def identify_trading_zones(self, data: Dict[str, pd.DataFrame]) -> List[Dict[str, Any]]:
        """Identify high-probability ICT trading zones"""
        try:
            zones = []
            
            # Add all active patterns as trading zones
            for timeframe, patterns in self.active_patterns.items():
                for pattern in patterns:
                    if pattern.is_mitigated or pattern.time_validity < 0.3:
                        continue
                    
                    quality_score = pattern.strength * pattern.confidence * pattern.time_validity
                    
                    zones.append({
                        'type': 'ict_pattern',
                        'subtype': pattern.pattern_type.value,
                        'timeframe': timeframe,
                        'top': pattern.top,
                        'bottom': pattern.bottom,
                        'direction': pattern.direction,
                        'strength': pattern.strength,
                        'quality_score': quality_score,
                        'confluence_score': self._calculate_pattern_confluence_score(pattern),
                        'institutional_footprint': pattern.institutional_footprint,
                        'pattern_id': pattern.pattern_id,
                        'entry_level': pattern.entry_level,
                        'risk_reward_ratio': pattern.risk_reward_ratio
                    })
            
            # Sort by quality score
            zones.sort(key=lambda x: x['quality_score'], reverse=True)
            
            return zones[:30]  # Top 30 zones
            
        except Exception as e:
            self.logger.error(f"Error identifying trading zones: {e}")
            return []
    
    def scan_for_entry_models(self, data: Dict[str, pd.DataFrame], 
                             zones: List[Dict[str, Any]]) -> List[TradeSetup]:
        """Scan for ICT entry patterns within identified zones"""
        try:
            setups = []
            
            for zone in zones:
                if zone['type'] != 'ict_pattern':
                    continue
                
                # Check if we have entry timeframe data
                if self.entry_timeframe not in data:
                    continue
                
                entry_data = data[self.entry_timeframe]
                current_price = entry_data['close'].iloc[-1]
                
                # Check if price is in this zone
                if zone['bottom'] <= current_price <= zone['top']:
                    # Look for entry model within zone
                    if self.entry_model == ICTEntryModel.MENTORSHIP_2022:
                        entry_signals = self._scan_mentorship_2022_model('', entry_data)
                        
                        for signal in entry_signals:
                            if signal.event_type == 'ICT_ENTRY_ZONE_FORMED':
                                setup = TradeSetup(
                                    symbol='',  # Will be filled by calling function
                                    direction='long' if signal.direction == 'bullish' else 'short',
                                    entry_price=signal.level,
                                    stop_loss=signal.metadata.get('stop_level', 0.0),
                                    take_profit=None,  # Will be calculated
                                    position_size=0.0,  # Will be calculated by risk manager
                                    confluence_score=zone['confluence_score'],
                                    strategy_source='enhanced_ict',
                                    timeframe=self.entry_timeframe,
                                    timestamp=datetime.utcnow(),
                                    metadata={
                                        'zone_info': zone,
                                        'entry_model': self.entry_model.value,
                                        'pattern_type': zone['subtype'],
                                        'pattern_id': zone['pattern_id'],
                                        'institutional_footprint': zone['institutional_footprint'],
                                        'signal_metadata': signal.metadata,
                                        'risk_reward_ratio': zone['risk_reward_ratio']
                                    }
                                )
                                setups.append(setup)
            
            return setups
            
        except Exception as e:
            self.logger.error(f"Error scanning for ICT entry models: {e}")
            return []
    
    def _calculate_pattern_confluence_score(self, pattern: ICTPattern) -> float:
        """Calculate confluence score for a pattern"""
        try:
            base_score = pattern.strength * pattern.confidence
            
            # Pattern type weights
            type_weights = {
                ICTPatternType.ORDER_BLOCK: self.ob_confluence_score,
                ICTPatternType.FAIR_VALUE_GAP: self.fvg_confluence_score,
                ICTPatternType.BREAKER_BLOCK: self.ob_confluence_score * 1.2,
                ICTPatternType.MITIGATION_BLOCK: self.ob_confluence_score * 1.1
            }
            
            type_weight = type_weights.get(pattern.pattern_type, 2.0)
            
            # Institutional footprint bonus
            institutional_bonus = pattern.institutional_footprint * self.liquidity_sweep_bonus
            
            # Time validity factor
            time_factor = pattern.time_validity
            
            confluence_score = (base_score * type_weight + institutional_bonus) * time_factor
            
            return min(5.0, confluence_score)
            
        except Exception as e:
            self.logger.error(f"Error calculating pattern confluence score: {e}")
            return 2.0
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get enhanced ICT strategy parameters"""
        return {
            'trading_timeframe': self.trading_timeframe,
            'entry_timeframe': self.entry_timeframe,
            'htf_timeframes': self.htf_timeframes,
            'swing_length': self.swing_length,
            'min_displacement_pips': self.min_displacement_pips,
            'fvg_min_gap_pips': self.fvg_min_gap_pips,
            'volume_confirmation_threshold': self.volume_confirmation_threshold,
            'entry_model': self.entry_model.value,
            'use_session_filters': self.use_session_filters,
            'kill_zones_only': self.kill_zones_only,
            'use_volume_profile': self.use_volume_profile,
            'use_order_flow_analysis': self.use_order_flow_analysis,
            'use_displacement_analysis': self.use_displacement_analysis,
            'poi_confluence_score': self.poi_confluence_score,
            'mss_confluence_score': self.mss_confluence_score,
            'fvg_confluence_score': self.fvg_confluence_score,
            'ob_confluence_score': self.ob_confluence_score,
            'liquidity_sweep_bonus': self.liquidity_sweep_bonus,
            'pattern_min_strength': self.pattern_min_strength,
            'pattern_timeout_hours': self.pattern_timeout_hours,
            'performance_metrics': self.performance_metrics
        }
    
    def validate_setup(self, setup: TradeSetup) -> bool:
        """Validate ICT trade setup with comprehensive criteria"""
        try:
            # Check confluence score threshold
            if setup.confluence_score < self.poi_confluence_score:
                return False
            
            # Check for proper ICT context
            zone_info = setup.metadata.get('zone_info')
            if not zone_info:
                return False
            
            # Validate institutional footprint
            institutional_footprint = zone_info.get('institutional_footprint', 0.0)
            if institutional_footprint < 0.3:
                return False
            
            # Validate pattern quality
            quality_score = zone_info.get('quality_score', 0.0)
            if quality_score < 0.5:
                return False
            
            # Validate risk-reward ratio
            risk_reward_ratio = zone_info.get('risk_reward_ratio', 0.0)
            if risk_reward_ratio < 1.0:
                return False
            
            # Check daily bias alignment
            if self.current_context and self.current_context.daily_bias != 'neutral':
                if ((setup.direction == 'long' and self.current_context.daily_bias == 'bearish') or
                    (setup.direction == 'short' and self.current_context.daily_bias == 'bullish')):
                    return False
            
            # Session filter validation
            if self.use_session_filters:
                current_session = self._determine_current_session()
                if self.kill_zones_only and current_session == 'asian':
                    return False  # Avoid Asian session if kill zones only
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating ICT setup: {e}")
            return False
    
    def get_strategy_status(self) -> Dict[str, Any]:
        """Get comprehensive ICT strategy status"""
        try:
            # Calculate pattern statistics
            total_patterns = sum(len(patterns) for patterns in self.active_patterns.values())
            mitigated_patterns = sum(
                sum(1 for p in patterns if p.is_mitigated) 
                for patterns in self.active_patterns.values()
            )
            
            # Calculate liquidity statistics
            total_liquidity = sum(len(levels) for levels in self.liquidity_levels.values())
            swept_liquidity = sum(
                sum(1 for l in levels if l.is_swept)
                for levels in self.liquidity_levels.values()
            )
            
            return {
                'strategy_name': 'Enhanced ICT Strategy',
                'enabled': self.enabled,
                'current_state': self.state.value if self.state else 'unknown',
                'trading_timeframe': self.trading_timeframe,
                'entry_timeframe': self.entry_timeframe,
                'htf_timeframes': self.htf_timeframes,
                'entry_model': self.entry_model.value,
                'market_context': {
                    'daily_bias': self.current_context.daily_bias if self.current_context else 'unknown',
                    'session_bias': self.current_context.session_bias if self.current_context else 'unknown',
                    'current_session': self.current_context.current_session if self.current_context else 'unknown',
                    'institutional_activity': self.current_context.institutional_activity if self.current_context else 0.0,
                    'htf_pois_count': len(self.current_context.htf_pois) if self.current_context else 0
                },
                'pattern_statistics': {
                    'total_patterns': total_patterns,
                    'mitigated_patterns': mitigated_patterns,
                    'active_patterns': total_patterns - mitigated_patterns,
                    'pattern_breakdown': {
                        tf: len(patterns) for tf, patterns in self.active_patterns.items()
                    }
                },
                'liquidity_statistics': {
                    'total_levels': total_liquidity,
                    'swept_levels': swept_liquidity,
                    'active_levels': total_liquidity - swept_liquidity
                },
                'performance_metrics': self.performance_metrics.copy()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting ICT strategy status: {e}")
            return {'error': str(e)}
    
    async def shutdown(self) -> None:
        """Shutdown enhanced ICT strategy"""
        try:
            self.logger.info("Shutting down Enhanced ICT Strategy...")
            
            # Shutdown thread executor
            if hasattr(self, 'executor'):
                self.executor.shutdown(wait=True)
            
            # Clear all pattern data
            self.active_patterns.clear()
            self.liquidity_levels.clear()
            self.pending_setups.clear()
            
            # Reset state
            self.transition_state(StrategyState.AWAITING_CONTEXT)
            
            # Final performance report
            self.logger.info(f"Final ICT Performance Metrics: {self.performance_metrics}")
            
            self.logger.info("Enhanced ICT Strategy shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during ICT shutdown: {e}")

    # === HELPER METHODS ===
    def _calculate_momentum(self, prices, period):
        """Calculate momentum over specified period"""
        if len(prices) <= period:
            return 0.0
        return (prices[-1] - prices[-period-1]) / prices[-period-1]
    
    def _calculate_ema(self, prices, period):
        """Calculate Exponential Moving Average"""
        if len(prices) == 0:
            return 0.0
        if len(prices) == 1:
            return prices[0]
        
        multiplier = 2.0 / (period + 1)
        ema = prices[0]
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        return ema
    
    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = np.diff(prices[-period-1:])
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains)
        avg_loss = np.mean(losses)
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_williams_r(self, highs, lows, closes, period=14):
        """Calculate Williams %R"""
        if len(closes) < period:
            return -50.0
        
        highest_high = np.max(highs[-period:])
        lowest_low = np.min(lows[-period:])
        current_close = closes[-1]
        
        if highest_high == lowest_low:
            return -50.0
        
        williams_r = -100 * ((highest_high - current_close) / (highest_high - lowest_low))
        return williams_r
    
    def _calculate_stochastic(self, highs, lows, closes, period=14):
        """Calculate Stochastic %K"""
        if len(closes) < period:
            return 50.0
        
        lowest_low = np.min(lows[-period:])
        highest_high = np.max(highs[-period:])
        current_close = closes[-1]
        
        if highest_high == lowest_low:
            return 50.0
        
        stoch_k = 100 * ((current_close - lowest_low) / (highest_high - lowest_low))
        return stoch_k
    
    def _calculate_atr(self, highs, lows, closes, period=14):
        """Calculate Average True Range"""
        if len(highs) < period + 1:
            return 0.001
        
        true_ranges = []
        for i in range(1, min(period + 1, len(highs))):
            tr1 = highs[-i] - lows[-i]
            tr2 = abs(highs[-i] - closes[-i-1])
            tr3 = abs(lows[-i] - closes[-i-1])
            true_ranges.append(max(tr1, tr2, tr3))
        
        return np.mean(true_ranges) if true_ranges else 0.001
    
    def _create_default_result(self, data, symbol, reason):
        """Create default result for insufficient data"""
        current_price = data['close'].iloc[-1] if not data.empty else 1.0
        return {
            'signal': 'HOLD',
            'confidence': 0.0,
            'direction': 'neutral',
            'price': float(current_price),
            'entry_price': float(current_price),
            'reason': f'{self.__class__.__name__}: {reason}',
            'stop_loss': None,
            'take_profit': None,
            'metadata': {'strategy_type': self.__class__.__name__.lower(), 'data_points': len(data)}
        }
    
    def _create_analysis_result(self, signal_type, confidence, direction, current_price, reasons, metadata):
        """Create comprehensive analysis result"""
        return {
            'signal': signal_type,
            'confidence': confidence,
            'direction': direction,
            'price': current_price,
            'entry_price': current_price,
            'reason': f'{self.__class__.__name__}: {", ".join(reasons)}' if reasons else f'{self.__class__.__name__}: No clear signal',
            'stop_loss': current_price * 0.995 if signal_type == "BUY" else current_price * 1.005 if signal_type == "SELL" else None,
            'take_profit': current_price * 1.015 if signal_type == "BUY" else current_price * 0.985 if signal_type == "SELL" else None,
            'metadata': {**metadata, 'data_points': len(data) if 'data' in locals() else 0}
        }
    
    def _handle_analysis_error(self, error, data, symbol):
        """Handle analysis errors gracefully"""
        current_price = data['close'].iloc[-1] if not data.empty else 1.0
        if hasattr(self, 'logger'):
            self.logger.error(f"Error in {self.__class__.__name__} analysis: {error}")
        return {
            'signal': 'HOLD',
            'confidence': 0.0,
            'direction': 'neutral',
            'price': float(current_price),
            'entry_price': float(current_price),
            'reason': f'{self.__class__.__name__}: Analysis error',
            'stop_loss': None,
            'take_profit': None,
            'metadata': {'strategy_type': self.__class__.__name__.lower(), 'error': str(error)}
        }


    # === MAIN ANALYZE METHOD ===
    def analyze(self, data: pd.DataFrame, symbol: str = None) -> Optional[Dict[str, Any]]:
        """
        ICT/Smart Money Concepts analysis with order blocks and liquidity levels
        """
        try:
            if data is None or data.empty or len(data) < 20:
                return self._create_default_result(data, symbol, "Insufficient data for ICT/SMC analysis")

            current_price = float(data['close'].iloc[-1])
            highs = data.get('high', data['close']).values
            lows = data.get('low', data['close']).values
            closes = data['close'].values
            
            # Order blocks identification (simplified)
            order_block_bullish = None
            order_block_bearish = None
            
            if len(data) >= 10:
                # Look for bullish order block (strong buying after decline)
                for i in range(-10, -2):
                    if (closes[i] < closes[i-1] and closes[i+1] > closes[i] and 
                        closes[i+2] > closes[i+1]):
                        order_block_bullish = lows[i]
                        break
                
                # Look for bearish order block (strong selling after rally)
                for i in range(-10, -2):
                    if (closes[i] > closes[i-1] and closes[i+1] < closes[i] and 
                        closes[i+2] < closes[i+1]):
                        order_block_bearish = highs[i]
                        break
            
            # Liquidity levels (recent highs/lows)
            if len(highs) >= 15:
                liquidity_high = np.max(highs[-15:])
                liquidity_low = np.min(lows[-15:])
            else:
                liquidity_high = current_price * 1.002
                liquidity_low = current_price * 0.998
            
            # Fair Value Gap (FVG) detection
            fvg_bullish = None
            fvg_bearish = None
            
            if len(data) >= 5:
                for i in range(-5, -1):
                    # Bullish FVG: gap between low[i-1] and high[i+1]
                    if (highs[i+1] < lows[i-1] and closes[i] > closes[i-1]):
                        fvg_bullish = (lows[i-1] + highs[i+1]) / 2
                    
                    # Bearish FVG: gap between high[i-1] and low[i+1]
                    if (lows[i+1] > highs[i-1] and closes[i] < closes[i-1]):
                        fvg_bearish = (highs[i-1] + lows[i+1]) / 2
            
            # Momentum and trend
            momentum_5 = self._calculate_momentum(closes, 5)
            
            # Signal generation based on ICT/SMC concepts
            signal_type = "HOLD"
            confidence = 0.0
            direction = "neutral"
            reasons = []
            
            # Bullish order block retest
            if (order_block_bullish and current_price <= order_block_bullish * 1.002 and 
                momentum_5 > 0.001):
                signal_type = "BUY"
                direction = "bullish"
                confidence = 0.8
                reasons.append(f"Bullish order block retest: {order_block_bullish:.5f}")
                reasons.append(f"Momentum confirmation: {momentum_5:.3%}")
                
            # Bearish order block retest
            elif (order_block_bearish and current_price >= order_block_bearish * 0.998 and 
                  momentum_5 < -0.001):
                signal_type = "SELL"
                direction = "bearish"
                confidence = 0.8
                reasons.append(f"Bearish order block retest: {order_block_bearish:.5f}")
                reasons.append(f"Momentum confirmation: {momentum_5:.3%}")
                
            # Liquidity grab and reversal
            elif current_price > liquidity_high and momentum_5 < -0.002:
                signal_type = "SELL"
                direction = "bearish"
                confidence = 0.7
                reasons.append("Liquidity grab above highs with reversal")
                
            elif current_price < liquidity_low and momentum_5 > 0.002:
                signal_type = "BUY"
                direction = "bullish"
                confidence = 0.7
                reasons.append("Liquidity grab below lows with reversal")
                
            # Fair Value Gap fill
            elif fvg_bullish and current_price <= fvg_bullish and momentum_5 > 0.001:
                signal_type = "BUY"
                direction = "bullish"
                confidence = 0.6
                reasons.append("Bullish FVG fill opportunity")
                
            elif fvg_bearish and current_price >= fvg_bearish and momentum_5 < -0.001:
                signal_type = "SELL"
                direction = "bearish"
                confidence = 0.6
                reasons.append("Bearish FVG fill opportunity")
            
            return self._create_analysis_result(
                signal_type, confidence, direction, current_price, reasons,
                {
                    'order_block_bullish': order_block_bullish,
                    'order_block_bearish': order_block_bearish,
                    'liquidity_high': liquidity_high,
                    'liquidity_low': liquidity_low,
                    'fvg_bullish': fvg_bullish,
                    'fvg_bearish': fvg_bearish,
                    'momentum_5': momentum_5,
                    'strategy_type': 'ict_smc'
                }
            )
            
        except Exception as e:
            return self._handle_analysis_error(e, data, symbol)

