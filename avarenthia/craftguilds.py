"""Round 48: the crafts guilds. Every life skill has a guild that keeps it (guilds.GUILDS, kind 'life'): Alembic and
Barrel, the Cartographers and the Brotherhood of the Net were there; the Hammer and Tongs, the Tanners' and Trappers'
Lodge, the Needle and Loom and the Lantern and Ladle are new, each with halls among at least three peoples.

- A rank asks a rank in the craft as well (CRAFT_NEED) and a fee when the master raises you (FEE), instead of dues:
  the guild jobs earn the standing, the master raises you (`s['paid']` is the rank you were raised to).
- The hall keeps the guild's own anvil, bench or hearth (`m.guild_bench`): members use it free.
- The tests at 25 and 40 can be shown to the master in the hall as well as to the far town's master.
- From Journeyman what you make carries the guild's mark (`it.gmark`): a sixth more from merchants, and the hall
  buys it.
- The master's board: one order at a time, better paid than the town's.
- At Master the guild secret: re-temper, mounting, livery, a table for the house.
- The guild day in every hall town (feasts.today): stalls and a contest for your best piece.

The standing lives with the other guilds (guilds.state); the livery and the trophies on the player."""
import random

from . import data as D
from .worldgen import cheb

NEW = ('hammer', 'lodge', 'needle', 'ladle')
CRAFT_NEED = [0, 10, 20, 30, 40]            # the rank in the guild's craft each guild rank asks
FEE = [0, 50, 200, 800, 2500]               # in copper: 50c, 2s, 8s, 25s
TOOL = {'hammer': 'ANVIL', 'lodge': 'BENCH', 'needle': 'BENCH', 'ladle': 'HEARTH'}
MARK = {'hammer': 'Hammer', 'lodge': 'Lodge', 'needle': 'Loom', 'ladle': 'Ladle'}
MARK_OF = {'smithing': 'hammer', 'leatherworking': 'lodge', 'tailoring': 'needle'}
ORDER_CRAFT = {'hammer': ('smithing',), 'lodge': ('leatherworking',), 'needle': ('tailoring',),
               'ladle': ('cooking', 'brewing'), 'alembic': ('alchemy', 'brewing')}
SECRET = {'hammer': 'Re-temper a piece you made', 'lodge': 'Mount the head of a named beast',
          'needle': 'Sew a livery in a people\'s colours', 'ladle': 'Cook a table for the house'}
# the master's board: what the world needs of each guild (shown with the order)
ORDER_WHY = {
    'hammer': ['Spears for the watch, before the raiders come again.', 'Tools for the mines, and quickly.',
               'Mail for a baron\'s riders.'],
    'lodge': ['Boots for a company marching north.', 'Saddles and straps for the post riders.',
              'Jerkins for the wardens of the woods.'],
    'needle': ['Winter cloaks before the snow.', 'A wedding cloak for a baron\'s house.', 'Robes for the temple choir.'],
    'ladle': ['A feast-day meal for the whole street.', 'Food for an army on the march.', 'The guild hall\'s own table.'],
    'alembic': ['Draughts for the temple\'s sick.', 'A strong brew for a captain\'s men.'],
}
# the people's colours a livery can be sewn in (the @ wears it)
LIVERY = {'human': ((220, 190, 90), 'the gold of the Crown'), 'dwarf': ((200, 120, 70), 'the copper of the holds'),
          'elf': ((120, 210, 150), 'the green of the Elder Tree'), 'halfling': ((210, 170, 110), 'the hill-folk\'s ochre'),
          'orc': ((190, 90, 80), 'the half-orcs\' red')}
GUILD_DAY_NAME = {'hammer': 'the Day of the Anvil', 'lodge': 'the Lodge Day', 'needle': 'the Day of the Loom',
                  'ladle': 'the Day of the Ladle'}
PRIZE = {'hammer': ('mat', 'bar_moonsilver', 2), 'lodge': ('leather', 'cavefur', 3), 'needle': ('mat', 'cloth_shadowsilk', 2),
         'ladle': ('coin', 300, 1)}


def G():
    from . import guilds as GU
    return GU


# ------------------------------------------------------------------ where the halls are
def setup(world):
    """Halls for the four new guilds, among three peoples or more each (called at the end of guilds.setup)."""
    rng = random.Random(len(world.settlements) * 6007 + world.settlements[0].y)
    ss = world.settlements
    halls = world.guild_halls

    def some(pred, n):
        got = [s.id for s in ss if pred(s)]
        rng.shuffle(got)
        return got[:n]
    human_city = lambda s: s.race == 'human' and s.is_city               # noqa: E731
    halls['hammer'] = some(human_city, 2) + some(lambda s: s.race == 'dwarf' and s.kind in ('city', 'metropolis', 'town'), 2) \
        + some(lambda s: s.race == 'orc' and s.kind in ('town', 'village'), 1)
    halls['lodge'] = (some(lambda s: human_city(s) and getattr(s, 'harbour', False), 2) or some(human_city, 2)) \
        + some(lambda s: s.race == 'halfling' and s.kind in ('town', 'village'), 1) \
        + some(lambda s: s.race == 'orc' and s.kind in ('town', 'village'), 1)
    halls['needle'] = some(human_city, 2) + some(lambda s: s.race == 'elf', 1) \
        + some(lambda s: s.race in ('halfling', 'dwarf') and s.kind in ('town', 'village'), 1)
    halls['ladle'] = some(lambda s: s.race == 'human' and s.kind in ('town', 'village') and 'inn' in s.services, 3) \
        + some(lambda s: s.race == 'halfling' and 'inn' in s.services, 2) \
        + some(lambda s: s.race == 'dwarf' and s.kind == 'town', 1)
    for k in NEW:                       # a small world without some peoples: fill up from any town
        if len({ss[i].race for i in halls[k]}) < 3 or len(halls[k]) < 3:
            extra = [s.id for s in ss if s.id not in halls[k] and s.kind in ('town', 'city', 'village') and s.id != 0]
            rng.shuffle(extra)
            seen = {ss[i].race for i in halls[k]}
            for i in extra:
                if ss[i].race not in seen or len(halls[k]) < 3:
                    halls[k].append(i)
                    seen.add(ss[i].race)
                if len(seen) >= 3 and len(halls[k]) >= 3:
                    break


