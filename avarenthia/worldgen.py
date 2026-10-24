"""Procedural generation: the vale, Thornfield, dungeons and wilderness encounters."""
import math
import random
from collections import deque

from . import data as D
from .data import (WALL, FLOOR, DOOR, DOWN, UP, WATER, GRASS, FOREST, MOUNTAIN, SWAMP, TOWN, ENTR, TREE, PATH, WELL, ROCK)
from .entities import GameMap, make_monster, make_npc, random_gear, make_gear, Item

D8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]


def cheb(ax, ay, bx, by):
    return max(abs(ax - bx), abs(ay - by))


def bfs(m, sx, sy, passable, maxd=None):
    """Breadth-first distances (8-way) from (sx, sy). passable(tile_id) -> bool. With maxd, cells further
    than that stay at -1 (much faster on the big maps)."""
    ok = [bool(passable(k)) for k in range(len(D.TILES))]
    dist = [-1] * (m.w * m.h)
    s = sy * m.w + sx
    dist[s] = 0
    q = deque([s])
    w, h, t = m.w, m.h, m.t
    lim = maxd if maxd is not None else 1 << 30
    while q:
        c = q.popleft()
        dc = dist[c] + 1
        if dc > lim:
            continue
        x, y = c % w, c // w
        for dx, dy in D8:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                ni = ny * w + nx
                if dist[ni] == -1 and ok[t[ni]]:
                    dist[ni] = dc
                    q.append(ni)
    return dist


def noise_grid(w, h, s):
    gw = math.ceil(w / s) + 2
    g = [random.random() for _ in range(gw * (math.ceil(h / s) + 2))]

    def f(x, y):
        fx, fy = x / s, y / s
        ix, iy = int(fx), int(fy)
        tx, ty = fx - ix, fy - iy
        sx, sy = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
        a, b = g[iy * gw + ix], g[iy * gw + ix + 1]
        c, d = g[(iy + 1) * gw + ix], g[(iy + 1) * gw + ix + 1]
        return a + (b - a) * sx + (c - a) * sy + (a - b - c + d) * sx * sy
    return f


def occupied(game, m, x, y):
    p = game.player
    if game.cur == m.key and p.x == x and p.y == y:
        return True
    if (x, y) in getattr(m, 'warded', ()):          # a sanctuary: nothing of the dark steps in (themes.py)
        return True
    return m.mon_at(x, y) is not None


def rand_free(game, m, pred, min_from=None):
    for _ in range(3000):
        x, y = random.randint(0, m.w - 1), random.randint(0, m.h - 1)
        if not pred(m.tile(x, y)) or occupied(game, m, x, y):
            continue
        if min_from and cheb(x, y, min_from[0], min_from[1]) < min_from[2]:
            continue
        return x, y
    return None


def free_around(game, m, x, y, r):
    out = []
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            nx, ny = x + dx, y + dy
            if (dx or dy) and m.inb(nx, ny) and D.TILES[m.tile(nx, ny)].walk and not occupied(game, m, nx, ny):
                out.append((nx, ny))
    out.sort(key=lambda c: cheb(c[0], c[1], x, y))
    return out


# ------------------------------------------------------------------ dungeons
def gen_cave(m):
    w, h = m.w, m.h
    for _ in range(40):
        t = [ROCK if (x in (0, w - 1) or y in (0, h - 1) or random.random() < .45) else FLOOR
             for y in range(h) for x in range(w)]
        for _ in range(5):
            n = t[:]
            for y in range(1, h - 1):
                for x in range(1, w - 1):
                    c = 0
                    for dy in (-1, 0, 1):
                        row = (y + dy) * w + x
                        c += (t[row - 1] == ROCK) + (t[row] == ROCK) + (t[row + 1] == ROCK)
                    n[y * w + x] = ROCK if c >= 5 else FLOOR
            t = n
        region = [-1] * (w * h)
        best_id, best_n, rid = -1, 0, 0
        for i in range(w * h):
            if t[i] != FLOOR or region[i] != -1:
                continue
            q = deque([i])
            region[i] = rid
            size = 0
            while q:
                cc = q.popleft()
                size += 1
                x, y = cc % w, cc // w
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ni = (y + dy) * w + x + dx
                    if t[ni] == FLOOR and region[ni] == -1:
                        region[ni] = rid
                        q.append(ni)
            if size > best_n:
                best_n, best_id = size, rid
            rid += 1
        if best_n < w * h * .33:
            continue
        for i in range(w * h):
            if t[i] == FLOOR and region[i] != best_id:
                t[i] = ROCK
        m.t = t
        return True
    return False


