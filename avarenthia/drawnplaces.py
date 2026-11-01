"""Whole places (the editor's round C, approved 31 October 2026): maps drawn whole, one of a kind, set into the world.

A whole place is a PLACE block in a .des file (`places/*.des`, or Nilio's `my places.des`), with lines of its own
before its floors and a FLOOR block for each floor:

    PLACE:  Saint Odo's Rest
    SIZE:   60x34                       60 x 34, 80 x 50, 100 x 60 or 120 x 70
    SIGN:   ± #e8e0c8                   its sign on the world map and the sign's colour
    LOOK:   A chapel in ruins ...       what the look and the map say of it
    WORLD:  land=grass,forest road=near level=2 how=one found=map,rumour
    RUMOUR: They say ...                the tale the inns tell (found=rumour)
    BOOK:   ...                         the line in an old book on a library shelf (found=book)
    LAND:   fitted                      the land round it as the world has it (fitted), or as drawn (drawn)
    THING / LIST                        for every floor
    FLOOR:  ground                      ground, up 1, up 2 ..., down 1, down 2 ...
    MOOD / THING / EVENT / SWITCH / COUNTER / CREATURE / MORE / DRESS / SUBST    as in a piece
    PERSON: Brother Anselm at 12,8 says="The dead sleep badly here."
    ITEM:   longsword at 5,5            one fixed thing: a gear base, or tome
    MAP ... ENDMAP
    ENDPLACE

The ground floor lies on the land: rock (space) there is the land as it is; its + is the way in from the west edge.
Under it and over it every floor is a level of its own (Dungeon records with d.site, never on the world map); the
stairs < and > take you to the floor above or below, onto its twin stair. `?` cells are room slots: the game sets
one of the theme rooms there, anew in every world. Things, events, switches and puzzles work as in the drawn rooms
(themes.py, puzzles.py): each floor is room 0 of its map, and a slot's theme room the next.

`WORLD` words: land= the kinds of land (the biome names of the world map, or any); road= near, far or any;
level= how dangerous the country round it is (1-5); how= one (every world) or half (one world in two);
found= map (on the map from the start), rumour (the inns tell of it), book (a line on a library shelf).
"""
import random

from . import data as D
from . import pieces as P
from .worldgen import cheb

SIZES = ((60, 34), (80, 50), (100, 60), (120, 70))
FOUND = ('map', 'rumour', 'book')
ROADS = ('near', 'far', 'any')


class Place:
    def __init__(self, name):
        self.name, self.file = name, ''
        self.size = SIZES[0]
        self.sign, self.fg = '±', (232, 224, 200)
        self.look, self.rumour, self.book, self.land = '', '', '', 'fitted'
        self.world = {'land': ['any'], 'road': 'any', 'level': 1, 'how': 'one', 'found': ['map']}
        self.shared = []             # THING and LIST lines for every floor
        self.floors = []             # [Floor]

    def floor(self, name):
        return next((f for f in self.floors if f.name == name), None)

    def order(self):
        """The floors from the top down: up n ... up 1, ground, down 1 ... down n."""
        def key(f):
            if f.name == 'ground':
                return 0
            way, _, n = f.name.partition(' ')
            return (-1 if way == 'up' else 1) * int(n or 1)
        return sorted(self.floors, key=key)


class Floor:
    def __init__(self, name):
        self.name, self.lines, self.rows = name, [], []
        self.persons = []            # [(name, (x, y), says)]
        self.items = []              # [(what, (x, y))]
        self.piece = None

    @property
    def depth(self):
        """0 the ground, 1 the first floor down, -1 the first floor up."""
        if self.name == 'ground':
            return 0
        way, _, n = self.name.partition(' ')
        return (1 if way == 'down' else -1) * int(n or 1)


class Bad(ValueError):
    pass


def _at(text, where):
    """'Brother Anselm at 12,8 rest' -> ('Brother Anselm', (12, 8), 'rest')."""
    head, _, tail = text.partition(' at ')
    xy, _, rest = tail.strip().partition(' ')
    try:
        x, y = (int(v) for v in xy.split(','))
    except ValueError:
        raise Bad(f'{where}: write a place as "... at 12,8"')
    return head.strip(), (x, y), rest.strip()


