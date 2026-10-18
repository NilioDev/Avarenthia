"""Classless skills. Fourteen disciplines grow by use; higher ranks unlock new skills in that
discipline. You carry six skills on your bar and can only change them in a town.

Two pools pay for them: the weapon skills and Warcraft (martial, any weapon, grows on Strength) cost stamina,
the spells cost mana."""
import random

from .worldgen import cheb, free_around

BAR_SIZE = 6
UNLOCKS = (0, 8, 20, 35, 55)

DISCIPLINES = {
    'unarmed': dict(name='Unarmed', kind='weapon', weapon='empty hands'),
    'swords': dict(name='Swordsmanship', kind='weapon', weapon='a sword'),
    'axes': dict(name='Axes and Maces', kind='weapon', weapon='an axe, mace, club or staff'),
    'daggers': dict(name='Daggers', kind='weapon', weapon='a dagger'),
    'archery': dict(name='Archery', kind='weapon', weapon='a bow'),
    'fire': dict(name='Fire Magic', kind='magic'),
    'frost': dict(name='Frost Magic', kind='magic'),
    'storm': dict(name='Storm Magic', kind='magic'),
    'restoration': dict(name='Restoration', kind='magic'),
    'shadow': dict(name='Shadow Magic', kind='magic'),
    'warcraft': dict(name='Warcraft', kind='martial'),
    'nature': dict(name='Nature', kind='magic'),
    'necromancy': dict(name='Necromancy', kind='magic'),
    'beastcraft': dict(name='Beastcraft', kind='magic'),
}
DISC_COLOR = {'unarmed': (230, 200, 170), 'swords': (220, 220, 230), 'axes': (210, 170, 120), 'daggers': (170, 200, 140), 'archery': (216, 208, 176),
              'fire': (255, 122, 44), 'frost': (159, 216, 255), 'storm': (242, 240, 122), 'restoration': (150, 255, 170),
              'shadow': (176, 110, 255), 'warcraft': (242, 196, 67), 'nature': (120, 200, 90), 'necromancy': (190, 200, 170),
              'beastcraft': (200, 150, 90)}
DISC_ORDER = list(DISCIPLINES)
WEAPON_LINE = {'dagger': 'daggers', 'shortsword': 'swords', 'longsword': 'swords', 'bastard': 'swords', 'runeblade': 'swords',
               'club': 'axes', 'mace': 'axes', 'waraxe': 'axes', 'staff': 'axes', 'warstaff': 'axes',
               'shortbow': 'archery', 'longbow': 'archery', 'warbow': 'archery',
               'greatsword': 'swords', 'greataxe': 'axes', 'maul': 'axes'}
from . import data as _D  # noqa: E402
for _k, _b in _D.BASES.items():          # exceptional and elite grades fight like their family
    if _b.get('family') in WEAPON_LINE:
        WEAPON_LINE[_k] = WEAPON_LINE[_b['family']]


class Skill:
    def __init__(self, sid, name, line, tier, cost, cd, mode, **kw):
        self.id, self.name, self.line, self.unlock = sid, name, line, UNLOCKS[tier]
        self.cost, self.cd, self.mode = cost, cd, mode
        self.dtype = kw.get('dtype', 'weapon' if DISCIPLINES[line]['kind'] in ('weapon', 'martial') else 'spell')
        self.pct, self.pct_r = kw.get('pct', 100), kw.get('pct_r', 1.5)
        self.lo, self.hi, self.r = kw.get('lo', 0), kw.get('hi', 0), kw.get('r', .4)
        self.radius = kw.get('radius', 1)
        self.range = kw.get('range', 9)
        self.fx = kw.get('fx', {})
        self.heal = kw.get('heal')
        self.buff = kw.get('buff')
        self.drain = kw.get('drain', 0)
        self.hits = kw.get('hits', 1)
        self.crit = kw.get('crit', False)
        self.execute = kw.get('execute', 1)
        self.bonus_frozen = kw.get('bonus_frozen', 1)
        self.splash = kw.get('splash', 0)
        self.cure = kw.get('cure', False)
        self.jumps = kw.get('jumps', 0)
        self.color = kw.get('color', (255, 106, 74))
        self.glyph = kw.get('glyph', '*')
        self.flavor = kw.get('flavor', '')
        self.undead = kw.get('undead', 1)
        self.party = kw.get('party', False)          # heals your hireling and your beast as well
        self.summon = kw.get('summon')               # (kind, how many, turns): thralls that fight for you a while
        self.shape = kw.get('shape')                 # (name, damage %, less damage taken %, turns)
        self.life_cost = kw.get('life_cost', 0)      # paid in life, on top of the mana
        self.fury = kw.get('fury', 0)                # your beast fights harder for this many turns
        self.guild = False


