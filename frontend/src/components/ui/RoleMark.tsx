import { roleColor } from "../../lib/roles";

/** A small square in the role's colour, followed by the role name. */
export function RoleMark({ role }: { role: string }) {
  return (
    <span className="rolemark mono">
      <i style={{ background: roleColor(role) }} aria-hidden="true" />
      {role}
    </span>
  );
}