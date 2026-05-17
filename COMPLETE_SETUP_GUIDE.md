# PRISM - Complete Step-by-Step Setup Guide for Windows

**Last Updated:** 2026-05-17  
**Platform:** Windows 11 with PowerShell  
**Time Required:** 15-20 minutes

---

## Prerequisites Check

Before starting, verify you have:

### 1. Python 3.13

```powershell
python --version
```

**Expected:** `Python 3.13.x`

If not installed:

- Download from: https://www.python.org/downloads/
- During installation, check "Add Python to PATH"

### 2. Node.js 18+

```powershell
node --version
npm --version
```

**Expected:** `v18.x.x` or higher

If not installed:

- Download from: https://nodejs.org/
- Install LTS version

### 3. Git

```powershell
git --version
```

**Expected:** `git version x.x.x`

If not installed:

- Download from: https://git-scm.com/download/win

---

## Step-by-Step Setup

### Step 1: Navigate to Project Directory

```powershell
# Open PowerShell and navigate to your project
cd D:\Hackathon\PRISM
```

### Step 2: Install Python Dependencies

```powershell
# Install minimal dependencies (without tree-sitter that requires Rust)
pip install -r requirements-minimal.txt
```

**Wait for installation to complete.** You should see:

```
Successfully installed fastapi-0.111.0 uvicorn-0.29.0 ...
```

**If you see errors:**

- Try: `python -m pip install --upgrade pip`
- Then retry: `pip install -r requirements-minimal.txt`

### Step 3: Install CLI Tool

```powershell
# Install PRISM CLI in development mode
pip install -e .
```

**Verify installation:**

```powershell
prism --help
```

**Expected output:**

```
Usage: prism [OPTIONS] COMMAND [ARGS]...

  PRISM — Pull Request Intelligent Semantic Monitor.

Commands:
  analyze  Analyze a pull request and print a risk summary.
  demo     Run a canned, bulletproof demo...
  version  Print the CLI version.
```

### Step 4: Install Frontend Dependencies

```powershell
# Navigate to frontend directory
cd frontend\prism

# Install npm packages
npm install
```

**This will take 2-3 minutes.** Wait for completion.

**If you see errors:**

- Try: `npm cache clean --force`
- Then retry: `npm install`

```powershell
# Return to project root
cd ..\..
```

### Step 5: Verify Installation

```powershell
# Check Python packages
pip list | Select-String "fastapi|sqlalchemy|uvicorn"
```

**Expected:**

```
fastapi         0.111.0
sqlalchemy      2.0.30
uvicorn         0.29.0
```

```powershell
# Check CLI
prism version
```

**Expected:** `prism 0.1.0` (or similar)

---

## Running PRISM

### Option A: Quick Test (Recommended First)

Open **THREE** PowerShell terminals:

#### Terminal 1: Start Backend

```powershell
# Navigate to project
cd D:\Hackathon\PRISM

# Start backend server
python start_backend.py
```

**Expected output:**

```
============================================================
>> Starting PRISM Backend Server
============================================================
...
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Keep this terminal running!**

#### Terminal 2: Start Frontend

```powershell
# Navigate to frontend
cd D:\Hackathon\PRISM\frontend\prism

# Start development server
npm run dev
```

**Expected output:**

```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

**Keep this terminal running!**

#### Terminal 3: Test CLI

```powershell
# Navigate to project
cd D:\Hackathon\PRISM

# Run demo mode
prism demo
```

**Expected:**

1. Terminal shows analysis summary
2. Browser automatically opens to: `http://localhost:3000/report/demo8chr`
3. Dashboard displays with demo data

---

## Verification Steps

### 1. Verify Backend is Running

Open browser to: http://localhost:8000/healthz

**Expected:** `{"ok":true}`

### 2. Verify Frontend is Running

Open browser to: http://localhost:3000/

**Expected:** PRISM splash screen with form

### 3. Test CLI Commands

```powershell
# Show help
prism --help

# Show version
prism version

# Run demo (should open browser)
prism demo
```

