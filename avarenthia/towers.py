"""Towers (round 6): slender and high, every floor the same small footprint, about 15 across, 3 to 6 storeys.

The ground floor stands on the place's own map (places.py); every floor above is a level of its own, a map the size
of the ground map with the tower in the same spot and empty air (D.AIR) all round. A stair or ladder comes out where
it left from below; the next one up lies elsewhere, in a stone tower a quarter turn further round, like a spiral.
The top is a lookout: standing there marks the land round about on the world map.

Up high you see it: round the tower the ground map is drawn faded in a blue-grey haze, the paler the higher you are,
with the tower's shadow across it, birds wheeling below and now and then a wisp of cloud. Arrow slits show the same
when you stand beside one. Each people builds its own; a fallen tower has lost one side, and a true ruin is a stump.

Edges and falls: stepping off asks first, with how far down it is. A knockback or a shove can throw you, or a foe,
over the edge; a fall hurts by the number of floors, and you land on what lies below."""
import math
import random

from . import data as D
from .data import FLOOR, WALL, DOOR, UP, DOWN, AIR, PLANK
from .entities import GameMap, make_monster, make_npc
from .worldgen import cheb

HAZE = (132, 150, 172)              # the blue-grey of the air between you and the ground
HAZE_BG = (24, 30, 42)
BIRD = (40, 44, 52)

