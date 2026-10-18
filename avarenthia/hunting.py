"""Herds and hunting, skinning, tanning and leatherworking.

The world map does not fill up with animals. Game is a number per stretch of country (world.areas); you see a herd
(one `q`) only within a few cells, and where one passed, hoof tracks `:` that fade in a day or two. Two to four great
herds (reindeer, aurochs, wildebeest) travel with the seasons, north and up in summer, south and down in winter, and
wolves or gnolls follow them. Walk into a herd and its zone becomes the hunting ground: the herd grazes, the leader
(`Q`) watches, the wind decides what they smell. A hit animal runs on a few steps and falls; the rest flee.

A carcass is skinned where it lies (Enter, with a knife or a dagger): cuts of meat named by the animal, a hide, and
sometimes antlers, horn or tusks. A fresh hide rots in two days; salted on a stretching frame it keeps. A tanner
makes leather of it in three days, or oak bark does it in your pack in five. Leather goes on a workbench."""
import random

from . import data as D

DAY = D.DAY_LEN


class Herd:
    """A herd on the world map. Ordinary herds come and go near you; great ones travel with the seasons."""

    def __init__(self, uid, kind, x, y, n, great=False):
        self.id, self.kind, self.x, self.y, self.n, self.great = uid, kind, x, y, n, great
        self.home_y = y
        self.rest = 0            # a great herd that was hunted moves on for a while


# ------------------------------------------------------------------ what lives where
# by the lands of cooking.LANDS: the herd animals there
LAND_PREY = {
    'forest': ['red_deer', 'red_deer', 'boar'], 'birch': ['red_deer'], 'taiga': ['elk', 'reindeer'], 'tundra': ['reindeer'],
    'moor': ['heath_sheep'], 'mountain': ['ibex', 'wild_goat'], 'steppe': ['aurochs', 'wild_horse'],
    'savanna': ['gazelle', 'wildebeest'], 'desert': ['gazelle'], 'canyon': ['bighorn'], 'marsh': ['elk'],
    'jungle': ['forest_hog'],
}
GREAT = {'reindeer': 'tundra', 'aurochs': 'steppe', 'wildebeest': 'savanna'}
FOLLOWERS = {'reindeer': ['wolf', 'winter_wolf'], 'aurochs': ['wolf'], 'wildebeest': ['gnoll_hunter', 'hyena']}
OPEN = {D.GRASS, D.SAND, D.HILLS, D.ROAD}
COVER = {D.TREE, D.FOREST, D.ROCK, D.SWAMP}
WIND = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]     # where the wind comes FROM
WIND_NAME = ['north', 'northeast', 'east', 'southeast', 'south', 'southwest', 'west', 'northwest']
ARROW = ['↓', '↓', '←', '←', '↑', '↑', '→', '→']        # which way it blows, at the edge (or corner) it comes from


def lands_at(game, x, y):
    from . import cooking as CK
    from . import seasons as SE
    om = game.maps['over']
    return CK.lands_of(SE.biome(om, y * om.w + x)) if om.inb(x, y) else []


def prey_for(game, x, y):
    for land in lands_at(game, x, y):
        if land in LAND_PREY:
            return LAND_PREY[land]
    return []


def area_key(game, x, y):
    w = game.world
    ao = getattr(w, 'area_of', None)
    from .world import WORLD_W
    k = ao[y * WORLD_W + x] if ao else 0
    return k if k else -1 - w.region_at(x, y).id


def stock(game, x, y):
    """How much game this stretch of country holds: 0 to 4."""
    st = game.world.__dict__.setdefault('game_stock', {})
    k = area_key(game, x, y)
    if k not in st:
        lands = lands_at(game, x, y)
        st[k] = 4 if any(l in ('steppe', 'savanna', 'tundra', 'forest', 'taiga') for l in lands) else \
            1 if 'desert' in lands else 3
    return st[k]


def hunted(game, x, y):
    st = game.world.__dict__.setdefault('game_stock', {})
    k = area_key(game, x, y)
    st[k] = max(0, stock(game, x, y) - 1)


def herds(game):
    return game.world.__dict__.setdefault('herds', [])


def hoof(game):
    return game.world.__dict__.setdefault('hoof', {})


def setup(game):
    """The great herds of this world: two to four, each on its own wide land."""
    om, w = game.maps['over'], game.world
    if getattr(w, 'great_done', False):
        return
    w.great_done = True
    cands = {}
    for _ in range(3000):
        x, y = random.randrange(om.w), random.randrange(om.h)
        if not D.TILES[om.tile(x, y)].walk or om.tile(x, y) in (D.TOWN, D.CITY):
            continue
        for kind, land in GREAT.items():
            if land in lands_at(game, x, y):
                cands.setdefault(kind, []).append((x, y))
    want = random.randint(2, 4)
    kinds = [k for k in GREAT if cands.get(k)]
    random.shuffle(kinds)
    for i in range(min(want, len(kinds) * 2)):
        kind = kinds[i % len(kinds)] if kinds else None
        if not kind:
            break
        x, y = random.choice(cands[kind])
        hd = Herd(game.new_id(), kind, x, y, random.randint(12, 30), True)
        herds(game).append(hd)


def herd_at(game, x, y):
    if game.map.kind != 'over':
        return None
    return next((h for h in herds(game) if (h.x, h.y) == (x, y) and seen_herd(game, h)), None)


