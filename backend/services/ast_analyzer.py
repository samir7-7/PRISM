"""
AST analyzer using tree-sitter for code parsing.
Extracts functions, classes, and imports from source code.
"""
import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
import tree_sitter_typescript as tstypescript
from tree_sitter import Language, Parser
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class CodeElement:
    """Represents a code element (function, class, import, etc.)."""
    
    type: str  # function, class, import, method
    name: str
    file_path: str
    line_start: int
    line_end: int
    dependencies: List[str]  # Names of other elements this depends on
    metadata: Dict[str, Any]  # Additional information


class ASTAnalyzer:
    """Analyzer for extracting code structure using tree-sitter."""
    
    def __init__(self):
        # Initialize parsers for different languages
        self.parsers = {
            'python': self._create_parser(Language(tspython.language())),
            'javascript': self._create_parser(Language(tsjavascript.language())),
            'typescript': self._create_parser(Language(tstypescript.language())),
        }
    
    def _create_parser(self, language: Language) -> Parser:
        """Create a parser for a specific language."""
        parser = Parser()
        parser.set_language(language)
        return parser
    
    def analyze_file(self, file_path: str, content: str) -> List[CodeElement]:
        """
        Analyze a source file and extract code elements.
        
        Args:
            file_path: Path to the file
            content: File content as string
            
        Returns:
            List of CodeElement objects
        """
        # Determine language from file extension
        language = self._detect_language(file_path)
        
        if language not in self.parsers:
            # Unsupported language, return empty list
            return []
        
        parser = self.parsers[language]
        tree = parser.parse(bytes(content, 'utf8'))
        
        # Extract elements based on language
        if language == 'python':
            return self._extract_python_elements(tree, file_path, content)
        elif language in ['javascript', 'typescript']:
            return self._extract_js_elements(tree, file_path, content)
        
        return []
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        if file_path.endswith('.py'):
            return 'python'
        elif file_path.endswith('.js') or file_path.endswith('.jsx'):
            return 'javascript'
        elif file_path.endswith('.ts') or file_path.endswith('.tsx'):
            return 'typescript'
        return 'unknown'
    
    def _extract_python_elements(
        self, 
        tree, 
        file_path: str, 
        content: str
    ) -> List[CodeElement]:
        """Extract code elements from Python AST."""
        elements = []
        root_node = tree.root_node
        
        # Extract imports
        for node in self._find_nodes_by_type(root_node, ['import_statement', 'import_from_statement']):
            import_elem = self._parse_python_import(node, file_path, content)
            if import_elem:
                elements.append(import_elem)
        
        # Extract function definitions
        for node in self._find_nodes_by_type(root_node, ['function_definition']):
            func_elem = self._parse_python_function(node, file_path, content)
            if func_elem:
                elements.append(func_elem)
        
        # Extract class definitions
        for node in self._find_nodes_by_type(root_node, ['class_definition']):
            class_elem = self._parse_python_class(node, file_path, content)
            if class_elem:
                elements.append(class_elem)
        
        return elements
    
    def _extract_js_elements(
        self, 
        tree, 
        file_path: str, 
        content: str
    ) -> List[CodeElement]:
        """Extract code elements from JavaScript/TypeScript AST."""
        elements = []
        root_node = tree.root_node
        
        # Extract imports
        for node in self._find_nodes_by_type(root_node, ['import_statement']):
            import_elem = self._parse_js_import(node, file_path, content)
            if import_elem:
                elements.append(import_elem)
        
        # Extract function declarations
        for node in self._find_nodes_by_type(root_node, ['function_declaration', 'arrow_function']):
            func_elem = self._parse_js_function(node, file_path, content)
            if func_elem:
                elements.append(func_elem)
        
        # Extract class declarations
        for node in self._find_nodes_by_type(root_node, ['class_declaration']):
            class_elem = self._parse_js_class(node, file_path, content)
            if class_elem:
                elements.append(class_elem)
        
        return elements
    
    def _find_nodes_by_type(self, node, types: List[str]) -> List:
        """Recursively find all nodes of specific types."""
        results = []
        
        if node.type in types:
            results.append(node)
        
        for child in node.children:
            results.extend(self._find_nodes_by_type(child, types))
        
        return results
    
    def _parse_python_import(self, node, file_path: str, content: str) -> Optional[CodeElement]:
        """Parse Python import statement."""
        line_start = node.start_point[0] + 1
        line_end = node.end_point[0] + 1
        
        # Extract import names
        import_text = content[node.start_byte:node.end_byte]
        
        return CodeElement(
            type='import',
            name=import_text.strip(),
            file_path=file_path,
            line_start=line_start,
            line_end=line_end,
            dependencies=[],
            metadata={'raw': import_text}
        )
    
    def _parse_python_function(self, node, file_path: str, content: str) -> Optional[CodeElement]:
        """Parse Python function definition."""
        # Find function name
        name_node = None
        for child in node.children:
            if child.type == 'identifier':
                name_node = child
                break
        
        if not name_node:
            return None
        
        func_name = content[name_node.start_byte:name_node.end_byte]
        line_start = node.start_point[0] + 1
        line_end = node.end_point[0] + 1
        
        return CodeElement(
            type='function',
            name=func_name,
            file_path=file_path,
            line_start=line_start,
            line_end=line_end,
            dependencies=[],
            metadata={}
        )
    
    def _parse_python_class(self, node, file_path: str, content: str) -> Optional[CodeElement]:
        """Parse Python class definition."""
        # Find class name
        name_node = None
        for child in node.children:
            if child.type == 'identifier':
                name_node = child
                break
        
        if not name_node:
            return None
        
        class_name = content[name_node.start_byte:name_node.end_byte]
        line_start = node.start_point[0] + 1
        line_end = node.end_point[0] + 1
        
        return CodeElement(
            type='class',
            name=class_name,
            file_path=file_path,
            line_start=line_start,
            line_end=line_end,
            dependencies=[],
            metadata={}
        )
    
    def _parse_js_import(self, node, file_path: str, content: str) -> Optional[CodeElement]:
        """Parse JavaScript/TypeScript import statement."""
        line_start = node.start_point[0] + 1
        line_end = node.end_point[0] + 1
        
        import_text = content[node.start_byte:node.end_byte]
        
        return CodeElement(
            type='import',
            name=import_text.strip(),
            file_path=file_path,
            line_start=line_start,
            line_end=line_end,
            dependencies=[],
            metadata={'raw': import_text}
        )
    
    def _parse_js_function(self, node, file_path: str, content: str) -> Optional[CodeElement]:
        """Parse JavaScript/TypeScript function."""
        # Try to find function name
        name = 'anonymous'
        for child in node.children:
            if child.type == 'identifier':
                name = content[child.start_byte:child.end_byte]
                break
        
        line_start = node.start_point[0] + 1
        line_end = node.end_point[0] + 1
        
        return CodeElement(
            type='function',
            name=name,
            file_path=file_path,
            line_start=line_start,
            line_end=line_end,
            dependencies=[],
            metadata={}
        )
    
    def _parse_js_class(self, node, file_path: str, content: str) -> Optional[CodeElement]:
        """Parse JavaScript/TypeScript class."""
        # Find class name
        name_node = None
        for child in node.children:
            if child.type == 'identifier':
                name_node = child
                break
        
        if not name_node:
            return None
        
        class_name = content[name_node.start_byte:name_node.end_byte]
        line_start = node.start_point[0] + 1
        line_end = node.end_point[0] + 1
        
        return CodeElement(
            type='class',
            name=class_name,
            file_path=file_path,
            line_start=line_start,
            line_end=line_end,
            dependencies=[],
            metadata={}
        )

# Made with Bob
