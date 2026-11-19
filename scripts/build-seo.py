#!/usr/bin/env python3
"""Regenerate all committed SEO/GEO artifacts and static pages in site/.

Inputs : site/data/pins.json, site/data/places.json, site/LICENSE-MANIFEST.json
Outputs:
  site/robots.txt                     allow all crawlers (incl. AI), sitemap pointer
  site/sitemap.xml                    /, /credits.html, /s/<key>.html for every pin
  site/llms.txt                       project brief for LLM crawlers
  site/credits.html                   human-readable license/attribution table
  site/s/<key>.html                   one static page per pin (canonical, JSON-LD,
                                      tap-to-play, links to map + all other pins)
  site/index.html                     patched between markers:
                                      LD-JSON-BEGIN/END   -> JSON-LD incl. FAQPage
                                      SOUND-INDEX-BEGIN/END -> static sound index
                                      FAQ-BEGIN/END       -> FAQ <details> list

Run after changing pins.json / LICENSE-MANIFEST.json / the FAQ below:
    python3 scripts/build-seo.py
Everything written is committed; the site stays fully static, audio stays tap-gated.
"""
import datetime
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, "..", "site")
BASE = "https://sound.marespot.com"
REPO = "https://github.com/KaiByka/adriatic-sounds"
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


def kb(n):
    return f"{n / 1000:.0f} KB"


def lic_url(m):
    return m["license_url"].replace("http://creativecommons.org", "https://creativecommons.org")


def lic_short(m):
    return m["license"].split(" (")[0]


# ------------------------------------------------------------------- FAQ
FAQ = [
    {
        "q": "Are the recordings free to use?",
        "a": ("Yes. Every published sound is <b>CC0 or CC-BY</b> — the only licenses we ship. "
              "Non-commercial (CC-BY-NC) and no-derivatives (CC-BY-ND) licenses are banned here, because this "
              "project promotes a commercial product. To reuse a recording, credit the creator and link the "
              "license shown on its pin card; the full list is on the <a href=\"/credits.html\">credits page</a> "
              "and in <a href=\"/LICENSE-MANIFEST.json\">LICENSE-MANIFEST.json</a>."),
    },
    {
        "q": "Where was each sound actually recorded?",
        "a": ("Each pin card and the manifest carry the exact coordinates and recording date, and the caption "
              "states the real place. Some Adriatic recordings were made on the Italian or Slovenian shore — "
              "the sea has no border — and every caption says where the sound was actually made."),
    },
    {
        "q": "What is the sea organ in Zadar?",
        "a": ("The Morske orgulje is a wave-powered sound installation built into the Zadar waterfront: the sea "
              "pushes air through tuned pipes. It is the most famous sound-object on the coast — and its pin is "
              "honestly marked <b>not yet recorded</b> until the maker's own recording of it is published."),
    },
    {
        "q": "Can I contribute a recording?",
        "a": (f"Yes, if it is CC0 or CC-BY. Ideally 30–90 seconds, mono, no talking, wind guard on the mic. "
              f"Open an issue or PR in the <a href=\"{REPO}\">project repository</a> with the file, exact "
              "location, date and license — nothing is published until the license is verified."),
    },
    {
        "q": "How do I link to or share one sound?",
        "a": ("Use the pin's own page, e.g. <a href=\"/s/senj-bura.html\">sound.marespot.com/s/senj-bura.html</a>, "
              "or the map deep link <a href=\"/#sound=senj-bura\">sound.marespot.com/#sound=senj-bura</a> "
              "(also accepted as ?sound=senj-bura). Please credit the creator and license when you share."),
    },
]

# ------------------------------------------------------------------- CSP
CSP_PAGE = ("default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; "
            "img-src 'self' data:; media-src 'self' blob:; connect-src 'self'; font-src 'self'; "
            "object-src 'none'; base-uri 'self'; form-action 'none'; upgrade-insecure-requests")
CSP_STATIC = CSP_PAGE.replace("script-src 'unsafe-inline'", "script-src 'none'")

