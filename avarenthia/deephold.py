"""The dwarves. A deephold is a city cut into the roots of the mountains: one gate, a bridge over a chasm guarded by
statues of the first kings, and in the middle the Great Forge with its pool of molten iron, ringed by a street of
shops. The king's High Seat lies to the north, the barracks to the west (dwarves hire out there), the temple to the
east, the homes, the cart station and the stair down to the mines to the south.

The mines go down level by level. The working galleries at the top are lit and the dwarves dig there; below lie the
old galleries, dark and dangerous, and at the bottom the Deep Gate opens on the Deep Roads. Ore veins glint in the
walls: dig them with a pick (bump into them). Cracked props are a warning: dig near one and the roof may come down.

In front of the mountains, in the hills, lie the dwarf villages: stone houses, goat terraces, a mine above the
village, a smelter, a mead hall, a brewery and a watchtower."""
import math
import random

from . import data as D
from .data import (FLOOR, ROCK, DOOR, DOWN, UP, STALL, ANVIL, ALTAR, BED, TABLE, BARREL, PLANK, STATUE, GRASS, PATH,
                   WALL, FENCE, TREE, BRIDGE, CHASM, MOLTEN, ORE, GEMS, PROP, CRACKED, RUBBLE, RAIL, CART, FIREPIT)
from .entities import GameMap, make_npc
from .worldgen import cheb

THANE_LINES = [
    'Welcome to {hold}, surface-dweller. Mind the forges, and mind your manners.',
    'Our fathers dug these halls when your kind still lived in trees. The Deep Roads below were ours too, once.',
    'The Deep Roads run for a hundred leagues under the mountains. Goblins and worse live there now.',
    "Grolm? A disgrace. He dug where we forbade digging, found something in the dark, and it ate his mind. "
    "We cast him out. Now he holds the old mine near Thornfield, they say.",
    'Bring us grain and ale and timber, and we will pay in good iron. The mountain gives stone, not bread.',
    'Dig in our galleries when the clan knows your name, and not before. Till then the veins are ours.',
]
TORCH_COL = (255, 170, 80)
WORKING = 2                 # the top levels of the mines are working galleries
GATE_LEVEL = 4              # the Deep Gate lies at the bottom of the old galleries
MINE_DEPTH = 6


# ------------------------------------------------------------------ the world
def hold_of(game, s):
    """The deephold a dwarf village belongs to."""
    if s.kind == 'deephold':
        return s
    holds = [o for o in game.world.settlements if o.kind == 'deephold']
    return min(holds, key=lambda o: cheb(o.x, o.y, s.x, s.y)) if holds else None


def is_dwarven(s):
    return s.kind == 'deephold' or getattr(s, 'dwarven', False)


