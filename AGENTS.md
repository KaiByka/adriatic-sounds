# AGENTS.md — Sounds of the Adriatic agent contract

You are a coding agent working on "Sounds of the Adriatic". Read this before every task. When a task conflicts with this file, this file wins.

## Mission

A static sound map of the Croatian coast: pins on a dark coastline map that play field recordings of the place — harbors, coves, wind, bells, the sea itself. Published on GitHub Pages at `sound.marespot.com`. Purpose: earn backlinks for marespot.com from sound-map, field-recording and ambient-content audiences. It is a listening gallery, not a product.

## Non-negotiable hard rules

1. **Static output only.** No backend, no accounts at runtime, no analytics beyond GoatCounter (async, no cookies, enabled only once the human provides the code). Deploy = GitHub Actions publishing the `site/` folder.
2. **Nothing auto-plays, ever.** Audio plays only after a user gesture on that specific pin. No background loops, no preload="auto", no autoplay of any kind. First page load requests zero audio bytes; every audio file loads only when its pin's play button is tapped for the first time (fetch-then-cache in-session is fine).
3. **Audio licensing is stricter than image licensing.** The only acceptable licenses are **CC0 and CC-BY**. **CC BY-NC, CC BY-ND and CC BY-NC-ND are banned** — non-commercial terms are unusable because the project promotes a commercial product. Every shipped sound must be listed in `site/LICENSE-MANIFEST.json` with: pin key, title, creator (Freesound username or "MareSpot" for own recordings), license (exact name + URL), source URL, duration, filesize, and the date you verified the license. If you cannot verify a sound's license, do not ship it. Attribution must be *rendered on the pin card*, not buried in the manifest only.
4. **Audio budget.** Per sound: <= 90 seconds, mono, Opus or mp3, <= 500 KB (Opus 32k mono preferred). All sounds together <= 60 MB. A pin never loads audio until played.
5. **Build-time API keys only.** The Freesound API key lives in an environment variable during the ingestion script's run; it never enters the repo, the site output, or any log. Nothing at runtime uses any API: all audio is committed files.
6. **Mobile-first, dark theme, headphones intended.** Tap targets >= 44px. The map UI must behave with audio session interruptions (headphone unplug pauses sound). Lighthouse mobile >= 85; first draw (HTML+CSS+JS+map data, NO audio) <= 2 MB transferred.
7. **MareSpot linkage, exact and minimal.** Footer credit on all pages: "A MareSpot experiment — live Adriatic wind, shelter & sea temperature at marespot.com" (text link). One contextual bridge at most, on the bura/wind pin card, one sentence linking wind sound to live wind data. Nothing more without human approval.
8. **Deep-linkable pins.** Every pin reachable at `#sound=<key>`; state (selected pin) serializes to the URL hash.
9. **Honest captions.** A pin says what the sound is, where and when it was recorded, by whom. Placeholder/synthesized sounds must be labeled as placeholders in the visible caption, never presented as real recordings. If a location has no recording yet, the pin says "not yet recorded" — never a fake.
10. **Map source:** Natural Earth (public domain), same policy as charts/baltic. No runtime tile servers.

## Tech stack (fixed, deliberately boring)

- Vanilla HTML + TypeScript + Vite, no framework. Map = SVG/canvas drawn from committed GeoJSON (equirectangular projection over the Adriatic bbox is fine; no map library needed at this scale). Audio via a single `<audio>` element managed by the app.
- Ingestion: Python or Node script in `scripts/`, run at build time by the human/CI with the API key in env; commits go through review like everything else.
- Deploy: `.github/workflows/deploy.yml` publishing `site/` via actions/deploy-pages, Pages source = GitHub Actions.

## Definition of done

A visitor on a phone opens sound.marespot.com, sees a dark Adriatic coast with pins, taps "the bura in the rigging" and hears wind — with headphones, the sound starting only because they tapped. Tapping again stops it. Every playing pin shows its creator, license and source link. No sound ever plays without a tap. First load requests no audio.
