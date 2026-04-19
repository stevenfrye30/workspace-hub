#!/usr/bin/env python3
"""Append a curated batch of new works to data/*.json.

Replace NEW_WORKS with your batch and run. Optional 'artist' field seeds the
artist view — omit for anonymous / collective / architectural works.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"

NEW_WORKS: dict[str, list[dict]] = {
    "europe": [
        {
            "title": "Mona Lisa",
            "meta": "High Renaissance · c. 1503–1519 · Louvre, Paris",
            "desc": "Probably Lisa Gherardini, wife of a Florentine merchant. Leonardo carried it with him for years, reworking it endlessly. Her fame owes as much to her 1911 theft as to her painter.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/960px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg",
            "artist": "Leonardo da Vinci",
        },
        {
            "title": "Liberty Leading the People",
            "meta": "French Romanticism · 1830 · Louvre, Paris",
            "desc": "Painted after the July Revolution that overthrew Charles X. Liberty strides over the barricades, bare-breasted, bayonet and tricolor raised. The boy with pistols later became Hugo's Gavroche.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/La_Libert%C3%A9_guidant_le_peuple_-_Eug%C3%A8ne_Delacroix_-_Mus%C3%A9e_du_Louvre_Peintures_RF_129_-_apr%C3%A8s_restauration_2024.jpg/960px-La_Libert%C3%A9_guidant_le_peuple_-_Eug%C3%A8ne_Delacroix_-_Mus%C3%A9e_du_Louvre_Peintures_RF_129_-_apr%C3%A8s_restauration_2024.jpg",
            "artist": "Eugène Delacroix",
        },
        {
            "title": "The Raft of the Medusa",
            "meta": "French Romanticism · 1818–1819 · Louvre, Paris",
            "desc": "A real recent disaster: 147 men cut loose on a raft off Senegal after the captain took the lifeboats. Fifteen survived. Géricault visited morgues and built a model in his studio.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/JEAN_LOUIS_TH%C3%89ODORE_G%C3%89RICAULT_-_La_Balsa_de_la_Medusa_%28Museo_del_Louvre%2C_1818-19%29.jpg/960px-JEAN_LOUIS_TH%C3%89ODORE_G%C3%89RICAULT_-_La_Balsa_de_la_Medusa_%28Museo_del_Louvre%2C_1818-19%29.jpg",
            "artist": "Théodore Géricault",
        },
        {
            "title": "The Coronation of Napoleon",
            "meta": "French Neoclassicism · 1805–1807 · Louvre, Paris",
            "desc": "Nearly ten meters wide. Napoleon, having just placed the crown on his own head, is about to crown Joséphine. David inserted Napoleon's mother in the grandstand though she refused to attend.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Jacques-Louis_David_-_The_Coronation_of_Napoleon_%281805-1807%29.jpg/960px-Jacques-Louis_David_-_The_Coronation_of_Napoleon_%281805-1807%29.jpg",
            "artist": "Jacques-Louis David",
        },
        {
            "title": "The Wedding at Cana",
            "meta": "Venetian Renaissance · 1563 · Louvre, Paris",
            "desc": "The largest painting in the Louvre at seventy square meters. Painted for a Venetian refectory; Napoleon's troops cut it in half in 1797 to ship it to France.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Paolo_Veronese_008.jpg/960px-Paolo_Veronese_008.jpg",
            "artist": "Paolo Veronese",
        },
        {
            "title": "The Lacemaker",
            "meta": "Dutch Golden Age · c. 1669–1671 · Louvre, Paris",
            "desc": "Only ten inches tall. A girl bent over her bobbins in concentrated silence — Vermeer's smallest canvas and one of his most intense studies of attention.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/03/Johannes_Vermeer_-_The_lacemaker_%28c.1669-1671%29.jpg/960px-Johannes_Vermeer_-_The_lacemaker_%28c.1669-1671%29.jpg",
            "artist": "Johannes Vermeer",
        },
        {
            "title": "Psyche Revived by Cupid's Kiss",
            "meta": "Neoclassical · 1793 · Louvre, Paris",
            "desc": "Canova's marble of the moment Cupid wakes Psyche with a kiss. Designed to be circled — every angle offers a different composition.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/0_Psych%C3%A9_ranim%C3%A9e_par_le_baiser_de_l%27Amour_-_Canova_-_Louvre_1.JPG/960px-0_Psych%C3%A9_ranim%C3%A9e_par_le_baiser_de_l%27Amour_-_Canova_-_Louvre_1.JPG",
            "artist": "Antonio Canova",
        },
        {
            "title": "La Grande Odalisque",
            "meta": "French Neoclassicism · 1814 · Louvre, Paris",
            "desc": "A concubine reclines on impossibly long, boneless anatomy. Critics counted extra vertebrae; Ingres was not interested in bones — he was interested in line.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/df/La_grande_odalisque_-_Jean-Auguste_Dominique_Ingres_-_Mus%C3%A9e_du_Louvre_Peintures_RF_1158.jpg/960px-La_grande_odalisque_-_Jean-Auguste_Dominique_Ingres_-_Mus%C3%A9e_du_Louvre_Peintures_RF_1158.jpg",
            "artist": "Jean-Auguste-Dominique Ingres",
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
