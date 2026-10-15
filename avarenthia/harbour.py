"""Harbours. Every settlement on the coast has a waterfront on the side that faces the sea, and how much of one
depends on how big the place is:

hamlet      a short jetty or two, boats drawn up on the beach, nets drying
village     two jetties (one bent into an L), a boathouse, a fishmonger, drying racks
town        a cove with a stone quay at its head, three piers none alike, a warehouse and the Net Hall
city        a straight quay with a deep berth and a big ship at it, a crane, a harbour wall with a beacon,
            a fish market under awnings, a customs house
metropolis  two basins split by a mole, a lighthouse, a shipyard with a hull on the slip, ships everywhere

In the fjords there is no beach: a ledge on the rock with a tiny jetty, or nothing at all.
There is no sailing yet; the boats and the ships are waiting for that."""
import math
import random

from . import data as D
from .data import WATER, SHALLOW, PATH, PLANK, STALL, BARREL, WALL, GRASS, SAND, ROCK, TABLE

SEA_BIOMES = ('ocean', 'sea', 'shallows', 'surf', 'reef', 'fjord')
DEPTHS = {'hamlet': 10, 'village': 12, 'town': 18, 'city': 22, 'metropolis': 26}
DEPTH = 12            # the old default, for maps made before the harbours had tiers

STONE = ((160, 154, 144), (70, 66, 60))
HULL, HULL_DARK, DECK, PLANKS = (190, 132, 76), (140, 96, 56), (150, 110, 66), (118, 84, 50)
SHIP_HULL, SHIP_EDGE = (86, 56, 32), (60, 40, 24)
WATER_BG, SHALLOW_BG, SAND_BG = (6, 20, 48), (23, 50, 82), (40, 34, 22)
FISH = [('π', (170, 150, 110)), ('#', (150, 150, 140)), ('○', (160, 110, 60))]
CARGO = [('○', (160, 110, 60)), ('■', (150, 110, 70)), ('■', (120, 90, 60)), ('≡', (180, 160, 120))]
AWNINGS = ((70, 110, 190), (220, 220, 210), (190, 70, 60), (200, 170, 70))


def mark_coast(m, world):
    """Which settlements lie on the sea, and on which side of them; and which of them sit in a fjord."""
    names = getattr(m, 'biome_names', [])
    sea_ids = {names.index(b) for b in SEA_BIOMES if b in names}
    fj = names.index('fjord') if 'fjord' in names else -1
    cliff = names.index('cliff') if 'cliff' in names else -1
    for s in world.settlements:
        s.harbour, s.sea_side, s.fjord = False, None, False
        if s.kind == 'deephold':
            continue
        sx = sy = n = nf = 0
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                x, y = s.x + dx, s.y + dy
                if not m.inb(x, y):
                    continue
                b = m.biome[y * m.w + x]
                if m.tile(x, y) == WATER and b in sea_ids:
                    sx, sy, n = sx + dx, sy + dy, n + 1
                if b in (fj, cliff):
                    nf += 1
        if n >= 3:
            s.harbour = True
            s.fjord = nf >= 4 and s.kind in ('hamlet', 'village', 'town')
            if abs(sx) >= abs(sy):
                s.sea_side = 'E' if sx > 0 else 'W'
            else:
                s.sea_side = 'S' if sy > 0 else 'N'


def depth_for(s):
    return 9 if getattr(s, 'fjord', False) else DEPTHS.get(s.kind, DEPTH)


def band(m, side, depth=None):
    """The cells of the waterfront: (x0, y0, x1, y1) inclusive, and a function giving depth from the map edge."""
    dp = depth or getattr(m, 'harbour_depth', DEPTH)
    if side == 'N':
        return (0, 0, m.w - 1, dp - 1), lambda x, y: y
    if side == 'S':
        return (0, m.h - dp, m.w - 1, m.h - 1), lambda x, y: m.h - 1 - y
    if side == 'W':
        return (0, 0, dp - 1, m.h - 1), lambda x, y: x
    return (m.w - dp, 0, m.w - 1, m.h - 1), lambda x, y: m.w - 1 - x


