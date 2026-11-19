# Awesome-list PR targets (prepared, not yet submitted)

Four alive, topically-fitting awesome lists. For each: exact section, anchor line to
insert after, and the exact entry line (format matched to the list's style).
Automation: `scripts/submit-awesome-prs.sh` (needs `gh auth login` once).
Manual alternative: fork → branch → paste the entry after the anchor → PR.

PR title (all): `Add Sounds of the Adriatic — sound map of the Croatian coast`

PR body (all):
> Adds [Sounds of the Adriatic](https://sound.marespot.com/) — a dark, static sound map of the
> Croatian coast: tap a pin to play a field recording. 11 sounds, all CC0/CC-BY with creator,
> license and source credited on every pin (see [credits page](https://sound.marespot.com/credits.html)).
> Map coastline: Natural Earth (public domain). Audio loads only on tap. No tracking.
>
> Happy to adjust wording/placement to fit the list.

| # | Repo | Stars / alive | Section | Anchor line (insert after) | Entry line |
|---|---|---|---|---|---|
| 1 | `landscape82/awesome-sound-design-resources` | 16★ / PRs merged 2026-11-17 | `## 🌲 Field Recording & Capture` | `- **[radio aporee ::: maps](https://aporee.org/maps/)** 🆓 🌐 - Global sound map...` | `- **[Sounds of the Adriatic](https://sound.marespot.com/)** 🆓 🌐 - Dark sound map of the Croatian coast: tap a pin to play free CC0/CC-BY field recordings (creator + license on every pin).` |
| 2 | `sshuair/awesome-gis` | 5632★ / pushed 2026-07 | `## Amazing Map Sites` | `- [CHATTY MAPS](...) - the sounds map of city.` | `- [Sounds of the Adriatic](https://sound.marespot.com/) - Sound map of the Croatian coast: tap a pin to hear CC0/CC-BY field recordings (harbours, coves, wind, bells).` |
| 3 | `Spacial/awesome-arts` | 48★ / pushed 2026-10 | audio section (near "SOUNDS OF THE FOREST" soundmap) | `- [SOUNDS OF THE FOREST](...)` | `- [Sounds of the Adriatic](https://sound.marespot.com/): a dark sound map of the Croatian coast — free CC-BY field recordings, tap a pin to listen.` |
| 4 | `fmariv/awesome-web-gis-resources` | 15★ / pushed 2026-11-15 | `## Geospatial Visualization & Storytelling` | `- [Flourish](https://flourish.studio/) — ...` | `- [Sounds of the Adriatic](https://sound.marespot.com/) — interactive sound map of the Croatian coast: tap a pin to play CC0/CC-BY field recordings.` |

Notes:
- #1 is linted (awesome-lint + link-check CI) — the bold-link + 🆓 🌐 + " - desc." format above matches its rules.
- #2 has a ContributingGuidelines.md — one line per resource, PR welcome.
- Checked as dead/don't bother: `DolbyIO/awesome-audio` (last PR 2023), `hwclass/awesome-sound` (2021).

## Submitted (2026-11-19, via scripts/submit-awesome-prs.sh) — all OPEN, 1 link line each in the diff

1. https://github.com/landscape82/awesome-sound-design-resources/pull/87
2. https://github.com/sshuair/awesome-gis/pull/341
3. https://github.com/Spacial/awesome-arts/pull/10
4. https://github.com/fmariv/awesome-web-gis-resources/pull/9

Follow-up: watch for maintainer comments; if merged, the backlinks go live on github.com.
Re-run the script later for more targets — it skips any with an already-open PR.
