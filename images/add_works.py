#!/usr/bin/env python3
"""Append a curated batch of new works to data/*.json.

Replace NEW_WORKS with your batch and run. Optional 'artist' field seeds the
artist view — omit for anonymous / collective / architectural works.

Safe to rerun: skips entries whose title already exists in the target region.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"

NEW_WORKS: dict[str, list[dict]] = {
    "egypt-nubia": [
        {
            "title": "Dendera Zodiac",
            "meta": "Ptolemaic · c. 50 BCE",
            "desc": "A circular sandstone relief of the night sky carried off from the ceiling of Dendera temple by a French explorer in 1821. Now in the Louvre; a replica hangs in the original.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/Zodiaque_de_Dend%C3%A9ra_-_Mus%C3%A9e_du_Louvre_Antiquit%C3%A9s_Egyptiennes_D_38_%3B_E_13482.jpg/960px-Zodiaque_de_Dend%C3%A9ra_-_Mus%C3%A9e_du_Louvre_Antiquit%C3%A9s_Egyptiennes_D_38_%3B_E_13482.jpg",
        },
        {
            "title": "Prisse Papyrus",
            "meta": "Middle Kingdom · c. 1900 BCE",
            "desc": "The oldest literary book in existence. Two teachings of wisdom — \"the Instructions of Kagemni\" and \"of Ptahhotep\" — carefully written in cursive hieroglyphs.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Papyrus_Prisse_part_I._Kagemni-bibliotekNF.tif/lossy-page1-960px-Papyrus_Prisse_part_I._Kagemni-bibliotekNF.tif.jpg",
        },
    ],
    "mesopotamia-persia": [
        {
            "title": "Royal Cemetery of Ur",
            "meta": "Sumerian · c. 2600 BCE · Iraq",
            "desc": "Sixteen royal graves, each with servants, soldiers, and musicians sacrificed and buried beside the king. Out came the Standard of Ur, Queen Puabi's headdress, and the Ram in the Thicket.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Royal_Cemetery_of_Ur_excavations_%28B%26W%29.jpg/960px-Royal_Cemetery_of_Ur_excavations_%28B%26W%29.jpg",
        },
        {
            "title": "Yazılıkaya",
            "meta": "Hittite · 13th c. BCE · Turkey",
            "desc": "An open-air rock sanctuary near Hattusa. Sixty-six gods and goddesses walk in procession along the cliff face — the full Hittite pantheon gathered in stone.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/58/Yazilikaya_Kammer_A.jpg/960px-Yazilikaya_Kammer_A.jpg",
        },
    ],
    "mediterranean": [
        {
            "title": "Parthenon Frieze",
            "meta": "Classical Greek · Pheidias workshop · c. 440 BCE",
            "desc": "A continuous band 160 meters long, showing the Panathenaic procession — horses, musicians, elders, gods receiving the city's tribute. Half survives in the British Museum, half in Athens.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Cavalcade_west_frieze_Parthenon_BM.jpg/960px-Cavalcade_west_frieze_Parthenon_BM.jpg",
        },
        {
            "title": "Herculaneum",
            "meta": "Roman · buried 79 CE · Italy",
            "desc": "Pompeii's smaller, richer neighbor. Volcanic mud sealed it instead of ash, so wooden beams, baby cradles, and carbonized scrolls all survived.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Antigua_ciudad_de_Herculano%2C_Italia%2C_2023-03-27%2C_DD_135-138_PAN.jpg/960px-Antigua_ciudad_de_Herculano%2C_Italia%2C_2023-03-27%2C_DD_135-138_PAN.jpg",
        },
    ],
    "europe": [
        {
            "title": "Sunflowers",
            "meta": "Post-Impressionism · 1888",
            "desc": "Painted in Arles to decorate Gauguin's guest bedroom. Van Gogh made seven versions; in letters, he called them an ode to gratitude.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Vincent_Willem_van_Gogh_127.jpg/960px-Vincent_Willem_van_Gogh_127.jpg",
            "artist": "Vincent van Gogh",
        },
        {
            "title": "View of Delft",
            "meta": "Dutch Golden Age · c. 1660–1661",
            "desc": "Vermeer's hometown across the water, clouds moving overhead. Proust called it \"the most beautiful painting in the world\" and had one of his characters die looking at it.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Vermeer-view-of-delft.jpg/960px-Vermeer-view-of-delft.jpg",
            "artist": "Johannes Vermeer",
        },
        {
            "title": "The Treachery of Images",
            "meta": "Surrealism · 1929",
            "desc": "A pipe painted with the words \"Ceci n'est pas une pipe\" (This is not a pipe). It isn't — it's a painting of one. Magritte's founding joke of Surrealism.",
            "image": "https://upload.wikimedia.org/wikipedia/en/b/b9/MagrittePipe.jpg",
            "artist": "René Magritte",
        },
    ],
    "islamic-world": [
        {
            "title": "Bibi-Khanym Mosque",
            "meta": "Timurid · 1399–1404 · Samarkand",
            "desc": "Timur commissioned it after sacking Delhi — the largest mosque in the Islamic world at the time. The main dome collapsed within decades; centuries later the Soviets rebuilt it.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/%D0%9C%D0%B5%D1%87%D0%B5%D1%82%D1%8C_%D0%91%D0%B8%D0%B1%D0%B8_%D0%A5%D0%B0%D0%BD%D1%83%D0%BC._%D0%A1%D0%B0%D0%BC%D0%B0%D1%80%D0%BA%D0%B0%D0%BD%D0%B4.jpg/960px-%D0%9C%D0%B5%D1%87%D0%B5%D1%82%D1%8C_%D0%91%D0%B8%D0%B1%D0%B8_%D0%A5%D0%B0%D0%BD%D1%83%D0%BC._%D0%A1%D0%B0%D0%BC%D0%B0%D1%80%D0%BA%D0%B0%D0%BD%D0%B4.jpg",
        },
        {
            "title": "Great Mosque of Herat",
            "meta": "Ghurid onward · 12th c. · Afghanistan",
            "desc": "The Friday Mosque of Herat, its courtyard walls tiled in a dense cobalt and turquoise mosaic. Its tile workshops still operate beside the mosque, rebuilding what time erodes.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/b/bd/Friday_Mosque_in_Herat%2C_Afghanistan.jpg",
        },
        {
            "title": "Khamsa of Nizami",
            "meta": "Persian · 12th c. poem, illuminated 14th c. onward",
            "desc": "Five epic romances — Khosrow and Shirin, Layla and Majnun, and others — illustrated by every Persian royal workshop for centuries. The British Library copy alone has 30 miniatures.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Khusraw_arriving_at_Shirin%27s_castle_%28f.80%29._Khamsa_of_Nizami%2C_Jalayirid_style%2C_1386-88%2C_Baghdad_%28British_Library%2C_Or.13297%29.jpg/960px-Khusraw_arriving_at_Shirin%27s_castle_%28f.80%29._Khamsa_of_Nizami%2C_Jalayirid_style%2C_1386-88%2C_Baghdad_%28British_Library%2C_Or.13297%29.jpg",
        },
    ],
    "south-asia": [
        {
            "title": "Mahabodhi Temple",
            "meta": "Gupta → restored 19th c. · Bodh Gaya",
            "desc": "Built at the spot the Buddha attained enlightenment under a Bodhi tree. A direct descendant of that tree still grows beside the temple.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Mahabodhitemple.jpg/960px-Mahabodhitemple.jpg",
        },
        {
            "title": "Akbar's Tomb",
            "meta": "Mughal · 1605–1613 · Sikandra, Agra",
            "desc": "A five-story mausoleum on a platform in a paradise garden. Akbar designed much of it himself; Jahangir's later changes produced the strange tiered result.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Akbar%27s_Tomb_in_Sikandra_15.jpg/960px-Akbar%27s_Tomb_in_Sikandra_15.jpg",
        },
    ],
    "east-asia": [
        {
            "title": "Fine Wind, Clear Morning (Red Fuji)",
            "meta": "Edo Japan · Hokusai · c. 1830–1832",
            "desc": "Hokusai's other famous Fuji — a single triangular form lit crimson by morning sun, clouds streaming off the summit. From the same series as the Great Wave.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/%E3%80%8C%E5%AF%8C%E5%B6%BD%E4%B8%89%E5%8D%81%E5%85%AD%E6%99%AF_%E5%87%B1%E9%A2%A8%E5%BF%AB%E6%99%B4%E3%80%8D-South_Wind%2C_Clear_Sky_%28Gaif%C5%AB_kaisei%29%2C_also_known_as_Red_Fuji%2C_from_the_series_Thirty-six_Views_of_Mount_Fuji_%28Fugaku_sanj%C5%ABrokkei%29_MET_DP141062.jpg/960px-thumbnail.jpg",
            "artist": "Katsushika Hokusai",
        },
        {
            "title": "Cypress Trees",
            "meta": "Momoyama Japan · Kanō Eitoku · 1590",
            "desc": "An eight-panel folding screen with a single enormous cypress sprawling across gold leaf. The Kano school's monumental court style at its peak.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/%E7%8B%A9%E9%87%8E%E6%B0%B8%E5%BE%B3%E3%80%8A%E6%AA%9C%E5%9B%B3%E5%B1%8F%E9%A2%A8%E3%80%8B1590%E5%B9%B4%E3%80%8116%E4%B8%96%E7%B4%80%E3%80%81%E6%A1%83%E5%B1%B1%E6%99%82%E4%BB%A3%E3%80%81%E6%9D%B1%E4%BA%AC%E5%9B%BD%E7%AB%8B%E5%8D%9A%E7%89%A9%E9%A4%A8.jpg/960px-%E7%8B%A9%E9%87%8E%E6%B0%B8%E5%BE%B3%E3%80%8A%E6%AA%9C%E5%9B%B3%E5%B1%8F%E9%A2%A8%E3%80%8B1590%E5%B9%B4%E3%80%8116%E4%B8%96%E7%B4%80%E3%80%81%E6%A1%83%E5%B1%B1%E6%99%82%E4%BB%A3%E3%80%81%E6%9D%B1%E4%BA%AC%E5%9B%BD%E7%AB%8B%E5%8D%9A%E7%89%A4%E9%A4%A8.jpg",
            "artist": "Kanō Eitoku",
        },
        {
            "title": "Actor Prints of Sharaku",
            "meta": "Edo Japan · Tōshūsai Sharaku · 1794–1795",
            "desc": "Kabuki actors caught mid-gesture, their exaggerated faces rendered in crisp black outline against mica backgrounds. Sharaku worked for ten months and then vanished.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/0/0e/Toshusai_Sharaku-_Otani_Oniji%2C_1794.jpg",
            "artist": "Tōshūsai Sharaku",
        },
    ],
    "southeast-asia-oceania": [
        {
            "title": "Moon of Pejeng",
            "meta": "Dong Son tradition · c. 300 BCE · Bali",
            "desc": "The largest bronze kettledrum in the world — almost two meters across. In Balinese legend it's the fallen wheel of a chariot of the moon.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/68/Moon_of_Pejeng%2C_Pura_Penataran_Sasih_1463.jpg/960px-Moon_of_Pejeng%2C_Pura_Penataran_Sasih_1463.jpg",
        },
        {
            "title": "Wat Rong Khun (White Temple)",
            "meta": "Contemporary Thai Buddhist · Chalermchai Kositpipat · 1997 onward · Chiang Rai",
            "desc": "An entire temple sculpted white, glittering with shards of mirror. The artist intends it to take centuries to complete; hands rise from hell at the entrance.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Wat_Rong_Khun_-_Chiang_Rai.jpg/960px-Wat_Rong_Khun_-_Chiang_Rai.jpg",
            "artist": "Chalermchai Kositpipat",
        },
    ],
    "americas": [
        {
            "title": "Paquimé (Casas Grandes)",
            "meta": "Mogollon · 13th–14th c. · Chihuahua, Mexico",
            "desc": "Multi-story adobe pueblos north of the Maya world but connected to them — Paquimé traded in parrots, copper bells, and turquoise. Burned and abandoned before the Spanish arrived.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Paquime1.jpg/960px-Paquime1.jpg",
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