# ------------------------------------------------------------------ the city
def gen_deephold(game, s):
    from .towns import town_names, townsfolk
    from .dress import TORCH, CARPET
    from . import mercs as MC
    W, H = 100, 64
    m = GameMap(s.map_key, 'town', s.name, W, H, ROCK)
    m.radius, m.sid, m.hid, m.signs = 60, s.id, None, []
    m.underground = True
    m.did, m.depth = getattr(s, 'deep_did', None), 0
    m.deco = bytearray(W * H)
    m.lights, m.glows = [], []
    m.ambient = .35
    m.carts = True
    m.stone_bridges = True
    names = town_names('dwarf')

    def room(x0, y0, x1, y1, t=FLOOR):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                m.set(x, y, t)

    def dig(a, b, t=FLOOR, width=1):
        (x0, y0), (x1, y1) = a, b
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for k in range(n + 1):
            x, y = round(x0 + (x1 - x0) * k / n), round(y0 + (y1 - y0) * k / n)
            for d in range(-(width // 2), width - width // 2):
                for xx, yy in ((x + d, y), (x, y + d)):
                    if m.inb(xx, yy) and m.tile(xx, yy) == ROCK:
                        m.set(xx, yy, t)

    def light(x, y, col=TORCH_COL, r=5):
        m.lights.append((x, y, col, r))

    def oval(cx, cy, rx, ry):
        return [(x, y) for y in range(int(cy - ry) - 1, int(cy + ry) + 2) for x in range(int(cx - rx) - 1, int(cx + rx) + 2)
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1]
    gy = 32
    # the gate tunnel, the chasm and the bridge, with the first kings in stone on either side
    room(0, gy - 1, 10, gy + 1)
    m.entry = (0, gy)
    for y in range(1, H - 1):
        x0 = 12 + int(1.5 * math.sin(y / 4)) + (1 if y % 7 == 0 else 0)
        for x in range(x0, x0 + 4):
            m.set(x, y, CHASM)
    for y in range(gy - 1, gy + 2):
        for x in range(10, 20):
            if m.tile(x, y) == CHASM:
                m.set(x, y, BRIDGE)
            elif m.tile(x, y) == ROCK:
                m.set(x, y, FLOOR)
    room(19, gy - 4, 27, gy + 4)                 # the gate hall
    for x, y in ((9, gy - 2), (9, gy + 2), (20, gy - 4), (20, gy + 4)):
        m.set(x, y, STATUE)
    m.signs.append((19, gy - 6, 'THE FIRST KINGS'))
    m.chasm_note = True
    light(23, gy, r=6)
    # the avenue to the ring street
    dig((27, gy), (41, gy), width=3)
    for x in range(30, 41, 5):
        light(x, gy - 1, r=4)
        m.deco[(gy - 1) * W + x] = TORCH
    # the Great Forge in the middle, molten iron at its heart
    cx, cy = 58, 32
    for x, y in oval(cx, cy, 9, 5):
        m.set(x, y, FLOOR)
    for x, y in oval(cx, cy, 3.2, 1.6):
        m.set(x, y, MOLTEN)
    m.lights.append((cx, cy, (255, 110, 30), 10))
    m.glows.append((cx, cy, (255, 110, 30), 8))
    for k in range(6):
        a = k / 6 * math.tau + .5
        m.set(round(cx + 6.5 * math.cos(a)), round(cy + 3.6 * math.sin(a)), ANVIL)
    m.signs.append((cx - 6, cy - 7, 'THE GREAT FORGE'))
    # the ring street round it, and the passages in to the forge
    ring = [(x, y) for x, y in oval(cx, cy, 17, 12) if ((x - cx) / 14.5) ** 2 + ((y - cy) / 9.6) ** 2 > 1]
    for x, y in ring:
        m.set(x, y, FLOOR)
    for a, b in (((cx, cy - 5), (cx, cy - 11)), ((cx, cy + 5), (cx, cy + 11)), ((cx - 9, cy), (cx - 16, cy)),
                 ((cx + 9, cy), (cx + 16, cy))):
        dig(a, b, width=3)
    for k in range(8):
        a = k / 8 * math.tau + .4
        x, y = round(cx + 16 * math.cos(a)), round(cy + 11 * math.sin(a))
        if m.tile(x, y) == FLOOR:
            light(x, y, r=5)
            m.deco[y * W + x] = TORCH
    # the shops on the ring street: smith, trade house, inn and healer (the temple has its own ward)
    shops = {}
    for key, (x0, y0, x1, y1), door in (('smith', (37, 14, 49, 19), (44, 19)), ('trade', (67, 14, 79, 19), (72, 19)),
                                        ('inn', (37, 45, 49, 51), (44, 45)), ('healer', (67, 45, 79, 50), (72, 45))):
        room(x0, y0, x1, y1, PLANK if key == 'inn' else FLOOR)
        tgt = (door[0], cy - 10 if y0 < cy else cy + 10)
        dig(door, tgt)
        m.set(door[0], door[1], DOOR)
        shops[key] = (x0, y0, x1, y1)
        light((x0 + x1) // 2, (y0 + y1) // 2, r=6)
    x0, y0, x1, y1 = shops['smith']
    for x in range(x0 + 1, x1, 3):
        m.set(x, y0, ANVIL)
    m.lights.append((x0 + 2, y0, (255, 120, 40), 4))
    m.signs.append((x0 + 2, y0 - 1, 'SMITH'))
    m.mons.append(make_npc(game, f'{names.pop()} the Smith', 'shop', '#d8d0b0', x0 + 6, y0 + 2, True, race='dwarf'))
    x0, y0, x1, y1 = shops['trade']
    for x in range(x0 + 2, x1 - 1, 3):
        m.set(x, y0 + 1, STALL)
    m.signs.append((x0 + 1, y0 - 1, 'TRADE HOUSE'))
    m.mons.append(make_npc(game, f'{names.pop()} the Trader', 'market', '#f2c44a', x0 + 6, y0 + 3, True, race='dwarf'))
    x0, y0, x1, y1 = shops['inn']
    for x in range(x0 + 2, x1 - 1, 3):
        m.set(x, y1 - 1, TABLE)
    m.set(x1, y0 + 1, BARREL)
    m.set(x0, y0 + 1, BARREL)
    m.signs.append((x0 + 2, y1 + 1, 'INN'))
    m.mons.append(make_npc(game, f'Innkeeper {names.pop()}', 'inn', '#e0a060', x0 + 6, y0 + 2, True, race='dwarf'))
    x0, y0, x1, y1 = shops['healer']
    for x in range(x0 + 2, x1 - 1, 4):
        m.set(x, y1, BED)
    m.signs.append((x0 + 2, y1 + 1, 'HEALER'))
    m.mons.append(make_npc(game, f'{names.pop()} the Healer', 'herbalist', '#90d070', x0 + 6, y0 + 2, True, race='dwarf'))
    # the north ward: the king's High Seat
    room(48, 2, 68, 10)
    dig((cx, 10), (cx, cy - 12), width=3)
    for x in range(52, 65):
        for y in range(3, 10):
            m.deco[y * W + x] = CARPET
    m.set(cx, 2, STATUE)
    for x in (50, 66):
        light(x, 6, r=6)
        m.deco[6 * W + x] = TORCH
    m.signs.append((51, 1, 'THE HIGH SEAT'))
    m.mons.append(make_npc(game, f'King {names.pop()}', 'thane', '#ffd860', cx, 3, True, race='dwarf'))
    for gx in (cx - 3, cx + 3):
        townsfolk(game, m, [(gx, 9)], (gx, 9), names, 'guard', '#b0b8c8', role='guard')
    # the west ward: the barracks, where dwarves sign on as hirelings
    room(26, 40, 36, 48)
    dig((31, 40), (31, gy + 2))
    m.set(31, 40, DOOR)
    for y in range(41, 48, 2):
        m.set(35, y, BED)
    light(30, 44, r=5)
    m.signs.append((27, 49, 'BARRACKS'))
    rng = random.Random(s.id * 7919 + game.day // 7)
    for k in range(2):
        o = MC.make_offer(game, rng)
        o['kind'] = rng.choice(['defender', 'defender', 'warrior'])
        o['name'] = names.pop()
        o['fee'], o['wage'] = MC.fee_for(o['kind'], o['lvl']), MC.wage_for(o['kind'], o['lvl'])
        n = make_npc(game, f'{o["name"]}, of the clan guard', 'recruit', '#c8b8a0', 28 + k * 3, 43, True, race='dwarf')
        n.offer = o
        m.mons.append(n)
    # the east ward: the temple
    room(82, 25, 96, 39)
    dig((75, cy), (82, cy), width=3)
    m.set(95, cy, ALTAR)
    for x in range(85, 93, 2):
        for y in (28, 36):
            m.set(x, y, TABLE)
    light(92, cy, (255, 220, 160), 7)
    m.signs.append((84, 24, 'TEMPLE'))
    m.mons.append(make_npc(game, f'Brother {names.pop()}', 'healer', '#f4f0e6', 93, cy, True, race='dwarf'))
    # the south ward: the homes, the cart station and the stair down to the mines
    room(40, 54, 76, 58)
    dig((cx, cy + 12), (cx, 54), width=3)
    homes = []
    for hx in range(41, 76, 6):
        for hy0, hy1, door_y in ((60, 62, 59), ):
            room(hx, hy0, hx + 4, hy1, PLANK)
            m.set(hx + 2, door_y, DOOR)
            m.set(hx, hy1, BED)
            homes.append((hx + 2, hy0 + 1))
    room(78, 53, 96, 58)                         # the cart station
    dig((76, 56), (78, 56))
    for x in range(79, 97):
        m.set(x, 57, RAIL)
    m.set(86, 57, CART)
    m.set(92, 57, CART)
    light(86, 55, r=5)
    m.signs.append((80, 52, 'CART LINE'))
    m.mons.append(make_npc(game, f'{names.pop()} the Cartwright', 'cartwright', '#c8a070', 88, 55, True, race='dwarf'))
    room(40, 47, 46, 52)
    dig((43, 53), (43, 52))
    m.set(43, 48, DOWN)
    m.lights.append((43, 48, (90, 140, 255), 3))
    m.signs.append((39, 46, 'THE MINES'))
    for x in range(44, 74, 6):
        light(x, 56, r=4)
    # the people of the hold
    for gx, gy2 in ((25, gy - 3), (25, gy + 3)):
        townsfolk(game, m, [(gx, gy2)], (gx, gy2), names, 'guard', '#b0b8c8', role='guard')
    jobs = ['smith', 'smith', 'smith', 'miner', 'miner', 'brewer', 'mason', 'stonecutter', 'miner']
    for j in jobs:
        if j == 'smith':
            a = random.uniform(0, math.tau)
            work = (round(cx + 7.5 * math.cos(a)), round(cy + 4.2 * math.sin(a)))
            if m.tile(*work) != FLOOR:
                work = (cx - 5, cy)
        elif j == 'miner':
            work = (43 + random.randint(-2, 2), 50)
        elif j == 'brewer':
            work = (44, 47)
        else:
            work = random.choice(ring)
        townsfolk(game, m, homes, work, names, j, '#c8a070')
    m.set(28, gy - 2, D.SIGNPOST)
    m.signpost = (28, gy - 2)
    m.portal_pos = (cx - 1, cy + 7)
    m.centre = (cx, cy + 8)
    m.glows += [(x, y, c, r) for x, y, c, r in m.lights]
    return m


def thane_talk(game, npc):
    hold = game.here.name if game.here else 'the hold'
    line = random.choice(THANE_LINES).format(hold=hold)
    game.request = ('dialog', npc.name, f'"{line}"')


# ------------------------------------------------------------------ the villages in the hills
def gen_village(game, s):
    """A dwarf village in the hills before the mountains: stone houses round a square, goat terraces on the slope, the
    mine above the village with its carts, a smelter, a mead hall, a brewery and a watchtower."""
    from .towns import town_names, townsfolk, LIVESTOCK
    W, H = 84, 54
    m = GameMap(s.map_key, 'town', s.name, W, H, GRASS)
    m.radius, m.sid, m.hid, m.signs = 60, s.id, None, []
    m.wall_fg = (168, 162, 150)
    m.lights, m.glows = [], []
    m.carts = True
    hold = hold_of(game, s)
    m.did = getattr(hold, 'deep_did', None) if hold else None
    names = town_names('dwarf')
    for i in range(len(m.t)):
        r = random.random()
        m.t[i] = D.HILLS if r < .25 else TREE if r < .29 else GRASS
    # the mountain behind the village, and the mine cut into it
    for x in range(W):
        top = 9 + int(2 * math.sin(x / 6))
        for y in range(top):
            m.set(x, y, ROCK)
    for y in range(3, 12):
        for x in range(38, 46):
            m.set(x, y, FLOOR)
    for x, y in ((37, 4), (46, 4), (37, 8), (46, 8)):
        m.set(x, y, PROP)
    for x, y in ((39, 2), (42, 2), (44, 2), (37, 6), (46, 6)):
        m.set(x, y, ORE)
    for y in range(5, 14):
        m.set(41, y, RAIL)
    m.set(41, 9, CART)
    m.signs.append((36, 12, 'THE MINE'))
    m.adit = (38, 3, 46, 11)

    def house(x0, y0, w, h, kind):
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                m.set(x, y, WALL if x in (x0, x0 + w - 1) or y in (y0, y0 + h - 1) else PLANK)
        return [(x, y) for y in range(y0 + 1, y0 + h - 1) for x in range(x0 + 1, x0 + w - 1)]
    sq = (42, 30)
    # the square and the road down through the village
    ey = 40
    for x in range(0, sq[0] + 1):
        m.set(x, ey, PATH)
    for y in range(13, ey + 1):
        m.set(sq[0], y, PATH)
    for x in range(sq[0] - 6, sq[0] + 7):
        for y in range(sq[1] - 2, sq[1] + 3):
            m.set(x, y, PATH)
    m.entry = (0, ey)
    # the mead hall (the inn), the smelter, the brewery, the market stall
    hall = house(24, 24, 13, 7, 'inn')
    m.set(36, 27, DOOR)
    for x in range(26, 34, 3):
        m.set(x, 28, TABLE)
    m.set(25, 25, BARREL)
    m.signs.append((25, 23, 'MEAD HALL'))
    m.mons.append(make_npc(game, f'{names.pop()} the Mead-keeper', 'inn', '#e0a060', 30, 26, True, race='dwarf'))
    smelt = house(50, 16, 10, 6, 'smelter')
    m.set(50, 19, DOOR)
    m.set(56, 18, MOLTEN)
    m.set(57, 18, FIREPIT)
    m.lights.append((56, 18, (255, 110, 30), 5))
    m.glows.append((56, 18, (255, 110, 30), 4))
    m.set(52, 17, ANVIL)
    m.signs.append((50, 15, 'SMELTER'))
    m.mons.append(make_npc(game, f'{names.pop()} the Smith', 'shop', '#d8d0b0', 53, 19, True, race='dwarf'))
    brew = house(50, 33, 10, 6, 'brewery')
    m.set(50, 35, DOOR)
    for x in range(52, 59, 2):
        m.set(x, 34, BARREL)
    m.signs.append((50, 39, 'BREWERY'))
    m.set(sq[0] + 3, sq[1] - 1, STALL)
    m.mons.append(make_npc(game, f'{names.pop()} the Trader', 'market', '#f2c44a', sq[0] + 3, sq[1], True, race='dwarf'))
    m.mons.append(make_npc(game, f'Elder {names.pop()}', 'elder', '#e0d0b0', sq[0] - 2, sq[1], True, race='dwarf'))
    # the cart stop on the line to the hold
    for x in range(60, W):
        m.set(x, 26, RAIL)
    m.set(66, 26, CART)
    m.mons.append(make_npc(game, f'{names.pop()} the Cartwright', 'cartwright', '#c8a070', 64, 27, True, race='dwarf'))
    m.signs.append((60, 24, 'CART LINE'))
    # the watchtower over the road
    for y in range(34, 39):
        for x in range(2, 7):
            m.set(x, y, WALL if x in (2, 6) or y in (34, 38) else FLOOR)
    m.set(4, 38, DOOR)
    # a river that runs past the village on the world map runs past it here too, where it spoils the least
    from .towns import river_course, carve_river
    course = river_course(game, s, m, 12)
    if course:
        ground = (GRASS, D.HILLS, TREE)
        built = set(m.t) - set(ground) - {PATH, RAIL}
        along_x = abs(course[-1][0] - course[0][0]) >= abs(course[-1][1] - course[0][1])
        best = None
        for off in sorted(range(-60, 61, 2), key=abs):
            pts = [(x, y + off) if along_x else (x + off, y) for x, y in course]
            test = GameMap('x', 'town', 'x', W, H, GRASS)
            test.t = list(m.t)
            carve_river(test, pts, 1.8, keep=built)
            hurt = sum(1 for i, t in enumerate(test.t) if t != m.t[i] and any(
                m.inb(i % W + dx, i // W + dy) and m.t[(i // W + dy) * W + i % W + dx] in built
                for dx in (-1, 0, 1) for dy in (-1, 0, 1)))
            wet = sum(1 for i, t in enumerate(test.t) if t != m.t[i])
            if wet >= (W if along_x else H) * 3 and (best is None or hurt < best[0]):
                best = (hurt, pts)
            if best and best[0] == 0:
                break
        if best:
            carve_river(m, best[1], 1.8, keep=built)
        for o in m.mons:
            if m.tile(o.x, o.y) in (D.WATER, D.SHALLOW):
                dry = min(((x, y) for y in range(H) for x in range(W) if m.tile(x, y) in (GRASS, PATH, D.HILLS)),
                          key=lambda c: cheb(c[0], c[1], o.x, o.y))
                o.x, o.y = dry
    # stone houses
    homes = []
    for x0, y0 in ((8, 28), (8, 34), (16, 42), (28, 42), (64, 32), (70, 38), (24, 14), (56, 42), (38, 46), (68, 46)):
        if any(m.tile(x, y) not in (GRASS, D.HILLS, TREE) for y in range(y0 - 1, y0 + 6) for x in range(x0 - 1, x0 + 8)):
            continue
        cells = house(x0, y0, 7, 5, 'home')
        m.set(x0 + 3, y0 + (0 if y0 > sq[1] else 4), DOOR)
        m.set(x0 + 1, y0 + 1, BED)
        homes.append(cells[-1])
    # goat terraces on the slope, walled with stone
    for ty in (14, 18):
        for x in range(4, 22):
            if m.tile(x, ty) in (GRASS, D.HILLS, TREE):
                m.set(x, ty, FENCE)
        for x in range(4, 22):
            if m.tile(x, ty + 1) in (GRASS, D.HILLS, TREE):
                m.set(x, ty + 1, GRASS)
    for x, y in ((7, 16), (12, 16), (17, 20), (9, 20)):
        name, ch, fg = ('A goat', 'g', '#c8b890')
        if m.tile(x, y) in (GRASS, D.HILLS):
            m.mons.append(make_npc(game, name, 'livestock', fg, x, y, False, ch=ch))
    m.signs.append((4, 12, 'GOAT TERRACES'))
    townsfolk(game, m, [(4, 36)], (4, 41), names, 'guard', '#b0b8c8', role='guard')
    for j in ['miner', 'miner', 'miner', 'smith', 'brewer', 'goatherd', 'mason']:
        work = {'miner': (42, 6), 'smith': (54, 19), 'brewer': (55, 36), 'goatherd': (12, 20)}.get(j, (sq[0] + random.randint(-5, 5), sq[1] + 1))
        townsfolk(game, m, homes or [sq], work, names, j, '#c8a070')
    m.portal_pos = (sq[0] - 4, sq[1] + 1)
    m.centre = sq
    m.lights += [(sq[0] - 6, sq[1] - 2, TORCH_COL, 5), (sq[0] + 6, sq[1] + 2, TORCH_COL, 5)]
    m.glows += [(x, y, c, r) for x, y, c, r in m.lights]
    return m


# ------------------------------------------------------------------ the mines
def dress_mine(game, m, dg, depth):
    """A level of the mines: ore and gems in the walls, pit props (some cracked, in the old galleries), lamps and dwarf
    miners in the working galleries at the top, and the Deep Gate at the bottom of the old ones."""
    from .dress import TORCH
    from .towns import town_names
    w = m.w
    hold = game.world.settlements[dg.mine] if getattr(dg, 'mine', None) is not None else None
    m.mine, m.mine_depth = dg.mine, depth
    m.working = depth <= WORKING
    old = not m.working
    if getattr(m, 'deco', None) is None:
        m.deco = bytearray(w * m.h)
    wall_next = [i for i, t in enumerate(m.t) if t in (ROCK, D.WALL) and 0 < i % w < w - 1 and 0 < i // w < m.h - 1 and
                 any(m.t[i + o] == FLOOR for o in (1, -1, w, -w))]
    p_ore, p_gem = (.03, .002) if m.working else (.045, .006) if depth < GATE_LEVEL + 1 else (.02, .004)
    for i in wall_next:
        r = random.random()
        if r < p_gem:
            m.t[i] = GEMS
        elif r < p_gem + p_ore:
            m.t[i] = ORE
        elif r < p_gem + p_ore + (.035 if depth <= GATE_LEVEL else 0):
            m.t[i] = CRACKED if old and random.random() < .45 else PROP
    if m.working:
        m.mons = [o for o in m.mons if o.is_npc] if depth == 1 else [o for o in m.mons if o.is_npc or random.random() < .3]
        floors = [i for i, t in enumerate(m.t) if t == FLOOR]
        random.shuffle(floors)
        lamps = []
        for i in floors:
            if len(lamps) >= 14:
                break
            x, y = i % w, i // w
            if all(cheb(x, y, a, b) > 7 for a, b in lamps):
                lamps.append((x, y))
                m.deco[i] = TORCH
                m.lights.append((x, y, TORCH_COL, 6))
        m.ambient = max(getattr(m, 'ambient', .3), .45)
        names = town_names('dwarf')
        from .worldgen import rand_free
        for k in range(4 if depth == 1 else 2):
            c = rand_free(game, m, lambda t: t == FLOOR)
            if c:
                role = 'foreman' if k == 0 and depth == 1 else 'villager'
                n = make_npc(game, f'{names.pop()} the Foreman' if role == 'foreman' else f'{names.pop()} the miner',
                             role, '#c8a070', c[0], c[1], role == 'foreman', race='dwarf')
                n.job = 'miner'
                m.mons.append(n)
    if depth == GATE_LEVEL and DOWN in m.t:
        i = m.t.index(DOWN)
        m.signs = getattr(m, 'signs', []) + [(i % w - 6, i // w - 1, 'THE DEEP GATE')]
        m.lights.append((i % w, i // w, (90, 140, 255), 4))
    if depth > GATE_LEVEL and hold:
        m.name = f'The Deep Roads under {hold.name}'


def on_level(game, m, first):
    """Coming down a level of the mines: say where you are."""
    d = getattr(m, 'mine_depth', None)
    if d is None or not first:
        return
    if d == 1:
        game.msg('The working galleries: lamps on the walls, carts and the ring of picks. Ore glints in the rock.', 'info')
    elif d == WORKING + 1:
        game.msg('The old galleries. No lamps here, and the props are old. Watch for cracked ones.', 'bad')
    elif d == GATE_LEVEL + 1:
        game.msg('You pass the Deep Gate. Beyond it run the Deep Roads, which the dwarves lost long ago.', 'bad')


def on_step(game):
    """Cracked props groan when you pass under them, and now and then one gives way."""
    m, p = game.map, game.player
    near = [(p.x + dx, p.y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)
            if m.inb(p.x + dx, p.y + dy) and m.tile(p.x + dx, p.y + dy) == CRACKED]
    if not near:
        return
    if not getattr(m, 'warned_props', False):
        m.warned_props = True
        game.msg('A cracked prop creaks over your head. Dust trickles down.', 'bad')
    if random.random() < .02:
        cave_in(game, *near[0])


def has_pick(game):
    return any(i.k == 'tool' and i.t == 'pick' for i in game.player.inv)


def may_dig(game):
    """In the dwarves' own galleries you dig only when the clan knows you; old galleries are free for anyone."""
    m, p = game.map, game.player
    if p.race == 'dwarf':
        return True
    if getattr(m, 'mine', None) is not None and not getattr(m, 'working', False):
        return True
    s = game.world.settlements[m.mine] if getattr(m, 'mine', None) is not None else game.here
    return s is not None and s.rep >= 15


def dig(game, x, y):
    """Bump a vein to dig it out, with a pick. Ore and gems go on your cart, like any other trade goods."""
    from . import economy as ECO, lifeskills as LS, crime as CR
    m, p = game.map, game.player
    t = m.tile(x, y)
    if t == RUBBLE:
        m.set(x, y, FLOOR)
        game.msg('You clear the rubble away.' if has_pick(game) else 'You clear the rubble away with your bare hands. It takes a while.')
        return 6 if has_pick(game) else 20
    if not has_pick(game):
        game.msg('An ore vein. You need a pick to dig it; outfitters sell them.' if t == ORE else
                 'A vein of gems glitters in the rock. You need a pick to dig it out.')
        return 0
    if game.hostile_visible():
        game.msg('Not with enemies about!', 'bad')
        return 0
    good = 'gems' if t == GEMS else 'ore'
    metal = 'iron'
    if good == 'ore':
        from . import crafts as CRF
        metal = CRF.dig_vein(game, x, y)
        if metal is None:
            return 0
    if metal == 'iron' and ECO.cargo_weight(p) + D.GOODS[good]['w'] > ECO.cargo_capacity(p):
        game.msg(f'You have no room for {D.GOODS[good]["name"].lower()}. Sell some cargo, or bring a mule or a cart.', 'bad')
        return 0
    if getattr(m, 'tribe', None) == 'kobolds':
        from . import tribes as TR
        TR.theft(game)
    elif (getattr(m, 'working', False) or getattr(m, 'sid', None) is not None) and not may_dig(game):
        seen = any(o.is_npc and getattr(o, 'race', '') == 'dwarf' and cheb(o.x, o.y, p.x, p.y) <= 9 for o in m.mons)
        foreman = next((o for o in m.mons if o.is_npc and getattr(o, 'race', '') == 'dwarf' and cheb(o.x, o.y, p.x, p.y) <= 9), None)
        if foreman:
            game.say(foreman, 'Oi! Those veins belong to the clan!')
        CR.commit(game, 8, "digging in the dwarves' galleries", witnessed=1.0 if seen else .3)
    r = LS.rank(game, 'mining')
    turns = max(6, 22 - r)
    m.set(x, y, FLOOR)
    from . import crafts as CRF
    at = CRF.METALS[metal][2] if good == 'ore' else 10
    LS.gain(game, 'mining', 3 if good == 'gems' else 1 + at / 10, at=at, what=metal if good == 'ore' else 'gems')
    if metal != 'iron':
        CRF.give(game, 'ore_' + metal, 1 + (1 if random.random() < .3 else 0))
        game.msg(f'You break {CRF.ORE_NAME[metal].lower()} out of the vein!', 'gold')
    elif good == 'gems':
        p.cargo[good] = p.cargo.get(good, 0) + 1
        game.msg('You prise a fist of rough gems out of the rock!', 'gold')
    else:
        p.cargo[good] = p.cargo.get(good, 0) + 1
        game.msg(random.choice(['You dig out a load of iron ore.', 'Chunks of ore come loose under your pick.',
                                'You break the vein out of the rock: a good load of ore.']), 'good')
    if r >= 10 and good == 'ore' and random.random() < .08:
        p.cargo['gems'] = p.cargo.get('gems', 0) + 1
        game.msg('Among the ore, a gem!', 'gold')
    cracked = [(x + dx, y + dy) for dx in range(-2, 3) for dy in range(-2, 3)
               if m.inb(x + dx, y + dy) and m.tile(x + dx, y + dy) == CRACKED]
    if cracked and random.random() < .5:
        cave_in(game, *cracked[0])
    return turns


def cave_in(game, x, y):
    """The prop gives way and the roof comes down around it."""
    m, p = game.map, game.player
    game.msg('The cracked prop splits with a crack like thunder. The roof comes down!', 'bad')
    m.set(x, y, RUBBLE)
    hit = False
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            cx, cy = x + dx, y + dy
            if not m.inb(cx, cy) or m.tile(cx, cy) != FLOOR:
                continue
            if (cx, cy) == (p.x, p.y):
                hit = True
                continue
            if m.mon_at(cx, cy) or random.random() < .45:
                continue
            m.set(cx, cy, RUBBLE)
    if hit or cheb(p.x, p.y, x, y) <= 2:
        dmg = max(3, round(game.stats()['max_life'] * random.uniform(.15, .3)))
        game.hurt(dmg, 'a cave-in')
    game.events.append(('shake',))


def chasm(game):
    from . import events as EV
    EV.ask(game, 'chasm', 'The chasm', 'The chasm drops away into the dark. Far below you hear water, and the ring of '
           'picks: the mines. You could climb down, but not without a fall.',
           [('Climb down into the dark', 'down'), ('Step back', 'bye')])


def r_chasm(game, choice, ctx):
    from .worldgen import rand_free
    if choice != 'down':
        return
    m = game.map
    did = getattr(m, 'did', None)
    depth = getattr(m, 'depth', 0) or 0
    dg = game.world.dungeons.get(did) if did else None
    if not dg:
        game.msg('There is no way down here.')
        return
    depth = min(dg.depth, depth + 1)
    game.msg('You climb down, slip, and fall the last of the way!', 'bad')
    game.hurt(max(3, round(game.stats()['max_life'] * random.uniform(.1, .2))), 'a fall into the chasm')
    if game.dead:
        return
    game.enter_dungeon(did, depth, 'up')
    c = rand_free(game, game.map, lambda t: t == FLOOR)
    if c:
        game.player.x, game.player.y = c
        game.compute_fov()


# ------------------------------------------------------------------ the cart line
def stops(game, here):
    return [s for s in game.world.settlements if is_dwarven(s) and s.id != here.id]


def fare(here, s):
    return max(100, cheb(here.x, here.y, s.x, s.y) * 12)


def cart_talk(game, npc=None):
    from . import events as EV
    from .money import fmt
    here = game.here
    if here is None:
        game.msg('An ore cart.')
        return
    dest = sorted(stops(game, here), key=lambda s: cheb(here.x, here.y, s.x, s.y))[:6]
    if not dest:
        game.msg('The cart line runs nowhere from here.')
        return
    opts = [(f'{s.name} ({fmt(fare(here, s))}, {days(here, s)} day{"s" if days(here, s) > 1 else ""})', f'go:{s.id}') for s in dest]
    EV.ask(game, 'cart', npc.name if npc else 'The cart line', '"The carts run through the tunnels under the mountains, '
           'hold to hold, village to village. Sit on the ore and keep your hands in."', opts + [('Not today', 'bye')])


def days(a, b):
    return max(1, round(cheb(a.x, a.y, b.x, b.y) / 40))


def r_cart(game, choice, ctx):
    from .money import fmt
    here = game.here
    if not choice.startswith('go:') or here is None:
        return
    s = game.world.settlements[int(choice[3:])]
    cost = fare(here, s)
    p = game.player
    if p.gold < cost:
        game.msg(f'The fare is {fmt(cost)}.', 'bad')
        return
    p.gold -= cost
    n = days(here, s)
    game.msg(f'You ride the ore carts through the dark for {n} day{"s" if n > 1 else ""}.', 'info')
    game.end_turn(n * D.DAY_LEN, quiet=True)
    if game.dead:
        return
    game.over_pos = (s.x, s.y)
    game.enter_town(s.id)


# ------------------------------------------------------------------ talking
def talk(game, npc):
    if npc.role == 'cartwright':
        cart_talk(game, npc)
        return
    if npc.role == 'foreman':
        ok = may_dig(game)
        game.say(npc, 'Know the clan, dig the clan\'s rock. Pick in hand, mind the props.' if ok else
                 'These veins belong to the clan. Dig here and you answer to the king. The old galleries below are anyone\'s.')
        return
    thane_talk(game, npc)


def register():
    from . import events as EV
    EV.RESOLVERS['chasm'] = r_chasm
    EV.RESOLVERS['cart'] = r_cart


register()
