"""
AST analyzer using tree-sitter for code parsing.
Extracts functions, classes, and imports from source code.
"""
import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
import tree_sitter_typescript as tstypescript
from tree_sitter import Language, Parser
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
import os


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
        # tree-sitter 0.22+ requires passing language to Parser constructor
        # TypeScript module has language_typescript() instead of language()
        self.parsers = {
            'python': Parser(Language(tspython.language())),
            'javascript': Parser(Language(tsjavascript.language())),
            'typescript': Parser(Language(tstypescript.language_typescript())),
        }
        
        # Symbol table: maps symbol names to their defining file paths
        # Format: {symbol_name: file_path}
        self.symbol_table: Dict[str, str] = {}
        
        # Import map: tracks what each file imports and from where
        # Format: {file_path: {imported_name: source_module}}
        self.import_map: Dict[str, Dict[str, str]] = {}
    
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
    
    def analyze_files(self, files: Dict[str, str]) -> List[CodeElement]:
        """
        Analyze multiple files and build cross-file dependencies.
        
        Args:
            files: Dictionary mapping file paths to their content
            
        Returns:
            List of CodeElement objects with resolved dependencies
        """
        all_elements = []
        
        # First pass: Extract all elements and build symbol table
        for file_path, content in files.items():
            elements = self.analyze_file(file_path, content)
            all_elements.extend(elements)
            
            # Build symbol table for functions and classes
            for elem in elements:
                if elem.type in ['function', 'class', 'method']:
                    self.symbol_table[elem.name] = elem.file_path
        
        # Second pass: Resolve dependencies
        for file_path, content in files.items():
            language = self._detect_language(file_path)
            if language not in self.parsers:
                continue
                
            parser = self.parsers[language]
            tree = parser.parse(bytes(content, 'utf8'))
            
            # Extract imports and build import map
            if language == 'python':
                self._build_python_import_map(tree, file_path, content)
            elif language in ['javascript', 'typescript']:
                self._build_js_import_map(tree, file_path, content)
        
        # Third pass: Extract function calls and resolve dependencies
        for elem in all_elements:
            if elem.type in ['function', 'method']:
                # Find the element in the original file and extract calls
                file_content = files.get(elem.file_path, '')
                if file_content:
                    language = self._detect_language(elem.file_path)
                    if language in self.parsers:
                        parser = self.parsers[language]
                        tree = parser.parse(bytes(file_content, 'utf8'))
                        
                        # Find the function node and extract calls
                        if language == 'python':
                            calls = self._extract_python_calls(tree, elem, file_content)
                        elif language in ['javascript', 'typescript']:
                            calls = self._extract_js_calls(tree, elem, file_content)
                        else:
                            calls = set()
                        
                        # Resolve calls to dependencies
                        elem.dependencies = self._resolve_dependencies(
                            calls, elem.file_path
                        )
        
        return all_elements
    
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

    
    def _build_python_import_map(self, tree, file_path: str, content: str):
        """Build import map for Python file."""
        if file_path not in self.import_map:
            self.import_map[file_path] = {}
        
        root_node = tree.root_node
        
        # Handle 'import module' statements
        for node in self._find_nodes_by_type(root_node, ['import_statement']):
            import_text = content[node.start_byte:node.end_byte]
            # Extract module name (e.g., "import os" -> "os")
            parts = import_text.replace('import', '').strip().split()
            if parts:
                module_name = parts[0].split('.')[0]
                self.import_map[file_path][module_name] = module_name
        
        # Handle 'from module import name' statements
        for node in self._find_nodes_by_type(root_node, ['import_from_statement']):
            import_text = content[node.start_byte:node.end_byte]
            # Parse "from X import Y" or "from X import Y as Z"
            if 'from' in import_text and 'import' in import_text:
                parts = import_text.split('import')
                if len(parts) == 2:
                    module_part = parts[0].replace('from', '').strip()
                    names_part = parts[1].strip()
                    
                    # Handle multiple imports: "from X import A, B, C"
                    for name in names_part.split(','):
                        name = name.strip().split(' as ')[0].strip()
                        if name:
                            self.import_map[file_path][name] = module_part
    
    def _build_js_import_map(self, tree, file_path: str, content: str):
        """Build import map for JavaScript/TypeScript file."""
        if file_path not in self.import_map:
            self.import_map[file_path] = {}
        
        root_node = tree.root_node
        
        for node in self._find_nodes_by_type(root_node, ['import_statement']):
            import_text = content[node.start_byte:node.end_byte]
            
            # Parse various import formats:
            # import X from 'module'
            # import { X, Y } from 'module'
            # import * as X from 'module'
            
            if 'from' in import_text:
                parts = import_text.split('from')
                if len(parts) == 2:
                    module_part = parts[1].strip().strip("'\"").strip(';')
                    import_part = parts[0].replace('import', '').strip()
                    
                    # Handle named imports: { X, Y }
                    if '{' in import_part and '}' in import_part:
                        names = import_part.strip('{}').split(',')
                        for name in names:
                            name = name.strip().split(' as ')[0].strip()
                            if name:
                                self.import_map[file_path][name] = module_part
                    # Handle default import: X
                    elif import_part and not import_part.startswith('*'):
                        self.import_map[file_path][import_part] = module_part
    
    def _extract_python_calls(self, tree, elem: CodeElement, content: str) -> Set[str]:
        """Extract function calls from a Python function."""
        calls = set()
        root_node = tree.root_node
        
        # Find the function node that matches this element
        for func_node in self._find_nodes_by_type(root_node, ['function_definition']):
            func_line_start = func_node.start_point[0] + 1
            if func_line_start == elem.line_start:
                # Found the matching function, extract calls from its body
                for call_node in self._find_nodes_by_type(func_node, ['call']):
                    # Get the function name being called
                    for child in call_node.children:
                        if child.type in ['identifier', 'attribute']:
                            call_name = content[child.start_byte:child.end_byte]
                            # Extract just the function name (not the full path)
                            if '.' in call_name:
                                call_name = call_name.split('.')[-1]
                            calls.add(call_name)
                            break
                break
        
        return calls
    
    def _extract_js_calls(self, tree, elem: CodeElement, content: str) -> Set[str]:
        """Extract function calls from a JavaScript/TypeScript function."""
        calls = set()
        root_node = tree.root_node
        
        # Find the function node that matches this element
        for func_node in self._find_nodes_by_type(root_node, ['function_declaration', 'arrow_function']):
            func_line_start = func_node.start_point[0] + 1
            if func_line_start == elem.line_start:
                # Found the matching function, extract calls from its body
                for call_node in self._find_nodes_by_type(func_node, ['call_expression']):
                    # Get the function name being called
                    for child in call_node.children:
                        if child.type in ['identifier', 'member_expression']:
                            call_name = content[child.start_byte:child.end_byte]
                            # Extract just the function name (not the full path)
                            if '.' in call_name:
                                call_name = call_name.split('.')[-1]
                            calls.add(call_name)
                            break
                break
        
        return calls
    
    def _resolve_dependencies(self, calls: Set[str], file_path: str) -> List[str]:
        """
        Resolve function calls to their defining files.
        
        Args:
            calls: Set of function names called
            file_path: Path of the file making the calls
            
        Returns:
            List of dependency identifiers (file_path:function_name)
        """
        dependencies = []
        imports = self.import_map.get(file_path, {})
        
        for call_name in calls:
            # Check if this call is imported from another module
            if call_name in imports:
                source_module = imports[call_name]
                # Try to resolve to actual file path
                # For now, use module name as identifier
                dependencies.append(f"{source_module}:{call_name}")
            
            # Check if this call is defined in the symbol table
            elif call_name in self.symbol_table:
                defining_file = self.symbol_table[call_name]
                # Only add as dependency if it's from a different file
                if defining_file != file_path:
                    dependencies.append(f"{defining_file}:{call_name}")
        
        return dependencies
