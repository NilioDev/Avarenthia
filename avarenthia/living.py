"""A livelier world map. Where warbands clash a battlefield is left, with the dead and what they carried; a village
in a conquered region may be plundered and lie half burnt until it is rebuilt. A rival party of adventurers roams
from dungeon to dungeon: sometimes they get there first, sometimes you find their camp, sometimes their bodies.
Ferrymen take you over the rivers for a few coppers, even when the fords run high. Travellers leave offerings at
the crossroads shrines. And ships sail between the harbours, pirates among them."""
import random

from . import data as D
from .money import fmt
from .worldgen import cheb

BATTLE_DAYS = 40
PLUNDER_DAYS = 25
RIVAL_NAMES = ['the Silver Hawks', 'the Lantern Company', 'the Brothers Vey', 'the Grey Cloaks', 'the Ashford Five',
               'the Seven Spoons', 'the Wandering Shield', 'the Red Lark Band']
RIVAL_FG = (110, 220, 200)
SHIP_FG, PIRATE_FG, FERRY_FG = (230, 222, 200), (220, 70, 60), (190, 150, 90)
SHRINE_LOOK = ('Π', (232, 200, 110))
KINDS = ('rivals', 'ship', 'ferry')


# ------------------------------------------------------------------ battlefields
def battle(game, x, y, who):
    """Two forces fought here; the field stays for a while."""
    w = game.world
    w.battles = [b for b in getattr(w, 'battles', []) if game.day - b['day'] < BATTLE_DAYS][-11:]
    if any(cheb(b['x'], b['y'], x, y) <= 3 for b in w.battles):
        return
    w.battles.append(dict(x=x, y=y, day=game.day, who=who, looted=False, lvl=w.danger_at(x, y) + 2))


def battle_at(game, x, y, r=0):
    return next((b for b in getattr(game.world, 'battles', []) if cheb(b['x'], b['y'], x, y) <= r
                 and game.day - b['day'] < BATTLE_DAYS), None)


def battle_look(game, x, y):
    """The look of a battlefield cell (the centre and the ring round it), or None."""
    b = battle_at(game, x, y, 1)
    if not b:
        return None
    if (x, y) == (b['x'], b['y']):
        return '†', (200, 190, 176), (54, 22, 16)
    from .look import _h
    return ('x' if _h(x, y, 44) % 3 == 0 else ','), (150, 96, 74), (34, 16, 12)


def on_battlefield(game):
    """Walking onto the heart of a battlefield: take what the dead no longer need, once."""
    p = game.player
    b = battle_at(game, p.x, p.y)
    if not b or b['looted']:
        return
    b['looted'] = True
    from .entities import random_gear
    game.msg(f"The dead of {b['who']} lie where they fell. You take what is still of use.", 'info')
    coin = random.randint(20, 60) + b['lvl'] * 6
    p.gold += coin
    game.msg(f'{fmt(coin)} from the purses of the fallen.', 'gold')
    if random.random() < .6:
        it = random_gear(game, b['lvl'])
        if game.add_to_inv(it):
            game.msg(f'You take {it.display_name()}.', 'good')


# ------------------------------------------------------------------ plundered villages
def plunder(game, region, faction):
    """A region changes hands: one of its villages may be plundered on the way."""
    w = game.world
    cands = [s for s in w.settlements if s.region == region and s.id != 0 and not s.is_city
             and s.kind in ('hamlet', 'village') and not plundered(game, s)]
    if not cands or random.random() < .5:
        return
    s = random.choice(cands)
    s.plundered = game.day + PLUNDER_DAYS
    s.event = ('war', random.randint(6, 9))
    for g in ('grain', 'ale', 'cloth'):
        s.market[g][0] = min(s.market[g][0], 4)
    from . import news as NW
    NW.post(game, 'war', f"{s.name} was plundered by {D.FACTIONS[faction]['short']} troops. Half of it burned.", s.x, s.y)


def plundered(game, s):
    return getattr(s, 'plundered', 0) > game.day


