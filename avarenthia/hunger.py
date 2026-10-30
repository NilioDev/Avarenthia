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
    'cider': ('Jug of Halfling Cider', 100, 120, (230, 200, 110)),
    'stout': ('Mug of Dwarf Stout', 140, 160, (90, 60, 40)),
    'cordial': ('Flask of Gnome Cordial', 60, 220, (150, 110, 200)),
    'elven_wine': ('Bottle of Elven Wine', 80, 450, (230, 236, 190)),
    'juniper_spirits': ('Flask of Juniper Spirits', 30, 380, (200, 220, 230)),
    'spiced_spirits': ('Flask of Spiced Spirits', 30, 420, (220, 130, 60)),
    'royal_mead': ('Bottle of Royal Mead', 150, 900, (250, 200, 60)),
    'valley_cheese': ('Valley Goat Cheese', 600, 400, (250, 236, 180)),
    'goat_cheese': ('Goat Cheese', 350, 60, (246, 232, 190)),
    'dates': ('Dried Dates', 200, 15, (170, 100, 50)),
    # cuts of game, named by the animal (skinning, hunting.py)
    'venison': ('Venison', 200, 70, (176, 70, 60)), 'boar_meat': ('Boar Meat', 200, 60, (190, 96, 86)),
    'hare_meat': ('Hare Meat', 120, 35, (196, 110, 96)), 'grouse': ('Grouse', 110, 40, (150, 100, 80)),
    'elk_meat': ('Elk Meat', 220, 70, (160, 64, 56)), 'reindeer_meat': ('Reindeer Meat', 200, 70, (170, 72, 66)),
    'ptarmigan': ('Ptarmigan', 100, 40, (200, 160, 150)), 'mutton': ('Mutton', 190, 55, (200, 120, 110)),
    'ibex_meat': ('Ibex Meat', 190, 70, (170, 90, 80)), 'aurochs_meat': ('Aurochs Meat', 240, 80, (150, 50, 46)),
    'horse_meat': ('Horse Meat', 200, 50, (166, 76, 70)), 'quail': ('Quail', 80, 35, (190, 150, 120)),
    'gazelle_meat': ('Gazelle Meat', 180, 60, (186, 96, 80)), 'wildebeest_meat': ('Wildebeest Meat', 210, 55, (156, 70, 64)),
    'guinea_fowl': ('Guinea Fowl', 110, 40, (170, 140, 130)), 'bighorn_meat': ('Bighorn Meat', 190, 70, (176, 96, 84)),
    'duck': ('Wild Duck', 130, 45, (170, 120, 90)), 'hog_meat': ('Hog Meat', 200, 55, (190, 100, 90)),
    'frog_legs': ('Frog Legs', 60, 30, (170, 190, 130)),
    # from farms, shores and far places (cooking.py)
    'eggs': ('Eggs', 120, 30, (240, 230, 200)), 'milk': ('Jug of Milk', 90, 20, (244, 244, 236)),
    'butter': ('Pat of Butter', 100, 40, (250, 230, 140)), 'goat_milk': ("Jug of Goat's Milk", 90, 25, (240, 236, 220)),
    'salt': ('Bag of Salt', 0, 20, (236, 236, 240)), 'smoked_fish': ('Smoked Fish', 260, 120, (190, 130, 80)),
    'drake_egg': ('Drake Egg', 200, 2500, (220, 120, 70)), 'elder_sap': ('Sap of the Elder Tree', 60, 3000, (220, 240, 170)),
    'crab': ('Crab', 130, 60, (220, 110, 70)), 'mussels': ('Mussels', 90, 40, (90, 90, 120)),
    'oysters': ('Oysters', 80, 200, (200, 200, 190)), 'parrot_eggs': ('Parrot Eggs', 90, 60, (230, 220, 170)),
    'heather_honey': ('Heather Honey', 160, 110, (210, 150, 70)),
}
# raw meat that may upset your stomach (cook it: Roast Meat never does)
RAW = {'meat', 'venison', 'boar_meat', 'hare_meat', 'grouse', 'elk_meat', 'reindeer_meat', 'ptarmigan', 'mutton',
       'ibex_meat', 'aurochs_meat', 'horse_meat', 'quail', 'gazelle_meat', 'wildebeest_meat', 'guinea_fowl',
       'bighorn_meat', 'duck', 'hog_meat', 'frog_legs'}
DRINKS = {'ale', 'wine', 'mead', 'cider', 'stout', 'cordial', 'elven_wine', 'juniper_spirits', 'spiced_spirits',
          'royal_mead'}
BEASTS = {'wolf', 'jackal', 'bat', 'rat', 'spider', 'drake', 'troll', 'ogre'}
from .creatures import BEASTS as _NEW_BEASTS
BEASTS |= _NEW_BEASTS


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
    if any(b[0] == 'fed' for b in p.buffs):
        return                                       # a pilaf that keeps you going for days
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
    if it.k == 'dish':
        from . import cooking as CK
        return CK.food_value(it)
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
    if it.k == 'dish':
        from . import cooking as CK
        return CK.eat(game, it)
    if it.k == 'food' and it.t in DRINKS:
        from . import brewing as BR
        return BR.drink(game, it)
    game.remove_one(it)
    p.food = min(MAX, p.food + v)
    if it.k == 'fish':
        from .lifeskills import FISH
        game.heal(FISH[it.t][5], True)
    if it.k == 'food' and it.t in RAW and random.random() < .15:
        p.poison = [4, 1]
        game.msg(f'You eat the {FOODS[it.t][0].lower()} raw. Your stomach does not like it.', 'bad')
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
