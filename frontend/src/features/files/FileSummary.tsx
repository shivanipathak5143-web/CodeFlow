import { useEffect, useState } from "react";
import { api, messageOf } from "../../api/client";
import { ErrorNote } from "../../components/ui/ErrorNote";
import { useElapsed } from "../../hooks/useElapsed";

export function FileSummary({ url, path }: { url: string; path: string }) {
  const [text, setText] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const elapsed = useElapsed(loading);

  // A different file means a different summary.
  useEffect(() => {
    setText(null);
    setError(null);
  }, [path]);

  async function run() {
    setLoading(true);
    setError(null);
    try {
      setText((await api.fileSummary(url, path)).summary);
    } catch (e) {
      setError(messageOf(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="filesummary">
      <button className="btn btn--ghost" onClick={run} disabled={loading}>
        {loading ? `Reading… ${elapsed}s` : text ? "Explain again" : "Explain this file"}
      </button>
      <ErrorNote message={error} />
      {text && <p className="prose">{text}</p>}
    </div>
  );
}