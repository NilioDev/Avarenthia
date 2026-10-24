"""Old places on the land (round 11): what the made history left lying about, so the world looks old and lived in.
Each is one cell of the world map with a small play map of its own, and what matters there is a tile you bump.
- an old battlefield, where a war of the history was decided: grassy mounds to dig, rusted spear points, a cairn
  for the fallen; on the day of the battle the dead walk the field at night;
- a deserted village, emptied by a plague, a war or a dragon (an event of its own in the history): roofless houses,
  a dry well, a field gone to weeds, a burnt chapel; bandits, a hermit or a ghost may live there now;
- a broken bridge of the old Empire: piers in the river, a ford beside it, and an old way running on from it;
- memorials: a stone with the names of the fallen, an old emperor's statue lying in the grass with its head beside
  it, a gallows hill at a crossroads where the Watch hangs its sentences;
- an old quarry: half-cut blocks, a giant statue never finished, sometimes flooded; a fossil now and then;
- a shipwreck on the shore, reached at low tide, searched once; often the wreckers came first;
- a hermitage: a hut on a rock or in a wood, and a hermit who knows the country;
- a leper colony outside a city, with a bell; the temple sends food there;
- and, as small signs on the world map, the marks of the peoples: dwarf boundary stones, elven moonstones along a
  path, orc skull poles, kobold scratches pointing at something shiny."""
import random

from . import data as D
from . import calendar as CAL
from .data import GRASS, PATH, TREE, WALL, FLOOR, DOOR, RUBBLE, WATER, SHALLOW, SAND, FIELD, WELL, ALTAR
from .worldgen import cheb

LOOK = {'oldfield': ('×', (176, 132, 104)), 'deserted': ('⌂', (146, 140, 130)), 'oldbridge': ('╧', (168, 160, 144)),
        'namestone': ('┴', (204, 198, 180)), 'fallenking': ('ß', (176, 172, 160)), 'gallows': ('Γ', (160, 118, 82)),
        'quarry': ('□', (186, 176, 156)), 'wreck': ('▬', (170, 128, 88)), 'hermitage': ('╓', (196, 180, 140)),
        'colony': ('±', (190, 196, 156))}
NAMED = {'oldfield': 'Old battlefield', 'deserted': 'Deserted village', 'oldbridge': 'Broken bridge',
         'namestone': 'Stone of names', 'fallenking': 'Fallen statue', 'gallows': 'Gallows hill', 'quarry': 'Old quarry',
         'wreck': 'Shipwreck', 'hermitage': 'Hermitage', 'colony': 'Leper colony'}
DESC = {'oldfield': 'An old battlefield: grassy mounds over the dead of a war long ago, and a cairn for the fallen.',
        'deserted': 'A deserted village. The roofs are gone; nobody has lived here for a long time.',
        'oldbridge': 'A broken bridge of the old Empire: its piers still stand in the river, and there is a ford beside it.',
        'namestone': 'A memorial stone by the road, cut with names.',
        'fallenking': 'A great statue lies in the grass, its head beside it.',
        'gallows': 'A gallows hill where the roads meet. The Watch hangs its sentences here.',
        'quarry': 'An old quarry, half-cut blocks still lying where they were left.',
        'wreck': 'A wrecked ship on the shore. You can reach it at low tide.',
        'hermitage': 'A hermit\'s hut, far from the roads.',
        'colony': 'A leper colony outside the city, with a bell on a post by the gate.'}
POI_LOOK = {'dwarfstone': ('┬', (214, 176, 110)), 'moonstone': ('·', (214, 226, 255)), 'skullpole': ('ⁿ', (220, 210, 186)),
            'scratch': ('«', (204, 182, 110)), 'cache': ('*', (236, 210, 120))}
POI_NAMED = {'dwarfstone': 'Dwarf boundary stone', 'moonstone': 'Moonstone', 'skullpole': 'Skull pole',
             'scratch': 'Kobold scratches', 'cache': "Kobolds' hoard"}
CAUSES = {
    'plague': 'the Grey Plague came to {v} in the spring; those who lived went away before the harvest, and nobody '
              'went back.',
    'war': 'soldiers burned {v} in a war between the crowns, and drove off its herds; its people never came home.',
    'dragon': 'a dragon came down on {v} three nights running. On the fourth day the village stood empty, and it has '
              'stood empty since.'}
WHO_NOW = ['bandits', 'hermit', 'ghost', None, None]
SHIPS = ['Gull', 'Mercy', 'Fair Wind', 'Saint Edda', 'Grey Lady', 'Salt Rose', 'Heron', 'Good Hope', 'Merry Wren',
         'Black Swan', 'Patience', 'Morning Star']
NAMES_ON = ['Aldo, Bennet, Cuthbert', 'Hew the Smith, Wat, the two sons of Garrick', 'Osric, Dunstan, Ivo and Ivo\'s '
            'brother', 'forty men of the levy, and their captain', 'Tamsin\'s Edwin, Mabel\'s Hob, Old Jory']
ANNIVERSARY_HOUR = 22


def is_old(site):
    return site.kind in LOOK


def doy(game):
    """The day of the year, 1 to 360."""
    _y, mo, d, _wd = CAL._split(game.day)
    return mo * CAL.DAYS_IN_MONTH + d


def date_of(n):
    mo, d = divmod(n - 1, CAL.DAYS_IN_MONTH)
    return f'the {CAL.ordinal(d + 1)} of {CAL.MONTHS[mo]}'


def event_of(game, site):
    from . import history as HI
    k = getattr(site, 'event', None)
    evs = HI.events(game.world)
    return evs[k] if k is not None and k < len(evs) else None


