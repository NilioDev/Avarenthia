"""Ctrl+G in the editor: make with a maker (round 55). The game's own makers run on the kept Try world
(`try world.sav`): every dungeon kind, every kind of place on the land, every kind of settlement, and the land of each
biome as you walk it in its zone. What one makes becomes an ordinary drawing: a room when it fits in 40 x 30, else a
whole place with the maker's floors as its floors. The game does not know a maker began it.

With a rectangle selected in a whole place, Ctrl+G makes a maker area instead (drawnplaces.fill_area): the game fills
it anew in every world, joined to what is drawn round it."""
import random

from .. import data as D
from .. import drawnplaces as DP
from .. import pieces as P
from ..entities import GameMap
from .model import Room, PlaceDoc, MAX_W, MAX_H, _name_of

STATES = ('as made',) + ('lived', 'fallen', 'held', 'overgrown', 'flooded', 'burnt', 'frozen', 'stricken', 'haunted',
                         'besieged', 'plundered', 'settled', 'sealed', 'emptied')
CREATURES = ('as ?', 'as drawn', 'none')
UPWARD = ('tower', 'upper')                       # styles whose deeper floors go up
SKIP_SITES = ('drawn',)
SKIP_STYLES = ('drawn', 'tower', 'upper')       # towers and upper floors come with their place
SKIP_TAGS = ('skyseat',)
_SIGN = {}
for _ch, _t in P.LEGEND.items():
    _SIGN.setdefault(_t, _ch)
_SIGN.update({D.DOOR: "'", D.UP: '<', D.DOWN: '>', D.ROCK: ' '})
WAYS_OUT = (D.ENTR,)                              # a place's mouth to what lies below


def _dress_tiles():
    from .. import dressing as DR
    out = {DR.tile(name) for things in DR.SETS.values() for name, _how, _n in things}
    for ch in 'stbcgmkhawfejyp%_q':
        out.add(P.LEGEND[ch])
    return out - {D.FLOOR, D.WALL, D.GRASS}


def nice(word):
    return word.replace('_', ' ')


class Maker:
    """One entry of the list: a kind of thing the game makes, and the things of that kind in the Try world."""

    def __init__(self, mid, group, label, how, pool, floors=1, states=False, area=False):
        self.id, self.group, self.label, self.how, self.pool = mid, group, label, how, pool
        self.floors = floors          # how many floors it can give (1: one map)
        self.states = states          # it takes a state (the more makers' places)
        self.area = area              # it can fill a maker area


def makers(game):
    """Every maker of the Try world, in groups: Dungeons, Places, Settlements, Land."""
    w = game.world
    out = []
    dg = {}
    for did, d in w.dungeons.items():
        if d.style in SKIP_STYLES or d.tag in SKIP_TAGS:
            continue
        key = getattr(d, 'maker', None) or (d.tag if d.style in ('rooms', 'cave') else d.style)
        dg.setdefault(key, []).append(did)
    for key in sorted(dg):
        ds = [w.dungeons[i] for i in dg[key]]
        most = max(d.depth for d in ds)
        out.append(Maker('dungeon:' + key, 'DUNGEONS', nice(key), 'dungeon', dg[key], min(4, most),
                         states=any(getattr(d, 'maker', None) for d in ds)))
    st = {}
    for s in w.sites:
        if s.kind in SKIP_SITES:
            continue
        people = getattr(s, 'people', None)
        key = s.kind + (f', {people}' if people and s.kind in ('temple', 'tower', 'barrow', 'monastery', 'fort',
                                                             'manor', 'hall') else '')
        st.setdefault(key, []).append(s.id)
    above = {}
    for did, d in w.dungeons.items():
        if d.style in UPWARD and getattr(d, 'site', None) is not None:
            above[d.site] = did
    game._made_above = above
    for key in sorted(st):
        more = [w.dungeons[getattr(w.sites[i], 'below', None)].depth if getattr(w.sites[i], 'below', None) in w.dungeons
                else w.dungeons[above[i]].depth if i in above else 0 for i in st[key]]
        out.append(Maker('site:' + key, 'PLACES', nice(key), 'site', st[key], 1 + min(3, max(more))))
    se = {}
    for i, s in enumerate(w.settlements):
        race = getattr(s, 'race', None)
        key = s.kind + (f', {race}' if race and race != 'human' else '')
        se.setdefault(key, []).append(i)
    for key in sorted(se):
        out.append(Maker('settle:' + key, 'SETTLEMENTS', nice(key), 'settle', se[key]))
    om = game.maps['over']
    cells = {}
    bio = getattr(om, 'biome', None)
    if bio is not None:
        for i, b in enumerate(bio):
            name = om.biome_names[b]
            if name not in DP.WATERY and D.TILES[om.t[i]].walk:
                cells.setdefault(name, []).append(i)
    for key in sorted(cells):
        out.append(Maker('land:' + key, 'LAND', nice(key), 'land', cells[key], area=True))
    out.append(Maker('rooms', 'FOR AN AREA', 'rooms (classic)', 'area', [0], area=True))
    out.append(Maker('cave', 'FOR AN AREA', 'cave', 'area', [0], area=True))
    return out


