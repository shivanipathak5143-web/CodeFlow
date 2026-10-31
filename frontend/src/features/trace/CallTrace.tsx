import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, messageOf } from "../../api/client";
import type { TraceResponse } from "../../api/types";
import { useLoadedRepo } from "../../app/providers";
import { DiagramPanel } from "../../components/ui/DiagramPanel";
import { ErrorNote } from "../../components/ui/ErrorNote";
import { filePath } from "../../lib/format";

export function CallTrace() {
  const { url } = useLoadedRepo();
  const navigate = useNavigate();
  const [target, setTarget] = useState("");
  const [start, setStart] = useState("");
  const [result, setResult] = useState<TraceResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!target.trim()) return;
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      setResult(await api.trace(url, target.trim(), start.trim()));
    } catch (err) {
      setError(messageOf(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <article className="page">
      <header className="page__head">
        <p className="eyebrow mono">06 / Data flow</p>
        <h1>How does a call get from here to there</h1>
        <p className="dim">
          Finds the shortest chain of function calls from an entry point to anything whose name matches the target.
          Without a start, HTTP routes are used. Python only.
        </p>
      </header>

      <form className="stack" onSubmit={submit}>
        <div className="row">
          <label className="field">
            <span className="eyebrow mono">Target</span>
            <input
              className="input mono"
              placeholder="db, save, model…"
              value={target}
              onChange={(e) => setTarget(e.target.value)}
            />
          </label>
          <label className="field">
            <span className="eyebrow mono">Start (optional)</span>
            <input
              className="input mono"
              placeholder="part of a function or file name"
              value={start}
              onChange={(e) => setStart(e.target.value)}
            />
          </label>
          <button className="btn btn--solid" disabled={busy || !target.trim()}>
            {busy ? "Tracing" : "Trace"}
          </button>
        </div>
      </form>
      <ErrorNote message={error} />

      {result && (
        <>
          <ol className="tracepath mono">
            {result.path.map((node) => {
              const [file, fn] = node.split("::");
              return (
                <li key={node}>
                  <b>{fn}()</b> <Link to={filePath(file)}>{file}</Link>
                </li>
              );
            })}
          </ol>
          <DiagramPanel code={result.mermaid} name="trace" onNodeClick={(p) => navigate(filePath(p))} />
        </>
      )}
    </article>
  );
}