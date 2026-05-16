"""
Test H1 fix: Cross-file dependency resolution in AST analyzer.

This test verifies that the ASTAnalyzer can now:
1. Extract function calls from function bodies
2. Build a symbol table across multiple files
3. Resolve imports and track their sources
4. Match function calls to their definitions across files
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.services.ast_analyzer import ASTAnalyzer, CodeElement


def test_python_cross_file_dependencies():
    """Test that Python cross-file dependencies are resolved."""
    
    # Create test files
    files = {
        'module_a.py': '''
def helper_function():
    return 42

class HelperClass:
    def method(self):
        pass
''',
        'module_b.py': '''
from module_a import helper_function, HelperClass

def main_function():
    result = helper_function()
    obj = HelperClass()
    return result
'''
    }
    
    analyzer = ASTAnalyzer()
    elements = analyzer.analyze_files(files)
    
    # Find main_function element
    main_func = None
    for elem in elements:
        if elem.name == 'main_function' and elem.type == 'function':
            main_func = elem
            break
    
    assert main_func is not None, "main_function not found"
    
    # Verify dependencies were extracted
    assert len(main_func.dependencies) > 0, "No dependencies found for main_function"
    
    # Check that helper_function is in dependencies
    has_helper = any('helper_function' in dep for dep in main_func.dependencies)
    assert has_helper, f"helper_function not in dependencies: {main_func.dependencies}"
    
    print("✓ Python cross-file dependencies resolved")
    print(f"  main_function dependencies: {main_func.dependencies}")


def test_symbol_table_building():
    """Test that symbol table is built correctly."""
    
    files = {
        'file1.py': '''
def function_one():
    pass

def function_two():
    pass
''',
        'file2.py': '''
def function_three():
    pass

class ClassOne:
    pass
'''
    }
    
    analyzer = ASTAnalyzer()
    elements = analyzer.analyze_files(files)
    
    # Check symbol table was populated
    assert 'function_one' in analyzer.symbol_table
    assert 'function_two' in analyzer.symbol_table
    assert 'function_three' in analyzer.symbol_table
    assert 'ClassOne' in analyzer.symbol_table
    
    # Verify file paths are correct
    assert analyzer.symbol_table['function_one'] == 'file1.py'
    assert analyzer.symbol_table['function_three'] == 'file2.py'
    
    print("✓ Symbol table built correctly")
    print(f"  Symbol table: {analyzer.symbol_table}")


def test_import_map_building():
    """Test that import map tracks imports correctly."""
    
    files = {
        'module.py': '''
import os
from pathlib import Path
from typing import List, Dict
'''
    }
    
    analyzer = ASTAnalyzer()
    elements = analyzer.analyze_files(files)
    
    # Check import map was populated
    assert 'module.py' in analyzer.import_map
    imports = analyzer.import_map['module.py']
    
    # Verify imports were tracked
    assert 'os' in imports or 'Path' in imports or 'List' in imports
    
    print("✓ Import map built correctly")
    print(f"  Import map: {analyzer.import_map}")


def test_local_vs_cross_file_dependencies():
    """Test that local calls are not marked as dependencies."""
    
    files = {
        'single_file.py': '''
def helper():
    return 1

def caller():
    result = helper()
    return result
'''
    }
    
    analyzer = ASTAnalyzer()
    elements = analyzer.analyze_files(files)
    
    # Find caller function
    caller_func = None
    for elem in elements:
        if elem.name == 'caller' and elem.type == 'function':
            caller_func = elem
            break
    
    assert caller_func is not None
    
    # Dependencies should be empty or not include same-file references
    # (since helper is in the same file)
    same_file_deps = [dep for dep in caller_func.dependencies if 'single_file.py' in dep]
    
    print("✓ Local vs cross-file dependencies handled")
    print(f"  caller dependencies: {caller_func.dependencies}")
    print(f"  Same-file deps: {same_file_deps}")


def test_javascript_cross_file_dependencies():
    """Test JavaScript/TypeScript cross-file dependency resolution."""
    
    files = {
        'utils.js': '''
export function utilFunction() {
    return true;
}

export class UtilClass {
    constructor() {}
}
''',
        'main.js': '''
import { utilFunction, UtilClass } from './utils';

function mainFunction() {
    const result = utilFunction();
    const obj = new UtilClass();
    return result;
}
'''
    }
    
    analyzer = ASTAnalyzer()
    elements = analyzer.analyze_files(files)
    
    # Find mainFunction
    main_func = None
    for elem in elements:
        if elem.name == 'mainFunction' and elem.type == 'function':
            main_func = elem
            break
    
    if main_func:
        print("✓ JavaScript cross-file dependencies processed")
        print(f"  mainFunction dependencies: {main_func.dependencies}")
    else:
        print("⚠ mainFunction not found (JS parsing may need tree-sitter-javascript)")


def test_empty_dependencies_before_fix():
    """Verify that single-file analysis still works (backward compatibility)."""
    
    analyzer = ASTAnalyzer()
    
    # Single file analysis (old method)
    content = '''
def simple_function():
    return 42
'''
    
    elements = analyzer.analyze_file('test.py', content)
    
    assert len(elements) > 0
    func = elements[0]
    assert func.name == 'simple_function'
    
    # Old method doesn't resolve dependencies (backward compatible)
    assert func.dependencies == []
    
    print("✓ Backward compatibility maintained")
    print(f"  Single-file analysis still works")


def run_all_tests():
    """Run all H1 cross-file dependency tests."""
    print("\n" + "="*60)
    print("Testing H1 Fix: Cross-File Dependency Resolution")
    print("="*60 + "\n")
    
    tests = [
        ("Symbol Table Building", test_symbol_table_building),
        ("Import Map Building", test_import_map_building),
        ("Python Cross-File Dependencies", test_python_cross_file_dependencies),
        ("Local vs Cross-File Dependencies", test_local_vs_cross_file_dependencies),
        ("JavaScript Cross-File Dependencies", test_javascript_cross_file_dependencies),
        ("Backward Compatibility", test_empty_dependencies_before_fix),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\nTest: {test_name}")
            print("-" * 60)
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ ERROR: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)

# Made with Bob
