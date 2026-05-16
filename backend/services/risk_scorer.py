"""
Risk scorer for calculating risk scores based on multiple factors.
Combines complexity, impact scope, and criticality into a single score.
"""
import networkx as nx
from typing import Dict, Any, List
from backend.utils.diff_parser import FileChange


class RiskScorer:
    """Calculator for risk scores based on code changes."""
    
    def __init__(self):
        self.weights = {
            'complexity': 0.25,
            'impact_scope': 0.35,
            'criticality': 0.30,
            'test_coverage': 0.10
        }
    
    def calculate_risk_score(
        self,
        file_changes: List[FileChange],
        graph: nx.DiGraph,
        impacted_nodes: List[str],
        changed_nodes: List[str]
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive risk score.
        
        Args:
            file_changes: List of FileChange objects from diff parser
            graph: Dependency graph
            impacted_nodes: List of impacted node IDs
            changed_nodes: List of changed node IDs
            
        Returns:
            Dictionary with risk score and breakdown
        """
        # Calculate individual factors
        complexity_score = self._calculate_complexity_score(file_changes)
        impact_scope_score = self._calculate_impact_scope_score(
            graph, impacted_nodes, changed_nodes
        )
        criticality_score = self._calculate_criticality_score(
            graph, changed_nodes
        )
        test_coverage_score = self._estimate_test_coverage_score(
            file_changes
        )
        
        # Calculate weighted total
        total_score = (
            complexity_score * self.weights['complexity'] +
            impact_scope_score * self.weights['impact_scope'] +
            criticality_score * self.weights['criticality'] +
            test_coverage_score * self.weights['test_coverage']
        )
        
        # Determine risk level
        risk_level = self._determine_risk_level(total_score)
        
        return {
            'risk_score': round(total_score, 2),
            'risk_level': risk_level,
            'risk_factors': {
                'complexity_score': round(complexity_score, 2),
                'impact_scope': round(impact_scope_score, 2),
                'criticality': round(criticality_score, 2),
                'test_coverage': round(test_coverage_score, 2)
            }
        }
    
    def _calculate_complexity_score(self, file_changes: List[FileChange]) -> float:
        """
        Calculate complexity score based on code changes.
        
        Factors:
        - Number of files changed
        - Lines added/deleted
        - Change distribution
        
        Returns:
            Score from 0-100
        """
        if not file_changes:
            return 0.0
        
        num_files = len(file_changes)
        total_additions = sum(fc.additions for fc in file_changes)
        total_deletions = sum(fc.deletions for fc in file_changes)
        total_changes = total_additions + total_deletions
        
        # Score based on number of files (0-30 points)
        file_score = min(num_files * 3, 30)
        
        # Score based on total changes (0-40 points)
        change_score = min(total_changes / 10, 40)
        
        # Score based on change distribution (0-30 points)
        # Higher score if changes are concentrated in few files
        if num_files > 0:
            avg_changes_per_file = total_changes / num_files
            concentration = min(avg_changes_per_file / 20, 1.0) * 30
        else:
            concentration = 0
        
        return file_score + change_score + concentration
    
    def _calculate_impact_scope_score(
        self,
        graph: nx.DiGraph,
        impacted_nodes: List[str],
        changed_nodes: List[str]
    ) -> float:
        """
        Calculate impact scope score based on graph analysis.
        
        Factors:
        - Number of impacted nodes
        - Ratio of impacted to total nodes
        - Depth of impact
        
        Returns:
            Score from 0-100
        """
        if graph.number_of_nodes() == 0:
            return 0.0
        
        num_impacted = len(impacted_nodes)
        num_changed = len(changed_nodes)
        total_nodes = graph.number_of_nodes()
        
        # Score based on absolute number of impacted nodes (0-40 points)
        impact_count_score = min(num_impacted * 2, 40)
        
        # Score based on impact ratio (0-40 points)
        impact_ratio = num_impacted / total_nodes if total_nodes > 0 else 0
        ratio_score = impact_ratio * 40
        
        # Score based on amplification factor (0-20 points)
        amplification = num_impacted / num_changed if num_changed > 0 else 1
        amplification_score = min(amplification * 2, 20)
        
        return impact_count_score + ratio_score + amplification_score
    
    def _calculate_criticality_score(
        self,
        graph: nx.DiGraph,
        changed_nodes: List[str]
    ) -> float:
        """
        Calculate criticality score based on node importance.
        
        Factors:
        - Centrality of changed nodes
        - Number of dependencies
        
        Returns:
            Score from 0-100
        """
        if not changed_nodes or graph.number_of_nodes() == 0:
            return 0.0
        
        try:
            # Calculate betweenness centrality
            centrality = nx.betweenness_centrality(graph)
            
            # Get centrality scores for changed nodes
            changed_centrality = [
                centrality.get(node, 0) for node in changed_nodes
            ]
            
            # Average centrality of changed nodes
            avg_centrality = sum(changed_centrality) / len(changed_centrality)
            
            # Score based on centrality (0-60 points)
            centrality_score = avg_centrality * 60
            
        except:
            # Fallback if centrality calculation fails
            centrality_score = 30
        
        # Score based on out-degree (number of dependencies) (0-40 points)
        total_out_degree = sum(
            graph.out_degree(node) for node in changed_nodes if node in graph
        )
        avg_out_degree = total_out_degree / len(changed_nodes) if changed_nodes else 0
        degree_score = min(avg_out_degree * 4, 40)
        
        return centrality_score + degree_score
    
    def _estimate_test_coverage_score(self, file_changes: List[FileChange]) -> float:
        """
        Estimate test coverage score (inverse - lower coverage = higher risk).
        
        This is a simplified heuristic based on file patterns.
        In production, integrate with actual test coverage tools.
        
        Returns:
            Score from 0-100 (higher = more risk due to less coverage)
        """
        if not file_changes:
            return 0.0
        
        # Count test files vs non-test files
        test_files = 0
        non_test_files = 0
        
        for fc in file_changes:
            file_path = fc.file_path.lower()
            if 'test' in file_path or 'spec' in file_path or file_path.endswith('_test.py'):
                test_files += 1
            else:
                non_test_files += 1
        
        # If tests are being changed, assume better coverage (lower risk)
        if test_files > 0:
            coverage_ratio = test_files / (test_files + non_test_files)
            # Inverse score: more tests = lower risk
            return (1 - coverage_ratio) * 100
        else:
            # No test files changed = higher risk
            return 80.0
    
    def _determine_risk_level(self, score: float) -> str:
        """
        Determine risk level category from score.
        
        Uses 3-tier system as defined in TECH SPEC:
        - LOW: 0-33
        - MEDIUM: 34-66
        - HIGH: 67-100
        
        Args:
            score: Risk score (0-100)
            
        Returns:
            Risk level: LOW, MEDIUM, or HIGH
        """
        if score >= 67:
            return 'HIGH'
        elif score >= 34:
            return 'MEDIUM'
        else:
            return 'LOW'

# Made with Bob
