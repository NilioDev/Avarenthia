"""The long road of the life skills (part 2): the master's tests, orders, and the three great masters.

Master's tests: at rank 25 and again at 40 a life skill stops until a master of it has seen your work. The master
lives in a town somewhere in the world (a job in your journal tells where) and asks one thing at your height: a
fish of a better tier, herbs from harder land, a piece you made of better stuff. Bring it, and the skill goes on.

Orders: the town boards ask for work at your own height (a piece of your best craft, a few drinks, a strong
draught, good dishes). They pay modestly, and they teach without gathering.

The great masters: one smith, one leatherworker and one tailor in the whole world, far from the roads. Nobody marks
them on a map: you hear of them at an inn or from a tanner. Their test is in three parts: bring a top find of their
craft, bring a part of a notorious or legendary named beast, and win back the workshop they lost to whatever lives
there now. After that they unmake for you (crafts.unmake_menu): one power moved per visit, for gold, at 50%.

State: the master sites on world.masters; what you have done on p.life_tests, p.masters and p.master_used."""
import random

from . import data as D
from . import lifeskills as LS
from .worldgen import cheb

LOOK = {'master': ('Φ', (232, 196, 120)), 'lostshop': ('╪', (150, 140, 128))}
TRADE = {'fishing': 'fisher', 'foraging': 'herb-gatherer', 'alchemy': 'alchemist', 'brewing': 'brewer',
         'mining': 'miner', 'smithing': 'smith', 'hunting': 'huntsman', 'skinning': 'skinner', 'cooking': 'cook',
         'leatherworking': 'leatherworker', 'tailoring': 'tailor'}
GREAT = {'smithing': ('smith', 'forge'), 'leatherworking': ('leatherworker', 'tannery'), 'tailoring': ('tailor', 'weaving hall')}
PRICE = 30000                                   # three gold for one Unmake
TIERS_UP = 'BCDET'


# ------------------------------------------------------------------ what a master asks
def _tier_of(it):
    """The tier of a gathered or made thing, or None."""
    from . import foraging as FG
    from . import crafts as CRF
    if it.k == 'fish':
        return LS.FISH[it.t][6]
    if it.k == 'plant' and it.t in FG.HERBS:
        return FG.HERBS[it.t][0]
    if it.k == 'mat':
        return CRF.tier_of(it.t)
    if it.k == 'leather':
        return CRF.LEATHERS.get(it.t, CRF.LEATHERS['leather'])[1]
    if it.k == 'part':
        from . import beastparts as BP
        return BP.tier(it.t)
    if it.k == 'gear' and getattr(it, 'made', None):
        craft, m, _q = it.made
        return CRF.STUFF[craft][m][1]
    return None


def at_least(t, want):
    return t is not None and ('ABCDET'.index(t) >= 'ABCDET'.index(want) or t == 'T')


def wants(key, lvl):
    """(what the master asks, a test on an item, how many)."""
    t = 'C' if lvl == 25 else 'D'
    if key == 'fishing':
        return (f'a fish of tier {t} or better', lambda i: i.k == 'fish' and at_least(_tier_of(i), t), 1)
    if key == 'foraging':
        return (f'three herbs of tier {t} or better', lambda i: i.k == 'plant' and at_least(_tier_of(i), t), 3)
    if key == 'alchemy':
        q = 6 if lvl == 25 else 9
        return (f'a brew of strength {q} or more', lambda i: i.k == 'draught' and getattr(i, 'q', 0) >= q, 1)
    if key == 'brewing':
        ok = ('stout', 'cordial', 'elven_wine') if lvl == 25 else ('juniper_spirits', 'spiced_spirits', 'royal_mead')
        from . import brewing as BRW
        names = ' or '.join(BRW.RECIPES[BRW.BY_FOOD[f]][0] for f in ok)
        return (f'a {names} of your own brewing', lambda i: i.k == 'food' and i.t in ok and getattr(i, 'origin', None), 1)
    if key == 'mining':
        return (f'three ores or bars of tier {t} or better', lambda i: i.k == 'mat' and not i.t.startswith('cloth_')
                and at_least(_tier_of(i), t), 3)
    if key in ('smithing', 'leatherworking', 'tailoring'):
        return (f'a fine or masterwork piece you made of tier {t} stuff',
                lambda i: i.k == 'gear' and getattr(i, 'made', (None,))[0] == key and i.made[2] != 'crude'
                and at_least(_tier_of(i), t), 1)
    if key == 'hunting':
        return (f'two parts of a beast of tier {t} or better', lambda i: i.k == 'part' and at_least(_tier_of(i), t), 2)
    if key == 'skinning':
        return (f'three pieces of tier {t} leather', lambda i: i.k == 'leather' and at_least(_tier_of(i), t), 3)
    from . import cooking as CK
    layer = 'hearty' if lvl == 25 else 'luxury'
    return (f'three {layer} dishes of your own cooking',
            lambda i: i.k == 'dish' and i.t in CK.DISHES and CK.DISHES[i.t][1] == layer, 3)


