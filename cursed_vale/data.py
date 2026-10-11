"""Static game data: tiles, classes, skills, items, monsters, dungeons."""


def hexrgb(h):
    if isinstance(h, tuple):
        return h
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# ---------------------------------------------------------------- tiles
(WALL, FLOOR, DOOR, ODOOR, DOWN, UP, WATER, GRASS, FOREST, MOUNTAIN, SWAMP, TOWN, ENTR, TREE, PATH, WELL, ROCK, ROAD, HILLS, SAND,
 CITY, FIELD, FENCE, TABLE, BED, STALL, FOUNTAIN, CASTLE, FORT, ANVIL, ALTAR, BARREL, PLANK) = range(33)


class Tile:
    __slots__ = ('ch', 'fg', 'walk', 'opaque', 'door', 'name', 'cost', 'bg')

    def __init__(self, ch, fg, walk, opaque, name, door=False, cost=10, bg=None):
        self.ch, self.fg, self.walk, self.opaque, self.name, self.door = ch, hexrgb(fg), walk, opaque, name, door
        self.cost = cost          # overworld travel time in turns per step
        self.bg = hexrgb(bg) if bg else None


TILES = [
    Tile('#', '#8c8373', False, True, 'wall'),
    Tile('.', '#5f5a52', True, False, 'floor'),
    Tile('+', '#b8803c', False, True, 'closed door', door=True),
    Tile("'", '#b8803c', True, False, 'open door'),
    Tile('>', '#f0e8d2', True, False, 'stairs down'),
    Tile('<', '#f0e8d2', True, False, 'stairs up'),
    Tile('≈', '#4682c8', False, False, 'water'),
    Tile('.', '#5f8c40', True, False, 'grassland', cost=10),
    Tile('♣', '#2f8040', True, False, 'forest', cost=14),
    Tile('▲', '#a39c8e', False, True, 'mountains'),
    Tile('"', '#76843f', True, False, 'swamp', cost=18),
    Tile('⌂', '#f2c44a', True, False, 'village', cost=10),
    Tile('>', '#e8603e', True, False, 'dungeon entrance', cost=10),
    Tile('♠', '#3c8c48', False, True, 'tree'),
    Tile('.', '#957148', True, False, 'path'),
    Tile('o', '#6aa2d8', False, False, 'well'),
    Tile('#', '#7a644e', False, True, 'rock'),
    Tile('·', '#c8a46a', True, False, 'road', cost=6, bg='#2a2116'),
    Tile('∩', '#9a8a5a', True, False, 'hills', cost=14),
    Tile('.', '#d8c47a', True, False, 'sand', cost=11),
    Tile('■', '#ffd860', True, False, 'city', cost=10),
    Tile('ⁿ', '#a8a050', True, False, 'field'),
    Tile('═', '#8a6a40', False, False, 'fence'),
    Tile('π', '#a07848', False, False, 'table'),
    Tile('≡', '#b06060', False, False, 'bed'),
    Tile('▬', '#d8a040', False, False, 'market stall'),
    Tile('○', '#6aa2d8', False, False, 'fountain'),
    Tile('Ω', '#e8e0d0', True, False, 'castle', cost=10),
    Tile('╬', '#d0c8b8', True, False, 'fort', cost=10),
    Tile('¥', '#9aa0aa', False, False, 'anvil'),
    Tile('±', '#e8d070', False, False, 'altar'),
    Tile('○', '#a07040', False, False, 'barrel'),
    Tile('.', '#8a6a44', True, False, 'wooden floor'),
]

# ---------------------------------------------------------------- classes and skills
CLASSES = {
    'barbarian': dict(name='Barbarian', str=30, dex=20, vit=25, ene=10, life_lvl=3, mana_lvl=1,
                      desc='Huge life pool. Cleaves through crowds, stuns with War Cry, leaps into the fray.'),
    'rogue': dict(name='Rogue', str=20, dex=30, vit=20, ene=15, life_lvl=2, mana_lvl=1.5,
                  desc='Fights at range with throwing knives. Damage scales with Dexterity.'),
    'sorceress': dict(name='Sorceress', str=10, dex=25, vit=15, ene=35, life_lvl=1.5, mana_lvl=2.5,
                      desc='Fragile but devastating. Firebolt, Frost Nova and Chain Lightning.'),
}
CLASS_ORDER = ['barbarian', 'rogue', 'sorceress']


class Skill:
    def __init__(self, sid, name, lvl, cost, desc):
        self.id, self.name, self.lvl, self.cost, self.desc = sid, name, lvl, cost, desc


