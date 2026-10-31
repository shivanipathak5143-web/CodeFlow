import { useState } from "react";
import { Link } from "react-router-dom";
import { api, messageOf } from "../../api/client";
import type { RoleRow } from "../../api/types";
import { DiagramPanel } from "../../components/ui/DiagramPanel";
import { ErrorNote } from "../../components/ui/ErrorNote";
import { RoleMark } from "../../components/ui/RoleMark";
import { useAsync } from "../../hooks/useAsync";
import { filePath, nf } from "../../lib/format";
import { FileSummary } from "./FileSummary";

interface Props {
  url: string;
  path: string;
  role?: RoleRow;
}

function FileLinks({ title, paths }: { title: string; paths: string[] }) {
  return (
    <section className="block block--tight">
      <h3 className="eyebrow mono">
        {title} <span>{paths.length}</span>
      </h3>
      {paths.length === 0 ? (
        <p className="dim">None inside this repo.</p>
      ) : (
        <ul className="pathlist mono">
          {paths.slice(0, 40).map((p) => (
            <li key={p}>
              <Link to={filePath(p)}>{p}</Link>
            </li>
          ))}
          {paths.length > 40 && <li className="dim">…and {paths.length - 40} more</li>}
        </ul>
      )}
    </section>
  );
}

export function FileDetails({ url, path, role }: Props) {
  const file = useAsync(() => api.file(url, path), [url, path]);
  const [fn, setFn] = useState("");
  const [flow, setFlow] = useState("");
  const [flowError, setFlowError] = useState<string | null>(null);

  async function draw(name: string) {
    setFlowError(null);
    try {
      setFlow((await api.flowchart(url, path, name)).mermaid);
    } catch (e) {
      setFlow("");
      setFlowError(messageOf(e));
    }
  }

  if (file.loading) return <p className="note mono">Loading {path}…</p>;
  if (file.error) return <ErrorNote message={file.error} />;
  const f = file.data;
  if (!f) return null;
  const chosen = fn && f.functions.includes(fn) ? fn : f.functions[0] ?? "";

  return (
    <div className="filedetails">
      <h2 className="mono filedetails__path">{f.path}</h2>
      <p className="mono dim">
        {f.lang} · {nf.format(f.loc)} lines
      </p>

      {role && (
        <p className="roleline">
          <RoleMark role={role.role} />
          <span className="mono dim">
            {role.source === "model" ? `model, confidence ${role.confidence.toFixed(2)}` : "keyword rule"}
            {role.rule !== role.role && ` · rule says ${role.rule}`}
          </span>
        </p>
      )}

      <FileSummary url={url} path={path} />

      {f.routes.length > 0 && (
        <p className="mono routes">
          {f.routes.map(([, r]) => (
            <span key={r}>{r}</span>
          ))}
        </p>
      )}

      <div className="split">
        <FileLinks title="Imports" paths={f.imports} />
        <FileLinks title="Imported by" paths={f.imported_by} />
      </div>

      {f.functions.length > 0 && f.lang === "python" && (
        <section className="block block--tight">
          <h3 className="eyebrow mono">Function flowchart</h3>
          <div className="row">
            <select className="select mono" value={chosen} onChange={(e) => setFn(e.target.value)}>
              {f.functions.map((n) => (
                <option key={n}>{n}</option>
              ))}
            </select>
            <button className="btn btn--ghost" onClick={() => draw(chosen)}>
              Draw
            </button>
          </div>
          <ErrorNote message={flowError} />
          {flow && <DiagramPanel code={flow} name={`flow-${chosen}`} />}
        </section>
      )}

      <section className="block block--tight">
        <h3 className="eyebrow mono">Source</h3>
        <pre className="code mono">
          {f.code.split("\n").map((line, i) => (
            <span key={i} className="code__line">
              {line || " "}
              {"\n"}
            </span>
          ))}
        </pre>
        {f.code.length >= 20000 && <p className="dim">Showing the first 20,000 characters.</p>}
      </section>
    </div>
  );
}