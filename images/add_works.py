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
    "africa": [
        {
            "title": "Brandberg Rock Paintings",
            "meta": "San · up to 2,000 years old · Namibia",
            "desc": "The Brandberg Massif hides thousands of rock paintings, most famously the \"White Lady\" — not a lady at all, but a medicine figure. Painted for ritual, not ornament.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Brandberg_%28Namibia%29.jpg/960px-Brandberg_%28Namibia%29.jpg",
        },
        {
            "title": "Twyfelfontein Petroglyphs",
            "meta": "Pre-San hunter-gatherers · 6,000 years old · Namibia",
            "desc": "Thousands of rock engravings of giraffes, rhinos, and lions on sandstone. A seal, 900 km from the nearest sea, suggests long-distance travel — or long memory.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Twyfelfontein_16.jpg/960px-Twyfelfontein_16.jpg",
        },
    ],
    "egypt-nubia": [
        {
            "title": "Great Sphinx of Tanis",
            "meta": "Old to Middle Kingdom · c. 2600–1800 BCE",
            "desc": "One of the largest sphinxes outside Giza — reused and re-inscribed by pharaoh after pharaoh. Now guards the entrance of the Louvre's Egyptian galleries.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Grand_sphinx_de_Tanis_-_Mus%C3%A9e_du_Louvre_Antiquit%C3%A9s_%C3%A9gyptiennes_N_23_%3B_A_23_%3B_Salt_3837.jpg/960px-Grand_sphinx_de_Tanis_-_Mus%C3%A9e_du_Louvre_Antiquit%C3%A9s_%C3%A9gyptiennes_N_23_%3B_A_23_%3B_Salt_3837.jpg",
        },
        {
            "title": "Mastaba of Ti",
            "meta": "Old Kingdom · c. 2400 BCE · Saqqara",
            "desc": "The tomb of a minor royal official, painted inside with daily-life scenes — farming, fishing, ships under sail — and regarded as the high point of Old Kingdom relief.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/7/7e/Mastaba_Ti_07.jpg",
        },
    ],
    "mesopotamia-persia": [
        {
            "title": "Stele of the Vultures",
            "meta": "Sumerian · c. 2450 BCE · Lagash",
            "desc": "The earliest known battle monument. King Eannatum's army marches in lockstep behind their shields; on the other side, vultures carry off the heads of the defeated.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Stele_of_the_Vultures_in_the_Louvre_Museum_%28enhanced_composite%29.jpg/960px-Stele_of_the_Vultures_in_the_Louvre_Museum_%28enhanced_composite%29.jpg",
        },
        {
            "title": "Queen Puabi's Headdress",
            "meta": "Sumerian · c. 2600 BCE · Ur",
            "desc": "Gold leaves, lapis lazuli pendants, carnelian beads, tied with ribbon hair-wire. Queen Puabi went to her grave wearing this, attended by 23 servants — also buried.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/b/b8/Queen_Puabi_with_attendants.jpg",
        },
    ],
    "mediterranean": [
        {
            "title": "Portland Vase",
            "meta": "Roman cameo glass · c. 1–25 CE",
            "desc": "A cobalt-blue glass vase dipped in white and carved back through the outer layer. One of the finest surviving pieces of Roman cameo glass — and inspiration for Wedgwood's first portraits.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Portland_Vase_BM_Gem4036_n1.jpg/960px-Portland_Vase_BM_Gem4036_n1.jpg",
        },
        {
            "title": "Equestrian Statue of Marcus Aurelius",
            "meta": "Roman Imperial · c. 175 CE",
            "desc": "The only surviving large Roman bronze equestrian. It lived because Christians mistook it for Constantine. Now replaced by a copy in the Campidoglio; the original is inside.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Equestrian_statue_of_Marcus_Aurelius_%28Rome%29.jpg/960px-Equestrian_statue_of_Marcus_Aurelius_%28Rome%29.jpg",
        },
    ],
    "europe": [
        {
            "title": "Scrovegni Chapel Frescoes",
            "meta": "Proto-Renaissance · 1303–1305 · Padua",
            "desc": "Giotto's cycle of the life of the Virgin and Christ. A man paid for it to save his father from hell — his father appears in the painting, handing over the chapel model.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/Padova_Cappella_degli_Scrovegni_Innen_Langhaus_West_5.jpg/960px-Padova_Cappella_degli_Scrovegni_Innen_Langhaus_West_5.jpg",
            "artist": "Giotto di Bondone",
        },
        {
            "title": "The Fighting Temeraire",
            "meta": "English Romanticism · 1839",
            "desc": "A storied warship, veteran of Trafalgar, tugged by a smudgy little steam tug to the breaker's yard. Turner's elegy for the age of sail — voted Britain's favorite painting.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/The_Fighting_Temeraire%2C_JMW_Turner%2C_National_Gallery.jpg/960px-The_Fighting_Temeraire%2C_JMW_Turner%2C_National_Gallery.jpg",
            "artist": "J. M. W. Turner",
        },
        {
            "title": "Judith Beheading Holofernes",
            "meta": "Baroque · c. 1599",
            "desc": "Judith, arms extended to keep the blood off her dress, saws through the Assyrian general's neck. Caravaggio's first great biblical violence — the beginning of his reputation.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/df/Caravaggio_-_Giuditta_e_Oloferne_%28ca._1599%29.jpg/960px-Caravaggio_-_Giuditta_e_Oloferne_%28ca._1599%29.jpg",
            "artist": "Caravaggio",
        },
    ],
    "islamic-world": [
        {
            "title": "Maqamat al-Hariri",
            "meta": "Abbasid · al-Wasiti · 1237 · Baghdad",
            "desc": "An illustrated manuscript of Hariri's picaresque stories — streets, markets, pilgrims, drunks, courts of law. The earliest surviving paintings of daily Baghdad life.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Maqama_43_Abu_Zayd_travelling_on_horse.jpg/960px-Maqama_43_Abu_Zayd_travelling_on_horse.jpg",
            "artist": "Yahya al-Wasiti",
        },
        {
            "title": "Shahnameh of Shah Tahmasp",
            "meta": "Safavid · 16th c. · Iran",
            "desc": "A royal copy of Ferdowsi's epic with 258 miniatures painted by the court workshop — mountains with gold streams, demons in the rocks. One of the great illuminated manuscripts.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/The_Court_of_Gayumars_%28Cropped%29.jpg/960px-The_Court_of_Gayumars_%28Cropped%29.jpg",
        },
    ],
    "south-asia": [
        {
            "title": "Pancha Rathas",
            "meta": "Pallava · 7th c. · Mahabalipuram",
            "desc": "Five monolithic shrines carved from a single granite ridge in the shape of temple chariots. Each is a different architectural experiment — the prototypes for a millennium of South Indian temples.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Five_Rathas_at_Mahaballipuram%2CTamil_Nadu.jpg/960px-Five_Rathas_at_Mahaballipuram%2CTamil_Nadu.jpg",
        },
        {
            "title": "Nalanda Mahavihara",
            "meta": "Pala dynasty · 5th–12th c. · Bihar",
            "desc": "A Buddhist university that drew ten thousand monks from across Asia. Burned by Bakhtiyar Khalji around 1193; the library, they say, smoked for months.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Temple_No.-_3%2C_Nalanda_Archaeological_Site.jpg/960px-Temple_No.-_3%2C_Nalanda_Archaeological_Site.jpg",
        },
    ],
    "east-asia": [
        {
            "title": "Night-Shining White",
            "meta": "Tang dynasty · Han Gan · c. 750 · China",
            "desc": "A tethered stallion struggling at the post — snorting, hooves kicking. The emperor Xuanzong's favorite horse, painted in ink so alive it almost leaves the silk.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Palefrenier_menant_deux_chevaux_par_Han_Gan.jpg/960px-Palefrenier_menant_deux_chevaux_par_Han_Gan.jpg",
            "artist": "Han Gan",
        },
        {
            "title": "Red and White Plum Blossoms",
            "meta": "Edo Japan · Ogata Kōrin · early 18th c.",
            "desc": "A pair of folding screens: two plum trees, red and white, lean toward a stylized silver river of whorls. Rinpa-school decorative painting at its most distilled.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Ogata_Korin_-_RED_AND_WHITE_PLUM_BLOSSOMS_%28National_Treasure%29_-_Google_Art_Project.jpg/960px-Ogata_Korin_-_RED_AND_WHITE_PLUM_BLOSSOMS_%28National_Treasure%29_-_Google_Art_Project.jpg",
            "artist": "Ogata Kōrin",
        },
    ],
    "southeast-asia-oceania": [
        {
            "title": "Candi Sukuh",
            "meta": "Majapahit · 15th c. · Java",
            "desc": "A Hindu temple built as a truncated stone pyramid — closer to Maya than to Angkor. Its reliefs are frank about fertility; the statues at the gate tell you what they're for.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/70/Candi_Sukuh_2007.JPG/960px-Candi_Sukuh_2007.JPG",
        },
    ],
    "americas": [
        {
            "title": "Pyramid of the Magician",
            "meta": "Late Classic Maya · 600–900 CE · Uxmal",
            "desc": "An oval-based pyramid whose legend says it was built in one night by a dwarf magician. Every stone is carved; the central doorway is a monster's open mouth.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Pyramid_of_the_Magician_%288264902976%29.jpg/960px-Pyramid_of_the_Magician_%288264902976%29.jpg",
        },
        {
            "title": "Tumi Ceremonial Knife",
            "meta": "Lambayeque · 900–1100 · Northern Peru",
            "desc": "A gold sacrificial knife topped with the long-eared god Naylamp, eyes inlaid with turquoise. Used for ritual decapitation; now a symbol of Peru on souvenir shelves everywhere.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/Ceremonial_Knife_%28Tumi%29_MET_DP215693.jpg/960px-Ceremonial_Knife_%28Tumi%29_MET_DP215693.jpg",
        },
        {
            "title": "Coyolxāuhqui Stone",
            "meta": "Mexica · late 15th c. · Tenochtitlan",
            "desc": "A twelve-foot disk of the moon goddess, dismembered by her brother Huitzilopochtli. Found by electric-company workers in Mexico City in 1978 — it launched modern excavation of the Templo Mayor.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Mexico-3980_-_Coyolxauhqui_Stone_%282508259597%29.jpg/960px-Mexico-3980_-_Coyolxauhqui_Stone_%282508259597%29.jpg",
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
