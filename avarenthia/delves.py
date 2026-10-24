"""The underground kinds, each its own plan (round 7; `dungeons/ondergronds.md`, approved 22 October 2026).

Whoever made a place decides its shape. Water grinds long passages and big halls along a stream; beasts dig round
dens; ants hang chambers like grapes on their tunnels; spiders fill halls with web; kobolds and goblins dig narrow
ways braced with props; people build crypts of niches. Rooms are named by their use (a cook den, a sleeping den,
the leader's nook, an egg chamber) and the folk stand where they belong: watchers by the way in, sleepers asleep in
the dens, the leader with the guard at the bottom. Fewer of them than in a classic level, each with a reason.

`plan_for(d, depth)` says whether a level gets one of these plans (the tag of its dungeon decides); `carve` lays it
out on the GameMap gen_dungeon made and returns where the stairs go; `folk` puts the inhabitants and the room things
in once the level is dressed. Classic dungeons, the mines and the sunken ruins keep the K5 maker."""
import math
import random
from collections import deque

from . import data as D
from .data import FLOOR, WALL, ROCK, DOOR, UP, DOWN, SHALLOW, WATER
from .entities import make_monster

D4 = ((1, 0), (-1, 0), (0, 1), (0, -1))

# role: what the room is for. Each kind: its maker's character and the rooms it has.
#   wide: the width of the ordinary ways, main: of the main way; wiggle: how much a way wanders (0 straight)
#   built: walls of cut stone (joined lines) instead of raw rock; small: one screen (80 x 50)
#   rooms: [(role, n, (rx_lo, rx_hi), (ry_lo, ry_hi))]; first: the room you arrive in; last: where the way down or
#   the leader is
KINDS = {
    'den': dict(maker='kobolds', wide=2, main=3, wiggle=.35, small=True, first='mouth', last='hoard',
                rooms=[('mouth', 1, (4, 5), (3, 4)), ('cook', 1, (5, 6), (4, 5)), ('sleep', 2, (4, 5), (3, 4)),
                       ('store', 1, (3, 4), (3, 3)), ('hoard', 1, (5, 6), (4, 5))]),
    'warren': dict(maker='goblins', wide=2, main=3, wiggle=.3, small=True, first='lookout', last='leader', props=True,
                   rooms=[('lookout', 1, (4, 5), (3, 4)), ('sleep', 1, (8, 10), (4, 5)), ('cook', 1, (7, 9), (4, 5)),
                          ('loot', 1, (5, 6), (3, 4)), ('leader', 1, (7, 8), (4, 5))]),
    'cave': dict(maker='water', wide=3, main=4, wiggle=.45, first='mouth', last='pool',
                 rooms=[('mouth', 1, (5, 7), (4, 5)), ('hall', 3, (10, 15), (6, 9)), ('crawl', 2, (4, 5), (3, 4)),
                        ('dens', 2, (5, 7), (4, 5)), ('pool', 1, (9, 12), (6, 8))], stream=True),
    'antnest': dict(maker='ants', wide=2, main=3, wiggle=.4, first='mouth', last='queen',
                    rooms=[('mouth', 1, (5, 6), (4, 4)), ('food', 3, (4, 6), (3, 4)), ('eggs', 3, (4, 5), (3, 4)),
                           ('workers', 2, (5, 7), (4, 5)), ('queen', 1, (9, 11), (6, 7))]),
    'spiderlair': dict(maker='spiders', wide=3, main=3, wiggle=.35, first='mouth', last='brood',
                       rooms=[('mouth', 1, (5, 6), (4, 4)), ('webs', 3, (8, 12), (5, 7)), ('larder', 2, (5, 6), (4, 5)),
                              ('eggs', 1, (5, 6), (4, 4)), ('brood', 1, (10, 12), (6, 8))]),
    'grotto': dict(maker='sea', wide=3, main=4, wiggle=.4, first='mouth', last='lake',
                   rooms=[('mouth', 1, (6, 7), (4, 5)), ('hall', 3, (9, 13), (6, 8)), ('wrecks', 1, (6, 8), (4, 5)),
                          ('ledge', 2, (5, 6), (3, 4)), ('lake', 1, (14, 17), (8, 10))]),
    'gloam': dict(maker='the dark', wide=3, main=4, wiggle=.25, first='mouth', last='eye',
                  rooms=[('mouth', 1, (5, 6), (4, 5)), ('glow', 3, (8, 11), (5, 7)), ('crystal', 2, (6, 8), (4, 6)),
                         ('still', 1, (7, 9), (5, 6)), ('eye', 1, (11, 13), (7, 8))]),
    'lair_dragon': dict(maker='the dragon', wide=4, main=5, wiggle=.25, first='mouth', last='hoard',
                        rooms=[('mouth', 1, (6, 7), (4, 5)), ('ramp', 2, (8, 10), (5, 6)), ('burnt', 2, (7, 9), (5, 6)),
                               ('hoard', 1, (18, 22), (11, 13))], sky=True),
    'lair_spider': dict(maker='spiders', wide=3, main=4, wiggle=.35, first='mouth', last='brood',
                        rooms=[('mouth', 1, (5, 6), (4, 4)), ('webs', 4, (9, 13), (5, 7)), ('larder', 2, (5, 7), (4, 5)),
                               ('eggs', 2, (5, 6), (4, 4)), ('brood', 1, (12, 14), (7, 8))]),
    'burrow': dict(maker='gnolls', wide=2, main=3, wiggle=.4, first='mouth', last='bonepit',
                   rooms=[('mouth', 1, (5, 6), (4, 4)), ('dens', 3, (5, 7), (4, 5)), ('feed', 1, (6, 8), (4, 5)),
                          ('pups', 1, (4, 5), (3, 4)), ('bonepit', 1, (9, 11), (6, 7))]),
    'swamp': dict(maker='water', wide=3, main=4, wiggle=.4, first='mouth', last='lake',
                  rooms=[('mouth', 1, (5, 6), (4, 4)), ('drowned', 3, (8, 11), (5, 7)), ('eggs', 1, (5, 6), (4, 4)),
                         ('ledge', 1, (5, 6), (3, 4)), ('lake', 1, (12, 14), (7, 8))], stream=True),
    'crypt': dict(maker='people', wide=3, main=3, wiggle=0, built=True, first='stair', last='tomb',
                  rooms=[('stair', 1, (4, 5), (3, 4)), ('niches', 4, (8, 11), (4, 5)), ('ossuary', 1, (6, 8), (4, 6)),
                         ('chapel', 1, (7, 8), (5, 6)), ('tomb', 1, (7, 9), (5, 6))]),
}
KIND_OF_TAG = {'lair_spider': 'lair_spider'}

