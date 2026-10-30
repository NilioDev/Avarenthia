"""Trade part 3 (round 26): your own caravan, and the road with the NPC caravans on it.

A wagon is bought at the stables of a town or city once you own the mule cart: up to three (four from League rank
6), each pulled by a mule or an ox (the ox pulls more and walks slower), each with a driver on a weekly wage. The
wagons follow you on the world map as a string of signs and carry cargo of their own. The road matters: off the road
they go slowly, in spring they stick in the mud, a ford in spate or a closed pass stops them like you; the beasts eat
grain from the cargo; a wheel breaks now and then. On a land map the wagons stand round you (in a ring at night);
walk into the lead wagon to make camp, leave the caravan here, look at the cargo, pay the crew or mend a wheel. Raids
ask a toll or fall on you; a wagon that falls loses its cargo. Unpaid drivers stop. All of it lives on the player
(`p.caravan`).

The NPC caravans: walk with one (its guards keep you safe; you arrive with it), trade with it on the road at its home
town's prices; League caravans race you to the market of a big load; robbing one has weight."""
import math
import random

from . import data as D
from .worldgen import cheb

WAGON_PRICE = 40000                 # 400 silver for the wagon itself
BEASTS = {'mule': dict(name='mule', price=15000, cap=150, slow=1.0),
          'ox': dict(name='ox', price=24000, cap=210, slow=1.35)}
WAGE = 1500                         # a driver's wage, a week
STABLE_FEE = 20                     # a night in the stables, a wagon
FG = (110, 226, 236)
NAMES = ['the Saltwind Train', 'the Long Road Company', 'the Grey Mule Wagons', 'the Lantern Train', 'the Dusty Wheel',
         'the Wayfarers\' Wagons', 'the Copper Bell Train', 'the Hearthstone Wagons', 'the Far Road Company',
         'the Red Axle', 'the Swallow Train', 'the Ironhoof Wagons']
NIGHT_RING = [(-2, -1), (-2, 1), (2, -1), (2, 1), (0, -2), (0, 2), (-1, 2), (1, -2)]


def most(game):
    from . import tradegoods as TG
    return 4 if TG.rank(game) >= 6 else 3


def get(p):
    return getattr(p, 'caravan', None)


def with_you(p):
    cv = get(p)
    return bool(cv and cv['wagons'] and cv['at'] is None)


def capacity(p):
    """The cargo the wagons carry while they are with you."""
    cv = get(p)
    if not with_you(p):
        return 0
    return sum(BEASTS[w['beast']]['cap'] for w in cv['wagons'])


def slow(p):
    """How much the wagons slow you on the world map: the slowest beast sets the pace."""
    cv = get(p)
    if not with_you(p):
        return 1.0
    return max(BEASTS[w['beast']]['slow'] for w in cv['wagons']) * (1.25 if cv.get('hungry') else 1.0)


def cargo_value(game):
    p = game.player
    return sum(q * D.GOODS[g]['base'] for g, q in p.cargo.items())


