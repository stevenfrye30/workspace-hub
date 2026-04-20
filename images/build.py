#!/usr/bin/env python3
"""Generate world-gallery HTML from data/ JSON.

Reads:
    data/regions.json       — list of regions (+ continent) and museums
    data/<slug>.json        — per-region content (title, subtitle, intro, works)

Writes:
    index.html              — landing page (regions by continent + artists)
    regions/<slug>.html     — one page per region, works bucketed by era,
                              with prev/next footer
    artists.html            — works grouped by named artist
    timeline.html           — every work in chronological order, era-banded
    all.html                — every work on one page, live search + era
                              filter + by-year / by-region sort

Shared: style.css and lightbox.js at the top level.

Adding a new work: edit data/<slug>.json, rerun `python build.py`.
Adding a new region: create data/<slug>.json, add entry in data/regions.json,
rerun.
"""
import json
import re
import unicodedata
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
REGIONS_OUT = HERE / "regions"


def h(s: str) -> str:
    return escape(s, quote=False)


def h_attr(s: str) -> str:
    return escape(s, quote=True)


def slugify(s: str) -> str:
    # Strip diacritics first so "Édouard" -> "edouard", "Tōshūsai" -> "toshusai".
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE).strip().lower()
    return re.sub(r"[\s_-]+", "-", s)


def resolve_href(target: str, ctx_prefix: str = "") -> str:
    """Prepend ctx_prefix to internal page links (relative paths).
    Absolute URLs (http, https, /, #) pass through unchanged."""
    if target.startswith(("http://", "https://", "/", "#")):
        return target
    return ctx_prefix + target


def normalize_search(s: str) -> str:
    """Lowercase + strip diacritics so searches like 'horyu' match 'Hōryū-ji'."""
    s = s.lower()
    return "".join(
        c for c in unicodedata.normalize("NFKD", s)
        if not unicodedata.combining(c)
    )


def resolve_image(url: str, prefix: str = "") -> str:
    """Prepend `prefix` to relative image paths (e.g. `media/foo.jpg` on
    region pages, which live one directory below the media folder).
    Absolute URLs (http, https, /) pass through unchanged."""
    if url.startswith(("http://", "https://", "/")):
        return url
    return prefix + url


# Era buckets used to sub-group works on region pages and the timeline,
# and to power the filter chips on All Works. Slugs must match the JS
# `eraBounds` keys in ALL_TPL.
ERAS = [
    (-10**9, -1000, "Before 1000 BCE", "pre-1000bce"),
    (-1000, 0, "1000 BCE \u2013 0", "1000bce-0"),
    (0, 500, "0 \u2013 500 CE", "0-500"),
    (500, 1000, "500 \u2013 1000", "500-1000"),
    (1000, 1500, "1000 \u2013 1500", "1000-1500"),
    (1500, 1800, "1500 \u2013 1800", "1500-1800"),
    (1800, 10**9, "1800 onward", "1800+"),
]


def bucket_by_era(works: list[dict]) -> list[tuple[str, list[dict]]]:
    """Return works grouped by era label, preserving the ERAS order.
    Only returns buckets that have at least one work."""
    blocks = []
    for lo, hi, label, _slug in ERAS:
        era_works = [w for w in works if lo <= w.get("year", 0) < hi]
        if era_works:
            era_works.sort(key=lambda w: w.get("year", 0))
            blocks.append((label, era_works))
    return blocks


_SURNAME_OVERRIDES = {
    "Pieter Bruegel the Elder": "bruegel",
    "Leonardo da Vinci": "leonardo",
    "Gu Kaizhi": "gu",
    "Guo Xi": "guo",
    "Zhang Zeduan": "zhang",
}


def artist_sort_key(name: str) -> tuple[str, str]:
    if name in _SURNAME_OVERRIDES:
        return (_SURNAME_OVERRIDES[name], name.lower())
    parts = name.replace(".", "").split()
    surname = parts[-1] if parts else name
    return (surname.lower(), name.lower())