MOODS = {
    'mouth': ['The way in. Daylight fades behind you.', 'The mouth of the place. The air turns cold and close.'],
    'stair': ['The foot of the stair. The air is still and dry.'],
    'lookout': ['A lookout by the way in. Someone sat here watching, not long ago.'],
    'cook': ['A cook den. A fire, a pot and a stink of burnt fat.', 'Where they cook. Bones are piled by the fire.'],
    'sleep': ['A sleeping den. Straw and rags, and the smell of whoever sleeps here.'],
    'store': ['A store hole: sacks, barrels and gnawed bones.'],
    'hoard': ['The heart of the place, and a glitter in the dark.'],
    'loot': ['A loot corner: what they took from the road, heaped any old how.'],
    'leader': ["The leader's nook. A seat of crates, and the best of the loot behind it."],
    'hall': ['A great hall, carved by water long gone. Your steps echo.', 'Water ground this hall out of the stone.'],
    'crawl': ['A low crawlway. The roof scrapes your back.'],
    'dens': ['A den, scraped round and smooth by something that sleeps here.'],
    'pool': ['A still pool fills the end of the cave. Drops fall and ring in it.'],
    'food': ['A food chamber, packed with what the ants carried home.'],
    'eggs': ['An egg chamber. Pale eggs lie in heaps, warm to the touch.'],
    'workers': ['A tunnel hall where the workers come and go.'],
    'queen': ['The queen\'s chamber, deep in the middle of the nest. Something huge stirs.'],
    'webs': ['A hall full of web. Threads catch at your face.', 'Web hangs in curtains from the roof.'],
    'larder': ['A larder of things spun in silk. Some of the bundles are the size of a man.'],
    'brood': ['The brood hall. The web here is thick as cloth, and it trembles.'],
    'wrecks': ['Timbers of a wreck the sea washed in. Barnacles on everything.'],
    'ledge': ['A ledge above the water. The rock is slick.'],
    'lake': ['A lake under the rock. The water breathes with the tide.'],
    'glow': ['Fungus glows on every wall. The light is wrong somehow.'],
    'crystal': ['Crystal grows from the rock, and your own face looks back from every one.'],
    'still': ['It is very still here. Too still. Something is listening.'],
    'eye': ['The eye of the deep. The dark here has a shape.'],
    'ramp': ['A wide ramp, scraped smooth by something heavy going up and down.'],
    'burnt': ['Burnt bones and glassy stone. Something breathed fire here.'],
    'feed': ['A feeding pit. The bones are fresh.'],
    'pups': ['A pup den, full of whines and the smell of milk.'],
    'bonepit': ['The bone pit of the bone-caller. Every kill they ever made lies here.'],
    'drowned': ['A drowned hall. The water stands to your knees.'],
    'niches': ['A gallery of niches. The dead lie on shelves in the walls.', 'Niches full of bones, row on row.'],
    'ossuary': ['An ossuary: skulls stacked to the roof, long bones in bundles.'],
    'chapel': ['A small chapel for the dead. The candles went out long ago.'],
    'tomb': ['A sealed tomb. The slab has been moved, a little.'],
}


