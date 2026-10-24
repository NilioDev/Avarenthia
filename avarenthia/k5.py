"""K5: the maker of classic dungeons, the way of Brogue in our style (approved 22 October 2026; mockups
`dungeons/mockups/K5_ways_seed*.png`). Rooms of many shapes grow onto the level one at a time, each slid along until
its door meets a wall of what is already dug, mostly close to the middle so the level stays compact. Main ways are
3 wide and join rooms (also as L and T pieces); narrow ways are 1 wide and short, to a side room or straight through
the rock as a short cut. Every passage runs from room to room; an arm no room joined is filled in again. Loops only
where walking round is long, lakes only where all floor stays reachable. After making, a check: doors only in a
straight wall, never two walls side by side.

make(w, h) returns a Plan: what each cell is, the doors, the rooms (with the ones behind a single entrance kept for
theme rooms) and where the stairs go. It knows nothing of tiles; worldgen.gen_k5 turns it into a GameMap."""
import math
import random
from collections import deque

D4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
DIRS8 = ((1, 0), (0, 1), (1, 1), (1, -1))
SHAPES = ['plain', 'chamfer', 'round', 'ell', 'tee', 'cross', 'overlap', 'chunky', 'pillars', 'rotunda',
          'inner', 'gallery', 'zed', 'bays', 'cave', 'ell', 'chamfer', 'cross']
BIG = {'pillars', 'rotunda', 'inner', 'gallery', 'cross', 'tee'}
MOODS = {
    'mixed': {'corridor': .15, 'hallway': .5, 'narrow': .35, 'caves': .5, 'near': .7},
    'halls and corridors': {'corridor': .2, 'hallway': .6, 'narrow': .2, 'caves': .2, 'near': .4},
    'close-packed': {'corridor': .08, 'hallway': .4, 'narrow': .5, 'caves': .4, 'near': .9},
}
SIZES = {'small': (80, 50), 'middle': (100, 60), 'large': (120, 70), 'very large': (150, 90)}


class Room:
    """One room of a level: its cells, its kind (room, cave, hall for a passage piece) and its shape."""
    __slots__ = ('id', 'cells', 'kind', 'shape', 'theme')

    def __init__(self, rid, cells, kind, shape):
        self.id, self.cells, self.kind, self.shape, self.theme = rid, cells, kind, shape, None

    def bbox(self):
        xs, ys = [c[0] for c in self.cells], [c[1] for c in self.cells]
        return min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1

    def middle(self, floor):
        """A floor cell near the middle of the room (for stairs and a room's one telling thing)."""
        bx, by, bw, bh = self.bbox()
        ok = [c for c in self.cells if floor.get(c) in ('room', 'cave') and floor.get((c[0] + 1, c[1])) in ('room', 'cave')]
        ok = ok or [c for c in self.cells if floor.get(c) in ('room', 'cave')] or list(self.cells)
        return min(ok, key=lambda c: (c[0] - bx - bw / 2) ** 2 + (c[1] - by - bh / 2) ** 2)


