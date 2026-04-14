"""
Combine everything:
  1. Fetch Unicode Scripts.txt + Blocks.txt + PropertyValueAliases.txt.
  2. Build unified script-code -> languages mapping (UNION of Wikidata + CLDR,
     with source tracking per pair).
  3. Iterate UnicodeData.txt, enriching each entry with:
       - script      ISO 15924 code (e.g. "Latn")
       - script_name human-readable
       - block       Unicode block name
       - languages   list of {code, name, source}
  4. Emit:
       - data/script_index.json      (script_code -> {name, languages, codepoint_count, sample})
       - pages/index.html            (list of all scripts)
       - pages/<script_code>.html    (per-script page: langs + glyph grid)

Run:  python enrich_and_build.py
"""
from __future__ import annotations
import bisect
import html
import json
import re
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("pip install requests", file=sys.stderr); sys.exit(1)

HERE = Path(__file__).parent            # .../scripts_languages
ROOT = HERE.parent                       # .../Digital Symbols
DATA = HERE / "data"
PAGES = ROOT / "pages"
PAGES.mkdir(exist_ok=True)

UA = {"User-Agent": "digital-symbols-research/1.0"}

UCD_SCRIPTS = "https://www.unicode.org/Public/UCD/latest/ucd/Scripts.txt"
UCD_BLOCKS = "https://www.unicode.org/Public/UCD/latest/ucd/Blocks.txt"
UCD_ALIASES = "https://www.unicode.org/Public/UCD/latest/ucd/PropertyValueAliases.txt"

# ---------------------------------------------------------------------------
# 1. Unicode UCD fetchers
# ---------------------------------------------------------------------------
def _download(url: str, dest: Path) -> str:
    if dest.exists():
        return dest.read_text(encoding="utf-8")
    print(f"[ucd] {url}", flush=True)
    txt = requests.get(url, headers=UA, timeout=60).text
    dest.write_text(txt, encoding="utf-8")
    return txt

def parse_ranges(text: str) -> list[tuple[int,int,str]]:
    """Parse lines like '0041..005A    ; Latin'."""
    out = []
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line: continue
        m = re.match(r"([0-9A-Fa-f]+)(?:\.\.([0-9A-Fa-f]+))?\s*;\s*(.+)$", line)
        if not m: continue
        start = int(m.group(1), 16)
        end = int(m.group(2), 16) if m.group(2) else start
        out.append((start, end, m.group(3).strip()))
    return out

def parse_script_aliases(text: str) -> dict[str, str]:
    """Return {LongName: ShortISO15924Code}. 'sc' = Script property."""
    out = {}
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or not line.startswith("sc ;"): continue
        parts = [p.strip() for p in line.split(";")]
        # sc ; Latn ; Latin
        if len(parts) >= 3:
            out[parts[2]] = parts[1]   # Latin -> Latn
    return out

class RangeIndex:
    """Binary-searchable list of (start, end, value)."""
    def __init__(self, ranges):
        ranges = sorted(ranges)
        self.starts = [r[0] for r in ranges]
        self.ends   = [r[1] for r in ranges]
        self.vals   = [r[2] for r in ranges]
    def lookup(self, cp: int) -> str | None:
        i = bisect.bisect_right(self.starts, cp) - 1
        if i < 0: return None
        if self.ends[i] >= cp: return self.vals[i]
        return None