# ------------------------------------------------------------------ on the world map
def place(game, m, world, reach_set):
    """After the history is made: its battles and empty villages, and the other old places, on the land."""
    from .sites import Site
    from .world import scaled
    from .history import ago  # noqa: F401  (the history must exist first)
    w = m.w
    taken = [(s.x, s.y) for s in world.settlements] + [(q.x, q.y) for q in world.sites] + \
            [(d.x, d.y) for d in world.dungeons.values()] + [(h.x, h.y) for h in world.holds]
    used = {s.name for s in world.sites}
    bad = (D.ROAD, D.TOWN, D.CITY, D.ENTR, D.RIVER, D.CASTLE, D.FORT)

    def free(x, y, gap=4):
        i = y * w + x
        return (3 <= x < w - 3 and 3 <= y < m.h - 3 and i in reach_set and D.TILES[m.t[i]].walk and m.t[i] not in bad
                and i not in world.wonder_cells and all(cheb(x, y, a, b) >= gap for a, b in taken))

    def near(x, y, lo, hi, gap=4, pred=None):
        spots = [(x + dx, y + dy) for dx in range(-hi, hi + 1) for dy in range(-hi, hi + 1) if lo <= max(abs(dx), abs(dy))]
        random.shuffle(spots)
        return next(((a, b) for a, b in spots if m.inb(a, b) and free(a, b, gap) and (pred is None or pred(a, b))), None)

    def add(kind, xy, name, **kw):
        if name in used:
            name = f'{name} ({len(world.sites)})'
        st = Site(len(world.sites), kind, xy[0], xy[1], name)
        st.faction = world.region_at(*xy).faction
        for k, v in kw.items():
            setattr(st, k, v)
        world.sites.append(st)
        taken.append(xy)
        used.add(name)
        return st

    H = world.history
    # the empty villages: events of their own, set into the history before it is numbered again
    from .towns import town_names
    vnames = [n for n in town_names('human') if not any(s.name == n for s in world.settlements)]
    start = min((e['year'] for e in H), default=CAL.YEAR - 200)
    empty = []
    for _ in range(scaled(2)):
        spot = None
        for _t in range(400):
            x, y = random.randint(4, w - 5), random.randint(4, m.h - 5)
            if free(x, y, 8) and 4 <= world.road_dist[y * w + x] <= 24 and m.tile(x, y) in (GRASS, D.FOREST, D.HILLS) \
                    and all(cheb(x, y, s.x, s.y) >= 10 for s in world.settlements):
                spot = (x, y)
                break
        if not spot or not vnames:
            continue
        v = vnames.pop()
        cause = random.choice(list(CAUSES))
        e = dict(year=random.randint(start + 10, CAL.YEAR - 30), ch='The Old Days', kind='deserted',
                 title=f'The emptying of {v}', x=spot[0], y=spot[1], prio=1, cause=cause, village=v)
        e['text'] = f'In {e["year"]} AR ' + CAUSES[cause].format(v=v)
        H.append(e)
        empty.append(e)
        taken.append(spot)
    H.sort(key=lambda e: e['year'])
    for i, e in enumerate(H):
        e['id'] = i
    for e in empty:
        taken.remove((e['x'], e['y']))
        st = add('deserted', (e['x'], e['y']), e['village'], event=e['id'], cause=e['cause'],
                 who=random.choice(WHO_NOW))
        e['lead'] = ('site', st.id)
    # the old battlefields beside the villages they are named for
    for e in [e for e in H if e.get('field')][:scaled(4)]:
        spot = near(e['x'], e['y'], 2, 7)
        if not spot:
            continue
        s = world.settlement_at(e['x'], e['y'])
        name = f'The Old Field of {s.name}' if s else 'The Old Field'
        e['doy'] = random.randint(1, 360)
        st = add('oldfield', spot, name, event=e['id'])
        e.setdefault('lead', ('site', st.id))
    # broken bridges of the old Empire, where an old way meets a river
    riv = getattr(m, 'river', None) or bytearray(w * m.h)
    cells = [i for i, v in enumerate(riv) if v and world.road_dist[i] >= 6]
    random.shuffle(cells)
    from .hidden import VARNISH
    made = 0
    for i in cells:
        if made >= scaled(2):
            break
        x, y = i % w, i // w
        spot = near(x, y, 1, 1, 10)
        if spot:
            vert = sum(1 for dy in (-1, 1) if m.inb(x, y + dy) and riv[(y + dy) * w + x]) >= 1
            add('oldbridge', spot, f'The Broken Bridge of {random.choice(VARNISH)}', river=(x, y), flows='ns' if vert else 'ew')
            made += 1
    # memorials: the stones of names by the roads, an emperor's statue, the gallows hills where roads meet
    fields = [e for e in H if e.get('field')]
    for k in range(scaled(2)):
        e = random.choice(fields) if fields else None
        base = (e['x'], e['y']) if e else (world.settlements[0].x, world.settlements[0].y)
        spot = near(*base, 3, 12, pred=lambda a, b: 1 <= world.road_dist[b * w + a] <= 3)
        if spot:
            add('namestone', spot, f'The Stone of {e["title"].replace("The ", "the ") if e else "the Fallen"}',
                event=e['id'] if e else None, names=random.choice(NAMES_ON))
    found = next((e for e in H if e['kind'] == 'empire'), None)
    if found:
        spot = None
        for _t in range(300):
            x, y = random.randint(4, w - 5), random.randint(4, m.h - 5)
            if free(x, y, 8) and 3 <= world.road_dist[y * w + x] <= 14:
                spot = (x, y)
                break
        if spot:
            add('fallenking', spot, 'The Fallen Emperor', event=found['id'])
    cross = [i for i, t in enumerate(m.t) if t == D.ROAD and sum(1 for o in (1, -1, w, -w) if 0 <= i + o < len(m.t)
                                                                   and m.t[i + o] == D.ROAD) >= 3]
    random.shuffle(cross)
    made = 0
    for i in cross:
        if made >= scaled(2):
            break
        x, y = i % w, i // w
        if not any(5 <= cheb(x, y, s.x, s.y) <= 20 and s.kind in ('town', 'city', 'metropolis') for s in world.settlements):
            continue
        spot = near(x, y, 1, 2, 6)
        if spot:
            add('gallows', spot, 'Gallows Hill')
            made += 1
    # quarries in the hills
    hills = [i for i, t in enumerate(m.t) if t == D.HILLS]
    random.shuffle(hills)
    made = 0
    for gap, rd in ((10, 12), (6, 30)):                # near a road if it can be, else further out
        for i in hills:
            if made >= scaled(2):
                break
            x, y = i % w, i // w
            if free(x, y, gap) and world.road_dist[i] <= rd:
                reg = world.region_at(x, y)
                add('quarry', (x, y), f'The Old Quarry of {reg.name}', flooded=random.random() < .4)
                made += 1
    # wrecks on the shore
    shore = [i for i, t in enumerate(m.t) if t in (SAND, GRASS) and sum(1 for o in (1, -1, w, -w)
                                                                    if 0 <= i + o < len(m.t) and m.t[i + o] == WATER) >= 1]
    random.shuffle(shore)
    made = 0
    ships = SHIPS[:]
    random.shuffle(ships)
    for gap in (12, 6):
        for i in shore:
            if made >= scaled(2) or not ships:
                break
            x, y = i % w, i // w
            if free(x, y, gap) and not riv[i]:
                add('wreck', (x, y), f'The Wreck of the {ships.pop()}')
                made += 1
    # hermitages, far from the roads
    made = 0
    for _t in range(6000):
        if made >= scaled(2):
            break
        x, y = random.randint(4, w - 5), random.randint(4, m.h - 5)
        i = y * w + x
        wild = m.t[i] in (D.FOREST, D.HILLS, TREE) if _t < 3000 else m.t[i] not in (SAND, D.SWAMP)
        if free(x, y, 10 if _t < 3000 else 6) and wild and (8 if _t < 3000 else 5) <= world.road_dist[i] <= 40:
            add('hermitage', (x, y), f'{random.choice(["Old", "Brother", "Mother", "Father"])} '
                f'{random.choice(["Wendel", "Ninian", "Hilde", "Corwen", "Ismay", "Aldo", "Brannoc"])}\'s Hut')
            made += 1
    # a leper colony outside some of the cities
    cities = [s for s in world.settlements if s.is_city and s.race == 'human']
    random.shuffle(cities)
    for s in cities[:scaled(1) + 1]:
        spot = near(s.x, s.y, 5, 9)
        if spot:
            add('colony', spot, f'The Lazar House of {s.name}', city=s.id)
    marks(game, m, world, free, taken)


