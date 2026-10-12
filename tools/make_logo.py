"""Turn assets/logo.png into avarenthia/logo.py: the title emblem as blocks of the CGA font.

The ornate As are made exact mirror images of each other, the letters are smoothed into solid strokes with
a dark outline, and the scrolls keep their fine shading. The result is baked into a module so the game needs
no image library at run time.

Usage: python tools/make_logo.py  (needs Pillow and numpy)"""
import math
import os

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
RAMP = ' ·░▒▓█'


def lum(c):
    return (c[0] * .3 + c[1] * .55 + c[2] * .15) / 255


def mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def build(width=90):
    arr = np.asarray(Image.open(os.path.join(ROOT, 'assets', 'logo.png')).convert('RGB')).copy()
    # the right ornate A becomes the mirror of the left one
    left = np.zeros_like(arr)
    for y in range(arr.shape[0]):
        cut = int(247 + (266 - 247) * (y - 236) / 84) if 236 <= y <= 320 else 300
        left[y, :cut] = arr[y, :cut]
    arr[:, 762:] = 0
    arr[:, 762:] = np.maximum(arr[:, 762:], left[:, ::-1][:, 762:])
    # the subtitle is written in real letters by the game; wipe it here (not the blade)
    arr[318:364, 292:497] = 0
    arr[318:364, 528:735] = 0
    src = Image.fromarray(arr).crop((118, 68, 906, 492))
    src = ImageEnhance.Contrast(src.filter(ImageFilter.UnsharpMask(4, 160, 2))).enhance(1.15)
    w = width
    h = round(src.height / src.width * w)
    soft = np.asarray(src.filter(ImageFilter.GaussianBlur(3)).resize((w, h), Image.LANCZOS)).astype(float)
    sharp = np.asarray(src.resize((w, h), Image.LANCZOS)).astype(float)
    L = np.array([[lum(soft[y, x]) * 1.7 for x in range(w)] for y in range(h)])
    LS = np.array([[lum(sharp[y, x]) * 1.5 for x in range(w)] for y in range(h)])
    first = int(math.ceil((761 - 118) / 788 * w)) + 1
    ltop, lbot = round((242 - 68) / 424 * h), round((316 - 68) / 424 * h)
    lcol0, lcol1 = round((250 - 118) / 788 * w), round((760 - 118) / 788 * w)
    for y in range(h):
        for x in range(w):
            if not (lcol0 <= x <= lcol1):
                L[y, x] = LS[y, x]
    L[:, first:] = L[:, ::-1][:, first:]
    outline = set()
    for y in range(h):
        for x in range(w):
            if L[y, x] > .5 and lcol0 <= x <= lcol1:
                for dx, dy in ((1, 1), (1, 0), (0, 1), (-1, 0), (0, -1), (2, 1)):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < w and 0 <= yy < h and L[yy, xx] <= .5:
                        outline.add((xx, yy))
    cells = []
    for y in range(h):
        for x in range(w):
            l = L[y, x]
            if l < .14:
                if (x, y) in outline:
                    cells.append((x, y, ' ', (0, 0, 0), 0, 1))
                continue
            letters = ltop <= y <= lbot and lcol0 <= x <= lcol1
            ch = '█' if l > .5 else '▓' if l > .34 else '▒' if l > .22 else '░'
            if letters and l <= .5:
                ch = '░' if l < .34 else '▒'
            strong = False
            if not (lcol0 <= x <= lcol1):
                ch = RAMP[min(len(RAMP) - 1, int(l * (len(RAMP) - 1)))]
                strong = l > .62 and ltop - 1 <= y <= lbot
                if strong:
                    ch = '█'
            rel = (y - ltop) / max(1, lbot - ltop)
            col = mix((255, 236, 170), (196, 140, 64), rel)
            if not letters and not strong:
                col = mix(col, (150, 110, 56), .35)
            if l <= .5:
                col = mix(col, (90, 64, 32), .45)
            cells.append((x, y, ch, col, int(min(1, l) * 100), int((x, y) in outline)))
    sub = round((340 - 68) / 424 * h)
    return w, h, sub, cells


if __name__ == '__main__':
    w, h, sub, cells = build()
    out = os.path.join(ROOT, 'avarenthia', 'logo.py')
    with open(out, 'w', encoding='utf-8') as f:
        f.write('"""The title emblem, made by tools/make_logo.py from assets/logo.png. Do not edit by hand."""\n')
        f.write(f'W, H, SUBTITLE_ROW = {w}, {h}, {sub}\n')
        f.write('# (x, y, glyph, (r, g, b), shine 0-100, on the dark outline)\n')
        f.write('CELLS = [\n')
        for c in cells:
            f.write(f'    ({c[0]}, {c[1]}, {c[2]!r}, {c[3]}, {c[4]}, {c[5]}),\n')
        f.write(']\n')
    print(out, len(cells))
