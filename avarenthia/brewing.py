"""Brewing: the craft of trade and company. Ten drinks, from ale to royal mead, each learnt from the people that makes
it (by tasting it, or from an innkeeper there). It needs the kettles and barrels of an inn or a monastery cellar.

A drink sells best far from where it was brewed. From rank 30 a batch also fills a barrel for your cart (trade goods).
A round for the company at a fire or a hearth cheers your hirelings; a drink of their own people is a welcome gift at
the inns of the halflings, dwarves, gnomes and elves. Strong spirits are the base of a tincture (alchemy.py), and warm
you and give you courage; too much spoils your aim."""
import random

from . import hunger as HU
from . import lifeskills as LS

# key: name, rank needed, ingredients {(kind, key): n}, result food key, how many, who makes it, strong
RECIPES = {
    'ale': ('Ale', 0, {('food', 'barley'): 2}, 'ale', 2, None, False),
    'wine': ('Berry Wine', 3, {('plant', 'blackberry'): 4}, 'wine', 1, None, False),
    'mead': ('Mead', 6, {('food', 'honey'): 1, ('food', 'barley'): 1}, 'mead', 2, None, False),
    'cider': ('Halfling Cider', 10, {('food', 'apple'): 3}, 'cider', 2, 'halfling', False),
    'stout': ('Dwarf Stout', 15, {('food', 'barley'): 3, ('plant', 'cave_mushroom'): 1}, 'stout', 2, 'dwarf', False),
    'cordial': ('Gnome Cordial', 20, {('plant', 'bilberry'): 2, ('food', 'honey'): 1}, 'cordial', 2, 'gnome', False),
    'elven_wine': ('Elven Wine', 25, {('plant', 'wild_strawberry'): 3, ('food', 'honey'): 1}, 'elven_wine', 1, 'elf', False),
    'juniper_spirits': ('Juniper Spirits', 30, {('plant', 'juniper'): 3, ('food', 'barley'): 1}, 'juniper_spirits', 1,
                        'north', True),
    'spiced_spirits': ('Spiced Spirits', 35, {('plant', 'wild_pepper'): 1, ('plant', 'vanilla'): 1, ('food', 'barley'): 2},
                       'spiced_spirits', 1, 'south', True),
    'royal_mead': ('Royal Mead', 45, {('food', 'honey'): 2, ('plant', 'saffron'): 1}, 'royal_mead', 1, None, False),
}
STARTER = ('ale', 'wine', 'mead')
BY_FOOD = {v[3]: k for k, v in RECIPES.items()}
TASTES = {
    'ale': 'You down the ale. Warm, bitter and good.', 'wine': 'Sweet, dark berry wine. Your cheeks glow.',
    'mead': 'Golden mead, thick with honey. You feel like singing.',
    'cider': 'Halfling cider, sharp and cloudy, tasting of a whole orchard.',
    'stout': 'Dwarf stout: black, bitter, and almost a meal.', 'cordial': 'Gnome cordial, sweet and fizzing on the tongue.',
    'elven_wine': 'Elven wine, pale and light, and it stays with you like a song.',
    'juniper_spirits': 'Juniper spirits burn all the way down. The cold cannot touch you now.',
    'spiced_spirits': 'Spiced spirits: pepper, vanilla and fire. You feel brave.',
    'royal_mead': 'Royal mead, dark gold and saffron. Barons drink this.',
}


def ing_name(kind, key):
    if kind == 'plant':
        from .foraging import PLANTS
        return PLANTS[key][0]
    return HU.FOODS[key][0]


def where_ok(game):
    m = game.map
    return m.kind == 'town' or getattr(m, 'site', None) is not None


def known(game):
    p = game.player
    if not hasattr(p, 'drinks'):
        p.drinks = set(STARTER)
    return p.drinks


def learn(game, key, how):
    if key in known(game):
        return False
    known(game).add(key)
    game.msg(how.format(name=RECIPES[key][0]), 'gold')
    return True


