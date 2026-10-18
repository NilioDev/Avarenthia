"""Cooking: no fixed recipes. You know Roast Meat and Grilled Fish; every other dish you find in the pot yourself,
hear from an innkeeper, a traveller or a people that trusts you, or read in a rare cookbook.

Walk into a fire (a camp fire, a fire pit, an inn's hearth): the dishes you know and have everything for, and at the
bottom Try something new: up to three things from your pack, one short choice at a time. A match teaches the dish;
one thing short gives a hint; nothing right gives Camp Mush. Rank never gives recipes: it means fewer burnt dishes,
more portions from one pot, stronger and longer effects, and at a high rank tasting what is in someone else's dish.

Each dish is one line in DISHES, so more are easy to add. Ingredients are items: plants (foraging.PLANTS, with
their own look per world until you know them), foods (hunger.FOODS: cuts of meat, eggs, milk...) and fish.
A dish item is Item('dish', key, n); a cookbook Item('cookbook', key)."""
import random

from . import data as D

# ------------------------------------------------------------------ ingredients
# the classes a dish may ask for, and the taste the hint names when it is missing
MEATS = {'meat', 'venison', 'boar_meat', 'hare_meat', 'grouse', 'elk_meat', 'reindeer_meat', 'ptarmigan', 'mutton',
         'ibex_meat', 'aurochs_meat', 'horse_meat', 'quail', 'gazelle_meat', 'wildebeest_meat', 'guinea_fowl',
         'bighorn_meat', 'duck', 'hog_meat', 'frog_legs'}
TASTE = {
    'wild_onion': 'sharp', 'wild_garlic': 'sharp', 'mustard_seed': 'sharp', 'wild_pepper': 'sharp', 'juniper': 'sharp',
    'honey': 'sweet', 'heather_honey': 'sweet', 'apple': 'sweet', 'dates': 'sweet', 'fig': 'sweet', 'mango': 'sweet',
    'wild_strawberry': 'sweet', 'vanilla': 'sweet', 'coconut': 'sweet', 'baobab': 'sweet', 'bilberry': 'sweet',
    'crowberry': 'sweet', 'blackberry': 'sweet', 'berries': 'sweet',
    'wild_thyme': 'green', 'yarrow': 'green', 'feverfew': 'green', 'moonpetal': 'green', 'kingsfoil': 'green',
    'spruce_tips': 'green', 'gentian': 'green', 'wild_sage': 'green', 'watercress': 'green', 'samphire': 'green',
    'seaweed': 'green', 'lichen': 'green',
    'salt': 'salty',
    'barley': 'filling', 'bread': 'filling', 'wild_millet': 'filling', 'hazelnut': 'filling', 'beechnut': 'filling',
    'pine_nut': 'filling', 'calamus': 'filling', 'wild_carrot': 'filling',
    'milk': 'creamy', 'goat_milk': 'creamy', 'butter': 'creamy', 'cheese': 'creamy', 'goat_cheese': 'creamy',
    'eggs': 'creamy',
    'chanterelle': 'earthy', 'cep': 'earthy', 'cave_mushroom': 'earthy',
    'ale': 'strong', 'wine': 'strong', 'mead': 'strong',
}
HINT = {'sharp': 'It wants something sharp.', 'sweet': 'It wants something sweet.', 'green': 'It wants something green.',
        'salty': 'It wants salt.', 'filling': 'It wants something to bind it.', 'creamy': 'It wants something creamy.',
        'earthy': 'It wants something earthy, from the forest floor.', 'strong': 'It wants a splash of something strong.',
        'meat': 'It wants meat.', 'fish': 'It wants fish.', 'other': 'It wants one thing more.'}
BERRIES = {'blackberry', 'bilberry', 'crowberry', 'wild_strawberry'}

