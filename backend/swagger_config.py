"""
Swagger/OpenAPI Configuration for PRISM API
Enhanced API documentation with detailed schemas and examples.
"""

# API Metadata
API_TITLE = "PRISM API"
API_DESCRIPTION = """
## Predictive Risk Intelligence for Software Modifications

PRISM provides semantic code analysis for pull requests using advanced AST parsing, 
dependency graph construction, and AI-powered insights via IBM watsonx.ai.

### Key Features

* 🔍 **Deep Code Analysis**: AST-based parsing of code changes
* 🕸️ **Dependency Mapping**: Automatic dependency graph construction
* ⚠️ **Risk Assessment**: Multi-factor risk scoring algorithm
* 🤖 **AI Insights**: Semantic analysis powered by IBM watsonx.ai
* 🧪 **Test Generation**: Automated regression test scenario creation
* 📊 **Impact Analysis**: Identify all affected components

### Analysis Pipeline

1. **Fetch PR Diff**: Retrieve changes from GitHub
2. **AST Analysis**: Parse code structure and extract definitions
3. **Graph Building**: Construct dependency relationships
4. **Impact Traversal**: Identify all affected nodes
5. **Risk Scoring**: Calculate risk based on multiple factors
6. **AI Insights**: Get semantic understanding from IBM watsonx.ai
7. **Test Generation**: Create regression test scenarios
8. **Report Storage**: Save results to database

### Authentication

Currently, the API uses GitHub tokens and IBM watsonx.ai API keys configured 
via environment variables. No per-request authentication is required.

### Rate Limits

- Analysis requests: Recommended max 10 concurrent requests
- Report retrieval: No strict limits
- Batch analysis: Limited to 5 PRs per request

### Support

For issues or questions, please refer to the project documentation or 
contact the development team.
"""

API_VERSION = "1.0.0"
API_TERMS_OF_SERVICE = "https://github.com/your-org/prism"
API_CONTACT = {
    "name": "PRISM Development Team",
    "url": "https://github.com/your-org/prism",
    "email": "support@prism-api.dev"
}
API_LICENSE = {
    "name": "MIT License",
    "url": "https://opensource.org/licenses/MIT"
}

# Tags metadata for grouping endpoints
TAGS_METADATA = [
    {
        "name": "analysis",
        "description": """
        **Code Analysis Operations**
        
        Endpoints for analyzing pull requests and retrieving analysis status.
        The main `/analyze` endpoint triggers the complete analysis pipeline.
        """,
    },
    {
        "name": "reports",
        "description": """
        **Report Management**
        
        Retrieve, list, and manage analysis reports. Reports contain complete
        analysis results including risk scores, impacted components, AI insights,
        and regression test scenarios.
        """,
    },
    {
        "name": "health",
        "description": """
        **System Health & Information**
        
        Health checks and API information endpoints for monitoring and discovery.
        """,
    }
]

# Example request/response payloads
EXAMPLES = {
    "analyze_request": {
        "summary": "Analyze a Pull Request",
        "description": "Analyze PR #123 from the example repository",
        "value": {
            "pr_id": "123",
            "repository": "owner/repo-name"
        }
    },
    "analyze_response": {
        "summary": "Successful Analysis",
        "description": "Complete analysis results with risk assessment",
        "value": {
            "report_id": 1,
            "pr_id": "123",
            "repository": "owner/repo-name",
            "pr_url": "https://github.com/owner/repo-name/pull/123",
            "changed_files": [
                {
                    "path": "src/services/user_service.py",
                    "status": "modified",
                    "additions": 45,
                    "deletions": 12,
                    "changes": 57
                }
            ],
            "impacted_nodes": [
                {
                    "name": "UserService.authenticate",
                    "type": "function",
                    "file": "src/services/user_service.py",
                    "impact_level": "high",
                    "dependencies": ["Database", "AuthProvider"]
                }
            ],
            "risk_score": 7.5,
            "risk_level": "high",
            "risk_factors": {
                "complexity_score": 8.2,
                "impact_breadth": 6.5,
                "critical_path": True,
                "test_coverage": 0.75
            },
            "semantic_insights": {
                "summary": "Authentication logic modified with potential security implications",
                "concerns": [
                    "Password validation logic changed",
                    "Session management updated"
                ],
                "recommendations": [
                    "Add security audit",
                    "Review authentication flow",
                    "Update integration tests"
                ]
            },
            "regression_scenarios": [
                {
                    "scenario": "Test user login with valid credentials",
                    "priority": "high",
                    "test_type": "integration"
                }
            ],
            "analysis_duration": 3.45,
            "created_at": "2026-05-16T08:00:00Z"
        }
    },
    "report_response": {
        "summary": "Report Details",
        "description": "Complete report with all analysis data",
        "value": {
            "id": 1,
            "pr_id": "123",
            "repository": "owner/repo-name",
            "pr_url": "https://github.com/owner/repo-name/pull/123",
            "status": "completed",
            "risk_score": 7.5,
            "risk_level": "high",
            "changed_files": [],
            "impacted_nodes": [],
            "risk_factors": {},
            "semantic_insights": {},
            "regression_scenarios": [],
            "analysis_duration": 3.45,
            "created_at": "2026-05-16T08:00:00Z",
            "error_message": None
        }
    }
}

# Swagger UI configuration
SWAGGER_UI_PARAMETERS = {
    "deepLinking": True,
    "displayRequestDuration": True,
    "filter": True,
    "showExtensions": True,
    "showCommonExtensions": True,
    "syntaxHighlight.theme": "monokai",
    "tryItOutEnabled": True,
    "persistAuthorization": True,
    "displayOperationId": True,
}

# ReDoc configuration
REDOC_OPTIONS = {
    "hideDownloadButton": False,
    "expandResponses": "200,201",
    "pathInMiddlePanel": True,
    "nativeScrollbars": True,
    "theme": {
        "colors": {
            "primary": {
                "main": "#2196F3"
            }
        },
        "typography": {
            "fontSize": "14px",
            "fontFamily": "Roboto, sans-serif",
            "headings": {
                "fontFamily": "Roboto, sans-serif"
            }
        }
    }
}

# Made with Bob