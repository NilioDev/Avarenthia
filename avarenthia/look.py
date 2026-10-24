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


BIOME_STYLE = {   # biome: (glyph choices, fg, bg) -- the overworld in the Dwarf Fortress manner
    # Dwarf Fortress style: black ground, one strong glyph per biome in a clear colour
    'ocean': ([(75, '≈'), (25, '~')], (34, 58, 160), (2, 4, 20)),
    'sea': ([(75, '≈'), (25, '~')], (52, 92, 196), (4, 8, 30)),
    'shallows': ([(70, '≈'), (30, '~')], (80, 140, 226), (6, 16, 40)),
    'lake': ([(80, '≈'), (20, '~')], (80, 170, 236), (6, 20, 44)),
    'river': ([(1, '≈')], (70, 150, 240), (6, 16, 36)),
    'beach': ([(70, '.'), (30, ',')], (226, 206, 136), (14, 12, 8)),
    'meadow': ([(70, '"'), (15, ','), (15, '.')], (96, 190, 70), (8, 10, 7)),
    'steppe': ([(60, '"'), (25, ','), (15, '.')], (176, 176, 82), (10, 10, 6)),
    'shrubland': ([(45, '∙'), (35, '"'), (20, ',')], (150, 160, 80), (10, 10, 6)),
    'shrubland_cold': ([(45, '∙'), (35, '"'), (20, ',')], (150, 170, 140), (8, 10, 10)),
    'forest': ([(85, '♣'), (15, '♠')], (40, 156, 52), (6, 10, 6)),
    'deep_forest': ([(60, '♣'), (40, '♠')], (24, 116, 40), (4, 8, 4)),
    'conifer': ([(85, '♠'), (15, '♣')], (34, 128, 72), (5, 9, 6)),
    'taiga': ([(70, '↑'), (30, '♠')], (52, 126, 104), (6, 9, 9)),
    'dry_forest': ([(80, '♣'), (20, '"')], (140, 160, 44), (9, 9, 4)),
    'jungle': ([(55, '♣'), (45, '♠')], (60, 210, 70), (4, 10, 4)),
    'savanna': ([(70, '"'), (20, ','), (10, '♣')], (206, 186, 72), (11, 9, 4)),
    'desert': ([(45, '~'), (35, '.'), (20, ',')], (232, 200, 112), (14, 11, 6)),
    'badlands': ([(55, '∩'), (25, '.'), (20, 'n')], (196, 104, 60), (14, 7, 5)),
    'tundra': ([(55, '·'), (25, ':'), (20, '.')], (196, 208, 210), (9, 10, 12)),
    'tundra_hills': ([(70, 'n'), (30, '∩')], (186, 196, 200), (9, 10, 12)),
    'glacier': ([(60, '░'), (40, '▒')], (220, 236, 250), (60, 80, 104)),
    'hills': ([(70, 'n'), (30, '∩')], (120, 160, 70), (8, 9, 6)),
    'mountain': ([(90, '▲'), (10, '^')], (150, 148, 144), (10, 10, 10)),
    'peak': ([(90, '▲'), (10, '^')], (244, 246, 252), (18, 18, 22)),
    'swamp': ([(45, '♣'), (35, '"'), (20, '≈')], (60, 140, 104), (5, 9, 8)),
    'marsh': ([(55, '"'), (30, '≈'), (15, ',')], (100, 166, 130), (6, 10, 9)),
    'ashland': ([(40, '.'), (25, ','), (20, '·'), (15, '"')], (120, 110, 104), (14, 12, 12)),
    'volcano': ([(70, '▲'), (30, '^')], (230, 90, 40), (60, 18, 10)),
    'crater_rim': ([(45, '∩'), (25, 'n'), (20, '.'), (10, '▲')], (168, 140, 120), (34, 26, 22)),
    'crater_lake': ([(50, '≈'), (30, '~'), (20, ' ')], (90, 170, 200), (10, 40, 64)),
    'crater_isle': ([(1, '*')], (255, 220, 160), (40, 30, 26)),
    'chasm': ([(70, ' '), (30, '·')], (60, 40, 34), (0, 0, 0)),
    'chasm_edge': ([(45, '▒'), (35, '░'), (20, ':')], (176, 100, 64), (40, 18, 12)),
    'ravine': ([(60, '░'), (40, ':')], (120, 80, 56), (22, 12, 8)),
    'ravine_edge': ([(50, '▒'), (30, '∩'), (20, ':')], (168, 112, 70), (46, 26, 16)),
    'salt': ([(40, '·'), (25, '░'), (20, ' '), (15, '.')], (236, 236, 228), (120, 116, 108)),
    'geyser': ([(60, '°'), (40, '*')], (230, 250, 255), (40, 100, 110)),
    'hotpool': ([(60, '≈'), (40, '~')], (120, 230, 220), (20, 80, 90)),
    'sinter': ([(40, '.'), (30, '·'), (30, ',')], (220, 200, 150), (60, 54, 44)),
    'elder_tree': ([(1, '♣')], (255, 214, 90), (40, 70, 20)),
    'crystal': ([(55, '♦'), (25, '*'), (20, '^')], (200, 140, 255), (40, 20, 60)),
    'crystal_ground': ([(40, '.'), (30, '·'), (30, '♦')], (130, 200, 230), (24, 22, 40)),
    'whirl_a': ([(60, '≈'), (40, '~')], (150, 200, 240), (14, 40, 80)),
    'whirl_b': ([(60, '~'), (40, ' ')], (70, 110, 190), (4, 12, 32)),
    'whirl_eye': ([(1, 'O')], (220, 240, 255), (0, 0, 10)),
    'reef': ([(40, '°'), (30, '∙'), (30, ','),], (250, 140, 130), (30, 110, 120)),
    'lagoon': ([(50, '≈'), (30, '~'), (20, ' ')], (120, 230, 220), (20, 110, 130)),
    'petrified': ([(50, '↑'), (30, '♠'), (20, '.')], (150, 140, 130), (36, 32, 30)),
    'tar': ([(50, '≈'), (30, '~'), (20, '°')], (96, 84, 110), (4, 3, 6)),
    'bone_sand': ([(50, '.'), (25, ','), (15, '`'), (10, ' ')], (210, 186, 130), (58, 46, 26)),
    'bone_spine': ([(1, '═')], (240, 232, 210), (60, 50, 34)),
    'bone_rib': ([(1, '│')], (230, 222, 200), (50, 42, 28)),
    'bone_skull': ([(1, 'Θ')], (250, 244, 224), (70, 56, 38)),
    'shroom': ([(40, 'τ'), (30, '♠'), (30, '"')], (120, 230, 210), (20, 14, 34)),
    'lava': ([(60, '≈'), (40, '~')], (255, 120, 30), (110, 24, 6)),
    'brine': ([(60, '≈'), (40, '~')], (170, 220, 220), (90, 120, 120)),
    'salt_edge': ([(40, '.'), (30, '·'), (30, ',')], (220, 214, 196), (70, 62, 46)),
    'dune': ([(50, '.'), (30, ' '), (20, ',')], (196, 160, 92), (50, 36, 16)),
    'dune_crest': ([(75, '~'), (25, '≈')], (250, 214, 140), (74, 54, 24)),
    'cay': ([(60, '.'), (40, ',')], (240, 230, 190), (70, 140, 140)),
    'stone_ground': ([(40, '.'), (30, ','), (30, '·')], (150, 144, 136), (30, 28, 26)),
    'tar_edge': ([(40, ','), (30, '.'), (30, '"')], (110, 100, 70), (20, 18, 12)),
    'fjord': ([(50, '≈'), (30, '~'), (20, ' ')], (90, 150, 214), (12, 32, 66)),
    'cliff': ([(50, '▲'), (30, '^'), (20, '∩')], (196, 200, 206), (52, 54, 60)),
    'scorched': ([(40, '.'), (25, ','), (20, '·'), (15, ' ')], (110, 92, 80), (22, 16, 14)),
    'dead_trees': ([(60, '↑'), (25, '♠'), (15, '.')], (120, 104, 92), (22, 16, 14)),
    'scar_core': ([(40, '░'), (30, '▒'), (20, '.'), (10, '*')], (230, 90, 50), (60, 12, 8)),
    'ice_shelf': ([(40, '░'), (30, ' '), (20, '·'), (10, '▒')], (230, 240, 250), (170, 190, 210)),
    'pack_ice': ([(40, '▒'), (30, '░'), (30, '·')], (220, 234, 246), (110, 140, 170)),
    'icy_water': ([(50, '~'), (30, '·'), (20, ' ')], (160, 200, 230), (20, 40, 70)),
    'berg': ([(70, '▲'), (30, '^')], (240, 248, 255), (30, 60, 100)),
    'atoll_palm': ([(60, '♣'), (40, 'τ')], (60, 200, 80), (40, 44, 22)),
    'lagoon_deep': ([(50, '≈'), (30, '~'), (20, ' ')], (80, 170, 200), (8, 46, 76)),
    'surf': ([(60, '~'), (40, '≈')], (150, 190, 230), (20, 50, 96)),
    'reef_flat': ([(60, '~'), (40, '≈')], (120, 220, 210), (20, 90, 110)),
    # the finer grain of the land (lands.py)
    'moor': ([(50, '"'), (30, ','), (20, '∙')], (164, 124, 160), (10, 8, 10)),
    'alpine': ([(55, '"'), (25, 'n'), (20, '·')], (150, 210, 130), (10, 12, 10)),
    'floodplain': ([(65, '"'), (35, ',')], (110, 206, 96), (8, 13, 9)),
    'clearing': ([(70, '"'), (30, '.')], (130, 196, 84), (8, 11, 6)),
    'burnt': ([(45, '↑'), (35, '.'), (20, ',')], (110, 92, 78), (16, 12, 10)),
    'birch': ([(70, '♠'), (30, '↑')], (206, 214, 190), (8, 10, 8)),
    'palms': ([(70, 'τ'), (30, '"')], (110, 200, 80), (16, 14, 6)),
    'oasis': ([(70, '≈'), (30, '~')], (90, 210, 226), (8, 46, 56)),
    'mangrove': ([(50, '♣'), (30, '≈'), (20, '"')], (70, 140, 86), (6, 14, 14)),
    'karst': ([(50, 'n'), (30, '∩'), (20, '·')], (206, 204, 184), (14, 14, 12)),
    'sinkhole': ([(1, 'O')], (120, 116, 104), (0, 0, 0)),
    'mesa': ([(65, '■'), (35, '▀')], (206, 100, 58), (60, 24, 14)),
    'canyon': ([(50, '.'), (30, ','), (20, ':')], (206, 146, 94), (32, 16, 10)),
}

