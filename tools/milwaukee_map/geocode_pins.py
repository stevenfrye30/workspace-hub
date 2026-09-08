"""Geocode the SCOUTED pins baked into milwaukee.html via Nominatim.

    python tools/milwaukee_map/geocode_pins.py            dry run: review table,
                                                          results cached beside
                                                          this file (gitignored)
    python tools/milwaukee_map/geocode_pins.py --apply    rewrite coords + addr
                                                          from the cached run

Addresses are pulled from each pin's name (fallback: note). Pins without
one are listed and left alone; add a (prefix, address) pair to MANUAL for
those. 1 req/s against the public endpoint, identified by User-Agent,
results boxed to the city bounds. The parser handles single- and
double-quoted entries and REFUSES if it parses fewer entries than the
array holds — a silently skipped pin is how Manny's went unmapped once.
"""
from __future__ import annotations
import json
import math
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import bundle

CACHE = Path(__file__).parent / "geocode_results.json"
UA = "OurMilwaukeeMap-datafix/1.0 (personal map; https://stevenfrye30.github.io/Workspace/milwaukee.html)"
VIEWBOX = "-88.12,43.24,-87.80,42.87"

# Hand-supplied queries for pins whose text carries no street address.
MANUAL: list[tuple[str, str]] = []

ADDR_RE = re.compile(
    r"(\d{3,5}[A-Z]?\s+[NSEW]\.?\s+[A-Za-z0-9'. ]*?[A-Za-z]\s*"
    r"(?:Ave(?:nue)?|St(?:reet)?|Dr(?:ive)?|Blvd|Rd|Road|Pl(?:ace)?|Pkwy|Ln|Ct|Way))\b")
QS = r"'((?:[^'\\]|\\.)*)'"
QD = r'"((?:[^"\\]|\\.)*)"'


def dist_m(a, b):
    R, t = 6371000, math.pi / 180
    s = (math.sin((b[0] - a[0]) * t / 2) ** 2
         + math.cos(a[0] * t) * math.cos(b[0] * t) * math.sin((b[1] - a[1]) * t / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(s))


def parse_scouted(inner: str):
    m = re.search(r"const SCOUTED = \[\n(.*?)\n\];", inner, re.S)
    if not m:
        raise SystemExit("REFUSE: SCOUTED array not found")
    body, base = m.group(1), m.start(1)
    expected = len(re.findall(r"\{ type:", body))
    entries = []
    entry_re = re.compile(
        r"\{ type:'(\w+)',(?: home:true,)? name:(?:%s|%s), note:(?:%s|%s),.*?lat:\s*(-?[\d.]+), lng:\s*(-?[\d.]+)\s*\}" % (QS, QD, QS, QD),
        re.S)
    for em in entry_re.finditer(body):
        name = em.group(2) if em.group(2) is not None else em.group(3)
        note = em.group(4) if em.group(4) is not None else em.group(5)
        entries.append({
            "type": em.group(1),
            "name": name.replace("\\'", "'").replace('\\"', '"'),
            "note": note.replace("\\'", "'").replace('\\"', '"'),
            "lat": float(em.group(6)), "lng": float(em.group(7)),
            "start": base + em.start(), "end": base + em.end(),
        })
    if len(entries) != expected:
        raise SystemExit(f"REFUSE: SCOUTED holds {expected} entries but only {len(entries)} parsed — fix the parser before trusting it")
    return entries


def find_address(e):
    for source in (e["name"], re.sub(r"<[^>]+>", " ", e["note"])):
        m = ADDR_RE.search(source)
        if m:
            return re.sub(r"\s+", " ", m.group(1)).strip()
    return None


def geocode(addr: str):
    q = addr if re.search(r"milwaukee|wauwatosa|shorewood", addr, re.I) else addr + ", Milwaukee, WI"
    url = ("https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&bounded=1"
           f"&viewbox={VIEWBOX}&q=" + urllib.parse.quote(q))
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        js = json.loads(r.read().decode("utf-8"))
    if not js:
        return None
    hit = js[0]
    lat, lon = float(hit["lat"]), float(hit["lon"])
    if not (42.87 < lat < 43.24 and -88.12 < lon < -87.80):
        return None
    return {"lat": lat, "lng": lon, "addr": ", ".join(hit.get("display_name", "").split(", ")[:3])}


def dry_run():
    inner = bundle.extract()
    entries = parse_scouted(inner)
    results, unresolved = {"pins": {}}, []
    manual = dict(MANUAL)
    for e in entries:
        addr = next((a for p, a in manual.items() if e["name"].startswith(p)), None) or find_address(e)
        short = e["name"].split(" — ")[0].encode("ascii", "replace").decode()[:44]
        if not addr:
            unresolved.append(short)
            continue
        time.sleep(1.1)
        g = geocode(addr)
        if not g:
            unresolved.append(f"{short} — '{addr}' found no match in the city")
            continue
        results["pins"][e["name"]] = {"old": [e["lat"], e["lng"]], "new": [g["lat"], g["lng"]],
                                      "addr": g["addr"], "query": addr}
        print(f"{short:<46}{addr:<26}{e['lat']:.5f},{e['lng']:.5f} -> {g['lat']:.5f},{g['lng']:.5f}"
              f"  {dist_m((e['lat'], e['lng']), (g['lat'], g['lng'])):6.0f}m")
    CACHE.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    if unresolved:
        print("\nUNRESOLVED (stay put — add to MANUAL to fix):")
        for u in unresolved:
            print("  -", u)
    print(f"\ncached -> {CACHE.name}; review, then run with --apply")


def apply():
    results = json.loads(CACHE.read_text(encoding="utf-8"))
    inner = bundle.extract()
    entries = parse_scouted(inner)
    changed = 0
    for e in sorted(entries, key=lambda x: -x["start"]):
        r = results["pins"].get(e["name"])
        if not r:
            continue
        seg = inner[e["start"]:e["end"]]
        seg = re.sub(r"lat:\s*-?[\d.]+, lng:\s*-?[\d.]+",
                     f"lat:{r['new'][0]:.5f}, lng:{r['new'][1]:.5f}", seg)
        addr_js = r["addr"].replace("'", "\\'")
        if "addr:" in seg:
            seg = re.sub(r"addr:(?:%s|%s)" % (QS, QD), f"addr:'{addr_js}'", seg)
        else:
            seg = seg.replace("phone:", f"addr:'{addr_js}', phone:", 1)
        inner = inner[:e["start"]] + seg + inner[e["end"]:]
        changed += 1
    bundle.write_inner(inner)
    print(f"applied {changed} pins — smoke-test on localhost, then commit")


if __name__ == "__main__":
    apply() if "--apply" in sys.argv else dry_run()
