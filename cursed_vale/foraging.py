"""Foraging and herbalism.

Foraging is finding food in the wild, by trial and error. Every world has its own look for each plant:
the red berries that fed you last time might be nightshade in the next world. Until you know a plant
you see only what it looks like; eat it to find out. Most are harmless, some feed you, a few will kill
you. The more you forage, the more often you recognise what you pick.

Herbalism is gathering herbs and knowing them. Alchemy is brewing them into potions (P), in the spirit of
World of Warcraft; the herbalist monks in the monasteries teach the basics. Brewing (ale, mead, wine) is a
craft of its own, done at the kettles of an inn or a monastery cellar."""
import random

from . import data as D

# key: name, group, food value, effect, rarity weight
PLANTS = {
    'blackberry': ('Blackberries', 'berry', 70, None, 10),
    'nightshade': ('Nightshade', 'berry', 0, 'deadly', 4),
    'rowanberry': ('Rowan Berries', 'berry', 30, 'sick', 6),
    'hazelnut': ('Hazelnuts', 'nut', 90, None, 7),
    'chanterelle': ('Chanterelles', 'mushroom', 100, None, 7),
    'fly_agaric': ('Fly Agaric', 'mushroom', 10, 'poison', 6),
    'deathcap': ('Deathcap', 'mushroom', 0, 'deadly', 4),
    'sleepcap': ('Sleepcap', 'mushroom', 20, 'sleep', 5),
    'wild_onion': ('Wild Onion', 'root', 60, None, 8),
    'bitterroot': ('Bitterroot', 'root', 40, 'sick', 6),
    'yarrow': ('Yarrow', 'herb', 15, 'heal', 9),
    'moonpetal': ('Moonpetal', 'herb', 10, 'mana', 6),
    'feverfew': ('Feverfew', 'herb', 10, 'cure', 6),
    'kingsfoil': ('Kingsfoil', 'herb', 20, 'heal2', 2),
}
LOOKS = {
    'berry': ['red berries', 'black berries', 'purple berries', 'orange berries', 'pale berries'],
    'nut': ['small brown nuts', 'hard green nuts'],
    'mushroom': ['a white mushroom', 'a speckled red mushroom', 'a pale brown mushroom', 'a grey mushroom', 'a yellow mushroom'],
    'root': ['a thick root', 'a knobbly white root', 'a red root'],
    'herb': ['a feathery herb', 'a blue flower', 'a silvery leaf', 'a yellow flower', 'a broad green leaf', 'a star-shaped flower'],
}
# where things grow: terrain -> groups and weights
WHERE = {
    D.FOREST: {'berry': 5, 'nut': 3, 'mushroom': 6, 'herb': 3, 'root': 1},
    D.GRASS: {'berry': 3, 'herb': 5, 'root': 3, 'mushroom': 1},
    D.HILLS: {'herb': 4, 'root': 3, 'berry': 2},
    D.SWAMP: {'herb': 4, 'mushroom': 4, 'root': 2, 'berry': 1},
    D.SAND: {'root': 2, 'herb': 1},
    D.TREE: {'berry': 5, 'nut': 3, 'mushroom': 6, 'herb': 3},
    D.FLOOR: {'mushroom': 1},
}
# alchemy recipes: key -> (name, rank needed, ingredients, result potion)
RECIPES = {
    'healing': ('Healing Draught', 0, {'yarrow': 2}, 'hp'),
    'mana': ('Mana Tonic', 0, {'moonpetal': 2}, 'mp'),
    'antidote': ('Antidote', 3, {'feverfew': 1, 'yarrow': 1}, 'cure'),
    'elixir': ('Kingsfoil Elixir', 8, {'kingsfoil': 1, 'yarrow': 1, 'moonpetal': 1}, 'rejuv'),
}


def setup_world(world):
    """Decide what each plant looks like in this world."""
    looks = {g: random.sample(v, len(v)) for g, v in LOOKS.items()}
    world.plant_look = {}
    for k, (_n, grp, *_rest) in PLANTS.items():
        pool = looks[grp]
        world.plant_look[k] = pool.pop() if pool else f'some {grp}'


def known(game, key):
    return key in game.player.known_plants


def plant_name(game, key, n=1):
    look = game.world.plant_look.get(key, 'a plant')
    if known(game, key):
        return PLANTS[key][0]
    return look