# ---------------------------------------------------------------------------
# Shared nav
# ---------------------------------------------------------------------------

NAV_TPL = """<nav class="top-nav">
  <a href="{workspace}" class="nav-ws" title="Back to Workspace">&larr;</a>
  <a href="{home}" class="nav-brand">World Gallery</a>
  <div class="nav-links">
    <a href="{home}"{cls_regions}>Regions</a>
    <a href="{artists}"{cls_artists}>Artists</a>
    <a href="{timeline}"{cls_timeline}>Timeline</a>
    <a href="{all_}"{cls_all}>All works</a>
  </div>
</nav>
"""


def make_nav(current: str, in_subdir: bool = False) -> str:
    prefix = "../" if in_subdir else ""
    return NAV_TPL.format(
        workspace=f"{prefix}../",
        home=f"{prefix}index.html",
        artists=f"{prefix}artists.html",
        timeline=f"{prefix}timeline.html",
        all_=f"{prefix}all.html",
        cls_regions=' class="active"' if current == "regions" else "",
        cls_artists=' class="active"' if current == "artists" else "",
        cls_timeline=' class="active"' if current == "timeline" else "",
        cls_all=' class="active"' if current == "all" else "",
    )


def format_year(year: int) -> str:
    if year < 0:
        return f"{-year} BCE"
    if year < 1000:
        return f"{year} CE"
    return str(year)


# ---------------------------------------------------------------------------
# Work card
# ---------------------------------------------------------------------------

WORK_TPL = """    <article class="work">
      <img src="{image}" alt="{alt}" loading="lazy">
      <div class="body">
        <div class="t">{title}</div>
{artist}        <div class="meta">{meta}</div>
        <div class="d">{desc}</div>
      </div>
    </article>
"""

ALL_WORK_TPL = """    <article class="work" data-search="{search}" data-year="{year}">
      <img src="{image}" alt="{alt}" loading="lazy">
      <div class="body">
        {region_badge}
        <div class="t">{title}</div>
{artist}        <div class="meta">{meta}</div>
        <div class="d">{desc}</div>
      </div>
    </article>
"""

TL_WORK_TPL = """      <article class="work tl-entry" data-year="{year}">
        <div class="tl-year">{year_display}</div>
        <img src="{image}" alt="{alt}" loading="lazy">
        <div class="body">
          {region_badge}
          <div class="t">{title}</div>
{artist}          <div class="meta">{meta}</div>
          <div class="d">{desc}</div>
        </div>
      </article>
"""


def _artist_line(w: dict, ctx_prefix: str, indent: str = "        ") -> str:
    artist = w.get("artist")
    if not artist:
        return ""
    slug = slugify(artist)
    href = resolve_href(f"artists/{slug}.html", ctx_prefix)
    return f'{indent}<div class="work-artist">by <a href="{href}">{h(artist)}</a></div>\n'


def _region_badge(region_title: str, region_slug: str, ctx_prefix: str) -> str:
    href = resolve_href(f"regions/{region_slug}.html", ctx_prefix)
    return f'<a class="region-badge" href="{href}">{h(region_title)}</a>'


def render_work(w: dict, ctx_prefix: str = "") -> str:
    return WORK_TPL.format(
        image=resolve_image(w["image"], ctx_prefix),
        alt=h(w["title"]),
        title=h(w["title"]),
        artist=_artist_line(w, ctx_prefix),
        meta=h(w["meta"]),
        desc=h(w["desc"]),
    )


def render_all_work(w: dict, region_title: str, region_slug: str, ctx_prefix: str = "") -> str:
    tokens = [w["title"], w["meta"], w.get("desc", ""), w.get("artist", ""), region_title]
    search = normalize_search(" ".join(t for t in tokens if t))
    return ALL_WORK_TPL.format(
        image=resolve_image(w["image"], ctx_prefix),
        alt=h(w["title"]),
        title=h(w["title"]),
        artist=_artist_line(w, ctx_prefix),
        meta=h(w["meta"]),
        desc=h(w["desc"]),
        region_badge=_region_badge(region_title, region_slug, ctx_prefix),
        search=h_attr(search),
        year=w.get("year", 0),
    )


