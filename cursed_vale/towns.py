"""Villages, cities and strongholds that feel lived in: furnished buildings, fields and market
stalls, and townsfolk who go to work by day and home at night."""
import random
from collections import deque

from . import data as D
from .data import (WALL, FLOOR, DOOR, ODOOR, GRASS, TREE, PATH, WELL, FIELD, FENCE, TABLE, BED, STALL, FOUNTAIN,
                   ANVIL, ALTAR, BARREL, PLANK, ROCK)
from .entities import GameMap, make_npc, make_monster
from .worldgen import cheb, rand_free

NAMES = ['Dorien', 'Ilse', 'Berend', 'Maud', 'Aldric', 'Petra', 'Hob', 'Wenna', 'Garrick', 'Tamsin', 'Osric', 'Lyra',
         'Bram', 'Edda', 'Corwin', 'Nell', 'Fenwick', 'Rowan', 'Sabine', 'Tobin', 'Agnes', 'Merrit', 'Jory', 'Hilde',
         'Alwin', 'Bess', 'Cuthbert', 'Dunstan', 'Elsa', 'Gilles', 'Hester', 'Ivo', 'Jessamy', 'Kit', 'Leofric', 'Mabel']


def town_names(race):
    from .races import names_for
    names = names_for(race, 40)
    random.shuffle(names)
    return names


JOBS = ['farmer', 'farmer', 'baker', 'weaver', 'woodcutter', 'fisher', 'tanner', 'carter', 'cooper', 'miller', 'potter']
BARKS = {
    'shepherd': ['Come by, come by! Daft animals.', 'Wolves took two lambs last week.', 'Mind the gate, stranger.'],
    'acolyte': ['The light keeps us.', 'Have you prayed today, traveller?'],
    'monk': ['Silence is a prayer too.', 'The herb garden needs weeding again.'],
    'farmer': ['Rain is coming, I can smell it.', 'These turnips won\'t dig themselves.', 'The crows took half the seed again.'],
    'baker': ['Fresh bread! Still warm!', 'Mind the flour, love.'],
    'weaver': ['Finest cloth this side of the river.', 'My loom has been clacking since dawn.'],
    'woodcutter': ['Wolves in the deep woods again.', 'My back aches like an old cart.'],
    'fisher': ['The nets came up empty this morning.', 'Smells like a storm out on the water.'],
    'guard': ['Move along.', 'Keep your blade sheathed in town.', 'Quiet night. I like quiet nights.'],
    'child': ['Are you an adventurer? Have you killed a dragon?', 'Tag! You\'re it!', 'Mum says I can\'t go past the fence.'],
    'drinker': ['Another round!', 'I tell you, I saw a ghost on the old road.', 'Hic.'],
    'any': ['Lovely day, isn\'t it?', 'Prices keep going up, I swear.', 'Did you hear about the bandits on the east road?',
            'Mind how you go.', 'The temple bell woke me again.'],
}

DAY_START, DAY_END = 6, 20


def hour(game):
    return (game.turn % D.DAY_LEN) * 24 // D.DAY_LEN


def is_night(game):
    h = hour(game)
    return h >= 21 or h < 5


# ------------------------------------------------------------------ building blocks
class Plot:
    def __init__(self, x, y, w, h, kind):
        self.x, self.y, self.w, self.h, self.kind = x, y, w, h, kind
        self.door = None
        self.inside = []

    def overlaps(self, o, gap=2):
        return not (self.x + self.w + gap <= o.x or o.x + o.w + gap <= self.x or
                    self.y + self.h + gap <= o.y or o.y + o.h + gap <= self.y)


def build(m, pl, wall=WALL, floor=FLOOR):
    for yy in range(pl.y, pl.y + pl.h):
        for xx in range(pl.x, pl.x + pl.w):
            edge = yy in (pl.y, pl.y + pl.h - 1) or xx in (pl.x, pl.x + pl.w - 1)
            m.set(xx, yy, wall if edge else floor)
    pl.inside = [(xx, yy) for yy in range(pl.y + 1, pl.y + pl.h - 1) for xx in range(pl.x + 1, pl.x + pl.w - 1)]