# ------------------------------------------------------------------ the dishes
# key: name, tier, ingredients, where (lands or None), who (I innkeeper, T travellers, P people, S trying, B book),
#      effect, teller (for T: hunters, fishers, herders; for P: the people)
DISHES = {
    # simple: local dishes
    'roast_meat': ('Roast Meat', 'simple', ['meat'], None, '*', 'nostomach', None),
    'grilled_fish': ('Grilled Fish', 'simple', ['fish'], None, '*', None, None),
    'mushroom_skewer': ('Mushroom Skewer', 'simple', ['chanterelle'], 'forest', 'S', None, None),
    'barley_porridge': ('Barley Porridge', 'simple', ['barley', 'milk'], 'farm', 'IT', 'long', None),
    'berry_porridge': ('Berry Porridge', 'simple', ['barley', 'berries'], None, 'S', None, None),
    'baked_apples': ('Baked Apples', 'simple', ['apple', 'honey'], 'farm', 'I', None, None),
    'fish_soup': ('Fish Soup', 'simple', ['fish', 'wild_onion'], 'water', 'T', None, 'fishers'),
    'omelette': ('Omelette', 'simple', ['eggs', 'wild_onion'], 'farm', 'I', None, None),
    'cheese_toast': ('Cheese Toast', 'simple', ['bread', 'cheese'], None, 'I', None, None),
    'thyme_rabbit': ('Thyme Rabbit', 'simple', ['hare_meat', 'wild_thyme'], 'forest', 'T', None, 'hunters'),
    'birch_water': ('Birch Water', 'simple', ['birch_sap'], 'birch', 'I', 'heal_s', None),
    'elk_broth': ('Elk Broth', 'simple', ['elk_meat', 'spruce_tips'], 'taiga', 'I', 'warm', None),
    'reindeer_jerky': ('Reindeer Jerky', 'simple', ['reindeer_meat', 'salt'], 'tundra', 'T', 'keeps_long', 'herders'),
    'crowberry_mash': ('Crowberry Mash', 'simple', ['crowberry', 'lichen'], 'tundra', 'T', None, 'herders'),
    'heather_cake': ('Heather Honey Cake', 'simple', ['heather_honey', 'barley'], 'moor', 'I', None, None),
    'goat_curd': ('Goat Milk Curd', 'simple', ['goat_milk'], 'mountain', 'T', None, 'herders'),
    'garlic_bread': ('Wild Garlic Bread', 'simple', ['wild_garlic', 'bread'], 'mountain', 'I', 'hale', None),
    'steppe_kebab': ('Steppe Kebab', 'simple', ['aurochs_meat', 'wild_carrot'], 'steppe', 'T', None, 'herders'),
    'millet_cakes': ('Millet Cakes', 'simple', ['wild_millet', 'honey'], 'savanna', 'I', 'keeps', None),
    'date_porridge': ('Date Porridge', 'simple', ['dates', 'barley'], 'desert', 'I', None, None),
    'fig_paste': ('Fig Paste', 'simple', ['fig', 'honey'], 'desert', 'T', 'keeps', 'herders'),
    'sage_mutton': ('Sage Mutton', 'simple', ['bighorn_meat', 'wild_sage'], 'canyon', 'I', None, None),
    'eel_in_ale': ('Eel in Ale', 'simple', ['eel', 'ale'], 'marsh', 'I', None, None),
    'frog_legs': ('Fried Frog Legs', 'simple', ['frog_legs', 'watercress'], 'marsh', 'T', None, 'hunters'),
    'steamed_mussels': ('Steamed Mussels', 'simple', ['mussels', 'samphire'], 'coast', 'I', None, None),
    'crab_boil': ('Crab Boil', 'simple', ['crab', 'seaweed'], 'coast', 'T', None, 'fishers'),
    'coconut_fish': ('Coconut Fish', 'simple', ['fish', 'coconut'], 'coast', 'I', None, None),
    'mango_pork': ('Mango Pork', 'simple', ['hog_meat', 'mango'], 'jungle', 'I', None, None),
    'cave_fry': ('Cave Mushroom Fry', 'simple', ['cave_mushroom', 'salt'], 'karst', 'T', None, 'hunters'),
    # hearty: mostly by trying
    'hunters_stew': ("Hunter's Stew", 'hearty', ['meat', 'wild_onion', 'chanterelle'], None, 'S', 'muchfood warm', None),
    'forest_fry': ('Forest Fry', 'hearty', ['chanterelle', 'wild_onion', 'hazelnut'], None, 'S', 'muchfood', None),
    'venison_pie': ('Venison Pie', 'hearty', ['venison', 'bread', 'bilberry'], None, 'S', None, None),
    'boar_ribs': ('Boar Ribs', 'hearty', ['boar_meat', 'honey', 'salt'], None, 'S', None, None),
    'aurochs_steak': ('Aurochs Steak', 'hearty', ['aurochs_meat', 'salt', 'mustard_seed'], None, 'S', 'dmg', None),
    'herb_broth': ('Herb Broth', 'hearty', ['yarrow', 'wild_onion'], None, 'S', 'regen', None),
    'fever_tea': ('Fever Tea', 'hearty', ['feverfew', 'honey'], None, 'S', 'hale cure', None),
    'yarrow_tea': ('Yarrow Tea', 'hearty', ['yarrow', 'honey'], None, 'S', 'heal_s', None),
    'moon_soup': ('Moon Soup', 'hearty', ['moonpetal', 'fish'], None, 'S', 'mana', None),
    'trail_cakes': ('Trail Cakes', 'hearty', ['hazelnut', 'honey', 'barley'], None, 'S', 'keeps light', None),
    'shepherds_supper': ("Shepherd's Supper", 'hearty', ['goat_cheese', 'bread', 'wild_onion'], None, 'S', None, None),
    'desert_plate': ('Desert Plate', 'hearty', ['dates', 'goat_cheese', 'fig'], None, 'S', 'cool', None),
    'juniper_elk': ('Juniper Elk', 'hearty', ['elk_meat', 'juniper', 'salt'], None, 'S', 'warm_long', None),
    'grouse_heather': ('Grouse in Heather', 'hearty', ['grouse', 'heather_honey', 'wild_thyme'], None, 'S', None, None),
    'ibex_stew': ('Ibex Stew', 'hearty', ['ibex_meat', 'gentian', 'wild_garlic'], None, 'S', 'warm', None),
    'gazelle_skewers': ('Gazelle Skewers', 'hearty', ['gazelle_meat', 'wild_millet', 'baobab'], None, 'S', 'swift', None),
    'pepper_crab': ('Pepper Crab', 'hearty', ['crab', 'wild_pepper'], None, 'S', None, None),
    'pine_bread': ('Pine Nut Bread', 'hearty', ['pine_nut', 'barley', 'wild_sage'], None, 'S', 'keeps_long', None),
    'mulled_wine': ('Mulled Wine', 'hearty', ['wine', 'honey', 'apple'], None, 'S', 'warm', None),
    'nut_loaf': ('Nut Loaf', 'hearty', ['hazelnut', 'barley', 'butter'], None, 'P', None, 'halfling'),
    'second_breakfast': ('Second Breakfast', 'hearty', ['eggs', 'bread', 'cheese'], None, 'P', 'muchfood', 'halfling'),
    'deep_bread': ('Deep Bread', 'hearty', ['barley', 'cave_mushroom', 'salt'], None, 'P', 'keeps_long', 'dwarf'),
    'mead_stew': ('Mead Stew', 'hearty', ['meat', 'mead', 'wild_onion'], None, 'P', 'warm poisonres', 'dwarf'),
    'rootcake': ('Rootcake', 'hearty', ['calamus', 'hazelnut', 'honey'], None, 'P', None, 'gnome'),
    'starlight_broth': ('Starlight Broth', 'hearty', ['moonpetal', 'yarrow', 'wild_strawberry'], None, 'P', 'mana heal_m',
                        'elf'),
    # luxury: only by trying, or a rare book; they sell well in cities
    'kingsfoil_stew': ('Kingsfoil Stew', 'luxury', ['kingsfoil', 'meat', 'wild_onion'], None, 'SB', 'heal_l', None),
    'feast_hunt': ('Feast of the Hunt', 'luxury', ['meat', 'cep', 'wine'], None, 'SB', 'company', None),
    'oysters_wine': ('Oysters in Wine', 'luxury', ['oysters', 'wine', 'samphire'], None, 'SB', 'mana luck', None),
    'golden_supper': ('Golden Carp Supper', 'luxury', ['golden', 'butter', 'wild_thyme'], None, 'SB', 'allround', None),
    'vanilla_cream': ('Vanilla Cream', 'luxury', ['vanilla', 'goat_milk', 'honey'], None, 'SB', 'wages', None),
    'spiced_haunch': ('Spiced Haunch', 'luxury', ['venison', 'wild_pepper', 'juniper'], None, 'SB', 'dmg warm_long', None),
    'oasis_pilaf': ('Oasis Pilaf', 'luxury', ['wild_millet', 'dates', 'pine_nut'], None, 'SB', 'fed', None),
    'cep_omelette': ('Cep Omelette', 'luxury', ['eggs', 'cep', 'butter'], None, 'SB', 'regen mana', None),
    'wyrm_custard': ('Wyrm-egg Custard', 'luxury', ['drake_egg', 'milk', 'honey'], None, 'SB', 'fireres', None),
    'elder_nectar': ('Elder Tree Nectar', 'luxury', ['elder_sap', 'wild_strawberry', 'honey'], None, 'SB', 'heal_full',
                     None),
}
FOOD = {'simple': 300, 'hearty': 450, 'luxury': 520}
PRICE = {'simple': 30, 'hearty': 80, 'luxury': 450}          # in copper; a city cook pays half again
KNOWN_FROM_START = ('roast_meat', 'grilled_fish')
WORDS = {'nostomach': 'Cooked through: no stomach ache.', 'long': 'It stays with you a long time.',
         'heal_s': 'Heals a little.', 'heal_m': 'Heals.', 'heal_l': 'Heals a great deal.',
         'heal_full': 'Heals you fully, once a week.', 'warm': 'Warms you against the cold.',
         'warm_long': 'Warms you against the cold for a long while.', 'keeps': 'Keeps well.',
         'keeps_long': 'Keeps very long.', 'hale': 'You fall ill less often.', 'cure': 'Settles the stomach and cures poison.',
         'dmg': 'Strength: you hit harder for a while.', 'regen': 'Your wounds heal faster for a while.',
         'mana': 'Your mana comes back faster for a while.', 'cool': 'No heat exhaustion for a day.',
         'swift': 'Faster across the world map for a day.', 'fed': 'No hunger for two days.',
         'poisonres': 'Poison bites less.', 'fireres': 'Fire bites less for a day.',
         'company': 'For you, your hireling and your beast.', 'luck': 'Luck: better finds for a day.',
         'allround': 'Everything a little better for a day.', 'wages': "Your hireling's spirits rise: a week without wages.",
         'muchfood': 'Very filling.', 'light': 'Light to carry: a home-made travel ration.'}

