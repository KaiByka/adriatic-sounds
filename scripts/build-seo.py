#!/usr/bin/env python3
"""Regenerate the committed SEO/GEO artifacts in site/ from the pin + license data.

Outputs:
  site/robots.txt                     allow all crawlers (incl. AI), point at sitemap
  site/sitemap.xml                    root URL (+ future per-pin pages)
  site/llms.txt                       project brief for LLM crawlers
  site/index.html                     the JSON-LD block (LD-JSON-BEGIN/END markers)
                                      and the static sound index (SOUND-INDEX-BEGIN/END)

Run after changing site/data/pins.json or site/LICENSE-MANIFEST.json:
    python3 scripts/build-seo.py
Everything it writes is committed; the site stays fully static.
"""
import datetime
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, "..", "site")
BASE = "https://sound.marespot.com"
TODAY = datetime.date.today().isoformat()

pins = json.load(open(os.path.join(SITE, "data", "pins.json")))
manifest = json.load(open(os.path.join(SITE, "LICENSE-MANIFEST.json")))
by_key = {s["key"]: s for s in manifest["sounds"]}


def esc(s):
    return html.escape(str(s), quote=True)


def iso_dur(sec):
    sec = int(round(sec))
    return f"PT{sec // 60}M{sec % 60}S"


def fmt_dur(sec):
    sec = int(round(sec))
    return f"{sec // 60}:{sec % 60:02d}"


# ---------------------------------------------------------------- JSON-LD
def build_jsonld():
    graph = [
        {
            "@type": "WebSite", "@id": BASE + "/#website",
            "name": "Sounds of the Adriatic", "url": BASE + "/", "inLanguage": "en",
            "description": "A sound map of the Croatian coast: free CC0/CC-BY field recordings "
                           "of harbours, coves, wind, bells and open sea. Tap a pin, hear the place.",
        },
        {
            "@type": "WebPage", "@id": BASE + "/#webpage", "url": BASE + "/",
            "name": "Sounds of the Adriatic — a sound map of the Croatian coast",
            "description": "11 free CC-BY field recordings of the Croatian coast. Tap a pin to listen.",
            "isPartOf": {"@id": BASE + "/#website"},
            "primaryImageOfPage": BASE + "/og-image.png",
        },
    ]
    items = []
    pos = 0
    for p in pins:
        if not p.get("audio"):
            continue
        pos += 1
        obj = {
            "@type": "AudioObject",
            "name": p["name"],
            "description": p["desc"],
            "url": f"{BASE}/#sound={p['key']}",
            "contentUrl": f"{BASE}/{p['audio']}",
        }
        m = by_key.get(p["key"])
        if m:
            # canonical https form of the license URL
            obj["license"] = m["license_url"].replace("http://creativecommons.org", "https://creativecommons.org")
            obj["author"] = {"@type": "Person", "name": f"{m['author']} (Freesound)"}
            obj["duration"] = iso_dur(m["duration_seconds"])
            obj["encodingFormat"] = "audio/ogg; codecs=opus"
            obj["contentSize"] = str(m["filesize_bytes"])
            if m.get("recorded_at"):
                obj["datePublished"] = m["recorded_at"][:10]
        items.append({"@type": "ListItem", "position": pos, "item": obj})
    graph.append({
        "@type": "ItemList", "@id": BASE + "/#sounds",
        "name": "All sounds on the map", "numberOfItems": len(items),
        "itemListElement": items,
    })
    ld = {"@context": "https://schema.org", "@graph": graph}
    s = json.dumps(ld, ensure_ascii=False, separators=(",", ":"))
    return '<script type="application/ld+json">' + s.replace("</", "<\\/") + "</script>"