def on_enter_town(game, s, m):
    """Burnt houses in a plundered village, cleared away again once it is rebuilt."""
    from .look import _h
    burnt = getattr(m, 'burnt_cells', None)
    if plundered(game, s):
        if burnt is None:
            over = getattr(m, 'over', None)
            if over is None:
                m.over = over = {}
            cells = []
            seeds = random.sample(range(len(m.t)), min(len(m.t), 8))
            for c in seeds:
                cx, cy = c % m.w, c // m.w
                for dy in range(-4, 5):
                    for dx in range(-5, 6):
                        x, y = cx + dx, cy + dy
                        if m.inb(x, y) and dx * dx / 25 + dy * dy / 16 < 1 and _h(x, y, 71) % 3:
                            i = y * m.w + x
                            if i in over:
                                continue
                            t = m.t[i]
                            if t in (D.WALL, D.FLOOR, D.GRASS, D.PATH, D.FIELD, D.FENCE):
                                ch = '#' if t == D.WALL else ',' if _h(x, y, 72) % 2 else '.'
                                over[i] = (ch, (84, 74, 66) if t == D.WALL else (70, 62, 56), (18, 14, 12))
                                cells.append(i)
            m.burnt_cells = cells
            m._look = None
        game.msg(f'{s.name} was plundered not long ago: burnt roofs, empty stalls. The folk are rebuilding.', 'bad')
    elif burnt:
        for i in burnt:
            m.over.pop(i, None)
        m.burnt_cells = None
        m._look = None
        game.msg(f'{s.name} has been rebuilt. New thatch shines on the roofs.', 'info')


# ------------------------------------------------------------------ rival adventurers
def spawn_rivals(game):
    from .wanderers import Wanderer
    w = game.world
    if any(x.kind == 'rivals' for x in w.wanderers) or getattr(w, 'rivals_back', 0) > game.day:
        return
    used = getattr(w, 'rival_names', [])
    names = [n for n in RIVAL_NAMES if n not in used] or RIVAL_NAMES
    s = random.choice([s for s in w.settlements if s.is_city] or w.settlements)
    wd = Wanderer(game.new_id(), 'rivals', s.x, s.y)
    wd.ch, wd.fg = '☻', RIVAL_FG
    wd.name = random.choice(names)
    w.rival_names = used + [wd.name]
    wd.speed = 11
    wd.camp = 0
    w.wanderers.append(wd)
    next_dungeon(game, wd)


def next_dungeon(game, wd):
    """The rivals pick a dungeon nobody has cleared yet, not too far off."""
    from .world import dijkstra_path
    w, om = game.world, game.maps['over']
    cands = [d for d in w.dungeons.values() if not getattr(d, 'rivals', None) and getattr(d, 'mine', None) is None
             and not getattr(d, 'hidden', False) and 15 < cheb(d.x, d.y, wd.x, wd.y) < 90
             and game.max_depth.get(d.id, 0) == 0]
    if not cands:
        return
    d = random.choice(cands)
    wd.path = dijkstra_path(om, (wd.x, wd.y), (d.x, d.y), lambda t: D.TILES[t].cost if D.TILES[t].walk else None) or []
    wd.path_i, wd.target = 0, d.id


def step_rivals(game, wd):
    w = game.world
    if getattr(wd, 'camp', 0) > 0:
        wd.camp -= 1
        if wd.camp == 0:
            next_dungeon(game, wd)
        return
    if wd.path_i < len(wd.path):
        nx, ny = wd.path[wd.path_i]
        p = game.player
        if game.cur == 'over' and (nx, ny) == (p.x, p.y):
            return
        wd.x, wd.y = nx, ny
        wd.path_i += 1
        return
    d = w.dungeons.get(getattr(wd, 'target', None))
    if d is None:
        next_dungeon(game, wd)
        return
    from . import news as NW
    r = random.random()
    if r < .5:
        d.rivals = 'cleared'
        NW.post(game, 'rumour', f'{wd.name[0].upper() + wd.name[1:]} came back from {d.name} with full packs.', d.x, d.y)
        wd.camp = random.randint(18, 30)                # a camp by the way in while they count the loot
    elif r < .75:
        d.rivals = 'dead'
        d.rival_name = wd.name
        w.wanderers.remove(wd)
        w.rivals_back = game.day + random.randint(10, 20)
        NW.post(game, 'rumour', f'{wd.name[0].upper() + wd.name[1:]} went into {d.name} and never came out.', d.x, d.y)
    else:
        wd.camp = random.randint(18, 30)
        wd.target = None
        next_dungeon(game, wd)


