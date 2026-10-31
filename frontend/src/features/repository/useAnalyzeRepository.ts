import { useCallback, useState } from "react";
import { api, messageOf } from "../../api/client";
import type { AnalyzeResponse } from "../../api/types";
import { safeGet, safeSet } from "../../lib/storage";

export type AnalyzeStatus = "idle" | "loading" | "ready" | "error";
export const LAST_REPO_KEY = "codeflow.repo";

export function useAnalyzeRepository() {
  const [url, setUrl] = useState<string>(() => safeGet("session", LAST_REPO_KEY) ?? "");
  const [status, setStatus] = useState<AnalyzeStatus>("idle");
  const [data, setData] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  /** Resolves to true on success so callers can navigate. */
  const analyze = useCallback(async (next: string, refresh = false): Promise<boolean> => {
    setStatus("loading");
    setError(null);
    setUrl(next);
    try {
      const res = await api.analyze(next, refresh);
      setData(res);
      setStatus("ready");
      safeSet("session", LAST_REPO_KEY, next);
      return true;
    } catch (e) {
      setError(messageOf(e));
      setStatus("error");
      return false;
    }
  }, []);

  return { url, status, data, error, analyze };
}