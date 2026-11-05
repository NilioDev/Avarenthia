"""Block 15: more makers (round 50, part 1). Places that are not a classic dungeon, each with its own plan so you can
tell from the map what it is (delves-style rooms by their use, data in `makerdata.py`):

- a fallen dwarf hold in three layers (the city, the workshops, the mines), the chasm bridge fallen, the forges cold;
  why it fell comes from the history and goes into the chronicle;
- real mines: galleries along the ore with rails and props, cave-ins, the deep level flooded; the Lost Mine is one;
- the sewers of a city: channels with ledges, grates up to the street, a thieves' den;
- the catacombs of a city: a grid of narrow passages lined with the dead, a bone chapel;
- the dungeon under a castle: cells with prisoners to free, the question room, the guard room and the jailer;
- a maze with the minotaur at its heart;
- ice caves in the glaciers: slick ice you slide over, the frozen dead.

A dungeon made here carries `d.maker`; `delves.kind_for` turns that into the plan of each level."""
import random

from . import data as D
from . import makerdata as MD
from .worldgen import cheb

NAMES = {
    'sewer': 'The Sewers of {s}', 'catacomb': 'The Catacombs of {s}', 'castle': 'The Dungeons of {s}',
    'maze': ['The Maze of the Bull', 'The Labyrinth of Old Kings', 'The Hedge of Horns', 'The Winding Dark'],
    'icecave': ['The Blue Caves', 'The Glacier Mouth', 'The Frozen Throat', 'The Caves of Rime'],
    'fallenhold': ['Khaz Dummar, the Fallen Hold', 'Barak Uldin, the Fallen Hold', 'Gundrak, the Silent Hold'],
    'realmine': ['The Old Copper Workings', 'The Deep Seam', 'Coalpit Hollow'],
    'lavatube': ['The Fire Tubes', 'The Burnt Throat', 'The Ember Runs', 'The Old Fire Road'],
    'tidecave': ["The Smugglers' Hole", 'The Gull Cave', "The Drowned Man's Cave", 'The Tide Hall'],
    'fungal': ['The Spore Deep', 'The Mushroom Wood', 'The Pale Hollows', 'The Breathing Dark'],
    'smial': ['Bag End Hollow', 'Old Burrowes Smial', 'Number Nine, Under-Hill', 'The Empty Smial'],
    'burntglade': ['The Burnt Glade', 'The Ash Ring', 'The Black Bower', 'The Glade of Cinders'],
    'drowned': ['Old {s} under the Lake', 'Drowned {s}', 'Sunken {s}'],
    'hideout': ["Gallow's Quarry", 'The Outlaws\' Pit', 'Red Hob\'s Quarry', 'The Wolfshead Hole'],
    'feyhill': ['The Hollow Hill', 'The Hill of the Fair Folk', 'The Green Mound', 'The Hill Where Time Sleeps'],
    'steading': ["The Jarl's Steading", "Grimhald's Hall", 'The Giant Steading', 'The House of Ymmir'],
    'wyrmbones': ["The Wyrm's Rest", 'The Dragon Bones', 'The Old Wyrm', 'The Ribs of Fafnir'],
    'shaft': ['The Swallow Hole', 'The Long Drop', 'The Windy Pit', 'The Throat of the Hill'],
    'cellar': ['The Cellars of {s}', 'Under {s}'],
    'geode': ['The Rainbow Cave', 'The Glittering Hollow', 'The Crystal Egg'],
    'termite': ['The Great Mound', 'The Red Tower', 'The Termite Spire', 'The Chewed Hill'],
    'vaults': ['The Vaults of {s}', 'The Old Graveyard of {s}'],
}
TAG = {'sewer': 'lair_rat', 'catacomb': 'crypt', 'castle': 'dungeon', 'maze': 'dungeon', 'icecave': 'cave',
       'realmine': 'deep', 'lavatube': 'lair_ifrit', 'tidecave': 'grotto', 'fungal': 'gloam', 'smial': 'lair_rat',
       'burntglade': 'wild', 'drowned': 'lair_drowned', 'hideout': 'wild', 'feyhill': 'lair_fey', 'steading': 'lair_giant',
       'wyrmbones': 'crypt', 'shaft': 'cave', 'cellar': 'lair_rat', 'geode': 'deep', 'termite': 'antnest', 'vaults': 'crypt'}
# part 2 on the land: (kind, how many, depth, wall colour, the biomes it seeks, else these tiles)
LAND = [('lavatube', 2, 2, '#6a4a3a', ('volcano', 'lava', 'ashland', 'scorched', 'crater_rim'), ('MOUNTAIN_EDGE',)),
        ('tidecave', 2, 1, '#6a7a7a', ('beach', 'cliff', 'fjord', 'surf'), ('COAST',)),
        ('fungal', 2, 2, '#7a6a8a', ('shroom',), ('deep_forest', 'swamp', 'jungle')),
        ('burntglade', 2, 1, '#4a4038', ('burnt', 'dead_trees'), ('forest', 'birch', 'deep_forest')),
        ('drowned', 1, 1, '#5a6a5a', ('LAKESIDE',), ()),
        ('hideout', 2, 1, '#8a8070', ('canyon', 'badlands'), ('hills',)),
        ('feyhill', 1, 1, '#6a8a5a', ('clearing', 'meadow'), ('forest',)),
        ('steading', 2, 2, '#8a8478', ('alpine', 'tundra_hills'), ('MOUNTAIN_EDGE',)),
        ('wyrmbones', 1, 1, '#c8c0a8', ('bone_sand',), ('badlands', 'desert')),
        ('shaft', 2, 3, '#7a7468', ('sinkhole', 'karst'), ('hills',)),
        ('geode', 1, 1, '#9a8ab8', ('crystal', 'crystal_ground'), ('MOUNTAIN_EDGE',)),
        ('termite', 2, 2, '#a86a40', ('savanna',), ('steppe', 'dry_forest'))]


