import { useEffect, useState } from "react";
import { messageOf } from "../api/client";

interface State<T> {
  data: T | null;
  error: string | null;
  loading: boolean;
}

/** Runs `fn` whenever `deps` change. Pass null to stay idle. Ignores results from stale runs. */
export function useAsync<T>(fn: (() => Promise<T>) | null, deps: unknown[]): State<T> {
  const [state, setState] = useState<State<T>>({ data: null, error: null, loading: fn !== null });

  useEffect(() => {
    if (!fn) {
      setState({ data: null, error: null, loading: false });
      return;
    }
    let live = true;
    setState((s) => ({ ...s, loading: true, error: null }));
    fn().then(
      (data) => live && setState({ data, error: null, loading: false }),
      (e) => live && setState({ data: null, error: messageOf(e), loading: false }),
    );
    return () => {
      live = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return state;
}