SKILLS = {
    'barbarian': [
        Skill('cleave', 'Cleave', 1, 4, lambda r: f'Strike every adjacent enemy for {100 + r * 15}% weapon damage.'),
        Skill('warcry', 'War Cry', 3, 7, lambda r: f'Deal {6 + r * 5} damage to all enemies within 3 tiles and stun them for 2 turns.'),
        Skill('leap', 'Leap Attack', 6, 9, lambda r: f'Leap next to the nearest enemy (up to 6 tiles) and smash everything around you for {150 + r * 25}% weapon damage.'),
    ],
    'rogue': [
        Skill('knives', 'Throwing Knives', 1, 2, lambda r: f'Hurl a knife at the nearest enemy for {85 + r * 15}% weapon damage.'),
        Skill('fan', 'Fan of Blades', 3, 7, lambda r: f'Hit every enemy within 2 tiles for {70 + r * 15}% weapon damage.'),
        Skill('shadow', 'Shadow Step', 6, 8, lambda r: f'Step through the shadows next to an enemy up to 8 tiles away and strike for {200 + r * 30}% damage. Always critical.'),
    ],
    'sorceress': [
        Skill('firebolt', 'Firebolt', 1, 3, lambda r: f'Launch a bolt of fire at the nearest enemy for {3 + r * 3}-{7 + r * 4} damage, plus Energy/4.'),
        Skill('nova', 'Frost Nova', 3, 8, lambda r: f'Blast every enemy within 2 tiles for {2 + r * 2}-{5 + r * 3} damage, plus Energy/6, and freeze them for 3 turns.'),
        Skill('chain', 'Chain Lightning', 6, 12, lambda r: f'Lightning strikes the nearest enemy and arcs to {2 + r // 2} more for {5 + r * 4}-{11 + r * 5} damage, plus Energy/3.'),
    ],
}

# ---------------------------------------------------------------- items
BASES = {
    'dagger': dict(name='Dagger', slot='weapon', dmg=(1, 5), lvl=1, val=12, hit=10),
    'shortsword': dict(name='Short Sword', slot='weapon', dmg=(2, 6), lvl=1, val=20),
    'club': dict(name='Club', slot='weapon', dmg=(1, 8), lvl=1, val=15),
    'staff': dict(name='Gnarled Staff', slot='weapon', dmg=(2, 5), lvl=1, val=15, mana=10),
    'longsword': dict(name='Long Sword', slot='weapon', dmg=(3, 10), lvl=4, val=60),
    'mace': dict(name='Flanged Mace', slot='weapon', dmg=(4, 9), lvl=5, val=70),
    'warstaff': dict(name='War Staff', slot='weapon', dmg=(4, 11), lvl=7, val=120, mana=25),
    'waraxe': dict(name='War Axe', slot='weapon', dmg=(5, 14), lvl=7, val=110),
    'bastard': dict(name='Bastard Sword', slot='weapon', dmg=(7, 17), lvl=10, val=170),
    'runeblade': dict(name='Rune Blade', slot='weapon', dmg=(9, 22), lvl=13, val=250, hit=15),
    'cap': dict(name='Cap', slot='helm', arm=(2, 4), lvl=1, val=10),
    'skullcap': dict(name='Skull Cap', slot='helm', arm=(5, 8), lvl=4, val=35),
    'fullhelm': dict(name='Full Helm', slot='helm', arm=(9, 13), lvl=8, val=80),
    'greathelm': dict(name='Great Helm', slot='helm', arm=(14, 20), lvl=12, val=150),
    'quilted': dict(name='Quilted Armor', slot='armor', arm=(4, 7), lvl=1, val=15),
    'leather': dict(name='Leather Armor', slot='armor', arm=(8, 12), lvl=3, val=35),
    'ringmail': dict(name='Ring Mail', slot='armor', arm=(13, 19), lvl=5, val=70),
    'chainmail': dict(name='Chain Mail', slot='armor', arm=(19, 27), lvl=8, val=120),
    'platemail': dict(name='Plate Mail', slot='armor', arm=(29, 41), lvl=12, val=220),
    'shortbow': dict(name='Short Bow', slot='weapon', dmg=(2, 6), lvl=1, val=25, ranged=True),
    'longbow': dict(name='Long Bow', slot='weapon', dmg=(4, 11), lvl=5, val=80, ranged=True),
    'warbow': dict(name='War Bow', slot='weapon', dmg=(7, 17), lvl=10, val=170, ranged=True),
    'ring': dict(name='Ring', slot='ring', lvl=1, val=40, magic_only=True),
    'amulet': dict(name='Amulet', slot='amulet', lvl=3, val=60, magic_only=True),
}
SLOTS = ['weapon', 'helm', 'armor', 'ring', 'amulet']
SLOTNAME = {'weapon': 'Weapon', 'helm': 'Helm', 'armor': 'Armor', 'ring': 'Ring', 'amulet': 'Amulet'}
SLOTGLYPH = {'weapon': ')', 'armor': '[', 'helm': ']', 'ring': '=', 'amulet': '"'}

