"""Villages, cities and strongholds that feel lived in: furnished buildings, fields and market
stalls, and townsfolk who go to work by day and home at night."""
import math
import random
import heapq
from collections import deque

from . import data as D
from .data import (WALL, FLOOR, DOOR, ODOOR, GRASS, TREE, PATH, WELL, FIELD, FENCE, TABLE, BED, STALL, FOUNTAIN,
                   ANVIL, ALTAR, BARREL, PLANK, ROCK, WATER, SHALLOW)
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
from .lore import BARKS  # noqa: E402  (what people say lives with the rest of the lore)

DAY_START, DAY_END = 6, 20


def hour(game):
    return (game.turn % D.DAY_LEN) * 24 // D.DAY_LEN


def lamp_light(game):
    """How dark it is in the streets, 0 (day) to 1 (night): dusk over three hours from about six, dawn over two
    from about five; earlier dusk and later dawn in winter, the other way round in summer."""
    from .seasons import dusk, dawn
    t = (game.turn % D.DAY_LEN) * 24 / D.DAY_LEN
    du, da = dusk(game.day), dawn(game.day)
    if da + 2 <= t < du:
        return 0.0
    if du <= t < du + 3:
        return (t - du) / 3
    if da <= t < da + 2:
        return 1 - (t - da) / 2
    return 1.0


def lamps_wanted(game):
    """Should the street lamps burn now? From dusk until an hour after dawn."""
    from .seasons import dusk, dawn
    t = (game.turn % D.DAY_LEN) * 24 / D.DAY_LEN
    return t >= dusk(game.day) or t < dawn(game.day) + 1


def lamp_round(game):
    """The hours the lamplighter is out: three at dusk, two at dawn."""
    from .seasons import dusk, dawn
    du, da = int(dusk(game.day)), int(dawn(game.day) + 1)
    return {du, du + 1, du + 2, da - 1, da}


LAMP_COL = (255, 176, 90)


def set_lamp(m, k, on):
    """Light or put out lamp k of a town map."""
    lit = m.lamp_on
    if on:
        lit.add(k)
    else:
        lit.discard(k)
    m.lights = [(m.lamps[j][0], m.lamps[j][1], LAMP_COL, 6) for j in sorted(lit)] + list(getattr(m, 'glows', []))
    m._light = None


def sync_lamps(game, m):
    """Coming into a town: the lamps are as the lamplighter left them."""
    if not getattr(m, 'lamps', None):
        return
    on = lamps_wanted(game)
    m.lamp_on = set(range(len(m.lamps))) if on else set()
    set_lamp(m, 0, on) if m.lamps else None


def town_ambient(game, m):
    """Daylight in a town map, bluish at night. Updates the cached light when it changes."""
    k = lamp_light(game)
    amb = (round(1 - .74 * k, 2), round(1 - .7 * k, 2), round(1 - .58 * k, 2))
    if getattr(m, 'ambient', None) != amb:
        m.ambient = amb
        m._light = None
    return k


def place_lamps(m, cells):
    """Put lamp posts on these cells (where there is room) and remember them."""
    m.lamps = getattr(m, 'lamps', [])
    m.lamp_on = getattr(m, 'lamp_on', set())
    for x, y in cells:
        if m.inb(x, y) and m.tile(x, y) in (GRASS, PATH) and not any(abs(x - a) + abs(y - b) < 3 for a, b in m.lamps):
            m.set(x, y, D.LAMP)
            m.lamps.append((x, y))


def hearths(m, buildings):
    """Fires and candles inside inns, temples and the elder's house: warm light at night."""
    m.glows = []
    for pl in buildings:
        if pl.kind in ('inn', 'temple', 'elder', 'barracks') and pl.inside:
            cx = sum(c[0] for c in pl.inside) // len(pl.inside)
            cy = sum(c[1] for c in pl.inside) // len(pl.inside)
            col = (255, 150, 70) if pl.kind != 'temple' else (255, 220, 150)
            m.glows.append((cx, cy, col, max(4, min(pl.w, pl.h))))
    m.lamp_on = getattr(m, 'lamp_on', set())
    m.lights = list(m.glows)