def herd_sight(game):
    """How far off you see a herd on the world map: a few cells, more on open land and with Hunting."""
    from . import lifeskills as LS
    p, m = game.player, game.map
    t = m.tile(p.x, p.y)
    r = 4 + (1 if t in OPEN else 0) + (1 if LS.rank(game, 'hunting') >= 10 else 0) - (1 if t == D.FOREST else 0)
    return max(2, min(r, game.over_sight() + 1))


def seen_herd(game, h):
    from .worldgen import cheb
    p = game.player
    return game.map.kind == 'over' and cheb(h.x, h.y, p.x, p.y) <= herd_sight(game) and game.visible(h.x, h.y)


def look(game, h):
    """The sign of a herd: one q in the colour of its animal."""
    return 'q', D.MONSTERS[h.kind]['fg']


def herd_name(h):
    t = D.MONSTERS[h.kind]
    word = {'red_deer': 'deer', 'boar': 'boar'}.get(h.kind, t['name'].lower())
    return f'A great herd of {word}' if h.great else f'A herd of {word}'


# ------------------------------------------------------------------ the herds move
def over_tick(game):
    """On the world map: herds come and go near you and leave their tracks."""
    from .worldgen import cheb
    p, om = game.player, game.maps['over']
    if game.turn % 15:
        return
    hs = herds(game)
    hs[:] = [h for h in hs if h.great or cheb(h.x, h.y, p.x, p.y) <= 10]
    local = [h for h in hs if not h.great]
    if len(local) < 2 and random.random() < .3:
        for _ in range(8):
            d = random.randint(4, 8)
            x, y = p.x + random.randint(-d, d), p.y + random.randint(-d, d)
            if not om.inb(x, y) or cheb(x, y, p.x, p.y) < 4 or not D.TILES[om.tile(x, y)].walk:
                continue
            if om.tile(x, y) in (D.TOWN, D.CITY, D.ROAD, D.ENTR) or game.world.settlement_at(x, y):
                continue
            kinds = prey_for(game, x, y)
            if not kinds or random.random() * 4 >= stock(game, x, y):
                continue
            hs.append(Herd(game.new_id(), random.choice(kinds), x, y, random.randint(3, 7)))
            break
    for h in hs:
        if not h.great and random.random() < .25:
            step(game, h, random.choice(WIND))


def step(game, h, d):
    om = game.maps['over']
    x, y = h.x + d[0], h.y + d[1]
    if not om.inb(x, y) or not D.TILES[om.tile(x, y)].walk or om.tile(x, y) in (D.TOWN, D.CITY):
        return False
    if game.world.settlement_at(x, y):
        return False
    hoof(game)[(h.x, h.y)] = (game.turn, h.kind, d)
    h.x, h.y = x, y
    return True


def daily(game):
    """Each day: the great herds travel with the seasons, the game comes back, old tracks fade, hides rot."""
    from . import seasons as SE
    w = game.world
    w.wind = (getattr(w, 'wind', random.randrange(8)) + random.choice((-1, 0, 0, 1))) % 8
    now = SE.Now(game)
    summer = 60 <= now.doy < 240                        # spring and summer: north and up; autumn and winter: south
    for h in herds(game):
        if not h.great:
            continue
        if h.rest:
            h.rest -= 1
        if game.day % 2 and not h.rest:
            continue
        want = -1 if summer else 1
        if abs(h.y + want - h.home_y) > 30:
            want = 0
        opts = [(dx, want) for dx in (-1, 0, 1)] if want else [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy]
        random.shuffle(opts)
        opts.sort(key=lambda d: GREAT[h.kind] not in lands_at(game, h.x + d[0], h.y + d[1]))
        for d in opts:
            if step(game, h, d):
                break
        if random.random() < .2:
            follow(game, h)
    tr = hoof(game)
    for k in [k for k, v in tr.items() if game.turn - v[0] > DAY * 2]:
        del tr[k]
    st = w.__dict__.get('game_stock', {})
    if game.day % 10 == 0:
        for k in st:
            st[k] = min(4, st[k] + 1)
    spoil(game)


def follow(game, h):
    """Wolves follow the reindeer and the aurochs, gnolls the wildebeest."""
    from . import wanderers as WA
    w = game.world
    if sum(1 for wd in w.wanderers if getattr(wd, 'herd', None) == h.id) >= 1:
        return
    keys = [random.choice(FOLLOWERS[h.kind]) for _ in range(random.randint(2, 4))]
    keys = [k for k in keys if k in D.MONSTERS] or ['wolf'] * 3
    om = game.maps['over']
    x, y = h.x + random.randint(-2, 2), h.y + random.randint(-2, 2)
    if not om.inb(x, y) or not D.TILES[om.tile(x, y)].walk:
        return
    wd = WA.make_group(game, 'monsters', x, y, w.danger_at(x, y) + 1, keys)
    wd.home, wd.herd = (h.x, h.y), h.id
    w.wanderers.append(wd)


def tracks_at(game, x, y):
    """Fresh hoof tracks on the world map: (turn, kind, direction) or None."""
    v = hoof(game).get((x, y))
    if v and game.turn - v[0] <= DAY * 2:
        return v
    return None


def track_look(game, x, y):
    v = tracks_at(game, x, y)
    if not v:
        return None
    age = (game.turn - v[0]) / (DAY * 2)
    k = 1 - age * .6
    return ':', (int(170 * k + 40), int(140 * k + 36), int(100 * k + 30))


