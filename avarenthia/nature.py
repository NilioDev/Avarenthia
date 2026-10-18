"""Nature and wonders: waterfalls, cascades, great falls, rapids, hot springs, a tidal causeway and the Frozen Stair,
and the wonders out of the old tales (the Drifting Isles, the Starwater, the Thunder Anvil, the Hollow Hill, the
Unwintering, the Undying Flame, the Drowned Bell, the Star Well, the Singing Stones, the Wisp Fen, the Singing
Sands, the Glowing Bay, the Green Well and the Stone Wood).

Each is one cell on the world map: a site (`world.sites`) with its own play map, made on the first visit and kept.
Which of them a world has and where is random per world; the water sites sit where a river leaves the hills.
Each gives the player one thing to do: a tile to bump or step on. Tides, moon, dusk and storms come from the clock.
"""
import math
import random

from . import data as D
from .worldgen import cheb

WATER_KINDS = ('falls', 'cascade', 'greatfalls', 'rapids', 'hotspring', 'causeway', 'frozenfalls')
WONDERS = ('isles', 'starwater', 'anvil', 'mound', 'unwintering', 'flame', 'bell', 'starwell', 'stones', 'wisps',
           'sands', 'bay', 'cenote', 'stonewood')
LOOK = {'falls': ('≡', (236, 248, 255)), 'cascade': ('≡', (196, 232, 250)), 'greatfalls': ('≡', (255, 255, 255)),
        'rapids': ('≈', (226, 242, 255)), 'hotspring': ('°', (190, 240, 228)), 'causeway': ('╫', (190, 160, 112)),
        'frozenfalls': ('≡', (210, 236, 255)), 'isles': ('▀', (176, 196, 150)), 'starwater': ('*', (200, 210, 255)),
        'anvil': ('↑', (226, 222, 150)), 'mound': ('∩', (120, 214, 100)), 'unwintering': ('♣', (150, 240, 150)),
        'flame': ('▲', (255, 170, 60)), 'bell': ('Ω', (150, 176, 210)), 'starwell': ('o', (200, 215, 255)),
        'stones': ('Π', (206, 196, 176)), 'wisps': ('∙', (140, 230, 210)), 'sands': ('░', (240, 214, 140)),
        'bay': ('≈', (110, 200, 255)), 'cenote': ('o', (110, 222, 170)), 'stonewood': ('♣', (178, 168, 146))}
DESC = {
    'falls': 'A waterfall where the river leaves the hills. A pool full of fish, and a hollow behind the falling water.',
    'cascade': 'A river falling in many low steps down a hillside, pool after pool. A cairn on top looks out far.',
    'greatfalls': 'A great curtain of water falling in a horseshoe, and spray that hangs like smoke. A lookout on the rim.',
    'rapids': 'White water over boulders. Stepping stones cross it, if your feet are sure.',
    'hotspring': 'Hot water out of the ground: bathe to heal, and it warms you in winter.',
    'causeway': 'A path of poles out to an islet with an old chapel. Only at low tide.',
    'frozenfalls': 'A waterfall in the cold north. In winter it freezes, and a ledge high up can be reached.',
    'isles': 'Rocks hanging in the air over a vale. A chain hangs down from one of them.',
    'starwater': 'A lake that shows the stars by day. A stair under it leads to its twin, far away.',
    'anvil': 'An iron spike on a hill where the lightning strikes. A weapon left there in a storm is blessed.',
    'mound': 'A green hill. At full moon a door opens in it, with music inside.',
    'unwintering': 'A patch of spring in the middle of the snow, with a herb that grows nowhere else.',
    'flame': 'Fire burning out of the bare rock, night and day. A blade worked in it holds its edge.',
    'bell': 'A lake with a bell under it that rings in a storm. Only then can you dive to the drowned chapel.',
    'starwell': 'An old well with stars in it by day. A coin and a wish; not always the wish you meant.',
    'stones': 'A ring of stones that hums at dusk. Sleep in the middle and dream of a hidden place.',
    'wisps': 'A marsh where blue lights drift at night. Follow them, to treasure or into the mire.',
    'sands': 'Dunes that hum underfoot. Where the hum is loudest, something lies buried.',
    'bay': 'A bay where the waves break in blue light on summer nights, and the fish bite better.',
    'cenote': 'A clear pool in a hole in the jungle floor. A rope leads down; offerings lie at the bottom.',
    'stonewood': 'A forest turned to stone. Amber lies in the grit, and now and then a fossil.',
}
FIXED = {'isles': 'The Drifting Isles', 'starwater': 'The Starwater', 'anvil': 'The Thunder Anvil', 'mound': 'The Hollow Hill',
         'unwintering': 'The Unwintering', 'flame': 'The Undying Flame', 'bell': 'The Drowned Bell',
         'starwell': 'The Star Well', 'stones': 'The Singing Stones', 'wisps': 'The Wisp Fen', 'sands': 'The Singing Sands',
         'bay': 'The Glowing Bay', 'cenote': 'The Green Well', 'stonewood': 'The Stone Wood'}
GREAT = ["The Thundering Stair", "The Bride's Veil", "The White Mare", "The Giant's Beard", "The Roaring Maid"]
WATER_A = ['White', 'Silver', 'Thunder', 'Raven', "Bride's", "Giant's", 'Grey', 'Moss', 'Echo', "Maiden's", "Old Man's",
           'Smoke', 'Hollow', 'Wolf', 'Heron', 'Otter', 'Alder', 'Ash', 'Kettle', 'Stag', 'Shining', 'Weeping']
SPRING_A = ['Steam', 'Warm', 'Mist', 'Sulphur', 'Healing', "Old Wives'", 'Kettle', 'Bathing', 'Hearth', 'Cloud']
SAINTS = ['Edda', 'Wendel', 'Corwen', 'Aldra', 'Brannoc', 'Ismay', 'Hilda', 'Ninian']
HIGH = {'mountain', 'hills', 'alpine', 'tundra_hills', 'canyon', 'mesa', 'karst', 'peak'}
COLD = {'tundra', 'taiga', 'glacier', 'tundra_hills', 'shrubland_cold', 'conifer'}
TIDE_HOURS = 12.4


# ------------------------------------------------------------------ the clock: moon, tide, dusk
def moon(day):
    """The moon's age in days, 0..27; full from 13 to 15."""
    return day % 28


def full_moon(game):
    return 13 <= moon(game.day) <= 15


def tide(game):
    """-1 (low) .. 1 (high): two tides a day, a little later each day."""
    hrs = game.turn * 24 / D.DAY_LEN
    return math.cos(hrs / TIDE_HOURS * math.tau)


def low_tide(game):
    return tide(game) < -.15


def hour(game):
    return (game.turn % D.DAY_LEN) * 24 / D.DAY_LEN


def dusk(game):
    from .seasons import dusk as SD
    h = hour(game)
    d = SD(game.day)
    return d - 1 <= h <= d + 2.5


def winter(game):
    from . import calendar as CAL
    return CAL.season(game.day) == 'winter'


def summer(game):
    from . import calendar as CAL
    return CAL.season(game.day) == 'summer'


def night(game):
    from .towns import is_night
    return is_night(game)


def storm_at(game, site):
    from . import weather as WX
    rid = game.world.region_of[site.y * game.maps['over'].w + site.x]
    return WX.region_weather(game, rid) in ('storm', 'downpour', 'drystorm')


# ------------------------------------------------------------------ where they lie
def _names(m):
    return getattr(m, 'biome_names', None) or []


def biome(m, x, y):
    n = _names(m)
    return n[m.biome[y * m.w + x]] if n else ''


