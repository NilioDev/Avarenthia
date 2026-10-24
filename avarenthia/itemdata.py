"""Gear, in the manner of the old Diablo II: ten slots, base items in three grades (normal, exceptional and elite)
with Strength and Dexterity needs, a wide pool of prefixes and suffixes in tiers with ranges, uniques whose powers
roll within a range, small sets bound to the places and peoples of the realm, and loot tables per kind of enemy.

There are no sockets, gems or runewords, and no weapon swap: what you carry is what you fight with."""


def _rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ------------------------------------------------------------------ slots
# the places on your body; a ring item goes on either hand
SLOTS = ['weapon', 'shield', 'helm', 'amulet', 'armor', 'gloves', 'belt', 'boots', 'ring1', 'ring2']
SLOTNAME = {'weapon': 'Weapon', 'shield': 'Off-hand', 'helm': 'Helm', 'armor': 'Armor', 'ring': 'Ring', 'ring1': 'Ring',
            'ring2': 'Ring', 'amulet': 'Amulet', 'gloves': 'Gloves', 'belt': 'Belt', 'boots': 'Boots'}
SLOTGLYPH = {'weapon': ')', 'shield': '(', 'armor': '[', 'helm': ']', 'ring': '=', 'amulet': '"', 'gloves': '[',
             'belt': '-', 'boots': '['}
GRADES = ['normal', 'exceptional', 'elite']
GRADE_STEP = (0, 9, 18)            # levels added by each grade
GRADE_MULT = (1, 1.7, 2.5)         # damage and armor
GRADE_VAL = (1, 3, 8)

