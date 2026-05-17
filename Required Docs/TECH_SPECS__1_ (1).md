# TECH_SPECS.md — PRISM: Technical Specifications

---

## 1. Recommended Tech Stack

### Frontend — Next.js + React + TailwindCSS + React Flow

**Why Next.js:** It gives the team a full-featured React framework with file-based routing, API routes if needed, and fast setup. It removes the friction of configuring React manually. For a hackathon, this means the frontend is ready to build features from minute one.

**Why TailwindCSS:** Utility-first CSS eliminates the need to name classes or manage stylesheets. A student team can build a polished UI quickly without context-switching between component logic and style definitions.

**Why React Flow:** The dependency graph visualization is the visual centerpiece of PRISM. React Flow is purpose-built for interactive node-edge diagrams. It handles pan, zoom, node selection, and custom rendering out of the box. Building this from scratch with D3 would consume the entire hackathon.

---

### Backend — Python + FastAPI

**Why Python:** The AST analysis stack (tree-sitter, Python's built-in `ast` module) and the graph library (NetworkX) are all Python-native. Building the backend in Python eliminates the impedance mismatch of calling these tools from another language.

**Why FastAPI:** It is the fastest Python web framework to work with. Automatic request validation, automatic OpenAPI docs, async support, and clean routing make it ideal for a hackathon backend. A student who has never used FastAPI before can be productive within an hour.

---

### Static Analysis — tree-sitter + Python AST

**Why tree-sitter:** tree-sitter produces concrete syntax trees for dozens of languages with a unified API. For TypeScript and JavaScript parsing, it is the most practical choice. It is fast, well-documented, and does not require a language runtime to be installed.

**Why Python AST:** For Python codebases, the standard library `ast` module is sufficient and requires no additional dependencies. It parses Python files into traversable trees.

Together, these two tools cover the primary target languages without requiring a complex analysis toolchain.

---

### Graph Engine — NetworkX

**Why NetworkX:** NetworkX is a Python graph library that handles directed graphs natively. Constructing nodes, adding edges, running traversals, and serializing the graph to JSON are all simple operations. It does not require a running database, a server, or a schema. For a hackathon, this is exactly the right tool.

**Why not Neo4j:** Neo4j is a powerful graph database, but it requires a running server, a connection layer, a query language (Cypher), and non-trivial setup. For the hackathon scope, the dependency graph is constructed per-analysis and does not need to persist in a graph database. NetworkX serialized to JSON in a standard database is sufficient and far simpler.

---

### Database — Firebase (Firestore)

**Why Firestore:** PRISM stores one large report document per analysis run — nested graph data, IBM Bob insights, regression scenarios, warnings, all in one place. This is exactly the document model Firestore is built for. There is no relational structure to normalize, no joins to write, no schema migrations to run. Create a Firebase project, paste the credentials into `.env`, and the database is live. No server to install, no local setup, no connection string debugging.

**Why not PostgreSQL:** PostgreSQL is the right call for relational data with complex queries. PRISM has neither. Every read is a single document fetch by ID. Every write is one document creation. Adding SQLAlchemy, Alembic, and a running Postgres instance for that workload is unnecessary infrastructure under hackathon time pressure.

**Frontend reads Firestore directly:** The Next.js dashboard uses the Firebase client SDK to read the report document straight from Firestore — without going through the backend at all. This eliminates the need to build and maintain the `GET /api/reports/:id` backend endpoint entirely. One less thing to build, one less thing to break during the demo.

**Free tier:** Firebase's Spark plan is free and more than sufficient — 1GB storage, 50k reads/day, 20k writes/day.

**Live debugging bonus:** The Firebase console shows every document being written in real time. During the hackathon this means you can watch reports land in the database the moment the pipeline finishes, without writing a single query.

---

### AI Layer — IBM Bob

IBM Bob is the semantic reasoning engine. It is not a generic LLM call — it receives a structured context payload and is prompted specifically for engineering risk reasoning. The integration is a single HTTP call to the IBM Bob API with a carefully constructed prompt.

---

---

## 2. System Architecture

PRISM is a **modular monolith on the backend** with a **separate Next.js frontend**. There are no microservices. There is one backend process and one frontend process.

### High-Level Architecture

```
Developer Terminal
      │
      ▼
PRISM CLI (Python package)
      │  HTTP POST /api/analysis/run
      ▼
FastAPI Backend
      │
      ├── AST Analyzer
      │       └── Parses changed files
      │
      ├── Graph Builder
      │       └── Constructs NetworkX dependency graph
      │
      ├── Impact Traverser
      │       └── Walks graph, identifies downstream nodes
      │
      ├── IBM Bob Client
      │       └── Sends context, receives semantic reasoning
      │
      ├── Risk Scorer
      │       └── Computes risk score
      │
      ├── Regression Generator
      │       └── Produces test scenarios
      │
      └── Firebase Client
              └── Writes completed report to Firestore
                        │
                        ▼
              Next.js Dashboard
              (reads report directly from Firestore via Firebase SDK)
```

### Request / Data Flow

1. CLI sends `POST /api/analysis/run` with the PR identifier
2. The backend fetches the PR diff from the repository source
3. The AST analyzer parses the changed files and extracts structural elements
4. The graph builder constructs the NetworkX dependency graph around changed nodes
5. The impact traverser walks the graph and returns a list of affected downstream nodes
6. The IBM Bob client assembles a structured prompt and sends it to the IBM Bob API
7. The risk scorer computes a score based on impacted nodes, severity, and change categories
8. The regression generator produces targeted test scenarios based on high-risk graph paths
9. The full analysis result is written to Firestore as a single report document
10. The backend returns the report ID and dashboard URL to the CLI
11. The CLI displays the terminal summary and URL
12. The developer opens the dashboard URL in the browser
13. The Next.js frontend uses the Firebase client SDK to read the report document directly from Firestore — no backend request needed

### Frontend / Backend Interaction

The frontend does not call the FastAPI backend to read reports. It reads directly from Firestore using the Firebase client SDK. The FastAPI backend is only involved in triggering and running the analysis pipeline. This simplifies the backend surface area — there is no report retrieval endpoint to build or maintain.

---

## 3. Folder Structure

```
prism/
├── cli/                        # Python CLI package
│   ├── __init__.py
│   ├── main.py                 # Entry point — parses CLI args, calls backend
│   ├── client.py               # HTTP client — sends requests to FastAPI backend
│   └── formatter.py            # Terminal output formatting
│
├── backend/                    # FastAPI application
│   ├── main.py                 # FastAPI app instantiation, router registration
│   ├── config.py               # Environment variable loading (API keys, DB URL)
│   │
│   ├── api/                    # Route handlers — thin, delegate to services
│   │   ├── analysis.py         # POST /analysis/run
│   │   └── reports.py          # GET /reports/:id
│   │
│   ├── services/               # Core business logic
│   │   ├── analysis_pipeline.py    # Orchestrates the full analysis flow
│   │   ├── ast_analyzer.py         # AST parsing and element extraction
│   │   ├── graph_builder.py        # NetworkX graph construction
│   │   ├── impact_traverser.py     # Graph traversal, downstream node identification
│   │   ├── ibm_bob_client.py       # IBM Bob API integration
│   │   ├── risk_scorer.py          # Risk score computation
│   │   └── regression_generator.py # Regression scenario generation
│   │
│   ├── models/                 # Database models (SQLAlchemy ORM)
│   │   ├── report.py           # Report model — stores full analysis result
│   │   └── base.py             # Base class for ORM models
│   │
│   ├── schemas/                # Pydantic schemas — request/response validation
│   │   ├── analysis.py         # AnalysisRequest, AnalysisResponse schemas
│   │   └── report.py           # ReportDetail schema
│   │
│   ├── repositories/           # Database access layer
│   │   └── report_repository.py    # Save and retrieve reports from DB
│   │
│   ├── utils/                  # Shared utilities
│   │   ├── diff_parser.py      # Parses raw git diff into structured format
│   │   ├── github_client.py    # Fetches PR diff from GitHub API
│   │   └── graph_serializer.py # Converts NetworkX graph to JSON for storage
│   │
│   └── db.py                   # Database session management
│
├── frontend/                   # Next.js application
│   ├── pages/
│   │   ├── index.tsx           # Landing / redirect page
│   │   └── report/
│   │       └── [id].tsx        # Dashboard report page — loads analysis by ID
│   │
│   ├── components/
│   │   ├── RiskSummaryCard.tsx     # Displays score, category, impacted count
│   │   ├── DependencyGraph.tsx     # React Flow graph visualization
│   │   ├── InsightsPanel.tsx       # IBM Bob reasoning text display
│   │   ├── RegressionList.tsx      # List of generated regression scenarios
│   │   └── NodeDetail.tsx          # Sidebar shown when a graph node is selected
│   │
│   ├── services/
│   │   └── api.ts              # API calls to the backend (fetch report by ID)
│   │
│   ├── hooks/
│   │   └── useReport.ts        # Data fetching hook for report loading state
│   │
│   ├── styles/
│   │   └── globals.css         # TailwindCSS base imports
│   │
│   └── public/                 # Static assets
│
├── tests/                      # Backend tests
│   ├── test_ast_analyzer.py
│   ├── test_graph_builder.py
│   ├── test_impact_traverser.py
│   └── test_risk_scorer.py
│
├── .env.example                # Environment variable template
├── requirements.txt            # Python dependencies
├── README.md                   # Setup instructions
└── demo/                       # Demo repository and sample PR data
    ├── sample_repo/            # Pre-structured repo for demo
    └── sample_pr_diff.txt      # Pre-built diff for reliable demo
```

### Folder Responsibilities

**`cli/`** — This is the developer-facing tool. It is intentionally thin. It should not contain analysis logic. Its job is to accept input, call the backend, and display output. If the CLI becomes complex, logic has leaked from the wrong place.

**`backend/api/`** — Route handlers only. Each handler validates the incoming request using a Pydantic schema and delegates immediately to a service. No business logic should live in a route handler. This makes routes easy to read and services easy to test.

**`backend/services/`** — This is where the substance of the application lives. Each service file has one clear responsibility. The `analysis_pipeline.py` file is the orchestrator — it calls the other services in sequence and assembles the result. It does not implement any analysis logic itself.

**`backend/models/`** — Pydantic data models representing the report structure. These are plain Python classes that define the shape of the report object as it flows through the pipeline — not ORM models, since there is no SQL schema to map to. They exist to give the pipeline type safety and make the data contract explicit between services.

**`backend/schemas/`** — Pydantic schemas define the shape of data coming into and going out of the API. They also serve as the contract between the CLI and the backend. Keep them simple and explicit.

**`backend/repositories/`** — Firebase access is isolated here. Services call the repository to read and write Firestore documents. Services never interact with the Firebase SDK directly. This separation means if the database ever changes, only this file needs to update — nothing in the service layer changes.

**`backend/utils/`** — Shared helpers with no business logic of their own. `diff_parser.py` knows how to turn a raw git diff string into a structured list of changed files and lines. `github_client.py` knows how to call the GitHub API to fetch a PR diff. These are utility functions, not services.

**`frontend/pages/`** — Next.js file-based routes. Each page file corresponds to a URL. Pages are thin — they load data and pass it to components. They do not contain rendering logic beyond layout.

**`frontend/components/`** — All visual and interactive elements live here. Components receive props and render UI. They do not fetch data directly (except through hooks). Each component should be independently understandable and independently renderable.

**`frontend/services/`** — Firebase SDK interaction lives here. The `firebase.ts` file initializes the Firebase app and exports the Firestore instance. The `api.ts` file exports async functions that read report documents from Firestore. Components and hooks import from here — they never touch the Firebase SDK directly. If the data access pattern changes, it is fixed in one place.

**`frontend/hooks/`** — React hooks that encapsulate loading state, error state, and data for specific pages. `useReport.ts` handles the lifecycle of fetching and holding a report for the dashboard page.

**`demo/`** — Critical for the hackathon. The demo repository and sample PR are pre-built so the demo is reliable and impressive. Do not rely on a live codebase for the demo presentation.

---

## 4. Backend Structure

### Analysis Pipeline Service

This is the orchestrating service. It is called by the route handler and runs the full analysis sequence:

1. Receives the PR identifier
2. Calls the GitHub client utility to fetch the raw diff
3. Calls the diff parser to structure the diff
4. Calls the AST analyzer with the list of changed files
5. Calls the graph builder with the extracted elements
6. Calls the impact traverser with the graph
7. Calls the IBM Bob client with the assembled context
8. Calls the risk scorer with the traversal results and IBM Bob output
9. Calls the regression generator with the high-risk paths
10. Assembles the full report object
11. Calls the report repository to save the report
12. Returns the report ID and dashboard URL

The pipeline service should not implement any of these steps itself — it delegates to the appropriate service and assembles results.

### AST Analyzer Service

Accepts a list of changed file paths and their contents. For each file, it determines the language (Python, TypeScript, JavaScript) and routes to the appropriate parser. It extracts:

- Function definitions and their names
- Import statements and what they import
- Exported symbols
- API route definitions (for web frameworks)
- Event emission calls
- Database model references

The output is a structured list of extracted elements per file.

### Graph Builder Service

Accepts the list of extracted elements. Constructs a directed NetworkX graph where:

- Each node represents a meaningful element: a function, a service, an API, an event, a model
- Each edge represents a relationship: imports, calls, emits, consumes

For the hackathon, the graph is built from the extracted elements of the changed files and their direct neighbors. The builder may also read a pre-indexed graph snapshot if available (stored from a prior full-repository analysis).

### Impact Traverser Service

Accepts the graph and the set of directly changed nodes. Performs a breadth-first traversal outward from changed nodes following dependency edges. Returns:

- The list of all reachable downstream nodes within a configurable depth
- The traversal paths (chains of dependencies)
- Nodes classified by how many hops removed they are from the change

### IBM Bob Client Service

Accepts the structured context: the diff summary, the list of impacted nodes, the traversal paths, and relevant surrounding code snippets. Assembles a carefully constructed prompt. Calls the IBM Bob API. Parses the response into structured fields:

- Semantic risk narrative
- List of specific warnings per impacted system
- Architectural impact summary
- Regression reasoning

If the call fails, the client returns a partial result with an error flag rather than raising an exception that would kill the pipeline.

### Risk Scorer Service

Computes a numeric score (0–100) based on:

- Number of downstream nodes impacted
- Categories of impacted systems (payments and auth are higher risk than analytics)
- Presence of specific high-risk change patterns (enum changes, permission logic, API contracts)
- IBM Bob's risk classification if available

Assigns a categorical label: LOW (0–33), MEDIUM (34–66), HIGH (67–100).

### Regression Generator Service

Accepts the high-risk impacted paths from the traverser. For each high-risk path, generates a structured test scenario description covering:

- The specific behavioral assumption that may be violated
- The system or component that should be tested
- The input condition and expected output
- The edge case most likely to reveal the regression

The output is a list of structured test scenario objects, not executable test code.

### Firebase Repository

Handles all Firestore reads and writes for reports. Uses the `firebase-admin` SDK on the backend. Exposes:

- `save_report(report_data)` — serializes the full report object and writes it as a single Firestore document in the `reports` collection, keyed by the report UUID
- `get_report(report_id)` — retrieves a report document by ID (used by the status endpoint if needed)

The graph data is serialized to a plain dict using the graph serializer utility before being passed here. Firestore stores nested objects natively, so no further transformation is needed. The frontend reads the same document directly via the Firebase client SDK — the document structure on write must match what the frontend expects to read.

### Auth Flow

For the hackathon: no authentication. The API is open. Reports are accessed by UUID-based report IDs which are effectively unguessable. This is sufficient for a demo environment.

---

## 5. Frontend Structure

### Pages

**`pages/report/[id].tsx`** — The core page. It reads the report ID from the URL, uses the `useReport` hook to load the report from the backend, and renders the four main panels: RiskSummaryCard, DependencyGraph, InsightsPanel, and RegressionList. It handles loading and error states cleanly.

**`pages/index.tsx`** — A minimal landing page. Can redirect to a demo report or display a brief product description. Not critical for the hackathon but useful as a URL entry point.

### Components

**`RiskSummaryCard`** — Displays the risk score (large number), the categorical label (color-coded: green/yellow/red), the count of impacted nodes, and the list of impacted service names. This is the first thing a developer sees and should communicate the severity immediately.

**`DependencyGraph`** — The visual centerpiece. Uses React Flow to render the dependency graph stored in the report. Nodes are color-coded by type (service, event, API, model) and by impact status (changed, directly impacted, indirectly impacted). Edges show dependency direction. Clicking a node opens the NodeDetail sidebar. The graph is the primary interactive element of the dashboard.

**`NodeDetail`** — A sidebar or panel that appears when a graph node is selected. Shows the node's name, type, the IBM Bob warning associated with it (if any), and which regression scenarios relate to it.

**`InsightsPanel`** — Displays IBM Bob's semantic narrative in readable prose. Structured with the overall architectural impact summary at the top, followed by per-system warnings. Text is formatted for readability, not as raw JSON.

**`RegressionList`** — A list of generated regression scenarios. Each item shows the affected system, the behavioral assumption at risk, and the suggested test description. Items are copyable for developer convenience.

### Hooks

**`useReport`** — Fetches the report document directly from Firestore using the Firebase client SDK and the report ID from the URL. Manages three states: loading, data, and error. Returns these to the page component so the page can render appropriate UI for each state. No backend HTTP call is made — the hook talks to Firestore directly.

### State Management

No global state management library is needed (no Redux, no Zustand). Each page manages its own local state through hooks. The only state that needs to be shared between components is the selected graph node — this is passed as props from the page to `DependencyGraph` and `NodeDetail`.

### Firebase Integration

The Firebase client SDK is initialized once in `services/firebase.ts` and the Firestore instance is exported from there. All Firestore reads go through `services/api.ts`, which imports the Firestore instance and exports typed async functions for fetching reports. Components and hooks never import from the Firebase SDK directly — they always go through `services/api.ts`. This keeps Firebase as an implementation detail that can be changed in one file if needed.

---

## 6. Database Design

PRISM uses Firebase Firestore as its database. There is one collection: `reports`. Each document in that collection represents one complete analysis run, identified by a UUID that is also used in the dashboard URL.

### Collection: `reports`

**Identity and context fields:**

- `id` — UUID string, used as the Firestore document ID and in the dashboard URL (`/report/:id`). A UUID is used instead of an auto-increment integer so report IDs are unguessable — there is no way to enumerate or predict others.
- `pr_identifier` — the PR number or branch name passed to the CLI. Displayed on the dashboard header.
- `repository_url` — the GitHub repository URL. Stored so the dashboard can link back to the source.
- `created_at` — ISO timestamp of when the analysis was triggered. Used for display and future report history features.

**Risk output fields:**

- `risk_score` — integer between 0 and 100. The single number summarizing merge confidence. Displayed prominently on the dashboard summary card.
- `risk_label` — string: `LOW`, `MEDIUM`, or `HIGH`. Derived from the risk score (0–33 = LOW, 34–66 = MEDIUM, 67–100 = HIGH). Stored separately so the dashboard applies color coding without recalculating.
- `impacted_node_count` — integer count of downstream nodes identified by the traversal. Stored as a flat field so the summary card can display it without parsing the full graph.

**Heavy payload fields:**

- `graph_data` — the full dependency graph serialized as a nested object, pre-formatted for React Flow. Contains a `nodes` array (each node has an `id`, `type`, `label`, `position`, and `impactStatus` flag) and an `edges` array (each edge has `source`, `target`, and `relationship` type). Written once, read once. Never queried — always fetched whole.
- `ibm_bob_narrative` — plain text string of IBM Bob's overall architectural impact summary. Shown as the prose paragraph in the Insights Panel.
- `ibm_bob_warnings` — array of objects, one per flagged downstream node. Each object contains the node name, the specific assumption at risk, and IBM Bob's explanation. Rendered as the per-system warning list in the Insights Panel.
- `regression_scenarios` — array of objects, one per generated test scenario. Each contains the affected system name, the behavioral assumption being tested, and the suggested test description. Rendered in the Regression Scenario Explorer.
- `changed_files` — array of file path strings from the PR diff. Used to populate the changed files list on the summary card.

**Pipeline state field:**

- `status` — string: `PENDING`, `COMPLETE`, or `PARTIAL`. Written as `PENDING` the moment the pipeline starts. Flipped to `COMPLETE` when everything succeeds. Set to `PARTIAL` if IBM Bob fails but the graph and risk score were computed — the dashboard handles `PARTIAL` gracefully by showing graph and score with a note that semantic insights are unavailable.

### Why One Document Per Report

Firestore is a document database. A PRISM report is written once and read once — there are no joins, no cross-document queries, no relational structure needed. One document ID, one Firestore read, and the dashboard has everything it needs. There is no collection for warnings, no subcollection for scenarios, no reference to resolve.

### Future Extension

If a repository index feature is added later, a second collection `repository_indexes` can store pre-indexed dependency graphs keyed by repository URL. Nothing about the `reports` collection changes.

---

## 7. API Structure

### Endpoint Organization

With the frontend reading Firestore directly, the FastAPI backend has a minimal API surface. It handles one thing: triggering the analysis pipeline.

**`/api/analysis`** — Analysis lifecycle

- `POST /api/analysis/run` — Accepts a PR identifier, runs the full synchronous pipeline, writes the completed report to Firestore, and returns the report ID and dashboard URL

There is no report retrieval endpoint. The dashboard reads the report from Firestore directly using the Firebase client SDK.

### Request Structure

`POST /api/analysis/run`

The request body contains:

- `pr_identifier` — string, the PR ID or branch name
- `repository_url` — string, the GitHub repository URL
- `github_token` (optional) — string, for private repository access

### Response Structure

`POST /api/analysis/run` returns after the pipeline completes:

- `report_id` — UUID string matching the Firestore document ID
- `dashboard_url` — the full URL the developer opens to view the analysis
- `risk_score` — integer, for immediate CLI display without a Firestore read
- `risk_label` — string, for immediate CLI display
- `impacted_node_count` — integer, for immediate CLI display
- `status` — `COMPLETE` or `PARTIAL`

### Authentication

No authentication for the hackathon. The API is open. Report IDs are UUIDs — guessing a valid ID is computationally infeasible for demo purposes.

### Validation Flow

FastAPI uses Pydantic schemas for automatic request validation. If a required field is missing or the wrong type, FastAPI returns a 422 response with a clear error message. No manual validation code is needed. Define the schemas carefully — they are the API contract.

---

## 8. Deployment Strategy

### Local Development (Primary for Hackathon)

Two things run locally:

- FastAPI backend on port 8000
- Next.js frontend on port 3000

Firestore is always the real Firebase project — there is no local database file or server to run. This means an internet connection is needed during development, which is never a problem in practice. The Firebase console gives a live view of every document being written, which is extremely useful for debugging during the hackathon.

### Cloud Deployment (If Time Allows)

- **Backend:** Deploy to Render or Railway — both support Python/FastAPI with a `requirements.txt` and a start command. Free tier is sufficient.
- **Database:** Nothing to deploy — Firestore is already live in Firebase.
- **Frontend:** Deploy to Vercel — connect the GitHub repository, set the Firebase config environment variables and the backend URL, and it deploys automatically on push.

This is a two-service deployment (FastAPI backend + Vercel frontend) that can be done in under 30 minutes once the code is working locally.

### Environment Variables

All sensitive values go in a `.env` file that is never committed. An `.env.example` file documents what is needed:

Backend:
- `OPENROUTER_API_KEY`
- `GITHUB_TOKEN` (optional, for private repos)
- `BACKEND_URL`
- `FIREBASE_PROJECT_ID`
- `FIREBASE_PRIVATE_KEY`
- `FIREBASE_CLIENT_EMAIL`

Frontend:
- `NEXT_PUBLIC_FIREBASE_API_KEY`
- `NEXT_PUBLIC_FIREBASE_PROJECT_ID`
- `NEXT_PUBLIC_FIREBASE_APP_ID`
- `NEXT_PUBLIC_BACKEND_URL`

---

## 9. Development Workflow

### Team Structure and Task Distribution

The project splits naturally into four tracks that can be developed largely in parallel:

**Track 1 — Backend Core (1–2 developers)**
Responsibility: FastAPI setup, Firebase client, analysis pipeline, AST analyzer, graph builder, impact traverser, risk scorer.

This is the most logic-dense track and should be started first. Get the pipeline running end-to-end with mock IBM Bob responses before integrating the real API. Use the Firebase console to verify documents are being written correctly as you go.

**Track 2 — IBM Bob Integration (1 developer)**
Responsibility: IBM Bob client, prompt engineering, response parsing, regression generator.

This track can work against the pipeline's expected interface from the start — the IBM Bob client has a defined input (structured context) and output (semantic insights). Stub the client to return sample data while the API details are worked out.

**Track 3 — Frontend and Dashboard (1–2 developers)**
Responsibility: Next.js setup, Firebase client SDK integration, React Flow graph component, all dashboard components.

Start with hardcoded report data (a local JSON fixture) so the dashboard can be built and styled before the backend is complete. Wire the real Firestore reads in at the end — the data shape is identical, only the source changes.

**Track 4 — CLI (1 developer)**
Responsibility: Python CLI package, terminal formatting, backend HTTP client.

This is the simplest track. The CLI is a thin wrapper around an HTTP call. Once the backend API contract is agreed on, this can be built and tested against the backend independently.

### Branch Strategy

- `main` — production-ready, always demo-able
- `dev` — integration branch where features are merged
- Feature branches off `dev` — named by feature: `feat/ast-analyzer`, `feat/graph-builder`, `feat/dashboard-graph`

Merge to `dev` frequently. Merge `dev` to `main` only when the full integration is tested.

### Development Order

1. Define the API contract (request/response schemas) — agree before writing code
2. Build the FastAPI skeleton with empty routes returning mock data
3. Build the frontend against mock data
4. Build the CLI against the mock backend
5. Implement the analysis pipeline services one by one, replacing mock data with real results
6. Integrate IBM Bob — first with a stub, then with the real API
7. Wire everything together, test the full flow end-to-end
8. Build and validate the demo scenario
9. Polish the dashboard UI

### Integration Flow

The integration point between all tracks is the Firestore document structure — specifically the shape of the report document that the backend writes and the frontend reads. Agree on this schema first. Every track builds to this contract:

- Backend writes a Firestore document that matches it
- Frontend reads a Firestore document that matches it
- CLI displays a summary derived from the fields returned by the analysis endpoint

As long as the document shape is respected, tracks can be developed and tested independently.

### Demo Preparation

The demo must be practiced. The demo PR (in `demo/sample_repo/`) is pre-built to produce a specific, impressive graph. Run the full flow at least three times before presenting. Have a recorded backup in case of network issues or API failures during the live demo.

The demo narrative should be:

1. Show the PR on screen
2. Show CI passing
3. Run `prism analyze`
4. Show the terminal output
5. Open the dashboard
6. Walk the graph — point out the highlighted risk path
7. Read one IBM Bob insight aloud
8. Show one regression scenario
9. Conclude: "PRISM found what CI missed."