AFFIXES = [
    dict(stat='dmg_flat', pre=True, slots=['weapon'], tiers=[(1, 'Jagged', 1, 3), (5, 'Deadly', 3, 6), (10, 'Vicious', 6, 10)]),
    dict(stat='ed', pre=True, slots=['weapon'], tiers=[(1, 'Sharp', 15, 30), (5, 'Cruel', 30, 60), (10, 'Savage', 60, 100)]),
    dict(stat='edef', pre=True, slots=['armor', 'helm'], tiers=[(1, 'Sturdy', 15, 30), (5, 'Strong', 30, 60), (10, 'Glorious', 60, 100)]),
    dict(stat='hit', pre=True, slots=['weapon', 'ring', 'amulet', 'helm'], tiers=[(1, 'Bronze', 8, 15), (5, 'Iron', 15, 30), (10, 'Steel', 30, 50)]),
    dict(stat='mana', pre=True, slots=['helm', 'ring', 'amulet', 'weapon'], tiers=[(1, 'Lapis', 8, 15), (5, 'Cobalt', 15, 25), (10, 'Sapphire', 25, 40)]),
    dict(stat='life', pre=False, slots=['armor', 'helm', 'ring', 'amulet'], tiers=[(1, 'of the Jackal', 5, 10), (5, 'of the Fox', 10, 20), (10, 'of the Bear', 20, 35)]),
    dict(stat='str', pre=False, slots=SLOTS, tiers=[(1, 'of Strength', 2, 4), (6, 'of Might', 4, 8), (12, 'of the Titan', 8, 12)]),
    dict(stat='dex', pre=False, slots=SLOTS, tiers=[(1, 'of Dexterity', 2, 4), (6, 'of Skill', 4, 8), (12, 'of Precision', 8, 12)]),
    dict(stat='vit', pre=False, slots=SLOTS, tiers=[(1, 'of Vitality', 2, 4), (6, 'of Vigor', 4, 8), (12, 'of Life', 8, 12)]),
    dict(stat='ene', pre=False, slots=SLOTS, tiers=[(1, 'of Energy', 2, 4), (6, 'of the Mind', 4, 8), (12, 'of Wizardry', 8, 12)]),
    dict(stat='leech', pre=False, slots=['weapon', 'ring', 'amulet'], tiers=[(2, 'of the Leech', 2, 4), (8, 'of the Bat', 4, 7)]),
    dict(stat='crit', pre=False, slots=['weapon', 'ring', 'amulet', 'helm'], tiers=[(1, 'of Piercing', 2, 4), (7, 'of Slaying', 4, 8)]),
    dict(stat='regen', pre=False, slots=['armor', 'ring', 'amulet'], tiers=[(1, 'of Regeneration', 1, 1), (8, 'of Renewal', 2, 3)]),
]
AFFTXT = {
    'dmg_flat': '+{} damage', 'ed': '+{}% enhanced damage', 'edef': '+{}% enhanced defense',
    'hit': '+{} to accuracy', 'mana': '+{} to mana', 'life': '+{} to life', 'str': '+{} to Strength',
    'dex': '+{} to Dexterity', 'vit': '+{} to Vitality', 'ene': '+{} to Energy',
    'leech': '{}% of damage stolen as life', 'crit': '+{}% critical strike chance', 'regen': '+{} life regeneration',
}
UNIQUES = [
    dict(name='Gutripper', base='dagger', lvl=2, aff={'ed': 70, 'leech': 6, 'dex': 3}),
    dict(name='Ratcatcher', base='shortsword', lvl=3, aff={'ed': 60, 'dmg_flat': 3, 'hit': 25}, boss='ratking'),
    dict(name='Thornfield Aegis', base='quilted', lvl=2, aff={'edef': 100, 'life': 15, 'vit': 3}),
    dict(name='Crown of Ash', base='cap', lvl=4, aff={'life': 20, 'mana': 15, 'crit': 4}),
    dict(name='Hearthstone Loop', base='ring', lvl=5, aff={'life': 15, 'regen': 2, 'str': 4}),
    dict(name='Pale Moon Band', base='ring', lvl=7, aff={'mana': 30, 'ene': 8, 'crit': 5}),
    dict(name="Grolm's Splitter", base='waraxe', lvl=8, aff={'ed': 120, 'str': 8, 'crit': 8}, boss='grolm'),
    dict(name='Bonecaller', base='amulet', lvl=9, aff={'life': 30, 'leech': 5, 'vit': 6}),
    dict(name='Veil of the Undying', base='chainmail', lvl=11, aff={'edef': 150, 'life': 40, 'regen': 3}),
    dict(name='Stormherald', base='warstaff', lvl=10, aff={'ed': 80, 'mana': 40, 'ene': 10}),
]
RARE_A = ['Doom', 'Grim', 'Blood', 'Storm', 'Bone', 'Dread', 'Shadow', 'Rune', 'Ghoul', 'Wraith', 'Plague', 'Ash', 'Iron', 'Gale']
RARE_B = ['Bite', 'Song', 'Shell', 'Visage', 'Loop', 'Mark', 'Edge', 'Ward', 'Brand', 'Coil', 'Fang', 'Call', 'Hide', 'Eye']
RARITY_COLOR = {'normal': hexrgb('#e6dfcf'), 'magic': hexrgb('#7f9bff'), 'rare': hexrgb('#efe065'), 'unique': hexrgb('#d9a547')}
RARITY_MULT = {'normal': 1, 'magic': 2.5, 'rare': 5, 'unique': 8}
POTIONS = {
    'hp': dict(name='Health Potion', col=hexrgb('#e04a3c'), val=25),
    'mp': dict(name='Mana Potion', col=hexrgb('#4f78ff'), val=25),
    'rejuv': dict(name='Rejuvenation Potion', col=hexrgb('#b45ae0'), val=80),
}