OVER_NATURAL = {WATER, GRASS, FOREST, MOUNTAIN, SWAMP, HILLS, SAND, RIVER}


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
    if t == D.SECRET:                               # a hidden door looks like any other wall
        t = WALL
    x, y = i % m.w, i // m.w
    td = D.TILES[t]
    over = m.kind == 'over'
    bio = getattr(m, 'biome', None) if over else None
    if bio is not None and t in OVER_NATURAL:
        b = m.biome_names[bio[i]]
        if t == RIVER:
            b = 'river'
        st = BIOME_STYLE.get(b)
        if st:
            opts, fg, bg = st
            r, r2 = _h(x, y), _h(x, y, 7)
            if b == 'river':           # rivers as joined lines, as on the Dwarf Fortress world map
                key = (_wet(m, x, y - 1), _wet(m, x, y + 1), _wet(m, x - 1, y), _wet(m, x + 1, y))
                return RIVER_GLYPH.get(key, '≈'), _jit(fg, r2, .06), bg
            ch = _pick(r, opts)
            if b == 'volcano' and r % 4 == 0:
                ch, fg = '*', (255, 180, 60)
            return ch, _jit(fg, r2, .12), bg
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
    if t == ROAD and over:
        return road_look(m, i, x, y)
    if t == RIVER:
        key = (_wet(m, x, y - 1), _wet(m, x, y + 1), _wet(m, x - 1, y), _wet(m, x + 1, y))
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
    if t == D.SLOPE:        # a grassy hill with homes dug into it: a darker slope round a lighter top
        key = sum(1 for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0))
                  if m.inb(x + dx, y + dy) and m.t[(y + dy) * m.w + x + dx] in (D.SLOPE, D.EARTH))
        if key == 4:
            return _pick(r, [(40, ' '), (25, '"'), (20, ','), (15, '.')]), _jit((120, 200, 90), r2, .12), (34, 66, 26)
        return _pick(r, [(55, '∩'), (45, 'n')]), _jit((120, 170, 80), r2, .1), (22, 44, 17)
    if t == D.EARTH:        # the walls of a hole in a hill; round windows where they face the open air
        join = (D.EARTH, D.DOOR, D.ODOOR)
        key = tuple(1 if m.inb(x + dx, y + dy) and m.t[(y + dy) * m.w + x + dx] in join else 0
                    for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)))
        below = m.t[(y + 1) * m.w + x] if m.inb(x, y + 1) else None
        near_door = any(m.inb(x + dx, y) and m.t[y * m.w + x + dx] in (D.DOOR, D.ODOOR) for dx in (-1, 1))
        if below in (D.SLOPE, D.PATH, GRASS) and key in ((0, 0, 1, 1),) and not near_door and r % 3 == 0:
            return '°', (250, 220, 130), (46, 34, 20)
        return WALL_GLYPH.get(key, '■'), _jit((160, 120, 76), r2, .05), (46, 34, 20)
    if t == D.HEDGE:
        return _pick(r, [(60, '♣'), (40, '♠')]), _jit((44, 122, 44), r2, .14), (8, 20, 8)
    if t == D.BRIDGE:       # the deck runs the way the road does, across the water
        run_ns = sum(1 for dy in (-2, -1, 1, 2) if m.inb(x, y + dy) and m.t[(y + dy) * m.w + x] == D.BRIDGE)
        run_we = sum(1 for dx in (-2, -1, 1, 2) if m.inb(x + dx, y) and m.t[y * m.w + x + dx] == D.BRIDGE)
        stone = getattr(m, 'stone_bridges', False)
        if m.kind == 'dungeon':          # underground the walls are double lines, so the deck is drawn plainer
            fire = any(m.inb(x + dx, y + dy) and m.t[(y + dy) * m.w + x + dx] == D.LAVA for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            return ('│' if run_ns > run_we else '='), _jit((176, 128, 80), r2, .06), (52, 18, 6) if fire else (14, 26, 48)
        return ('║' if run_ns > run_we else '═'), _jit((190, 184, 170) if stone else (176, 128, 80), r2, .06), \
            (60, 58, 54) if stone else (44, 30, 16)
    if t == D.DOOR and getattr(m, 'round_doors', False):     # halfling doors: round, and painted
        return '○', [(200, 70, 50), (220, 180, 60), (60, 130, 60), (70, 110, 190)][r % 4], (30, 22, 14)
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
        if m.kind == 'dungeon' or getattr(m, 'underground', False):
            if not _face(m, x, y):              # the rock beyond the walls: a quiet speckle, never a wall
                return rock_look(m, r, r2)
            if t == WALL and getattr(m, 'rooms', None) is not None:    # built halls: thin walls that join up
                key = tuple(1 if m.inb(x + dx, y + dy) and (m.t[(y + dy) * m.w + x + dx] in (D.DOOR, D.ODOOR, D.VAULTDOOR) or (
                    m.t[(y + dy) * m.w + x + dx] in (WALL, D.SECRET) and _face(m, x + dx, y + dy))) else 0
                    for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)))
                return WALL_GLYPH.get(key, '■'), _jit(fg, r2, .05), (30, 27, 24)
            return td.ch, _jit(fg, r2, .07), _jit(scale(fg, .32), r, .1)
        return td.ch, _jit(fg, r2, .07), td.bg or BG
    return td.ch, td.fg, td.bg or BG


