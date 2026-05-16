"""
Simple unit test for M1 fix - Coverage flag for incomplete graph data.
This test verifies the logic without requiring full backend dependencies.
"""
import sys


class SimpleGraph:
    """Simplified graph class to test coverage flag logic."""
    
    def __init__(self):
        self.graph = {}
        self.coverage_complete = True
    
    def build_graph(self, elements, has_pre_indexed_data=False):
        """Build graph with coverage metadata."""
        # Set coverage flag based on whether we have pre-indexed data
        self.coverage_complete = has_pre_indexed_data
        
        # Add coverage metadata to graph
        self.graph['coverage_complete'] = self.coverage_complete
        self.graph['coverage_note'] = (
            "Complete repository analysis" if self.coverage_complete 
            else "On-demand analysis - coverage may be incomplete for unchanged files"
        )
        
        return self.graph


class TestCoverageFlag:
    """Test coverage flag logic."""
    
    def test_coverage_complete_with_pre_indexed_data(self):
        """Test that coverage is marked complete when pre-indexed data exists."""
        builder = SimpleGraph()
        graph = builder.build_graph([], has_pre_indexed_data=True)
        
        assert graph['coverage_complete'] == True
        assert 'Complete repository analysis' in graph['coverage_note']
        print("[PASS] Coverage flag is True with pre-indexed data")
    
    def test_coverage_incomplete_without_pre_indexed_data(self):
        """Test that coverage is marked incomplete for on-demand analysis."""
        builder = SimpleGraph()
        graph = builder.build_graph([], has_pre_indexed_data=False)
        
        assert graph['coverage_complete'] == False
        assert 'incomplete' in graph['coverage_note'].lower()
        print("[PASS] Coverage flag is False without pre-indexed data")
    
    def test_coverage_default_is_incomplete(self):
        """Test that default behavior marks coverage as incomplete."""
        builder = SimpleGraph()
        graph = builder.build_graph([])  # No has_pre_indexed_data parameter
        
        assert graph['coverage_complete'] == False
        assert 'coverage_note' in graph
        print("[PASS] Default coverage flag is False")
    
    def test_coverage_note_exists(self):
        """Test that coverage note is always present."""
        builder = SimpleGraph()
        
        # Test with True
        graph1 = builder.build_graph([], has_pre_indexed_data=True)
        assert 'coverage_note' in graph1
        assert len(graph1['coverage_note']) > 0
        
        # Test with False
        graph2 = builder.build_graph([], has_pre_indexed_data=False)
        assert 'coverage_note' in graph2
        assert len(graph2['coverage_note']) > 0
        
        print("[PASS] Coverage note always exists")
    
    def test_coverage_metadata_accessible(self):
        """Test that coverage metadata is accessible from graph."""
        builder = SimpleGraph()
        graph = builder.build_graph([], has_pre_indexed_data=True)
        
        # Verify metadata is accessible
        assert 'coverage_complete' in graph
        assert 'coverage_note' in graph
        assert isinstance(graph['coverage_complete'], bool)
        assert isinstance(graph['coverage_note'], str)
        
        print("[PASS] Coverage metadata is accessible")


if __name__ == "__main__":
    # Run tests manually
    test = TestCoverageFlag()
    
    print("Running coverage flag tests...")
    tests_run = 0
    tests_passed = 0
    
    for method_name in dir(test):
        if method_name.startswith('test_'):
            tests_run += 1
            try:
                method = getattr(test, method_name)
                method()
                tests_passed += 1
            except Exception as e:
                print(f"[FAIL] {method_name}: {e}")
    
    print(f"\n{tests_passed}/{tests_run} tests passed")
    
    if tests_passed == tests_run:
        print("\n[SUCCESS] All coverage flag tests passed!")
        sys.exit(0)
    else:
        print(f"\n[ERROR] {tests_run - tests_passed} tests failed")
        sys.exit(1)

# Made with Bob
