# PRISM Backend API Contract

**Version:** 1.0  
**Status:** Frozen for CLI implementation  
**Last Updated:** 2026-05-16

This document defines the contract between the PRISM CLI and the backend API. This contract is **frozen** - the CLI implementation depends on these exact schemas.

---

## Table of Contents

- [Overview](#overview)
- [Base URL](#base-url)
- [Authentication](#authentication)
- [Endpoints](#endpoints)
  - [Health Check](#health-check)
  - [Run Analysis](#run-analysis)
- [Data Models](#data-models)
- [Error Handling](#error-handling)
- [Examples](#examples)

---

## Overview

The PRISM CLI communicates with the backend via REST API. All requests use JSON payloads, and all responses return JSON.

### Design Principles

1. **Synchronous** - Single POST request, wait for complete response
2. **Stateless** - No session management required
3. **Simple** - Minimal endpoints, clear schemas
4. **Reliable** - Predictable error responses

---

## Base URL

The backend base URL is configurable via environment variable:

```env
PRISM_BACKEND_URL=http://localhost:8000
```

**Default:** `http://localhost:8000`  
**Production:** `https://api.prism.dev` (example)

---

## Authentication

### GitHub Token

The CLI passes a GitHub Personal Access Token to the backend, which uses it to fetch PR diffs via GitHub API.

**Token Format:** `ghp_` followed by 36 alphanumeric characters

**Required Scopes:**

- `repo` - For private repositories
- `public_repo` - For public repositories only

**Security:**

- Token is passed in request body (not headers)
- Backend should validate token before use
- Backend should not store tokens

---

## Endpoints

### Health Check

Check if the backend is running and responsive.

#### Request

```http
GET /healthz HTTP/1.1
Host: localhost:8000
```

**No request body required**

#### Response (200 OK)

```json
{
  "ok": true
}
```

**Response Time:** < 100ms (should be fast, no DB queries)

#### Purpose

- Pre-flight check before analysis
- Monitoring and health checks
- Quick validation during demos

#### CLI Usage

```python
# cli/client.py
def check_health(self) -> bool:
    response = self.client.get(f"{self.backend_url}/healthz", timeout=2.0)
    return response.status_code == 200 and response.json().get("ok") == True
```

---

### Run Analysis

Analyze a pull request and return risk assessment.

#### Request

```http
POST /api/analysis/run HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "pr_identifier": "pr-142",
  "repository_url": "https://github.com/owner/repo",
  "github_token": "ghp_1234567890abcdefghijklmnopqrstuvwxyz"
}
```

#### Request Schema

```typescript
interface AnalysisRequest {
  pr_identifier: string; // PR identifier (e.g., "pr-142", "#142", "142")
  repository_url: string; // Full GitHub repo URL
  github_token?: string; // Optional for public repos
}
```

**Field Descriptions:**

| Field            | Type   | Required | Description                                                         |
| ---------------- | ------ | -------- | ------------------------------------------------------------------- |
| `pr_identifier`  | string | Yes      | PR number or identifier. Formats: "pr-142", "#142", "142"           |
| `repository_url` | string | Yes      | Full GitHub repository URL. Format: `https://github.com/owner/repo` |
| `github_token`   | string | No       | GitHub PAT. Required for private repos, optional for public         |

**Validation Rules:**

- `pr_identifier`: Non-empty string, may include "pr-" prefix or "#"
- `repository_url`: Valid GitHub URL format
- `github_token`: If provided, must start with `ghp_`

#### Response (200 OK)

```json
{
  "report_id": "8sj2kd",
  "dashboard_url": "http://localhost:3000/report/8sj2kd",
  "risk_score": 82,
  "risk_label": "HIGH",
  "impacted_node_count": 14,
  "status": "COMPLETE"
}
```

#### Response Schema

```typescript
interface AnalysisResponse {
  report_id: string; // Unique report identifier (UUID or short ID)
  dashboard_url: string; // Full URL to view report in dashboard
  risk_score: number; // Risk score 0-100
  risk_label: "LOW" | "MEDIUM" | "HIGH"; // Risk category
  impacted_node_count: number; // Number of impacted code nodes
  status: "COMPLETE" | "PARTIAL"; // Analysis completion status
}
```

**Field Descriptions:**

| Field                 | Type   | Description                                                             |
| --------------------- | ------ | ----------------------------------------------------------------------- |
| `report_id`           | string | Unique identifier for this analysis report                              |
| `dashboard_url`       | string | Full URL to view detailed report in web dashboard                       |
| `risk_score`          | number | Computed risk score from 0 (safe) to 100 (high risk)                    |
| `risk_label`          | enum   | Human-readable risk category: LOW (0-40), MEDIUM (41-70), HIGH (71-100) |
| `impacted_node_count` | number | Number of code nodes affected by this PR                                |
| `status`              | enum   | COMPLETE = full analysis, PARTIAL = some services unavailable           |

**Response Time:** 15-30 seconds (includes AST parsing, graph building, AI service calls)

#### Status Codes

| Code | Meaning             | CLI Action                        |
| ---- | ------------------- | --------------------------------- |
| 200  | Success             | Parse response, render summary    |
| 400  | Bad Request         | Show validation error to user     |
| 401  | Unauthorized        | Show auth error, check token      |
| 404  | Not Found           | PR or repository not found        |
| 422  | Validation Error    | Show field-specific errors        |
| 500  | Server Error        | Show backend error, suggest retry |
| 503  | Service Unavailable | Backend overloaded or down        |

---

## Data Models

### Risk Score Calculation

```
Risk Score = weighted_sum(
  complexity_score,
  impact_breadth,
  semantic_risk_count,
  critical_path_affected
)

Range: 0-100
```

### Risk Labels

| Label  | Score Range | Color     | Meaning                                       |
| ------ | ----------- | --------- | --------------------------------------------- |
| LOW    | 0-40        | 🟢 Green  | Minimal impact, safe to merge                 |
| MEDIUM | 41-70       | 🟡 Yellow | Moderate impact, review carefully             |
| HIGH   | 71-100      | 🔴 Red    | Significant impact, thorough testing required |

### Status Values

| Status   | Meaning                                      | CLI Behavior                   |
| -------- | -------------------------------------------- | ------------------------------ |
| COMPLETE | All services succeeded                       | Show full summary              |
| PARTIAL  | Some services failed (e.g., AI service timeout) | Show summary with warning note |

**PARTIAL Status Example:**

```
⚠ AI service unavailable — graph and score are still valid.
```

---

## Error Handling

### Error Response Format

All error responses follow FastAPI's standard format:

```json
{
  "detail": "Human-readable error message"
}
```

### Common Errors

#### 400 Bad Request

```json
{
  "detail": "Invalid repository URL format"
}
```

**Causes:**

- Malformed repository URL
- Invalid PR identifier format
- Missing required fields

#### 401 Unauthorized

```json
{
  "detail": "GitHub authentication failed"
}
```

**Causes:**

- Invalid or expired GitHub token
- Token lacks required scopes
- Token revoked

#### 404 Not Found

```json
{
  "detail": "Pull request #142 not found in repository"
}
```

**Causes:**

- PR doesn't exist
- Repository doesn't exist
- No access to private repository

#### 422 Validation Error

```json
{
  "detail": [
    {
      "loc": ["body", "pr_identifier"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Causes:**

- Pydantic validation failure
- Type mismatch
- Missing required field

#### 500 Internal Server Error

```json
{
  "detail": "Analysis pipeline failed: AST parsing error"
}
```

**Causes:**

- Backend service failure
- Database connection error
- Unexpected exception

#### 503 Service Unavailable

```json
{
  "detail": "Backend is temporarily unavailable"
}
```

**Causes:**

- Backend starting up
- Overloaded with requests
- Maintenance mode

---

## Examples

### Example 1: Successful Analysis

**Request:**

```bash
curl -X POST http://localhost:8000/api/analysis/run \
  -H "Content-Type: application/json" \
  -d '{
    "pr_identifier": "pr-142",
    "repository_url": "https://github.com/prism-demo/payment-service",
    "github_token": "ghp_1234567890abcdefghijklmnopqrstuvwxyz"
  }'
```

**Response (200):**

```json
{
  "report_id": "8sj2kd",
  "dashboard_url": "http://localhost:3000/report/8sj2kd",
  "risk_score": 82,
  "risk_label": "HIGH",
  "impacted_node_count": 14,
  "status": "COMPLETE"
}
```

### Example 2: Partial Analysis (AI Service Unavailable)

**Request:** Same as Example 1

**Response (200):**

```json
{
  "report_id": "9tk3lm",
  "dashboard_url": "http://localhost:3000/report/9tk3lm",
  "risk_score": 65,
  "risk_label": "MEDIUM",
  "impacted_node_count": 8,
  "status": "PARTIAL"
}
```

**CLI Output:**

```
⚠ AI service unavailable — graph and score are still valid.
```

### Example 3: Authentication Error

**Request:**

```json
{
  "pr_identifier": "pr-142",
  "repository_url": "https://github.com/private-org/private-repo",
  "github_token": "invalid_token"
}
```

**Response (401):**

```json
{
  "detail": "GitHub authentication failed: Bad credentials"
}
```

### Example 4: PR Not Found

**Request:**

```json
{
  "pr_identifier": "pr-99999",
  "repository_url": "https://github.com/owner/repo",
  "github_token": "ghp_valid_token"
}
```

**Response (404):**

```json
{
  "detail": "Pull request #99999 not found in repository owner/repo"
}
```

### Example 5: Validation Error

**Request:**

```json
{
  "pr_identifier": "pr-142"
  // Missing repository_url
}
```

**Response (422):**

```json
{
  "detail": [
    {
      "loc": ["body", "repository_url"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## CLI Implementation Guide

### Request Building

```python
# cli/client.py
class AnalysisClient:
    def run(
        self,
        pr_identifier: str,
        repository_url: str,
        github_token: str | None = None
    ) -> AnalysisResponse:
        payload = {
            "pr_identifier": pr_identifier,
            "repository_url": repository_url,
        }
        if github_token:
            payload["github_token"] = github_token

        response = self.client.post(
            f"{self.backend_url}/api/analysis/run",
            json=payload,
            timeout=self.timeout
        )

        response.raise_for_status()
        return AnalysisResponse(**response.json())
```

### Response Parsing

```python
# cli/client.py
from pydantic import BaseModel
from typing import Literal

class AnalysisResponse(BaseModel):
    report_id: str
    dashboard_url: str
    risk_score: int
    risk_label: Literal["LOW", "MEDIUM", "HIGH"]
    impacted_node_count: int
    status: Literal["COMPLETE", "PARTIAL"]
```

### Error Handling

```python
# cli/client.py
try:
    response = self.run(pr_id, repo_url, token)
except httpx.ConnectError:
    raise BackendUnreachable(f"Cannot connect to {self.backend_url}")
except httpx.TimeoutException:
    raise BackendTimeout(f"Request timed out after {self.timeout}s")
except httpx.HTTPStatusError as e:
    if e.response.status_code == 401:
        raise AuthError("GitHub authentication failed")
    elif e.response.status_code == 404:
        raise NotFoundError("PR or repository not found")
    else:
        detail = e.response.json().get("detail", "Unknown error")
        raise BackendError(detail)
```

---

## Testing

### Mock Backend for CLI Tests

```python
# tests/test_client.py
import httpx
from unittest.mock import Mock

def test_successful_analysis():
    mock_response = {
        "report_id": "test123",
        "dashboard_url": "http://localhost:3000/report/test123",
        "risk_score": 50,
        "risk_label": "MEDIUM",
        "impacted_node_count": 5,
        "status": "COMPLETE"
    }

    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json=mock_response)
    )

    client = AnalysisClient(backend_url="http://test", transport=transport)
    result = client.run("pr-142", "https://github.com/owner/repo")

    assert result.risk_score == 50
    assert result.risk_label == "MEDIUM"
```

---

## Backend Implementation Checklist

For backend developers implementing this API:

- [ ] Implement `GET /healthz` endpoint
- [ ] Implement `POST /api/analysis/run` endpoint
- [ ] Validate request schema with Pydantic
- [ ] Handle GitHub API authentication
- [ ] Fetch PR diff from GitHub
- [ ] Run analysis pipeline (AST, graph, AI service, risk scoring)
- [ ] Generate report ID and dashboard URL
- [ ] Return response matching schema exactly
- [ ] Handle errors gracefully with clear messages
- [ ] Add request timeout handling (60s default)
- [ ] Log requests for debugging
- [ ] Add rate limiting (optional)
- [ ] Support demo fixture PR (pr-142 on prism-demo/payment-service)

---

## Demo Mode Support

The backend must recognize and handle the demo fixture:

**Demo Request:**

```json
{
  "pr_identifier": "pr-142",
  "repository_url": "https://github.com/prism-demo/payment-service"
}
```

**Expected Behavior:**

- Return pre-baked impressive results
- No actual GitHub API call needed
- Fast response (< 2 seconds)
- Always succeeds (for demo reliability)

**Demo Response:**

```json
{
  "report_id": "demo-8sj2kd",
  "dashboard_url": "http://localhost:3000/report/demo-8sj2kd",
  "risk_score": 82,
  "risk_label": "HIGH",
  "impacted_node_count": 14,
  "status": "COMPLETE"
}
```

---

## Version History

| Version | Date       | Changes                     |
| ------- | ---------- | --------------------------- |
| 1.0     | 2026-05-16 | Initial contract definition |

---

## Related Documentation

- **CLI Architecture:** [`CLI_PLAN.md`](CLI_PLAN.md)
- **CLI README:** [`README.md`](README.md)
- **Environment Setup:** [`ENV_CONFIGURATION.md`](ENV_CONFIGURATION.md)
- **Development Guide:** [`DEVELOPMENT.md`](DEVELOPMENT.md)

---

**Contract Status:** ✅ Frozen  
**Breaking Changes:** Require CLI version bump  
**Questions:** Contact backend team lead
