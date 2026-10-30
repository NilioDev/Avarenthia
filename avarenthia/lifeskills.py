"""Life skills: crafts and pastimes that grow slowly by doing them, up to rank 50.
Work far below your rank teaches nothing, a first make or catch counts double, and what you gather has a tier that
follows the danger of the land. Fishing lives here; the others in foraging, alchemy, brewing, crafts, hunting, cooking."""
import random

from . import data as D

LIFE = {
    'fishing': dict(name='Fishing', desc='Cast a line by any shore, river or pool (a, with a pole).',
                    perks={3: 'Trout and carp start to bite', 5: 'Casts take less time', 8: 'Pike bite in deep water',
                           12: 'Salmon run in the rivers', 15: 'Casts take much less time',
                           18: 'The legendary golden carp may bite', 25: 'Master angler: almost every cast lands a fish',
                           30: 'You cut a hole in the ice and fish through it in winter',
                           40: 'In a storm the big ones bite', 50: 'Now and then two fish on one line'}),
    'foraging': dict(name='Foraging', desc='Food and herbs from the wild (F). Taste strange plants warily.',
                     perks={3: 'You sometimes recognise what you pick', 5: 'You find more at once',
                            8: 'Poisonous plants make you uneasy; rare herbs turn up more often',
                            10: 'Searching takes less time', 12: 'You can tell a herb at a glance',
                            15: 'You see a herb\'s second property when you pick it; you rarely come back empty-handed',
                            30: 'Rare herbs turn up twice as often', 40: 'You never eat a poisonous plant by mistake',
                            50: 'A herb you know catches your eye as you pass'}),
    'alchemy': dict(name='Alchemy', desc='Draughts and oils from herbs (P): what two or three herbs share.',
                    perks={5: 'Fewer ruined brews', 10: 'Brews rarely fail', 20: 'Stronger brews',
                           30: 'Now and then two from one brew', 40: 'Oils last longer', 50: 'Your brews never fail'}),
    'brewing': dict(name='Brewing', desc='Ale, cider, wine, mead and spirits (P), at an inn or a cellar.',
                    perks={5: 'Fewer spoiled batches', 10: 'You brew an extra mug now and then',
                           30: 'A barrel with every batch, when your cart has room', 40: 'Your drinks sell better',
                           50: 'Your name on the label: inns buy what you brew'}),
    'mining': dict(name='Mining', desc='Dig ore and gems from veins (walk into one, with a pick).',
                   perks={3: 'You dig a little faster', 6: 'You dig faster', 10: 'Now and then a gem among the ore',
                          15: 'You dig much faster', 30: 'You see a vein through one wall',
                          40: 'You hear a cave-in coming and are out from under it', 50: 'Every vein gives one more'}),
    'smithing': dict(name='Smithing', desc='At an anvil: smelt ore, forge arms and armour, mend, hone.',
                     perks={5: 'Fewer crude pieces', 15: 'Fine work more often', 25: 'Masterwork now and then',
                            30: 'You mend on the road with a bar from your pack', 40: 'Two parts in a piece, and Unmake',
                            50: 'Masterwork more often; Unmake at full value'}),
    'hunting': dict(name='Hunting', desc='Tracks and herds: walk into a herd on the world map.',
                    perks={3: 'You read how old tracks are', 6: 'Game notices you a little later',
                           10: 'You see herds from further off', 15: 'You snare small game more often',
                           30: 'The tracks of named beasts stay readable twice as long',
                           40: 'You stalk a herd to striking distance', 50: 'A beast\'s den shows as soon as you find its track'}),
    'skinning': dict(name='Skinning', desc='Stand on a carcass and press Enter, with a knife or a dagger.',
                     perks={3: 'Fewer torn hides', 8: 'Good hides more often', 15: 'An extra cut of meat',
                            20: 'Fine hides more often', 30: 'Trophies of big game', 40: 'Parts never tear',
                            50: 'Fine hides of common game'}),
    'cooking': dict(name='Cooking', desc='Walk into a fire or a hearth. No recipes: try things in the pot.',
                    perks={5: 'Fewer burnt dishes', 10: 'An extra portion from every pot',
                           15: 'You taste what is in the inn\'s stew', 20: 'Another portion, and stronger dishes',
                           30: 'A feast: one dish feeds your whole company', 40: 'Your dishes keep twice as long',
                           50: 'What a dish does lasts longer'}),
    'leatherworking': dict(name='Leatherworking', desc='Leather goods at a workbench; oak bark tans a salted hide.',
                           perks={5: 'Sturdier work', 15: 'Fine work more often', 25: 'Masterwork now and then',
                                  30: 'You mend on the road with leather from your pack',
                                  40: 'Two parts in a piece, and Unmake', 50: 'Masterwork more often; Unmake at full value'}),
    'tailoring': dict(name='Tailoring', desc='Cloth at a workbench: robes, hoods, wraps; bandages, rope.',
                      perks={5: 'Fewer crude pieces', 15: 'Fine work more often', 25: 'Masterwork now and then',
                             30: 'You mend on the road with cloth from your pack', 40: 'Two parts in a piece, and Unmake',
                             50: 'Masterwork more often; Unmake at full value'}),
}
LIFE_ORDER = ['fishing', 'foraging', 'alchemy', 'brewing', 'mining', 'smithing', 'hunting', 'skinning', 'cooking',
              'leatherworking', 'tailoring']

