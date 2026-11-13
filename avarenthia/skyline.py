"""A first sight of a town: the first time you come to a settlement, one quiet card before its map, with its skyline
against the sky of that hour and season, drawn in half blocks from the settlement's own map (its wall and towers,
the gate, the temple's spire, the keep, the roofs, the mill; smoke from chimneys, lit windows at night), its name in
gold and one line (kind, land, lord). Once per settlement (`p.sights`); the journal's Places tab shows it again.

The picture is a grid of pixels (two to a cell, top and bottom of '▀'); `card(game, sid)` makes it, `draw` puts it on
a canvas. Not for dungeons and sites."""
import random

from . import data as D

CW, CH = 92, 22                      # the picture: cells across and down (two pixels a cell down)
PH = CH * 2
GROUND = PH - 5                      # the pixel row where the ground starts

WALLS = {0, 44, 49, 68, 129}         # tiles that are walls (a house's, the town's)
KINDS = {'gnomes': 'hamlet', 'hamlet': 'hamlet', 'village': 'village', 'town': 'town', 'city': 'city', 'metropolis': 'great city',
         'deephold': 'hold under the mountain', 'glade': 'glade', 'gnomes': 'hamlet'}
PEOPLE = {'human': 'human', 'dwarf': 'dwarf', 'elf': 'elven', 'halfling': 'halfling', 'orc': 'half-orc',
          'gnome': 'gnome', 'goblin': 'goblin', 'kobold': 'kobold', 'gnoll': 'gnoll', 'lizard': 'lizardfolk'}
TALL = {'temple': 9, 'keep': 12, 'barracks': 6, 'inn': 6, 'elder': 6, 'warehouse': 5, 'stables': 4, 'customs': 5,
        'harbourmaster': 6, 'keepsake': 6, 'shop': 5, 'home': 4}

# roof and wall colours by people (the roof, the wall below it)
LOOK = {'human': ((120, 58, 40), (150, 132, 110)), 'dwarf': ((92, 92, 100), (120, 112, 104)),
        'halfling': ((70, 112, 52), (130, 100, 64)), 'orc': ((96, 70, 44), (120, 92, 60)),
        'elf': ((60, 110, 70), (120, 130, 100)), 'gnome': ((140, 70, 60), (150, 130, 110)),
        'goblin': ((80, 70, 50), (100, 90, 70))}


def seen(p):
    if not hasattr(p, 'sights') or p.sights is None:
        p.sights = set()
    return p.sights


SITES = {'glade': 'elf', 'gnomes': 'gnome'}      # the peoples' own homes that are sites, not settlements (folk.py)


class Home:
    """A settlement or a people's home site, seen the same way."""
    def __init__(self, game, key):
        w = game.world
        self.key = key
        if key.startswith('site'):
            o = w.sites[int(key[4:])]
            self.kind, self.race, self.region = o.kind, SITES.get(o.kind, 'human'), None
        else:
            o = w.settlements[int(key[1:])]
            self.kind, self.race, self.region = o.kind, getattr(o, 'race', 'human') or 'human', o.region
        self.o, self.name, self.x, self.y, self.map_key = o, o.name, o.x, o.y, o.map_key
        self.id = o.id
        self.plundered = getattr(o, 'plundered', 0) > game.day or bool(getattr(o, 'harm', None))


def key_of(obj):
    return f'site{obj.id}' if obj.kind in SITES and not hasattr(obj, 'services') else f's{obj.id}'


def on_enter(game, obj):
    """The first time in a settlement (or an elven glade, a gnome hamlet): the card comes before its map
    (App.after_action shows it)."""
    sg = seen(game.player)
    k = key_of(obj)
    if k in sg:
        return False
    sg.add(k)
    game.first_sight = k
    return True


# ------------------------------------------------------------------ the sky
def _mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def sky_of(game):
    """(top colour, bottom colour, night, season) for the hour and the time of year."""
    from . import towns as TW, calendar as CAL
    from .seasons import dusk, dawn
    t = (game.turn % D.DAY_LEN) * 24 / D.DAY_LEN
    season = CAL.season(game.day)
    dk, dw = dusk(game.day), dawn(game.day)
    night = TW.is_night(game)
    if night:
        top, bot = (8, 10, 26), (22, 26, 52)
    elif dk <= t < dk + 3:                         # dusk: gold under, violet over
        top, bot = (52, 40, 86), (196, 116, 64)
    elif dw <= t < dw + 2:                         # dawn: rose under
        top, bot = (70, 86, 130), (210, 150, 120)
    else:
        top, bot = (58, 104, 168), (150, 186, 214)
    if season == 'winter' and not night:
        top, bot = _mix(top, (150, 156, 166), .45), _mix(bot, (206, 210, 214), .45)
    return top, bot, night, season


