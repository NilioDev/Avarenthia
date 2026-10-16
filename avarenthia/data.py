"""Static game data: tiles, classes, skills, items, monsters, dungeons."""


def hexrgb(h):
    if isinstance(h, tuple):
        return h
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# ---------------------------------------------------------------- tiles
(WALL, FLOOR, DOOR, ODOOR, DOWN, UP, WATER, GRASS, FOREST, MOUNTAIN, SWAMP, TOWN, ENTR, TREE, PATH, WELL, ROCK, ROAD, HILLS, SAND,
 CITY, FIELD, FENCE, TABLE, BED, STALL, FOUNTAIN, CASTLE, FORT, ANVIL, ALTAR, BARREL, PLANK, RIVER, SIGNPOST, SHALLOW, STATUE, CHEST, CHEST_OPEN, GRAVE, LAMP) = range(41)
BOAT = 41


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
    Tile('≈', '#4f9fe0', True, False, 'river (ford)', cost=24),
    Tile('┬', '#d0a060', False, False, 'signpost'),
    Tile('~', '#8cc0f0', True, False, 'shallow water', cost=14, bg='#173252'),
    Tile('ß', '#cfcac0', False, False, 'statue'),
    Tile('■', '#d8a040', False, False, 'treasure chest', bg='#2a1c0c'),
    Tile('□', '#8a7050', False, False, 'open chest'),
    Tile('┼', '#9a9aa0', False, False, 'gravestone'),
    Tile('Γ', '#8a7a60', False, False, 'lamp post'),
    Tile('◘', '#b08050', False, False, 'boat', bg='#173252'),
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
from .itemdata import (BASES, SLOTS, SLOTNAME, SLOTGLYPH, AFFIXES, AFFTXT, UNIQUES, SETS, GEAR_USERS, FAMILY_OF,  # noqa: E402,F401
                       UNDEAD, RES_CAP, RESISTS, ELEMENT_RES, SKILL_PREFIX, grades, SET_COLOR)
RARE_A = ['Doom', 'Grim', 'Blood', 'Storm', 'Bone', 'Dread', 'Shadow', 'Rune', 'Ghoul', 'Wraith', 'Plague', 'Ash', 'Iron', 'Gale']
RARE_B = ['Bite', 'Song', 'Shell', 'Visage', 'Loop', 'Mark', 'Edge', 'Ward', 'Brand', 'Coil', 'Fang', 'Call', 'Hide', 'Eye']
RARITY_COLOR = {'normal': hexrgb('#e6dfcf'), 'magic': hexrgb('#7f9bff'), 'rare': hexrgb('#efe065'), 'unique': hexrgb('#d9a547'),
                'set': hexrgb('#5fd27a')}
RARITY_MULT = {'normal': 1, 'magic': 2.5, 'rare': 5, 'unique': 8, 'set': 7}
# curses hidden on some magic and rare items: (stat, low, high), always negative
CURSES = [('life', 6, 18), ('str', 3, 8), ('dex', 3, 8), ('vit', 3, 7), ('ene', 3, 8), ('hit', 10, 30), ('ed', 10, 30),
          ('edef', 15, 40), ('crit', 2, 4), ('mana', 6, 15)]
CURSETXT = {'dmg_flat': '-{} damage', 'ed': '-{}% damage', 'edef': '-{}% defense', 'hit': '-{} to accuracy',
            'mana': '-{} to mana', 'life': '-{} to life', 'str': '-{} to Strength', 'dex': '-{} to Dexterity',
            'vit': '-{} to Vitality', 'ene': '-{} to Energy', 'crit': '-{}% critical strike chance', 'regen': '-{} life regeneration'}