def place(game, m, world, reach_set):
    """Put this world's falls, rapids, springs, causeways and wonders on the map."""
    from .sites import Site
    from .world import scaled
    w = m.w
    taken = [(s.x, s.y) for s in world.settlements] + [(q.x, q.y) for q in world.sites] + \
            [(d.x, d.y) for d in world.dungeons.values()] + [(h.x, h.y) for h in world.holds]
    used = world.__dict__.setdefault('used_names', set())
    riv = getattr(m, 'river', None) or bytearray(w * m.h)

    def free(x, y, gap=4):
        i = y * w + x
        return (3 <= x < w - 3 and 3 <= y < m.h - 3 and i in reach_set and D.TILES[m.t[i]].walk
                and m.t[i] not in (D.ROAD, D.TOWN, D.CITY, D.ENTR, D.RIVER) and i not in world.wonder_cells
                and all(cheb(x, y, a, b) >= gap for a, b in taken))

    def beside(x, y):
        for r in (1, 2):
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if free(x + dx, y + dy):
                        return x + dx, y + dy
        return None

    def add(kind, x, y, name):
        st = Site(len(world.sites), kind, x, y, name)
        st.faction = world.region_at(x, y).faction
        world.sites.append(st)
        taken.append((x, y))
        used.add(name)
        return st

    def name_of(kind, first=False):
        for _ in range(60):
            a = random.choice(WATER_A)
            nm = {'falls': random.choice([f'{a} Falls', f'The {a} Force', f'{a} Spout']),
                  'cascade': random.choice([f'The {a} Steps', f'{a} Cascade']),
                  'greatfalls': f'The {random.choice(["Roaring", "Endless", "Smoking", "Thundering", "White"])} Curtain',
                  'frozenfalls': 'The Frozen Stair' if first else f'{a} Falls',
                  'rapids': random.choice([f'The {a} Rapids', f'{a} Race']),
                  'hotspring': f'{random.choice(SPRING_A)} Springs',
                  'causeway': random.choice([f"Saint {random.choice(SAINTS)}'s Isle", f'{a} Isle', 'The Tide Isle'])}[kind]
            if first and kind == 'falls':
                nm = random.choice(GREAT)
            if nm not in used:
                return nm
        return f'{kind.capitalize()} {len(world.sites)}'

    # the steps where a river leaves the hills: falls, cascades, great falls, the Frozen Stair
    el = m.elev
    steps = []
    for i, v in enumerate(riv):
        if not v:
            continue
        x, y = i % w, i // w
        lower = [el[(y + dy) * w + x + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                 if m.inb(x + dx, y + dy) and riv[(y + dy) * w + x + dx]]
        if not lower:
            continue
        drop = el[i] - min(lower)
        high = sum(1 for dy in range(-2, 3) for dx in range(-2, 3) if m.inb(x + dx, y + dy) and biome(m, x + dx, y + dy) in HIGH)
        if drop >= 3 and high >= 3:
            steps.append((drop + random.random(), x, y))
    steps.sort(reverse=True)
    made = {'falls': 0, 'frozenfalls': 0, 'greatfalls': 0}
    picked = []
    for _d, x, y in steps:
        if len(picked) >= scaled(2) or any(cheb(x, y, a, b) < 22 for a, b in picked):
            continue
        spot = beside(x, y)
        if not spot:
            continue
        reg = world.region_at(x, y)
        cold = getattr(reg, 'climate', '') == 'cold' or biome(m, x, y) in COLD or any(
            biome(m, x + dx, y + dy) in COLD for dx in (-2, 0, 2) for dy in (-2, 0, 2) if m.inb(x + dx, y + dy))
        comp = _river_len(m, riv, x, y)
        if cold and made['frozenfalls'] < 2:
            kind = 'frozenfalls'
        elif comp >= 30 and not made['greatfalls']:
            kind = 'greatfalls'
        elif sum(1 for dy in range(-3, 4) for dx in range(-3, 4) if m.inb(x + dx, y + dy)
                 and biome(m, x + dx, y + dy) == 'hills') >= 12 and random.random() < .5:
            kind = 'cascade'
        else:
            kind = 'falls'
        st = add(kind, *spot, name_of(kind, first=not made.get(kind, 1)))
        st.river = (x, y)
        made[kind] = made.get(kind, 0) + 1
        picked.append((x, y))
    # rapids on hill rivers
    cells = [i for i, v in enumerate(riv) if v]
    random.shuffle(cells)
    n = scaled(1) + 1
    for i in cells:
        if n <= 0:
            break
        x, y = i % w, i // w
        if biome(m, x, y) != 'river' and not any(biome(m, x + dx, y + dy) in HIGH for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                                                 if m.inb(x + dx, y + dy)):
            continue
        if any(cheb(x, y, a, b) < 22 for a, b in picked):
            continue
        spot = beside(x, y)
        if spot:
            add('rapids', *spot, name_of('rapids'))
            picked.append((x, y))
            n -= 1
    # hot springs in the hills or the cold, causeways on the coast
    pool = list(reach_set)
    random.shuffle(pool)

    def put(kind, pred, count, gap=30):
        out = []
        for i in pool:
            if count <= 0:
                break
            x, y = i % w, i // w
            if not free(x, y) or not pred(x, y) or any(cheb(x, y, a, b) < gap for a, b in out):
                continue
            out.append(add(kind, x, y, FIXED.get(kind) or name_of(kind)))
            out[-1] = (x, y)
            count -= 1
        return out

    def near(x, y, names, r=2, k=1):
        return sum(1 for dy in range(-r, r + 1) for dx in range(-r, r + 1)
                   if m.inb(x + dx, y + dy) and biome(m, x + dx, y + dy) in names) >= k

    def coast(x, y):
        return any(m.inb(x + dx, y + dy) and m.t[(y + dy) * w + x + dx] == D.WATER and biome(m, x + dx, y + dy) != 'lake'
                   for dx in (-1, 0, 1) for dy in (-1, 0, 1))
    put('hotspring', lambda x, y: near(x, y, {'hotpool', 'sinter', 'geyser', 'volcano', 'ashland'}, 3)
            or near(x, y, HIGH | COLD, 2, 8) and random.random() < .2, scaled(1) + 1)
    put('causeway', coast, 1 + (random.random() < .5))
    # the wonders out of the old tales: each at most once, some worlds lack some
    preds = {
        'isles': lambda x, y: biome(m, x, y) in ('forest', 'meadow', 'desert', 'savanna', 'steppe', 'grass', 'hills', 'shrubland',
                                                 'birch', 'moor', 'dry_forest'),
        'anvil': lambda x, y: biome(m, x, y) in ('hills', 'moor', 'alpine', 'badlands', 'steppe'),
        'mound': lambda x, y: biome(m, x, y) in ('meadow', 'grass', 'moor', 'birch', 'forest') and m.t[y * w + x] == D.GRASS,
        'unwintering': lambda x, y: biome(m, x, y) in COLD,
        'flame': lambda x, y: biome(m, x, y) in ('badlands', 'mountain', 'ashland', 'hills', 'mesa', 'canyon', 'stone_ground')
                              and near(x, y, {'mountain', 'peak', 'volcano', 'ashland'}, 2),
        'bell': lambda x, y: near(x, y, {'lake'}, 2),
        'starwell': lambda x, y: biome(m, x, y) in ('forest', 'meadow', 'birch', 'grass', 'shrubland', 'hills'),
        'stones': lambda x, y: biome(m, x, y) in ('moor', 'hills', 'meadow', 'steppe', 'tundra'),
        'wisps': lambda x, y: biome(m, x, y) in ('swamp', 'marsh', 'floodplain', 'mangrove') and near(x, y, {'swamp', 'marsh'}, 2, 6),
        'sands': lambda x, y: biome(m, x, y) in ('dune', 'dune_crest', 'desert') and near(x, y, {'dune', 'dune_crest'}, 2, 6),
        'bay': lambda x, y: coast(x, y) and getattr(world.region_at(x, y), 'climate', '') != 'cold',
        'cenote': lambda x, y: biome(m, x, y) == 'jungle' and near(x, y, {'jungle'}, 2, 14),
        'stonewood': lambda x, y: near(x, y, {'petrified'}, 2) or (biome(m, x, y) in ('badlands', 'dry_forest', 'savanna')
                                                                  and random.random() < .1),
    }
    for kind in WONDERS:
        if kind == 'starwater':
            continue
        if random.random() > (.35 if kind == 'isles' else .8):
            continue
        put(kind, preds[kind], 1)
    if random.random() < .7:                         # the Starwater and its twin, far apart
        a = put('starwater', lambda x, y: biome(m, x, y) in ('meadow', 'forest', 'grass', 'birch', 'moor', 'hills'), 1)
        if a:
            ax, ay = a[0]
            b = [i for i in pool if free(i % w, i // w) and cheb(i % w, i // w, ax, ay) >= 90
                 and biome(m, i % w, i // w) in ('meadow', 'forest', 'grass', 'birch', 'moor', 'hills', 'steppe', 'taiga')]
            first = next(q for q in world.sites if (q.x, q.y) == (ax, ay))
            if b:
                bx, by = b[0] % w, b[0] // w
                twin = add('starwater', bx, by, 'The Twin Starwater')
                first.twin, twin.twin = twin.id, first.id
            else:
                world.sites.remove(first)
                taken.remove((ax, ay))


def _river_len(m, riv, x, y):
    seen, todo = {(x, y)}, [(x, y)]
    while todo and len(seen) < 300:
        cx, cy = todo.pop()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                n = (cx + dx, cy + dy)
                if n not in seen and m.inb(*n) and riv[n[1] * m.w + n[0]]:
                    seen.add(n)
                    todo.append(n)
    return len(seen)


def is_nature(site):
    return site.kind in LOOK


# ------------------------------------------------------------------ the play maps
def _base(game, site, w, h, ground, key=None, name=None):
    from .entities import GameMap
    m = GameMap(key or site.map_key, 'town', name or site.name, w, h, ground)
    m.glows, m.lights = [], []
    m.radius, m.sid, m.hid, m.signs = 60, None, None, []
    m.site = site.id
    m.nature = site.kind
    m.level = game.world.danger_at(site.x, site.y) + 1
    return m


def _done(m, entry):
    m.entry = entry
    for i in range(len(m.seen)):
        m.seen[i] = 1
    m.lights = list(m.glows)
    return m


def oval(m, cx, cy, rx, ry, tile, only=None, edge=None):
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            if not m.inb(x, y):
                continue
            d = ((x - cx) / max(.5, rx)) ** 2 + ((y - cy) / max(.5, ry)) ** 2
            if d <= 1 and (only is None or m.tile(x, y) in only):
                m.set(x, y, tile)
            elif edge and d <= edge[0] and (only is None or m.tile(x, y) in only):
                m.set(x, y, edge[1])


def scatter(m, tile, p, on=(D.GRASS,)):
    for i, t in enumerate(m.t):
        if t in on and random.random() < p:
            m.t[i] = tile


def path(m, a, b, tile=D.PATH, over=(D.GRASS, D.TREE, D.SAND, D.SNOW, D.GRIT, D.BAREROCK, D.SWAMP, D.RUBBLE)):
    x, y = a
    for _ in range(400):
        if m.inb(x, y) and m.tile(x, y) in over:
            m.set(x, y, tile)
        if (x, y) == b:
            return
        dx, dy = (b[0] > x) - (b[0] < x), (b[1] > y) - (b[1] < y)
        if dx and dy:
            if random.random() < .5:
                dy = 0
            else:
                dx = 0
        x, y = x + dx, y + dy


def river_band(m, pts, half=1.6, deep=D.WATER, bank=D.SHALLOW, keep=()):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
        for j in range(n + 1):
            x, y = x0 + (x1 - x0) * j / n, y0 + (y1 - y0) * j / n
            for yy in range(int(y - half - 1), int(y + half + 2)):
                for xx in range(int(x - half - 1), int(x + half + 2)):
                    if not m.inb(xx, yy) or m.tile(xx, yy) in keep:
                        continue
                    d = math.hypot(xx - x, yy - y)
                    if d <= half - .6:
                        m.set(xx, yy, deep)
                    elif d <= half + .3 and m.tile(xx, yy) != deep:
                        m.set(xx, yy, bank)


def site_map(game, site):
    """The play map of a nature site, from the world seed and where it lies."""
    state = random.getstate()
    random.seed(game.seed * 7919 + site.x * 1009 + site.y * 31 + 5)
    try:
        return BUILD[site.kind](game, site)
    finally:
        random.setstate(state)


def _falls(game, site, frozen=False):
    w, h = 80, 46
    m = _base(game, site, w, h, D.GRASS)
    cx = 40
    top = {x: 15 + int(2 * math.sin(x * .21) + 1.5 * math.sin(x * .07 + 1)) for x in range(w)}
    t0 = top[cx]
    for y in range(h):
        for x in range(w):
            if y < top[x] - 8:
                m.set(x, y, D.TREE if random.random() < .35 else D.CLIFF if random.random() < .3 else D.GRASS)
            elif y <= top[x]:
                m.set(x, y, D.CLIFF)
            elif random.random() < .12 and abs(x - cx) > 8:
                m.set(x, y, D.TREE)
    for y in range(0, t0 - 7):                       # the river above, running to the lip
        for x in range(cx - 2 + int(math.sin(y * .5)), cx + 3 + int(math.sin(y * .5))):
            m.set(x, y, D.WATER)
    fall = D.ICEFALL if frozen else D.FALLS
    for y in range(t0 - 7, t0 + 1):                  # the falling water down the cliff face
        for x in range(cx - 2, cx + 3):
            m.set(x, y, fall)
    py = t0 + 5
    for y in range(t0 + 1, py + 6):                 # the plunge pool, foaming under the falls
        for x in range(cx - 12, cx + 13):
            d = ((x - cx) / 10) ** 2 + ((y - py) / 4.5) ** 2
            if d < .25 and y < py:
                m.set(x, y, D.FOAM)
            elif d < 1:
                m.set(x, y, D.WATER)
            elif d < 1.45:
                m.set(x, y, D.SHALLOW)
            elif d < 2.6 and m.tile(x, y) in (D.GRASS, D.TREE) and random.random() < .45:
                m.set(x, y, D.SPRAY)
    river_band(m, [(cx + 4 * math.sin(y * .18), y) for y in range(py + 3, h + 2, 3)], 2.2)
    if frozen:                                      # a ledge high on the cliff, beside the falls, with what was left there
        lx, ly = cx + 5, t0 - 5
        for x in range(lx, lx + 4):
            m.set(x, ly, D.FLOOR)
        m.set(lx + 3, ly, D.CHEST)
        m.ledge, m.ledge_back = (lx, ly), (cx + 3, t0 + 2)
        if m.tile(cx + 3, t0 + 2) in (D.WATER, D.FOAM):
            m.ledge_back = (cx + 12, t0 + 3)
    else:                                           # the hollow behind the falls
        for y in range(t0 - 6, t0):
            for x in range(cx - 8, cx + 3):
                if abs(x - (cx - 3)) / 2.4 + abs(y - (t0 - 3)) < 3.8 and m.tile(x, y) == D.CLIFF:
                    m.set(x, y, D.FLOOR)
        m.set(cx - 6, t0 - 3, D.CHEST)
        for y in range(t0 - 2, t0 + 1):             # a way in along the foot of the falls
            m.set(cx - 3, y, D.FLOOR if m.tile(cx - 3, y) == D.CLIFF else m.tile(cx - 3, y))
        if m.tile(cx - 3, t0 + 1) in (D.WATER, D.FOAM, D.SHALLOW):
            m.set(cx - 3, t0 + 1, D.SHALLOW)
    ey = h - 6
    path(m, (0, ey), (cx - 12, py + 3))
    m.flow = (0, 1)
    return _done(m, (0, ey))


def _cascade(game, site):
    w, h = 64, 50
    m = _base(game, site, w, h, D.GRASS)
    scatter(m, D.TREE, .14)
    cx = 30
    steps = list(range(8, h - 6, 8))
    xs = {}
    for y in range(h):
        xs[y] = cx + int(3 * math.sin(y * .23))
    for sy in steps:                                 # the ledges across the hillside
        for x in range(w):
            if abs(x - xs[sy]) > 2:
                m.set(x, sy, D.LEDGE if random.random() < .9 else D.CLIFF)
    for y in range(h):
        x0 = xs[y]
        on_step = any(y in (s, s + 1) for s in steps)
        for x in range(x0 - 1, x0 + 2):
            m.set(x, y, D.FALLS if on_step else D.WATER)
    for sy in steps:                                 # a pool under every step
        oval(m, xs[sy] , sy + 4, 5, 2.2, D.WATER, edge=(1.5, D.SHALLOW))
        m.set(xs[sy], sy + 2, D.FOAM)
        m.set(xs[sy] + 1, sy + 2, D.FOAM)
    px = cx + 10                                     # the path up beside the falls, through every ledge
    for y in range(h - 1, 1, -1):
        if m.tile(px, y) in (D.LEDGE, D.CLIFF):
            m.set(px, y, D.PATH)
        elif m.tile(px, y) in (D.GRASS, D.TREE):
            m.set(px, y, D.PATH)
    m.set(px + 1, 2, D.CAIRN)
    m.lookout = 10
    path(m, (0, h - 3), (px, h - 3))
    m.flow = (0, 1)
    return _done(m, (0, h - 3))


def _greatfalls(game, site):
    w, h = 90, 50
    m = _base(game, site, w, h, D.GRASS)
    scatter(m, D.TREE, .1)
    cx, cy, r = 45, 6, 18
    for y in range(h):
        for x in range(w):
            d = math.hypot((x - cx) * .8, (y - cy) * 1.3)
            if y <= cy + 2 and d < r + 4:
                m.set(x, y, D.WATER)                 # the river above the rim
            elif d < r - 2.5:
                m.set(x, y, D.FOAM if d < r - 6 else D.WATER)
            elif d < r:
                m.set(x, y, D.FALLS)
            elif d < r + 3:
                m.set(x, y, D.CLIFF)
            elif d < r + 9 and random.random() < .5 and m.tile(x, y) in (D.GRASS, D.TREE):
                m.set(x, y, D.SPRAY)
    river_band(m, [(cx + 5 * math.sin(y * .15), y) for y in range(cy + 12, h + 3, 3)], 3.4)
    rx, ry = cx + 26, cy + 4                         # the rim path to the lookout
    for x in range(rx - 3, rx + 4):
        if m.tile(x, ry) in (D.CLIFF, D.GRASS, D.SPRAY, D.TREE):
            m.set(x, ry, D.PATH)
    m.set(rx - 3, ry, D.CAIRN)
    path(m, (w - 1, h - 10), (rx + 3, ry))
    path(m, (0, h - 8), (w - 1, h - 10))
    for y in range(h):
        for x in range(w):
            if m.tile(x, y) == D.PATH and any(m.inb(x + dx, y + dy) and m.tile(x + dx, y + dy) in (D.WATER, D.FOAM)
                                              for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                m.set(x, y, D.BRIDGE)                # a footbridge where the path meets the river
    m.lookout = 16
    m.flow = (0, 1)
    return _done(m, (0, h - 8))


def _rapids(game, site):
    w, h = 70, 40
    m = _base(game, site, w, h, D.GRASS)
    scatter(m, D.TREE, .12)
    cx = 34
    for x in range(w):
        y0 = 14 + int(2 * math.sin(x * .13))
        for y in range(y0, y0 + 11):
            edge = y in (y0, y0 + 10)
            m.set(x, y, D.SHALLOW if edge else D.BOULDER if random.random() < .1 else D.RAPIDS)
    for y in range(h):
        if m.tile(cx, y) in (D.RAPIDS, D.BOULDER):
            m.set(cx, y, D.STEPSTONE)
    ny = 14 + int(2 * math.sin(cx * .13)) - 3
    m.set(cx + 6, ny - 2, D.CHEST)
    for x in range(cx, cx + 6):
        if m.tile(x, ny) in (D.GRASS, D.TREE):
            m.set(x, ny, D.PATH)
    path(m, (0, h - 6), (cx, h - 6))
    path(m, (cx, h - 6), (cx, 14 + int(2 * math.sin(cx * .13)) + 11))
    m.flow = (1, 0)
    return _done(m, (0, h - 6))


def _hotspring(game, site):
    w, h = 60, 34
    m = _base(game, site, w, h, D.BAREROCK)
    scatter(m, D.GRASS, .3, (D.BAREROCK,))
    scatter(m, D.RUBBLE, .03, (D.BAREROCK,))
    pools = [(30, 15, 5, 2.6), (19, 20, 3, 1.6), (41, 22, 3.5, 1.8), (23, 10, 2.5, 1.4)]
    for x, y, rx, ry in pools:
        oval(m, x, y, rx, ry, D.HOTPOOL, edge=(1.6, D.SPRAY))
    path(m, (0, h // 2), (24, 16))
    return _done(m, (0, h // 2))


def _causeway(game, site):
    w, h = 70, 40
    m = _base(game, site, w, h, D.WATER)
    for y in range(h):
        shore = 16 + int(3 * math.sin(y * .2))
        for x in range(shore):
            m.set(x, y, D.SAND if x > shore - 5 else D.GRASS)
    oval(m, 54, 20, 9, 7, D.GRASS, edge=(1.4, D.SAND))
    scatter(m, D.TREE, .1, (D.GRASS,))
    shore = 16 + int(3 * math.sin(20 * .2))
    for x in range(shore - 1, 46):
        if m.tile(x, 20) == D.WATER:
            m.set(x, 20, D.CAUSEWAY)
    from .towns import Plot, build, place_door
    ch = Plot(53, 16, 8, 6, 'chapel')                # the old chapel on the islet, roofless
    build(m, ch)
    place_door(m, ch, 46, 20)
    for x, y in ch.inside:
        if random.random() < .15:
            m.set(x, y, D.RUBBLE)
    m.set(59, 18, D.ALTAR)
    m.set(54, 17, D.CHEST)
    path(m, (0, 20), (shore - 2, 20))
    return _done(m, (0, 20))


def _isles(game, site):
    w, h = 90, 56
    b = biome(game.maps['over'], site.x, site.y)
    ground = D.SAND if b in ('desert', 'savanna', 'steppe', 'badlands') else D.GRASS
    m = _base(game, site, w, h, ground)
    scatter(m, D.TREE, .05 if ground == D.SAND else .14, (ground,))
    m.isle_look = 'sand' if ground == D.SAND else 'green'
    isles = []
    for _ in range(200):
        if len(isles) >= random.randint(3, 5):
            break
        rx, ry = random.randint(6, 11), random.randint(3, 5)
        x, y = random.randint(rx + 4, w - rx - 4), random.randint(ry + 4, h - ry - 14)
        if any(abs(x - a) < rx + ar + 4 and abs(y - b_) < ry + br + 3 for a, b_, ar, br, _f in isles):
            continue
        isles.append((x, y, rx, ry, False))
    if not isles:
        isles = [(45, 18, 9, 4, False)]
    # some isles shed water: it falls, makes a pool, a brook, a small lake, then a river off the map
    k = random.randrange(len(isles))
    x, y, rx, ry, _f = isles[k]
    isles[k] = (x, y, rx, ry, True)
    fy = int(y + ry) + 1
    m.set(x, fy, D.FALLS)
    m.set(x, fy + 1, D.FALLS)
    oval(m, x, fy + 4, 3, 1.6, D.WATER, edge=(1.6, D.SHALLOW))
    lx, ly = min(w - 10, x + 14), min(h - 8, fy + 12)
    river_band(m, [(x, fy + 5), ((x + lx) / 2, (fy + ly) / 2 + 2), (lx, ly)], 1.2)
    oval(m, lx, ly, 5, 2.5, D.WATER, edge=(1.5, D.SHALLOW))
    river_band(m, [(lx, ly), (lx + 3, h - 2), (lx + 2, h + 3)], 1.6)
    m.isles = isles
    c = next((j for j in range(len(isles)) if j != k), k)        # the chain hangs from another isle if it can
    x, y, rx, ry, _f = isles[c]
    cy = int(y + ry) + 1
    m.set(x - 2, cy, D.CHAIN)
    m.chain = (x - 2, cy)
    m.chain_isle = c
    path(m, (0, h - 6), (x - 2, cy + 1))
    m.flow = (0, 1)
    return _done(m, (0, h - 6))


def isle_top(game, site, ground_map):
    """The top of the isle the chain hangs from: grass or sand on rock, and the empty air all round."""
    x, y, rx, ry, _f = ground_map.isles[ground_map.chain_isle]
    w, h = int(rx * 2 + 12), int(ry * 2 + 10)
    m = _base(game, site, w, h, D.AIR, key=site.map_key + ':top', name=f'On top of {site.name}')
    cx, cy = w // 2, h // 2
    ground = D.SAND if getattr(ground_map, 'isle_look', '') == 'sand' else D.GRASS
    oval(m, cx, cy, rx, ry + 1, ground)
    scatter(m, D.TREE, .12, (ground,))
    m.set(cx - 2, int(cy + ry), D.CHAIN)
    m.chain = (cx - 2, int(cy + ry))
    m.set(cx + 2, cy - 1, D.CHEST)
    m.top_of = True
    return _done(m, (cx - 2, int(cy + ry) - 1))


def _starwater(game, site):
    w, h = 60, 36
    m = _base(game, site, w, h, D.GRASS)
    scatter(m, D.TREE, .12)
    oval(m, 32, 18, 12, 7, D.WATER, edge=(1.3, D.SHALLOW))
    for x in range(20, 26):
        m.set(x, 18, D.PLANK)                        # a jetty, and the stair going down under the water at its end
    m.set(26, 18, D.STARSTAIR)
    m.stair = (25, 18)
    m.stars = True
    path(m, (0, 18), (19, 18))
    return _done(m, (0, 18))


def _anvil(game, site):
    w, h = 50, 34
    m = _base(game, site, w, h, D.GRASS)
    oval(m, 25, 16, 11, 7, D.SLOPE)
    oval(m, 25, 16, 3, 2, D.GRIT)
    m.set(25, 16, D.SPIKE)
    path(m, (0, 26), (22, 18), over=(D.GRASS, D.SLOPE, D.GRIT))
    return _done(m, (0, 26))


def _mound(game, site):
    w, h = 54, 34
    m = _base(game, site, w, h, D.GRASS)
    scatter(m, D.TREE, .06)
    oval(m, 27, 15, 10, 6, D.SLOPE)
    m.set(27, 21, D.MOUNDDOOR)
    m.door = (27, 21)
    path(m, (0, 26), (27, 22))
    return _done(m, (0, 26))


def _unwintering(game, site):
    w, h = 60, 36
    m = _base(game, site, w, h, D.SNOW)
    scatter(m, D.TREE, .1, (D.SNOW,))
    oval(m, 32, 17, 9, 6, D.GRASS)
    for _ in range(6):
        x, y = random.randint(26, 38), random.randint(13, 21)
        if m.tile(x, y) == D.GRASS:
            m.set(x, y, D.EVERBLOOM)
    m.spring = (32, 17, 9, 6)
    path(m, (0, 18), (24, 18), over=(D.SNOW, D.TREE))
    return _done(m, (0, 18))


def _flame(game, site):
    w, h = 50, 32
    m = _base(game, site, w, h, D.BAREROCK)
    scatter(m, D.RUBBLE, .05, (D.BAREROCK,))
    oval(m, 25, 15, 3, 2, D.GRIT)
    m.set(25, 15, D.FLAME)
    m.glows.append((25, 15, (255, 150, 50), 7))
    path(m, (0, 16), (23, 15))
    return _done(m, (0, 16))


def _bell(game, site):
    w, h = 64, 40
    m = _base(game, site, w, h, D.GRASS)
    scatter(m, D.TREE, .16)
    oval(m, 32, 16, 14, 8, D.WATER, edge=(1.3, D.SHALLOW))
    for y in range(17, 26):
        if m.tile(32, y) in (D.WATER, D.SHALLOW, D.GRASS, D.TREE):
            m.set(32, y, D.PLANK)
    m.set(32, 16, D.DARKWATER)
    m.bell = (32, 16)
    path(m, (0, 30), (32, 26))
    m.flow = None
    return _done(m, (0, 30))


def _starwell(game, site):
    w, h = 46, 30
    m = _base(game, site, w, h, D.GRASS)
    scatter(m, D.TREE, .25)
    oval(m, 23, 14, 5, 3, D.GRASS)
    m.set(23, 14, D.STARWELL)
    path(m, (0, 20), (22, 15))
    return _done(m, (0, 20))


def _stones(game, site):
    w, h = 56, 36
    m = _base(game, site, w, h, D.GRASS)
    scatter(m, D.TREE, .03)
    cx, cy, r = 28, 17, 6
    for k in range(9):
        a = k / 9 * math.tau
        m.set(round(cx + math.cos(a) * r * 1.4), round(cy + math.sin(a) * r * .8), D.SINGSTONE)
    m.ring = (cx, cy, r)
    path(m, (0, 26), (cx, cy + 6))
    return _done(m, (0, 26))


def _wisps(game, site):
    w, h = 70, 44
    m = _base(game, site, w, h, D.SWAMP)
    for _ in range(30):
        oval(m, random.randint(4, w - 4), random.randint(4, h - 4), random.uniform(1.5, 4), random.uniform(1, 2.5),
             D.SHALLOW if random.random() < .6 else D.WATER, only=(D.SWAMP,))
    scatter(m, D.TREE, .07, (D.SWAMP,))
    pts, x, y = [], 6, h // 2
    while len(pts) < 5:
        x, y = min(w - 5, x + random.randint(9, 14)), max(4, min(h - 5, y + random.randint(-8, 8)))
        m.set(x, y, D.SWAMP)
        pts.append((x, y))
    m.wisp = pts
    return _done(m, (0, h // 2))


def _sands(game, site):
    w, h = 70, 40
    m = _base(game, site, w, h, D.SAND)
    m.dig = (random.randint(36, 62), random.randint(6, h - 6))
    return _done(m, (0, h // 2))


def _bay(game, site):
    w, h = 70, 40
    m = _base(game, site, w, h, D.WATER)
    for y in range(h):
        shore = 24 + int(6 * math.sin(y * .12)) + int(2 * math.sin(y * .5))
        for x in range(shore):
            m.set(x, y, D.SAND if x > shore - 6 else D.GRASS)
    scatter(m, D.TREE, .08, (D.GRASS,))
    from .towns import Plot, build, place_door, furnish
    hut = Plot(8, 6, 6, 5, 'home')
    build(m, hut)
    place_door(m, hut, 12, 20)
    furnish(m, hut)
    m.glowbay = True
    path(m, (0, 20), (20, 20))
    return _done(m, (0, 20))


def _cenote(game, site):
    w, h = 60, 40
    m = _base(game, site, w, h, D.GRASS)
    scatter(m, D.TREE, .45)
    cx, cy = 34, 18
    for y in range(h):
        for x in range(w):
            d = math.hypot((x - cx) * .6, y - cy)
            if d < 4.2:
                m.set(x, y, D.GREENWATER)
            elif d < 5.4:
                m.set(x, y, D.FLOOR)
            elif d < 6.6:
                m.set(x, y, D.CLIFF)
            elif d < 8 and m.tile(x, y) == D.TREE:
                m.set(x, y, D.GRASS)
    m.set(cx, cy - 7, D.ROPEDOWN)
    m.set(cx, cy - 5, D.ROPEDOWN)
    m.rope_top, m.rope_bottom = (cx, cy - 8), (cx + 1, cy - 5)
    m.dives = 3
    path(m, (0, 30), (cx, cy - 8))
    return _done(m, (0, 30))


def _stonewood(game, site):
    w, h = 64, 40
    m = _base(game, site, w, h, D.GRIT)
    scatter(m, D.STONETREE, .28, (D.GRIT,))
    n = 0
    while n < 11:
        x, y = random.randint(8, w - 3), random.randint(2, h - 3)
        if m.tile(x, y) == D.GRIT:
            m.set(x, y, D.AMBER)
            n += 1
    path(m, (0, 20), (w - 1, 22), over=(D.GRIT, D.STONETREE))
    return _done(m, (0, 20))


BUILD = {'falls': _falls, 'frozenfalls': lambda g, s: _falls(g, s, True), 'cascade': _cascade, 'greatfalls': _greatfalls,
         'rapids': _rapids, 'hotspring': _hotspring, 'causeway': _causeway, 'isles': _isles, 'starwater': _starwater,
         'anvil': _anvil, 'mound': _mound, 'unwintering': _unwintering, 'flame': _flame, 'bell': _bell,
         'starwell': _starwell, 'stones': _stones, 'wisps': _wisps, 'sands': _sands, 'bay': _bay, 'cenote': _cenote,
         'stonewood': _stonewood}


# ------------------------------------------------------------------ what you do there
BUMP = {D.FOAM, D.RAPIDS, D.BOULDER, D.ICEFALL, D.CHAIN, D.AIR, D.STARSTAIR, D.SPIKE, D.MOUNDDOOR, D.FLAME, D.DARKWATER,
        D.STARWELL, D.SINGSTONE, D.EVERBLOOM, D.STONETREE, D.AMBER, D.TROLLSTONE, D.CAIRN, D.ROPEDOWN, D.GREENWATER}


def site_of(game, m=None):
    m = m or game.map
    sid = getattr(m, 'site', None)
    return game.world.sites[sid] if sid is not None else None


def on_enter(game, site, m):
    k = site.kind
    line = {'falls': 'The roar of the falls fills your head; a cold mist drifts over the pool.',
            'greatfalls': 'The ground trembles with the falling water. Spray hangs over everything like smoke.',
            'cascade': 'Water chatters down the hillside from pool to pool.',
            'rapids': 'White water roars over the rocks.',
            'hotspring': 'Steam rises from pools of hot water. The air smells of eggs and stone.',
            'causeway': ('The tide is out: a path of poles runs over the wet sand to the islet.' if low_tide(game)
                         else 'The tide is in. Poles stick out of the water where the path to the islet runs.'),
            'frozenfalls': ('The falls hang frozen, a stair of blue ice up the cliff.' if winter(game)
                            else 'The falls thunder down the cliff. High up beside them is a ledge.'),
            'isles': 'Rocks hang in the air over the vale, and their shadows drift over the grass.',
            'starwater': 'The lake is dark, and stars shine in it though the sun is up.',
            'anvil': 'An iron spike stands on the hilltop, black and pitted, the grass round it burnt.',
            'mound': ('Music comes from the hill, and a door stands open in its side.' if full_moon(game) and night(game)
                      else 'A green hill, round as a loaf. The grass on it is very soft.'),
            'unwintering': 'In the middle of the snow, the grass is green and flowers are out.',
            'flame': 'Fire burns out of the bare rock with a low roar, and nothing feeds it.',
            'bell': ('Under the storm a bell is ringing, somewhere beneath the lake.' if storm_at(game, site)
                     else 'The lake lies still and black.'),
            'starwell': 'An old well in a clearing. When you look down, there are stars in it.',
            'stones': 'A ring of grey stones on the hill. You think you hear a hum.',
            'wisps': 'A wide marsh, reeds and black water.' + (' Blue lights drift between the reeds.' if night(game) else ''),
            'sands': 'The dunes sigh and hum under your feet.',
            'bay': 'A quiet bay with a fisher\'s hut.' + (' The waves break in blue light.' if night(game) and summer(game) else ''),
            'cenote': 'In a clearing the ground falls away into a round hole. Far below lies clear green water.',
            'stonewood': 'Trees of grey stone stand all round you, every ring of their bark still there.'}.get(k)
    if line:
        game.msg(line, 'info')
    if k == 'causeway':
        game.flags['tide_said'] = low_tide(game)


def blocked(game, x, y):
    """Some ground can only be walked at some times: the causeway at low tide."""
    m = game.map
    if m.tile(x, y) == D.CAUSEWAY and not low_tide(game):
        if game.map.tile(game.player.x, game.player.y) == D.CAUSEWAY:
            p = game.player
            p.life -= 2
            game.msg('The sea is coming in! You wade on, waist-deep.', 'bad')
            return None
        return 'The tide is in. The sea covers the causeway.'
    return None


def on_step(game):
    m, p = game.map, game.player
    k = getattr(m, 'nature', None)
    if not k:
        return
    t = m.tile(p.x, p.y)
    if t == D.HOTPOOL:
        bathe(game)
    elif t == D.STEPSTONE:
        slip(game)
    elif t == D.FALLS and not getattr(m, 'soaked', False):
        m.soaked = True
        game.msg('You step through the falling water. It hammers your shoulders, and you are soaked.', 'info')
    elif t == D.CAUSEWAY and not low_tide(game):
        p.life -= 1
    if k == 'wisps':
        follow_wisp(game)
    elif k == 'sands':
        hum(game)


def bathe(game):
    p = game.player
    last = getattr(p, 'bathed_day', -1)
    if last == game.day:
        return
    p.bathed_day = game.day
    s = game.stats()
    p.life = min(s['max_life'], p.life + s['max_life'] // 2)
    p.poison = None
    p.buffs = [b for b in p.buffs if b[0] != 'warm'] + [['warm', 1, D.DAY_LEN // 2, 'Warmed by the spring']]
    game.msg('You sink into the hot water. Aches and cold drain out of you.' +
             (' Snow settles on your hair and melts.' if winter(game) else ''), 'good')


def slip(game):
    p = game.player
    s = game.stats()
    if random.random() >= max(.04, .16 - s['dex'] / 400):
        return
    m = game.map
    fx, fy = getattr(m, 'flow', None) or (1, 0)
    for k in range(6, 22):                          # swept downstream to the nearest bank
        x, y = p.x + fx * k, p.y
        for dy in range(0, 12):
            for yy in (y - dy, y + dy):
                if m.inb(x, yy) and m.tile(x, yy) in (D.GRASS, D.PATH, D.TREE, D.SHALLOW) and not m.mon_at(x, yy):
                    dmg = random.randint(2, 6)
                    p.life = max(1, p.life - dmg)
                    p.x, p.y = x, yy
                    game.msg(f'Your foot slips off the wet stone! The water takes you and throws you on the bank '
                             f'downstream (-{dmg}).', 'bad')
                    game.end_turn(5)
                    return
    return


def bump(game, x, y):
    """Walking into one of the wonders' tiles. Returns the turns it took."""
    m = game.map
    t = m.tile(x, y)
    site = site_of(game)
    say = game.msg
    if t == D.FOAM:
        say('The pool boils white under the falls. Nobody swims in that.')
    elif t == D.RAPIDS:
        say('White water races over the rocks. Only the stepping stones cross it.')
    elif t == D.BOULDER:
        say('A boulder, slick with spray.')
    elif t == D.ICEFALL:
        return climb_ice(game)
    elif t == D.CHAIN:
        return climb_chain(game, site)
    elif t == D.AIR:
        say('Nothing but air, and the vale far below.')
    elif t == D.STARSTAIR:
        return star_stair(game, site)
    elif t == D.SPIKE:
        return anvil(game, site)
    elif t == D.MOUNDDOOR:
        return hollow_hill(game, site)
    elif t == D.FLAME:
        return temper(game)
    elif t == D.DARKWATER:
        return drowned_bell(game, site)
    elif t == D.STARWELL:
        return star_well(game, site)
    elif t == D.SINGSTONE:
        say('The stone is cold. ' + ('It hums under your hand, low and deep.' if dusk(game) or night(game)
                                     else 'Lichen grows in the old carvings.'))
    elif t == D.EVERBLOOM:
        return pick(game, x, y, 'everbloom')
    elif t == D.STONETREE:
        say('A tree of stone, every ring of its bark still there. No axe would bite on it.')
    elif t == D.AMBER:
        return pick(game, x, y, 'amber')
    elif t == D.TROLLSTONE:
        say('A troll, caught by the sun and turned to grey stone, one arm still raised.')
    elif t == D.CAIRN:
        return lookout(game, site)
    elif t == D.ROPEDOWN:
        return rope(game)
    elif t == D.GREENWATER:
        return dive(game)
    return 0


def climb_ice(game):
    m, p = game.map, game.player
    if not winter(game):
        game.msg('The water thunders down too hard to climb. In the deep of winter, they say, it freezes.')
        return 0
    if cheb(p.x, p.y, *m.ledge) <= 2:
        p.x, p.y = m.ledge_back
        game.msg('You climb back down the frozen falls.', 'info')
    else:
        p.x, p.y = m.ledge
        game.msg('You climb the frozen falls, hacking holds in the blue ice. At last you pull yourself onto the ledge.',
                 'info')
    game.end_turn(20)
    return 0


def climb_chain(game, site):
    m, p = game.map, game.player
    if getattr(m, 'top_of', False):
        g = game.maps[site.map_key]
        game.cur = site.map_key
        p.x, p.y = g.chain[0] + 1, g.chain[1]
        game.msg('You climb down the chain to the vale.', 'info')
    else:
        key = site.map_key + ':top'
        if key not in game.maps:
            game.maps[key] = isle_top(game, site, m)
        top = game.maps[key]
        game.cur = key
        p.x, p.y = top.entry
        game.msg('You climb the chain, hand over hand, up into the air. At the top: grass, wind, and the vale far below.',
                 'info')
    game.end_turn(15)
    game.compute_fov()
    return 0


def star_stair(game, site):
    twin = getattr(site, 'twin', None)
    if twin is None:
        game.msg('The stair goes down into the dark water, and ends in nothing.')
        return 0
    other = game.world.sites[twin]
    p = game.player
    game.msg('You go down the stair under the water. The stars close over your head; it is like walking through the '
             'night sky. Then the steps lead up again.', 'unique')
    if other.map_key not in game.maps:
        game.maps[other.map_key] = site_map(game, other)
    game.cur = other.map_key
    om = game.maps['over']
    om.seen[other.y * om.w + other.x] = 1
    game.over_pos = (other.x, other.y)
    m = game.map
    p.x, p.y = m.stair
    game.mark_visit('site', other.id)
    game.msg(f'You come up out of {other.name}, far from where you went down.', 'info')
    game.end_turn(30)
    game.compute_fov()
    return 0


def anvil(game, site):
    from . import events as EV
    left = getattr(site, 'left', None)
    if left:
        if storm_at(game, site) and not getattr(left, 'blessed', False):
            bless(game, site)
        EV.ask(game, 'nature', 'The Thunder Anvil',
               'Your ' + left.display_name() + ' lies against the spike' +
               (', and the steel has a blue sheen now. It tingles in your hand.' if getattr(left, 'blessed', False)
                else ', wet and waiting for the storm.'),
               [('Take it back', 'anvil_take'), ('Leave it', 'bye')], site=site.id)
        return 0
    w = game.eq_item('weapon')
    if not w:
        game.msg('The spike is black and pitted. People say a weapon left here in a storm is blessed by the lightning.')
        return 0
    if getattr(w, 'blessed', False):
        game.msg('Your weapon has been blessed here already. The lightning does not strike twice in the same steel.')
        return 0
    EV.ask(game, 'nature', 'The Thunder Anvil', 'The spike is black and pitted, and the grass round it is burnt. People '
           'say a weapon left here in a storm is blessed by the lightning.' +
           (' The storm is overhead now.' if storm_at(game, site) else ''),
           [(f'Leave your {w.display_name()} at the spike', 'anvil_leave'), ('Not now', 'bye')], site=site.id)
    return 0


def bless(game, site):
    it = site.left
    it.blessed = True
    lvl = max(1, getattr(it, 'ilvl', 1))
    it.aff = list(it.aff) + [['light_dmg', 2 + lvl // 3]]
    if game.map.key == site.map_key:
        game.msg('Lightning strikes the spike with a crack that shakes the hill! Blue fire runs down it.', 'unique')


def hollow_hill(game, site):
    from . import events as EV
    if not (full_moon(game) and night(game)):
        game.msg('A round door of turf, shut so close you could pass it a hundred times. Only at full moon, they say.')
        return 0
    EV.ask(game, 'nature', 'The Hollow Hill', 'Inside the hill there are lights and music, and tall people in green who '
           'smile with too many teeth. They sell strange things, and take no coin. "A thing you carry, for a thing we '
           'have," says one. "Or a dance. Only one."',
           [('Trade a thing you carry', 'fey_trade'), ('Dance with them', 'fey_dance'), ('Back away', 'bye')], site=site.id)
    return 0


def temper(game):
    w = game.eq_item('weapon')
    if not w:
        game.msg('The flame roars out of the bare rock. A smith would give a year to work a blade in it.')
        return 0
    if getattr(w, 'tempered', False):
        game.msg('Your weapon has been worked in the Undying Flame already.')
        return 0
    w.tempered = True
    ed = next((a for a in w.aff if a[0] == 'ed'), None)
    if ed:
        ed[1] += 10
    else:
        w.aff = list(w.aff) + [['ed', 10]]
    if getattr(w, 'mdur', 0):
        w.mdur += 15
        w.dur = w.mdur
    game.msg(f'You hold your {w.display_name()} in the flame until it glows, and cool it in the snow-water of your '
             'flask. The edge comes out keen and grey: it will hold.', 'unique')
    game.end_turn(60)
    return 0


def drowned_bell(game, site):
    if getattr(site, 'bell_done', False):
        game.msg('The water is black and still. You have been down to the chapel; there is nothing more there.')
        return 0
    if not storm_at(game, site):
        game.msg('The water is black and still. Only in a storm, they say, does the bell ring, and the way down opens.')
        return 0
    site.bell_done = True
    from .worldgen import random_gear
    from .entities import Item
    from .money import purse
    m, p = game.map, game.player
    lvl = getattr(m, 'level', 3)
    game.msg('The bell rings under you, slow and heavy. You take a breath and dive. Down and down, to a chapel of green '
             'stone where the bell swings in its tower; on the drowned altar lie the offerings of a village long gone.',
             'unique')
    game.spill(m, p.x, p.y, random_gear(game, lvl + 3, 2.0))
    game.spill(m, p.x, p.y, Item(game.new_id(), 'gold', 'gold', purse(lvl, 8)))
    game.spill(m, p.x, p.y, curio(game, 'offering'))
    if random.random() < .5:
        from .entities import make_monster
        for _ in range(2):
            spot = next(((p.x + dx, p.y + dy) for dx, dy in ((2, 0), (-2, 0), (0, 2), (1, 2), (-1, 2))
                         if m.inb(p.x + dx, p.y + dy) and D.TILES[m.tile(p.x + dx, p.y + dy)].walk
                         and not m.mon_at(p.x + dx, p.y + dy)), None)
            if spot:
                mon = make_monster(game, 'drowned', spot[0], spot[1], lvl + 1)
                mon.awake = True
                m.mons.append(mon)
        game.msg('Something followed you up out of the water.', 'bad')
    game.end_turn(20)
    return 1


WISHES = [('wealth', 'For wealth'), ('health', 'For health'), ('knowing', 'To know a hidden thing'), ('luck', 'For luck')]


def star_well(game, site):
    from . import events as EV
    from .money import fmt
    if getattr(site, 'wish_day', -1) == game.day:
        game.msg('The stars in the well have gone pale. One wish a day, the old tale says.')
        return 0
    p = game.player
    opts = [(f'{label} ({fmt(100)})', k if p.gold >= 100 else None) for k, label in WISHES] + [('Walk away', 'bye')]
    EV.ask(game, 'nature', 'The Star Well', 'Stars shine in the water at the bottom of the well, though it is ' +
           ('night above as well.' if night(game) else 'broad day above.') + ' Throw in a silver coin and wish.',
           opts, site=site.id)
    return 0


def wish(game, site, k):
    from .entities import Item
    from .money import purse
    p = game.player
    p.gold -= 100
    site.wish_day = game.day
    twist = random.random() < .3
    lvl = game.world.danger_at(site.x, site.y) + 1
    if k == 'wealth':
        if twist:
            p.food = max(0, p.food - 250)
            game.msg('Coins rattle up out of the well into your hands, warm as bread. Your pack feels lighter: your food '
                     'is gone.', 'info')
        game.spill(game.map, p.x, p.y, Item(game.new_id(), 'gold', 'gold', purse(lvl, 5)))
        if not twist:
            game.msg('Something glints at your feet that was not there before.', 'good')
    elif k == 'health':
        s = game.stats()
        p.life = s['max_life']
        p.poison = None
        if twist:
            p.food = max(0, p.food - 300)
            game.msg('Warmth runs through you and every hurt closes. And you are hungry, so hungry.', 'info')
        else:
            p.buffs = [b for b in p.buffs if b[0] != 'regen'] + [['regen', 2, D.DAY_LEN, 'The well\'s blessing']]
            game.msg('Warmth runs through you, and every hurt closes.', 'good')
    elif k == 'knowing':
        if twist:
            game.msg('You see, for a moment, a dark place and a thing that waits in it, and it sees you too. You know '
                     'nothing more than before, and wish you knew less.', 'bad')
        elif not dream(game, 'The water shows you a place, clear as a picture:'):
            game.msg('The water shows you only your own face.', 'info')
    else:
        if twist:
            p.buffs = [b for b in p.buffs if b[0] != 'frail'] + [['frail', 10, D.DAY_LEN, 'Luck run backwards']]
            game.msg('A star goes out in the well. Your luck has run the wrong way.', 'bad')
        else:
            p.buffs = [b for b in p.buffs if b[0] != 'dmg'] + [['dmg', 10, D.DAY_LEN, 'Starlit luck']]
            game.msg('A star flares in the well. You feel lucky.', 'good')


def dream(game, lead):
    """A hidden place shown to you: a glade, a gnome hamlet, a hidden valley or cove, or a dungeon you never found."""
    from . import chronicle as CH
    from .engine import dir_name
    w, p = game.world, game.player
    om = game.maps['over']
    x0, y0 = (p.x, p.y) if game.cur == 'over' else game.over_pos
    hidden = [q for q in w.sites if getattr(q, 'hidden', False) and not getattr(q, 'found', True)]
    hidden += [d for d in w.dungeons.values() if not om.seen[d.y * om.w + d.x]]
    if not hidden:
        return False
    q = min(hidden, key=lambda q: (cheb(q.x, q.y, x0, y0) + random.randint(0, 40), q.name))
    om.seen[q.y * om.w + q.x] = 1
    if hasattr(q, 'found'):
        q.found = True
    game.msg(f'{lead} {q.name}, far to the {dir_name(q.x - x0, q.y - y0)}. It is marked on your map.', 'unique')
    CH.add(game, 'Places', f'{q.name} lies to the {dir_name(q.x - x0, q.y - y0)}, shown in a dream.', 'heard',
           'a dream', game.map.name, place=(q.x, q.y), title=q.name, key=f'dream:{q.name}')
    return True


def rest(game):
    """Sleeping in the middle of the Singing Stones at dusk or by night: a dream of a hidden place."""
    m, p = game.map, game.player
    ring = getattr(m, 'ring', None)
    if not ring or not (dusk(game) or night(game)) or game.hostile_visible():
        return False
    cx, cy, r = ring
    if ((p.x - cx) / (r * 1.4)) ** 2 + ((p.y - cy) / (r * .8)) ** 2 >= .8:
        return False
    site = site_of(game)
    game.msg('You lie down in the middle of the ring. The stones hum, and you sleep.', 'info')
    game.rest_here(quiet=True)
    game.end_turn(D.DAY_LEN // 4, True)
    if game.day - getattr(site, 'dream_day', -99) < 7 or not dream(game, 'You dream of'):
        game.msg('You sleep deep and wake with the hum still in your bones, but you remember no dream.', 'info')
    else:
        site.dream_day = game.day
    return True


def pick(game, x, y, what):
    m = game.map
    if what == 'everbloom':
        from .entities import Item
        it = Item(game.new_id(), 'plant', 'everbloom')
        if not game.add_to_inv(it):
            game.msg('Your pack is full.', 'bad')
            return 0
        game.player.known_plants.add('everbloom')
        m.set(x, y, D.GRASS)
        game.msg('You pick a sprig of Everbloom. It smells of spring in the middle of winter.', 'good')
        return 1
    it = curio(game, 'amber')
    if not game.add_to_inv(it):
        game.msg('Your pack is full.', 'bad')
        return 0
    m.set(x, y, D.GRIT)
    game.msg('You dig a lump of amber out of the grit. Something small is caught inside it.', 'good')
    if random.random() < .15:
        f = curio(game, 'fossil')
        if game.add_to_inv(f):
            game.msg('Under it lies a stone shell, curled like a ram\'s horn: a fossil. Scholars pay for those.', 'good')
    return 1


CURIO = {'amber': ('A lump of amber', 6, (240, 168, 56), 'Old tree-gold with a tiny creature caught inside. Traders pay for it.'),
         'fossil': ('A fossil shell', 18, (196, 186, 160), 'A shell of stone, curled like a ram\'s horn. Scholars pay well.'),
         'offering': ('An old offering', 20, (120, 222, 170), 'Jade and gold, given to the water long ago. A trader pays well '
                                                              'and asks nothing.')}


def curio(game, t):
    from .entities import Item
    it = Item(game.new_id(), 'curio', t)
    it.name = CURIO[t][0]
    return it


def lookout(game, site):
    om = game.maps['over']
    r = getattr(game.map, 'lookout', 10)
    if getattr(site, 'looked', False):
        game.msg('The land lies spread out below you, as before.')
        return 0
    site.looked = True
    for y in range(site.y - r, site.y + r + 1):
        for x in range(site.x - r, site.x + r + 1):
            if om.inb(x, y) and (x - site.x) ** 2 + ((y - site.y) * 1.4) ** 2 <= r * r:
                om.seen[y * om.w + x] = 1
    game.msg('From the cairn on top you see the land for miles around: rivers, woods and roads. You fix it all in '
             'your mind (and on your map).', 'good')
    return 1


def rope(game):
    m, p = game.map, game.player
    if cheb(p.x, p.y, *m.rope_bottom) <= 1:
        p.x, p.y = m.rope_top
        game.msg('You climb the rope back up into the green heat.', 'info')
    else:
        p.x, p.y = m.rope_bottom
        game.msg('You climb down the rope, down the wet rock, to a ledge just above the green water.', 'info')
    game.end_turn(10)
    return 0


def dive(game):
    m, p = game.map, game.player
    if m.dives <= 0:
        game.msg('You dive again and again, but there is nothing more on the bottom but bones and old leaves.')
        game.end_turn(10)
        return 0
    m.dives -= 1
    r = random.random()
    game.msg('You dive into the clear green water, down to where the light fades.', 'info')
    if r < .7:
        game.spill(m, p.x, p.y, curio(game, 'offering'))
        game.msg('In the silt at the bottom lies an offering: jade and gold, given to the water long ago.', 'good')
    elif r < .9:
        from .worldgen import random_gear
        game.spill(m, p.x, p.y, random_gear(game, getattr(m, 'level', 2) + 2, 1.5))
        game.msg('Among the bones on the bottom lies something worth bringing up.', 'good')
    else:
        game.msg('Only bones down there, and the water is cold. You come up gasping.', 'info')
    game.end_turn(20)
    return 1


def follow_wisp(game):
    m, p = game.map, game.player
    if not night(game) or getattr(m, 'wisp_day', -1) == game.day:
        return
    k = getattr(m, 'wisp_k', 0)
    pts = m.wisp
    if k >= len(pts) or cheb(p.x, p.y, *pts[k]) > 1:
        return
    k += 1
    m.wisp_k = k
    if k < len(pts):
        game.msg('The blue light drifts away as you come near, deeper into the fen. It waits for you.', 'info')
        return
    m.wisp_k, m.wisp_day = 0, game.day
    if random.Random(game.day * 13 + game.seed).random() < .55:
        game.msg('The light sinks into the ground and goes out. Where it was, the moss covers an old chest.', 'good')
        spot = next(((p.x + dx, p.y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if m.inb(p.x + dx, p.y + dy)
                     and m.tile(p.x + dx, p.y + dy) in (D.SWAMP, D.GRASS, D.SHALLOW)), None)
        if spot:
            m.set(*spot, D.CHEST)
    else:
        s = game.stats()
        dmg = max(2, s['max_life'] // 8)
        p.life = max(1, p.life - dmg)
        game.msg(f'The light goes out, and the ground goes out with it. You sink to the chest in black mire and only drag '
                 f'yourself out after a long and dreadful struggle (-{dmg}).', 'bad')
        game.end_turn(30)


def hum(game):
    m, p = game.map, game.player
    if getattr(m, 'dug', False):
        return
    d = cheb(p.x, p.y, *m.dig)
    band = 0 if d == 0 else 1 if d <= 3 else 2 if d <= 8 else 3 if d <= 16 else 4
    if band == getattr(m, 'hum_band', None):
        return
    m.hum_band = band
    if band == 4:
        return
    if band:
        game.msg(['', 'The humming is loud now, right under your feet.', 'The sand hums under your feet.',
                  'A faint hum in the sand.'][band], 'info')
        return
    m.dug = True
    game.msg('The sand roars underfoot. You dig with your hands, and a hand deep the sand gives way: the top of a buried '
             'wall, and a chest in the sand beside it.', 'unique')
    x, y = m.dig
    for dx in (-2, -1, 0, 1, 2):
        if m.inb(x + dx, y - 1):
            m.set(x + dx, y - 1, D.WALL)
    if m.inb(x + 1, y):
        m.set(x + 1, y, D.CHEST)
    game.end_turn(30)


def fish_bonus(game):
    m = game.map
    k = getattr(m, 'nature', None)
    if k in ('falls', 'cascade', 'greatfalls', 'frozenfalls'):
        return .15
    if k == 'rapids':
        return .2
    if k == 'bay' and night(game) and summer(game):
        return .3
    return 0


def sunlit(game, m):
    """Is it day, and open sky over this map? (Trolls turn to stone in it.)"""
    return m.kind in ('wild', 'town', 'siege') and not getattr(m, 'underground', False) and not night(game)


def to_stone(game, mon):
    m = game.map
    m.mons.remove(mon)
    m.set(mon.x, mon.y, D.TROLLSTONE)
    if game.visible(mon.x, mon.y):
        game.msg(f'The sunlight falls on {mon.name.lower() if mon.name else "the troll"}. It stiffens, greys, and '
                 'turns to stone where it stands!', 'unique')


def daily(game):
    """Storms bless what lies at the Thunder Anvil; now and then a star falls on an ordinary night."""
    for site in game.world.sites:
        if site.kind == 'anvil' and getattr(site, 'left', None) and not getattr(site.left, 'blessed', False) \
                and storm_at(game, site):
            bless(game, site)
    from . import weather as WX
    from . import jobs as JB
    st = JB.star(game)
    if not WX.starfall(game.day) and (not st or st.get('taken') or game.day - st['day'] > 20) and random.random() < 1 / 45:
        JB.fall(game, rare=True)


def r_nature(game, choice, ctx):
    site = game.world.sites[ctx['site']]
    p = game.player
    if choice == 'anvil_leave':
        w = game.eq_item('weapon')
        if not w:
            return
        for k, v in list(p.eq.items()):
            if v == w.id:
                del p.eq[k]
        p.inv = [i for i in p.inv if i.id != w.id]
        site.left = w
        game.msg(f'You lean your {w.display_name()} against the spike and step back. Now for a storm.', 'info')
        if storm_at(game, site):
            bless(game, site)
    elif choice == 'anvil_take':
        it = site.left
        if not game.add_to_inv(it):
            game.msg('Your pack is full.', 'bad')
            return
        site.left = None
        game.msg(f'You take back your {it.display_name()}.' +
                 (' It hums faintly, and sparks crawl along the edge: thunder-blessed.' if getattr(it, 'blessed', False) else ''),
                 'good' if getattr(it, 'blessed', False) else 'info')
    elif choice == 'fey_trade':
        goods = [i for i in p.inv if i.id not in p.eq.values() and i.k in ('gear', 'curio', 'fish', 'plant', 'food', 'potion')]
        if not goods:
            game.msg('"You carry nothing we want," they laugh, and the music swallows you back out onto the grass.', 'info')
            return
        give = max(goods, key=lambda i: i.value())
        p.inv.remove(give)
        from .worldgen import random_gear
        from .entities import Item, make_tome
        lvl = game.world.danger_at(site.x, site.y) + 2
        r = random.random()
        got = random_gear(game, lvl + 2, 2.5) if r < .45 else make_tome(game, lvl) if r < .7 else \
            Item(game.new_id(), 'potion', 'rejuv', 3)
        if not game.add_to_inv(got):
            game.spill(game.map, p.x, p.y, got)
        game.msg(f'They take your {give.display_name()} with long cold fingers, and put {got.display_name()} in your hands. '
                 'When you look back, the door is only turf.', 'unique')
    elif choice == 'fey_dance':
        s = game.stats()
        p.life, p.mana, p.stamina = s['max_life'], s['max_mana'], s['max_stamina']
        p.buffs = [b for b in p.buffs if b[0] != 'regen'] + [['regen', 2, D.DAY_LEN, 'Danced with the fair folk']]
        game.end_turn(D.DAY_LEN, True)
        game.msg('You dance. It is only one dance, you are sure of it. When you come out, a whole day has gone by, and you '
                 'feel younger than you have in years.', 'unique')
    elif choice in dict(WISHES):
        wish(game, site, choice)


def register():
    from . import events as EV
    EV.RESOLVERS['nature'] = r_nature


register()


# ------------------------------------------------------------------ how it moves (worked out from the clock, never saved)
def _h(x, y, salt=0):
    return ((x * 73856093) ^ (y * 19349663) ^ (salt * 83492791)) & 0xffff


def _mix(a, b, k):
    k = max(0.0, min(1.0, k))
    return (int(a[0] + (b[0] - a[0]) * k), int(a[1] + (b[1] - a[1]) * k), int(a[2] + (b[2] - a[2]) * k))


FRAME = .19                                         # one step of falling water, foam and flow


def curtain(m, x, y, t):
    """Falling water: every column its own strand, with its own speed, thickness and gaps."""
    f = int(t / FRAME)
    top = getattr(m, '_tops', None)
    if top is None:
        top = m._tops = {}
        for i, tt in enumerate(m.t):
            if tt in (D.FALLS, D.ICEFALL):
                xx, yy = i % m.w, i // m.w
                top[xx] = min(top.get(xx, yy), yy)
    if y == top.get(x, y) and not (m.inb(x, y - 1) and m.tile(x, y - 1) in (D.FALLS, D.ICEFALL)):
        k = ((x * 5 + f) % 12) / 12
        return ('─' if k < .7 else '≈'), _mix((200, 230, 250), (255, 255, 255), k), (70, 116, 170)
    speed = 1 + _h(x, 0, 5) % 3
    run = 2 + _h(x, 1, 6) % 4
    seg = (y - speed * f + _h(x, 2, 7)) // run
    v = (_h(x, seg, 8) % 100) / 100 * .8 + .2
    if _h(x, 3, 9) % 5 == 0:
        v -= .2                                     # a thinner strand at the edge of the fall
    if _h(x, y, f) % 61 == 0:
        return '∙', (255, 255, 255), _mix((36, 64, 98), (96, 146, 198), v)
    ch, fg = ('║', (252, 254, 255)) if v > .8 else ('│', (222, 240, 252)) if v > .62 else (':', (186, 214, 238)) \
        if v > .45 else ('·', (150, 186, 216)) if v > .3 else (' ', (150, 186, 216))
    return ch, fg, _mix((30, 54, 82), (100, 150, 202), v * .85 + .05)


_W = [(((k * 37) % 19) / 10 - .9, ((k * 53) % 17) / 9 - .9, k * 1.7, (k % 3) + 1) for k in range(7)]


def churn(x, y, t, fast=1.0):
    """Foam that boils: waves crossing each other, so no two cells move alike."""
    a = t * fast * 1.6
    v = sum(math.sin(kx * x * 1.3 + ky * y * 1.9 + ph + kt * a) for kx, ky, ph, kt in _W) / 7
    v = max(0.0, min(1.0, (v * .5 + .5 - .2) * 1.6))
    ch, fg = ('░', (240, 248, 255)) if v > .82 else ('≈', (226, 242, 255)) if v > .66 else ('~', (196, 224, 246)) \
        if v > .5 else ('∙', (170, 206, 236)) if v > .34 else ('·', (130, 176, 214))
    return ch, fg, _mix((22, 52, 88), (96, 146, 196), v * .9)


def stream(m, x, y, look, t):
    """A glint now and then running downstream along each lane of the water."""
    ch, fg, bg = look
    dx, dy = m.flow
    lane, along = (x, y) if dy else (y, x)
    v = _h(lane, (along * (1 if dx + dy > 0 else -1) - int(t / FRAME)) // 3, 21) % 100
    if v > 88:
        return '~', (190, 228, 255), bg
    if v > 78:
        return '≈', (140, 196, 240), bg
    return ch, fg, bg


ANIM = {D.FALLS, D.ICEFALL, D.FOAM, D.SPRAY, D.RAPIDS, D.HOTPOOL, D.FLAME, D.SINGSTONE, D.STARWELL, D.DARKWATER,
        D.MOUNDDOOR, D.GREENWATER}


def cell(game, m, i, x, y, look, t, night_):
    """The look of a nature tile now, or None when it does not move."""
    ch, fg, bg = look
    tt = m.t[i]
    if tt == D.FALLS:
        return curtain(m, x, y, t)
    if tt == D.ICEFALL:
        if winter(game):
            return ('║' if _h(x, y, 2) % 3 else '│'), (226, 244, 255), (110, 150, 190)
        return curtain(m, x, y, t)
    if tt == D.FOAM:
        return churn(x, y, t)
    if tt == D.RAPIDS:
        c = churn(x * 2 + int(t * 4), y, t, 2.2)
        return c[0], c[1], _mix(c[2], (60, 100, 150), .3)
    if tt == D.SPRAY:
        k = .5 + .5 * math.sin(t * 1.3 + x * .7 - y * .4 + _h(x, y, 3) % 7)
        return ('░' if k > .8 else '°' if k > .4 else '·'), _mix(fg, (230, 240, 248), k * .6), _mix(bg, (90, 110, 124), k * .5)
    if tt == D.HOTPOOL:
        k = .5 + .5 * math.sin(t * .9 + x * 1.1 + y * 2.3)
        return ('°' if k > .85 else ch), _mix(fg, (255, 255, 255), k * .4), bg
    if tt == D.FLAME:
        from .anim import flame
        f = flame(t * 1.3, x, y)
        return ch, _mix((255, 120, 30), (255, 230, 140), f - .5), _mix(bg, (120, 40, 8), f - .6)
    if tt == D.SINGSTONE:
        if dusk(game) or night_:
            k = .5 + .5 * math.sin(t * 1.5 + x)
            return ch, _mix(fg, (200, 210, 255), k * .5), bg
        return None
    if tt in (D.STARWELL, D.DARKWATER, D.GREENWATER):
        k = _h(x, y, int(t * 2)) % 9
        return (('*' if k == 0 else '·' if k < 3 else ch), _mix(fg, (230, 236, 255), .5 if k < 3 else 0), bg) \
            if tt == D.STARWELL else (ch, _mix(fg, (190, 210, 240), .3 * (k == 0)), bg)
    if tt == D.MOUNDDOOR and full_moon(game) and night_:
        return ch, _mix(fg, (255, 230, 150), .5 + .5 * math.sin(t * 2)), (60, 50, 20)
    return None


def overlay(game, m, x, y, i, look, t, night_, vis):
    """What hangs over the ground, or shines in the water: isles, stars, glowing waves, wisps. (look, moving)"""
    ch, fg, bg = look
    moving = False
    isles = getattr(m, 'isles', None)
    if isles:
        p = game.player
        for k, (cx, cy, rx, ry, _f) in enumerate(isles):
            d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if d > 1:
                continue
            under = ((p.x - cx) / rx) ** 2 + ((p.y - cy) / ry) ** 2 <= 1 and game.cur == m.key
            if under:                               # the isle over you: only its shadow on the ground
                return (ch, _mix(fg, (0, 0, 0), .5), _mix(bg or (0, 0, 0), (0, 0, 0), .5)), False
            bottom = ((x - cx) / rx) ** 2 + ((y + 1 - cy) / ry) ** 2 > 1
            if bottom:
                return ('▀', (150, 140, 124), (62, 56, 50)), False
            sand = getattr(m, 'isle_look', '') == 'sand'
            top = (196, 170, 110) if sand else (96, 150, 64)
            g = '♣' if _h(x, y, 11) % 7 == 0 and not sand else '"' if _h(x, y, 12) % 3 == 0 else '.'
            return (g, _mix(top, (255, 255, 255), .1), _mix(top, (30, 30, 20), .7)), False
    tt = m.t[i]
    if getattr(m, 'stars', False) and tt in (D.WATER, D.SHALLOW) and vis:
        k = _h(x, y, 77) % 11
        tw = .5 + .5 * math.sin(t * 2 + _h(x, y, 5))
        if k == 0:
            return ('*' if tw > .7 else '·', _mix((200, 210, 255), (255, 255, 255), tw), (8, 12, 30)), True
        return (ch, fg, _mix(bg or (10, 20, 40), (6, 8, 24), .7)), True
    if getattr(m, 'glowbay', False) and tt in (D.WATER, D.SHALLOW) and night_ and summer(game) and vis:
        k = .5 + .5 * math.sin(t * 1.2 - x * .5 + _h(y, 0, 3) % 5)
        if k > .75:
            return ('~', _mix((90, 200, 255), (200, 250, 255), k), _mix(bg or (10, 20, 40), (20, 80, 110), k - .5)), True
    if getattr(m, 'wisp', None) and night_ and vis and getattr(m, 'wisp_day', -1) != game.day:
        k = getattr(m, 'wisp_k', 0)
        if k < len(m.wisp) and (x, y) == m.wisp[k]:
            g = .6 + .4 * math.sin(t * 3)
            return ('∙' if g < .9 else '•', _mix((120, 200, 255), (230, 250, 255), g), _mix(bg or (0, 0, 0), (20, 60, 90), g)), True
    if getattr(m, 'flow', None) and tt in (D.WATER, D.SHALLOW, D.RIVER) and vis:
        return stream(m, x, y, look, t), True
    return None, moving
