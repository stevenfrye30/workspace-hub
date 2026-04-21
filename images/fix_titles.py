#!/usr/bin/env python3
"""Prefix generic titles with culture/artist info so they read better without
descriptions. Edits data/<region>.json in place.

Example transforms:
    "Bowl"                  -> "Moche Bowl"
    "Portrait of a Woman"   -> "Rembrandt: Portrait of a Woman"
    "Figure" (Luba)         -> "Luba Figure"
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"

SINGLE_WORD_GENERIC = {
    "Bowl", "Jar", "Vase", "Vessel", "Figurine", "Figure", "Fragment", "Carving",
    "Ornament", "Ring", "Earring", "Pendant", "Staff", "Bead", "Mask", "Head",
    "Cup", "Plate", "Dish", "Headdress", "Stool", "Lintel", "Panel", "Textile",
    "Hat", "Basket", "Drawing", "Print", "Bust", "Portrait", "Coin", "Medal",
    "Sculpture", "Tile", "Tunic", "Jug", "Pitcher", "Pot", "Box", "Spoon",
    "Doll", "Hanging", "Carving", "Weaving",
}

COMPOUND_GENERIC = {
    "Male Figure", "Female Figure", "Standing Figure", "Seated Figure",
    "Portrait of a Woman", "Portrait of a Man", "Portrait of a Lady",
    "Portrait of a Gentleman", "Portrait of a Young Woman", "Portrait of a Young Man",
    "Bust of a Man", "Bust of a Woman", "Bust of a Lady",
    "Self-Portrait", "Still Life", "Landscape",
    "Head of a Man", "Head of a Woman",
}

# First look for these as substrings in the meta (case-insensitive) — gives an
# ethnic / cultural adjective to prepend. Ordered by specificity.
CULTURE_MAP = [
    ("moche", "Moche"), ("nasca", "Nasca"), ("nazca", "Nasca"),
    ("wari", "Wari"), ("huari", "Wari"), ("chancay", "Chancay"),
    ("chimú", "Chimú"), ("chimu", "Chimú"), ("inca", "Inca"),
    ("olmec", "Olmec"), ("teotihuacan", "Teotihuacan"),
    ("aztec", "Aztec"), ("mixtec", "Mixtec"), ("zapotec", "Zapotec"),
    ("maya", "Maya"), ("veracruz", "Veracruz"), ("paracas", "Paracas"),
    ("chavin", "Chavín"), ("cupisnique", "Cupisnique"),
    ("calima", "Calima"), ("sinú", "Sinú"), ("zenú", "Sinú"),
    ("quimbaya", "Quimbaya"), ("tairona", "Tairona"), ("muisca", "Muisca"),
    ("tlaltecuhtli", "Aztec"),
    ("coclé", "Coclé"), ("diquís", "Diquís"),
    ("navajo", "Navajo"), ("hopi", "Hopi"), ("zuni", "Zuni"),
    ("tlingit", "Tlingit"), ("haida", "Haida"), ("kwakwaka", "Kwakwaka'wakw"),
    ("mimbres", "Mimbres"), ("talavera", "Talavera"),
    ("yoruba", "Yoruba"), ("benin", "Benin"), ("igbo", "Igbo"),
    ("kongo", "Kongo"), ("kuba", "Kuba"), ("luba", "Luba"), ("songye", "Songye"),
    ("chokwe", "Chokwe"), ("fang", "Fang"), ("senufo", "Senufo"),
    ("dogon", "Dogon"), ("bamana", "Bamana"), ("bambara", "Bamana"),
    ("akan", "Akan"), ("asante", "Asante"), ("ashanti", "Asante"),
    ("fon", "Fon"), ("bamileke", "Bamileke"), ("bamum", "Bamum"),
    ("mangbetu", "Mangbetu"), ("lega", "Lega"), ("pende", "Pende"),
    ("yaka", "Yaka"), ("teke", "Teke"), ("baga", "Baga"), ("baule", "Baule"),
    ("mossi", "Mossi"), ("lobi", "Lobi"), ("dan ", "Dan"),
    ("mende", "Mende"), ("sapi", "Sapi"), ("punu", "Punu"),
    ("kota", "Kota"), ("hemba", "Hemba"), ("tabwa", "Tabwa"), ("mbole", "Mbole"),
    ("kwele", "Kwele"), ("mumuye", "Mumuye"), ("jukun", "Jukun"),
    ("ethiopia", "Ethiopian"), ("zulu", "Zulu"), ("ndebele", "Ndebele"),
    ("shona", "Shona"), ("tuareg", "Tuareg"), ("makonde", "Makonde"),
    ("malagasy", "Malagasy"),
    ("sasanian", "Sasanian"), ("parthian", "Parthian"),
    ("achaemenid", "Achaemenid"), ("hittite", "Hittite"),
    ("luristan", "Luristan"), ("urart", "Urartian"),
    ("assyrian", "Assyrian"), ("babylonian", "Babylonian"),
    ("sumerian", "Sumerian"), ("akkadian", "Akkadian"),
    ("elamite", "Elamite"), ("mesopotam", "Mesopotamian"),
    ("palmyra", "Palmyrene"), ("scyth", "Scythian"),
    ("phoenician", "Phoenician"),
    ("etruscan", "Etruscan"), ("roman", "Roman"),
    ("minoan", "Minoan"), ("mycenaean", "Mycenaean"),
    ("cycladic", "Cycladic"), ("corinthian", "Corinthian"),
    ("attic", "Attic Greek"), ("apulian", "Apulian"),
    ("lucanian", "Lucanian"), ("thracian", "Thracian"),
    ("greek", "Greek"),
    ("byzantine", "Byzantine"), ("coptic", "Coptic"),
    ("predynastic", "Predynastic Egyptian"),
    ("old kingdom", "Old Kingdom Egyptian"),
    ("middle kingdom", "Middle Kingdom Egyptian"),
    ("new kingdom", "New Kingdom Egyptian"),
    ("late period", "Late Period Egyptian"),
    ("ptolemaic", "Ptolemaic Egyptian"),
    ("amarna", "Amarna Egyptian"),
    ("nubia", "Nubian"), ("kush", "Kushite"), ("meroe", "Meroitic"),
    ("egypt", "Egyptian"),
    ("iznik", "Iznik"), ("ottoman", "Ottoman"),
    ("safavid", "Safavid"), ("mamluk", "Mamluk"),
    ("mughal", "Mughal"), ("fatimid", "Fatimid"),
    ("kashan", "Kashan"), ("qajar", "Qajar"),
    ("timurid", "Timurid"), ("seljuk", "Seljuk"),
    ("ilkhan", "Ilkhanid"), ("nasrid", "Nasrid"),
    ("abbasid", "Abbasid"), ("umayyad", "Umayyad"),
    ("iran", "Persian"), ("persia", "Persian"),
    ("deccan", "Deccani"),
    ("chola", "Chola"), ("gandhara", "Gandharan"),
    ("gupta", "Gupta"), ("kushan", "Kushan"),
    ("maurya", "Mauryan"), ("pala", "Pala"),
    ("hoysala", "Hoysala"), ("pallava", "Pallava"),
    ("rajput", "Rajput"), ("pahari", "Pahari"),
    ("kangra", "Kangra"), ("basohli", "Basohli"),
    ("jaipur", "Jaipur"), ("bundi", "Bundi"),
    ("kashmir", "Kashmiri"), ("sri lanka", "Sri Lankan"),
    ("tibet", "Tibetan"), ("nepal", "Nepali"),
    ("khmer", "Khmer"), ("cambodia", "Khmer"),
    ("java", "Javanese"), ("sumatra", "Sumatran"),
    ("bali", "Balinese"), ("vietnam", "Vietnamese"),
    ("cham", "Cham"), ("thailand", "Thai"),
    ("sukhothai", "Sukhothai"), ("ayutthaya", "Ayutthaya"),
    ("dvaravati", "Dvaravati"), ("lanna", "Lanna"),
    ("laos", "Lao"), ("burma", "Burmese"), ("myanmar", "Burmese"),
    ("pagan", "Pagan Burmese"),
    ("philippines", "Philippine"), ("mindanao", "Mandaya"),
    ("papua", "Papuan"), ("sepik", "Sepik"), ("asmat", "Asmat"),
    ("solomon", "Solomon Islands"), ("fiji", "Fijian"),
    ("maori", "Māori"), ("hawaii", "Hawaiian"),
    ("marquesas", "Marquesan"), ("tonga", "Tongan"), ("samoa", "Samoan"),
    ("rapa nui", "Rapa Nui"), ("polynesia", "Polynesian"),
    ("aboriginal", "Aboriginal"),
    ("china, ming", "Ming Chinese"), ("ming dynasty", "Ming Chinese"),
    ("china, qing", "Qing Chinese"), ("qing dynasty", "Qing Chinese"),
    ("china, song", "Song Chinese"), ("song dynasty", "Song Chinese"),
    ("china, tang", "Tang Chinese"), ("tang dynasty", "Tang Chinese"),
    ("china, han", "Han Chinese"), ("han dynasty", "Han Chinese"),
    ("china, zhou", "Zhou Chinese"),
    ("china, shang", "Shang Chinese"),
    ("china, yuan", "Yuan Chinese"),
    ("china, jin", "Jin Chinese"),
    ("jingdezhen", "Jingdezhen"), ("longquan", "Longquan"),
    ("jizhou", "Jizhou"), ("cizhou", "Cizhou"),
    ("china", "Chinese"),
    ("japan", "Japanese"), ("edo", "Edo Japanese"),
    ("meiji", "Meiji Japanese"), ("heian", "Heian Japanese"),
    ("kamakura", "Kamakura Japanese"),
    ("korea", "Korean"), ("joseon", "Joseon"), ("goryeo", "Goryeo"),
    ("koryo", "Goryeo"), ("silla", "Silla"), ("baekje", "Baekje"),
    ("netherlands", "Dutch"), ("dutch", "Dutch"),
    ("belgium", "Belgian"), ("flemish", "Flemish"),
    ("germany", "German"), ("german", "German"),
    ("france", "French"), ("french", "French"),
    ("italy", "Italian"), ("italian", "Italian"),
    ("venice", "Venetian"), ("florence", "Florentine"),
    ("spain", "Spanish"), ("spanish", "Spanish"),
    ("portugal", "Portuguese"), ("austria", "Austrian"),
    ("vienna", "Viennese"), ("switzerland", "Swiss"),
    ("england", "English"), ("britain", "British"), ("british", "British"),
    ("scotland", "Scottish"), ("ireland", "Irish"),
    ("russia", "Russian"), ("poland", "Polish"),
    ("czech", "Czech"), ("hungary", "Hungarian"),
    ("norway", "Norwegian"), ("denmark", "Danish"),
    ("sweden", "Swedish"), ("finland", "Finnish"),
    ("america", "American"), ("united states", "American"),
    ("mexico", "Mexican"), ("brazil", "Brazilian"),
    ("colonial peru", "Colonial Peruvian"),
    ("morocco", "Moroccan"), ("tunisia", "Tunisian"),
]


def find_culture(meta: str) -> str:
    m = meta.lower()
    for needle, adj in CULTURE_MAP:
        if needle in m:
            return adj
    return ""


def fix_title(title: str, meta: str, artist: str) -> str:
    t = title.strip()
    if t in SINGLE_WORD_GENERIC:
        prefix = find_culture(meta) or (artist.split()[-1] if artist else "")
        if prefix:
            return f"{prefix} {t}"
    elif t in COMPOUND_GENERIC:
        if artist:
            surname = artist.split()[-1].rstrip(",")
            return f"{surname}: {t}"
        prefix = find_culture(meta)
        if prefix:
            return f"{prefix} {t}"
    return title


def main():
    changed = 0
    for path in sorted(DATA.glob("*.json")):
        if path.name == "regions.json":
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        local_changed = 0
        seen_titles = {w["title"] for w in data["works"]}
        for w in data["works"]:
            new_title = fix_title(w["title"], w.get("meta", ""), w.get("artist", ""))
            if new_title == w["title"]:
                continue
            # Avoid introducing dupes — keep original if new title already exists.
            if new_title in seen_titles:
                # Append disambiguator if collision
                idx = 2
                probe = f"{new_title} ({idx})"
                while probe in seen_titles:
                    idx += 1
                    probe = f"{new_title} ({idx})"
                new_title = probe
            seen_titles.discard(w["title"])
            seen_titles.add(new_title)
            w["title"] = new_title
            local_changed += 1
        if local_changed:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8")
        print(f"  {path.stem}: {local_changed} titles fixed")
        changed += local_changed
    print(f"\nTotal titles fixed: {changed}")


if __name__ == "__main__":
    main()