S = Skill
LEAF, BONE, BEAST = (120, 200, 90), (210, 210, 180), (200, 150, 90)
FIRE, ICE, STORM, HOLY, DARK, STEEL, ARROW, WAR = (255, 122, 44), (159, 216, 255), (242, 240, 122), (150, 255, 170), (176, 110, 255), (255, 106, 74), (216, 208, 176), (242, 196, 67)
SKILL_LIST = [
    # unarmed
    S('haymaker', 'Haymaker', 'unarmed', 0, 3, 4, 'melee', pct=170, pct_r=3, fx={'stun': 1}),
    S('flurry', 'Flurry of Blows', 'unarmed', 1, 4, 5, 'melee', pct=55, pct_r=1.5, hits=3),
    S('throat_punch', 'Throat Punch', 'unarmed', 2, 5, 8, 'melee', pct=120, fx={'stun': 3}),
    S('iron_fist', 'Iron Fist', 'unarmed', 3, 7, 10, 'melee', pct=260, pct_r=3, crit=True),
    S('whirlwind_kick', 'Whirlwind Kick', 'unarmed', 4, 9, 9, 'adjacent', pct=180, pct_r=2.5, fx={'stun': 1}),
    # swords
    S('power_strike', 'Power Strike', 'swords', 0, 3, 4, 'melee', pct=150, pct_r=2),
    S('sever', 'Sever Artery', 'swords', 1, 4, 6, 'melee', pct=100, fx={'bleed': (3, .2, 6)}),
    S('whirl', 'Whirling Blade', 'swords', 2, 6, 7, 'adjacent', pct=110, pct_r=1.5),
    S('hamstring', 'Hamstring', 'swords', 3, 5, 9, 'melee', pct=120, fx={'stun': 2}),
    S('execution', "Executioner's Strike", 'swords', 4, 8, 12, 'melee', pct=280, pct_r=3, execute=2),
    # axes and maces
    S('heavy_blow', 'Heavy Blow', 'axes', 0, 3, 5, 'melee', pct=165, pct_r=2),
    S('cleave', 'Cleave', 'axes', 1, 5, 5, 'adjacent', pct=120, pct_r=1.5),
    S('skull_crack', 'Skull Crack', 'axes', 2, 6, 10, 'melee', pct=140, fx={'stun': 3}),
    S('rend', 'Rending Chop', 'axes', 3, 6, 8, 'melee', pct=150, fx={'vuln': 6}),
    S('earthshaker', 'Earthshaker', 'axes', 4, 10, 14, 'around', pct=190, pct_r=2, radius=2, fx={'stun': 2}),
    # daggers
    S('quick_stab', 'Quick Stab', 'daggers', 0, 2, 2, 'melee', pct=70, pct_r=1, hits=2),
    S('envenom', 'Poisoned Blade', 'daggers', 1, 4, 6, 'melee', pct=100, fx={'poison': (3, .25, 8)}),
    S('shadowstep', 'Shadow Step', 'daggers', 2, 6, 10, 'leap', pct=180, range=6, crit=True, color=DARK, glyph='%'),
    S('fan', 'Fan of Knives', 'daggers', 3, 7, 8, 'around', pct=90, radius=2, color=ARROW, glyph='x'),
    S('assassinate', 'Assassinate', 'daggers', 4, 9, 15, 'melee', pct=320, pct_r=3, crit=True, execute=1.5),
    # archery
    S('aimed', 'Aimed Shot', 'archery', 0, 3, 3, 'shot', pct=145, pct_r=2, color=ARROW, glyph='-'),
    S('crippling', 'Crippling Shot', 'archery', 1, 4, 6, 'shot', pct=100, fx={'stun': 1, 'bleed': (2, .2, 5)}, color=ARROW, glyph='-'),
    S('fire_arrow', 'Burning Arrow', 'archery', 2, 5, 5, 'shot', pct=120, fx={'burn': (4, .3, 5)}, color=FIRE, glyph='-'),
    S('volley', 'Volley', 'archery', 3, 8, 10, 'volley', pct=80, pct_r=1.2, radius=7, color=ARROW, glyph='-'),
    S('pierce', 'Piercing Arrow', 'archery', 4, 8, 9, 'pierce', pct=220, pct_r=2.5, color=ARROW, glyph='='),
    # fire
    S('firebolt', 'Firebolt', 'fire', 0, 4, 1, 'bolt', lo=5, hi=9, r=.45, color=FIRE),
    S('immolate', 'Immolate', 'fire', 1, 5, 6, 'curse', fx={'burn': (4, .35, 6)}, color=FIRE),
    S('fireball', 'Fireball', 'fire', 2, 9, 5, 'bolt', lo=9, hi=15, r=.6, splash=1, color=FIRE),
    S('flame_ring', 'Ring of Fire', 'fire', 3, 10, 10, 'around', lo=8, hi=13, r=.5, radius=2, fx={'burn': (3, .25, 4)}, color=FIRE),
    S('meteor', 'Meteor', 'fire', 4, 16, 16, 'bolt', lo=22, hi=34, r=1, splash=2, color=FIRE),
    # frost
    S('frost_shard', 'Frost Shard', 'frost', 0, 4, 1, 'bolt', lo=4, hi=7, r=.4, fx={'freeze_chance': .25}, color=ICE),
    S('frost_armor', 'Frost Armor', 'frost', 1, 8, 40, 'self', buff=('def', 20, 1.2, 40), color=ICE),
    S('nova', 'Frost Nova', 'frost', 2, 9, 9, 'around', lo=4, hi=8, r=.4, radius=2, fx={'freeze': 3}, color=ICE),
    S('ice_lance', 'Ice Lance', 'frost', 3, 8, 4, 'bolt', lo=10, hi=16, r=.6, bonus_frozen=2.5, color=ICE),
    S('blizzard', 'Blizzard', 'frost', 4, 15, 15, 'target_area', lo=10, hi=18, r=.6, radius=2, fx={'freeze': 2}, color=ICE),
    # storm
    S('spark', 'Spark', 'storm', 0, 3, 1, 'bolt', lo=1, hi=13, r=.5, color=STORM, glyph='~'),
    S('static', 'Static Field', 'storm', 1, 6, 6, 'around', lo=4, hi=9, r=.35, radius=2, color=STORM, glyph='~'),
    S('chain', 'Chain Lightning', 'storm', 2, 10, 6, 'chain', lo=7, hi=14, r=.55, jumps=3, color=STORM, glyph='~'),
    S('thunderclap', 'Thunderclap', 'storm', 3, 7, 9, 'adjacent', dtype='spell', lo=9, hi=14, r=.5, fx={'stun': 2}, color=STORM, glyph='!'),
    S('storm_call', 'Call the Storm', 'storm', 4, 16, 16, 'storm', lo=12, hi=22, r=.8, radius=8, jumps=6, color=STORM, glyph='~'),
    # restoration
    S('mend', 'Mend', 'restoration', 0, 5, 3, 'self', heal=(10, .9), color=HOLY, glyph='+'),
    S('renewal', 'Renewal', 'restoration', 1, 6, 15, 'self', buff=('regen', 2, .08, 15), color=HOLY, glyph='+'),
    S('purify', 'Purify', 'restoration', 2, 6, 10, 'self', heal=(15, .8), cure=True, color=HOLY, glyph='+'),
    S('sanctuary', 'Sanctuary', 'restoration', 3, 10, 30, 'self', buff=('dr', 20, .3, 12), color=HOLY, glyph='+'),
    S('divine', 'Divine Light', 'restoration', 4, 14, 25, 'self', heal=(40, 2.2), cure=True, color=HOLY, glyph='+'),
    # shadow
    S('drain', 'Life Drain', 'shadow', 0, 4, 2, 'bolt', lo=4, hi=8, r=.4, drain=.5, color=DARK),
    S('weakness', 'Curse of Weakness', 'shadow', 1, 5, 8, 'curse', fx={'weaken': 8}, color=DARK),
    S('shadow_bolt', 'Shadow Bolt', 'shadow', 2, 8, 3, 'bolt', lo=10, hi=18, r=.65, color=DARK),
    S('plague', 'Plague', 'shadow', 3, 10, 10, 'around', lo=2, hi=5, r=.2, radius=3, fx={'poison': (4, .3, 8)}, color=DARK),
    S('soul_harvest', 'Soul Harvest', 'shadow', 4, 15, 16, 'around', lo=10, hi=16, r=.6, radius=3, drain=.35, color=DARK),
    # warcraft
    S('warcry', 'War Cry', 'warcraft', 0, 5, 12, 'around', dtype='none', radius=3, fx={'stun': 1}, color=WAR, glyph='!'),
    S('rage', 'Battle Rage', 'warcraft', 1, 6, 25, 'self', buff=('dmg', 20, .5, 12), color=WAR, glyph='!'),
    S('second_wind', 'Second Wind', 'warcraft', 2, 6, 30, 'self', heal=(20, 1.5), cure=True, color=WAR, glyph='+'),
    S('iron_skin', 'Iron Skin', 'warcraft', 3, 8, 30, 'self', buff=('dr', 25, .3, 10), color=WAR, glyph='#'),
    S('charge', 'Charge', 'warcraft', 4, 9, 12, 'leap', pct=200, pct_r=2, range=6, fx={'stun': 2}, color=WAR),
    # nature
    S('thorn_lash', 'Thorn Lash', 'nature', 0, 4, 1, 'bolt', lo=4, hi=8, r=.4, fx={'bleed': (2, .15, 4)}, color=LEAF, glyph='~'),
    S('barkskin', 'Barkskin', 'nature', 1, 6, 30, 'self', buff=('def', 25, 1.3, 30), color=LEAF, glyph='#'),
    S('grasping_roots', 'Grasping Roots', 'nature', 2, 7, 10, 'target_area', dtype='none', radius=1, fx={'stun': 3},
      color=LEAF, glyph='"'),
    S('healing_rain', 'Healing Rain', 'nature', 3, 10, 20, 'self', heal=(18, 1.2), buff=('regen', 2, .06, 12), party=True,
      color=(130, 200, 255), glyph='+'),
    S('wrath_of_oak', 'Wrath of the Oak', 'nature', 4, 14, 14, 'around', lo=12, hi=20, r=.6, radius=2, fx={'stun': 2},
      color=LEAF, glyph='♣'),
    # necromancy
    S('grave_touch', 'Grave Touch', 'necromancy', 0, 4, 2, 'bolt', lo=4, hi=7, r=.4, drain=.3, range=4, color=BONE),
    S('bone_spear', 'Bone Spear', 'necromancy', 1, 6, 4, 'pierce', lo=6, hi=11, r=.5, color=BONE, glyph='='),
    S('death_mark', 'Mark of Death', 'necromancy', 2, 5, 8, 'curse', fx={'vuln': 10}, color=BONE),
    S('raise_skeleton', 'Raise Skeleton', 'necromancy', 3, 10, 25, 'summon', summon=('skeleton', 1, 30), color=BONE, glyph='z'),
    S('withering', 'Withering', 'necromancy', 4, 14, 14, 'around', lo=8, hi=14, r=.5, radius=3, drain=.3,
      fx={'weaken': 6}, color=BONE),
    # beastcraft
    S('feral_howl', 'Feral Howl', 'beastcraft', 0, 4, 10, 'around', dtype='none', radius=2, fx={'weaken': 5}, color=BEAST, glyph='!'),
    S('mend_beast', 'Lick the Wounds', 'beastcraft', 1, 5, 8, 'self', heal=(10, .8), party=True, color=BEAST, glyph='+'),
    S('hawk_eye', 'Hawk Eye', 'beastcraft', 2, 5, 25, 'self', buff=('dmg', 15, .4, 15), fury=15, color=BEAST, glyph='!'),
    S('call_wolf', 'Call a Wolf', 'beastcraft', 3, 10, 30, 'summon', summon=('wolf', 1, 30), color=BEAST, glyph='C'),
    S('alpha_roar', 'Alpha Roar', 'beastcraft', 4, 12, 18, 'around', dtype='none', radius=3, fx={'stun': 2, 'weaken': 6},
      fury=12, color=BEAST, glyph='!'),
]
# techniques taught only by guild masters (see guilds.py); they never turn up in tomes
TECHNIQUES = [
    S('mage_armor', 'Mage Armor', 'frost', 1, 8, 30, 'self', buff=('dr', 15, .25, 20), color=ICE, flavor='Circle of Magi'),
    S('arcane_barrage', 'Arcane Barrage', 'storm', 2, 12, 6, 'chain', lo=9, hi=17, r=.6, jumps=4, color=STORM, glyph='~',
      flavor='Circle of Magi'),
    S('inferno', 'Inferno', 'fire', 4, 18, 14, 'around', lo=16, hi=26, r=.8, radius=3, fx={'burn': (5, .4, 6)}, color=FIRE,
      flavor='Circle of Magi'),
    S('shield_wall', 'Shield Wall', 'warcraft', 1, 6, 25, 'self', buff=('def', 40, 1.5, 15), color=WAR, glyph='#',
      flavor='Iron Company'),
    S('battle_drill', 'Battle Drill', 'warcraft', 2, 8, 22, 'self', buff=('dmg', 30, .6, 14), color=WAR, glyph='!', flavor='Iron Company'),
    S('last_stand', 'Last Stand', 'warcraft', 4, 12, 40, 'self', heal=(40, 2), buff=('dr', 35, .3, 8), cure=True, color=WAR, glyph='+',
      flavor='Iron Company'),
    S('smite', 'Smite', 'restoration', 1, 6, 3, 'bolt', lo=8, hi=14, r=.5, undead=2, color=HOLY, glyph='+', flavor='Order of Dawn'),
    S('holy_shield', 'Holy Shield', 'restoration', 2, 10, 30, 'self', buff=('dr', 30, .3, 12), color=HOLY, glyph='+',
      flavor='Order of Dawn'),
    S('dawnbreak', 'Dawnbreak', 'restoration', 4, 16, 16, 'around', lo=14, hi=24, r=.7, radius=3, undead=2.5, color=HOLY, glyph='*',
      flavor='Order of Dawn'),
    S('hunters_mark', "Hunter's Mark", 'archery', 1, 4, 6, 'shot', pct=160, pct_r=2, fx={'vuln': 8}, color=ARROW, glyph='-',
      flavor='Wardens of the Wild'),
    S('rain_of_arrows', 'Rain of Arrows', 'archery', 2, 10, 10, 'volley', pct=110, pct_r=1.5, radius=8, color=ARROW, glyph='-',
      flavor='Wardens of the Wild'),
    S('thornbind', 'Thornbind', 'archery', 4, 9, 12, 'shot', pct=200, pct_r=2.5, fx={'stun': 4, 'bleed': (4, .3, 6)}, color=(112, 200, 90),
      glyph='-', flavor='Wardens of the Wild'),
    S('garrote', 'Garrote', 'daggers', 1, 5, 7, 'melee', pct=150, crit=True, fx={'bleed': (4, .3, 6), 'stun': 1},
      flavor="Thieves' Guild"),
    S('smoke_bomb', 'Smoke Bomb', 'daggers', 2, 6, 14, 'around', dtype='none', radius=2, fx={'stun': 3}, color=(150, 150, 150), glyph='░',
      flavor="Thieves' Guild"),
    S('deaths_kiss', "Death's Kiss", 'daggers', 4, 10, 16, 'melee', pct=380, pct_r=3, crit=True, execute=2.5, flavor="Thieves' Guild"),
    S('hellfire', 'Hellfire', 'shadow', 1, 7, 3, 'bolt', lo=10, hi=18, r=.6, drain=.25, splash=1, color=(220, 60, 120),
      flavor='Hollow Coven'),
    S('pact_of_blood', 'Pact of Blood', 'shadow', 2, 4, 30, 'self', buff=('dmg', 40, .6, 15), color=(200, 40, 60), glyph='!',
      flavor='Hollow Coven'),
    S('morraks_hand', "Morrak's Hand", 'shadow', 4, 18, 16, 'around', lo=18, hi=30, r=.9, radius=3, drain=.5, color=DARK,
      flavor='Hollow Coven'),
    # for those who serve two guilds
    S('spellblade', 'Spellblade', 'warcraft', 2, 8, 6, 'melee', dtype='weapon', pct=210, pct_r=2, fx={'burn': (4, .3, 5)}, color=FIRE,
      flavor='Iron Company and Circle of Magi'),
    S('soul_knife', 'Soul Knife', 'shadow', 2, 8, 4, 'bolt', lo=12, hi=22, r=.7, drain=.4, range=3, color=DARK,
      flavor="Thieves' Guild and Hollow Coven"),
    S('thornstorm', 'Thornstorm', 'storm', 2, 12, 10, 'around', lo=10, hi=18, r=.6, radius=3, fx={'bleed': (3, .25, 5), 'stun': 1},
      color=(160, 220, 110), glyph='~', flavor='Wardens and Circle of Magi'),
    S('crusade', 'Crusade', 'warcraft', 2, 10, 30, 'self', buff=('dmg', 45, .6, 15), color=(255, 232, 160), glyph='!',
      flavor='Order of Dawn and Iron Company'),
    # the Green Moot
    S('entangle', 'Entangle', 'nature', 1, 7, 12, 'around', dtype='none', radius=2, fx={'stun': 3}, color=LEAF, glyph='"',
      flavor='The Green Moot'),
    S('spirit_totem', 'Spirit Totem', 'nature', 2, 10, 30, 'self', heal=(20, 1.2), buff=('regen', 3, .08, 20), party=True,
      color=(140, 230, 160), glyph='¶', flavor='The Green Moot'),
    S('wild_shape', 'Wild Shape', 'nature', 4, 12, 50, 'shape', shape=('bear', 35, 25, 25), color=BEAST, glyph='q',
      flavor='The Green Moot'),
    # the Hallowed Chapter
    S('mass_mend', 'Mass Mend', 'restoration', 1, 8, 8, 'self', heal=(16, 1.1), party=True, color=HOLY, glyph='+',
      flavor='The Hallowed Chapter'),
    S('hallowed_ground', 'Hallowed Ground', 'restoration', 2, 10, 30, 'around', dtype='none', radius=4, fx={'stun': 4},
      color=(255, 240, 200), glyph='+', flavor='The Hallowed Chapter'),
    S('rite_of_return', 'Rite of Return', 'restoration', 4, 20, 80, 'rite', color=HOLY, glyph='+', flavor='The Hallowed Chapter'),
    # the Quiet Ossuary
    S('raise_dead', 'Raise Dead', 'necromancy', 1, 10, 20, 'raise', color=BONE, glyph='z', flavor='The Quiet Ossuary'),
    S('bone_armour', 'Bone Armour', 'necromancy', 2, 8, 30, 'self', buff=('dr', 20, .3, 20), color=BONE, glyph='#',
      flavor='The Quiet Ossuary'),
    S('corpse_burst', 'Corpse Burst', 'necromancy', 4, 14, 10, 'burst', lo=16, hi=26, r=.8, radius=2, color=(200, 220, 120),
      flavor='The Quiet Ossuary'),
    # the Order of the Still Hand
    S('still_flurry', 'Hundred Hands', 'unarmed', 1, 5, 5, 'melee', pct=50, pct_r=1.2, hits=4, flavor='Order of the Still Hand'),
    S('stone_stance', 'Stone Stance', 'unarmed', 2, 6, 25, 'self', buff=('dr', 35, .3, 12), color=(170, 160, 150), glyph='#',
      flavor='Order of the Still Hand'),
    S('pressure_point', 'Pressure Point', 'unarmed', 2, 5, 8, 'melee', pct=80, pct_r=1, fx={'stun': 2}, flavor='Order of the Still Hand'),
    S('wind_step', 'Wind Step', 'unarmed', 4, 6, 6, 'leap', pct=140, pct_r=2, range=4, color=(220, 230, 255), glyph='~',
      flavor='Order of the Still Hand'),
    # the Houndwardens' Lodge
    S('tame', 'Tame', 'beastcraft', 1, 8, 20, 'tame', color=BEAST, glyph='♥', flavor="The Houndwardens' Lodge"),
    S('call_of_the_pack', 'Call of the Pack', 'beastcraft', 2, 12, 40, 'summon', summon=('wolf', 2, 30), color=BEAST, glyph='C',
      flavor="The Houndwardens' Lodge"),
    S('pack_fury', 'Pack Fury', 'beastcraft', 4, 10, 30, 'self', buff=('dmg', 25, .5, 15), fury=15, color=(230, 120, 60), glyph='!',
      flavor="The Houndwardens' Lodge"),
    # for those who serve two guilds
    S('wildheart', 'Wildheart', 'nature', 2, 12, 50, 'shape', shape=('wolf', 55, 10, 25), fury=25, color=BEAST, glyph='C',
      flavor='Green Moot and Wardens'),
    S('lichcraft', 'Lichcraft', 'necromancy', 2, 10, 12, 'around', lo=14, hi=24, r=.8, radius=3, drain=.2, life_cost=12,
      fx={'weaken': 6}, color=(150, 120, 220), flavor='Quiet Ossuary and Hollow Coven'),
    S('mendicant', "Mendicant's Fist", 'unarmed', 2, 6, 5, 'melee', pct=190, pct_r=2, heal=(6, .5), fx={'stun': 1},
      color=HOLY, flavor='Still Hand and Order of Dawn'),
    S('war_handler', 'War-Handler', 'beastcraft', 2, 12, 40, 'summon', summon=('war_dog', 2, 40), fury=20, color=(200, 170, 120),
      glyph='C', flavor="Houndwardens and Iron Company"),
]
for _t in TECHNIQUES:
    _t.guild = True
