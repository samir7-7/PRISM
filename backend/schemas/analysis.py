"""
Pydantic schemas for analysis requests and responses.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator


class AnalyzeRequest(BaseModel):
    """Request schema for POST /api/analysis/run endpoint."""
    
    pr_identifier: str = Field(..., alias="pr_id", description="Pull request ID or number")
    repository_url: str = Field(..., alias="repository", description="Repository URL or owner/repo")
    github_token: Optional[str] = None
    
    @field_validator('repository_url')
    @classmethod
    def validate_repository_url(cls, v: str) -> str:
        """Validate that repository_url is either a valid URL or owner/repo format."""
        v = v.strip()
        
        # Check if it's a valid GitHub URL or owner/repo format
        if '/' not in v:
            raise ValueError('repository_url must be a GitHub URL or owner/repo format')
        
        # If it contains spaces or other invalid characters, reject it
        if ' ' in v or '\t' in v or '\n' in v:
            raise ValueError('repository_url contains invalid characters')
        
        # Basic check: if it looks like a URL, it should start with http
        if '://' in v and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('repository_url must be a valid HTTP(S) URL')
        
        return v
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "pr_identifier": "123",
                "repository_url": "https://github.com/octocat/Hello-World",
                "github_token": "ghp_..."
            }
        }


class AnalysisResponse(BaseModel):
    """Response schema matching the Prism CLI contract."""
    
    report_id: str
    dashboard_url: str
    risk_score: int = Field(..., ge=0, le=100, description="Risk score (0-100)")
    risk_label: str  # LOW, MEDIUM, HIGH
    impacted_node_count: int = Field(..., ge=0, description="Number of impacted nodes")
    status: str = "COMPLETE"


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
    risk_level: str = Field(..., description="Risk level: LOW, MEDIUM, HIGH")
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
