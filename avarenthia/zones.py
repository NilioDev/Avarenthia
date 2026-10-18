"""Walking the land: every world cell can be entered as a zone of 80x51 tiles.

`>` in open country on the world map takes you down into the zone of that cell; walk off its edge and you are in
the next zone; `<` takes you back up. The world map stays the way to travel; zones are for looking around.

Every tile is a pure function of (world seed, global tile x, y): the world cell and its neighbours are blended
from cell centre to cell centre and roughened with noise, so a forest frays into hills with no seam at a zone edge.
Rivers and roads run from a cell's middle to a point on the edge it shares with the next river or road cell; that
point is a hash of the edge, so both sides draw it the same. Towns, sites, holds, dungeon mouths and places found in
the wild stand in the middle of their zone: walk in (or `>` on a dungeon mouth) and you are there.

On screen the 3x3 zones around you are one map (game.maps['zone'], kind 'wild', m.zone = the centre cell), so
sight and chasing foes run on across the edges. Cross into the next cell and the window moves: what changed in the
old zones is put away in game.zones[(cx, cy)] (tiles, items, what you have seen), and the new ones are made again
from the seed. An untouched zone is never saved.

An ambush on the world map is fought in the zone of its cell; the foes carry o.enc. Cross into the next zone with
no foe beside you and they stay behind.
"""
import random
import zlib

import numpy as np

from . import data as D
from .entities import GameMap

ZW, ZH = 80, 51
KEY = 'zone'

# per world tile: (trees, rocks, water, slopes)
FEEL = {
    D.GRASS: (.04, .005, 0, 0), D.ROAD: (.04, .005, 0, 0), D.FOREST: (.42, .01, 0, 0), D.HILLS: (.07, .07, 0, .42),
    D.MOUNTAIN: (.02, .9, 0, .3), D.SWAMP: (.08, 0, .22, 0), D.WATER: (0, 0, 1, 0), D.SAND: (0, .01, 0, 0),
    D.ENTR: (.06, .18, 0, .2), D.TOWN: (.03, 0, 0, 0), D.CITY: (.01, 0, 0, 0), D.RIVER: (.04, .005, 0, 0),
    D.CASTLE: (.02, .02, 0, .1), D.FORT: (.02, .02, 0, .1),
}
# the finer grain of the land: (trees, rocks, water, slopes, ground); None keeps the tile's own
BIOME = {
    'desert': (.004, .01, None, None, D.SAND), 'dune': (0, 0, None, .1, D.SAND), 'dune_crest': (0, 0, None, .25, D.SAND),
    'bone_sand': (0, .02, None, None, D.SAND), 'beach': (.01, None, None, None, D.SAND), 'cay': (.06, None, None, None, D.SAND),
    'surf': (0, None, None, None, D.SAND), 'atoll_palm': (.12, None, None, None, D.SAND),
    'badlands': (.005, .07, None, .2, D.SAND), 'salt': (0, .01, None, None, D.BAREROCK), 'salt_edge': (.005, None, None, None, D.SAND),
    'savanna': (.03, None, None, None, None), 'steppe': (.012, None, None, None, None), 'meadow': (.015, None, None, None, None),
    'shrubland': (.08, None, None, None, None), 'shrubland_cold': (.06, None, None, None, None),
    'jungle': (.58, None, .03, None, None), 'deep_forest': (.62, None, None, None, None), 'birch': (.34, None, None, None, None),
    'conifer': (.46, None, None, None, None), 'taiga': (.4, None, None, None, None), 'dry_forest': (.3, None, None, None, None),
    'dead_trees': (.2, None, None, None, D.GRIT), 'clearing': (.05, None, None, None, None),
    'petrified': (.12, .03, None, None, D.GRIT), 'marsh': (.04, None, .3, None, D.SWAMP), 'swamp': (.12, None, .28, None, D.SWAMP),
    'floodplain': (.05, None, .12, None, None), 'mangrove': (.32, None, .32, None, D.SWAMP), 'moor': (.01, .03, .06, .1, None),
    'alpine': (.03, .1, None, .3, None), 'tundra': (.01, .01, .02, None, None), 'tundra_hills': (.01, .04, None, .3, None),
    'ice_shelf': (0, None, None, None, D.SNOW), 'ashland': (.02, .03, None, None, D.GRIT), 'scorched': (.01, .02, None, None, D.GRIT),
    'burnt': (.06, None, None, None, D.GRIT), 'karst': (.05, .16, None, .2, None), 'crystal': (0, .14, None, None, D.BAREROCK),
    'crystal_ground': (.01, .06, None, None, D.BAREROCK), 'stone_ground': (.01, .05, None, None, D.BAREROCK),
    'crater_rim': (.02, .12, None, .3, D.BAREROCK), 'ravine_edge': (.04, .12, None, .3, None), 'ravine': (.03, .2, None, .2, None),
    'chasm_edge': (.02, .2, None, .2, D.BAREROCK), 'tar_edge': (.03, None, .1, None, D.GRIT), 'scar_core': (0, .05, None, None, D.GRIT),
    'sinter': (0, .02, .05, None, D.BAREROCK), 'geyser': (0, .02, .05, None, D.BAREROCK), 'hotpool': (0, .02, .08, None, D.BAREROCK),
}
ROADS = (D.ROAD, D.TOWN, D.CITY, D.CASTLE, D.FORT)
SETTLE_LOOK = {'metropolis': ('█', (255, 232, 150), (90, 70, 30)), 'city': ('■', (255, 216, 96), (60, 44, 20)),
               'town': ('⌂', (250, 206, 90), (52, 38, 18)), 'village': ('⌂', (226, 186, 90), (30, 24, 14)),
               'hamlet': ('∩', (196, 160, 96), (30, 24, 14)), 'deephold': ('▼', (255, 200, 90), (60, 40, 20))}