# ------------------------------------------------------------------ ranks
def craft_rank(game, key):
    from . import lifeskills as LS
    return max((LS.rank(game, sk) for sk in G().GUILDS[key].get('skills', ())), default=0)


def earned(game, key):
    """The rank your standing has earned, before the master raises you."""
    rep = G().state(game)[key]['rep']
    return max(i for i, v in enumerate(G().RANK_REP) if rep >= v)


def raise_option(game, key):
    """The master's option to raise you, greyed when the craft or the coin is short; [] when there is nothing to raise."""
    from .money import fmt
    from . import lifeskills as LS
    GU = G()
    s = GU.state(game)[key]
    paid = s.get('paid', 0)
    if earned(game, key) <= paid or paid >= 4:
        return []
    nxt = paid + 1
    sk = GU.GUILDS[key]['skills']
    names = ' or '.join(LS.LIFE[k]['name'] for k in sk[:2])
    ok = craft_rank(game, key) >= CRAFT_NEED[nxt] and game.player.gold >= FEE[nxt]
    return [(f'Be raised to {GU.GUILDS[key]["ranks"][nxt]} ({fmt(FEE[nxt])}; {names} {CRAFT_NEED[nxt]})',
             'raise' if ok else None)]


def do_raise(game, key):
    GU = G()
    s = GU.state(game)[key]
    nxt = s.get('paid', 0) + 1
    if nxt > 4 or earned(game, key) < nxt or craft_rank(game, key) < CRAFT_NEED[nxt] or game.player.gold < FEE[nxt]:
        return False
    game.player.gold -= FEE[nxt]
    s['paid'] = nxt
    g = GU.GUILDS[key]
    game.msg(f'The master pins the {g["short"]} badge of a {g["ranks"][nxt].lower()} on you. The hall drinks to it.',
             'unique')
    if nxt == 2 and key in MARK.keys():
        from . import guide as GDE
        GDE.tip(game, 'guildmark')
    return True


# ------------------------------------------------------------------ the guild's own bench
def dress_hall(game, m, pl, key, master=None):
    """The guild's anvil, bench or hearth inside its hall."""
    tool = TOOL.get(key)
    if not tool or not getattr(pl, 'inside', None):
        return None
    from .towns import free_inside
    spots = [c for c in free_inside(m, pl) if not master or cheb(c[0], c[1], master.x, master.y) >= 2]
    door = getattr(pl, 'door', None)
    if door:
        spots = [c for c in spots if cheb(c[0], c[1], door[0], door[1]) >= 2] or spots
    if not spots:
        return None
    c = spots[0]
    m.set(c[0], c[1], getattr(D, tool))
    m.__dict__.setdefault('guild_bench', {})[tuple(c)] = key
    dress_street(m, pl, key)
    return c


