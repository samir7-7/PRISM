# PRISM Setup Instructions

## Prerequisites
- Python 3.12+
- Node.js 18+
- Git

## Backend Setup

### 1. Install Python Dependencies
```bash
# Make sure you're in the project root
cd "E:\Hacakathon IBM"

# Activate virtual environment
.\venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt

# If that fails, install core dependencies manually:
pip install fastapi uvicorn sqlalchemy httpx python-dotenv pydantic typer rich
```

### 2. Verify Backend Installation
```bash
python -c "import uvicorn; print('uvicorn installed')"
python -c "import fastapi; print('fastapi installed')"
```

### 3. Start Backend
```bash
python start_backend.py
```

Backend should start on: `http://localhost:8000`

## Frontend Setup

### 1. Install Node Dependencies
```bash
cd frontend/prism
npm install
```

### 2. Start Frontend
```bash
npm run dev
```

Frontend should start on: `http://localhost:5173`

## CLI Setup

### 1. Install CLI (if not already installed)
```bash
cd cli
pip install -e .
```

### 2. Verify CLI Installation
```bash
prism --help
```

## Testing the Deep-Link Flow

### 1. Start Both Servers
Terminal 1:
```bash
python start_backend.py
```

Terminal 2:
```bash
cd frontend/prism
npm run dev
```

### 2. Run Analysis
Terminal 3:
```bash
prism analyze pr-142 --repo https://github.com/owner/repo
```

### 3. Expected Output
```
✓ Analysis complete
  Report ID: a1b2c3d4
  Risk Score: 65 (MEDIUM)
  Impacted Nodes: 8
  
Dashboard URL: http://localhost:5173/report/a1b2c3d4
```

### 4. Test Deep-Link
- Click or paste the dashboard URL in your browser
- **Expected**: Dashboard loads immediately with analysis results
- **Expected**: No input form is shown

## Troubleshooting

### "ModuleNotFoundError: No module named 'uvicorn'"
```bash
pip install uvicorn
```

### "ModuleNotFoundError: No module named 'fastapi'"
```bash
pip install fastapi
```

### Backend won't start
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process if needed (replace PID)
taskkill /PID <PID> /F
```

### Frontend won't start
```bash
# Check if port 5173 is in use
netstat -ano | findstr :5173

# Kill process if needed
taskkill /PID <PID> /F
```

### CLI not found
```bash
# Reinstall CLI
cd cli
pip install -e .
```

## Environment Variables

### Backend (.env in project root)
```env
DATABASE_URL=sqlite:///./prism.db
GITHUB_TOKEN=your_github_token_here
OPENROUTER_API_KEY=your_openrouter_key_here
```

### Frontend (frontend/prism/.env)
```env
VITE_API_URL=http://localhost:8000
```

### CLI (cli/.env)
```env
PRISM_API_URL=http://localhost:8000
GITHUB_TOKEN=your_github_token_here
```

## Quick Start (All in One)

```bash
# Terminal 1 - Backend
python start_backend.py

# Terminal 2 - Frontend
cd frontend/prism && npm run dev

# Terminal 3 - Test CLI
prism analyze pr-142 --repo https://github.com/demo/repo
```

## Made with Bob