"""Barrows (round 6): the grave of someone great, a small place (80 x 50), each people its own.

Outside, on its own land, the mound and its way in: a ring of standing stones round a hill (human), a dead great
tree (elf), a door cut in a rock face (dwarf), a little green hill (halfling), an outcrop of crystal (gnome), a
cairn among skull poles (orc), a hole in a slope (goblin), an old shaft (kobold), a hill of bones (gnoll), a sacred
pool round an island with a stone egg (lizardfolk). Inside, narrow and low, fights in passages, not hordes: a long
passage, an antechamber of grave goods, side rooms of bone niches, and the burial chamber with the bier.

The bier is the telling thing: take from it and the dead wake. Sometimes an older grave lies below (the kobolds'
always, and their loose floor gives way into it)."""
import random

from . import data as D
from .data import FLOOR, WALL, DOOR, UP, ROCK
from .entities import GameMap, make_monster, Item
from .worldgen import cheb, choose_monster
from . import places as PL

KING = {'human': ('draugr', 'The Hill King'), 'elf': ('banshee', 'The Eldest of the Roots'),
        'dwarf': ('draugr', 'The Stone King'), 'halfling': ('ghost', 'The Grieving Grandmother'),
        'gnome': ('wight', 'The Great Inventor'), 'orc': ('draugr', 'The Warlord under the Cairn'),
        'goblin': ('skel_warrior', 'The Boss, Dead and Grinning'), 'kobold': ('wight', 'The Old Hoardmaster'),
        'gnoll': ('ghast_lord', 'The Great Packlord'), 'lizard': ('wight', 'The Drowned Elder')}
INSIDE = {'human': 'A long passage lined with standing stones. The air is still and old.',
          'elf': 'Roots hold up the dark. Here the elves lie in cradles of root, under starlight lamps.',
          'dwarf': 'Behind the rune door: a hall of stone kings, and the cold of the deep.',
          'halfling': 'A family tomb, small and swept. Dried flowers lie at every niche.',
          'gnome': 'The dead lie sealed in crystal. Something clicks in the walls.',
          'orc': 'Under the cairn: piled stones, slain wargs and broken weapons.',
          'goblin': 'A zigzag way. Every turn smells of a trap.',
          'kobold': 'Coins everywhere, and a floor that sounds hollow.',
          'gnoll': 'Bones of every kill, heaped to the roof.',
          'lizard': 'Stone coffins sunk in a sacred pool, round an island with a stone egg.'}
BIER_TEXT = {'human': 'The hill king lies on his bier in rusted mail, a crown on his skull and treasure at his feet.',
             'elf': 'The eldest lies in a cradle of root. A sapling grows from her breast; silver lies in her hands.',
             'dwarf': 'The lord lies in his armour, his axe on his chest, gold heaped round him.',
             'halfling': 'Grandmother lies under a quilt gone grey. A little purse lies by her hand.',
             'gnome': 'The great inventor lies sealed in clear crystal, the book of her works on the lid.',
             'orc': 'The warlord sits on his bier of stones, a great blade across his knees.',
             'goblin': 'The boss lies buried in what he stole: pots, rings, a crown, a dented helm.',
             'kobold': 'The old hoardmaster lies on his coin, curled up like he is still guarding it.',
             'gnoll': 'The great packlord lies on a bed of bones, his teeth still bared.',
             'lizard': 'The elder lies in a stone coffin on the island, beside the stone egg.'}


