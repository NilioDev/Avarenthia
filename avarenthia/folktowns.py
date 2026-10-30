"""Cities that grew, part 2 (round 25): the other peoples build their own way. Dwarves plan (terraces in half rings
up to the gate of the hold), halflings let it ramble (a hedge ring, hills with homes dug into them, the green with
the party tree), half-orcs grow rings of huts round the chief's longhouse and the fighting pit. Each is made in its
own frame with the City of citygrow.py and peopled the same way. Also the bridges on the open land, in the style of
the people whose land it is (`dress_bridges`, called by zones.make). Made from the mockups Nilio approved (project
files, steden/mockup_volken.py)."""
import math
import random

import numpy as np

from . import data as D
from . import citygrow as CG

G, WALLT, PLANK, DOOR, STREET, LANE, WATER = CG.G, CG.WALLT, CG.PLANK, CG.DOOR, CG.STREET, CG.LANE, CG.WATER
FLOOR = CG.FLOOR

WATCH = {'dwarf': (8, None), 'dwarf_big': (12, None), 'halfling': (2, 'A shirriff'),
         'orc': (3, "A half-orc of the chief's guard")}       # how many keep watch, and what they are called
HOUSES = {'halfling': (0, 1, 1, 0), 'orc': (1, 1, 0, 1)}       # inns, shops, stables, barracks a town has
SIZE = {'dwarf': (240, 140), 'dwarf_big': (300, 160), 'halfling': (164, 104), 'orc': (136, 88)}


def maker_for(s):
    """Which of the peoples' makers builds this place, or None."""
    race = getattr(s, 'race', 'human')
    if race == 'dwarf' and s.is_city and s.kind != 'deephold' and not getattr(s, 'dwarven', False):
        return 'dwarf'
    if race == 'halfling' and s.kind in ('town', 'city', 'metropolis'):
        return 'halfling'
    if race == 'orc' and s.kind in ('town', 'village', 'city'):
        return 'orc'
    return None


def settle_orcs(m, world, start):
    """The half-orcs have towns of their own, far out from the old heartland: the towns of the outer lands that lie
    furthest from the first village, never in the halflings' country or among the dwarves."""
    from .world import scaled
    half = set(getattr(world, 'halfling_land', ()))
    cand = [s for s in world.settlements if s.kind == 'town' and s.id != 0 and s.race == 'human'
            and s.region not in half and not getattr(s, 'harbour', False)]
    cand.sort(key=lambda s: -math.hypot(s.x - start[0], s.y - start[1]))
    for s in cand[:scaled(2)]:
        s.race = 'orc'


def _side_way(ang):
    """A road can not climb the mountain behind a dwarf city: one that would goes out to the side below it."""
    if math.sin(ang) < .3:
        return .25 if math.cos(ang) >= 0 else math.pi - .25
    return ang


def _off_sea(ang):
    """A road of the land does not leave a harbour town across the water: one that would goes out to the side."""
    if math.sin(ang) < -.3:
        return -.25 if math.cos(ang) >= 0 else math.pi + .25
    return ang


