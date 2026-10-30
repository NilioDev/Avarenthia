"""Trade part 2 (round 22): goods and ways. Builds on economy.py.

- Goods with a name: each world picks 12 to 15 famous goods of a region (Amber Coast Wine, Thornwood Mead, a hold's
  stout), dearer than the plain good and best sold far from home; the maker has only a few. Good and bad years each
  new year: a hail summer makes one dear, a fine year a famous vintage. Every kind can come from several regions.
- Master makers: in three or four towns a master makes a few masterworks a season (a silver cup, a tapestry, a dress
  sword). Trade goods, not gear. Cities ask for them on their boards.
- Far goods (silk, incense, porcelain, dyes) come only by sea to the harbour cities and by the caravans of the south.
- Barter with peoples who keep no coin: kobolds, orcs and elves give goods sold nowhere else.
- Monster goods: an alchemist in a city pays double for beast parts.
- Spoiling: fruit, fish and the like go off on the road; salt in the cargo slows it.
- Need far away: a snowed-in village or a besieged city pays three times as much for what it lacks.
- Contraband: black lotus from the swamps; the Watch searches at town gates; the cove pays well.
- War trade: arms are dear in a realm at war; selling to both sides costs standing when it comes out.
- Market news at the inn, a few days old. Rank with the Merchant League by the profit you make.
Per-world state lives on world.trade; what is yours (League profit, who you sold arms to) on the player."""
import random

from . import data as D
from . import economy as ECO
from . import news as NW
from .money import fmt

# good, name, where it can be made, how much dearer, spoils
NAMED = [
    ('wine', '{a} Wine', 'warm', 2.2, False), ('wine', '{a} Red', 'south', 2.0, False),
    ('ale', '{s} Stout', 'hold', 2.2, False), ('ale', '{a} Brown Ale', 'grass', 1.8, False),
    ('honey', '{a} Mead', 'forest', 2.4, False), ('herbs', '{a} Pipe-weed', 'halfling', 2.5, False),
    ('wool', '{a} Wool', 'hills', 2.0, False), ('cloth', '{s} Linen', 'grass', 1.8, False),
    ('furs', '{a} Sable', 'cold', 2.5, False), ('fish', '{a} Smoked Eel', 'wet', 2.0, True),
    ('fruit', '{a} Cider', 'grass', 2.0, True), ('salt', '{a} Rock Salt', 'hills', 1.8, False),
    ('tools', '{s} Steel', 'hold', 1.8, False), ('spice', '{a} Saffron', 'south', 2.0, False),
    ('gems', '{a} Amber', 'coast', 1.6, False), ('timber', '{a} Black Oak', 'forest', 2.0, False),
    ('medicine', '{s} Theriac', 'city', 2.0, False), ('cloth', '{s} Lace', 'city', 2.5, False),
    ('furs', '{a} Wolfskins', 'cold', 1.8, False), ('honey', '{a} Heather Honey', 'hills', 2.0, False),
]
MASTER = [('{s} Silver Cup', 160, 1), ('{s} Tapestry', 220, 2), ('{s} Dress Sword', 260, 2), ('{s} Gold Brooch', 180, 1)]
FAR = {'silk': dict(name='Silk', base=70, w=1), 'incense': dict(name='Incense', base=55, w=1),
       'porcelain': dict(name='Porcelain', base=90, w=2), 'dyes': dict(name='Dyes', base=45, w=1)}
BARTERED = {'glowcap': dict(name='Glowcap Mushrooms', base=45, w=1), 'orchides': dict(name='Orc-Tanned Hides', base=50, w=2),
            'moonsilk': dict(name='Moonsilk', base=110, w=1)}
CONTRA = {'lotus': dict(name='Black Lotus', base=60, w=1)}
# a people: (whose site kinds, what they want in your cargo and how many, what they give and how many)
BARTER = {'kobolds': (('gems', 2), ('glowcap', 4)), 'warcamp': (('salt', 6), ('orchides', 4)),
          'glade': (('salt', 5), ('moonsilk', 2))}
