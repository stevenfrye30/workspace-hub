"""Parse Shakespeare's Sonnets from sonnets.txt (Project Gutenberg #1041)
and emit corpus.json as [{line, sonnet, idx}, ...].
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "sonnets.txt"
DST = HERE / "corpus.json"


def main():
    text = SRC.read_text(encoding="utf-8-sig")

    m1 = re.search(r"\*\*\* START OF .*? \*\*\*", text)
    m2 = re.search(r"\*\*\* END OF .*? \*\*\*", text)
    if m1:
        text = text[m1.end():]
    if m2:
        text = text[: m2.start() - (len(text) - len(text[m1.end():]) if m1 else 0)]

    # simpler: re-slice
    body = SRC.read_text(encoding="utf-8-sig")
    s = re.search(r"\*\*\* START OF .*? \*\*\*", body)
    e = re.search(r"\*\*\* END OF .*? \*\*\*", body)
    body = body[s.end():e.start()] if (s and e) else body

    entries = []
    current = None
    for raw in body.splitlines():
        line = raw.strip()
        if not line:
            continue
        # Roman numeral or number = sonnet header
        mm = re.match(r"^([IVXLCDM]+|[0-9]+)\.?$", line)
        if mm:
            current = mm.group(1)
            continue
        if current is None:
            continue
        if re.match(r"^(the sonnets|by william shakespeare|contents|the end)$", line, re.I):
            continue
        if "project gutenberg" in line.lower():
            continue
        if len(line) < 10:
            continue
        clean = re.sub(r"\s+", " ", line)
        entries.append({"line": clean, "sonnet": current})

    for i, e in enumerate(entries):
        e["idx"] = i

    DST.write_text(json.dumps(entries, ensure_ascii=False), encoding="utf-8")
    print(f"{len(entries)} lines -> {DST} ({DST.stat().st_size:,} bytes)")
    print(f"first: {entries[0]}")
    print(f"last:  {entries[-1]}")


if __name__ == "__main__":
    main()
