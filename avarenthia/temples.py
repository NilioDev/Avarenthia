"""Temples of every people (round 6), each a middle place, 100 x 60, on its own land (places.land).

Human: a nave with pews and two rows of pillars, a transept with a chapel at each end, the choir with the altar, the
sacristy (the way down) and the priest's room; a churchyard, a garden, and sometimes a bell tower with a lookout.
Elf: no walls and no roof, glades in the old wood joined by paths of white stone round the moonwell; the eldest
tree has a stair up into its crown. Dwarf: the hall of the forefathers cut into the rock. Halfling: a round hearth
chapel in a hedged garden. Gnome: a hollow under the roots, a ring of glowing mushrooms round a crystal. Orc: a
palisade ring round the ring of blood. Goblin: a cave nook with an idol of junk. Kobold: a shrine to shine. Gnoll:
a ring of bone poles in a hedge of thorns. Lizardfolk: a stepped mound in the swamp with the egg altar on top.

Below every temple lies its own deep place, 3 to 5 levels, older and rougher the deeper you go; some were built
over something older still, under a loose flagstone at the bottom (places.bottom)."""
import math
import random

from . import data as D
from .data import FLOOR, WALL, DOOR, PATH, UP, DOWN, PLANK
from .entities import make_npc, make_monster
from .worldgen import cheb
from . import places as PL

W, H = 100, 60
FOES = {'orc': ('orc_shaman', ('orc', 'orc_spear', 'orc_berserker'), 'worg'),
        'goblin': ('gob_shaman', ('goblin', 'gobarcher', 'gob_sneak'), None),
        'kobold': ('kob_sorcerer', ('kobold', 'kob_slinger', 'kob_trapper'), None),
        'gnoll': ('gnoll_caller', ('gnoll_hunter',), 'hyena'),
        'lizard': ('lizard_shaman', ('lizard_warrior', 'lizard_spear'), 'crocodile')}
LOOK = {'orc': ('o', '#8cbc5a'), 'goblin': ('g', '#bec85a'), 'kobold': ('k', '#d28c50'), 'gnoll': ('n', '#c8a05a'),
        'lizard': ('l', '#64aa64')}
PRIEST = {'human': 'Sister {n}', 'elf': '{n}, Priestess of the Glades', 'dwarf': 'Hearthpriest {n}',
          'halfling': 'Mother {n}', 'gnome': '{n} the Lamp-Keeper'}
MOOD = {'human': ("The priests' crypt. Neat rows of tombs, and candles someone still lights.",
                  'Old catacombs. The niches here were cut long before the temple above.'),
        'elf': ('The root halls. Roots thick as pillars hold up the earth overhead.',
                'Deeper, the roots give way to raw rock and the dark.'),
        'dwarf': ('The tombs of the forefathers. Stone faces watch from every wall.', 'Older halls, rough-hewn and cold.'),
        'halfling': ('The cellars: jars and casks, and a door that should have stayed shut.', 'Earth and old roots.'),
        'gnome': ('The deep hollows, lit here and there by a crystal.', 'The crystals give out. Only rock now.'),
        'orc': ('The cave of the war god. The cells at the top stink of fear.', 'Down to the blood altar.'),
        'goblin': ('Holes under the shrine, heaped with what they stole.', 'Deeper holes, older and wetter.'),
        'kobold': ('The shine pits: little tunnels full of glints.', 'The pits go down and down.'),
        'gnoll': ('The burrows, dug with claws.', 'Down to the bone pit of the bone-caller.'),
        'lizard': ('The drowned halls. Water stands to your knees.', 'Deeper and darker water.')}


def site_map(game, site):
    pe = PL.people_of(site)
    m = PL.land(game, site, W, H)
    cx, cy = m.centre
    cx = max(38, min(W - 34, cx))
    cy = max(22, min(H - 22, cy))
    m.centre = (cx, cy)
    friendly = PL.tier(game, site) >= 0
    door = BUILD[pe](game, site, m, cx, cy, friendly)
    weather(m)
    PL.finish(m, door)
    m.made_tier = PL.tier(game, site)
    m.place = 'temple'
    return m


# ------------------------------------------------------------------ building blocks
def box(m, x0, y0, x1, y1, wall=WALL, floor=FLOOR):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            m.set(x, y, wall if y in (y0, y1) or x in (x0, x1) else floor)