def place_door(m, pl, tx, ty):
    """Put a door in the wall facing (tx, ty)."""
    cx, cy = pl.x + pl.w // 2, pl.y + pl.h // 2
    if abs(ty - cy) * pl.w >= abs(tx - cx) * pl.h:
        y = pl.y + pl.h - 1 if ty > cy else pl.y
        x = min(max(pl.x + 1, tx), pl.x + pl.w - 2)
        out = (x, y + (1 if ty > cy else -1))
    else:
        x = pl.x + pl.w - 1 if tx > cx else pl.x
        y = min(max(pl.y + 1, ty), pl.y + pl.h - 2)
        out = (x + (1 if tx > cx else -1), y)
    m.set(x, y, DOOR)
    pl.door = (x, y)
    return out


def carve_path(m, a, b, avoid_walls=True):
    x, y = a
    for _ in range(400):
        if (x, y) == b:
            return
        if m.inb(x, y) and m.tile(x, y) in (GRASS, TREE, FIELD):
            m.set(x, y, PATH)
        dx = (b[0] > x) - (b[0] < x)
        dy = (b[1] > y) - (b[1] < y)
        for nx, ny in ((x + dx, y), (x, y + dy), (x + dx, y + dy), (x - dy, y + dx)):
            if (nx, ny) != (x, y) and m.inb(nx, ny) and m.tile(nx, ny) in (GRASS, TREE, FIELD, PATH, FLOOR, ODOOR):
                x, y = nx, ny
                break
        else:
            return


def free_inside(m, pl, pred=lambda t: t in (FLOOR, PLANK)):
    cells = [c for c in pl.inside if pred(m.tile(*c)) and not m.mon_at(*c)]
    random.shuffle(cells)
    return cells


