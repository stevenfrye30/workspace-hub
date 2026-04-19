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
            "title": "Red Bird",
            "meta": "Contemporary · c. 2000s · United Kingdom / Nigeria",
            "desc": "Chris Ofili's paintings layer resin-coated elephant dung onto glittering collage. His work interrogates Black identity and the politics of representation in Britain.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/4/4a/Red_Bird_Chris_Ofili.jpg",
            "artist": "Chris Ofili",
            "year": 2005,
        },
        {
            "title": "Shona Stone Sculpture",
            "meta": "Shona · 20th c. onward · Zimbabwe",
            "desc": "A post-colonial sculptural tradition carved from serpentine and springstone. Figures of spirits and ancestors, often semi-abstracted — now Zimbabwe's most recognized art export.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Zimbabwe_sculpture_at_Atlanta_airport.JPG/960px-Zimbabwe_sculpture_at_Atlanta_airport.JPG",
            "year": 1980,
        },
    ],
    "egypt-nubia": [
        {
            "title": "Amarna Letters",
            "meta": "New Kingdom · 14th c. BCE",
            "desc": "Clay tablets of diplomatic correspondence between Egypt and its neighbors — Babylonia, Assyria, the Hittites, Canaanite city-states. Written in Akkadian, the lingua franca of the Bronze Age.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Five_Amarna_letters_on_display_at_the_British_Museum%2C_LondonA.jpg/960px-Five_Amarna_letters_on_display_at_the_British_Museum%2C_LondonA.jpg",
            "year": -1350,
        },
    ],
    "mesopotamia-persia": [
        {
            "title": "Statue of Gudea",
            "meta": "Neo-Sumerian · c. 2120 BCE · Lagash",
            "desc": "More than twenty small diorite statues of the prince of Lagash survive, each showing him at prayer. The diorite was hauled from the Sinai; carving it took tools that barely existed.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Gudea_of_Lagash_Girsu.jpg/960px-Gudea_of_Lagash_Girsu.jpg",
            "year": -2120,
        },
        {
            "title": "Petra — Al-Khazneh",
            "meta": "Nabataean · 1st c. BCE – 1st c. CE · Jordan",
            "desc": "The \"Treasury\" — a 40-meter temple-facade carved directly into the rose-red sandstone cliff. Bedouin shot at the urn at the top, hoping to spill hidden pharaoh's gold.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Treasury_petra_crop.jpeg/960px-Treasury_petra_crop.jpeg",
            "year": 0,
        },
    ],
    "mediterranean": [
        {
            "title": "House of the Faun",
            "meta": "Roman · 2nd c. BCE · Pompeii",
            "desc": "One of the largest residences in Pompeii, three acres across. Its atrium held the bronze dancing faun that gave it the name; the floor held the Alexander Mosaic.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/House_of_the_Faun_%28Pompeii%29.jpg/960px-House_of_the_Faun_%28Pompeii%29.jpg",
            "year": -150,
        },
        {
            "title": "Nike of Paionios",
            "meta": "Classical Greek · Paionios · c. 420 BCE · Olympia",
            "desc": "The Messenians and Naupactians dedicated her at Olympia after a victory over Sparta. Nike lands on a plinth, wind pressing drapery against her body — 170 years before the Winged Victory of Samothrace.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/Nike_of_Paionios%2C_Olympia_Archaeological_Museum_%2816309967616%29.jpg/960px-Nike_of_Paionios%2C_Olympia_Archaeological_Museum_%2816309967616%29.jpg",
            "artist": "Paionios",
            "year": -420,
        },
    ],
    "europe": [
        {
            "title": "Composition VII",
            "meta": "Abstract · 1913",
            "desc": "Kandinsky called it the most complex work he ever painted — over thirty preparatory studies. Motifs of resurrection, flood, and last judgment dissolve into color and line.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/Composition_VII_-_Wassily_Kandinsky%2C_GAC.jpg/960px-Composition_VII_-_Wassily_Kandinsky%2C_GAC.jpg",
            "artist": "Wassily Kandinsky",
            "year": 1913,
        },
        {
            "title": "Composition with Red, Blue and Yellow",
            "meta": "De Stijl · 1930",
            "desc": "Black lines, three primary colors, white negative space, canvas flat as the grid itself. Mondrian believed he had found the underlying logic of visible reality.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Piet_Mondriaan%2C_1930_-_Mondrian_Composition_II_in_Red%2C_Blue%2C_and_Yellow.jpg/960px-Piet_Mondriaan%2C_1930_-_Mondrian_Composition_II_in_Red%2C_Blue%2C_and_Yellow.jpg",
            "artist": "Piet Mondrian",
            "year": 1930,
        },
        {
            "title": "I and the Village",
            "meta": "Cubist / Expressionist · 1911",
            "desc": "A green-faced peasant and a white goat exchange a look across a village that floats and spins. Chagall's memory of his hometown of Vitebsk, filtered through Paris.",
            "image": "https://upload.wikimedia.org/wikipedia/en/thumb/e/e7/Chagall_IandTheVillage.jpg/960px-Chagall_IandTheVillage.jpg",
            "artist": "Marc Chagall",
            "year": 1911,
        },
    ],
    "islamic-world": [
        {
            "title": "Naqsh-e Jahan Square",
            "meta": "Safavid · 1598 onward · Isfahan",
            "desc": "One of the largest squares in the world. Built by Shah Abbas to stage polo, military reviews, and the stateliness of a capital — framed on four sides by a mosque, a palace, a bazaar, and a private chapel.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ee/Naqsh-i_Jahan_Square%2C_Jan._2018.jpg/960px-Naqsh-i_Jahan_Square%2C_Jan._2018.jpg",
            "year": 1598,
        },
        {
            "title": "Shah Cheragh",
            "meta": "Qajar · 14th c. onward · Shiraz",
            "desc": "A Shia shrine covered inside floor to ceiling in thousands of shards of mirror. Candlelight becomes a galaxy. Pilgrims hold a finger against the wall and watch their reflection splinter.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/Mausoleo_de_Shah_Cheragh%2C_Shiraz%2C_Ir%C3%A1n%2C_2016-09-24%2C_DD_32.jpg/960px-Mausoleo_de_Shah_Cheragh%2C_Shiraz%2C_Ir%C3%A1n%2C_2016-09-24%2C_DD_32.jpg",
            "year": 1350,
        },
    ],
    "south-asia": [
        {
            "title": "Amaravati Stupa Reliefs",
            "meta": "Satavahana · 2nd c. BCE – 3rd c. CE · Andhra Pradesh",
            "desc": "A Buddhist stupa whose limestone casing was carved with some of the earliest Buddha figures in India. Most pieces are now in the British Museum and the Chennai Government Museum.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/British_Museum_Asia_14.jpg/960px-British_Museum_Asia_14.jpg",
            "year": 0,
        },
        {
            "title": "Karla Caves",
            "meta": "Early Buddhist · 1st c. BCE · Maharashtra",
            "desc": "The largest rock-cut chaitya hall in India — a barrel-vaulted cave church with a lantern roof carved in stone to mimic wood beams it never had.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/ff/Karla_caves_Chaitya.jpg/960px-Karla_caves_Chaitya.jpg",
            "year": -50,
        },
        {
            "title": "Mathura Bodhisattva",
            "meta": "Kushan · 1st–3rd c. CE · Uttar Pradesh",
            "desc": "Red sandstone figures in a distinctly Indian idiom — broad-shouldered, loose-robed, flatter and more frontal than the Greco-Buddhist Gandhara school evolving to the northwest.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Amohaasi_Bodhisattva%2C_Mathura.jpg/960px-Amohaasi_Bodhisattva%2C_Mathura.jpg",
            "year": 150,
        },
        {
            "title": "Rampurva Bull Capital",
            "meta": "Mauryan · 3rd c. BCE · Bihar",
            "desc": "An Ashokan pillar capital: a single polished Chunar sandstone bull, so highly burnished it was mistaken for metal. One of the finest survivals of the Mauryan court style.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/a/a0/Rampurva_bull_in_Presidential_Palace_high_closeup.jpg",
            "year": -250,
        },
    ],
    "east-asia": [
        {
            "title": "Haniwa",
            "meta": "Kofun period · 3rd–6th c. CE · Japan",
            "desc": "Hollow terracotta cylinders and figures set in rings around imperial tumuli. Armored warriors, horses, dancers, shrine maidens — the only accessible record of pre-literate Japanese dress.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Warrior_in_Keiko_Armor%2C_National_Treasure%2C_Kofun_period%2C_6th_century%2C_haniwa_%28terracotta_tomb_figurine%29_from_Iizuka-machi%2C_Ota-shi%2C_Gunma_-_Tokyo_National_Museum_-_DSC06425.JPG/960px-thumbnail.jpg",
            "year": 500,
        },
        {
            "title": "Kakiemon Porcelain",
            "meta": "Edo Japan · 17th c. onward · Arita",
            "desc": "Overglaze enamels on a milk-white ground. The Kakiemon workshop at Arita invented a palette — iron red, green, yellow, blue — that Meissen and Chantilly spent decades trying to copy.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Hexagonal_Jar%2C_Imari_ware%2C_Kakiemon_type%2C_Edo_period%2C_17th_century%2C_flowering_plant_and_phoenix_design_in_overglaze_enamel_-_Tokyo_National_Museum_-_DSC05329_%28retouched%29.jpg/960px-thumbnail.jpg",
            "year": 1670,
        },
        {
            "title": "Katsura Imperial Villa",
            "meta": "Edo Japan · 1620 onward · Kyoto",
            "desc": "A villa and garden considered one of the finest masterpieces of Japanese architecture. Shoin-zukuri precision: every plank, every sight-line from every veranda, deliberately aligned.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/Katsura_Rikyu_%283264799678%29.jpg/960px-Katsura_Rikyu_%283264799678%29.jpg",
            "year": 1620,
        },
    ],
    "southeast-asia-oceania": [
        {
            "title": "Ban Chiang",
            "meta": "Bronze Age · 1500 BCE – 300 CE · Thailand",
            "desc": "Painted red-on-buff pottery from a prehistoric village in northeast Thailand — swirling spirals and concentric whorls. Bronze was cast here earlier than the textbooks once allowed.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Ban_Chiang_Museum_Excavation.JPG/960px-Ban_Chiang_Museum_Excavation.JPG",
            "year": -600,
        },
    ],
    "americas": [
        {
            "title": "Crooked Beak of Heaven Mask",
            "meta": "Kwakwaka'wakw · 19th c. · Pacific Northwest",
            "desc": "A transformation mask from the Hamatsa winter dance. The outer \"cannibal bird\" beak opens with strings during the dance to reveal a human face within — the return of the initiate.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Crooked_Beak_of_Heaven_Mask.jpg/960px-Crooked_Beak_of_Heaven_Mask.jpg",
            "year": 1870,
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
