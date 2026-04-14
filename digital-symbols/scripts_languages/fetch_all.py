"""
Fetch every language <-> script mapping from Unicode CLDR and Wikidata, then compare.

Strategy:
  1. CLDR first (local GitHub download; always works).
  2. Wikidata: (a) a *minimal* SPARQL for the (lang QID, script QID, iso639, iso15924)
     pairs with NO label SERVICE (labels are the expensive part).
     (b) Resolve QIDs to English labels via the wbgetentities API in batches of 50.

Run:
  python fetch_all.py                     # both sources
  python fetch_all.py --cldr-only         # skip Wikidata
  python fetch_all.py --wikidata-only     # skip CLDR
"""
from __future__ import annotations
import argparse
import csv
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    import requests
except ImportError:
    print("pip install requests", file=sys.stderr)
    sys.exit(1)

HERE = Path(__file__).parent
DATA = HERE / "data"
DATA.mkdir(exist_ok=True)
UA = "digital-symbols-research/1.0 (personal research; contact: local)"
_CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")

# ===========================================================================
# CLDR
# ===========================================================================
CLDR_SUPPLEMENTAL = ("https://raw.githubusercontent.com/unicode-org/cldr/main/"
                     "common/supplemental/supplementalData.xml")
CLDR_LANGS = ("https://raw.githubusercontent.com/unicode-org/cldr-json/main/"
              "cldr-json/cldr-localenames-full/main/en/languages.json")
CLDR_SCRIPTS = ("https://raw.githubusercontent.com/unicode-org/cldr-json/main/"
                "cldr-json/cldr-localenames-full/main/en/scripts.json")

def fetch_cldr():
    print("[cldr] supplementalData.xml ...", flush=True)
    xml_text = requests.get(CLDR_SUPPLEMENTAL, headers={"User-Agent": UA}, timeout=60).text
    root = ET.fromstring(xml_text)
    pairs = []
    for ld in root.iter("languageData"):
        for lang in ld.findall("language"):
            code = lang.get("type")
            status = "secondary" if lang.get("alt") == "secondary" else "primary"
            for s in (lang.get("scripts") or "").split():
                pairs.append({"lang_code": code, "script_code": s, "status": status})
    print(f"[cldr] {len(pairs)} pairs", flush=True)

    print("[cldr] language names ...", flush=True)
    lnames = requests.get(CLDR_LANGS, headers={"User-Agent": UA}, timeout=60).json()
    lnames = lnames["main"]["en"]["localeDisplayNames"]["languages"]

    print("[cldr] script names ...", flush=True)
    snames = requests.get(CLDR_SCRIPTS, headers={"User-Agent": UA}, timeout=60).json()
    snames = snames["main"]["en"]["localeDisplayNames"]["scripts"]

    (DATA / "cldr_pairs.json").write_text(json.dumps(pairs, indent=2, ensure_ascii=False), encoding="utf-8")
    (DATA / "cldr_language_names.json").write_text(json.dumps(lnames, indent=2, ensure_ascii=False), encoding="utf-8")
    (DATA / "cldr_script_names.json").write_text(json.dumps(snames, indent=2, ensure_ascii=False), encoding="utf-8")
    return pairs, lnames, snames

# ===========================================================================
# Wikidata
# ===========================================================================
WDQS = "https://query.wikidata.org/sparql"
WB_API = "https://www.wikidata.org/w/api.php"

# Only *languages* (and language-like entities) — P282 is used on written works
# too. Restrict by: instance of language (Q34770) or its subclasses, OR anything
# that has an ISO 639-3 code (P220), which by definition is a language.
PAIRS_SPARQL = """
SELECT DISTINCT ?language ?script ?iso639_3 ?iso639_1 ?iso15924 WHERE {
  ?language wdt:P282 ?script .
  {
    ?language wdt:P31/wdt:P279* wd:Q34770 .   # human language
  } UNION {
    ?language wdt:P220 [] .                    # has ISO 639-3 -> is a language
  } UNION {
    ?language wdt:P218 [] .                    # has ISO 639-1
  }
  OPTIONAL { ?language wdt:P220  ?iso639_3 . }
  OPTIONAL { ?language wdt:P218  ?iso639_1 . }
  OPTIONAL { ?script   wdt:P506  ?iso15924 . }
}
"""

def _sparql(query: str, retries: int = 6) -> list[dict]:
    for attempt in range(retries):
        try:
            r = requests.get(
                WDQS,
                params={"query": query, "format": "json"},
                headers={"User-Agent": UA, "Accept": "application/sparql-results+json"},
                timeout=300,
            )
            if r.status_code == 429:
                wait = int(r.headers.get("Retry-After", "30"))
                print(f"  429, sleeping {wait}s", flush=True)
                time.sleep(wait)
                continue
            r.raise_for_status()
            return json.loads(_CTRL.sub("", r.text))["results"]["bindings"]
        except (requests.HTTPError, requests.ConnectionError, json.JSONDecodeError) as e:
            if attempt == retries - 1:
                raise
            wait = 15 * (attempt + 1)
            print(f"  retry in {wait}s ({type(e).__name__})", flush=True)
            time.sleep(wait)
    return []

def _qid(uri: str) -> str:
    return uri.rsplit("/", 1)[-1]

