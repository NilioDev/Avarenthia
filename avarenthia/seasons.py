"""The year on the world map. Snow comes down from the north and the heights in winter and draws back in spring;
lakes and rivers freeze (a short cut, until the thaw makes the ice thin and the fords run high); passes fill with
snow; broadleaf woods turn gold and red, then stand bare; pack ice grows along the northern coast; beasts leave
tracks in the snow; the dirt roads turn to mud in spring; small streams run dry late in summer and a fire can run
through the dry grass; berries and mushrooms wait to be picked in autumn; on Midsummer night fires burn on the hills.
Everything here is worked out from the day and the land, so little is saved: the fires, the burnt land, the tracks
and what you picked."""
import math
import random

from . import calendar as CAL
from . import data as D
from .look import _h

YEAR_LEN = CAL.DAYS_IN_MONTH * 12
MIDSUMMER = 5 * CAL.DAYS_IN_MONTH + 14          # the 15th of Highsun
# how deep the snow lies through the year: (day of the year, depth 0..1); the year starts on the 1st of Deepfrost
SNOW = [(0, .9), (15, 1.0), (30, .9), (60, .4), (90, .1), (120, 0), (285, 0), (300, .15), (330, .45), (360, .9)]
NO_SNOW = {'desert', 'savanna', 'jungle', 'badlands', 'salt', 'volcano', 'hotpool', 'geyser', 'sinter', 'oasis',
           'mangrove', 'mesa', 'canyon', 'crater_isle', 'chasm'}
BROADLEAF = {'forest', 'deep_forest', 'dry_forest', 'birch'}
SEA = {'ocean', 'sea', 'shallows'}
FREEZES = {'lake', 'river', 'marsh', 'swamp'}
GRASSLAND = {'steppe', 'savanna', 'meadow', 'shrubland'}
LEAVES = [(214, 170, 52), (196, 84, 40), (226, 128, 44), (180, 140, 50)]
SNOW_FG, SNOW_BG = (222, 228, 238), (62, 68, 80)
ICE_FG, ICE_BG = (196, 224, 244), (64, 90, 116)


def doy(day):
    return (CAL.START + day - 1) % YEAR_LEN


def year(day):
    return (CAL.START + day - 1) // YEAR_LEN


def depth(day):
    d = doy(day)
    for (a, va), (b, vb) in zip(SNOW, SNOW[1:]):
        if a <= d < b:
            return va + (vb - va) * (d - a) / (b - a)
    return SNOW[-1][1]


def sun(day):
    """1 at midsummer, -1 at midwinter."""
    return math.cos(2 * math.pi * (doy(day) - MIDSUMMER) / YEAR_LEN)


def dusk(day):
    """The hour the light starts to go: earlier in winter, later in summer."""
    return 18 + 1.5 * sun(day)


def dawn(day):
    return 5 - 1.5 * sun(day)


class Now:
    """The season as the world map needs it, worked out once per frame or step."""

    def __init__(self, game):
        day = game.day
        self.day, self.doy, self.year = day, doy(day), year(day)
        self.depth = depth(day)
        d = self.doy
        self.thaw = 30 <= d < 58 and self.depth > .3              # the ice still holds, but thinly
        self.spate = 40 <= d < 80                                   # meltwater: the northern fords run high
        self.mud = 45 <= d < 100
        self.drought = 200 <= d < 256
        self.fire_season = 180 <= d < 260
        self.autumn = 270 <= d < 330                                # leaves turning; berries and mushrooms
        self.leaf = min(1.0, max(0.0, (d - 270) / 25)) if self.autumn else 0.0
        self.bare = d >= 322 or d < 75
        from .towns import is_night
        self.midsummer = d == MIDSUMMER and is_night(game)
        self.winter = CAL.season(day) == 'winter'


