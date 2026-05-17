# PRISM Frontend Deep Audit — `frontend_issues.md`

**Audit Date:** 2026-05-17
**Auditor Role:** Senior Frontend Architect / Routing-Debugging Specialist
**Scope:** Full frontend system — routing, state, API integration, component architecture, navigation flows, backend integration

---

## 1. Executive Summary

The PRISM frontend has **one critical root-cause bug** that directly explains why URLs like `http://localhost:5173/report/0717400d` redirect to the homepage instead of rendering the report page. This is caused by a **report ID generation mismatch** between the CLI-facing endpoint and the database storage layer — the two code paths use different hash inputs to generate the deterministic report ID, meaning the ID embedded in the dashboard URL does **not** match the ID stored in the database. The frontend fetch fails with a 404, the error handler silently navigates to `/`, and the user sees the homepage.

Beyond this critical bug, there are **20+ additional issues** spanning architectural fragility, race conditions, missing error handling, type mismatches, dead code, and patterns that will cause future failures.

---

## 2. Overall Frontend Health Assessment

| Dimension | Rating | Notes |
|---|---|---|
| Routing | ⚠️ Fragile | Catch-all wildcard redirect masks errors; no 404 page |
| State Management | 🔴 Critical | In-memory only; no persistence; race condition in Report→Dashboard flow |
| API Integration | 🔴 Critical | Report ID mismatch between CLI and DB; no retry logic |
| Error Handling | 🔴 Poor | Silent redirects on error; no user-facing error pages |
| Type Safety | ⚠️ Moderate | `as any` casts; type mismatches between backend/frontend schemas |
| Component Architecture | ⚠️ Fragile | Circular page imports; no error boundaries; no Suspense |
| Configuration | ⚠️ Incomplete | No frontend `.env`; hardcoded defaults |
| Navigation | 🔴 Broken | Multiple issues causing unintended redirects |

---

## 3. Routing System Analysis

### 3.1 Route Definitions (`App.tsx`)

```
/              → CLISplash
/dashboard     → Dashboard
/dashboard/tests → Tests
/dashboard/timeline → ComingSoon
/dashboard/impact   → ComingSoon
/report/:id    → Report
*              → Navigate to "/" (replace)
```

### 3.2 Issues

**ISSUE-R1: Wildcard Catch-All Silently Swallows All Invalid Routes**
- **File:** `App.tsx:24`
- **Severity:** HIGH
- **Root Cause:** `<Route path="*" element={<Navigate to="/" replace />} />` redirects every unmatched route to home with `replace`, destroying browser history and masking 404s.
- **Observed Behavior:** Any typo in URL, deleted route, or failed route match silently redirects to homepage.
- **Expected Behavior:** Should render a 404 page or at minimum preserve the URL in history.
- **Impact:** Makes debugging routing issues nearly impossible; users lose context on any navigation failure.

**ISSUE-R2: No Layout Route Wrapper**
- **File:** `App.tsx` (entire file)
- **Severity:** MEDIUM
- **Root Cause:** All routes are flat siblings. No `<Route element={<Layout />}>` wrapper to share common providers, error boundaries, or layout chrome.
- **Impact:** Every page must independently handle loading states, error boundaries, and layout. No shared context scope.

**ISSUE-R3: No Route Guards or Protected Routes**
- **File:** `App.tsx`
- **Severity:** LOW (for current scope)
- **Root Cause:** No authentication or data-availability guards on routes. Dashboard and Tests pages self-redirect in `useEffect` instead of being protected at the route level.
- **Impact:** Race conditions between route mounting and data availability checks.

**ISSUE-R4: No Lazy Loading**
- **File:** `App.tsx`
- **Severity:** LOW
- **Root Cause:** All pages are eagerly imported. No `React.lazy()` or `Suspense` boundaries.
- **Impact:** Initial bundle includes all pages even though most users only visit 1-2 routes.

**ISSUE-R5: BrowserRouter Without Basename or Future Flags**
- **File:** `App.tsx:10`
- **Severity:** LOW
- **Root Cause:** `<BrowserRouter>` used without `basename` or React Router v7 future flags.
- **Impact:** May cause issues if deployed to a sub-path; missing v7 migration flags.

---

## 4. Report Flow Analysis — Full Trace

### 4.1 Expected Flow

```
CLI → POST /api/analysis/run → Backend generates report_id → Stores in DB → Returns dashboard_url
User opens dashboard_url → Browser → React Router matches /report/:id → Report component mounts
Report extracts id from useParams → Calls GET /api/reports/{id} → Backend returns report
Report converts response → Stores in Zustand → Renders <Dashboard /> → Dashboard reads from store → Renders UI
```

### 4.2 Actual Flow (Broken)

