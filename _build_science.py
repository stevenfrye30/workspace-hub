#!/usr/bin/env python3
"""Build the static `science/` subsite.

Reads live data from the class-notes Flask project and dumps two JSON files:
  - science/data/glossary.json  (2,039 entries from courses/Resources/_Glossary/*.md)
  - science/data/clusters.json  (CONCEPT_CLUSTERS, lightly trimmed)

The HTML pages in science/ fetch those JSON files at runtime, so no re-deploy
is needed unless you want fresh content.
"""

import hashlib
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CLASS_NOTES = os.path.normpath(os.path.join(HERE, "..", "projects", "class notes"))
GLOSSARY_DIR = os.path.join(CLASS_NOTES, "courses", "Resources", "_Glossary")
EXTRACTS_DIR = os.path.join(CLASS_NOTES, "_phase2_extracts")
OUT_DIR = os.path.join(HERE, "science", "data")
EXTRACTS_OUT_DIR = os.path.join(OUT_DIR, "extracts")

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


SEG_SPLIT_RE = re.compile(r"\n?---\s+(Slide|Page|Image)\s+(\d+)\s+---\n", re.IGNORECASE)

# Fallback mapping for older extracts missing SUBJECT/SUB_SUBJECT headers.
# Keys are the folder slugs under _phase2_extracts/.
SLUG_TO_SUBJECT = {
    "anatomy": ("Biology", "Anatomy & Physiology"),
    "biochem": ("Biology", "Biochemistry"),
    "bioinformatics": ("Biology", "Bioinformatics"),
    "cellbio": ("Biology", "Cell Biology"),
    "genetics": ("Biology", "Genetics"),
    "immunology": ("Biology", "Immunology"),
    "molbio": ("Biology", "Molecular Biology"),
    "elementary-bio": ("Biology", "Elementary Biology"),
    "plant-bio": ("Biology", "Plant Biology"),
    "vaccine-bio": ("Biology", "Vaccine Biology"),
    "ochem": ("Chemistry", "Organic Chemistry"),
    "analytical-chem": ("Chemistry", "Analytical Chemistry"),
    "elementary-chem": ("Chemistry", "Elementary Chemistry"),
    "physical-chem": ("Chemistry", "Physical Chemistry"),
    "earth-sci": ("Other", "Earth Science"),
    "psychology": ("Other", "Psychology"),
    "resources-bio-other": ("Resources", "Biology & Other"),
    "resources-chem": ("Resources", "Chemistry"),
}


def parse_extract(path):
    """Parse header + body of an _phase2_extracts/*.txt file."""
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    lines = content.splitlines()
    source = subject = sub_subject = extracted_by = None
    body_start = 0
    for i, line in enumerate(lines[:12]):
        if line.startswith("# SOURCE:"):
            source = line[len("# SOURCE:"):].strip()
        elif line.startswith("# SUBJECT:"):
            subject = line[len("# SUBJECT:"):].strip()
        elif line.startswith("# SUB_SUBJECT:"):
            sub_subject = line[len("# SUB_SUBJECT:"):].strip()
        elif line.startswith("# EXTRACTED_BY:"):
            extracted_by = line[len("# EXTRACTED_BY:"):].strip()
        elif line.strip() and not line.startswith("#"):
            body_start = i
            break
        else:
            body_start = i + 1
    if not source:
        return None
    body = "\n".join(lines[body_start:])

    # Split body into segments using "--- Slide/Page/Image N ---" markers
    pieces = SEG_SPLIT_RE.split(body)
    segments = []
    if pieces and pieces[0].strip():
        segments.append({"kind": "intro", "n": 0, "text": pieces[0].strip()})
    for i in range(1, len(pieces), 3):
        if i + 2 >= len(pieces):
            break
        kind = pieces[i].lower()
        try:
            n = int(pieces[i + 1])
        except (ValueError, IndexError):
            n = 0
        txt = pieces[i + 2].strip() if i + 2 < len(pieces) else ""
        if txt:
            segments.append({"kind": kind, "n": n, "text": txt})

    return {
        "source": source.replace("\\", "/"),
        "subject": subject,
        "sub_subject": sub_subject,
        "extracted_by": extracted_by,
        "segments": segments,
    }


def subject_path_for(extract):
    """Key matching a cluster's subjects[] entry, e.g. 'Biology/Cell Biology'."""
    subj = extract.get("subject") or ""
    sub = extract.get("sub_subject") or ""
    if not subj or not sub:
        return None
    return f"{subj}/{sub}"


def extract_id(source_path):
    return hashlib.md5(source_path.encode("utf-8")).hexdigest()[:12]


def export_extracts():
    """Write one JSON file per extract + a flat index."""
    if os.path.isdir(EXTRACTS_OUT_DIR):
        shutil.rmtree(EXTRACTS_OUT_DIR)
    os.makedirs(EXTRACTS_OUT_DIR, exist_ok=True)

    if not os.path.isdir(EXTRACTS_DIR):
        print(f"  [warn] no extracts dir: {EXTRACTS_DIR}")
        return {"count": 0}

    index = []
    total_chars = 0
    skipped = 0

    for r, _d, files in os.walk(EXTRACTS_DIR):
        slug = os.path.basename(r.rstrip(os.sep))
        fallback = SLUG_TO_SUBJECT.get(slug)
        for fn in sorted(files):
            if not fn.endswith(".txt"):
                continue
            full = os.path.join(r, fn)
            info = parse_extract(full)
            if not info or not info.get("segments"):
                skipped += 1
                continue
            # Fill subject/sub_subject from folder slug if missing
            if (not info.get("subject") or not info.get("sub_subject")) and fallback:
                info["subject"] = info.get("subject") or fallback[0]
                info["sub_subject"] = info.get("sub_subject") or fallback[1]
            subj_path = subject_path_for(info)
            if not subj_path:
                skipped += 1
                continue

            eid = extract_id(info["source"])
            # Shard by first 2 hex chars to keep directory sizes reasonable
            shard = eid[:2]
            shard_dir = os.path.join(EXTRACTS_OUT_DIR, shard)
            os.makedirs(shard_dir, exist_ok=True)
            out_path = os.path.join(shard_dir, f"{eid}.json")

            payload = {
                "id": eid,
                "source": info["source"],
                "subject": info["subject"],
                "sub_subject": info["sub_subject"],
                "subject_path": subj_path,
                "extracted_by": info.get("extracted_by"),
                "segments": info["segments"],
            }
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False)

            char_count = sum(len(s["text"]) for s in info["segments"])
            total_chars += char_count

            index.append({
                "id": eid,
                "shard": shard,
                "source": info["source"],
                "title": os.path.basename(info["source"]),
                "subject": info["subject"],
                "sub_subject": info["sub_subject"],
                "subject_path": subj_path,
                "segments": len(info["segments"]),
                "chars": char_count,
                "extracted_by": info.get("extracted_by"),
            })

    index_path = os.path.join(OUT_DIR, "extracts_index.json")
    index.sort(key=lambda x: (x["subject_path"], x["title"].lower()))
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump({"extracts": index}, f, ensure_ascii=False)
    print(f"  extracts: {len(index)} indexed, {total_chars // 1024} KB text, {skipped} skipped")
    print(f"  wrote {index_path} ({os.path.getsize(index_path) // 1024} KB)")
    return {"count": len(index), "chars": total_chars, "skipped": skipped}


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

    print("Extracts:")
    export_extracts()


if __name__ == "__main__":
    main()
