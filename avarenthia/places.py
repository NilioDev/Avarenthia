"""Places on their own land (round 6): the temples, towers and barrows of every people.

Each stands on a play map of its own, cut from the land of its world cell as you would walk it in its zone
(zones.make), so a temple in the hills has hills round it and the path in comes from the side. The temple you walk
into on that map; a tower's floors above (towers.py) and every crypt, cellar and barrow below are levels of their
own, reached by stairs: Dungeon records in world.dungeons with d.site set, so they never show on the world map.

Who may come how far in depends on your name with that people (`tier`): turned away at the gate, the open parts,
or everywhere (the crypt, the stair up). Where a warden stands in the way you are told so, and may push past: a
crime. The hostile peoples' places you fight your way through; orcs and goblins let their own kind and the horde's
friends in."""
import random

from . import data as D
from .data import GRASS, FLOOR, WALL, DOOR, PATH, UP, DOWN
from .entities import GameMap, make_npc, make_monster
from .worldgen import cheb

PEOPLES = ('human', 'elf', 'dwarf', 'halfling', 'gnome', 'orc', 'goblin', 'kobold', 'gnoll', 'lizard')
HOSTILE = {'orc', 'goblin', 'kobold', 'gnoll', 'lizard'}
KINDS = {'tower', 'barrow', 'fort', 'manor'}   # new site kinds; temples and monasteries keep theirs and gain a people
OLD = ('temple', 'monastery')
HALLS = ('monastery', 'fort', 'manor')
FG = {'human': (240, 230, 200), 'elf': (206, 240, 200), 'dwarf': (226, 176, 126), 'halfling': (206, 220, 126),
      'gnome': (226, 204, 120), 'orc': (170, 204, 100), 'goblin': (196, 204, 96), 'kobold': (230, 156, 90),
      'gnoll': (214, 178, 100), 'lizard': (116, 196, 126)}
SIGN = {'temple': 'π', 'tower': '¡', 'barrow': '∩', 'monastery': 'Θ', 'fort': '╩', 'manor': 'Å'}
PLURAL = {'human': 'people', 'elf': 'elves', 'dwarf': 'dwarves', 'halfling': 'halflings', 'gnome': 'gnomes', 'orc': 'orcs',
          'goblin': 'goblins', 'kobold': 'kobolds', 'gnoll': 'gnolls', 'lizard': 'lizardfolk'}
ADJ = {'human': 'human', 'elf': 'elven', 'dwarf': 'dwarven', 'halfling': 'halfling', 'gnome': 'gnome', 'orc': 'orc',
       'goblin': 'goblin', 'kobold': 'kobold', 'gnoll': 'gnoll', 'lizard': 'lizardfolk'}
NAMES = {
    'temple': {'elf': ['The Moonwell Glades', 'The Grove of Songs', 'The Starlit Glades'],
               'dwarf': ['The Hall of the Forefathers', 'The Ancestor Hall', 'The Hall of Stone Fathers'],
               'halfling': ['The Hearth Chapel', 'The Harvest Chapel', 'The Chapel in the Hedge'],
               'gnome': ['The Crystal Hollow', 'The Glimmer Hollow', 'The Hollow of Lights'],
               'orc': ['The Ring of Blood', "The War God's Ring", 'The Red Ring'],
               'goblin': ['The Junk Shrine', 'The Shrine of Many Things', 'The Nook of the Idol'],
               'kobold': ['The Shrine to Shine', 'The Glitter Shrine', 'The Bright Nook'],
               'gnoll': ['The Bone Ring', 'The Moon Kraal', 'The Ring of the Bone-Caller'],
               'lizard': ['The Egg Mound', 'The Sun Mound', 'The Stepped Mound']},
    'tower': {'human': ['Watchtower', 'Lookout', 'Beacon Tower', 'Signal Tower'],
              'elf': ['The White Spire', 'The Spire of Leaves', 'The Star Tower'],
              'dwarf': ['The Beacon Tower', 'The Stone Watch', 'The Hammer Tower'],
              'orc': ['The Skull Tower', 'The Log Tower', 'The Drum Tower'],
              'goblin': ['The Crooked Tower', 'The Scrap Tower', 'The Leaning Tower'],
              'kobold': ['The Shiny Spire', 'The Glint Tower', 'The Piled Spire'],
              'gnoll': ['The Bone Tower', 'The Pole Tower', 'The Howling Tower'],
              'lizard': ['The Reed Tower', 'The Stilt Tower', 'The Smoke Tower'],
              'ruin': ['The Fallen Tower', 'The Broken Tower', 'The Old Tower', 'The Leaning Stones', 'The Split Tower'],
              'stump': ['The Tower Stump', 'The Ivy Stump', 'The Stub of Stone']},
    'barrow': {'human': ["The Old King's Barrow", 'Howe of the Nine', 'The Grey Mound', 'Barrow of the Hollow Crown'],
               'elf': ['The Root Tomb', 'The Tomb under the Dead Tree', 'The Sleeping Roots'],
               'dwarf': ['The Sealed Vault', 'The Vault of Stone Kings', 'The Rune-Sealed Tomb'],
               'halfling': ['The Resting Hill', 'The Quiet Hill', 'The Family Hill'],
               'gnome': ['The Crystal Crypt', 'The Inventor\'s Crypt', 'The Glass Tomb'],
               'orc': ['The Bone Cairn', "The Warlord's Cairn", 'The Cairn of Skulls'],
               'goblin': ['The Trapped Tomb', "The Boss's Tomb", 'The Tomb of Turns'],
               'kobold': ['The Hoard Tomb', "The Hoardmaster's Tomb", 'The Coin Grave'],
               'gnoll': ['The Bone Hill', "The Packlord's Hill", 'The Hill of Every Kill'],
               'lizard': ['The Drowned Tomb', 'The Sunken Coffins', 'The Pool of the Stone Egg']},
}
NAME_FALLBACK = {'human': ['Hal', 'Bran', 'Edda', 'Osric', 'Wenna', 'Tobin'], 'kobold': ['Yip', 'Skrit', 'Tikka', 'Murk'],
                 'gnoll': ['Gharr', 'Yeek', 'Rakka', 'Shurr'], 'lizard': ['Sssath', 'Ikss', 'Thassa', 'Ruuk']}