# ------------------------------------------------------------------ base items
# key: (slot, three names, level, damage or armor, value, (Strength, Dexterity) need weights, extras)
# the first key is the normal grade; '<key>_x' is exceptional and '<key>_e' elite
FAMILIES = {
    # one-handed weapons
    'dagger': ('weapon', ('Dagger', 'Rondel', 'Fang Dagger'), 1, (2, 7), 12, (0, 1), dict(hit=10)),
    'shortsword': ('weapon', ('Short Sword', 'Falchion', 'Varnish Gladius'), 1, (2, 6), 20, (.8, .4), {}),
    'club': ('weapon', ('Club', 'Cudgel', 'Truncheon'), 1, (1, 8), 15, (.8, 0), {}),
    'longsword': ('weapon', ('Long Sword', 'War Sword', 'Rune Sword'), 4, (3, 10), 60, (.9, .5), {}),
    'mace': ('weapon', ('Flanged Mace', 'Morning Star', 'Devil Star'), 5, (4, 9), 70, (1, 0), {}),
    'waraxe': ('weapon', ('War Axe', 'Bearded Axe', 'Berserker Axe'), 7, (5, 14), 110, (1, 0), {}),
    'bastard': ('weapon', ('Bastard Sword', 'Espadon', 'Champion Sword'), 10, (7, 17), 170, (1.1, .3), {}),
    'runeblade': ('weapon', ('Rune Blade', 'Elder Blade', 'Phase Blade'), 13, (9, 22), 250, (.9, .7), dict(hit=15)),
    'scimitar': ('weapon', ('Scimitar', 'Shamshir', 'Talwar'), 3, (3, 8), 50, (.6, .6), {}),
    'flail': ('weapon', ('Flail', 'Knout', 'Scourge'), 6, (3, 12), 90, (1.1, 0), {}),
    'warhammer': ('weapon', ('War Hammer', 'Battle Hammer', 'Rune Hammer'), 9, (6, 13), 140, (1.3, 0), {}),
    'spear': ('weapon', ('Spear', 'War Spear', 'Varnish Pilum'), 2, (2, 8), 30, (.7, .3), dict(reach=True)),
    'throwknives': ('weapon', ('Throwing Knives', 'Balanced Knives', 'Wind Knives'), 2, (2, 6), 30, (0, .8),
                    dict(ranged=True)),
    'sling': ('weapon', ('Sling', 'Braided Sling', 'Giant Sling'), 1, (1, 5), 8, (0, .4), dict(ranged=True)),
    # two-handed weapons: the off-hand stays empty
    'staff': ('weapon', ('Gnarled Staff', 'Rune Staff', 'Elder Staff'), 1, (2, 5), 15, (.5, 0), dict(mana=10, two=True, reach=True)),
    'warstaff': ('weapon', ('War Staff', 'Battle Staff', 'Archon Staff'), 7, (4, 11), 120, (.6, 0), dict(mana=25, two=True, reach=True)),
    'greatsword': ('weapon', ('Greatsword', 'Flamberge', 'Colossus Blade'), 6, (6, 16), 120, (1.3, .3), dict(two=True)),
    'greataxe': ('weapon', ('Great Axe', 'Executioner Axe', 'Doom Axe'), 9, (8, 22), 160, (1.4, 0), dict(two=True)),
    'maul': ('weapon', ('Maul', 'Great Maul', 'Thunder Maul'), 12, (10, 26), 210, (1.6, 0), dict(two=True)),
    'halberd': ('weapon', ('Halberd', 'Poleaxe', 'Great Glaive'), 8, (6, 18), 140, (1.2, .2), dict(two=True, reach=True)),
    'scythe': ('weapon', ('War Scythe', 'Grim Scythe', 'Reaper'), 6, (4, 14), 100, (1, .3), dict(two=True, reach=True)),
    'lightxbow': ('weapon', ('Light Crossbow', 'Hunting Crossbow', 'Rune Crossbow'), 3, (4, 10), 60, (.5, .2),
                  dict(ranged=True, two=True)),
    'heavyxbow': ('weapon', ('Heavy Crossbow', 'Arbalest', 'Siege Arbalest'), 9, (8, 20), 160, (.9, .3),
                  dict(ranged=True, two=True)),
    'shortbow': ('weapon', ('Short Bow', 'Edge Bow', 'Spider Bow'), 1, (2, 6), 25, (0, 1), dict(ranged=True, two=True)),
    'longbow': ('weapon', ('Long Bow', 'Rune Bow', 'Shadow Bow'), 5, (4, 11), 80, (.3, 1), dict(ranged=True, two=True)),
    'warbow': ('weapon', ('War Bow', 'Gothic Bow', 'Ward Bow'), 10, (7, 17), 170, (.4, 1.1), dict(ranged=True, two=True)),
    # helms
    'cap': ('helm', ('Cap', 'War Hat', 'Shako'), 1, (2, 4), 10, (0, 0), {}),
    'circlet': ('helm', ('Circlet', 'Coronet', 'Diadem'), 6, (3, 6), 60, (0, 0), dict(mana=12)),
    'skullcap': ('helm', ('Skull Cap', 'Sallet', 'Armet'), 4, (5, 8), 35, (.5, 0), {}),
    'fullhelm': ('helm', ('Full Helm', 'Basinet', 'Spired Helm'), 8, (9, 13), 80, (.8, 0), {}),
    'greathelm': ('helm', ('Great Helm', 'Winged Helm', 'Guardian Crown'), 12, (14, 20), 150, (1, 0), {}),
    # body armor
    'quilted': ('armor', ('Quilted Armor', 'Ghost Armor', 'Dusk Shroud'), 1, (4, 7), 15, (.3, 0), {}),
    'leather': ('armor', ('Leather Armor', 'Serpentskin Armor', 'Wyrmhide'), 3, (8, 12), 35, (.4, 0), {}),
    'ringmail': ('armor', ('Ring Mail', 'Linked Mail', 'Diamond Mail'), 5, (13, 19), 70, (.7, 0), {}),
    'chainmail': ('armor', ('Chain Mail', 'Mesh Armor', 'Boneweave'), 8, (19, 27), 120, (.9, 0), {}),
    'platemail': ('armor', ('Plate Mail', 'Gothic Plate', 'Lacquered Plate'), 12, (29, 41), 220, (1.2, 0), {}),
    # off-hand: shields, and grimoires for those who fight with magic
    'buckler': ('shield', ('Buckler', 'Defender', 'Heater'), 1, (3, 5), 12, (.4, 0), {}),
    'roundshield': ('shield', ('Round Shield', 'Grim Shield', 'Luna'), 4, (6, 9), 40, (.6, 0), {}),
    'kiteshield': ('shield', ('Kite Shield', 'Dragon Shield', 'Hyperion'), 8, (10, 15), 90, (.9, 0), {}),
    'towershield': ('shield', ('Tower Shield', 'Pavise', 'Aegis'), 12, (16, 22), 170, (1.2, 0), {}),
    'grimoire': ('shield', ('Grimoire', 'Codex', 'Varnish Codex'), 3, None, 50, (0, 0), dict(mana=15)),
    # hands, waist and feet
    'gloves': ('gloves', ('Leather Gloves', 'Demonhide Gloves', 'Bramble Mitts'), 1, (1, 3), 10, (0, 0), {}),
    'hgloves': ('gloves', ('Heavy Gloves', 'Sharkskin Gloves', 'Vampirebone Gloves'), 4, (2, 4), 25, (.3, 0), {}),
    'gauntlets': ('gloves', ('Gauntlets', 'War Gauntlets', 'Ogre Gauntlets'), 10, (4, 7), 70, (.8, 0), {}),
    # fist weapons: worn on the hands, they strike while the weapon hand is empty (Unarmed)
    'cestus': ('gloves', ('Cestus', 'Spiked Cestus', 'Ironbound Cestus'), 2, (1, 2), 30, (.8, 0), dict(fist=(2, 6))),
    'claws': ('gloves', ('Tiger Claws', 'Bagh Nakh', 'Wyrm Claws'), 4, (1, 2), 45, (0, .8), dict(fist=(2, 7))),
    'sash': ('belt', ('Sash', 'Demonhide Sash', 'Spiderweb Sash'), 1, (1, 2), 10, (0, 0), {}),
    'belt': ('belt', ('Belt', 'Mesh Belt', 'Mithril Coil'), 5, (3, 5), 35, (.4, 0), {}),
    'platedbelt': ('belt', ('Plated Belt', 'War Belt', 'Colossus Girdle'), 10, (5, 8), 80, (.8, 0), {}),
    'boots': ('boots', ('Boots', 'Demonhide Boots', 'Wyrmhide Boots'), 1, (1, 3), 10, (0, 0), {}),
    'hboots': ('boots', ('Heavy Boots', 'Sharkskin Boots', 'Scarabshell Boots'), 4, (3, 5), 25, (.3, 0), {}),
    'greaves': ('boots', ('Greaves', 'War Boots', 'Myrmidon Greaves'), 10, (6, 9), 75, (.8, 0), {}),
}

