# PRISM CLI Implementation Checklist

**Status:** Planning Complete → Ready for Implementation  
**Last Updated:** 2026-05-16  
**Estimated Total Time:** 6-8 hours

This checklist tracks the implementation of the PRISM CLI from planning to deployment.

---

## 📋 Quick Status

| Phase                    | Status         | Progress |
| ------------------------ | -------------- | -------- |
| Planning & Documentation | ✅ Complete    | 100%     |
| Foundation Setup         | ⏳ Not Started | 0%       |
| Core Implementation      | ⏳ Not Started | 0%       |
| Testing                  | ⏳ Not Started | 0%       |
| Documentation Updates    | ⏳ Not Started | 0%       |
| Deployment               | ⏳ Not Started | 0%       |

**Overall Progress:** 16% (Planning Complete)

---

## Phase 1: Planning & Documentation ✅

### Architecture & Design

- [x] Review existing CLI_PLAN.md
- [x] Analyze current codebase state
- [x] Identify architectural mismatches
- [x] Create CLI_ARCHITECTURE_ANALYSIS.md
- [x] Document gaps and recommendations

### Documentation

- [x] Create comprehensive README.md
- [x] Document environment configuration (ENV_CONFIGURATION.md)
- [x] Define API contract (API_CONTRACT.md)
- [x] Document pyproject.toml updates (PYPROJECT_UPDATES.md)
- [x] Create implementation checklist (this file)

**Phase 1 Complete:** ✅ All planning documentation ready

---

## Phase 2: Foundation Setup ⏳

**Estimated Time:** 30 minutes  
**Priority:** 🔴 Critical - Must complete before coding

### 2.1 Update pyproject.toml

- [ ] Backup current pyproject.toml
- [ ] Update project metadata (name, description, authors)
- [ ] Replace Textual dependencies with Typer stack
- [ ] Add pydantic and pydantic-settings
- [ ] Configure console script entry point (`prism = "cli.main:app"`)
- [ ] Add dev dependencies (pytest, ruff, black)
- [ ] Add tool configurations (ruff, black, pytest)
- [ ] Verify TOML syntax is valid

**Reference:** [`PYPROJECT_UPDATES.md`](PYPROJECT_UPDATES.md)

### 2.2 Environment Setup

- [ ] Create `.env.example` file from template
- [ ] Create personal `.env` file (not committed)
- [ ] Add `.env` to `.gitignore`
- [ ] Set PRISM_BACKEND_URL
- [ ] Set PRISM_GITHUB_TOKEN (if available)
- [ ] Set PRISM_REPO_URL (optional)

**Reference:** [`ENV_CONFIGURATION.md`](ENV_CONFIGURATION.md)

### 2.3 Install Dependencies

- [ ] Create fresh virtual environment (optional but recommended)
- [ ] Run `pip install -e ".[dev]"`
- [ ] Verify typer installed: `pip show typer`
- [ ] Verify rich installed: `pip show rich`
- [ ] Verify httpx installed: `pip show httpx`
- [ ] Verify pydantic installed: `pip show pydantic`
- [ ] Update uv.lock if using uv: `uv lock`

### 2.4 Project Structure

- [ ] Verify cli/ directory structure
- [ ] Create tests/ directory if missing
- [ ] Ensure **init**.py exists in cli/

**Verification:**

```bash
pip install -e ".[dev]"
pip list | grep -E "typer|rich|httpx|pydantic"
```

---

## Phase 3: Core Implementation ⏳

**Estimated Time:** 4-5 hours  
**Priority:** 🔴 Critical

### 3.1 Error Handling (cli/errors.py)

**Time:** 20 minutes

- [ ] Create `cli/errors.py`
- [ ] Define `PrismError` base exception with `.hint` attribute
- [ ] Implement `BackendUnreachable(PrismError)`
- [ ] Implement `BackendTimeout(PrismError)`
- [ ] Implement `BackendBadRequest(PrismError)`
- [ ] Implement `BackendServerError(PrismError)`
- [ ] Implement `AuthError(PrismError)`
- [ ] Implement `NotFoundError(PrismError)`
- [ ] Add docstrings for each exception

**Reference:** [`CLI_PLAN.md`](CLI_PLAN.md:115)

### 3.2 Configuration (cli/config.py)

**Time:** 30 minutes

