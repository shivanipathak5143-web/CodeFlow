import { useRef } from "react";
import { DiagramToolbar } from "./DiagramToolbar";
import { MermaidDiagram } from "./MermaidDiagram";

interface Props {
  code: string;
  name: string;
  idmap?: Record<string, string>;
  onNodeClick?: (path: string) => void;
  emptyText?: string;
}

/** A diagram plus its export buttons. */
export function DiagramPanel({ code, name, idmap, onNodeClick, emptyText }: Props) {
  const svgRef = useRef<SVGSVGElement | null>(null);
  return (
    <div className="panel">
      <MermaidDiagram code={code} idmap={idmap} onNodeClick={onNodeClick} svgRef={svgRef} emptyText={emptyText} />
      <DiagramToolbar code={code} svgRef={svgRef} name={name} />
    </div>
  );
}