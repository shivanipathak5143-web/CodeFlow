import { BrowserRouter } from "react-router-dom";
import MouseEffects from "../components/ui/MouseEffects";
import { useReducedMotion } from "../hooks/useReducedMotion";
import { Providers, useFx } from "./providers";
import { AppRoutes } from "./routes";

/**
 * One full-screen, click-through layer. MouseEffects listens on the whole document,
 * so every click on every page gets the effect without any page needing to know about it.
 */
function ClickEffects() {
  const { mode } = useFx();
  const reduced = useReducedMotion();
  if (reduced || mode === "off") return null;
  return (
    <div className="fx-layer" aria-hidden="true">
      <MouseEffects
        color="#ff5a1f"
        interactionMode={mode}
        duration={0.35}
        strokeWidth={1.5}
        effectSize={84}
        showLabel={false}
      />
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <Providers>
        <ClickEffects />
        <AppRoutes />
      </Providers>
    </BrowserRouter>
  );
}