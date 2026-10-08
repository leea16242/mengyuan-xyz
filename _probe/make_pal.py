# -*- coding: utf-8 -*-
"""Render the search palette in its final visual state.

Headless Chrome does not advance CSS transitions under --virtual-time-budget,
so the palette's fade/slide would freeze half way. This probe pins the palette
open and freezes the entrance animations, then the caller screenshots it.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

FORCE = (
    "<style>\n"
    ".js .reveal{opacity:1!important;transform:none!important;transition:none!important}\n"
    ".aurora b,.fchip{animation:none!important}\n"
    ".pal{opacity:1!important;visibility:visible!important;transition:none!important}\n"
    ".pal__box{transform:none!important;transition:none!important}\n"
    "</style>"
)

DRIVE = """<script>
window.addEventListener('load', function () {
  setTimeout(function () {
    var inp = document.getElementById('palInput');
    document.getElementById('searchBtn').click();
    inp.value = '%s';
    inp.dispatchEvent(new Event('input', { bubbles: true }));
  }, 300);
});
</script>"""


def main():
    with open(os.path.join(ROOT, "dist", "index.html"), "r", encoding="utf-8") as fh:
        html = fh.read()
    html = html.replace("</head>", FORCE + "\n</head>", 1)
    for name, query in (("probe_pal.html", "SolidWorks"), ("probe_pal_empty.html", "zzzz")):
        out = os.path.join(HERE, name)
        with open(out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(html.replace("</body>", (DRIVE % query) + "\n</body>", 1))
        print("wrote", out)


if __name__ == "__main__":
    main()
