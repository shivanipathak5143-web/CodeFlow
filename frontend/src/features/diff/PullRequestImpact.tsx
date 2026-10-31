import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, messageOf } from "../../api/client";
import type { DiffResponse } from "../../api/types";
import { useLoadedRepo } from "../../app/providers";
import { DiagramPanel } from "../../components/ui/DiagramPanel";
import { ErrorNote } from "../../components/ui/ErrorNote";
import { filePath } from "../../lib/format";

export function PullRequestImpact() {
  const { url } = useLoadedRepo();
  const navigate = useNavigate();
  const [pr, setPr] = useState("");
  const [diff, setDiff] = useState("");
  const [result, setResult] = useState<DiffResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      setResult(await api.diff(url, pr.trim(), diff.trim()));
    } catch (err) {
      setError(messageOf(err));
    } finally {
      setBusy(false);
    }
  }

  const affected = result ? Object.entries(result.affected) : [];

  return (
    <article className="page">
      <header className="page__head">
        <p className="eyebrow mono">07 / PR impact</p>
        <h1>What a change reaches</h1>
        <p className="dim">
          Takes the files a pull request touches and finds every file that imports them, directly or through others.
          It reads the repository’s default branch, not the PR’s own commit, so treat it as an estimate.
        </p>
      </header>

      <form className="stack" onSubmit={submit}>
        <label className="field">
          <span className="eyebrow mono">Pull request URL</span>
          <input
            className="input mono"
            placeholder="https://github.com/owner/repo/pull/123"
            value={pr}
            onChange={(e) => setPr(e.target.value)}
          />
        </label>
        <label className="field">
          <span className="eyebrow mono">…or paste a unified diff</span>
          <textarea
            className="input mono"
            rows={4}
            placeholder="diff --git a/app/x.py b/app/x.py"
            value={diff}
            onChange={(e) => setDiff(e.target.value)}
          />
        </label>
        <div>
          <button className="btn btn--solid" disabled={busy || (!pr.trim() && !diff.trim())}>
            {busy ? "Working" : "Find impact"}
          </button>
        </div>
      </form>
      <ErrorNote message={error} />

      {result && (
        <>
          <div className="split">
            <section className="block block--tight">
              <h3 className="eyebrow mono">
                Changed <span>{result.changed.length}</span>
              </h3>
              <ul className="pathlist mono impact impact--changed">
                {result.changed.map((p) => (
                  <li key={p}>
                    <Link to={filePath(p)}>{p}</Link>
                  </li>
                ))}
              </ul>
            </section>
            <section className="block block--tight">
              <h3 className="eyebrow mono">
                Affected <span>{affected.length}</span>
              </h3>
              <ul className="pathlist mono impact impact--affected">
                {affected.slice(0, 60).map(([p, d]) => (
                  <li key={p}>
                    <Link to={filePath(p)}>{p}</Link> <small>{d} {d === 1 ? "step" : "steps"} away</small>
                  </li>
                ))}
                {affected.length > 60 && <li className="dim">…and {affected.length - 60} more</li>}
              </ul>
            </section>
          </div>
          <DiagramPanel code={result.mermaid} name="pr-impact" idmap={result.idmap} onNodeClick={(p) => navigate(filePath(p))} />
        </>
      )}
    </article>
  );
}