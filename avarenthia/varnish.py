"""The Varnish (round 12): the empire before the Ruin, in the land and in the chronicle.

- Ruined cities, overgrown, half under the sand, sunk in a marsh or frozen, each spanning a block of 3 x 3 world
  cells. No sign on the world map beforehand: you find one by walking into its zones (columns between the trees, old
  paving, a gate of star-iron without a wall, stones with letters that say its name). In the middle lies the Sky Court
  round its sky well, and under it a hidden dungeon whose way in you find only on the spot.
- Varnish places, hidden until you walk up to them: the towers of the Northern Wall of the nine legions, wind towers,
  the road of the standing dead, a star-iron forge, the Gates of Leagues, a sluice hall, the fallen sky, star houses
  and a sunken harbour. League stones count down IV, III, II, I towards a city.
- Lore (varnishtexts.py): loose fragments for the chronicle's chapter The Varnish; about eight books per world whose
  pages lie where they fit, bound by a library scribe once you have them all; five riddles that grow in The Old Days
  and, made whole, point to a unique hidden place with its own boss.
What belongs to the player (pages, fragments, books bound) lives on the player: p.varnish."""
import random

from . import data as D
from . import varnishtexts as T
from .data import GRASS, TREE, WALL, FLOOR, RUBBLE, WATER, SHALLOW, SAND, DOWN, UP
from .worldgen import cheb

LOOK = {'vcity': ('╩', (176, 190, 224)), 'walltower': ('▐', (168, 176, 196)), 'windtower': ('⌠', (176, 200, 220)),
        'deadroad': ('Ö', (196, 188, 168)), 'forge': ('◘', (150, 170, 220)), 'gate': ('╦', (180, 196, 236)),
        'sluice': ('╟', (150, 180, 200)), 'fallensky': ('♦', (140, 150, 190)), 'starhouse': ('☼', (190, 206, 255)),
        'harbour': ('╢', (150, 176, 196)), 'vdeep': ('▼', (200, 210, 255))}
WHAT = {'vcity': 'a city of the Varnish', 'walltower': 'a tower of the Northern Wall', 'windtower': 'a Varnish wind tower',
        'deadroad': 'a road of the Varnish dead', 'forge': 'a Varnish forge', 'gate': 'a Varnish Gate of Leagues',
        'sluice': 'a Varnish sluice hall', 'fallensky': 'where the sky fell', 'starhouse': 'a Varnish star house',
        'harbour': 'a sunken Varnish harbour', 'vdeep': 'a place the riddles spoke of'}
DESC = {'vcity': 'The ruins of a city of the Varnish, round its Sky Court and the round sky well in the middle.',
        'walltower': 'A broken tower of the Northern Wall, where the nine legions watched the north.',
        'windtower': 'A Varnish wind tower. In a storm it howls.',
        'deadroad': 'An old road of the Varnish, its sides cut with niches where the dead stand bound.',
        'forge': 'A Varnish forge: heaps of slag, and anvils of star-iron that have not rusted.',
        'gate': 'A Gate of Leagues: an arch of star-iron on its own, a star map in the stone before it.',
        'sluice': 'A Varnish sluice hall. Water stands in it.',
        'fallensky': 'Black stones and glassy sand, where something fell from the sky.',
        'starhouse': 'A Varnish star house, where the tellers counted the sky. Dust lies thick on the floor.',
        'harbour': 'A sunken Varnish harbour: column stumps standing in the shallows.',
        'vdeep': 'A place of the Varnish the riddles led you to.'}
LEAGUE = ('IV', 'III', 'II', 'I')
TOC = {'king': 'The Hollow King', 'orcs': 'Where the orcs came', 'vaults': 'What the vaults hold',
       'dead': 'Why the dead stand'}       # the riddles' headings, short enough for the contents
LEAGUE_LOOK = ('│', (196, 200, 214))
NUMERAL = {'IV': 'four', 'III': 'three', 'II': 'two', 'I': 'one'}
CITY_BOSSES = ['iron_sentinel', 'bound_gale', 'standing_legate', 'hollow_echo']
DEEP_BOSS = {'anchor': 'chained_star', 'throne': 'hollow_shard', 'pits': 'first_uncounted', 'vault': 'name_keeper',
             'hall': 'bound_magister'}
WAYS = ('stone', 'air', 'hollow', 'lever')
BIND_PRICE = 500          # binding a book: five silver and an hour
BOUND_PRICE = 2000        # what a library pays for a bound book, once
LORE_PRICE = 300          # the scribe's Varnish shelf: three silver
WALL_FG = D.hexrgb('#8a96b0')
BUMP = {D.VSTONE, D.NICHE, D.VANVIL, D.STARIRON, D.STARMAP, D.SLUICE, D.CHAINLINK, D.AIRWELL, D.HOLLOW, D.VLAMP,
        D.DAYMARKS, D.SKYWELL, D.LITLAMP, D.OPENNICHE, D.BLACKSTONE}
PLACE_KINDS = ('walltower', 'windtower', 'deadroad', 'forge', 'gate', 'sluice', 'fallensky', 'starhouse', 'harbour')


def is_varnish(site):
    return site.kind in LOOK


def st(game):
    """What this hero has of the Varnish: pages, fragments, books bound and sold."""
    p = game.player
    if not hasattr(p, 'varnish'):
        p.varnish = dict(pages=set(), read=set(), frags=set(), lore=set(), bound=set(), sold=set(), whole=set(),
                         stones=set(), lib=0)
    return p.varnish


def letters(game):
    return bool(game.__dict__.get('varnish_letters'))


def info(game):
    return getattr(game.world, 'varnish', None) or {}


# ------------------------------------------------------------------ on the world map
def place(game, m, world, reach_set):
    """Last of all the world: the Varnish cities, their places and wall, the league stones, the five deep places, and
    which books lie in this world and where their pages are. With dice of its own, so the rest of the world comes out
    as it would without them."""
    state = random.getstate()
    random.seed(game.seed * 7717 + 12)
    try:
        _place(game, m, world, reach_set)
    finally:
        random.setstate(state)


