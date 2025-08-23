#!/usr/bin/env python3
"""
Fix Indentation Issues in Strategy Files
Fixes the specific indentation error at line 16
"""

from pathlib import Path
import re

def fix_strategy_file_indentation(file_path):
    """Fix indentation issues in a specific strategy file"""
    
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if len(lines) < 16:
            print(f"   ⚠️ File has less than 16 lines: {len(lines)}")
            return False
        
        print(f"   📄 Original line 16: '{lines[15].rstrip()}'")
        
        # Common fixes for line 16 issues
        fixed_lines = []
        
        for i, line in enumerate(lines):
            line_num = i + 1
            
            # Special handling for problematic lines around line 16
            if line_num == 16:
                # Remove problematic indentation
                stripped = line.lstrip()
                
                # Check if it's a class definition, function definition, or other construct
                if stripped.startswith('class '):
                    # Class should have no indentation
                    fixed_line = stripped
                elif stripped.startswith('def '):
                    # Method should have 4 spaces if inside class, 0 if top-level
                    # Check if we're inside a class by looking at previous lines
                    in_class = any('class ' in lines[j] for j in range(max(0, i-10), i))
                    if in_class:
                        fixed_line = '    ' + stripped
                    else:
                        fixed_line = stripped
                elif stripped.startswith('"""') or stripped.startswith("'''"):
                    # Docstring should match the function/class indentation
                    in_class = any('class ' in lines[j] for j in range(max(0, i-10), i))
                    in_function = any('def ' in lines[j] for j in range(max(0, i-5), i))
                    
                    if in_function and in_class:
                        fixed_line = '        ' + stripped  # 8 spaces for method docstring
                    elif in_function or in_class:
                        fixed_line = '    ' + stripped      # 4 spaces for class/function docstring
                    else:
                        fixed_line = stripped               # No indentation for module docstring
                elif stripped.startswith('import ') or stripped.startswith('from '):
                    # Imports should have no indentation
                    fixed_line = stripped
                elif stripped == '' or stripped.isspace():
                    # Empty lines
                    fixed_line = '\n'
                else:
                    # Other lines - try to guess proper indentation
                    in_class = any('class ' in lines[j] for j in range(max(0, i-10), i))
                    in_function = any('def ' in lines[j] for j in range(max(0, i-5), i))
                    
                    if in_function and in_class:
                        fixed_line = '        ' + stripped  # 8 spaces for method content
                    elif in_function or in_class:
                        fixed_line = '    ' + stripped      # 4 spaces for class/function content
                    else:
                        fixed_line = stripped               # No indentation for module level
                
                print(f"   ✏️ Fixed line 16: '{fixed_line.rstrip()}'")
                fixed_lines.append(fixed_line if fixed_line.endswith('\n') else fixed_line + '\n')
            else:
                fixed_lines.append(line)
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)
        
        print(f"   ✅ Successfully fixed {file_path.name}")
        return True
        
    except Exception as e:
        print(f"   ❌ Error fixing {file_path.name}: {e}")
        return False

def main():
    """Fix all strategy files with indentation errors"""
    
    # List of files with indentation errors from the debug output
    problematic_files = [
        "base_strategy.py",
        "compatibility.py", 
        "ict_strategy.py",
        "indicator_suite_strategy.py",
        "news_strategy.py",
        "pivot_point_strategy.py",
        "rtm_strategy.py", 
        "scalping_strategy.py",
        "smc_indicators.py",
        "technical_indicators.py",
        "volume_strategy.py"
    ]
    
    strategies_dir = Path("strategies")
    
    print("🔧 FIXING STRATEGY INDENTATION ISSUES")
    print("=" * 60)
    
    fixed_count = 0
    
    for filename in problematic_files:
        file_path = strategies_dir / filename
        
        if not file_path.exists():
            print(f"❌ File not found: {filename}")
            continue
        
        print(f"\n📄 Fixing: {filename}")
        
        if fix_strategy_file_indentation(file_path):
            fixed_count += 1
    
    print(f"\n📊 INDENTATION FIX SUMMARY:")
    print(f"   Files processed: {len(problematic_files)}")
    print(f"   Files fixed: {fixed_count}")
    print(f"   Success rate: {fixed_count/len(problematic_files)*100:.1f}%")

if __name__ == "__main__":
    main()
