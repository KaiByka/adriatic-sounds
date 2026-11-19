#!/usr/bin/env python3
"""Ingest sprint-2 sounds found by find-freesound-candidates.py (no API key needed).

For every entry in scripts/sprint2-selection.json:
  1. looks the sound up in scripts/data/candidates.json (already license- and
     geotag-verified there) and re-verifies CC0/CC-BY + bbox mechanically,
  2. downloads the public HQ preview mp3,
  3. transcodes to mono 24 kHz Opus 32k, trimmed to <= 90 s with a 4 s fade-out,
     <= 500 KB (same pipeline as fetch-freesound.py),
  4. writes site/audio/<key>.opus, updates site/data/pins.json and
     site/LICENSE-MANIFEST.json.

Usage: python3 scripts/ingest-scraped.py
Then:  python3 scripts/build-seo.py   (regenerate pin pages / sitemap / llms.txt)
"""
import json
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
SELECTION = ROOT / "scripts" / "sprint2-selection.json"
CANDIDATES = ROOT / "scripts" / "data" / "candidates.json"

UA = {"User-Agent": "Mozilla/5.0 adriatic-sounds-ingest/2.0"}
ALLOWED = {
    "creativecommons.org/publicdomain/zero/1.0/": "CC0 1.0",
    "creativecommons.org/licenses/by/4.0/": "CC-BY 4.0",
    "creativecommons.org/licenses/by/3.0/": "CC-BY 3.0",
}
BANNED = ("noncommercial", "-nc", "/nd", "noderivs", "all-rights-reserved", "sampling+")
LAT0, LAT1, LON0, LON1 = 41.5, 46.5, 12.0, 20.0
MAX_SECONDS = 90.0
TRIM_SECONDS = 89.0
MAX_BYTES = 500 * 1024
SAMPLE_RATE = 24000
BITRATE = "32k"
VERIFIED = "2026-11-19"


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"cmd failed: {' '.join(cmd)}\n{p.stderr[-2000:]}")
    return p.stdout


def probe(path):
    out = run(["ffprobe", "-v", "error", "-select_streams", "a:0",
               "-show_entries", "stream=codec_name,sample_rate,channels:format=duration,size",
               "-of", "json", str(path)])
    d = json.loads(out)
    st = d["streams"][0]
    return {"codec": st["codec_name"], "rate": int(st["sample_rate"]),
            "channels": int(st["channels"]), "duration": float(d["format"]["duration"]),
            "size": int(d["format"]["size"])}


def download(url, dest):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
        while True:
            chunk = r.read(65536)
            if not chunk:
                break
            f.write(chunk)


def main():
    sel = json.loads(SELECTION.read_text())
    cands = {c["freesound_id"]: c for c in json.loads(CANDIDATES.read_text())["candidates"]}
    pins = json.loads((SITE / "data" / "pins.json").read_text())
    by_key = {p["key"]: p for p in pins}
    manifest = json.loads((SITE / "LICENSE-MANIFEST.json").read_text())
    (SITE / "audio").mkdir(exist_ok=True)

    results = []
    for item in sel["pins"]:
        key = item["key"]
        c = cands.get(item["freesound_id"])
        if not c:
            raise SystemExit(f"REJECTED {key}: id {item['freesound_id']} not in verified candidates")
        # mechanical re-verification at ingest time
        lic_key = c["license_url"].lower().replace("https://", "").replace("http://", "")
        lic_name = ALLOWED.get(lic_key)
        if lic_name is None or any(b in lic_key for b in BANNED):
            raise SystemExit(f"REJECTED {key}: license {c['license_url']}")
        if not (LAT0 <= c["lat"] <= LAT1 and LON0 <= c["lon"] <= LON1):
            raise SystemExit(f"REJECTED {key}: geotag outside bbox")
        if not c.get("preview_hq_mp3"):
            raise SystemExit(f"REJECTED {key}: no preview")

        dur = min(float(c["duration"]), TRIM_SECONDS)
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / f"{c['freesound_id']}.mp3"
            download(c["preview_hq_mp3"], src)
            out = SITE / "audio" / f"{key}.opus"
            fade_start = max(0.0, dur - 4.0)
            run(["ffmpeg", "-y", "-v", "error", "-i", str(src),
                 "-t", f"{dur:.3f}", "-ac", "1", "-ar", str(SAMPLE_RATE),
                 "-af", f"afade=t=out:st={fade_start:.3f}:d=4",
                 "-c:a", "libopus", "-b:a", BITRATE, str(out)])
        info = probe(out)
        assert info["codec"] == "opus" and info["channels"] == 1, info
        assert info["duration"] <= MAX_SECONDS, info
        assert info["size"] <= MAX_BYTES, info

        credit = (f"“{c['title']}” — recorded by {c['username']} (Freesound), {lic_name}. "
                  f"Recorded at {c['lat']:.2f}N {c['lon']:.2f}E" +
                  (f" ({c['geotag_name']})" if c.get("geotag_name") else "") + ".")
        pin = {
            "key": key, "name": item["name"], "place": item["place"],
            "lat": item["lat"], "lon": item["lon"], "desc": item["desc"],
            "audio": f"audio/{key}.opus", "credit": credit, "source": c["page_url"],
        }
        if item.get("update") and key in by_key:
            by_key[key].update(pin)
        else:
            if key in by_key:
                raise SystemExit(f"pin key {key} already exists and is not marked update:true")
            pins.append(pin)
            by_key[key] = pins[-1]
        manifest["sounds"] = [s for s in manifest["sounds"] if s["key"] != key]
        manifest["sounds"].append({
            "key": key, "file": f"audio/{key}.opus", "title": c["title"], "author": c["username"],
            "license": f"{lic_name} ({c['license_url']})", "license_url": c["license_url"],
            "source_url": c["page_url"], "freesound_id": c["freesound_id"],
            "duration_seconds": round(info["duration"], 2), "filesize_bytes": info["size"],
            "sample_rate_hz": info["rate"], "resampled_to_hz": SAMPLE_RATE,
            "channels": 1, "codec": "opus",
            "geotag": {"lat": c["lat"], "lon": c["lon"]},
            "license_verified": VERIFIED,
        })
        results.append((key, c["freesound_id"], lic_name, round(info["duration"], 1), info["size"]))

    manifest["updated"] = VERIFIED
    (SITE / "data" / "pins.json").write_text(json.dumps(pins, indent=1, ensure_ascii=False) + "\n")
    (SITE / "LICENSE-MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    for r in results:
        print(f"OK {r[0]:<20} id={r[1]:>7} {r[2]:<9} {r[3]:>6}s {r[4]:>7} bytes")
    total = sum(s["filesize_bytes"] for s in manifest["sounds"])
    print(f"TOTAL audio: {total/1e6:.2f} MB, {len(manifest['sounds'])} sounds, {len(pins)} pins")


if __name__ == "__main__":
    main()
