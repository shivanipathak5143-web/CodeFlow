import { useRef, useState } from "react";
import { DiagramToolbar } from "./DiagramToolbar";
import { MermaidDiagram } from "./MermaidDiagram";

interface Props {
  code: string;
  name: string;
  idmap?: Record<string, string>;
  onNodeClick?: (path: string) => void;
  emptyText?: string;
}

/** A diagram plus its export buttons. Fits the panel width by default; "Actual size" scrolls instead. */
export function DiagramPanel({ code, name, idmap, onNodeClick, emptyText }: Props) {
  const svgRef = useRef<SVGSVGElement | null>(null);
  const [fit, setFit] = useState(true);
  return (
    <div className={fit ? "panel panel--fit" : "panel"}>
      <MermaidDiagram code={code} idmap={idmap} onNodeClick={onNodeClick} svgRef={svgRef} emptyText={emptyText} />
      <DiagramToolbar code={code} svgRef={svgRef} name={name} fit={fit} onToggleFit={() => setFit((f) => !f)} />
    </div>
  );
}