def marks(game, m, world, free, taken):
    """Small signs of whose land it was, found only by walking up to them."""
    from .events import POI
    from .sites import SITE_LOOK  # noqa: F401
    w = m.w

    def poi(kind, x, y, name, **kw):
        q = POI(len(world.pois), kind, x, y, name)
        q.secret = True
        for k, v in kw.items():
            setattr(q, k, v)
        world.pois.append(q)
        taken.append((x, y))
        return q

    def ring(cx, cy, lo, hi, gap=3):
        for _t in range(200):
            x, y = cx + random.randint(-hi, hi), cy + random.randint(-hi, hi)
            if lo <= cheb(x, y, cx, cy) <= hi and m.inb(x, y) and free(x, y, gap):
                return x, y
        return None
    for s in [s for s in world.settlements if s.kind == 'deephold']:
        for _ in range(2):
            spot = ring(s.x, s.y, 9, 16)
            if spot:
                poi('dwarfstone', *spot, 'A dwarf boundary stone', hold=s.id)
    elves = [s for s in world.sites if s.kind == 'glade'] + [s for s in world.settlements if getattr(s, 'elder', False)]
    for s in elves:
        spot = ring(s.x, s.y, 14, 18)
        if not spot:
            continue
        line = [spot]
        for k in (2, 3):                           # each nearer the hidden place than the last
            x, y = line[-1]
            nx, ny = x + (s.x - x) * k // 6, y + (s.y - y) * k // 6
            more = ring(nx, ny, 0, 2, 2)
            if more and cheb(*more, s.x, s.y) >= 5:
                line.append(more)
        prev = None
        for k, (x, y) in enumerate(line):
            q = poi('moonstone', x, y, 'A moonstone', toward=(s.x, s.y), step=k)
            if prev:
                prev.next = q.id
            prev = q
    from . import tribes as TR
    for s in [s for s in world.sites if TR.is_camp(s)]:
        if s.kind == 'kobolds':
            spot = ring(s.x, s.y, 5, 8)
            if spot:
                hoard = ring(spot[0], spot[1], 4, 8)
                if hoard:
                    c = poi('cache', *hoard, "The kobolds' hoard")
                    poi('scratch', *spot, 'Kobold scratches', cache=c.id)
        elif random.random() < .7:
            spot = ring(s.x, s.y, 6, 9)
            if spot:
                poi('skullpole', *spot, 'A skull pole', camp=s.id)


# ------------------------------------------------------------------ the play maps
def _base(game, site, w, h, ground=GRASS):
    from .entities import GameMap
    m = GameMap(site.map_key, 'town', site.name, w, h, ground)
    m.glows, m.lights = [], []
    m.radius, m.sid, m.hid, m.signs = 60, None, None, []
    m.site = site.id
    m.old = site.kind
    m.dug = set()
    m.level = game.world.danger_at(site.x, site.y) + 1
    return m


def _done(m, entry):
    m.entry = entry
    _reach_all(m, (entry[0] + 1, entry[1]))
    for i in range(len(m.seen)):
        m.seen[i] = 1
    m.lights = list(m.glows)
    return m


def _reach(m, start):
    seen, todo = {start}, [start]
    while todo:
        x, y = todo.pop()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                c = (x + dx, y + dy)
                if c not in seen and m.inb(*c) and (D.TILES[m.tile(*c)].walk or m.tile(*c) == DOOR):
                    seen.add(c)
                    todo.append(c)
    return seen


def _reach_all(m, start):
    """Every telling thing can be walked up to: a cut-off one gets a trodden way to it."""
    m.set(*start, m.tile(*start) if D.TILES[m.tile(*start)].walk else PATH)
    got = _reach(m, start)
    for i, t in enumerate(m.t):
        if t not in BUMP:
            continue
        x, y = i % m.w, i // m.w
        if any((x + a, y + b) in got for a in (-1, 0, 1) for b in (-1, 0, 1)):
            continue
        cx, cy = x, y
        for _ in range(400):
            dx, dy = (start[0] > cx) - (start[0] < cx), (start[1] > cy) - (start[1] < cy)
            if dx and dy:
                if random.random() < .5:
                    dy = 0
                else:
                    dx = 0
            cx, cy = cx + dx, cy + dy
            if (cx, cy) in got:
                break
            if m.tile(cx, cy) not in BUMP and not D.TILES[m.tile(cx, cy)].walk and m.tile(cx, cy) != DOOR:
                m.set(cx, cy, SHALLOW if m.tile(cx, cy) == WATER else PATH)
        got = _reach(m, start)


