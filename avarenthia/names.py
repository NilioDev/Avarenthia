"""Place names: one name maker for every people.

Each people has a small grammar of parts and patterns, with a small chance of a fixed, hand-made name. A name is
made when the world is made, fits the land where the place lies (no -ford without a river, no -haven away from the
sea) and is never used twice in one world (`world.used_names`). Humans speak three ways by where they live: the north
Norse-sounding, the west Celtic-sounding, the heartland old English.
"""
import random

from . import data as D

# ------------------------------------------------------------------ the land under a place
HIGH = {'mountain', 'hills', 'alpine', 'tundra_hills', 'canyon', 'peak', 'glacier', 'mesa', 'badlands', 'karst'}
WOOD = {'forest', 'deep_forest', 'taiga', 'conifer', 'birch', 'jungle', 'dry_forest', 'petrified'}
MARSH = {'swamp', 'marsh', 'mangrove', 'floodplain', 'moor'}


def land_at(m, x, y):
    """What lies around a place on the world map: a set of 'river', 'coast', 'hills', 'wood', 'marsh'."""
    out = set()
    riv = getattr(m, 'river', None)
    names = getattr(m, 'biome_names', None)
    bs = {}
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            xx, yy = x + dx, y + dy
            if not m.inb(xx, yy):
                continue
            i = yy * m.w + xx
            t = m.t[i]
            near = max(abs(dx), abs(dy)) <= 1
            if near and ((riv and riv[i]) or t == D.RIVER):
                out.add('river')
            if t == D.WATER:
                b = names[m.biome[i]] if names else ''
                if b != 'lake':
                    out.add('coast')
                elif near:
                    out.add('lake')
            if near and t in (D.HILLS, D.MOUNTAIN):
                out.add('hills')
            if names:
                b = names[m.biome[i]]
                bs[b] = bs.get(b, 0) + 1
    if names:
        if sum(v for k, v in bs.items() if k in HIGH) >= 5:
            out.add('hills')
        if sum(v for k, v in bs.items() if k in WOOD) >= 9:
            out.add('wood')
        if sum(v for k, v in bs.items() if k in MARSH) >= 6:
            out.add('marsh')
    return out


def dialect(m, x, y):
    """Which way the humans speak here: the north, the west or the heartland."""
    if y < m.h * .36:
        return 'north'
    if x < m.w * .34:
        return 'west'
    return 'heart'


# words that only fit some land: a name with one of them is used only where that land is
NEEDS = [
    ('river', ('ford', 'bridge', 'wade', 'wath', 'Aber', 'Rhyd', 'Water')),
    ('coast', ('haven', 'mouth', 'Port', 'Porth', 'ness', 'Salt', 'sound', 'reach', 'Gull', 'strand')),
    ('hills', ('crag', 'fell', 'Dun', 'Bryn', 'scar', 'howe', 'down', 'ridge', 'edge', 'Hill', 'hill', 'tor')),
    ('wood', ('wood', 'holt', 'hurst', 'shaw', 'lund', 'Coed', 'grove', 'with')),
    ('marsh', ('fen', 'marsh', 'Ros', 'carr', 'mire', 'Mire')),
]


def fits(name, land):
    for need, words in NEEDS:
        if need in land or (need == 'river' and 'lake' in land and 'Water' in name):
            continue
        if any(w in name for w in words):
            return False
    return True


def pick(xs):
    return random.choice(xs)


