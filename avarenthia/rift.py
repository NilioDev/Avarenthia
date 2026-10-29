"""The Rift and the Ashen Deep (round 9). Now and then a rift tears open in the world: a scar on the world map, the
land round it burning slowly to ash, fiends out of it raiding the villages near it at night. Sometimes it opens
under the bottom of a very deep dungeon instead. Below lie three to five levels of black basalt and ash with a
river of fire and its bridges of chains, brimstone vents, bone fields where the dead rise, cages with the taken
and their gaolers, and at the bottom a hall of black iron where the Lord of Cinders keeps court before the burning
gate. Break the gate and the rift closes; the land heals slowly. Nobody rests down there."""
import math
import random

from . import data as D
from .data import FLOOR, ROCK, WALL, UP, DOWN
from .worldgen import cheb, free_around, bfs, gen_cave

LORDS = ['Azhkal of the Seventh Coal', 'Vorrask the Unquenched', 'Ilthrix, Who Was a Star', 'Morgrath Ember-Crowned',
         'Sathrel the Ashen Bride', 'Khor of the Last Fire', 'Ulmeth Who Eats the Light', 'Dravga of the Black Bell']
TAKEN = ['a miller from {v}', 'a shepherd girl from {v}', 'the smith of {v}', 'a pedlar taken on the road to {v}',
         'two children from {v}', 'an old priest from {v}', 'a farmer from {v}']
WALL_FG = (74, 64, 68)
AMBIENT = (.62, .36, .26)          # the fire gives the light: you carry none down there
FIENDS = ('imp', 'hellhound', 'hollow_spawn', 'hungering_shade')
MAX_ASH = 9
for _k in FIENDS:                  # the fiends already in the game live in the Deep too
    if 'rift' not in D.MONSTERS[_k]['tags'].split():
        D.MONSTERS[_k]['tags'] += ' rift'


def get(world):
    return world.__dict__.get('rift')


def active(world):
    r = get(world)
    return r if r and r['state'] == 'open' else None


# ------------------------------------------------------------------ the rift on the world map
def find_spot(game, near=None, lo=6, hi=40):
    w, om = game.world, game.maps['over']
    start = w.settlements[0]
    bad = (D.ROAD, D.TOWN, D.CITY, D.ENTR, D.RIVER, D.WATER, D.MOUNTAIN, D.CASTLE, D.FORT)
    for _ in range(6000):
        if near:
            x, y = near[0] + random.randint(-hi, hi), near[1] + random.randint(-hi, hi)
            if not lo <= cheb(x, y, *near) <= hi:
                continue
        else:
            x, y = random.randint(6, om.w - 7), random.randint(6, om.h - 7)
        if not om.inb(x, y) or not (4 <= x < om.w - 4 and 4 <= y < om.h - 4):
            continue
        i = y * om.w + x
        t = om.t[i]
        if not D.TILES[t].walk or t in bad or i in getattr(w, 'wonder_cells', ()) or w.road_dist[i] < 3:
            continue
        if near is None and cheb(x, y, start.x, start.y) < 25:
            continue
        if any(cheb(x, y, s.x, s.y) < 8 for s in w.settlements) or any(cheb(x, y, d.x, d.y) < 4 for d in w.dungeons.values()) \
                or any(cheb(x, y, q.x, q.y) < 4 for q in w.sites) or any(cheb(x, y, h.x, h.y) < 6 for h in w.holds):
            continue
        return x, y
    return None


def deep_dungeons(world):
    return [d for d in world.dungeons.values() if d.depth >= 4 and getattr(d, 'site', None) is None
            and getattr(d, 'town', None) is None and getattr(d, 'mine', None) is None and not getattr(d, 'poi', False)
            and d.tag != 'rift' and getattr(d, 'under', None) is None]


