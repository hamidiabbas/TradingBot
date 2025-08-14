#!/usr/bin/env python3
"""
TARGETED MULTI-TIMEFRAME FIX FOR YOUR STRATEGY FILES
==============================================================================
This script specifically targets your .\strategies\ folder structure
and adds proper analyze_multi_timeframe methods to each strategy file.
==============================================================================
"""

import os
import re
import shutil
from datetime import datetime
from typing import Dict, List, Any

class TargetedStrategyFixer:
    """Targeted strategy fixer for the discovered file structure"""
    
    def __init__(self):
        self.strategies_dir = ".\\strategies"
        self.target_files = {
            'ict_strategy.py': 'EnhancedICTStrategy',
            'rtm_strategy.py': 'EnhancedRTMStrategy',
            'smc_strategy.py': 'EnhancedSMCStrategy',
            'scalping_strategy.py': 'EnhancedScalpingStrategy',
            'news_strategy.py': 'EnhancedNewsStrategy',
            'pivot_point_strategy.py': 'EnhancedPivotPointStrategy'
        }
        
    def create_backup(self, file_path: str) -> bool:
        """Create backup of strategy file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{file_path}.mtf_backup_{timestamp}"
            shutil.copy2(file_path, backup_path)
            print(f"   ✅ Backup created: {backup_path}")
            return True
        except Exception as e:
            print(f"   ❌ Backup failed: {e}")
            return False
    
    def get_mtf_method_for_strategy(self, strategy_name: str) -> str:
        """Get appropriate MTF method based on strategy type"""
        
        if "ICT" in strategy_name.upper():
            return '''
    def analyze_multi_timeframe(self, mtf_data: Dict[str, pd.DataFrame], symbol: str) -> Dict[str, Any]:
        """ICT Multi-timeframe analysis with complete methodology"""
        
        if not self.validate_mtf_data(mtf_data):
            return self.analyze(mtf_data.get('H1', list(mtf_data.values())[0]), symbol)
        
        try:
            # D1: Major trend and institutional bias
            daily_bias = 'NEUTRAL'
            daily_levels = []
            if 'D1' in mtf_data:
                daily_bias = self._get_trend_direction(mtf_data['D1'])
                daily_levels = self._get_key_levels(mtf_data['D1'])
            
            # H4: Intermediate bias and market structure
            h4_bias = 'NEUTRAL'
            h4_structure = {}
            if 'H4' in mtf_data:
                h4_bias = self._get_trend_direction(mtf_data['H4'])
                h4_structure = self._analyze_market_structure(mtf_data['H4'])
            
            # H1: Order blocks and liquidity zones
            h1_patterns = {}
            if 'H1' in mtf_data:
                h1_patterns = self._detect_ict_patterns(mtf_data['H1'])
            
            # M15: Precision entry timing
            primary_tf = 'M15' if 'M15' in mtf_data else 'H1'
            entry_signal = self.analyze(mtf_data[primary_tf], symbol)
            
            # ICT Confluence calculation
            confluence_score = 0.0
            
            # Trend alignment across timeframes
            if daily_bias == h4_bias and daily_bias != 'NEUTRAL':
                confluence_score += 0.3
            
            # Order block proximity
            current_price = entry_signal.get('entry_price', mtf_data[primary_tf]['close'].iloc[-1])
            if h1_patterns.get('order_blocks'):
                for ob in h1_patterns['order_blocks'][:3]:
                    if abs(current_price - ob) / current_price < 0.001:  # Within 10 pips
                        confluence_score += 0.2
                        break
            
            # Liquidity sweep confirmation
            if h1_patterns.get('liquidity_swept'):
                confluence_score += 0.15
            
            # Session timing (ICT Kill Zones)
            if 'H1' in mtf_data:
                current_hour = mtf_data['H1'].index[-1].hour
                if 8 <= current_hour <= 11 or 13 <= current_hour <= 16:  # London/NY sessions
                    confluence_score += 0.1
            
            # Final ICT signal with confluence
            base_confidence = entry_signal.get('confidence', 0.5)
            ict_confidence = min(1.0, base_confidence + confluence_score)
            
            # ICT requires strong confluence (higher threshold)
            if ict_confidence < 0.65:
                return {
                    'signal': 'HOLD',
                    'confidence': ict_confidence,
                    'reason': 'Insufficient ICT confluence for entry',
                    'analysis': {
                        'methodology': 'ICT_Multi_Timeframe',
                        'daily_bias': daily_bias,
                        'h4_bias': h4_bias,
                        'confluence_score': confluence_score,
                        'timeframes_analyzed': list(mtf_data.keys())
                    }
                }
            
            # Enhance signal with ICT methodology
            entry_signal['confidence'] = ict_confidence
            entry_signal['reason'] = f"ICT MTF Analysis: D1={daily_bias}, H4={h4_bias}, Confluence={confluence_score:.2f}"
            entry_signal['analysis'] = {
                'methodology': 'ICT_Multi_Timeframe',
                'daily_bias': daily_bias,
                'h4_bias': h4_bias,
                'order_blocks_detected': len(h1_patterns.get('order_blocks', [])),
                'confluence_score': confluence_score,
                'timeframes_used': list(mtf_data.keys())
            }
            
            return entry_signal
            
        except Exception as e:
            return self.analyze(mtf_data.get('H1', list(mtf_data.values())[0]), symbol)
'''
        
        elif "RTM" in strategy_name.upper():
            return '''
    def analyze_multi_timeframe(self, mtf_data: Dict[str, pd.DataFrame], symbol: str) -> Dict[str, Any]:
        """RTM Multi-timeframe analysis with zone methodology"""
        
        if not self.validate_mtf_data(mtf_data):
            return self.analyze(mtf_data.get('H1', list(mtf_data.values())[0]), symbol)
        
        try:
            # D1: Major support/resistance zones
            daily_zones = []
            if 'D1' in mtf_data:
                daily_zones = self._get_key_levels(mtf_data['D1'])
            
            # H4: Intermediate zones and trend direction
            h4_zones = []
            h4_trend = 'NEUTRAL'
            if 'H4' in mtf_data:
                h4_zones = self._get_key_levels(mtf_data['H4'])
                h4_trend = self._get_trend_direction(mtf_data['H4'])
            
            # H1: Entry validation with zone confluence
            primary_tf = 'H1' if 'H1' in mtf_data else list(mtf_data.keys())[0]
            entry_signal = self.analyze(mtf_data[primary_tf], symbol)
            
            # RTM Zone confluence analysis
            current_price = entry_signal.get('entry_price', mtf_data[primary_tf]['close'].iloc[-1])
            zone_confluence = 0.0
            
            # Daily zone proximity (20 pips tolerance)
            for zone in daily_zones[:5]:
                if abs(current_price - zone) / current_price < 0.002:
                    zone_confluence += 0.25
                    break
            
            # H4 zone proximity (10 pips tolerance)
            for zone in h4_zones[:3]:
                if abs(current_price - zone) / current_price < 0.001:
                    zone_confluence += 0.2
                    break
            
            # Trend alignment with signal
            signal_direction = entry_signal.get('signal', 'HOLD')
            trend_alignment = 0.0
            if signal_direction != 'HOLD':
                signal_trend = 'BULLISH' if signal_direction == 'BUY' else 'BEARISH'
                if signal_trend == h4_trend:
                    trend_alignment = 0.2
            
            # Zone strength analysis
            zone_strength = min(0.15, len(daily_zones) * 0.03 + len(h4_zones) * 0.02)
            
            # Calculate RTM confidence
            base_confidence = entry_signal.get('confidence', 0.5)
            rtm_confidence = min(1.0, base_confidence + zone_confluence + trend_alignment + zone_strength)
            
            # RTM threshold for zone-based entries
            if rtm_confidence < 0.6:
                return {
                    'signal': 'HOLD',
                    'confidence': rtm_confidence,
                    'reason': 'Insufficient RTM zone confluence',
                    'analysis': {
                        'methodology': 'RTM_Multi_Timeframe', 
                        'h4_trend': h4_trend,
                        'zone_confluence': zone_confluence,
                        'trend_alignment': trend_alignment,
                        'daily_zones': len(daily_zones),
                        'h4_zones': len(h4_zones)
                    }
                }
            
            # Enhance signal with RTM analysis
            entry_signal['confidence'] = rtm_confidence
            entry_signal['reason'] = f"RTM MTF: Trend={h4_trend}, Zones={zone_confluence:.2f}, Alignment={trend_alignment:.2f}"
            entry_signal['analysis'] = {
                'methodology': 'RTM_Multi_Timeframe',
                'h4_trend': h4_trend,
                'zone_confluence': zone_confluence,
                'trend_alignment': trend_alignment,
                'zone_strength': zone_strength,
                'timeframes_used': list(mtf_data.keys())
            }
            
            return entry_signal
            
        except Exception as e:
            return self.analyze(mtf_data.get('H1', list(mtf_data.values())[0]), symbol)
'''
        
        elif "SMC" in strategy_name.upper():
            return '''
    def analyze_multi_timeframe(self, mtf_data: Dict[str, pd.DataFrame], symbol: str) -> Dict[str, Any]:
        """SMC Multi-timeframe analysis with smart money concepts"""
        
        if not self.validate_mtf_data(mtf_data):
            return self.analyze(mtf_data.get('H1', list(mtf_data.values())[0]), symbol)
        
        try:
            # H4: Market structure and order blocks
            h4_structure = {}
            if 'H4' in mtf_data:
                h4_structure = self._analyze_smc_structure(mtf_data['H4'])
            
            # H1: Liquidity zones and market microstructure
            h1_liquidity = {}
            if 'H1' in mtf_data:
                h1_liquidity = self._analyze_liquidity_zones(mtf_data['H1'])
            
            # M15: Precise entry with microstructure
            primary_tf = 'M15' if 'M15' in mtf_data else 'H1'
            entry_signal = self.analyze(mtf_data[primary_tf], symbol)
            
            # SMC Confluence calculation
            structure_confluence = 0.0
            current_price = entry_signal.get('entry_price', mtf_data[primary_tf]['close'].iloc[-1])
            
            # Order block confluence
            if h4_structure.get('order_blocks'):
                for ob in h4_structure['order_blocks'][:3]:
                    if abs(current_price - ob) / current_price < 0.001:
                        structure_confluence += 0.25
                        break
            
            # Liquidity zone confluence
            if h1_liquidity.get('zones'):
                for zone in h1_liquidity['zones'][:3]:
                    if abs(current_price - zone) / current_price < 0.0005:
                        structure_confluence += 0.2
                        break
            
            # Market structure shift confirmation
            if h4_structure.get('mss_detected'):
                structure_confluence += 0.15
            
            # Fair value gap interaction
            if h1_liquidity.get('in_fvg'):
                structure_confluence += 0.1
            
            # Calculate SMC confidence
            base_confidence = entry_signal.get('confidence', 0.5)
            smc_confidence = min(1.0, base_confidence + structure_confluence)
            
            # SMC threshold
            if smc_confidence < 0.6:
                return {
                    'signal': 'HOLD',
                    'confidence': smc_confidence,
                    'reason': 'Insufficient SMC structure confluence',
                    'analysis': {
                        'methodology': 'SMC_Multi_Timeframe',
                        'structure_confluence': structure_confluence,
                        'order_blocks': len(h4_structure.get('order_blocks', [])),
                        'liquidity_zones': len(h1_liquidity.get('zones', []))
                    }
                }
            
            # Enhance signal with SMC analysis
            entry_signal['confidence'] = smc_confidence
            entry_signal['reason'] = f"SMC MTF: Structure={structure_confluence:.2f}"
            entry_signal['analysis'] = {
                'methodology': 'SMC_Multi_Timeframe',
                'structure_confluence': structure_confluence,
                'timeframes_used': list(mtf_data.keys())
            }
            
            return entry_signal
            
        except Exception as e:
            return self.analyze(mtf_data.get('H1', list(mtf_data.values())[0]), symbol)
'''
        
        else:
            # Generic MTF method for other strategies
            return '''
    def analyze_multi_timeframe(self, mtf_data: Dict[str, pd.DataFrame], symbol: str) -> Dict[str, Any]:
        """Generic multi-timeframe analysis with trend confluence"""
        
        # Use best available timeframe for main analysis
        primary_tf = 'H1' if 'H1' in mtf_data else list(mtf_data.keys())[0]
        primary_signal = self.analyze(mtf_data[primary_tf], symbol)
        
        if len(mtf_data) <= 1:
            return primary_signal
        
        try:
            # Multi-timeframe trend analysis
            trends = {}
            for tf, data in mtf_data.items():
                trends[tf] = self._get_trend_direction(data)
            
            # Calculate trend confluence
            confluence_score = self._calculate_confluence_score(mtf_data)
            
            # Enhance signal with multi-timeframe analysis
            if primary_signal.get('signal') not in ['BUY', 'SELL']:
                return primary_signal
            
            base_confidence = primary_signal.get('confidence', 0.5)
            mtf_confidence = min(1.0, base_confidence + (confluence_score * 0.3))
            
            primary_signal['confidence'] = mtf_confidence
            primary_signal['reason'] = f"Multi-timeframe analysis: confluence={confluence_score:.2f}"
            primary_signal['analysis'] = {
                'methodology': 'Generic_Multi_Timeframe',
                'trends': trends,
                'confluence_score': confluence_score,
                'timeframes_used': list(mtf_data.keys())
            }
            
            return primary_signal
            
        except Exception as e:
            return primary_signal
'''
    
    def get_helper_methods(self) -> str:
        """Get helper methods for MTF analysis"""
        return '''
    
    def validate_mtf_data(self, mtf_data: Dict[str, pd.DataFrame]) -> bool:
        """Validate multi-timeframe data availability"""
        if not mtf_data:
            return False
        
        # Check if we have at least one valid timeframe with sufficient data
        valid_tfs = 0
        for tf, data in mtf_data.items():
            if not data.empty and len(data) >= 20:
                valid_tfs += 1
        
        return valid_tfs >= 1
    
    def _get_trend_direction(self, data: pd.DataFrame) -> str:
        """Get trend direction for timeframe"""
        try:
            data = data.copy()
            data['ema_20'] = data['close'].ewm(span=20).mean()
            data['ema_50'] = data['close'].ewm(span=50).mean()
            
            current_price = data['close'].iloc[-1]
            ema_20 = data['ema_20'].iloc[-1]
            ema_50 = data['ema_50'].iloc[-1]
            
            if current_price > ema_20 > ema_50:
                return 'BULLISH'
            elif current_price < ema_20 < ema_50:
                return 'BEARISH'
            else:
                return 'NEUTRAL'
        except:
            return 'NEUTRAL'
    
    def _get_key_levels(self, data: pd.DataFrame) -> List[float]:
        """Get key support/resistance levels"""
        try:
            levels = []
            # Simple pivot points
            data['pivot_high'] = data['high'].rolling(5, center=True).max()
            data['pivot_low'] = data['low'].rolling(5, center=True).min()
            
            # Recent highs and lows
            recent_highs = data['pivot_high'].dropna().tail(5)
            recent_lows = data['pivot_low'].dropna().tail(5)
            
            levels.extend(recent_highs.tolist())
            levels.extend(recent_lows.tolist())
            
            return sorted(set(levels))  # Remove duplicates and sort
        except:
            return []
    
    def _analyze_market_structure(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze market structure"""
        try:
            structure = {
                'trend': self._get_trend_direction(data),
                'strength': 0.5,
                'bos_detected': False,
                'choch_detected': False
            }
            
            # Simple structure analysis
            data['high_break'] = data['high'] > data['high'].shift(1)
            data['low_break'] = data['low'] < data['low'].shift(1)
            
            recent_breaks = data[['high_break', 'low_break']].tail(10)
            if recent_breaks['high_break'].sum() > recent_breaks['low_break'].sum():
                structure['strength'] = 0.7
                structure['bos_detected'] = True
            elif recent_breaks['low_break'].sum() > recent_breaks['high_break'].sum():
                structure['strength'] = 0.3
                structure['bos_detected'] = True
            
            return structure
        except:
            return {'trend': 'NEUTRAL', 'strength': 0.5, 'bos_detected': False, 'choch_detected': False}
    
    def _detect_ict_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Detect ICT patterns"""
        try:
            patterns = {
                'order_blocks': [],
                'fair_value_gaps': [],
                'liquidity_swept': False
            }
            
            # Simple order block detection
            if 'tick_volume' in data.columns:
                data['volume_avg'] = data['tick_volume'].rolling(10).mean()
                
                for i in range(10, len(data)-1):
                    if data['tick_volume'].iloc[i] > data['volume_avg'].iloc[i] * 1.5:
                        if data['close'].iloc[i] > data['open'].iloc[i]:  # Bullish
                            patterns['order_blocks'].append(data['low'].iloc[i])
                        else:  # Bearish
                            patterns['order_blocks'].append(data['high'].iloc[i])
            
            # Simple FVG detection
            for i in range(2, len(data)):
                # Check for gaps
                if data['low'].iloc[i] > data['high'].iloc[i-2]:  # Bullish FVG
                    patterns['fair_value_gaps'].append({
                        'type': 'bullish',
                        'upper': data['low'].iloc[i],
                        'lower': data['high'].iloc[i-2]
                    })
                elif data['high'].iloc[i] < data['low'].iloc[i-2]:  # Bearish FVG
                    patterns['fair_value_gaps'].append({
                        'type': 'bearish',
                        'upper': data['low'].iloc[i-2],
                        'lower': data['high'].iloc[i]
                    })
            
            return patterns
        except:
            return {'order_blocks': [], 'fair_value_gaps': [], 'liquidity_swept': False}
    
    def _analyze_smc_structure(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze SMC structure"""
        try:
            structure = {
                'order_blocks': [],
                'mss_detected': False,
                'structure_shift': 'none'
            }
            
            # Order block detection with volume
            if 'tick_volume' in data.columns:
                data['volume_avg'] = data['tick_volume'].rolling(15).mean()
                
                for i in range(15, len(data)-5):
                    if data['tick_volume'].iloc[i] > data['volume_avg'].iloc[i] * 1.3:
                        structure['order_blocks'].append(data['high'].iloc[i] if data['close'].iloc[i] < data['open'].iloc[i] else data['low'].iloc[i])
            
            # Simple MSS detection
            highs = data['high'].rolling(10).max()
            lows = data['low'].rolling(10).min()
            
            if len(highs) > 20 and len(lows) > 20:
                recent_high = highs.iloc[-10:]
                recent_low = lows.iloc[-10:]
                
                if recent_high.iloc[-1] > recent_high.iloc[-5] and recent_low.iloc[-1] > recent_low.iloc[-5]:
                    structure['mss_detected'] = True
                    structure['structure_shift'] = 'bullish'
                elif recent_high.iloc[-1] < recent_high.iloc[-5] and recent_low.iloc[-1] < recent_low.iloc[-5]:
                    structure['mss_detected'] = True
                    structure['structure_shift'] = 'bearish'
            
            return structure
        except:
            return {'order_blocks': [], 'mss_detected': False, 'structure_shift': 'none'}
    
    def _analyze_liquidity_zones(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze liquidity zones"""
        try:
            liquidity = {
                'zones': [],
                'equal_highs': [],
                'equal_lows': [],
                'in_fvg': False
            }
            
            # Equal highs/lows detection
            for i in range(5, len(data)-5):
                # Equal highs (within 5 pips)
                if abs(data['high'].iloc[i] - data['high'].iloc[i-1]) / data['high'].iloc[i] < 0.0005:
                    if data['high'].iloc[i] > data['high'].iloc[i-2]:
                        liquidity['equal_highs'].append(data['high'].iloc[i])
                        liquidity['zones'].append(data['high'].iloc[i])
                
                # Equal lows (within 5 pips)
                if abs(data['low'].iloc[i] - data['low'].iloc[i-1]) / data['low'].iloc[i] < 0.0005:
                    if data['low'].iloc[i] < data['low'].iloc[i-2]:
                        liquidity['equal_lows'].append(data['low'].iloc[i])
                        liquidity['zones'].append(data['low'].iloc[i])
            
            return liquidity
        except:
            return {'zones': [], 'equal_highs': [], 'equal_lows': [], 'in_fvg': False}
    
    def _calculate_confluence_score(self, mtf_data: Dict[str, pd.DataFrame]) -> float:
        """Calculate multi-timeframe confluence score"""
        try:
            confluence = 0.0
            trends = {}
            
            # Get trend for each timeframe
            for tf, data in mtf_data.items():
                trends[tf] = self._get_trend_direction(data)
            
            # Calculate trend alignment
            if len(trends) > 1:
                trend_values = list(trends.values())
                bullish_count = trend_values.count('BULLISH')
                bearish_count = trend_values.count('BEARISH')
                total_tfs = len(trend_values)
                
                max_alignment = max(bullish_count, bearish_count)
                confluence = max_alignment / total_tfs if total_tfs > 0 else 0
            
            return min(1.0, confluence)
        except:
            return 0.5
'''
    
    def fix_strategy_file(self, filename: str, strategy_class: str) -> bool:
        """Fix individual strategy file"""
        
        file_path = os.path.join(self.strategies_dir, filename)
        
        print(f"\n🔧 Processing: {filename}")
        print(f"   Target class: {strategy_class}")
        
        if not os.path.exists(file_path):
            print(f"   ❌ File not found: {file_path}")
            return False
        
        # Create backup
        if not self.create_backup(file_path):
            return False
        
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if already has analyze_multi_timeframe
            if 'def analyze_multi_timeframe(' in content:
                print(f"   ⚠️ {strategy_class} already has analyze_multi_timeframe method")
                return True
            
            # Add required imports
            if 'from typing import Dict, List, Any' not in content:
                import_section = content.find('import pandas as pd')
                if import_section != -1:
                    content = content[:import_section] + 'from typing import Dict, List, Any\n' + content[import_section:]
            
            # Find the strategy class
            class_pattern = rf'(class\s+{re.escape(strategy_class)}.*?)(?=\nclass|\Z)'
            class_match = re.search(class_pattern, content, re.DOTALL)
            
            if not class_match:
                print(f"   ❌ Class {strategy_class} not found in {filename}")
                return False
            
            class_content = class_match.group(1)
            
            # Find the end of the class (before last method ends)
            method_pattern = r'\n    def\s+\w+\([^)]*\):'
            methods = list(re.finditer(method_pattern, class_content))
            
            if methods:
                # Find the end of the last method
                last_method_start = methods[-1].start()
                remaining_class = class_content[last_method_start:]
                
                # Find where this method ends (next def or class)
                next_def = re.search(r'\n(?:    def|\S)', remaining_class[1:])
                if next_def:
                    insert_pos = last_method_start + next_def.start() + 1
                else:
                    insert_pos = len(class_content)
            else:
                # No methods found, insert after class definition
                class_def_end = class_content.find(':', class_content.find(f'class {strategy_class}')) + 1
                docstring_end = class_content.find('"""', class_def_end)
                if docstring_end != -1:
                    docstring_end = class_content.find('"""', docstring_end + 3) + 3
                    insert_pos = docstring_end
                else:
                    insert_pos = class_def_end
            
            # Get the appropriate MTF method
            mtf_method = self.get_mtf_method_for_strategy(strategy_class)
            helper_methods = self.get_helper_methods()
            
            # Insert the methods
            new_class_content = (class_content[:insert_pos] + 
                               mtf_method + 
                               helper_methods + 
                               class_content[insert_pos:])
            
            # Replace in main content
            new_content = content.replace(class_content, new_class_content)
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"   ✅ Successfully added analyze_multi_timeframe to {strategy_class}")
            return True
            
        except Exception as e:
            print(f"   ❌ Error processing {filename}: {e}")
            return False
    
    def fix_all_strategies(self) -> Dict[str, bool]:
        """Fix all strategy files"""
        
        print("🔧 TARGETED STRATEGY MULTI-TIMEFRAME FIX")
        print("="*60)
        
        results = {}
        
        for filename, strategy_class in self.target_files.items():
            results[strategy_class] = self.fix_strategy_file(filename, strategy_class)
        
        return results