PAGE_CSS = """
  :root { --bg:#050c16; --panel:#101d33; --line:#1d2c47; --text:#e8edf5; --muted:#8fa0b8; --accent:#d8a24a; --teal:#57c7c9; --serif:Georgia,'Times New Roman',serif; }
  * { box-sizing:border-box; margin:0; padding:0; }
  body { background: radial-gradient(140% 100% at 50% -10%, #0c1c33 0%, var(--bg) 58%) fixed, var(--bg); color:var(--text); font:16px/1.6 system-ui,sans-serif; min-height:100vh; display:flex; flex-direction:column; }
  header.ph { text-align:center; padding:44px 16px 0; }
  .kicker { font-size:11px; letter-spacing:.42em; text-transform:uppercase; }
  .kicker a { color:var(--accent); text-decoration:none; }
  h1 { font: italic 700 clamp(26px,5vw,40px)/1.15 var(--serif); margin-top:10px; }
  .meta { color:var(--accent); font-size:13.5px; margin-top:6px; letter-spacing:.04em; }
  main.pcard { width:calc(100% - 24px); max-width:760px; margin:22px auto 0; background:rgba(13,24,43,.8); border:1px solid rgba(216,162,74,.18); border-radius:20px; padding:20px 22px; }
  .desc { color:var(--muted); font-size:15.5px; }
  .row { display:flex; align-items:center; gap:14px; margin-top:16px; flex-wrap:wrap; }
  button.play { background:linear-gradient(180deg,#eec06f,var(--accent)); color:#1a1205; border:0; border-radius:999px; min-width:110px; min-height:44px; padding:11px 20px; font:600 15px system-ui,sans-serif; cursor:pointer; box-shadow:0 6px 20px rgba(216,162,74,.32); }
  button.play:disabled { background:var(--panel); color:var(--muted); border:1px solid var(--line); box-shadow:none; cursor:default; }
  button.play.playing::before { content:"◼ "; } button.play:not(.playing)::before { content:"▶ "; }
  button.play:disabled::before { content:""; }
  .track { flex:1 1 120px; height:5px; background:var(--line); border-radius:99px; overflow:hidden; }
  .fill { height:100%; width:0; background:linear-gradient(90deg,var(--accent),#f2cd8a); }
  .time { font:12px system-ui,sans-serif; color:var(--muted); font-variant-numeric:tabular-nums; min-width:86px; text-align:right; }
  .credit { font-size:12.5px; color:#7288a6; margin-top:14px; line-height:1.6; }
  .credit a, .bridge a { color:var(--accent); text-decoration:none; border-bottom:1px dotted rgba(216,162,74,.5); }
  .bridge { margin-top:12px; font-size:13.5px; color:var(--muted); }
  .bridge a { color:var(--teal); border-bottom-color:rgba(87,199,201,.5); }
  .badge { display:inline-block; font-size:11px; letter-spacing:.08em; text-transform:uppercase; border:1px solid var(--accent); color:var(--accent); border-radius:6px; padding:2px 8px; margin-left:8px; vertical-align:middle; }
  .maplink { display:inline-block; margin-top:18px; color:var(--text); border:1px solid var(--line); border-radius:999px; padding:10px 20px; text-decoration:none; min-height:44px; }
  .maplink:hover { border-color:var(--accent); color:var(--accent); }
  nav.others { width:calc(100% - 24px); max-width:760px; margin:30px auto 0; }
  nav.others h2 { font: italic 700 20px var(--serif); margin-bottom:10px; }
  nav.others ul { list-style:none; display:grid; grid-template-columns:1fr 1fr; gap:8px; }
  @media (max-width:640px){ nav.others ul { grid-template-columns:1fr; } }
  nav.others a { display:block; color:var(--muted); text-decoration:none; border:1px solid var(--line); border-radius:10px; padding:9px 12px; font-size:13.5px; }
  nav.others a:hover { color:var(--accent); border-color:rgba(216,162,74,.4); }
  nav.others a.cur { color:var(--accent); border-color:rgba(216,162,74,.5); }
  footer { text-align:center; padding:26px 16px 40px; color:#7288a6; font-size:14px; border-top:1px solid var(--line); margin-top:32px; }
  footer a { color:var(--muted); }
  footer .fine { margin-top:8px; font-size:12px; }
  table.credits { width:100%; border-collapse:collapse; font-size:13px; margin-top:14px; }
  table.credits th { text-align:left; color:var(--accent); font-weight:600; padding:8px 8px; border-bottom:1px solid var(--line); }
  table.credits td { padding:8px; border-bottom:1px solid rgba(29,44,71,.6); vertical-align:top; color:var(--muted); }
  table.credits td a { color:var(--accent); }
  main.pcard p.lead { color:var(--muted); font-size:15px; margin-bottom:6px; }
"""