```
CLI → POST /api/analysis/run → Backend generates report_id using sha1("{pr_id}:{repo_url}")[:8]
     → Stores report in DB using sha1("{repository}#{pr_id}")[:8]  ← DIFFERENT HASH!
     → Returns dashboard_url with CLI's report_id

User opens dashboard_url → /report/{cli_report_id}
Report component → GET /api/reports/{cli_report_id}
Backend → Tries int lookup (fails) → Tries string lookup → NOT FOUND (DB has different ID)
Backend → 404 response
Report → catch block → navigate("/") → USER SEES HOMEPAGE
```

### 4.3 CRITICAL ROOT CAUSE: Report ID Generation Mismatch

**ISSUE-RC1: Two Different Report ID Algorithms**
- **Files:** `backend/analysis.py:31-35` vs `backend/repositories/report_repository.py:22-24`
- **Severity:** CRITICAL (BLOCKER)
- **CLI/Endpoint algorithm:** `sha1(f"{pr_id}:{repo_url}").hexdigest()[:8]`
- **Database/Repository algorithm:** `sha1(f"{repository}#{pr_id}").hexdigest()[:8]`
- **Example:** For `pr_id="pr-142"`, `repo_url="https://github.com/demo/repo"`:
  - CLI generates: `sha1("pr-142:https://github.com/demo/repo")` → e.g., `a1b2c3d4`
  - DB stores: `sha1("https://github.com/demo/repo#pr-142")` → e.g., `e5f6g7h8`
- **Result:** The dashboard URL contains `a1b2c3d4` but the database has the report under `e5f6g7h8`. Lookup always fails.
- **Reproduction:** Run any CLI analysis → open the returned URL → observe redirect to homepage.
- **Architectural Impact:** Complete breakage of the deep-link feature. No report URL will ever work.

### 4.4 Secondary Flow Issues

**ISSUE-F1: Report Component Error Handler Silently Redirects**
- **File:** `Report.tsx:48-54`
- **Severity:** HIGH
- **Root Cause:** On any API failure (404, 500, network error), the catch block calls `navigate('/')` with no user feedback.
- **Observed Behavior:** User sees a brief "Loading report..." flash, then homepage appears. No error message.
- **Expected Behavior:** Should display an error page with the failure reason and a retry option.

**ISSUE-F2: Dashboard Redirect Guard Conflicts with Report Flow**
- **File:** `Dashboard.tsx:15-20`
- **Severity:** HIGH
- **Root Cause:** Dashboard has `useEffect` that redirects to `/` when `!currentAnalysis && !isLoading`. When Report renders Dashboard after fetching data, there is a potential race condition where Dashboard's effect fires before Zustand state propagation is visible.
- **Mechanism:** Report calls `setAnalysis(data)` then `setLoading(false)` then sets `isLoadingReport=false`. Dashboard mounts, reads store. If `currentAnalysis` is still `null` (state not yet propagated) and `isLoading` is `false` (or the timing is off), Dashboard navigates to `/`.
- **React 19 Factor:** Concurrent rendering and the babel react-compiler plugin may alter the timing of state visibility across component boundaries.

**ISSUE-F3: Report Renders Dashboard as a Component, Not a Route**
- **File:** `Report.tsx:5,68`
- **Severity:** MEDIUM
- **Root Cause:** `Report` imports `Dashboard` from `./Dashboard` and renders it directly (`return <Dashboard />`). This bypasses the router, meaning Dashboard has no route context for its own navigation.
- **Impact:** Dashboard's `useNavigate()` and `useLocation()` still work (they read from context), but the URL in the browser remains `/report/:id` while Dashboard renders. This creates URL/Content mismatch.

**ISSUE-F4: No Loading State Coordination Between Report and Dashboard**
- **File:** `Report.tsx:60-68`, `Dashboard.tsx:22-28`
- **Severity:** MEDIUM
- **Root Cause:** Report uses local `isLoadingReport` state. Dashboard uses store `isLoading`. These are separate and unsynchronized.
- **Impact:** Dashboard may show "Loading analysis..." while Report has already finished loading, or vice versa.

---

## 5. Root Cause Candidates

### 5.1 Primary Root Cause (Confirmed)

**Report ID Hash Mismatch** — The CLI endpoint (`/api/analysis/run`) and the database repository layer use different string formats to generate the deterministic report ID. The URL returned to the user contains an ID that does not exist in the database. Every deep-link report request results in a 404, which triggers a silent redirect to the homepage.

### 5.2 Secondary Root Causes (Contributing)

1. **Silent error handling** — Even if the API call succeeded, the Dashboard redirect guard could still cause issues due to race conditions.
2. **No error visibility** — Users have no way to know why the redirect happened.
3. **Zustand in-memory store** — Page refresh loses all data, causing Dashboard to redirect.