def open_rift(game, spot=None, under=None):
    """A rift tears open: on the land, or under the bottom of a very deep dungeon."""
    from .world import Dungeon
    from . import realms as RL
    w, om = game.world, game.maps['over']
    if active(w):
        return None
    deep = deep_dungeons(w)
    if under is None and spot is None and deep and random.random() < .3:
        under = random.choice(deep)
    if under is not None:
        x, y = under.x, under.y
    else:
        spot = spot or find_spot(game)
        if not spot:
            return None
        x, y = spot
    n = sum(1 for k in w.dungeons if k.startswith('rift'))
    did = 'rift' if not n else f'rift{n}'
    dg = Dungeon(did, 'The Ashen Deep', random.randint(3, 5), w.danger_at(x, y) + 4, 'rift', 'rift', 'cinder_lord',
                 WALL_FG, x, y, False)
    w.dungeons[did] = dg
    r = w.rift = dict(x=x, y=y, did=did, opened=game.day, state='open', lord=random.choice(LORDS), r=1, gate=3,
                      under=under.id if under is not None else None, raids=0)
    if under is not None:
        dg.under = under.id
        under.rift_below = did
        bottom = game.maps.get(f'{under.id}:{under.depth}')
        if bottom is not None:
            crack(game, bottom)
        RL.news(game, f'They say the bottom of {under.name} has broken through into somewhere hot and red, and that '
                      'what climbs out of it is not of this world.', x, y, 'Places', title='A rift below the earth')
    else:
        om.set(x, y, D.ENTR)
        RL.news(game, f'The earth tore open near {w.region_at(x, y).name}. A red glow stands over the place at night, '
                      'and the grass round it is turning to ash.', x, y, 'Places', title='A rift in the world')
    _ash_reset(w)
    return r


def close(game):
    from . import realms as RL
    w = game.world
    r = get(w)
    if not r or r['state'] != 'open':
        return
    r['state'], r['closed'] = 'closed', game.day
    RL.news(game, f'The rift near {w.region_at(r["x"], r["y"]).name} has closed. The red glow is gone, and they say '
                  f'{r["lord"]} burns no longer.', r['x'], r['y'], 'Places', title='The rift closed')
    game.gain_xp(150 + w.dungeons[r['did']].base * 20)


def _ash_reset(world):
    world.__dict__.pop('_rift_ash', None)


def _noise(x, y):
    return ((x * 73856093) ^ (y * 19349663)) % 1000 / 1000


def ash_cells(world):
    """The land round the rift burnt to ash: a set of world-map cells (cached)."""
    r = get(world)
    if not r or r['r'] <= 0:
        return ()
    c = world.__dict__.get('_rift_ash')
    if c and c[0] == r['r']:
        return c[1]
    from .world import WORLD_W, WORLD_H
    out = set()
    rad = r['r']
    for dy in range(-rad - 2, rad + 3):
        for dx in range(-rad - 2, rad + 3):
            x, y = r['x'] + dx, r['y'] + dy
            if 0 <= x < WORLD_W and 0 <= y < WORLD_H and math.hypot(dx, dy) <= rad * (.7 + .6 * _noise(x, y)):
                out.add(y * WORLD_W + x)
    world._rift_ash = (rad, out)
    return out


def ash_at(game, x, y):
    w = game.world
    from .world import WORLD_W
    return active(w) is not None and (y * WORLD_W + x) in ash_cells(w)


def monthly(game):
    w = game.world
    r = get(w)
    if r is None or (r['state'] == 'closed' and game.day - r.get('closed', 0) > 360 and r['r'] <= 0):
        if game.day >= 40 and random.random() < .1:
            open_rift(game)
        return
    if r['state'] == 'open':
        r['r'] = min(MAX_ASH, r['r'] + 1)
    else:
        r['r'] = max(0, r['r'] - 1)                  # the land heals, slowly
    _ash_reset(w)