class Plan:
    """What K5 made: floor {cell: kind} (room, cave, hall, water, shallow, rubble), doors (doorways that get a door),
    arches (open doorways), rooms, up and down, the mood, and the faults the check found (0 when all is well)."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.floor, self.doors, self.arches, self.rooms = {}, set(), set(), []
        self.up = self.down = None
        self.mood = None
        self.bad_doors = self.double = 0
        self.themes = []            # rooms behind a single entrance, kept for theme rooms
        self.marks = {}             # what the drawn pieces put in their rooms: {cell: glyph}
        self.bottom = None          # the room of the bottom piece, when there is one


def rect(x, y, w, h):
    return {(xx, yy) for xx in range(x, x + w) for yy in range(y, y + h)}


def _room_cells(w, h, shape):
    out = set()
    cx, cy = (w - 1) / 2, (h - 1) / 2
    cut = random.randint(1, 3)
    for yy in range(h):
        for xx in range(w):
            dx, dy = min(xx, w - 1 - xx), min(yy, h - 1 - yy)
            if shape == 'chamfer' and dx + dy < cut:
                continue
            if shape == 'round' and ((xx - cx) / (w / 2)) ** 2 + ((yy - cy) / (h / 2)) ** 2 > 1.0:
                continue
            out.add((xx, yy))
    return out


def shape_cells(shape):
    """The floor of one room, before it is turned; and the kind it counts as."""
    R = random.randint
    if shape == 'plain':
        return rect(0, 0, R(11, 18), R(8, 12)), 'room'
    if shape == 'chamfer':
        return _room_cells(R(12, 20), R(8, 13), 'chamfer'), 'room'
    if shape == 'round':
        return _room_cells(R(13, 19), R(10, 14), 'round'), 'room'
    if shape == 'bays':                                      # alcoves, with thick stone between them
        w, h = R(13, 21), R(7, 10)
        cells = rect(1, 1, w, h)
        for xx in range(3, w - 1, 4):
            cells |= {(xx, 0), (xx + 1, 0), (xx, h + 1), (xx + 1, h + 1)}
        return cells, 'room'
    if shape == 'ell':
        a, b, t1, t2 = R(16, 24), R(14, 20), R(6, 9), R(6, 9)
        return rect(0, 0, a, t1) | rect(0, 0, t2, b), 'room'
    if shape == 'tee':
        a, t, s, ln = R(18, 26), R(6, 8), R(7, 9), R(8, 12)
        return rect(0, 0, a, t) | rect(a // 2 - s // 2, t, s, ln), 'room'
    if shape == 'cross':                                     # two rectangles through one middle
        a, b, c, d = R(16, 24), R(6, 8), R(7, 10), R(12, 17)
        return rect(0, (d - b) // 2, a, b) | rect((a - c) // 2, 0, c, d), 'room'
    if shape == 'overlap':                                   # two rooms laid over each other
        w1, h1, w2, h2 = R(10, 16), R(7, 10), R(10, 16), R(7, 10)
        return rect(0, 0, w1, h1) | rect(R(4, 9), R(3, 6), w2, h2), 'room'
    if shape == 'zed':
        w1, h1, w2, h2 = R(10, 14), R(7, 9), R(10, 14), R(7, 9)
        return rect(0, 0, w1, h1) | rect(w1 - R(4, 6), h1 - R(2, 3), w2, h2), 'room'
    if shape == 'chunky':                                    # a handful of circles run together
        cells = set()
        cx = cy = 0
        for _ in range(R(3, 5)):
            r = R(3, 5)
            for x in range(cx - r * 2, cx + r * 2 + 1):
                for y in range(cy - r, cy + r + 1):
                    if ((x - cx) / (r * 1.6)) ** 2 + ((y - cy) / r) ** 2 <= 1:
                        cells.add((x, y))
            cx += R(-6, 7)
            cy += R(-3, 4)
        return cells, 'room'
    if shape == 'pillars':                                   # a great hall: rows of pillars to fight between
        w, h = R(20, 28), R(12, 16)
        cells = _room_cells(w, h, 'chamfer')
        step = random.choice((4, 5))
        for px in range(3, w - 3, step):
            for py in ((3, h - 4) if random.random() < .5 else range(3, h - 3, 4)):
                cells.discard((px, py))
        return cells, 'room'
    if shape == 'rotunda':                                   # a round hall round a solid core
        w, h = R(17, 23), R(13, 17)
        cw, ch = R(3, 5), R(3, 4)
        return _room_cells(w, h, 'round') - rect((w - cw) // 2, (h - ch) // 2, cw, ch), 'room'
    if shape == 'inner':                                     # a room with a room in it, one way in
        w, h = R(17, 23), R(12, 15)
        ring = rect(4, 3, w - 8, h - 6) - rect(5, 4, w - 10, h - 8)
        gap = random.choice([(w // 2, 3), (w // 2, h - 4), (4, h // 2), (w - 5, h // 2)])
        return rect(0, 0, w, h) - (ring - {gap}), 'room'
    if shape == 'gallery':                                   # a long hall with a row of pillars down the middle
        w = R(22, 30)
        return rect(0, 0, w, 7) - {(px, 3) for px in range(3, w - 3, 4)}, 'room'
    if shape == 'cave':
        w, h = R(16, 26), R(10, 16)
        return {(x, y) for y in range(h) for x in range(w)
                if math.hypot((x - w / 2) / (w / 2), (y - h / 2) / (h / 2)) < 1 + random.uniform(-.25, .1)}, 'cave'
    raise ValueError(shape)


def turn(cells):
    """Turn and mirror a shape at random, then put it back at the origin."""
    k, flip = random.randint(0, 3), random.random() < .5
    out = set()
    for x, y in cells:
        if flip:
            x = -x
        for _ in range(k):
            x, y = -y, x
        out.add((x, y))
    mx, my = min(c[0] for c in out), min(c[1] for c in out)
    return {(x - mx, y - my) for x, y in out}


def door_sites(cells):
    """For each side, where a door can go: in a straight bit of wall, two cells of wall each side."""
    sites = {}
    for d in D4:
        p = (d[1], d[0])
        good = [(x + d[0], y + d[1]) for x, y in cells if (x + d[0], y + d[1]) not in cells and all(
            (x + k * p[0], y + k * p[1]) in cells and (x + k * p[0] + d[0], y + k * p[1] + d[1]) not in cells
            for k in (-2, -1, 1, 2))]
        if good:
            sites[d] = good
    return sites


def hallway(start, d, lengths, width=3):
    """A hallway from start going d, 3 wide (a main way) or 1 (a narrow way), bent when two lengths are given."""
    cells = set()
    half = width // 2
    span = range(-half, half + 1)
    x, y = start
    for i, n in enumerate(lengths):
        for _ in range(n):
            for o in span:
                cells.add((x + (o if d[1] else 0), y + (o if d[0] else 0)))
            x, y = x + d[0], y + d[1]
        if i + 1 < len(lengths):
            for a in span:
                for b in span:
                    cells.add((x - d[0] + a, y - d[1] + b))
            nd = random.choice([(d[1], d[0]), (-d[1], -d[0])])
            x, y = x - d[0] + nd[0] * (half + 1), y - d[1] + nd[1] * (half + 1)
            d = nd
    return cells, (x, y), d


class _Level:
    """The level while it grows: who owns each cell, what it is, and the narrow ways (where a narrow way meets a
    wall, the corner it makes is not a double wall)."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.owner, self.floor = {}, {}
        self.narrow = set()
        self.edge = set()           # rock cells beside floor: where the next piece may join
        self.near = bytearray(w * h)    # 1 where a cell is dug or touches one that is

    def dig(self, c, kind, who):
        self.floor[c] = kind
        self.owner[c] = who
        w, near = self.w, self.near
        for a in (-1, 0, 1):
            for b in (-1, 0, 1):
                x, y = c[0] + a, c[1] + b
                if 0 <= x < w and 0 <= y < self.h:
                    near[y * w + x] = 1
        self.edge.discard(c)
        for d in D4:
            n = (c[0] + d[0], c[1] + d[1])
            if n not in self.floor and 2 <= n[0] < self.w - 2 and 2 <= n[1] < self.h - 2:
                self.edge.add(n)

    def undig(self, c):
        del self.owner[c], self.floor[c]
        if any((c[0] + d[0], c[1] + d[1]) in self.floor for d in D4):
            self.edge.add(c)
        for d in D4:
            n = (c[0] + d[0], c[1] + d[1])
            if n in self.edge and not any((n[0] + e[0], n[1] + e[1]) in self.floor for e in D4):
                self.edge.discard(n)

    def doubles(self, area, extra=None, gone=(), narrow=()):
        """Rock with floor on one side and floor again two cells on: two walls side by side. Straight it is always a
        fault; diagonal only between two different pieces (inside one room it is the inner corner of an L)."""
        own = self.owner
        extra = extra or {}

        def who(c):
            if c in extra:
                return extra[c]
            if c in gone:
                return None
            return own.get(c)
        nar = self.narrow | set(narrow)
        out = []
        for x, y in area:
            if who((x, y)) is not None:
                continue
            for d in DIRS8:
                for sgn in (1, -1):
                    a = (x + sgn * d[0], y + sgn * d[1])
                    wa = who(a)
                    if wa is None:
                        continue
                    b = (x - sgn * d[0], y - sgn * d[1])
                    if who(b) is not None:
                        continue
                    c = (x - 2 * sgn * d[0], y - 2 * sgn * d[1])
                    wc = who(c)
                    if wc is not None and (0 in d or (wa != wc and a not in nar and c not in nar)):
                        out.append((x, y))
        return out

    def free(self, rel, ox, oy):
        """Whether a piece at (ox, oy) stays inside the level and off everything dug (with a wall between)."""
        w, h, near = self.w, self.h, self.near
        x0, y0, x1, y1 = 2 - ox, 2 - oy, w - 3 - ox, h - 3 - oy
        for x, y in rel:
            if not (x0 <= x <= x1 and y0 <= y <= y1) or near[(y + oy) * w + x + ox]:
                return False
        return True

    def fits(self, placed, door, me, narrow=()):
        """No double wall made by the new piece: floor, two cells of rock, floor again. The level had none, so any
        new one has a cell of the piece at one end: look three cells out from each, in the eight directions."""
        own = self.owner
        new = set(placed)
        new.add(door)
        nar = self.narrow | set(narrow) | ({door} if narrow else set())
        for a in new:
            for d in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                b = (a[0] + d[0], a[1] + d[1])
                if b in new or b in own:
                    continue
                c = (b[0] + d[0], b[1] + d[1])
                if c in new or c in own:
                    continue
                e = (c[0] + d[0], c[1] + d[1])
                if e in new:
                    if 0 in d:
                        return False        # a straight double wall inside the new piece is a fault too
                    continue
                we = own.get(e)
                if we is not None and (0 in d or (a not in nar and e not in nar)):
                    return False
        return True


