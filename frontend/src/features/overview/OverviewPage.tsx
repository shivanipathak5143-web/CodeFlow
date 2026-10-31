import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, messageOf } from "../../api/client";
import { useLoadedRepo } from "../../app/providers";
import { DiagramPanel } from "../../components/ui/DiagramPanel";
import { ErrorNote } from "../../components/ui/ErrorNote";
import { useElapsed } from "../../hooks/useElapsed";
import { filePath, repoName } from "../../lib/format";
import { StatsCards } from "./StatsCards";

export function OverviewPage() {
  const { url, data } = useLoadedRepo();
  const navigate = useNavigate();
  const [summary, setSummary] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const elapsed = useElapsed(loading);

  async function explain() {
    setLoading(true);
    setError(null);
    try {
      setSummary((await api.repoSummary(url)).summary);
    } catch (e) {
      setError(messageOf(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <article className="page">
      <header className="page__head">
        <p className="eyebrow mono">01 / Overview</p>
        <h1>{repoName(url)}</h1>
        <p className="mono dim">commit {data.commit}</p>
      </header>

      <StatsCards stats={data.stats} />

      <section className="block">
        <h2>Read these first</h2>
        <p className="dim">
          Starts at the entry point, then follows what it imports. Chosen by the import graph, not by a language model.
        </p>
        <ol className="reading">
          {data.onboarding.map((step, i) => (
            <li key={step.path}>
              <span className="mono">{i + 1}</span>
              <div>
                <Link to={filePath(step.path)} className="mono">
                  {step.path}
                </Link>
                <p className="dim">{step.reason}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>

      <section className="block">
        <h2>What the project does</h2>
        <p className="dim">
          Written by the language model from the README and the most-imported files. It is a starting point, so check
          it against the code.
        </p>
        <button className="btn btn--solid" onClick={explain} disabled={loading}>
          {loading ? `Reading files… ${elapsed}s` : summary ? "Explain again" : "Explain this repo"}
        </button>
        <ErrorNote message={error} />
        {summary && <p className="prose">{summary}</p>}
      </section>

      {data.ml_mermaid && (
        <section className="block">
          <h2>Pipeline stages</h2>
          <p className="dim">This looks like a machine-learning project. Files are placed in stages by their predicted role.</p>
          <DiagramPanel code={data.ml_mermaid} name="pipeline" onNodeClick={(p) => navigate(filePath(p))} />
        </section>
      )}
    </article>
  );
}