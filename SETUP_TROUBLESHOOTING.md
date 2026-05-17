# PRISM Setup Troubleshooting Guide

## Quick Fix for "No module named 'sqlalchemy'" Error

### Problem

When running `python start_backend.py`, you get:

```
ModuleNotFoundError: No module named 'sqlalchemy'
```

### Solution

The dependencies need to be installed. Follow these steps:

#### Option 1: Install All Dependencies (Recommended)

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install CLI tool
pip install -e .

# Install frontend dependencies
cd frontend/prism
npm install
cd ../..
```

#### Option 2: Use Setup Script

```bash
# Run the setup script (Git Bash or Linux/Mac)
./setup.sh
```

#### Option 3: Manual Virtual Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Windows (CMD):
.\venv\Scripts\activate.bat

# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Install frontend
cd frontend/prism
npm install
cd ../..
```

### Verify Installation

```bash
# Check Python packages
pip list | grep -E "sqlalchemy|fastapi|uvicorn"

# Expected output:
# fastapi         0.111.0
# sqlalchemy      2.0.30
# uvicorn         0.29.0

# Check CLI installation
prism --help

# Check frontend dependencies
cd frontend/prism && npm list --depth=0
```

---

## Common Setup Issues

### Issue 1: Virtual Environment Not Activated

**Symptom:** Packages install but still get import errors

**Solution:**

```bash
# Activate virtual environment first
# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Then install
pip install -r requirements.txt
```

### Issue 2: Python Version Mismatch

**Symptom:** Installation fails or compatibility errors

**Solution:**

```bash
# Check Python version
python --version
# Required: Python 3.13+

# If wrong version, install Python 3.13+
# Then recreate virtual environment
python3.13 -m venv venv
```

### Issue 3: Permission Errors on Windows

**Symptom:** "cannot be loaded because running scripts is disabled"

**Solution:**

```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate venv
.\venv\Scripts\Activate.ps1
```

### Issue 4: npm install Fails

**Symptom:** Frontend dependencies won't install

**Solution:**

```bash
# Check Node.js version
node --version
# Required: Node.js 18+

# Clear npm cache
cd frontend/prism
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Issue 5: Port Already in Use

**Symptom:** Backend or frontend won't start

**Solution:**

```bash
# Find and kill process on port 8000 (backend)
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9

# Find and kill process on port 3000 (frontend)
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:3000 | xargs kill -9
```

---

## Complete Fresh Setup (Nuclear Option)

If nothing works, start completely fresh:

```bash
# 1. Delete all generated files
rm -rf venv/
rm -rf frontend/prism/node_modules/
rm -rf frontend/prism/dist/
rm -rf __pycache__/
rm -rf *.egg-info/
rm -rf .pytest_cache/

# 2. Create new virtual environment
python -m venv venv

# 3. Activate it
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate

# 4. Upgrade pip
python -m pip install --upgrade pip

# 5. Install Python dependencies
pip install -r requirements.txt

# 6. Install CLI
pip install -e .

# 7. Install frontend
cd frontend/prism
npm install
cd ../..

# 8. Verify everything
python start_backend.py  # Should start without errors
prism --help             # Should show CLI help
cd frontend/prism && npm run dev  # Should start on port 3000
```

---

## Verification Checklist

After setup, verify each component:

### ✅ Backend

```bash
python start_backend.py
# Should see: "INFO:     Uvicorn running on http://127.0.0.1:8000"
# Open: http://localhost:8000/healthz
# Expected: {"ok": true}
```

### ✅ Frontend

```bash
cd frontend/prism
npm run dev
# Should see: "Local: http://localhost:3000/"
# Open: http://localhost:3000/
# Expected: PRISM splash screen
```

### ✅ CLI

```bash
prism --help
# Should show command list

prism version
# Should show version number

prism demo
# Should run analysis and open browser
```

---

## Still Having Issues?

1. **Check Python Path:**

   ```bash
   which python  # Linux/Mac
   where python  # Windows
   # Should point to venv/bin/python or venv\Scripts\python.exe
   ```

2. **Check Installed Packages:**

   ```bash
   pip list
   # Should show all packages from requirements.txt
   ```

3. **Check Node/npm:**

   ```bash
   node --version  # Should be 18+
   npm --version   # Should be 9+
   ```

4. **Check Git:**

   ```bash
   git --version
   # Required for CLI repository detection
   ```

5. **Review Logs:**
   - Backend logs: Terminal output from `python start_backend.py`
   - Frontend logs: Browser DevTools → Console
   - CLI logs: Terminal output from `prism` commands

---

## Environment Variables

Create `.env` file in project root (optional):

```env
# Backend
PRISM_BACKEND_URL=http://localhost:8000

# GitHub (optional for public repos)
PRISM_GITHUB_TOKEN=ghp_your_token_here

# Default repository (optional)
PRISM_REPO_URL=https://github.com/your-org/your-repo

# IBM Bob API (if using)
IBM_BOB_API_KEY=your_api_key_here
```

---

## Quick Reference

### Start All Services

```bash
# Terminal 1 - Backend
python start_backend.py

# Terminal 2 - Frontend
cd frontend/prism && npm run dev

# Terminal 3 - CLI
prism demo
```

### Stop All Services

```bash
# Press Ctrl+C in each terminal
# Or kill processes:
# Windows:
taskkill /F /IM python.exe
taskkill /F /IM node.exe

# Linux/Mac:
pkill -f "python start_backend.py"
pkill -f "npm run dev"
```

---

**Last Updated:** 2026-05-17  
**For more help:** See [CLI_FRONTEND_INTEGRATION.md](CLI_FRONTEND_INTEGRATION.md)