---

## 6. Confirmed Broken Flows

### 6.1 Deep-Link Report Access (CRITICAL)
- **Flow:** User opens `http://localhost:5173/report/{id}` from CLI output
- **Break Point:** API returns 404 (report ID mismatch) → catch block → `navigate('/')`
- **Result:** Homepage shown instead of report

### 6.2 Dashboard Page Refresh (HIGH)
- **Flow:** User is on `/dashboard`, presses F5/refresh
- **Break Point:** Zustand store is empty (in-memory) → Dashboard's useEffect sees `!currentAnalysis && !isLoading` → `navigate('/')`
- **Result:** User loses all context, redirected to homepage

### 6.3 Tests Page Direct Access (HIGH)
- **Flow:** User opens `http://localhost:5173/dashboard/tests` directly
- **Break Point:** Same as 6.2 — no analysis data in store → redirect to `/`
- **Result:** Cannot access tests page without first running analysis through the splash form

### 6.4 ComingSoon Pages Redirect (MEDIUM)
- **Flow:** User opens `/dashboard/timeline` or `/dashboard/impact`
- **Break Point:** ComingSoon components do NOT have redirect guards, but if accessed before any analysis, they render with empty layout (Sidebar shows no PR info)
- **Result:** Partial/broken UI rather than redirect (inconsistent with other pages)

### 6.5 Sidebar Navigation Dead Links (MEDIUM)
- **Flow:** User clicks "SEMANTIC TREE", "RISK ANALYSIS", or "LOGS" in Sidebar
- **Break Point:** All three navigate to `/dashboard` (same path)
- **Result:** No visual feedback, no navigation, no differentiation

---

## 7. Missing/Incomplete Components

### 7.1 No Error Boundary
- **Severity:** HIGH
- **Impact:** Any React rendering error crashes the entire app with a blank white screen.
- **Expected:** Error boundary wrapping routes to show user-friendly error pages.

### 7.2 No 404 Page
- **Severity:** MEDIUM
- **Impact:** All invalid URLs silently redirect to home. Users cannot tell if a URL is wrong or if content was removed.

### 7.3 No Report-Specific Error Page
- **Severity:** HIGH
- **Impact:** When a report fails to load, user sees homepage with no explanation.

### 7.4 No Suspense Boundaries
- **Severity:** LOW
- **Impact:** No streaming or progressive loading. All-or-nothing render.

### 7.5 No Loading Skeleton Components
- **Severity:** LOW
- **Impact:** "Loading report..." and "Loading analysis..." are plain text, not skeleton UI.

### 7.6 No Frontend `.env` File
- **Severity:** MEDIUM
- **Impact:** API URL relies on hardcoded default. No environment-specific configuration.

---

## 8. Backend Integration Problems

### 8.1 Report ID Generation Mismatch (CRITICAL)
- **Already documented in Section 4.3**
- **Files:** `backend/analysis.py:31-35`, `backend/repositories/report_repository.py:22-24`
- **Two different hash inputs produce two different IDs for the same PR.**

### 8.2 API Response Shape Mismatch
- **Files:** `backend/schemas/report.py` vs `frontend/src/types/index.ts`
- **Severity:** MEDIUM
- **Issue:** Backend `ReportResponse` has `report_id: Optional[str]` field. Frontend `ReportResponse` type has `id: number` but no `report_id` field. The Report component maps `report.id` (numeric DB ID) but the URL uses the string report_id.
- **Impact:** The data mapping in `Report.tsx:29-43` works by coincidence but is fragile.

### 8.3 `analysis_duration` Type Inconsistency
- **Backend:** `ReportResponse.analysis_duration: Optional[float]`
- **Frontend:** `AnalyzeResponse.analysis_duration: number` (required)
- **Report.tsx workaround:** `report.analysis_duration || 0`
- **Severity:** LOW
- **Risk:** If backend returns `null`, the `|| 0` fallback masks the issue but StatsRow may still fail.

### 8.4 No API Versioning
- **Severity:** LOW
- **Impact:** Any backend schema change silently breaks the frontend.

### 8.5 CORS Documentation Out of Date
- **File:** `frontend/prism/Frontend_README.md:107-121`
- **Severity:** LOW
- **Issue:** README says backend must allow `http://localhost:3000`, but Vite runs on `5173`. Backend config is correct (`3000` and `5173`), but documentation is misleading.

---

## 9. State Management Issues

### 9.1 Zustand Store is In-Memory Only
- **File:** `store/analysisStore.ts`
- **Severity:** HIGH
- **Issue:** No persistence middleware (localStorage, sessionStorage, or IndexedDB). All analysis state is lost on page refresh.
- **Impact:** Deep-linked reports work only on first load. Any refresh loses data and redirects to home.