def _scatter(m, tile, p, on=(GRASS,)):
    for i, t in enumerate(m.t):
        if t in on and random.random() < p:
            m.t[i] = tile


def _path(m, a, b, tile=PATH):
    from .nature import path
    path(m, a, b, tile)


def _ruin_house(m, x0, y0, x1, y1, door):
    """Four walls with gaps, grass inside: the roof fell in long ago."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            edge = y in (y0, y1) or x in (x0, x1)
            if edge:
                m.set(x, y, WALL if random.random() < .72 else RUBBLE)
            elif random.random() < .12:
                m.set(x, y, RUBBLE)
            else:
                m.set(x, y, GRASS)
    m.set(*door, GRASS)


def site_map(game, site):
    """The play map of an old place, from the world seed and where it lies."""
    state = random.getstate()
    random.seed(game.seed * 6151 + site.x * 977 + site.y * 37 + 11)
    try:
        m = BUILD[site.kind](game, site)
    finally:
        random.setstate(state)
    folk(game, site, m)
    return m


def _oldfield(game, site):
    w, h = 70, 40
    m = _base(game, site, w, h)
    _scatter(m, TREE, .03)
    _scatter(m, D.SPEARS, .015)
    for _ in range(14):
        x, y = random.randint(12, w - 6), random.randint(4, h - 5)
        if m.tile(x, y) == GRASS:
            m.set(x, y, D.MOUND)
    cx, cy = w // 2 + 6, h // 2
    m.set(cx, cy, D.CAIRN)
    _path(m, (0, h // 2), (cx - 1, cy))
    return _done(m, (0, h // 2))


def _deserted(game, site):
    w, h = 76, 44
    m = _base(game, site, w, h)
    _scatter(m, TREE, .04)
    cy = h // 2
    _path(m, (0, cy), (w - 10, cy))
    for x0 in (10, 24, 38, 52):
        for top in (True, False):
            if random.random() < .2:
                continue
            y0 = cy - 8 if top else cy + 3
            _ruin_house(m, x0, y0, x0 + 7, y0 + 5, (x0 + 3, y0 + 5 if top else y0))
    m.set(32, cy - 2, WELL)
    for y in range(cy + 11, min(h - 2, cy + 18)):          # the field gone to weeds
        for x in range(8, 30):
            m.set(x, y, FIELD if random.random() < .3 else D.BRAMBLE if random.random() < .25 else GRASS)
    # the burnt chapel at the far end
    cx0, cy0 = w - 14, cy - 5
    for y in range(cy0, cy0 + 11):
        for x in range(cx0, cx0 + 10):
            edge = y in (cy0, cy0 + 10) or x in (cx0, cx0 + 9)
            m.set(x, y, (WALL if random.random() < .6 else RUBBLE) if edge else (D.ASH if random.random() < .6 else RUBBLE
                                                                               if random.random() < .2 else FLOOR))
    m.set(cx0, cy, GRASS)
    m.set(cx0 + 7, cy, ALTAR)
    return _done(m, (0, cy))


def _oldbridge(game, site):
    w, h = 60, 40
    m = _base(game, site, w, h)
    _scatter(m, TREE, .05)
    rx = w // 2
    for y in range(h):
        for x in range(rx - 4, rx + 5):
            m.set(x, y, WATER if abs(x - rx) <= 2 else SHALLOW)
    by = h // 2
    for x in (rx - 2, rx + 2):                       # the piers stand where the deck ran
        m.set(x, by, D.PIER)
    for x in (rx - 4, rx - 3, rx + 3, rx + 4):
        m.set(x, by, D.RUBBLE)
    for x in range(rx - 4, rx + 5):                  # the ford, downstream
        m.set(x, by + 6, SHALLOW)
    _path(m, (0, by), (rx - 5, by))
    _path(m, (rx + 5, by), (w - 1, by))
    _path(m, (rx - 5, by), (rx - 5, by + 6))
    _path(m, (rx + 5, by + 6), (rx + 5, by))
    return _done(m, (0, by))


def _memorial(game, site):
    w, h = 50, 26
    m = _base(game, site, w, h)
    _scatter(m, TREE, .04)
    cy = h // 2
    _path(m, (0, cy), (w - 1, cy))
    if site.kind == 'namestone':
        m.set(26, cy - 2, D.NAMESTONE)
    elif site.kind == 'fallenking':
        for x in range(20, 28):                      # the emperor lies along the grass
            m.set(x, cy - 3, D.STATUE)
        m.set(30, cy - 4, D.HEAD)
        m.set(19, cy - 3, D.STONE)
    else:
        for y in range(cy - 6, cy - 1):              # the hill, and the gallows on it
            for x in range(18, 32):
                if ((x - 25) / 7) ** 2 + ((y - cy + 3.5) / 2.6) ** 2 < 1:
                    m.set(x, y, D.HILLS)
        m.set(25, cy - 4, D.GALLOWS)
        m.set(23, cy - 3, D.GRASS)
    return _done(m, (0, cy))


def _quarry(game, site):
    w, h = 64, 40
    m = _base(game, site, w, h)
    cx, cy = w // 2 + 4, h // 2
    for y in range(h):
        for x in range(w):
            d = ((x - cx) / 22) ** 2 + ((y - cy) / 14) ** 2
            if d > 1 and x > 8:
                m.set(x, y, D.ROCK)
            elif d > .82 and x > 8:
                m.set(x, y, D.BAREROCK)
    if getattr(site, 'flooded', False):
        for y in range(h):
            for x in range(w):
                d = ((x - cx - 6) / 11) ** 2 + ((y - cy) / 7) ** 2
                if d < 1:
                    m.set(x, y, WATER if d < .7 else SHALLOW)
    for _ in range(16):
        x, y = random.randint(cx - 18, cx + 18), random.randint(cy - 10, cy + 10)
        if m.tile(x, y) in (GRASS, D.BAREROCK):
            m.set(x, y, D.BLOCK)
    for k in range(5):                               # the giant who was never finished, lying in the cut
        m.set(cx - 12 + k, cy + 7, D.STATUE)
    m.set(cx - 13, cy + 7, D.HEAD)
    from .nature import path
    path(m, (0, cy), (cx - 14, cy), PATH, (GRASS, D.BAREROCK, D.ROCK))
    return _done(m, (0, cy))


def _wreck(game, site):
    w, h = 64, 36
    m = _base(game, site, w, h, SAND)
    for y in range(h):
        for x in range(w):
            if x >= 40:
                m.set(x, y, WATER)
            elif x >= 26:
                m.set(x, y, D.WETSAND)
            elif x < 8:
                m.set(x, y, GRASS)
    hx, hy = 32, h // 2 - 3                           # the hull on its side, broken open to the shore
    for y in range(hy, hy + 7):
        for x in range(hx, hx + 12):
            edge = y in (hy, hy + 6) or x in (hx, hx + 11)
            m.set(x, y, D.HULL if edge else D.WETSAND)
    m.set(hx, hy + 3, D.WETSAND)
    m.set(hx + 9, hy + 3, D.SEACHEST)
    for _ in range(10):
        x, y = random.randint(26, 39), random.randint(2, h - 3)
        if m.tile(x, y) == D.WETSAND:
            m.set(x, y, RUBBLE)
    return _done(m, (0, h // 2))


def _hermitage(game, site):
    w, h = 50, 30
    m = _base(game, site, w, h)
    _scatter(m, TREE, .25)
    cy = h // 2
    hx, hy = 24, cy - 3
    for y in range(hy, hy + 6):
        for x in range(hx, hx + 7):
            m.set(x, y, WALL if y in (hy, hy + 5) or x in (hx, hx + 6) else FLOOR)
    m.set(hx, cy, DOOR)
    m.set(hx + 4, hy + 1, D.BED)
    m.set(hx + 2, hy + 4, D.FIREPIT)
    m.glows.append((hx + 2, hy + 4, (255, 140, 50), 4))
    m.set(hx + 9, cy + 3, D.FIELD)
    _path(m, (0, cy), (hx - 1, cy))
    return _done(m, (0, cy))


def _colony(game, site):
    w, h = 60, 34
    m = _base(game, site, w, h)
    _scatter(m, TREE, .03)
    cy = h // 2
    for y in range(4, h - 4):                        # a low wall round the huts
        for x in (16, w - 6):
            m.set(x, y, WALL)
    for x in range(16, w - 5):
        m.set(x, 4, WALL)
        m.set(x, h - 5, WALL)
    m.set(16, cy, GRASS)
    m.set(14, cy - 1, D.LEPERBELL)
    for x0, y0 in ((22, 7), (34, 7), (22, cy + 3), (34, cy + 3), (46, 10)):
        for y in range(y0, y0 + 5):
            for x in range(x0, x0 + 7):
                m.set(x, y, WALL if y in (y0, y0 + 4) or x in (x0, x0 + 6) else FLOOR)
        m.set(x0 + 3, y0 + 4 if y0 < cy else y0, DOOR)
    _path(m, (0, cy), (15, cy))
    return _done(m, (0, cy))


BUILD = {'oldfield': _oldfield, 'deserted': _deserted, 'oldbridge': _oldbridge, 'namestone': _memorial,
         'fallenking': _memorial, 'gallows': _memorial, 'quarry': _quarry, 'wreck': _wreck, 'hermitage': _hermitage,
         'colony': _colony}


def folk(game, site, m):
    """Who lives at the place now."""
    from .entities import make_npc, make_monster
    from .towns import town_names
    names = town_names('human')
    lvl = m.level
    if site.kind == 'deserted':
        who = getattr(site, 'who', None)
        if who == 'bandits':
            for _ in range(random.randint(3, 5)):
                spot = _free(m, (20, m.w - 20), (4, m.h - 4))
                if spot:
                    m.mons.append(make_monster(game, random.choice(['bandit', 'bandit', 'brigand']), *spot, lvl))
        elif who == 'hermit':
            spot = _free(m, (24, 40), (m.h // 2 - 6, m.h // 2 + 6))
            if spot:
                m.mons.append(make_npc(game, f'{names.pop()} the Hermit', 'oldplace', '#c8b890', *spot, True))
    elif site.kind == 'hermitage':
        m.mons.append(make_npc(game, site.name.replace("'s Hut", ''), 'oldplace', '#d8c8a0', 27, m.h // 2, True))
    elif site.kind == 'colony':
        m.mons.append(make_npc(game, f'Brother {names.pop()}', 'oldplace', '#e0d8b0', 20, m.h // 2 + 1, True))
        for _ in range(4):
            spot = _free(m, (20, m.w - 8), (6, m.h - 6))
            if spot:
                o = make_npc(game, 'A leper', 'leper', '#a8a890', *spot, False)
                m.mons.append(o)
    elif site.kind == 'gallows':
        m.mons.append(make_npc(game, 'A Watchman', 'oldplace', '#b0b8c8', 27, m.h // 2 - 2, True))


def _free(m, xs, ys):
    for _ in range(200):
        x, y = random.randint(*xs), random.randint(*ys)
        if m.inb(x, y) and D.TILES[m.tile(x, y)].walk and not m.mon_at(x, y):
            return x, y
    return None


# ------------------------------------------------------------------ being there
def on_enter(game, site, m):
    k = site.kind
    e = event_of(game, site)
    line = {'oldfield': 'Low mounds lie under the grass, in rows. Here and there a rusted point sticks up.',
            'deserted': 'Nobody lives here. Walls without roofs, and nettles in the doorways.',
            'oldbridge': 'The river runs between stone piers. The bridge that stood on them is long gone.',
            'namestone': 'A grey stone stands by the road, cut with names.',
            'fallenking': 'A great stone figure lies in the grass, face down. Its head lies a little way off.',
            'gallows': 'A gallows on the hill where the roads meet. The wind turns what hangs there.',
            'quarry': 'An old quarry. Blocks lie half cut, as if the masons went to dinner and never came back.',
            'wreck': 'A broken ship lies on its side at the edge of the sea.',
            'hermitage': 'Woodsmoke, and a hut nobody would find by chance.',
            'colony': 'A wall of rough stone, and a bell on a post by the gate. Folk keep their distance here.'}[k]
    if k == 'deserted' and getattr(site, 'who', None) == 'ghost' and night(game):
        line += ' A pale shape moves between the houses.'
        if not getattr(m, 'ghosted', None) == game.day:
            from .entities import make_monster
            spot = _free(m, (24, m.w - 20), (6, m.h - 6))
            if spot:
                m.mons.append(make_monster(game, 'ghost', *spot, m.level))
            m.ghosted = game.day
    if k == 'wreck':
        line += ' The tide is out: you can walk out to it.' if low_tide(game) else ' The tide is in, round the hull.'
    if k == 'quarry' and getattr(site, 'flooded', False):
        line += ' Water has filled the deepest cut.'
    game.msg(line, 'info')
    if e and k in ('oldfield', 'deserted'):
        from . import history as HI
        if not HI.known(game, e):
            HI.learn(game, e, 'seen', where=site.name)
    alms_here(game, site)
    walk_dead(game, site, m)


def night(game):
    from . import towns as TD
    return TD.is_night(game)


def low_tide(game):
    from .nature import low_tide as lt
    return lt(game)


def blocked(game, x, y):
    """Wet sand is under the sea when the tide is in."""
    if game.map.tile(x, y) == D.WETSAND and not low_tide(game):
        return 'The tide is in. The sea covers the sand out to the wreck.'
    return None


def walk_dead(game, site, m):
    """On the night of the battle, the dead walk their field."""
    if site.kind != 'oldfield':
        return
    e = event_of(game, site)
    from . import debug as DBG
    if not e or not (doy(game) == e.get('doy') or DBG.has(game, 'oldnight')) or not night(game) \
            or getattr(m, 'walked', None) == game.day:
        return
    from .entities import make_monster
    m.walked = game.day
    for _ in range(random.randint(4, 6)):
        spot = _free(m, (14, m.w - 4), (3, m.h - 4))
        if spot:
            o = make_monster(game, random.choice(['skeleton', 'skeleton', 'skel_warrior']), *spot, m.level)
            o.awake = True
            m.mons.append(o)
    spot = _free(m, (30, m.w - 4), (3, m.h - 4))
    if spot:
        o = make_monster(game, 'wight', *spot, m.level + 1)
        o.awake = True
        m.mons.append(o)
    game.msg(f'It is the night of {e["title"]}. The mounds stir, and the dead of the field get up out of the grass.',
             'bad')


def on_step(game):
    m = game.map
    site = game.world.sites[m.site]
    if site.kind == 'oldfield' and game.turn % 20 == 0:
        walk_dead(game, site, m)


BUMP = {D.MOUND, D.DUGMOUND, D.CAIRN, D.PIER, D.NAMESTONE, D.STATUE, D.HEAD, D.GALLOWS, D.BLOCK, D.SEACHEST, D.HULL,
        D.LEPERBELL, ALTAR, WELL}


def bump(game, x, y):
    """Walking into the telling things of an old place. Returns the turns it took, or None."""
    m = game.map
    t = m.tile(x, y)
    if t not in BUMP:
        return None
    site = game.world.sites[m.site]
    e = event_of(game, site)
    say = game.msg
    from . import chronicle as CH
    from . import history as HI
    if t == D.MOUND:
        return dig(game, site, e, x, y)
    if t == D.DUGMOUND:
        say('You dug this mound already. Only bones and earth.')
        return 0
    if t == D.CAIRN and e:
        text = (f'A cairn of field stones. A slab on top says that here lie the dead of {e["title"]}, who fell on '
                f'{date_of(e["doy"])}, {e["year"]} AR.')
        CH.add(game, 'Places', f'{site.name}: the dead of {e["title"]} lie here. They fell on {date_of(e["doy"])}, '
               f'{e["year"]} AR; on that night, they say, they walk.', 'seen', where=site.name, place=(site.x, site.y),
               key=f'old:{site.id}', quiet=True)
        HI.learn(game, e, 'seen', where=site.name)
        game.request = ('dialog', 'A cairn', text)
        return 0
    if t == D.PIER:
        return pier(game, site)
    if t == D.NAMESTONE:
        text = f'Names are cut into the stone, worn soft by the rain: {getattr(site, "names", "names nobody reads now")}.'
        if e:
            text += f' Above them: "They fell for {e["win"] if e.get("win") else "the crown"} in {e["title"].replace("The ", "the ")}, {e["year"]} AR."'
            HI.learn(game, e, 'seen', where=site.name)
        CH.add(game, 'Places', f'{site.name}: names of the fallen by the road.', 'seen', where=site.name,
               place=(site.x, site.y), key=f'old:{site.id}', quiet=True)
        game.request = ('dialog', site.name, text)
        return 0
    if t in (D.STATUE, D.HEAD) and site.kind == 'fallenking':
        text = 'The stone emperor lies on his face in the grass, his crown cracked off. The head looks up at the sky.'
        if e:
            text += f' Letters on the plinth: {e["title"].replace("The founding of", "Founder of")}.'
            HI.learn(game, e, 'seen', where=site.name)
        CH.add(game, 'Places', f'{site.name}: an emperor of stone lies in the grass, his head beside him.', 'seen',
               where=site.name, place=(site.x, site.y), key=f'old:{site.id}', quiet=True)
        game.request = ('dialog', site.name, text)
        return 0
    if t in (D.STATUE, D.HEAD):
        say('A giant of stone, never finished: a face without eyes, hands still inside the block.')
        return 0
    if t == D.GALLOWS:
        return gallows(game, site)
    if t == D.BLOCK:
        return block(game, site, x, y)
    if t == D.SEACHEST:
        return search_wreck(game, site, x, y)
    if t == D.HULL:
        say("Old ship's timbers, black with tar and weed.")
        return 0
    if t == D.LEPERBELL:
        say('You ring the bell. After a while a man in a grey robe comes to the gate, and keeps his distance.')
        return 1
    if t == ALTAR and site.kind == 'deserted':
        if not getattr(site, 'prayed', False):
            site.prayed = True
            say('A blackened altar. Someone has laid wild flowers on it, not long ago.')
        else:
            say('A blackened altar, and dry flowers.')
        return 0
    if t == WELL and site.kind == 'deserted':
        say('The well is choked with stones. Somebody made sure nobody would drink from it again.'
            if getattr(site, 'cause', '') == 'plague' else 'The bucket is long gone. Far down, water shines.')
        return 0
    return None


def dig(game, site, e, x, y):
    from .nature import curio
    from . import debug as DBG
    m, p = game.map, game.player
    m.set(x, y, D.DUGMOUND)
    game.end_turn(6)
    blade = not getattr(site, 'blade_found', False) and (random.random() < .04 or DBG.has(game, 'oldfind'))
    if blade and e:
        site.blade_found = True
        it = old_weapon(game, e, m.level)
        if it and game.add_to_inv(it):
            game.msg(f'Deep in the mound, among the bones, your fingers close on iron that has not rusted through: '
                     f'{it.name}.', 'gold')
            return 0
    r = random.random()
    if r < .6:
        it = curio(game, 'rust')
        game.add_to_inv(it)
        game.msg('You dig into the mound: bones, and a lump of rusted iron that was a sword once.')
    elif r < .72:
        it = curio(game, 'oldcoin')
        game.add_to_inv(it)
        game.msg('Among the bones, a coin of the old days, green with age.', 'good')
    else:
        game.msg('You dig into the mound: only bones and earth.')
    p.food = max(0, p.food - 2)
    return 0


def old_weapon(game, e, lvl):
    from .entities import make_gear
    fams = [f for f in ('longsword', 'shortsword', 'waraxe', 'spear', 'mace') if D.grades(f)]
    if not fams:
        return None
    from .entities import base_for
    it = make_gear(game, base_for(random.choice(fams), lvl + 2), 'magic', lvl + 2)
    title = e['title'][4:] if e['title'].startswith('The ') else e['title']
    it.name = f"{D.BASES[it.base]['name']} of the {title}"
    it.named = True
    return it


def pier(game, site):
    from . import hidden as HP
    text = ('Square-cut stone, black with the river, without mortar: the Varnish built it, and the river has not '
            'moved it in a thousand years. The deck that ran over it fell long ago; the road goes down to a ford.')
    om = game.maps['over']
    ways = [wy for wy in getattr(game.world, 'ways', []) if wy.cells]
    if ways and not getattr(site, 'way_shown', False):
        wy = min(ways, key=lambda wy: min(cheb(i % om.w, i // om.w, site.x, site.y) for i in wy.cells[::3]))
        if min(cheb(i % om.w, i // om.w, site.x, site.y) for i in wy.cells[::3]) <= 40:
            site.way_shown = True
            HP.discover_way(game, wy.id, 'From the old bridge the line of an old road runs on.', HP.stretch(wy, 0, .3))
            text += ' On the far bank you can still make out where the old road ran on.'
    game.request = ('dialog', site.name, text)
    return 0


def gallows(game, site):
    from . import crime as CR
    w = game.world
    watch = (w.powers.get('watch') or {}).get('name', 'the Watch')
    text = (f'A board is nailed to the post, signed by {watch.replace("The ", "the ")}: the names of the hanged, '
            f'and what they did. Robbery on the king\'s road. Horse theft. Murder.')
    if CR.wanted_in(game):
        text += ' Below them, a fresh notice. The face drawn on it looks a lot like yours.'
    game.request = ('dialog', site.name, text)
    return 0


def block(game, site, x, y):
    from .nature import curio
    m = game.map
    done = m.dug
    if (x, y) in done:
        game.msg('A half-cut block. You split it already.')
        return 0
    done.add((x, y))
    game.end_turn(4)
    if random.random() < .18:
        game.add_to_inv(curio(game, 'fossil'))
        game.msg('You knock at a cracked block, and it splits. Inside, curled like a ram\'s horn: a shell of stone.',
                 'good')
    else:
        game.msg('A half-cut block, the chisel marks still sharp. It was never finished.')
    return 0


def search_wreck(game, site, x, y):
    from .entities import Item, random_gear
    from .money import fmt, purse
    p = game.player
    if getattr(site, 'searched', False):
        game.msg('An empty sea chest, its lid split.')
        return 0
    site.searched = True
    game.end_turn(5)
    lvl = game.world.danger_at(site.x, site.y)
    if random.random() < .55:
        game.msg('Someone was here before you. The lid is smashed, the chest is empty, and there are bootprints '
                 'in the wet sand: the wreckers came first.', 'bad')
        return 0
    gold = purse(lvl, 2)
    p.gold += gold
    found = [fmt(gold)]
    if random.random() < .4:
        game.add_to_inv(Item(game.new_id(), 'potion', random.choice(['hp', 'mp'])))
        found.append('a stoppered bottle')
    if random.random() < .2:
        g = random_gear(game, lvl + 1)
        if game.add_to_inv(g):
            found.append(g.name)
    game.msg('Under the wet sail at the bottom of the chest: ' + ', '.join(found) + '.', 'gold')
    return 0


# ------------------------------------------------------------------ the people there
def talk(game, npc):
    from . import events as EV
    m = game.map
    site = game.world.sites[m.site]
    if site.kind == 'colony':
        food = [i for i in game.player.inv if i.k == 'food']
        EV.ask(game, 'oldplace', npc.name, '"Stay on that side of the line, friend. We take what is given at the gate. '
               'Bread, mostly. The city forgets us, but the temple does not, not always."',
               [('Leave food at the gate', 'alms' if food else None), ('Goodbye', 'bye')], site=site.id)
    elif site.kind == 'gallows':
        game.say(npc, random.choice(['Move along. Nothing here for you, unless you want to join them.',
                                     'Three this month. The roads are bad.', 'They hang three days. Then we bury them.']))
    else:
        last = getattr(site, 'told_day', -99)
        if game.day - last < 7:
            game.say(npc, random.choice(['I have told you what I know. Sit by the fire if you like.',
                                         'The quiet is the point. Go on, now.']))
            return
        site.told_day = game.day
        from . import history as HI
        text = HI.hint(game, npc) or '"Out here you hear the wind, and the wolves. Not much else."'
        game.request = ('dialog', npc.name, text if text.startswith('"') else f'"{text}"')


def r_oldplace(game, choice, ctx):
    from . import gods as GD
    p = game.player
    if choice != 'alms':
        return
    food = [i for i in p.inv if i.k == 'food']
    if not food:
        return
    it = food[0]
    if getattr(it, 'n', 1) > 1:
        it.n -= 1
    else:
        p.inv.remove(it)
    site = game.world.sites[ctx['site']]
    if getattr(site, 'alms_day', -1) != game.day:
        site.alms_day = game.day
        GD.gain(game, 2, 'alms')
    game.msg('You leave food at the gate and step back. A hand takes it in, and someone says a blessing on you.',
             'good')


def alms_here(game, site):
    """The temple's bread brought to the lepers' gate."""
    from . import jobs as JB
    if site.kind != 'colony':
        return
    for mi in game.missions:
        if mi.kind == 'alms' and mi.state == 'active' and mi.data.get('site') == site.id and not mi.data.get('reached'):
            game.player.parcels = [pc for pc in game.player.parcels if pc['mid'] != mi.id]
            JB.effects(game, god=(mi.data.get('god'), 4), quiet=True)
            JB._turnin(game, mi, 'You leave the temple\'s bread at the gate, and the brother counts the loaves.')


def make_alms(game, s):
    """A temple job: bread for the lepers outside a city."""
    from . import jobs as JB
    from . import gods as GD
    if 'temple' not in s.services:
        return None
    cols = [q for q in game.world.sites if q.kind == 'colony' and cheb(q.x, q.y, s.x, s.y) <= 90]
    if not cols:
        return None
    q = min(cols, key=lambda q: cheb(q.x, q.y, s.x, s.y))
    god = GD.temple_god(game) if getattr(game.map, 'sid', None) == s.id else getattr(s, 'god', None)
    d = cheb(q.x, q.y, s.x, s.y)
    from .missions import travel_days
    return JB.mission(game, s, 'alms', f'Bread for {JB.the(q.name)}',
                      f'Carry the temple\'s bread to {JB.the(q.name)}, to the {JB._dir(s, q.x, q.y)}, and leave it at the '
                      f'gate. Do not go in. Come back and tell us it is done.', 8 + d * .2, (6, 10),
                      game.day + travel_days(int(d * 1.4)) * 2 + 4,
                      site=q.id, spot=[q.x, q.y], reach=0, where=q.name, god=god)


# ------------------------------------------------------------------ the marks on the world map
def on_poi(game, poi):
    from .engine import dir_name
    from . import chronicle as CH
    w = game.world
    k = poi.kind
    if k not in POI_LOOK:
        return False
    if k == 'dwarfstone':
        s = w.settlements[poi.hold]
        text = (f'A squat stone, cut square, with dwarf runes down one face. Even without the runes you know what '
                f'it says: here begins the land of {s.name}. Mind where you dig.')
        CH.add(game, 'Places', f'A boundary stone marks the land of {s.name}.', 'seen', place=(poi.x, poi.y),
               key=f'mark:{poi.id}', quiet=True)
    elif k == 'moonstone':
        tx, ty = poi.toward
        text = ('A white stone no higher than your knee, cold to the touch, a crescent cut into it. '
                f'Another like it shows pale further {dir_name(tx - poi.x, ty - poi.y)}.')
        nxt = getattr(poi, 'next', None)
        if nxt is not None:
            q = w.pois[nxt]
            from .events import reveal
            reveal(game, q)
        else:
            text = ('A white stone, cold to the touch, a crescent cut into it. This is the last of them. Whatever they '
                    'lead to is close, and does not want to be found.')
    elif k == 'skullpole':
        text = ('A pole hung with skulls, beast and man, and rags that were banners. Orcs set these at the edge of what '
                'they hold. Their camp is not far.')
        st = w.sites[poi.camp]
        game.reveal_place(st.x, st.y)
    elif k == 'scratch':
        c = w.pois[poi.cache]
        text = (f'Scratches on a flat rock, low down, the way kobolds make them: an arrow pointing '
                f'{dir_name(c.x - poi.x, c.y - poi.y)}, and a little star with lines round it. Something shiny.')
        from .events import reveal
        reveal(game, c)
    else:
        if game.day < poi.ready_day:
            game.msg('A hole under a stone, empty now.')
            return True
        poi.ready_day = 10 ** 9
        from .nature import curio
        from .money import fmt
        coins = random.randint(30, 140)
        game.player.gold += coins
        game.add_to_inv(curio(game, 'trinket'))
        text = (f'Under a flat stone, a hole lined with moss, and in it everything shiny the kobolds could carry: '
                f'buttons, a spoon, {fmt(coins)} in odd coins, and a trinket of bright glass.')
    game.request = ('dialog', poi.name, text)
    return True


def register():
    from . import events as EV
    from . import jobs as JB
    from .nature import CURIO
    EV.RESOLVERS['oldplace'] = r_oldplace
    JB.LABEL['alms'] = 'Alms for the lepers'
    JB.KINDS.add('alms')
    JB.MAKE['alms'] = make_alms
    if 'alms' not in JB.TEMPLE:
        JB.TEMPLE.append('alms')
    CURIO.update({'rust': ('A lump of rusted iron', .3, (150, 96, 64), 'It was a sword once, or a spear. Now it is rust.'),
                  'oldcoin': ('An old coin', 3, (150, 170, 120), 'A coin of the old days, green with age. A collector '
                                                                'might want it.'),
                  'trinket': ('A trinket of bright glass', 2, (150, 220, 240), 'Pretty, and worth very little, '
                                                                             'unless you are a kobold.')})


register()