def recipes(game):
    """The drinks you know, with the rank they need: shown greyed out until you reach it."""
    r = LS.rank(game, 'brewing')
    if r >= 45:
        learn(game, 'royal_mead', 'After all these years you work it out yourself: {name}, with saffron.')
    return [(k, v) for k, v in RECIPES.items() if k in known(game) and (k not in STARTER or r >= v[1])]


def have(game, kind, key):
    return sum(i.n for i in game.player.inv if i.k == kind and i.t == key)


def can_brew(game, key):
    return LS.rank(game, 'brewing') >= RECIPES[key][1] and \
        all(have(game, kind, k) >= n for (kind, k), n in RECIPES[key][2].items())


def brew(game, key):
    name, rank, ing, res, n, _who, _strong = RECIPES[key]
    if not where_ok(game):
        game.msg('You need a kettle and barrels for that: brew at an inn or in a monastery cellar.', 'bad')
        return 0
    if LS.rank(game, 'brewing') < rank:
        LS.too_hard(game, 'brewing', rank, name)
        return 0
    if not can_brew(game, key):
        game.msg(f'For {name} you need ' + ', '.join(f'{c} {ing_name(kind, k)}' for (kind, k), c in ing.items()) + '.', 'bad')
        return 0
    p = game.player
    for (kind, k), c in ing.items():
        for _ in range(c):
            game.remove_one(next(i for i in p.inv if i.k == kind and i.t == k))
    r = LS.rank(game, 'brewing')
    if random.random() < max(.04, .25 - r * .03):
        game.msg(f'The batch turns sour. Your {name.lower()} is spoiled.', 'bad')
        LS.gain(game, 'brewing', 1, at=rank)
        return 20
    if r >= 10 and random.random() < .3:
        n += 1
    it = HU.make_food(game, res, n)
    it.origin = game.world_pos()
    game.add_to_inv(it) or game.spill(game.map, p.x, p.y, it)
    game.msg(f'You brew {n} {HU.FOODS[res][0].lower()}{"s" if n > 1 and res == "ale" else ""}.', 'good')
    if r >= 30:
        from . import economy as ECO
        from . import data as D
        if ECO.cargo_weight(p) + D.GOODS['ale']['w'] <= ECO.cargo_capacity(p):
            p.cargo['ale'] = p.cargo.get('ale', 0) + 1
            game.msg('You fill a barrel as well, for the cart: trade goods.', 'good')
    LS.gain(game, 'brewing', 2 + rank / 5, at=rank, what=key)
    return 20


# ------------------------------------------------------------------ drinking
def drink(game, it):
    """A drink: it heals a little and cheers you; you learn a drink by tasting it; strong spirits warm you and give
    courage; the third strong drink in a short while spoils your aim."""
    p = game.player
    key = BY_FOOD.get(it.t)
    game.remove_one(it)
    p.food = min(HU.MAX, p.food + HU.FOODS[it.t][1])
    game.heal(6 if it.t == 'ale' else 12, True)
    game.msg(TASTES.get(key, 'You drink it.'), 'good')
    if key and key not in known(game) and key != 'royal_mead':
        learn(game, key, 'You taste what is in it, and could brew it yourself one day: {name}.')
    strong = key and RECIPES[key][6]
    cups = [t for t in getattr(p, 'cups', []) if game.turn - t < 300] + [game.turn]
    p.cups = cups
    if strong:
        p.buffs = [b for b in p.buffs if b[0] not in ('warm', 'courage')] + \
            [['warm', 1, 400, 'Warm from the inside'], ['courage', 5, 120, 'Courage from the cup']]
    if len(cups) >= 3 or (strong and len(cups) >= 2):
        p.buffs = [b for b in p.buffs if b[0] != 'tipsy'] + [['tipsy', -25, 150, 'Tipsy']]
        game.msg('The world sways a little. Your aim will not be what it was for a while.', 'bad')
    return 1


def far_value(game, it, v):
    """A drink sells best far from where it was brewed (or from the people that makes it)."""
    o = getattr(it, 'origin', None)
    if o is None or game is None:
        return v
    from .worldgen import cheb
    x, y = game.world_pos()
    master = 1.2 if LS.rank(game, 'brewing') >= 40 else 1          # a master brewer's drinks sell better
    return round(v * master * (1 + min(1.0, cheb(x, y, o[0], o[1]) / 120)), 2)


