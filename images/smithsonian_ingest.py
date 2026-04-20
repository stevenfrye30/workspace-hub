#!/usr/bin/env python3
"""Smithsonian Open Access ingest helper.

Uses api.si.edu. Covers NMAfA (African), Freer-Sackler (Asian), NMAI (Native
American), Anacostia, and more — ~4.5M CC0 objects across a single API.

Requires an api.data.gov key (free). Set env var SI_API_KEY, or write the key
alone into a file named `.si_key` next to this script.

  python smithsonian_ingest.py search "Benin bronze" [--unit NMAfA] [--limit 30]
      Keyword search. Filter to a specific museum unit with --unit if desired.

  python smithsonian_ingest.py fetch <record_id> ... --region africa [-o batch.json]
      Fetch records by Smithsonian ID, emit add_works.py entries.
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://api.si.edu/openaccess/api/v1.0"
UA = {"User-Agent": "images-gallery/1.0"}
HERE = Path(__file__).resolve().parent


def load_key():
    k = os.environ.get("SI_API_KEY")
    if k:
        return k.strip()
    kf = HERE / ".si_key"
    if kf.exists():
        return kf.read_text(encoding="utf-8").strip()
    sys.exit("No API key. Get one from https://api.data.gov/signup, set SI_API_KEY or write to .si_key")


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def _first(d, *paths, default=""):
    """Safely walk nested dict/list paths. Each path is a list of keys/indices."""
    for path in paths:
        cur = d
        ok = True
        for k in path:
            if isinstance(cur, list):
                try:
                    cur = cur[k]
                except (IndexError, TypeError):
                    ok = False; break
            elif isinstance(cur, dict):
                cur = cur.get(k)
                if cur is None:
                    ok = False; break
            else:
                ok = False; break
        if ok and cur:
            return cur if not isinstance(cur, list) else (cur[0] if cur else default)
    return default


def extract_content_fields(record):
    content = record.get("content") or {}
    dnr = content.get("descriptiveNonRepeating") or {}
    freetext = (content.get("freetext") or {})
    indexed = (content.get("indexedStructured") or {})

    title = dnr.get("title", {}).get("content") or record.get("title") or ""
    # Artist / maker
    artist = ""
    for f in freetext.get("name", []) or []:
        if f.get("label") in ("Artist", "Maker", "Creator", "Attributed to"):
            artist = f.get("content") or ""
            if artist:
                break
    if not artist and indexed.get("name"):
        artist = indexed["name"][0] if isinstance(indexed["name"], list) else indexed["name"]

    # Date
    date_display = ""
    for f in freetext.get("date", []) or []:
        if f.get("content"):
            date_display = f["content"]; break
    year = None
    if indexed.get("date"):
        dates = indexed["date"] if isinstance(indexed["date"], list) else [indexed["date"]]
        for d in dates:
            import re
            m = re.search(r"-?\d{3,4}", str(d))
            if m:
                year = int(m.group()); break

    # Culture / place
    culture = ""
    for f in freetext.get("culture", []) or []:
        if f.get("content"):
            culture = f["content"]; break
    if not culture:
        place = (indexed.get("geoLocation") or [])
        if place:
            culture = str(place[0])[:40]

    medium = ""
    for f in freetext.get("physicalDescription", []) or []:
        if f.get("label") in ("Medium", "Materials"):
            medium = f.get("content") or ""; break

    # Image
    image = ""
    media = (dnr.get("online_media") or {}).get("media") or []
    for m in media:
        if (m.get("type") or "").lower() == "images":
            # Try resources first (multiple sizes), fallback to top-level 'content'
            for res in (m.get("resources") or []):
                if (res.get("label") or "").lower() in ("high-resolution jpeg (public)", "screen image", "high resolution"):
                    image = res.get("url") or ""
                    if image: break
            if not image:
                image = m.get("content") or ""
            if image: break

    return {
        "title": title.strip(),
        "artist": artist.strip(),
        "year": year,
        "date_display": date_display.strip(),
        "culture": culture.strip(),
        "medium": medium.strip(),
        "image": image.strip(),
    }


def to_entry(record):
    fields = extract_content_fields(record)
    if not fields["image"]:
        return None
    meta_bits = [b for b in (fields["culture"], fields["date_display"], fields["medium"]) if b]
    meta = " · ".join(meta_bits)
    entry = {
        "title": fields["title"],
        "meta": meta,
        "desc": "",
        "image": fields["image"],
        "_si_id": record.get("id"),
        "_si_unit": record.get("unitCode"),
    }
    artist = fields["artist"]
    if artist and artist.lower() not in ("unknown", "anonymous", "maker unknown"):
        entry["artist"] = artist
    if isinstance(fields["year"], int):
        entry["year"] = fields["year"]
    return entry


def cmd_search(args):
    key = load_key()
    q = args.query
    if args.unit:
        q = f"({q}) AND unit_code:{args.unit}"
    if args.cc0_only:
        q = f"({q}) AND online_media_type:\"Images\" AND media_usage:\"CC0\""
    params = {"api_key": key, "q": q, "rows": str(args.limit)}
    url = f"{API}/search?" + urllib.parse.urlencode(params)
    data = get(url)
    rows = (data.get("response") or {}).get("rows") or []
    if not rows:
        print("No results.")
        return
    total = (data.get("response") or {}).get("rowCount")
    print(f"Total: {total}. Showing first {len(rows)}:")
    for r in rows:
        rid = r.get("id", "")
        fields = extract_content_fields(r)
        title = fields["title"][:50]
        artist = fields["artist"][:25]
        year = fields["year"] or ""
        unit = r.get("unitCode", "")[:10]
        has_image = "img" if fields["image"] else "   "
        print(f"  {rid:<30} {unit:<10} {year!s:>6}  {has_image}  {artist:<25}  {title}")


def cmd_fetch(args):
    key = load_key()
    entries = []
    for rid in args.ids:
        print(f"  fetching {rid}...", file=sys.stderr)
        try:
            url = f"{API}/content/{urllib.parse.quote(rid, safe='')}?api_key={key}"
            data = get(url)
        except Exception as e:
            print(f"    ERR: {e}", file=sys.stderr)
            continue
        record = data.get("response") or data
        entry = to_entry(record)
        if entry is None:
            print(f"    SKIP {rid}: no image", file=sys.stderr)
            continue
        entries.append(entry)

    out = {args.region: entries}
    payload = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(payload + "\n", encoding="utf-8")
        print(f"Wrote {len(entries)} entries to {args.output}", file=sys.stderr)
    else:
        print(payload)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("search", help="Search the collection.")
    sp.add_argument("query")
    sp.add_argument("--unit", help='Unit code, e.g. NMAfA (African), FSG (Freer/Sackler), NMAI (American Indian), NMAH (American History).')
    sp.add_argument("--cc0-only", action="store_true", help="Limit to CC0-licensed items.")
    sp.add_argument("--limit", type=int, default=30)
    sp.set_defaults(func=cmd_search)

    fp = sub.add_parser("fetch", help="Fetch records by Smithsonian ID.")
    fp.add_argument("ids", nargs="+")
    fp.add_argument("--region", default="europe")
    fp.add_argument("-o", "--output")
    fp.set_defaults(func=cmd_fetch)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