SKILLS = {s.id: s for s in SKILL_LIST + TECHNIQUES}
STARTING_BAR = ['power_strike', 'firebolt', 'mend', None, None, None]


def pool(sk):
    """What a skill costs: 'stamina' for the weapon skills and Warcraft, 'mana' for spells."""
    return 'stamina' if DISCIPLINES[sk.line]['kind'] in ('weapon', 'martial') else 'mana'


def cost_of(game, sk):
    gnome = getattr(game.player, 'race', '') == 'gnome' and pool(sk) == 'mana'
    return max(1, round(sk.cost * (.85 if gnome else 1)))


def can_pay(game, sk):
    p = game.player
    return (getattr(p, 'stamina', 0) if pool(sk) == 'stamina' else p.mana) >= cost_of(game, sk)


def by_line(line):
    return [s for s in SKILL_LIST if s.line == line]


def weapon_line(game):
    w = game.eq_item('weapon')
    return WEAPON_LINE.get(w.base) if w else 'unarmed'


LINE_ELEM = {'fire': 'fire', 'frost': 'cold', 'storm': 'lightning', 'nature': 'poison', 'necromancy': 'cold'}
GEAR_RANKS = 3        # each '+1 to a discipline' on your gear makes its skills strike as if three ranks higher


def rank(game, line):
    """The rank your skills of this discipline work at: what you have learned, plus your gear."""
    return game.player.disc[line][0] + game.stats().get('skill_' + line, 0) * GEAR_RANKS


