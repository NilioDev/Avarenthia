"""The hostile peoples at home. Orcs and goblins in a war camp behind a palisade, goblins on their own in a ravine,
kobolds in their cave mine, gnolls in a hunting camp that moves with the game, lizardfolk in a village on stilts.

They are not dungeons full of monsters but places where people live: the young, the old and the workers run when
there is trouble, the guards warn a stranger off before they fight, and the whole place only rises against you once
you have gone too far. Orcs, goblins and friends of the horde may come in and trade; the wanted can still sell in the
goblins' market; a shiny toll buys a welcome from the kobolds."""
import math
import random

from . import data as D
from .data import (GRASS, FLOOR, DOOR, ODOOR, PATH, TREE, WATER, SHALLOW, SWAMP, ROCK, PLANK, BRIDGE, CHEST, TABLE,
                   BARREL, ANVIL, STALL, FENCE, SAND, PALISADE, STAKES, HIDE, FIREPIT, TOTEM, CAGE, FURS, RACK, MIDDEN,
                   CLIFF, SHROOM, GLITTER, RAIL, CART, EGGS, FISHTRAP, STILT, THORNS, ORE)
from .entities import GameMap, make_npc, make_monster, Item
from .worldgen import cheb

LOOK = {'warcamp': ('Ψ', (214, 96, 60)), 'ravine': ('¤', (190, 200, 90)), 'kobolds': ('∆', (226, 150, 84)),
        'gnolls': ('¥', (214, 176, 96)), 'stilts': ('╥', (110, 190, 120))}
KIND_NAME = {'warcamp': 'an orc war camp', 'ravine': 'a goblin ravine', 'kobolds': 'the kobold caves',
             'gnolls': 'a gnoll hunting camp', 'stilts': 'a lizardfolk village'}
NAMES = {
    'warcamp': ['Skullgate', 'The Red Stockade', 'Gorefang Camp', 'Ironjaw Camp', 'The Bone Palisade', 'Blacktusk Camp'],
    'ravine': ['Snaggle Gully', 'Ratgut Ravine', 'The Knifecrack', 'Grubber\'s Gulch', 'The Stinkcleft', 'Nettle Gorge'],
    'kobolds': ['The Glitter Caves', 'Shinydig', 'The Tinkle Mines', 'Copperhole', 'The Bright Burrows', 'Pebblegleam'],
    'gnolls': ['The Laughing Camp', 'Bonepole Camp', 'The Hyena Ring', 'Red Grass Camp', 'The Carrion Fires'],
    'stilts': ['Sslathaar', 'Ix-Hessa', 'Thesk Mire', 'Shass Ko', 'The Reed Hives', 'Ossk Vael'],
}
# who lives there: the fighters (and what they become when roused), and their colours
ORC, ORC_YOUNG, ORC_OLD = ('o', (110, 180, 70)), ('o', (170, 210, 130)), ('o', (140, 150, 120))
GOB, GOB_YOUNG = ('g', (190, 200, 90)), ('g', (220, 230, 150))
KOB, KOB_YOUNG = ('k', (210, 140, 80)), ('k', (240, 190, 140))
GNOLL, GNOLL_YOUNG = ('n', (200, 160, 90)), ('n', (230, 200, 140))
LIZ, LIZ_YOUNG = ('l', (100, 170, 100)), ('l', (160, 220, 140))
CAPTIVE = ('☺', (230, 200, 170))
WARN = {
    'warcamp': ['Turn back. This is the camp of the {tribe}. One more step and we cut you down.',
                'No further. Strangers who come through this gate do not go out again.'],
    'ravine': ['This is our gully. Go back up the way you came, or we drop rocks on you.',
               'No closer! Nobody comes down here who is not one of us.'],
    'kobolds': ['Shiny toll! Shiny toll, or go away! No toll, no caves!', 'Stop! Stop! Pay the shiny or go back up!'],
    'gnolls': ['Go. This is the hunting ground of the pack.', 'Walk away, meat. The pack is watching.'],
    'stilts': ['Ssstop. This water is ours. Go back the way you came.', 'No warm-blood comes to the egg pools. Go.'],
}
FRIEND = {
    'warcamp': ['Trade at the smithy, if you have coin. Keep your hands off the cages.', 'The chief says you are no enemy. So, no enemy.'],
    'ravine': ['Market\'s down by the water. Nobody asks where anything came from.', 'You are wanted up there? Welcome down here.'],
    'kobolds': ['Toll is paid! Friend of the caves! Mind the carts.', 'Shiny friend! Come, come, see the hoard. Only look!'],
}
TOLL = 300                  # copper: three silver in bright coins buys the kobolds' welcome
RANSOM = 2000               # copper: twenty silver buys a captive's freedom from the orcs
ORE_PRICE = 600             # copper: kobolds sell iron ore cheap
GUIDE = 200
ANGRY_DAYS = 12


# ------------------------------------------------------------------ the world
def biome_at(m, x, y):
    names = getattr(m, 'biome_names', None)
    return names[m.biome[y * m.w + x]] if names else None


