#!/usr/bin/env python3
"""Bulk ingest — search Cleveland + Art Institute of Chicago + V&A with many
queries, auto-filter by culture/place, write entries directly to
data/<region>.json with desc="" and dedupe by title and image URL.

Usage:
    python bulk_ingest.py                # full PLAN
    python bulk_ingest.py region1 region2  # only named regions

To grow the gallery further, add rows to PLAN or bump per-query limits.
"""
import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
CMA = "https://openaccess-api.clevelandart.org/api/artworks"
AIC = "https://api.artic.edu/api/v1/artworks/search"
VAM = "https://api.vam.ac.uk/v2/objects/search"
MET = "https://collectionapi.metmuseum.org/public/collection/v1"
UA = {"User-Agent": "images-gallery/1.0"}


def get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


# ---------- Cleveland ----------

def _cma_first_artist(d):
    for c in d.get("creators") or []:
        desc = c.get("description") or ""
        name = desc.split("(")[0].strip()
        if name and name.lower() not in ("anonymous", "unknown", "maker unknown"):
            return name
    return ""


def cma_normalize(d):
    images = d.get("images") or {}
    img = (images.get("print") or {}).get("url") or (images.get("web") or {}).get("url")
    if not img:
        return None
    title = (d.get("title") or "").strip()
    if not title:
        return None
    culture = d.get("culture") or []
    if isinstance(culture, list):
        culture = ", ".join(culture)
    date_disp = (d.get("creation_date") or "").strip()
    technique = (d.get("technique") or "").strip()
    meta = " · ".join(b for b in (culture, date_disp, technique) if b)
    entry = {
        "title": title,
        "meta": meta,
        "desc": "",
        "image": img,
        "_culture": culture.lower(),
    }
    year = d.get("creation_date_earliest")
    if isinstance(year, int):
        entry["year"] = year
    artist = _cma_first_artist(d)
    if artist:
        entry["artist"] = artist
    return entry


def cma_search(q, limit, typ=None):
    p = {"q": q, "has_image": "1", "limit": str(limit)}
    if typ:
        p["type"] = typ
    url = f"{CMA}?{urllib.parse.urlencode(p)}"
    try:
        data = get(url).get("data") or []
    except Exception as e:
        print(f"  CMA ERR {q!r}: {e}", file=sys.stderr)
        return []
    out = []
    for d in data:
        e = cma_normalize(d)
        if e:
            out.append(e)
    return out


# ---------- Art Institute of Chicago ----------

AIC_FIELDS = ",".join([
    "id", "title", "image_id", "artist_display", "date_start", "date_end",
    "classification_title", "place_of_origin", "medium_display",
    "is_public_domain", "style_title",
])


def aic_normalize(d):
    if not d.get("is_public_domain"):
        return None
    image_id = d.get("image_id")
    if not image_id:
        return None
    title = (d.get("title") or "").strip()
    if not title:
        return None
    place = (d.get("place_of_origin") or "").strip()
    date = ""
    ds, de = d.get("date_start"), d.get("date_end")
    if ds and de and ds != de:
        date = f"{ds}–{de}"
    elif ds:
        date = str(ds)
    medium = (d.get("medium_display") or "").strip().split(",")[0].strip()
    style = (d.get("style_title") or "").strip()
    bits = [b for b in (place, style, date, medium) if b]
    meta = " · ".join(bits)
    artist = (d.get("artist_display") or "").split("\n")[0].split("(")[0].strip()
    if artist.lower() in ("", "unknown artist", "anonymous", "unknown"):
        artist = ""
    entry = {
        "title": title,
        "meta": meta,
        "desc": "",
        "image": f"https://www.artic.edu/iiif/2/{image_id}/full/843,/0/default.jpg",
        "_culture": (place + " " + style).lower(),
    }
    year = d.get("date_start")
    if isinstance(year, int) and year != 0:
        entry["year"] = year
    if artist:
        entry["artist"] = artist
    return entry


def aic_search(q, limit):
    params = {"q": q, "fields": AIC_FIELDS, "limit": str(limit)}
    url = f"{AIC}?{urllib.parse.urlencode(params)}"
    try:
        data = get(url).get("data") or []
    except Exception as e:
        print(f"  AIC ERR {q!r}: {e}", file=sys.stderr)
        return []
    out = []
    for d in data:
        e = aic_normalize(d)
        if e:
            out.append(e)
    return out


# ---------- Victoria & Albert ----------

def vam_normalize(d):
    primary = d.get("_primaryImageId") or (d.get("_images") or {}).get("_primary_thumbnail", "")
    if not primary:
        return None
    # image id is often the full filename
    img_id = primary
    if img_id.startswith("http"):
        image_url = img_id
    else:
        image_url = f"https://framemark.vam.ac.uk/collections/{img_id}/full/735,/0/default.jpg"
    title = (d.get("_primaryTitle") or d.get("objectType") or "").strip()
    if not title:
        return None
    place = (d.get("_primaryPlace") or "").strip()
    date = (d.get("_primaryDate") or "").strip()
    maker = (d.get("_primaryMaker") or {}).get("name", "").strip()
    mat = ""
    bits = [b for b in (place, date, mat) if b]
    meta = " · ".join(bits)
    entry = {
        "title": title,
        "meta": meta,
        "desc": "",
        "image": image_url,
        "_culture": place.lower(),
    }
    year = None
    date_range = d.get("_primaryDate") or ""
    # very rough year extraction
    import re
    m = re.search(r"\b(\d{3,4})\b", date_range)
    if m:
        try:
            year = int(m.group(1))
            # crude: if "BC" appears, negate
            if "BC" in date_range.upper() or "BCE" in date_range.upper():
                year = -year
            entry["year"] = year
        except ValueError:
            pass
    if maker and maker.lower() not in ("unknown", "anonymous"):
        entry["artist"] = maker
    return entry


def vam_search(q, limit):
    params = {
        "q": q,
        "images_exist": "1",
        "response_format": "json",
        "page_size": str(limit),
        "cluster": "false",
    }
    url = f"{VAM}?{urllib.parse.urlencode(params)}"
    try:
        resp = get(url)
    except Exception as e:
        print(f"  V&A ERR {q!r}: {e}", file=sys.stderr)
        return []
    records = resp.get("records") or []
    out = []
    for d in records:
        e = vam_normalize(d)
        if e:
            out.append(e)
    return out


# ---------- Metropolitan Museum of Art ----------

def met_normalize(obj):
    if not obj.get("isPublicDomain"):
        return None
    image = obj.get("primaryImageSmall") or obj.get("primaryImage") or ""
    if not image:
        return None
    title = (obj.get("title") or "").strip()
    if not title:
        return None
    artist = (obj.get("artistDisplayName") or "").strip()
    if artist.lower() in ("", "unknown", "anonymous"):
        artist = ""
    date_disp = (obj.get("objectDate") or "").strip()
    culture = (obj.get("culture") or obj.get("period") or "").strip()
    medium = (obj.get("medium") or "").strip().split(";")[0].strip()
    dept = (obj.get("department") or "").strip()

    meta_bits = [b for b in (culture, date_disp, medium) if b]
    meta = " · ".join(meta_bits)
    entry = {
        "title": title,
        "meta": meta,
        "desc": "",
        "image": image,
        "_culture": (culture + " " + dept + " " + (obj.get("country") or "")).lower(),
    }
    year = obj.get("objectBeginDate")
    if (not isinstance(year, int)) or year == 0:
        year = obj.get("objectEndDate")
    if isinstance(year, int) and year != 0:
        entry["year"] = year
    if artist:
        entry["artist"] = artist
    return entry


def met_search(q, limit):
    try:
        params = {"q": q, "hasImages": "true"}
        url = f"{MET}/search?{urllib.parse.urlencode(params)}"
        resp = get(url, timeout=30)
    except Exception as e:
        print(f"  MET search ERR {q!r}: {e}", file=sys.stderr)
        return []
    ids = (resp.get("objectIDs") or [])[:limit]
    if not ids:
        return []

    def fetch_one(oid):
        try:
            return get(f"{MET}/objects/{oid}", timeout=20)
        except Exception:
            return None

    with ThreadPoolExecutor(max_workers=10) as ex:
        objs = list(ex.map(fetch_one, ids))
    out = []
    for o in objs:
        if not o:
            continue
        e = met_normalize(o)
        if e:
            out.append(e)
    return out


# ---------- Query plan ----------

