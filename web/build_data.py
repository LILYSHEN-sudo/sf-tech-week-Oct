"""Build web/data.js for the map page.

Inputs : ../data/00-ready-to-use-data/sf-tech-week-events-master-slim.json
         ../data/source-data/sf-analysis-neighborhoods.geojson     (DataSF "Analysis Neighborhoods")
Output : ./data.js  (window.TW = {...})

    python3 build_data.py
"""
import json
import math
import os
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
SOURCE_DATA = os.path.join(DATA, "source-data")
READY_DATA = os.path.join(DATA, "00-ready-to-use-data")
NEIGHBORHOOD_GEOJSON = os.path.join(SOURCE_DATA, "01-sf-event-data-1710", "raw", "sf-analysis-neighborhoods.geojson")

# Projection: equirectangular with cos(lat) correction, 1000 px wide.
LNG0, LNG1, LAT0, LAT1 = -122.5155, -122.3550, 37.7080, 37.8330
KX = math.cos(math.radians(37.77))
SCALE = 1000 / ((LNG1 - LNG0) * KX)


def project(lng, lat):
    return round((lng - LNG0) * KX * SCALE, 1), round((LAT1 - lat) * SCALE, 1)


# Approximate centers for the tech-week neighborhood labels (hand-placed, street-level accuracy
# is not needed: events only carry a neighborhood name).
CENTERS = {
    "SOMA": (-122.4056, 37.7785), "FiDi": (-122.3999, 37.7946), "Downtown": (-122.4032, 37.7882),
    "Union Square": (-122.4075, 37.7879), "Mission": (-122.4148, 37.7599), "Embarcadero": (-122.3937, 37.7955),
    "Jackson Square": (-122.4030, 37.7967), "Marina": (-122.4370, 37.8030), "Mission Bay": (-122.3915, 37.7706),
    "Hayes Valley": (-122.4240, 37.7765), "Civic Center": (-122.4176, 37.7793), "Dogpatch": (-122.3880, 37.7597),
    "North Beach": (-122.4100, 37.8003), "Rincon Hill": (-122.3925, 37.7865), "Russian Hill": (-122.4194, 37.8011),
    "Lower Nob Hill": (-122.4135, 37.7880), "South Beach": (-122.3890, 37.7810), "Pacific Heights": (-122.4350, 37.7925),
    "Salesforce Park": (-122.3965, 37.7895), "Golden Gate Park": (-122.4862, 37.7694), "Chinatown": (-122.4078, 37.7941),
    "Nob Hill": (-122.4161, 37.7930), "Fisherman's Wharf": (-122.4177, 37.8080), "Alamo Square": (-122.4346, 37.7764),
    "Potrero Hill": (-122.4009, 37.7605), "Design District": (-122.4030, 37.7680), "Presidio Heights": (-122.4530, 37.7887),
    "NOPA": (-122.4410, 37.7755), "Cow Hollow": (-122.4360, 37.7975), "Castro": (-122.4350, 37.7609),
    "Telegraph Hill": (-122.4058, 37.8025), "Ocean Beach": (-122.5090, 37.7594), "Duboce Triangle": (-122.4330, 37.7690),
    "Panhandle": (-122.4470, 37.7725), "Haight Ashbury": (-122.4481, 37.7692), "Lower Haight": (-122.4310, 37.7720),
}

# Bay Area labels outside SF, only used by the tiled map (map.html). "East Bay" is a region label with no city:
# it is pinned to downtown Oakland and the page says the position is indicative.
OUTSIDE = {
    "Palo Alto": (-122.1430, 37.4419), "Stanford": (-122.1697, 37.4275), "Mountain View": (-122.0838, 37.3861),
    "San Mateo": (-122.3255, 37.5630), "Hillsborough": (-122.3794, 37.5741), "East Bay": (-122.2711, 37.8044),
}

DOMAINS = [
    "AI Agents & DevTools", "AI Infra & Compute", "Deep Tech & Hardware", "Bio & Health", "Fintech & Crypto",
    "GTM & Sales", "Fundraising & Investing", "Creator, Media & Consumer", "Enterprise & SaaS", "Global Founders",
    "Cybersecurity", "Climate", "People & Hiring", "Women-focused",
]
INTENTS = ["Funding", "Networking", "Building", "Learning", "Consumer", "Hiring", "Entertainment"]
AUDIENCES = ["Founder", "Investor", "Engineer", "Marketing", "Sales", "HR", "Creator", "PM"]
DAYS = ["2026-10-05", "2026-10-06", "2026-10-07", "2026-10-08", "2026-10-09", "2026-10-10", "2026-10-11"]

HOOD_ALIASES = {
    "Downtown (SF)": "Downtown",
    "FiDi (SF)": "FiDi",
    "Union Square (SF)": "Union Square",
    "Virtual (SF)": "Virtual",
    "": "Unknown",
}


def clean_hood(name):
    return HOOD_ALIASES.get((name or "").strip(), (name or "").strip() or "Unknown")


def split_tags(value):
    return {v.strip() for v in (value or "").split(";") if v.strip()}


def bitmask(universe, values):
    return sum(1 << i for i, value in enumerate(universe) if value in values)


def clean_status(value):
    value = (value or "").strip()
    return value or "unknown"


