"""How the land looks: every cell gets its own glyph and shade, from its height, moisture, climate
and a bit of noise, in the spirit of the Dwarf Fortress world map. Cached per map."""
from . import data as D
from .data import (WATER, GRASS, FOREST, MOUNTAIN, SWAMP, HILLS, SAND, ROAD, RIVER, TREE, FLOOR, PATH, FIELD, ROCK,
                   WALL, PLANK)

BG = (13, 11, 10)
NATURAL = {WATER, GRASS, FOREST, MOUNTAIN, SWAMP, HILLS, SAND, RIVER, TREE, FLOOR, PATH, FIELD, ROCK, WALL, PLANK}


def _h(x, y, salt=0):
    n = (x * 374761393 + y * 668265263 + salt * 2246822519) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return (n ^ (n >> 16)) & 0xFFFF


def _mix(a, b, t):
    return (round(a[0] + (b[0] - a[0]) * t), round(a[1] + (b[1] - a[1]) * t), round(a[2] + (b[2] - a[2]) * t))


def _jit(c, r, amt=.1):
    k = 1 + ((r % 1000) / 1000 - .5) * 2 * amt
    return (max(0, min(255, round(c[0] * k))), max(0, min(255, round(c[1] * k))), max(0, min(255, round(c[2] * k))))


def _pick(r, opts):
    """opts: list of (weight, value); r: 0..65535."""
    tot = sum(w for w, _ in opts)
    v = r * tot / 65536
    for w, o in opts:
        if v < w:
            return o
        v -= w
    return opts[-1][1]


def _water_depth(m):
    from collections import deque
    w, h = m.w, m.h
    d = bytearray([9]) * (w * h)
    q = deque()
    for i, t in enumerate(m.t):
        if t != WATER:
            d[i] = 0
            q.append(i)
    while q:
        c = q.popleft()
        nd = d[c] + 1
        if nd > 5:
            continue
        x, y = c % w, c // w
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                ni = ny * w + nx
                if d[ni] > nd and m.t[ni] == WATER:
                    d[ni] = nd
                    q.append(ni)
    return d


RIVER_GLYPH = {  # (up, down, left, right) -> glyph
    (1, 1, 0, 0): '║', (0, 0, 1, 1): '═', (1, 0, 0, 0): '║', (0, 1, 0, 0): '║', (0, 0, 1, 0): '═', (0, 0, 0, 1): '═',
    (0, 1, 0, 1): '╔', (0, 1, 1, 0): '╗', (1, 0, 0, 1): '╚', (1, 0, 1, 0): '╝',
    (1, 1, 0, 1): '╠', (1, 1, 1, 0): '╣', (0, 1, 1, 1): '╦', (1, 0, 1, 1): '╩', (1, 1, 1, 1): '╬', (0, 0, 0, 0): '≈',
}


FENCE_GLYPH = {  # (up, down, left, right) -> glyph
    (1, 1, 0, 0): '│', (0, 0, 1, 1): '─', (1, 0, 0, 0): '│', (0, 1, 0, 0): '│', (0, 0, 1, 0): '─', (0, 0, 0, 1): '─',
    (0, 1, 0, 1): '┌', (0, 1, 1, 0): '┐', (1, 0, 0, 1): '└', (1, 0, 1, 0): '┘',
    (1, 1, 0, 1): '├', (1, 1, 1, 0): '┤', (0, 1, 1, 1): '┬', (1, 0, 1, 1): '┴', (1, 1, 1, 1): '┼', (0, 0, 0, 0): '┼',
}


WALL_GLYPH = {  # (up, down, left, right) -> glyph
    (1, 1, 0, 0): '║', (0, 0, 1, 1): '═', (1, 0, 0, 0): '║', (0, 1, 0, 0): '║', (0, 0, 1, 0): '═', (0, 0, 0, 1): '═',
    (0, 1, 0, 1): '╔', (0, 1, 1, 0): '╗', (1, 0, 0, 1): '╚', (1, 0, 1, 0): '╝',
    (1, 1, 0, 1): '╠', (1, 1, 1, 0): '╣', (0, 1, 1, 1): '╦', (1, 0, 1, 1): '╩', (1, 1, 1, 1): '╬', (0, 0, 0, 0): '■',
}


def _wet(m, x, y):
    if not m.inb(x, y):
        return 0
    i = y * m.w + x
    riv = getattr(m, 'river', None)
    return 1 if (m.t[i] in (RIVER, WATER) or (riv and riv[i])) else 0


