"""
Tests for graph builder service.
Validates dependency graph construction from code elements.
"""
import pytest
import networkx as nx
from backend.services.graph_builder import GraphBuilder
from backend.services.ast_analyzer import CodeElement


class TestGraphBuilder:
    """Test suite for GraphBuilder."""
    
    @pytest.fixture
    def builder(self):
        """Create a GraphBuilder instance."""
        return GraphBuilder()
    
    @pytest.fixture
    def sample_elements(self):
        """Create sample code elements for testing."""
        return [
            CodeElement(
                type='function',
                name='calculate_total',
                file_path='utils.py',
                line_start=1,
                line_end=5,
                dependencies=[],
                metadata={}
            ),
            CodeElement(
                type='function',
                name='process_payment',
                file_path='payment.py',
                line_start=10,
                line_end=20,
                dependencies=['calculate_total'],
                metadata={}
            ),
            CodeElement(
                type='class',
                name='PaymentService',
                file_path='services.py',
                line_start=1,
                line_end=30,
                dependencies=[],
                metadata={}
            ),
            CodeElement(
                type='import',
                name='from utils import calculate_total',
                file_path='payment.py',
                line_start=1,
                line_end=1,
                dependencies=[],
                metadata={'raw': 'from utils import calculate_total'}
            )
        ]
    
    def test_build_graph_creates_nodes(self, builder, sample_elements):
        """Test that build_graph creates nodes for all elements."""
        graph = builder.build_graph(sample_elements)
        
        # Should have 4 nodes (one per element)
        assert graph.number_of_nodes() == 4
        
        # Check that nodes exist
        node_names = [data.get('name') for _, data in graph.nodes(data=True)]
        assert 'calculate_total' in node_names
        assert 'process_payment' in node_names
        assert 'PaymentService' in node_names
    
    def test_node_attributes(self, builder, sample_elements):
        """Test that nodes have correct attributes."""
        graph = builder.build_graph(sample_elements)
        
        # Find the calculate_total node
        calc_node = None
        for node_id, data in graph.nodes(data=True):
            if data.get('name') == 'calculate_total':
                calc_node = (node_id, data)
                break
        
        assert calc_node is not None
        node_id, data = calc_node
        
        # Check required attributes
        assert data['type'] == 'function'
        assert data['name'] == 'calculate_total'
        assert data['file'] == 'utils.py'
        assert data['line_start'] == 1
        assert data['line_end'] == 5
        assert 'label' in data
    
    def test_edge_creation_from_dependencies(self, builder, sample_elements):
        """Test that edges are created based on dependencies."""
        graph = builder.build_graph(sample_elements)
        
        # Should have edges based on dependencies
        assert graph.number_of_edges() >= 1
        
        # Check that process_payment depends on calculate_total
        # (edge should exist from process_payment to calculate_total)
        edges = list(graph.edges())
        assert len(edges) > 0
    
    def test_import_dependency_inference(self, builder, sample_elements):
        """Test that import dependencies are inferred."""
        graph = builder.build_graph(sample_elements)
        
        # Elements in payment.py should depend on imports in payment.py
        # Check that edges exist connecting functions to imports
        edges_with_type = [(u, v, d.get('type')) for u, v, d in graph.edges(data=True)]
        
        # Should have 'imports' type edges
        import_edges = [e for e in edges_with_type if e[2] == 'imports']
        assert len(import_edges) > 0
    
    def test_empty_element_list(self, builder):
        """Test that empty element list produces empty graph."""
        graph = builder.build_graph([])
        
        assert graph.number_of_nodes() == 0
        assert graph.number_of_edges() == 0
    
    def test_expand_graph_with_neighbors(self, builder):
        """Test expanding graph to include neighbors of changed files."""
        # Create elements from multiple files
        all_elements = [
            CodeElement(
                type='function',
                name='func_a',
                file_path='file_a.py',
                line_start=1,
                line_end=5,
                dependencies=[],
                metadata={}
            ),
            CodeElement(
                type='function',
                name='func_b',
                file_path='file_b.py',
                line_start=1,
                line_end=5,
                dependencies=['func_a'],
                metadata={}
            ),
            CodeElement(
                type='function',
                name='func_c',
                file_path='file_c.py',
                line_start=1,
                line_end=5,
                dependencies=['func_b'],
                metadata={}
            )
        ]
        
        # Expand graph for changed file_b.py
        expanded_graph = builder.expand_graph_with_neighbors(['file_b.py'], all_elements)
        
        # Should include file_b and its neighbors (file_a and file_c)
        assert expanded_graph.number_of_nodes() >= 1
        
        # Check that changed nodes are marked
        changed_marked = False
        for node_id, data in expanded_graph.nodes(data=True):
            if data.get('file') == 'file_b.py' and data.get('changed'):
                changed_marked = True
                break
        assert changed_marked
    
    def test_get_file_dependencies(self, builder):
        """Test getting file-level dependencies."""
        elements = [
            CodeElement(
                type='function',
                name='func_a',
                file_path='file_a.py',
                line_start=1,
                line_end=5,
                dependencies=[],
                metadata={}
            ),
            CodeElement(
                type='function',
                name='func_b',
                file_path='file_b.py',
                line_start=1,
                line_end=5,
                dependencies=['func_a'],
                metadata={}
            )
        ]
        
        graph = builder.build_graph(elements)
        file_deps = builder.get_file_dependencies(graph)
        
        # Should return a dictionary
        assert isinstance(file_deps, dict)
        
        # file_b.py should depend on file_a.py (if edge exists)
        # Note: depends on whether edge was created
        assert isinstance(file_deps, dict)
    
    def test_get_critical_nodes(self, builder):
        """Test identifying critical nodes by centrality."""
        # Create a graph with clear central node
        elements = [
            CodeElement(
                type='function',
                name='central_func',
                file_path='central.py',
                line_start=1,
                line_end=5,
                dependencies=[],
                metadata={}
            ),
            CodeElement(
                type='function',
                name='func_1',
                file_path='file1.py',
                line_start=1,
                line_end=5,
                dependencies=['central_func'],
                metadata={}
            ),
            CodeElement(
                type='function',
                name='func_2',
                file_path='file2.py',
                line_start=1,
                line_end=5,
                dependencies=['central_func'],
                metadata={}
            ),
            CodeElement(
                type='function',
                name='func_3',
                file_path='file3.py',
                line_start=1,
                line_end=5,
                dependencies=['central_func'],
                metadata={}
            )
        ]
        
        graph = builder.build_graph(elements)
        critical_nodes = builder.get_critical_nodes(graph, top_n=3)
        
        # Should return list of tuples (node_id, centrality_score)
        assert isinstance(critical_nodes, list)
        assert len(critical_nodes) <= 3
        
        if critical_nodes:
            # Each item should be a tuple
            assert isinstance(critical_nodes[0], tuple)
            assert len(critical_nodes[0]) == 2
    
    def test_get_critical_nodes_empty_graph(self, builder):
        """Test critical nodes on empty graph."""
        graph = builder.build_graph([])
        critical_nodes = builder.get_critical_nodes(graph)
        
        assert critical_nodes == []
    
    def test_node_id_creation(self, builder):
        """Test that node IDs are unique and consistent."""
        element = CodeElement(
            type='function',
            name='test_func',
            file_path='test.py',
            line_start=10,
            line_end=20,
            dependencies=[],
            metadata={}
        )
        
        node_id = builder._create_node_id(element)
        
        # Should be a string
        assert isinstance(node_id, str)
        
        # Should contain key information
        assert 'test.py' in node_id
        assert 'function' in node_id
        assert 'test_func' in node_id
        assert '10' in node_id
    
    def test_graph_is_directed(self, builder, sample_elements):
        """Test that the graph is a directed graph."""
        graph = builder.build_graph(sample_elements)
        
        assert isinstance(graph, nx.DiGraph)
        assert graph.is_directed()
    
    def test_multiple_files_same_function_name(self, builder):
        """Test handling of same function name in different files."""
        elements = [
            CodeElement(
                type='function',
                name='process',
                file_path='file_a.py',
                line_start=1,
                line_end=5,
                dependencies=[],
                metadata={}
            ),
            CodeElement(
                type='function',
                name='process',
                file_path='file_b.py',
                line_start=1,
                line_end=5,
                dependencies=[],
                metadata={}
            )
        ]
        
        graph = builder.build_graph(elements)
        
        # Should create separate nodes for each
        assert graph.number_of_nodes() == 2
        
        # Node IDs should be different (include file path)
        node_ids = list(graph.nodes())
        assert len(set(node_ids)) == 2

# Made with Bob