### 9.2 No Store Hydration on Report Route
- **File:** `pages/Report.tsx`
- **Severity:** HIGH
- **Issue:** When a user navigates to `/report/:id`, the Report component fetches data and stores it. But if the user then navigates to `/dashboard` and refreshes, the store is cleared.
- **Expected:** Store should persist or re-hydrate from the current report ID on mount.

### 9.3 Single Global Analysis State
- **File:** `store/analysisStore.ts`
- **Severity:** MEDIUM
- **Issue:** Only one `currentAnalysis` can exist at a time. Cannot compare reports or view report history.
- **Impact:** Limits future features like report comparison, history, or multi-report dashboards.

### 9.4 Store Setters in useEffect Dependencies
- **File:** `Report.tsx:58`
- **Severity:** LOW
- **Issue:** `[id, navigate, setAnalysis, setLoading, setError]` — Zustand setters are stable references, but including them in the dependency array is unnecessary and signals a misunderstanding of the store API.

---

## 10. Navigation & Redirect Issues

### 10.1 Report Component Redirects on Any Error
- **File:** `Report.tsx:53`
- **Severity:** HIGH
- **Issue:** `navigate('/')` on any error — 404, 500, network timeout, CORS failure. All treated identically.
- **Expected:** Differentiate between "report not found" (show 404), "server error" (show retry), "network error" (show offline message).

### 10.2 Dashboard Redirects When No Data
- **File:** `Dashboard.tsx:17`
- **Severity:** HIGH
- **Issue:** `navigate('/')` when `!currentAnalysis && !isLoading`. This fires on page refresh, direct URL access, and any timing issue.
- **Expected:** Should be a route-level guard, not a component-level side effect.

### 10.3 Tests Page Same Redirect Pattern
- **File:** `Tests.tsx:15-18`
- **Severity:** HIGH
- **Issue:** Identical redirect pattern as Dashboard.

### 10.4 TopNav Logo Navigates to Home, Not Dashboard
- **File:** `components/layout/TopNav.tsx:28`
- **Severity:** MEDIUM
- **Issue:** Clicking "PRISM" logo navigates to `/` (splash page), not `/dashboard`. Users expect logo to go to the main app view.
- **Impact:** When viewing a report or dashboard, clicking logo loses all context.

### 10.5 RE-ANALYZE Button Clears All State
- **File:** `components/layout/TopNav.tsx:16-19`
- **Severity:** MEDIUM
- **Issue:** `clearAnalysis()` then `navigate('/')` destroys all stored data. If user is viewing a deep-linked report, clicking RE-ANALYZE loses the report permanently (no persistence).

### 10.6 TerminalWindow Displays Wrong Port
- **File:** `components/cli/TerminalWindow.tsx:149`
- **Severity:** MEDIUM
- **Issue:** Displays `http://localhost:3000/report/{reportId}` but Vite runs on port 5173. The `navigate()` call is correct, but the displayed URL is wrong and would fail if copied/pasted.

---

## 11. API Handling Problems

### 11.1 No Request Interceptors
- **File:** `services/api.ts:12-17`
- **Severity:** LOW
- **Issue:** No auth token injection, no request logging, no request timeout configuration beyond axios defaults.

### 11.2 Error Interceptor Only Logs
- **File:** `services/api.ts:20-26`
- **Severity:** MEDIUM
- **Issue:** Interceptor logs the error and re-throws. No transformation, no retry logic, no user-friendly error mapping.

### 11.3 No Retry Logic
- **Severity:** MEDIUM
- **Issue:** All API calls are single-attempt. Transient failures (network blips, server restarts) cause permanent navigation to home.

### 11.4 No Request Cancellation
- **Severity:** LOW
- **Issue:** If user navigates away while a report is loading, the in-flight request is not cancelled.

### 11.5 `getReport` Accepts Both String and Number But Backend Endpoint Behavior Differs
- **File:** `services/api.ts:42-44`, `backend/api/reports.py:19-54`
- **Severity:** LOW (due to the larger ID mismatch issue)
- **Issue:** Frontend passes string IDs. Backend tries int lookup first (`report_id.isdigit()`), then string lookup. For 8-char hex IDs like `0717400d`, `isdigit()` returns false, so string lookup is used. This is correct behavior, but the ID mismatch means the string lookup still fails.

---

## 12. Error Handling Weaknesses

### 12.1 No User-Facing Error Messages
- **Severity:** HIGH
- **Files:** `Report.tsx:48-54`, `Dashboard.tsx:15-20`, `Tests.tsx:14-18`
- **Issue:** All errors result in silent redirects. Users never see what went wrong.