# ------------------------------------------------------------------ inns, gifts and the company
def local(game, s):
    """The drink a settlement's inn knows: its people's own, or the north's juniper and the south's spices."""
    race = getattr(s, 'race', 'human')
    k = next((k for k, v in RECIPES.items() if v[5] == race), None)
    if k:
        return k
    from .weather import climate
    from .world import WORLD_H
    cl = climate(game.world, game.world.region_at(s.x, s.y).id)
    if cl == 'cold':
        return 'juniper_spirits'
    if cl in ('arid', 'hot', 'tropical') or s.y > WORLD_H * .7:
        return 'spiced_spirits'
    return None


def at_inn(game, s, keeper):
    """An innkeeper tells you how their drink is made; at the inns of the peoples, a drink of their own is a gift."""
    who = keeper.name if keeper is not None else 'The innkeeper'
    k = local(game, s)
    if k and k not in known(game) and ((s.id + game.seed) % 2 == 0 or getattr(s, 'rep', 0) >= 10):
        learn(game, k, f'{who} tells you how their {{name}} is brewed.')
    gift(game, s, keeper)
    label(game, s, who)
    from . import mastery as MA
    MA.rumour(game, who)


def label(game, s, who):
    """Brewing 50: your name on the label. The inn buys a few of your drinks, once a day, at a good price."""
    from .money import fmt
    p = game.player
    if LS.rank(game, 'brewing') < 50 or p.__dict__.get('label_day', {}).get(s.id) == game.day:
        return
    mine = [i for i in drinks_in_pack(game) if getattr(i, 'origin', None) is not None][:3]
    if not mine:
        return
    p.__dict__.setdefault('label_day', {})[s.id] = game.day
    total = 0
    for it in mine:
        total += round(it.value() * 1.5)                 # its worth, half again
        game.remove_one(it)
    p.gold += total
    game.msg(f'{who} knows your name on the label, and takes {len(mine)} of your drinks for the cellar: {fmt(total)}.', 'gold')


def gift(game, s, keeper):
    p = game.player
    race = getattr(s, 'race', 'human')
    k = next((k for k, v in RECIPES.items() if v[5] == race), None)
    given = p.__dict__.setdefault('drink_gifts', set())
    it = next((i for i in p.inv if k and i.k == 'food' and i.t == RECIPES[k][3]), None) if k else None
    if not it or s.id in given:
        return False
    given.add(s.id)
    game.remove_one(it)
    s.rep = getattr(s, 'rep', 0) + 5
    who = keeper.name if keeper is not None else 'The innkeeper'
    game.msg(f'You give {who} a {RECIPES[k][0].lower()} of their own people. It is taken with a broad smile: they will '
             f'remember you here.', 'gold')
    hidden = [q for q in game.world.pois if not q.found]
    if hidden:
        from .worldgen import cheb
        from .events import reveal
        q = min(hidden, key=lambda q: cheb(q.x, q.y, s.x, s.y))
        reveal(game, q)
        game.msg(f'Over the cup, {who} tells you of {q.name}.', 'info')
    return True


def drinks_in_pack(game):
    return [i for i in game.player.inv if i.k == 'food' and i.t in HU.DRINKS]


def round_ok(game):
    from . import mercs as MC
    company = MC.party(game)
    return bool(company) and sum(i.n for i in drinks_in_pack(game)) >= len(company)


def round_for_company(game):
    """A round for the company: a drink for each of your companions, and their spirits rise."""
    from . import mercs as MC
    company = MC.party(game)
    if not round_ok(game):
        return 0
    for mc in company:
        it = drinks_in_pack(game)[0]
        game.remove_one(it)
        mc.morale = min(100, getattr(mc, 'morale', 70) + 15)
    game.msg('You pour a round for the company. Cups are raised, a song is started, and spirits rise.', 'good')
    return 10