def need_for(r):
    return 8 + r * 2


# ------------------------------------------------------------------ descriptions
def describe(sk, r):
    parts = []
    if sk.dtype == 'weapon':
        dmg = f'{round(sk.pct + sk.pct_r * r)}% weapon damage'
    elif sk.dtype == 'spell':
        dmg = f'{round(sk.lo + r * sk.r)}-{round(sk.hi + r * sk.r)} damage (+Energy/5)'
    else:
        dmg = ''
    m = sk.mode
    if m == 'melee':
        parts.append(f"Strike an adjacent enemy{' twice' if sk.hits == 2 else f' {sk.hits} times' if sk.hits > 2 else ''} for {dmg}.")
    elif m == 'adjacent':
        parts.append(f'Hit every adjacent enemy for {dmg}.')
    elif m == 'around':
        parts.append(f"Affect every enemy within {sk.radius} tiles{(' for ' + dmg) if dmg else ''}.")
    elif m in ('bolt', 'shot'):
        parts.append(f"{'Shoot' if m == 'shot' else 'Hurl a bolt at'} the nearest enemy for {dmg}." + (f' Splashes {sk.splash} tile{"s" if sk.splash > 1 else ""} around the target.' if sk.splash else ''))
    elif m == 'volley':
        parts.append(f'Shoot every visible enemy within {sk.radius} tiles for {dmg}.')
    elif m == 'pierce':
        parts.append(f'An arrow that passes through every enemy in a line for {dmg}.')
    elif m == 'chain':
        parts.append(f'Lightning strikes the nearest enemy and arcs to {sk.jumps + r // 25} more for {dmg}.')
    elif m == 'leap':
        parts.append(f'Leap next to an enemy up to {sk.range} tiles away and strike for {dmg}.')
    elif m == 'storm':
        parts.append(f'Lightning strikes up to {sk.jumps} visible enemies for {dmg} each.')
    elif m == 'target_area':
        parts.append(f"Strike the area around the nearest enemy ({sk.radius} tile{'s' if sk.radius > 1 else ''})"
                     + (f' for {dmg}.' if dmg else '.'))
    elif m == 'curse':
        parts.append('Afflict the nearest visible enemy.')
    elif m == 'summon':
        k, n, t = sk.summon
        one, many = {'skeleton': ('a skeleton', 'skeletons'), 'wolf': ('a wolf', 'wolves'),
                     'war_dog': ('a war dog', 'war dogs')}.get(k, (k, k))
        parts.append(f"Call {one if n == 1 else f'{n} {many}'} to fight at your side for {t + r // 2} turns.")
    elif m == 'raise':
        parts.append(f'The last enemy to fall near you rises and fights for you for {20 + r // 2} turns.')
    elif m == 'tame':
        parts.append('Tame the wolf, bear, panther or hawk next to you; easier when it is hurt. It stays with you, '
                     'eats meat and takes orders (h). One beast at a time.')
    elif m == 'rite':
        parts.append('Raise your fallen hireling or beast where it lies, without a temple.')
    elif m == 'burst':
        parts.append(f'The nearest corpse bursts: {dmg} to every enemy within {sk.radius} tiles of it.')
    elif m == 'shape':
        nm, dp, dr_, t = sk.shape
        parts.append(f'Take the shape of a {nm} for {t} turns: +{dp + r // 4}% damage, {dr_}% less damage taken.')
    if sk.heal:
        parts.append(f'Heals {round(sk.heal[0] + sk.heal[1] * r)} life.')
    if sk.buff:
        k, b, br, t = sk.buff
        v = round(b + br * r)
        parts.append({'def': f'+{v} defense', 'regen': f'+{v} life per turn', 'dr': f'{min(60, v)}% less damage taken',
                      'dmg': f'+{v}% damage'}[k] + f' for {t} turns.')
    fx = sk.fx
    if 'stun' in fx:
        parts.append(f"Stuns for {fx['stun']} turn{'s' if fx['stun'] > 1 else ''}.")
    if 'freeze' in fx:
        parts.append(f"Freezes for {fx['freeze']} turns.")
    if 'freeze_chance' in fx:
        parts.append(f"{round(fx['freeze_chance'] * 100)}% chance to freeze.")
    for k, word in (('burn', 'Burns'), ('bleed', 'Bleeds'), ('poison', 'Poisons')):
        if k in fx:
            b, br, t = fx[k]
            parts.append(f'{word} for {round(b + br * r)} per turn over {t} turns.')
    if 'weaken' in fx:
        parts.append(f"Weakened enemies deal 30% less damage for {fx['weaken']} turns.")
    if 'vuln' in fx:
        parts.append(f"Target takes 25% more damage for {fx['vuln']} turns.")
    if sk.drain:
        parts.append(f'Heals you for {round(sk.drain * 100)}% of the damage.')
    if sk.party:
        parts.append('Heals your hireling and your beast as well.')
    if sk.fury:
        parts.append(f'Your beast fights 40% harder for {sk.fury} turns.')
    if sk.life_cost:
        parts.append(f'Costs {sk.life_cost} life.')
    if sk.crit:
        parts.append('Always a critical hit.')
    if sk.execute > 1:
        parts.append(f'x{sk.execute:g} damage against enemies below 30% life.')
    if sk.bonus_frozen > 1:
        parts.append(f'x{sk.bonus_frozen:g} damage against frozen enemies.')
    if sk.cure:
        parts.append('Cures poison and burning.')
    return ' '.join(parts)


