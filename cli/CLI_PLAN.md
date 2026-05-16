# PRISM CLI — Detailed Architecture Plan

## Context

PRISM is a hackathon project (24–48h) that adds a semantic risk-analysis layer on top of pull requests. The system has three deliverables: a **CLI**, a **FastAPI backend**, and a **Next.js dashboard**. This plan covers only the **CLI** — the developer-facing entry point.

Per the PRD and TECH_SPECS, the CLI is intentionally thin. Its single job is: accept a PR identifier, call the backend, render a readable summary, and point the user at the dashboard. No analysis logic lives here. The design optimises for **demo reliability and visual impact**, not production robustness.

User-confirmed decisions driving this plan:

- **PR source**: GitHub API via token (CLI passes `pr_identifier` + `repository_url`; backend fetches the diff).
- **Wait UX**: synchronous POST + Rich spinner with stage labels.
- **Extras**: `--open` flag, `prism demo` shortcut, Rich/colored output.
- **Packaging**: `pip install -e .` with a `console_scripts` entry point so the demo command is literally `prism`.

Out of scope here: backend services, dashboard, IBM Bob, Firestore schema (covered elsewhere in TECH_SPECS).

---

## Goals

1. `prism analyze <pr-id>` runs end-to-end in <30s and prints a readable summary + dashboard URL.
2. `prism demo` runs a canned, bulletproof demo against a pre-baked PR — the fallback if the live demo glitches.
3. Output is visually striking on a projector: color-coded risk label, boxed summary, clickable URL.
4. The CLI is independently testable against a mock backend (Track 4 can move in parallel with Track 1).
5. Total CLI code budget: ~300–400 LoC. If it grows beyond that, logic has leaked from the backend.

## Non-Goals

- No local AST analysis, graph construction, or IBM Bob calls in the CLI.
- No authentication beyond passing a GitHub token through to the backend.
- No multi-PR batching, no watch mode, no IDE integration.
- No retries with exponential backoff — one call, one result. If the backend is down, fail loudly.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                       prism (CLI binary)                        │
│                                                                 │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────────┐ │
│  │  main.py │──▶│ config.py│──▶│ client.py│──▶│ formatter.py │ │
│  │  (Typer) │   │ (.env +  │   │ (httpx)  │   │   (rich)     │ │
│  │          │   │  flags)  │   │          │   │              │ │
│  └──────────┘   └──────────┘   └─────┬────┘   └──────┬───────┘ │
│       │                              │               │         │
│       │                              ▼               ▼         │
│       │                   POST /api/analysis/run   stdout      │
│       │                              │                         │
│       │                              ▼                         │
│       │                       FastAPI backend                  │
│       │                              │                         │
│       ▼                              ▼                         │
│  prism demo                  AnalysisResponse JSON             │
│  (alias → analyze            { report_id, dashboard_url,       │
│   on baked demo PR)            risk_score, risk_label,         │
│                                impacted_node_count, status }   │
└─────────────────────────────────────────────────────────────────┘
```

Four files do the real work; three more (`__init__`, `errors`, `demo_fixture`) are tiny supporting modules.

---

## Folder Structure

```
prism/
├── cli/
│   ├── __init__.py          # exposes __version__
│   ├── main.py              # Typer app, commands: analyze, demo, version
│   ├── config.py            # Settings (pydantic-settings) — env + flags
│   ├── client.py            # AnalysisClient — wraps httpx POST to backend
│   ├── formatter.py         # Rich rendering — spinner, summary box, errors
│   ├── errors.py            # Typed CLI exceptions (BackendDown, AuthError, …)
│   └── demo_fixture.py      # Constants for `prism demo` (pr-id, repo URL)
│
├── pyproject.toml           # Package metadata + console_scripts entry point
├── .env.example             # PRISM_BACKEND_URL, PRISM_GITHUB_TOKEN
└── tests/
    ├── test_client.py       # httpx MockTransport — verify request shape
    ├── test_formatter.py    # snapshot tests for summary rendering
    └── test_main.py         # Typer CliRunner — happy path + error paths
