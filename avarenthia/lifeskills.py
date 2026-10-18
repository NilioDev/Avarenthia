"""Life skills: crafts and pastimes that grow by doing them, each with its own rewards along the way
(in the spirit of Project Gorgon). Fishing is the first; more will follow."""
import random

from . import data as D

LIFE = {
    'fishing': dict(name='Fishing', desc='Cast a line by any shore, river or pool (a, with a pole).',
                    perks={3: 'Trout and carp start to bite', 5: 'Casts take less time', 8: 'Pike bite in deep water',
                           12: 'Salmon run in the rivers', 15: 'Casts take much less time',
                           18: 'The legendary golden carp may bite', 25: 'Master angler: almost every cast lands a fish'}),
    'foraging': dict(name='Foraging', desc='Search the wild for food (F). Taste strange plants with care.',
                     perks={3: 'You sometimes recognise what you pick', 5: 'You find more at once', 8: 'Poisonous plants make you uneasy',
                            10: 'Searching takes less time', 15: 'You rarely come back empty-handed'}),
    'herbalism': dict(name='Herbalism', desc='Picking herbs and knowing them; grows as you pick and learn.',
                      perks={3: 'You often recognise the herbs you pick', 5: 'You gather more herbs at once',
                             8: 'Kingsfoil and other rare herbs turn up more often', 12: 'You can tell a herb at a glance'}),
    'alchemy': dict(name='Alchemy', desc='Potions from herbs (P). Monastery herbalists teach the basics.',
                    perks={3: 'Recipe: Antidote', 5: 'Fewer ruined potions', 8: 'Recipe: Kingsfoil Elixir', 10: 'Potions rarely fail'}),
    'brewing': dict(name='Brewing', desc='Ale, mead and wine (P), at an inn or in a monastery cellar.',
                    perks={3: 'Recipe: Berry Wine', 5: 'Fewer spoiled batches', 6: 'Recipe: Mead', 10: 'You brew an extra mug now and then'}),
    'mining': dict(name='Mining', desc='Dig ore and gems from veins (walk into one, with a pick).',
                   perks={3: 'You dig a little faster', 6: 'You dig faster', 10: 'Now and then a gem among the ore',
                          15: 'You dig much faster'}),
    'hunting': dict(name='Hunting', desc='Tracks and herds: walk into a herd on the world map.',
                    perks={3: 'You read how old tracks are', 6: 'Game notices you a little later',
                           10: 'You see herds from further off', 15: 'You snare small game more often'}),
    'skinning': dict(name='Skinning', desc='Stand on a carcass and press Enter, with a knife or a dagger.',
                     perks={3: 'Fewer torn hides', 8: 'Good hides more often', 15: 'An extra cut of meat',
                            20: 'Fine hides more often'}),
    'cooking': dict(name='Cooking', desc='Walk into a fire or a hearth. No recipes: try things in the pot.',
                    perks={5: 'Fewer burnt dishes', 10: 'An extra portion from every pot',
                           15: 'You taste what is in the inn\'s stew', 20: 'Another portion, and stronger dishes'}),
    'leatherworking': dict(name='Leatherworking', desc='Leather goods at a workbench; oak bark tans a salted hide.',
                           perks={5: 'Sturdier work', 15: 'Fine work: better armour'}),
}
LIFE_ORDER = ['fishing', 'foraging', 'herbalism', 'alchemy', 'brewing', 'mining', 'hunting', 'skinning', 'cooking',
              'leatherworking']

# key: name, minimum rank, waters, weight, value, healing
FISH = {
    'minnow': ('Minnow', 0, 'river lake sea swamp cave', 10, 2, 3),
    'perch': ('River Perch', 0, 'river lake', 8, 5, 6),
    'herring': ('Herring', 0, 'sea', 9, 4, 5),
    'carp': ('Mud Carp', 3, 'lake swamp', 7, 8, 8),
    'trout': ('Brown Trout', 3, 'river', 7, 10, 10),
    'cavefish': ('Blind Cavefish', 2, 'cave', 7, 16, 9),
    'eel': ('Marsh Eel', 5, 'swamp river', 5, 14, 12),
    'mackerel': ('Mackerel', 4, 'sea', 6, 12, 10),
    'pike': ('Pike', 8, 'lake river', 4, 24, 16),
    'salmon': ('Silver Salmon', 12, 'river', 4, 32, 20),
    'tuna': ('Bluefin', 12, 'sea', 3, 36, 22),
    'golden': ('Golden Carp', 18, 'lake river swamp', 1, 140, 30),
    'legend': ('Legendary Fish', 16, '', 0, 0, 0),           # the big one of a Brotherhood job: never caught by chance
}
JUNK = ['an old boot', 'a tangle of weed', 'a rusty helmet', 'a waterlogged branch']


