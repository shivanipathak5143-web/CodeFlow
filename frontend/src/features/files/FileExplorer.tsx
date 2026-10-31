import { useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../../api/client";
import { useLoadedRepo } from "../../app/providers";
import { ErrorNote } from "../../components/ui/ErrorNote";
import { useAsync } from "../../hooks/useAsync";
import { basename, dirname } from "../../lib/format";
import { ROLE_ORDER, roleColor } from "../../lib/roles";
import { FileDetails } from "./FileDetails";

const LIMIT = 300;

export function FileExplorer() {
  const { url } = useLoadedRepo();
  const [params, setParams] = useSearchParams();
  const selected = params.get("path");
  const [text, setText] = useState("");
  const [role, setRole] = useState("all");

  const roles = useAsync(() => api.roles(url), [url]);
  const rows = roles.data?.roles ?? [];

  const visible = useMemo(() => {
    const q = text.trim().toLowerCase();
    return rows
      .filter((r) => (role === "all" || r.role === role) && (!q || r.path.toLowerCase().includes(q)))
      .sort((a, b) => ROLE_ORDER.indexOf(a.role) - ROLE_ORDER.indexOf(b.role) || b.confidence - a.confidence);
  }, [rows, text, role]);

  const selectedRow = rows.find((r) => r.path === selected);

  return (
    <article className="page page--wide">
      <header className="page__head">
        <p className="eyebrow mono">03 / Files</p>
        <h1>Every file, with its role</h1>
        <p className="dim">
          {roles.data?.source === "model"
            ? "Roles are predicted by your trained classifier. Low-confidence files show as “other”."
            : "Roles come from keyword rules in the file path. Train the classifier in ml/ to replace them."}
        </p>
      </header>

      <div className="explorer">
        <div className="explorer__list">
          <div className="row">
            <input
              className="input mono"
              placeholder="filter by path"
              value={text}
              onChange={(e) => setText(e.target.value)}
              aria-label="Filter files by path"
            />
            <select className="select mono" value={role} onChange={(e) => setRole(e.target.value)} aria-label="Filter by role">
              <option value="all">all roles</option>
              {ROLE_ORDER.map((r) => (
                <option key={r}>{r}</option>
              ))}
            </select>
          </div>
          {roles.loading && <p className="note mono">Classifying files…</p>}
          <ErrorNote message={roles.error} />
          <ul className="filelist">
            {visible.slice(0, LIMIT).map((r) => (
              <li key={r.path}>
                <button
                  className={r.path === selected ? "is-selected" : ""}
                  onClick={() => setParams({ path: r.path })}
                  title={r.path}
                >
                  <i style={{ background: roleColor(r.role) }} aria-hidden="true" />
                  <span className="mono">
                    {basename(r.path)}
                    <small>{dirname(r.path)}</small>
                  </span>
                  <em className="mono">{r.role}</em>
                </button>
              </li>
            ))}
          </ul>
          {visible.length > LIMIT && (
            <p className="dim mono">
              Showing {LIMIT} of {visible.length}. Filter to narrow it down.
            </p>
          )}
          {!roles.loading && visible.length === 0 && <p className="dim">No files match.</p>}
        </div>

        <div className="explorer__detail">
          {selected ? (
            <FileDetails url={url} path={selected} role={selectedRow} />
          ) : (
            <p className="note">Choose a file on the left.</p>
          )}
        </div>
      </div>
    </article>
  );
}