def render_tl_work(w: dict, region_title: str, region_slug: str, ctx_prefix: str = "") -> str:
    return TL_WORK_TPL.format(
        image=resolve_image(w["image"], ctx_prefix),
        alt=h(w["title"]),
        title=h(w["title"]),
        artist=_artist_line(w, ctx_prefix, indent="          "),
        meta=h(w["meta"]),
        desc=h(w["desc"]),
        region_badge=_region_badge(region_title, region_slug, ctx_prefix),
        year=w.get("year", 0),
        year_display=h(format_year(w.get("year", 0))),
    )


# ---------------------------------------------------------------------------
# Region page
# ---------------------------------------------------------------------------

REGION_TPL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} &mdash; World Gallery</title>
<link rel="stylesheet" href="../style.css">
</head>
<body>
<!-- Generated by build.py. Edit data/{slug}.json and rerun. -->
{nav}
<div class="page">
  <header class="page-header">
    <div>
      <h1>{title}</h1>
      <div class="subtitle">{subtitle}</div>
    </div>
  </header>
  <p class="intro">
    {intro}
  </p>
  <div class="hint">Click any image to enlarge. Use &larr; &rarr; or close with Esc.</div>
{works}
  <footer class="region-footer">
    <a href="{prev_href}"><span class="arrow">&larr;</span>{prev_title}</a>
    <a href="{next_href}">{next_title}<span class="arrow">&rarr;</span></a>
  </footer>
  <footer class="page-footer">
    Images via <a href="https://commons.wikimedia.org/" target="_blank" rel="noopener">Wikimedia Commons</a>. Click any image to open it and see its source.
  </footer>
</div>
<script src="../lightbox.js"></script>
</body>
</html>
"""


def build_region(slug: str, data: dict, neighbors: tuple[dict, dict]) -> int:
    blocks = bucket_by_era(data["works"])
    parts = []
    for label, era_works in blocks:
        parts.append(f'  <h3 class="era">{h(label)}</h3>')
        parts.append('  <div class="grid">')
        for w in era_works:
            parts.append(render_work(w, ctx_prefix="../").rstrip("\n"))
        parts.append("  </div>")
    works_html = "\n".join(parts)

    prev, next_ = neighbors
    html_out = REGION_TPL.format(
        slug=slug,
        title=h(data["title"]),
        subtitle=h(data["subtitle"]),
        intro=h(data["intro"]),
        works=works_html,
        nav=make_nav("regions", in_subdir=True),
        prev_href=f"{prev['slug']}.html",
        prev_title=h(prev["title"]),
        next_href=f"{next_['slug']}.html",
        next_title=h(next_["title"]),
    )
    (REGIONS_OUT / f"{slug}.html").write_text(html_out, encoding="utf-8")
    return len(data["works"])


# ---------------------------------------------------------------------------
# Artists page
# ---------------------------------------------------------------------------

ARTISTS_DIR_TPL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>By Artist &mdash; World Gallery</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<!-- Generated by build.py. -->
@@NAV@@
<div class="page">
  <header class="page-header">
    <div>
      <h1>By Artist</h1>
      <div class="subtitle">@@COUNT@@ named makers. Click a name to see all of their works. Anonymous and collective works live in the regional views.</div>
    </div>
  </header>
  <div class="card-grid">
@@CARDS@@
  </div>
  <footer class="page-footer">
    Images via <a href="https://commons.wikimedia.org/" target="_blank" rel="noopener">Wikimedia Commons</a>. Click any image to open it and see its source.
  </footer>
</div>
</body>
</html>
"""

