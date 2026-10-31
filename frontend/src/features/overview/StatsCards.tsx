import type { Stats } from "../../api/types";
import { nf } from "../../lib/format";

/** A ruled ledger rather than four boxes. */
export function StatsCards({ stats }: { stats: Stats }) {
  const roles = stats.role_source === "model" ? "model" : "rules";
  const items: [string, string, string][] = [
    ["Files", nf.format(stats.files), "code files parsed"],
    ["Imports", nf.format(stats.edges), "links between files"],
    ["Functions", nf.format(stats.functions), "found across the repo"],
    ["Roles", roles, stats.role_source === "model" ? "from your classifier" : "from keyword rules"],
  ];
  return (
    <dl className="ledger">
      {items.map(([term, value, note]) => (
        <div key={term}>
          <dt className="mono">{term}</dt>
          <dd>{value}</dd>
          <p className="mono">{note}</p>
        </div>
      ))}
    </dl>
  );
}