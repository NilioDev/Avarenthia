"""Dressing and lighting for dungeons, in the spirit of Brogue: pools and lakes, moss and glowing fungus,
bones, rubble and cobwebs, carpets and statues, wall torches and coloured light that pools on the floor."""
import random

from . import data as D
from .data import FLOOR, WALL, ROCK, WATER, SHALLOW, STATUE, DOOR, ODOOR, UP, DOWN

# decoration codes (m.deco); they only change how a floor (or wall) looks, never what it does
MOSS, GRASS, FUNGUS, BONES, RUBBLE, BLOOD, WEB, CARPET, TORCH, CRYSTAL, ASH, SLIME, FILTH, MUD, FIRE = range(1, 16)

DECO_LOOK = {
    MOSS: ([(55, ','), (30, '.'), (15, '"')], (70, 128, 70), None),
    GRASS: ([(60, '"'), (40, "'")], (96, 160, 70), (16, 26, 12)),
    FUNGUS: ([(60, '"'), (40, ',')], (90, 230, 200), (10, 40, 38)),
    BONES: ([(60, ','), (40, '%')], (220, 214, 196), None),
    RUBBLE: ([(60, ','), (40, '.')], (150, 140, 128), None),
    BLOOD: ([(70, '.'), (30, ',')], (150, 20, 20), (52, 8, 8)),
    WEB: ([(60, '"'), (40, ':')], (220, 220, 230), None),
    CARPET: ([(100, '.')], (150, 60, 60), (70, 18, 22)),
    CRYSTAL: ([(100, '*')], (170, 140, 255), (30, 20, 60)),
    ASH: ([(60, '.'), (40, ',')], (110, 100, 96), (24, 20, 20)),
    SLIME: ([(70, '~'), (30, ',')], (120, 200, 80), (16, 34, 10)),
    FILTH: ([(40, '%'), (35, ','), (25, '~')], (140, 112, 60), (30, 22, 10)),
    MUD: ([(50, '.'), (30, ','), (20, '~')], (110, 84, 52), (28, 20, 12)),
    FIRE: ([(100, '☼')], (255, 150, 60), (70, 26, 8)),
}
# (colour, radius) of things that glow
GLOW = {FUNGUS: ((60, 200, 170), 3), TORCH: ((255, 160, 70), 6), CRYSTAL: ((150, 110, 255), 4), FIRE: ((255, 130, 50), 6)}
AMBIENT = {'cave': .30, 'dungeon': .26, 'crypt': .22, 'barrow': .2, 'gloam': .18}


def _blob(m, cx, cy, size, ok):
    """A random organic patch of cells around (cx, cy) satisfying ok(i)."""
    out = set()
    front = [(cx, cy)]
    while front and len(out) < size:
        x, y = front.pop(random.randrange(len(front)))
        if not m.inb(x, y):
            continue
        i = y * m.w + x
        if i in out or not ok(i):
            continue
        out.add(i)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if random.random() < .8:
                front.append((x + dx, y + dy))
    return out


def _floor_cells(m):
    return [i for i, t in enumerate(m.t) if t == FLOOR]


def _connected(m, a, b):
    from .worldgen import bfs
    dist = bfs(m, a[0], a[1], lambda t: D.TILES[t].walk or D.TILES[t].door)
    return dist[b[1] * m.w + b[0]] >= 0


