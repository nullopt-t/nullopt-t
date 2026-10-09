"""Generate assets/stats.svg and assets/langs.svg (IBM Plex Mono embedded)."""
import base64, json, os, sys, urllib.request

USER = os.environ.get("GH_USER", "nullopt-t")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
FONT = base64.b64encode(open("assets/IBMPlexMono-SemiBold.woff2", "rb").read()).decode()
COLORS = {"Go": "#00ADD8", "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "C++": "#f34b7d",
          "C": "#8a8a8a", "HTML": "#e34c26", "CSS": "#563d7c", "Shell": "#89e051", "Python": "#3572A5"}

def api(path):
    req = urllib.request.Request("https://api.github.com" + path)
    req.add_header("Accept", "application/vnd.github+json")
    if TOKEN:
        req.add_header("Authorization", "Bearer " + TOKEN)
    with urllib.request.urlopen(req) as r:
        return json.load(r)

def collect():
    if "--demo" in sys.argv:
        return {"Repos": 17, "Stars": 3, "Followers": 11, "Following": 101}, {"Go": 7000, "JavaScript": 2000, "C++": 1000}
    user = api(f"/users/{USER}")
    repos = [r for r in api(f"/users/{USER}/repos?per_page=100&type=owner") if not r["fork"]]
    langs = {}
    for r in repos:
        for k, v in api(f"/repos/{USER}/{r['name']}/languages").items():
            langs[k] = langs.get(k, 0) + v
    stats = {"Repos": user["public_repos"], "Stars": sum(r["stargazers_count"] for r in repos),
             "Followers": user["followers"], "Following": user["following"]}
    return stats, langs

def wrap(w, h, body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<style>@font-face{{font-family:"PlexMono";src:url(data:font/woff2;base64,{FONT}) format("woff2");font-weight:600}}
text{{font-family:"PlexMono","IBM Plex Mono",ui-monospace,Menlo,Consolas,monospace;font-weight:600;font-size:14px;fill:#c9d1d9}}
.t{{fill:#00ADD8;font-size:15px}}.m{{fill:#8b949e}}.v{{fill:#fff}}</style>
<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="8" fill="#0d1117" stroke="#30363d"/>
{body}</svg>'''

def stats_svg(s):
    rows = "".join(f'<text class="m" x="24" y="{66+i*26}">{k}</text><text class="v" x="{W-24}" y="{66+i*26}" text-anchor="end">{v}</text>'
                   for i, (k, v) in enumerate(s.items()))
    return wrap(W, 170, f'<text class="t" x="24" y="34">$ stats --user {USER}</text>{rows}')

def langs_svg(l):
    top = sorted(l.items(), key=lambda x: -x[1])[:5]
    total = sum(v for _, v in top) or 1
    rows = ""
    for i, (k, v) in enumerate(top):
        y = 62 + i * 20
        pct = v / total * 100
        rows += (f'<text class="m" x="24" y="{y}">{k}</text>'
                 f'<rect x="150" y="{y-11}" width="150" height="9" rx="4" fill="#21262d"/>'
                 f'<rect x="150" y="{y-11}" width="{max(pct*1.5,4):.0f}" height="9" rx="4" fill="{COLORS.get(k, "#00ADD8")}"/>'
                 f'<text class="v" x="{W-24}" y="{y}" text-anchor="end">{pct:.0f}%</text>')
    return wrap(W, 170, f'<text class="t" x="24" y="34">$ top-languages</text>{rows}')

W = 360
stats, langs = collect()
os.makedirs("assets", exist_ok=True)
open("assets/stats.svg", "w", encoding="utf-8").write(stats_svg(stats))
open("assets/langs.svg", "w", encoding="utf-8").write(langs_svg(langs))
print("ok", stats)
