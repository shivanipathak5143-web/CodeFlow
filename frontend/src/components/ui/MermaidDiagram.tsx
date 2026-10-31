import { useEffect, useRef, useState, type MutableRefObject } from "react";
import { portableMermaid } from "../../lib/download";

type MermaidApi = typeof import("mermaid").default;

let loader: Promise<MermaidApi> | null = null;
let counter = 0;

// Mermaid is large, so it is loaded the first time a diagram is shown.
function loadMermaid(): Promise<MermaidApi> {
  if (!loader) {
    loader = import("mermaid").then((m) => {
      m.default.initialize({
        startOnLoad: false,
        securityLevel: "strict",
        theme: "base",
        flowchart: { htmlLabels: false, useMaxWidth: false, curve: "linear" },
        themeVariables: {
          fontFamily: "'IBM Plex Mono', ui-monospace, monospace",
          fontSize: "13px",
          background: "#0e0d0b",
          mainBkg: "#1a1915",
          primaryColor: "#1a1915",
          primaryTextColor: "#ebe7da",
          primaryBorderColor: "#4a473d",
          nodeBorder: "#4a473d",
          lineColor: "#8b877a",
          secondaryColor: "#14130f",
          tertiaryColor: "#14130f",
          clusterBkg: "#12110e",
          clusterBorder: "#2f2d25",
          edgeLabelBackground: "#0e0d0b",
          titleColor: "#ebe7da",
        },
      });
      return m.default;
    });
  }
  return loader;
}

interface Props {
  code: string;
  /** mermaid node id (n3) -> file path. Needed together with onNodeClick to make nodes clickable. */
  idmap?: Record<string, string>;
  onNodeClick?: (path: string) => void;
  svgRef?: MutableRefObject<SVGSVGElement | null>;
  emptyText?: string;
}

export function MermaidDiagram({ code, idmap, onNodeClick, svgRef, emptyText = "Nothing to draw." }: Props) {
  const host = useRef<HTMLDivElement>(null);
  const [svg, setSvg] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let live = true;
    setError(null);
    if (!code) {
      setSvg("");
      return;
    }
    loadMermaid()
      .then((mermaid) => mermaid.render(`mmd${++counter}`, portableMermaid(code)))
      .then(({ svg: out }) => live && setSvg(out))
      .catch((e: unknown) => live && setError(e instanceof Error ? e.message : String(e)));
    return () => {
      live = false;
    };
  }, [code]);

  // After the SVG is in the DOM: expose it for export, and make file nodes clickable.
  useEffect(() => {
    const root = host.current;
    const el = root?.querySelector("svg") ?? null;
    if (svgRef) svgRef.current = el;
    if (!root || !idmap || !onNodeClick) return;
    const cleanups: Array<() => void> = [];
    root.querySelectorAll<SVGGElement>("g.node").forEach((node) => {
      const m = /^flowchart-(n\d+)-/.exec(node.id);
      const path = m ? idmap[m[1]] : undefined;
      if (!path) return;
      node.setAttribute("data-path", path);
      node.style.cursor = "pointer";
      const handler = () => onNodeClick(path);
      node.addEventListener("click", handler);
      cleanups.push(() => node.removeEventListener("click", handler));
    });
    return () => cleanups.forEach((fn) => fn());
  }, [svg, idmap, onNodeClick, svgRef]);

  if (error) return <p className="note note--error">Diagram error: {error}</p>;
  if (!code) return <p className="note">{emptyText}</p>;
  if (!svg) return <p className="note">Drawing…</p>;
  return <div className="diagram" ref={host} dangerouslySetInnerHTML={{ __html: svg }} />;
}