# ------------------------------------------------------------------ where they are
def place(m, world, reach):
    """At world making, after the holds: the new places on the land (own random stream: the rest of the world stays)."""
    from .world import Dungeon
    rnd = random.Random(len(world.settlements) * 977 + world.settlements[0].x * 31 + len(world.dungeons))
    taken = {(d.x, d.y) for d in world.dungeons.values()} | {(s.x, s.y) for s in world.settlements} | \
        {(h.x, h.y) for h in world.holds}
    reach_set = set(reach) if not isinstance(reach, set) else reach

    def spot_near(x, y, lo, hi, tiles=None):
        cells = [(x + dx, y + dy) for dx in range(-hi, hi + 1) for dy in range(-hi, hi + 1)
                 if lo <= max(abs(dx), abs(dy)) <= hi]
        rnd.shuffle(cells)
        for cx, cy in cells:
            if not m.inb(cx, cy) or (cx, cy) in taken or any(cheb(cx, cy, a, b) < 2 for a, b in taken):
                continue
            t = m.tile(cx, cy)
            if t in (D.WATER, D.MOUNTAIN, D.RIVER, D.ROAD, D.TOWN, D.CITY, D.CASTLE, D.FORT, D.ENTR):
                continue
            if tiles and t not in tiles:
                continue
            if (cy * m.w + cx) not in reach_set:
                continue
            return cx, cy
        return None

    def add(did, name, depth, base, tag, maker, x, y, wall='#8a8478', style='rooms'):
        dg = Dungeon(did, name, depth, base, style, tag, None, D.hexrgb(wall), x, y, False)
        dg.maker = maker
        world.dungeons[did] = dg
        taken.add((x, y))
        return dg
    danger = lambda x, y: world.region_at(x, y).danger                      # noqa: E731
    cities = [s for s in world.settlements if s.is_city and s.race == 'human']
    rnd.shuffle(cities)
    for k, s in enumerate(cities[:4]):                 # the sewers' outfall by the wall
        c = spot_near(s.x, s.y, 2, 4)
        if c:
            add(f'sewer{k}', NAMES['sewer'].format(s=s.name), 2, max(1, danger(*c) * 2 - 1), TAG['sewer'], 'sewer', *c,
                wall='#6e6a5c').city = s.id
    for k, s in enumerate(cities[:3]):                 # the catacombs under the temple quarter (every city has one)
        c = spot_near(s.x, s.y, 2, 5)
        if c:
            add(f'catac{k}', NAMES['catacomb'].format(s=s.name), 2, max(1, danger(*c) * 2), TAG['catacomb'], 'catacomb',
                *c, wall='#8a8a96').city = s.id
    holds = [h for h in world.holds if h.kind == 'castle'] or list(world.holds)
    rnd.shuffle(holds)
    for k, h in enumerate(holds[:3]):                  # the dungeon under a castle
        c = spot_near(h.x, h.y, 1, 3)
        if c:
            add(f'cdun{k}', NAMES['castle'].format(s=getattr(h, 'name', None) or 'the Castle'), 1,
                max(1, danger(*c) * 2 - 1), TAG['castle'], 'castle', *c, wall='#7e7a74').hold = h.id
    cands = [i for i in reach_set if m.t[i] in (D.GRASS, D.HILLS)]
    rnd.shuffle(cands)
    names = NAMES['maze'][:]
    rnd.shuffle(names)
    for k in range(2):                                 # mazes in open country
        for i in cands[k * 40:(k + 1) * 40]:
            c = spot_near(i % m.w, i // m.w, 0, 0)
            if c and all(cheb(c[0], c[1], s.x, s.y) >= 6 for s in world.settlements):
                add(f'maze{k}', names[k], 1, max(2, danger(*c) * 2), TAG['maze'], 'maze', *c, wall='#8c8a70')
                break
    from .nature import biome
    cold = [i for i in reach_set if biome(m, i % m.w, i // m.w) == 'glacier']           # the glaciers first
    rnd.shuffle(cold)
    snow = [i for i in reach_set if m.t[i] == D.SNOW and i not in cold]
    rnd.shuffle(snow)
    cold += snow
    names = NAMES['icecave'][:]
    rnd.shuffle(names)
    for k in range(2):                                 # ice caves in the glaciers
        for i in cold[k * 40:(k + 1) * 40]:
            c = spot_near(i % m.w, i // m.w, 0, 0)
            if c:
                add(f'ice{k}', names[k], 2, max(2, danger(*c) * 2), TAG['icecave'], 'icecave', *c, wall='#a8c8e0',
                    style='cave')
                break
    hills = [i for i in reach_set if m.t[i] == D.HILLS and any(m.inb(i % m.w + a, i // m.w + b)
                                                             and m.t[(i // m.w + b) * m.w + i % m.w + a] == D.MOUNTAIN
                                                             for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    rnd.shuffle(hills)
    for i in hills[:60]:                               # one fallen dwarf hold, by the mountains
        c = spot_near(i % m.w, i // m.w, 0, 0)
        if c and all(cheb(c[0], c[1], s.x, s.y) >= 10 for s in world.settlements):
            key, _line, tag = rnd.choice(MD.CAUSES)
            dg = add('fallenhold', rnd.choice(NAMES['fallenhold']), 3, max(3, danger(*c) * 2 + 1), tag, 'fallenhold',
                     *c, wall='#8a7a6a')
            dg.cause = key
            break
    names = NAMES['realmine'][:]
    rnd.shuffle(names)
    for k, i in enumerate(hills[60:62]):               # an abandoned mine or two
        c = spot_near(i % m.w, i // m.w, 0, 0)
        if c:
            add(f'rmine{k}', names[k], 2, max(1, danger(*c) * 2), TAG['realmine'], 'realmine', *c, wall='#8a7a6a',
                style='cave')
    lost = world.dungeons.get('mine')                  # the Lost Mine becomes a real mine
    if lost is not None:
        lost.maker = 'realmine'
    set_places_part2(m, world, reach_set, rnd, spot_near, add, danger, cities)
    set_states(world, rnd)


def set_places_part2(m, world, reach_set, rnd, spot_near, add, danger, cities):
    # --- part 2: the places of the land, each where its country is
    from .nature import biome
    by_biome = {}
    for i in reach_set:
        by_biome.setdefault(biome(m, i % m.w, i // m.w), []).append(i)

    def near_tile(i, tiles, r=1):
        x, y = i % m.w, i // m.w
        return any(m.inb(x + a, y + b) and m.t[(y + b) * m.w + x + a] in tiles
                   for a in range(-r, r + 1) for b in range(-r, r + 1))
    lake = set()
    for i, _t in enumerate(m.t):
        if m.t[i] == D.WATER and biome(m, i % m.w, i // m.w) in ('lake', 'crater_lake'):
            lake.add(i)
    for kind_, n, depth, wall, seek, fallback in LAND:
        cands = []
        for b in seek:
            if b == 'LAKESIDE':
                cands += [i for i in reach_set if any(j in lake for j in (i + 1, i - 1, i + m.w, i - m.w))]
            else:
                cands += by_biome.get(b, [])
        more = []
        for b in fallback:
            if b == 'MOUNTAIN_EDGE':
                more += [i for i in reach_set if m.t[i] == D.HILLS and near_tile(i, (D.MOUNTAIN,))]
            elif b == 'COAST':
                more += [i for i in reach_set if near_tile(i, (D.WATER,)) and not any(
                    j in lake for j in (i + 1, i - 1, i + m.w, i - m.w))]
            else:
                more += by_biome.get(b, [])
        rnd.shuffle(cands)
        rnd.shuffle(more)
        names = NAMES[kind_][:]
        rnd.shuffle(names)
        k = 0
        for i in cands + more:
            if k >= n:
                break
            c = spot_near(i % m.w, i // m.w, 0, 0)
            if not c or any(cheb(c[0], c[1], s.x, s.y) < 4 for s in world.settlements):
                continue
            nm = names[k % len(names)]
            if '{s}' in nm:
                s = min(world.settlements, key=lambda q: cheb(q.x, q.y, *c))
                nm = nm.format(s=s.name)
            add(f'{kind_}{k}', nm, depth, max(1, danger(*c) * 2), TAG[kind_], kind_, *c, wall=wall,
                style='rooms' if MD.KINDS[kind_].get('built') else 'cave')
            k += 1
    halflings = [s for s in world.settlements if s.race == 'halfling']
    rnd.shuffle(halflings)
    for k, s in enumerate(halflings[:2]):              # a hill home the halflings left
        c = spot_near(s.x, s.y, 2, 5, (D.GRASS, D.HILLS, D.FOREST))
        if c:
            add(f'smial{k}', NAMES['smial'][k], 1, max(1, danger(*c) * 2 - 1), TAG['smial'], 'smial', *c, wall='#8a7a5a')
    towns = [s for s in world.settlements if s.kind in ('town', 'city') and s.race in ('human', 'halfling', 'dwarf')]
    rnd.shuffle(towns)
    for k, s in enumerate(towns[:3]):                  # cellars under a town (their hatch by the gate)
        c = spot_near(s.x, s.y, 1, 3)
        if c:
            add(f'cellar{k}', NAMES['cellar'][k % 2].format(s=s.name), 1, max(1, danger(*c) * 2 - 1), TAG['cellar'],
                'cellar', *c, wall='#7a6a5a').town_near = s.id
    for k, s in enumerate(cities[3:5] or cities[:2]):  # a graveyard of family vaults outside a city
        c = spot_near(s.x, s.y, 2, 5)
        if c:
            add(f'vaults{k}', NAMES['vaults'][k % 2].format(s=s.name), 1, max(1, danger(*c) * 2), TAG['vaults'], 'vaults',
                *c, wall='#8a8a96')


def kind(d, depth):
    """The plan of this level of a maker's place (delves.kind_for)."""
    mk = getattr(d, 'maker', None)
    if mk == 'fallenhold':
        return ('fallenhold', 'fallenhold2', 'fallenhold3')[min(depth, 3) - 1]
    if mk == 'realmine':
        return 'realmine' if depth < d.depth or d.depth == 1 else 'realmine_deep'
    return mk


# ------------------------------------------------------------------ carving: the grid and the maze
def _box_room(m, role, cx, cy, rx, ry, rooms):
    cells = {(x, y) for y in range(cy - ry, cy + ry + 1) for x in range(cx - rx, cx + rx + 1) if 1 <= x < m.w - 1
             and 1 <= y < m.h - 1}
    for x, y in cells:
        m.t[y * m.w + x] = D.FLOOR
    rooms.append((role, cx, cy, cells))


def _finish(m, kind, rooms):
    m.delve, m.built = kind, True
    m.room_of = bytearray(b'\xff') * (m.w * m.h)
    m.rooms = []
    for rid, (role, cx, cy, cells) in enumerate(rooms):
        m.rooms.append([f'delve:{role}', 'room', None])
        for x, y in cells:
            m.room_of[y * m.w + x] = rid
    m.delve_rooms = [(r[0], r[1], r[2]) for r in rooms]


def carve_grid(game, m, d, depth, kind):
    """Catacombs: narrow passages on a grid, every wall between them lined with the dead; a bone chapel at the end."""
    W, H = min(m.w - 2, 90), min(m.h - 2, 50)
    x0, y0 = (m.w - W) // 2, (m.h - H) // 2
    m.t = [D.WALL] * (m.w * m.h)
    for y in range(y0, y0 + H):
        for x in range(x0, x0 + W):
            if (x - x0) % 4 == 0 or (y - y0) % 4 == 0:
                if random.random() < .93 or (x - x0) % 4 == 0 and (y - y0) % 4 == 0:
                    m.t[y * m.w + x] = D.FLOOR
    for y in range(y0, y0 + H):                       # the dead in the walls beside the passages
        for x in range(x0, x0 + W):
            i = y * m.w + x
            if m.t[i] == D.WALL and (x + 2 * y) % 3 == 0 and any(m.t[i + o] == D.FLOOR for o in (1, -1, m.w, -m.w)):
                m.t[i] = D.BONES
    rooms = []
    _box_room(m, 'stair', x0 + 2, y0 + H // 2, 2, 2, rooms)
    _box_room(m, 'bonechapel', x0 + W - 8, y0 + H // 2, 6, 4, rooms)
    _box_room(m, 'ossuary', x0 + W // 3, y0 + 6, 4, 3, rooms)
    _box_room(m, 'ossuary', x0 + 2 * W // 3, y0 + H - 7, 4, 3, rooms)
    _finish(m, kind, rooms)
    _join(m, (x0 + 2, y0 + H // 2))
    return (x0 + 1, y0 + H // 2), (x0 + W - 8, y0 + H // 2)


def carve_maze(game, m, d, depth, kind):
    """A true maze: one way through, many dead ends, cut in hedges of stone; the heart in the middle."""
    W, H = min(m.w - 2, 79) | 1, min(m.h - 2, 49) | 1
    x0, y0 = (m.w - W) // 2, (m.h - H) // 2
    m.t = [D.WALL] * (m.w * m.h)
    cw, ch = W // 2, H // 2
    seen = {(0, ch // 2)}
    stack = [(0, ch // 2)]
    cell = lambda a, b: (x0 + 1 + 2 * a, y0 + 1 + 2 * b)           # noqa: E731
    m.t[cell(0, ch // 2)[1] * m.w + cell(0, ch // 2)[0]] = D.FLOOR
    while stack:
        a, b = stack[-1]
        nb = [(a + da, b + db) for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1))
              if 0 <= a + da < cw and 0 <= b + db < ch and (a + da, b + db) not in seen]
        if not nb:
            stack.pop()
            continue
        na, nbb = random.choice(nb)
        seen.add((na, nbb))
        (x1, y1), (x2, y2) = cell(a, b), cell(na, nbb)
        m.t[((y1 + y2) // 2) * m.w + (x1 + x2) // 2] = D.FLOOR
        m.t[y2 * m.w + x2] = D.FLOOR
        stack.append((na, nbb))
    for _ in range(W * H // 120):                      # a few loops, so it is not only one way
        x, y = random.randrange(x0 + 2, x0 + W - 2), random.randrange(y0 + 2, y0 + H - 2)
        if m.t[y * m.w + x] == D.WALL and ((m.t[y * m.w + x - 1] == D.FLOOR == m.t[y * m.w + x + 1]) or
                                          (m.t[(y - 1) * m.w + x] == D.FLOOR == m.t[(y + 1) * m.w + x])):
            m.t[y * m.w + x] = D.FLOOR
    rooms = []
    gx, gy = cell(0, ch // 2)
    _box_room(m, 'gate', gx, gy, 1, 1, rooms)
    hx, hy = x0 + W // 2, y0 + H // 2
    _box_room(m, 'heart', hx, hy, 4, 3, rooms)
    _finish(m, kind, rooms)
    return (gx, gy), (hx, hy)


def carve_vaults(game, m, d, depth, kind):
    """A graveyard of family vaults: rows of small stone houses of the dead among the yews, the oldest at the end."""
    W, H = min(m.w - 2, 70), min(m.h - 2, 40)
    x0, y0 = (m.w - W) // 2, (m.h - H) // 2
    m.t = [D.TREE] * (m.w * m.h)
    for y in range(y0 + 1, y0 + H - 1):
        for x in range(x0 + 1, x0 + W - 1):
            m.t[y * m.w + x] = D.FLOOR if random.random() > .03 else D.GRAVE
    rooms = []
    gy = y0 + H // 2
    _box_room(m, 'lychgate', x0 + 3, gy, 2, 2, rooms)
    spots = [(x0 + 12 + 9 * a, y0 + 6 + 9 * b) for a in range((W - 24) // 9) for b in range((H - 10) // 9)]
    random.shuffle(spots)
    big = (x0 + W - 9, gy)
    spots = [c for c in spots if cheb(*c, *big) > 7 and cheb(*c, x0 + 3, gy) > 6]
    for cx, cy, rx, ry, role in [(big[0], big[1], 4, 3, 'greatvault')] + [(c[0], c[1], 2, 2, 'vault') for c in spots[:9]]:
        for y in range(cy - ry - 1, cy + ry + 2):     # the vault's walls, its door on the side to the gate
            for x in range(cx - rx - 1, cx + rx + 2):
                m.t[y * m.w + x] = D.WALL
        _box_room(m, role, cx, cy, rx, ry, rooms)
        m.t[(cy + ry + 1) * m.w + cx] = D.DOOR
    _finish(m, kind, rooms)
    return (x0 + 2, gy), big


def _join(m, start):
    from .delves import _join as J
    J(m, start)


# ------------------------------------------------------------------ after the carving: water, rails, ice
def after_carve(game, m, d, depth, kind, up, down):
    spec = MD.KINDS.get(kind, {})
    if spec.get('channels'):                           # the middle of each channel runs with the city's water
        for rid, (role, cx, cy) in enumerate(m.delve_rooms):
            if role == 'channel':
                for i, r in enumerate(m.room_of):
                    if r == rid and i // m.w == cy and m.t[i] == D.FLOOR:
                        m.t[i] = D.SHALLOW
    if spec.get('rails'):                              # a cart line from the pithead to the face
        from .worldgen import bfs
        dist = bfs(m, down[0], down[1], lambda t: D.TILES[t].walk)
        x, y = up
        for _ in range(400):
            i = y * m.w + x
            if dist[i] < 0 or dist[i] <= 1:
                break
            if m.t[i] == D.FLOOR and (x, y) != tuple(up):
                m.t[i] = D.RAIL
            nxt = [(x + a, y + b) for a in (-1, 0, 1) for b in (-1, 0, 1) if (a or b) and m.inb(x + a, y + b)
                   and 0 <= dist[(y + b) * m.w + x + a] < dist[i]]
            if not nxt:
                break
            x, y = nxt[0]
        m.mine_rock = True
    if kind == 'realmine_deep':
        for rid, (role, cx, cy) in enumerate(m.delve_rooms):
            if role == 'flooded':
                for i, r in enumerate(m.room_of):
                    if r == rid and m.t[i] == D.FLOOR and abs(i % m.w - cx) + abs(i // m.w - cy) <= 4:
                        m.t[i] = D.WATER
    if spec.get('ice'):
        m.icecave = True
        for rid, (role, cx, cy) in enumerate(m.delve_rooms):
            if role in ('icehall', 'crevasse', 'frozenhall'):
                for i, r in enumerate(m.room_of):
                    if r == rid and m.t[i] == D.FLOOR and cheb(i % m.w, i // m.w, *up) > 2 \
                            and cheb(i % m.w, i // m.w, *down) > 1 and random.random() < .8:
                        m.t[i] = D.SLICK
    def cells_of(rid):
        return [i for i, r in enumerate(m.room_of) if r == rid and m.t[i] == D.FLOOR]
    keep = {up[1] * m.w + up[0], down[1] * m.w + down[0]}
    from .worldgen import bfs

    def joined():
        dist = bfs(m, up[0], up[1], lambda t: D.TILES[t].walk or D.TILES[t].door)
        return dist[down[1] * m.w + down[0]] >= 0

    def paint(cells, tile, back=D.FLOOR):
        """Lay a tile that blocks; take it back if it cut the way from the stair up to the far end."""
        was = [(i, m.t[i]) for i in cells]
        for i in cells:
            m.t[i] = tile
        if not joined():
            for i, t in was:
                m.t[i] = back if back is not None else t
    if spec.get('crust'):                              # lava tubes: crusts on the floor, pools of fire
        for i, t in enumerate(m.t):
            if t == D.FLOOR and i not in keep and random.random() < .12:
                m.t[i] = D.CRUST
        for rid, (role, cx, cy) in enumerate(m.delve_rooms):
            if role in ('firepool', 'magmahall'):
                r = 2 if role == 'firepool' else 1
                cs = cells_of(rid)
                for i in cs:
                    if i not in keep and cheb(i % m.w, i // m.w, cx, cy) == r + 1:
                        m.t[i] = D.CRUST
                paint([i for i in cs if i not in keep and cheb(i % m.w, i // m.w, cx, cy) <= r], D.LAVA, D.CRUST)
    if spec.get('tidal'):                              # the low caves the sea fills at high tide (tick)
        m.tidal = dict(low=[], sump=[], high=None)
        for rid, (role, cx, cy) in enumerate(m.delve_rooms):
            if role in ('lowcave', 'sump', 'seamouth'):
                m.tidal['sump' if role == 'sump' else 'low'] += [i for i in cells_of(rid) if i not in keep]
    if spec.get('spores'):
        m.spores = True
    if spec.get('outdoor'):                            # out under the sky: the walls are trees
        for i, t in enumerate(m.t):
            if t == D.ROCK:
                m.t[i] = D.TREE
        m.outdoor = True
    if spec.get('ash'):
        for i, t in enumerate(m.t):
            if t == D.FLOOR and i not in keep and random.random() < .5:
                m.t[i] = D.ASH
    if spec.get('mud'):                                # the lake bed: pools left in the mud
        for rid, (role, cx, cy) in enumerate(m.delve_rooms):
            if role in ('mudstreet', 'lakeshore'):
                for i in cells_of(rid):
                    if i not in keep and random.random() < .3:
                        m.t[i] = D.SHALLOW
    if spec.get('ribs'):                               # the ribs: rows of bone across the ribcage, with ways between
        for rid, (role, cx, cy) in enumerate(m.delve_rooms):
            if role == 'ribcage':
                paint([i for i in cells_of(rid) if (i % m.w - cx) % 3 == 0 and abs(i // m.w - cy) >= 2 and i not in keep],
                      D.BONES)
    if spec.get('pit'):                                # the open pit in the middle of the shaft
        for rid, (role, cx, cy) in enumerate(m.delve_rooms):
            if role == 'pitrim' and depth < d.depth:
                paint([i for i in cells_of(rid) if i not in keep and (i % m.w - cx) ** 2 + ((i // m.w - cy) * 1.6) ** 2 <= 12],
                      D.CHASM)
        m.shaft = True
    if spec.get('prism'):
        m.prism = True
    if getattr(d, 'maker', None) == 'fallenhold':
        m.cause = getattr(d, 'cause', 'deep')
        if m.cause == 'flood' and depth >= 2:
            for rid, (role, cx, cy) in enumerate(m.delve_rooms):
                if role in ('store', 'cavein', 'gallery') and random.random() < .5:
                    for i, r in enumerate(m.room_of):
                        if r == rid and m.t[i] == D.FLOOR:
                            m.t[i] = D.SHALLOW


# ------------------------------------------------------------------ the folk only these places have
def after_folk(game, m, d, depth, up, down):
    from .entities import make_monster, make_npc
    from .worldgen import free_around
    lvl = d.base + depth
    kind = m.delve
    rooms = list(enumerate(m.delve_rooms))

    def cells_of(rid):
        return [(i % m.w, i // m.w) for i, r in enumerate(m.room_of) if r == rid and D.TILES[m.t[i]].walk
                and not m.mon_at(i % m.w, i // m.w)]
    if kind == 'maze':
        heart = next(rid for rid, r in rooms if r[0] == 'heart')
        if not any(o.k == 'minotaur' for o in m.mons):
            c = random.choice(cells_of(heart))
            m.mons.append(make_monster(game, 'minotaur', c[0], c[1], lvl + 2))
    if kind == 'castle':
        names = ['Old Wat', 'Merrin', 'Tobyn the poacher', 'Hesk', 'A girl from the village', 'Brother Ansel']
        random.shuffle(names)
        for rid, r in rooms:
            if r[0] == 'cell' and random.random() < .7 and names:
                cs = cells_of(rid)
                if cs:
                    c = random.choice(cs)
                    n = make_npc(game, names.pop() + ', a prisoner', 'prisoner', '#c8b8a0', c[0], c[1], True)
                    n.home_pos = n.work_pos = c
                    m.mons.append(n)
        gr = next((rid for rid, r in rooms if r[0] == 'guardroom'), None)
        if gr is not None:
            cs = cells_of(gr)
            if cs:
                c = random.choice(cs)
                m.mons.append(make_monster(game, 'jailer', c[0], c[1], lvl))
    if kind == 'icecave':
        for rid, r in rooms:
            if r[0] in ('frozen', 'frozenhall'):
                for c in random.sample(cells_of(rid), min(3, len(cells_of(rid)))):
                    mon = make_monster(game, 'frozen_dead', c[0], c[1], lvl)
                    mon.awake = False
                    m.mons.append(mon)
    if kind == 'sewer':
        den = next((rid for rid, r in rooms if r[0] == 'den'), None)
        if den is not None:
            for c in cells_of(den)[:3]:
                m.mons.append(make_monster(game, 'bandit', c[0], c[1], lvl))
    if kind in ('fallenhold', 'fallenhold2', 'fallenhold3') and depth == 1:
        tell_cause(game, d)
    if kind in ('realmine', 'realmine_deep') and getattr(m, 'deco', None) is not None:   # the miners' lamps
        from .dress import TORCH, GLOW
        rock = [i for i, t in enumerate(m.t) if t == D.ROCK and 0 < i % m.w < m.w - 1 and 0 < i // m.w < m.h - 1
                and any(m.t[i + o] in (D.FLOOR, D.RAIL) for o in (1, -1, m.w, -m.w))]
        for i in random.sample(rock, min(len(rock), random.randint(8, 12))):
            m.deco[i] = TORCH
            col, r = GLOW[TORCH]
            m.lights.append((i % m.w, i // m.w, col, r))
    if kind == 'hideout':                              # the outlaws: a watch by the bell, the rest about the quarry
        for role, n, watch, asleep, plus in (('quarrygate', 2, True, False, 0), ('yard', 3, False, False, 0),
                                             ('bunks', 2, False, True, 0), ('lootroom', 1, False, False, 3)):
            for rid, r in rooms:
                if r[0] != role:
                    continue
                for c in random.sample(cells_of(rid), min(n, len(cells_of(rid)))):
                    o = make_monster(game, 'bandit', c[0], c[1], lvl + plus)
                    o.watch, o.awake = watch, not asleep and random.random() < .3
                    if plus:
                        o.name = 'Outlaw Captain'
                    m.mons.append(o)
    if kind == 'tidecave':
        stash = next((rid for rid, r in rooms if r[0] == 'stash'), None)
        if stash is not None:
            for c in cells_of(stash)[:2]:
                m.mons.append(make_monster(game, 'bandit', c[0], c[1], lvl))
    apply_state(game, m, d, depth, up, down)
    if depth == 1:
        state_line(game, d)


def tell_cause(game, d):
    """The chronicle: why the hold fell (seen with your own eyes)."""
    from . import chronicle as CH
    line = next((c[1] for c in MD.CAUSES if c[0] == getattr(d, 'cause', 'deep')), MD.CAUSES[0][1])
    CH.seen_place(game, 'fall:' + d.id, d.name, f'{d.name} {line}. The halls are as they left them.', (d.x, d.y))


# ------------------------------------------------------------------ on the ice, and the prisoners
def on_step(game, ox, oy):
    """In an ice cave: on slick ice you slide on the way you went until something stops you."""
    m, p = game.map, game.player
    if m.t[p.y * m.w + p.x] != D.SLICK:
        return
    dx, dy = p.x - ox, p.y - oy
    if abs(dx) > 1 or abs(dy) > 1 or (dx, dy) == (0, 0):
        return
    slid = 0
    while m.t[p.y * m.w + p.x] == D.SLICK and slid < 30:
        nx, ny = p.x + dx, p.y + dy
        if not m.inb(nx, ny) or not D.TILES[m.tile(nx, ny)].walk or game.occupied(m, nx, ny):
            break
        p.x, p.y = nx, ny
        slid += 1
    if slid:
        game.msg('You slide across the ice.')
        game.compute_fov()
        from . import guide as GDE
        GDE.tip(game, 'ice')


def talk(game, npc):
    """A prisoner in a castle's cells: free them (the castle's lord will not thank you, their village will)."""
    if npc.role != 'prisoner':
        return False
    m = game.map
    m.mons.remove(npc)
    game.msg(f'You break the lock. {npc.name.split(",")[0]} slips past you towards the stair, with a look you will '
             'remember.', 'good')
    freed = game.player.__dict__.setdefault('freed', 0)
    game.player.freed = freed + 1
    near = min(game.world.settlements, key=lambda s: cheb(s.x, s.y, *game.world_pos()))
    from . import jobs as JB
    JB.effects(game, town=[(near.id, 2)], quiet=True)
    from . import tally as TY
    TY.add(game, 'freed')
    return True


# ------------------------------------------------------------------ part 2 while you are there
def tick(game):
    """Each step in a maker's place: the tide in the sea cave, the spores of the fungal deep."""
    m, p = game.map, game.player
    td = getattr(m, 'tidal', None)
    if td:
        from .nature import tide
        lvl = tide(game)
        high = 2 if lvl > .6 else 1 if lvl > .1 else 0
        if high != td['high']:
            was, td['high'] = td['high'], high
            here = p.y * m.w + p.x
            for i in td['low']:
                if m.t[i] in (D.FLOOR, D.SHALLOW):
                    m.t[i] = D.SHALLOW if high else D.FLOOR
            for i in td['sump']:
                if m.t[i] in (D.FLOOR, D.SHALLOW, D.WATER) and i != here:
                    m.t[i] = D.WATER if high == 2 else D.SHALLOW if high else D.FLOOR
            if was is not None:
                game.msg('The tide is coming in: the sea runs into the low caves.' if high > was else
                         'The tide is going out. The low caves drain.', 'info')
    if getattr(m, 'spores', False) and m.tile(p.x, p.y) == D.SHROOM and random.random() < .12:
        from . import behave as BH
        BH.give(game, 'confused', 3, 'A cloud of spores bursts round you. Your head swims.')


def may_enter(game, dg):
    """The drowned village shows only in a dry summer, when the lake draws back."""
    from . import arenas as AR
    if AR.closed(game, dg):
        return False
    if getattr(dg, 'maker', None) != 'drowned':
        return True
    from . import calendar as CAL
    if CAL.season(game.day) == 'summer':
        return True
    game.msg('The lake stands high. Only in a dry summer does it draw back from the roofs of the old village.', 'info')
    return False


def left(game, dg):
    """Out of a maker's place into the daylight: under the fey hill a week went by outside."""
    if getattr(dg, 'maker', None) == 'feyhill':
        game.turn += 7 * D.DAY_LEN
        game.end_turn(0, quiet=True)
        game.msg('The sun stands wrong in the sky. The grass has grown and the leaves have turned: a week has gone by '
                 'out here, though you were under the hill an afternoon.', 'unique')


def arrive(game, dg, depth):
    """A word on coming into a level that is not a stair down."""
    if getattr(dg, 'maker', None) == 'termite' and depth > 1:
        game.msg('You climb higher inside the mound. The air grows warmer.', 'info')


def shaft(game):
    """The open pit of a sinkhole shaft: look down, jump, or go down on a rope."""
    from . import events as EV
    EV.RESOLVERS['shaft'] = r_shaft
    m = game.map
    dg = game.world.dungeons.get(getattr(m, 'did', None))
    left_ = (dg.depth - m.depth) if dg else 0
    rope = any(i.k == 'tool' and i.t == 'rope' for i in game.player.inv)
    EV.ask(game, 'shaft', 'The shaft', 'The pit drops away into the dark. Wind comes up out of it, and far down you '
           'hear water.', [('Look down', 'look'), ('Go down on a rope' if rope else 'Go down on a rope (you have none)',
                                                     'rope' if rope else None),
                           ('Jump', 'jump'), ('Step back', 'bye')], left=left_)


def r_shaft(game, choice, ctx):
    from .worldgen import rand_free
    m = game.map
    if choice == 'look':
        n = ctx.get('left', 0)
        game.msg(f'You lie flat at the rim and look down. You count {n} ledge{"s" if n != 1 else ""} below, and a '
                 'glint of water at the bottom.' if n else 'You look down: only the bottom, wet and dark.', 'info')
        return
    if choice not in ('rope', 'jump'):
        return
    did, depth = m.did, m.depth
    dg = game.world.dungeons[did]
    if depth >= dg.depth:
        return
    if choice == 'rope':
        game.msg('You tie the rope off at the rim and let yourself down, hand over hand, to the next ledge.', 'good')
    else:
        game.msg('You jump. The ledge comes up hard.', 'bad')
        game.hurt(max(4, round(game.stats()['max_life'] * random.uniform(.15, .3))), 'a jump down a shaft')
        if game.dead:
            return
    game.enter_dungeon(did, depth + 1, 'up')
    c = rand_free(game, game.map, lambda t: t == D.FLOOR)
    if c:
        game.player.x, game.player.y = c
        game.compute_fov()



# ------------------------------------------------------------------ part 3: the states and the break-ins (round 52)
STATES = ('lived', 'fallen', 'held', 'overgrown', 'flooded', 'burnt', 'frozen', 'stricken', 'haunted', 'besieged',
          'plundered', 'settled', 'sealed', 'emptied')
# the line on the first step in (level 1), for the states that show
STATE_LINE = {
    'held': 'Others have moved in here: their marks are on the walls, their stink in the air.',
    'overgrown': 'Green has taken the place: grass between the stones, roots through the walls.',
    'flooded': 'Water stands in the low half of the place. You will swim, or find another way.',
    'burnt': 'The place burnt not long ago. The floor is still warm, and smoke hangs under the roof.',
    'frozen': 'Frost lies on everything. The floors are ice, and the dwellers stand frozen where they were.',
    'stricken': 'The doors were nailed shut and marked with a red cross. Sickness was here; stay too long and it '
                'may find you.',
    'haunted': 'It is very still. By day nothing stirs; they say the dead walk here at night.',
    'besieged': 'Besiegers have broken in at the gate. Somewhere deeper, defenders still hold out.',
    'plundered': 'Plunderers are still at work: you hear them breaking chests in the dark.',
    'settled': 'People live here again: fires, washing, children. Refugees, by the look of them.',
    'sealed': 'The dust lies unbroken. Nobody has opened this place since it fell.',
    'emptied': 'Footprints in the dust, and the chests stand open: someone came here before you.',
}
LIVED = {'hideout', 'steading', 'termite', 'feyhill', 'sewer', 'castle', 'maze', 'tidecave', 'lavatube', 'fungal',
         'geode', 'cellar', 'shaft', 'icecave'}
FIXED_STATE = {'icecave': 'frozen', 'drowned': 'flooded', 'burntglade': 'burnt', 'feyhill': 'lived'}
HELD_BY = ('warren', 'lair_orc', 'lair_spider', 'gloam', 'lair_rat')


def states_for(d):
    """The states this place may be in (lived-in places are seldom ruins)."""
    mk = d.maker
    if mk in FIXED_STATE:
        return [FIXED_STATE[mk]]
    if mk in LIVED:
        return ['lived'] * 5 + ['held', 'besieged', 'plundered', 'stricken']
    out = ['fallen'] * 3 + ['held', 'overgrown', 'stricken', 'haunted', 'plundered', 'settled', 'sealed', 'emptied']
    if mk not in ('lavatube',):
        out.append('flooded')
    if mk not in ('tidecave', 'drowned'):
        out.append('burnt')
    if mk in ('fallenhold', 'castle'):
        out.append('besieged')
    return out


def set_states(world, rnd):
    """At world making: each maker's place its state, and the break-ins between neighbours."""
    for d in world.dungeons.values():
        if getattr(d, 'maker', None):
            d.state = rnd.choice(states_for(d)) if not d.boss else 'fallen'     # a fixed boss's place stays as it is
            d.state_day = 1
            if d.state == 'held':
                d.held_by = rnd.choice(HELD_BY)
    mk = [d for d in world.dungeons.values() if getattr(d, 'maker', None)]

    def nearest(d, ok):
        cands = [o for o in world.dungeons.values() if o is not d and ok(o)]
        return min(cands, key=lambda o: cheb(o.x, o.y, d.x, d.y), default=None)
    for d in mk:
        other = None
        if d.maker == 'sewer':
            other = next((o for o in mk if o.maker == 'catacomb' and getattr(o, 'city', -1) == getattr(d, 'city', -2)),
                         None)
        elif d.maker == 'realmine':
            other = nearest(d, lambda o: getattr(o, 'varnish', False) or o.tag == 'deep' and not getattr(o, 'maker', None))
        elif d.maker == 'castle':
            other = nearest(d, lambda o: o.tag == 'crypt')
        elif d.maker == 'shaft':
            other = nearest(d, lambda o: getattr(o, 'maker', None) == 'fungal' or o.tag in ('cave', 'gloam')
                            and not getattr(o, 'maker', None))
        elif d.maker == 'cellar':
            other = nearest(d, lambda o: getattr(o, 'maker', None) in ('sewer', 'catacomb'))
        if other is not None and cheb(other.x, other.y, d.x, d.y) <= 40:
            d.breakin = other.id


def apply_state(game, m, d, depth, up, down):
    """Lay the place's state over a level just made."""
    from .worldgen import spawn_pack, free_around
    from .entities import make_monster, make_npc
    st = getattr(d, 'state', None)
    lvl = d.base + depth
    keep = {up[1] * m.w + up[0], down[1] * m.w + down[0]}
    floor = [i for i, t in enumerate(m.t) if t == D.FLOOR and i not in keep]
    rooms = list(enumerate(m.delve_rooms or []))

    def room_spot(rid):
        cs = [(i % m.w, i // m.w) for i, r in enumerate(m.room_of) if r == rid and m.t[i] == D.FLOOR
              and not m.mon_at(i % m.w, i // m.w)]
        return random.choice(cs) if cs else None
    hostile = [o for o in m.mons if not o.is_npc]
    m.state = st
    if st == 'held':
        for rid, _r in random.sample(rooms, min(2, len(rooms))):
            c = room_spot(rid)
            if c:
                spawn_pack(game, m, lvl, getattr(d, 'held_by', 'warren'), c, None, False)
    elif st == 'overgrown':
        for i in floor:
            r = random.random()
            m.t[i] = D.GRASS if r < .3 else D.SHROOM if r < .34 else m.t[i]
    elif st == 'flooded':
        for i in floor:
            if i // m.w > m.h * .55:
                m.t[i] = D.WATER if i // m.w > m.h * .7 and random.random() < .7 else D.SHALLOW
        from .worldgen import bfs
        dist = bfs(m, up[0], up[1], lambda t: D.TILES[t].walk or D.TILES[t].door)
        if dist[down[1] * m.w + down[0]] < 0:                 # never cut off on foot: the water stays shallow then
            for i in floor:
                if m.t[i] == D.WATER:
                    m.t[i] = D.SHALLOW
    elif st == 'burnt':
        for i in floor:
            r = random.random()
            m.t[i] = D.ASH if r < .4 else m.t[i]
        m.burnt = True
    elif st == 'frozen':
        for i in floor:
            if random.random() < .3:
                m.t[i] = D.SLICK
        m.icecave = True
        for o in hostile:
            o.awake = False
    elif st == 'stricken':
        m.stricken = True
    elif st == 'haunted':
        m.haunted = True
        for o in hostile:
            o.awake = False
    elif st == 'besieged' and depth == 1:
        m.besieged = True
        for _ in range(2):
            c = random.choice(free_around(game, m, up[0], up[1], 6) or [up])
            for _k in range(3):
                spot = free_around(game, m, c[0], c[1], 2)
                if spot:
                    o = make_monster(game, 'bandit', spot[0][0], spot[0][1], lvl + 1)
                    o.name, o.besieger, o.awake = 'Besieger', True, True
                    m.mons.append(o)
        last = max(rooms, key=lambda r: abs(r[1][1] - up[0]) + abs(r[1][2] - up[1]), default=None)
        if last:
            for _k in range(3):
                c = room_spot(last[0])
                if c:
                    n = make_npc(game, 'A defender', 'defender', '#c8c0a0', c[0], c[1], True)
                    n.home_pos = n.work_pos = c
                    m.mons.append(n)
    elif st == 'plundered':
        for i, t in enumerate(m.t):
            if t == D.CHEST and random.random() < .7:
                m.t[i] = D.FLOOR
        for rid, _r in random.sample(rooms, min(2, len(rooms))):
            c = room_spot(rid)
            if c:
                o = make_monster(game, 'bandit', c[0], c[1], lvl)
                o.name = 'Plunderer'
                m.mons.append(o)
    elif st == 'settled':
        near = {up}
        for o in hostile:
            if cheb(o.x, o.y, *up) < 20 or random.random() < .5:
                m.mons.remove(o)
        for k in range(3):
            spot = free_around(game, m, up[0], up[1], 4 + k)
            if spot:
                c = random.choice(spot)
                n = make_npc(game, random.choice(['A refugee', 'A settler', 'A refugee mother', 'An old refugee']),
                             'settler', '#c8b890', c[0], c[1], True)
                n.home_pos = n.work_pos = c
                m.mons.append(n)
                near.add(c)
    elif st == 'sealed':
        if depth == d.depth:
            from .entities import random_gear
            last = max(rooms, key=lambda r: abs(r[1][1] - up[0]) + abs(r[1][2] - up[1]), default=None)
            c = room_spot(last[0]) if last else None
            if c:
                spawn_pack(game, m, lvl + 3, d.tag, c, 1, False)
                game.spill(m, c[0], c[1], random_gear(game, lvl + 3, 2.0))
    elif st == 'emptied':
        for i, t in enumerate(m.t):
            if t == D.CHEST:
                m.t[i] = D.FLOOR
        from .delves import _snares
        _snares(game, m, up, lvl)
    # the break-in: a cracked wall in the last level gives onto the other place
    if getattr(d, 'breakin', None) and depth == d.depth:
        cands = [(i % m.w, i // m.w) for i, t in enumerate(m.t) if t in (D.WALL, D.ROCK) and 0 < i % m.w < m.w - 1
                 and 0 < i // m.w < m.h - 1 and any(m.t[i + o] == D.FLOOR for o in (1, -1, m.w, -m.w))]
        if cands:
            c = max(cands, key=lambda c: abs(c[0] - up[0]) + abs(c[1] - up[1]) - random.random() * 20)
            m.set(c[0], c[1], D.CRACKWALL)
            m.breakin = c


def state_line(game, d):
    st = getattr(d, 'state', None)
    if st in STATE_LINE:
        game.msg(STATE_LINE[st], 'info')


def break_in(game, x, y):
    """Bump the cracked wall at the bottom: through it into the place beyond."""
    m = game.map
    if getattr(m, 'breakin', None) != (x, y):
        return None
    d = game.world.dungeons[m.did]
    other = game.world.dungeons.get(getattr(d, 'breakin', None))
    if other is None:
        return None
    from .worldgen import rand_free
    game.msg(f'You break through the cracked wall and squeeze into the dark beyond: {other.name}.', 'unique')
    game.enter_dungeon(other.id, 1, 'down')
    c = rand_free(game, game.map, lambda t: t == D.FLOOR)
    if c:
        game.player.x, game.player.y = c
    game.compute_fov()
    from . import chronicle as CH
    CH.seen_place(game, f'break:{d.id}', d.name, f'Under {d.name} a wall gives onto {other.name}.', (d.x, d.y))
    return 1


def state_tick(game):
    """Each step in a level with a state that acts: the sickness, the night's dead, the siege broken."""
    m, p = game.map, game.player
    if getattr(m, 'stricken', False) and game.turn % 150 == 0 and random.random() < .25:
        from . import behave as BH
        BH.give(game, 'diseased', random.randint(150, 260), 'The sick air of this place gets into you. (Diseased: no '
                'natural healing)')
    if getattr(m, 'haunted', False) and not getattr(m, 'risen', False):
        from .towns import is_night
        if is_night(game):
            from .worldgen import spawn_pack
            m.risen = True
            spot = (p.x + 4, p.y) if m.inb(p.x + 4, p.y) and D.TILES[m.tile(p.x + 4, p.y)].walk else (p.x, p.y)
            spawn_pack(game, m, m.level + 1, 'crypt', spot, None, True)
            for o in m.mons:
                if not o.is_npc:
                    o.awake = True
            game.msg('Night has fallen outside. All through the place, the dead get up.', 'bad')
    if getattr(m, 'besieged', False) and not any(getattr(o, 'besieger', False) and o.hp > 0 for o in m.mons):
        m.besieged = False
        d = game.world.dungeons[m.did]
        d.state, d.state_day = 'lived', game.day
        near = min(game.world.settlements, key=lambda s: cheb(s.x, s.y, d.x, d.y))
        from . import jobs as JB
        JB.effects(game, town=[(near.id, 2)], quiet=True)
        game.msg('The defenders throw open the inner door. The siege is broken, and they will tell of it in '
                 f'{near.name}.', 'good')


def talk_state(game, npc):
    if npc.role == 'settler':
        game.msg(random.choice(['"We came when the war burnt our village. Nobody else wanted this place."',
                                '"Mind the lower halls. We do not go down there."',
                                '"There is soup, if you have a bowl."']))
        return True
    if npc.role == 'defender':
        game.msg('"Hold the gate with us, or go. We will not leave."' if getattr(game.map, 'besieged', False) else
                 '"You broke them. We will not forget it."')
        return True
    return False


def daily(game):
    """The states shift while you play: a siege falls if nobody comes, plunder grows over, ruins are moved into."""
    w = game.world
    here = game.cur.split(':')[0] if ':' in game.cur else None
    for d in w.dungeons.values():
        st = getattr(d, 'state', None)
        if st is None or d.id == here:
            continue
        new = None
        age = game.day - getattr(d, 'state_day', 1)
        if st == 'besieged' and age > 20:
            new = 'plundered'
        elif st == 'plundered' and age > 60:
            new = 'overgrown'
        elif st == 'fallen' and random.random() < .002:
            new = random.choice(['held', 'settled'])
        if new:
            shift(game, d, new)


def shift(game, d, new):
    d.state, d.state_day = new, game.day
    if new == 'held':
        d.held_by = random.choice(HELD_BY)
    for k in [k for k in game.maps if k.startswith(d.id + ':')]:
        del game.maps[k]                              # made again as it is now, the next time you come
