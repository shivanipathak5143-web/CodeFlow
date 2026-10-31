import { NavLink } from "react-router-dom";
import { useRepo } from "../../app/providers";

const ITEMS = [
  { to: "/repo/overview", label: "Overview" },
  { to: "/repo/graph", label: "Architecture" },
  { to: "/repo/files", label: "Files" },
  { to: "/repo/modules", label: "Modules" },
  { to: "/repo/search", label: "Search" },
  { to: "/repo/trace", label: "Data flow" },
  { to: "/repo/pr", label: "PR impact" },
];

export function Sidebar() {
  const { data } = useRepo();
  const source = data?.stats.role_source;

  return (
    <nav className="sidebar" aria-label="Sections">
      <ol>
        {ITEMS.map((item, i) => (
          <li key={item.to}>
            <NavLink to={item.to} className={({ isActive }) => (isActive ? "is-active" : "")}>
              <span className="mono">{String(i + 1).padStart(2, "0")}</span>
              {item.label}
            </NavLink>
          </li>
        ))}
      </ol>
      {source && (
        <p className="sidebar__foot mono">
          file roles from
          <br />
          <b>{source === "model" ? "your trained model" : "keyword rules"}</b>
          {source !== "model" && (
            <>
              <br />
              train one in ml/ to use ML
            </>
          )}
        </p>
      )}
    </nav>
  );
}