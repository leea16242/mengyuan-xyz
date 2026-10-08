# -*- coding: utf-8 -*-
"""Build the single-file AetherFlow landing page.

Steps:
  1. crop the AI generated portraits to a face-centred square (drops the corner watermark)
  2. encode them as base64 JPEG data URIs
  3. concatenate the src/ parts into one self-contained output.html
"""
import base64
import io
import os
import re
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
OUT = os.path.join(HERE, "output.html")

PARTS = [
    "00_head.html",
    "10_tokens.css",
    "20_components.css",
    "30_sections.css",
    "35_sections2.css",
    "40_body_a.html",
    "50_body_b.html",
    "60_body_c.html",
    "90_script.html",
]

# token -> (source png, face centre x, face centre y, crop side) as image fractions
AVATARS = {
    "{{AV1}}": ("assets/Square_studio_portrait_headsho_2026-10-04T12-15-39.png", 0.46, 0.32, 0.56),
    "{{AV2}}": ("assets/p5/Square_studio_portrait_headsho_2026-10-04T12-16-10.png", 0.47, 0.36, 0.60),
    "{{AV3}}": ("assets/Square_studio_portrait_headsho_2026-10-04T12-15-38.png", 0.50, 0.42, 0.60),
    "{{AV4}}": ("assets/p5/Square_studio_portrait_headsho_2026-10-04T12-16-11.png", 0.49, 0.42, 0.60),
    "{{AV5}}": ("assets/p5/Square_studio_portrait_headsho_2026-10-04T12-16-09.png", 0.50, 0.42, 0.60),
}
OUT_SIZE = 224          # 2x the 48px avatar slot, 4x+ the 22px nav cluster
JPEG_QUALITY = 84


def avatar_uri(rel_path, cx, cy, side):
    path = os.path.join(HERE, rel_path.replace("/", os.sep))
    img = Image.open(path).convert("RGB")
    w, h = img.size
    s = int(min(w, h) * side)
    left = max(0, min(w - s, int(w * cx - s / 2)))
    top = max(0, min(h - s, int(h * cy - s / 2)))
    img = img.crop((left, top, left + s, top + s)).resize((OUT_SIZE, OUT_SIZE), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
    raw = buf.getvalue()
    print("  %-52s %6d bytes -> %5.1f kB base64" % (os.path.basename(rel_path), len(raw), len(raw) * 4 / 3 / 1024))
    return "data:image/jpeg;base64," + base64.b64encode(raw).decode("ascii")


def main():
    print("1/3  encoding avatars")
    tokens = {k: avatar_uri(*v) for k, v in AVATARS.items()}

    print("2/3  concatenating %d source parts" % len(PARTS))
    chunks = []
    for name in PARTS:
        with open(os.path.join(SRC, name), "r", encoding="utf-8") as fh:
            chunks.append(fh.read())
    html = "\n".join(chunks)

    for token, uri in tokens.items():
        html = html.replace(token, uri)

    print("3/3  writing output")
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(html)

    left = re.findall(r"\{\{[A-Z0-9_]+\}\}", html)
    if left:
        print("ERROR unresolved placeholders: %s" % sorted(set(left)))
        return 1

    # aesthetic hard rule: no em dash / en dash anywhere in the deliverable
    bad = sorted(set(re.findall(u"[\u2014\u2013]", html)))
    if bad:
        for i, line in enumerate(html.splitlines(), 1):
            if any(b in line for b in bad):
                print("ERROR dash at line %d: %s" % (i, line.strip()[:110]))
        return 1

    size = os.path.getsize(OUT)
    print("OK  %s  (%.1f kB, %d lines)" % (OUT, size / 1024, html.count("\n") + 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