# ------------------------------------------------------------------ the picture
class Pic:
    def __init__(self, sky):
        top, bot = sky[0], sky[1]
        self.px = [[_mix(top, bot, y / (PH - 1)) for _x in range(CW)] for y in range(PH)]
        self.marks = {}                  # (cx, cy) -> (char, colour): smoke and stars over the pixels

    def set(self, x, y, c):
        if 0 <= x < CW and 0 <= y < PH:
            self.px[y][x] = c

    def rect(self, x0, y0, x1, y1, c):
        for y in range(max(0, y0), min(PH, y1 + 1)):
            for x in range(max(0, x0), min(CW, x1 + 1)):
                self.px[y][x] = c


def _structures(m):
    """(x, y, w, h, kind) of the buildings and homes on the settlement's map."""
    out = []
    for b in getattr(m, 'buildings', None) or []:
        x, y, w, h = b['box']
        out.append((x, y, w, h, b['kind'].split(':')[0]))
    for pl in getattr(m, 'homes', None) or []:
        out.append((pl.x, pl.y, pl.w, pl.h, 'home'))
    return out


def _count(m, tiles):
    return sum(1 for t in m.t if t in tiles)


def _free_walls(m, sts):
    """Wall tiles of the town itself (not of a house): the town wall."""
    inside = set()
    for x, y, w, h, _k in sts:
        for yy in range(y - 1, y + h + 1):
            for xx in range(x - 1, x + w + 1):
                inside.add(yy * m.w + xx)
    return sum(1 for i, t in enumerate(m.t) if t in WALLS and i not in inside)


