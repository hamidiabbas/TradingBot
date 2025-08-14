#!/usr/bin/env python3
"""
Dynamic Position Sizing Configuration Fix
Enables proper dynamic position sizing based on signal strength
"""

def fix_position_sizing_config():
    """Fix position sizing configuration"""
    
    print("🔧 FIXING DYNAMIC POSITION SIZING CONFIGURATION")
    print("="*60)
    
    # Updated config.yaml content
    dynamic_config = """# Dynamic Position Sizing Configuration - FIXED

position_sizing:
  # ENABLE DYNAMIC SIZING
  method: "kelly"                    # Use Kelly Criterion
  use_dynamic: true                  # Enable dynamic sizing
  use_kelly: true                   # Enable Kelly formula
  
  # KELLY PARAMETERS (CRITICAL)
  base_risk_percentage: 2.0         # Base risk per trade (2%)
  confidence_multiplier: 1.5        # Multiply by signal confidence
  kelly_multiplier: 0.5             # Kelly fraction multiplier (conservative)
  
  # DYNAMIC RANGE SETTINGS
  min_position_size: 0.01           # Minimum lot size
  max_position_size: 0.10           # Maximum lot size (10x range)
  min_risk_per_trade: 0.5           # 0.5% minimum risk
  max_risk_per_trade: 5.0           # 5.0% maximum risk
  
  # CONFIDENCE-BASED SCALING
  confidence_scaling:
    enable: true                    # Enable confidence scaling
    low_confidence_threshold: 0.6   # Below this = minimum sizing
    high_confidence_threshold: 0.9  # Above this = maximum sizing
    scaling_factor: 2.0             # 2x difference between min/max
  
  # VOLATILITY ADJUSTMENTS  
  volatility_adjustment:
    enable: true                    # Adjust for market volatility
    atr_period: 14                 # ATR calculation period
    volatility_multiplier: 0.8     # Reduce size in high volatility
    
  # ACCOUNT PROTECTION
  max_total_exposure: 0.20          # 20% maximum total exposure
  max_positions: 5                  # Maximum concurrent positions
  
  # DISABLE STATIC SIZING
  fixed_size: null                  # Disable fixed sizing
  use_fixed: false                 # Ensure fixed sizing is off

# Enhanced Kelly Position Sizing Parameters
kelly_parameters:
  # HISTORICAL PERFORMANCE DATA (Update these regularly)
  win_rate: 0.55                   # 55% win rate (update from backtest)
  average_win: 0.025              # 2.5% average win
  average_loss: 0.015             # 1.5% average loss
  
  # RISK ADJUSTMENT
  risk_adjustment_factor: 0.7      # Conservative adjustment
  max_kelly_fraction: 0.25         # Cap Kelly at 25%
  
  # CONFIDENCE INTEGRATION
  confidence_weight: 0.6          # Weight of signal confidence
  base_allocation: 0.4           # Base allocation regardless of confidence

# Signal Processing for Position Sizing
signal_processing:
  confidence_smoothing: true       # Smooth confidence values
  outlier_filtering: true         # Filter extreme values
  rolling_average_period: 3       # Rolling average for stability
"""
    
    try:
        # Backup existing config
        import shutil
        from datetime import datetime
        
        if os.path.exists("config.yaml"):
            backup_name = f"config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
            shutil.copy2("config.yaml", backup_name)
            print(f"✅ Configuration backed up as: {backup_name}")
        
        # Write new dynamic configuration
        with open("config.yaml", 'w', encoding='utf-8') as f:
            f.write(dynamic_config)
        
        print("✅ Dynamic position sizing configuration updated")
        return True
        
    except Exception as e:
        print(f"❌ Configuration update failed: {e}")
        return False

if __name__ == "__main__":
    fix_position_sizing_config()
