# 🔍 PRISM - Pull Request Intelligent Semantic Monitor

> **Catch semantic bugs before they reach production**  
> PRISM analyzes pull requests beyond syntax — understanding how code changes ripple through your entire system.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3.1-61DAFB.svg)](https://reactjs.org/)

---

## 📖 About PRISM

**PRISM** is a semantic risk analysis tool that transforms how teams review pull requests. While traditional CI/CD pipelines validate syntax and run tests, PRISM goes deeper — analyzing how code changes propagate through your system's dependency graph to identify hidden semantic risks.

### The Problem We Solve

Modern CI/CD pipelines are blind to **semantic risk**:

- ✅ **CI says:** "Build passed, tests passed, no conflicts"
- ❌ **Reality:** A renamed enum breaks 3 downstream services in production
- ❌ **Reality:** An API field change silently breaks analytics pipelines
- ❌ **Reality:** A refactored permission check alters behavior under edge cases

**PRISM catches these issues before merge** by combining:
- 🔬 **Static AST Analysis** - Deep code structure understanding
- 🕸️ **Dependency Graph Traversal** - Impact radius mapping
- 🤖 **AI-Powered Reasoning** - Natural language risk explanations via OpenRouter
- 📊 **Interactive Visualization** - Clear, actionable insights

### Who We Are

PRISM was built during a hackathon by a team passionate about improving developer workflows and preventing production incidents. We believe that every developer should have access to intelligent tooling that makes code review faster, safer, and more confident.

---

## ✨ Key Features

- **🔍 Semantic Risk Analysis** - Goes beyond syntax to understand behavioral impact
- **📈 Risk Scoring** - Quantifies change risk (0-100) with detailed breakdowns
- **🕸️ Dependency Graph** - Visualizes how changes propagate through your codebase
- **🤖 AI Insights** - Natural language explanations powered by OpenRouter AI
- **🧪 Regression Scenarios** - Auto-generated test cases for impacted areas
- **💻 CLI Tool** - Fast, developer-friendly command-line interface
- **🎨 Visual Dashboard** - Interactive web UI for exploring analysis results

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+** (Required for backend)
- **Node.js 18+** (Required for frontend)
- **Git** (For repository operations)

### Installation

#### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd PRISM

# Run the setup script (Git Bash on Windows, or any Unix shell)
./setup.sh
```

The setup script will:
1. Create a Python virtual environment
2. Install all Python dependencies
3. Install frontend dependencies
4. Set up the CLI tool

#### Option 2: Manual Setup

```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install CLI tool
pip install -e cli/

# 4. Install frontend dependencies
cd frontend/prism
npm install
cd ../..
```

### Configuration

1. **Copy the environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Configure required API keys in `.env`:**
   ```bash
   # GitHub Configuration (Required)
   GITHUB_TOKEN=ghp_your_github_personal_access_token_here
   GITHUB_API_URL=https://api.github.com

   # OpenRouter Configuration (Required for AI insights)
   OPENROUTER_API_KEY=sk-or-v1-your_openrouter_api_key_here
   OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
   OPENROUTER_MODEL_ID=minimax/minimax-m2.5:free

   # Database (SQLite by default)
   DATABASE_URL=sqlite:///./prism.db

   # Application Settings
   CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
   LOG_LEVEL=INFO
   API_HOST=0.0.0.0
   API_PORT=8000
   ```

3. **Get your API keys:**
   - **GitHub Token:** https://github.com/settings/tokens (requires `repo` scope)
   - **OpenRouter API Key:** https://openrouter.ai/ (free tier available)

### Running PRISM

#### Start the Backend

```bash
# Activate virtual environment if not already active
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start the FastAPI backend
python start_backend.py

# Backend will be available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

#### Start the Frontend

```bash
# In a new terminal
cd frontend/prism
npm run dev

# Frontend will be available at http://localhost:5173
```

#### Use the CLI

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run analysis on a pull request
prism analyze pr-142 --repo https://github.com/owner/repo

# Run the demo (no setup required)
prism demo

# Check CLI version
prism version

# Get help
prism --help
```

---

## 📚 Usage Examples

### Analyze a Pull Request

```bash
# Basic analysis
prism analyze pr-142 --repo https://github.com/owner/repo

# With custom backend
prism analyze pr-142 --repo https://github.com/owner/repo --backend http://localhost:8000

# With GitHub token
prism analyze pr-142 --repo https://github.com/owner/repo --token ghp_your_token

# Open dashboard automatically after analysis
prism analyze pr-142 --repo https://github.com/owner/repo --open

# JSON output for CI/CD integration
prism analyze pr-142 --repo https://github.com/owner/repo --json
```

### Environment Variables (CLI)

The CLI supports environment variables with the `PRISM_` prefix:

```bash
# Set in .env or export
export PRISM_BACKEND_URL=http://localhost:8000
export PRISM_GITHUB_TOKEN=ghp_your_token
export PRISM_REPO_URL=https://github.com/owner/repo
export PRISM_TIMEOUT=60
export PRISM_OUTPUT_FORMAT=pretty
export PRISM_AUTO_OPEN=false

# Then run without flags
prism analyze pr-142
```

---

## 🏗️ Architecture

### Tech Stack

**Backend:**
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **NetworkX** - Dependency graph construction and traversal
- **tree-sitter** - Multi-language AST parsing
- **httpx** - Async HTTP client for GitHub and OpenRouter APIs

**Frontend:**
- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **TailwindCSS** - Utility-first CSS framework
- **React Flow** - Interactive dependency graph visualization

**CLI:**
- **Typer** - Modern CLI framework
- **Rich** - Beautiful terminal output

### System Components

```
┌─────────────────┐
│   Developer     │
│    Terminal     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│   PRISM CLI     │─────▶│  FastAPI Backend │
│  (Python Tool)  │      │                  │
└─────────────────┘      │  ┌────────────┐  │
                         │  │ AST Parser │  │
         ┌───────────────┤  └────────────┘  │
         │               │  ┌────────────┐  │
         ▼               │  │Graph Engine│  │
┌─────────────────┐      │  └────────────┘  │
│ React Dashboard │      │  ┌────────────┐  │
│  (Visualization)│      │  │Risk Scorer │  │
└─────────────────┘      │  └────────────┘  │
                         │  ┌────────────┐  │
                         │  │ OpenRouter │  │
                         │  │   Client   │  │
                         │  └────────────┘  │
                         └──────────────────┘
                                  │
                         ┌────────┴────────┐
                         ▼                 ▼
                    ┌─────────┐      ┌──────────┐
                    │ GitHub  │      │OpenRouter│
                    │   API   │      │   API    │
                    └─────────┘      └──────────┘
```

---

## 🔮 Future Improvements

### Planned Enhancements

#### 1. **Standalone Package Distribution**
- **Goal:** Publish PRISM as a PyPI package for easy installation
- **Benefits:**
  - Install with `pip install prism-analyzer`
  - No repository cloning required
  - Automatic dependency management
  - Version-controlled releases
- **Implementation:**
  - Package backend and CLI together
  - Separate frontend as optional web component
  - Include pre-built frontend assets in package

#### 2. **Enhanced Language Support**
- **Current:** Python, JavaScript, TypeScript
- **Planned:** Java, Go, Rust, C#, Ruby
- **Approach:** Extend tree-sitter grammar support

#### 3. **CI/CD Integration**
- **GitHub Actions:** Pre-built workflow for PR checks
- **GitLab CI:** Pipeline template
- **Jenkins:** Plugin development
- **Output:** Status checks, comments on PRs with risk summaries

#### 4. **Advanced Graph Analysis**
- **Circular dependency detection**
- **Critical path identification**
- **Change impact prediction** (ML-based)
- **Historical risk correlation**

#### 5. **Database Improvements**
- **Migration to PostgreSQL** for production deployments
- **Optional Firebase/Firestore** support for real-time features
- **Report history and trending**
- **Team analytics dashboard**

#### 6. **AI Enhancements**
- **Multi-model support** (OpenAI, Anthropic, local models)
- **Fine-tuned models** for code-specific reasoning
- **Contextual learning** from past analyses
- **Automated fix suggestions**

#### 7. **Performance Optimizations**
- **Incremental analysis** (only analyze changed portions)
- **Caching layer** for repeated analyses
- **Parallel processing** for large codebases
- **Streaming results** for real-time feedback

#### 8. **Developer Experience**
- **VS Code extension** for in-editor analysis
- **Git hooks** for pre-commit checks
- **Slack/Teams notifications**
- **Customizable risk thresholds**

### Minor Improvements

- [ ] Add unit test coverage reporting
- [ ] Implement rate limiting for API calls
- [ ] Add retry logic with exponential backoff
- [ ] Improve error messages and debugging
- [ ] Add configuration file support (`.prismrc`)
- [ ] Implement analysis result caching
- [ ] Add support for monorepo analysis
- [ ] Create Docker images for easy deployment
- [ ] Add metrics and monitoring (Prometheus/Grafana)
- [ ] Implement webhook support for automation

---

## 🧪 Testing

```bash
# Run backend tests
pytest tests/

# Run CLI tests
cd cli
pytest tests/

# Run with coverage
pytest --cov=backend --cov=cli tests/
```

## 🤝 Contributing

We welcome contributions! Whether it's bug reports, feature requests, or code contributions, we appreciate your help in making PRISM better.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request