# ------------------------------------------------------------------ the land, cached per map (never saved)
def cold(m):
    """How cold each cell of the world map is, 0 (warm south, low land) to about 1.4 (the far north, the peaks)."""
    c = getattr(m, '_cold', None)
    if c is not None:
        return c
    elev = getattr(m, 'elev', None)
    c = []
    for i in range(m.w * m.h):
        lat = (i // m.w) / m.h
        e = elev[i] / 255 if elev else .4
        c.append(max(0.0, (.55 - lat) / .55) * .8 + max(0.0, e - .45) * 1.6)
    m._cold = c
    return c


def biome(m, i):
    b = getattr(m, 'biome', None)
    return m.biome_names[b[i]] if b else ''


def passes(m):
    """The narrow ways between the mountains: open ground with mountains crowding in on both sides."""
    ps = getattr(m, '_passes', None)
    if ps is not None:
        return ps
    ps = set()
    if m.kind == 'over':
        elev = getattr(m, 'elev', None)
        for i, t in enumerate(m.t):
            if t in (D.MOUNTAIN, D.WATER, D.TOWN, D.CITY, D.ENTR) or not D.TILES[t].walk:
                continue
            if elev and elev[i] < 120:
                continue
            x, y = i % m.w, i // m.w
            if 0 < x < m.w - 1 and 0 < y < m.h - 1:
                mt = [m.t[(y + dy) * m.w + x + dx] == D.MOUNTAIN for dx, dy in
                      ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1))]
                if (mt[0] and mt[1]) or (mt[2] and mt[3]) or sum(mt) >= 5:
                    ps.add(i)
    m._passes = ps
    return ps


def snowy(m, i, st):
    b = biome(m, i)
    if b in NO_SNOW or b in SEA or m.t[i] in (D.WATER, D.RIVER):
        return False
    c = cold(m)[i]
    return c > 1.15 - st.depth or (c >= 1.25 and m.t[i] in (D.HILLS, D.MOUNTAIN))     # the heights keep theirs


def frozen(m, i, st):
    """Lakes, rivers and pools frozen hard enough to walk on."""
    if m.t[i] not in (D.WATER, D.RIVER) or st.depth <= .2:
        return False
    b = biome(m, i)
    return (b in FREEZES or m.t[i] == D.RIVER) and cold(m)[i] > 1.3 - st.depth


def thin(m, i, st):
    return st.thaw and frozen(m, i, st) and cold(m)[i] < 1.42 - st.depth


def pack(m, i, st):
    return st.depth > .3 and biome(m, i) in SEA and (i // m.w) < m.h * (st.depth - .3) * .2


def closed(m, i, st):
    return st.depth > .7 and i in passes(m) and snowy(m, i, st)


def spate(m, i, st):
    """A ford running high with meltwater: rivers that froze this winter."""
    return st.spate and m.t[i] == D.RIVER and not frozen(m, i, st) and cold(m)[i] > .45


def dry(m, i, st):
    """A small stream run dry: the upper course of a river in the warm half of the world."""
    if not st.drought or m.t[i] != D.RIVER or cold(m)[i] > .35:
        return False
    from .anim import flow
    return flow(m).get(i, 0) >= 10


def bare(m, i, st):
    return st.bare and biome(m, i) in BROADLEAF and m.t[i] == D.FOREST


def find(m, i, st, world):
    """Berries or mushrooms to pick here this autumn: 'berry', 'mushroom' or None."""
    if not st.autumn or m.t[i] not in (D.FOREST, D.GRASS):
        return None
    x, y = i % m.w, i // m.w
    r = _h(x, y, 900 + st.year)
    if r % 70:
        return None
    if (st.year, i) in getattr(world, 'picked', ()):
        return None
    return 'mushroom' if m.t[i] == D.FOREST and r % 140 else 'berry'


def bonfires(m):
    """The hilltops where the Midsummer fires burn: a few high points among the hills, cached on the map."""
    b = getattr(m, '_bonfires', None)
    if b is not None:
        return b
    b = []
    elev = getattr(m, 'elev', None)
    for i, t in enumerate(m.t):
        if t != D.HILLS or not elev:
            continue
        x, y = i % m.w, i // m.w
        if _h(x, y, 61) % 9:
            continue
        if all(not m.inb(x + dx, y + dy) or elev[(y + dy) * m.w + x + dx] <= elev[i]
               for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2)):
            b.append(i)
    m._bonfires = b
    return b


