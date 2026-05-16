"""
Repository layer for database operations on analysis reports.
Handles CRUD operations for AnalysisReport model.
"""
import json
import hashlib
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from backend.models.report import AnalysisReport
from backend.schemas.report import ReportResponse, ReportListItem


class ReportRepository:
    """Repository for analysis report database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _make_report_id(self, pr_id: str, repository: str) -> str:
        """Build a deterministic 8-char report_id from the request."""
        digest = hashlib.sha1(f"{repository}#{pr_id}".encode()).hexdigest()
        return digest[:8]
    
    def create_report(self, analysis_result: dict) -> AnalysisReport:
        """
        Create a new analysis report in the database.
        
        Args:
            analysis_result: Dictionary with analysis results from pipeline
            
        Returns:
            Created AnalysisReport instance
        """
        # Generate deterministic report_id
        report_id = self._make_report_id(
            analysis_result['pr_id'], 
            analysis_result['repository']
        )
        
        # Serialize complex objects to JSON strings
        report = AnalysisReport(
            report_id=report_id,
            pr_id=analysis_result['pr_id'],
            repository=analysis_result['repository'],
            pr_url=analysis_result.get('pr_url'),
            changed_files=json.dumps(analysis_result['changed_files']),
            dependency_graph=json.dumps(analysis_result['dependency_graph']),
            impacted_nodes=json.dumps(analysis_result['impacted_nodes']),
            risk_score=analysis_result['risk_score'],
            risk_level=analysis_result['risk_level'],
            risk_factors=json.dumps(analysis_result['risk_factors']),
            semantic_insights=analysis_result['semantic_insights'],
            regression_scenarios=json.dumps(analysis_result['regression_scenarios']),
            analysis_duration=analysis_result.get('analysis_duration'),
            status=analysis_result.get('status', 'completed'),
            error_message=analysis_result.get('error_message')
        )
        
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        
        return report
    
    def get_report_by_id(self, report_id: int) -> Optional[AnalysisReport]:
        """
        Retrieve a report by its database integer ID.
        
        Args:
            report_id: Database ID of the report
            
        Returns:
            AnalysisReport instance or None if not found
        """
        return self.db.query(AnalysisReport).filter(
            AnalysisReport.id == report_id
        ).first()

    def get_report_by_string_id(self, report_id: str) -> Optional[AnalysisReport]:
        """
        Retrieve a report by its deterministic string report_id.
        
        Args:
            report_id: 8-char string ID of the report
            
        Returns:
            AnalysisReport instance or None if not found
        """
        return self.db.query(AnalysisReport).filter(
            AnalysisReport.report_id == report_id
        ).first()
    
    def get_report_by_pr(
        self,
        pr_id: str,
        repository: str
    ) -> Optional[AnalysisReport]:
        """
        Retrieve the most recent report for a specific PR.
        
        Args:
            pr_id: Pull request ID
            repository: Repository name
            
        Returns:
            AnalysisReport instance or None if not found
        """
        return self.db.query(AnalysisReport).filter(
            AnalysisReport.pr_id == pr_id,
            AnalysisReport.repository == repository
        ).order_by(AnalysisReport.created_at.desc()).first()
    
    def get_all_reports(
        self,
        skip: int = 0,
        limit: int = 50
    ) -> List[AnalysisReport]:
        """
        Retrieve all reports with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of AnalysisReport instances
        """
        return self.db.query(AnalysisReport).order_by(
            AnalysisReport.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    def get_reports_by_repository(
        self,
        repository: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[AnalysisReport]:
        """
        Retrieve reports for a specific repository.
        
        Args:
            repository: Repository name
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of AnalysisReport instances
        """
        return self.db.query(AnalysisReport).filter(
            AnalysisReport.repository == repository
        ).order_by(
            AnalysisReport.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    def count_reports(self) -> int:
        """
        Count total number of reports.
        
        Returns:
            Total count of reports
        """
        return self.db.query(AnalysisReport).count()
    
    def delete_report(self, report_id: int) -> bool:
        """
        Delete a report by ID.
        
        Args:
            report_id: Database ID of the report
            
        Returns:
            True if deleted, False if not found
        """
        report = self.get_report_by_id(report_id)
        if report:
            self.db.delete(report)
            self.db.commit()
            return True
        return False
    
    def to_response_model(self, report: AnalysisReport) -> ReportResponse:
        """
        Convert database model to response schema.
        
        Args:
            report: AnalysisReport database model
            
        Returns:
            ReportResponse schema
        """
        return ReportResponse(
            id=report.id,
            report_id=report.report_id,
            pr_id=report.pr_id,
            repository=report.repository,
            pr_url=report.pr_url,
            changed_files=json.loads(report.changed_files) if report.changed_files else [],
            dependency_graph=json.loads(report.dependency_graph) if report.dependency_graph else {},
            impacted_nodes=json.loads(report.impacted_nodes) if report.impacted_nodes else [],
            risk_score=report.risk_score,
            risk_level=report.risk_level,
            risk_factors=json.loads(report.risk_factors) if report.risk_factors else {},
            semantic_insights=report.semantic_insights or "",
            regression_scenarios=json.loads(report.regression_scenarios) if report.regression_scenarios else [],
            created_at=report.created_at.isoformat() + 'Z' if report.created_at else "",
            analysis_duration=report.analysis_duration,
            status=report.status,
            error_message=report.error_message
        )
    
    def to_list_item(self, report: AnalysisReport) -> ReportListItem:
        """
        Convert database model to list item schema.
        
        Args:
            report: AnalysisReport database model
            
        Returns:
            ReportListItem schema
        """
        return ReportListItem(
            id=report.id,
            report_id=report.report_id,
            pr_id=report.pr_id,
            repository=report.repository,
            risk_score=report.risk_score,
            risk_level=report.risk_level,
            created_at=report.created_at.isoformat() + 'Z' if report.created_at else "",
            status=report.status
        )

# Made with Bob