# ------------------------------------------------------------------ learning
def gain(game, line, amount):
    p = game.player
    d = p.disc[line]
    from .races import RACES
    rc = RACES.get(getattr(p, 'race', 'human'), RACES['human'])
    amount = amount * rc['learn'].get(line, 1.1 if p.race == 'human' else 1)
    d[1] += amount
    while d[0] < 100 and d[1] >= need_for(d[0]):
        d[1] -= need_for(d[0])
        d[0] += 1
        game.msg(f"Your {DISCIPLINES[line]['name']} rises to {d[0]}.", 'good')
        if d[0] in UNLOCKS:
            game.msg(f"You can now study harder {DISCIPLINES[line]['name']} tomes.", 'gold')


def learn(game, sid):
    """Learn a skill from a tome. Returns True if the tome was used up."""
    p = game.player
    sk = SKILLS[sid]
    if sid in p.known:
        game.msg(f'You already know {sk.name}.')
        return False
    r = p.disc[sk.line][0]
    if r < sk.unlock:
        game.msg(f"The words swim before your eyes. You need {DISCIPLINES[sk.line]['name']} {sk.unlock} "
                 f"to understand this tome (you have {r}).", 'bad')
        return False
    p.known.append(sid)
    game.msg(f'You study the tome and learn {sk.name}!', 'gold')
    if None in p.bar:
        p.bar[p.bar.index(None)] = sid
        game.msg(f'{sk.name} is now on your skill bar.', 'info')
    else:
        game.msg('Change your skills in a town or stronghold (Z).', 'info')
    return True


