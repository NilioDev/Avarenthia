"""Places in the countryside that are not towns: temples, monasteries and watchtowers.
(Their ruined cousins are hidden places with a way down; see events.py.)"""
import random

from . import data as D
from .data import GRASS, FLOOR, WALL, DOOR, PATH, TREE, ALTAR, BED, TABLE, FIELD, FENCE, WELL, UP
from .entities import GameMap, make_npc
from .worldgen import cheb

SITE_LOOK = {'temple': ('π', (240, 230, 200)), 'monastery': ('Θ', (210, 180, 130)), 'watchtower': ('¡', (200, 200, 210))}
TEMPLE_NAMES = ['Temple of the Dawn', 'Temple of Saint Aldra', 'Temple of the Quiet Flame', 'Temple of the Seven Stars',
                'Temple of Mercy', 'Temple of the Lantern']
MONASTERY_NAMES = ['Monastery of the Grey Brothers', 'Abbey of Saint Wendel', 'Cloister of the Silent Bell',
                   'Monastery of the Green Hand', 'Priory of the Hollow Oak']


class Site:
    def __init__(self, sid, kind, x, y, name):
        self.id, self.kind, self.x, self.y, self.name = sid, kind, x, y, name
        self.faction = None

    @property
    def map_key(self):
        return f'site:{self.id}'

    @property
    def glyph(self):
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
    for kind, n, road in (('temple', 2, (1, 3)), ('monastery', 2, (3, 14)), ('watchtower', 5, (1, 2))):
        made = 0
        for x, y in cells:
            if made >= n:
                break
            if not ok(x, y, road, 8):
                continue
            if kind == 'monastery' and m.tile(x, y) not in (D.HILLS, D.FOREST, D.GRASS):
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


def climb_tower(game):
    """From the top of a watchtower you can see far over the land."""
    m = game.map
    site = game.world.sites[m.site]
    om = game.maps['over']
    r = 16
    n = 0
    for y in range(site.y - r, site.y + r + 1):
        for x in range(site.x - r * 2, site.x + r * 2 + 1):
            if om.inb(x, y) and ((x - site.x) / 2) ** 2 + (y - site.y) ** 2 <= r * r and not om.seen[y * om.w + x]:
                om.seen[y * om.w + x] = 1
                n += 1
    game.msg('You climb to the top of the tower. The land lies spread out below you, and you mark what you see on your map.'
             if n else 'You climb to the top of the tower. Nothing you have not seen before.', 'info')
