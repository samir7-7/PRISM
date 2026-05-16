"""
Serializer for NetworkX graphs to/from JSON format.
Enables storage and transmission of dependency graphs.
"""
import json
import networkx as nx
from typing import Dict, Any


class GraphSerializer:
    """Serializer for NetworkX graphs."""
    
    @staticmethod
    def serialize(graph: nx.DiGraph) -> str:
        """
        Serialize a NetworkX directed graph to JSON string.
        
        Args:
            graph: NetworkX DiGraph object
            
        Returns:
            JSON string representation of the graph
        """
        # Convert graph to node-link format (suitable for JSON)
        data = nx.node_link_data(graph)
        return json.dumps(data, indent=2)
    
    @staticmethod
    def deserialize(json_str: str) -> nx.DiGraph:
        """
        Deserialize a JSON string to NetworkX directed graph.
        
        Args:
            json_str: JSON string representation of the graph
            
        Returns:
            NetworkX DiGraph object
        """
        data = json.loads(json_str)
        return nx.node_link_graph(data, directed=True)
    
    @staticmethod
    def to_dict(graph: nx.DiGraph) -> Dict[str, Any]:
        """
        Convert graph to dictionary format.
        
        Args:
            graph: NetworkX DiGraph object
            
        Returns:
            Dictionary representation of the graph
        """
        return nx.node_link_data(graph)
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> nx.DiGraph:
        """
        Create graph from dictionary format.
        
        Args:
            data: Dictionary representation of the graph
            
        Returns:
            NetworkX DiGraph object
        """
        return nx.node_link_graph(data, directed=True)
    
    @staticmethod
    def get_graph_stats(graph: nx.DiGraph) -> Dict[str, Any]:
        """
        Get statistics about the graph.
        
        Args:
            graph: NetworkX DiGraph object
            
        Returns:
            Dictionary with graph statistics
        """
        return {
            'num_nodes': graph.number_of_nodes(),
            'num_edges': graph.number_of_edges(),
            'is_directed': graph.is_directed(),
            'is_connected': nx.is_weakly_connected(graph) if graph.number_of_nodes() > 0 else False,
            'density': nx.density(graph) if graph.number_of_nodes() > 0 else 0.0
        }
    
    @staticmethod
    def export_for_visualization(graph: nx.DiGraph) -> Dict[str, Any]:
        """
        Export graph in format suitable for frontend visualization.
        
        Args:
            graph: NetworkX DiGraph object
            
        Returns:
            Dictionary with nodes and edges arrays for visualization
        """
        nodes = []
        for node_id, node_data in graph.nodes(data=True):
            nodes.append({
                'id': node_id,
                'label': node_data.get('label', node_id),
                'type': node_data.get('type', 'unknown'),
                'file': node_data.get('file', ''),
                'line': node_data.get('line', 0),
                **{k: v for k, v in node_data.items() if k not in ['label', 'type', 'file', 'line']}
            })
        
        edges = []
        for source, target, edge_data in graph.edges(data=True):
            edges.append({
                'source': source,
                'target': target,
                'type': edge_data.get('type', 'depends_on'),
                **{k: v for k, v in edge_data.items() if k != 'type'}
            })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'stats': GraphSerializer.get_graph_stats(graph)
        }

# Made with Bob
