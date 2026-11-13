"""The balance of the newer systems (rounds 59-66), next to what a day earns (tests/money.py):

    camps      the quartermaster of a host camp: what he pays against what the nearest town asks, and after a
               cartload has gone through
    homes      a town house against a bed at the inn, the hearth tax, building out on the land, a seat
    wars       ransoms, and how much your task in the field battle moves the odds
    inn        the stakes at the gaming table

    python tests/newbalance.py [seed]
"""
import os
import random
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))

from avarenthia import engine as E, data as D  # noqa: E402
from avarenthia import economy as ECO, homes as HM, camps as CM, wars as WR, inngames as IG  # noqa: E402
from avarenthia.money import fmt  # noqa: E402

E.save_path = lambda: os.path.join(tempfile.gettempdir(), f'avarenthia_newbal_{os.getpid()}.dat')


def world(seed):
    random.seed(seed)
    return E.Game('Tally', hardcore=False, seed=seed)


def camps(g, out):
    """The quartermaster: his price against the town's, before and after a cartload bought in that town."""
    w = g.world
    towns = [s for s in w.settlements if getattr(s, 'market', None)][:12]
    rows = []
    for s in towns:
        c = dict(x=s.x + 3, y=s.y + 3)
        for gd in CM.WAR_GOODS:
            if gd not in s.market:
                continue
            buy, war = ECO.buy_price(s, gd), CM.war_price(g, c, gd)
            rows.append((s.name, gd, buy, war, war / buy - 1))
    m = [r[4] for r in rows]
    out.append('== camps: the quartermaster against the nearest town (buy there, sell to him)')
    out.append(f'  {len(rows)} town-goods; margin mean {sum(m) / len(m):+.0%}, best {max(m):+.0%}, '
               f'worst {min(m):+.0%}; {sum(1 for x in m if x > 0)} of {len(m)} pay')
    for r in sorted(rows, key=lambda r: -r[4])[:6]:
        out.append(f'  {r[0]:<18} {r[1]:<9} buy {fmt(r[2]):>8}  quartermaster {fmt(r[3]):>8}  {r[4]:+.0%}')
    # a cartload: buy 60 in the best town, one by one, then sell all 60 to him
    s_name, gd = sorted(rows, key=lambda r: -r[4])[0][:2]
    s = next(x for x in towns if x.name == s_name)
    c = dict(x=s.x + 3, y=s.y + 3)
    p = g.player
    p.gold = 10 ** 9
    gold0 = p.gold
    n = 0
    for _ in range(60):
        if ECO.units(s, gd) <= 0:
            break
        ECO.buy(g, s, gd, 1)
        n += 1
    paid = gold0 - p.gold
    n = p.cargo.get(gd, 0)                   # what the cart held of it
    c['wd'] = None
    get = CM.pay_for(g, c, gd, p.cargo.get(gd, 0))
    out.append(f'  a cartload of {n} {gd} from {s.name}: paid {fmt(paid)}, the quartermaster gives {fmt(get)} (war prices for {CM.NEED}) '
               f'({get / max(1, paid) - 1:+.0%}); profit {fmt(get - paid)}')
    p.cargo.pop(gd, None)
    return get - paid


def homes(g, out):
    out.append('== homes (an inn bed is ' + fmt(g.MEAL) + ' a night)')
    for size, gold in HM.TOWN_PRICE.items():
        price = gold * HM.GOLD
        tax = max(5 * HM.SILVER, round(price / 60 / 500) * 500)
        per_day = tax / HM.SEASON
        nights = price / max(1, g.MEAL - per_day)
        out.append(f'  {size:<11} house {fmt(price):>6}, tax {fmt(tax)} a season ({fmt(round(per_day))} a day); '
                   f'pays back in {nights:.0f} nights instead of the inn')
    tot = HM.STAKE
    line = []
    for st in HM.STAGES[1:]:
        tot += st[2] * HM.GOLD
        line.append(f'{st[0]} {fmt(tot)}')
    out.append('  built on the land, adding up from the 2g stake: ' + ', '.join(line))
    for k, gold in HM.SEAT_PRICE.items():
        rest = sum(st[2] for st in HM.SEAT_STAGES) * HM.GOLD
        out.append(f'  a {k}: {fmt(gold * HM.GOLD)} and {fmt(rest)} to restore it; a steward and a guard '
                   f'{fmt((HM.STEWARD_WAGE + HM.GUARD_WAGE) * 30)} a month')


def wars(g, out):
    out.append('== wars')
    out.append('  ransom: ' + ', '.join(f'{k} {fmt(v * 100)}' for k, v in WR.RANSOM.items()))
    # the field: the strength ratio decides; your part moves it at most 15%
    for ratio in (.35, .5, .65):
        for b in (-.05, 0, .15):
            out.append(f'  hosts {ratio:.0%} : {1 - ratio:.0%}, your part {b:+.0%}: about {min(.95, max(.05, ratio + b)):.0%} to win')


def inn(g, out):
    out.append('== inn games')
    out.append(f'  stakes {", ".join(fmt(s) for s in IG.STAKES)}; at most {fmt(IG.NIGHT_LIMIT)} a night '
               f'({fmt(IG.NIGHT_LIMIT * 2)} in a city)')


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    g = world(seed)
    out = []
    camps(g, out)
    homes(g, out)
    wars(g, out)
    inn(g, out)
    print('\n'.join(out))


if __name__ == '__main__':
    main()
