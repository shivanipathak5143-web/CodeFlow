import re
import httpx
import networkx as nx

PR_RE = re.compile(r"^https://github\.com/([\w.-]+)/([\w.-]+)/pull/(\d+)/?$")

def diff_text_from_pr(pr_url:str)->str:
    m=PR_RE.match(pr_url.strip())
    if not m:
        raise ValueError('Use a URL like https://github.com/owner/repo/pull/123')

    owner,repo,num=m.group()
    r = httpx.get(f"https://github.com/{owner}/{repo}/pull/{num}.diff",
                  follow_redirects=True, timeout=30)
    r.raise_for_status()
    return r.text

def changed_files(diff_text: str):
    return sorted(set(re.findall(r"^diff --git a/.+? b/(.+)$", diff_text, flags=re.M)))


def impact(G, changed):
    """Changed files plus every file that (transitively) imports them, with distance."""
    changed = [c for c in changed if c in G]
    affected, rev = {}, G.reverse(copy=False)
    for c in changed:
        for node, dist in nx.single_source_shortest_path_length(rev, c).items():
            if node not in changed:
                affected[node] = min(dist, affected.get(node, dist))
    return changed, dict(sorted(affected.items(), key=lambda kv: kv[1]))