def need_for(r):
    return 20 + r * 6


def gain(game, key, amount):
    from .races import RACES
    p = game.player
    sk = p.life_sk.setdefault(key, [0, 0])
    rc = RACES.get(getattr(p, 'race', 'human'), RACES['human'])
    from .guilds import life_bonus
    sk[1] += amount * rc['learn'].get(key, 1.1 if p.race == 'human' else 1) * life_bonus(game, key)
    while sk[0] < 50 and sk[1] >= need_for(sk[0]):
        sk[1] -= need_for(sk[0])
        sk[0] += 1
        game.msg(f"Your {LIFE[key]['name']} rises to {sk[0]}.", 'good')
        perk = LIFE[key]['perks'].get(sk[0])
        if perk:
            game.msg(f'New at {LIFE[key]["name"]} {sk[0]}: {perk}.', 'gold')


def rank(game, key):
    return game.player.life_sk.get(key, [0, 0])[0]


# ------------------------------------------------------------------ fishing
def water_here(game):
    """The kind of water next to the player, or None."""
    m, p = game.map, game.player
    kinds = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            x, y = p.x + dx, p.y + dy
            if not m.inb(x, y):
                continue
            t = m.tile(x, y)
            if t == D.RIVER or (m.kind == 'over' and getattr(m, 'river', None) and m.river[y * m.w + x] and t == D.ROAD):
                kinds.append('river')
            elif t in (D.WATER, D.SHALLOW):
                if m.kind == 'dungeon':
                    kinds.append('cave')
                elif m.kind == 'over':
                    kinds.append('sea' if _open_water(m, x, y) else 'lake')
                else:
                    kinds.append('swamp' if any(m.tile(x + a, y + b) == D.SWAMP for a in (-1, 0, 1) for b in (-1, 0, 1)
                                                if m.inb(x + a, y + b)) or m.tile(p.x, p.y) == D.SWAMP else 'lake')
    if not kinds:
        if m.kind == 'over' and m.tile(p.x, p.y) == D.SWAMP:
            return 'swamp'
        return None
    for k in ('river', 'sea', 'lake', 'swamp', 'cave'):
        if k in kinds:
            return k
    return kinds[0]


def _open_water(m, x, y):
    n = 0
    for dy in range(-4, 5, 2):
        for dx in range(-4, 5, 2):
            if m.inb(x + dx, y + dy) and m.tile(x + dx, y + dy) == D.WATER:
                n += 1
    return n >= 18


def has_pole(game):
    return any(i.k == 'tool' and i.t == 'rod' for i in game.player.inv)


def make_fish(game, key, n=1):
    from .entities import Item
    it = Item(game.new_id(), 'fish', key, n)
    it.name = FISH[key][0]
    return it


def can_fish(game):
    """The kind of water you would fish in, or None (with the reason told)."""
    if not has_pole(game):
        game.msg('You need a fishing pole. Outfitters sell them for a few coins.')
        return None
    if game.hostile_visible():
        game.msg('Not with enemies about!', 'bad')
        return None
    water = water_here(game)
    if not water:
        game.msg('There is no water here to fish in. Stand next to a river, lake, pool or the sea.')
        return None
    return water


