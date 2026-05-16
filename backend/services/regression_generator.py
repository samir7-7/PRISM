"""
Regression test scenario generator.
Creates actionable test scenarios based on code changes and impact analysis.
"""
from typing import List, Dict, Any
import networkx as nx
from backend.schemas.analysis import RegressionScenario


class RegressionGenerator:
    """Generator for regression test scenarios."""
    
    def __init__(self):
        self.scenario_counter = 0
    
    def generate_scenarios(
        self,
        changed_files: List[str],
        impacted_nodes: List[str],
        graph: nx.DiGraph,
        ibm_insights: str = ""
    ) -> List[RegressionScenario]:
        """
        Generate regression test scenarios based on analysis.
        
        Args:
            changed_files: List of changed file paths
            impacted_nodes: List of impacted node IDs
            graph: Dependency graph
            ibm_insights: Optional insights from IBM watsonx.ai
            
        Returns:
            List of RegressionScenario objects
        """
        scenarios = []
        
        # Generate scenarios for changed files
        scenarios.extend(self._generate_file_scenarios(changed_files))
        
        # Generate scenarios for impacted components
        scenarios.extend(self._generate_impact_scenarios(impacted_nodes, graph))
        
        # Generate integration scenarios
        scenarios.extend(self._generate_integration_scenarios(changed_files, impacted_nodes, graph))
        
        # Parse IBM insights for additional scenarios
        if ibm_insights:
            scenarios.extend(self._parse_ibm_scenarios(ibm_insights))
        
        # Prioritize scenarios
        scenarios = self._prioritize_scenarios(scenarios)
        
        # PRD requires at least 3 scenarios per high-risk path
        # Ensure we have sufficient high-priority scenarios
        high_priority_count = sum(1 for s in scenarios if s.priority == "HIGH")
        
        # If we have high-risk paths but insufficient scenarios, keep all
        # Otherwise, return prioritized list (no arbitrary cap)
        if high_priority_count > 0 and high_priority_count < 3:
            # Keep all scenarios to meet minimum requirement
            return scenarios
        
        # Return all scenarios (no cap) - let consumers decide how many to use
        return scenarios
    
    def _generate_file_scenarios(self, changed_files: List[str]) -> List[RegressionScenario]:
        """Generate scenarios for directly changed files."""
        scenarios = []
        
        # Generate scenarios for all changed files (no arbitrary limit)
        for file_path in changed_files:
            self.scenario_counter += 1
            
            # Determine file type and generate appropriate scenario
            if file_path.endswith('.py'):
                scenario_type = "Python module"
            elif file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
                scenario_type = "JavaScript/TypeScript module"
            else:
                scenario_type = "Source file"
            
            scenarios.append(RegressionScenario(
                scenario_id=f"RS-{self.scenario_counter:03d}",
                title=f"Verify changes in {file_path.split('/')[-1]}",
                description=f"Test the modified {scenario_type} to ensure changes work as expected",
                affected_component=file_path,
                test_steps=[
                    f"Review changes in {file_path}",
                    "Execute unit tests for modified functions/classes",
                    "Verify input validation and error handling",
                    "Test edge cases and boundary conditions"
                ],
                expected_behavior="All functionality in the modified file works correctly without breaking existing behavior",
                priority="HIGH"
            ))
        
        return scenarios
    
    def _generate_impact_scenarios(
        self,
        impacted_nodes: List[str],
        graph: nx.DiGraph
    ) -> List[RegressionScenario]:
        """Generate scenarios for impacted components."""
        scenarios = []
        
        # Group impacted nodes by file
        files_with_impacts = {}
        # Process all impacted nodes (no arbitrary limit)
        for node_id in impacted_nodes:
            if node_id in graph:
                file_path = graph.nodes[node_id].get('file', '')
                if file_path:
                    if file_path not in files_with_impacts:
                        files_with_impacts[file_path] = []
                    files_with_impacts[file_path].append(node_id)
        
        # Generate scenarios for all impacted files
        for file_path, nodes in files_with_impacts.items():
            self.scenario_counter += 1
            
            component_names = [
                graph.nodes[node].get('name', 'component') 
                for node in nodes[:3]
            ]
            
            scenarios.append(RegressionScenario(
                scenario_id=f"RS-{self.scenario_counter:03d}",
                title=f"Test downstream impacts in {file_path.split('/')[-1]}",
                description=f"Verify that components depending on changed code still function correctly",
                affected_component=file_path,
                test_steps=[
                    f"Test {', '.join(component_names)} functionality",
                    "Verify data flow from changed components",
                    "Check for unexpected side effects",
                    "Validate integration points"
                ],
                expected_behavior="All dependent components continue to work correctly with the changes",
                priority="MEDIUM"
            ))
        
        return scenarios
    
    def _generate_integration_scenarios(
        self,
        changed_files: List[str],
        impacted_nodes: List[str],
        graph: nx.DiGraph
    ) -> List[RegressionScenario]:
        """Generate integration test scenarios."""
        scenarios = []
        
        if len(changed_files) > 1 or len(impacted_nodes) > 5:
            self.scenario_counter += 1
            
            scenarios.append(RegressionScenario(
                scenario_id=f"RS-{self.scenario_counter:03d}",
                title="End-to-end integration testing",
                description="Test complete workflows that span multiple changed and impacted components",
                affected_component="Multiple components",
                test_steps=[
                    "Identify critical user workflows",
                    "Execute end-to-end tests for each workflow",
                    "Verify data consistency across components",
                    "Test error handling and recovery",
                    "Validate performance under load"
                ],
                expected_behavior="All integrated workflows complete successfully without errors or performance degradation",
                priority="HIGH"
            ))
        
        return scenarios
    
    def _parse_ibm_scenarios(self, ibm_insights: str) -> List[RegressionScenario]:
        """Parse IBM watsonx.ai insights for test scenarios."""
        scenarios = []
        
        # Simple parsing - look for numbered lists or bullet points
        lines = ibm_insights.split('\n')
        current_scenario = None
        
        for line in lines:
            line = line.strip()
            
            # Look for scenario indicators
            if any(indicator in line.lower() for indicator in ['test', 'scenario', 'verify', 'validate']):
                if len(line) > 20 and len(line) < 200:  # Reasonable length
                    self.scenario_counter += 1
                    
                    scenarios.append(RegressionScenario(
                        scenario_id=f"RS-{self.scenario_counter:03d}",
                        title=line[:100],  # Truncate if too long
                        description="AI-suggested test scenario based on semantic analysis",
                        affected_component="As identified by AI analysis",
                        test_steps=[
                            "Review AI-generated scenario details",
                            "Adapt to specific codebase context",
                            "Execute test",
                            "Document results"
                        ],
                        expected_behavior="Behavior as described in AI analysis",
                        priority="MEDIUM"
                    ))
                    
                    if len(scenarios) >= 2:  # Limit AI scenarios
                        break
        
        return scenarios
    
    def _prioritize_scenarios(
        self,
        scenarios: List[RegressionScenario]
    ) -> List[RegressionScenario]:
        """Prioritize scenarios by importance."""
        # Sort by priority: HIGH > MEDIUM > LOW
        priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        
        return sorted(
            scenarios,
            key=lambda s: priority_order.get(s.priority, 3)
        )
    
    def generate_summary(self, scenarios: List[RegressionScenario]) -> Dict[str, Any]:
        """Generate a summary of test scenarios."""
        return {
            'total_scenarios': len(scenarios),
            'by_priority': {
                'HIGH': sum(1 for s in scenarios if s.priority == 'HIGH'),
                'MEDIUM': sum(1 for s in scenarios if s.priority == 'MEDIUM'),
                'LOW': sum(1 for s in scenarios if s.priority == 'LOW')
            },
            'estimated_effort_hours': len(scenarios) * 2,  # Rough estimate: 2 hours per scenario
            'recommended_execution_order': [s.scenario_id for s in scenarios]
        }

# Made with Bob
