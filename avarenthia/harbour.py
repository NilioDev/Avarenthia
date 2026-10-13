"""Harbours: the settlements on the coast get a waterfront on the side that faces the sea, with a stone quay,
wooden piers, boats tied up at them, a fish market, a sailors' tavern full of tales (the Sky-Seat among them)
and the Brotherhood of the Net. There is no sailing yet; the boats are waiting for that."""
import random

from . import data as D
from .data import WATER, SHALLOW, PATH, PLANK, STALL, BARREL, WALL, GRASS, TREE

SEA_BIOMES = ('ocean', 'sea', 'shallows', 'surf', 'reef')
DEPTH = 12            # how far the waterfront reaches into the map: sea, shallows, quay


def mark_coast(m, world):
    """Which settlements lie on the sea, and on which side of them."""
    names = getattr(m, 'biome_names', [])
    sea_ids = {names.index(b) for b in SEA_BIOMES if b in names}
    for s in world.settlements:
        s.harbour, s.sea_side = False, None
        if s.kind == 'deephold':
            continue
        sx = sy = n = 0
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                x, y = s.x + dx, s.y + dy
                if m.inb(x, y) and m.tile(x, y) == WATER and m.biome[y * m.w + x] in sea_ids:
                    sx, sy, n = sx + dx, sy + dy, n + 1
        if n >= 3:
            s.harbour = True
            if abs(sx) >= abs(sy):
                s.sea_side = 'E' if sx > 0 else 'W'
            else:
                s.sea_side = 'S' if sy > 0 else 'N'


def band(m, side):
    """The cells of the waterfront: (x0, y0, x1, y1) inclusive, and a function giving depth from the map edge."""
    if side == 'N':
        return (0, 0, m.w - 1, DEPTH - 1), lambda x, y: y
    if side == 'S':
        return (0, m.h - DEPTH, m.w - 1, m.h - 1), lambda x, y: m.h - 1 - y
    if side == 'W':
        return (0, 0, DEPTH - 1, m.h - 1), lambda x, y: x
    return (m.w - DEPTH, 0, m.w - 1, m.h - 1), lambda x, y: m.w - 1 - x


def carve(m, s):
    """Lay the waterfront: open sea at the edge, then shallows, then a quay of stone. Returns a plot to keep free."""
    from .towns import Plot
    (x0, y0, x1, y1), depth = band(m, s.sea_side)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            d = depth(x, y)
            if d < 7:
                m.set(x, y, WATER)
            elif d < 9:
                m.set(x, y, SHALLOW)
            else:
                m.set(x, y, PATH)               # the quay
    m.harbour_side = s.sea_side
    m.exits = [e for e in getattr(m, 'exits', []) if not (x0 <= e[0] <= x1 and y0 <= e[1] <= y1)] or getattr(m, 'exits', [])
    pad = 2
    return Plot(max(0, x0 - pad), max(0, y0 - pad), x1 - x0 + 1 + 2 * pad, y1 - y0 + 1 + 2 * pad, 'harbour')


def furnish(game, m, s, names):
    """Piers and boats along the quay, the fish market, the Net Hall and the sailors."""
    from .entities import make_npc
    from .towns import townsfolk, town_names
    names = town_names(getattr(s, 'race', 'human'))
    side = m.harbour_side
    (x0, y0, x1, y1), depth = band(m, side)
    horiz = side in ('N', 'S')
    length = (x1 - x0) if horiz else (y1 - y0)
    out = -1 if side in ('N', 'W') else 1          # the direction of the open sea

    def at(along, d):
        """The cell `along` the coast, `d` cells in from the map edge."""
        if side == 'N':
            return along, d
        if side == 'S':
            return along, m.h - 1 - d
        if side == 'W':
            return d, along
        return m.w - 1 - d, along
    boats = 0
    for k, a in enumerate(range(8, length - 8, 11)):
        for d in range(3, 10):                       # a wooden pier out into the water
            x, y = at(a, d)
            m.set(x, y, PLANK)
        for d in (4, 6):                             # boats tied up alongside
            x, y = at(a + 1, d)
            if m.tile(x, y) in (WATER, SHALLOW) and random.random() < .8:
                m.set(x, y, D.BOAT)
                boats += 1
        if k % 2 == 0:
            x, y = at(a + 2, 10)
            if m.tile(x, y) == PATH:
                m.set(x, y, BARREL)
    # the fish market on the quay
    mid = length // 2
    for a in range(mid - 4, mid + 5, 2):
        x, y = at(a, 11)
        if m.inb(x, y):
            m.set(x, y, STALL)
    fx, fy = at(mid, 10)
    m.mons.append(make_npc(game, f'{names.pop() if names else "Old Wenna"} the Fishmonger', 'market', '#80c0e0', fx, fy, True))
    # the Brotherhood of the Net keeps its table at the end of the quay
    from . import guilds as GU
    if s.id in getattr(game.world, 'guild_halls', {}).get('anglers', []):
        gx, gy = at(mid + 9, 10)
        npc = make_npc(game, GU.master_name('anglers', names), 'guild', GU.GUILDS['anglers']['fg'], gx, gy, True)
        npc.guild = 'anglers'
        m.mons.append(npc)
        m.signs.append((max(0, gx - 4), gy + (1 if side in ('N', 'W') else -1) * (1 if horiz else 0), 'NET HALL'))
    # sailors on the quay and in the tavern
    inn = None
    for o in m.mons:
        if o.role == 'inn':
            inn = o
            break
    for _ in range(random.randint(2, 4)):
        a = random.randint(6, max(7, length - 6))
        work = at(a, 10)
        home = [(inn.x, inn.y + 1)] if inn else [work]
        t = townsfolk(game, m, home, work, names, 'sailor', fg='#b0c8d8')
        t.job = 'sailor'
    m.signs[:] = [(sx, sy, ("SAILORS' REST" if txt == 'INN' and inn and abs(sy - inn.y) < 12 else txt)) for sx, sy, txt in m.signs]
    m.boats = boats


SAILOR_BARKS = [
    'Out past the reefs in the warm south, the sea turns. Round and round. The old hands steer well clear.',
    'I saw it once, on a clear morning, far out: a black rock hanging in the sky. Nobody believes me. You don\'t either.',
    'They call it the Sky-Seat. The city of the Varnish fell into the sea, all but one piece that never came down.',
    'There\'s an atoll down south, torn open on one side. A wreck lies on the reef. Nobody who went to look came back rich.',
    'When the boats can sail that far, I\'ll take you. Not before. The currents down there eat ships.',
    'Fish don\'t care about kings. That\'s why I like fish.',
    'Salt in your beard, tar on your hands, and nothing in your purse. A sailor\'s life.',
    'The gulls know when a storm comes. Watch the gulls.',
]