# ------------------------------------------------------------------ outside, on its own land
def site_map(game, site):
    pe = PL.people_of(site)
    m = PL.land(game, site, 80, 50)
    cx, cy = m.centre
    cx = max(20, min(m.w - 20, cx))
    cy = max(14, min(m.h - 14, cy))
    PL.clear(m, cx - 18, cy - 12, cx + 18, cy + 12)
    import math
    from .temples import oval
    door = (cx - 8, cy)
    if pe in ('human', 'halfling', 'goblin', 'gnoll'):
        rx, ry = {'human': (11, 6), 'halfling': (7, 4), 'goblin': (9, 6), 'gnoll': (9, 5)}[pe]
        fill = {'gnoll': D.BONES, 'goblin': ROCK}.get(pe, D.SLOPE)
        for x, y in oval(cx, cy, rx, ry):
            m.set(x, y, fill if pe != 'gnoll' or (x + y) % 3 else D.SLOPE)
        door = (cx - rx, cy)
        for x in range(cx - rx, cx - rx + 3):
            m.set(x, cy, FLOOR if x > cx - rx else D.DOWN)
            if pe in ('human', 'halfling'):
                for y in (cy - 1, cy + 1):
                    m.set(x, y, D.EARTH)
        m.set(cx - rx, cy, D.DOWN)
        if pe == 'human':
            for k in range(14):                                       # the ring of standing stones
                a = k / 14 * math.tau
                m.set(round(cx + math.cos(a) * (rx + 4)), round(cy + math.sin(a) * (ry + 3)), D.STONE)
        if pe == 'halfling':
            for x, y in oval(cx - rx - 3, cy, 2, 1):
                m.set(x, y, D.FIELD)                                  # flowers laid every year
    elif pe == 'elf':
        for x, y in oval(cx, cy, 3, 2):
            m.set(x, y, D.TRUNK)
        for k in range(9):
            a = k / 9 * math.tau
            for r in (4, 5, 6):
                x, y = round(cx + math.cos(a) * r), round(cy + math.sin(a) * r * .6)
                if random.random() < .7:
                    m.set(x, y, D.ROOT)
        door = (cx - 4, cy)
        m.set(*door, D.DOWN)
        m.set(cx - 5, cy, FLOOR)
    elif pe == 'dwarf':
        for y in range(0, m.h):
            for x in range(cx + 2, m.w):
                if abs(y - cy) < 14 or x > cx + 6:
                    m.set(x, y, ROCK)
        door = (cx + 2, cy)
        m.set(*door, D.DOWN)
        m.set(cx + 1, cy - 1, D.STATUE)
        m.set(cx + 1, cy + 1, D.STATUE)
    elif pe == 'gnome':
        for x, y in oval(cx, cy, 4, 3):
            if random.random() < .6:
                m.set(x, y, D.CRYSTAL)
        door = (cx - 4, cy)
        m.set(*door, D.DOWN)
        m.glows = [(cx, cy, (120, 230, 255), 4)]
        m.lights = list(m.glows)
    elif pe == 'orc':
        for x, y in oval(cx, cy, 6, 4):
            m.set(x, y, D.RUBBLE)
        door = (cx - 6, cy)
        m.set(*door, D.DOWN)
        for x in range(cx - 16, cx - 7, 3):
            m.set(x, cy - 2, D.TOTEM)
            m.set(x, cy + 2, D.TOTEM)
    elif pe == 'kobold':
        for x, y in oval(cx, cy, 4, 3):
            m.set(x, y, D.RUBBLE)
        for x, y in oval(cx, cy, 2, 1):
            m.set(x, y, FLOOR)
        door = (cx, cy)
        m.set(*door, D.DOWN)
        m.set(cx - 2, cy, FLOOR)
        m.set(cx - 3, cy, FLOOR)
        m.set(cx - 4, cy, FLOOR)
        m.set(cx + 1, cy - 1, D.GLITTER)
    elif pe == 'lizard':
        for x, y in oval(cx, cy, 13, 8):
            m.set(x, y, D.SHALLOW)
        for x, y in oval(cx, cy, 10, 6):
            m.set(x, y, D.WATER)
        for x, y in oval(cx, cy, 2, 1):
            m.set(x, y, FLOOR)
        m.set(cx, cy - 1, D.STATUE)
        door = (cx + 1, cy)
        m.set(*door, D.DOWN)
        for x in range(cx - 13, cx - 1):                            # a sunken causeway to wade along
            m.set(x, cy, D.SHALLOW)
    PL.finish(m, (door[0], door[1]))
    m.place = 'barrow'
    return m