def _face(m, x, y):
    """A wall that faces open ground: something other than rock lies beside it, straight or slanting."""
    for dy in (-1, 0, 1):
        yy = y + dy
        if not 0 <= yy < m.h:
            continue
        for dx in (-1, 0, 1):
            xx = x + dx
            if 0 <= xx < m.w and m.t[yy * m.w + xx] not in (WALL, ROCK, D.SECRET):
                return True
    return False


# the tint of the rock beyond the walls, by the kind of ground (Nilio, 22 October 2026)
ROCK_TINT = {'stone': (84, 84, 90), 'earth': (98, 76, 54), 'basalt': (62, 58, 66)}
ORE_GLINT = ((212, 172, 80), (190, 120, 80), (170, 176, 190))


def rock_kind(m):
    """Grey stone, brown earth, or dark basalt deep down."""
    k = getattr(m, 'rock', None)
    if k:
        return k
    d = getattr(m, 'depth', 0) or 0
    tag = getattr(m, 'dtag', '')
    if tag in ('lair_dragon', 'gloam') or d >= 4:
        return 'basalt'
    if tag in ('den', 'cave', 'warren', 'antnest', 'barrow', 'spiderlair', 'lair_spider'):
        return 'earth'
    return 'stone'


def rock_look(m, r, r2):
    """Solid rock: a sparse speckle in a dim earth colour, the same each time you look; a glint of ore in a mine."""
    tint = ROCK_TINT[rock_kind(m)]
    if getattr(m, 'mine_rock', False) and r % 53 == 0:
        return '*', ORE_GLINT[r2 % 3], (8, 8, 9)
    ch = _pick(r, [(20, '#'), (7, '·'), (73, ' ')])
    return ch, _jit(tint, r2, .12), (8, 8, 9)


