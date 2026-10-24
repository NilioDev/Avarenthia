"""Places in the countryside that are not towns: temples, monasteries, watchtowers, farmsteads along the roads
and the odd roadside inn.
(Their ruined cousins are hidden places with a way down; see events.py.)"""
import random

from . import data as D
from .data import GRASS, FLOOR, WALL, DOOR, PATH, TREE, ALTAR, BED, TABLE, FIELD, FENCE, WELL, UP
from .entities import GameMap, make_npc
from .worldgen import cheb

SITE_LOOK = {'temple': ('π', (240, 230, 200)), 'monastery': ('Θ', (210, 180, 130)), 'watchtower': ('¡', (200, 200, 210)),
             'tower': ('¡', (200, 200, 210)), 'barrow': ('∩', (196, 200, 170)),
             'farm': ('ƒ', (180, 196, 100)), 'roadinn': ('╤', (236, 164, 84)), 'valley': ('•', (226, 196, 130)),
             'glade': ('♠', (170, 236, 150)), 'gnomes': ('♣', (226, 204, 120)), 'oasis': ('¥', (130, 214, 96)),
             'shieling': ('⌂', (214, 200, 170))}
from .tribes import LOOK as _CAMP_LOOK  # noqa: E402
SITE_LOOK.update(_CAMP_LOOK)
from .nature import LOOK as _NATURE_LOOK  # noqa: E402
SITE_LOOK.update(_NATURE_LOOK)
from .oldplaces import LOOK as _OLD_LOOK  # noqa: E402
SITE_LOOK.update(_OLD_LOOK)
from . import seats as _SEATS  # noqa: E402
SITE_LOOK.update(_SEATS.LOOK)
ROADINN_NAMES = ["The Wayfarer's Rest", 'The Crossed Keys', 'The Drowsy Mule', 'The Last Lantern', 'The Weary Boot',
                 'The Green Man', 'The Hanged Fiddler', 'The Three Crowns', 'The Broken Wheel', 'The Milestone',
                 'The Sleeping Dog', 'The Pilgrim\'s Staff', 'The Black Kettle']
FARM_NAMES = ['Farm', 'Homestead', 'Steading', 'Croft', 'Farmstead']
TEMPLE_NAMES = ['Temple of the Dawn', 'Temple of Saint Aldra', 'Temple of the Quiet Flame', 'Temple of the Seven Stars',
                'Temple of Mercy', 'Temple of the Lantern', 'Temple of the Open Hand', 'Temple of Saint Corwen']
MONASTERY_NAMES = ['Monastery of the Grey Brothers', 'Abbey of Saint Wendel', 'Cloister of the Silent Bell',
                   'Monastery of the Green Hand', 'Priory of the Hollow Oak', 'Abbey of the White Ford']


class Site:
    def __init__(self, sid, kind, x, y, name):
        self.id, self.kind, self.x, self.y, self.name = sid, kind, x, y, name
        self.faction = None

    @property
    def map_key(self):
        return f'site:{self.id}'

    @property
    def glyph(self):
        if self.kind in _SEATS.KINDS:
            return _SEATS.glyph(self)
        from . import places as PL
        if PL.is_place(self):
            return PL.glyph(self)
        return SITE_LOOK[self.kind]