def place_camps(game, m, world, reach_set):
    """Each people where its land is: the war camp in the badlands or steppe, the goblins in a real ravine, the
    kobolds where the hills meet the mountains, the gnolls on the savanna, the lizardfolk in the swamps."""
    from .sites import Site
    w = m.w
    start = world.settlements[0]
    taken = [(s.x, s.y) for s in world.settlements] + [(q.x, q.y) for q in world.sites] + \
            [(d.x, d.y) for d in world.dungeons.values()] + [(h.x, h.y) for h in world.holds]

    def near(x, y, b, r=1):
        return sum(1 for dy in range(-r, r + 1) for dx in range(-r, r + 1) if m.inb(x + dx, y + dy) and biome_at(m, x + dx, y + dy) in b)

    def fits(kind, x, y):
        b = biome_at(m, x, y)
        if kind == 'warcamp':
            return b in ('badlands', 'steppe') and near(x, y, ('badlands', 'steppe')) >= 7
        if kind == 'ravine':
            return b == 'ravine' and near(x, y, ('ravine',)) >= 3
        if kind == 'kobolds':
            return b == 'hills' and any(m.inb(x + dx, y + dy) and m.tile(x + dx, y + dy) == D.MOUNTAIN
                                        for dx in (-1, 0, 1) for dy in (-1, 0, 1))
        if kind == 'gnolls':
            return b == 'savanna' and near(x, y, ('savanna',)) >= 7
        if kind == 'stilts':
            return b in ('swamp', 'marsh') and near(x, y, ('swamp', 'marsh')) >= 7
        return False
    cells = [i for i in reach_set if 3 <= i % w < w - 3 and 3 <= i // w < m.h - 3 and i not in world.wonder_cells]
    random.shuffle(cells)
    for kind, n in (('warcamp', 2), ('ravine', 2), ('kobolds', 2), ('gnolls', 2), ('stilts', 2)):
        names = NAMES[kind][:]
        random.shuffle(names)
        made = 0
        for i in cells:
            if made >= n or not names:
                break
            x, y = i % w, i // w
            if not D.TILES[m.tile(x, y)].walk or m.tile(x, y) in (D.ROAD, D.RIVER) or world.road_dist[i] < 2:
                continue
            if cheb(x, y, start.x, start.y) < 20 or any(cheb(x, y, a, b) < (5 if kind == 'ravine' else 8) for a, b in taken):
                continue
            if not fits(kind, x, y):
                continue
            st = Site(len(world.sites), kind, x, y, names.pop())
            st.faction = 'horde' if kind in ('warcamp', 'ravine') and 'horde' in D.FACTIONS else None
            if kind == 'ravine':
                st.course = ravine_course(m, x, y)
            if kind == 'gnolls':
                st.move_day = random.randint(8, 16)
            world.sites.append(st)
            taken.append((x, y))
            made += 1


def ravine_course(m, x, y):
    """Which way the ravine runs on the world map here: 'we' or 'ns'."""
    we = sum(1 for dx in (-2, -1, 1, 2) if m.inb(x + dx, y) and biome_at(m, x + dx, y) == 'ravine')
    ns = sum(1 for dy in (-2, -1, 1, 2) if m.inb(x, y + dy) and biome_at(m, x, y + dy) == 'ravine')
    diag = sum(1 for d in (-2, -1, 1, 2) if m.inb(x + d, y + d) and biome_at(m, x + d, y + d) == 'ravine')
    adiag = sum(1 for d in (-2, -1, 1, 2) if m.inb(x + d, y - d) and biome_at(m, x + d, y - d) == 'ravine')
    if we >= ns and we >= max(diag, adiag) - 1:
        return 'we'
    return 'ns' if ns >= max(diag, adiag) - 1 else 'we'


def is_camp(site):
    return site is not None and site.kind in LOOK


def level(game, site):
    return max(3, game.world.danger_at(site.x, site.y) + 2)


def welcome(game, site):
    """Will they let you in? Orcs and goblins and friends of the horde in the war camp; in the ravine also the wanted;
    the kobolds once you have paid their toll. Gnolls and lizardfolk never."""
    from . import crime as CR
    p = game.player
    if getattr(site, 'angry', -1) > game.day:
        return False
    if site.kind in ('warcamp', 'ravine'):
        if p.race in ('orc', 'goblin') or p.rep.get('horde', -30) >= 0:
            return True
        return site.kind == 'ravine' and CR.max_heat(game) > 0
    if site.kind == 'kobolds':
        return bool(getattr(site, 'toll', False))
    return False


# ------------------------------------------------------------------ building the maps
def _new(site, w, h, fill):
    m = GameMap(site.map_key, 'town', site.name, w, h, fill)
    m.radius, m.sid, m.hid, m.signs = 60, None, None, []
    m.site, m.tribe = site.id, site.kind
    m.inner, m.warned, m.roused = set(), False, False
    m.lights, m.glows = [], []
    m.deco = bytearray(w * h)
    m.cages = []
    return m


def box(m, x0, y0, w, h, wall=HIDE, floor=FLOOR):
    """A hut: walls round a floor. Returns the floor cells."""
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            m.set(x, y, wall if x in (x0, x0 + w - 1) or y in (y0, y0 + h - 1) else floor)
    return [(x, y) for y in range(y0 + 1, y0 + h - 1) for x in range(x0 + 1, x0 + w - 1)]


def oval(cx, cy, rx, ry):
    return {(x, y) for y in range(int(cy - ry) - 1, int(cy + ry) + 2) for x in range(int(cx - rx) - 1, int(cx + rx) + 2)
            if ((x - cx) / max(.5, rx)) ** 2 + ((y - cy) / max(.5, ry)) ** 2 <= 1}


def round_hut(m, cx, cy, rx, ry, wall=HIDE, floor=FLOOR):
    cells = oval(cx, cy, rx + .5, ry + .5)
    for x, y in cells:
        edge = any((x + dx, y + dy) not in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        m.set(x, y, wall if edge else floor)
    return sorted(c for c in cells if m.tile(*c) == floor)


def line(a, b):
    (x0, y0), (x1, y1) = a, b
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    return [(round(x0 + (x1 - x0) * k / n), round(y0 + (y1 - y0) * k / n)) for k in range(n + 1)]


def trail(m, pts, t=PATH, over=(GRASS, SAND, TREE, SWAMP, MIDDEN, D.HILLS), width=1):
    for a, b in zip(pts, pts[1:]):
        for x, y in line(a, b):
            for dx in range(width):
                if m.inb(x + dx, y) and m.tile(x + dx, y) in over:
                    m.set(x + dx, y, t)


def fire(m, x, y, col=(255, 140, 50), r=5):
    m.set(x, y, FIREPIT)
    m.lights.append((x, y, col, r))
    m.glows.append((x, y, col, r))


def who(game, m, x, y, look, name, foe=None, flee=False, job='folk', race=None, stay=False):
    """Someone who lives here. foe: what they fight as once the place is roused; flee: they run instead."""
    if not m.inb(x, y) or not D.TILES[m.tile(x, y)].walk or m.mon_at(x, y):
        spots = [(x + dx, y + dy) for r in range(1, 4) for dx in range(-r, r + 1) for dy in range(-r, r + 1)
                 if m.inb(x + dx, y + dy) and D.TILES[m.tile(x + dx, y + dy)].walk and not m.mon_at(x + dx, y + dy)]
        if not spots:
            return None
        x, y = spots[0]
    n = make_npc(game, name, 'tribe', look[1], x, y, stay, ch='☺', race=race)
    n.ch = look[0]
    n.foe, n.flee, n.tjob = foe, flee, job
    m.mons.append(n)
    return n


def gen_camp(game, site):
    fn = {'warcamp': war_camp, 'ravine': ravine, 'kobolds': kobold_caves, 'gnolls': gnoll_camp, 'stilts': stilt_village}
    m = fn[site.kind](game, site)
    m.centre = getattr(m, 'centre', (m.w // 2, m.h // 2))
    if getattr(site, 'angry', -1) > game.day:
        m.warned = True
        rouse(game, m, None)
    return m


def tribe_name(site):
    return {'warcamp': 'horde', 'ravine': 'gully', 'kobolds': 'caves', 'gnolls': 'pack', 'stilts': 'swamp'}[site.kind]


def war_camp(game, site):
    """A palisade of sharp stakes round the chief's long hall, the longhouses of the orc families, the fighting pit,
    the smithy the goblins work, the shaman's totem, wolf pens and a boar sty, a cage of captives, and the goblins'
    lean-tos down by the midden."""
    W, H = 104, 60
    m = _new(site, W, H, GRASS)
    for i in range(len(m.t)):
        r = random.random()
        m.t[i] = SAND if r < .5 else GRASS
    cx, cy, rx, ry = 54, 27, 49, 24
    inner = {(x, y) for x in range(W) for y in range(H) if abs((x - cx) / rx) ** 4 + abs((y - cy) / ry) ** 4 <= 1}
    ring = {(x, y) for x, y in inner if any((x + dx, y + dy) not in inner for dx in (-1, 0, 1) for dy in (-1, 0, 1))}
    gate = {(x, y) for x, y in ring if abs(x - cx) <= 1 and y > cy}
    for x, y in ring - gate:
        m.set(x, y, PALISADE)
    outside = {(x + dx, y + dy) for x, y in ring for dx in (-1, 0, 1) for dy in (-1, 0, 1)} - inner
    for x, y in outside:
        if m.inb(x, y) and abs(x - cx) > 3 and random.random() < .5:
            m.set(x, y, STAKES)
    m.inner = inner - ring
    gy = max(y for x, y in gate)
    # the road in from the west, round to the gate
    ey = H - 3
    trail(m, [(0, ey), (cx, ey), (cx, gy)], width=2)
    trail(m, [(cx, gy), (cx, 16)], width=2)
    m.entry = (0, ey)
    m.gate = (cx, gy)
    lvl = level(game, site)
    names = _names('orc')
    # the chief's long hall
    box(m, 36, 6, 36, 10)
    m.set(54, 15, DOOR)
    m.set(53, 7, D.STATUE)
    for x in (42, 66):
        fire(m, x, 10)
    for x in (40, 44, 60, 64):
        m.set(x, 13, TABLE)
    m.set(70, 7, CHEST)
    m.set(70, 14, BARREL)
    m.signs.append((47, 5, "THE CHIEF'S HALL"))
    chief = who(game, m, 54, 8, ('o', (240, 120, 70)), f'{names.pop()}, chief of the camp', 'orc_chief', job='chief', race='orc', stay=True)
    for x in (51, 57):
        who(game, m, x, 12, ORC, 'An orc of the chief\'s guard', 'orc_berserker', job='guard', race='orc', stay=True)
    # longhouses of the orc families
    for x0, y0, door in ((14, 17, (21, 23)), (14, 30, (21, 30)), (82, 17, (89, 23))):
        cells = box(m, x0, y0, 15, 7)
        m.set(*door, DOOR)
        for c in (cells[0], cells[2], cells[-1], cells[-3]):
            m.set(c[0], c[1], FURS)
        fire(m, x0 + 7, y0 + 3, r=4)
        who(game, m, x0 + 3, y0 + 3, ORC, 'An orc warrior', random.choice(['orc', 'orc_spear']), race='orc')
        who(game, m, x0 + 11, y0 + 3, ORC_YOUNG, 'A young orc', flee=True, job='young', race='orc')
        if random.random() < .6:
            who(game, m, x0 + 5, y0 + 2, ORC_OLD, 'An old orc', flee=True, job='old', race='orc')
    m.signs.append((14, 15, 'LONGHOUSES'))
    # the fighting pit
    for x, y in oval(54, 26, 6, 3):
        m.set(x, y, SAND)
    ring = oval(54, 26, 7.5, 4.5)
    for x, y in ring:
        edge = any((x + dx, y + dy) not in ring for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)))
        if edge and m.tile(x, y) in (GRASS, SAND) and not (x == 54 and y > 26):
            m.set(x, y, FENCE)
    for x in (51, 57):
        who(game, m, x, 26, ORC, 'An orc at the fighting pit', random.choice(['orc', 'orc_berserker']), race='orc')
    m.signs.append((48, 21, 'THE PIT'))
    # the smithy, worked by goblins
    box(m, 66, 30, 12, 6)
    m.set(72, 30, DOOR)
    fire(m, 68, 31, (255, 120, 40), 4)
    m.set(71, 32, ANVIL)
    m.set(76, 31, BARREL)
    who(game, m, 73, 33, GOB, 'A goblin smith', flee=True, job='trader', race='goblin', stay=True)
    m.signs.append((66, 36, 'SMITHY'))
    # the shaman's totem
    m.set(34, 26, TOTEM)
    for k in range(8):
        a = k / 8 * math.tau
        x, y = round(34 + 3 * math.cos(a)), round(26 + 1.5 * math.sin(a))
        m.deco[y * W + x] = 4          # bones
    who(game, m, 36, 27, ('o', (150, 200, 140)), 'The camp shaman', 'orc_shaman', job='shaman', race='orc')
    # wolf pens and a boar sty
    for x in range(84, 98):
        m.set(x, 38, FENCE)
        m.set(x, 44, FENCE)
    for y in range(38, 45):
        m.set(84, y, FENCE)
        m.set(97, y, FENCE)
    for x, y in ((87, 40), (90, 42), (93, 40)):
        who(game, m, x, y, ('C', (170, 170, 170)), 'A war wolf', 'wolf', job='beast')
    m.signs.append((84, 46, 'WOLF PENS'))
    for x in range(86, 95):
        m.set(x, 28, FENCE)
        m.set(x, 32, FENCE)
    for y in range(29, 32):
        m.set(86, y, FENCE)
        m.set(94, y, FENCE)
    for x in (89, 91):
        who(game, m, x, 30, ('q', (150, 110, 80)), 'A war boar', 'boar', job='beast')
    # the cook fire and the hide racks
    fire(m, 46, 38)
    for x in range(58, 66, 2):
        m.set(x, 42, RACK)
    who(game, m, 44, 39, GOB, 'A goblin cook', flee=True, job='worker', race='goblin')
    # the goblins' lean-tos by the midden, against the palisade
    for x0 in (20, 27, 34):
        cells = box(m, x0, 44, 6, 4)
        m.set(x0 + 3, 44, DOOR)
        m.set(cells[0][0], cells[0][1], FURS)
        who(game, m, x0 + 3, 42, GOB, 'A goblin', random.choice(['goblin', 'gobarcher']), race='goblin')
    who(game, m, 24, 41, GOB_YOUNG, 'A goblin brat', flee=True, job='young', race='goblin')
    for x, y in oval(13, 41, 3, 2):
        m.set(x, y, MIDDEN)
    m.signs.append((18, 49, 'LEAN-TOS'))
    # the cage of captives
    for x in range(68, 75):
        m.set(x, 46, CAGE)
        m.set(x, 49, CAGE)
    for y in (47, 48):
        m.set(68, y, CAGE)
        m.set(74, y, CAGE)
    m.cages = [(68, 46, 74, 49)]
    for x, y in ((70, 47), (72, 48)):
        captive(game, m, x, y)
    m.signs.append((67, 50, 'CAPTIVES'))
    # the gate guards
    for gx in (cx - 3, cx + 3):
        who(game, m, gx, gy - 1, ORC, 'An orc on the gate', 'orc_spear', job='gate', race='orc', stay=True)
    loose = [c for c in m.inner if m.tile(*c) in (GRASS, SAND, PATH)]
    for _ in range(3):
        x, y = random.choice(loose)
        who(game, m, x, y, ORC, 'An orc warrior', random.choice(['orc', 'orc_spear', 'orc_berserker']), race='orc')
    for _ in range(2):
        x, y = random.choice(loose)
        who(game, m, x, y, GOB, 'A goblin', random.choice(['goblin', 'gob_sneak']), race='goblin')
    stray = [c for c in solid(m) if c not in m.inner]
    assert not stray, stray[:5]
    m.centre = (cx, cy)
    m.chief = chief.id if chief else None
    return m


def _names(race):
    from .towns import town_names
    return town_names(race)


def solid(m):
    """Everything built in a camp (walls, beds, fires, pens, cages): it must all lie inside the palisade."""
    built = {HIDE, FURS, FIREPIT, TABLE, CHEST, BARREL, ANVIL, TOTEM, CAGE, RACK, D.STATUE, DOOR, FENCE}
    return [(i % m.w, i // m.w) for i, t in enumerate(m.t) if t in built]


def captive(game, m, x, y, name=None):
    from .races import random_name
    n = make_npc(game, name or random_name('human'), 'tribe', CAPTIVE[1], x, y, True, race='human')
    n.foe, n.flee, n.tjob = None, False, 'captive'
    m.mons.append(n)
    return n


def ravine(game, site):
    """Goblins on their own: burrows dug into both cliffs, rope bridges between them, scrap huts on the floor by the
    stream, rat pens, a mushroom patch, and the market of stolen goods. The ravine runs the way it does on the map."""
    W, H = 100, 56
    m = _new(site, W, H, ROCK)
    ns = getattr(site, 'course', 'we') == 'ns'
    # lay the ravine out running west to east, then turn it if it runs north to south on the map
    L, Wd = (H, W) if ns else (W, H)          # along, across
    mid = Wd // 2
    lo = [mid - 15 + int(3 * math.sin(a / 7) + 2 * math.sin(a / 3)) for a in range(L)]
    hi = [mid + 15 + int(3 * math.sin(a / 6 + 1) + 2 * math.sin(a / 2.7)) for a in range(L)]

    def put(a, c, t):                          # a: along the ravine, c: across it
        x, y = (c, a) if ns else (a, c)
        if m.inb(x, y):
            m.set(x, y, t)

    def at(a, c):
        return (c, a) if ns else (a, c)
    for a in range(L):
        for c in range(Wd):
            if c < lo[a] - 9 or c > hi[a] + 9:
                put(a, c, D.HILLS if random.random() < .7 else ROCK)
            elif c < lo[a] or c > hi[a]:
                put(a, c, CLIFF)
            else:
                put(a, c, GRASS if random.random() < .5 else SAND)
                m.inner.add(at(a, c))
    for a in range(L):                         # the stream at the bottom
        c = (lo[a] + hi[a]) // 2 + int(3 * math.sin(a / 5))
        for dc in (0, 1):
            put(a, c + dc, SHALLOW)
    # the way in: down the end of the ravine
    for a in range(0, 3):
        for c in range(lo[a], hi[a] + 1):
            put(a, c, PATH if abs(c - mid) <= 1 else GRASS)
    m.entry = (0, mid)
    if ns:                                     # from the west, over the rim and down a stair cut in the cliff
        for x in range(0, lo[4] + 1):
            m.set(x, 4, PATH)
        m.entry = (0, 4)
    lvl = level(game, site)
    names = _names('goblin')
    # burrows in the cliff walls
    for a in range(6, L - 6, 9):
        for side in (-1, 1):
            if side < 0:
                c0 = lo[a] - 7
                cells = []
                for aa in range(a - 1, a + 3):
                    for cc in range(c0, c0 + 7):
                        edge = aa in (a - 1, a + 2) or cc in (c0, c0 + 6)
                        put(aa, cc, ROCK if edge else FLOOR)
                put(a, c0 + 6, DOOR)
                put(a + 1, c0 + 6, CLIFF)
                put(a, c0 + 1, FURS)
                put(a + 1, c0 + 3, CHEST if random.random() < .25 else BARREL)
                for aa in range(a, a + 2):
                    for cc in range(c0, c0 + 7):
                        m.inner.add(at(aa, cc))
                if random.random() < .7:
                    x, y = at(a + 1, c0 + 2)
                    who(game, m, x, y, GOB, 'A goblin', random.choice(['goblin', 'gobarcher', 'gob_sneak']), race='goblin')
            else:
                c0 = hi[a] + 1
                for aa in range(a - 1, a + 3):
                    for cc in range(c0, c0 + 7):
                        edge = aa in (a - 1, a + 2) or cc in (c0, c0 + 6)
                        put(aa, cc, ROCK if edge else FLOOR)
                put(a, c0, DOOR)
                put(a, c0 + 5, FURS)
                put(a + 1, c0 + 3, BARREL)
                for aa in range(a, a + 2):
                    for cc in range(c0, c0 + 7):
                        m.inner.add(at(aa, cc))
                if random.random() < .6:
                    x, y = at(a + 1, c0 + 4)
                    who(game, m, x, y, GOB_YOUNG, 'A goblin brat', flee=True, job='young', race='goblin')
    # rope bridges high across, from burrow to burrow
    for a in (L // 4, 3 * L // 4):
        for c in range(lo[a], hi[a] + 1):
            put(a, c, BRIDGE)
    # scrap huts on the floor, by the stream
    for a0, c0 in ((L // 3 - 6, lo[L // 3] + 3), (L // 3 - 6, hi[L // 3] - 9), (2 * L // 3 + 2, lo[2 * L // 3] + 3),
                   (2 * L // 3 + 2, hi[2 * L // 3] - 9)):
        for aa in range(a0, a0 + 5):
            for cc in range(c0, c0 + 7):
                edge = aa in (a0, a0 + 4) or cc in (c0, c0 + 6)
                put(aa, cc, HIDE if edge else FLOOR)
        put(a0 + 4 if a0 < L // 2 else a0, c0 + 3, DOOR)
        put(a0 + 1, c0 + 1, FURS)
        x, y = at(a0 + 2, c0 + 4)
        fire(m, x, y, r=3)
        x, y = at(a0 + 2, c0 + 2)
        who(game, m, x, y, GOB, 'A goblin', random.choice(['goblin', 'goblin', 'gob_bomber']), race='goblin')
    # the market of stolen goods in the middle
    a_m = L // 2
    cm = (lo[a_m] + hi[a_m]) // 2
    for k, cc in enumerate(range(cm - 8, cm + 9, 4)):
        put(a_m - 1, cc, STALL)
    x, y = at(a_m, cm - 3)
    who(game, m, x, y, ('☺', (220, 200, 160)), f'{_names("human")[0]}, a fence',
        flee=True, job='trader', race='human', stay=True)
    for cc in (cm - 6, cm + 2, cm + 6):
        x, y = at(a_m, cc)
        who(game, m, x, y, GOB, 'A goblin hawker', flee=True, job='worker', race='goblin')
    m.signs.append((at(a_m - 3, cm - 9)[0], at(a_m - 3, cm - 9)[1], 'MARKET'))
    # rat pens and a mushroom patch
    a_r = L // 2 - 12
    for cc in range(cm - 12, cm - 3):
        put(a_r, cc, FENCE)
        put(a_r + 3, cc, FENCE)
    for aa in range(a_r, a_r + 4):
        put(aa, cm - 12, FENCE)
        put(aa, cm - 4, FENCE)
    for cc in (cm - 9, cm - 6):
        x, y = at(a_r + 1, cc)
        who(game, m, x, y, ('r', (160, 140, 120)), 'A fat rat', 'rat', job='beast')
    for aa in range(a_r, a_r + 4):
        for cc in range(cm + 3, cm + 11):
            if (aa + cc) % 2 and m.tile(*at(aa, cc)) in (GRASS, SAND):
                put(aa, cc, SHROOM)
    # the lookouts on the way in, and the boss
    for cc in (mid - 4, mid + 4):
        x, y = at(5, cc)
        who(game, m, x, y, GOB, 'A goblin lookout', 'gobarcher', job='gate', race='goblin', stay=True)
    x, y = at(a_m + 4, cm)
    boss = who(game, m, x, y, ('g', (240, 200, 80)), f'{names.pop()}, boss of the gully', 'gob_boss', job='chief', race='goblin')
    x, y = at(a_m + 6, cm + 3)
    who(game, m, x, y, ('g', (150, 220, 120)), 'The gully shaman', 'gob_shaman', job='shaman', race='goblin')
    m.gate = at(5, mid)
    m.warn_line = 7                            # how far along the ravine the lookouts let you come
    m.along_ns = ns
    m.chief = boss.id if boss else None
    m.centre = at(a_m, cm)
    return m


def kobold_caves(game, site):
    """A kobold mine: caves joined by passages, the way in laid with snares, the hoard of shiny things at the heart,
    a drift with rails and ore carts, sleeping nooks, a mushroom cave and an ore store."""
    from .behave import traps
    W, H = 100, 56
    m = _new(site, W, H, ROCK)
    m.underground = True
    m.ambient = .35
    m.wall_fg = (122, 100, 80)

    def cave(cx, cy, rx, ry):
        cells = {c for c in oval(cx, cy, rx, ry) if random.random() < .93 or
                 ((c[0] - cx) / rx) ** 2 + ((c[1] - cy) / ry) ** 2 < .6}
        for x, y in cells:
            if 1 <= x < W - 1 and 1 <= y < H - 1:
                m.set(x, y, FLOOR)
                m.inner.add((x, y))
        return cells
    caves = [(50, 28, 12, 6), (18, 12, 9, 5), (84, 12, 10, 5), (18, 44, 10, 5), (84, 45, 10, 5), (50, 8, 7, 3)]
    for c in caves:
        cave(*c)
    for (ax, ay, _, _), (bx, by, _, _) in [(caves[0], caves[i]) for i in range(1, 6)]:
        for x, y in line((ax, ay), (bx, by)):
            for dx in (0, 1):
                m.set(x + dx, y, FLOOR)
                m.inner.add((x + dx, y))
    # the way in: a long passage from the hillside, with snares in it
    ey = 51
    for x, y in line((0, ey), (18, 44)):
        for dy in (0, 1):
            m.set(x, y + dy, FLOOR)
    m.entry = (0, ey)
    tr = traps(m)
    for x, y in ((5, 50), (9, 48), (13, 47)):
        if m.tile(x, y) == FLOOR:
            tr[(x, y)] = 4 + level(game, site)
    m.signs.append((1, 54, 'THE WAY IN'))
    # the hoard in the middle cave: shiny things heaped up, and coin on the floor
    from .money import purse
    lvl = level(game, site)
    for x, y in oval(50, 28, 11, 5) - oval(50, 28, 9, 4):
        if m.tile(x, y) == FLOOR and random.random() < .35:
            m.set(x, y, GLITTER)
    if not getattr(site, 'looted', False):
        for _ in range(6):
            x, y = 50 + random.randint(-6, 6), 28 + random.randint(-3, 3)
            if m.tile(x, y) == FLOOR:
                it = Item(game.new_id(), 'gold', 'gold', purse(lvl, .6))
                it.x, it.y = x, y
                m.items.append(it)
        m.set(50, 25, CHEST)
    names = _names('goblin')
    chief = who(game, m, 50, 28, ('k', (255, 210, 90)), f'{names.pop()}, keeper of the hoard', 'kob_chief', job='chief', stay=True)
    for x, y in ((46, 30), (55, 26), (43, 27)):
        who(game, m, x, y, KOB, 'A kobold', random.choice(['kobold', 'kob_slinger']))
    # the drift: rails, carts and ore in the walls
    for x in range(62, W - 2):
        for y in (28, 29):
            m.set(x, y, FLOOR)
            m.inner.add((x, y))
        m.set(x, 30, RAIL)
        m.inner.add((x, 30))
        for y in (27, 31):
            if random.random() < .25:
                m.set(x, y, ORE)
    for x in (70, 84):
        m.set(x, 30, CART)
    for x in (76, 92):
        who(game, m, x, 29, KOB, 'A kobold miner', random.choice(['kobold', 'kob_trapper']), job='worker')
    m.signs.append((66, 25, 'THE DRIFT'))
    # sleeping nooks and the young
    for x, y in ((14, 10), (17, 13), (21, 11), (24, 13), (13, 13)):
        if m.tile(x, y) == FLOOR:
            m.set(x, y, FURS)
    for x, y in ((16, 12), (20, 14), (22, 10)):
        who(game, m, x, y, KOB_YOUNG, 'A kobold whelp', flee=True, job='young')
    # the mushroom cave, the ore store, the cooking cave
    for y in range(42, 49):
        for x in range(76, 93):
            if (x + y) % 2 and m.tile(x, y) == FLOOR:
                m.set(x, y, SHROOM)
    for x in range(80, 90, 2):
        if m.tile(x, 10) == FLOOR:
            m.set(x, 10, BARREL)
    who(game, m, 86, 12, ('k', (200, 220, 160)), 'A kobold trader', flee=True, job='trader', stay=True)
    fire(m, 50, 7, r=4)
    who(game, m, 47, 9, KOB, 'A kobold cook', flee=True, job='worker')
    # the guard cave by the way in
    for x, y in ((20, 44), (16, 46)):
        who(game, m, x, y, KOB, 'A kobold guard', 'kob_slinger', job='gate', stay=True)
    who(game, m, 22, 43, ('k', (200, 120, 230)), 'A kobold hexer', 'kob_sorcerer', job='shaman')
    m.gate = (18, 45)
    m.lights += [(50, 28, (255, 210, 120), 6), (18, 44, (255, 160, 80), 4), (84, 12, (255, 160, 80), 4)]
    m.chief = chief.id if chief else None
    m.centre = (50, 28)
    return m


def gnoll_camp(game, site):
    """Tents of hide on bone poles inside a ring of thorns, the packlord's tent with skulls at the door, the great fire,
    meat drying, a bone heap, and the hyenas loose in their own ring. When the game runs out the camp moves on."""
    W, H = 100, 56
    m = _new(site, W, H, GRASS)
    for _ in range(18):
        x, y = random.randrange(W), random.randrange(H)
        m.set(x, y, TREE)
    cx, cy, rx, ry = 52, 27, 40, 21
    ring = oval(cx, cy, rx, ry) - oval(cx, cy, rx - 1.2, ry - 1.2)
    for x, y in ring:
        if m.inb(x, y) and not (abs(x - cx) < 2 and y > cy):
            m.set(x, y, THORNS)
    m.inner = oval(cx, cy, rx - 1.3, ry - 1.3)
    gy = cy + ry
    ey = H - 3
    trail(m, [(0, ey), (cx, ey), (cx, gy), (cx, cy + 3)])
    m.entry = (0, ey)
    m.gate = (cx, gy)
    names = _names('orc')
    # the packlord's tent
    round_hut(m, cx, 11, 8, 4)
    m.set(cx, 15, DOOR)
    m.set(cx + 5, 10, CHEST)
    m.set(cx - 4, 11, FURS)
    m.set(cx + 4, 12, FURS)
    for dx in (-2, 2):
        m.deco[16 * W + cx + dx] = 4
    lord = who(game, m, cx, 10, ('n', (240, 170, 80)), f'{names.pop()}, packlord', 'gnoll_packlord', job='chief', stay=True)
    # family tents round the fire
    for tx, ty in ((26, 19), (78, 19), (24, 35), (80, 35), (40, 40), (64, 40)):
        round_hut(m, tx, ty, 4, 2)
        m.set(tx, ty - 2 if ty > cy else ty + 2, DOOR)
        m.set(tx - 2, ty, FURS)
        who(game, m, tx + 2, ty, GNOLL_YOUNG, 'A gnoll whelp', flee=True, job='young')
        who(game, m, tx + 1, ty + (3 if ty > cy else -3), GNOLL, 'A gnoll hunter', 'gnoll_hunter')
    # the great fire, the meat racks, the bone heap
    fire(m, cx, cy, r=7)
    for k in range(3):
        who(game, m, cx - 4 + k * 4, cy + 2, GNOLL, 'A gnoll by the fire', random.choice(['gnoll_hunter', 'gnoll_caller']))
    for x in list(range(34, 44, 2)) + list(range(62, 72, 2)):
        m.set(x, cy + 1, RACK)
    for x, y in oval(70, 11, 3, 1):
        m.deco[y * W + x] = 4
    # the hyenas, loose in their own ring
    for x, y in oval(24, 27, 5, 2) - oval(24, 27, 4, 1):
        m.set(x, y, FENCE)
    for x in (22, 25, 27):
        who(game, m, x, 27, ('C', (180, 160, 110)), 'A hyena', 'hyena', job='beast')
    for x, y in ((cx - 6, gy - 2), (cx + 6, gy - 2)):
        who(game, m, x, y, GNOLL, 'A gnoll sentry', 'gnoll_hunter', job='gate', stay=True)
    m.chief = lord.id if lord else None
    m.centre = (cx, cy)
    return m


def stilt_village(game, site):
    """Huts on stilts over the swamp, joined by plank walks; fish traps and canoes in the channels; the shaman's hut
    with the totem; and the warm egg pools, which the whole village guards."""
    W, H = 100, 56
    m = _new(site, W, H, SWAMP)
    for y in range(H):
        for x in range(W):
            n = math.sin(x / 7) + math.sin(y / 5) + math.sin((x + y) / 9)
            m.set(x, y, GRASS if n > 1.1 else SWAMP if n > .3 else SHALLOW if n > -.6 else WATER)
    huts = [(20, 12), (44, 9), (70, 12), (88, 26), (24, 34), (50, 30), (76, 42), (40, 48)]
    for hx, hy in huts:
        cells = round_hut(m, hx, hy, 4, 2, HIDE, PLANK)
        m.set(hx, hy + 2, DOOR)
        for dx in (-4, 4):
            if m.inb(hx + dx, hy + 2):
                m.set(hx + dx, hy + 2, STILT)
        m.set(hx - 2, hy, FURS)
        m.set(hx + 2, hy, BARREL)
    walks = [(0, 1), (1, 2), (1, 5), (5, 3), (5, 4), (5, 6), (4, 7), (6, 7)]
    for a, b in walks:
        (ax, ay), (bx, by) = huts[a], huts[b]
        for x, y in line((ax, ay + 3), (bx, by + 3)):
            if m.tile(x, y) in (WATER, SHALLOW, SWAMP, GRASS):
                m.set(x, y, PLANK)
    ey = 37
    for x, y in line((0, ey), (huts[4][0], huts[4][1] + 3)):
        if m.tile(x, y) in (WATER, SHALLOW, SWAMP, GRASS):
            m.set(x, y, PLANK)
    m.entry = (0, ey)
    m.inner = {(x, y) for x in range(14, W) for y in range(H)}
    m.gate = (14, ey)
    # the shaman's hut in the middle, with the totem before it
    m.set(50, 34, TOTEM)
    shaman = who(game, m, 50, 30, ('l', (170, 220, 170)), 'The swamp shaman', 'lizard_shaman', job='chief', stay=True)
    # the egg pools
    m.eggs = []
    for ex, ey2 in ((64, 22), (32, 22)):
        for x, y in oval(ex, ey2, 3, 1):
            m.set(x, y, SHALLOW)
        for dx in (-2, 0, 2):
            m.set(ex + dx, ey2, EGGS)
            m.eggs.append((ex + dx, ey2))
        who(game, m, ex + 4, ey2, LIZ, 'A lizardfolk guarding the eggs', 'lizard_warrior', job='guard', stay=True)
    for x, y in ((10, 24), (14, 26), (90, 46), (94, 44), (60, 52)):
        if m.inb(x, y):
            m.set(x, y, FISHTRAP)
    for x in range(66, 74, 2):
        m.set(x, 16, RACK)
    for hx, hy in huts:
        who(game, m, hx - 1, hy, LIZ, 'A lizardfolk', random.choice(['lizard_warrior', 'lizard_spear']))
    for x, y in ((31, 24), (65, 24), (42, 48)):
        who(game, m, x, y, LIZ_YOUNG, 'A hatchling', flee=True, job='young')
    for x, y in ((12, 33), (60, 50)):
        who(game, m, x, y, ('q', (110, 140, 90)), 'A crocodile', 'crocodile', job='beast')
    who(game, m, 15, ey - 1, LIZ, 'A lizardfolk on the walk', 'lizard_spear', job='gate', stay=True)
    m.chief = shaman.id if shaman else None
    m.centre = (50, 32)
    return m


# ------------------------------------------------------------------ being there
def on_enter(game, site, m):
    """Coming in: tell how it stands with them."""
    if m.roused:
        game.msg(f'{site.name} is up in arms against you.', 'bad')
    elif welcome(game, site):
        game.msg(f'{site.name}: {KIND_NAME[site.kind]}. They know you here; they will let you in.', 'info')
    else:
        game.msg(f'{site.name}: {KIND_NAME[site.kind]}. They will not want you here.', 'bad')
    ensure_captives(game, site, m)


def on_step(game):
    """A step on a camp's map: the guards warn you off once, then the place rises if you go on."""
    m, p = game.map, game.player
    site = game.world.sites[m.site]
    if m.roused or welcome(game, site):
        return
    if site.kind == 'stilts' and any(cheb(p.x, p.y, x, y) <= 2 for x, y in getattr(m, 'eggs', ())):
        game.msg('You come near the egg pools. A hiss goes up from every hut at once: the whole village is coming!', 'bad')
        rouse(game, m, 'eggs')
        return
    inside = (p.x, p.y) in m.inner
    if site.kind == 'ravine':
        along = p.y if m.along_ns else p.x
        inside = along > m.warn_line + 3
        near = along >= m.warn_line - 2
    else:
        near = cheb(p.x, p.y, *m.gate) <= 7
    if inside and m.warned:
        game.msg('You did not listen. They come for you!', 'bad')
        rouse(game, m, 'trespass')
        return
    if (near or inside) and not m.warned:
        m.warned = True
        guard = min((o for o in m.mons if o.is_npc and getattr(o, 'foe', None)),
                    key=lambda o: cheb(o.x, o.y, p.x, p.y), default=None)
        if guard:
            game.say(guard, random.choice(WARN[site.kind]).format(tribe=tribe_name(site)))
        game.msg('They warn you off. Go further and they will fight.', 'bad')


def rouse(game, m, why):
    """The whole place rises: the fighters come for you, everyone else runs."""
    if m.roused:
        return
    m.roused = True
    site = game.world.sites[m.site]
    lvl = level(game, site)
    pid = game.new_id()
    for i, n in enumerate(m.mons):
        if not n.is_npc or getattr(n, 'tjob', None) is None:
            continue
        if n.foe:
            chief = n.tjob == 'chief'
            mon = make_monster(game, n.foe, n.x, n.y, lvl + (2 if chief else 1 if n.tjob in ('guard', 'shaman') else 0))
            if chief:
                mon.name, mon.fg = n.name.split(',')[0], D.UNIQUE_FG
                mon.hp = mon.maxhp = round(mon.maxhp * 1.6)
            mon.awake, mon.pack = True, pid
            mon.faction = 'horde' if site.kind in ('warcamp', 'ravine') and 'horde' in D.FACTIONS else None
            m.mons[i] = mon
        elif n.tjob != 'captive':
            n.flee, n.stay = True, False
    if why is not None:
        site.angry = game.day + ANGRY_DAYS
        if site.kind in ('warcamp', 'ravine') and 'horde' in D.FACTIONS:
            from .war import change_rep
            if game.player.rep.get('horde', -30) >= 0:
                change_rep(game, 'horde', -25)
        from . import news as NW
        NW.post(game, 'danger', f'Someone stirred up {site.name}; {KIND_NAME[site.kind]} is up in arms.', site.x, site.y)
        game.msg({'warcamp': 'Horns blow all over the camp. The orcs are coming!',
                  'ravine': 'Shrieks echo from both cliffs. The goblins are coming!',
                  'kobolds': 'A gong clangs in the dark. Yip! Yip! The kobolds are coming!',
                  'gnolls': 'The hyenas start to laugh. The pack is coming!',
                  'stilts': 'Drums on the water. The lizardfolk are coming!'}[site.kind], 'bad')


def stale(game, site):
    """A camp that rose against you calms down after a while, and rebuilds what you broke."""
    m = game.maps.get(site.map_key)
    return m is not None and getattr(m, 'roused', False) and getattr(site, 'angry', -1) <= game.day


def daily(game):
    """Gnolls follow the game: when it runs out they strike the tents and set up somewhere else on the savanna."""
    w = game.world
    om = game.maps['over']
    for site in getattr(w, 'sites', ()):
        if site.kind != 'gnolls' or game.day < getattr(site, 'move_day', 10 ** 9) or game.cur == site.map_key:
            continue
        site.move_day = game.day + random.randint(10, 16)
        cands = [(site.x + dx, site.y + dy) for dx in range(-24, 25) for dy in range(-16, 17) if 8 <= max(abs(dx), abs(dy))]
        random.shuffle(cands)
        others = [(q.x, q.y) for q in w.sites if q is not site] + [(s.x, s.y) for s in w.settlements]
        for x, y in cands:
            if not om.inb(x, y) or biome_at(om, x, y) != 'savanna' or om.tile(x, y) in (D.ROAD, D.RIVER):
                continue
            if any(cheb(x, y, a, b) < 6 for a, b in others) or (x, y) == (game.player.x, game.player.y):
                continue
            site.x, site.y = x, y
            game.maps.pop(site.map_key, None)
            break


# ------------------------------------------------------------------ talking
def talk(game, npc):
    from . import events as EV
    m = game.map
    site = game.world.sites[m.site]
    job = getattr(npc, 'tjob', 'folk')
    if job == 'captive':
        captive_talk(game, npc, site)
        return
    if m.roused:
        game.msg(f'{npc.name} shrinks away from you.' if npc.flee else f'{npc.name} will not talk now.')
        return
    friend = welcome(game, site)
    if npc.foe and not friend:
        opts = [('Back away', 'bye'), ('Attack', 'attack')]
        if site.kind == 'kobolds' and job == 'gate':
            opts.insert(0, (f'Pay the shiny toll ({fmt(TOLL)} in bright coin)', 'toll'))
        EV.ask(game, 'tribe', npc.name, f'"{random.choice(WARN[site.kind]).format(tribe=tribe_name(site))}"', opts, npc=npc.id)
        m.warned = True
        return
    if job == 'trader' and friend:
        trader(game, npc, site)
        return
    if npc.flee and not friend:
        game.msg(random.choice([f'{npc.name} stares at you and backs off.', f'{npc.name} hisses and keeps away.',
                                f'{npc.name} runs to fetch someone.']))
        return
    if friend:
        game.say(npc, random.choice(FRIEND.get(site.kind, ['...'])))
        return
    game.msg(f'{npc.name} watches you.')


def trader(game, npc, site):
    from . import events as EV
    if site.kind == 'kobolds':
        EV.ask(game, 'tribe', npc.name, '"Friend of the caves! Ore, cheap, cheap. A guide to the deep holes. '
               'Or something shiny for us? We pay well for shiny."',
               [(f'Buy iron ore ({fmt(ORE_PRICE)} a load)', 'ore'), (f'Ask for a guide ({fmt(GUIDE)})', 'guide'),
                ('Sell them something shiny', 'shiny'), ('Goodbye', 'bye')], npc=npc.id)
        return
    key = f'tribe{site.id}'
    if game.day - getattr(site, 'stock_day', -99) >= 5 or key not in game.shops:
        from .worldgen import gen_shop
        site.stock_day = game.day
        game.shops[key] = gen_shop(game)
    text = ('"Blades and mail, fresh off the anvil. Coin first."' if site.kind == 'warcamp'
            else '"Everything you see fell off a cart. Do not ask which cart."')
    opts = [('See the goods', 'shop')]
    if site.kind == 'warcamp' and any(o.is_npc and getattr(o, 'tjob', '') == 'captive' for o in game.map.mons):
        opts.append((f'Buy a captive\'s freedom ({fmt(RANSOM)})', 'ransom'))
    opts.append(('Goodbye', 'bye'))
    EV.ask(game, 'tribe', npc.name, text, opts, npc=npc.id)


def captive_talk(game, npc, site):
    from . import events as EV
    m = game.map
    if m.roused or welcome(game, site) is False:
        text = (f'{npc.name} grips the bars. "Get us out of here! Please! The latch is on the outside!"')
        opts = [('Break the cage open', 'free'), ('Not yet', 'bye')]
    else:
        text = f'{npc.name} grips the bars. "You are with them? Then buy us out. They sell anything for coin."'
        opts = [('Not now', 'bye')]
    EV.ask(game, 'tribe', npc.name, text, opts, npc=npc.id)


def fmt(c):
    from .money import fmt as f
    return f(c)


def r_tribe(game, choice, ctx):
    m = game.map
    if getattr(m, 'tribe', None) is None:
        return
    site = game.world.sites[m.site]
    npc = next((o for o in m.mons if o.id == ctx.get('npc')), None)
    p = game.player
    if choice == 'attack':
        rouse(game, m, 'attack')
    elif choice == 'toll':
        if p.gold < TOLL:
            game.msg('You do not have enough bright coin.', 'bad')
            return
        p.gold -= TOLL
        site.toll = True
        game.msg('The kobold bites every coin, then squeaks with joy. The caves are open to you now.', 'good')
    elif choice == 'shop':
        game.request = ('shop', f'tribe{site.id}')
    elif choice == 'ransom':
        if p.gold < RANSOM:
            game.msg(f'They want {fmt(RANSOM)}.', 'bad')
            return
        c = next((o for o in m.mons if o.is_npc and getattr(o, 'tjob', '') == 'captive'), None)
        if c:
            p.gold -= RANSOM
            set_free(game, site, m, [c], bought=True)
    elif choice == 'free':
        caps = [o for o in m.mons if o.is_npc and getattr(o, 'tjob', '') == 'captive']
        if not m.roused:
            rouse(game, m, 'captives')
        open_cage(m)
        set_free(game, site, m, caps)
    elif choice == 'ore':
        from . import economy as ECO
        if p.gold < ORE_PRICE:
            game.msg(f'A load of ore costs {fmt(ORE_PRICE)}.', 'bad')
            return
        if ECO.cargo_weight(p) + D.GOODS['ore']['w'] > ECO.cargo_capacity(p):
            game.msg('You have no room for a load of ore. A mule or a cart would carry it.', 'bad')
            return
        p.gold -= ORE_PRICE
        p.cargo['ore'] = p.cargo.get('ore', 0) + 1
        p.cost_basis['ore'] = p.cost_basis.get('ore', 0) + ORE_PRICE
        game.msg('The kobolds roll a load of iron ore onto your cart, giggling.', 'gold')
    elif choice == 'guide':
        if p.gold < GUIDE:
            game.msg(f'A guide costs {fmt(GUIDE)}.', 'bad')
            return
        w = game.world
        om = game.maps['over']
        holes = [d for d in w.dungeons.values() if not om.seen[d.y * om.w + d.x] and getattr(d, 'town', None) is None]
        if not holes:
            game.say(npc, 'You know all the holes already! Clever friend.')
            return
        d = min(holes, key=lambda d: cheb(d.x, d.y, site.x, site.y))
        p.gold -= GUIDE
        game.reveal_place(d.x, d.y)
        from .engine import dir_name
        game.say(npc, f'A hole to the {dir_name(d.x - site.x, d.y - site.y)}: {d.name}. Deep! Mind the things in it.')
    elif choice == 'shiny':
        it = next((i for i in game.backpack() if i.k == 'gear' and i.slot in ('ring', 'amulet')), None)
        if not it:
            game.say(npc, 'No shiny on you? Rings! Amulets! Bring us those.')
            return
        price = it.value() * 2
        game.remove_one(it)
        p.gold += price
        game.msg(f'The kobold snatches {it.display_name()} and hugs it. They pay you {fmt(price)}, twice what a town would.', 'gold')


def open_cage(m):
    """Break the cage: the latch side comes open."""
    for x0, y0, x1, y1 in m.cages:
        for x in range(x0 + 1, x1):
            if m.tile(x, y1) == CAGE:
                m.set(x, y1, FLOOR)
                break


def set_free(game, site, m, caps, bought=False):
    """The captives go home: the villages near the camp hear of it, and a job to free them is done."""
    from . import missions as MS, jobs as JB, news as NW
    if not caps:
        return
    for c in caps:
        m.mons.remove(c)
    site.freed = getattr(site, 'freed', 0) + len(caps)
    names = ', '.join(c.name for c in caps)
    game.msg(f'{names} {"walk" if len(caps) > 1 else "walks"} free, and {"make" if len(caps) > 1 else "makes"} for home.'
             if bought else f'You break the latch. {names} slip{"" if len(caps) > 1 else "s"} out and run for the gate.', 'good')
    near = sorted(game.world.settlements, key=lambda s: cheb(s.x, s.y, site.x, site.y))[:1]
    for s in near:
        s.rep = min(100, s.rep + 4 * len(caps))
        game.msg(f'{s.name} will hear of it. (standing {s.rep})', 'good')
        NW.post(game, 'danger', f'Captives came home to {s.name} from {site.name}; someone set them free.', s.x, s.y)
    for mi in MS.active(game):
        if mi.kind == 'rescue' and mi.state == 'active' and mi.data.get('camp') == site.id:
            if any(c.name == mi.data.get('name') for c in caps):
                JB._turnin(game, mi, f'{mi.data["name"]} is free.')
    game.gain_xp(20 * len(caps) + 4 * level(game, site))


def ensure_captives(game, site, m):
    """A job to free someone from the war camp puts them in its cage."""
    from . import missions as MS
    if site.kind != 'warcamp' or m.roused or not m.cages:
        return
    x0, y0, x1, y1 = m.cages[0]
    here = {o.name for o in m.mons if o.is_npc and getattr(o, 'tjob', '') == 'captive'}
    for mi in MS.active(game):
        if mi.kind == 'rescue' and mi.state == 'active' and mi.data.get('camp') == site.id and mi.data['name'] not in here:
            spots = [(x, y) for y in range(y0 + 1, y1) for x in range(x0 + 1, x1) if not m.mon_at(x, y)]
            if spots:
                captive(game, m, *spots[0], name=mi.data['name'])


def near_camp(game, s, kind, r):
    camps = [q for q in getattr(game.world, 'sites', ()) if q.kind == kind and cheb(q.x, q.y, s.x, s.y) <= r]
    return min(camps, key=lambda q: cheb(q.x, q.y, s.x, s.y)) if camps else None


def theft(game):
    """Opening their chests or taking from the hoard while they watch: that is the end of being welcome."""
    m = game.map
    site = game.world.sites[m.site]
    if site.kind == 'kobolds':
        site.looted = True
    if not m.roused:
        game.msg('They saw that!', 'bad')
        rouse(game, m, 'theft')


def cage(game):
    """Bump the bars of the cage: talk to whoever is in it."""
    m = game.map
    c = next((o for o in m.mons if o.is_npc and getattr(o, 'tjob', '') == 'captive'), None)
    if c:
        captive_talk(game, c, game.world.sites[m.site])
    else:
        game.msg('The cage is empty.')


def describe(site):
    return {'warcamp': 'A war camp of orcs and goblins behind a palisade of stakes. Orcs, goblins and friends of the horde may trade.',
            'ravine': 'Goblins live down in this ravine. Their market buys and sells anything, even from the wanted.',
            'kobolds': 'Kobold caves: a mine, and a hoard of shiny things. Pay their toll and they trade.',
            'gnolls': 'A gnoll hunting camp. It moves when the game runs out.',
            'stilts': 'A lizardfolk village on stilts. They guard their egg pools with their lives.'}[site.kind]


def register():
    from . import events as EV
    EV.RESOLVERS['tribe'] = r_tribe


register()
