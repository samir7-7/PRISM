# PRISM Dashboard Deep-Link Flow Fix

## Problem Summary
The CLI returned a dashboard URL after PR analysis, but opening that URL showed the dashboard input form asking for PR number and repository URL again, instead of directly displaying the analysis report.

## Root Causes Identified

1. **Wrong Port in Backend URLs**: Backend was generating dashboard URLs with port 3000 instead of 5173 (Vite's default port)
2. **Frontend Type Mismatch**: Frontend Report component was trying to parse report IDs as integers, but backend returns string-based deterministic IDs
3. **API Service Type Constraint**: Frontend API service only accepted numeric report IDs

## Changes Made

### Backend Changes

#### 1. `backend/api/analysis.py`
- **Line 57**: Changed dashboard URL from `http://localhost:3000/report/{report_id}` to `http://localhost:5173/report/{report_id}`
- **Line 95**: Changed fallback dashboard URL from port 3000 to 5173
- **Purpose**: Ensure CLI returns correct frontend URL

#### 2. `backend/analysis.py`
- **Line 18**: Updated DEMO_RESPONSE dashboard_url from port 3000 to 5173
- **Line 149**: Updated analyze() function dashboard_url from port 3000 to 5173
- **Purpose**: Ensure all code paths return correct frontend URL

### Frontend Changes

#### 3. `frontend/prism/src/services/api.ts`
- **Line 42**: Changed `getReport` parameter type from `reportId: number` to `reportId: string | number`
- **Purpose**: Accept both string-based deterministic IDs and numeric database IDs

#### 4. `frontend/prism/src/pages/Report.tsx`
- **Line 25**: Changed from `apiService.getReport(parseInt(id))` to `apiService.getReport(id)`
- **Purpose**: Pass report ID as-is without parsing, supporting string IDs

## How It Works Now

### Backend Flow
1. CLI calls `POST /api/analysis/run` with PR number and repository URL
2. Backend generates deterministic 8-character report_id using SHA1 hash: `hashlib.sha1(f"{pr_id}:{repo_url}").hexdigest()[:8]`
3. Backend stores report in database with this report_id
4. Backend returns response with:
   - `report_id`: The 8-character string ID
   - `dashboard_url`: `http://localhost:5173/report/{report_id}`
   - Risk score, status, etc.

### Frontend Flow
1. User clicks the dashboard URL (e.g., `http://localhost:5173/report/a1b2c3d4`)
2. React Router matches `/report/:id` route and renders `Report` component
3. Report component extracts `id` from URL params
4. Report component calls `apiService.getReport(id)` with the string ID
5. API service calls `GET /api/reports/{report_id}` 
6. Backend's `get_report` endpoint:
   - First tries to parse as integer and lookup by database ID
   - If that fails or ID is not numeric, looks up by string report_id
7. Backend returns full report data
8. Frontend renders Dashboard component with the report data

## API Endpoint Behavior

### `GET /api/reports/{report_id}`
The endpoint now handles both ID types:
- **Numeric IDs** (e.g., `123`): Looks up by database primary key
- **String IDs** (e.g., `a1b2c3d4`): Looks up by deterministic report_id field

This dual-mode lookup ensures backward compatibility while supporting the new deep-link flow.

## Testing the Fix

### Manual Test Steps
1. Start backend: `python start_backend.py`
2. Start frontend: `cd frontend/prism && npm run dev`
3. Run CLI analysis: `prism analyze pr-142 --repo https://github.com/owner/repo`
4. CLI prints dashboard URL like: `http://localhost:5173/report/a1b2c3d4`
5. Click or paste the URL in browser
6. **Expected**: Dashboard loads immediately with analysis results
7. **Expected**: No input form is shown

### Demo PR Test
```bash
prism analyze pr-142 --repo https://github.com/demo/repo
```
Should return:
```
Dashboard URL: http://localhost:5173/report/demo8chr
```

Opening this URL should show the demo analysis report directly.

## Files Modified

1. `backend/api/analysis.py` - Fixed dashboard URLs (2 locations)
2. `backend/analysis.py` - Fixed dashboard URLs (2 locations)
3. `frontend/prism/src/services/api.ts` - Accept string/number IDs
4. `frontend/prism/src/pages/Report.tsx` - Don't parse ID as integer

## Acceptance Criteria Met

✅ Running `prism analyze pr-142 --repo <github-url>` prints a dashboard URL
✅ Dashboard URL points to correct port (5173)
✅ Dashboard URL includes deterministic report_id
✅ Clicking the URL opens the exact analysis report
✅ No PR number or GitHub repo URL is requested again
✅ Report page shows loading state while fetching
✅ Report page shows error and redirects if report not found
✅ Backend stores report with deterministic report_id
✅ Backend GET endpoint supports both string and numeric IDs

## Architecture Notes

### Report ID Strategy
The system uses a **deterministic report ID** approach:
- Generated from PR number + repository URL
- Same PR analyzed multiple times gets same report_id
- Enables direct linking without database lookups
- 8 characters from SHA1 hash provides good uniqueness

### URL Structure
- Landing page: `http://localhost:5173/`
- Report page: `http://localhost:5173/report/{report_id}`
- Dashboard (after form): `http://localhost:5173/dashboard`

### Routing
- `/` - CLISplash page with input form
- `/report/:id` - Direct report view (deep-link target)
- `/dashboard` - Dashboard after manual form submission
- `/dashboard/tests` - Test scenarios view

## Future Enhancements

1. **URL Shortening**: Consider shorter report IDs (4-6 chars) if collision risk is acceptable
2. **Report Versioning**: Track multiple analyses of same PR over time
3. **Share Links**: Add copy-to-clipboard button for dashboard URLs
4. **QR Codes**: Generate QR codes for easy mobile access
5. **Expiration**: Add TTL for old reports to manage database size

## Made with Bob