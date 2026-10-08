# -*- coding: utf-8 -*-
"""Generate case imagery from the original CAD / schematic renders.

For every case:
  assets/cases/<key>.webp       600x375  index card thumbnail
  assets/cases/<key>-1.webp     1000x625 detail hero
  assets/cases/<key>-2..n.webp  1000x625 detail gallery

Auto-framing: background colour = median of the border pixels, non-background
pixels are projected onto both axes to find the subject box, then a 16:10 window
is centred on it with 10% margin and padded with the background colour when it
falls outside the image. Sources live in cad-sample/ and WorkBuddy-work/.
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))          # D:\AIchat\AIdailychat
OUT = os.path.join(HERE, "assets", "cases")

CARD = (600, 375)
SHOT = (1000, 625)
MARGIN = 0.10
TOL = 26.0

# key -> [(source, mode), ...]; first item is the hero.
#   mode = None        自动取景（找主体框后裁 16:10）
#          (x0,y0,x1,y1) 先按比例预裁，再自动取景
#          "center"      直接居中裁 16:10（主体铺满整幅、取景会误判时用）
CASES = {
    "pump": [
        ("cad-sample/pump/齿轮油泵_装配渲染.png", "center"),
        ("cad-sample/pump/齿轮油泵_侧视.png", "center"),
        ("cad-sample/_shared/motion_curve.png", "center"),
    ],
    "crown": [
        ("cad-sample/parts/crown_cap/crown_cap_render.png", None),
    ],
    "gear": [
        ("cad-sample/parts/gear/gear_gb_2m30t_eq_profile.png", None),
        ("cad-sample/parts/gear/gear_gb_1m20t.png", None),
    ],
    "funnel": [
        ("cad-sample/parts/funnel_cup/FINAL_iso.png", None),
        ("cad-sample/parts/funnel_cup/funnel_cup_fillet_neck.png", None),
        ("cad-sample/parts/funnel_cup/FINAL_junc.png", None),
    ],
    "bracket": [
        ("cad-sample/parts/bracket_1684/bracket_20260904T074351Z.png", None),
    ],
    "eplan": [
        ("WorkBuddy-work/eplan_work/export/正反转_控制电路.png", None),
        ("WorkBuddy-work/eplan_work/export/正反转_主电路.png", None),
    ],
}


def center_crop(img, ratio):
    w, h = img.size
    if w / float(h) > ratio:
        nw = int(round(h * ratio))
        left = (w - nw) // 2
        return img.crop((left, 0, left + nw, h))
    nh = int(round(w / ratio))
    top = (h - nh) // 2
    return img.crop((0, top, w, top + nh))


def frame(img, size):
    w, h = img.size
    a = np.asarray(img.convert("RGB"), dtype=np.float32)
    border = np.concatenate([a[0:4].reshape(-1, 3), a[-4:].reshape(-1, 3),
                             a[:, 0:4].reshape(-1, 3), a[:, -4:].reshape(-1, 3)])
    bg = np.median(border, axis=0)
    mask = (np.abs(a - bg).max(axis=2) > TOL)
    cols = mask.sum(axis=0) > max(2, h * 0.01)
    rows = mask.sum(axis=1) > max(2, w * 0.01)
    if cols.any() and rows.any():
        xs, ys = np.where(cols)[0], np.where(rows)[0]
        box = (int(xs[0]), int(ys[0]), int(xs[-1]) + 1, int(ys[-1]) + 1)
    else:
        box = (0, 0, w, h)

    ratio = size[0] / float(size[1])
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    bw = (box[2] - box[0]) * (1 + MARGIN * 2)
    bh = (box[3] - box[1]) * (1 + MARGIN * 2)
    if bw / bh < ratio:
        bw = bh * ratio
    else:
        bh = bw / ratio

    left, top = int(round(cx - bw / 2)), int(round(cy - bh / 2))
    canvas = Image.new("RGB", (int(round(bw)), int(round(bh))), tuple(int(v) for v in bg))
    canvas.paste(img, (-left, -top))
    return canvas.resize(size, Image.LANCZOS)


def main():
    os.makedirs(OUT, exist_ok=True)
    total, count = 0, 0
    for key, items in CASES.items():
        for i, (rel, mode) in enumerate(items):
            img = Image.open(os.path.join(ROOT, rel.replace("/", os.sep)))
            if isinstance(mode, tuple):
                w, h = img.size
                img = img.crop((int(w * mode[0]), int(h * mode[1]), int(w * mode[2]), int(h * mode[3])))
            for size, name in ((CARD, "%s.webp" % key), (SHOT, "%s-%d.webp" % (key, i + 1))):
                dst = os.path.join(OUT, name)
                out = center_crop(img, size[0] / float(size[1])) if mode == "center" else frame(img, size)
                out.resize(size, Image.LANCZOS).save(dst, "WEBP", quality=78, method=6)
                sz = os.path.getsize(dst)
                total += sz
                count += 1
                if size == SHOT:
                    print("  %-14s %6d B  <- %s" % (name, sz, os.path.basename(rel)[:44]))
    print("OK  %d images, %d B total" % (count, total))


if __name__ == "__main__":
    main()
