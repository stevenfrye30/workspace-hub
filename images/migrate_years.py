#!/usr/bin/env python3
"""One-shot: infer a `year` (int) for every work in data/*.json that lacks one.

Parses the `meta` string with a stack of regexes, picking the earliest plausible
date. Negative = BCE. Works that already carry `year` are left alone.

Prints entries it couldn't parse so you can fix them by hand.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"

CENTURY_RE = re.compile(
    r"(\d{1,2})(?:st|nd|rd|th)\s*(?:–|-)\s*(\d{1,2})(?:st|nd|rd|th)\s*c\.?(?:\s*(BCE))?",
    re.IGNORECASE,
)
SINGLE_CENTURY_RE = re.compile(
    r"(?:(?:late|early|mid(?:-|\s))\s*)?(\d{1,2})(?:st|nd|rd|th)\s*c\.?(?:\s*(BCE))?",
    re.IGNORECASE,
)
YEAR_RANGE_RE = re.compile(r"(\d{3,4})\s*(?:–|-)\s*(\d{3,4})(?:\s*(BCE))?", re.IGNORECASE)
SINGLE_YEAR_RE = re.compile(r"(?:c\.?\s*|around\s*)?(\d{3,4})(?:\s*(BCE|CE))?", re.IGNORECASE)
BCE_RANGE_RE = re.compile(
    r"(\d{1,5})\s*(?:–|-)\s*(\d{1,5})\s*BCE", re.IGNORECASE
)
BCE_SINGLE_RE = re.compile(
    r"(?:c\.?\s*|around\s*)?(\d{1,5})\s*BCE", re.IGNORECASE
)
CE_RANGE_RE = re.compile(
    r"(\d{1,4})\s*(?:–|-)\s*(\d{1,4})\s*CE\b", re.IGNORECASE
)
CE_SINGLE_RE = re.compile(
    r"(?:c\.?\s*|buried\s*|around\s*)?(\d{1,4})\s*CE\b", re.IGNORECASE
)
MIXED_BCE_CE_RE = re.compile(
    r"(\d{1,5})\s*BCE\s*(?:–|-)\s*(\d{1,4})\s*CE", re.IGNORECASE
)
MILLENNIUM_RE = re.compile(
    r"(\d)(?:st|nd|rd|th)\s*millennium\s*(BCE)?", re.IGNORECASE
)

# Titles whose meta has no date — hand-set a representative year.
MANUAL: dict[str, int] = {
    "Senufo Sculpture": 1850,
    "Asmat Carving": 1900,
    "Tā Moko": 1700,
    "Uluru": -30000,
    "Tongkonan": 1600,
    "Hei-tiki": 1700,
    "Indigenous Australian Art": -15000,
    "Rongorongo": 1700,
}


def century_to_year(century: int, bce: bool = False) -> int:
    """Return the middle year of a century (1st c. CE → 50; 5th c. BCE → -450)."""
    if bce:
        return -(century * 100) + 50
    return (century - 1) * 100 + 50


def parse_year(meta: str) -> int | None:
    s = meta

    # Mixed BCE → CE range, e.g. "54 BCE – 20 CE" → -54 (earliest).
    m = MIXED_BCE_CE_RE.search(s)
    if m:
        return -int(m.group(1))

    # BCE range, e.g. "c. 130–100 BCE" or "c. 2600–2350 BCE"
    m = BCE_RANGE_RE.search(s)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        return -((a + b) // 2)

    # Single BCE year, e.g. "c. 539 BCE" or "15 BCE"
    m = BCE_SINGLE_RE.search(s)
    if m:
        return -int(m.group(1))

    # CE range, e.g. "70–80 CE" or "1–25 CE"
    m = CE_RANGE_RE.search(s)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        return (a + b) // 2

    # Single CE year, e.g. "79 CE" or "15 CE"
    m = CE_SINGLE_RE.search(s)
    if m:
        return int(m.group(1))

    # Century range, e.g. "11th–15th c."
    m = CENTURY_RE.search(s)
    if m:
        a = int(m.group(1))
        b = int(m.group(2))
        bce = bool(m.group(3))
        # midpoint century
        mid = (a + b) / 2
        if bce:
            return int(-(mid * 100) + 50)
        return int((mid - 1) * 100 + 50)

    # Single century, e.g. "12th c." or "9th c. BCE" or "late 15th c."
    m = SINGLE_CENTURY_RE.search(s)
    if m:
        c = int(m.group(1))
        bce = bool(m.group(2))
        year = century_to_year(c, bce)
        # "late" → shift later (or earlier BCE)
        before_str = s[max(0, m.start() - 10):m.start()].lower()
        if "late" in before_str:
            year += 30 if not bce else -30
        elif "early" in before_str:
            year -= 30 if not bce else -30
        return year

    # Millennium, e.g. "3rd millennium BCE"
    m = MILLENNIUM_RE.search(s)
    if m:
        mil = int(m.group(1))
        bce = bool(m.group(2))
        if bce:
            return -(mil - 1) * 1000 - 500
        return (mil - 1) * 1000 + 500

    # Year range, e.g. "1818–1819" or "1610–1614"
    m = YEAR_RANGE_RE.search(s)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        bce = bool(m.group(3))
        val = (a + b) // 2
        return -val if bce else val

    # Single year, e.g. "c. 1665" or "1563"
    m = SINGLE_YEAR_RE.search(s)
    if m:
        y = int(m.group(1))
        tag = (m.group(2) or "").upper()
        if tag == "BCE":
            return -y
        return y

    return None


def main() -> None:
    unresolved = []
    total_checked = 0
    touched = 0
    for path in sorted(DATA.glob("*.json")):
        if path.name == "regions.json":
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        changed = False
        for w in data.get("works", []):
            total_checked += 1
            if "year" in w:
                continue
            y = MANUAL.get(w["title"]) or parse_year(w["meta"])
            if y is None:
                unresolved.append((path.stem, w["title"], w["meta"]))
                continue
            w["year"] = y
            touched += 1
            changed = True
        if changed:
            path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
    print(f"Inferred year for {touched} of {total_checked} works.")
    if unresolved:
        print(f"\n{len(unresolved)} unresolved -- add `year` by hand:")
        for slug, title, meta in unresolved:
            line = f"  [{slug}] {title!r}  meta={meta!r}"
            print(line.encode("ascii", "replace").decode("ascii"))


if __name__ == "__main__":
    main()