# ------------------------------------------------------------------ inside
def level(game, dg, depth):
    """The barrow itself, under its mound: built after its people's way."""
    site = game.world.sites[dg.site]
    pe = PL.people_of(site)
    w, h = 80, 50
    m = GameMap(f'{dg.id}:{depth}', 'dungeon', site.name, w, h, ROCK)
    m.did, m.depth, m.level, m.radius, m.wall_fg = dg.id, depth, dg.base + depth, 7, dg.wall
    m.dtag, m.last = 'barrow', depth == dg.depth
    m.barrow, m.built = pe, pe not in ('orc', 'goblin', 'gnoll')
    m.lights, m.deco, m.mons, m.items = [], bytearray(w * h), [], []
    wall = D.ROOT if pe == 'elf' else WALL
    cy = h // 2
    up = (6, cy)

    def box(x0, y0, x1, y1):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                edge = y in (y0, y1) or x in (x0, x1)
                if edge and m.tile(x, y) == ROCK:
                    m.set(x, y, wall)
                elif not edge:
                    m.set(x, y, FLOOR)

    def corridor(a, b, wide=1):
        x, y = a
        cells = [(x, y)]
        while (x, y) != b:
            if x != b[0]:
                x += (b[0] > x) - (b[0] < x)
            else:
                y += (b[1] > y) - (b[1] < y)
            cells.append((x, y))
        for x, y in cells:
            for k in range(wide):
                yy = y + k
                m.set(x, yy, FLOOR)
                for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                    if m.inb(x + dx, yy + dy) and m.tile(x + dx, yy + dy) == ROCK:
                        m.set(x + dx, yy + dy, wall)
        return cells
    turns = []
    if pe == 'goblin':                                              # a zigzag way, a trap at every turn
        pts = [up, (14, cy), (14, cy - 8), (22, cy - 8), (22, cy + 6), (30, cy + 6), (30, cy)]
        for a, b in zip(pts, pts[1:]):
            corridor(a, b)
        turns = pts[1:-1]
        passage = []
        ante_x = 30
    else:
        passage = corridor(up, (28, cy), 1 if pe in ('halfling', 'kobold') else 2 if pe in ('dwarf', 'human') else 1)
        ante_x = 28
    box(ante_x, cy - 6, ante_x + 12, cy + 6)                          # the antechamber of grave goods
    for y in range(cy - 1, cy + 2):
        m.set(ante_x, y, FLOOR)
    corridor((ante_x + 12, cy), (48, cy))
    tomb = (48, cy - 8, 64, cy + 8)
    box(*tomb)                                                       # the burial chamber
    m.set(48, cy, DOOR if pe not in ('orc', 'gnoll', 'lizard') else FLOOR)
    bier = (57, cy)
    sides = []
    for k, (sx, sy) in enumerate(((ante_x + 2, cy - 13), (ante_x + 2, cy + 8), (16, cy - 9), (16, cy + 4))):
        if (pe == 'halfling' and k > 1) or pe == 'goblin':
            break
        box(sx, sy, sx + 7, sy + 5)
        dx = sx + 3
        if k < 2:
            corridor((dx, cy - 6 if sy < cy else cy + 6), (dx, sy + 5 if sy < cy else sy))
        else:
            corridor((dx, cy - 1 if sy < cy else cy + 2), (dx, sy + 5 if sy < cy else sy))
        sides.append((sx, sy))
        for x in range(sx + 1, sx + 7):                              # the bone niches
            for y in (sy + 1, sy + 4):
                if random.random() < .55 and (x, y) != (dx, sy + 1 if sy > cy else sy + 4):
                    m.set(x, y, D.BONES)
    m.set(*up, UP)
    # the one thing per people
    if pe == 'human' or pe == 'dwarf':
        for x in range(9, 27, 3):
            for y in (cy - 1, cy + 2):
                if m.tile(x, y) == wall:
                    m.set(x, y, D.STONE)                             # stones lining the passage
    if pe == 'dwarf':
        for x in range(50, 64, 3):
            m.set(x, cy - 6, D.STATUE)                               # the stone kings
            m.set(x, cy + 6, D.STATUE)
        m.set(10, cy, DOOR)                                          # the rune door
        traps = [(14, cy), (20, cy + 1), (24, cy)]
    elif pe == 'gnome':
        for x in range(50, 64, 2):
            m.set(x, cy - 7, D.CRYSTAL)
            m.set(x, cy + 7, D.CRYSTAL)
        traps = [(11, cy), (17, cy), (23, cy)]
    elif pe == 'goblin':
        traps = turns
    else:
        traps = []
    if pe == 'orc':
        for x in range(10, 27, 4):
            m.set(x, cy - 1, D.TOTEM)
            m.set(x, cy + 1, D.TOTEM)
    if pe == 'gnoll':
        for _ in range(40):
            x, y = random.randint(49, 63), random.randint(cy - 7, cy + 7)
            if cheb(x, y, *bier) > 2:
                m.set(x, y, D.BONES)
    if pe == 'elf':
        m.set(bier[0], bier[1] - 1, D.TREE)                          # the sapling from the eldest's breast
        for x in range(51, 63, 3):
            m.set(x, cy - 5, D.BIER)
            m.set(x, cy + 5, D.BIER)
        m.glows = [(x, cy, (200, 220, 255), 3) for x in (40, 52, 60)]
    if pe == 'lizard':
        for y in range(cy - 7, cy + 8):
            for x in range(49, 64):
                if cheb(x, y, *bier) > 2:
                    m.set(x, y, D.WATER if cheb(x, y, *bier) > 4 else D.SHALLOW)
        for x, y in ((51, cy - 5), (62, cy - 5), (51, cy + 5), (62, cy + 5)):
            m.set(x, y, D.BIER)                                      # stone coffins sunk in the pool
        m.set(bier[0] + 1, bier[1], D.STATUE)                        # the stone egg
        for x in range(49, 54):
            m.set(x, cy, D.SHALLOW)
    if pe == 'kobold':
        for _ in range(16):
            x, y = random.randint(49, 63), random.randint(cy - 7, cy + 7)
            if cheb(x, y, *bier) > 1 and m.tile(x, y) == FLOOR:
                m.set(x, y, D.GLITTER)
    m.set(*bier, D.BIER)
    m.bier = bier
    from . import behave as BH
    for c in traps:
        if m.tile(*c) == FLOOR:
            BH.traps(m)[c] = max(3, m.level * 2)
            m.__dict__.setdefault('trap_kind', {})[c] = 'plate'
    if pe == 'goblin':                                               # the false tomb, and the real one behind a wall
        box(36, cy - 16, 46, cy - 10)
        corridor((40, cy - 6), (40, cy - 10))
        m.set(41, cy - 13, D.BIER)
        m.false_bier = (41, cy - 13)
        m.set(48, cy, D.SECRET)
    # grave goods in the antechamber
    for _ in range(3):
        x, y = random.randint(ante_x + 2, ante_x + 10), random.choice((cy - 5, cy + 5))
        if m.tile(x, y) == FLOOR:
            m.set(x, y, D.BARREL)
    from .worldgen import place_chest
    place_chest(m)
    from .money import purse
    for _ in range(2):
        x, y = random.randint(ante_x + 2, ante_x + 10), random.randint(cy - 4, cy + 4)
        if m.tile(x, y) == FLOOR:
            it = Item(game.new_id(), 'gold', 'gold', purse(m.level, 1.5))
            it.x, it.y = x, y
            m.items.append(it)
    # the dead who sleep in the niches
    n = 0 if pe == 'halfling' else random.randint(3, 5)
    rooms = [(sx + 1 + random.randint(0, 5), sy + 2 + random.randint(0, 1)) for sx, sy in sides] + \
            [(random.randint(ante_x + 2, ante_x + 10), random.randint(cy - 3, cy + 3)) for _ in range(2)]
    random.shuffle(rooms)
    for c in rooms[:n]:
        if m.tile(*c) == FLOOR:
            o = make_monster(game, choose_monster(m.level, 'barrow'), c[0], c[1], m.level)
            m.mons.append(o)
    if pe == 'halfling' and random.random() < .5:
        o = make_monster(game, 'ghost', 40, cy, m.level)
        m.mons.append(o)
    m.mood_line = INSIDE[pe]
    return m