PERISH = {'fruit', 'fish'}
NEED = {'snow': ('grain', 'is snowed in'), 'siege': ('medicine', 'is under siege')}
LEAGUE = [(0, None), (50000, 'Associate'), (250000, 'Member'), (1000000, 'Master Trader'), (3000000, 'Merchant Prince')]
SEARCH = .3
REF_UNITS = 3            # extra goods: three in stock is the plain price; more is cheap, fewer dear


def st(world):
    w = world
    if getattr(w, 'trade', None) is None:
        w.trade = dict(named={}, need={}, year=None)
    return w.trade


def extras():
    """Every good beyond the nineteen plain ones that is in play now."""
    return [g for g in D.GOODS if g not in D.GOOD_ORDER]


def is_extra(g):
    return g in D.GOODS and g not in D.GOOD_ORDER


# ------------------------------------------------------------------ making them, once per world
def _where(world, s, cond):
    from .world import WORLD_H
    lat = s.y / WORLD_H
    return {'warm': lat > .55 and s.biome in ('grass', 'hills', 'coast'), 'south': lat > .65,
            'hold': s.kind == 'deephold', 'grass': s.biome == 'grass' and s.kind != 'deephold',
            'forest': s.biome == 'forest', 'halfling': getattr(s, 'race', '') == 'halfling',
            'hills': s.biome == 'hills' and s.kind != 'deephold', 'cold': lat < .3,
            'wet': s.biome in ('swamp', 'coast'), 'coast': s.biome == 'coast' or getattr(s, 'harbour', False),
            'city': s.is_city}[cond]


def _area(world, s):
    from .lands import area_at
    a = area_at(world, s.x, s.y)
    if a:
        return a[4:] if a.startswith('The ') else a
    return world.region_at(s.x, s.y).name if hasattr(world, 'region_at') else s.name


def init(world, seed):
    """Pick this world's named goods and master works, and stock every market with the extra goods."""
    rnd = random.Random(seed * 4111 + 3)
    T = st(world)
    T['named'] = {}
    setts = [s for s in world.settlements if s.market]
    used, names = set(), set()
    rows = NAMED[:]
    rnd.shuffle(rows)
    want = rnd.randint(12, 15)
    for good, pat, cond, mult, perish in rows:
        if len(T['named']) >= want:
            break
        homes = [s for s in setts if s.id not in used and _where(world, s, cond)]
        if not homes:
            continue
        s = rnd.choice(homes)
        name = pat.format(a=_area(world, s), s=s.name)
        if name in names or len(name) > 25:
            continue
        used.add(s.id)
        names.add(name)
        k = f'n{len(T["named"])}'
        T['named'][k] = dict(name=name, good=good, base=round(D.GOODS[good]['base'] * mult), w=D.GOODS[good]['w'],
                             home=s.id, hx=s.x, hy=s.y, perish=perish, kind='named', f=1.0)
    towns = [s for s in setts if s.kind in ('town', 'city') and s.id not in used]
    rnd.shuffle(towns)
    towns = [s for s in towns if len(s.name) <= 12]
    for (pat, base, w), s in zip(MASTER[:rnd.randint(3, 4)], towns):
        k = f'n{len(T["named"])}'
        T['named'][k] = dict(name=pat.format(s=s.name), good=None, base=base, w=w, home=s.id, hx=s.x, hy=s.y,
                             perish=False, kind='master', f=1.0)
    install(world)
    for s in world.settlements:
        if not s.market:
            continue
        for g in extras():
            stock(world, s, g)
    years(world, rnd, quiet=True)


def install(world):
    """Put this world's goods into the table of goods (after making or loading a world)."""
    for g in [g for g in D.GOODS if g not in D.GOOD_ORDER]:
        del D.GOODS[g]
    for k, v in {**FAR, **BARTERED, **CONTRA}.items():
        D.GOODS[k] = dict(v, kind='far' if k in FAR else 'barter' if k in BARTERED else 'contra')
    for k, v in st(world)['named'].items():
        D.GOODS[k] = dict(v)
    for g in extras():
        D.GOODS[g]['ref'] = REF_UNITS * ECO.step(g)