- [ ] Create `cli/config.py`
- [ ] Import pydantic-settings BaseSettings
- [ ] Define `Settings` class with model_config
- [ ] Add `backend_url: str` field (default: "http://localhost:8000")
- [ ] Add `github_token: str | None` field
- [ ] Add `repo_url: str | None` field
- [ ] Add `timeout: int` field (default: 60)
- [ ] Add `output_format: Literal["pretty", "json"]` field
- [ ] Add `auto_open: bool` field (default: False)
- [ ] Configure env*prefix="PRISM*"
- [ ] Configure env_file=".env"
- [ ] Test loading from .env file

**Reference:** [`CLI_PLAN.md`](CLI_PLAN.md:98-103), [`ENV_CONFIGURATION.md`](ENV_CONFIGURATION.md)

### 3.3 HTTP Client (cli/client.py)

**Time:** 45 minutes

- [ ] Create `cli/client.py`
- [ ] Import httpx, pydantic
- [ ] Define `AnalysisResponse` Pydantic model
  - [ ] report_id: str
  - [ ] dashboard_url: str
  - [ ] risk_score: int
  - [ ] risk_label: Literal["LOW", "MEDIUM", "HIGH"]
  - [ ] impacted_node_count: int
  - [ ] status: Literal["COMPLETE", "PARTIAL"]
- [ ] Implement `AnalysisClient` class
- [ ] Add `__init__(backend_url, timeout)`
- [ ] Implement `check_health() -> bool` method
- [ ] Implement `run(pr_identifier, repository_url, github_token) -> AnalysisResponse`
- [ ] Add error handling for connection errors
- [ ] Add error handling for timeouts
- [ ] Add error handling for HTTP status errors
- [ ] Map HTTP errors to custom exceptions

**Reference:** [`CLI_PLAN.md`](CLI_PLAN.md:104-108), [`API_CONTRACT.md`](API_CONTRACT.md)

### 3.4 Output Formatting (cli/formatter.py)

**Time:** 1 hour

- [ ] Create `cli/formatter.py`
- [ ] Import rich (Console, Panel, Progress, Text)
- [ ] Implement `with_progress(stages: list[str])` context manager
  - [ ] Create Progress with spinner
  - [ ] Add task with stages
  - [ ] Yield progress context
  - [ ] Auto-advance stages on timer
- [ ] Implement `render_summary(response: AnalysisResponse)`
  - [ ] Create title panel
  - [ ] Add status checkmarks
  - [ ] Add risk score box with color coding
  - [ ] Add dashboard URL
  - [ ] Handle PARTIAL status with warning
- [ ] Implement `render_error(err: PrismError)`
  - [ ] Create red error panel
  - [ ] Show error message
  - [ ] Show hint
- [ ] Implement `render_json(response: AnalysisResponse)`
  - [ ] Output JSON to stdout
  - [ ] No Rich formatting

**Reference:** [`CLI_PLAN.md`](CLI_PLAN.md:110-114)

### 3.5 Demo Fixture (cli/demo_fixture.py)

**Time:** 5 minutes

- [ ] Create `cli/demo_fixture.py`
- [ ] Define `DEMO_PR_ID = "pr-142"`
- [ ] Define `DEMO_REPO_URL = "https://github.com/prism-demo/payment-service"`
- [ ] Add docstring explaining demo mode

**Reference:** [`CLI_PLAN.md`](CLI_PLAN.md:117-122)

### 3.6 Main CLI (cli/main.py)

**Time:** 1.5 hours

- [ ] Create `cli/main.py` (replace existing Textual app)
- [ ] Import typer, rich, other modules
- [ ] Create Typer app: `app = typer.Typer()`
- [ ] Implement `analyze` command
  - [ ] Add pr_id positional argument
  - [ ] Add --repo flag
  - [ ] Add --open flag
  - [ ] Add --json flag
  - [ ] Add --backend flag
  - [ ] Add --token flag
  - [ ] Load Settings with overrides
  - [ ] Run pre-flight health check
  - [ ] Create AnalysisClient
  - [ ] Call client.run() with progress spinner
  - [ ] Render summary or JSON
  - [ ] Open browser if --open
  - [ ] Handle errors with try/except
- [ ] Implement `demo` command
  - [ ] Load demo fixture constants
  - [ ] Call analyze with fixture values
  - [ ] Force --open flag
- [ ] Implement `version` command
  - [ ] Print **version** from **init**.py
- [ ] Add main entry point: `if __name__ == "__main__": app()`

**Reference:** [`CLI_PLAN.md`](CLI_PLAN.md:90-96)

### 3.7 Package Init (cli/**init**.py)

**Time:** 5 minutes

- [ ] Update `cli/__init__.py`
- [ ] Define `__version__ = "0.1.0"`
- [ ] Add package docstring
- [ ] Export main components (optional)

