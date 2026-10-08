# -*- coding: utf-8 -*-
"""Static cost report for the glass page.

Counts the expensive compositing primitives (backdrop-filter surface area,
filter:blur layers, elements with infinite animations) so a fix can be
measured rather than guessed at.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

DIAG = """<script>
(function () {
  function name(e) { return typeof e.className === 'string' && e.className ? e.className : e.tagName; }
  window.addEventListener('load', function () {
    var out = [], bf = [], flt = [], anim = [], vw = innerWidth, vh = innerHeight;
    Array.prototype.forEach.call(document.querySelectorAll('body *'), function (e) {
      var r = e.getBoundingClientRect(), c = getComputedStyle(e);
      var area = Math.round(r.width * r.height);
      if (c.backdropFilter && c.backdropFilter !== 'none') {
        bf.push({ n: name(e), a: area, v: r.bottom > 0 && r.top < vh });
      }
      if (c.filter && c.filter !== 'none') {
        flt.push({ n: name(e), f: c.filter, a: area });
      }
      if (c.animationName && c.animationName !== 'none') { anim.push(name(e)); }
    });
    var total = bf.reduce(function (s, x) { return s + x.a; }, 0);
    var inView = bf.filter(function (x) { return x.v; }).reduce(function (s, x) { return s + x.a; }, 0);
    out.push('viewport ' + vw + 'x' + vh + ' = ' + Math.round(vw * vh / 1000) + 'k px2');
    out.push('backdrop-filter: ' + bf.length + ' elements, total ' + Math.round(total / 1000) + 'k px2 = '
      + (total / (vw * vh)).toFixed(2) + 'x viewport, in-view ' + Math.round(inView / 1000) + 'k px2');
    out.push('biggest bf: ' + bf.sort(function (a, b) { return b.a - a.a; }).slice(0, 5)
      .map(function (x) { return x.n.slice(0, 22) + '=' + Math.round(x.a / 1000) + 'k'; }).join(' | '));
    out.push('filter:blur layers: ' + flt.length + ' -> ' + flt.slice(0, 6)
      .map(function (x) { return x.n.slice(0, 18) + ' ' + x.f.slice(0, 22) + ' ' + Math.round(x.a / 1000) + 'k'; }).join(' | '));
    out.push('animated elements: ' + anim.length + ' -> ' + anim.slice(0, 8).join(', '));
    out.push('doc height: ' + document.documentElement.scrollHeight + 'px, stylesheets: ' + document.styleSheets.length);
    document.body.setAttribute('data-perf', out.join(' || '));
  });
})();
</script>"""


def main():
    with open(os.path.join(ROOT, "dist", "index.html"), "r", encoding="utf-8") as fh:
        html = fh.read()
    out = os.path.join(HERE, "probe_diag.html")
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(html.replace("</body>", DIAG + "\n</body>", 1))
    print("wrote", out)


if __name__ == "__main__":
    main()