BASES = {}
FAMILY_OF = {}
for _k, (_slot, _names, _lvl, _stat, _val, (_ws, _wd), _ex) in FAMILIES.items():
    for _g in range(3):
        key = _k if _g == 0 else _k + ('_x' if _g == 1 else '_e')
        lvl = _lvl + GRADE_STEP[_g]
        b = dict(name=_names[_g], slot=_slot, lvl=lvl, val=round(_val * GRADE_VAL[_g]), grade=GRADES[_g], family=_k,
                 rstr=round(_ws * (8 + lvl * 2.2)), rdex=round(_wd * (8 + lvl * 2.2)))
        if _stat:
            lo, hi = round(_stat[0] * GRADE_MULT[_g]), round(_stat[1] * GRADE_MULT[_g])
            b['dmg' if _slot == 'weapon' else 'arm'] = (lo, hi)
        for _ek, _ev in _ex.items():
            if isinstance(_ev, tuple):
                _ev = tuple(round(v * GRADE_MULT[_g]) for v in _ev)
            b[_ek] = round(_ev * GRADE_MULT[_g]) if isinstance(_ev, (int, float)) and not isinstance(_ev, bool) else _ev
        BASES[key] = b
        FAMILY_OF[key] = _k
BASES['ring'] = dict(name='Ring', slot='ring', lvl=1, val=40, magic_only=True, grade='normal', family='ring', rstr=0, rdex=0)
BASES['amulet'] = dict(name='Amulet', slot='amulet', lvl=3, val=60, magic_only=True, grade='normal', family='amulet', rstr=0, rdex=0)
FAMILY_OF['ring'], FAMILY_OF['amulet'] = 'ring', 'amulet'


def grades(family):
    """The base keys of a family, normal first."""
    if family in ('ring', 'amulet'):
        return [family]
    return [family, family + '_x', family + '_e']


# ------------------------------------------------------------------ affixes
WEAPON = ['weapon']
ARMOUR = ['armor', 'helm', 'shield', 'gloves', 'belt', 'boots']
JEWEL = ['ring', 'amulet']
ALL = ['weapon', 'shield', 'helm', 'armor', 'gloves', 'belt', 'boots', 'ring', 'amulet']