def lamplighter(game, m, npc):
    """The lamplighter walks from lamp to lamp at dusk, and again at dawn to put them out."""
    lamps = getattr(m, 'lamps', [])
    want = lamps_wanted(game)
    todo = [k for k in range(len(lamps)) if (k in m.lamp_on) != want]
    h = hour(game)
    rnd = lamp_round(game)
    if todo and h in rnd:
        k = min(todo, key=lambda j: cheb(lamps[j][0], lamps[j][1], npc.x, npc.y))
        lx, ly = lamps[k]
        if cheb(lx, ly, npc.x, npc.y) <= 1:
            set_lamp(m, k, want)
            if game.visible(npc.x, npc.y) and random.random() < .15:
                game.say(npc, random.choice(['Evening! Light against the dark.', 'There we are.', 'One more lit.'])
                         if want else random.choice(['Morning already.', 'Out you go, little flame.']))
            return None
        spots = [(lx + dx, ly + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                 if m.inb(lx + dx, ly + dy) and D.TILES[m.tile(lx + dx, ly + dy)].walk]
        return min(spots, key=lambda c: cheb(c[0], c[1], npc.x, npc.y)) if spots else npc.home_pos
    if todo and h not in rnd:                       # the night came on, or the morning: the rest follow
        for k in todo:
            set_lamp(m, k, want)
    return npc.home_pos


def is_night(game):
    from .seasons import dusk, dawn
    t = (game.turn % D.DAY_LEN) * 24 / D.DAY_LEN
    return t >= dusk(game.day) + 3 or t < dawn(game.day)


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
    elif k == 'keepsake':           # a hall of old curiosities nobody can bear to throw away
        for xx in range(ix0, ix1 + 1, 2):
            put((xx, iy0), D.STATUE if (xx - ix0) % 4 == 0 else BARREL)
        put(((ix0 + ix1) // 2, (iy0 + iy1) // 2 + 1), TABLE)
        put((ix0, iy1), D.CHEST_OPEN)
        put((ix1, iy1), D.CHEST_OPEN)
    elif k == 'keep':
        for xx in range(ix0 + 2, ix1 - 1):
            put((xx, (iy0 + iy1) // 2), TABLE)
        put(((ix0 + ix1) // 2, iy0), ALTAR)


ROLE_OF = {'inn': 'inn', 'market': 'market', 'shop': 'shop', 'temple': 'healer', 'stables': 'stables', 'elder': 'elder'}
SIGN = {'inn': 'INN', 'shop': 'OUTFITTER', 'temple': 'TEMPLE', 'stables': 'STABLES', 'elder': 'ELDER', 'keep': 'KEEP',
        'barracks': 'BARRACKS', 'keepsake': 'KEEPSAKE HALL'}
TITLE = {'inn': ('Innkeeper {n}', '#e0a060'), 'market': ('{n} the Trader', '#f2c44a'), 'shop': ('{n} the Outfitter', '#d8d0b0'),
         'temple': ('Sister {n}', '#f4f0e6'), 'stables': ('Stablemaster {n}', '#c8a070'), 'elder': ('Elder Berend Ashford', '#c08cf0')}


# what hangs over the door of each kind of building: one glyph, like the painted boards over a medieval street
SIGN_GLYPH = {'inn': ('¡', (236, 176, 84)), 'shop': ('¥', (206, 206, 216)), 'temple': ('†', (244, 234, 200)),
              'stables': ('Ω', (206, 160, 110)), 'elder': ('♦', (200, 150, 240)), 'barracks': ('╬', (200, 200, 220)),
              'keep': ('Ω', (230, 220, 190)), 'guild:magi': ('*', (143, 168, 255)), 'guild:iron': ('Φ', (200, 204, 216)),
              'guild:dawn': ('☼', (255, 232, 160)), 'guild:wardens': ('♣', (112, 192, 96)), 'guild:alembic': ('!', (224, 160, 224)),
              'guild:carto': ('≡', (216, 200, 144)), 'guild:anglers': ('≈', (128, 192, 224)),
              'warehouse': ('■', (170, 126, 80)), 'customs': ('$', (230, 206, 120)), 'harbourmaster': ('⌂', (176, 200, 224)),
              'boathouse': ('≈', (150, 190, 210))}
INN_NAMES = ["The Drowsy Mule", "The Crossed Keys", "The Last Lantern", "The Weary Boot", "The Green Man", "The Hanged Fiddler",
             "The Three Crowns", "The Golden Sheaf", "The Wandering Goose", "The Broken Wheel", "The Red Hart", "The Old Oak",
             "The Hearth and Hound", "The Laughing Pike", "The Copper Kettle", "The Sleeping Giant", "The Silver Bell",
             "The Black Ram", "The Merry Miller", "The Lame Horse", "The Stag's Head", "The Rose and Thistle",
             "The Plough and Star", "The Barley Mow", "The Bishop's Mitre", "The Gilded Cup", "The White Swan"]
HALFLING_INN_NAMES = ["The Plump Partridge", "The Sleepy Badger", "The Honey Pot", "The Merry Kettle", "The Pipe and Pickle",
                      "The Second Breakfast", "The Mossy Stone", "The Crooked Chimney", "The Fat Goose", "The Warm Hearth",
                      "The Bramble Bush", "The Laughing Trout"]
SEA_INN_NAMES = ["The Salty Gull", "The Drowned Sailor", "The Mermaid's Rest", "The Anchor and Rope", "The Lantern Quay",
                 "The Tarred Hand", "The Ship's Cat"]


def add_sign(m, pl, text):
    """Register a building: its box, its door and its kind. Its name is given once the people are in
    (see name_buildings); its hanging sign and its label are drawn by the map."""
    if not pl.door:
        return
    bx = plot_box(pl)
    kind = 'guild:' + pl.guild if getattr(pl, 'guild', None) else pl.kind
    if not hasattr(m, 'buildings'):
        m.buildings = []
    b = dict(kind=kind, name=text.title(), box=(bx.x, bx.y, bx.w, bx.h), door=pl.door, plot=pl)
    m.buildings.append(b)
    hang_sign(m, b)


def hang_sign(m, b):
    """The board on the wall beside the door."""
    g = SIGN_GLYPH.get(b['kind'])
    if not g:
        return
    dx, dy = b['door']
    for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        x, y = dx + ox, dy + oy
        if m.inb(x, y) and m.tile(x, y) == WALL:
            if not hasattr(m, 'hang'):
                m.hang = {}
            m.hang[(x, y)] = g
            b['hang'] = (x, y)
            return


def name_buildings(game, m, s=None):
    """Give every building a proper name: the inns their own, the rest after who runs them."""
    from . import guilds as GU
    used = {b['name'] for gm in game.maps.values() for b in getattr(gm, 'buildings', []) if gm is not m}
    inns = HALFLING_INN_NAMES if getattr(s, 'race', '') == 'halfling' else INN_NAMES
    pool = [n for n in inns if n not in used] or inns[:]
    random.shuffle(pool)
    sea = [n for n in SEA_INN_NAMES if n not in used] or SEA_INN_NAMES[:]
    random.shuffle(sea)
    for b in getattr(m, 'buildings', []):
        k = b['kind']
        x, y, w, h = b['box']
        owner = next((o for o in m.mons if x <= o.x < x + w and y <= o.y < y + h and o.role in ('shop', 'stables', 'healer', 'inn')), None)
        sur = owner.name.split(' the ')[0].split()[-1] if owner else random.choice(['Hale', 'Brook', 'Marsh', 'Cooper', 'Wright'])
        if k == 'inn':
            near_sea = getattr(m, 'harbour_side', None) and any(m.tile(xx, yy) == WATER for xx in range(max(0, x - 12), min(m.w, x + w + 12))
                                                                for yy in range(max(0, y - 12), min(m.h, y + h + 12)))
            b['name'] = (sea.pop() if sea else pool.pop()) if near_sea else (pool.pop() if pool else 'The Inn')
            b['what'] = 'inn'
        elif k == 'shop':
            b['name'], b['what'] = f"{sur}'s Outfitters", 'outfitter'
        elif k == 'stables':
            b['name'], b['what'] = f"{sur}'s Stables", 'stables'
        elif k == 'temple':
            try:
                from .gods import temple_god, GODS
                b['name'] = f"Temple of {GODS[temple_god(game, m)]['name']}"
            except Exception:
                b['name'] = 'The Temple'
            b['what'] = 'temple'
        elif k == 'elder':
            b['name'], b['what'] = "The Elder's House", 'elder'
        elif k == 'barracks':
            b['name'], b['what'] = 'The Barracks', 'barracks'
        elif k == 'keepsake':
            b['name'], b['what'] = 'The Keepsake Hall', 'hall of old curiosities'
        elif k.startswith('guild:'):
            b['name'], b['what'] = GU.GUILDS[k[6:]]['name'], 'guild hall'
        else:
            b['what'] = k


def newsfolk(game, m, s, buildings, names):
    """The people who bring the news: a factor of the Merchants' Guild in the inn of every town, a captain in the
    barracks (or a sergeant off duty at the inn), and a sailor or two by the fire in a harbour."""
    if s is None or s.kind == 'hamlet':
        return
    inn = next((p for p in buildings if p.kind == 'inn'), None)
    barracks = next((p for p in buildings if p.kind == 'barracks'), None)

    def put(pl, name, role, fg, ch='☺'):
        if not pl:
            return None
        spots = [c for c in free_inside(m, pl) if c[1] > pl.y + 1] or free_inside(m, pl)
        if not spots or not names:
            return None
        c = spots[0]
        npc = make_npc(game, name.format(n=names.pop()), role, fg, c[0], c[1], True, ch=ch)
        m.mons.append(npc)
        return npc
    if s.kind != 'village' or random.random() < .5:
        put(inn, '{n}, Factor of the Merchants\' Guild', 'factor', '#f0d070')
    if barracks:
        put(barracks, 'Captain {n}', 'captain', D.FACTIONS[s.faction]['fg'])
    else:
        put(inn, 'Sergeant {n}, off duty', 'captain', D.FACTIONS[s.faction]['fg'])
    if getattr(s, 'harbour', False):
        put(inn, '{n} the Sailor', 'sailor', '#80c0e0')


def staff(game, m, pl, role_key, names, s):
    """Put the person who runs a building behind its counter."""
    nm, col = TITLE[role_key]
    if role_key == 'elder' and (s is None or s.id != 0):
        nm = 'Mayor {n}' if getattr(s, 'race', '') == 'halfling' else 'Elder {n}'
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


def townsfolk(game, m, home, work, names, job=None, fg='#a8aab4', ch='☺', role='villager'):
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


def farmland(game, m, plots, sy, names, avoid=None, want=None):
    """Fields of crops, fenced pastures with livestock and orchards around a village."""
    w, h = m.w, m.h
    fields, pastures = [], []
    want = want or [('field', 9), ('pasture', 3), ('orchard', 2)]
    for kind, n in want:
        made = 0
        for _ in range(400):
            if made >= n:
                break
            fw, fh = (random.randint(9, 15), random.randint(6, 10)) if kind == 'field' else (random.randint(8, 13), random.randint(6, 9))
            fx, fy = random.randint(1, w - fw - 2), random.randint(1, h - fh - 2)
            fp = Plot(fx, fy, fw, fh, kind)
            if any(fp.overlaps(o, 1) for o in plots) or (fy <= sy + 3 and fy + fh >= sy - 3):
                continue
            if any(m.tile(xx, yy) in (PATH, WALL, FLOOR, PLANK, WATER, SHALLOW, D.LAMP, WELL, STALL, D.BRIDGE, D.SLOPE, D.EARTH)
                   for yy in range(fy - 1, fy + fh + 1) for xx in range(fx - 1, fx + fw + 1) if m.inb(xx, yy)):
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
                        m.set(xx, yy, FENCE if edge else FIELD)
                    elif kind == 'pasture':
                        m.set(xx, yy, FENCE if edge else GRASS)
                    else:                      # an orchard: fruit trees in rows behind a fence, so it reads as planted
                        m.set(xx, yy, FENCE if edge else TREE if (xx - fx) % 2 == 1 and (yy - fy) % 2 == 1 else GRASS)
            gx = fx + fw // 2
            gy = fy + fh - 1 if (fy < sy if sy > -100 else fy + fh // 2 < h // 2) else fy
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


def fishing_pond(game, m, plots, sy, names, fisher=True):
    """A reedy pond by the village, with an old fisherman who will teach you to fish."""
    for _ in range(300):
        pw, ph = random.randint(11, 15), random.randint(6, 7)
        px = random.randint(4, m.w - pw - 4)
        py = random.choice([random.randint(max(2, sy - 24), sy - ph - 3), random.randint(sy + 4, min(m.h - ph - 2, sy + 20))])
        pl = Plot(px - 1, py - 1, pw + 2, ph + 2, 'pond')
        if any(pl.overlaps(o, 1) for o in plots):
            continue
        if any(m.tile(xx, yy) in (PATH, WALL, FLOOR, PLANK, FENCE, FIELD) for yy in range(py - 1, py + ph + 1)
               for xx in range(px - 1, px + pw + 1)):
            continue
        plots.append(pl)
        cx, cy = px + pw / 2 - .5, py + ph / 2 - .5
        for yy in range(py, py + ph):
            for xx in range(px, px + pw):
                d = ((xx - cx) / (pw / 2)) ** 2 + ((yy - cy) / (ph / 2)) ** 2
                if d < .55:
                    m.set(xx, yy, WATER)
                elif d < 1:
                    m.set(xx, yy, SHALLOW if random.random() < .7 else GRASS)
                elif m.tile(xx, yy) == TREE:
                    m.set(xx, yy, GRASS)
        # a little jetty of planks, the fisherman at its end
        jx = px + pw // 2
        top = py < sy
        step = -1 if top else 1
        shore = py + ph - 1 if top else py
        for k in range(3):
            m.set(jx, shore + k * step, PLANK)
        fy = shore + 2 * step
        carve_path(m, (jx, shore - step), (jx, sy))
        if not fisher:
            return pl
        full = names.pop()
        from .races import who
        gender, race = who(full)
        fisher = make_npc(game, f"Old {full.split()[0]} the {'Fisherwoman' if gender == 'female' else 'Fisherman'}", 'fisher', '#9cc8e0', jx, fy, True,
                          race=race, gender=gender)
        m.mons.append(fisher)
        return pl
    return None


def wooded(m, belt=9, inner=.004, game=None, s=None):
    """The land round a village: woods along the edges only where the world map has woods on that side,
    open country elsewhere, and hardly a tree in the village itself (a few in gardens and on the green)."""
    w, h = m.w, m.h
    side = {'n': .15, 's': .15, 'w': .15, 'e': .15}
    if game is not None and s is not None:
        om = game.maps['over']
        for k, (dx, dy) in {'n': (0, -1), 's': (0, 1), 'w': (-1, 0), 'e': (1, 0)}.items():
            cells = [(s.x + dx * r + ox, s.y + dy * r + oy) for r in range(2, 7) for ox in (-2, 0, 2) for oy in (-1, 0, 1)]
            cells = [c for c in cells if om.inb(*c)]
            woods = sum(1 for c in cells if om.tile(*c) == D.FOREST)
            side[k] = woods / max(1, len(cells))
    for y in range(h):
        for x in range(w):
            p = inner
            for k, d in (('n', y), ('s', h - 1 - y), ('w', x), ('e', w - 1 - x)):
                if d < belt:
                    p = max(p, (belt - d) / belt * (.08 + .62 * side[k]))
            if random.random() < p:
                m.set(x, y, TREE)


def lay_road(m, pts, width):
    """A road through a list of points, `width` cells wide."""
    half = width // 2
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for k in range(n + 1):
            x = round(x0 + (x1 - x0) * k / n)
            y = round(y0 + (y1 - y0) * k / n)
            for dy in range(-half, width - half):
                for dx in range(-half, width - half):
                    if abs(x1 - x0) >= abs(y1 - y0) and dx:
                        continue        # a road running east-west is wide north-south, and the other way round
                    if abs(x1 - x0) < abs(y1 - y0) and dy:
                        continue
                    if m.inb(x + dx, y + dy):
                        m.set(x + dx, y + dy, PATH)


def meander(a, b, step, wobble, horizontal=True):
    """Points from a to b that wander a little sideways."""
    pts = [a]
    off = 0
    n = max(1, int(abs((b[0] - a[0]) if horizontal else (b[1] - a[1])) // step))
    for k in range(1, n):
        off = max(-wobble, min(wobble, off + random.choice([-1, 0, 0, 1])))
        t = k / n
        if horizontal:
            pts.append((round(a[0] + (b[0] - a[0]) * t), round(a[1] + (b[1] - a[1]) * t) + off))
        else:
            pts.append((round(a[0] + (b[0] - a[0]) * t) + off, round(a[1] + (b[1] - a[1]) * t)))
    pts.append(b)
    return pts


def road_cells(m):
    return {(i % m.w, i // m.w) for i, t in enumerate(m.t) if t == PATH}


def house_plot(kind, x, y):
    """A plot for a building: homes are often L-shaped, with an annex on one side."""
    if kind in ('inn', 'temple'):
        pw, ph = random.randint(11, 14), random.randint(8, 10)
    elif kind in ('shop', 'stables', 'elder', 'keepsake'):
        pw, ph = random.randint(8, 11), random.randint(6, 8)
    else:
        pw, ph = random.randint(6, 9), random.randint(5, 8)
    pl = Plot(x, y, pw, ph, kind)
    pl.annex = None
    if kind in ('home', 'elder', 'inn') and random.random() < .5:
        aw, ah = random.randint(4, 6), random.randint(4, 6)
        side = random.choice(['l', 'r'])
        ay = y + ph - ah if random.random() < .5 else y
        ax = x - aw + 1 if side == 'l' else x + pw - 1
        pl.annex = (ax, ay, aw, ah)
    return pl


def plot_box(pl):
    """The bounding box of a building with its annex: (x, y, w, h)."""
    x0, y0, x1, y1 = pl.x, pl.y, pl.x + pl.w, pl.y + pl.h
    if getattr(pl, 'annex', None):
        ax, ay, aw, ah = pl.annex
        x0, y0, x1, y1 = min(x0, ax), min(y0, ay), max(x1, ax + aw), max(y1, ay + ah)
    return Plot(x0, y0, x1 - x0, y1 - y0, pl.kind)


def build_house(m, pl):
    """Walls and floor for a building, joining an annex into one L-shaped room."""
    build(m, pl)
    inside = list(pl.inside)
    if getattr(pl, 'annex', None):
        ax, ay, aw, ah = pl.annex
        sub = Plot(ax, ay, aw, ah, pl.kind)
        for yy in range(ay, ay + ah):
            for xx in range(ax, ax + aw):
                if (xx, yy) in set(inside):
                    continue
                edge = yy in (ay, ay + ah - 1) or xx in (ax, ax + aw - 1)
                m.set(xx, yy, WALL if edge else FLOOR)
        sub_inside = [(xx, yy) for yy in range(ay + 1, ay + ah - 1) for xx in range(ax + 1, ax + aw - 1)]
        # open up the shared wall so the two parts make one room
        for yy in range(min(ay, pl.y), max(ay + ah, pl.y + pl.h)):
            for xx in range(min(ax, pl.x), max(ax + aw, pl.x + pl.w)):
                if m.tile(xx, yy) != WALL:
                    continue
                ns = m.tile(xx, yy - 1) == FLOOR and m.tile(xx, yy + 1) == FLOOR
                ew = m.tile(xx - 1, yy) == FLOOR and m.tile(xx + 1, yy) == FLOOR
                if ns or ew:
                    m.set(xx, yy, FLOOR)
                    inside.append((xx, yy))
        inside += [c for c in sub_inside if c not in inside]
    pl.inside = inside


def garden(m, pl, away_y, plots=()):
    """A small fenced garden behind a house, with vegetables or a fruit tree."""
    bx = plot_box(pl)
    gw, gh = random.randint(5, 8), random.randint(4, 5)
    gx = bx.x + random.randint(0, max(0, bx.w - gw))
    gy = bx.y - gh if away_y < 0 else bx.y + bx.h
    cells = [(xx, yy) for yy in range(gy, gy + gh) for xx in range(gx, gx + gw)]
    if not all(m.inb(*c) and m.tile(*c) in (GRASS, TREE) for c in cells):
        return None
    gp = Plot(gx, gy, gw, gh, 'garden')
    if any(gp.overlaps(o, 1) for o in plots if o is not bx and not (o.x == bx.x and o.y == bx.y)):
        return None
    veg = random.random() < .6
    for xx, yy in cells:
        edge = yy in (gy, gy + gh - 1) or xx in (gx, gx + gw - 1)
        if edge:
            m.set(xx, yy, FENCE)
        else:
            m.set(xx, yy, FIELD if veg else GRASS)
    if not veg:
        m.set(gx + gw // 2, gy + gh // 2, TREE)
    gate = (gx + gw // 2, gy + gh - 1 if away_y < 0 else gy)
    m.set(*gate, GRASS)
    return Plot(gx, gy, gw, gh, 'garden')


def road_dirs(game, s):
    """The roads that leave a settlement on the world map, as they really lie there: [(dx, dy, neighbour id)].
    Every road that touches the settlement counts (also the great roads, roads to castles, and roads that only
    pass through), so a road that runs on past the village on the map runs through it on the village map too."""
    import math
    from collections import deque
    om = game.maps['over']
    w = game.world
    road_like = (D.ROAD, D.CASTLE, D.FORT)
    out = []
    for sx, sy in [(s.x + dx, s.y + dy) for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0), (1, -1), (1, 1), (-1, 1), (-1, -1))]:
        if not om.inb(sx, sy) or om.tile(sx, sy) != D.ROAD:
            continue
        # follow this road outwards: where it is after a few steps gives the direction, where it ends the neighbour
        seen = {(s.x, s.y), (sx, sy)}
        q = deque([(sx, sy, 1)])
        far, other = (sx, sy), None
        while q:
            x, y, d = q.popleft()
            if d <= 6 and max(abs(x - s.x), abs(y - s.y)) > max(abs(far[0] - s.x), abs(far[1] - s.y)):
                far = (x, y)
            if d > 160:
                continue
            for ddx, ddy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
                nx, ny = x + ddx, y + ddy
                if (nx, ny) in seen or not om.inb(nx, ny):
                    continue
                t = om.tile(nx, ny)
                if t in (D.TOWN, D.CITY):
                    o = w.settlement_at(nx, ny)
                    if o and o.id != s.id and other is None:
                        other = o.id
                    continue
                if t in road_like:
                    seen.add((nx, ny))
                    q.append((nx, ny, d + 1))
        dx, dy = far[0] - s.x, far[1] - s.y
        if not (dx or dy):
            continue
        a = math.atan2(dy, dx)
        if any(abs((a - math.atan2(o[1], o[0]) + math.pi) % (2 * math.pi) - math.pi) < .6 for o in out):
            continue                                     # two roads leaving the same way share one
        out.append((dx, dy, other))
    if not out:                                          # no road at all: the old way, from the list of roads
        from .wanderers import road_path
        for a, b in getattr(w, 'road_edges', []):
            if s.id in (a, b):
                other = b if a == s.id else a
                path = road_path(game, s.id, other) or []
                if len(path) >= 2:
                    px, py = path[min(6, len(path) - 1)]
                    if (px - s.x) or (py - s.y):
                        out.append((px - s.x, py - s.y, other))
    return out


def edge_point(m, cx, cy, dx, dy):
    """Where a ray from (cx, cy) in direction (dx, dy) leaves the map."""
    best = None
    for t in range(1, m.w + m.h):
        x, y = round(cx + dx * t / max(abs(dx), abs(dy))), round(cy + dy * t / max(abs(dx), abs(dy)))
        if not (0 <= x < m.w and 0 <= y < m.h):
            break
        best = (x, y)
    return best


D8 = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))


def river_course(game, s, m, k):
    """When a river on the world map runs past a settlement, where it runs on the settlement's own map: a smooth line
    of points from edge to edge, k cells of the town map for every cell of the world map. None when no river is near."""
    om = game.maps['over']
    riv = getattr(om, 'river', None)
    if not riv:
        return None
    R = 4
    cells = {(x, y) for dy in range(-R, R + 1) for dx in range(-R, R + 1) for x, y in [(s.x + dx, s.y + dy)]
             if om.inb(x, y) and riv[y * om.w + x]}
    if not any(cheb(x, y, s.x, s.y) <= 2 for x, y in cells):
        return None
    start = min(cells, key=lambda c: (cheb(c[0], c[1], s.x, s.y), c))
    comp, todo = {start}, [start]
    while todo:
        c = todo.pop()
        for dx, dy in D8:
            n = (c[0] + dx, c[1] + dy)
            if n in cells and n not in comp:
                comp.add(n)
                todo.append(n)
    # follow the stretch from one end to the other
    deg = lambda c: sum((c[0] + dx, c[1] + dy) in comp for dx, dy in D8[:4])
    end = min(comp, key=lambda c: (deg(c), c))
    line, left = [end], comp - {end}
    while left:
        c = line[-1]
        nxt = [n for n in left if cheb(n[0], n[1], c[0], c[1]) == 1]
        if not nxt:
            break
        n = min(nxt, key=lambda q: (abs(q[0] - c[0]) + abs(q[1] - c[1]), q))
        line.append(n)
        left.discard(n)
    cx, cy = m.w // 2, m.h // 2
    near = min(line, key=lambda c: (cheb(c[0], c[1], s.x, s.y), c))
    line = [c for j, c in enumerate(line) if j in (0, len(line) - 1) or c == near]   # the bend that matters, no loops
    pts = [(cx + (x - s.x) * k, cy + (y - s.y) * k) for x, y in line]
    if len(pts) == 1:
        pts = [(pts[0][0] - k, pts[0][1]), (pts[0][0] + k, pts[0][1])]
    for _ in range(3):                                  # round off the corners of the world map's grid
        out = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            out += [(a[0] * .75 + b[0] * .25, a[1] * .75 + b[1] * .25), (a[0] * .25 + b[0] * .75, a[1] * .25 + b[1] * .75)]
        pts = out + [pts[-1]]

    def beyond(a, b):                                    # carry on past b, the way a-b points, off the map
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = max(1e-6, (dx * dx + dy * dy) ** .5)
        return (b[0] + dx / n * (m.w + m.h), b[1] + dy / n * (m.w + m.h))
    return [beyond(pts[1], pts[0])] + pts + [beyond(pts[-2], pts[-1])]


def carve_river(m, pts, half=2.2, keep=()):
    """Lay a river along the points: deep in the middle, shallow at the banks. Where a road crosses it, a bridge."""
    keep = set(keep) | {FOUNTAIN, STALL, WELL}
    wet = set()
    crossed = set()
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        # only the part of the segment that is on the map
        n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
        wob = random.random() * 6.28
        for j in range(n + 1):
            t = j / n
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            if not (-4 <= x < m.w + 4 and -4 <= y < m.h + 4):
                continue
            hw = half + .5 * math.sin(wob + (x + y) / 7)
            for yy in range(int(y - hw - 1), int(y + hw + 2)):
                for xx in range(int(x - hw - 1), int(x + hw + 2)):
                    if not m.inb(xx, yy):
                        continue
                    d = ((xx - x) ** 2 + (yy - y) ** 2) ** .5
                    if d > hw + .4:
                        continue
                    t0 = m.tile(xx, yy)
                    if t0 in keep or t0 == WATER:
                        continue
                    if t0 in (PATH, D.BRIDGE):
                        crossed.add((xx, yy))
                    m.set(xx, yy, WATER if d <= hw - .7 else SHALLOW)
                    wet.add((xx, yy))
    lay_bridges(m, pts, crossed, 3 if half >= 2.2 else 2)
    return wet


def lay_bridges(m, pts, crossed, width):
    """One straight bridge where each road met the water, square across the river from bank to bank,
    with a bit of lane joining it to the road on either side."""
    left = set(crossed)
    while left:
        group, todo = set(), [left.pop()]
        while todo:
            c = todo.pop()
            group.add(c)
            for dx, dy in D8:
                n = (c[0] + dx, c[1] + dy)
                if n in left:
                    left.discard(n)
                    todo.append(n)
        gx = sum(c[0] for c in group) / len(group)
        gy = sum(c[1] for c in group) / len(group)
        # which way the river runs here: along the nearest stretch of its course
        best = None
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            vx, vy = x1 - x0, y1 - y0
            ll = vx * vx + vy * vy or 1
            t = max(0.0, min(1.0, ((gx - x0) * vx + (gy - y0) * vy) / ll))
            d = (x0 + vx * t - gx) ** 2 + (y0 + vy * t - gy) ** 2
            if best is None or d < best[0]:
                best = (d, vx, vy, x0 + vx * t, y0 + vy * t)
        _d, vx, vy, rx, ry = best
        across = (1, 0) if abs(vy) >= abs(vx) else (0, 1)          # the deck runs across the flow
        side = (across[1], across[0])
        mid = (round(rx), round(ry))
        mid = (mid[0], round(gy)) if across == (1, 0) else (round(gx), mid[1])
        rows = []
        for k in range(-(width // 2), width - width // 2):
            ox, oy = mid[0] + side[0] * k, mid[1] + side[1] * k
            if not m.inb(ox, oy) or m.tile(ox, oy) not in (WATER, SHALLOW):
                continue
            ends = []
            for sgn in (-1, 1):
                j = 0
                while j < 40 and m.inb(ox + across[0] * (j + 1) * sgn, oy + across[1] * (j + 1) * sgn) and \
                        m.tile(ox + across[0] * (j + 1) * sgn, oy + across[1] * (j + 1) * sgn) in (WATER, SHALLOW):
                    j += 1
                ends.append(j * sgn)
            rows.append((ox, oy, ends))
        if not rows or any(abs(e) >= 40 for _x, _y, ends in rows for e in ends):
            continue
        lo = min(ends[0] for _x, _y, ends in rows)
        hi = max(ends[1] for _x, _y, ends in rows)
        for ox, oy, _e in rows:                 # every plank the same length: a square deck
            for j in range(lo, hi + 1):
                x, y = ox + across[0] * j, oy + across[1] * j
                if m.inb(x, y):
                    m.set(x, y, D.BRIDGE)
            for j, sgn in ((lo - 1, -1), (hi + 1, 1)):
                x, y = ox + across[0] * j, oy + across[1] * j
                if m.inb(x, y) and m.tile(x, y) in (GRASS, TREE, FIELD):
                    m.set(x, y, PATH)
                if m.inb(x, y):
                    join_road(m, x, y, (across[0] * sgn, across[1] * sgn))


def join_road(m, x, y, out):
    """From a bridge end, lay lane to the nearest road cell on this side of the water (if one is near)."""
    roads = [(cheb(xx, yy, x, y), xx, yy) for yy in range(y - 12, y + 13) for xx in range(x - 12, x + 13)
             if m.inb(xx, yy) and (xx, yy) != (x, y) and m.tile(xx, yy) == PATH
             and (xx - x) * out[0] + (yy - y) * out[1] >= 0]
    if not roads:
        return
    _d, tx, ty = min(roads)
    cx, cy = x, y
    while (cx, cy) != (tx, ty):
        if cx != tx and (out[0] or cy == ty):      # first away from the water, then along the bank
            cx += 1 if tx > cx else -1
        else:
            cy += 1 if ty > cy else -1
        if m.tile(cx, cy) in (WATER, SHALLOW, D.BRIDGE):
            return
        if m.tile(cx, cy) in (GRASS, TREE, FIELD):
            m.set(cx, cy, PATH)


def river_banks(m, wet):
    """Thin out the trees along the banks, so the water shows."""
    for x, y in wet:
        for dx, dy in D8[:4]:
            if m.inb(x + dx, y + dy) and m.tile(x + dx, y + dy) == TREE and random.random() < .5:
                m.set(x + dx, y + dy, GRASS)


TIER = {   # size of the map, homes, fields/pastures/orchards, square
    'hamlet': ((88, 58), (4, 7), ((5, 2, 1)), None),
    'village': ((112, 72), (14, 19), ((14, 4, 3)), 'green'),
    'town': ((136, 88), (26, 32), ((16, 5, 3)), 'square'),
}


def gen_village(game, s):
    """A hamlet, village or town in open country: roads that go where the roads on the world map go,
    houses along them, a green or a market square where they meet, farmland and woods around."""
    tier = s.kind if s.kind in TIER else 'village'
    (w, h), (hmin, hmax), (nf, npast, norch), square = TIER[tier]
    if tier == 'town' and getattr(s, 'race', '') == 'halfling':
        w, h = 164, 104                          # room for the hedge, the hills inside it and the fields beyond
    m = GameMap(s.map_key, 'town', s.name, w, h, GRASS)
    m.radius, m.sid, m.hid, m.signs = 60, s.id, None, []
    wooded(m, game=game, s=s)
    cx, cy = w // 2, h // 2
    # the roads out, one for every road on the world map; the two busiest are three wide
    dirs = road_dirs(game, s) or [(-1, 0, None)]
    m.exits = []
    for k, (dx, dy, other) in enumerate(dirs):
        ex, ey = edge_point(m, cx, cy, dx, dy)
        near = next((e for e in m.exits if cheb(e[0], e[1], ex, ey) < 14), None)
        if near:                                    # two roads leaving the same way share one
            m.exits.append((near[0], near[1], other))
            continue
        pts = meander((cx, cy), (ex, ey), 6, 1, abs(ex - cx) >= abs(ey - cy))
        lay_road(m, pts, 3 if k < 2 and tier != 'hamlet' else 2)
        m.exits.append((ex, ey, other))
    names = town_names(getattr(s, 'race', 'human'))
    plots = []
    # where the roads meet: a green with a well, a paved market square with a fountain, or just a bend
    if square == 'green':
        for yy in range(cy - 7, cy + 8):
            for xx in range(cx - 10, cx + 11):
                if ((xx - cx) / 10) ** 2 + ((yy - cy) / 7) ** 2 < 1 and m.tile(xx, yy) != PATH:
                    m.set(xx, yy, GRASS)
        for yy in range(cy - 3, cy + 4):            # the market corner of the green, paved
            for xx in range(cx + 2, cx + 10):
                m.set(xx, yy, PATH)
        m.set(cx - 4, cy - 4, WELL)
        stalls = [(cx + 3, cy + 3), (cx + 4, cy + 3), (cx + 7, cy + 3), (cx + 8, cy + 3)]
        plots.append(Plot(cx - 11, cy - 8, 23, 17, 'green'))
        trader_spot = (cx + 5, cy + 2)
    elif square == 'square':
        for yy in range(cy - 6, cy + 7):
            for xx in range(cx - 11, cx + 12):
                m.set(xx, yy, PATH)
        m.set(cx, cy, FOUNTAIN)
        stalls = [(cx - 9, cy - 4), (cx - 8, cy - 4), (cx - 5, cy - 4), (cx + 5, cy + 4), (cx + 8, cy + 4), (cx + 9, cy + 4),
                  (cx - 9, cy + 4), (cx - 8, cy + 4), (cx + 8, cy - 4), (cx + 9, cy - 4)]
        plots.append(Plot(cx - 12, cy - 7, 25, 15, 'square'))
        trader_spot = (cx - 8, cy - 3)
    else:
        stalls = []
        plots.append(Plot(cx - 3, cy - 3, 7, 7, 'crossing'))
        trader_spot = None
    for c in stalls:
        m.set(c[0], c[1], STALL)
    halfling = getattr(s, 'race', '') == 'halfling'
    if halfling:
        m.round_doors = True
        m.wall_fg = (186, 140, 90)               # timber and plaster
        if tier == 'town':                       # a lane round the town inside the hedge, with houses and hills along it
            from .folk import ring
            rcx, rcy, rrx, rry = ring(m)
            for j in range(900):
                ang = j / 900 * math.tau
                x, y = round(rcx + math.cos(ang) * (rrx - 14)), round(rcy + math.sin(ang) * (rry - 11))
                if m.tile(x, y) in (GRASS, TREE):
                    m.set(x, y, PATH)
    # a river that runs past the village on the world map runs through it here, with bridges where the roads cross
    course = river_course(game, s, m, 9 if tier == 'hamlet' else 12)
    wet = carve_river(m, course, 1.8 if tier == 'hamlet' else 2.3) if course else set()
    river_banks(m, wet)
    m.stone_bridges = tier == 'town'
    from . import harbour as HB
    if getattr(s, 'harbour', False):
        plots.append(HB.carve(m, s))
    if s.id == 0 or (tier != 'hamlet' and random.random() < .3 and not wet):
        pond = fishing_pond(game, m, plots, cy, names, fisher=s.id == 0)
        if pond:
            plots.append(pond)
    roads = road_cells(m)
    near_road = [c for c in roads if 6 < c[0] < w - 6 and 6 < c[1] < h - 6 and cheb(c[0], c[1], cx, cy) < (16 if tier == 'hamlet' else 40)]
    kinds = [k for k in ('inn', 'shop', 'temple', 'stables') if k in s.services]
    if s.id == 0 or tier in ('village', 'hamlet'):
        kinds.append('elder')                    # the elder: Berend in Thornfield, and work for the village elsewhere
    from . import guilds as GU
    lodges = [k for k in GU.halls_in(game, s.id) if not GU.GUILDS[k]['secret'] and k != 'anglers']
    kinds += ['lodge:' + k for k in lodges]
    smials = []
    hedged = halfling and tier == 'town'
    if halfling:                                 # halflings dig their homes into the hills, or build round-doored houses
        from . import folk as FK
        smials = FK.dig_hills(game, m, plots, near_road, tier)
        if tier == 'town':
            kinds.append('keepsake')
    kinds += ['home'] * max(2, random.randint(hmin, hmax) - len(smials))
    buildings = []
    for k in kinds:
        for _ in range(500):
            rx, ry = random.choice(near_road)
            pl = house_plot('shop' if k.startswith('lodge:') else k, rx + random.randint(-15, 5), ry + random.randint(-12, 5))
            if k.startswith('lodge:'):
                pl.kind, pl.guild = 'keep', k[6:]
            bx = plot_box(pl)
            if bx.x < 3 or bx.y < 3 or bx.x + bx.w > w - 3 or bx.y + bx.h > h - 3:
                continue
            if any(bx.overlaps(o, 2) for o in plots):
                continue
            cells = [(xx, yy) for yy in range(bx.y - 1, bx.y + bx.h + 1) for xx in range(bx.x - 1, bx.x + bx.w + 1)]
            if any(c in roads or c in wet for c in cells):
                continue
            if any(m.tile(*c) in (D.SLOPE, D.EARTH, D.BRIDGE, WATER) for c in cells if m.inb(*c)):
                continue
            if hedged and not all(FK.in_ring(m, x, y) for x, y in ((bx.x, bx.y), (bx.x + bx.w, bx.y), (bx.x, bx.y + bx.h),
                                                                    (bx.x + bx.w, bx.y + bx.h))):
                continue                            # a halfling town keeps its houses inside its hedge
            if min(cheb(c[0], c[1], bx.x + bx.w // 2, bx.y + bx.h // 2) for c in near_road) > 9:
                continue                            # houses stand by the road, not off in the woods
            plots.append(bx)
            buildings.append(pl)
            break
    for pl in buildings:
        build_house(m, pl)
        tgt = min(roads, key=lambda c: cheb(c[0], c[1], pl.x + pl.w // 2, pl.y + pl.h // 2))
        out = place_door(m, pl, tgt[0], tgt[1])
        carve_path(m, out, tgt)
        furnish(m, pl)
        if getattr(pl, 'guild', None):
            add_sign(m, pl, GU.GUILDS[pl.guild]['name'])
        elif pl.kind in SIGN:
            add_sign(m, pl, SIGN[pl.kind])
        if pl.kind == 'home' and random.random() < .55 and not (
                hedged and not (FK.in_ring(m, pl.x, pl.y - 6) and FK.in_ring(m, pl.x + pl.w, pl.y + pl.h + 6))):
            gd = garden(m, pl, -1 if tgt[1] > pl.y + pl.h // 2 else 1, plots)
            if gd:
                plots.append(gd)
    for pl in smials:
        furnish(m, pl)
    buildings += smials
    fields, pastures = farmland(game, m, plots, -999, names, want=[('field', nf), ('pasture', npast), ('orchard', norch)],
                                avoid=(lambda fx, fy, fw, fh: not FK.outside_ring(m, fx, fy, fw, fh)) if hedged else None)
    fields = fields + pastures
    if halfling:
        FK.hedges(m, tier)
    # street lamps along the roads, round the square and by the doors that matter
    lamp_spots = []
    if tier != 'hamlet':
        for (x, y) in sorted(roads)[::7]:
            for ox, oy in ((0, -2), (0, 2), (-2, 0), (2, 0)):
                if m.inb(x + ox, y + oy) and m.tile(x + ox, y + oy) == GRASS and cheb(x, y, cx, cy) < 40:
                    lamp_spots.append((x + ox, y + oy))
                    break
        lamp_spots += [(cx - 3, cy - 4), (cx + 8, cy + 2)]
    for pl in buildings:
        if pl.kind in ('inn', 'temple', 'elder') and pl.door:
            dx, dy = pl.door
            lamp_spots += [(dx + 2, dy + (1 if dy >= pl.y + pl.h - 1 else -1))]
    place_lamps(m, lamp_spots)
    hearths(m, buildings)
    # the people who run things
    for pl in buildings:
        if getattr(pl, 'guild', None):
            GU.place_master(game, m, pl, pl.guild, names)
        elif pl.kind in ROLE_OF:
            staff(game, m, pl, pl.kind, names, s)
    newsfolk(game, m, s, buildings, names)
    from . import mercs as MC
    MC.place_recruits(game, m, s, buildings, names)
    if getattr(s, 'harbour', False):
        HB.furnish(game, m, s, names)
    homes = [p for p in buildings if p.kind == 'home']
    old_fisher = next((o for o in m.mons if o.role == 'fisher'), None)
    if old_fisher and homes:                       # the fisherman keeps hours too: out on his jetty by day, home at night
        beds = [c for c in homes[-1].inside if m.tile(*c) in (FLOOR, PLANK)]
        if beds:
            old_fisher.home_pos, old_fisher.work_pos = random.choice(beds), (old_fisher.x, old_fisher.y)
            old_fisher.job, old_fisher.path = 'fisher', []
    nm, col = TITLE['market']
    if trader_spot:
        m.set(*trader_spot, PATH if square == 'square' else GRASS)
        m.mons.append(make_npc(game, nm.format(n=names.pop()), 'market', col, trader_spot[0], trader_spot[1], True))
        if square == 'square':
            m.mons.append(make_npc(game, nm.format(n=names.pop()), 'market', col, cx + 8, cy + 3, True))
    elif homes:                                    # in a hamlet the farmer sells from his own kitchen
        spot = free_inside(m, homes[0])
        if spot:
            m.mons.append(make_npc(game, f'Farmer {names.pop()}', 'market', col, spot[0][0], spot[0][1], True))
            homes = homes[1:]
    inn = next((p for p in buildings if p.kind == 'inn'), None)
    street_cells = sorted(near_road)
    for i, pl in enumerate(homes):
        beds = [c for c in pl.inside if m.tile(*c) in (FLOOR, PLANK)]
        if i == 0 and tier != 'hamlet':
            townsfolk(game, m, beds, (cx, cy + 1), names, 'lamplighter', fg='#e0c080')
            continue
        for _ in range(random.randint(1, 2)):
            r = random.random()
            if r < .5 and fields:
                work, job = random.choice(random.choice(fields)), random.choice(['farmer', 'farmer', 'shepherd'])
            elif r < .6:
                work, job = (cx + random.randint(-6, 6), cy + random.randint(-5, 5)), 'child'
            elif r < .75 and inn:
                work, job = random.choice(free_inside(m, inn) or [inn.door]), 'drinker'
            else:
                work = random.choice(street_cells)
                job = random.choice(JOBS)
            if not m.inb(*work) or not D.TILES[m.tile(*work)].walk:
                work = (cx, cy)
            townsfolk(game, m, beds, work, names, job, fg='#c8b8a0' if job == 'child' else '#a8aab4')
    for k in range(2 if tier != 'hamlet' else 1):
        c = rand_free(game, m, lambda t: t == GRASS)
        if c:
            m.mons.append(make_npc(game, 'A village dog' if k == 0 else 'A cat', 'dog', '#c8a070' if k == 0 else '#a0a0a0',
                                   c[0], c[1], False, ch='d' if k == 0 else 'c'))
    pp = next(((cx + dx, cy + dy) for dx, dy in ((2, -3), (-3, 2), (3, 3), (-2, -2), (4, 0))
               if m.inb(cx + dx, cy + dy) and m.tile(cx + dx, cy + dy) in (GRASS, PATH)), (cx, cy))
    name_buildings(game, m, s)
    m.portal_pos = pp
    m.entry = m.exits[0][:2]
    m.centre = (cx, cy)
    for i in range(len(m.seen)):
        m.seen[i] = 1
    return m


# ------------------------------------------------------------------ cities
def gen_city(game, s):
    big = s.kind == 'metropolis'
    w, h = (196, 110) if big else (150, 80)
    m = GameMap(s.map_key, 'town', s.name, w, h, GRASS)
    m.radius, m.sid, m.hid, m.signs = 60, s.id, None, []
    for x in range(w):
        for y in (0, h - 1):
            m.set(x, y, WALL)
    for y in range(h):
        for x in (0, w - 1):
            m.set(x, y, WALL)
    if big:
        streets_y = [h // 5, 2 * h // 5, h // 2, 3 * h // 5, 4 * h // 5]
        streets_x = [w // 8 * k for k in range(1, 8)]
    else:
        streets_y = [h // 4, h // 2, 3 * h // 4]
        streets_x = [w // 6, 2 * w // 6, w // 2, 4 * w // 6, 5 * w // 6]
    for y in streets_y:
        for x in range(1, w - 1):
            m.set(x, y, PATH)
    for x in streets_x:
        for y in range(1, h - 1):
            m.set(x, y, PATH)
    hy, hx = streets_y[len(streets_y) // 2], streets_x[len(streets_x) // 2]
    for x in range(1, w - 1):           # the high street and the market way are three wide
        for d in (-1, 1):
            m.set(x, hy + d, PATH)
    for y in range(1, h - 1):
        for d in (-1, 1):
            m.set(hx + d, y, PATH)
    # gates where the roads of the world map come in
    m.exits = []
    for dx, dy, other in (road_dirs(game, s) or [(-1, 0, None)]):
        ex, ey = edge_point(m, w // 2, h // 2, dx, dy)
        if ex in (0, w - 1):
            ey = min(streets_y, key=lambda v: abs(v - ey))
        else:
            ex = min(streets_x, key=lambda v: abs(v - ex))
        m.set(ex, ey, PATH)
        m.exits.append((ex, ey, other))
    gy = m.exits[0][1]
    # plaza
    px, py = hx, (streets_y[len(streets_y) // 2 - 1] + hy) // 2
    for yy in range(py - 3, py + 4):
        for xx in range(px - 8, px + 9):
            m.set(xx, yy, PATH)
    m.set(px, py, FOUNTAIN)
    course = river_course(game, s, m, 14)
    if course:
        carve_river(m, course, 3.0)
    m.stone_bridges = True
    names = town_names(getattr(s, 'race', 'human'))
    plots = [Plot(px - 9, py - 4, 19, 9, 'plaza')]
    from . import harbour as HB
    if getattr(s, 'harbour', False):
        plots.append(HB.carve(m, s))
    stall_spots = [(px - 6, py - 2), (px - 6, py + 2), (px + 6, py - 2), (px + 6, py + 2), (px - 3, py - 3), (px + 3, py + 3)]
    for c in stall_spots:
        m.set(c[0], c[1], STALL)
    kinds = ['inn', 'inn', 'inn', 'shop', 'shop', 'temple', 'stables', 'barracks', 'barracks'] + ['home'] * 58
    if big:
        kinds = ['inn'] * 5 + ['shop'] * 3 + ['temple', 'temple', 'stables', 'barracks', 'barracks', 'barracks'] + ['home'] * 110
    from . import guilds as GU
    kinds = ['guild:' + k for k in GU.halls_in(game, s.id) if k != 'anglers'] + kinds
    buildings = []
    for k in kinds:
        for _ in range(300):
            x0, y0 = random.randint(2, w - 16), random.randint(2, h - 12)
            gk = k[6:] if k.startswith('guild:') else None
            if gk:            # a guild hall looks like a keep; a secret den like any other house
                secret = GU.GUILDS[gk]['secret']
                pl = house_plot('home' if secret else 'inn', x0, y0)
                pl.kind, pl.guild = ('home' if secret else 'keep'), gk
            else:
                pl = house_plot('inn' if k == 'barracks' else k, x0, y0)
                pl.kind = k
            bx = plot_box(pl)
            cells = [(xx, yy) for yy in range(bx.y - 1, bx.y + bx.h + 1) for xx in range(bx.x - 1, bx.x + bx.w + 1)]
            if bx.x < 2 or bx.x + bx.w > w - 2 or bx.y + bx.h > h - 2:
                continue
            if any(m.tile(*c) in (PATH, WALL, STALL, FOUNTAIN, WATER, SHALLOW, D.BRIDGE) for c in cells) or \
                    any(bx.overlaps(o, 1) for o in plots):
                continue
            plots.append(bx)
            buildings.append(pl)
            break
    for pl in buildings:
        build_house(m, pl)
        tx = min(streets_x, key=lambda sx: abs(sx - (pl.x + pl.w // 2)))
        ty = min(streets_y, key=lambda sy_: abs(sy_ - (pl.y + pl.h // 2)))
        if abs(ty - (pl.y + pl.h // 2)) <= abs(tx - (pl.x + pl.w // 2)):
            out = place_door(m, pl, pl.x + pl.w // 2, ty)
            carve_path(m, out, (out[0], ty))
        else:
            out = place_door(m, pl, tx, pl.y + pl.h // 2)
            carve_path(m, out, (tx, out[1]))
        furnish(m, pl)
        if getattr(pl, 'guild', None):
            if GU.GUILDS[pl.guild]['sign']:               # the secret ones hang out no sign
                add_sign(m, pl, GU.GUILDS[pl.guild]['name'])
        elif pl.kind in SIGN:
            add_sign(m, pl, SIGN[pl.kind])
    for i in range(len(m.t)):
        if m.t[i] == GRASS and random.random() < .008:
            m.t[i] = TREE
    spots = []
    for y in streets_y:
        spots += [(x, y + (2 if y == streets_y[1] else 1) * (1 if (x // 10) % 2 else -1)) for x in range(5, w - 5, 10)]
    for x in streets_x:
        spots += [(x + (2 if x == streets_x[2] else 1) * (1 if (y // 9) % 2 else -1), y) for y in range(5, h - 5, 9)]
    place_lamps(m, spots)
    streets = [(x, y) for x in streets_x for y in range(2, h - 2)] + [(x, y) for y in streets_y for x in range(2, w - 2)]
    people_city(game, m, s, buildings, names, px, py, stall_spots, streets, 14 if big else 9)
    ex, ey = m.exits[0][:2]
    m.entry = (ex, ey)
    for i in range(len(m.seen)):
        m.seen[i] = 1
    return m


def people_city(game, m, s, buildings, names, px, py, stall_spots, streets, n_guards, guard_name=None, harbour=True):
    """Fill a city with its people: those who run things, the townsfolk with their days, the watch."""
    from . import guilds as GU
    hearths(m, buildings)
    first = {}
    for pl in buildings:
        if getattr(pl, 'guild', None):
            GU.place_master(game, m, pl, pl.guild, names)
    GU.reveal_master(game, m)
    for pl in buildings:
        if getattr(pl, 'guild', None) and pl.kind == 'keep':
            continue
        if pl.kind in ROLE_OF and pl.kind not in first:
            first[pl.kind] = staff(game, m, pl, pl.kind, names, s)
        elif pl.kind == 'inn':
            spots = free_inside(m, pl)
            if spots:
                m.mons.append(make_npc(game, f'Innkeeper {names.pop()}', 'inn', '#e0a060', spots[0][0], spots[0][1], True))
    newsfolk(game, m, s, buildings, names)
    from . import mercs as MC
    MC.place_recruits(game, m, s, buildings, names)
    nm, col = TITLE['market']
    for c in stall_spots[:3]:
        spot = (c[0], c[1] + (1 if c[1] > py else -1)) if c[1] != py else (c[0] + 1, c[1])
        if m.tile(*spot) == PATH and not m.mon_at(*spot):
            m.mons.append(make_npc(game, nm.format(n=names.pop()), 'market', col, spot[0], spot[1], True))
            break
    homes = [p for p in buildings if p.kind == 'home']
    inns = [p for p in buildings if p.kind == 'inn']
    plaza_cells = [(xx, yy) for yy in range(py - 3, py + 4) for xx in range(px - 8, px + 9) if m.tile(xx, yy) in (PATH, PLANK)]
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
                work, job = random.choice(streets), 'any'
            if not D.TILES[m.tile(*work)].walk:
                work = (px, py + 1)
            townsfolk(game, m, beds, work, names, job, ch='☺',
                      fg='#c8b8a0' if job == 'child' else '#a8aab4')
    if homes:
        beds = [c for c in homes[0].inside if m.tile(*c) in (FLOOR, PLANK)]
        for _ in range(2):
            townsfolk(game, m, beds, (px, py + 1), names, 'lamplighter', fg='#e0c080')
    barracks = next((p for p in buildings if p.kind == 'barracks'), None)
    gfg = D.FACTIONS[s.faction]['fg']
    gname = guard_name or f"A {D.FACTIONS[s.faction]['short']} guard"
    for i in range(n_guards):
        home = free_inside(m, barracks) if barracks else [(px, py + 1)]
        post = random.choice(streets) if i % 2 else (px + random.randint(-7, 7), py + random.choice([-3, 3]))
        if not m.inb(*post) or not D.TILES[m.tile(*post)].walk:
            post = (px, py + 1)
        g = townsfolk(game, m, home, post, [gname], 'guard', fg=gfg, role='guard')
        g.name = gname
        g.night_watch = i < 2
    if harbour and getattr(s, 'harbour', False):
        from . import harbour as HB
        HB.furnish(game, m, s, names)
    name_buildings(game, m, s)
    m.portal_pos = (px + 2, py + 1)
    m.centre = (px, py + 4)


def gen_settlement_map(game, s):
    if s.kind == 'deephold':
        from .deephold import gen_deephold
        return gen_deephold(game, s)
    if getattr(s, 'dwarven', False):
        from .deephold import gen_village as gen_dwarf_village
        m = gen_dwarf_village(game, s)
    elif getattr(s, 'elder', False):
        from .folk import gen_elder_city
        m = gen_elder_city(game, s)
    else:
        m = gen_city(game, s) if s.is_city else gen_village(game, s)
    place_signpost(m)
    return m


def place_signpost(m):
    """A signpost where the roads meet (or by the road in), telling where the roads lead."""
    if getattr(m, 'centre', None):
        cx, cy = m.centre
        spots = [(cx + dx, cy + dy) for r in range(2, 12) for dx in range(-r, r + 1) for dy in (-r, r)]
        for x, y in spots:
            if m.inb(x, y) and m.tile(x, y) == GRASS and not m.mon_at(x, y) and any(
                    m.inb(x + a, y + b) and m.tile(x + a, y + b) == PATH for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                m.set(x, y, D.SIGNPOST)
                m.signpost = (x, y)
                return
    ex, ey = m.entry
    for dx in range(2, 8):
        for dy in (-1, 1, -2, 2):
            x, y = ex + dx, ey + dy
            if m.inb(x, y) and m.tile(x, y) in (GRASS, PATH, D.FLOOR) and not m.mon_at(x, y):
                m.set(x, y, D.SIGNPOST)
                m.signpost = (x, y)
                return


def embed(m, W, H, fields=True):
    """Set a small map in the middle of a bigger stretch of countryside: woods, a few fields and the road in.
    Everything on the small map moves with it."""
    if m.w >= W and m.h >= H:
        return m
    W, H = max(W, m.w), max(H, m.h)
    ox, oy = (W - m.w) // 2, (H - m.h) // 2
    big = GameMap(m.key, m.kind, m.name, W, H, GRASS)
    wooded(big, belt=10, inner=.012)
    ex, ey = m.entry if m.entry else (0, m.h // 2)
    # the road in, from the edge of the big map to where the old one began
    lay_road(big, meander((0, ey + oy), (ex + ox, ey + oy), 5, 1, True), 1)
    for y in range(m.h):
        for x in range(m.w):
            big.t[(y + oy) * W + x + ox] = m.t[y * m.w + x]
    st = m.__dict__.copy()
    for k in ('w', 'h', 't', 'seen', '_look', '_look_t', '_light', '_light_dom', '_light_dyn'):
        st.pop(k, None)
    big.__dict__.update(st)
    big.w, big.h = W, H
    big.seen = bytearray([1]) * (W * H) if m.seen and min(m.seen) == 1 else bytearray(W * H)
    for o in big.mons + big.items:
        o.x += ox
        o.y += oy
        for a in ('home_pos', 'work_pos'):
            if hasattr(o, a) and getattr(o, a):
                v = getattr(o, a)
                setattr(o, a, (v[0] + ox, v[1] + oy))
        if hasattr(o, 'path'):
            o.path = []
    big.signs = [(x + ox, y + oy, t) for x, y, t in getattr(m, 'signs', [])]
    if getattr(m, 'hang', None):
        big.hang = {(x + ox, y + oy): v for (x, y), v in m.hang.items()}
    if getattr(m, 'buildings', None):
        big.buildings = []
        for b in m.buildings:
            b = dict(b)
            x, y, w_, h_ = b['box']
            b['box'] = (x + ox, y + oy, w_, h_)
            b['door'] = (b['door'][0] + ox, b['door'][1] + oy)
            if 'hang' in b:
                b['hang'] = (b['hang'][0] + ox, b['hang'][1] + oy)
            big.buildings.append(b)
    big.entry = (0, ey + oy)
    if m.portal_pos:
        big.portal_pos = (m.portal_pos[0] + ox, m.portal_pos[1] + oy)
    if getattr(m, 'lamps', None):
        big.lamps = [(x + ox, y + oy) for x, y in m.lamps]
    if getattr(m, 'lights', None):
        big.lights = [(x + ox, y + oy) + tuple(rest) for x, y, *rest in m.lights]
    if getattr(m, 'signpost', None):
        big.signpost = (m.signpost[0] + ox, m.signpost[1] + oy)
    if fields:                                  # a few fields and meadows on the land around
        plots = [Plot(ox - 1, oy - 1, m.w + 2, m.h + 2, 'site')]
        for _ in range(60):
            fw, fh = random.randint(8, 14), random.randint(5, 8)
            fx, fy = random.randint(10, W - fw - 10), random.randint(10, H - fh - 10)
            fp = Plot(fx, fy, fw, fh, 'field')
            if any(fp.overlaps(o, 2) for o in plots):
                continue
            if any(big.tile(xx, yy) == PATH for yy in range(fy - 1, fy + fh + 1) for xx in range(fx - 1, fx + fw + 1)):
                continue
            plots.append(fp)
            for yy in range(fy, fy + fh):
                for xx in range(fx, fx + fw):
                    edge = yy in (fy, fy + fh - 1) or xx in (fx, fx + fw - 1)
                    big.set(xx, yy, FENCE if edge else FIELD)
            big.set(fx + fw // 2, fy if fy > oy else fy + fh - 1, GRASS)
            if len(plots) > 5:
                break
    return big


# ------------------------------------------------------------------ strongholds
def gen_hold_map(game, hd, hostile):
    """A castle or fort, out in its own stretch of land."""
    return embed(_hold_map(game, hd, hostile), 96, 62)


def _hold_map(game, hd, hostile):
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


_PASS = None


def path_between(m, a, b):
    """A short walking route for townsfolk (A* with a straight-line guess; the first 60 steps)."""
    global _PASS
    if _PASS is None:
        _PASS = [t.walk or t.door for t in D.TILES]
    w, h = m.w, m.h
    start, goal = a[1] * w + a[0], b[1] * w + b[0]
    gx, gy = b
    prev = {start: None}
    cost = {start: 0}
    pq = [(max(abs(a[0] - gx), abs(a[1] - gy)), 0, start)]
    t = m.t
    found = False
    while pq:
        _f, d, c = heapq.heappop(pq)
        if c == goal:
            found = True
            break
        if d > cost[c]:
            continue
        x, y = c % w, c // w
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
            nx, ny = x + dx, y + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            ni = ny * w + nx
            if not _PASS[t[ni]]:
                continue
            nd = d + 1
            if nd < cost.get(ni, 1 << 30):
                cost[ni] = nd
                prev[ni] = c
                heapq.heappush(pq, (nd + max(abs(nx - gx), abs(ny - gy)), nd, ni))
    if not found:
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
    if getattr(m, 'lamps', None) and not any(getattr(o, 'job', '') == 'lamplighter' for o in m.mons):
        want = lamps_wanted(game)            # no lamplighter here: the monks or the guards see to the lamps
        if (len(m.lamp_on) == len(m.lamps)) != want:
            m.lamp_on = set()
            for k in range(len(m.lamps)):
                set_lamp(m, k, want)
    for npc in m.mons:
        if npc.is_npc and npc.role == 'livestock' and random.random() < .25:
            game.random_step(npc)
            continue
        if not npc.is_npc or not hasattr(npc, 'work_pos'):
            continue
        if npc.job == 'lamplighter':
            tgt = lamplighter(game, m, npc)
            if tgt is None:
                continue
        else:
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
            from .lore import chatter
            game.say(n, chatter(game, n))
    # close doors behind people at night now and then
    if is_night(game) and random.random() < .05:
        for i, t in enumerate(m.t):
            if t == ODOOR and random.random() < .1:
                x, y = i % m.w, i // m.w
                if not m.mon_at(x, y) and (x, y) != (p.x, p.y):
                    m.t[i] = DOOR
