# pyproject.toml Updates Required

This document details the changes needed to [`pyproject.toml`](pyproject.toml) to align with the Typer-based CLI architecture defined in [`CLI_PLAN.md`](CLI_PLAN.md).

---

## Current State

**File:** [`cli/pyproject.toml`](pyproject.toml)

```toml
[project]
name = "cli"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "httpx>=0.28.1",
    "python-dotenv>=1.2.2",
    "textual>=8.2.6",          # ❌ Wrong framework
]

[dependency-groups]
dev = [
    "pytest>=9.0.3",
    "pytest-asyncio>=1.3.0",
    "textual-dev>=1.8.0",      # ❌ Not needed
]
```

---

## Required Changes

### 1. Project Metadata

**Update project name and description:**

```toml
[project]
name = "prism-cli"                    # Changed from "cli"
version = "0.1.0"
description = "PRISM CLI - Pull Request Intelligent Semantic Monitor"
readme = "README.md"
requires-python = ">=3.13"
authors = [
    {name = "PRISM Team", email = "team@prism.dev"}
]
keywords = ["cli", "pull-request", "code-analysis", "risk-assessment"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Quality Assurance",
    "Programming Language :: Python :: 3.13",
]
```

### 2. Dependencies

**Replace Textual with Typer + Rich stack:**

```toml
dependencies = [
    # CLI Framework
    "typer>=0.12.0",           # Command-line interface framework

    # Output Formatting
    "rich>=13.0.0",            # Terminal formatting and progress bars

    # HTTP Client
    "httpx>=0.27.0",           # Async HTTP client (keep existing)

    # Data Validation & Settings
    "pydantic>=2.0.0",         # Data validation
    "pydantic-settings>=2.0.0", # Environment variable management
]
```

**Rationale for each dependency:**

| Package             | Version  | Purpose                            | Size   |
| ------------------- | -------- | ---------------------------------- | ------ |
| `typer`             | >=0.12.0 | CLI framework with type hints      | ~50KB  |
| `rich`              | >=13.0.0 | Terminal formatting, progress bars | ~500KB |
| `httpx`             | >=0.27.0 | HTTP client for backend API        | ~200KB |
| `pydantic`          | >=2.0.0  | Response validation                | ~1MB   |
| `pydantic-settings` | >=2.0.0  | .env file loading                  | ~50KB  |

**Total:** ~1.8MB (acceptable for CLI tool)

### 3. Development Dependencies

**Update dev dependencies for testing:**

```toml
[dependency-groups]
dev = [
    # Testing
    "pytest>=9.0.3",
    "pytest-cov>=4.1.0",       # Coverage reporting
    "pytest-httpx>=0.30.0",    # HTTP mocking for tests

    # Code Quality
    "ruff>=0.1.0",             # Fast linter
    "black>=23.0.0",           # Code formatter
    "mypy>=1.7.0",             # Type checker (optional)

    # Development Tools
    "ipython>=8.18.0",         # Better REPL
]
```

### 4. Console Scripts Entry Point

**Add entry point for `prism` command:**

```toml
[project.scripts]
prism = "cli.main:app"
```

This enables:

```bash
pip install -e .
prism --help          # Works!
prism analyze pr-142  # Works!
```

### 5. Optional Dependencies

**Add optional dependency groups:**

```toml
[project.optional-dependencies]
# For CI/CD environments
ci = [
    "pytest>=9.0.3",
    "pytest-cov>=4.1.0",
    "pytest-httpx>=0.30.0",
]

# For development
dev = [
    "ruff>=0.1.0",
    "black>=23.0.0",
    "mypy>=1.7.0",
    "ipython>=8.18.0",
]
```

Usage:

```bash
pip install -e ".[dev]"  # Install with dev dependencies
pip install -e ".[ci]"   # Install with CI dependencies
```

### 6. Build System

**Add build system configuration:**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["cli"]
```

### 7. Tool Configurations

**Add tool-specific configurations:**

```toml
[tool.ruff]
line-length = 100
target-version = "py313"
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]  # Line too long (handled by black)

[tool.black]
line-length = 100
target-version = ["py313"]

[tool.mypy]
python_version = "3.13"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false  # Optional for hackathon

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --cov=cli --cov-report=term-missing"
```

---

## Complete Updated pyproject.toml

Here's the complete file with all changes:

```toml
[project]
name = "prism-cli"
version = "0.1.0"
description = "PRISM CLI - Pull Request Intelligent Semantic Monitor"
readme = "README.md"
requires-python = ">=3.13"
authors = [
    {name = "PRISM Team", email = "team@prism.dev"}
]
keywords = ["cli", "pull-request", "code-analysis", "risk-assessment"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Quality Assurance",
    "Programming Language :: Python :: 3.13",
]