def bump(game, x, y):
    """The bier: take from it and the dead wake. Returns turns, or None when (x, y) is not this barrow's bier."""
    from . import events as EV
    m = game.map
    t = m.tile(x, y)
    if t == D.SECRET:
        from .themes import found_door
        found_door(game, x, y)
        return 1
    if t != D.BIER:
        return None
    if (x, y) == getattr(m, 'false_bier', None):
        if getattr(m, 'false_taken', False):
            game.msg('The false tomb is empty now. Somewhere the real boss is laughing.')
            return 0
        EV.ask(game, 'barrow_bier', 'A tomb', 'A tomb heaped with pots and rings. It looks just like the tomb of a goblin boss.',
               [('Take from it', 'take'), ('Leave it', 'bye')], cell=(x, y), false=True)
        return 0
    if (x, y) != getattr(m, 'bier', None):
        game.msg('A stone coffin. Whoever lies here took nothing worth having.')
        return 0
    if getattr(m, 'bier_taken', False):
        game.msg('The bier is bare now. You took what lay on it.')
        return 0
    EV.ask(game, 'barrow_bier', 'The bier', BIER_TEXT.get(m.barrow, BIER_TEXT['human']),
           [('Take from the bier', 'take'), ('Leave the dead in peace', 'bye')], cell=(x, y))
    return 0