def rdp(points, eps):
    """Ramer-Douglas-Peucker line simplification."""
    if len(points) < 3:
        return points
    (x1, y1), (x2, y2) = points[0], points[-1]
    dx, dy = x2 - x1, y2 - y1
    norm = math.hypot(dx, dy)
    idx, dmax = 0, 0.0
    for i in range(1, len(points) - 1):
        px, py = points[i]
        # Closed rings start and end on the same point: fall back to point distance.
        d = abs(dy * px - dx * py + x2 * y1 - y2 * x1) / norm if norm else math.hypot(px - x1, py - y1)
        if d > dmax:
            idx, dmax = i, d
    if dmax > eps:
        return rdp(points[: idx + 1], eps)[:-1] + rdp(points[idx:], eps)
    return [points[0], points[-1]]


def ring_path(ring):
    pts = rdp([project(lng, lat) for lng, lat in ring], 0.8)
    if len(pts) < 4:
        return ""
    return "M" + "L".join(f"{x:g},{y:g}" for x, y in pts) + "Z"


def build_shapes():
    candidates = [
        os.path.join(SOURCE_DATA, "sf-analysis-neighborhoods.geojson"),
        NEIGHBORHOOD_GEOJSON,
    ]
    path = next((p for p in candidates if os.path.exists(p)), None)
    if not path:
        raise FileNotFoundError("Could not find sf-analysis-neighborhoods.geojson")
    gj = json.load(open(path))
    shapes = []
    for f in gj["features"]:
        geom = f["geometry"]
        polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        d = "".join(ring_path(poly[0]) for poly in polys)
        if d:
            shapes.append({"name": f["properties"].get("nhood", ""), "d": d})
    return shapes


def main():
    master_path = os.path.join(READY_DATA, "sf-tech-week-events-master-slim.json")
    rows = json.load(open(master_path, encoding="utf-8"))
    rows = [r for r in rows if r.get("date") in DAYS]
    for r in rows:
        r["_hood_clean"] = clean_hood(r.get("neighborhood"))

    hoods = sorted({r["_hood_clean"] for r in rows})
    hood_meta = []
    for h in hoods:
        region = next((r.get("region") or "Unknown") for r in rows if r["_hood_clean"] == h)
        xy = project(*CENTERS[h]) if h in CENTERS else None
        ll = CENTERS.get(h) or OUTSIDE.get(h)
        hood_meta.append({"name": h, "region": region, "xy": xy, "ll": list(ll) if ll else None})
    missing = [h["name"] for h in hood_meta if h["region"] == "San Francisco" and not h["xy"]]
    missing += [h["name"] for h in hood_meta if h["region"] in ("Peninsula & South Bay", "East Bay") and not h["ll"]]
    if missing:
        raise SystemExit(f"no map center for: {missing}")
    hidx = {h: i for i, h in enumerate(hoods)}

    # The 23 official themes, most used first (the map's topic buttons use this order).
    theme_n = {}
    for r in rows:
        for t in split_tags(r.get("themes")):
            theme_n[t] = theme_n.get(t, 0) + 1
    themes = sorted(theme_n, key=lambda t: (-theme_n[t], t))

    format_n = {}
    for r in rows:
        for f in split_tags(r.get("formats")):
            format_n[f] = format_n.get(f, 0) + 1
    formats = sorted(format_n, key=lambda f: (-format_n[f], f))

    events = []
    for r in rows:
        hour_raw = r.get("hour")
        hour = int(hour_raw) if isinstance(hour_raw, int) or str(hour_raw).isdigit() else -1
        if 0 <= hour < 6:
            hour = -1
        ths = split_tags(r.get("themes"))
        tmask = bitmask(themes, ths)
        fs = split_tags(r.get("formats"))
        fmask = bitmask(formats, fs)
        intents = {i for i in split_tags(r.get("intent_inferred")) if i != "general"}
        imask = bitmask(INTENTS, intents)
        audiences = {a for a in split_tags(r.get("audience_inferred")) if a != "general"}
        amask = bitmask(AUDIENCES, audiences)
        url = r.get("partiful_url") or r.get("techweek_go_event_url") or ""
        # compact row: [hood, day, hour, domainMask, name, host, time, status, url,
        #               themeMask, formatMask, intentMask, audienceMask]
        events.append([hidx[r["_hood_clean"]], DAYS.index(r["date"]), hour, 0,
                       r.get("name") or "", r.get("primary_host") or "", r.get("time") or "", clean_status(r.get("registration_status")), url,
                       tmask, fmask, imask, amask])

    payload = {
        "generated": date.today().isoformat(), "source": "data/00-ready-to-use-data/sf-tech-week-events-master-slim.json",
        "domains": DOMAINS, "themes": themes, "formats": formats,
        "intents": INTENTS, "audiences": AUDIENCES, "days": DAYS, "hoods": hood_meta,
        "events": events, "lift": [], "shapes": build_shapes(), "size": [1000, round((LAT1 - LAT0) * SCALE)],
    }
    with open(os.path.join(HERE, "data.js"), "w", encoding="utf-8") as f:
        f.write("window.TW=" + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n")
    print(f"events {len(events)}, hoods {len(hoods)}, shapes {len(payload['shapes'])}, "
          f"bytes {os.path.getsize(os.path.join(HERE, 'data.js'))}")


if __name__ == "__main__":
    main()
