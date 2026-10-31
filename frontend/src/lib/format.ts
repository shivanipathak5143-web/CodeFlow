export const basename = (p: string) => p.split("/").pop() ?? p;

export function dirname(p: string) {
  const i = p.lastIndexOf("/");
  return i < 0 ? "" : p.slice(0, i);
}

export const nf = new Intl.NumberFormat("en-US");

/** "owner/name" or a full URL in, canonical GitHub URL out. */
export function toRepoUrl(input: string): string {
  const v = input.trim().replace(/\/+$/, "");
  if (/^[\w.-]+\/[\w.-]+$/.test(v)) return `https://github.com/${v}`;
  return v;
}

/** https://github.com/owner/name -> owner/name */
export function repoName(url: string): string {
  const m = url.match(/github\.com\/([\w.-]+)\/([\w.-]+?)(?:\.git)?\/?$/);
  return m ? `${m[1]}/${m[2]}` : url;
}

export function filePath(path: string) {
  return `/repo/files?path=${encodeURIComponent(path)}`;
}