def parse(text, file=''):
    """The whole places in one file's text."""
    out, cur, fl, in_map = [], None, None, False
    for n, line in enumerate(text.split('\n'), 1):
        where = f'{file}:{n}'
        line = line.rstrip('\r')
        st = line.strip()
        if cur is None:
            if st.upper().startswith('PLACE:'):
                cur = Place(st.split(':', 1)[1].strip())
                cur.file = file
            continue
        if in_map:
            if st == 'ENDMAP':
                in_map = False
            else:
                fl.rows.append(line.rstrip())
            continue
        if not st or st.startswith(';'):
            continue
        if st == 'ENDPLACE':
            for f in cur.floors:
                f.piece = _piece(cur, f, where)
            out.append(cur)
            cur, fl = None, None
            continue
        if st == 'MAP':
            if fl is None:
                raise Bad(f'{where}: MAP before FLOOR')
            in_map = True
            continue
        if ':' not in st:
            raise Bad(f'{where}: cannot read "{st}"')
        key, val = st.split(':', 1)
        key, val = key.strip().upper(), val.strip()
        if key == 'FLOOR':
            fl = Floor(val)
            cur.floors.append(fl)
        elif fl is None:
            _head(cur, key, val, st, where)
        elif key == 'PERSON':
            who, xy, rest = _at(val, where)
            says = rest.split('=', 1)[1].strip().strip('"') if rest.startswith('says=') else ''
            fl.persons.append((who, xy, says))
        elif key == 'ITEM':
            what, xy, _r = _at(val, where)
            fl.items.append((what, xy))
        else:
            fl.lines.append(st)
    if cur is not None:
        raise Bad(f'{file}: {cur.name}: no ENDPLACE')
    return out


def _head(pl, key, val, line, where):
    if key == 'SIZE':
        try:
            w, h = (int(v) for v in val.lower().split('x'))
        except ValueError:
            raise Bad(f'{where}: write a size as 60x34')
        pl.size = (w, h)
    elif key == 'SIGN':
        ch, _, col = val.partition(' ')
        pl.sign = ch or '±'
        if col.strip():
            pl.fg = D.hexrgb(col.strip())
    elif key == 'LOOK':
        pl.look = val
    elif key == 'RUMOUR':
        pl.rumour = val
    elif key == 'BOOK':
        pl.book = val
    elif key == 'LAND':
        pl.land = val if val in ('fitted', 'drawn') else 'fitted'
    elif key == 'WORLD':
        for word in val.split():
            k, _, v = word.partition('=')
            if k in ('land', 'found'):
                pl.world[k] = [x for x in v.split(',') if x]
            elif k == 'level':
                pl.world[k] = max(1, min(5, int(v or 1)))
            elif k in ('road', 'how'):
                pl.world[k] = v
            else:
                raise Bad(f'{where}: no such word in WORLD: {k}')
    elif key in ('THING', 'LIST'):
        pl.shared.append(line)
    else:
        raise Bad(f'{where}: no such line before the first FLOOR: {key}')


def _piece(pl, fl, where):
    """The floor as a piece (pieces.Piece), so the rooms' code reads its things, events and creatures."""
    text = '\n'.join([f'NAME: {pl.name}/{fl.name}'] + pl.shared + fl.lines + ['MAP'] + fl.rows + ['ENDMAP'])
    try:
        pc = P.parse(text, pl.file, checked=False)[0]
    except P.Bad as e:
        raise Bad(f'{where}: {pl.name}, {fl.name}: {str(e).split(": ", 1)[-1]}')
    pc.part = 'place'
    return pc


# ------------------------------------------------------------------ all of them
_ALL = None


def load(force=False):
    global _ALL
    if _ALL is not None and not force:
        return _ALL
    out = []
    for f, t in sorted(P.texts(force=force).items()):
        if 'PLACE:' in t:
            out += parse(t, f)
    for pl in out:
        for fl in pl.floors:
            P.EXTRA[fl.piece.name] = fl.piece
    _ALL = out
    return out


def by_name(name):
    return next((pl for pl in load() if pl.name == name), None)