# ------------------------------------------------------- static index list
def build_index_items():
    items = []
    for p in pins:
        m = by_key.get(p["key"])
        place = f"{p['place']} · {p['lat']:.2f}°N {p['lon']:.2f}°E"
        if p.get("audio") and m:
            lic = esc(m["license"].split(" (")[0])
            credit = (f'{lic} · {esc(m["author"])} (Freesound) · {fmt_dur(m["duration_seconds"])} · '
                      f'<a href="{esc(p["source"])}" rel="noopener">source ↗</a> · '
                      f'<a href="{esc(p["audio"])}" download>file ⇩</a>')
        else:
            credit = "Not yet recorded — the maker's own recording is planned for this spot."
        items.append(
            "    <li>\n"
            f'      <a class="idx-link" href="#sound={p["key"]}">{esc(p["name"])}</a>'
            f'<span class="idx-place">{esc(place)}</span>\n'
            f"      <p>{esc(p['desc'])}</p>\n"
            f'      <p class="idx-credit">{credit}</p>\n'
            "    </li>"
        )
    return "\n".join(items)


# ------------------------------------------------------------- patch files
def patch_index(replacements):
    path = os.path.join(SITE, "index.html")
    s = open(path).read()
    for begin, end, repl in replacements:
        pat = re.compile(re.escape(begin) + r".*?" + re.escape(end), re.S)
        if not pat.search(s):
            raise SystemExit(f"markers {begin} … {end} not found in index.html")
        s = pat.sub(lambda _: begin + "\n" + repl + "\n" + end, s, count=1)
    open(path, "w").write(s)
    print("patched", path)


def write(rel, content):
    path = os.path.join(SITE, rel)
    with open(path, "w") as f:
        f.write(content)
    print("wrote", path, len(content), "bytes")


ROBOTS = f"""# Sounds of the Adriatic — {BASE}
# We want to be indexed by search engines AND AI/LLM crawlers.
User-agent: *
Allow: /

Sitemap: {BASE}/sitemap.xml
"""

SITEMAP = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{BASE}/</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
"""


def build_llms_txt():
    lines = [
        "# Sounds of the Adriatic — llms.txt",
        "",
        "A sound map of the Croatian coast. A dark map of the Adriatic with pins;",
        "tapping a pin plays a field recording of that place — harbours, coves,",
        "wind in the rigging, church bells, cicadas, open-sea swell.",
        "",
        f"Site: {BASE}/",
        "Map data: Natural Earth (public domain).",
        "",
        "## License policy",
        "",
        "Only CC0 and CC-BY recordings are published (non-commercial and",
        "no-derivatives licenses are banned because the project promotes a",
        "commercial product). Every sound is listed with creator, license URL,",
        f"source URL and verification date in {BASE}/LICENSE-MANIFEST.json and is",
        "credited on its pin card.",
        "",
        "## Sounds",
        "",
    ]
    for i, p in enumerate(pins, 1):
        m = by_key.get(p["key"])
        head = f"{i}. **{p['name']}** — {p['place']} ({p['lat']:.2f}°N {p['lon']:.2f}°E). {p['desc']}"
        if p.get("audio") and m:
            lines.append(head)
            lines.append(f"   License: {m['license']} — creator: {m['author']} (Freesound).")
            lines.append(f"   Listen/share: {BASE}/#sound={p['key']} · file: {BASE}/{p['audio']} "
                         f"({fmt_dur(m['duration_seconds'])}, {m['filesize_bytes']} bytes, Opus mono)")
            lines.append(f"   Source: {p['source']}")
        else:
            lines.append(head)
            lines.append("   Status: not yet recorded (the maker's own recording is planned here).")
        lines.append("")
    lines += [
        "## How to attribute",
        "",
        "If you link, embed or reuse a recording, credit the creator named on the",
        "pin and link the license URL shown there (CC-BY requires attribution;",
        "CC0 does not). Example: \"Wind in the rigging\" by zybil, CC-BY 4.0,",
        f"via {BASE}/#sound=senj-bura.",
        "",
        "## Related",
        "",
        "A MareSpot experiment — live Adriatic wind, shelter & sea temperature at https://marespot.com",
        "",
    ]
    return "\n".join(lines)


def main():
    write("robots.txt", ROBOTS)
    write("sitemap.xml", SITEMAP)
    write("llms.txt", build_llms_txt())
    patch_index([
        ("<!-- LD-JSON-BEGIN -->", "<!-- LD-JSON-END -->", build_jsonld()),
        ("<!-- SOUND-INDEX-BEGIN -->", "<!-- SOUND-INDEX-END -->", build_index_items()),
    ])


if __name__ == "__main__":
    main()