# ---------------------------------------------------------------- monsters
MONSTERS = {
    'rat': dict(ch='r', fg='#b49c78', name='Giant Rat', tags='cave', min_l=1, hp=.55, dmg=.6, df=.6, xp=.6),
    'bat': dict(ch='b', fg='#9e8ebc', name='Cave Bat', tags='cave dungeon', min_l=1, hp=.5, dmg=.6, df=1.4, xp=.6, erratic=True, fast=True),
    'kobold': dict(ch='k', fg='#d4844c', name='Kobold', tags='cave dungeon', min_l=1, hp=.8, dmg=.8, df=.8, xp=.8),
    'goblin': dict(ch='g', fg='#7cb44c', name='Goblin', tags='cave dungeon wild', min_l=2, hp=.9, dmg=1, df=1, xp=1),
    'gobarcher': dict(ch='g', fg='#d0dc68', name='Goblin Archer', tags='cave dungeon', min_l=2, hp=.7, dmg=.8, df=1, xp=1.1, ranged=True),
    'jackal': dict(ch='C', fg='#cca452', name='Jackal', tags='wild', min_l=1, hp=.6, dmg=.7, df=1, xp=.7, fast=True),
    'wolf': dict(ch='C', fg='#acacac', name='Dire Wolf', tags='wild', min_l=3, hp=1, dmg=1, df=1.1, xp=1.1, fast=True),
    'bandit': dict(ch='@', fg='#d45c5c', name='Bandit', tags='wild', min_l=2, hp=1.1, dmg=1.1, df=1, xp=1.2),
    'brigand': dict(ch='@', fg='#e09060', name='Bandit Archer', tags='wild', min_l=3, hp=.8, dmg=.9, df=1, xp=1.2, ranged=True),
    'orc': dict(ch='o', fg='#6cae3c', name='Orc Brute', tags='dungeon cave', min_l=4, hp=1.3, dmg=1.2, df=1, xp=1.3),
    'spider': dict(ch='s', fg='#b46ed4', name='Venom Spider', tags='cave dungeon', min_l=4, hp=.9, dmg=.9, df=1.3, xp=1.2, poison=True, fast=True),
    'zombie': dict(ch='z', fg='#8eae8e', name='Zombie', tags='crypt dungeon', min_l=4, hp=1.8, dmg=1.3, df=.5, xp=1.2, slow=True),
    'skeleton': dict(ch='z', fg='#ece8dc', name='Skeleton', tags='crypt', min_l=5, hp=1, dmg=1, df=1.1, xp=1.1),
    'skarcher': dict(ch='z', fg='#c8d0ff', name='Skeleton Archer', tags='crypt', min_l=6, hp=.8, dmg=.9, df=1.1, xp=1.2, ranged=True),
    'ogre': dict(ch='O', fg='#c4a462', name='Ogre', tags='dungeon wild', min_l=7, hp=2, dmg=1.5, df=.8, xp=2),
    'cultist': dict(ch='@', fg='#d04898', name='Cultist', tags='crypt', min_l=7, hp=.9, dmg=1, df=1, xp=1.5, caster=True),
    'ghost': dict(ch='G', fg='#a4ccec', name='Ghost', tags='crypt', min_l=8, hp=1, dmg=1.05, df=1.8, xp=1.6, fast=True),
    'troll': dict(ch='T', fg='#4c8e6c', name='Cave Troll', tags='dungeon', min_l=8, hp=2.2, dmg=1.4, df=1, xp=2.2, regen=True),
    'wraith': dict(ch='W', fg='#7494a4', name='Wraith', tags='crypt', min_l=9, hp=1.6, dmg=1.3, df=1.4, xp=2.2, leech=True),
    'soldier': dict(ch='@', fg='#c8ccd8', name='Soldier', tags='faction', min_l=3, hp=1.2, dmg=1.1, df=1.2, xp=1.3),
    'crossbow': dict(ch='@', fg='#a8b8d0', name='Crossbowman', tags='faction', min_l=3, hp=.9, dmg=1, df=1, xp=1.3, ranged=True),
    'knight': dict(ch='K', fg='#e8e8f0', name='Knight', tags='faction', min_l=6, hp=2, dmg=1.4, df=1.8, xp=2.2),
    'mercenary': dict(ch='@', fg='#d8b070', name='Mercenary', tags='faction', min_l=3, hp=1.2, dmg=1.2, df=1.1, xp=1.3),
    'druid': dict(ch='@', fg='#70c060', name='Druid', tags='faction', min_l=4, hp=.9, dmg=1, df=1, xp=1.5, caster=True),
    'warden': dict(ch='@', fg='#58a050', name='Warden', tags='faction', min_l=3, hp=1, dmg=1, df=1.2, xp=1.3, ranged=True),
    'raider': dict(ch='@', fg='#c84040', name='Black Hand Raider', tags='faction', min_l=3, hp=1.1, dmg=1.2, df=1, xp=1.3),
    'robber_knight': dict(ch='K', fg='#a02828', name='Robber Knight', tags='faction', min_l=6, hp=2, dmg=1.5, df=1.6, xp=2.2),
    'ratking': dict(ch='R', fg='#e8b474', name='The Rat King', boss=True, lvl_fix=4, hp=6, dmg=1.2, df=1.2, xp=8, summon='rat', tags=''),
    'grolm': dict(ch='h', fg='#e8803c', name='Grolm the Digger', boss=True, lvl_fix=9, hp=6, dmg=1.4, df=1.3, xp=10, leap=True, tags=''),
    'lich': dict(ch='L', fg='#c486ff', name='Morvenna the Undying', boss=True, lvl_fix=14, hp=7, dmg=1.4, df=1.6, xp=15, caster=True, summon='skeleton', nova=True, tags=''),
}
for _m in MONSTERS.values():
    _m['fg'] = hexrgb(_m['fg'])
    for _k in ('boss', 'erratic', 'fast', 'ranged', 'poison', 'slow', 'caster', 'regen', 'leech', 'leap', 'nova'):
        _m.setdefault(_k, False)
    _m.setdefault('summon', None)
    _m.setdefault('min_l', 1)