### 4. Test Web Interface

1. Open: http://localhost:3000/
2. Enter:
   - **PR ID:** `pr-142`
   - **Repository:** `owner/repo`
3. Click **"Analyze Pull Request"**
4. Should see terminal animation
5. Should navigate to dashboard

---

## Common Issues & Fixes

### Issue 1: "Port 8000 already in use"

**Solution:**

```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace <PID> with actual number)
taskkill /PID <PID> /F

# Restart backend
python start_backend.py
```

### Issue 2: "Port 3000 already in use"

**Solution:**

```powershell
# Find process using port 3000
netstat -ano | findstr :3000

# Kill the process
taskkill /PID <PID> /F

# Restart frontend
cd frontend\prism
npm run dev
```

### Issue 3: "Module not found" errors

**Solution:**

```powershell
# Reinstall Python dependencies
pip install -r requirements-minimal.txt

# Reinstall CLI
pip install -e .
```

### Issue 4: Frontend won't start

**Solution:**

```powershell
cd frontend\prism

# Clear cache and reinstall
npm cache clean --force
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install
```

### Issue 5: CLI command not found

**Solution:**

```powershell
# Reinstall CLI
pip install -e .

# If still not working, use full path:
python -m cli.main --help
```

---

## Usage Examples

### CLI Usage

#### Basic Analysis

```powershell
# Analyze a PR (auto-detects repo from git)
prism analyze pr-142

# Analyze with explicit repository
prism analyze pr-142 --repo https://github.com/owner/repo

# Analyze and open dashboard
prism analyze pr-142 --open
```

#### Demo Mode

```powershell
# Run bulletproof demo
prism demo
```

#### JSON Output (for CI/CD)

```powershell
# Get JSON output
prism analyze pr-142 --json
```

### Web Interface Usage

1. **Open:** http://localhost:3000/
2. **Enter PR Details:**
   - PR ID: `142` or `pr-142`
   - Repository: `owner/repo` or full URL
3. **Click:** "Analyze Pull Request"
4. **View:** Dashboard with results

### Direct Dashboard Access

If you have a report ID from CLI:

```
http://localhost:3000/report/<report-id>
```

Example:

```
http://localhost:3000/report/8sj2kd
```

---

## Stopping Services

### Stop Backend

In Terminal 1 (backend), press: `Ctrl + C`

### Stop Frontend

In Terminal 2 (frontend), press: `Ctrl + C`

### Stop All (Alternative)

```powershell
# Kill all Python processes
taskkill /F /IM python.exe

# Kill all Node processes
taskkill /F /IM node.exe
```

---

## Daily Workflow

### Starting Work

```powershell
# Terminal 1 - Backend
cd D:\Hackathon\PRISM
python start_backend.py

# Terminal 2 - Frontend
cd D:\Hackathon\PRISM\frontend\prism
npm run dev

# Terminal 3 - CLI
cd D:\Hackathon\PRISM
prism demo
```

### Stopping Work

Press `Ctrl + C` in each terminal, or close the terminals.

---

## Testing the Integration

### Test 1: CLI → Dashboard Flow

```powershell
# Run demo
prism demo
```

**Verify:**

- ✅ Terminal shows summary
- ✅ Browser opens automatically
- ✅ Dashboard loads on port 3000
- ✅ Report data displays correctly

### Test 2: Web → Dashboard Flow

1. Open: http://localhost:3000/
2. Enter PR details
3. Submit form

**Verify:**

- ✅ Terminal animation plays
- ✅ Navigates to /report/:id
- ✅ Dashboard loads
- ✅ Same data as CLI would show

### Test 3: Direct URL Access

```
http://localhost:3000/report/demo8chr
```

**Verify:**

- ✅ Dashboard loads directly
- ✅ No redirect to splash screen

---

## Environment Configuration (Optional)

Create `.env` file in project root:

```env
# Backend URL
PRISM_BACKEND_URL=http://localhost:8000

# GitHub Token (optional for public repos)
PRISM_GITHUB_TOKEN=ghp_your_token_here

# Default repository (optional)
PRISM_REPO_URL=https://github.com/your-org/your-repo
```

**To get GitHub token:**

1. Go to: https://github.com/settings/tokens
2. Generate new token (classic)
3. Select scopes: `repo` (for private) or `public_repo` (for public)
4. Copy token and paste in `.env`

---

## Troubleshooting Checklist

If something doesn't work:

### 1. Check Prerequisites

```powershell
python --version  # Should be 3.13+
node --version    # Should be 18+
npm --version     # Should be 9+
git --version     # Should be installed
```

### 2. Check Installations

```powershell
pip list | Select-String "fastapi|sqlalchemy"
prism --help
cd frontend\prism && npm list --depth=0
```

### 3. Check Services

```powershell
# Backend health
curl http://localhost:8000/healthz

# Frontend running
# Open: http://localhost:3000/
```

### 4. Check Ports

```powershell
# Check if ports are free
netstat -ano | findstr :8000
netstat -ano | findstr :3000
```

### 5. Check Logs

- Backend: Look at Terminal 1 output
- Frontend: Look at Terminal 2 output
- Browser: Open DevTools → Console

---

## Quick Reference Commands

### Installation

```powershell
pip install -r requirements-minimal.txt
pip install -e .
cd frontend\prism && npm install
```

### Starting Services

```powershell
# Backend
python start_backend.py

# Frontend
cd frontend\prism && npm run dev

# CLI
prism demo
```

### Verification

```powershell
# Backend
curl http://localhost:8000/healthz

# Frontend
# Open: http://localhost:3000/

# CLI
prism --help
```

### Stopping

```powershell
# Press Ctrl+C in each terminal
# Or:
taskkill /F /IM python.exe
taskkill /F /IM node.exe
```

---

## Next Steps

After successful setup:

1. **Read Documentation:**
   - [CLI_FRONTEND_INTEGRATION.md](CLI_FRONTEND_INTEGRATION.md) - Complete guide
   - [SETUP_TROUBLESHOOTING.md](SETUP_TROUBLESHOOTING.md) - Detailed troubleshooting
   - [README.md](README.md) - Project overview

2. **Try Different Commands:**

   ```powershell
   prism analyze pr-142 --repo https://github.com/owner/repo
   prism analyze pr-142 --open
   prism analyze pr-142 --json
   ```

3. **Explore Dashboard:**
   - Interactive dependency graph
   - AI insights
   - Regression scenarios

4. **Test with Real PRs:**
   - Use your own GitHub repositories
   - Analyze actual pull requests

---

## Support

**Documentation:**

- Complete Guide: [CLI_FRONTEND_INTEGRATION.md](CLI_FRONTEND_INTEGRATION.md)
- Troubleshooting: [SETUP_TROUBLESHOOTING.md](SETUP_TROUBLESHOOTING.md)
- Quick Start: [README.md](README.md)

**Common Issues:**

- Dependencies: See [SETUP_TROUBLESHOOTING.md](SETUP_TROUBLESHOOTING.md)
- Port conflicts: Kill processes on ports 3000/8000
- Module errors: Reinstall with `pip install -r requirements-minimal.txt`

---

## Summary

**Setup Steps:**

1. ✅ Install Python dependencies: `pip install -r requirements-minimal.txt`
2. ✅ Install CLI: `pip install -e .`
3. ✅ Install frontend: `cd frontend\prism && npm install`
4. ✅ Start backend: `python start_backend.py`
5. ✅ Start frontend: `cd frontend\prism && npm run dev`
6. ✅ Test CLI: `prism demo`

**Verification:**

- Backend: http://localhost:8000/healthz → `{"ok":true}`
- Frontend: http://localhost:3000/ → Splash screen
- CLI: `prism demo` → Opens dashboard

**You're ready to use PRISM!** 🎉

---

**Document Version:** 1.0  
**Last Updated:** 2026-05-17  
**Platform:** Windows 11 PowerShell
