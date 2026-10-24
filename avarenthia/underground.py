"""Rivers underground (approved 22 October 2026): a river of water or of fire comes in at one edge of a level and
leaves at another. Between caves it runs through the rock in a channel of its own, with rock for banks; where it cuts a
room or a way, the floor gives way to it. Every part of the level stays reachable: where the river cuts the way, a
bridge, a ford or a crust of cooled rock takes you over, which makes a good choke point.

Water you can swim, but heavy armour and a heavy pack pull you under; monsters that cannot swim stay on the bank and
some swim after you. Fire burns whoever steps in it, and a shove or a knockback sends a foe into it.
The light that runs downstream comes from m.river_flow (anim.py)."""
import random
from collections import deque

from . import data as D

D4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
D8 = D4 + ((1, 1), (1, -1), (-1, 1), (-1, -1))
SWIMMERS = {'drowned', 'drowned_king', 'mire_leech', 'lizard_warrior', 'lizard_spear', 'lizard_shaman', 'crocodile',
            'giant_frog', 'giant_crab', 'crabfolk', 'merrow'}
HEAVY = {'chainmail', 'platemail'}          # body armour that pulls a swimmer under
CHANCE = .45                                 # how often a large K5 level has a river
FIRE_FROM = 3                                # rivers of fire only from this depth down
FIRE_SHARE = .35                             # and then this share of them


def _walk(t):
    td = D.TILES[t]
    return td.walk or td.door


def _parts(m):
    """The walkable parts of the map: a list of index sets, biggest first."""
    seen = bytearray(len(m.t))
    parts = []
    for s, t in enumerate(m.t):
        if seen[s] or not _walk(t):
            continue
        part, q = [s], deque([s])
        seen[s] = 1
        while q:
            i = q.popleft()
            x, y = i % m.w, i // m.w
            for dx, dy in D8:
                nx, ny = x + dx, y + dy
                if 0 <= nx < m.w and 0 <= ny < m.h:
                    j = ny * m.w + nx
                    if not seen[j] and _walk(m.t[j]):
                        seen[j] = 1
                        part.append(j)
                        q.append(j)
        parts.append(set(part))
    parts.sort(key=len, reverse=True)
    return parts


