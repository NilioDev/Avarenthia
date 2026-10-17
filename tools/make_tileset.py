"""Regenerate assets/glyphs.png from the bundled pixel font.

Usage: python tools/make_tileset.py [path/to/font.ttf]
Needs Pillow. The font is the IBM CGA 8x8 font (assets/fonts/Px437_IBM_CGA.ttf): rendered at 8 px without
anti-aliasing every glyph lands exactly on the 8x8 grid, one glyph per 8x8 tile. The few characters the game uses that the font lacks are drawn by hand below.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, ROOT)
from avarenthia.glyphs import CHARS, COLUMNS, ROWS, TILE_W, TILE_H, SHEET  # noqa: E402

FONT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'assets', 'fonts', 'Px437_IBM_CGA.ttf')
OUT = os.path.join(ROOT, 'assets', SHEET)
GRID = 8

# glyphs the CGA font does not have, drawn in its style (8x8, two-pixel strokes)
HAND = {
    '…': ['........', '........', '........', '........', '........', '##.##.##', '##.##.##', '........'],
    '×': ['........', '##...##.', '.##.##..', '..###...', '.##.##..', '##...##.', '........', '........'],
    'Π': ['########', '.##..##.', '.##..##.', '.##..##.', '.##..##.', '.##..##.', '.##..##.', '........'],
    '†': ['..##....', '..##....', '######..', '..##....', '..##....', '..##....', '..##....', '........'],
    '∆': ['........', '...##...', '..####..', '.##..##.', '##....##', '########', '........', '........'],
    'Ψ': ['##.##.##', '##.##.##', '##.##.##', '.######.', '...##...', '...##...', '..####..', '........'],
    '¤': ['........', '##....##', '.######.', '.##..##.', '.##..##.', '.######.', '##....##', '........'],
    '□': ['........', '.######.', '.#....#.', '.#....#.', '.#....#.', '.#....#.', '.######.', '........'],
}
for _ch, _bits in zip('▖▗▘▝▙▛▜▟▚▞', ('0010', '0001', '1000', '0100', '1011', '1110', '1101', '0111', '1001', '0110')):
    _q = [[_bits[(y // 4) * 2 + x // 4] == '1' for x in range(8)] for y in range(8)]   # quarters: TL TR BL BR
    HAND[_ch] = [''.join('#' if c else '.' for c in row) for row in _q]


def glyph(font, ch):
    """The 8x8 bitmap of one character."""
    if ch in HAND:
        im = Image.new('L', (GRID, GRID), 0)
        for y, row in enumerate(HAND[ch]):
            for x, c in enumerate(row):
                if c == '#':
                    im.putpixel((x, y), 255)
        return im
    im = Image.new('L', (GRID, GRID), 0)
    d = ImageDraw.Draw(im)
    d.fontmode = '1'          # no anti-aliasing: crisp pixels
    d.text((0, 0), ch, font=font, fill=255)
    return im


def main():
    from fontTools.ttLib import TTFont
    have = TTFont(FONT).getBestCmap()
    missing = [c for c in CHARS if ord(c) not in have and c not in HAND and c != ' ']
    if missing:
        print('warning: not in the font and not drawn by hand:', ''.join(missing))
    font = ImageFont.truetype(FONT, GRID)
    sheet = Image.new('RGBA', (COLUMNS * TILE_W, ROWS * TILE_H), (0, 0, 0, 0))
    for i, ch in enumerate(CHARS):
        g = glyph(font, ch)
        tile = Image.new('RGBA', (TILE_W, TILE_H), (255, 255, 255, 0))
        tile.putalpha(g)
        sheet.paste(tile, ((i % COLUMNS) * TILE_W, (i // COLUMNS) * TILE_H))
    sheet.save(OUT)
    print('wrote', os.path.abspath(OUT), sheet.size, len(CHARS), 'characters')


if __name__ == '__main__':
    main()
