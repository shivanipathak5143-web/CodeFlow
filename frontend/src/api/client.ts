import type {
  AnalyzeResponse,
  DiffResponse,
  FileDetailsResponse,
  ModulesResponse,
  RolesResponse,
  SearchHit,
  TraceResponse,
} from "./types";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

export const messageOf = (e: unknown) => (e instanceof Error ? e.message : String(e));

async function post<T>(path: string, body: unknown): Promise<T> {
  let res: Response;
  try {
    res = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    throw new ApiError(0, "Cannot reach the backend. Is it running on port 8000?");
  }
  const text = await res.text();
  let json: unknown = null;
  try {
    json = text ? JSON.parse(text) : null;
  } catch {
    /* non-JSON error body */
  }
  if (!res.ok) {
    const detail = (json as { detail?: unknown } | null)?.detail;
    throw new ApiError(res.status, typeof detail === "string" ? detail : res.statusText || "Request failed");
  }
  return json as T;
}

export const api = {
  analyze: (url: string, refresh = false) => post<AnalyzeResponse>("/api/analyze", { url, refresh }),
  file: (url: string, path: string) => post<FileDetailsResponse>("/api/file", { url, path }),
  fileSummary: (url: string, path: string) => post<{ summary: string }>("/api/file_summary", { url, path }),
  repoSummary: (url: string) => post<{ summary: string }>("/api/summary", { url }),
  roles: (url: string) => post<RolesResponse>("/api/roles", { url }),
  modules: (url: string) => post<ModulesResponse>("/api/modules", { url }),
  search: (url: string, query: string) => post<{ results: SearchHit[] }>("/api/search", { url, query }),
  flowchart: (url: string, path: string, fn: string) =>
    post<{ mermaid: string }>("/api/flowchart", { url, path, function: fn }),
  trace: (url: string, target: string, start?: string) =>
    post<TraceResponse>("/api/trace", { url, target, start: start || null }),
  diff: (url: string, prUrl?: string, diff?: string) =>
    post<DiffResponse>("/api/diff", { url, pr_url: prUrl || null, diff: diff || null }),
};