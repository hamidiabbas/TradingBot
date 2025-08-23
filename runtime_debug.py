#!/usr/bin/env python3
"""
Inject Runtime Debug to See What's Actually Happening
"""

def inject_runtime_debug():
    """Add runtime debug prints to see actual values at runtime"""
    
    print("💉 INJECTING RUNTIME DEBUG INTO MAIN.PY")
    print("=" * 50)
    
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the process_signals_and_execute method and add debug
        lines = content.split('\n')
        new_lines = []
        
        in_process_signals = False
        debug_added = False
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            # Find the method
            if 'def process_signals_and_execute(' in line:
                in_process_signals = True
                print(f"✅ Found process_signals_and_execute method at line {i+1}")
            
            # Add debug right before the limit check
            if in_process_signals and 'if total_positions >=' in line and not debug_added:
                # Add comprehensive debug
                debug_lines = [
                    '',
                    '                # 🔍 RUNTIME DEBUG - INJECTED',
                    '                print(f"🔍 RUNTIME DEBUG:")',
                    '                print(f"   total_positions = {total_positions}")',
                    '                print(f"   self.max_positions = {self.max_positions}")',
                    '                print(f"   self.base_risk_per_trade = {self.base_risk_per_trade}")',
                    '                print(f"   Type of self.max_positions: {type(self.max_positions)}")',
                    '                print(f"   Value check: {total_positions} >= {self.max_positions} = {total_positions >= self.max_positions}")',
                    ''
                ]
                
                # Insert debug lines before the current line
                for debug_line in reversed(debug_lines):
                    new_lines.insert(-1, debug_line)
                
                debug_added = True
                print(f"✅ Added runtime debug at line {i+1}")
        
        # Also add debug to the limit_reason assignment
        for i, line in enumerate(new_lines):
            if 'limit_reason = f"Position limit reached' in line:
                # Add debug right before this line
                debug_line = '                print(f"🔍 LIMIT MESSAGE DEBUG: Using total_positions={total_positions}, max_positions={self.max_positions}")'
                new_lines.insert(i, debug_line)
                print(f"✅ Added limit message debug")
                break
        
        # Write back
        new_content = '\n'.join(new_lines)
        with open('main.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"\n🎉 RUNTIME DEBUG INJECTED!")
        print(f"📄 File size: {len(new_content)} characters")
        print(f"\n🚀 Now run your bot and you'll see EXACTLY what values are being used!")
        
    except Exception as e:
        print(f"❌ Error injecting debug: {e}")

if __name__ == "__main__":
    inject_runtime_debug()
