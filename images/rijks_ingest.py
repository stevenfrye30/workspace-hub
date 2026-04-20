#!/usr/bin/env python3
"""Rijksmuseum Data Services ingest helper (new API, no key required).

Uses the 2024+ Linked-Art-over-HTTP API at data.rijksmuseum.nl. The legacy
Rijksstudio API was shut down on 2026-01-05.

  python rijks_ingest.py search "<query>" [--limit 20]
      Search by free text (matches titles, creators, descriptions).

  python rijks_ingest.py fetch SK-C-5 SK-A-180 ... --region europe [-o batch.json]
      Fetch specific object numbers and emit entries in the add_works.py format.
      'desc' is left blank for hand-written descriptions.
"""
import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEARCH = "https://data.rijksmuseum.nl/search/collection"
UA = {"User-Agent": "images-gallery/1.0", "Accept": "application/ld+json"}

# Getty AAT vocabulary IDs we care about:
AAT_BRIEF_NAME = "http://vocab.getty.edu/aat/300404670"      # preferred/brief name
AAT_SHORT_TITLE = "http://vocab.getty.edu/aat/300417207"     # short title
AAT_DESCRIPTION = "http://vocab.getty.edu/aat/300048722"     # descriptive text
AAT_LANG_EN = "http://vocab.getty.edu/aat/300388277"
AAT_LANG_NL = "http://vocab.getty.edu/aat/300388256"


def http_get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def _classified_ids(node: dict) -> list[str]:
    out = []
    for c in (node.get("classified_as") or []):
        if isinstance(c, dict):
            cid = c.get("id")
            if cid:
                out.append(cid)
        elif isinstance(c, str):
            out.append(c)
    return out


def _lang_id(node: dict) -> str | None:
    langs = node.get("language") or []
    for l in langs:
        if isinstance(l, dict) and l.get("id"):
            return l["id"]
    return None


def extract_title(obj: dict) -> str:
    names = [n for n in (obj.get("identified_by") or []) if n.get("type") == "Name"]
    # Prefer brief/short title in English.
    def score(n):
        cids = _classified_ids(n)
        is_brief = AAT_BRIEF_NAME in cids or AAT_SHORT_TITLE in cids
        is_en = _lang_id(n) == AAT_LANG_EN
        return (is_brief, is_en, -len(n.get("content") or ""))
    if not names:
        return ""
    names.sort(key=score, reverse=True)
    return (names[0].get("content") or "").strip()


def _clean_artist(name: str) -> str:
    return re.sub(r"\s*\([^)]*\)\s*$", "", name or "").strip()


def extract_artist(obj: dict) -> str:
    produced = obj.get("produced_by") or {}
    for part in produced.get("part") or []:
        for actor in part.get("carried_out_by") or []:
            for n in actor.get("notation") or []:
                if isinstance(n, dict) and n.get("@language") == "en" and n.get("@value"):
                    return _clean_artist(n["@value"])
            for n in actor.get("notation") or []:
                if isinstance(n, dict) and n.get("@value"):
                    return _clean_artist(n["@value"])
    for rb in produced.get("referred_to_by") or []:
        if rb.get("type") == "LinguisticObject":
            content = rb.get("content")
            if content:
                return _clean_artist(content)
    return ""


def extract_year(obj: dict) -> int | None:
    ts = ((obj.get("produced_by") or {}).get("timespan")) or {}
    if not isinstance(ts, dict):
        return None
    for key in ("begin_of_the_begin", "end_of_the_end"):
        v = ts.get(key)
        if isinstance(v, str):
            m = re.match(r"(-?\d{1,4})", v)
            if m:
                return int(m.group(1))
    for n in ts.get("identified_by") or []:
        content = n.get("content") or ""
        m = re.search(r"-?\d{3,4}", content)
        if m:
            return int(m.group(0))
    return None


def extract_description(obj: dict) -> str:
    parts = []
    for so in obj.get("subject_of") or []:
        if so.get("type") != "LinguisticObject":
            continue
        for p in so.get("part") or []:
            if AAT_DESCRIPTION in _classified_ids(p):
                content = p.get("content")
                if content:
                    parts.append(content.strip())
    return parts[0] if parts else ""


def extract_image_id(obj: dict) -> str | None:
    shows = obj.get("shows") or []
    for s in shows:
        if s.get("id"):
            return s["id"]
    return None


