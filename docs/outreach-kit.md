# Launch / backlink outreach kit (Sprint 3)

Goal (from README): earn backlinks for marespot.com from the **sound-map, field-recording and
ambient-content** audiences. Target: **10–30 quality referring domains in the first 3 months**.

Everything you need is already live and linkable:

- Map: https://sound.marespot.com/
- Per-sound pages (best link targets — unique content + metadata): https://sound.marespot.com/s/&lt;key&gt;.html
- Credits/licenses page (trust signal for the CC community): https://sound.marespot.com/credits.html
- Share card: https://sound.marespot.com/og-image.png · machine-readable brief: https://sound.marespot.com/llms.txt

## The pitch (pick by channel length)

**25 words**
> Sounds of the Adriatic — a dark sound map of the Croatian coast. 11 free CC-BY field recordings; tap a pin, hear the place. https://sound.marespot.com/

**60 words**
> I built a sound map of the Croatian coast: a night-dark map of the Adriatic with pins you tap to hear real field recordings — harbour murmur, cicadas in the pines, the bura in the rigging, church bells across the water. Every sound is CC0/CC-BY with the creator credited on the pin. Nothing autoplays. https://sound.marespot.com/

**150 words (newsletter / blog pitch)**
> Sounds of the Adriatic (https://sound.marespot.com/) is a static sound map of the Croatian coast: a dark map with 12 pins, 11 of them playing real field recordings — wind in marina rigging, tide bubbling between limestone rocks, church bells and cicadas in Betina, a car ferry crossing the Kvarner, crickets at night, open-sea swell. Each pin links to its own page with the full story: where and when it was recorded, by whom, under which license (only CC0/CC-BY are used — NC/ND are deliberately excluded), with a link to the original on Freesound and the raw file. The map itself is drawn from Natural Earth (public domain); the audio loads only when a pin is tapped. There's a credits page (…/credits.html) and a machine-readable license manifest (…/LICENSE-MANIFEST.json) if you want to verify any of it. It's a MareSpot experiment — the same team runs live Adriatic wind/shelter/sea-temperature data at marespot.com.

## Per-pin one-liners (drop into posts, lists, comments)

- **The sea organ** — Zadar — not yet recorded — https://sound.marespot.com/s/zadar-organ.html
- **Wind in the rigging** — Marina Kornati, Biograd na Moru — CC-BY 4.0 by zybil — https://sound.marespot.com/s/senj-bura.html
- **Tide between the rocks** — Near Rogoznica — CC-BY 4.0 by artsybadboi — https://sound.marespot.com/s/vis-cove.html
- **Bells and cicadas in Betina** — Betina, island of Murter — CC-BY 4.0 by Satoration — https://sound.marespot.com/s/sibenik-bells.html
- **Old-town murmur with gulls** — Starigrad, Pag — CC-BY 3.0 by dkustic — https://sound.marespot.com/s/hvar-riva.html
- **Evening on the promenade** — Lapad, Dubrovnik — CC-BY 4.0 by miastodzwiekow — https://sound.marespot.com/s/split-riva.html
- **Island channel ambience** — Brijuni islands — CC-BY 4.0 by VlatkoBlazek — https://sound.marespot.com/s/rovinj-harbor.html
- **Open-sea swell** — Open Adriatic, 42.65N 14.04E — CC-BY 4.0 by Loredenii — https://sound.marespot.com/s/kornati-open.html
- **Old town at dusk** — Dubrovnik old town — CC-BY 4.0 by miastodzwiekow — https://sound.marespot.com/s/dubrovnik-port.html
- **Ferry with gulls aboard** — Kvarner channel near Rab — CC-BY 3.0 by dkustic — https://sound.marespot.com/s/krk-ferry.html
- **Crickets at night** — Hills above Dramalj, near Crikvenica — CC-BY 3.0 by Nonoo — https://sound.marespot.com/s/lastovo-night.html
- **Cicadas in the pines** — Brač island — CC-BY 4.0 by VlatkoBlazek — https://sound.marespot.com/s/stari-grad-cicadas.html

(Regenerate this list from `site/data/pins.json` + `site/LICENSE-MANIFEST.json` when pins change.)

## Where to post, in order

| # | Venue | Format | Notes |
|---|---|---|---|
| 1 | **Awesome-list PRs** (GitHub) — see the concrete repo list below | one-line PR adding the link + 25-word pitch | highest-quality, permanent, dofollow links; read each repo's contribution rules |

**Prepared and ready to submit:** `docs/awesome-pr-targets.md` lists 4 vetted, alive lists with the exact section, anchor line and entry line for each; `scripts/submit-awesome-prs.sh` forks → branches → inserts → pushes → opens all PRs in one run (needs `gh auth login -h github.com` once; insertion logic tested against the live READMEs). Run: `bash scripts/submit-awesome-prs.sh`.

Concrete awesome-list targets (verified to exist; check they're still active — recent commits/merged PRs — before PRing):

- `landscape82/awesome-sound-design-resources` — has a **Maps** section (lists radio aporee's sound map there) → add us next to it
- `DolbyIO/awesome-audio` — the big curated audio-resources list (maps/sound-maps section)
- `hwclass/awesome-sound` — curated sound & audio packages/resources
- `GareBear99/awesome-audio-lists` — index of audio awesome-lists
- `github.com/topics/field-recording` — browse repos tagged `field-recording`; some keep resource lists in READMEs
- search GitHub yourself: `https://github.com/search?q=awesome+sound+map&type=repositories` and `q=awesome+field+recording`, `q=awesome+open+data+audio`

PR line format (match each repo's style):
> `- [Sounds of the Adriatic](https://sound.marespot.com/) — dark sound map of the Croatian coast; 11 free CC-BY field recordings, tap a pin to play.`

| 2 | **r/fieldrecording** (Reddit) | post in the designated self-promo/share thread (check weekly pinned thread rules) | use the 60-word pitch + homepage link; offer the credits page. Engage in comments |
| 3 | **Freesound forum / groups** (freesound.org) | a post in the sound-map/geotagging groups: "we built a sound map from CC0/CC-BY Freesound recordings — every sound credited and linked back" | links to /credits.html shine here; do NOT re-upload others' sounds as your own |
| 4 | **Hacker News — Show HN** | title: "Show HN: Sounds of the Adriatic — a sound map of the Croatian coast" + 60-word pitch | post from the human's account (karma); be present in the thread for 2h |
| 5 | **r/ambientmusic, r/croatia, r/sailing** (Reddit) | one relevant post each max, only where genuinely on-topic (bura pin → r/sailing) | follow each sub's self-promo rules; many ban direct links outside megathreads |
| 6 | **Field-recording / ambient newsletters & blogs** (search "field recording newsletter", "soundmap blog", "sonic cartography") | 150-word pitch | personal, specific email; mention what's in it for their readers |
| 7 | **Travel/Croatia blogs** (English-language Dalmatia guides) | offer the map + a specific pin (e.g. Dubrovnik old town at dusk) as a resource | natural fit: "listen before you visit" |
| 8 | **Wikimedia Commons** (optional, human account) | cross-post the CC-BY files with proper attribution templates | extra reach + a .commons backlink; only CC-BY files, never NC |
| 9 | **Sonic-cartography / academic lists** (university course pages, research group resource lists) | short pitch + credits page | .edu links are gold for trust |

## Channel copy

**Ready-to-post, per-channel drafts live in `docs/social-posts.md`** — tailored bodies for
r/fieldrecording (weekly thread only), r/croatia, r/ambientmusic, r/sailing (reply-only, no
standalone post), the Freesound "Freesound Project" forum, Show HN, newsletter emails, and an
X/Mastodon thread — each with the community's rules noted and a posting-time tip.

Quick versions:

**Show HN title**
> Show HN: Sounds of the Adriatic — a sound map of the Croatian coast

## Ground rules

1. **Disclose**: you are the maker. Say so in the first line where the venue asks.
2. **One post per venue.** No cross-posting spam, no link chains, no bought links.
3. **License-correct sharing**: link to our pages/files; never strip attribution; never imply the recordings are yours.
4. **Honesty**: Zadar sea organ is marked "not yet recorded" — keep it that way in copy; don't oversell.
5. **marespot.com mention**: one line max per post (the footer already carries it on-site; rule 7 of AGENTS.md applies to the site, and the same spirit applies in outreach).
6. Reply to every comment for the first 2 hours; fix what people find.

## Tracking

Log every placement (check GSC → Links monthly):

| Date | Venue | URL posted | Link live? | Notes |
|---|---|---|---|---|
| | | | | |

Review after 30/60/90 days: which venues produced clicks (GSC Performance) vs pure links (Links report). Double down on what works; drop what doesn't.
