"""The land in finer grain: the newer kinds of country (moor, birch wood, mountain meadow, flood meadow, mangrove,
mesa and canyon, oasis, limestone karst with its sinkholes), what each asks of a traveller, the names of the great
woods, moors, hills and wastes, and the two small places that go with them: an oasis where the caravans water, and a
herders' summer hut up on the mountain meadows.

Every kind of country here does one thing you notice while you walk it:
- moor: open, you see far; but on early mornings a mist lies on it, and the wolves hunt in it.
- old forest (deep_forest): you see almost nothing under the trees; the rare herbs grow there.
- birch wood: light and quiet; little lies in wait there.
- mountain meadow (alpine): high and open, you see far; mountain herbs; the herders' huts.
- flood meadow: the farms crowd onto it; in spring it lies under water and walking is slow.
- mangrove: trees standing in the tide; slow going, crocodiles and smugglers.
- canyon (between the mesas): narrow and walled; robbers wait there.
- oasis: water and palms in the desert; a caravan camp with a trader.
- karst: limestone hills; their sinkholes drop into caves."""
import random
from array import array

from . import data as D
from .worldgen import cheb

# ------------------------------------------------------------------ the names of the land
FAMILY = {}
for _f, _bs in (('wood', 'forest deep_forest conifer taiga dry_forest jungle birch'),
                ('tangle', 'mangrove'),
                ('moor', 'moor'),
                ('plain', 'meadow steppe savanna shrubland floodplain clearing'),
                ('hills', 'hills karst badlands alpine'),
                ('mountains', 'mountain peak'),
                ('fen', 'swamp marsh'),
                ('waste', 'desert dune dune_crest'),
                ('breaks', 'mesa canyon'),
                ('cold', 'tundra tundra_hills shrubland_cold glacier')):
    for _b in _bs.split():
        FAMILY[_b] = _f
NAME_PARTS = {
    'wood': (['Grey', 'Elder', 'Thorn', 'Wolf', 'Raven', 'Black', 'Silver', 'Ash', 'Oak', 'Hollow', 'Mist', 'Owl', 'Hart',
              'Briar', 'Moss', 'Fern', 'Gloam', 'Bramble', 'Rook', 'Yew'], ['wood', 'weald', 'holt', 'shaw', 'hurst']),
    'tangle': (['Salt', 'Mud', 'Root', 'Brack', 'Eel', 'Heron', 'Drowned'], [' Tangle', ' Mangroves']),
    'moor': (['Ash', 'Grey', 'Heather', 'Wind', 'Raven', 'Cold', 'Mist', 'Black', 'Curlew', 'Lapwing'], ['moor', 'moors', ' Heath']),
    'plain': (['Gold', 'Wind', 'Long', 'Bright', 'Sun', 'Green', 'Barley', 'Horse', 'Lark', 'Amber', 'Tall', 'Red',
               'Hare', 'Broad'], [' Plains', ' Downs', ' Fields', ' Grass', ' Meadows', 'lands']),
    'hills': (['Iron', 'Stone', 'Grim', 'High', 'Red', 'Chalk', 'Flint', 'Barrow', 'Cairn', 'Wether', 'Goat', 'Crow'],
              [' Hills', ' Fells', 'tors', ' Downs', ' Heights']),
    'mountains': (['Iron', 'Grey', 'Storm', 'White', 'Dragon', 'Giant', 'Frost', 'Broken', 'Thunder', 'Ember', 'Eagle'],
                  ['spine', ' Teeth', ' Crowns', ' Peaks', ' Wall']),
    'fen': (['Black', 'Sump', 'Weeping', 'Reed', 'Mire', 'Dead', 'Grey', 'Frog', 'Eel', 'Bog', 'Bittern'],
            ['fen', ' Mire', ' Marshes', ' Fens']),
    'waste': (['Red', 'Burning', 'Bone', 'Thirst', 'Sun', 'Copper', 'Dust', 'Glass', 'Jackal'], [' Waste', ' Sands', ' Barrens']),
    'breaks': (['Red', 'Rust', 'Vulture', 'Broken', 'Hollow', 'Blood', 'Sunset'], [' Mesas', ' Breaks', ' Canyons']),
    'cold': (['White', 'Frost', 'Pale', 'Wolf', 'Rime', 'Snow', 'Bitter'], [' Barrens', ' Wastes', ' Tundra']),
}
REGION_FAMILY = {'grass': 'plain', 'forest': 'wood', 'swamp': 'fen', 'hills': 'hills', 'coast': 'plain'}
MIN_AREA = 90                  # cells: smaller patches get no name of their own