def resolve_image(visual_item_id: str, width: int = 1200) -> str | None:
    """Follow VisualItem → DigitalObject → IIIF access_point, and return a sized URL."""
    visual = http_get_json(visual_item_id)
    dshown = visual.get("digitally_shown_by") or []
    for d in dshown:
        dig_id = d.get("id")
        if not dig_id:
            continue
        digital = http_get_json(dig_id)
        for ap in digital.get("access_point") or []:
            url = ap.get("id") or ""
            if not url:
                continue
            # IIIF: .../full/max/0/default.jpg  →  .../full/{w},/0/default.jpg
            return re.sub(r"/full/[^/]+/0/", f"/full/{width},/0/", url)
    return None


def _get_object_number(obj: dict) -> str:
    """Return the exact object number from an object's identified_by array."""
    for ib in obj.get("identified_by") or []:
        if ib.get("type") != "Identifier":
            continue
        cids = _classified_ids(ib)
        if "http://vocab.getty.edu/aat/300312355" in cids:
            return ib.get("content") or ""
    return ""


def search_id_by_object_number(object_number: str) -> str | None:
    """Rijksmuseum objectNumber search is prefix-match; filter for exact."""
    url = f"{SEARCH}?" + urllib.parse.urlencode({
        "objectNumber": object_number,
        "imageAvailable": "true",
    })
    data = http_get_json(url)
    items = data.get("orderedItems") or []
    for item in items[:20]:
        pid = item.get("id")
        if not pid:
            continue
        try:
            obj = http_get_json(pid)
        except Exception:
            continue
        if _get_object_number(obj) == object_number:
            return pid
    # Fallback: first result if no exact match found.
    return items[0].get("id") if items else None


def fetch_entry(object_number: str) -> dict | None:
    pid = search_id_by_object_number(object_number)
    if not pid:
        print(f"    no match for {object_number}", file=sys.stderr)
        return None
    obj = http_get_json(pid)
    visual = extract_image_id(obj)
    image = resolve_image(visual) if visual else None
    if not image:
        print(f"    no image for {object_number}", file=sys.stderr)
        return None

    entry = {
        "title": extract_title(obj),
        "meta": "",
        "desc": "",
        "image": image,
        "_rijks_object": object_number,
        "_rijks_description": extract_description(obj),
    }
    artist = extract_artist(obj)
    if artist and artist.lower() not in ("anonymous", "unknown"):
        entry["artist"] = artist
    year = extract_year(obj)
    if year is not None:
        entry["year"] = year
    return entry


def cmd_search(args) -> None:
    params = {"imageAvailable": "true"}
    if args.title:
        params["title"] = args.title
    if args.creator:
        params["creator"] = args.creator
    if args.description:
        params["description"] = args.description
    url = f"{SEARCH}?" + urllib.parse.urlencode(params)
    data = http_get_json(url)
    items = (data.get("orderedItems") or [])[: args.limit]
    if not items:
        print("No results.")
        return
    print(f"Found {len(items)} results (showing up to {args.limit}):\n")
    for item in items:
        pid = item.get("id")
        if not pid:
            continue
        try:
            obj = http_get_json(pid)
        except Exception as e:
            print(f"  ERR: {e}")
            continue
        obj_no = ""
        for ib in obj.get("identified_by") or []:
            if ib.get("type") == "Identifier":
                obj_no = ib.get("content") or ""
                break
        title = extract_title(obj)[:55]
        artist = extract_artist(obj)[:30]
        year = extract_year(obj) or ""
        print(f"  {obj_no:<15} {str(year):>5}  {artist:<30}  {title}")


def cmd_fetch(args) -> None:
    entries = []
    for obj_no in args.object_numbers:
        print(f"  fetching {obj_no}...", file=sys.stderr)
        try:
            entry = fetch_entry(obj_no)
        except Exception as e:
            print(f"    ERR: {e}", file=sys.stderr)
            continue
        if entry:
            entries.append(entry)

    out = {args.region: entries}
    payload = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(payload + "\n", encoding="utf-8")
        print(f"Wrote {len(entries)} entries to {args.output}", file=sys.stderr)
    else:
        print(payload)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("search", help="Search the collection.")
    sp.add_argument("--title")
    sp.add_argument("--creator")
    sp.add_argument("--description")
    sp.add_argument("--limit", type=int, default=20)
    sp.set_defaults(func=cmd_search)

    fp = sub.add_parser("fetch", help="Fetch object numbers, emit add_works entries.")
    fp.add_argument("object_numbers", nargs="+")
    fp.add_argument("--region", default="europe")
    fp.add_argument("-o", "--output")
    fp.set_defaults(func=cmd_fetch)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