# the steps of a life skill: what each lets you work, and how dangerous the land must be for it to lie there
TIERS = 'ABCDE'
TIER_RANK = {'A': 0, 'B': 10, 'C': 20, 'D': 30, 'E': 40, 'T': 30}
TIER_DANGER = {'A': 0, 'B': 4, 'C': 6, 'D': 8, 'E': 10, 'T': 0}

# key: name, rank, waters, weight, value, healing, tier, where else (night, storm, north, south, mountain, broad,
#      deep, deepest, forest, star: see fish_cond)
FISH = {
    # A, fresh water
    'minnow': ('Minnow', 0, 'river lake swamp cave', 10, 2, 3, 'A', ''),
    'perch': ('River Perch', 0, 'river lake', 8, 5, 6, 'A', ''),
    'carp': ('Mud Carp', 2, 'lake swamp', 7, 8, 8, 'A', ''),
    'trout': ('Brown Trout', 3, 'river', 7, 10, 10, 'A', ''),
    'cavefish': ('Blind Cavefish', 2, 'cave', 7, 16, 9, 'A', ''),
    'eel': ('Marsh Eel', 5, 'swamp river', 5, 14, 12, 'A', ''),
    'pike': ('Pike', 7, 'lake river', 4, 24, 16, 'A', ''),
    # A, salt water
    'sprat': ('Sprat', 0, 'sea', 10, 2, 3, 'A', ''),
    'herring': ('Herring', 0, 'sea', 9, 4, 5, 'A', ''),
    'flounder': ('Flounder', 2, 'sea', 7, 8, 8, 'A', ''),
    'mackerel': ('Mackerel', 4, 'sea', 6, 12, 10, 'A', ''),
    'cod': ('Cod', 6, 'sea', 5, 18, 14, 'A', ''),
    # B
    'salmon': ('Silver Salmon', 10, 'river', 4, 32, 20, 'B', ''),
    'tuna': ('Bluefin', 12, 'sea', 3, 36, 22, 'B', ''),
    'catfish': ('Catfish', 11, 'swamp', 4, 30, 20, 'B', ''),
    'grayling': ('Grayling', 13, 'river', 4, 34, 20, 'B', 'mountain'),
    # C
    'sturgeon': ('Great Sturgeon', 20, 'river', 3, 70, 28, 'C', 'broad'),
    'swordfish': ('Swordfish', 22, 'sea', 3, 75, 30, 'C', ''),
    'ice_char': ('Ice Char', 24, 'lake', 3, 70, 28, 'C', 'north'),
    'deep_eel': ('Deep Eel', 23, 'cave', 3, 72, 28, 'C', 'deep'),
    # D
    'ghost_pike': ('Ghost Pike', 30, 'lake', 2, 120, 36, 'D', 'night forest'),
    'sailfish': ('Sailfish', 32, 'sea', 2, 125, 38, 'D', 'south'),
    'whitefish': ('Blind Whitefish', 34, 'cave', 2, 120, 36, 'D', 'deep'),
    # E
    'thunderfin': ('Thunderfin', 40, 'sea', 2, 200, 44, 'E', 'storm'),
    'abyss_eel': ('Abyss Eel', 42, 'cave', 2, 210, 44, 'E', 'deepest'),
    'elder_sturgeon': ('Elder Sturgeon', 45, 'river', 1, 240, 50, 'E', 'broad'),
    # the top: luck, and the crafts' own rares
    'golden': ('Golden Carp', 15, 'lake river swamp', 1, 140, 30, 'T', ''),
    'moonfish': ('Moonfish', 35, 'lake', 1, 260, 40, 'T', 'star night'),
    'legend': ('Legendary Fish', 16, '', 0, 0, 0, 'T', ''),  # the big one of a Brotherhood job: never caught by chance
}
JUNK = ['an old boot', 'a tangle of weed', 'a rusty helmet', 'a waterlogged branch']


