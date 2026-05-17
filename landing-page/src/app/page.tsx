export default function Home() {
  return (
    <main className="min-h-screen bg-prism-bg text-prism-text">
      <div className="mx-auto flex min-h-screen w-full max-w-6xl flex-col justify-between px-6 py-8 md:px-10">
        <header className="flex items-center justify-between">
          <div className="font-mono text-sm tracking-[0.2em] text-prism-text-muted">
            PRISM
          </div>
          <a
            href="#launch"
            className="rounded-md border border-prism-border bg-prism-surface px-4 py-2 text-xs font-semibold uppercase tracking-[0.14em] text-prism-text transition hover:border-prism-blue hover:text-prism-blue"
          >
            Launch
          </a>
        </header>

        <section className="grid items-center gap-10 py-12 md:grid-cols-2 md:gap-16">
          <div>
            <p className="mb-4 font-mono text-xs uppercase tracking-[0.2em] text-prism-blue">
              Pull Request Intelligence
            </p>
            <h1 className="mb-6 text-5xl font-bold leading-tight tracking-tight md:text-6xl">
              Catch semantic failures before merge.
            </h1>
            <p className="max-w-xl text-base text-prism-text-muted md:text-lg">
              PRISM analyzes dependency propagation and behavior-level risk so
              your team can detect silent breakages before they hit production.
            </p>
            <div className="mt-8 flex flex-wrap gap-4">
              <a
                id="launch"
                href="#"
                className="rounded-md bg-prism-blue px-5 py-3 text-sm font-semibold text-white transition hover:opacity-90"
              >
                Analyze Pull Request
              </a>
              <a
                href="#"
                className="rounded-md border border-prism-border bg-prism-surface px-5 py-3 text-sm font-semibold text-prism-text transition hover:border-prism-blue"
              >
                View Dashboard
              </a>
            </div>
          </div>

          <div className="rounded-xl border border-prism-border bg-prism-surface p-5 shadow-[0_0_0_1px_rgba(255,255,255,0.02)]">
            <div className="mb-4 flex items-center gap-2">
              <span className="h-2.5 w-2.5 rounded-full bg-prism-red" />
              <span className="h-2.5 w-2.5 rounded-full bg-prism-yellow" />
              <span className="h-2.5 w-2.5 rounded-full bg-prism-green" />
            </div>
            <div className="space-y-2 font-mono text-xs text-prism-text-muted">
              <p>&gt; prism analyze pr-142 --repo owner/repo</p>
              <p className="text-prism-blue">✓ Analysis complete</p>
              <p>Risk Score: 65 (MEDIUM)</p>
              <p>Impacted Nodes: 8</p>
              <p className="text-prism-green">All systems nominal · 128ms</p>
            </div>
          </div>
        </section>

        <section className="grid gap-4 pb-8 md:grid-cols-3">
          <article className="rounded-lg border border-prism-border bg-prism-surface p-5">
            <p className="text-3xl font-semibold">0-100</p>
            <p className="mt-2 text-sm text-prism-text-muted">Risk scoring</p>
          </article>
          <article className="rounded-lg border border-prism-border bg-prism-surface p-5">
            <p className="text-3xl font-semibold">AST + Graph</p>
            <p className="mt-2 text-sm text-prism-text-muted">
              Semantic impact engine
            </p>
          </article>
          <article className="rounded-lg border border-prism-border bg-prism-surface p-5">
            <p className="text-3xl font-semibold">AI Insights</p>
            <p className="mt-2 text-sm text-prism-text-muted">
              Natural language explanations
            </p>
          </article>
        </section>

        <footer className="flex flex-col gap-3 border-t border-prism-border pt-6 text-xs text-prism-text-muted md:flex-row md:items-center md:justify-between">
          <span>PRISM-ENGINE-V4.2.1 / ENVIRONMENT: PRODUCTION</span>
          <span className="inline-flex items-center gap-2">
            <span className="h-2 w-2 animate-pulse rounded-full bg-prism-green" />
            All systems nominal
          </span>
        </footer>
      </div>
    </main>
  );
}
