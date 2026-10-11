"""Crime and the law. Every town keeps its own memory of you. Rob people near it and your standing drops;
low enough and you are wanted there: notices go up on the boards, the local lord sends bounty hunters,
and the guards will want a word at the gate. Fines can be paid. Memories fade, slowly."""
import random

from . import data as D
from .money import fmt, purse
from .worldgen import cheb

WANTED_AT = -20      # standing at or below which a town wants you
BANNED_AT = -50      # standing at or below which the gates are shut
# how hard the law comes after you, by wanted level (1-5)
TIERS = {
    1: dict(name='The village watch of {town}', keys=['watchman', 'watchman', 'huntsman'], range=20, elite=0),
    2: dict(name='Sheriff {who} of {town} and deputies', keys=['sheriff', 'deputy', 'deputy', 'huntsman'], range=32, elite=0),
    3: dict(name="{lord}'s men-at-arms", keys=['soldier', 'soldier', 'crossbow', 'soldier', 'deputy'], range=50, elite=0),
    4: dict(name='Knights of {lord}', keys=['knight', 'knight', 'crossbow', 'crossbow', 'soldier'], range=80, elite=1),
    5: dict(name='An army of {lord}', keys=['knight', 'knight', 'soldier', 'soldier', 'soldier', 'crossbow', 'crossbow'],
            range=999, elite=1),
}


