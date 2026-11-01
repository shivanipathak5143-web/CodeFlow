import type { ReactNode } from "react";

export type Block =
  | { kind: "para"; text: string }
  | { kind: "label"; text: string }
  | { kind: "items"; items: { term?: string; text: string }[] };

const BULLET = /^\s*(?:[-*•]|\d+[.)])\s+/;
const stripMarks = (s: string) => s.replace(/\*\*|__|`/g, "").trim();

function splitTerm(s: string): { term?: string; text: string } {
  const i = s.indexOf(":");
  if (i > 0 && i <= 48 && s[i + 1] === " " && s.slice(0, i).trim().split(/\s+/).length <= 6) {
    return { term: stripMarks(s.slice(0, i)), text: s.slice(i + 1).trim() };
  }
  return { text: s };
}

export function parseExplanation(raw: string): Block[] {
  const blocks: Block[] = [];
  let para: string[] = [];
  let items: { term?: string; text: string }[] | null = null;

  const flushPara = () => {
    if (!para.length) return;
    const t = para.join(" ").trim();
    para = [];
    if (!t) return;
    blocks.push(t.endsWith(":") && t.length < 60 ? { kind: "label", text: stripMarks(t.slice(0, -1)) } : { kind: "para", text: t });
  };
  const flushItems = () => {
    if (items && items.length) blocks.push({ kind: "items", items });
    items = null;
  };

  let blank = false;
  for (const line of raw.replace(/\r/g, "").split("\n")) {
    if (!line.trim()) {
      blank = true;
      flushPara();
      continue;
    }
    const m = BULLET.exec(line);
    if (m) {
      flushPara();
      if (!items) items = [];
      items.push(splitTerm(line.slice(m[0].length).trim()));
    } else if (items && !blank) {
      items[items.length - 1].text += " " + line.trim(); // a wrapped line of the previous bullet
    } else {
      flushItems();
      para.push(line.trim());
    }
    blank = false;
  }
  flushPara();
  flushItems();
  return blocks;
}

/** Text between backticks becomes inline code; stray ** and __ are dropped. */
function inline(text: string): ReactNode[] {
  const parts = text.replace(/\*\*|__/g, "").split("`");
  if (parts.length % 2 === 0) return [parts.join("`")]; // unbalanced backticks: leave as is
  return parts.map((part, i) =>
    i % 2 ? (
      <code key={i} className="mono">
        {part}
      </code>
    ) : (
      part
    ),
  );
}

export function Explanation({ text }: { text: string }) {
  const blocks = parseExplanation(text);
  const lead = blocks.findIndex((b) => b.kind === "para");
  return (
    <div className="explain">
      {blocks.map((b, i) => {
        if (b.kind === "para") {
          return (
            <p key={i} className={i === lead ? "explain__lead" : "explain__para"}>
              {inline(b.text)}
            </p>
          );
        }
        if (b.kind === "label") {
          return (
            <h3 key={i} className="eyebrow mono explain__label">
              {b.text}
            </h3>
          );
        }
        return (
          <ul key={i} className="explain__items">
            {b.items.map((it, j) => (
              <li key={j} className={it.term ? "" : "is-plain"}>
                {it.term && <b>{it.term}</b>}
                <span>{inline(it.text)}</span>
              </li>
            ))}
          </ul>
        );
      })}
    </div>
  );
}