def stock(world, s, g):
    """The normal stock of an extra good in a market: a few where it is made, almost none elsewhere."""
    gd = D.GOODS[g]
    one = ECO.step(g)
    have = .9
    if gd['kind'] in ('named', 'master') and gd['home'] == s.id:
        have = 6 if gd['kind'] == 'named' else 2.5
    elif gd['kind'] == 'far' and (getattr(s, 'harbour', False) and s.is_city or s.y > .8 * _h()):
        have = 8
    elif gd['kind'] == 'contra' and s.biome == 'swamp' and s.kind != 'deephold':
        have = 6
    t = have * one
    s.market[g] = [t, t, t]


def _h():
    from .world import WORLD_H
    return WORLD_H


# ------------------------------------------------------------------ prices
def factor(s, g):
    """What the trade of the world adds to a price: a named good's year and its road from home, need, war."""
    f = 1.0
    gd = D.GOODS.get(g)
    if gd and 'f' in gd:
        f *= gd['f']
        if gd.get('home') is not None and gd['home'] != s.id:
            d = max(abs(s.x - gd['hx']), abs(s.y - gd['hy']))
            f *= 1 + min(.4, d / 250)
    W = WORLD[0]
    if W is not None:
        n = st(W)['need'].get(s.id)
        if n and n[0] == g:
            f *= 3
        if g == 'arms' and at_war(W, s):
            f *= 1.6
    return f


WORLD = [None]


def at_war(world, s):
    from . import realms as RL
    R = getattr(world, 'realm', None)
    if not R or not R.wars:
        return None
    kg = RL.kingdom_of_region(R, s.region)
    if kg is None:
        return None
    for w in R.wars:
        if kg.id in (w['a'], w['b']):
            return (kg.id, w['b'] if kg.id == w['a'] else w['a'])
    return None


def refuse(game, s, g, selling):
    """A market that will not deal in a good: contraband in the open."""
    if g in CONTRA and (selling or s.biome != 'swamp'):
        return 'Nobody here will touch black lotus in the open. Try the cove.'
    return None


# ------------------------------------------------------------------ every day
def daily(game):
    w = game.world
    WORLD[0] = w
    T = st(w)
    spoil(game)
    for sid, (g, left) in list(T['need'].items()):
        if left <= 1:
            del T['need'][sid]
            s = w.settlements[sid]
            NW.post(game, 'trade', f'The road to {s.name} is open again.', s.x, s.y)
        else:
            T['need'][sid] = (g, left - 1)
    from . import calendar as CAL
    if random.random() < .06 and len(T['need']) < 2:
        winter = CAL.season(game.day) == 'winter'
        cands = []
        for s in w.settlements:
            if s.id in T['need'] or not s.market or s.id == 0:
                continue
            if winter and s.kind == 'village' and (s.y < .35 * _h() or s.biome == 'hills'):
                cands.append((s, 'snow'))
            elif s.is_city and at_war(w, s):
                cands.append((s, 'siege'))
        if cands:
            s, why = random.choice(cands)
            g, text = NEED[why]
            T['need'][s.id] = (g, random.randint(10, 16))
            s.market[g][0] = 0.0
            NW.post(game, 'trade', f'{s.name} {text}: they would pay three times over for {D.GOODS[g]["name"].lower()}, '
                    'if anyone gets through.', s.x, s.y)
    from . import seasons as SE
    if SE.doy(game.day) == 0 and T.get('year') != game.day:
        years(w, random, game=game)


def years(world, rnd, game=None, quiet=False):
    """A new year: each named good has a plain, a bad or a famous year."""
    T = st(world)
    T['year'] = game.day if game else 0
    for k, v in T['named'].items():
        if v['kind'] != 'named':
            continue
        r = rnd.random()
        v['f'], v['yr'] = (1.4, 'bad') if r < .18 else (1.25, 'good') if r < .33 else (1.0, None)
        if k in D.GOODS:
            D.GOODS[k]['f'], D.GOODS[k]['yr'] = v['f'], v['yr']
        home = world.settlements[v['home']]
        if home.market.get(k):
            t = ECO.step(k) * (3 if v['yr'] == 'bad' else 9 if v['yr'] == 'good' else 6)
            home.market[k][1] = home.market[k][2] = t
        if game and not quiet and v['yr']:
            NW.post(game, 'trade', (f'Hail spoiled the {v["name"]} this year. What there is will be dear.' if v['yr'] == 'bad'
                                    else f'This year\'s {v["name"]} is the best in memory. The great houses want it.'),
                    home.x, home.y)


