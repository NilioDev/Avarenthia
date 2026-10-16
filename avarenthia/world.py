"""The open world: regions, settlements, roads, dungeons and the people living in towns."""
import heapq
import math
import random

from . import data as D
from .data import (WALL, FLOOR, DOOR, WATER, GRASS, FOREST, MOUNTAIN, SWAMP, TOWN, ENTR, TREE, PATH, WELL, ROAD,
                   HILLS, SAND, CITY, CASTLE, FORT, RIVER)
from .entities import GameMap, make_npc
from .worldgen import D8, cheb, bfs, noise_grid, rand_free

WORLD_W, WORLD_H = 320, 180
N_CITIES, N_VILLAGES = 8, 38
# what each biome of the terrain is underfoot: the tile decides walking, roads and placement
BIOME_TILE = {}
for _t, _bs in ((WATER, 'ocean sea shallows icy_water pack_ice ice_shelf berg lake lagoon lagoon_deep reef_flat surf reef '
                         'whirl_a whirl_b whirl_eye fjord crater_lake hotpool brine'),
                (RIVER, 'river'),
                (SAND, 'beach desert dune dune_crest cay salt salt_edge bone_sand'),
                (GRASS, 'meadow steppe shrubland shrubland_cold savanna tundra ashland scorched sinter crystal_ground '
                        'stone_ground tar_edge crater_isle'),
                (FOREST, 'forest deep_forest conifer taiga dry_forest jungle petrified dead_trees shroom elder_tree atoll_palm'),
                (HILLS, 'hills tundra_hills badlands crater_rim chasm_edge crystal geyser cliff'),
                (MOUNTAIN, 'mountain peak volcano glacier chasm lava scar_core'),
                (SWAMP, 'swamp marsh tar')):
    for _b in _bs.split():
        BIOME_TILE[_b] = _t
WONDER_BIOMES = set('crater_rim crater_lake crater_isle chasm chasm_edge salt salt_edge brine dune dune_crest geyser hotpool '
                    'sinter elder_tree crystal crystal_ground whirl_a whirl_b whirl_eye reef_flat surf lagoon lagoon_deep cay '
                    'atoll_palm petrified stone_ground tar tar_edge shroom fjord cliff scorched dead_trees scar_core bone_sand '
                    'lava volcano ashland'.split())

TIERS = ['hamlet', 'village', 'town', 'city', 'metropolis']   # small to large
NPC_NAMES = ['Dorien', 'Ilse', 'Berend', 'Maud', 'Aldric', 'Petra', 'Hob', 'Wenna', 'Garrick', 'Tamsin', 'Osric', 'Lyra',
             'Bram', 'Edda', 'Corwin', 'Nell', 'Fenwick', 'Rowan', 'Sabine', 'Tobin', 'Agnes', 'Merrit', 'Jory', 'Hilde']


class Region:
    def __init__(self, rid, cx, cy):
        self.id, self.cx, self.cy = rid, cx, cy
        self.biome = 'grass'
        self.name = ''
        self.danger = 1
        self.faction = 'crown'


class Settlement:
    def __init__(self, sid, name, kind, x, y):
        self.id, self.name, self.kind, self.x, self.y = sid, name, kind, x, y
        self.region = 0
        self.biome = 'grass'
        self.produce, self.demand = [], []
        self.market = {}          # good -> [stock, target, normal_target]
        self.event = None         # (event key, days left)
        self.race = 'human'
        self.board = []           # mission offers
        self.board_day = -99
        self.rep = 0
        self.services = set()
        self.faction = 'crown'

    @property
    def map_key(self):
        return f'town:{self.id}'

    @property
    def is_city(self):
        """Walled cities: a city or a metropolis."""
        return self.kind in ('city', 'metropolis')

    @property
    def kind_name(self):
        return {'deephold': 'dwarven hold'}.get(self.kind, self.kind)

    @property
    def size(self):
        """0 hamlet .. 4 metropolis (a deephold counts as a city)."""
        return TIERS.index(self.kind) if self.kind in TIERS else 3


