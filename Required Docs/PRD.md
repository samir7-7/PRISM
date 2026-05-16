# PRD.md — PRISM: Pull Request Intelligent Semantic Monitor

---

## 1. Project Overview

### What the Product Does

PRISM is a semantic risk analysis layer that sits on top of the existing pull request workflow. When a developer submits a pull request, PRISM analyzes not just the changed code but also its relationships to the surrounding codebase — tracing how the change propagates through downstream services, APIs, events, and assumptions.

It delivers a risk score, a list of impacted system components, IBM Bob-powered semantic insights, and generated regression scenarios — surfaced through a CLI summary and an interactive visual dashboard.

### Problem Being Solved

Modern CI/CD pipelines are syntactic validators. They confirm that code compiles, tests pass, and no merge conflict exists. But they are blind to semantic risk: the hidden behavioral inconsistencies that arise when a small, syntactically valid change breaks a downstream assumption.

Examples of silent semantic failures:

- A status enum changes from `PENDING` to `PROCESSING`, but analytics pipelines still expect `PENDING`
- An API response field is renamed, but three downstream consumers still reference the old name
- A permission check is refactored in a way that alters behavior only under a specific state transition sequence

These changes pass every CI check. They fail in production.

PRISM introduces a contextual reasoning layer that answers the question traditional CI cannot: *Should this code merge?*

### Why It Matters

The cost of a production regression is significantly higher than the cost of catching it at review time. Current tooling forces developers to manually trace dependencies, understand execution graphs, and reason about downstream assumptions — a slow, error-prone, expert-dependent process.

PRISM automates this reasoning, making every developer capable of understanding the full impact radius of their change before merging.

### Target Users

- Software developers at companies with interconnected service architectures
- Tech leads and senior engineers who review pull requests
- Platform/DevOps teams maintaining CI/CD pipeline quality
- Hackathon demo audience: engineering organizations interested in intelligent developer tooling

### Core Value Proposition

PRISM reduces the gap between "CI passed" and "safe to merge" by injecting contextual semantic intelligence directly into the pull request workflow — powered by dependency graph traversal and IBM Bob reasoning.

---

## 2. Hackathon Context

### Why This Project Is Suitable for a Hackathon

PRISM is scoped correctly for a hackathon. The core MVP requires:

- A CLI that takes a PR identifier and outputs a structured risk summary
- A backend that performs AST analysis, constructs a dependency graph, and calls IBM Bob
- A visual dashboard that renders the graph and insights

Each of these pieces is independently demoable. If the graph isn't perfect, the demo still shows the concept. If regression generation is basic, the dashboard still communicates the vision clearly.

### Demo Potential

The demo follows a clear, dramatic narrative:

1. Developer opens a PR that changes a status enum
2. Traditional CI shows: `✓ Build Passed, ✓ Tests Passed`
3. Developer runs `prism analyze pr-142`
4. PRISM reports: `⚠ 3 semantic risks detected, Risk Score: HIGH (82/100)`
5. Developer opens the dashboard
6. The graph lights up: `PaymentService → PaymentProcessedEvent → AnalyticsService ⚠ EXPECTS PENDING`
7. IBM Bob explains the risk in natural language
8. Regression scenarios are shown

This is a compelling, understandable, technically impressive demo that communicates value immediately.

### Innovation Angle

PRISM is not a chatbot. It is not a code review assistant. It is a structurally novel tool that combines:

- Static AST analysis
- Graph-based impact traversal
- Large language model reasoning (IBM Bob)
- Interactive visual communication

The combination of these layers into a practical developer workflow tool is the innovation.

### Practical Impact

Real engineering teams spend significant time in PR review trying to understand downstream impact manually. PRISM makes this automatic, visual, and reasoned. It reduces review time, improves merge confidence, and catches production issues before they happen.

---

## 3. Core Features

### MVP Features

These are the features that must be built and working for the hackathon demo:

- **CLI command:** `prism analyze <pr-id>` — triggers the full analysis pipeline
- **PR diff extraction:** fetches and parses the raw code changes from the PR
- **AST analysis:** extracts function calls, imports, API references, events, and models from changed files
- **Dependency graph construction:** builds a local graph of relationships between the changed nodes and their neighbors
- **Impact traversal:** walks the graph to identify downstream affected nodes
- **IBM Bob integration:** sends structured context to IBM Bob and receives semantic risk reasoning
- **Risk scoring:** produces a simple numeric risk score with a categorical label (LOW / MEDIUM / HIGH)
- **Regression scenario generation:** generates targeted test scenarios based on impacted graph paths
- **CLI summary output:** displays a readable summary with risk score and dashboard link
- **Interactive dashboard:** visualizes the dependency graph, risk summary, IBM Bob insights, and regression scenarios

### Stretch Goals

Features worth building if time allows:

- GitHub/GitLab webhook integration so `prism analyze` runs automatically on PR creation
- Support for multiple repository languages (Python, TypeScript, Go)
- Persistent analysis history so developers can compare risk across PR revisions
- Team-level risk analytics aggregated over time

### Future Improvements (Lightweight)

Ideas for post-hackathon iteration:

- IDE plugin that surfaces PRISM insights inline in the code editor
- Slack/Teams notification integration that delivers risk summaries to team channels
- Custom risk rule configuration per repository

---

## 4. User Flow

### Entry Point

The developer creates a pull request in their repository as they normally would. PRISM does not modify this workflow. After creating the PR, the developer runs a single CLI command from the terminal.

### Step 1 — CLI Invocation

The developer executes:

```
prism analyze <pr-id>
```

The CLI authenticates with the PRISM backend (if configured) and submits the PR identifier for analysis.

### Step 2 — Backend Analysis Pipeline

The PRISM backend performs the following steps in sequence:

1. Fetches the PR diff from the repository source (GitHub API or local git)
2. Parses changed files through AST analysis to extract structural elements: functions, imports, API calls, event emissions, model references
3. Constructs a dependency graph around the changed elements using pre-indexed repository knowledge or on-demand traversal
4. Traverses the graph outward to identify downstream nodes — services, handlers, consumers — that depend on the changed components
5. Assembles a structured context payload: diff, impacted graph, surrounding code summaries
6. Sends the context to IBM Bob with a semantic reasoning prompt
7. Receives IBM Bob's analysis: risk narrative, downstream warnings, architectural interpretation
8. Generates targeted regression scenarios based on the highest-risk graph paths
9. Computes a risk score
10. Stores the result and generates a unique dashboard URL

### Step 3 — CLI Output

The terminal displays a compact, readable summary:

```
✓ Pull request analyzed
✓ Dependency graph constructed
✓ 14 impacted nodes identified
⚠ 3 semantic risks detected
✓ Regression scenarios generated

Risk Score: HIGH (82/100)

Open full analysis:
http://localhost:3000/report/8sj2kd
```

### Step 4 — Dashboard Investigation

The developer opens the URL in the browser. The dashboard loads the full analysis for this report.

The developer can:

- View the risk summary card: score, impacted service count, risk category
- Explore the interactive dependency graph — pan, zoom, click on nodes to inspect relationships
- Read IBM Bob's semantic narrative in the insights panel
- Browse generated regression scenarios and copy them for implementation
- Understand which specific downstream systems are at risk and why

### Step 5 — Decision and Merge

Armed with PRISM's analysis, the developer makes an informed merge decision:

- If risk is LOW: merge with confidence
- If risk is MEDIUM: review the specific impacted paths before merging
- If risk is HIGH: investigate the flagged downstream systems, validate or update them, and re-run analysis

---

## 5. User Stories

**As a developer**, I want to run a single command after creating a PR so that I can understand its downstream impact without manually tracing dependencies.

**As a developer**, I want to see a visual graph of which systems are affected by my change so that I can quickly understand the impact radius.

**As a developer**, I want IBM Bob to explain semantic risks in plain language so that I can understand *why* a change is risky, not just *that* it is risky.

**As a developer**, I want PRISM to generate targeted regression scenarios so that I know which tests to write or run to validate my change.

