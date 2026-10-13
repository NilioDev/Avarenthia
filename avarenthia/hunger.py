"""Hunger. You burn food slowly; eat bread, rations, fish or meat, or pay for a hot meal at an inn.

A full belly lasts about a week: after a day or two you are hungry, after four or so weak (you heal no more
and hit softer), then you faint, and only after six or seven days without a bite do you start to starve."""
import random

MAX = 1000
RATE = .5            # food burned per turn: 150 a day
# key: name, food value, price in copper, glyph colour
FOODS = {
    'bread': ('Loaf of Bread', 300, 80, (220, 180, 110)),
    'ration': ('Travel Ration', 550, 250, (200, 160, 100)),
    'cheese': ('Wedge of Cheese', 250, 150, (240, 220, 120)),
    'apple': ('Apple', 110, 25, (220, 70, 60)),
    'meat': ('Raw Meat', 180, 60, (200, 90, 90)),
    'jerky': ('Dried Meat', 350, 180, (170, 100, 70)),
    'barley': ('Sack of Barley', 40, 30, (214, 190, 120)),
    'honey': ('Pot of Honey', 160, 90, (240, 190, 60)),
    'ale': ('Mug of Ale', 90, 70, (210, 150, 60)),
    'wine': ('Bottle of Berry Wine', 80, 260, (170, 50, 90)),
    'mead': ('Bottle of Mead', 120, 300, (240, 200, 90)),
    'valley_cheese': ('Valley Goat Cheese', 600, 400, (250, 236, 180)),
}
DRINKS = {'ale', 'wine', 'mead'}
BEASTS = {'wolf', 'jackal', 'bat', 'rat', 'spider', 'drake', 'troll', 'ogre'}


HUNGRY, WEAK, FAINT = 650, 300, 100


def state(food):
    if food > 850:
        return 'Satiated'
    if food >= HUNGRY:
        return ''
    if food >= WEAK:
        return 'Hungry'
    if food >= FAINT:
        return 'Weak'
    return 'Fainting' if food > 0 else 'Starving'


def tick(game, turns=1):
    p = game.player
    before = state(p.food)
    p.food_acc = getattr(p, 'food_acc', 0.0) + RATE * turns
    burn = int(p.food_acc)
    p.food_acc -= burn
    p.food = max(0, p.food - burn)
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
    return game.player.food < WEAK


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
    if it.k == 'food' and it.t in DRINKS:
        game.heal(6 if it.t == 'ale' else 12, True)
        game.msg({'ale': 'You down the ale. Warm, bitter and good.', 'wine': 'Sweet, dark berry wine. Your cheeks glow.',
                  'mead': 'Golden mead, thick with honey. You feel like singing.'}[it.t], 'good')
        return 1
    if it.k == 'food' and it.t == 'meat' and random.random() < .15:
        p.poison = [4, 1]
        game.msg('You eat the raw meat. Your stomach does not like it.', 'bad')
    else:
        game.msg(f'You eat the {it.display_name().split("x ", 1)[-1].lower()}. {state(p.food) or "You feel fine."}', 'good')
    return 1


def has_food(game):
    return any(food_value(i) for i in game.player.inv)


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
