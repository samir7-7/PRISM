# PRISM - Pull Request Intelligent Semantic Monitor

**Predictive Risk Intelligence & Semantic Monitoring for Pull Requests**

PRISM analyzes pull requests to detect semantic risks that traditional CI/CD pipelines miss. It uses AST analysis, dependency graph traversal, and AI-powered reasoning to identify hidden behavioral risks before they reach production.

---

## 🚀 Quick Start

### 1. Setup (One-Time)

Run the setup script to create a virtual environment and install all dependencies:

```bash
# In Git Bash or Linux/Mac terminal
./setup.sh
```

This will:

1. Create a virtual environment in the `venv` directory
2. Activate the virtual environment
3. Install Python requirements from `requirements.txt`
4. Install frontend dependencies in `frontend/prism`
5. Install CLI tool

### 2. Start Services

**Terminal 1 - Backend:**

```bash
python start_backend.py
# Backend runs on http://localhost:8000
```

**Terminal 2 - Frontend:**

```bash
cd frontend/prism
npm run dev
# Frontend runs on http://localhost:3000
```

### 3. Run Analysis

**Option A - CLI (Recommended):**

```bash
# Demo mode (always works)
prism demo

# Analyze a real PR
prism analyze pr-142 --repo https://github.com/owner/repo --open
```

**Option B - Web Interface:**

1. Open http://localhost:3000/
2. Enter PR ID and repository
3. Click "Analyze Pull Request"
4. View results in dashboard

---

## 📚 Documentation

- **[CLI ↔ Frontend Integration Guide](CLI_FRONTEND_INTEGRATION.md)** - Complete usage guide
- **[CLI Architecture](cli/CLI_PLAN.md)** - CLI design and implementation
- **[API Contract](cli/API_CONTRACT.md)** - Backend API specification
- **[Frontend README](frontend/prism/FRONTEND_README.md)** - Frontend architecture
- **[Project PRD](Required%20Docs/PRD.md)** - Product requirements
- **[Tech Specs](<Required%20Docs/TECH_SPECS__1_%20(1).md>)** - Technical specifications

---

## 🏗️ Architecture

```
┌─────────────┐
│     CLI     │  prism analyze pr-142 --open
│   (Typer)   │
└──────┬──────┘
       │ POST /api/analysis/run
       ▼
┌─────────────────────────────────────┐
│   FastAPI Backend                   │
│   ├─ Fetch PR diff (GitHub API)    │
│   ├─ AST Analysis                   │
│   ├─ Build dependency graph         │
│   ├─ Impact traversal               │
│   ├─ IBM Bob semantic reasoning     │
│   ├─ Risk scoring                   │
│   └─ Generate regression scenarios  │
└──────┬──────────────────────────────┘
       │ Store in Database
       ▼
┌─────────────┐
│  Database   │ (SQLite/PostgreSQL)
└──────┬──────┘
       │
       ├─ CLI: report_id, risk_score, dashboard_url
       │
       └─ Frontend: Full report with graph data
              ▼
       ┌─────────────┐
       │  Frontend   │ http://localhost:3000/report/{id}
       │  Dashboard  │ - Interactive dependency graph
       │  (React)    │ - IBM Bob insights
       └─────────────┘ - Regression scenarios
```

---

## 🎯 Features

### ✅ Implemented

- **CLI Tool** - `prism analyze` command with rich terminal output
- **Semantic Analysis** - AST parsing and dependency graph construction
- **Risk Scoring** - Intelligent risk assessment (0-100 scale)
- **IBM Bob Integration** - AI-powered semantic reasoning
- **Interactive Dashboard** - React-based visualization with dependency graph
- **Regression Scenarios** - Auto-generated test scenarios
- **Demo Mode** - Bulletproof demo with pre-baked results
- **Dual Entry Points** - CLI and web interface

### 🔄 Integration Points

1. **CLI → Backend** - `POST /api/analysis/run` (canonical endpoint)
2. **Backend → Database** - Store complete analysis reports
3. **Frontend → Backend** - `GET /api/reports/{id}` for report retrieval
4. **CLI → Browser** - Auto-open dashboard with `--open` flag

---

## 🛠️ Tech Stack

### Backend

- **Python 3.13+**
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **NetworkX** - Graph analysis
- **tree-sitter** - AST parsing
- **IBM watsonx.ai** - Semantic reasoning