def need_for(r):
    """Slow, like the long road beside the fighting: rank 10 in about an hour, 50 in sixty hours or more."""
    return round(20 + 4 * r + .35 * r * r)


# how much a piece of work teaches, by its rank against yours
COLOURS = {'grey': ((128, 128, 128), 0), 'green': ((110, 200, 100), .35), 'yellow': ((236, 210, 90), 1),
           'orange': ((240, 150, 60), 1.3)}


def colour(r, at):
    """The colour of a piece of work in a craft list: grey teaches nothing, green little, yellow and orange most."""
    d = r - at
    return 'grey' if d >= 10 else 'green' if d >= 5 else 'yellow' if d >= -2 else 'orange'


def colour_of(game, key, at):
    return COLOURS[colour(rank(game, key), at)][0]


def first_time(game, key, what):
    """True the first time you make or catch this: it counts double."""
    done = game.player.__dict__.setdefault('life_firsts', set())
    if (key, what) in done:
        return False
    done.add((key, what))
    return True


def gain(game, key, amount, at=None, what=None):
    """Learning by doing. With `at` (the rank of the work) the work far below you teaches nothing; with `what` the
    first time you make or catch it counts double."""
    from .races import RACES
    p = game.player
    sk = p.life_sk.setdefault(key, [0, 0])
    if at is not None:
        amount *= COLOURS[colour(sk[0], at)][1]
    if what is not None and first_time(game, key, what):
        amount *= 2
    if amount <= 0:
        return
    rc = RACES.get(getattr(p, 'race', 'human'), RACES['human'])
    from .guilds import life_bonus
    sk[1] += amount * rc['learn'].get(key, 1.1 if p.race == 'human' else 1) * life_bonus(game, key)
    while sk[0] < 50 and sk[1] >= need_for(sk[0]):
        from . import mastery as MA
        if MA.held(game, key, sk[0]):                   # 25 and 40: a master's test first
            sk[1] = need_for(sk[0])
            break
        sk[1] -= need_for(sk[0])
        sk[0] += 1
        game.msg(f"Your {LIFE[key]['name']} rises to {sk[0]}.", 'good')
        perk = LIFE[key]['perks'].get(sk[0])
        if perk:
            game.msg(f'New at {LIFE[key]["name"]} {sk[0]}: {perk}.', 'gold')