# ------------------------------------------------------------------ humans
HEART = dict(
    a=['Ash', 'Bram', 'Brad', 'Ald', 'Elm', 'Oak', 'Thorn', 'Hazel', 'Wil', 'Bar', 'Cold', 'Kings', 'Mill', 'Stan',
       'Black', 'White', 'Red', 'Green', 'Long', 'Hart', 'Hay', 'Lang', 'Wor', 'Bur', 'Ches', 'Sut', 'Nor', 'Hal', 'Ted',
       'Lud', 'Cran', 'Fern', 'Hollin', 'Ox', 'Sal', 'Bex', 'Wend', 'Ast', 'Bil', 'Col', 'Dur', 'Eller', 'Fox', 'Gos',
       'Har', 'Hen', 'Lin', 'Mar', 'Pen', 'Rad', 'Sel', 'Shep', 'Ty', 'Wal', 'Whit', 'Yar', 'Bramble', 'Barrow'],
    any=['ton', 'ley', 'ham', 'bury', 'wick', 'field', 'stead', 'worth', 'cote', 'combe', 'den', 'well', 'stow',
         'brook', 'mere', 'thorpe', 'ington', 'bourne', 'church', 'hall', 'green', 'gate'],
    river=['ford', 'bridge', 'ford', 'wade', 'brook'],
    coast=['haven', 'mouth', 'strand', 'haven'],
    hills=['down', 'hill', 'ridge', 'edge', 'tor', 'don'],
    wood=['wood', 'holt', 'hurst', 'grove', 'shaw'],
    marsh=['fen', 'mere', 'marsh', 'moor'],
)
NORTH = dict(
    a=['Thor', 'Kettle', 'Raven', 'Skel', 'Grim', 'Ulf', 'Stain', 'Ask', 'Kirk', 'Hag', 'Brod', 'Sca', 'Tos', 'Ormes',
       'Swin', 'Gun', 'Har', 'Ald', 'Bjor', 'Siggs', 'Kel', 'Sax', 'Eske', 'Frost', 'Wolf', 'Hrafn', 'Ing',
       'Kald', 'Lod', 'Mick', 'Nab', 'Os', 'Rae', 'Sel', 'Tor', 'Ulls', 'Wath', 'Yng', 'Bol', 'Dal', 'Hof', 'Ketil'],
    any=['by', 'thorpe', 'wick', 'garth', 'toft', 'holm', 'thwaite', 'gard', 'by', 'stad', 'set', 'bek'],
    river=['wath', 'ford', 'bridge'],
    coast=['ness', 'wick', 'sound', 'mouth', 'haven'],
    hills=['fell', 'crag', 'scar', 'howe'],
    wood=['lund', 'with', 'skeld'],
    marsh=['carr', 'mire', 'mere'],
)
WEST = dict(
    roots=['morrow', 'vellan', 'farren', 'lewyn', 'dower', 'gwyth', 'ithel', 'maris', 'goren', 'ruan', 'tarran',
           'wenna', 'brannoc', 'elow', 'cadoc', 'hayle', 'derwen', 'gelli', 'idris', 'myrddin', 'nant', 'owen', 'rhos',
           'sennen', 'tegid', 'wynn', 'alder', 'carrow', 'dinas', 'fynnon', 'garrow', 'kellan', 'lowen', 'meneth'],
    any=['Pen', 'Tre', 'Llan', 'Kil', 'Pol', 'Lis'],
    river=['Aber', 'Rhyd'],
    coast=['Porth', 'Aber'],
    hills=['Bryn', 'Dun', 'Carn'],
    wood=['Coed'],
    marsh=['Ros', 'Mor'],
)
PORTS = ['Varen', 'Aldis', 'Noris', 'Harell', 'Merrow', 'Ostin', 'Calder', 'Seren', 'Brannock', 'Hollis', 'Wendle',
         'Garron', 'Ismay', 'Corvel', 'Tamber', 'Lusk', 'Ravel', 'Sorrow']
CITY_FIXED = ['Port Varen', 'Highmarch', 'Caer Dunmor', 'Westergate', 'Lindholm', 'Saltreach', 'Aldmark',
              'Kingsbridge', 'Marrowgate', 'Vellhaven', 'Stonecrown', 'Ashenmoor', 'Greywater', 'Redwall']


def _land_parts(g, land):
    parts = list(g['any'])
    for k in ('river', 'coast', 'hills', 'wood', 'marsh'):
        if k in land:
            parts += g[k] * 2                    # the land shows in the name more often than not
    return parts


def human(land, region, kind):
    if region == 'west':
        g = WEST
        root = pick(g['roots'])
        pre = pick(_land_parts(g, land))
        if kind in ('city', 'metropolis'):
            return f'Caer {root.capitalize()}' if random.random() < .5 or pre in ('Pen', 'Tre', 'Llan', 'Kil', 'Pol', 'Lis') \
                else pre + root
        if kind == 'town' and random.random() < .2:
            return f'{pre}{root} Cross'
        return f'{pre} {root.capitalize()}' if pre in ('Coed', 'Dun') and random.random() < .5 else pre + root
    g = NORTH if region == 'north' else HEART
    base = pick(g['a']) + pick(_land_parts(g, land))
    if kind in ('city', 'metropolis'):
        r = random.random()
        if 'coast' in land and r < .35:
            return 'Port ' + pick(PORTS)
        grand = ['King', 'Queen', 'High', 'Castle', 'Mark', 'Ald', 'Stone', 'Crown', 'Earl'] if region == 'heart' else \
            ['Jarls', 'Ravens', 'Konungs', 'High', 'Stone', 'Thing', 'Wolf']
        tail = ['march', 'gate', 'minster', 'hold', 'wall', 'reach'] if region == 'heart' else ['garth', 'gard', 'hall', 'holm', 'by']
        if 'river' in land and r < .6:
            tail = tail + ['bridge', 'bridge']
        if 'coast' in land:
            tail = tail + ['haven', 'reach']
        return pick(grand) + pick(tail)
    if region == 'heart':
        r = random.random()
        if kind == 'town' and r < .18:
            return 'Market ' + base
        if kind == 'town' and r < .3:
            return base + ' Cross'
        if kind in ('hamlet', 'village') and r < .1:
            return pick(['Little ', 'Great ', 'Nether ', 'Upper ']) + base
    return base


