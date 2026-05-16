# PRISM Architecture Notes & Deviations

**Last Updated:** 2026-05-16  
**Purpose:** Document intentional deviations from TECH_SPEC and architectural decisions

---

## Database Architecture

### SQLite vs Firebase/Firestore

**TECH_SPEC Requirement:** Firebase (Firestore) as database  
**Actual Implementation:** SQLite + SQLAlchemy  
**Reason:** Hackathon pragmatism - SQLite requires zero external setup, no credentials, and works immediately for demo purposes.

**Trade-offs:**
- ✅ **Pros:** Zero setup, portable, works offline, simple for demo
- ❌ **Cons:** Not suitable for production concurrent access, no real-time features, limited scalability

**Production Migration Path:**
1. Replace `backend/db.py` with Firebase Admin SDK initialization
2. Update `backend/repositories/report_repository.py` to use Firestore document operations
3. Remove SQLAlchemy models from `backend/models/`
4. Update frontend to read directly from Firestore (remove backend report retrieval endpoints)

**Current Risks:**
- `check_same_thread=False` in SQLite config (line 14 of `backend/db.py`) allows multi-threaded access but risks data corruption
- No connection pooling or lock handling - concurrent writes may fail with "database is locked" errors

---

## API Endpoints

### Dual Analysis Endpoints

**TECH_SPEC Requirement:** Only `POST /api/analysis/run`  
**Actual Implementation:** Two endpoints with different schemas

1. **`POST /api/analysis/run`** (CLI Contract)
   - Returns: `AnalysisResponse` with string `report_id`, int `risk_score`, string `risk_label`
   - Used by: CLI
   - Status: Fully functional

2. **`POST /api/analyze`** (Legacy/Frontend)
   - Returns: `AnalyzeResponse` with int `report_id`, float `risk_score`, string `risk_level`, plus full analysis details
   - Used by: Frontend dashboard
   - Status: Fully functional

**Reason:** Frontend was built against `/api/analyze` before CLI contract was finalized. Both work correctly for their respective consumers.

**Recommendation:** Unify to single endpoint or clearly document which is canonical.

---

## Extra Backend Endpoints (Beyond TECH_SPEC)

The following endpoints exist but are not specified in TECH_SPEC:

