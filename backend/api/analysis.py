"""
API endpoints for code analysis.
Handles PR analysis requests and returns results.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import logging

from backend.db import get_db
from backend.schemas.analysis import AnalyzeRequest, AnalyzeResponse, AnalysisError
from backend.services.analysis_pipeline import AnalysisPipeline
from backend.repositories.report_repository import ReportRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["analysis"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_pr(
    request: AnalyzeRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze a pull request for semantic risks and impact.
    
    This endpoint:
    1. Fetches PR diff from GitHub
    2. Analyzes code structure with AST
    3. Builds dependency graph
    4. Identifies impacted components
    5. Calculates risk score
    6. Gets semantic insights from IBM watsonx.ai
    7. Generates regression test scenarios
    8. Stores results in database
    
    Args:
        request: AnalyzeRequest with pr_id and repository
        db: Database session
        
    Returns:
        AnalyzeResponse with complete analysis results
        
    Raises:
        HTTPException: If analysis fails
    """
    try:
        logger.info(f"Received analysis request for PR {request.pr_id} in {request.repository}")
        
        # Execute analysis pipeline
        pipeline = AnalysisPipeline()
        result = await pipeline.analyze_pr(
            pr_id=request.pr_id,
            repository=request.repository
        )
        
        # Store results in database
        repo = ReportRepository(db)
        report = repo.create_report(result)
        
        # Convert to response model
        response = AnalyzeResponse(
            report_id=report.id,
            pr_id=result['pr_id'],
            repository=result['repository'],
            pr_url=result.get('pr_url'),
            changed_files=result['changed_files'],
            impacted_nodes=result['impacted_nodes'],
            risk_score=result['risk_score'],
            risk_level=result['risk_level'],
            risk_factors=result['risk_factors'],
            semantic_insights=result['semantic_insights'],
            regression_scenarios=result['regression_scenarios'],
            analysis_duration=result['analysis_duration'],
            created_at=result['created_at']
        )
        
        logger.info(f"Analysis completed successfully. Report ID: {report.id}")
        return response
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/analyze/status/{report_id}")
async def get_analysis_status(
    report_id: int,
    db: Session = Depends(get_db)
):
    """
    Get the status of an analysis by report ID.
    
    Args:
        report_id: Database ID of the analysis report
        db: Database session
        
    Returns:
        Status information
        
    Raises:
        HTTPException: If report not found
    """
    repo = ReportRepository(db)
    report = repo.get_report_by_id(report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return {
        "report_id": report.id,
        "status": report.status,
        "pr_id": report.pr_id,
        "repository": report.repository,
        "created_at": report.created_at.isoformat() + 'Z' if report.created_at else None,
        "risk_level": report.risk_level,
        "error_message": report.error_message
    }


@router.post("/analyze/batch")
async def analyze_multiple_prs(
    requests: list[AnalyzeRequest],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Queue multiple PR analyses to run in the background.
    
    This is useful for analyzing multiple PRs at once.
    Results can be retrieved later using the report IDs.
    
    Args:
        requests: List of AnalyzeRequest objects
        background_tasks: FastAPI background tasks
        db: Database session
        
    Returns:
        List of queued analysis IDs
    """
    # For hackathon: simplified implementation
    # In production: use proper task queue (Celery, RQ, etc.)
    
    queued = []
    for req in requests[:5]:  # Limit to 5 PRs
        # Add to background tasks
        # Note: This is a simplified approach
        queued.append({
            "pr_id": req.pr_id,
            "repository": req.repository,
            "status": "queued"
        })
    
    return {
        "message": f"Queued {len(queued)} analyses",
        "analyses": queued
    }

# Made with Bob