ROAD_JOIN = {D.ROAD, D.TOWN, D.CITY, D.ENTR, D.CASTLE, D.FORT}
ROAD_FG = (214, 164, 88)          # ochre
MAIN_FG = (250, 200, 110)
ROAD_BG = (44, 31, 18)            # a strip of trodden earth under the road
MAIN_BG = (58, 40, 22)
PATH_FG = (138, 160, 116)         # the old ways: faint grey-green


def _ground_bg(m, i):
    bio = getattr(m, 'biome', None)
    if bio is None:
        return BG
    st = BIOME_STYLE.get(m.biome_names[bio[i]])
    return st[2] if st else BG


def road_look(m, i, x, y):
    """Roads on the world map as joined lines: the great roads between cities doubled, the rest single,
    and bridges where they cross a river."""
    w = m.w
    main = getattr(m, 'main_road', ())
    riv = getattr(m, 'river', None)
    if riv and riv[i]:
        wet = (_wet(m, x, y - 1), _wet(m, x, y + 1), _wet(m, x - 1, y), _wet(m, x + 1, y))
        # the river runs one way, the bridge the other
        return ('╫' if (wet[0] or wet[1]) and not (wet[2] or wet[3]) else '╪'), MAIN_FG, (14, 34, 64)

    def j(dx, dy):
        if not m.inb(x + dx, y + dy):
            return 0
        return 1 if m.t[(y + dy) * w + x + dx] in ROAD_JOIN else 0
    key = (j(0, -1), j(0, 1), j(-1, 0), j(1, 0))
    if i in main:
        return WALL_GLYPH.get(key, '═').replace('■', '═'), MAIN_FG, MAIN_BG
    return FENCE_GLYPH.get(key, '─'), ROAD_FG, ROAD_BG


