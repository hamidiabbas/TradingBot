#!/usr/bin/env python3
"""
Comprehensive Bug Hunter and Fixer
"""

import re

def find_and_fix_all_bugs():
    """Find and fix ALL instances of the bugs"""
    
    print("🔍 COMPREHENSIVE BUG HUNTER & FIXER")
    print("=" * 50)
    
    try:
        # Read the file
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        print(f"📄 Original file size: {len(content)} characters")
        
        # BUG HUNT 1: Find all instances of "/8" in error messages
        print("\n🔍 HUNTING BUG 1: Hardcoded /8 patterns")
        
        patterns_8 = [
            (r'/8\}', '/{self.max_positions}'),
            (r'/8\)', '/{self.max_positions})'),
            (r'\{total_positions\}/8', '{total_positions}/{self.max_positions}'),
            (r'194/8', '194/{self.max_positions}'),
            (r'200/8', '200/{self.max_positions}'),
            (r'positions/8', 'positions/{self.max_positions}'),
        ]
        
        for pattern, replacement in patterns_8:
            matches = re.findall(pattern, content)
            if matches:
                print(f"   🎯 Found {len(matches)} matches for pattern: {pattern}")
                content = re.sub(pattern, replacement, content)
        
        # BUG HUNT 2: Find all f-strings with position limits
        print("\n🔍 HUNTING BUG 2: F-string position limit patterns")
        
        # Search for all f-string patterns that might contain the bug
        fstring_patterns = re.findall(r'f"[^"]*Position limit reached[^"]*"', content)
        for i, pattern in enumerate(fstring_patterns):
            print(f"   📍 F-string {i+1}: {pattern}")
            if '/8}' in pattern or '/8)' in pattern:
                print(f"      ❌ CONTAINS BUG!")
                fixed_pattern = pattern.replace('/8}', '/{self.max_positions}').replace('/8)', '/{self.max_positions})')
                content = content.replace(pattern, fixed_pattern)
                print(f"      ✅ Fixed to: {fixed_pattern}")
        
        # BUG HUNT 3: Risk percentage display
        print("\n🔍 HUNTING BUG 3: Risk percentage display")
        
        risk_patterns = [
            (r'Risk per Trade: 1\.500%', 'Risk per Trade: 0.500%'),
            (r'Risk per Trade: 1\.5%', 'Risk per Trade: 0.5%'),
            (r'1\.500% \(optimized', '0.500% (optimized'),
            (r'1\.5% \(optimized', '0.5% (optimized'),
        ]
        
        for pattern, replacement in risk_patterns:
            matches = re.findall(pattern, content)
            if matches:
                print(f"   🎯 Found {len(matches)} risk display bugs")
                content = re.sub(pattern, replacement, content)
        
        # BUG HUNT 4: Configuration values
        print("\n🔍 HUNTING BUG 4: Configuration defaults")
        
        config_patterns = [
            (r"'base_risk_per_trade': 0\.015", "'base_risk_per_trade': 0.005"),
            (r"'base_risk_per_trade': 0\.02", "'base_risk_per_trade': 0.005"),
            (r"base_risk_per_trade.*?=.*?0\.015", "base_risk_per_trade = 0.005"),
            (r"base_risk_per_trade.*?=.*?0\.02", "base_risk_per_trade = 0.005"),
        ]
        
        for pattern, replacement in config_patterns:
            old_content = content
            content = re.sub(pattern, replacement, content)
            if content != old_content:
                print(f"   ✅ Fixed config pattern: {pattern}")
        
        # BUG HUNT 5: Direct string replacements for sneaky bugs
        print("\n🔍 HUNTING BUG 5: Direct string bugs")
        
        direct_replacements = [
            ('(194/8)', '(194/{self.max_positions})'),
            ('(200/8)', '(200/{self.max_positions})'),
            ('({total_positions}/8)', '({total_positions}/{self.max_positions})'),
            ('limit reached (194/8)', 'limit reached (194/{self.max_positions})'),
            ('limit reached (200/8)', 'limit reached (200/{self.max_positions})'),
            ('f"Position limit reached ({total_positions}/8)"', 'f"Position limit reached ({total_positions}/{self.max_positions})"'),
        ]
        
        for old_str, new_str in direct_replacements:
            if old_str in content:
                print(f"   🎯 Found direct string: {old_str}")
                content = content.replace(old_str, new_str)
                print(f"   ✅ Replaced with: {new_str}")
        
        # BUG HUNT 6: Search for any remaining "8" that could be the bug
        print("\n🔍 HUNTING BUG 6: Any remaining position limit bugs")
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'Position limit reached' in line and '/8' in line:
                print(f"   ❌ Line {i+1} still has bug: {line.strip()}")
                # Fix this specific line
                new_line = line.replace('/8}', '/{self.max_positions}').replace('/8)', '/{self.max_positions})')
                lines[i] = new_line
                print(f"   ✅ Fixed to: {new_line.strip()}")
        
        content = '\n'.join(lines)
        
        # Final verification and save
        if content != original_content:
            # Write the completely fixed file
            with open('main.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"\n🎉 COMPREHENSIVE FIXES APPLIED!")
            print(f"📄 New file size: {len(content)} characters")
            print(f"📊 Total changes: {len(content) - len(original_content)} characters")
            
            # Final verification
            print(f"\n🔍 FINAL VERIFICATION:")
            
            # Check for remaining bugs
            if '/8}' in content or '/8)' in content:
                remaining_8 = content.count('/8}') + content.count('/8)')
                print(f"   ❌ Still has {remaining_8} instances of '/8'")
                
                # Show exactly where
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if '/8}' in line or '/8)' in line:
                        print(f"      Line {i+1}: {line.strip()}")
            else:
                print(f"   ✅ No '/8' bugs remaining!")
            
            if 'Risk per Trade: 0.500%' in content or 'Risk per Trade: 0.5%' in content:
                print(f"   ✅ Risk percentage display fixed!")
            else:
                print(f"   ❌ Risk percentage display still wrong")
                
            print(f"\n🚀 ALL BUGS SHOULD BE FIXED - RESTART YOUR BOT!")
            
        else:
            print(f"\n⚠️ No bugs found to fix")
            
    except Exception as e:
        print(f"❌ Error during comprehensive fix: {e}")

if __name__ == "__main__":
    find_and_fix_all_bugs()