def choose_monster(lvl, tag):
    c = [k for k, d in D.MONSTERS.items() if not d['boss'] and tag in d['tags'].split() and lvl - 6 <= d['min_l'] <= lvl]
    if not c:
        c = [k for k, d in D.MONSTERS.items() if not d['boss'] and tag in d['tags'].split()]
    weights = [(3 if D.MONSTERS[k]['min_l'] >= lvl - 2 else 1) * (.25 if D.MONSTERS[k]['chief'] else 1) for k in c]
    return random.choices(c, weights)[0]


def band_keys(k, n):
    """A pack led by a k: the others come from its band (goblins bring archers and a shaman), never a second chief;
    ants and wasps come in hordes."""
    from .creatures import BANDS, HORDE
    if k in HORDE:
        n = random.randint(*HORDE[k])
    pool = BANDS.get(k)
    if not pool:
        return [k] * (1 if D.MONSTERS[k].get('chief') else n)
    return [k] + [random.choice(pool) for _ in range(n - 1)]


def spawn_pack(game, m, lvl, tag, center, elite=None, awake=False):
    k = choose_monster(lvl, tag)
    pid = game.new_id()
    big = D.MONSTERS[k]['hp'] >= 2
    if elite is None:
        r = random.random()
        elite = 2 if r < .07 else 1 if r < .19 else 0
    size = random.randint(2, 4) if elite == 1 else random.randint(1, 2) if big else random.randint(2, 5)
    if tag == 'den':                    # the first dungeon: lone kobolds and pairs, never a mob
        elite, size = 0, random.choices([1, 2], [3, 2])[0]

    def add(mon):
        mon.pack, mon.awake = pid, awake
        m.mons.append(mon)

    keys = band_keys(k, size) if tag != 'den' else [k] * size
    if elite == 2:
        add(make_monster(game, k, center[0], center[1], lvl + 1, 2))
        keys = band_keys(k, random.randint(3, 5))[1:]
    spots = free_around(game, m, center[0], center[1], 3)
    if elite != 2:
        spots.insert(0, center)
    for i in range(min(len(keys), len(spots))):
        el = 1 if elite == 1 and not D.MONSTERS[keys[i]].get('chief') else 0
        add(make_monster(game, keys[i], spots[i][0], spots[i][1], lvl + (1 if random.random() < .3 else 0), el))
    return elite > 0


def gen_k5(m):
    """A classic dungeon level from the K5 maker (k5.py): rooms of many shapes, main and narrow ways, lakes, and
    2 or 3 theme rooms drawn as pieces (pieces.py, themes.py). Keeps on the map which room each cell belongs to
    (m.room_of, m.rooms) for the mood lines and theme rooms. Returns where the stairs up and down go."""
    from . import k5
    from . import pieces as PC
    from . import themes as TH
    from . import underground as UG
    tag, depth = getattr(m, 'dtag', 'crypt'), getattr(m, 'depth', 1) or 1
    n = random.choice((2, 2, 3)) if m.w >= 100 else 1
    themes = [(pc, PC.drawn(pc)) for pc in PC.pick('middle', tag, depth, n)]
    arr = PC.pick('arrival', tag, depth, 1) if random.random() < .3 else []
    low = PC.pick('bottom', tag, depth, 1) if getattr(m, 'last', False) and random.random() < .6 else []
    plan = k5.make(m.w, m.h, themes=themes, arrival=(arr[0], PC.drawn(arr[0])) if arr else None,
                   bottom=(low[0], PC.drawn(low[0])) if low else None)
    cells = {'room': FLOOR, 'cave': FLOOR, 'hall': FLOOR, 'rubble': FLOOR, 'water': WATER, 'shallow': D.SHALLOW}
    for (x, y), k in plan.floor.items():
        m.set(x, y, cells[k])
    for x, y in plan.doors:
        m.set(x, y, DOOR)
    m.room_of = bytearray(b'\xff') * (m.w * m.h)
    m.rooms = []
    m.made = random.getrandbits(40)                 # which level this is, for the rooms you have seen
    room_ids, piece_of, gates = {}, {}, []
    for r in plan.rooms:
        if r.kind == 'hall' or not r.cells or len(m.rooms) >= 250:
            continue
        rid = len(m.rooms)
        m.rooms.append([r.shape, r.kind, None])      # shape, kind, theme (filled in by the theme rooms)
        for x, y in r.cells:
            m.room_of[y * m.w + x] = rid
            room_ids[(x, y)] = rid
        if r.theme:
            pc = PC.by_name(r.theme)
            piece_of[rid] = pc
            if pc.part == 'middle':
                gates.append((rid, pc.gate))
    TH.lay(m, plan, room_ids, piece_of)
    for rid, kind in gates:
        TH.gate(m, rid, kind)
    m.k5_rubble = [y * m.w + x for (x, y), k in plan.floor.items() if k == 'rubble']
    m.k5_themes = [m.room_of[c[1] * m.w + c[0]] for r in plan.themes for c in [next(iter(r.cells))]
                   if m.room_of[c[1] * m.w + c[0]] != 255]
    m.mood = plan.mood
    if m.w >= 120 and random.random() < UG.CHANCE:          # a river of water or fire runs through
        UG.add_river(m, depth, (plan.up, plan.down))
    return plan.up, plan.down


