# PRISM Backend Implementation Checklist

## Quick Reference for Implementation

### Phase 1: Foundation ✓ Priority: CRITICAL
- [ ] [`backend/config.py`](backend/config.py) - Settings with pydantic-settings
- [ ] [`backend/db.py`](backend/db.py) - SQLAlchemy setup
- [ ] [`.env.example`](.env.example) - Environment template
- [ ] [`backend/models/base.py`](backend/models/base.py) - Base model
- [ ] [`backend/models/report.py`](backend/models/report.py) - AnalysisReport model
- [ ] [`backend/schemas/analysis.py`](backend/schemas/analysis.py) - Request/response schemas
- [ ] [`backend/schemas/report.py`](backend/schemas/report.py) - Report schemas

### Phase 2: Utilities ✓ Priority: HIGH
- [ ] [`backend/utils/github_client.py`](backend/utils/github_client.py) - GitHub API integration
- [ ] [`backend/utils/diff_parser.py`](backend/utils/diff_parser.py) - Parse unified diffs
- [ ] [`backend/utils/graph_serializer.py`](backend/utils/graph_serializer.py) - NetworkX ↔ JSON

### Phase 3: Core Services ✓ Priority: CRITICAL
- [ ] [`backend/services/ast_analyzer.py`](backend/services/ast_analyzer.py) - tree-sitter parsing
- [ ] [`backend/services/graph_builder.py`](backend/services/graph_builder.py) - Build dependency graph
- [ ] [`backend/services/impact_traverser.py`](backend/services/impact_traverser.py) - Find downstream impacts
- [ ] [`backend/services/ibm_bob_client.py`](backend/services/ibm_bob_client.py) - watsonx.ai integration
- [ ] [`backend/services/risk_scorer.py`](backend/services/risk_scorer.py) - Calculate risk score
- [ ] [`backend/services/regression_generator.py`](backend/services/regression_generator.py) - Generate test scenarios

### Phase 4: Orchestration ✓ Priority: CRITICAL
- [ ] [`backend/services/analysis_pipeline.py`](backend/services/analysis_pipeline.py) - Main workflow orchestrator

### Phase 5: API Layer ✓ Priority: HIGH
- [ ] [`backend/api/analysis.py`](backend/api/analysis.py) - POST /api/analyze endpoint
- [ ] [`backend/api/reports.py`](backend/api/reports.py) - GET /api/reports/{id} endpoint

### Phase 6: Data Layer ✓ Priority: HIGH
- [ ] [`backend/repositories/report_repository.py`](backend/repositories/report_repository.py) - Database operations

### Phase 7: Application ✓ Priority: CRITICAL
- [ ] [`backend/main.py`](backend/main.py) - FastAPI app with CORS and routing

### Phase 8: Testing & Demo ✓ Priority: MEDIUM
- [ ] Create sample demo PR diff in [`demo/sample_pr_diff.txt`](demo/sample_pr_diff.txt)
- [ ] Test complete flow end-to-end
- [ ] Verify dashboard integration
- [ ] Prepare demo script

---

## File Dependencies

```
main.py
├── config.py
├── db.py
├── api/analysis.py
│   ├── schemas/analysis.py
│   ├── services/analysis_pipeline.py
│   └── repositories/report_repository.py
└── api/reports.py
    ├── schemas/report.py
    └── repositories/report_repository.py

analysis_pipeline.py
├── utils/github_client.py
├── utils/diff_parser.py
├── services/ast_analyzer.py
├── services/graph_builder.py
├── services/impact_traverser.py
├── services/ibm_bob_client.py
├── services/risk_scorer.py
├── services/regression_generator.py
└── utils/graph_serializer.py
```

---

## Implementation Order (Recommended)

### Day 1 Morning (4 hours)
1. **Foundation** - config, db, models, schemas (1.5 hours)
2. **Utilities** - github_client, diff_parser, graph_serializer (1.5 hours)
3. **Test utilities** - verify GitHub API works (1 hour)

### Day 1 Afternoon (4 hours)
4. **AST Analyzer** - tree-sitter integration (2 hours)
5. **Graph Builder** - NetworkX graph construction (1.5 hours)
6. **Test graph building** - verify graph structure (0.5 hours)