# each people's tower: its outline, walls and floors, ladders or stairs, how it splits into rooms, the top
STYLE = {
    'human': dict(shape=('disc', 7.5), wall=WALL, fg=(186, 182, 172), floor=FLOOR, ladder=False, split='across',
                  slits=True, rim=D.PARAPET, marks=(D.FIREPIT,), uses=('guard room', 'barracks', 'mess', 'store',
                                                                        "the keeper's room"),
                  name='a round tower of grey stone'),
    'elf': dict(shape=('wobble', 7.4), wall=WALL, fg=(222, 234, 216), floor=FLOOR, ladder=False, split=None, trunk=True,
                slits=True, rim=D.HEDGE, marks=(), uses=('hall of songs', 'store', 'sleeping loft', "the keeper's room"),
                name='a tower of white stone round a living trunk'),
    'dwarf': dict(shape=('square', 7, 3), wall=WALL, fg=(156, 136, 112), floor=FLOOR, ladder=False, split='down',
                  slits=True, rim=D.PARAPET, marks=(D.BOLTS, D.FIREPIT), uses=('forge', 'store', 'guard room', 'barracks'),
                  name='a square tower of hewn blocks'),
    'orc': dict(shape=('square', 6, 0), wall=D.PALISADE, fg=None, floor=PLANK, ladder=True, split=None, slits=False,
                rim=D.STAKES, marks=(D.DRUM, D.TOTEM), uses=('sleeping floor', 'store', 'trophy floor'),
                name='a tower of rough logs'),
    'goblin': dict(shape=('crooked', 6.4), wall=WALL, fg=(136, 124, 92), floor=PLANK, ladder=True, split=None, holes=True,
                   slits=False, rim=D.PARAPET, marks=(D.GONG,), uses=('junk floor', 'sleeping floor', 'store'),
                   name='a crooked tower of scrap and planks'),
    'kobold': dict(shape=('disc', 5.4), wall=WALL, fg=(158, 132, 104), floor=FLOOR, ladder=True, split=None, slits=False,
                   rim=D.PARAPET, marks=(D.MIRROR,), uses=('hoard room', 'sleeping floor', 'store'),
                   name='a narrow spire of piled stone with shiny bits in its walls'),
    'gnoll': dict(shape=('square', 6, 1), wall=D.HIDE, fg=None, floor=PLANK, ladder=True, split=None, slits=False,
                  rim=D.FENCE, gaps=True, marks=(D.HORN,), uses=('bone floor', 'sleeping floor'),
                  name='a tower of poles and hides lashed together'),
    'lizard': dict(shape=('disc', 6.2), wall=D.REEDS, fg=None, floor=PLANK, ladder=True, split=None, slits=False,
                   rim=D.FENCE, stilts=True, marks=(D.FIREPIT,), uses=('egg nest', 'sleeping floor', 'store'),
                   name='a tower of woven reeds on stilts over the swamp'),
    # a human temple's bell tower, and the eldest tree of an elven temple with its stair up into the crown
    'bell': dict(shape=('square', 2, 0), wall=WALL, fg=(186, 182, 172), floor=FLOOR, ladder=False, split=None, small=True,
                 slits=True, rim=D.PARAPET, marks=(D.BELL,), uses=('ringing loft', 'store'), name='a bell tower'),
    'elftree': dict(shape=('disc', 4.6), wall=D.TRUNK, fg=None, floor=PLANK, ladder=False, split=None, small=True,
                    slits=False, rim=D.HEDGE, marks=(), uses=('crown',), name='the eldest tree'),
}
STONE = {'human', 'elf', 'dwarf', 'kobold'}
USES = {
    'guard room': ((D.RACK, D.TABLE), 'The guard room. Spears stand in a rack by the table.'),
    'barracks': ((D.BED, D.BED, D.BED), 'The barracks. Bunks stand close along the curve of the wall.'),
    'mess': ((D.TABLE, D.TABLE, D.BARREL), 'The mess. A long table, and the smell of old stew.'),
    'store': ((D.BARREL, D.BARREL, D.CHEST), 'The store. Barrels and sacks are stacked against the wall.'),
    "the keeper's room": ((D.BED, D.TABLE, D.SHELVES), "The keeper's room: a bed, a table, a shelf of logbooks."),
    'hall of songs': ((D.STONE,), 'A hall of songs. The living wood hums faintly round the trunk.'),
    'sleeping loft': ((D.BED, D.BED), 'A sleeping loft, open to the leaves.'),
    'forge': ((D.ANVIL, D.FIREPIT), 'The forge floor. The anvil is warm, the bellows patched.'),
    'sleeping floor': ((D.FURS, D.FURS), 'A sleeping floor, furs heaped against the walls.'),
    'trophy floor': ((D.TOTEM, D.BONES), 'A floor of trophies: skulls on poles, and the bones of what they ate.'),
    'junk floor': ((D.BARREL, D.MIDDEN), 'Junk is piled everywhere. Watch where you put your feet.'),
    'hoard room': ((D.GLITTER, D.GLITTER, D.CHEST), 'The hoard room. Bits of metal and glass gleam in heaps.'),
    'bone floor': ((D.BONES, D.BONES), 'Bones lie everywhere, gnawed white.'),
    'egg nest': ((D.EGGS,), 'The egg nest. The air is warm and damp.'),
    'ringing loft': ((), 'The ringing loft. Bell ropes hang down through holes in the boards.'),
    'crown': ((), 'Up among the great branches. Leaves whisper all round you.'),
}
TOP_LINE = {'human': 'The battlements. A brazier burns in the middle of the roof.',
            'elf': 'The crown of leaves, open to the stars.',
            'dwarf': 'The roof: a bolt thrower and a beacon, ready to be lit.',
            'orc': 'The top, under a roof of hides. A war drum stands by the edge.',
            'goblin': "A crow's nest of planks. A gong hangs from a pole.",
            'kobold': 'The top of the spire. A polished shield flashes in the light.',
            'gnoll': 'An open platform on the poles, and a horn of bone.',
            'lizard': 'A platform of reeds over the water. A smoke fire smoulders on a stone.',
            'bell': 'The bell chamber, open on all sides. The great bell hangs in the middle.',
            'elftree': 'The crown of the eldest tree. Through the leaves the land lies far below.'}
WATCH = {'human': ('soldier', 'A tower guard'), 'elf': ('warden', 'An elven warden'), 'dwarf': ('clansman', 'A dwarf guard')}
FOES = {'orc': ('orc', 'orc_spear', 'orc_berserker'), 'goblin': ('goblin', 'gobarcher', 'gob_sneak'),
        'kobold': ('kobold', 'kob_slinger', 'kob_trapper'), 'gnoll': ('gnoll_hunter', 'hyena'),
        'lizard': ('lizard_warrior', 'lizard_spear'), 'human': ('soldier', 'crossbow'), 'elf': ('warden',),
        'dwarf': ('clansman', 'thunderer'), 'bandits': ('bandit', 'brigand'), 'beast': ('giant_hawk', 'wyvern')}