### 12.2 No Error State Rendering
- **Severity:** HIGH
- **Issue:** The Zustand store has an `error` field, but no component renders it. `setError()` is called but the error is never displayed.

### 12.3 Console-Only Error Logging
- **Severity:** MEDIUM
- **Issue:** `console.error('Failed to load report:', error)` in `Report.tsx:49`. Errors are invisible to end users.

### 12.4 No Network Error Differentiation
- **Severity:** MEDIUM
- **Issue:** 404, 500, timeout, CORS, and DNS failures all produce the same behavior (redirect to home).

### 12.5 No Error Recovery
- **Severity:** MEDIUM
- **Issue:** Once an error occurs, the only recovery is manual navigation. No retry buttons, no "try again" flows.

---

## 13. Configuration Problems

### 13.1 No Frontend `.env` File
- **Severity:** MEDIUM
- **Location:** `frontend/prism/` (missing)
- **Issue:** `VITE_API_URL` is not configured. Falls back to `http://localhost:8000` which happens to be correct for development but is fragile.

### 13.2 Vite Config Has Duplicate React Processing
- **File:** `vite.config.js:9-10`
- **Severity:** MEDIUM
- **Issue:** Both `react()` plugin and `babel()` with `reactCompilerPreset()` are configured. The React plugin already handles JSX/TSX transformation. Adding Babel with the React compiler may cause double-processing or conflicts.

### 13.3 README States Wrong Port
- **File:** `frontend/prism/FRONTEND_README.md:21`
- **Severity:** LOW
- **Issue:** Says "The app will be available at `http://localhost:3000`" but Vite defaults to `5173`.

### 13.4 Dead `App.jsx` File
- **File:** `src/App.jsx`
- **Severity:** LOW
- **Issue:** This is the default Vite template starter file. It is not imported anywhere (main.jsx imports `App.tsx`), but its presence is confusing and suggests incomplete cleanup.

### 13.5 No TypeScript Strict Mode Verification
- **Severity:** LOW
- **Issue:** `App.tsx` uses `as any` cast on line 45 of `Report.tsx`. No `tsconfig.json` was inspected for strict mode settings.

---

## 14. Architecture Consistency Problems

### 14.1 Mixed File Extensions
- **Issue:** `main.jsx` imports `App.tsx`. Project mixes `.jsx`, `.tsx`, `.ts` files.
- **Severity:** LOW
- **Impact:** Inconsistent conventions; potential confusion about which files are active.

### 14.2 Page Imports Dashboard as Component
- **File:** `Report.tsx:5`
- **Severity:** MEDIUM
- **Issue:** Report page imports and renders Dashboard directly instead of navigating to the `/dashboard` route. This creates a coupling between pages that should be independent.

### 14.3 No Shared Layout Component
- **Severity:** MEDIUM
- **Issue:** Dashboard, Tests, and ComingSoon all duplicate the same layout structure (`TopNav` + `Sidebar` + `main`). No shared layout wrapper.

### 14.4 Sidebar Navigation Items All Point to Same Route
- **File:** `components/layout/Sidebar.tsx:18-24`
- **Severity:** MEDIUM
- **Issue:** "DASHBOARD", "SEMANTIC TREE", "RISK ANALYSIS", and "LOGS" all navigate to `/dashboard`. Only "TESTS" has a unique path. This makes the sidebar misleading.

### 14.5 DependencyGraph Builds Fake Edges
- **File:** `components/dashboard/DependencyGraph.tsx:91-104`
- **Severity:** LOW
- **Issue:** Edges are created by connecting sequential nodes (`index-1 → index`), not by actual dependency relationships. The graph visualization is cosmetic, not data-driven.

### 14.6 Zoom Controls Are Non-Functional
- **File:** `components/dashboard/DependencyGraph.tsx:121-131`
- **Severity:** LOW
- **Issue:** Zoom in/out/fit buttons are rendered but have no `onClick` handlers. React Flow's built-in Controls component provides actual zoom functionality, making these buttons redundant dead UI.

---

## 15. Technical Debt Areas

### 15.1 `as any` Type Cast
- **File:** `Report.tsx:45`
- **Issue:** `setAnalysis(analysisData as any)` bypasses TypeScript type checking.
- **Risk:** Masks type mismatches between `ReportResponse` and `AnalyzeResponse`.

### 15.2 Dead `App.jsx` File
- **File:** `src/App.jsx`
- **Issue:** Default Vite template content, not imported anywhere. Should be removed.

### 15.3 App.css Contains Unused Template Styles
- **File:** `src/App.css`
- **Issue:** Contains styles for the default Vite template (`.counter`, `.hero`, `#center`, etc.). Not used by the actual application.