# ------------------------------------------------------------------ where things come from
# the lands, as families of the world map's biomes
LANDS = {
    'forest': {'forest', 'deep_forest', 'dry_forest', 'conifer', 'clearing'}, 'birch': {'birch'},
    'taiga': {'taiga', 'conifer'}, 'tundra': {'tundra', 'tundra_hills', 'ice_shelf'}, 'moor': {'moor'},
    'mountain': {'alpine', 'hills', 'mountain', 'peak', 'karst'}, 'steppe': {'steppe', 'meadow', 'shrubland',
                                                                              'shrubland_cold'},
    'savanna': {'savanna'}, 'desert': {'desert', 'dune', 'dune_crest', 'bone_sand', 'oasis', 'salt', 'salt_edge'},
    'canyon': {'badlands', 'ravine', 'ravine_edge', 'crater_rim', 'mesa', 'canyon'}, 'marsh': {'marsh', 'floodplain', 'swamp'},
    'coast': {'beach', 'mangrove', 'cay', 'atoll_palm', 'surf', 'palms'}, 'jungle': {'jungle'},
    'karst': {'karst', 'shroom', 'sinkhole'},
    'water': {'river', 'lake', 'floodplain', 'marsh'}, 'farm': {'meadow', 'clearing', 'steppe', 'shrubland'},
}
# what grows and lives there: found by foraging, a few sold in its villages
LOCAL = {
    'forest': ['wild_thyme', 'beechnut', 'cep', 'oak_bark'], 'birch': ['birch_sap', 'wild_strawberry'],
    'taiga': ['juniper', 'spruce_tips'], 'tundra': ['crowberry', 'lichen'], 'moor': [('food', 'heather_honey'), 'bilberry'],
    'mountain': ['gentian', 'wild_garlic'], 'steppe': ['wild_carrot', 'mustard_seed'],
    'savanna': ['baobab', 'wild_millet'], 'desert': ['fig', 'cactus_fruit'], 'canyon': ['wild_sage', 'pine_nut'],
    'marsh': ['watercress', 'calamus', ('food', 'frog_legs')], 'coast': ['samphire', 'coconut', 'seaweed',
                                                                      ('food', 'crab'), ('food', 'mussels'),
                                                                      ('food', 'oysters')],
    'jungle': ['wild_pepper', 'vanilla', 'mango', ('food', 'parrot_eggs')], 'karst': ['cave_mushroom'],
}
SMALL_GAME = {'forest': ('hare', 'hare_meat'), 'birch': ('black_grouse', 'grouse'), 'taiga': ('snow_hare', 'hare_meat'),
              'tundra': ('ptarmigan', 'ptarmigan'), 'moor': ('black_grouse', 'grouse'), 'steppe': ('quail', 'quail'),
              'savanna': ('guinea_fowl', 'guinea_fowl'), 'desert': ('desert_hare', 'hare_meat'), 'marsh': ('duck', 'duck')}


