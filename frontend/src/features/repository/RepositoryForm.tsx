import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useRepo } from "../../app/providers";
import { ErrorNote } from "../../components/ui/ErrorNote";
import { useElapsed } from "../../hooks/useElapsed";
import { toRepoUrl } from "../../lib/format";

const EXAMPLES = ["pallets/flask", "karpathy/nanoGPT", "psf/requests"];

export function RepositoryForm() {
  const { analyze, status, error, url } = useRepo();
  const [value, setValue] = useState(url);
  const navigate = useNavigate();
  const loading = status === "loading";
  const elapsed = useElapsed(loading);

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!value.trim() || loading) return;
    if (await analyze(toRepoUrl(value))) navigate("/repo/overview");
  }

  return (
    <form className="repoform" onSubmit={submit}>
      <label htmlFor="repo" className="eyebrow mono">
        Public GitHub repository
      </label>
      <div className="repoform__row">
        <input
          id="repo"
          className="repoform__input mono"
          placeholder="owner/name  or  https://github.com/owner/name"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          autoComplete="off"
          spellCheck={false}
        />
        <button className="btn btn--solid" type="submit" disabled={loading || !value.trim()}>
          {loading ? "Working" : "Analyse"}
        </button>
      </div>

      {loading ? (
        <p className="note mono" role="status">
          Cloning and parsing… {elapsed}s. Large repositories can take a minute.
        </p>
      ) : (
        <p className="repoform__try mono">
          try{" "}
          {EXAMPLES.map((ex) => (
            <button key={ex} type="button" className="linkish" onClick={() => setValue(ex)}>
              {ex}
            </button>
          ))}
        </p>
      )}
      <ErrorNote message={error} />
    </form>
  );
}