"""
Pydantic schemas for report retrieval.
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from backend.schemas.analysis import RiskFactors, RegressionScenario


class ReportResponse(BaseModel):
    """Response schema for GET /api/reports/{id} endpoint."""
    
    id: int
    report_id: Optional[str] = None
    pr_id: str
    repository: str
    pr_url: Optional[str] = None
    
    # Analysis results
    changed_files: List[str]
    dependency_graph: dict  # Serialized NetworkX graph
    impacted_nodes: List[str]
    
    # Risk assessment
    risk_score: float = Field(..., ge=0, le=100)
    risk_level: str
    risk_factors: RiskFactors
    
    # IBM Bob insights
    semantic_insights: str
    
    # Regression scenarios
    regression_scenarios: List[RegressionScenario]
    
    # Metadata
    created_at: str
    analysis_duration: Optional[float] = None
    status: str
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class ReportListItem(BaseModel):
    """Schema for report list items."""
    
    id: int
    report_id: Optional[str] = None
    pr_id: str
    repository: str
    risk_score: float
    risk_level: str
    created_at: str
    status: str
    
    class Config:
        from_attributes = True


class ReportListResponse(BaseModel):
    """Response schema for GET /api/reports endpoint (list all reports)."""
    
    reports: List[ReportListItem]
    total: int
    page: int = 1
    page_size: int = 50

# Made with Bob