CHIEF = {'orc': 'orc_chief', 'goblin': 'gob_boss', 'kobold': 'kob_chief', 'gnoll': 'gnoll_packlord', 'lizard': 'lizard_shaman',
         'bandits': 'robber_knight'}


# ------------------------------------------------------------------ the shape
def footprint(tw):
    """The cells of the tower's outline, the same on every floor."""
    st = STYLE[tw['people']]
    kind = st['shape'][0]
    cx, cy = tw['cx'], tw['cy']
    rnd = random.Random(tw['seed'])
    bumps = [rnd.uniform(-1.3, .9) for _ in range(12)]
    out = set()
    for y in range(cy - 9, cy + 10):
        for x in range(cx - 9, cx + 10):
            dx, dy = x - cx, y - cy
            a = math.atan2(dy, dx)
            if kind == 'disc':
                ok = math.hypot(dx, dy) < st['shape'][1]
            elif kind == 'wobble':
                ok = math.hypot(dx, dy) < st['shape'][1] + .7 * math.cos(3 * a)
            elif kind == 'crooked':
                t = (a + math.pi) / (2 * math.pi) * 12
                i, u = int(t) % 12, t - int(t)
                ok = math.hypot(dx, dy) < st['shape'][1] + bumps[i] * (1 - u) + bumps[(i + 1) % 12] * u
            else:
                h, cut = st['shape'][1], st['shape'][2]
                ok = max(abs(dx), abs(dy)) <= h and (h - abs(dx)) + (h - abs(dy)) >= cut
            if ok:
                out.add((x, y))
    return out


def rim_of(cells):
    return {(x, y) for x, y in cells if any((x + dx, y + dy) not in cells for dx in (-1, 0, 1) for dy in (-1, 0, 1))}