def make_name(family, used):
    first, last = NAME_PARTS[family]
    for _ in range(80):
        a, b = random.choice(first), random.choice(last)
        nm = a + b
        if nm not in used and 'The ' + nm.strip() not in used and a[-1].lower() != b.strip()[0].lower() \
                and not a.lower().endswith(b.strip()[:2].lower()):
            return nm
    return random.choice(first) + random.choice(last) + ' ' + str(len(used))


def region_name(biome, used):
    """A name for a region when the old list has run out (the bigger world has more regions)."""
    return make_name(REGION_FAMILY.get(biome, 'plain'), used)


def name_areas(m, world):
    """Every large stretch of one kind of country gets a name: the Ravenweald, the Ashmoors, the Ironspine."""
    w, h = m.w, m.h
    names = m.biome_names
    fam = [FAMILY.get(b) for b in names]
    area_of = array('H', bytes(2 * w * h))
    areas = [None]
    used = {r.name for r in world.regions} | {n for n, _x, _y in getattr(world, 'wonders', ())}
    bio = m.biome
    for start in range(w * h):
        f = fam[bio[start]]
        if f is None or area_of[start]:
            continue
        k = len(areas)
        area_of[start] = k
        cells = [start]
        j = 0
        while j < len(cells):
            c = cells[j]
            j += 1
            x, y = c % w, c // w
            for nc in ((c - 1) if x > 0 else -1, (c + 1) if x < w - 1 else -1, c - w if y > 0 else -1, c + w if y < h - 1 else -1):
                if nc >= 0 and not area_of[nc] and fam[bio[nc]] == f:
                    area_of[nc] = k
                    cells.append(nc)
        if len(cells) < MIN_AREA:
            for c in cells:
                area_of[c] = 65535              # seen, but too small to name
            continue
        sx = sum(c % w for c in cells) // len(cells)
        sy = sum(c // w for c in cells) // len(cells)
        nm = make_name(f, used)
        used.add(nm)
        areas.append(dict(name='The ' + nm.strip(), family=f, x=sx, y=sy, size=len(cells)))
    for i in range(w * h):
        if area_of[i] == 65535:
            area_of[i] = 0
    world.area_of, world.areas = area_of, areas


def area_at(world, x, y):
    """The name of the stretch of country at (x, y), or None."""
    ao = getattr(world, 'area_of', None)
    if not ao:
        return None
    from .world import WORLD_W
    k = ao[y * WORLD_W + x]
    return world.areas[k]['name'] if k else None


def the(name):
    return 'the ' + name[4:] if name.startswith('The ') else name


# ------------------------------------------------------------------ walking the land
def biome(game, x=None, y=None):
    m = game.maps['over']
    p = game.player
    x = p.x if x is None else x
    y = p.y if y is None else y
    bio = getattr(m, 'biome', None)
    if bio is None or not m.inb(x, y):
        return None
    return m.biome_names[bio[y * m.w + x]]


def misty(game):
    """Early mornings the moors lie under a mist."""
    from .towns import hour
    return 4 <= hour(game) < 9


def sight(game, r):
    """How far you see on the overworld by day, by the kind of country underfoot."""
    b = biome(game)
    if b == 'deep_forest':
        return 1
    if b == 'moor':
        return 1 if misty(game) else 6
    if b == 'alpine':
        return 7
    if b == 'canyon':
        return min(r, 2)
    return r


def ambush(game):
    """How likely something waits for you here, against the usual."""
    b = biome(game)
    return {'canyon': 2.0, 'birch': .5, 'clearing': .7, 'mangrove': 1.3}.get(b, 1.5 if b == 'moor' and misty(game) else 1.0)


def cost(game, c):
    """The flood meadows lie under water in spring."""
    from . import calendar as CAL
    if biome(game) == 'floodplain' and CAL.season(game.day) == 'spring':
        return c * 2
    return c


PACKS = {
    'moor': ['wolf', 'worg', 'winter_wolf', 'banshee'],
    'mangrove': ['crocodile', 'constrictor', 'giant_frog', 'mire_leech'],
    'canyon': ['bandit', 'brigand', 'gnoll_hunter', 'vulture'],
    'alpine': ['giant_hawk', 'brown_bear', 'wyvern', 'snow_ape'],
    'karst': ['bat', 'cave_bear', 'centipede'],
}
SMUGGLERS = ['bandit', 'brigand']


def pack(game, lvl):
    """The beasts of this kind of country, or None to use the region's own."""
    b = biome(game)
    if b == 'mangrove' and random.random() < .3:
        return [random.choice(SMUGGLERS) for _ in range(random.randint(2, 4))]
    pool = [k for k in PACKS.get(b, ()) if k in D.MONSTERS and D.MONSTERS[k]['min_l'] <= lvl + 1]
    if not pool or random.random() < .4:
        return None
    k = random.choice(pool)
    big = D.MONSTERS[k]['hp'] >= 2
    n = random.randint(1, 2) if big else random.randint(2, 3 + lvl // 4)
    from .worldgen import band_keys
    return band_keys(k, n)


def forage(game, where):
    """What grows here: (groups and weights, how much likelier the rare herbs are)."""
    b = biome(game)
    if b in ('deep_forest', 'alpine'):
        return dict(where, herb=where.get('herb', 1) + 4), 4
    if b == 'floodplain':
        return dict(where, root=where.get('root', 0) + 3, berry=where.get('berry', 0) + 2), 1
    return where, 1


def on_step(game):
    """Say so when you walk into a named stretch of country, or onto a flooded meadow."""
    p = game.player
    w = game.world
    nm = area_at(w, p.x, p.y)
    last = getattr(game, 'area_said', None)
    if nm and nm != last and game.turn - getattr(game, 'area_said_turn', -999) > 60:
        game.area_said, game.area_said_turn = nm, game.turn
        what = {'wood': 'woods', 'tangle': 'mangroves', 'moor': 'moor', 'plain': 'open country', 'hills': 'hills',
                'fen': 'marshes', 'waste': 'desert', 'breaks': 'canyon country', 'cold': 'frozen land'}
        k = w.area_of[p.y * game.maps['over'].w + p.x]
        game.msg(f'You enter {the(nm)}: {what.get(w.areas[k]["family"], "wild country")}.', 'info')
    b = biome(game)
    if b == 'floodplain' and cost(game, 1) > 1 and not getattr(game, 'flood_said', False):
        game.flood_said = True
        game.msg('The flood meadows lie under water this spring. You wade.', 'info')
    if b == 'moor' and misty(game) and game.day != getattr(game, 'mist_said', -1):
        game.mist_said = game.day
        game.msg('A mist lies on the moor. You can barely see your own feet.', 'info')


# ------------------------------------------------------------------ the oasis and the herders' huts
OASIS_NAMES = ['Palmwater', 'Sweetwell', 'Date Spring', 'Greenwater', 'Caravan Well', 'Mirage Pool', 'The Last Well']
SHIELING_NAMES = ['Shieling', 'Summer Hut', 'Goat Hut', 'Herders\' Hut']


def place_sites(game, m, world, reach_set):
    """A caravan camp at each oasis, and herders' huts up on the mountain meadows."""
    from .sites import Site
    w = m.w
    taken = [(s.x, s.y) for s in world.settlements] + [(q.x, q.y) for q in world.sites] + \
            [(d.x, d.y) for d in world.dungeons.values()] + [(h.x, h.y) for h in world.holds]
    names = OASIS_NAMES[:]
    random.shuffle(names)
    for ox, oy in getattr(world, 'oases', []):
        spots = [(ox + dx, oy + dy) for dx in range(-3, 4) for dy in range(-2, 3)]
        random.shuffle(spots)
        for x, y in spots:
            i = y * w + x
            if not names or i not in reach_set or not D.TILES[m.tile(x, y)].walk or m.tile(x, y) in (D.ROAD, D.ENTR):
                continue
            if any(cheb(x, y, a, b) < 3 for a, b in taken):
                continue
            st = Site(len(world.sites), 'oasis', x, y, names.pop())
            st.faction = world.region_at(x, y).faction
            world.sites.append(st)
            taken.append((x, y))
            break
    alp = m.biome_names.index('alpine') if 'alpine' in m.biome_names else None
    if alp is None:
        return
    from .world import scaled
    cells = [i for i in reach_set if m.biome[i] == alp and m.t[i] == D.GRASS]
    random.shuffle(cells)
    want = scaled(3)
    from .towns import town_names
    for i in cells:
        if want <= 0:
            break
        x, y = i % w, i // w
        if not (3 <= x < w - 3 and 3 <= y < m.h - 3) or any(cheb(x, y, a, b) < 10 for a, b in taken):
            continue
        fam = town_names('human')[0].split()[-1]
        st = Site(len(world.sites), 'shieling', x, y, f'{fam}\'s {random.choice(SHIELING_NAMES)}')
        st.faction = world.region_at(x, y).faction
        world.sites.append(st)
        taken.append((x, y))
        want -= 1


def site_map(game, site):
    from .entities import GameMap, make_npc
    from .data import SAND, GRASS, WATER, TREE, PATH, WALL, FLOOR, DOOR, FENCE, TABLE, BED, FIREPIT
    from .towns import town_names, townsfolk
    names = town_names('human')
    if site.kind == 'oasis':
        w, h = 60, 30
        m = GameMap(site.map_key, 'town', site.name, w, h, SAND)
        cx, cy = 34, 15
        for y in range(h):
            for x in range(w):
                d = ((x - cx) / 7) ** 2 + ((y - cy) / 3.6) ** 2
                if d < 1:
                    m.set(x, y, WATER)
                elif d < 3.4 and random.random() < .35:
                    m.set(x, y, TREE)                    # palms round the water
                elif d < 4.2:
                    m.set(x, y, GRASS)
        for x in range(0, cx - 8):
            m.set(x, cy, PATH)
        # the caravan's tents along the shore
        tents = [(14, 8), (14, 19), (48, 7), (48, 20)]
        for tx, ty in tents:
            for y in range(ty, ty + 4):
                for x in range(tx, tx + 6):
                    edge = y in (ty, ty + 3) or x in (tx, tx + 5)
                    m.set(x, y, WALL if edge else FLOOR)
            m.set(tx + 2, ty + (3 if ty < cy else 0), DOOR)
            m.set(tx + 1, ty + 1, BED)
        m.mons.append(make_npc(game, f'{names.pop()} the Caravan Master', 'lands', '#f0d080', 20, cy - 1, True))
        for _ in range(3):
            townsfolk(game, m, [(15, 9)], (random.randint(16, 26), cy + random.choice((-2, 2))), names, 'carter', fg='#c8b088')
        for x, y in ((22, cy + 3), (24, cy + 4)):
            m.mons.append(make_npc(game, 'A camel', 'livestock', '#c8a060', x, y, False, ch='c'))
        fires = [(27, cy + 3, 5)]                     # the caravan's fire on the shore
    else:
        w, h = 50, 22
        m = GameMap(site.map_key, 'town', site.name, w, h, GRASS)
        cy = h // 2
        for x in range(0, 20):
            m.set(x, cy, PATH)
        hx, hy = 20, cy - 3                         # a low stone hut
        for y in range(hy, hy + 6):
            for x in range(hx, hx + 8):
                m.set(x, y, WALL if y in (hy, hy + 5) or x in (hx, hx + 7) else FLOOR)
        m.set(hx, cy, DOOR)
        m.set(hx + 5, hy + 1, BED)
        m.set(hx + 3, hy + 2, TABLE)
        fires = [(hx + 5, hy + 4, 4)]                 # the hearth
        px, py = 32, cy - 5                         # the goat fold
        for y in range(py, py + 10):
            for x in range(px, px + 12):
                if y in (py, py + 9) or x in (px, px + 11):
                    m.set(x, y, FENCE)
        m.set(px, cy, GRASS)
        for _ in range(random.randint(4, 6)):
            m.mons.append(make_npc(game, 'A goat', 'livestock', '#c8b890', random.randint(px + 2, px + 9),
                                   random.randint(py + 2, py + 7), False, ch='g'))
        m.mons.append(make_npc(game, f'Herder {names.pop()}', 'lands', '#d8c8a0', hx + 2, hy + 3, True))
        m.mons.append(make_npc(game, 'A sheepdog', 'dog', '#b89060', 28, cy + 1, False, ch='d'))
    m.glows = []
    for x, y, r in fires:
        m.set(x, y, FIREPIT)
        m.glows.append((x, y, (255, 140, 50), r))
    m.lights = list(m.glows)
    m.radius, m.sid, m.hid, m.signs = 60, None, None, []
    m.site = site.id
    m.entry = (0, cy)
    for i in range(len(m.seen)):
        m.seen[i] = 1
    return m


CHEESE_PRICE, DATES_PRICE = 60, 30


def on_enter(game, site, m):
    """The herders' huts stand empty in winter: herder, flock and dog are down by the villages until spring."""
    if site.kind != 'shieling':
        return
    from .seasons import herders_away
    away = getattr(m, 'away', [])
    if herders_away(game):
        if not away:
            m.away = [o for o in m.mons if o.role in ('lands', 'livestock', 'dog')]
            m.mons = [o for o in m.mons if o not in m.away]
        game.msg('The hut is shut up for the winter. The herder has taken the flock down to the villages.', 'info')
    elif away:
        m.mons += away
        m.away = []


def talk(game, npc):
    from . import events as EV
    from .money import fmt
    site = game.world.sites[game.map.site]
    if site.kind == 'oasis':
        key = f'oasis{site.id}'
        if game.day - getattr(site, 'stock_day', -99) >= 5 or key not in game.shops:
            from .worldgen import gen_shop
            site.stock_day = game.day
            game.shops[key] = gen_shop(game)
        EV.ask(game, 'lands', npc.name, '"Water is free here; that is the law of the sands. The rest you pay for. '
               'We carry what the towns forgot to make, and dates."',
               [('See the goods', 'shop'), (f'Buy dates ({fmt(DATES_PRICE)})', 'dates'), ('Goodbye', 'bye')], site=site.id)
    else:
        EV.ask(game, 'lands', npc.name, '"Up here it is the goats and me, all summer. Cheese, if you want it. '
               'And mind the eagles; they take kids."',
               [(f'Buy goat cheese ({fmt(CHEESE_PRICE)})', 'cheese'), ('Goodbye', 'bye')], site=site.id)


def r_lands(game, choice, ctx):
    from .hunger import make_food
    from .money import fmt
    p = game.player
    if choice == 'shop':
        game.request = ('shop', f'oasis{ctx["site"]}')
    elif choice in ('dates', 'cheese'):
        price = DATES_PRICE if choice == 'dates' else CHEESE_PRICE
        if p.gold < price:
            game.msg(f'That costs {fmt(price)}.', 'bad')
            return
        it = make_food(game, 'dates' if choice == 'dates' else 'goat_cheese', 2 if choice == 'dates' else 1)
        if not game.add_to_inv(it):
            game.msg('Your pack is full.', 'bad')
            return
        p.gold -= price
        game.msg(f'You buy {it.name.lower()}.', 'good')


def register():
    from . import events as EV
    EV.RESOLVERS['lands'] = r_lands


register()
