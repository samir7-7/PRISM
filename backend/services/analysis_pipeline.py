"""
Analysis pipeline orchestrator.
Coordinates all services to perform complete PR analysis.
"""
import time
import logging
from typing import Dict, Any, List
from datetime import datetime

from backend.utils.github_client import GitHubClient
from backend.utils.diff_parser import DiffParser
from backend.utils.graph_serializer import GraphSerializer
from backend.services.ast_analyzer import ASTAnalyzer, CodeElement
from backend.services.graph_builder import GraphBuilder
from backend.services.impact_traverser import ImpactTraverser
from backend.services.risk_scorer import RiskScorer
from backend.services.ibm_bob_client import IBMBobClient
from backend.services.regression_generator import RegressionGenerator

logger = logging.getLogger(__name__)


class AnalysisPipeline:
    """Orchestrates the complete analysis workflow."""
    
    def __init__(self):
        self.github_client = GitHubClient()
        self.ast_analyzer = ASTAnalyzer()
        self.graph_builder = GraphBuilder()
        self.risk_scorer = RiskScorer()
        self.ibm_client = IBMBobClient()
        self.regression_generator = RegressionGenerator()
    
    async def analyze_pr(
        self,
        pr_id: str,
        repository: str
    ) -> Dict[str, Any]:
        """
        Execute complete analysis pipeline for a pull request.
        
        Args:
            pr_id: Pull request ID/number
            repository: Repository in format 'owner/repo'
            
        Returns:
            Complete analysis results dictionary
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting analysis for PR {pr_id} in {repository}")
            
            # Step 1: Fetch PR information and diff from GitHub
            logger.info("Step 1: Fetching PR data from GitHub")
            owner, repo = self.github_client.parse_repository(repository)
            pr_info = await self.github_client.get_pr_info(owner, repo, pr_id)
            pr_diff = await self.github_client.get_pr_diff(owner, repo, pr_id)
            
            pr_url = pr_info.get('html_url', '')
            
            # Step 2: Parse diff to extract changed files
            logger.info("Step 2: Parsing diff")
            diff_parser = DiffParser(pr_diff)
            file_changes = diff_parser.parse()
            changed_files = diff_parser.get_changed_files()
            
            if not changed_files:
                return self._create_empty_result(pr_id, repository, pr_url, start_time)
            
            # Step 3: Analyze code structure with AST
            logger.info("Step 3: Analyzing code structure")
            all_elements = []
            
            # For hackathon: analyze only changed files (not entire repo)
            for file_path in changed_files[:10]:  # Limit to 10 files
                try:
                    # Fetch file content
                    content = await self.github_client.get_file_content(
                        owner, repo, file_path, ref=pr_info.get('head', {}).get('sha')
                    )
                    elements = self.ast_analyzer.analyze_file(file_path, content)
                    all_elements.extend(elements)
                except Exception as e:
                    logger.warning(f"Failed to analyze {file_path}: {e}")
                    continue
            
            # Step 4: Build dependency graph
            logger.info("Step 4: Building dependency graph")
            graph = self.graph_builder.build_graph(all_elements)
            
            # Step 5: Identify impacted components
            logger.info("Step 5: Identifying impacted components")
            traverser = ImpactTraverser(graph)
            impact_summary = traverser.get_impact_summary(changed_files)
            impacted_nodes = impact_summary['all_impacted_nodes']
            
            # Step 6: Calculate risk score
            logger.info("Step 6: Calculating risk score")
            changed_nodes = impact_summary['changed_nodes']
            risk_result = self.risk_scorer.calculate_risk_score(
                file_changes,
                graph,
                impacted_nodes,
                changed_nodes
            )
            
            # Step 7: Get semantic insights from IBM watsonx.ai
            logger.info("Step 7: Getting semantic insights from IBM watsonx.ai")
            diff_summary = diff_parser.get_change_summary()
            impacted_component_names = [
                graph.nodes[node].get('name', node) 
                for node in impacted_nodes[:20]
            ]
            
            try:
                semantic_insights = await self.ibm_client.analyze_code_changes(
                    diff_summary=str(diff_summary),
                    changed_files=changed_files,
                    impacted_components=impacted_component_names
                )
            except Exception as e:
                logger.error(f"IBM watsonx.ai analysis failed: {e}")
                semantic_insights = "Semantic analysis unavailable. Please review changes manually."
            
            # Step 8: Generate regression test scenarios
            logger.info("Step 8: Generating regression test scenarios")
            scenarios = self.regression_generator.generate_scenarios(
                changed_files,
                impacted_nodes,
                graph,
                semantic_insights
            )
            
            # Step 9: Serialize graph for storage
            logger.info("Step 9: Serializing results")
            graph_data = GraphSerializer.to_dict(graph)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Compile results
            result = {
                'pr_id': pr_id,
                'repository': repository,
                'pr_url': pr_url,
                'changed_files': changed_files,
                'dependency_graph': graph_data,
                'impacted_nodes': impacted_nodes,
                'risk_score': risk_result['risk_score'],
                'risk_level': risk_result['risk_level'],
                'risk_factors': risk_result['risk_factors'],
                'semantic_insights': semantic_insights,
                'regression_scenarios': [s.dict() for s in scenarios],
                'analysis_duration': round(duration, 2),
                'created_at': datetime.utcnow().isoformat() + 'Z',
                'status': 'completed'
            }
            
            logger.info(f"Analysis completed in {duration:.2f}s")
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Analysis failed: {e}", exc_info=True)
            
            return {
                'pr_id': pr_id,
                'repository': repository,
                'pr_url': '',
                'changed_files': [],
                'dependency_graph': {},
                'impacted_nodes': [],
                'risk_score': 0.0,
                'risk_level': 'UNKNOWN',
                'risk_factors': {
                    'complexity_score': 0.0,
                    'impact_scope': 0.0,
                    'criticality': 0.0,
                    'test_coverage': 0.0
                },
                'semantic_insights': f"Analysis failed: {str(e)}",
                'regression_scenarios': [],
                'analysis_duration': round(duration, 2),
                'created_at': datetime.utcnow().isoformat() + 'Z',
                'status': 'failed',
                'error_message': str(e)
            }
    
    def _create_empty_result(
        self,
        pr_id: str,
        repository: str,
        pr_url: str,
        start_time: float
    ) -> Dict[str, Any]:
        """Create result for PR with no changes."""
        duration = time.time() - start_time
        
        return {
            'pr_id': pr_id,
            'repository': repository,
            'pr_url': pr_url,
            'changed_files': [],
            'dependency_graph': {},
            'impacted_nodes': [],
            'risk_score': 0.0,
            'risk_level': 'LOW',
            'risk_factors': {
                'complexity_score': 0.0,
                'impact_scope': 0.0,
                'criticality': 0.0,
                'test_coverage': 100.0
            },
            'semantic_insights': 'No code changes detected in this PR.',
            'regression_scenarios': [],
            'analysis_duration': round(duration, 2),
            'created_at': datetime.utcnow().isoformat() + 'Z',
            'status': 'completed'
        }

# Made with Bob