### 15.4 Unused `dependency_graph` Field
- **File:** `backend/schemas/report.py:20`, `frontend/src/types/index.ts:47`
- **Issue:** Backend returns `dependency_graph: dict` (serialized NetworkX graph). Frontend type declares it but never uses it. The DependencyGraph component builds its own graph from `impacted_nodes`.

### 15.5 Hardcoded Latency Display
- **File:** `CLISplash.tsx:143`
- **Issue:** Displays "128ms latency" as a static string. Not connected to any real measurement.

### 15.6 Hardcoded Coverage Percentage
- **File:** `Tests.tsx:70`
- **Issue:** Displays "Coverage: +12.4%" as a static string. Not data-driven.

### 15.7 Hardcoded Risk Mitigation Display
- **File:** `Tests.tsx:147`
- **Issue:** Displays `risk_level` under "RISK MITIGATION" label, which is semantically incorrect (risk level is not mitigation).

---

## 16. Risky Patterns

### 16.1 useEffect Navigation as Side Effect
- **Files:** `Dashboard.tsx:15-20`, `Tests.tsx:14-18`, `Report.tsx:14-58`
- **Pattern:** Using `useEffect` to trigger navigation based on state conditions.
- **Risk:** Race conditions, double-render issues, navigation during render.

### 16.2 Error Swallowing in Catch Blocks
- **Files:** `Report.tsx:48-54`, `CLISplash.tsx:30-34`
- **Pattern:** Catching errors, logging to console, then navigating away.
- **Risk:** Errors are invisible; debugging requires console inspection.

### 16.3 Direct Component Import Across Pages
- **File:** `Report.tsx:5`
- **Pattern:** One page component importing another page component directly.
- **Risk:** Tight coupling, unclear ownership, routing bypass.

### 16.4 Zustand Store as Single Source of Truth Without Persistence
- **File:** `store/analysisStore.ts`
- **Pattern:** All application state lives in volatile memory.
- **Risk:** Any page refresh, tab close, or navigation clears everything.

### 16.5 Silent 404 Handling
- **File:** `Report.tsx:48-54`
- **Pattern:** API 404 treated the same as any other error.
- **Risk:** Users cannot distinguish between "report doesn't exist" and "server is down".

### 16.6 Inline `onClick` Navigation in TerminalWindow
- **File:** `TerminalWindow.tsx:143-146`
- **Pattern:** `<a>` element with `onClick` that calls `navigate()` and `preventDefault()`.
- **Risk:** Breaks middle-click/open-in-new-tab; the `href` is wrong port anyway.

---

## 17. Production Readiness Concerns

### 17.1 No Error Boundaries
- **Severity:** HIGH
- **Impact:** Any unhandled React error crashes the entire SPA to a blank screen.

### 17.2 No Analytics or Monitoring
- **Severity:** MEDIUM
- **Impact:** No way to track usage, errors, or performance in production.

### 17.3 No Accessibility Audit
- **Severity:** MEDIUM
- **Impact:** Missing ARIA labels, keyboard navigation, focus management, screen reader support.

### 17.4 No Performance Optimization
- **Severity:** LOW
- **Impact:** No code splitting, no lazy loading, no memoization, no virtualization for lists.

### 17.5 No Security Headers
- **Severity:** MEDIUM
- **Impact:** No CSP, no X-Frame-Options, no other security headers configured in Vite.

### 17.6 Hardcoded Demo Data References
- **Severity:** LOW
- **Impact:** Static strings like "128ms latency", "Coverage: +12.4%", "SCHEMA V2.4.1" suggest production readiness but are fake.

### 17.7 No Build Verification
- **Severity:** MEDIUM
- **Impact:** No CI/CD pipeline, no build tests, no production build verification.

### 17.8 Exposed API Keys in `.env`
- **Severity:** CRITICAL (for repository)
- **File:** `.env`
- **Issue:** GitHub token and OpenRouter API key are committed to the repository in plaintext.
- **Impact:** Credentials are exposed. Must be rotated immediately.

---

## 18. Severity Levels

| Severity | Count | Description |
|---|---|---|
| **CRITICAL** | 2 | System is broken; feature does not work at all |
| **HIGH** | 10 | Major functionality broken or severely degraded |
| **MEDIUM** | 12 | Functionality works but is fragile, misleading, or incomplete |
| **LOW** | 8 | Minor issues, cleanup items, or future concerns |

### Critical Issues
1. **Report ID hash mismatch** — Deep links never work (Section 4.3)
2. **Exposed API credentials** — GitHub token and OpenRouter key in `.env` (Section 17.8)