ARTIST_PAGE_TPL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name} &mdash; World Gallery</title>
<link rel="stylesheet" href="../style.css">
</head>
<body>
<!-- Generated by build.py. -->
{nav}
<div class="page">
  <header class="page-header">
    <div>
      <h1>{name}</h1>
      <div class="subtitle">{count} {noun} in the gallery.</div>
    </div>
  </header>
  <div class="hint">Click any image to enlarge. Use &larr; &rarr; or close with Esc.</div>
  <div class="grid">
{works}
  </div>
  <footer class="region-footer">
    <a href="{prev_href}"><span class="arrow">&larr;</span>{prev_name}</a>
    <a href="{next_href}">{next_name}<span class="arrow">&rarr;</span></a>
  </footer>
  <footer class="page-footer">
    Images via <a href="https://commons.wikimedia.org/" target="_blank" rel="noopener">Wikimedia Commons</a>. Click any image to open it and see its source.
  </footer>
</div>
<script src="../lightbox.js"></script>
</body>
</html>
"""


def collect_artists(meta: dict) -> dict[str, list[dict]]:
    artists: dict[str, list[dict]] = {}
    for r in meta["regions"]:
        data = json.loads((DATA / f"{r['slug']}.json").read_text(encoding="utf-8"))
        for w in data["works"]:
            name = w.get("artist")
            if name:
                artists.setdefault(name, []).append(w)
    return artists


def build_artists(artists: dict[str, list[dict]]) -> tuple[int, int]:
    artists_out = HERE / "artists"
    artists_out.mkdir(exist_ok=True)
    nav_top = make_nav("artists")

    if not artists:
        html_out = (
            ARTISTS_DIR_TPL
            .replace("@@NAV@@", nav_top)
            .replace("@@COUNT@@", "0")
            .replace("@@CARDS@@", '    <p class="intro">No artist-tagged works yet.</p>')
        )
        (HERE / "artists.html").write_text(html_out, encoding="utf-8")
        return 0, 0

    names = sorted(artists.keys(), key=artist_sort_key)
    total_works = 0

    # Directory page: one card per artist, linking to artists/<slug>.html.
    cards = []
    for name in names:
        slug = slugify(name)
        count = len(artists[name])
        noun = "work" if count == 1 else "works"
        cards.append(
            f'    <a class="card" href="artists/{slug}.html">\n'
            f'      <div class="t">{h(name)}</div>\n'
            f'      <div class="d">{count} {noun}</div>\n'
            f'    </a>'
        )
    dir_html = (
        ARTISTS_DIR_TPL
        .replace("@@NAV@@", nav_top)
        .replace("@@COUNT@@", str(len(names)))
        .replace("@@CARDS@@", "\n".join(cards))
    )
    (HERE / "artists.html").write_text(dir_html, encoding="utf-8")

    # Per-artist detail pages at artists/<slug>.html, with wrap-around
    # prev/next alphabetical navigation.
    nav_detail = make_nav("artists", in_subdir=True)
    for i, name in enumerate(names):
        slug = slugify(name)
        works = sorted(artists[name], key=lambda w: w.get("year", 0))
        works_html = "".join(render_work(w, ctx_prefix="../") for w in works).rstrip()
        prev_name = names[(i - 1) % len(names)]
        next_name = names[(i + 1) % len(names)]
        count = len(works)
        noun = "work" if count == 1 else "works"
        html_out = ARTIST_PAGE_TPL.format(
            name=h(name),
            count=count,
            noun=noun,
            works=works_html,
            nav=nav_detail,
            prev_href=f"{slugify(prev_name)}.html",
            prev_name=h(prev_name),
            next_href=f"{slugify(next_name)}.html",
            next_name=h(next_name),
        )
        (artists_out / f"{slug}.html").write_text(html_out, encoding="utf-8")
        total_works += count

    return len(names), total_works


# ---------------------------------------------------------------------------
# All works page (with live search)
# ---------------------------------------------------------------------------

ALL_TPL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>All Works &mdash; World Gallery</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<!-- Generated by build.py. -->
@@NAV@@
<div class="page">
  <header class="page-header">
    <div>
      <h1>All Works</h1>
      <div class="subtitle">Every piece, searchable. Type a title, culture, artist, period, or region.</div>
    </div>
  </header>
  <div class="all-search">
    <input type="text" id="search-input" placeholder="Search @@TOTAL@@ works&hellip; (e.g. Monet, Buddhist, bronze)" autofocus>
    <div class="result-count" id="result-count">@@TOTAL@@ works</div>
  </div>
  <div class="filter-controls">
    <div class="filter-chips">
@@CHIPS@@
    </div>
    <div class="sort-toggle">
      <button class="sort-btn active" data-sort="region">By region</button>
      <button class="sort-btn" data-sort="year">Chronological</button>
    </div>
  </div>
  <div class="grid" id="all-grid">
@@WORKS@@
  </div>
  <div class="no-results" id="no-results">No works match that search.</div>
  <footer class="page-footer">
    Images via <a href="https://commons.wikimedia.org/" target="_blank" rel="noopener">Wikimedia Commons</a>. Click any image to open it and see its source.
  </footer>
</div>
<script src="lightbox.js"></script>
<script>
(function() {
  const input = document.getElementById('search-input');
  const grid = document.getElementById('all-grid');
  const works = Array.from(grid.querySelectorAll('.work'));
  const count = document.getElementById('result-count');
  const empty = document.getElementById('no-results');
  const total = works.length;

  // Remember the original region-grouped order so "By region" can restore it.
  works.forEach((w, i) => { w.dataset.origIndex = i; });

  const eraBounds = {
    'all': [null, null],
    'pre-1000bce': [null, -1000],
    '1000bce-0': [-1000, 0],
    '0-500': [0, 500],
    '500-1000': [500, 1000],
    '1000-1500': [1000, 1500],
    '1500-1800': [1500, 1800],
    '1800+': [1800, null]
  };
  let currentEra = 'all';

  function normalize(s) {
    return s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  }

  function matchEra(year, era) {
    const [lo, hi] = eraBounds[era];
    if (lo !== null && year < lo) return false;
    if (hi !== null && year >= hi) return false;
    return true;
  }

  function apply() {
    const q = normalize(input.value.trim());
    let visible = 0;
    for (const w of works) {
      const year = +w.dataset.year;
      const textMatch = !q || w.dataset.search.includes(q);
      const eraMatch = matchEra(year, currentEra);
      const match = textMatch && eraMatch;
      w.style.display = match ? '' : 'none';
      if (match) visible++;
    }
    const filtering = q || currentEra !== 'all';
    count.textContent = filtering ? (visible + ' of ' + total + ' works') : (total + ' works');
    empty.style.display = (visible === 0) ? 'block' : 'none';
  }

  input.addEventListener('input', apply);

  document.querySelectorAll('.era-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('.era-chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      currentEra = chip.dataset.era;
      apply();
    });
  });

  document.querySelectorAll('.sort-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.sort-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const mode = btn.dataset.sort;
      const sorted = works.slice();
      if (mode === 'year') {
        sorted.sort((a, b) => +a.dataset.year - +b.dataset.year);
      } else {
        sorted.sort((a, b) => +a.dataset.origIndex - +b.dataset.origIndex);
      }
      for (const w of sorted) grid.appendChild(w);
    });
  });
})();
</script>
</body>
</html>
"""