def on_step(game):
    """Walking onto tracks: reading them, more with Hunting."""
    from . import lifeskills as LS
    p = game.player
    v = tracks_at(game, p.x, p.y)
    if not v or getattr(game, '_track_read', None) == (p.x, p.y):
        return
    game._track_read = (p.x, p.y)
    r = LS.rank(game, 'hunting')
    if random.random() > .5 + r * .05:
        return
    from .engine import dir_name
    LS.gain(game, 'hunting', .5)
    hours = (game.turn - v[0]) * 24 // DAY
    word = D.MONSTERS[v[1]]['name'].lower()
    if r < 3:
        game.msg(f'Hoof tracks, heading {dir_name(*v[2])}.', 'info')
        return
    when = 'very fresh' if hours < 3 else f'about {hours} hours old' if hours < 24 else 'a day old or more'
    game.msg(f'Tracks of {word}, {when}, heading {dir_name(*v[2])}.', 'info')


# ------------------------------------------------------------------ the hunting ground
def hunt(game, h):
    """Walking into a herd on the world map: its zone becomes the hunting ground."""
    from . import zones as ZN
    from .worldgen import cheb
    p = game.player
    dx, dy = h.x - p.x, h.y - p.y
    m = ZN.enter(game, (h.x, h.y), near=(-dx * 30, -dy * 18))
    m.hunt = h.id
    mx, my = ZN.local_mid(game, m)
    spots = [(x, y) for y in range(my - 8, my + 9) for x in range(mx - 10, mx + 11)
             if m.inb(x, y) and D.TILES[m.tile(x, y)].walk and not m.mon_at(x, y) and 11 <= cheb(x, y, p.x, p.y)]
    if not spots:
        spots = [ZN.free_near(game, m, mx, my)]
    c = min(spots, key=lambda s: abs(cheb(s[0], s[1], p.x, p.y) - 14) + random.random() * 3)
    from .worldgen import free_around
    near = [c] + free_around(game, m, c[0], c[1], 4)
    lvl = max(1, game.world.danger_at(h.x, h.y))
    n = min(len(near), 3 + min(h.n, 6) // 2 + (2 if h.great else 0))
    from .entities import make_monster
    for i in range(n):
        o = make_monster(game, h.kind, near[i][0], near[i][1], lvl)
        o.prey, o.awake, o.ps = h.id, True, 'graze'
        if i == 0:
            o.ch, o.lead = 'Q', True
            if h.kind in ('red_deer', 'elk', 'reindeer', 'aurochs', 'ibex', 'bighorn'):
                o.name = {'red_deer': 'Red Deer Stag', 'elk': 'Elk Bull', 'reindeer': 'Reindeer Bull', 'aurochs': 'Aurochs Bull',
                          'ibex': 'Ibex Buck', 'bighorn': 'Bighorn Ram'}[h.kind]
        m.mons.append(o)
    small(game, m)
    w = game.world
    w.wind = getattr(w, 'wind', random.randrange(8))
    game.msg(f'{herd_name(h)} grazes ahead. The wind blows from the {WIND_NAME[w.wind]}.', 'info')
    hunted(game, h.x, h.y)
    if h.great:
        h.rest = 3
    else:
        herds(game).remove(h)
    from . import guide as GD
    GD.tip(game, 'hunt')
    return 1


def small(game, m):
    """Small game about the hunting ground: a hare in the grass, a grouse in the heather."""
    from . import cooking as CK
    from . import zones as ZN
    from .entities import make_monster
    lands = CK.here_lands(game)
    kinds = [CK.SMALL_GAME[l][0] for l in lands if l in CK.SMALL_GAME]
    if any(l in ('tundra', 'taiga') for l in lands):
        kinds += ['fox', 'ermine']
    if not kinds:
        return
    p = game.player
    for _ in range(random.randint(1, 3)):
        x, y = ZN.free_near(game, m, p.x + random.randint(-14, 14), p.y + random.randint(-10, 10))
        if abs(x - p.x) + abs(y - p.y) < 6:
            continue
        o = make_monster(game, random.choice(kinds), x, y, 1)
        o.prey, o.awake, o.ps = -1, True, 'graze'
        m.mons.append(o)


def wind_arrow(game):
    """On the hunting ground: (glyph, side) of the arrow at the edge the wind comes from, or None."""
    m = game.map
    if getattr(m, 'hunt', None) is None or not any(getattr(o, 'prey', None) is not None for o in m.mons):
        return None
    w = getattr(game.world, 'wind', 0)
    return ARROW[w], WIND[w]


def _cover(game, x, y):
    m = game.map
    return sum(1 for dx in (-1, 0, 1) for dy in (-1, 0, 1)
               if m.inb(x + dx, y + dy) and m.tile(x + dx, y + dy) in COVER)


def notices(game, o, d):
    """Does this animal notice you? Sight (closer, more open: sooner) and smell (downwind of you)."""
    from . import lifeskills as LS
    p = game.player
    r = LS.rank(game, 'hunting')
    t = o.tpl
    sight = 11 - min(5, _cover(game, p.x, p.y) * 2) - r // 6 + (3 if t.get('skittish') else 0)
    if d <= max(2, sight) and random.random() < (.6 if getattr(o, 'lead', False) else .25):
        return True
    wx, wy = WIND[getattr(game.world, 'wind', 0)]
    ax, ay = o.x - p.x, o.y - p.y
    down = -(ax * wx + ay * wy)                 # how far downwind of you it stands
    if down > 0 and down * down >= .5 * (ax * ax + ay * ay) and d <= 16 - r // 5:
        return True
    return False


def alarm(game, hid, why=None):
    m = game.map
    for o in m.mons:
        if getattr(o, 'prey', None) == hid and o.ps in ('graze', 'alert'):
            o.ps = 'flee'
    if why:
        game.msg(why, 'info')


def on_noise(game):
    """You attacked or shot: every animal near takes fright."""
    from .worldgen import cheb
    m, p = game.map, game.player
    for o in list(m.mons):
        if getattr(o, 'prey', None) is not None and o.ps == 'graze' and cheb(o.x, o.y, p.x, p.y) <= 15:
            o.ps = 'flee'


def prey_turn(game, o):
    """An animal's turn on the hunting ground."""
    from . import ai as AI
    from .dress import add_blood
    from .worldgen import cheb
    m, p = game.map, game.player
    t = o.tpl
    d = cheb(o.x, o.y, p.x, p.y)
    if o.hp < o.maxhp and o.ps != 'charge':
        o.ps = 'flee'
        alarm(game, o.prey)
        on_noise(game)
        if not getattr(o, 'dying', 0) and o.hp < o.maxhp * .6 and not t.get('small'):
            o.dying = random.randint(3, 6)
            game.msg(f'{o.the().capitalize()} is hit and bolts, leaving blood.', 'info')
    if getattr(o, 'dying', 0):
        add_blood(m, o.x, o.y, 0)
        o.dying -= 1
        if o.dying <= 0:
            game.msg(f'{o.the().capitalize()} stumbles and falls.', 'good')
            game.kill(o)
            return
        AI.step_away(game, o)
        return
    if o.ps == 'graze':
        if notices(game, o, d):
            o.ps = 'alert'
            if getattr(o, 'lead', False) and game.visible(o.x, o.y):
                game.msg(f'{o.the().capitalize()} lifts its head and stares your way.', 'info')
            return
        if random.random() < .15:
            game.random_step(o)
        return
    if o.ps == 'alert':
        if (t.get('charge') or o.k == 'boar') and d <= 6 and getattr(o, 'lead', False):
            o.ps, o.charge = 'charge', 8
            game.msg(f'{o.the().capitalize()} lowers its head and charges!', 'bad')
            return
        alarm(game, o.prey, 'The herd takes fright and runs!' if getattr(o, 'lead', False) and o.prey != -1 else None)
        o.ps = 'flee'
        return
    if o.ps == 'charge':
        o.charge = getattr(o, 'charge', 0) - 1
        if o.charge <= 0 or o.hp < o.maxhp * .4:
            o.ps = 'flee'
            return
        if d <= 1:
            if random.random() < game.mon_hit_chance(o, game.stats()['def']):
                game.hurt(random.randint(*o.dmg) * 1.3, o.name)
            else:
                game.msg(f'{o.the().capitalize()} thunders past you.', 'info')
            return
        game.step_toward(o)
        return
    # fleeing
    if d <= 1 and t.get('kick') and random.random() < .5:
        game.msg(f'{o.the().capitalize()} kicks out at you!', 'bad')
        if random.random() < game.mon_hit_chance(o, game.stats()['def']):
            game.hurt(random.randint(*o.dmg), o.name)
        return
    steps = 2 if (t.get('fast') or t.get('far')) and game.turn % 2 == 0 else 1
    for _ in range(steps):
        if not AI.step_away(game, o):
            game.random_step(o)
    if t.get('rocks') and any(m.inb(o.x + dx, o.y + dy) and m.tile(o.x + dx, o.y + dy) in (D.ROCK, D.MOUNTAIN)
                              for dx in (-1, 0, 1) for dy in (-1, 0, 1)) and random.random() < .3:
        m.mons.remove(o)
        return
    if min(o.x, o.y, m.w - 1 - o.x, m.h - 1 - o.y) <= 1 or (d > 30 and not game.visible(o.x, o.y)):
        m.mons.remove(o)                        # gone over the hill


# ------------------------------------------------------------------ carcasses and skinning
# monster: meat, cuts (lo, hi), hide name, hide worth (silver, a good hide), parts [(part, chance)], fur, size (leather)
SKINS = {
    'red_deer': ('venison', (2, 3), 'Deer Hide', 3, [('antlers', .4)], False, 2),
    'elk': ('elk_meat', (3, 4), 'Elk Hide', 4, [('antlers', .5)], False, 3),
    'reindeer': ('reindeer_meat', (2, 3), 'Reindeer Hide', 4, [('antlers', .5)], False, 2),
    'aurochs': ('aurochs_meat', (4, 5), 'Aurochs Hide', 6, [('horn', .6)], False, 4),
    'wild_horse': ('horse_meat', (3, 3), 'Horse Hide', 3, [], False, 3),
    'ibex': ('ibex_meat', (2, 2), 'Ibex Hide', 3, [('horn', .6)], False, 2),
    'wild_goat': ('mutton', (2, 2), 'Goat Hide', 2, [('horn', .3)], False, 1),
    'gazelle': ('gazelle_meat', (2, 2), 'Gazelle Hide', 3, [('horn', .4)], False, 1),
    'wildebeest': ('wildebeest_meat', (3, 3), 'Wildebeest Hide', 3, [('horn', .4)], False, 3),
    'forest_hog': ('hog_meat', (2, 3), 'Hog Hide', 2, [('tusks', .5)], False, 2),
    'bighorn': ('bighorn_meat', (2, 2), 'Bighorn Hide', 3, [('horn', .7)], False, 2),
    'heath_sheep': ('mutton', (2, 2), 'Sheepskin', 3, [], False, 1),
    'hare': ('hare_meat', (1, 1), 'Hare Pelt', 1, [], False, 0),
    'snow_hare': ('hare_meat', (1, 1), 'Snow Hare Pelt', 2, [], True, 0),
    'desert_hare': ('hare_meat', (1, 1), 'Hare Pelt', 1, [], False, 0),
    'black_grouse': ('grouse', (1, 1), None, 0, [('feathers', .8)], False, 0),
    'ptarmigan': ('ptarmigan', (1, 1), None, 0, [('feathers', .8)], False, 0),
    'quail': ('quail', (1, 1), None, 0, [('feathers', .5)], False, 0),
    'guinea_fowl': ('guinea_fowl', (1, 1), None, 0, [('feathers', .8)], False, 0),
    'duck': ('duck', (1, 1), None, 0, [('feathers', .8)], False, 0),
    'fox': (None, (0, 0), 'Fox Fur', 12, [], True, 0),
    'ermine': (None, (0, 0), 'Ermine Fur', 20, [], True, 0),
    # the beasts you fight: a beast has a hide, not a sword
    'boar': ('boar_meat', (2, 3), 'Boar Hide', 3, [('tusks', .5)], False, 2),
    'wolf': ('meat', (1, 2), 'Wolf Pelt', 6, [('fangs', .3)], True, 1),
    'winter_wolf': ('meat', (1, 2), 'Winter Wolf Pelt', 15, [('fangs', .3)], True, 1),
    'worg': ('meat', (1, 2), 'Worg Pelt', 6, [('fangs', .4)], True, 2),
    'brown_bear': ('meat', (3, 4), 'Bear Fur', 18, [('claws', .5)], True, 3),
    'cave_bear': ('meat', (3, 5), 'Cave Bear Fur', 20, [('claws', .6)], True, 4),
    'crocodile': ('meat', (2, 3), 'Crocodile Hide', 14, [('fangs', .3)], False, 2),
    'panther': ('meat', (1, 2), 'Panther Pelt', 14, [('claws', .4)], True, 1),
    'sabretooth': ('meat', (2, 3), 'Sabretooth Pelt', 20, [('fangs', .8)], True, 2),
    'snow_ape': ('meat', (2, 3), 'Snow Ape Fur', 12, [], True, 2),
    'mammoth': ('meat', (5, 7), 'Mammoth Hide', 10, [('ivory', .8)], False, 5),
    'rhino': ('meat', (4, 5), 'Rhino Hide', 8, [('horn', .7)], False, 4),
    'hyena': ('meat', (1, 2), 'Hyena Pelt', 2, [], False, 1),
    'jackal': ('meat', (1, 1), 'Jackal Pelt', 1, [], False, 0),
    'badger': ('meat', (1, 1), 'Badger Pelt', 3, [], True, 0),
    'constrictor': ('meat', (1, 2), 'Snakeskin', 6, [], False, 1),
    'cobra': (None, (0, 0), 'Snakeskin', 4, [('fangs', .5)], False, 0),
    'giant_frog': ('frog_legs', (2, 2), None, 0, [], False, 0),
    'drake': ('meat', (2, 3), 'Drake Hide', 25, [('claws', .5), ('drake_egg', .1)], False, 2),
    'frost_drake': ('meat', (2, 3), 'Frost Drake Hide', 28, [('claws', .5), ('drake_egg', .1)], False, 2),
    'swamp_drake': ('meat', (2, 3), 'Swamp Drake Hide', 22, [('claws', .5), ('drake_egg', .1)], False, 2),
}
PARTS = {'antlers': ('Antlers', 4), 'horn': ('Horn', 3), 'tusks': ('Tusks', 4), 'feathers': ('Bunch of Feathers', .5),
         'claws': ('Claws', 3), 'fangs': ('Fangs', 3), 'ivory': ('Ivory', 30)}
QUALITY = ['Torn', 'Rough', 'Good', 'Fine']
Q_MULT = [.3, .6, 1, 1.5]
CARCASS_COL = (190, 120, 100)


def carcass(game, mon):
    """What a prey animal or a skinnable beast leaves: a carcass to skin (never picked up). True if it left one."""
    if mon.k not in SKINS:
        return False
    from .entities import Item
    it = Item(game.new_id(), 'carcass', mon.k)
    it.fg = mon.tpl['fg']
    game.spill(game.map, mon.x, mon.y, it)
    it.x, it.y = mon.x, mon.y
    return True


def carcass_here(game):
    p, m = game.player, game.map
    return next((i for i in m.items if i.k == 'carcass' and (i.x, i.y) == (p.x, p.y)), None)


def has_knife(game):
    p = game.player
    if any(i.k == 'tool' and i.t == 'knife' for i in p.inv):
        return True
    w = game.eq_item('weapon')
    return bool(w and D.BASES[w.base].get('family') == 'dagger') or any(
        i.k == 'gear' and D.BASES[i.base].get('family') == 'dagger' for i in p.inv)


def skin(game, it):
    """Skin the carcass you stand on."""
    from . import lifeskills as LS
    from .entities import Item
    from .hunger import make_food
    m = game.map
    if game.hostile_visible() and any(getattr(o, 'prey', None) is None for o in game.visible_hostiles()):
        game.msg('Not with enemies about!', 'bad')
        return 0
    meat, cuts, hide, worth, parts, fur, size = SKINS[it.t]
    name = D.MONSTERS[it.t]['name'].lower()
    m.items.remove(it)
    got = []
    if not has_knife(game):
        if meat:
            n = max(1, cuts[0] - 1)
            add(game, make_food(game, 'meat', n))
            got.append(f'{n} Raw Meat')
        game.msg(f'Without a knife you tear what meat you can from the {name}' + (f': {got[0]}.' if got else ', and get nothing.')
                 + ' A knife or a dagger would give you the hide as well.', 'info')
        return 10
    r = LS.rank(game, 'skinning')
    if meat:
        n = random.randint(*cuts) + (1 if r >= 15 and cuts[1] >= 2 else 0)
        f = make_food(game, meat, n)
        add(game, f)
        got.append(f.display_name())
    if hide:
        q = max(0, min(3, int(random.random() * 2 + r / 7 + (.6 if r >= 3 else 0))))
        h = Item(game.new_id(), 'hide', it.t)
        h.q, h.state, h.until = q, 'fresh', game.day + 2
        add(game, h)
        got.append(display(game, h))
    for part, ch in parts:
        if random.random() < ch + r * .01:
            if part == 'drake_egg':
                add(game, make_food(game, 'drake_egg'))
                got.append('a Drake Egg')
            else:
                pt = Item(game.new_id(), 'part', part)
                add(game, pt)
                got.append(PARTS[part][0])
    LS.gain(game, 'skinning', 1 + size * .5)
    game.msg(f'You skin the {name}: ' + ', '.join(got) + '.' if got else f'There is nothing worth taking on the {name}.', 'good')
    return 10 + size * 5


def add(game, it):
    if not game.add_to_inv(it):
        p = game.player
        game.spill(game.map, p.x, p.y, it)


# ------------------------------------------------------------------ hides: salting, tanning, rotting
def spoil(game):
    """Each morning: fresh hides and dishes go off, tanning hides become leather."""
    p = game.player
    for it in list(p.inv):
        until = getattr(it, 'until', None)
        if it.k == 'hide' and it.state == 'tanning' and game.day >= it.until:
            p.inv.remove(it)
            n = pieces(it)
            from .entities import Item
            if n:
                add(game, Item(game.new_id(), 'leather', 'leather', n))
            game.msg(f'The {SKINS[it.t][2].lower()} has tanned: {n} pieces of leather.' if n else
                     f'The {SKINS[it.t][2].lower()} was too torn: it tans into nothing worth having.', 'good')
        elif until is not None and game.day >= until and it.k in ('hide', 'dish', 'food'):
            if it.k == 'hide' and it.state != 'fresh':
                continue
            p.inv.remove(it)
            what = display(game, it).split(' (')[0] if it.k == 'hide' else it.display_name()
            game.msg({'hide': f'The {what.lower()} has rotted. You throw it away.',
                      'dish': f'The {what.lower()} has gone bad. You throw it away.'}.get(it.k,
                                                                                   f'The {what.lower()} has gone off.'), 'bad')


def pieces(it):
    size = SKINS[it.t][6]
    return max(0, round(size * Q_MULT[it.q] + (.4 if it.q >= 2 else 0))) if size else (1 if it.q >= 2 else 0)


def display(game, it):
    if it.k == 'carcass':
        return f'Carcass of a {D.MONSTERS[it.t]["name"]}'
    if it.k == 'part':
        return (f'{it.n}x ' if it.n > 1 else '') + PARTS[it.t][0]
    if it.k == 'leather':
        return f'{it.n} pieces of Leather' if it.n > 1 else 'Piece of Leather'
    name = SKINS[it.t][2]
    q = QUALITY[it.q]
    if it.state == 'salted':
        return f'Salted {name} ({q.lower()})'
    if it.state == 'tanning':
        left = max(1, it.until - game.day) if game else '?'
        return f'Tanning {name} ({left} day{"s" if left != 1 else ""})'
    left = max(0, it.until - game.day) if game else 2
    return f'Fresh {name} ({q.lower()}, {left} day{"s" if left != 1 else ""})' if left else f'Fresh {name} ({q.lower()}, rotting)'


def lines(game, it):
    if it.k == 'carcass':
        return ['Stand on it and press Enter to skin it. A knife or a dagger gives the hide as well as the meat.']
    if it.k == 'part':
        return ['Traders buy it.']
    if it.k == 'leather':
        return ['Leather, tanned and ready. Work it at a workbench: armour, gloves, boots, a belt, a waterskin.']
    out = []
    if it.state == 'fresh':
        out.append('A fresh hide rots in two days. Salt it on a stretching frame to keep it, or bring it to a tanner.')
    elif it.state == 'salted':
        out.append('Salted: it keeps. A tanner makes leather of it, or rub oak bark in it and let it tan in your pack.')
    else:
        out.append('It is tanning in your pack.')
    if SKINS[it.t][5]:
        out.append('Fine fur: it fetches much more in the cities and the cold north.')
    return out


def value(game, it):
    """In silver."""
    if it.k == 'carcass':
        return 0
    if it.k == 'part':
        return PARTS[it.t][1]
    if it.k == 'leather':
        return 1.5
    v = SKINS[it.t][3] * Q_MULT[it.q] * (1.25 if it.state == 'salted' else 1)
    if SKINS[it.t][5] and game is not None:
        here = game.here
        cold = False
        try:
            from .weather import climate
            x, y = game.world_pos()
            cold = climate(game.world, game.world.region_at(x, y).id) == 'cold'
        except Exception:
            pass
        if (here is not None and here.is_city) or cold:
            v *= 1.6
    return round(v, 2)


def glyph(it):
    return {'carcass': '%', 'part': '\'', 'leather': '=', 'hide': '='}[it.k]


def color(it):
    if it.k == 'carcass':
        return getattr(it, 'fg', CARCASS_COL)
    if it.k == 'part':
        return (226, 214, 180)
    if it.k == 'leather':
        return (176, 120, 70)
    return {'fresh': (200, 140, 110), 'salted': (220, 200, 170), 'tanning': (170, 120, 80)}.get(it.state, (190, 150, 110))


def use(game, it):
    """Using a hide or the frame from your pack."""
    p = game.player
    if it.k == 'tool' and it.t == 'frame':
        return set_frame(game, it)
    if it.k == 'hide' and it.state == 'salted':
        bark = next((i for i in p.inv if i.k == 'plant' and i.t == 'oak_bark'), None)
        if not bark:
            game.msg('A salted hide. A tanner makes leather of it; or you could tan it yourself with oak bark.', 'info')
            return 0
        game.remove_one(bark)
        it.state, it.until = 'tanning', game.day + 5
        game.msg(f'You rub the oak bark into the {SKINS[it.t][2].lower()} and roll it up. It will tan in your pack: five days.',
                 'good')
        from . import lifeskills as LS
        LS.gain(game, 'leatherworking', 1)
        return 20
    if it.k == 'hide':
        game.msg('A fresh hide. Salt it on a stretching frame before it rots, or bring it to a tanner.', 'info')
    return 0


def set_frame(game, it):
    m, p = game.map, game.player
    if m.kind not in ('wild', 'dungeon') or getattr(m, 'deck', False):
        game.msg('Set the frame up on open ground: out in the land, not on the world map or in a town.' if m.kind == 'over'
                 else 'There is no room to set up the frame here.', 'info')
        return 0
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)):
        x, y = p.x + dx, p.y + dy
        if m.inb(x, y) and D.TILES[m.tile(x, y)].walk and m.tile(x, y) not in (D.DOWN, D.UP, D.ENTR, D.WATER) \
                and not m.mon_at(x, y) and not any(i.x == x and i.y == y for i in m.items):
            p.inv.remove(it)
            m.set(x, y, D.FRAME)
            game.msg('You set up the stretching frame beside you. Walk into it to salt your hides.', 'good')
            return 10
    game.msg('There is no room to set up the frame here.', 'info')
    return 0


