"""Sailing: hire a passage at the quay (no ship of your own). A skipper on every harbour's waterfront takes you
along the coast: a fishing boat from any harbour on short hops, a coaster between villages and bigger places, a
merchant ship only between the cities with a deep berth. Days pass on the voyage and your cargo comes along. Winter
keeps the boats in more often and pack ice locks the northern harbours. On some voyages pirates come alongside:
fight them on deck or hand over the cargo; an armed escort costs more and almost nobody tries it. One or two pirate
coves lie hidden on the coast, with a fence, a tavern and the captain: trade there, or root them out."""
import math
import random

from . import data as D
from .money import fmt
from .worldgen import cheb

TIER = {'hamlet': 0, 'village': 1, 'town': 2, 'city': 3, 'metropolis': 4}
SHIPS = {   # kind: name, lowest harbour tier at both ends, furthest reach (sea cells), cells a day, copper a cell,
            #       least fare, cargo it takes, chance of pirates
    'boat': dict(name='fishing boat', tier=0, reach=80, per_day=30, rate=5, least=60, cargo=12, risk=.12),
    'coaster': dict(name='coaster', tier=1, reach=200, per_day=45, rate=7, least=150, cargo=45, risk=.15),
    'merchant': dict(name='merchant ship', tier=3, reach=9999, per_day=60, rate=9, least=300, cargo=999, risk=.08),
}
ARMED = 1.6
COVE_NAMES = ["Gallows Cove", "Black Gull Inlet", "Rotten Mast Bay", "The Smugglers' Hole", "Redwater Cove"]
PIRATE, PIRATE_YOUNG = ('@', (220, 90, 70)), ('☺', (230, 180, 150))
CONTRABAND_PRICE = 4500       # copper: a load of smuggled spice, half its price in town


def tier(s):
    return TIER.get(s.kind, 0)


