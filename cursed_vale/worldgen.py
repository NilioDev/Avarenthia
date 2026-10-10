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


def bfs(m, sx, sy, passable):
    """Breadth-first distances (8-way) from (sx, sy). passable(tile_id) -> bool."""
    dist = [-1] * (m.w * m.h)
    s = sy * m.w + sx
    dist[s] = 0
    q = deque([s])
    w, t = m.w, m.t
    while q:
        c = q.popleft()
        x, y = c % w, c // w
        dc = dist[c] + 1
        for dx, dy in D8:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < m.h:
                ni = ny * w + nx
                if dist[ni] == -1 and passable(t[ni]):
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


# ------------------------------------------------------------------ overworld
def gen_over():
    w, h = 80, 40
    for _ in range(30):
        m = GameMap('over', 'over', 'The Vale', w, h, GRASS)
        m.radius = 9
        n1, n2, m1, m2 = noise_grid(w, h, 9), noise_grid(w, h, 4), noise_grid(w, h, 11), noise_grid(w, h, 5)
        H, Mo = [], []
        for y in range(h):
            for x in range(w):
                e = max(abs(x / (w - 1) - .5), abs(y / (h - 1) - .5)) * 2
                H.append(.65 * n1(x, y) + .35 * n2(x, y) + e ** 3 * .9)
                Mo.append(.6 * m1(x, y) + .4 * m2(x, y))
        sH, sM = sorted(H), sorted(Mo)
        qh = lambda p: sH[int(p * (len(sH) - 1))]
        qm = lambda p: sM[int(p * (len(sM) - 1))]
        water, low, mount, forest, wet = qh(.1), qh(.22), qh(.8), qm(.62), qm(.45)
        for i in range(w * h):
            x, y, hv, mo = i % w, i // w, H[i], Mo[i]
            if x in (0, w - 1) or y in (0, h - 1) or hv > mount:
                t = MOUNTAIN
            elif hv < water:
                t = WATER
            elif hv < low and mo > wet:
                t = SWAMP
            elif mo > forest:
                t = FOREST
            else:
                t = GRASS
            m.t[i] = t
        best, bd = None, 1e9
        for y in range(1, h - 1):
            for x in range(1, w - 1):
                if m.tile(x, y) == GRASS:
                    d = math.hypot(x - w / 2, y - h / 2)
                    if d < bd:
                        bd, best = d, (x, y)
        if not best:
            continue
        dist = bfs(m, best[0], best[1], lambda t: D.TILES[t].walk)
        reach = [i for i in range(w * h) if dist[i] > 0]
        if len(reach) < 700:
            continue
        reach.sort(key=lambda i: dist[i])
        xy = lambda i: (i % w, i // w)
        used = set()

        def near_mount(i):
            x, y = xy(i)
            return any(m.inb(x + dx, y + dy) and m.tile(x + dx, y + dy) == MOUNTAIN for dx, dy in D8)

        def choose(lst, fb):
            l2 = [i for i in lst if i not in used]
            r = random.choice(l2) if l2 else fb
            used.add(r)
            return xy(r)

        rat = choose([i for i in reach if 7 <= dist[i] <= 14], reach[int(len(reach) * .15)])
        mc = [i for i in reach if 15 <= dist[i] <= 30 and near_mount(i)] or [i for i in reach if 15 <= dist[i] <= 30]
        mine = choose(mc, reach[int(len(reach) * .5)])
        far = [i for i in reach[int(len(reach) * .85):] if cheb(*xy(i), *mine) >= 8]
        far_wet = [i for i in far if m.t[i] in (SWAMP, FOREST)]
        crypt = choose(far_wet or far, reach[-1])
        m.set(best[0], best[1], TOWN)
        dlocs = {'rat': rat, 'mine': mine, 'crypt': crypt}
        for k, (x, y) in dlocs.items():
            m.set(x, y, ENTR)
        return m, best, dlocs
    raise RuntimeError('World generation failed')


# ------------------------------------------------------------------ town
def gen_town(game):
    m = GameMap('town', 'town', 'Thornfield', 56, 22, GRASS)
    m.radius = 40
    for i in range(len(m.t)):
        if random.random() < .04:
            m.t[i] = TREE
    for x in range(2, 54):
        m.set(x, 10, PATH)
    for y in range(6, 22):
        m.set(28, y, PATH)

    def house(x, y, w, h, dx, dy):
        for yy in range(y - 1, y + h + 1):
            for xx in range(x - 1, x + w + 1):
                if m.inb(xx, yy) and m.tile(xx, yy) == TREE:
                    m.set(xx, yy, GRASS)
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                edge = yy in (y, y + h - 1) or xx in (x, x + w - 1)
                m.set(xx, yy, WALL if edge else FLOOR)
        m.set(dx, dy, DOOR)
        step = -1 if dy > 10 else 1
        yy = dy + step
        while yy != 10:
            m.set(dx, yy, PATH)
            yy += step

    house(5, 2, 13, 6, 11, 7)
    house(37, 2, 13, 6, 43, 7)
    house(5, 13, 11, 6, 10, 13)
    house(19, 13, 7, 5, 22, 13)
    house(36, 13, 12, 6, 41, 13)
    m.set(28, 5, WELL)
    m.portal_pos = (31, 8)
    for y in range(7, 10):
        for x in range(30, 33):
            if m.tile(x, y) == TREE:
                m.set(x, y, GRASS)
    m.mons.append(make_npc(game, 'Dorien the Merchant', 'shop', '#f2c44a', 11, 4, True))
    m.mons.append(make_npc(game, 'Sister Ilse', 'healer', '#f4f0e6', 43, 4, True))
    m.mons.append(make_npc(game, 'Elder Berend', 'elder', '#c08cf0', 10, 16, True))
    for _ in range(4):
        c = rand_free(game, m, lambda t: t in (GRASS, PATH))
        if c:
            m.mons.append(make_npc(game, 'A villager', 'villager', '#9aa0aa', c[0], c[1], False))
    c = rand_free(game, m, lambda t: t == GRASS)
    if c:
        m.mons.append(make_npc(game, 'The village dog', 'dog', '#c8a070', c[0], c[1], False, ch='d'))
    m.entry = (28, 21)
    for i in range(len(m.seen)):
        m.seen[i] = 1
    return m


# ------------------------------------------------------------------ dungeons
def gen_rooms(m):
    rooms = []
    for _ in range(400):
        if len(rooms) >= 11:
            break
        rw, rh = random.randint(5, 12), random.randint(3, 6)
        x, y = random.randint(2, m.w - rw - 3), random.randint(2, m.h - rh - 3)
        if any(x - 2 < r[0] + r[2] and x + rw + 2 > r[0] and y - 2 < r[1] + r[3] and y + rh + 2 > r[1] for r in rooms):
            continue
        rooms.append((x, y, rw, rh))
    for x0, y0, rw, rh in rooms:
        for yy in range(y0, y0 + rh):
            for xx in range(x0, x0 + rw):
                m.set(xx, yy, FLOOR)
    rooms.sort(key=lambda r: r[0])
    c = lambda r: (r[0] + r[2] // 2, r[1] + r[3] // 2)

    def hl(x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if m.tile(x, y) == WALL:
                m.set(x, y, FLOOR)

    def vl(y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if m.tile(x, y) == WALL:
                m.set(x, y, FLOOR)

    def tunnel(a, b):
        (x1, y1), (x2, y2) = c(a), c(b)
        if random.random() < .5:
            hl(x1, x2, y1)
            vl(y1, y2, x2)
        else:
            vl(y1, y2, x1)
            hl(x1, x2, y2)

    for i in range(len(rooms) - 1):
        tunnel(rooms[i], rooms[i + 1])
    for _ in range(2):
        tunnel(random.choice(rooms), random.choice(rooms))
    for x0, y0, rw, rh in rooms:
        cand = []
        for yy in range(y0, y0 + rh):
            cand += [(x0 - 1, yy, 'v'), (x0 + rw, yy, 'v')]
        for xx in range(x0, x0 + rw):
            cand += [(xx, y0 - 1, 'h'), (xx, y0 + rh, 'h')]
        for x, y, o in cand:
            if m.tile(x, y) != FLOOR:
                continue
            if o == 'v':
                ok = m.tile(x, y - 1) == WALL and m.tile(x, y + 1) == WALL
            else:
                ok = m.tile(x - 1, y) == WALL and m.tile(x + 1, y) == WALL
            if ok and random.random() < .45:
                m.set(x, y, DOOR)
    return [c(r) for r in rooms]


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
    weights = [3 if D.MONSTERS[k]['min_l'] >= lvl - 2 else 1 for k in c]
    return random.choices(c, weights)[0]


def spawn_pack(game, m, lvl, tag, center, elite=None, awake=False):
    k = choose_monster(lvl, tag)
    pid = game.new_id()
    big = D.MONSTERS[k]['hp'] >= 2
    if elite is None:
        r = random.random()
        elite = 2 if r < .07 else 1 if r < .19 else 0
    size = random.randint(2, 4) if elite == 1 else random.randint(1, 2) if big else random.randint(2, 5)

    def add(mon):
        mon.pack, mon.awake = pid, awake
        m.mons.append(mon)

    if elite == 2:
        add(make_monster(game, k, center[0], center[1], lvl + 1, 2))
        size = random.randint(2, 4)
    spots = free_around(game, m, center[0], center[1], 3)
    if elite != 2:
        spots.insert(0, center)
    for i in range(min(size, len(spots))):
        add(make_monster(game, k, spots[i][0], spots[i][1], lvl + (1 if random.random() < .3 else 0), 1 if elite == 1 else 0))
    return elite > 0


def gen_dungeon(game, did, depth):
    d = D.DUNGEONS[did]
    lvl = d['base'] + depth
    last = depth == d['depth']
    m = GameMap(f'{did}:{depth}', 'dungeon', d['name'], 70, 28, ROCK if d['style'] == 'cave' else WALL)
    m.did, m.depth, m.level, m.radius, m.wall_fg = did, depth, lvl, 7, d['wall']
    if d['style'] == 'cave':
        gen_cave(m)
        floors = [i for i, t in enumerate(m.t) if t == FLOOR]
        s = random.choice(floors)
        up = (s % m.w, s // m.w)
        dist = bfs(m, up[0], up[1], lambda t: D.TILES[t].walk or D.TILES[t].door)
        bi = max(floors, key=lambda i: dist[i])
        far = (bi % m.w, bi // m.w)
    else:
        centers = gen_rooms(m)
        up, far = centers[0], centers[-1]
    m.set(up[0], up[1], UP)
    if last:
        m.mons.append(make_monster(game, d['boss'], far[0], far[1], lvl))
    else:
        m.set(far[0], far[1], DOWN)
    npacks = 4 + depth + random.randint(0, 1)
    elites = 0
    for i in range(npacks):
        c = rand_free(game, m, lambda t: t == FLOOR, (up[0], up[1], 9))
        if not c:
            continue
        el = None
        if i == npacks - 1 and depth >= 2 and not elites:
            el = 2 if random.random() < .5 else 1
        if spawn_pack(game, m, lvl, d['tag'], c, el, False):
            elites += 1
    for _ in range(1 + random.randint(0, 2)):
        c = rand_free(game, m, lambda t: t == FLOOR)
        if c:
            it = random_gear(game, lvl)
            it.x, it.y = c
            m.items.append(it)
    for _ in range(2 + random.randint(0, 2)):
        c = rand_free(game, m, lambda t: t == FLOOR)
        if c:
            it = Item(game.new_id(), 'gold', 'gold', random.randint(lvl * 3, lvl * 9 + 10))
            it.x, it.y = c
            m.items.append(it)
    for _ in range(random.randint(1, 2)):
        c = rand_free(game, m, lambda t: t == FLOOR)
        if c:
            it = Item(game.new_id(), 'potion', 'hp' if random.random() < .65 else 'mp')
            it.x, it.y = c
            m.items.append(it)
    return m


def gen_wild(game, terrain, danger):
    m = GameMap('wild', 'wild', 'Wilderness', 48, 20, SWAMP if terrain == SWAMP else GRASS)
    m.radius, m.level = 11, danger
    dens = .24 if terrain == FOREST else .06
    for i in range(len(m.t)):
        if terrain == SWAMP:
            if random.random() < .12:
                m.t[i] = WATER
            elif random.random() < .05:
                m.t[i] = TREE
        elif random.random() < dens:
            m.t[i] = TREE
    cx, cy = 24, 10
    for y in range(cy - 2, cy + 3):
        for x in range(cx - 2, cx + 3):
            m.set(x, y, SWAMP if terrain == SWAMP else GRASS)
    c = rand_free(game, m, lambda t: D.TILES[t].walk, (cx, cy, 7))
    if c:
        spawn_pack(game, m, danger, 'wild', c, None, True)
    if random.random() < .4:
        c2 = rand_free(game, m, lambda t: D.TILES[t].walk)
        if c2:
            it = Item(game.new_id(), 'gold', 'gold', random.randint(danger * 4, danger * 10 + 10))
            it.x, it.y = c2
            m.items.append(it)
    m.entry = (cx, cy)
    return m


def gen_shop(game):
    lvl = max(1, game.player.lvl)
    ks = [k for k, b in D.BASES.items() if b['lvl'] <= lvl + 2]
    return [make_gear(game, random.choice(ks), 'magic' if random.random() < .35 else 'normal', lvl) for _ in range(8)]