```

### File-by-file responsibility

**`cli/main.py`** — Typer app. Three commands:

- `analyze <pr-id>` — primary command, accepts flags.
- `demo` — calls `analyze` with hard-coded fixture values from `demo_fixture.py`.
- `version` — prints `__version__`.

Each command is ~15 lines: parse args → build `Settings` → call `AnalysisClient.run()` → pass result to `formatter.render_summary()`. No logic.

**`cli/config.py`** — `Settings` via `pydantic-settings`. Loads from `.env` then overrides from CLI flags. Fields:

- `backend_url: str` (default `http://localhost:8000`)
- `github_token: str | None`
- `timeout_seconds: int = 60`
- `open_browser: bool = False`
- `output_format: Literal["pretty", "json"] = "pretty"` (json is wired but not advertised — costs ~5 LoC, useful if a judge asks about CI integration)

**`cli/client.py`** — `AnalysisClient`. One method:

```
def run(pr_identifier, repository_url, github_token) -> AnalysisResponse
```

Implementation: `httpx.Client` with the configured timeout, POSTs JSON to `{backend_url}/api/analysis/run`, validates the response against a Pydantic model that mirrors the backend's `AnalysisResponse` schema (`report_id`, `dashboard_url`, `risk_score`, `risk_label`, `impacted_node_count`, `status`). Raises typed errors from `errors.py` on connection failure, 4xx, 5xx, or schema mismatch.

**`cli/formatter.py`** — All Rich rendering lives here. Three public functions:

- `with_progress(stages: list[str]) -> ContextManager` — yields a `rich.progress.Progress` context the client uses to advance through stages (`"Fetching PR diff"`, `"Building dependency graph"`, `"Calling IBM Bob"`, `"Computing risk score"`, `"Generating regressions"`). Stages are _fake_ — they advance on a timer because the backend is one synchronous POST. This is honest demo theatre: each label corresponds to a real backend stage, and the cumulative timer is bounded by the actual response. If we want true progress later, swap to SSE without changing the CLI's public surface.
- `render_summary(response: AnalysisResponse)` — prints the summary panel (see Output spec below).
- `render_error(err: PrismError)` — prints a red boxed error with a one-line cause and a suggested fix.

**`cli/errors.py`** — `PrismError` base + `BackendUnreachable`, `BackendTimeout`, `BackendBadRequest`, `BackendServerError`, `AuthError`. Each carries a user-friendly `.hint` string. `main.py` has one top-level `except PrismError` that routes to `formatter.render_error()` and exits with a non-zero code.

**`cli/demo_fixture.py`** — Pure constants:

```
DEMO_PR_ID = "pr-142"
DEMO_REPO_URL = "https://github.com/prism-demo/payment-service"
```

The backend's analysis pipeline must recognise this PR and return the pre-baked impressive report. (Coordination point with Track 1.)

---

## Command Surface

| Command                                 | Purpose                                                                                                       |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `prism analyze <pr-id>`                 | Primary command.                                                                                              |
| `prism analyze <pr-id> --repo <url>`    | Override repo URL.                                                                                            |
| `prism analyze <pr-id> --open`          | Open dashboard URL in browser after summary.                                                                  |
| `prism analyze <pr-id> --json`          | Emit JSON instead of pretty output (undocumented in `--help` to keep surface clean; ask judges → mention it). |
| `prism analyze <pr-id> --backend <url>` | Override backend URL.                                                                                         |
| `prism analyze <pr-id> --token <tok>`   | Override GitHub token.                                                                                        |
| `prism demo`                            | Canned demo. Implies `--open`.                                                                                |
| `prism version`                         | Print version.                                                                                                |
| `prism --help`                          | Typer-generated help.                                                                                         |

Flag precedence: CLI flag > env var > `.env` > default. Standard.

---

## 1. `prism analyze <pr-id>`

### The mental model

Your "is this PR safe to merge?" button. Type it after creating a PR; get back a risk score and a dashboard link in under 30 seconds.

### Use cases

**1.1 — Daily PR review (the 95% case)**
You just pushed a branch and opened a PR. CI is green, but you're not sure if your enum rename broke downstream consumers.

```
$ prism analyze pr-142
```

You read the risk score. LOW → merge. MEDIUM → click the dashboard link and investigate. HIGH → fix before merging.

**1.2 — Reviewing someone else's PR**
A teammate asks you to review their PR. Instead of manually tracing what their change affects, you run PRISM on their PR ID and get the dependency graph for free.

```
$ prism analyze 287
```

You jump straight to the dashboard, look at the impacted nodes, and leave informed comments instead of "looks good to me."

**1.3 — Pre-merge sanity check on your own PR**
You've gotten approvals, CI is green, you're about to click Merge. One last `prism analyze` to make sure nothing has shifted since you first opened it (someone else might have merged a conflicting change that's now part of your branch's context).