def rock(m, x0, y0, x1, y1):
    """A hill of rock to dig the temple into; weather() wears its rim ragged afterwards."""
    under = m.__dict__.setdefault('_under', {})
    for y in range(max(0, y0), min(H, y1 + 1)):
        for x in range(max(0, x0), min(W, x1 + 1)):
            under.setdefault((x, y), m.tile(x, y))
            m.set(x, y, D.ROCK)
    m._hill = ((x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2 + .5, (y1 - y0) / 2 + .5)


def weather(m):
    """Wear the hill's straight rim back to the land beneath, never within two steps of what was dug."""
    under = m.__dict__.pop('_under', None)
    if not under:
        return
    dug = [(x, y) for (x, y) in under if m.tile(x, y) != D.ROCK]
    near = {(x + dx, y + dy) for x, y in dug for dx in range(-2, 3) for dy in range(-2, 3)}
    hx, hy, rx, ry = m.__dict__.pop('_hill')
    worn = set()
    for (x, y), t in under.items():                                    # round the corners off
        if (x, y) not in near and abs((x - hx) / rx) ** 2.6 + abs((y - hy) / ry) ** 2.6 > .9 + random.random() * .12:
            m.set(x, y, t)
            worn.add((x, y))
    for _ in range(3):
        gone = []
        for (x, y), t in under.items():
            if (x, y) in worn or (x, y) in near or m.tile(x, y) != D.ROCK:
                continue
            open_ = sum(1 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                        if (x + dx, y + dy) not in under or (x + dx, y + dy) in worn)
            if open_ and random.random() < .22 * open_:
                gone.append((x, y, t))
        for x, y, t in gone:
            m.set(x, y, t)
            worn.add((x, y))


def oval(cx, cy, rx, ry):
    return [(x, y) for y in range(cy - ry, cy + ry + 1) for x in range(cx - rx, cx + rx + 1)
            if ((x - cx) / (rx + .5)) ** 2 + ((y - cy) / (ry + .5)) ** 2 <= 1]


def ring_of(cells):
    s = set(cells)
    return [(x, y) for x, y in cells if any((x + dx, y + dy) not in s for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]


def rounded(m, cx, cy, rx, ry, wall, floor):
    cells = oval(cx, cy, rx, ry)
    edge = set(ring_of(cells))
    for x, y in cells:
        m.set(x, y, wall if (x, y) in edge else floor)
    return cells


def npc(game, m, name, role, fg, x, y, stay=True, ch='☺'):
    if not D.TILES[m.tile(x, y)].walk:
        m.set(x, y, FLOOR)
    n = make_npc(game, name, role, fg, x, y, stay, ch=ch)
    m.mons.append(n)
    return n


def folk(game, m, site, cells, n, job='acolyte', fg='#d8d0c0'):
    from .towns import townsfolk, town_names
    pe = PL.people_of(site)
    try:
        names = town_names(pe)
    except Exception:
        names = ['A worshipper'] * 6
    cs = [c for c in cells if D.TILES[m.tile(*c)].walk and not m.mon_at(*c)]
    random.shuffle(cs)
    for c in cs[:n]:
        townsfolk(game, m, [c], c, names, job, fg=fg)


def priest(game, site, m, x, y):
    start = getattr(game.world, 'start_temple', None) == site.id
    pe = PL.people_of(site)
    name = 'Sister Ilse Marsh' if start else PRIEST.get(pe, 'Brother {n}').format(n=PL.a_name(pe))
    return npc(game, m, name, 'healer', '#f4f0e6', x, y)


def warden(game, site, m, x, y, cell, need=2):
    """A warden who keeps the way: stands beside `cell`, which only those with `need` standing may pass."""
    pe = PL.people_of(site)
    npc(game, m, f'A {PL.ADJ[pe]} warden', 'guard', '#c8c4b4', x, y)
    m.bar = getattr(m, 'bar', {})
    m.bar[cell] = need


def foes(game, site, m, cells, n, chief_at=None):
    """The fighters of a hostile people's temple, or (to its friends) the same people going about their business."""
    pe = PL.people_of(site)
    chief, rank, beast = FOES[pe]
    lvl = game.world.dungeons[site.below].base + 1
    friend = PL.tier(game, site) >= 0
    cs = [c for c in cells if D.TILES[m.tile(*c)].walk and not m.mon_at(*c)]
    random.shuffle(cs)
    if chief_at:
        cs.insert(0, chief_at)
    for k, c in enumerate(cs[:n]):
        key = chief if k == 0 and chief_at else random.choice(rank)
        if friend:
            ch, fg = LOOK[pe]
            nm = D.MONSTERS[key]['name']
            npc(game, m, f'{nm} of {site.name}' if k == 0 and chief_at else f'A {nm.lower()}', 'villager', fg, c[0], c[1],
                stay=k == 0, ch=ch)
        else:
            o = make_monster(game, key, c[0], c[1], lvl + (1 if k == 0 and chief_at else 0), 1 if k == 0 and chief_at else 0)
            m.mons.append(o)
    return cs


def beasts(game, site, m, cells, n):
    pe = PL.people_of(site)
    beast = FOES[pe][2]
    if not beast or beast not in D.MONSTERS or PL.tier(game, site) >= 0:
        return
    lvl = game.world.dungeons[site.below].base
    cs = [c for c in cells if D.TILES[m.tile(*c)].walk and not m.mon_at(*c)]
    for c in random.sample(cs, min(n, len(cs))):
        m.mons.append(make_monster(game, beast, c[0], c[1], lvl))


def bell_tower(game, site, m, x0, y0, door):
    """A 5 x 5 bell tower whose walls were drawn already; its stair up and the tower plan for its floors."""
    from . import towers as TOW
    cx, cy = x0 + 2, y0 + 2
    site.tw = TOW.plan(site, cx, cy, 'bell', random.randint(3, 4), seed=site.id * 31 + 7)
    site.tw['bell'] = True
    up = site.tw['stairs'][0]
    if cheb(up[0], up[1], *door) <= 1 and len(site.tw['stairs']) > 1:
        site.tw['stairs'][0], site.tw['stairs'][1] = site.tw['stairs'][1], site.tw['stairs'][0]
        up = site.tw['stairs'][0]
    m.set(up[0], up[1], UP)
    m.bar = getattr(m, 'bar', {})
    m.bar[up] = 1


# ------------------------------------------------------------------ the human temple
def human(game, site, m, cx, cy, friendly):
    PL.clear(m, cx - 34, cy - 20, cx + 30, cy + 20)
    # the churchyard wall, with its gate to the west
    for x in range(cx - 30, cx + 29):
        for y in (cy - 18, cy + 18):
            m.set(x, y, D.FENCE)
    for y in range(cy - 18, cy + 19):
        for x in (cx - 30, cx + 28):
            m.set(x, y, D.FENCE)
    for y in (cy - 1, cy, cy + 1):
        m.set(cx - 30, y, PATH)
    box(m, cx - 24, cy - 3, cx - 19, cy + 3)                        # the porch
    box(m, cx - 19, cy - 6, cx + 6, cy + 6)                         # the nave
    box(m, cx + 6, cy - 13, cx + 13, cy + 13)                       # the transept
    for y in range(cy - 5, cy + 6):
        m.set(cx + 6, y, FLOOR)
    box(m, cx + 13, cy - 6, cx + 24, cy + 6)                        # the choir
    for y in range(cy - 4, cy + 5):
        m.set(cx + 13, y, FLOOR)
    box(m, cx + 13, cy + 6, cx + 24, cy + 13)                       # the sacristy
    box(m, cx + 13, cy - 13, cx + 24, cy - 6)                       # the priest's room
    for y in range(cy - 13, cy + 14):                                # mend the shared walls
        m.set(cx + 13, y, WALL if abs(y - cy) > 4 else FLOOR)
    for y in (cy - 6, cy + 6):
        for x in range(cx + 13, cx + 25):
            m.set(x, y, WALL)
    m.set(cx - 24, cy, DOOR)
    m.set(cx - 19, cy, DOOR)
    sac, room = (cx + 18, cy + 6), (cx + 18, cy - 6)
    m.set(*sac, DOOR)
    m.set(*room, DOOR)
    for x in range(cx - 16, cx + 5, 3):                             # two rows of pillars
        m.set(x, cy - 3, D.PILLAR)
        m.set(x, cy + 3, D.PILLAR)
    for x in range(cx - 15, cx + 4, 2):                             # pews facing the altar, an aisle down the middle
        if (x - (cx - 16)) % 3 == 0:
            continue
        for y in (cy - 2, cy - 1, cy + 1, cy + 2):
            m.set(x, y, D.PEW)
    altar = (cx + 21, cy)
    m.set(*altar, D.ALTAR)
    for y in (cy - 2, cy + 2):
        m.set(cx + 22, y, D.STATUE)
    m.set(cx + 9, cy - 11, D.STATUE)                                # the two chapels at the ends of the transept
    m.set(cx + 10, cy - 11, D.ALTAR)
    m.set(cx + 9, cy + 11, D.STATUE)
    m.set(cx + 10, cy + 11, D.ALTAR)
    for x in (cx + 8, cx + 11):
        m.set(x, cy - 9, D.PEW)
        m.set(x, cy + 9, D.PEW)
    m.set(cx + 22, cy + 10, DOWN)                                   # the way down, in the sacristy
    m.set(cx + 15, cy + 8, D.SHELVES)
    m.set(cx + 16, cy + 8, D.TABLE)
    m.set(cx + 22, cy - 10, D.BED)
    m.set(cx + 16, cy - 10, D.TABLE)
    m.set(cx + 15, cy - 8, D.SHELVES)
    for x in range(cx - 26, cx + 4, 3):                             # the graves, north of the nave
        for y in (cy - 16, cy - 13, cy - 10):
            if x < cx - 24 and y == cy - 10:
                continue
            m.set(x, y, D.GRAVE)
    for y in range(cy + 9, cy + 16):                                # the garden, south
        for x in range(cx - 26, cx - 4):
            m.set(x, y, D.FIELD if y % 2 else m.ground)
    m.set(cx - 2, cy + 12, D.WELL)
    if getattr(site, 'bell', False):
        box(m, cx - 23, cy - 7, cx - 19, cy - 3)                     # the bell tower, against the porch and the nave
        m.set(cx - 21, cy - 3, DOOR)
        bell_tower(game, site, m, cx - 23, cy - 7, (cx - 21, cy - 3))
    priest(game, site, m, cx + 19, cy)
    folk(game, m, site, [(x, y) for x in range(cx - 14, cx + 4) for y in (cy - 4, cy + 4)], 2)
    warden(game, site, m, cx + 19, cy + 5, sac, 2)
    m.bar[(cx - 19, cy)] = 1
    m.bar[(cx - 24, cy)] = 1
    m.signs.append((cx - 26, cy - 5, 'TEMPLE'))
    PL.lit(m, [(cx + 20, cy - 1), (cx + 20, cy + 1), (cx - 21, cy)])
    m.altar = altar
    return (cx - 30, cy)


# ------------------------------------------------------------------ elves: glades in the old wood
def elf(game, site, m, cx, cy, friendly):
    from . import towers as TOW
    for y in range(max(0, cy - 26), min(H, cy + 27)):
        for x in range(max(0, cx - 44), min(W, cx + 44)):
            if m.tile(x, y) not in (D.WATER,) and random.random() < .9:
                m.set(x, y, D.TREE)
    glades = {'great': (cx, cy, 11, 7), 'songs': (cx - 22, cy - 11, 7, 4), 'healers': (cx - 22, cy + 11, 7, 4),
              'fallen': (cx + 20, cy + 12, 7, 4), 'tree': (cx + 21, cy - 11, 8, 5)}
    for gx, gy, rx, ry in glades.values():
        for x, y in oval(gx, gy, rx, ry):
            if m.inb(x, y):
                m.set(x, y, D.GRASS)
    for a, b in (('great', 'songs'), ('great', 'healers'), ('great', 'fallen'), ('great', 'tree')):
        ga, gb = glades[a], glades[b]
        PL.trail(m, (ga[0], ga[1]), (gb[0], gb[1]), D.WHITE)
    # the moonwell, ringed by stones
    m.set(cx, cy, D.FOUNTAIN)
    m.moonwell = (cx, cy)
    for k in range(10):
        a = k / 10 * math.tau
        m.set(round(cx + math.cos(a) * 5), round(cy + math.sin(a) * 3), D.STONE)
    for x, y in oval(cx, cy, 1, 1):
        if (x, y) != (cx, cy):
            m.set(x, y, D.WHITE)
    gx, gy = glades['songs'][:2]
    for k in range(6):
        a = k / 6 * math.tau
        m.set(round(gx + math.cos(a) * 4), round(gy + math.sin(a) * 2), D.STONE)
    hx, hy = glades['healers'][:2]
    for x in range(hx - 4, hx + 5):
        for y in (hy - 1, hy + 1):
            m.set(x, y, D.FIELD)
    fx, fy = glades['fallen'][:2]
    for x in range(fx - 4, fx + 5, 2):
        for y in (fy - 2, fy + 1):
            m.set(x, y, D.GRAVE)
    # the eldest tree: a hollow trunk with a stair winding up into the crown, and the root halls below
    tx, ty = glades['tree'][:2]
    site.tw = TOW.plan(site, tx, ty, 'elftree', random.randint(4, 5), seed=site.id * 17 + 3)
    cells = TOW.footprint(site.tw)
    rim = TOW.rim_of(cells)
    for x, y in cells:
        m.set(x, y, D.TRUNK if (x, y) in rim else PLANK)
    tdoor = min((c for c in rim if c[1] >= ty), key=lambda c: (c[0], -c[1]))
    m.set(*tdoor, D.ODOOR)
    up = site.tw['stairs'][0]
    if cheb(up[0], up[1], *tdoor) <= 1:
        site.tw['stairs'].reverse()
        up = site.tw['stairs'][0]
    m.set(*up, UP)
    inner = [c for c in cells - rim if m.tile(*c) == PLANK and cheb(c[0], c[1], *up) >= 2 and cheb(c[0], c[1], *tdoor) >= 2]
    down = random.choice(inner) if inner else (tx, ty)
    m.set(*down, DOWN)
    for k in range(8):                                               # its roots run out over the glade
        a = k / 8 * math.tau
        for r in (6, 7):
            x, y = round(tx + math.cos(a) * r), round(ty + math.sin(a) * r * .7)
            if m.inb(x, y) and m.tile(x, y) == D.GRASS and random.random() < .6:
                m.set(x, y, D.ROOT)
    m.wall_fg = (222, 234, 216)
    priest(game, site, m, cx + 2, cy + 3)
    folk(game, m, site, oval(gx, gy, 3, 1), 2, 'singer', '#e0e8d0')
    folk(game, m, site, oval(fx, fy, 3, 1), 1, 'mourner', '#c0c8c0')
    folk(game, m, site, oval(hx, hy, 3, 2), 1, 'herb-warden', '#90d080')
    warden(game, site, m, tdoor[0] - 1, tdoor[1] + (1 if tdoor[1] < H - 2 else 0), tdoor, 2)
    m.glows = [(x, y, (190, 230, 255), 3) for x, y in ((cx - 4, cy - 2), (cx + 4, cy + 2), (gx, gy), (fx, fy), (tx, ty + 6))]
    m.lights = list(m.glows)
    m.altar = (cx, cy)
    return (cx - 11, cy)


# ------------------------------------------------------------------ dwarves: the hall of the forefathers in the rock
def dwarf(game, site, m, cx, cy, friendly):
    rock(m, cx - 22, cy - 24, cx + 39, cy + 24)
    PL.clear(m, cx - 34, cy - 8, cx - 21, cy + 8)
    box(m, cx - 20, cy - 6, cx + 14, cy + 6)                         # the hall of the forefathers
    m.set(cx - 20, cy, DOOR)
    m.set(cx - 20, cy - 1, DOOR)
    for x in range(cx - 16, cx + 12, 3):                             # the forefathers in stone along both walls
        m.set(x, cy - 5, D.STATUE)
        m.set(x, cy + 5, D.STATUE)
    for x in range(cx - 14, cx + 10, 4):
        m.set(x, cy - 2, D.PILLAR)
        m.set(x, cy + 2, D.PILLAR)
    altar = (cx + 12, cy)
    m.set(*altar, D.ALTAR)                                           # the forge altar
    m.set(cx + 12, cy - 2, D.ANVIL)
    m.set(cx + 12, cy + 2, D.FIREPIT)
    box(m, cx - 10, cy - 14, cx + 2, cy - 6)                         # the hearthpriest's room
    box(m, cx - 10, cy + 6, cx + 2, cy + 14)                         # the stair down to the tombs
    room, stair = (cx - 4, cy - 6), (cx - 4, cy + 6)
    m.set(*room, DOOR)
    m.set(*stair, DOOR)
    m.set(cx - 8, cy - 12, D.BED)
    m.set(cx - 6, cy - 12, D.TABLE)
    m.set(cx, cy - 12, D.SHELVES)
    m.set(cx - 4, cy + 12, DOWN)
    m.set(cx - 8, cy + 8, D.STATUE)
    m.set(cx, cy + 8, D.STATUE)
    box(m, cx + 14, cy - 4, cx + 22, cy + 4)                         # the brazier hall behind the altar
    m.set(cx + 14, cy, DOOR)
    m.set(cx + 19, cy, D.FIREPIT)
    m.set(cx + 18, cy - 3, D.BARREL)
    m.set(cx + 18, cy + 3, D.BARREL)
    m.wall_fg = (176, 150, 120)
    priest(game, site, m, cx + 10, cy)
    folk(game, m, site, [(x, y) for x in range(cx - 15, cx + 9) for y in (cy - 3, cy + 3, cy)], 2, 'mourner', '#d8b890')
    warden(game, site, m, cx - 3, cy + 5, stair, 2)
    m.bar[(cx - 20, cy)] = 1
    m.bar[(cx - 20, cy - 1)] = 1
    PL.lit(m, [(cx + 11, cy + 1), (cx + 19, cy + 1), (cx - 19, cy + 2)])
    m.altar = altar
    return (cx - 34, cy)


# ------------------------------------------------------------------ halflings: the hearth chapel in its garden
def halfling(game, site, m, cx, cy, friendly):
    PL.clear(m, cx - 26, cy - 17, cx + 26, cy + 17)
    hedge = oval(cx, cy, 23, 14)
    for x, y in ring_of(hedge):
        m.set(x, y, D.HEDGE)
    for y in (cy - 1, cy, cy + 1):
        m.set(cx - 23, y, PATH)
    for y in range(cy - 11, cy + 12):                                # vegetable beds and an orchard
        for x in range(cx - 20, cx - 8):
            if y < cy - 3 and (x + y) % 2 == 0 and ((x - cx) / 23.5) ** 2 + ((y - cy) / 14.5) ** 2 < .8:
                m.set(x, y, D.FIELD)
    for x in range(cx + 13, cx + 20, 3):
        for y in range(cy - 9, cy + 10, 3):
            if ((x - cx) / 23.5) ** 2 + ((y - cy) / 14.5) ** 2 < .8:
                m.set(x, y, D.TREE)
    rounded(m, cx, cy, 9, 6, WALL, PLANK)
    door = (cx - 9, cy)
    m.set(*door, DOOR)
    m.round_doors = True
    altar = (cx + 6, cy)
    m.set(*altar, D.ALTAR)
    m.set(cx + 6, cy - 2, D.FIELD)
    m.set(cx + 6, cy + 2, D.FIELD)
    m.set(cx, cy - 4, D.HEARTH)
    for x in (cx - 5, cx - 3, cx - 1, cx + 1):
        for y in (cy - 2, cy - 1, cy + 1, cy + 2):
            m.set(x, y, D.PEW)
    m.set(cx + 3, cy + 4, DOWN)                                      # a hatch to the cellars
    priest(game, site, m, cx + 4, cy)
    folk(game, m, site, [(x, y) for x in range(cx - 18, cx - 6) for y in range(cy + 4, cy + 10)], 2, 'gardener', '#c8d090')
    warden(game, site, m, cx + 2, cy + 3, (cx + 3, cy + 4), 2)
    m.bar[door] = 1
    PL.lit(m, [(cx, cy - 3), (cx + 5, cy + 1)])
    m.altar = altar
    return (cx - 23, cy)


# ------------------------------------------------------------------ gnomes: a hollow under the roots
def gnome(game, site, m, cx, cy, friendly):
    for y in range(max(0, cy - 20), min(H, cy + 21)):
        for x in range(max(0, cx - 30), min(W, cx + 30)):
            m.set(x, y, D.TREE if random.random() < .7 else m.ground)
    PL.clear(m, cx - 24, cy - 1, cx - 8, cy + 1)
    for x, y in oval(cx, cy - 9, 12, 3):                             # the roots over the hollow
        if m.inb(x, y):
            m.set(x, y, D.ROOT)
    rounded(m, cx, cy, 9, 6, D.EARTH, FLOOR)
    door = (cx - 9, cy)
    m.set(*door, DOOR)
    crystal = (cx + 1, cy)
    m.set(*crystal, D.CRYSTAL)
    for k in range(10):
        a = k / 10 * math.tau
        m.set(round(cx + 1 + math.cos(a) * 4), round(cy + math.sin(a) * 2.5), D.SHROOM)
    box(m, cx + 9, cy - 3, cx + 15, cy + 3, D.EARTH, FLOOR)          # the lamp-keeper's nook, and the way down
    m.set(cx + 9, cy, DOOR)
    m.set(cx + 13, cy + 1, DOWN)
    m.set(cx + 13, cy - 2, D.SHELVES)
    priest(game, site, m, cx - 3, cy + 2)
    folk(game, m, site, [(x, y) for x in range(cx - 6, cx + 7) for y in (cy - 4, cy + 4)], 2, 'tinker', '#e0cc80')
    warden(game, site, m, cx + 7, cy + 2, (cx + 9, cy), 2)
    m.bar[door] = 1
    m.glows = [(cx + 1, cy, (120, 230, 255), 5)] + [(round(cx + 1 + math.cos(k) * 4), round(cy + math.sin(k) * 2.5),
                                                      (220, 120, 90), 2) for k in range(0, 6, 2)]
    m.lights = list(m.glows)
    m.altar = crystal
    return (cx - 24, cy)


# ------------------------------------------------------------------ orcs: the ring of blood
def orc(game, site, m, cx, cy, friendly):
    from .tribes import round_hut
    PL.clear(m, cx - 30, cy - 19, cx + 30, cy + 19)
    wall = oval(cx, cy, 27, 17)
    for x, y in ring_of(wall):
        m.set(x, y, D.PALISADE)
    for y in (cy - 1, cy, cy + 1):
        m.set(cx - 27, y, PATH)
    for x, y in oval(cx, cy, 1, 1):
        m.set(x, y, D.BLOODPIT)
    m.set(cx, cy - 4, D.TOTEM)
    for k in range(12):                                              # the ring of blood
        a = k / 12 * math.tau
        if k % 3:
            m.set(round(cx + math.cos(a) * 7), round(cy + math.sin(a) * 4.5), D.STAKES)
    box(m, cx + 7, cy - 14, cx + 22, cy - 6, D.HIDE, FLOOR)           # the warchief's long hall
    m.set(cx + 14, cy - 6, DOOR)
    m.set(cx + 20, cy - 10, D.HIGHSEAT)
    for x in (cx + 10, cx + 15):
        m.set(x, cy - 10, D.FIREPIT)
    hut = round_hut(m, cx - 13, cy - 9, 4, 3, D.HIDE, FLOOR)          # the shaman's hut, and the cave below it
    m.set(cx - 13, cy - 6, DOOR)
    m.set(cx - 13, cy - 10, D.ALTAR)
    m.set(cx - 11, cy - 9, DOWN)
    round_hut(m, cx - 13, cy + 9, 4, 3, D.HIDE, FLOOR)                # the trophy hut
    m.set(cx - 13, cy + 6, DOOR)
    m.set(cx - 14, cy + 10, D.TOTEM)
    m.set(cx - 12, cy + 10, D.BONES)
    for y in range(cy + 6, cy + 10):                                  # the cage of captives
        m.set(cx + 6, y, D.CAGE)
    for x in range(cx + 10, cx + 21):                                 # the warg pen
        for y in (cy + 5, cy + 12):
            m.set(x, y, D.FENCE)
    for y in range(cy + 5, cy + 13):
        for x in (cx + 10, cx + 20):
            m.set(x, y, D.FENCE)
    pen = [(x, y) for x in range(cx + 11, cx + 20) for y in range(cy + 6, cy + 12)]
    m.tribe = None
    foes(game, site, m, [(x, y) for x, y in oval(cx, cy, 12, 8) if cheb(x, y, cx, cy) > 3] +
         [(x, y) for x in range(cx + 9, cx + 21) for y in range(cy - 13, cy - 7)], 6, chief_at=(cx - 14, cy - 9))
    beasts(game, site, m, pen, 2)
    PL.lit(m, [(cx + 10, cy - 10), (cx + 15, cy - 10), (cx, cy)])
    m.altar = (cx - 13, cy - 10)
    return (cx - 27, cy)


# ------------------------------------------------------------------ goblins and kobolds: a nook in the rock
def _cave(m, cx, cy, n, seed_cells=None):
    """Dig a cave from (cx, cy) by drunken walks. Returns its floor cells."""
    cells = set()
    for _ in range(5):
        x, y = cx, cy
        for _ in range(n):
            if m.inb(x, y) and 2 <= x < m.w - 2 and 2 <= y < m.h - 2:
                cells.add((x, y))
            dx, dy = random.choice(((1, 0), (-1, 0), (0, 1), (0, -1)))
            x = max(cx - 14, min(cx + 14, x + dx))
            y = max(cy - 9, min(cy + 9, y + dy))
    for x, y in cells:
        m.set(x, y, FLOOR)
    return cells


def nook(game, site, m, cx, cy, friendly, things, back):
    rock(m, cx - 20, cy - 18, cx + 29, cy + 18)
    cells = _cave(m, cx + 4, cy, 160)
    mouth = (cx - 20, cy)
    for x in range(cx - 20, cx + 5):                                   # the passage in from the slope
        m.set(x, cy, FLOOR)
        if random.random() < .4:
            m.set(x, cy + random.choice((-1, 1)), FLOOR)
    far = max(cells, key=lambda c: c[0] + random.random())
    m.set(*far, back)
    around = [c for c in cells if cheb(c[0], c[1], *far) in (1, 2)]
    random.shuffle(around)
    for t, c in zip(things, around):
        m.set(c[0], c[1], t)
    left = [c for c in cells if m.tile(*c) == FLOOR and cheb(c[0], c[1], *far) > 5 and c[0] > cx + 2]
    down = min(left, key=lambda c: c[1]) if left else (cx + 4, cy - 2)
    m.set(*down, DOWN)
    m.altar = far
    return cells, mouth, far


def goblin(game, site, m, cx, cy, friendly):
    cells, mouth, far = nook(game, site, m, cx, cy, friendly, [D.GLITTER, D.BARREL, D.MIDDEN, D.GLITTER, D.BARREL], D.IDOL)
    foes(game, site, m, list(cells), 5, chief_at=(far[0] - 1, far[1]))
    PL.lit(m, [(far[0] - 1, far[1] + 1)])
    return (mouth[0], mouth[1])


def kobold(game, site, m, cx, cy, friendly):
    cells, mouth, far = nook(game, site, m, cx, cy, friendly, [D.GLITTER, D.GLITTER, D.MIRROR, D.ALTAR, D.GLITTER], D.GLITTER)
    m.set(*far, D.ALTAR)
    foes(game, site, m, list(cells), 5, chief_at=(far[0] - 1, far[1]))
    m.glows = [(far[0] - 1, far[1], (255, 210, 120), 4)]
    m.lights = list(m.glows)
    return (mouth[0], mouth[1])


# ------------------------------------------------------------------ gnolls: the bone ring in the thorns
def gnoll(game, site, m, cx, cy, friendly):
    from .tribes import round_hut
    PL.clear(m, cx - 28, cy - 18, cx + 28, cy + 18)
    hedge = oval(cx, cy, 25, 15)
    for x, y in ring_of(hedge):
        m.set(x, y, D.THORNS)
    for y in (cy - 1, cy, cy + 1):
        m.set(cx - 25, y, PATH)
    altar = (cx, cy)
    m.set(*altar, D.ALTAR)
    for k in range(10):                                              # the ring of bone poles
        a = k / 10 * math.tau
        m.set(round(cx + math.cos(a) * 6), round(cy + math.sin(a) * 4), D.TOTEM)
    m.set(cx, cy - 8, D.STONE)                                       # the moon stone
    for hx, hy in ((cx - 14, cy - 8), (cx - 14, cy + 8), (cx + 14, cy + 8)):
        round_hut(m, hx, hy, 3, 2, D.HIDE, FLOOR)
        m.set(hx, hy - 2 if hy < cy else hy + 2, DOOR)
        m.set(hx + 1, hy, D.FURS)
    caller = (cx - 14, cy - 8)
    m.set(cx - 15, cy - 8, DOWN)                                      # the burrows, under the bone-caller's tent
    for x in range(cx + 10, cx + 13):                                 # the feeding pit
        for y in (cy - 9, cy - 8):
            m.set(x, y, D.BLOODPIT)
    m.set(cx + 13, cy - 9, D.BONES)
    m.set(cx + 9, cy - 8, D.BONES)
    for x in range(cx + 16, cx + 23):                                 # the hyena pen
        for y in (cy - 4, cy + 2):
            m.set(x, y, D.FENCE)
    for y in range(cy - 4, cy + 3):
        for x in (cx + 16, cx + 22):
            m.set(x, y, D.FENCE)
    pen = [(x, y) for x in range(cx + 17, cx + 22) for y in range(cy - 3, cy + 2)]
    foes(game, site, m, [(x, y) for x, y in oval(cx, cy, 14, 9) if cheb(x, y, cx, cy) > 4], 5,
         chief_at=(caller[0] + 1, caller[1] + 1))
    beasts(game, site, m, pen, 3)
    PL.lit(m, [(cx, cy + 1)])
    m.altar = altar
    return (cx - 25, cy)


# ------------------------------------------------------------------ lizardfolk: the stepped mound in the swamp
def lizard(game, site, m, cx, cy, friendly):
    for y in range(max(0, cy - 22), min(H, cy + 23)):
        for x in range(max(0, cx - 34), min(W, cx + 34)):
            r = ((x - cx) / 30) ** 2 + ((y - cy) / 20) ** 2
            if r < 1:
                m.set(x, y, D.SHALLOW if random.random() < .55 else D.SWAMP)
    for k, h in enumerate((10, 8, 6, 4, 2)):
        for y in range(cy - h, cy + h + 1):
            for x in range(cx - h, cx + h + 1):
                edge = max(abs(x - cx), abs(y - cy)) == h
                m.set(x, y, WALL if edge else FLOOR)
        for x, y in ((cx, cy - h), (cx, cy + h), (cx - h, cy), (cx + h, cy)):
            m.set(x, y, PATH)                                         # stairs on all four sides
    m.wall_fg = (150, 160, 120)
    altar = (cx, cy)
    m.set(*altar, D.ALTAR)
    m.set(cx - 1, cy, D.EGGS)
    m.set(cx + 1, cy, D.EGGS)
    m.set(cx, cy + 1, DOWN)
    PL.trail(m, (cx - 34, cy), (cx - 11, cy), PATH)
    for x in range(cx - 34, cx - 10):
        if m.tile(x, cy) in (D.SHALLOW, D.SWAMP, D.WATER):
            m.set(x, cy, D.CAUSEWAY)
    foes(game, site, m, [(x, y) for y in range(cy - 9, cy + 10) for x in range(cx - 9, cx + 10)
                         if m.tile(x, y) == FLOOR and cheb(x, y, cx, cy) > 1], 5, chief_at=(cx, cy - 1))
    beasts(game, site, m, [(x, y) for y in range(cy - 18, cy + 19) for x in range(cx - 30, cx + 30)
                           if m.tile(x, y) == D.SHALLOW and cheb(x, y, cx, cy) > 12], 2)
    PL.lit(m, [(cx, cy - 1)])
    m.altar = altar
    return (cx - 34, cy)


BUILD = {'human': human, 'elf': elf, 'dwarf': dwarf, 'halfling': halfling, 'gnome': gnome, 'orc': orc,
         'goblin': goblin, 'kobold': kobold, 'gnoll': gnoll, 'lizard': lizard}


# ------------------------------------------------------------------ the deep place below
def on_level(game, m, dg, depth):
    """The mood of each level below a temple: the first neat, the rest older and rougher."""
    site = game.world.sites[dg.site]
    pe = PL.people_of(site)
    if depth > dg.depth:
        game.msg(getattr(m, 'mood_line', 'Older than anything above.'), 'unique')
        return
    game.msg(MOOD[pe][0 if depth == 1 else 1], 'info')
