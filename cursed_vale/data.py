"""Static game data: tiles, classes, skills, items, monsters, dungeons."""


def hexrgb(h):
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# ---------------------------------------------------------------- tiles
WALL, FLOOR, DOOR, ODOOR, DOWN, UP, WATER, GRASS, FOREST, MOUNTAIN, SWAMP, TOWN, ENTR, TREE, PATH, WELL, ROCK = range(17)


class Tile:
    __slots__ = ('ch', 'fg', 'walk', 'opaque', 'door', 'name')

    def __init__(self, ch, fg, walk, opaque, name, door=False):
        self.ch, self.fg, self.walk, self.opaque, self.name, self.door = ch, hexrgb(fg), walk, opaque, name, door


TILES = [
    Tile('#', '#8c8373', False, True, 'wall'),
    Tile('.', '#5f5a52', True, False, 'floor'),
    Tile('+', '#b8803c', False, True, 'closed door', door=True),
    Tile("'", '#b8803c', True, False, 'open door'),
    Tile('>', '#f0e8d2', True, False, 'stairs down'),
    Tile('<', '#f0e8d2', True, False, 'stairs up'),
    Tile('~', '#4682c8', False, False, 'water'),
    Tile('.', '#5f8c40', True, False, 'grass'),
    Tile('&', '#2f8040', True, False, 'forest'),
    Tile('^', '#a39c8e', False, True, 'mountains'),
    Tile('"', '#76843f', True, False, 'swamp'),
    Tile('#', '#f2c44a', True, False, 'Thornfield'),
    Tile('>', '#e8603e', True, False, 'dungeon entrance'),
    Tile('&', '#3c8c48', False, True, 'tree'),
    Tile('.', '#957148', True, False, 'path'),
    Tile('o', '#6aa2d8', False, False, 'well'),
    Tile('#', '#7a644e', False, True, 'rock'),
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
