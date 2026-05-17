# PRISM CLI ↔ Frontend Integration Guide

**Version:** 1.0  
**Last Updated:** 2026-05-17  
**Status:** ✅ Complete & Tested

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Setup Instructions](#setup-instructions)
4. [Usage Guide](#usage-guide)
5. [Integration Flow](#integration-flow)
6. [API Reference](#api-reference)
7. [Troubleshooting](#troubleshooting)
8. [Testing](#testing)

---

## Overview

PRISM (Pull Request Intelligent Semantic Monitor) consists of three integrated components:

1. **CLI** - Command-line tool for developers (`prism analyze`)
2. **Backend** - FastAPI server for analysis pipeline
3. **Frontend** - React dashboard for visualization

This document explains how these components work together and how to use them.

---

## Architecture

### System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER ENTRY POINTS                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  CLI Entry:                    Web Entry:                       │
│  $ prism analyze pr-142        http://localhost:3000/           │
│         │                              │                         │
│         └──────────────┬───────────────┘                         │
│                        ▼                                         │
│              POST /api/analysis/run                              │
│              {pr_identifier, repository_url}                     │
│                        │                                         │
│                        ▼                                         │
│              ┌─────────────────┐                                 │
│              │  FastAPI Backend │                                │
│              │  - Fetch PR diff │                                │
│              │  - AST analysis  │                                │
│              │  - Build graph   │                                │
│              │  - IBM Bob       │                                │
│              │  - Risk scoring  │                                │
│              └────────┬─────────┘                                │
│                       │                                          │
│                       ▼                                          │
│              Store in Database                                   │
│              (SQLite/PostgreSQL)                                 │
│                       │                                          │
│         ┌─────────────┴─────────────┐                            │
│         ▼                           ▼                            │
│   CLI Response:              Frontend Reads:                     │
│   {report_id: "abc123de",    GET /api/reports/abc123de          │
│    dashboard_url,            (Full report data)                  │
│    risk_score,                       │                           │
│    risk_label}                       ▼                           │
│         │                    React Dashboard                     │
│         │                    - Dependency graph                  │
│         └──> Opens Browser   - Risk summary                      │
│              to dashboard    - IBM Bob insights                  │
│                              - Regression scenarios              │
└─────────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

1. **Single Canonical Endpoint**: Both CLI and web use `POST /api/analysis/run`
2. **String Report IDs**: 8-character deterministic hashes (e.g., "abc123de")
3. **Port 3000**: Frontend always runs on port 3000 (matches documentation)
4. **Direct Navigation**: CLI opens browser directly to `/report/:id`
5. **Backward Compatible**: Backend accepts both string and numeric IDs

---

## Setup Instructions

### Prerequisites

- **Python 3.13+** (for CLI and backend)
- **Node.js 18+** (for frontend)
- **Git** (for repository detection)
- **GitHub Token** (optional, for private repos)

### 1. Backend Setup

```bash
# Navigate to project root
cd d:/Hackathon/PRISM

# Install backend dependencies
pip install -r requirements.txt

# Start backend server
python start_backend.py

# Verify backend is running
curl http://localhost:8000/healthz
# Expected: {"ok": true}
```

**Backend runs on:** `http://localhost:8000`

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend/prism

# Install dependencies
npm install

# Start development server
npm run dev

# Frontend will start on port 3000
```

**Frontend runs on:** `http://localhost:3000`

**Important:** The frontend is configured to run on port 3000 with `strictPort: true`. If port 3000 is already in use, the server will fail with an error. Free up port 3000 or change the configuration in `vite.config.js`.

### 3. CLI Setup

```bash
# Navigate to CLI directory
cd cli

# Install CLI in development mode
pip install -e .

# Verify installation
prism --help
prism version
```

### 4. Environment Configuration

Create a `.env` file in the CLI directory:

```env
# Backend URL (default: http://localhost:8000)
PRISM_BACKEND_URL=http://localhost:8000

# GitHub Personal Access Token (optional for public repos)
PRISM_GITHUB_TOKEN=ghp_your_token_here

# Default repository (optional)
PRISM_REPO_URL=https://github.com/your-org/your-repo
```

**GitHub Token Scopes Required:**

- `repo` - For private repositories
- `public_repo` - For public repositories only

---

## Usage Guide

### CLI Usage

#### 1. Basic Analysis

```bash
# Analyze a PR (auto-detects repository from git remote)
prism analyze pr-142

# Analyze with explicit repository
prism analyze pr-142 --repo https://github.com/owner/repo

# Analyze and open dashboard automatically
prism analyze pr-142 --open
```

#### 2. Demo Mode (Bulletproof)

```bash
# Run pre-baked demo (always works)
prism demo

# Demo with custom backend
prism demo --backend http://localhost:8000
```

#### 3. Advanced Options

```bash
# Override backend URL
prism analyze pr-142 --backend http://production-backend.com

# Provide GitHub token inline
prism analyze pr-142 --token ghp_your_token_here

# JSON output (for CI/CD integration)
prism analyze pr-142 --json
```

#### 4. CLI Output Example

```
Detected repo: https://github.com/owner/repo

✓ Pull request analyzed
✓ Dependency graph constructed
✓ 14 impacted nodes identified
⚠ 3 semantic risks detected
✓ Regression scenarios generated

Risk Score: HIGH (82/100)

Open full analysis:
http://localhost:3000/report/8sj2kd
```

### Web Interface Usage

#### 1. Access the Dashboard

Open your browser to: `http://localhost:3000/`

#### 2. Analyze a Pull Request

1. Enter **Pull Request ID** (e.g., `142` or `pr-142`)
2. Enter **Repository** (e.g., `owner/repo` or full URL)
3. Click **"Analyze Pull Request"**
4. Watch the terminal animation
5. Automatically redirected to dashboard

#### 3. View Analysis Results

The dashboard displays:

- **Risk Summary Card**
  - Risk score (0-100)
  - Risk level (LOW/MEDIUM/HIGH)
  - Impacted node count
  - Changed files list

- **Dependency Graph** (Interactive)
  - Pan, zoom, drag nodes
  - Color-coded by impact
  - Click nodes for details

- **AI Insights Panel**
  - IBM Bob semantic analysis
  - Plain-language risk explanations
  - Architectural impact summary

- **Regression Scenarios**
  - Generated test scenarios
  - Priority levels
  - Affected components
  - Test steps

#### 4. Direct Report Access

If you have a report ID from the CLI:

```
http://localhost:3000/report/8sj2kd
```

---

## Integration Flow

### Flow 1: CLI → Dashboard

```
Developer Terminal:
$ prism analyze pr-142 --open

↓ (CLI sends request)

Backend:
POST /api/analysis/run
{
  "pr_identifier": "pr-142",
  "repository_url": "https://github.com/owner/repo"
}

↓ (Backend processes)

Backend Response:
{
  "report_id": "8sj2kd",
  "dashboard_url": "http://localhost:3000/report/8sj2kd",
  "risk_score": 82,
  "risk_label": "HIGH",
  "impacted_node_count": 14,
  "status": "COMPLETE"
}

↓ (CLI displays summary)

Terminal Output:
Risk Score: HIGH (82/100)
Open full analysis: http://localhost:3000/report/8sj2kd

↓ (CLI opens browser)

Browser:
http://localhost:3000/report/8sj2kd

↓ (Frontend fetches full report)

Frontend:
GET /api/reports/8sj2kd

↓ (Renders dashboard)

Dashboard displays full analysis
```

### Flow 2: Web Form → Dashboard

```
Browser:
http://localhost:3000/

↓ (User fills form)

Form Submission:
PR ID: pr-142
Repository: owner/repo

↓ (Frontend sends request)

Frontend:
POST /api/analysis/run
{
  "pr_identifier": "pr-142",
  "repository_url": "https://github.com/owner/repo"
}

↓ (Backend processes - same as CLI)

Backend Response:
{
  "report_id": "abc123de",
  "dashboard_url": "http://localhost:3000/report/abc123de",
  ...
}

↓ (Frontend navigates)

Browser:
http://localhost:3000/report/abc123de

↓ (Same as CLI flow from here)

Dashboard displays full analysis
```

---

## API Reference

### Canonical Endpoint (CLI Contract)

#### POST /api/analysis/run

**Description:** Run full semantic analysis on a pull request.

**Request:**

```json
{
  "pr_identifier": "pr-142",
  "repository_url": "https://github.com/owner/repo",
  "github_token": "ghp_..." // optional
}
```

**Response (200 OK):**

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

**Status Values:**

- `COMPLETE` - Full analysis succeeded
- `PARTIAL` - Some services failed (e.g., IBM Bob timeout)

**Risk Labels:**

- `LOW` (0-40) - Minimal impact, safe to merge
- `MEDIUM` (41-70) - Moderate impact, review carefully
- `HIGH` (71-100) - Significant impact, thorough testing required

### Report Retrieval

#### GET /api/reports/{report_id}

**Description:** Get full report by ID (accepts string or number).

**Parameters:**

- `report_id` - String (e.g., "8sj2kd") or Number (e.g., 123)

**Response (200 OK):**

```json
{
  "id": 123,
  "report_id": "8sj2kd",
  "pr_id": "pr-142",
  "repository": "https://github.com/owner/repo",
  "changed_files": ["src/payment.py", "src/analytics.py"],
  "impacted_nodes": ["PaymentService", "AnalyticsService", ...],
  "risk_score": 82,
  "risk_level": "HIGH",
  "risk_factors": {...},
  "semantic_insights": "...",
  "regression_scenarios": [...],
  "dependency_graph": {...},
  "created_at": "2026-05-17T09:00:00Z",
  "status": "completed"
}
```

### Health Check

#### GET /healthz

**Description:** Check if backend is running.

**Response (200 OK):**

```json
{
  "ok": true
}
```

---

## Troubleshooting

### Common Issues

#### 1. Frontend Not on Port 3000

**Symptom:** Frontend starts on port 5173 instead of 3000

**Solution:**

```bash
# Check vite.config.js has:
server: {
  port: 3000,
  strictPort: true,
}

# If port 3000 is in use, find and kill the process:
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:3000 | xargs kill -9
```

#### 2. CLI Opens Wrong URL

**Symptom:** CLI opens `http://localhost:5173/report/...`

**Cause:** Backend hardcoded wrong port

**Solution:** Backend should return `http://localhost:3000/report/...` in `dashboard_url`

#### 3. Report Not Found (404)

**Symptom:** Dashboard shows "Report not found"

**Possible Causes:**

- Report ID doesn't exist in database
- Backend not running
- Database connection issue

**Solution:**

```bash
# Check backend is running
curl http://localhost:8000/healthz

# Check report exists
curl http://localhost:8000/api/reports/8sj2kd

# Check backend logs for errors
```

#### 4. CORS Errors

**Symptom:** Browser console shows CORS errors

**Solution:** Backend must allow `http://localhost:3000`:

```python
# backend/config.py or backend/app.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 5. Type Errors in Frontend

**Symptom:** TypeScript errors about `report_id` type mismatch

**Solution:** Ensure all types use `string` for `report_id`:

- `AnalyzeResponse.report_id: string`
- `AnalysisRunResponse.report_id: string`
- `ReportResponse.report_id?: string`
- `TerminalWindow.reportId?: string`

#### 6. CLI Can't Detect Repository

**Symptom:** "Missing repository URL" error

**Solutions:**

```bash
# Option 1: Run from inside git repository
cd /path/to/repo
prism analyze pr-142

# Option 2: Provide --repo flag
prism analyze pr-142 --repo https://github.com/owner/repo

# Option 3: Set environment variable
export PRISM_REPO_URL=https://github.com/owner/repo
prism analyze pr-142
```

---

## Testing

### Manual Testing Checklist

#### ✅ Backend Tests

```bash
# 1. Health check
curl http://localhost:8000/healthz
# Expected: {"ok": true}

# 2. Demo endpoint
curl -X POST http://localhost:8000/api/analysis/run \
  -H "Content-Type: application/json" \
  -d '{"pr_identifier":"pr-142","repository_url":"https://github.com/prism-demo/payment-service"}'
# Expected: 200 OK with report_id

# 3. Report retrieval (string ID)
curl http://localhost:8000/api/reports/demo8chr
# Expected: 200 OK with full report

# 4. Report retrieval (numeric ID)
curl http://localhost:8000/api/reports/1
# Expected: 200 OK with full report
```

#### ✅ CLI Tests

```bash
# 1. Version check
prism version
# Expected: prism X.X.X

# 2. Help text
prism --help
# Expected: Command list displayed

# 3. Demo mode
prism demo
# Expected: Terminal output + browser opens

# 4. Analysis with auto-detect
cd /path/to/git/repo
prism analyze pr-142
# Expected: Analysis runs, summary displayed

# 5. Analysis with explicit repo
prism analyze pr-142 --repo https://github.com/owner/repo
# Expected: Analysis runs, summary displayed

# 6. JSON output
prism analyze pr-142 --json
# Expected: Valid JSON output

# 7. Open browser flag
prism analyze pr-142 --open
# Expected: Browser opens to dashboard
```

#### ✅ Frontend Tests

```bash
# 1. Port verification
npm run dev
# Expected: "Local: http://localhost:3000/"

# 2. Home page loads
# Open: http://localhost:3000/
# Expected: Splash screen with form

# 3. Form submission
# Enter PR ID: pr-142
# Enter Repository: owner/repo
# Click "Analyze Pull Request"
# Expected: Terminal animation → Navigate to /report/:id

# 4. Direct report URL
# Open: http://localhost:3000/report/demo8chr
# Expected: Dashboard loads with report data

# 5. Invalid report ID
# Open: http://localhost:3000/report/invalid123
# Expected: Error message (not redirect loop)
```

#### ✅ Integration Tests

```bash
# End-to-end flow 1: CLI → Browser → Dashboard
prism demo
# Verify:
# 1. Terminal shows summary
# 2. Browser opens automatically
# 3. Dashboard loads on port 3000
# 4. Report data displays correctly

# End-to-end flow 2: Web Form → Dashboard
# 1. Open http://localhost:3000/
# 2. Enter PR ID and repository
# 3. Submit form
# Verify:
# 4. Terminal animation plays
# 5. Navigates to /report/:id
# 6. Dashboard loads with same data
```

### Automated Tests

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests (if configured)
cd frontend/prism
npm test

# CLI tests
cd cli
pytest tests/ -v
```

---

## Best Practices

### For Developers Using PRISM

1. **Always run `prism demo` first** - Verifies setup before analyzing real PRs
2. **Use `--open` flag** - Automatically opens dashboard for quick review
3. **Check backend health** - Run `curl http://localhost:8000/healthz` if issues occur
4. **Keep GitHub token secure** - Use environment variables, never commit tokens
5. **Review dashboard thoroughly** - Don't rely solely on CLI summary

### For PRISM Developers

1. **Never change port 3000** - All documentation assumes this port
2. **Keep API contract frozen** - CLI depends on exact response schema
3. **Support both ID types** - Backend must accept string and numeric IDs
4. **Test demo mode** - Must always work for reliable presentations
5. **Document breaking changes** - Update this guide for any API changes

---

## Additional Resources

- **CLI Architecture:** `cli/CLI_PLAN.md`
- **API Contract:** `cli/API_CONTRACT.md`
- **Frontend README:** `frontend/prism/FRONTEND_README.md`
- **Backend API Docs:** `http://localhost:8000/docs` (when running)
- **Project PRD:** `Required Docs/PRD.md`
- **Tech Specs:** `Required Docs/TECH_SPECS__1_ (1).md`

---

## Support

For issues or questions:

1. Check this documentation
2. Review troubleshooting section
3. Check backend logs: `python start_backend.py`
4. Check frontend console: Browser DevTools → Console
5. Check CLI verbose output: `prism analyze pr-142 --verbose` (if implemented)

---

**Document Version:** 1.0  
**Last Updated:** 2026-05-17  
**Maintained By:** PRISM Development Team