### Day 2 Morning (4 hours)
7. **Impact Traverser** - BFS/DFS traversal (1 hour)
8. **Risk Scorer** - scoring algorithm (1 hour)
9. **Regression Generator** - scenario templates (1 hour)
10. **IBM Bob Client** - watsonx.ai integration (1 hour)

### Day 2 Afternoon (4 hours)
11. **Analysis Pipeline** - orchestrate all services (1.5 hours)
12. **API Endpoints** - FastAPI routes (1 hour)
13. **Repository Layer** - database operations (0.5 hours)
14. **Main Application** - wire everything together (1 hour)

### Final Polish (2-4 hours)
15. **End-to-end testing** - complete flow (1 hour)
16. **Error handling** - graceful degradation (1 hour)
17. **Demo preparation** - sample data, script (1 hour)
18. **Documentation** - API docs, README updates (1 hour)

---

## Critical Path Items

These MUST work for the demo:
1. ✅ GitHub API integration (fetch PR diff)
2. ✅ AST analysis (extract functions/imports)
3. ✅ Graph construction (build dependency graph)
4. ✅ IBM Bob integration (semantic analysis)
5. ✅ Risk scoring (calculate 0-100 score)
6. ✅ API endpoints (POST /analyze, GET /reports/{id})
7. ✅ Database persistence (save/retrieve reports)

---

## Testing Commands

```bash
# Start backend
uvicorn backend.main:app --reload --port 8000

# Test health endpoint
curl http://localhost:8000/health

# Test analyze endpoint
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"pr_id": "123", "repository": "owner/repo"}'

# Test report retrieval
curl http://localhost:8000/api/reports/{report_id}

# View API docs
open http://localhost:8000/docs
```

---

## Environment Variables Checklist

```bash
# Required for MVP
✓ GITHUB_TOKEN
✓ IBM_BOB_API_KEY
✓ IBM_BOB_API_URL
✓ IBM_BOB_PROJECT_ID

# Optional (have defaults)
○ DATABASE_URL (default: sqlite:///./prism.db)
○ CORS_ORIGINS (default: ["http://localhost:3000"])
○ LOG_LEVEL (default: INFO)
○ IBM_BOB_MODEL_ID (default: ibm/granite-13b-chat-v2)
```

---

## Common Issues & Solutions

### Issue: tree-sitter installation fails
**Solution**: Install build tools
```bash
# Windows
pip install wheel
# Linux/Mac
sudo apt-get install build-essential
```

### Issue: GitHub API rate limit
**Solution**: Use authenticated token, cache responses during dev

### Issue: IBM Bob timeout
**Solution**: Implement graceful degradation, return partial results

### Issue: SQLite locked
**Solution**: Use `check_same_thread=False` in engine config

---

## Demo Script Outline

1. **Setup** (30 seconds)
   - Show existing PR in GitHub
   - Highlight the code change

2. **Run Analysis** (10 seconds)
   ```bash
   prism analyze 123
   ```

3. **Show CLI Output** (20 seconds)
   - Risk score: HIGH (82/100)
   - Impacted nodes: 14
   - Dashboard URL

4. **Open Dashboard** (60 seconds)
   - Interactive graph visualization
   - IBM Bob insights panel
   - Regression scenarios
   - Risk breakdown

5. **Explain Value** (30 seconds)
   - Traditional CI: ✓ Build passed
   - PRISM: ⚠ Semantic risks detected
   - Prevents production incidents

**Total Demo Time**: ~2.5 minutes

---

## Success Metrics

- [ ] Analysis completes in < 30 seconds
- [ ] Risk score accurately reflects change severity
- [ ] Graph shows clear dependency paths
- [ ] IBM Bob insights are actionable
- [ ] Dashboard loads in < 3 seconds
- [ ] No crashes during demo
- [ ] Error messages are clear and helpful

---

## Post-Hackathon Improvements

1. Webhook integration for automatic analysis
2. Multi-language support (Java, Go, Ruby)
3. Persistent graph database
4. Team analytics dashboard
5. IDE plugin integration
6. Slack/Teams notifications
7. Custom risk rules per repository
8. Historical trend analysis

---

## Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **tree-sitter**: https://tree-sitter.github.io/tree-sitter/
- **NetworkX**: https://networkx.org/documentation/stable/
- **IBM watsonx.ai**: https://www.ibm.com/products/watsonx-ai
- **GitHub API**: https://docs.github.com/en/rest

---

**Ready to build! 🚀**