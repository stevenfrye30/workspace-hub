#!/usr/bin/env python3
"""One-off: add the `artist` field to earlier works that should have one.

Maps exact work title → artist. Idempotent (skips works that already carry an
artist). Run once; re-runs are harmless.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"

# title → artist name. Use the title as it appears in data/*.json.
BACKFILL: dict[str, str] = {
    # Europe
    "Sistine Chapel Ceiling": "Michelangelo",
    "The Night Watch": "Rembrandt",
    "Las Meninas": "Diego Velázquez",
    "Girl with a Pearl Earring": "Johannes Vermeer",
    "The Starry Night": "Vincent van Gogh",
    "The Scream": "Edvard Munch",
    "The Arnolfini Portrait": "Jan van Eyck",
    "The School of Athens": "Raphael",
    "David": "Michelangelo",
    "The Last Supper": "Leonardo da Vinci",
    "The Garden of Earthly Delights": "Hieronymus Bosch",
    "The Birth of Venus": "Sandro Botticelli",
    "Pietà": "Michelangelo",
    "A Sunday on La Grande Jatte": "Georges Seurat",
    "Water Lilies": "Claude Monet",
    "The Thinker": "Auguste Rodin",
    "Primavera": "Sandro Botticelli",
    "The Isenheim Altarpiece": "Matthias Grünewald",
    "Ghent Altarpiece": "Jan van Eyck",

    # East Asia
    "The Great Wave off Kanagawa": "Katsushika Hokusai",
    "Along the River During Qingming": "Zhang Zeduan",
    "Early Spring": "Guo Xi",

    # Mediterranean — Roman copies attributed to original Greek sculptors
    "Discobolus": "Myron",
    "Doryphoros": "Polykleitos",
    "Apoxyomenos": "Lysippos",
    "Aphrodite of Knidos": "Praxiteles",
}


def main() -> None:
    touched = 0
    for path in sorted(DATA.glob("*.json")):
        if path.name == "regions.json":
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        changed = False
        for w in data.get("works", []):
            if "artist" in w and w["artist"]:
                continue
            artist = BACKFILL.get(w["title"])
            if artist:
                w["artist"] = artist
                changed = True
                touched += 1
                print(f"  {path.stem}: {w['title']} -> {artist}")
        if changed:
            path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
    print(f"\nBackfilled {touched} works. Run `python build.py` to regenerate.")


if __name__ == "__main__":
    main()