def ring(tw, cells):
    """Where a stair may stand: inside, against the wall (or round the trunk), in order round the tower."""
    cx, cy = tw['cx'], tw['cy']
    wall = rim_of(cells)
    inner = cells - wall
    if STYLE[tw['people']].get('trunk'):
        opts = [(x, y) for x, y in inner if cheb(x, y, cx, cy) == 2]
    else:
        near = 1 if STYLE[tw['people']].get('small') else 2
        opts = [(x, y) for x, y in inner if any((x + dx, y + dy) in wall for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                and cheb(x, y, cx, cy) >= near]
    return sorted(opts, key=lambda c: math.atan2(c[1] - cy, c[0] - cx))


def plan(site, cx, cy, people, storeys, state='whole', seed=None):
    """Lay out a tower on a site: where it stands and where every stair goes. Kept on the site (site.tw)."""
    tw = dict(cx=cx, cy=cy, people=people, storeys=storeys, state=state, seed=seed if seed is not None else random.getrandbits(30))
    cells = footprint(tw)
    opts = ring(tw, cells)
    rnd = random.Random(tw['seed'] + 1)
    if state == 'half':                     # the fallen side: everything keeps to the side that still stands
        a = rnd.uniform(0, 2 * math.pi)
        tw['fall'] = (math.cos(a), math.sin(a))
        fx, fy = tw['fall']
        opts = [c for c in opts if (c[0] - cx) * fx + (c[1] - cy) * fy < -1.5] or opts
    n = storeys if state != 'ruin' else 2
    stairs = []
    if STYLE[people]['ladder'] or state == 'half':
        last = None
        for _k in range(n - 1):
            pool = [c for c in opts if last is None or cheb(c[0], c[1], *last) >= 4] or opts
            last = rnd.choice(pool)
            stairs.append(last)
    else:
        a0 = rnd.uniform(-math.pi, math.pi)
        for k in range(n - 1):
            a = a0 + k * math.pi / 2
            stairs.append(min(opts, key=lambda c: abs(math.remainder(math.atan2(c[1] - cy, c[0] - cx) - a, 2 * math.pi))))
    tw['stairs'] = stairs
    return tw


# ------------------------------------------------------------------ the ground floor, on the place's own map
def ground(game, site, m, tw, friendly):
    """Build the ground floor on map m. Returns the door cell."""
    st = STYLE[tw['people']]
    cells = footprint(tw)
    wall = rim_of(cells)
    cx, cy = tw['cx'], tw['cy']
    for x, y in cells:
        m.set(x, y, st['wall'] if (x, y) in wall else st['floor'])
    if st.get('stilts'):                    # reeds on stilts: below the floor only poles in the water
        for x, y in cells:
            m.set(x, y, D.SHALLOW)
        for x, y in wall:
            if (x + y) % 3 == 0:
                m.set(x, y, D.STILT)
    if st.get('trunk'):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                m.set(cx + dx, cy + dy, D.TRUNK)
    door = min((c for c in wall if abs(c[1] - cy) <= 1), key=lambda c: (c[0], abs(c[1] - cy)))
    if not st.get('stilts'):
        m.set(door[0], door[1], DOOR)
    up = tw['stairs'][0] if tw['stairs'] else None
    if up:
        m.set(up[0], up[1], UP)
    if tw.get('cellar'):
        hatch = _spot(m, cells - wall, avoid=[up, door], st=st)
        if hatch:
            m.set(hatch[0], hatch[1], DOWN)
    if tw['state'] == 'half':
        _fallen_foot(m, tw, cells, wall)
    elif tw['state'] == 'ruin':
        _stump(m, tw, cells, wall, up)
    m.tower_door = door
    return door


def _spot(m, cells, avoid=(), st=None):
    opts = [c for c in cells if m.tile(*c) in (FLOOR, PLANK, D.SHALLOW) and all(a is None or cheb(c[0], c[1], *a) >= 2 for a in avoid)]
    return random.choice(opts) if opts else None


def _fallen_foot(m, tw, cells, wall):
    """Half fallen: its stones lie in a heap round the foot on the fallen side, and a few fell in through the roof."""
    fx, fy = tw['fall']
    cx, cy = tw['cx'], tw['cy']
    for y in range(cy - 14, cy + 15):
        for x in range(cx - 14, cx + 15):
            if not m.inb(x, y) or (x, y) in cells:
                continue
            d = (x - cx) * fx + (y - cy) * fy
            side = abs((x - cx) * -fy + (y - cy) * fx)
            if d > 6 and d < 14 and side < 6 and random.random() < .5 - (d - 6) * .05 and D.TILES[m.tile(x, y)].walk:
                m.set(x, y, D.RUBBLE)
    inner = list(cells - wall)
    for x, y in random.sample(inner, min(len(inner), 6)):
        if m.tile(x, y) in (FLOOR, PLANK):
            m.set(x, y, D.RUBBLE)


def _stump(m, tw, cells, wall, up):
    """A true ruin: only a stump of wall stands, ivy on it, rubble and grass inside."""
    for x, y in wall:
        if m.tile(x, y) == DOOR:
            m.set(x, y, D.GRASS)
        elif random.random() < .45:
            m.set(x, y, D.IVY)
        elif random.random() < .5:
            m.set(x, y, D.RUBBLE)
        else:
            m.set(x, y, D.GRASS)
    for x, y in cells - wall:
        if m.tile(x, y) in (FLOOR, PLANK):
            m.set(x, y, D.RUBBLE if random.random() < .2 else D.GRASS)


# ------------------------------------------------------------------ the floors above (levels of their own)
def floor_map(game, dg, depth):
    """Floor `depth` above the ground of the tower dg belongs to."""
    site = game.world.sites[dg.site]
    tw = site.tw
    st = STYLE[tw['people']]
    gm = game.maps[site.map_key]
    m = GameMap(f'{dg.id}:{depth}', 'dungeon', site.name, gm.w, gm.h, AIR)
    m.did, m.depth, m.level, m.wall_fg = dg.id, depth, dg.base + depth, st['fg']
    m.radius, m.sky, m.built = 30, site.id, True
    m.sky_centre = (tw['cx'], tw['cy'])
    m.below = site.map_key if depth == 1 else f'{dg.id}:{depth - 1}'
    m.lights, m.deco, m.mons, m.items = [], bytearray(m.w * m.h), [], []
    m.ladders = st['ladder']
    m.dtag = 'tower'
    top = depth == dg.depth
    cells = footprint(tw)
    wall = rim_of(cells)
    cx, cy = tw['cx'], tw['cy']
    ruin = tw['state'] == 'ruin'
    for x, y in cells:
        m.set(x, y, (st['rim'] if top else st['wall']) if (x, y) in wall else st['floor'])
    if top and st.get('gaps'):
        for x, y in wall:
            if (x * 7 + y * 3) % 5 == 0:
                m.set(x, y, st['floor'])     # an open platform: here and there no rail at all
    if st.get('trunk'):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                m.set(cx + dx, cy + dy, D.TRUNK)
    if not top and st['slits']:
        for x, y in wall:
            if (x * 5 + y * 11 + depth) % 6 == 0 and _outer(cells, x, y):
                m.set(x, y, D.SLIT)
    down = tw['stairs'][depth - 1]
    up = tw['stairs'][depth] if not top and depth < len(tw['stairs']) else None
    m.set(down[0], down[1], DOWN)
    if up:
        m.set(up[0], up[1], UP)
    if tw['state'] == 'half':
        _cut(m, tw, cells, depth, (down, up))
    if ruin:
        _ledge(m, tw, cells, down)
    if st.get('holes') and not top:
        inner = [c for c in cells - wall if m.tile(*c) == st['floor'] and cheb(c[0], c[1], *down) > 2
                 and (up is None or cheb(c[0], c[1], *up) > 2)]
        for x, y in random.sample(inner, min(len(inner), random.randint(1, 2))):
            m.set(x, y, AIR)                    # a hole in the floor: the floor below shows through it
    use = None
    if top:
        m.mood_line = TOP_LINE[tw['people']] if not ruin else 'A last broken ledge. The wind pulls at you.'
        if not ruin and tw['state'] != 'half':
            marks = list(st['marks'])
            if tw.get('bell'):
                marks = [D.BELL]
            spots = sorted((c for c in cells - wall if m.tile(*c) == st['floor'] and cheb(c[0], c[1], *down) > 1),
                           key=lambda c: cheb(c[0], c[1], cx, cy))
            for k, t in enumerate(marks):
                if k < len(spots):
                    m.set(spots[k * 3 % max(1, len(spots))][0], spots[k * 3 % max(1, len(spots))][1], t)
    elif not ruin:
        use = st['uses'][(depth - 1) % len(st['uses'])]
        _furnish(m, cells, wall, use, (down, up), st)
        m.mood_line = USES[use][1]
    _connect(m, down, up, st)
    for i, t in enumerate(m.t):
        if t == AIR:
            m.seen[i] = 1                       # the land below is always there to see
    people(game, m, site, tw, dg, depth, top, use, (down, up))
    return m


def _outer(cells, x, y):
    return any((x + dx, y + dy) not in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))


