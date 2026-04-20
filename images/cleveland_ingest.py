#!/usr/bin/env python3
"""Cleveland Museum of Art Open Access ingest helper.

Uses openaccess-api.clevelandart.org. No auth required. ~60k CC0 objects with
strong Asian, Islamic, pre-Columbian, and African holdings.

  python cleveland_ingest.py search "Chinese bronze" [--limit 20] [--type Sculpture]
      Search matching artworks and print id / title / artist / year.

  python cleveland_ingest.py fetch 94979 1234 --region europe [-o batch.json]
      Fetch by artwork ID, emit add_works.py entries.
"""
import argparse
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://openaccess-api.clevelandart.org/api/artworks"
UA = {"User-Agent": "images-gallery/1.0"}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def first_artist(d):
    for c in d.get("creators") or []:
        desc = c.get("description") or ""
        # "John Singleton Copley (American, 1738-1815)" → "John Singleton Copley"
        name = desc.split("(")[0].strip()
        if name and name.lower() not in ("anonymous", "unknown", "maker unknown"):
            return name
    return ""


def to_entry(d):
    if not d or d.get("share_license_status") not in ("CC0", None):  # None = older records, usually open
        pass  # still include if image exists
    images = d.get("images") or {}
    img = (images.get("print") or {}).get("url") or (images.get("web") or {}).get("url")
    if not img:
        return None
    year = d.get("creation_date_earliest")
    title = (d.get("title") or "").strip()
    artist = first_artist(d)

    date_disp = (d.get("creation_date") or "").strip()
    culture = d.get("culture") or []
    if isinstance(culture, list):
        culture = ", ".join(culture)
    technique = (d.get("technique") or "").strip()
    meta_bits = [b for b in (culture, date_disp, technique) if b]
    meta = " · ".join(meta_bits)

    entry = {
        "title": title,
        "meta": meta,
        "desc": "",
        "image": img,
        "_cma_object": d.get("id"),
        "_cma_accession": d.get("accession_number"),
    }
    if artist:
        entry["artist"] = artist
    if isinstance(year, int):
        entry["year"] = year
    return entry


def cmd_search(args):
    params = {"q": args.query, "has_image": "1", "limit": str(args.limit)}
    if args.type:
        params["type"] = args.type
    if args.department:
        params["department"] = args.department
    url = f"{API}?" + urllib.parse.urlencode(params)
    data = get(url)
    hits = data.get("data") or []
    if not hits:
        print("No results.")
        return
    print(f"Total: {data.get('info',{}).get('total')}. Showing first {len(hits)}:")
    for a in hits:
        aid = a.get("id", "")
        title = (a.get("title") or "")[:50]
        year = a.get("creation_date_earliest") or ""
        artist = first_artist(a)[:25]
        typ = (a.get("type") or "")[:14]
        culture = ", ".join(a.get("culture") or [])[:18]
        print(f"  {aid:<7} {year!s:>6}  {typ:<14}  {culture:<18}  {artist:<25}  {title}")


def cmd_fetch(args):
    entries = []
    for aid in args.ids:
        print(f"  fetching {aid}...", file=sys.stderr)
        try:
            resp = get(f"{API}/{aid}")
        except Exception as e:
            print(f"    ERR: {e}", file=sys.stderr)
            continue
        entry = to_entry(resp.get("data") or {})
        if entry is None:
            print(f"    SKIP {aid}: no image", file=sys.stderr)
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
    sp.add_argument("--type", help='e.g. "Painting", "Sculpture", "Textile".')
    sp.add_argument("--department", help='e.g. "Chinese Art", "African Art".')
    sp.add_argument("--limit", type=int, default=20)
    sp.set_defaults(func=cmd_search)

    fp = sub.add_parser("fetch", help="Fetch artwork IDs.")
    fp.add_argument("ids", nargs="+", type=int)
    fp.add_argument("--region", default="europe")
    fp.add_argument("-o", "--output")
    fp.set_defaults(func=cmd_fetch)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
