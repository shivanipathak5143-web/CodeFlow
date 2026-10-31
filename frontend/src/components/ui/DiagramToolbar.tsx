import { useState, type MutableRefObject } from "react";
import { readmeBlock, saveBlob, svgToPng, portableMermaid } from "../../lib/download";

interface Props {
  code: string;
  svgRef: MutableRefObject<SVGSVGElement | null>;
  name: string;
}

export function DiagramToolbar({ code, svgRef, name }: Props) {
  const [msg, setMsg] = useState("");
  const flash = (t: string) => {
    setMsg(t);
    setTimeout(() => setMsg(""), 1800);
  };

  async function copy(text: string, label: string) {
    try {
      await navigator.clipboard.writeText(text);
      flash(`${label} copied`);
    } catch {
      flash("Copy blocked by the browser");
    }
  }

  async function png() {
    if (!svgRef.current) return flash("Diagram is not ready");
    try {
      saveBlob(await svgToPng(svgRef.current), `${name}.png`);
    } catch (e) {
      flash(e instanceof Error ? e.message : "PNG export failed");
    }
  }

  const disabled = !code;
  return (
    <div className="toolbar">
      <button className="btn btn--ghost" disabled={disabled} onClick={() => copy(portableMermaid(code), "Mermaid")}>
        Copy Mermaid
      </button>
      <button
        className="btn btn--ghost"
        disabled={disabled}
        onClick={() => saveBlob(new Blob([portableMermaid(code)], { type: "text/plain" }), `${name}.mmd`)}
      >
        .mmd
      </button>
      <button className="btn btn--ghost" disabled={disabled} onClick={png}>
        PNG
      </button>
      <button className="btn btn--ghost" disabled={disabled} onClick={() => copy(readmeBlock(code), "README block")}>
        README block
      </button>
      <span className="toolbar__msg mono" role="status">
        {msg}
      </span>
    </div>
  );
}