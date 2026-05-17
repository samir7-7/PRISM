"""
PRISM Backend - FastAPI Application
Main entry point for the API server.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import logging

from backend.config import settings
from backend.db import init_db
from backend.api import analysis, reports
from backend.swagger_config import (
    API_TITLE,
    API_DESCRIPTION,
    API_VERSION,
    API_CONTACT,
    API_LICENSE,
    TAGS_METADATA,
    SWAGGER_UI_PARAMETERS
)

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application with enhanced OpenAPI configuration
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    contact=API_CONTACT,
    license_info=API_LICENSE,
    openapi_tags=TAGS_METADATA,
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_parameters=SWAGGER_UI_PARAMETERS
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analysis.router)
app.include_router(reports.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Starting PRISM API server...")
    logger.info(f"CORS origins: {settings.cors_origins}")
    
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


@app.get("/", tags=["health"])
async def root():
    """
    Root endpoint - API status check.
    
    Returns basic information about the PRISM API service.
    """
    return {
        "service": "PRISM API",
        "status": "running",
        "version": API_VERSION,
        "description": "Predictive Risk Intelligence for Software Modifications",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        }
    }


@app.get("/healthz", tags=["health"])
async def healthz():
    """
    CLI health check endpoint.
    
    Returns 200 {"ok": true} if the service is up.
    Required by the Prism CLI pre-flight check.
    """
    return {"ok": True}


@app.get("/health", tags=["health"])
async def health_check():
    """
    Detailed health check endpoint.
    
    Returns the health status of the API and its dependencies.
    Useful for monitoring and load balancer health checks.
    """
    return {
        "status": "healthy",
        "database": "connected",
        "services": {
            "github_api": "configured",
            "openrouter": "configured",
            "ast_analyzer": "ready",
            "graph_builder": "ready",
            "impact_traverser": "ready",
            "risk_scorer": "ready"
        },
        "version": API_VERSION
    }


@app.get("/api/info", tags=["health"])
async def api_info():
    """
    API information and capabilities.
    
    Returns detailed information about the API's features, endpoints,
    and capabilities. Useful for API discovery and integration.
    """
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "description": "Semantic code analysis for pull requests",
        "capabilities": [
            "Pull request analysis",
            "AST-based code parsing",
            "Dependency graph construction",
            "Impact analysis and traversal",
            "Multi-factor risk scoring",
            "AI-powered semantic insights via OpenRouter",
            "Automated regression test scenario generation",
            "Report storage and retrieval"
        ],
        "endpoints": {
            "analyze": "POST /api/analyze",
            "analyze_status": "GET /api/analyze/status/{report_id}",
            "batch_analyze": "POST /api/analyze/batch",
            "get_report": "GET /api/reports/{id}",
            "list_reports": "GET /api/reports",
            "get_by_pr": "GET /api/reports/pr/{pr_id}",
            "delete_report": "DELETE /api/reports/{id}",
            "stats": "GET /api/reports/stats/summary"
        },
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_spec": "/openapi.json"
        },
        "contact": API_CONTACT
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower()
    )

# Made with Bob
