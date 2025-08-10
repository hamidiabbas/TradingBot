"""
Quick Fix for Missing Typing Imports
===================================
Adds missing typing imports to all Python files in the project
"""

import os
import re
from pathlib import Path

def fix_typing_imports(file_path):
    """Add missing typing imports to a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if typing imports are needed
        typing_patterns = [
            r'\bDict\[',
            r'\bAny\b',
            r'\bOptional\[',
            r'\bList\[',
            r'\bTuple\[',
            r'\bUnion\['
        ]
        
        needs_typing = any(re.search(pattern, content) for pattern in typing_patterns)
        
        if needs_typing:
            # Check if typing import already exists
            has_typing_import = re.search(r'from typing import', content)
            
            if not has_typing_import:
                # Find the first import line
                import_match = re.search(r'^(import|from)\s+', content, re.MULTILINE)
                
                if import_match:
                    # Add typing import before first import
                    typing_import = "from typing import Dict, Any, Optional, List, Tuple, Union\n"
                    insert_pos = import_match.start()
                    new_content = content[:insert_pos] + typing_import + content[insert_pos:]
                    
                    # Write back to file
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    print(f"✅ Fixed typing imports in: {file_path}")
                    return True
                    
        return False
        
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def main():
    """Fix typing imports in all Python files"""
    project_root = Path('.')
    python_files = list(project_root.rglob('*.py'))
    
    fixed_count = 0
    
    print("🔧 Fixing missing typing imports...")
    
    for py_file in python_files:
        # Skip certain directories
        skip_dirs = ['__pycache__', '.git', 'venv', 'env']
        if any(skip_dir in str(py_file) for skip_dir in skip_dirs):
            continue
            
        if fix_typing_imports(py_file):
            fixed_count += 1
    
    print(f"\n✅ Fixed typing imports in {fixed_count} files")
    print("🚀 You can now run your backtesting system!")

if __name__ == "__main__":
    main()
