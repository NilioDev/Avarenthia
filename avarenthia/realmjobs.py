"""Work for the lords and the other powers, and against them: the player is a piece in their game.

Every job here is one mission kind, 'realm', with a task: where to go, what you find there and the choice you make,
each played on the spot with one key. Jobs for these powers pay modestly; betrayal pays more and makes enemies.
The lords give most of the small work (a letter, a claimant to back, an heir to save or to kill, a gate to open, a
wedding to guard...); village boards ask for help against the raiders; the raiders' chiefs, the prior of the holy
order, the witches, the Watch, the rebels, the pretender and the dwarves' keeper of the grudge book have their own.
How a choice weighs is in jobs.effects; what it changes in the world is in the task's own code."""
import random

from . import data as D
from .worldgen import cheb

TASKS = {}


def task(key, giver, title):
    def deco(fn):
        TASKS[key] = dict(giver=giver, title=title, make=fn)
        return fn
    return deco


# ------------------------------------------------------------------ helpers
def R(game):
    return game.world.realm


def PWS(game):
    return game.world.powers


def spot(game, x, y, lo, hi):
    from .named import _spot as sp
    return sp(game, x, y, lo, hi)


def dirto(src, x, y):
    from .engine import dir_name
    return dir_name(x - src[0], y - src[1])


def stat_chance(game, key, base=.35):
    from .jobs import stat
    return max(.15, min(.9, base + (stat(game, key) - 10) * .04))


def lvl_at(game, x, y, plus=2):
    return max(3, game.world.danger_at(x, y) + plus)


def giver_pos(game, g):
    w = game.world
    k = g['kind']
    if k == 'lord':
        from . import realms as RL
        lo = R(game).lord(g['lid'])
        return RL.place_of(game, lo)
    if k == 'town':
        s = w.settlements[g['sid']]
        return s.x, s.y
    if 'site' in g:
        st = w.sites[g['site']]
        return st.x, st.y
    if 'sid' in g:
        s = w.settlements[g['sid']]
        return s.x, s.y
    return 0, 0


def mission(game, g, key, title, desc, reward_s, deadline_days=20, faction=None, **data):
    from . import missions as MS
    m = MS.Mission(game.new_id(), 'realm', g.get('sid') if g['kind'] == 'town' else None)
    m.title, m.desc = title, desc
    m.reward = round(reward_s) * 100
    m.rep = random.randint(4, 8)
    m.deadline = game.day + deadline_days
    m.faction = faction
    data.update(task=key, giver=g, giver_name=g['name'])
    m.data = data
    return m


def turnin(game, m, text):
    from .jobs import _turnin
    _turnin(game, m, text)


def fight(game, m, keys, lvl, elite=0, intro=None):
    from .jobs import fight as jf
    return jf(game, m, keys, lvl, elite, intro, 'realm')


def fx(game, **kw):
    from .jobs import effects
    return effects(game, **kw)


def favour(game, kid, n):
    from . import realms as RL
    RL.add_favour(game, kid, n)


def giver_kid(game, m):
    from . import realms as RL
    g = m.data['giver']
    if g['kind'] == 'lord':
        lo = R(game).lord(g['lid'])
        kg = RL.kingdom_of_lord(R(game), lo) if lo else None
        return kg.id if kg else None
    return g.get('kid')


def villages_near(game, x, y, r, pred=lambda s: True):
    return [s for s in game.world.settlements if s.kind in ('hamlet', 'village', 'town') and s.id != 0
            and cheb(s.x, s.y, x, y) <= r and pred(s)]


def raider_of(game, kind):
    for i, rd in enumerate(PWS(game)['raiders']):
        if rd['kind'] == kind:
            return i, rd
    return None, None


def kingdom_of(game, lo):
    from . import realms as RL
    return RL.kingdom_of_lord(R(game), lo)


# ------------------------------------------------------------------ the lords' work
@task('letter', 'lord', 'Carry a letter')
def make_letter(game, g):
    from . import realms as RL
    Rl = R(game)
    lo = Rl.lord(g['lid'])
    kg = kingdom_of(game, lo)
    cands = [o for o in Rl.lords.values() if o.alive and o.id != lo.id and o.title in ('baron', 'lord', 'king', 'emperor')
             and Rl.houses[o.house].seat and 12 <= cheb(*RL.place_of(game, o), *RL.place_of(game, lo)) <= 90]
    if not cands:
        return None
    to = random.choice(cands)
    x, y = RL.place_of(game, to)
    where = RL.seat_name(game.world, Rl.houses[to.house].seat)
    pay = 12 + cheb(x, y, *RL.place_of(game, lo)) // 5
    return mission(game, g, 'letter', f'A letter for {to.first} {Rl.houses[to.house].name}',
                   f'{RL.style(Rl, lo, False)} gives you a letter under seal for {RL.style(Rl, to, False)}, at {where} to the '
                   f'{dirto(RL.place_of(game, lo), x, y)}. Put it in no other hand.', pay, 25, 'crown', spot=[x, y], reach=1,
                   where=where, to=to.id, kid=kg.id if kg else None)


def arrive_letter(game, m):
    Rl = R(game)
    to = Rl.lord(m.data['to'])
    return (f'The guards at the gate send for {to.first if to else "the lord"}\'s steward, who holds out a hand for the '
            f'letter. The seal is plain wax; it would lift with a warm knife.',
            [('Hand the letter over', 'give'), ('Lift the seal and read it first', 'read')])


def do_letter(game, m, choice):
    from . import missions as MS
    from . import chronicle as CH
    from . import realms as RL
    Rl = R(game)
    lo = Rl.lord(m.data['giver']['lid'])
    if choice == 'read':
        secret = random.choice([f'{lo.first} asks for men against a neighbour, and promises land for them.',
                                f'{lo.first} offers a daughter\'s hand, and a mill, for an old debt forgiven.',
                                f'{lo.first} writes of a plot at court, and names no names.'])
        CH.add(game, 'Lords and houses', f'A letter of {RL.style(Rl, lo, False)}: {secret}', 'read', who='a letter you opened',
               key=f'letter:{m.id}', quiet=True)
        game.msg(f'You read the letter. {secret}', 'info')
        if random.random() < .3:
            game.msg('The steward looks at the seal a long moment. "This has been opened." Word will go back.', 'bad')
            favour(game, m.data.get('kid'), -6)
            MS.fail(game, m, 'The seal was broken.')
            return
    game.msg('The steward takes the letter with a bow.', 'good')
    favour(game, m.data.get('kid'), 3)
    MS.complete(game, m, [])


@task('claimant', 'lord', 'Back a claimant')
def make_claimant(game, g):
    from . import realms as RL
    Rl = R(game)
    lo = Rl.lord(g['lid'])
    kg = kingdom_of(game, lo)
    if not kg or not kg.civil:
        return None
    claimant = Rl.lord(kg.civil['claimant'])
    king = Rl.lord(kg.king)
    side = 'claimant' if lo.id == claimant.id or lo.liege == claimant.id else 'king'
    foe = king if side == 'claimant' else claimant
    fx_, fy = RL.place_of(game, foe)
    sp = spot(game, fx_, fy, 6, 16)
    if not sp:
        return None
    return mission(game, g, 'claimant', f'Fight for {(claimant if side == "claimant" else king).first}',
                   f'The war of the {kg.short} crown: {RL.style(Rl, lo, False)} asks you to ride with {lo.his} men against '
                   f'those of {RL.style(Rl, foe, False)}, who hold the field to the {dirto(RL.place_of(game, lo), *sp)}.',
                   30 + lvl_at(game, *sp) * 3, 20, 'crown', spot=list(sp), reach=1, where='the field', side=side, kid=kg.id)


def arrive_claimant(game, m):
    return ('Banners on the ridge, and men drawn up across the road. A horn sounds.',
            [('Charge with the others', 'fight'), ('Hang back and let them fight', 'leave')])


def do_claimant(game, m, choice):
    if choice == 'fight':
        x, y = m.data['spot']
        fight(game, m, ['soldier', 'soldier', 'crossbow', 'knight'], lvl_at(game, x, y, 3), 0, 'The enemy line comes on at a run.')
        return
    m.data['cool'] = game.turn + 60


def won_claimant(game, m):
    kg = R(game).kingdoms[m.data['kid']]
    if kg.civil:
        kg.civil['score'] += 1 if m.data['side'] == 'claimant' else -1
    favour(game, kg.id, 5)
    turnin(game, m, 'The field is yours. They will sing of this charge in some hall or other.')


@task('save_heir', 'lord', 'Save an heir')
def make_save_heir(game, g):
    from . import realms as RL
    Rl = R(game)
    lo = Rl.lord(g['lid'])
    kg = kingdom_of(game, lo)
    heirs = [o for o in Rl.lords.values() if o.alive and o.title == 'heir' and Rl.houses[o.house].seat
             and not Rl.houses[o.house].fallen and cheb(*RL.place_of(game, o), *RL.place_of(game, lo)) <= 60]
    if not heirs:
        return None
    h = random.choice(heirs)
    hx, hy = RL.place_of(game, h)
    sp = spot(game, hx, hy, 6, 16)
    if not sp:
        return None
    house = Rl.houses[h.house]
    return mission(game, g, 'save_heir', f'Bring {h.first} {house.name} home',
                   f'Outlaws took {h.first}, heir of House {house.name}, on the road, and ask a ransom no house can pay. '
                   f'They hold {h.him} in a camp to the {dirto(RL.place_of(game, lo), *sp)}. Bring {h.him} home alive.',
                   35 + lvl_at(game, *sp) * 3, 18, 'crown', spot=list(sp), reach=1, where='the outlaws\' camp', heir=h.id,
                   kid=kg.id if kg else None)


def arrive_save_heir(game, m):
    h = R(game).lord(m.data['heir'])
    return (f'A fire in a hollow, horses tied to the trees. {h.first if h else "The heir"} sits bound by the fire, '
            f'and the outlaws are counting their coin already.', [('Fall on them', 'fight'), ('Not now', 'leave')])


def do_save_heir(game, m, choice):
    if choice == 'fight':
        x, y = m.data['spot']
        fight(game, m, ['bandit', 'bandit', 'brigand', 'robber_knight'], lvl_at(game, x, y, 2), 1)
        return
    m.data['cool'] = game.turn + 60


def won_save_heir(game, m):
    h = R(game).lord(m.data['heir'])
    favour(game, m.data.get('kid'), 6)
    turnin(game, m, f'You cut {h.first if h else "the heir"} loose. The way home is short.')


