"""Hunger. You burn food every turn; eat bread, rations, fish or meat, or pay for a hot meal at an inn."""
import random

MAX = 1000
# key: name, food value, price in copper, glyph colour
FOODS = {
    'bread': ('Loaf of Bread', 300, 80, (220, 180, 110)),
    'ration': ('Travel Ration', 550, 250, (200, 160, 100)),
    'cheese': ('Wedge of Cheese', 250, 150, (240, 220, 120)),
    'apple': ('Apple', 110, 25, (220, 70, 60)),
    'meat': ('Raw Meat', 180, 60, (200, 90, 90)),
    'jerky': ('Dried Meat', 350, 180, (170, 100, 70)),
}
BEASTS = {'wolf', 'jackal', 'bat', 'rat', 'spider', 'drake', 'troll', 'ogre'}


def state(food):
    if food > 850:
        return 'Satiated'
    if food >= 300:
        return ''
    if food >= 120:
        return 'Hungry'
    if food >= 40:
        return 'Weak'
    return 'Fainting' if food > 0 else 'Starving'


def tick(game, turns=1):
    p = game.player
    before = state(p.food)
    p.food = max(0, p.food - turns)
    after = state(p.food)
    if after != before and after:
        msgs = {'Hungry': ('You are getting hungry.', 'info'), 'Weak': ('You are weak with hunger. Eat something!', 'bad'),
                'Fainting': ('You are fainting from hunger!', 'bad'), 'Starving': ('You are starving to death!', 'bad')}
        if after in msgs:
            game.msg(*msgs[after])
    if p.food == 0 and game.turn % 6 == 0:
        p.life -= 1
        if p.life <= 0:
            game.die('starvation')


def weak(game):
    return game.player.food < 120


def food_value(it):
    if it.k == 'plant':
        from . import foraging as FG
        name, grp, food, eff, _w = FG.PLANTS[it.t]
        return food if FG.known(FG.GAME, it.t) and eff in (None, 'heal', 'heal2', 'mana', 'cure') else 0
    if it.k == 'food':
        return FOODS[it.t][1]
    if it.k == 'fish':
        from .lifeskills import FISH
        return 80 + FISH[it.t][5] * 12
    return 0


def eat(game, it):
    p = game.player
    v = food_value(it)
    if not v:
        return 0
    if p.food >= MAX - 30:
        game.msg('You are too full to eat another bite.')
        return 0
    if it.k == 'plant':
        from . import foraging as FG
        return FG.eat_plant(game, it)
    game.remove_one(it)
    p.food = min(MAX, p.food + v)
    if it.k == 'fish':
        from .lifeskills import FISH
        game.heal(FISH[it.t][5], True)
    if it.k == 'food' and it.t == 'meat' and random.random() < .15:
        p.poison = [4, 1]
        game.msg('You eat the raw meat. Your stomach does not like it.', 'bad')
    else:
        game.msg(f'You eat the {it.display_name().split("x ", 1)[-1].lower()}. {state(p.food) or "You feel fine."}', 'good')
    return 1


def eat_best(game):
    """Eat the food that best fits your hunger."""
    p = game.player
    foods = [i for i in p.inv if food_value(i)]
    if not foods:
        game.msg('You have nothing to eat.', 'bad')
        return 0
    need = MAX - p.food
    fit = [i for i in foods if food_value(i) <= need]
    it = max(fit, key=food_value) if fit else min(foods, key=food_value)
    return eat(game, it)


def make_food(game, key, n=1):
    from .entities import Item
    it = Item(game.new_id(), 'food', key, n)
    it.name = FOODS[key][0]
    return it
