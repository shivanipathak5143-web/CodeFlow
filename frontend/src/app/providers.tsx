import { createContext, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import type { InteractionMode } from "../components/ui/MouseEffects";
import { useAnalyzeRepository } from "../features/repository/useAnalyzeRepository";
import { safeGet, safeSet } from "../lib/storage";

// ---- click effect preference -------------------------------------------------

export type FxMode = InteractionMode | "off";
export const FX_MODES: FxMode[] = ["sniper", "rings", "burst", "particles", "crosshair", "wavy", "off"];
const FX_KEY = "codeflow.fx";

interface FxValue {
  mode: FxMode;
  setMode: (m: FxMode) => void;
}
const FxContext = createContext<FxValue | null>(null);

export function useFx(): FxValue {
  const v = useContext(FxContext);
  if (!v) throw new Error("useFx must be used inside <Providers>");
  return v;
}

// ---- analysed repository -----------------------------------------------------

type RepoValue = ReturnType<typeof useAnalyzeRepository>;
const RepoContext = createContext<RepoValue | null>(null);

export function useRepo(): RepoValue {
  const v = useContext(RepoContext);
  if (!v) throw new Error("useRepo must be used inside <Providers>");
  return v;
}

/** The analysed repo. Only call inside routes guarded by <RequireRepo>. */
export function useLoadedRepo() {
  const { url, data } = useRepo();
  if (!data) throw new Error("No repository loaded");
  return { url, data };
}

export function Providers({ children }: { children: ReactNode }) {
  const [mode, setModeState] = useState<FxMode>(() => {
    const saved = safeGet("local", FX_KEY) as FxMode | null;
    return saved && FX_MODES.includes(saved) ? saved : "sniper";
  });
  const fx = useMemo<FxValue>(
    () => ({
      mode,
      setMode: (m) => {
        setModeState(m);
        safeSet("local", FX_KEY, m);
      },
    }),
    [mode],
  );

  const repo = useAnalyzeRepository();
  const { analyze, url, status, data, error } = repo;
  const value = useMemo(() => ({ analyze, url, status, data, error }), [analyze, url, status, data, error]);

  // Reloading a /repo/* page re-opens the last repository (the backend keeps it cached).
  const resumed = useRef(false);
  useEffect(() => {
    if (resumed.current) return;
    resumed.current = true;
    if (window.location.pathname.startsWith("/repo/") && url) void analyze(url);
  }, [analyze, url]);

  return (
    <FxContext.Provider value={fx}>
      <RepoContext.Provider value={value}>{children}</RepoContext.Provider>
    </FxContext.Provider>
  );
}