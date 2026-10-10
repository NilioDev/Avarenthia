"""Markets, cargo and news events. Prices follow stock: what a town has plenty of is cheap,
what it lacks is dear. Stocks drift back toward their normal level every day, caravans and
the player move goods around, and events shift what a town needs for a while."""
import random

from . import data as D

REF = 40.0


def init_markets(world):
    for s in world.settlements:
        prod, dem = D.CITY_TRADE if s.is_city else D.BIOME_TRADE[s.biome]
        n = 3 if s.is_city else 2
        s.produce = random.sample(prod, min(len(prod), n))
        if s.id == 0:
            s.produce = ['grain', 'ale']
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


def price(s, g):
    stock = max(1.0, s.market[g][0])
    f = (REF / stock) ** 0.55
    return D.GOODS[g]['base'] * max(.35, min(3.2, f))


def buy_price(s, g):
    return max(1, round(price(s, g) * 1.08 * (1 - min(s.rep, 100) / 400)))


def sell_price(s, g):
    b = buy_price(s, g)
    return max(1, min(b - 1, round(price(s, g) * .92 * (1 + min(s.rep, 100) / 400))))


def cargo_capacity(p):
    return D.BASE_CARGO + sum(D.MOUNTS[k]['cap'] for k in p.mounts)


def cargo_weight(p):
    return sum(q * D.GOODS[g]['w'] for g, q in p.cargo.items()) + sum(pc['w'] for pc in p.parcels)


def free_cargo(p):
    return cargo_capacity(p) - cargo_weight(p)


def buy(game, s, g, n=1):
    p = game.player
    done = spent = 0
    for _ in range(n):
        pr = buy_price(s, g)
        if p.gold < pr or free_cargo(p) < D.GOODS[g]['w'] or s.market[g][0] < 1:
            break
        p.gold -= pr
        spent += pr
        s.market[g][0] -= 1
        p.cargo[g] = p.cargo.get(g, 0) + 1
        done += 1
    if done:
        have = p.cargo[g]
        old = p.cost_basis.get(g, 0) * (have - done)
        p.cost_basis[g] = (old + spent) / have
        game.msg(f"You buy {done} {D.GOODS[g]['name']} for {spent} gold.", 'gold')
    elif s.market[g][0] < 1:
        game.msg(f"{s.name} has no {D.GOODS[g]['name']} left to sell.", 'bad')
    elif free_cargo(p) < D.GOODS[g]['w']:
        game.msg('You have no room left for cargo. A pack mule or cart would help.', 'bad')
    else:
        game.msg('You cannot afford that.', 'bad')
    return done


def sell(game, s, g, n=1):
    p = game.player
    done = got = 0
    for _ in range(n):
        if p.cargo.get(g, 0) <= 0:
            break
        pr = sell_price(s, g)
        p.gold += pr
        got += pr
        s.market[g][0] += 1
        p.cargo[g] -= 1
        if p.cargo[g] <= 0:
            del p.cargo[g]
        done += 1
    if done:
        cost = p.cost_basis.get(g)
        note = ''
        if cost:
            profit = got - round(cost * done)
            note = f" ({'+' if profit >= 0 else ''}{profit} profit)"
            if g not in p.cargo:
                p.cost_basis.pop(g, None)
        game.msg(f"You sell {done} {D.GOODS[g]['name']} for {got} gold{note}.", 'gold')
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


def daily(game):
    w = game.world
    for s in w.settlements:
        if s.event:
            key, left = s.event
            if left <= 1:
                ev = D.EVENTS[key]
                for g in (ev['good'], ev.get('also')):
                    if g:
                        s.market[g][1] = s.market[g][2]
                s.event = None
                game.msg(f'News: life returns to normal in {s.name}.', 'info')
            else:
                s.event = (key, left - 1)
        for g, m in s.market.items():
            m[0] += (m[1] - m[0]) * .15 + random.gauss(0, max(1.0, m[1] * .03))
            m[0] = max(0.0, m[0])
    if random.random() < .25:
        cands = [s for s in w.settlements if not s.event]
        if cands:
            s = random.choice(cands)
            key = random.choice(list(D.EVENTS))
            ev = D.EVENTS[key]
            s.event = (key, random.randint(5, 9))
            for g in (ev['good'], ev.get('also')):
                if g:
                    s.market[g][1] = ev['target']
            if key in ('famine', 'festival', 'plague', 'collapse', 'war', 'fire'):
                for g in (ev['good'], ev.get('also')):
                    if g:
                        s.market[g][0] = min(s.market[g][0], ev['target'] * 2)
            game.msg('News: ' + ev['text'].format(town=s.name), 'info')