def _place(game, m, world, reach_set):
    from .sites import Site
    from .world import scaled, Dungeon
    from . import nature as NT
    w, h = m.w, m.h
    V = world.varnish = dict(ruin={}, wall=[], books=[], pages={}, src={}, deep={})
    taken = [(s.x, s.y) for s in world.settlements] + [(q.x, q.y) for q in world.sites] + \
            [(d.x, d.y) for d in world.dungeons.values()] + [(hh.x, hh.y) for hh in world.holds] + \
            [(q.x, q.y) for q in world.pois]
    bad = (D.ROAD, D.TOWN, D.CITY, D.ENTR, D.RIVER, D.CASTLE, D.FORT, WATER, D.MOUNTAIN)

    def ok(x, y):
        i = y * w + x
        return 3 <= x < w - 3 and 3 <= y < h - 3 and i in reach_set and D.TILES[m.t[i]].walk and m.t[i] not in bad \
            and i not in world.wonder_cells and (x, y) not in V['ruin']

    def free(x, y, gap=4):
        return ok(x, y) and all(cheb(x, y, a, b) >= gap for a, b in taken)

    def near(x, y, lo, hi, gap=4, pred=None):
        spots = [(x + dx, y + dy) for dx in range(-hi, hi + 1) for dy in range(-hi, hi + 1) if lo <= max(abs(dx), abs(dy))]
        random.shuffle(spots)
        return next(((a, b) for a, b in spots if m.inb(a, b) and free(a, b, gap) and (pred is None or pred(a, b))), None)

    def anywhere(pred, gap=6, tries=4000):
        for _t in range(tries):
            x, y = random.randint(4, w - 5), random.randint(4, h - 5)
            if free(x, y, gap if _t < tries // 2 else max(3, gap // 2)) and pred(x, y):
                return x, y
        return None

    def add(kind, xy, name, **kw):
        s = Site(len(world.sites), kind, xy[0], xy[1], name)
        s.faction = world.region_at(*xy).faction
        s.hidden, s.found = True, False
        for k, v in kw.items():
            setattr(s, k, v)
        world.sites.append(s)
        taken.append(xy)
        return s

    def below(site, name, boss, depth):
        did = f'varnish{site.id}'
        danger = world.danger_at(site.x, site.y) + 2
        dg = Dungeon(did, name, depth, danger, 'rooms', 'vault', boss, WALL_FG, site.x, site.y, False)
        dg.site, dg.size, dg.varnish, dg.vn = site.id, 'middle', True, site.kind
        world.dungeons[did] = dg
        site.below = did
        return dg

    def land(x, y):
        t = m.tile(x, y)
        b = NT.biome(m, x, y)
        if t == SAND or b in ('desert', 'dune', 'dune_crest', 'bone_sand', 'badlands', 'salt_edge'):
            return 'sand'
        if t == D.SWAMP or b in ('marsh', 'swamp', 'mangrove', 'floodplain'):
            return 'marsh'
        if b in ('tundra', 'tundra_hills', 'ice_shelf', 'taiga', 'shrubland_cold', 'alpine'):
            return 'ice'
        return 'overgrown'

    # the cities: a 3 x 3 block of cells, the Sky Court in the middle one
    names = T.CITY_NAMES[:]
    random.shuffle(names)
    bosses = CITY_BOSSES[:]
    random.shuffle(bosses)
    cities = []
    for k in range(scaled(2)):
        spot = None
        for _t in range(6000):
            loose = _t > 3000                       # a crowded world: closer to the roads and the other places
            x, y = random.randint(6, w - 7), random.randint(6, h - 7)
            if free(x, y, 5 if loose else 10) and world.road_dist[y * w + x] >= (2 if loose else 4) \
                    and all(ok(x + a, y + b) for a in (-1, 0, 1) for b in (-1, 0, 1)) \
                    and all(cheb(x, y, s.x, s.y) >= (8 if loose else 12) for s in world.settlements):
                spot = (x, y)
                break
        if not spot or not names:
            continue
        vname = names.pop()
        s = add('vcity', spot, 'A Varnish ruin', vname=vname, land=land(*spot), way=random.choice(WAYS), open=False,
                named=False)
        below(s, f'Beneath {vname}', bosses[k % len(bosses)], random.randint(2, 3))
        for a in (-1, 0, 1):
            for b in (-1, 0, 1):
                V['ruin'][(spot[0] + a, spot[1] + b)] = s.id
                taken.append((spot[0] + a, spot[1] + b))
        cities.append(s)
    # the Northern Wall: five to seven towers on a line across the north, the wall between them
    n = random.randint(5, 7)
    legions = sorted(random.sample(range(9), n))
    y0 = int(h * random.uniform(.14, .22))
    towers = []
    for j, lg in enumerate(legions):
        x = int(w * (.1 + .8 * (j + .5) / n))
        spot = near(x, y0, 0, 8, 6) or near(x, y0, 0, 16, 4)
        yy = y0
        while not spot and yy < h * .5:                 # a northern sea: the wall stands on the first land south of it
            yy += 8
            spot = near(x, yy, 0, 12, 3)
        if spot:
            towers.append(add('walltower', spot, f'The Tower of the {T.LEGIONS[lg]} Legion', legion=lg, lamp=False))
    if towers:
        random.choice(towers).lamp = True
    for a, b in zip(towers, towers[1:]):
        steps = max(abs(b.x - a.x), abs(b.y - a.y))
        for k in range(1, steps):
            x, y = a.x + (b.x - a.x) * k // steps, a.y + (b.y - a.y) * k // steps
            i = y * w + x
            if m.inb(x, y) and m.t[i] not in bad and (x, y) not in V['ruin']:
                V['wall'].append(i)
    vpick = lambda: random.choice(T.CITY_NAMES).split()[-1]  # noqa: E731

    def one(kind, xy, **kw):
        if xy:
            return add(kind, xy, random.choice(T.PLACE_NAMES[kind]).format(v=vpick(), n=''), **kw)
        return None
    hills = lambda x, y: m.tile(x, y) in (D.HILLS, D.FOREST, GRASS) and any(  # noqa: E731
        m.inb(x + a, y + b) and m.tile(x + a, y + b) in (D.MOUNTAIN, D.HILLS) for a in (-2, 0, 2) for b in (-2, 0, 2))
    for _ in range(scaled(1)):
        one('windtower', anywhere(hills, 10))
    for _ in range(scaled(1)):
        one('deadroad', anywhere(lambda x, y: 2 <= world.road_dist[y * w + x] <= 10, 10))
    crater = next(((x, y) for nm, x, y in world.wonders if nm == 'Starfall Crater'), None)
    one('forge', (near(*crater, 2, 9, 4) if crater else None) or anywhere(hills, 8))
    for _ in range(scaled(1)):
        one('gate', anywhere(lambda x, y: 3 <= world.road_dist[y * w + x] <= 14, 12))
    riv = getattr(m, 'river', None) or bytearray(w * h)
    wet = [i for i, v in enumerate(riv) if v]
    random.shuffle(wet)
    spot = next((s for s in (near(i % w, i // w, 1, 2, 6) for i in wet[:300]) if s), None)
    one('sluice', spot or anywhere(lambda x, y: True, 8))
    one('fallensky', anywhere(lambda x, y: world.road_dist[y * w + x] >= 6, 12))
    for _ in range(scaled(1)):
        one('starhouse', anywhere(lambda x, y: m.tile(x, y) in (D.HILLS, GRASS, SAND), 10))
    shore = lambda x, y: any(m.inb(x + a, y + b) and m.tile(x + a, y + b) == WATER  # noqa: E731
                             for a in (-1, 0, 1) for b in (-1, 0, 1))
    for _ in range(max(1, scaled(1) - 1)):
        one('harbour', anywhere(shore, 12))
    # the five deep places of the riddles
    sky = next(((x, y) for nm, x, y in world.wonders if nm == 'The Sky-Seat'), None)
    spots = {}
    if sky:
        for r in range(2, 40, 2):
            spots['anchor'] = near(*sky, max(0, r - 2), r, 5, shore)
            if spots['anchor']:
                break
    spots.setdefault('anchor', None)
    spots['anchor'] = spots['anchor'] or anywhere(shore, 8)
    city = random.choice(cities) if cities else None
    spots['throne'] = (near(city.x, city.y, 3, 7, 3) if city else None) or anywhere(lambda x, y: True, 8)
    spots['pits'] = anywhere(lambda x, y: x > w * .6 and m.tile(x, y) in (D.HILLS, D.FOREST, GRASS), 8) or \
        anywhere(lambda x, y: x > w * .5, 6)
    spots['vault'] = anywhere(hills, 8) or anywhere(lambda x, y: True, 8)
    road = next((s for s in world.sites if s.kind == 'deadroad'), None)
    spots['hall'] = (near(road.x, road.y, 2, 6, 3) if road else None) or anywhere(lambda x, y: True, 8)
    for key in ('anchor', 'throne', 'pits', 'vault', 'hall'):
        if spots[key]:
            s = add('vdeep', spots[key], T.DEEP_NAMES[key], deep=key, open=True)
            below(s, T.DEEP_NAMES[key], DEEP_BOSS[key], 3)
            V['deep'][key] = s.id
    # league stones count down towards each city
    from .events import POI
    for s in cities:
        start = near(s.x, s.y, 14, 18, 3)
        if not start:
            continue
        prev = None
        for k, num in enumerate(LEAGUE):
            x, y = round(start[0] + (s.x - start[0]) * k / 4), round(start[1] + (s.y - start[1]) * k / 4)
            xy = (x, y) if free(x, y, 2) else near(x, y, 0, 2, 2)
            if not xy or cheb(*xy, s.x, s.y) < 2:
                continue
            q = POI(len(world.pois), 'leaguestone', xy[0], xy[1], f'A league stone, {num}')
            q.secret, q.city, q.num = True, s.id, num
            world.pois.append(q)
            taken.append(xy)
            if prev:
                prev.next = q.id
            prev = q
    choose_books(game, m, world)


def choose_books(game, m, world):
    """About eight books, at least one of every thread, and where each of their pages lies."""
    from . import oldplaces as OP  # noqa: F401
    V = world.varnish
    by = {}
    for b in T.BOOKS:
        by.setdefault(b['thread'], []).append(b['key'])
    chosen = [random.choice(v) for v in by.values()]
    rest = [b['key'] for b in T.BOOKS if b['key'] not in chosen]
    chosen += random.sample(rest, 2)
    V['books'] = chosen
    sites = world.sites

    def kind(*ks):
        return [('site', s.id) for s in sites if s.kind in ks]
    cities = [s for s in sites if s.kind == 'vcity']
    places = {'walltower': kind('walltower'), 'vcity': kind('vcity') + [('dungeon', s.below) for s in cities],
              'starhouse': kind('starhouse'), 'windtower': kind('windtower'), 'gate': kind('gate'),
              'harbour': kind('harbour'), 'deadroad': kind('deadroad'), 'deserted': kind('deserted'),
              'hermitage': kind('hermitage'), 'river': kind('oldbridge'),
              'road': [('poi', q.id) for q in world.pois if q.kind == 'leaguestone'],
              'library': [('library', None)],
              'mine': [('dungeon', s.below) for s in cities]}
    for bk in chosen:
        b = T.BOOK[bk]
        used = set()
        for n in range(len(b['pages'])):
            tags = list(b['where'])
            random.shuffle(tags)
            cands = [c for t in tags for c in places.get(t, ())]
            spot = next((c for c in cands if c not in used or c == ('library', None)), None) or \
                (cands[0] if cands else None) or (random.choice(places['vcity']) if places['vcity'] else None) \
                or ('library', None)
            used.add(spot)
            V['pages'][(bk, n)] = spot
    # where each riddle fragment comes from in this world: what is not here, the libraries know
    have = {s.kind for s in sites} | {getattr(s, 'deep', None) for s in sites}
    for r in T.RIDDLES:
        for i, (_text, src, _f) in enumerate(r['frags']):
            if src.startswith('page:'):
                _p, bk, n = src.split(':')
                eff = src if bk in chosen and int(n) < len(T.BOOK[bk]['pages']) else 'library'
            elif src.startswith('place:'):
                eff = src if src[6:] in have else 'library'
            else:
                eff = src
            V['src'][(r['key'], i)] = eff


# ------------------------------------------------------------------ the zones: ruins between the trees
def paint(game, t, cx0, cy0, nx, ny, ox, oy):
    """Lay the Varnish ruins over the land of the zones being made (zones.make)."""
    V = info(game)
    if not V:
        return
    from .zones import ZW, ZH, h2, salt, mid
    s = salt(game)
    H, W = t.shape
    soft = {GRASS, TREE, SAND, D.SLOPE, D.SWAMP, D.SNOW, D.BAREROCK, D.GRIT, D.DRIFT, D.FIELD}
    om = game.maps['over']
    wall = set(V.get('wall', ()))

    def put(x, y, tile):
        if 0 <= x < W and 0 <= y < H and int(t[y, x]) in soft:
            t[y, x] = tile
    for cy in range(cy0, cy0 + ny):
        for cx in range(cx0, cx0 + nx):
            x0, y0 = (cx - cx0) * ZW, (cy - cy0) * ZH
            sid = V['ruin'].get((cx, cy))
            if sid is not None:
                site = game.world.sites[sid]
                r = random.Random(game.seed * 7919 + cx * 131 + cy * 17)
                buried = {'sand': .45, 'marsh': .3, 'ice': .25}.get(site.land, .1)
                cover = {'sand': SAND, 'marsh': SHALLOW, 'ice': D.SNOW}.get(site.land, TREE)
                centre = (cx, cy) == (site.x, site.y)
                for gy in range(y0 + 4, y0 + ZH - 3, 11):           # the old streets, in a grid
                    for x in range(x0 + 2, x0 + ZW - 2):
                        if r.random() > buried:
                            put(x, gy, D.VPAVE)
                        if (x - x0) % 6 == 0 and r.random() < .55:
                            put(x, gy - 1, D.COLUMN if r.random() > buried else cover)
                for gx in range(x0 + 6, x0 + ZW - 4, 16):
                    for y in range(y0 + 2, y0 + ZH - 2):
                        if r.random() > buried:
                            put(gx, y, D.VPAVE)
                for _ in range(2 if centre else 5):                 # houses without roofs
                    hx, hy = r.randint(x0 + 4, x0 + ZW - 14), r.randint(y0 + 4, y0 + ZH - 10)
                    hw, hh = r.randint(5, 9), r.randint(4, 6)
                    for y in range(hy, hy + hh):
                        for x in range(hx, hx + hw):
                            if y in (hy, hy + hh - 1) or x in (hx, hx + hw - 1):
                                put(x, y, (WALL if r.random() < .6 else RUBBLE) if r.random() > buried else cover)
                if not centre and h2(cx, cy, s + 71) < .35:          # a gate with no wall
                    gx, gy = x0 + r.randint(10, ZW - 12), y0 + r.randint(8, ZH - 10)
                    put(gx, gy, D.IRONGATE)
                    put(gx + 3, gy, D.IRONGATE)
                if not centre and h2(cx, cy, s + 73) < .5:           # a stone with the city's name
                    put(x0 + r.randint(8, ZW - 8), y0 + r.randint(6, ZH - 6), D.VSTONE)
            elif cy * om.w + cx in wall:                               # the Northern Wall
                r = random.Random(game.seed * 3571 + cx * 97 + cy * 13)
                ay = ZH // 2 + r.randint(-2, 2)
                for x in range(x0, x0 + ZW):
                    ay = max(4, min(ZH - 5, ay + (r.random() < .1) - (r.random() < .1)))
                    for k in (0, 1):
                        if r.random() < .82:
                            put(x, y0 + ay + k, D.VWALL if r.random() < .8 else RUBBLE)
    for cy in range(cy0, cy0 + ny):                                     # the places' own cells: a column or two
        for cx in range(cx0, cx0 + nx):
            got = None
            for q in _place_at(game, cx, cy):
                got = q
            if got is None:
                continue
            mx, my = mid(cx, cy, s)
            r = random.Random(game.seed * 113 + cx * 7 + cy)
            for _ in range(6):
                put(mx - ox + r.randint(-9, 9), my - oy + r.choice((-4, -3, 3, 4)), D.COLUMN)



def _place_at(game, cx, cy):
    cache = getattr(game, '_vn_at', None)
    if cache is None or cache[0] != len(game.world.sites):
        out = {}
        for s in game.world.sites:
            if s.kind in PLACE_KINDS or s.kind == 'vdeep':
                out[(s.x, s.y)] = s
        game._vn_at = cache = (len(game.world.sites), out)
    s = cache[1].get((cx, cy))
    return [s] if s else []


def zone_step(game):
    """Walking the zones: a ruin you see is a ruin you have found."""
    from . import zones as ZN
    from . import folk as FK
    m, p = game.map, game.player
    V = info(game)
    if not V:
        return
    cell = ZN.cell_of(m, p.x, p.y)
    sid = V['ruin'].get(cell)
    if sid is not None and FK.unfound(game.world.sites[sid]):
        near = any(m.tile(p.x + a, p.y + b) in (D.COLUMN, D.VPAVE, D.IRONGATE, D.VSTONE, WALL, RUBBLE)
                   for a in range(-6, 7) for b in range(-4, 5) if m.inb(p.x + a, p.y + b))
        if near:
            site = game.world.sites[sid]
            discover(game, site, {'sand': 'Columns stand up out of the sand, in rows.',
                                  'marsh': 'Columns stand in the reeds, in rows, and a paved street runs under the '
                                           'water.',
                                  'ice': 'Columns stand in the snow, in rows, rimed white.'}.get(
                site.land, 'Between the trees stand columns, in rows, and old paving under the moss.'))
    for s in _place_at(game, *cell):
        if FK.unfound(s):
            mx, my = ZN.local_mid(game, m)
            if cheb(p.x, p.y, mx, my) <= 10:
                discover(game, s, 'Old stone shows through the grass ahead.')


def over_step(game):
    """On the world map: step into a ruin's cells, or beside a Varnish place."""
    from . import folk as FK
    p = game.player
    V = info(game)
    if not V:
        return
    sid = V['ruin'].get((p.x, p.y))
    if sid is not None and FK.unfound(game.world.sites[sid]):
        discover(game, game.world.sites[sid], 'Columns stand among the trees here, in rows.')
    for s in game.world.sites:
        if (s.kind in PLACE_KINDS or s.kind == 'vdeep') and FK.unfound(s) and cheb(s.x, s.y, p.x, p.y) <= 1:
            discover(game, s, 'Old stone shows through the grass ahead.')


def discover(game, site, how):
    from . import folk as FK
    from . import chronicle as CH
    FK.discover(game, site, how)
    xp = 6 + game.world.danger_at(site.x, site.y) * 2
    game.gain_xp(xp) if hasattr(game, 'gain_xp') else None
    CH.add(game, 'Places', f'{site.name}: {DESC[site.kind]}', 'seen', where='with your own eyes', place=(site.x, site.y),
           key=f'vn:{site.id}', quiet=True)


def name_city(game, site):
    """A stone with the letters says the city's name."""
    if site.named:
        return False
    site.named = True
    site.name = site.vname
    dg = game.world.dungeons.get(getattr(site, 'below', None))
    if dg:
        dg.name = f'Beneath {site.vname}'
    from . import chronicle as CH
    CH.add(game, 'Places', f'The ruin is {site.vname}, a city of the Varnish.', 'read', who='a stone with old letters',
           place=(site.x, site.y), key=f'vn:{site.id}', title=site.vname)
    return True


# ------------------------------------------------------------------ the play maps
def site_map(game, site):
    state = random.getstate()
    random.seed(game.seed * 4099 + site.x * 991 + site.y * 41 + 7)
    try:
        m = BUILD[site.kind](game, site)
    finally:
        random.setstate(state)
    return m


def _base(game, site, w, h, ground=GRASS):
    from .entities import GameMap
    m = GameMap(site.map_key, 'town', site.name, w, h, ground)
    m.glows, m.lights = [], []
    m.radius, m.sid, m.hid, m.signs = 60, None, None, []
    m.site = site.id
    m.vn = site.kind
    m.vthings = {}
    m.level = game.world.danger_at(site.x, site.y) + 1
    return m


def _ground(m, land):
    for i in range(len(m.t)):
        r = random.random()
        if land == 'sand':
            m.t[i] = SAND if r > .02 else D.ROCK
        elif land == 'marsh':
            m.t[i] = SHALLOW if r < .22 else D.SWAMP if r < .3 else GRASS if r > .04 else TREE
        elif land == 'ice':
            m.t[i] = D.SNOW if r > .03 else D.DRIFT
        else:
            m.t[i] = TREE if r < .14 else GRASS


def _done(m, entry):
    from . import oldplaces as OP
    m.entry = entry
    start = (entry[0] + 1, entry[1])
    m.set(*start, m.tile(*start) if D.TILES[m.tile(*start)].walk else D.PATH)
    got = OP._reach(m, start)
    for i, t in enumerate(m.t):
        x, y = i % m.w, i // m.w
        if (t not in BUMP and t not in (D.LEVER, DOWN)) or t == D.SKYWELL or underwater(m, x, y):
            continue                            # (the sky well is walked round; the drowned hall waits for its sluice)
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
            tt = m.tile(cx, cy)
            if tt not in BUMP and tt not in (D.LEVER, DOWN) and not D.TILES[tt].walk:
                m.set(cx, cy, SHALLOW if tt == WATER else D.VPAVE)
        got = OP._reach(m, start)
    for i in range(len(m.seen)):
        m.seen[i] = 1
    m.lights = list(m.glows)
    return m


def _spot(m, xs, ys, tiles=None):
    for _ in range(300):
        x, y = random.randint(*xs), random.randint(*ys)
        if m.inb(x, y) and (D.TILES[m.tile(x, y)].walk if tiles is None else m.tile(x, y) in tiles) and not m.mon_at(x, y):
            return x, y
    return None


def _ruin_walls(m, x0, y0, x1, y1, keep=.7, door=None):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if y in (y0, y1) or x in (x0, x1):
                m.set(x, y, D.VWALL if random.random() < keep else RUBBLE)
            else:
                m.set(x, y, D.VPAVE if random.random() < .7 else GRASS if m.tile(x, y) == GRASS else D.VPAVE)
    if door:
        m.set(*door, D.VPAVE)


def _city(game, site):
    w, h = 76, 46
    m = _base(game, site, w, h)
    _ground(m, site.land)
    cx, cy = w // 2 + 4, h // 2
    for y in range(h):                                     # the court and its streets
        for x in range(w):
            d = ((x - cx) / 1.0) ** 2 + ((y - cy) * 1.7) ** 2
            if d <= 16 ** 2 and random.random() < .9:
                m.set(x, y, D.VPAVE)
            if d <= 5 ** 2:
                m.set(x, y, D.SKYWELL)
    for y in range(h):
        for x in range(w):
            d = ((x - cx) ** 2 + ((y - cy) * 1.7) ** 2) ** .5
            if 15.5 <= d <= 16.5 and (x + y) % 3 == 0:
                m.set(x, y, D.COLUMN if random.random() < .8 else RUBBLE)
    for x in range(0, w):
        if random.random() < .85:
            m.set(x, cy, D.VPAVE if m.tile(x, cy) != D.SKYWELL else D.SKYWELL)
    for y in range(0, h):
        if random.random() < .85 and m.tile(cx, y) != D.SKYWELL:
            m.set(cx, y, D.VPAVE)
    for _ in range(7):                                      # houses round the court
        for _t in range(40):
            hw, hh = random.randint(6, 10), random.randint(4, 7)
            x0, y0 = random.randint(2, w - hw - 3), random.randint(2, h - hh - 3)
            if all(((x - cx) ** 2 + ((y - cy) * 1.7) ** 2) ** .5 > 18 for x in (x0, x0 + hw) for y in (y0, y0 + hh)) \
                    and not any(m.tile(x, y) in (D.VWALL, D.SKYWELL) for x in range(x0, x0 + hw + 1)
                                for y in range(y0, y0 + hh + 1)):
                _ruin_walls(m, x0, y0, x0 + hw, y0 + hh, .65, (x0 + hw // 2, y0 + hh))
                break
    m.set(4, cy - 2, D.IRONGATE)                            # the gate you come in by, with no wall
    m.set(4, cy + 2, D.IRONGATE)
    stones = []
    for _ in range(3):
        sp = _spot(m, (cx - 14, cx + 14), (cy - 9, cy + 9), (D.VPAVE,))
        if sp:
            m.set(*sp, D.VSTONE)
            stones.append(sp)
    if stones:
        m.vthings[stones[0]] = 'name'
    way = site.way
    m.way = None
    if way == 'stone' and len(stones) > 1:
        m.vthings[stones[1]] = 'way'
        m.way = stones[1]
    elif way == 'air':
        sp = _spot(m, (cx - 14, cx + 14), (cy - 9, cy + 9), (D.VPAVE,))
        if sp:
            m.set(*sp, D.AIRWELL)
            m.way = sp
    elif way == 'hollow':
        sp = _spot(m, (cx - 12, cx + 12), (cy - 8, cy + 8), (D.VPAVE,))
        if sp:
            m.set(*sp, D.HOLLOW)
            m.way = sp
    if m.way is None:                                       # a lever behind a statue
        site.way = 'lever'
        sp = _spot(m, (cx + 8, cx + 14), (cy - 6, cy + 6), (D.VPAVE,))
        sp = sp or (cx + 10, cy + 3)
        m.set(*sp, D.STATUE)
        m.set(sp[0] + 1, sp[1], D.LEVER)
        m.vthings[(sp[0] + 1, sp[1])] = 'lever'
        m.way = (sp[0] - 2, sp[1])
    if site.open:
        _open_way(m, site)
    return _done(m, (0, cy))


def _open_way(m, site):
    x, y = m.way
    if site.way in ('stone', 'lever'):
        spot = next(((x + a, y + b) for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1))
                     if m.inb(x + a, y + b) and D.TILES[m.tile(x + a, y + b)].walk), (x, y + 1))
        if site.way == 'lever':
            spot = (x, y)
        m.set(*spot, DOWN)
    else:
        m.set(x, y, DOWN)


def _walltower(game, site):
    w, h = 64, 38
    m = _base(game, site, w, h)
    _ground(m, 'ice' if site.y < game.maps['over'].h * .12 else 'overgrown')
    wy = h // 2
    for x in range(w):
        for k in (0, 1):
            if random.random() < .85:
                m.set(x, wy + k, D.VWALL if random.random() < .8 else RUBBLE)
    tx, ty = w // 2, wy - 4
    _ruin_walls(m, tx - 5, ty - 4, tx + 5, wy + 1, .8, (tx, wy + 1))
    for y in range(ty - 3, wy + 1):
        for x in range(tx - 4, tx + 5):
            m.set(x, y, D.VPAVE)
    m.set(tx, wy + 1, D.VPAVE)
    m.set(tx, wy, D.VPAVE)
    for x in (tx - 5, tx + 5):
        m.set(x, ty - 1, D.DAYMARKS)
    m.vthings[(tx - 5, ty - 1)] = 'days'
    m.set(tx + 2, ty - 2, D.VSTONE)
    if site.lamp:
        m.set(tx - 2, ty - 3, D.LITLAMP if getattr(site, 'lit', False) else D.VLAMP)
    for x in range(w):                                      # a trodden way along the south of the wall
        if m.tile(x, wy + 4) in (GRASS, TREE, D.SNOW, D.DRIFT):
            m.set(x, wy + 4, D.PATH)
    return _done(m, (0, wy + 4))


def _windtower(game, site):
    w, h = 56, 36
    m = _base(game, site, w, h)
    _ground(m, 'overgrown')
    for i in range(len(m.t)):
        if random.random() < .08:
            m.t[i] = D.ROCK
    cx, cy = w // 2, h // 2
    for y in range(h):
        for x in range(w):
            d = ((x - cx) ** 2 + ((y - cy) * 1.6) ** 2) ** .5
            if 5.5 <= d <= 6.6:
                m.set(x, y, D.VWALL if random.random() < .85 else RUBBLE)
            elif d < 5.5:
                m.set(x, y, D.VPAVE)
    m.set(cx - 6, cy, D.VPAVE)
    m.set(cx, cy, D.VSTONE)
    m.vthings[(cx, cy)] = 'place'
    m.set(cx + 3, cy - 1, D.AIRWELL)
    m.vthings[(cx + 3, cy - 1)] = 'look'
    return _done(m, (0, cy))


def _deadroad(game, site):
    w, h = 72, 30
    m = _base(game, site, w, h)
    _ground(m, 'overgrown')
    cy = h // 2
    for x in range(w):
        for y in (cy - 1, cy, cy + 1):
            m.set(x, y, D.VPAVE)
        for y in (cy - 3, cy - 2, cy + 2, cy + 3):
            m.set(x, y, D.VWALL)
    for x in range(6, w - 4, 3):
        for y in (cy - 2, cy + 2):
            m.set(x, y, D.NICHE if random.random() < .8 else D.OPENNICHE)
    first = next((x for x in range(6, w) if m.tile(x, cy - 2) == D.NICHE), 6)
    m.vthings[(first, cy - 2)] = 'place'
    m.set(w // 2, cy - 2, D.VSTONE)
    return _done(m, (0, cy))


def _forge(game, site):
    w, h = 60, 36
    m = _base(game, site, w, h)
    _ground(m, 'overgrown')
    for i in range(len(m.t)):
        if random.random() < .06:
            m.t[i] = D.SLAG
    cx, cy = w // 2, h // 2
    _ruin_walls(m, cx - 10, cy - 6, cx + 10, cy + 6, .6, (cx - 10, cy))
    m.set(cx, cy, D.VANVIL)
    m.vthings[(cx, cy)] = 'place'
    m.set(cx + 4, cy - 2, D.VANVIL)
    for k in range(2):
        sp = _spot(m, (cx - 8, cx + 8), (cy - 4, cy + 4), (D.VPAVE, GRASS))
        if sp:
            m.set(*sp, D.STARIRON)
    m.set(cx - 5, cy + 3, D.VSTONE)
    return _done(m, (0, cy))


def _gate(game, site):
    w, h = 56, 34
    m = _base(game, site, w, h)
    _ground(m, 'overgrown')
    cx, cy = w // 2, h // 2
    for y in range(cy - 4, cy + 5):
        for x in range(cx - 7, cx + 8):
            m.set(x, y, D.VPAVE)
    for y in range(cy - 2, cy + 3):
        m.set(cx - 2, y, D.IRONGATE)
        m.set(cx + 2, y, D.IRONGATE)
    m.set(cx - 5, cy, D.STARMAP)
    m.vthings[(cx - 5, cy)] = 'map'
    m.set(cx + 5, cy + 3, D.VSTONE)
    for x in range(0, cx - 7):
        m.set(x, cy, D.VPAVE)
    for x in range(cx + 8, w):
        m.set(x, cy, D.VPAVE)
    return _done(m, (0, cy))


def _sluice(game, site):
    w, h = 60, 36
    m = _base(game, site, w, h)
    _ground(m, 'overgrown')
    x0, y0, x1, y1 = 14, 6, 50, 28
    _ruin_walls(m, x0, y0, x1, y1, .9, (x0, (y0 + y1) // 2))
    for y in range(y0 + 1, y1):
        for x in range(x0 + 1, x1):
            m.set(x, y, WATER if x > x0 + 8 else D.VPAVE)
    for y in range(y0 + 1, y1):
        m.set(x0 + 8, y, D.VWALL)
    my = (y0 + y1) // 2
    m.set(x0 + 8, my, D.SLUICE)
    m.vthings[(x0 + 8, my)] = 'sluice'
    m.set(x1 - 4, my, D.VSTONE)                            # under water until the hall runs dry
    m.vthings[(x1 - 4, my)] = 'place'
    m.flooded = not getattr(site, 'drained', False)
    if not m.flooded:
        drain(m)
    return _done(m, (0, my))


def underwater(m, x, y):
    return getattr(m, 'flooded', False) and any(m.inb(x + a, y + b) and m.tile(x + a, y + b) == WATER
                                                for a in (-1, 0, 1) for b in (-1, 0, 1))


def drain(m):
    for i, t in enumerate(m.t):
        if t == WATER:
            m.t[i] = D.VPAVE if random.random() < .85 else SHALLOW
    for (x, y), what in list(m.vthings.items()):
        if what == 'sluice':
            m.set(x, y, D.OPENSLUICE)
    m.flooded = False


def _fallensky(game, site):
    w, h = 64, 40
    m = _base(game, site, w, h, D.GLASSSAND)
    cx, cy = w // 2 + 4, h // 2
    for i in range(len(m.t)):
        x, y = i % w, i // w
        d = ((x - cx) ** 2 + ((y - cy) * 1.6) ** 2) ** .5
        if d > 22:
            m.t[i] = GRASS if random.random() > .08 else TREE
        elif random.random() < .05:
            m.t[i] = D.BLACKSTONE
    for k in range(-4, 5):
        m.set(cx + k, cy + (k // 3), D.CHAINLINK if k in (-4, 4) else D.BLACKSTONE if k == 0 else D.GLASSSAND)
    m.vthings[(cx - 4, cy - 2)] = 'place'
    m.vthings[(cx + 4, cy + 1)] = 'place'
    return _done(m, (0, cy))


def _starhouse(game, site):
    w, h = 56, 34
    m = _base(game, site, w, h)
    _ground(m, 'overgrown')
    x0, y0, x1, y1 = 12, 6, 44, 27
    _ruin_walls(m, x0, y0, x1, y1, .9, (x0, (y0 + y1) // 2))
    for y in range(y0 + 1, y1):
        for x in range(x0 + 1, x1):
            m.set(x, y, D.DUST)
    m.set(x1 - 2, y0 + 2, D.VSTONE)
    m.dust = sum(1 for t in m.t if t == D.DUST)
    if getattr(site, 'swept', False):
        for i, t in enumerate(m.t):
            if t == D.DUST:
                m.t[i] = D.STARFLOOR
    return _done(m, (0, (y0 + y1) // 2))


def _harbour(game, site):
    w, h = 64, 38
    m = _base(game, site, w, h, SAND)
    for i in range(len(m.t)):
        x, y = i % w, i // w
        if x > 30:
            m.t[i] = SHALLOW if x < 46 else WATER
    for y in range(4, h - 4, 4):
        for x in range(32, 50, 5):
            m.set(x, y, D.COLUMN)
    for x in range(20, 44):
        m.set(x, h // 2, D.VPAVE if x < 31 else SHALLOW)
    m.set(26, h // 2 - 2, D.VSTONE)
    return _done(m, (0, h // 2))


def _deep(game, site):
    w, h = 50, 30
    m = _base(game, site, w, h)
    _ground(m, 'overgrown' if site.deep != 'anchor' else 'sand')
    cx, cy = w // 2, h // 2
    _ruin_walls(m, cx - 8, cy - 5, cx + 8, cy + 5, .9, (cx - 8, cy))
    m.set(cx + 4, cy, DOWN)
    m.set(cx, cy - 3, D.VSTONE)
    if site.deep == 'pits':
        m.set(cx - 3, cy + 3, D.CHAINLINK)
        m.vthings[(cx - 3, cy + 3)] = 'place'
    if site.deep == 'anchor':                              # the gardener's apple tree, on its ledge
        for x in range(w - 9, w - 3):
            for y in range(2, 6):
                m.set(x, y, D.ROCK if y == 5 or x == w - 9 else GRASS)
        m.set(w - 6, 3, TREE)
        m.set(w - 9, 4, GRASS)
        m.vthings[(w - 6, 3)] = 'apple'
    return _done(m, (0, cy))


BUILD = {'vcity': _city, 'walltower': _walltower, 'windtower': _windtower, 'deadroad': _deadroad, 'forge': _forge,
         'gate': _gate, 'sluice': _sluice, 'fallensky': _fallensky, 'starhouse': _starhouse, 'harbour': _harbour,
         'vdeep': _deep}


# ------------------------------------------------------------------ being there
def on_enter(game, site, m):
    """Coming to any place: pages lie where they lie; at a Varnish place, a line on what you see."""
    put_pages(game, ('site', site.id), m)
    if not is_varnish(site):
        return
    k = site.kind
    line = {'vcity': 'Columns round a sunken court, and in the middle a round well open to the sky, so deep you see no '
                     'bottom.',
            'walltower': 'A broken tower on a broken wall. The north is very empty from up here.',
            'windtower': 'A round tower with no roof. The wind goes round inside it.',
            'deadroad': 'A paved road between two walls cut with niches. In every niche someone stands.',
            'forge': 'Slag heaps, and black anvils without a speck of rust.',
            'gate': 'An arch of black iron stands on its own, with no wall on either side of it.',
            'sluice': 'A long hall of the Varnish, half of it under still water.',
            'fallensky': 'The ground is glass here, green and cracked, and black stones lie about as if thrown.',
            'starhouse': 'A long house without a roof. Dust lies on the floor like grey snow.',
            'harbour': 'Column stumps stand in the shallows in rows, where the quays were.',
            'vdeep': 'This is the place. A stair goes down into the dark.'}[k]
    if k == 'windtower':
        from . import weather as WX
        if WX.current(game) in ('storm', 'downpour', 'blizzard', 'haboob', 'sandstorm'):
            line = 'The tower howls in the storm, a long low note that you feel in your teeth.'
    if k == 'sluice' and getattr(m, 'flooded', False):
        line += ' A sluice gate of iron stands shut in the dividing wall.'
    game.msg(line, 'info')
    if k == 'windtower' and not getattr(site, 'looked', False):
        look_out(game, site, 12)


def look_out(game, site, r):
    """From the top of the tower: the land round, and the old places in it."""
    from . import folk as FK
    om = game.maps['over']
    site.looked = True
    for y in range(site.y - r, site.y + r + 1):
        for x in range(site.x - r, site.x + r + 1):
            if om.inb(x, y) and (x - site.x) ** 2 + ((y - site.y) * 1.4) ** 2 <= r * r:
                om.seen[y * om.w + x] = 1
    for s in game.world.sites:
        if is_varnish(s) and FK.unfound(s) and cheb(s.x, s.y, site.x, site.y) <= r:
            FK.discover(game, s, None)
    game.msg('From the top of the broken wall you see the land for miles round, and the old stones in it. You put it '
             'all on your map.', 'good')


def put_pages(game, loc, m, spot=None):
    """Lay the pages that lie here (once; a page you took is gone)."""
    V = info(game)
    if not V:
        return
    have = st(game)['pages']
    on = {getattr(i, 'vpage', None) for i in m.items}
    from .entities import Item
    for key, where in V['pages'].items():
        if where != loc or key in have or key in on:
            continue
        sp = spot or _spot(m, (2, m.w - 3), (2, m.h - 3))
        if not sp:
            continue
        it = Item(game.new_id(), 'vpage', 'vpage')
        it.vpage = key
        it.x, it.y = sp
        m.items.append(it)


def on_level(game, m, dg, depth):
    """A new level of a dungeon: pages that lie in it; at the bottom of a Varnish deep, its treasure room."""
    want = 1 if getattr(dg, 'mine', None) is not None else dg.depth
    if depth == want:
        put_pages(game, ('dungeon', dg.id), m)
    if not getattr(dg, 'vn', None) or depth != dg.depth:
        return
    from . import worldgen as W
    up = m.t.index(UP) if UP in m.t else 0
    ux, uy = up % m.w, up // m.w
    far = [i for i, t in enumerate(m.t) if t == FLOOR and cheb(i % m.w, i // m.w, ux, uy) > 12]
    if far:
        i = random.choice(far)
        m.set(i % m.w, i // m.w, D.STARIRON)
    c = W.rand_free(game, m, lambda t: t == FLOOR)
    if c:
        m.set(c[0], c[1], D.VSTONE)


def stairs(game, t, d):
    """Down from a Varnish place into what lies under it."""
    m = game.map
    if not getattr(m, 'vn', None) or t != DOWN or d == 'up':
        return None
    site = game.world.sites[m.site]
    if not getattr(site, 'below', None):
        return None
    game.enter_dungeon(site.below, 1, 'up')
    return 1


def on_step(game):
    """At a star house your feet sweep the dust off an iron floor."""
    m, p = game.map, game.player
    if getattr(m, 'vn', None) != 'starhouse':
        return
    swept = False
    for a in (-1, 0, 1):
        for b in (-1, 0, 1):
            if m.inb(p.x + a, p.y + b) and m.tile(p.x + a, p.y + b) == D.DUST:
                m.set(p.x + a, p.y + b, D.STARFLOOR)
                swept = True
    if not swept:
        return
    site = game.world.sites[m.site]
    left = sum(1 for t in m.t if t == D.DUST)
    if not getattr(site, 'saw_floor', False):
        site.saw_floor = True
        game.msg('Under the dust the floor is iron, cut with stars.', 'info')
    if left <= getattr(m, 'dust', 1) * .3 and not getattr(site, 'swept', False):
        site.swept = True
        game.msg('With the dust gone you can see it: the whole sky, in iron, as the Varnish knew it. Some of the stars '
                 'have been hammered out and filled with lead.', 'unique')
        place_frag(game, 'starhouse', site.name)


# ------------------------------------------------------------------ the telling things
def bump(game, x, y):
    """Walking into a Varnish thing. Returns the turns it took, or None."""
    m = game.map
    t = m.tile(x, y)
    if getattr(m, 'vn', None) and m.vthings.get((x, y)) == 'apple':
        return apple(game)
    if t == D.LEVER and getattr(m, 'vn', None) and m.vthings.get((x, y)) == 'lever':
        return open_way(game, 'The lever behind the statue moves, stiffly. Stone grinds under the court, and a stair '
                              'opens in the floor.')
    if t not in BUMP:
        return None
    vt = getattr(m, 'vthings', {}).get((x, y))
    site = game.world.sites[m.site] if getattr(m, 'vn', None) else None
    where = site.name if site else game.map.name
    if t == D.VSTONE:
        return read_vstone(game, x, y, vt, site)
    if t == D.SKYWELL:
        game.msg('The sky well goes down and down. Far below, a star shows in water, or something like a star.', 'info')
        return 0
    if t == D.AIRWELL:
        if vt == 'look':
            if site and not getattr(site, 'looked', False):
                look_out(game, site, 12)
                return 10
            game.msg('Cold air comes up out of the shaft. From the top of the wall the land lies spread out, as '
                     'before.')
            return 0
        return open_way(game, 'Cold air rises out of the well, smelling of stone and old water. Iron rungs go down '
                              'the shaft. It is not a well.')
    if t == D.HOLLOW:
        return open_way(game, 'The flagstone sounds hollow under your heel. You lever it up: steps go down into the '
                              'dark.')
    if t == D.NICHE:
        game.request = None
        from . import events as EV
        EV.ask(game, 'varnish', 'A niche with a standing dead',
               'Someone stands in the niche, upright, dry as leather, a seal of black iron on the chest. Small letters '
               'run round the seal.', [('Read the seal', 'seal'), ('Break the seal', 'break'), ('Leave it', 'bye')],
               x=x, y=y, place=bool(vt == 'place'))
        return 0
    if t == D.OPENNICHE:
        game.msg('An empty niche. Whoever stood here is gone, or is lying in pieces at your feet.')
        return 0
    if t == D.VANVIL:
        if vt == 'place':
            if not place_frag(game, 'forge', where):
                game.msg('A black anvil, not a speck of rust on it. Letters on the side say what it was for, and you '
                         'have read them.')
            return 5
        game.msg('An anvil of star-iron. You can still see your face in it.')
        return 0
    if t == D.STARIRON:
        from .nature import curio
        if game.add_to_inv(curio(game, 'stariron')):
            m.set(x, y, D.SLAG if getattr(m, 'vn', None) else FLOOR)
            game.msg('You break a shard off the lump of star-iron. It is cold, and heavier than it looks, and it '
                     'shines.', 'gold')
            return 10
        game.msg('Your bag is full.', 'bad')
        return 0
    if t == D.STARMAP:
        return star_map(game, site)
    if t == D.SLUICE:
        if not getattr(m, 'flooded', False):
            return 0
        drain(m)
        if site:
            site.drained = True
        put_pages(game, ('site', site.id) if site else None, m)
        game.msg('You heave the wheel round. Iron groans, the sluice lifts, and the water of the hall runs out under '
                 'your feet with a long sigh. Whatever lay under it lies in the open now.', 'unique')
        place_frag(game, 'sluice', where)
        from .nature import curio
        for _ in range(random.randint(2, 3)):
            sp = _spot(m, (28, 48), (8, 26), (D.VPAVE,))
            if sp:
                it = curio(game, 'oldcoin')
                it.x, it.y = sp
                m.items.append(it)
        return 20
    if t == D.CHAINLINK:
        if vt == 'place' and place_frag(game, 'pits' if site and site.kind == 'vdeep' else 'fallensky', where):
            return 5
        game.msg('A link of a chain of star-iron, as thick as a man. It is snapped through.')
        return 0
    if t == D.BLACKSTONE:
        game.msg('A black stone, smooth and heavier than any stone should be. It is warm on the side that faces the '
                 'sky.')
        return 0
    if t == D.DAYMARKS:
        game.msg('The stone is scratched with days in fives, thousands of them, row on row. At the end of the last row '
                 'someone has written a name, and the numbers 3,651.', 'info')
        return 0
    if t == D.VLAMP:
        from . import towns as TD
        if not TD.is_night(game):
            game.msg('An iron lantern on the parapet, cold. Rags and lard are still in it. It would want lighting at '
                     'night.')
            return 0
        return light_lamp(game, x, y, site)
    if t == D.LITLAMP:
        game.msg('The lantern burns on the wall, as it did the last night. Far along the wall, a spark answers.')
        return 0
    return None


def apple(game):
    """The gardener's tree: one apple a year for who has read her book."""
    from .calendar import _split
    s = st(game)
    year = _split(game.day)[0]
    if not s.get('apple'):
        game.msg('A very old apple tree on a ledge, bent by the sea wind. Somebody planted it a long way from home.')
        return 0
    if s.get('apple_year') == year:
        game.msg('The old apple tree has given its one apple this year.')
        return 0
    from .entities import Item
    it = Item(game.new_id(), 'food', 'apple')
    if not game.add_to_inv(it):
        game.msg('Your bag is full.', 'bad')
        return 0
    s['apple_year'] = year
    game.msg('The gardener\'s tree has one apple on it, red, and it comes off in your hand. It has flowered.', 'unique')
    from . import chronicle as CH
    CH.add(game, 'The Varnish', 'You picked the one apple of the year from the gardener\'s tree below the Sky-Seat.',
           'seen', where=game.map.name, key=f'vapple:{year}', quiet=True)['head'] = 'Bound books'
    return 5


def open_way(game, text):
    m = game.map
    site = game.world.sites[m.site]
    if site.open:
        game.msg('The way down is open.')
        return 0
    site.open = True
    _open_way(m, site)
    game.msg(text, 'unique')
    from . import chronicle as CH
    CH.add(game, 'Places', f'Under {site.name} lies a way down that no map shows.', 'seen', where=site.name,
           place=(site.x, site.y), key=f'vway:{site.id}', title=f'Beneath {site.name}')
    return 10


def read_vstone(game, x, y, vt, site):
    """A stone with the old letters: the city's name, the way in, a piece of a riddle or of the empire."""
    m = game.map
    key = f'{m.key}:{x}:{y}' if getattr(m, 'zone', None) is None else f'zone:{m.org[0] + x}:{m.org[1] + y}'
    if not letters(game):
        game.msg('The stone is cut with old letters you cannot read: Varnish. A scribe in a city library could teach '
                 'you them.', 'info')
        return 0
    s = st(game)
    if getattr(m, 'zone', None) is not None:                   # a city's name stone out in the ruins
        from . import zones as ZN
        sid = info(game)['ruin'].get(ZN.cell_of(m, x, y))
        if sid is not None:
            city = game.world.sites[sid]
            if name_city(game, city):
                discover(game, city, None) if not city.found else None
                game.msg(f'The old letters say: "Here begins {city.vname}. Count your steps." It is on your map now.',
                         'unique')
                return 5
            game.msg(f'The old letters say: "Here begins {city.vname}. Count your steps."')
            return 0
    if vt == 'name' and site and site.kind == 'vcity':
        if name_city(game, site):
            game.map.name = site.name
            game.msg(f'The old letters say: "{site.vname}. The sky is near." You know the city\'s name now.', 'unique')
            return 5
    if vt == 'way' and site and site.kind == 'vcity' and not site.open:
        return open_way(game, 'The letters say: "Count three from the stone toward the well, and ask." You press where '
                              'they say. A flagstone sinks, and a stair goes down.')
    if vt == 'place' and site:
        if place_frag(game, 'windtower' if site.kind == 'windtower' else 'sluice' if site.kind == 'sluice' else
                      site.kind, site.name):
            return 5
    if key in s['stones']:
        game.msg('You have read this stone.')
        return 0
    s['stones'].add(key)
    where = site.name if site else m.name
    if give_riddle(game, 'stone', 'a stone with old letters', where):
        return 5
    heads = {'walltower': ('Soldiers and the wall', 'The last days'), 'deadroad': ('The bound dead', 'Law and measure'),
             'forge': ('Mages and the binding', 'Trades and the sea'), 'harbour': ('Trades and the sea',),
             'starhouse': ('Why it fell', 'Mages and the binding'), 'gate': ('Law and measure', 'The emperors')}
    got = give_lore(game, 'read', 'a stone with old letters', where,
                    heads.get(site.kind if site else '', None))
    if got:
        game.msg(f'You read the stone. {got}', 'info')
        return 5
    game.msg('The stone says what other stones have said.')
    return 0


def r_varnish(game, choice, ctx):
    m = game.map
    x, y = ctx.get('x'), ctx.get('y')
    if choice == 'seal':
        if not letters(game):
            game.msg('The letters round the seal are Varnish. You cannot read them.', 'info')
            return
        site = game.world.sites[m.site]
        if ctx.get('place') and place_frag(game, 'deadroad', site.name):
            return
        game.msg('Round the seal: a name, a sum of money, and a number of years. The years have long run out. The dead '
                 'one stands anyway.', 'info')
    elif choice == 'break':
        from .entities import make_monster
        m.set(x, y, D.OPENNICHE)
        spot = next(((x + a, y + b) for a, b in ((0, 1), (0, -1), (1, 0), (-1, 0)) if m.inb(x + a, y + b)
                     and D.TILES[m.tile(x + a, y + b)].walk and not m.mon_at(x + a, y + b)), None)
        if spot:
            o = make_monster(game, 'bound_dead', *spot, m.level + 1)
            o.awake = True
            m.mons.append(o)
        game.msg('The seal cracks. The dead one opens its eyes, and steps down out of the niche.', 'bad')
        if random.random() < .5:
            from .nature import curio
            it = curio(game, 'oldcoin')
            it.x, it.y = x, y + (1 if y < m.h // 2 else -1)
            m.items.append(it)
        game.end_turn(1)


def star_map(game, site):
    """The star map before a Gate of Leagues: the nearest city you do not know, and the other gates."""
    from . import folk as FK
    w = game.world
    if getattr(site, 'mapped', False):
        game.msg('The star map shows the cities of the Empire as stars, and the gates as lines between them. You have '
                 'taken what it can tell you.')
        return 0
    site.mapped = True
    cands = sorted((s for s in w.sites if s.kind == 'vcity' and FK.unfound(s)), key=lambda s: cheb(s.x, s.y, site.x, site.y))
    told = []
    if cands:
        c = cands[0]
        FK.discover(game, c, None)
        told.append('the city nearest to it')
    for s in w.sites:
        if s.kind == 'gate' and s is not site and FK.unfound(s):
            FK.discover(game, s, None)
            told.append('another gate')
    if told:
        game.msg('The star map is a map of the land, not the sky: every city of the Empire a star, every gate a line of '
                 f'iron between them. Following the lines you find {" and ".join(told[:2])}. You put them on your map.',
                 'unique')
    else:
        game.msg('The star map is a map of the land, every city of the Empire a star. You know all it shows.', 'info')
    return 10


def light_lamp(game, x, y, site):
    from . import folk as FK
    from . import chronicle as CH
    m = game.map
    m.set(x, y, D.LITLAMP)
    if site:
        site.lit = True
    for s in game.world.sites:
        if s.kind == 'walltower' and FK.unfound(s):
            FK.discover(game, s, None)
    om = game.maps['over']
    for i in info(game).get('wall', ()):
        om.seen[i] = 1
    game.msg('The lard takes, and the lantern burns. Then, far to the west and far to the east, one by one, the other '
             'towers answer: a spark on every tower of the Wall, for as long as you watch. You put them all on your '
             'map.', 'unique')
    CH.add(game, 'Places', 'You lit the lantern on the Northern Wall, and the towers of the Wall answered.', 'seen',
           where=site.name if site else m.name, key='vn:lamp', title='The lanterns of the Wall')
    return 10


# ------------------------------------------------------------------ the chronicle: fragments, riddles, pages
def _fact(game, ch, head, text, src, who, where, key, title=None, place=None):
    from . import chronicle as CH
    f = CH.add(game, ch, text, src, who=who, where=where, key=key, title=title, place=place, quiet=True)
    f['head'] = head
    return f


def give_lore(game, src, who, where, heads=None):
    """A loose fragment of the empire you have not had. Returns its text."""
    s = st(game)
    pool = [(hd, i) for hd in (heads or list(T.FRAGS)) for i in range(len(T.FRAGS[hd])) if (hd, i) not in s['lore']]
    if not pool and heads:
        pool = [(hd, i) for hd in T.FRAGS for i in range(len(T.FRAGS[hd])) if (hd, i) not in s['lore']]
    if not pool:
        return None
    hd, i = random.choice(pool)
    s['lore'].add((hd, i))
    text = T.FRAGS[hd][i]
    _fact(game, 'The Varnish', hd, text, src, who, where, f'vl:{hd}:{i}')
    game.msg(f'Your chronicle grows: The Varnish, {hd.lower()}.', 'gold')
    return text


def give_riddle(game, kind, who, where):
    """A fragment of a riddle that comes from this kind of source. Returns True when there was one."""
    V = info(game)
    s = st(game)
    pool = [k for k, v in V.get('src', {}).items() if v == kind and k not in s['frags']]
    if not pool:
        return False
    rk, i = random.choice(pool)
    riddle_frag(game, rk, i, who, where)
    return True


def place_frag(game, kind, where):
    return give_riddle(game, f'place:{kind}', 'what you saw', where)


def riddle_frag(game, rk, i, who, where):
    r = T.RIDDLE[rk]
    s = st(game)
    if (rk, i) in s['frags']:
        return False
    s['frags'].add((rk, i))
    text, src, false = r['frags'][i]
    eff = info(game).get('src', {}).get((rk, i), src)
    how = 'heard' if eff == 'rumour' else 'seen' if eff.startswith('place:') else 'read'
    f = _fact(game, 'The Old Days', r['title'], text, how, who, where, f'vr:{rk}:{i}')
    if false and rk in s['whole']:
        from . import chronicle as CH
        CH.disprove(game, f['key'], false)
    game.msg(f'Your chronicle grows: a piece of the riddle of {r["title"][0].lower() + r["title"][1:]}.', 'gold')
    whole(game, rk)
    return True


def true_count(game, rk):
    s = st(game)
    return sum(1 for i, fr in enumerate(T.RIDDLE[rk]['frags']) if not fr[2] and (rk, i) in s['frags'])


def whole(game, rk):
    """Six true pieces: the riddle is whole. The answer, the false pieces shown up, and the place it points to."""
    from . import chronicle as CH
    from . import folk as FK
    s = st(game)
    if rk in s['whole'] or true_count(game, rk) < T.WHOLE:
        return False
    s['whole'].add(rk)
    r = T.RIDDLE[rk]
    for i, fr in enumerate(r['frags']):
        if fr[2] and (rk, i) in s['frags']:
            CH.disprove(game, f'vr:{rk}:{i}', fr[2])
    _fact(game, 'The Old Days', r['title'], r['answer'], 'read', 'your own reckoning', 'from all you found',
          f'vr:{rk}:answer', title='The riddle made whole')
    game.msg(f'The riddle of {r["title"][0].lower() + r["title"][1:]} is whole.', 'unique')
    sid = info(game).get('deep', {}).get(r['place'])
    if sid is not None:
        site = game.world.sites[sid]
        if FK.unfound(site):
            FK.discover(game, site, None)
        CH.add(game, 'Places', f'The riddle points to {site.name}, and where it lies.', 'read', who='your own reckoning',
               where='from all you found', place=(site.x, site.y), key=f'vn:{site.id}', title=site.name)
        game.msg(f'And it points to a place: {site.name}. You mark it on your map.', 'unique')
    if len(s['whole']) == len(T.RIDDLES):
        _fact(game, 'The Old Days', T.LAST[0], T.LAST[1], 'read', 'your own reckoning', 'from all you found',
              'vr:last', title=T.LAST[0])
        game.msg('All five riddles are whole. You know now what the Ruin was.', 'unique')
    from . import shadow as SH
    SH.riddle_whole(game, rk)
    return True


def pick_page(game, it):
    """A page in the old letters goes in with your papers, not in your bag."""
    s = st(game)
    key = it.vpage
    s['pages'].add(key)
    b = T.BOOK[key[0]]
    noun = b['noun']
    if not letters(game):
        game.msg(f'You pick up a {noun} written in the old letters. You cannot read it yet; you keep it with your '
                 'papers.', 'info')
        return
    read_page(game, key)


def read_page(game, key):
    s = st(game)
    if key in s['read']:
        return
    s['read'].add(key)
    bk, n = key
    b = T.BOOK[bk]
    noun = b['noun']
    _fact(game, 'The Varnish', f'book:{bk}', b['pages'][n], 'read', f'a {noun} in the old letters',
          game.loc_name() if hasattr(game, 'loc_name') else None, f'vp:{bk}:{n}')
    have = sum(1 for k in s['read'] if k[0] == bk)
    total = len(b['pages'])
    if have == 1:
        game.msg(f'You read the {noun}. Your chronicle grows: The Varnish, loose pages.', 'gold')
    elif have < total:
        game.msg(f'You read the {noun}. It belongs with another you have: {have} of {total}.', 'gold')
    else:
        game.msg(f'You read the {noun}. You have all {total} now. A scribe in a city library could bind them.', 'unique')
    for (rk, i), src in info(game).get('src', {}).items():
        if src == f'page:{bk}:{n}':
            riddle_frag(game, rk, i, f'a {noun} in the old letters', 'in the page itself')


def read_carried(game):
    """You have learnt the letters: the pages you carry can be read now."""
    s = st(game)
    left = sorted(k for k in s['pages'] if k not in s['read'])
    for k in left:
        read_page(game, k)
    return len(left)


def complete(game):
    s = st(game)
    return [bk for bk in info(game).get('books', ()) if bk not in s['bound']
            and all((bk, n) in s['read'] for n in range(len(T.BOOK[bk]['pages'])))]


def bind(game, bk, where):
    """The scribe binds the pages in order, and finds what only the whole shows."""
    from .entities import Item
    s = st(game)
    b = T.BOOK[bk]
    s['bound'].add(bk)
    it = Item(game.new_id(), 'vbook', 'vbook')
    it.book = bk
    it.name = b['title']
    if not game.add_to_inv(it):
        game.spill(game.map, game.player.x, game.player.y, it)
    _fact(game, 'The Varnish', 'Bound books', b['hidden'], 'read', b['title'], where, f'vb:{bk}', title=b['title'])
    _fact(game, 'The Varnish', 'Bound books', b['chron'], 'read', b['title'], where, f'vbc:{bk}')
    game.msg(f'Your chronicle grows: {b["title"]}, bound whole.', 'unique')
    effect(game, b.get('effect'), b['title'])


def effect(game, eff, title):
    """What a whole book shows: a place, a piece of a riddle, an old road, a lie found out."""
    from . import folk as FK
    from . import chronicle as CH
    if not eff:
        return
    w = game.world
    kind = eff[0]
    if kind == 'place':
        what = eff[1]
        if what == 'lowfold':
            cands = [s for s in w.sites if s.kind == 'valley' and FK.unfound(s)] or \
                [s for s in w.sites if s.kind == 'deserted']
        else:
            cands = [s for s in w.sites if s.kind == what and FK.unfound(s)] or [s for s in w.sites if s.kind == what]
        if cands:
            s = random.choice(cands)
            if FK.unfound(s):
                FK.discover(game, s, None)
            game.reveal_place(s.x, s.y)
            CH.add(game, 'Places', f'{title} names {s.name}, and where it lies.', 'read', who=title, place=(s.x, s.y),
                   key=f'lead:{title}', quiet=True)
            game.msg(f'The book names {s.name}. You mark it on your map.', 'info')
    elif kind == 'riddle':
        _k, rk, i = eff
        if i < len(T.RIDDLE[rk]['frags']):
            riddle_frag(game, rk, i, title, 'in the bound book')
    elif kind == 'way':
        from . import hidden as HP
        wy = HP.random_unknown(game, game.over_pos)
        if wy:
            HP.discover_way(game, wy.id, f'{title} follows an old road, and you know where it leaves the land you know.',
                            [HP.start_of(game, wy)])
    elif kind == 'disprove':
        for f in CH.facts(game):
            if f['text'].startswith(eff[1]):
                CH.disprove(game, f['key'], 'his letters were written in his own hand, the last of them too.')
    elif kind == 'lamp':
        towers = [s for s in w.sites if s.kind == 'walltower' and s.lamp]
        for s in towers:
            if FK.unfound(s):
                FK.discover(game, s, None)
            game.msg(f'The book says which tower kept its lantern: {s.name}. You mark it on your map.', 'info')
    elif kind == 'recipe':
        from . import cooking as CK
        CK.learn(game, eff[1], 'Your recipes grow: {name}, from the book.')
    elif kind == 'apple':
        st(game)['apple'] = True
        sid = info(game).get('deep', {}).get('anchor')
        if sid is not None:
            s = w.sites[sid]
            game.reveal_place(s.x, s.y)
            game.msg(f'The book says where the old apple tree grows: on a ledge by {s.name}, under the Sky-Seat. You '
                     'mark it on your map.', 'info')
    elif kind == 'ferry':
        game.player.ferry_free = True
        game.msg('The tally is the ferrymen\'s own. Show it at a ferry and no ferryman will take your fare.', 'info')


# ------------------------------------------------------------------ at the library
def scribe_opts(game, opt):
    """The scribe's Varnish shelf, and binding what you bring whole."""
    from .money import fmt
    out = [opt('The Varnish', 'vlore', LORE_PRICE)]
    for bk in complete(game)[:2]:
        out.append(opt(f'Bind {T.BOOK[bk]["title"]}', f'vbind:{bk}', BIND_PRICE))
    for it in game.player.inv:
        if it.k == 'vbook' and it.book not in st(game)['sold']:
            out.append((f'Sell {it.name} ({fmt(BOUND_PRICE)})', f'vsell:{it.book}'))
            break
    return out


def r_scribe(game, npc, choice, price):
    """Returns True when the choice was a Varnish one."""
    from .money import fmt
    if not (choice == 'vlore' or choice.startswith('vbind:') or choice.startswith('vsell:')):
        return False
    p = game.player
    where = game.loc_name()
    if choice.startswith('vsell:'):
        bk = choice[6:]
        it = next((i for i in p.inv if i.k == 'vbook' and i.book == bk), None)
        if it:
            p.inv.remove(it)
            st(game)['sold'].add(bk)
            p.gold += BOUND_PRICE
            game.say(npc, f'"{it.name}. Whole? Bound in order?" The scribe turns every page twice, and counts out '
                          f'{fmt(BOUND_PRICE)}. "There is no other copy. There never was."')
        return True
    cost = price(LORE_PRICE if choice == 'vlore' else BIND_PRICE)
    if p.gold < cost:
        game.msg('You cannot pay for that.', 'bad')
        return True
    p.gold -= cost
    if choice.startswith('vbind:'):
        bk = choice[6:]
        game.end_turn(D.DAY_LEN // 24, True)
        game.say(npc, '"Sit. It takes an hour, and you will want to watch." The scribe lays the pages out in order, '
                      'stitches them, and stops at the spine. "There is something under the old binding paste. Here."')
        bind(game, bk, where)
        return True
    game.end_turn(D.DAY_LEN // 8, True)
    s = st(game)
    got = 0
    for _ in range(2):
        if give_lore(game, 'read', 'the library\'s Varnish shelf', where):
            got += 1
    if give_riddle(game, 'library', 'the library\'s Varnish shelf', where):
        got += 1
    page = next((k for k, v in sorted(info(game).get('pages', {}).items()) if v == ('library', None)
                 and k not in s['pages']), None)
    if page:
        s['pages'].add(page)
        noun = T.BOOK[page[0]]['noun']
        game.say(npc, f'"There is a {noun} in the old letters in a box of loose papers. Nobody has wanted it in a '
                      'hundred years. Take it."')
        if letters(game):
            read_page(game, page)
        got += 1
    if not got:
        game.say(npc, '"You have read all we keep of the Varnish. The rest is out there, under the moss."')
        p.gold += cost
    else:
        game.say(npc, '"The Varnish. Everyone wants the treasure, nobody wants the people." The scribe brings what the '
                      'shelf has.')
        s['lib'] += 1
    return True


def learnt_letters(game):
    n = read_carried(game)
    if n:
        game.msg(f'With the letters you read the {n} page{"s" if n != 1 else ""} you carry.', 'gold')


# ------------------------------------------------------------------ heard: rumours
def rumour(game, npc=None):
    """Now and then someone knows a piece of a riddle, or something the Varnish said."""
    from . import chronicle as CH
    V = info(game)
    if not V:
        return None
    s = st(game)
    pool = [k for k, v in V['src'].items() if v == 'rumour' and k not in s['frags']]
    who = CH.speaker(npc)
    where = game.loc_name()
    if pool and random.random() < .6:
        rk, i = random.choice(pool)
        riddle_frag(game, rk, i, who, where)
        return T.RIDDLE[rk]['frags'][i][0]
    left = [i for i in range(len(T.FRAGS['Voices'])) if ('Voices', i) not in s['lore']]
    if not left:
        return None
    i = random.choice(left)
    s['lore'].add(('Voices', i))
    text = T.FRAGS['Voices'][i]
    _fact(game, 'The Varnish', 'Voices', text, 'heard', who, where, f'vl:Voices:{i}')
    return f'My grandmother had it from hers, who had it from a stone: {text}'


# ------------------------------------------------------------------ the chronicle's pages
def blocks(game, ch, fs):
    """The Varnish and The Old Days, with their headings: fragments by subject, the books in pieces, the riddles."""
    out = []
    plain = [f for f in fs if not f.get('head')]
    for f in plain:
        out.append(('fact', f))
    s = st(game)
    if ch == 'The Old Days':
        from . import chronicle as CH
        for g in CH.gaps(game, ch):
            out.append(('gap', g))
        for r in T.RIDDLES:
            got = [f for f in fs if f.get('head') == r['title']]
            if not got:
                continue
            out.append(('h', r['title'], TOC.get(r['key'], r['title'])))
            got.sort(key=lambda f: f['key'].endswith(':answer'))
            for f in got:
                out.append(('fact', f))
            if r['key'] not in s['whole']:
                n = true_count(game, r['key'])
                out.append(('gap', f'{r["gap"]} You have {len(got)} piece{"s" if len(got) != 1 else ""} of it.'
                            if n < T.WHOLE else r['gap']))
        last = [f for f in fs if f.get('head') == T.LAST[0]]
        if last:
            out.append(('h', T.LAST[0]))
            out += [('fact', f) for f in last]
        return out
    for hd in T.FRAGS:
        got = [f for f in fs if f.get('head') == hd]
        if got:
            out.append(('h', hd))
            out += [('fact', f) for f in got]
    books = [bk for bk in info(game).get('books', ()) if any(k[0] == bk for k in s['read']) and bk not in s['bound']]
    loose = [bk for bk in books if sum(1 for k in s['read'] if k[0] == bk) == 1]
    sets = [bk for bk in books if bk not in loose]
    if loose:
        out.append(('h', 'Loose pages'))
        for bk in loose:
            out += [('fact', f) for f in fs if f.get('head') == f'book:{bk}']
    if sets:
        out.append(('h', 'Pages that belong together', 'Pages together'))
        for bk in sets:
            b = T.BOOK[bk]
            total = len(b['pages'])
            have = sorted(n for k, n in s['read'] if k == bk)
            noun = b['noun']
            missing = [n for n in range(total) if n not in have]
            plural = noun + ('s' if not noun.endswith('f') else '') if noun != 'diary leaf' else 'diary leaves'
            if noun.endswith('leaf') and noun != 'diary leaf':
                plural = noun[:-1] + 'ves'
            from .calendar import ordinal
            line = f'{total} {plural} in one hand: {len(have)} of {total}.'
            if missing:
                line += ' Still missing: the ' + _and([ordinal(n + 1) for n in missing]) + '.'
            out.append(('p', line))
            for n in have:
                f = next((f for f in fs if f['key'] == f'vp:{bk}:{n}'), None)
                if f:
                    out.append(('fact', f))
    bound = [f for f in fs if f.get('head') == 'Bound books']
    if bound:
        out.append(('h', 'Bound books'))
        out += [('fact', f) for f in bound]
    if not letters(game):
        out.append(('gap', 'What the Varnish wrote you cannot read. The scribes of a city library teach the old '
                           'letters.'))
    unread = len(s['pages']) - len(s['read'])
    if unread > 0:
        out.append(('gap', f'You carry {unread} page{"s" if unread != 1 else ""} in the old letters that you cannot '
                           'read yet.'))
    if not fs:
        out.append(('gap', 'The empire before the Ruin: its gods, its emperors, its people. Their stones stand in the '
                           'ruins, their pages lie where they fell, and the scribes keep a shelf of what is known.'))
    return out


def _and(xs):
    return xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + ' and ' + xs[-1]


# ------------------------------------------------------------------ items: pages and bound books (entities.CRAFT)
def display(game, it):
    if it.k == 'vbook':
        return it.name
    return 'A page in the old letters'


def lines(game, it):
    if it.k == 'vbook':
        b = T.BOOK[it.book]
        return [f'A book of the Varnish, bound whole from {len(b["pages"])} {b["noun"]}s by a library scribe.',
                b['chron'], 'A city library would pay well for it, once.']
    return ['A page written in the old letters of the Varnish.']


def value(game, it):
    return 2 if it.k == 'vbook' else .1


def glyph(it):
    return '≡' if it.k == 'vbook' else '~'


def color(it):
    return (196, 170, 255) if it.k == 'vbook' else (216, 206, 176)


def read_bound(game, it):
    """Reading a bound book: the whole story, in order, with its last page."""
    b = T.BOOK[it.book]
    text = '\n\n'.join(b['pages'] + [b['hidden']])
    game.request = ('dialog', b['title'], text)
    return 0


# ------------------------------------------------------------------ the league stones (events.POI)
def on_poi(game, poi):
    if poi.kind != 'leaguestone':
        return False
    from .engine import dir_name
    from . import folk as FK
    w = game.world
    city = w.sites[poi.city]
    put_here = info(game).get('pages', {})
    for key, where in put_here.items():
        if where == ('poi', poi.id) and key not in st(game)['pages']:
            from .entities import Item
            it = Item(game.new_id(), 'vpage', 'vpage')
            it.vpage = key
            pick_page(game, it)
            game.msg('Wedged under the stone, folded small: a page in the old letters.', 'info')
    if not letters(game):
        text = (f'A stone post, knee high, cut with a Varnish numeral: {poi.num}. Below it, letters you cannot read, '
                f'and an arrow pointing {dir_name(city.x - poi.x, city.y - poi.y)}.')
    elif poi.num == 'I':
        text = ('A stone post, cut with the numeral I. The letters say: "One league. Count your steps; the city counts '
                'them too."')
        if FK.unfound(city):
            FK.discover(game, city, None)
            text += ' The way is plain now. You mark the city on your map.'
    else:
        text = (f'A stone post, cut with the numeral {poi.num}. The letters say: "{NUMERAL[poi.num].capitalize()} '
                f'leagues." An arrow points {dir_name(city.x - poi.x, city.y - poi.y)}.')
    nxt = getattr(poi, 'next', None)
    if nxt is not None and letters(game):
        from .events import reveal
        reveal(game, w.pois[nxt])
    game.request = ('dialog', poi.name, text)
    return True


def register():
    from . import events as EV
    from .nature import CURIO
    from . import entities as EN
    EV.RESOLVERS['varnish'] = r_varnish
    EN.CRAFT.update({'vpage': 'varnish', 'vbook': 'varnish'})
    CURIO.update({'stariron': ('A shard of star-iron', 8, (150, 180, 240), 'Black iron of the Varnish that never rusts '
                                                                           'and still shines. A smith would want it.'),
                  'oldcoin': CURIO.get('oldcoin') or ('An old coin', 3, (150, 170, 120), 'A coin of the old days, '
                                                                                       'green with age.')})


register()
