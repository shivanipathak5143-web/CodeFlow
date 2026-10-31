import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { api, messageOf } from "../../api/client";
import type { SearchHit } from "../../api/types";
import { useLoadedRepo } from "../../app/providers";
import { ErrorNote } from "../../components/ui/ErrorNote";
import { filePath } from "../../lib/format";

export function CodeSearch() {
  const { url } = useLoadedRepo();
  const [query, setQuery] = useState("");
  const [hits, setHits] = useState<SearchHit[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;
    setBusy(true);
    setError(null);
    try {
      setHits((await api.search(url, query)).results);
    } catch (err) {
      setError(messageOf(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <article className="page">
      <header className="page__head">
        <p className="eyebrow mono">05 / Search</p>
        <h1>Find the file that does it</h1>
        <p className="dim">
          Matches your words against identifiers, imports and path names. It compares words, not meaning, so try the
          vocabulary the code would use (“auth”, “token”, “loader”).
        </p>
      </header>

      <form className="row" onSubmit={submit}>
        <input
          className="input input--grow mono"
          placeholder="where is the login logic"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button className="btn btn--solid" disabled={busy || !query.trim()}>
          {busy ? "Searching" : "Search"}
        </button>
      </form>
      <ErrorNote message={error} />

      {hits && hits.length === 0 && <p className="note">Nothing matched. Try different words.</p>}
      {hits && hits.length > 0 && (
        <ol className="results">
          {hits.map((h) => (
            <li key={h.path}>
              <Link to={filePath(h.path)} className="mono">
                {h.path}
              </Link>
              <span className="mono dim">score {h.score.toFixed(2)}</span>
              {h.functions.length > 0 && <p className="mono dim">{h.functions.join(", ")}</p>}
            </li>
          ))}
        </ol>
      )}
    </article>
  );
}