TIMELINE_TPL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Timeline &mdash; World Gallery</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<!-- Generated by build.py. -->
@@NAV@@
<div class="page">
  <header class="page-header">
    <div>
      <h1>Timeline</h1>
      <div class="subtitle">All @@TOTAL@@ works in chronological order &mdash; cross-cultural contemporaries lined up.</div>
    </div>
  </header>
  <div class="hint">Click any image to enlarge. Use &larr; &rarr; or close with Esc.</div>
@@ERAS@@
  <footer class="page-footer">
    Images via <a href="https://commons.wikimedia.org/" target="_blank" rel="noopener">Wikimedia Commons</a>. Click any image to open it and see its source.
  </footer>
</div>
<script src="lightbox.js"></script>
</body>
</html>
"""

ERA_CHIP_TPL = '      <button class="era-chip" data-era="{era}">{label}<span class="c">{count}</span></button>\n'


def build_all_works(meta: dict) -> int:
    works_html_chunks = []
    all_works_flat: list[dict] = []
    total = 0
    for r in meta["regions"]:
        data = json.loads((DATA / f"{r['slug']}.json").read_text(encoding="utf-8"))
        for w in data["works"]:
            works_html_chunks.append(render_all_work(w, r["title"], r["slug"]))
            all_works_flat.append(w)
            total += 1
    works_html = "".join(works_html_chunks).rstrip()

    # Era filter chips with per-bucket counts.
    chips = [f'      <button class="era-chip active" data-era="all">All<span class="c">{total}</span></button>']
    for lo, hi, label, slug in ERAS:
        count = sum(1 for w in all_works_flat if lo <= w.get("year", 0) < hi)
        if count == 0:
            continue
        chips.append(
            ERA_CHIP_TPL.format(era=slug, label=h(label), count=count).rstrip("\n")
        )
    chips_html = "\n".join(chips)

    nav = make_nav("all")
    html_out = (
        ALL_TPL
        .replace("@@NAV@@", nav)
        .replace("@@WORKS@@", works_html)
        .replace("@@CHIPS@@", chips_html)
        .replace("@@TOTAL@@", str(total))
    )
    (HERE / "all.html").write_text(html_out, encoding="utf-8")
    return total


def build_timeline(meta: dict) -> int:
    # Flatten all (work, region_title, region_slug) triples, then bucket.
    triples: list[tuple[dict, str, str]] = []
    for r in meta["regions"]:
        data = json.loads((DATA / f"{r['slug']}.json").read_text(encoding="utf-8"))
        for w in data["works"]:
            triples.append((w, r["title"], r["slug"]))

    sections = []
    for lo, hi, label, _slug in ERAS:
        era_triples = [(w, rt, rs) for w, rt, rs in triples if lo <= w.get("year", 0) < hi]
        if not era_triples:
            continue
        era_triples.sort(key=lambda x: x[0].get("year", 0))
        body = "".join(render_tl_work(w, rt, rs) for w, rt, rs in era_triples).rstrip()
        sections.append(
            f'  <section class="tl-era" id="era-{_slug}">\n'
            f'    <h2 class="tl-era-title">{h(label)}<span class="tl-era-count">{len(era_triples)} works</span></h2>\n'
            f'    <div class="grid">\n{body}\n    </div>\n'
            f'  </section>'
        )
    eras_html = "\n".join(sections)

    html_out = (
        TIMELINE_TPL
        .replace("@@NAV@@", make_nav("timeline"))
        .replace("@@TOTAL@@", str(len(triples)))
        .replace("@@ERAS@@", eras_html)
    )
    (HERE / "timeline.html").write_text(html_out, encoding="utf-8")
    return len(triples)


# ---------------------------------------------------------------------------
# Landing page
# ---------------------------------------------------------------------------

TILE_TPL = """  <a class="region-tile" href="regions/{slug}.html">
    <img class="tile-img" src="{image}" alt="" loading="lazy">
    <div class="tile-overlay">
      <div class="tile-title">{title}</div>
      <div class="tile-blurb">{blurb}</div>
    </div>
  </a>
