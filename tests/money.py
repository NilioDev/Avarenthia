"""The money check ("Playing it" in docs/plan.md): a bot lives a set of days at level 1, 10 and 20 the way a player
earns and pays, with the game's own rewards and prices, and prints one table per level.

Earning, in turn: a job from the board (the reward; the days its road takes), a trade run between two towns (the best
good bought in one and sold in the other, as much as the cart holds; the days of the road), hunting (beasts of the
level's tier, their hides and meat sold to the outfitter) and a guard's wage (escort jobs).
Paying: a bed at the inn on a night in town, food on the road, mending what the fights wore, a hireling's wage from
level 10, and the temple's raising once.

    python tests/money.py [days] [seed]
    python tests/money.py --opening [worlds]     the day of the first tome, over that many worlds (round 40)

The part `money` of test_headless.py runs a short check and fails when a build leaves the BANDS below. The bands are
first guesses, to settle with Nilio after he has read the first tables."""
import math
import os
import random
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from avarenthia import engine as E, data as D  # noqa: E402
from avarenthia import economy as ECO, missions as MS, mercs as MC, hunting as HT  # noqa: E402
from avarenthia.entities import Item, make_gear  # noqa: E402
from avarenthia.money import fmt  # noqa: E402

E.save_path = lambda: os.path.join(tempfile.gettempdir(), f'avarenthia_money_{os.getpid()}.dat')

LEVELS = (1, 10, 20)
TIER = {1: 'A', 10: 'B', 20: 'C'}            # the game a hunter of that level takes
WEAR = .06                                   # what a day of fighting takes from the gear's life
EARN = ('job', 'trade', 'hunt', 'guard')

# per level: (coin in per day, lowest, highest), (days of work for a bed, highest), (days for a raising, highest)
BANDS = {1: dict(net=(-150, 6000), bed=1.0, raise_=3),
         10: dict(net=(0, 8000), bed=.5, raise_=4),
         20: dict(net=(0, 10000), bed=.5, raise_=6)}

_WORLD = {}


def new_game(seed, lvl):
    """One world per seed, kept for all levels; the hero set to the level with plain gear of it."""
    from avarenthia import debug as DBG
    if seed not in _WORLD:
        random.seed(seed)
        _WORLD[seed] = E.Game('Purse', hardcore=False, seed=seed)
    g = _WORLD[seed]
    random.seed(seed * 31 + lvl)
    p = g.player
    if p.lvl < lvl:
        DBG.level_up(g, lvl - p.lvl)
    for bk in ('longsword', 'leather'):
        if bk in D.BASES:
            it = make_gear(g, bk, 'normal', max(lvl, D.BASES[bk]['lvl']))
            g.add_to_inv(it)
            p.eq[it.slot] = it.id
    p.gold = {1: 600, 10: 5000, 20: 15000}.get(lvl, 1000)      # what a hero of the level carries
    return g


def town_near(g, x, y, exclude=None):
    w = g.world
    rows = [s for s in w.settlements if s.kind in ('village', 'town', 'city', 'metropolis') and s is not exclude
            and getattr(s, 'market', None)]
    return min(rows, key=lambda s: max(abs(s.x - x), abs(s.y - y)))


def road_days(a, b):
    return MS.travel_days(max(abs(a.x - b.x), abs(a.y - b.y)) * 1.3)


def do_job(g, s, kinds=None):
    """One job from this town's board: (coin, days, the town where it ends)."""
    for _ in range(10):
        try:
            mi = MS.make_offer(g, s, kinds=kinds)
        except Exception:
            mi = None
        if mi and mi.reward:
            break
    else:
        return 0, 1, s
    days = max(1, (mi.deadline - g.day - 2) if mi.deadline else 2)
    end = g.world.settlements[mi.target] if isinstance(mi.target, int) and mi.target < len(g.world.settlements) else s
    return mi.reward, days, end


