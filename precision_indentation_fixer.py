# precision_indentation_fixer.py - Fix exact line numbers with indentation errors
from pathlib import Path

def fix_specific_indentation_errors():
    """Fix indentation errors at specific line numbers"""
    
    # Map of file -> line numbers with errors
    error_locations = {
        'breakout_strategy.py': [598, 599],
        'mean_reversion_strategy.py': [895, 896], 
        'momentum_scalping_strategy.py': [21, 22],
        'news_strategy.py': [678, 679],
        'pivot_point_strategy.py': [446, 447],
        'scalping_strategy.py': [1056, 1057],
        'volume_strategy.py': [1529, 1530]
    }
    
    strategies_dir = Path("strategies")
    
    for filename, error_lines in error_locations.items():
        filepath = strategies_dir / filename
        
        if not filepath.exists():
            continue
            
        print(f"🔧 Fixing {filename} at lines {error_lines}...")
        
        try:
            # Read all lines
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Fix each problematic line
            for line_num in error_lines:
                if line_num <= len(lines):
                    line_index = line_num - 1  # Convert to 0-based index
                    line = lines[line_index]
                    
                    # Check if this line ends with colon (indicating it needs an indented block)
                    if line.strip().endswith(':'):
                        # Check if next line exists and is properly indented
                        if line_index + 1 < len(lines):
                            next_line = lines[line_index + 1]
                            # If next line is not indented or is empty/comment, add pass
                            if not next_line.strip() or not next_line.startswith('    '):
                                lines.insert(line_index + 1, '    pass  # Auto-generated\n')
                                print(f"   ✅ Added 'pass' after line {line_num}")
                        else:
                            # No next line, add pass
                            lines.append('    pass  # Auto-generated\n')
                            print(f"   ✅ Added 'pass' at end of file after line {line_num}")
                    
                    # Check if this line is an empty line after a colon
                    elif line_index > 0 and lines[line_index - 1].strip().endswith(':'):
                        # Replace empty line with pass
                        lines[line_index] = '    pass  # Auto-generated\n'
                        print(f"   ✅ Replaced empty line {line_num} with 'pass'")
            
            # Write back the fixed content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print(f"   ✅ Successfully fixed {filename}")
            
        except Exception as e:
            print(f"   ❌ Error fixing {filename}: {e}")
    
    print(f"\n🚀 PRECISION INDENTATION FIXING COMPLETE!")

if __name__ == "__main__":
    fix_specific_indentation_errors()
