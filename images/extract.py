#!/usr/bin/env python3
"""One-time extractor: seed data/*.json from existing regions/*.html.

Run once to bootstrap the data directory from the hand-written HTML.
After that, edit data/*.json and regenerate with build.py.
"""
import html
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REGIONS = HERE / "regions"
DATA = HERE / "data"
DATA.mkdir(exist_ok=True)

# (slug, landing-page blurb). Title is pulled from each region's <h1>.
REGION_META = [
    ("africa", "Ife, Benin, Great Zimbabwe, Lalibela, Djenné."),
    ("egypt-nubia", "Pyramids, Nefertiti, Karnak, Abu Simbel, Meroë."),
    ("mesopotamia-persia", "Ishtar Gate, Hammurabi, Lamassu, Persepolis."),
    ("mediterranean", "Parthenon, Venus de Milo, Laocoön, Pompeii."),
    ("europe", "Kells, Chartres, Sistine Chapel, Rembrandt, Van Gogh."),
    ("islamic-world", "Alhambra, Dome of the Rock, Córdoba, Isfahan."),
    ("south-asia", "Taj Mahal, Ajanta, Khajuraho, Chola bronze, Sanchi."),
    ("east-asia", "Terracotta Army, Forbidden City, Hokusai, Hōryū-ji."),
    ("southeast-asia-oceania", "Angkor Wat, Borobudur, Bagan, Moai, Aboriginal rock art."),
    ("americas", "Teotihuacan, Palenque, Sun Stone, Machu Picchu, Nazca."),
]

WORK_PATTERN = re.compile(
    r'<article class="work">\s*'
    r'<img src="([^"]+)" alt="[^"]*"[^>]*>\s*'
    r'<div class="body">\s*'
    r'<div class="t">(.+?)</div>\s*'
    r'<div class="meta">(.+?)</div>\s*'
    r'<div class="d">(.+?)</div>\s*'
    r'</div>\s*</article>',
    re.DOTALL,
)


def extract(slug: str) -> dict:
    src = (REGIONS / f"{slug}.html").read_text(encoding="utf-8")
    title = html.unescape(re.search(r"<h1>(.+?)</h1>", src).group(1))
    subtitle = html.unescape(re.search(r'<div class="subtitle">(.+?)</div>', src).group(1))
    intro_raw = re.search(r'<p class="intro">\s*(.+?)\s*</p>', src, re.DOTALL).group(1)
    intro = html.unescape(re.sub(r"\s+", " ", intro_raw).strip())

    works = [
        {
            "title": html.unescape(m.group(2)),
            "meta": html.unescape(m.group(3)),
            "desc": html.unescape(m.group(4)),
            "image": m.group(1),
        }
        for m in WORK_PATTERN.finditer(src)
    ]

    return {
        "title": title,
        "subtitle": subtitle,
        "intro": intro,
        "works": works,
    }


def main() -> None:
    regions_index = []
    for slug, blurb in REGION_META:
        data = extract(slug)
        (DATA / f"{slug}.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        regions_index.append({"slug": slug, "title": data["title"], "blurb": blurb})
        print(f"  {slug}: {len(data['works'])} works")

    meta = {
        "regions": regions_index,
        "museums": [
            {
                "slug": "louvre",
                "title": "The Louvre",
                "blurb": "Wings, history, and selected works. Paris, France.",
                "href": "louvre/",
            }
        ],
    }
    (DATA / "regions.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"\nExtracted {len(REGION_META)} regions to data/")


if __name__ == "__main__":
    main()