"""


def _region_hero_image(region: dict) -> str:
    """Return the image URL for a region's landing tile.
    Prefers an explicit `hero` field in regions.json (a path or URL); falls
    back to the first work in the region's data file."""
    hero = region.get("hero")
    if hero:
        return hero
    data = json.loads((DATA / f"{region['slug']}.json").read_text(encoding="utf-8"))
    works = data.get("works") or []
    return works[0]["image"] if works else ""


def build_region_tiles(regions: list[dict]) -> str:
    tiles = []
    for r in regions:
        image = _region_hero_image(r)
        if not image:
            continue
        tiles.append(TILE_TPL.format(
            slug=r["slug"],
            image=h_attr(image),
            title=h(r["title"]),
            blurb=h(r["blurb"]),
        ))
    return '<div class="region-tiles">\n' + "".join(tiles).rstrip() + '\n  </div>'


INDEX_TPL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>World Gallery</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<!-- Generated by build.py. Edit data/regions.json and per-region files, then rerun. -->
@@NAV@@
<div class="page">
  <header class="page-header">
    <div>
      <h1>World Gallery</h1>
      <div class="subtitle">Art and architecture from everywhere &mdash; @@TOTAL_COUNT@@ works, @@REGION_COUNT@@ regions, @@ARTIST_COUNT@@ named artists.</div>
    </div>
  </header>

  <h2 class="section">By region</h2>
  @@REGION_TILES@@

  <h2 class="section">By artist <span class="count">featured makers &mdash; see all @@ARTIST_COUNT@@ &rarr;</span></h2>
  <div class="card-grid">
