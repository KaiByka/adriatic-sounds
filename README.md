# Sounds of the Adriatic

A sound map of the Croatian coast: harbor murmurs, cicada-filled pine coves, the bura humming through rigging, bells across the water, waves slapping limestone. Tap a pin, hear the place. A static site for GitHub Pages, built to earn backlinks for marespot.com, aimed at the field-recording, sound-map and ambient-content audiences your map projects don't reach.

## Why this project

1. **A different linking audience.** Baltic Lanes and charts.marespot.com recruit map/data curators; this recruits sound-map and field-recording communities, plus the huge ambient-content crowd ("3 hours of cove ambience" videos).
2. **The literal MareSpot bridge.** Hear the wind in the rigging, then check the shelter score.
3. **Unique assets.** Open-licensed recordings form the base layer, but the maker's own recordings (made on this coast) are the layer nobody else on the internet has.

## Live at

`https://sound.marespot.com` (GitHub Pages + Actions deploy, same pattern as charts: CNAME `sound` → `<username>.github.io`).

## Repo layout

```
adriatic-sounds/
├── README.md            ← this file
├── AGENTS.md            ← agent contract (licenses and audio budgets are the hard part)
├── site/                ← the deployed site (vanilla HTML/CSS/JS, no framework, no build)
│   ├── index.html       ← map, pin sheet, static sound index, About/FAQ, JSON-LD (SEO/GEO files below)
│   ├── s/<key>.html     ← one static SEO page per pin (player, credits, JSON-LD) — scripts/build-seo.py
│   ├── credits.html     ← human-readable license table from the manifest — scripts/build-seo.py
│   ├── robots.txt / sitemap.xml / llms.txt / 404.html / og-image.png / apple-touch-icon.png
│   ├── audio/           ← the sounds (committed, per-file budgeted)
│   ├── data/            ← pins.json, places.json, coastline.json (Natural Earth, public domain, pre-clipped)
│   └── LICENSE-MANIFEST.json  ← every sound + license + attribution + source URL
├── scripts/             ← build-time tools (build-seo.py, clip-coastline.py, make-og-image.py,
│                          make-icon.py, fetch-freesound.py) — rerun build-seo.py after changing pins/manifest
└── docs/
    └── sourcing.md      ← Freesound workflow, license rules, recording guide
```

## Working method

Agents do all coding; read `AGENTS.md` first. Sprint 1: replace placeholder sounds with >= 10 real CC0/CC-BY recordings from Freesound. Sprint 2: the maker's own recorded sounds and >= 20 pins. Sprint 3: launch kit (OG image, press stills, suggested captions).

Every push runs Lighthouse CI (mobile, `.lighthouserc.json`: performance >= 85, a11y/best-practices/SEO >= 90) against `site/` served locally, and the Pages deploy only runs if it passes.

## Attribution (footer, all pages)

"A MareSpot experiment — live Adriatic wind, shelter & sea temperature at [marespot.com](https://marespot.com)"

Per-pin caption: what you hear, where it was recorded, by whom, under which license, with a link to the source.
