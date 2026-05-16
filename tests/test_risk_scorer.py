"""
Tests for risk scorer service.
Validates risk score calculation based on multiple factors.
"""
import pytest
import networkx as nx
from backend.services.risk_scorer import RiskScorer
from backend.utils.diff_parser import FileChange


def create_file_change(file_path: str, additions: int = 10, deletions: int = 5) -> FileChange:
    """Helper to create FileChange with all required parameters."""
    return FileChange(
        file_path=file_path,
        old_path=file_path,
        new_path=file_path,
        change_type='modified',
        additions=additions,
        deletions=deletions,
        changed_lines=list(range(1, additions + 1))
    )


class TestRiskScorer:
    """Test suite for RiskScorer."""
    
    @pytest.fixture
    def scorer(self):
        """Create a RiskScorer instance."""
        return RiskScorer()
    
    @pytest.fixture
    def sample_file_changes(self):
        """Create sample file changes for testing."""
        return [
            FileChange(
                file_path='src/payment.py',
                old_path='src/payment.py',
                new_path='src/payment.py',
                change_type='modified',
                additions=50,
                deletions=20,
                changed_lines=list(range(1, 51))
            ),
            FileChange(
                file_path='src/utils.py',
                old_path='src/utils.py',
                new_path='src/utils.py',
                change_type='modified',
                additions=10,
                deletions=5,
                changed_lines=list(range(1, 11))
            )
        ]
    
    @pytest.fixture
    def sample_graph(self):
        """Create a sample graph for testing."""
        graph = nx.DiGraph()
        
        # Create nodes
        for i in range(10):
            graph.add_node(f'node_{i}', name=f'func_{i}', type='function')
        
        # Create edges (dependencies)
        graph.add_edge('node_1', 'node_0')
        graph.add_edge('node_2', 'node_0')
        graph.add_edge('node_3', 'node_1')
        graph.add_edge('node_4', 'node_1')
        graph.add_edge('node_5', 'node_2')
        
        return graph
    
    def test_calculate_risk_score_returns_dict(self, scorer, sample_file_changes, sample_graph):
        """Test that calculate_risk_score returns proper structure."""
        result = scorer.calculate_risk_score(
            file_changes=sample_file_changes,
            graph=sample_graph,
            impacted_nodes=['node_0', 'node_1', 'node_2'],
            changed_nodes=['node_0']
        )
        
        # Check structure
        assert isinstance(result, dict)
        assert 'risk_score' in result
        assert 'risk_level' in result
        assert 'risk_factors' in result
        
        # Check types
        assert isinstance(result['risk_score'], (int, float))
        assert isinstance(result['risk_level'], str)
        assert isinstance(result['risk_factors'], dict)
    
    def test_risk_score_range(self, scorer, sample_file_changes, sample_graph):
        """Test that risk score is within valid range (0-100)."""
        result = scorer.calculate_risk_score(
            file_changes=sample_file_changes,
            graph=sample_graph,
            impacted_nodes=['node_0', 'node_1'],
            changed_nodes=['node_0']
        )
        
        assert 0 <= result['risk_score'] <= 100
    
    def test_risk_level_low(self, scorer):
        """Test LOW risk level classification (0-33)."""
        level = scorer._determine_risk_level(0)
        assert level == 'LOW'
        
        level = scorer._determine_risk_level(33)
        assert level == 'LOW'
        
        level = scorer._determine_risk_level(20)
        assert level == 'LOW'
    
    def test_risk_level_medium(self, scorer):
        """Test MEDIUM risk level classification (34-66)."""
        level = scorer._determine_risk_level(34)
        assert level == 'MEDIUM'
        
        level = scorer._determine_risk_level(66)
        assert level == 'MEDIUM'
        
        level = scorer._determine_risk_level(50)
        assert level == 'MEDIUM'
    
    def test_risk_level_high(self, scorer):
        """Test HIGH risk level classification (67-100)."""
        level = scorer._determine_risk_level(67)
        assert level == 'HIGH'
        
        level = scorer._determine_risk_level(100)
        assert level == 'HIGH'
        
        level = scorer._determine_risk_level(85)
        assert level == 'HIGH'
    
    def test_complexity_score_empty_changes(self, scorer):
        """Test complexity score with no file changes."""
        score = scorer._calculate_complexity_score([])
        
        assert score == 0.0
    
    def test_complexity_score_single_file(self, scorer):
        """Test complexity score with single file change."""
        changes = [create_file_change('test.py', 10, 5)]
        
        score = scorer._calculate_complexity_score(changes)
        
        # Should be greater than 0
        assert score > 0
        assert score <= 100
    
    def test_complexity_score_multiple_files(self, scorer):
        """Test complexity score increases with more files."""
        single_file = [create_file_change('test1.py', 10, 5)]
        
        multiple_files = [
            create_file_change('test1.py', 10, 5),
            create_file_change('test2.py', 10, 5),
            create_file_change('test3.py', 10, 5)
        ]
        
        score_single = scorer._calculate_complexity_score(single_file)
        score_multiple = scorer._calculate_complexity_score(multiple_files)
        
        # More files should result in higher score
        assert score_multiple > score_single
    
    def test_complexity_score_large_changes(self, scorer):
        """Test complexity score increases with larger changes."""
        small_change = [create_file_change('test.py', 5, 2)]
        
        large_change = [create_file_change('test.py', 100, 50)]
        
        score_small = scorer._calculate_complexity_score(small_change)
        score_large = scorer._calculate_complexity_score(large_change)
        
        # Larger changes should result in higher score
        assert score_large > score_small
    
    def test_impact_scope_score_empty_graph(self, scorer):
        """Test impact scope score with empty graph."""
        graph = nx.DiGraph()
        
        score = scorer._calculate_impact_scope_score(graph, [], [])
        
        assert score == 0.0
    
    def test_impact_scope_score_increases_with_impact(self, scorer, sample_graph):
        """Test that impact scope score increases with more impacted nodes."""
        # Small impact
        score_small = scorer._calculate_impact_scope_score(
            sample_graph,
            impacted_nodes=['node_0', 'node_1'],
            changed_nodes=['node_0']
        )
        
        # Large impact
        score_large = scorer._calculate_impact_scope_score(
            sample_graph,
            impacted_nodes=['node_0', 'node_1', 'node_2', 'node_3', 'node_4'],
            changed_nodes=['node_0']
        )
        
        # More impacted nodes should result in higher score
        assert score_large > score_small
    
    def test_criticality_score_empty_graph(self, scorer):
        """Test criticality score with empty graph."""
        graph = nx.DiGraph()
        
        score = scorer._calculate_criticality_score(graph, [])
        
        assert score == 0.0
    
    def test_criticality_score_with_nodes(self, scorer, sample_graph):
        """Test criticality score calculation with nodes."""
        score = scorer._calculate_criticality_score(
            sample_graph,
            changed_nodes=['node_0']
        )
        
        # Should return a valid score
        assert isinstance(score, float)
        assert 0 <= score <= 100
    
    def test_test_coverage_score_no_changes(self, scorer):
        """Test coverage score with no changes."""
        score = scorer._estimate_test_coverage_score([])
        
        assert score == 0.0
    
    def test_test_coverage_score_no_tests(self, scorer):
        """Test coverage score when no test files are changed."""
        changes = [
            create_file_change('src/payment.py', 50, 20),
            create_file_change('src/utils.py', 10, 5)
        ]
        
        score = scorer._estimate_test_coverage_score(changes)
        
        # No test files = higher risk
        assert score > 50
    
    def test_test_coverage_score_with_tests(self, scorer):
        """Test coverage score when test files are changed."""
        changes = [
            create_file_change('src/payment.py', 50, 20),
            create_file_change('tests/test_payment.py', 30, 10)
        ]
        
        score = scorer._estimate_test_coverage_score(changes)
        
        # With test files = lower risk
        assert score < 80
    
    def test_risk_factors_breakdown(self, scorer, sample_file_changes, sample_graph):
        """Test that risk factors are properly broken down."""
        result = scorer.calculate_risk_score(
            file_changes=sample_file_changes,
            graph=sample_graph,
            impacted_nodes=['node_0', 'node_1', 'node_2'],
            changed_nodes=['node_0']
        )
        
        factors = result['risk_factors']
        
        # Check all factors are present
        assert 'complexity_score' in factors
        assert 'impact_scope' in factors
        assert 'criticality' in factors
        assert 'test_coverage' in factors
        
        # Check all are numeric
        for key, value in factors.items():
            assert isinstance(value, (int, float))
            assert 0 <= value <= 100
    
    def test_weighted_scoring(self, scorer):
        """Test that weights are properly applied."""
        # Verify weights sum to 1.0
        total_weight = sum(scorer.weights.values())
        assert abs(total_weight - 1.0) < 0.01
    
    def test_edge_case_single_node_graph(self, scorer):
        """Test with single node graph."""
        graph = nx.DiGraph()
        graph.add_node('node_0', name='func_0', type='function')
        
        changes = [create_file_change('test.py', 10, 5)]
        
        result = scorer.calculate_risk_score(
            file_changes=changes,
            graph=graph,
            impacted_nodes=['node_0'],
            changed_nodes=['node_0']
        )
        
        # Should handle gracefully
        assert 'risk_score' in result
        assert 0 <= result['risk_score'] <= 100
    
    def test_edge_case_zero_changes(self, scorer, sample_graph):
        """Test with zero file changes."""
        result = scorer.calculate_risk_score(
            file_changes=[],
            graph=sample_graph,
            impacted_nodes=['node_0'],
            changed_nodes=['node_0']
        )
        
        # Should handle gracefully
        assert 'risk_score' in result
        # Score should be low with no changes
        assert result['risk_score'] < 50
    
    def test_edge_case_no_impacted_nodes(self, scorer, sample_file_changes, sample_graph):
        """Test with no impacted nodes."""
        result = scorer.calculate_risk_score(
            file_changes=sample_file_changes,
            graph=sample_graph,
            impacted_nodes=[],
            changed_nodes=[]
        )
        
        # Should handle gracefully
        assert 'risk_score' in result
        assert result['risk_score'] >= 0
    
    def test_high_risk_scenario(self, scorer):
        """Test a scenario that should produce high risk."""
        # Many files, large changes, many impacted nodes
        graph = nx.DiGraph()
        for i in range(50):
            graph.add_node(f'node_{i}', name=f'func_{i}', type='function')
            if i > 0:
                graph.add_edge(f'node_{i}', f'node_{i-1}')
        
        changes = [
            create_file_change(f'file_{i}.py', 100, 50)
            for i in range(10)
        ]
        
        result = scorer.calculate_risk_score(
            file_changes=changes,
            graph=graph,
            impacted_nodes=[f'node_{i}' for i in range(30)],
            changed_nodes=['node_0']
        )
        
        # Should produce high risk
        assert result['risk_score'] > 50
        assert result['risk_level'] in ['MEDIUM', 'HIGH']
    
    def test_low_risk_scenario(self, scorer):
        """Test a scenario that should produce low risk."""
        # Single small change, few impacted nodes
        graph = nx.DiGraph()
        graph.add_node('node_0', name='func_0', type='function')
        graph.add_node('node_1', name='func_1', type='function')
        
        changes = [create_file_change('test.py', 2, 1)]
        
        result = scorer.calculate_risk_score(
            file_changes=changes,
            graph=graph,
            impacted_nodes=['node_0'],
            changed_nodes=['node_0']
        )
        
        # Should produce low risk
        assert result['risk_score'] < 50
        assert result['risk_level'] in ['LOW', 'MEDIUM']
    
    def test_3_tier_system_alignment(self, scorer):
        """Test that risk levels align with 3-tier system from TECH SPEC."""
        # Test boundary values
        assert scorer._determine_risk_level(0) == 'LOW'
        assert scorer._determine_risk_level(33) == 'LOW'
        assert scorer._determine_risk_level(34) == 'MEDIUM'
        assert scorer._determine_risk_level(66) == 'MEDIUM'
        assert scorer._determine_risk_level(67) == 'HIGH'
        assert scorer._determine_risk_level(100) == 'HIGH'
        
        # Ensure no CRITICAL level exists
        for score in [75, 80, 90, 95, 100]:
            level = scorer._determine_risk_level(score)
            assert level != 'CRITICAL'
            assert level == 'HIGH'

# Made with Bob
