# -*- coding: utf-8 -*-
"""Detail-page check: the shared script must survive a page that has no search
palette, no carousel, no subscribe form and no mobile menu.

Also pins the detail layout open for screenshots (headless Chrome does not
advance CSS transitions under --virtual-time-budget).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SLUG = sys.argv[1] if len(sys.argv) > 1 else "pump"


def make(name, theme, freeze):
    with open(os.path.join(ROOT, "dist", "case", SLUG, "index.html"), "r", encoding="utf-8") as fh:
        html = fh.read()
    if theme == "light":
        html = html.replace('<html lang="zh-CN" data-theme="dark">', '<html lang="zh-CN" data-theme="light">', 1)
        html = html.replace("var theme = 'dark';", "var theme = 'light';", 1)
    if freeze:
        html = html.replace("</head>", "<style>.js .reveal{opacity:1!important;transform:none!important;"
                                       "transition:none!important}.aurora b{animation:none!important}</style>\n</head>", 1)
    out = os.path.join(HERE, name)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(html)
    print("wrote", out)


TEST = """<script>
window.addEventListener('error', function (e) { document.body.setAttribute('data-err', e.message); });
window.addEventListener('load', function () {
  setTimeout(function () {
    var log = [];
    function t(k, v) { log.push(k + '=' + v); }
    t('h1', document.querySelector('h1').textContent);
    t('steps', document.querySelectorAll('.steps li').length);
    t('facts', document.querySelectorAll('.facts > div').length);
    t('chips', document.querySelectorAll('.chips li').length);
    t('images', document.querySelectorAll('img[src^="data:image/webp"]').length);
    t('has_pal', !!document.getElementById('pal'));
    t('has_form', !!document.getElementById('subForm'));
    t('totop', !!document.getElementById('totop'));
    t('prev', document.querySelector('.pn__item b').textContent);
    t('next', document.querySelector('.pn__item--next b').textContent);
    t('broken_imgs', Array.prototype.filter.call(document.images, function (i) { return !i.complete || i.naturalWidth === 0; }).length);
    document.getElementById('theme').click();
    t('theme', document.documentElement.getAttribute('data-theme'));
    document.getElementById('theme').click();
    t('theme_back', document.documentElement.getAttribute('data-theme'));
    document.body.setAttribute('data-test', log.join(' | '));
  }, 900);
});
</script>"""


def main():
    src = os.path.join(ROOT, "dist", "case", SLUG, "index.html")
    with open(src, "r", encoding="utf-8") as fh:
        html = fh.read()
    out = os.path.join(HERE, "probe_detail_test.html")
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(html.replace("</body>", TEST + "\n</body>", 1))
    print("wrote", out)
    make("probe_detail_dark.html", "dark", True)
    make("probe_detail_light.html", "light", True)


if __name__ == "__main__":
    main()
