"""
Tests for AST analyzer service.
Validates code element extraction from Python, JavaScript, and TypeScript files.
"""
import pytest
from backend.services.ast_analyzer import ASTAnalyzer, CodeElement


class TestASTAnalyzer:
    """Test suite for ASTAnalyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Create an ASTAnalyzer instance."""
        return ASTAnalyzer()
    
    def test_python_function_extraction(self, analyzer):
        """Test extraction of Python function definitions."""
        code = """
def calculate_total(items):
    total = 0
    for item in items:
        total += item
    return total

def process_data(data):
    return data.strip()
"""
        elements = analyzer.analyze_file("test.py", code)
        
        # Should extract 2 functions
        functions = [e for e in elements if e.type == 'function']
        assert len(functions) == 2
        
        # Check function names
        func_names = {f.name for f in functions}
        assert 'calculate_total' in func_names
        assert 'process_data' in func_names
        
        # Check line numbers
        calc_func = next(f for f in functions if f.name == 'calculate_total')
        assert calc_func.line_start == 2
        assert calc_func.file_path == "test.py"
    
    def test_python_class_extraction(self, analyzer):
        """Test extraction of Python class definitions."""
        code = """
class PaymentService:
    def __init__(self):
        self.total = 0
    
    def process(self):
        pass

class UserManager:
    pass
"""
        elements = analyzer.analyze_file("services.py", code)
        
        # Should extract 2 classes
        classes = [e for e in elements if e.type == 'class']
        assert len(classes) == 2
        
        # Check class names
        class_names = {c.name for c in classes}
        assert 'PaymentService' in class_names
        assert 'UserManager' in class_names
    
    def test_python_import_extraction(self, analyzer):
        """Test extraction of Python import statements."""
        code = """
import os
import sys
from typing import List, Dict
from backend.services import analyzer
"""
        elements = analyzer.analyze_file("module.py", code)
        
        # Should extract 4 imports
        imports = [e for e in elements if e.type == 'import']
        assert len(imports) == 4
        
        # Check import content
        import_texts = [i.name for i in imports]
        assert any('import os' in text for text in import_texts)
        assert any('from typing import' in text for text in import_texts)
    
    def test_javascript_function_extraction(self, analyzer):
        """Test extraction of JavaScript function definitions."""
        code = """
function calculateTotal(items) {
    return items.reduce((sum, item) => sum + item, 0);
}

function processData(data) {
    return data.trim();
}
"""
        elements = analyzer.analyze_file("utils.js", code)
        
        # Should extract 2 functions
        functions = [e for e in elements if e.type == 'function']
        assert len(functions) >= 2
        
        # Check function names
        func_names = {f.name for f in functions}
        assert 'calculateTotal' in func_names
        assert 'processData' in func_names
    
    def test_javascript_class_extraction(self, analyzer):
        """Test extraction of JavaScript class definitions."""
        code = """
class PaymentService {
    constructor() {
        this.total = 0;
    }
    
    process() {
        return this.total;
    }
}

class UserManager {
}
"""
        elements = analyzer.analyze_file("services.js", code)
        
        # Should extract 2 classes
        classes = [e for e in elements if e.type == 'class']
        assert len(classes) == 2
        
        # Check class names
        class_names = {c.name for c in classes}
        assert 'PaymentService' in class_names
        assert 'UserManager' in class_names
    
    def test_typescript_function_extraction(self, analyzer):
        """Test extraction of TypeScript function definitions."""
        code = """
function calculateTotal(items: number[]): number {
    return items.reduce((sum, item) => sum + item, 0);
}

const processData = (data: string): string => {
    return data.trim();
};
"""
        elements = analyzer.analyze_file("utils.ts", code)
        
        # Should extract at least 1 function (arrow functions may vary)
        functions = [e for e in elements if e.type == 'function']
        assert len(functions) >= 1
        
        # Check that calculateTotal is extracted
        func_names = {f.name for f in functions}
        assert 'calculateTotal' in func_names
    
    def test_unsupported_language_returns_empty(self, analyzer):
        """Test that unsupported file types return empty list."""
        code = "SELECT * FROM users;"
        elements = analyzer.analyze_file("query.sql", code)
        
        assert elements == []
    
    def test_empty_file_returns_empty(self, analyzer):
        """Test that empty files return empty list."""
        code = ""
        elements = analyzer.analyze_file("empty.py", code)
        
        assert elements == []
    
    def test_file_with_no_extractable_elements(self, analyzer):
        """Test file with only comments and whitespace."""
        code = """
# This is a comment
# Another comment

"""
        elements = analyzer.analyze_file("comments.py", code)
        
        # Should return empty or only trivial elements
        assert len(elements) == 0
    
    def test_language_detection(self, analyzer):
        """Test language detection from file extensions."""
        assert analyzer._detect_language("test.py") == "python"
        assert analyzer._detect_language("test.js") == "javascript"
        assert analyzer._detect_language("test.jsx") == "javascript"
        assert analyzer._detect_language("test.ts") == "typescript"
        assert analyzer._detect_language("test.tsx") == "typescript"
        assert analyzer._detect_language("test.sql") == "unknown"
    
    def test_code_element_attributes(self, analyzer):
        """Test that CodeElement has all required attributes."""
        code = """
def test_function():
    pass
"""
        elements = analyzer.analyze_file("test.py", code)
        
        assert len(elements) == 1
        element = elements[0]
        
        # Check all required attributes exist
        assert hasattr(element, 'type')
        assert hasattr(element, 'name')
        assert hasattr(element, 'file_path')
        assert hasattr(element, 'line_start')
        assert hasattr(element, 'line_end')
        assert hasattr(element, 'dependencies')
        assert hasattr(element, 'metadata')
        
        # Check types
        assert isinstance(element.type, str)
        assert isinstance(element.name, str)
        assert isinstance(element.file_path, str)
        assert isinstance(element.line_start, int)
        assert isinstance(element.line_end, int)
        assert isinstance(element.dependencies, list)
        assert isinstance(element.metadata, dict)
    
    def test_multi_language_support(self, analyzer):
        """Test that analyzer supports multiple languages."""
        # Python
        py_elements = analyzer.analyze_file("test.py", "def foo(): pass")
        assert len(py_elements) > 0
        
        # JavaScript
        js_elements = analyzer.analyze_file("test.js", "function foo() {}")
        assert len(js_elements) > 0
        
        # TypeScript
        ts_elements = analyzer.analyze_file("test.ts", "function foo(): void {}")
        assert len(ts_elements) > 0

# Made with Bob