def place_danger(game):
    """How dangerous the land is where you stand: the danger of the country, and each floor down counts one more."""
    x, y = game.world_pos()
    d = game.world.danger_at(x, y) if game.maps['over'].inb(x, y) else 1
    m = game.map
    if m.kind == 'dungeon':
        d += max(0, (getattr(m, 'depth', 1) or 1) - 1) + 2
    return d


def tier_open(game, tier):
    """Does the land here hold work of this tier?"""
    return place_danger(game) >= TIER_DANGER[tier]


def too_hard(game, key, at, name):
    game.msg(f'{name}: too hard for you yet ({LIFE[key]["name"]} {at}).', 'info')


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
    if all_frozen(game):
        if rank(game, 'fishing') < 30:
            game.msg('The water is frozen hard. Cutting a hole for a line is a master\'s trick (Fishing 30).', 'info')
            return None
        game.msg('You cut a hole in the ice and let your line down into the dark water.', 'info')
    return water


def all_frozen(game):
    """On the world map in deep winter: is every water beside you frozen?"""
    m, p = game.map, game.player
    if m.kind != 'over':
        return False
    from . import seasons as SE
    st = SE.Now(game)
    cells = [(p.x + dx, p.y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if m.inb(p.x + dx, p.y + dy)
             and m.tile(p.x + dx, p.y + dy) in (D.WATER, D.RIVER, D.SHALLOW)]
    return bool(cells) and all(SE.frozen(m, y * m.w + x, st) for x, y in cells)


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
    chance = min(.95, chance + fish_bonus(game) + (.08 if any(i.k == 'tool' and i.t == 'hooks' for i in p.inv) else 0))
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
    here = [(k, f) for k, f in FISH.items() if water in f[2].split() and fish_cond(game, f[7]) and tier_open(game, f[6])]
    if r >= 25:
        here = [(k, f) for k, f in here if f[1] >= 5] or here      # a master's hook is too big for a minnow
    cands = [(k, f) for k, f in here if f[1] <= r]
    big = [(k, f) for k, f in here if f[1] > r]
    if big and random.random() < .12:
        k, f = random.choice(big)
        out.update(kind='big', fish=k)                # something too strong for your line yet
        return out
    if not cands:
        cands = [('sprat' if water == 'sea' else 'minnow', FISH['sprat' if water == 'sea' else 'minnow'])]
    storm = r >= 40 and fish_cond(game, 'storm')          # a master knows the big ones bite in a storm
    k, f = random.choices(cands, [f[3] * (1 + (f[1] / 10)) * (2.5 if storm and f[6] in 'CDE' else 1) for _k, f in cands])[0]
    out.update(kind='fish', fish=k, weight=1 + f[1] // 3)
    return out


def fish_cond(game, cond):
    """Where else a fish wants to be: at night, in a storm, in the north or the south, in a mountain stream, in a
    broad river, deep under the earth, by a forest, at the Starwater."""
    if not cond:
        return True
    from . import towns as TW
    m = game.map
    for c in cond.split():
        if c == 'night' and not TW.is_night(game):
            return False
        if c == 'storm':
            from . import weather as WX
            if WX.current(game) != 'storm':
                return False
        if c in ('north', 'south'):
            from .weather import climate
            x, y = game.world_pos()
            cl = climate(game.world, game.world.region_at(x, y).id)
            from .world import WORLD_H
            south = cl in ('arid', 'hot', 'tropical') or y > WORLD_H * .7
            if (c == 'north' and cl != 'cold') or (c == 'south' and not south):
                return False
        if c in ('mountain', 'forest'):
            from . import cooking as CK
            lands = CK.here_lands(game)
            if c not in lands:
                return False
        if c == 'broad' and not _broad(game):
            return False
        if c in ('deep', 'deepest'):
            depth = (getattr(m, 'depth', 0) or 0) if m.kind == 'dungeon' else 0
            if depth < (4 if c == 'deep' else 6):
                return False
        if c == 'star' and not near_site(game, ('starwater', 'starwell'), 6):
            return False
    return True


def _broad(game):
    """A broad river: three or more river cells across, where you stand."""
    m, p = game.map, game.player
    n = sum(1 for dx in range(-3, 4) for dy in range(-3, 4) if m.inb(p.x + dx, p.y + dy) and m.tile(p.x + dx, p.y + dy) == D.RIVER)
    return n >= 12


def near_site(game, kinds, r):
    from .worldgen import cheb
    x, y = game.world_pos()
    return any(q.kind in kinds and cheb(q.x, q.y, x, y) <= r for q in game.world.sites)


def land(game, pl, ok):
    """How it ends: ok is whether you struck in time and brought it in. Returns the turns it took."""
    kind = pl['kind']
    gain(game, 'fishing', .5, at=FISH[pl['fish']][1] if pl.get('fish') else best_here(game, pl['water']))
    if kind == 'monster':
        game.msg('Something huge takes the bait and pulls. Then it comes out of the water after you!', 'bad')
        game.start_encounter(None, game.map.tile(game.player.x, game.player.y), pl['lvl'], pl['keys'])
        return 1
    if kind == 'big':
        game.msg(f'Something heavy takes the hook and snaps your line at once. A {FISH[pl["fish"]][0]}? Too strong for '
                 f'you yet (Fishing {FISH[pl["fish"]][1]}).', 'info')
        return pl['turns']
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
        game.msg(f'You catch a {f[0]}!', 'gold' if f[1] >= 10 else 'good')
    else:
        game.msg(f'You catch a {f[0]}, but your pack is full. You let it go.')
    gain(game, 'fishing', 1 + f[1] // 6, at=f[1], what=k)
    if rank(game, 'fishing') >= 50 and f[6] != 'T' and random.random() < .15:
        two = make_fish(game, k)
        if game.add_to_inv(two):
            game.msg(f'A second {f[0]} comes up on the same line!', 'good')
    from .gods import on_craft
    on_craft(game, 'fish')
    if k == 'golden':
        game.msg('A golden carp! Fishermen will talk about this for years.', 'unique')
    elif k == 'moonfish':
        game.msg('A moonfish, pale as the moon on the water. A cook would give much for it.', 'unique')
    return pl['turns']


def fish(game):
    """One quick cast, decided at once (a master angler's way, and the tests'). Returns the turns it took."""
    water = can_fish(game)
    if not water:
        return 0
    return land(game, plan(game, water), True)


def best_here(game, water):
    """The rank of the best fish you can catch in this water: what a cast that brings nothing teaches by."""
    rs = [f[1] for f in FISH.values() if water in f[2].split() and f[1] <= rank(game, 'fishing')
          and fish_cond(game, f[7]) and tier_open(game, f[6])]
    return max(rs) if rs else 0


def bandage(game, it):
    """A bandage (Tailoring): it stops the bleeding and a little life comes back."""
    p = game.player
    game.remove_one(it)
    p.poison = None
    game.heal(8 + rank(game, 'tailoring') // 2, True)
    game.msg('You bind the wound tight. The bleeding stops.', 'good')
    return 3


def net(game):
    """A fishing net (Tailoring): small fish from shallow water, without a cast. Returns the turns it took."""
    water = water_here(game)
    if not water or game.hostile_visible():
        game.msg('Cast the net beside shallow water, with no enemies about.', 'info')
        return 0
    small = [k for k, f in FISH.items() if water in f[2].split() and f[1] <= 3 and f[6] == 'A' and not f[7]]
    if not small or random.random() < .35:
        game.msg('You haul the net in: weed and mud.')
        return 20
    k = random.choice(small)
    n = random.randint(1, 3)
    it = make_fish(game, k, n)
    game.add_to_inv(it) or game.spill(game.map, game.player.x, game.player.y, it)
    game.msg(f'You haul the net in: {n} {FISH[k][0].lower()}{"" if n == 1 else "s"}.', 'good')
    gain(game, 'fishing', .3, at=FISH[k][1])
    return 20


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