# each: stat, prefix?, slots, tiers [(item level, name, low, high)]
AFFIXES = [
    # ---- prefixes
    dict(stat='dmg_flat', pre=True, slots=WEAPON + ['gloves'],
         tiers=[(1, 'Jagged', 1, 3), (5, 'Deadly', 3, 6), (10, 'Vicious', 6, 10), (17, 'Brutal', 10, 16), (25, 'Merciless', 16, 24)]),
    dict(stat='ed', pre=True, slots=WEAPON,
         tiers=[(1, 'Sharp', 15, 30), (6, 'Cruel', 30, 60), (12, 'Savage', 60, 100), (20, 'Ruthless', 100, 150), (28, 'Wrathful', 150, 200)]),
    dict(stat='edef', pre=True, slots=ARMOUR,
         tiers=[(1, 'Sturdy', 15, 30), (5, 'Strong', 30, 60), (11, 'Glorious', 60, 100), (18, 'Blessed', 100, 140), (27, 'Godly', 140, 200)]),
    dict(stat='hit', pre=True, slots=WEAPON + JEWEL + ['helm', 'gloves'],
         tiers=[(1, 'Bronze', 8, 15), (5, 'Iron', 15, 30), (10, 'Steel', 30, 50), (18, 'Silver', 50, 80), (26, 'Starmetal', 80, 120)]),
    dict(stat='mana', pre=True, slots=['helm', 'shield', 'weapon'] + JEWEL,
         tiers=[(1, 'Lapis', 8, 15), (5, 'Cobalt', 15, 25), (11, 'Sapphire', 25, 40), (20, 'Azure', 40, 60)]),
    dict(stat='res_fire', pre=True, slots=ARMOUR + JEWEL,
         tiers=[(1, 'Ruddy', 5, 10), (6, 'Crimson', 11, 20), (14, 'Scarlet', 21, 30), (24, 'Emberward', 31, 40)]),
    dict(stat='res_cold', pre=True, slots=ARMOUR + JEWEL,
         tiers=[(1, 'Hoary', 5, 10), (6, 'Rimed', 11, 20), (14, 'Wintry', 21, 30), (24, 'Wintersworn', 31, 40)]),
    dict(stat='res_light', pre=True, slots=ARMOUR + JEWEL,
         tiers=[(1, 'Lined', 5, 10), (6, 'Insulated', 11, 20), (14, 'Grounded', 21, 30), (24, 'Stormproof', 31, 40)]),
    dict(stat='res_poison', pre=True, slots=ARMOUR + JEWEL,
         tiers=[(1, 'Beryl', 5, 10), (6, 'Jade', 11, 20), (14, 'Verdant', 21, 30), (24, 'Viperhide', 31, 40)]),
    dict(stat='res_all', pre=True, slots=['armor', 'shield', 'amulet', 'ring'],
         tiers=[(8, 'Prismatic', 4, 8), (16, 'Warding', 8, 15), (26, 'Varnish-warded', 15, 22)]),
    dict(stat='fire_dmg', pre=True, slots=WEAPON + ['gloves', 'ring'],
         tiers=[(3, 'Smoldering', 1, 4), (9, 'Burning', 3, 8), (18, 'Blazing', 6, 14), (27, 'Infernal', 12, 24)]),
    dict(stat='cold_dmg', pre=True, slots=WEAPON + ['gloves', 'ring'],
         tiers=[(3, 'Chilling', 1, 3), (9, 'Freezing', 3, 7), (18, 'Frozen', 6, 12), (27, 'Hibernal', 10, 20)]),
    dict(stat='light_dmg', pre=True, slots=WEAPON + ['gloves', 'ring'],
         tiers=[(3, 'Sparking', 1, 6), (9, 'Arcing', 2, 12), (18, 'Thundering', 4, 22), (27, 'Tempest', 8, 36)]),
    dict(stat='skill', pre=True, slots=['amulet', 'helm', 'weapon', 'shield', 'gloves'],
         tiers=[(8, '', 1, 1), (22, '', 1, 2)]),
    # ---- suffixes
    dict(stat='life', pre=False, slots=['armor', 'helm', 'shield', 'belt'] + JEWEL,
         tiers=[(1, 'of the Jackal', 5, 10), (5, 'of the Fox', 10, 20), (11, 'of the Bear', 20, 35), (20, 'of the Whale', 35, 55),
                (28, 'of the Colossus', 55, 80)]),
    dict(stat='str', pre=False, slots=ALL,
         tiers=[(1, 'of Strength', 2, 4), (6, 'of Might', 4, 8), (12, 'of the Titan', 8, 12), (20, 'of the Mountain', 12, 18)]),
    dict(stat='dex', pre=False, slots=ALL,
         tiers=[(1, 'of Dexterity', 2, 4), (6, 'of Skill', 4, 8), (12, 'of Precision', 8, 12), (20, 'of the Hawk', 12, 18)]),
    dict(stat='vit', pre=False, slots=ALL,
         tiers=[(1, 'of Vitality', 2, 4), (6, 'of Vigor', 4, 8), (12, 'of Life', 8, 12), (20, 'of the Oak', 12, 18)]),
    dict(stat='ene', pre=False, slots=ALL,
         tiers=[(1, 'of Energy', 2, 4), (6, 'of the Mind', 4, 8), (12, 'of Wizardry', 8, 12), (20, 'of the Magus', 12, 18)]),
    dict(stat='leech', pre=False, slots=WEAPON + JEWEL + ['gloves'],
         tiers=[(2, 'of the Leech', 2, 4), (8, 'of the Bat', 4, 7), (18, 'of the Vampire', 7, 10)]),
    dict(stat='crit', pre=False, slots=WEAPON + JEWEL + ['helm', 'gloves'],
         tiers=[(1, 'of Piercing', 2, 4), (7, 'of Slaying', 4, 8), (18, 'of Butchery', 8, 12)]),
    dict(stat='regen', pre=False, slots=['armor', 'belt'] + JEWEL,
         tiers=[(1, 'of Regeneration', 1, 1), (8, 'of Renewal', 2, 3), (18, 'of the Troll', 3, 5)]),
    dict(stat='sight', pre=False, slots=['helm'] + JEWEL, tiers=[(2, 'of Light', 1, 1), (10, 'of the Sun', 2, 2)]),
    dict(stat='undead', pre=False, slots=WEAPON, tiers=[(3, 'of the Dawn', 25, 50), (12, 'of Sanctity', 50, 100)]),
    dict(stat='thorns', pre=False, slots=['armor', 'shield', 'belt'],
         tiers=[(3, 'of Thorns', 2, 5), (11, 'of Spikes', 5, 12), (22, 'of Bramble', 12, 24)]),
    dict(stat='lpk', pre=False, slots=WEAPON + ['gloves', 'ring'], tiers=[(4, 'of Carrion', 1, 3), (14, 'of the Vulture', 3, 6)]),
    dict(stat='mpk', pre=False, slots=WEAPON + ['helm', 'ring', 'amulet'], tiers=[(4, 'of Echoes', 1, 3), (14, 'of the Wraith', 3, 6)]),
    dict(stat='mf', pre=False, slots=['ring', 'amulet', 'boots', 'gloves', 'helm'],
         tiers=[(4, 'of Fortune', 5, 15), (14, 'of Luck', 15, 25), (24, 'of Providence', 25, 35)]),
    dict(stat='dr', pre=False, slots=['armor', 'shield', 'belt'], tiers=[(10, 'of the Bulwark', 2, 4), (22, 'of the Fortress', 4, 7)]),
]