def card(game, key):
    """The card of a settlement or a people's home: {'name', 'line', 'pic'} (pic a Pic)."""
    s = Home(game, key)
    sid = s.id + (5000 if key.startswith('site') else 0)
    m = game.maps.get(s.map_key)
    if m is None:
        if key.startswith('site'):
            from . import sites as ST
            m = game.maps[s.map_key] = ST.gen_site_map(game, s.o)
        else:
            from . import towns as TW
            m = game.maps[s.map_key] = TW.gen_settlement_map(game, s.o)
    sky = sky_of(game)
    night, season = sky[2], sky[3]
    pic = Pic(sky)
    rnd = random.Random(sid * 7919 + 13)
    race = s.race
    roof, wallc = LOOK.get(race, LOOK['human'])
    burnt = s.plundered
    if night:
        roof, wallc = _mix(roof, (10, 12, 24), .6), _mix(wallc, (10, 12, 24), .6)
    ground = {'winter': (200, 204, 210), 'autumn': (96, 82, 44)}.get(season, (58, 86, 44))
    if night:
        ground = _mix(ground, (8, 10, 20), .65)
    # stars and the moon at night
    if night:
        for _ in range(26):
            pic.marks[(rnd.randrange(CW), rnd.randrange(0, CH // 2))] = ('·', (150, 150, 180))
        pic.marks[(CW - 14, 2)] = ('○', (230, 226, 200))
    sts = _structures(m)
    kind = s.kind
    # the far land behind: mountains for dwarves, hills else
    far = _mix(sky[1], (40, 46, 60), .5)
    if race == 'dwarf' or kind == 'deephold' or _count(m, {16, 56}) > len(m.t) // 6:
        for _ in range(3):
            cx, hh = rnd.randrange(CW), rnd.randrange(12, 22)
            for dx in range(-hh * 2, hh * 2 + 1):
                top = GROUND - hh + abs(dx) // 2
                pic.rect(cx + dx, top, cx + dx, GROUND, _mix(far, (70, 70, 80), .3))
            if season == 'winter' or True:
                for dx in range(-3, 4):
                    pic.set(cx + dx, GROUND - hh + abs(dx) // 2, (220, 224, 230) if not night else (90, 94, 110))
    else:
        for x in range(CW):
            h = int(3 + 2 * abs(((x * 7 + sid) % 40) - 20) / 20)
            pic.rect(x, GROUND - h, x, GROUND, far)
    # trees: crowns among the houses (an elven glade is all trees)
    trees = 26 if kind == 'glade' or race == 'elf' else min(14, _count(m, {13}) // 30)
    green = (40, 84, 44) if season != 'autumn' else (150, 92, 36)
    if season == 'winter':
        green = (60, 70, 66)
    if night:
        green = _mix(green, (8, 10, 20), .6)
    for _ in range(trees):
        tx = rnd.randrange(CW)
        r = rnd.randrange(3, 7) if kind == 'glade' or race == 'elf' else rnd.randrange(2, 4)
        base = GROUND - rnd.randrange(0, 3)
        pic.rect(tx, base - r * 2, tx, base, _mix(green, (40, 30, 20), .5))
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy * 2 <= r * r:
                    pic.set(tx + dx, base - r * 2 + dy, green)
    # the houses, back to front: further ones higher and dimmer
    scale = CW / max(1, m.w)
    chimneys = []
    windows = []
    for x, y, bw, bh, k in sorted(sts, key=lambda st: st[1]):
        depth = 1 - y / max(1, m.h)               # 1 at the back, 0 at the front
        x0, x1 = int(x * scale), max(int(x * scale), int((x + bw) * scale) - 1)
        base = GROUND - int(depth * (9 if kind in ('city', 'metropolis') else 4))
        tall = TALL.get(k, 5) + min(4, bw // 10) + {'city': 5, 'metropolis': 7, 'town': 2}.get(kind, 0)
        if kind in ('hamlet', 'village'):
            tall = max(3, tall - 2)
        fade = .35 * depth
        rc = _mix(roof, sky[1], fade)
        wc = _mix(wallc, sky[1], fade)
        if burnt and rnd.random() < .4:
            rc, wc = (24, 20, 18), (40, 34, 30)
        top = base - tall
        if race == 'halfling' and k == 'home':      # a hill home: a green mound with a round door
            r = max(3, (x1 - x0) // 2 + 2)
            cx = (x0 + x1) // 2
            for dx in range(-r - 1, r + 2):
                hh = max(0, int((1 - (dx / (r + 1.5)) ** 2) * 7))
                pic.rect(cx + dx, base - hh, cx + dx, base, _mix(_mix(green, (90, 140, 60), .4), sky[1], .3 * depth))
            door = (170, 120, 50) if not night else (230, 190, 90)
            pic.rect(cx - 1, base - 2, cx + 1, base, door)
            pic.set(cx, base - 3, door)
            continue
        pic.rect(x0, top + 2, x1, base, wc)
        if race in ('dwarf',):                       # flat stone roofs
            pic.rect(x0, top + 1, x1, top + 2, rc)
        elif race in ('orc', 'goblin'):              # a long low hall with a ridge
            pic.rect(x0, top + 1, x1, top + 2, rc)
            pic.set((x0 + x1) // 2, top, rc)
        else:                                        # a gable
            half = max(1, (x1 - x0 + 2) // 2)
            for dy in range(half):
                a, b = x0 + dy, x1 - dy
                if a > b:
                    break
                pic.rect(a, top + 2 - dy, b, top + 2 - dy, rc)
        if k == 'temple':                            # the spire
            cx = (x0 + x1) // 2
            pic.rect(cx, top - 8, cx, top + 1, rc)
            pic.set(cx, top - 9, (230, 210, 140) if not night else (120, 110, 80))
        elif k == 'keep':                            # the keep: a tower with teeth
            pic.rect(x0, top - 4, x1, top + 2, wc)
            for xx in range(x0, x1 + 1, 2):
                pic.set(xx, top - 5, wc)
        if season == 'winter' and k != 'keep':
            pic.set((x0 + x1) // 2, top + 1 if race != 'dwarf' else top + 1, (230, 232, 236))
        if k in ('home', 'inn', 'elder') and rnd.random() < .5:
            chimneys.append(((x0 + x1) // 2 + 1, top))
        for _ in range(max(1, (x1 - x0) // 3)):
            windows.append((rnd.randint(x0, x1), rnd.randint(top + 3, max(top + 3, base - 1))))
    # the town's own wall and towers, or a palisade, or a hedge, in front
    walled = _free_walls(m, sts) > (m.w + m.h) and kind in ('town', 'city', 'metropolis')
    stone = (126, 118, 106) if not night else (40, 40, 52)
    if burnt:
        stone = _mix(stone, (30, 26, 24), .4)
    if walled:
        wh = 5 if kind != 'metropolis' else 6
        pic.rect(0, GROUND - wh, CW - 1, GROUND, stone)
        for xx in range(0, CW, 2):
            pic.set(xx, GROUND - wh - 1, stone)
        step = 16 if kind != 'metropolis' else 12
        for tx in range(4, CW, step):
            pic.rect(tx, GROUND - wh - 5, tx + 3, GROUND, _mix(stone, (255, 255, 255), .08))
            pic.set(tx, GROUND - wh - 6, stone)
            pic.set(tx + 3, GROUND - wh - 6, stone)
        gx = CW // 2
        pic.rect(gx - 4, GROUND - wh - 3, gx + 4, GROUND, _mix(stone, (255, 255, 255), .08))
        pic.rect(gx - 2, GROUND - 4, gx + 2, GROUND, (26, 20, 16) if not night else (200, 150, 70))
    elif _count(m, {47, 48}):
        wood = (110, 80, 48) if not night else (36, 28, 22)
        for xx in range(CW):
            pic.rect(xx, GROUND - (4 if xx % 2 else 5), xx, GROUND, wood)
    elif _count(m, {42}):
        hedge = _mix(green, (30, 70, 30), .5)
        pic.rect(0, GROUND - 2, CW - 1, GROUND, hedge)
    if kind == 'deephold':                            # the gate in the mountain
        gx = CW // 2
        pic.rect(gx - 7, GROUND - 14, gx + 7, GROUND, (86, 86, 94) if not night else (34, 34, 44))
        pic.rect(gx - 3, GROUND - 9, gx + 3, GROUND, (20, 16, 14) if not night else (220, 150, 60))
    # the ground
    pic.rect(0, GROUND + 1, CW - 1, PH - 1, ground)
    # lit windows at night; fire and dark smoke over a burnt one; chimney smoke else
    if night:
        for wx, wy in windows:
            if rnd.random() < .3:
                pic.set(wx, wy, (240, 200, 110))
    if burnt:
        for _ in range(6):
            fx = rnd.randrange(CW)
            pic.set(fx, GROUND - rnd.randrange(3, 8), (230, 90, 30))
            for k in range(1, 5):
                pic.marks[(fx // 1 + k // 2, max(0, (GROUND - 10) // 2 - k))] = ('§' if k < 2 else '°', (60, 56, 54))
    else:
        for cx, top in chimneys[:6]:
            sm = (190, 190, 196) if not night else (90, 92, 110)
            for k, ch in enumerate(('·', '°', '·')):
                pic.marks[(cx + k // 2, max(0, top // 2 - 1 - k))] = (ch, sm)
    return {'name': s.name, 'line': line(game, s), 'pic': pic}


def line(game, s):
    """'A walled human city in the grassland, held by Baron Aldric Hale.'"""
    from . import realms as RL
    race = s.race
    what = KINDS.get(s.kind, s.kind)
    people = PEOPLE.get(race, race)
    m = game.maps.get(s.map_key)
    walled = ''
    if m is not None and s.kind in ('town', 'city', 'metropolis') and _free_walls(m, _structures(m)) > (m.w + m.h):
        walled = 'walled '
    art = 'An' if (walled or people)[0] in 'aeiou' else 'A'
    from . import lands as LD
    land = None
    try:
        land = LD.biome(game, s.x, s.y)
    except Exception:
        land = None
    text = f'{art} {walled}{people} {what}'
    if land:
        text += f' in the {land.replace("_", " ")}'
    R = RL.get(game)
    lord = None
    if R is not None and s.region is not None:
        b = R.baronies.get(s.region)
        lo = R.lord(b.lord) if b is not None else None
        if lo is not None and getattr(lo, 'alive', True):
            lord = RL.style(R, lo, False)
    if s.plundered:
        text += ', burnt not long ago'
    if lord:
        text += f', held by {lord}'
    return text + '.'


def draw(cv, x, y, pic):
    """The picture at x, y on a canvas: a cell is the top pixel over the bottom one."""
    for cy in range(CH):
        top, bot = pic.px[cy * 2], pic.px[cy * 2 + 1]
        for cx in range(CW):
            mk = pic.marks.get((cx, cy))
            if mk:
                cv.put(x + cx, y + cy, mk[0], mk[1], top[cx])
            elif top[cx] == bot[cx]:
                cv.put(x + cx, y + cy, ' ', top[cx], top[cx])
            else:
                cv.put(x + cx, y + cy, '▀', top[cx], bot[cx])


def places(game):
    """The settlements and homes you have seen, in the order of the world (for the journal's Places tab)."""
    sg = seen(game.player)
    out = [Home(game, f's{s.id}') for s in game.world.settlements if f's{s.id}' in sg]
    return out + [Home(game, f'site{q.id}') for q in game.world.sites if f'site{q.id}' in sg]