def cell(m, i, depth=None):
    """(glyph, fg, bg) for cell i of map m."""
    t = m.t[i]
    x, y = i % m.w, i // m.w
    td = D.TILES[t]
    over = m.kind == 'over'
    r = _h(x, y)
    r2 = _h(x, y, 7)
    elev = m.elev[i] / 255 if over and hasattr(m, 'elev') else .5
    mo = m.moist[i] / 255 if over and hasattr(m, 'moist') else .5
    lat = y / m.h if over else .5
    cold = max(0.0, (.28 - lat) / .28) if over else 0
    hot = max(0.0, (lat - .78) / .22) if over else 0
    if t == GRASS:
        base = _mix((190, 178, 92), (84, 164, 58), min(1, mo * 1.3))
        base = _mix(base, (150, 166, 152), cold * .8)
        base = _mix(base, (196, 170, 96), hot * .7)
        base = _mix(base, scale(base, .8), max(0, elev - .6))
        if over:
            ch = _pick(r, [(24, '.'), (20, ','), (16, "'"), (10, '`'), (18 if mo > .45 else 6, '"'), (6, ' ')])
        else:       # town greens and meadows: calmer, so buildings and fields stand out
            ch = _pick(r, [(45, ' '), (25, '.'), (15, ','), (10, "'"), (5, '"')])
            return ch, _jit((96, 150, 70), r2, .15), (14, 20, 11)
        if cold > .5 and r2 % 5 == 0:
            ch = '·'
        bgc = _mix((15, 20, 10), (20, 18, 10), 1 - mo) if over else BG
        return ch, _jit(base, r2, .16), bgc
    if t in (FOREST, TREE):
        if cold > .35 or elev > .8:
            ch, base = '↑', (44, 108, 74)
        elif hot > .4:
            ch, base = _pick(r, [(1, '♣'), (1, '♠')]), (96, 140, 50)
        else:
            ch = _pick(r, [(55, '♣'), (45, '♠')])
            base = _mix((54, 120, 44), (34, 150, 64), mo)
        if t == TREE and not over:
            ch = _pick(r, [(50, '♣'), (35, '♠'), (15, '↑')])
        return ch, _jit(base, r2, .18), (10, 20, 11) if over else BG
    if t == HILLS:
        base = _mix((112, 120, 70), (150, 134, 96), elev)
        base = _mix(base, (170, 176, 176), cold * .6)
        ch = _pick(r, [(48, '∩'), (26, 'n'), (14, '.'), (12, "'")])
        if ch in ('.', "'"):
            base = _mix(base, (120, 140, 70), .5)
        return ch, _jit(base, r2, .12), (24, 22, 15)
    if t == MOUNTAIN:
        snow = elev > .975 or cold > .3
        base = (232, 234, 240) if snow else _mix((128, 122, 112), (178, 172, 164), (elev - .92) / .08)
        return _pick(r, [(80, '▲'), (20, '^')]), _jit(base, r2, .06), (34, 31, 30) if not snow else (48, 50, 58)
    if t == WATER:
        dd = depth[i] if depth else 3
        if dd <= 1:
            return _pick(r, [(60, '≈'), (40, '~')]), _jit((96, 156, 222), r2, .08), (18, 40, 76)
        if dd <= 3:
            return _pick(r, [(50, '≈'), (30, '~'), (20, ' ')]), _jit((66, 116, 196), r2, .08), (11, 28, 60)
        return _pick(r, [(30, '≈'), (20, '~'), (50, ' ')]), _jit((44, 84, 160), r2, .08), (6, 17, 42)
    if t == RIVER or (t == ROAD and over and getattr(m, 'river', None) and m.river[i]):
        key = (_wet(m, x, y - 1), _wet(m, x, y + 1), _wet(m, x - 1, y), _wet(m, x + 1, y))
        if t == ROAD:       # a bridge: drawn across the river
            vertical = key[0] or key[1]
            return ('═' if vertical else '║'), (176, 132, 80), (14, 34, 64)
        return _pick(r, [(55, '~'), (45, '≈')]), _jit((92, 162, 238), r2, .08), (16, 40, 76)
    if t == SWAMP:
        ch = _pick(r, [(34, '"'), (18, ','), (16, '~'), (14, '√'), (10, '.'), (8, '♣')])
        col = (70, 118, 128) if ch == '~' else (82, 132, 60) if ch == '♣' else _mix((104, 122, 60), (80, 110, 70), mo)
        return ch, _jit(col, r2, .14), (16, 22, 14)
    if t == SAND:
        base = _mix((214, 196, 130), (226, 180, 110), hot)
        return _pick(r, [(60, '.'), (20, ','), (12, '`'), (8, ' ')]), _jit(base, r2, .08), (34, 28, 18) if over else BG
    if t == ROAD:
        return td.ch, _jit(td.fg, r2, .06), td.bg or BG
    if t == FIELD:          # rows of crops and furrows
        if y % 2:
            return _pick(r, [(70, 'ⁿ'), (30, '"')]), _jit((200, 180, 70), r2, .12), (30, 24, 12)
        return '.', _jit((120, 90, 50), r2, .1), (36, 26, 14)
    if t == D.FENCE:        # rails that join up with their neighbours
        key = tuple(1 if m.inb(x + dx, y + dy) and m.t[(y + dy) * m.w + x + dx] == D.FENCE else 0
                    for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)))
        return FENCE_GLYPH.get(key, '─'), _jit((168, 124, 74), r2, .06), (24, 22, 12)
    if t == PATH and not over:      # village lanes: packed earth with ruts and stones
        return _pick(r, [(50, '.'), (25, ','), (15, '·'), (10, ' ')]), _jit((150, 118, 76), r2, .1), _jit((40, 31, 20), r, .06)
    if t in (FLOOR, PATH, PLANK):
        return td.ch, _jit(td.fg, r2, .08), td.bg or BG
    if t == WALL and m.kind == 'town':     # buildings: walls that join up, like a plan of the house
        join = (WALL, D.DOOR, D.ODOOR)
        key = tuple(1 if m.inb(x + dx, y + dy) and m.t[(y + dy) * m.w + x + dx] in join else 0
                    for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)))
        fg = m.wall_fg or (176, 166, 150)
        return WALL_GLYPH.get(key, '■'), _jit(fg, r2, .05), (30, 27, 24)
    if t in (WALL, ROCK):
        fg = m.wall_fg if (t == WALL and m.wall_fg) else td.fg
        if m.kind == 'dungeon':
            return td.ch, _jit(fg, r2, .07), _jit(scale(fg, .32), r, .1)
        return td.ch, _jit(fg, r2, .07), td.bg or BG
    return td.ch, td.fg, td.bg or BG