#!/usr/bin/env python3
"""
Enhanced Dynamic Kelly Position Sizing Implementation
Replaces static sizing with confidence-based dynamic sizing
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
import MetaTrader5 as mt5

class EnhancedKellyPositionSizer:
    """Enhanced Kelly Position Sizer with dynamic confidence scaling"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Kelly parameters from config
        self.win_rate = config.get('win_rate', 0.55)
        self.average_win = config.get('average_win', 0.025)
        self.average_loss = config.get('average_loss', 0.015)
        self.risk_adjustment = config.get('risk_adjustment_factor', 0.7)
        self.max_kelly = config.get('max_kelly_fraction', 0.25)
        
        # Dynamic sizing parameters
        self.base_risk = config.get('base_risk_percentage', 2.0) / 100
        self.confidence_multiplier = config.get('confidence_multiplier', 1.5)
        self.kelly_multiplier = config.get('kelly_multiplier', 0.5)
        
        # Size limits
        self.min_size = config.get('min_position_size', 0.01)
        self.max_size = config.get('max_position_size', 0.10)
        self.min_risk = config.get('min_risk_per_trade', 0.005)  # 0.5%
        self.max_risk = config.get('max_risk_per_trade', 0.05)   # 5.0%
        
        # Confidence scaling
        confidence_config = config.get('confidence_scaling', {})
        self.enable_confidence_scaling = confidence_config.get('enable', True)
        self.low_confidence_threshold = confidence_config.get('low_confidence_threshold', 0.6)
        self.high_confidence_threshold = confidence_config.get('high_confidence_threshold', 0.9)
        self.scaling_factor = confidence_config.get('scaling_factor', 2.0)
        
        print(f"🎯 Enhanced Kelly Position Sizer initialized")
        print(f"   Base Risk: {self.base_risk:.1%}")
        print(f"   Position Range: {self.min_size} - {self.max_size} lots")
        print(f"   Confidence Scaling: {'Enabled' if self.enable_confidence_scaling else 'Disabled'}")
    
    def calculate_position_size(self, signal: Dict[str, Any], account_balance: float) -> float:
        """Calculate dynamic position size using enhanced Kelly criterion"""
        
        try:
            symbol = signal.get('symbol', 'EURUSD')
            confidence = float(signal.get('confidence', 0.5))
            signal_strength = abs(float(signal.get('signal_strength', confidence)))
            
            print(f"\n🎯 CALCULATING DYNAMIC POSITION SIZE:")
            print(f"   Symbol: {symbol}")
            print(f"   Confidence: {confidence:.3f}")
            print(f"   Signal Strength: {signal_strength:.3f}")
            print(f"   Account Balance: ${account_balance:,.2f}")
            
            # Step 1: Calculate base Kelly fraction
            kelly_fraction = self._calculate_kelly_fraction(confidence)
            print(f"   📊 Base Kelly Fraction: {kelly_fraction:.4f}")
            
            # Step 2: Apply confidence scaling
            if self.enable_confidence_scaling:
                confidence_multiplier = self._calculate_confidence_multiplier(confidence)
                kelly_fraction *= confidence_multiplier
                print(f"   📈 Confidence Multiplier: {confidence_multiplier:.3f}")
                print(f"   📊 Adjusted Kelly Fraction: {kelly_fraction:.4f}")
            
            # Step 3: Convert to risk percentage
            risk_percentage = kelly_fraction * self.risk_adjustment
            risk_percentage = max(self.min_risk, min(self.max_risk, risk_percentage))
            print(f"   ⚖️  Risk Percentage: {risk_percentage:.3%}")
            
            # Step 4: Calculate position size based on risk
            risk_amount = account_balance * risk_percentage
            print(f"   💰 Risk Amount: ${risk_amount:.2f}")
            
            # Step 5: Convert to lot size based on symbol specifications
            position_size = self._convert_risk_to_lots(symbol, risk_amount, signal)
            
            # Step 6: Apply size limits
            position_size = max(self.min_size, min(self.max_size, position_size))
            
            print(f"   📏 Final Position Size: {position_size:.4f} lots")
            print(f"   📊 Position Value: ${position_size * 100000:.2f}")
            
            return round(position_size, 4)
            
        except Exception as e:
            print(f"❌ Position sizing error: {e}")
            return self.min_size
    
    def _calculate_kelly_fraction(self, confidence: float) -> float:
        """Calculate Kelly fraction with confidence integration"""
        
        # Base Kelly formula: f = (bp - q) / b
        # where: b = odds, p = win probability, q = lose probability
        
        # Adjust win rate based on confidence
        adjusted_win_rate = self.win_rate * (0.5 + confidence * 0.5)  # Scale with confidence
        adjusted_lose_rate = 1 - adjusted_win_rate
        
        # Calculate Kelly fraction
        if self.average_loss > 0:
            odds_ratio = self.average_win / self.average_loss
            kelly_fraction = (adjusted_win_rate * odds_ratio - adjusted_lose_rate) / odds_ratio
        else:
            kelly_fraction = self.base_risk
        
        # Apply Kelly multiplier (conservative approach)
        kelly_fraction *= self.kelly_multiplier
        
        # Cap at maximum Kelly fraction
        kelly_fraction = max(0.01, min(self.max_kelly, kelly_fraction))
        
        return kelly_fraction
    
    def _calculate_confidence_multiplier(self, confidence: float) -> float:
        """Calculate confidence-based multiplier"""
        
        if confidence <= self.low_confidence_threshold:
            return 1.0  # Minimum multiplier
        elif confidence >= self.high_confidence_threshold:
            return self.scaling_factor  # Maximum multiplier
        else:
            # Linear interpolation between thresholds
            range_size = self.high_confidence_threshold - self.low_confidence_threshold
            confidence_position = (confidence - self.low_confidence_threshold) / range_size
            return 1.0 + (self.scaling_factor - 1.0) * confidence_position
    
    def _convert_risk_to_lots(self, symbol: str, risk_amount: float, signal: Dict[str, Any]) -> float:
        """Convert risk amount to lot size for specific symbol"""
        
        try:
            # Get symbol information
            symbol_info = mt5.symbol_info(symbol)
            if not symbol_info:
                print(f"⚠️ Symbol info unavailable for {symbol}, using default")
                return risk_amount / 100000  # Default calculation
            
            # Get current price
            tick = mt5.symbol_info_tick(symbol)
            if not tick:
                print(f"⚠️ Price unavailable for {symbol}, using signal price")
                current_price = float(signal.get('entry_price', 1.0))
            else:
                current_price = (tick.bid + tick.ask) / 2
            
            # Calculate contract value
            contract_size = symbol_info.trade_contract_size
            pip_value = symbol_info.trade_tick_value
            
            # Estimate stop loss distance (for risk calculation)
            # Use ATR or default to 50 pips
            stop_distance_pips = 50  # Default, should be calculated from signal
            stop_distance_price = stop_distance_pips * symbol_info.point * 10
            
            # Calculate position size
            # Risk Amount = Position Size * Contract Size * Stop Distance
            position_size = risk_amount / (contract_size * stop_distance_price)
            
            # Adjust for symbol specifications
            volume_step = symbol_info.volume_step
            position_size = round(position_size / volume_step) * volume_step
            
            return max(symbol_info.volume_min, min(symbol_info.volume_max, position_size))
            
        except Exception as e:
            print(f"⚠️ Risk-to-lots conversion error: {e}")
            # Fallback calculation
            return risk_amount / 100000