def frame(game, x, y):
    """Walking into a stretching frame: salt the fresh hides; with none, pack the frame up (your own frame only)."""
    from . import lifeskills as LS
    from .entities import Item
    m, p = game.map, game.player
    fresh = [i for i in p.inv if i.k == 'hide' and i.state == 'fresh']
    salt = sum(i.n for i in p.inv if i.k == 'food' and i.t == 'salt')
    town = m.kind == 'town'
    if fresh and not salt:
        game.msg('You need salt to cure the hides: a bag of salt from any outfitter.', 'bad')
        return 0
    if fresh:
        done = 0
        for h in fresh[:salt]:
            s = next(i for i in p.inv if i.k == 'food' and i.t == 'salt')
            game.remove_one(s)
            h.state, h.until = 'salted', None
            done += 1
            LS.gain(game, 'skinning', 1)
        game.msg(f'An hour of scraping and salting: {done} salted hide{"s" if done > 1 else ""}. They will keep now.', 'good')
        return 60
    if town:
        game.msg('A hide stretched on a frame, half scraped. It smells.')
        return 0
    m.set(x, y, getattr(m, 'base', None) and m.base[y * m.w + x] or D.GRASS)
    add(game, Item(game.new_id(), 'tool', 'frame'))
    game.msg('You take down the stretching frame and pack it.')
    return 5