def heat(s):
    """Wanted level 0-5 in a town."""
    if s.rep > WANTED_AT:
        return 0
    return min(5, 1 + (WANTED_AT - s.rep) // 15)


def max_heat(game):
    return max((heat(s) for s in game.world.settlements), default=0)


def standing_word(rep):
    if rep <= BANNED_AT:
        return 'Outlaw'
    if rep <= WANTED_AT:
        return 'Wanted'
    if rep < 0:
        return 'Distrusted'
    if rep < 15:
        return 'Stranger'
    if rep < 40:
        return 'Known'
    if rep < 75:
        return 'Respected'
    return 'Hero'


def where(game):
    p = game.player
    return (p.x, p.y) if game.cur == 'over' else game.over_pos


def commit(game, severity, what, witnessed=1.0, near=None):
    """Record a crime. The nearest towns hear of it if anyone saw."""
    from .war import change_rep
    w = game.world
    x, y = near or where(game)
    if random.random() > witnessed:
        game.msg('Nobody saw you. This time.', 'info')
        return False
    towns = sorted(w.settlements, key=lambda s: cheb(s.x, s.y, x, y))[:2]
    for i, s in enumerate(towns):
        d = cheb(s.x, s.y, x, y)
        if d > 45:
            continue
        hit = severity if i == 0 else severity // 2
        before = s.rep
        s.rep = max(-100, s.rep - hit)
        s.crimes = getattr(s, 'crimes', [])[-4:] + [what]
        if s.rep <= WANTED_AT < before:
            game.msg(f'You are now WANTED in {s.name} for {what}.', 'bad')
        elif game.known_settlement(s):
            game.msg(f'Word of {what} will reach {s.name}. (standing {s.rep})', 'bad')
        if i == 0:
            change_rep(game, s.faction, -max(1, severity // 4), quiet=True)
    return True


def wanted_in(game):
    return [s for s in game.world.settlements if s.rep <= WANTED_AT]


def bounty(s):
    return max(500, -s.rep * 400)


def fine(s):
    return bounty(s)


def daily(game):
    w = game.world
    for s in w.settlements:
        if s.rep < 0 and game.day % 2 == 0:
            s.rep += 1                     # people forget, slowly
        h = heat(s)
        if h and random.random() < .15 + h * .1:
            groups = sum(1 for x in w.wanderers if x.kind == 'lawmen' and x.origin == s.id)
            if groups < (1 if h <= 3 else 2):
                spawn_lawmen(game, s)


def spawn_lawmen(game, s):
    from .wanderers import make_group, wanderer_at, passable
    w = game.world
    om = game.maps['over']
    p = game.player
    for _ in range(80):
        x, y = s.x + random.randint(-4, 4), s.y + random.randint(-4, 4)
        if om.inb(x, y) and passable(game, x, y, True) and not wanderer_at(game, x, y) and (x, y) != (p.x, p.y):
            break
    else:
        return None
    h = max(1, heat(s))
    t = TIERS[h]
    from .races import random_name
    lord = D.FACTIONS[s.faction]['name'] if s.faction != 'cult' else s.name
    keys = list(t['keys'])
    lvl = max(2, p.lvl - 2 + h)
    wd = make_group(game, 'bandits', x, y, lvl, keys, t['elite'], None)
    wd.kind = 'lawmen'
    wd.ch, wd.fg = ('@', (150, 180, 255)) if h < 4 else ('K', (190, 210, 255))
    wd.name = t['name'].format(town=s.name, who=random_name(s.race, 'other'), lord=lord)
    wd.origin = s.id
    wd.heat = h
    wd.range = t['range']
    wd.speed = 11 if h < 5 else 9
    if h >= 2:
        game.msg(f'News: {wd.name} {"ride" if h >= 4 else "set out"} to bring you in.', 'bad')
    wd.group['faction'] = None
    w.wanderers.append(wd)
    return wd


def stars(game):
    return max_heat(game)


def at_gate(game, s):
    """Called when you enter a town. Returns True if the guards stop you."""
    from .events import ask
    if s.rep > WANTED_AT:
        return False
    if getattr(s, 'stopped_day', -1) == game.day:
        return False
    s.stopped_day = game.day
    f = fine(s)
    what = (getattr(s, 'crimes', None) or ['your crimes'])[-1]
    opts = []
    if game.player.gold >= f:
        opts.append((f'Pay the fine of {fmt(f)}', 'pay'))
    opts += [('Spend three days in the stocks', 'stocks'), ('Turn and run', 'run')]
    ask(game, 'gate', f'The guards of {s.name}',
        f'Two guards block your way, hands on their swords. "You are wanted in {s.name} for {what}. '
        f'Pay your fine, or take your punishment."', opts, sid=s.id)
    return True


def r_gate(game, choice, ctx):
    s = game.world.settlements[ctx['sid']]
    p = game.player
    if choice == 'pay':
        p.gold -= fine(s)
        s.rep = -5
        s.crimes = []
        game.msg(f'You pay the fine. The guards step aside. Your slate in {s.name} is clean, if not spotless.', 'info')
    elif choice == 'stocks':
        s.rep = -8
        s.crimes = []
        lost = p.gold // 4
        p.gold -= lost
        game.end_turn(D.DAY_LEN * 3, True)
        game.msg(f'Three days in the stocks. Rotten fruit, jeers, and {fmt(lost)} "for your keep". Then they let you go.', 'bad')
    else:
        game.leave_to_over()
        game.msg('You slip away before they can grab you.', 'bad')
        spawn_lawmen(game, s)


# ------------------------------------------------------------------ robbery
def rob_traveller(game, wd):
    p = game.player
    w = game.world
    if 'knight' in wd.name and random.random() < .7:
        game.msg(f'{wd.name.split(" the ")[0]} draws a sword. "Try it, thief."', 'bad')
        wd.group = dict(keys=['knight'], lvl=max(3, p.lvl), elite=0, leader=None, faction=None)
        wd.hostile = True
        commit(game, 10, 'attacking a traveller', .6)
        game.start_encounter(wd)
        return
    g = purse(max(2, p.lvl), 3)
    p.gold += g
    game.msg(f'You take {fmt(g)} from {wd.name.split(" the ")[0]}, who flees down the road.', 'bad')
    if wd in w.wanderers:
        w.wanderers.remove(wd)
    commit(game, 15, 'robbery on the road', .7, (wd.x, wd.y))


def rob_caravan(game, wd):
    p = game.player
    s = game.world.settlements[wd.origin]
    lvl = max(3, game.world.danger_at(wd.x, wd.y) + 1)
    guards = random.randint(2, 4)
    wd.group = dict(keys=['merchant'] + ['mercenary'] * guards, lvl=lvl, elite=0, leader=None, faction=s.faction)
    wd.hostile = True
    wd.robbed = True
    commit(game, 30, 'robbing a caravan', 1.0, (wd.x, wd.y))
    game.start_encounter(wd)


def caravan_plundered(game, wd):
    """After a caravan robbery: its goods are yours, as far as you can carry them."""
    from .economy import free_cargo
    p = game.player
    if not wd.goods:
        return
    g, q = wd.goods
    room = free_cargo(p) // max(1, D.GOODS[g]['w'])
    took = min(q, room)
    if took:
        p.cargo[g] = p.cargo.get(g, 0) + took
        p.cost_basis.setdefault(g, 0)
    game.msg(f"You plunder the caravan: {took} {D.GOODS[g]['name']}" + (' (the rest you leave behind).' if took < q else '.'), 'gold')
