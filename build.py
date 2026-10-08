# -*- coding: utf-8 -*-
"""Build the MENGYUAN site into dist/.

  dist/index.html               index page
  dist/case/<slug>/index.html   6 case detail pages

Every page is self-contained: CSS and images are inlined as data URIs, so the
only thing that lands on disk is HTML. Deploy with:

  wrangler pages deploy dist --project-name mengyuan-xyz --branch main

Checks on every page: no unresolved {{PLACEHOLDER}} and no em dash / en dash.
"""
import base64
import html
import os
import re
import shutil
import sys

import cases

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
ASSETS = os.path.join(HERE, "assets", "cases")
DIST = os.path.join(HERE, "dist")

INDEX_PARTS = ["00_head.html", "10_tokens.css", "20_components.css", "30_sections.css",
               "35_sections2.css", "40_body_a.html", "50_body_b.html", "60_body_c.html",
               "90_script.html"]
DETAIL_PARTS = ["70_detail_head.html", "10_tokens.css", "20_components.css", "30_sections.css",
                "35_sections2.css", "45_detail.css", "75_detail_body.html", "90_script.html"]


def read(name):
    with open(os.path.join(SRC, name), "r", encoding="utf-8") as fh:
        return fh.read()


def uri(name):
    path = os.path.join(ASSETS, name)
    if not os.path.exists(path):
        raise SystemExit("ERROR missing asset %s (run build_thumbs.py first)" % path)
    with open(path, "rb") as fh:
        return "data:image/webp;base64," + base64.b64encode(fh.read()).decode("ascii")


def t(s):                       # text node
    return html.escape(s, quote=False)


def a(s):                       # attribute value
    return html.escape(s, quote=True)


def gallery(c):
    if len(c["shots"]) < 2:
        return ""
    figs = []
    for i, cap in enumerate(c["shots"][1:], start=2):
        figs.append(
            '<figure class="detail__shot"><span class="detail__frame">'
            '<img src="%s" alt="%s" width="1000" height="625" loading="lazy" decoding="async">'
            '</span><figcaption>%s</figcaption></figure>'
            % (uri("%s-%d.webp" % (c["slug"], i)), a(cap), t(cap)))
    return '<section class="detail__sec reveal"><h2>细节</h2><div class="gal">%s</div></section>' % "".join(figs)


def build_index():
    page = "\n".join(read(n) for n in INDEX_PARTS)
    for c in cases.CASES:
        page = page.replace("{{CASE_%s}}" % c["slug"], uri("%s.webp" % c["slug"]))
    return page


def build_detail(c, prev, nxt):
    page = "\n".join(read(n) for n in DETAIL_PARTS)
    rep = {
        "{{PAGE_TITLE}}": t("%s · %s · MENGYUAN" % (c["title"], c["tags"][0])),
        "{{PAGE_DESC}}": a(c["summary"]),
        "{{NUM}}": c["num"],
        "{{TITLE}}": t(c["title"]),
        "{{SUMMARY}}": t(c["summary"]),
        "{{TAGS}}": "".join("<span>%s</span>" % t(x) for x in c["tags"]),
        "{{HERO_SRC}}": uri("%s-1.webp" % c["slug"]),
        "{{HERO_ALT}}": a("%s的渲染图" % c["title"]),
        "{{HERO_CAP}}": t(c["shots"][0]),
        "{{OVERVIEW}}": "".join("<p>%s</p>" % t(p) for p in c["overview"]),
        "{{FACTS}}": "".join("<div><dt>%s</dt><dd>%s</dd></div>" % (t(k), t(v)) for k, v in c["facts"]),
        "{{STEPS}}": "".join("<li><b>%s</b><p>%s</p></li>" % (t(h), t(b)) for h, b in c["steps"]),
        "{{GALLERY}}": gallery(c),
        "{{APIS}}": "".join("<li>%s</li>" % t(x) for x in c["apis"]),
        "{{PREV_HREF}}": "../%s/" % prev["slug"],
        "{{PREV_TITLE}}": t(prev["title"]),
        "{{NEXT_HREF}}": "../%s/" % nxt["slug"],
        "{{NEXT_TITLE}}": t(nxt["title"]),
    }
    for key, val in rep.items():
        page = page.replace(key, val)
    return page


def check(name, page):
    left = re.findall(r"\{\{[A-Z0-9_]+\}\}", page)
    if left:
        print("ERROR %s unresolved placeholders: %s" % (name, sorted(set(left))))
        return False
    bad = re.findall(u"[\u2014\u2013]", page)
    if bad:
        for i, line in enumerate(page.splitlines(), 1):
            if any(b in line for b in bad):
                print("ERROR %s dash at line %d: %s" % (name, i, line.strip()[:110]))
                break
        return False
    return True


def main():
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    state = {"ok": True, "pages": 0, "total": 0}

    def emit(rel, page):
        path = os.path.join(DIST, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not check(rel, page):
            state["ok"] = False
            return
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(page)
        state["pages"] += 1
        state["total"] += os.path.getsize(path)

    emit("index.html", build_index())
    n = len(cases.CASES)
    for i, c in enumerate(cases.CASES):
        emit(os.path.join("case", c["slug"], "index.html"),
             build_detail(c, cases.CASES[(i - 1) % n], cases.CASES[(i + 1) % n]))

    if not state["ok"]:
        return 1
    print("OK  %d pages, %.1f kB total -> %s" % (state["pages"], state["total"] / 1024, DIST))
    return 0


if __name__ == "__main__":
    sys.exit(main())
