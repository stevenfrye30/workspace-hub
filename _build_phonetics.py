"""Extract shared phonetics code from sound-map/index.html into
/data/phonetics.js, then remove those blocks from sound-map.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "sound-map" / "index.html"
DST = ROOT / "data" / "phonetics.js"

html = SRC.read_text(encoding="utf-8")
lines = html.split("\n")

# Top-level shared blocks identified by starting declaration name (1-indexed line → declaration).
# For each, we'll extract from its starting line up to (but not including) the next top-level line.
shared_decls = {
    "SM_PHONEMES", "SM_FEATS", "SM_GROUP_COLORS", "SM_PHON_EXAMPLE",
    "SM_FOOT_NAMES", "SM_METER_NAMES", "SM_AUDIO",
    "smParsePhonemes", "smSyllabify", "smDescribe", "smSpeak",
    "smSylNucleus", "smSylOnset", "smSylCoda", "smSylRhymeKey",
    "smWordProximity", "smLastVowelOf", "smProximityBucket",
    "smAnalyzeMeter", "smFindMultiRhymes", "smComputeGroups",
    "smLevenshtein",
}
# Detect top-level declarations
decl_re = re.compile(r"^(?:const|let|var|function)\s+([A-Za-z_]\w*)")
decl_positions = []  # list of (line_idx, name)
for i, line in enumerate(lines):
    m = decl_re.match(line)
    if m:
        decl_positions.append((i, m.group(1)))

# For each shared decl, find its line range: from its line to the next top-level decl line.
ranges = []  # list of (start, end_exclusive, name)
for idx, (line_idx, name) in enumerate(decl_positions):
    if name not in shared_decls:
        continue
    end = decl_positions[idx + 1][0] if idx + 1 < len(decl_positions) else len(lines)
    ranges.append((line_idx, end, name))

# Sort by start
ranges.sort()

# Extract shared code
out_lines = [
    "// Shared phonetic library used by Sound Map and Flow Lab.",
    "// All functions here are pure (no DOM access); keep it that way.",
    "// Depends on the global `D` from data/cmudict.js.",
    "",
]
for start, end, name in ranges:
    out_lines.extend(lines[start:end])
    # If the extracted block doesn't end with a blank line, add one
    if out_lines and out_lines[-1].strip():
        out_lines.append("")

DST.write_text("\n".join(out_lines), encoding="utf-8")
print(f"Wrote {DST} ({DST.stat().st_size:,} bytes, {len(ranges)} blocks)")

# Now remove those lines from the source, keeping everything else.
# Build a set of lines-to-remove.
remove = set()
for start, end, _ in ranges:
    for i in range(start, end):
        remove.add(i)

new_lines = [ln for i, ln in enumerate(lines) if i not in remove]

# Insert <script src="../data/phonetics.js"></script> before the inline script
# that uses these functions. We'll insert it right after the cmudict.js script.
new_html = "\n".join(new_lines)
new_html = new_html.replace(
    '<script src="../data/cmudict.js"></script>',
    '<script src="../data/cmudict.js"></script>\n<script src="../data/phonetics.js"></script>',
    1,
)

# Collapse long runs of blank lines
new_html = re.sub(r"\n{3,}", "\n\n", new_html)

SRC.write_text(new_html, encoding="utf-8")
print(f"Rewrote {SRC}: new size {SRC.stat().st_size:,} bytes")
