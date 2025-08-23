#!/usr/bin/env python3
"""
Identify and Replace Fake Template Strategies
"""

import os
import ast
from pathlib import Path

class FakeStrategyDetector:
    """Detect which strategies are fake templates vs real implementations"""
    
    def __init__(self):
        self.strategies_dir = Path("strategies")
        self.fake_strategies = []
        self.real_strategies = []
        
    def scan_all_strategies(self):
        """Scan all strategy files and identify fake vs real"""
        
        print("🔍 SCANNING FOR FAKE TEMPLATE STRATEGIES")
        print("=" * 50)
        
        if not self.strategies_dir.exists():
            print("❌ Strategies directory not found!")
            return
        
        strategy_files = list(self.strategies_dir.glob("*.py"))
        
        for file_path in strategy_files:
            if file_path.name == "__init__.py":
                continue
                
            is_fake = self._is_fake_strategy(file_path)
            
            if is_fake:
                self.fake_strategies.append(file_path.name)
                print(f"❌ FAKE TEMPLATE: {file_path.name}")
            else:
                self.real_strategies.append(file_path.name)
                print(f"✅ REAL STRATEGY: {file_path.name}")
        
        print(f"\n📊 SUMMARY:")
        print(f"   Fake Templates: {len(self.fake_strategies)}")
        print(f"   Real Strategies: {len(self.real_strategies)}")
        
        return self.fake_strategies, self.real_strategies
    
    def _is_fake_strategy(self, file_path: Path) -> bool:
        """Check if strategy file contains fake hardcoded values"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for fake indicators
            fake_indicators = [
                "0.950",  # Hardcoded confidence
                "0.937",
                "0.924", 
                "return 0.95",
                "confidence = 0.9",
                "PREMIUM",  # Hardcoded quality
                "# Simple moving average crossover",  # Template comment
                "# Generic strategy template",
                "confidence = 0.65",  # Template default
            ]
            
            fake_count = sum(1 for indicator in fake_indicators if indicator in content)
            
            # Check for lack of real technical analysis
            real_indicators = [
                "df['close'].rolling(",
                ".ewm(",
                "rsi",
                "macd", 
                ".std()",
                "bollinger",
                "atr",
                "pct_change()",
                "correlation"
            ]
            
            real_count = sum(1 for indicator in real_indicators if indicator.lower() in content.lower())
            
            # If more fake indicators than real, it's probably a template
            return fake_count > real_count
            
        except Exception as e:
            print(f"⚠️ Error reading {file_path}: {e}")
            return True  # Assume fake if can't read

def main():
    detector = FakeStrategyDetector()
    fake_strategies, real_strategies = detector.scan_all_strategies()
    
    print(f"\n🎯 FAKE STRATEGIES TO REPLACE:")
    for fake in fake_strategies:
        print(f"   - {fake}")

if __name__ == "__main__":
    main()