def daily(game):
    """At night the fiends come out of the rift and raid the villages near it."""
    w = game.world
    r = active(w)
    if not r or random.random() > .18:
        return
    from .living import plundered, PLUNDER_DAYS
    from . import realms as RL
    near = [s for s in w.settlements if s.kind in ('hamlet', 'village', 'town') and s.id != 0 and cheb(s.x, s.y, r['x'], r['y']) <= 30
            and not plundered(game, s)]
    if not near:
        return
    s = min(near, key=lambda q: cheb(q.x, q.y, r['x'], r['y']) + random.randint(0, 12))
    s.plundered = game.day + PLUNDER_DAYS
    s.event = ('war', random.randint(4, 7))
    r['raids'] += 1
    taken = random.choice(TAKEN).format(v=s.name)
    r.setdefault('taken', []).append(taken)
    RL.news(game, random.choice([f'Fiends came out of the dark at night and set fire to {s.name}. They took {taken}.',
                                 f'Something burning ran through {s.name} in the night. In the morning {taken} was gone.',
                                 f'Hounds of fire hunted round {s.name} all night. Folk say they belong to {r["lord"]}.']),
            s.x, s.y, 'Places')


# ------------------------------------------------------------------ the levels
def level(game, d, depth):
    """A level of the Ashen Deep: basalt and ash, a river of fire with bridges of chains, vents, bone fields, cages,
    and at the bottom the hall of black iron with the burning gate."""
    from . import k5
    from . import underground as UG
    from .worldgen import spawn_pack, rand_free, place_chest
    from .entities import GameMap, make_monster, Item
    last = depth >= d.depth
    size = 'very large' if last else 'large'
    mw, mh = k5.SIZES[size]
    m = GameMap(f'{d.id}:{depth}', 'dungeon', d.name, mw, mh, ROCK)
    lvl = d.base + depth
    m.did, m.depth, m.level, m.radius, m.wall_fg = d.id, depth, lvl, 9, d.wall
    m.dtag, m.last, m.style = d.tag, last, 'rift'
    m.rift, m.ambient = True, AMBIENT
    gen_cave(m)
    floors = [i for i, t in enumerate(m.t) if t == FLOOR]
    s = random.choice(floors)
    up = (s % m.w, s // m.w)
    dist = bfs(m, up[0], up[1], lambda t: D.TILES[t].walk)
    far_i = max(floors, key=lambda i: dist[i])
    far = (far_i % m.w, far_i // m.w)
    if last:
        far = court(game, m, far, up, lvl)
        reach = bfs(m, up[0], up[1], lambda t: D.TILES[t].walk)
        for i, t in enumerate(m.t):                # scraps of cave the hall cut off fill in
            if t == FLOOR and reach[i] < 0:
                m.t[i] = ROCK
    m.theme_cells = set(getattr(m, 'hall_cells', ()))      # the river of fire goes round the hall of black iron
    for _ in range(6):                             # a river of fire through every level
        if UG.add_river(m, 3, (up, far), fire=True, bridge=D.CHAINS, swallow=60):
            break
    m.set(*up, UP)
    if not last:
        m.set(*far, DOWN)
    open_ = lambda t: t in (FLOOR, D.ASH)                                       # noqa: E731
    near_stairs = lambda x, y: cheb(x, y, *up) < 4 or cheb(x, y, *far) < 4     # noqa: E731
    for i, t in enumerate(m.t):                    # ash underfoot
        if t == FLOOR and random.random() < .6 and not near_stairs(i % m.w, i // m.w):
            m.t[i] = D.ASH
    m.vents = {}
    for _ in range(random.randint(6, 10)):
        c = rand_free(game, m, open_, (up[0], up[1], 6))
        if c and not near_stairs(*c):
            m.set(*c, D.VENT)
            m.vents[c] = random.randint(2, 9)
    m.bonefields = []
    for _ in range(random.randint(2, 3)):
        c = rand_free(game, m, open_, (up[0], up[1], 10))
        if not c:
            continue
        cells = [(c[0] + dx, c[1] + dy) for dx in range(-3, 4) for dy in range(-2, 3)
                 if math.hypot(dx * .7, dy) <= 2.2 and m.inb(c[0] + dx, c[1] + dy) and open_(m.tile(c[0] + dx, c[1] + dy))
                 and not near_stairs(c[0] + dx, c[1] + dy)]
        for x, y in cells:
            m.set(x, y, D.BONEFIELD)
        if cells:
            m.bonefields.append(dict(cells=cells, risen=False))
    cages(game, m, up, far, lvl)
    npacks = round((4 + depth) * 1.3 * (m.w * m.h / 4200) ** .5)
    for k in range(npacks):
        c = rand_free(game, m, open_, (up[0], up[1], 10))
        if c:
            spawn_pack(game, m, lvl, 'rift', c, 2 if k == npacks - 1 and depth >= 2 else None, False)
    chains = [i for i, t in enumerate(m.t) if t == D.CHAINS]
    done = []
    for i in chains:                               # a warden at each bridge
        x, y = i % m.w, i // m.w
        if any(cheb(x, y, a, b) < 8 for a, b in done):
            continue
        spot = next((c for c in free_around(game, m, x, y, 2) if open_(m.tile(*c)) and not game.occupied(m, *c)), None)
        if spot:
            o = make_monster(game, 'chain_warden', spot[0], spot[1], lvl)
            m.mons.append(o)
            done.append((x, y))
    for _ in range(random.randint(1, 2)):
        c = rand_free(game, m, open_)
        if c:
            it = Item(game.new_id(), 'potion', 'hp' if random.random() < .6 else 'mp')
            it.x, it.y = c
            m.items.append(it)
    if last:
        place_chest(m)
        from . import bosses as BS
        BS.on_level(game, m)                       # the hall shuts behind you until its lord falls
    m.mood_line = random.choice(['Black stone, warm to the touch. Ash drifts down from nowhere, and the air tastes of sulphur.',
                                 'The heat comes up through your boots. Somewhere a river of fire roars.',
                                 'Red light on black rock, and ash over everything. Nobody could sleep here.'])
    return m


def cages(game, m, up, far, lvl):
    """Cages hung on chains with the taken in them, a gaoler, and the gong it runs for."""
    from .entities import make_monster
    from .worldgen import rand_free
    r = get(game.world) or {}
    taken = list(r.get('taken', ())) or [random.choice(TAKEN).format(v='a village up above')]
    m.cages = {}
    open_ = lambda t: t in (FLOOR, D.ASH)                  # noqa: E731
    for _ in range(random.randint(1, 2)):
        c = rand_free(game, m, open_, (up[0], up[1], 12))
        if not c:
            continue
        x, y = c
        row = [(x + k, y) for k in range(-2, 3) if m.inb(x + k, y) and open_(m.tile(x + k, y))]
        for k, cc in enumerate(row[::2]):
            m.set(*cc, D.CAGE)
            m.cages[cc] = taken.pop(0) if taken and k == 0 else (random.choice(TAKEN).format(v='a village up above')
                                                                if random.random() < .4 else None)
        spot = next((cc for cc in free_around(game, m, x, y + 1, 2) if open_(m.tile(*cc)) and not game.occupied(m, *cc)), None)
        if spot:
            m.mons.append(make_monster(game, 'gaoler', spot[0], spot[1], lvl))
        if getattr(m, 'gong', None) is None:
            g = rand_free(game, m, open_, (x, y, 8))
            if g and cheb(g[0], g[1], x, y) <= 25:
                m.set(*g, D.GONG)
                m.gong = g


def court(game, m, far, up, lvl):
    """The hall of black iron at the bottom: the burning gate, its fire bowls, and the Lord of Cinders. Returns where
    the hall's door is, so the way there stays open."""
    from .entities import make_monster
    hw, hh = 25, 15
    fx, fy = far
    x0 = max(2, min(m.w - hw - 2, fx - hw // 2))
    y0 = max(2, min(m.h - hh - 2, fy - hh // 2))
    cx, cy = x0 + hw // 2, y0 + hh // 2
    m.hall_cells = set()
    for y in range(y0 - 1, y0 + hh + 1):
        for x in range(x0 - 1, x0 + hw + 1):
            edge = x in (x0 - 1, x0 + hw) or y in (y0 - 1, y0 + hh)
            m.set(x, y, WALL if edge else D.IRON)
            m.hall_cells.add(y * m.w + x)
    m.built = True
    # the door faces the way you come in
    if abs(up[0] - cx) > abs(up[1] - cy):
        door = (x0 - 1, cy) if up[0] < cx else (x0 + hw, cy)
        back = (x0 + hw - 2, cy) if up[0] < cx else (x0 + 1, cy)
    else:
        door = (cx, y0 - 1) if up[1] < cy else (cx, y0 + hh)
        back = (cx, y0 + hh - 2) if up[1] < cy else (cx, y0 + 1)
    m.set(*door, D.IRON)
    out = (door[0] + (door[0] > cx) - (door[0] < cx), door[1] + (door[1] > cy) - (door[1] < cy))
    reach = bfs(m, up[0], up[1], lambda t: D.TILES[t].walk and t != D.IRON)
    x, y = out
    for _ in range(m.w + m.h):                     # a way out from the door into the caves you came through
        if not (1 <= x < m.w - 1 and 1 <= y < m.h - 1):
            break
        if m.tile(x, y) not in (FLOOR,) and m.tile(x, y) != D.IRON:
            m.set(x, y, FLOOR)
        if reach[y * m.w + x] >= 0:
            break
        nx, ny = x + (up[0] > x) - (up[0] < x), y + (up[1] > y) - (up[1] < y)
        if x0 - 1 <= nx <= x0 + hw and y0 - 1 <= ny <= y0 + hh:       # never back through the hall's own wall
            nx, ny = (x + (up[0] > x) - (up[0] < x), y) if not (x0 - 1 <= x + (up[0] > x) - (up[0] < x) <= x0 + hw
                                                                and y0 - 1 <= y <= y0 + hh) else (x, y + (up[1] > y) - (up[1] < y))
        if (nx, ny) == (x, y):
            break
        if nx != x and ny != y:                    # no slanting steps: a river must be able to cut it square
            side = (nx, y) if (y * m.w + nx) not in m.hall_cells else (x, ny)
            if m.tile(*side) != D.IRON:
                m.set(*side, FLOOR)
        x, y = nx, ny
    m.set(*back, D.FIREGATE)
    m.gate = back
    bowls = [(back[0] + a, back[1] + b) for a, b in ((-2, -2), (2, -2), (-2, 2), (2, 2))]
    for c in bowls:
        if m.inb(*c) and m.tile(*c) == D.IRON:
            m.set(*c, D.FIREBOWL)
    for k in range(3, hw - 3, 4):                 # pillars down the hall
        for yy in (y0 + 2, y0 + hh - 3):
            if m.tile(x0 + k, yy) == D.IRON:
                m.set(x0 + k, yy, D.PILLAR)
    r = get(game.world) or {}
    tx, ty = (back[0] + (cx > back[0]) - (cx < back[0]), back[1] + (cy > back[1]) - (cy < back[1]))
    lord = make_monster(game, 'cinder_lord', tx, ty, lvl + 2)
    lord.name = r.get('lord', random.choice(LORDS))
    lord.lord = True
    m.mons.append(lord)
    for c in free_around(game, m, tx, ty, 3)[:3]:
        if m.tile(*c) == D.IRON:
            m.mons.append(make_monster(game, 'imp', c[0], c[1], lvl))
    return out


def crack(game, m):
    """The bottom of a very deep dungeon breaks through into the Deep: a crack going down."""
    from .worldgen import rand_free
    if DOWN in m.t:
        return
    up = m.t.index(UP) if UP in m.t else 0
    c = rand_free(game, m, lambda t: t == FLOOR, (up % m.w, up // m.w, 10))
    if c:
        m.set(*c, DOWN)
        m.crack = c


# ------------------------------------------------------------------ down there
def stairs(game, t, d):
    """The crack at the bottom of a deep dungeon, and the way back up out of a Deep opened under one."""
    m, w = game.map, game.world
    if m.kind != 'dungeon':
        return None
    dg = w.dungeons.get(m.did)
    if dg is None:
        return None
    below = getattr(dg, 'rift_below', None)
    if t == DOWN and d != 'up' and below and m.depth >= dg.depth:
        game.msg('You climb down through the crack, into heat and a red glow.', 'bad')
        game.enter_dungeon(below, 1, 'up')
        return 1
    if t == UP and d != 'down' and getattr(dg, 'under', None) and m.depth == 1:
        under = w.dungeons[dg.under]
        game.enter_dungeon(under.id, under.depth, 'down')
        game.msg('You climb back up through the crack.', 'info')
        return 1
    return None


def on_enter(game, m):
    if getattr(m, 'mood_line', None) and not getattr(m, 'mood_told', False):
        m.mood_told = True
        game.msg(m.mood_line, 'info')


def on_step(game):
    """A step on a bone field: the dead rise out of it."""
    m, p = game.map, game.player
    if m.tile(p.x, p.y) != D.BONEFIELD:
        return
    from .entities import make_monster
    for bf in getattr(m, 'bonefields', ()):
        if bf['risen'] or (p.x, p.y) not in bf['cells']:
            continue
        bf['risen'] = True
        spots = [c for c in bf['cells'] if cheb(c[0], c[1], p.x, p.y) >= 1 and not game.occupied(m, *c)]
        random.shuffle(spots)
        for c in spots[:random.randint(2, 3)]:
            o = make_monster(game, 'ashwalker', c[0], c[1], m.level)
            o.awake = True
            m.mons.append(o)
        game.flash(spots[:3], (200, 190, 170), '%', .3)
        game.msg('The bones stir under your feet. Grey shapes sit up in the ash, and stand.', 'bad')


def turn(game):
    """Every turn down there: the vents puff, the lord heals from its gate and calls its hounds."""
    m, p = game.map, game.player
    from .entities import make_monster
    for c, k in list(getattr(m, 'vents', {}).items()):
        k -= 1
        if k > 0:
            m.vents[c] = k
            continue
        m.vents[c] = random.randint(5, 9)
        cells = [(c[0] + dx, c[1] + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if m.inb(c[0] + dx, c[1] + dy)]
        seen = game.visible(*c)
        if seen:
            game.flash(cells, (230, 210, 80), '░', .25)
        if cheb(p.x, p.y, *c) <= 1 and not game.dead:
            p.stamina = max(0, p.stamina - 6)
            game.msg('The vent puffs out choking yellow smoke. You cough until your eyes run.', 'bad')
            game.hurt(max(1, m.level // 4), 'brimstone smoke', 'poison')
        for o in m.mons:
            if not o.is_npc and o.tpl.get('family') != 'fiend' and cheb(o.x, o.y, *c) <= 1:
                o.hp -= max(1, m.level // 4)
    for o in list(m.mons):
        if getattr(o, 'brittle', 0):
            o.brittle -= 1
        if not getattr(o, 'lord', False) or o.hp <= 0:
            continue
        lit = D.FIREBOWL in m.t and getattr(m, 'gate', None) and m.tile(*m.gate) == D.FIREGATE
        from . import bosses as BS
        if lit and o.hp < BS.cap_hp(o):
            o.hp = min(BS.cap_hp(o), o.hp + max(2, o.maxhp // 40))
            if game.visible(o.x, o.y) and random.random() < .15:
                game.msg(f'Fire runs from the gate into {o.name}, and its wounds close.', 'bad')
        if o.hp <= o.maxhp // 2 and not getattr(o, 'called', False):
            o.called = True
            n = 0
            for c in free_around(game, m, o.x, o.y, 3):
                if n >= 3:
                    break
                if D.TILES[m.tile(*c)].walk and not game.occupied(m, *c):
                    h = make_monster(game, 'hellhound', c[0], c[1], m.level)
                    h.awake = True
                    m.mons.append(h)
                    n += 1
            game.msg(f'{o.name} howls, and hellhounds come running out of the fire.', 'bad')


def bump(game, x, y, t):
    """Fire bowls, the burning gate, the cages, the gong. Returns turns spent, or None."""
    m = game.map
    r = get(game.world)
    if t == D.FIREBOWL:
        m.set(x, y, D.BOWLOUT)
        game.msg('You tip the fire bowl over. The coals hiss out on the iron.' + (
            ' The gate burns lower.' if D.FIREBOWL not in m.t else ''), 'good')
        return 1
    if t == D.FIREGATE:
        lord = next((o for o in m.mons if getattr(o, 'lord', False)), None)
        if lord:
            game.hurt(max(3, game.stats()['max_life'] // 10), 'the burning gate', 'fire')
            game.msg('You strike the burning gate. Its fire leaps at you while its lord still lives.', 'bad')
        else:
            game.msg('You strike the burning gate. Black iron cracks.', 'info')
        game.shake()
        if r and r['state'] == 'open' and r['did'] == m.did:
            r['gate'] -= 1
            if r['gate'] > 0:
                return 1
        m.set(x, y, D.BROKENGATE)
        for i, tt in enumerate(m.t):
            if tt == D.FIREBOWL:
                m.t[i] = D.BOWLOUT
        game.msg('The gate breaks with a sound like a bell cracking. The fire in it goes out, the whole Deep shudders, '
                 'and far above, the rift closes.', 'unique')
        close(game)
        return 1
    if t == D.CAGE:
        who = getattr(m, 'cages', {}).pop((x, y), 'nobody')
        m.set(x, y, D.ASH)
        if who:
            game.msg(f'You break the cage open. Inside is {who}, alive. They run for the stairs, weeping.', 'good')
            game.gain_xp(15 + m.level * 2)
            if r and who in r.get('taken', []):
                r['taken'].remove(who)
                r['freed'] = r.get('freed', 0) + 1
        else:
            game.msg('You break the cage open. There is only ash inside, and a shoe.', 'info')
        return 1
    if t == D.GONG:
        ring(game, m)
        return 1
    return None


def ring(game, m, who=None):
    m.rung = True
    for o in m.mons:
        if not o.is_npc:
            o.awake = True
    game.shake()
    game.msg((f'{who} strikes the gong!' if who else 'You strike the gong.') + ' The sound rolls through the Deep, and '
             'everything on this level wakes.', 'bad')


# ------------------------------------------------------------------ the creatures' tricks
def gaoler(game, mon, dist, seen):
    """It runs for the gong when it sees you. Returns True when it used its turn."""
    m = game.map
    g = getattr(m, 'gong', None)
    if g is None or getattr(m, 'rung', False):
        return False
    if not getattr(mon, 'running', False):
        if not (seen and dist <= 8):
            return False
        mon.running = True
        game.msg(f'{mon.the().capitalize()} sees you and runs for the gong!', 'bad')
    if cheb(mon.x, mon.y, *g) <= 1:
        ring(game, m, mon.the().capitalize())
        mon.running = False
        return True
    dmap = m.__dict__.get('_gong_dist')
    if dmap is None:
        dmap = m._gong_dist = bfs(m, g[0], g[1], lambda t: D.TILES[t].walk)
    best = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            x, y = mon.x + dx, mon.y + dy
            if (dx or dy) and m.inb(x, y) and D.TILES[m.tile(x, y)].walk and not game.occupied(m, x, y) \
                    and dmap[y * m.w + x] >= 0 and (best is None or dmap[y * m.w + x] < best[0]):
                best = (dmap[y * m.w + x], x, y)
    if best:
        mon.x, mon.y = best[1], best[2]
    return True


def hook(game, mon, dist):
    """The chain warden throws its hooked chain and drags you to it, over the fire if it can."""
    from .behave import _line_ok
    p, m = game.player, game.map
    if not 2 <= dist <= 5 or getattr(mon, 'hook_cd', 0) > game.turn or random.random() > .35 or not _line_ok(game, mon):
        return False
    mon.hook_cd = game.turn + 5
    sx, sy = (mon.x > p.x) - (mon.x < p.x), (mon.y > p.y) - (mon.y < p.y)
    x, y, burned = p.x, p.y, False
    while cheb(x + sx, y + sy, mon.x, mon.y) >= 1 and (x + sx, y + sy) != (mon.x, mon.y):
        nx, ny = x + sx, y + sy
        tt = m.tile(nx, ny)
        if not (D.TILES[tt].walk or tt == D.LAVA) or game.occupied(m, nx, ny):
            break
        x, y = nx, ny
        burned = burned or tt == D.LAVA
    if m.tile(x, y) == D.LAVA:                    # never left lying in the fire: the chain lets go on the far side
        x, y = p.x, p.y
    if (x, y) == (p.x, p.y):
        return False
    game.flash([(p.x, p.y), (x, y)], (170, 170, 180), '~', .2)
    p.x, p.y = x, y
    game.msg(f'{mon.the().capitalize()} throws a hooked chain and drags you to it' + (', over the fire!' if burned else '!'), 'bad')
    if burned:
        game.hurt(max(4, game.stats()['max_life'] // 8), 'the river of fire', 'fire')
    game.compute_fov()
    return True


def sulphur(game, mon, dist):
    """The brimstone toad spits sulphur that chokes: it costs you stamina."""
    from .behave import _line_ok
    p = game.player
    if not 2 <= dist <= 4 or getattr(mon, 'spit_cd', 0) > game.turn or random.random() > .35 or not _line_ok(game, mon):
        return False
    mon.spit_cd = game.turn + 4
    game.flash([(p.x, p.y)], (230, 210, 60), '*', .2)
    p.stamina = max(0, p.stamina - (8 + mon.lvl // 2))
    game.msg(f'{mon.the().capitalize()} spits a gob of sulphur at you. You choke and gasp for breath.', 'bad')
    game.hurt(max(1, mon.dmg[0] // 2), mon.the(), 'poison')
    return True


def struck(game, mon, dmg):
    """You hit it up close: the slag brute burns you, the ashwalker puffs blinding ash."""
    from . import behave as BH
    p = game.player
    if dmg <= 0 or game.dead or cheb(mon.x, mon.y, p.x, p.y) > 1:
        return
    if BH.beh(mon, 'slag'):
        game.msg(f'{mon.the().capitalize()} is glowing hot. It burns you as you strike.', 'bad')
        game.hurt(max(1, mon.lvl // 2), mon.the(), 'fire')
    elif BH.beh(mon, 'ash') and random.random() < .4 and not BH.has(game, 'blinded'):
        BH.give(game, 'blinded', 2, 'A cloud of ash puffs up from the blow, and you cannot see!')


def incoming(game, mon, dmg, elem):
    """Frost makes the slag brute brittle; then every blow does double."""
    from . import behave as BH
    if not BH.beh(mon, 'slag'):
        return dmg
    if elem == 'cold':
        if not getattr(mon, 'brittle', 0):
            game.msg(f'The cold cracks {mon.the()}: it is brittle now!', 'good')
        mon.brittle = 6
    elif getattr(mon, 'brittle', 0):
        dmg *= 2
    return dmg


def died(game, mon):
    """A cinderling dies into burning ground."""
    from . import spellmap as SM
    from . import behave as BH
    if BH.beh(mon, 'cinders'):
        SM.place(game, game.map, mon.x, mon.y, D.BURNING, 8, max(2, mon.lvl // 2))
