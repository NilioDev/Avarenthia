"""Brewing: ale, wine and mead. A craft of its own (not alchemy): it needs the kettles and barrels of an
inn or a monastery cellar. Drinks feed you a little, cheer you up and sell well."""
import random

from . import hunger as HU
from . import lifeskills as LS

# key: name, rank needed, ingredients {(kind, key): n}, result food key, how many
RECIPES = {
    'ale': ('Ale', 0, {('food', 'barley'): 2}, 'ale', 2),
    'wine': ('Berry Wine', 3, {('plant', 'blackberry'): 4}, 'wine', 1),
    'mead': ('Mead', 6, {('food', 'honey'): 1, ('food', 'barley'): 1}, 'mead', 2),
}


def ing_name(kind, key):
    if kind == 'plant':
        from .foraging import PLANTS
        return PLANTS[key][0]
    return HU.FOODS[key][0]


def where_ok(game):
    m = game.map
    return m.kind == 'town' or getattr(m, 'site', None) is not None


def recipes(game):
    r = LS.rank(game, 'brewing')
    return [(k, v) for k, v in RECIPES.items() if r >= v[1]]


def have(game, kind, key):
    return sum(i.n for i in game.player.inv if i.k == kind and i.t == key)


def can_brew(game, key):
    return all(have(game, kind, k) >= n for (kind, k), n in RECIPES[key][2].items())


def brew(game, key):
    name, rank, ing, res, n = RECIPES[key]
    if not where_ok(game):
        game.msg('You need a kettle and barrels for that: brew at an inn or in a monastery cellar.', 'bad')
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
        LS.gain(game, 'brewing', 1)
        return 20
    if r >= 10 and random.random() < .3:
        n += 1
    game.add_to_inv(HU.make_food(game, res, n))
    game.msg(f'You brew {n} {HU.FOODS[res][0].lower()}{"s" if n > 1 and res == "ale" else ""}.', 'good')
    LS.gain(game, 'brewing', 2 + rank // 2)
    return 20
