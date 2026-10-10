"""Regenerate assets/glyphs_12x24.png from a monospace TrueType font.

Usage: python tools/make_tileset.py [path/to/font.ttf]
Needs Pillow. Box-drawing and block characters are drawn by hand so they
join seamlessly; everything else is rendered from the font.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from cursed_vale.glyphs import CHARS, COLUMNS, ROWS, TILE_W, TILE_H  # noqa: E402

FONT = sys.argv[1] if len(sys.argv) > 1 else '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
OUT = os.path.join(os.path.dirname(__file__), '..', 'assets', 'glyphs_12x24.png')


def draw_special(d, ch):
    w, h = TILE_W, TILE_H
    cx, cy = w // 2, h // 2
    t = 2  # line thickness
    hl = lambda x0, x1: d.rectangle([x0, cy - t // 2, x1, cy - t // 2 + t - 1], fill=255)
    vl = lambda y0, y1: d.rectangle([cx - t // 2, y0, cx - t // 2 + t - 1, y1], fill=255)
    L, R, U, Dn = (lambda: hl(0, cx)), (lambda: hl(cx - 1, w - 1)), (lambda: vl(0, cy)), (lambda: vl(cy - 1, h - 1))
    parts = {'─': 'LR', '│': 'UD', '┌': 'RD', '┐': 'LD', '└': 'UR', '┘': 'UL', '┤': 'UDL', '├': 'UDR',
             '┬': 'LRD', '┴': 'LRU', '┼': 'LRUD'}
    if ch in parts:
        for p in parts[ch]:
            {'L': L, 'R': R, 'U': U, 'D': Dn}[p]()
        return True
    blocks = {'█': (0, 0, w, h), '▀': (0, 0, w, h // 2), '▄': (0, h // 2, w, h), '▌': (0, 0, w // 2, h), '▐': (w // 2, 0, w, h)}
    if ch in blocks:
        x0, y0, x1, y1 = blocks[ch]
        d.rectangle([x0, y0, x1 - 1, y1 - 1], fill=255)
        return True
    shades = {'░': 70, '▒': 130, '▓': 200}
    if ch in shades:
        d.rectangle([0, 0, w - 1, h - 1], fill=shades[ch])
        return True
    return False


def main():
    font = ImageFont.truetype(FONT, 20)
    ascent, descent = font.getmetrics()
    sheet = Image.new('RGBA', (COLUMNS * TILE_W, ROWS * TILE_H), (0, 0, 0, 0))
    for i, ch in enumerate(CHARS):
        glyph = Image.new('L', (TILE_W, TILE_H), 0)
        d = ImageDraw.Draw(glyph)
        if not draw_special(d, ch):
            adv = font.getlength(ch)
            x = (TILE_W - adv) / 2
            y = (TILE_H - (ascent + descent)) / 2
            d.text((x, y), ch, font=font, fill=255)
        tile = Image.new('RGBA', (TILE_W, TILE_H), (255, 255, 255, 0))
        tile.putalpha(glyph)
        sheet.paste(tile, ((i % COLUMNS) * TILE_W, (i // COLUMNS) * TILE_H))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    sheet.save(OUT)
    print('wrote', os.path.abspath(OUT), sheet.size)


if __name__ == '__main__':
    main()