# ------------------------------------------------------------------ using
def use(game, slot):
    p = game.player
    sid = p.bar[slot] if slot < len(p.bar) else None
    if not sid:
        game.msg('That skill slot is empty. Skills are learned from tomes; choose them in a town with Z.' if p.known else
                 'You know no skills yet. Skill tomes are found on monsters, in ruins and with traders.')
        return 0
    sk = SKILLS[sid]
    m = game.map
    if p.cooldowns.get(sid, 0) > 0:
        game.msg(f'{sk.name} is recharging ({p.cooldowns[sid]} turns).')
        return 0
    if m.kind in ('over', 'town') and sk.mode != 'self':
        game.msg('There is nothing to fight here.')
        return 0
    cost = cost_of(game, sk)
    kind = pool(sk)
    if not can_pay(game, sk):
        game.msg(f'Not enough {kind} for {sk.name} ({cost} needed).', 'bad')
        return 0
    d = DISCIPLINES[sk.line]
    if d['kind'] == 'weapon' and weapon_line(game) != sk.line:
        game.msg(f"{sk.name} needs {d['weapon']} in your hands.", 'bad')
        return 0
    if sk.life_cost and p.life <= sk.life_cost + 1:
        game.msg(f'{sk.name} would take more life than you have.', 'bad')
        return 0
    r = rank(game, sk.line)
    if not EXEC[sk.mode](game, sk, r):
        return 0
    if sk.life_cost:
        p.life -= sk.life_cost
        game.msg(f'{sk.name} takes its price in life.', 'bad')
    if sk.heal and sk.mode not in ('self',):
        game.heal(round(sk.heal[0] + sk.heal[1] * r), show=True)
    if sk.fury:
        from . import mercs as MC
        bst = MC.with_you(game, 'beast')
        if bst:
            bst.fury = max(bst.fury, sk.fury)
            game.msg(f'{bst.name} bristles and bares its teeth.', 'good')
    if kind == 'stamina':
        p.stamina -= cost
        p.strained = game.turn
    else:
        p.mana -= cost
    p.cooldowns[sid] = sk.cd
    gain(game, sk.line, 3)
    return 1


def _spell_dmg(game, sk, r):
    grow = 'str' if DISCIPLINES[sk.line]['kind'] == 'martial' else 'ene'
    dmg = random.randint(round(sk.lo + r * sk.r), round(sk.hi + r * sk.r)) + game.stats()[grow] // 5
    if sk.line in ('fire', 'storm'):
        from . import weather as WX
        wx = WX.current(game)
        if sk.line == 'fire' and wx in ('rain', 'downpour', 'storm', 'snow', 'blizzard', 'sleet', 'freezing'):
            dmg = round(dmg * .75)                      # fire sputters in the wet
        elif sk.line == 'fire' and wx in ('heat', 'drystorm'):
            dmg = round(dmg * 1.15)
        elif sk.line == 'storm' and wx in ('storm', 'drystorm'):
            dmg = round(dmg * 1.25)                     # the sky lends its lightning
    return dmg


def _hit(game, mon, sk, r, ranged=False):
    """Apply one hit of this skill to a monster. Returns True if it died."""
    if mon.hp <= 0 or mon not in game.map.mons:
        return True
    if sk.dtype == 'weapon':
        pct = sk.pct + sk.pct_r * r
        if sk.execute > 1 and mon.hp < mon.maxhp * .3:
            pct *= sk.execute
        dead = game.weapon_strike(mon, pct, force_crit=sk.crit, ranged=ranged)
        dealt = 0
    elif sk.dtype == 'spell':
        dmg = _spell_dmg(game, sk, r)
        game._area = sk.mode in ('around', 'chain', 'storm', 'target_area', 'volley')
        if sk.bonus_frozen > 1 and mon.hold > 0:
            dmg *= sk.bonus_frozen
        if sk.undead > 1 and not mon.is_npc and mon.k in _D.UNDEAD:
            dmg *= sk.undead
        before = mon.hp
        dead = game.damage_mon(mon, dmg, col=sk.color, elem=LINE_ELEM.get(sk.line))
        game._area = False
        dealt = before - max(0, mon.hp)
        if sk.drain:
            game.heal(round(dealt * sk.drain))
    else:
        dead = False
    if not dead:
        apply_fx(game, mon, sk, r)
    return dead


def apply_fx(game, mon, sk, r):
    fx = sk.fx
    if 'stun' in fx:
        mon.hold = max(mon.hold, fx['stun'])
    if 'freeze' in fx:
        mon.hold = max(mon.hold, fx['freeze'])
        mon.frozen = True
    if 'freeze_chance' in fx and random.random() < fx['freeze_chance']:
        mon.hold = max(mon.hold, 2)
        mon.frozen = True
    for k in ('burn', 'bleed', 'poison'):
        if k in fx:
            b, br, t = fx[k]
            mon.effects[k] = [t, max(1, round(b + br * r))]
    if 'weaken' in fx:
        mon.effects['weaken'] = [fx['weaken'], 0]
    if 'vuln' in fx:
        mon.effects['vuln'] = [fx['vuln'], 0]
    mon.awake = True


def _melee_target(game):
    p = game.player
    adj = [o for o in game.visible_hostiles() if cheb(o.x, o.y, p.x, p.y) <= 1]
    t = game.target()
    if t and t in adj:
        return t
    if not adj:
        return None
    for o in adj:
        if o.id == p.last_target:
            return o
    return adj[0]