# (query, culture_needles, sources)
# culture_needles = list of lowercase substrings; at least one must match the
# item's "_culture" field (culture, place_of_origin, style, etc.) or the item
# is dropped. sources: subset of {"cma","aic","vam"}. Empty = all.
ALL = ("cma", "aic", "vam")
ALL_PLUS_MET = ("cma", "aic", "vam", "met")
MET_ONLY = ("met",)
CMA_ONLY = ("cma",)

PLAN: dict[str, list[tuple[str, list[str], tuple[str, ...]]]] = {
    "mesopotamia-persia": [
        ("Sasanian", ["sasanian", "iran"], ALL),
        ("Parthian", ["parthian", "iran"], ALL),
        ("Luristan bronze", ["luristan", "amlash", "iran"], ALL),
        ("Hittite", ["hittite", "anatolia", "turkey"], ALL),
        ("Sumerian", ["sumer", "mesopotam", "iraq"], ALL),
        ("Assyrian relief", ["assyrian", "iraq", "mesopotam"], ALL),
        ("Palmyra", ["palmyra", "syria"], ALL),
        ("Achaemenid", ["achaemenid", "persepolis", "iran"], ALL),
        ("Urartian", ["urart", "armenia"], ALL),
        ("Mesopotamian cylinder seal", ["mesopotam", "iraq", "sumer"], ALL),
        ("Neo-Assyrian", ["assyrian", "iraq"], ALL),
        ("Babylonian", ["babylon", "mesopotam"], ALL),
        ("Elamite", ["elam", "susa", "iran"], ALL),
        ("Scythian gold", ["scyth", "siberia"], ALL),
        ("Qajar lacquer", ["qajar", "iran"], ALL),
        ("Sasanian silver", ["sasanian", "iran"], ALL),
        ("Bactrian", ["bactria", "afghanistan"], ALL),
        ("Mesopotamian statue", ["mesopotam", "iraq", "sumer"], ALL),
        ("Sumerian tablet", ["sumer", "mesopotam", "iraq"], ALL),
        ("Nineveh ivory", ["assyrian", "iraq", "nineveh"], ALL),
        ("Iranian bronze", ["iran"], ALL),
        ("Median", ["median", "iran"], ALL),
        ("Achaemenid gold", ["achaemenid", "iran"], ALL),
        ("Parthian terracotta", ["parthian", "iran"], ALL),
        ("Persian ceramic", ["iran", "persian"], ALL),
        ("Nishapur", ["nishapur", "iran"], ALL),
        ("Gorgan", ["iran", "gorgan"], ALL),
        ("Ziwiye", ["ziwiye", "iran"], ALL),
        ("Hasanlu", ["hasanlu", "iran"], ALL),
        ("Marlik", ["marlik", "iran"], ALL),
        ("Sasanian stucco", ["sasanian", "iran"], ALL),
        ("Sasanian seal", ["sasanian", "iran"], ALL),
        ("Persian lacquer", ["iran", "persian"], ALL),
        ("Iranian ceramic tile", ["iran"], ALL),
        ("Khorasan", ["khorasan", "iran"], ALL),
        ("Tepe Hissar", ["iran"], ALL),
        ("Susa", ["susa", "iran", "elam"], ALL),
        ("Persepolis column", ["persepolis", "iran"], ALL),
    ],
    "mediterranean": [
        ("black-figure", ["greek", "attic", "corinthian"], ALL),
        ("red-figure", ["greek", "attic"], ALL),
        ("Greek vase", ["greek", "attic", "corinthian"], ALL),
        ("Roman glass", ["roman"], ALL),
        ("Roman fresco", ["roman", "pompeii"], ALL),
        ("Roman mosaic", ["roman"], ALL),
        ("Etruscan bronze", ["etruscan"], ALL),
        ("Etruscan mirror", ["etruscan"], ALL),
        ("Corinthian vase", ["greek", "corinthian"], ALL),
        ("Minoan", ["minoan", "crete"], ALL),
        ("Mycenaean", ["mycenaean", "greek"], ALL),
        ("Cycladic", ["cycladic"], ALL),
        ("Greek sculpture", ["greek"], ALL),
        ("Roman portrait", ["roman"], ALL),
        ("Roman silver", ["roman"], ALL),
        ("Greek gold", ["greek"], ALL),
        ("Hellenistic", ["hellenistic", "greek"], ALL),
        ("Apulian", ["apulian", "south italian"], ALL),
        ("Archaic kouros", ["greek", "archaic"], ALL),
        ("Attic amphora", ["greek", "attic"], ALL),
        ("Attic kylix", ["greek", "attic"], ALL),
        ("Attic pelike", ["greek", "attic"], ALL),
        ("Geometric Greek", ["greek", "geometric"], ALL),
        ("Lucanian vase", ["lucanian", "south italian"], ALL),
        ("Gnathian", ["gnathian", "south italian"], ALL),
        ("Roman terracotta", ["roman"], ALL),
        ("Roman bronze", ["roman"], ALL),
        ("Roman sarcophagus", ["roman"], ALL),
        ("Ravenna mosaic", ["ravenna", "byzantine", "italy"], ALL),
        ("Late Antique silver", ["roman", "byzantine"], ALL),
        ("Tanagra figurine", ["tanagra", "greek"], ALL),
        ("Pompeii fresco", ["pompeii", "roman"], ALL),
        ("Herculaneum", ["herculaneum", "roman"], ALL),
        ("Phoenician", ["phoenician", "lebanon"], ALL),
        ("Carthaginian", ["carthage", "tunisia", "punic"], ALL),
        ("Sabine", ["sabine", "etruscan"], ALL),
        ("Exekias", ["greek", "attic"], ALL),
        ("Euphronios", ["greek", "attic"], ALL),
        ("Douris", ["greek", "attic"], ALL),
        ("Brygos", ["greek", "attic"], ALL),
        ("Andokides painter", ["greek", "attic"], ALL),
        ("Berlin Painter", ["greek", "attic"], ALL),
        ("Kleophrades", ["greek", "attic"], ALL),
        ("Kleitias", ["greek", "attic"], ALL),
        ("Nikosthenes", ["greek", "attic"], ALL),
        ("Amasis Painter", ["greek", "attic"], ALL),
        ("Roman cameo gem", ["roman"], ALL),
        ("Roman intaglio", ["roman"], ALL),
        ("Aeneid", ["roman"], ALL),
        ("Pompeii villa", ["roman", "pompeii"], ALL),
        ("Republican Roman", ["roman"], ALL),
        ("Antioch mosaic", ["antioch", "roman", "byzantine"], ALL),
        ("Pergamon", ["greek", "hellenistic"], ALL),
        ("Knossos", ["minoan", "crete"], ALL),
        ("Mycenae", ["mycenaean", "greek"], ALL),
        ("Cretan", ["crete", "minoan"], ALL),
        ("Thracian", ["thracian", "bulgaria"], ALL),
        ("Faiyum portrait", ["egypt", "fayum"], ALL),
        ("Roman wall painting", ["roman"], ALL),
    ],
    "egypt-nubia": [
        ("Coptic textile", ["coptic", "egypt", "byzantine"], ALL),
        ("Old Kingdom relief", ["egypt"], ALL),
        ("Middle Kingdom Egypt", ["egypt"], ALL),
        ("New Kingdom Egypt", ["egypt"], ALL),
        ("Egyptian faience", ["egypt"], ALL),
        ("shabti", ["egypt"], ALL),
        ("Late period Egyptian", ["egypt"], ALL),
        ("Nubian", ["nubia", "kush", "meroe", "sudan"], ALL),
        ("Egyptian amulet", ["egypt"], ALL),
        ("Egyptian papyrus", ["egypt"], ALL),
        ("Ptolemaic", ["egypt", "ptolem"], ALL),
        ("mummy portrait", ["egypt", "fayum"], ALL),
        ("Egyptian cosmetic", ["egypt"], ALL),
        ("Egyptian jewelry", ["egypt"], ALL),
        ("hieroglyph stele", ["egypt"], ALL),
        ("Egyptian tomb painting", ["egypt"], ALL),
        ("Amarna Egypt", ["egypt", "amarna"], ALL),
        ("Thebes tomb", ["egypt", "thebes"], ALL),
        ("Saqqara", ["egypt", "saqqara"], ALL),
        ("Giza relief", ["egypt", "giza"], ALL),
        ("Predynastic Egyptian", ["egypt", "predynastic"], ALL),
        ("canopic jar", ["egypt"], ALL),
        ("Book of the Dead", ["egypt"], ALL),
        ("sarcophagus Egypt", ["egypt"], ALL),
        ("Egyptian bronze cat", ["egypt"], ALL),
        ("Horus Egypt", ["egypt"], ALL),
        ("Isis Egypt", ["egypt"], ALL),
        ("Meroe Kush", ["nubia", "kush", "meroe", "sudan"], ALL),
        ("Kerma Nubia", ["nubia", "sudan", "kerma"], ALL),
        ("ushabti", ["egypt"], ALL),
        ("Egyptian glass", ["egypt"], ALL),
        ("Coptic icon", ["coptic", "egypt", "byzantine"], ALL),
        ("Egyptian granite", ["egypt"], ALL),
        ("Akhenaten", ["egypt", "amarna"], ALL),
        ("Nefertiti", ["egypt", "amarna"], ALL),
        ("Tutankhamun", ["egypt"], ALL),
        ("Ramesses", ["egypt"], ALL),
        ("Hatshepsut", ["egypt"], ALL),
        ("Ptah Egyptian", ["egypt"], ALL),
        ("Sekhmet", ["egypt"], ALL),
        ("Bastet", ["egypt"], ALL),
        ("Anubis Egypt", ["egypt"], ALL),
        ("Bes Egypt", ["egypt"], ALL),
        ("Egyptian cartouche", ["egypt"], ALL),
        ("Egyptian limestone relief", ["egypt"], ALL),
        ("Egyptian statuette", ["egypt"], ALL),
        ("Egyptian wooden coffin", ["egypt"], ALL),
        ("Taharqa Kush", ["nubia", "kush"], ALL),
        ("Piye", ["nubia", "kush"], ALL),
        ("Egyptian scarab", ["egypt"], ALL),
        ("Fayum portrait", ["egypt", "fayum", "roman"], ALL),
        ("Gerzean palette", ["egypt", "predynastic"], ALL),
    ],
    "africa": [
        ("Yoruba", ["yoruba", "nigeria"], ALL),
        ("Kongo", ["kongo", "congo"], ALL),
        ("Dogon", ["dogon", "mali"], ALL),
        ("Senufo", ["senufo", "ivory coast", "côte"], ALL),
        ("Bamana", ["bamana", "bambara", "mali"], ALL),
        ("Luba", ["luba"], ALL),
        ("Songye", ["songye"], ALL),
        ("Chokwe", ["chokwe"], ALL),
        ("Fang", ["fang", "gabon"], ALL),
        ("Akan Asante", ["akan", "asante", "ghana"], ALL),
        ("Benin bronze", ["benin", "nigeria"], ALL),
        ("Ethiopian icon", ["ethiopia"], ALL),
        ("Mangbetu", ["mangbetu"], ALL),
        ("Kuba", ["kuba", "congo"], ALL),
        ("Mossi", ["mossi", "burkina"], ALL),
        ("Ashanti gold", ["asante", "ashanti", "ghana"], ALL),
        ("Baule", ["baule", "ivory"], ALL),
        ("Makonde", ["makonde", "tanzania", "mozambique"], ALL),
        ("Zulu", ["zulu", "south africa"], ALL),
        ("Tuareg", ["tuareg", "sahara"], ALL),
        ("Nok terracotta", ["nok", "nigeria"], ALL),
        ("Igbo", ["igbo", "nigeria"], ALL),
        ("Ibibio", ["ibibio", "nigeria"], ALL),
        ("Edo Nigeria", ["edo", "nigeria", "benin"], ALL),
        ("Fon Dahomey", ["fon", "dahomey", "benin"], ALL),
        ("Bwa Mossi", ["bwa", "mossi", "burkina"], ALL),
        ("Lobi", ["lobi", "burkina"], ALL),
        ("Guro", ["guro", "ivory coast", "côte"], ALL),
        ("Dan", ["dan", "ivory coast", "liberia"], ALL),
        ("Mende", ["mende", "sierra leone"], ALL),
        ("Sapi Sherbro", ["sapi", "sherbro", "sierra leone"], ALL),
        ("Punu Gabon", ["punu", "gabon"], ALL),
        ("Kota reliquary", ["kota", "gabon"], ALL),
        ("Teke", ["teke", "congo"], ALL),
        ("Pende", ["pende", "congo"], ALL),
        ("Yaka", ["yaka", "congo"], ALL),
        ("Mangbetu", ["mangbetu", "congo"], ALL),
        ("Shona", ["shona", "zimbabwe"], ALL),
        ("Ndebele", ["ndebele", "south africa"], ALL),
        ("Baga", ["baga", "guinea"], ALL),
        ("Lega", ["lega", "congo"], ALL),
        ("Mumuye", ["mumuye", "nigeria"], ALL),
        ("Jukun", ["jukun", "nigeria"], ALL),
        ("Bamum", ["bamum", "cameroon"], ALL),
        ("Bamileke Cameroon", ["bamileke", "cameroon"], ALL),
        ("Mbole", ["mbole", "congo"], ALL),
        ("Tabwa", ["tabwa", "congo"], ALL),
        ("Hemba", ["hemba", "congo"], ALL),
        ("Ethiopian cross", ["ethiopia"], ALL),
        ("Egyptian Christian Coptic", ["coptic", "egypt"], ALL),
        ("Namibian", ["namibia", "himba"], ALL),
        ("Malagasy", ["madagascar"], ALL),
        ("Swahili coast", ["swahili", "kenya", "tanzania"], ALL),
        ("Fulani", ["fulani", "fulbe", "niger", "nigeria"], ALL),
        ("Tuareg silver", ["tuareg", "niger", "mali"], ALL),
        ("Ashanti goldweight", ["asante", "ashanti", "ghana"], ALL),
        ("Ethiopian manuscript", ["ethiopia"], ALL),
        ("Benin queen mother", ["benin", "nigeria"], ALL),
        ("Ife", ["ife", "nigeria"], ALL),
        ("Igbo Mbari", ["igbo", "nigeria"], ALL),
        ("Kongo Vili", ["vili", "kongo", "congo"], ALL),
        ("Kwele mask", ["kwele", "gabon", "congo"], ALL),
        ("Bembe", ["bembe", "congo"], ALL),
        ("Chokwe chair", ["chokwe", "angola", "congo"], ALL),
        ("Zande", ["zande", "congo", "sudan"], ALL),
        ("Senufo pakha", ["senufo", "côte", "ivory"], ALL),
        ("Moba", ["moba", "togo"], ALL),
        ("Ewe cloth", ["ewe", "ghana", "togo"], ALL),
        ("Agbogbo", ["igbo", "nigeria"], ALL),
        ("Urhobo", ["urhobo", "nigeria"], ALL),
        ("Mbole", ["mbole", "congo"], ALL),
        ("Kuba ndop", ["kuba", "congo"], ALL),
        ("Mali cast iron", ["mali", "dogon"], ALL),
        ("Gelede", ["yoruba", "nigeria", "benin"], ALL),
        ("Epa mask", ["yoruba", "nigeria"], ALL),
        ("Egungun", ["yoruba", "nigeria"], ALL),
        ("Chi Wara", ["bamana", "mali"], ALL),
    ],
    "islamic-world": [
        ("Iznik", ["turkey", "iznik", "ottoman"], ALL),
        ("Safavid", ["iran", "safavid"], ALL),
        ("Mamluk", ["mamluk", "egypt", "syria"], ALL),
        ("Mughal painting", ["mughal", "india"], ALL),
        ("Ottoman textile", ["ottoman", "turkey"], ALL),
        ("Kashan lusterware", ["kashan", "iran"], ALL),
        ("Qajar painting", ["qajar", "iran"], ALL),
        ("Timurid", ["timurid", "iran", "herat"], ALL),
        ("Persian miniature", ["iran", "persian"], ALL),
        ("Shahnameh", ["iran", "persian"], ALL),
        ("Seljuk", ["seljuk", "iran", "anatolia"], ALL),
        ("Fatimid", ["fatimid", "egypt"], ALL),
        ("Nasrid", ["nasrid", "spain", "granada"], ALL),
        ("Ilkhanid", ["ilkhan", "iran"], ALL),
        ("Moroccan", ["morocco", "moroccan"], ALL),
        ("Abbasid", ["abbasid", "iraq"], ALL),
        ("Umayyad", ["umayyad"], ALL),
        ("Deccani painting", ["deccan", "india"], ALL),
        ("Indo-Persian", ["india", "persian", "mughal"], ALL),
        ("Arab calligraphy", ["arab", "egypt", "syria", "iraq"], ALL),
        ("Persian carpet", ["iran", "persian"], ALL),
        ("Safavid carpet", ["iran", "safavid"], ALL),
        ("Isfahan carpet", ["iran", "isfahan"], ALL),
        ("Mughal jade", ["india", "mughal"], ALL),
        ("Mughal jewelry", ["india", "mughal"], ALL),
        ("Ottoman tile", ["turkey", "ottoman", "iznik"], ALL),
        ("Alhambra tile", ["spain", "granada", "nasrid"], ALL),
        ("Syrian glass mosque lamp", ["syria", "egypt", "mamluk"], ALL),
        ("Nizami Khamsa", ["iran", "persian", "mughal"], ALL),
        ("Behzad", ["iran", "persian", "herat"], ALL),
        ("Reza Abbasi", ["iran", "safavid"], ALL),
        ("Bihzad manuscript", ["iran", "persian", "herat"], ALL),
        ("Persian tile lustre", ["iran", "kashan"], ALL),
        ("Damascus tile", ["syria", "damascus"], ALL),
        ("Hispano-Moresque", ["spain", "valencia"], ALL),
        ("Mudéjar", ["spain", "mudejar"], ALL),
        ("Ottoman calligraphy", ["turkey", "ottoman"], ALL),
        ("Safavid textile", ["iran", "safavid"], ALL),
        ("Ottoman silk", ["turkey", "ottoman"], ALL),
        ("Mughal textile", ["india", "mughal"], ALL),
        ("Koran illumination", ["iran", "egypt", "mughal", "persian", "ottoman"], ALL),
        ("Kashmiri shawl", ["india", "kashmir"], ALL),
        ("Ottoman miniature", ["turkey", "ottoman"], ALL),
        ("Bihzad miniature", ["iran", "persian", "herat"], ALL),
        ("Sultan Muhammad", ["iran", "persian", "tabriz"], ALL),
        ("Mir Sayyid Ali", ["iran", "persian", "mughal"], ALL),
        ("Aqa Mirak", ["iran", "persian"], ALL),
        ("Basawan", ["india", "mughal"], ALL),
        ("Manohar", ["india", "mughal"], ALL),
        ("Daswanth", ["india", "mughal"], ALL),
        ("Miskin", ["india", "mughal"], ALL),
        ("Abu'l-Hasan", ["india", "mughal"], ALL),
        ("Govardhan", ["india", "mughal"], ALL),
        ("Nanha", ["india", "mughal"], ALL),
        ("Balchand", ["india", "mughal"], ALL),
        ("Payag", ["india", "mughal"], ALL),
        ("Levni", ["turkey", "ottoman"], ALL),
        ("Matrakci Nasuh", ["turkey", "ottoman"], ALL),
        ("Nakkas Osman", ["turkey", "ottoman"], ALL),
        ("Jahangir portrait", ["india", "mughal"], ALL),
        ("Akbar hunting", ["india", "mughal"], ALL),
        ("Shah Jahan", ["india", "mughal"], ALL),
        ("Babur", ["india", "mughal"], ALL),
        ("Mir Ali of Herat", ["iran", "persian"], ALL),
        ("Iznik mosque lamp", ["turkey", "iznik", "ottoman"], ALL),
        ("Nasta'liq", ["iran", "persian", "mughal"], ALL),
        ("Thuluth", ["egypt", "syria", "arab"], ALL),
        ("Kufic", ["iran", "egypt", "syria"], ALL),
        ("Maghrebi manuscript", ["morocco", "maghreb", "andalusia"], ALL),
        ("Bukhara manuscript", ["uzbek", "bukhara"], ALL),
        ("Safavid tile", ["iran", "safavid"], ALL),
        ("Kharagpur India", ["india"], ALL),
        ("Persian silver", ["iran", "persian"], ALL),
    ],
    "americas": [
        ("Maya", ["maya"], ALL),
        ("Moche", ["moche", "peru"], ALL),
        ("Nazca", ["nasca", "nazca", "peru"], ALL),
        ("Wari", ["wari", "huari", "peru"], ALL),
        ("Inca", ["inca", "peru"], ALL),
        ("Aztec", ["aztec", "mexico"], ALL),
        ("Olmec", ["olmec", "mexico"], ALL),
        ("Veracruz", ["veracruz", "mexico"], ALL),
        ("Teotihuacan", ["teotihuacan", "mexico"], ALL),
        ("Northwest Coast Tlingit", ["tlingit", "haida", "kwakwaka", "northwest"], ALL),
        ("Chancay", ["chancay", "peru"], ALL),
        ("Chimú", ["chim", "peru"], ALL),
        ("Mixtec", ["mixtec", "mexico"], ALL),
        ("Zapotec", ["zapotec", "mexico", "monte alban"], ALL),
        ("Huastec", ["huastec", "mexico"], ALL),
        ("Navajo", ["navajo", "new mexico", "arizona"], ALL),
        ("Plains beadwork", ["plains", "sioux", "cheyenne", "native"], ALL),
        ("Pueblo pottery", ["pueblo", "new mexico", "hopi"], ALL),
        ("Chavin", ["chavin", "peru"], ALL),
        ("Paracas", ["paracas", "peru"], ALL),
        ("Calima gold", ["calima", "colombia"], ALL),
        ("Tairona", ["tairona", "colombia"], ALL),
        ("Muisca", ["muisca", "colombia"], ALL),
        ("Quimbaya", ["quimbaya", "colombia"], ALL),
        ("Costa Rica jade", ["costa rica"], ALL),
        ("Panama gold", ["panama"], ALL),
        ("Diquís", ["diquís", "costa rica"], ALL),
        ("Coclé", ["coclé", "panama"], ALL),
        ("Sinú gold", ["sinú", "zenú", "colombia"], ALL),
        ("Jama-Coaque", ["jama", "ecuador"], ALL),
        ("La Tolita", ["tolita", "ecuador"], ALL),
        ("Chorrera", ["chorrera", "ecuador"], ALL),
        ("Bahía Ecuador", ["bahía", "ecuador"], ALL),
        ("Recuay", ["recuay", "peru"], ALL),
        ("Cupisnique", ["cupisnique", "peru"], ALL),
        ("Sicán", ["sican", "lambayeque", "peru"], ALL),
        ("Chancay cloth", ["chancay", "peru"], ALL),
        ("Moche stirrup", ["moche", "peru"], ALL),
        ("Nazca textile", ["nazca", "nasca", "peru"], ALL),
        ("Inca quipu", ["inca", "peru"], ALL),
        ("Mixtec turquoise", ["mixtec", "mexico"], ALL),
        ("Aztec stone sculpture", ["aztec", "mexico"], ALL),
        ("Zapotec urn", ["zapotec", "monte alban", "mexico"], ALL),
        ("Colima dog", ["colima", "mexico"], ALL),
        ("Jalisco", ["jalisco", "mexico"], ALL),
        ("Nayarit", ["nayarit", "mexico"], ALL),
        ("Cahokia", ["cahokia", "mississippian"], ALL),
        ("Mississippian", ["mississippian", "native american"], ALL),
        ("Iroquois", ["iroquois", "native american"], ALL),
        ("Sioux beadwork", ["sioux", "plains", "native american"], ALL),
        ("Cherokee", ["cherokee", "native american"], ALL),
        ("Mimbres", ["mimbres", "new mexico"], ALL),
        ("Anasazi", ["anasazi", "ancestral pueblo", "new mexico"], ALL),
        ("Haida", ["haida", "northwest"], ALL),
        ("Kwakwaka'wakw", ["kwakwaka", "kwakiutl"], ALL),
        ("Inuit", ["inuit", "eskimo", "alaska"], ALL),
        ("Aleut", ["aleut", "alaska"], ALL),
        ("Lacquerware Cuzco", ["cuzco", "peru"], ALL),
        ("Maya stela", ["maya"], ALL),
        ("Maya codex vessel", ["maya"], ALL),
        ("Palenque", ["maya", "mexico"], ALL),
        ("Copan", ["maya", "honduras"], ALL),
        ("Tikal", ["maya", "guatemala"], ALL),
        ("Yaxchilan", ["maya"], ALL),
        ("Moche pot", ["moche", "peru"], ALL),
        ("Peruvian textile", ["peru", "andean"], ALL),
        ("Aymara", ["aymara", "bolivia"], ALL),
        ("Quechua", ["quechua", "peru"], ALL),
        ("Andean bronze", ["andean", "peru"], ALL),
        ("Andean silver", ["andean", "peru"], ALL),
        ("Ica vessel", ["ica", "peru"], ALL),
        ("Puebla pottery", ["puebla", "mexico"], ALL),
        ("Talavera", ["talavera", "mexico"], ALL),
        ("Viceregal Spanish colonial", ["mexico", "peru", "colonial"], ALL),
        ("Kuna mola", ["kuna", "panama"], ALL),
        ("Sandpainting Navajo", ["navajo", "native"], ALL),
        ("Cheyenne beadwork", ["cheyenne", "plains", "native"], ALL),
        ("Crow beadwork", ["crow", "plains", "native"], ALL),
        ("Apache basket", ["apache", "native"], ALL),
        ("Pomo basket", ["pomo", "california"], ALL),
        ("Hopi pottery", ["hopi", "new mexico", "arizona"], ALL),
        ("Zuni pottery", ["zuni", "new mexico"], ALL),
        ("Anishinaabe", ["anishinaabe", "ojibwe", "native"], ALL),
        ("Seminole", ["seminole", "native"], ALL),
        ("Hohokam", ["hohokam", "arizona"], ALL),
        ("Fremont", ["fremont", "utah"], ALL),
        ("Mississippian gorget", ["mississippian", "native"], ALL),
    ],
    "southeast-asia-oceania": [
        ("Khmer bronze", ["cambodia", "khmer"], ALL),
        ("Khmer sandstone", ["cambodia", "khmer"], ALL),
        ("Thai Buddha", ["thailand", "ayutthaya", "sukhothai", "dvaravati"], ALL),
        ("Javanese sculpture", ["java", "indonesia"], ALL),
        ("Burmese Buddha", ["burma", "myanmar", "pagan"], ALL),
        ("Cham", ["cham", "vietnam"], ALL),
        ("Balinese", ["bali"], ALL),
        ("Sepik", ["papua", "sepik"], ALL),
        ("Asmat", ["asmat", "irian", "papua"], ALL),
        ("Solomon Islands", ["solomon"], ALL),
        ("Polynesian", ["polynesia", "hawaii", "marquesas", "tahiti"], ALL),
        ("Māori", ["maori", "new zealand"], ALL),
        ("Philippines textile", ["philippines"], ALL),
        ("Thai manuscript", ["thailand"], ALL),
        ("Vietnamese ceramic", ["vietnam"], ALL),
        ("Indonesian textile", ["indonesia"], ALL),
        ("Fiji", ["fiji"], ALL),
        ("Australian aboriginal", ["australia", "aboriginal"], ALL),
        ("Dayak Borneo", ["borneo", "dayak"], ALL),
        ("Angkor", ["cambodia", "angkor"], ALL),
        ("Banteay Srei", ["cambodia"], ALL),
        ("Phnom Da", ["cambodia", "phnom"], ALL),
        ("Funan", ["funan", "cambodia", "vietnam"], ALL),
        ("Oc Eo", ["oc eo", "vietnam"], ALL),
        ("Srivijaya", ["srivijaya", "sumatra"], ALL),
        ("Majapahit", ["majapahit", "java"], ALL),
        ("Borobudur", ["java", "borobudur"], ALL),
        ("Prambanan", ["java", "prambanan"], ALL),
        ("Sukhothai ceramic", ["thailand", "sukhothai"], ALL),
        ("Sawankhalok", ["thailand", "sawankhalok"], ALL),
        ("Bencharong", ["thailand", "bencharong"], ALL),
        ("Ban Chiang", ["thailand", "ban chiang"], ALL),
        ("Dong Son", ["vietnam", "dong son", "dongson"], ALL),
        ("Vietnam Le dynasty", ["vietnam"], ALL),
        ("Annam ceramic", ["vietnam", "annam"], ALL),
        ("Burmese lacquer", ["burma", "myanmar"], ALL),
        ("Pagan Burma", ["burma", "myanmar", "pagan"], ALL),
        ("Mon Buddha", ["mon", "thailand", "burma", "myanmar"], ALL),
        ("Dvaravati", ["thailand", "dvaravati"], ALL),
        ("Khmer lintel", ["cambodia", "khmer"], ALL),
        ("Batak", ["batak", "sumatra"], ALL),
        ("Nias", ["nias", "indonesia"], ALL),
        ("Kalimantan", ["kalimantan", "borneo"], ALL),
        ("Torres Strait", ["torres", "papua"], ALL),
        ("Marshall Islands", ["marshall"], ALL),
        ("Caroline Islands", ["caroline", "micronesia"], ALL),
        ("Cook Islands", ["cook islands", "polynesia"], ALL),
        ("Tonga", ["tonga", "polynesia"], ALL),
        ("Samoa", ["samoa", "polynesia"], ALL),
        ("Marquesas", ["marquesas", "polynesia"], ALL),
        ("Easter Island", ["easter", "rapa nui"], ALL),
        ("Balinese painting", ["bali"], ALL),
        ("Thai Lanna", ["thailand", "lanna"], ALL),
        ("Thai Chiang Mai", ["thailand", "chiang mai"], ALL),
        ("Angkor bronze", ["cambodia", "khmer"], ALL),
        ("Pre-Angkor", ["cambodia"], ALL),
        ("Vishnu Cambodia", ["cambodia"], ALL),
        ("Shiva Khmer", ["cambodia"], ALL),
        ("Java gold", ["java", "indonesia"], ALL),
        ("Sailendra", ["java", "sailendra"], ALL),
        ("Ratnagiri", ["india", "orissa"], ALL),
        ("Mataram bronze", ["java", "indonesia", "mataram"], ALL),
        ("Khmer Banteay Chhmar", ["cambodia"], ALL),
        ("Khmer linga yoni", ["cambodia"], ALL),
        ("Cham Dong Duong", ["vietnam", "cham"], ALL),
        ("Le dynasty", ["vietnam"], ALL),
        ("Nguyen dynasty", ["vietnam", "nguyen"], ALL),
        ("Lao Buddha", ["laos", "lan xang"], ALL),
        ("Hmong embroidery", ["hmong", "laos", "vietnam", "thailand"], ALL),
        ("Karen textile", ["karen", "thailand", "burma", "myanmar"], ALL),
        ("Ifugao", ["philippines", "ifugao"], ALL),
        ("Bontoc", ["philippines", "bontoc"], ALL),
        ("Moluccan", ["moluccas", "indonesia"], ALL),
        ("Sulawesi", ["sulawesi", "indonesia"], ALL),
        ("Tongan", ["tonga"], ALL),
        ("Society Islands", ["society islands", "tahiti"], ALL),
        ("Hawaiian feather", ["hawaii", "hawaiian"], ALL),
        ("Melanesian", ["melanesia", "papua", "vanuatu"], ALL),
        ("Kirgiz", ["kyrgyz", "central asia"], ALL),
    ],
    "south-asia": [
        ("Chola bronze", ["india", "chola"], ALL),
        ("Gandhara", ["gandhara", "pakistan", "afghanistan"], ALL),
        ("Pala", ["pala", "bihar", "india"], ALL),
        ("Nepal bronze", ["nepal"], ALL),
        ("Tibet thangka", ["tibet"], ALL),
        ("Rajput", ["rajput", "india"], ALL),
        ("Pahari painting", ["pahari", "kangra", "basohli", "india"], ALL),
        ("Jain manuscript", ["jain", "india"], ALL),
        ("Mathura sculpture", ["mathura", "india"], ALL),
        ("Hoysala", ["hoysala", "karnataka", "india"], ALL),
        ("Vijayanagara", ["vijayanagara", "india"], ALL),
        ("Company School", ["company", "india"], ALL),
        ("Bengal Kalighat", ["kalighat", "bengal", "india"], ALL),
        ("Kushan", ["kushan", "india", "pakistan"], ALL),
        ("Sri Lanka Buddha", ["sri lanka", "ceylon"], ALL),
        ("Kerala mural", ["kerala", "india"], ALL),
        ("Jaipur painting", ["jaipur", "rajasthan", "india"], ALL),
        ("Indian bronze Shiva", ["india"], ALL),
        ("Gupta Buddha", ["india", "gupta"], ALL),
        ("Maurya", ["india", "maurya"], ALL),
        ("Shunga", ["india", "shunga"], ALL),
        ("Pallava", ["india", "pallava"], ALL),
        ("Pandya", ["india", "pandya"], ALL),
        ("Sena Bengal", ["india", "sena", "bengal"], ALL),
        ("Ajanta", ["india", "ajanta"], ALL),
        ("Ellora", ["india", "ellora"], ALL),
        ("Sanchi", ["india", "sanchi"], ALL),
        ("Barhut", ["india", "barhut", "bharhut"], ALL),
        ("Amaravati", ["india", "amaravati"], ALL),
        ("Indian miniature", ["india"], ALL),
        ("Bundi painting", ["india", "bundi"], ALL),
        ("Kota painting", ["india", "kota"], ALL),
        ("Kangra painting", ["india", "kangra"], ALL),
        ("Basohli painting", ["india", "basohli"], ALL),
        ("Guler painting", ["india", "guler"], ALL),
        ("Tibetan Buddhist bronze", ["tibet"], ALL),
        ("Tibetan mandala", ["tibet"], ALL),
        ("Bhutan", ["bhutan"], ALL),
        ("Nepalese", ["nepal"], ALL),
        ("Pahari", ["pahari", "india"], ALL),
        ("Deccani", ["deccan", "deccani", "india"], ALL),
        ("Jaipur miniature", ["india", "jaipur"], ALL),
        ("Sikh", ["sikh", "punjab", "india"], ALL),
        ("Hindu temple sculpture", ["india"], ALL),
        ("Chola Shiva", ["india", "chola"], ALL),
        ("Pala bronze", ["india", "pala"], ALL),
        ("Kashmir bronze", ["kashmir", "india"], ALL),
        ("Gandhara stucco", ["gandhara", "pakistan", "afghanistan"], ALL),
        ("Sri Lankan bronze", ["sri lanka", "ceylon"], ALL),
        ("Orissan", ["orissa", "odisha", "india"], ALL),
        ("Khajuraho", ["khajuraho", "india"], ALL),
        ("Konark", ["konark", "india"], ALL),
        ("Kailasa", ["india", "ellora"], ALL),
        ("Buddhist stupa", ["india", "pakistan", "nepal"], ALL),
        ("Buddha Gupta", ["india", "gupta"], ALL),
        ("Vishnu India", ["india"], ALL),
        ("Krishna India", ["india"], ALL),
        ("Ganesha India", ["india"], ALL),
        ("Shiva Nataraja", ["india"], ALL),
        ("Parvati", ["india"], ALL),
        ("Saraswati", ["india"], ALL),
        ("Lakshmi", ["india"], ALL),
        ("Tara Buddhist", ["tibet", "nepal", "india"], ALL),
        ("Avalokiteshvara", ["tibet", "nepal", "india", "china"], ALL),
        ("Manjushri", ["tibet", "nepal", "india"], ALL),
        ("Mahayana bronze", ["tibet", "nepal", "india"], ALL),
        ("Tibetan thangka deity", ["tibet"], ALL),
        ("Kashmir manuscript", ["kashmir", "india"], ALL),
        ("Bengal painting", ["india", "bengal"], ALL),
        ("Ravi Varma", ["india"], ALL),
        ("Pattachitra", ["india", "orissa", "odisha"], ALL),
        ("Madhubani", ["india", "bihar"], ALL),
        ("Warli", ["india", "maharashtra"], ALL),
        ("Mewar painting", ["india", "mewar", "rajasthan"], ALL),
        ("Mughal miniature album", ["india", "mughal"], ALL),
        ("Satavahana", ["india", "satavahana"], ALL),
        ("Kerala bronze", ["india", "kerala"], ALL),
        ("Dravidian stone", ["india"], ALL),
        ("Indian jewelry gold", ["india"], ALL),
    ],
    "east-asia": [
        ("Ming porcelain", ["china", "ming"], ALL),
        ("Qing porcelain", ["china", "qing"], ALL),
        ("Song ceramics", ["china", "song"], ALL),
        ("Tang", ["china", "tang"], ALL),
        ("Chinese painting Song", ["china", "song"], ALL),
        ("Chinese painting Ming", ["china", "ming"], ALL),
        ("Chinese painting Yuan", ["china", "yuan"], ALL),
        ("Chinese bronze Shang", ["china", "shang"], ALL),
        ("Chinese bronze Zhou", ["china", "zhou"], ALL),
        ("Chinese jade", ["china"], ALL),
        ("Chinese calligraphy", ["china"], ALL),
        ("Chinese lacquer", ["china"], ALL),
        ("Ukiyo-e", ["japan"], ALL),
        ("Hokusai", ["japan"], ALL),
        ("Hiroshige", ["japan"], ALL),
        ("Utamaro", ["japan"], ALL),
        ("Japanese screen", ["japan"], ALL),
        ("Japanese lacquer", ["japan"], ALL),
        ("Japanese Buddhist", ["japan"], ALL),
        ("Kamakura", ["japan", "kamakura"], ALL),
        ("Heian", ["japan", "heian"], ALL),
        ("Edo period", ["japan", "edo"], ALL),
        ("Meiji", ["japan", "meiji"], ALL),
        ("Korean celadon", ["korea", "koryo", "goryeo"], ALL),
        ("Joseon", ["korea", "joseon"], ALL),
        ("Buncheong", ["korea", "buncheong"], ALL),
        ("Korean painting", ["korea"], ALL),
        ("Chinese tomb figure", ["china"], ALL),
        ("netsuke", ["japan"], ALL),
        ("Han dynasty", ["china", "han"], ALL),
        ("Zhou bronze", ["china", "zhou"], ALL),
        ("Shang bronze", ["china", "shang"], ALL),
        ("Neolithic Chinese", ["china", "neolithic"], ALL),
        ("Chinese snuff bottle", ["china"], ALL),
        ("Tang horse", ["china", "tang"], ALL),
        ("Yuan porcelain", ["china", "yuan"], ALL),
        ("Longquan celadon", ["china", "longquan"], ALL),
        ("Jun ware", ["china", "jun"], ALL),
        ("Ding ware", ["china", "ding"], ALL),
        ("Ru ware", ["china", "ru"], ALL),
        ("Cizhou", ["china", "cizhou"], ALL),
        ("Chinese silk", ["china"], ALL),
        ("Chinese embroidery", ["china"], ALL),
        ("Chinese fan painting", ["china"], ALL),
        ("Chinese album leaf", ["china"], ALL),
        ("Shen Zhou", ["china", "ming"], ALL),
        ("Wen Zhengming", ["china", "ming"], ALL),
        ("Dong Qichang", ["china", "ming"], ALL),
        ("Bada Shanren", ["china", "qing"], ALL),
        ("Shitao", ["china", "qing"], ALL),
        ("Qi Baishi", ["china"], ALL),
        ("Zhao Mengfu", ["china", "yuan"], ALL),
        ("Ni Zan", ["china", "yuan"], ALL),
        ("Japanese woodblock", ["japan"], ALL),
        ("Utagawa Kuniyoshi", ["japan"], ALL),
        ("Kitagawa Utamaro", ["japan"], ALL),
        ("Katsushika Hokusai", ["japan"], ALL),
        ("Ando Hiroshige", ["japan"], ALL),
        ("Tōshūsai Sharaku", ["japan"], ALL),
        ("Yoshitoshi", ["japan"], ALL),
        ("Kunisada", ["japan"], ALL),
        ("Suzuki Harunobu", ["japan"], ALL),
        ("Kiyonaga", ["japan"], ALL),
        ("Japanese Nanban", ["japan", "nanban"], ALL),
        ("Japanese Rinpa", ["japan"], ALL),
        ("Kano school", ["japan"], ALL),
        ("Tosa school", ["japan"], ALL),
        ("Zen calligraphy", ["japan"], ALL),
        ("Tea ceremony", ["japan"], ALL),
        ("Raku tea bowl", ["japan"], ALL),
        ("Oribe ware", ["japan"], ALL),
        ("Shino ware", ["japan"], ALL),
        ("Japanese inro", ["japan"], ALL),
        ("Jomon pottery", ["japan", "jomon"], ALL),
        ("Haniwa", ["japan", "kofun"], ALL),
        ("Korean Silla", ["korea", "silla"], ALL),
        ("Korean Baekje", ["korea", "baekje"], ALL),
        ("Goryeo celadon", ["korea", "goryeo", "koryo"], ALL),
        ("Korean folk painting", ["korea", "joseon"], ALL),
        ("Korean lacquer", ["korea"], ALL),
        ("Ma Yuan", ["china"], ALL),
        ("Xia Gui", ["china"], ALL),
        ("Li Cheng", ["china"], ALL),
        ("Guo Xi", ["china"], ALL),
        ("Fan Kuan", ["china"], ALL),
        ("Liang Kai", ["china"], ALL),
        ("Muqi", ["china"], ALL),
        ("Wang Meng", ["china"], ALL),
        ("Huang Gongwang", ["china"], ALL),
        ("Qiu Ying", ["china"], ALL),
        ("Tang Yin", ["china"], ALL),
        ("Shitao landscape", ["china"], ALL),
        ("Zhu Da", ["china"], ALL),
        ("Gong Xian", ["china"], ALL),
        ("Wu Zhen", ["china"], ALL),
        ("Chen Hongshou", ["china"], ALL),
        ("Shen Nanpin", ["china"], ALL),
        ("Yuan Jiang", ["china"], ALL),
        ("Zhang Xuan", ["china"], ALL),
        ("Gu Kaizhi", ["china"], ALL),
        ("Chinese Buddhist sculpture", ["china"], ALL),
        ("Bronze mirror Tang", ["china", "tang"], ALL),
        ("Blue-and-white Chinese", ["china", "ming", "yuan"], ALL),
        ("Famille rose", ["china"], ALL),
        ("Famille verte", ["china"], ALL),
        ("Jingdezhen", ["china"], ALL),
        ("Guan ware", ["china", "guan"], ALL),
        ("Cloisonné", ["china", "japan"], ALL),
        ("Chinese rhinoceros horn", ["china"], ALL),
        ("Sotatsu", ["japan"], ALL),
        ("Ogata Korin", ["japan"], ALL),
        ("Itō Jakuchū", ["japan"], ALL),
        ("Maruyama Okyo", ["japan"], ALL),
        ("Hon'ami Kōetsu", ["japan"], ALL),
        ("Sakai Hōitsu", ["japan"], ALL),
        ("Tawaraya Sotatsu", ["japan"], ALL),
        ("Nagasawa Rosetsu", ["japan"], ALL),
        ("Shubun", ["japan"], ALL),
        ("Sesshū", ["japan"], ALL),
        ("Kanō Eitoku", ["japan"], ALL),
        ("Kanō Motonobu", ["japan"], ALL),
        ("Hasegawa Tōhaku", ["japan"], ALL),
        ("Jakuchū chicken", ["japan"], ALL),
        ("Japanese sword tsuba", ["japan"], ALL),
        ("Samurai armor", ["japan"], ALL),
        ("Buncheong bowl", ["korea", "buncheong"], ALL),
        ("Korean moon jar", ["korea", "joseon"], ALL),
    ],
    "europe": [
        ("Rembrandt", ["netherlands", "dutch"], ALL),
        ("Dürer", ["german", "nuremberg"], ALL),
        ("Monet", ["france", "french"], ALL),
        ("Van Gogh", ["netherlands", "france", "dutch"], ALL),
        ("Cézanne", ["france", "french"], ALL),
        ("Manet", ["france", "french"], ALL),
        ("Degas", ["france", "french"], ALL),
        ("Turner", ["england", "british"], ALL),
        ("Goya", ["spain", "spanish"], ALL),
        ("Constable", ["england", "british"], ALL),
        ("Italian Renaissance", ["italy", "italian"], ALL),
        ("Raphael drawing", ["italy", "italian"], ALL),
        ("Titian", ["italy", "italian", "venice"], ALL),
        ("Caravaggio", ["italy", "italian"], ALL),
        ("Flemish painting", ["flemish", "belgium", "netherlands"], ALL),
        ("Medieval manuscript", ["france", "england", "italy", "german"], ALL),
        ("Byzantine icon", ["byzantine", "greek"], ALL),
        ("Russian icon", ["russia", "russian"], ALL),
        ("Art Nouveau", ["france", "austria", "belgium"], ALL),
        ("Impressionism", ["france", "french"], ALL),
        ("Post-Impressionism", ["france", "french"], ALL),
        ("Dutch still life", ["netherlands", "dutch"], ALL),
        ("Baroque", ["italy", "netherlands", "flemish", "spain"], ALL),
        ("Renaissance bronze", ["italy", "italian"], ALL),
        ("Gothic sculpture", ["france", "german", "english"], ALL),
        ("Romantic landscape", ["france", "england", "german"], ALL),
        ("Velázquez", ["spain", "spanish"], ALL),
        ("El Greco", ["spain", "crete", "greek"], ALL),
        ("Botticelli", ["italy", "italian", "florence"], ALL),
        ("Hieronymus Bosch", ["netherlands", "flemish", "dutch"], ALL),
        ("Pieter Bruegel", ["flemish", "netherlands", "belgium"], ALL),
        ("Frans Hals", ["netherlands", "dutch"], ALL),
        ("Vermeer", ["netherlands", "dutch"], ALL),
        ("Jacob van Ruisdael", ["netherlands", "dutch"], ALL),
        ("Fragonard", ["france", "french"], ALL),
        ("Watteau", ["france", "french"], ALL),
        ("Gainsborough", ["england", "british"], ALL),
        ("Reynolds", ["england", "british"], ALL),
        ("Jacques-Louis David", ["france", "french"], ALL),
        ("Ingres", ["france", "french"], ALL),
        ("Delacroix", ["france", "french"], ALL),
        ("Courbet", ["france", "french"], ALL),
        ("Corot", ["france", "french"], ALL),
        ("Millet", ["france", "french"], ALL),
        ("Renoir", ["france", "french"], ALL),
        ("Pissarro", ["france", "french"], ALL),
        ("Sisley", ["france", "french"], ALL),
        ("Seurat", ["france", "french"], ALL),
        ("Signac", ["france", "french"], ALL),
        ("Toulouse-Lautrec", ["france", "french"], ALL),
        ("Gauguin", ["france", "tahiti", "french"], ALL),
        ("Klimt", ["austria", "vienna"], ALL),
        ("Schiele", ["austria", "vienna"], ALL),
        ("Edvard Munch", ["norway", "norwegian"], ALL),
        ("Whistler", ["america", "britain", "english"], ALL),
        ("Sargent", ["america", "american"], ALL),
        ("Winslow Homer", ["america", "american"], ALL),
        ("Thomas Eakins", ["america", "american"], ALL),
        ("Cassatt", ["america", "american", "france"], ALL),
        ("Edward Hopper", ["america", "american"], ALL),
        ("Georges Braque", ["france", "french"], ALL),
        ("Pablo Picasso", ["spain", "france", "spanish"], ALL),
        ("Henri Matisse", ["france", "french"], ALL),
        ("Paul Klee", ["germany", "swiss", "switzerland"], ALL),
        ("Kandinsky", ["russia", "germany"], ALL),
        ("Malevich", ["russia", "soviet"], ALL),
        ("Chagall", ["russia", "france", "french"], ALL),
        ("Mondrian", ["netherlands", "dutch"], ALL),
        ("Leonardo", ["italy", "italian", "florence"], ALL),
        ("Michelangelo", ["italy", "italian"], ALL),
        ("Lucas Cranach", ["germany", "german"], ALL),
        ("Hans Holbein", ["germany", "swiss", "british"], ALL),
        ("Peter Paul Rubens", ["flemish", "belgium"], ALL),
        ("Anthony van Dyck", ["flemish", "belgium", "britain", "english"], ALL),
        ("Tiepolo", ["italy", "italian", "venice"], ALL),
        ("Canaletto", ["italy", "italian", "venice"], ALL),
        ("Guardi", ["italy", "italian", "venice"], ALL),
        ("French tapestry", ["france", "french"], ALL),
        ("Sèvres porcelain", ["france", "french"], ALL),
        ("Meissen porcelain", ["germany", "german", "meissen"], ALL),
        ("English silver", ["england", "british"], ALL),
        ("Fabergé", ["russia", "russian"], ALL),
        ("Icon Russian", ["russia", "russian"], ALL),
        ("German expressionism", ["germany", "german"], ALL),
        ("Die Brücke", ["germany", "german"], ALL),
        ("Bauhaus", ["germany", "german"], ALL),
        ("Fauvism", ["france", "french"], ALL),
        ("Cubism", ["france", "french", "spain"], ALL),
        ("Vienna Secession", ["austria", "vienna"], ALL),
        ("Wedgwood", ["england", "british"], ALL),
        ("Tiffany", ["america", "american"], ALL),
        ("William Morris", ["england", "british"], ALL),
        ("Pre-Raphaelite", ["england", "british"], ALL),
        ("Rococo", ["france", "french", "german", "italy"], ALL),
        ("Neoclassical", ["france", "italy", "english", "british"], ALL),
        ("Georgian silver", ["england", "british"], ALL),
        ("Caspar David Friedrich", ["germany", "german"], ALL),
        ("Friedrich Overbeck", ["germany", "german"], ALL),
        ("Anselm Feuerbach", ["germany", "german"], ALL),
        ("Adolph Menzel", ["germany", "german"], ALL),
        ("Lovis Corinth", ["germany", "german"], ALL),
        ("Max Liebermann", ["germany", "german"], ALL),
        ("Fernand Khnopff", ["belgium", "belgian"], ALL),
        ("James Ensor", ["belgium", "belgian"], ALL),
        ("Georges Rouault", ["france", "french"], ALL),
        ("Henri Rousseau", ["france", "french"], ALL),
        ("Maurice Denis", ["france", "french"], ALL),
        ("Pierre Bonnard", ["france", "french"], ALL),
        ("Édouard Vuillard", ["france", "french"], ALL),
        ("Odilon Redon", ["france", "french"], ALL),
        ("Gustave Moreau", ["france", "french"], ALL),
        ("Théodore Géricault", ["france", "french"], ALL),
        ("Honoré Daumier", ["france", "french"], ALL),
        ("Camille Claudel", ["france", "french"], ALL),
        ("Auguste Rodin", ["france", "french"], ALL),
        ("Aristide Maillol", ["france", "french"], ALL),
        ("Eugène Boudin", ["france", "french"], ALL),
        ("Joseph Vernet", ["france", "french"], ALL),
        ("Hubert Robert", ["france", "french"], ALL),
        ("Jean-Baptiste Greuze", ["france", "french"], ALL),
        ("Jean-Baptiste Chardin", ["france", "french"], ALL),
        ("Nicolas Poussin", ["france", "french"], ALL),
        ("Claude Lorrain", ["france", "french", "italy"], ALL),
        ("Georges de La Tour", ["france", "french"], ALL),
        ("Le Nain", ["france", "french"], ALL),
        ("Annibale Carracci", ["italy", "italian", "bologna"], ALL),
        ("Guercino", ["italy", "italian"], ALL),
        ("Domenichino", ["italy", "italian"], ALL),
        ("Salvator Rosa", ["italy", "italian"], ALL),
        ("Alessandro Magnasco", ["italy", "italian"], ALL),
        ("Bernardo Bellotto", ["italy", "italian"], ALL),
        ("Giuseppe Maria Crespi", ["italy", "italian"], ALL),
        ("Pordenone", ["italy", "italian"], ALL),
        ("Tintoretto", ["italy", "italian", "venice"], ALL),
        ("Veronese", ["italy", "italian", "venice"], ALL),
        ("Giorgione", ["italy", "italian", "venice"], ALL),
        ("Bellini", ["italy", "italian", "venice"], ALL),
        ("Mantegna", ["italy", "italian"], ALL),
        ("Fra Angelico", ["italy", "italian", "florence"], ALL),
        ("Filippo Lippi", ["italy", "italian"], ALL),
        ("Luca Signorelli", ["italy", "italian"], ALL),
        ("Piero della Francesca", ["italy", "italian"], ALL),
        ("Domenico Ghirlandaio", ["italy", "italian"], ALL),
        ("Bartolomé Esteban Murillo", ["spain", "spanish"], ALL),
        ("José de Ribera", ["spain", "spanish"], ALL),
        ("Francisco de Zurbarán", ["spain", "spanish"], ALL),
        ("Joaquin Sorolla", ["spain", "spanish"], ALL),
        ("Diego Rivera", ["mexico", "mexican"], ALL),
        ("Frida Kahlo", ["mexico", "mexican"], ALL),
        ("Roy Lichtenstein", ["america", "american"], ALL),
        ("Andy Warhol", ["america", "american"], ALL),
        ("Jackson Pollock", ["america", "american"], ALL),
        ("Mark Rothko", ["america", "american"], ALL),
        ("Willem de Kooning", ["america", "american", "dutch"], ALL),
        ("Georgia O'Keeffe", ["america", "american"], ALL),
        ("Mary Cassatt", ["america", "american"], ALL),
        ("John Singer Sargent", ["america", "american"], ALL),
        ("James Whistler", ["america", "american", "british"], ALL),
        ("Albert Bierstadt", ["america", "american"], ALL),
        ("Frederic Edwin Church", ["america", "american"], ALL),
        ("Thomas Cole", ["america", "american"], ALL),
        ("Childe Hassam", ["america", "american"], ALL),
        ("William Merritt Chase", ["america", "american"], ALL),
        ("George Bellows", ["america", "american"], ALL),
        ("Hans Hofmann", ["america", "american", "german"], ALL),
        ("Salvador Dalí", ["spain", "spanish", "france"], ALL),
        ("Joan Miró", ["spain", "spanish", "france"], ALL),
        ("René Magritte", ["belgium", "belgian"], ALL),
        ("Marcel Duchamp", ["france", "french", "america"], ALL),
        ("Constantin Brancusi", ["romania", "france", "french"], ALL),
        ("Alexander Calder", ["america", "american", "france"], ALL),
        ("Henry Moore", ["england", "british"], ALL),
        ("Barbara Hepworth", ["england", "british"], ALL),
        ("Édouard Manet drawing", ["france", "french"], ALL),
        ("Paul Cézanne watercolor", ["france", "french"], ALL),
        ("Lautrec poster", ["france", "french"], ALL),
        ("Mucha", ["austria", "czech", "france"], ALL),
        ("Lalique", ["france", "french"], ALL),
        ("Émile Gallé", ["france", "french"], ALL),
        ("Daum", ["france", "french"], ALL),
        ("Royal Doulton", ["england", "british"], ALL),
        ("Adam Elsheimer", ["germany", "german"], ALL),
        ("Aelbert Cuyp", ["netherlands", "dutch"], ALL),
        ("Jan Steen", ["netherlands", "dutch"], ALL),
        ("Adriaen van de Velde", ["netherlands", "dutch"], ALL),
        ("Willem Kalf", ["netherlands", "dutch"], ALL),
        ("Pieter de Hooch", ["netherlands", "dutch"], ALL),
        ("Salomon van Ruysdael", ["netherlands", "dutch"], ALL),
        ("Hendrick Avercamp", ["netherlands", "dutch"], ALL),
        ("Ambrosius Bosschaert", ["netherlands", "dutch"], ALL),
        ("Rachel Ruysch", ["netherlands", "dutch"], ALL),
        ("Cornelis Cort", ["netherlands", "dutch"], ALL),
        ("Lucas van Leyden", ["netherlands", "dutch"], ALL),
        ("Jan Brueghel", ["flemish", "belgium", "netherlands"], ALL),
        ("Jan van Eyck", ["flemish", "belgium", "netherlands"], ALL),
        ("Rogier van der Weyden", ["flemish", "belgium", "netherlands"], ALL),
        ("Hans Memling", ["flemish", "belgium", "netherlands"], ALL),
        ("Hugo van der Goes", ["flemish", "belgium", "netherlands"], ALL),
        ("Robert Campin", ["flemish", "belgium", "netherlands"], ALL),
        ("Quentin Massys", ["flemish", "belgium", "netherlands"], ALL),
    ],
}


