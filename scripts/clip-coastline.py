#!/usr/bin/env python3
"""Clip the Natural Earth 110m land polygon to the Adriatic bbox.

Input : scripts/data/ne-110m-land.json  (Natural Earth 110m Land, public domain,
        https://www.naturalearthdata.com/downloads/110m-cultural-vectors/)
Output: site/data/coastline.json        (what the site actually ships)

The site's SVG viewBox is lon 12..20, lat 41.5..46.5 (see site/index.html).
We clip to a slightly larger bbox so land fills the map to its edges and the
coast glow / draw-on animation are not cut off at the viewBox border.

Usage: python3 scripts/clip-coastline.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "data", "ne-110m-land.json")
DST = os.path.join(HERE, "..", "site", "data", "coastline.json")

# viewBox bbox with a buffer (degrees)
LON0, LON1 = 10.8, 21.2
LAT0, LAT1 = 40.8, 47.2


def clip_ring(ring, lon0, lon1, lat0, lat1):
    """Sutherland-Hodgman clip of one ring against the bbox rectangle."""
    def clip_edge(pts, inside, intersect):
        if not pts:
            return []
        out = []
        prev = pts[-1]
        for cur in pts:
            if inside(cur):
                if not inside(prev):
                    out.append(intersect(prev, cur))
                out.append(cur)
            elif inside(prev):
                out.append(intersect(prev, cur))
            prev = cur
        return out

    def ix_lon(v, a, b):  # intersect with vertical line x=v
        t = (v - a[0]) / (b[0] - a[0]) if b[0] != a[0] else 0.0
        return [v, a[1] + t * (b[1] - a[1])]

    def ix_lat(v, a, b):  # intersect with horizontal line y=v
        t = (v - a[1]) / (b[1] - a[1]) if b[1] != a[1] else 0.0
        return [a[0] + t * (b[0] - a[0]), v]

    pts = ring
    pts = clip_edge(pts, lambda p: p[0] >= lon0, lambda a, b: ix_lon(lon0, a, b))
    pts = clip_edge(pts, lambda p: p[0] <= lon1, lambda a, b: ix_lon(lon1, a, b))
    pts = clip_edge(pts, lambda p: p[1] >= lat0, lambda a, b: ix_lat(lat0, a, b))
    pts = clip_edge(pts, lambda p: p[1] <= lat1, lambda a, b: ix_lat(lat1, a, b))
    return pts


def round_ring(ring, nd=3):
    return [[round(x, nd), round(y, nd)] for x, y in ring]


def main():
    with open(SRC) as f:
        world = json.load(f)

    features = []
    for feat in world["features"]:
        geom = feat["geometry"]
        polys = []
        if geom["type"] == "Polygon":
            polys = [geom["coordinates"]]
        elif geom["type"] == "MultiPolygon":
            polys = geom["coordinates"]
        for rings in polys:
            # keep only rings that survive clipping
            clipped = [c for c in (round_ring(clip_ring(r, LON0, LON1, LAT0, LAT1)) for r in rings)
                       if len(c) >= 3]
            if clipped:
                features.append({
                    "type": "Feature",
                    "properties": {"name": feat.get("properties", {}).get("name", "land")},
                    "geometry": {"type": "Polygon", "coordinates": clipped},
                })

    fc = {"type": "FeatureCollection", "features": features}
    with open(DST, "w") as f:
        json.dump(fc, f, separators=(",", ":"))

    n_pts = sum(len(r) for ft in features for r in ft["geometry"]["coordinates"])
    print(f"wrote {DST}: {len(features)} polygon(s), {n_pts} points, "
          f"{os.path.getsize(DST)} bytes")


if __name__ == "__main__":
    main()