def talk_rivals(game, wd):
    from . import events as EV
    d = game.world.dungeons.get(getattr(wd, 'target', None))
    if getattr(wd, 'camp', 0) > 0:
        line = ('"Sit down, sit down. There is stew. ' + (f'We are for {d.name} next. Do not even think of it."'
                if d else 'We have done well this season. Better than you, by the look of you."'))
    elif d:
        line = f'"Off to {d.name}, friend. If you were thinking of it, you are too late."'
    else:
        line = '"Every hole in this land, we have been down it. Or we will."'
    EV.ask(game, 'rivals', wd.name[0].upper() + wd.name[1:], line + '\n\nA party of adventurers, armed to the teeth. '
           'They go after the same dungeons as you.', [('Goodbye', 'bye')])


def on_dungeon_level(game, dg, m, depth):
    """A level the rivals got to first: most of its monsters dead, the chests open; or their bodies by the stairs."""
    what = getattr(dg, 'rivals', None)
    if what == 'cleared':
        m.mons = [o for o in m.mons if o.is_npc or getattr(o, 'is_boss', False) or random.random() < .3]
        for i, t in enumerate(m.t):
            if t == D.CHEST:
                m.t[i] = D.CHEST_OPEN
        m.items = [it for it in m.items if it.k in ('quest', 'relic', 'tome') or random.random() < .3]
        if depth == 1:
            game.msg('Someone was here before you: chalk marks on the walls, the dead left where they fell.', 'info')
    elif what == 'dead' and depth == 1 and not getattr(dg, 'bodies_laid', False):
        dg.bodies_laid = True
        from .entities import random_gear, Item
        from .worldgen import free_around
        up = m.t.index(D.UP) if D.UP in m.t else None
        if up is None:
            return
        spots = free_around(game, m, up % m.w, up // m.w, 3)
        for k, (x, y) in enumerate(spots[:3]):
            it = random_gear(game, dg.base + 2) if k < 2 else Item(game.new_id(), 'gold', 'gold', random.randint(40, 120))
            it.x, it.y = x, y
            m.items.append(it)
        game.msg(f"Bodies lie by the stairs: {getattr(dg, 'rival_name', 'a party of adventurers')}, who got no further.",
                 'bad')


# ------------------------------------------------------------------ ferries
def place_ferries(game):
    """A ferryman on a few rivers, near the towns and away from the bridges."""
    from .wanderers import Wanderer
    from .world import scaled
    w, om = game.world, game.maps['over']
    w.ferries = []
    tries = 0
    while len(w.ferries) < scaled(5) and tries < 4000:
        tries += 1
        s = random.choice(w.settlements)
        x, y = s.x + random.randint(-22, 22), s.y + random.randint(-22, 22)
        if not om.inb(x, y) or om.tile(x, y) != D.RIVER:
            continue
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            bank, far = (x - dx, y - dy), far_bank(om, x, y, dx, dy)
            if far and om.inb(*bank) and om.tile(*bank) in (D.GRASS, D.FOREST, D.HILLS, D.SWAMP, D.SAND) \
                    and not any(cheb(f[0], f[1], *bank) < 30 for f in w.ferries) \
                    and not any(om.tile(bank[0] + a, bank[1] + b) == D.ROAD for a in range(-6, 7) for b in range(-6, 7)
                                if om.inb(bank[0] + a, bank[1] + b)):
                wd = Wanderer(game.new_id(), 'ferry', *bank)
                wd.ch, wd.fg, wd.name = '≡', FERRY_FG, 'A ferryman'
                wd.far, wd.speed = far, 99
                w.wanderers.append(wd)
                w.ferries.append(bank)
                break


def far_bank(m, x, y, dx, dy):
    """The land on the other side of the river, going in direction (dx, dy) from river cell (x, y)."""
    for _ in range(6):
        if not m.inb(x, y):
            return None
        if m.tile(x, y) != D.RIVER:
            return (x, y) if D.TILES[m.tile(x, y)].walk and m.tile(x, y) not in (D.TOWN, D.CITY) else None
        x, y = x + dx, y + dy
    return None


def talk_ferry(game, wd):
    from . import events as EV
    from . import seasons as SE
    st = SE.Now(game)
    om = game.maps['over']
    fx, fy = wd.far
    across = [(x, y) for x in range(min(wd.x, fx), max(wd.x, fx) + 1) for y in range(min(wd.y, fy), max(wd.y, fy) + 1)
              if om.tile(x, y) == D.RIVER]
    if across and all(SE.frozen(om, y * om.w + x, st) for x, y in across):
        game.msg('The ferryman shrugs at the ice. "Walk across. Nobody pays me in winter."')
        return
    high = any(SE.spate(om, y * om.w + x, st) for x, y in across)
    fare = 8 if high else 3
    EV.ask(game, 'ferry', 'The ferryman', ('"High water, but she floats. Costs more, mind." ' if high else
                                           '"Over the river? Sit in the middle and don\'t lean."') +
           f'\n\nThe fare is {fmt(fare)}.', [(f'Cross ({fmt(fare)})', 'cross'), ('Not now', 'bye')], wd=wd.id, fare=fare)


def r_ferry(game, choice, ctx):
    if choice != 'cross':
        return
    p = game.player
    wd = next((x for x in game.world.wanderers if x.id == ctx['wd']), None)
    if not wd:
        return
    if p.gold < ctx['fare']:
        game.msg('You cannot pay the fare.', 'bad')
        return
    p.gold -= ctx['fare']
    p.x, p.y = wd.far
    game.msg('The ferry creaks over the water on its rope. You step off on the far bank.', 'info')
    game.end_turn(12)


# ------------------------------------------------------------------ crossroads shrines
def place_shrines(game):
    """Small shrines where roads meet, away from the towns."""
    from .world import scaled
    w, om = game.world, game.maps['over']
    w.crossroads = []
    road = D.ROAD
    cells = [i for i, t in enumerate(om.t) if t == road]
    random.shuffle(cells)
    for i in cells:
        x, y = i % om.w, i // om.w
        arms = sum(1 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1))
                   if om.inb(x + dx, y + dy) and om.tile(x + dx, y + dy) == road)
        if arms < 3 or any(cheb(s.x, s.y, x, y) < 8 for s in w.settlements):
            continue
        if any(cheb(c['x'], c['y'], x, y) < 30 for c in w.crossroads):
            continue
        w.crossroads.append(dict(x=x, y=y, offer=random.randint(10, 40)))
        if len(w.crossroads) >= scaled(6):
            break