class Dungeon:
    def __init__(self, did, name, depth, base, style, tag, boss, wall, x, y, main):
        self.id, self.name, self.depth, self.base, self.style, self.tag = did, name, depth, base, style, tag
        self.boss, self.wall, self.x, self.y, self.main = boss, wall, x, y, main
        self.relic = None         # mission id of a fetch quest hidden at the bottom


class Stronghold:
    def __init__(self, hid, name, kind, faction, x, y):
        self.id, self.name, self.kind, self.faction, self.x, self.y = hid, name, kind, faction, x, y
        self.region = 0
        self.max_garrison = 30 if kind == 'castle' else 16
        self.garrison = self.max_garrison
        self.board = []
        self.board_day = -99

    @property
    def map_key(self):
        return f'hold:{self.id}'

    @property
    def title(self):
        f = D.FACTIONS[self.faction]
        return f"{f['castle'] if self.kind == 'castle' else f['fort']} {self.name}"


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
        self.holds = []
        self.road_dist = None     # bytearray: steps to the nearest road or settlement (capped)
        self.pois = []

    def danger_at(self, x, y):
        """Region danger plus a bonus for being far from the roads."""
        rd = self.road_dist[y * WORLD_W + x] if self.road_dist else 0
        bl = getattr(self, 'blight', None)
        return self.region_at(x, y).danger + min(5, rd // 5) + (2 if bl and bl[y * WORLD_W + x] else 0)

    def off_road(self, x, y):
        return self.road_dist[y * WORLD_W + x] if self.road_dist else 0

    def hold_at(self, x, y):
        for h in self.holds:
            if h.x == x and h.y == y:
                return h
        return None

    def region_at(self, x, y):
        return self.regions[self.region_of[y * WORLD_W + x]]

    def settlement_at(self, x, y):
        for s in self.settlements:
            if s.x == x and s.y == y:
                return s
        return None

    def dungeon_at(self, x, y):
        for d in self.dungeons.values():
            if d.x == x and d.y == y and getattr(d, 'town', None) is None:
                return d
        return None


# ------------------------------------------------------------------ generation
def _carve_rivers(m, H, n=9):
    """Rivers spring from the hills below the mountains and run downhill to a lake or the sea."""
    w, h = m.w, m.h
    m.river = bytearray(w * h)
    srcs = [i for i in range(w * h) if m.t[i] == HILLS and any(
        m.inb(i % w + dx, i // w + dy) and m.t[(i // w + dy) * w + i % w + dx] == MOUNTAIN for dx, dy in D8)]
    random.shuffle(srcs)
    made = 0
    for s in srcs:
        if made >= n:
            break
        x, y = s % w, s // w
        if any(m.river[(y + dy) * w + x + dx] for dy in range(-6, 7) for dx in range(-6, 7) if m.inb(x + dx, y + dy)):
            continue
        path, seen = [s], {s}
        ok = False
        for _ in range(220):
            c = path[-1]
            cx, cy = c % w, c // w
            best = None
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = cx + dx, cy + dy
                if not (0 < nx < w - 1 and 0 < ny < h - 1):
                    continue
                ni = ny * w + nx
                if ni in seen or m.t[ni] == MOUNTAIN:
                    continue
                v = H[ni] + random.random() * .015
                if best is None or v < best[0]:
                    best = (v, ni)
            if best is None:
                break
            ni = best[1]
            if m.t[ni] == WATER or m.river[ni]:
                ok = True
                break
            path.append(ni)
            seen.add(ni)
        if not ok or len(path) < 14:
            continue
        for c in path:
            m.t[c] = RIVER
            m.river[c] = 1
        made += 1


def _road_cost(t):
    if t == ROAD:
        return 1
    if t == RIVER:
        return 9
    if t in (GRASS, SAND, TOWN, CITY, ENTR):
        return 3
    if t in (FOREST, HILLS):
        return 6
    if t == SWAMP:
        return 8
    return None


def dijkstra_path(m, a, b, cost_fn=_road_cost):
    """Cheapest 8-way path from a to b on the overworld, as a list of cells after a (A* search)."""
    w, h = m.w, m.h
    costs = [cost_fn(k) for k in range(len(D.TILES))]
    floor = min((c for c in costs if c is not None), default=1)
    INF = 1 << 30
    dist = {}
    prev = {}
    s, goal = a[1] * w + a[0], b[1] * w + b[0]
    gx, gy = b
    dist[s] = 0
    pq = [(0, 0, s)]
    t = m.t
    while pq:
        _f, d, c = heapq.heappop(pq)
        if c == goal:
            break
        if d > dist.get(c, INF):
            continue
        x, y = c % w, c // w
        for dx, dy in D8:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                ni = ny * w + nx
                cc = costs[t[ni]]
                if cc is None:
                    continue
                nd = d + cc + (1 if dx and dy else 0)
                if nd < dist.get(ni, INF):
                    dist[ni] = nd
                    prev[ni] = c
                    ddx, ddy = abs(nx - gx), abs(ny - gy)
                    heapq.heappush(pq, (nd + floor * max(ddx, ddy), nd, ni))
    if goal not in dist:
        return None
    out = []
    c = goal
    while c != s:
        out.append((c % w, c // w))
        c = prev[c]
    out.reverse()
    return out


def gen_world(game):
    from . import evils as EVL, factions as FA
    w, h = WORLD_W, WORLD_H
    evils = EVL.choose()
    factions = FA.generate(EVL.info(evils[0]))
    FA.install(factions)
    for _attempt in range(40):
        m = GameMap('over', 'over', 'The Wilds', w, h, GRASS)
        m.radius = 10
        from . import terrain as TR
        gen = TR.generate(random.getrandbits(32), w, h)
        B = gen['B']
        names = sorted(set(B.ravel().tolist()))
        m.biome_names = names
        idx = {n: k for k, n in enumerate(names)}
        flat = B.ravel().tolist()
        m.biome = bytearray(idx[b] for b in flat)
        m.t = bytearray(BIOME_TILE.get(b, GRASS) for b in flat) if isinstance(m.t, bytearray) else [BIOME_TILE.get(b, GRASS) for b in flat]
        for i in range(w * h):
            x, y = i % w, i // w
            if x in (0, w - 1) or y in (0, h - 1):
                m.t[i] = WATER
        el, rn = gen['elev'].ravel(), gen['rain'].ravel()
        m.elev = bytearray(int(max(0, min(255, v * 255))) for v in el)
        m.moist = bytearray(int(max(0, min(255, v * 255))) for v in rn)
        m.river = bytearray(1 if (v and m.t[i] == RIVER) else 0 for i, v in enumerate(gen['river'].ravel()))
        m.over = {y * w + x: v for (x, y), v in gen['over'].items() if 0 <= x < w and 0 <= y < h}
        m.shadow = {y * w + x for (x, y) in gen['shadow'] if 0 <= x < w and 0 <= y < h}
        wonder_cells = {i for i, b in enumerate(flat) if b in WONDER_BIOMES} | set(m.over)
        # start: temperate open land near the heart of the continent, from which most of it can be walked
        temp = gen['temp'].ravel()
        cont = gen['continent'].ravel()
        n_cont = int(cont.sum())
        cx_ = sum(i % w for i in range(w * h) if cont[i]) / max(1, n_cont)
        cy_ = sum(i // w for i in range(w * h) if cont[i]) / max(1, n_cont)
        cands = sorted((i for i in range(w * h) if m.t[i] == GRASS and cont[i] and .38 < temp[i] < .62
                        and flat[i] in ('meadow', 'steppe', 'shrubland') and i not in wonder_cells),
                       key=lambda i: math.hypot(i % w - cx_, i // w - cy_))
        start = None
        for i in cands[:600:30]:
            dist = bfs(m, i % w, i // w, lambda t: D.TILES[t].walk)
            if sum(1 for d in dist if d > 0) > n_cont * .7:
                start = (i % w, i // w)
                break
        if not start:
            continue
        world = World()
        world.wonders = list(gen['wonders'])
        world.wonder_cells = wonder_cells
        world.evils = evils
        world.factions = factions
        reach = [i for i in range(w * h) if dist[i] > 0 and i not in wonder_cells]
        reach_set = set(reach)
        _make_regions(m, world, reach, start)
        if not _place_settlements(game, m, world, reach_set, dist, start):
            continue
        _build_roads(m, world)
        _place_dungeons(m, world, reach, dist, start)
        for s in world.settlements:
            if s.kind == 'deephold':
                did = f'deep{s.id}'
                danger = world.region_at(s.x, s.y).danger
                dg = Dungeon(did, f'Deep Roads of {s.name}', 4, danger + 2, random.choice(['rooms', 'cave']), 'deep', None,
                             D.hexrgb('#8a7a6a'), s.x, s.y, True)
                dg.town = s.id
                world.dungeons[did] = dg
                s.deep_did = did
        _assign_factions(m, world, start)
        _place_strongholds(m, world, reach)
        for h in world.holds:
            m.set(h.x, h.y, CASTLE if h.kind == 'castle' else FORT)
        _road_distance(m, world)
        for s in world.settlements:
            m.set(s.x, s.y, CITY if s.is_city else TOWN)
        for d in world.dungeons.values():
            if getattr(d, 'town', None) is None:
                m.set(d.x, d.y, ENTR)
        from .foraging import setup_world
        setup_world(world)
        from .sites import gen_sites
        gen_sites(game, m, world)
        from .events import gen_pois
        gen_pois(game, m, world)
        from .hidden import generate as old_ways
        old_ways(game, m, world)
        from .harbour import mark_coast
        mark_coast(m, world)
        return m, world
    raise RuntimeError('World generation failed')


def _make_regions(m, world, reach, start):
    w = m.w
    centers = [start]
    pool = reach[:]
    random.shuffle(pool)
    for i in pool:
        if len(centers) >= 26:
            break
        x, y = i % w, i // w
        if all(math.hypot(x - cx, y - cy) > 24 for cx, cy in centers):
            centers.append((x, y))
    world.regions = [Region(i, cx, cy) for i, (cx, cy) in enumerate(centers)]
    import numpy as np
    gy, gx = np.mgrid[0:m.h, 0:m.w]
    cxs = np.array([c[0] for c in centers])[:, None, None]
    cys = np.array([c[1] for c in centers])[:, None, None]
    nearest = ((gx[None] - cxs) ** 2 + (gy[None] - cys) ** 2).argmin(axis=0).ravel().tolist()
    rof = bytearray(nearest)
    counts = [dict() for _ in centers]
    for i in range(m.w * m.h):
        best = nearest[i]
        t = m.t[i]
        b = {GRASS: 'grass', FOREST: 'forest', SWAMP: 'swamp', HILLS: 'hills', MOUNTAIN: 'hills', SAND: 'coast'}.get(t)
        if b:
            counts[best][b] = counts[best].get(b, 0) + (3 if b == 'coast' else 1)
    world.region_of = rof
    # each region's climate, from the biomes it is made of (the weather follows it)
    bnames = getattr(m, 'biome_names', None)
    if bnames:
        cold = {'tundra', 'taiga', 'glacier', 'tundra_hills', 'shrubland_cold', 'conifer'}
        arid = {'desert', 'dune', 'dune_crest', 'savanna', 'badlands', 'salt', 'dry_forest'}
        wet = {'swamp', 'marsh'}
        tally = [dict(cold=0, arid=0, marsh=0, temperate=0) for _ in centers]
        for i in range(m.w * m.h):
            if m.t[i] in (WATER, MOUNTAIN):
                continue
            b = bnames[m.biome[i]]
            k = 'cold' if b in cold else 'arid' if b in arid else 'marsh' if b in wet else 'temperate'
            tally[rof[i]][k] += 1
        for r in world.regions:
            tl = tally[r.id]
            tl['marsh'] *= 3                     # a little marsh already makes a marshy region
            r.climate = max(tl, key=tl.get)
    used = set()
    for r in world.regions:
        c = counts[r.id]
        r.biome = max(c, key=c.get) if c else 'grass'
        names = [n for n in D.BIOME_NAMES[r.biome] if n not in used] or D.BIOME_NAMES[r.biome]
        r.name = random.choice(names)
        used.add(r.name)
        r.danger = 1 if r.id == 0 else max(1, min(10, 1 + round(math.hypot(r.cx - start[0], r.cy - start[1]) / 17)))
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
    for want_coast in (True, True) + (False,) * (N_CITIES - 2):
        for i in cells:
            x, y = i % w, i // w
            if dist[i] < 22 or not far_enough(x, y, 30):
                continue
            near_water = any(m.inb(x + dx, y + dy) and m.tile(x + dx, y + dy) == WATER for dx in range(-2, 3) for dy in range(-2, 3))
            if want_coast and not near_water:
                continue
            cities.append((x, y))
            taken.append((x, y))
            break
    if len(cities) < N_CITIES - 1:
        return False
    city_names = random.sample(D.CITY_NAMES, len(cities))
    for (x, y), nm in zip(cities, city_names):
        sett.append(Settlement(len(sett), nm, 'city', x, y))
    # villages: spread over regions
    for i in cells:
        if len(sett) >= 1 + len(cities) + N_VILLAGES:
            break
        x, y = i % w, i // w
        if not far_enough(x, y, 11):
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
    if len(sett) < 1 + len(cities) + N_VILLAGES - 4:
        return False
    # sizes: the first coastal city is the great metropolis; the rest of the small places are towns,
    # villages and hamlets
    sett[1].kind = 'metropolis'
    for s in sett[1 + len(cities):]:
        r = random.random()
        s.kind = 'town' if r < .25 else 'village' if r < .65 else 'hamlet'
    # dwarven deepholds, cut into the roots of the mountains
    from .deephold import DEEP_NAMES
    dnames = random.sample(DEEP_NAMES, 2)
    for i in cells:
        if sum(1 for s in sett if s.kind == 'deephold') >= 2:
            break
        x, y = i % w, i // w
        if m.t[i] != HILLS or dist[i] < 15 or not far_enough(x, y, 14):
            continue
        if not any(m.inb(x + dx, y + dy) and m.tile(x + dx, y + dy) == MOUNTAIN for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
            continue
        taken.append((x, y))
        sett.append(Settlement(len(sett), dnames.pop(), 'deephold', x, y))
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
    world.road_edges = []
    m.main_road = set()
    # the great roads between the cities first, so the lesser roads join onto them
    cities = [k for k in range(n) if ss[k].is_city]
    great = []
    if cities:
        tree = {cities[0]}
        while len(tree) < len(cities):
            a, b = min(((a, b) for a in tree for b in cities if b not in tree), key=lambda e: d(*e))
            great.append((a, b))
            tree.add(b)
    for a, b in great:
        p = dijkstra_path(m, (ss[a].x, ss[a].y), (ss[b].x, ss[b].y))
        if p:
            lay_road(m, [(ss[a].x, ss[a].y)] + p, True)
    for a, b in edges:
        p = dijkstra_path(m, (ss[a].x, ss[a].y), (ss[b].x, ss[b].y))
        if not p:
            continue
        world.road_edges.append((a, b))
        lay_road(m, [(ss[a].x, ss[a].y)] + p, ss[a].is_city and ss[b].is_city)


ROAD_GROUND = (GRASS, SAND, FOREST, HILLS, SWAMP, RIVER)


def orthogonal(m, p, ok=None):
    """A path with every diagonal step turned into two straight ones, so it can be drawn as a joined line."""
    ok = ok or (lambda x, y: m.tile(x, y) in ROAD_GROUND or m.tile(x, y) == ROAD)
    out = p[:1]
    for (x0, y0), (x1, y1) in zip(p, p[1:]):
        if x0 != x1 and y0 != y1:
            a, b = (x1, y0), (x0, y1)
            pick = [c for c in (a, b) if m.tile(*c) == ROAD] or [c for c in (a, b) if ok(*c)]
            if pick:
                pick.sort(key=lambda c: m.tile(*c) in (RIVER, SWAMP))
                out.append(pick[0])
        out.append((x1, y1))
    return out


def lay_road(m, p, main=False):
    for x, y in orthogonal(m, p):
        if m.tile(x, y) in ROAD_GROUND:
            m.set(x, y, ROAD)        # over a river this is a bridge (m.river stays marked)
        if main and m.tile(x, y) == ROAD:
            m.main_road.add(y * m.w + x)


def _place_dungeons(m, world, reach, dist, start):
    w = m.w
    used = set()
    blocked = {(s.x, s.y) for s in world.settlements}

    def ok(i):
        x, y = i % w, i // w
        return (x, y) not in blocked and m.t[i] not in (ROAD, WATER, MOUNTAIN, RIVER) and all(cheb(x, y, s.x, s.y) >= 5 for s in world.settlements) \
            and all(cheb(x, y, o[0], o[1]) >= 8 for o in used)

    def choose(lst, fb):
        lst = [i for i in lst if ok(i)]
        i = random.choice(lst) if lst else fb
        used.add((i % w, i // w))
        return i % w, i // w

    near_mount = lambda i: any(m.inb(i % w + dx, i // w + dy) and m.tile(i % w + dx, i // w + dy) in (MOUNTAIN, HILLS) for dx, dy in D8)
    rat = choose([i for i in reach if 7 <= dist[i] <= 14], reach[len(reach) // 10])
    mine = choose([i for i in reach if 16 <= dist[i] <= 32 and near_mount(i)] or [i for i in reach if 16 <= dist[i] <= 32], reach[len(reach) // 4])
    den = choose([i for i in reach if 4 <= dist[i] <= 8], reach[len(reach) // 20])
    for did, (x, y) in (('den', den), ('rat', rat), ('mine', mine)):
        t = D.DUNGEONS[did]
        world.dungeons[did] = Dungeon(did, t['name'], t['depth'], t['base'], t['style'], t['tag'], t['boss'], t['wall'], x, y, True)
    # the lairs of the great evils, far from home and in the land that suits them
    terr = {'swamp': (SWAMP,), 'forest': (FOREST,), 'hills': (HILLS,), 'grass': (GRASS,), 'coast': (SAND, SWAMP)}
    for e in world.evils:
        d = e.d
        want = set(t for k in d['terrain'] for t in terr[k])
        far = [i for i in reach if 30 <= dist[i] <= 60]
        x, y = choose([i for i in far if m.t[i] in want] or far, reach[len(reach) // 3])
        did = 'crypt' if e.key == 'lich' else f'lair_{e.key}'
        world.dungeons[did] = Dungeon(did, d['lair'].format(short=e.short), d['depth'], d['base'], d['style'], d['tag'],
                                      d['boss'], D.hexrgb(d['wall']), x, y, True)
        e.did, e.x, e.y = did, x, y
    sides = D.SIDE_DUNGEONS[:]
    random.shuffle(sides)
    pool = reach[:]
    random.shuffle(pool)
    k = 0
    for i in pool:
        if k >= 9:
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
    # the nests and warrens: an ant nest, a spider lair, a goblin warren and a snake ruin, each in the land it likes
    from .creatures import THEMED
    land = {'grass': (GRASS,), 'forest': (FOREST,), 'swamp': (SWAMP,), 'hills': (HILLS,), 'coast': (SAND,)}
    for j, (names, style, tag, boss, wall, likes) in enumerate(THEMED):
        want = {t for b in likes for t in land[b]}
        cands = [i for i in reach if dist[i] >= 14 and m.t[i] in want and ok(i)] or \
                [i for i in reach if dist[i] >= 12 and ok(i)]
        if not cands:
            continue
        i = random.choice(cands)
        x, y = i % w, i // w
        used.add((x, y))
        danger = world.region_at(x, y).danger
        did = f'nest{j}'
        world.dungeons[did] = Dungeon(did, random.choice(names), 3, max(1, danger * 2 - 1), style, tag, boss, D.hexrgb(wall),
                                      x, y, False)


# ------------------------------------------------------------------ settlement maps
def settlement_services(s):
    if s.kind == 'deephold':
        return {'inn', 'market', 'shop', 'temple'}
    if s.id == 0:
        return {'inn', 'market', 'shop', 'stables'}      # Thornfield's temple stands outside the village
    sv = {'inn', 'market'}
    if s.is_city:
        sv |= {'shop', 'temple', 'stables'}
    elif s.kind == 'hamlet':
        sv = {'market'}                          # a farmer who sells what the hamlet makes, from his own house
        if random.random() < .3:
            sv.add('inn')
    elif s.kind == 'town':
        sv |= {'shop', 'stables'}
        if random.random() < .8:
            sv.add('temple')
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
        'temple': ('Sister {n}', '#f4f0e6'), 'stables': ('Stablemaster {n}', '#c8a070'), 'elder': ('Elder Berend Ashford', '#c08cf0'),
    }
    for role, (cx, cy) in labels.items():
        nm, col = titles[role]
        n = names.pop()
        if s.id == 0 and role == 'shop':
            label = 'Dorien Hale the Merchant'
        elif s.id == 0 and role == 'temple':
            label = 'Sister Ilse Marsh'
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



# ------------------------------------------------------------------ factions
def _assign_factions(m, world, start):
    regs = world.regions
    count = {r.id: 0 for r in regs}
    for st in world.settlements:
        count[st.region] += 1
    lair = world.evils[0]
    crypt_reg = world.region_of[lair.y * m.w + lair.x]
    owner = {0: 'crown'}
    if crypt_reg != 0:
        owner[crypt_reg] = 'cult'
    free = [r for r in regs if r.id not in owner]
    # dwarf clans hold the hills, orc tribes the far badlands
    if 'clan' in D.FACTIONS:
        hills = sorted((r for r in free if r.biome == 'hills'), key=lambda r: -r.danger)[:3] or \
            sorted(free, key=lambda r: -r.danger)[2:3]
        for r in hills:
            owner[r.id] = 'clan'
        free = [r for r in regs if r.id not in owner]
    if 'horde' in D.FACTIONS:
        for r in sorted(free, key=lambda r: (-r.danger, count[r.id]))[:2]:
            owner[r.id] = 'horde'
        free = [r for r in regs if r.id not in owner]
    # outlaws take the dangerous, empty places
    bh = sorted((r for r in free if r.danger >= 3), key=lambda r: (count[r.id], -r.danger, r.biome != 'hills'))[:3]
    for r in bh:
        owner[r.id] = 'blackhand'
    free = [r for r in regs if r.id not in owner]
    cult_extra = sorted((r for r in free if r.biome == 'swamp' and count[r.id] <= 1), key=lambda r: -r.danger)[:1]
    for r in cult_extra:
        owner[r.id] = 'cult'
    if 'cult' not in owner.values() and free:
        owner[max(free, key=lambda r: r.danger).id] = 'cult'
    free = [r for r in regs if r.id not in owner]
    for r in free:
        if r.biome in ('forest', 'swamp'):
            owner[r.id] = 'circle'
    cities_by_reg = {}
    for st in world.settlements:
        if st.is_city:
            cities_by_reg[st.region] = cities_by_reg.get(st.region, 0) + 1
    free = [r for r in regs if r.id not in owner]
    league = sorted((r for r in free if cities_by_reg.get(r.id)), key=lambda r: -cities_by_reg[r.id])[:3]
    if not league and free:
        league = [max(free, key=lambda r: count[r.id])]
    for r in league:
        owner[r.id] = 'league'
    for r in regs:
        r.faction = owner.get(r.id, 'crown')
    for f in D.FACTION_ORDER:
        if f not in (r.faction for r in regs):
            cand = [r for r in regs if r.id != 0 and r.faction == 'crown']
            if cand:
                random.choice(cand).faction = f
    for st in world.settlements:
        st.faction = regs[st.region].faction
    world.settlements[0].faction = 'crown'
    for st in world.settlements:
        st.race = D.FACTIONS[st.faction].get('race', 'human') if random.random() < .8 or st.id == 0 else \
            random.choice(['human', 'human', 'halfling', 'dwarf', 'elf', 'gnome'])
        if st.kind == 'deephold':
            st.race = 'dwarf'
            if 'clan' in D.FACTIONS:
                st.faction = 'clan'


HOLD_PLAN = {'crown': (2, 2), 'league': (1, 1), 'circle': (1, 1), 'clan': (1, 1), 'horde': (1, 2), 'blackhand': (1, 2), 'cult': (1, 1)}


def _place_strongholds(m, world, reach):
    w = m.w
    names = D.STRONGHOLD_NAMES[:]
    random.shuffle(names)
    taken = [(s.x, s.y) for s in world.settlements] + [(d.x, d.y) for d in world.dungeons.values()]
    pool = reach[:]
    random.shuffle(pool)
    for f, (castles, forts) in HOLD_PLAN.items():
        regs = [r.id for r in world.regions if r.faction == f and r.id != 0]
        if not regs:
            continue
        for kind in ['castle'] * castles + ['fort'] * forts:
            for i in pool:
                x, y = i % w, i // w
                if world.region_of[i] not in regs or m.t[i] in (ROAD, WATER, MOUNTAIN) or not D.TILES[m.t[i]].walk:
                    continue
                if any(cheb(x, y, a, b) < 9 for a, b in taken):
                    continue
                if not (3 <= x < m.w - 3 and 3 <= y < m.h - 3):
                    continue
                h = Stronghold(len(world.holds), names.pop() if names else f'Hold {len(world.holds)}', kind, f, x, y)
                h.region = world.region_of[i]
                world.holds.append(h)
                taken.append((x, y))
                break
    # castles of the kingdom and the league are linked to the road network
    for h in world.holds:
        if h.faction in ('crown', 'league', 'circle', 'clan'):
            near = min(world.settlements, key=lambda s: cheb(s.x, s.y, h.x, h.y))
            p = dijkstra_path(m, (h.x, h.y), (near.x, near.y))
            if p:
                lay_road(m, [(h.x, h.y)] + p)


def flip_region(game, rid, faction):
    """A region changes hands: its settlements follow."""
    w = game.world
    reg = w.regions[rid]
    old = reg.faction
    reg.faction = faction
    for st in w.settlements:
        if st.region == rid and st.id != 0:
            st.faction = faction
    return old


def _road_distance(m, world):
    from collections import deque
    w, h = m.w, m.h
    dist = bytearray([255]) * (w * h)
    q = deque()
    for i, t in enumerate(m.t):
        if t in (ROAD, TOWN, CITY):
            dist[i] = 0
            q.append(i)
    while q:
        c = q.popleft()
        d = dist[c] + 1
        if d > 60:
            continue
        x, y = c % w, c // w
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                ni = ny * w + nx
                if dist[ni] > d:
                    dist[ni] = d
                    q.append(ni)
    world.road_dist = dist
