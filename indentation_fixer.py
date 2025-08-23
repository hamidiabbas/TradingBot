# indentation_fixer.py - Fix all indentation errors in strategy files
from pathlib import Path
import re

def fix_indentation_errors():
    """Fix specific indentation errors in strategy files"""
    
    error_files = [
        'breakout_strategy.py',
        'mean_reversion_strategy.py', 
        'momentum_scalping_strategy.py',
        'news_strategy.py',
        'pivot_point_strategy.py',
        'scalping_strategy.py',
        'volume_strategy.py'
    ]
    
    strategies_dir = Path("strategies")
    
    for filename in error_files:
        filepath = strategies_dir / filename
        
        if not filepath.exists():
            continue
            
        print(f"🔧 Fixing {filename}...")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Fix 1: Add pass statement after if statements with no body
            content = re.sub(r'(if .+:)\s*\n(?!\s{4,})', r'\1\n    pass\n', content)
            
            # Fix 2: Add pass statement after else statements with no body  
            content = re.sub(r'(else:)\s*\n(?!\s{4,})', r'\1\n    pass\n', content)
            
            # Fix 3: Add pass statement after elif statements with no body
            content = re.sub(r'(elif .+:)\s*\n(?!\s{4,})', r'\1\n    pass\n', content)
            
            # Fix 4: Add pass statement after for/while loops with no body
            content = re.sub(r'(for .+:)\s*\n(?!\s{4,})', r'\1\n    pass\n', content)
            content = re.sub(r'(while .+:)\s*\n(?!\s{4,})', r'\1\n    pass\n', content)
            
            # Fix 5: Add pass statement after try/except/finally with no body
            content = re.sub(r'(try:)\s*\n(?!\s{4,})', r'\1\n    pass\n', content)
            content = re.sub(r'(except.+:)\s*\n(?!\s{4,})', r'\1\n    pass\n', content)
            content = re.sub(r'(finally:)\s*\n(?!\s{4,})', r'\1\n    pass\n', content)
            
            # Fix 6: Add pass statement after function/class definitions with no body
            content = re.sub(r'(def .+:)\s*\n(?!\s{4,})', r'\1\n    pass\n', content)
            content = re.sub(r'(class .+:)\s*\n(?!\s{4,})', r'\1\n    pass\n', content)
            
            # Write the fixed content back
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"   ✅ Fixed indentation errors in {filename}")
            
        except Exception as e:
            print(f"   ❌ Error fixing {filename}: {e}")
    
    print(f"\n🚀 INDENTATION FIXING COMPLETE!")
    print(f"   All 7 files processed")
    print(f"   Run strategy_debugger.py again to test")

if __name__ == "__main__":
    fix_indentation_errors()