@task('kill_heir', 'lord', 'An heir in the way')
def make_kill_heir(game, g):
    from . import realms as RL
    Rl = R(game)
    lo = Rl.lord(g['lid'])
    if not ({'ambitious', 'greedy'} & set(lo.traits)):
        return None
    h0 = Rl.houses[lo.house]
    foes = [Rl.houses[f] for f in h0.feuds if not Rl.houses[f].fallen]
    heirs = [Rl.lord(Rl.lord(f.head).heir) for f in foes if f.head is not None and Rl.lord(f.head) and Rl.lord(f.head).heir]
    heirs = [h for h in heirs if h and h.alive]
    if not heirs:
        return None
    h = random.choice(heirs)
    hx, hy = RL.place_of(game, h)
    sp = spot(game, hx, hy, 4, 10)
    if not sp:
        return None
    house = Rl.houses[h.house]
    return mission(game, g, 'kill_heir', f'The heir of House {house.name}',
                   f'"House {house.name} has wronged mine for the last time." {RL.style(Rl, lo, False)} wants {h.first}, '
                   f'the heir of House {house.name}, dead, and no one the wiser. {h.he.capitalize()} hunts in the woods to the '
                   f'{dirto(RL.place_of(game, lo), *sp)}. It pays well.', 70, 16, None, spot=list(sp), reach=1,
                   where='the hunting woods', heir=h.id, dark='murder')


def arrive_kill_heir(game, m):
    h = R(game).lord(m.data['heir'])
    return (f'{h.first if h else "The heir"} rides alone ahead of the huntsmen, laughing, young. {h.he.capitalize() if h else "He"} '
            f'has not seen you.', [('Do it', 'kill'), ('Warn the heir instead', 'warn'), ('Not now', 'leave')])


def do_kill_heir(game, m, choice):
    from . import missions as MS
    from . import realms as RL
    Rl = R(game)
    h = Rl.lord(m.data['heir'])
    if choice == 'kill':
        x, y = m.data['spot']
        fight(game, m, ['knight', 'soldier'], lvl_at(game, x, y, 2), 0, 'The huntsmen come at you, horns blowing.')
        m.data['murder'] = True
        return
    if choice == 'warn':
        house = Rl.houses[h.house] if h else None
        game.msg(f'{h.first if h else "The heir"} listens, goes pale, and rides for home. House {house.name if house else ""} will '
                 f'remember who warned them.', 'good')
        kg = kingdom_of(game, Rl.lord(house.head)) if house and house.head else None
        favour(game, kg.id if kg else None, 5)
        MS.fail(game, m, 'You warned the heir.')
        return
    m.data['cool'] = game.turn + 60


def won_kill_heir(game, m):
    from . import realms as RL
    h = R(game).lord(m.data['heir'])
    if h and h.alive:
        RL.die(game, h, 'a hunting accident, they say')
    fx(game, crime=(12, 'the murder of a noble heir', .35), god=('valdric', -5))
    turnin(game, m, 'It is done. The huntsmen will find what is left.')


@task('gate', 'lord', 'Open a gate')
def make_gate(game, g):
    from . import realms as RL
    Rl = R(game)
    lo = Rl.lord(g['lid'])
    kg = kingdom_of(game, lo)
    if not kg or not kg.rebel or kg.rebel['baron'] == lo.id:
        return None
    rb = Rl.lord(kg.rebel['baron'])
    b = Rl.baronies[kg.rebel['rid']]
    x, y = RL.seat_pos(game.world, b.seat)
    return mission(game, g, 'gate', f'Open the gate of {RL.seat_name(game.world, b.seat)}',
                   f'{RL.style(Rl, rb, False)} holds {RL.seat_name(game.world, b.seat)} against the king. Get in by night and '
                   f'open the gate for the king\'s men.', 45, 16, 'crown', spot=[x, y], reach=2, where=RL.seat_name(game.world, b.seat),
                   kid=kg.id)


def arrive_gate(game, m):
    return ('The walls are dark; torches walk along the top. Somewhere a dog barks. The king\'s men wait in the trees for your signal.',
            [('Climb the wall where the torches are far apart', 'climb'), ('Walk up to the gate as a messenger', 'bluff'),
             ('Not now', 'leave')])


def do_gate(game, m, choice):
    if choice == 'leave':
        m.data['cool'] = game.turn + 60
        return
    ok = random.random() < stat_chance(game, 'dex' if choice == 'climb' else 'ene')
    x, y = m.data['spot']
    if ok:
        won_gate(game, m)
        return
    fight(game, m, ['soldier', 'crossbow', 'soldier'], lvl_at(game, x, y, 3), 0, '"Who goes there?" The alarm bell rings.')


def won_gate(game, m):
    kg = R(game).kingdoms[m.data['kid']]
    if kg.rebel:
        kg.rebel['help'] = kg.rebel.get('help', 0) - 2
    favour(game, kg.id, 6)
    turnin(game, m, 'The bar comes off, the gate swings open, and the king\'s men pour in.')


@task('wedding', 'lord', 'Guard a wedding')
def make_wedding(game, g):
    from . import realms as RL
    Rl = R(game)
    lo = Rl.lord(g['lid'])
    note = next((n for n in PWS(game)['notes'] if n['kind'] == 'wedding' and lo.house in n['houses'] and n['day'] > game.day), None)
    if not note:
        return None
    x, y = RL.place_of(game, lo)
    other = Rl.houses[[h for h in note['houses'] if h != lo.house][0]]
    return mission(game, g, 'wedding', f'Guard the wedding of House {Rl.houses[lo.house].name}',
                   f'House {Rl.houses[lo.house].name} weds House {other.name}. There are those who would rather it did not '
                   f'happen. Stand guard at the feast.', 30, max(4, note['day'] - game.day + 2), 'crown', spot=[x, y], reach=1,
                   where='the wedding feast', kid=(kingdom_of(game, lo).id if kingdom_of(game, lo) else None))


def arrive_wedding(game, m):
    return ('Garlands on the gate, a roast on the spit, a fiddler tuning up. Among the guests, a serving man you did not see '
            'come in carries a cup to the high table.', [('Stop the serving man', 'stop'), ('Watch the gate instead', 'gate')])


def do_wedding(game, m, choice):
    x, y = m.data['spot']
    if choice == 'stop' and random.random() < stat_chance(game, 'dex', .5):
        game.msg('You catch his wrist. The cup spills, and the dogs that lap it up do not get up again.', 'good')
        won_wedding(game, m)
        return
    fight(game, m, ['bandit', 'brigand', 'bandit'], lvl_at(game, x, y, 2), 0,
          'Knives come out among the guests: hired blades, and they came for the bride.')


def won_wedding(game, m):
    favour(game, m.data.get('kid'), 5)
    turnin(game, m, 'The wedding goes on, louder for the fright.')


@task('hostage', 'lord', 'Bring back a hostage')
def make_hostage(game, g):
    from . import realms as RL
    idx, rd = raider_of(game, 'barbarian')
    if rd is None:
        return None
    Rl = R(game)
    lo = Rl.lord(g['lid'])
    sp = spot(game, rd['x'], rd['y'], 3, 8)
    if not sp:
        return None
    return mission(game, g, 'hostage', f'A hostage among the {rd["people"]}',
                   f'The {rd["people"]} of {rd["land"]} hold a cousin of House {Rl.houses[lo.house].name}, taken in a raid, '
                   f'to the {dirto(RL.place_of(game, lo), *sp)}. Bring {random.choice(["him", "her"])} home: by silver, by '
                   f'stealth or by steel.', 40, 25, 'crown', spot=list(sp), reach=2, where=rd['land'], raider=idx,
                   kid=(kingdom_of(game, lo).id if kingdom_of(game, lo) else None))


def arrive_hostage(game, m):
    p = game.player
    opts = []
    if p.gold >= 2000:
        opts.append(('Pay the ransom from your own purse (20s)', 'pay'))
    opts += [('Steal the hostage away by night', 'steal'), ('Challenge their champion for the hostage', 'duel'), ('Not now', 'leave')]
    return ('The clan keeps the hostage in a hut by the cattle pen, a rope on one ankle. The warriors are drinking.', opts)


def do_hostage(game, m, choice):
    x, y = m.data['spot']
    if choice == 'pay':
        game.player.gold -= 2000
        turnin(game, m, 'The chieftain counts the silver twice and cuts the rope himself.')
        return
    if choice == 'steal':
        if random.random() < stat_chance(game, 'dex'):
            turnin(game, m, 'You are a league away before the dogs start barking.')
            return
        fight(game, m, ['clan_warrior', 'clan_warrior', 'clan_rider'], lvl_at(game, x, y, 2), 0, 'The dogs. The whole clan wakes.')
        return
    if choice == 'duel':
        fight(game, m, ['clan_warrior'], lvl_at(game, x, y, 4), 2, 'The champion steps into the ring, grinning.')
        return
    m.data['cool'] = game.turn + 60


@task('hire', 'lord', 'Hire the clans')
def make_hire(game, g):
    from . import realms as RL
    idx, rd = raider_of(game, 'barbarian')
    Rl = R(game)
    lo = Rl.lord(g['lid'])
    if rd is None or lo.title not in ('baron', 'king') or not ({'ambitious', 'craven'} & set(lo.traits)):
        return None
    return mission(game, g, 'hire', f'Hire the {rd["people"]} for {lo.first}',
                   f'{RL.style(Rl, lo, False)} wants two hundred spears of the {rd["people"]} for {lo.his} quarrels. Go to '
                   f'{rd["land"]} and strike the bargain with {PW_chief(rd)}.', 35, 25, 'crown', spot=[rd['x'], rd['y']], reach=2,
                   where=rd['land'], raider=idx, kid=(kingdom_of(game, lo).id if kingdom_of(game, lo) else None))


def PW_chief(rd):
    from . import powers as PW
    return PW.chief_style(rd)


def arrive_hire(game, m):
    rd = PWS(game)['raiders'][m.data['raider']]
    opts = [('Offer the baron\'s silver', 'offer')]
    if game.player.gold >= 1000:
        opts.append(('Sweeten it from your own purse (10s)', 'sweet'))
    opts.append(('Not now', 'leave'))
    return (f'{PW_chief(rd)} hears you out over a horn of ale. "Two hundred spears. And what does your baron give, that a '
            f'winter raid would not?"', opts)


def do_hire(game, m, choice):
    if choice == 'leave':
        m.data['cool'] = game.turn + 60
        return
    rd = PWS(game)['raiders'][m.data['raider']]
    if choice == 'sweet':
        game.player.gold -= 1000
    if choice == 'sweet' or random.random() < stat_chance(game, 'ene', .45):
        rd['friend'] = True
        turnin(game, m, 'The chieftain spits in a palm and holds it out. The spears will come, and they will be paid.')
    else:
        from . import missions as MS
        MS.fail(game, m, '"Not for that." The chieftain turns away.')


