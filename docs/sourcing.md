# Where the sounds come from (and what you may legally ship)

## The three layers, in build order

### Layer 1 — Freesound (base layer, sprint 1)

Freesound (freesound.org) is a 20-year collaborative archive of field recordings with an API that supports **geotag and license filters** — this is the primary ingesting source.

Workflow (`scripts/fetch-freesound`, needs `FREESOUND_API_KEY` env var, never committed):

1. Search: `web_search`/`content_search` for terms (waves, sea, wind, harbor, seagulls, cicadas, harbour, bells, port, rigging, marina, night, crickets, church bells) with:
   - `min_lon=12, max_lon=20, min_lat=41.5, max_lat=46.5` (Adriatic bbox)
   - filter license: Creative Commons 0 **or** Creative Commons Attribution only
   - filter duration <= 180s, prefer mono 44.1/48 kHz sources
2. For each hit, record: id, username, license, geotag, duration; download preview (hq) or original per size; transcode to Opus 32k mono or mp3 64k mono, trim to <= 90s where sensible (keep the natural head/tail, never mid-sample cuts).
3. Write the entry into `site/LICENSE-MANIFEST.json` and create the pin in `site/data/pins.json` only if the geotag is meaningful (in or near the coast). If geotag is missing but the recording is clearly Adriatic/coastal-generic (username/description evidence), pin it to a *representative* location and say so in the caption ("location approximate").
4. **Reject list, applied mechanically:** `cc-by-nc`, `cc-by-nd`, `cc-by-nc-nd` in any form. When in doubt: skip, not risk — there is no shortage of CC0/BY sea sounds.

Known quirk: Freesound's coverage of *Croatia specifically* is thin; most Adriatic recordings are from Italian and Slovenian coasts. That is fine and honest (the sea has no border), but captions must state where each recording was actually made.

### No-API-key path (used for sprint 2)

When `FREESOUND_API_KEY` is not available, `scripts/find-freesound-candidates.py` scrapes the **public**
search (with `license:"Creative Commons 0"` / `"Creative Commons Attribution"` + `duration:[0 TO 180]`
filters) and each sound page, then mechanically verifies per sound: license exactly CC0/CC-BY, geotag
inside the Adriatic bbox, duration, preview URL. Output: `scripts/data/candidates.json`.
`scripts/ingest-scraped.py` then downloads the public HQ previews and transcodes them with the exact
same pipeline as `fetch-freesound.py` (mono 24 kHz Opus 32k, <= 90 s, <= 500 KB) for the entries in
`scripts/sprint2-selection.json`. The same mechanical rejects apply at ingest time. The API path
remains preferred when a key is available (it returns authoritative metadata).

### Layer 2 — the maker's own recordings (the unique layer, sprint 2)

Recorded on the Croatian coast by the human owner. License: "© MareSpot, used with permission" in the manifest (self-owned, or simply "recorded by the author"). This layer needs no external licensing at all — that is its point. The recording guide (also send to the human):

- Phone voice memos are fine: hold still, 30–90 seconds, wind muffling guarded (phone in a sock works), mono, no talking.
- Targets, roughly one evening + one morning: waves on stone in a quiet cove; cicadas + pine shade; harbor murmur at dusk (Hvar, Riva Split, Rovinj); church bells across water at noon; **the sea organ in Zadar** (this is the single best sound-object on the coast — record at various sea states); bura in rigging (Senj or any marina during a bura day); a ferry arriving; crickets at night.
- Label each file `place_shortlabel.wav`, note exact location + date; the agent transcodes and manifests them like any other entry.

### Layer 3 — the sea itself (stretch, after launch)

Open research datasets exist (e.g. Eastern Mediterranean odontocete whistle clips on Zenodo; low-cost passive acoustic monitoring sets). Rules: **verify the specific record's license before shipping** (Zenodo records vary; CC-BY is common, CC0 exists, some are "for research only" — those are banned), attribute the dataset + DOI on the pin card, and present scientific recordings exactly as what they are ("bottlenose dolphin whistles recorded for a monitoring study, not a soundscape").

## What NOT to use

- **Live hydrophone streams (LIDO/listentothedeep etc.):** live external streams break the static-site rule and their reuse terms are unclear. No.
- **Radio Aporee:** its soundmap content is NC-licensed almost throughout. No.
- **YouTube/videogame/TV audio, sampled music, anything "found on the internet":** no. Freesound CC0/BY + own recordings + verified research datasets, nothing else.

## Attribution text pattern (rendered on every pin card)

"Waves on limestone, Pine cove, Vis — recorded by mariokt (Freesound), CC-BY 4.0, [source link]" or "Bura in the rigging, Senj — recorded by the author (MareSpot)."
