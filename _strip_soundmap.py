"""Remove Sound Map from ipa/index.html (now served by sound-map/)."""
import re
from pathlib import Path

SRC = Path(__file__).resolve().parent / "ipa" / "index.html"

html = SRC.read_text(encoding="utf-8")

# 1) Remove the Sound Map tab button.
html = re.sub(
    r'\n  <button class="tab-btn"[^>]*data-tab="sound"[^>]*>Sound Map</button>',
    "",
    html,
)

# 2) Remove the panel-sound HTML block.
html = re.sub(
    r"\n<!-- ═+\n\s*TAB 4\s*·\s*SOUND MAP\s*\n\s*═+ -->\n<div id=\"panel-sound\".*?</div>\n(?=\n<div class=\"status-bar\")",
    "",
    html,
    flags=re.DOTALL,
)

# 3) Remove the Sound Map CSS section (from the SOUND MAP comment
# through the blank line before the next section).
html = re.sub(
    r"\n\n/\* ═+ SOUND MAP ═+ \*/.*?(?=\n@media \(max-width:768px\))",
    "\n\n",
    html,
    flags=re.DOTALL,
    count=1,
)

# 4) Remove the Sound Map JS section (from "// ══ SOUND MAP ══" to "</script>").
html = re.sub(
    r"\n\n// ═+\n//  SOUND MAP\n// ═+.*?(?=\n</script>)",
    "",
    html,
    flags=re.DOTALL,
    count=1,
)

SRC.write_text(html, encoding="utf-8")
print(f"Stripped Sound Map from {SRC}; new size {SRC.stat().st_size:,} bytes")
