"""The goblin village (round 7; mockup `dungeons/mockups/E2b_goblin_village.png`): cut into the back wall of their
ravine, built like a settlement. A carved gate in the end of the ravine leads in; inside, a main gallery four wide
runs to the chief's hall at the back, with the market hall and its pillars, the forge, the family halls with their
hearths, the cell block (barred fronts between stone walls, a door in each), the wolf pens (a keepers' aisle, pens
cut into the rock, a barred front), a shrine, and the treasury behind the chief's hall; a lower gallery loops round.
Below lie the mine and the deep halls (a goblin hole of the large size, `delves.py`).

The village is a camp of `tribes.py` like the ravine itself: the same warn-then-rouse rule, traders, children and
workers who flee, captives for a rescue job. It rises with the ravine and calms with it. The chief's high seat
decides it: with the chief dead, whoever sits in it holds the village, and the goblins bow."""
import random

from . import data as D
from .data import FLOOR, WALL, ROCK, DOOR, UP, DOWN
from . import tribes as TR
from .worldgen import cheb

W, H = 120, 70
GALLERY = (33, 36)                 # the main gallery's rows


def key(site):
    return f'{site.map_key}:v'


def deep_id(site):
    return f'gm{site.id}'


def setup(world, site):
    """The mine and deep halls under the village: a Dungeon record with d.site, off the world map."""
    from .world import Dungeon
    did = deep_id(site)
    if did in world.dungeons:
        return
    danger = world.region_at(site.x, site.y).danger
    dg = Dungeon(did, f'The Deep Halls under {site.name}', 1, max(1, danger * 2), 'rooms', 'warren', 'goblin_king',
                 D.hexrgb('#7a6a4a'), site.x, site.y, False)
    dg.site, dg.size, dg.home = site.id, 'large', key(site)
    world.dungeons[did] = dg
    site.below = did