dependencies = [
    "typer>=0.12.0",
    "rich>=13.0.0",
    "httpx>=0.27.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=9.0.3",
    "pytest-cov>=4.1.0",
    "pytest-httpx>=0.30.0",
    "ruff>=0.1.0",
    "black>=23.0.0",
    "mypy>=1.7.0",
    "ipython>=8.18.0",
]

ci = [
    "pytest>=9.0.3",
    "pytest-cov>=4.1.0",
    "pytest-httpx>=0.30.0",
]

[project.scripts]
prism = "cli.main:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["cli"]

[tool.ruff]
line-length = 100
target-version = "py313"
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]

[tool.black]
line-length = 100
target-version = ["py313"]

[tool.mypy]
python_version = "3.13"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --cov=cli --cov-report=term-missing"
```

---

## Migration Steps

### Step 1: Backup Current File

```bash
cp pyproject.toml pyproject.toml.backup
```

### Step 2: Update Dependencies

```bash
# Remove old dependencies
pip uninstall textual textual-dev python-dotenv -y

# Install new dependencies
pip install typer rich pydantic pydantic-settings

# Or reinstall everything
pip install -e ".[dev]"
```

### Step 3: Verify Installation

```bash
# Check installed packages
pip list | grep -E "typer|rich|httpx|pydantic"

# Verify entry point
which prism  # Should show path to installed script
prism --help # Should work (after implementing main.py)
```

### Step 4: Update Lock File (if using uv)

```bash
# Regenerate uv.lock
uv lock

# Sync dependencies
uv sync
```

---

## Dependency Comparison

### Before (Textual-based)

```
textual==8.2.6
├── markdown-it-py
├── pygments
├── rich
└── typing-extensions

python-dotenv==1.2.2

httpx==0.28.1
├── certifi
├── httpcore
├── idna
└── sniffio
```

**Total:** ~15 packages, ~5MB

### After (Typer-based)

```
typer==0.12.0
├── click
├── rich
└── typing-extensions

rich==13.0.0
├── markdown-it-py
└── pygments

httpx==0.27.0
├── certifi
├── httpcore
├── idna
└── sniffio

pydantic==2.0.0
├── pydantic-core
└── typing-extensions

pydantic-settings==2.0.0
└── pydantic
```

**Total:** ~12 packages, ~3MB

**Result:** Smaller, simpler dependency tree ✅

---

## Compatibility Notes

### Python Version

- **Minimum:** Python 3.13
- **Tested:** Python 3.13
- **Recommended:** Python 3.13+

### Operating Systems

- ✅ Windows 10/11
- ✅ macOS 12+
- ✅ Linux (Ubuntu 20.04+, Debian 11+)

### Package Managers

- ✅ pip
- ✅ uv (recommended)
- ✅ poetry (with adaptation)
- ✅ pipenv (with adaptation)

---

## Verification Checklist

After updating `pyproject.toml`:

- [ ] File syntax is valid (no TOML errors)
- [ ] All dependencies install successfully
- [ ] `pip install -e .` completes without errors
- [ ] `prism --help` command works
- [ ] `pytest` runs (after implementing tests)
- [ ] `ruff check cli/` passes (after implementing code)
- [ ] `black cli/` formats code correctly
- [ ] No dependency conflicts reported

---

## Troubleshooting

### Issue: Entry Point Not Found

**Symptom:**

```bash
prism: command not found
```

**Solution:**

```bash
# Reinstall in editable mode
pip install -e .

# Check if scripts directory is in PATH
python -m site --user-base
# Add <user-base>/bin to PATH if needed
```

### Issue: Dependency Conflicts

**Symptom:**

```
ERROR: Cannot install prism-cli because these package versions have conflicting dependencies.
```

**Solution:**

```bash
# Create fresh virtual environment
python -m venv venv-new
source venv-new/bin/activate  # or venv-new\Scripts\activate on Windows
pip install -e ".[dev]"
```

### Issue: Import Errors

**Symptom:**

```python
ModuleNotFoundError: No module named 'typer'
```

**Solution:**

```bash
# Verify installation
pip list | grep typer

# Reinstall if missing
pip install typer>=0.12.0
```

---

## Related Documentation

- **Architecture Plan:** [`CLI_PLAN.md`](CLI_PLAN.md)
- **Architecture Analysis:** [`CLI_ARCHITECTURE_ANALYSIS.md`](CLI_ARCHITECTURE_ANALYSIS.md)
- **README:** [`README.md`](README.md)
- **Environment Setup:** [`ENV_CONFIGURATION.md`](ENV_CONFIGURATION.md)

---

**Status:** Ready for Implementation  
**Priority:** 🔴 High - Required before any code changes  
**Estimated Time:** 15 minutes