def scale(c, k):
    return (round(c[0] * k), round(c[1] * k), round(c[2] * k))


def get(m, i):
    """Cached look of cell i; recomputed when the tile changes."""
    cache = getattr(m, '_look', None)
    if cache is None or len(cache) != len(m.t):
        depth = _water_depth(m) if m.kind == 'over' else None
        m._look = [_decorate(m, j, cell(m, j, depth)) for j in range(len(m.t))]
        m._look_t = list(m.t)
        cache = m._look
    if m._look_t[i] != m.t[i]:
        m._look_t[i] = m.t[i]
        cache[i] = _decorate(m, i, cell(m, i))
        if m.kind == 'dungeon':                 # a wall dug away: the walls round it face the open now
            x, y = i % m.w, i // m.w
            for j in (i - m.w - 1, i - m.w, i - m.w + 1, i - 1, i + 1, i + m.w - 1, i + m.w, i + m.w + 1):
                if 0 <= j < len(m.t) and abs(j % m.w - x) <= 1:
                    cache[j] = _decorate(m, j, cell(m, j))
    return cache[i]


def _decorate(m, i, look):
    """Things drawn over the land itself: the shadow of what hangs in the sky, bones in the sand, the shard."""
    sh = getattr(m, 'shadow', None)
    ov = getattr(m, 'over', None)
    if not sh and not ov:
        return look
    ch, fg, bg = look
    if sh and i in sh:
        fg, bg = scale(fg, .55), scale(bg, .55)
    if ov and i in ov and m.t[i] not in (D.ROAD, D.TOWN, D.CITY, D.ENTR, D.CASTLE, D.FORT):
        och, ofg, obg = ov[i]
        ch, fg, bg = och, tuple(ofg), (tuple(obg) if obg is not None else bg)
    return ch, fg, bg


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