@@ARTIST_CARDS@@
  </div>
  <footer class="page-footer">
    Images via <a href="https://commons.wikimedia.org/" target="_blank" rel="noopener">Wikimedia Commons</a>. Click any image to open it and see its source.
  </footer>
</div>
</body>
</html>
"""

CARD_TPL = """    <a class="card" href="{href}">
      <div class="t">{title}</div>
      <div class="d">{blurb}</div>
    </a>
"""

CARD_MORE_TPL = """    <a class="card card-more" href="{href}">
      <div>
        <div class="t">{title}</div>
        <div class="d">{blurb}</div>
      </div>
    </a>
"""


def build_index(meta: dict, counts: dict[str, int], artists: dict[str, list[dict]]) -> None:
    region_tiles_html = build_region_tiles(meta["regions"])

    # Featured artists: those with >= 2 works, sorted by count desc then surname.
    featured = sorted(
        ((name, works) for name, works in artists.items() if len(works) >= 2),
        key=lambda pair: (-len(pair[1]), artist_sort_key(pair[0])),
    )
    artist_cards = "".join(
        CARD_TPL.format(
            href=f"artists/{slugify(name)}.html",
            title=h(name),
            blurb=f"{len(works)} works",
        )
        for name, works in featured
    )
    artist_cards += CARD_MORE_TPL.format(
        href="artists.html",
        title=h("View all artists"),
        blurb=f"{len(artists)} named makers",
    )
    artist_cards = artist_cards.rstrip()

    total = sum(counts.values())
    html_out = (
        INDEX_TPL
        .replace("@@NAV@@", make_nav("regions"))
        .replace("@@REGION_TILES@@", region_tiles_html)
        .replace("@@ARTIST_CARDS@@", artist_cards)
        .replace("@@TOTAL_COUNT@@", str(total))
        .replace("@@REGION_COUNT@@", str(len(meta["regions"])))
        .replace("@@ARTIST_COUNT@@", str(len(artists)))
    )
    (HERE / "index.html").write_text(html_out, encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    meta = json.loads((DATA / "regions.json").read_text(encoding="utf-8"))
    regions = meta["regions"]
    counts: dict[str, int] = {}
    for i, r in enumerate(regions):
        slug = r["slug"]
        data = json.loads((DATA / f"{slug}.json").read_text(encoding="utf-8"))
        prev = regions[(i - 1) % len(regions)]
        next_ = regions[(i + 1) % len(regions)]
        counts[slug] = build_region(slug, data, (prev, next_))
        print(f"  {slug}: {counts[slug]} works")
    artists = collect_artists(meta)
    n_artists, n_artist_works = build_artists(artists)
    total_all = build_all_works(meta)
    build_timeline(meta)
    build_index(meta, counts, artists)
    print(
        f"\nBuilt {len(regions)} regions + index + artists + timeline + all. "
        f"{total_all} works total ({n_artist_works} by {n_artists} named artists)."
    )


if __name__ == "__main__":
    main()