FOOTER = f"""<footer>
  <p><b>A MareSpot experiment — live Adriatic wind, shelter &amp; sea temperature at <a href="https://marespot.com">marespot.com</a></b></p>
  <p class="fine">Map: Natural Earth (public domain) · All sounds CC0 / CC-BY, credited on each pin card · full list in LICENSE-MANIFEST.json</p>
</footer>"""

PLAYER_JS = """
(() => {
  const btn = document.getElementById('play');
  if (!btn || btn.disabled) return;
  const audio = new Audio();
  audio.preload = 'none'; /* no audio bytes are fetched before the tap */
  const file = btn.dataset.file;
  const fill = document.getElementById('fill'), timeEl = document.getElementById('time');
  let loaded = false;
  const fmt = s => { s = Math.floor(s); return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0'); };
  function sync() {
    const playing = !audio.paused && !audio.ended;
    btn.classList.toggle('playing', playing);
    btn.textContent = playing ? 'Stop' : 'Play';
  }
  btn.addEventListener('click', async () => {
    if (!audio.paused) { audio.pause(); return; }
    btn.disabled = true;
    try {
      if (!loaded) {
        btn.textContent = 'Loading…';
        const res = await fetch(file); /* first tap on this page: only now are bytes requested */
        const buf = await res.arrayBuffer();
        audio.src = URL.createObjectURL(new Blob([buf.slice(0)], { type: 'audio/ogg' }));
        loaded = true;
      }
      await audio.play();
    } catch (e) { console.error(e); }
    btn.disabled = false;
  });
  audio.addEventListener('play', sync);
  audio.addEventListener('pause', sync); /* headphone unplug / OS interruption */
  audio.addEventListener('ended', sync);
  audio.addEventListener('loadedmetadata', () => {
    if (audio.duration && isFinite(audio.duration)) timeEl.textContent = '0:00 / ' + fmt(audio.duration);
  });
  audio.addEventListener('timeupdate', () => {
    if (audio.duration && isFinite(audio.duration)) {
      fill.style.width = (audio.currentTime / audio.duration * 100) + '%';
      timeEl.textContent = fmt(audio.currentTime) + ' / ' + fmt(audio.duration);
    }
  });
  document.addEventListener('visibilitychange', () => { if (document.hidden) audio.pause(); });
})();
"""


