#!/usr/bin/env python3
"""Find candidate Freesound sounds for the Adriatic sound map WITHOUT an API key.

Scrapes Freesound's public search (license-filtered) and sound pages, then verifies
per sound, mechanically:
  - license must be exactly CC0 or CC-BY (any NC/ND/other marker -> rejected)
  - geotag must exist and be inside the Adriatic bbox (41.5..46.5 N, 12..20 E)
  - duration <= 180 s (ingest trims to <= 90 s)
  - not already used in site/LICENSE-MANIFEST.json

Output: scripts/data/candidates.json (all verified candidates with preview URLs).

Usage: python3 scripts/find-freesound-candidates.py
No secrets needed; public pages only; polite 0.4 s delay between requests.
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts" / "data" / "candidates.json"
MANIFEST = ROOT / "site" / "LICENSE-MANIFEST.json"

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36 adriatic-sounds-research/1.0"}

ALLOWED = {
    "creativecommons.org/publicdomain/zero/1.0/": "CC0 1.0",
    "creativecommons.org/licenses/by/4.0/": "CC-BY 4.0",
    "creativecommons.org/licenses/by/3.0/": "CC-BY 3.0",
}
BANNED = ("noncommercial", "-nc", "/nd", "noderivs", "all-rights-reserved", "sampling+")
LAT0, LAT1, LON0, LON1 = 41.5, 46.5, 12.0, 20.0

QUERIES = [
    "croatia sea waves", "croatia waves rocks", "croatia harbor ambience", "croatia church bells",
    "croatia cicadas", "croatia crickets night", "croatia wind", "croatia seagulls",
    "adriatic sea", "dalmatia", "istria sea", "kvarner", "zadar", "split croatia",
    "dubrovnik", "hvar", "pula", "rovinj", "sibenik", "pula istria", "venice lagoon",
    "piran slovenia", "trieste", "ravenna", "ancona", "pescara", "bari", "brindisi",
    "croatia market", "croatia rain", "croatia thunder", "croatia boat", "croatia ferry",
    "croatia underwater", "croatia kayak", "croatia cove",
]
LICENSES = ["Creative Commons 0", "Creative Commons Attribution"]


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def search(q, lic):
    f = f'license:"{lic}" duration:[0 TO 180]'
    url = "https://freesound.org/search/?" + urllib.parse.urlencode({"q": q, "f": f})
    html = get(url)
    return re.findall(r"/people/([\w.-]+)/sounds/(\d+)/", html)


def parse_sound(user, sid):
    url = f"https://freesound.org/people/{user}/sounds/{sid}/"
    html = get(url)
    g = lambda pat, cast=str: (lambda m: cast(m.group(1)) if m else None)(re.search(pat, html))
    title = g(r'property="og:audio:title" content="([^"]*)"')
    artist = g(r'property="og:audio:artist" content="([^"]*)"')
    lic_url = g(r'(creativecommons\.org/(?:licenses|publicdomain)/[a-z0-9./-]+)')
    dur = g(r'duration="([0-9.]+)"', float)
    prev_lq = g(r'property="og:audio" content="[^"]*?(https://cdn\.freesound\.org/previews/[^"]+-lq\.mp3)"')
    created = g(r'datetime="([^"]+)"')
    geotag_name = g(r'title="Geotag: ([^"]*)"')
    has_geo_modal = "geotag/?ajax=1" in html
    rec = {
        "freesound_id": int(sid), "page_url": url, "username": user,
        "title": title, "duration": dur, "license_url": lic_url and ("https://" + lic_url if not lic_url.startswith("http") else lic_url),
        "preview_hq_mp3": prev_lq and prev_lq.replace("-lq.mp3", "-hq.mp3"),
        "created": created, "geotag_name": geotag_name, "has_geotag": has_geo_modal,
    }
    if has_geo_modal:
        try:
            geo = get(url + "geotag/?ajax=1")
            m = re.search(r'center-lat="([^"]+)"', geo)
            n = re.search(r'center-lon="([^"]+)"', geo)
            rec["lat"] = float(m.group(1)) if m else None
            rec["lon"] = float(n.group(1)) if n else None
        except Exception:
            rec["lat"] = rec["lon"] = None
    else:
        rec["lat"] = rec["lon"] = None
    return rec


def verify(rec):
    if not rec.get("license_url"):
        return "no license on page"
    key = rec["license_url"].lower().replace("https://", "").replace("http://", "")
    name = ALLOWED.get(key)
    if name is None or any(b in key for b in BANNED):
        return f"license not CC0/CC-BY: {rec['license_url']}"
    if rec.get("lat") is None or rec.get("lon") is None:
        return "no geotag"
    if not (LAT0 <= rec["lat"] <= LAT1 and LON0 <= rec["lon"] <= LON1):
        return f"geotag {rec['lat']},{rec['lon']} outside bbox"
    if not rec.get("duration") or rec["duration"] > 180:
        return f"duration {rec.get('duration')}"
    if not rec.get("preview_hq_mp3"):
        return "no preview"
    rec["license"] = name
    return None


def main():
    used = {s.get("freesound_id") for s in json.loads(MANIFEST.read_text())["sounds"]}
    seen = set()
    candidates = []
    rejected = {}
    for q in QUERIES:
        for lic in LICENSES:
            try:
                pairs = search(q, lic)
            except Exception as e:
                print(f"search failed {q!r} {lic}: {e}", file=sys.stderr)
                continue
            for user, sid in pairs:
                if int(sid) in used or (user, sid) in seen:
                    continue
                seen.add((user, sid))
                time.sleep(0.4)
                try:
                    rec = parse_sound(user, sid)
                except Exception as e:
                    rejected[sid] = f"fetch error {e}"
                    continue
                rec["query"] = q
                why = verify(rec)
                if why:
                    rejected[sid] = why
                else:
                    candidates.append(rec)
                    print(f"OK  {rec['freesound_id']:>7} {rec['license']:<9} {rec['duration']:>6.1f}s "
                          f"{rec['lat']:.2f},{rec['lon']:.2f} {rec['geotag_name'] or ''} :: {rec['title'][:60]}")
            print(f"-- {q!r} [{lic}]: {len(pairs)} hits", file=sys.stderr)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({"candidates": candidates, "rejected": rejected}, indent=1, ensure_ascii=False))
    print(f"\n{len(candidates)} verified candidates -> {OUT}")
    print(f"{len(rejected)} rejected (see rejected map)")


if __name__ == "__main__":
    main()
