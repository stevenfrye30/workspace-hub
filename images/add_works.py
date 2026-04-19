#!/usr/bin/env python3
"""Append a curated batch of new works to data/*.json.

Replace NEW_WORKS with your batch and run. Optional 'artist' field seeds a
future artist-view — omit it for anonymous / collective / architectural works.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"

NEW_WORKS: dict[str, list[dict]] = {
    "africa": [
        {
            "title": "Asante Jewelry",
            "meta": "Akan / Asante · 19th c. · Ghana",
            "desc": "Gold jewelry for the chief and his court — beads, pectorals, rings cast with the same lost-wax technique as the goldweights. Sumptuary law regulated who could wear what.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Guinea_Coast%2C_Ghana%2C_Asante_people%2C_19th_century_-_Jewelry_-_1935.310_-_Cleveland_Museum_of_Art.tif/lossy-page1-960px-Guinea_Coast%2C_Ghana%2C_Asante_people%2C_19th_century_-_Jewelry_-_1935.310_-_Cleveland_Museum_of_Art.tif.jpg",
        },
        {
            "title": "Ethiopian Processional Cross",
            "meta": "Ethiopian Orthodox · 12th c. onward · Ethiopia",
            "desc": "Hand-held metal crosses carried at the front of church processions. Each is unique — geometries nested inside geometries, hammered out by a parish smith.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/ET_Axum_asv2018-01_img03_Abba_Pentalewon.jpg/960px-ET_Axum_asv2018-01_img03_Abba_Pentalewon.jpg",
        },
    ],
    "americas": [
        {
            "title": "Ghost Dance Shirt",
            "meta": "Lakota · 1890 · Great Plains",
            "desc": "Hide shirts painted with stars and eagles, worn in the Ghost Dance — believed to turn aside bullets. Shirts were collected from the dead at Wounded Knee.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/Ghost_Dance_shirt.jpg/960px-Ghost_Dance_shirt.jpg",
        },
    ],
}


def main() -> None:
    added_total = 0
    for slug, new_works in NEW_WORKS.items():
        path = DATA / f"{slug}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["works"].extend(new_works)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"  {slug}: +{len(new_works)} (now {len(data['works'])})")
        added_total += len(new_works)
    print(f"\nAdded {added_total} works. Run `python build.py` to regenerate HTML.")


if __name__ == "__main__":
    main()