# ------------------------------------------------------------------ how it looks
def look(game, m, i, lk, st, t=0.0):
    """The look of world-map cell i in this season (lk is its usual look). The season's own look is cached for the
    day; fires, burnt land, tracks and what is left to pick are laid over it."""
    w = game.world
    fires = getattr(w, 'fires', None)
    x, y = i % m.w, i // m.w
    if fires and i in fires:
        from .anim import flame
        f = flame(t, x, y)
        return ('^' if f > .82 else '*'), (255, int(150 * f), 40), (int(80 * f), 22, 6)
    burnt = getattr(w, 'burnt', None)
    if burnt and i in burnt and m.t[i] not in (D.ROAD, D.TOWN, D.CITY, D.WATER, D.RIVER):
        return (',' if _h(x, y, 5) % 3 else '.'), (74, 66, 58), (13, 11, 10)
    if getattr(m, '_sl_key', None) != st.day:
        m._sl, m._sl_key = {}, st.day
    v = m._sl.get(i)
    if v is None:
        v = m._sl[i] = _season_look(m, i, lk, st)
    out, snow = v
    if snow:
        tr = getattr(w, 'tracks', None)
        if tr and i in tr:
            return ':', (100, 104, 116), SNOW_BG
    elif st.autumn:
        kind = find(m, i, st, w)
        if kind:
            return ('∙', (210, 40, 70), out[2]) if kind == 'berry' else ('°', (226, 200, 160), out[2])
    return out


def _season_look(m, i, lk, st):
    """(look, lies under snow) for cell i on this day."""
    ch, fg, bg = lk
    tt = m.t[i]
    x, y = i % m.w, i // m.w
    if tt in (D.WATER, D.RIVER):
        if frozen(m, i, st):
            return (('·' if _h(x, y, 3) % 4 else '-'), ICE_FG, (ICE_BG if not thin(m, i, st) else (46, 70, 96))), False
        if pack(m, i, st):
            return (('▒' if _h(x, y, 4) % 3 else '░'), (220, 232, 244), (92, 110, 130)), False
        if dry(m, i, st):
            return ('·', (150, 130, 96), (16, 13, 9)), False
        if spate(m, i, st):
            return (ch, (150, 140, 110), (30, 26, 20)), False
        return lk, False
    if tt in (D.ROAD, D.TOWN, D.CITY, D.ENTR, D.CASTLE, D.FORT):
        return lk, False
    if closed(m, i, st):
        return ('▓', (240, 244, 250), (128, 134, 148)), False
    if snowy(m, i, st):
        if tt in (D.FOREST, D.TREE):
            tree = (118, 104, 92) if biome(m, i) in BROADLEAF else fg
            return (ch, _mix(tree, SNOW_FG, .3), SNOW_BG), True
        if tt in (D.HILLS, D.MOUNTAIN):
            return (ch, SNOW_FG, _mix(bg, SNOW_BG, .7)), True
        return (('·' if _h(x, y, 8) % 3 else "'"), SNOW_FG, SNOW_BG), True
    if tt == D.FOREST and biome(m, i) in BROADLEAF:
        if st.leaf > 0:
            return (ch, _mix(fg, LEAVES[_h(x, y, 12) % len(LEAVES)], st.leaf), bg), False
        if st.bare:
            return (ch, (118, 104, 92), bg), False
    return lk, False


def _mix(a, b, k):
    return (int(a[0] + (b[0] - a[0]) * k), int(a[1] + (b[1] - a[1]) * k), int(a[2] + (b[2] - a[2]) * k))


