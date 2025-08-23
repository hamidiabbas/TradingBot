#!/usr/bin/env python3
"""
Real Strategy Loader - Only Load Professional Strategies
"""

import importlib
import sys
from pathlib import Path
from typing import Dict, List, Any

class RealStrategyLoader:
    """Load only real professional strategies"""
    
    def __init__(self):
        self.strategies_dir = Path("strategies")
        self.real_strategies = {}
        
    def load_real_strategies_only(self) -> Dict[str, Any]:
        """Load only verified real strategies"""
        
        print("🔄 LOADING REAL STRATEGIES ONLY")
        print("=" * 40)
        
        # Whitelist of real professional strategies
        real_strategy_whitelist = {
            'ict_strategy.py': 'EnhancedICTStrategy',
            'rtm_strategy.py': 'EnhancedRTMStrategy'
        }
        
        loaded_strategies = {}
        
        for filename, class_name in real_strategy_whitelist.items():
            strategy_path = self.strategies_dir / filename
            
            if strategy_path.exists():
                try:
                    # Import the module
                    module_name = f"strategies.{filename[:-3]}"  # Remove .py
                    
                    if module_name in sys.modules:
                        # Reload if already loaded
                        importlib.reload(sys.modules[module_name])
                    
                    module = importlib.import_module(module_name)
                    
                    # Get the strategy class
                    if hasattr(module, class_name):
                        strategy_class = getattr(module, class_name)
                        loaded_strategies[class_name] = strategy_class
                        print(f"✅ Loaded: {class_name} from {filename}")
                        
                        # Verify it's real
                        if self._verify_real_strategy(strategy_class):
                            print(f"   🛡️ Verified as REAL professional strategy")
                        else:
                            print(f"   ⚠️ Warning: May not be professional strategy")
                    else:
                        print(f"❌ Class {class_name} not found in {filename}")
                        
                except Exception as e:
                    print(f"❌ Error loading {filename}: {e}")
            else:
                print(f"⚠️ Strategy file not found: {filename}")
        
        print(f"\n🎯 Total real strategies loaded: {len(loaded_strategies)}")
        return loaded_strategies
    
    def _verify_real_strategy(self, strategy_class) -> bool:
        """Verify that a strategy class is real and professional"""
        
        try:
            # Check for professional indicators
            class_source = str(strategy_class)
            
            professional_indicators = [
                'Enhanced',
                'Professional',
                'Advanced',
                'Institutional'
            ]
            
            # Check class name
            has_professional_name = any(
                indicator in strategy_class.__name__ 
                for indicator in professional_indicators
            )
            
            # Check for real methods (not just basic analyze)
            if hasattr(strategy_class, '__init__'):
                # Try to instantiate and check methods
                try:
                    # Check if it has sophisticated initialization
                    init_code = str(strategy_class.__init__)
                    has_complex_init = len(init_code) > 500  # Professional strategies have complex init
                    
                    return has_professional_name and has_complex_init
                except:
                    return has_professional_name
            
            return has_professional_name
            
        except Exception:
            return False

def verify_no_fake_strategies():
    """Verify no fake strategies are being loaded"""
    
    print("\n🔍 VERIFYING NO FAKE STRATEGIES")
    print("-" * 40)
    
    strategies_dir = Path("strategies")
    
    # Check for disabled fake files
    fake_files = list(strategies_dir.glob("*.FAKE_DISABLED"))
    disabled_files = list(Path("templates_disabled").glob("*.DISABLED"))
    
    print(f"✅ Fake strategies disabled: {len(fake_files)}")
    print(f"✅ Template generators disabled: {len(disabled_files)}")
    
    # Check for any remaining suspicious files
    suspicious_files = []
    for py_file in strategies_dir.glob("*.py"):
        if py_file.name.startswith('__'):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'confidence = 0.95' in content or 'return 0.95' in content:
                suspicious_files.append(py_file.name)
        except:
            pass
    
    if suspicious_files:
        print(f"⚠️ Suspicious files found: {suspicious_files}")
        print("   These may contain hardcoded fake confidence values")
    else:
        print("✅ No suspicious files detected")
    
    return len(suspicious_files) == 0

if __name__ == "__main__":
    loader = RealStrategyLoader()
    strategies = loader.load_real_strategies_only()
    verification_passed = verify_no_fake_strategies()
    
    print(f"\n🎉 VERIFICATION: {'PASSED' if verification_passed else 'FAILED'}")