# where each people builds, on the world map, and which places of theirs it builds near
LAND = {'human': (D.GRASS, D.HILLS, D.FOREST), 'elf': (D.FOREST,), 'dwarf': (D.HILLS,), 'halfling': (D.GRASS, D.HILLS),
        'gnome': (D.FOREST, D.HILLS), 'orc': (D.GRASS, D.HILLS, D.SAND), 'goblin': (D.HILLS, D.GRASS, D.FOREST),
        'kobold': (D.HILLS,), 'gnoll': (D.GRASS, D.SAND), 'lizard': (D.SWAMP,)}
CAMP = {'orc': 'warcamp', 'goblin': 'ravine', 'kobold': 'kobolds', 'gnoll': 'gnolls', 'lizard': 'stilts'}
DEEP_TAG = {'human': 'crypt', 'elf': 'cave', 'dwarf': 'crypt', 'halfling': 'cave', 'gnome': 'cave', 'orc': 'lair_orc',
            'goblin': 'warren', 'kobold': 'den', 'gnoll': 'burrow', 'lizard': 'swamp'}
DEEP_NAME = {'human': 'The Crypt below {n}', 'elf': 'The Root Halls under {n}', 'dwarf': 'The Tombs under {n}',
             'halfling': 'The Cellars under {n}', 'gnome': 'The Deep Hollows under {n}', 'orc': 'The Cave of the War God',
             'goblin': 'The Holes under {n}', 'kobold': 'The Shine Pits', 'gnoll': 'The Burrows under {n}',
             'lizard': 'The Drowned Halls under {n}'}
WALLS = {'crypt': '#7e869c', 'cave': '#8a8072', 'lair_orc': '#7a6a52', 'warren': '#8a7a5a', 'den': '#8a7058',
         'burrow': '#8a7a5e', 'swamp': '#5e7a64', 'barrow': '#6a7a70', 'dungeon': '#a0835e'}


# ------------------------------------------------------------------ who is who
def the(name):
    """A place's name in the middle of a sentence: 'the Temple of Mercy', 'the Hearth Chapel'."""
    if name.startswith('The '):
        return 'the ' + name[4:]
    return name if name.split()[0] not in ('Temple', 'Abbey', 'Monastery') else 'the ' + name


def people_of(site):
    return getattr(site, 'people', None) or 'human'


def is_place(site):
    return site is not None and (site.kind in KINDS or (site.kind in OLD and getattr(site, 'people', None)))


def glyph(site):
    if getattr(site, 'state', 'whole') != 'whole':
        return SIGN[site.kind], (150, 144, 132)
    return SIGN[site.kind], FG[people_of(site)]


def a_name(people):
    from .towns import town_names
    try:
        names = town_names(people)
    except Exception:
        names = []
    return (names[0].split()[0] if names else random.choice(NAME_FALLBACK.get(people, NAME_FALLBACK['human'])))


def describe(game, site):
    pe = people_of(site)
    if site.kind in HALLS:
        from . import halls as HL
        return HL.describe(game, site)
    if site.kind == 'temple':
        return f'A temple of the {PLURAL[pe]}. ' + ('Priests heal the sick and lift curses; a place to wake if you fall.'
                                                    if pe not in HOSTILE else 'Its altar is not for strangers.')
    if site.kind == 'tower':
        st = getattr(site, 'state', 'whole')
        if st == 'half':
            return 'A tower, half fallen. One side lies in a heap at its foot.'
        if st == 'ruin':
            return 'The stump of a tower, grown over with ivy.'
        return f"A tower of the {PLURAL[pe]}, {site.storeys} storeys high. From the top you see far over the land."
    return f'A barrow of the {PLURAL[pe]}: the grave of someone great. Take from the dead, and they wake.'


