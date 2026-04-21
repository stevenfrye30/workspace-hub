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
<!-- Generated by build.py. Data in ../works.json. -->
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
  <div class="filter-controls">
    <div class="filter-chips" id="r-era-chips">
{era_chips}
    </div>
    <div class="filter-chips" id="r-cat-chips" style="max-width:100%;">
{cat_chips}
    </div>
  </div>
  <div id="r-container"></div>
  <div class="load-more-wrap">
    <button id="r-load-more" class="load-more-btn" hidden>Show more &darr;</button>
  </div>
  <footer class="region-footer">
    <a href="{prev_href}"><span class="arrow">&larr;</span>{prev_title}</a>
    <a href="{next_href}">{next_title}<span class="arrow">&rarr;</span></a>
  </footer>
  <footer class="page-footer">
    Images via <a href="https://commons.wikimedia.org/" target="_blank" rel="noopener">Wikimedia Commons</a>. Click any image to open it and see its source.
  </footer>
</div>
<script src="../lightbox.js"></script>
<script>
(function() {{
  const REGION = "{slug}";
  const PAGE_SIZE = 300;
  const container = document.getElementById('r-container');
  const loadMore = document.getElementById('r-load-more');
  const eraBounds = {{
    'all': [null, null], 'pre-1000bce': [null, -1000], '1000bce-0': [-1000, 0],
    '0-500': [0, 500], '500-1000': [500, 1000], '1000-1500': [1000, 1500],
    '1500-1800': [1500, 1800], '1800+': [1800, null]
  }};
  const eraLabels = {{
    'pre-1000bce': 'Before 1000 BCE', '1000bce-0': '1000 BCE – 0',
    '0-500': '0 – 500 CE', '500-1000': '500 – 1000', '1000-1500': '1000 – 1500',
    '1500-1800': '1500 – 1800', '1800+': '1800 onward'
  }};

  let works = [];
  let filtered = [];
  let rendered = 0;
  let currentEra = 'all';
  let currentCat = 'all';

  function eraFor(y) {{
    for (const [slug, [lo, hi]] of Object.entries(eraBounds)) {{
      if (slug === 'all') continue;
      if ((lo === null || y >= lo) && (hi === null || y < hi)) return slug;
    }}
    return 'all';
  }}
  function matchEra(y, era) {{
    const [lo, hi] = eraBounds[era];
    if (lo !== null && y < lo) return false;
    if (hi !== null && y >= hi) return false;
    return true;
  }}

  function cardHtml(w) {{
    const artistLine = w.a ? '<div class="work-artist">by <a href="../artists/' + w.as + '.html">' + w.a + '</a></div>' : '';
    const desc = w.d ? '<div class="d">' + w.d + '</div>' : '';
    return (
      '<article class="work">' +
      '<img src="' + w.u + '" alt="' + w.t + '" loading="lazy">' +
      '<div class="body">' +
      '<div class="t">' + w.t + '</div>' +
      artistLine +
      '<div class="meta">' + w.m + '</div>' +
      desc +
      '</div></article>'
    );
  }}

  function renderAll() {{
    const sliceSoFar = filtered.slice(0, rendered);
    let out = '';
    let lastEra = null;
    let open = false;
    for (const w of sliceSoFar) {{
      const e = eraFor(w.y || 0);
      if (e !== lastEra) {{
        if (open) out += '</div>';
        const cnt = filtered.filter(x => eraFor(x.y || 0) === e).length;
        out += '<h3 class="era">' + (eraLabels[e] || e) + ' <span style="color:var(--muted);font-style:italic;font-weight:normal;text-transform:none;letter-spacing:normal;font-size:12px;margin-left:8px;">' + cnt + ' works</span></h3><div class="grid">';
        open = true;
        lastEra = e;
      }}
      out += cardHtml(w);
    }}
    if (open) out += '</div>';
    container.innerHTML = out;
  }}

  function renderBatch() {{
    const next = filtered.slice(rendered, rendered + PAGE_SIZE);
    if (next.length === 0) {{ loadMore.hidden = true; return; }}
    rendered += next.length;
    renderAll();
    loadMore.hidden = rendered >= filtered.length;
  }}

  function applyFilter() {{
    filtered = works.filter(w => {{
      if (w.rs !== REGION) return false;
      if (currentEra !== 'all' && !matchEra(w.y || 0, currentEra)) return false;
      if (currentCat !== 'all' && w.c !== currentCat) return false;
      return true;
    }});
    filtered.sort((a, b) => (a.y || 0) - (b.y || 0));
    rendered = 0;
    container.innerHTML = '';
    renderBatch();
  }}

  loadMore.addEventListener('click', renderBatch);
  document.querySelectorAll('#r-era-chips .era-chip').forEach(chip => {{
    chip.addEventListener('click', () => {{
      document.querySelectorAll('#r-era-chips .era-chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      currentEra = chip.dataset.era;
      applyFilter();
    }});
  }});
  document.querySelectorAll('#r-cat-chips .era-chip').forEach(chip => {{
    chip.addEventListener('click', () => {{
      document.querySelectorAll('#r-cat-chips .era-chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      currentCat = chip.dataset.cat;
      applyFilter();
    }});
  }});

  fetch('../works.json').then(r => r.json()).then(data => {{
    works = data;
    applyFilter();
  }});
}})();
</script>
</body>
</html>
"""


def build_region(slug: str, data: dict, neighbors: tuple[dict, dict]) -> int:
    from collections import Counter
    works = data["works"]
    era_counts: Counter = Counter()
    cat_counts: Counter = Counter()
    for w in works:
        y = w.get("year", 0)
        for lo, hi, _label, slug2 in ERAS:
            if lo <= y < hi:
                era_counts[slug2] += 1
                break
        cat_counts[infer_category(w.get("meta", ""), w.get("title", ""))] += 1

    total = len(works)
    era_chips = [f'      <button class="era-chip active" data-era="all">All<span class="c">{total:,}</span></button>']
    for lo, hi, label, sl in ERAS:
        cnt = era_counts[sl]
        if cnt == 0:
            continue
        era_chips.append(
            f'      <button class="era-chip" data-era="{sl}">{h(label)}<span class="c">{cnt:,}</span></button>'
        )
    era_chips_html = "\n".join(era_chips)

    cat_chips = [f'      <button class="era-chip active" data-cat="all">All media<span class="c">{total:,}</span></button>']
    for cat in CAT_ORDER:
        cnt = cat_counts.get(cat, 0)
        if cnt == 0:
            continue
        cat_chips.append(
            f'      <button class="era-chip" data-cat="{cat}">{CAT_LABELS[cat]}<span class="c">{cnt:,}</span></button>'
        )
    cat_chips_html = "\n".join(cat_chips)

    prev, next_ = neighbors
    html_out = REGION_TPL.format(
        slug=slug,
        title=h(data["title"]),
        subtitle=h(data["subtitle"]),
        intro=h(data["intro"]),
        era_chips=era_chips_html,
        cat_chips=cat_chips_html,
        nav=make_nav("regions", in_subdir=True),
        prev_href=f"{prev['slug']}.html",
        prev_title=h(prev["title"]),
        next_href=f"{next_['slug']}.html",
        next_title=h(next_["title"]),
    )
    (REGIONS_OUT / f"{slug}.html").write_text(html_out, encoding="utf-8")
    return total


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
      <div class="subtitle">@@COUNT@@ named makers. Anonymous and collective works live in the regional views.</div>
    </div>
  </header>
  <div class="all-search">
    <input type="text" id="a-search" placeholder="Search artist name&hellip;" autocomplete="off" autofocus>
    <div class="result-count" id="a-count">@@COUNT@@ artists</div>
  </div>
  <div class="filter-controls">
    <div class="filter-chips" id="a-region-chips">
@@REGION_CHIPS@@
    </div>
  </div>
  <div class="filter-controls">
    <div class="filter-chips" id="a-century-chips">
@@CENTURY_CHIPS@@
    </div>
    <div class="sort-toggle">
      <button class="sort-btn active" data-sort="count">By work count</button>
      <button class="sort-btn" data-sort="alpha">A–Z</button>
    </div>
  </div>
  <div class="card-grid" id="a-grid">
@@CARDS@@
  </div>
  <div class="no-results" id="a-empty">No artists match that filter.</div>
  <div class="load-more-wrap">
    <button id="a-load-more" class="load-more-btn" hidden>Show more &darr;</button>
  </div>
  <footer class="page-footer">
    Images via <a href="https://commons.wikimedia.org/" target="_blank" rel="noopener">Wikimedia Commons</a>.
  </footer>
</div>
<script>
(function() {
  const PAGE_SIZE = 300;
  const grid = document.getElementById('a-grid');
  const allCards = Array.from(grid.querySelectorAll('.card'));
  const search = document.getElementById('a-search');
  const countLabel = document.getElementById('a-count');
  const empty = document.getElementById('a-empty');
  const loadMore = document.getElementById('a-load-more');

  const total = allCards.length;
  let filtered = allCards.slice();
  let rendered = 0;
  let state = { q: '', region: 'all', century: 'all', sort: 'count' };

  function normalize(s) {
    return s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  }
  function cmpAlpha(a, b) { return (a.dataset.sortkey || '').localeCompare(b.dataset.sortkey || ''); }
  function cmpCount(a, b) { return (+b.dataset.count) - (+a.dataset.count) || cmpAlpha(a, b); }

  function apply() {
    const q = state.q;
    filtered = allCards.filter(c => {
      if (q && !c.dataset.search.includes(q)) return false;
      if (state.region !== 'all' && c.dataset.region !== state.region) return false;
      if (state.century !== 'all' && c.dataset.century !== state.century) return false;
      return true;
    });
    filtered.sort(state.sort === 'alpha' ? cmpAlpha : cmpCount);
    grid.innerHTML = '';
    rendered = 0;
    renderBatch();
    const filtering = state.q || state.region !== 'all' || state.century !== 'all';
    countLabel.textContent = filtering
      ? (filtered.length.toLocaleString() + ' of ' + total.toLocaleString() + ' artists')
      : (total.toLocaleString() + ' artists');
    empty.style.display = filtered.length === 0 ? 'block' : 'none';
  }

  function renderBatch() {
    const next = filtered.slice(rendered, rendered + PAGE_SIZE);
    if (next.length === 0) { loadMore.hidden = true; return; }
    const frag = document.createDocumentFragment();
    next.forEach(c => frag.appendChild(c));
    grid.appendChild(frag);
    rendered += next.length;
    loadMore.hidden = rendered >= filtered.length;
  }

  loadMore.addEventListener('click', renderBatch);
  search.addEventListener('input', () => { state.q = normalize(search.value.trim()); apply(); });

  document.querySelectorAll('#a-region-chips .era-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('#a-region-chips .era-chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      state.region = chip.dataset.region;
      apply();
    });
  });
  document.querySelectorAll('#a-century-chips .era-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('#a-century-chips .era-chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      state.century = chip.dataset.century;
      apply();
    });
  });
  document.querySelectorAll('.sort-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.sort-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.sort = btn.dataset.sort;
      apply();
    });
  });

  apply();
})();
</script>
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


def build_artists(artists: dict[str, list[dict]], meta: dict | None = None) -> tuple[int, int]:
    from collections import Counter
    artists_out = HERE / "artists"
    artists_out.mkdir(exist_ok=True)
    nav_top = make_nav("artists")

    if not artists:
        html_out = (
            ARTISTS_DIR_TPL
            .replace("@@NAV@@", nav_top)
            .replace("@@COUNT@@", "0")
            .replace("@@REGION_CHIPS@@", "")
            .replace("@@CENTURY_CHIPS@@", "")
            .replace("@@CARDS@@", '    <p class="intro">No artist-tagged works yet.</p>')
        )
        (HERE / "artists.html").write_text(html_out, encoding="utf-8")
        return 0, 0

    names = sorted(artists.keys(), key=artist_sort_key)
    total_works = 0

    # Compute primary region + primary century per artist.
    artist_region: dict[str, tuple[str, str]] = {}
    artist_century: dict[str, str] = {}
    region_counts: Counter = Counter()
    century_counts: Counter = Counter()
    regions_meta = (meta or {}).get("regions", [])
    region_slugs = {r["slug"] for r in regions_meta}

    # Use artist → region counter derived from works directly (already in artists dict).
    # But we need region slug per work. Re-derive from scratch via meta:
    if meta:
        region_titles = {r["slug"]: r["title"] for r in regions_meta}
        per_artist_region: dict[str, Counter] = {}
        for r in regions_meta:
            data = json.loads((DATA / f"{r['slug']}.json").read_text(encoding="utf-8"))
            for w in data["works"]:
                n = w.get("artist")
                if n:
                    per_artist_region.setdefault(n, Counter())[r["slug"]] += 1
        for n in names:
            ctr = per_artist_region.get(n, Counter())
            if ctr:
                top_slug = ctr.most_common(1)[0][0]
                artist_region[n] = (top_slug, region_titles[top_slug])
            else:
                artist_region[n] = ("", "")

    def century_bucket(year: int) -> tuple[str, str]:
        if year == 0:
            return ("unk", "Unknown")
        if year < 1500:
            return ("pre1500", "Before 1500")
        if year < 1600:
            return ("1500s", "1500s")
        if year < 1700:
            return ("1600s", "1600s")
        if year < 1800:
            return ("1700s", "1700s")
        if year < 1900:
            return ("1800s", "1800s")
        if year < 2000:
            return ("1900s", "1900s")
        return ("2000s", "2000s")

    CENTURY_ORDER = [("pre1500", "Before 1500"), ("1500s", "1500s"), ("1600s", "1600s"),
                     ("1700s", "1700s"), ("1800s", "1800s"), ("1900s", "1900s"),
                     ("2000s", "2000s"), ("unk", "Unknown")]

    for n in names:
        years = [w.get("year", 0) for w in artists[n] if isinstance(w.get("year"), int) and w.get("year") != 0]
        median_year = sorted(years)[len(years) // 2] if years else 0
        slug, label = century_bucket(median_year)
        artist_century[n] = slug
        century_counts[slug] += 1
        region_slug, _ = artist_region.get(n, ("", ""))
        if region_slug:
            region_counts[region_slug] += 1

    # Region chips (in regions.json order).
    region_chips_html = [f'      <button class="era-chip active" data-region="all">All regions<span class="c">{len(names):,}</span></button>']
    for r in regions_meta:
        cnt = region_counts.get(r["slug"], 0)
        if cnt == 0:
            continue
        region_chips_html.append(
            f'      <button class="era-chip" data-region="{r["slug"]}">{h(r["title"])}<span class="c">{cnt:,}</span></button>'
        )

    # Century chips.
    century_chips_html = [f'      <button class="era-chip active" data-century="all">All periods<span class="c">{len(names):,}</span></button>']
    for sl, label in CENTURY_ORDER:
        cnt = century_counts.get(sl, 0)
        if cnt == 0:
            continue
        century_chips_html.append(
            f'      <button class="era-chip" data-century="{sl}">{label}<span class="c">{cnt:,}</span></button>'
        )

    # Directory cards with data attributes for JS filtering.
    cards = []
    for name in names:
        slug = slugify(name)
        count = len(artists[name])
        noun = "work" if count == 1 else "works"
        region_slug, _ = artist_region.get(name, ("", ""))
        cent = artist_century.get(name, "unk")
        search_key = normalize_search(name)
        sort_key = artist_sort_key(name)[0]
        cards.append(
            f'    <a class="card" href="artists/{slug}.html"'
            f' data-region="{region_slug}" data-century="{cent}"'
            f' data-search="{h_attr(search_key)}" data-sortkey="{h_attr(sort_key)}"'
            f' data-count="{count}">\n'
            f'      <div class="t">{h(name)}</div>\n'
            f'      <div class="d">{count} {noun}</div>\n'
            f'    </a>'
        )

    dir_html = (
        ARTISTS_DIR_TPL
        .replace("@@NAV@@", nav_top)
        .replace("@@COUNT@@", f"{len(names):,}")
        .replace("@@REGION_CHIPS@@", "\n".join(region_chips_html))
        .replace("@@CENTURY_CHIPS@@", "\n".join(century_chips_html))
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
<!-- Generated by build.py. Data in works.json. -->
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
    <div class="result-count" id="result-count">Loading &hellip;</div>
  </div>
  <div class="filter-controls">
    <div class="filter-chips" id="era-chips">
@@ERA_CHIPS@@
    </div>
    <div class="sort-toggle">
      <button class="sort-btn active" data-sort="region">By region</button>
      <button class="sort-btn" data-sort="year">Chronological</button>
    </div>
  </div>
  <div class="filter-controls">
    <div class="filter-chips" id="region-chips">
@@REGION_CHIPS@@
    </div>
  </div>
  <div class="filter-controls">
    <div class="filter-chips" id="cat-chips">
@@CAT_CHIPS@@
    </div>
  </div>
  <div class="grid" id="all-grid"></div>
  <div class="no-results" id="no-results">No works match that search.</div>
  <div class="load-more-wrap">
    <button id="load-more" class="load-more-btn" hidden>Show more &darr;</button>
  </div>
  <footer class="page-footer">
    Images via <a href="https://commons.wikimedia.org/" target="_blank" rel="noopener">Wikimedia Commons</a>. Click any image to open it and see its source.
  </footer>
</div>
<script src="lightbox.js"></script>
<script>
(function() {
  const PAGE_SIZE = 300;
  const input = document.getElementById('search-input');
  const grid = document.getElementById('all-grid');
  const count = document.getElementById('result-count');
  const empty = document.getElementById('no-results');
  const loadMore = document.getElementById('load-more');

  let allWorks = [];
  let filtered = [];
  let rendered = 0;
  let state = { q: '', era: 'all', region: 'all', cat: 'all', sort: 'region' };

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

  function normalize(s) {
    return s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  }

  function matchEra(y, era) {
    const [lo, hi] = eraBounds[era] || [null, null];
    if (lo !== null && y < lo) return false;
    if (hi !== null && y >= hi) return false;
    return true;
  }

  function applyFilter() {
    const q = state.q;
    filtered = allWorks.filter(w => {
      if (q && !w.s.includes(q)) return false;
      if (state.era !== 'all' && !matchEra(w.y, state.era)) return false;
      if (state.region !== 'all' && w.rs !== state.region) return false;
      if (state.cat !== 'all' && w.c !== state.cat) return false;
      return true;
    });
    if (state.sort === 'year') {
      filtered.sort((a, b) => (a.y || 0) - (b.y || 0));
    } else {
      filtered.sort((a, b) => a.i - b.i);
    }
    grid.innerHTML = '';
    rendered = 0;
    renderBatch();
    empty.style.display = filtered.length === 0 ? 'block' : 'none';
    const filtering = state.q || state.era !== 'all' || state.region !== 'all' || state.cat !== 'all';
    count.textContent = filtering
      ? (filtered.length.toLocaleString() + ' of ' + allWorks.length.toLocaleString() + ' works')
      : (allWorks.length.toLocaleString() + ' works');
  }

  function cardHtml(w) {
    const artistLine = w.a ? '<div class="work-artist">by <a href="artists/' + w.as + '.html">' + w.a + '</a></div>' : '';
    const desc = w.d ? '<div class="d">' + w.d + '</div>' : '';
    return (
      '<article class="work">' +
      '<img src="' + w.u + '" alt="' + w.t + '" loading="lazy">' +
      '<div class="body">' +
      '<a class="region-badge" href="regions/' + w.rs + '.html">' + w.r + '</a>' +
      '<div class="t">' + w.t + '</div>' +
      artistLine +
      '<div class="meta">' + w.m + '</div>' +
      desc +
      '</div></article>'
    );
  }

  function renderBatch() {
    const next = filtered.slice(rendered, rendered + PAGE_SIZE);
    if (next.length === 0) {
      loadMore.hidden = true;
      return;
    }
    const html = next.map(cardHtml).join('');
    grid.insertAdjacentHTML('beforeend', html);
    rendered += next.length;
    loadMore.hidden = rendered >= filtered.length;
  }

  loadMore.addEventListener('click', renderBatch);
  input.addEventListener('input', () => { state.q = normalize(input.value.trim()); applyFilter(); });

  document.querySelectorAll('#era-chips .era-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('#era-chips .era-chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      state.era = chip.dataset.era;
      applyFilter();
    });
  });
  document.querySelectorAll('#region-chips .era-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('#region-chips .era-chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      state.region = chip.dataset.region;
      applyFilter();
    });
  });
  document.querySelectorAll('#cat-chips .era-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('#cat-chips .era-chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      state.cat = chip.dataset.cat;
      applyFilter();
    });
  });
  document.querySelectorAll('.sort-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.sort-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.sort = btn.dataset.sort;
      applyFilter();
    });
  });

  // Prefill from ?q= URL param (used by home-page search form).
  const urlQ = new URLSearchParams(location.search).get('q');
  if (urlQ) {
    input.value = urlQ;
    state.q = normalize(urlQ.trim());
  }

  // Fetch data.
  fetch('works.json').then(r => r.json()).then(data => {
    allWorks = data.map((w, i) => { w.i = i; return w; });
    applyFilter();
  }).catch(err => {
    count.textContent = 'Error loading works.';
    console.error(err);
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
<!-- Generated by build.py. Data in works.json. -->
@@NAV@@
<div class="page">
  <header class="page-header">
    <div>
      <h1>Timeline</h1>
      <div class="subtitle">All @@TOTAL@@ works in chronological order &mdash; cross-cultural contemporaries lined up.</div>
    </div>
  </header>
  <div class="hint">Click any image to enlarge. Use &larr; &rarr; or close with Esc.</div>
  <div class="filter-controls">
    <div class="filter-chips" id="tl-era-chips">
@@ERA_CHIPS@@
    </div>
  </div>
  <div id="tl-container"></div>
  <div class="load-more-wrap">
    <button id="tl-load-more" class="load-more-btn" hidden>Show more &darr;</button>
  </div>
  <footer class="page-footer">
    Images via <a href="https://commons.wikimedia.org/" target="_blank" rel="noopener">Wikimedia Commons</a>. Click any image to open it and see its source.
  </footer>
</div>
<script src="lightbox.js"></script>
<script>
(function() {
  const PAGE_SIZE = 400;
  const container = document.getElementById('tl-container');
  const loadMore = document.getElementById('tl-load-more');
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
  const eraLabels = {
    'pre-1000bce': 'Before 1000 BCE',
    '1000bce-0': '1000 BCE – 0',
    '0-500': '0 – 500 CE',
    '500-1000': '500 – 1000',
    '1000-1500': '1000 – 1500',
    '1500-1800': '1500 – 1800',
    '1800+': '1800 onward'
  };

  let works = [];
  let filtered = [];
  let rendered = 0;
  let currentEra = 'all';
  let currentEraHeader = null;

  function fmtYear(y) { if (y < 0) return (-y) + ' BCE'; if (y < 1000) return y + ' CE'; return String(y); }
  function eraFor(y) {
    for (const [slug, [lo, hi]] of Object.entries(eraBounds)) {
      if (slug === 'all') continue;
      if ((lo === null || y >= lo) && (hi === null || y < hi)) return slug;
    }
    return 'all';
  }

  function matchEra(y, era) {
    const [lo, hi] = eraBounds[era];
    if (lo !== null && y < lo) return false;
    if (hi !== null && y >= hi) return false;
    return true;
  }

  function cardHtml(w) {
    const artistLine = w.a ? '<div class="work-artist">by <a href="artists/' + w.as + '.html">' + w.a + '</a></div>' : '';
    const desc = w.d ? '<div class="d">' + w.d + '</div>' : '';
    return (
      '<article class="work tl-entry">' +
      '<div class="tl-year">' + fmtYear(w.y || 0) + '</div>' +
      '<img src="' + w.u + '" alt="' + w.t + '" loading="lazy">' +
      '<div class="body">' +
      '<a class="region-badge" href="regions/' + w.rs + '.html">' + w.r + '</a>' +
      '<div class="t">' + w.t + '</div>' +
      artistLine +
      '<div class="meta">' + w.m + '</div>' +
      desc +
      '</div></article>'
    );
  }

  function renderBatch() {
    const next = filtered.slice(rendered, rendered + PAGE_SIZE);
    if (next.length === 0) { loadMore.hidden = true; return; }
    let html = '';
    let lastEra = currentEraHeader;
    for (const w of next) {
      const e = eraFor(w.y || 0);
      if (e !== lastEra) {
        const cnt = filtered.filter(x => eraFor(x.y || 0) === e).length;
        html += '<section class="tl-era"><h2 class="tl-era-title">' + (eraLabels[e] || e) +
                '<span class="tl-era-count">' + cnt + ' works</span></h2><div class="grid">';
        if (lastEra !== null) html = '</div></section>' + html;
        lastEra = e;
      }
      html += cardHtml(w);
    }
    html += '</div></section>';
    // Strip the first redundant close if this is the very first render.
    if (currentEraHeader === null && html.startsWith('</div></section>')) html = html.slice('</div></section>'.length);
    // The dance above is because we need to close the previous open section when a new era starts.
    // Simpler: always re-render from scratch.
    container.innerHTML = '';
    currentEraHeader = null;
    let open = false;
    let out = '';
    const sliceSoFar = filtered.slice(0, rendered + next.length);
    for (const w of sliceSoFar) {
      const e = eraFor(w.y || 0);
      if (e !== currentEraHeader) {
        if (open) out += '</div></section>';
        const cnt = filtered.filter(x => eraFor(x.y || 0) === e).length;
        out += '<section class="tl-era"><h2 class="tl-era-title">' + (eraLabels[e] || e) +
               '<span class="tl-era-count">' + cnt + ' works</span></h2><div class="grid">';
        open = true;
        currentEraHeader = e;
      }
      out += cardHtml(w);
    }
    if (open) out += '</div></section>';
    container.innerHTML = out;
    rendered += next.length;
    loadMore.hidden = rendered >= filtered.length;
  }

  function applyFilter() {
    filtered = (currentEra === 'all') ? works.slice() : works.filter(w => matchEra(w.y || 0, currentEra));
    filtered.sort((a, b) => (a.y || 0) - (b.y || 0));
    rendered = 0;
    currentEraHeader = null;
    container.innerHTML = '';
    renderBatch();
  }

  loadMore.addEventListener('click', renderBatch);
  document.querySelectorAll('#tl-era-chips .era-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('#tl-era-chips .era-chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      currentEra = chip.dataset.era;
      applyFilter();
    });
  });

  fetch('works.json').then(r => r.json()).then(data => { works = data; applyFilter(); });
})();
</script>
</body>
</html>
"""

ERA_CHIP_TPL = '      <button class="era-chip" data-era="{era}">{label}<span class="c">{count}</span></button>\n'


# Category inference: check in order of specificity. Checks meta first, then title fallback.
CATEGORY_RULES = [
    ("photograph",  ["photograph", "albumen", "salt print", "daguerreotype", "gelatin silver"]),
    ("print",       ["engraving", "etching", "woodblock", "woodcut", "lithograph", "aquatint",
                      "mezzotint", "drypoint", "ukiyo-e", " print"]),
    ("manuscript",  ["manuscript", "illuminated", "folio", "miniature", "calligraphy", "codex",
                      "page from", "shahnameh", "quran", "qur'an", "shahnama", "leaf from"]),
    ("painting",    ["oil on", "tempera", "gouache", "watercolor", "fresco", "ink on silk",
                      "ink on paper", "hanging scroll", "handscroll", "album leaf", "painting",
                      "impressionism", "post-impressionism", "fauvism", "cubism", "expressionism",
                      "surrealism", "realism", "pre-raphaelite", "romantic", "neoclassical",
                      "baroque painting", "rococo", "rinpa", "kano", "ukiyo-e painting",
                      "mughal painting", "persian miniature", "rajput"]),
    ("drawing",     ["drawing", "pen and ink", "charcoal", "chalk", "pencil", "brush and ink",
                      "silverpoint", "sketch"]),
    ("textile",     ["textile", "tapestry", "embroidery", "ikat", "carpet", "rug", "kesi", "dagmay",
                      "tunic", "garment", "robe", "cloth", "cape", "shawl", "kimono", "kaftan",
                      "silk:", "linen:", "wool:", "cotton:", "batik"]),
    ("ceramic",     ["ceramic", "porcelain", "earthenware", "stoneware", "fritware", "celadon",
                      "lusterware", "luster ware", "fayence", "faience", "iznik", "kaolin",
                      "redware", "majolica", "blue-and-white", "famille rose", "famille verte",
                      "buncheong", "raku", "oribe", "jun ware", "ding ware", "ru ware",
                      "longquan", "cizhou"]),
    ("glass",       ["glass"]),
    ("lacquer",     ["lacquer"]),
    ("jewelry",     ["jewel", "necklace", "earring", "pendant", "brooch", "diadem", "bracelet",
                      "amulet", "ring ", "signet"]),
    ("mask",        ["mask", "headdress"]),
    ("furniture",   ["furniture", "chair", "cabinet", "bed", "table", "throne", "stool"]),
    ("metalwork",   ["gold", "silver", "bronze", "copper", "brass", "metalwork", "coin", "medal",
                      "rhyton", "stirrup", "wine vessel"]),
    ("architecture", ["temple", "mosque", "pyramid", "palace", "church", "cathedral", "tomb",
                      "stupa", "monastery", "fort", "castle", "ziggurat", "pagoda", "citadel",
                      "basilica", "colonnade", "gateway", "obelisk", "tower", "shrine", "wat ",
                      "bagan", "angkor", "borobudur", "prambanan", "karnak", "dome of", "taj mahal",
                      "alhambra", "persepolis", "hagia sophia", "parthenon", "colosseum", "forum"]),
    ("sculpture",   ["sculpture", "statue", "statuette", "figurine", "figure", "stele", "relief",
                      "marble", "limestone", "sandstone", "granite", "terracotta", "alabaster",
                      "wood", "stone", "ivory", "jade", "obsidian", "basalt", "schist",
                      "bust", "head of", "buddha", "bodhisattva", "guanyin", "kouros",
                      "lamassu", "moai"]),
]

# Title-only hints for when meta is sparse.
TITLE_HINTS = [
    ("architecture", ["temple", "mosque", "pyramid", "palace", "church", "cathedral", "tomb",
                       "stupa", "monastery", "fort", "castle", "ziggurat", "pagoda", "citadel",
                       "basilica", "gateway", "obelisk", "shrine", "bagan", "angkor", "pergamon",
                       "borobudur", "prambanan", "karnak", "alhambra", "persepolis",
                       "hagia sophia", "parthenon", "colosseum", "forum", "luxor", "dome of",
                       "taj mahal", "ellora", "khajuraho", "ajanta", "machu picchu", "teotihuacan",
                       "chichen itza", "tikal", "palenque", "city", "villa", "madrasa",
                       "pantheon", "nishapur"]),
    ("sculpture",    ["bust of", "head of", "statue of", "figure of", "relief of", "stele of",
                       "moai", "lamassu", "kouros", "kore", "buddha", "bodhisattva", "guanyin",
                       "shiva", "vishnu", "ganesha", "krishna", "parvati", "lakshmi",
                       "seated", "standing", "figurine", "figurines"]),
    ("mask",         ["mask", "headdress"]),
    ("textile",      ["carpet", "rug", "tunic", "robe", "kimono", "tapestry", "mantle"]),
    ("ceramic",      ["vase", "jar", "bowl", "plate", "pitcher", "cup", "amphora", "krater",
                       "hydria", "lekythos", "kylix", "oinochoe", "dish"]),
    ("metalwork",    ["coin", "medal", "pectoral", "rhyton", "finial", "plaque"]),
    ("print",        ["print"]),
    ("manuscript",   ["page from", "folio", "leaf from", "shahnama", "shahnameh", "nizami",
                       "book of", "quran", "gospel"]),
    ("painting",     ["water lilies", "self-portrait", "landscape", "portrait", "still life",
                       "madonna", "crucifixion", "annunciation", "last supper",
                       "starry night", "fan painting", "scroll"]),
]


def infer_category(meta: str, title: str = "", artist: str = "") -> str:
    m = meta.lower()
    for cat, needles in CATEGORY_RULES:
        if any(n in m for n in needles):
            return cat
    t = title.lower()
    for cat, needles in TITLE_HINTS:
        if any(n in t for n in needles):
            return cat
    # Regional fallbacks for Mughal/Rajput/Pahari/Deccan — almost always painting/manuscript
    if any(k in m for k in ("mughal", "rajput", "pahari", "kangra", "basohli",
                              "deccani", "bundi", "jaipur miniature", "bikaner")):
        return "painting"
    # Kashmir shawls / textile hubs
    if "kashmir" in m:
        return "textile"
    # Spanish colonial / Florentine paper art context without medium usually means painting
    if ("florence" in m or "impressionism" in m or "post-impressionism" in m or
        "expressionism" in m or "realism" in m or "romantic" in m or
        "neoclassical" in m or "fauvism" in m or "cubism" in m or
        "pre-raphaelite" in m or "symbolism" in m or "mannerism" in m):
        return "painting"
    # If the work carries a recognized artist and nothing else matched, assume painting
    # (artist-attributed works without medium keywords are overwhelmingly paintings).
    if artist and artist.strip():
        return "painting"
    return "other"


CAT_LABELS = {
    "painting": "Painting", "sculpture": "Sculpture", "architecture": "Architecture",
    "print": "Print", "drawing": "Drawing", "photograph": "Photograph", "textile": "Textile",
    "ceramic": "Ceramic", "glass": "Glass", "lacquer": "Lacquer", "jewelry": "Jewelry",
    "mask": "Mask", "furniture": "Furniture", "metalwork": "Metalwork",
    "manuscript": "Manuscript", "other": "Other",
}

CAT_ORDER = ["painting", "sculpture", "architecture", "print", "drawing", "photograph",
             "textile", "ceramic", "metalwork", "manuscript", "glass", "lacquer", "jewelry",
             "mask", "furniture", "other"]


def build_all_works(meta: dict) -> int:
    from collections import Counter
    all_entries: list[dict] = []
    era_counts: Counter = Counter({s: 0 for _, _, _, s in ERAS})
    region_counts: Counter = Counter()
    cat_counts: Counter = Counter()
    region_titles: dict[str, str] = {r["slug"]: r["title"] for r in meta["regions"]}

    for r in meta["regions"]:
        data = json.loads((DATA / f"{r['slug']}.json").read_text(encoding="utf-8"))
        for w in data["works"]:
            year = w.get("year", 0)
            cat = infer_category(w.get("meta", ""), w.get("title", ""), w.get("artist", ""))
            search_tokens = [w.get("title", ""), w.get("meta", ""), w.get("desc", ""),
                              w.get("artist", ""), r["title"]]
            s = normalize_search(" ".join(t for t in search_tokens if t))
            entry = {
                "t": w["title"],
                "m": w["meta"],
                "u": w["image"],
                "r": r["title"],
                "rs": r["slug"],
                "y": year,
                "c": cat,
                "s": s,
            }
            if w.get("desc"):
                entry["d"] = w["desc"]
            if w.get("artist"):
                entry["a"] = w["artist"]
                entry["as"] = slugify(w["artist"])
            all_entries.append(entry)

            region_counts[r["slug"]] += 1
            cat_counts[cat] += 1
            for lo, hi, _label, slug in ERAS:
                if lo <= year < hi:
                    era_counts[slug] += 1
                    break

    total = len(all_entries)
    (HERE / "works.json").write_text(
        json.dumps(all_entries, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )

    # Era chips (same as before).
    era_chips = [f'      <button class="era-chip active" data-era="all">All<span class="c">{total:,}</span></button>']
    for lo, hi, label, slug in ERAS:
        cnt = era_counts[slug]
        if cnt == 0:
            continue
        era_chips.append(
            f'      <button class="era-chip" data-era="{slug}">{h(label)}<span class="c">{cnt:,}</span></button>'
        )
    era_chips_html = "\n".join(era_chips)

    # Region chips.
    region_chips = [f'      <button class="era-chip active" data-region="all">All regions<span class="c">{total:,}</span></button>']
    for r in meta["regions"]:
        cnt = region_counts[r["slug"]]
        if cnt == 0:
            continue
        region_chips.append(
            f'      <button class="era-chip" data-region="{r["slug"]}">{h(r["title"])}<span class="c">{cnt:,}</span></button>'
        )
    region_chips_html = "\n".join(region_chips)

    # Category chips.
    cat_chips = [f'      <button class="era-chip active" data-cat="all">All media<span class="c">{total:,}</span></button>']
    for cat in CAT_ORDER:
        cnt = cat_counts.get(cat, 0)
        if cnt == 0:
            continue
        cat_chips.append(
            f'      <button class="era-chip" data-cat="{cat}">{CAT_LABELS[cat]}<span class="c">{cnt:,}</span></button>'
        )
    cat_chips_html = "\n".join(cat_chips)

    nav = make_nav("all")
    html_out = (
        ALL_TPL
        .replace("@@NAV@@", nav)
        .replace("@@ERA_CHIPS@@", era_chips_html)
        .replace("@@REGION_CHIPS@@", region_chips_html)
        .replace("@@CAT_CHIPS@@", cat_chips_html)
        .replace("@@TOTAL@@", f"{total:,}")
    )
    (HERE / "all.html").write_text(html_out, encoding="utf-8")
    return total


def build_timeline(meta: dict) -> int:
    from collections import Counter
    era_counts: Counter = Counter()
    total = 0
    for r in meta["regions"]:
        data = json.loads((DATA / f"{r['slug']}.json").read_text(encoding="utf-8"))
        for w in data["works"]:
            total += 1
            y = w.get("year", 0)
            for lo, hi, _label, slug in ERAS:
                if lo <= y < hi:
                    era_counts[slug] += 1
                    break

    era_chips = [f'      <button class="era-chip active" data-era="all">All<span class="c">{total:,}</span></button>']
    for lo, hi, label, slug in ERAS:
        cnt = era_counts[slug]
        if cnt == 0:
            continue
        era_chips.append(
            f'      <button class="era-chip" data-era="{slug}">{h(label)}<span class="c">{cnt:,}</span></button>'
        )
    era_chips_html = "\n".join(era_chips)

    html_out = (
        TIMELINE_TPL
        .replace("@@NAV@@", make_nav("timeline"))
        .replace("@@TOTAL@@", f"{total:,}")
        .replace("@@ERA_CHIPS@@", era_chips_html)
    )
    (HERE / "timeline.html").write_text(html_out, encoding="utf-8")
    return total


# ---------------------------------------------------------------------------
# Landing page
# ---------------------------------------------------------------------------

TILE_TPL = """  <a class="region-tile" href="regions/{slug}.html">
    <img class="tile-img" src="{image}" alt="" loading="lazy">
    <div class="tile-overlay">
      <div class="tile-count">{count} works</div>
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


def build_region_tiles(regions: list[dict], counts: dict[str, int]) -> str:
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
            count=counts.get(r["slug"], 0),
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

  <form class="home-search" action="all.html" method="get" role="search">
    <input type="text" name="q" placeholder="Search works, artists, periods, years&hellip;" autocomplete="off" autofocus>
  </form>

  <h2 class="section">By region</h2>
  @@REGION_TILES@@

  <footer class="page-footer">
    Images via <a href="https://commons.wikimedia.org/" target="_blank" rel="noopener">Wikimedia Commons</a>. Click any image to open it and see its source.
  </footer>
</div>
</body>
</html>
"""

def build_index(meta: dict, counts: dict[str, int], artists: dict[str, list[dict]]) -> None:
    region_tiles_html = build_region_tiles(meta["regions"], counts)
    total = sum(counts.values())
    html_out = (
        INDEX_TPL
        .replace("@@NAV@@", make_nav("regions"))
        .replace("@@REGION_TILES@@", region_tiles_html)
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
    n_artists, n_artist_works = build_artists(artists, meta)
    total_all = build_all_works(meta)
    build_timeline(meta)
    build_index(meta, counts, artists)
    print(
        f"\nBuilt {len(regions)} regions + index + artists + timeline + all. "
        f"{total_all} works total ({n_artist_works} by {n_artists} named artists)."
    )


if __name__ == "__main__":
    main()
