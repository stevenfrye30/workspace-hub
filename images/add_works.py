#!/usr/bin/env python3
"""Push the gallery toward 550."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"

NEW_WORKS: dict[str, list[dict]] = {
    "africa": [
        {
            "title": "Cairo Citadel",
            "meta": "Ayyubid → Ottoman · 1176 onward · Egypt",
            "desc": "Saladin's fortress above old Cairo, topped centuries later by the Mosque of Muhammad Ali with its tall twin minarets — a silhouette that defines the skyline.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Flickr_-_HuTect_ShOts_-_Citadel_of_Salah_El.Din_and_Masjid_Muhammad_Ali_%D9%82%D9%84%D8%B9%D8%A9_%D8%B5%D9%84%D8%A7%D8%AD_%D8%A7%D9%84%D8%AF%D9%8A%D9%86_%D8%A7%D9%84%D8%A3%D9%8A%D9%88%D8%A8%D9%8A_%D9%88%D9%85%D8%B3%D8%AC%D8%AF_%D9%85%D8%AD%D9%85%D8%AF_%D8%B9%D9%84%D9%8A_-_Cairo_-_Egypt_-_17_04_2010_%284%29.jpg/960px-thumbnail.jpg",
            "year": 1176,
        },
        {
            "title": "Osun-Osogbo Sacred Grove",
            "meta": "Yoruba · 20th-c. revival of traditional · Nigeria",
            "desc": "A forest along the Oshun River filled with sculptures revived by the Austrian-Yoruba artist Susanne Wenger and local carvers — the last surviving intact sacred grove of the Yoruba.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Osun_groove_Osogbo.jpg/960px-Osun_groove_Osogbo.jpg",
            "year": 1960,
        },
        {
            "title": "Cape Coast Castle",
            "meta": "Colonial fortification · 1653 onward · Ghana",
            "desc": "A whitewashed castle on the Gulf of Guinea used for the Atlantic slave trade — enslaved Africans passed through its \"Door of No Return.\" Now a museum, with whitewash still yearly.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Cape_Coast_Castle%2C_Cape_Coast%2C_Ghana.JPG/960px-Cape_Coast_Castle%2C_Cape_Coast%2C_Ghana.JPG",
            "year": 1653,
        },
        {
            "title": "Swahili Stone Towns",
            "meta": "Swahili coast · 12th–19th c. · East Africa",
            "desc": "Coral-stone trading towns — Lamu, Pate, Kilwa — with carved wooden doors studded in brass, Indian Ocean dhows in their harbors, and mosques whose minarets face inland.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/LamuIsland-PortAuthority.jpg/960px-LamuIsland-PortAuthority.jpg",
            "year": 1500,
        },
    ],
    "egypt-nubia": [
        {
            "title": "Gayer-Anderson Cat",
            "meta": "Late Period · c. 600 BCE",
            "desc": "A hollow-cast bronze cat in the form of the goddess Bastet, with gold earrings and nose ring. Slightly battered but uncannily alive — one of the most reproduced pieces in the British Museum.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/British_Museum_Egypt_101-black.jpg/960px-British_Museum_Egypt_101-black.jpg",
            "year": -600,
        },
        {
            "title": "Deir el-Medina",
            "meta": "New Kingdom · c. 1550–1080 BCE",
            "desc": "The workers' village for those who built the royal tombs. Its own tombs are painted with a precision surprising for common craftsmen — because the craftsmen were the painters of the Valley of the Kings.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Deir_el-Medina%2C_Luxor%2C_Egipto%2C_2022-04-03%2C_DD_18.jpg/960px-Deir_el-Medina%2C_Luxor%2C_Egipto%2C_2022-04-03%2C_DD_18.jpg",
            "year": -1400,
        },
        {
            "title": "Temple of Hibis",
            "meta": "Late Period · 6th c. BCE · Kharga Oasis",
            "desc": "The largest surviving temple of the Persian period in Egypt. Carved in sandstone in the middle of a desert oasis; its roof blocks depict 700 Egyptian deities.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/7/77/HibisComplete.jpg",
            "year": -520,
        },
        {
            "title": "Memphis (Egypt)",
            "meta": "Early Dynastic onward · c. 3100 BCE · Lower Egypt",
            "desc": "The first capital of unified Egypt, sacred to Ptah. What survives today is ruins in a palm grove — a colossal reclining statue of Ramesses II, sphinxes, embalmed Apis bulls.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Memphis200401.JPG/960px-Memphis200401.JPG",
            "year": -3100,
        },
        {
            "title": "Temple of Amun at Jebel Barkal",
            "meta": "Kushite · c. 1450 BCE onward · Sudan",
            "desc": "Built by Thutmose III below a sandstone butte the Nubians believed Amun lived inside. Reused by Kushite pharaohs who conquered Egypt from here in the 25th Dynasty.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Amun_Tempel_Barkal_SW.jpg/960px-Amun_Tempel_Barkal_SW.jpg",
            "year": -1450,
        },
    ],
    "mesopotamia-persia": [
        {
            "title": "Kish Tablet",
            "meta": "Early Sumerian · c. 3200 BCE",
            "desc": "A small limestone tablet from Kish covered in proto-cuneiform signs — possibly the earliest known writing. Accounts of barley, fish, and a threshing sled.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/a/a9/Tableta_con_trillo.png",
            "year": -3200,
        },
        {
            "title": "Sumerian Libation Plaque",
            "meta": "Early Dynastic · c. 2500 BCE · Ur",
            "desc": "A perforated stone plaque once hung in a temple. The top register shows a naked priest pouring an offering to a seated god; the lower register, worshipers bringing livestock.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Wall_plaque_showing_libation_scene_from_Ur%2C_Iraq%2C_2500_BCE._British_Museum_%28adjusted_for_perspective%29.jpg/960px-Wall_plaque_showing_libation_scene_from_Ur%2C_Iraq%2C_2500_BCE._British_Museum_%28adjusted_for_perspective%29.jpg",
            "year": -2500,
        },
    ],
    "mediterranean": [
        {
            "title": "Temple of Aphaia",
            "meta": "Late Archaic Greek · c. 500 BCE · Aegina",
            "desc": "A limestone temple whose pedimental sculptures, now in Munich, capture the hinge between Archaic stiffness and Classical naturalism — look at the east and west together to see a style changing.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Aegina_-_Temple_of_Aphaia_03.jpg/960px-Aegina_-_Temple_of_Aphaia_03.jpg",
            "year": -500,
        },
        {
            "title": "Temple of Poseidon at Sounion",
            "meta": "Classical Greek · c. 440 BCE · Attica",
            "desc": "White marble columns on a cape where the sea drops 60 meters away on three sides. Byron carved his name into one of the columns in 1810.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/Greece_Cape_Sounion_BW_2017-10-09_10-12-43.jpg/960px-Greece_Cape_Sounion_BW_2017-10-09_10-12-43.jpg",
            "year": -440,
        },
        {
            "title": "Temple of Zeus at Olympia",
            "meta": "Classical Greek · c. 470 BCE",
            "desc": "Once held the chryselephantine Zeus — one of the Seven Wonders of the ancient world, carved by Phidias. The temple fell in an earthquake; the Zeus was hauled to Constantinople and burned.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Olympia-ZeusTempelRestoration.jpg/960px-Olympia-ZeusTempelRestoration.jpg",
            "year": -470,
        },
        {
            "title": "Hagia Triada Sarcophagus",
            "meta": "Late Minoan · c. 1400 BCE · Crete",
            "desc": "A painted limestone sarcophagus showing funeral rites on all four sides — a bull sacrifice, women carrying pails of blood, the deceased receiving offerings. Our clearest window onto Minoan ritual.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/49/Sarcophagus_archmus_Heraklion.jpg/960px-Sarcophagus_archmus_Heraklion.jpg",
            "year": -1400,
        },
        {
            "title": "Roman Forum",
            "meta": "Roman Republic → Imperial · 7th c. BCE – 4th c. CE",
            "desc": "The civic heart of ancient Rome — law courts, speaker's platforms, temples, triumphal arches, all crammed into a low strip between the Palatine and Capitoline hills.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Foro_Romano_Musei_Capitolini_Roma.jpg/960px-Foro_Romano_Musei_Capitolini_Roma.jpg",
            "year": -500,
        },
        {
            "title": "Obelisk of Theodosius",
            "meta": "Egyptian carved 15th c. BCE, re-erected 390 CE · Istanbul",
            "desc": "An Egyptian obelisk Thutmose III set up at Karnak; Theodosius hauled it to Constantinople and planted it on a marble base carved with Byzantine court scenes. Two monuments in one.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Obelisk_of_Theodosius_I.jpg/960px-Obelisk_of_Theodosius_I.jpg",
            "year": -1450,
        },
    ],
    "europe": [
        {
            "title": "Bacchus",
            "meta": "Baroque · c. 1596 · Florence",
            "desc": "Caravaggio's boyish, tipsy Bacchus — fingernails dirty, a decaying fruit basket in the foreground. Lost for three centuries, rediscovered in a Uffizi storeroom in 1913.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Baco%2C_por_Caravaggio.jpg/960px-Baco%2C_por_Caravaggio.jpg",
            "artist": "Caravaggio",
            "year": 1596,
        },
        {
            "title": "The Gleaners",
            "meta": "Realism · 1857",
            "desc": "Three peasant women stoop to pick up leftover grain after the harvest. The wealthy hated it — it looked like socialism. Millet painted rural labor as dignified, not picturesque.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Jean-Fran%C3%A7ois_Millet_-_Gleaners_-_Google_Art_Project_2.jpg/960px-Jean-Fran%C3%A7ois_Millet_-_Gleaners_-_Google_Art_Project_2.jpg",
            "artist": "Jean-François Millet",
            "year": 1857,
        },
        {
            "title": "Westminster Abbey",
            "meta": "English Gothic · 1245 onward · London",
            "desc": "Coronation church of English monarchs since 1066; also a vast, crowded graveyard — Newton, Darwin, Stephen Hawking. Poets' Corner adds Chaucer, Dickens, T. S. Eliot.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Westminster_Abbey_St_Peter.jpg/960px-Westminster_Abbey_St_Peter.jpg",
            "year": 1245,
        },
        {
            "title": "Reims Cathedral",
            "meta": "High Gothic · 1211–1275 · France",
            "desc": "Coronation church of the kings of France. Shelled for five years in World War I; its sculptures, including the famous Smiling Angel, shattered and then were painstakingly reassembled.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/70/Exterior_view_of_the_west_facade_of_Notre-Dame_Cathedral_in_Reims.jpg/960px-Exterior_view_of_the_west_facade_of_Notre-Dame_Cathedral_in_Reims.jpg",
            "year": 1245,
        },
        {
            "title": "The Dance",
            "meta": "Fauvism · 1909–1910",
            "desc": "Five red figures hold hands in a frenzied ring against blue sky and green earth. Matisse called the composition \"the highest point of the story\" — the first great Modernist painting of pure color.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/a/a7/Matissedance.jpg",
            "artist": "Henri Matisse",
            "year": 1910,
        },
    ],
    "islamic-world": [
        {
            "title": "Agra Fort",
            "meta": "Mughal · 1565–1573 · Uttar Pradesh",
            "desc": "Red sandstone fort rebuilt by Akbar, later inner palaces added by Shah Jahan. Imprisoned here by his own son Aurangzeb, Shah Jahan could see the Taj Mahal across the river until his death.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Agra_03-2016_10_Agra_Fort.jpg/960px-Agra_03-2016_10_Agra_Fort.jpg",
            "year": 1570,
        },
        {
            "title": "Ali Qapu",
            "meta": "Safavid · early 17th c. · Isfahan",
            "desc": "Six-story royal pavilion overlooking Naqsh-e Jahan Square. Its upper music room has plaster cut into silhouettes of jars and vases — both ornament and acoustic resonator.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/%C4%80l%C4%AB_Q%C4%81p%C5%AB_in_golden_time.jpg/960px-%C4%80l%C4%AB_Q%C4%81p%C5%AB_in_golden_time.jpg",
            "year": 1600,
        },
        {
            "title": "Chehel Sotoun",
            "meta": "Safavid · 1647 · Isfahan",
            "desc": "A pavilion of \"forty columns\" — twenty real wooden ones plus their reflections in the long rectangular pool. Interior halls are painted with the Shah's battles and banquets.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Chehel_Sotoon.jpg/960px-Chehel_Sotoon.jpg",
            "year": 1647,
        },
        {
            "title": "Sheikh Lotfollah Mosque",
            "meta": "Safavid · 1603–1619 · Isfahan",
            "desc": "The private royal chapel on the east side of Naqsh-e Jahan Square. No minarets, no courtyard — just a single domed hall whose tilework, buff and turquoise, changes color with the sun.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Sheikh_Lotfallah_Esfahan.JPG/960px-Sheikh_Lotfallah_Esfahan.JPG",
            "year": 1615,
        },
    ],
    "south-asia": [
        {
            "title": "Modhera Sun Temple",
            "meta": "Chaulukya dynasty · 1026 · Gujarat",
            "desc": "Temple to Surya oriented so the first rays of the equinox sun strike the inner sanctum. A cistern called Ramakunda in front holds over a hundred miniature shrines along its steps.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/Surya_mandhir.jpg/960px-Surya_mandhir.jpg",
            "year": 1026,
        },
        {
            "title": "Chand Baori",
            "meta": "Gurjara-Pratihara · 9th c. · Rajasthan",
            "desc": "A thirteen-story stepwell carved with 3,500 narrow steps into dizzying geometric patterns down its walls. One of the oldest and deepest stepwells in India.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Chand_Baori_perspective_panorama_%28July_2022%29.jpg/960px-Chand_Baori_perspective_panorama_%28July_2022%29.jpg",
            "year": 850,
        },
        {
            "title": "Somnath Temple",
            "meta": "Chaulukya → rebuilt 1951 · Gujarat",
            "desc": "A Hindu pilgrimage site destroyed and rebuilt seven times — plundered most famously by Mahmud of Ghazni in 1025. The current temple was built after Indian independence, at the sea's edge.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Somanath_mandir_%28cropped%29.jpg/960px-Somanath_mandir_%28cropped%29.jpg",
            "year": 1951,
        },
        {
            "title": "Rani ki Vav",
            "meta": "Chaulukya dynasty · 11th c. · Gujarat",
            "desc": "A subterranean stepwell dug by Queen Udayamati for her husband. Seven levels down, 500 sculptures of Vishnu avatars and apsaras. Silted over by the Saraswati; rediscovered in the 1980s.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Rani_ki_vav_02.jpg/960px-Rani_ki_vav_02.jpg",
            "year": 1080,
        },
        {
            "title": "Mysore Palace",
            "meta": "Indo-Saracenic · 1912 · Karnataka",
            "desc": "The current incarnation — fourth to stand on the site — is a wedding cake of Hindu, Mughal, Rajput, and Gothic elements. Lit up nightly by nearly a hundred thousand bulbs.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Mysore_Palace_Morning.jpg/960px-Mysore_Palace_Morning.jpg",
            "year": 1912,
        },
        {
            "title": "Mehrangarh Fort",
            "meta": "Rathore dynasty · 1459 onward · Jodhpur",
            "desc": "A hundred-meter cliff-top fort in the Blue City of Jodhpur. Its walls still bear handprints of the widows of maharajas who threw themselves on the pyre in the medieval practice of sati.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Mehrangarh_Fort_sanhita.jpg/960px-Mehrangarh_Fort_sanhita.jpg",
            "year": 1460,
        },
    ],
    "east-asia": [
        {
            "title": "Streams and Mountains with a Clear Distant View",
            "meta": "Southern Song · Xia Gui · early 13th c.",
            "desc": "A long ink handscroll in the \"one-corner\" style — only a fraction of the silk is painted, leaving vast voids for the viewer to read as mist and distance. A founding image of Chinese minimalism.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Xia_Gui%2C_Streams_and_Mountains_with_a_Clear_Distant_View%2C_detail.jpg/960px-Xia_Gui%2C_Streams_and_Mountains_with_a_Clear_Distant_View%2C_detail.jpg",
            "artist": "Xia Gui",
            "year": 1210,
        },
        {
            "title": "Spring Outing of the Tang Court",
            "meta": "Tang Dynasty · attributed to Zhang Xuan · 8th c.",
            "desc": "A later copy of a lost Zhang Xuan handscroll: the imperial court rides out on a spring morning in a tight file of horses. The women in the vanguard seem to pull the viewer along.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Spring_Outing_of_the_Tang_Court.jpg/960px-Spring_Outing_of_the_Tang_Court.jpg",
            "artist": "Zhang Xuan",
            "year": 750,
        },
        {
            "title": "Ink Landscape (Self-Portrait)",
            "meta": "Qing · Shitao · late 17th c.",
            "desc": "Shitao paints himself sitting on a rock, brush poised, surrounded by hills he is still deciding to render. A Ming prince turned Buddhist monk; his theoretical writings on painting are still studied.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Shitao-autoportrait.jpg/960px-Shitao-autoportrait.jpg",
            "artist": "Shitao",
            "year": 1690,
        },
        {
            "title": "Qiu Ying Paintings",
            "meta": "Ming · Qiu Ying · 1494–1552",
            "desc": "One of the \"Four Masters of the Ming Dynasty.\" Rose from lacquer-worker to court painter. His handscrolls of palace scenes and mountain recluses are among the most copied in Chinese art history.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Qiu_Ying_-_%E4%BB%87%E8%8B%B1%EF%BC%881494-1552%29.jpg/960px-Qiu_Ying_-_%E4%BB%87%E8%8B%B1%EF%BC%881494-1552%29.jpg",
            "artist": "Qiu Ying",
            "year": 1530,
        },
        {
            "title": "Tale of Genji Scroll",
            "meta": "Late Heian · early 12th c. · Japan",
            "desc": "The oldest illustrated version of Murasaki Shikibu's Genji. The \"blown-off roof\" perspective looks down into private chambers; faces are reduced to lines, clothing is everything.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/Genji_emaki_azumaya.jpg/960px-Genji_emaki_azumaya.jpg",
            "year": 1120,
        },
        {
            "title": "Huang Quan Bird Painting",
            "meta": "Five Dynasties · Huang Quan · c. 950 CE",
            "desc": "Meticulously observed birds, insects, and turtles. Huang Quan was a palace painter in Sichuan; his \"sketches from life\" became the model for Northern Song nature painting.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Huang-Quan-Xie-sheng-zhen-qin-tu.jpg/960px-Huang-Quan-Xie-sheng-zhen-qin-tu.jpg",
            "artist": "Huang Quan",
            "year": 950,
        },
        {
            "title": "Nishiki-e (Brocade Prints)",
            "meta": "Edo Japan · 1765 onward",
            "desc": "Multi-color woodblock prints developed by Suzuki Harunobu in 1765 — the first polychrome ukiyo-e. Enabled Utamaro, Hokusai, Hiroshige to work in full color.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/3/34/Nishikie.jpg",
            "year": 1765,
        },
    ],
    "southeast-asia-oceania": [
        {
            "title": "Pura Tanah Lot",
            "meta": "Balinese Hindu · 16th c. · Bali",
            "desc": "A Hindu sea temple perched on a rock pounded by surf. At high tide it becomes an island; legend says sea snakes guard it from the base.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/TanahLot_2014.JPG/960px-TanahLot_2014.JPG",
            "year": 1550,
        },
        {
            "title": "Tau Tau",
            "meta": "Toraja · Sulawesi, Indonesia",
            "desc": "Carved wooden effigies of the dead, placed in cliff-face galleries above Toraja villages. Each tau tau faces outward and is redressed periodically by descendants; some are centuries old.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/a/a4/COLLECTIE_TROPENMUSEUM_Verschillende_tau-tau_van_een_overleden_vorst_TMnr_20000489.jpg",
            "year": 1850,
        },
        {
            "title": "Polynesian Tiki",
            "meta": "Polynesian · pre-contact · Pacific",
            "desc": "Stone or wooden carvings of deified ancestors, dotting the Marquesas, Tahiti, and Hawaii. Variants spread as far as Easter Island's moai.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/8/8e/Tiki1905.jpg",
            "year": 1500,
        },
        {
            "title": "Malangan Carvings",
            "meta": "New Ireland · 19th c. onward · Papua New Guinea",
            "desc": "Elaborately painted wooden figures carved for a single memorial ceremony, then deliberately destroyed or allowed to rot. Their knowledge was owned as intellectual property; only certain carvers could make certain forms.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Malanggan-Masken_Berlin-Dahlem.jpg/960px-Malanggan-Masken_Berlin-Dahlem.jpg",
            "year": 1880,
        },
        {
            "title": "Wat Xieng Thong",
            "meta": "Lan Xang · 1559–1560 · Luang Prabang",
            "desc": "The royal temple of the Lao kingdom. Its sim has a sweeping tiered roof that nearly touches the ground; interior walls are covered in gilded-black lacquer tell-tales.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Temple_Wat_Xieng_Thong_-_Luang_Prabang_-_Laos.jpg/960px-Temple_Wat_Xieng_Thong_-_Luang_Prabang_-_Laos.jpg",
            "year": 1560,
        },
    ],
    "americas": [
        {
            "title": "Muisca Raft (El Dorado)",
            "meta": "Muisca · 600–1600 CE · Colombia",
            "desc": "A miniature gold raft showing the chief and his attendants during the initiation ritual in Lake Guatavita — the story that grew into the European myth of El Dorado.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Gold_Museum%2C_Bogota_%2836145671394%29.jpg/960px-Gold_Museum%2C_Bogota_%2836145671394%29.jpg",
            "year": 1300,
        },
        {
            "title": "Chimor",
            "meta": "Chimú · 900–1470 CE · Northern Peru",
            "desc": "Kingdom that ruled the Peruvian coast before the Inca conquered it. Its capital Chan Chan is the largest adobe city ever built; gold, silver, and feather work survive in elite tombs.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/a/a5/Photomontage_Chimu_Culture.jpg",
            "year": 1200,
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