# ------------------------------------------------------------------ walking the land
def blocked(game, x, y):
    """A reason the season bars this world-map cell, or None. Frozen water is open (see walkable)."""
    m = game.maps['over']
    i = y * m.w + x
    st = Now(game)
    if i in getattr(game.world, 'fires', {}):
        return 'The grass is burning. You cannot go that way.'
    if closed(m, i, st):
        return 'Deep snow has closed the pass. It will not open before the thaw.'
    if spate(m, i, st):
        return 'The ford runs high and brown with meltwater. Nobody crosses it now.'
    return None


def walkable(game, x, y):
    """Water you can walk on now: frozen hard."""
    m = game.maps['over']
    return m.t[y * m.w + x] == D.WATER and frozen(m, y * m.w + x, Now(game))


def cost(game, c):
    """Snow off the road is slow going; spring mud slows the dirt roads; ice and dry beds are walked like land."""
    m, p = game.map, game.player
    if m.kind != 'over':
        return c
    i = p.y * m.w + p.x
    st = Now(game)
    t = m.t[i]
    if t in (D.WATER, D.RIVER) and (frozen(m, i, st) or dry(m, i, st)):
        return 12
    if t == D.ROAD:
        if st.mud and cold(m)[i] < .9 and not any(abs(s.x - p.x) <= 3 and abs(s.y - p.y) <= 3
                                                   for s in game.world.settlements):
            return round(c * 1.6)
        return c
    if snowy(m, i, st):
        return round(c * 1.4)
    return c


def sight(game, r):
    """Bare woods let you see one cell further."""
    m, p = game.map, game.player
    if m.kind == 'over' and bare(m, p.y * m.w + p.x, Now(game)):
        return r + 1
    return r