def problems(pl):
    """What is wrong with a whole place, in plain words: [(message, floor name or None)]."""
    out = []
    if pl.size not in SIZES:
        out.append((f'a whole place is 60x34, 80x50, 100x60 or 120x70, not {pl.size[0]}x{pl.size[1]}', None))
    if not pl.floor('ground'):
        out.append(('a whole place needs a ground floor (FLOOR: ground)', None))
    names = [f.name for f in pl.floors]
    for f in pl.floors:
        if names.count(f.name) > 1:
            out.append((f'two floors are called {f.name}', f.name))
        w = max((len(r) for r in f.rows), default=0)
        if w > pl.size[0] or len(f.rows) > pl.size[1]:
            out.append((f'the floor {f.name} is bigger than the place', f.name))
    order = pl.order()
    for i, f in enumerate(order):
        ups = sum(r.count('<') for r in f.rows)
        downs = sum(r.count('>') for r in f.rows)
        above = order[i - 1] if i > 0 else None
        below = order[i + 1] if i + 1 < len(order) else None
        if ups and above is None:
            out.append((f'the floor {f.name} has stairs up, and no floor above it', f.name))
        if downs and below is None:
            out.append((f'the floor {f.name} has stairs down, and no floor below it', f.name))
        if below is not None and (not downs or not sum(r.count('<') for r in below.rows)):
            out.append((f'the stairs between {f.name} and {below.name} have no twin: draw > on the one and < on the '
                        'other', f.name))
    g = pl.floor('ground')
    if g is not None and not any('+' in r for r in g.rows):
        out.append(('the ground floor needs a + where the way in comes to it', 'ground'))
    for f in pl.floors:
        out += [(f'{f.name}: {msg}', f.name) for msg in _unreached(pl, f)]
        if any('?' in r for r in f.rows) and not _slot_pieces(_slots(f.rows)[0] if _slots(f.rows) else set()):
            out.append((f'{f.name}: no theme room fits in its room slot ?: make the slot bigger', f.name))
    if 'rumour' in pl.world['found'] and not pl.rumour:
        out.append(('it is found by a rumour: write the RUMOUR', None))
    if 'book' in pl.world['found'] and not pl.book:
        out.append(('it is found in a book: write the BOOK line', None))
    for f in pl.world['found']:
        if f not in FOUND:
            out.append((f'it cannot be found by "{f}": map, rumour or book', None))
    if pl.world['road'] not in ROADS:
        out.append(('road= is near, far or any', None))
    return out


def _walks(ch, pc):
    return ch in '<>+\'?' or P._walks(ch, pc)


def _unreached(pl, f):
    """Every stair and the way in reach each other on a floor (walking, over doors; things in the way count as rock)."""
    pc = f.piece
    if pc is None:
        return []
    cells = {(x, y) for y, row in enumerate(f.rows) for x, ch in enumerate(row)
             if ch not in ' #' and (_walks(ch, pc) or ch in pc.things and D.TILES[pc.things[ch][0]].walk)}
    if f.name == 'ground':
        cells |= {(x, y) for y, row in enumerate(f.rows) for x, ch in enumerate(row) if ch == ' '} if pl.land else set()
    ends = [(x, y) for y, row in enumerate(f.rows) for x, ch in enumerate(row) if ch in '<>+']
    if len(ends) < 2:
        return []
    seen, todo = {ends[0]}, [ends[0]]
    while todo:
        x, y = todo.pop()
        for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if n in cells and n not in seen:
                seen.add(n)
                todo.append(n)
    cut = [e for e in ends if e not in seen]
    return ['the way to its stairs is cut off (a stair or the way in cannot be reached)'] if cut else []


def _slots(rows):
    """The room slots of a drawing: [set of cells] for each patch of ?."""
    q = {(x, y) for y, row in enumerate(rows) for x, ch in enumerate(row) if ch == '?'}
    out = []
    while q:
        c = q.pop()
        part, todo = {c}, [c]
        while todo:
            x, y = todo.pop()
            for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if n in q:
                    q.discard(n)
                    part.add(n)
                    todo.append(n)
        out.append(part)
    return out


def _slot_pieces(cells):
    """The theme rooms that fit in a slot (by the size of the box round it)."""
    if not cells:
        return []
    w = max(c[0] for c in cells) - min(c[0] for c in cells) + 1
    h = max(c[1] for c in cells) - min(c[1] for c in cells) + 1
    out = []
    for pc in P.load():
        if pc.part != 'middle':
            continue
        pw = max((len(r) for r in pc.rows), default=0)
        ph = len(pc.rows)
        if max(pw, ph) <= min(w, h) or (pw <= w and ph <= h and pw <= h and ph <= w):
            out.append(pc)
    return out