def lands_of(biome):
    return [k for k, v in LANDS.items() if biome in v]


def here_biome(game):
    from . import seasons as SE
    om = game.maps['over']
    x, y = game.world_pos()
    return SE.biome(om, y * om.w + x) if om.inb(x, y) else ''


def here_lands(game):
    return lands_of(here_biome(game))


# ------------------------------------------------------------------ what you know
def known(game):
    p = game.player
    if not hasattr(p, 'dishes'):
        p.dishes = set(KNOWN_FROM_START)
    return p.dishes


def learn(game, key, how):
    if key in known(game):
        return False
    known(game).add(key)
    game.msg(how.format(name=DISHES[key][0]), 'gold')
    return True


def ing_name(spec):
    from . import foraging as FG
    from .hunger import FOODS
    from .lifeskills import FISH
    if spec == 'meat':
        return 'meat'
    if spec == 'fish':
        return 'fish'
    if spec == 'berries':
        return 'berries'
    if spec in FG.PLANTS:
        return FG.PLANTS[spec][0].lower()
    if spec in FOODS:
        return FOODS[spec][0].lower()
    if spec in FISH:
        return FISH[spec][0].lower()
    return spec.replace('_', ' ')


def key_of(it):
    """The ingredient an item is, or None."""
    if it.k in ('plant', 'food', 'fish'):
        return it.t
    return None


def fits(spec, key, it=None):
    from . import foraging as FG
    if spec == key:
        return True
    if spec == 'meat':
        return key in MEATS
    if spec == 'fish':
        return it is not None and it.k == 'fish' and key != 'legend'
    if spec == 'berries':
        return key in BERRIES
    return False


def match(specs, keys, items=None):
    """Can these ingredient keys fill exactly these specs, one each? (specific specs first)."""
    if len(specs) != len(keys):
        return False
    items = items or [None] * len(keys)
    order = sorted(range(len(specs)), key=lambda i: specs[i] in ('meat', 'fish', 'berries'))
    used = [False] * len(keys)

    def go(n):
        if n == len(order):
            return True
        sp = specs[order[n]]
        for j, k in enumerate(keys):
            if not used[j] and fits(sp, k, items[j]):
                used[j] = True
                if go(n + 1):
                    return True
                used[j] = False
        return False
    return go(0)


def cookable(game):
    """The dishes you know and have everything for: [(key, [items to use])]."""
    p = game.player
    out = []
    for key in sorted(known(game), key=lambda k: DISHES[k][0]):
        specs = DISHES[key][2]
        take, left = [], {i.id: i.n for i in p.inv}
        for sp in sorted(specs, key=lambda s: s in ('meat', 'fish', 'berries')):
            cands = [i for i in p.inv if key_of(i) and fits(sp, key_of(i), i) and left[i.id] > 0
                     and not (i.k == 'plant' and not _plant_known(game, i.t))]
            if not cands:
                take = None
                break
            it = min(cands, key=lambda i: i.value())
            left[it.id] -= 1
            take.append(it)
        if take:
            out.append((key, take))
    return out