def ensure_halls(game, m):
    """A town whose plan made no hall for one of its crafts guilds: the guild takes over a house."""
    s = game.here
    if s is None or getattr(m, 'sid', None) != s.id:
        return
    show_dry(game, m, s)
    halls = getattr(game.world, 'guild_halls', {})
    for key in NEW:
        if s.id not in halls.get(key, ()) or any(getattr(o, 'guild', None) == key for o in m.mons):
            continue
        houses = [b for b in getattr(m, 'buildings', ()) if b['kind'] in ('home', 'shop', 'keepsake')
                  and getattr(b.get('plot'), 'inside', None) and len(b['plot'].inside) >= 6]
        cx, cy = getattr(m, 'centre', (m.w // 2, m.h // 2))
        if not houses:                       # no house to take (carved halls, the roots of the Elder Tree): a table
            table_hall(game, m, s, key, cx, cy)
            continue
        b = min(houses, key=lambda b: cheb(b['box'][0], b['box'][1], cx, cy) - len(b['plot'].inside) // 4)
        b['kind'] = 'guild:' + key
        b['name'] = G().GUILDS[key]['sign'].title()
        b['plot'].guild = key
        from .towns import town_names
        G().place_master(game, m, b['plot'], key, town_names(getattr(s, 'race', 'human')))
        m._look = None


def table_hall(game, m, s, key, cx, cy):
    """The guild meets at a table by the square: the master, and the guild's tool beside them."""
    from .townlife import _free_near, _walk
    from .entities import make_npc
    from .towns import town_names
    c = _free_near(m, cx, cy, 2, 9)
    if not c:
        return None
    g = G().GUILDS[key]
    names = town_names(getattr(s, 'race', 'human'))
    npc = make_npc(game, G().master_name(key, names), 'guild', g['fg'], c[0], c[1], True)
    npc.guild = key
    m.mons.append(npc)
    spot = next(((c[0] + dx, c[1] + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1))
                 if _walk(m, c[0] + dx, c[1] + dy) and not m.mon_at(c[0] + dx, c[1] + dy)), None)
    if spot and key in TOOL:
        m.set(spot[0], spot[1], getattr(D, TOOL[key]))
        m.__dict__.setdefault('guild_bench', {})[spot] = key
    m._look = None
    return npc


def bench_here(game):
    """The guild whose own bench you stand by, or None."""
    m, p = game.map, game.player
    for (x, y), key in getattr(m, 'guild_bench', {}).items():
        if cheb(x, y, p.x, p.y) <= 1:
            return key
    return None


def free_bench(game):
    key = bench_here(game)
    return bool(key) and G().state(game)[key]['joined'] and not shut(game, key)


def bench_line(game):
    key = bench_here(game)
    if not key:
        return ''
    g = G().GUILDS[key]
    if G().state(game)[key]['joined']:
        return f' This is the {g["short"]}\'s own: free to you as a member.'
    return f' This is the {g["short"]}\'s own: members use it free.'


# ------------------------------------------------------------------ the mark
def mark(game, it, craft):
    """From Journeyman what you make carries the mark of your guild."""
    key = MARK_OF.get(craft)
    if not key:
        return
    GU = G()
    if not GU.state(game)[key]['joined'] or GU.rank(game, key) < 2:
        return
    it.gmark = key
    it.name = f'{it.name}, {MARK[key]} mark'


def mark_mult(it):
    return 1.15 if getattr(it, 'gmark', None) else 1.0


def marked_work(game, key):
    return [i for i in game.player.inv if getattr(i, 'gmark', None) == key and not game.is_equipped(i)]


def hall_price(it):
    """The hall pays two fifths of the worth for its own members' work, more than an outfitter."""
    return max(1, it.value() * 2 // 5)


def sell_marked(game, key):
    from .money import fmt
    got, n = 0, 0
    for it in marked_work(game, key):
        got += hall_price(it)
        n += 1
        game.player.inv.remove(it)
    game.player.gold += got
    game.msg(f'The hall takes {n} piece{"s" if n != 1 else ""} with its mark for {fmt(got)}.', 'gold')


# ------------------------------------------------------------------ the master's test
def tests_here(game, key):
    """Active master's tests this guild can judge."""
    sk = G().GUILDS[key].get('skills', ())
    return [m for m in game.missions if m.kind == 'mastertest' and m.state == 'active' and m.data.get('key') in sk]


def hand_in_test(game, mid):
    from . import mastery as MA
    from . import missions as MS
    from . import lifeskills as LS
    m = next((x for x in game.missions if x.id == mid), None)
    if not m:
        return
    d = m.data
    what, test, n = MA.wants(d['key'], d['lvl'])
    if not MA.have(game, test, n):
        game.msg(f'The master shakes her head. "Bring {what}, and we will see."', 'info')
        return
    MA.take(game, test, n)
    game.player.__dict__.setdefault('life_tests', set()).add((d['key'], d['lvl']))
    game.msg(f'The master turns your work over under the lamp, and nods. Your {LS.LIFE[d["key"]]["name"]} can rise '
             'again; word goes to the far master that you need not come.', 'unique')
    MS.complete(game, m, [m.giver])
    LS.gain(game, d['key'], 0.01)


# ------------------------------------------------------------------ the master's board
def order_for(game, key):
    return next((m for m in game.missions if m.kind == 'order' and getattr(m, 'guild', None) == key
                 and m.state in ('active', 'turnin')), None)


def make_order(game, key):
    """One order at a time, a half better paid than a town board's, at your height."""
    from . import mastery as MA
    from . import lifeskills as LS
    from . import jobs as JB
    from . import missions as MS
    here = game.here
    crafts = ORDER_CRAFT.get(key)
    if not here or not crafts:
        return None
    best = max(crafts, key=lambda k: LS.rank(game, k))
    r = LS.rank(game, best)
    if r < 3:
        game.msg('"Come back when your hands know a little more of the work."', 'info')
        return None
    t = MA.tier_for(r)
    n = random.randint(1, 2) if best in MARK_OF else random.randint(2, 4)
    data = dict(key=best, tier=t, n=n, at=r, who=G().GUILDS[key]['short'], q=3 + r // 6,
                layer='simple' if r < 15 else 'hearty' if r < 35 else 'luxury')
    what, _test, _n = MA.order_wants(game, data)
    why = random.choice(ORDER_WHY.get(key, ['The hall has an order.']))
    m = JB.mission(game, here, 'order', f'{G().GUILDS[key]["short"]}: {why.rstrip(".")}',
                   f'{why} The master wants {what}.', (8 + r * .8 + n * 3) * 1.5, (3, 6), game.day + 20, **data)
    m.guild = key
    here.board.append(m)
    if MS.accept(game, here, m) is False:
        if m in here.board:
            here.board.remove(m)
        return None
    if m in here.board:
        here.board.remove(m)
    return m


# ------------------------------------------------------------------ the secrets
def secret_option(game, key):
    if key not in SECRET or G().rank(game, key) < 3:
        return []
    return [(SECRET[key], 'secret')]


def secret(game, key):
    from . import events as EV
    from .money import fmt
    p = game.player
    if key == 'hammer':
        items = [i for i in p.inv if i.k == 'gear' and getattr(i, 'made', None) and i.made[0] == 'smithing'
                 and any(isinstance(v, int) for _s, v in i.aff) and not getattr(i, 'tempered', False)]
        opts = [(f'{i.display_name()} ({fmt(100)})', f'temper:{i.id}') for i in items[:12]]
        EV.ask(game, 'cgsecret', 'Re-tempering', 'Back into the fire, and quenched again: what the metal gives it '
               'gives once more, better or worse. Each piece only once.', opts + [('Never mind', 'bye')], guild=key)
    elif key == 'lodge':
        items = [i for i in p.inv if i.k == 'npart']
        opts = [(f'{i.display_name()} ({fmt(200)})', f'mount:{i.id}') for i in items[:12]]
        EV.ask(game, 'cgsecret', 'Mounting', 'A part of a named beast, set on a board of oak: a trophy to sell, or to '
               'give a lord.', opts + [('Never mind', 'bye')], guild=key)
    elif key == 'needle':
        cloth = sum(i.n for i in p.inv if i.k == 'mat' and i.t.startswith('cloth_'))
        opts = [(f'{txt.capitalize()} ({fmt(150)}, one bolt of cloth)', f'livery:{k}' if cloth else None)
                for k, (_c, txt) in LIVERY.items()]
        if getattr(p, 'livery', None):
            opts.append(('Take the livery off', 'livery:off'))
        EV.ask(game, 'cgsecret', 'Livery', 'Clothes in a people\'s colours: their land thinks better of you, and anyone '
               'can see whose colours you wear.', opts + [('Never mind', 'bye')], guild=key)
    elif key == 'ladle':
        here = game.here
        dishes = [i for i in p.inv if i.k == 'dish']
        n = sum(i.n for i in dishes)
        last = p.__dict__.setdefault('tables', {}).get(here.id if here else -1, -99)
        ok = n >= 3 and game.day - last >= 7
        EV.ask(game, 'cgsecret', 'A table for the house', 'You cook for the whole inn: three dishes of your own, laid '
               'out on the long table. Once a week in a town.' + ('' if n >= 3 else ' You have not got three dishes.'),
               [('Lay the table', 'table' if ok else None), ('Never mind', 'bye')], guild=key)


def r_secret(game, choice, ctx):
    from .money import fmt
    p = game.player
    if not choice or choice == 'bye':
        return
    kind, _, arg = choice.partition(':')
    if kind == 'temper':
        it = next((i for i in p.inv if str(i.id) == arg), None)
        if not it or p.gold < 100:
            game.msg('That costs 1 silver.', 'bad')
            return
        p.gold -= 100
        before = sum(v for _s, v in it.aff if isinstance(v, int))
        for a in it.aff:
            if isinstance(a[1], int):
                a[1] = max(1, round(a[1] * random.uniform(.7, 1.35)))
        it.tempered = True
        after = sum(v for _s, v in it.aff if isinstance(v, int))
        game.msg(f'You re-temper {it.display_name()}. ' + ('It comes out better.' if after > before else
                 'It comes out worse. The metal has its own mind.' if after < before else 'Nothing changes.'),
                 'good' if after >= before else 'bad')
        game.end_turn(40)
    elif kind == 'mount':
        it = next((i for i in p.inv if str(i.id) == arg), None)
        if not it or p.gold < 200:
            game.msg('That costs 2 silver.', 'bad')
            return
        p.gold -= 200
        from .entities import Item
        tr = Item(game.new_id(), 'trophy', getattr(it, 'beast', 'a beast'))
        tr.worth = max(20, round(it.value() / 100 * 3))
        p.inv.remove(it)
        game.add_to_inv(tr) or game.spill(game.map, p.x, p.y, tr)
        game.msg(f'You set it on oak: {display(game, tr)}.', 'gold')
        game.end_turn(40)
    elif kind == 'livery':
        if arg == 'off':
            p.livery = None
            game.msg('You put the livery away.', 'info')
            return
        cloth = next((i for i in p.inv if i.k == 'mat' and i.t.startswith('cloth_')), None)
        if not cloth or p.gold < 150:
            game.msg('A livery takes a bolt of cloth and 1 silver 50.', 'bad')
            return
        p.gold -= 150
        game.remove_one(cloth)
        p.livery = arg
        p.livery_seen = set()
        game.msg(f'You sew a livery in {LIVERY[arg][1]}, and put it on.', 'gold')
        game.end_turn(60)
    elif kind == 'table':
        here = game.here
        dishes = [i for i in p.inv if i.k == 'dish']
        if sum(i.n for i in dishes) < 3 or not here:
            return
        n = 3
        for it in dishes:
            while n and it in p.inv:
                game.remove_one(it)
                n -= 1
        p.__dict__.setdefault('tables', {})[here.id] = game.day
        here.rep = min(100, here.rep + 4)
        here.table_day = game.day
        game.msg('The whole inn eats at your table. They talk, as people do over a good meal.', 'gold')
        for _ in range(2):
            game.msg(game.rumor(), 'info')
        game.end_turn(60)


def livery_fg(p):
    k = getattr(p, 'livery', None)
    return LIVERY[k][0] if k in LIVERY else None


def on_enter_town(game, s):
    """A livery in this people's colours: some standing, once per settlement."""
    p = game.player
    k = getattr(p, 'livery', None)
    if k and s.race == k and s.id not in p.__dict__.setdefault('livery_seen', set()):
        p.livery_seen.add(s.id)
        s.rep = min(100, s.rep + 3)
        game.msg(f'People here see {LIVERY[k][1]} on you, and nod.', 'good')


# ------------------------------------------------------------------ the trophy (an item)
def display(game, it):
    return f'Mounted head of {it.t}'


def lines(game, it):
    return ['A trophy of a named beast, set on oak by the Tanners\' Lodge. A lord may take it as a gift.']


def value(game, it):
    return getattr(it, 'worth', 20)


def glyph(it):
    return '¥'


def color(it):
    return (200, 160, 110)


def trophy_option(game):
    it = next((i for i in game.player.inv if i.k == 'trophy'), None)
    return [(f'Give the {display(game, it).lower()} as a gift', 'trophy')] if it else []


def give_trophy(game):
    it = next((i for i in game.player.inv if i.k == 'trophy'), None)
    if not it:
        return False
    game.player.inv.remove(it)
    return True


# ------------------------------------------------------------------ the guild day
def day_of(key, s):
    """The guild's day in this hall's town: the same day each year, between spring and autumn."""
    h = (s.id * 2654435761 + NEW.index(key) * 40503) & 0xffff
    return (3 + h % 6, 1 + (h >> 5) % 28, 1)


def days_today(game, s, day):
    from . import feasts as FE
    out = []
    for key in NEW:
        now = getattr(game.world, 'guild_day_now', None) == (s.id, day)       # the debug menu's guild day
        if s.id in getattr(game.world, 'guild_halls', {}).get(key, ()) and (now or FE._on(day, day_of(key, s))):
            out.append(FE.GUILD_DAYS[key])
    return out


def entries(game, key):
    """What you may enter in the contest: your own work of the guild's craft."""
    p = game.player
    if key == 'ladle':
        from . import cooking as CK
        return [i for i in p.inv if i.k == 'dish' and i.t in CK.DISHES]
    craft = next(c for c, k in MARK_OF.items() if k == key)
    return [i for i in p.inv if i.k == 'gear' and getattr(i, 'made', None) and i.made[0] == craft]


def score(it):
    from . import crafts as CRF
    if it.k == 'dish':
        from . import cooking as CK
        return {'simple': 3, 'hearty': 8, 'luxury': 14}.get(CK.DISHES[it.t][1], 3)
    craft, m, q = it.made
    return CRF.TIER_VAL[CRF.STUFF[craft][m][1]] + 2 * len(it.aff) + (6 if q == 'masterwork' else 0) \
        + (-2 if q == 'crude' else 0)


def contest(game, key, npc=None):
    """Your best piece against the town's best: tier, powers and masterwork, and a roll."""
    from . import news as NW
    from .money import fmt
    ents = entries(game, key)
    if not ents:
        game.msg('You have nothing of your own making to enter. Next year, then.', 'info')
        return False
    best = max(ents, key=score)
    mine = score(best) + random.randint(0, 8)
    theirs = 6 + random.randint(0, 12) + game.player.lvl // 4
    g = G().GUILDS[key]
    s = game.here
    if mine <= theirs:
        game.msg(f'The judges look long at {best.display_name()}, and give the ribbon to a local master. Next year.', 'info')
        return True
    kind, what, n = PRIZE[key]
    if kind == 'coin':
        game.player.gold += what
        got = fmt(what)
    elif kind == 'mat':
        from . import crafts as CRF
        CRF.give(game, what, n)
        got = f'{n} x {CRF.mat_name(what)}'
    else:
        from .entities import Item
        it = Item(game.new_id(), 'leather', what, n)
        game.add_to_inv(it) or game.spill(game.map, game.player.x, game.player.y, it)
        got = f'{n} pieces of {what} leather'
    game.msg(f'{best.display_name()} wins the ribbon of {g["short"]}! The prize: {got}.', 'unique')
    if s:
        s.rep = min(100, s.rep + 3)
        NW.post(game, 'guildday', f'{game.player.name} won the ribbon on {GUILD_DAY_NAME[key]} in {s.name}.', s.x, s.y)
    return True


# ------------------------------------------------------------------ the streets and the happenings
HALL_DECO = {'lodge': ('‡', (170, 120, 80)), 'needle': ('o', (120, 150, 210))}     # hides on racks, the dyers' vats


def dress_street(m, pl, key):
    """Outside the hall: the tanners' hides on racks, the dyers' vats (only a look; the smiths' anvil sparks)."""
    deco = HALL_DECO.get(key)
    door = getattr(pl, 'door', None)
    if not deco or not door:
        return
    over = getattr(m, 'over', None)
    if over is None:
        m.over = over = {}
    n = 0
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            x, y = door[0] + dx, door[1] + dy
            if n >= 3 or not m.inb(x, y) or max(abs(dx), abs(dy)) < 2 or (x, y) in pl.inside:
                continue
            if D.TILES[m.tile(x, y)].walk and m.tile(x, y) not in (D.DOOR, D.ROAD) and (x * 7 + y * 3) % 4 == 0:
                over[y * m.w + x] = (deco[0], deco[1], None)
                n += 1
    m._look = None


EMPTY = {'lodge': ('¦', (110, 100, 90)), 'needle': ('o', (90, 84, 76))}      # bare racks, dry vats


def show_dry(game, m, s):
    """After a quarrel over the water lost: the losing hall's racks stand empty, or its vats dry, for a season."""
    over = getattr(m, 'over', None)
    if not over:
        return
    lose = dry(game, s)
    for k, (ch, col) in HALL_DECO.items():
        full, empty = (ch, col), EMPTY[k]
        want = empty if lose == k else full
        for i, v in list(over.items()):
            if (v[0], tuple(v[1])) in (full, empty) and (v[0], tuple(v[1])) != want:
                over[i] = (want[0], want[1], None)
    m._look = None


def happenings(game, s):
    """The crafts guilds' small happenings in a town with one of their halls."""
    halls = getattr(game.world, 'guild_halls', {})
    out = []
    if s.id in halls.get('hammer', ()):
        out.append('strongarm')
    if any(s.id in halls.get(k, ()) for k in NEW):
        out.append('journeyman')
    return out


def next_hall(game, s):
    """The nearest other town with a crafts guild hall: where a journeyman walks on to."""
    halls = getattr(game.world, 'guild_halls', {})
    ids = {i for k in NEW for i in halls.get(k, ()) if i != s.id}
    if not ids:
        return None
    return min(ids, key=lambda i: cheb(game.world.settlements[i].x, game.world.settlements[i].y, s.x, s.y))


def talk_happening(game, npc):
    p = game.player
    m = game.map
    if npc.role == 'strongarm':
        m.mons.remove(npc)
        if getattr(m, 'arm_day', None) == game.day:
            return
        m.arm_day = game.day
        game.msg('"The striker\'s down with a fever and the order is due." You swing the sledge at the forge until '
                 'evening. Your arms ache; the smith pays you 40 coppers and shows you a trick with the tongs.', 'good')
        p.gold += 40
        from . import lifeskills as LS
        LS.gain(game, 'smithing', 4)
        game.end_turn(D.DAY_LEN // 4, True)
        return
    to = getattr(npc, 'bound', None)
    where = game.world.settlements[to].name if to is not None else 'the next town'
    game.say(npc, f'"On my wander year, friend. A season in every hall, and then they call me master. Next it is '
                  f'{where}; they say the work there is hard and the beer is good."')
    if to is not None:
        game.reveal_place(game.world.settlements[to].x, game.world.settlements[to].y)


# ------------------------------------------------------------------ the master's window
def master_options(game, key):
    """The crafts guilds' options at the master's table (guilds.talk)."""
    GU = G()
    if GU.GUILDS[key]['kind'] != 'life' or not GU.state(game)[key]['joined']:
        return []
    from .money import fmt
    if shut(game, key):
        return [(f'The hall will not deal with you until {_shut_day(game, key)}', None)]
    opts = raise_option(game, key)
    for m in guild_missions(game, key):
        opts.append((f'Report: {m.title}', f'cgreport:{m.id}'))
    if key in NEW:
        opts.append(('Guild work of the hall', 'cgjobs'))
    opts += quarrel_option(game, key)
    if key == 'hammer' and game.player.__dict__.get('guild_mine') is not None:
        opts.append(('Your share of the guild mine\'s ore', 'cgmine'))
    for m in tests_here(game, key):
        from . import lifeskills as LS
        opts.append((f'Show your work for the test of {LS.LIFE[m.data["key"]]["name"]} {m.data["lvl"]}', f'cgtest:{m.id}'))
    if key in ORDER_CRAFT:
        o = order_for(game, key)
        opts.append(('The master\'s board: an order' if not o else 'The master\'s board: your order is in your journal',
                     'cgorder' if not o else None))
    work = marked_work(game, key)
    if work:
        opts.append((f'Sell your marked work to the hall ({fmt(sum(hall_price(i) for i in work))})', 'cgsell'))
    opts += secret_option(game, key)
    return opts


def resolve(game, choice, key):
    """True when the choice was one of ours."""
    if choice == 'raise':
        do_raise(game, key)
    elif choice.startswith('cgtest:'):
        hand_in_test(game, int(choice[7:]))
    elif choice == 'cgorder':
        m = make_order(game, key)
        if m:
            game.msg(f'The master hands you an order: {m.desc}', 'gold')
    elif choice == 'cgsell':
        sell_marked(game, key)
    elif choice == 'cgjobs':
        master = next((o.name for o in game.map.mons if getattr(o, 'guild', None) == key), None)
        jobs_window(game, key, master)
    elif choice.startswith('cgreport:'):
        report(game, int(choice[9:]))
    elif choice == 'cgquarrel':
        quarrel(game, key)
    elif choice == 'cgmine':
        mine_share(game)
    elif choice == 'secret':
        secret(game, key)
    else:
        return False
    return True


# ------------------------------------------------------------------ round 49: the guild jobs
JOBS = ('fetch', 'world', 'wander', 'forger', 'mine', 'heirloom')
JOB_NAME = {'fetch': 'Fetch the stuff', 'world': 'Work for the world', 'wander': "The journeyman's wander year",
            'forger': 'The false mark', 'mine': 'The fallen mine', 'heirloom': "The founder's heirloom",
            'quarrel': 'The quarrel over the water'}
FETCH = {'hammer': ('find', 'a sack of deep ore'), 'needle': ('find', 'a bolt of old Fey Silk'),
         'lodge': ('hunt', None), 'ladle': ('bring', 'spice')}
HEIRLOOM = {
    'hammer': ('The founder\'s sword', 'The founder\'s Varnish sword lies broken in three pieces, in three old places. '
               'Bring them back, and the hall will forge it whole.'),
    'lodge': ('The founder\'s beast', 'The beast that killed our founder still walks. The Lodge has waited a long time.'),
    'needle': ('The realm\'s banner', 'The old banner of the realm, that our founder wove, hangs forgotten in a lord\'s '
               'seat and its pieces are lost. Bring them home.'),
    'ladle': ('The king\'s meal', 'Our founder cooked for a king once. Cook the meal again: wine, spice, and a dish of '
              'your own, carried to the great city.'),
}
# the guild's gift at the end of a job: (kind, what by rank 0..4)
GIFT = {'hammer': ('mat', ['bar_iron', 'bar_silver', 'bar_deepiron', 'bar_blackiron', 'bar_adamant']),
        'needle': ('mat', ['cloth_wool', 'cloth_felt', 'cloth_spidersilk', 'cloth_shadowsilk', 'cloth_queensilk']),
        'lodge': ('leather', ['leather', 'sturdy', 'thick', 'cavefur', 'drake']),
        'ladle': ('coin', [100, 200, 300, 500, 800])}


def _hall_people(game, key):
    halls = getattr(game.world, 'guild_halls', {}).get(key, ())
    return [game.world.settlements[i] for i in halls]


def _need(game, key, s, kind, master, steps, line, title, coin, **extra):
    """A guild job as a folk-in-need record, so the folk maker carries it (steps, twists, the memory)."""
    nd = dict(id=game.new_id(), sid=s.id, name=master.split(' ')[-1] if master else 'the master', title=master or 'The master',
              gender='male', people=s.race, trade='guild', motive='skill', src='guild', line=line, steps=steps,
              made=game.day, until=game.day + 30, coin=coin, reward='guild', twist=None, seed=None, hint=None,
              guild=key, job=kind, job_title=f'{G().GUILDS[key]["short"]}: {title}')
    nd.update(extra)
    return nd


def offers(game, key, master=None):
    """The guild jobs this hall has for you now: up to three, of the kinds that fit the world and your rank."""
    from . import folkquests as FQ
    from . import lifeskills as LS
    s = game.here
    if not s or key not in NEW:
        return []
    r = G().rank(game, key)
    out = []
    rnd_coin = lambda n: (n + random.randint(0, 4)) * 100           # noqa: E731  (little coin: the guild pays in kind)
    # 1. fetch: the higher the rank, the more dangerous the place
    verb, thing = FETCH[key]
    if verb == 'find':
        ds = sorted(FQ._dungeons(game, s), key=lambda d: d.depth)
        if ds:
            d = ds[min(len(ds) - 1, r * len(ds) // 5)]
            out.append(_need(game, key, s, 'fetch', master, [dict(v='find', did=d.id, relic=thing, name=d.name)],
                             f'We are short of the best stuff. {thing[0].upper() + thing[1:]} lies in {d.name}.',
                             f'{thing[0].upper() + thing[1:]}', rnd_coin(4)))
    elif verb == 'hunt':
        ns = FQ._named(game, s)
        if ns:
            n = ns[0]
            out.append(_need(game, key, s, 'fetch', master, [dict(v='hunt', nid=n.id, name=n.name)],
                             f'A hide off {n.name} would make the Lodge\'s name for a year.', f'The hide of {n.name}',
                             rnd_coin(5)))
    else:
        out.append(_need(game, key, s, 'fetch', master, [dict(v='bring', good=thing, qty=2)],
                         'The hall\'s kitchen is out of spice, and the guild day is near.', 'Spice for the hall',
                         rnd_coin(3)))
    # 2. work for the world: pieces the world needs, made by you
    craft = {'hammer': 'smithing', 'lodge': 'leatherworking', 'needle': 'tailoring', 'ladle': 'cooking'}[key]
    if LS.rank(game, craft) >= 3:
        why = random.choice(ORDER_WHY[key])
        what = 'dishes of your own cooking' if key == 'ladle' else f'pieces of your own {LS.LIFE[craft]["name"].lower()}'
        out.append(_need(game, key, s, 'world', master, [dict(v='piece', craft=craft, n=2, what=what)], why,
                         why.rstrip('.'), rnd_coin(3)))
    # 3. the wander year: a journeyman to a hall in another town, of another people if it can be
    others = [o for o in _hall_people(game, key) if o.id != s.id]
    if others:
        o = min(others, key=lambda o: (o.race == s.race, cheb(o.x, o.y, s.x, s.y)))
        nm = random.choice(['Jory', 'Wenna', 'Tam', 'Ilsa', 'Bram', 'Odo'])
        out.append(_need(game, key, s, 'wander', master, [dict(v='go', sid=o.id, name=o.name, who='the hall there')],
                         f'{nm}, our journeyman, goes on his wander year to the hall in {o.name}. The roads are bad; walk '
                         'with him.', f'{nm}\'s wander year', rnd_coin(3), to_sid=o.id))
    # 4. the false mark: a forger in a city's poor quarter
    cities = [o for o in game.world.settlements if o.is_city and o.id != s.id and cheb(o.x, o.y, s.x, s.y) <= 80]
    if cities and r >= 1:
        o = min(cities, key=lambda o: cheb(o.x, o.y, s.x, s.y))
        out.append(_need(game, key, s, 'forger', master, [dict(v='go', sid=o.id, name=o.name, who='the forger')],
                         f'Goods with our mark, and not ours, on the market of {o.name}. Find the forger in the poor '
                         'quarter.', 'The false mark', rnd_coin(5), twist='forger'))
    # 6. the fallen mine (the Hammer and Tongs): kobolds or worse in the guild's mine
    if key == 'hammer' and not game.player.__dict__.get('guild_mine'):
        ns = FQ._nests(game, s)
        if ns:
            d = ns[0]
            out.append(_need(game, key, s, 'mine', master, [dict(v='clear', did=d.id, boss=d.boss, name=d.name)],
                             f'Our mine in {d.name} is lost to what came up from below. Clear it, and every member may '
                             'dig there again.', 'The fallen mine', rnd_coin(6), mine=d.id))
    # 7. the founder's heirloom, once, at Master
    done = game.player.__dict__.setdefault('heirlooms', set())
    if r >= 3 and key not in done:
        steps = heirloom_steps(game, key, s)
        if steps:
            title, line = HEIRLOOM[key]
            out.append(_need(game, key, s, 'heirloom', master, steps, line, title, rnd_coin(10)))
    taken = {m.data.get('job') for m in game.missions if m.kind == 'folk' and m.data.get('guild') == key
             and m.state in ('active', 'turnin')}
    out = [nd for nd in out if nd['job'] not in taken]
    random.shuffle(out)
    return out[:3]


def heirloom_steps(game, key, s):
    from . import folkquests as FQ
    ds = FQ._dungeons(game, s)
    if key == 'hammer':
        if len(ds) < 3:
            return None
        ds = sorted(ds, key=lambda d: -d.depth)[:3]
        return [dict(v='find', did=d.id, relic=f'a piece of the founder\'s sword ({k} of 3)', name=d.name)
                for k, d in enumerate(ds, 1)]
    if key == 'lodge':
        ns = sorted(FQ._named(game, s), key=lambda n: -getattr(n, 'lvl', 0))
        return [dict(v='hunt', nid=ns[0].id, name=ns[0].name)] if ns else None
    if key == 'needle':
        hs = FQ._seats(game, s)
        if not hs or not ds:
            return None
        return [dict(v='seat', hid=hs[0].id, name=hs[0].title), dict(v='find', did=ds[0].id, relic='the banner\'s lost '
                                                                     'corner', name=ds[0].name)]
    big = [o for o in game.world.settlements if o.kind == 'metropolis'] or [o for o in game.world.settlements if o.is_city]
    if not big:
        return None
    return [dict(v='bring', good='wine', qty=1), dict(v='go', sid=big[0].id, name=big[0].name, who='the king\'s steward'),
            dict(v='dish')]


def has_pieces(game, st):
    return len(_pieces(game, st)) >= st['n']


def _pieces(game, st):
    p = game.player
    if st['craft'] == 'cooking':
        return [i for i in p.inv if i.k == 'dish']
    return [i for i in p.inv if i.k == 'gear' and getattr(i, 'made', None) and i.made[0] == st['craft']
            and not game.is_equipped(i)]


def take_pieces(game, st):
    n = st['n']
    for it in _pieces(game, st):
        if n <= 0:
            break
        if it.k == 'dish':
            game.remove_one(it)
        else:
            game.player.inv.remove(it)
        n -= 1


def jobs_window(game, key, master):
    from . import events as EV
    from . import folkquests as FQ
    from .money import fmt
    if shut(game, key):
        game.msg(f'"You took the other side at the water. Come back after {_shut_day(game, key)}."', 'bad')
        return
    lst = offers(game, key, master)
    s = game.here
    FQ.store(game).setdefault(s.id, [])
    game.world.__dict__.setdefault('guild_offers', {})[key] = lst
    if not lst:
        game.msg('"Nothing the hall needs of you just now."', 'info')
        return
    text = '"The hall has work for a member:"\n\n' + '\n'.join(f'- {nd["line"]} ({FQ.brief(game, nd)})' for nd in lst)
    opts = [(f'{nd["job_title"]} ({fmt(nd["coin"])} and the guild\'s thanks)', f'take:{i}') for i, nd in enumerate(lst)]
    EV.ask(game, 'cgjob', G().GUILDS[key]['short'], text, opts + [('Not now', 'bye')], guild=key)


def r_job(game, choice, ctx):
    from . import folkquests as FQ
    key = ctx['guild']
    if not choice or not choice.startswith('take:'):
        return
    lst = game.world.__dict__.get('guild_offers', {}).get(key, [])
    i = int(choice[5:])
    if i >= len(lst):
        return
    nd = lst.pop(i)
    FQ.store(game).setdefault(nd['sid'], []).append(nd)
    m = FQ.take(game, nd['id'])
    if m:
        m.guild = key
    elif nd in FQ.store(game).get(nd['sid'], []):
        FQ.store(game)[nd['sid']].remove(nd)
    return m


def guild_missions(game, key):
    from . import folkquests as FQ
    return [m for m in game.missions if m.kind == 'folk' and m.data.get('guild') == key and m.state in ('active', 'turnin')
            and (m.state == 'turnin' or FQ._ready(game, m))]


def report(game, mid):
    from . import folkquests as FQ
    m = next((x for x in game.missions if x.id == mid), None)
    if m and (m.state == 'turnin' or FQ._ready(game, m)):
        FQ.finish(game, m, None)


def reward(game, m):
    """The guild pays in kind: materials of the craft by your rank, standing in two towns, a mine, a piece of your own."""
    from . import jobs as JB
    d = m.data
    key = d['guild']
    kind = d.get('job')
    r = G().rank(game, key)
    if kind == 'wander' and d.get('to_sid') is not None:
        JB.effects(game, town=[(m.giver, 2), (d['to_sid'], 3)], quiet=True)
    if kind == 'mine':
        game.player.guild_mine = d.get('mine')
        return 'The mine is the guild\'s again. Members may dig there, and the hall gives you a share of its ore.'
    if kind == 'heirloom':
        game.player.__dict__.setdefault('heirlooms', set()).add(key)
        from .entities import make_gear
        fam = {'hammer': 'longsword', 'lodge': 'leather', 'needle': 'robe', 'ladle': 'sash'}[key]
        from .itemdata import grades
        base = grades(fam)[-1]
        it = make_gear(game, base, 'rare', game.player.lvl + 3)
        it.name = f'{G().GUILDS[key]["short"]}\'s Gift, {D.BASES[base]["name"]}'
        it.gmark = key
        game.add_to_inv(it) or game.spill(game.map, game.player.x, game.player.y, it)
        G().state(game)[key]['rep'] += 120
        return f'The whole hall stands when you come in. The master gives you {it.name}, made for you.'
    gk, ladder = GIFT[key]
    what = ladder[min(4, r + (1 if kind == 'fetch' else 0))]
    if gk == 'coin':
        game.player.gold += what
        from .money import fmt
        return f'The hall adds {fmt(what)} from the kitchen\'s box.'
    if gk == 'mat':
        from . import crafts as CRF
        CRF.give(game, what, 2)
        return f'The hall gives you two of {CRF.mat_name(what)}.'
    from .entities import Item
    it = Item(game.new_id(), 'leather', what, 2)
    game.add_to_inv(it) or game.spill(game.map, game.player.x, game.player.y, it)
    return f'The hall gives you {it.display_name()}.'


def mine_share(game):
    """Once a week, a member who won back the mine takes a share of its ore at the Hammer and Tongs."""
    from . import crafts as CRF
    p = game.player
    if game.day - p.__dict__.get('mine_day', -99) < 7:
        game.msg('"Your share for this week is taken. The mine is not a well."', 'info')
        return
    p.mine_day = game.day
    r = G().rank(game, 'hammer')
    ore = ['ore_iron', 'ore_silver', 'ore_deepiron', 'ore_blackiron', 'ore_adamant'][min(4, r)]
    CRF.give(game, ore, 3)
    game.msg(f'From the guild\'s mine: three of {CRF.mat_name(ore)}.', 'good')


# ------------------------------------------------------------------ 5. the quarrel over the water
def quarrel_state(game):
    """On the player: {'loser': guild, 'until': day, 'sid': town} while a quarrel's consequence lasts."""
    return game.player.__dict__.setdefault('water', {})


def quarrel_option(game, key):
    if key not in ('lodge', 'needle'):
        return []
    q = quarrel_state(game)
    if q.get('year') == game.day // 360:
        return []
    return [('The tanners and the dyers quarrel over the water', 'cgquarrel')]


def quarrel(game, key):
    from . import events as EV
    from . import lifeskills as LS
    both = min(LS.rank(game, 'leatherworking'), LS.rank(game, 'tailoring'))
    EV.ask(game, 'cgquarrel', 'The quarrel over the water', 'The tanners soak their hides upstream, and the dyers '
           'downstream say their vats run brown. Both halls want you on their side; the Watch wants it settled.',
           [('Side with the tanners', 'lodge'), ('Side with the dyers', 'needle'),
            (f'Mediate (Leatherworking and Tailoring 15; yours {both})', 'mediate' if both >= 15 else None),
            ('Keep out of it', 'bye')], guild=key)


def r_quarrel(game, choice, ctx):
    from . import jobs as JB
    from . import calendar as CAL
    if not choice or choice == 'bye':
        return
    GU = G()
    q = quarrel_state(game)
    here = game.here
    q.clear()
    q.update(year=game.day // 360, sid=here.id if here else None)
    if choice == 'mediate':
        ok = random.random() < .6
        for k in ('lodge', 'needle'):
            st = GU.state(game)[k]
            st['rep'] = max(0, st['rep'] + (25 if ok else -25))
            st['paid'] = min(st['paid'], earned(game, k))
        game.msg('You get both halls round one table, and in the end the tanners move their pits a bend downstream. '
                 'Both think a little better of you.' if ok else 'You talk until the lamps burn down, and both halls '
                 'leave angrier than they came. Each thinks you favoured the other.', 'good' if ok else 'bad')
        if here:
            JB.effects(game, town=[(here.id, 3 if ok else -1)], quiet=True)
        return
    win, lose = choice, ('needle' if choice == 'lodge' else 'lodge')
    st = GU.state(game)[lose]
    st['rep'] = max(0, st['rep'] - 90)
    st['paid'] = min(st['paid'], earned(game, lose))          # standing is your rank: it can fall
    GU.state(game)[win]['rep'] += 30
    q.update(loser=lose, until=game.day + 90)
    from .entities import Item
    tok = Item(game.new_id(), 'favour', 'repair' if win == 'lodge' else 'bed')
    tok.who = GU.GUILDS[win]['short']
    tok.giver = GU.GUILDS[win]['name']
    game.add_to_inv(tok) or game.spill(game.map, game.player.x, game.player.y, tok)
    game.msg(f'You side with {GU.GUILDS[win]["short"]}. {GU.GUILDS[lose]["short"]} shut their bench and board to you '
             f'until {CAL.short(game.day + 90)}; {GU.GUILDS[win]["short"]} give you a favour.', 'gold')
    if here:
        JB.effects(game, town=[(here.id, 1)], quiet=True)


def shut(game, key):
    q = quarrel_state(game)
    return q.get('loser') == key and game.day < q.get('until', 0)


def _shut_day(game, key):
    from . import calendar as CAL
    return CAL.short(quarrel_state(game).get('until', game.day))


def dry(game, s):
    """The town shows it: the losing tanners' racks stand empty, the losing dyers' vats stay dry."""
    q = quarrel_state(game)
    if q.get('sid') == s.id and game.day < q.get('until', 0):
        return q.get('loser')
    return None


def register():
    from . import events as EV
    from . import entities as EN
    EV.RESOLVERS['cgsecret'] = r_secret
    EV.RESOLVERS['cgjob'] = r_job
    EV.RESOLVERS['cgquarrel'] = r_quarrel
    EN.CRAFT['trophy'] = 'craftguilds'


register()