# ------------------------------------------------------------------ the other peoples
HALF_A = ['Apple', 'Barley', 'Bramble', 'Clover', 'Honey', 'Little', 'Mossy', 'Nether', 'Puddle', 'Tumble', 'Under',
          'Willow', 'Thistle', 'Button', 'Pipe', 'Hazel', 'Bywater', 'Crick', 'Frog', 'Goose', 'Hobble', 'Muddle',
          'Pickle', 'Plum', 'Sweet', 'Toad', 'Bracken', 'Dimble', 'Ferny']
HALF_B = ['bottom', 'burrow', 'combe', 'hollow', 'well', 'by', 'end', 'field', 'hithe', 'dell', 'brook', 'hill', 'wick',
          'cot', 'smial', 'stock', 'bank']


def halfling(land, kind):
    r = random.random()
    a = pick(HALF_A)
    if r < .12:
        return f'{a}-under-Hill'
    if r < .22:
        return f'Little {pick(["Tumbling", "Puddling", "Mudding", "Snoring", "Dimbling", "Pickling", "Nibbling"])}'
    if r < .3 and 'river' in land:
        return f'{a}-by-the-Water'
    if r < .36 and 'hills' in land:
        return f'{a}-on-the-Hill'
    return a + pick(HALF_B)


ELF_A = ['Ael', 'Ith', 'Syl', 'Cal', 'Mir', 'Orr', 'Lae', 'Ner', 'Thal', 'Eil', 'Lor', 'Gal', 'Ela']
ELF_M = ['', 'an', 'el', 'ir', 'or', 'en', 'ar']
ELF_B = ['vael', 'thiel', 'ond', 'dor', 'myr', 'ranth', 'mar', 'wen', 'ilas', 'oth', 'iel']
ELF_FIXED = ['Aelindor', 'Calemyr', 'Ithelmar', 'Sylvaranth', 'Orrenvael', 'Mirathiel']
GLADE_A = ['Moon', 'Star', 'Silver', 'Dawn', 'Dusk', 'Mist', 'Lantern', 'Whisper', 'Thistle', 'Fern', 'Birch', 'Dew',
           'Glimmer', 'Willow', 'Hush', 'Gleam', 'Night', 'Ever']
GLADE_B = ['water', 'light', 'fern', 'moss', 'leaf', 'song', 'shade', 'bloom', 'brook', 'wood']
GLADE_FIXED = ['Moonwater Glade', 'Thistlelight', 'Silverbirch Glade', 'Dawnfern', 'Starmoss Hollow', 'Whisperleaf',
               'Lanternwood', 'The Glade of Falling Stars']


def elf_city():
    return pick(ELF_A) + pick(ELF_M) + pick(ELF_B)


def glade():
    a, b = pick(GLADE_A), pick(GLADE_B)
    return a + b + pick([' Glade', ' Hollow', '', ' Dell', ' Glade'])


HOLD_A = ['Khaz', 'Karak', 'Dun', 'Zirak', 'Barak', 'Kar', 'Gund', 'Thrum', 'Ered', 'Bor', 'Azgal', 'Druk']
HOLD_B = ['Durim', 'Varn', 'Ithrand', 'Azul', 'Brodd', 'Kadrin', 'Ungor', 'Thorn', 'Grim', 'Bazar', 'Duran']
HOLD_C = ['dum', 'grund', 'thar', 'gard', 'kar', 'hund']
DEEP_FIXED = ['Khaz Durim', 'Karak Varn', 'Dun Ithrand', 'Barazgund', 'Erebkar', 'Gundholm', 'Zirak Thorn', 'Thrumgard Deep']
MINE_A = ['Stone', 'Iron', 'Copper', 'Anvil', 'Flint', 'Slate', 'Coal', 'Tin', 'Granite', 'Hammer', 'Pick', 'Ore',
          'Bellows', 'Ingot', 'Lode', 'Seam', 'Cinder', 'Basalt']