def _plant_known(game, key):
    from . import foraging as FG
    return FG.known(game, key)


def pot_items(game):
    """What in your pack could go in the pot (one row per kind of thing)."""
    seen, out = set(), []
    for it in game.player.inv:
        k = key_of(it)
        if k and k != 'legend' and (it.k, it.t) not in seen:
            seen.add((it.k, it.t))
            out.append(it)
    return out


# ------------------------------------------------------------------ at the fire
def at_fire(game, where='camp'):
    """Walking into a fire: what you can cook."""
    from . import events as EV
    from . import lifeskills as LS
    opts = [(DISHES[k][0], f'cook:{k}') for k, _take in cookable(game)][:18]
    if pot_items(game):
        opts.append(('Try something new', 'try'))
    opts.append(('Leave the fire', 'leave'))
    text = {'camp': 'Your fire crackles. ', 'hearth': 'The hearth is warm and the pot is clean. ',
            'pit': 'Coals glow in the pit. '}.get(where, '')
    if len(opts) == 1:
        text += 'You have nothing to cook.'
    elif not cookable(game):
        text += 'You know nothing you have everything for. You could try something new.'
    else:
        text += 'What will you cook?'
    r = LS.rank(game, 'cooking')
    if r:
        text += f'\n\nCooking {r}.'
    EV.ask(game, 'cook', 'At the fire', text, opts, where=where)


def r_cook(game, choice, ctx):
    if choice == 'try':
        return ask_pick(game, [])
    if not choice or not choice.startswith('cook:'):
        return
    key = choice[5:]
    take = dict(cookable(game)).get(key)
    if not take:
        return
    for it in take:
        game.remove_one(it)
    serve(game, key, len(take))


def ask_pick(game, picks):
    from . import events as EV
    pid = {i for i in picks}
    items = [i for i in pot_items(game) if i.id not in pid or i.n > sum(1 for x in picks if x == i.id)]
    opts = [(i.display_name().split('x ', 1)[-1] if i.n > 1 else i.display_name(), f'add:{i.id}') for i in items][:20]
    if picks:
        opts.append(("That's all", 'done'))
    opts.append(('Never mind', 'leave'))
    have = ', '.join(_name_of(game, i) for i in picks)
    EV.ask(game, 'cook_pick', 'Something new', (f'In the pot: {have}.\n\n' if picks else '') +
           ('What goes in next?' if picks else 'What goes in the pot first?'), opts, picks=list(picks))


def _name_of(game, iid):
    it = next((i for i in game.player.inv if i.id == iid), None)
    if not it:
        return '?'
    n = it.display_name()
    return n.split('x ', 1)[-1] if it.n > 1 else n


def r_pick(game, choice, ctx):
    picks = list(ctx.get('picks', []))
    if choice == 'leave' or not choice:
        return
    if choice.startswith('add:'):
        picks.append(int(choice[4:]))
        if len(picks) < 3:
            return ask_pick(game, picks)
    attempt(game, picks)


def attempt(game, picks):
    """Into the pot with them: a dish you learn, a hint, or Camp Mush."""
    from . import lifeskills as LS
    p = game.player
    items = []
    for iid in picks:
        it = next((i for i in p.inv if i.id == iid), None)
        if it:
            items.append(it)
    if not items:
        return
    keys = [key_of(i) for i in items]
    hit = [k for k, v in DISHES.items() if match(v[2], keys, items)]
    hit.sort(key=lambda k: sum(s in ('meat', 'fish', 'berries') for s in DISHES[k][2]))
    for it in items:
        game.remove_one(it)
    game.end_turn(20)
    if hit:
        key = hit[0]
        new = key not in known(game)
        LS.gain(game, 'cooking', 4 if new else 1)
        if new:
            known(game).add(key)
            game.msg(f'You have made something good: {DISHES[key][0]}. You will remember how.', 'gold')
        serve(game, key, len(items), learned=new)
        return
    # one thing short of something?
    near = []
    for k, v in DISHES.items():
        specs = v[2]
        if len(specs) == len(keys) + 1:
            for j, sp in enumerate(specs):
                if match(specs[:j] + specs[j + 1:], keys, items):
                    near.append(sp)
                    break
    LS.gain(game, 'cooking', .5)
    mush(game)
    if near:
        sp = random.choice(near)
        taste = 'meat' if sp == 'meat' else 'fish' if sp == 'fish' else TASTE.get(sp, 'other')
        game.msg(f'Not bad. {HINT[taste]}', 'info')
    else:
        game.msg('Nothing about that worked. Camp Mush: it fills a hole.', 'info')


def mush(game):
    from .entities import Item
    it = Item(game.new_id(), 'dish', 'mush')
    game.add_to_inv(it) or game.spill(game.map, game.player.x, game.player.y, it)


