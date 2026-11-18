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
├── site/                ← the deployed site (vanilla HTML/JS, no framework)
│   ├── index.html
│   ├── app/             ← map render, pin cards, audio player UI
│   ├── audio/           ← the sounds (committed, per-file budgeted)
│   ├── data/            ← pins.json, coastline.json (Natural Earth, public domain)
│   └── LICENSE-MANIFEST.json  ← every sound + license + attribution + source URL
└── docs/
    └── sourcing.md      ← Freesound workflow, license rules, recording guide
```

## Working method

Agents do all coding; read `AGENTS.md` first. Sprint 1: replace placeholder sounds with >= 10 real CC0/CC-BY recordings from Freesound. Sprint 2: the maker's own recorded sounds and >= 20 pins. Sprint 3: launch kit (OG image, press stills, suggested captions).

## Attribution (footer, all pages)

"A MareSpot experiment — live Adriatic wind, shelter & sea temperature at [marespot.com](https://marespot.com)"

Per-pin caption: what you hear, where it was recorded, by whom, under which license, with a link to the source.