# the four ways a waterfront can face, as screen directions: towards the sea, towards the land, along the coast
SCREEN = {'N': dict(sea='U', land='D', fwd='R', back='L'), 'S': dict(sea='D', land='U', fwd='R', back='L'),
          'W': dict(sea='L', land='R', fwd='D', back='U'), 'E': dict(sea='R', land='L', fwd='D', back='U')}
HALF = {'U': '▀', 'D': '▄', 'L': '▌', 'R': '▐'}
ARROW = {'U': '▲', 'D': '▼', 'L': '◄', 'R': '►'}


class Front:
    """The waterfront in its own coordinates: `a` runs along the coast, `d` counts in from the open sea (0 at the
    map edge). Everything is drawn in these, whichever side the sea is on."""

    def __init__(self, m, side, depth):
        self.m, self.side, self.depth = m, side, depth
        self.length = m.w if side in ('N', 'S') else m.h
        self.dirs = SCREEN[side]
        if not hasattr(m, 'over') or m.over is None:
            m.over = {}

    def xy(self, a, d):
        m, s = self.m, self.side
        if s == 'N':
            return a, d
        if s == 'S':
            return a, m.h - 1 - d
        if s == 'W':
            return d, a
        return m.w - 1 - d, a

    def inb(self, a, d):
        return 0 <= a < self.length and 0 <= d < self.m.w + self.m.h and self.m.inb(*self.xy(a, d))

    def get(self, a, d):
        return self.m.tile(*self.xy(a, d)) if self.inb(a, d) else WATER

    def set(self, a, d, t):
        if self.inb(a, d):
            self.m.set(*self.xy(a, d), t)

    def draw(self, a, d, ch, fg, bg=None):
        if self.inb(a, d):
            x, y = self.xy(a, d)
            self.m.over[y * self.m.w + x] = (ch, fg, bg)

    def undraw(self, a, d):
        if self.inb(a, d):
            x, y = self.xy(a, d)
            self.m.over.pop(y * self.m.w + x, None)

    def wet(self, a, d):
        return self.get(a, d) in (WATER, SHALLOW)

    # glyphs that turn with the coast
    def half(self, way):
        return HALF[self.dirs[way]]

    def arrow(self, way):
        return ARROW[self.dirs[way]]

    def line(self, axis, double=False):
        """A line along the coast ('a') or out to sea ('d')."""
        across = self.dirs['fwd'] in ('L', 'R')
        horiz = across if axis == 'a' else not across
        return ('═' if horiz else '║') if double else ('─' if horiz else '│')

    # ------------------------------------------------------------- the shore
    def shape(self, shore, beach=2, ground=GRASS, keep=(PATH,)):
        """shore(a) is where the land begins. Deep water, then shallows, then sand, then the land."""
        for a in range(self.length):
            sd = shore(a)
            for d in range(self.depth):
                if d < sd - 2:
                    self.set(a, d, WATER)
                elif d < sd:
                    self.set(a, d, SHALLOW)
                elif d < sd + beach:
                    self.set(a, d, SAND)
                elif self.get(a, d) not in keep:
                    self.set(a, d, ground)

    def quay(self, a0, a1, qd, width=2):
        """A straight quay wall: stone from qd inland, dredged water out to sea from it."""
        for a in range(max(0, a0), min(self.length, a1 + 1)):
            for d in range(qd, qd + width):
                self.set(a, d, PATH)
            for d in range(0, qd):
                self.set(a, d, WATER if d < qd - 1 else SHALLOW)

    def dress_stone(self):
        """The stone of the quays: grey flags, and a dark face where they drop into the water."""
        m = self.m
        rng = random.Random(m.w * 31 + m.h)
        for a in range(self.length):
            for d in range(self.depth):
                if self.get(a, d) != PATH or not getattr(self, 'stone', None) or (a, d) not in self.stone:
                    continue
                r = rng.random()
                fg = tuple(max(0, min(255, int(c * (0.92 + r * .16)))) for c in STONE[0])
                bg = tuple(max(0, min(255, int(c * (0.95 + r * .1)))) for c in STONE[1])
                if self.wet(a, d - 1):
                    self.draw(a, d, self.half('sea'), (40, 40, 44), bg)
                else:
                    self.draw(a, d, '.' if r < .3 else ' ' if r < .8 else '·', fg, bg)

    def mark_stone(self, a0, a1, d0, d1):
        self.stone = getattr(self, 'stone', set())
        for a in range(a0, a1 + 1):
            for d in range(d0, d1 + 1):
                if self.get(a, d) == PATH:
                    self.stone.add((a, d))

    # ------------------------------------------------------------- things on the water
    def pier(self, a, d, n, branch=None):
        """A wooden pier from (a, d) out to sea for n cells; branch: (at, side, length) for an L or a T."""
        cells = []
        for i in range(n):
            dd = d - i
            if dd < 1:
                break
            if self.get(a, dd) in (WATER, SHALLOW, SAND, PATH, ROCK, GRASS):
                self.set(a, dd, PLANK)
                cells.append((a, dd))
        if branch and len(cells) > branch[0]:
            at, side, ln = branch
            ba, bd = cells[at]
            for j in range(1, ln + 1):
                if self.wet(ba + side * j, bd):
                    self.set(ba + side * j, bd, PLANK)
                    cells.append((ba + side * j, bd))
        for ca, cd in cells:
            if self.get(ca, cd) != PLANK:
                continue
            along = self.get(ca - 1, cd) == PLANK or self.get(ca + 1, cd) == PLANK
            out = self.get(ca, cd - 1) == PLANK or self.get(ca, cd + 1) == PLANK
            ch = '╬' if along and out else self.line('a', True) if along else self.line('d', True)
            self.draw(ca, cd, ch, (176, 132, 80), (60, 40, 22))
        return cells

    def boat(self, a, d, out=True, beached=False):
        """A rowing boat, three cells long: pointing out to sea, or lying along the shore."""
        cells = [(a, d - i) for i in range(3)] if out else [(a + i, d) for i in range(3)]
        if not all(self.wet(*c) or (beached and self.get(*c) == SAND) for c in cells):
            return False
        for k, (ca, cd) in enumerate(cells):
            bg = SAND_BG if self.get(ca, cd) == SAND else SHALLOW_BG if self.get(ca, cd) == SHALLOW else WATER_BG
            self.set(ca, cd, D.BOAT)
            if out:
                ch = self.arrow('land') if k == 0 else self.arrow('sea') if k == 2 else '█'
            else:
                ch = self.arrow('back') if k == 0 else self.arrow('fwd') if k == 2 else '█'
            self.draw(ca, cd, ch, HULL if ch != '█' else HULL_DARK, bg)
        return True

    def ship(self, a, d, length=14, masts=2, flag=(200, 60, 50)):
        """A big ship seen from above, lying along the quay: bow towards `back`, five cells across, from d (on the
        land side) out to d - 4. Only on open water."""
        L = length
        if not all(self.wet(a + i, d - r) for i in range(L + 1) for r in range(5)):
            return False
        for i in range(L + 1):
            for r in range(5):
                self.set(a + i, d - r, WATER)
        for i in range(2, L):
            self.draw(a + i, d, self.half('sea'), SHIP_HULL, WATER_BG)
            self.draw(a + i, d - 4, self.half('land'), SHIP_HULL, WATER_BG)
        self.draw(a + 1, d - 1, self.half('sea'), SHIP_HULL, WATER_BG)
        self.draw(a + 1, d - 3, self.half('land'), SHIP_HULL, WATER_BG)
        self.draw(a, d - 2, self.arrow('back'), SHIP_HULL, WATER_BG)
        for r in (1, 2, 3):
            for i in range(2 if r != 2 else 1, L):
                self.draw(a + i, d - r, self.line('a'), PLANKS, DECK)
            self.draw(a + L, d - r, self.half('back'), SHIP_HULL, WATER_BG)
            self.draw(a + L - 1, d - r, '▒', (100, 70, 40), (130, 94, 56))
        for k in range(masts):
            ma = a + 3 + round(k * (L - 7) / max(1, masts - 1)) if masts > 1 else a + L // 2
            self.draw(ma, d - 2, '○', (236, 226, 200), DECK)
            for r in (1, 3):
                self.draw(ma, d - r, self.line('d'), (210, 200, 176), DECK)
        self.draw(a + L // 2 + 1, d - 2, '#', SHIP_EDGE, DECK)
        self.draw(a + L, d, self.half('sea'), flag, WATER_BG)
        return True

    def breakwater(self, pts, light=None):
        """A harbour wall of piled stone, two wide, with loose rock tumbled into the sea along it."""
        cells = []
        for (a0, d0), (a1, d1) in zip(pts, pts[1:]):
            n = max(abs(a1 - a0), abs(d1 - d0))
            for t in range(n + 1):
                a = round(a0 + (a1 - a0) * t / max(1, n))
                d = round(d0 + (d1 - d0) * t / max(1, n))
                for ca, cd in ((a, d), (a, d + 1)):
                    if self.inb(ca, cd):
                        self.set(ca, cd, PATH)
                        cells.append((ca, cd))
        self.stone = getattr(self, 'stone', set()) | set(cells)
        rng = random.Random(len(cells))
        for ca, cd in cells:
            for oa, od in ((0, -1), (0, 2), (1, 0), (-1, 0)):
                if self.wet(ca + oa, cd + od) and rng.random() < .45:
                    self.draw(ca + oa, cd + od, '°' if rng.random() < .5 else '∙', (150, 150, 150), (30, 46, 70))
        if light and pts:
            a, d = pts[-1]
            if light == 'tower':
                for oa in (-1, 0, 1):
                    for od in (-1, 0, 1):
                        self.set(a + oa, d + od, PATH)
                        self.stone.add((a + oa, d + od))
                self.light_cell = (a, d)
                self.set(a, d, D.LAMP)
                self.tower = (a, d)
            else:
                self.set(a, d, D.LAMP)
                self.light_cell = (a, d)
        return cells

    def stalls(self, a, d, n):
        """Market stalls under striped awnings, on the quay."""
        for i in range(n):
            c = AWNINGS[i % len(AWNINGS)]
            for k in range(2):
                if self.get(a + i * 3 + k, d) == PATH:
                    self.set(a + i * 3 + k, d, STALL)
                    self.draw(a + i * 3 + k, d, '▀', c, (60, 54, 48))

    def crane(self, a, d):
        self.draw(a, d, 'Γ', (190, 170, 120), STONE[1])
        self.draw(a + 1, d, self.line('a'), (190, 170, 120), STONE[1])
        self.draw(a + 2, d - 1, self.line('d'), (190, 170, 120), STONE[1] if self.get(a + 2, d - 1) == PATH else WATER_BG)

    def scatter(self, a0, a1, d0, d1, n, items, kinds=(PATH, SAND), rng=random):
        for _ in range(n * 8):
            if n <= 0:
                break
            a, d = rng.randint(a0, a1), rng.randint(d0, d1)
            x, y = self.xy(a, d)
            i = y * self.m.w + x
            if self.get(a, d) in kinds and i not in self.m.over:
                ch, fg = rng.choice(items)
                self.set(a, d, BARREL if ch in ('○', '■') else TABLE if ch == 'π' else self.get(a, d))
                bg = SAND_BG if self.get(a, d) == SAND else STONE[1]
                self.draw(a, d, ch, fg, bg)
                n -= 1

    def building(self, a, d, wa, wd, kind, sign, guild=None):
        """A building on the waterfront, `wa` along the coast and `wd` deep, door facing the sea."""
        from .towns import Plot, build, place_door, add_sign
        x0, y0 = self.xy(a, d)
        x1, y1 = self.xy(a + wa - 1, d + wd - 1)
        x, y = min(x0, x1), min(y0, y1)
        w, h = abs(x1 - x0) + 1, abs(y1 - y0) + 1
        if not (self.m.inb(x, y) and self.m.inb(x + w - 1, y + h - 1)):
            return None
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.m.over.pop(yy * self.m.w + xx, None)
        pl = Plot(x, y, w, h, kind)
        build(self.m, pl, WALL, PLANK)
        tx, ty = self.xy(a + wa // 2, d - 3)
        out = place_door(self.m, pl, tx, ty)
        if self.m.inb(*out) and self.m.tile(*out) not in (PATH, PLANK):
            self.m.set(*out, PATH)
        if guild:
            pl.guild = guild
        add_sign(self.m, pl, sign)
        return pl


# ------------------------------------------------------------------ laying out the waterfront
def carve(m, s):
    """Shape the sea and the shore. Returns a plot the town keeps its houses out of."""
    from .towns import Plot
    depth = depth_for(s)
    m.harbour_side, m.harbour_depth, m.harbour_tier = s.sea_side, depth, ('fjord' if getattr(s, 'fjord', False) else s.kind)
    f = Front(m, s.sea_side, depth)
    seed = s.id * 7 + 3
    L = f.length
    tier = m.harbour_tier

    def wobble(a, amp):
        return amp * (math.sin(a * .13 + seed) * .6 + math.sin(a * .31 + seed * 2) * .3)
    if tier == 'fjord':
        for a in range(L):
            for d in range(depth):
                if d < 4:
                    f.set(a, d, WATER)
                elif d < 5:
                    f.set(a, d, SHALLOW)
                else:
                    f.set(a, d, ROCK)
        mid = L // 2 + random.randint(-L // 6, L // 6)
        for a in range(mid - 7, mid + 8):                # a ledge on the rock, and the path up to the town
            for d in range(5, depth):
                if abs(a - mid) + (depth - d) * .4 < 9:
                    f.set(a, d, PATH if abs(a - mid) <= 1 else GRASS)
        m.harbour_mid = mid
    elif tier in ('hamlet', 'village'):
        base = depth - (6 if tier == 'hamlet' else 7)
        f.shape(lambda a: int(round(base + wobble(a, 1.6))), beach=2 if tier == 'village' else 3)
    elif tier == 'town':
        c0, c1 = int(L * .3), int(L * .7)

        def shore(a):
            sd = 5 + wobble(a, 1.4)
            if c0 < a < c1:
                sd += 4 * math.sin((a - c0) / (c1 - c0) * math.pi) ** .7
            return int(round(sd))
        f.shape(shore, beach=2)
        q = (c0 + c1) // 2
        f.quay(c0 + 5, q, 9)
        f.quay(q + 1, c1 - 5, 10)
        for d in range(11, 13):
            for a in range(c0 + 5, c1 - 4):
                if f.get(a, d) in (SAND, GRASS):
                    f.set(a, d, PATH)
        f.mark_stone(c0 + 5, c1 - 5, 9, 12)
        m.harbour_quay = (c0 + 5, c1 - 5)
    else:
        qd = 11 if tier == 'city' else 13
        f.shape(lambda a: qd, beach=0, ground=PATH, keep=())
        f.quay(2, L - 3, qd, 3)
        for a in range(L):
            for d in range(qd, depth):
                f.set(a, d, PATH)
        f.mark_stone(0, L - 1, qd, depth - 1)
    f.dress_stone()
    m.exits = [e for e in getattr(m, 'exits', []) if not band_has(m, e[0], e[1])] or getattr(m, 'exits', [])
    (x0, y0, x1, y1), _dd = band(m, s.sea_side, depth)
    pad = 2
    return Plot(max(0, x0 - pad), max(0, y0 - pad), x1 - x0 + 1 + 2 * pad, y1 - y0 + 1 + 2 * pad, 'harbour')


def band_has(m, x, y):
    (x0, y0, x1, y1), _d = band(m, m.harbour_side)
    return x0 <= x <= x1 and y0 <= y <= y1


def furnish(game, m, s, names):
    """Piers, boats and ships, the buildings of the waterfront, and the people who work there."""
    from .entities import make_npc
    from .towns import townsfolk, town_names, free_inside
    from . import guilds as GU
    names = town_names(getattr(s, 'race', 'human'))
    tier = getattr(m, 'harbour_tier', None) or s.kind
    f = Front(m, m.harbour_side, getattr(m, 'harbour_depth', DEPTH))
    L, dp = f.length, f.depth
    rng = random.Random(s.id * 131 + 7)
    boats = 0
    keeper = None                                    # where the fishmonger stands
    anglers = s.id in getattr(game.world, 'guild_halls', {}).get('anglers', [])
    plots = []

    def shore_at(a):
        return next((d for d in range(dp) if not f.wet(a, d)), dp)
    if tier == 'fjord':
        mid = getattr(m, 'harbour_mid', L // 2)
        if rng.random() < .7:                         # a tiny jetty clinging to the rock, and one boat
            f.pier(mid + 2, 5, 3)
            boats += f.boat(mid + 3, 4)
            keeper = (mid, 6)
        f.scatter(mid - 5, mid + 5, 5, dp - 1, 3, FISH, kinds=(GRASS,), rng=rng)
    elif tier in ('hamlet', 'village'):
        n = 2 if tier == 'village' or rng.random() < .35 else 1
        spots = sorted(rng.sample(range(L // 4, 3 * L // 4), n)) if n > 1 else [L // 2 + rng.randint(-8, 8)]
        if n > 1 and spots[1] - spots[0] < 12:
            spots[1] = min(L - 10, spots[0] + 14)
        for k, a in enumerate(spots):
            sd = shore_at(a)
            ln = 5 if tier == 'hamlet' else (7 if k == 0 else 4)
            branch = (ln - 2, 1 if rng.random() < .5 else -1, 4) if tier == 'village' and k == 0 else None
            f.pier(a, sd + 1, ln + 1, branch)
            boats += f.boat(a + 1, sd - 2) or f.boat(a - 1, sd - 2)
            if k == 0:
                keeper = (a - 1, sd + 1)
        for _ in range(rng.randint(1, 2)):           # boats drawn up on the beach
            a = rng.randint(6, L - 9)
            sd = shore_at(a)
            boats += f.boat(a, sd, out=False, beached=True)
        f.scatter(4, L - 5, 0, dp - 1, 5 if tier == 'hamlet' else 9, FISH, kinds=(SAND,), rng=rng)
        if tier == 'village':
            a = (spots[0] + 6) if spots[0] + 16 < L else spots[0] - 14
            sd = max(shore_at(a + k) for k in range(8)) + 2
            if dp - sd >= 4:
                pl = f.building(a, sd, 8, min(5, dp - sd), 'boathouse', 'BOATHOUSE')
                if pl:
                    plots.append(pl)
    elif tier == 'town':
        q0, q1 = getattr(m, 'harbour_quay', (L // 3, 2 * L // 3))
        span = q1 - q0
        a1, a2, a3 = q0 + span // 6, q0 + span // 2, q0 + 5 * span // 6
        f.pier(a1, 8, 7)
        boats += f.boat(a1 + 1, 7) + f.boat(a1 - 1, 5)
        f.pier(a2, 8, 8, (6, -1, 4))                   # an L
        boats += f.boat(a2 + 1, 7)
        f.pier(a3, 9, 6, (4, 1, 3))                    # a little T
        boats += f.boat(a3 + 1, 8)
        a = rng.randint(6, max(7, q0 - 10))
        boats += f.boat(a, shore_at(a), out=False, beached=True)
        f.scatter(q0, q1, 10, 12, 9, CARGO, kinds=(PATH,), rng=rng)
        keeper = ((a1 + a2) // 2, 11)
        pl = f.building(q0 + 2, 13, 10, dp - 13, 'warehouse', 'WAREHOUSE')
        if pl:
            plots.append(pl)
        if anglers:
            pl = f.building(q1 - 11, 13, 10, dp - 13, 'guild', 'NET HALL', guild='anglers')
            if pl:
                plots.append(pl)
    else:
        big = tier == 'metropolis'
        qd = 13 if big else 11
        # the deep berth, a big ship alongside and a crane over it
        f.ship(4, qd - 2, 15, 2)
        f.set(11, qd - 1, PLANK)
        f.draw(11, qd - 1, f.line('d', True), (150, 110, 70), (60, 40, 22))
        f.crane(20, qd + 1)
        # the harbour wall, out from the far end and bending along the sea, a light at its head
        f.breakwater([(L - 4, qd - 1), (L - 8, 3), (L - (40 if big else 30), 1)], light='tower' if big else 'beacon')
        if big:
            mole = L // 2
            for d in range(1, qd):
                for a in (mole - 1, mole, mole + 1):
                    f.set(a, d, PATH)
                    f.stone.add((a, d))
            f.ship(4, qd - 8, 13, 2, flag=(60, 160, 90))
            f.ship(mole - 18, qd - 3, 14, 3, flag=(220, 190, 60))
            f.ship(mole + 3, qd - 2, 15, 3, flag=(60, 90, 200))
            f.crane(34, qd + 1)
            # the shipyard: a slipway down into the water, a hull on it with its ribs still open
            sa = mole - 30
            for d in range(qd - 2, min(dp - 1, qd + 9)):
                for a in range(sa, sa + 8):
                    f.set(a, d, PLANK if d >= qd else SHALLOW)
                    if d >= qd:
                        f.draw(a, d, '=', (150, 110, 70), (50, 36, 22))
            for d in range(qd + 1, min(dp - 1, qd + 8)):
                f.draw(sa + 1, d, f.line('d', True), (150, 110, 70), (50, 36, 22))
                f.draw(sa + 6, d, f.line('d', True), (150, 110, 70), (50, 36, 22))
                if d % 2:
                    for a in range(sa + 2, sa + 6):
                        f.draw(a, d, f.line('a'), (176, 132, 82), (50, 36, 22))
            m.signs.append((*f.xy(sa, min(dp - 1, qd + 9)), 'SHIPYARD'))
            piers = [(mole + 22, 9, (7, 1, 6)), (mole + 34, 7, (5, -1, 4))]
        else:
            piers = [(L // 2 - 8, 8, (6, 1, 5)), (L // 2 + 3, 9, (7, -1, 3)), (L // 2 + 13, 5, None)]
        for a, n, br in piers:
            f.pier(a, qd - 1, n, br)
            boats += f.boat(a + 1, qd - 3) + f.boat(a - 1, qd - 6)
        f.ship(L // 2 - 22, 5, 12, 2, flag=(200, 60, 50))      # out in the roads, waiting for a berth
        f.stalls(L // 2 - 6, qd + 2, 5)
        keeper = (L // 2 - 4, qd + 3)
        f.scatter(3, L - 4, qd, qd + 2, 16 if big else 12, CARGO, kinds=(PATH,), rng=rng)
        row = qd + 4
        houses = [('customs', 'CUSTOMS HOUSE'), ('warehouse', 'WAREHOUSE'), ('warehouse', 'WAREHOUSE')]
        if big:
            houses.insert(0, ('harbourmaster', 'HARBOUR MASTER'))
        if anglers:
            houses.append(('guild', 'NET HALL'))
        a = 6
        for kind, sign in houses:
            wa = 12
            if big and a < mole - 30 + 9 and a + wa > mole - 31:
                a = mole - 30 + 10
            pl = f.building(a, row, wa, dp - row - 1, kind, sign, guild='anglers' if sign == 'NET HALL' else None)
            if pl:
                plots.append(pl)
            a += wa + 4
            if a + wa >= L - 4:
                break
        f.dress_stone()
    light = getattr(f, 'light_cell', None)
    if light:
        x, y = f.xy(*light)
        m.over[y * m.w + x] = ('☼', (255, 230, 120) if tier == 'metropolis' else (255, 150, 60), (120, 90, 30))
        tw = getattr(f, 'tower', None)
        if tw:
            for side, ch in (('back', '('), ('fwd', ')')):
                a = tw[0] + (-1 if side == 'back' else 1)
                f.draw(a, tw[1], ch, (200, 196, 186), (70, 66, 60))
        m.glows = list(getattr(m, 'glows', [])) + [(x, y, (255, 200, 120), 9)]
        m.lights = list(getattr(m, 'lights', [])) + [(x, y, (255, 200, 120), 9)]
    if tier in ('town', 'city', 'metropolis'):
        f.dress_stone()
    # inside the waterfront buildings
    for pl in plots:
        inside = free_inside(m, pl)
        if pl.kind == 'warehouse':
            for c in inside[:max(2, len(inside) // 5)]:
                m.set(*c, BARREL)
        elif pl.kind in ('customs', 'harbourmaster'):
            for c in inside[:2]:
                m.set(*c, TABLE)
            spot = free_inside(m, pl)
            if spot and names:
                title = 'Harbour Master' if pl.kind == 'harbourmaster' else 'Customs Officer'
                m.mons.append(make_npc(game, f'{names.pop()}, {title}', 'villager', '#b0c8d8', spot[0][0], spot[0][1], True))
        elif getattr(pl, 'guild', None) == 'anglers':
            GU.place_master(game, m, pl, 'anglers', names)
    # the Net-Elder where there is no hall of his own on the water
    if anglers and not any(getattr(pl, 'guild', None) == 'anglers' for pl in plots) and keeper:
        gx, gy = f.xy(keeper[0] + 4, keeper[1])
        if m.inb(gx, gy) and D.TILES[m.tile(gx, gy)].walk and not m.mon_at(gx, gy):
            npc = make_npc(game, GU.master_name('anglers', names), 'guild', GU.GUILDS['anglers']['fg'], gx, gy, True)
            npc.guild = 'anglers'
            m.mons.append(npc)
    # the fishmonger
    if keeper:
        fx, fy = f.xy(*keeper)
        if m.inb(fx, fy) and D.TILES[m.tile(fx, fy)].walk and not m.mon_at(fx, fy):
            m.mons.append(make_npc(game, f'{names.pop() if names else "Old Wenna"} the Fishmonger', 'market', '#80c0e0', fx, fy, True))
    # sailors and fishers on the waterfront, who sleep at the inn
    inn = next((o for o in m.mons if o.role == 'inn'), None)
    walk = [(a, d) for a in range(4, L - 4) for d in range(dp) if f.get(a, d) in (PATH, PLANK, SAND)]
    for _ in range({'fjord': 1, 'hamlet': 1, 'village': 2, 'town': 3, 'city': 4, 'metropolis': 6}.get(tier, 2)):
        if not walk:
            break
        work = f.xy(*rng.choice(walk))
        home = [(inn.x, inn.y + 1)] if inn else [work]
        t = townsfolk(game, m, home, work, names, 'sailor', fg='#b0c8d8')
        t.job = 'sailor'
    m.boats = boats
    m._look = None


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