# ------------------------------------------------------------------ the tanner and the workbench
TAN_FEE = 30            # copper per hide
SALT_FEE = 10


def talk_tanner(game, npc):
    from . import events as EV
    from .money import fmt
    p, s = game.player, game.here
    sid = s.id if s else 0
    waiting = game.world.__dict__.setdefault('tanning', {}).get(sid, [])
    ready = [w for w in waiting if w[0] <= game.day]
    hides = [i for i in p.inv if i.k == 'hide' and i.state in ('fresh', 'salted')]
    opts = []
    if ready:
        opts.append((f'Collect your leather ({sum(w[1] for w in ready)} pieces)', 'collect'))
    if hides:
        fee = sum(TAN_FEE + (SALT_FEE if h.state == 'fresh' else 0) for h in hides)
        opts.append((f'Have your {len(hides)} hide{"s" if len(hides) > 1 else ""} tanned ({fmt(fee)})', 'tan')
                    if p.gold >= fee else (f'Have your hides tanned ({fmt(fee)}): you cannot pay', None))
    opts.append(('Leave', 'leave'))
    later = [w for w in waiting if w[0] > game.day]
    text = '"Hides, leather, a bench to work it on. What have you brought me?"'
    if later:
        d = min(w[0] for w in later) - game.day
        text += f'\n\n"Yours is still in the pit. Come back in {d} day{"s" if d != 1 else ""}."'
    EV.ask(game, 'tanner', npc.name, text, opts, sid=sid)


