"""The open world: regions, settlements, roads, dungeons and the people living in towns."""
import heapq
import math
import random

from . import data as D
from .data import (WALL, FLOOR, DOOR, WATER, GRASS, FOREST, MOUNTAIN, SWAMP, TOWN, ENTR, TREE, PATH, WELL, ROAD,
                   HILLS, SAND, CITY)
from .entities import GameMap, make_npc
from .worldgen import D8, cheb, bfs, noise_grid, rand_free

WORLD_W, WORLD_H = 160, 90
NPC_NAMES = ['Dorien', 'Ilse', 'Berend', 'Maud', 'Aldric', 'Petra', 'Hob', 'Wenna', 'Garrick', 'Tamsin', 'Osric', 'Lyra',
             'Bram', 'Edda', 'Corwin', 'Nell', 'Fenwick', 'Rowan', 'Sabine', 'Tobin', 'Agnes', 'Merrit', 'Jory', 'Hilde']


class Region:
    def __init__(self, rid, cx, cy):
        self.id, self.cx, self.cy = rid, cx, cy
        self.biome = 'grass'
        self.name = ''
        self.danger = 1


class Settlement:
    def __init__(self, sid, name, kind, x, y):
        self.id, self.name, self.kind, self.x, self.y = sid, name, kind, x, y
        self.region = 0
        self.biome = 'grass'
        self.produce, self.demand = [], []
        self.market = {}          # good -> [stock, target, normal_target]
        self.event = None         # (event key, days left)
        self.board = []           # mission offers
        self.board_day = -99
        self.rep = 0
        self.services = set()

    @property
    def map_key(self):
        return f'town:{self.id}'

    @property
    def is_city(self):
        return self.kind == 'city'


class Dungeon:
    def __init__(self, did, name, depth, base, style, tag, boss, wall, x, y, main):
        self.id, self.name, self.depth, self.base, self.style, self.tag = did, name, depth, base, style, tag
        self.boss, self.wall, self.x, self.y, self.main = boss, wall, x, y, main
        self.relic = None         # mission id of a fetch quest hidden at the bottom


class World:
    """Everything about the overworld that is not a GameMap."""

    def __init__(self):
        self.regions = []
        self.region_of = None     # bytearray, region id per overworld cell
        self.settlements = []
        self.dungeons = {}
        self.paths = {}           # (sid_a, sid_b) -> list of (x, y)
        self.wanderers = []
        self.start = 0

    def region_at(self, x, y):
        return self.regions[self.region_of[y * WORLD_W + x]]

    def settlement_at(self, x, y):
        for s in self.settlements:
            if s.x == x and s.y == y:
                return s
        return None

    def dungeon_at(self, x, y):
        for d in self.dungeons.values():
            if d.x == x and d.y == y:
                return d
        return None


# ------------------------------------------------------------------ generation
def _road_cost(t):
    if t == ROAD:
        return 1
    if t in (GRASS, SAND, TOWN, CITY, ENTR):
        return 3
    if t in (FOREST, HILLS):
        return 6
    if t == SWAMP:
        return 8
    return None


