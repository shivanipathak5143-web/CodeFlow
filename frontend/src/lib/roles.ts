// Colours for file roles. Muted on purpose; they sit next to text, they do not shout.
export const ROLE_COLOR: Record<string, string> = {
  entry: "#ff5a1f",
  api: "#d9a441",
  model: "#7fb08a",
  data: "#6fa3b8",
  training: "#c9778a",
  evaluation: "#a89bc7",
  config: "#b8b09a",
  util: "#8b877a",
  test: "#5f5c52",
  other: "#44423a",
};

export const ROLE_ORDER = [
  "entry", "api", "model", "data", "training", "evaluation", "config", "util", "test", "other",
];

export const roleColor = (role: string) => ROLE_COLOR[role] ?? ROLE_COLOR.other;