POTIONS = {
    'hp': dict(name='Health Potion', col=hexrgb('#e04a3c'), val=18),
    'mp': dict(name='Mana Potion', col=hexrgb('#4f78ff'), val=18),
    'rejuv': dict(name='Rejuvenation Potion', col=hexrgb('#b45ae0'), val=60),
    'cure': dict(name='Antidote', col=hexrgb('#80d060'), val=20),
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
    'snagtooth': dict(ch='k', fg='#f0b040', name='Snagtooth the Kobold Chief', boss=True, lvl_fix=1, hp=2.0, dmg=.65, df=.8, xp=6,
                      tags=''),
    'ratking': dict(ch='R', fg='#e8b474', name='The Rat King', boss=True, lvl_fix=4, hp=6, dmg=1.2, df=1.2, xp=8, summon='rat', tags=''),
    'grolm': dict(ch='h', fg='#e8803c', name='Grolm the Digger', boss=True, lvl_fix=9, hp=6, dmg=1.4, df=1.3, xp=10, leap=True, tags=''),
    'lich': dict(ch='L', fg='#c486ff', name='Morvenna the Undying', boss=True, lvl_fix=14, hp=7, dmg=1.4, df=1.6, xp=15, caster=True, summon='skeleton', nova=True, tags='',
                 summon_msg='{name} beckons, and a skeleton claws its way out of the ground!', nova_msg='{name} unleashes a wave of grave-cold!',
                 bolt='bolt of darkness'),
    # the great evils of the world (only some appear in each game)
    'dragon': dict(ch='D', fg='#ff5a30', name='The Dragon', boss=True, lvl_fix=16, hp=8.5, dmg=1.6, df=1.7, xp=18, caster=True, nova=True,
                   summon='drake', tags='', summon_msg='{name} roars, and a drake answers the call!',
                   nova_msg='{name} breathes a torrent of fire!', bolt='gout of flame', nova_col=(255, 120, 40)),
    'broodmother': dict(ch='S', fg='#d080f0', name='The Brood Mother', boss=True, lvl_fix=12, hp=6.5, dmg=1.3, df=1.3, xp=14, poison=True,
                        summon='spider', fast=True, tags='', summon_msg='Eggs burst around {name}. More spiders!'),
    'warlord': dict(ch='O', fg='#ff6040', name='The Warlord', boss=True, lvl_fix=13, hp=7.5, dmg=1.7, df=1.5, xp=15, leap=True,
                    summon='goblin', tags='', summon_msg='{name} bellows, and a goblin rushes to his side!',
                    leap_msg='{name} charges at you with a war cry!'),
    'drowned_king': dict(ch='&', fg='#60d0b8', name='The Drowned King', boss=True, lvl_fix=14, hp=7, dmg=1.4, df=1.5, xp=15, caster=True,
                         nova=True, summon='drowned', tags='', summon_msg='Something wet crawls out of the dark water. A drowned one!',
                         nova_msg='{name} calls a wave of black water!', bolt='lance of brine', nova_col=(90, 200, 200)),
    'watchman': dict(ch='@', fg='#b8a888', name='Village Watchman', tags='', min_l=1, hp=.9, dmg=.8, df=.9, xp=.8),
    'huntsman': dict(ch='@', fg='#a0b070', name='Huntsman', tags='', min_l=1, hp=.8, dmg=.8, df=.9, xp=.9, ranged=True),
    'deputy': dict(ch='@', fg='#c8b070', name='Deputy', tags='', min_l=2, hp=1.1, dmg=1, df=1.1, xp=1.1),
    'sheriff': dict(ch='@', fg='#f0d060', name='Sheriff', tags='', min_l=3, hp=1.5, dmg=1.2, df=1.3, xp=1.6),
    'merchant': dict(ch='@', fg='#f0d080', name='Merchant', tags='', min_l=1, hp=.8, dmg=.6, df=.8, xp=.5),
    'drake': dict(ch='d', fg='#f08040', name='Fire Drake', tags='lair_dragon', min_l=6, hp=1.3, dmg=1.3, df=1.3, xp=1.8, fast=True),
    'drowned': dict(ch='z', fg='#70b0a0', name='Drowned One', tags='lair_drowned', min_l=4, hp=1.6, dmg=1.2, df=.8, xp=1.3, slow=True),
    'clansman': dict(ch='h', fg='#d8a070', name='Dwarf Clansman', tags='faction', min_l=3, hp=1.4, dmg=1.15, df=1.5, xp=1.4),
    'thunderer': dict(ch='h', fg='#b0b8c8', name='Dwarf Thunderer', tags='faction', min_l=4, hp=1.1, dmg=1.2, df=1.3, xp=1.5, ranged=True),
    # creatures of the elements, each at home in its own corner of the realm
    'salamander': dict(ch='S', fg='#ff7a2c', name='Salamander', tags='wild', min_l=4, hp=1.1, dmg=1.1, df=1.1, xp=1.4, elem='fire',
                       caster=True, bolt='spit of fire'),
    'ice_witch': dict(ch='@', fg='#a8e0ff', name='Ice Witch', tags='wild', min_l=5, hp=.9, dmg=1.15, df=1, xp=1.6, elem='cold',
                      caster=True, bolt='shard of ice', nova=True, nova_msg='{name} breathes out a blast of frost!',
                      nova_col=(159, 216, 255)),
    'storm_spirit': dict(ch='&', fg='#f2f07a', name='Storm Spirit', tags='wild', min_l=6, hp=1, dmg=1.2, df=1.5, xp=1.7, elem='lightning',
                         caster=True, fast=True, erratic=True, bolt='bolt of lightning'),
    'bog_lurker': dict(ch='B', fg='#7aa860', name='Bog Lurker', tags='wild', min_l=4, hp=1.6, dmg=1.1, df=.9, xp=1.4, elem='poison',
                       poison=True, slow=True),
}
# the families of round one (spiders, insects, goblinoids and the peoples below), from creatures.py
from . import creatures as _CR
for _k, _d in _CR.NEW.items():
    _d = dict(_d)
    _d['beh'] = frozenset(_d.get('beh', '').split())
    MONSTERS[_k] = _d