# +1 to a discipline: the prefix is named after the discipline
SKILL_PREFIX = {'fire': "Kindler's", 'frost': "Rimewright's", 'storm': "Stormcaller's", 'restoration': "Healer's",
                'shadow': "Shade's", 'warcraft': "Warlord's", 'swords': "Blademaster's", 'axes': "Axeman's",
                'daggers': "Cutthroat's", 'archery': "Fletcher's", 'unarmed': "Brawler's", 'spears': "Pikeman's"}

AFFTXT = {
    'dmg_flat': '+{} damage', 'ed': '+{}% enhanced damage', 'edef': '+{}% enhanced defense',
    'hit': '+{} to accuracy', 'mana': '+{} to mana', 'life': '+{} to life', 'str': '+{} to Strength',
    'dex': '+{} to Dexterity', 'vit': '+{} to Vitality', 'ene': '+{} to Energy',
    'leech': '{}% of damage stolen as life', 'crit': '+{}% critical strike chance', 'regen': '+{} life regeneration',
    'res_fire': 'Fire resistance +{}%', 'res_cold': 'Cold resistance +{}%', 'res_light': 'Lightning resistance +{}%',
    'res_poison': 'Poison resistance +{}%', 'res_all': 'All resistances +{}%',
    'fire_dmg': '+{} fire damage', 'cold_dmg': '+{} cold damage', 'light_dmg': '+{} lightning damage',
    'sight': '+{} to light radius', 'undead': '+{}% damage to the undead', 'thorns': 'Attackers take {} damage',
    'lpk': '+{} life after each kill', 'mpk': '+{} mana after each kill', 'mf': '{}% better chance of finding magic items',
    'dr': 'Damage taken reduced by {}%',
}
for _l in SKILL_PREFIX:
    AFFTXT['skill_' + _l] = '+{} to %s (3 ranks each)' % {'fire': 'Fire Magic', 'frost': 'Frost Magic', 'storm': 'Storm Magic',
                                           'restoration': 'Restoration', 'shadow': 'Shadow Magic', 'warcraft': 'Warcraft',
                                           'swords': 'Swordsmanship', 'axes': 'Axes and Maces', 'daggers': 'Daggers',
                                           'archery': 'Bows and Crossbows', 'unarmed': 'Unarmed',
                                           'spears': 'Spears and Staves'}[_l]

RES_CAP = 75
RESISTS = [('res_fire', 'Fire', (255, 122, 44)), ('res_cold', 'Cold', (159, 216, 255)),
           ('res_light', 'Lightning', (242, 240, 122)), ('res_poison', 'Poison', (127, 224, 122))]