def serve(game, key, n_ing, learned=False):
    """The dish comes out of the pot: burnt now and then, more portions with rank."""
    from . import lifeskills as LS
    from .entities import Item
    r = LS.rank(game, 'cooking')
    if not learned:
        game.end_turn(20)
    if random.random() < max(.02, .22 - r * .02):
        game.msg(f'You burn the {DISHES[key][0].lower()}. Black, bitter, and only half a meal.', 'bad')
        LS.gain(game, 'cooking', .5)
        mush(game)
        return
    portions = 1 + (1 if n_ing >= 2 else 0) + r // 10
    it = Item(game.new_id(), 'dish', key, portions)
    it.q = r                                        # how well it was made: stronger and longer effects
    keep = effects(key)
    if 'keeps_long' not in keep:
        it.until = game.day + (20 if 'keeps' in keep else 5)
    if not game.add_to_inv(it):
        game.spill(game.map, game.player.x, game.player.y, it)
    LS.gain(game, 'cooking', 1 + (DISHES[key][1] != 'simple'))
    if not learned:
        game.msg(f'You cook {portions} {"portion" if portions == 1 else "portions"} of {DISHES[key][0]}.', 'good')


def effects(key):
    if key == 'mush':
        return []
    return (DISHES[key][5] or '').split()


# ------------------------------------------------------------------ eating
def food_value(it):
    if it.t == 'mush':
        return 150
    v = FOOD[DISHES[it.t][1]]
    ef = effects(it.t)
    if 'muchfood' in ef:
        v += 250
    if 'long' in ef:
        v += 150
    return v


