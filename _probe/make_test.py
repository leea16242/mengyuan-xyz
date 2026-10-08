# -*- coding: utf-8 -*-
"""Headless functional test: drives the deliverable through its real UI and
reports the observed state, so behaviour is verified without a browser devtools.

Injected on top of output.html, then read back through Chrome's --dump-dom.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

TEST = """<script>
(function () {
  var log = [];
  function t(k, v) { log.push(k + '=' + v); }
  window.addEventListener('error', function (e) { log.push('WINDOW_ERROR=' + e.message); });

  window.addEventListener('load', function () {
    setTimeout(function () {
      try {
        var pal = document.getElementById('pal');
        var inp = document.getElementById('palInput');
        var type = function (v) { inp.value = v; inp.dispatchEvent(new Event('input', { bubbles: true })); };
        var key = function (k) { pal.dispatchEvent(new KeyboardEvent('keydown', { key: k, bubbles: true })); };
        var rows = function () { return document.querySelectorAll('.pal__item').length; };

        document.getElementById('searchBtn').click();
        t('pal_open', pal.classList.contains('open'));
        t('pal_all_rows', rows());
        type('齿轮');
        t('pal_hit_齿轮', rows());
        t('pal_first_title', document.querySelector('.pal__item .pal__text b').textContent);
        type('zzzz');
        t('pal_empty_shown', !document.getElementById('palEmpty').hidden);
        type('SolidWorks 装配');
        t('pal_multiterm', rows());
        type('EPLAN');
        document.querySelector('.pal__item').dispatchEvent(new MouseEvent('click', { bubbles: true }));
        t('pal_closed_after_click', !pal.classList.contains('open'));
        t('pal_carousel_jumped', document.querySelector('[data-dots] [aria-current="true"]').getAttribute('aria-label'));
        setTimeout(function () { t('pal_ring_shown', document.querySelectorAll('.hit').length > 0); }, 200);

        document.getElementById('searchBtn').click();
        type('SolidWorks');
        key('ArrowDown');
        t('pal_kbd_select', document.querySelector('.pal__item[aria-selected="true"]').id);
        t('pal_kbd_rows', rows());
        key('Enter');
        t('pal_enter_closed', !pal.classList.contains('open'));
        document.getElementById('searchBtn').click();
        key('Escape');
        t('pal_esc_closed', !pal.classList.contains('open'));

        document.querySelector('.tag').dispatchEvent(new MouseEvent('click', { bubbles: true }));
        t('tag_search_value', document.getElementById('palInput').value);
        t('tag_search_rows', rows());
        key('Escape');

        var link = document.querySelector('.feat__link[data-case="6"]');
        t('skill_link_data', link ? link.getAttribute('data-case') : 'MISSING');
        link.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
        t('skill_link_jumped', document.querySelector('[data-dots] [aria-current="true"]').getAttribute('aria-label'));
        t('totop_exists', !!document.getElementById('totop'));

        var qa2 = document.querySelectorAll('[data-qa]')[1];
        document.getElementById('q2b').click();
        t('faq_open', qa2.getAttribute('data-open'));
        t('faq_aria', document.getElementById('q2b').getAttribute('aria-expanded'));
        t('faq_others_closed', document.querySelectorAll('[data-qa][data-open="true"]').length);

        document.getElementById('theme').click();
        t('theme_after_toggle', document.documentElement.getAttribute('data-theme'));
        t('theme_switch_state', document.getElementById('theme').getAttribute('aria-checked'));
        t('theme_saved', String(localStorage.getItem('af-theme')));

        var cur = function () {
          var d = document.querySelector('[data-dots] [aria-current="true"]');
          return d ? d.getAttribute('aria-label') : 'none';
        };
        var before = cur();
        document.querySelector('[data-next]').click();
        t('dots', before + ' -> ' + cur());
        document.querySelector('[data-prev]').click();
        t('dots_back', cur());
        t('slide_aria', document.querySelectorAll('.slide')[1].getAttribute('aria-hidden'));

        var form = document.getElementById('subForm');
        var input = document.getElementById('email');
        var fire = function () { form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true })); };

        input.value = 'nope';
        fire();
        t('invalid_err', document.getElementById('subMsg').classList.contains('err'));
        t('invalid_text', document.getElementById('subMsg').textContent.slice(0, 24));

        input.value = 'sam@acme.com';
        fire();
        t('loading', form.classList.contains('loading'));
        t('btn_disabled', document.getElementById('subBtn').disabled);

        setTimeout(function () {
          t('loading_after', form.classList.contains('loading'));
          t('toast_shown', document.getElementById('toast').classList.contains('show'));
          t('toast_text', document.getElementById('toastText').textContent.slice(0, 46));
          t('input_cleared', document.getElementById('email').value === '');
          t('msg_reset', document.getElementById('subMsg').textContent.slice(0, 18));
          document.body.setAttribute('data-test', log.join(' | '));
        }, 2200);
      } catch (err) {
        document.body.setAttribute('data-test', 'THROWN=' + err.message + ' ## ' + log.join(' | '));
      }
    }, 1400);
  });
})();
</script>"""


def main():
    with open(os.path.join(ROOT, "dist", "index.html"), "r", encoding="utf-8") as fh:
        html = fh.read()
    out = os.path.join(HERE, "probe_test.html")
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(html.replace("</body>", TEST + "\n</body>", 1))
    print("wrote", out)


if __name__ == "__main__":
    main()