def gen_dungeon(game, did, depth):
    from . import k5
    d = game.world.dungeons[did]
    lvl = d.base + depth
    last = depth == d.depth
    dw, dh = k5.SIZES['small' if d.tag == 'den' else 'large']
    m = GameMap(f'{did}:{depth}', 'dungeon', d.name, dw, dh, ROCK if d.style == 'cave' else WALL)
    m.did, m.depth, m.level, m.radius, m.wall_fg = did, depth, lvl, 7, d.wall
    m.dtag, m.last = d.tag, last
    m.mine_rock = d.tag == 'deep' or did == 'mine'           # now and then a glint of ore in the rock
    if d.style == 'cave':
        gen_cave(m)
        floors = [i for i, t in enumerate(m.t) if t == FLOOR]
        s = random.choice(floors)
        up = (s % m.w, s // m.w)
        dist = bfs(m, up[0], up[1], lambda t: D.TILES[t].walk or D.TILES[t].door)
        bi = max(floors, key=lambda i: dist[i])
        far = (bi % m.w, bi // m.w)
    else:
        up, far = gen_k5(m)
    m.set(up[0], up[1], UP)
    if not last:
        m.set(far[0], far[1], DOWN)
    from .dress import dress
    dress(game, m, d)
    if m.tile(*far) not in (D.FLOOR, DOWN):
        m.set(far[0], far[1], D.FLOOR if last else DOWN)
    if last:
        if d.boss:
            m.mons.append(make_monster(game, d.boss, far[0], far[1], lvl))
        else:
            spawn_pack(game, m, lvl + 1, d.tag, far, 2, False)
    npacks = round((4 + depth + random.randint(0, 1)) * 1.5 * (m.w * m.h / 4200) ** .5)     # bigger levels, a few more
    if d.tag == 'den':
        npacks = 5                      # the first fight should teach, not punish (packs of one or two)
    elites = 0
    for i in range(npacks):
        c = rand_free(game, m, lambda t: t == FLOOR, (up[0], up[1], 9))
        if not c:
            continue
        el = None
        if i == npacks - 1 and depth >= 2 and not elites:
            el = 2 if random.random() < .5 else 1
        tag = 'vault' if getattr(d, 'varnish', False) and random.random() < .4 else d.tag     # what the Varnish left on guard
        if spawn_pack(game, m, lvl, tag, c, el, False):
            elites += 1
    for _ in range(random.randint(0, 1)):
        c = rand_free(game, m, lambda t: t == FLOOR)
        if c:
            it = random_gear(game, lvl)
            it.x, it.y = c
            m.items.append(it)
    # coins are rare: now and then a few on the floor, sometimes a treasure chest
    if random.random() < .25:
        c = rand_free(game, m, lambda t: t == FLOOR)
        if c:
            from .money import purse
            it = Item(game.new_id(), 'gold', 'gold', purse(lvl, .5))
            it.x, it.y = c
            m.items.append(it)
    if last or random.random() < .4:
        place_chest(m)
    for _ in range(random.randint(1, 2)):
        c = rand_free(game, m, lambda t: t == FLOOR)
        if c:
            it = Item(game.new_id(), 'potion', 'hp' if random.random() < .65 else 'mp')
            it.x, it.y = c
            m.items.append(it)
    if getattr(m, 'things', None) is not None:
        from . import themes as TH
        TH.setup(game, m, lvl)
    return m


def place_chest(m):
    """A treasure chest against a wall."""
    cands = [i for i, t in enumerate(m.t) if t == FLOOR and 0 < i % m.w < m.w - 1 and sum(
        1 for o in (1, -1, m.w, -m.w) if 0 <= i + o < len(m.t) and m.t[i + o] in (WALL, ROCK)) == 1]
    if not cands:
        return None
    i = random.choice(cands)
    m.set(i % m.w, i // m.w, D.CHEST)
    return i


def open_chest(game, x, y):
    """Open a chest: coins, gear and sometimes a tome or a potion spill out."""
    from .money import purse
    from .entities import make_tome
    m = game.map
    m.set(x, y, D.CHEST_OPEN)
    lvl = getattr(m, 'level', 1)
    game.spill(m, x, y, Item(game.new_id(), 'gold', 'gold', purse(lvl, 6)))
    if random.random() < .7:
        game.spill(m, x, y, random_gear(game, lvl + 1, 1.5))
    if random.random() < .2:
        game.spill(m, x, y, make_tome(game, lvl))
    dg = game.world.dungeons.get(getattr(m, 'did', None))
    if getattr(dg, 'poi', False) and random.random() < .2:       # ruins keep old maps
        from .hidden import make_map_item
        game.spill(m, x, y, make_map_item(game))
    if random.random() < .5:
        game.spill(m, x, y, Item(game.new_id(), 'potion', random.choice(['hp', 'hp', 'mp', 'rejuv'])))
    if (getattr(dg, 'poi', False) or m.kind in ('siege', 'town')) and random.random() < .04:   # an old ruin, a castle kitchen
        from .cooking import cookbook
        book = cookbook(game)
        if book:
            game.spill(m, x, y, book)
    game.msg('You open the chest. Treasure!', 'gold')


def gen_wild(game, terrain, lvl, keys, elite=0, leader=None, faction=None):
    """A small battle map for an overworld encounter. keys lists the monster type of each enemy."""
    base = {SWAMP: SWAMP, D.SAND: D.SAND}.get(terrain, GRASS)
    m = GameMap('wild', 'wild', 'Wilderness', 80, 51, base)
    m.radius, m.level = 11, lvl
    for i in range(len(m.t)):
        r = random.random()
        if terrain == SWAMP:
            if r < .12:
                m.t[i] = WATER
            elif r < .17:
                m.t[i] = TREE
        elif terrain == FOREST:
            if r < .24:
                m.t[i] = TREE
        elif terrain == D.HILLS:
            if r < .1:
                m.t[i] = ROCK
            elif r < .13:
                m.t[i] = TREE
        elif terrain == D.SAND:
            if r < .06:
                m.t[i] = WATER
        elif r < .05:
            m.t[i] = TREE
    cx, cy = m.w // 2, m.h // 2
    for y in range(cy - 2, cy + 3):
        for x in range(cx - 2, cx + 3):
            m.set(x, y, base)
    c = rand_free(game, m, lambda t: D.TILES[t].walk, (cx, cy, 7))
    if c and keys:
        pid = game.new_id()
        spots = [c] + free_around(game, m, c[0], c[1], 3)
        for i, k in enumerate(keys):
            if i >= len(spots):
                break
            el = 2 if (elite == 2 and i == 0) else (1 if elite == 1 else 0)
            mon = make_monster(game, k, spots[i][0], spots[i][1], lvl + (1 if random.random() < .3 else 0), el)
            if el == 2 and leader:
                mon.name = leader
            mon.pack, mon.awake = pid, True
            mon.faction = faction
            m.mons.append(mon)
    m.entry = (cx, cy)
    return m


def gen_shop(game, city=False):
    lvl = max(1, game.player.lvl) + (1 if city else 0)
    ks = [k for k, b in D.BASES.items() if b['lvl'] <= lvl + 2]
    stock = [make_gear(game, random.choice(ks), 'magic' if random.random() < .06 else 'normal', lvl) for _ in range(8)]
    if city and random.random() < .5:
        from .entities import make_tome
        stock.append(make_tome(game, 0))
    return stock