def have(game, test, n):
    return sum(i.n if i.stackable else 1 for i in game.player.inv if test(i)) >= n


def take(game, test, n):
    for it in [i for i in game.player.inv if test(i)]:
        while n > 0 and it in game.player.inv:
            game.remove_one(it) if it.stackable else game.player.inv.remove(it)
            n -= 1


# ------------------------------------------------------------------ the tests at 25 and 40
def passed(game, key, lvl):
    return (key, lvl) in game.player.__dict__.setdefault('life_tests', set())


def held(game, key, lvl):
    """LS.gain: may the skill go past this rank yet?"""
    if lvl not in (25, 40) or passed(game, key, lvl):
        return False
    need_test(game, key, lvl)
    return True


def need_test(game, key, lvl):
    """The skill stops: a master somewhere sets a test (a job in your journal)."""
    from . import missions as MS
    from . import jobs as JB
    if any(m.kind == 'mastertest' and m.data.get('key') == key and m.data.get('lvl') == lvl
           for m in game.missions if m.state in ('active', 'turnin')):
        return
    w = game.world
    ss = [s for s in w.settlements if s.kind in ('town', 'city', 'village') and s.id != 0]
    if not ss:
        return
    rnd = random.Random(game.seed * 71 + LS.LIFE_ORDER.index(key) * 13 + lvl)
    ox, oy = game.world_pos()
    far = [s for s in ss if 25 <= cheb(s.x, s.y, ox, oy) <= 120] or ss
    s = rnd.choice(far)
    from .towns import town_names
    who = rnd.choice(town_names(getattr(s, 'race', 'human')))
    what, _test, _n = wants(key, lvl)
    trade = TRADE[key]
    m = JB.mission(game, s, 'mastertest', f"A master's test: {LS.LIFE[key]['name']} {lvl}",
                   f'{who}, a master {trade} of {s.name}, will see your work before your {LS.LIFE[key]["name"]} goes on. '
                   f'Bring {what}.', 10 + lvl // 2, (3, 6), None, key=key, lvl=lvl, who=who)
    m.state = 'active'
    game.missions.append(m)
    game.reveal_place(s.x, s.y)
    game.msg(f'Your {LS.LIFE[key]["name"]} will not go further without a master\'s word. {who}, a master {trade} in '
             f'{s.name}, sets you a test: bring {what}. It is in your journal.', 'gold')


def hand_in(game, m, sid):
    """In a town: a master's test or an order handed in. True if the job was this town's."""
    from . import missions as MS
    if m.giver != sid or m.state != 'active':
        return m.giver == sid
    d = m.data
    if m.kind == 'mastertest':
        what, test, n = wants(d['key'], d['lvl'])
        if not have(game, test, n):
            game.msg(f"{d['who']} still waits for {what}.", 'info')
            return True
        take(game, test, n)
        game.player.life_tests.add((d['key'], d['lvl']))
        game.msg(f"{d['who']} turns your work over a long time, and nods. \"Go on, then.\" Your "
                 f"{LS.LIFE[d['key']]['name']} can rise again.", 'unique')
        MS.complete(game, m, [sid])
        LS.gain(game, d['key'], 0.01)
        return True
    what, test, n = order_wants(game, d)
    if not have(game, test, n):
        game.msg(f"{d['who']} still waits for {what}.", 'info')
        return True
    take(game, test, n)
    r = LS.rank(game, d['key'])
    LS.gain(game, d['key'], 6 + r / 5, at=d['at'])
    MS.complete(game, m, [sid])
    return True


def line(game, m):
    d = m.data
    if m.kind == 'mastertest':
        what, test, n = wants(d['key'], d['lvl'])
    else:
        what, test, n = order_wants(game, d)
    got = sum(i.n if i.stackable else 1 for i in game.player.inv if test(i))
    return f'Bring {what} (you carry {min(got, n)} of {n}).'


# ------------------------------------------------------------------ orders on the boards
ORDERS = ('smithing', 'leatherworking', 'tailoring', 'brewing', 'alchemy', 'cooking')
ORDER_WHO = {'smithing': 'The farrier', 'leatherworking': 'The saddler', 'tailoring': 'The draper', 'brewing': 'The innkeeper',
             'alchemy': 'The healer', 'cooking': 'The reeve'}


def tier_for(r):
    return 'E' if r >= 40 else 'D' if r >= 30 else 'C' if r >= 20 else 'B' if r >= 10 else 'A'


def order_wants(game, d):
    key, t = d['key'], d['tier']
    if key in ('smithing', 'leatherworking', 'tailoring'):
        return (f'{d["n"]} pieces of your own {LS.LIFE[key]["name"].lower()} of tier {t} stuff or better',
                lambda i: i.k == 'gear' and getattr(i, 'made', (None,))[0] == key and at_least(_tier_of(i), t), d['n'])
    if key == 'brewing':
        return (f'{d["n"]} drinks of your own brewing', lambda i: i.k == 'food' and getattr(i, 'origin', None) is not None, d['n'])
    if key == 'alchemy':
        q = d['q']
        return (f'a brew of strength {q} or more', lambda i: i.k == 'draught' and getattr(i, 'q', 0) >= q, 1)
    from . import cooking as CK
    layer = d['layer']
    return (f'{d["n"]} {layer} dishes', lambda i: i.k == 'dish' and i.t in CK.DISHES and CK.DISHES[i.t][1] == layer, d['n'])


def make_order(game, s):
    """An order at your own height, from a board, for your best craft (from rank 5)."""
    from . import jobs as JB
    best = max(ORDERS, key=lambda k: LS.rank(game, k))
    r = LS.rank(game, best)
    if r < 5:
        return None
    t = tier_for(r)
    n = random.randint(1, 2) if best in ('smithing', 'leatherworking', 'tailoring') else random.randint(2, 4)
    who = random.choice(JB.NAMES)
    data = dict(key=best, tier=t, n=n, at=r, who=f'{who}', q=3 + r // 6, layer='simple' if r < 15 else 'hearty' if r < 35 else 'luxury')
    what, _test, _n = order_wants(game, data)
    return JB.mission(game, s, 'order', f'An order for {LS.LIFE[best]["name"].lower()}',
                      f'{ORDER_WHO[best]}, {who}, has an order and nobody here to fill it: {what}.',
                      8 + r * .8 + n * 3, (3, 6), game.day + 20, **data)


# ------------------------------------------------------------------ the great masters
def ensure(game):
    """Place the three great masters far from the roads, each with the workshop they lost, once per world."""
    w = game.world
    if getattr(w, 'masters', None) is not None:
        return w.masters
    from .sites import Site, site_at
    om = game.maps['over']
    rnd = random.Random(game.seed * 9311 + 5)
    w.masters = {}
    names = ['Old Hagan', 'Mother Ysolt', 'Brannoc Ironhand', 'Tamsin Greyneedle', 'Corwin Hidewright', 'Edda Silverthread',
             'Ulfric Coalbeard', 'Wenna Tanglehand']
    rnd.shuffle(names)

    def free(x, y):
        return om.inb(x, y) and D.TILES[om.tile(x, y)].walk and om.tile(x, y) not in (D.ROAD, D.TOWN, D.CITY, D.ENTR) \
            and not site_at(w, x, y) and not any(cheb(x, y, s.x, s.y) < 8 for s in w.settlements)
    taken = []
    for craft, (who, shop) in GREAT.items():
        spot = None
        for gap in (6, 4, 2):
            for _ in range(3000):
                x, y = rnd.randint(4, om.w - 5), rnd.randint(4, om.h - 5)
                if free(x, y) and w.road_dist[y * om.w + x] >= gap and all(cheb(x, y, a, b) >= 60 for a, b in taken):
                    spot = (x, y)
                    break
            if spot:
                break
        if not spot:
            continue
        taken.append(spot)
        name = names.pop()
        st = Site(len(w.sites), 'master', spot[0], spot[1], f"{name}'s {'Forge' if craft == 'smithing' else 'Workshop'}")
        st.faction = w.region_at(*spot).faction
        st.craft, st.master = craft, name
        st.hidden, st.found = True, False
        w.sites.append(st)
        lost = None
        for _ in range(500):
            x, y = spot[0] + rnd.randint(-22, 22), spot[1] + rnd.randint(-14, 14)
            if free(x, y) and cheb(x, y, *spot) >= 8:
                lost = Site(len(w.sites), 'lostshop', x, y, f"{name}'s Old {shop.title()}")
                lost.faction = w.region_at(x, y).faction
                lost.craft, lost.master = craft, name
                lost.hidden, lost.found = True, False
                w.sites.append(lost)
                break
        w.masters[craft] = dict(site=st.id, lost=lost.id if lost else None, name=name)
    return w.masters


def stage(game, craft):
    return game.player.__dict__.setdefault('masters', {}).get(craft, 0)


def rumour(game, who='The innkeeper'):
    """At an inn, or from a tanner: word of a great master. One in four talks, until you have heard of all three."""
    from . import folk as FK
    from .engine import dir_name
    from . import jobs as JB
    ms = ensure(game)
    p = game.player
    heard = p.__dict__.setdefault('masters_heard', set())
    left = [c for c in ms if c not in heard]
    if not left or random.random() > .25:
        return False
    craft = random.choice(left)
    heard.add(craft)
    st = game.world.sites[ms[craft]['site']]
    ox, oy = game.world_pos()
    FK.discover(game, st, None)
    game.msg(f'{who} leans closer. "They say the best {GREAT[craft][0]} alive is {st.master}, who lives alone '
             f'{JB._region(game, st.x, st.y)}, to the {dir_name(st.x - ox, st.y - oy)}, far from any road. Takes no '
             f'apprentices. Does not like visitors." It is on your map now.', 'gold')
    return True


def site_map(game, site):
    from .entities import GameMap, make_npc, make_monster
    state = random.getstate()
    random.seed(game.seed * 2741 + site.x * 977 + site.y * 37 + 5)
    try:
        w, h = 48, 28
        m = GameMap(site.map_key, 'town', site.name, w, h, D.GRASS)
        m.glows, m.lights, m.signs = [], [], []
        m.radius, m.sid, m.hid = 60, None, None
        m.site = site.id
        m.level = game.world.danger_at(site.x, site.y) + 3
        cy = h // 2
        for i in range(len(m.t)):
            if random.random() < .12:
                m.t[i] = D.TREE
        hx, hy = 20, cy - 4
        for y in range(hy - 1, hy + 10):
            for x in range(hx - 1, hx + 12):
                m.set(x, y, D.GRASS)
        lost = site.kind == 'lostshop'
        for y in range(hy, hy + 9):
            for x in range(hx, hx + 11):
                edge = y in (hy, hy + 8) or x in (hx, hx + 10)
                if lost:
                    m.set(x, y, (D.WALL if random.random() < .65 else D.RUBBLE) if edge else
                          (D.RUBBLE if random.random() < .15 else D.FLOOR))
                else:
                    m.set(x, y, D.WALL if edge else D.FLOOR)
        m.set(hx, cy, D.DOOR if not lost else D.FLOOR)
        tool = D.ANVIL if site.craft == 'smithing' else D.BENCH
        m.set(hx + 7, cy - 2, tool)
        m.set(hx + 8, hy + 6, D.FIREPIT if not lost else D.RUBBLE)
        if not lost:
            m.set(hx + 9, hy + 1, D.BED)
            m.glows.append((hx + 8, hy + 6, (255, 140, 50), 4))
        from .nature import path
        path(m, (0, cy), (hx - 1, cy), D.PATH, (D.GRASS, D.TREE))
        m.entry = (0, cy)
        for i in range(len(m.seen)):
            m.seen[i] = 1
        m.lights = list(m.glows)
        if lost:
            m.lostshop = site.craft
            danger = game.world.danger_at(site.x, site.y)
            pool = [k for k in ('bandit', 'brigand', 'orc', 'goblin', 'gnoll_hunter', 'wolf', 'troll', 'ogre', 'ghoul')
                    if k in D.MONSTERS and D.MONSTERS[k]['min_l'] <= danger + 3]
            kind = random.choice(pool or ['bandit'])
            for _ in range(random.randint(4, 6)):
                for _t in range(60):
                    x, y = random.randint(hx + 1, hx + 9), random.randint(hy + 1, hy + 7)
                    if D.TILES[m.tile(x, y)].walk and not m.mon_at(x, y):
                        o = make_monster(game, kind if random.random() < .7 else random.choice(pool or [kind]), x, y,
                                         danger + 3)
                        m.mons.append(o)
                        break
        else:
            o = make_npc(game, site.master, 'master', '#e8c478', hx + 5, cy, True)
            o.site = site.id
            m.mons.append(o)
    finally:
        random.setstate(state)
    return m


def on_enter(game, site, m):
    if site.kind == 'master':
        site.visits = getattr(site, 'visits', 0) + 1
    elif site.kind == 'lostshop' and getattr(m, 'lostshop', None) and stage(game, site.craft) == 3:
        if not any(not o.is_npc for o in m.mons):
            won_back(game, site)
        else:
            game.msg(f'{site.master}\'s old {GREAT[site.craft][1]}. Whatever lives here now does not want you in it.', 'bad')


def after_kill(game):
    """The last of them falls in a master's old workshop: it is won back."""
    m = game.map
    if not getattr(m, 'lostshop', None) or any(not o.is_npc for o in m.mons):
        return
    site = game.world.sites[m.site]
    if stage(game, site.craft) == 3:
        won_back(game, site)


def won_back(game, site):
    game.player.masters[site.craft] = 4
    game.msg(f'The {GREAT[site.craft][1]} is quiet. {site.master} will want to hear it is theirs again.', 'gold')


def talk(game, npc):
    """A great master: the three parts of the test, then Unmake for gold."""
    from . import events as EV
    from .money import fmt
    from . import folk as FK
    w = game.world
    site = w.sites[npc.site]
    craft = site.craft
    p = game.player
    ms = p.__dict__.setdefault('masters', {})
    st = ms.get(craft, 0)
    who, shop = GREAT[craft]
    if st == 0:
        ms[craft] = st = 1
        game.say(npc, f'"So you found me. Everyone wants something of a {who}. Prove you are worth my time: bring me '
                      f'{TOP_TEXT[craft]}."')
        return
    if st == 1:
        test = TOP[craft]
        if have(game, test, 1):
            take(game, test, 1)
            ms[craft] = 2
            game.say(npc, '"Hm. Real, and not stolen from a market stall. Now bring me a part off a beast with a name: a '
                          'notorious one, or a legend."')
        else:
            game.say(npc, f'"{TOP_TEXT[craft].capitalize()}. Not before."')
        return
    if st == 2:
        test = lambda i: i.k == 'npart' and getattr(i, 'rank', '') in ('notorious', 'legendary')  # noqa: E731
        if have(game, test, 1):
            take(game, test, 1)
            ms[craft] = 3
            lost = w.sites[w.masters[craft]['lost']] if w.masters[craft].get('lost') is not None else None
            if lost:
                FK.discover(game, lost, None)
            game.say(npc, f'"Good. One thing more. My old {shop} lies a day from here. Something moved in when I was '
                          f'away, and I am too old to throw it out. Win it back."')
            if lost is None:
                ms[craft] = 4
        else:
            game.say(npc, '"A part off a notorious beast, or a legend. Nothing less."')
        return
    if st == 3:
        game.say(npc, f'"My {shop} is still not mine. Go on."')
        return
    used = p.__dict__.setdefault('master_used', {})
    if used.get(craft) == getattr(site, 'visits', 0):
        game.say(npc, '"One a visit. My hands are not what they were. Come back another time."')
        return
    from . import crafts as CRF
    if not CRF.unmake_pairs(game, craft, True):
        game.say(npc, f'"Bring me a found piece with a power worth moving, and a plain piece of {who}\'s work to take it. '
                      f'I ask {fmt(PRICE)}, and I promise nothing: half the time it fails."')
        return
    used[craft] = getattr(site, 'visits', 0)
    CRF.unmake_menu(game, craft, master=PRICE)


TOP = {'smithing': lambda i: i.k == 'star' or (i.k == 'mat' and i.t in ('bar_star', 'ore_star')),
       'leatherworking': lambda i: (i.k == 'leather' and i.t == 'drake') or i.k == 'npart',
       'tailoring': lambda i: i.k == 'mat' and i.t == 'cloth_feysilk'}
TOP_TEXT = {'smithing': 'star-iron', 'leatherworking': 'drake hide, or a part off a named beast',
            'tailoring': 'a bolt of Fey Silk'}


def register():
    from . import jobs as JB
    JB.LABEL.update(mastertest="A master's test", order='An order')
    JB.KINDS.update(('mastertest', 'order'))
    JB.MAKE['order'] = make_order
    for lst in (JB.VILLAGE, JB.TOWN, JB.CITY):
        if 'order' not in lst:
            lst.append('order')


register()