def kind_for(d):
    return KIND_OF_TAG.get(d.tag, d.tag)


def plan_for(d, depth):
    """Does this level get its own plan? Not the older bottom under a temple, nor the mines or classic dungeons."""
    if depth > d.depth or getattr(d, 'varnish', False):
        return None
    k = kind_for(d)
    return k if k in KINDS else None


# ------------------------------------------------------------------ shapes
def blob(cx, cy, rx, ry, rough=.18):
    """A rounded chamber with a rough edge."""
    out = set()
    k = [random.uniform(-rough, rough) for _ in range(12)]
    for y in range(cy - ry - 1, cy + ry + 2):
        for x in range(cx - rx - 1, cx + rx + 2):
            a = math.atan2(y - cy, x - cx)
            j = (a + math.pi) / (2 * math.pi) * 12
            i0 = int(j) % 12
            f = j - int(j)
            r = 1 + k[i0] * (1 - f) + k[(i0 + 1) % 12] * f
            if ((x - cx) / (rx + .5)) ** 2 + ((y - cy) / (ry + .5)) ** 2 <= r * r:
                out.add((x, y))
    return out


def box(cx, cy, rx, ry):
    return {(x, y) for y in range(cy - ry, cy + ry + 1) for x in range(cx - rx, cx + rx + 1)}


def brush(x, y, w):
    """The cells a way of width w covers at (x, y)."""
    lo = -(w - 1) // 2
    return {(x + dx, y + dy) for dx in range(lo, lo + w) for dy in range(lo, lo + w)}


def way(a, b, w, wiggle, inside):
    """A way from a to b, w wide; it wanders by `wiggle` (0: straight, an L for built places)."""
    x, y = a
    out = set()
    if not wiggle:
        bend = (b[0], a[1]) if random.random() < .5 else (a[0], b[1])
        for p, q in ((a, bend), (bend, b)):
            x, y = p
            while (x, y) != q:
                out |= brush(x, y, w)
                x += (q[0] > x) - (q[0] < x)
                y += (q[1] > y) - (q[1] < y)
            out |= brush(x, y, w)
        return {c for c in out if inside(*c)}
    k = 0
    while (x, y) != b and k < 2000:
        k += 1
        out |= brush(x, y, w)
        dx, dy = (b[0] > x) - (b[0] < x), (b[1] > y) - (b[1] < y)
        if random.random() < wiggle:
            nx, ny = (x, y + random.choice((-1, 1))) if abs(b[0] - x) > abs(b[1] - y) else (x + random.choice((-1, 1)), y)
        elif dx and (not dy or random.random() < abs(b[0] - x) / (abs(b[0] - x) + abs(b[1] - y))):
            nx, ny = x + dx, y
        else:
            nx, ny = x, y + dy
        if not inside(nx, ny):
            nx, ny = (x + dx, y) if dx else (x, y + dy)
        x, y = nx, ny
    out |= brush(*b, w)
    return {c for c in out if inside(*c)}


# ------------------------------------------------------------------ the plan
class Room:
    __slots__ = ('role', 'cx', 'cy', 'rx', 'ry', 'cells')

    def __init__(self, role, cx, cy, rx, ry, cells):
        self.role, self.cx, self.cy, self.rx, self.ry, self.cells = role, cx, cy, rx, ry, cells