MINE_B = ['stead', 'holm', 'cleft', 'combe', 'barrow', 'brow', 'gate', 'by', 'thorpe', 'delve', 'shaft', 'deep', 'cut',
          'pit']


def hold():
    r = random.random()
    if r < .5:
        return f'{pick(HOLD_A)} {pick(HOLD_B)}'
    a, c = pick(HOLD_A), pick(HOLD_C)
    if a[-1] == c[0]:
        c = 'grund' if c != 'grund' else 'dum'
    return a + c if r < .85 else a + c + ' Deep'


def dwarf_village():
    return pick(MINE_A) + pick(MINE_B)


GNOME_A = ['Moss', 'Toad', 'Acorn', 'Fern', 'Hazel', 'Owl', 'Root', 'Beech', 'Bramble', 'Snail', 'Wren', 'Toadstool',
           'Burdock', 'Nettle', 'Thimble', 'Cobble', 'Puffball', 'Hedgehog', 'Sorrel']
GNOME_B = ['hame', 'dell', 'bottom', 'wick', ' Hollow', 'hame', 'burrow', 'stump', ' Dell']
GNOME_FIXED = ['Under-the-Oak', 'Old Beech Hollow', 'Under-the-Ash', 'Behind-the-Elder']


def gnome():
    return pick(GNOME_A) + pick(GNOME_B)


ORC_ADJ = ['Split', 'Red', 'Black', 'Broken', 'Bloody', 'Iron', 'Grinning', 'Burnt', 'Rotten', 'Howling', 'Bone']
ORC_N = ['Tusk', 'Hand', 'Skull', 'Fang', 'Axe', 'Jaw', 'Banner', 'Spear', 'Eye', 'Fist', 'Moon']
GOB_A = ['Rat', 'Snot', 'Grub', 'Knife', 'Stink', 'Nettle', 'Mud', 'Louse', 'Gob', 'Toad', 'Maggot', 'Snaggle', 'Scab',
         'Wart', 'Bog', 'Gristle']
GOB_B = ['gut', 'crack', 'cleft', 'hole', 'nose', 'tooth', 'rot']
KOB_A = ['Shiny', 'Tinkle', 'Glimmer', 'Glitter', 'Copper', 'Pebble', 'Sparkle', 'Twinkle', 'Bright', 'Gleam', 'Jingle',
         'Button', 'Brass']
KOB_B = ['dig', 'hole', 'burrow', 'mine', 'den', 'nook']
GNOLL_A = ['Bone', 'Blood', 'Carrion', 'Dust', 'Red', 'Yellow', 'Hyena', 'Crack', 'Gut', 'Marrow', 'Sun']
LIZ_A = ['Ss', 'Ix', 'Os', 'Th', 'Hss', 'Sk', 'Ish', 'Xa', 'Zs', 'Ka']
LIZ_B = ['la', 'ess', 'ath', 'ka', 'ssa', 'oss', 'ish', 'eth']
LIZ_C = ['ar', 'k', 'ss', 'aar', 'vael', 'ko', 'esh', 'ith']


def camp(kind):
    r = random.random()
    if kind == 'warcamp':
        a, n = pick(ORC_ADJ), pick(ORC_N)
        return f'The {a} {n} Camp' if r < .5 else f'Camp of the {a} {n}'
    if kind == 'ravine':
        a, b = pick(GOB_A), pick(GOB_B)
        if r < .35:
            return f'The {a}{b}'
        return f'{a}{b} {pick(["Gully", "Gulch", "Ravine", "Gorge"])}' if r < .75 else f'{a} {pick(["Gully", "Gulch"])}'
    if kind == 'kobolds':
        a = pick(KOB_A)
        return a + pick(KOB_B) if r < .7 else f'The {a} Caves'
    if kind == 'gnolls':
        a = pick(GNOLL_A)
        if r < .4:
            return f'The {a}-Laugh Pack'
        if r < .7:
            return f'{pick(["Red", "Yellow", "Dry", "Tall"])} Grass Camp'
        return f'The {a} Ring' if r < .85 else f'{a}pole Camp'
    if kind == 'stilts':
        nm = pick(LIZ_A) + pick(LIZ_B) + pick(LIZ_C)
        if r < .2:
            return f'{pick(["Ix", "Os", "Ish", "Xa"])}-{nm.capitalize()}'
        if r < .35:
            return f'{nm} {pick(["Vael", "Ko", "Ess", "Mire"])}'
        return nm
    return 'The Camp'