def page_head(title, desc, canonical, ld, csp, og_type="website"):
    ld_js = json.dumps(ld, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="google-site-verification" content="TXobfaZY7FfdrdfULA5z-FzDM37T2LCpVPcXOT2QNiE">
<meta name="theme-color" content="#050c16">
<meta http-equiv="Content-Security-Policy" content="{csp}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="Sounds of the Adriatic">
<meta property="og:locale" content="en_US">
<meta property="og:image" content="{BASE}/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Dark night map of the Adriatic with gold sound pins — Sounds of the Adriatic">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{BASE}/og-image.png">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%23050c16'/%3E%3Ccircle cx='16' cy='16' r='6' fill='%23d8a24a'/%3E%3C/svg%3E">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<script type="application/ld+json">{ld_js}</script>
<style>{PAGE_CSS}</style>
</head>
"""


def website_ref():
    return {"@type": "WebSite", "@id": BASE + "/#website", "name": "Sounds of the Adriatic", "url": BASE + "/"}


def audio_object(p, m, page_url):
    obj = {
        "@type": "AudioObject", "@id": page_url + "#audio",
        "name": p["name"], "description": p["desc"],
        "url": page_url, "contentUrl": f"{BASE}/{p['audio']}",
        "license": lic_url(m), "author": {"@type": "Person", "name": f"{m['author']} (Freesound)"},
        "duration": iso_dur(m["duration_seconds"]),
        "encodingFormat": "audio/ogg; codecs=opus",
        "contentSize": str(m["filesize_bytes"]),
    }
    if m.get("recorded_at"):
        obj["datePublished"] = m["recorded_at"][:10]
    return obj


# ------------------------------------------------------------- pin pages
def build_pin_page(p):
    key = p["key"]
    page_url = f"{BASE}/s/{key}.html"
    m = by_key.get(key)
    has_audio = bool(p.get("audio") and m)
    title = f"{p['name']} — Sounds of the Adriatic"
    desc = f"{p['desc']} Recorded at {p['place']} ({p['lat']:.2f}°N {p['lon']:.2f}°E)."
    if not has_audio:
        desc += " Not yet recorded."

    graph = [website_ref(), {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Sounds", "item": BASE + "/#sounds"},
            {"@type": "ListItem", "position": 3, "name": p["name"], "item": page_url},
        ],
    }]
    if has_audio:
        graph.append(audio_object(p, m, page_url))
    else:
        graph.append({"@type": "CreativeWork", "@id": page_url + "#work", "name": p["name"],
                      "description": desc, "url": page_url})
    ld = {"@context": "https://schema.org", "@graph": graph}

    place = f"{esc(p['place'])} · {p['lat']:.2f}°N {p['lon']:.2f}°E"
    badge = "" if has_audio else '<span class="badge">not yet recorded</span>'
    if has_audio:
        player = f"""  <div class="row">
    <button class="play" id="play" data-file="{esc('/' + p['audio'])}">Play</button>
    <div class="track" id="track"><div class="fill" id="fill"></div></div>
    <span class="time" id="time"></span>
  </div>"""
        credit = (f'{esc(p["credit"])} <a href="{esc(p["source"])}" rel="noopener">source ↗</a><br>'
                  f'License: <a href="{esc(lic_url(m))}" rel="noopener">{esc(lic_short(m))}</a> · '
                  f'{fmt_dur(m["duration_seconds"])} · {kb(m["filesize_bytes"])} Opus mono · '
                  f'<a href="/{esc(p["audio"])}" download>download file ⇩</a>')
    else:
        player = '  <div class="row"><button class="play" disabled>Not yet recorded</button></div>'
        credit = "Not yet recorded — the maker's own recording is planned for this spot."
    bridge = ""
    if p.get("bridge"):
        bridge = (f'  <p class="bridge">{esc(p["bridge"]["text"])} '
                  f'<a href="{esc(p["bridge"]["url"])}" rel="noopener">{esc(p["bridge"]["label"])} ↗</a></p>')
    others = []
    for q in pins:
        cur = ' class="cur"' if q["key"] == key else ""
        label = f'{esc(q["name"])} — {esc(q["place"].split(",")[0])}'
        others.append(f'    <li><a href="/s/{q["key"]}.html"{cur}>{label}</a></li>')
    others = "\n".join(others)
    return page_head(title, desc, page_url, ld, CSP_PAGE, og_type="article") + f"""<body>
<header class="ph">
  <div class="kicker"><a href="/">Sounds of the Adriatic</a></div>
  <h1>{esc(p['name'])}</h1>{badge}
  <p class="meta">{place}</p>
</header>
<main class="pcard">
  <p class="desc">{esc(p['desc'])}</p>
{player}
{bridge}
  <div class="credit">{credit}</div>
  <p><a class="maplink" href="/#sound={key}">▶ Open this pin on the map</a></p>
</main>
<nav class="others" aria-label="All sounds">
  <h2>All sounds on the map</h2>
  <ul>
{others}
  </ul>
</nav>
{FOOTER}
<script>{PLAYER_JS}</script>
</body>
</html>
"""


# ---------------------------------------------------------- credits page
def build_credits_page():
    canonical = f"{BASE}/credits.html"
    ld = {"@context": "https://schema.org", "@graph": [website_ref(), {
        "@type": "WebPage", "@id": canonical + "#webpage", "url": canonical,
        "name": "Credits & licenses — Sounds of the Adriatic",
        "description": "Every sound on the map with creator, license, source URL, duration, file size and license-verification date.",
    }]}
    rows = []
    for p in pins:
        m = by_key.get(p["key"])
        if m:
            rows.append(
                "<tr>"
                f'<td><a href="/s/{p["key"]}.html">{esc(p["name"])}</a><br>{esc(p["place"])}</td>'
                f'<td>{esc(m["title"])}</td>'
                f'<td>{esc(m["author"])}</td>'
                f'<td><a href="{esc(lic_url(m))}" rel="noopener">{esc(lic_short(m))}</a></td>'
                f'<td><a href="{esc(m["source_url"])}" rel="noopener">Freesound ↗</a></td>'
                f'<td>{esc((m.get("recorded_at") or "")[:10])}</td>'
                f'<td>{fmt_dur(m["duration_seconds"])}</td>'
                f'<td>{kb(m["filesize_bytes"])}</td>'
                f'<td>{esc(m.get("license_verified", ""))}</td>'
                "</tr>")
        else:
            rows.append(
                "<tr>"
                f'<td><a href="/s/{p["key"]}.html">{esc(p["name"])}</a><br>{esc(p["place"])}</td>'
                f'<td colspan="8">Not yet recorded — planned</td>'
                "</tr>")
    rows.append(
        '<tr><td colspan="2"><b>Map coastline</b></td>'
        f'<td colspan="3">{esc(manifest["map"]["source"])}</td>'
        f'<td colspan="2">{esc(manifest["map"]["license"])}</td>'
        '<td></td><td></td><td></td></tr>')
    table = ("<table class=\"credits\"><thead><tr><th>Sound</th><th>Title</th><th>Creator</th>"
             "<th>License</th><th>Source</th><th>Recorded</th><th>Length</th><th>File</th><th>License verified</th>"
             "</tr></thead><tbody>" + "\n".join(rows) + "</tbody></table>")
    return page_head(
        "Credits & licenses — Sounds of the Adriatic",
        "Every sound on the Adriatic sound map with creator, license, source URL, duration, file size and license-verification date. Only CC0 and CC-BY are published.",
        canonical, ld, CSP_STATIC) + f"""<body>
<header class="ph">
  <div class="kicker"><a href="/">Sounds of the Adriatic</a></div>
  <h1>Credits &amp; licenses</h1>
  <p class="meta">Every published sound, its creator, license and source — verified per entry.</p>
</header>
<main class="pcard">
  <p class="lead">Only <b>CC0</b> and <b>CC-BY</b> recordings are published on this site. CC-BY-NC, CC-BY-ND and
  CC-BY-NC-ND are banned — non-commercial terms are unusable because the project promotes a commercial product.
  Machine-readable version: <a href="/LICENSE-MANIFEST.json" style="color:var(--accent)">LICENSE-MANIFEST.json</a>.</p>
  {table}
</main>
{FOOTER}
</body>
</html>
"""


# ------------------------------------------------------------- homepage LD
def build_home_ld():
    graph = [
        website_ref() | {"inLanguage": "en",
                        "description": "A sound map of the Croatian coast: free CC0/CC-BY field recordings of harbours, coves, wind, bells and open sea. Tap a pin, hear the place."},
        {"@type": "WebPage", "@id": BASE + "/#webpage", "url": BASE + "/",
         "name": "Sounds of the Adriatic — a sound map of the Croatian coast",
         "description": "11 free CC-BY field recordings of the Croatian coast. Tap a pin to listen.",
         "isPartOf": {"@id": BASE + "/#website"}, "primaryImageOfPage": BASE + "/og-image.png"},
    ]
    items = []
    pos = 0
    for p in pins:
        m = by_key.get(p["key"])
        if not (p.get("audio") and m):
            continue
        pos += 1
        items.append({"@type": "ListItem", "position": pos,
                      "item": audio_object(p, m, f"{BASE}/s/{p['key']}.html")})
    graph.append({"@type": "ItemList", "@id": BASE + "/#sounds", "name": "All sounds on the map",
                  "numberOfItems": len(items), "itemListElement": items})
    graph.append({
        "@type": "FAQPage", "@id": BASE + "/#faq",
        "mainEntity": [{"@type": "Question", "name": q["q"],
                        "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", q["a"])}}
                       for q in FAQ],
    })
    return {"@context": "https://schema.org", "@graph": graph}


# ------------------------------------------------------- homepage patches
def build_index_items():
    items = []
    for p in pins:
        m = by_key.get(p["key"])
        place = f"{p['place']} · {p['lat']:.2f}°N {p['lon']:.2f}°E"
        if p.get("audio") and m:
            credit = (f'{esc(lic_short(m))} · {esc(m["author"])} (Freesound) · {fmt_dur(m["duration_seconds"])} · '
                      f'<a href="{esc(p["source"])}" rel="noopener">source ↗</a> · '
                      f'<a href="/{esc(p["audio"])}" download>file ⇩</a> · '
                      f'<a href="/#sound={p["key"]}">on the map</a>')
        else:
            credit = "Not yet recorded — the maker's own recording is planned for this spot."
        items.append(
            "    <li>\n"
            f'      <a class="idx-link" href="/s/{p["key"]}.html">{esc(p["name"])}</a>'
            f'<span class="idx-place">{esc(place)}</span>\n'
            f"      <p>{esc(p['desc'])}</p>\n"
            f'      <p class="idx-credit">{credit}</p>\n'
            "    </li>")
    return "\n".join(items)


def build_faq_html():
    return "\n".join(
        f'<details>\n  <summary>{esc(q["q"])}</summary>\n  <p>{q["a"]}</p>\n</details>'
        for q in FAQ)


def build_llms_txt():
    lines = [
        "# Sounds of the Adriatic — llms.txt", "",
        "A sound map of the Croatian coast. A dark map of the Adriatic with pins;",
        "tapping a pin plays a field recording of that place — harbours, coves,",
        "wind in the rigging, church bells, cicadas, open-sea swell.", "",
        f"Site: {BASE}/",
        f"Credits & licenses (human-readable): {BASE}/credits.html",
        "Map data: Natural Earth (public domain).", "",
        "## License policy", "",
        "Only CC0 and CC-BY recordings are published (non-commercial and",
        "no-derivatives licenses are banned because the project promotes a",
        f"commercial product). Machine-readable list: {BASE}/LICENSE-MANIFEST.json", "",
        "## Sounds", "",
    ]
    for i, p in enumerate(pins, 1):
        m = by_key.get(p["key"])
        head = f"{i}. **{p['name']}** — {p['place']} ({p['lat']:.2f}°N {p['lon']:.2f}°E). {p['desc']}"
        if p.get("audio") and m:
            lines += [head,
                      f"   License: {m['license']} — creator: {m['author']} (Freesound).",
                      f"   Page: {BASE}/s/{p['key']}.html · on the map: {BASE}/#sound={p['key']} "
                      f"(also ?sound={p['key']}) · file: {BASE}/{p['audio']} "
                      f"({fmt_dur(m['duration_seconds'])}, {kb(m['filesize_bytes'])}, Opus mono)",
                      f"   Source: {p['source']}", ""]
        else:
            lines += [head, "   Status: not yet recorded (the maker's own recording is planned here).", ""]
    lines += [
        "## How to attribute", "",
        "If you link, embed or reuse a recording, credit the creator named on the",
        "pin/page and link the license URL shown there (CC-BY requires attribution;",
        "CC0 does not). Example: \"Wind in the rigging\" by zybil, CC-BY 4.0,",
        f"via {BASE}/s/senj-bura.html.", "",
        "## Related", "",
        "A MareSpot experiment — live Adriatic wind, shelter & sea temperature at https://marespot.com", "",
    ]
    return "\n".join(lines)


def build_sitemap():
    urls = [(f"{BASE}/", "1.0", "weekly")]
    urls.append((f"{BASE}/credits.html", "0.6", "monthly"))
    for p in pins:
        urls.append((f"{BASE}/s/{p['key']}.html", "0.8", "monthly"))
    body = "\n".join(
        f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{TODAY}</lastmod>\n"
        f"    <changefreq>{cf}</changefreq>\n    <priority>{pr}</priority>\n  </url>"
        for u, pr, cf in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + body + "\n</urlset>\n")


ROBOTS = f"""# Sounds of the Adriatic — {BASE}
# We want to be indexed by search engines AND AI/LLM crawlers.
User-agent: *
Allow: /

Sitemap: {BASE}/sitemap.xml
"""


# ------------------------------------------------------------------ patch
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
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print("wrote", path, len(content), "bytes")


def main():
    write("robots.txt", ROBOTS)
    write("sitemap.xml", build_sitemap())
    write("llms.txt", build_llms_txt())
    write("credits.html", build_credits_page())
    for p in pins:
        write(f"s/{p['key']}.html", build_pin_page(p))
    ld_js = '<script type="application/ld+json">' + json.dumps(
        build_home_ld(), ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + "</script>"
    patch_index([
        ("<!-- LD-JSON-BEGIN -->", "<!-- LD-JSON-END -->", ld_js),
        ("<!-- SOUND-INDEX-BEGIN -->", "<!-- SOUND-INDEX-END -->", build_index_items()),
        ("<!-- FAQ-BEGIN -->", "<!-- FAQ-END -->", build_faq_html()),
    ])


if __name__ == "__main__":
    main()
