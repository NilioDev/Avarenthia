"""Foraging, with the herbs of alchemy in it (Herbalism was its own skill once; it joined Foraging).

Foraging is finding food in the wild, by trial and error. Every world has its own look for each plant:
the red berries that fed you last time might be nightshade in the next world. Until you know a plant
you see only what it looks like; eat it to find out. Most are harmless, some feed you, a few will kill
you. The more you forage, the more often you recognise what you pick.

The herbs (HERBS) each have a tier and two properties, and grow in their own land; the better ones lie where the land
is more dangerous, and above your rank they are "too hard for you yet". Tasting a herb teaches its first property,
Foraging 15 shows the second when you pick it, a brew that works teaches both. Alchemy (alchemy.py) brews what two or
three herbs share. Brewing (ale, cider, wine, mead, spirits) is a craft of its own, at the kettles of an inn."""
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
    'everbloom': ('Everbloom', 'herb', 10, 'heal2', 0),          # grows only in the Unwintering
    # what grows in one land only (cooking.LOCAL): never found by plain foraging, only where it grows
    'wild_thyme': ('Wild Thyme', 'herb', 10, None, 0), 'beechnut': ('Beechnuts', 'nut', 60, None, 0),
    'cep': ('Ceps', 'mushroom', 110, None, 0), 'oak_bark': ('Oak Bark', 'bark', 0, None, 0),
    'birch_sap': ('Birch Sap', 'sap', 40, None, 0), 'wild_strawberry': ('Wild Strawberries', 'berry', 60, None, 0),
    'juniper': ('Juniper Berries', 'berry', 20, None, 0), 'spruce_tips': ('Spruce Tips', 'herb', 10, None, 0),
    'crowberry': ('Crowberries', 'berry', 50, None, 0), 'lichen': ('Reindeer Lichen', 'herb', 20, None, 0),
    'bilberry': ('Bilberries', 'berry', 60, None, 0), 'gentian': ('Gentian', 'herb', 5, None, 0),
    'wild_garlic': ('Wild Garlic', 'root', 40, None, 0), 'wild_carrot': ('Wild Carrot', 'root', 70, None, 0),
    'mustard_seed': ('Mustard Seed', 'seed', 10, None, 0), 'baobab': ('Baobab Fruit', 'fruit', 90, None, 0),
    'wild_millet': ('Wild Millet', 'seed', 60, None, 0), 'fig': ('Figs', 'fruit', 90, None, 0),
    'cactus_fruit': ('Cactus Fruit', 'fruit', 70, None, 0), 'wild_sage': ('Wild Sage', 'herb', 10, None, 0),
    'pine_nut': ('Pine Nuts', 'nut', 80, None, 0), 'watercress': ('Watercress', 'herb', 30, None, 0),
    'calamus': ('Calamus Root', 'root', 50, None, 0), 'samphire': ('Samphire', 'herb', 30, None, 0),
    'coconut': ('Coconut', 'fruit', 120, None, 0), 'seaweed': ('Seaweed', 'herb', 30, None, 0),
    'wild_pepper': ('Wild Pepper', 'seed', 5, None, 0), 'vanilla': ('Vanilla Pods', 'seed', 5, None, 0),
    'mango': ('Mango', 'fruit', 100, None, 0), 'cave_mushroom': ('Cave Mushrooms', 'mushroom', 70, None, 0),
}
# the herbs of alchemy that plain foraging never finds: each lives where HERBS says (rarity 0)
for _k, _n, _g, _f in [
        ('nettle', 'Nettle', 'herb', 20), ('plantain', 'Plantain', 'herb', 10), ('chamomile', 'Chamomile', 'herb', 5),
        ('elderflower', 'Elderflower', 'herb', 10), ('dandelion', 'Dandelion', 'herb', 20), ('mint', 'Mint', 'herb', 5),
        ('bloodmoss', 'Bloodmoss', 'herb', 5), ('wolfsbane', 'Wolfsbane', 'herb', 0), ('saltwort', 'Saltwort', 'herb', 10),
        ('comfrey', 'Comfrey', 'herb', 10), ('valerian', 'Valerian', 'root', 10), ('st_johns_wort', "St John's Wort", 'herb', 5),
        ('willow_bark', 'Willow Bark', 'bark', 0), ('mugwort', 'Mugwort', 'herb', 5), ('sundew', 'Sundew', 'herb', 0),
        ('ghostcap', 'Ghostcap', 'mushroom', 5), ('emberleaf', 'Emberleaf', 'herb', 0), ('frostbloom', 'Frostbloom', 'herb', 5),
        ('silverreed', 'Silverreed', 'herb', 5), ('arnica', 'Arnica', 'herb', 5), ('edelweiss', 'Edelweiss', 'herb', 5),
        ('mandrake', 'Mandrake', 'root', 0), ('aloe', 'Aloe', 'herb', 10), ('dragons_tongue', "Dragon's Tongue", 'herb', 0),
        ('duskthorn', 'Duskthorn', 'herb', 0), ('deeproot', 'Deeproot', 'root', 20), ('mountain_heart', 'Mountain Heart', 'herb', 10),
        ('hemlock', 'Hemlock', 'herb', 0), ('myrrh', 'Myrrh', 'resin', 0), ('lotus', 'Lotus', 'herb', 10),
        ('vervain', 'Vervain', 'herb', 5), ('witchbloom', 'Witchbloom', 'herb', 0), ('sunpetal', 'Sunpetal', 'herb', 10),
        ('elder_moss', 'Elder Moss', 'herb', 10), ('frankincense', 'Frankincense', 'resin', 0),
        ('hellebore', 'Black Hellebore', 'herb', 0), ('saffron', 'Saffron Crocus', 'herb', 10), ('starmoss', 'Starmoss', 'herb', 10)]:
    PLANTS[_k] = (_n, _g, _f, None, 0)