def x_melee(game, sk, r):
    t = _melee_target(game)
    if not t:
        game.msg('No enemy within reach.')
        return False
    game.player.last_target = t.id
    game.flash([(t.x, t.y)], sk.color, '/', .14)
    for _ in range(sk.hits):
        if _hit(game, t, sk, r):
            break
    return True


def x_adjacent(game, sk, r):
    p = game.player
    t = [o for o in game.visible_hostiles() if cheb(o.x, o.y, p.x, p.y) <= 1]
    if not t:
        game.msg('No enemies next to you.')
        return False
    game.flash(ring_cells(p.x, p.y, 1), sk.color, sk.glyph, .16)
    for o in t:
        _hit(game, o, sk, r)
    return True


def x_around(game, sk, r):
    p = game.player
    t = [o for o in game.visible_hostiles() if cheb(o.x, o.y, p.x, p.y) <= sk.radius]
    cells = []
    for rr in range(1, sk.radius + 1):
        cells += ring_cells(p.x, p.y, rr)
    game.flash(cells, sk.color, sk.glyph, .22)
    if not t:
        game.msg('No enemies in range.')
        return True
    for o in t:
        _hit(game, o, sk, r)
    return True


def _projectile_target(game, sk):
    t = game.nearest_target(sk.range, True)
    if not t:
        game.miss_target('No target in sight.')
    return t


def x_bolt(game, sk, r, ranged=False):
    t = _projectile_target(game, sk)
    if not t:
        return False
    p = game.player
    p.last_target = t.id
    game.flash(game.path_to(t)[:-1], sk.color, sk.glyph, .17)
    tx, ty = t.x, t.y
    _hit(game, t, sk, r, ranged)
    if sk.splash:
        cells = []
        for rr in range(1, sk.splash + 1):
            cells += ring_cells(tx, ty, rr)
        game.flash(cells, sk.color, '*', .22)
        for o in [o for o in game.visible_hostiles() if cheb(o.x, o.y, tx, ty) <= sk.splash and (o.x, o.y) != (tx, ty)]:
            _hit(game, o, sk, r, ranged)
    return True


def x_shot(game, sk, r):
    return x_bolt(game, sk, r, ranged=True)


def x_volley(game, sk, r):
    p = game.player
    t = [o for o in game.visible_hostiles() if cheb(o.x, o.y, p.x, p.y) <= sk.radius and game.line_clear(p.x, p.y, o.x, o.y)]
    if not t:
        game.msg('No targets in sight.')
        return False
    for o in t:
        game.flash(game.path_to(o)[:-1], sk.color, sk.glyph, .17)
        _hit(game, o, sk, r, True)
    return True


def x_pierce(game, sk, r):
    t = _projectile_target(game, sk)
    if not t:
        return False
    p, m = game.player, game.map
    dx, dy = t.x - p.x, t.y - p.y
    n = max(abs(dx), abs(dy))
    cells = []
    for i in range(1, 12):
        x, y = p.x + round(dx * i / n), p.y + round(dy * i / n)
        if not m.inb(x, y) or game.opaque(x, y):
            break
        cells.append((x, y))
    game.flash(cells, sk.color, sk.glyph, .18)
    for x, y in cells:
        o = m.mon_at(x, y)
        if o and not o.is_npc:
            _hit(game, o, sk, r, True)
    return True


def x_chain(game, sk, r):
    t = _projectile_target(game, sk)
    if not t:
        return False
    hit = set()
    frm = (game.player.x, game.player.y)
    jumps = 1 + sk.jumps + r // 25
    while t and jumps > 0:
        jumps -= 1
        game.flash(game.cells_between(frm, (t.x, t.y)), sk.color, sk.glyph, .2)
        hit.add(t.id)
        frm = (t.x, t.y)
        _hit(game, t, sk, r)
        cand = [o for o in game.visible_hostiles() if o.id not in hit and cheb(o.x, o.y, *frm) <= 4]
        t = min(cand, key=lambda o: cheb(o.x, o.y, *frm)) if cand else None
    return True


def x_storm(game, sk, r):
    p = game.player
    t = [o for o in game.visible_hostiles() if cheb(o.x, o.y, p.x, p.y) <= sk.radius]
    if not t:
        game.msg('No targets in sight.')
        return False
    random.shuffle(t)
    for o in t[:sk.jumps]:
        game.flash([(o.x, o.y - 1), (o.x, o.y)], sk.color, sk.glyph, .25)
        _hit(game, o, sk, r)
    game.shake()
    return True


def x_target_area(game, sk, r):
    t = game.nearest_target(sk.range, False)
    if not t:
        game.miss_target('No target in sight.')
        return False
    tx, ty = t.x, t.y
    cells = [(tx, ty)]
    for rr in range(1, sk.radius + 1):
        cells += ring_cells(tx, ty, rr)
    game.flash(cells, sk.color, '*', .26)
    for o in [o for o in game.visible_hostiles() if cheb(o.x, o.y, tx, ty) <= sk.radius]:
        _hit(game, o, sk, r)
    return True


def x_curse(game, sk, r):
    t = game.nearest_target(sk.range, False)
    if not t:
        game.miss_target('No target in sight.')
        return False
    game.flash([(t.x, t.y)], sk.color, '*', .22)
    apply_fx(game, t, sk, r)
    game.player.last_target = t.id
    game.msg(f'{sk.name} takes hold of {t.the()}.', 'info')
    return True


def x_leap(game, sk, r):
    p, m = game.player, game.map
    t = game.nearest_target(sk.range, False)
    if not t:
        game.miss_target('No enemy within reach.')
        return False
    if cheb(t.x, t.y, p.x, p.y) > 1:
        spots = [c for c in free_around(game, m, t.x, t.y, 1) if game.visible(*c)]
        if not spots:
            game.msg('There is no room to land.')
            return False
        dst = min(spots, key=lambda c: cheb(c[0], c[1], p.x, p.y))
        game.flash(game.cells_between((p.x, p.y), dst), sk.color, sk.glyph, .18)
        p.x, p.y = dst
        game.compute_fov()
    p.last_target = t.id
    _hit(game, t, sk, r)
    return True


def x_self(game, sk, r):
    p = game.player
    did = False
    if sk.heal:
        amt = round(sk.heal[0] + sk.heal[1] * r)
        game.heal(amt, show=True)
        did = True
        if sk.party:
            from . import mercs as MC
            for mc in MC.party(game):
                mx = MC.stats(game, mc)['max_hp']
                if mc.hp < mx:
                    mc.hp = min(mx, mc.hp + amt)
                    MC.refresh_body(game, mc)
                    if mc.body is not None:
                        game.num(mc.body.x, mc.body.y, f'+{amt}', (120, 240, 140))
    if sk.cure:
        p.poison = None
        p.burn = None
        from .behave import cure
        cure(game)
    if sk.buff:
        k, b, br, t = sk.buff
        v = round(b + br * r)
        if k == 'dr':
            v = min(60, v)
        p.buffs = [x for x in p.buffs if x[0] != k] + [[k, v, t, sk.name]]
        did = True
    game.flash(ring_cells(p.x, p.y, 1), sk.color, sk.glyph, .2)
    game.msg(f'You use {sk.name}.', 'good')
    return did or sk.cure