ELEMENT_RES = {'fire': 'res_fire', 'cold': 'res_cold', 'lightning': 'res_light', 'poison': 'res_poison'}

# ------------------------------------------------------------------ uniques
# each stat rolls within its range; a unique with every stat at the top is a perfect one.
# src: who or what can carry it (monster keys, 'chest', or a boss); nobody else ever drops it
UNIQUES = [
    # named pieces come in every grade: low ones are plain magic (two powers of their level), the middle ones rare,
    # only the great ones unique. Their powers stay within what a found item of that level could have.
    dict(name='Gutripper', base='dagger', lvl=2, rar='magic', aff={'ed': (15, 25), 'leech': (2, 3)},
         src=['bandit', 'brigand', 'kobold', 'chest']),
    dict(name='Ratcatcher', base='shortsword', lvl=3, rar='magic', aff={'ed': (15, 25), 'hit': (8, 12)}, boss='ratking'),
    dict(name='Thornfield Aegis', base='quilted', lvl=2, rar='magic', aff={'edef': (15, 25), 'life': (5, 8)}, src=['chest']),
    dict(name='Crown of Ash', base='cap', lvl=4, rar='magic', aff={'life': (5, 10), 'res_fire': (5, 10)}, src=['cultist', 'chest']),
    dict(name='Hearthstone Loop', base='ring', lvl=5, rar='rare', aff={'life': (8, 12), 'regen': (1, 1), 'str': (2, 3)},
         src=['merchant', 'chest']),
    dict(name='Pale Moon Band', base='ring', lvl=7, rar='rare', aff={'mana': (15, 20), 'crit': (2, 4), 'res_cold': (11, 15)},
         src=['cultist', 'druid', 'lich']),
    dict(name="Grolm's Splitter", base='waraxe', lvl=8, rar='rare', aff={'ed': (30, 50), 'str': (4, 6), 'crit': (3, 5)}, boss='grolm'),
    dict(name='Bonecaller', base='amulet', lvl=9, rar='rare', aff={'life': (12, 18), 'leech': (2, 4), 'skill_shadow': (1, 1)},
         src=['cultist', 'lich']),
    dict(name='Veil of the Undying', base='chainmail', lvl=11, aff={'edef': (60, 80), 'life': (20, 30), 'regen': (2, 3),
                                                                     'res_cold': (11, 20)}, src=['wraith', 'lich']),
    dict(name='Stormherald', base='warstaff', lvl=10, rar='rare', aff={'ed': (30, 50), 'mana': (15, 25), 'skill_storm': (1, 1),
                                                                      'light_dmg': (2, 12)}, src=['storm_spirit', 'cultist', 'chest']),
    dict(name="Snagtooth's Pick", base='club', lvl=1, rar='magic', aff={'hit': (8, 12), 'mf': (3, 5)}, boss='snagtooth'),
    dict(name='Wolfsbane Grips', base='gloves', lvl=3, rar='magic', aff={'dex': (2, 3), 'crit': (2, 3)}, src=['bandit', 'huntsman']),
    dict(name='Mudtrudgers', base='boots', lvl=4, rar='magic', aff={'res_poison': (8, 12), 'edef': (15, 25)},
         src=['bog_lurker', 'goblin']),
    dict(name='Cinderwalk', base='hboots', lvl=9, rar='rare', aff={'res_fire': (11, 20), 'fire_dmg': (2, 6), 'life': (10, 15)},
         src=['salamander', 'drake']),
    dict(name="Hagthorn's Coil", base='belt', lvl=10, rar='rare', aff={'res_cold': (15, 20), 'mana': (15, 25), 'ene': (4, 6)},
         src=['ice_witch']),
    dict(name='Ogrebreaker', base='maul', lvl=13, aff={'ed': (70, 100), 'str': (8, 10), 'thorns': (4, 8)}, src=['ogre', 'troll']),
    dict(name='Knightfall', base='greatsword', lvl=10, rar='rare', aff={'ed': (40, 60), 'hit': (30, 40), 'res_all': (3, 5)},
         src=['knight', 'robber_knight']),
    dict(name='Eye of the Storm', base='circlet', lvl=12, aff={'skill_storm': (1, 1), 'res_light': (20, 30), 'mana': (20, 30),
                                                               'sight': (1, 1)}, src=['storm_spirit']),
    dict(name="Morvenna's Last Word", base='grimoire', lvl=14, aff={'skill_shadow': (1, 1), 'mana': (25, 40), 'mpk': (2, 3),
                                                                   'res_cold': (20, 30)}, boss='lich'),
    dict(name='Dragonhide', base='leather_x', lvl=16, aff={'res_fire': (30, 40), 'edef': (80, 110), 'life': (25, 35),
                                                           'thorns': (5, 10)}, boss='dragon'),
    dict(name='Warlord\'s Due', base='greataxe_x', lvl=16, aff={'ed': (80, 110), 'leech': (4, 6), 'str': (8, 12)}, boss='warlord'),
    dict(name='Broodmother\'s Silk', base='sash_x', lvl=13, aff={'res_poison': (21, 30), 'life': (20, 30), 'dex': (6, 8)},
         boss='broodmother'),
    dict(name='Brinecrown', base='fullhelm_x', lvl=15, aff={'res_cold': (21, 30), 'res_light': (15, 25), 'life': (20, 30),
                                                            'regen': (2, 3)}, boss='drowned_king'),
]