ORC_A = ['Gor', 'Ugh', 'Kar', 'Mog', 'Thra', 'Zug', 'Dur', 'Ruk', 'Nag', 'Bol', 'Skar', 'Grash', 'Ur', 'Lug']
ORC_B = ['mar', 'gash', 'thak', 'dush', 'zog', 'kul', 'rak', 'burz', 'grat', 'ok', 'nar', 'mosh']
ORC_C = ['', '', '', ' Stand', ' Ring', ' Hold', "'s Pit", ' Stakes']


def orc_town():
    """A half-orc town: a hard old name, sometimes with what it is."""
    return pick(ORC_A) + pick(ORC_B) + pick(ORC_C)


# ------------------------------------------------------------------ one name, never twice
def make(world, people, kind='village', land=(), region='heart'):
    """A new name for a place of this people and kind, fitting the land, not yet used in this world."""
    used = world.__dict__.setdefault('used_names', set())
    land = set(land)
    best = None
    for k in range(80):
        nm = _one(people, kind, land, region)
        if k < 40 and stem(nm) in {stem(u) for u in used}:
            continue                              # not three places in a row called Hof-something
        if nm in used or not fits(nm, land | ({'hills', 'wood', 'marsh', 'coast'} if people == 'halfling' else set())):
            continue
        best = nm
        break
    if best is None:                              # the grammar ran dry: number it rather than repeat
        base = _one(people, kind, land, region)
        best = next(f'{base} {r}' for r in ('Major', 'Minor', 'Over', 'Nether', 'Old', 'New') + tuple(map(str, range(2, 99)))
                    if f'{base} {r}' not in used)
    used.add(best)
    return best


SKIP = {'The', 'Port', 'Market', 'Caer', 'Camp', 'of', 'the', 'Little', 'Great', 'Upper', 'Nether', 'Coed', 'Dun'}


def stem(nm):
    """The first telling part of a name, to keep a world from naming three places Hof-something."""
    words = [w for w in nm.replace('-', ' ').split() if w not in SKIP] or [nm]
    return words[0][:4]


def _one(people, kind, land, region):
    fixed = random.random() < .12
    if people == 'elf':
        if kind == 'glade':
            return pick(GLADE_FIXED) if fixed else glade()
        return pick(ELF_FIXED) if fixed else elf_city()
    if people == 'dwarf':
        if kind in ('deephold', 'hold'):
            return pick(DEEP_FIXED) if fixed else hold()
        return dwarf_village()
    if people == 'gnome':
        return pick(GNOME_FIXED) if fixed and random.random() < .5 else gnome()
    if people == 'halfling':
        return halfling(land, kind)
    if people in ('warcamp', 'ravine', 'kobolds', 'gnolls', 'stilts'):
        return camp(people)
    if people == 'orc':
        return orc_town()
    if kind in ('city', 'metropolis') and fixed:
        return pick(CITY_FIXED)
    return human(land, region, kind)


def name_settlements(m, world):
    """Name every settlement but Thornfield, by its people and the land it lies in."""
    used = world.__dict__.setdefault('used_names', set())
    used.add('Thornfield')
    for s in world.settlements:
        if s.id == 0:
            continue
        land = land_at(m, s.x, s.y)
        if s.kind == 'deephold':
            s.name = make(world, 'dwarf', 'deephold', land)
        elif getattr(s, 'dwarven', False) or (s.race == 'dwarf' and not s.is_city):
            s.name = make(world, 'dwarf', 'village', land)
        elif getattr(s, 'elder', False):
            s.name = make(world, 'elf', 'city', land)
        elif s.race == 'halfling':
            s.name = make(world, 'halfling', s.kind, land)
        elif s.race == 'orc':
            s.name = make(world, 'orc', s.kind, land)
        elif s.race == 'dwarf':
            s.name = make(world, 'dwarf', 'hold', land)
        else:
            s.name = make(world, 'human', s.kind, land, dialect(m, s.x, s.y))
