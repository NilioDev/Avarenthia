"""Render a FakeCanvas to a PNG with the real tileset (for checking the look without a window)."""
import os

from PIL import Image

from avarenthia.glyphs import CHARS, COLUMNS, TILE_W, TILE_H, SHEET

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def save(cv, path, scale=1):
    sheet = Image.open(os.path.join(HERE, 'assets', SHEET)).convert('RGBA')
    out = Image.new('RGB', (cv.w * TILE_W, cv.h * TILE_H))
    cache = {}
    for i, ch in enumerate(cv.ch):
        x, y = i % cv.w, i // cv.w
        bg, fg = tuple(cv.bg[i]), tuple(cv.fg[i])
        out.paste(bg, (x * TILE_W, y * TILE_H, (x + 1) * TILE_W, (y + 1) * TILE_H))
        if ch == ' ':
            continue
        if ch not in cache:
            j = CHARS.index(ch)
            cache[ch] = sheet.crop(((j % COLUMNS) * TILE_W, (j // COLUMNS) * TILE_H,
                                    (j % COLUMNS + 1) * TILE_W, (j // COLUMNS + 1) * TILE_H)).getchannel('A')
        out.paste(fg, (x * TILE_W, y * TILE_H), cache[ch])
    if scale != 1:
        out = out.resize((out.width * scale, out.height * scale), Image.NEAREST)
    out.save(path)