def r_tanner(game, choice, ctx):
    from .entities import Item
    from .money import fmt
    p = game.player
    sid = ctx.get('sid', 0)
    tan = game.world.__dict__.setdefault('tanning', {})
    if choice == 'collect':
        waiting = tan.get(sid, [])
        ready = [w for w in waiting if w[0] <= game.day]
        n = sum(w[1] for w in ready)
        tan[sid] = [w for w in waiting if w[0] > game.day]
        if n:
            add(game, Item(game.new_id(), 'leather', 'leather', n))
        game.msg(f'The tanner hands you {n} pieces of good leather.' if n else 'The hides were too torn: nothing came of them.',
                 'good')
    elif choice == 'tan':
        hides = [i for i in p.inv if i.k == 'hide' and i.state in ('fresh', 'salted')]
        fee = sum(TAN_FEE + (SALT_FEE if h.state == 'fresh' else 0) for h in hides)
        if p.gold < fee or not hides:
            return
        p.gold -= fee
        n = sum(pieces(h) for h in hides)
        for h in hides:
            p.inv.remove(h)
        tan.setdefault(sid, []).append((game.day + 3, n))
        game.msg(f'You pay {fmt(fee)}. "Three days. Come back for it; I do not keep it forever."', 'gold')


# what the bench makes: key -> (name, leather, kind, base or tool)
MAKE = {
    'armour': ('Leather Armor', 4, 'gear', 'leather'), 'gloves': ('Leather Gloves', 1, 'gear', 'gloves'),
    'boots': ('Leather Boots', 2, 'gear', 'boots'), 'belt': ('Belt', 1, 'gear', 'belt'),
    'waterskin': ('Waterskin', 1, 'tool', 'waterskin'),
}
BENCH_FEE = 20