# ------------------------------------------------------------------ sets: a few pieces each, bound to a place or a people
SETS = {
    'varnish': dict(name="The Varnish General's Regalia", fg=_rgb('#5fd27a'),
                    lore='Worn by a general of the old Empire, and laid with him in his grave.',
                    pieces=[('Varnish War-Helm', 'fullhelm', {'life': 20, 'res_all': 5}),
                            ("General's Cuirass", 'chainmail', {'edef': 80, 'vit': 6}),
                            ('Seal of the Ninth Legion', 'amulet', {'hit': 30, 'str': 5}),
                            ('Girdle of Command', 'belt', {'life': 15, 'dr': 2})],
                    partial={'res_all': 10, 'hit': 40}, full={'skill_warcraft': 2, 'dr': 5, 'life': 40},
                    src=['varnish', 'skeleton', 'wraith']),
    'ravenwatch': dict(name='Ravenwatch Harness', fg=_rgb('#5fd27a'),
                       lore='The gear of the Crown\'s border wardens, the Ravenwatch.',
                       pieces=[('Ravenwatch Visor', 'skullcap', {'sight': 1, 'dex': 4}),
                               ('Ravenwatch Heater', 'roundshield', {'edef': 60, 'res_cold': 15}),
                               ('Ravenwatch Grips', 'hgloves', {'hit': 20, 'crit': 3})],
                       partial={'life': 20}, full={'res_all': 10, 'ed': 30}, src=['soldier', 'knight', 'crossbow']),
    'thornwarden': dict(name="Thornwarden's Garb", fg=_rgb('#5fd27a'),
                        lore='Woven for the Circle\'s wardens of the deep woods.',
                        pieces=[("Thornwarden's Bow", 'longbow', {'ed': 50, 'dex': 5}),
                                ("Thornwarden's Treads", 'boots', {'res_poison': 20, 'vit': 4}),
                                ("Thornwarden's Wraps", 'gloves', {'dex': 4, 'lpk': 2})],
                        partial={'regen': 2}, full={'skill_archery': 2, 'crit': 6}, src=['warden', 'druid']),
    'blackhand': dict(name="The Black Hand's Due", fg=_rgb('#5fd27a'),
                      lore='What the robber knights take from the roads, they wear.',
                      pieces=[("Cutpurse's Gloves", 'hgloves', {'mf': 15, 'dex': 3}),
                              ('Tollkeeper\'s Belt', 'belt', {'life': 15, 'str': 4}),
                              ('The Black Signet', 'ring', {'leech': 4, 'crit': 3})],
                      partial={'mf': 20}, full={'leech': 4, 'dmg_flat': 6, 'skill_daggers': 1},
                      src=['raider', 'robber_knight', 'bandit']),
}
SET_COLOR = _rgb('#5fd27a')

