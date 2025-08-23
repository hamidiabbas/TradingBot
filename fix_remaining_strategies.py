#!/usr/bin/env python3
"""
Quick Indentation Fix for Remaining Strategies
"""

from pathlib import Path
import textwrap

def fix_strategy_indentation(file_path):
    """Fix indentation by re-writing with proper structure"""
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Find the problematic line 16 area
        lines = content.split('\n')
        
        if len(lines) < 16:
            return False
            
        # Simple fix: ensure proper class/function indentation
        fixed_lines = []
        for i, line in enumerate(lines):
            if i == 15:  # Line 16 (0-indexed)
                # Remove any problematic indentation and fix
                stripped = line.strip()
                if stripped.startswith('class ') or stripped.startswith('def ') and not stripped.startswith('    def'):
                    fixed_lines.append(stripped)
                elif stripped.startswith('"""') or stripped.startswith("'''"):
                    # Check context for proper docstring indentation
                    prev_lines = lines[max(0, i-5):i]
                    if any('class ' in prev or 'def ' in prev for prev in prev_lines):
                        fixed_lines.append('    ' + stripped)
                    else:
                        fixed_lines.append(stripped)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        # Write back
        with open(file_path, 'w') as f:
            f.write('\n'.join(fixed_lines))
            
        return True
        
    except Exception as e:
        print(f"❌ Error fixing {file_path.name}: {e}")
        return False

def main():
    """Fix all problematic strategies"""
    
    problematic_files = [
        "base_strategy.py",
        "ict_strategy.py", 
        "indicator_suite_strategy.py",
        "news_strategy.py",
        "rtm_strategy.py",
        "scalping_strategy.py", 
        "smc_indicators.py",
        "technical_indicators.py",
        "volume_strategy.py"
    ]
    
    strategies_dir = Path("strategies")
    fixed_count = 0
    
    print("🔧 FIXING REMAINING INDENTATION ISSUES")
    print("=" * 50)
    
    for filename in problematic_files:
        file_path = strategies_dir / filename
        if file_path.exists():
            print(f"📄 Fixing: {filename}")
            if fix_strategy_indentation(file_path):
                print(f"   ✅ Fixed")
                fixed_count += 1
            else:
                print(f"   ❌ Failed")
    
    print(f"\n📊 Fixed {fixed_count}/{len(problematic_files)} files")

if __name__ == "__main__":
    main()
