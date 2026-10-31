import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useLoadedRepo } from "../../app/providers";
import { DiagramPanel } from "../../components/ui/DiagramPanel";
import { filePath } from "../../lib/format";

export function RepositoryGraph() {
  const { data } = useLoadedRepo();
  const navigate = useNavigate();
  const [view, setView] = useState<"imports" | "pipeline">("imports");
  const showing = view === "pipeline" && data.ml_mermaid ? data.ml_mermaid : data.mermaid;

  return (
    <article className="page page--wide">
      <header className="page__head">
        <p className="eyebrow mono">02 / Architecture</p>
        <h1>What imports what</h1>
        <p className="dim">
          The 40 most-imported files, grouped by top-level folder. An arrow means “imports”. Click a box to open that
          file.
        </p>
      </header>

      {data.ml_mermaid && (
        <div className="tabs" role="tablist">
          <button role="tab" aria-selected={view === "imports"} onClick={() => setView("imports")}>
            Imports
          </button>
          <button role="tab" aria-selected={view === "pipeline"} onClick={() => setView("pipeline")}>
            ML pipeline
          </button>
        </div>
      )}

      <DiagramPanel
        code={showing}
        name={view === "pipeline" ? "pipeline" : "architecture"}
        idmap={view === "imports" ? data.idmap : undefined}
        onNodeClick={view === "imports" ? (p) => navigate(filePath(p)) : undefined}
        emptyText="No import links were found. This repo may use a language or layout the parser does not follow yet."
      />
    </article>
  );
}