```
$ prism analyze pr-142
```

**1.4 — Re-running after pushing a fix**
PRISM flagged your PR as HIGH risk. You added a backwards-compatibility shim. You push the fix and re-run:

```
$ prism analyze pr-142
```

Risk drops to LOW. You merge with confidence.

**1.5 — Catching a regression CI missed**
Your CI passes because you didn't change any test files. But PRISM finds that your refactor changed the order of side effects in a payment handler — a downstream analytics service depends on that order.

```
$ prism analyze pr-142
# ⚠ 3 semantic risks detected — HIGH (82/100)
```

You investigate before the issue ships.

### What gets sent

```json
POST {backend_url}/api/analysis/run
{
  "pr_identifier": "pr-142",
  "repository_url": "<from .env>",
  "github_token": "<from .env>"
}
```

---

## 2. `prism analyze <pr-id> --repo <url>`

### The mental model

"Temporarily point at a different repo for this one command, without editing my config."

### Use cases

**2.1 — Multi-repo work**
Your `.env` points at `main-backend` (your daily driver). A teammate asks you to review PR #87 in `payment-service`. You don't want to edit your `.env` and remember to switch it back.

```
$ prism analyze pr-87 --repo https://github.com/my-company/payment-service
```

Next time you run `prism analyze pr-142` without the flag, you're back to analyzing `main-backend` automatically.

**2.2 — Reviewing an open-source PR**
You spotted an interesting PR on a third-party repo and want to see what PRISM says about it.

```
$ prism analyze 12453 --repo https://github.com/some-oss/cool-library
```

You weren't going to set up `.env` for this; it's a one-off.

**2.3 — Forks and personal experiments**
You forked a repo to experiment. Your `.env` still points at the upstream. You want to analyze a PR in your fork.

```
$ prism analyze pr-3 --repo https://github.com/your-username/cool-library-fork
```

**2.4 — Demo prep against the canned demo repo**
Your `.env` is configured for your real work. For the hackathon demo you want to hit the prebuilt demo repo without polluting your config.

```
$ prism analyze pr-142 --repo https://github.com/prism-demo/payment-service
```

(Or use `prism demo` — see §7.)

**2.5 — Live demo flex during Q&A**
Judge asks "can it analyze any GitHub repo?" You demonstrate live:

```
$ prism analyze 156 --repo https://github.com/anthropics/anthropic-sdk-python
```

### What gets sent

```json
{
  "pr_identifier": "pr-87",
  "repository_url": "https://github.com/my-company/payment-service",  ← overridden
  "github_token": "<from .env>"
}
```

---

## 3. `prism analyze <pr-id> --open`

### The mental model

"Don't make me copy-paste the dashboard URL — just open it."

### Use cases

**3.1 — Live demo on stage**
You're presenting. You don't want to fumble copying a URL from the terminal into the browser address bar while everyone watches.

```
$ prism analyze pr-142 --open
```

Terminal summary appears → browser launches the dashboard automatically → seamless transition.

**3.2 — Fast investigation flow**
PRISM flagged HIGH risk. You want to dive straight into the graph rather than read the terminal summary in detail.

```
$ prism analyze pr-142 --open
```

You skim the score in the terminal; the dashboard is already open by the time you've read it.

**3.3 — Screencast / video tutorial**
You're recording a how-to. `--open` makes the demo flow on screen feel natural — no awkward "now click this URL" moments.

```
$ prism analyze pr-142 --open
```

**3.4 — Pair programming over screen-share**
You're sharing your screen with a teammate. `--open` saves the "scroll up, find the URL, select it carefully without selecting the spinner output, copy, switch to browser, paste" choreography.

```
$ prism analyze pr-142 --open
```

**3.5 — Combine with `--repo` for multi-repo + auto-open**

```
$ prism analyze pr-87 --repo https://github.com/my-company/payment-service --open
```

Investigate a different repo with zero friction.

### What changes

Same HTTP request as §1. After the summary renders, the CLI calls `webbrowser.open(response.dashboard_url)`.

---

## 4. `prism analyze <pr-id> --json`

### The mental model

"Don't render pretty boxes — give me raw structured data I can pipe into other tools."

### Use cases

**4.1 — CI/CD merge gate**
The classic story. You add PRISM as a CI step that fails the build if risk is HIGH.

```bash
# .github/workflows/prism.yml
- run: |
    score=$(prism analyze ${{ github.event.pull_request.number }} --json | jq -r .risk_score)
    if [ "$score" -gt 67 ]; then
      echo "::error::PRISM HIGH risk ($score). Manual review required."
      exit 1
    fi
```

