import { Link } from "react-router-dom";
import { FX_MODES, useFx, useRepo, type FxMode } from "../../app/providers";
import { BRAND } from "../../lib/brand";
import { repoName } from "../../lib/format";

export function Header({ minimal = false }: { minimal?: boolean }) {
  const { mode, setMode } = useFx();
  const { url, data } = useRepo();

  return (
    <header className="header">
      <Link to="/" className="brand">
        <svg width="18" height="18" viewBox="0 0 32 32" aria-hidden="true">
          <path d="M9 22 L16 10 L23 22" fill="none" stroke="currentColor" strokeWidth="2" />
          <circle cx="9" cy="22" r="3.4" fill="var(--accent)" />
          <circle cx="16" cy="10" r="3.4" fill="currentColor" />
          <circle cx="23" cy="22" r="3.4" fill="currentColor" />
        </svg>
        {BRAND}
      </Link>

      {!minimal && data && (
        <p className="header__repo mono" title={url}>
          {repoName(url)} <span>@ {data.commit}</span>
        </p>
      )}

      <label className="header__fx mono">
        click effect
        <select value={mode} onChange={(e) => setMode(e.target.value as FxMode)}>
          {FX_MODES.map((m) => (
            <option key={m} value={m}>
              {m}
            </option>
          ))}
        </select>
      </label>
    </header>
  );
}