---

## Phase 4: Testing ⏳

**Estimated Time:** 2 hours  
**Priority:** 🟡 High

### 4.1 Test Setup

- [ ] Create `tests/__init__.py`
- [ ] Create `tests/conftest.py` with fixtures
- [ ] Add pytest configuration in pyproject.toml

### 4.2 Client Tests (tests/test_client.py)

**Time:** 45 minutes

- [ ] Create `tests/test_client.py`
- [ ] Test successful analysis with MockTransport
- [ ] Test health check
- [ ] Test connection error handling
- [ ] Test timeout handling
- [ ] Test 401 authentication error
- [ ] Test 404 not found error
- [ ] Test 500 server error
- [ ] Test response validation

### 4.3 Formatter Tests (tests/test_formatter.py)

**Time:** 30 minutes

- [ ] Create `tests/test_formatter.py`
- [ ] Test render_summary with LOW risk
- [ ] Test render_summary with MEDIUM risk
- [ ] Test render_summary with HIGH risk
- [ ] Test render_summary with PARTIAL status
- [ ] Test render_error
- [ ] Test render_json
- [ ] Snapshot test for output consistency

### 4.4 Main Tests (tests/test_main.py)

**Time:** 45 minutes

- [ ] Create `tests/test_main.py`
- [ ] Use Typer CliRunner
- [ ] Test `prism --help`
- [ ] Test `prism version`
- [ ] Test `prism analyze` with mocked backend
- [ ] Test `prism demo`
- [ ] Test flag combinations
- [ ] Test error paths
- [ ] Test exit codes

### 4.5 Run Tests

- [ ] Run `pytest` - all tests pass
- [ ] Run `pytest --cov=cli` - check coverage
- [ ] Fix any failing tests
- [ ] Aim for >80% coverage

---

## Phase 5: Documentation Updates ⏳

**Estimated Time:** 30 minutes  
**Priority:** 🟢 Medium

### 5.1 Update README

- [ ] Verify installation instructions work
- [ ] Update examples with real commands
- [ ] Add screenshots/GIFs (optional)
- [ ] Update troubleshooting section

### 5.2 Create Additional Docs

- [ ] Create actual `.env.example` file (copy from ENV_CONFIGURATION.md)
- [ ] Create CONTRIBUTING.md (optional)
- [ ] Create CHANGELOG.md (optional)

### 5.3 Code Documentation

- [ ] Add docstrings to all public functions
- [ ] Add type hints throughout
- [ ] Add inline comments for complex logic

---

## Phase 6: Quality Assurance ⏳

**Estimated Time:** 1 hour  
**Priority:** 🟡 High

### 6.1 Code Quality

- [ ] Run `ruff check cli/` - no errors
- [ ] Run `black cli/` - code formatted
- [ ] Run `mypy cli/` - type check passes (optional)
- [ ] Review code for TODOs and FIXMEs

### 6.2 Manual Testing

- [ ] Test `pip install -e .` from scratch
- [ ] Test `prism --help` output
- [ ] Test `prism version`
- [ ] Test `prism demo` (requires backend)
- [ ] Test `prism analyze pr-142` (requires backend + token)
- [ ] Test all flag combinations
- [ ] Test error scenarios (backend down, bad token, etc.)
- [ ] Test on different terminals (PowerShell, bash, zsh)

### 6.3 Integration Testing

- [ ] Start backend locally
- [ ] Run full end-to-end test
- [ ] Verify dashboard URL opens correctly
- [ ] Test with real GitHub PR
- [ ] Verify JSON output format

---

## Phase 7: Deployment Preparation ⏳

**Estimated Time:** 30 minutes  
**Priority:** 🟢 Low (for hackathon)

### 7.1 Package Preparation

- [ ] Verify pyproject.toml is complete
- [ ] Test `pip install -e .` in clean environment
- [ ] Build wheel: `python -m build`
- [ ] Test wheel installation

### 7.2 Documentation

- [ ] Create CLI_DOCUMENTATION_INDEX.md
- [ ] Update main README with links
- [ ] Prepare demo script
- [ ] Create quick reference card

### 7.3 Demo Preparation

- [ ] Verify demo mode works reliably
- [ ] Prepare backup demo data
- [ ] Test on presentation machine
- [ ] Prepare troubleshooting notes

---

## Verification Checklist

Before marking implementation complete:

### Functionality