def test_dynamic_position_sizing():
    """Test the dynamic position sizing with various scenarios"""
    
    print("🧪 TESTING DYNAMIC POSITION SIZING")
    print("="*50)
    
    # Test configuration
    config = {
        'win_rate': 0.55,
        'average_win': 0.025,
        'average_loss': 0.015,
        'base_risk_percentage': 2.0,
        'confidence_multiplier': 1.5,
        'kelly_multiplier': 0.5,
        'min_position_size': 0.01,
        'max_position_size': 0.10,
        'confidence_scaling': {
            'enable': True,
            'low_confidence_threshold': 0.6,
            'high_confidence_threshold': 0.9,
            'scaling_factor': 2.0
        }
    }
    
    # Initialize sizer
    sizer = EnhancedKellyPositionSizer(config)
    account_balance = 100000.0  # $100k account
    
    # Test scenarios with different confidence levels
    test_signals = [
        {'symbol': 'EURUSD', 'confidence': 0.5, 'entry_price': 1.1000, 'signal_strength': 0.5},   # Low confidence
        {'symbol': 'EURUSD', 'confidence': 0.7, 'entry_price': 1.1000, 'signal_strength': 0.7},   # Medium confidence
        {'symbol': 'EURUSD', 'confidence': 0.9, 'entry_price': 1.1000, 'signal_strength': 0.9},   # High confidence
        {'symbol': 'GBPUSD', 'confidence': 0.6, 'entry_price': 1.2500, 'signal_strength': 0.6},   # Different symbol
        {'symbol': 'USDJPY', 'confidence': 0.8, 'entry_price': 150.00, 'signal_strength': 0.8},   # JPY pair
    ]
    
    print(f"\nAccount Balance: ${account_balance:,.2f}")
    print(f"\n{'Signal':<15} {'Confidence':<12} {'Position Size':<15} {'Risk Amount':<15} {'Variation'}")
    print("-" * 80)
    
    base_size = None
    for i, signal in enumerate(test_signals):
        position_size = sizer.calculate_position_size(signal, account_balance)
        risk_amount = position_size * 100000 * 0.005  # Rough risk calculation
        
        if base_size is None:
            base_size = position_size
            variation = "Base"
        else:
            variation_pct = ((position_size - base_size) / base_size) * 100
            variation = f"{variation_pct:+.1f}%"
        
        print(f"{signal['symbol']:<15} {signal['confidence']:<12.3f} {position_size:<15.4f} ${risk_amount:<14.2f} {variation}")
    
    print(f"\n✅ Dynamic sizing test completed")
    print(f"📊 Position sizes should vary significantly based on confidence levels")

if __name__ == "__main__":
    # Fix configuration
    fix_position_sizing_config()
    
    # Test dynamic sizing
    if mt5.initialize():
        test_dynamic_position_sizing()
        mt5.shutdown()
    else:
        print("⚠️ MT5 not available - running configuration fix only")
