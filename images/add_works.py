#!/usr/bin/env python3
"""Append a curated batch of new works to data/*.json.

Safe to rerun: skips entries whose title already exists in the target region.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"

NEW_WORKS: dict[str, list[dict]] = {
    "africa": [
        {
            "title": "Adinkra Symbols",
            "meta": "Akan / Asante · 18th c. onward · Ghana",
            "desc": "A system of visual proverbs stamped or woven into cloth — each glyph carrying a name and an aphorism. Worn at funerals; later embraced globally as a Pan-African vocabulary.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Gyaman_Adinkra_Symbols.jpg/960px-Gyaman_Adinkra_Symbols.jpg",
            "year": 1750,
        },
    ],
    "egypt-nubia": [
        {
            "title": "Bent Pyramid",
            "meta": "Old Kingdom · Sneferu · c. 2600 BCE · Dahshur",
            "desc": "Sneferu's second pyramid — the angle changes partway up, either to prevent collapse or because ambition had to meet physics. A crucial step between stepped and smooth pyramids.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/Bent_Pyramid_%E6%9B%B2%E6%8A%98%E9%87%91%E5%AD%97%E5%A1%94_-_panoramio.jpg/960px-Bent_Pyramid_%E6%9B%B2%E6%8A%98%E9%87%91%E5%AD%97%E5%A1%94_-_panoramio.jpg",
            "year": -2600,
        },
    ],
    "mesopotamia-persia": [
        {
            "title": "Lyres of Ur",
            "meta": "Sumerian · c. 2500 BCE · Royal Cemetery",
            "desc": "Wooden lyres covered in gold and lapis, the sound boxes shaped into bulls' heads. Found in Queen Puabi's grave next to the women who played them. The oldest stringed instruments we have.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/The_Queen%27s_gold_lyre_from_the_Royal_Cemetery_at_Ur._C._2500_BCE._Iraq_Museum.jpg/960px-The_Queen%27s_gold_lyre_from_the_Royal_Cemetery_at_Ur._C._2500_BCE._Iraq_Museum.jpg",
            "year": -2500,
        },
        {
            "title": "Assyrian Winged Genii",
            "meta": "Neo-Assyrian · c. 870 BCE · Nimrud",
            "desc": "Four-winged protective spirits carved in alabaster lining Ashurnasirpal II's palace. They lift a pine cone and a bucket — a gesture of ritual purification never fully decoded.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Genien%2C_Nimrud_870_v._Chr._Aegyptisches_Museum%2C_Muenchen-4.jpg/960px-Genien%2C_Nimrud_870_v._Chr._Aegyptisches_Museum%2C_Muenchen-4.jpg",
            "year": -870,
        },
    ],
    "mediterranean": [
        {
            "title": "New York Kouros",
            "meta": "Archaic Greek · c. 590 BCE",
            "desc": "One of the earliest freestanding Greek marble nudes, Attic. Still stiff with Egyptian influence — striding left foot, clenched fists — but the archaic smile has arrived.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Marble_statue_of_a_kouros_%28youth%29_MET_DT263.jpg/960px-Marble_statue_of_a_kouros_%28youth%29_MET_DT263.jpg",
            "year": -590,
        },
        {
            "title": "Moschophoros (Calf Bearer)",
            "meta": "Archaic Greek · c. 560 BCE · Acropolis",
            "desc": "A man carries a calf to sacrifice; both smile — the archaic grin. His tunic is incised rather than carved, an early convention already on its way out.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/ACMA_Moschophoros.jpg/960px-ACMA_Moschophoros.jpg",
            "year": -560,
        },
        {
            "title": "Ludovisi Throne",
            "meta": "Greek · c. 470 BCE",
            "desc": "A marble three-sided relief of uncertain function (a throne? an altar?). On its main panel, Aphrodite rising from the sea, draped in a wet gown that might as well not be there.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/Ludovisi_throne_Altemps_Inv8570_n4.jpg/960px-Ludovisi_throne_Altemps_Inv8570_n4.jpg",
            "year": -470,
        },
        {
            "title": "Apollo Belvedere",
            "meta": "Hellenistic / Roman copy · c. 120–140 CE",
            "desc": "A marble copy of a lost Greek bronze, long considered the pinnacle of male beauty. Winckelmann helped launch Neoclassicism by writing about this single statue.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/Apollo_del_Belvedere.jpg/960px-Apollo_del_Belvedere.jpg",
            "year": 130,
        },
    ],
    "europe": [
        {
            "title": "The Death of Marat",
            "meta": "French Neoclassicism · 1793",
            "desc": "Marat in his bathtub, stabbed by Charlotte Corday, pen still in hand. David painted him as a secular martyr — a revolutionary Pietà for a Republic that had killed its king.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/aa/Death_of_Marat_by_David.jpg/960px-Death_of_Marat_by_David.jpg",
            "artist": "Jacques-Louis David",
            "year": 1793,
        },
        {
            "title": "Les Demoiselles d'Avignon",
            "meta": "Proto-Cubism · 1907",
            "desc": "Five Barcelona prostitutes, faces half-African mask, bodies fractured into angular planes. Picasso hid it for years; when it emerged it had already ended the 19th century.",
            "image": "https://upload.wikimedia.org/wikipedia/en/thumb/4/4c/Les_Demoiselles_d%27Avignon.jpg/960px-Les_Demoiselles_d%27Avignon.jpg",
            "artist": "Pablo Picasso",
            "year": 1907,
        },
        {
            "title": "Cologne Cathedral",
            "meta": "High Gothic · 1248–1880 · Germany",
            "desc": "Started in 1248, stopped in 1473, resumed in 1842, finished with the original medieval drawings in hand. For four years after completion it was the tallest building on earth.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/K%C3%B6lner_Dom_-_Westfassade_2022_ohne_Ger%C3%BCst-0968_b.jpg/960px-K%C3%B6lner_Dom_-_Westfassade_2022_ohne_Ger%C3%BCst-0968_b.jpg",
            "year": 1250,
        },
        {
            "title": "Florence Cathedral (Duomo)",
            "meta": "Italian Gothic / Renaissance · 1296–1436",
            "desc": "Brunelleschi's dome, still the largest brick dome ever built. He designed it without drawings, built it without scaffolding, and took the method with him to the grave.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Cattedrale_di_Santa_Maria_del_Fiore_%E2%80%93_Il_Duomo_di_Firenze.jpg/960px-Cattedrale_di_Santa_Maria_del_Fiore_%E2%80%93_Il_Duomo_di_Firenze.jpg",
            "year": 1300,
        },
    ],
    "islamic-world": [
        {
            "title": "Al-Aqsa Mosque",
            "meta": "Umayyad onward · 705 CE · Jerusalem",
            "desc": "The congregational mosque on the Temple Mount, third holiest site in Islam. Rebuilt repeatedly after earthquakes; the wooden prayer hall facing the qibla dates partly to the 1930s.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Jerusalem-2013-Temple_Mount-Al-Aqsa_Mosque_%28NE_exposure%29.jpg/960px-Jerusalem-2013-Temple_Mount-Al-Aqsa_Mosque_%28NE_exposure%29.jpg",
            "year": 705,
        },
        {
            "title": "Bou Inania Madrasa",
            "meta": "Marinid · 1350–1355 · Fez",
            "desc": "A teaching mosque of carved cedar, zellige tile, and stucco so fine it looks punched through paper. The Marinid sultan reportedly said the building cost was so beautiful it didn't matter what it cost.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/Bou_Inania_Madrasa_2011.jpg/960px-Bou_Inania_Madrasa_2011.jpg",
            "year": 1350,
        },
        {
            "title": "Tomb of Jahangir",
            "meta": "Mughal · 1637 · Lahore",
            "desc": "Jahangir — Akbar's son, Shah Jahan's father — lies under white marble inlaid with pietra dura flowers, in a garden tomb of red sandstone. The minarets at the corners rise but never touch the roof.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Tomb_of_Emperor_Jahangir.jpg/960px-Tomb_of_Emperor_Jahangir.jpg",
            "year": 1637,
        },
    ],
    "south-asia": [
        {
            "title": "Bhaja Caves",
            "meta": "Early Buddhist · 2nd c. BCE · Maharashtra",
            "desc": "Twenty-two rock-cut viharas and a chaitya, with wooden ribs imitated in stone. Reliefs show figures riding elephants, dancing — a rare look at secular imagery in early Buddhist art.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/0/08/The_Bhaje_Caves_05.jpg",
            "year": -150,
        },
        {
            "title": "Jagannath Temple, Puri",
            "meta": "Eastern Ganga · 12th c. · Odisha",
            "desc": "Home of the annual Rath Yatra — giant wooden chariots hauled through the streets carrying the three deities. The temple's cooks feed the god daily from one of the largest kitchens in the world.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Shri_Jagannath_temple.jpg/960px-Shri_Jagannath_temple.jpg",
            "year": 1150,
        },
        {
            "title": "Lepakshi Temple",
            "meta": "Vijayanagara · 16th c. · Andhra Pradesh",
            "desc": "A granite temple to Shiva whose ceiling holds the largest surviving Vijayanagara mural. One of its columns hangs a fraction of an inch above the floor — pilgrims pass cloth beneath it.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Front_side_of_Veerabhadra_Temple%2C_Lepakshi.jpg/960px-Front_side_of_Veerabhadra_Temple%2C_Lepakshi.jpg",
            "year": 1540,
        },
        {
            "title": "Thanjavur Painting",
            "meta": "Nayaka / Maratha · 16th–19th c. · Tamil Nadu",
            "desc": "Devotional paintings built up in gesso, then layered in gold leaf, semi-precious stones, and mirrored glass. Surface so encrusted the figures seem to float off the board.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/Thanjavur_art_from_south_India.jpg/960px-Thanjavur_art_from_south_India.jpg",
            "year": 1700,
        },
    ],
    "east-asia": [
        {
            "title": "Leshan Giant Buddha",
            "meta": "Tang China · 713–803 · Sichuan",
            "desc": "A seated Maitreya carved directly into a sandstone cliff at the confluence of three rivers. Seventy-one meters tall; his ears alone are seven meters. Built, a monk said, to calm the waters.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/36275-Leshan_%2849067653383%29.jpg/960px-36275-Leshan_%2849067653383%29.jpg",
            "year": 713,
        },
        {
            "title": "Bulguksa",
            "meta": "Unified Silla · 751 CE · Gyeongju, Korea",
            "desc": "A Buddhist temple with twin pagodas (Dabotap and Seokgatap) that encode two sutras in stone form. Burned by the Japanese in 1593, rebuilt in the 1970s on the original foundations.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Lotus_Flower_Bridge_and_Seven_Treasure_Bridge_at_Bulguksa_in_Gyeongju%2C_Korea.jpg/960px-Lotus_Flower_Bridge_and_Seven_Treasure_Bridge_at_Bulguksa_in_Gyeongju%2C_Korea.jpg",
            "year": 751,
        },
        {
            "title": "Lantingji Xu (Preface to the Orchid Pavilion)",
            "meta": "Eastern Jin · Wang Xizhi · 353 CE · China",
            "desc": "A drunkenly perfect calligraphic masterpiece, 324 characters describing a riverside gathering of poets. Wang Xizhi tried to rewrite it next day and could not match it. Later buried with an emperor.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/1/1e/XingshuLantingxv.jpg",
            "artist": "Wang Xizhi",
            "year": 353,
        },
        {
            "title": "Dream of the Red Chamber",
            "meta": "Qing China · Cao Xueqin · 18th c.",
            "desc": "A classic Chinese novel in 120 chapters, commonly illustrated from Qing to today — the Jia family's decline rendered in garden pavilions, dying flowers, a jade inscribed with fate.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/7/79/Hongloumeng2.jpg",
            "artist": "Cao Xueqin",
            "year": 1760,
        },
    ],
    "southeast-asia-oceania": [
        {
            "title": "Mentawai Body Tattoo",
            "meta": "Mentawai people · millennia · Indonesia",
            "desc": "A Mentawai sikerei (shaman) in full body tattoo. Designs carry rank and history; the practice is said to be one of the oldest continuous tattoo traditions on earth.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Sikerei_Dukun_Mentawai.jpg/960px-Sikerei_Dukun_Mentawai.jpg",
            "year": 1900,
        },
    ],
    "americas": [
        {
            "title": "Hopi Katsina Doll",
            "meta": "Hopi · 19th c. onward · American Southwest",
            "desc": "Carved cottonwood figures given to Hopi children to teach them the 400+ spirit beings of the Katsinam. Collectors later prized them so much the carving style changed to please buyers.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/2/27/Palahiko_Mana_Water-Drinking_Maiden_1899_Hopi.jpg",
            "year": 1899,
        },
        {
            "title": "Zuni Fetishes",
            "meta": "A:shiwi (Zuni) · traditional · New Mexico",
            "desc": "Small stone carvings of animals — bear, eagle, mountain lion — each holding a spirit and often wrapped with an offering bundle of turquoise or shell.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/DVRededicationMay222016_0355_%2829286303406%29.jpg/960px-DVRededicationMay222016_0355_%2829286303406%29.jpg",
            "year": 1900,
        },
        {
            "title": "Inuit Art",
            "meta": "Inuit · 20th c. contemporary · Arctic",
            "desc": "Carved soapstone, serpentine, and whalebone figures of hunters, spirits, and animals. A tradition fused out of older ivory carving and 20th-century print cooperatives like Cape Dorset.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/PaQi_2.jpg/960px-PaQi_2.jpg",
            "year": 1960,
        },
        {
            "title": "Haida Argillite Carving",
            "meta": "Haida · 19th c. onward · Haida Gwaii",
            "desc": "Black shale carvings only the Haida may quarry, developed as a trade art for European sailors. Ship figureheads, pipes, and eventually complex narrative panels.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/e/e2/Haida_argillite_carving_BC_1850_nmai13-1875.jpg",
            "year": 1850,
        },
    ],
}


def main() -> None:
    added_total = 0
    for slug, new_works in NEW_WORKS.items():
        path = DATA / f"{slug}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        existing = {w["title"] for w in data["works"]}
        added = 0
        for w in new_works:
            if w["title"] in existing:
                print(f"  skip (already present): {slug} / {w['title']}")
                continue
            data["works"].append(w)
            added += 1
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"  {slug}: +{added} (now {len(data['works'])})")
        added_total += added
    print(f"\nAdded {added_total} works. Run `python build.py` to regenerate HTML.")


if __name__ == "__main__":
    main()