- `GET /api/analyze/status/{report_id}` - Get analysis status
- `POST /api/analyze/batch` - Batch analysis (simplified implementation)
- `GET /api/reports/` - List all reports
- `GET /api/reports/{id}` - Get report by ID
- `GET /api/reports/pr/{pr_id}` - Get reports for specific PR
- `DELETE /api/reports/{id}` - Delete report
- `GET /api/reports/stats/summary` - Report statistics
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /healthz` - Health check (CLI contract)
- `GET /api/info` - API information

**Status:** All functional, provide useful utility for development and debugging.

**Note:** `/api/info` currently advertises `POST /api/analyze` as primary endpoint (should be `/api/analysis/run` per CLI contract).

---

## Analysis Pipeline

### File Processing Limits

**Original Implementation:** 
- AST analysis limited to first 10 changed files
- Regression generator capped at 10 total scenarios
- File scenarios limited to 5 files
- Impact scenarios limited to 10 nodes, 3 files

**Fixed Implementation:**
- ✅ All changed files now analyzed (no arbitrary limit)
- ✅ Regression scenarios no longer capped at 10
- ✅ Ensures at least 3 scenarios per high-risk path (PRD requirement)
- ✅ All impacted nodes and files processed

---

## External API Integration

### Retry Logic & Rate Limiting

**IBM Bob (watsonx.ai) Client:**
- ✅ Retry logic implemented: 3 attempts with exponential backoff
- ✅ Retries on: 429 (rate limit), 502 (bad gateway), 503 (service unavailable), timeouts
- ✅ Backoff: 1s → 2s → 4s
- ✅ Graceful degradation on final failure

**GitHub API Client:**
- ✅ Retry logic implemented: 3 attempts with exponential backoff
- ✅ Rate limit detection: Checks `X-RateLimit-Remaining` header
- ✅ Rate limit handling: Waits for `X-RateLimit-Reset` time (capped at 60s)
- ✅ Empty token handling: Only includes Authorization header when token provided
- ❌ No connection pooling (creates new client per request)

---

## Cross-File Dependency Resolution

**Status:** NOT IMPLEMENTED  
**Impact:** `element.dependencies` is always empty, cross-file impact analysis incomplete

**Current Behavior:**
- AST analyzer extracts elements from individual files
- Graph builder can only infer dependencies within same file (imports)
- No function call tracking across files
- No cross-module dependency resolution

**Why Not Fixed:**
- Requires significant refactoring of AST analyzer
- Needs symbol table/scope analysis across entire codebase
- Complex for multiple languages (Python, JS, TS)
- Time-intensive for hackathon scope

**Workaround:** Graph builder uses import statements to infer file-level dependencies.

---

## Demo Infrastructure

### Demo Passthrough

**Implementation:** `backend/analysis.py` module provides:
- Demo PR detection (`is_demo()`)
- Canned response for demo PR (instant, no external API calls)
- Heuristic scoring from PR metadata
- Graceful degradation on GitHub API failures

**Demo PR:** `pr-142` in `prism-demo/payment-service` repository

### Sample Repository

**TECH_SPEC Requirement:** Pre-structured `demo/sample_repo/` directory  
**Actual Status:** Directory empty, only `demo/sample_pr_diff.txt` exists

**Recommendation:** Populate with sample Python/TypeScript project for reliable graph traversal demo.

---

## Test Coverage

### Fixed Test Issues

1. ✅ `test_main.py` - Fixed `--json` visibility assertion (now correctly expects hidden)
2. ✅ `test_client.py` - Fixed attribute name (`client.client` → `client._client`, 8 occurrences)
3. ✅ Created `backend/app.py` - Unblocks `prism backend serve` and backend tests
4. ✅ Created `backend/analysis.py` - Unblocks test suite with demo functionality

### Empty Test Files

The following test files exist but contain no tests:
- `tests/test_ast_analyzer.py` (0 lines)
- `tests/test_graph_builder.py` (0 lines)
- `tests/test_impact_traverser.py` (0 lines)
- `tests/test_risk_scorer.py` (0 lines)

**Impact:** Core services have zero test coverage.

---

## Risk Scoring

### Three-Tier vs Four-Tier System

**TECH_SPEC:** 3 tiers - LOW (0-33), MEDIUM (34-66), HIGH (67-100)  
**Implementation:** Risk scorer uses 3-tier system correctly

**CLI Contract:** Expects LOW, MEDIUM, HIGH  
**Status:** ✅ Compliant

---

## Security Considerations

### GitHub Token Handling

- ✅ Token only included in Authorization header when provided
- ✅ Empty/None tokens don't send malformed headers
- ⚠️ Tokens stored in plaintext in `.env` (acceptable for hackathon)

### Database Security

- ⚠️ SQLite file has no encryption
- ⚠️ No authentication on API endpoints
- ⚠️ Report IDs are SHA-1 hashes (predictable but sufficient for demo)

---

## Production Readiness Checklist

### Critical (Must Fix)

- [ ] Migrate from SQLite to PostgreSQL or Firebase
- [ ] Implement proper connection pooling
- [ ] Add authentication/authorization
- [ ] Implement circuit breaker pattern for external APIs
- [ ] Add comprehensive logging and monitoring
- [ ] Implement cross-file dependency resolution

### Important (Should Fix)

- [ ] Add database migration system
- [ ] Implement proper error tracking (Sentry, etc.)
- [ ] Add rate limiting on API endpoints
- [ ] Implement caching layer (Redis)
- [ ] Add comprehensive test coverage
- [ ] Set up CI/CD pipeline

### Nice to Have

- [ ] Add API versioning
- [ ] Implement GraphQL endpoint
- [ ] Add WebSocket support for real-time updates
- [ ] Implement background job queue (Celery)
- [ ] Add metrics and analytics

---

## Performance Characteristics

### Current Limitations

- **Concurrent Requests:** Limited by SQLite (single-writer)
- **Large PRs:** No pagination, all files loaded into memory
- **Graph Size:** NetworkX in-memory, no size limits enforced
- **API Timeouts:** 60s for IBM Bob, 30s for GitHub (may be insufficient for large PRs)

### Optimization Opportunities

1. **Caching:** Cache GitHub API responses, AST analysis results
2. **Async Processing:** Move analysis to background queue
3. **Incremental Analysis:** Only re-analyze changed portions
4. **Graph Persistence:** Store pre-computed graphs for faster analysis

---

## Deployment Notes

### Environment Variables Required

**Backend:**
```
IBM_BOB_API_KEY=<watsonx.ai API key>
IBM_BOB_PROJECT_ID=<watsonx.ai project ID>
GITHUB_TOKEN=<optional, for private repos>
BACKEND_URL=http://localhost:8000
```

**Frontend:**
```
VITE_API_URL=http://localhost:8000
```

### Startup Sequence

1. Start backend: `python start_backend.py` (or `uvicorn backend.main:app`)
2. Start frontend: `cd frontend/prism && npm run dev`
3. CLI available: `prism analyze <pr-id> --repo <url>`

### Demo Mode

For reliable demo without external dependencies:
```bash
prism demo
```

This uses canned response, bypasses GitHub and IBM Bob APIs.

---

## Conclusion

The system is **functional and demo-ready** with known limitations documented above. All critical blocking issues have been resolved. Remaining issues are primarily production-hardening concerns that don't affect hackathon demo viability.

**Recommended Demo Path:** Use `prism demo` command for maximum reliability.