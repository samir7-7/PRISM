"""
Database model for analysis reports.
Stores complete analysis results including graph, risks, and recommendations.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from backend.models.base import Base


class AnalysisReport(Base):
    """Analysis report database model."""
    
    __tablename__ = "analysis_reports"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # PR Information
    pr_id = Column(String(50), nullable=False, index=True)
    repository = Column(String(255), nullable=False)
    pr_url = Column(String(500))
    
    # Analysis Results (stored as JSON strings)
    changed_files = Column(Text)  # JSON array of file paths
    dependency_graph = Column(Text)  # JSON serialized NetworkX graph
    impacted_nodes = Column(Text)  # JSON array of impacted node IDs
    
    # Risk Assessment
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(20))  # LOW, MEDIUM, HIGH, CRITICAL
    risk_factors = Column(Text)  # JSON object with risk breakdown
    
    # IBM Bob Analysis
    semantic_insights = Column(Text)  # IBM Bob's analysis text
    
    # Regression Testing
    regression_scenarios = Column(Text)  # JSON array of test scenarios
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    analysis_duration = Column(Float)  # Duration in seconds
    status = Column(String(20), default="completed")  # completed, failed, pending
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<AnalysisReport(id={self.id}, pr_id={self.pr_id}, risk_score={self.risk_score})>"

# Made with Bob
