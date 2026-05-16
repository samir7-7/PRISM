# PRISM Frontend

Predictive Risk Intelligence & Semantic Monitoring Dashboard

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

The app will be available at `http://localhost:3000`

## 🔧 Configuration

Create a `.env` file in the frontend/prism directory:

```env
VITE_API_URL=http://localhost:8000
```

## 📋 Prerequisites

- Node.js 18+ (recommended: 20+)
- Backend API running on `http://localhost:8000`

## 🏗️ Architecture

### Tech Stack
- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Router v7** - Routing
- **Zustand** - State management
- **React Flow** - Dependency graph visualization
- **Framer Motion** - Animations
- **Axios** - HTTP client
- **Lucide React** - Icons

### Project Structure

```
src/
├── components/
│   ├── cli/              # CLI terminal components
│   ├── dashboard/        # Dashboard-specific components
│   ├── layout/           # Layout components (Nav, Sidebar)
│   └── tests/            # Test scenario components
├── pages/                # Route pages
├── services/             # API service layer
├── store/                # Zustand state management
├── types/                # TypeScript type definitions
└── App.tsx               # Main app with routing
```

## 🎨 Design System

### Color Palette
- **Background**: `#0d1117` (near-black)
- **Surface**: `#161b22` (card/panel bg)
- **Border**: `#21262d` (subtle dividers)
- **Orange**: `#f97316` (warnings, drift indicators)
- **Green**: `#22c55e` (success, nominal state)
- **Red**: `#ef4444` (critical alerts)
- **Yellow**: `#eab308` (warnings)
- **Blue**: `#3b82f6` (info, buttons)
- **Text Primary**: `#e6edf3`
- **Text Muted**: `#8b949e`

### Typography
- **UI Font**: Inter, system-ui
- **Code Font**: JetBrains Mono, Fira Code

## 🗺️ Routes

- `/` - CLI Splash / Analysis Input
- `/dashboard` - Main Dashboard (Explorer)
- `/dashboard/tests` - Regression Test Scenarios
- `/dashboard/timeline` - Timeline View (Coming Soon)
- `/dashboard/impact` - Impact Analysis (Coming Soon)
- `/report/:id` - Full Report View

## 🔌 API Integration

The frontend connects to the backend API at `http://localhost:8000`:

### Endpoints Used
- `POST /api/analyze` - Analyze a pull request
- `GET /api/reports/{id}` - Get specific report
- `GET /api/reports/pr/{pr_id}` - Get report by PR ID
- `GET /api/reports` - List all reports
- `GET /api/reports/stats/summary` - Get statistics
- `GET /health` - Health check

### CORS Configuration

**IMPORTANT**: The backend must allow CORS from `http://localhost:3000`

Add to your backend configuration:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🎯 Features

### ✅ Implemented
- CLI-style splash screen with typewriter animation
- Real-time PR analysis with loading states
- Interactive dependency graph (drag, zoom, pan)
- AI-powered semantic insights display
- Risk detection and categorization
- Regression test scenario generation
- Responsive dark theme UI
- Full API integration
- State management with Zustand
- Route-based navigation

### 🔄 Data Flow

1. User enters PR ID and repository on splash screen
2. Frontend calls `POST /api/analyze`
3. Terminal animation plays during analysis
4. Results stored in Zustand global state
5. User redirected to dashboard
6. Dashboard reads from state (no additional API call)
7. "RE-ANALYZE" button clears state and returns to splash

## 🧪 Development

### Running with Backend

1. Start the backend server:
   ```bash
   cd backend
   python start_backend.py
   ```

2. Start the frontend dev server:
   ```bash
   cd frontend/prism
   npm run dev
   ```

3. Open `http://localhost:3000`

### Building for Production

```bash
npm run build
```

The build output will be in the `dist/` directory.

## 🐛 Troubleshooting

### CORS Errors
- Ensure backend has CORS middleware configured
- Check that `VITE_API_URL` matches your backend URL

### TypeScript Errors
- Run `npm install` to ensure all types are installed
- Check that `src/vite-env.d.ts` exists

### Graph Not Rendering
- Ensure React Flow styles are imported
- Check browser console for errors
- Verify `impacted_nodes` data from API

### Animation Issues
- Clear browser cache
- Check Framer Motion is installed correctly

## 📝 Notes

- The app requires an active backend connection to function
- All data is fetched from the backend API (no mock data)
- The dependency graph is generated from `impacted_nodes` array
- Risk badges are mapped: HIGH→CRITICAL, MEDIUM→WARNING, LOW→ADVISORY

## 🤝 Contributing

When adding new features:
1. Follow the existing component structure
2. Use TypeScript for type safety
3. Maintain the dark theme color palette
4. Add proper loading and error states
5. Update this README if needed

---

Built with ❤️ for PRISM - Predictive Risk Intelligence & Semantic Monitoring