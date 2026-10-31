import { useNavigate } from "react-router-dom";
import { api } from "../../api/client";
import { useLoadedRepo } from "../../app/providers";
import { DiagramPanel } from "../../components/ui/DiagramPanel";
import { ErrorNote } from "../../components/ui/ErrorNote";
import { useAsync } from "../../hooks/useAsync";
import { filePath } from "../../lib/format";

function separation(s: number | null): string {
  if (s === null) return "Too few files to measure.";
  if (s < 0.25) return "Weak separation. Treat the groups as suggestions, not facts.";
  if (s < 0.5) return "Moderate separation. The groups are meaningful but overlap.";
  return "Strong separation.";
}

export function ModuleClusters() {
  const { url } = useLoadedRepo();
  const navigate = useNavigate();
  const mods = useAsync(() => api.modules(url), [url]);
  const m = mods.data;

  return (
    <article className="page">
      <header className="page__head">
        <p className="eyebrow mono">04 / Modules</p>
        <h1>Groups the code falls into</h1>
        <p className="dim">
          Unsupervised clustering over each file’s code and its position in the import graph. No labels were used, and
          the number of groups was chosen automatically.
        </p>
      </header>

      {mods.loading && <p className="note mono">Clustering…</p>}
      <ErrorNote message={mods.error} />

      {m && (
        <>
          <dl className="ledger ledger--small">
            <div>
              <dt className="mono">Groups</dt>
              <dd>{m.k}</dd>
            </div>
            <div>
              <dt className="mono">Silhouette</dt>
              <dd>{m.silhouette ?? "–"}</dd>
              <p className="mono">{separation(m.silhouette)}</p>
            </div>
            <div>
              <dt className="mono">Match to folders</dt>
              <dd>{m.nmi ?? "–"}</dd>
              <p className="mono">NMI, 0 to 1. Higher means the folders already reflect the groups.</p>
            </div>
          </dl>

          <DiagramPanel
            code={m.mermaid}
            name="modules"
            idmap={m.idmap}
            onNodeClick={(p) => navigate(filePath(p))}
          />

          <ul className="clusterlist">
            {m.clusters.map((c) => (
              <li key={c.id}>
                <span className="mono">{c.label}</span>
                <span className="mono dim">{c.size} files</span>
              </li>
            ))}
          </ul>
        </>
      )}
    </article>
  );
}