def dress(game, m, d):
    """Decorate a freshly generated dungeon level. d is the Dungeon record."""
    m.deco = bytearray(m.w * m.h)
    m.lights = []
    tag = d.tag
    style = getattr(m, 'style', d.style)
    floors = _floor_cells(m)
    theme = getattr(m, 'theme_cells', None)
    if theme:
        floors = [i for i in floors if i not in theme]       # the theme rooms keep what was drawn for them
    if not floors:
        return
    up = m.t.index(UP) if UP in m.t else floors[0]
    upxy = (up % m.w, up // m.w)
    goal = m.t.index(DOWN) if DOWN in m.t else max(floors, key=lambda i: abs(i % m.w - upxy[0]) + abs(i // m.w - upxy[1]))
    goalxy = (goal % m.w, goal // m.w)
    # water: a lake or a few pools, deep in the middle when that does not cut the level in two
    for _ in range(0 if getattr(m, 'delve', None) else random.randint(1, 3) if style == 'cave' else 0 if hasattr(m, 'rooms') else random.randint(0, 2)):
        c = random.choice(floors)
        cells = _blob(m, c % m.w, c // m.w, random.randint(10, 45), lambda i: m.t[i] == FLOOR)
        for i in cells:
            m.t[i] = SHALLOW
        deep = [i for i in cells if all(m.t[i + o] in (SHALLOW, WATER) for o in (1, -1, m.w, -m.w))]
        for i in deep:
            m.t[i] = WATER
        if deep and not _connected(m, upxy, goalxy):
            for i in deep:
                m.t[i] = SHALLOW
    floors = _floor_cells(m)

    def patch(code, n, size, where=None):
        for _ in range(n):
            c = random.choice(floors if where is None else where)
            for i in _blob(m, c % m.w, c // m.w, size, lambda i: m.t[i] == FLOOR and not m.deco[i]):
                m.deco[i] = code

    if tag == 'den':                    # a kobold warren: filth, gnawed bones, mud and smoky cookfires
        patch(MUD, random.randint(5, 8), 30)
        patch(FILTH, random.randint(6, 10), 7)
        patch(BONES, random.randint(6, 10), 4)
        patch(RUBBLE, random.randint(3, 5), 6)
        patch(SLIME, random.randint(1, 3), 5)
        patch(MOSS, random.randint(1, 3), 12)
        for _ in range(random.randint(2, 3)):
            c = random.choice(floors)
            m.deco[c] = FIRE
            for o in (1, -1, m.w, -m.w):
                if 0 <= c + o < len(m.t) and m.t[c + o] == FLOOR and random.random() < .5:
                    m.deco[c + o] = BONES
    elif style == 'cave':
        patch(MOSS, random.randint(3, 6), 30)
        patch(GRASS, random.randint(1, 3), 20)
        patch(FUNGUS, random.randint(2, 5), random.randint(6, 14))
        patch(RUBBLE, random.randint(2, 4), 8)
        if random.random() < .35:
            patch(CRYSTAL, random.randint(1, 2), 3)
    else:
        patch(RUBBLE, random.randint(2, 5), 6)
        patch(MOSS, random.randint(1, 3), 12)
        if tag == 'crypt':
            patch(BONES, random.randint(4, 8), 5)
            patch(WEB, random.randint(2, 5), 4)
        if random.random() < .5:
            patch(FUNGUS, random.randint(1, 2), 6)
        # carpets in a few rooms, statues by the walls of big ones
        for _ in range(random.randint(1, 3)):
            c = random.choice(floors)
            for i in _blob(m, c % m.w, c // m.w, 40, lambda i: m.t[i] == FLOOR):
                if not m.deco[i]:
                    m.deco[i] = CARPET
        for _ in range(random.randint(2, 6)):
            c = random.choice(floors)
            x, y = c % m.w, c // m.w
            walls = sum(1 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if m.tile(x + dx, y + dy) in (WALL, ROCK))
            near_door = any(m.tile(x + dx, y + dy) in (DOOR, ODOOR) for dx in (-1, 0, 1) for dy in (-1, 0, 1))
            if walls == 1 and not near_door:
                m.t[c] = STATUE
                if not _connected(m, upxy, goalxy):
                    m.t[c] = FLOOR
    if tag in ('lair_dragon',):
        patch(ASH, random.randint(4, 8), 20)
        patch(BONES, random.randint(3, 6), 4)
    elif tag == 'lair_spider':
        patch(WEB, random.randint(8, 14), 10)
        patch(BONES, random.randint(2, 4), 3)
    elif tag == 'lair_orc':
        patch(BONES, random.randint(3, 6), 4)
        patch(BLOOD, random.randint(3, 6), 4)
    elif tag == 'lair_drowned':
        patch(SLIME, random.randint(4, 8), 14)
    elif tag == 'antnest':                  # packed earth, egg chambers and the husks of what the ants brought home
        patch(MUD, random.randint(6, 10), 30)
        patch(FILTH, random.randint(3, 6), 6)
        patch(BONES, random.randint(3, 6), 4)
    elif tag == 'spiderlair':
        patch(WEB, random.randint(10, 16), 12)
        patch(BONES, random.randint(3, 5), 3)
    elif tag == 'warren':                   # a goblin warren: filth, mud, gnawed bones and cookfires
        patch(MUD, random.randint(4, 7), 25)
        patch(FILTH, random.randint(5, 9), 7)
        patch(BONES, random.randint(4, 8), 4)
        for _ in range(random.randint(2, 4)):
            c = random.choice(floors)
            m.deco[c] = FIRE
    elif tag == 'barrow':                   # earth-walled burial halls: bones, grave dirt, a few old offerings
        patch(BONES, random.randint(5, 9), 5)
        patch(RUBBLE, random.randint(3, 6), 8)
        patch(MUD, random.randint(2, 4), 12)
    elif tag == 'gloam':                    # the deep that watches: glowing fungus, slime, crystal
        patch(FUNGUS, random.randint(5, 9), 10)
        patch(SLIME, random.randint(3, 6), 10)
        patch(CRYSTAL, random.randint(1, 3), 3)
    elif tag == 'grotto':                   # a sea cave: weed, slime and the bones of drowned sailors
        patch(SLIME, random.randint(6, 10), 14)
        patch(BONES, random.randint(2, 4), 3)
    elif tag == 'snakeruin':                # old halls half full of drifted sand
        patch(RUBBLE, random.randint(5, 9), 10)
        patch(BONES, random.randint(2, 4), 3)
    # torches on walls next to floors
    n_torch = {'cave': random.randint(0, 3), 'crypt': random.randint(4, 8)}.get(style if style == 'cave' else tag, random.randint(8, 14))
    walls = [i for i, t in enumerate(m.t) if t == WALL and any(
        0 <= i + o < len(m.t) and m.t[i + o] in (FLOOR, SHALLOW) for o in (1, -1, m.w, -m.w))]
    for i in random.sample(walls, min(n_torch, len(walls))):
        m.deco[i] = TORCH
    for i, v in enumerate(m.deco):
        if v in GLOW and (v == TORCH or random.random() < (.35 if v == FUNGUS else .6)):
            col, r = GLOW[v]
            if tag == 'crypt' and v == TORCH:
                col = (110, 170, 255)                # pale witchfire in the crypts
            m.lights.append((i % m.w, i // m.w, col, r))
    for i in getattr(m, 'k5_rubble', ()):          # what fell from the roof in K5's halls
        if m.t[i] == FLOOR and not m.deco[i]:
            m.deco[i] = RUBBLE
    m.ambient = AMBIENT.get(tag, AMBIENT.get(style, .26))


def add_blood(m, x, y, amount=1):
    if m.kind not in ('dungeon', 'wild', 'siege'):
        return
    if getattr(m, 'deco', None) is None:
        m.deco = bytearray(m.w * m.h)
    for _ in range(amount):
        xx, yy = x + random.randint(-1, 1), y + random.randint(-1, 1)
        if m.inb(xx, yy) and D.TILES[m.tile(xx, yy)].walk and m.deco[yy * m.w + xx] not in (TORCH,):
            m.deco[yy * m.w + xx] = BLOOD
    if m.inb(x, y) and D.TILES[m.tile(x, y)].walk:
        m.deco[y * m.w + x] = BLOOD


def deco_look(m, i, look):
    """Apply decoration i of map m to a (glyph, fg, bg) look."""
    v = m.deco[i]
    ch, fg, bg = look
    if v in (TORCH, FIRE):
        import time
        f = .5 + .5 * _wave(time.monotonic() * 2.2, i % 97)
        fg = (255, int(130 + 70 * f), int(40 + 60 * f))
        if v == TORCH:
            return '#', fg, (int(70 + 30 * f), int(30 + 14 * f), 10)
        if m.t[i] == FLOOR:
            return ('☼' if f > .2 else '*'), fg, (int(56 + 24 * f), int(20 + 10 * f), 8)
    spec = DECO_LOOK.get(v)
    if not spec or m.t[i] not in (FLOOR, SHALLOW, D.GRASS, D.PATH, D.SAND):
        return look
    from .look import _h, _pick, _jit
    chars, col, dbg = spec
    r = _h(i, 1, 23)
    if m.t[i] == SHALLOW:
        return ch, col, dbg or bg
    return _pick(r, chars), _jit(col, r, .12), dbg or bg


# ------------------------------------------------------------------ light
def light_map(m):
    """Static light from torches, fungus and crystals: a list of (r, g, b) multipliers, cached on the map."""
    cache = getattr(m, '_light', None)
    if cache is not None:
        return cache
    from . import fov
    amb = getattr(m, 'ambient', .3)
    ar, ag, ab = amb if isinstance(amb, tuple) else (amb, amb, amb)
    lm = [[ar, ag, ab] for _ in range(m.w * m.h)]
    dom = [-1] * (m.w * m.h)          # the strongest light on each cell, which flickers
    dyn = [None] * (m.w * m.h)
    best = [0.0] * (m.w * m.h)
    for li, (lx, ly, col, r) in enumerate(getattr(m, 'lights', ())):
        vis = fov.cells(m, lx, ly, r)
        for y in range(max(0, ly - r), min(m.h, ly + r + 1)):
            for x in range(max(0, lx - r), min(m.w, lx + r + 1)):
                i = y * m.w + x
                if not vis[i]:
                    continue
                dd = ((x - lx) ** 2 + (y - ly) ** 2) ** .5
                k = max(0.0, 1 - dd / (r + .5)) * 1.1
                c = lm[i]
                c[0] += col[0] / 255 * k
                c[1] += col[1] / 255 * k
                c[2] += col[2] / 255 * k
                if k > best[i]:
                    best[i], dom[i] = k, li
                    dyn[i] = (col[0] / 255 * k, col[1] / 255 * k, col[2] / 255 * k)
    m._light = lm
    m._light_dom, m._light_dyn = dom, dyn
    return lm


def _wave(t, seed):
    """Smooth random wobble in -1..1, the same for everyone looking at the same light."""
    import math
    a = math.sin(t * 2.3 + seed * 1.7) + math.sin(t * 5.1 + seed * 3.1) * .6 + math.sin(t * 11.7 + seed * .7) * .35
    return a / 1.95


def flicker(m, li, t):
    """How bright light li is right now: fires and torches flicker, crystals and fungus pulse slowly."""
    import math
    lights = getattr(m, 'lights', ())
    if not 0 <= li < len(lights):
        return 1.0
    col = lights[li][2]
    if col[0] > col[2] + 60:              # warm: a flame
        return .84 + .16 * _wave(t * 1.4, li)
    return .86 + .14 * math.sin(t * (0.9 + (li % 5) * .17) + li * 2.3)


def light_at(m, i, t):
    """The light on cell i at time t, flicker included."""
    lm = light_map(m)
    dom = getattr(m, '_light_dom', None)
    c = lm[i]
    if not dom or dom[i] < 0:
        return c
    f = flicker(m, dom[i], t)
    d = m._light_dyn[i]
    return (c[0] - d[0] * (1 - f), c[1] - d[1] * (1 - f), c[2] - d[2] * (1 - f))


def lit(look, light, glow=None):
    """Colour a look by the light falling on it. glow: extra light colour for the background."""
    ch, fg, bg = look
    lr, lg, lb = light
    fg = (min(255, int(fg[0] * lr)), min(255, int(fg[1] * lg)), min(255, int(fg[2] * lb)))
    tint = max(0.0, (lr + lg + lb) / 3 - .45)
    bg = (min(255, int(bg[0] * min(1.6, lr) + 40 * tint * lr / 1.5)),
          min(255, int(bg[1] * min(1.6, lg) + 40 * tint * lg / 1.5)),
          min(255, int(bg[2] * min(1.6, lb) + 40 * tint * lb / 1.5)))
    return ch, fg, bg
