"""
Tests for impact traverser service.
Validates BFS traversal and impact analysis on dependency graphs.
"""
import pytest
import networkx as nx
from backend.services.impact_traverser import ImpactTraverser


class TestImpactTraverser:
    """Test suite for ImpactTraverser."""
    
    @pytest.fixture
    def simple_graph(self):
        """Create a simple directed graph for testing."""
        graph = nx.DiGraph()
        
        # Create a chain: A -> B -> C -> D
        graph.add_node('A', name='func_a', file='file_a.py', type='function')
        graph.add_node('B', name='func_b', file='file_b.py', type='function')
        graph.add_node('C', name='func_c', file='file_c.py', type='function')
        graph.add_node('D', name='func_d', file='file_d.py', type='function')
        
        # Add edges (B depends on A, C depends on B, D depends on C)
        graph.add_edge('B', 'A')
        graph.add_edge('C', 'B')
        graph.add_edge('D', 'C')
        
        return graph
    
    @pytest.fixture
    def complex_graph(self):
        """Create a more complex graph with multiple paths."""
        graph = nx.DiGraph()
        
        # Create a diamond pattern:
        #     A
        #    / \
        #   B   C
        #    \ /
        #     D
        graph.add_node('A', name='func_a', file='file_a.py', type='function')
        graph.add_node('B', name='func_b', file='file_b.py', type='function')
        graph.add_node('C', name='func_c', file='file_c.py', type='function')
        graph.add_node('D', name='func_d', file='file_d.py', type='function')
        
        graph.add_edge('B', 'A')
        graph.add_edge('C', 'A')
        graph.add_edge('D', 'B')
        graph.add_edge('D', 'C')
        
        return graph
    
    def test_find_impacted_nodes_single_change(self, simple_graph):
        """Test finding impacted nodes from a single changed node."""
        traverser = ImpactTraverser(simple_graph)
        
        # Change node A, should impact B, C, D
        impacted = traverser.find_impacted_nodes(['A'])
        
        # Should include the changed node and all downstream
        assert 'A' in impacted
        assert 'B' in impacted
        assert 'C' in impacted
        assert 'D' in impacted
        assert len(impacted) == 4
    
    def test_find_impacted_nodes_middle_change(self, simple_graph):
        """Test finding impacted nodes from a middle node."""
        traverser = ImpactTraverser(simple_graph)
        
        # Change node B, should impact C and D but not A
        impacted = traverser.find_impacted_nodes(['B'])
        
        assert 'B' in impacted
        assert 'C' in impacted
        assert 'D' in impacted
        assert 'A' not in impacted
        assert len(impacted) == 3
    
    def test_find_impacted_nodes_leaf_change(self, simple_graph):
        """Test finding impacted nodes from a leaf node."""
        traverser = ImpactTraverser(simple_graph)
        
        # Change node D (leaf), should only impact itself
        impacted = traverser.find_impacted_nodes(['D'])
        
        assert 'D' in impacted
        assert len(impacted) == 1
    
    def test_find_impacted_nodes_multiple_changes(self, simple_graph):
        """Test finding impacted nodes from multiple changed nodes."""
        traverser = ImpactTraverser(simple_graph)
        
        # Change nodes A and C
        impacted = traverser.find_impacted_nodes(['A', 'C'])
        
        # Should include A, B, C, D
        assert 'A' in impacted
        assert 'B' in impacted
        assert 'C' in impacted
        assert 'D' in impacted
    
    def test_find_impacted_by_file(self, simple_graph):
        """Test finding impacted nodes by file path."""
        traverser = ImpactTraverser(simple_graph)
        
        # Change file_a.py (contains node A)
        impacted = traverser.find_impacted_by_file(['file_a.py'])
        
        # Should impact all nodes that depend on A
        assert len(impacted) >= 1
        
        # Check that nodes from file_a.py are included
        node_files = [simple_graph.nodes[n].get('file') for n in impacted]
        assert 'file_a.py' in node_files
    
    def test_calculate_impact_depth(self, simple_graph):
        """Test calculating depth of impact for each node."""
        traverser = ImpactTraverser(simple_graph)
        
        # Change node A
        depths = traverser.calculate_impact_depth(['A'])
        
        # A should be depth 0 (directly changed)
        assert depths['A'] == 0
        
        # B should be depth 1 (direct dependency)
        assert depths['B'] == 1
        
        # C should be depth 2
        assert depths['C'] == 2
        
        # D should be depth 3
        assert depths['D'] == 3
    
    def test_calculate_impact_depth_multiple_paths(self, complex_graph):
        """Test depth calculation with multiple paths."""
        traverser = ImpactTraverser(complex_graph)
        
        # Change node A
        depths = traverser.calculate_impact_depth(['A'])
        
        # A should be depth 0
        assert depths['A'] == 0
        
        # B and C should be depth 1
        assert depths['B'] == 1
        assert depths['C'] == 1
        
        # D should be depth 2 (shortest path from A)
        assert depths['D'] == 2
    
    def test_get_impact_paths(self, simple_graph):
        """Test finding paths between nodes."""
        traverser = ImpactTraverser(simple_graph)
        
        # Find paths from A to D
        paths = traverser.get_impact_paths('A', 'D', max_paths=5)
        
        # Should find at least one path
        assert len(paths) >= 1
        
        # Path should start with A and end with D
        if paths:
            assert paths[0][0] == 'A'
            assert paths[0][-1] == 'D'
    
    def test_get_impact_paths_no_path(self, simple_graph):
        """Test finding paths when no path exists."""
        traverser = ImpactTraverser(simple_graph)
        
        # Try to find path from D to A (reverse direction, should not exist)
        paths = traverser.get_impact_paths('D', 'A', max_paths=5)
        
        # Should return empty list
        assert paths == []
    
    def test_get_impact_summary(self, simple_graph):
        """Test getting comprehensive impact summary."""
        traverser = ImpactTraverser(simple_graph)
        
        # Get summary for file_a.py
        summary = traverser.get_impact_summary(['file_a.py'])
        
        # Check required fields
        assert 'total_changed_nodes' in summary
        assert 'total_impacted_nodes' in summary
        assert 'impacted_files' in summary
        assert 'impact_by_depth' in summary
        assert 'impact_by_type' in summary
        assert 'max_depth' in summary
        assert 'changed_nodes' in summary
        assert 'all_impacted_nodes' in summary
        
        # Check types
        assert isinstance(summary['total_changed_nodes'], int)
        assert isinstance(summary['total_impacted_nodes'], int)
        assert isinstance(summary['impacted_files'], list)
        assert isinstance(summary['impact_by_depth'], dict)
        assert isinstance(summary['impact_by_type'], dict)
        assert isinstance(summary['max_depth'], int)
    
    def test_get_impact_summary_multiple_files(self, simple_graph):
        """Test impact summary with multiple changed files."""
        traverser = ImpactTraverser(simple_graph)
        
        # Change multiple files
        summary = traverser.get_impact_summary(['file_a.py', 'file_b.py'])
        
        # Should have at least 2 changed nodes
        assert summary['total_changed_nodes'] >= 2
        
        # Should have impacted files
        assert len(summary['impacted_files']) >= 2
    
    def test_get_critical_impacts(self, complex_graph):
        """Test identifying critical node impacts."""
        traverser = ImpactTraverser(complex_graph)
        
        # Mark D as critical and change A
        critical_impacts = traverser.get_critical_impacts(['A'], ['D'])
        
        # Should identify that D is impacted
        assert len(critical_impacts) >= 1
        
        if critical_impacts:
            impact = critical_impacts[0]
            assert 'critical_node' in impact
            assert 'node_data' in impact
            assert 'affecting_changes' in impact
            assert impact['critical_node'] == 'D'
    
    def test_get_critical_impacts_no_impact(self, simple_graph):
        """Test critical impacts when critical node is not affected."""
        traverser = ImpactTraverser(simple_graph)
        
        # Mark A as critical and change D (D doesn't impact A)
        critical_impacts = traverser.get_critical_impacts(['D'], ['A'])
        
        # Should return empty list
        assert critical_impacts == []
    
    def test_empty_graph(self):
        """Test traverser with empty graph."""
        graph = nx.DiGraph()
        traverser = ImpactTraverser(graph)
        
        # Should handle empty graph gracefully
        impacted = traverser.find_impacted_nodes([])
        assert impacted == set()
        
        depths = traverser.calculate_impact_depth([])
        assert depths == {}
    
    def test_single_node_graph(self):
        """Test traverser with single node."""
        graph = nx.DiGraph()
        graph.add_node('A', name='func_a', file='file_a.py', type='function')
        
        traverser = ImpactTraverser(graph)
        
        # Change the only node
        impacted = traverser.find_impacted_nodes(['A'])
        
        assert 'A' in impacted
        assert len(impacted) == 1
    
    def test_disconnected_graph(self):
        """Test traverser with disconnected components."""
        graph = nx.DiGraph()
        
        # Create two disconnected components
        graph.add_node('A', name='func_a', file='file_a.py', type='function')
        graph.add_node('B', name='func_b', file='file_b.py', type='function')
        graph.add_node('C', name='func_c', file='file_c.py', type='function')
        graph.add_node('D', name='func_d', file='file_d.py', type='function')
        
        # Connect A-B and C-D separately
        graph.add_edge('B', 'A')
        graph.add_edge('D', 'C')
        
        traverser = ImpactTraverser(graph)
        
        # Change A should only impact A and B
        impacted = traverser.find_impacted_nodes(['A'])
        
        assert 'A' in impacted
        assert 'B' in impacted
        assert 'C' not in impacted
        assert 'D' not in impacted
    
    def test_cyclic_graph_handling(self):
        """Test that traverser handles cycles correctly."""
        graph = nx.DiGraph()
        
        # Create a cycle: A -> B -> C -> A
        graph.add_node('A', name='func_a', file='file_a.py', type='function')
        graph.add_node('B', name='func_b', file='file_b.py', type='function')
        graph.add_node('C', name='func_c', file='file_c.py', type='function')
        
        graph.add_edge('B', 'A')
        graph.add_edge('C', 'B')
        graph.add_edge('A', 'C')
        
        traverser = ImpactTraverser(graph)
        
        # Should handle cycle without infinite loop
        impacted = traverser.find_impacted_nodes(['A'])
        
        # Should include all nodes in the cycle
        assert 'A' in impacted
        assert 'B' in impacted
        assert 'C' in impacted
        assert len(impacted) == 3

# Made with Bob