for _k in ('wolf_spider', 'web_weaver', 'trapdoor', 'spider_swarm', 'brood_spider', 'webkin', 'jumping_spider'):
    MONSTERS[_k]['tags'] += ' lair_spider'
for _k in ('kob_slinger', 'kob_trapper', 'kob_sorcerer'):
    MONSTERS[_k]['tags'] += ' lair_dragon'
for _k in ('goblin', 'gobarcher', 'kobold'):
    MONSTERS[_k]['tags'] += ' warren'
# what the elements do to each kind: resistances in percent (negative: a weakness), and the element of its attacks
for _k, _res in (('skeleton', dict(cold=25, poison=100, fire=-25)), ('skarcher', dict(cold=25, poison=100, fire=-25)),
                 ('zombie', dict(poison=100, fire=-25)), ('ghost', dict(cold=75, poison=100, lightning=25)),
                 ('wraith', dict(cold=50, poison=100, fire=-25)), ('lich', dict(cold=75, poison=100)),
                 ('drowned', dict(cold=50, lightning=-50, poison=50)), ('drowned_king', dict(cold=60, lightning=-50, poison=75)),
                 ('troll', dict(fire=-50, poison=50)), ('spider', dict(poison=100)), ('broodmother', dict(poison=100, fire=-25)),
                 ('drake', dict(fire=75, cold=-25)), ('dragon', dict(fire=75, cold=-25)), ('salamander', dict(fire=90, cold=-50)),
                 ('ice_witch', dict(cold=75, fire=-50)), ('storm_spirit', dict(lightning=90, poison=100)),
                 ('bog_lurker', dict(poison=75, fire=-25)), ('ogre', dict(cold=20)), ('bat', dict(lightning=-25)),
                 ('cultist', dict(fire=20)), ('druid', dict(fire=25, poison=25)), ('clansman', dict(fire=20)), ('thunderer', dict(fire=20))):
    MONSTERS[_k]['res'] = _res
for _k, _el in (('drake', 'fire'), ('dragon', 'fire'), ('cultist', 'fire'), ('druid', 'fire'), ('lich', 'cold'),
                ('drowned_king', 'cold'), ('ghost', 'cold'), ('wraith', 'cold'), ('spider', 'poison'), ('broodmother', 'poison')):
    MONSTERS[_k]['elem'] = _el
CLIMATE_MONSTERS = {'cold': ['ice_witch'], 'arid': ['salamander'], 'marsh': ['bog_lurker'], 'temperate': []}
ELEMENT_WORD = {'fire': 'fire', 'cold': 'cold', 'lightning': 'lightning', 'poison': 'poison'}
for _k, _extra in (('kobold', 'den'),
                   ('goblin', 'deep'), ('gobarcher', 'deep'), ('orc', 'deep'), ('troll', 'deep'), ('ogre', 'deep'),
                   ('spider', 'deep'), ('kobold', 'deep'), ('bat', 'deep'), ('kobold', 'lair_dragon'), ('spider', 'lair_spider'), ('bat', 'lair_spider'), ('orc', 'lair_orc'),
                   ('goblin', 'lair_orc'), ('gobarcher', 'lair_orc'), ('ogre', 'lair_orc'), ('zombie', 'lair_drowned'),
                   ('ghost', 'lair_drowned')):
    MONSTERS[_k]['tags'] += ' ' + _extra
for _m in MONSTERS.values():
    _m['fg'] = hexrgb(_m['fg'])
    for _k in ('boss', 'erratic', 'fast', 'ranged', 'poison', 'slow', 'caster', 'regen', 'leech', 'leap', 'nova'):
        _m.setdefault(_k, False)
    _m.setdefault('res', {})
    _m.setdefault('elem', None)
    _m.setdefault('summon', None)
    _m.setdefault('min_l', 1)
    _m.setdefault('chief', False)
    _m.setdefault('beh', frozenset())

CHIEFS = {_k for _k, _m in MONSTERS.items() if _m['chief']}