# ---------------------------------------------------------------- dwarves
def dwarf_city(c, roads, big=False):
    """Built to a plan: the gate of the hold in the mountain face, and below it terraces cut in half rings round that
    gate like the rows of a theatre. On each terrace one street with a row of alike stone houses, the Great Stair on
    the axis and four lesser stairs, the forge square half way down, a wall with square towers."""
    W, H = c.W, c.H
    ax = W // 2
    top = [26 + 5 * math.sin(x / 23 + 1) + 2.5 * math.sin(x / 9) + abs(x - ax) * .06 for x in range(W)]
    gy = int(top[ax])
    SQ = 1.45
    dd = lambda x, y: ((abs(x - ax) / SQ) ** 4 + abs(y - gy) ** 4) ** .25
    n_rows = 9 if big else 7
    WALLR = 18 + 10 * (n_rows - 1) + 2
    c.cx, c.cy = ax, gy + WALLR // 2
    for y in range(H):
        for x in range(W):
            if y < top[x]:
                c.set(x, y, D.ROCK if y < top[x] - 2 else D.CLIFF)
                c.reserved[y * W + x] = 1
            else:
                c.set(x, y, G if dd(x, y) < WALLR + 1 else (D.GRIT if random.random() < .4 else G))
                if dd(x, y) > WALLR + 3 and random.random() < .025:
                    c.set(x, y, D.TREE)
    # the gate of the hold, carved in the rock with two kings in stone: the hall of the lord of the city
    for y in range(gy - 8, gy + 1):
        for x in range(ax - 9, ax + 10):
            c.set(x, y, FLOOR if abs(x - ax) < 8 and y > gy - 7 else WALLT)
    for x in (ax - 5, ax + 5):
        c.set(x, gy - 4, D.STATUE)
    c.set(ax, gy - 6, D.HIGHSEAT)
    for x in range(ax - 1, ax + 2):
        c.set(x, gy, DOOR)
    c.great.append(('keep', (ax - 9, gy - 8, 19, 9), (ax, gy)))

    def inside(x, y):
        return y >= top[x] and dd(x, y) < WALLR
    c.city_wall(inside, tower_every=1000)
    ring = [(x, y) for y in range(H) for x in range(W) if c.t(x, y) == WALLT and c.inside[y * W + x] and y > gy + 2]
    ring.sort(key=lambda p: math.atan2(p[1] - gy, (p[0] - ax) / SQ))
    for i in range(0, len(ring), 20):                 # square towers on the wall
        x, y = ring[i]
        CG.rect(c, x - 2, y - 2, 5, 5)
    radii = [18 + 10 * k for k in range(n_rows)]
    for y in range(H):
        for x in range(W):
            if not c.inside[y * W + x] or c.t(x, y) == WALLT:
                continue
            d = dd(x, y)
            for r in radii[1:]:
                if abs(d - r) < .55:
                    c.set(x, y, D.LEDGE)
                    c.reserved[y * W + x] = 1
                elif .55 <= d - r < 2.4:
                    c.set(x, y, STREET)
                    c.level[(x, y)] = 1
                    a = math.atan2(y - gy, x - ax)
                    c.dirs[(x, y)] = (-math.sin(a), math.cos(a))
            if d < radii[0] and y > gy:
                c.set(x, y, STREET)                      # the court before the gate
                c.level[(x, y)] = 0
                c.reserved[y * W + x] = 1
    # the stairs: the Great Stair on the axis, four lesser ones, a flight of steps where each climbs a ledge
    for ang, wd in ((math.pi / 2, 5), (math.pi / 2 - .62, 1), (math.pi / 2 + .62, 1), (math.pi / 2 - 1.15, 1),
                    (math.pi / 2 + 1.15, 1)):
        for k in range(0, 2 * WALLR + 6):
            t = k / 2
            x = ax + math.cos(ang) * t * SQ
            y = gy + math.sin(ang) * t
            for o in range(-(wd // 2), wd // 2 + 1):
                xx, yy = int(round(x)) + (o if wd > 1 else 0), int(round(y))
                if not c.ok(xx, yy) or not c.inside[yy * W + xx] or c.t(xx, yy) == WALLT or yy <= gy:
                    continue
                if c.t(xx, yy) == D.LEDGE:
                    c.set(xx, yy, D.STEPS)
                elif c.t(xx, yy) != D.STEPS:
                    c.set(xx, yy, STREET)
                c.level[(xx, yy)] = 0 if wd > 1 else 2
                c.dirs[(xx, yy)] = (math.cos(ang), math.sin(ang))
    # the gate in the wall at the foot of the Great Stair, a tower each side
    gb = max(y for y in range(H) if c.inside[y * W + ax])
    for x in range(ax - 2, ax + 3):
        for y in range(gb - 3, min(H, gb + 3)):
            if c.t(x, y) in (WALLT, G, D.GRIT, D.TREE):
                c.set(x, y, STREET)
                c.level[(x, y)] = 0
    CG.rect(c, ax - 8, gb - 3, 5, 5)
    CG.rect(c, ax + 4, gb - 3, 5, 5)
    for x in range(ax - 3, ax + 4):
        for y in range(gb - 3, gb + 2):
            if c.t(x, y) == WALLT:
                c.set(x, y, STREET)
    gates = [(ax, gb)]
    c.gates = gates
    # the forge square half way down, on the axis: the great forge hall, anvils, the founder in stone
    fr = radii[len(radii) // 2]
    fy = gy + fr + 3
    for y in range(fy - 1, fy + 11):
        for x in range(ax - 16, ax + 17):
            if c.t(x, y) != D.LEDGE:
                c.set(x, y, STREET)
                c.level[(x, y)] = 0
                c.reserved[y * W + x] = 1
    c.set(ax, fy + 6, D.STATUE)
    for x in (ax - 11, ax + 11):
        c.set(x, fy + 8, D.ANVIL)
    hx0 = ax + 18
    CG.rect(c, hx0, fy, 22, 11, floor=FLOOR)           # the great forge hall: the town's smith
    for x in range(hx0 + 3, hx0 + 20, 4):
        c.set(x, fy + 2, D.HEARTH)
    c.set(hx0, fy + 5, DOOR)
    c.houses.append([hx0, fy, hx0 + 21, fy + 10, (hx0, fy + 5)])
    CG.rect(c, ax - 39, fy, 22, 11, floor=FLOOR)       # the guild hall of the smiths
    c.set(ax - 18, fy + 5, DOOR)
    c.houses.append([ax - 39, fy, ax - 18, fy + 10, (ax - 18, fy + 5)])
    c.market = (ax, fy + 4)
    for x in (ax - 13, ax - 8, ax + 8, ax + 13):       # stalls of the forge square
        c.set(x, fy + 2, D.STALL)
        c.stalls.append((x, fy + 2))
    c.rows(lambda x, y, p: (random.choice((6, 7, 8)), 7), passes=2)
    for i in range(W * H):
        x, y = i % W, i // W
        if c.inside[i] and c.t(x, y) in (G, D.TREE, D.WELL):
            c.set(x, y, D.BAREROCK if random.random() < .8 else D.GRIT)
    # the cart line along the lowest terrace, to the mine mouth in the west face
    for (x, y), l in list(c.level.items()):
        if l == 1 and abs(dd(x, y) - radii[-1] - 1.5) < .5 and x < ax - 3 and c.t(x, y) == STREET:
            c.set(x, y, D.RAIL)
    for y in range(gy - 8, gy + 1):
        for x in range(ax - 9, ax + 10):
            c.inside[y * W + x] = 1
    _steps_join(c)
    # the roads out from the gate, along the foot of the mountain
    for ang, other in roads:
        road, out = CG.gate_road(c, ax, gb + 2, _side_way(ang), 400)
        c.street(road, 2, 0)
        c.exits.append((out, other))
    CG.check_inside(c)
    return c.market


def _steps_join(c):
    """Where the end of a terrace lies cut off from the stairs, a flight of steps is cut in its ledge to the next."""
    W = c.W
    for _ in range(40):
        start = c.market
        seen, q = {start}, [start]
        while q:
            x, y = q.pop()
            for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if n not in seen and c.ok(*n) and D.TILES[c.t(*n)].walk:
                    seen.add(n)
                    q.append(n)
        loose = [q for q in c.level if c.t(*q) in (STREET, LANE) and c.inside[q[1] * W + q[0]] and q not in seen]
        if not loose:
            return
        cut = None
        for (x, y) in loose:
            for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                for k in (1, 2):
                    lx, ly = x + dx * k, y + dy * k
                    if not c.ok(lx, ly) or c.t(lx, ly) != D.LEDGE:
                        break
                    far = (lx + dx, ly + dy)
                    if far in seen:
                        cut = [(x + dx * j, y + dy * j) for j in range(1, k + 1)]
                        break
                if cut:
                    break
            if cut:
                break
        if not cut:                                    # what no stair can reach was never paved: bare rock
            for q in loose:
                c.set(*q, D.BAREROCK)
                c.level.pop(q, None)
            return
        for q in cut:
            c.set(*q, D.STEPS)


def _paths_home(c, starts):
    """A footpath from each hill door down to the nearest path that leads to the green."""
    from collections import deque
    start = c.market
    joined, q = {start}, [start]
    while q:
        x, y = q.pop()
        for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if n not in joined and c.ok(*n) and (c.t(*n) in CG.STREETS or n == start):
                joined.add(n)
                q.append(n)
    soft = (G, D.TREE, D.SLOPE, D.FIELD, LANE, STREET)
    for s0 in starts:
        if not c.ok(*s0):
            continue
        prev, dq = {s0: None}, deque([s0])
        end = None
        while dq:
            cur = dq.popleft()
            if cur in joined and cur != s0:
                end = cur
                break
            x, y = cur
            for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if n not in prev and c.ok(*n) and c.inside[n[1] * c.W + n[0]] and c.t(*n) in soft \
                        and (c.t(*n) != D.SLOPE or len(prev) < 60):
                    prev[n] = cur
                    dq.append(n)
        while end is not None:
            if c.t(*end) not in (STREET, LANE):
                c.set(*end, LANE)
                c.level[end] = 2
            joined.add(end)
            end = prev[end]


# ---------------------------------------------------------------- halflings
def halfling_town(c, roads, top=0):
    """Let it ramble: a hedge ring, hills with homes dug into their faces, little houses with gardens on winding paths,
    the green with the party tree, the Keepsake Hall and the inn at its side, an orchard and a pond."""
    W, H = c.W, c.H
    cx, cy = W // 2, top + (H - top) // 2 + 2
    c.cx, c.cy = cx, cy
    inside, edge = CG.blob(cx, cy, W * .43, (H - top) * .4, rough=.1)
    roads = [(_off_sea(a), o) if top and o != 'harbour' else (a, o) for a, o in roads]
    for y in range(H):
        for x in range(W):
            if not inside(x, y) and random.random() < .05:
                c.set(x, y, D.TREE)
            c.inside[y * W + x] = 1 if inside(x, y) else 0
    for y in range(H):                                # the hedge ring, gaps where the paths come in
        for x in range(W):
            if inside(x, y) and not inside(x, y, .965):
                c.set(x, y, D.HEDGE)
                c.reserved[y * W + x] = 1
    gin, gedge = CG.blob(cx, cy, 13, 8, rough=.15)    # the green, with the party tree and lanterns round it
    for y in range(H):
        for x in range(W):
            if gin(x, y):
                c.set(x, y, G)
                c.reserved[y * W + x] = 1
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            c.set(cx + dx, cy + dy, D.TREE)
    for k in range(10):
        a = k * math.pi / 5
        c.set(int(cx + math.cos(a) * 6), int(cy + math.sin(a) * 3.5), D.LAMP)
    for (bx, by, bw, bh, k) in ((cx - 9, cy - 18, 19, 7, 'keepsake'), (cx + 17, cy - 4, 12, 8, 'inn')):
        CG.rect(c, bx, by, bw, bh, floor=PLANK)
        door = (bx + bw // 2, by + bh - 1) if k == 'keepsake' else (bx, by + bh // 2)
        c.set(*door, DOOR)
        c.great.append((k, (bx, by, bw, bh), door))
        CG.reserve(c, bx - 1, by - 1, bw + 2, bh + 2)
    c.market = (cx, cy + 5)
    for x in range(cx - 8, cx + 9, 4):                 # the market on the green: a few stalls on its south side
        if x != cx:
            c.set(x, cy + 6, D.STALL)
            c.stalls.append((x, cy + 6))
    # paths: from each road's gap in the hedge to the green, wandering, and a ring path round the green
    ways = [a for a, _ in roads] or [math.pi / 2]
    while len(ways) < 3:
        ways.append(ways[-1] + 2.1)
    for k, ang in enumerate(ways):
        gx, gy = edge(ang)
        sx, sy = gedge(ang, 1.05)
        pts = CG.wobbly((sx, sy), (gx, gy), 4.5, 6)
        c.street(pts, 1, 0)
        for x, y in [(int(round(px)), int(round(py))) for px, py in pts[-6:]]:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if c.ok(x + dx, y + dy) and c.t(x + dx, y + dy) == D.HEDGE:
                        c.set(x + dx, y + dy, LANE)
        if k < len(roads):
            road, out = CG.gate_road(c, gx, gy, ang, 400)
            c.street(road, 1, 0)
            c.exits.append((out, roads[k][1]))
            c.gates.append((int(gx), int(gy)))
    c.street([gedge(i * .1, 1.08) for i in range(64)], 1, 1)
    # hills, each with homes dug into its south face, the round door on a path
    hills = []
    for _ in range(300):
        if len(hills) >= 4:
            break
        hx, hy = random.randint(cx - 55, cx + 55), random.randint(cy - 32, cy + 26)
        rx, ry = random.randint(11, 15), random.randint(5, 7)
        if math.hypot(hx - cx, (hy - cy) * 1.6) < 30 or any(abs(hx - a) < rx + b + 6 and abs(hy - bb) < ry + e + 5
                                                            for a, bb, b, e in hills):
            continue
        cells = [(x, y) for y in range(hy - ry, hy + ry + 1) for x in range(hx - rx, hx + rx + 1)
                 if ((x - hx) / rx) ** 2 + ((y - hy) / ry) ** 2 < 1]
        if any(not c.ok(x, y) or not inside(x, y, .9) or c.t(x, y) != G or c.reserved[y * W + x] for x, y in cells):
            continue
        hills.append((hx, hy, rx, ry))
        cs = set(cells)
        for x, y in cells:
            c.set(x, y, D.SLOPE)
            c.reserved[y * W + x] = 1
        for sx in range(hx - rx + 5, hx + rx - 4, 8):
            rim = max(y for x, y in cells if x == sx)
            hall = rim - 2
            for xx in range(sx - 3, sx + 4):
                for yy in range(hall - 3, hall + 2):
                    if (xx, yy) in cs:
                        c.set(xx, yy, D.EARTH)
            for xx in range(sx - 2, sx + 3):
                c.set(xx, hall, PLANK)
                c.set(xx, hall - 2, PLANK)
            c.set(sx, hall - 1, PLANK)
            c.set(sx - 2, hall - 2, D.BED)
            c.set(sx + 2, hall, D.TABLE)
            c.set(sx, hall + 1, DOOR)
            for wx in (sx - 2, sx + 2):
                c.set(wx, hall + 1, D.WINDOW)
            c.set(sx, hall + 2, LANE)
            c.level[(sx, hall + 2)] = 2
            c.houses.append([sx - 3, hall - 3, sx + 3, hall + 1, (sx, hall + 1)])
            c.street(CG.wobbly((sx, hall + 2), (cx + (sx - cx) * .4, cy + (hall - cy) * .4), 2, 5), 1, 2)
    _paths_home(c, [(h[4][0], h[4][1] + 1) for h in c.houses if h[4]])
    c.rows(lambda x, y, p: (random.randint(5, 6), random.randint(5, 6)), passes=1)
    for i in range(W * H):                             # vegetable patches by the houses
        x, y = i % W, i // W
        if c.inside[i] and not c.reserved[i] and c.t(x, y) == G:
            near = any((x + dx, y + dy) in c.housewall for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2))
            if near and random.random() < .5:
                c.set(x, y, D.FIELD)
    for _ in range(3):                                 # orchards
        for _ in range(200):
            ox, oy = random.randint(cx - 60, cx + 60), random.randint(cy - 35, cy + 30)
            box = [(ox + i * 2, oy + j * 2) for i in range(6) for j in range(3)]
            if all(c.ok(x, y) and inside(x, y, .9) and c.t(x, y) in (G, D.FIELD) and not c.reserved[y * W + x]
                   for x, y in box):
                for x, y in box:
                    c.set(x, y, D.TREE)
                break
    for _ in range(200):                               # the pond
        px, py = random.randint(cx - 50, cx + 50), random.randint(cy - 30, cy + 30)
        cells = [(x, y) for y in range(py - 3, py + 4) for x in range(px - 6, px + 7)
                 if ((x - px) / 6) ** 2 + ((y - py) / 3) ** 2 < 1]
        if all(c.ok(x, y) and c.t(x, y) in (G, D.FIELD, D.TREE) and not c.reserved[y * W + x] and
               not any(c.is_street(x + a, y + b) for a in (-1, 0, 1) for b in (-1, 0, 1)) for x, y in cells):
            for x, y in cells:
                c.set(x, y, WATER)
                c.reserved[y * W + x] = 1
            break
    CG.fields(c, 30)
    CG.check_inside(c)
    return c.market


# ---------------------------------------------------------------- half-orcs
def orc_town(c, roads, top=0):
    """Rings of huts round the chief's longhouse and the fighting pit, a palisade with stakes before it, mud paths,
    pens, drying racks, the smith's open forge."""
    W, H = c.W, c.H
    cx, cy = W // 2, top + (H - top) // 2
    c.cx, c.cy = cx, cy
    roads = [(_off_sea(a), o) if top and o != 'harbour' else (a, o) for a, o in roads]
    for y in range(H):
        for x in range(W):
            r = random.random()
            c.set(x, y, D.GRIT if r < .35 else G)
            if r > .985:
                c.set(x, y, D.BRAMBLE)
    inside, edge = CG.blob(cx, cy, W * .43, (H - top) * .42, rough=.1)
    for y in range(H):
        for x in range(W):
            c.inside[y * W + x] = 1 if inside(x, y) else 0
            if inside(x, y) and not inside(x, y, .97):
                c.set(x, y, D.PALISADE)
                c.reserved[y * W + x] = 1
            elif not inside(x, y) and inside(x, y, 1.03) and (x + y) % 2 == 0:
                c.set(x, y, D.STAKES)
    lx, ly = cx - 15, cy - 15                         # the chief's longhouse, north of the middle
    for y in range(ly, ly + 9):
        for x in range(lx, lx + 31):
            c.set(x, y, D.HIDE if y in (ly, ly + 8) or x in (lx, lx + 30) else FLOOR)
            c.reserved[y * W + x] = 1
    for x in range(lx + 4, lx + 27, 6):
        c.set(x, ly + 4, D.FIREPIT)
    c.set(lx + 28, ly + 4, D.HIGHSEAT)
    c.set(lx + 15, ly + 8, DOOR)
    c.set(lx + 15, ly + 1, D.TOTEM)
    c.great.append(('keep', (lx, ly, 31, 9), (lx + 15, ly + 8)))
    for y in range(ly + 9, cy - 1):                    # the way from his door to the pit
        for x in (lx + 14, lx + 15, lx + 16):
            c.set(x, y, STREET)
            c.level[(x, y)] = 0
    for y in range(cy - 2, cy + 11):                   # the fighting pit: sand inside a ring of stakes
        for x in range(cx - 10, cx + 11):
            r = ((x - cx) / 9.5) ** 2 + ((y - cy - 4) / 5.8) ** 2
            if r < 1:
                c.set(x, y, D.STAKES if r > .78 else D.SAND)
                c.reserved[y * W + x] = 1
    for x in (cx - 1, cx, cx + 1):                     # a way in through the stakes from the north
        for y in range(cy - 2, cy + 1):
            c.set(x, y, D.SAND)
    for a in (-2.4, -.7, 1.0, 2.2):
        c.set(int(cx + math.cos(a) * 12), int(cy + 4 + math.sin(a) * 8), D.TOTEM)
    rings = [(W * .16, (H - top) * .17), (W * .27, (H - top) * .27), (W * .37, (H - top) * .36)]
    for rx, ry in rings:                               # mud paths: rings round the middle, spokes out to the gates
        pts = [(cx + math.cos(i * .08) * rx * (1 + .06 * math.sin(i * .3)), cy + math.sin(i * .08) * ry)
               for i in range(80)]
        c.street(pts + pts[:1], 1, 1)
    ways = [a for a, _ in roads] or [math.pi / 2]
    while len(ways) < 3:
        ways.append(ways[-1] + 2.1)
    for k, ang in enumerate(ways):
        gx, gy = edge(ang)
        c.street(CG.wobbly((cx + math.cos(ang) * 12, cy + math.sin(ang) * 9), (gx, gy), 2.5, 6), 2, 0)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                xx, yy = int(gx) + dx, int(gy) + dy
                if c.ok(xx, yy) and c.t(xx, yy) in (D.PALISADE, D.STAKES):
                    c.set(xx, yy, STREET)
        for d in (-2, 2):                              # a watch platform each side of the gate
            tx = int(gx + (d if abs(math.cos(ang)) < .5 else 0))
            ty = int(gy + (d if abs(math.cos(ang)) >= .5 else 0))
            for dx in (0, 1):
                for dy in (0, 1):
                    if c.ok(tx + dx, ty + dy) and inside(tx + dx, ty + dy) and not c.is_street(tx + dx, ty + dy):
                        c.set(tx + dx, ty + dy, D.PALISADE)
        if k < len(roads):
            road, out = CG.gate_road(c, gx, gy, ang, 400)
            for x, y in c.densify(road)[:3]:           # through the stakes
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        q = (int(round(x)) + dx, int(round(y)) + dy)
                        if c.ok(*q) and c.t(*q) == D.STAKES:
                            c.set(*q, G)
            c.street(road, 1, 0)
            c.exits.append((out, roads[k][1]))
            c.gates.append((int(gx), int(gy)))
    c.market = (cx, cy - 4)
    for x in (cx - 9, cx - 5, cx + 5, cx + 9):         # trade at the pit's edge
        if c.t(x, cy - 4) in (G, D.GRIT):
            c.set(x, cy - 4, D.STALL)
            c.stalls.append((x, cy - 4))
    for x in range(cx - 12, cx + 13):
        for y in (cy - 3, cy - 5):
            if c.t(x, y) in (G, D.GRIT):
                c.set(x, y, STREET)
                c.level[(x, y)] = 1
    for x in range(cx - 12, cx + 13):
        if c.t(x, cy - 4) in (G, D.GRIT):
            c.set(x, cy - 4, STREET)
            c.level[(x, cy - 4)] = 1

    def longhouse(w, h):
        """A long hall of hide and timber by a ring path: the mead hall, the trader's, the shrine."""
        for _ in range(400):
            rx, ry = random.choice(rings[:2])
            a = random.uniform(0, 6.3)
            x0, y0 = int(cx + math.cos(a) * (rx + 5)), int(cy + math.sin(a) * (ry + 4))
            cells = [(x, y) for y in range(y0 - 1, y0 + h + 1) for x in range(x0 - 1, x0 + w + 1)]
            if any(not c.ok(*q) or not inside(*q) or c.reserved[q[1] * W + q[0]] or c.t(*q) not in (G, D.GRIT, D.BRAMBLE)
                   for q in cells):
                continue
            CG.rect(c, x0, y0, w, h, wall=D.HIDE, floor=FLOOR)
            door = min(((x, y) for x in range(x0 + 1, x0 + w - 1) for y in (y0, y0 + h - 1)),
                       key=lambda q: math.hypot(q[0] - cx, q[1] - cy))
            c.set(*door, DOOR)
            out = (door[0], door[1] + (1 if door[1] == y0 + h - 1 else -1))
            c.street_join([out, (out[0] + (cx - out[0]) * .3, out[1] + (cy - out[1]) * .3)], 1, 2)
            c.houses.append([x0, y0, x0 + w - 1, y0 + h - 1, door])
            return True
        return False
    for w, h in ((12, 7), (10, 6), (10, 6), (9, 6)):
        longhouse(w, h)

    def hut(hx, hy, r):
        cells = [(x, y) for y in range(hy - r, hy + r + 1) for x in range(hx - r - 1, hx + r + 2)
                 if ((x - hx) / (r + .9)) ** 2 + ((y - hy) / (r + .4)) ** 2 < 1]
        if any(not c.ok(x, y) or not inside(x, y, .93) or c.reserved[y * W + x] or c.t(x, y) not in (G, D.GRIT)
               for x, y in cells):
            return False
        cs = set(cells)
        for x, y in cells:
            ring_ = any((x + dx, y + dy) not in cs for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            c.set(x, y, D.HIDE if ring_ else FLOOR)
            c.reserved[y * W + x] = 1
        c.set(hx, hy, D.FURS)
        best = None                                    # the door: the ring cell nearest a path
        for x, y in cells:
            if c.t(x, y) != D.HIDE:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if (x - dx, y - dy) in cs and c.t(x - dx, y - dy) != D.HIDE:
                    for k in range(1, 6):
                        if c.is_street(x + dx * k, y + dy * k):
                            if best is None or k < best[0]:
                                best = (k, x, y, dx, dy)
                            break
        if not best:
            for x, y in cells:
                c.set(x, y, G)
                c.reserved[y * W + x] = 0
            return False
        k, x, y, dx, dy = best
        c.set(x, y, DOOR)
        for j in range(1, k):
            c.set(x + dx * j, y + dy * j, LANE)
            c.level[(x + dx * j, y + dy * j)] = 2
        xs, ys = [q[0] for q in cells], [q[1] for q in cells]
        c.houses.append([min(xs), min(ys), max(xs), max(ys), (x, y)])
        return True
    for (rx, ry) in rings:
        for i in range(90):
            a = i * 2 * math.pi / 90 + random.uniform(-.02, .02)
            for side in (-4, 4):
                hut(int(cx + math.cos(a) * (rx + side * 1.3)), int(cy + math.sin(a) * (ry + side)), random.choice((2, 2, 3)))
    for i in range(W * H):
        x, y = i % W, i // W
        if c.inside[i] and not c.reserved[i] and c.t(x, y) in (G, D.GRIT) and not any(
                c.is_street(x + a, y + b) for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            r = random.random()
            if r < .012:
                c.set(x, y, D.FIREPIT)
            elif r < .02:
                c.set(x, y, D.RACK)
            elif r < .024:
                c.set(x, y, D.MIDDEN)
    for _ in range(2):                                 # pens with beasts
        for _ in range(200):
            px, py = random.randint(8, W - 18), random.randint(8, H - 14)
            box = [(x, y) for y in range(py, py + 6) for x in range(px, px + 10)]
            if all(inside(*q) and not c.reserved[q[1] * W + q[0]] and c.t(*q) in (G, D.GRIT) and not
                   any(c.is_street(q[0] + a, q[1] + b) for a in (-1, 0, 1) for b in (-1, 0, 1)) for q in box):
                for x, y in box:
                    c.set(x, y, D.FENCE if y in (py, py + 5) or x in (px, px + 9) else G)
                    c.reserved[y * W + x] = 1
                break
    sx, sy = cx + 22, cy + 8                           # the smith's open forge
    if all(c.ok(x, y) and c.t(x, y) in (G, D.GRIT) for y in range(sy, sy + 4) for x in range(sx, sx + 7)):
        c.set(sx + 2, sy + 1, D.ANVIL)
        c.set(sx + 4, sy + 1, D.FIREPIT)
        c.set(sx + 3, sy + 2, D.RACK)
    CG.check_inside(c)
    return c.market


# ---------------------------------------------------------------- bridges on the open land
STYLE_TILES = {          # people: (deck, parapet, what stands at each end)
    'human': (D.SDECK, D.BPARAPET, None),
    'trestle': (D.TRESTLE, None, None),
    'dwarf': (D.GDECK, D.GPARAPET, D.BRAZIER),
    'elf': (D.ROOTDECK, D.LEAFRAIL, D.GLOWMOSS),
    'halfling': (D.SDECK, D.FLOWERBOX, None),
    'gnome': (D.COPPERDECK, D.BPARAPET, None),
    'tribe': (D.LOGDECK, None, D.STAKES),
    'lizard': (D.RWALK, None, None),
}
TRIBES = {'warcamp': 'tribe', 'ravine': 'tribe', 'kobolds': 'tribe', 'gnolls': 'tribe', 'stilts': 'lizard'}


def people_at(game, cx, cy):
    """Whose land a world cell is, for the look of its bridges: the nearest people's place within reach."""
    w = game.world
    if cx is None:
        return 'human'
    from .world import WORLD_W, WORLD_H
    reg = w.region_at(cx, cy).id if 0 <= cx < WORLD_W and 0 <= cy < WORLD_H else None
    best, bd = 'human', 14
    for s in w.settlements:
        d = max(abs(s.x - cx), abs(s.y - cy))
        if d < bd:
            race = getattr(s, 'race', 'human')
            best, bd = (race if race in ('dwarf', 'elf', 'halfling', 'gnome') else
                        'tribe' if race in ('orc', 'goblin') else 'human'), d
    for st in w.sites:
        d = max(abs(st.x - cx), abs(st.y - cy))
        if d < bd and (st.kind in TRIBES or st.kind in ('glade', 'gnomes')):
            best, bd = TRIBES.get(st.kind, 'elf' if st.kind == 'glade' else 'gnome'), d
    for h in getattr(w, 'holds', ()):
        if max(abs(h.x - cx), abs(h.y - cy)) < min(bd, 10):
            best, bd = 'dwarf', max(abs(h.x - cx), abs(h.y - cy))
    if best == 'human' and reg is not None and reg in getattr(w, 'halfling_land', ()):
        best = 'halfling'
    return best


def _h(x, y, s):
    return ((x * 73856093) ^ (y * 19349663) ^ (s * 83492791)) % 1000 / 1000


def dress_bridges(game, t, wet, before, ox, oy, zw, zh, salt):
    """The bridges where the roads of a land map cross water: each run laid straight (or at 45 degrees) from bank to
    bank, the road taking it up in line at both ends, in the style of the people whose land it is. t: the tiles
    (numpy, BRIDGE on the old crossings); wet: water before the road; before: the tiles under the road."""
    H, W = t.shape
    seen = np.zeros((H, W), dtype=bool)
    ys, xs = np.nonzero(t == D.BRIDGE)
    walk = lambda x, y: 0 <= x < W and 0 <= y < H and not wet[y, x]
    for y0, x0 in zip(ys.tolist(), xs.tolist()):
        if seen[y0, x0]:
            continue
        run, q = [], [(x0, y0)]
        seen[y0, x0] = True
        while q:
            x, y = q.pop()
            run.append((x, y))
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W and 0 <= ny < H and not seen[ny, nx] and t[ny, nx] == D.BRIDGE:
                        seen[ny, nx] = True
                        q.append((nx, ny))
        ends = []                                      # the road cells on dry land by the run
        for x, y in run:
            for dx in (-2, -1, 0, 1, 2):
                for dy in (-2, -1, 0, 1, 2):
                    nx, ny = x + dx, y + dy
                    if walk(nx, ny) and t[ny, nx] == D.ROAD and (nx, ny) not in ends:
                        ends.append((nx, ny))
        wx, wy = (ox + run[0][0]) // zw, (oy + run[0][1]) // zh
        if len(ends) < 2:                              # it runs on out of sight: the old crossing, in its people's wood
            for x, y in run:                           # or stone
                t[y, x] = STYLE_TILES[people_at(game, wx, wy)][0]
            continue
        a, b = max(((p, q) for p in ends for q in ends), key=lambda pq: math.hypot(pq[0][0] - pq[1][0], pq[0][1] - pq[1][1]))
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        k = round(ang / (math.pi / 4)) % 8
        d = ((1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1))[k]
        deck, x, y = [], a[0] + d[0], a[1] + d[1]
        for _ in range(3):                             # from the bank to the water's edge
            if not walk(x, y):
                break
            t[y, x] = D.ROAD
            x, y = x + d[0], y + d[1]
        a = (x - d[0], y - d[1])
        while 0 <= x < W and 0 <= y < H and wet[y, x] and len(deck) < 40:
            deck.append((x, y))
            x, y = x + d[0], y + d[1]
        if not deck or not walk(x, y):
            for x, y in run:
                t[y, x] = STYLE_TILES[people_at(game, wx, wy)][0]
            continue
        land = (x, y)
        wx, wy = (ox + deck[len(deck) // 2][0]) // zw, (oy + deck[len(deck) // 2][1]) // zh
        style = people_at(game, wx, wy)
        r = _h(wx, wy, salt)
        if style == 'human' and r < .3:
            style = 'trestle'
        fallen = style == 'human' and .3 <= r < .4 and len(deck) >= 4
        dk, par, end = STYLE_TILES[style]
        for x, y in run:                               # the old crossing goes back to water
            t[y, x] = before[y, x]
        for i, (x, y) in enumerate(deck):
            if fallen and len(deck) // 2 - 1 <= i <= len(deck) // 2:
                continue                               # an old bridge with a span fallen in: wade at the ford
            t[y, x] = dk
            if par:
                for sx, sy in ((-d[1], d[0]), (d[1], -d[0])):
                    px, py = x + sx, y + sy
                    if 0 <= px < W and 0 <= py < H and wet[py, px] and t[py, px] != dk:
                        t[py, px] = par
        # the road takes the bridge up in line on the far side, then bends back to its own course
        x, y = land
        tx, ty = b
        for _ in range(60):
            if (x, y) == (tx, ty) or not walk(x, y):
                break
            if t[y, x] not in (D.ROAD,):
                t[y, x] = D.ROAD
            x += int(tx > x) - int(tx < x)
            y += int(ty > y) - int(ty < y)
        if end is not None:                            # braziers, lanterns or stakes beside both ends
            for (ex, ey) in (a, land):
                for sx, sy in ((-d[1], d[0]), (d[1], -d[0])):
                    px, py = ex + sx, ey + sy
                    if walk(px, py) and t[py, px] in (D.GRASS, D.SLOPE, D.FIELD, D.PATH, D.TREE):
                        t[py, px] = end