def on_step(game):
    """Thin ice, the mud, berries and mushrooms: what the season does when you step on a world-map cell."""
    m, p, w = game.map, game.player, game.world
    i = p.y * m.w + p.x
    st = Now(game)
    if thin(m, i, st):
        if getattr(game, 'ice_warned', None) != st.day:
            game.ice_warned = st.day
            game.msg('The ice creaks and cracks under you. It will not hold for long.', 'bad')
        elif random.random() < .35:
            dmg = max(3, p.life // 5)
            p.life -= dmg
            game.num(p.x, p.y, f'-{dmg}', (160, 210, 255))
            game.msg('The ice gives way! You go into the freezing water and drag yourself out, soaked and shaking.', 'bad')
            if p.life <= 0:
                game.die('the thin ice')
            return
    if st.mud and m.t[i] == D.ROAD and getattr(game, 'mud_told', None) != st.year and cost(game, 10) > 10:
        game.mud_told = st.year
        game.msg('The road is deep in mud with the thaw. Travel is slow.', 'info')
    kind = find(m, i, st, w)
    if kind:
        from . import foraging as FG
        if FG.pick_season(game, kind):
            w.picked = getattr(w, 'picked', set())
            w.picked.add((st.year, i))


def track(game, wd):
    """A beast on snow leaves its tracks behind."""
    m = game.maps['over']
    if not m.inb(wd.x, wd.y):
        return
    i = wd.y * m.w + wd.x
    st = Now(game)
    if st.depth > 0 and snowy(m, i, st):
        w = game.world
        w.tracks = getattr(w, 'tracks', {})
        w.tracks[i] = (st.day, wd.name)


def track_at(game, x, y):
    tr = getattr(game.world, 'tracks', {})
    m = game.maps['over']
    return tr.get(y * m.w + x)


# ------------------------------------------------------------------ the fires in the grass, and the year turning
def tick(game, turns):
    """Grass fires spread a little every hour."""
    w = game.world
    fires = getattr(w, 'fires', None)
    if not fires:
        return
    w.fire_acc = getattr(w, 'fire_acc', 0) + turns
    if w.fire_acc < D.DAY_LEN // 24:
        return
    w.fire_acc = 0
    m = game.maps['over']
    w.burnt = getattr(w, 'burnt', {})
    for i, left in list(fires.items()):
        x, y = i % m.w, i // m.w
        if len(fires) < 70:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                j = (y + dy) * m.w + x + dx
                if m.inb(x + dx, y + dy) and j not in fires and j not in w.burnt and m.t[j] == D.GRASS \
                        and biome(m, j) in GRASSLAND and random.random() < .3:
                    fires[j] = random.randint(2, 4)
        if left <= 1:
            del fires[i]
            w.burnt[i] = game.day
        else:
            fires[i] = left - 1
    p = game.player
    if game.cur == 'over' and p.y * m.w + p.x in fires:
        p.life -= 4
        game.msg('The fire is on you! You are burnt.', 'bad')
        if p.life <= 0:
            game.die('a grass fire')


def daily(game):
    w, m = game.world, game.maps['over']
    st = Now(game)
    # old tracks fill in
    if getattr(w, 'tracks', None):
        w.tracks = {i: v for i, v in w.tracks.items() if st.day - v[0] <= 2}
    # burnt land grows green again in spring
    if getattr(w, 'burnt', None) and CAL.season(st.day) == 'spring':
        for i in [i for i in w.burnt if random.random() < .15]:
            del w.burnt[i]
    if getattr(w, 'picked', None):
        w.picked = {k for k in w.picked if k[0] == st.year}
    # a fire in the dry grass, somewhere you might see it
    if st.fire_season and len(getattr(w, 'fires', {})) < 20 and random.random() < .2:
        p = game.player
        px, py = (p.x, p.y) if game.cur == 'over' else game.over_pos
        for _ in range(40):
            x, y = px + random.randint(-30, 30), py + random.randint(-20, 20)
            if not m.inb(x, y):
                continue
            i = y * m.w + x
            if m.t[i] == D.GRASS and biome(m, i) in GRASSLAND and cold(m)[i] < .4 and abs(x - px) + abs(y - py) > 6:
                w.fires = getattr(w, 'fires', {})
                w.fires[i] = 3
                break


def midsummer_note(game):
    """Once, when the Midsummer fires are lit."""
    st = Now(game)
    if st.midsummer and getattr(game, 'midsummer_told', None) != st.year and game.cur == 'over':
        game.midsummer_told = st.year
        game.msg('It is Midsummer night: fires burn on the hilltops as far as you can see.', 'gold')


def describe(game, x, y):
    """A line about what the season has done to this world-map cell, or None."""
    m, w = game.maps['over'], game.world
    i = y * m.w + x
    st = Now(game)
    if i in getattr(w, 'fires', {}):
        return 'The grass is burning.'
    if i in getattr(w, 'burnt', {}):
        return 'Burnt ground, black and bare. It will be green again in the spring.'
    if frozen(m, i, st):
        return 'Frozen over. The ice is thin and cracking.' if thin(m, i, st) else 'Frozen hard: you can walk across.'
    if pack(m, i, st):
        return 'Pack ice, grinding and white.'
    if dry(m, i, st):
        return 'A stream bed, run dry in the summer heat.'
    if spate(m, i, st):
        return 'The river runs high with meltwater. The ford is impassable.'
    if closed(m, i, st):
        return 'The pass lies deep in snow, shut until the thaw.'
    tr = track_at(game, x, y)
    if tr and snowy(m, i, st):
        return f'Tracks in the snow: {tr[1].lower()}, ' + ('fresh.' if tr[0] == st.day else 'a day or two old.')
    if snowy(m, i, st):
        return 'Under snow.'
    kind = find(m, i, st, w)
    if kind:
        return 'Ripe berries on the bushes. Walk over them to pick some.' if kind == 'berry' else \
            'Mushrooms in the leaf litter. Walk over them to pick some.'
    if bare(m, i, st):
        return 'The trees stand bare for the winter. You see a little further.'
    if st.leaf > 0 and biome(m, i) in BROADLEAF and m.t[i] == D.FOREST:
        return 'The leaves are turning gold and red.'
    return None


def bears_sleep(game, keys):
    """Bears sleep the winter through."""
    return CAL.season(game.day) == 'winter' and any('bear' in k for k in keys)


def herders_away(game):
    """The herders' huts on the high meadows stand empty in winter; the flocks are down by the villages."""
    return CAL.season(game.day) == 'winter'