PLANTS['hemlock'] = ('Hemlock', 'herb', 0, 'deadly', 0)
PLANTS['wolfsbane'] = ('Wolfsbane', 'herb', 0, 'poison', 0)
PLANTS['hellebore'] = ('Black Hellebore', 'herb', 0, 'poison', 0)
PLANTS['duskthorn'] = ('Duskthorn', 'herb', 0, 'poison', 0)
PLANTS['mandrake'] = ('Mandrake', 'root', 0, 'sleep', 0)
PLANTS['valerian'] = ('Valerian', 'root', 10, 'sleep', 0)

# the 17 properties of alchemy
PROPS = ['Heal', 'Mana', 'Stamina', 'Regen', 'Cure', 'Staunch', 'Ward Fire', 'Ward Cold', 'Ward Poison', 'Sight', 'Calm',
         'Swift', 'Strength', 'Sleep', 'Venom', 'Flame', 'Silver']
# herb: tier, its two properties, where it grows (lands, biomes, or: any, cave, deep, night, winter, cursed, wonder)
HERBS = {
    # A: around your first villages
    'yarrow': ('A', ('Heal', 'Staunch'), 'any'), 'moonpetal': ('A', ('Mana', 'Sleep'), 'any'),
    'feverfew': ('A', ('Cure', 'Regen'), 'any'), 'sleepcap': ('A', ('Sleep', 'Mana'), 'forest birch taiga'),
    'nettle': ('A', ('Stamina', 'Regen'), 'any'), 'plantain': ('A', ('Staunch', 'Cure'), 'farm steppe moor'),
    'chamomile': ('A', ('Calm', 'Regen'), 'farm steppe'), 'wild_thyme': ('A', ('Ward Cold', 'Cure'), 'forest canyon'),
    'wild_sage': ('A', ('Mana', 'Sight'), 'canyon steppe'), 'wild_garlic': ('A', ('Ward Poison', 'Stamina'), 'mountain forest'),
    'elderflower': ('A', ('Ward Cold', 'Heal'), 'forest farm birch'), 'dandelion': ('A', ('Heal', 'Stamina'), 'farm steppe'),
    'mint': ('A', ('Swift', 'Calm'), 'water marsh'), 'fly_agaric': ('A', ('Venom', 'Sight'), 'forest birch taiga'),
    # B: further from the road, the first rough country
    'kingsfoil': ('B', ('Heal', 'Regen'), 'forest'), 'bloodmoss': ('B', ('Staunch', 'Regen'), 'marsh'),
    'wolfsbane': ('B', ('Venom', 'Silver'), 'mountain taiga tundra'), 'saltwort': ('B', ('Ward Fire', 'Staunch'), 'coast desert'),
    'comfrey': ('B', ('Heal', 'Strength'), 'water farm'), 'valerian': ('B', ('Sleep', 'Calm'), 'marsh water farm'),
    'st_johns_wort': ('B', ('Sight', 'Cure'), 'steppe forest'), 'juniper': ('B', ('Ward Poison', 'Ward Cold'), 'taiga moor'),
    'gentian': ('B', ('Cure', 'Stamina'), 'mountain'), 'willow_bark': ('B', ('Regen', 'Calm'), 'water'),
    'mugwort': ('B', ('Sight', 'Swift'), 'steppe moor'), 'sundew': ('B', ('Staunch', 'Sight'), 'moor marsh'),
    # C: the wild
    'ghostcap': ('C', ('Sight', 'Sleep'), 'deep_forest night'), 'emberleaf': ('C', ('Flame', 'Ward Cold'), 'canyon'),
    'frostbloom': ('C', ('Ward Fire', 'Mana'), 'mountain winter'), 'silverreed': ('C', ('Silver', 'Mana'), 'water'),
    'arnica': ('C', ('Heal', 'Stamina'), 'mountain'), 'edelweiss': ('C', ('Ward Cold', 'Regen'), 'alpine peak'),
    'nightshade': ('C', ('Venom', 'Sight'), 'forest jungle'), 'mandrake': ('C', ('Sleep', 'Strength'), 'moor steppe night'),
    'aloe': ('C', ('Ward Fire', 'Heal'), 'desert savanna'),
    # D: far country, deep dungeons
    'dragons_tongue': ('D', ('Ward Fire', 'Flame'), 'canyon mountain'), 'duskthorn': ('D', ('Venom', 'Swift'), 'mangrove jungle'),
    'deeproot': ('D', ('Stamina', 'Strength'), 'deep'), 'mountain_heart': ('D', ('Regen', 'Stamina'), 'peak alpine'),
    'hemlock': ('D', ('Venom', 'Sleep'), 'floodplain marsh'), 'myrrh': ('D', ('Heal', 'Ward Poison'), 'desert'),
    'lotus': ('D', ('Mana', 'Calm'), 'oasis jungle'), 'vervain': ('D', ('Silver', 'Sight'), 'moor steppe'),
    # E: the worst land
    'witchbloom': ('E', ('Strength', 'Regen'), 'cursed'), 'sunpetal': ('E', ('Ward Fire', 'Heal'), 'oasis desert'),
    'elder_moss': ('E', ('Mana', 'Regen'), 'deep_forest'), 'frankincense': ('E', ('Silver', 'Heal'), 'desert'),
    'hellebore': ('E', ('Venom', 'Strength'), 'cursed marsh'), 'saffron': ('E', ('Swift', 'Mana'), 'mesa canyon'),
    # the top: the crafts' own rares
    'starmoss': ('T', ('Star', 'Star'), 'wonder'), 'everbloom': ('T', ('Heal', 'Regen'), 'never'),
}
TIER_VALUE = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'T': 5}
TIER_WEIGHT = {'A': 10, 'B': 6, 'C': 4, 'D': 3, 'E': 2, 'T': .6}
ALCHEMY = set(HERBS)
LOOKS = {
    'berry': ['red berries', 'black berries', 'purple berries', 'orange berries', 'pale berries', 'blue berries',
              'dark red berries', 'tiny red berries', 'glossy black berries'],
    'nut': ['small brown nuts', 'hard green nuts', 'tiny three-sided nuts', 'pale seeds from a cone'],
    'mushroom': ['a white mushroom', 'a speckled red mushroom', 'a pale brown mushroom', 'a grey mushroom', 'a yellow mushroom',
                 'a fat brown-capped mushroom', 'a pale mushroom from the dark', 'a frilled orange mushroom'],
    'root': ['a thick root', 'a knobbly white root', 'a red root', 'a bulb with broad leaves', 'a thin orange root',
             'a fragrant reed root', 'a forked man-shaped root', 'a gnarled black root'],
    'herb': ['a feathery herb', 'a blue flower', 'a silvery leaf', 'a yellow flower', 'a broad green leaf', 'a star-shaped flower',
             'a tiny grey-leaved herb', 'soft green shoots', 'a crust of pale growth', 'a cluster of purple bells',
             'a spiky blue-grey herb', 'round peppery leaves', 'a fleshy green stalk', 'a ribbon of dark green weed',
             'a stinging leaf', 'a ribbed broad leaf', 'a white daisy', 'a flat white umbel', 'a yellow clock flower',
             'a fragrant square stem', 'a red-tipped moss', 'a hooded purple flower', 'a grey salty stalk',
             'a hairy broad leaf', 'a star of golden petals', 'a silver-grey bush', 'a sticky red rosette',
             'a pale glowing cap', 'a leaf with glowing red veins', 'a white frost-rimmed flower', 'a silvery reed',
             'a yellow mountain daisy', 'a woolly white star', 'a thick spiked leaf', 'a forked red tongue of a leaf',
             'a black thorny sprig', 'a red-hearted mountain herb', 'a spotted hollow stalk', 'a floating white flower',
             'a thin blue spike', 'a black-petalled bloom', 'a golden sun-shaped flower', 'a beard of ancient moss',
             'a dark green bloom', 'a purple crocus with red threads', 'a moss that glitters like stars', 'a pale blue bell',
             'a fern with curled tips', 'a bitter grey herb'],
    'fruit': ['a hard-shelled fruit', 'a soft purple fruit', 'a spiny red fruit', 'a heavy brown fruit', 'a sweet yellow fruit',
              'a green-skinned fruit'],
    'seed': ['tiny yellow seeds', 'a head of wild grain', 'small hot red pods', 'long dark pods', 'a pinch of black seeds'],
    'sap': ['a pale sap', 'a sweet clear sap'],
    'bark': ['rough grey bark', 'dark furrowed bark', 'a strip of pale bark'],
    'resin': ['a lump of golden resin', 'tears of pale resin'],
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


def on_walk(game):
    """Foraging 50: walking the wild, a herb you know catches your eye and you pick it in passing."""
    from . import lifeskills as LS
    if LS.rank(game, 'foraging') < 50 or random.random() > .02 or game.map.tile(game.player.x, game.player.y) == D.ROAD:
        return
    k = draw_herb(game)
    if k and k != 'hard' and known(game, k):
        it = make_plant(game, k, 1)
        if game.add_to_inv(it):
            game.msg(f'By the way a {plant_name(game, k)} catches your eye. You pick it in passing.', 'good')


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
    boost = 1
    if m.kind == 'over':
        from .lands import forage as land_forage
        where, boost = land_forage(game, where)      # the old forest and the mountain meadows: rare herbs
    r = LS.rank(game, 'foraging')
    turns = (25 if m.kind == 'over' else 6) * (.7 if r >= 10 else 1)
    LS.gain(game, 'foraging', .6)
    luck = .1 if any(b[0] == 'luck' for b in p.buffs) else 0
    if random.random() > .35 + r * .03 + luck + (.1 if getattr(p, 'race', '') in ('elf', 'halfling', 'goblin') else 0):
        game.msg(random.choice(['You search the undergrowth, but find nothing worth taking.', 'Nothing but weeds and nettles.',
                                'You find a few berries, but the birds got there first.']))
        return round(turns)
    if m.kind in ('over', 'wild'):
        from . import cooking as CK
        from . import crafts as CRF
        if CRF.fey_silk(game):
            return round(turns)
        if 'marsh' in CK.here_lands(game) and any(i.k == 'tool' and i.t == 'pick' for i in p.inv) \
                and random.random() < .15 and LS.tier_open(game, 'B'):
            if LS.rank(game, 'mining') >= CRF.METALS['bog'][2]:
                CRF.give(game, 'ore_bog', 1)
                game.msg('Under the turf your pick strikes a crust of rusty bog iron. You cut it out.', 'good')
                LS.gain(game, 'mining', 1, at=CRF.METALS['bog'][2], what='bog')
                return round(turns)
        if CK.forage_local(game):
            return round(turns)
    grp = random.choices(list(where), list(where.values()))[0]
    key = None
    if grp == 'herb' or random.random() < .25:
        key = draw_herb(game, boost)
        if key == 'hard':
            return round(turns)
    if key is None:
        cands = [k for k, v in PLANTS.items() if v[1] == grp and k not in HERBS or k in ('fly_agaric', 'sleepcap', 'nightshade')
                 and v[1] == grp and HERBS[k][0] == 'A']
        if not cands:
            cands = [k for k, v in PLANTS.items() if v[1] == grp and v[4]]
        key = random.choices(cands, [PLANTS[k][4] for k in cands])[0]
    n = random.randint(1, 2 + r // 6)
    it = make_plant(game, key, n)
    if not game.add_to_inv(it):
        game.msg('Your pack is full.', 'bad')
        return round(turns)
    at = LS.TIER_RANK[HERBS[key][0]] if key in HERBS else 0
    LS.gain(game, 'foraging', 1.5 if key in HERBS else 1, at=at, what=key)
    from .gods import on_craft
    on_craft(game, 'forage')
    if key in HERBS and r >= 5:
        extra = random.randint(0, 1 + r // 8)
        if extra:
            it.n += extra
            n += extra
    if not known(game, key) and random.random() < r * (.07 if key in HERBS else .05):
        learn(game, key, 'you recognise it from experience')
        LS.gain(game, 'foraging', 3, at=at)
    if key in HERBS and known(game, key) and r >= 15:
        learn_prop(game, key, 1)
    game.msg(f'You find {n} {plant_name(game, key)}.' if known(game, key) else f'You find {plant_name(game, key)} ({n}).', 'good')
    if not known(game, key) and PLANTS[key][3] in ('deadly', 'poison') and random.random() < r * .06:
        game.msg('Something about it makes you uneasy.', 'info')
    return round(turns)


def here_tokens(game):
    """What the land here is, in the words of HERBS: its lands and biome, and night, winter, cave, deep, cursed."""
    from . import cooking as CK
    from . import towns as TW
    from .calendar import season
    m, w = game.map, game.world
    toks = {'any'} | set(CK.here_lands(game)) | {CK.here_biome(game)}
    if m.kind == 'dungeon':
        toks = {'cave'} | ({'deep'} if (getattr(m, 'depth', 0) or 0) >= 4 else set())
    if TW.is_night(game):
        toks.add('night')
    if season(game.day) == 'winter':
        toks.add('winter')
    x, y = game.world_pos()
    bl = getattr(w, 'blight', None)
    from .world import WORLD_W
    if (bl and bl[y * WORLD_W + x]) or _tainted(game, x, y):
        toks.add('cursed')
    from . import lifeskills as LS
    if LS.near_site(game, ('starwater', 'starwell', 'wisps', 'stones', 'unwintering', 'mound'), 4) or \
            getattr(m, 'folk', None) == 'elf' or getattr(m, 'glade', False):
        toks.add('wonder')
    return toks


def _tainted(game, x, y):
    try:
        from .evils import taint_at
        return bool(taint_at(game, x, y))
    except Exception:
        return False


def herb_here(game, key, toks=None):
    """Does this herb grow here? Its land, and the land's danger for its tier."""
    from . import lifeskills as LS
    tier, _pr, where = HERBS[key]
    toks = toks if toks is not None else here_tokens(game)
    need = where.split()
    if 'night' in need and 'night' not in toks or 'winter' in need and 'winter' not in toks:
        return False
    lands = [w for w in need if w not in ('night', 'winter')]
    return any(w in toks for w in lands) and LS.tier_open(game, tier)


def draw_herb(game, boost=1):
    """A herb that grows here, by its rarity. Above your rank it is too hard for you yet ('hard'); None if none grow."""
    from . import lifeskills as LS
    toks = here_tokens(game)
    if game.map.kind == 'dungeon' and 'deep' not in toks and random.random() < .7:
        return None
    cands = [k for k in HERBS if herb_here(game, k, toks)]
    if not cands:
        return None
    r = LS.rank(game, 'foraging')
    k = random.choices(cands, [TIER_WEIGHT[HERBS[c][0]] * (boost * (2 if r >= 8 else 1) if HERBS[c][0] != 'A' else 1)
                               * (2 if r >= 30 and HERBS[c][0] in 'CDET' else 1) for c in cands])[0]
    at = LS.TIER_RANK[HERBS[k][0]]
    if at > r:
        LS.too_hard(game, 'foraging', at, plant_name(game, k)[0].upper() + plant_name(game, k)[1:])
        return 'hard'
    return k


# ------------------------------------------------------------------ what you know of a herb
def props_known(game, key):
    """The properties of a herb you know: the names, '?' for what you have not learnt yet."""
    kn = game.player.__dict__.setdefault('herb_props', {}).get(key, set())
    pr = HERBS[key][1]
    if key == 'starmoss':
        return ['Star' if 0 in kn else '?']
    return [pr[i] if i in kn else '?' for i in (0, 1)]


def learn_prop(game, key, i, quiet=False):
    if key not in HERBS:
        return False
    kn = game.player.__dict__.setdefault('herb_props', {}).setdefault(key, set())
    if i in kn:
        return False
    kn.add(i)
    if not quiet:
        what = 'it strengthens any brew' if key == 'starmoss' else HERBS[key][1][i]
        game.msg(f'{PLANTS[key][0]}: {what}.', 'info')
    return True


def pick_season(game, grp):
    """Berries or mushrooms found on the world map in autumn: picked by walking onto them. True if picked."""
    from . import lifeskills as LS
    cands = [k for k, v in PLANTS.items() if v[1] == grp]
    key = random.choices(cands, [PLANTS[k][4] for k in cands])[0]
    n = random.randint(2, 4)
    it = make_plant(game, key, n)
    if not game.add_to_inv(it):
        game.msg('There are ' + ('berries' if grp == 'berry' else 'mushrooms') + ' here, but your pack is full.')
        return False
    LS.gain(game, 'foraging', .5)
    game.msg(f'You pick {n} {plant_name(game, key)}.' if known(game, key) else f'You pick {plant_name(game, key)} ({n}).',
             'good')
    return True


def eat_plant(game, it):
    from . import lifeskills as LS
    from .hunger import MAX
    p = game.player
    key = it.t
    name, grp, food, effect, _w = PLANTS[key]
    was_known = known(game, key)
    if effect in ('deadly', 'poison') and LS.rank(game, 'foraging') >= 40:
        game.msg(f'You know better than to eat {plant_name(game, key)}: it is poison.', 'info')
        learn(game, key, 'a forager knows poison')
        return False
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
        LS.gain(game, 'foraging', 3, at=LS.TIER_RANK[HERBS[key][0]] if key in HERBS else 0)
        learn(game, key, 'the hard way' if effect in ('deadly', 'poison', 'sick', 'sleep') else 'by tasting it')
    if key in HERBS:
        learn_prop(game, key, 0)                    # tasting teaches what it does first
    return 1


def herbalist_talk(game, npc):
    p = game.player
    from . import lifeskills as LS
    if not p.recipes:
        p.recipes.update({'taught'})
        for k in ('yarrow', 'moonpetal', 'dandelion'):
            p.known_plants.add(k)
            learn_prop(game, k, 0, True)
        learn_prop(game, 'yarrow', 1, True)
        game.request = ('dialog', npc.name,
                        f'"A forager, are you? Then listen, before you poison yourself. This one, {game.world.plant_look["yarrow"]}, '
                        f'is yarrow: it heals, and it stops bleeding. And {game.world.plant_look["moonpetal"]}, moonpetal, '
                        f'clears the mind. {game.world.plant_look["dandelion"][0].upper() + game.world.plant_look["dandelion"][1:]} '
                        'is dandelion: it heals too.\n\n'
                        'Every herb has two virtues. Steep two or three herbs together and what they share comes out in '
                        'the brew: yarrow and dandelion both heal, so together they make a healing draught. Share '
                        'nothing, and you have boiled weeds.\n\n'
                        'Never eat a mushroom you do not know. Never. Bring me what you find and I will tell you what it is."')
        LS.gain(game, 'alchemy', 3)
        LS.gain(game, 'foraging', 2)
        return
    unknown = sorted({i.t for i in p.inv if i.k == 'plant' and not known(game, i.t)})
    if unknown:
        lines = []
        for k in unknown:
            lines.append(f'{game.world.plant_look[k]}: {PLANTS[k][0]}' + {'deadly': ' (deadly! throw it away)', 'poison': ' (poisonous)',
                                                                          'sick': ' (makes you sick)', 'sleep': ' (puts you to sleep)'}.get(PLANTS[k][3], '')
                         + (f'; it gives {HERBS[k][1][0]}' if k in HERBS and k != 'starmoss' else ''))
            p.known_plants.add(k)
            learn_prop(game, k, 0, True)
        LS.gain(game, 'foraging', len(unknown))
        game.request = ('dialog', npc.name, '"Let me see what you have there... "\n\n' + '\n'.join(lines))
        return
    game.say(npc, random.choice(['Yarrow for wounds, moonpetal for the mind, feverfew for the belly.',
                                 'The deathcap looks like any other mushroom. That is what makes it so good at killing.',
                                 'Three herbs that share one virtue make a strong brew.',
                                 'Come back when you have found something new.']))