def gen_sites(game, m, world):
    """One temple near Thornfield (where you wake), and a few more temples, monasteries and watchtowers."""
    world.sites = []
    taken = [(s.x, s.y) for s in world.settlements] + [(h.x, h.y) for h in world.holds] + \
            [(d.x, d.y) for d in world.dungeons.values()]
    home = world.settlements[0]
    tnames, mnames = TEMPLE_NAMES[:], MONASTERY_NAMES[:]
    random.shuffle(tnames)
    random.shuffle(mnames)

    def ok(x, y, near_road=None, far=4):
        if not m.inb(x, y) or not (2 <= x < m.w - 2 and 2 <= y < m.h - 2):
            return False
        t = m.tile(x, y)
        if not D.TILES[t].walk or t in (D.ROAD, D.TOWN, D.CITY, D.ENTR, D.RIVER, D.CASTLE, D.FORT):
            return False
        if y * m.w + x in getattr(world, 'wonder_cells', ()):
            return False
        if any(cheb(x, y, a, b) < far for a, b in taken):
            return False
        if near_road is not None:
            rd = world.road_dist[y * m.w + x]
            if not (near_road[0] <= rd <= near_road[1]):
                return False
        return True

    def place(kind, name, cands):
        random.shuffle(cands)
        for x, y in cands:
            if ok(x, y):
                s = Site(len(world.sites), kind, x, y, name)
                s.faction = world.region_at(x, y).faction
                world.sites.append(s)
                taken.append((x, y))
                return s
        return None

    # the temple where you wake, a short walk from Thornfield
    near = [(home.x + dx, home.y + dy) for dx in range(-6, 7) for dy in range(-5, 6) if 3 <= max(abs(dx), abs(dy)) <= 6]
    t0 = place('temple', tnames.pop(), [c for c in near if ok(c[0], c[1], far=3)])
    world.start_temple = t0.id if t0 else None
    cells = [(x, y) for y in range(3, m.h - 3) for x in range(3, m.w - 3)]
    random.shuffle(cells)
    from .world import scaled
    for kind, n, road in (('temple', scaled(2), (1, 3)), ('monastery', scaled(2), (3, 14)), ('watchtower', scaled(5), (1, 2))):
        made = 0
        for x, y in cells:
            if made >= n:
                break
            if not ok(x, y, road, 8):
                continue
            if kind == 'monastery' and m.tile(x, y) not in (D.HILLS, D.FOREST, D.GRASS):
                continue
            if kind in ('temple', 'monastery') and not (tnames if kind == 'temple' else mnames):
                continue
            name = tnames.pop() if kind == 'temple' and tnames else mnames.pop() if kind == 'monastery' and mnames else None
            if kind == 'watchtower':
                used = {q.name for q in world.sites}
                opts = [f"{world.region_at(x, y).name} {k}" for k in ('Watchtower', 'Lookout', 'Beacon Tower', 'Signal Tower')]
                name = next((o for o in opts if o not in used), opts[0] + f' {len(world.sites)}')
            s = Site(len(world.sites), kind, x, y, name)
            s.faction = world.region_at(x, y).faction
            world.sites.append(s)
            taken.append((x, y))
            made += 1
    # farmsteads along the roads near the villages, and a few inns where the roads run long and empty
    from .towns import town_names
    inames = ROADINN_NAMES[:]
    random.shuffle(inames)
    flood = m.biome_names.index('floodplain') if 'floodplain' in getattr(m, 'biome_names', []) else None
    for kind, n, road, near, far in (('roadinn', scaled(4), (1, 1), (11, 99), 8), ('farm', scaled(14), (1, 1), (4, 22), 5)):
        made = 0
        for x, y in cells:
            if made >= n:
                break
            if not ok(x, y, road, far) or m.tile(x, y) not in (D.GRASS, D.HILLS, D.SAND):
                continue
            if kind == 'farm' and flood is not None and m.biome[y * m.w + x] != flood and random.random() < .5:
                continue                              # the farms crowd onto the flood meadows
            d = min(cheb(x, y, st.x, st.y) for st in world.settlements)
            if not (near[0] <= d <= near[1]):
                continue
            if kind == 'roadinn' and any(q.kind == 'roadinn' and cheb(x, y, q.x, q.y) < 26 for q in world.sites):
                continue
            region = world.region_at(x, y)
            if kind == 'farm':
                fam = town_names('human')[0].split()[-1]
                name = f'{fam} {random.choice(FARM_NAMES)}'
            else:
                name = inames.pop() if inames else 'The Roadside Inn'
            s = Site(len(world.sites), kind, x, y, name)
            s.faction = region.faction
            world.sites.append(s)
            taken.append((x, y))
            made += 1