- [ ] `prism --help` shows all commands
- [ ] `prism version` prints version
- [ ] `prism demo` runs successfully
- [ ] `prism analyze pr-142 --repo URL` works
- [ ] `--open` flag opens browser
- [ ] `--json` flag outputs JSON
- [ ] Error messages are clear and helpful
- [ ] Progress spinner shows stages

### Code Quality

- [ ] All tests pass
- [ ] Code coverage >80%
- [ ] No linter errors
- [ ] Code is formatted
- [ ] Type hints present
- [ ] Docstrings complete

### Documentation

- [ ] README is accurate
- [ ] API contract documented
- [ ] Environment setup documented
- [ ] Examples work
- [ ] Troubleshooting guide complete

### Integration

- [ ] Works with backend API
- [ ] GitHub token authentication works
- [ ] Dashboard URL is correct
- [ ] Demo mode is reliable

---

## Time Estimates Summary

| Phase                    | Estimated Time | Priority    |
| ------------------------ | -------------- | ----------- |
| Planning & Documentation | ✅ Complete    | 🔴 Critical |
| Foundation Setup         | 30 min         | 🔴 Critical |
| Core Implementation      | 4-5 hours      | 🔴 Critical |
| Testing                  | 2 hours        | 🟡 High     |
| Documentation Updates    | 30 min         | 🟢 Medium   |
| Quality Assurance        | 1 hour         | 🟡 High     |
| Deployment Preparation   | 30 min         | 🟢 Low      |

**Total Estimated Time:** 8-10 hours

**Minimum Viable Product (MVP):** Phases 1-3 + basic testing = ~5-6 hours

---

## Implementation Order

**Recommended sequence for fastest MVP:**

1. ✅ **Planning** (Complete)
2. **Foundation** (30 min)
   - Update pyproject.toml
   - Install dependencies
   - Create .env
3. **Core - Errors** (20 min)
   - Implement cli/errors.py
4. **Core - Config** (30 min)
   - Implement cli/config.py
5. **Core - Client** (45 min)
   - Implement cli/client.py
6. **Core - Formatter** (1 hour)
   - Implement cli/formatter.py
7. **Core - Demo** (5 min)
   - Implement cli/demo_fixture.py
8. **Core - Main** (1.5 hours)
   - Implement cli/main.py
9. **Testing** (2 hours)
   - Write and run tests
10. **QA** (1 hour)
    - Manual testing and fixes

**Critical Path:** Steps 2-8 must be completed in order

---

## Blockers & Dependencies

### External Dependencies

- ⚠️ **Backend API** - Must be running for integration testing
- ⚠️ **GitHub Token** - Required for real PR analysis
- ⚠️ **Demo Fixture** - Backend must support demo PR

### Internal Dependencies

- ✅ Planning documentation complete
- ⏳ pyproject.toml must be updated before coding
- ⏳ errors.py must exist before client.py
- ⏳ All core modules must exist before main.py

---

## Success Criteria

### Minimum (MVP)

- [ ] `prism demo` works reliably
- [ ] `prism analyze` works with backend
- [ ] Error messages are clear
- [ ] Output looks good on projector

### Target (Full Implementation)

- [ ] All commands implemented
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Code quality checks pass

### Stretch Goals

- [ ] CI/CD pipeline
- [ ] Published to PyPI
- [ ] Comprehensive test coverage
- [ ] Performance optimizations

---

## Notes & Decisions

### Architecture Decision

- ✅ **Decided:** Use Typer + Rich (not Textual)
- **Rationale:** Simpler, faster, better for demos
- **Impact:** Complete rewrite of main.py required

### Key Trade-offs

- **Synchronous vs Async:** Chose synchronous for simplicity
- **Progress Stages:** Fake timer-based (not real backend events)
- **Error Handling:** Fail fast (no retries)
- **Demo Mode:** Hardcoded fixture for reliability

---

## Related Documentation

- **Architecture:** [`CLI_PLAN.md`](CLI_PLAN.md)
- **Analysis:** [`CLI_ARCHITECTURE_ANALYSIS.md`](CLI_ARCHITECTURE_ANALYSIS.md)
- **README:** [`README.md`](README.md)
- **API Contract:** [`API_CONTRACT.md`](API_CONTRACT.md)
- **Environment:** [`ENV_CONFIGURATION.md`](ENV_CONFIGURATION.md)
- **Dependencies:** [`PYPROJECT_UPDATES.md`](PYPROJECT_UPDATES.md)

---

**Status:** Ready for Implementation  
**Next Step:** Phase 2 - Foundation Setup  
**Owner:** CLI Implementation Team  
**Last Updated:** 2026-05-16