def shrine_at(game, x, y):
    return next((c for c in getattr(game.world, 'crossroads', []) if (c['x'], c['y']) == (x, y)), None)


def on_shrine(game, c):
    from . import events as EV
    EV.ask(game, 'crossroads', 'A crossroads shrine', 'A small shrine where the roads meet: a carved post under a little '
           'roof, ribbons, and a bowl. Travellers leave a few coins for a safe road.' +
           (f' There is about {fmt(c["offer"])} in the bowl.' if c['offer'] else ' The bowl is empty.'),
           [(f'Leave an offering ({fmt(10)})', 'give'), ('Take the offerings', 'take'), ('Walk on', 'bye')],
           x=c['x'], y=c['y'])


def r_crossroads(game, choice, ctx):
    p = game.player
    c = shrine_at(game, ctx['x'], ctx['y'])
    if not c:
        return
    if choice == 'give':
        if p.gold < 10:
            game.msg('You have not even that much.', 'bad')
            return
        p.gold -= 10
        c['offer'] += 10
        p.buffs = [b for b in p.buffs if b[0] not in ('safe_road', 'ill_luck')] + [['safe_road', 1, D.DAY_LEN * 2, 'A safe road']]
        game.msg('You drop the coins in the bowl. The road ahead feels a little kinder.', 'good')
    elif choice == 'take':
        got = c['offer']
        c['offer'] = 0
        p.gold += got
        p.buffs = [b for b in p.buffs if b[0] != 'safe_road'] + [['ill_luck', 1, D.DAY_LEN * 5, 'Ill luck on the road']]
        game.msg(f'You empty the bowl: {fmt(got)}. A cold wind gets up along the road.' if got else
                 'There is nothing to take. A cold wind gets up along the road all the same.', 'bad')


def ambush_factor(game):
    """A gift at the shrine keeps the road safer; a theft brings ill luck."""
    k = 1.0
    for b in game.player.buffs:
        if b[0] == 'safe_road':
            k *= .5
        elif b[0] == 'ill_luck':
            k *= 2
    return k


# ------------------------------------------------------------------ ships at sea
def sea_cells(om):
    from .harbour import SEA_BIOMES
    names = om.biome_names
    ids = {names.index(b) for b in SEA_BIOMES if b in names}
    return lambda i: om.t[i] == D.WATER and om.biome[i] in ids


def berth(game, s):
    """The sea cell nearest a harbour."""
    om = game.maps['over']
    sea = sea_cells(om)
    best = None
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            x, y = s.x + dx, s.y + dy
            if om.inb(x, y) and sea(y * om.w + x):
                d = abs(dx) + abs(dy)
                if best is None or d < best[0]:
                    best = (d, (x, y))
    return best[1] if best else None