@task('envoy', 'lord', 'An envoy to the mist folk')
def make_envoy(game, g):
    from . import realms as RL
    idx, rd = raider_of(game, 'mist')
    if rd is None:
        return None
    Rl = R(game)
    lo = Rl.lord(g['lid'])
    return mission(game, g, 'envoy', 'Take an envoy through the marshes',
                   f'{RL.style(Rl, lo, False)} sends an envoy to the {rd["people"]} of {rd["land"]}, to talk of peace on the '
                   f'marsh roads. Nobody knows the way. Take {random.choice(["him", "her"])} there.', 35, 25, 'crown',
                   spot=[rd['x'], rd['y']], reach=3, where=rd['land'], raider=idx,
                   kid=(kingdom_of(game, lo).id if kingdom_of(game, lo) else None))


def arrive_envoy(game, m):
    return ('The mist comes up off the water, white and thick. The envoy grips your sleeve. Shapes move at the edge of sight.',
            [('Stand still and call out a greeting', 'call'), ('Draw steel and press on', 'press')])


def do_envoy(game, m, choice):
    rd = PWS(game)['raiders'][m.data['raider']]
    x, y = m.data['spot']
    if choice == 'call' and random.random() < .7:
        rd['friend'] = True
        turnin(game, m, 'Grey figures come out of the mist and lead you in. The envoy will talk for days.')
        return
    fight(game, m, ['mist_stalker', 'mist_stalker'], lvl_at(game, x, y, 2), 0, 'Knives in the mist!')


@task('pay', 'lord', 'The company\'s pay')
def make_pay(game, g):
    from . import realms as RL
    Rl = R(game)
    lo = Rl.lord(g['lid'])
    kg = kingdom_of(game, lo)
    cs = [(i, c) for i, c in enumerate(PWS(game)['companies']) if not c['gone'] and kg and c['employer'] == kg.id]
    if not cs:
        return None
    i, c = random.choice(cs)
    return mission(game, g, 'pay', f'Pay {c["name"].replace("The ", "the ")}',
                   f'{c["name"]} has not been paid for a month and grumbles. Take {lo.his} chest of silver to their camp, '
                   f'and see it reaches Captain {c["captain"]}.', 25, 12, 'crown', spot=[c['x'], c['y']], reach=1,
                   where=f'the camp of {c["name"].replace("The ", "the ")}', company=i, kid=kg.id)


def arrive_pay(game, m):
    return ('The sellswords crowd round as you ride in. The chest is heavy on your saddle; nobody knows what is in it but you.',
            [('Hand the chest to the captain', 'give'), ('Keep half; say it was all there was', 'skim')])


def do_pay(game, m, choice):
    c = PWS(game)['companies'][m.data['company']]
    if choice == 'skim':
        game.player.gold += 3000
        c['bribed'] = c.get('bribed', 0) + .3
        game.msg('You keep 30 silver. The captain counts the rest with a face like thunder.', 'gold')
        fx(game, crime=(6, 'theft of a lord\'s silver', .3))
    turnin(game, m, 'The company is paid, after a fashion.')


@task('bribe', 'lord', 'Buy a captain')
def make_bribe(game, g):
    from . import realms as RL
    Rl = R(game)
    lo = Rl.lord(g['lid'])
    kg = kingdom_of(game, lo)
    if not kg:
        return None
    foes = {w_['b'] if w_['a'] == kg.id else w_['a'] for w_ in Rl.wars if kg.id in (w_['a'], w_['b'])}
    cs = [(i, c) for i, c in enumerate(PWS(game)['companies']) if not c['gone'] and c['employer'] in foes]
    if not cs:
        return None
    i, c = random.choice(cs)
    return mission(game, g, 'bribe', f'Buy Captain {c["captain"]}',
                   f'{c["name"]} fights for the enemy. {RL.style(Rl, lo, False)} gives you a purse for Captain {c["captain"]}, '
                   f'and the promise of a bigger one, if the company changes sides.', 40, 14, 'crown', spot=[c['x'], c['y']],
                   reach=1, where=f'the camp of {c["name"].replace("The ", "the ")}', company=i, kid=kg.id)


def arrive_bribe(game, m):
    c = PWS(game)['companies'][m.data['company']]
    return (f'Captain {c["captain"]} weighs the purse in one hand. "Gold talks," {"she" if c["captain_g"] == "female" else "he"} says. '
            f'"Let us hear what it says."', [('Make the offer', 'offer'), ('Not now', 'leave')])


def do_bribe(game, m, choice):
    if choice == 'leave':
        m.data['cool'] = game.turn + 60
        return
    c = PWS(game)['companies'][m.data['company']]
    c['employer'] = m.data['kid']
    from . import realms as RL
    RL.news(game, f'{c["name"]} has gone over to {R(game).kingdoms[m.data["kid"]].short}: more gold, they say.', c['x'], c['y'])
    turnin(game, m, 'The captain pockets the purse. By morning the banners have changed.')


@task('catch_rebel', 'lord', 'Catch the rebel leader')
def make_catch(game, g):
    from . import realms as RL
    rv = PWS(game)['revolt']
    Rl = R(game)
    lo = Rl.lord(g['lid'])
    kg = kingdom_of(game, lo)
    if not rv or not kg or rv['kid'] != kg.id:
        return None
    st = game.world.sites[rv['site']]
    return mission(game, g, 'catch_rebel', f'Catch {rv["leader"]}',
                   f'{rv["leader"]} leads the rising from a camp near {game.world.settlements[rv["sid"]].name}. Bring '
                   f'{"her" if rv["leader_g"] == "female" else "him"} in, and the rest will go home.', 40, 20, 'crown',
                   spot=[st.x, st.y], reach=1, where=st.name, kid=kg.id)


def arrive_catch(game, m):
    rv = PWS(game)['revolt']
    who = rv['leader'] if rv else 'the leader'
    return (f'Thin smoke, thin faces. Peasants with scythes and flails stand up as you come. {who} steps forward.',
            [('Take the leader', 'take'), ('Turn away; leave them be', 'free')])


def do_catch(game, m, choice):
    from . import missions as MS
    if choice == 'free':
        fx(game, god=('solmara', 2))
        MS.fail(game, m, 'You let the rising be.')
        return
    x, y = m.data['spot']
    fight(game, m, ['peasant', 'peasant', 'peasant', 'peasant'], lvl_at(game, x, y, 0), 0, 'They will not give up their leader.')


def won_catch(game, m):
    rv = PWS(game)['revolt']
    if rv:
        rv['help'] = rv.get('help', 0) - 3
    favour(game, m.data.get('kid'), 5)
    fx(game, god=('solmara', -2))
    turnin(game, m, 'The leader is taken, in chains. The rest scatter to their villages.')


@task('betray_pretender', 'lord', 'The pretender\'s hiding place')
def make_betray(game, g):
    from . import realms as RL
    pt = PWS(game)['pretender']
    Rl = R(game)
    lo = Rl.lord(g['lid'])
    kg = kingdom_of(game, lo)
    if not pt or not kg or pt['kid'] != kg.id or pt['site'] is None:
        return None
    pl = Rl.lord(pt['lid'])
    st = game.world.sites[pt['site']]
    return mission(game, g, 'betray_pretender', f'Find {pl.first} {Rl.houses[pl.house].name}',
                   f'The exile {pl.first} {Rl.houses[pl.house].name} gathers men somewhere in the wilds. Find the camp '
                   f'and bring word, and the king will do the rest. It is said to lie to the '
                   f'{dirto(RL.place_of(game, lo), st.x, st.y)}.', 50, 30, 'crown', spot=[st.x, st.y], reach=1,
                   where='the hidden camp', kid=kg.id, nomark=True)


def arrive_betray(game, m):
    return ('Tents under the trees, a banner of an old house rolled on its pole. Nobody has seen you.',
            [('Mark the place and ride for the king', 'mark'), ('Walk in and warn them', 'warn')])


def do_betray(game, m, choice):
    from . import missions as MS
    from . import powers as PW
    pt = PWS(game)['pretender']
    if choice == 'warn':
        if pt:
            pt['followers'] += 2
        game.msg('The exile hears you out and thanks you. By nightfall the camp has moved.', 'info')
        MS.fail(game, m, 'You warned the exile.')
        return
    if pt and pt['site'] is not None:
        PW.mark_site(game, pt['site'], 'empty')
        pt['site'] = None
        pt['where'] = 'sea'
        pt['followers'] = 0
    from . import realms as RL
    RL.news(game, 'The king\'s riders burned the hidden camp of the exile. The pretender fled over the sea.', *m.data['spot'])
    favour(game, m.data.get('kid'), 6)
    turnin(game, m, 'You mark the camp and ride hard.')


@task('warlord', 'lord', 'A rising warlord')
def make_warlord(game, g):
    from . import realms as RL
    pw = PWS(game)
    gv = pw['gorvash']
    tr = max(pw['tribes'], key=lambda t: t['strength']) if pw['tribes'] else None
    if not tr or (not gv and tr['strength'] < 7):
        return None
    chief = gv['chief'] if gv else tr['chief']
    t = next((t for t in pw['tribes'] if t['chief'] == chief), tr)
    sp = spot(game, t['x'], t['y'], 2, 6)
    if not sp:
        return None
    Rl = R(game)
    lo = Rl.lord(g['lid'])
    return mission(game, g, 'warlord', f'Kill {chief}',
                   f'{chief} of {t["name"].replace("The ", "the ")} ' + ('leads the Gorvash.' if gv else 'grows strong enough to unite the tribes.') +
                   f' Kill the warlord, and the tribes fall to feuding again. {t["name"]} camp lies to the '
                   f'{dirto(RL.place_of(game, lo), *sp)}.', 60, 30, 'crown', spot=list(sp), reach=1, where=t['name'], chief=chief,
                   kid=(kingdom_of(game, lo).id if kingdom_of(game, lo) else None))


def arrive_warlord(game, m):
    return (f'{m.data["chief"]} sits by the fire with the war chiefs around, a cleaver across the knees.',
            [('Challenge the warlord to single combat', 'duel'), ('Attack the warlord and the guard', 'attack'), ('Not now', 'leave')])


def do_warlord(game, m, choice):
    x, y = m.data['spot']
    m.data['leader'] = m.data['chief']
    if choice == 'duel':
        fight(game, m, ['orc_chief'], lvl_at(game, x, y, 4), 2, f'The orcs make a ring. {m.data["chief"]} laughs and stands.')
    elif choice == 'attack':
        fight(game, m, ['orc_chief', 'orc', 'orc_berserker', 'orc'], lvl_at(game, x, y, 3), 1)
    else:
        m.data['cool'] = game.turn + 60


def won_warlord(game, m):
    from . import powers as PW
    pw = PWS(game)
    if pw['gorvash'] and pw['gorvash']['chief'] == m.data['chief']:
        PW.end_gorvash(game, 'was slain in single combat by a stranger')
    else:
        for t in pw['tribes']:
            if t['chief'] == m.data['chief']:
                t['strength'] = 2
                from .races import random_name
                t['chief'] = random_name('orc', t['chief_g'])
    favour(game, m.data.get('kid'), 8)
    from . import chronicle as CH
    CH.deed(game, f'The death of {m.data["chief"]}', f'You killed {m.data["chief"]}, the warlord of the tribes.')
    turnin(game, m, f'{m.data["chief"]} is dead. The tribes will be at each other\'s throats by spring.')