DUNGEONS = {
    'rat': dict(name='The Rat Warrens', depth=3, base=0, style='cave', tag='cave', boss='ratking', wall=None),
    'mine': dict(name='The Lost Mine', depth=4, base=3, style='rooms', tag='dungeon', boss='grolm', wall=hexrgb('#a0835e')),
    'crypt': dict(name='Crypt of Morvenna', depth=5, base=7, style='rooms', tag='crypt', boss='lich', wall=hexrgb('#7e869c')),
}
DUNGEON_ORDER = ['rat', 'mine', 'crypt']
ELITE_MODS = ['Fast', 'Extra Strong', 'Stone Skin', 'Fire Enchanted', 'Vampiric']
UNIQUE_NAME = (['Gore', 'Bone', 'Blood', 'Grim', 'Rot', 'Ash', 'Venom', 'Dread', 'Skull', 'Black'],
               ['maw', 'fang', 'grinder', 'spawn', 'hide', 'gnaw', 'claw', 'tooth', 'heart'],
               ['the Wicked', 'the Cold', 'the Hungry', 'the Defiler', 'the Unclean', 'the Mad', 'the Hollow'])
CHAMPION_FG = hexrgb('#7a9cff')
UNIQUE_FG = hexrgb('#efc54e')

RUMORS = [
    'Champions glow blue. Unique monsters glow gold. Both carry better loot.',
    'Spiders poison you. A health potion cleanses the blood.',
    'Health orbs, those red stars, heal you when you step on them.',
    'They say Grolm the Digger never puts down his axe.',
    'Morvenna hurls bolts of darkness. Range will not save you.',
    'Dire wolves hunt in packs in the wilderness.',
    'Sister Ilse in the temple heals anyone, free of charge.',
    'Blue items have one or two magic properties, yellow ones many more.',
    'Shift + direction runs. X explores on its own until it spots trouble.',
]