# ------------------------------------------------------------------ loot tables: what each kind of enemy carries
# families, not grades: the grade follows the item level where it drops
GEAR_USERS = {
    'kobold': ['dagger', 'club', 'cap', 'sash'], 'goblin': ['dagger', 'club', 'shortsword', 'cap', 'buckler', 'quilted', 'gloves', 'sash'],
    'gobarcher': ['shortbow', 'dagger', 'cap', 'leather', 'boots'],
    'bandit': ['dagger', 'shortsword', 'club', 'quilted', 'leather', 'cap', 'buckler', 'gloves', 'boots', 'sash', 'ring'],
    'brigand': ['shortbow', 'longbow', 'dagger', 'leather', 'cap', 'gloves', 'boots'],
    'orc': ['waraxe', 'mace', 'club', 'greataxe', 'leather', 'ringmail', 'skullcap', 'roundshield', 'hgloves', 'belt'],
    'ogre': ['club', 'mace', 'maul'],
    'skeleton': ['shortsword', 'longsword', 'buckler', 'roundshield', 'ringmail', 'skullcap', 'hboots'], 'skarcher': ['shortbow', 'longbow'],
    'cultist': ['staff', 'warstaff', 'dagger', 'grimoire', 'circlet', 'ring', 'amulet', 'sash'], 'zombie': ['quilted'],
    'soldier': ['longsword', 'shortsword', 'roundshield', 'chainmail', 'ringmail', 'skullcap', 'fullhelm', 'hgloves', 'hboots', 'belt'],
    'crossbow': ['longbow', 'shortbow', 'leather', 'cap', 'boots'],
    'knight': ['bastard', 'longsword', 'greatsword', 'kiteshield', 'platemail', 'chainmail', 'fullhelm', 'greathelm', 'gauntlets',
               'greaves', 'platedbelt'],
    'mercenary': ['longsword', 'mace', 'waraxe', 'ringmail', 'roundshield', 'skullcap', 'hgloves', 'belt', 'hboots'],
    'druid': ['staff', 'warstaff', 'circlet', 'amulet', 'ring', 'sash'], 'warden': ['longbow', 'shortbow', 'leather', 'cap', 'boots', 'gloves'],
    'raider': ['waraxe', 'mace', 'shortsword', 'leather', 'ringmail', 'buckler', 'hgloves', 'belt', 'ring'],
    'robber_knight': ['bastard', 'longsword', 'greatsword', 'chainmail', 'kiteshield', 'fullhelm', 'gauntlets', 'platedbelt'],
    'clansman': ['waraxe', 'mace', 'greataxe', 'roundshield', 'ringmail', 'chainmail', 'fullhelm', 'gauntlets', 'greaves'],
    'thunderer': ['longbow', 'chainmail', 'skullcap', 'hboots'],
    'watchman': ['club', 'shortsword', 'quilted', 'cap', 'boots'], 'huntsman': ['shortbow', 'longbow', 'leather', 'gloves', 'boots'],
    'deputy': ['shortsword', 'longsword', 'buckler', 'leather', 'belt'], 'sheriff': ['longsword', 'roundshield', 'chainmail', 'skullcap', 'belt'],
    'merchant': ['dagger', 'ring', 'amulet'],
    'ice_witch': ['staff', 'circlet', 'grimoire', 'ring', 'amulet', 'belt'], 'storm_spirit': ['amulet', 'ring', 'circlet'],
    'snagtooth': ['club', 'cap'], 'ratking': ['shortsword', 'ring'],
    'grolm': ['waraxe', 'mace', 'fullhelm', 'gauntlets'], 'lich': ['warstaff', 'grimoire', 'amulet', 'ring', 'circlet'],
    'dragon': ['ring', 'amulet', 'greathelm', 'platemail', 'leather'],
    'warlord': ['waraxe', 'greataxe', 'mace', 'platemail', 'greathelm', 'gauntlets', 'platedbelt'],
    'drowned_king': ['amulet', 'ring', 'warstaff', 'fullhelm'], 'broodmother': ['sash', 'ring', 'amulet'],
}
UNDEAD = {'zombie', 'skeleton', 'skarcher', 'ghost', 'wraith', 'lich', 'drowned', 'drowned_king'}
from .menagerie import UNDEAD as _UND
UNDEAD |= _UND

from .creatures import GEAR as _NEW_GEAR
GEAR_USERS.update(_NEW_GEAR)
# the weapons that came later, with those who use them (only those who use gear drop gear)
for _k, _add, _drop in (
        ('dune_rider', ['scimitar'], ['shortsword']), ('canyon_rider', ['scimitar'], []),
        ('orc', ['flail', 'spear'], []), ('goblin', ['spear'], []), ('gob_boss', ['flail'], []),
        ('orc_chief', ['flail'], []), ('orc_spear', ['spear'], ['dagger']), ('hob_legionary', ['spear'], []),
        ('clansman', ['warhammer'], []), ('grey_dwarf', ['warhammer'], []), ('pass_clansman', ['warhammer'], []),
        ('thunderer', ['heavyxbow', 'lightxbow'], ['longbow']), ('crossbow', ['lightxbow', 'heavyxbow'], ['longbow', 'shortbow']),
        ('kob_slinger', ['sling'], []), ('pass_slinger', ['sling'], []), ('shade_elf', ['longbow'], ['shortbow']),
        ('watch_soldier', ['halberd'], []), ('cultist', ['scythe'], []), ('gnoll_packlord', ['claws'], [])):
    if _k in GEAR_USERS:
        GEAR_USERS[_k] = [f for f in GEAR_USERS[_k] if f not in _drop] + [f for f in _add if f not in GEAR_USERS[_k]]