def do_trade(g, s):
    """The best run from this town to a town a few days off, bought and sold for real at both markets (the prices
    bend as you buy and sell, the route tires), with the coin in the purse and the cargo room the hero has."""
    p = g.player
    w = g.world
    best = (0, None, None, 1)
    for o in sorted((o for o in w.settlements if o is not s and getattr(o, 'market', None)),
                    key=lambda o: max(abs(o.x - s.x), abs(o.y - s.y)))[:6]:
        days = road_days(s, o)
        for gd in s.market:
            if gd not in o.market or ECO.units(s, gd) < 1:
                continue
            margin = ECO.sell_price(o, gd) - ECO.buy_price(s, gd)
            if margin * 4 / days > best[0] / best[3]:
                best = (margin * 4, o, gd, days)
    _m, o, gd, days = best
    if o is None or p.gold < 1:
        return 0, 1, s
    before = p.gold
    n = ECO.buy(g, s, gd, 999)
    if n:
        ECO.sell(g, o, gd, n)
    p.cargo.pop(gd, None)
    return p.gold - before, days, o


def do_hunt(g, lvl):
    """A day's hunting: two or three beasts of the level's tier, skinned and sold."""
    tier = TIER[lvl]
    beasts = [k for k in HT.SKINS if HT.GAME_TIER.get(k, 'A') == tier and HT.SKINS[k][2]] or list(HT.SKINS)[:4]
    coin = 0
    for _ in range(random.randint(2, 3)):
        k = random.choice(beasts)
        h = Item(g.new_id(), 'hide', k)
        h.q, h.state, h.until = 2 if lvl >= 10 else 1, 'fresh', g.day + 2
        coin += g.sell_value(h)
        meat = HT.SKINS[k][0]
        if meat:
            from avarenthia.hunger import make_food
            coin += g.sell_value(make_food(g, meat, 2))
    return coin, 1


def costs(g, lvl, days, in_town_nights):
    """What those days cost: beds in town, food on the road, mending, a hireling."""
    out = {'bed': in_town_nights * g.MEAL, 'food': (days - in_town_nights) * g.STEW}
    gear = [it for it in g.player.inv if g.is_equipped(it) and getattr(it, 'mdur', 0)]
    mend = 0
    for it in gear:
        it.dur = max(1, round(it.mdur * (1 - WEAR * days)))
        mend += g.repair_cost(it)
        it.dur = it.mdur
    out['mending'] = mend
    out['hireling'] = MC.wage_for('warrior', lvl) * days if lvl >= 10 else 0
    return out


def live(lvl, days=40, seed=11, quiet=False):
    g = new_game(seed, lvl)
    s = g.world.settlements[0]
    inn, outn = {k: 0 for k in EARN}, {}
    spent_days = {k: 0 for k in EARN}
    day = 0
    i = 0
    while day < days:
        kind = EARN[i % len(EARN)]
        i += 1
        if kind == 'job':
            coin, d, s2 = do_job(g, s)
        elif kind == 'guard':
            coin, d, s2 = do_job(g, s, ['escort'])
        elif kind == 'trade':
            coin, d, s2 = do_trade(g, s)
        else:
            coin, d = do_hunt(g, lvl)
            s2 = s
        d = max(1, min(d, days - day))
        inn[kind] += coin
        spent_days[kind] += d
        for k, v in costs(g, lvl, d, 1).items():
            outn[k] = outn.get(k, 0) + v
            g.player.gold -= v
        if kind != 'trade':                     # a trade run's coin is already in the purse
            g.player.gold += coin
        g.player.gold = max(0, g.player.gold)
        s = s2
        day += d
    fee = g.raise_fee(lvl)
    outn['temple'] = fee
    total_in = sum(inn.values())
    total_out = sum(outn.values())
    per_day = (total_in - total_out) / days
    earn_day = total_in / days
    wpn = make_gear(g, 'longsword', 'magic', lvl)
    potion = Item(g.new_id(), 'potion', 'hp', 1)
    gear = [it for it in g.player.inv if g.is_equipped(it) and getattr(it, 'mdur', 0)]
    for it in gear:
        it.dur = it.mdur // 2
    mend = sum(g.repair_cost(it) for it in gear)
    buys = {'a bed': g.MEAL, 'mending half-worn gear': mend, 'a good weapon of the level': wpn.value(),
            'a healing potion': potion.value(), 'a raising at the temple': fee}
    res = dict(lvl=lvl, days=days, inn=inn, out=outn, kind_days=spent_days, per_day=per_day, earn_day=earn_day,
               buys={k: v / max(1, earn_day) for k, v in buys.items()}, prices=buys)
    if not quiet:
        table(res)
    return res