# ---------------------------------------------------------------- trade goods
# base price in gold, weight per unit
GOODS = {
    'grain': dict(name='Grain', base=8, w=1),
    'fish': dict(name='Salted Fish', base=11, w=1),
    'timber': dict(name='Timber', base=12, w=3),
    'ore': dict(name='Iron Ore', base=14, w=3),
    'salt': dict(name='Salt', base=16, w=1),
    'ale': dict(name='Ale', base=15, w=2),
    'herbs': dict(name='Herbs', base=18, w=1),
    'furs': dict(name='Furs', base=28, w=1),
    'cloth': dict(name='Cloth', base=30, w=1),
    'tools': dict(name='Tools', base=40, w=2),
    'medicine': dict(name='Medicine', base=55, w=1),
    'arms': dict(name='Arms', base=65, w=2),
    'spice': dict(name='Spices', base=80, w=1),
    'gems': dict(name='Gems', base=120, w=1),
}
GOOD_ORDER = list(GOODS)

# what settlements in each biome tend to make and want
BIOME_TRADE = {
    'grass': (['grain', 'ale', 'cloth'], ['tools', 'salt', 'fish', 'medicine']),
    'forest': (['timber', 'furs', 'herbs'], ['grain', 'tools', 'ale', 'salt']),
    'swamp': (['herbs', 'fish'], ['grain', 'cloth', 'medicine', 'tools']),
    'hills': (['ore', 'gems', 'ale'], ['grain', 'cloth', 'timber', 'fish']),
    'coast': (['fish', 'salt', 'spice'], ['timber', 'grain', 'tools', 'furs']),
}
CITY_TRADE = (['tools', 'arms', 'cloth', 'medicine'], ['ore', 'timber', 'grain', 'furs', 'gems', 'herbs', 'spice'])

BIOME_NAMES = {
    'grass': ['Vale', 'Meadows', 'Downs', 'Fields'],
    'forest': ['Greywood', 'Elderwood', 'Thornwood', 'Wolfwood'],
    'swamp': ['Mirefen', 'Blackfen', 'Sumpmoor', 'Weeping Marsh'],
    'hills': ['Ironhills', 'Stonereach', 'Grimtor', 'Highfells'],
    'coast': ['Saltcoast', 'Gull Shore', 'Wrackstrand', 'Amber Coast'],
}
BIOME_MONSTERS = {
    'grass': ['jackal', 'wolf', 'bandit', 'goblin', 'ogre'],
    'forest': ['wolf', 'goblin', 'spider', 'ogre', 'troll'],
    'swamp': ['spider', 'zombie', 'goblin', 'ghost', 'wraith'],
    'hills': ['goblin', 'orc', 'ogre', 'wolf', 'troll'],
    'coast': ['jackal', 'bandit', 'goblin', 'orc'],
}
NIGHT_MONSTERS = ['zombie', 'ghost', 'wraith', 'skeleton', 'wolf']
TOWN_A = ['Ash', 'Bram', 'Cold', 'Dun', 'Elm', 'Fen', 'Gold', 'Hollow', 'Iron', 'Kings', 'Mill', 'Oak', 'Raven',
          'Salt', 'Stone', 'Wolf', 'Wyn', 'Black', 'Red', 'Long', 'Briar', 'Marsh', 'Copper', 'Gull']
TOWN_B = ['ford', 'wick', 'haven', 'mere', 'stead', 'bury', 'dale', 'moor', 'gate', 'holm', 'ton', 'brook', 'hollow', 'cross']
CITY_NAMES = ['Port Varen', 'Highmarch', 'Caer Dunmor', 'Westergate', 'Lindholm', 'Saltreach', 'Aldmark', 'Kingsbridge', 'Marrowgate', 'Vellhaven']
SIDE_DUNGEONS = [('Howling Cave', 'cave', 'cave'), ('Sunken Chapel', 'rooms', 'crypt'), ('Old Barrow', 'rooms', 'crypt'),
                 ('Gloomhollow', 'cave', 'cave'), ('Drowned Halls', 'rooms', 'dungeon'), ('Wyrm Den', 'cave', 'cave'),
                 ('Bandit Hideout', 'rooms', 'dungeon'), ('Forgotten Delve', 'rooms', 'dungeon')]