### High Issues
1. Silent error redirect in Report component (Section 10.1)
2. Dashboard redirect guard race condition (Section 10.2)
3. Tests page redirect guard (Section 10.3)
4. No error boundary (Section 7.1)
5. No report error page (Section 7.3)
6. Zustand store in-memory only (Section 9.1)
7. No store hydration on report route (Section 9.2)
8. No user-facing error messages (Section 12.1)
9. No error state rendering (Section 12.2)
10. Wildcard catch-all masks errors (Section 3.2, R1)

### Medium Issues
1. Report renders Dashboard as component, not route (Section 4.4, F3)
2. Loading state unsynchronized (Section 4.4, F4)
3. API response shape mismatch (Section 8.2)
4. No frontend `.env` (Section 13.1)
5. Vite duplicate React processing (Section 13.2)
6. TopNav logo navigates to home (Section 10.4)
7. RE-ANALYZE clears all state (Section 10.5)
8. TerminalWindow wrong port display (Section 10.6)
9. Error interceptor only logs (Section 11.2)
10. No retry logic (Section 11.3)
11. No shared layout component (Section 14.3)
12. Sidebar dead navigation links (Section 14.4)

### Low Issues
1. No lazy loading (Section 3.2, R4)
2. No Suspense (Section 7.4)
3. No loading skeletons (Section 7.5)
4. CORS docs outdated (Section 8.5)
5. Store setters in useEffect deps (Section 9.4)
6. No request interceptors (Section 11.1)
7. No request cancellation (Section 11.4)
8. Dead App.jsx file (Section 13.4)

---

## 19. Reproduction Steps

### 19.1 Reproduce Primary Bug (Report ID Mismatch)

```bash
# 1. Start backend
python start_backend.py

# 2. Start frontend
cd frontend/prism && npm run dev

# 3. Run CLI analysis
prism demo
# or: prism analyze pr-142 --repo https://github.com/demo/repo

# 4. Note the dashboard URL printed by CLI, e.g.:
#    http://localhost:5173/report/a1b2c3d4

# 5. Open that URL in browser
#    OBSERVED: Brief "Loading report..." then redirect to homepage
#    EXPECTED: Dashboard with analysis results

# 6. Verify in browser console:
#    - Network tab: GET /api/reports/a1b2c3d4 → 404
#    - Console: "Failed to load report:" with 404 error
```

### 19.2 Reproduce Dashboard Refresh Bug

```bash
# 1. Start backend and frontend
# 2. Run analysis through the splash form (not CLI)
# 3. Wait for redirect to /dashboard
# 4. Press F5 to refresh
#    OBSERVED: Redirect to homepage
#    EXPECTED: Dashboard still shows analysis data
```

### 19.3 Reproduce Tests Page Direct Access Bug

```bash
# 1. Start frontend (no analysis run)
# 2. Navigate to http://localhost:5173/dashboard/tests
#    OBSERVED: Redirect to homepage
#    EXPECTED: Tests page with message to run analysis first
```

### 19.4 Reproduce Sidebar Dead Links

```bash
# 1. Run analysis and navigate to dashboard
# 2. Click "SEMANTIC TREE" in sidebar
#    OBSERVED: No change (already on /dashboard)
# 3. Click "RISK ANALYSIS" in sidebar
#    OBSERVED: No change (already on /dashboard)
# 4. Click "LOGS" in sidebar
#    OBSERVED: No change (already on /dashboard)
```

### 19.5 Reproduce TerminalWindow Wrong Port

```bash
# 1. Run analysis through splash form
# 2. Wait for terminal animation to complete
# 3. Observe the displayed URL:
#    OBSERVED: http://localhost:3000/report/{id}
#    ACTUAL: Vite runs on port 5173
#    If user copies this URL, it will not work
```

---

## 20. Recommended Investigation Priority Order

### Phase 1: Blockers (Fix First)
1. **Report ID hash mismatch** — Unify the hash algorithm between CLI endpoint and database repository. This is the root cause of the reported bug.
2. **Exposed API credentials** — Remove `.env` from repository, rotate all exposed keys.

### Phase 2: Critical UX Fixes
3. **Report error handling** — Replace silent redirect with error page showing failure reason and retry option.
4. **Dashboard redirect guard** — Move from component useEffect to route-level guard. Add loading state coordination with Report component.
5. **Zustand persistence** — Add localStorage/sessionStorage persistence for analysis state.

### Phase 3: Navigation & Routing
6. **Replace wildcard redirect** — Add proper 404 page.
7. **Fix TopNav logo** — Navigate to `/dashboard` when on dashboard/report routes.
8. **Fix Sidebar dead links** — Either implement the routes or remove/disable the links.
9. **Fix TerminalWindow port** — Display correct port or use relative URLs.