# ------------------------------------------------------------------ in the world
def place(game, m, world, reach_set):
    """Set this world's whole places down, with dice of their own."""
    from .landmarks import Lay
    state = random.getstate()
    random.seed(game.seed * 7907 + 36)
    try:
        lay = Lay(game, m, world, reach_set)
        for pl in sorted(load(), key=lambda q: q.name):
            if pl.world['how'] == 'half' and random.random() < .5:
                continue
            xy = _spot(lay, world, pl)
            if xy is None:
                continue
            st = lay.add('drawn', xy, pl.name, hidden='map' not in pl.world['found'])
            st.place = pl.name
            setup(game, world, st, pl)
    finally:
        random.setstate(state)


def _spot(lay, world, pl):
    lands = [x for x in pl.world['land'] if x != 'any']
    road = pl.world['road']
    lvl = pl.world['level']

    def land_ok(x, y):
        return not lands or lay.bio(x, y) in lands or D.TILES[lay.m.tile(x, y)].name in lands

    def level_ok(x, y):
        return abs(world.danger_at(x, y) + 1 - lvl) <= 1

    def road_ok(x, y):
        return road != 'far' or lay.road(x, y) > 6
    cells = lay.by_road() if road == 'near' else None
    for pred in (lambda x, y: land_ok(x, y) and level_ok(x, y) and road_ok(x, y),
                 lambda x, y: land_ok(x, y) and road_ok(x, y), lambda x, y: road_ok(x, y), lambda x, y: True):
        xy = lay.search(pred, gap=5, cells=cells)
        if xy:
            return xy
    return None


def setup(game, world, site, pl):
    """The floors above and below: one Dungeon record for the place (never on the world map)."""
    from .world import Dungeon
    did = f'dp{site.id}'
    dg = Dungeon(did, pl.name, len(pl.floors), pl.world['level'] * 2 - 1, 'drawn', 'crypt', None, None, site.x, site.y,
                 False)
    dg.site, dg.drawn = site.id, True
    world.dungeons[did] = dg
    site.floors_did = did


def place_of(game, site):
    return by_name(getattr(site, 'place', ''))


def glyph(site):
    pl = by_name(getattr(site, 'place', ''))
    return (pl.sign, pl.fg) if pl else ('±', (232, 224, 200))


def describe(game, site):
    pl = place_of(game, site)
    return (pl.look if pl and pl.look else f'{site.name}.')


def key_of(site, fl):
    return site.map_key if fl.name == 'ground' else f'dp{site.id}:{fl.name}'


def below_key(game, m):
    """The key of the floor under this one of a whole place, or None."""
    sid, name = m.dp
    site = game.world.sites[sid]
    order = place_of(game, site).order()
    i = next(k for k, f in enumerate(order) if f.name == name)
    return key_of(site, order[i + 1]) if i + 1 < len(order) else None


# ------------------------------------------------------------------ the maps
def site_map(game, site):
    """The ground floor on its land, the way in from the west edge."""
    pl = place_of(game, site)
    return floor_map(game, site, pl, pl.floor('ground'))