def table(r):
    print(f"\n=== Level {r['lvl']}: {r['days']} days ===")
    print('Coin in, per day, by kind of work:')
    for k, v in r['inn'].items():
        d = max(1, r['kind_days'][k])
        print(f'  {k:<10} {fmt(v / r["days"]):>14}   ({r["kind_days"][k]} days of it, {fmt(v / d)} a day while doing it)')
    print('Coin out, per day:')
    for k, v in r['out'].items():
        print(f'  {k:<10} {fmt(v / r["days"]):>14}')
    print(f"  In {fmt(r['earn_day'])} a day, out {fmt(r['earn_day'] - r['per_day'])}: {fmt(r['per_day'])} a day left over.")
    print('Days of work to buy:')
    for k, v in r['buys'].items():
        print(f'  {k:<28} {v:6.1f} days ({fmt(r["prices"][k])})')


def check(days=20, seed=11):
    """For the test: each level's numbers inside its bands. Returns the list of what left its band."""
    bad = []
    for lvl in LEVELS:
        r = live(lvl, days, seed, quiet=True)
        b = BANDS[lvl]
        lo, hi = b['net']
        if not lo <= r['per_day'] <= hi:
            bad.append(f'level {lvl}: {fmt(r["per_day"])} a day left over, outside {fmt(lo)} to {fmt(hi)}')
        if r['buys']['a bed'] > b['bed']:
            bad.append(f'level {lvl}: a bed takes {r["buys"]["a bed"]:.1f} days of work (at most {b["bed"]})')
        if r['buys']['a raising at the temple'] > b['raise_']:
            bad.append(f'level {lvl}: a raising takes {r["buys"]["a raising at the temple"]:.1f} days (at most {b["raise_"]})')
    return bad


def opening(worlds=10):
    """The day of the first tome, modelled: Snagtooth's hoard once the den is reached and cleared (the road there
    and a day below), or the Thornfield shop's tome on day one when it has one and the priestess's coppers buy it."""
    from avarenthia import firststeps as FS
    rows = []
    for seed in range(1, worlds + 1):
        random.seed(seed)
        g = E.Game('Opening', hardcore=False, seed=seed)
        w = g.world
        ts = w.sites[w.start_temple]
        d = w.dungeons['den']
        den_day = 1 + MS.travel_days(max(abs(d.x - ts.x), abs(d.y - ts.y)) * 1.3) + 1
        shop = [it for it in g.shops.get(0, []) if it.k == 'tome']
        first = 1 if shop and shop[0].value() <= 520 else den_day
        city = FS.letter_city(g)
        th = w.settlements[0]
        rows.append((seed, den_day, bool(shop), first, city.name, road_days(th, city)))
        print(f'  world {seed:>2}: den cleared day {den_day}, Thornfield shop tome {"yes" if shop else "no "}, '
              f'first tome day {first}; the letter to {city.name}, {road_days(th, city)} days off')
    days = [r[3] for r in rows]
    print(f'First tome: day {min(days)} to {max(days)}, on average day {sum(days) / len(days):.1f}.')
    return rows


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--opening':
        opening(int(sys.argv[2]) if len(sys.argv) > 2 else 10)
        E.delete_save()
        sys.exit(0)
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 11
    for lvl in LEVELS:
        live(lvl, days, seed)
    print('\nBands:', 'all inside' if not check(min(days, 20), seed) else '; '.join(check(min(days, 20), seed)))
    E.delete_save()
    _ = math