def dijkstra_path(m, a, b, cost_fn=_road_cost):
    """Cheapest 8-way path from a to b on the overworld, as a list of cells after a."""
    w = m.w
    INF = 1 << 30
    dist = [INF] * (m.w * m.h)
    prev = [-1] * (m.w * m.h)
    s, goal = a[1] * w + a[0], b[1] * w + b[0]
    dist[s] = 0
    pq = [(0, s)]
    t = m.t
    while pq:
        d, c = heapq.heappop(pq)
        if c == goal:
            break
        if d > dist[c]:
            continue
        x, y = c % w, c // w
        for dx, dy in D8:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < m.h:
                ni = ny * w + nx
                cc = cost_fn(t[ni])
                if cc is None:
                    continue
                nd = d + cc + (1 if dx and dy else 0)
                if nd < dist[ni]:
                    dist[ni] = nd
                    prev[ni] = c
                    heapq.heappush(pq, (nd, ni))
    if dist[goal] >= INF:
        return None
    out = []
    c = goal
    while c != s:
        out.append((c % w, c // w))
        c = prev[c]
    out.reverse()
    return out


def gen_world(game):
    w, h = WORLD_W, WORLD_H
    for _attempt in range(40):
        m = GameMap('over', 'over', 'The Wilds', w, h, GRASS)
        m.radius = 10
        n1, n2, n3 = noise_grid(w, h, 16), noise_grid(w, h, 7), noise_grid(w, h, 3)
        m1, m2 = noise_grid(w, h, 14), noise_grid(w, h, 6)
        H, Mo = [], []
        for y in range(h):
            for x in range(w):
                e = max(abs(x / (w - 1) - .5), abs(y / (h - 1) - .5)) * 2
                H.append(.55 * n1(x, y) + .3 * n2(x, y) + .15 * n3(x, y) - e ** 3 * .45)
                Mo.append(.65 * m1(x, y) + .35 * m2(x, y))
        sH, sM = sorted(H), sorted(Mo)
        qh = lambda p: sH[int(p * (len(sH) - 1))]
        qm = lambda p: sM[int(p * (len(sM) - 1))]
        water, low, hills, mount = qh(.17), qh(.27), qh(.84), qh(.92)
        forest, wet = qm(.6), qm(.55)
        for i in range(w * h):
            x, y, hv, mo = i % w, i // w, H[i], Mo[i]
            if x in (0, w - 1) or y in (0, h - 1) or hv < water:
                t = WATER
            elif hv > mount:
                t = MOUNTAIN
            elif hv > hills:
                t = HILLS
            elif hv < low and mo > wet:
                t = SWAMP
            elif mo > forest:
                t = FOREST
            else:
                t = GRASS
            m.t[i] = t
        # beaches
        for i in range(w * h):
            if m.t[i] in (GRASS, FOREST):
                x, y = i % w, i // w
                if any(m.inb(x + dx, y + dy) and m.t[(y + dy) * w + x + dx] == WATER for dx, dy in D8) and random.random() < .7:
                    m.t[i] = SAND
        # start: walkable grass near the middle with a large reachable area
        cands = sorted((i for i in range(w * h) if m.t[i] == GRASS), key=lambda i: math.hypot(i % w - w / 2, i // w - h / 2))
        start = None
        for i in cands[:400:20]:
            dist = bfs(m, i % w, i // w, lambda t: D.TILES[t].walk)
            if sum(1 for d in dist if d > 0) > w * h * .45:
                start = (i % w, i // w)
                break
        if not start:
            continue
        world = World()
        reach = [i for i in range(w * h) if dist[i] > 0]
        reach_set = set(reach)
        _make_regions(m, world, reach, start)
        if not _place_settlements(game, m, world, reach_set, dist, start):
            continue
        _build_roads(m, world)
        _place_dungeons(m, world, reach, dist, start)
        for s in world.settlements:
            m.set(s.x, s.y, CITY if s.is_city else TOWN)
        for d in world.dungeons.values():
            m.set(d.x, d.y, ENTR)
        return m, world
    raise RuntimeError('World generation failed')


def _make_regions(m, world, reach, start):
    w = m.w
    centers = [start]
    pool = reach[:]
    random.shuffle(pool)
    for i in pool:
        if len(centers) >= 11:
            break
        x, y = i % w, i // w
        if all(math.hypot(x - cx, y - cy) > 24 for cx, cy in centers):
            centers.append((x, y))
    world.regions = [Region(i, cx, cy) for i, (cx, cy) in enumerate(centers)]
    rof = bytearray(m.w * m.h)
    counts = [dict() for _ in centers]
    for i in range(m.w * m.h):
        x, y = i % w, i // w
        best = min(range(len(centers)), key=lambda r: (x - centers[r][0]) ** 2 + (y - centers[r][1]) ** 2)
        rof[i] = best
        t = m.t[i]
        b = {GRASS: 'grass', FOREST: 'forest', SWAMP: 'swamp', HILLS: 'hills', MOUNTAIN: 'hills', SAND: 'coast'}.get(t)
        if b:
            counts[best][b] = counts[best].get(b, 0) + (3 if b == 'coast' else 1)
    world.region_of = rof
    used = set()
    for r in world.regions:
        c = counts[r.id]
        r.biome = max(c, key=c.get) if c else 'grass'
        names = [n for n in D.BIOME_NAMES[r.biome] if n not in used] or D.BIOME_NAMES[r.biome]
        r.name = random.choice(names)
        used.add(r.name)
        r.danger = 1 if r.id == 0 else max(1, min(10, 1 + round(math.hypot(r.cx - start[0], r.cy - start[1]) / 11)))
    world.regions[0].name = 'The Vale of Thorns'
    world.regions[0].biome = 'grass'


def _settlement_biome(m, world, x, y):
    if any(m.inb(x + dx, y + dy) and m.tile(x + dx, y + dy) == WATER for dx in range(-3, 4) for dy in range(-3, 4)):
        return 'coast'
    t = m.tile(x, y)
    return {FOREST: 'forest', SWAMP: 'swamp', HILLS: 'hills', SAND: 'coast'}.get(t, world.region_at(x, y).biome)


def _place_settlements(game, m, world, reach_set, dist, start):
    w = m.w
    taken = [start]
    names = set(['Thornfield'])

    def far_enough(x, y, d):
        return all(cheb(x, y, a, b) >= d for a, b in taken)

    ok_tiles = (GRASS, SAND, FOREST, HILLS)
    cells = [i for i in reach_set if m.t[i] in ok_tiles and 4 <= i % w < w - 4 and 4 <= i // w < m.h - 4]
    random.shuffle(cells)
    sett = [Settlement(0, 'Thornfield', 'village', start[0], start[1])]
    # cities: far from the start and from each other, one of them on the coast if possible
    cities = []
    for want_coast in (True, False, False):
        for i in cells:
            x, y = i % w, i // w
            if dist[i] < 25 or not far_enough(x, y, 34):
                continue
            near_water = any(m.inb(x + dx, y + dy) and m.tile(x + dx, y + dy) == WATER for dx in range(-2, 3) for dy in range(-2, 3))
            if want_coast and not near_water:
                continue
            cities.append((x, y))
            taken.append((x, y))
            break
    if len(cities) < 3:
        return False
    city_names = random.sample(D.CITY_NAMES, 3)
    for (x, y), nm in zip(cities, city_names):
        sett.append(Settlement(len(sett), nm, 'city', x, y))
    # villages: spread over regions
    for i in cells:
        if len(sett) >= 13:
            break
        x, y = i % w, i // w
        if not far_enough(x, y, 13):
            continue
        nm = None
        for _ in range(30):
            cand = random.choice(D.TOWN_A) + random.choice(D.TOWN_B)
            if cand not in names:
                nm = cand
                break
        names.add(nm)
        taken.append((x, y))
        sett.append(Settlement(len(sett), nm, 'village', x, y))
    if len(sett) < 11:
        return False
    for s in sett:
        s.region = world.region_of[s.y * w + s.x]
        s.biome = _settlement_biome(m, world, s.x, s.y)
    world.settlements = sett
    return True


def _build_roads(m, world):
    ss = world.settlements
    n = len(ss)
    d = lambda a, b: math.hypot(ss[a].x - ss[b].x, ss[a].y - ss[b].y)
    in_tree, edges = {0}, []
    while len(in_tree) < n:
        a, b = min(((a, b) for a in in_tree for b in range(n) if b not in in_tree), key=lambda e: d(*e))
        edges.append((a, b))
        in_tree.add(b)
    extra = sorted(((a, b) for a in range(n) for b in range(a + 1, n) if (a, b) not in edges and (b, a) not in edges), key=lambda e: d(*e))
    edges += extra[:4]
    for a, b in edges:
        p = dijkstra_path(m, (ss[a].x, ss[a].y), (ss[b].x, ss[b].y))
        if not p:
            continue
        for x, y in p:
            if m.tile(x, y) in (GRASS, SAND, FOREST, HILLS, SWAMP):
                m.set(x, y, ROAD)


def _place_dungeons(m, world, reach, dist, start):
    w = m.w
    used = set()
    blocked = {(s.x, s.y) for s in world.settlements}

    def ok(i):
        x, y = i % w, i // w
        return (x, y) not in blocked and m.t[i] not in (ROAD, WATER, MOUNTAIN) and all(cheb(x, y, s.x, s.y) >= 5 for s in world.settlements) \
            and all(cheb(x, y, o[0], o[1]) >= 8 for o in used)

    def choose(lst, fb):
        lst = [i for i in lst if ok(i)]
        i = random.choice(lst) if lst else fb
        used.add((i % w, i // w))
        return i % w, i // w

    near_mount = lambda i: any(m.inb(i % w + dx, i // w + dy) and m.tile(i % w + dx, i // w + dy) in (MOUNTAIN, HILLS) for dx, dy in D8)
    rat = choose([i for i in reach if 7 <= dist[i] <= 14], reach[len(reach) // 10])
    mine = choose([i for i in reach if 16 <= dist[i] <= 32 and near_mount(i)] or [i for i in reach if 16 <= dist[i] <= 32], reach[len(reach) // 4])
    crypt = choose([i for i in reach if 26 <= dist[i] <= 45 and m.t[i] in (SWAMP, FOREST)] or [i for i in reach if 26 <= dist[i] <= 45], reach[len(reach) // 3])
    for did, (x, y) in (('rat', rat), ('mine', mine), ('crypt', crypt)):
        t = D.DUNGEONS[did]
        world.dungeons[did] = Dungeon(did, t['name'], t['depth'], t['base'], t['style'], t['tag'], t['boss'], t['wall'], x, y, True)
    sides = D.SIDE_DUNGEONS[:]
    random.shuffle(sides)
    pool = reach[:]
    random.shuffle(pool)
    k = 0
    for i in pool:
        if k >= 6:
            break
        if not ok(i) or dist[i] < 12:
            continue
        x, y = i % w, i // w
        used.add((x, y))
        name, style, tag = sides[k]
        danger = world.region_at(x, y).danger
        did = f'side{k}'
        wall = {'crypt': D.hexrgb('#7e869c'), 'dungeon': D.hexrgb('#a0835e')}.get(tag)
        world.dungeons[did] = Dungeon(did, name, random.randint(2, 3), max(0, danger * 2 - 2), style, tag, None, wall, x, y, False)
        k += 1


# ------------------------------------------------------------------ settlement maps
def settlement_services(s):
    if s.id == 0:
        return {'inn', 'market', 'shop', 'temple', 'stables'}
    sv = {'inn', 'market'}
    if s.is_city:
        sv |= {'shop', 'temple', 'stables'}
    else:
        if random.random() < .7:
            sv.add('shop')
        if random.random() < .4:
            sv.add('temple')
        if random.random() < .5:
            sv.add('stables')
    return sv


def gen_settlement_map(game, s):
    city = s.is_city
    w, h = (76, 23) if city else (58, 21)
    m = GameMap(s.map_key, 'town', s.name, w, h, GRASS)
    m.radius = 60
    m.sid = s.id
    m.signs = []
    for i in range(len(m.t)):
        if random.random() < (.02 if city else .05):
            m.t[i] = TREE
    sy = h // 2
    for x in range(0, w):
        m.set(x, sy, PATH)
    if city:
        for x in range(w):
            for y in (0, h - 1):
                m.set(x, y, WALL)
        for y in range(h):
            for x in (0, w - 1):
                if y != sy:
                    m.set(x, y, WALL)
    names = NPC_NAMES[:]
    random.shuffle(names)
    roles = []
    order = ['inn', 'market', 'shop', 'temple', 'stables']
    for r in order:
        if r in s.services:
            roles.append(r)
    if s.id == 0:
        roles.append('elder')
    # house slots above and below the street
    slots = []
    x = 3
    while x < w - 12:
        hw = random.randint(9, 12)
        slots.append((x, 2 if not city else 2, hw, sy - 4, 'top'))
        x += hw + random.randint(2, 4)
    x = 3
    while x < w - 12:
        hw = random.randint(9, 12)
        slots.append((x, sy + 3, hw, h - sy - 5 if not city else h - sy - 5, 'bot'))
        x += hw + random.randint(2, 4)
    random.shuffle(slots)
    labels = {}
    for idx, (x0, y0, hw, hh, side) in enumerate(slots):
        hh = max(4, min(hh, 6))
        if side == 'top':
            y0 = sy - 2 - hh
        for yy in range(y0 - 1, y0 + hh + 1):
            for xx in range(x0 - 1, x0 + hw + 1):
                if m.inb(xx, yy) and m.tile(xx, yy) == TREE:
                    m.set(xx, yy, GRASS)
        for yy in range(y0, y0 + hh):
            for xx in range(x0, x0 + hw):
                edge = yy in (y0, y0 + hh - 1) or xx in (x0, x0 + hw - 1)
                m.set(xx, yy, WALL if edge else FLOOR)
        dx = x0 + hw // 2
        dy = y0 + hh - 1 if side == 'top' else y0
        m.set(dx, dy, DOOR)
        step = 1 if side == 'top' else -1
        yy = dy + step
        while yy != sy:
            m.set(dx, yy, PATH)
            yy += step
        role = roles[idx] if idx < len(roles) else None
        cx, cy = x0 + hw // 2, y0 + hh // 2
        if role:
            labels[role] = (cx, cy)
            sign = {'inn': 'INN', 'market': 'TRADER', 'shop': 'OUTFITTER', 'temple': 'TEMPLE', 'stables': 'STABLES', 'elder': 'ELDER'}[role]
            m.signs.append((dx - len(sign) // 2, dy + (1 if side == 'top' else -1), sign))
        elif random.random() < .6:
            m.mons.append(make_npc(game, 'A townsperson', 'villager', '#9aa0aa', cx, cy, False))
    if len(roles) > len(slots):
        return gen_settlement_map(game, s)
    titles = {
        'inn': ('Innkeeper {n}', '#e0a060'), 'market': ('{n} the Trader', '#f2c44a'), 'shop': ('{n} the Outfitter', '#d8d0b0'),
        'temple': ('Sister {n}', '#f4f0e6'), 'stables': ('Stablemaster {n}', '#c8a070'), 'elder': ('Elder Berend', '#c08cf0'),
    }
    for role, (cx, cy) in labels.items():
        nm, col = titles[role]
        n = names.pop()
        if s.id == 0 and role == 'shop':
            label = 'Dorien the Merchant'
        elif s.id == 0 and role == 'temple':
            label = 'Sister Ilse'
        else:
            label = nm.format(n=n)
        m.mons.append(make_npc(game, label, 'healer' if role == 'temple' else role, col, cx, cy, True))
    for wx in range(w // 2 - 6, w // 2 + 6):
        if m.tile(wx, sy - 2) == GRASS and m.tile(wx, sy - 3) in (GRASS, TREE):
            m.set(wx, sy - 2, WELL)
            break
    for _ in range(3 if not city else 6):
        c = rand_free(game, m, lambda t: t in (GRASS, PATH))
        if c:
            m.mons.append(make_npc(game, 'A townsperson' if not city else 'A city guard', 'villager' if not city else 'guard',
                                   '#9aa0aa' if not city else '#7a9cff', c[0], c[1], False))
    if not city:
        c = rand_free(game, m, lambda t: t == GRASS)
        if c:
            m.mons.append(make_npc(game, 'A village dog', 'dog', '#c8a070', c[0], c[1], False, ch='d'))
    px = w // 2 + 3
    m.portal_pos = (px, sy - 1)
    m.set(px, sy - 1, GRASS)
    m.set(px, sy, PATH)
    m.entry = (1 if not city else 0, sy)
    for i in range(len(m.seen)):
        m.seen[i] = 1
    return m
