# -*- coding: utf-8 -*-
"""Probe renderer: builds verification copies of output.html.

Headless Chrome does not reliably advance CSS transitions under
--virtual-time-budget, so entrance animations freeze half way and the
screenshot looks empty. These copies force the revealed state so the
LAYOUT and STYLING can be reviewed. They are throwaway, never shipped.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "dist", "index.html")

FORCE = (
    "<style>/* probe only: freeze the entrance animation at its final state */\n"
    ".js .reveal{opacity:1!important;transform:none!important;transition:none!important}\n"
    ".aurora b{animation:none!important}\n"
    ".fchip{animation:none!important}\n"
    "</style>"
)


def build(name, theme):
    with open(SRC, "r", encoding="utf-8") as fh:
        html = fh.read()
    if theme == "light":
        html = html.replace('<html lang="en" data-theme="dark">', '<html lang="en" data-theme="light">', 1)
        html = html.replace("var theme = 'dark';", "var theme = 'light';", 1)
    html = html.replace("</head>", FORCE + "\n</head>", 1)
    out = os.path.join(HERE, name)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(html)
    print("wrote", out)


build("probe_dark.html", "dark")
build("probe_light.html", "light")