def _cut(m, tw, cells, depth, keep):
    """Half fallen: higher up, more of each floor is gone, and you stand at a broken edge."""
    fx, fy = tw['fall']
    cx, cy = tw['cx'], tw['cy']
    k = 1.5 - depth * .6
    for x, y in cells:
        d = (x - cx) * fx + (y - cy) * fy + random.uniform(-.8, .8)
        if d > k and (x, y) not in keep:
            m.set(x, y, AIR)
    for x, y in cells:
        if m.tile(x, y) in (FLOOR, PLANK) and any(m.inb(x + dx, y + dy) and m.tile(x + dx, y + dy) == AIR
                                                 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))) and random.random() < .25:
            m.set(x, y, D.RUBBLE)


def _ledge(m, tw, cells, down):
    """A true ruin: the stair ends at a last broken ledge."""
    keep = {c for c in cells if cheb(c[0], c[1], *down) <= 1}
    for x, y in cells:
        if (x, y) not in keep:
            m.set(x, y, AIR)
    for x, y in keep:
        if m.tile(x, y) not in (DOWN,):
            m.set(x, y, FLOOR if random.random() < .7 else D.RUBBLE)
    for x, y in keep:
        if (x, y) != down and m.tile(x, y) == D.RUBBLE and random.random() < .5:
            m.set(x, y, FLOOR)