class Made:
    """What a maker made: its floors [(name, GameMap)] from the top down, which floor is the ground, and a line."""

    def __init__(self, floors, ground, line):
        self.floors, self.ground, self.line = floors, ground, line


def make(game, mk, n=0, floors=1, state='as made', size=(80, 50)):
    """Make one with the maker: the n-th roll (another of its kind in the world, another seed). Returns a Made or
    raises ValueError with a plain reason."""
    rnd = random.Random(n * 7919 + len(mk.id) * 31 + sum(map(ord, mk.id)))
    pick = mk.pool[rnd.randrange(len(mk.pool))] if mk.pool else None
    saved = random.getstate()
    random.seed(rnd.random())
    try:
        return _make(game, mk, pick, max(1, min(mk.floors, floors)), state, size, rnd)
    except ValueError:
        raise
    except Exception as e:                       # a maker that needs more of the world than the Try world has
        raise ValueError(f'the {mk.label} maker could not make one here ({type(e).__name__}: {e})')
    finally:
        random.setstate(saved)


def _make(game, mk, pick, floors, state, size, rnd):
    from .. import worldgen as WG
    w = game.world
    if mk.how == 'dungeon':
        d = w.dungeons[pick]
        old = getattr(d, 'state', None)
        if mk.states and state != 'as made':
            d.state = state
        try:
            maps = [WG.gen_dungeon(game, pick, k) for k in range(1, min(floors, d.depth) + 1)]
        finally:
            if mk.states:
                d.state = old
        up = d.style in UPWARD
        names = [f"{'up' if up else 'down'} {k}" for k in range(1, len(maps) + 1)]
        fl = list(zip(names, maps))
        if up:
            fl.reverse()
        return Made(fl, None, f'{d.name}, level 1' + (f' to {len(maps)}' if len(maps) > 1 else ''))
    if mk.how == 'site':
        from .. import sites as ST
        s = w.sites[pick]
        m = ST.gen_site_map(game, s)
        game.maps[s.map_key] = m                   # the floors over it are drawn over its map
        fl = [('ground', m)]
        below = getattr(s, 'below', None)
        up = getattr(game, '_made_above', {}).get(s.id)
        if floors > 1 and below in w.dungeons:
            fl += [(f'down {k}', WG.gen_dungeon(game, below, k)) for k in range(1, min(floors - 1, w.dungeons[below].depth) + 1)]
        elif floors > 1 and up in w.dungeons:
            fl = [(f'up {k}', WG.gen_dungeon(game, up, k))
                  for k in range(min(floors - 1, w.dungeons[up].depth), 0, -1)] + fl
        return Made(fl, 'ground', s.name)
    if mk.how == 'settle':
        from .. import towns as TW
        s = w.settlements[pick]
        return Made([('ground', TW.gen_settlement_map(game, s))], 'ground', s.name)
    if mk.how == 'land':
        from .. import zones as ZN
        om = game.maps['over']
        cx, cy = pick % om.w, pick // om.w
        nx, ny = -(-size[0] // ZN.ZW), -(-size[1] // ZN.ZH)
        t, _marks = ZN.make(game, max(0, cx - nx // 2), max(0, cy - ny // 2), nx, ny)
        m = GameMap('made', 'wild', 'land', t.shape[1], t.shape[0], D.GRASS)
        m.t = [int(v) for v in t.ravel()]
        return Made([('ground', m)], 'ground', f'{mk.label} near {cx},{cy}')
    if mk.how == 'area':
        rows = DP.area_tiles(game, mk.id, size[0], size[1], rnd)
        if rows is None:
            raise ValueError(f'the {mk.label} maker could not fill {size[0]} x {size[1]}')
        m = GameMap('made', 'dungeon', 'area', size[0], size[1], D.WALL)
        m.t = [v for row in rows for v in row]
        return Made([('down 1', m)], None, f'{mk.label}, {size[0]} x {size[1]}')
    raise ValueError('no such maker')


def area_preview(game, what, w, h, n=0):
    """What a maker area of w x h would hold in one world (the editor shows it)."""
    rows = DP.area_tiles(game, what, w, h, random.Random(n * 977 + w * 13 + h))
    if rows is None:
        return None
    m = GameMap('made', 'dungeon', 'area', w, h, D.WALL)
    m.t = [v for row in rows for v in row]
    return m


# ------------------------------------------------------------------ what was made, as a drawing
def frame_of(made, frame=None):
    """(x0, y0, w, h): the part taken, the whole map when no frame is dragged; never bigger than 120 x 80."""
    W = max(m.w for _n, m in made.floors)
    H = max(m.h for _n, m in made.floors)
    if frame:
        (ax, ay), (bx, by) = frame
        x0, y0 = max(0, min(ax, bx)), max(0, min(ay, by))
        x1, y1 = min(W - 1, max(ax, bx)), min(H - 1, max(ay, by))
        x0, y0 = min(x0, x1), min(y0, y1)
        w, h = x1 - x0 + 1, y1 - y0 + 1
    else:
        x0, y0, w, h = 0, 0, W, H
    big = DP.SIZES[-1]
    if w > big[0]:
        x0, w = x0 + (w - big[0]) // 2, big[0]
    if h > big[1]:
        y0, h = y0 + (h - big[1]) // 2, big[1]
    return x0, y0, w, h


def _sign(t, room, dress, keep_dress, lost):
    if not keep_dress and t in dress:
        return '.'
    ch = _SIGN.get(t)
    if ch is not None:
        return ch
    ch = room.letter_for(_name_of(t), None)
    if ch is None:                                # all 26 letters taken: the nearest plain sign
        lost.add(D.TILES[t].name)
        return '.' if D.TILES[t].walk else '#'
    return ch


def _draw(room, m, x0, y0, ox, oy, w, h, opts, dress, lost, persons):
    for y in range(h):
        for x in range(w):
            sx, sy = x0 + x, y0 + y
            if not m.inb(sx, sy):
                continue
            room.set(ox + x, oy + y, _sign(m.tile(sx, sy), room, dress, opts['dressing'], lost))
    if opts['creatures'] == 'none':
        return
    for mon in m.mons:
        x, y = mon.x - x0, mon.y - y0
        if not (0 <= x < w and 0 <= y < h) or room.get(ox + x, oy + y) in " #+'<>":
            continue
        if getattr(mon, 'k', None) == 'npc':
            if persons:
                room.persons.append((mon.name.replace(' at ', ' by ').replace('"', "'"), (ox + x, oy + y), ''))
            continue
        k = getattr(mon, 'k', None)
        room.spots[(ox + x, oy + y)] = k if opts['creatures'] == 'as drawn' and k in D.MONSTERS else '?'


def to_drawing(made, opts, frame=None, name='made'):
    """The Made as a Room (a part of one floor that fits in 40 x 30) or a PlaceDoc. opts: creatures, dressing.
    Returns (drawing, a line for the status bar)."""
    x0, y0, w, h = frame_of(made, frame)
    dress = _dress_tiles()
    lost = set()
    one = len(made.floors) == 1
    if one and frame and w <= MAX_W and h <= MAX_H:     # a part dragged out of it: a room
        r = Room(name, w, h)
        _draw(r, made.floors[0][1], x0, y0, 0, 0, w, h, opts, dress, lost, False)
        for y in range(h):
            for x in range(w):
                if r.get(x, y) in '<>':
                    r.set(x, y, '.')
        _gate(r)
        r.undo.clear()
        return r, _line(made, w, h, lost, f'a room of {w} x {h}')
    size = next((s for s in DP.SIZES if s[0] >= w and s[1] >= h), DP.SIZES[-1])
    d = PlaceDoc(name, size)
    ox, oy = (size[0] - w) // 2, (size[1] - h) // 2
    names = [n for n, _m in made.floors]
    for fname, m in made.floors:
        f = d.add_floor(fname)
        _draw(f, m, x0, y0, ox, oy, w, h, opts, dress, lost, fname == 'ground')
    if made.ground is None:                         # a dungeon: a small house over its stair on the ground
        g = d.add_floor('ground')
        cx, cy = size[0] // 2, size[1] // 2
        for y in range(cy - 3, cy + 4):
            for x in range(cx - 5, cx + 6):
                g.set(x, y, '#' if x in (cx - 5, cx + 5) or y in (cy - 3, cy + 3) else '.')
        g.set(cx - 5, cy, '+')
        g.set(cx, cy, '<' if names[0].startswith('up') else '>')
    _stairs(d)
    if made.ground is not None and not any('+' in ''.join(row) for row in d.floor('ground').grid):
        _way_in(d.floor('ground'))
    for f in d.floors:
        f.undo.clear()
        f.dirty = False
    return d, _line(made, w, h, lost, f'a whole place of {size[0]} x {size[1]}')


def _line(made, w, h, lost, what):
    s = f'Made: {what}' + (f', {len(made.floors) + (made.ground is None)} floors.' if len(made.floors) > 1 or
                            made.ground is None else '.')
    if lost:
        s += ' Some tiles had no letter left: floor or wall.'
    return s


def _gate(r):
    """A room needs a way in: a door it has, or one cut in its edge where the floor meets it."""
    doors = [(x, y) for y in range(r.h) for x in range(r.w) if r.get(x, y) == "'"]
    if doors:
        x, y = min(doors, key=lambda c: (abs(c[0] - r.w // 2) + abs(c[1] - r.h)))
        r.set(x, y, '+')
        return
    edge = [(x, y) for y in range(r.h) for x in range(r.w) if (x in (0, r.w - 1) or y in (0, r.h - 1))
            and r.get(x, y) not in ' #']
    if edge:
        x, y = min(edge, key=lambda c: (abs(c[0] - r.w // 2) + abs(c[1] - r.h)))
        r.set(x, y, '+')


def _stairs(d):
    """Each floor's stairs match the floors above and below it: a stair to no floor becomes floor, and a floor that
    lacks the stair to its twin gets one by the stair it has."""
    order = d.order()
    for i, f in enumerate(order):
        above, below = i > 0, i + 1 < len(order)
        for y in range(f.h):
            for x in range(f.w):
                ch = f.get(x, y)
                if (ch == '<' and not above) or (ch == '>' and not below):
                    f.set(x, y, '.')
        for want, need in (('<', above), ('>', below)):
            if need and not any(want in ''.join(row) for row in f.grid):
                spot = next(((x, y) for y in range(f.h) for x in range(f.w) if f.get(x, y) == '.'), None) or \
                    next(((x, y) for y in range(f.h) for x in range(f.w) if f.get(x, y) in '",'), None)
                if spot:
                    f.set(*spot, want)


def _way_in(g):
    """The + on the ground floor where the way in from the west edge comes: the first walkable cell from the west on
    the middle rows."""
    rows = sorted(range(1, g.h - 1), key=lambda y: abs(y - g.h // 2))
    for y in rows:
        for x in range(1, g.w):
            ch = g.get(x, y)
            if ch in '.",' or (ch in g.things and D.TILES[P.tile_named(g.things[ch][0])].walk):
                g.set(x, y, '+')
                return
            if ch not in ' ':
                break