def culture_match(c, needles):
    if not needles:
        return True
    c = c or ""
    return any(n in c for n in needles)


def run_region(region, queries, limit_per_query, sleep_between, force_sources=None):
    path = DATA / f"{region}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    existing_titles = {w["title"].lower() for w in data["works"]}
    existing_images = {w["image"] for w in data["works"]}
    starting_count = len(data["works"])

    added = 0
    filtered_by_culture = 0
    skipped_dupes = 0

    for q, needles, sources in queries:
        if force_sources:
            sources = force_sources
        hits: list[dict] = []
        if "cma" in sources:
            hits += cma_search(q, limit_per_query)
        if "aic" in sources:
            hits += aic_search(q, limit_per_query)
        if "vam" in sources:
            hits += vam_search(q, limit_per_query)
        if "met" in sources:
            hits += met_search(q, limit_per_query)

        for h in hits:
            cult = h.pop("_culture", "")
            if not culture_match(cult, needles):
                filtered_by_culture += 1
                continue
            t_lc = h["title"].lower()
            if t_lc in existing_titles:
                skipped_dupes += 1
                continue
            if h["image"] in existing_images:
                skipped_dupes += 1
                continue
            data["works"].append(h)
            existing_titles.add(t_lc)
            existing_images.add(h["image"])
            added += 1

        if sleep_between:
            time.sleep(sleep_between)

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"  {region}: +{added} (was {starting_count}, now {starting_count + added})"
          f"   [filtered {filtered_by_culture}, dupes {skipped_dupes}]")
    return added


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("regions", nargs="*")
    ap.add_argument("--limit", type=int, default=20, help="per-query per-source limit")
    ap.add_argument("--sleep", type=float, default=0.0, help="sleep between queries")
    ap.add_argument("--source", choices=["cma", "aic", "vam", "met", "all"], default=None,
                    help="Override sources per query. 'met' runs Met only.")
    args = ap.parse_args()

    force_sources = None
    if args.source and args.source != "all":
        force_sources = (args.source,)

    regions = args.regions or list(PLAN.keys())
    total = 0
    for region in regions:
        if region not in PLAN:
            print(f"  no plan for {region!r}", file=sys.stderr)
            continue
        total += run_region(region, PLAN[region], args.limit, args.sleep, force_sources)
    print(f"\nAdded {total} works total.")


if __name__ == "__main__":
    main()