DUNGEONS = {
    'den': dict(name='The Hollow Den', depth=1, base=0, style='cave', tag='den', boss='snagtooth', wall=None),
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
    'hills': ['goblin', 'orc', 'ogre', 'wolf', 'troll', 'storm_spirit'],
    'coast': ['jackal', 'bandit', 'goblin', 'orc', 'storm_spirit'],
}
NIGHT_MONSTERS = ['zombie', 'ghost', 'wraith', 'skeleton', 'wolf'] + _CR.NIGHT_ADD
for _b, _ks in _CR.BIOME_ADD.items():
    BIOME_MONSTERS[_b] += _ks
for _c, _ks in _CR.CLIMATE_ADD.items():
    CLIMATE_MONSTERS[_c] = CLIMATE_MONSTERS.get(_c, []) + _ks
TOWN_A = ['Ash', 'Bram', 'Cold', 'Dun', 'Elm', 'Fen', 'Gold', 'Hollow', 'Iron', 'Kings', 'Mill', 'Oak', 'Raven',
          'Salt', 'Stone', 'Wolf', 'Wyn', 'Black', 'Red', 'Long', 'Briar', 'Marsh', 'Copper', 'Gull']
TOWN_B = ['ford', 'wick', 'haven', 'mere', 'stead', 'bury', 'dale', 'moor', 'gate', 'holm', 'ton', 'brook', 'hollow', 'cross']
CITY_NAMES = ['Port Varen', 'Highmarch', 'Caer Dunmor', 'Westergate', 'Lindholm', 'Saltreach', 'Aldmark', 'Kingsbridge', 'Marrowgate', 'Vellhaven']
SIDE_DUNGEONS = [('Howling Cave', 'cave', 'cave'), ('Sunken Chapel', 'rooms', 'crypt'), ('Old Barrow', 'rooms', 'crypt'),
                 ('Gloomhollow', 'cave', 'cave'), ('Drowned Halls', 'rooms', 'dungeon'), ('Wyrm Den', 'cave', 'cave'),
                 ('Bandit Hideout', 'rooms', 'dungeon'), ('Forgotten Delve', 'rooms', 'dungeon'),
                 ('Frostmaw Grotto', 'cave', 'cave'), ('Saltworn Vaults', 'rooms', 'dungeon'), ('Ashen Crypt', 'rooms', 'crypt'),
                 ('Weeping Mine', 'cave', 'cave')]
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
    'undead': dict(text='The dead rise from the graves around {town}. Arms and medicine are scarce.', good='arms', target=2,
                   also='medicine'),
}

MOUNTS = {
    'mule': dict(name='Pack Mule', price=15000, cap=60, desc='Carries 60 more units of cargo.'),
    'cart': dict(name='Mule Cart', price=50000, cap=160, desc='Carries 160 more units. Needs a pack mule.'),
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
                    'Ironhall', 'Thornkeep', 'Gallowmere', 'Redcliff', 'Kestrel Rock', 'Old Vigil', 'Harrowgate', 'Emberfall',
                    'Coldwater', 'Ravenhold', 'Bleakstone', 'Hawksreach', 'Duskwall', 'Grimhold', 'Stonecairn', 'Mirewatch']
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
    'salamander': ('A lizard as long as a man, its belly glowing like a forge.', 'Deserts, ash lands and the burning isles.',
                   'It spits fire and fears nothing hot. Frost and fire resistance win this fight.'),
    'ice_witch': ('A hag of the frozen north who breathes winter.', 'Tundra, taiga and the cold hills.',
                  'Her frost bites deep. Fire is her bane; cold barely touches her.'),
    'storm_spirit': ('A crackling shape of cloud and light that will not keep still.', 'High hills, cliffs and wild coasts.',
                     'Lightning is its blood. Steel and fire hurt it; storm magic does not.'),
    'bog_lurker': ('A heap of rot and reeds that rises out of the mire.', 'Swamps and marshes.',
                   'Its touch poisons. Burn it, and keep antidotes at hand.'),
}
# the three layers for the new kinds: how one looks, what they do (DOES), and their weakness and home
DOES = {}
for _k, _d in _CR.NEW.items():
    _look = min(_d['looks'], key=lambda t: ('{noun}' in t and bool(_d.get('nouns'))) + ('{sex}' in t))
    _look = _look.replace(' {noun}' if _d.get('nouns') else '{noun}', '' if _d.get('nouns') else _d.get('noun', ''))
    _p = ('she', 'her', 'her') if _d.get('gender') == 'f' else ('it', 'its', 'it')
    _look = _look.replace('{sex} ', '').format(he=_p[0], his=_p[1], him=_p[2])
    LORE[_k] = (_look, _d.get('home', 'Unknown.'), _d.get('weak', 'No advice yet.'))
    DOES[_k] = _d.get('does', '')