def site_at(world, x, y):
    for s in getattr(world, 'sites', ()):
        if s.x == x and s.y == y:
            return s
    return None


# ------------------------------------------------------------------ maps
def _rect(m, x0, y0, x1, y1, wall=WALL, floor=FLOOR):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            edge = y in (y0, y1) or x in (x0, x1)
            m.set(x, y, wall if edge else floor)


def _base(site, w, h):
    m = GameMap(site.map_key, 'town', site.name, w, h, GRASS)
    m.radius, m.sid, m.hid, m.signs = 60, None, None, []
    m.site = site.id
    for i in range(len(m.t)):
        if random.random() < .05:
            m.t[i] = TREE
    sy = h // 2
    for x in range(0, w // 2):
        m.set(x, sy, PATH)
    m.entry = (0, sy)
    return m, sy


def gen_site_map(game, site):
    """A temple, monastery or watchtower in its own stretch of countryside, with lamps by the door."""
    from .towns import embed, place_lamps
    if site.kind == 'valley':
        from .hidden import valley_map
        return valley_map(game, site)
    if site.kind == 'glade':
        from .folk import glade_map
        return glade_map(game, site)
    if site.kind == 'gnomes':
        from .folk import gnome_map
        return gnome_map(game, site)
    from . import tribes as TR
    if TR.is_camp(site):
        return TR.gen_camp(game, site)
    if site.kind in ('oasis', 'shieling'):
        from .lands import site_map
        return site_map(game, site)
    from . import nature as NT
    if NT.is_nature(site):
        return NT.site_map(game, site)
    from . import oldplaces as OP
    if OP.is_old(site):
        return OP.site_map(game, site)
    if _SEATS.is_seat(site):
        return _SEATS.gen_map(game, site)
    from . import places as PL
    if PL.is_place(site):
        return PL.gen_map(game, site)
    m = _site_map(game, site)
    ex, ey = m.entry
    lamps = [(x, y) for x in range(4, m.w - 2) for y in (ey - 2, ey + 2) if m.tile(x, y) == GRASS
             and any(m.tile(x + dx, ey) == DOOR for dx in (1, 2, 3))]
    place_lamps(m, lamps[:2])
    return embed(m, 96, 62)


def _site_map(game, site):
    from .towns import town_names, townsfolk
    races = D.FACTIONS.get(site.faction, {}).get('race', 'human') if site.faction else 'human'
    names = town_names(races)
    if site.kind == 'temple':
        m, sy = _base(site, 50, 21)
        x0, y0, x1, y1 = 22, 5, 42, 15
        _rect(m, x0, y0, x1, y1)
        m.set(x0, sy, DOOR)
        for x in range(x0 + 3, x1 - 3, 2):
            for y in (y0 + 3, y1 - 3):
                m.set(x, y, TABLE)          # pews
        m.set(x1 - 2, sy, ALTAR)
        m.signs.append((x0 + 6, y0 - 1, 'TEMPLE'))
        start = getattr(game.world, 'start_temple', None) == site.id
        prname = 'Sister Ilse Marsh' if start else f'Sister {names.pop()}'
        m.mons.append(make_npc(game, prname, 'healer', '#f4f0e6', x1 - 3, sy, True))
        for _ in range(2):
            townsfolk(game, m, [(x0 + 4, y0 + 2)], (random.randint(x0 + 3, x1 - 4), random.choice((sy - 1, sy + 1))),
                      names, 'acolyte', '#d8d0c0')
        # a small graveyard and a herb garden
        for x in range(4, 16, 3):
            for y in (2, 4):
                m.set(x, y, D.GRAVE)
        for x in range(4, 16):
            for y in (sy + 3, sy + 4, sy + 5):
                m.set(x, y, FIELD)
        m.lights = []
        return m
    if site.kind == 'monastery':
        m, sy = _base(site, 60, 23)
        x0, y0, x1, y1 = 18, 2, 56, 20
        _rect(m, x0, y0, x1, y1)
        for x in range(x0 + 1, x1):
            for y in range(y0 + 1, y1):
                m.set(x, y, GRASS)
        m.set(x0, sy, PATH)
        # chapel, refectory, cells around a cloister garden
        _rect(m, 40, 3, 55, 9)
        m.set(47, 9, DOOR)
        m.set(52, 6, ALTAR)
        _rect(m, 40, 13, 55, 19)
        m.set(47, 13, DOOR)
        for x in range(43, 53, 3):
            m.set(x, 16, TABLE)
        _rect(m, 20, 13, 35, 19)
        m.set(27, 13, DOOR)
        for x in range(22, 34, 2):
            m.set(x, 18, BED)
        for x in range(23, 36):
            for y in range(4, 10):
                m.set(x, y, FIELD if (x + y) % 3 else GRASS)
        m.set(30, 11, WELL)
        m.signs += [(45, 2, 'CHAPEL'), (44, 20, 'REFECTORY')]
        m.mons.append(make_npc(game, f'Abbot {names.pop()}', 'healer', '#f4f0e6', 50, 6, True))
        m.mons.append(make_npc(game, f'Brother {names.pop()} the Herbalist', 'herbalist', '#90d070', 29, 7, True))
        m.mons.append(make_npc(game, f'Brother {names.pop()} the Cellarer', 'inn', '#e0a060', 47, 15, True))
        for j in range(4):
            townsfolk(game, m, [(24 + j * 2, 17)], (random.randint(24, 34), random.randint(5, 9)), names, 'monk', '#b0a080')
        return m
    if site.kind == 'farm':
        return _farm_map(game, site, names)
    if site.kind == 'roadinn':
        return _roadinn_map(game, site, names)
    # watchtower
    m, sy = _base(site, 44, 19)
    cx, cy = 28, sy
    _rect(m, cx - 4, cy - 4, cx + 4, cy + 4)
    m.set(cx - 4, cy, DOOR)
    m.set(cx + 2, cy - 2, UP)
    m.signs.append((cx - 5, cy - 5, 'WATCHTOWER'))
    gfg = D.FACTIONS.get(site.faction, {}).get('fg', (180, 180, 200))
    for gx, gy in ((cx - 5, cy - 1), (cx - 5, cy + 1), (cx, cy + 2)):
        townsfolk(game, m, [(cx, cy)], (gx, gy), [f"A {D.FACTIONS.get(site.faction, {}).get('short', 'tower')} guard"],
                  'guard', fg=gfg, role='guard')
    m.mons.append(make_npc(game, f'Captain {names.pop()}', 'tower', '#e8e0c0', cx + 1, cy, True))
    return m


# ------------------------------------------------------------------ farmsteads and roadside inns
def _farm_map(game, site, names):
    """A farmstead: the farmhouse, a barn with animals, fields and a pasture, and the family who works it."""
    from .towns import (townsfolk, Plot, house_plot, build_house, place_door, furnish, hearths, farmland, LIVESTOCK)
    from .data import PLANK, BARREL
    m, sy = _base(site, 70, 36)
    house = house_plot('home', 26, sy - 9)
    house.annex = (house.x + house.w - 1, house.y + 2, 5, 5)
    build_house(m, house)
    place_door(m, house, house.x + house.w // 2, sy)
    furnish(m, house)
    barn = Plot(42, sy - 10, 14, 9, 'stables')
    from .towns import build
    build(m, barn)
    for c in barn.inside:
        m.set(c[0], c[1], PLANK)
    m.set(barn.x + barn.w // 2, barn.y + barn.h - 1, DOOR)
    for c in ((barn.x + 1, barn.y + 1), (barn.x + 2, barn.y + 1), (barn.x + barn.w - 2, barn.y + 1)):
        m.set(c[0], c[1], BARREL)
    name, ch, fg = random.choice(LIVESTOCK)
    for c in random.sample([c for c in barn.inside if m.tile(*c) == PLANK], 3):
        m.mons.append(make_npc(game, name, 'livestock', fg, c[0], c[1], False, ch=ch))
    for x in range(26, 56):                       # the yard between house and barn
        if m.tile(x, sy - 1) == GRASS:
            m.set(x, sy - 1, PATH)
    m.set(38, sy - 3, WELL)
    plots = [Plot(house.x - 1, house.y - 1, house.w + 7, house.h + 2, 'h'), Plot(barn.x - 1, barn.y - 1, barn.w + 2, barn.h + 2, 'b'),
             Plot(0, sy - 1, 26, 3, 'road'), Plot(36, sy - 4, 4, 3, 'well')]
    fields, pastures = farmland(game, m, plots, -999, names, want=[('field', 4), ('pasture', 1), ('orchard', 1)])
    family = names.pop()
    beds = [c for c in house.inside if m.tile(*c) in (FLOOR, PLANK)]
    work = random.choice(random.choice(fields)) if fields else (30, sy)
    farmer = townsfolk(game, m, beds, work, [f'Farmer {family}'], 'farmer', fg='#c8b890')
    farmer.name = f'Farmer {family}'
    farmer.role = 'farmer'
    farmer.stay = False
    for job in ('farmer', 'child'):
        townsfolk(game, m, beds, random.choice(random.choice(fields)) if fields and job == 'farmer' else (34, sy - 2),
                  names, job, fg='#c8b8a0' if job == 'child' else '#b8b0a0')
    m.mons.append(make_npc(game, 'A farm dog', 'dog', '#b89060', 32, sy - 2, False, ch='d'))
    hearths(m, [house])
    m.glows = [(house.x + 2, house.y + 2, (255, 150, 70), 5)]
    m.lights = list(m.glows)
    return m


def _roadinn_map(game, site, names):
    """A lonely inn by the road: a taproom, rooms upstairs (well, at the back), a stable and a few travellers."""
    from .towns import townsfolk, Plot, build, place_door, hearths, furnish
    from .data import PLANK, BARREL, STALL
    m, sy = _base(site, 64, 30)
    inn = Plot(24, sy - 9, 16, 10, 'inn')
    build(m, inn)
    place_door(m, inn, inn.x + inn.w // 2, sy)
    furnish(m, inn)
    rooms = Plot(39, sy - 9, 9, 10, 'home')
    build(m, rooms)
    for c in rooms.inside:
        m.set(c[0], c[1], PLANK)
    for y in range(rooms.y + 1, rooms.y + rooms.h - 1, 2):
        m.set(rooms.x + rooms.w - 2, y, BED)
    m.set(rooms.x, rooms.y + 3, D.ODOOR)            # through from the taproom
    stable = Plot(26, sy + 2, 12, 6, 'stables')
    build(m, stable)
    for c in stable.inside:
        m.set(c[0], c[1], PLANK)
    m.set(stable.x + stable.w // 2, stable.y, DOOR)
    m.mons.append(make_npc(game, 'A tired mule', 'livestock', '#a08060', stable.x + 3, stable.y + 3, False, ch='m'))
    for x in range(0, 64):
        if m.tile(x, sy) == GRASS:
            m.set(x, sy, PATH)
    spots = [c for c in inn.inside if m.tile(*c) in (FLOOR, PLANK)]
    keeper = make_npc(game, f'{names.pop()} the Innkeeper', 'roadinn', '#e0a060', spots[0][0], inn.y + 1, True)
    m.mons.append(keeper)
    for _ in range(random.randint(2, 4)):
        townsfolk(game, m, [random.choice(spots)], random.choice(spots), names, random.choice(['drinker', 'drinker', 'carter']))
    m.signs.append((inn.x + 3, inn.y - 1, site.name.upper()[:18]))
    hearths(m, [inn])
    return m