RELICS = ["Saint Edda's Reliquary", 'the Silver Chalice', 'the Moonstone Idol', 'the Lost Charter', 'the Gilded Censer',
          "the Old King's Signet", 'the Starmetal Ingot', 'the Book of Hours']
BANDIT_LEADERS = ['Black Hal', 'Red Maeve', 'One-Eyed Joss', 'Grisel the Knife', 'Old Corbin', 'Mad Ulric', 'Sable Tom']

EVENTS = {
    'famine': dict(text='Famine grips {town}. Grain is desperately needed.', good='grain', target=2),
    'harvest': dict(text='A bumper harvest in {town}. Grain is cheap there.', good='grain', target=180),
    'festival': dict(text='{town} holds its harvest festival. Ale is in demand.', good='ale', target=3),
    'plague': dict(text='Sickness spreads in {town}. Medicine and herbs fetch high prices.', good='medicine', target=2, also='herbs'),
    'collapse': dict(text='A mine collapsed near {town}. Iron ore is scarce.', good='ore', target=3),
    'war': dict(text='{town} arms its militia. Weapons sell for a fortune.', good='arms', target=2),
    'fire': dict(text='Fire destroyed half of {town}. Timber is needed for rebuilding.', good='timber', target=2),
}

MOUNTS = {
    'mule': dict(name='Pack Mule', price=150, cap=60, desc='Carries 60 more units of cargo.'),
    'cart': dict(name='Mule Cart', price=500, cap=160, desc='Carries 160 more units. Needs a pack mule.'),
}
BASE_CARGO = 30
DAY_LEN = 300


# ---------------------------------------------------------------- factions
FACTIONS = {
    'crown': dict(name='The Crown of Aldmark', short='Crown', fg='#e8d070', start=10, enemies=['blackhand', 'cult'],
                  troops=['soldier', 'soldier', 'crossbow', 'knight'], castle='Castle', fort='Watchfort',
                  desc='The old kingdom. Holds the heartland, its castles and most of its villages.'),
    'league': dict(name='The Merchant League', short='League', fg='#e8a050', start=5, enemies=['blackhand', 'cult'],
                   troops=['mercenary', 'mercenary', 'crossbow'], castle='Counting Keep', fort='Toll Fort',
                   desc='Rich trading cities that pay mercenaries to keep the roads open.'),
    'circle': dict(name='The Circle of Thorns', short='Circle', fg='#70c060', start=0, enemies=['cult', 'blackhand'],
                   troops=['warden', 'druid', 'wolf'], castle='Grove Hold', fort='Thornwatch',
                   desc='Druids and wardens of the deep woods and marshes. Distrust outsiders.'),
    'blackhand': dict(name='The Black Hand', short='Black Hand', fg='#d04040', start=-40, enemies=['crown', 'league', 'circle'],
                      troops=['raider', 'raider', 'brigand', 'robber_knight'], castle='Robber Keep', fort='Raider Fort',
                      desc='Robber knights and outlaws who tax the roads with steel.'),
    'cult': dict(name='The Cult of the Undying', short='Cult', fg='#b070ff', start=-100, enemies=['crown', 'league', 'circle', 'blackhand'],
                 troops=['cultist', 'skeleton', 'zombie', 'skarcher'], castle='Black Spire', fort='Bone Tower',
                 desc="Morvenna's servants. They raise the dead and answer to no one living."),
}
FACTION_ORDER = list(FACTIONS)
for _f in FACTIONS.values():
    _f['fg'] = hexrgb(_f['fg'])
STRONGHOLD_NAMES = ['Greymantle', 'Ravensward', 'Highkeep', 'Stormhold', 'Ashgard', 'Dunmere', 'Blackmoor', 'Wolfcrag',
                    'Ironhall', 'Thornkeep', 'Gallowmere', 'Redcliff', 'Kestrel Rock', 'Old Vigil']
START_STATS = dict(str=15, dex=15, vit=15, ene=15)
LEVEL_STAT_POINTS = 3


