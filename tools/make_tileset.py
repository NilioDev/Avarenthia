"""Regenerate assets/glyphs_8x16.png from the bundled pixel font.

Usage: python tools/make_tileset.py [path/to/font.ttf]
Needs Pillow. The default font is Classic Console Neue (assets/fonts/clacon2.ttf),
an 8x16 pixel font: rendered at 16 px without anti-aliasing every glyph lands
exactly on the pixel grid.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, ROOT)
from cursed_vale.glyphs import CHARS, COLUMNS, ROWS, TILE_W, TILE_H, SHEET  # noqa: E402

FONT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'assets', 'fonts', 'clacon2.ttf')
OUT = os.path.join(ROOT, 'assets', SHEET)


def main():
    font = ImageFont.truetype(FONT, TILE_H)
    sheet = Image.new('RGBA', (COLUMNS * TILE_W, ROWS * TILE_H), (0, 0, 0, 0))
    for i, ch in enumerate(CHARS):
        glyph = Image.new('L', (TILE_W, TILE_H), 0)
        d = ImageDraw.Draw(glyph)
        d.fontmode = '1'          # no anti-aliasing: crisp pixels
        d.text((0, 0), ch, font=font, fill=255)
        tile = Image.new('RGBA', (TILE_W, TILE_H), (255, 255, 255, 0))
        tile.putalpha(glyph)
        sheet.paste(tile, ((i % COLUMNS) * TILE_W, (i // COLUMNS) * TILE_H))
    sheet.save(OUT)
    print('wrote', os.path.abspath(OUT), sheet.size)


if __name__ == '__main__':
    main()