# ---------------------------------------------------------------------------
# 2. Language mapping: union of Wikidata + CLDR
# ---------------------------------------------------------------------------
def build_script_to_langs():
    wd = json.loads((DATA/"wikidata_pairs.json").read_text(encoding="utf-8"))
    cldr = json.loads((DATA/"cldr_pairs.json").read_text(encoding="utf-8"))
    lnames = json.loads((DATA/"cldr_language_names.json").read_text(encoding="utf-8"))

    # script_iso -> {lang_code: {"name": ..., "sources": set(), "status": ...}}
    idx: dict[str, dict] = {}
    def add(script_iso, lang_code, name, source, status=None):
        if not script_iso or not lang_code: return
        d = idx.setdefault(script_iso, {})
        ent = d.setdefault(lang_code, {"code": lang_code, "name": name or "", "sources": set(), "status": status})
        if name and not ent["name"]: ent["name"] = name
        ent["sources"].add(source)
        if status and not ent.get("status"): ent["status"] = status

    for r in wd:
        s = r.get("script_iso")
        code = r.get("lang_iso3") or r.get("lang_iso1")
        if not s or not code: continue
        add(s, code, r.get("lang_name"), "wikidata")

    for r in cldr:
        add(r["script_code"], r["lang_code"], lnames.get(r["lang_code"], ""), "cldr", r["status"])

    # finalize: sort langs, convert sets to sorted lists
    out = {}
    for script, langs in idx.items():
        lst = sorted(langs.values(), key=lambda x: (x["name"] or x["code"]).lower())
        for e in lst:
            e["sources"] = sorted(e["sources"])
        out[script] = lst
    return out

