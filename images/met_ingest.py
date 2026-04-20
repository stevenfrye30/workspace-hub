#!/usr/bin/env python3
"""Metropolitan Museum of Art Open Access ingest helper.

Uses collectionapi.metmuseum.org. No auth required. Most images are CC0;
the script filters to isPublicDomain=True so output is always clean.

  python met_ingest.py search "Benin bronze" [--limit 30] [--department "African Art"]
      Search and print matching object IDs / titles.

  python met_ingest.py fetch 123 456 789 --region africa [-o batch.json]
      Fetch objectIDs, emit add_works.py entries (desc blank for hand-writing).

  python met_ingest.py departments
      Print the department name → ID table (useful for filtering searches).
"""
import argparse
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://collectionapi.metmuseum.org/public/collection/v1"
UA = {"User-Agent": "images-gallery/1.0"}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def to_entry(obj):
    if not obj.get("isPublicDomain"):
        return None
    image = obj.get("primaryImage") or ""
    if not image:
        return None
    title = (obj.get("title") or "").strip()
    artist = (obj.get("artistDisplayName") or "").strip()
    year = obj.get("objectBeginDate")
    if year is None or year == 0:
        year_end = obj.get("objectEndDate")
        if year_end is not None and year_end != 0:
            year = year_end
    date_disp = (obj.get("objectDate") or "").strip()
    culture = (obj.get("culture") or obj.get("period") or "").strip()
    medium = (obj.get("medium") or "").strip()

    meta_bits = [b for b in (culture, date_disp, medium) if b]
    meta = " · ".join(meta_bits)

    entry = {
        "title": title,
        "meta": meta,
        "desc": "",
        "image": image,
        "_met_object": obj.get("objectID"),
    }
    if artist and artist.lower() not in ("anonymous", "unknown"):
        entry["artist"] = artist
    if isinstance(year, int) and year != 0:
        entry["year"] = year
    return entry


def cmd_search(args):
    params = {"q": args.query, "hasImages": "true"}
    if args.department:
        depts = get(f"{API}/departments").get("departments", [])
        match = next((d for d in depts if args.department.lower() in d["displayName"].lower()), None)
        if not match:
            sys.exit(f"No department matches '{args.department}'. Try `departments` subcommand.")
        params["departmentId"] = str(match["departmentId"])
    if args.title:
        params["title"] = "true"
    url = f"{API}/search?" + urllib.parse.urlencode(params)
    data = get(url)
    ids = data.get("objectIDs") or []
    if not ids:
        print("No results.")
        return
    print(f"Total: {data.get('total')}. Showing first {args.limit}:")
    for oid in ids[: args.limit]:
        try:
            obj = get(f"{API}/objects/{oid}")
        except Exception as e:
            print(f"  ERR {oid}: {e}")
            continue
        if not obj.get("isPublicDomain"):
            continue
        if not obj.get("primaryImage"):
            continue
        title = (obj.get("title") or "")[:55]
        artist = (obj.get("artistDisplayName") or "")[:25]
        year = obj.get("objectBeginDate") or ""
        culture = (obj.get("culture") or "")[:18]
        print(f"  {oid:<8} {year!s:>6}  {culture:<18}  {artist:<25}  {title}")


def cmd_fetch(args):
    entries = []
    for oid in args.object_ids:
        print(f"  fetching {oid}...", file=sys.stderr)
        try:
            obj = get(f"{API}/objects/{oid}")
        except Exception as e:
            print(f"    ERR: {e}", file=sys.stderr)
            continue
        entry = to_entry(obj)
        if entry is None:
            print(f"    SKIP {oid}: not public domain or no image", file=sys.stderr)
            continue
        entries.append(entry)

    out = {args.region: entries}
    payload = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(payload + "\n", encoding="utf-8")
        print(f"Wrote {len(entries)} entries to {args.output}", file=sys.stderr)
    else:
        print(payload)


def cmd_departments(args):
    data = get(f"{API}/departments")
    for d in data.get("departments", []):
        print(f"  {d['departmentId']:>3}  {d['displayName']}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("search", help="Search the collection.")
    sp.add_argument("query")
    sp.add_argument("--department", help='e.g. "African Art", "Asian Art", "Islamic Art".')
    sp.add_argument("--title", action="store_true", help="Search only in titles.")
    sp.add_argument("--limit", type=int, default=30)
    sp.set_defaults(func=cmd_search)

    fp = sub.add_parser("fetch", help="Fetch objectIDs, emit add_works entries.")
    fp.add_argument("object_ids", nargs="+", type=int)
    fp.add_argument("--region", default="europe")
    fp.add_argument("-o", "--output")
    fp.set_defaults(func=cmd_fetch)

    dp = sub.add_parser("departments", help="List departments with IDs.")
    dp.set_defaults(func=cmd_departments)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