# ------------------------------------------------------------------ the world: coves
def place_coves(game):
    """One or two pirate coves, hidden on a lonely coast: a fjord, the mangroves or a reef islet if there is one."""
    from .sites import Site
    from .harbour import SEA_BIOMES
    w, om = game.world, game.maps['over']
    names = om.biome_names
    sea = {names.index(b) for b in SEA_BIOMES if b in names}
    good = {names.index(b) for b in ('fjord', 'mangrove', 'reef', 'cliff') if b in names}
    cands = []
    for i, t in enumerate(om.t):
        if not D.TILES[t].walk or t in (D.ROAD, D.TOWN, D.CITY, D.ENTR):
            continue
        x, y = i % om.w, i // om.w
        if not any(om.inb(x + dx, y + dy) and om.t[(y + dy) * om.w + x + dx] == D.WATER and om.biome[(y + dy) * om.w + x + dx] in sea
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            continue
        cands.append((0 if om.biome[i] in good else 1, random.random(), x, y))
    cands.sort()
    taken = [(s.x, s.y) for s in w.settlements] + [(s.x, s.y) for s in w.sites] + [(d.x, d.y) for d in w.dungeons.values()]
    n = 0
    for _k, _r, x, y in cands:
        if any(cheb(x, y, a, b) < 25 for a, b in taken) or any(cheb(x, y, c.x, c.y) < 100 for c in coves(game)):
            continue
        site = Site(len(w.sites), 'cove', x, y, COVE_NAMES[n % len(COVE_NAMES)])
        site.hidden, site.found = True, False
        w.sites.append(site)
        taken.append((x, y))
        n += 1
        if n >= 2:
            break


def coves(game):
    return [s for s in game.world.sites if s.kind == 'cove']


# ------------------------------------------------------------------ the skipper
def closed(game, s):
    """Why no ship sails from here today, or None: pack ice, or a sea too rough for the boats (more often in winter)."""
    from . import seasons as SE
    from .living import berth
    from .look import _h
    b = berth(game, s)
    if b is None:
        return 'There is no water deep enough here for anything bigger than a rowing boat.'
    om = game.maps['over']
    st = SE.Now(game)
    if SE.pack(om, b[1] * om.w + b[0], st) or (st.depth > .5 and s.y < om.h * .12):
        return 'The harbour is locked in ice. Nothing sails until the spring.'
    from . import calendar as CAL
    rough = {'winter': 4, 'autumn': 2}.get(CAL.season(game.day), 1)
    if _h(s.id, game.day, 41) % 10 < rough:
        return 'No ship goes out today. The sea is too rough; try again tomorrow.'
    return None


def routes(game, here):
    """(destination, ship kind, sea cells) for every passage from here, nearest first."""
    from .living import berth, sea_path, harbours
    a = berth(game, here)
    if a is None:
        return []
    out = []
    for s in harbours(game):
        if s.id == here.id or cheb(s.x, s.y, here.x, here.y) > 260:
            continue
        kinds = [k for k, v in SHIPS.items() if tier(here) >= v['tier'] and tier(s) >= v['tier']]
        if not kinds:
            continue
        b = berth(game, s)
        path = sea_path(game, a, b) if b else None
        if not path:
            continue
        kinds = [k for k in kinds if len(path) <= SHIPS[k]['reach']]
        if kinds:
            out.append((s, kinds[-1], len(path)))     # the biggest ship that runs there
    out.sort(key=lambda r: r[2])
    return out


def fare(kind, n, armed=False):
    v = SHIPS[kind]
    return round(max(v['least'], n * v['rate']) * (ARMED if armed else 1))


def days(kind, n):
    return max(1, round(n / SHIPS[kind]['per_day']))


def talk(game, npc):
    from . import events as EV
    here = game.here
    if here is None:
        return
    why = closed(game, here)
    if why:
        game.say(npc, why)
        return
    rs = routes(game, here)[:7]
    from . import skyseat as SK
    whirl = SK.opt(game, here)
    if not rs and not whirl:
        game.say(npc, 'Nothing sails from here to anywhere you would want to go.')
        return
    opts = [(f"{s.name}: {SHIPS[k]['name']}, {fmt(fare(k, n))}, {days(k, n)} day{'s' if days(k, n) > 1 else ''}",
             f'to:{s.id}:{k}:{n}') for s, k, n in rs] + whirl
    EV.ask(game, 'sail', npc.name, '"Where to? I know every skipper on this coast. Your cargo comes along, if the boat '
           'can take it."', opts + [('Ask about pirates', 'pirates'), ('Not today', 'bye')], npc=npc.id)


def r_sail(game, choice, ctx):
    from . import events as EV
    from . import economy as ECO
    p = game.player
    if choice == 'whirl':
        from . import skyseat as SK
        SK.whirl(game)
        return
    if choice == 'pirates':
        cv = [c for c in coves(game) if not getattr(c, 'found', False)]
        if not cv:
            game.msg('"Pirates? Somebody found their nest already. Fewer of them about, these days."')
            return
        from .engine import dir_name
        here = game.here
        c = min(cv, key=lambda c: cheb(c.x, c.y, here.x, here.y))
        game.msg(f'"They put in somewhere to the {dir_name(c.x - here.x, c.y - here.y)}, they say. Out of the way, '
                 'where nobody looks. Follow one of their ships, if you are tired of living."', 'info')
        return
    if choice.startswith('to:'):
        _t, sid, kind, n = choice.split(':')
        s, n = game.world.settlements[int(sid)], int(n)
        if ECO.cargo_weight(p) > SHIPS[kind]['cargo']:
            game.msg(f"A {SHIPS[kind]['name']} takes no more than {SHIPS[kind]['cargo']} weight of cargo. You carry too much.", 'bad')
            return
        EV.ask(game, 'sail', f"To {s.name}", f"A {SHIPS[kind]['name']}, {days(kind, n)} day{'s' if days(kind, n) > 1 else ''} at sea. "
               'An armed escort costs more; pirates leave armed ships alone.',
               [(f'Plain passage ({fmt(fare(kind, n))})', f'go:{sid}:{kind}:{n}:0'),
                (f'With an armed escort ({fmt(fare(kind, n, True))})', f'go:{sid}:{kind}:{n}:1'), ('Not now', 'bye')])
        return
    if choice.startswith('go:'):
        _g, sid, kind, n, armed = choice.split(':')
        sail(game, game.world.settlements[int(sid)], kind, int(n), armed == '1')


def sail(game, dest, kind, n, armed):
    p = game.player
    cost = fare(kind, n, armed)
    if p.gold < cost:
        game.msg(f'The passage costs {fmt(cost)}.', 'bad')
        return
    p.gold -= cost
    d = days(kind, n)
    if d > 1 and 'starpath' in p.__dict__.get('marks', {}):
        d -= 1                                      # you know the voyagers' star chart, and the skipper listens
    game.voyage = dict(dest=dest.id, kind=kind, days=d, armed=armed)
    game.msg(f"You go aboard the {SHIPS[kind]['name']} for {dest.name}.", 'info')
    risk = SHIPS[kind]['risk'] * (.12 if armed else 1)
    if any(cheb(c.x, c.y, dest.x, dest.y) < 80 for c in coves(game)):
        risk *= 1.5
    if random.random() < risk:
        game.end_turn(max(1, d // 2) * D.DAY_LEN // 2, quiet=True)
        if game.dead:
            return
        from . import events as EV
        EV.ask(game, 'pirates', 'Pirates!', 'A ship with a black sail comes up fast behind you. Grappling hooks fly over '
               'the rail. "Your cargo, or your lives!"',
               [('Fight them on deck', 'fight'), ('Hand over the cargo', 'yield')])
        return
    arrive(game)


def arrive(game, half=False):
    v = getattr(game, 'voyage', None)
    if not v:
        return
    game.voyage = None
    dest = game.world.settlements[v['dest']]
    d = v['days'] if not half else max(1, v['days'] - max(1, v['days'] // 2) // 2)
    game.msg(f"{d} day{'s' if d > 1 else ''} at sea. You come ashore at {dest.name}.", 'info')
    game.end_turn(d * D.DAY_LEN, quiet=True)
    if game.dead:
        return
    game.over_pos = (dest.x, dest.y)
    game.enter_town(dest.id)


def r_pirates(game, choice, ctx):
    p = game.player
    if choice == 'yield':
        lost = sum(p.cargo.values())
        p.cargo, p.cost_basis = {}, {}
        game.msg(f'The pirates carry off your cargo ({lost} loads) and let the ship go.' if lost else
                 'You have no cargo. The pirates take the ship\'s instead, curse you, and let you go.', 'bad')
        arrive(game, half=True)
    else:
        deck_fight(game)


# ------------------------------------------------------------------ the fight on deck
def deck_fight(game):
    """Two ships lashed together: yours below, theirs above, gangplanks between. No way off but the sea."""
    from .entities import GameMap, make_monster, make_npc
    W_, H_ = 48, 17
    m = GameMap('deck', 'wild', 'On deck', W_, H_, D.WATER)
    for y0, y1 in ((2, 6), (10, 14)):
        for y in range(y0, y1 + 1):
            for x in range(5, W_ - 5):
                edge = y in (y0, y1) or x in (5, W_ - 6)
                m.set(x, y, D.FENCE if edge else D.PLANK)
        for x in (8, 24, 40):
            m.set(x, (y0 + y1) // 2, D.BARREL)
    for x in (12, 23, 34):
        for y in range(6, 11):
            m.set(x, y, D.PLANK)                     # the gangplanks
    m.deck = True
    m.entry = (24, 12)
    m.lights = []
    for i in range(len(m.seen)):
        m.seen[i] = 1
    dest = game.world.settlements[game.voyage['dest']]
    lvl = max(2, game.world.danger_at(dest.x, dest.y) + 1)
    pid = game.new_id()
    spots = [(x, y) for y in range(3, 6) for x in range(7, W_ - 7) if m.tile(x, y) == D.PLANK]
    random.shuffle(spots)
    for k, (x, y) in enumerate(spots[:random.randint(4, 6)]):
        mon = make_monster(game, 'brigand' if k % 3 == 2 else 'bandit', x, y, lvl, 1 if k == 0 else 0)
        mon.name = 'The pirate captain' if k == 0 else 'A pirate' if k % 3 != 2 else 'A pirate with a crossbow'
        mon.awake, mon.pack = True, pid
        m.mons.append(mon)
    for x in (10, 30, 38):
        c = make_npc(game, 'A sailor', 'villager', '#b0c8d8', x, 13, False)
        c.flee = True
        m.mons.append(c)
    game.maps['deck'] = m
    game.cur = 'deck'
    game.player.x, game.player.y = m.entry
    game.msg('Steel out! The pirates swarm over the rail. Beat them, and the voyage goes on.', 'bad')
    game.compute_fov()


def on_turn(game):
    """After each turn on deck: once the pirates are beaten the ship sails on."""
    m = game.map
    if not getattr(m, 'deck', False) or game.dead:
        return
    if any(not o.is_npc for o in m.mons):
        return
    p = game.player
    loot = random.randint(80, 200)
    p.gold += loot
    game.msg(f'The last pirate goes over the side. In their ship you find {fmt(loot)}.', 'gold')
    cv = [c for c in coves(game) if not getattr(c, 'found', False)]
    if cv and random.random() < .4:
        c = random.choice(cv)
        from .folk import discover
        discover(game, c, 'Among the captain\'s things is a chart, a cove marked on it in red ink.')
    dest = game.world.settlements[game.voyage['dest']]
    game.cur = 'over'                                # at sea again, out of sight of land
    p.x, p.y = dest.x, dest.y
    game.maps.pop('deck', None)
    game.compute_fov()
    arrive(game, half=True)


def off_deck(game):
    game.msg('Only the grey sea out there. Fight, or go down with the ship.', 'bad')


# ------------------------------------------------------------------ the cove
def cove_map(game, site):
    """A pirate cove: a beach between rocks, shacks, a tavern, the fence's store, the captain's house, a pier with
    their ship at anchor."""
    from . import tribes as TR
    W_, H_ = 70, 32
    m = TR._new(site, W_, H_, D.ROCK)
    for y in range(H_):
        for x in range(W_):
            shore = 48 + int(3 * math.sin(y / 4))
            if x >= shore:
                m.set(x, y, D.WATER if x > shore + 2 else D.SHALLOW)
            elif x >= shore - 6:
                m.set(x, y, D.SAND)
            elif 4 < y < H_ - 4 and x > 6:
                m.set(x, y, D.GRASS if random.random() < .7 else D.SAND)
    for x in range(0, 10):                           # a path in from the land side
        m.set(x, H_ // 2, D.PATH)
    m.entry = (0, H_ // 2)

    def shack(x0, y0, w, h, door):
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                m.set(x, y, D.WALL if y in (y0, y0 + h - 1) or x in (x0, x0 + w - 1) else D.FLOOR)
        m.set(*door, D.DOOR)
    shack(12, 6, 10, 6, (16, 11))                    # the tavern
    for x in (14, 16, 18):
        m.set(x, 8, D.TABLE)
    m.set(20, 7, D.BARREL)
    shack(26, 6, 8, 5, (29, 10))                     # the fence's store
    m.set(31, 7, D.CHEST)
    shack(14, 20, 9, 6, (18, 20))                    # the captain's house
    shack(28, 21, 6, 5, (30, 21))                    # a shack for the crew
    m.set(32, 23, D.FURS)
    for x in range(42, 60):                          # the pier, and their ship at anchor
        m.set(x, H_ // 2, D.PLANK)
        m.set(x, H_ // 2 + 1, D.PLANK)
    for x in range(56, 66):
        for y in range(H_ // 2 - 4, H_ // 2 - 1):
            m.set(x, y, D.PLANK)
    TR.fire(m, 38, 16, r=5)
    m.inner = {(x, y) for x in range(10, W_) for y in range(H_)}
    m.gate = (10, H_ // 2)
    TR.who(game, m, 16, 9, PIRATE_YOUNG, 'The tavern keeper', job='tavern', flee=True, stay=True)
    TR.who(game, m, 30, 8, PIRATE_YOUNG, 'Grell the fence', job='trader', flee=True, stay=True)
    cap = TR.who(game, m, 18, 22, ('@', (240, 200, 90)), 'Captain Maud Varro', 'brigand', job='chief', stay=True)
    for x, y in ((40, 14), (36, 18), (45, 17), (24, 15), (52, 16), (30, 24)):
        TR.who(game, m, x, y, PIRATE, 'A pirate', random.choice(['bandit', 'bandit', 'brigand']), job='guard')
    m.chief = cap.id if cap else None
    m.centre = (30, 16)
    return m


def cove_talk(game, npc, site):
    """The tavern, the fence and the captain. True if handled."""
    from . import events as EV
    from . import tradegoods as TG
    job = getattr(npc, 'tjob', '')
    if job == 'tavern':
        EV.ask(game, 'cove', npc.name, '"Rum, and a bed in the back. Nobody asks your name; nobody tells it."',
               [(f'A drink and a bed ({fmt(30)})', 'rest'), ('Goodbye', 'bye')], npc=npc.id)
        return True
    if job == 'trader':
        EV.ask(game, 'cove', npc.name, '"Anything that fell off a ship, I buy. Anything that never paid a toll, I sell."',
               [('See the goods', 'shop'), (f'Buy a load of smuggled spice ({fmt(CONTRABAND_PRICE)})', 'spice')] +
               TG.cove_opts(game) + [('Goodbye', 'bye')], npc=npc.id)
        return True
    if job == 'chief':
        EV.ask(game, 'cove', npc.name, '"Drink, trade, and keep your blade in its sheath. The cove is free to anyone who '
               'keeps their mouth shut in the towns."', [('Leave her be', 'bye'), ('Draw steel: root them out', 'attack')],
               npc=npc.id)
        return True
    return False


def r_cove(game, choice, ctx):
    from . import tribes as TR
    from . import economy as ECO
    p, m = game.player, game.map
    site = game.world.sites[m.site]
    if choice == 'lotus':
        from . import tradegoods as TG
        TG.cove_sell(game)
        return
    if choice == 'attack':
        TR.rouse(game, m, 'attack')
    elif choice == 'shop':
        key = f'tribe{site.id}'
        if game.day - getattr(site, 'stock_day', -99) >= 5 or key not in game.shops:
            from .worldgen import gen_shop
            site.stock_day = game.day
            game.shops[key] = gen_shop(game)
        game.request = ('shop', key)
    elif choice == 'spice':
        if p.gold < CONTRABAND_PRICE:
            game.msg(f'A load costs {fmt(CONTRABAND_PRICE)}.', 'bad')
        elif ECO.free_cargo(p) < D.GOODS['spice']['w']:
            game.msg('You have no room for it.', 'bad')
        else:
            p.gold -= CONTRABAND_PRICE
            have = p.cargo.get('spice', 0)
            p.cost_basis['spice'] = (p.cost_basis.get('spice', 0) * have + CONTRABAND_PRICE) / (have + 1)
            p.cargo['spice'] = have + 1
            game.msg('Grell rolls out a small cask that smells of cinnamon. "Never saw me."', 'gold')
    elif choice == 'rest':
        if p.gold < 30:
            game.msg('Thirty copper, friend.', 'bad')
            return
        p.gold -= 30
        game.msg('Rum, a straw bed and the sound of the sea. You sleep like the dead.', 'good')
        game.end_turn(D.DAY_LEN // 3, quiet=True)
        p.life = game.stats()['max_life']


def register():
    from . import events as EV
    EV.RESOLVERS['sail'] = r_sail
    EV.RESOLVERS['pirates'] = r_pirates
    EV.RESOLVERS['cove'] = r_cove


register()