# ---------------------------------------------------------------------------
# 3. Enrich symbols.json
# ---------------------------------------------------------------------------
def enrich():
    scripts_txt = _download(UCD_SCRIPTS, DATA/"Scripts.txt")
    blocks_txt  = _download(UCD_BLOCKS, DATA/"Blocks.txt")
    aliases_txt = _download(UCD_ALIASES, DATA/"PropertyValueAliases.txt")

    long_to_iso = parse_script_aliases(aliases_txt)          # "Latin" -> "Latn"
    script_idx  = RangeIndex(parse_ranges(scripts_txt))      # cp -> "Latin"
    block_idx   = RangeIndex(parse_ranges(blocks_txt))       # cp -> "Basic Latin"

    script_to_langs = build_script_to_langs()

    # symbols list built directly from UnicodeData.txt (was symbols.json, now removed)
    ucd_txt = (ROOT/"UnicodeData.txt").read_text(encoding="utf-8")
    symbols = []
    for line in ucd_txt.splitlines():
        parts = line.split(";")
        if len(parts) < 3 or not parts[1] or parts[1].startswith("<"):
            continue
        cp = parts[0]
        try:
            ch = chr(int(cp, 16))
        except (ValueError, OverflowError):
            continue
        symbols.append({"cp": cp, "ch": ch, "name": parts[1], "cat": parts[2]})
    print(f"[enrich] {len(symbols)} symbols", flush=True)

    # Summary index while we're iterating
    script_summary: dict[str, dict] = {}

    for s in symbols:
        cp = int(s["cp"], 16)
        long_name = script_idx.lookup(cp)
        iso = long_to_iso.get(long_name) if long_name else None
        block = block_idx.lookup(cp)
        s["script"] = iso
        s["script_name"] = long_name
        s["block"] = block
        s["languages"] = script_to_langs.get(iso, []) if iso else []

        if iso:
            agg = script_summary.setdefault(iso, {
                "code": iso, "name": long_name, "languages": s["languages"],
                "codepoint_count": 0, "samples": [],
            })
            agg["codepoint_count"] += 1
            if len(agg["samples"]) < 12 and s.get("ch") and s["ch"].strip():
                agg["samples"].append({"cp": s["cp"], "ch": s["ch"], "name": s.get("name","")})

    (DATA/"script_index.json").write_text(
        json.dumps(script_summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[enrich] wrote script_index.json", flush=True)
    return symbols, script_summary

# ---------------------------------------------------------------------------
# 4. HTML pages
# ---------------------------------------------------------------------------
CSS = """
body{font-family:system-ui,sans-serif;max-width:1100px;margin:2em auto;padding:0 1em;color:#222}
h1{margin-bottom:.2em}
.meta{color:#666;margin-bottom:1.5em}
a{color:#06c;text-decoration:none}a:hover{text-decoration:underline}
table{border-collapse:collapse;width:100%;margin:1em 0}
th,td{text-align:left;padding:.4em .6em;border-bottom:1px solid #eee;vertical-align:top}
th{background:#f6f6f6}
.glyphs{display:grid;grid-template-columns:repeat(auto-fill,minmax(80px,1fr));gap:.5em;margin:1em 0}
.glyph{border:1px solid #ddd;padding:.6em;text-align:center;border-radius:4px}
.glyph .ch{font-size:2em;line-height:1}
.glyph .cp{font-family:monospace;font-size:.75em;color:#888}
.badge{display:inline-block;font-size:.7em;padding:.1em .4em;background:#eef;border-radius:3px;margin-left:.3em;color:#446}
.badge.cldr{background:#efe;color:#464}
.badge.wikidata{background:#fee;color:#644}
.sources{font-size:.8em;color:#888}
"""

def page(title: str, body: str) -> str:
    return f"""<!doctype html><meta charset=utf-8>
<title>{html.escape(title)}</title>
<style>{CSS}</style>
<body>
{body}
"""

def build_pages(script_summary, symbols):
    # Group a larger glyph sample per script (up to 256 codepoints)
    per_script: dict[str, list[dict]] = {}
    for s in symbols:
        if s.get("script") and len(per_script.setdefault(s["script"], [])) < 256:
            per_script[s["script"]].append(s)

    # index page
    rows = []
    for iso, info in sorted(script_summary.items(), key=lambda kv: kv[1]["name"] or kv[0]):
        rows.append(
            f"<tr><td><a href='{iso}.html'>{html.escape(info['name'])}</a></td>"
            f"<td><code>{iso}</code></td>"
            f"<td>{info['codepoint_count']}</td>"
            f"<td>{len(info['languages'])}</td></tr>"
        )
    index_body = (
        "<h1>Scripts</h1>"
        f"<p class=meta>{len(script_summary)} scripts across {sum(s['codepoint_count'] for s in script_summary.values())} codepoints.</p>"
        "<table><thead><tr><th>Script</th><th>Code</th><th>Codepoints</th><th>Languages</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )
    (PAGES/"index.html").write_text(page("Scripts", index_body), encoding="utf-8")

    for iso, info in script_summary.items():
        lang_rows = []
        for l in info["languages"]:
            badges = "".join(
                f"<span class='badge {src}'>{src}</span>" for src in l["sources"]
            )
            status = f" <span class=sources>({l['status']})</span>" if l.get("status") else ""
            lang_rows.append(
                f"<tr><td>{html.escape(l['name'] or '')}</td>"
                f"<td><code>{html.escape(l['code'])}</code></td>"
                f"<td>{badges}{status}</td></tr>"
            )
        glyphs = "".join(
            f"<div class=glyph><div class=ch>{html.escape(s.get('ch','') or '')}</div>"
            f"<div class=cp>U+{s['cp']}</div></div>"
            for s in per_script.get(iso, [])
        )
        body = (
            f"<p><a href='index.html'>← all scripts</a></p>"
            f"<h1>{html.escape(info['name'])} <span class=sources>({iso})</span></h1>"
            f"<p class=meta>{info['codepoint_count']} codepoints · {len(info['languages'])} languages</p>"
            f"<h2>Languages</h2>"
            + ("<table><thead><tr><th>Name</th><th>Code</th><th>Source</th></tr></thead>"
               f"<tbody>{''.join(lang_rows)}</tbody></table>"
               if lang_rows else "<p><em>No languages linked in Wikidata or CLDR.</em></p>")
            + f"<h2>Glyphs (first {len(per_script.get(iso, []))})</h2>"
            f"<div class=glyphs>{glyphs}</div>"
        )
        (PAGES/f"{iso}.html").write_text(page(info["name"], body), encoding="utf-8")
    print(f"[pages] wrote {len(script_summary)+1} HTML files to {PAGES}", flush=True)

# ---------------------------------------------------------------------------
def main():
    symbols, script_summary = enrich()
    build_pages(script_summary, symbols)

if __name__ == "__main__":
    main()
