#!/usr/bin/env python3
"""Batch 13 — push past 750."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"

NEW_WORKS: dict[str, list[dict]] = {
    "africa": [
        {
            "title": "Elmina Castle",
            "meta": "Portuguese colonial · 1482 · Ghana",
            "desc": "Whitewashed on a rock above the Gulf of Guinea — the oldest European building in sub-Saharan Africa. Started as a trading post for gold, became a holding point for the Atlantic slave trade.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Elmina_Castle_-_Ghana.jpg/960px-Elmina_Castle_-_Ghana.jpg",
            "year": 1482,
        },
        {
            "title": "Herero Dress",
            "meta": "Herero · late 19th c. onward · Namibia",
            "desc": "Floor-length Victorian gowns adopted from 19th-century German missionaries — kept, inverted, made defiantly Herero. The horned headdress honors cattle; the silhouette accuses a colonial past.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/7/71/Herero_women.jpg",
            "year": 1900,
        },
        {
            "title": "Great Mosque of Touba",
            "meta": "Mouride · 1963 · Senegal",
            "desc": "Founded by the Sufi saint Amadou Bamba; the current mosque completed in the 1960s. Five minarets and a green dome; a gathering of millions every year at the Magal pilgrimage.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Touba_%28senegal%29_2006.JPG/960px-Touba_%28senegal%29_2006.JPG",
            "year": 1963,
        },
        {
            "title": "Mbuti Bark Cloth",
            "meta": "Mbuti · traditional · Ituri Rainforest",
            "desc": "Beaten fig-bark cloth painted by women with dots, curves, and grids in charcoal, juice, and mud. Every panel is an individual composition — one of Africa's most abstract traditional visual idioms.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/f/f6/Bambuti.jpg",
            "year": 1930,
        },
        {
            "title": "Timbuktu Manuscripts",
            "meta": "West African Islamic · 13th c. onward · Mali",
            "desc": "Hundreds of thousands of hand-copied manuscripts on astronomy, law, medicine, poetry. Families smuggled them out of Timbuktu in 2013 as jihadists approached, hiding them in cellars and metal chests.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Timbuktu-manuscripts-astronomy-mathematics.jpg/960px-Timbuktu-manuscripts-astronomy-mathematics.jpg",
            "year": 1400,
        },
        {
            "title": "Ethiopian Illuminated Bible",
            "meta": "Ethiopian Orthodox · 15th c. onward",
            "desc": "Ge'ez-language bibles painted on parchment with bold figural interior pages — a distinctly Ethiopian Christian visual tradition that ran continuously from late antiquity to the 20th century.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/e/e2/Ethiopic_genesis_%28ch._29%2C_v._11-16%29%2C_15th_century_%28The_S.S._Teacher%27s_Edition-The_Holy_Bible_-_Plate_XII%2C_1%29.jpg",
            "year": 1450,
        },
    ],
    "egypt-nubia": [
        {
            "title": "Canopic Jars",
            "meta": "New Kingdom onward · c. 1500 BCE – 1000 BCE",
            "desc": "Four jars holding the mummy's liver, lungs, stomach, and intestines. Their lids shaped as the four sons of Horus — jackal, baboon, falcon, and human — each guarding a separate organ.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Canopic_jars_%28casts%29%2C_Egypt%2C_945-712_BC_-_National_Museum_of_Natural_History%2C_United_States_-_DSC00557.jpg/960px-Canopic_jars_%28casts%29%2C_Egypt%2C_945-712_BC_-_National_Museum_of_Natural_History%2C_United_States_-_DSC00557.jpg",
            "year": -900,
        },
    ],
    "mesopotamia-persia": [
        {
            "title": "Tell Brak",
            "meta": "Northern Mesopotamian · 4th millennium BCE · Syria",
            "desc": "One of the earliest large cities anywhere — older than Uruk. Its \"Eye Temple\" held thousands of tiny alabaster figurines with enormous eyes, stacked in devotional drifts.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Tell_Brak_001.jpg/960px-Tell_Brak_001.jpg",
            "year": -3500,
        },
        {
            "title": "Achaemenid Gold Rhyton",
            "meta": "Achaemenid Persia · 550–330 BCE",
            "desc": "A drinking horn that ends in the forequarters of a roaring lion, carved from a single piece of gold. Ceremonial, not functional — elite tableware as declaration of empire.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Achaemenid_gold_rhyton_in_the_shape_of_a_lion%2C_from_Ecbatana%2C_ca._550-330_BC%2C_Exhibition-_%27Iran%2C_Cradle_of_Civilizations%27%2C_Archaeological_Museum_of_Alicante_%28MARQ%29%2C_Spain_-_48244034452.jpg/960px-thumbnail.jpg",
            "year": -440,
        },
        {
            "title": "Dura-Europos Frescoes",
            "meta": "Parthian · 1st–3rd c. CE · Syria",
            "desc": "A caravan-city on the Euphrates whose buried buildings preserved the earliest synagogue murals, the earliest Christian house-church paintings, and Greek, Palmyrene, and Mithraic frescoes — all within blocks of each other.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/6/6a/Dura_Europos_fresco_Sacrifice_of_Conon.jpg",
            "year": 230,
        },
    ],
    "mediterranean": [
        {
            "title": "Temple of Apollo at Delphi",
            "meta": "Classical Greek · 4th c. BCE · Delphi",
            "desc": "The seat of the Oracle. Inscribed on its wall: \"Know thyself.\" Six of the original 38 Doric columns still stand at the edge of the sacred precinct.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Delphi_Temple_of_Apollo.jpg/960px-Delphi_Temple_of_Apollo.jpg",
            "year": -350,
        },
        {
            "title": "Heraion of Samos",
            "meta": "Archaic Greek · 6th c. BCE",
            "desc": "Sanctuary of Hera near her birthplace. Four successive temples built on the same footprint; the fourth was the largest Greek temple ever begun — never finished. One column standing.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Heraion_of_Samos_2.jpg/960px-Heraion_of_Samos_2.jpg",
            "year": -540,
        },
        {
            "title": "Propylaea of the Acropolis",
            "meta": "Classical Greek · Mnesicles · 437–432 BCE · Athens",
            "desc": "The ceremonial gateway to the Acropolis. An unfinished masterpiece — the Peloponnesian War stopped construction; beam sockets on the unfinished wings still wait for marble that never came.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/a/a6/Propylaea_and_Temple_of_Athena_Nike_at_the_Acropolis_%28Pierer%29.jpg",
            "year": -435,
        },
    ],
    "europe": [
        {
            "title": "Vertumnus",
            "meta": "Mannerism · 1591",
            "desc": "Portrait of Emperor Rudolf II as Vertumnus, god of seasons — his face built from pears, grapes, squash, grain. Arcimboldo's joke on Habsburg dignity; the emperor loved it.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Vertumnus_%C3%A5rstidernas_gud_m%C3%A5lad_av_Giuseppe_Arcimboldo_1591_-_Skoklosters_slott_-_91503.jpg/960px-Vertumnus_%C3%A5rstidernas_gud_m%C3%A5lad_av_Giuseppe_Arcimboldo_1591_-_Skoklosters_slott_-_91503.jpg",
            "artist": "Giuseppe Arcimboldo",
            "year": 1591,
        },
        {
            "title": "The Cardsharps",
            "meta": "Baroque · c. 1594",
            "desc": "An early Caravaggio: a boy is cheated at cards by a pair of accomplices — one palming a card behind his back, the other reading his hand over his shoulder. A career-making genre scene.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Caravaggio_%28Michelangelo_Merisi%29_-_The_Cardsharps_-_Google_Art_Project.jpg/960px-Caravaggio_%28Michelangelo_Merisi%29_-_The_Cardsharps_-_Google_Art_Project.jpg",
            "artist": "Caravaggio",
            "year": 1594,
        },
        {
            "title": "The Milkmaid of Bordeaux",
            "meta": "Late Goya · c. 1827",
            "desc": "Goya's last canvas, painted at 81 in exile in Bordeaux. A young woman looking down over her shoulder — loose, almost proto-Impressionist brushwork. Bequeathed to his last companion.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Goya_MilkMaid.jpg/960px-Goya_MilkMaid.jpg",
            "artist": "Francisco Goya",
            "year": 1827,
        },
    ],
    "islamic-world": [
        {
            "title": "Jameh Mosque of Yazd",
            "meta": "Azari style · 12th–15th c. · Iran",
            "desc": "A tall twin-minaret mosque faced in blue tile mosaic. Its high entrance iwan is featured on the Iranian 200-rial note.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Jameh_Mosque_of_Yazd_Iran.jpg/960px-Jameh_Mosque_of_Yazd_Iran.jpg",
            "year": 1350,
        },
        {
            "title": "Itchan Kala View",
            "meta": "Khanate of Khiva · 10th c. onward · Uzbekistan",
            "desc": "The walled inner town of Khiva — minarets, mausoleums, madrasas all packed inside dun-colored mud-brick walls. So intact it can feel like a stage set.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dc/View_from_the_city_walls%2C_Khiva_%284934484894%29.jpg/960px-View_from_the_city_walls%2C_Khiva_%284934484894%29.jpg",
            "year": 1600,
        },
        {
            "title": "Merv",
            "meta": "Seljuk · 11th–12th c. · Turkmenistan",
            "desc": "A caravan oasis on the Silk Road — Alexander's Margiana, the Sasanian second city, a Seljuk capital. The mausoleum of Sultan Sanjar still stands, its blue dome long since fallen in.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Turkmenistan_Merv_city.jpg/960px-Turkmenistan_Merv_city.jpg",
            "year": 1150,
        },
        {
            "title": "Imam Reza Shrine",
            "meta": "Safavid → Pahlavi · 9th c. onward · Mashhad",
            "desc": "The largest mosque in the world by floor area. Tomb of the eighth Shia Imam; seven courtyards; interiors covered in mirror mosaics that turn every surface into fractured gold.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/%D8%B5%D8%AD%D9%86_%D8%A7%DB%8C%D9%88%D8%A7%D9%86_%D8%B7%D9%84%D8%A7_%D9%88_%D8%B3%D9%82%D8%A7%D8%AE%D8%A7%D9%86%D9%87.jpg/960px-%D8%B5%D8%AD%D9%86_%D8%A7%DB%8C%D9%88%D8%A7%D9%86_%D8%B7%D9%84%D8%A7_%D9%88_%D8%B3%D9%82%D8%A7%D8%AE%D8%A7%D9%86%D9%87.jpg",
            "year": 820,
        },
    ],
    "south-asia": [
        {
            "title": "Lotus Mahal",
            "meta": "Vijayanagara · 16th c. · Hampi",
            "desc": "A pavilion in the zenana quarter with lotus-shaped scalloped arches. Architectural hybrid: Hindu temple superstructure atop Islamic multifoil arches — courtly syncretism in stone.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/Flat_elevation_of_Lotus_Mahal%2C_Hampi_%28Closeup%29.jpg/960px-Flat_elevation_of_Lotus_Mahal%2C_Hampi_%28Closeup%29.jpg",
            "year": 1550,
        },
        {
            "title": "Rock Garden of Chandigarh",
            "meta": "Outsider · Nek Chand · 1957 onward · India",
            "desc": "A secret sculpture park a road inspector built on the sly from broken bangles, electric switches, ceramic shards, and urban trash. Discovered by authorities in 1975; preserved on public demand.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Chandigarh_Rock_Garden_4.jpg/960px-Chandigarh_Rock_Garden_4.jpg",
            "artist": "Nek Chand",
            "year": 1957,
        },
        {
            "title": "Lotus Temple",
            "meta": "Modernist Bahá'í · Fariborz Sahba · 1986 · Delhi",
            "desc": "A Bahá'í House of Worship in 27 free-standing white marble petals arranged in three clusters — one of the most visited buildings in the world.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/LotusDelhi.jpg/960px-LotusDelhi.jpg",
            "artist": "Fariborz Sahba",
            "year": 1986,
        },
    ],
    "east-asia": [
        {
            "title": "Itsukushima Shrine",
            "meta": "Heian onward · 12th c. · Japan",
            "desc": "A shrine built over the tidal flats — the famous vermilion torii appears to float at high tide. Commoners were forbidden to set foot on the sacred island; they approached by boat.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Itsukushima_Shrine_Torii_Gate_%2813890465459%29.jpg/960px-Itsukushima_Shrine_Torii_Gate_%2813890465459%29.jpg",
            "year": 1168,
        },
        {
            "title": "Kyoto Imperial Palace",
            "meta": "Heian → Edo · 794–1868 · Kyoto",
            "desc": "The residence of the emperor of Japan from 794 until 1869. Repeatedly burned and rebuilt; the current compound follows the Heian original, walled off in parkland in central Kyoto.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Kyoto-gosho_Kenreimon_%28open%29.JPG/960px-Kyoto-gosho_Kenreimon_%28open%29.JPG",
            "year": 794,
        },
        {
            "title": "Nijō Castle",
            "meta": "Edo Japan · 1603 · Kyoto",
            "desc": "Residence of the Tokugawa shoguns during visits to Kyoto. Its \"nightingale\" floors squeak deliberately underfoot — designed to warn of intruders. The shogunate fell within its walls in 1868.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/NinomaruPalace.jpg/960px-NinomaruPalace.jpg",
            "year": 1603,
        },
        {
            "title": "Jogyesa",
            "meta": "Korean Seon Buddhist · founded 1395 · Seoul",
            "desc": "The head temple of the Jogye Order — the principal Korean Buddhist school. An old pagoda tree in the courtyard is 450 years old; lanterns hang from it by the thousands at Buddha's birthday.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Jogyesa_Temple_%281509839597%29.jpg/960px-Jogyesa_Temple_%281509839597%29.jpg",
            "year": 1395,
        },
    ],
    "southeast-asia-oceania": [
        {
            "title": "Phra Pathom Chedi",
            "meta": "Mon → Rama IV · 3rd c. BCE core, 1850s outer · Thailand",
            "desc": "The tallest stupa in the world — 120 meters of orange-tiled bell. A Mon-era chedi encased in a 19th-century Siamese one, as if a building were its own tomb.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/%E0%B8%9E%E0%B8%A3%E0%B8%B0%E0%B8%9B%E0%B8%90%E0%B8%A1%E0%B9%80%E0%B8%88%E0%B8%94%E0%B8%B5%E0%B8%A2%E0%B9%8C%E0%B8%97%E0%B8%B4%E0%B8%A8%E0%B9%80%E0%B8%AB%E0%B8%99%E0%B8%B7%E0%B8%AD.jpg/960px-%E0%B8%9E%E0%B8%A3%E0%B8%B0%E0%B8%9B%E0%B8%90%E0%B8%A1%E0%B9%80%E0%B8%88%E0%B8%94%E0%B8%B5%E0%B8%A2%E0%B9%8C%E0%B8%97%E0%B8%B4%E0%B8%A8%E0%B9%80%E0%B8%AB%E0%B8%99%E0%B8%B7%E0%B8%AD.jpg",
            "year": 1853,
        },
        {
            "title": "Preah Khan",
            "meta": "Khmer Empire · Jayavarman VII · 1191 · Cambodia",
            "desc": "A temple-monastery and university at Angkor, its halls so extensive they once housed 100,000 people. Left partly jungle-swallowed — silk-cotton tree roots grip the stonework.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Preah_Khan%2C_Angkor%2C_Camboya%2C_2013-08-17%2C_DD_26.JPG/960px-Preah_Khan%2C_Angkor%2C_Camboya%2C_2013-08-17%2C_DD_26.JPG",
            "year": 1191,
        },
        {
            "title": "Thiên Mụ Pagoda",
            "meta": "Nguyễn lords · 1601 · Huế, Vietnam",
            "desc": "Seven storeys of octagonal tower on the Perfume River. In 1963 a Thiên Mụ monk drove from here to Saigon and set himself on fire in protest — the photograph that shook a war.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/ThienMuPagoda.jpg/960px-ThienMuPagoda.jpg",
            "year": 1601,
        },
        {
            "title": "Shwezigon Pagoda",
            "meta": "Pagan Kingdom · 11th c. · Myanmar",
            "desc": "A gilded stupa in Bagan, rebuilt after earthquakes. Its bell shape and golden leaf-gilt became the standard template for Burmese stupas for a thousand years.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Shwezigon.jpg/960px-Shwezigon.jpg",
            "year": 1090,
        },
    ],
    "americas": [
        {
            "title": "Canyon de Chelly",
            "meta": "Ancestral Puebloan · 350–1300 CE · Arizona",
            "desc": "Red sandstone canyon with cliff-dweller ruins tucked into shadowed overhangs. Later a Navajo stronghold; Kit Carson's 1864 campaign forced the Long Walk from here.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Canyon_de_Chelly%2C_Navajo.jpg/960px-Canyon_de_Chelly%2C_Navajo.jpg",
            "year": 1100,
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
