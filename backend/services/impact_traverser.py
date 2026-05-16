"""
Impact traverser for analyzing downstream effects of code changes.
Uses graph traversal to identify all components affected by changes.
"""
import networkx as nx
from typing import List, Set, Dict, Any
from collections import deque


class ImpactTraverser:
    """Traverser for identifying impact of code changes."""
    
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph
    
    def find_impacted_nodes(self, changed_nodes: List[str]) -> Set[str]:
        """
        Find all nodes impacted by changes to the given nodes.
        Uses BFS to traverse the dependency graph.
        
        Graph convention: edge B→A means "B depends on A"
        So when A changes, we find nodes that point TO A (predecessors)
        
        Args:
            changed_nodes: List of node IDs that were changed
            
        Returns:
            Set of all impacted node IDs (including changed nodes)
        """
        impacted = set(changed_nodes)
        
        # BFS traversal to find all downstream dependencies
        queue = deque(changed_nodes)
        visited = set(changed_nodes)
        
        while queue:
            current = queue.popleft()
            
            # Get all nodes that depend on the current node (predecessors in this graph convention)
            for predecessor in self.graph.predecessors(current):
                if predecessor not in visited:
                    visited.add(predecessor)
                    impacted.add(predecessor)
                    queue.append(predecessor)
        
        return impacted
    
    def find_impacted_by_file(self, changed_files: List[str]) -> Set[str]:
        """
        Find all nodes impacted by changes to specific files.
        
        Args:
            changed_files: List of file paths that were changed
            
        Returns:
            Set of impacted node IDs
        """
        # Find all nodes in changed files
        changed_nodes = []
        for node_id, data in self.graph.nodes(data=True):
            if data.get('file') in changed_files:
                changed_nodes.append(node_id)
        
        return self.find_impacted_nodes(changed_nodes)
    
    def calculate_impact_depth(self, changed_nodes: List[str]) -> Dict[str, int]:
        """
        Calculate the depth of impact for each affected node.
        Depth 0 = directly changed, depth 1 = direct dependency, etc.
        
        Args:
            changed_nodes: List of node IDs that were changed
            
        Returns:
            Dictionary mapping node IDs to their impact depth
        """
        depths = {}
        
        # Initialize changed nodes with depth 0
        for node in changed_nodes:
            depths[node] = 0
        
        # BFS with depth tracking
        queue = deque([(node, 0) for node in changed_nodes])
        visited = set(changed_nodes)
        
        while queue:
            current, depth = queue.popleft()
            
            # Get all nodes that depend on the current node (predecessors in this graph convention)
            for predecessor in self.graph.predecessors(current):
                if predecessor not in visited:
                    visited.add(predecessor)
                    depths[predecessor] = depth + 1
                    queue.append((predecessor, depth + 1))
        
        return depths
    
    def get_impact_paths(
        self,
        source_node: str,
        target_node: str,
        max_paths: int = 5
    ) -> List[List[str]]:
        """
        Find paths from a changed node to an impacted node.
        
        Graph convention: edge B→A means "B depends on A"
        To find impact paths from A to B, we need to reverse the graph
        because nx.all_simple_paths follows edge direction.
        
        Args:
            source_node: Changed node ID
            target_node: Impacted node ID
            max_paths: Maximum number of paths to return
            
        Returns:
            List of paths (each path is a list of node IDs)
        """
        try:
            # Reverse the graph to follow impact direction
            # In original: B→A (B depends on A)
            # In reversed: A→B (A impacts B)
            reversed_graph = self.graph.reverse()
            
            # Find all simple paths (no cycles)
            paths = list(nx.all_simple_paths(
                reversed_graph,
                source=source_node,
                target=target_node,
                cutoff=10  # Limit path length to avoid infinite loops
            ))
            return paths[:max_paths]
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []
    
    def get_impact_summary(self, changed_files: List[str]) -> Dict[str, Any]:
        """
        Get a comprehensive summary of the impact analysis.
        
        Args:
            changed_files: List of file paths that were changed
            
        Returns:
            Dictionary with impact analysis summary
        """
        # Find changed nodes
        changed_nodes = []
        for node_id, data in self.graph.nodes(data=True):
            if data.get('file') in changed_files:
                changed_nodes.append(node_id)
        
        # Find all impacted nodes
        impacted_nodes = self.find_impacted_nodes(changed_nodes)
        
        # Calculate depths
        depths = self.calculate_impact_depth(changed_nodes)
        
        # Group by depth
        by_depth: Dict[int, List[str]] = {}
        for node, depth in depths.items():
            if depth not in by_depth:
                by_depth[depth] = []
            by_depth[depth].append(node)
        
        # Group by file
        impacted_files = set()
        for node in impacted_nodes:
            file_path = self.graph.nodes[node].get('file')
            if file_path:
                impacted_files.add(file_path)
        
        # Group by type
        by_type: Dict[str, int] = {}
        for node in impacted_nodes:
            node_type = self.graph.nodes[node].get('type', 'unknown')
            by_type[node_type] = by_type.get(node_type, 0) + 1
        
        return {
            'total_changed_nodes': len(changed_nodes),
            'total_impacted_nodes': len(impacted_nodes),
            'impacted_files': list(impacted_files),
            'impact_by_depth': {str(k): len(v) for k, v in by_depth.items()},
            'impact_by_type': by_type,
            'max_depth': max(depths.values()) if depths else 0,
            'changed_nodes': changed_nodes,
            'all_impacted_nodes': list(impacted_nodes)
        }
    
    def get_critical_impacts(
        self, 
        changed_nodes: List[str], 
        critical_nodes: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Identify if any critical nodes are impacted by the changes.
        
        Args:
            changed_nodes: List of changed node IDs
            critical_nodes: List of critical node IDs (e.g., from centrality analysis)
            
        Returns:
            List of critical impacts with path information
        """
        impacted = self.find_impacted_nodes(changed_nodes)
        critical_impacts = []
        
        for critical_node in critical_nodes:
            if critical_node in impacted:
                # Find which changed node(s) impact this critical node
                affecting_changes = []
                for changed_node in changed_nodes:
                    paths = self.get_impact_paths(changed_node, critical_node, max_paths=1)
                    if paths:
                        affecting_changes.append({
                            'changed_node': changed_node,
                            'path': paths[0]
                        })
                
                if affecting_changes:
                    critical_impacts.append({
                        'critical_node': critical_node,
                        'node_data': self.graph.nodes[critical_node],
                        'affecting_changes': affecting_changes
                    })
        
        return critical_impacts

# Made with Bob