def straight_door(floor, c):
    """A door only in a straight wall: floor on two opposite sides, wall on the other two, and the wall runs on."""
    x, y = c
    for d, p in (((1, 0), (0, 1)), ((0, 1), (1, 0))):
        if (x + d[0], y + d[1]) in floor and (x - d[0], y - d[1]) in floor:
            if all((x + k * p[0], y + k * p[1]) not in floor for k in (-2, -1, 1, 2)):
                return True
    return False


def _straight_after(floor, placed, door):
    class Over(dict):
        def __contains__(self, c):
            return c in placed or c == door or dict.__contains__(self, c)
    return straight_door(Over(floor), door)


def walk(floor, start, block=(), limit=None):
    dist = {start: 0}
    q = deque([start])
    while q:
        c = q.popleft()
        dc = dist[c] + 1
        if limit and dc > limit:
            continue
        for d in D4:
            n = (c[0] + d[0], c[1] + d[1])
            if n in floor and n not in dist and n not in block:
                dist[n] = dc
                q.append(n)
    return dist


def _design(deck, mood):
    """One piece: a room (maybe with a hallway on it), or a corridor piece of its own.
    Returns (cells, hall, sites, kind, shape, arms, narrow) or None."""
    if random.random() < mood['corridor']:                  # a corridor piece of its own: a bend or a junction
        cells = rect(-1, -1, 3, 3)
        sites, arms = {}, []
        for d in random.sample(D4, random.choice((2, 2, 3, 3, 4))):
            c, end, _ = hallway((d[0] * 2, d[1] * 2), d, [random.randint(4, 10)])
            cells |= c
            sites[d] = [end]
            arms.append((c, end))
        return cells, set(), sites, 'hall', 'corridor', arms, set()
    if not deck:
        deck.extend(SHAPES)
        random.shuffle(deck)
    shape = deck.pop()
    if shape == 'cave' and random.random() > mood['caves']:
        shape = deck.pop() if deck else 'plain'
    cells, kind = shape_cells(shape)
    cells = turn(cells)
    sites = door_sites(cells)
    if not sites:
        return None
    hall, narrow = set(), set()
    if kind == 'cave' or random.random() < mood['hallway']:    # a hallway on the room, now and then bent
        d = random.choice(list(sites))
        s = random.choice(sites[d])
        if shape not in BIG and random.random() < mood['narrow']:
            hall, end, d2 = hallway(s, d, [random.randint(3, 6)] + ([random.randint(2, 4)] if random.random() < .4 else []), 1)
            narrow = hall
        else:
            hall, end, d2 = hallway(s, d, [random.randint(5, 12)] + ([random.randint(5, 10)] if random.random() < .45 else []))
        sites = {d2: [end]}
    return cells, hall, sites, kind, shape, [], narrow


