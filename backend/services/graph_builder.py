"""
Dependency graph builder using NetworkX.
Constructs a directed graph of code dependencies from AST analysis.
"""
import networkx as nx
from typing import List, Dict, Set
from backend.services.ast_analyzer import CodeElement


class GraphBuilder:
    """Builder for constructing dependency graphs."""
    
    def __init__(self):
        self.graph = nx.DiGraph()
    
    def build_graph(self, elements: List[CodeElement]) -> nx.DiGraph:
        """
        Build a dependency graph from code elements.
        
        Args:
            elements: List of CodeElement objects from AST analysis
            
        Returns:
            NetworkX directed graph
        """
        # Reset graph
        self.graph = nx.DiGraph()
        
        # Add nodes for all elements
        for element in elements:
            node_id = self._create_node_id(element)
            self.graph.add_node(
                node_id,
                type=element.type,
                name=element.name,
                file=element.file_path,
                line_start=element.line_start,
                line_end=element.line_end,
                label=f"{element.name} ({element.type})",
                metadata=element.metadata
            )
        
        # Add edges based on dependencies
        for element in elements:
            source_id = self._create_node_id(element)
            
            # Add edges for explicit dependencies
            for dep_name in element.dependencies:
                # Find matching node
                target_id = self._find_node_by_name(dep_name)
                if target_id:
                    self.graph.add_edge(
                        source_id,
                        target_id,
                        type='depends_on'
                    )
        
        # Infer additional dependencies from imports
        self._infer_import_dependencies(elements)
        
        return self.graph
    
    def _create_node_id(self, element: CodeElement) -> str:
        """Create a unique node ID for a code element."""
        # Format: file_path:element_type:element_name:line
        return f"{element.file_path}:{element.type}:{element.name}:{element.line_start}"
    
    def _find_node_by_name(self, name: str) -> str:
        """Find a node ID by element name."""
        for node_id, data in self.graph.nodes(data=True):
            if data.get('name') == name:
                return node_id
        return None
    
    def _infer_import_dependencies(self, elements: List[CodeElement]):
        """Infer dependencies from import statements."""
        # Group elements by file
        files_map: Dict[str, List[CodeElement]] = {}
        for element in elements:
            if element.file_path not in files_map:
                files_map[element.file_path] = []
            files_map[element.file_path].append(element)
        
        # For each file, connect imports to functions/classes in the same file
        for file_path, file_elements in files_map.items():
            imports = [e for e in file_elements if e.type == 'import']
            non_imports = [e for e in file_elements if e.type != 'import']
            
            # Simple heuristic: functions/classes in a file depend on imports in that file
            for imp in imports:
                import_id = self._create_node_id(imp)
                for elem in non_imports:
                    elem_id = self._create_node_id(elem)
                    # Add edge from element to import (element depends on import)
                    if not self.graph.has_edge(elem_id, import_id):
                        self.graph.add_edge(
                            elem_id,
                            import_id,
                            type='imports'
                        )
    
    def expand_graph_with_neighbors(
        self, 
        changed_files: List[str], 
        all_elements: List[CodeElement]
    ) -> nx.DiGraph:
        """
        Expand graph to include neighbors of changed files.
        
        Args:
            changed_files: List of file paths that were changed
            all_elements: All code elements from the repository
            
        Returns:
            Expanded NetworkX directed graph
        """
        # Build full graph
        full_graph = self.build_graph(all_elements)
        
        # Find nodes in changed files
        changed_nodes = set()
        for node_id, data in full_graph.nodes(data=True):
            if data.get('file') in changed_files:
                changed_nodes.add(node_id)
        
        # Expand to include immediate neighbors (1-hop)
        expanded_nodes = set(changed_nodes)
        for node in changed_nodes:
            # Add predecessors (nodes that depend on this node)
            expanded_nodes.update(full_graph.predecessors(node))
            # Add successors (nodes this node depends on)
            expanded_nodes.update(full_graph.successors(node))
        
        # Create subgraph with expanded nodes
        subgraph = full_graph.subgraph(expanded_nodes).copy()
        
        # Mark changed nodes
        for node in changed_nodes:
            if node in subgraph:
                subgraph.nodes[node]['changed'] = True
        
        return subgraph
    
    def get_file_dependencies(self, graph: nx.DiGraph) -> Dict[str, Set[str]]:
        """
        Get file-level dependencies from the graph.
        
        Args:
            graph: NetworkX directed graph
            
        Returns:
            Dictionary mapping file paths to sets of dependent file paths
        """
        file_deps: Dict[str, Set[str]] = {}
        
        for source, target in graph.edges():
            source_file = graph.nodes[source].get('file')
            target_file = graph.nodes[target].get('file')
            
            if source_file and target_file and source_file != target_file:
                if source_file not in file_deps:
                    file_deps[source_file] = set()
                file_deps[source_file].add(target_file)
        
        return file_deps
    
    def get_critical_nodes(self, graph: nx.DiGraph, top_n: int = 10) -> List[tuple]:
        """
        Identify critical nodes based on centrality measures.
        
        Args:
            graph: NetworkX directed graph
            top_n: Number of top critical nodes to return
            
        Returns:
            List of (node_id, centrality_score) tuples
        """
        if graph.number_of_nodes() == 0:
            return []
        
        # Calculate betweenness centrality (nodes that are on many paths)
        try:
            centrality = nx.betweenness_centrality(graph)
            sorted_nodes = sorted(
                centrality.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            return sorted_nodes[:top_n]
        except:
            # Fallback to degree centrality if betweenness fails
            centrality = nx.degree_centrality(graph)
            sorted_nodes = sorted(
                centrality.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            return sorted_nodes[:top_n]

# Made with Bob
