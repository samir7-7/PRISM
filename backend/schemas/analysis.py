"""
Pydantic schemas for analysis requests and responses.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """Request schema for POST /api/analyze endpoint."""
    
    pr_id: str = Field(..., description="Pull request ID or number")
    repository: str = Field(..., description="Repository in format 'owner/repo'")
    
    class Config:
        json_schema_extra = {
            "example": {
                "pr_id": "123",
                "repository": "octocat/Hello-World"
            }
        }


class RiskFactors(BaseModel):
    """Breakdown of risk factors."""
    
    complexity_score: float = Field(..., description="Code complexity contribution (0-100)")
    impact_scope: float = Field(..., description="Number of impacted components (0-100)")
    criticality: float = Field(..., description="Criticality of changed components (0-100)")
    test_coverage: float = Field(..., description="Test coverage factor (0-100)")


class RegressionScenario(BaseModel):
    """A single regression test scenario."""
    
    scenario_id: str
    title: str
    description: str
    affected_component: str
    test_steps: List[str]
    expected_behavior: str
    priority: str  # HIGH, MEDIUM, LOW


class AnalyzeResponse(BaseModel):
    """Response schema for POST /api/analyze endpoint."""
    
    report_id: int = Field(..., description="Database ID of the analysis report")
    pr_id: str
    repository: str
    pr_url: Optional[str] = None
    
    # Analysis results
    changed_files: List[str]
    impacted_nodes: List[str]
    risk_score: float = Field(..., ge=0, le=100, description="Overall risk score (0-100)")
    risk_level: str = Field(..., description="Risk level: LOW, MEDIUM, HIGH, CRITICAL")
    risk_factors: RiskFactors
    
    # IBM Bob insights
    semantic_insights: str
    
    # Regression scenarios
    regression_scenarios: List[RegressionScenario]
    
    # Metadata
    analysis_duration: float = Field(..., description="Analysis duration in seconds")
    created_at: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "report_id": 1,
                "pr_id": "123",
                "repository": "octocat/Hello-World",
                "pr_url": "https://github.com/octocat/Hello-World/pull/123",
                "changed_files": ["src/main.py", "src/utils.py"],
                "impacted_nodes": ["main.process_data", "utils.validate_input"],
                "risk_score": 75.5,
                "risk_level": "HIGH",
                "risk_factors": {
                    "complexity_score": 80,
                    "impact_scope": 70,
                    "criticality": 85,
                    "test_coverage": 60
                },
                "semantic_insights": "This change modifies core data processing logic...",
                "regression_scenarios": [
                    {
                        "scenario_id": "RS-001",
                        "title": "Test data validation with edge cases",
                        "description": "Verify that modified validation logic handles edge cases",
                        "affected_component": "utils.validate_input",
                        "test_steps": ["Step 1", "Step 2"],
                        "expected_behavior": "Should handle null values gracefully",
                        "priority": "HIGH"
                    }
                ],
                "analysis_duration": 12.5,
                "created_at": "2024-01-01T12:00:00Z"
            }
        }


class AnalysisError(BaseModel):
    """Error response schema."""
    
    error: str
    detail: str
    pr_id: Optional[str] = None
    repository: Optional[str] = None

# Made with Bob