**4.2 — Slack/Teams bot notifications**
A small script runs `prism analyze --json` on every new PR and posts a formatted message to a Slack channel.

```bash
result=$(prism analyze "$PR_ID" --json)
label=$(echo "$result" | jq -r .risk_label)
url=$(echo "$result" | jq -r .dashboard_url)
slack-post "#engineering" "🔍 PR $PR_ID → $label · $url"
```

**4.3 — Dashboards and analytics**
You want to track average PR risk over time. Run PRISM nightly across recent PRs, save the JSON to a file, feed it into a chart.

```bash
for pr in $(gh pr list --json number -q '.[].number'); do
  prism analyze "$pr" --json >> daily-risk-log.jsonl
done
```

**4.4 — Editor / IDE plugin glue**
Your VS Code extension shells out to `prism analyze --json` and parses the result to show inline diagnostics.

**4.5 — Hackathon judge Q&A**
Judge: "Could this run in CI?" You: type live —

```
$ prism analyze pr-142 --json
{"report_id":"...","risk_score":82,"risk_label":"HIGH",...}
```

"Yes — pipe it through `jq`, fail the build above a threshold. One line."

**4.6 — Programmatic comparison across PRs**
You want to find your team's highest-risk recent PRs:

```bash
gh pr list --limit 50 --json number | jq -r '.[].number' | \
  while read n; do
    prism analyze "$n" --json | jq -r "[$n, .risk_score, .risk_label] | @tsv"
  done | sort -k2 -n -r | head
```

### What changes

- Rich spinner is **suppressed** (output must be pipe-clean).
- Output is raw JSON, no colors, no boxes.
- Errors are emitted as JSON: `{"error": "...", "hint": "..."}`.
- Exit code still 0 on success, 1 on error — scripts can branch on it.

### Why it's hidden from `--help`

Keeps the demo's `--help` surface visually clean. You demonstrate it on demand during Q&A.

---

## 5. `prism analyze <pr-id> --backend <url>`

### The mental model

"Point this run at a different PRISM backend instance."

### Use cases

**5.1 — Hitting a teammate's backend during the hackathon**
Backend dev is running FastAPI on their laptop at `192.168.1.42:8000`. You're on the CLI track and want to test against their machine without editing `.env`.

```
$ prism analyze pr-142 --backend http://192.168.1.42:8000
```

**5.2 — Local dev vs deployed demo**
During development you run FastAPI locally. For the live demo you've deployed to Render. You don't want to constantly rewrite `.env`.

```
# Daily work — hits localhost from .env
$ prism analyze pr-142

# Demo dry run — hits the cloud
$ prism analyze pr-142 --backend https://prism-api.onrender.com
```

**5.3 — Comparing local-fix vs deployed bug**
You suspect a bug exists only in the deployed backend. Run the same PR against both:

```
$ prism analyze pr-142                                          # local
$ prism analyze pr-142 --backend https://prism-api.onrender.com  # deployed
```

Diff the outputs to confirm.

**5.4 — Staging vs production**
You have a staging backend with verbose logging enabled. You want to test there without changing config.

```
$ prism analyze pr-142 --backend https://prism-staging.onrender.com
```

**5.5 — Demo failover**
Your local backend crashed mid-demo. You've also deployed it to Render as a backup. One-line switch:

```
$ prism analyze pr-142 --backend https://prism-api.onrender.com --open
```

**5.6 — Combine with everything else**

```
$ prism analyze pr-87 \
    --repo https://github.com/my-company/payment-service \
    --backend https://prism-api.onrender.com \
    --token ghp_xxx \
    --open
```

Full override per-invocation, nothing touches `.env`.

### What changes

The CLI POSTs to `{url}/api/analysis/run` instead of the default `{PRISM_BACKEND_URL}/api/analysis/run`.

---

## 6. `prism analyze <pr-id> --token <tok>`

### The mental model

"Use this GitHub token instead of the one in my `.env`, just for this run."

### Use cases

**6.1 — Multi-org token juggling**
You have one PAT for your personal repos and another for the company org (different scopes). `.env` has your personal token. Right now you need to analyze a company-internal PR.

```
$ prism analyze pr-287 \
    --repo https://github.com/my-company/internal-service \
    --token ghp_company_xxx
```

**6.2 — Testing a freshly rotated token**
You just regenerated a PAT. Before committing it to `.env`, try it once:

