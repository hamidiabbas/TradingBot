#!/usr/bin/env python3
"""
Fixed Debug with Encoding Handling
"""

def debug_main_config():
    """Debug main.py with proper encoding handling"""
    
    print("🔍 DEBUGGING CONFIGURATION ISSUES")
    print("=" * 50)
    
    # Try different encodings
    encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
    content = None
    used_encoding = None
    
    for encoding in encodings_to_try:
        try:
            with open('main.py', 'r', encoding=encoding) as f:
                content = f.read()
            used_encoding = encoding
            print(f"✅ Successfully read main.py with {encoding} encoding")
            break
        except UnicodeDecodeError as e:
            print(f"❌ Failed with {encoding}: {e}")
            continue
        except Exception as e:
            print(f"❌ Error with {encoding}: {e}")
            continue
    
    if content is None:
        print("❌ Could not read main.py with any encoding!")
        return
    
    print(f"📄 File size: {len(content)} characters")
    print(f"📝 Used encoding: {used_encoding}")
    
    # Now debug the content
    print("\n🔍 SEARCHING FOR BUG PATTERNS:")
    
    # Check for key configuration lines
    if 'max_positions = 500' in content:
        print("✅ Found max_positions = 500 in file")
    elif 'max_positions = 8' in content:
        print("❌ Found max_positions = 8 in file - THIS IS THE BUG!")
    else:
        print("⚠️ No direct max_positions assignment found")
    
    # Check for risk configuration
    if "'base_risk_per_trade': 0.005" in content:
        print("✅ Found correct risk configuration (0.005)")
    elif "'base_risk_per_trade': 0.015" in content:
        print("❌ Found wrong risk configuration (0.015) - THIS IS THE BUG!")
    else:
        print("⚠️ Risk configuration not found in expected format")
    
    # Look for the critical bug - hardcoded /8}
    if '/8}' in content:
        print("❌ FOUND HARDCODED /8} - THIS IS THE MAIN BUG!")
        # Find the line
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '/8}' in line:
                print(f"   Line {i+1}: {line.strip()}")
    else:
        print("✅ No hardcoded /8} found")
    
    # Look for position limit messages
    if 'Position limit reached' in content:
        print("📍 Found position limit messages:")
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'Position limit reached' in line:
                print(f"   Line {i+1}: {line.strip()}")
    
    # Check actual config values using regex
    import re
    
    print("\n📊 SEARCHING FOR ACTUAL VALUES:")
    
    # Find all max_positions assignments
    max_pos_matches = re.findall(r'max_positions.*?=.*?(\d+)', content)
    if max_pos_matches:
        print(f"📍 Found max_positions values: {max_pos_matches}")
    
    # Find all base_risk_per_trade assignments  
    risk_matches = re.findall(r'base_risk_per_trade.*?=.*?(0\.\d+)', content)
    if risk_matches:
        print(f"📍 Found base_risk_per_trade values: {risk_matches}")
    
    # Check for FULLY FIXED marker
    if 'FULLY FIXED' in content:
        print("✅ File shows FULLY FIXED version")
    else:
        print("❌ File doesn't show FULLY FIXED marker")

if __name__ == "__main__":
    debug_main_config()
