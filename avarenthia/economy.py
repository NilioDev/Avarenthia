"""Markets, cargo and news events. Prices follow stock: what a town has plenty of is cheap,
what it lacks is dear. Stocks drift back toward their normal level every day, caravans and
the player move goods around, and events shift what a town needs for a while."""
import random

from . import data as D
from . import news as NW
from .money import fmt

REF = 40.0
RESTOCK = .05                # each day stock comes back this share of the way to its normal level
TIRE_FORGET = .05            # each day a market forgets this share of what you sold it
TIRE_HALF = 90.0             # this much sold (in stock) and a market pays you only two thirds
faction_rep = lambda s: 0    # set by the game: the player's standing with a settlement's faction
race_factor = lambda s: 1.0  # set by the game: how the townsfolk's race feels about yours
today = lambda: 0            # set by the game: the day of the year, for the prices of the season


def _discount(s):
    return max(-.2, min(.3, min(s.rep, 100) / 400 + faction_rep(s) / 500))


def init_markets(world):
    for s in world.settlements:
        prod, dem = D.CITY_TRADE if s.is_city else D.BIOME_TRADE[s.biome]
        if s.kind == 'deephold':
            prod, dem = ['ore', 'arms', 'tools', 'gems'], ['grain', 'ale', 'timber', 'cloth', 'furs']
        n = 3 if s.is_city or s.kind == 'deephold' else 2
        s.produce = random.sample(prod, min(len(prod), n))
        if s.id == 0:
            s.produce = ['grain', 'ale']
        local = regional(world, s)
        if local and local not in s.produce:
            s.produce.append(local)
        s.demand = random.sample([g for g in dem if g not in s.produce], min(len([g for g in dem if g not in s.produce]), n + 1))
        if s.id == 0:
            s.demand = ['tools', 'salt', 'fish']
        for g in D.GOOD_ORDER:
            if g in s.produce:
                t = random.uniform(95, 140)
            elif g in s.demand:
                t = random.uniform(6, 13)
            else:
                t = random.uniform(24, 46)
            if s.is_city:
                t *= 1.3
            s.market[g] = [t, t, t]


def regional(world, s):
    """The good of the season this place makes, by where it lies: ice in the cold north, wine in the warm south,
    apples and cider in the middle lands, honey on the grass, wool in the hills."""
    from .world import WORLD_H
    lat = s.y / WORLD_H
    if lat < .25:
        return 'ice' if random.random() < .6 else 'furs'
    if lat > .7:
        return 'wine'
    if s.biome == 'hills':
        return 'wool'
    if s.biome == 'grass':
        return random.choice(['honey', 'fruit'])
    return 'fruit' if random.random() < .5 else None


def season_factor(g, doy=None):
    """Cheap at harvest, dear out of season: 1 - swing at the cheapest day, 1 + swing half a year later."""
    sv = D.SEASONAL.get(g)
    if not sv:
        return 1.0
    import math
    d = today() if doy is None else doy
    return 1 - sv[1] * math.cos(2 * math.pi * (d - sv[0]) / 360)


def in_season(doy):
    """(goods cheap now, goods dear now)."""
    f = {g: season_factor(g, doy) for g in D.SEASONAL}
    return [g for g, v in f.items() if v < .85], [g for g, v in f.items() if v > 1.15]


def step(g):
    """How far one of this good moves a market's stock: a gem far more than a sack of grain."""
    return max(1.0, (D.GOODS[g]['base'] / 12) ** .5)


def bend(g):
    """How hard the price follows the stock: the dearer the good, the harder."""
    return .55 + .2 * min(1.0, D.GOODS[g]['base'] / 120)


def units(s, g):
    """How many of this good a market has to sell."""
    return int(s.market[g][0] / step(g))


def price(s, g):
    stock = max(1.0, s.market[g][0])
    f = (REF / stock) ** bend(g)
    return D.GOODS[g]['base'] * max(.35, min(3.2, f)) * season_factor(g) * 100     # copper


def buy_price(s, g):
    return max(1, round(price(s, g) * 1.08 * (1 - _discount(s)) * race_factor(s)))


def sell_price(s, g, fair=False, tired=0.0):
    """What a town pays for one; on its market day (fair) a tenth more; less when you have sold it much of this
    good of late (tired: see tired())."""
    b = buy_price(s, g)
    return max(1, min(b - 1, round(price(s, g) * .92 * (1.1 if fair else 1) * (1 + _discount(s)) / race_factor(s)
                                   * tire_factor(tired))))


def tire_factor(tired):
    return 1 / (1 + tired / (2 * TIRE_HALF))


def tired(game, s, g):
    """What you have sold this market of this good of late, in stock; the market forgets it slowly."""
    return getattr(game.player, 'tired', {}).get(f'{s.id}:{g}', 0.0)


def fair_day(game, s):
    from . import towns as TW
    return game.here is s and TW.day_kind(game, s) == 'market'


def cargo_capacity(p):
    return D.BASE_CARGO + sum(D.MOUNTS[k]['cap'] for k in p.mounts) + (20 if getattr(p, 'race', '') == 'dwarf' else 0)