def _drawn_piece(dr):
    """A drawn piece (pieces.drawn) as K5 grows it: its floor cells and its one way in."""
    cells, gate, step = dr
    floor = {c for c, ch in cells.items() if ch not in '#+'}
    return floor, {step: [gate]}


def make(w, h, mood=None, rooms_wanted=None, themes=(), arrival=None, bottom=None):
    """Grow one level. Returns a Plan. themes: drawn pieces (pieces.drawn) set in as theme rooms behind a single
    entrance; arrival: one for the first room (where the stairs up go); bottom: one for the far room."""
    mood_name = mood or random.choice(list(MOODS))
    mood = MOODS[mood_name]
    lv = _Level(w, h)
    plan = Plan(w, h)
    plan.mood = mood_name
    want = rooms_wanted or max(8, round(20 * w * h / (120 * 70)))
    deck, doors, open_ends, arms_of = [], set(), set(), []
    rooms = plan.rooms
    first = None
    marks = plan.marks
    sealed = set()                          # theme rooms: nothing else may join them
    pending = [(t, 'theme') for t in themes] + ([(bottom, 'bottom')] if bottom else [])
    random.shuffle(pending)
    for _ in range(50):
        if arrival:
            fl, _sites = _drawn_piece(arrival[1])
            first = (fl, set(), _sites, 'room', 'theme', [], set())
        else:
            first = _design(deck, {**mood, 'corridor': 0, 'hallway': 0})
        if first:
            cells = first[0]
            if max(c[0] for c in cells) < w - 8 and max(c[1] for c in cells) < h - 8:
                break
    cells, _h, _s, kind, shape, _a, _n = first
    bw, bh = max(c[0] for c in cells) + 1, max(c[1] for c in cells) + 1
    ox, oy = max(3, (w - bw) // 2), max(3, (h - bh) // 2)
    placed = {(x + ox, y + oy) for x, y in cells}
    for c in placed:
        lv.dig(c, kind, 0)
    rooms.append(Room(0, placed, kind, shape))
    if arrival:
        rooms[0].theme = arrival[0].name
        rooms[0].shape = 'theme'
        for (x, y), ch in arrival[1][0].items():
            if ch not in '#+.':
                marks[(x + ox, y + oy)] = ch
    misses = 0
    piece_of = {}
    for _attempt in range(700):
        if (sum(1 for r in rooms if r.kind != 'hall') >= want and not pending) or misses > 120:
            break                           # full, or nothing fits any more
        theme = None
        if pending and len(rooms) >= 3 and (random.random() < .6 or sum(1 for r in rooms if r.kind != 'hall') >= want):
            theme = pending[-1]
            fl, sites_ = _drawn_piece(theme[0][1])
            (d, (s_,)), = sites_.items()
            hall = set()
            if random.random() < .75:                  # mostly a narrow way of its own leads to it: one way in
                hall, end, d2 = hallway(s_, d, [random.randint(3, 7)], 1)
                sites_ = {d2: [end]}
            piece = (fl, hall, sites_, 'room', 'theme', [], hall)
        else:
            piece = _design(deck, mood)
        if not piece:
            continue
        cells, hall, sites, kind, shape, arms, narrow = piece
        both = cells | hall
        me = len(rooms)
        found = []
        floor = lv.floor
        for wx, wy in random.sample(tuple(lv.edge), min(len(lv.edge), 500)):
            near = [d for d in D4 if (wx - d[0], wy - d[1]) in floor]
            if len(near) != 1:
                continue
            d = near[0]
            back = (-d[0], -d[1])
            if back not in sites:
                continue
            onto = (wx - d[0], wy - d[1])
            if onto in doors or lv.owner.get(onto) in sealed:
                continue
            if floor[onto] == 'hall' and ((wx, wy) not in open_ends or kind == 'hall' or hall):
                continue                    # onto a passage only at the open end of an arm, and only a room
            sx, sy = random.choice(sites[back])
            ox, oy = wx - sx, wy - sy
            if not lv.free(both, ox, oy):
                continue
            placed = {(x + ox, y + oy) for x, y in both}
            nar = {(x + ox, y + oy) for x, y in narrow} if kind != 'hall' else ()
            if lv.fits(placed, (wx, wy), me, nar) and _straight_after(floor, placed, (wx, wy)):
                found.append((ox, oy, wx, wy))
                if len(found) >= 8:
                    break
        if not found:
            misses += 1
            if theme and misses > 25:
                pending.pop()               # this one will not fit anywhere
                misses = 0
            continue
        misses = 0
        if random.random() < mood['near']:  # mostly compact, sometimes anywhere, so the level also reaches out
            fl = lv.floor
            mx, my = sum(c[0] for c in fl) / len(fl), sum(c[1] for c in fl) / len(fl)
            ccx, ccy = sum(c[0] for c in both) / len(both), sum(c[1] for c in both) / len(both)
            ox, oy, wx, wy = min(found, key=lambda f: (f[0] + ccx - mx) ** 2 + ((f[1] + ccy - my) * 1.6) ** 2)
        else:
            ox, oy, wx, wy = random.choice(found)
        rc = {(x + ox, y + oy) for x, y in cells}
        for c in rc:
            lv.dig(c, kind, me)
        for x, y in hall:
            lv.dig((x + ox, y + oy), 'hall', me)
        lv.dig((wx, wy), 'hall', me)
        if kind != 'hall' and narrow:
            lv.narrow |= {(x + ox, y + oy) for x, y in narrow} | {(wx, wy)}
        doors.add((wx, wy))
        rooms.append(Room(me, rc, kind, shape))
        if theme:
            pending.pop()
            sealed.add(me)
            rooms[-1].theme = theme[0][0].name
            piece_of[me] = theme[1]
            for (x, y), ch in theme[0][1][0].items():
                if ch not in '#+.':
                    marks[(x + ox, y + oy)] = ch
        open_ends.discard((wx, wy))
        if kind == 'hall':
            arms_of.append((me, [{(x + ox, y + oy) for x, y in a} for a, _e in arms]))
            for _a, e in arms:
                if (e[0] + ox, e[1] + oy) != (wx, wy):
                    open_ends.add((e[0] + ox, e[1] + oy))
    _prune(lv, arms_of, doors, rooms)
    keep = {c for c, o in lv.owner.items() if o in sealed or (arrival and o == 0)}
    _loops(lv, doors, keep)
    _shortcuts(lv, doors, keep)
    _lakes(lv, doors, keep)
    floor = lv.floor
    pool = [c for c, k in floor.items() if k in ('hall', 'room') and c not in doors and c not in keep]
    for c in random.sample(pool, min(len(pool) // 60 + 6, len(pool))):
        floor[c] = 'rubble'
    bad = [d for d in doors if not straight_door(floor, d)]
    doors.difference_update(bad)
    plan.bad_doors = len(bad)
    plan.double = len(lv.doubles([(x, y) for x in range(2, w - 2) for y in range(2, h - 2)]))
    plan.floor = floor
    for d in doors:
        (plan.doors if random.random() < .6 else plan.arches).add(d)
    real = [r for r in rooms if r.kind != 'hall' and r.cells & set(floor)]
    for r in rooms:
        r.cells = {c for c in r.cells if c in floor}
    up_room = real[0]
    plan.up = next((c for c, ch in marks.items() if ch == '<' and c in up_room.cells), None) or up_room.middle(floor)
    dist = walk(floor, plan.up)
    low = [r for r in real if piece_of.get(r.id) == 'bottom']
    far = low[0] if low else max([r for r in real[1:] if r.id not in sealed] or real,
                                 key=lambda r: max(dist.get(c, 0) for c in r.cells))
    plan.down = next((c for c, ch in marks.items() if ch == '>' and c in far.cells), None) or far.middle(floor)
    plan.bottom = far if low else None

    def entries(cs):
        ring = {(c[0] + d[0], c[1] + d[1]) for c in cs for d in D4} - cs
        return sum(1 for c in ring if c in floor)
    single = [r for r in real if r is not up_room and r is not far and r.kind == 'room' and entries(r.cells) <= 3
              and r.id not in sealed]
    plan.themes = sorted(single, key=lambda r: -len(r.cells))
    _centre(plan)
    return plan


def _centre(plan):
    """Slide the whole level to the middle of the map: rooms grow from the middle but not always evenly."""
    xs, ys = [c[0] for c in plan.floor], [c[1] for c in plan.floor]
    dx = (plan.w - max(xs) - 1 - min(xs)) // 2
    dy = (plan.h - max(ys) - 1 - min(ys)) // 2
    if not dx and not dy:
        return
    mv = lambda c: (c[0] + dx, c[1] + dy)  # noqa: E731
    plan.floor = {mv(c): k for c, k in plan.floor.items()}
    plan.doors, plan.arches = {mv(c) for c in plan.doors}, {mv(c) for c in plan.arches}
    for r in plan.rooms:
        r.cells = {mv(c) for c in r.cells}
    plan.up, plan.down = mv(plan.up), mv(plan.down)
    plan.marks = {mv(c): ch for c, ch in plan.marks.items()}


def _prune(lv, arms_of, doors, rooms):
    """An arm of a corridor piece that nothing joined is filled in again; a piece that reaches one room goes whole."""
    def fill(gone):
        area = {(x + i, y + j) for x, y in gone for i in range(-3, 4) for j in range(-3, 4)}
        if lv.doubles(area, gone=gone):
            return False
        for c in gone:
            lv.undig(c)
            doors.discard(c)
        return True
    for me, parts in arms_of:
        own = lv.owner
        used = [arm for arm in parts if any(own.get((x + d[0], y + d[1]), me) != me or (x + d[0], y + d[1]) in doors
                                            for x, y in arm for d in D4)]
        if len(used) <= 1:
            fill({c for c, o in own.items() if o == me})
            continue
        for arm in parts:
            if arm not in used:
                fill({c for c in arm if own.get(c) == me})


def _loops(lv, doors, keep=()):
    """Loops, only where walking round would take more than 30 steps."""
    floor, w, h = lv.floor, lv.w, lv.h
    cand = list(lv.edge)
    random.shuffle(cand)
    loops = 0
    for x, y in cand:
        if loops >= 8:
            break
        for d in ((1, 0), (0, 1)):
            a, b = (x + d[0], y + d[1]), (x - d[0], y - d[1])
            if a in floor and b in floor and 'hall' not in (floor[a], floor[b]) and (x, y) not in floor \
                    and a not in keep and b not in keep:
                trial = dict(floor)
                trial[(x, y)] = 'hall'
                if not straight_door(trial, (x, y)) or walk(floor, a, limit=31).get(b, 999) <= 30:
                    continue
                area = [(x + i, y + j) for i in range(-3, 4) for j in range(-3, 4)]
                if lv.doubles(area, {(x, y): -1 - loops}):
                    continue
                lv.dig((x, y), 'hall', -1 - loops)
                doors.add((x, y))
                loops += 1
                break


def _shortcuts(lv, doors, keep=()):
    """Narrow ways as short cuts: one wide, straight through the rock from room to room, where walking round is long."""
    floor, owner = lv.floor, lv.owner
    cand = list(lv.edge)
    random.shuffle(cand)
    tunnels = 0
    for x, y in cand:
        if tunnels >= 4:
            break
        nb = [d for d in D4 if floor.get((x - d[0], y - d[1])) in ('room', 'cave')]
        if len(nb) != 1 or sum((x + d[0], y + d[1]) in floor for d in D4) != 1:
            continue
        d = nb[0]
        src = (x - d[0], y - d[1])
        way = []
        c = None
        for k in range(10):
            c = (x + d[0] * k, y + d[1] * k)
            if c in floor:
                break
            way.append(c)
        else:
            continue
        if len(way) < 3 or floor.get(c) not in ('room', 'cave') or owner.get(c) == owner.get(src) or c in keep \
                or src in keep:
            continue
        p = (d[1], d[0])
        if any((v[0] + p[0], v[1] + p[1]) in floor or (v[0] - p[0], v[1] - p[1]) in floor for v in way):
            continue
        tf = dict(floor)
        tf.update(dict.fromkeys(way, 'hall'))
        if not (straight_door(tf, way[0]) and straight_door(tf, way[-1])) or walk(floor, src, limit=31).get(c, 999) <= 30:
            continue
        area = {(v[0] + i, v[1] + j) for v in way for i in range(-3, 4) for j in range(-3, 4)}
        if lv.doubles(area, dict.fromkeys(way, -100 - tunnels), narrow=way):
            continue
        lv.narrow |= set(way)
        for v in way:
            lv.dig(v, 'hall', -100 - tunnels)
        doors.add(random.choice((way[0], way[-1])))
        tunnels += 1


def _lakes(lv, doors, keep=()):
    """Lakes, only where all the floor stays reachable, with shallow water round the deep."""
    floor, w, h = lv.floor, lv.w, lv.h
    for size in (16, 12, 9, 7):
        for _ in range(10):
            cx, cy = random.randint(8, w - 9), random.randint(6, h - 7)
            rx, ry = size / 2, size / 3.2
            blob = {(x, y) for x in range(int(cx - rx - 1), int(cx + rx + 2)) for y in range(int(cy - ry - 1), int(cy + ry + 2))
                    if math.hypot((x - cx) / rx, (y - cy) / ry) < 1 + random.uniform(-.2, .1)}
            wet = {c for c in blob if c in floor and c not in doors and c not in keep}
            if len(wet) < 12:
                continue
            deep = {c for c in wet if all((c[0] + d[0], c[1] + d[1]) in blob for d in D4)
                    and all((c[0] + a, c[1] + b) in floor for a in (-1, 0, 1) for b in (-1, 0, 1))}
            rest = [c for c in floor if c not in deep]
            if not rest or len(walk(floor, rest[0], deep)) != len(rest):
                continue
            for c in wet:
                floor[c] = 'water' if c in deep else 'shallow'
            break