def main():
    """Main execution function"""
    
    fixer = TargetedStrategyFixer()
    results = fixer.fix_all_strategies()
    
    # Print summary
    print("\n" + "="*60)
    print("📋 MULTI-TIMEFRAME FIX SUMMARY")
    print("="*60)
    
    successful = sum(1 for success in results.values() if success)
    total = len(results)
    
    print(f"\n📊 RESULTS:")
    print(f"   Total strategies: {total}")
    print(f"   Successfully fixed: {successful}")
    print(f"   Failed: {total - successful}")
    
    print(f"\n📈 INDIVIDUAL RESULTS:")
    for strategy, success in results.items():
        status = "✅ FIXED" if success else "❌ FAILED"
        print(f"   {status} {strategy}")
    
    if successful == total:
        print(f"\n🎉 ALL STRATEGIES SUCCESSFULLY FIXED!")
        print(f"✅ All multi-timeframe methods have been added")
        print(f"✅ Backups created for all modified files")
        print(f"✅ Ready for strategy testing")
        
        print(f"\n📋 NEXT STEPS:")
        print(f"   1. Run: python quick_strategy_test.py")
        print(f"   2. Verify all strategies pass MTF tests")
        print(f"   3. Proceed with full 10-year backtesting")
    else:
        print(f"\n⚠️ SOME FIXES FAILED")
        print(f"   Check error messages above for details")
        print(f"   Successfully fixed strategies can be used for backtesting")

if __name__ == "__main__":
    main()