def plan(game, water):
    """What is down there, decided when you cast: nothing, junk, a bottle, a fish, or something you do not want."""
    r = rank(game, 'fishing')
    over = game.map.kind == 'over'
    turns = round((30 if over else 6) * (.6 if r >= 15 else .8 if r >= 5 else 1))
    chance = min(.92 if r >= 25 else .82, .35 + r * .025)
    p = game.player
    from .anim import rising_near
    if rising_near(game, p.x, p.y):
        chance = min(.95, chance + .2)                # cast where the rings are
        game.msg('Fish are rising here.', 'info')
    from .nature import fish_bonus
    chance = min(.95, chance + fish_bonus(game))
    out = dict(water=water, rank=r, turns=turns, kind='none', fish=None, weight=0)
    from .evils import taint_at
    ev = taint_at(game, p.x, p.y) if over else None
    if over and random.random() < (.06 if ev else .015):
        lvl = game.world.danger_at(p.x, p.y) + 1
        keys = ['drowned', 'drowned'] if ev and ev.key == 'drowned' else ['zombie'] if game.world.danger_at(p.x, p.y) > 6 else ['jackal', 'jackal']
        out.update(kind='monster', keys=keys, lvl=lvl, weight=9)
        return out
    from . import jobs as JB
    if JB.big_bite(game, water):
        out.update(kind='fish', fish='legend', weight=9)
        return out
    if random.random() >= chance:
        return out
    if random.random() < max(.02, .12 - r * .008):
        hidden = [q for q in game.world.pois if not q.found]
        if random.random() < .25 and hidden:
            out.update(kind='bottle', poi=random.choice(hidden).id, weight=1)
        else:
            out.update(kind='junk', junk=random.choice(JUNK), weight=2)
        return out
    cands = [(k, f) for k, f in FISH.items() if f[1] <= r and water in f[2].split()]
    if not cands:
        cands = [('minnow', FISH['minnow'])]
    k, f = random.choices(cands, [f[3] * (1 + (f[1] / 10)) for _k, f in cands])[0]
    out.update(kind='fish', fish=k, weight=1 + f[1] // 3)
    return out


def land(game, pl, ok):
    """How it ends: ok is whether you struck in time and brought it in. Returns the turns it took."""
    gain(game, 'fishing', .5)
    kind = pl['kind']
    if kind == 'monster':
        game.msg('Something huge takes the bait and pulls. Then it comes out of the water after you!', 'bad')
        game.start_encounter(None, game.map.tile(game.player.x, game.player.y), pl['lvl'], pl['keys'])
        return 1
    if kind == 'none':
        game.msg(random.choice(['Nothing bites.', 'A nibble... and it is gone.', 'The float bobs, then lies still.',
                                'Something steals your bait.']))
        return pl['turns']
    if not ok:
        return pl['turns']
    if kind == 'bottle':
        from .events import reveal
        q = game.world.pois[pl['poi']]
        reveal(game, q)
        game.msg(f'You fish up a bottle with a map inside! It shows the way to {q.name}.', 'gold')
        gain(game, 'fishing', 3)
        return pl['turns']
    if kind == 'junk':
        game.msg(f'You reel in... {pl["junk"]}. You toss it back.')
        return pl['turns']
    k = pl['fish']
    if k == 'legend':
        from . import jobs as JB
        JB.landed(game)
        gain(game, 'fishing', 6)
        return pl['turns']
    f = FISH[k]
    it = make_fish(game, k)
    if game.add_to_inv(it):
        game.msg(f'You catch a {f[0]}!', 'gold' if f[1] >= 12 else 'good')
    else:
        game.msg(f'You catch a {f[0]}, but your pack is full. You let it go.')
    gain(game, 'fishing', 1 + f[1] // 6)
    from .gods import on_craft
    on_craft(game, 'fish')
    if k == 'golden':
        game.msg('A golden carp! Fishermen will talk about this for years.', 'unique')
    return pl['turns']


def fish(game):
    """One quick cast, decided at once (a master angler's way, and the tests'). Returns the turns it took."""
    water = can_fish(game)
    if not water:
        return 0
    return land(game, plan(game, water), True)


def place_name(game):
    m = game.map
    here = game.here
    return f'{m.name}' if m.kind != 'over' else (here.name if here else 'the open country')


def eat(game, it):
    f = FISH.get(it.t)
    if not f:
        return 0
    p = game.player
    game.remove_one(it)
    game.heal(f[5], True)
    game.msg(f'You eat the {f[0].lower()}. It is {"delicious" if f[1] >= 8 else "not bad"}.', 'good')
    return 1
