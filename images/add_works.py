#!/usr/bin/env python3
"""Batch 27 — Parthian, Sasanian, Hittite, Bamileke/Baga/Mangbetu, Roman glass, Coptic, Iznik, Mughal, Khmer bronzes."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"

NEW_WORKS: dict[str, list[dict]] = {
    "mesopotamia-persia": [
        {
            "title": "Palmyrene Procession of Nobles",
            "meta": "Palmyra · 100–150 CE · limestone",
            "desc": "A relief of robed Palmyrene nobles in frontal procession — the caravan city brokered silk between Rome and Parthia, before Zenobia's revolt brought Aurelian's legions down on it in 272.",
            "image": "https://openaccess-cdn.clevelandart.org/1970.15/1970.15_print.jpg",
            "year": 100,
        },
        {
            "title": "Parthian Head of a Girl",
            "meta": "Parthian · 1st–2nd c. CE · terracotta",
            "desc": "A small terracotta head, broken from a figurine — mass-produced in Parthian workshops between Tigris and Euphrates, where Greek portrait conventions met Iranian faces.",
            "image": "https://openaccess-cdn.clevelandart.org/1933.167/1933.167_print.jpg",
            "year": 1,
        },
        {
            "title": "Hittite Stag Poletop",
            "meta": "Anatolia · Hittite · 14th–12th c. BCE · bronze",
            "desc": "A cast-bronze stag that crowned a wooden standard — the Hittites worshipped a stag-god alongside the storm-god, and metal figurines like this stood on ceremonial carts.",
            "image": "https://openaccess-cdn.clevelandart.org/1975.13/1975.13_print.jpg",
            "year": -1400,
        },
        {
            "title": "Hittite Relief Vessel with Ritual Scenes",
            "meta": "Anatolia · Hittite · 14th–12th c. BCE · burnished earthenware",
            "desc": "An earthenware jar molded in four panels of Hittite ritual scenes — one of only a handful of figurative narrative vessels from the empire that fought Ramesses II at Kadesh.",
            "image": "https://openaccess-cdn.clevelandart.org/1985.70/1985.70_print.jpg",
            "year": -1400,
        },
        {
            "title": "Sasanian Royal Hunt Dish",
            "meta": "Sasanian Iran · 5th–6th c. CE · silver gilt",
            "desc": "King Hormizd on horseback twisting to shoot a lion that has leapt onto his saddle. Sasanian hunt dishes travelled as royal diplomatic gifts, reaching as far as the Volga.",
            "image": "https://openaccess-cdn.clevelandart.org/1962.150/1962.150_print.jpg",
            "year": 400,
        },
        {
            "title": "Sasanian Water Buffalo Rhyton",
            "meta": "Sasanian Iran · 6th–7th c. · gilt silver with glass inlay",
            "desc": "A drinking horn whose spout is a water buffalo, its rider a woman — likely the goddess Anahita, whose cult fused fertility, water, and war in late Sasanian Iran.",
            "image": "https://openaccess-cdn.clevelandart.org/1964.96/1964.96_print.jpg",
            "year": 500,
        },
        {
            "title": "Sumerian Striding Goat",
            "meta": "Sumer · c. 3200 BCE · limestone with Egyptian blue inlay",
            "desc": "A limestone goat with inlaid blue eyes, from the Uruk period just before writing — Sumerian temple workshops fixed the animal forms that would echo through the next three millennia.",
            "image": "https://openaccess-cdn.clevelandart.org/1984.35/1984.35_print.jpg",
            "year": -3200,
        },
        {
            "title": "Amlash Lion Hunting Cup",
            "meta": "Amlash (Iran) · 11th c. BCE · silver",
            "desc": "A raised silver cup from south of the Caspian, showing a hunter driving his spear into a lion. Amlash metalwork surfaces in tombs along a mountain corridor Iranian-speakers followed south into the plateau.",
            "image": "https://openaccess-cdn.clevelandart.org/1965.25/1965.25_print.jpg",
            "year": -1100,
        },
    ],
    "africa": [
        {
            "title": "Kuba Bwoom Mask",
            "meta": "Kuba · Congo · mid–late 19th c. · wood and paint",
            "desc": "An initiation helmet mask with bulging forehead — Bwoom represents a commoner or prince opposite two royal masks; at masquerades the three perform a mythic family argument.",
            "image": "https://openaccess-cdn.clevelandart.org/1935.304/1935.304_print.jpg",
            "year": 1850,
        },
        {
            "title": "Yombe Phemba Mother and Child",
            "meta": "Yombe · Congo · mid–late 19th c. · wood",
            "desc": "A seated Yombe mother with her child — phemba figures held fertility medicine in a cavity in the back, carried by women struggling to conceive.",
            "image": "https://openaccess-cdn.clevelandart.org/2003.35/2003.35_print.jpg",
            "year": 1850,
        },
        {
            "title": "Mangbetu Figurative Harp (Domu)",
            "meta": "Mangbetu · Congo · early 20th c. · wood and rawhide",
            "desc": "An arched harp topped with a female head in elongated Mangbetu style — head-binding was a real beauty practice, and musicians in the 1920s Ituri played these at King Okondo's palace.",
            "image": "https://openaccess-cdn.clevelandart.org/1918.356/1918.356_print.jpg",
            "year": 1900,
        },
        {
            "title": "Baga Serpent Headdress",
            "meta": "Baga · Guinea · late 19th–early 20th c. · wood and paint",
            "desc": "A tall painted wooden serpent worn above the dancer's head. When colonial missions banned the Baga cult in the 1950s the masks burned or sold abroad; the form was revived in 1985.",
            "image": "https://openaccess-cdn.clevelandart.org/1960.37/1960.37_print.jpg",
            "year": 1890,
        },
        {
            "title": "Bamileke Elephant Mask (Mbap Mteng)",
            "meta": "Bamileke · Cameroon Grassfields · early 20th c. · beads on cloth",
            "desc": "A beaded cloth elephant mask with long trunk panels — worn by members of the Kuosi society, it declared the wearer's wealth through thousands of imported glass beads.",
            "image": "https://openaccess-cdn.clevelandart.org/1985.1082/1985.1082_print.jpg",
            "year": 1900,
        },
        {
            "title": "Sapi Nomoli Figure",
            "meta": "Sapi · Sierra Leone · 15th c. · soapstone",
            "desc": "A soapstone seated figure carved by the Sapi before Portuguese contact — later farmers pulled these up from their fields, called them nomoli, and placed them in rice shrines as house-spirits.",
            "image": "https://openaccess-cdn.clevelandart.org/1976.29/1976.29_print.jpg",
            "year": 1400,
        },
        {
            "title": "Djenné-Djenno Terracotta Figure",
            "meta": "Djenné-Djenno · Mali · 14th–17th c. · terracotta",
            "desc": "A terracotta figure from sub-Saharan Africa's oldest city, found buried in abandoned house-floors. Most were looted in the 1970s–80s; provenance is now a permanent scandal of the trade.",
            "image": "https://openaccess-cdn.clevelandart.org/1985.199/1985.199_print.jpg",
            "year": 1400,
        },
        {
            "title": "Lega Bwami Iginga Figure",
            "meta": "Lega · Congo · 19th c. · elephant ivory",
            "desc": "A small ivory figurine used in the Bwami initiation — each iginga embodied a proverb the initiate had to memorize. Bwami is an ethical order: the higher the rank, the more elaborate the ivory.",
            "image": "https://openaccess-cdn.clevelandart.org/2005.3/2005.3_print.jpg",
            "year": 1850,
        },
    ],
    "mediterranean": [
        {
            "title": "Roman Cameo Glass: Head of Diana",
            "meta": "Roman Italy · 1st c. BCE–1st c. CE · cameo glass",
            "desc": "A sardonyx-glass cameo with a right-facing Diana — cameo glass imitated the carved layered stone of imperial workshops, letting non-elites wear the look in a ring.",
            "image": "https://openaccess-cdn.clevelandart.org/1965.465/1965.465_print.jpg",
            "year": -25,
        },
        {
            "title": "Roman Janiform Head Flask",
            "meta": "Roman Eastern Mediterranean · 2nd–4th c. CE · mold-blown glass",
            "desc": "A blown-glass flask with two faces back-to-back, filled with perfume or unguent — mold-blown in Syria and Palestine, where Roman workshops fed the empire's market in small luxury glass.",
            "image": "https://openaccess-cdn.clevelandart.org/1923.945/1923.945_print.jpg",
            "year": 100,
        },
        {
            "title": "Roman Millefiori Bowl",
            "meta": "Roman Italy · 1st c. CE · glass",
            "desc": "A bowl built from cross-sectioned glass canes fused together — the Roman \"thousand flowers\" technique, lost after antiquity and rediscovered in Renaissance Venice.",
            "image": "https://openaccess-cdn.clevelandart.org/1919.10/1919.10_print.jpg",
            "year": 1,
        },
        {
            "title": "Etruscan Mirror: Eos and Memnon",
            "meta": "Etruscan · c. 470 BCE · bronze",
            "desc": "A polished-bronze mirror back engraved with Eos carrying the dead body of her son Memnon — the Etruscans loved Greek myth but gave the figures Etruscan names: Thesan for Eos, Memnun for Memnon.",
            "image": "https://openaccess-cdn.clevelandart.org/1952.259/1952.259_print.jpg",
            "year": -470,
        },
        {
            "title": "Corinthian Bull-Shaped Aryballos",
            "meta": "Corinthian Greece · c. 600 BCE · ceramic",
            "desc": "An oil flask shaped as a bull, once filled with olive oil for the gymnasium — Corinth exported animal-shaped vessels across the Mediterranean in the orientalizing century.",
            "image": "https://openaccess-cdn.clevelandart.org/1979.3/1979.3_print.jpg",
            "year": -600,
        },
        {
            "title": "Late Roman Spoon with Saint Paul",
            "meta": "Late Roman · 4th c. CE · silver and niello",
            "desc": "A silver spoon inscribed with Paul in a victor's pose — by the 4th century Roman silversmiths were recasting saints as athletes of the faith, blending pagan and Christian at table.",
            "image": "https://openaccess-cdn.clevelandart.org/1964.39/1964.39_print.jpg",
            "year": 350,
        },
    ],
    "egypt-nubia": [
        {
            "title": "Coptic Curtain Panel with Merrymaking",
            "meta": "Coptic Egypt · 6th c. · linen and wool tapestry",
            "desc": "A tapestry-woven panel with dancers and drinkers among vines — Coptic Egypt decorated private houses with pagan-style merrymaking long after the Theodosian edicts had closed the temples.",
            "image": "https://openaccess-cdn.clevelandart.org/2000.5/2000.5_print.jpg",
            "year": 500,
        },
        {
            "title": "Coptic Virgin and Child Tapestry",
            "meta": "Coptic Egypt · 6th c. · wool tapestry",
            "desc": "A wool tapestry panel of the Virgin enthroned with Christ — one of the earliest surviving Virgin-and-Child images, woven at roughly the moment Byzantine painters were fixing the icon format at Sinai.",
            "image": "https://openaccess-cdn.clevelandart.org/1967.144/1967.144_print.jpg",
            "year": 500,
        },
        {
            "title": "Heart Scarab of Nefer",
            "meta": "New Kingdom · Dynasty 18 · c. 1500 BCE · graywacke",
            "desc": "A greywacke heart scarab, placed over the mummy's chest, with a Book of the Dead spell on its underside asking the owner's heart not to testify against him at judgment.",
            "image": "https://openaccess-cdn.clevelandart.org/1921.1030/1921.1030_print.jpg",
            "year": -1500,
        },
        {
            "title": "Saqqara Relief of Nyankhnesut",
            "meta": "Old Kingdom · Dynasty 6 · c. 2300 BCE · painted limestone",
            "desc": "A tomb relief of the 6th Dynasty official Nyankhnesut seated at an offering table — the convention locked in the Old Kingdom, looking forward to three millennia of imitation.",
            "image": "https://openaccess-cdn.clevelandart.org/1930.735/1930.735_print.jpg",
            "year": -2300,
        },
    ],
    "islamic-world": [
        {
            "title": "Iznik Tile Spandrel with Saz Sprays",
            "meta": "Ottoman Iznik · c. 1570 · fritware with underglaze",
            "desc": "A ceramic spandrel — the curving wedge above an arch — with cobalt tulips and saz leaves. Iznik in the 1570s was the workshop that tiled Süleymaniye in Istanbul and Selimiye in Edirne.",
            "image": "https://openaccess-cdn.clevelandart.org/2004.70/2004.70_print.jpg",
            "year": 1570,
        },
        {
            "title": "Iznik Dish with Artichokes",
            "meta": "Ottoman Iznik · c. 1540 · fritware",
            "desc": "A dish painted with heavy cobalt artichokes and vines — early Iznik still imitated the Ming blue-and-white that Ottoman merchants brought in from Chinese ports.",
            "image": "https://openaccess-cdn.clevelandart.org/1995.17/1995.17_print.jpg",
            "year": 1540,
        },
        {
            "title": "Qajar Wall Cover with Peacocks",
            "meta": "Qajar Iran · 19th c. · painted and printed silk",
            "desc": "A silk hanging hand-painted with peacocks and European-style portrait medallions — late Qajar taste blended Persian ornament with imported chromolithograph imagery.",
            "image": "https://openaccess-cdn.clevelandart.org/1916.1483/1916.1483_print.jpg",
            "year": 1850,
        },
        {
            "title": "Portrait of Raja Jagat Singh of Nurpur",
            "meta": "Mughal India · Bichitr · c. 1619",
            "desc": "A portrait by Bichitr of the Punjab Hills raja — a vassal ruler who would later rebel against Jahangir. Bichitr, signing his name in the lower margin, was Jahangir's most psychologically acute painter.",
            "image": "https://openaccess-cdn.clevelandart.org/2013.324/2013.324_print.jpg",
            "artist": "Bichitr",
            "year": 1619,
        },
        {
            "title": "Rustam Slays the White Div",
            "meta": "Shah Tahmasp Shahnameh · Safavid Tabriz · 1530s",
            "desc": "A leaf from Shah Tahmasp's Shahnameh: Rustam reaching into the cave to split the White Demon with a dagger. This manuscript was the grandest Persian painting ever made; Tahmasp later gave it to Sultan Selim II.",
            "image": "https://openaccess-cdn.clevelandart.org/1988.96.a/1988.96.a_print.jpg",
            "artist": "Abd al-Vahhab",
            "year": 1530,
        },
        {
            "title": "Nushirwan Listens to the Owls",
            "meta": "Safavid Qazvin · 1550s · illustration to Nizami's Khamsa",
            "desc": "King Anushirvan halts his ride to hear two owls debate — the moral: a bad ruler leaves so many ruined villages that the owls get rich on the dowries of their daughters.",
            "image": "https://openaccess-cdn.clevelandart.org/1944.487.a/1944.487.a_print.jpg",
            "year": 1555,
        },
        {
            "title": "Khujasta and the Parrot",
            "meta": "Mughal India · Akbar's Tutinameh · c. 1560",
            "desc": "The merchant's wife Khujasta about to slip out for a night with a lover; the parrot begins the first of seven nights of stalling tales to keep her home — Akbar's early masterpiece of narrative painting.",
            "image": "https://openaccess-cdn.clevelandart.org/1962.279.43.a/1962.279.43.a_print.jpg",
            "year": 1560,
        },
    ],
    "americas": [
        {
            "title": "Tlingit Chilkat Blanket",
            "meta": "Tlingit · Northwest Coast · late 19th c. · cedar bark and mountain goat",
            "desc": "A ceremonial dance robe of cedar bark and mountain-goat wool — Chilkat weaving draws its formline crest figures freehand rather than on a grid, almost unique among loom traditions.",
            "image": "https://openaccess-cdn.clevelandart.org/1981.69/1981.69_print.jpg",
            "year": 1880,
        },
        {
            "title": "Tlingit Totem Pole",
            "meta": "Tlingit · Northwest Coast · c. 1880 · carved and painted cedar",
            "desc": "A Tlingit cedar totem pole — not religion or writing but lineage heraldry, declaring a clan house's crest animals. Most surviving 19th-century poles were cut down and sold; few stand in place.",
            "image": "https://openaccess-cdn.clevelandart.org/1989.89/1989.89_print.jpg",
            "year": 1880,
        },
        {
            "title": "Calima Gold Pectoral",
            "meta": "Calima · Colombia · 1–800 CE · hammered gold",
            "desc": "A hammered-gold chest ornament worn across the collarbone at full width — Calima lords in the Cauca Valley dressed in pounded gold heavy enough to have been audible as they moved.",
            "image": "https://openaccess-cdn.clevelandart.org/2015.2/2015.2_print.jpg",
            "year": 100,
        },
        {
            "title": "Sinú Gold Bird Finial",
            "meta": "Sinú (Zenú) · Colombia · 5th–11th c. · cast gold",
            "desc": "A cast-gold finial shaped as a long-beaked bird — the Sinú crowned staffs and litter-poles with these, their lost-wax casting so refined the Spanish melted most of it down for bullion.",
            "image": "https://openaccess-cdn.clevelandart.org/2015.4/2015.4_print.jpg",
            "year": 400,
        },
        {
            "title": "Aztec Tlaloc",
            "meta": "Aztec · Central Mexico · 13th–16th c. · stone",
            "desc": "The rain god with his goggle eyes and fanged mouth — Tenochtitlán sat on a lake-surrounded island, and the Aztecs owed their two harvests a year to Tlaloc and his dwarf rain-helpers.",
            "image": "https://openaccess-cdn.clevelandart.org/1966.361/1966.361_print.jpg",
            "year": 1300,
        },
        {
            "title": "Mimbres Bowl",
            "meta": "Mimbres · New Mexico · c. 1000–1150 · painted earthenware",
            "desc": "A black-on-white bowl buried with the dead, its base punctured to release the spirit. The Mimbres abandoned their valley around 1150 and the painting tradition stopped with them.",
            "image": "https://openaccess-cdn.clevelandart.org/1973.165/1973.165_print.jpg",
            "year": 1050,
        },
    ],
    "southeast-asia-oceania": [
        {
            "title": "Khmer Durga Slaying the Buffalo Demon",
            "meta": "Khmer · Koh Ker · 10th c. · bronze",
            "desc": "Durga pressing her trident into the buffalo-demon Mahishasura — cast at Koh Ker, the sandstone capital Jayavarman IV built when he split from Angkor for seventeen years before the court returned.",
            "image": "https://openaccess-cdn.clevelandart.org/1996.27/1996.27_print.jpg",
            "year": 950,
        },
        {
            "title": "Hevajra Bronze",
            "meta": "Khmer · NE Thailand · c. 1200 · bronze",
            "desc": "An eight-armed, four-headed dancing Hevajra — the esoteric Buddhist deity Jayavarman VII adopted when Angkor turned Mahayana in the twilight of the empire.",
            "image": "https://openaccess-cdn.clevelandart.org/2011.143/2011.143_print.jpg",
            "year": 1200,
        },
        {
            "title": "Angkor Wat Naga Palanquin Finial",
            "meta": "Khmer · Angkor Wat period · 12th c. · bronze",
            "desc": "A multi-headed cobra-king finial that crowned a palanquin pole — Vasuki coiling up to protect the canopy under which a noble rode through the temple courts.",
            "image": "https://openaccess-cdn.clevelandart.org/1987.14.2/1987.14.2_print.jpg",
            "year": 1150,
        },
        {
            "title": "Baphuon Kneeling Male Figure",
            "meta": "Khmer · Baphuon period · 11th c. · bronze",
            "desc": "A bronze figure kneeling in añjali, the gesture of adoration — a portrait of a minister or king. Baphuon-period metalwork carried Khmer bronze to its height just before Angkor Wat.",
            "image": "https://openaccess-cdn.clevelandart.org/1978.8/1978.8_print.jpg",
            "year": 1050,
        },
        {
            "title": "Pyu Standing Buddha",
            "meta": "Burma · Pyu period · 9th c. · kaolin",
            "desc": "A small kaolin-clay Buddha made for a Pyu-period shrine in pre-Pagan Burma — before the Bamar conquest and the Theravada consolidation under King Anawrahta in the 11th century.",
            "image": "https://openaccess-cdn.clevelandart.org/1973.159/1973.159_print.jpg",
            "year": 850,
        },
        {
            "title": "Mandaya Dagmay Ikat",
            "meta": "Mandaya · Mindanao · early 20th c. · hemp, warp-ikat",
            "desc": "A hemp dagmay cloth woven by the Mandaya of southern Mindanao — the warp-ikat patterns encode ancestor-spirit figures, and a woman's weaving skill shaped her marriage prospects.",
            "image": "https://openaccess-cdn.clevelandart.org/1917.748.b/1917.748.b_print.jpg",
            "year": 1900,
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
                print(f"  skip: {slug} / {w['title']}")
                continue
            data["works"].append(w)
            added += 1
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"  {slug}: +{added} (now {len(data['works'])})")
        added_total += added
    print(f"\nAdded {added_total} works.")


if __name__ == "__main__":
    main()
