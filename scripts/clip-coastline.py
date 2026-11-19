#!/usr/bin/env python3
"""Clip + simplify Natural Earth 10m land to the Adriatic bbox (with islands!).

Input : scripts/data/ne_10m_land.geojson  (Natural Earth 10m Land, public domain,
        https://www.naturalearthdata.com/downloads/10m-cultural-vectors/)
Output: site/data/coastline.json           (what the site actually ships)

The site's SVG viewBox is lon 12..20, lat 41.5..46.5 (see site/index.html).
We clip to a slightly larger bbox so land fills the map to its edges and the
coast glow / draw-on animation are not cut off at the viewBox border.

Rings are simplified with Douglas-Peucker at ~0.0022 deg (well under one map
pixel) and tiny slivers are dropped, keeping the shipped file small enough for
the <=2MB first-draw budget while keeping every island that is visible at map
scale (Krk, Cres, Hvar, Brac, Vis, Korcula, Mljet, Rab, Pag, ...).

Usage: python3 scripts/clip-coastline.py [tolerance_deg]
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "data", "ne_10m_land.geojson")
DST = os.path.join(HERE, "..", "site", "data", "coastline.json")

# viewBox bbox with a buffer (degrees)
LON0, LON1 = 10.8, 21.2
LAT0, LAT1 = 40.8, 47.2

# lon degrees are shorter than lat degrees at this latitude; scale for distances
COS = math.cos(math.radians(44.0))

TOL = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0001  # degrees (lat units)
MIN_PTS = 6        # drop rings that simplify to almost nothing
MIN_AREA = float(sys.argv[2]) if len(sys.argv) > 2 else 1e-6  # deg^2 sliver threshold


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


def dp_simplify(ring, tol):
    """Douglas-Peucker on a closed ring, in lon-scaled coordinate space."""
    pts = [(x * COS, y) for x, y in ring]
    n = len(pts)
    if n < 3:
        return ring
    keep = [False] * n
    keep[0] = keep[-1] = True
    stack = [(0, n - 1)]
    while stack:
        a, b = stack.pop()
        ax, ay = pts[a]
        bx, by = pts[b]
        dx, dy = bx - ax, by - ay
        norm = math.hypot(dx, dy)
        maxd, idx = -1.0, -1
        for i in range(a + 1, b):
            px, py = pts[i]
            if norm == 0:
                d = math.hypot(px - ax, py - ay)
            else:
                d = abs(dx * (py - ay) - dy * (px - ax)) / norm
            if d > maxd:
                maxd, idx = d, i
        if maxd > tol:
            keep[idx] = True
            stack.append((a, idx))
            stack.append((idx, b))
    return [ring[i] for i in range(n) if keep[i]]


def ring_area(ring):
    a = 0.0
    for i in range(len(ring) - 1):
        a += ring[i][0] * ring[i + 1][1] - ring[i + 1][0] * ring[i][1]
    return abs(a) / 2.0


def round_ring(ring, nd=3):
    return [[round(x, nd), round(y, nd)] for x, y in ring]


def main():
    with open(SRC) as f:
        world = json.load(f)

    polys = []  # list of polygons; each polygon = list of rings
    for feat in world["features"]:
        geom = feat["geometry"]
        if not geom:
            continue
        raw = ([geom["coordinates"]] if geom["type"] == "Polygon"
               else geom["coordinates"] if geom["type"] == "MultiPolygon" else [])
        for rings in raw:
            clipped = []
            for r in rings:
                c = clip_ring(r, LON0, LON1, LAT0, LAT1)
                if len(c) < 4:
                    continue
                s = dp_simplify(c, TOL)
                if len(s) >= MIN_PTS and ring_area(s) >= MIN_AREA:
                    clipped.append(round_ring(s))
            if clipped:
                polys.append(clipped)

    fc = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"name": "land"},
         "geometry": {"type": "MultiPolygon", "coordinates": polys}}
    ]}
    with open(DST, "w") as f:
        json.dump(fc, f, separators=(",", ":"))

    n_pts = sum(len(r) for p in polys for r in p)
    print(f"wrote {DST}: {len(polys)} polygon(s), {n_pts} points, "
          f"{os.path.getsize(DST)} bytes (tol={TOL})")


if __name__ == "__main__":
    main()
