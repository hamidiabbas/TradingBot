#!/usr/bin/env python3
"""
Strategy File Finder and Structure Analyzer
Locates all strategy files and analyzes their structure
"""

import os
import re
import inspect
from typing import Dict, List, Any
import importlib.util

def find_strategy_files(search_paths: List[str] = None) -> Dict[str, Any]:
    """Find all strategy files in the project"""
    
    if search_paths is None:
        search_paths = [
            '.',           # Current directory
            './strategies', # Strategies folder
            './src',       # Source folder
            './trading',   # Trading folder
        ]
    
    strategy_files = {
        'python_files': [],
        'strategy_classes': {},
        'main_files': []
    }
    
    print("🔍 SEARCHING FOR STRATEGY FILES...")
    print("="*60)
    
    # Target strategy names we're looking for
    target_strategies = [
        'EnhancedICTStrategy', 'ICTStrategy',
        'EnhancedRTMStrategy', 'RTMStrategy', 
        'EnhancedSMCStrategy', 'SMCStrategy',
        'EnhancedScalpingStrategy', 'ScalpingStrategy',
        'EnhancedNewsStrategy', 'NewsStrategy',
        'EnhancedPivotPointStrategy', 'PivotPointStrategy'
    ]
    
    # Search for Python files
    for search_path in search_paths:
        if os.path.exists(search_path):
            print(f"📁 Searching in: {search_path}")
            
            for root, dirs, files in os.walk(search_path):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        strategy_files['python_files'].append(file_path)
                        
                        # Check if it's a main strategy file
                        if any(name in file.lower() for name in ['strategy', 'signal_factory', 'main', 'trading']):
                            strategy_files['main_files'].append(file_path)
                        
                        # Search for strategy classes in the file
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                                for strategy_name in target_strategies:
                                    # Look for class definitions
                                    pattern = rf'class\s+{re.escape(strategy_name)}\s*\([^)]*\):'
                                    if re.search(pattern, content):
                                        if file_path not in strategy_files['strategy_classes']:
                                            strategy_files['strategy_classes'][file_path] = []
                                        strategy_files['strategy_classes'][file_path].append(strategy_name)
                                        print(f"   ✅ Found {strategy_name} in {file_path}")
                        
                        except Exception as e:
                            print(f"   ⚠️ Error reading {file_path}: {e}")
    
    return strategy_files

def analyze_strategy_structure(file_path: str) -> Dict[str, Any]:
    """Analyze the structure of a strategy file"""
    
    analysis = {
        'file_path': file_path,
        'classes_found': [],
        'has_analyze_method': {},
        'has_analyze_multi_timeframe': {},
        'imports': [],
        'total_lines': 0
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            analysis['total_lines'] = len(content.split('\n'))
        
        # Find all class definitions
        class_pattern = r'class\s+(\w+)\s*\([^)]*\):'
        classes = re.findall(class_pattern, content)
        analysis['classes_found'] = classes
        
        # Check for analyze methods in each class
        for class_name in classes:
            # Look for analyze method
            analyze_pattern = rf'class\s+{re.escape(class_name)}.*?(?=class|\Z)'
            class_content = re.search(analyze_pattern, content, re.DOTALL)
            
            if class_content:
                class_text = class_content.group(0)
                analysis['has_analyze_method'][class_name] = 'def analyze(' in class_text
                analysis['has_analyze_multi_timeframe'][class_name] = 'def analyze_multi_timeframe(' in class_text
        
        # Find imports
        import_pattern = r'^(from\s+\S+\s+import\s+.+|import\s+.+)$'
        imports = re.findall(import_pattern, content, re.MULTILINE)
        analysis['imports'] = imports[:10]  # First 10 imports
        
    except Exception as e:
        analysis['error'] = str(e)
    
    return analysis

def print_analysis_report(strategy_files: Dict[str, Any]):
    """Print comprehensive analysis report"""
    
    print("\n" + "="*80)
    print("📋 STRATEGY FILE ANALYSIS REPORT")
    print("="*80)
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total Python files found: {len(strategy_files['python_files'])}")
    print(f"   Main strategy files: {len(strategy_files['main_files'])}")
    print(f"   Files with target strategies: {len(strategy_files['strategy_classes'])}")
    
    if strategy_files['main_files']:
        print(f"\n📁 MAIN STRATEGY FILES:")
        for file_path in strategy_files['main_files']:
            print(f"   • {file_path}")
    
    if strategy_files['strategy_classes']:
        print(f"\n🎯 STRATEGY CLASSES FOUND:")
        for file_path, strategies in strategy_files['strategy_classes'].items():
            print(f"\n   📄 {file_path}:")
            
            # Analyze this file
            analysis = analyze_strategy_structure(file_path)
            
            print(f"      Lines of code: {analysis['total_lines']}")
            print(f"      Total classes: {len(analysis['classes_found'])}")
            print(f"      Target strategies: {len(strategies)}")
            
            for strategy in strategies:
                has_analyze = analysis['has_analyze_method'].get(strategy, False)
                has_mtf = analysis['has_analyze_multi_timeframe'].get(strategy, False)
                
                status_analyze = "✅" if has_analyze else "❌"
                status_mtf = "✅" if has_mtf else "❌"
                
                print(f"         {status_analyze} {strategy} - analyze() method")
                print(f"         {status_mtf} {strategy} - analyze_multi_timeframe() method")
    
    else:
        print(f"\n❌ NO TARGET STRATEGIES FOUND!")
        print(f"   The following strategies were not found in any files:")
        target_strategies = [
            'EnhancedICTStrategy', 'ICTStrategy',
            'EnhancedRTMStrategy', 'RTMStrategy', 
            'EnhancedSMCStrategy', 'SMCStrategy',
            'EnhancedScalpingStrategy', 'ScalpingStrategy',
            'EnhancedNewsStrategy', 'NewsStrategy',
            'EnhancedPivotPointStrategy', 'PivotPointStrategy'
        ]
        for strategy in target_strategies:
            print(f"     • {strategy}")

if __name__ == "__main__":
    print("🔍 STRATEGY FILE FINDER AND ANALYZER")
    print("="*60)
    
    # Find all strategy files
    results = find_strategy_files()
    
    # Print detailed analysis
    print_analysis_report(results)
    
    print(f"\n💡 RECOMMENDATIONS:")
    
    if results['strategy_classes']:
        print(f"   ✅ Strategies found! Use the targeted fix approach below.")
    else:
        print(f"   ❌ No strategies found. Possible reasons:")
        print(f"      1. Strategies are in a different location")
        print(f"      2. Strategies have different class names") 
        print(f"      3. Strategies are dynamically generated")
        print(f"      4. Files are in a different format")
        
    print(f"   🔧 Run this script first to identify the correct file structure")