def learn(game, key, how=''):
    p = game.player
    if key in p.known_plants:
        return
    p.known_plants.add(key)
    game.msg(f'You now know {plant_name(game, key)} when you see it' + (f' ({how}).' if how else '.'), 'info')


def make_plant(game, key, n=1):
    from .entities import Item
    it = Item(game.new_id(), 'plant', key, n)
    it.name = PLANTS[key][0]
    return it


# ------------------------------------------------------------------ foraging
def forage(game):
    from . import lifeskills as LS
    m, p = game.map, game.player
    if m.kind in ('town', 'siege') or (m.kind == 'dungeon' and m.tile(p.x, p.y) != D.FLOOR):
        game.msg('There is nothing to forage here.')
        return 0
    if game.hostile_visible():
        game.msg('Not with enemies about!', 'bad')
        return 0
    t = m.tile(p.x, p.y)
    if m.kind == 'over' and t == D.ROAD:
        game.msg('The roadside has been picked clean. Try off the road.')
        return 0
    where = WHERE.get(t) or ({'mushroom': 1} if m.kind == 'dungeon' else None)
    if m.kind != 'over':
        near = [m.tile(p.x + dx, p.y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if m.inb(p.x + dx, p.y + dy)]
        if D.TREE in near:
            where = WHERE[D.TREE]
    if not where:
        game.msg('Nothing edible grows here.')
        return 0
    r = LS.rank(game, 'foraging')
    turns = (25 if m.kind == 'over' else 6) * (.7 if r >= 10 else 1)
    LS.gain(game, 'foraging', .6)
    if random.random() > .35 + r * .03 + (.1 if getattr(p, 'race', '') in ('elf', 'halfling', 'goblin') else 0):
        game.msg(random.choice(['You search the undergrowth, but find nothing worth taking.', 'Nothing but weeds and nettles.',
                                'You find a few berries, but the birds got there first.']))
        return round(turns)
    grp = random.choices(list(where), list(where.values()))[0]
    cands = [k for k, v in PLANTS.items() if v[1] == grp]
    rare = 3 if LS.rank(game, 'herbalism') >= 8 else 1
    key = random.choices(cands, [PLANTS[k][4] * (rare if PLANTS[k][4] <= 2 else 1) for k in cands])[0]
    n = random.randint(1, 2 + r // 6)
    it = make_plant(game, key, n)
    if not game.add_to_inv(it):
        game.msg('Your pack is full.', 'bad')
        return round(turns)
    LS.gain(game, 'foraging', 1)
    from .gods import on_craft
    on_craft(game, 'forage')
    hr = LS.rank(game, 'herbalism')
    if PLANTS[key][1] == 'herb':
        LS.gain(game, 'herbalism', 1.5)
        if hr >= 5:
            extra = random.randint(0, 1 + hr // 6)
            if extra:
                it.n += extra
                n += extra
    if not known(game, key) and (random.random() < r * .05 or (PLANTS[key][1] == 'herb' and random.random() < hr * .07)):
        learn(game, key, 'you recognise it from experience')
        if PLANTS[key][1] == 'herb':
            LS.gain(game, 'herbalism', 3)
    game.msg(f'You find {n} {plant_name(game, key)}.' if known(game, key) else f'You find {plant_name(game, key)} ({n}).', 'good')
    if not known(game, key) and PLANTS[key][3] in ('deadly', 'poison') and random.random() < r * .06:
        game.msg('Something about it makes you uneasy.', 'info')
    return round(turns)


def eat_plant(game, it):
    from . import lifeskills as LS
    from .hunger import MAX
    p = game.player
    key = it.t
    name, grp, food, effect, _w = PLANTS[key]
    was_known = known(game, key)
    game.remove_one(it)
    p.food = min(MAX, p.food + food)
    s = game.stats()
    if effect == 'deadly':
        dmg = 6 + p.lvl
        p.poison = [12, max(3, dmg // 2)]
        game.msg(f'You eat the {plant_name(game, key)}. Within minutes your stomach knots and your vision swims. Poison!', 'bad')
        game.shake()
    elif effect == 'poison':
        p.poison = [6, 2]
        game.msg('Your mouth goes numb and the world spins for a while. You will live. Probably.', 'bad')
    elif effect == 'sick':
        p.food = max(0, p.food - 120)
        game.msg('Bitter. You retch most of it back up.', 'bad')
    elif effect == 'sleep':
        game.msg('A heavy drowsiness comes over you. You sink down where you stand...', 'bad')
        game.end_turn(40, True)
        game.msg('You wake, groggy, some time later.', 'info')
    elif effect == 'heal':
        game.heal(12, True)
        game.msg('A clean, bitter taste. Your wounds ache a little less.', 'good')
    elif effect == 'heal2':
        game.heal(30, True)
        game.msg('Warmth spreads through you. Your wounds close a little.', 'good')
    elif effect == 'mana':
        p.mana = min(s['max_mana'], p.mana + 15)
        game.msg('A cool, silvery taste. Your mind clears.', 'good')
    elif effect == 'cure':
        p.poison = None
        game.msg('It tastes of camomile. Your stomach settles.', 'good')
    else:
        game.msg(f'You eat the {plant_name(game, key)}. Good, honest food.', 'good')
    if not was_known:
        LS.gain(game, 'foraging', 3)
        if grp == 'herb':
            LS.gain(game, 'herbalism', 2)
        learn(game, key, 'the hard way' if effect in ('deadly', 'poison', 'sick', 'sleep') else 'by tasting it')
    return 1


# ------------------------------------------------------------------ alchemy
def recipes(game):
    from . import lifeskills as LS
    r = LS.rank(game, 'alchemy')
    taught = game.player.recipes
    return [(k, v) for k, v in RECIPES.items() if k in taught or (k not in ('healing', 'mana') and r >= v[1] and taught)]


def can_brew(game, key):
    _n, rank, ing, _res = RECIPES[key]
    p = game.player
    for k, n in ing.items():
        have = sum(i.n for i in p.inv if i.k == 'plant' and i.t == k)
        if have < n or not known(game, k):
            return False
    return True


def brew(game, key):
    from . import lifeskills as LS
    from .entities import Item
    name, rank, ing, res = RECIPES[key]
    if not can_brew(game, key):
        game.msg(f'You lack the herbs for a {name}: ' + ', '.join(f'{n} {PLANTS[k][0]}' for k, n in ing.items()) + '.', 'bad')
        return 0
    p = game.player
    for k, n in ing.items():
        for _ in range(n):
            it = next(i for i in p.inv if i.k == 'plant' and i.t == k)
            game.remove_one(it)
    r = LS.rank(game, 'alchemy')
    if random.random() < max(.05, .3 - r * .03):
        game.msg(f'The brew curdles and turns black. Your {name} is ruined.', 'bad')
        LS.gain(game, 'alchemy', 1)
        return 10
    game.add_to_inv(Item(game.new_id(), 'potion', res))
    game.msg(f'You brew a {name}.', 'good')
    LS.gain(game, 'alchemy', 2 + rank // 2)
    return 10


def herbalist_talk(game, npc):
    p = game.player
    if not p.recipes:
        p.recipes.update({'healing', 'mana'})
        for k in ('yarrow', 'moonpetal'):
            p.known_plants.add(k)
        game.request = ('dialog', npc.name,
                        f'"A forager, are you? Then listen, before you poison yourself. This one, {game.world.plant_look["yarrow"]}, '
                        f'is yarrow: two of them steeped make a healing draught. And {game.world.plant_look["moonpetal"]}, '
                        'moonpetal, clears the mind; two make a mana tonic.\\n\\n'
                        'Never eat a mushroom you do not know. Never. Bring me what you find and I will tell you what it is."\\n\\n'
                        '(You learn two alchemy recipes. Press P to brew.)')
        from . import lifeskills as LS
        LS.gain(game, 'alchemy', 3)
        LS.gain(game, 'herbalism', 2)
        return
    unknown = sorted({i.t for i in p.inv if i.k == 'plant' and not known(game, i.t)})
    if unknown:
        lines = []
        for k in unknown:
            lines.append(f'{game.world.plant_look[k]}: {PLANTS[k][0]}' + {'deadly': ' (deadly! throw it away)', 'poison': ' (poisonous)',
                                                                          'sick': ' (makes you sick)', 'sleep': ' (puts you to sleep)'}.get(PLANTS[k][3], ''))
            p.known_plants.add(k)
        from . import lifeskills as LS
        LS.gain(game, 'herbalism', len(unknown))
        game.request = ('dialog', npc.name, '"Let me see what you have there... "\\n\\n' + '\\n'.join(lines))
        return
    game.say(npc, random.choice(['Yarrow for wounds, moonpetal for the mind, feverfew for the belly.',
                                 'The deathcap looks like any other mushroom. That is what makes it so good at killing.',
                                 'Come back when you have found something new.']))