### Frontend

- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Flow** - Dependency graph visualization
- **Framer Motion** - Animations

### CLI

- **Typer** - CLI framework
- **Rich** - Terminal formatting
- **httpx** - HTTP client
- **Pydantic** - Data validation

---

## 📖 Usage Examples

### CLI Examples

```bash
# Basic analysis (auto-detects repo from git remote)
prism analyze pr-142

# Analysis with explicit repository
prism analyze pr-142 --repo https://github.com/owner/repo

# Open dashboard automatically
prism analyze pr-142 --open

# Demo mode (pre-baked results)
prism demo

# JSON output (for CI/CD)
prism analyze pr-142 --json

# Custom backend
prism analyze pr-142 --backend http://production-backend.com

# With GitHub token
prism analyze pr-142 --token ghp_your_token_here
```

### Web Interface

1. **Home Page:** http://localhost:3000/
2. **Enter PR Details:**
   - PR ID: `142` or `pr-142`
   - Repository: `owner/repo` or full URL
3. **View Results:** Automatically redirected to dashboard
4. **Direct Access:** http://localhost:3000/report/{report_id}

---

## 🧪 Testing

### Manual Testing

```bash
# 1. Verify backend
curl http://localhost:8000/healthz
# Expected: {"ok": true}

# 2. Test CLI
prism demo
# Expected: Terminal output + browser opens

# 3. Test frontend
# Open: http://localhost:3000/
# Submit form with PR details
# Expected: Dashboard loads with analysis
```

### Automated Tests

```bash
# Backend tests
pytest tests/ -v

# CLI tests
cd cli && pytest tests/ -v

# Frontend tests (if configured)
cd frontend/prism && npm test
```

---

## 🐛 Troubleshooting

### Common Issues

**Frontend not on port 3000:**

```bash
# Kill process using port 3000
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:3000 | xargs kill -9
```

**Backend not reachable:**

```bash
# Check if backend is running
curl http://localhost:8000/healthz

# Restart backend
python start_backend.py
```

**CLI can't detect repository:**

```bash
# Option 1: Run from inside git repo
cd /path/to/repo && prism analyze pr-142

# Option 2: Use --repo flag
prism analyze pr-142 --repo https://github.com/owner/repo

# Option 3: Set environment variable
export PRISM_REPO_URL=https://github.com/owner/repo
```

**CORS errors in browser:**

- Ensure backend has CORS middleware configured for `http://localhost:3000`
- Check `backend/config.py` or `backend/app.py`

For more troubleshooting, see **[CLI_FRONTEND_INTEGRATION.md](CLI_FRONTEND_INTEGRATION.md#troubleshooting)**

---

## 📁 Project Structure

```
PRISM/
├── cli/                    # CLI tool (Typer + Rich)
│   ├── main.py            # Entry point
│   ├── client.py          # Backend HTTP client
│   ├── config.py          # Settings management
│   ├── formatter.py       # Terminal output
│   └── tests/             # CLI tests
│
├── backend/               # FastAPI application
│   ├── api/              # Route handlers
│   ├── services/         # Business logic
│   ├── models/           # Database models
│   ├── schemas/          # Pydantic schemas
│   ├── repositories/     # Data access layer
│   └── utils/            # Shared utilities
│
├── frontend/prism/       # React dashboard
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Route pages
│   │   ├── services/     # API client
│   │   ├── store/        # State management
│   │   └── types/        # TypeScript types
│   └── public/           # Static assets
│
├── tests/                # Backend tests
├── demo/                 # Demo fixtures
└── Required Docs/        # Documentation
```

---

## 🤝 Contributing

1. Follow existing code structure
2. Update documentation for changes
3. Test thoroughly before committing
4. Keep API contract frozen (breaking changes require version bump)

---

## 📄 License

[Add license information]

---

## 🙏 Acknowledgments

Built with:

- IBM watsonx.ai for semantic reasoning
- React Flow for graph visualization
- FastAPI for backend framework
- Typer for CLI framework

---

**Version:** 1.0  
**Status:** ✅ Production Ready  
**Last Updated:** 2026-05-17

For detailed usage instructions, see **[CLI_FRONTEND_INTEGRATION.md](CLI_FRONTEND_INTEGRATION.md)**