def friendly(game, site):
    """Is this place's people at peace with you? (Fallen towers and barrows hold no people.)"""
    if site.kind == 'barrow':
        return False
    if getattr(site, 'state', 'whole') != 'whole':
        return False
    return tier(game, site) >= 0


def tier(game, site):
    """How far in you may come: -1 they fight you, 0 turned away at the gate, 1 the open parts, 2 everywhere."""
    from . import crime as CR
    from .races import relation
    p = game.player
    pe = people_of(site)
    if pe in HOSTILE:
        if pe in ('orc', 'goblin') and (p.race in ('orc', 'goblin') or p.rep.get('horde', -30) >= 0):
            return 2
        return -1
    score = p.rep.get(site.faction, 0) if site.faction else 0
    score += relation(pe if pe in ('human', 'elf', 'dwarf', 'halfling', 'gnome', 'orc', 'goblin') else 'human', p.race)
    if CR.max_heat(game) >= 3:
        score -= 20                             # the wanted are not welcome in holy places
    if getattr(site, 'forced', -99) > game.day - 30:
        score -= 30
    return 0 if score < -10 else 1 if score < 10 else 2


# ------------------------------------------------------------------ on the world map
def place(game, m, world, reach_set):
    """Give the old temples and watchtowers a people, and raise the temples, towers and barrows of every people
    near their own places, in the land they like."""
    from .world import scaled
    from .sites import Site
    from . import halls as HL
    for k, v in HL.NAMES.items():
        NAMES.setdefault(k, v)
    taken = [(s.x, s.y) for s in world.settlements] + [(q.x, q.y) for q in world.sites] + \
            [(d.x, d.y) for d in world.dungeons.values()] + [(h.x, h.y) for h in world.holds]
    halfland = set(getattr(world, 'halfling_land', ()))
    for st in world.sites:
        if st.kind == 'temple':
            r = world.region_at(st.x, st.y)
            st.people = 'halfling' if r.id in halfland and st.id != getattr(world, 'start_temple', None) else 'human'
            setup(game, world, st)
        elif st.kind == 'watchtower':
            st.kind, st.people = 'tower', 'human'
            setup(game, world, st)
        elif st.kind == 'monastery':
            st.people = 'human'
            setup(game, world, st)

    def anchors(pe):
        if pe in CAMP:
            return [(q.x, q.y) for q in world.sites if q.kind == CAMP[pe]]
        if pe == 'elf':
            return [(q.x, q.y) for q in world.sites if q.kind == 'glade'] + \
                   [(s.x, s.y) for s in world.settlements if getattr(s, 'elder', False)]
        if pe == 'gnome':
            return [(q.x, q.y) for q in world.sites if q.kind == 'gnomes']
        if pe == 'dwarf':
            return [(s.x, s.y) for s in world.settlements if s.kind == 'deephold' or getattr(s, 'dwarven', False)]
        if pe == 'halfling':
            return [(s.x, s.y) for s in world.settlements if getattr(s, 'race', '') == 'halfling']
        return [(s.x, s.y) for s in world.settlements if getattr(s, 'race', 'human') == 'human']

    def spot(pe, near=(4, 16), anywhere=False, pred=None):
        ok_land = LAND[pe]
        ans = anchors(pe)
        cells = []
        if ans:
            for ax, ay in random.sample(ans, len(ans)):
                for _ in range(60):
                    x, y = ax + random.randint(-near[1], near[1]), ay + random.randint(-near[1], near[1])
                    if near[0] <= cheb(x, y, ax, ay) <= near[1]:
                        cells.append((x, y))
        if anywhere or not ans:
            cells += [(i % m.w, i // m.w) for i in random.sample(list(reach_set), min(3000, len(reach_set)))]
        for x, y in cells:
            if not (3 <= x < m.w - 3 and 3 <= y < m.h - 3) or y * m.w + x not in reach_set:
                continue
            t = m.tile(x, y)
            if t not in ok_land or y * m.w + x in getattr(world, 'wonder_cells', ()):
                continue
            if world.road_dist[y * m.w + x] < (1 if pe not in HOSTILE else 3):
                continue
            if any(cheb(x, y, a, b) < 5 for a, b in taken):
                continue
            if pred and not pred(x, y):
                continue
            return x, y
        return None

    def add(kind, pe, xy, **kw):
        x, y = xy
        used = {q.name for q in world.sites}
        pool = NAMES[kind].get(kw.get('pool', pe)) or NAMES[kind]['human']
        name = next((n for n in random.sample(pool, len(pool)) if n not in used), None)
        if kind in ('tower', 'fort', 'manor') and pool is NAMES[kind].get('human'):
            rn = world.region_at(x, y).name
            name = next((f'{rn} {n}' for n in random.sample(pool, len(pool)) if f'{rn} {n}' not in used), None)   # as the old watchtowers were named
        if name is None:
            rn = world.region_at(x, y).name
            name = next((f'{n} of {rn}' for n in random.sample(pool, len(pool)) if f'{n} of {rn}' not in used),
                        f'{random.choice(pool)} of {rn}')
        s = Site(len(world.sites), kind, x, y, name)
        s.faction = world.region_at(x, y).faction
        s.people = pe
        for k, v in kw.items():
            if k != 'pool':
                setattr(s, k, v)
        world.sites.append(s)
        taken.append((x, y))
        setup(game, world, s)
        return s
    for pe in PEOPLES:
        if pe == 'human':
            continue
        if pe == 'halfling' and not halfland:
            continue
        xy = spot(pe)
        if xy:
            add('temple', pe, xy)
    for pe in ('elf', 'dwarf', 'orc', 'goblin', 'kobold', 'gnoll', 'lizard'):
        xy = spot(pe, (5, 18))
        if xy:
            add('tower', pe, xy)
    for k in range(scaled(2)):                  # towers nobody keeps: half fallen, or only a stump
        xy = spot('human', (12, 40), anywhere=True)
        if xy:
            state = 'half' if k % 2 == 0 else 'ruin'
            add('tower', 'human', xy, state=state, pool='ruin' if state == 'half' else 'stump',
                holder=random.choice(('bandits', 'beast', 'cellar')))
    for pe in PEOPLES:
        if pe == 'halfling' and not halfland:
            continue
        for _ in range(2 if pe == 'human' else 1):
            xy = spot(pe, (6, 24))
            if xy:
                add('barrow', pe, xy)
    for pe in PEOPLES:                          # abbeys, forts and manors (halls.py); the humans' old monasteries stay
        if pe == 'halfling' and not halfland:
            continue
        for kind, n in (('monastery', 0 if pe == 'human' else 1), ('fort', 2 if pe == 'human' else 1),
                        ('manor', 2 if pe == 'human' else 1)):
            for _ in range(n):
                xy = spot(pe, (5, 20)) or spot(pe, (4, 40), anywhere=True)
                if xy:
                    add(kind, pe, xy)
    # the old kings of the north: barrows in the cold lands, where the spirits rise under the northern lights (aurora.py)
    from . import aurora as AU
    north = lambda x, y: AU.northern(world, x, y)                       # noqa: E731
    for _ in range(scaled(2) - sum(1 for q in world.sites if q.kind == 'barrow' and north(q.x, q.y))):
        xy = spot('human', (6, 40), pred=north) or spot('human', (6, 40), anywhere=True, pred=north)
        if xy:
            add('barrow', 'human', xy)


def setup(game, world, site):
    """What lies above and below a place: a tower's floors and cellar, a temple's deep place and bell tower,
    a barrow's halls. Dungeon records with d.site, so they never show on the world map."""
    from .world import Dungeon
    pe = people_of(site)
    danger = world.region_at(site.x, site.y).danger
    base = max(1, danger * 2 - 1)
    site.state = getattr(site, 'state', 'whole')
    if site.kind == 'tower':
        site.storeys = random.randint(3, 6) if site.state == 'whole' else random.randint(3, 4)
        site.cellar = random.random() < (.6 if site.state != 'whole' or pe in HOSTILE else .35)
        site.manned = site.state == 'whole'
        did = f'tw{site.id}'
        n = 1 if site.state == 'ruin' else site.storeys - 1
        dg = Dungeon(did, site.name, n, base, 'tower', 'tower', None, None, site.x, site.y, True)
        dg.site, dg.rise = site.id, True
        world.dungeons[did] = dg
        site.floors = did
        if site.cellar:
            hold = getattr(site, 'holder', None)
            cd = Dungeon(f'tc{site.id}', f'The cellar of {site.name}', 2 if hold == 'cellar' else 1, base,
                         'rooms', 'crypt' if hold == 'cellar' else 'dungeon', None, D.hexrgb(WALLS['dungeon']), site.x, site.y, False)
            cd.site, cd.size = site.id, 'small'
            world.dungeons[cd.id] = cd
            site.below = cd.id
    elif site.kind == 'temple':
        n = random.randint(3, 5)
        tag = DEEP_TAG[pe]
        did = f'tp{site.id}'
        dg = Dungeon(did, DEEP_NAME[pe].format(n=the(site.name)), n, base, 'rooms', tag, None, D.hexrgb(WALLS.get(tag, '#7e869c')),
                     site.x, site.y, False)
        dg.site, dg.size = site.id, 'middle'
        rough = pe in HOSTILE or pe in ('elf', 'gnome', 'halfling')
        dg.styles = ['rooms'] * (n - 1) + ['cave'] if not rough else ['rooms'] + ['cave'] * (n - 1)
        dg.older = random.random() < .3          # built over something older; the way in is walled up
        world.dungeons[did] = dg
        site.below = did
        if pe == 'human' and random.random() < .45:
            site.bell = True
        if pe == 'elf':
            site.bell = True                       # the eldest tree's stair up to a lookout in its crown
        site.god = {'dwarf': 'durnak', 'elf': 'thessa', 'halfling': 'thessa', 'gnome': 'skell'}.get(pe, getattr(site, 'god', None))
        if pe in HOSTILE:
            site.god = 'morrak'
    elif site.kind in HALLS:
        from . import halls as HL
        HL.setup(game, world, site)
    elif site.kind == 'barrow':
        did = f'br{site.id}'
        deeper = pe == 'kobold' or random.random() < .35
        dg = Dungeon(did, site.name, 2 if deeper else 1, base + 1, 'barrow', 'barrow', None, D.hexrgb(WALLS['barrow']),
                     site.x, site.y, False)
        dg.site, dg.size = site.id, 'small'
        dg.styles = ['barrow', 'rooms']
        world.dungeons[did] = dg
        site.below = did


def tower_dg(game, site):
    """The floors of the tower on this site (a tower, or a temple's bell tower)."""
    from .world import Dungeon
    did = getattr(site, 'floors', None)
    if did is None and getattr(site, 'tw', None):
        did = f'tw{site.id}'
        dg = Dungeon(did, site.name, site.tw['storeys'] - 1, max(1, game.world.region_at(site.x, site.y).danger * 2 - 1),
                     'tower', 'tower', None, None, site.x, site.y, True)
        dg.site, dg.rise = site.id, True
        game.world.dungeons[did] = dg
        site.floors = did
    return did


# ------------------------------------------------------------------ the land round a place
GROUNDS = (D.GRASS, D.SAND, D.SNOW, D.SLOPE, D.PATH, D.SWAMP, D.GRIT, D.BAREROCK)


def land(game, site, W, H):
    """A W x H map of the land at this world cell, the way you would walk it in its zone, with the cell's middle in
    the middle of the map. The ground tile the place is built on is kept as m.ground."""
    from . import zones as ZN
    t, _marks = ZN.make(game, site.x - 1, site.y - 1, 3, 3)
    s = ZN.salt(game)
    gx, gy = ZN.mid(site.x, site.y, s)
    lx, ly = gx - (site.x - 1) * ZN.ZW, gy - (site.y - 1) * ZN.ZH
    x0 = max(0, min(t.shape[1] - W, lx - W // 2))
    y0 = max(0, min(t.shape[0] - H, ly - H // 2))
    m = GameMap(site.map_key, 'town', site.name, W, H, GRASS)
    m.t = [int(v) for v in t[y0:y0 + H, x0:x0 + W].ravel()]
    for i, v in enumerate(m.t):
        if v in (D.ENTR, D.TOWN, D.CITY, D.CASTLE, D.FORT, D.FIELD, D.FENCE, D.ROAD):
            m.t[i] = GRASS if v != D.ROAD else PATH
    m.radius, m.sid, m.hid, m.signs = 60, None, None, []
    m.site, m.place = site.id, site.kind
    m.lights, m.glows = [], []
    cx, cy = lx - x0, ly - y0
    near = [m.tile(x, y) for y in range(cy - 6, cy + 7) for x in range(cx - 8, cx + 9) if m.inb(x, y)]
    walk = [v for v in near if v in GROUNDS and v != D.PATH]
    m.ground = max(set(walk), key=walk.count) if walk else GRASS
    m.centre = (cx, cy)
    return m


def clear(m, x0, y0, x1, y1, t=None, keep=()):
    """Clear a box of trees, rocks and water for a building: the place's own ground."""
    t = m.ground if t is None else t
    for y in range(max(0, y0), min(m.h, y1 + 1)):
        for x in range(max(0, x0), min(m.w, x1 + 1)):
            if m.tile(x, y) not in keep:
                m.set(x, y, t)


def trail(m, a, b, t=PATH, over=None):
    """A path from a to b that wanders a little; over water it is a plank bridge."""
    x, y = a
    k = 0
    while (x, y) != b:
        k += 1
        if abs(b[0] - x) >= abs(b[1] - y) or random.random() < .25:
            x += (b[0] > x) - (b[0] < x)
        else:
            y += (b[1] > y) - (b[1] < y)
        if k % 5 == 0 and random.random() < .35 and abs(b[0] - x) > 3:
            y += random.choice((-1, 1)) if 2 < y < m.h - 3 else 0
        if not m.inb(x, y):
            continue
        cur = m.tile(x, y)
        if over is not None and cur not in over:
            continue
        if cur in (D.WATER, D.SHALLOW, D.RIVER):
            m.set(x, y, D.BRIDGE)
        elif cur in (D.TREE, D.ROCK, D.CLIFF, D.SLOPE, GRASS, D.SAND, D.SNOW, D.SWAMP, D.GRIT, D.BAREROCK, D.HEDGE, D.THORNS):
            m.set(x, y, t)


def finish(m, door, entry_y=None):
    """The way in from the west edge of the map to the door, and everything seen (it is open land)."""
    ey = door[1] if entry_y is None else entry_y
    trail(m, (0, ey), (door[0] - 1, door[1]))
    m.set(0, ey, PATH)
    m.entry = (0, ey)
    for i in range(len(m.seen)):
        m.seen[i] = 1
    return m


def gen_map(game, site):
    """The map of a place on its own land."""
    if site.kind == 'tower':
        return tower_site(game, site)
    if site.kind == 'barrow':
        from . import barrows as BR
        return BR.site_map(game, site)
    if site.kind in HALLS:
        from . import halls as HL
        return HL.site_map(game, site)
    from . import temples as TP
    return TP.site_map(game, site)


def tower_site(game, site):
    from . import towers as TOW
    m = land(game, site, 80, 50)
    cx, cy = m.centre
    cx = max(16, min(m.w - 16, cx))
    cy = max(12, min(m.h - 12, cy))
    pe = people_of(site)
    st = TOW.STYLE[pe]
    clear(m, cx - 10, cy - 10, cx + 10, cy + 10, D.SHALLOW if st.get('stilts') and m.ground == D.SWAMP else None)
    if not getattr(site, 'tw', None):
        site.tw = TOW.plan(site, cx, cy, pe, site.storeys, site.state)
        site.tw['cellar'] = getattr(site, 'cellar', False)
    else:
        site.tw['cx'], site.tw['cy'] = cx, cy
    tw = site.tw
    door = TOW.ground(game, site, m, tw, friendly(game, site))
    m.tower = True
    up = tw['stairs'][0] if tw['stairs'] else None
    if up and site.state == 'whole':
        m.bar = {up: 2}
    finish(m, door)
    lit(m, [door])
    folk_tower(game, site, m, tw, door, up)
    m.made_tier = tier(game, site)
    return m


def folk_tower(game, site, m, tw, door, up):
    """The watch on the ground floor of a manned tower, foes in a hostile one, bandits or worse in a fallen one."""
    from . import towers as TOW
    cells = TOW.footprint(tw)
    inner = [c for c in cells - TOW.rim_of(cells) if D.TILES[m.tile(*c)].walk and c != up and m.tile(*c) not in (UP, DOWN)]
    random.shuffle(inner)
    pe = people_of(site)
    lvl = game.world.dungeons[site.floors].base
    if friendly(game, site):
        if pe in TOW.WATCH and inner:
            c = min(inner, key=lambda q: cheb(q[0], q[1], *up)) if up else inner[0]
            g = make_npc(game, f'{TOW.WATCH[pe][1]} on the stair', 'guard', '#c8c4b4', c[0], c[1], True)
            m.mons.append(g)
            m.warden = (c[0], c[1])
        return
    hold = getattr(site, 'holder', None) or pe
    if hold in ('beast', 'cellar'):
        return
    foes = TOW.FOES.get(hold) or ('bandit',)
    for c in inner[:2 if hold == 'bandits' else 1]:
        k = random.choice(foes)
        m.mons.append(make_monster(game, k, c[0], c[1], lvl))
    outside = [(x, y) for y in range(m.h) for x in range(m.w) if m.tile(x, y) == m.ground
               and 4 <= cheb(x, y, tw['cx'], tw['cy']) <= 12]
    for c in random.sample(outside, min(len(outside), 1 if hold == 'bandits' else 2)):
        m.mons.append(make_monster(game, random.choice(foes), c[0], c[1], lvl))


def lit(m, cells):
    m.glows = list(getattr(m, 'glows', [])) + [(x, y, (255, 190, 110), 3) for x, y in cells]
    m.lights = list(m.glows)


# ------------------------------------------------------------------ coming and going
def on_enter(game, site, m):
    """Arriving: who is here and what they make of you; in a hostile tower the watch sees you coming."""
    t = tier(game, site)
    pe = people_of(site)
    if site.kind in HALLS:
        from . import halls as HL
        return HL.on_enter(game, site, m)
    if site.kind == 'tower' and getattr(site, 'manned', False) and t < 0:
        site.alarm = game.day
        for o in m.mons:
            if not o.is_npc:
                o.awake = True
        game.msg('A shout comes down from the top of the tower: the watch has seen you coming!', 'bad')
    elif site.kind == 'tower' and site.state == 'whole' and t == 2:
        game.msg('The guard on the stair nods you through. The keeper will let you up.', 'info')
    elif site.kind == 'tower' and site.state == 'whole' and t >= 0:
        game.msg(f'The guard on the stair watches you. Only friends of the {PLURAL[pe]} go up.', 'info')
    elif site.kind == 'temple' and t == 0:
        game.msg(f'A warden stands at the door. Your name is not good with the {PLURAL[pe]}.', 'bad')
    elif site.kind == 'temple' and t < 0:
        game.msg(f'This is a holy place of the {PLURAL[pe]}, and they do not suffer strangers in it.', 'bad')
    elif site.kind == 'barrow':
        from . import aurora as AU
        AU.on_barrow(game)


def stale(game, site, m):
    """The map was made for a different welcome: make it again (the levels above and below stay)."""
    t = tier(game, site)
    old = getattr(m, 'made_tier', t)
    return (t < 0) != (old < 0)


def barred(game, x, y):
    """A warden in the way: returns turns spent (0) when you are stopped, None when you may go on."""
    from . import events as EV
    m = game.map
    need = m.bar.get((x, y))
    if need is None or getattr(m, 'forced', False):
        return None
    site = game.world.sites[m.site]
    if tier(game, site) >= need:
        return None
    pe = people_of(site)
    who = 'The guard on the stair' if site.kind == 'tower' else 'A warden'
    where = 'the stair up' if site.kind == 'tower' else 'the way down' if need >= 2 else 'the door'
    EV.ask(game, 'place_bar', who, f'"Not you." {who} stands in front of {where}. Only friends of the {PLURAL[pe]} '
           'come further. Push past, and it is a crime.', [('Push past', 'force'), ('Turn back', 'bye')], site=site.id)
    return 0


def r_bar(game, choice, ctx):
    from . import crime as CR
    if choice != 'force':
        return
    site = game.world.sites[ctx['site']]
    m = game.map
    m.forced = True
    site.forced = game.day
    game.msg('You shove past. Shouts follow you.', 'bad')
    CR.commit(game, 8, f'forcing your way into {site.name}', .9, (site.x, site.y))


def stairs(game, t, d):
    """Stairs that belong to a place: up a tower, down into a crypt, cellar or barrow, and back. Returns the turns
    spent, or None when these stairs are not a place's."""
    m = game.map
    if getattr(m, 'tribe', None) == 'ravine':
        from . import gobvillage as GV
        return GV.stairs(game, t, d)
    if getattr(m, 'place', None) and getattr(m, 'site', None) is not None:
        site = game.world.sites[m.site]
        if t == UP and d != 'down':
            did = tower_dg(game, site)
            if did is None:
                return None
            game.enter_dungeon(did, 1, 'down')
            return 1
        if t == DOWN and d != 'up' and getattr(site, 'below', None):
            if site.kind == 'barrow':
                from . import aurora as AU
                if AU.guard_down(game, site):
                    return 0
            game.enter_dungeon(site.below, 1, 'up')
            return 1
        return None
    if m.kind != 'dungeon':
        return None
    dg = game.world.dungeons.get(m.did)
    if dg is None or getattr(dg, 'site', None) is None:
        return None
    site = game.world.sites[dg.site]
    if getattr(dg, 'rise', False):
        if t == UP and d != 'down':
            game.enter_dungeon(dg.id, m.depth + 1, 'down')
            return 1
        if t == DOWN and d != 'up':
            if m.depth == 1:
                back(game, site, UP)
            else:
                game.enter_dungeon(dg.id, m.depth - 1, 'up')
            return 1
        return None
    if t == UP and d != 'down' and m.depth == 1:
        back(game, site, DOWN, getattr(dg, 'home', None))
        return 1
    if t == DOWN and d != 'up' and m.depth >= dg.depth and getattr(m, 'ancient', False):
        game.enter_dungeon(dg.id, m.depth + 1, 'up')
        return 1
    return None


def back(game, site, tile, home=None):
    """Out of a tower or up out of a crypt: back onto the place's own map, on its stair."""
    p = game.player
    home = home or site.map_key
    if home not in game.maps:
        if home != site.map_key:
            from . import gobvillage as GV
            game.maps[home] = GV.make(game, site)
        else:
            from .sites import gen_site_map
            game.maps[home] = gen_site_map(game, site)
    game.cur = home
    m = game.map
    spot = None
    if tile in m.t:
        i = m.t.index(tile)
        spot = (i % m.w, i // m.w)
    p.x, p.y = spot or (m.entry[0] + 1, m.entry[1])
    game.msg('You climb down again.' if tile == UP else 'You climb back up into the daylight.', 'info')
    game.compute_fov()
    game.request = ('save',)


def bump(game, x, y):
    """The telling things of a place's own map. Returns turns spent, or None when it is not one of them."""
    from . import gods as GD
    m = game.map
    t = m.tile(x, y)
    if (x, y) in getattr(m, 'things', ()):
        return None                             # a telling thing of its own (halls.py, themes.py)
    site = game.world.sites[m.site] if getattr(m, 'site', None) is not None else None
    if t == D.ALTAR and site is not None and site.kind == 'temple':
        if people_of(site) in HOSTILE and tier(game, site) < 2:
            game.msg({'orc': 'The blood altar of the war god. It is sticky, and not with wine.',
                      'goblin': 'An idol of junk and its heap of offerings. Something here is watching you.',
                      'kobold': 'A shrine to shine: coins, a polished mirror and candles. Take nothing.',
                      'gnoll': 'An altar of skulls, picked clean. The bone-caller speaks to the moon here.',
                      'lizard': 'The egg altar, warm in the sun. The eggs on it are stone.'}.get(people_of(site), 'An altar.'))
            return 0
        game.msg(GD.pray(game, GD.temple_god(game)), 'info')
        return 1
    if t == D.BELL:
        game.msg('You pull the rope. The bell booms out over the land.', 'info')
        for o in m.mons:
            if not o.is_npc:
                o.awake = True
        return 1
    if t == D.DRUM:
        game.msg('You beat the drum. Boom. Boom. Far off, something answers.', 'info')
        return 1
    if t == D.HORN:
        game.msg('You blow the bone horn. It moans over the land like a beast.', 'info')
        return 1
    if t == D.GONG:
        game.msg('You strike the gong. Every goblin for a league knows you are here now.', 'info')
        for o in m.mons:
            if not o.is_npc:
                o.awake = True
        return 1
    if t == D.MIRROR and getattr(m, 'sky', None) is not None:
        game.msg('A polished shield on a pole: turned to the sun, it flashes a warning far over the land.', 'info')
        return 0
    if t == D.BOLTS:
        game.msg('A bolt thrower on a swivel, loaded and pointing at the road.', 'info')
        return 0
    if t == D.CRYSTAL:
        game.msg('The crystal glows from within. Your own face looks back at you from deep inside it.', 'info')
        return 0
    if t == D.IDOL:
        game.msg('An idol of junk: pots, a helmet, a doll, nails. Its glass eyes follow you.', 'info')
        return 0
    if t == D.BLOODPIT:
        game.msg('A pit of old blood, thick and dark. The flies love it.', 'info')
        return 0
    if t == D.STONE:
        game.msg('A standing stone, older than anyone remembers. It is cold under your hand.', 'info')
        return 0
    if t == D.FOUNTAIN and getattr(m, 'moonwell', None) == (x, y):
        p = game.player
        if getattr(p, 'moonwell_day', -1) == game.day:
            game.msg('The moonwell is still. You have drunk from it today.', 'info')
            return 0
        p.moonwell_day = game.day
        p.mana = game.stats()['max_mana']
        game.msg('You drink from the moonwell. The water is cold as starlight, and your mind clears.', 'good')
        return 1
    return None


# ------------------------------------------------------------------ the hidden bottom
def hidden_temples(game):
    return [q for q in game.world.sites if q.kind == 'temple' and getattr(game.world.dungeons.get(getattr(q, 'below', None)), 'older', False)]


def rumour(game):
    """A tale of a temple built over something older, when there is one you have not heard of."""
    from .engine import dir_name
    p = game.player
    known = p.__dict__.setdefault('old_bottoms', set())
    ox, oy = game.world_pos()
    cands = [q for q in hidden_temples(game) if q.id not in known and cheb(q.x, q.y, ox, oy) < 90]
    if not cands:
        return None
    q = min(cands, key=lambda c: cheb(c.x, c.y, ox, oy))
    known.add(q.id)
    game.reveal_place(q.x, q.y)
    return (f'They say {q.name}, to the {dir_name(q.x - ox, q.y - oy)}, was built over something older. Right at the '
            'bottom of its deep place a flagstone lies loose, and under it a way goes on down.')


def loose_step(game):
    """Standing on the loose flagstone of a temple's last level: if you know the tale, it lifts."""
    m, p = game.map, game.player
    if m.tile(p.x, p.y) != D.LOOSE:
        return
    dg = game.world.dungeons.get(m.did)
    site = game.world.sites[dg.site]
    if site.id in p.__dict__.get('old_bottoms', set()) or random.random() < .08:
        p.__dict__.setdefault('old_bottoms', set()).add(site.id)
        m.set(p.x, p.y, DOWN)
        m.ancient = True
        game.msg('A flagstone rocks under your foot. You lift it: steps go down into the dark, older than the walls '
                 'round you.', 'unique')


def bottom(game, m, dg):
    """The last level of a temple's deep place: the way to the older bottom lies under a loose flagstone."""
    floors = [i for i, t in enumerate(m.t) if t == FLOOR]
    up = m.t.index(UP) if UP in m.t else 0
    far = [i for i in floors if cheb(i % m.w, i // m.w, up % m.w, up // m.w) > 12] or floors
    if far:
        i = random.choice(far)
        m.t[i] = D.LOOSE


def ancient(game, m, dg):
    """The older thing a temple was built over: a ring of standing stones in a cave, and what guards it."""
    from .worldgen import rand_free, place_chest
    from .entities import make_tome
    floors = [i for i, t in enumerate(m.t) if t == FLOOR]
    if not floors:
        return
    c = max(floors, key=lambda i: sum(1 for o in (1, -1, m.w, -m.w, m.w + 1, m.w - 1, -m.w + 1, -m.w - 1)
                                      if 0 <= i + o < len(m.t) and m.t[i + o] == FLOOR))
    cx, cy = c % m.w, c // m.w
    import math
    for k in range(8):
        a = k / 8 * math.tau
        x, y = round(cx + math.cos(a) * 4), round(cy + math.sin(a) * 3)
        if m.inb(x, y) and m.tile(x, y) == FLOOR:
            m.set(x, y, D.STONE)
    o = make_monster(game, 'wight' if 'wight' in D.MONSTERS else 'wraith', cx, cy, m.level + 2, 2)
    o.name = 'The Old Warden'
    o.fg = D.UNIQUE_FG
    m.mons.append(o)
    place_chest(m)
    spot = rand_free(game, m, lambda t: t == FLOOR)
    if spot:
        tm = make_tome(game, m.level + 3)
        tm.x, tm.y = spot
        m.items.append(tm)
    m.mood_line = 'Older than the temple above: a cave, a ring of standing stones, and something that waited.'


from . import events as _EV                             # noqa: E402
_EV.RESOLVERS['place_bar'] = r_bar