# ------------------------------------------------------------------ the map
def make(game, site):
    m = TR._new(site, W, H, ROCK)
    m.key = key(site)
    m.name = f'{site.name}: the village'
    m.underground, m.ambient, m.built = True, .4, True
    m.wall_fg = (150, 130, 96)
    m.village = True
    m.along_ns, m.warn_line = False, 9
    lvl = TR.level(game, site)
    names = TR._names('goblin')
    random.shuffle(names)

    def hall(x0, y0, x1, y1):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                edge = x in (x0, x1) or y in (y0, y1)
                if m.tile(x, y) != FLOOR or not edge:
                    m.set(x, y, WALL if edge else FLOOR)
        for y in range(y0 + 1, y1):
            for x in range(x0 + 1, x1):
                m.inner.add((x, y))

    def cut(x0, y0, x1, y1):
        """A way through: floor, walls left where they were."""
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                m.set(x, y, FLOOR)
                m.inner.add((x, y))

    def who(x, y, look, name, foe=None, **kw):
        return TR.who(game, m, x, y, look, name, foe, race=kw.pop('race', 'goblin'), **kw)
    g0, g1 = GALLERY
    # the gate hall, just inside the rock, and the main gallery to the back
    hall(2, g0 - 5, 14, g1 + 5)
    cut(0, g0 + 1, 2, g1 - 1)
    hall(14, g0 - 1, 101, g1 + 1)
    cut(14, g0, 14, g1)
    m.set(1, (g0 + g1) // 2, UP)
    m.entry = (0, (g0 + g1) // 2)
    for x in (4, 12):
        m.set(x, g0 - 4, D.PROP)
        m.set(x, g1 + 4, D.PROP)
    m.gate = (8, (g0 + g1) // 2)
    for y in (g0 - 2, g1 + 2):
        who(10, y, TR.GOB, 'A goblin on the gate', 'gobarcher', job='gate', stay=True)
    # the market hall: pillars carry the roof, stalls cut from the living rock
    mx0, mx1 = 22, 50
    hall(mx0, 7, mx1, 24)
    cut(34, 24, 37, g0 - 1)
    for x in range(mx0 + 4, mx1 - 2, 5):
        m.set(x, 10, D.PILLAR)
        m.set(x, 21, D.PILLAR)
    for x in range(mx0 + 5, mx1 - 4, 6):
        m.set(x, 15, D.STALL)
        m.set(x + 1, 15, D.STALL)
    who(30, 13, ('☺', (220, 200, 160)), f'{TR._names("human")[0]}, a fence', flee=True, job='trader', race='human', stay=True)
    for x in (27, 39, 45):
        who(x, 17, TR.GOB, 'A goblin hawker', flee=True, job='worker')
    m.signs.append((mx0 + 1, 6, 'MARKET'))
    # the forge
    hall(56, 9, 76, 24)
    cut(64, 24, 67, g0 - 1)
    for x in (60, 64):
        m.set(x, 12, D.ANVIL)
    TR.fire(m, 70, 12, r=5)
    m.set(72, 12, D.HEARTH)
    for x in (59, 62, 65):
        m.set(x, 22, D.BARREL)
    m.set(73, 21, D.RACK)
    for x in (61, 67):
        who(x, 14, TR.GOB, 'A goblin smith', 'goblin', job='worker')
    # the shrine
    hall(80, 12, 92, 24)
    cut(85, 24, 87, g0 - 1)
    m.set(86, 15, D.IDOL)
    for x, y in ((83, 14), (89, 14), (84, 18), (88, 18)):
        m.set(x, y, D.GLITTER if random.random() < .5 else D.BONES)
    who(86, 19, ('g', (150, 220, 120)), 'The gully shaman', 'gob_shaman', job='shaman')
    # the family halls with their hearths
    for fx0 in (18, 36):
        hall(fx0, 41, fx0 + 15, 54)
        cut(fx0 + 6, g1 + 1, fx0 + 8, 40)
        m.set(fx0 + 7, 47, D.HEARTH)
        m.lights.append((fx0 + 7, 47, (255, 150, 60), 5))
        for k in range(5):
            m.set(fx0 + 2 + k * 3, 53 if k % 2 else 42, D.FURS)
        for k in range(2):
            who(fx0 + 4 + k * 6, 49, TR.GOB_YOUNG, 'A goblin brat', flee=True, job='young')
        who(fx0 + 10, 44, TR.GOB, 'A goblin mother', flee=True, job='worker')
    # the cell block: an aisle, cells on both sides, bars only as the front between stone walls
    hall(56, 40, 74, 62)
    cut(64, g1 + 1, 66, 40)
    cut(64, 40, 66, 61)
    m.cages = []
    caps = 0
    for k, cy in enumerate((42, 48, 54)):
        for side in (0, 1):
            x0, x1 = (57, 63) if side == 0 else (67, 73)
            for y in range(cy, cy + 5):
                m.set(x0 if side == 1 else x1, y, D.CAGE)        # the barred front, on the aisle
            for x in range(x0, x1 + 1):
                m.set(x, cy - 1, WALL)
                m.set(x, cy + 5, WALL)
            front = x1 if side == 0 else x0
            m.cages.append((min(x0, front), cy - 1, max(x1, front), cy + 5))
            m.set(front, cy + 2, DOOR)
            m.set(x0 + 2 if side == 0 else x1 - 2, cy + 1, D.FURS)
            if caps < 2 and random.random() < .5:
                TR.captive(game, m, x0 + 3 if side == 0 else x1 - 3, cy + 3)
                caps += 1
    m.cell_doors = [(x, y) for y in range(m.h) for x in (63, 67) if m.tile(x, y) == DOOR]
    who(65, 58, TR.GOB, 'A goblin jailer', 'goblin', job='guard', stay=True)
    # the wolf pens: a keepers' aisle, pens cut into the rock, a barred front with a door on each
    hall(78, 40, 98, 52)
    cut(84, g1 + 1, 86, 40)
    for k, px in enumerate(range(79, 97, 6)):
        for x in range(px, px + 5):
            m.set(x, 45, D.CAGE)
        m.set(px + 2, 45, DOOR)
        if px + 5 <= 97:
            for y in range(45, 52):
                m.set(px + 5, y, WALL)
        who(px + 2, 48, ('C', (170, 160, 150)), 'A goblin wolf', 'wolf', job='beast')
    who(90, 42, TR.GOB, 'A wolf keeper', 'goblin', job='worker')
    # the chief's hall at the back, and the treasury behind it
    hall(101, 16, 117, 50)
    cut(101, g0, 101, g1)
    for y in range(19, 48, 5):
        m.set(103, y, D.SPIRITTOTEM)
        m.set(115, y, D.SPIRITTOTEM)
    m.set(109, 18, D.HIGHSEAT)
    m.throne = (109, 18)
    chief = who(109, 19, ('g', (240, 200, 80)), f'{names[0]}, chief of the gully', 'gob_boss', job='chief')
    for x in (106, 112):
        who(x, 21, TR.GOB, 'A chief\'s guard', 'goblin', job='guard', stay=True)
    m.chief = chief.id if chief else None
    m.chief_name = names[0]
    hall(103, 52, 115, 62)
    cut(109, 50, 109, 51)
    m.set(109, 51, DOOR)
    for x, y in ((106, 55), (112, 55), (106, 59)):
        m.set(x, y, D.CHEST if (x, y) != (106, 59) else D.GLITTER)
    m.set(112, 59, D.GLITTER)
    m.treasury = (103, 52, 115, 62)
    # the loop round the back: a lower gallery from the family halls to the treasury, and the way down
    hall(24, 63, 104, 67)
    for fx in (24, 42):
        cut(fx, 54, fx + 2, 62)
    cut(98, 51, 100, 63)
    m.set(80, 65, DOWN)
    for _ in range(3):
        x, y = random.randint(20, 95), random.randint(g0, g1)
        who(x, y, TR.GOB, 'A goblin', random.choice(['goblin', 'gobarcher', 'gob_sneak']))
    m.centre = (60, (g0 + g1) // 2)
    for i, t in enumerate(m.t):
        if t in (FLOOR, D.CAGE, DOOR) or (i % m.w, i // m.w) in m.inner:
            m.seen[i] = 0
    return m


# ------------------------------------------------------------------ coming and going
def stairs(game, t, d):
    """The carved gate between the ravine and the village, and the stair down to the deep halls."""
    m = game.map
    site = game.world.sites[m.site]
    if not getattr(m, 'village', False):
        if t == DOWN and d != 'up' and getattr(m, 'delve_gate', None):
            enter(game, site)
            return 1
        return None
    if t == UP and d != 'down':
        back_to_ravine(game, site)
        return 1
    if t == DOWN and d != 'up':
        setup(game.world, site)
        game.enter_dungeon(deep_id(site), 1, 'up')
        return 1
    return None


def enter(game, site, at=UP):
    p = game.player
    k = key(site)
    if k not in game.maps:
        game.maps[k] = make(game, site)
    vm = game.maps[k]
    rm = game.maps.get(site.map_key)
    if rm is not None and rm.roused and not vm.roused:
        vm.warned = True
        TR.rouse(game, vm, None)
    elif getattr(site, 'angry', -1) > game.day and not vm.roused:
        vm.warned = True
        TR.rouse(game, vm, None)
    game.cur = k
    i = vm.t.index(at) if at in vm.t else None
    p.x, p.y = ((i % vm.w) + (1 if at == UP else 0), i // vm.w) if i is not None else (vm.entry[0] + 1, vm.entry[1])
    game.msg('Through the carved gate you come into the goblins\' village, cut deep into the rock.'
             if at == UP else 'You climb back up into the village.', 'info')
    game.compute_fov()
    game.request = ('save',)


def back_to_ravine(game, site):
    p = game.player
    if site.map_key not in game.maps:
        from .sites import gen_site_map
        game.maps[site.map_key] = gen_site_map(game, site)
    rm = game.maps[site.map_key]
    vm = game.maps.get(key(site))
    if vm is not None and vm.roused and not rm.roused:
        rm.warned = True
        TR.rouse(game, rm, None)
    game.cur = site.map_key
    gx, gy = rm.delve_gate
    spots = [(gx + dx, gy + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)
             if rm.inb(gx + dx, gy + dy) and D.TILES[rm.tile(gx + dx, gy + dy)].walk and (dx or dy)]
    p.x, p.y = spots[0] if spots else (gx, gy)
    game.msg('You come out through the carved gate into the ravine.', 'info')
    game.compute_fov()
    game.request = ('save',)


def bump(game, x, y):
    """The chief's high seat: with the chief dead, whoever sits in it holds the village. Returns turns, or None."""
    m = game.map
    if not getattr(m, 'village', False) or m.tile(x, y) != D.HIGHSEAT:
        return None
    site = game.world.sites[m.site]
    chief = any(o.hp > 0 and (getattr(o, 'tjob', None) == 'chief' or o.name == getattr(m, 'chief_name', None))
                for o in m.mons)
    if chief:
        game.msg('The chief\'s high seat, heaped with stolen cloth. The chief would gut anyone who sat in it.', 'info')
        return 0
    if getattr(site, 'held', -1) > game.day:
        game.msg('You sit in the high seat again. The goblins bow, and mutter.', 'info')
        return 1
    site.held = game.day + 120
    site.angry = -1
    for mm in (m, game.maps.get(site.map_key)):
        if mm is None:
            continue
        for o in mm.mons:
            if not o.is_npc and (getattr(o, 'faction', None) == 'horde' or o.k.startswith('gob')):
                o.effects['fear'] = 30
    game.msg('You climb into the high seat. One by one the goblins put down their blades and bow: whoever holds the '
             'seat holds the village. For now.', 'unique')
    return 1


def ravine_gate(m, at, put, L, lo, hi):
    """Cut the carved gate into the end of the ravine, with the goblin tower beside it. Returns the gate cell."""
    a = L - 3
    c = (lo[a] + hi[a]) // 2
    for aa in range(L - 6, L):
        for cc in range(lo[aa], hi[aa] + 1):
            put(aa, cc, D.GRASS if abs(cc - c) > 1 else D.PATH)
    for aa in range(L - 2, L):
        for cc in range(lo[aa] - 2, hi[aa] + 3):
            put(aa, cc, ROCK)
    put(L - 2, c, DOWN)
    for dc in (-2, 2):
        put(L - 3, c + dc, D.PROP)
    tx, ty = at(L - 8, hi[L - 8] - 3)           # the goblin tower by the gate: scrap walls round a gong
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if m.inb(tx + dx, ty + dy):
                m.set(tx + dx, ty + dy, D.HIDE if max(abs(dx), abs(dy)) == 2 else D.PLANK)
    m.set(tx, ty, D.GONG)
    mx, my = at(L - 8, (lo[L - 8] + hi[L - 8]) // 2)
    door = min(((tx + dx, ty + dy) for dx, dy in ((0, -2), (0, 2), (-2, 0), (2, 0))),
               key=lambda q: abs(q[0] - mx) + abs(q[1] - my))
    m.set(door[0], door[1], DOOR)
    m.gob_tower = (tx, ty)
    return at(L - 2, c)
