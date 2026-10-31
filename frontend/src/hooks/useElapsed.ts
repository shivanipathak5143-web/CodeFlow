import { useEffect, useState } from "react";

/** Whole seconds since `running` became true. Honest progress for slow operations. */
export function useElapsed(running: boolean) {
  const [seconds, setSeconds] = useState(0);
  useEffect(() => {
    if (!running) {
      setSeconds(0);
      return;
    }
    const t0 = Date.now();
    const id = setInterval(() => setSeconds(Math.floor((Date.now() - t0) / 1000)), 500);
    return () => clearInterval(id);
  }, [running]);
  return seconds;
}