def _place(w, h, spec, built, small):
    """Rooms laid out over the level: the first on the west side, the last far from it; none touching."""
    rooms = []
    margin = 3
    wanted = []
    for role, n, rxr, ryr in spec['rooms']:
        for _ in range(n):
            wanted.append((role, random.randint(*rxr), random.randint(*ryr)))
    first = [r for r in wanted if r[0] == spec['first']][:1]
    last = [r for r in wanted if r[0] == spec['last']][:1]
    rest = [r for r in wanted if r not in first and r not in last]
    order = first + last + rest

    def free(cx, cy, rx, ry):
        if cx - rx < margin or cy - ry < margin or cx + rx >= w - margin or cy + ry >= h - margin:
            return False
        return all(abs(cx - o.cx) > rx + o.rx + 3 or abs(cy - o.cy) > ry + o.ry + 3 for o in rooms)
    for k, (role, rx, ry) in enumerate(order):
        for tries in range(300):
            if k == 0:
                cx, cy = random.randint(rx + 4, rx + 10), random.randint(h // 3, 2 * h // 3)
            elif k == 1:
                cx, cy = random.randint(w - rx - 14, w - rx - 5), random.randint(ry + 5, h - ry - 6)
            else:
                cx, cy = random.randint(rx + margin, w - rx - margin - 1), random.randint(ry + margin, h - ry - margin - 1)
            if free(cx, cy, rx, ry):
                cells = box(cx, cy, rx, ry) if built else blob(cx, cy, rx, ry, .14 if small else .2)
                rooms.append(Room(role, cx, cy, rx, ry, cells))
                break
            if tries > 150:
                rx, ry = max(3, rx - 1), max(2, ry - 1)
    return rooms


def _links(rooms):
    """Which rooms a way joins: a tree by nearness, and one or two loops."""
    if len(rooms) < 2:
        return []
    inn, out = {0}, set(range(1, len(rooms)))
    links = []
    dist = lambda a, b: math.hypot(rooms[a].cx - rooms[b].cx, rooms[a].cy - rooms[b].cy)  # noqa: E731
    while out:
        a, b = min(((a, b) for a in inn for b in out), key=lambda p: dist(*p))
        links.append((a, b))
        inn.add(b)
        out.discard(b)
    extra = sorted(((a, b) for a in range(len(rooms)) for b in range(a + 1, len(rooms))
                    if (a, b) not in links and (b, a) not in links), key=lambda p: dist(*p))
    for a, b in extra[:random.randint(1, 2)]:
        links.append((a, b))
    return links


def carve(game, m, d, depth, kind):
    """Lay out a level of this kind on m (filled with rock or wall). Returns (up, down) cells."""
    spec = KINDS[kind]
    built = spec.get('built', False)
    rooms = _place(m.w, m.h, spec, built, spec.get('small'))
    inside = lambda x, y: 1 <= x < m.w - 1 and 1 <= y < m.h - 1  # noqa: E731
    floor = set()
    for r in rooms:
        floor |= {c for c in r.cells if inside(*c)}
    main = set()
    for k, (a, b) in enumerate(_links(rooms)):
        ra, rb = rooms[a], rooms[b]
        w = spec['main'] if {a, b} & {0, 1} or k == 0 else spec['wide']
        cells = way((ra.cx, ra.cy), (rb.cx, rb.cy), w, spec['wiggle'], inside)
        floor |= cells
        if w == spec['main']:
            main |= cells
    m.t = [ROCK if not built else WALL] * (m.w * m.h)
    for x, y in floor:
        m.t[y * m.w + x] = FLOOR
    m.delve, m.built = kind, built
    m.room_of = bytearray(b'\xff') * (m.w * m.h)
    m.rooms = []
    for r in rooms:
        rid = len(m.rooms)
        m.rooms.append([f'delve:{r.role}', 'room', None])
        for x, y in r.cells:
            if inside(x, y):
                m.room_of[y * m.w + x] = rid
    m.delve_rooms = [(r.role, r.cx, r.cy) for r in rooms]
    if built:
        _doors(m, rooms)
    up = _spot(m, rooms[0], (rooms[0].cx - rooms[0].rx // 2, rooms[0].cy))
    down = _spot(m, rooms[1], (rooms[1].cx, rooms[1].cy))
    _join(m, up)
    if spec.get('stream'):
        _stream(m, up, down)
    for rid, r in enumerate(rooms):
        if r.role in ('pool', 'lake'):
            _water(m, r, up, down, deep=True)
        elif r.role == 'drowned':
            _water(m, r, up, down, deep=False)
    return up, down


def _spot(m, r, want):
    cells = [c for c in r.cells if m.inb(*c) and m.tile(*c) == FLOOR]
    return min(cells, key=lambda c: (c[0] - want[0]) ** 2 + (c[1] - want[1]) ** 2) if cells else want


def _doors(m, rooms):
    """Built places: where a way meets a room's wall, wall it up but for a door in the middle of the opening."""
    for r in rooms:
        x0, x1, y0, y1 = r.cx - r.rx, r.cx + r.rx, r.cy - r.ry, r.cy + r.ry
        for side in ([(x, y0 - 1) for x in range(x0, x1 + 1)], [(x, y1 + 1) for x in range(x0, x1 + 1)],
                     [(x0 - 1, y) for y in range(y0, y1 + 1)], [(x1 + 1, y) for y in range(y0, y1 + 1)]):
            runs, cur = [], []
            for c in side + [None]:
                if c is not None and m.inb(*c) and m.tile(*c) == FLOOR:
                    cur.append(c)
                elif cur:
                    runs.append(cur)
                    cur = []
            for run in runs:
                for c in run:
                    m.set(c[0], c[1], WALL)
                mid = run[len(run) // 2]
                m.set(mid[0], mid[1], DOOR)


def _join(m, start):
    """Every floor reachable from the stairs: a part cut off gets a short way to the rest."""
    passable = lambda t: D.TILES[t].walk or t == DOOR  # noqa: E731
    for _ in range(12):
        seen = {start}
        q = deque([start])
        while q:
            x, y = q.popleft()
            for a, b in D4:
                c = (x + a, y + b)
                if c not in seen and m.inb(*c) and passable(m.tile(*c)):
                    seen.add(c)
                    q.append(c)
        rest = [(i % m.w, i // m.w) for i, t in enumerate(m.t) if passable(t) and (i % m.w, i // m.w) not in seen]
        if not rest:
            return
        c = rest[0]
        near = min(seen, key=lambda s: abs(s[0] - c[0]) + abs(s[1] - c[1]))
        x, y = c
        while (x, y) != near:
            if m.tile(x, y) in (ROCK, WALL, D.PROP):
                m.set(x, y, FLOOR)
            if x != near[0]:
                x += 1 if near[0] > x else -1
            else:
                y += 1 if near[1] > y else -1


def _water(m, r, up, down, deep):
    """A pool or lake in a room, deep in the middle, wading round the edge; a drowned hall is shallow all over.
    The way from the stairs up to the stairs down always stays open."""
    cells = [c for c in r.cells if m.inb(*c) and m.tile(*c) == FLOOR and c not in (up, down)]
    if not deep:
        for x, y in cells:
            if (x * 7 + y * 13) % 9:
                m.set(x, y, SHALLOW)
        return
    inner = blob(r.cx, r.cy, max(2, r.rx - 2), max(1, r.ry - 2), .25)
    for x, y in cells:
        if (x, y) in inner:
            m.set(x, y, SHALLOW)
    for x, y in cells:
        if m.tile(x, y) == SHALLOW and all(m.tile(x + a, y + b) in (SHALLOW, WATER) for a, b in D4):
            m.set(x, y, WATER)
    if not _reach(m, up, down):
        for x, y in cells:
            if m.tile(x, y) == WATER:
                m.set(x, y, SHALLOW)


def _reach(m, a, b):
    seen = {a}
    q = deque([a])
    while q:
        c = q.popleft()
        if c == b:
            return True
        for dx, dy in D4:
            n = (c[0] + dx, c[1] + dy)
            if n not in seen and m.inb(*n) and (D.TILES[m.tile(*n)].walk or m.tile(*n) == DOOR):
                seen.add(n)
                q.append(n)
    return False


def _stream(m, a, b):
    """A stream from the way in to the far end, two wide, shallow water you wade."""
    prev = {a: None}
    q = deque([a])
    while q:
        c = q.popleft()
        if c == b:
            break
        for dx, dy in D4:
            n = (c[0] + dx, c[1] + dy)
            if n not in prev and m.inb(*n) and m.tile(*n) == FLOOR:
                prev[n] = c
                q.append(n)
    if b not in prev:
        return
    c = prev[b]
    path = []
    while c is not None and c != a:
        path.append(c)
        c = prev[c]
    for k, (x, y) in enumerate(path[3:-3]):
        for dx, dy in ((0, 0), (1, 0) if k % 7 < 4 else (0, 1)):
            if m.tile(x + dx, y + dy) == FLOOR:
                m.set(x + dx, y + dy, SHALLOW)


# ------------------------------------------------------------------ the folk and the things
THINGS = {
    'cook': [(D.FIREPIT, 1, 'mid'), (D.BARREL, 2, 'wall')],
    'sleep': [(D.FURS, 4, 'wall')],
    'store': [(D.BARREL, 3, 'wall'), (D.MIDDEN, 1, 'any')],
    'hoard': [(D.GLITTER, 3, 'any')],
    'loot': [(D.BARREL, 2, 'wall'), (D.GLITTER, 1, 'wall')],
    'leader': [(D.HIGHSEAT, 1, 'wall')],
    'lookout': [(D.GONG, 1, 'wall')],
    'food': [(D.MIDDEN, 3, 'any')],
    'eggs': [(D.EGGS, 4, 'any')],
    'larder': [(D.REMAINS, 3, 'any')],
    'brood': [(D.EGGS, 2, 'any')],
    'wrecks': [(D.BARREL, 2, 'any'), (D.CHEST, 1, 'wall')],
    'crystal': [(D.CRYSTAL, 3, 'wall')],
    'glow': [(D.SHROOM, 6, 'any')],
    'hoard_dragon': [(D.GLITTER, 8, 'any'), (D.CHEST, 2, 'any')],
    'burnt': [(D.BONES, 3, 'any')],
    'feed': [(D.BONES, 3, 'any')],
    'bonepit': [(D.BONES, 6, 'any'), (D.ALTAR, 1, 'mid')],
    'pups': [(D.FURS, 3, 'wall')],
    'niches': [(D.BONES, 4, 'wall')],
    'ossuary': [(D.BONES, 8, 'any')],
    'chapel': [(D.ALTAR, 1, 'mid'), (D.PEW, 4, 'any')],
    'tomb': [(D.BIER, 1, 'mid')],
}
# who stands where: (how, count of packs); how: guard (awake), sleep, lone (one beast), leader (the bottom)
FOLK = {'mouth': ('guard', 1), 'lookout': ('watch', 1), 'stair': ('none', 0), 'cook': ('guard', 1), 'sleep': ('sleep', 1),
        'store': ('none', 0), 'hoard': ('leader', 1), 'loot': ('none', 0), 'leader': ('leader', 1), 'hall': ('sleep', 1),
        'crawl': ('none', 0), 'dens': ('sleep', 1), 'pool': ('leader', 1), 'food': ('guard', 1), 'eggs': ('guard', 1),
        'workers': ('guard', 1), 'queen': ('leader', 1), 'webs': ('sleep', 1), 'larder': ('none', 0), 'brood': ('leader', 1),
        'wrecks': ('none', 0), 'ledge': ('none', 0), 'lake': ('leader', 1), 'glow': ('sleep', 1), 'crystal': ('none', 0),
        'still': ('sleep', 1), 'eye': ('leader', 1), 'ramp': ('guard', 1), 'burnt': ('none', 0), 'feed': ('guard', 1),
        'pups': ('sleep', 1), 'bonepit': ('leader', 1), 'drowned': ('sleep', 1), 'niches': ('sleep', 1),
        'ossuary': ('guard', 1), 'chapel': ('none', 0), 'tomb': ('leader', 1)}


def folk(game, m, d, depth, up, down):
    """The things in each room and the folk where they belong. Returns how many packs it placed."""
    from .worldgen import spawn_pack, free_around
    lvl = d.base + depth
    last = depth >= d.depth
    kind = m.delve
    packs = 0
    budget = 3 + depth + (1 if not KINDS[kind].get('small') else 0)
    if d.tag == 'den':
        budget = 4
    roles = list(enumerate(m.delve_rooms))
    random.shuffle(roles)
    roles.sort(key=lambda r: FOLK.get(r[1][0], ('none', 0))[0] != 'leader')
    for rid, (role, cx, cy) in roles:
        things = THINGS.get('hoard_dragon' if kind == 'lair_dragon' and role == 'hoard' else role, [])
        _things(m, rid, things, (up, down))
        how, n = FOLK.get(role, ('sleep', 1))
        if how == 'none' or packs >= budget:
            continue
        spot = _spot(m, _RoomView(m, rid), (cx, cy))
        if how == 'leader':
            if not last:
                continue                            # the leader waits at the bottom; the way down is here instead
            if d.boss and d.boss in D.MONSTERS:
                if not any(o.k == d.boss for o in m.mons):
                    boss = make_monster(game, d.boss, spot[0], spot[1], lvl)
                    m.mons.append(boss)
            spawn_pack(game, m, lvl + 1, d.tag, spot, 1 if d.tag != 'den' else 0, False)
            packs += 1
        elif how == 'watch':
            spawn_pack(game, m, lvl, d.tag, spot, 0, True)
            for o in m.mons[-3:]:
                o.watch = True                       # sees you and strikes the gong
            packs += 1
        else:
            spawn_pack(game, m, lvl, d.tag, spot, None if d.tag != 'den' else 0, how == 'guard')
            packs += 1
    m.watch_turns = 0
    if KINDS[kind].get('props'):
        _props(m)
    if kind in ('den', 'warren'):
        _snares(game, m, up, lvl)
    if KINDS[kind].get('sky') and last:
        far = max((c for c in _RoomView(m, 1).cells if m.tile(*c) == FLOOR),
                  key=lambda c: abs(c[0] - up[0]) + abs(c[1] - up[1]), default=None)
        if far:
            m.set(far[0], far[1], UP)               # a way out to the sky, as the dragon goes
            m.sky_exit = far
    if kind == 'warren' and depth == 1:
        _back_way(m, up)
    return packs


class _RoomView:
    def __init__(self, m, rid):
        self.cells = [(i % m.w, i // m.w) for i, r in enumerate(m.room_of) if r == rid]


def _things(m, rid, things, keep):
    cells = [c for c in _RoomView(m, rid).cells if m.tile(*c) == FLOOR and all(abs(c[0] - k[0]) + abs(c[1] - k[1]) > 2
                                                                               for k in keep if k)]
    if not cells:
        return
    xs = [c[0] for c in cells]
    ys = [c[1] for c in cells]
    mid = ((min(xs) + max(xs)) // 2, (min(ys) + max(ys)) // 2)
    wallish = [c for c in cells if any(m.tile(c[0] + a, c[1] + b) in (ROCK, WALL) for a, b in D4)]
    for t, n, where in things:
        for _ in range(n):
            pool = wallish if where == 'wall' else cells
            if where == 'mid':
                pool = sorted(cells, key=lambda c: (c[0] - mid[0]) ** 2 + (c[1] - mid[1]) ** 2)[:3]
            pool = [c for c in pool if m.tile(*c) == FLOOR]
            if not pool:
                break
            c = random.choice(pool)
            if t in (D.EGGS, D.SHROOM) or _keeps_way(m, c):
                m.set(c[0], c[1], t)


def _keeps_way(m, c):
    """A thing may stand here if it closes no way: at most one of its four sides leads on."""
    open_ = [D.TILES[m.tile(c[0] + a, c[1] + b)].walk for a, b in D4]
    return sum(open_) >= 3 or (sum(open_) == 2 and not (open_[0] and open_[1]) and not (open_[2] and open_[3]))


def _props(m):
    """Goblin and kobold ways braced with pit props: on the rock beside a narrow way, now and then."""
    for i, t in enumerate(m.t):
        if t != ROCK or m.room_of[i] != 255:
            continue
        x, y = i % m.w, i // m.w
        if (x * 5 + y * 3) % 7:
            continue
        if any(m.tile(x + a, y + b) == FLOOR and m.room_of[(y + b) * m.w + x + a] == 255 for a, b in D4 if m.inb(x + a, y + b)):
            m.t[i] = D.PROP


def _snares(game, m, up, lvl):
    """Tripwires and a covered pit on the ways in: the way to the rest of the hole."""
    from .behave import traps
    tr = traps(m)
    kinds = m.__dict__.setdefault('trap_kind', {})
    ways = [(i % m.w, i // m.w) for i, t in enumerate(m.t) if t == FLOOR and m.room_of[i] == 255
            and 6 <= abs(i % m.w - up[0]) + abs(i // m.w - up[1]) <= 30]
    random.shuffle(ways)
    for k, c in enumerate(ways[:3]):
        tr[c] = 2 + lvl // 2
        kinds[c] = 'wire' if m.delve == 'warren' and k < 2 else kinds.get(c, 'snare')
        if kinds[c] == 'snare':
            kinds.pop(c)
    if m.delve == 'warren' and len(ways) > 3:
        c = ways[3]
        tr[c] = 4 + lvl
        kinds[c] = 'pit'


def _back_way(m, up):
    """The narrow back way out of a goblin hole, where they flee: a second way up, far from the first."""
    rid = max(range(len(m.delve_rooms)), key=lambda r: abs(m.delve_rooms[r][1] - up[0]) + abs(m.delve_rooms[r][2] - up[1]))
    cells = [c for c in _RoomView(m, rid).cells if m.tile(*c) == FLOOR]
    if not cells:
        return
    c = max(cells, key=lambda q: (q[1] < m.h // 2) * 100 - q[1] + q[0])
    m.set(c[0], c[1], UP)
    m.back_way = c


def tomb(game, m, x, y):
    """A sealed tomb in a crypt: push the slab aside for what was buried with the dead, once."""
    from .entities import Item, random_gear
    from .money import purse
    done = m.__dict__.setdefault('tombs_opened', set())
    if (x, y) in done:
        game.msg('The slab lies askew. You took what lay here.', 'info')
        return 0
    done.add((x, y))
    game.spill(m, x, y, Item(game.new_id(), 'gold', 'gold', purse(m.level, 2)))
    if random.random() < .5:
        game.spill(m, x, y, random_gear(game, m.level + 1, 1.5))
    game.msg('You heave the slab aside. Grave goods glint among the bones.', 'good')
    return 2


# ------------------------------------------------------------------ while you are there
def tick(game):
    """Each step: a goblin watch that has seen you for two turns strikes the gong, and the hole wakes."""
    m = game.map
    if getattr(m, 'delve', None) != 'warren' or getattr(m, 'gong_struck', False):
        return
    p = game.player
    vis = getattr(game, 'visible', None)
    watch = [o for o in m.mons if getattr(o, 'watch', False) and o.hp > 0]
    seen = [o for o in watch if max(abs(o.x - p.x), abs(o.y - p.y)) <= 8 and (vis is None or vis[o.y * m.w + o.x])]
    if not seen:
        m.watch_turns = 0
        return
    m.watch_turns = getattr(m, 'watch_turns', 0) + 1
    if m.watch_turns >= 2:
        strike(game, m, seen[0])


def strike(game, m, who):
    m.gong_struck = True
    for o in m.mons:
        if not o.is_npc:
            o.awake = True
    game.msg(f'{who.the()[0].upper() + who.the()[1:]} strikes the alarm gong! The whole hole wakes.', 'bad')


def wire(game):
    """A tripwire: a rattle of tins down the way, and the nearest den wakes."""
    m, p = game.map, game.player
    game.msg('Your foot catches a tripwire. Tins rattle away down the passage!', 'bad')
    for o in m.mons:
        if not o.is_npc and max(abs(o.x - p.x), abs(o.y - p.y)) <= 14:
            o.awake = True


def pit(game, dmg):
    """A covered pit: down you go, onto the stakes, or through to the level below."""
    m = game.map
    dg = game.world.dungeons.get(m.did)
    game.flash([(game.player.x, game.player.y)], (200, 180, 140), '░', .3)
    if dg is not None and m.depth < dg.depth:
        game.msg('The floor gives under you: a pit, covered with sticks and earth! You drop through to the level below.',
                 'bad')
        game.enter_dungeon(dg.id, m.depth + 1, 'up')
        from .worldgen import rand_free
        c = rand_free(game, game.map, lambda t: t == FLOOR)
        if c:
            game.player.x, game.player.y = c
        game.compute_fov()
    else:
        game.msg('The floor gives under you: a covered pit with stakes in it!', 'bad')
    game.hurt(dmg, 'a covered pit')


def bump(game, x, y):
    """The things of an underground place: the alarm gong, a sealed tomb, a nest's eggs. Returns turns spent, or None."""
    m = game.map
    t = m.tile(x, y)
    if t == D.GONG:
        if not getattr(m, 'gong_struck', False):
            m.gong_struck = True
            for o in m.mons:
                if not o.is_npc:
                    o.awake = True
        game.msg('You strike the gong. Every goblin in the hole knows you are here now.', 'info')
        return 1
    if t == D.BIER:
        return tomb(game, m, x, y)
    if t != D.EGGS:
        return None
    m.set(x, y, FLOOR)
    if m.deco is not None:
        m.deco[y * m.w + x] = 0
    woke = 0
    for o in m.mons:
        if not o.is_npc and not o.awake:
            o.awake = True
            woke += 1
    game.msg('You smash the eggs. A shrill sound runs through the whole nest' +
             (', and it comes for you!' if woke else '.'), 'bad' if woke else 'info')
    game.gain_xp(1)
    return 1