def scale(c, k):
    return (round(c[0] * k), round(c[1] * k), round(c[2] * k))


def get(m, i):
    """Cached look of cell i; recomputed when the tile changes."""
    cache = getattr(m, '_look', None)
    if cache is None or len(cache) != len(m.t):
        depth = _water_depth(m) if m.kind == 'over' else None
        m._look = [cell(m, j, depth) for j in range(len(m.t))]
        m._look_t = list(m.t)
        cache = m._look
    if m._look_t[i] != m.t[i]:
        m._look_t[i] = m.t[i]
        cache[i] = cell(m, i)
    return cache[i]


TAINT = {
    # kind: (fg tint, bg tint, ground glyphs, tree glyph, tree colour)
    'blight': ((128, 104, 136), (30, 14, 34), [(60, ','), (25, '.'), (15, "'")], '♠', (96, 84, 100)),
    'scorch': ((96, 84, 76), (34, 14, 8), [(45, '.'), (25, ','), (15, '`'), (15, '·')], '♠', (70, 50, 40)),
    'web': ((214, 214, 228), (28, 28, 34), [(35, '"'), (25, '░'), (20, ','), (20, '.')], '♣', (190, 196, 200)),
    'warpath': ((150, 104, 66), (32, 16, 10), [(45, ','), (25, '.'), (15, '~'), (15, 'x')], '♠', (100, 80, 60)),
    'mire': ((92, 112, 72), (14, 24, 20), [(35, '~'), (30, '"'), (20, ','), (15, '≈')], '♣', (70, 96, 70)),
}


def tainted(look, kind, i=0):
    """How a cell looks under the mark of a great evil."""
    ch, fg, bg = look
    tfg, tbg, ground, tree_ch, tree_fg = TAINT[kind]
    r = _h(i, 3, 11)
    if ch in ('♣', '♠', '↑'):
        ch, fg = tree_ch, _mix(fg, tree_fg, .8)
        if kind == 'web' and r % 3 == 0:
            ch = '░'
    elif ch in ('▲', '^', '∩', 'n', '~', '≈', '═', '║', '·') and fg[2] > 60 and kind != 'mire':
        fg = _mix(fg, tfg, .5)
    else:
        ch = _pick(r, ground)
        fg = _jit(tfg, r, .18)
        if kind == 'scorch' and r % 4 == 0:
            ch, fg = '·', (220, 90, 40)          # embers
        if kind == 'warpath' and ch == '~':
            fg = (150, 40, 34)                   # blood
    return ch, fg, _mix(bg, tbg, .7)


def blighted(look, strength=.55):
    return tainted(look, 'blight')