def bench(game, x, y):
    from . import events as EV
    from . import lifeskills as LS
    from .money import fmt
    p = game.player
    have = sum(i.n for i in p.inv if i.k == 'leather')
    opts = []
    for k, (name, need, kind, base) in MAKE.items():
        ok = have >= need and p.gold >= BENCH_FEE
        if kind == 'tool' and any(i.k == 'tool' and i.t == base for i in p.inv):
            continue
        opts.append((f'{name}: {need} leather', f'make:{k}') if ok else (f'{name}: {need} leather (you have {have})', None))
    opts.append(('Leave', 'leave'))
    r = LS.rank(game, 'leatherworking')
    EV.ask(game, 'bench', 'The workbench', f'Awls, needles, waxed thread and a heavy knife. The use of the bench costs '
           f'{fmt(BENCH_FEE)}.' + (f'\n\nLeatherworking {r}.' if r else ''), opts)


def r_bench(game, choice, ctx):
    from . import lifeskills as LS
    from .entities import Item, make_gear
    if not choice or not choice.startswith('make:'):
        return
    p = game.player
    name, need, kind, base = MAKE[choice[5:]]
    leather = [i for i in p.inv if i.k == 'leather']
    if sum(i.n for i in leather) < need or p.gold < BENCH_FEE:
        return
    p.gold -= BENCH_FEE
    left = need
    for it in leather:
        take = min(it.n, left)
        it.n -= take
        left -= take
        if it.n <= 0:
            p.inv.remove(it)
    r = LS.rank(game, 'leatherworking')
    if kind == 'tool':
        add(game, Item(game.new_id(), 'tool', base))
        game.msg(f'You stitch a {name.lower()}.', 'good')
    else:
        it = make_gear(game, base, 'normal', max(1, game.player.lvl))
        if it.arm:
            it.arm = round(it.arm * (1 + r * .02))
        if getattr(it, 'mdur', 0):
            it.mdur = it.dur = round(it.mdur * (1 + r * .02))
        it.name = ('Fine ' if r >= 15 else '') + it.name
        add(game, it)
        game.msg(f'You cut, stitch and rivet: {it.name}.', 'good')
    LS.gain(game, 'leatherworking', 2 + need)
    game.end_turn(30 + need * 10)