### Phase 4: Architecture & Resilience
10. **Add error boundaries** — Wrap route tree.
11. **Add shared layout wrapper** — Reduce duplication across Dashboard, Tests, ComingSoon.
12. **Add frontend `.env`** — Proper environment configuration.
13. **Fix Vite config** — Remove duplicate React processing.
14. **Add API retry logic** — Handle transient failures gracefully.

### Phase 5: Cleanup & Polish
15. **Remove dead files** — `App.jsx`, unused `App.css` styles.
16. **Fix type casts** — Remove `as any`, align backend/frontend types.
17. **Remove hardcoded strings** — Replace fake latency, coverage, version displays.
18. **Update documentation** — Fix port references in README.
19. **Add lazy loading** — Code-split routes.
20. **Add accessibility** — ARIA labels, keyboard navigation, focus management.

---

## Appendix A: File Inventory

### Frontend Files Audited
| File | Lines | Issues Found |
|---|---|---|
| `src/App.tsx` | 32 | 5 |
| `src/App.jsx` | 122 | 1 (dead code) |
| `src/main.jsx` | 12 | 0 |
| `src/pages/Report.tsx` | 71 | 6 |
| `src/pages/Dashboard.tsx` | 67 | 4 |
| `src/pages/Tests.tsx` | 171 | 3 |
| `src/pages/CLISplash.tsx` | 150 | 2 |
| `src/pages/ComingSoon.tsx` | 29 | 1 |
| `src/services/api.ts` | 90 | 4 |
| `src/store/analysisStore.ts` | 22 | 3 |
| `src/types/index.ts` | 116 | 3 |
| `src/components/layout/TopNav.tsx` | 74 | 3 |
| `src/components/layout/Sidebar.tsx` | 92 | 2 |
| `src/components/layout/StatsRow.tsx` | 59 | 1 |
| `src/components/dashboard/DependencyGraph.tsx` | 179 | 2 |
| `src/components/dashboard/AIInsightCard.tsx` | 56 | 0 |
| `src/components/dashboard/DetectedRisksCard.tsx` | 82 | 0 |
| `src/components/dashboard/RiskBadge.tsx` | 35 | 0 |
| `src/components/cli/TerminalWindow.tsx` | 172 | 2 |
| `src/components/tests/ScenarioCard.tsx` | 101 | 0 |
| `vite.config.js` | 13 | 1 |
| `index.css` | 80 | 0 |
| `App.css` | 184 | 1 (unused) |
| `FRONTEND_README.md` | 210 | 2 |

### Backend Files Audited (for integration analysis)
| File | Lines | Issues Found |
|---|---|---|
| `backend/api/analysis.py` | 252 | 1 (ID mismatch) |
| `backend/api/reports.py` | 210 | 0 |
| `backend/repositories/report_repository.py` | 234 | 1 (ID mismatch) |
| `backend/analysis.py` | 180 | 1 (ID mismatch) |
| `backend/schemas/report.py` | 68 | 1 (type mismatch) |
| `backend/schemas/analysis.py` | 146 | 0 |
| `backend/config.py` | 55 | 0 |
| `backend/main.py` | 177 | 0 |

---

## Appendix B: Data Flow Diagrams

### Broken Deep-Link Flow
```
CLI ──POST /api/analysis/run──→ Backend
                                   │
                                   ├── make_report_id("pr-142:https://...") → "a1b2c3d4"
                                   │   └── dashboard_url = "http://5173/report/a1b2c3d4"
                                   │
                                   └── repo.create_report()
                                         └── _make_report_id("https://...#pr-142") → "e5f6g7h8"
                                             └── Stored in DB with ID "e5f6g7h8"

User opens "http://5173/report/a1b2c3d4"
  └── Report component
        └── GET /api/reports/a1b2c3d4
              └── Backend: not found (DB has "e5f6g7h8")
                    └── 404 → Report catch → navigate("/") → HOMEPAGE
```

### Correct Flow (After Fix)
```
CLI ──POST /api/analysis/run──→ Backend
                                   │
                                   ├── Unified make_report_id() → "a1b2c3d4"
                                   │   └── dashboard_url = "http://5173/report/a1b2c3d4"
                                   │
                                   └── repo.create_report()
                                         └── Same make_report_id() → "a1b2c3d4"
                                             └── Stored in DB with ID "a1b2c3d4"

User opens "http://5173/report/a1b2c3d4"
  └── Report component
        └── GET /api/reports/a1b2c3d4
              └── Backend: found!
                    └── ReportResponse → convert to AnalyzeResponse → setAnalysis()
                          └── Render Dashboard with data ✓
```

---

*End of audit document. Total issues identified: 32 (2 Critical, 10 High, 12 Medium, 8 Low).*