def cargo_weight(p):
    return sum(q * D.GOODS[g]['w'] for g, q in p.cargo.items()) + sum(pc['w'] for pc in p.parcels)


def free_cargo(p):
    return cargo_capacity(p) - cargo_weight(p)


def buy(game, s, g, n=1):
    p = game.player
    done = spent = 0
    for _ in range(n):
        pr = buy_price(s, g)
        if p.gold < pr or free_cargo(p) < D.GOODS[g]['w'] or units(s, g) < 1:
            break
        p.gold -= pr
        spent += pr
        s.market[g][0] -= step(g)
        p.cargo[g] = p.cargo.get(g, 0) + 1
        done += 1
    if done:
        have = p.cargo[g]
        old = p.cost_basis.get(g, 0) * (have - done)
        p.cost_basis[g] = (old + spent) / have
        game.msg(f"You buy {done} {D.GOODS[g]['name']} for {fmt(spent)}.", 'gold')
    elif units(s, g) < 1:
        game.msg(f"{s.name} has no {D.GOODS[g]['name']} left to sell.", 'bad')
    elif free_cargo(p) < D.GOODS[g]['w']:
        game.msg('You have no room left for cargo. A pack mule or cart would help.', 'bad')
    else:
        game.msg('You cannot afford that.', 'bad')
    return done


def sell(game, s, g, n=1):
    p = game.player
    done = got = 0
    if not hasattr(p, 'tired'):
        p.tired = {}
    key = f'{s.id}:{g}'
    for _ in range(n):
        if p.cargo.get(g, 0) <= 0:
            break
        pr = sell_price(s, g, fair_day(game, s), p.tired.get(key, 0.0))
        p.gold += pr
        got += pr
        s.market[g][0] += step(g)
        p.tired[key] = p.tired.get(key, 0.0) + step(g)      # the route tires: the market remembers you
        p.cargo[g] -= 1
        if p.cargo[g] <= 0:
            del p.cargo[g]
        done += 1
    if done:
        from .gods import on_craft
        on_craft(game, 'trade')
        cost = p.cost_basis.get(g)
        note = ''
        if cost:
            profit = got - round(cost * done)
            note = f" ({'+' if profit >= 0 else '-'}{fmt(abs(profit))} profit)"
            if g not in p.cargo:
                p.cost_basis.pop(g, None)
        game.msg(f"You sell {done} {D.GOODS[g]['name']} for {fmt(got)}{note}.", 'gold')
    return done


def record_prices(game, s):
    game.price_log[s.id] = {'day': game.day, 'buy': {g: buy_price(s, g) for g in D.GOOD_ORDER},
                            'sell': {g: sell_price(s, g) for g in D.GOOD_ORDER}}


def best_known_sale(game, g, exclude):
    best = None
    for sid, rec in game.price_log.items():
        if sid == exclude:
            continue
        v = rec['sell'][g]
        if not best or v > best[0]:
            best = (v, sid, rec['day'])
    return best


def melt(game):
    """Ice melts in your cargo on the way: fast in summer, slowly in spring and autumn, not at all in winter."""
    p = game.player
    n = p.cargo.get('ice', 0)
    if not n:
        return
    from . import calendar as CAL
    rate = {'summer': .12, 'spring': .05, 'autumn': .04}.get(CAL.season(game.day), 0)
    lost = int(n * rate + random.random()) if rate else 0
    if lost:
        p.cargo['ice'] = n - min(n, lost)
        if not p.cargo['ice']:
            del p.cargo['ice']
            p.cost_basis.pop('ice', None)
        game.msg(f'{min(n, lost)} of your ice has melted away.', 'bad')


def daily(game):
    w = game.world
    melt(game)
    p = game.player
    t = getattr(p, 'tired', None)
    if t:
        for k in list(t):
            t[k] *= 1 - TIRE_FORGET
            if t[k] < 1:
                del t[k]
    for s in w.settlements:
        if s.event:
            key, left = s.event
            if left <= 1:
                ev = D.EVENTS[key]
                for g in (ev['good'], ev.get('also')):
                    if g:
                        s.market[g][1] = s.market[g][2]
                s.event = None
                NW.post(game, 'trade', f'Life is back to normal in {s.name}; the prices too.', s.x, s.y)
            else:
                s.event = (key, left - 1)
        for g, m in s.market.items():
            m[0] += (m[1] - m[0]) * RESTOCK + random.gauss(0, max(1.0, m[1] * .02))
            m[0] = max(0.0, m[0])
    if random.random() < .25:
        cands = [s for s in w.settlements if not s.event]
        if cands:
            s = random.choice(cands)
            key = random.choice([k for k in D.EVENTS if k != 'undead'])
            ev = D.EVENTS[key]
            s.event = (key, random.randint(5, 9))
            for g in (ev['good'], ev.get('also')):
                if g:
                    s.market[g][1] = ev['target']
            if key in ('famine', 'festival', 'plague', 'collapse', 'war', 'fire'):
                for g in (ev['good'], ev.get('also')):
                    if g:
                        s.market[g][0] = min(s.market[g][0], ev['target'] * 2)
            NW.post(game, 'trade', ev['text'].format(town=s.name), s.x, s.y)