def _course(w, h):
    """The middle line of a river from one edge to the other: a list of (x, y), meandering."""
    along, across = (w, h) if random.random() < .7 else (h, w)
    lo, hi = 7, across - 8
    a = random.randint(lo + (hi - lo) // 5, hi - (hi - lo) // 5)
    slope, line = 0, []
    for s in range(along):
        if random.random() < .14:
            slope = random.choice((-1, 0, 0, 1))
        if a + slope < lo or a + slope > hi:
            slope = -slope
        a += slope if s % 2 else 0                  # a gentle bend: at most one cell across every two along
        line.append((s, a) if along == w else (a, s))
    if random.random() < .5:
        line.reverse()                              # which way it flows
    return line, along == w


def add_river(m, depth, keep=(), fire=None, bridge=None, swallow=10):
    """Run a river through a dug level. Returns 'water', 'fire' or None (when it could not be joined up again).
    fire forces a river of fire; bridge is the one tile every crossing is made of (the Deep's chains); a cut-off
    scrap of floor smaller than swallow goes under the river."""
    if fire is None:
        fire = depth >= FIRE_FROM and random.random() < FIRE_SHARE
    tile = D.LAVA if fire else D.WATER
    old = bytearray(m.t)
    line, across_y = _course(m.w, m.h)
    flow = {}
    half = 1
    theme = getattr(m, 'theme_cells', ())              # a theme room keeps what was drawn in it
    for d, (cx, cy) in enumerate(line):
        for k in range(-half, half + 1):
            x, y = (cx, cy + k) if across_y else (cx + k, cy)
            if 0 <= x < m.w and 0 <= y < m.h:
                i = y * m.w + x
                if i not in flow and i not in theme:
                    flow[i] = d
                    m.t[i] = tile
    for x, y in keep:                               # the stairs stay dry, with a step of shore round them
        for dx, dy in D8 + ((0, 0),):
            j = (y + dy) * m.w + x + dx
            if 0 <= x + dx < m.w and 0 <= y + dy < m.h and j in flow:
                m.t[j] = old[j] if _walk(old[j]) else D.FLOOR
                del flow[j]
    if not _join(m, tile, keep, flow, bridge, swallow):
        m.t[:] = old
        return None
    m.river_flow = flow
    m.river = 'fire' if fire else 'water'
    return m.river


def _join(m, tile, keep, flow, bridge=None, swallow=10):
    """Make every part reachable from the stairs again: tiny cut-off bits go under the river, bigger ones get a
    crossing (the shortest way over the river from what is reachable)."""
    start = keep[0][1] * m.w + keep[0][0] if keep else None
    for _ in range(40):
        parts = _parts(m)
        if not parts:
            return False
        main = next((p for p in parts if start in p), parts[0])
        theme = getattr(m, 'theme_cells', ())
        rest = [p for p in parts if p is not main and not p <= theme]     # cells and cages behind bars stay shut
        if not rest:
            return True
        swallowed = False
        for p in rest:
            if len(p) < swallow and not any(k[1] * m.w + k[0] in p for k in keep) and \
                    any(m.t[j] == tile for i in p for j in _round(m, i)):
                for i in p:                          # a scrap of floor the river swallowed
                    m.t[i] = tile
                    flow[i] = min((flow[j] for j in _round(m, i) if j in flow), default=0)
                swallowed = True
        if not swallowed and not _cross(m, tile, main, flow, bridge):
            return False
    return False


def _round(m, i):
    x, y = i % m.w, i // m.w
    return [(y + dy) * m.w + x + dx for dx, dy in D4 if 0 <= x + dx < m.w and 0 <= y + dy < m.h]


def _cross(m, tile, main, flow, bridge=None):
    """Lay one crossing: a straight-as-can-be way over the river from the reachable part to another one."""
    prev = {}
    q = deque()
    for i in main:
        for j in _round(m, i):
            if m.t[j] == tile and j not in prev:
                prev[j] = None
                q.append(j)
    while q:
        i = q.popleft()
        for j in _round(m, i):
            if _walk(m.t[j]) and j not in main:
                way = []
                while i is not None:
                    way.append(i)
                    i = prev[i]
                if bridge is not None:
                    kind = bridge
                elif tile == D.LAVA:
                    kind = D.CRUST if random.random() < .6 else D.BRIDGE
                else:
                    kind = D.BRIDGE if random.random() < .6 or len(way) > 4 else D.SHALLOW
                for c in way:
                    m.t[c] = kind
                    flow.pop(c, None)
                return True
            if m.t[j] == tile and j not in prev:
                prev[j] = i
                q.append(j)
    return False


# ------------------------------------------------------------------ in the river
def heavy(game):
    """What would pull you under: your armour, your pack, or nothing."""
    p = game.player
    arm = game.eq_item('armor')
    if arm is not None and arm.base in HEAVY:
        return 'armour'
    from . import economy as ECO
    if ECO.cargo_weight(p) > ECO.cargo_capacity(p) // 2:
        return 'pack'
    return None


def step_in(game, nx, ny, dx, dy):
    """You walk into dungeon water or a river of fire. Returns the turns it took, or 0 when you stopped to ask."""
    from . import events as EV
    p, m = game.player, game.map
    t = m.tile(nx, ny)
    here = m.tile(p.x, p.y)
    ok = getattr(p, 'wade_ok', None) == (nx, ny)
    p.wade_ok = None
    if t == D.LAVA:
        if not ok:
            EV.ask(game, 'river_fire', 'The river of fire', 'Molten rock runs here, slow and bright. The heat stings your '
                   'face from a step away. To walk into it is to burn, badly.',
                   [('Step into the fire', 'in'), ('Step back', 'bye')], to=(nx, ny), d=(dx, dy))
            return 0
        p.x, p.y = nx, ny
        game.msg('You step into the fire. It burns!', 'bad')
        game.hurt(max(6, round(game.stats()['max_life'] * .35)), 'a river of fire', 'fire')
        return 1
    weight = heavy(game)
    if weight and here != D.WATER and not ok:
        what = 'your armour' if weight == 'armour' else 'your heavy pack'
        EV.ask(game, 'river_swim', 'Deep water', f'The water is deep and cold. With {what} it will pull you under: '
               'every stroke will cost you dearly.', [('Swim anyway', 'in'), ('Step back', 'bye')], to=(nx, ny), d=(dx, dy))
        return 0
    if here != D.WATER:
        game.msg('You wade in and swim.' if not weight else 'You go in. The weight drags at you at once.',
                 'info' if not weight else 'bad')
    p.x, p.y = nx, ny
    if weight:
        game.hurt(max(2, round(game.stats()['max_life'] * .08)), 'drowning')
    return 2                                        # swimming is slow


def r_wade(game, choice, ctx):
    if choice != 'in':
        return
    game.player.wade_ok = tuple(ctx['to'])
    cost = game.try_move(*ctx['d'])
    if cost:
        game.end_turn(cost)


def swims(mon):
    return mon.k in SWIMMERS


def swim_after(game, mon):
    """A swimmer with no way round goes into the water after you. True when it moved."""
    m, p = game.map, game.player
    best = None
    bd = max(abs(p.x - mon.x), abs(p.y - mon.y))
    for dx, dy in D8:
        nx, ny = mon.x + dx, mon.y + dy
        if not m.inb(nx, ny) or game.occupied(m, nx, ny) or (nx, ny) == (p.x, p.y):
            continue
        t = m.tile(nx, ny)
        if t != D.WATER and not D.TILES[t].walk:
            continue
        nd = max(abs(p.x - nx), abs(p.y - ny))
        if nd < bd:
            bd, best = nd, (nx, ny)
    if best:
        mon.x, mon.y = best
        return True
    return False


def into_fire(game, mon, back):
    """A foe shoved into a river of fire: it burns, and crawls out where it came from if it lives."""
    game.msg(f'{mon.the()[0].upper() + mon.the()[1:]} falls into the fire!', 'good')
    game.damage_mon(mon, max(8, round(mon.maxhp * .5)), elem='fire')
    if mon in game.map.mons:
        mon.x, mon.y = back


def over_edge(game, mon):
    """A foe shoved over the edge of a chasm: it falls to the level below, and is gone from this one."""
    game.msg(f'{mon.the()[0].upper() + mon.the()[1:]} goes over the edge and falls into the dark!', 'good')
    game.flash([(mon.x, mon.y)], (200, 200, 200), '↓', .3)
    if mon in game.map.mons:
        game.map.mons.remove(mon)
    game.gain_xp(max(1, round(mon.xp * .5)))


from . import events as _EV                             # noqa: E402  (events imports much; resolvers registered here)
_EV.RESOLVERS['river_fire'] = r_wade
_EV.RESOLVERS['river_swim'] = r_wade