def fetch_wikidata_pairs() -> list[dict]:
    print("[wikidata] fetching pairs (no labels) ...", flush=True)
    rows = _sparql(PAIRS_SPARQL)
    out = []
    for r in rows:
        out.append({
            "lang_qid":    _qid(r["language"]["value"]),
            "script_qid":  _qid(r["script"]["value"]),
            "lang_iso3":   r.get("iso639_3", {}).get("value"),
            "lang_iso1":   r.get("iso639_1", {}).get("value"),
            "script_iso":  r.get("iso15924", {}).get("value"),
        })
    print(f"[wikidata] {len(out)} pairs", flush=True)
    return out

def fetch_labels(qids: list[str]) -> dict[str, str]:
    """Batch resolve English labels via wbgetentities (50 QIDs/call)."""
    out = {}
    qids = sorted(set(qids))
    print(f"[wikidata] resolving {len(qids)} labels ...", flush=True)
    for i in range(0, len(qids), 50):
        chunk = qids[i:i+50]
        for attempt in range(5):
            try:
                r = requests.get(
                    WB_API,
                    params={
                        "action": "wbgetentities",
                        "ids": "|".join(chunk),
                        "props": "labels",
                        "languages": "en",
                        "format": "json",
                    },
                    headers={"User-Agent": UA},
                    timeout=60,
                )
                if r.status_code == 429:
                    time.sleep(int(r.headers.get("Retry-After", "20")))
                    continue
                r.raise_for_status()
                data = r.json().get("entities", {})
                for qid, ent in data.items():
                    lbl = ent.get("labels", {}).get("en", {}).get("value")
                    if lbl:
                        out[qid] = lbl
                break
            except Exception as e:
                if attempt == 4:
                    print(f"  label batch {i} FAILED: {e}", flush=True)
                else:
                    time.sleep(5 * (attempt + 1))
        if (i // 50) % 20 == 0:
            print(f"  labels {i+len(chunk)}/{len(qids)}", flush=True)
        time.sleep(0.6)  # polite
    return out

def fetch_wikidata():
    pairs = fetch_wikidata_pairs()
    qids = [p["lang_qid"] for p in pairs] + [p["script_qid"] for p in pairs]
    labels = fetch_labels(qids)
    out = []
    for p in pairs:
        out.append({
            "script_qid":  p["script_qid"],
            "script_name": labels.get(p["script_qid"]),
            "script_iso":  p["script_iso"],
            "lang_qid":    p["lang_qid"],
            "lang_name":   labels.get(p["lang_qid"]),
            "lang_iso3":   p["lang_iso3"],
            "lang_iso1":   p["lang_iso1"],
        })
    (DATA / "wikidata_pairs.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    return out

# ===========================================================================
# Compare
# ===========================================================================
def compare(wd_rows, cldr_pairs):
    def wd_key(r):
        lang = r.get("lang_iso3") or r.get("lang_iso1")
        return (lang, r.get("script_iso")) if lang and r.get("script_iso") else None
    wd_set   = {k for k in (wd_key(r) for r in wd_rows) if k}
    cldr_set = {(r["lang_code"], r["script_code"]) for r in cldr_pairs}
    both      = sorted(wd_set & cldr_set)
    only_wd   = sorted(wd_set - cldr_set)
    only_cldr = sorted(cldr_set - wd_set)
    return {
        "summary": {
            "wikidata_pairs_total":      len(wd_rows),
            "wikidata_pairs_with_codes": len(wd_set),
            "cldr_pairs_total":          len(cldr_pairs),
            "intersection":              len(both),
            "only_wikidata":             len(only_wd),
            "only_cldr":                 len(only_cldr),
        },
        "both":          [{"lang": l, "script": s} for l, s in both],
        "only_wikidata": [{"lang": l, "script": s} for l, s in only_wd],
        "only_cldr":     [{"lang": l, "script": s} for l, s in only_cldr],
    }

def write_csv(path, wd_rows, cldr_pairs, lnames, snames):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["source", "lang_code", "lang_name", "script_code", "script_name", "status_or_qid"])
        for r in wd_rows:
            w.writerow(["wikidata",
                        r.get("lang_iso3") or r.get("lang_iso1") or "",
                        r.get("lang_name") or "",
                        r.get("script_iso") or "",
                        r.get("script_name") or "",
                        r.get("lang_qid") or ""])
        for r in cldr_pairs:
            w.writerow(["cldr",
                        r["lang_code"],
                        lnames.get(r["lang_code"], "") if lnames else "",
                        r["script_code"],
                        snames.get(r["script_code"], "") if snames else "",
                        r["status"]])

# ===========================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cldr-only", action="store_true")
    ap.add_argument("--wikidata-only", action="store_true")
    args = ap.parse_args()

    cldr_pairs, lnames, snames = ([], {}, {})
    wd_rows = []

    if not args.wikidata_only:
        cldr_pairs, lnames, snames = fetch_cldr()

    if not args.cldr_only:
        wd_rows = fetch_wikidata()

    if cldr_pairs and wd_rows:
        comp = compare(wd_rows, cldr_pairs)
        (DATA / "comparison.json").write_text(json.dumps(comp, indent=2, ensure_ascii=False), encoding="utf-8")
        write_csv(DATA / "comparison.csv", wd_rows, cldr_pairs, lnames, snames)
        print("\n=== summary ===")
        for k, v in comp["summary"].items():
            print(f"  {k:30s} {v}")

    print(f"\nwrote: {DATA}", flush=True)

if __name__ == "__main__":
    main()