def spoil(game):
    """Fruit, fish and their like go off in the cargo: faster in summer; salt slows it."""
    p = game.player
    from . import calendar as CAL
    rate = {'summer': .05, 'spring': .03, 'autumn': .03}.get(CAL.season(game.day), .015)
    salty = p.cargo.get('salt', 0)
    for g in [g for g in p.cargo if g in PERISH or D.GOODS.get(g, {}).get('perish')]:
        n = p.cargo[g]
        r = rate * (.4 if salty * 5 >= n else 1)
        lost = int(n * r + random.random())
        if lost:
            p.cargo[g] = n - min(n, lost)
            if not p.cargo[g]:
                del p.cargo[g]
                p.cost_basis.pop(g, None)
            game.msg(f'{min(n, lost)} of your {D.GOODS[g]["name"].lower()} has gone off.', 'bad')


# ------------------------------------------------------------------ after a sale: the League, war trade
def after_sell(game, s, g, n, got, profit):
    p = game.player
    if profit and profit > 0:
        before = rank(game)
        p.league_profit = getattr(p, 'league_profit', 0) + profit
        r = rank(game)
        if r > before:
            game.msg(f'Word of your trading reaches the Merchant League: they count you a {LEAGUE[r][1]} now.', 'gold')
            from . import chronicle as CH
            CH.add(game, 'Your deeds', f'The Merchant League counts you a {LEAGUE[r][1]}.', 'seen', key='league',
                   quiet=True)
    if g == 'arms':
        war = at_war(game.world, s)
        if war:
            sides = p.__dict__.setdefault('arms_to', set())
            sides.add(war[0])
            if war[1] in sides and random.random() < .3:
                from . import realms as RL
                from .war import change_rep
                sides.clear()
                game.msg('Word gets out that you sell arms to both sides of the war. Neither crown forgives it.', 'bad')
                for kid in war:
                    RL.add_favour(game, kid, -15)
                change_rep(game, 'league', -5)
                NW.post(game, 'war', 'A trader sold arms to both sides of the war, they say.', s.x, s.y)


def rank(game):
    v = getattr(game.player, 'league_profit', 0)
    return max(i for i, (need, _t) in enumerate(LEAGUE) if v >= need)


def league_discount(game):
    return .02 * rank(game)


# ------------------------------------------------------------------ the market list
def rows(game, s):
    """The goods in a market's list: the plain ones, and the extra ones that are here, in your cargo or wanted."""
    p = game.player
    T = st(game.world)
    out = list(D.GOOD_ORDER)
    for g in extras():
        if g not in s.market:
            stock(game.world, s, g)
        if ECO.units(s, g) >= 1 or p.cargo.get(g) or (T['need'].get(s.id, ('',))[0] == g):
            out.append(g)
    return out


def note(game, s, g):
    """A line on the selected good, for the foot of the market list."""
    gd = D.GOODS[g]
    T = st(game.world)
    bits = []
    if gd.get('kind') in ('named', 'master'):
        home = game.world.settlements[gd['home']]
        bits.append(f'made in {home.name}' + (', a masterwork' if gd['kind'] == 'master' else ''))
        if gd.get('yr') == 'bad':
            bits.append('a bad year: dear')
        elif gd.get('yr') == 'good':
            bits.append('a famous year')
    elif gd.get('kind') == 'far':
        bits.append('from far away, by sea or the southern caravans')
    elif gd.get('kind') == 'barter':
        bits.append('only by barter')
    elif gd.get('kind') == 'contra':
        bits.append('contraband')
    if g in PERISH or gd.get('perish'):
        bits.append('goes off on the road')
    if T['need'].get(s.id, ('',))[0] == g:
        bits.append('needed here badly')
    if g == 'arms' and at_war(game.world, s):
        bits.append('dear in a war')
    return '; '.join(bits)