# ---------------------------------------------------------------- bestiary
# monster key -> (what it is, where it lives, a hunter's tip)
LORE = {
    'rat': ('Rats the size of dogs, grown fat on cellar grain and worse.', 'Caves, sewers and the Rat Warrens.',
            'Weak alone, dangerous in swarms. Fight them in corridors.'),
    'bat': ('Leathery wings, needle teeth, and no sense of direction.', 'Caves and old dungeons.',
            'They flit about at random. Let them come to you.'),
    'kobold': ('Small, scaly scavengers that worship anything shiny.', 'Caves and dungeons.',
               'Cowards at heart; kill the first and the rest falter.'),
    'goblin': ('Green-skinned raiders with crude blades and cruder manners.', 'Caves, dungeons and the wild hills.',
               'Goblins travel with archers. Close the distance fast.'),
    'gobarcher': ('A goblin with a bow and a surprising aim.', 'Caves and dungeons, behind other goblins.',
                  'Break line of sight around corners, then strike up close.'),
    'jackal': ('Lean scavengers of the open plains.', 'Grassland and desert, in packs.',
               'Fast but frail. A single good hit drops one.'),
    'wolf': ('Grey hunters as big as ponies, eyes like lamps in the dark.', 'Forests, hills and plains, worst at night.',
             'They are faster than you. Never run, stand and fight with your back to a wall.'),
    'bandit': ('Outlaws who decided the road owes them a living.', 'Along the roads and in hidden camps.',
               'Bandits carry gold. Their camps hold strongboxes.'),
    'brigand': ('A bandit who prefers to kill from a distance.', 'With bandit gangs.',
                'Kill the archers first; they will not stand in melee.'),
    'orc': ('Hulking brutes with iron jaws and iron cleavers.', 'Dungeons, caves and the far wilds.',
            'They hit hard but tire; armor pays for itself here.'),
    'spider': ('Bloated, hairy and dripping with venom.', 'Caves, swamps and forests.',
               'Their bite poisons. A health potion purges the venom.'),
    'zombie': ('The restless dead, slow and stubborn.', 'Crypts and graveyards, and the wilds at night.',
               'Slow as a funeral. Hit, step back, hit again.'),
    'skeleton': ('Bones bound together by old hate.', 'Crypts, and the open land when the moon is up.',
                 'Blunt and heavy blows serve best against bone.'),
    'skarcher': ('A skeleton that still remembers the bow.', 'Deep crypts.',
                 'Pin them in melee; their arrows fly true at range.'),
    'ogre': ('Twice the height of a man, three times the appetite.', 'Dungeons and remote hills.',
             'Slow to swing, deadly when it lands. Keep potions ready.'),
    'cultist': ("Morvenna's faithful, robed and chanting.", 'Crypts and dark places.',
                'Their bolts burn. Rush them before they finish the words.'),
    'ghost': ('A cold shape that drifts through stone and courage alike.', 'Crypts, ruins and haunted wilds at night.',
              'Hard to hit. Magic and steady accuracy win the day.'),
    'troll': ('Grey-green giants whose wounds close as you watch.', 'Deep caves, mountains and the far wilds.',
              'They regenerate. Burn them or never let up.'),
    'wraith': ('Hunger given shape, wrapped in shadow.', 'Deep crypts and the darkest wilds at night.',
               'They drink your life with every strike. End it quickly.'),
    'soldier': ('A trained soldier in the colours of a lord.', 'Strongholds and patrols.',
                'Disciplined, armored. Fight them one at a time.'),
    'crossbow': ('A soldier with a heavy crossbow.', 'Castle walls and patrols.', 'Slow to reload. Charge after the shot.'),
    'knight': ('A mounted noble in full plate.', 'Castles and warbands.', 'Very tough. Weaken or burn them first.'),
    'mercenary': ('Sellsword of the Merchant League.', 'League forts and caravans.', 'Loyal only to coin.'),
    'druid': ('A keeper of the old groves who calls down fire.', 'Circle groves and forests.',
              'Spellcasters fall quickly once you reach them.'),
    'warden': ('A Circle ranger, quiet and deadly with a bow.', 'Forests and Circle holds.',
               'Use trees and walls to break their line of fire.'),
    'raider': ('A Black Hand cutthroat.', 'Black Hand forts, toll roads and raids.', 'They come in numbers. Do not get surrounded.'),
    'robber_knight': ('A fallen knight who leads the Black Hand.', 'Black Hand strongholds.', 'Armored and cruel. Bring potions.'),
    'ratking': ('A writhing mass of rats fused into one hateful king.', 'The bottom of the Rat Warrens.',
                'He calls more rats. Kill him fast, then the brood.'),
    'grolm': ('An exiled dwarf who dug too deep and found madness.', 'The bottom of the Lost Mine.',
              'He leaps across the room at you. Keep your guard up.'),
    'lich': ('Morvenna the Undying, author of the curse.', 'The bottom of her crypt.',
             'Her bolts and frost waves strike from anywhere. Close in and do not stop.'),
}