@task('woodroad', 'lord', 'A road through the wood')
def make_woodroad(game, g):
    from . import realms as RL
    w = game.world
    if not any(r.faction == 'circle' for r in w.regions):
        return None
    Rl = R(game)
    lo = Rl.lord(g['lid'])
    if 'greedy' not in lo.traits and 'ambitious' not in lo.traits:
        return None
    om = game.maps['over']
    from . import powers as PW
    cells = PW.edge_cells(om, w, {r.id for r in w.regions if r.faction == 'circle'})
    lx, ly = RL.place_of(game, lo)
    cells = [i for i in cells if cheb(i % om.w, i // om.w, lx, ly) <= 70]
    if not cells:
        return None
    i = random.choice(cells)
    return mission(game, g, 'woodroad', 'Mark a road through the elven wood',
                   f'{RL.style(Rl, lo, False)} wants a road for the empire through the elven wood, and timber from it. Walk in '
                   f'and mark the line for the woodcutters, from the forest edge to the {dirto((lx, ly), i % om.w, i // om.w)}.',
                   35, 20, 'crown', spot=[i % om.w, i // om.w], reach=1, where='the forest edge',
                   kid=(kingdom_of(game, lo).id if kingdom_of(game, lo) else None))


def arrive_woodroad(game, m):
    return ('Old trees, older than any house of the empire. Somewhere above you, someone is watching.',
            [('Mark the line, tree by tree', 'mark'), ('Leave the wood as it is', 'refuse')])


def do_woodroad(game, m, choice):
    from . import missions as MS
    if choice == 'refuse':
        MS.fail(game, m, 'You left the wood as it is.')
        fx(game, faction=[('circle', 3)])
        return
    PWS(game)['forest']['edge'] = min(100, PWS(game)['forest']['edge'] + 20)
    fx(game, faction=[('circle', -10)])
    turnin(game, m, 'The axe-marks run white through the green. An arrow thuds into the tree beside your head: a warning.')


@task('supplies', 'lord', 'Supplies for the Watch')
def make_supplies(game, g):
    wt = PWS(game).get('watch')
    if not wt:
        return None
    st = game.world.sites[random.choice(wt['forts'])]
    return mission(game, g, 'supplies', f'Bread for {wt["name"].replace("The ", "the ")}',
                   f'{wt["name"]} is short of bread. Bring 6 Grain to {st.name} before the snow.', 30, 20, 'crown',
                   spot=[st.x, st.y], reach=1, where=st.name, good='grain', qty=6, kid=g.get('kid'))


def arrive_supplies(game, m):
    p = game.player
    q = m.data['qty']
    if p.cargo.get('grain', 0) >= q:
        return ('The soldiers of the Watch come out to the gate to see the carts. Some of them have not eaten bread in a week.',
                [('Hand over the grain', 'give')])
    game.msg(f'The Watch still waits for {q} Grain (you carry {p.cargo.get("grain", 0)}).', 'info')
    m.data['cool'] = game.turn + 80
    return None


def do_supplies(game, m, choice):
    p = game.player
    q = m.data['qty']
    p.cargo['grain'] -= q
    if not p.cargo['grain']:
        del p.cargo['grain']
        p.cost_basis.pop('grain', None)
    wt = PWS(game).get('watch')
    if wt:
        wt['strength'] = min(20, wt['strength'] + 3)
    from . import missions as MS
    MS.complete(game, m, [])


@task('pass', 'lord', 'A hidden pass')
def make_pass(game, g):
    from . import realms as RL
    idx, rd = raider_of(game, 'pass')
    Rl = R(game)
    lo = Rl.lord(g['lid'])
    kg = kingdom_of(game, lo)
    if rd is None or not kg or not any(kg.id in (w_['a'], w_['b']) for w_ in Rl.wars):
        return None
    sp = spot(game, rd['x'], rd['y'], 3, 9)
    if not sp:
        return None
    return mission(game, g, 'pass', 'Find a hidden pass for the host',
                   f'The host of {kg.short} must cross the mountains by {rd["land"]}, where the pass clans keep the ways. '
                   f'Find the hidden pass, by bargain or by climbing.', 40, 25, 'crown', spot=list(sp), reach=1,
                   where=rd['land'], raider=idx, kid=kg.id)


def arrive_pass(game, m):
    opts = [('Climb and look for it yourself', 'climb')]
    if game.player.gold >= 1500:
        opts.append(('Pay the clan for a guide (15s)', 'pay'))
    return ('Rock and snow, a goat track that goes nowhere twice. The clan watches from the heights.', opts + [('Not now', 'leave')])


def do_pass(game, m, choice):
    if choice == 'leave':
        m.data['cool'] = game.turn + 60
        return
    rd = PWS(game)['raiders'][m.data['raider']]
    if choice == 'pay':
        game.player.gold -= 1500
    elif random.random() > stat_chance(game, 'vit'):
        x, y = m.data['spot']
        fight(game, m, ['pass_clansman', 'pass_slinger'], lvl_at(game, x, y, 2), 0, 'The clan does not like strangers on its rocks.')
        return
    rd['angry'] = rd.get('angry', 0) + (0 if choice == 'pay' else 1)
    won_pass(game, m)


def won_pass(game, m):
    for w_ in R(game).wars:
        if m.data['kid'] in (w_['a'], w_['b']):
            w_['score'] += 1 if w_['a'] == m.data['kid'] else -1
    favour(game, m.data.get('kid'), 5)
    turnin(game, m, 'The pass is there, between two shoulders of rock, wide enough for horses.')


@task('canyon_scout', 'lord', 'Scout the cliff village')
def make_canyon(game, g):
    from . import realms as RL
    idx, rd = raider_of(game, 'canyon')
    if rd is None:
        return None
    Rl = R(game)
    lo = Rl.lord(g['lid'])
    return mission(game, g, 'canyon_scout', f'Scout {rd["land"]}',
                   f'The {rd["people"]} rob the caravans out of their cliff village, {rd["land"]}. {RL.style(Rl, lo, False)} wants '
                   f'to know how many they are, and how it can be climbed.', 35, 20, 'crown', spot=[rd['x'], rd['y']], reach=3,
                   where=rd['land'], raider=idx, kid=(kingdom_of(game, lo).id if kingdom_of(game, lo) else None))


def arrive_canyon(game, m):
    return ('Houses cut into the red cliff, ladders between them, smoke from a dozen fires. Lookouts on the rim.',
            [('Lie on the rim and count', 'watch'), ('Not now', 'leave')])


def do_canyon(game, m, choice):
    if choice == 'leave':
        m.data['cool'] = game.turn + 60
        return
    game.end_turn(D.DAY_LEN // 4, True)
    if random.random() < .35:
        x, y = m.data['spot']
        fight(game, m, ['canyon_rider', 'canyon_archer'], lvl_at(game, x, y, 2), 0, 'A lookout has seen you!')
        return
    turnin(game, m, 'You count the fires and the ladders, and find the goat path up the back.')


# ------------------------------------------------------------------ the villages' work against the raiders
@task('warn_sails', 'town', 'Sails on the horizon')
def make_warn(game, g):
    s = game.world.settlements[g['sid']]
    idx, rd = raider_of(game, 'sea')
    if rd is None:
        return None
    from . import powers as PW
    if s not in PW.coast_villages(game, rd['x'], rd['y'], 140):
        return None
    sp = PW.landing(game, s)
    if not sp:
        return None
    return mission(game, g, 'warn_sails', 'Set a watch on the beach',
                   f'Fishermen saw sails far out: the longships of the {rd["people"]}. {s.name} has no soldiers. Set a watch on '
                   f'the beach, to the {dirto((s.x, s.y), *sp)}, and ring the bell when they come.', 20, 15, s.faction,
                   spot=list(sp), reach=1, where='the beach', raider=idx, village=s.id)


def arrive_warn(game, m):
    return ('Grey sea, grey sky. A good place to see from. The bell rope runs down to the village.',
            [('Keep watch through the night', 'watch'), ('Not now', 'leave')])


def do_warn(game, m, choice):
    if choice == 'leave':
        m.data['cool'] = game.turn + 60
        return
    game.end_turn(D.DAY_LEN // 3, True)
    rd = PWS(game)['raiders'][m.data['raider']]
    rd['warned'][m.data['village']] = game.day + 40
    turnin(game, m, 'Before dawn you see them: dark hulls, oars. You ring the bell, and the village is ready.')


@task('mist_child', 'town', 'Lost in the mist')
def make_mist(game, g):
    s = game.world.settlements[g['sid']]
    idx, rd = raider_of(game, 'mist')
    if rd is None or cheb(s.x, s.y, rd['x'], rd['y']) > 60:
        return None
    sp = spot(game, (s.x + rd['x']) // 2, (s.y + rd['y']) // 2, 2, 8)
    if not sp:
        return None
    return mission(game, g, 'mist_child', 'Find a child lost in the mist',
                   f'A child of {s.name} went out after a goat in the morning mist and did not come back. They say the mist '
                   f'folk take children. Look to the {dirto((s.x, s.y), *sp)}.', 20, 8, s.faction, spot=list(sp), reach=1,
                   where='the marsh', raider=idx, village=s.id)


def arrive_mist(game, m):
    return ('Small footprints in the mud, going on into the reeds. Then other prints beside them, bare and long-toed.',
            [('Follow the footprints', 'follow'), ('Not now', 'leave')])


def do_mist(game, m, choice):
    if choice == 'leave':
        m.data['cool'] = game.turn + 60
        return
    x, y = m.data['spot']
    if random.random() < .55:
        turnin(game, m, 'You find the child asleep on a dry hummock, wrapped in a grey cloak that is not hers. The goat is there too.')
        return
    fight(game, m, ['mist_stalker', 'mist_stalker'], lvl_at(game, x, y, 2), 0, 'Grey shapes stand up out of the reeds.')


def won_mist(game, m):
    turnin(game, m, 'Behind them, in a reed hut, the child. Crying, but whole.')


@task('ice', 'town', 'Break the ice')
def make_ice(game, g):
    from . import calendar as CAL
    s = game.world.settlements[g['sid']]
    idx, rd = raider_of(game, 'ice')
    if rd is None or CAL.season(game.day) != 'winter' or cheb(s.x, s.y, rd['x'], rd['y']) > 70:
        return None
    from .jobs import _beside
    sp = _beside(game, s.x, s.y, 3, 10, (D.RIVER, D.WATER))
    if not sp:
        return None
    return mission(game, g, 'ice', 'Break the river ice',
                   f'The river is frozen hard, and the ice raiders of {rd["land"]} come south over the ice in winter. Break it '
                   f'below {s.name}, to the {dirto((s.x, s.y), *sp)}, before they come.', 20, 10, s.faction, spot=list(sp), reach=1,
                   where='the frozen river', raider=idx, village=s.id)


def arrive_ice(game, m):
    return ('The ice is grey and thick as a man\'s arm. It will take a day with an axe.', [('Break the ice', 'break'), ('Not now', 'leave')])


def do_ice(game, m, choice):
    if choice == 'leave':
        m.data['cool'] = game.turn + 60
        return
    game.end_turn(D.DAY_LEN // 2, True)
    rd = PWS(game)['raiders'][m.data['raider']]
    s = game.world.settlements[m.data['village']]
    for v in villages_near(game, s.x, s.y, 30):
        rd['warned'][v.id] = game.day + 30
    turnin(game, m, 'Black water opens behind you. No sledge will cross here this winter.')


@task('escort_caravan', 'town', 'Through the dunes')
def make_caravan(game, g):
    s = game.world.settlements[g['sid']]
    idx, rd = raider_of(game, 'desert')
    if rd is None or cheb(s.x, s.y, rd['x'], rd['y']) > 80:
        return None
    sp = spot(game, (s.x + rd['x']) // 2, (s.y + rd['y']) // 2, 2, 8)
    if not sp:
        return None
    return mission(game, g, 'escort_caravan', 'Bring a caravan through the dunes',
                   f'A salt caravan leaves {s.name} for the far oases, and the riders of {rd["land"]} watch the road. Ride with it '
                   f'as far as the dune wells, to the {dirto((s.x, s.y), *sp)}.', 25, 12, s.faction, spot=list(sp), reach=1,
                   where='the dune wells', raider=idx, village=s.id)


def arrive_caravan(game, m):
    return ('The camels kneel at the wells. Dust on the skyline: riders, coming fast.', [('Stand by the caravan', 'stand')])


def do_caravan(game, m, choice):
    x, y = m.data['spot']
    if random.random() < .35:
        turnin(game, m, 'The riders look you over from the dune crest, and ride on. The caravan is through.')
        return
    fight(game, m, ['dune_rider', 'dune_rider', 'dune_archer'], lvl_at(game, x, y, 2), 0, 'They come down the dune at a gallop.')


@task('false_lights', 'town', 'The false lights')
def make_lights(game, g):
    s = game.world.settlements[g['sid']]
    idx, rd = raider_of(game, 'wreckers')
    if rd is None or cheb(s.x, s.y, rd['x'], rd['y']) > 50:
        return None
    sp = spot(game, rd['x'], rd['y'], 2, 6)
    if not sp:
        return None
    return mission(game, g, 'false_lights', 'Put out the false lights',
                   f'Ships go onto the rocks near {rd["land"]} on storm nights, and lights are seen on the cliffs. Put them out '
                   f'on the next storm night, to the {dirto((s.x, s.y), *sp)}.', 25, 20, s.faction, spot=list(sp), reach=1,
                   where='the cliffs', raider=idx)


def arrive_lights(game, m):
    return ('Wind and rain off the sea. On the cliff a lantern swings on a pole, and men wait below it with hooks and ropes.',
            [('Put out the light', 'fight'), ('Not now', 'leave')])


def do_lights(game, m, choice):
    if choice == 'leave':
        m.data['cool'] = game.turn + 60
        return
    x, y = m.data['spot']
    fight(game, m, ['wrecker', 'wrecker', 'wrecker'], lvl_at(game, x, y, 1), 0, 'The wreckers turn on you with their hooks.')


def won_lights(game, m):
    rd = PWS(game)['raiders'][m.data['raider']]
    rd['strength'] = max(1, rd['strength'] - 2)
    turnin(game, m, 'The lantern goes over the cliff. Out at sea, a ship finds its way past the rocks.')


@task('convict', 'town', 'A son for the Watch')
def make_convict(game, g):
    wt = PWS(game).get('watch')
    if not wt:
        return None
    s = game.world.settlements[g['sid']]
    st = game.world.sites[random.choice(wt['forts'])]
    if cheb(s.x, s.y, st.x, st.y) > 90:
        return None
    sp = spot(game, (s.x + st.x) // 2, (s.y + st.y) // 2, 2, 8)
    if not sp:
        return None
    from .jobs import name_of
    son = name_of(game)
    return mission(game, g, 'convict', f'Free {son} on the road',
                   f'A mother at the inn of {s.name}: her son {son} was sold to the Border Watch for a theft of bread. They take '
                   f'him north in chains. Cut him loose on the road, to the {dirto((s.x, s.y), *sp)}, before he reaches the forts.',
                   20, 10, None, spot=list(sp), reach=1, where='the north road', son=son)


def arrive_convict(game, m):
    return (f'A cart, two soldiers of the Watch, and {m.data["son"]} in chains in the back, asleep against the boards.',
            [('Cut him loose while they sleep', 'sneak'), ('Fight the guards for him', 'fight'), ('Not now', 'leave')])


def do_convict(game, m, choice):
    if choice == 'leave':
        m.data['cool'] = game.turn + 60
        return
    x, y = m.data['spot']
    if choice == 'sneak' and random.random() < stat_chance(game, 'dex'):
        won_convict(game, m)
        return
    fight(game, m, ['watch_soldier', 'watch_soldier'], lvl_at(game, x, y, 1), 0, 'The guards wake.')


def won_convict(game, m):
    wt = PWS(game).get('watch')
    if wt:
        wt['strength'] = max(2, wt['strength'] - 1)
    fx(game, crime=(4, 'freeing a convict', .3))
    turnin(game, m, f'{m.data["son"]} runs for home, chains and all.')


@task('tribe_arms', 'town', 'Arms for the tribes')
def make_arms(game, g):
    s = game.world.settlements[g['sid']]
    camps = [st for st in game.world.sites if st.kind == 'warcamp' and cheb(st.x, st.y, s.x, s.y) <= 90]
    if not s.is_city or not camps:
        return None
    st = random.choice(camps)
    return mission(game, g, 'tribe_arms', f'Arms for {st.name}',
                   f'A merchant with no name and good boots: "Six loads of Arms to {st.name}. The orcs pay in gold, and nobody '
                   f'needs to know." The camp lies to the {dirto((s.x, s.y), st.x, st.y)}.', 60, 25, None, spot=[st.x, st.y],
                   reach=2, where=st.name, good='arms', qty=6, dark='arms')


def arrive_tribe_arms(game, m):
    p = game.player
    q = m.data['qty']
    if p.cargo.get('arms', 0) < q:
        game.msg(f'The orcs want {q} Arms (you carry {p.cargo.get("arms", 0)}).', 'info')
        m.data['cool'] = game.turn + 80
        return None
    return ('Orc guards look you over, then the loads. A goblin runs off to fetch the chief.',
            [('Hand over the arms', 'give'), ('Not now', 'leave')])


def do_tribe_arms(game, m, choice):
    if choice == 'leave':
        m.data['cool'] = game.turn + 60
        return
    p = game.player
    q = m.data['qty']
    p.cargo['arms'] -= q
    if not p.cargo['arms']:
        del p.cargo['arms']
        p.cost_basis.pop('arms', None)
    pw = PWS(game)
    if pw['tribes']:
        max(pw['tribes'], key=lambda t: t['strength'])['strength'] += 1
    fx(game, faction=[('crown', -6), ('horde', 4)])
    from . import missions as MS
    MS.complete(game, m, [])


@task('reef', 'town', 'Pearls from the reef')
def make_reef(game, g):
    s = game.world.settlements[g['sid']]
    idx, rd = raider_of(game, 'island')
    if rd is None or not s.is_city or cheb(s.x, s.y, rd['x'], rd['y']) > 120:
        return None
    sp = spot(game, rd['x'], rd['y'], 2, 7)
    if not sp:
        return None
    return mission(game, g, 'reef', 'Pearls from the voyagers\' reef',
                   f'A merchant house of {s.name} wants pearls from the reefs the voyagers of {rd["land"]} call theirs. Dive for '
                   f'them, and do not be seen.', 45, 25, None, spot=list(sp), reach=1, where='the reef', raider=idx, dark='reef')


def arrive_reef(game, m):
    return ('Clear water over white sand, and the dark shapes of the oyster beds.', [('Dive for pearls', 'dive'), ('Not now', 'leave')])


def do_reef(game, m, choice):
    if choice == 'leave':
        m.data['cool'] = game.turn + 60
        return
    rd = PWS(game)['raiders'][m.data['raider']]
    rd['angry'] = rd.get('angry', 0) + 2
    if random.random() < .4:
        x, y = m.data['spot']
        fight(game, m, ['reef_warrior', 'reef_spear'], lvl_at(game, x, y, 2), 0, 'Canoes come round the point, fast.')
        return
    turnin(game, m, 'A bag of pearls, wet and grey and worth a fortune. Behind you, a conch blows.')


# ------------------------------------------------------------------ the raiders' own work
@task('sail', 'chief:sea', 'Sail with the longships')
def make_sail(game, g):
    rd = PWS(game)['raiders'][g['raider']]
    from . import powers as PW
    vs = PW.coast_villages(game, rd['x'], rd['y'], 140)
    temples = [st for st in game.world.sites if st.kind in ('temple', 'monastery') and any(cheb(st.x, st.y, v.x, v.y) <= 10 for v in vs)]
    if not temples:
        return None
    st = random.choice(temples)
    return mission(game, g, 'sail', f'Plunder {st.name}', f'"Sail with us. There is a church on the coast with silver on the '
                   f'altar, {st.name}. You take a share like any oarsman." The realm will not forgive it.', 50, 25, None,
                   spot=[st.x, st.y], reach=1, where=st.name, temple=st.id, dark='plunder')


def arrive_sail(game, m):
    return ('The longship grinds onto the shingle below the church. The raiders leap over the side, axes up. The priests '
            'are ringing the bell.', [('Go up with them', 'go'), ('Stay with the ship', 'stay')])


def do_sail(game, m, choice):
    from . import missions as MS
    rd = PWS(game)['raiders'][m.data['giver']['raider']]
    if choice == 'stay':
        MS.fail(game, m, 'You stayed with the ship. The raiders will not ask again.')
        return
    rd['strength'] += 1
    fx(game, faction=[('crown', -10)], god=-6, crime=(10, 'the plunder of a church', .6))
    from . import realms as RL
    st = game.world.sites[m.data['temple']]
    RL.news(game, f'Sea raiders plundered {st.name} and carried off its silver.', st.x, st.y)
    turnin(game, m, 'The silver goes into the sacks. Your share waits in the jarl\'s hall.')


@task('betray_caravan', 'chief:desert', 'A caravan for the riders')
def make_betray_caravan(game, g):
    rd = PWS(game)['raiders'][g['raider']]
    sp = spot(game, rd['x'], rd['y'], 8, 20)
    if not sp:
        return None
    return mission(game, g, 'betray_caravan', 'Lead a caravan into the dunes',
                   '"A rich caravan goes north with the new moon. Ride with it as a guard, and lead it to the dry wells where we '
                   'wait." Half the salt is yours.', 55, 20, None, spot=list(sp), reach=1, where='the dry wells', dark='betrayal')


def arrive_betray_caravan(game, m):
    return ('The caravan follows you trustingly off the road toward the dry wells. The drivers are singing.',
            [('Lead them in', 'lead'), ('Turn them back to the road', 'back')])


def do_betray_caravan(game, m, choice):
    from . import missions as MS
    if choice == 'back':
        MS.fail(game, m, 'You turned the caravan back.')
        fx(game, guild=[('iron', 2)])
        return
    fx(game, faction=[('league', -8)], crime=(8, 'betraying a caravan', .5))
    turnin(game, m, 'The riders come over the dune. It is quick. You do not look back.')


@task('guide_sledges', 'chief:ice', 'Over the ice')
def make_guide(game, g):
    from . import calendar as CAL
    rd = PWS(game)['raiders'][g['raider']]
    if CAL.season(game.day) != 'winter':
        return None
    vs = villages_near(game, rd['x'], rd['y'], 70, lambda s: game.world.regions[s.region].faction == 'crown')
    if not vs:
        return None
    v = random.choice(vs)
    return mission(game, g, 'guide_sledges', f'Guide the sledges to {v.name}',
                   f'"The ice is thin in places we do not know. Show our sledges the way to {v.name}, and you will have furs '
                   f'and silver."', 50, 15, None, spot=[v.x, v.y], reach=3, where=v.name, village=v.id, dark='betrayal')


def arrive_guide(game, m):
    v = game.world.settlements[m.data['village']]
    return (f'The lights of {v.name} across the frozen river. The sledges wait behind you, the dogs quiet.',
            [('Lead them across', 'lead'), ('Take them onto the thin ice', 'thin')])


def do_guide(game, m, choice):
    from . import missions as MS
    v = game.world.settlements[m.data['village']]
    if choice == 'thin':
        MS.fail(game, m, 'The ice groans and breaks under the first sledge. The raiders turn back, cursing you.')
        fx(game, town=[(v.id, 8)])
        return
    from .living import PLUNDER_DAYS
    v.plundered = game.day + PLUNDER_DAYS
    v.event = ('war', 6)
    fx(game, town=[(v.id, -25)], faction=[('crown', -8)], crime=(10, 'guiding raiders to a village', .4))
    turnin(game, m, f'The sledges go howling into {v.name}.')


@task('avalanche', 'chief:pass', 'The mountain\'s anger')
def make_avalanche(game, g):
    rd = PWS(game)['raiders'][g['raider']]
    sp = spot(game, rd['x'], rd['y'], 3, 9)
    if not sp:
        return None
    return mission(game, g, 'avalanche', 'Loose the avalanche', '"A lord\'s men come up the pass and will not pay the toll. '
                   'Help us loose the snow on them. The mountain will be pleased, and so will we."', 45, 15, None,
                   spot=list(sp), reach=1, where='the high snowfield', dark='avalanche')


def arrive_avalanche(game, m):
    return ('The snowfield hangs over the pass like a held breath. Far below, a line of soldiers toils upward.',
            [('Loose it', 'loose'), ('Shout a warning down to them', 'warn')])


def do_avalanche(game, m, choice):
    from . import missions as MS
    if choice == 'warn':
        MS.fail(game, m, 'The soldiers turn back. The clan will not forget.')
        fx(game, faction=[('crown', 3)])
        return
    fx(game, faction=[('crown', -8)])
    turnin(game, m, 'A crack like thunder. The mountain comes down, and the pass is silent.')


@task('strip_wreck', 'chief:wreckers', 'A wreck on the rocks')
def make_wreck(game, g):
    rd = PWS(game)['raiders'][g['raider']]
    sp = spot(game, rd['x'], rd['y'], 2, 8)
    if not sp:
        return None
    return mission(game, g, 'strip_wreck', 'Strip the wreck', '"A ship on the rocks, full of wine and cloth. Help us strip her '
                   'before the lord\'s men come, and keep your mouth shut after."', 30, 8, None, spot=list(sp), reach=1,
                   where='the wreck', dark='wreck')


def arrive_wreck(game, m):
    return ('The ship lies broken on the rocks, the sea washing through her. A sailor is still clinging to the rigging.',
            [('Strip her with the others', 'strip'), ('Get the sailor ashore first', 'save')])


def do_wreck(game, m, choice):
    if choice == 'save':
        fx(game, god=3)
        game.msg('You haul the sailor ashore. The wreckers look at you sideways, but they say nothing.', 'info')
    fx(game, crime=(4, 'plundering a wreck', .3))
    turnin(game, m, 'Barrels and bales go up the cliff by rope. Nobody saw. Nobody will say.')


@task('kill_spy', 'chief:canyon', 'The baron\'s spy')
def make_spy(game, g):
    rd = PWS(game)['raiders'][g['raider']]
    sp = spot(game, rd['x'], rd['y'], 3, 10)
    if not sp:
        return None
    return mission(game, g, 'kill_spy', 'Kill the baron\'s spy', '"A spy of the baron counts our ladders from the rim. Find him '
                   'in the side canyons and make sure he does not ride home."', 40, 12, None, spot=list(sp), reach=1,
                   where='the side canyons', dark='spy')


def arrive_spy(game, m):
    return ('A man in a grey cloak, lying on the rim, writing on a tablet.', [('Kill him', 'kill'), ('Let him go', 'free')])


def do_spy(game, m, choice):
    from . import missions as MS
    if choice == 'free':
        MS.fail(game, m, 'You let the spy go.')
        return
    x, y = m.data['spot']
    fight(game, m, ['soldier', 'crossbow'], lvl_at(game, x, y, 2), 0, 'He has friends.')


def won_spy(game, m):
    fx(game, faction=[('crown', -6)])
    turnin(game, m, 'The tablet goes into the canyon after him.')


@task('pearl', 'chief:island', 'The stolen pearl')
def make_pearl(game, g):
    rd = PWS(game)['raiders'][g['raider']]
    towns = [s for s in game.world.settlements if s.kind in ('town', 'city', 'metropolis') and cheb(s.x, s.y, rd['x'], rd['y']) <= 120]
    if not towns:
        return None
    s = random.choice(towns)
    sp = spot(game, s.x, s.y, 2, 6)
    if not sp:
        return None
    return mission(game, g, 'pearl', 'Bring back the Moon Pearl', f'"A trader stole the Moon Pearl of our reef. He sells it in '
                   f'{s.name}. Bring it home to the reef." The voyagers do not forget a friend.', 35, 25, None, spot=list(sp),
                   reach=1, where=f'near {s.name}')


def arrive_pearl(game, m):
    opts = []
    if game.player.gold >= 2000:
        opts.append(('Buy it back from the trader (20s)', 'buy'))
    return ('The trader has a stall by the road, the pearl in a velvet box, two hired guards beside him.',
            opts + [('Take it from him', 'take'), ('Not now', 'leave')])


def do_pearl(game, m, choice):
    if choice == 'leave':
        m.data['cool'] = game.turn + 60
        return
    if choice == 'buy':
        game.player.gold -= 2000
        won_pearl(game, m)
        return
    x, y = m.data['spot']
    fight(game, m, ['bandit', 'bandit'], lvl_at(game, x, y, 1), 0, 'The guards draw.')


def won_pearl(game, m):
    rd = PWS(game)['raiders'][m.data['giver']['raider']]
    rd['friend'] = True
    rd['angry'] = 0
    turnin(game, m, 'The pearl is cold and heavy in your hand, the colour of the moon on water.')


# ------------------------------------------------------------------ the church, the witches, the Watch, the rebels, the exile
@task('witch_hunt', 'prior', 'Track down a witch')
def make_hunt(game, g):
    circles = [game.world.sites[i] for i in PWS(game)['circles'] if not getattr(game.world.sites[i], 'burnt', False)]
    if not circles:
        return None
    st = random.choice(circles)
    return mission(game, g, 'witch_hunt', f'Find the witch of {st.name}', f'A witch sells curses on the moor, at {st.name}. '
                   f'Find her and bring the Order to her.', 30, 25, 'crown', spot=[st.x, st.y], reach=1, where=st.name, circle=st.id)


def arrive_hunt(game, m):
    return ('Standing stones in a ring, a hut of turf, a fire with a pot on it. The witch looks up from the pot, unafraid.',
            [('Seize her for the Order', 'seize'), ('Let her go', 'free')])


def do_hunt(game, m, choice):
    from . import missions as MS
    from . import powers as PW
    st = game.world.sites[m.data['circle']]
    if choice == 'free':
        st.warned = game.day + 60
        MS.fail(game, m, 'You let the witch go.')
        return
    PW.mark_site(game, st.id, 'burnt')
    fx(game, god=('solmara', 2), faction=[('circle', -3)])
    turnin(game, m, 'The knights of the Order come at dusk with torches.')


@task('warn_witch', 'witch', 'Warn a sister')
def make_warn_witch(game, g):
    here = g['site']
    others = [game.world.sites[i] for i in PWS(game)['circles'] if i != here and not getattr(game.world.sites[i], 'burnt', False)]
    if not others:
        return None
    st = random.choice(others)
    return mission(game, g, 'warn_witch', f'Warn the circle of {st.name}', f'"The Order rides for my sister at {st.name}. Warn '
                   f'her before they come, and I will remember you."', 20, 15, None, spot=[st.x, st.y], reach=1, where=st.name, circle=st.id)


def arrive_warn_witch(game, m):
    return ('The witch of the circle listens, nods once, and starts putting out the fire.', [('Tell her everything', 'tell')])


def do_warn_witch(game, m, choice):
    st = game.world.sites[m.data['circle']]
    st.warned = game.day + 90
    st.found = True
    turnin(game, m, 'By nightfall the circle is empty, and the knights will find only cold ashes.')


@task('smuggle_arms', 'rebel', 'Arms for the rising')
def make_smuggle(game, g):
    rv = PWS(game).get('revolt')
    if not rv:
        return None
    st = game.world.sites[rv['site']]
    return mission(game, g, 'smuggle_arms', 'Arms for the rising', '"We fight with scythes. Bring us 4 Arms, and we will fight '
                   'with spears." Bring them here, to the camp.', 30, 25, None, spot=[st.x, st.y], reach=1, where=st.name,
                   good='arms', qty=4, dark='rebel')


def arrive_smuggle(game, m):
    p = game.player
    q = m.data['qty']
    if p.cargo.get('arms', 0) < q:
        game.msg(f'The rebels need {q} Arms (you carry {p.cargo.get("arms", 0)}).', 'info')
        m.data['cool'] = game.turn + 80
        return None
    return ('The rebels gather round the loads, touching the spearheads like holy things.', [('Hand them over', 'give')])


def do_smuggle(game, m, choice):
    p = game.player
    q = m.data['qty']
    p.cargo['arms'] -= q
    if not p.cargo['arms']:
        del p.cargo['arms']
        p.cost_basis.pop('arms', None)
    rv = PWS(game).get('revolt')
    if rv:
        rv['help'] = rv.get('help', 0) + 2
    fx(game, faction=[('crown', -5)], god=('solmara', 2))
    from . import missions as MS
    MS.complete(game, m, [])


@task('pretender_letter', 'pretender', 'A letter to the faithful')
def make_pletter(game, g):
    from . import realms as RL
    pt = PWS(game).get('pretender')
    if not pt:
        return None
    Rl = R(game)
    houses = [h for h in Rl.houses if h.rank == 'lesser' and not h.fallen and h.region in Rl.baronies
              and Rl.baronies[h.region].kingdom == pt['kid'] and h.seat]
    if not houses:
        return None
    h = random.choice(houses)
    x, y = RL.seat_pos(game.world, h.seat)
    return mission(game, g, 'pretender_letter', f'A letter for House {h.name}', f'"House {h.name} was loyal to my father. '
                   f'Carry this to {RL.seat_name(game.world, h.seat)}, and let no king\'s man see it."', 30, 25, None,
                   spot=[x, y], reach=1, where=RL.seat_name(game.world, h.seat), dark='treason')


def arrive_pletter(game, m):
    return ('The old lord reads the letter twice, and burns it in the hearth. "Tell him... tell him yes."', [('Bow and go', 'go')])


def do_pletter(game, m, choice):
    pt = PWS(game).get('pretender')
    if pt:
        pt['letters'] = pt.get('letters', 0) + 2
    fx(game, faction=[('crown', -4)])
    from . import missions as MS
    MS.complete(game, m, [])


# ------------------------------------------------------------------ the dwarves' book and the elves' wood
@task('debt', 'keeper', 'A debt in the book')
def make_debt(game, g):
    from . import realms as RL
    w = game.world
    book = PWS(game)['grudges'].get(g['sid'], [])
    gs = [x for x in book if not x['settled'] and x['against'][0] == 'k']
    if not gs:
        return None
    gr = random.choice(gs)
    kg = R(game).kingdoms[gr['against'][1]]
    x, y = RL.seat_pos(w, kg.seat)
    amount = 10 + gr['weight'] * 8
    return mission(game, g, 'debt', f'Collect a debt from {kg.short}', f'The book of {w.settlements[g["sid"]].name}: '
                   f'{gr["what"]}. Go to {RL.seat_name(w, kg.seat)} and bring back what is owed: {amount} silver.', 25, 30, 'clan',
                   spot=[x, y], reach=2, where=RL.seat_name(w, kg.seat), grudge=gr['id'], hold=g['sid'], amount=amount)


def arrive_debt(game, m):
    opts = [('Ask the king\'s steward for the debt', 'ask')]
    if game.player.gold >= m.data['amount'] * 100:
        opts.append((f'Pay it yourself ({m.data["amount"]}s)', 'pay'))
    return ('The steward of the court hears the dwarves\' claim with a sour face.', opts + [('Not now', 'leave')])


def do_debt(game, m, choice):
    from . import powers as PW
    from . import missions as MS
    if choice == 'leave':
        m.data['cool'] = game.turn + 60
        return
    if choice == 'pay':
        game.player.gold -= m.data['amount'] * 100
    elif random.random() > stat_chance(game, 'ene', .45):
        MS.fail(game, m, '"The crown owes nothing to the dwarves." The steward has you shown out.')
        return
    PW.settle(game, m.data['hold'], m.data['grudge'], 'paid in gold')
    turnin(game, m, 'The debt is paid. The keeper of the book will strike it out.')


@task('killer', 'keeper', 'A killer to hand over')
def make_killer(game, g):
    s = game.world.settlements[g['sid']]
    book = PWS(game)['grudges'].get(g['sid'], [])
    gs = [x for x in book if not x['settled']]
    if not gs:
        return None
    gr = random.choice(gs)
    sp = spot(game, s.x, s.y, 10, 30)
    if not sp:
        return None
    from .jobs import name_of
    who = f'{name_of(game)} {random.choice(["Crowe", "Ashby", "Grimm", "Lusk"])}'
    return mission(game, g, 'killer', f'Hand over {who}', f'The book of {s.name}: {gr["what"]}. The one who did it, {who}, hides '
                   f'in the wilds to the {dirto((s.x, s.y), *sp)}. Bring him to the hold, alive.', 30, 25, 'clan', spot=list(sp),
                   reach=1, where='the wilds', grudge=gr['id'], hold=g['sid'], leader=who)


def arrive_killer(game, m):
    return (f'{m.data["leader"]} and two hard men sit by a fire. He knows why you have come.', [('Take him', 'take'), ('Not now', 'leave')])


def do_killer(game, m, choice):
    if choice == 'leave':
        m.data['cool'] = game.turn + 60
        return
    x, y = m.data['spot']
    fight(game, m, ['brigand', 'bandit', 'bandit'], lvl_at(game, x, y, 2), 1)


def won_killer(game, m):
    from . import powers as PW
    PW.settle(game, m.data['hold'], m.data['grudge'], 'the killer handed over')
    turnin(game, m, f'{m.data["leader"]} goes to the hold in chains. The dwarves will judge him.')


@task('mediate', 'loremaster', 'Speak for the wood')
def make_mediate(game, g):
    w = game.world
    if not PWS(game)['forest']['cuts']:
        return None
    i = PWS(game)['forest']['cuts'][-1]
    om = game.maps['over']
    return mission(game, g, 'mediate', 'Speak between the elves and the woodcutters', 'The woodcutters of the empire eat into the '
                   'wood, and the young elves want to shoot them. Go to the edge where they cut, and make a peace both can keep.',
                   25, 25, 'circle', spot=[i % om.w, i // om.w], reach=2, where='the clear-cut')


def arrive_mediate(game, m):
    return ('Stumps, sawdust and a woodcutters\' camp on one side; on the other, the trees, and eyes in them.',
            [('Speak for the elves: the cutting stops here', 'elves'), ('Speak for the woodcutters: a ride\'s width, no more', 'cutters')])


def do_mediate(game, m, choice):
    fo = PWS(game)['forest']
    if choice == 'elves':
        fo['edge'] = max(0, fo['edge'] - 20)
        fx(game, faction=[('circle', 5), ('crown', -2)])
    else:
        fo['edge'] = max(0, fo['edge'] - 8)
        fx(game, faction=[('crown', 2)])
    turnin(game, m, 'Words go back and forth until dark. In the end both sides spit and agree.')


@task('woodcutters', 'loremaster', 'Chase off the woodcutters')
def make_cutters(game, g):
    if not PWS(game)['forest']['cuts']:
        return None
    i = random.choice(PWS(game)['forest']['cuts'][-20:])
    om = game.maps['over']
    return mission(game, g, 'woodcutters', 'Chase off the woodcutters', 'Woodcutters fell the old trees at the forest edge. '
                   'Drive them off, without killing if you can.', 25, 20, 'circle', spot=[i % om.w, i // om.w], reach=1,
                   where='the clear-cut')


def arrive_cutters(game, m):
    return ('Axes ring. A dozen woodcutters, and the baron\'s men guarding them.', [('Drive them off', 'fight'), ('Not now', 'leave')])


def do_cutters(game, m, choice):
    if choice == 'leave':
        m.data['cool'] = game.turn + 60
        return
    x, y = m.data['spot']
    fight(game, m, ['watchman', 'watchman', 'soldier'], lvl_at(game, x, y, 1), 0, 'The baron\'s men stand in your way.')


def won_cutters(game, m):
    PWS(game)['forest']['edge'] = max(0, PWS(game)['forest']['edge'] - 15)
    fx(game, faction=[('crown', -4)])
    turnin(game, m, 'The woodcutters run, leaving their axes in the stumps.')


SCENES = {
    'letter': (arrive_letter, do_letter, None), 'claimant': (arrive_claimant, do_claimant, won_claimant),
    'save_heir': (arrive_save_heir, do_save_heir, won_save_heir), 'kill_heir': (arrive_kill_heir, do_kill_heir, won_kill_heir),
    'gate': (arrive_gate, do_gate, won_gate), 'wedding': (arrive_wedding, do_wedding, won_wedding),
    'hostage': (arrive_hostage, do_hostage, None), 'hire': (arrive_hire, do_hire, None), 'envoy': (arrive_envoy, do_envoy, None),
    'pay': (arrive_pay, do_pay, None), 'bribe': (arrive_bribe, do_bribe, None), 'catch_rebel': (arrive_catch, do_catch, won_catch),
    'betray_pretender': (arrive_betray, do_betray, None), 'warlord': (arrive_warlord, do_warlord, won_warlord),
    'woodroad': (arrive_woodroad, do_woodroad, None), 'supplies': (arrive_supplies, do_supplies, None),
    'pass': (arrive_pass, do_pass, won_pass), 'canyon_scout': (arrive_canyon, do_canyon, None),
    'warn_sails': (arrive_warn, do_warn, None), 'mist_child': (arrive_mist, do_mist, won_mist), 'ice': (arrive_ice, do_ice, None),
    'escort_caravan': (arrive_caravan, do_caravan, None), 'false_lights': (arrive_lights, do_lights, won_lights),
    'convict': (arrive_convict, do_convict, won_convict), 'tribe_arms': (arrive_tribe_arms, do_tribe_arms, None),
    'reef': (arrive_reef, do_reef, None), 'sail': (arrive_sail, do_sail, None),
    'betray_caravan': (arrive_betray_caravan, do_betray_caravan, None), 'guide_sledges': (arrive_guide, do_guide, None),
    'avalanche': (arrive_avalanche, do_avalanche, None), 'strip_wreck': (arrive_wreck, do_wreck, None),
    'kill_spy': (arrive_spy, do_spy, won_spy), 'pearl': (arrive_pearl, do_pearl, won_pearl),
    'witch_hunt': (arrive_hunt, do_hunt, None), 'warn_witch': (arrive_warn_witch, do_warn_witch, None),
    'smuggle_arms': (arrive_smuggle, do_smuggle, None), 'pretender_letter': (arrive_pletter, do_pletter, None),
    'debt': (arrive_debt, do_debt, None), 'killer': (arrive_killer, do_killer, won_killer),
    'mediate': (arrive_mediate, do_mediate, None), 'woodcutters': (arrive_cutters, do_cutters, won_cutters),
}


# ------------------------------------------------------------------ the frame: arrive, choose, win, hand in
def arrive(game, m):
    """jobs.step: you reached the place of a realm job."""
    from . import events as EV
    sc = SCENES.get(m.data['task'])
    if not sc:
        return False
    out = sc[0](game, m)
    if not out:
        return False
    text, opts = out
    EV.ask(game, 'realmjob', m.title, text, opts, mid=m.id)
    return True


def r_realmjob(game, choice, ctx):
    from . import missions as MS
    m = MS.find(game, ctx['mid'])
    if not m or m.state != 'active':
        return
    sc = SCENES.get(m.data['task'])
    if sc:
        sc[1](game, m, choice)


def won(game, m, ok):
    """jobs.after_fight: the fight of a realm job is over."""
    if not ok:
        m.data['cool'] = game.turn + 60
        return
    sc = SCENES.get(m.data['task'])
    if sc and sc[2]:
        sc[2](game, m)
    else:
        turnin(game, m, 'It is done.')


def target_pos(game, m):
    if m.state == 'turnin':
        g = m.data['giver']
        x, y = giver_pos(game, g)
        return (x, y), m.data['giver_name']
    return tuple(m.data['spot']), m.data.get('where', 'the place')


# ------------------------------------------------------------------ who gives work
def offers(game, g, n=3):
    """Up to n jobs this giver has now."""
    kind = g['kind']
    keys = [k for k, t in TASKS.items() if t['giver'] == kind or (kind == 'chief' and t['giver'] == 'chief:' + g.get('rk', ''))]
    random.shuffle(keys)
    out = []
    from . import missions as MS
    busy = {x.data.get('task') for x in MS.active(game) if x.kind == 'realm'}
    for k in keys:
        if k in busy:
            continue
        try:
            m = TASKS[k]['make'](game, g)
        except (IndexError, KeyError, ValueError):
            m = None
        if m:
            out.append(m)
        if len(out) >= n:
            break
    return out


def board(game, g, key):
    """A giver's offers stay a few days."""
    st = game.__dict__.setdefault('realm_boards', {})
    day, ms = st.get(key, (-99, []))
    if game.day - day >= 4:
        ms = offers(game, g)
        st[key] = (game.day, ms)
    return ms


def offer(game, npc, lo):
    """A lord's work."""
    from . import realms as RL
    Rl = R(game)
    g = dict(kind='lord', lid=lo.id, house=lo.house, name=RL.style(Rl, lo, False))
    show(game, npc, g, f'lord{lo.id}', f'"{random.choice(["I have work for one who can keep their mouth shut.", "There is always work for a sword.", "Listen well."])}"')


def giver_of(game, npc):
    """The giver dict of a power's person, from their role."""
    w = game.world
    role = getattr(npc, 'role', '')
    site = getattr(game.map, 'site', None)
    if role == 'chief':
        rd = w.powers['raiders'][npc.raider]
        return dict(kind='chief', raider=npc.raider, rk=rd['kind'], site=rd['site'], name=npc.name)
    if role in ('prior', 'witch', 'watch_captain', 'merc_captain', 'rebel_leader', 'pretender'):
        k = {'prior': 'prior', 'witch': 'witch', 'watch_captain': 'watch', 'merc_captain': 'merc', 'rebel_leader': 'rebel',
             'pretender': 'pretender'}[role]
        return dict(kind=k, site=site, name=npc.name)
    if role in ('keeper', 'loremaster'):
        sid = getattr(game.map, 'sid', None)
        return dict(kind=role, sid=sid, name=npc.name)
    return None


def offer_giver(game, npc):
    g = giver_of(game, npc)
    if not g:
        return
    show(game, npc, g, f'{g["kind"]}{g.get("site", g.get("sid", ""))}', '"There is something you could do."')


def show(game, npc, g, key, intro):
    from . import events as EV
    from .money import fmt
    ms = board(game, g, key)
    if not ms:
        game.say(npc, random.choice(['"Nothing for you now. Come back in a few days."', '"Not today."']))
        return
    opts = [(f'{m.title} ({fmt(m.reward)})', f'take:{i}') for i, m in enumerate(ms)] + [('Not now', 'bye')]
    EV.ask(game, 'realmoffer', npc.name, intro + '\n\n' + '\n'.join(f'- {m.desc}' for m in ms), opts, board=key)


def r_realmoffer(game, choice, ctx):
    from . import missions as MS
    if not choice.startswith('take:'):
        return
    st = game.__dict__.get('realm_boards', {})
    day, ms = st.get(ctx['board'], (0, []))
    i = int(choice[5:])
    if i >= len(ms):
        return
    m = ms[i]
    if accept(game, m):
        ms.remove(m)


def accept(game, m):
    from . import missions as MS
    if len(MS.active(game)) >= MS.MAX_ACTIVE:
        game.msg(f'You already have {MS.MAX_ACTIVE} jobs. Finish one first.', 'bad')
        return False
    m.state = 'active'
    game.missions.append(m)
    if not m.data.get('nomark'):
        game.reveal_place(*m.data['spot'])
    game.msg(f'Job taken: {m.title}.', 'info')
    from . import guide as GDE
    GDE.tip(game, 'realmjob')
    return True


def turn_in(game, lo, npc):
    """Talking to a lord who gave you a job that is done."""
    from . import missions as MS
    for m in MS.active(game):
        if m.kind != 'realm' or m.state != 'turnin':
            continue
        g = m.data['giver']
        if g['kind'] == 'lord' and (g['lid'] == lo.id or g.get('house') == lo.house):
            favour(game, giver_kid(game, m), 4)
            MS.complete(game, m, [])
            return True
    return False


def turn_in_giver(game, g, npc):
    from . import missions as MS
    for m in MS.active(game):
        if m.kind != 'realm' or m.state != 'turnin':
            continue
        o = m.data['giver']
        if o['kind'] == g['kind'] and (o.get('site') == g.get('site') or o.get('sid') == g.get('sid') or
                                       o.get('raider') == g.get('raider') is not None):
            MS.complete(game, m, [])
            return True
    return False


def for_town(game, s):
    """jobs.MAKE['realm']: the village and town boards ask for help against the raiders."""
    g = dict(kind='town', sid=s.id, name=s.name)
    ms = offers(game, g, 1)
    return ms[0] if ms else None


# ------------------------------------------------------------------ the levy
def levy(game, kg, foe):
    """Your liege calls the levy: a job that comes to you, with a field to fight on."""
    from . import missions as MS
    from . import realms as RL
    Rl = R(game)
    p = game.player
    kn = getattr(p, 'knight', None)
    if not kn:
        return
    lo = Rl.lord(kn['lid'])
    if not lo or any(x.kind == 'realm' and x.data.get('task') == 'levy' for x in MS.active(game)):
        return
    x, y = RL.place_of(game, lo)
    sp = spot(game, x, y, 6, 18)
    if not sp:
        return
    g = dict(kind='lord', lid=lo.id, house=lo.house, name=RL.style(Rl, lo, False))
    what = f'the war with {foe.short}' if foe else 'the emperor\'s call to arms'
    m = mission(game, g, 'levy', f'Answer the levy of {kg.short}', f'Your liege {RL.style(Rl, lo, False)} calls you to {what}. '
                f'The host gathers in the field to the {dirto((x, y), *sp)}. A knight who does not come is no knight.', 25, 20,
                'crown', spot=list(sp), reach=1, where='the muster field', kid=kg.id)
    m.state = 'active'
    game.missions.append(m)
    game.reveal_place(*sp)
    kn['calls'] = kn.get('calls', 0) + 1
    game.msg(f'A rider brings word from your liege: {kg.short} calls its knights to {what}. (Journal: Jobs.)', 'gold')


def arrive_levy(game, m):
    return ('Tents, horses, banners. The enemy is camped across the stream, and tomorrow is the day.',
            [('Take your place in the line', 'fight')])


def do_levy(game, m, choice):
    x, y = m.data['spot']
    fight(game, m, ['soldier', 'soldier', 'crossbow', 'knight'], lvl_at(game, x, y, 3), 0, 'The trumpets sound. The lines close.')


def won_levy(game, m):
    favour(game, m.data.get('kid'), 8)
    for w_ in R(game).wars:
        if m.data['kid'] in (w_['a'], w_['b']):
            w_['score'] += 1 if w_['a'] == m.data['kid'] else -1
    turnin(game, m, 'The enemy breaks and runs. Your liege will want to thank you.')


SCENES['levy'] = (arrive_levy, do_levy, won_levy)


# ------------------------------------------------------------------ a beast for the yard (beastparts.py)
@task('catch', 'lord', 'A beast for the yard')
def make_catch(game, g):
    from . import realms as RL
    from . import named as NM
    lo = R(game).lord(g['lid'])
    if not lo:
        return None
    lx, ly = RL.place_of(game, lo)
    beasts = [n for n in NM.alive(game) if NM.kind_of(n.k) in ('beast', 'crawler') and n.rank != 'legendary'
              and n.did is None and n.boss is None and cheb(n.x, n.y, lx, ly) <= 70]
    if not beasts:
        return None
    n = min(beasts, key=lambda n: cheb(n.x, n.y, lx, ly))
    seat = R(game).houses[lo.house].seat
    ax, ay, _r = NM.area(game, n)
    return mission(game, g, 'catch', f'{n.Full}, alive',
                   f'{RL.style(R(game), lo, False)} wants {n.full}, the {D.MONSTERS[n.k]["name"].lower()} that '
                   f'{n.past}, brought in alive for {lo.his} yard. Wear it down, put it to sleep with a draught, and bind it '
                   f'with a rope. It was last seen to the {dirto((lx, ly), ax, ay)}.',
                   40 + n.lvl * 5, 30, None, spot=[ax, ay], reach=0, where='where it was seen', nid=n.id, nomark=False,
                   seat=list(seat) if seat else None)


def on_fail(game, m):
    """A levy not answered: the oath wears thin."""
    if m.kind == 'realm' and m.data.get('task') == 'levy':
        p = game.player
        kn = getattr(p, 'knight', None)
        if kn:
            favour(game, kn['kid'], -15)
            kn['missed'] = kn.get('missed', 0) + 1
            if kn['missed'] >= 2:
                p.knight = None
                game.msg('Your liege has struck your name from the roll of knights.', 'bad')


def register():
    from . import events as EV
    EV.RESOLVERS.update(realmjob=r_realmjob, realmoffer=r_realmoffer)
    from . import jobs as JB
    JB.LABEL['realm'] = 'Work for the realm'
    JB.KINDS.add('realm')
    JB.MAKE['realm'] = for_town
    JB.ARRIVE['realm'] = arrive
    JB.WON['realm'] = won
    for lst in (JB.VILLAGE, JB.TOWN, JB.CITY):
        lst.append('realm')


register()