```
$ prism analyze pr-142 --token ghp_brand_new_xxx
```

If it works, then update `.env`.

**6.3 — Diagnosing auth failures**
PRISM is failing with 401 from GitHub. Is the token wrong? Test with a known-good token from another project:

```
$ prism analyze pr-142 --token ghp_known_good_xxx
```

If that succeeds, the issue is in `.env`.

**6.4 — Demo isolation**
You don't want your personal GitHub PAT to live in the demo `.env` that gets passed around the team. Use `--token` only when needed:

```
$ prism analyze pr-142 --token "$MY_PERSONAL_PAT"
```

**6.5 — Bot/service-account tokens for CI**
In CI, the token comes from a secret store, not `.env`:

```bash
- run: prism analyze ${{ github.event.pull_request.number }} \
         --token ${{ secrets.PRISM_GITHUB_TOKEN }} \
         --json
```

**6.6 — Public repos (token omitted entirely)**
For a public repo, you might want to test without a token to confirm the unauthenticated path works (subject to GitHub's lower rate limits):

```
$ prism analyze 123 --repo https://github.com/some/public-repo --token ""
```

### Security caveat

Tokens in command-line args land in your shell history. For routine use, keep tokens in `.env` (which is `.gitignored`). Use `--token` for one-offs only.

### What changes

The `github_token` field of the request body is overridden.

---

## 7. `prism demo`

### The mental model

"The demo parachute." A zero-argument, bulletproof end-to-end run that always works.

### Use cases

**7.1 — Live demo opener**
You walk on stage. First thing you type:

```
$ prism demo
```

Spinner → summary → dashboard auto-opens. Everyone is impressed in under 20 seconds. You haven't even introduced yourself yet.

**7.2 — Demo failover mid-pitch**
You started with `prism analyze pr-142 --open` (the "realistic" flow) and it stalled — IBM Bob is slow, or Wi-Fi flaked. Without missing a beat:

```
$ prism demo
```

Same visual story, different code path under the hood (canned report, sub-second). The audience doesn't know the difference.

**7.3 — Rehearsal**
You're running through your pitch for the fifth time. You don't want to burn GitHub API rate-limit on the demo PR each time.

```
$ prism demo
```

Uses the cached/baked path; no rate-limit risk.

**7.4 — Showing the tool to a non-coding stakeholder**
Your PM/manager wants to see the project. You don't need to explain repos, PRs, tokens.

```
$ prism demo
```

"This runs the full thing on a sample PR."

**7.5 — Smoke test after a code change**
You just refactored the formatter. Does the CLI still work end-to-end?

```
$ prism demo
```

If it opens the dashboard with a HIGH risk panel, you didn't break anything.

**7.6 — Demoing in a hotel room with bad Wi-Fi**
The conference Wi-Fi is down. You're shooting a backup video from your hotel. The canned demo path doesn't need GitHub at all — just the local backend and frontend.

```
$ prism demo
```

### What it actually does

Equivalent to:

```python
analyze(
    pr_id="pr-142",                                              # from demo_fixture.py
    repo="https://github.com/prism-demo/payment-service",        # from demo_fixture.py
    open_browser=True,                                            # --open implied
)
```

The backend recognizes `pr-142` from this specific repo and returns a pre-baked Firestore report instantly — no GitHub fetch, no IBM Bob call, no real AST parsing.

### Composability

`--backend` and `--token` still apply, so you can run the demo against any backend:

```
$ prism demo --backend https://prism-api.onrender.com
```

---

## 8. `prism version`

### The mental model

"Print the version, that's it."

### Use cases

**8.1 — Sanity check after install**
You just ran `pip install -e .`. Did it work?

```
$ prism version
prism 0.1.0
```

✓ Installed correctly.

**8.2 — Confirming the right build is on PATH**
You have two clones of the repo for testing. Which `prism` is currently active?

```
$ prism version
prism 0.1.0
$ which prism
/home/user/prism-dev/.venv/bin/prism
```

**8.3 — Bug reports**
A teammate hits a bug. Step one of your bug template:

```
$ prism version
prism 0.1.0
```

Include it in the issue. Saves an hour of "which version were you on?"

**8.4 — CI build verification**
Your CI pipeline installs PRISM. Confirm it's the version you expect before running tests:

```yaml
- run: prism version
- run: prism analyze pr-${{ github.event.pull_request.number }} --json
```

**8.5 — Hackathon judge sanity-check**
A judge asks "is this a real CLI tool or a stub?"

```
$ prism version
prism 0.1.0
$ prism --help
```

Reassurance that this is a packaged Python tool, not a script demo.

---

## 9. `prism --help`

### The mental model

"What can this CLI do?"

### Use cases

**9.1 — First-time user discovery**
You just installed PRISM. What commands exist?

```
$ prism --help
```

Lists `analyze`, `demo`, `version`.

**9.2 — Subcommand help**
You know `analyze` exists but forgot what flags it takes:

```
$ prism analyze --help
```

Shows `--repo`, `--backend`, `--token`, `--open` with descriptions.

**9.3 — Onboarding a new team member**
"Just install it and run `prism --help`." No documentation page to maintain — Typer generates the help from the code.

**9.4 — Demo: showing surface area**
On stage you mention "the CLI surface is intentionally minimal." Prove it:

```
$ prism --help
```

Three commands. Audience sees focus, not bloat.

**9.5 — Confirming `--json` is hidden**
You designed `--json` to be invisible in `--help`. Verify:

```
$ prism analyze --help
# (no --json listed — exactly as intended)
$ prism analyze pr-142 --json
# (still works)
```

This is part of the "clean surface, hidden power" design story.

---

## Combinations: real workflows that compose multiple flags

The flags compose freely. Here are realistic combinations you'd actually use.

### Workflow A — Live demo, full safety

```
$ prism demo
```

One word. Hardcoded fixture. Auto-opens. Zero failure modes.

### Workflow B — Live demo, "realistic" path with fallback intent

```
$ prism analyze pr-142 --open
```

Uses `.env` repo and token. If it works, looks impressive ("look, real GitHub fetch!"). If it stutters, you fall back to `prism demo`.

### Workflow C — Cross-repo review on a different backend

```
$ prism analyze pr-87 \
    --repo https://github.com/my-company/payment-service \
    --backend https://prism-api.onrender.com \
    --open
```

You're at a conference (deployed backend), reviewing a teammate's PR in a repo that isn't your `.env` default.

### Workflow D — CI gate (the JSON pattern)

```bash
prism analyze "$PR_ID" --json --token "$GITHUB_TOKEN" > result.json
risk=$(jq -r .risk_score result.json)
[ "$risk" -gt 67 ] && exit 1
```

No `--open` (no browser in CI), `--json` for machine reading, `--token` from CI secret.

### Workflow E — Diagnosing a backend regression

```
$ prism analyze pr-142                                          # local backend
$ prism analyze pr-142 --backend https://prism-api.onrender.com # deployed backend
# Compare outputs.
```

### Workflow F — Token rotation safety check

```
$ prism analyze pr-142 --token "$NEW_TOKEN"
# If this succeeds, edit .env to replace the old token.
```

### Workflow G — One-off OSS analysis

```
$ prism analyze 12453 \
    --repo https://github.com/some-oss/cool-library \
    --token "$PUBLIC_REPO_PAT" \
    --open
```

No `.env` setup required for one-shot exploration.

---

## Flag precedence cheat sheet

| Value        | Highest priority     | Then                 | Then        | Default                 |
| ------------ | -------------------- | -------------------- | ----------- | ----------------------- |
| Repo URL     | `--repo`             | `PRISM_REPO_URL` env | `.env` file | Error (must be set)     |
| Backend URL  | `--backend`          | `PRISM_BACKEND_URL`  | `.env` file | `http://localhost:8000` |
| GitHub token | `--token`            | `PRISM_GITHUB_TOKEN` | `.env` file | `None` (unauth GitHub)  |
| Open browser | `--open` (or `demo`) | —                    | —           | Off                     |
| Output mode  | `--json`             | —                    | —           | Pretty (Rich)           |

Rule of thumb: **flags win over env vars; env vars win over file; everything beats defaults.**

## CLI Flow — Detailed Walkthrough

### Phase 1 — Invocation & Config Resolution

```
$ prism analyze pr-142 --open
```

1. Entry point resolves to `cli.main:app` (set in `pyproject.toml`'s `[project.scripts]`).
2. Typer parses `analyze` command, `pr-142` positional, `--open` flag.
3. `main.analyze()` constructs `Settings()`:
   - Loads `.env` from cwd (or `~/.prism/.env` as fallback).
   - Reads `PRISM_BACKEND_URL`, `PRISM_GITHUB_TOKEN`.
   - Applies CLI flag overrides.
4. If `repository_url` is missing, exits with `render_error` showing `Hint: pass --repo or set PRISM_REPO_URL`.

### Phase 2 — Pre-flight

Single check: is `backend_url` reachable? A 200ms `GET /healthz` ping with a 2s timeout. If it fails, render `BackendUnreachable` immediately. **Why pre-flight at all** — the analysis POST can take 25s; failing fast on a wrong URL saves the demo if someone forgot to start the server.

### Phase 3 — Run

5. `formatter.with_progress([...])` enters; spinner begins.
6. `AnalysisClient.run()` POSTs:
   ```json
   {
     "pr_identifier": "pr-142",
     "repository_url": "https://github.com/prism-demo/payment-service",
     "github_token": "ghp_…"
   }
   ```
7. While the request is in flight, the progress context advances stage labels on a timer (e.g. every 4s, capped at the last stage). This keeps the audience visually engaged during the 20–25s wait. The advance is purely cosmetic; the real source of truth is the HTTP response.
8. Response parses into `AnalysisResponse`. Progress context closes.

### Phase 4 — Render

9. `formatter.render_summary(response)` prints:

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  PRISM — Pull Request Intelligent Semantic Monitor          ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  ✓ Pull request analyzed
  ✓ Dependency graph constructed
  ✓ 14 impacted nodes identified
  ⚠ 3 semantic risks detected
  ✓ Regression scenarios generated

  ┌─────────────────────────────────────────┐
  │  Risk Score:  HIGH  (82 / 100)          │   ← red on HIGH
  └─────────────────────────────────────────┘   ← yellow on MEDIUM
                                                ← green on LOW
  Open full analysis:
  ▸ http://localhost:3000/report/8sj2kd
```

Implementation: Rich `Panel`, `Text` with style based on `risk_label`. Status is `PARTIAL` → add a yellow note `"IBM Bob unavailable — graph and score are still valid."` per the PRD's graceful-degradation requirement.

### Phase 5 — Post-render

10. If `--open` (or `prism demo`), call `webbrowser.open(response.dashboard_url)`.
11. Exit code 0 on COMPLETE/PARTIAL, 1 on any `PrismError`, 2 on invalid CLI usage (Typer's default).

---

## Example: End-to-End

**Setup**

```
$ pip install -e .
$ cat .env
PRISM_BACKEND_URL=http://localhost:8000
PRISM_GITHUB_TOKEN=ghp_xxx
PRISM_REPO_URL=https://github.com/prism-demo/payment-service
```

**Live demo invocation**

```
$ prism analyze pr-142 --open
⠋ Fetching PR diff…                       (0.4s)
⠙ Parsing AST                             (1.2s)
⠹ Building dependency graph               (3.8s)
⠸ Traversing impact (2 hops)              (5.1s)
⠼ Calling IBM Bob for semantic reasoning  (14.7s)
⠴ Computing risk score                    (15.0s)
⠦ Generating regression scenarios         (15.4s)
✓ Analysis complete                       (15.6s)

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  PRISM — Pull Request Intelligent Semantic Monitor          ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  ✓ Pull request analyzed
  ✓ Dependency graph constructed
  ✓ 14 impacted nodes identified
  ⚠ 3 semantic risks detected
  ✓ Regression scenarios generated

  ┌─────────────────────────────────────────┐
  │  Risk Score:  HIGH  (82 / 100)          │
  └─────────────────────────────────────────┘

  Open full analysis:
  ▸ http://localhost:3000/report/8sj2kd

(opening in browser…)
```

**Backup demo invocation** (zero-arg, can't fail mid-pitch)

```
$ prism demo
# identical output, but pr_identifier and repo are hardcoded
# in cli/demo_fixture.py and the backend serves a pre-baked report
```

**Error path**

```
$ prism analyze pr-142

  ✗ Cannot reach PRISM backend at http://localhost:8000
    Hint: is the backend running? Try `uvicorn backend.main:app --reload`.

$ echo $?
1
```

---

## Hackathon-Specific Pragmatism

These are deliberate trade-offs that would be wrong in production but right here:

- **Fake stage progression on a timer**: the backend is a single synchronous POST; we don't have real per-stage events. The spinner labels are a UX shim. Honest because each stage corresponds to a real backend phase; replaceable later with SSE.
- **Pre-flight `/healthz`**: backend must expose this. One-line FastAPI route — Track 1 owns it.
- **No retries**: if the call fails, we want to _know_ immediately and rerun. Retries would mask a broken demo.
- **`prism demo` exists**: this is the single most important resilience feature. If GitHub rate-limits us, if IBM Bob is slow, if the network drops — `prism demo` is hardcoded to call the backend with a PR identifier that the backend recognises and returns a baked Firestore report for. Live demos die on flaky networks; this is the parachute.
- **`--json` undocumented but present**: keeps `--help` clean while giving a one-line answer to "could this run in CI?"
- **No CLI-side caching**: every run is fresh. Cache complexity isn't worth it.
- **Token via env var, not OS keychain**: hackathon. Document `.env` in the README and move on.

---

## Things Added Beyond the Spec

| Addition                                    | Why                                                                    |
| ------------------------------------------- | ---------------------------------------------------------------------- |
| `prism demo` command                        | Demo insurance. Hardcoded fixture = guaranteed wow moment.             |
| `--open` flag                               | Saves the presenter from copy-pasting a URL on stage.                  |
| Pre-flight `/healthz` check                 | Fail fast on misconfigured backend (saves debug time during the demo). |
| Typed `PrismError` hierarchy with `.hint`   | One-line actionable error messages on stage.                           |
| `rich.progress.Progress` with staged labels | Turns a 25s blocking wait into a visual story.                         |
| Hidden `--json` mode                        | Free CI-integration answer for judges, ~5 LoC.                         |
| `prism version`                             | Lets judges sanity-check the build. Free.                              |

---

## Dependencies (CLI only)

```
typer >=0.12           # CLI framework
rich  >=13             # spinner + colored output (Typer already ships with it)
httpx >=0.27           # HTTP client with proper timeouts
pydantic >=2           # response validation
pydantic-settings >=2  # .env + env-var loading
```

All five are <2MB combined and Python 3.10+ compatible.

---

## Integration Contract with Backend (Track 1)

Frozen for the CLI; everything else can churn.

**Request** — `POST {backend_url}/api/analysis/run`

```json
{
  "pr_identifier": "string",
  "repository_url": "string",
  "github_token": "string (optional)"
}
```

**Response 200** — `AnalysisResponse`

```json
{
  "report_id": "uuid-string",
  "dashboard_url": "string",
  "risk_score": 0,
  "risk_label": "LOW | MEDIUM | HIGH",
  "impacted_node_count": 0,
  "status": "COMPLETE | PARTIAL"
}
```

**Healthz** — `GET {backend_url}/healthz` → `200 {"ok": true}` (cheap, no DB hit).

**Error responses** — FastAPI default 422 for validation; 500 with `{"detail": "…"}` for pipeline failure. CLI renders `detail` as the error hint.

---

## Verification

Local end-to-end check after implementation:

1. `pip install -e .` in repo root → `prism --help` should list `analyze`, `demo`, `version`.
2. Start the backend skeleton (Track 1 stub returning a canned `AnalysisResponse`).
3. Run `prism analyze pr-142 --repo https://github.com/x/y` → confirm spinner advances, summary box renders, exit code 0.
4. Stop the backend, run again → confirm `BackendUnreachable` error with hint, exit code 1.
5. Run `prism demo --backend http://localhost:8000` → confirm browser opens to dashboard URL.
6. Run `prism analyze pr-142 --json` → confirm machine-readable JSON on stdout, no Rich formatting.
7. Snapshot test in `tests/test_formatter.py` against a captured Rich console — guards against regressions in summary rendering before the demo.
8. `tests/test_client.py` uses `httpx.MockTransport` to assert request body shape matches the contract above.

---

## Critical Files to Create (Implementation Phase)

- `prism/cli/main.py`
- `prism/cli/config.py`
- `prism/cli/client.py`
- `prism/cli/formatter.py`
- `prism/cli/errors.py`
- `prism/cli/demo_fixture.py`
- `prism/cli/__init__.py`
- `prism/pyproject.toml` (entry point: `prism = "cli.main:app"`)
- `prism/.env.example`
- `prism/tests/test_main.py`
- `prism/tests/test_client.py`
- `prism/tests/test_formatter.py`

No existing files to modify — this is a greenfield package.

---

## Suggested Implementation Order

1. `pyproject.toml` + `cli/__init__.py` + skeletal `cli/main.py` → `prism --help` works.
2. `cli/errors.py` + `cli/config.py` → typed errors and settings loading.
3. `cli/client.py` + `cli/formatter.py` → real HTTP call + Rich rendering.
4. `cli/demo_fixture.py` + wire `prism demo` command.
5. `.env.example` + tests in `tests/`.