# ---------------------------------------------------------------- buying
def buy_wagon(game, beast):
    """At the stables: a wagon with its beast and a driver."""
    p = game.player
    if 'cart' not in p.mounts:
        game.msg('"Learn the road with a cart first," the stablemaster says. "Then come back for wagons."', 'bad')
        return False
    cv = get(p)
    if cv and len(cv['wagons']) >= most(game):
        game.msg(f'You have {len(cv["wagons"])} wagons, as many as one trader can keep on the road.', 'bad')
        return False
    here = getattr(game, 'here', None)
    if cv and cv['at'] is not None and not (here is not None and cv['at'] == ('s', here.id)):
        game.msg('Your caravan is not with you.', 'bad')
        return False
    price = WAGON_PRICE + BEASTS[beast]['price']
    if p.gold < price:
        game.msg('You cannot afford that.', 'bad')
        return False
    p.gold -= price
    if not cv:
        cv = p.caravan = dict(name=random.choice(NAMES), wagons=[], at=None, held={}, trail=[], last=(p.x, p.y),
                              owed=0, week=game.day // 7, day=game.day, mood=3, trips=0, raid=None, hungry=False)
        game.msg(f'Your wagons will be known as {cv["name"]}. Walk into the lead wagon on the land to see to them.',
                 'gold')
    cv['wagons'].append(dict(beast=beast, broken=False))
    from .economy import cargo_capacity
    game.msg(f'You buy a wagon with {"an ox" if beast == "ox" else "a mule"} and hire a driver at {fmt(WAGE)} a week. '
             f'Your cargo space is now {cargo_capacity(p)}.', 'gold')
    return True


def fmt(c):
    from .money import fmt as f
    return f(c)


# ---------------------------------------------------------------- where it is
def leave(game, where, quiet=False):
    """The caravan stays behind: what the wagons carry stays on them."""
    from .economy import cargo_capacity, cargo_weight
    p = game.player
    cv = get(p)
    if not with_you(p):
        return
    cv['at'] = where
    cv['since'] = game.day
    over = cargo_weight(p) - cargo_capacity(p)
    held = cv['held']
    for g in sorted(p.cargo, key=lambda g: -D.GOODS[g]['w']):
        while over > 0 and p.cargo.get(g, 0) > 0:
            p.cargo[g] -= 1
            held[g] = held.get(g, 0) + 1
            over -= D.GOODS[g]['w']
        if not p.cargo.get(g):
            p.cargo.pop(g, None)
    if not quiet:
        game.msg(f'{cv["name"][0].upper() + cv["name"][1:]} waits for you here' +
                 (', with the cargo you could not carry.' if held else '.'), 'info')


def rejoin(game, quiet=False):
    """You are back with your wagons: what they carry is yours to sell again."""
    p = game.player
    cv = get(p)
    if not cv or cv['at'] is None:
        return
    if cv['owed'] >= WAGE * len(cv['wagons']) * 2:
        if not quiet:
            game.msg('Your drivers sit by the wagons with folded arms: they will not drive another mile unpaid.', 'bad')
        return
    at = cv['at']
    if at[0] == 's':
        nights = max(1, game.day - cv.get('since', game.day))
        fee = nights * STABLE_FEE * len(cv['wagons'])
        p.gold = max(0, p.gold - fee)
        if not quiet:
            game.msg(f'You pay {fmt(fee)} to the stables and your wagons roll out behind you.', 'info')
    elif not quiet:
        game.msg(f'You are back with {cv["name"]}.', 'good')
    cv['at'] = None
    for g, q in cv['held'].items():
        p.cargo[g] = p.cargo.get(g, 0) + q
    cv['held'] = {}
    cv['trail'] = []
    cv['last'] = (p.x, p.y)


def on_enter_town(game, s):
    """Into a town: the wagons go to its stables, or wait at the gate where there are none."""
    p = game.player
    if not with_you(p):
        return
    if 'stables' in s.services:
        leave(game, ('s', s.id), quiet=True)
        game.msg('Your wagons go round to the stables.', 'info')
    else:
        leave(game, ('xy', s.x, s.y), quiet=True)
        game.msg('Your wagons wait outside the gate.', 'info')


def on_enter_place(game, x, y):
    """A dungeon, a site or a hold: the wagons wait outside."""
    if with_you(game.player):
        leave(game, ('xy', x, y), quiet=True)
        game.msg('Your wagons wait outside.', 'info')


def on_back(game):
    """Back on the world map: your wagons join you where they wait."""
    p = game.player
    cv = get(p)
    if not cv or cv['at'] is None or cv.get('kept'):
        return
    at = cv['at']
    here = (p.x, p.y)
    s = game.world.settlement_at(*here)
    if (at[0] == 'xy' and (at[1], at[2]) == here) or (at[0] == 's' and s is not None and at[1] == s.id):
        rejoin(game)


def wait_here(game):
    """Leave the caravan where it stands on purpose: it does not join you until you come back for it."""
    p = game.player
    x, y = (p.x, p.y) if game.cur == 'over' else game.over_pos
    leave(game, ('xy', x, y))
    p.caravan['kept'] = True


# ---------------------------------------------------------------- on the road
def blocked(game, nx, ny):
    """Somewhere wagons can not go though you could."""
    if not with_you(game.player):
        return None
    m = game.maps['over']
    t = m.tile(nx, ny)
    if t == D.RIVER:
        return 'The wagons can not go through the ford. They need a bridge, or a ferry.'
    if t == D.SWAMP:
        return 'The wagons would sink in the swamp.'
    return None


def cost(game, c, t):
    """The cost of a step on the world map with the wagons along."""
    p = game.player
    if not with_you(p):
        return c
    off = t not in (D.ROAD, D.BRIDGE)
    return c * slow(p) * (1.6 if off else 1.0)


def over_step(game):
    """After a step on the world map: the string of wagons follows, the beasts eat, a wheel may break, the mud may
    hold them, robbers may wait. Returns turns spent, or None."""
    p = game.player
    cv = get(p)
    if not cv:
        return None
    if cv['at'] is not None:
        if cv['at'][0] == 'xy' and (cv['at'][1], cv['at'][2]) == (p.x, p.y):
            cv.pop('kept', None)
            rejoin(game)
        return None
    if (p.x, p.y) != tuple(cv['last']):
        cv['trail'] = ([tuple(cv['last'])] + cv['trail'])[:len(cv['wagons'])]
        cv['last'] = (p.x, p.y)
    _days(game)
    if not with_you(p):
        return None
    m = game.maps['over']
    t = m.tile(p.x, p.y)
    off = t not in (D.ROAD, D.BRIDGE)
    if off and random.random() < .003 * len(cv['wagons']):
        w = random.choice(cv['wagons'])
        w['broken'] = True
        leave(game, ('xy', p.x, p.y), quiet=True)
        cv['kept'] = True
        game.msg('Crack: a wheel breaks. The caravan can not go on until it is mended: go down to it and walk into the '
                 'lead wagon.', 'bad')
        return None
    from . import calendar as CAL
    if off and CAL.season(game.day) == 'spring' and random.random() < .04:
        game.msg('The wagons sink to the axles in the spring mud. It takes the crew an hour to dig them out.', 'bad')
        return 30
    if raid_chance(game, t) > random.random():
        raid(game)
        return 1
    return None


def raid_chance(game, t):
    p = game.player
    w = game.world
    x, y = p.x, p.y
    h = w.settlements[0]
    if cheb(x, y, h.x, h.y) <= 6 or game.world.settlement_at(x, y):
        return 0
    if any(s.kind == 'serai' and cheb(x, y, s.x, s.y) <= 2 for s in w.sites):
        return 0        # no robber comes near the walls of a caravanserai
    from . import mercs as MC
    rich = min(2.0, .5 + cargo_value(game) / 20000)
    base = (.002 if t in (D.ROAD, D.BRIDGE) else .006) * (1 + w.danger_at(x, y) * .15)
    return base * rich * (.6 if MC.on_watch(game) else 1)


def raid(game):
    """Riders block the way: a toll, or a fight among the wagons."""
    from . import events as EV
    p = game.player
    toll = max(200, cargo_value(game) // 12)
    who = random.choice(['Bandits', 'Raiders', 'Hard men on horses'])
    p.caravan['toll'] = toll
    EV.ask(game, 'wagon_raid', f'{who} on the road',
           f'{who} come out of cover and stand across the way, more of them behind the wagons. "Nice wagons. '
           f'{fmt(toll)} and you roll on. Or we take what we like."',
           [(f'Pay the toll ({fmt(toll)})', 'pay'), ('Fight them among the wagons', 'fight')])


def r_raid(game, choice, ctx):
    p = game.player
    cv = get(p)
    if not cv:
        return
    toll = cv.pop('toll', 200)
    if choice == 'pay' and p.gold >= toll:
        p.gold -= toll
        game.msg('You pay. They count it twice, and let you pass.', 'info')
        return
    if choice == 'pay':
        game.msg('You have not got it. "Then we take it."', 'bad')
    fight(game)


def fight(game):
    """Robbers fall on the wagons: fought on the land, the wagons standing round you for cover."""
    p = game.player
    w = game.world
    x, y = (p.x, p.y) if game.cur == 'over' else game.over_pos
    lvl = w.danger_at(x, y) + 1
    pack = ['bandit'] + [random.choice(['bandit', 'brigand']) for _ in range(random.randint(2, 3 + lvl // 3))]
    p.caravan['raid'] = True
    game.start_encounter(None, game.maps['over'].tile(x, y), lvl, pack, 0)


def after_fight(game, fled=False):
    """A raid over: won, the wagons roll on; run away from it, and the robbers take a wagon's load."""
    p = game.player
    cv = get(p)
    if not cv or not cv.get('raid'):
        return
    cv['raid'] = None
    if fled:
        lose_load(game, 'The robbers drive off a wagon and empty it on the road.')
    else:
        game.msg('The robbers are gone. The drivers come out from under the wagons.', 'good')
        cv['mood'] = min(5, cv['mood'] + 1)


def lose_load(game, why, frac=None):
    """A wagon's share of the cargo is gone."""
    p = game.player
    cv = get(p)
    n = max(1, len(cv['wagons']))
    frac = frac or (capacity(p) / n) / max(1, capacity(p) + 30)
    lost = []
    for g in list(p.cargo):
        k = int(round(p.cargo[g] * frac))
        if k:
            p.cargo[g] -= k
            lost.append(f'{k} {D.GOODS[g]["name"].lower()}')
            if p.cargo[g] <= 0:
                del p.cargo[g]
    game.msg(why + (f' Lost: {", ".join(lost)}.' if lost else ''), 'bad')


def wagon_hit(game, wagon_npc):
    """A wagon smashed in a fight: its load is gone, its wheel broken."""
    p = game.player
    cv = get(p)
    if not cv:
        return
    lose_load(game, 'A wagon goes over in the fight, its load spilt and trampled.')
    for w in cv['wagons']:
        if not w['broken']:
            w['broken'] = True
            break


def _days(game):
    """A day on the road: the beasts eat; a week: the drivers are paid."""
    p = game.player
    cv = get(p)
    if game.day > cv['day']:
        for _ in range(min(7, game.day - cv['day'])):
            need = len(cv['wagons'])
            have = p.cargo.get('grain', 0)
            if have >= need:
                p.cargo['grain'] = have - need
                if not p.cargo['grain']:
                    del p.cargo['grain']
                cv['hungry'] = False
            else:
                if not cv['hungry']:
                    game.msg('The beasts are hungry and slow. Grain in the cargo would feed them.', 'bad')
                cv['hungry'] = True
        cv['day'] = game.day
    week = game.day // 7
    if week > cv['week']:
        cv['week'] = week
        due = WAGE * len(cv['wagons']) + cv['owed']
        if p.gold >= due:
            p.gold -= due
            cv['owed'] = 0
            game.msg(f'You pay your drivers their week: {fmt(due)}.', 'info')
        else:
            cv['owed'] = due - p.gold if p.gold < due else 0
            p.gold = 0 if p.gold < due else p.gold
            cv['mood'] = max(0, cv['mood'] - 2)
            game.msg('You could not pay your drivers in full. They grumble; another week like this and they stop.', 'bad')
            if cv['owed'] >= WAGE * len(cv['wagons']) * 2:
                leave(game, ('xy', p.x, p.y), quiet=True)
                cv['kept'] = True
                game.msg('Your drivers stop the wagons and will not go on until they are paid.', 'bad')


# ---------------------------------------------------------------- the wagons on a land map
def place(game, m):
    """Put the wagons round you on a land map: in a row behind you by day, in a ring at night."""
    from .entities import make_npc
    from . import towns as TW
    p = game.player
    m.mons = [o for o in m.mons if getattr(o, 'role', '') != 'wagon']
    cv = get(p)
    if not cv:
        return
    here = game.over_pos
    if cv['at'] is None:
        x0, y0 = p.x, p.y
    elif cv['at'][0] == 'xy' and (cv['at'][1], cv['at'][2]) == tuple(here) and getattr(m, 'zone', None) is not None:
        from . import zones as ZN
        x0, y0 = ZN.local_mid(game, m)
    else:
        return
    night = TW.is_night(game)
    spots = NIGHT_RING if night else [(-2 * (i + 1), 1) for i in range(4)]
    for i, w in enumerate(cv['wagons']):
        for dx, dy in [spots[i]] + [(a, b) for a in range(-4, 5) for b in range(-3, 4)]:
            x, y = x0 + dx, y0 + dy
            if m.inb(x, y) and D.TILES[m.tile(x, y)].walk and not m.mon_at(x, y) and (x, y) != (p.x, p.y):
                o = make_npc(game, ('The lead wagon' if i == 0 else 'A wagon') + (' (a broken wheel)' if w['broken'] else ''),
                             'wagon', '#6ee2ec', x, y, True, ch='♦')
                o.hp = o.maxhp = 60
                o.stay = True
                o.wagon = i
                m.mons.append(o)
                break


def follow(game, m):
    """On a land map the wagons that are with you roll after you."""
    p = game.player
    if not with_you(p):
        return
    for o in [o for o in m.mons if getattr(o, 'role', '') == 'wagon']:
        if cheb(o.x, o.y, p.x, p.y) <= 2:
            continue
        best = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = o.x + dx, o.y + dy
                if (dx or dy) and m.inb(nx, ny) and D.TILES[m.tile(nx, ny)].walk and not m.mon_at(nx, ny) \
                        and (nx, ny) != (p.x, p.y):
                    d = cheb(nx, ny, p.x, p.y)
                    if best is None or d < best[0]:
                        best = (d, nx, ny)
        if best:
            o.x, o.y = best[1], best[2]


def talk(game, npc):
    """Walking into a wagon: what to do with the caravan."""
    from . import events as EV
    p = game.player
    cv = get(p)
    if not cv:
        return
    from .economy import cargo_capacity, cargo_weight
    broken = [w for w in cv['wagons'] if w['broken']]
    load = ', '.join(f'{q} {D.GOODS[g]["name"].lower()}' for g, q in sorted({**p.cargo, **cv['held']}.items())) or 'nothing'
    text = (f'{cv["name"][0].upper() + cv["name"][1:]}: {len(cv["wagons"])} wagons, '
            f'{", ".join(BEASTS[w["beast"]]["name"] for w in cv["wagons"])}. Cargo {cargo_weight(p)} of '
            f'{cargo_capacity(p) + (0 if with_you(p) else capacity_all(p))}: {load}.')
    if cv['owed']:
        text += f' The drivers are owed {fmt(cv["owed"])}.'
    if broken:
        text += f' {len(broken)} wagon{"s have" if len(broken) > 1 else " has"} a broken wheel.'
    if cv['at'] is not None and not broken and not cv['owed']:
        text += ' It waits here for you.'
    opts = []
    if broken:
        opts.append(('Mend the wheel' + (' with tools from the cargo' if p.cargo.get('tools') else ', slowly'), 'mend'))
    if cv['owed']:
        opts.append((f'Pay the crew ({fmt(cv["owed"])})', 'pay'))
    if cv['at'] is not None and not broken:
        opts.append(('Take the caravan on with you', 'take'))
    if cv['at'] is None:
        opts.append(('Make camp with the crew for the night', 'camp'))
        opts.append(('Leave the caravan here', 'leave'))
    opts.append(('Go on', 'bye'))
    EV.ask(game, 'wagon', 'Your caravan', text, opts)


def capacity_all(p):
    cv = get(p)
    return sum(BEASTS[w['beast']]['cap'] for w in cv['wagons']) if cv else 0


def r_wagon(game, choice, ctx):
    p = game.player
    cv = get(p)
    if not cv or choice == 'bye':
        return
    if choice == 'mend':
        if p.cargo.get('tools'):
            p.cargo['tools'] -= 1
            if not p.cargo['tools']:
                del p.cargo['tools']
            game.end_turn(20, True)
            game.msg('With the tools from the cargo the crew have a new wheel on before long.', 'good')
        else:
            game.end_turn(D.DAY_LEN // 4, True)
            game.msg('Without tools the crew carve and lash a wheel together. It takes them half the day.', 'info')
        for w in cv['wagons']:
            w['broken'] = False
        if cv['at'] is not None and not cv['owed']:
            cv.pop('kept', None)
            rejoin(game, quiet=True)
            game.msg('The caravan is ready to roll.', 'good')
    elif choice == 'pay':
        if p.gold >= cv['owed']:
            p.gold -= cv['owed']
            cv['owed'] = 0
            cv['mood'] = max(cv['mood'], 2)
            game.msg('You pay the crew what they are owed. They get back up on the wagons.', 'good')
        else:
            game.msg('You have not got that much.', 'bad')
    elif choice == 'take':
        cv.pop('kept', None)
        rejoin(game)
    elif choice == 'leave':
        wait_here(game)
        m = game.map
        for o in [o for o in m.mons if getattr(o, 'role', '') == 'wagon']:
            o.stay = True
    elif choice == 'camp':
        camp(game)
    from . import zones as ZN
    if getattr(game.map, 'zone', None) is not None:
        place(game, game.map)


def camp(game):
    """A night in the ring of wagons: a round of drink keeps the crew glad, the fire keeps the beasts off."""
    p = game.player
    cv = get(p)
    need = len(cv['wagons'])
    drink = next((g for g in ('ale', 'wine', 'mead') if p.cargo.get(g, 0) >= need), None)
    if drink:
        p.cargo[drink] -= need
        if not p.cargo[drink]:
            del p.cargo[drink]
        cv['mood'] = min(5, cv['mood'] + 1)
        game.msg(f'You stand the crew a round of {D.GOODS[drink]["name"].lower()} by the fire. They sing.', 'good')
    else:
        game.msg('The wagons stand in a ring round the fire; the crew turn in early.', 'info')
    game.camp(True)


def robbers_drawn(game):
    """A camp with wagons draws more robbers."""
    return 1.4 if with_you(game.player) else 1.0


def on_camp_robbers(game):
    if with_you(game.player):
        game.player.caravan['raid'] = True


# ---------------------------------------------------------------- the NPC caravans
def walk_along(game, wd):
    """Pay to walk with a caravan to where it goes: safe and slow."""
    p = game.player
    w = game.world
    dest = w.settlements[wd.dest]
    left = max(1, len(wd.path) - wd.path_i)
    fare = 50 + left * 4
    if p.gold < fare:
        game.msg('You have not got the fare.', 'bad')
        return
    p.gold -= fare
    days = max(1, round(left * wd.speed / D.DAY_LEN))
    game.msg(f'You pay {fmt(fare)} and walk with the caravan, the guards around you. '
             f'{days} day{"s" if days > 1 else ""} later you reach {dest.name}.', 'info')
    if wd in w.wanderers:
        from . import wanderers as WA
        WA.arrive(game, wd)
    p.x, p.y = dest.x, dest.y
    if with_you(p):
        cv = get(p)
        cv['trail'], cv['last'] = [], (p.x, p.y)
    game.end_turn(days * D.DAY_LEN // 2, True)
    game.compute_fov()


def race(game, s, g, n, anywhere=False):
    """A big load bought: a League caravan with the same good sets out for the same market, to be there first."""
    if n < 20 or (game.here is not s and not anywhere):
        return
    w = game.world
    buyers = [o for o in w.settlements if o.id != s.id and g in o.demand]
    if not buyers:
        return
    dest = min(buyers, key=lambda o: o.market[g][0] + cheb(o.x, o.y, s.x, s.y) * .3)
    from . import wanderers as WA
    path = WA.road_path(game, s.id, dest.id)
    if not path or any(x.kind == 'caravan' and getattr(x, 'rival', False) and x.origin == s.id for x in w.wanderers):
        return
    wd = WA.Wanderer(game.new_id(), 'caravan', s.x, s.y)
    wd.ch, wd.fg, wd.name = '♦', (236, 150, 80), 'A League caravan'
    wd.speed = 11
    wd.rival = True
    wd.origin, wd.dest, wd.goods, wd.path = s.id, dest.id, (g, 30), list(path)
    w.wanderers.append(wd)
    game.msg(f'A League factor loads {D.GOODS[g]["name"].lower()} too, bound for {dest.name}. Whoever gets there '
             f'first sells dear.', 'info')


def robbed(game, wd):
    """A caravan robbed: dearer goods where it was going, more guards on the next from its town."""
    w = game.world
    s = w.settlements[wd.origin]
    s.caravan_guards = min(4, getattr(s, 'caravan_guards', 0) + 1)
    if wd.dest is not None:
        d = w.settlements[wd.dest]
        g, q = wd.goods
        d.market[g][0] = max(0, d.market[g][0] - q // 2)


def _register():
    from . import events as EV
    EV.RESOLVERS['wagon'] = r_wagon
    EV.RESOLVERS['wagon_raid'] = r_raid


_register()