def mark(game, s, g):
    gd = D.GOODS[g]
    if gd.get('kind') == 'contra':
        return '×'
    if gd.get('kind') in ('named', 'master', 'far', 'barter'):
        return '*'
    return None


# ------------------------------------------------------------------ the gate: the Watch searches
def at_gate(game, s):
    p = game.player
    n = p.cargo.get('lotus', 0)
    if not n or s.kind == 'village' or s.race in ('orc', 'goblin', 'lizardfolk'):
        return
    from . import classes as CL
    chance = SEARCH * (.5 if 'cunning' in CL.classes(game) else 1)
    if random.random() >= chance:
        return
    from . import crime as CR
    fine = min(p.gold, n * 300)
    p.gold -= fine
    del p.cargo['lotus']
    p.cost_basis.pop('lotus', None)
    game.msg(f'The Watch searches your cargo at the gate. They find the black lotus, take it, and fine you {fmt(fine)}.',
             'bad')
    CR.commit(game, 3, 'smuggling black lotus', witnessed=1.0)


def cove_opts(game):
    n = game.player.cargo.get('lotus', 0)
    return [(f'Sell your black lotus ({n} for {fmt(n * cove_price())})', 'lotus')] if n else []


def cove_price():
    return round(CONTRA['lotus']['base'] * 200)


def cove_sell(game):
    p = game.player
    n = p.cargo.pop('lotus', 0)
    p.cost_basis.pop('lotus', None)
    got = n * cove_price()
    p.gold += got
    game.msg(f'The fence sniffs the lotus, and counts out {fmt(got)} without a word.', 'gold')


# ------------------------------------------------------------------ barter
def barter_opts(game, kind):
    want, give = BARTER[kind]
    p = game.player
    ok = p.cargo.get(want[0], 0) >= want[1]
    return [(f'Barter: {want[1]} {D.GOODS[want[0]]["name"].lower()} for {give[1]} {D.GOODS[give[0]]["name"].lower()}',
             f'barter:{kind}' if ok and ECO.free_cargo(p) + want[1] * D.GOODS[want[0]]['w'] >= give[1] * D.GOODS[give[0]]['w']
             else None)]


def barter(game, kind):
    want, give = BARTER[kind]
    p = game.player
    if p.cargo.get(want[0], 0) < want[1]:
        return False
    p.cargo[want[0]] -= want[1]
    if not p.cargo[want[0]]:
        del p.cargo[want[0]]
        p.cost_basis.pop(want[0], None)
    p.cargo[give[0]] = p.cargo.get(give[0], 0) + give[1]
    game.msg(f'You trade {want[1]} {D.GOODS[want[0]]["name"].lower()} for {give[1]} {D.GOODS[give[0]]["name"].lower()}. '
             'Nobody else sells it.', 'gold')
    return True


# ------------------------------------------------------------------ monster goods: the alchemist of a city
def parts(game):
    return [i for i in game.player.inv if i.k == 'part']


def alchemist(game, npc):
    """In a city the herbalist buys beast parts at twice their worth, for the alchemists. True if asked."""
    here = game.here
    if not here or not here.is_city or not parts(game):
        return False
    from . import events as EV
    got = 2 * sum(i.value() * i.n for i in parts(game))
    EV.ask(game, 'alchemist', npc.name, '"Troll fat, scales, silk off a spider: the alchemists of this city buy all of '
           'it, and I buy for them."', [(f'Sell your beast parts ({fmt(got)})', 'sell'), ('Talk herbs', 'herbs'),
                                        ('Goodbye', 'bye')], npc=npc.id)
    return True


def r_alchemist(game, choice, ctx):
    npc = next((o for o in game.map.mons if o.id == ctx.get('npc')), None)
    if choice == 'sell':
        got = 2 * sum(i.value() * i.n for i in parts(game))
        for i in parts(game):
            game.player.inv.remove(i)
        game.player.gold += got
        game.msg(f'You sell your beast parts for {fmt(got)}.', 'gold')
    elif choice == 'herbs' and npc:
        from . import foraging as FG
        FG.herbalist_talk(game, npc)