def eat(game, it):
    """A dish: food, and what it does."""
    from .hunger import MAX
    from . import mercs as MC
    from . import behave as BH
    p = game.player
    v = food_value(it)
    if p.food >= MAX - 30:
        game.msg('You are too full to eat another bite.')
        return 0
    key = it.t
    q = getattr(it, 'q', 0)
    game.remove_one(it)
    p.food = min(MAX, p.food + v)
    if key == 'mush':
        game.msg('Camp Mush. You have eaten worse. Not often.', 'info')
        return 1
    k = 1 + q * .03
    long_ = 1 + q * .04
    day = D.DAY_LEN

    def buff(kind, val, turns, label):
        p.buffs = [b for b in p.buffs if b[0] != kind] + [[kind, val, round(turns * long_), label]]
    said = []
    for ef in effects(key):
        if ef == 'heal_s':
            game.heal(round(12 * k), True)
        elif ef == 'heal_m':
            game.heal(round(30 * k), True)
        elif ef == 'heal_l':
            game.heal(round(80 * k), True)
        elif ef == 'heal_full':
            last = getattr(p, 'nectar_day', -99)
            if game.day - last >= 7:
                p.nectar_day = game.day
                p.life = game.stats()['max_life']
                said.append('Light runs through you. Every wound closes.')
            else:
                game.heal(round(20 * k), True)
        elif ef in ('warm', 'warm_long'):
            buff('warm', 1, day // 2 if ef == 'warm' else day, 'Warm from the inside')
        elif ef == 'hale':
            buff('hale', 1, day, 'Hale and hearty')
        elif ef == 'cure':
            p.poison = None
            BH.cure(game, ('diseased',))
        elif ef == 'dmg':
            buff('dmg', round(10 * k), day // 2, 'Strength of the aurochs')
        elif ef == 'regen':
            buff('regen', max(1, round(2 * k)), day // 2, 'Well fed')
        elif ef == 'mana':
            buff('mregen', max(1, round(2 * k)), day // 2, 'A clear head')
        elif ef == 'cool':
            buff('cool', 1, day, 'Cool in the heat')
        elif ef == 'swift':
            buff('swift', 1, day, 'Light on your feet')
        elif ef == 'fed':
            buff('fed', 1, day * 2, 'Full for days')
        elif ef == 'poisonres':
            buff('res_poison', round(25 * k), day // 2, 'Poison-proof belly')
        elif ef == 'fireres':
            buff('res_fire', round(30 * k), day, 'Fire in your belly')
        elif ef == 'luck':
            buff('luck', 1, day, 'Lucky')
        elif ef == 'allround':
            buff('dmg', round(5 * k), day, 'A golden supper')
            buff('def', round(5 * k), day, 'A golden supper ')
            buff('regen', 1, day, 'A golden supper  ')
        elif ef == 'company':
            buff('regen', max(1, round(2 * k)), day // 2, 'The feast of the hunt')
            for mc in MC.party(game):
                if mc.body is not None:
                    mc.body.hp = mc.body.maxhp
                mc.hp = getattr(mc, 'maxhp', getattr(mc, 'hp', 0))
                mc.morale = min(100, mc.morale + 10)
            if MC.party(game):
                said.append('Your company eats with you, and the night is merry.')
        elif ef == 'wages':
            mc = MC.get(game)
            if mc and mc.state == 'alive':
                mc.morale = min(100, mc.morale + 25)
                mc.free_days = 7
                said.append(f'{mc.name} grins from ear to ear. "For this, I work a week for nothing."')
    game.msg(f'You eat the {DISHES[key][0].lower()}. ' + (' '.join(said) if said else random.choice(
        ['Good, honest food.', 'That hits the spot.', 'You lick the spoon.'])), 'good')
    return 1


# ------------------------------------------------------------------ drying racks
def rack(game, x, y):
    """Walk into a drying rack: hang your meat and fish, or take down what has dried."""
    m, p = game.map, game.player
    racks = m.__dict__.setdefault('racks', {})
    hung = racks.get((x, y))
    if hung:
        ready, what, salted = hung
        if game.turn < ready:
            game.msg('It is still drying. Come back in the morning.')
            return 0
        from .hunger import make_food
        del racks[(x, y)]
        for key, n in what.items():
            it = make_food(game, key, n)
            if not salted:
                it.until = game.day + 20
            if not game.add_to_inv(it):
                game.spill(m, p.x, p.y, it)
        game.msg('You take down what has dried: ' + ', '.join(f"{n} {'Dried Meat' if k == 'jerky' else 'Smoked Fish'}"
                                                              for k, n in what.items()) + '.', 'good')
        return 1
    meat = [i for i in p.inv if (i.k == 'food' and i.t in MEATS and i.t != 'frog_legs') or i.k == 'fish' and i.t != 'legend']
    if not meat:
        game.msg('A drying rack. Hang meat or fish on it overnight and it keeps.')
        return 0
    what = {}
    for it in meat:
        k = 'jerky' if it.k == 'food' else 'smoked_fish'
        what[k] = what.get(k, 0) + it.n
        p.inv.remove(it)
    salt = next((i for i in p.inv if i.k == 'food' and i.t == 'salt'), None)
    if salt:
        game.remove_one(salt)
    racks[(x, y)] = (game.turn + D.DAY_LEN * 2 // 3, what, bool(salt))
    game.msg('You hang it on the rack' + (', rubbed with salt' if salt else '') + '. By morning it will be dry.', 'good')
    from . import lifeskills as LS
    LS.gain(game, 'cooking', 1)
    return 5


# ------------------------------------------------------------------ hearing it from others
def inn_dish(game, s):
    """The local dish an innkeeper shares: about one inn in five, and only a simple dish of its own land."""
    if (s.id * 7 + game.seed) % 5:
        return None
    om = game.maps['over']
    from . import seasons as SE
    lands = set()
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            if om.inb(s.x + dx, s.y + dy):
                lands.update(lands_of(SE.biome(om, (s.y + dy) * om.w + s.x + dx)))
    lands.add('farm')
    cands = sorted(k for k, v in DISHES.items() if 'I' in v[4] and v[1] == 'simple' and v[3] in lands)
    if not cands:
        return None
    return cands[(s.id + game.seed) % len(cands)]


def people_dish(game, s):
    """The peoples share their own plain dishes with friends."""
    race = getattr(s, 'race', 'human')
    if race not in ('halfling', 'dwarf', 'gnome', 'elf') or getattr(s, 'rep', 0) < 10:
        return None
    cands = sorted(k for k, v in DISHES.items() if v[4] == 'P' and v[6] == race and k not in known(game))
    return cands[0] if cands else None


def at_inn(game, s, keeper):
    """Talking to an innkeeper: now and then a recipe."""
    key = people_dish(game, s) or inn_dish(game, s)
    if not key or key in known(game):
        return False
    who = keeper.name if keeper is not None else 'The innkeeper'
    learn(game, key, f'{who} tells you how the {{name}} is made here: ' +
          ' with '.join([', '.join(ing_name(i) for i in DISHES[key][2][:-1]), ing_name(DISHES[key][2][-1])]
                        if len(DISHES[key][2]) > 1 else [ing_name(DISHES[key][2][0])]) + '.')
    return True


def taste(game, s):
    """A cook of high rank tastes what is in the inn's stew."""
    from . import lifeskills as LS
    if LS.rank(game, 'cooking') < 15:
        return
    key = inn_dish(game, s) or next((k for k, v in DISHES.items() if v[1] == 'hearty' and 'S' in v[4]
                                     and (s.id + len(k)) % 9 == 0 and k not in known(game)), None)
    if key and key not in known(game):
        learn(game, key, 'You taste what is in it, and you know: {name}.')


def from_traveller(game, wd):
    """Herders, hunters and fishers on the road share a simple dish now and then."""
    if random.random() > .15:
        return False
    lands = set(here_lands(game))
    cands = [k for k, v in DISHES.items() if 'T' in v[4] and (v[3] in lands or not lands) and k not in known(game)]
    if not cands:
        return False
    key = random.choice(cands)
    teller = DISHES[key][6] or 'travellers'
    learn(game, key, f'Talk turns to food. {wd.name.split()[0]}, who has eaten with {teller}, tells you how they make '
                     '{name}: ' + ' and '.join(ing_name(i) for i in DISHES[key][2]) + '.')
    return True


def from_herder(game):
    lands = set(here_lands(game))
    cands = [k for k, v in DISHES.items() if v[6] == 'herders' and (v[3] in lands) and k not in known(game)]
    if not cands or random.random() > .5:
        return False
    key = random.choice(cands)
    learn(game, key, 'The herder shows you how they make {name}: ' + ' and '.join(ing_name(i) for i in DISHES[key][2]) + '.')
    return True


# ------------------------------------------------------------------ cookbooks
def cookbook(game):
    """A very rare cookbook (a few per world): one luxury dish."""
    w = game.world
    left = w.__dict__.setdefault('cookbooks', 4)
    if left <= 0:
        return None
    w.cookbooks = left - 1
    from .entities import Item
    cands = [k for k, v in DISHES.items() if v[1] == 'luxury']
    it = Item(game.new_id(), 'cookbook', random.choice(cands))
    return it


def read_book(game, it):
    key = it.t
    game.player.inv.remove(it)
    if not learn(game, key, 'You read the old cookbook from cover to cover. You know how to make {name} now.'):
        game.msg('You knew that one already. The cook in the next city will pay something for the book, at least... '
                 'but you have already torn out the page.', 'info')
    return 5


# ------------------------------------------------------------------ the items
def display(game, it):
    if it.k == 'cookbook':
        return f'Cookbook: {DISHES[it.t][0]}'
    if it.t == 'mush':
        return (f'{it.n}x ' if it.n > 1 else '') + 'Camp Mush'
    return (f'{it.n}x ' if it.n > 1 else '') + DISHES[it.t][0]


def lines(game, it):
    if it.k == 'cookbook':
        return ['A stained, much-thumbed cookbook. One dish in it is worth the rest: read it to learn it.']
    if it.t == 'mush':
        return ['Edible. Just.']
    name, tier, ings, *_r = DISHES[it.t]
    out = [f'A {tier} dish of ' + ', '.join(ing_name(i) for i in ings) + '.']
    out += [WORDS[e] for e in effects(it.t) if e in WORDS]
    if tier == 'luxury':
        out.append('A city cook would pay well for this.')
    return out


def value(game, it):
    """In silver."""
    if it.k == 'cookbook':
        return 25
    if it.t == 'mush':
        return 0
    v = PRICE[DISHES[it.t][1]] / 100
    here = game.here if game is not None else None
    if here is not None and here.is_city and DISHES[it.t][1] == 'luxury':
        v *= 1.5
    return v


def glyph(it):
    return '≡' if it.k == 'cookbook' else '%'


def color(it):
    if it.k == 'cookbook':
        return (200, 160, 110)
    if it.t == 'mush':
        return (150, 140, 110)
    return {'simple': (230, 180, 120), 'hearty': (240, 150, 80), 'luxury': (255, 214, 92)}[DISHES[it.t][1]]


# ------------------------------------------------------------------ the land's own ingredients
def forage_local(game):
    """Foraging out in the land: now and then what only grows (or runs) here. True if something was found."""
    from . import foraging as FG
    from . import lifeskills as LS
    from .hunger import make_food
    lands = [l for l in here_lands(game) if l in LOCAL]
    small = [l for l in here_lands(game) if l in SMALL_GAME]
    r = LS.rank(game, 'foraging')
    luck = any(b[0] == 'luck' for b in game.player.buffs)
    if small and random.random() < .1 + LS.rank(game, 'hunting') * .01:
        kind, meat = SMALL_GAME[random.choice(small)]
        it = make_food(game, meat)
        if game.add_to_inv(it):
            LS.gain(game, 'hunting', 1)
            game.msg(f'You snare a {D.MONSTERS[kind]["name"].lower()}: {it.display_name()}.', 'good')
            return True
    if not lands or random.random() > .35 + (.15 if luck else 0):
        return False
    pick = random.choice(LOCAL[random.choice(lands)])
    n = random.randint(1, 2 + r // 6)
    if isinstance(pick, tuple):
        it = make_food(game, pick[1], n)
        name = it.display_name()
    else:
        it = FG.make_plant(game, pick, n)
        name = FG.plant_name(game, pick)
    if not game.add_to_inv(it):
        game.msg('Your pack is full.', 'bad')
        return True
    LS.gain(game, 'foraging', 1)
    if isinstance(pick, str) and not FG.known(game, pick) and random.random() < r * .05:
        FG.learn(game, pick, 'you recognise it from experience')
    game.msg(f'You find {name}.' if isinstance(pick, tuple) or FG.known(game, pick) else f'You find {name} ({n}).', 'good')
    return True


def shop_stock(game, s):
    """What a village outfitter has of the land's own: one local thing, and something from the farms."""
    from . import foraging as FG
    from .hunger import make_food
    om = game.maps['over']
    from . import seasons as SE
    lands = [l for l in lands_of(SE.biome(om, s.y * om.w + s.x)) if l in LOCAL]
    out = []
    if lands:
        pick = random.choice(LOCAL[random.choice(lands)])
        out.append(make_food(game, pick[1]) if isinstance(pick, tuple) else FG.make_plant(game, pick))
    farm = random.sample(['eggs', 'milk', 'butter', 'cheese', 'goat_milk', 'apple'], 2 if not s.is_city else 1)
    out += [make_food(game, k) for k in farm]
    return out


def register():
    from . import events as EV
    EV.RESOLVERS['cook'] = r_cook
    EV.RESOLVERS['cook_pick'] = r_pick


register()
