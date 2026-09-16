"""Turn OCHA's Madagascar region boundaries into the home page's SVG map data.

    python tools/build_madagascar_map.py mdg_admin1.geojson

Source: "Madagascar - Subnational Administrative Boundaries" (COD-AB) on
https://data.humdata.org/dataset/cod-ab-mdg — BNGRC via OCHA, CC BY-IGO 3.0.
Take `mdg_admin1.geojson` from its GeoJSON archive.

Standard library only. Outlines are projected equirectangularly (corrected for
Madagascar's latitude), simplified with Douglas-Peucker, and small islets are
dropped; the result is tens of kilobytes instead of 18 MB.
"""
import argparse
import json
import math
from pathlib import Path

OUTPUT = Path(__file__).resolve().parent.parent / "ckanext" / "nice_ui" / "data" / "madagascar_regions.json"
HEIGHT = 1000.0

# OCHA only ships French names. Official Malagasy spellings for display; every
# spelling is also an alias used to match dataset tags to regions.
NAMES = {
    "MG11": ("Analamanga", []),
    "MG12": ("Vakinankaratra", []),
    "MG13": ("Itasy", []),
    "MG14": ("Bongolava", []),
    "MG21": ("Matsiatra Ambony", ["Haute Matsiatra", "Haute-Matsiatra"]),
    "MG22": ("Amoron'i Mania", ["Amoron I Mania", "Amoron'i Mania"]),
    "MG24": ("Ihorombe", []),
    "MG25": ("Atsimo-Atsinanana", ["Atsimo Atsinanana"]),
    "MG26": ("Vatovavy", []),
    "MG27": ("Fitovinany", []),
    "MG31": ("Atsinanana", []),
    "MG32": ("Analanjirofo", []),
    "MG33": ("Alaotra-Mangoro", ["Alaotra Mangoro"]),
    "MG34": ("Ambatosoa", []),
    "MG41": ("Boeny", []),
    "MG42": ("Sofia", []),
    "MG43": ("Betsiboka", []),
    "MG44": ("Melaky", []),
    "MG51": ("Atsimo-Andrefana", ["Atsimo Andrefana"]),
    "MG52": ("Androy", []),
    "MG53": ("Anosy", []),
    "MG54": ("Menabe", []),
    "MG71": ("Diana", []),
    "MG72": ("Sava", []),
}


def rings(geometry):
    polygons = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
    for polygon in polygons:
        yield polygon[0]  # outer ring; region interiors have no meaningful holes


def thin(points, tolerance):
    """Drop points within `tolerance` of the last kept one. Douglas-Peucker alone
    is far too slow on OCHA's rings (Diana's coastline has ~150k vertices)."""
    kept = [points[0]]
    for x, y in points[1:-1]:
        if math.hypot(x - kept[-1][0], y - kept[-1][1]) >= tolerance:
            kept.append((x, y))
    kept.append(points[-1])
    return kept


def simplify(points, tolerance):
    """Iterative Douglas-Peucker, after a radial-distance pass."""
    points = thin(points, tolerance / 2)
    if len(points) < 4:
        return points
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        start, end = stack.pop()
        (x1, y1), (x2, y2) = points[start], points[end]
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy)
        worst, index = -1.0, None
        for i in range(start + 1, end):
            x0, y0 = points[i]
            if length:
                distance = abs(dy * x0 - dx * y0 + x2 * y1 - y2 * x1) / length
            else:
                # A closed ring starts and ends on the same point: the "segment"
                # is a point, and line distance would be 0 for every vertex.
                distance = math.hypot(x0 - x1, y0 - y1)
            if distance > worst:
                worst, index = distance, i
        if index is not None and worst > tolerance:
            keep[index] = True
            stack.extend(((start, index), (index, end)))
    return [p for p, k in zip(points, keep) if k]


def area(points):
    return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1]))) / 2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("geojson")
    parser.add_argument("--tolerance", type=float, default=0.9, help="in viewBox units (height 1000)")
    parser.add_argument("--min-area", type=float, default=15.0, help="islets smaller than this are dropped")
    args = parser.parse_args()

    features = json.load(open(args.geojson))["features"]
    lons = [c[0] for f in features for r in rings(f["geometry"]) for c in r]
    lats = [c[1] for f in features for r in rings(f["geometry"]) for c in r]
    min_lon, max_lon, min_lat, max_lat = min(lons), max(lons), min(lats), max(lats)
    scale_x = math.cos(math.radians((min_lat + max_lat) / 2))
    k = HEIGHT / (max_lat - min_lat)
    width = (max_lon - min_lon) * scale_x * k

    def project(lon, lat):
        return ((lon - min_lon) * scale_x * k, (max_lat - lat) * k)

    regions = []
    for feature in sorted(features, key=lambda f: f["properties"]["adm1_pcode"]):
        pcode = feature["properties"]["adm1_pcode"]
        name, aliases = NAMES[pcode]
        projected = [[project(lon, lat) for lon, lat in ring] for ring in rings(feature["geometry"])]
        largest = max(projected, key=area)
        parts = []
        for ring in projected:
            if ring is not largest and area(ring) < args.min_area:
                continue
            simple = simplify(ring, args.tolerance)
            if len(simple) >= 4:
                parts.append("M" + " ".join(f"{x:.1f} {y:.1f}" for x, y in simple[:-1]) + "Z")
        regions.append({
            "pcode": pcode,
            "name": name,
            "aliases": sorted({name, feature["properties"]["adm1_name"], *aliases}),
            "d": "".join(parts),
        })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    json.dump({
        "viewBox": f"0 0 {width:.0f} {HEIGHT:.0f}",
        "attribution": "BNGRC / OCHA — CC BY-IGO",
        "regions": regions,
    }, open(OUTPUT, "w"), ensure_ascii=False, separators=(",", ":"))
    print(f"{OUTPUT} — {len(regions)} regions, {OUTPUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