PEACEFUL = ('caravan', 'traveler', 'patrol', 'rivals')


# ------------------------------------------------------------------ noise
def h2(x, y, s):
    """Hash noise in 0..1 for integer lattice points (ints or numpy arrays)."""
    v = (x * 374761393 + y * 668265263 + s * 1442695041) & 0xFFFFFFFF
    v = ((v ^ (v >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((v ^ (v >> 16)) & 0xFFFF) / 65535.0


def vnoise(X, Y, cell, s):
    gx, gy = X / cell, Y / cell
    x0, y0 = np.floor(gx).astype(np.int64), np.floor(gy).astype(np.int64)
    fx, fy = gx - x0, gy - y0
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a, b = h2(x0, y0, s), h2(x0 + 1, y0, s)
    c, d = h2(x0, y0 + 1, s), h2(x0 + 1, y0 + 1, s)
    return (a + (b - a) * fx) * (1 - fy) + (c + (d - c) * fx) * fy


def salt(game):
    return (game.seed % 99991) * 32


def mid(cx, cy, s):
    """The middle of a cell's zone, in global tiles: where its road meets and its town stands."""
    return (cx * ZW + ZW // 2 + int((h2(cx, cy, s + 9) - .5) * 20),
            cy * ZH + ZH // 2 + int((h2(cx, cy, s + 10) - .5) * 12))


def edge_point(ax, ay, bx, by, s):
    """Where a road or river crosses the edge between two cells: the same answer from both sides."""
    if ax != bx and ay != by:                       # diagonal neighbours meet at a corner
        return (max(ax, bx) * ZW, max(ay, by) * ZH)
    k = (min(ax, bx), min(ay, by), ax != bx)
    j = h2(k[0] * 3 + k[2], k[1], s)
    if ax != bx:
        return (max(ax, bx) * ZW, ay * ZH + int(ZH * (.3 + .4 * j)))
    return (ax * ZW + int(ZW * (.3 + .4 * j)), max(ay, by) * ZH)


# ------------------------------------------------------------------ the world map, read once
_CACHE = {}


def _cells(game):
    """Per world cell: the four feelings and the ground tile, as arrays (h, w). Made once per game."""
    om = game.maps['over']
    cut = getattr(game.world, 'clearcut', ())
    key = (id(om), game.seed, len(cut))
    if key in _CACHE:
        return _CACHE[key]
    _CACHE.clear()
    tt = np.array(om.t, dtype=np.int32).reshape(om.h, om.w)
    feel = np.zeros((4, om.h, om.w))
    for tid in np.unique(tt):
        f = FEEL.get(int(tid), FEEL[D.GRASS])
        for k in range(4):
            feel[k][tt == tid] = f[k]
    ground = np.full((om.h, om.w), D.GRASS, dtype=np.int32)
    bio = getattr(om, 'biome', None)
    if bio:
        names = om.biome_names
        ba = np.frombuffer(bytes(bio), dtype=np.uint8).reshape(om.h, om.w) if isinstance(bio, (bytes, bytearray)) \
            else np.array(bio, dtype=np.int32).reshape(om.h, om.w)
        land = (tt != D.WATER) & (tt != D.MOUNTAIN)
        for bi, name in enumerate(names):
            mod = BIOME.get(name)
            if not mod:
                continue
            sel = (ba == bi) & land
            if not sel.any():
                continue
            for k in range(4):
                if mod[k] is not None:
                    feel[k][sel] = mod[k]
            if mod[4] is not None:
                ground[sel] = mod[4]
    ground[tt == D.SAND] = D.SAND
    for i in cut:                                  # where the woodcutters were: stumps, a tree or two left
        feel[0][i // om.w, i % om.w] = .03
    riv = np.frombuffer(bytes(om.river), dtype=np.uint8).reshape(om.h, om.w) if getattr(om, 'river', None) \
        else np.zeros((om.h, om.w), dtype=np.uint8)
    _CACHE[key] = (tt, feel, ground, riv)
    return _CACHE[key]


def things(game):
    """What stands in the middle of a cell: {(cx, cy): (kind, ref)}."""
    w = game.world
    cache = getattr(game, '_zthings', None)
    if cache is not None and cache[0] == (len(w.settlements), len(w.sites), len(w.pois), len(w.holds)):
        return cache[1]
    out = {}
    for c in getattr(w, 'crossroads', ()):
        out[(c['x'], c['y'])] = ('shrine', None)
    for poi in w.pois:
        out[(poi.x, poi.y)] = ('poi', poi.id)
    for d in w.dungeons.values():
        if getattr(d, 'x', None) is not None and game.maps['over'].inb(d.x, d.y) \
                and game.maps['over'].tile(d.x, d.y) == D.ENTR:
            out[(d.x, d.y)] = ('d', d.id)
    for st in w.sites:
        out[(st.x, st.y)] = ('site', st.id)
    for h in w.holds:
        out[(h.x, h.y)] = ('h', h.id)
    for s in w.settlements:
        out[(s.x, s.y)] = ('s', s.id)
    game._zthings = ((len(w.settlements), len(w.sites), len(w.pois), len(w.holds)), out)
    return out


# ------------------------------------------------------------------ making the land
def _line(a, b, s):
    (ax, ay), (bx, by) = a, b
    n = max(abs(bx - ax), abs(by - ay), 1)
    f = np.arange(n + 1) / n
    X, Y = ax + (bx - ax) * f, ay + (by - ay) * f
    wob = (vnoise(X, Y, 9, s) - .5) * 6 * np.sin(np.pi * f)
    px = np.rint(X + (wob if ay != by else 0)).astype(np.int64)
    py = np.rint(Y + (wob if ax != bx else 0)).astype(np.int64)
    return px, py, f


def _paint(mask, px, py, width, ox, oy):
    H, W = mask.shape
    for dy in range(-(width // 2), width - width // 2):
        for dx in range(-(width // 2), width - width // 2):
            lx, ly = px + dx - ox, py + dy - oy
            ok = (lx >= 0) & (lx < W) & (ly >= 0) & (ly < H)
            mask[ly[ok], lx[ok]] = True


def make(game, cx0, cy0, nx=3, ny=3):
    """The tiles of world cells cx0..cx0+nx-1, cy0..cy0+ny-1 as an array (ny*ZH, nx*ZW), and the things in their
    middles as {(local x, local y): (kind, ref)}."""
    om = game.maps['over']
    s = salt(game)
    tt, cfeel, cground, criv = _cells(game)
    W, H = nx * ZW, ny * ZH
    ox, oy = cx0 * ZW, cy0 * ZH
    Y, X = np.mgrid[0:H, 0:W]
    GX, GY = X + ox, Y + oy
    u, v = (GX + .5) / ZW - .5, (GY + .5) / ZH - .5
    u = u + (vnoise(GX, GY, 11, s + 1) - .5) * .9
    v = v + (vnoise(GX, GY, 11, s + 2) - .5) * .9
    i0, j0 = np.floor(u).astype(np.int64), np.floor(v).astype(np.int64)
    fu, fv = u - i0, v - j0
    feel = np.zeros((4, H, W))
    for di, dj, wgt in ((0, 0, (1 - fu) * (1 - fv)), (1, 0, fu * (1 - fv)), (0, 1, (1 - fu) * fv), (1, 1, fu * fv)):
        ci, cj = np.clip(i0 + di, 0, om.w - 1), np.clip(j0 + dj, 0, om.h - 1)
        for k in range(4):
            feel[k] += cfeel[k][cj, ci] * wgt
    ni, nj = np.clip(np.floor(u + .5).astype(np.int64), 0, om.w - 1), np.clip(np.floor(v + .5).astype(np.int64), 0, om.h - 1)
    t = cground[nj, ni].copy()
    n1 = vnoise(GX, GY, 3, s + 3) * .6 + vnoise(GX, GY, 1.3, s + 4) * .4
    n2 = vnoise(GX, GY, 5, s + 5) * .7 + vnoise(GX, GY, 1.7, s + 6) * .3
    n3 = vnoise(GX, GY, 7, s + 7)
    n4 = vnoise(GX, GY, 6, s + 8) * .75 + vnoise(GX, GY, 2, s + 9) * .25
    t[n4 < feel[3]] = D.SLOPE
    t[n1 < feel[0] * 1.05] = D.TREE
    rock = n2 < feel[1]
    t[rock] = D.ROCK
    t[rock & (feel[1] > .55)] = D.CLIFF
    wet = feel[2] > .02
    t[(n3 < feel[2]) & wet] = D.SHALLOW
    t[(n3 < feel[2] - .12) & wet] = D.WATER

    def inside(cx, cy):
        return 0 <= cx < om.w and 0 <= cy < om.h

    def riv(cx, cy):
        return inside(cx, cy) and (criv[cy, cx] or tt[cy, cx] == D.WATER)

    def road(cx, cy):
        return inside(cx, cy) and tt[cy, cx] in ROADS

    shallow, deep, ford = (np.zeros((H, W), dtype=bool) for _ in range(3))
    path, lane = np.zeros((H, W), dtype=bool), np.zeros((H, W), dtype=bool)
    for cy in range(cy0 - 1, cy0 + ny + 1):
        for cx in range(cx0 - 1, cx0 + nx + 1):
            if not inside(cx, cy):
                continue
            m0 = mid(cx, cy, s)
            if criv[cy, cx] and tt[cy, cx] != D.WATER:
                links = 0
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                    if dx and dy and (riv(cx + dx, cy) or riv(cx, cy + dy)):
                        continue                    # a diagonal only where no straight step joins them
                    if riv(cx + dx, cy + dy):
                        links += 1
                        px, py, f = _line(m0, edge_point(cx, cy, cx + dx, cy + dy, s + 21), s + 31)
                        _paint(shallow, px, py, 6, ox, oy)
                        _paint(deep, px, py, 3, ox, oy)
                        g = .2 + .5 * h2(cx * 8 + dx + 1, cy * 8 + dy + 1, s + 23)
                        sel = (f >= g) & (f <= g + .14)  # a ford on every stretch: rivers can be waded
                        _paint(ford, px[sel], py[sel], 3, ox, oy)
                if links <= 1:                      # the river starts here, at a spring
                    _paint(shallow, np.array([m0[0]]), np.array([m0[1]]), 5, ox, oy)
            if road(cx, cy):
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                    if dx and dy and (road(cx + dx, cy) or road(cx, cy + dy)):
                        continue
                    if road(cx + dx, cy + dy):
                        px, py, f = _line(m0, edge_point(cx, cy, cx + dx, cy + dy, s + 22), s + 41)
                        _paint(path, px, py, 3, ox, oy)
                        _paint(lane, px, py, 1, ox, oy)
    t[shallow] = D.SHALLOW
    t[deep & ~ford] = D.WATER
    wetnow = (t == D.WATER) | (t == D.SHALLOW)
    t[path & ~wetnow] = D.PATH
    t[lane & ~wetnow] = D.ROAD
    t[lane & wetnow] = D.BRIDGE
    # what stands in the middle of its cell
    marks = {}
    th = things(game)
    for cy in range(cy0, cy0 + ny):
        for cx in range(cx0, cx0 + nx):
            got = th.get((cx, cy))
            if not got or not inside(cx, cy):
                continue
            mx, my = mid(cx, cy, s)
            lx, ly = mx - ox, my - oy
            kind, ref = got
            if kind == 'd':
                for ddy in range(-3, 4):
                    for ddx in range(-5, 6):
                        if abs(ddx) + abs(ddy) * 2 > 5 and h2(ddx + cx, ddy + cy, s + 3) < .8:
                            t[ly + ddy, lx + ddx] = D.ROCK
                for ddx in (-1, 0, 1):
                    t[ly + 1, lx + ddx] = D.GRASS
                t[ly, lx] = D.ENTR
            else:
                if kind == 's':
                    for ddy in range(-7, 8):
                        for ddx in range(-11, 12):
                            d = (ddx / 11) ** 2 + (ddy / 7) ** 2
                            if .2 < d < 1 and t[ly + ddy, lx + ddx] in (D.GRASS, D.TREE, D.SLOPE) \
                                    and h2(mx + ddx, my + ddy, s + 51) < .7:
                                t[ly + ddy, lx + ddx] = D.FIELD if (ddy + 40) % 3 else D.GRASS
                for ddy in (-1, 0, 1):
                    for ddx in (-1, 0, 1):
                        if not D.TILES[int(t[ly + ddy, lx + ddx])].walk:
                            t[ly + ddy, lx + ddx] = D.GRASS
            marks[(lx, ly)] = (kind, ref)
    return t, marks


# ------------------------------------------------------------------ the window of 3x3 zones
def zones(game):
    return game.__dict__.setdefault('zones', {})


def open_cell(game, cell):
    """Can you go down into this cell's zone?"""
    om = game.maps['over']
    x, y = cell
    return om.inb(x, y) and 0 < x < om.w - 1 and 0 < y < om.h - 1 and om.tile(x, y) not in (D.WATER, D.MOUNTAIN)


def _build(game, m, cell):
    """Fill map m with the 3x3 zones around cell, the changes you made laid back over them."""
    cx, cy = cell
    t, marks = make(game, cx - 1, cy - 1)
    m.t = [int(v) for v in t.ravel()]
    m.base = bytes(np.asarray(t, dtype=np.uint8).ravel())
    m.zone, m.org = (cx, cy), ((cx - 1) * ZW, (cy - 1) * ZH)
    m.marks = marks
    m.seen = bytearray(m.w * m.h)
    m.items = []
    store = zones(game)
    for j in range(3):
        for i in range(3):
            d = store.get((cx - 1 + i, cy - 1 + j))
            if not d:
                continue
            x0, y0 = i * ZW, j * ZH
            for k, tile in d.get('t', {}).items():
                m.t[(y0 + k // ZW) * m.w + x0 + k % ZW] = tile
            for it in d.get('items', ()):
                it.x, it.y = it.x + x0, it.y + y0
                m.items.append(it)
            d['items'] = []
            if d.get('seen'):
                bits = np.unpackbits(np.frombuffer(zlib.decompress(d['seen']), dtype=np.uint8))[:ZW * ZH]
                rows = bits.reshape(ZH, ZW)
                for y in range(ZH):
                    k = (y0 + y) * m.w + x0
                    m.seen[k:k + ZW] = rows[y].tobytes()
    m._look = None
    m.entry = local_mid(game, m)
    name(game, m)


def put_away(game, m):
    """Keep only what changed in the window's zones: tiles, items, what you have seen."""
    if getattr(m, 'zone', None) is None:
        return
    cx, cy = m.zone
    store = zones(game)
    base = m.base
    for j in range(3):
        for i in range(3):
            cell = (cx - 1 + i, cy - 1 + j)
            x0, y0 = i * ZW, j * ZH
            changed = {}
            for y in range(ZH):
                k = (y0 + y) * m.w + x0
                row = m.t[k:k + ZW]
                if bytes(row) != base[k:k + ZW]:
                    for x, tile in enumerate(row):
                        if tile != base[k + x]:
                            changed[y * ZW + x] = tile
            items = []
            for it in m.items:
                if x0 <= it.x < x0 + ZW and y0 <= it.y < y0 + ZH:
                    it.x, it.y = it.x - x0, it.y - y0
                    items.append(it)
            seen = bytearray()
            for y in range(ZH):
                k = (y0 + y) * m.w + x0
                seen += m.seen[k:k + ZW]
            d = {}
            if changed:
                d['t'] = changed
            if items:
                d['items'] = items
            if any(seen):
                d['seen'] = zlib.compress(np.packbits(np.frombuffer(bytes(seen), dtype=np.uint8)).tobytes(), 6)
            if d:
                store[cell] = d
            else:
                store.pop(cell, None)
    m.items = []


def name(game, m):
    from . import lands as LN
    w = game.world
    cx, cy = m.zone
    area = LN.area_at(w, cx, cy)
    m.name = area or w.region_at(cx, cy).name


def mark_look(game, kind, ref):
    w = game.world
    if kind == 's':
        s = w.settlements[ref]
        return SETTLE_LOOK.get(s.kind, SETTLE_LOOK['village'])
    if kind == 'h':
        h = w.holds[ref]
        return ('Ω' if h.kind == 'castle' else '╬'), D.hexrgb(D.FACTIONS[h.faction]['fg']) \
            if isinstance(D.FACTIONS[h.faction]['fg'], str) else D.FACTIONS[h.faction]['fg'], (40, 30, 20)
    if kind == 'site':
        from . import folk as FK
        if FK.unfound(w.sites[ref]):
            return None
        ch, fg = w.sites[ref].glyph
        return ch, fg, (40, 34, 26)
    if kind == 'poi':
        if not w.pois[ref].found:
            return None
        ch, fg = w.pois[ref].glyph
        return ch, fg, (34, 28, 22)
    if kind == 'shrine':
        from . import living as LV
        return LV.SHRINE_LOOK[0], LV.SHRINE_LOOK[1], (40, 32, 22)
    return None


def mark_name(game, kind, ref):
    w = game.world
    if kind == 's':
        return w.settlements[ref].name
    if kind == 'h':
        return w.holds[ref].title
    if kind == 'site':
        return w.sites[ref].name
    if kind == 'poi':
        return w.pois[ref].name
    if kind == 'd':
        return w.dungeons[ref].name
    return 'Crossroads shrine'


def local_mid(game, m, cell=None):
    cx, cy = cell or m.zone
    gx, gy = mid(cx, cy, salt(game))
    return gx - m.org[0], gy - m.org[1]


def free_near(game, m, x, y, avoid=()):
    from .worldgen import cheb
    best = None
    for r in range(0, 30):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if max(abs(dx), abs(dy)) != r:
                    continue
                nx, ny = x + dx, y + dy
                if not m.inb(nx, ny) or (nx, ny) in avoid or (nx, ny) in m.marks:
                    continue
                if D.TILES[m.tile(nx, ny)].walk and not m.mon_at(nx, ny):
                    if best is None or cheb(nx, ny, x, y) < cheb(best[0], best[1], x, y):
                        best = (nx, ny)
        if best:
            return best
    return x, y


def enter(game, cell, near=None):
    """Go down into the zone of a world cell. near: an offset from its middle to stand at."""
    p = game.player
    old = game.maps.get(KEY)
    if old is not None:
        put_away(game, old)
    m = GameMap(KEY, 'wild', 'The land', ZW * 3, ZH * 3, D.GRASS)
    m.radius, m.level = 18, game.world.danger_at(*cell)
    _build(game, m, cell)
    game.maps[KEY] = m
    game.cur = KEY
    game.over_pos = cell
    mx, my = local_mid(game, m)
    tx, ty = (mx + near[0], my + near[1]) if near else (mx, my)
    p.x, p.y = free_near(game, m, tx, ty)
    _seen_over(game, cell)
    sync_wanderers(game)
    game.compute_fov()
    from . import guide as GD
    GD.tip(game, 'land')
    return m


def leave(game):
    """Back up to the world map."""
    m = game.maps.pop(KEY, None)
    if m is not None:
        put_away(game, m)


def cell_of(m, x, y):
    return (x + m.org[0]) // ZW, (y + m.org[1]) // ZH


def _seen_over(game, cell):
    om = game.maps['over']
    cx, cy = cell
    for y in range(cy - 2, cy + 3):
        for x in range(cx - 2, cx + 3):
            if om.inb(x, y):
                om.seen[y * om.w + x] = 1


def fleeing_blocked(game, nx, ny):
    """Stepping into the next zone with a foe of the fight beside you: no."""
    from .worldgen import cheb
    m, p = game.map, game.player
    if cell_of(m, nx, ny) == m.zone:
        return False
    return any(getattr(o, 'enc', False) and not o.is_npc and o.hp > 0 and o.awake and cheb(o.x, o.y, p.x, p.y) <= 1
               for o in m.mons)


def after_move(game):
    """You stepped: into the next zone (the window moves), or onto what stands in a zone's middle."""
    m, p = game.map, game.player
    cell = cell_of(m, p.x, p.y)
    if cell != m.zone:
        recentre(game, m, cell)
        return True
    got = m.marks.get((p.x, p.y))
    if got:
        return arrive(game, got)
    return False


def recentre(game, m, cell):
    """The window moves so that cell is its middle; foes of a fight left behind stay behind."""
    behind = [o for o in m.mons if getattr(o, 'enc', False)]
    left_foes = any(not o.is_npc and o.hp > 0 for o in behind)
    gx0, gy0 = m.org
    put_away(game, m)
    _build(game, m, cell)
    dx, dy = gx0 - m.org[0], gy0 - m.org[1]
    keep = []
    for o in m.mons:
        if getattr(o, 'enc', False) or getattr(o, 'wd', None) is not None:
            continue
        o.x, o.y = o.x + dx, o.y + dy
        if m.inb(o.x, o.y):
            keep.append(o)
    m.mons = keep
    p = game.player
    p.x, p.y = p.x + dx, p.y + dy
    game.over_pos = cell
    m.level = game.world.danger_at(*cell)
    _seen_over(game, cell)
    from . import missions as MS
    esc = MS.escort_wanderer(game)
    if esc:
        esc.x, esc.y = cell
    if game.encounter is not None or getattr(game, 'zone_fight', False):
        if left_foes:
            game.msg('You leave them behind.', 'info')
        game.resolve_encounter()
    sync_wanderers(game)
    game.compute_fov()


def arrive(game, got):
    """Walking into the middle of a zone where a town, a site or a hold stands: you are there."""
    kind, ref = got
    w = game.world
    m, p = game.map, game.player
    from . import events as EV
    if kind == 'd':
        d = w.dungeons[ref]
        game.mark_visit('d', d.id)
        game.msg(f'You stand at the entrance of {d.name}. Press > to descend.', 'info')
        return False
    if kind == 'poi':
        poi = w.pois[ref]
        EV.reveal(game, poi)
        _at_cell(game, poi.x, poi.y, lambda: EV.on_poi(game, poi))
        return False
    if kind == 'shrine':
        from . import living as LV
        cx, cy = m.zone
        sh = LV.shrine_at(game, cx, cy)
        if sh:
            _at_cell(game, cx, cy, lambda: LV.on_shrine(game, sh))
        return False
    if kind == 'site':
        from . import folk as FK
        site = w.sites[ref]
        if FK.unfound(site):
            FK.discover(game, site, 'The trees part.')
        game.mark_visit('site', site.id)
    if kind == 'h':
        from . import war as WAR
        h = w.holds[ref]
        if WAR.is_hostile(game, h.faction):
            f = D.FACTIONS[h.faction]
            game.msg(f"{h.title} ({f['short']}) bars its gates against you. Press > to storm it.", 'bad')
            return False
    return go_in(game, got)


def _at_cell(game, x, y, fn):
    """Run a world-map hook as if you stood on that cell, then come back to the zone."""
    p = game.player
    keep = (game.cur, p.x, p.y)
    game.cur = 'over'
    p.x, p.y = x, y
    try:
        fn()
    finally:
        if game.cur == 'over':
            game.cur, p.x, p.y = keep


def go_in(game, got):
    """Through the gate of what stands in the middle of this zone."""
    kind, ref = got
    w = game.world
    m, p = game.map, game.player
    mx, my = local_mid(game, m)
    cx, cy = m.zone
    sx, sy = (p.x > mx) - (p.x < mx), (p.y > my) - (p.y < my)
    game.over_pos = (cx, cy)
    game.came_from = (cx + sx, cy + sy) if (sx or sy) else None
    if kind == 's':
        from . import war as WAR
        s = w.settlements[ref]
        ok, why = WAR.can_enter(game, s)
        if not ok:
            game.msg(why, 'bad')
            return False
        leave(game)
        game.enter_town(s.id)
        return True
    if kind == 'h':
        leave(game)
        game.enter_hold(ref)
        return True
    if kind == 'site':
        leave(game)
        game.enter_site(ref)
        return True
    if kind == 'd':
        leave(game)
        game.enter_dungeon(ref, 1, 'up')
        return True
    if kind == 'poi':
        poi = w.pois[ref]
        from . import events as EV
        if poi.kind in EV.RUIN_KINDS:
            from . import hidden as HP
            game.cur = 'over'
            p.x, p.y = poi.x, poi.y
            if not HP.vault_open(game, poi):
                game.cur = KEY
                p.x, p.y = mx, my + 1
                return False
            leave(game)
            game.enter_dungeon(poi.did, 1, 'up')
            return True
        arrive(game, got)
    return False


def out_of(game, dx, dy, x, y):
    """Leaving a town, site, hold or dungeon: into the zone of its cell, on the side you walked out."""
    if not open_cell(game, (x, y)):
        return False
    n = max(abs(dx), abs(dy)) or 1
    enter(game, (x, y), near=(round(dx / n * 5), round(dy / n * 4)) if (dx or dy) else (0, 2))
    return True


# ------------------------------------------------------------------ fights and wanderers
def fight(game, cell, lvl, keys, elite, leader, faction):
    """An ambush, fought in the zone of the cell where it fell on you."""
    from .entities import make_monster
    from .worldgen import cheb
    p = game.player
    if game.cur != KEY or game.map.zone != cell:
        enter(game, cell)
    m = game.map
    pid = game.new_id()
    out = []
    far = 6 if game.encounter is None else 10
    spots = [(x, y) for y in range(p.y - far - 3, p.y + far + 4) for x in range(p.x - far - 4, p.x + far + 5)
             if m.inb(x, y) and far <= cheb(x, y, p.x, p.y) <= far + 3 and D.TILES[m.tile(x, y)].walk
             and not m.mon_at(x, y) and (x, y) not in m.marks]
    if not spots:
        spots = [free_near(game, m, p.x + 3, p.y)]
    c = random.choice(spots)
    from .worldgen import free_around
    near = [c] + free_around(game, m, c[0], c[1], 3)
    for i, k in enumerate(keys):
        if i >= len(near):
            break
        el = 2 if (elite == 2 and i == 0) else (1 if elite == 1 else 0)
        mon = make_monster(game, k, near[i][0], near[i][1], lvl + (1 if random.random() < .3 else 0), el)
        if el == 2 and leader:
            mon.name = leader
        mon.pack, mon.awake, mon.enc = pid, True, True
        mon.faction = faction
        out.append(mon)
    m.mons[:0] = out
    game.zone_fight = True
    return m


def foes_left(m):
    return [o for o in m.mons if getattr(o, 'enc', False) and not o.is_npc and o.hp > 0]


def tick(game):
    """After each turn in a zone: a fight won, a hostile band walking into your zone, travellers coming and going."""
    m = game.map
    if getattr(game, 'zone_fight', False) and not foes_left(m):
        game.resolve_encounter()
        return
    if not getattr(game, 'zone_fight', False) and not game.pending:
        from .worldgen import cheb
        cx, cy = m.zone
        wd = next((x for x in game.world.wanderers if x.hostile and x.cooldown == 0 and cheb(x.x, x.y, cx, cy) == 0), None)
        if wd:
            game.start_encounter(wd)
            return
    if game.turn % 10 == 0:
        sync_wanderers(game)


def end_fight(game, m):
    """The fight in this zone is over: those who are left of it go their way."""
    m.mons = [o for o in m.mons if not (getattr(o, 'enc', False) and (o.is_npc or o.hp > 0))
              and getattr(o, 'role', '') != 'escort']
    for o in m.mons:
        o.enc = False
    game.zone_fight = False


def sync_wanderers(game):
    """Travellers, caravans and patrols in the window's cells stand in their zone; bump them to talk."""
    m = game.map
    if getattr(m, 'zone', None) is None:
        return
    from .entities import make_npc
    cx, cy = m.zone
    want = {wd.id: wd for wd in game.world.wanderers if wd.kind in PEACEFUL and not wd.hostile
            and abs(wd.x - cx) <= 1 and abs(wd.y - cy) <= 1}
    have = {}
    for o in m.mons[:]:
        k = getattr(o, 'wd', None)
        if k is None:
            continue
        wd = want.get(k)
        if wd is None or (o.cell != (wd.x, wd.y)):
            m.mons.remove(o)
        else:
            have[k] = o
    s = salt(game)
    for k, wd in want.items():
        if k in have:
            continue
        gx, gy = mid(wd.x, wd.y, s)
        lx = gx - m.org[0] + int((h2(wd.id, 1, s) - .5) * 30)
        ly = gy - m.org[1] + int((h2(wd.id, 2, s) - .5) * 20)
        x, y = free_near(game, m, lx, ly)
        fg = wd.fg if isinstance(wd.fg, str) else '#%02x%02x%02x' % tuple(wd.fg)
        o = make_npc(game, wd.name, 'wanderer', fg, x, y, True, ch='☺' if wd.ch == '@' else wd.ch)
        o.wd, o.cell = k, (wd.x, wd.y)
        m.mons.append(o)


def wanderer_of(game, o):
    k = getattr(o, 'wd', None)
    return next((wd for wd in game.world.wanderers if wd.id == k), None) if k is not None else None


# ------------------------------------------------------------------ seasons, drawn over the zone
def look(game, m, i, lk, st):
    """A zone tile in this season: snow, ice and autumn leaves come from its world cell, never baked in."""
    from . import seasons as SE
    om = game.maps['over']
    x, y = i % m.w, i // m.w
    cx, cy = (x + m.org[0]) // ZW, (y + m.org[1]) // ZH
    if not om.inb(cx, cy):
        return lk
    ci = cy * om.w + cx
    tt = m.t[i]
    ch, fg, bg = lk
    if tt in (D.WATER, D.SHALLOW):
        if _ice(om, ci, st):
            return ('·' if (x * 7 + y * 3) % 4 else '-'), SE.ICE_FG, SE.ICE_BG
        return lk
    if tt in (D.ROAD, D.BRIDGE, D.TOWN, D.CITY, D.ENTR, D.CASTLE, D.FORT):
        return lk
    if _snow(om, ci, st):
        if tt == D.TREE:
            return ch, SE._mix(fg, SE.SNOW_FG, .35), SE.SNOW_BG
        if tt in (D.ROCK, D.CLIFF):
            return ch, SE.SNOW_FG, SE._mix(bg, SE.SNOW_BG, .7)
        return (('·' if (x * 5 + y * 11) % 3 else "'"), SE.SNOW_FG, SE.SNOW_BG)
    if tt == D.TREE and SE.biome(om, ci) in SE.BROADLEAF:
        if st.leaf > 0:
            return ch, SE._mix(fg, SE.LEAVES[(x * 13 + y * 7) % len(SE.LEAVES)], st.leaf), bg
        if st.bare:
            return ch, (118, 104, 92), bg
    return lk


def _snow(om, ci, st):
    from . import seasons as SE
    b = SE.biome(om, ci)
    if b in SE.NO_SNOW or b in SE.SEA:
        return False
    c = SE.cold(om)[ci]
    return c > 1.15 - st.depth or (c >= 1.25 and om.t[ci] in (D.HILLS, D.MOUNTAIN))


def _ice(om, ci, st):
    from . import seasons as SE
    return st.depth > .2 and SE.biome(om, ci) not in SE.SEA and SE.cold(om)[ci] > 1.3 - st.depth


def frozen_at(game, m, x, y):
    """Water in a zone you can walk on now: its world cell's water is frozen hard."""
    from . import seasons as SE
    om = game.maps['over']
    cx, cy = cell_of(m, x, y)
    return om.inb(cx, cy) and _ice(om, cy * om.w + cx, SE.Now(game))