**As a tech lead**, I want a risk score that summarizes the overall merge confidence so that I can prioritize review effort across multiple PRs.

**As a developer**, I want the CLI output to be fast and readable so that PRISM fits naturally into my existing workflow without adding friction.

---

## 6. Functional Requirements

### Analysis Pipeline

- The system must accept a PR identifier and extract the corresponding diff
- The system must parse changed files through AST analysis and extract: function definitions, function calls, imports, API route references, event names, model references
- The system must construct a dependency graph connecting changed nodes to their known dependents
- The system must traverse the graph to at least two hops of depth to capture indirect impacts
- The system must assemble a structured context payload and submit it to IBM Bob
- The system must parse IBM Bob's response and extract structured insights
- The system must generate at least three targeted regression scenarios per high-risk path
- The system must compute a risk score between 0 and 100 and assign a categorical label

### CLI

- The CLI must accept `prism analyze <pr-id>` as a minimum viable command
- The CLI must display a structured terminal summary after analysis completes
- The CLI must output a valid URL pointing to the dashboard report

### Dashboard

- The dashboard must load a specific analysis report by its unique identifier
- The dashboard must render an interactive dependency graph using the stored graph data
- The dashboard must display the risk summary (score, category, impacted node count)
- The dashboard must display IBM Bob's semantic insights as readable text
- The dashboard must display the list of generated regression scenarios

### Edge Cases

- If the PR diff is empty or contains only non-code changes (documentation, config), the system should return a LOW risk score with a note explaining no structural changes were detected
- If IBM Bob returns an error or timeout, the system should return the graph and risk score without semantic insights, noting the partial result
- If a PR modifies files in a part of the repository with no pre-indexed graph data, the system should perform on-demand AST traversal and flag that coverage may be incomplete

---

## 7. Non-Functional Requirements

### Performance

- CLI response time from command invocation to summary output: under 30 seconds for a typical PR with fewer than 20 changed files
- Dashboard load time: under 3 seconds after the analysis report is stored

### Usability

- CLI output must be readable without documentation — a developer seeing it for the first time should understand the summary immediately
- Dashboard must be navigable without a tutorial — graph interaction should follow standard pan/zoom conventions
- IBM Bob insights must be written in plain engineering language, not academic jargon

### Reliability

- The analysis pipeline must return a result (even partial) rather than a silent failure for any valid PR identifier
- Failed IBM Bob calls must degrade gracefully — the system returns graph data and a note rather than an error

### Scalability

- For hackathon scope: the system needs to handle one analysis at a time reliably
- Architecture should not block scaling to concurrent analyses later, but this is not a current requirement

### Maintainability

- Code should be organized by feature responsibility, not by technical layer alone
- Each module should have a single clear purpose readable from its name
- No module should import from more than two other modules to prevent tight coupling

---

## 8. Constraints and Assumptions

### Hackathon Time Constraints

- The project has roughly 24–48 hours of build time
- The MVP should be achievable in 16–20 hours, leaving time for polish and demo preparation
- Stretch goals should only be started after the MVP is fully demo-ready

### Student Team Limitations

- Team members may have varying familiarity with AST analysis and graph libraries
- IBM Bob API integration should be assigned to a single owner to avoid merge conflicts
- The dashboard and backend should be developed in parallel by separate team members

### Realistic Implementation Boundaries

- The dependency graph does not need to be a complete, repository-wide analysis for the hackathon — a localized graph around changed files is sufficient for a convincing demo
- Regression scenario generation produces structured test descriptions, not necessarily executable test files, for the hackathon scope
- The system targets TypeScript/JavaScript and Python codebases as primary languages for AST analysis; other languages are out of scope for now
- Authentication and multi-user support are out of scope for the hackathon

### Assumptions

- IBM Bob API access is available and stable during the hackathon
- The demo repository (used for the demo PR) is pre-indexed or pre-structured to make graph traversal deterministic and impressive
- The team will prepare a specific demo PR in a controlled repository to ensure the demo narrative is reliable