def r_bier(game, choice, ctx):
    from .money import purse
    from .entities import random_gear, make_tome
    if choice != 'take':
        if not ctx.get('false'):
            game.msg('You leave the dead in peace.', 'info')
        return
    m = game.map
    x, y = ctx['cell']
    lvl = m.level
    if ctx.get('false'):
        m.false_taken = True
        game.spill(m, x, y, Item(game.new_id(), 'gold', 'gold', purse(lvl, .6)))
        from .worldgen import free_around
        for c in [c for c in free_around(game, m, x, y, 2) if not game.occupied(m, *c)][:3]:
            o = make_monster(game, 'skeleton', c[0], c[1], lvl)
            o.awake = True
            m.mons.append(o)
        game.msg('Junk and a few coins, and the bones round the tomb get up! This was never the boss.', 'bad')
        return
    m.bier_taken = True
    pe = m.barrow
    dg = game.world.dungeons.get(m.did)
    if dg is not None and getattr(dg, 'site', None) is not None:
        from . import aurora as AU
        AU.wake(game, game.world.sites[dg.site], 'Far above, out on the mound, a cold light flares: the spirit of the barrow '
                'knows what you have done.')
    game.spill(m, x, y, Item(game.new_id(), 'gold', 'gold', purse(lvl, 6 if pe in ('kobold', 'dwarf') else 3)))
    game.spill(m, x, y, random_gear(game, lvl + 2, 2.0))
    if pe == 'gnome':
        game.spill(m, x, y, make_tome(game, lvl + 2))
    if pe == 'kobold':
        game.msg('You scoop up the coin. The floor groans, cracks, and gives way under you!', 'bad')
        _fall_through(game)
        return
    key, title = KING.get(pe, KING['human'])
    if key not in D.MONSTERS:
        key = 'wight'
    from .worldgen import free_around
    spot = next((c for c in free_around(game, m, x, y, 2) if not game.occupied(m, *c)), None)
    if spot:
        o = make_monster(game, key, spot[0], spot[1], lvl + 2, 2)
        o.name, o.fg = title, D.UNIQUE_FG
        o.hp = o.maxhp = round(o.maxhp * 1.5)
        o.awake = True
        m.mons.append(o)
    for o in m.mons:
        if not o.is_npc:
            o.awake = True
    game.shake()
    game.msg({'halfling': 'A sigh fills the tomb. Grandmother rises, weeping, and she is angry.',
              'lizard': 'The water stirs. Something climbs out of the coffin beside the egg.'}.get(
        pe, f'The dead wake! {title} rises from the bier, and the barrow stirs with it.'), 'bad')


def _fall_through(game):
    """The kobolds' loose floor: down into the old shaft, the level below."""
    m = game.map
    dg = game.world.dungeons[m.did]
    if m.depth >= dg.depth:
        return
    game.enter_dungeon(dg.id, m.depth + 1, 'up')
    from .worldgen import rand_free
    c = rand_free(game, game.map, lambda t: t == FLOOR)
    if c:
        game.player.x, game.player.y = c
    game.hurt(max(3, game.stats()['max_life'] // 10), 'a fall into the old shaft')
    game.compute_fov()


def on_level(game, m, dg, depth):
    from . import aurora as AU
    AU.on_level(game, m, dg)
    if depth == 1 and getattr(m, 'mood_line', None):
        game.msg(m.mood_line, 'info')
    elif depth > 1:
        game.msg('An older grave, under the barrow: whoever lies here was buried long before the mound was raised.', 'info')


from . import events as _EV                             # noqa: E402
_EV.RESOLVERS['barrow_bier'] = r_bier