# ------------------------------------------------------------------ market news at the inn
def inn_news(game, here, npc):
    """Once a day an inn has a carter or a drover with prices from far away, a few days old."""
    if getattr(here, 'news_day', -1) == game.day or random.random() < .4:
        return
    here.news_day = game.day
    far = [s for s in game.world.settlements if s.market and s.id != here.id and
           max(abs(s.x - here.x), abs(s.y - here.y)) > 30 and game.price_log.get(s.id, {}).get('day', -99) < game.day - 7]
    if not far:
        return
    s = random.choice(far)
    old = random.randint(2, 6)
    ECO.record_prices(game, s)
    game.price_log[s.id]['day'] = game.day - old
    dear = max(D.GOOD_ORDER, key=lambda g: ECO.sell_price(s, g) / max(1, D.GOODS[g]['base'] * 100))
    game.msg(f'A carter at the inn came from {s.name} {old} days ago: {D.GOODS[dear]["name"].lower()} was dear there. '
             'The market list remembers what he said.', 'info')


# ------------------------------------------------------------------ the factor: the League
def factor_opts(game):
    r = rank(game)
    return [('Your standing with the League', 'league')] + ([('A League caravan to guard', 'caravan')] if r >= 4 else [])


def r_factor(game, npc, choice):
    if choice == 'league':
        r = rank(game)
        v = getattr(game.player, 'league_profit', 0)
        nxt = next((need for need, _t in LEAGUE if need > v), None)
        text = (f'"The League counts you a {LEAGUE[r][1]}. ' if r else '"The League does not know your name yet. ') + \
               (f'Make {fmt(nxt - v)} more on your own account and they will hear of it."' if nxt else
                'There is no higher name we give."')
        if r:
            text += f' Better prices in every market: {2 * r} in a hundred.'
        game.say(npc, text)
        return True
    if choice == 'caravan':
        from .news import offer
        offer(game, npc, 'league', ['escort'], 2.0, '"A League caravan wants a guard it can trust:"')
        return True
    return False


# ------------------------------------------------------------------ master works ordered by a city
def make_order(game, s):
    from . import jobs as JB
    T = st(game.world)
    ms = [(k, v) for k, v in T['named'].items() if v['kind'] == 'master' and v['home'] != s.id]
    if not ms or not s.is_city:
        return None
    k, v = random.choice(ms)
    home = game.world.settlements[v['home']]
    who = random.choice(['The lord mayor', 'The high priest', 'A banker\'s widow', 'The baron\'s steward'])
    return JB.mission(game, s, 'masterwork', f'A {v["name"]} for {s.name}',
                      f'{who} of {s.name} wants a {v["name"]}, made by the master in {home.name}. Buy one there and '
                      'bring it here.', v['base'] * 1.6, (6, 10), game.day + 60, good=k)


def hand_in(game, m, sid):
    from . import missions as MS
    if m.giver != sid or m.state != 'active':
        return
    g = m.data['good']
    p = game.player
    if p.cargo.get(g, 0) >= 1:
        p.cargo[g] -= 1
        if not p.cargo[g]:
            del p.cargo[g]
            p.cost_basis.pop(g, None)
        game.msg(f'They unwrap the {D.GOODS[g]["name"]} with great care, and pay you well for it.', 'gold')
        MS.complete(game, m, [sid])
    else:
        game.msg(f'{game.world.settlements[sid].name} still waits for its {D.GOODS[g]["name"]}.', 'info')


def line(game, m):
    g = m.data['good']
    gd = D.GOODS.get(g)
    if not gd:
        return 'The master who made it is gone.'
    return f'Buy a {gd["name"]} in {game.world.settlements[gd["home"]].name} and bring it here.'


def register():
    from . import events as EV
    from . import jobs as JB
    EV.RESOLVERS['alchemist'] = r_alchemist
    JB.LABEL['masterwork'] = 'A masterwork'
    JB.KINDS.add('masterwork')
    JB.MAKE['masterwork'] = make_order
    if 'masterwork' not in JB.CITY:
        JB.CITY.append('masterwork')


register()