def furnish(m, pl):
    k = pl.kind
    floor = PLANK if k in ('inn', 'home', 'shop', 'stables', 'elder', 'barracks') else FLOOR
    for c in pl.inside:
        m.set(c[0], c[1], floor)
    ix0, iy0, ix1, iy1 = pl.x + 1, pl.y + 1, pl.x + pl.w - 2, pl.y + pl.h - 2
    door = pl.door
    near_door = lambda c: door and cheb(c[0], c[1], door[0], door[1]) <= 1

    def put(c, t):
        if not near_door(c) and m.tile(*c) in (FLOOR, PLANK):
            m.set(c[0], c[1], t)

    if k == 'inn':
        for xx in range(ix0 + 1, ix1):
            put((xx, iy0 + 1), STALL)
        for _ in range(max(2, pl.w * pl.h // 16)):
            c = (random.randint(ix0 + 1, ix1 - 1), random.randint(iy0 + 3, iy1))
            put(c, TABLE)
        put((ix0, iy0), BARREL)
        put((ix1, iy0), BARREL)
    elif k == 'temple':
        put(((ix0 + ix1) // 2, iy0), ALTAR)
        for yy in range(iy0 + 2, iy1, 2):
            for xx in range(ix0 + 1, ix1):
                if xx != (ix0 + ix1) // 2:
                    put((xx, yy), TABLE)
    elif k == 'shop':
        for xx in range(ix0 + 1, ix1):
            put((xx, iy0 + 1), STALL)
        put((ix0, iy1), ANVIL)
        put((ix1, iy1), BARREL)
        put((ix1, iy0), BARREL)
    elif k == 'stables':
        for c in pl.inside:
            if random.random() < .4:
                m.set(c[0], c[1], FIELD)
    elif k in ('home', 'elder'):
        put((ix0, iy0), BED)
        if pl.w > 6:
            put((ix1, iy0), BED)
        put(((ix0 + ix1) // 2, (iy0 + iy1) // 2), TABLE)
        put((ix1, iy1), BARREL)
    elif k == 'barracks':
        for xx in range(ix0, ix1 + 1, 2):
            put((xx, iy0), BED)
        put((ix1, iy1), BARREL)
    elif k == 'keep':
        for xx in range(ix0 + 2, ix1 - 1):
            put((xx, (iy0 + iy1) // 2), TABLE)
        put(((ix0 + ix1) // 2, iy0), ALTAR)


ROLE_OF = {'inn': 'inn', 'market': 'market', 'shop': 'shop', 'temple': 'healer', 'stables': 'stables', 'elder': 'elder'}
SIGN = {'inn': 'INN', 'shop': 'OUTFITTER', 'temple': 'TEMPLE', 'stables': 'STABLES', 'elder': 'ELDER', 'keep': 'KEEP',
        'barracks': 'BARRACKS'}
TITLE = {'inn': ('Innkeeper {n}', '#e0a060'), 'market': ('{n} the Trader', '#f2c44a'), 'shop': ('{n} the Outfitter', '#d8d0b0'),
         'temple': ('Sister {n}', '#f4f0e6'), 'stables': ('Stablemaster {n}', '#c8a070'), 'elder': ('Elder Berend Ashford', '#c08cf0')}


def add_sign(m, pl, text):
    if not pl.door:
        return
    dx, dy = pl.door
    if dy == pl.y + pl.h - 1:
        sy = dy + 1
    elif dy == pl.y:
        sy = dy - 1
    else:
        sy = pl.y - 1
    m.signs.append((max(0, dx - len(text) // 2), sy, text))


def staff(game, m, pl, role_key, names, s):
    """Put the person who runs a building behind its counter."""
    nm, col = TITLE[role_key]
    label = nm.format(n=names.pop())
    if s is not None and s.id == 0 and role_key == 'shop':
        label = 'Dorien Hale the Merchant'
    if s is not None and s.id == 0 and role_key == 'temple':
        label = 'Sister Ilse Marsh'
    spots = free_inside(m, pl)
    if role_key in ('inn', 'shop'):
        spots = [c for c in spots if c[1] == pl.y + 1] or spots
    if role_key == 'temple':
        spots = [c for c in spots if c[1] == pl.y + 2] or spots
    if not spots:
        return None
    c = spots[0]
    npc = make_npc(game, label, ROLE_OF[role_key], col, c[0], c[1], True)
    m.mons.append(npc)
    return npc


def townsfolk(game, m, home, work, names, job=None, fg='#a8aab4', ch='@', role='villager'):
    c = random.choice(home) if home else work
    n = make_npc(game, f'{names.pop() if names else "A local"}' + (f' the {job}' if job and job not in ('child',) else ''),
                 role, fg, c[0], c[1], False, ch=ch)
    if job == 'child':
        n.name = 'A child'
    n.home_pos = c
    n.work_pos = work
    n.job = job or 'any'
    n.path = []
    m.mons.append(n)
    return n


# ------------------------------------------------------------------ villages
LIVESTOCK = [('A cow', 'C', '#d8c8b0'), ('A sheep', 's', '#f0f0f0'), ('A pig', 'p', '#f0a8a8'), ('A goat', 'g', '#c8b890'),
             ('A hen', 'c', '#e8d090')]


def farmland(game, m, plots, sy, names, avoid=None):
    """Fields of crops, fenced pastures with livestock and orchards around a village."""
    w, h = m.w, m.h
    fields, pastures = [], []
    want = [('field', 9), ('pasture', 3), ('orchard', 2)]
    for kind, n in want:
        made = 0
        for _ in range(400):
            if made >= n:
                break
            fw, fh = (random.randint(9, 16), random.randint(4, 7)) if kind == 'field' else (random.randint(8, 13), random.randint(5, 7))
            fx, fy = random.randint(1, w - fw - 2), random.randint(1, h - fh - 2)
            fp = Plot(fx, fy, fw, fh, kind)
            if any(fp.overlaps(o, 1) for o in plots) or fy <= sy <= fy + fh or abs(fy + fh // 2 - sy) < 3:
                continue
            if avoid and avoid(fx, fy, fw, fh):
                continue
            plots.append(fp)
            made += 1
            inner = [(xx, yy) for yy in range(fy + 1, fy + fh - 1) for xx in range(fx + 1, fx + fw - 1)]
            for yy in range(fy, fy + fh):
                for xx in range(fx, fx + fw):
                    edge = yy in (fy, fy + fh - 1) or xx in (fx, fx + fw - 1)
                    if kind == 'field':
                        m.set(xx, yy, FENCE if edge and random.random() < .5 else FIELD)
                    elif kind == 'pasture':
                        m.set(xx, yy, FENCE if edge else GRASS)
                    else:
                        m.set(xx, yy, TREE if not edge and (xx - fx) % 2 == 1 and (yy - fy) % 2 == 1 else GRASS)
            gx = fx + fw // 2
            gy = fy + fh - 1 if fy < sy else fy
            m.set(gx, gy, PATH)
            if kind == 'field':
                fields.append(inner)
            elif kind == 'pasture':
                name, ch, fg = random.choice(LIVESTOCK)
                spots = [c for c in inner if m.tile(*c) == GRASS]
                random.shuffle(spots)
                for c in spots[:random.randint(3, 6)]:
                    a = make_npc(game, name, 'livestock', fg, c[0], c[1], False, ch=ch)
                    m.mons.append(a)
                pastures.append(inner)
    return fields, pastures


def gen_village(game, s):
    w, h = 104, 38
    m = GameMap(s.map_key, 'town', s.name, w, h, GRASS)
    m.radius, m.sid, m.hid, m.signs = 60, s.id, None, []
    for i in range(len(m.t)):
        if random.random() < .04:
            m.t[i] = TREE
    sy = h // 2
    for x in range(w):
        m.set(x, sy, PATH)
    cx = w // 2
    # the green with a well and market stalls
    for yy in range(sy - 2, sy + 3):
        for xx in range(cx - 5, cx + 6):
            m.set(xx, yy, PATH if yy == sy else GRASS)
    m.set(cx, sy - 2, WELL)
    stalls = [(cx - 4, sy + 2), (cx - 3, sy + 2), (cx + 3, sy + 2), (cx + 4, sy + 2)]
    for c in stalls:
        m.set(c[0], c[1], STALL)
    names = town_names(getattr(s, 'race', 'human'))
    plots = [Plot(cx - 6, sy - 3, 13, 7, 'green')]
    kinds = [k for k in ('inn', 'shop', 'temple', 'stables') if k in s.services]
    if s.id == 0:
        kinds.append('elder')
    kinds += ['home'] * random.randint(10, 14)
    for k in kinds:
        for _ in range(300):
            pw, ph = (random.randint(11, 14), random.randint(6, 8)) if k in ('inn', 'temple') else (random.randint(7, 10), random.randint(5, 6))
            px = random.randint(max(2, cx - 36), min(w - pw - 2, cx + 36 - pw))
            py = random.choice([random.randint(1, sy - ph - 1), random.randint(sy + 2, h - ph - 1)])
            pl = Plot(px, py, pw, ph, k)
            if py < 1 or py + ph > h - 1 or any(pl.overlaps(o) for o in plots):
                continue
            plots.append(pl)
            break
    buildings = [p for p in plots if p.kind != 'green']
    for pl in buildings:
        build(m, pl)
        out = place_door(m, pl, pl.x + pl.w // 2, sy)
        carve_path(m, out, (out[0], sy))
        furnish(m, pl)
        if pl.kind in SIGN:
            add_sign(m, pl, SIGN[pl.kind])
    # farmland all around: fields, pastures with livestock, orchards
    fields, pastures = farmland(game, m, plots, sy, names)
    fields = fields + pastures
    # the people who run things
    for pl in buildings:
        if pl.kind in ROLE_OF:
            staff(game, m, pl, pl.kind, names, s)
    trader_spot = (cx - 3, sy + 3) if m.tile(cx - 3, sy + 3) in (GRASS, PATH) else (cx - 3, sy + 1)
    m.set(*trader_spot, GRASS)
    nm, col = TITLE['market']
    m.mons.append(make_npc(game, nm.format(n=names.pop()), 'market', col, trader_spot[0], trader_spot[1], True))
    homes = [p for p in buildings if p.kind == 'home']
    inn = next((p for p in buildings if p.kind == 'inn'), None)
    for pl in homes:
        beds = [c for c in pl.inside if m.tile(*c) in (FLOOR, PLANK)]
        for _ in range(random.randint(1, 2)):
            r = random.random()
            if r < .5 and fields:
                work, job = random.choice(random.choice(fields)), random.choice(['farmer', 'farmer', 'shepherd'])
            elif r < .6:
                work, job = (cx + random.randint(-4, 4), sy + random.choice([-1, 1])), 'child'
            elif r < .75 and inn:
                work, job = random.choice(free_inside(m, inn) or [inn.door]), 'drinker'
            else:
                work = (random.randint(2, w - 3), sy + random.choice([-1, 0, 1]))
                job = random.choice(JOBS)
            if not m.inb(*work) or not D.TILES[m.tile(*work)].walk:
                work = (cx, sy)
            townsfolk(game, m, beds, work, names, job, ch='☺' if job == 'child' else '@',
                      fg='#c8b8a0' if job == 'child' else '#a8aab4')
    c = rand_free(game, m, lambda t: t == GRASS)
    if c:
        dog = make_npc(game, 'A village dog', 'dog', '#c8a070', c[0], c[1], False, ch='d')
        m.mons.append(dog)
    m.portal_pos = (cx + 3, sy - 1)
    m.set(cx + 3, sy - 1, GRASS)
    m.entry = (0, sy)
    for i in range(len(m.seen)):
        m.seen[i] = 1
    return m


# ------------------------------------------------------------------ cities
def gen_city(game, s):
    w, h = 150, 50
    m = GameMap(s.map_key, 'town', s.name, w, h, GRASS)
    m.radius, m.sid, m.hid, m.signs = 60, s.id, None, []
    for x in range(w):
        for y in (0, h - 1):
            m.set(x, y, WALL)
    for y in range(h):
        for x in (0, w - 1):
            m.set(x, y, WALL)
    streets_y = [h // 4, h // 2, 3 * h // 4]
    streets_x = [w // 6, 2 * w // 6, w // 2, 4 * w // 6, 5 * w // 6]
    for y in streets_y:
        for x in range(1, w - 1):
            m.set(x, y, PATH)
    for x in streets_x:
        for y in range(1, h - 1):
            m.set(x, y, PATH)
    gy = streets_y[0]
    m.set(0, gy, PATH)
    m.set(w - 1, streets_y[1], PATH)
    m.set(streets_x[1], h - 1, PATH)
    # plaza
    px, py = streets_x[2], (streets_y[0] + streets_y[1]) // 2
    for yy in range(py - 3, py + 4):
        for xx in range(px - 8, px + 9):
            m.set(xx, yy, PATH)
    m.set(px, py, FOUNTAIN)
    names = town_names(getattr(s, 'race', 'human'))
    plots = [Plot(px - 9, py - 4, 19, 9, 'plaza')]
    stall_spots = [(px - 6, py - 2), (px - 6, py + 2), (px + 6, py - 2), (px + 6, py + 2), (px - 3, py - 3), (px + 3, py + 3)]
    for c in stall_spots:
        m.set(c[0], c[1], STALL)
    kinds = ['inn', 'inn', 'inn', 'shop', 'shop', 'temple', 'stables', 'barracks', 'barracks'] + ['home'] * 34
    for k in kinds:
        for _ in range(300):
            pw, ph = (random.randint(12, 16), random.randint(6, 8)) if k in ('inn', 'temple', 'barracks') else (random.randint(7, 11), random.randint(5, 7))
            x0, y0 = random.randint(2, w - pw - 2), random.randint(2, h - ph - 2)
            pl = Plot(x0, y0, pw, ph, k)
            cells = [(xx, yy) for yy in range(y0 - 1, y0 + ph + 1) for xx in range(x0 - 1, x0 + pw + 1)]
            if any(m.tile(*c) in (PATH, WALL, STALL, FOUNTAIN) for c in cells) or any(pl.overlaps(o, 1) for o in plots):
                continue
            plots.append(pl)
            break
    buildings = [p for p in plots if p.kind != 'plaza']
    for pl in buildings:
        build(m, pl)
        tx = min(streets_x, key=lambda sx: abs(sx - (pl.x + pl.w // 2)))
        ty = min(streets_y, key=lambda sy_: abs(sy_ - (pl.y + pl.h // 2)))
        if abs(ty - (pl.y + pl.h // 2)) <= abs(tx - (pl.x + pl.w // 2)):
            out = place_door(m, pl, pl.x + pl.w // 2, ty)
            carve_path(m, out, (out[0], ty))
        else:
            out = place_door(m, pl, tx, pl.y + pl.h // 2)
            carve_path(m, out, (tx, out[1]))
        furnish(m, pl)
        if pl.kind in SIGN:
            add_sign(m, pl, SIGN[pl.kind])
    for i in range(len(m.t)):
        if m.t[i] == GRASS and random.random() < .03:
            m.t[i] = TREE
    first = {}
    for pl in buildings:
        if pl.kind in ROLE_OF and pl.kind not in first:
            first[pl.kind] = staff(game, m, pl, pl.kind, names, s)
        elif pl.kind == 'inn':
            spots = free_inside(m, pl)
            if spots:
                m.mons.append(make_npc(game, f'Innkeeper {names.pop()}', 'inn', '#e0a060', spots[0][0], spots[0][1], True))
    nm, col = TITLE['market']
    for c in stall_spots[:3]:
        spot = (c[0], c[1] + (1 if c[1] > py else -1)) if c[1] != py else (c[0] + 1, c[1])
        if m.tile(*spot) == PATH and not m.mon_at(*spot):
            m.mons.append(make_npc(game, nm.format(n=names.pop()), 'market', col, spot[0], spot[1], True))
            break
    homes = [p for p in buildings if p.kind == 'home']
    inns = [p for p in buildings if p.kind == 'inn']
    plaza_cells = [(xx, yy) for yy in range(py - 3, py + 4) for xx in range(px - 8, px + 9) if m.tile(xx, yy) == PATH]
    for pl in homes:
        beds = [c for c in pl.inside if m.tile(*c) in (FLOOR, PLANK)]
        for _ in range(random.randint(1, 2)):
            r = random.random()
            if r < .5:
                work, job = random.choice(plaza_cells), random.choice(['weaver', 'baker', 'potter', 'carter', 'any'])
            elif r < .65 and inns:
                work, job = random.choice(free_inside(m, random.choice(inns)) or [(px, py + 1)]), 'drinker'
            elif r < .75:
                work, job = random.choice(plaza_cells), 'child'
            else:
                work, job = (random.choice(streets_x), random.randint(2, h - 3)), 'any'
            if not D.TILES[m.tile(*work)].walk:
                work = (px, py + 1)
            townsfolk(game, m, beds, work, names, job, ch='☺' if job == 'child' else '@',
                      fg='#c8b8a0' if job == 'child' else '#a8aab4')
    barracks = next((p for p in buildings if p.kind == 'barracks'), None)
    gfg = D.FACTIONS[s.faction]['fg']
    for i in range(9):
        home = free_inside(m, barracks) if barracks else [(px, py + 1)]
        post = (random.choice(streets_x), random.choice(streets_y)) if i % 2 else (px + random.randint(-7, 7), py + random.choice([-3, 3]))
        if not D.TILES[m.tile(*post)].walk:
            post = (px, py + 1)
        g = townsfolk(game, m, home, post, [f"A {D.FACTIONS[s.faction]['short']} guard"], 'guard', fg=gfg, role='guard')
        g.name = f"A {D.FACTIONS[s.faction]['short']} guard"
        g.night_watch = i < 2
    m.portal_pos = (px + 2, py + 1)
    m.entry = (1, gy)
    for i in range(len(m.seen)):
        m.seen[i] = 1
    return m


def gen_settlement_map(game, s):
    if s.kind == 'deephold':
        from .deephold import gen_deephold
        return gen_deephold(game, s)
    m = gen_city(game, s) if s.is_city else gen_village(game, s)
    place_signpost(m)
    return m


def place_signpost(m):
    """A signpost by the road into town, telling where the roads lead."""
    ex, ey = m.entry
    for dx in range(2, 8):
        for dy in (-1, 1, -2, 2):
            x, y = ex + dx, ey + dy
            if m.inb(x, y) and m.tile(x, y) in (GRASS, PATH, D.FLOOR) and not m.mon_at(x, y):
                m.set(x, y, D.SIGNPOST)
                m.signpost = (x, y)
                return


# ------------------------------------------------------------------ strongholds
def gen_hold_map(game, hd, hostile):
    castle = hd.kind == 'castle'
    w, h = (60, 23) if castle else (44, 19)
    m = GameMap(hd.map_key, 'siege' if hostile else 'town', hd.title, w, h, GRASS)
    m.radius = 12 if hostile else 60
    m.sid, m.hid, m.signs = None, hd.id, []
    m.level = 4 + (2 if castle else 0)
    wall = ROCK
    x0, y0, x1, y1 = 2, 1, w - 3, h - 2
    for x in range(x0, x1 + 1):
        m.set(x, y0, wall)
        m.set(x, y1, wall)
    for y in range(y0, y1 + 1):
        m.set(x0, y, wall)
        m.set(x1, y, wall)
    for (cx, cy) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if m.inb(cx + dx, cy + dy):
                    m.set(cx + dx, cy + dy, wall)
    gate_y = h // 2
    m.set(x0, gate_y, ODOOR)
    for x in range(0, x0):
        m.set(x, gate_y, PATH)
    for x in range(x0 + 1, x1):
        m.set(x, gate_y, PATH)
    kw, kh = (16, 9) if castle else (11, 7)
    keep = Plot(x1 - kw - 2, gate_y - kh // 2, kw, kh, 'keep')
    build(m, keep)
    place_door(m, keep, x0, gate_y)
    furnish(m, keep)
    barracks = Plot(x0 + 4, y0 + 2, 12 if castle else 9, 5, 'barracks')
    build(m, barracks)
    out = place_door(m, barracks, barracks.x + barracks.w // 2, gate_y)
    carve_path(m, out, (out[0], gate_y))
    furnish(m, barracks)
    armory = None
    if castle:
        armory = Plot(x0 + 4, y1 - 7, 11, 5, 'shop')
        build(m, armory)
        out = place_door(m, armory, armory.x + armory.w // 2, gate_y)
        carve_path(m, out, (out[0], gate_y))
        furnish(m, armory)
        chapel = Plot(x0 + 18, y1 - 7, 10, 5, 'temple')
        build(m, chapel)
        out = place_door(m, chapel, chapel.x + chapel.w // 2, gate_y)
        carve_path(m, out, (out[0], gate_y))
        furnish(m, chapel)
    f = D.FACTIONS[hd.faction]
    for c in [(x, y) for y in range(y0 + 1, y1) for x in range(x0 + 1, x1)]:
        if m.tile(*c) == GRASS and random.random() < .5:
            m.set(c[0], c[1], PATH)
    if hostile:
        n = max(4, min(14, hd.garrison // 2 + 2))
        lvl = max(3, game.world.regions[hd.region].danger + (3 if castle else 2))
        troops = f['troops']
        cells = [c for c in (keep.inside + barracks.inside + [(x, y) for y in range(y0 + 1, y1) for x in range(x0 + 6, x1)])
                 if D.TILES[m.tile(*c)].walk]
        random.shuffle(cells)
        pid = game.new_id()
        boss_spot = free_inside(m, keep)[0]
        boss = make_monster(game, random.choice(troops[-2:]), boss_spot[0], boss_spot[1], lvl + 2, 2)
        boss.name = f"{'Lord' if castle else 'Captain'} {random.choice(NAMES)} of {hd.name}"
        boss.faction = hd.faction
        boss.commander = True
        boss.pack = pid
        m.mons.append(boss)
        for c in cells[:n]:
            if m.mon_at(*c):
                continue
            mon = make_monster(game, random.choice(troops), c[0], c[1], lvl, 1 if random.random() < .12 else 0)
            mon.faction = hd.faction
            mon.pack = pid if random.random() < .3 else game.new_id()
            m.mons.append(mon)
        m.entry = (0, gate_y)
    else:
        names = town_names(D.FACTIONS[hd.faction].get('race', 'human'))
        spot = free_inside(m, keep)[0]
        m.mons.append(make_npc(game, f"Castellan {names.pop()}", 'castellan', '#f0e0a0', spot[0], spot[1], True))
        if armory:
            sp = free_inside(m, armory)
            if sp:
                m.mons.append(make_npc(game, f"Quartermaster {names.pop()}", 'shop', '#d8d0b0', sp[0][0], sp[0][1], True))
        else:
            sp = free_inside(m, barracks)
            if sp:
                m.mons.append(make_npc(game, f"Quartermaster {names.pop()}", 'shop', '#d8d0b0', sp[0][0], sp[0][1], True))
        if castle:
            sp = free_inside(m, chapel)
            if sp:
                m.mons.append(make_npc(game, f"Chaplain {names.pop()}", 'healer', '#f4f0e6', sp[0][0], sp[0][1], True))
        for i in range(4 if castle else 3):
            home = free_inside(m, barracks)
            post = (random.randint(x0 + 2, x1 - 2), random.randint(y0 + 1, y1 - 1))
            if not D.TILES[m.tile(*post)].walk:
                post = (x0 + 3, gate_y)
            g = townsfolk(game, m, home, post, [], 'guard', fg=f['fg'], role='guard',
                          ch=D.MONSTERS[f['troops'][0]]['ch'])
            g.name = f"A {f['short']} {D.MONSTERS[f['troops'][0]]['name'].lower()}"
            g.night_watch = i < 2
        m.signs.append((keep.x + 2, keep.y - 1, 'KEEP'))
        m.entry = (0, gate_y)
    for i in range(len(m.seen)):
        m.seen[i] = 1 if not hostile else 0
    return m


# ------------------------------------------------------------------ daily life
def target_for(game, npc):
    h = hour(game)
    if npc.job == 'guard':
        night = getattr(npc, 'night_watch', False)
        on = (h >= 21 or h < 5) if night else (5 <= h < 21)
        return npc.work_pos if on else npc.home_pos
    if npc.job == 'drinker':
        return npc.work_pos if (h >= 17 or h < 1) else npc.home_pos
    if npc.job == 'child':
        return npc.work_pos if 8 <= h < 18 else npc.home_pos
    return npc.work_pos if DAY_START <= h < DAY_END else npc.home_pos


def path_between(m, a, b):
    w = m.w
    start, goal = a[1] * w + a[0], b[1] * w + b[0]
    prev = {start: None}
    q = deque([start])
    while q:
        c = q.popleft()
        if c == goal:
            break
        x, y = c % w, c // w
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
            nx, ny = x + dx, y + dy
            if not (0 <= nx < w and 0 <= ny < m.h):
                continue
            ni = ny * w + nx
            if ni in prev:
                continue
            t = D.TILES[m.t[ni]]
            if not (t.walk or t.door):
                continue
            prev[ni] = c
            q.append(ni)
    if goal not in prev:
        return []
    out, c = [], goal
    while c != start:
        out.append((c % w, c // w))
        c = prev[c]
    out.reverse()
    return out[:60]


def live(game, m):
    """Move townsfolk one step along their day."""
    p = game.player
    for npc in m.mons:
        if npc.is_npc and npc.role == 'livestock' and random.random() < .25:
            game.random_step(npc)
            continue
        if not npc.is_npc or not hasattr(npc, 'work_pos'):
            continue
        tgt = target_for(game, npc)
        if (npc.x, npc.y) == tuple(tgt):
            if npc.job not in ('guard',) and random.random() < .15:
                game.random_step(npc)
            elif npc.job == 'guard' and random.random() < .3:
                game.random_step(npc)
            continue
        if not npc.path or tuple(npc.path[-1]) != tuple(tgt) or random.random() < .02:
            npc.path = path_between(m, (npc.x, npc.y), tuple(tgt))
            if not npc.path:
                continue
        nx, ny = npc.path[0]
        if (nx, ny) == (p.x, p.y) or (m.mon_at(nx, ny) and m.mon_at(nx, ny) is not npc):
            if random.random() < .3:
                npc.path = []
            continue
        if m.tile(nx, ny) == DOOR:
            m.set(nx, ny, ODOOR)
            continue
        npc.x, npc.y = nx, ny
        npc.path.pop(0)
    # chatter
    if random.random() < .08:
        near = [n for n in m.mons if n.is_npc and hasattr(n, 'job') and cheb(n.x, n.y, p.x, p.y) <= 6 and game.visible(n.x, n.y)]
        if near:
            n = random.choice(near)
            line = random.choice(BARKS.get(n.job, BARKS['any']) + BARKS['any'][:2])
            game.say(n, line)
    # close doors behind people at night now and then
    if is_night(game) and random.random() < .05:
        for i, t in enumerate(m.t):
            if t == ODOOR and random.random() < .1:
                x, y = i % m.w, i // m.w
                if not m.mon_at(x, y) and (x, y) != (p.x, p.y):
                    m.t[i] = DOOR
