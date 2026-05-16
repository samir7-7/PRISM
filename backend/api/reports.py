"""
API endpoints for retrieving analysis reports.
Handles report retrieval and listing.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import logging

from backend.db import get_db
from backend.schemas.report import ReportResponse, ReportListResponse, ReportListItem
from backend.repositories.report_repository import ReportRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific analysis report by ID (integer or string).
    
    Args:
        report_id: Database ID (int) or deterministic ID (string)
        db: Database session
        
    Returns:
        Complete analysis report
        
    Raises:
        HTTPException: If report not found
    """
    repo = ReportRepository(db)
    report = None
    
    # Try integer lookup first if possible
    if report_id.isdigit():
        report = repo.get_report_by_id(int(report_id))
    
    # If not found by int or not an int, try string ID
    if not report:
        report = repo.get_report_by_string_id(report_id)
    
    if not report:
        raise HTTPException(
            status_code=404,
            detail=f"Report with ID {report_id} not found"
        )
    
    return repo.to_response_model(report)


@router.get("/", response_model=ReportListResponse)
async def list_reports(
    repository: Optional[str] = Query(None, description="Filter by repository"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    List all analysis reports with pagination.
    
    Args:
        repository: Optional filter by repository name
        page: Page number (1-indexed)
        page_size: Number of items per page
        db: Database session
        
    Returns:
        Paginated list of reports
    """
    repo = ReportRepository(db)
    
    skip = (page - 1) * page_size
    
    if repository:
        reports = repo.get_reports_by_repository(repository, skip=skip, limit=page_size)
    else:
        reports = repo.get_all_reports(skip=skip, limit=page_size)
    
    total = repo.count_reports()
    
    report_items = [repo.to_list_item(r) for r in reports]
    
    return ReportListResponse(
        reports=report_items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/pr/{pr_id}", response_model=ReportResponse)
async def get_report_by_pr(
    pr_id: str,
    repository: str = Query(..., description="Repository in format 'owner/repo'"),
    db: Session = Depends(get_db)
):
    """
    Retrieve the most recent analysis report for a specific PR.
    
    Args:
        pr_id: Pull request ID
        repository: Repository name
        db: Database session
        
    Returns:
        Most recent analysis report for the PR
        
    Raises:
        HTTPException: If no report found for the PR
    """
    repo = ReportRepository(db)
    report = repo.get_report_by_pr(pr_id, repository)
    
    if not report:
        raise HTTPException(
            status_code=404,
            detail=f"No report found for PR {pr_id} in {repository}"
        )
    
    return repo.to_response_model(report)


@router.delete("/{report_id}")
async def delete_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete an analysis report.
    
    Args:
        report_id: Database ID of the report
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If report not found
    """
    repo = ReportRepository(db)
    success = repo.delete_report(report_id)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Report with ID {report_id} not found"
        )
    
    return {"message": f"Report {report_id} deleted successfully"}


@router.get("/stats/summary")
async def get_stats_summary(
    db: Session = Depends(get_db)
):
    """
    Get summary statistics about all reports.
    
    Args:
        db: Database session
        
    Returns:
        Statistics summary
    """
    repo = ReportRepository(db)
    
    all_reports = repo.get_all_reports(skip=0, limit=1000)  # Get recent reports
    
    if not all_reports:
        return {
            "total_reports": 0,
            "average_risk_score": 0,
            "risk_distribution": {},
            "most_analyzed_repositories": []
        }
    
    # Calculate statistics
    total = len(all_reports)
    avg_risk = sum(r.risk_score for r in all_reports) / total if total > 0 else 0
    
    risk_dist = {}
    for r in all_reports:
        level = r.risk_level
        risk_dist[level] = risk_dist.get(level, 0) + 1
    
    # Count by repository
    repo_counts = {}
    for r in all_reports:
        repo_counts[r.repository] = repo_counts.get(r.repository, 0) + 1
    
    top_repos = sorted(repo_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "total_reports": total,
        "average_risk_score": round(avg_risk, 2),
        "risk_distribution": risk_dist,
        "most_analyzed_repositories": [
            {"repository": repo, "count": count} 
            for repo, count in top_repos
        ]
    }

# Made with Bob
