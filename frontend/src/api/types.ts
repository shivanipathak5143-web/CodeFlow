// Shapes returned by the Python backend (app/main.py).

export interface Stats {
  files: number;
  edges: number;
  functions: number;
  ml_repo: boolean;
  role_source: "model" | "keywords" | "none";
}

export interface ReadingStep {
  path: string;
  reason: string;
}

export interface AnalyzeResponse {
  commit: string;
  stats: Stats;
  mermaid: string;
  idmap: Record<string, string>;
  ml_mermaid: string;
  onboarding: ReadingStep[];
}

export interface FileDetailsResponse {
  path: string;
  lang: string;
  loc: number;
  functions: string[];
  classes: string[];
  routes: [string, string][];
  imports: string[];
  imported_by: string[];
  code: string;
}

export interface RoleRow {
  path: string;
  role: string;
  confidence: number;
  source: "model" | "keywords";
  rule: string;
}

export interface RolesResponse {
  roles: RoleRow[];
  source: string;
}

export interface ModulesResponse {
  k: number;
  silhouette: number | null;
  nmi: number | null;
  ari: number | null;
  clusters: { id: number; label: string; size: number }[];
  mermaid: string;
  idmap: Record<string, string>;
}

export interface SearchHit {
  path: string;
  score: number;
  functions: string[];
}

export interface TraceResponse {
  path: string[];
  mermaid: string;
}

export interface DiffResponse {
  changed: string[];
  affected: Record<string, number>;
  mermaid: string;
  idmap: Record<string, string>;
}