def ring_cells(x, y, r):
    return [(x + dx, y + dy) for dy in range(-r, r + 1) for dx in range(-r, r + 1) if max(abs(dx), abs(dy)) == r]


def x_summon(game, sk, r):
    from . import mercs as MC
    p, m = game.player, game.map
    k, n, t = sk.summon
    if k not in _D.MONSTERS:
        k = 'wolf'
    spots = [c for c in free_around(game, m, p.x, p.y, 2) if c != (p.x, p.y)]
    if not spots:
        game.msg('There is no room.')
        return False
    random.shuffle(spots)
    name = {'skeleton': 'Risen Skeleton', 'wolf': 'Wolf of the Pack', 'war_dog': 'War Dog'}.get(sk.summon[0])
    for x, y in spots[:n]:
        o = MC.thrall(game, k, x, y, t + r // 2, name)
        if sk.summon[0] == 'war_dog':
            o.hp = o.maxhp = round(o.maxhp * 1.4)
            o.fg = (200, 170, 120)
    game.flash(spots[:n], sk.color, sk.glyph, .25)
    game.msg({'skeleton': 'Bones knit together out of the ground and stand up for you.',
              'wolf': 'A howl answers from the dark, and wolves come loping to your side.' if n > 1 else
                      'A wolf answers your call and falls in at your side.',
              'war_dog': 'You whistle, and war dogs in spiked collars come running.'}.get(sk.summon[0], 'Help comes.'), 'good')
    return True


def x_raise(game, sk, r):
    from . import mercs as MC
    p, m = game.player, game.map
    slain = [c for c in getattr(m, 'slain', []) if cheb(c[1], c[2], p.x, p.y) <= 7 and game.visible(c[1], c[2])
             and not _D.MONSTERS[c[0]].get('chief') and not _D.MONSTERS[c[0]].get('boss')]
    spot = None
    while slain:
        c = slain.pop()
        if not game.occupied(m, c[1], c[2]) and (c[1], c[2]) != (p.x, p.y):
            spot = c
            break
    if not spot:
        game.msg('There is no fallen enemy near you to raise.')
        return False
    m.slain.remove(spot)
    k, x, y, lvl = spot[:4]
    o = MC.thrall(game, k, x, y, 20 + r // 2, 'Risen ' + _D.MONSTERS[k]['name'], lvl)
    o.fg = (190, 200, 170)
    game.flash([(x, y)], sk.color, sk.glyph, .3)
    game.msg(f'You speak the word, and the {_D.MONSTERS[k]["name"].lower()} gets up again. It is yours, for a while.', 'good')
    return True


def x_burst(game, sk, r):
    p, m = game.player, game.map
    slain = [c for c in getattr(m, 'slain', []) if cheb(c[1], c[2], p.x, p.y) <= 7 and game.visible(c[1], c[2])]
    if not slain:
        game.msg('There is no corpse near you.')
        return False
    c = min(slain, key=lambda c: cheb(c[1], c[2], p.x, p.y))
    m.slain.remove(c)
    tx, ty = c[1], c[2]
    cells = [(tx, ty)]
    for rr in range(1, sk.radius + 1):
        cells += ring_cells(tx, ty, rr)
    game.flash(cells, sk.color, '*', .26)
    game.msg('The corpse swells, and bursts.', 'good')
    for o in [o for o in game.visible_hostiles() if cheb(o.x, o.y, tx, ty) <= sk.radius]:
        _hit(game, o, sk, r)
    return True


def x_tame(game, sk, r):
    from . import mercs as MC
    p = game.player
    if MC.get(game, 'beast'):
        game.msg(f'You already have {MC.get(game, "beast").name}. One beast at a time.')
        return False
    adj = [o for o in game.visible_hostiles() if cheb(o.x, o.y, p.x, p.y) <= 1]
    beasts = [o for o in adj if o.k in MC.TAME_OF and not o.elite and not getattr(o, 'named', None)]
    if not beasts:
        game.msg('Only a wolf, a bear, a panther or a hawk can be tamed, and it must be next to you.' if not adj else
                 'That one will never be tamed.')
        return False
    o = min(beasts, key=lambda o: o.hp / max(1, o.maxhp))
    chance = .15 + r / 120 + (1 - o.hp / max(1, o.maxhp)) * .5
    game.flash([(o.x, o.y)], sk.color, sk.glyph, .3)
    if random.random() >= chance:
        o.awake = True
        game.msg(f'You hold out your hand and speak low. {o.the()[0].upper() + o.the()[1:]} snarls and will not have it.', 'bad')
        return True
    mc = MC.tame(game, o)
    game.msg(f'{o.the()[0].upper() + o.the()[1:]} lowers its head and sniffs your hand. It is yours now: you call it {mc.name}. '
             'It eats meat; orders on h.', 'gold')
    return True


def x_rite(game, sk, r):
    from . import mercs as MC
    mc = MC.fallen(game)
    if not mc:
        game.msg('Nobody of yours lies dead.')
        return False
    MC.raise_up(game, mc, free=True)
    return True


def x_shape(game, sk, r):
    p = game.player
    nm, dp, dr_, t = sk.shape
    p.buffs = [b for b in p.buffs if b[0] not in ('dmg', 'dr') or not b[3].endswith('shape')]
    p.buffs += [['dmg', dp + r // 4, t, f'{nm.capitalize()} shape'], ['dr', dr_, t, f'{nm.capitalize()} shape']]
    game.flash(ring_cells(p.x, p.y, 1), sk.color, sk.glyph, .25)
    game.msg({'bear': 'Your body thickens and your hands turn to claws: you are a bear.',
              'wolf': 'You drop to all fours, grey and lean: you are a wolf, and you hunt.'}.get(nm, f'You become a {nm}.'), 'good')
    return True


EXEC = {'summon': x_summon, 'raise': x_raise, 'burst': x_burst, 'tame': x_tame, 'rite': x_rite, 'shape': x_shape,
        'melee': x_melee, 'adjacent': x_adjacent, 'around': x_around, 'bolt': x_bolt, 'shot': x_shot, 'volley': x_volley,
        'pierce': x_pierce, 'chain': x_chain, 'storm': x_storm, 'target_area': x_target_area, 'curse': x_curse,
        'leap': x_leap, 'self': x_self}