def floor_map(game, site, pl, fl):
    from . import places as PL, themes as TH, puzzles as PZ
    from .entities import GameMap
    W, H = pl.size
    lvl = pl.world['level'] * 2 - 1 + max(0, fl.depth)
    state = random.getstate()
    random.seed(game.seed * 6151 + site.id * 97 + fl.depth * 13)
    try:
        if fl.name == 'ground':
            m = PL.land(game, site, W, H)
            if pl.land == 'drawn':
                for i in range(len(m.t)):
                    m.t[i] = m.ground
            m.kind = 'town'
            m.radius = 60
            fill = None
        else:
            m = GameMap(key_of(site, fl), 'dungeon', f'{pl.name}', W, H, D.WALL)
            m.lights, m.glows = [], []
            m.radius = 7 if fl.depth > 0 else 9
            m.site = site.id
            fill = D.WALL
        m.did, m.depth, m.level, m.dtag, m.last = f'dp{site.id}', pl.order().index(fl) + 1, lvl, 'crypt', False
        m.dp = (site.id, fl.name)
        m.drawn = True
        m.seal_id = f'dp{site.id}'
        m.wall_fg = None
        _lay(game, m, pl, fl, fill)
        TH.setup(game, m, lvl)
        PZ.setup(game, m, lvl)
        TH.creatures(game, m, lvl)
        _people(game, m, fl)
        _items(game, m, fl, lvl)
        if fl.name == 'ground':
            door = m.door_cell
            PL.finish(m, door)
        else:
            m.entry = next(((i % m.w, i // m.w) for i, t in enumerate(m.t) if t in (D.UP, D.DOWN)), (1, 1))
    finally:
        random.setstate(state)
    return m


def _lay(game, m, pl, fl, fill):
    """The drawing on the map: its tiles, the room slots' theme rooms, and the things and events (themes.lay)."""
    from . import themes as TH
    pc = fl.piece
    rows = list(fl.rows)
    cells = {}
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == ' ' or not m.inb(x, y):
                continue
            if ch in pc.subst:
                opts = pc.subst[ch]
                ch = random.choices([o[0] for o in opts], [o[1] for o in opts])[0]
                if ch == ' ':
                    continue
            cells[(x, y)] = ch
    door = next((c for c, ch in cells.items() if ch == '+'), None)
    if pc.dress and door:
        out = P.Drawing(cells)
        P.dress_drawing(pc, out, door)
        cells = dict(out)
    # the room slots: a theme room in each, anew in every world
    slot_of = {}
    pieces = {0: pc}
    for i, part in enumerate(_slots(rows), 1):
        fits = _slot_pieces(part)
        if not fits:
            continue
        x0, y0 = min(c[0] for c in part), min(c[1] for c in part)
        bw = max(c[0] for c in part) - x0 + 1
        bh = max(c[1] for c in part) - y0 + 1
        for _try in range(12):
            sp = random.choices(fits, [q.weight for q in fits])[0]
            drawing, gate, _step = P.drawn(sp)
            dw = max(c[0] for c in drawing) + 1
            dh = max(c[1] for c in drawing) + 1
            if dw <= bw and dh <= bh:
                break
        else:
            for c in part:
                cells[c] = '.'
            continue
        ox, oy = x0 + (bw - dw) // 2, y0 + (bh - dh) // 2
        for c in part:
            cells[c] = '#'                              # the slot round the room is its wall
        for (dx, dy), ch in drawing.items():
            c = (ox + dx, oy + dy)
            cells[c] = 'D+' if ch == '+' else ('#' if ch == '#' else ch)
            slot_of[c] = i
        for (gx, gy), ch in drawing.items():           # from each door a way out of the slot
            if ch != '+':
                continue
            step = next(((-dx, -dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                         if drawing.get((gx + dx, gy + dy), '#') not in '#+'), (0, 1))
            _carve(cells, part, slot_of, (ox + gx + step[0], oy + gy + step[1]))
        pieces[i] = sp
    ids = sorted(pieces)                          # a slot that took no room keeps its floor, in room 0
    renum = {old: new for new, old in enumerate(ids)}
    pieces = {renum[k]: v for k, v in pieces.items()}
    slot_of = {c: renum[r] for c, r in slot_of.items()}
    m.rooms = [['drawn', 'drawn' if r == 0 else 'theme', pieces[r].name] for r in range(len(pieces))]
    m.room_of = bytearray(b'\xff') * (m.w * m.h)
    marks, room_ids = {}, {}
    for (x, y), ch in cells.items():
        i = y * m.w + x
        rid = slot_of.get((x, y), 0)
        m.room_of[i] = rid
        if ch == 'D+':
            m.set(x, y, D.DOOR)
        elif ch == '#':
            m.set(x, y, D.WALL)
        elif ch == '+':
            m.set(x, y, D.DOOR if fl.name != 'ground' else D.PATH)
            m.door_cell = (x, y)
        elif ch == "'":
            m.set(x, y, D.DOOR)
        elif ch == '<':
            m.set(x, y, D.UP)
        elif ch == '>':
            m.set(x, y, D.DOWN)
        elif ch == '?':
            m.set(x, y, D.FLOOR)
        else:
            marks[(x, y)] = ch
            room_ids[(x, y)] = rid
            if ch not in pieces[rid].things and ch not in P.LEGEND and P.dressed_tile(ch) is None:
                m.set(x, y, D.FLOOR)            # a mark for an event on plain floor
    if not getattr(m, 'door_cell', None):
        m.door_cell = (1, m.h // 2)

    class Plan:
        pass
    plan = Plan()
    plan.marks = marks
    plan.spots = {c: what for c, what in pc.spots.items() if m.inb(*c)}
    TH.lay(m, plan, room_ids, pieces)


def _carve(cells, part, inside, start):
    """The shortest way from a slot room's door through the slot's wall to the floor round the slot."""
    from collections import deque
    if start not in part or start in inside:
        return
    prev, q = {start: None}, deque([start])
    while q:
        c = q.popleft()
        for n in ((c[0] + 1, c[1]), (c[0] - 1, c[1]), (c[0], c[1] + 1), (c[0], c[1] - 1)):
            if n not in part and cells.get(n, ' ') not in (' ', '#'):
                while c is not None:
                    cells[c] = '.'
                    c = prev[c]
                return
            if n in part and n not in inside and n not in prev:
                prev[n] = c
                q.append(n)


def _people(game, m, fl):
    from .entities import make_npc
    for who, (x, y), says in fl.persons:
        if not m.inb(x, y) or not D.TILES[m.tile(x, y)].walk:
            continue
        o = make_npc(game, who, 'drawn', '#e0d0b0', x, y, True)
        o.says = says
        m.mons.append(o)


def _items(game, m, fl, lvl):
    from .entities import make_gear, make_tome
    for what, (x, y) in fl.items:
        if not m.inb(x, y):
            continue
        if what == 'tome':
            it = make_tome(game, lvl)
        elif what in D.BASES:
            it = make_gear(game, what, 'normal', lvl)
        else:
            continue
        it.x, it.y = x, y
        m.items.append(it)


# ------------------------------------------------------------------ being there
def on_enter(game, site, m):
    pc = P.by_name(m.rooms[0][2]) if getattr(m, 'rooms', None) else None
    if pc and pc.moods:
        game.msg(random.choice(pc.moods), 'info')


def talk(game, npc):
    game.msg(f'{npc.name}: "{npc.says}"' if getattr(npc, 'says', '') else f'{npc.name} nods to you.', 'info')


def stairs(game, t, d):
    """The stairs of a whole place: to the floor above or below, onto its twin stair. None when not one of ours."""
    m = game.map
    if not getattr(m, 'dp', None) or t not in (D.UP, D.DOWN):
        return None
    sid, name = m.dp
    site = game.world.sites[sid]
    pl = place_of(game, site)
    order = pl.order()
    i = next(k for k, f in enumerate(order) if f.name == name)
    if t == D.UP and d != 'down' and i > 0:
        go(game, site, pl, order[i - 1], D.DOWN)
        return 1
    if t == D.DOWN and d != 'up' and i + 1 < len(order):
        go(game, site, pl, order[i + 1], D.UP)
        return 1
    return None


def go(game, site, pl, fl, arrive):
    """Onto another floor of the place, on the stair you came up or down by."""
    p = game.player
    key = key_of(site, fl)
    if key not in game.maps:
        game.maps[key] = floor_map(game, site, pl, fl)
    game.cur = key
    m = game.map
    spot = None
    if arrive in m.t:
        i = m.t.index(arrive)
        spot = (i % m.w, i // m.w)
    p.x, p.y = spot or m.entry
    word = {0: 'the ground floor'}.get(fl.depth) or (f'the {_nth(-fl.depth)} floor up' if fl.depth < 0 else
                                                     f'the {_nth(fl.depth)} floor down')
    game.msg(f'{pl.name}: {word}.', 'info')
    seen = game.player.__dict__.setdefault('dp_floors', set())
    if key not in seen:
        seen.add(key)
        on_enter(game, site, m)
    game.compute_fov()
    game.request = ('save',)


def _nth(n):
    return ('first', 'second', 'third', 'fourth', 'fifth', 'sixth')[min(n, 6) - 1]


# ------------------------------------------------------------------ how you hear of it
def unknown(game, how):
    """The places of this world not yet found that can be found this way."""
    from .folk import unfound
    out = []
    for q in game.world.sites:
        if q.kind != 'drawn' or not unfound(q):
            continue
        pl = place_of(game, q)
        if pl and how in pl.world['found']:
            out.append((q, pl))
    return out


def rumour(game):
    """A tale of a whole place you have not found, near enough to walk to."""
    from .engine import dir_name
    from .folk import discover
    ox, oy = game.world_pos()
    cands = [(q, pl) for q, pl in unknown(game, 'rumour') if cheb(q.x, q.y, ox, oy) < 120]
    if not cands:
        return None
    q, pl = min(cands, key=lambda c: cheb(c[0].x, c[0].y, ox, oy))
    discover(game, q, None)
    return f'{pl.rumour} ({q.name}, to the {dir_name(q.x - ox, q.y - oy)}.)'


def book(game):
    """A line on a library shelf about a whole place not found yet."""
    from .folk import discover
    cands = unknown(game, 'book')
    if not cands:
        return None
    q, pl = random.choice(cands)
    discover(game, q, None)
    return pl.book
