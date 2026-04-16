"""Extract the Sound Map portion of ipa/index.html into a standalone
sound-map/index.html. Reads the source, copies CSS, extracts the
panel-sound HTML and the Sound Map JS, assembles a clean page.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "ipa" / "index.html"
DST = ROOT / "sound-map" / "index.html"
DST.parent.mkdir(exist_ok=True)

html = SRC.read_text(encoding="utf-8")

# 1) CSS — keep the whole <style> block; it has some dead selectors but < 10KB.
css_match = re.search(r"<style>(.*?)</style>", html, re.DOTALL)
assert css_match, "no <style> block found"
css = css_match.group(1)

# 2) HTML for #panel-sound
panel_match = re.search(
    r'<!-- [^\n]*TAB 4[^\n]*SOUND MAP[^\n]*-->\s*<div id="panel-sound"[^>]*>(.*?)</div>\s*\n\s*<div class="status-bar"',
    html, re.DOTALL,
)
if not panel_match:
    # Fallback: locate differently
    panel_match = re.search(
        r'<div id="panel-sound"[^>]*>(.*)</div>\s*\n\s*<div class="status-bar"',
        html, re.DOTALL,
    )
assert panel_match, "panel-sound block not found"
panel_html = panel_match.group(1)

# 3) JS — Sound Map functions + the corpus code + event wiring.
# Grab from "// ══ SOUND MAP ══" comment block through end of script.
sm_match = re.search(r"(// ══════════════════════════════════\n//  SOUND MAP\n.*)(?=\n</script>)", html, re.DOTALL)
assert sm_match, "SOUND MAP js block not found"
sm_js = sm_match.group(1)

out = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sound Map — Phonetic Explorer</title>
<style>
body {{ background: var(--bg); color: var(--text); font-family: Georgia, serif; line-height: 1.5; height: 100vh; margin: 0; display: flex; flex-direction: column; overflow: hidden; }}
#sm-header {{ display: flex; align-items: baseline; gap: 16px; padding: 14px 24px; border-bottom: 1px solid var(--bdr); background: var(--surf); flex-shrink: 0; }}
#sm-header h1 {{ font-size: 15px; font-weight: 700; letter-spacing: .08em; color: var(--gold); text-transform: uppercase; margin: 0; }}
#sm-header .sub {{ font-size: 12px; color: var(--muted); font-style: italic; flex: 1; }}
#sm-header a {{ color: var(--muted); text-decoration: none; font-size: 11px; letter-spacing: .04em; text-transform: uppercase; padding: 5px 12px; border: 1px solid var(--bdr); border-radius: var(--radius); }}
#sm-header a:hover {{ color: var(--gold); border-color: var(--gold); }}
#panel-sound {{ flex: 1; display: flex; flex-direction: column; overflow: hidden; }}
{css}
</style>
</head>
<body>
<header id="sm-header">
  <h1>Sound Map</h1>
  <span class="sub">Paste English text to see it broken into colored phonemes. Click a phoneme to hear it and see where in the mouth it's made.</span>
  <a href="../">← Workspace</a>
</header>

<div id="panel-sound">{panel_html}</div>

<div class="status-bar" id="status-bar"></div>

<script src="../data/cmudict.js"></script>
<script>
{sm_js}
</script>
</body>
</html>
"""

DST.write_text(out, encoding="utf-8")
print(f"Wrote {DST} ({DST.stat().st_size:,} bytes)")
