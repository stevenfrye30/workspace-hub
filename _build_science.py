#!/usr/bin/env python3
"""Build the static `science/` subsite.

Reads live data from the class-notes Flask project and dumps two JSON files:
  - science/data/glossary.json  (2,039 entries from courses/Resources/_Glossary/*.md)
  - science/data/clusters.json  (CONCEPT_CLUSTERS, lightly trimmed)

The HTML pages in science/ fetch those JSON files at runtime, so no re-deploy
is needed unless you want fresh content.
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CLASS_NOTES = os.path.normpath(os.path.join(HERE, "..", "projects", "class notes"))
GLOSSARY_DIR = os.path.join(CLASS_NOTES, "courses", "Resources", "_Glossary")
OUT_DIR = os.path.join(HERE, "science", "data")

# Filenames -> declared Subject for display
GLOSSARY_FILES = {
    "Analytical & Math.md": "Chemistry (Analytical & Math)",
    "Cell Biology.md": "Biology (Cell Biology)",
    "Chemistry.md": "Chemistry",
    "Genetics.md": "Biology (Genetics)",
    "Immunology.md": "Biology (Immunology)",
}


ENTRY_HEADING_RE = re.compile(r"^### (.+?)\s*$")
CATEGORY_HEADING_RE = re.compile(r"^## (.+?)\s*$")
FIELD_RE = re.compile(r"^-\s+\*\*([^*]+?):\*\*\s*(.*)$")


def parse_glossary(path: str, file_label: str, subject_default: str):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    entries = []
    current_category = None
    current = None

    def finalize():
        if current and current.get("term"):
            entries.append(current)

    for line in lines:
        cat_m = CATEGORY_HEADING_RE.match(line)
        if cat_m:
            finalize()
            current = None
            current_category = cat_m.group(1).strip()
            continue
        ent_m = ENTRY_HEADING_RE.match(line)
        if ent_m:
            finalize()
            current = {
                "term": ent_m.group(1).strip(),
                "file": file_label,
                "subject": subject_default,
                "category": current_category,
                "definition": "",
                "related": "",
                "key_detail": "",
                "sources": "",
            }
            continue
        if not current:
            continue
        fld = FIELD_RE.match(line)
        if not fld:
            continue
        field = fld.group(1).strip().lower()
        value = fld.group(2).strip()
        if field == "definition":
            current["definition"] = value
        elif field == "subject":
            current["subject"] = value
        elif field in ("source(s)", "source"):
            current["sources"] = value
        elif field == "related":
            current["related"] = value
        elif field in ("formula / key detail", "key detail"):
            current["key_detail"] = value
    finalize()
    return entries


def load_clusters():
    sys.path.insert(0, CLASS_NOTES)
    from app.config import CONCEPT_CLUSTERS
    out = []
    for c in CONCEPT_CLUSTERS:
        out.append({
            "id": c["id"],
            "kind": c.get("kind", "hub"),
            "label": c["label"],
            "icon": c["icon"],
            "desc": c["desc"],
            "subjects": c.get("subjects", []),
            "glossaries": [g.replace(".md", "") for g in c.get("glossaries", [])],
            "anchor_terms": c.get("anchor_terms", []),
        })
    return out


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    all_entries = []
    for fname, subject in GLOSSARY_FILES.items():
        path = os.path.join(GLOSSARY_DIR, fname)
        if not os.path.exists(path):
            print(f"  [skip] missing: {path}")
            continue
        label = fname.replace(".md", "")
        entries = parse_glossary(path, label, subject)
        for e in entries:
            all_entries.append(e)
        print(f"  {fname}: {len(entries)} entries")

    print(f"Total glossary entries: {len(all_entries)}")

    glossary_path = os.path.join(OUT_DIR, "glossary.json")
    with open(glossary_path, "w", encoding="utf-8") as f:
        json.dump({"entries": all_entries, "files": list(GLOSSARY_FILES.keys())}, f, ensure_ascii=False)
    print(f"Wrote {glossary_path} ({os.path.getsize(glossary_path) // 1024} KB)")

    clusters = load_clusters()
    clusters_path = os.path.join(OUT_DIR, "clusters.json")
    with open(clusters_path, "w", encoding="utf-8") as f:
        json.dump({"clusters": clusters}, f, ensure_ascii=False)
    print(f"Wrote {clusters_path} ({os.path.getsize(clusters_path) // 1024} KB, {len(clusters)} clusters)")


if __name__ == "__main__":
    main()