def _furnish(m, cells, wall, use, keep, st):
    """Split the floor if this people does, and put the floor's things against the wall."""
    cx, cy = (sum(c[0] for c in cells) // len(cells), sum(c[1] for c in cells) // len(cells))
    inner = cells - wall
    if st['split']:
        line = [(x, cy) for x, y in inner if y == cy] if st['split'] == 'across' else [(cx - 1, y) for x, y in inner if x == cx - 1]
        line = sorted(set(line))
        if line and not any(k is not None and c == k for c in line for k in keep):
            for x, y in line:
                m.set(x, y, st['wall'])
            mid = line[len(line) // 2]
            m.set(mid[0], mid[1], DOOR)
    things = list(USES[use][0])
    opts = [c for c in inner if m.tile(*c) == st['floor'] and any((c[0] + dx, c[1] + dy) in wall for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            and all(k is None or cheb(c[0], c[1], *k) >= 2 for k in keep)]
    random.shuffle(opts)
    for t, c in zip(things, opts):
        m.set(c[0], c[1], t)


def _connect(m, a, b, st):
    """Whatever was set down, the stairs still join: clear anything in the way."""
    if b is None:
        return
    from .worldgen import bfs
    d = bfs(m, a[0], a[1], lambda t: D.TILES[t].walk or D.TILES[t].door)
    if d[b[1] * m.w + b[0]] >= 0:
        return
    x, y = a
    while (x, y) != b:
        x += (b[0] > x) - (b[0] < x)
        y += (b[1] > y) - (b[1] < y)
        if (x, y) != b and not D.TILES[m.tile(x, y)].walk and m.tile(x, y) not in (D.TRUNK,):
            m.set(x, y, st['floor'])


def people(game, m, site, tw, dg, depth, top, use, keep):
    """Who is up here: the tower's own people where it is manned, a few strong foes where it is not."""
    from . import places as PL
    hold = getattr(site, 'holder', None) or tw['people']
    free = [i for i, t in enumerate(m.t) if t in (FLOOR, PLANK) and all(k is None or cheb(i % m.w, i // m.w, *k) >= 2 for k in keep)]
    random.shuffle(free)
    lvl = m.level
    if PL.friendly(game, site):
        if hold in WATCH and free:
            k = free.pop()
            if top:
                n = make_npc(game, f'Captain {PL.a_name(hold)}', 'tower', '#e8e0c0', k % m.w, k // m.w, True)
            else:
                n = make_npc(game, WATCH[hold][1], 'guard', '#c8c4b4', k % m.w, k // m.w, True)
            m.mons.append(n)
        return
    if hold == 'beast' and not top:
        return
    if hold == 'cellar':
        return
    n = 1 + (top or random.random() < .4)
    if tw['state'] == 'ruin':
        n = 1 if hold == 'beast' else 0
    foes = FOES.get(hold) or FOES.get(tw['people']) or ('bandit',)
    awake = getattr(site, 'alarm', -1) >= game.day
    for j in range(n):
        if not free:
            break
        k = free.pop()
        key = CHIEF.get(hold) if top and j == 0 and hold in CHIEF else random.choice(foes)
        if key not in D.MONSTERS:
            key = foes[0]
        o = make_monster(game, key, k % m.w, k // m.w, lvl + (1 if top else 0), 1 if top and j == 0 else 0)
        o.awake = awake
        m.mons.append(o)


# ------------------------------------------------------------------ up high you see it
_SHADOW = {}


def shadow(game, gm, tw, height):
    """The cells of the ground the tower's shadow falls on now: west in the morning, east in the afternoon."""
    from .towns import hour
    h = hour(game)
    key = (gm.key, tw['cx'], tw['cy'], height, h // 2)
    got = _SHADOW.get(key)
    if got is not None:
        return got
    if len(_SHADOW) > 40:
        _SHADOW.clear()
    out = set()
    if 6 <= h < 19:
        k = (h - 12.5) / 6.5                 # -1 at dawn, 1 at dusk
        dx, dy = -k, -.35                    # the sun goes round the south: the shadow leans north
        n = max(1, height) * 3 + 2
        cells = footprint(tw)
        for c in cells:
            for s in range(1, n + 1):
                out.add((round(c[0] + dx * s), round(c[1] + dy * s)))
        out -= cells
    _SHADOW[key] = out
    return out


def stack(game, m):
    """The maps below this floor, nearest first: the floors under it and last the ground."""
    out = []
    key = getattr(m, 'below', None)
    while key:
        b = game.maps.get(key)
        if b is None:
            break
        out.append(b)
        key = getattr(b, 'below', None) if getattr(b, 'sky', None) is not None else None
    return out


def air_look(game, m, i):
    """What you see where there is nothing but air: what lies below, faded by the height between."""
    from .canvas import mix, scale
    from . import look as LOOK
    for b in stack(game, m):
        if b.t[i] != AIR or getattr(b, 'sky', None) is None:
            ch, fg, bg = LOOK.get(b, i)
            down = m.depth - (b.depth if getattr(b, 'sky', None) is not None else 0)
            k = min(.82, .38 + .09 * down)
            fg, bg = mix(fg, HAZE, k), mix(bg, HAZE_BG, min(.9, k + .1))
            if getattr(b, 'sky', None) is None:
                site = game.world.sites[m.sky]
                if (i % m.w, i // m.w) in shadow(game, b, site.tw, m.depth):
                    fg, bg = scale(fg, .62), scale(bg, .55)
            return ch, fg, bg
    return ' ', (0, 0, 0), HAZE_BG


def sky(m, t, night):
    """Birds wheeling below you and a wisp of cloud drifting past: [(x, y, sign, colour)], drawn on the air only."""
    if night:
        return []
    cx, cy = getattr(m, 'sky_centre', (m.w // 2, m.h // 2))
    out = []
    for j in range(3):
        r = 9 + j * 3
        a = t * (.35 + .1 * j) + j * 2.1
        out.append((round(cx + math.cos(a) * r * 1.4), round(cy + math.sin(a) * r * .8), 'v', BIRD))
    k = (t * .02 + m.depth * .3) % 1.0              # a cloud crosses the whole map, now and then
    if k < .6:
        x0 = round(-10 + k / .6 * (m.w + 20))
        y0 = (cy - 8 + m.depth * 5) % max(1, m.h)
        for dx in range(6):
            for dy in range(2):
                if (dx + dy * 2) % 3:
                    out.append((x0 + dx + dy, y0 + dy, '░', (190, 196, 206)))
    return out


def fov(game, m, r):
    """What you see from a floor: through the open air and over the edge; beside an arrow slit, out of it too."""
    from . import fov as FOV
    p = game.player
    slits = [(p.x + dx, p.y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)
             if m.inb(p.x + dx, p.y + dy) and m.tile(p.x + dx, p.y + dy) == D.SLIT]
    for x, y in slits:
        m.t[y * m.w + x] = AIR                  # for this one look the slit is an opening
    try:
        vis = FOV.compute(m, p.x, p.y, r)
    finally:
        for x, y in slits:
            m.t[y * m.w + x] = D.SLIT
    return vis


# ------------------------------------------------------------------ the lookout
def lookout(game):
    """From the top you mark the land round about on the world map: farther the higher the tower, 4 more on a hill,
    half as far in fog or rain; at night only lights: villages, campfires and ships."""
    from . import fov as FOV
    from . import towns as TW
    from . import weather as WX
    m = game.map
    site = game.world.sites[m.sky]
    tw = site.tw
    om = game.maps['over']
    r = 10 + round((tw['storeys'] - 3) * 4 / 3)
    if om.tile(site.x, site.y) == D.HILLS:
        r += 4
    kind = WX.region_weather(game, game.world.region_at(site.x, site.y).id)
    if WX.KINDS.get(kind, ('', 'clear'))[1] in ('fog', 'rain', 'snow', 'sand'):
        r //= 2
    vis = FOV.cells(om, site.x, site.y, r)
    n = 0
    if TW.is_night(game):
        lights = [(s.x, s.y) for s in game.world.settlements] + \
                 [(q.x, q.y) for q in game.world.sites if q.kind in ('warcamp', 'ravine', 'kobolds', 'gnolls', 'stilts', 'cove',
                                                                     'merccamp', 'roadinn', 'oasis')] + \
                 [(wd.x, wd.y) for wd in getattr(game.world, 'wanderers', ()) if getattr(wd, 'kind', '') in ('ship', 'pirates')]
        for x, y in lights:
            i = y * om.w + x
            if 0 <= i < len(vis) and vis[i] and not om.seen[i]:
                om.seen[i] = 1
                n += 1
        game.msg('From the top you look out into the dark. Only lights show: ' +
                 ('you mark them on your map.' if n else 'none you have not seen before.'), 'info')
        return n
    for i, v in enumerate(vis):
        if v and not om.seen[i]:
            om.seen[i] = 1
            n += 1
    from .hidden import from_tower
    from_tower(game, vis)
    game.msg('The wind tugs at your cloak. The land lies small below.', 'info')
    game.msg('You mark what you see on your map.' if n else 'Nothing you have not seen before.', 'info')
    return n


# ------------------------------------------------------------------ edges and falls
def landing(game, m, x, y):
    """Where you would come down from (x, y): (map, floors down), or (None, 0) when nothing is known below."""
    for b in stack(game, m):
        if b.t[y * b.w + x] != AIR or getattr(b, 'sky', None) is None:
            return b, m.depth - (b.depth if getattr(b, 'sky', None) is not None else 0)
    return None, 0


def where_name(b):
    return 'ground' if getattr(b, 'sky', None) is None else 'floor below'


def edge(game, x, y):
    """Walking into the air: asked first, with how far down it is."""
    from . import events as EV
    b, n = landing(game, game.map, x, y)
    if b is None:
        game.msg('Nothing but air below, and you cannot see the bottom.', 'info')
        return 0
    EV.ask(game, 'tower_edge', 'The edge', f"Nothing but air. It is {n} floor{'s' if n > 1 else ''} down to the "
           f"{where_name(b)}. A fall like that hurts.", [('Jump', 'jump'), ('Step back', 'bye')], cell=(x, y))
    return 0


def r_edge(game, choice, ctx):
    if choice != 'jump':
        return
    fall(game, *ctx['cell'])


def fall(game, x, y, cause='a fall'):
    """You go over the edge at (x, y): it hurts by the number of floors, and you land on what lies below."""
    m = game.map
    b, n = landing(game, m, x, y)
    if b is None:
        return
    p = game.player
    s = game.stats()
    dmg = round(n * (4 + s['max_life'] * .09) + random.randint(0, 4))
    game.msg(f"You fall {n} floor{'s' if n > 1 else ''}!", 'bad')
    game.shake()
    _put(game, b, x, y)
    game.hurt(dmg, cause)
    if not game.dead:
        game.msg('You hit the ground hard.' if getattr(b, 'sky', None) is None else 'You crash onto the boards below.', 'bad')


def _put(game, b, x, y):
    """Move you onto map b at (x, y), or the nearest place you can stand."""
    from .worldgen import free_around
    p = game.player
    game.cur = b.key
    if not D.TILES[b.tile(x, y)].walk or game.occupied(b, x, y):
        spots = free_around(game, b, x, y, 3)
        if spots:
            x, y = min(spots, key=lambda c: cheb(c[0], c[1], x, y))
    p.x, p.y = x, y
    game.compute_fov()
    game.request = ('save',)


def thrown(game, x, y):
    """Knocked back over the edge by a foe: no asking now."""
    game.msg('You are thrown over the edge!', 'bad')
    fall(game, x, y, 'a fall from a tower')


def shove_over(game, mon, x, y):
    """A foe shoved or knocked over the edge: it falls to what lies below, and is gone from this floor."""
    m = game.map
    b, n = landing(game, m, x, y)
    game.msg(f'{mon.the()[0].upper() + mon.the()[1:]} goes over the edge and falls '
             f"{n if b else 'a long way'} floor{'s' if n != 1 else ''}!", 'good')
    game.flash([(mon.x, mon.y)], (200, 200, 200), '↓', .3)
    if mon in m.mons:
        m.mons.remove(mon)
    mon.hp -= round(n * mon.maxhp * .3)
    if b is not None and mon.hp > 0:
        from .worldgen import free_around
        spots = [c for c in free_around(game, b, x, y, 3) if not game.occupied(b, *c)]
        if spots:
            mon.x, mon.y = min(spots, key=lambda c: cheb(c[0], c[1], x, y))
            mon.awake = True
            b.mons.append(mon)
            return
    game.gain_xp(max(1, round(mon.xp * .5)))


def on_level(game, m, dg):
    """Arriving on a floor: its line, and from the top the lookout."""
    if getattr(m, 'mood_line', None):
        game.msg(m.mood_line, 'info')
    if m.depth == dg.depth and game.world.sites[dg.site].tw['state'] != 'ruin':
        lookout(game)


from . import events as _EV                             # noqa: E402
_EV.RESOLVERS['tower_edge'] = r_edge
