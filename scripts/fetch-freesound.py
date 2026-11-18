#!/usr/bin/env python3
"""
fetch-freesound.py — Sprint 1 ingestion for "Sounds of the Adriatic".

Reads FREESOUND_API_KEY from the environment (NEVER committed, NEVER logged).
For every pin in scripts/sprint1-selection.json:
  1. fetches the sound detail from the Freesound API,
  2. mechanically rejects anything whose license is not CC0 or CC-BY
     (NC / ND / unverifiable are all rejected),
  3. rejects sounds whose geotag is outside the Adriatic bbox,
  4. downloads the public HQ preview and transcodes to mono 24 kHz Opus 32k,
     trimmed to <= 90 s with a gentle fade-out, <= 500 KB,
  5. writes site/audio/<key>.opus, updates site/data/pins.json and
     site/LICENSE-MANIFEST.json.

Usage:  FREESOUND_API_KEY=... python3 scripts/fetch-freesound.py
"""
import certifi, json, os, ssl, subprocess, sys, tempfile, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
SELECTION = ROOT / "scripts" / "sprint1-selection.json"

KEY = os.environ.get("FREESOUND_API_KEY", "")
if not KEY:
    sys.exit("FREESOUND_API_KEY is not set. Export it for this run only; never commit it.")
CTX = ssl.create_default_context(cafile=certifi.where())

BBOX = {"min_lon": 12.0, "max_lon": 20.0, "min_lat": 41.5, "max_lat": 46.5}
ALLOWED_LICENSES = {
    "http://creativecommons.org/publicdomain/zero/1.0/": "CC0 1.0",
    "https://creativecommons.org/publicdomain/zero/1.0/": "CC0 1.0",
    "http://creativecommons.org/licenses/by/4.0/": "CC-BY 4.0",
    "https://creativecommons.org/licenses/by/4.0/": "CC-BY 4.0",
    "http://creativecommons.org/licenses/by/3.0/": "CC-BY 3.0",
    "https://creativecommons.org/licenses/by/3.0/": "CC-BY 3.0",
}
BANNED_MARKERS = ("noncommercial", "nc", "nd", "noderivs", "all-rights-reserved")

MAX_SECONDS = 90.0          # hard budget per sound
TRIM_SECONDS = 89.0         # trim target (Opus adds ~65 ms padding, keep under 90 s)
MAX_BYTES = 500 * 1024
SAMPLE_RATE = 24000         # encode-time input rate; Opus always decodes at 48 kHz
BITRATE = "32k"
VERIFIED = "2026-11-18"


def api(path, params=None):
    url = "https://freesound.org/apiv2" + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"Token {KEY}"})
    with urllib.request.urlopen(req, timeout=30, context=CTX) as r:
        return json.load(r)


def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "adriatic-sounds-ingest/1.0"})
    with urllib.request.urlopen(req, timeout=60, context=CTX) as r, open(dest, "wb") as f:
        while True:
            chunk = r.read(65536)
            if not chunk:
                break
            f.write(chunk)


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


def main():
    sel = json.loads(SELECTION.read_text())
    pins = json.loads((SITE / "data" / "pins.json").read_text())
    by_key = {p["key"]: p for p in pins}
    manifest = json.loads((SITE / "LICENSE-MANIFEST.json").read_text())
    manifest["sounds"] = [s for s in manifest.get("sounds", []) if not s.get("note", "").startswith("Placeholder")]
    manifest["updated"] = VERIFIED
    (SITE / "audio").mkdir(exist_ok=True)

    results = []
    for item in sel["pins"]:
        key = item["key"]
        sid = item["freesound_id"]
        s = api(f"/sounds/{sid}/")
        lic_url = s.get("license", "")
        lic_name = ALLOWED_LICENSES.get(lic_url)
        if lic_name is None or any(m in lic_url.lower() for m in BANNED_MARKERS):
            raise SystemExit(f"REJECTED {key}: license not CC0/CC-BY or unverifiable: {lic_url!r}")
        gt = s.get("geotag") or ""
        try:
            lat, lon = float(gt.split()[0]), float(gt.split()[1])
        except Exception:
            raise SystemExit(f"REJECTED {key}: no geotag, cannot verify bbox")
        if not (BBOX["min_lat"] <= lat <= BBOX["max_lat"] and BBOX["min_lon"] <= lon <= BBOX["max_lon"]):
            raise SystemExit(f"REJECTED {key}: geotag {lat},{lon} outside bbox")

        preview = (s.get("previews") or {}).get("preview-hq-mp3")
        if not preview:
            raise SystemExit(f"REJECTED {key}: no preview available")
        dur = min(float(s["duration"]), TRIM_SECONDS)
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / f"{sid}.mp3"
            download(preview, src)
            out = SITE / "audio" / f"{key}.opus"
            # mono, 24 kHz, Opus 32k, trim to <=90s, gentle 4s fade-out so the cut is never mid-sample
            fade_start = max(0.0, dur - 4.0)
            run(["ffmpeg", "-y", "-v", "error", "-i", str(src),
                 "-t", f"{dur:.3f}", "-ac", "1", "-ar", str(SAMPLE_RATE),
                 "-af", f"afade=t=out:st={fade_start:.3f}:d=4",
                 "-c:a", "libopus", "-b:a", BITRATE, str(out)])
        info = probe(out)
        assert info["codec"] == "opus" and info["channels"] == 1, info
        assert info["duration"] <= MAX_SECONDS, info
        assert info["size"] <= MAX_BYTES, info
        assert info["rate"] in (SAMPLE_RATE, 48000), info  # Opus decodes at 48 kHz; encoded from 24 kHz

        title = s.get("name", "").strip()
        author = s.get("username", "")
        source = s.get("url", f"https://freesound.org/people/{author}/sounds/{sid}/")
        credit = (f"“{title}” — recorded by {author} (Freesound), {lic_name}. "
                  f"Recorded {str(s.get('created', ''))[:10]} at {lat:.2f}N {lon:.2f}E.")
        p = by_key[key]
        p.update({
            "name": item["name"], "place": item["place"],
            "lat": item["lat"], "lon": item["lon"], "desc": item["desc"],
            "audio": f"audio/{key}.opus", "credit": credit, "source": source,
        })
        p.pop("placeholder", None)
        manifest["sounds"].append({
            "key": key, "file": f"audio/{key}.opus", "title": title, "author": author,
            "license": f"{lic_name} ({lic_url})", "license_url": lic_url,
            "source_url": source, "freesound_id": sid,
            "duration_seconds": round(info["duration"], 2), "filesize_bytes": info["size"],
            "sample_rate_hz": info["rate"], "resampled_to_hz": SAMPLE_RATE,
            "channels": 1, "codec": "opus",
            "recorded_at": s.get("created"), "geotag": {"lat": lat, "lon": lon},
            "license_verified": VERIFIED,
        })
        results.append((key, sid, lic_name, round(info["duration"], 1), info["size"]))

    (SITE / "data" / "pins.json").write_text(json.dumps(pins, indent=1, ensure_ascii=False) + "\n")
    (SITE / "LICENSE-MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    for r in results:
        print(f"OK {r[0]:<20} id={r[1]:>7} {r[2]:<9} {r[3]:>6}s {r[4]:>7} bytes")
    total = sum(r[4] for r in results)
    print(f"TOTAL audio: {total} bytes ({total/1e6:.2f} MB), {len(results)} sounds")


if __name__ == "__main__":
    main()