def furnish(game, m, s):
    """A town's tanner, with a frame and a workbench, in the stables or the outfitter's; a hearth in the inn."""
    from .entities import make_npc
    from .towns import free_inside
    if s is None or getattr(s, 'kind', '') in ('hamlet', 'deephold') or not getattr(m, 'buildings', None):
        return
    for b in m.buildings:
        pl = b.get('plot')
        if b['kind'] == 'inn' and pl is not None:
            spots = [c for c in free_inside(m, pl) if c[1] == pl.y + pl.h - 2 and abs(c[0] - (pl.x + pl.w // 2)) <= 2]
            if spots:
                m.set(spots[0][0], spots[0][1], D.HEARTH)
    shop = next((b for b in m.buildings if b['kind'] == 'stables'), None) or \
        next((b for b in m.buildings if b['kind'] == 'shop'), None)
    if shop is None or shop.get('plot') is None:
        return
    pl = shop['plot']
    spots = [c for c in free_inside(m, pl) if not m.mon_at(*c)]
    if len(spots) < 3:
        return
    door = shop.get('door')
    spots.sort(key=lambda c: -abs(c[1] - door[1]) - abs(c[0] - door[0]) if door else 0)
    m.set(spots[0][0], spots[0][1], D.BENCH)
    m.set(spots[1][0], spots[1][1], D.FRAME)
    c = spots[-1]
    from .towns import town_names
    nm = (town_names(getattr(s, 'race', 'human')) or ['Hesk'])[0]
    m.mons.append(make_npc(game, f'{nm.split()[0]} the Tanner', 'tanner', '#b08860', c[0], c[1], True))


def register():
    from . import events as EV
    EV.RESOLVERS['tanner'] = r_tanner
    EV.RESOLVERS['bench'] = r_bench


register()