def sea_path(game, a, b):
    """The way by sea from a to b (cells), or None. Cached on the world."""
    from collections import deque
    w = game.world
    w.sea_paths = getattr(w, 'sea_paths', {})
    if (a, b) in w.sea_paths:
        return w.sea_paths[(a, b)]
    om = game.maps['over']
    sea = sea_cells(om)
    W_ = om.w
    s, goal = a[1] * W_ + a[0], b[1] * W_ + b[0]
    prev = {s: -1}
    q = deque([s])
    while q:
        c = q.popleft()
        if c == goal:
            break
        x, y = c % W_, c // W_
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            nx, ny = x + dx, y + dy
            ni = ny * W_ + nx
            if 0 <= nx < W_ and 0 <= ny < om.h and ni not in prev and sea(ni):
                prev[ni] = c
                q.append(ni)
    out = None
    if goal in prev:
        out, c = [], goal
        while c != s:
            out.append((c % W_, c // W_))
            c = prev[c]
        out.reverse()
    w.sea_paths[(a, b)] = out
    return out


def harbours(game):
    return [s for s in game.world.settlements if getattr(s, 'harbour', False)]


def spawn_ship(game, pirate=False):
    from .wanderers import Wanderer
    hs = harbours(game)
    if len(hs) < 2:
        return
    from .sailing import coves
    cv = [c for c in coves(game)]
    for _ in range(6):
        a, b = random.sample(hs, 2)
        pa, pb = berth(game, a), berth(game, b)
        if pirate and cv:
            pa = berth(game, random.choice(cv))          # out of their cove: follow them home
        if not pa or not pb:
            continue
        path = sea_path(game, pa, pb)
        if not path or len(path) < 10:
            continue
        wd = Wanderer(game.new_id(), 'ship', *pa)
        wd.ch = 'Φ'
        wd.fg = PIRATE_FG if pirate else SHIP_FG
        wd.name = 'A pirate ship' if pirate else f'A merchant ship bound for {b.name}'
        if pirate and cv:
            path = list(reversed(path[:-1])) + [pa] + path      # from the cove out to a harbour, and back again
        wd.pirate = pirate
        wd.path, wd.path_i, wd.dest, wd.speed = path, 0, b.id, 7
        game.world.wanderers.append(wd)
        return wd


def step_ship(game, wd):
    if wd.path_i < len(wd.path):
        wd.x, wd.y = wd.path[wd.path_i]
        wd.path_i += 1
        return
    game.world.wanderers.remove(wd)


def daily(game):
    """Ships put to sea, the rivals set out again, old battlefields are picked clean."""
    w = game.world
    from .world import scaled
    while sum(1 for x in w.wanderers if x.kind == 'ship' and not x.pirate) < scaled(4):
        if not spawn_ship(game):
            break
    if not any(x.kind == 'ship' and x.pirate for x in w.wanderers) and random.random() < .5:
        spawn_ship(game, pirate=True)
    spawn_rivals(game)
    for c in getattr(w, 'crossroads', []):
        c['offer'] = min(120, c['offer'] + random.randint(0, 4))


def step(game, wd):
    if wd.kind == 'rivals':
        step_rivals(game, wd)
    elif wd.kind == 'ship':
        step_ship(game, wd)


def setup(game):
    """At the making of the world."""
    place_ferries(game)
    place_shrines(game)
    daily(game)


def talk(game, wd):
    """Walking into one of them on the world map. True if handled."""
    if wd.kind == 'rivals':
        talk_rivals(game, wd)
    elif wd.kind == 'ferry':
        talk_ferry(game, wd)
    elif wd.kind == 'ship':
        game.msg(wd.name + '.', 'info')
    else:
        return False
    return True


def describe(wd):
    if wd.kind == 'rivals':
        return f'{wd.name[0].upper() + wd.name[1:]}, a party of adventurers' + (', camped for a while.' if getattr(wd, 'camp', 0) else ' on the road.')
    if wd.kind == 'ferry':
        return 'A ferryman with his flat-bottomed ferry on a rope. Walk into him to cross.'
    if wd.kind == 'ship':
        return wd.name + ('. Keep well clear.' if wd.pirate else '.')
    return None


def r_rivals(game, choice, ctx):
    pass


def register():
    from . import events as EV
    EV.RESOLVERS['ferry'] = r_ferry
    EV.RESOLVERS['crossroads'] = r_crossroads
    EV.RESOLVERS['rivals'] = r_rivals


register()
