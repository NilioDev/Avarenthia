"""Classless skills. Fourteen disciplines grow by use; higher ranks unlock new skills in that
discipline. You carry six skills on your bar and can only change them in a town.

Each school of magic (and Warcraft) has eight tome skills, opening at ranks 0, 5, 12, 20, 30, 42, 55 and 70, and a rule
of its own that shows on the map (spellmap.py): fire burns the ground and burns hotter on the burning, frost makes ice,
water carries lightning, restoration sears the dead, shadow takes life and steals it back, the dead are the
necromancer's to raise, nature is strong where things grow, and a beastmaster works through the beast. The weapon
disciplines keep five tome skills, at 0, 8, 20, 35 and 55.

Two pools pay for them: the weapon skills and Warcraft (martial, any weapon, grows on Strength) cost stamina,
the spells cost mana."""
import random

from .worldgen import cheb, free_around

BAR_SIZE = 6
UNLOCKS = (0, 8, 20, 35, 55)                 # the weapon disciplines' tome skills, and the guilds' techniques
TOME = (0, 5, 12, 20, 30, 42, 55, 70)        # the schools of magic and Warcraft: eight tome skills each

DISCIPLINES = {
    'unarmed': dict(name='Unarmed', kind='weapon', weapon='empty hands'),
    'swords': dict(name='Swordsmanship', kind='weapon', weapon='a sword'),
    'axes': dict(name='Axes and Maces', kind='weapon', weapon='an axe, mace, club, flail or war hammer'),
    'spears': dict(name='Spears and Staves', kind='weapon', weapon='a spear, halberd, scythe or staff'),
    'daggers': dict(name='Daggers', kind='weapon', weapon='a dagger or throwing knives'),
    'archery': dict(name='Bows and Crossbows', kind='weapon', weapon='a bow, crossbow or sling'),
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
DISC_COLOR = {'unarmed': (230, 200, 170), 'swords': (220, 220, 230), 'axes': (210, 170, 120), 'spears': (200, 190, 150), 'daggers': (170, 200, 140), 'archery': (216, 208, 176),
              'fire': (255, 122, 44), 'frost': (159, 216, 255), 'storm': (242, 240, 122), 'restoration': (150, 255, 170),
              'shadow': (176, 110, 255), 'warcraft': (242, 196, 67), 'nature': (120, 200, 90), 'necromancy': (190, 200, 170),
              'beastcraft': (200, 150, 90)}
DISC_ORDER = list(DISCIPLINES)
WEAPON_LINE = {'dagger': 'daggers', 'shortsword': 'swords', 'longsword': 'swords', 'bastard': 'swords', 'runeblade': 'swords',
               'club': 'axes', 'mace': 'axes', 'waraxe': 'axes', 'staff': 'spears', 'warstaff': 'spears',
               'shortbow': 'archery', 'longbow': 'archery', 'warbow': 'archery',
               'greatsword': 'swords', 'greataxe': 'axes', 'maul': 'axes',
               'scimitar': 'swords', 'flail': 'axes', 'warhammer': 'axes', 'spear': 'spears', 'halberd': 'spears',
               'scythe': 'spears', 'throwknives': 'daggers', 'lightxbow': 'archery', 'heavyxbow': 'archery',
               'sling': 'archery'}
from . import data as _D  # noqa: E402
for _k, _b in _D.BASES.items():          # exceptional and elite grades fight like their family
    if _b.get('family') in WEAPON_LINE:
        WEAPON_LINE[_k] = WEAPON_LINE[_b['family']]


class Skill:
    def __init__(self, sid, name, line, tier, cost, cd, mode, **kw):
        self.id, self.name, self.line, self.tier = sid, name, line, tier
        self.unlock, self.step = UNLOCKS[min(4, tier)], tier          # set again below for the schools' tomes
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
        self.buff2 = kw.get('buff2')                 # a second state that comes with the buff (Frost Armor's chill)
        self.field = kw.get('field')                 # (tile, turns): what it leaves on the ground (spellmap.py)
        self.corpses = kw.get('corpses', 0)          # corpses near you it uses up
        self.need_beast = kw.get('need_beast', False)
        self.need_shield = kw.get('need_shield', False)  # works only with a shield in your other hand
        self.bonus_burning = kw.get('bonus_burning', 1)
        self.only_undead = kw.get('only_undead', False)
        self.life_frac = kw.get('life_frac', 0)      # paid in a share of the life you have
        self.both = kw.get('both', False)            # costs stamina and mana alike (martial and magic mixed)
        self.passive = kw.get('passive', False)      # a way of doing things, not a skill for the bar
        self.guild = False
        self.weapon_skill = False                    # set in weaponskills.py: keys 1-2, from the weapon in hand
        for k_, v_ in kw.items():                    # the weapon skills' own words: sunder, quick, width, push...
            if not hasattr(self, k_):
                setattr(self, k_, v_)


S = Skill
LEAF, BONE, BEAST = (120, 200, 90), (210, 210, 180), (200, 150, 90)
FIRE, ICE, STORM, HOLY, DARK, STEEL, ARROW, WAR = (255, 122, 44), (159, 216, 255), (242, 240, 122), (150, 255, 170), (176, 110, 255), (255, 106, 74), (216, 208, 176), (242, 196, 67)
SKILL_LIST = [
    # the weapon skills come with the weapon in hand (weaponskills.py), not from tomes
    # fire: the strongest against one; burning enemies take more fire, and fire leaves burning ground
    S('firebolt', 'Firebolt', 'fire', 0, 4, 1, 'bolt', lo=5, hi=9, r=.45, fx={'ignite': (.2, 3, .25, 4)}, color=FIRE),
    S('immolate', 'Immolate', 'fire', 1, 5, 6, 'curse', fx={'burn': (4, .35, 6)}, color=FIRE),
    S('searing_brand', 'Searing Brand', 'fire', 2, 7, 5, 'bolt', lo=10, hi=16, r=.6, range=6, bonus_burning=2, color=FIRE),
    S('fireball', 'Fireball', 'fire', 3, 9, 5, 'bolt', lo=9, hi=15, r=.6, splash=1, fx={'burn': (3, .25, 4)}, color=FIRE),
    S('flame_ring', 'Ring of Fire', 'fire', 4, 10, 10, 'around', lo=8, hi=13, r=.5, radius=1, field=(_D.BURNING, 6),
      fx={'burn': (3, .25, 4)}, color=FIRE),
    S('pyre', 'Pyre', 'fire', 5, 11, 8, 'pyre', lo=14, hi=22, r=.7, radius=2, color=FIRE),
    S('meteor', 'Meteor', 'fire', 6, 16, 16, 'bolt', lo=22, hi=34, r=1, splash=2, field=(_D.BURNING, 6), color=FIRE),
    S('heart_of_the_sun', 'Heart of the Sun', 'fire', 7, 22, 20, 'bolt', lo=40, hi=60, r=1.4, bonus_burning=2, color=(255, 214, 90)),
    # frost: defence and slowing; ice on the map
    S('frost_shard', 'Frost Shard', 'frost', 0, 4, 1, 'bolt', lo=4, hi=7, r=.4, fx={'slow': 3, 'freeze_chance': .2}, color=ICE),
    S('frost_armor', 'Frost Armor', 'frost', 1, 8, 40, 'self', buff=('def', 20, 1.2, 40), buff2=('chill', 1, 0, 40), color=ICE),
    S('ice_wall', 'Ice Wall', 'frost', 2, 7, 14, 'wall', color=ICE, glyph='█'),
    S('nova', 'Frost Nova', 'frost', 3, 9, 9, 'around', lo=4, hi=8, r=.4, radius=1, fx={'freeze': 3}, color=ICE),
    S('ice_lance', 'Ice Lance', 'frost', 4, 8, 4, 'bolt', lo=10, hi=16, r=.6, bonus_frozen=2.5, color=ICE),
    S('glacial_ward', 'Glacial Ward', 'frost', 5, 10, 30, 'self', buff=('ward', 30, 1.5, 30), color=ICE, glyph='#'),
    S('blizzard', 'Blizzard', 'frost', 6, 15, 15, 'target_area', lo=10, hi=18, r=.6, radius=2, fx={'slow': 4},
      field=(_D.DRIFT, 12), color=ICE),
    S('ice_tomb', 'Ice Tomb', 'frost', 7, 14, 60, 'tomb', color=ICE, glyph='█'),
    # storm: crowds; water conducts
    S('spark', 'Spark', 'storm', 0, 3, 1, 'bolt', lo=1, hi=13, r=.5, color=STORM, glyph='~'),
    S('static', 'Static Field', 'storm', 1, 6, 6, 'around', lo=4, hi=9, r=.35, radius=1, color=STORM, glyph='~'),
    S('gust', 'Gust', 'storm', 2, 6, 8, 'gust', lo=2, hi=5, r=.2, radius=2, color=(220, 230, 240), glyph='~'),
    S('chain', 'Chain Lightning', 'storm', 3, 10, 6, 'chain', lo=7, hi=14, r=.55, jumps=3, color=STORM, glyph='~'),
    S('thunderclap', 'Thunderclap', 'storm', 4, 7, 9, 'adjacent', dtype='spell', lo=9, hi=14, r=.5, fx={'stun': 2}, color=STORM, glyph='!'),
    S('ball_lightning', 'Ball Lightning', 'storm', 5, 12, 14, 'ball', lo=6, hi=11, r=.4, color=STORM, glyph='¤'),
    S('storm_call', 'Call the Storm', 'storm', 6, 16, 16, 'storm', lo=12, hi=22, r=.8, radius=8, jumps=6, color=STORM, glyph='~'),
    S('tempest', 'Tempest', 'storm', 7, 20, 40, 'tempest', lo=14, hi=24, r=.8, color=(255, 255, 255), glyph='~'),
    # restoration: keep you and your company whole; light against the dead
    S('mend', 'Mend', 'restoration', 0, 5, 3, 'self', heal=(10, .9), color=HOLY, glyph='+'),
    S('ward', 'Ward', 'restoration', 1, 6, 20, 'self', buff=('ward', 15, 1.0, 25), color=HOLY, glyph='#'),
    S('renewal', 'Renewal', 'restoration', 2, 6, 15, 'self', buff=('regen', 2, .08, 15), color=HOLY, glyph='+'),
    S('purify', 'Purify', 'restoration', 3, 6, 10, 'self', heal=(15, .8), cure=True, color=HOLY, glyph='+'),
    S('turn_undead', 'Turn Undead', 'restoration', 4, 8, 12, 'around', lo=8, hi=14, r=.5, radius=1, only_undead=True,
      fx={'fear': 5}, color=(255, 240, 200), glyph='+'),
    S('sanctuary', 'Sanctuary', 'restoration', 5, 10, 30, 'self', buff=('dr', 20, .3, 12), color=HOLY, glyph='+'),
    S('divine', 'Divine Light', 'restoration', 6, 14, 25, 'self', heal=(40, 2.2), cure=True, party=True, color=HOLY, glyph='+'),
    S('martyrs_grace', "Martyr's Grace", 'restoration', 7, 16, 80, 'self', buff=('martyr', 1, 0, 30), color=(255, 240, 200), glyph='+'),
    # shadow: curses, and the price; from rank 30 Morrak takes life as well as mana, and only shadow steals it back
    S('drain', 'Life Drain', 'shadow', 0, 4, 2, 'bolt', lo=4, hi=8, r=.4, drain=.5, color=DARK),
    S('weakness', 'Curse of Weakness', 'shadow', 1, 5, 8, 'curse', fx={'weaken': 8}, color=DARK),
    S('doom_mark', 'Mark of Doom', 'shadow', 2, 5, 8, 'curse', fx={'vuln': 10}, color=DARK),
    S('shadow_bolt', 'Shadow Bolt', 'shadow', 3, 8, 3, 'bolt', lo=10, hi=18, r=.65, color=DARK),
    S('dread', 'Dread', 'shadow', 4, 7, 12, 'around', dtype='none', radius=1, fx={'fear': 4}, life_cost=4, color=DARK, glyph='!'),
    S('plague', 'Plague', 'shadow', 5, 10, 10, 'around', lo=2, hi=5, r=.2, radius=2, fx={'poison': (4, .3, 8), 'plague': 8},
      life_cost=6, color=DARK),
    S('soul_harvest', 'Soul Harvest', 'shadow', 6, 15, 16, 'around', lo=10, hi=16, r=.6, radius=2, drain=.35, life_cost=10, color=DARK),
    S('morraks_bargain', "Morrak's Bargain", 'shadow', 7, 20, 30, 'around', lo=30, hi=50, r=1.2, radius=3, life_frac=.25,
      color=(200, 40, 60)),
    # necromancy: the dead fight for you; corpses are the resource
    S('grave_touch', 'Grave Touch', 'necromancy', 0, 4, 2, 'bolt', lo=4, hi=7, r=.4, range=4, fx={'slow': 3}, color=BONE),
    S('bone_spear', 'Bone Spear', 'necromancy', 1, 6, 4, 'pierce', lo=6, hi=11, r=.5, color=BONE, glyph='='),
    S('bone_shield', 'Bone Shield', 'necromancy', 2, 6, 25, 'self', buff=('dr', 20, .3, 20), corpses=1, color=BONE, glyph='#'),
    S('raise_skeleton', 'Raise Skeleton', 'necromancy', 3, 10, 25, 'summon', summon=('skeleton', 1, 30), corpses=1, color=BONE, glyph='z'),
    S('grave_mist', 'Grave Mist', 'necromancy', 4, 8, 8, 'mist', lo=3, hi=6, r=.25, fx={'poison': (3, .25, 6)}, color=(160, 200, 120)),
    S('bone_prison', 'Bone Prison', 'necromancy', 5, 10, 14, 'prison', color=BONE, glyph='#'),
    S('withering', 'Withering', 'necromancy', 6, 14, 14, 'around', lo=8, hi=14, r=.5, radius=2, fx={'weaken': 6}, color=BONE),
    S('army_of_the_dead', 'Army of the Dead', 'necromancy', 7, 20, 50, 'army', summon=('skeleton', 6, 25), radius=3, color=BONE, glyph='z'),
    # nature: the ground; stronger in forest and grass, weaker in desert, on ice and under the ground
    S('thorn_lash', 'Thorn Lash', 'nature', 0, 4, 1, 'bolt', lo=4, hi=8, r=.4, fx={'bleed': (2, .15, 4)}, color=LEAF, glyph='~'),
    S('barkskin', 'Barkskin', 'nature', 1, 6, 30, 'self', buff=('def', 25, 1.3, 30), color=LEAF, glyph='#'),
    S('grasping_roots', 'Grasping Roots', 'nature', 2, 7, 10, 'target_area', dtype='none', radius=1, fx={'stun': 2},
      field=(_D.ROOTS, 8), color=LEAF, glyph='"'),
    S('bramble_patch', 'Bramble Patch', 'nature', 3, 8, 12, 'target_area', dtype='none', radius=1, field=(_D.BRAMBLE, 14),
      color=(154, 176, 72), glyph='♠'),
    S('healing_rain', 'Healing Rain', 'nature', 4, 10, 20, 'self', heal=(18, 1.2), buff=('regen', 2, .06, 12), party=True,
      color=(130, 200, 255), glyph='+'),
    S('swarm', 'Swarm', 'nature', 5, 9, 10, 'curse', fx={'swarm': (4, .35, 8)}, color=(200, 190, 90), glyph='∙'),
    S('wrath_of_oak', 'Wrath of the Oak', 'nature', 6, 14, 14, 'around', lo=12, hi=20, r=.6, radius=2, fx={'stun': 2},
      color=LEAF, glyph='♣'),
    S('awaken_the_wood', 'Awaken the Wood', 'nature', 7, 16, 50, 'awaken', color=LEAF, glyph='♠'),
    # beastcraft: everything through your beast
    S('feral_howl', 'Feral Howl', 'beastcraft', 0, 4, 10, 'around', dtype='none', radius=1, fx={'weaken': 5}, color=BEAST, glyph='!'),
    S('tame', 'Tame', 'beastcraft', 1, 8, 20, 'tame', color=BEAST, glyph='♥'),
    S('sic_em', "Sic 'Em", 'beastcraft', 2, 5, 8, 'sic', fx={'stun': 2}, need_beast=True, color=BEAST, glyph='!'),
    S('mend_beast', 'Lick the Wounds', 'beastcraft', 3, 5, 8, 'self', heal=(10, .8), party=True, need_beast=True, color=BEAST, glyph='+'),
    S('call_wolf', 'Call a Wolf', 'beastcraft', 4, 10, 30, 'summon', summon=('wolf', 1, 30), color=BEAST, glyph='C'),
    S('bond_of_blood', 'Bond of Blood', 'beastcraft', 5, 8, 30, 'self', buff=('bond', 30, .2, 20), need_beast=True,
      color=(200, 60, 60), glyph='♥'),
    S('alpha_roar', 'Alpha Roar', 'beastcraft', 6, 12, 18, 'around', dtype='none', radius=2, fx={'stun': 2, 'weaken': 6},
      fury=12, need_beast=True, color=BEAST, glyph='!'),
    S('spirit_of_the_pack', 'Spirit of the Pack', 'beastcraft', 7, 14, 45, 'spirit', need_beast=True, color=(230, 200, 140), glyph='C'),
    # warcraft (martial, stamina): shouts and stances, with any weapon in hand
    S('warcry', 'War Cry', 'warcraft', 0, 5, 12, 'around', dtype='none', radius=1, fx={'stun': 1}, color=WAR, glyph='!'),
    S('rage', 'Battle Rage', 'warcraft', 1, 6, 25, 'self', buff=('dmg', 20, .5, 12), color=WAR, glyph='!'),
    S('brace', 'Brace', 'warcraft', 2, 5, 18, 'self', buff=('dr', 20, .25, 8), color=WAR, glyph='#'),
    S('second_wind', 'Second Wind', 'warcraft', 3, 6, 30, 'self', heal=(20, 1.5), cure=True, color=WAR, glyph='+'),
    S('iron_skin', 'Iron Skin', 'warcraft', 4, 8, 30, 'self', buff=('dr', 25, .3, 10), color=WAR, glyph='#'),
    S('rally', 'Rally', 'warcraft', 5, 10, 35, 'self', heal=(15, 1.0), buff=('dmg', 15, .3, 12), party=True, fury=12, color=WAR, glyph='!'),
    S('charge', 'Charge', 'warcraft', 6, 9, 12, 'leap', pct=200, pct_r=2, range=6, fx={'stun': 2}, color=WAR),
    S('unbroken', 'Unbroken', 'warcraft', 7, 10, 45, 'self', buff=('unbroken', 3, .05, 15), color=WAR, glyph='#'),
]
# techniques taught only by guild masters (see guilds.py); they never turn up in tomes
TECHNIQUES = [
    S('mage_armor', 'Mage Armor', 'frost', 1, 8, 30, 'self', buff=('dr', 15, .25, 20), color=ICE, flavor='Circle of Magi'),
    S('arcane_barrage', 'Arcane Barrage', 'storm', 2, 12, 6, 'chain', lo=9, hi=17, r=.6, jumps=4, color=STORM, glyph='~',
      flavor='Circle of Magi'),
    S('inferno', 'Inferno', 'fire', 4, 18, 14, 'around', lo=16, hi=26, r=.8, radius=2, fx={'burn': (5, .4, 6)}, field=(_D.BURNING, 6), color=FIRE,
      flavor='Circle of Magi'),
    S('shield_wall', 'Shield Wall', 'warcraft', 1, 6, 25, 'self', buff=('def', 40, 1.5, 15), color=WAR, glyph='#',
      flavor='Iron Company'),
    S('shield_bash', 'Shield Bash', 'warcraft', 0, 4, 6, 'bash', pct=60, pct_r=1, fx={'stun': 1}, need_shield=True,
      color=WAR, glyph='(', flavor='Iron Company'),
    S('block', 'Block', 'warcraft', 1, 5, 14, 'self', buff=('block', 1, 0, 6), need_shield=True, color=WAR, glyph='(',
      flavor='Iron Company'),
    S('battle_drill', 'Battle Drill', 'warcraft', 2, 8, 22, 'self', buff=('dmg', 30, .6, 14), color=WAR, glyph='!', flavor='Iron Company'),
    S('last_stand', 'Last Stand', 'warcraft', 4, 12, 40, 'self', heal=(40, 2), buff=('dr', 35, .3, 8), cure=True, color=WAR, glyph='+',
      flavor='Iron Company'),
    S('smite', 'Smite', 'restoration', 1, 6, 3, 'bolt', lo=8, hi=14, r=.5, undead=2, color=HOLY, glyph='+', flavor='Order of Dawn'),
    S('holy_shield', 'Holy Shield', 'restoration', 2, 10, 30, 'self', buff=('dr', 30, .3, 12), color=HOLY, glyph='+',
      flavor='Order of Dawn'),
    S('dawnbreak', 'Dawnbreak', 'restoration', 4, 16, 16, 'around', lo=14, hi=24, r=.7, radius=2, undead=2.5, color=HOLY, glyph='*',
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
    S('pact_of_blood', 'Pact of Blood', 'shadow', 2, 4, 30, 'self', buff=('dmg', 40, .6, 15), life_cost=8, color=(200, 40, 60), glyph='!',
      flavor='Hollow Coven'),
    S('morraks_hand', "Morrak's Hand", 'shadow', 4, 18, 16, 'around', lo=18, hi=30, r=.9, radius=2, drain=.5, life_cost=12, color=DARK,
      flavor='Hollow Coven'),
    # for those who serve two guilds
    S('spellblade', 'Spellblade', 'warcraft', 2, 8, 6, 'melee', dtype='weapon', pct=210, pct_r=2, fx={'burn': (4, .3, 5)}, both=True, color=FIRE,
      flavor='Iron Company and Circle of Magi'),
    S('soul_knife', 'Soul Knife', 'shadow', 2, 8, 4, 'bolt', lo=12, hi=22, r=.7, drain=.4, range=3, color=DARK,
      flavor="Thieves' Guild and Hollow Coven"),
    S('thornstorm', 'Thornstorm', 'storm', 2, 12, 10, 'around', lo=10, hi=18, r=.6, radius=2, fx={'bleed': (3, .25, 5), 'stun': 1},
      color=(160, 220, 110), glyph='~', flavor='Wardens and Circle of Magi'),
    S('crusade', 'Crusade', 'warcraft', 2, 10, 30, 'self', buff=('dmg', 45, .6, 15), both=True, color=(255, 232, 160), glyph='!',
      flavor='Order of Dawn and Iron Company'),
    # the Green Moot
    S('entangle', 'Entangle', 'nature', 1, 7, 12, 'around', dtype='none', radius=1, fx={'stun': 1}, field=(_D.ROOTS, 8), color=LEAF, glyph='"',
      flavor='The Green Moot'),
    S('spirit_totem', 'Spirit Totem', 'nature', 2, 10, 30, 'totem', heal=(3, .1), color=(140, 230, 160), glyph='¶', flavor='The Green Moot'),
    S('wild_shape', 'Wild Shape', 'nature', 4, 12, 50, 'shape', shape=('bear', 35, 25, 25), color=BEAST, glyph='q',
      flavor='The Green Moot'),
    # the Hallowed Chapter
    S('mass_mend', 'Mass Mend', 'restoration', 1, 8, 8, 'self', heal=(16, 1.1), party=True, color=HOLY, glyph='+',
      flavor='The Hallowed Chapter'),
    S('hallowed_ground', 'Hallowed Ground', 'restoration', 2, 10, 30, 'around', dtype='none', radius=3, field=(_D.HALLOWED, 20),
      color=(255, 240, 200), glyph='+', flavor='The Hallowed Chapter'),
    S('rite_of_return', 'Rite of Return', 'restoration', 4, 20, 80, 'rite', color=HOLY, glyph='+', flavor='The Hallowed Chapter'),
    # the Quiet Ossuary
    S('raise_dead', 'Raise Dead', 'necromancy', 1, 10, 20, 'raise', color=BONE, glyph='z', flavor='The Quiet Ossuary'),
    S('bone_golem', 'Bone Golem', 'necromancy', 2, 14, 40, 'golem', corpses=3, color=BONE, glyph='Z', flavor='The Quiet Ossuary'),
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
    S('pack_fury', 'Pack Fury', 'beastcraft', 1, 10, 30, 'self', buff=('dmg', 25, .5, 15), fury=15, color=(230, 120, 60), glyph='!',
      flavor="The Houndwardens' Lodge"),
    S('call_of_the_pack', 'Call of the Pack', 'beastcraft', 2, 12, 40, 'summon', summon=('wolf', 2, 30), color=BEAST, glyph='C',
      flavor="The Houndwardens' Lodge"),
    S('packmaster', 'Packmaster', 'beastcraft', 4, 0, 0, 'passive', passive=True, color=BEAST, glyph='C',
      flavor="The Houndwardens' Lodge"),
    # for those who serve two guilds
    S('wildheart', 'Wildheart', 'nature', 2, 12, 50, 'shape', shape=('wolf', 55, 10, 25), fury=25, color=BEAST, glyph='C',
      flavor='Green Moot and Wardens'),
    S('lichcraft', 'Lichcraft', 'necromancy', 2, 10, 12, 'around', lo=14, hi=24, r=.8, radius=2, life_cost=12,
      fx={'weaken': 6}, color=(150, 120, 220), flavor='Quiet Ossuary and Hollow Coven'),
    S('mendicant', "Mendicant's Fist", 'unarmed', 2, 6, 5, 'melee', pct=190, pct_r=2, heal=(6, .5), fx={'stun': 1},
      color=HOLY, flavor='Still Hand and Order of Dawn'),
    S('war_handler', 'War-Handler', 'beastcraft', 2, 12, 40, 'summon', summon=('war_dog', 2, 40), fury=20, color=(200, 170, 120),
      glyph='C', flavor="Houndwardens and Iron Company"),
]
for _t in TECHNIQUES:
    _t.guild = True
for _s in SKILL_LIST:
    if DISCIPLINES[_s.line]['kind'] != 'weapon':
        _s.unlock, _s.step = TOME[_s.tier], _s.tier * 4 / 7
    if _s.line == 'restoration':                 # light against the dead
        _s.undead = max(2, _s.undead)
for _t in TECHNIQUES:
    if _t.line == 'restoration':
        _t.undead = max(2, _t.undead)
SKILLS = {s.id: s for s in SKILL_LIST + TECHNIQUES}
STARTING_BAR = ['power_strike', 'firebolt', 'mend', None, None, None]


def pool(sk):
    """What a skill costs: 'stamina' for the weapon skills and Warcraft, 'mana' for spells."""
    return 'stamina' if DISCIPLINES[sk.line]['kind'] in ('weapon', 'martial') else 'mana'


def cost_of(game, sk):
    gnome = getattr(game.player, 'race', '') == 'gnome' and pool(sk) == 'mana'
    c = sk.cost * (.85 if gnome else 1)
    if pool(sk) == 'mana':
        from . import weaponskills as WS
        c *= WS.mana_mult(game)                     # a staff: spells cost less
        c *= 1 - sum(b[1] for b in game.player.buffs if b[0] == 'focus') / 100
    return max(1, round(c))


def can_pay(game, sk):
    p = game.player
    c = cost_of(game, sk)
    if sk.both:
        return getattr(p, 'stamina', 0) >= c and p.mana >= c
    return (getattr(p, 'stamina', 0) if pool(sk) == 'stamina' else p.mana) >= c


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
        parts.append(f"Affect every enemy within {sk.radius} tile{'s' if sk.radius > 1 else ''}{(' for ' + dmg) if dmg else ''}.")
    elif m in ('bolt', 'shot'):
        parts.append(f"{'Shoot' if m == 'shot' else 'Hurl a bolt at'} the nearest enemy{' twice' if m == 'shot' and sk.hits == 2 else ''} for {dmg}." + (f' Splashes {sk.splash} tile{"s" if sk.splash > 1 else ""} around the target.' if sk.splash else ''))
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
        if sk.corpses:
            parts.append(f'A corpse near you rises as {one} and fights at your side for {t + r // 2} turns.')
        else:
            parts.append(f"Call {one if n == 1 else f'{n} {many}'} to fight at your side for {t + r // 2} turns.")
    elif m == 'raise':
        parts.append(f'A corpse near you rises as what it was, with its own attacks, and fights for you for {20 + r // 2} turns.')
    elif m == 'tame':
        parts.append('Tame the wolf, bear, panther or hawk next to you; easier when it is hurt. It stays with you, '
                     'eats meat and takes orders (h). One beast at a time; a Packmaster keeps two.')
    elif m == 'rite':
        parts.append('Raise your fallen hireling or beast where it lies, without a temple.')
    elif m == 'burst':
        parts.append(f'The nearest corpse bursts: {dmg} to every enemy within {sk.radius} tiles of it.')
    elif m == 'shape':
        nm, dp, dr_, t = sk.shape
        parts.append(f'Take the shape of a {nm} for {t} turns: +{dp + r // 4}% damage, {dr_}% less damage taken.')
    elif m == 'wall':
        parts.append(f"Raise a wall of ice, {3 + (r >= 30) + (r >= 60)} tiles wide, across the way to the nearest enemy. "
                     f"It melts after {14 + r // 5} turns.")
    elif m == 'gust':
        parts.append(f"Throw every enemy within {sk.radius} tiles {2 + (r >= 40)} tiles back, for {dmg}.")
    elif m == 'ball':
        parts.append(f'A ball of lightning rolls towards the nearest enemy for {8 + r // 20} turns, striking all beside it '
                     f'for {dmg} each turn.')
    elif m == 'tempest':
        parts.append(f'For {5 + r // 20} turns lightning comes down on an enemy in sight every turn.')
    elif m == 'tomb':
        parts.append(f'Shut yourself in ice for {4 + r // 30} turns: nothing can hurt you and you heal, but you can do nothing.')
    elif m == 'pyre':
        parts.append(f'The nearest burning enemy bursts for {dmg}; its fire leaps to every enemy within {sk.radius} tiles.')
    elif m == 'mist':
        parts.append(f'Every corpse near you breathes out poison: {dmg} to each enemy beside one.')
    elif m == 'prison':
        parts.append(f'Walls of bone close around the nearest enemy; it is held for {4 + r // 15} turns.')
    elif m == 'army':
        k, n, t = sk.summon
        parts.append(f'Every corpse within {sk.radius} tiles, up to {n + r // 25}, rises as a skeleton for {t + r // 2} turns.')
    elif m == 'awaken':
        parts.append(f'A tree beside you wakes and fights for you for {30 + r // 2} turns. Only where trees stand.')
    elif m == 'sic':
        parts.append('Your beast springs at the nearest enemy and strikes.')
    elif m == 'spirit':
        parts.append(f'Your beast grows for {15 + r // 5} turns: 40% more life and damage.')
    elif m == 'totem':
        parts.append(f'Drive a totem into the ground beside you; for 20 turns it heals you and your company next to it '
                     f'{round(sk.heal[0] + sk.heal[1] * r)} life a turn.')
    elif m == 'golem':
        parts.append('Three corpses become one Bone Golem, which stays with you until it falls.')
    elif m == 'passive':
        parts.append('You may keep two tamed beasts instead of one. Nothing to put on the bar.')
    elif m == 'bash':
        parts.append(f'Drive your shield into the enemy beside you for {dmg} and push it back a tile.' if sk.need_shield
                     else f'Strike the enemy beside you for {dmg} and drive it back {getattr(sk, "push", 1)} tiles.')
    elif m == 'arc':
        far = getattr(sk, 'reach', 1) > 1
        parts.append(f"Sweep {'the' if not far else 'two tiles out over the'} {sk.width} tiles in front of you for {dmg}."
                     + (' Every foe struck gives you some life.' if getattr(sk, 'leech', 0) else ''))
    elif m == 'dervish':
        parts.append(f'Spin through up to two enemies beside you for {dmg}; it counts as a step for a scimitar.')
    elif m == 'hook':
        parts.append(f'Hook an enemy two tiles away, pull it a tile towards you and strike for {dmg}.')
    elif m == 'throw':
        parts.append(f'Throw your spear at an enemy up to {sk.range} tiles away for a hard blow. It lies where it fell.')
    elif m == 'fan':
        parts.append(f'Throw three knives at up to three enemies for {dmg} each.')
    elif m == 'area_shot':
        parts.append(f'Arrows rain on your target and every enemy beside it for {dmg}.')
    elif m == 'snap':
        parts.append(f'Shoot the nearest enemy for {dmg}, then step back from it.')
    elif m == 'skip':
        parts.append(f'A stone strikes the nearest enemy for {dmg} and skips on to a second within three tiles.')
    elif m == 'focus':
        parts.append('A turn of stillness: some mana comes back, and your next spell costs a third less.')
    elif m == 'reload':
        parts.append('Brace and wind your crossbow at once.')
    if sk.need_shield:
        parts.append('Needs a shield in your other hand.')
    if getattr(sk, 'sunder', False):
        parts.append('Goes through heavy armour.')
    if getattr(sk, 'armoured', 0) > 1:
        parts.append(f'x{sk.armoured:g} against the armoured.')
    if getattr(sk, 'unseen', 0) > 1:
        parts.append(f'x{sk.unseen:g} on a foe that has not seen you.')
    if getattr(sk, 'unblockable', False):
        parts.append('No shield or guard stops it.')
    if getattr(sk, 'rune', False):
        parts.append('The runes add a little damage of your first school.')
    if getattr(sk, 'quick', False):
        parts.append('Half a turn: every second one costs none.')
    if getattr(sk, 'push', 0) and m != 'bash':
        parts.append(f"Drives the foe back {sk.push} tile{'s' if sk.push > 1 else ''}.")
    if sk.field:
        parts.append({_D.BURNING: 'Leaves burning ground.', _D.ROOTS: 'Leaves grasping roots that hold who stands in them.',
                      _D.BRAMBLE: 'Leaves brambles that make who walks through them bleed.',
                      _D.DRIFT: 'Leaves snowdrifts that slow who wades through them.',
                      _D.HALLOWED: 'Makes the ground hallowed for 20 turns: the undead cannot step onto it.'}.get(sk.field[0], ''))
    if sk.heal and m != 'totem':
        parts.append(f'Heals {round(sk.heal[0] + sk.heal[1] * r)} life.')
    if sk.buff:
        k, b, br, t = sk.buff
        v = round(b + br * r)
        parts.append({'def': f'+{v} defense', 'regen': f'+{v} life per turn', 'dr': f'{min(60, v)}% less damage taken',
                      'dmg': f'+{v}% damage', 'ward': f'A ward takes the next {v} damage', 'bond': f'Your beast takes {min(50, v)}% '
                      'of the blows you take', 'unbroken': f'Every blow you take gives you {v} stamina',
                      'martyr': 'A blow that would kill you leaves you on one life, once,',
                      'block': 'Your shield catches the first blow each turn, all of it; a flail swings over it,',
                      'feint': 'Your next blow goes past a shield or a guard;', 'riposte': 'The first blow at you is '
                      'turned aside and answered with a strike,', 'keepback': 'Who comes up beside you meets your point '
                      'first,'}[k]
                     + f' for {t} turns.')
    if sk.buff2 and sk.buff2[0] == 'chill':
        parts.append('Who strikes you in melee is slowed.')
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
    if 'ignite' in fx:
        parts.append(f"{round(fx['ignite'][0] * 100)}% chance to set it burning.")
    if 'swarm' in fx:
        b, br, t = fx['swarm']
        parts.append(f'A swarm stings it for {round(b + br * r)} a turn over {t} turns.')
    if 'silence' in fx:
        parts.append(f"It cannot cast for {fx['silence']} turns.")
    if 'sunder' in fx:
        parts.append(f"Breaks its guard for {fx['sunder']} turns: armour stops nothing, and blows bite deeper.")
    if 'slow' in fx:
        parts.append(f"Slows for {fx['slow']} turns.")
    if 'fear' in fx:
        parts.append(f"{'The undead flee' if sk.only_undead else 'They flee'} for {fx['fear']} turns.")
    if 'plague' in fx:
        parts.append('When a plagued enemy dies, the plague leaps to those beside it.')
    if 'weaken' in fx:
        parts.append(f"Weakened enemies deal 30% less damage for {fx['weaken']} turns.")
    if 'vuln' in fx:
        parts.append(f"Target takes 25% more damage for {fx['vuln']} turns.")
    if sk.drain:
        parts.append(f'Heals you for {round(sk.drain * 100)}% of the damage.')
    if sk.line == 'restoration' and sk.dtype == 'spell':
        parts.append(f'x{max(2, sk.undead):g} damage against the undead.')
    if sk.party:
        parts.append('Heals your hireling and your beast as well.')
    if sk.fury:
        parts.append(f'Your beast fights 40% harder for {sk.fury} turns.')
    if sk.life_cost:
        parts.append(f'Costs {sk.life_cost} life.')
    if sk.life_frac:
        parts.append(f'Costs {round(sk.life_frac * 100)}% of your life.')
    if sk.corpses and m not in ('golem', 'summon'):
        parts.append('Uses up a corpse near you.' if sk.corpses == 1 else f'Uses up {sk.corpses} corpses near you.')
    if sk.need_beast:
        parts.append('Needs your beast at your side.')
    if sk.both:
        parts.append('Costs stamina and mana alike.')
    if sk.bonus_burning > 1:
        parts.append(f'x{sk.bonus_burning:g} damage against burning enemies.')
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
    from . import classes as CL
    i = CL.place(game, sid)
    if i is not None:
        game.msg(f'{sk.name} is now on key {i + 1}.', 'info')
    else:
        game.msg('Change your skills in a town or stronghold (Z).', 'info')
    return True


# ------------------------------------------------------------------ using
def use(game, slot):
    p = game.player
    from . import classes as CL
    from . import weaponskills as WS
    sid = CL.slot_skill(game, slot)
    if not sid:
        if slot in CL.WEAPON:
            locked = WS.second_locked(game)
            game.msg(f'{SKILLS[locked].name} comes to you at {DISCIPLINES[SKILLS[locked].line]["name"]} {WS.SECOND}.'
                     if locked else 'Your weapon has no skill here.')
        else:
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
    if sk.passive:
        game.msg(f'{sk.name} needs no calling: it is simply how you do things.')
        return 0
    if not can_pay(game, sk):
        game.msg(f"Not enough {'stamina and mana' if sk.both else kind} for {sk.name} ({cost} needed).", 'bad')
        return 0
    d = DISCIPLINES[sk.line]
    if d['kind'] == 'weapon' and not sk.weapon_skill and weapon_line(game) != sk.line:
        game.msg(f"{sk.name} needs {d['weapon']} in your hands.", 'bad')
        return 0
    from . import weapons as WP
    if sk.weapon_skill and sk.mode in WS.RANGED_MODES and WP.unloaded(game):
        game.msg('Wind your crossbow first: [f].', 'bad')
        return 0
    if sk.need_shield:
        from . import weapons as WP
        if not WP.has_shield(game):
            game.msg(f'{sk.name} needs a shield in your other hand.', 'bad')
            return 0
    if sk.life_cost and p.life <= sk.life_cost + 1:
        game.msg(f'{sk.name} would take more life than you have.', 'bad')
        return 0
    if sk.need_beast:
        from . import mercs as MC
        if not with_beast(game):
            game.msg(f'{sk.name} needs your beast at your side.' if MC.beasts(game) else
                     f'{sk.name} needs a beast of your own: tame one first.', 'bad')
            return 0
    if sk.corpses and sk.mode == 'self':
        from . import spellmap as SM
        if not SM.use_corpses(game, sk.corpses):
            game.msg(f"{sk.name} needs {'a corpse' if sk.corpses == 1 else f'{sk.corpses} corpses'} near you.", 'bad')
            return 0
    r = rank(game, sk.line)
    game._skill = sk
    try:
        if not EXEC[sk.mode](game, sk, r):
            return 0
    finally:
        game._skill = None
    if sk.weapon_skill and sk.mode in WS.RANGED_MODES and WP.wielded(game) in WP.CROSSBOWS:
        WP.main_hand(game).unloaded = True
    if pool(sk) == 'mana':
        p.buffs = [b for b in p.buffs if b[0] != 'focus']   # Focus is spent on one spell
    price = sk.life_cost + (round(p.life * sk.life_frac) if sk.life_frac else 0)
    if price:
        p.life = max(1, p.life - price)
        game.num(p.x, p.y, f'-{price}', (200, 40, 60))
        game.msg(f'{sk.name} takes its price in life.' if sk.line != 'shadow' else 'Morrak takes his price in life.', 'bad')
    if sk.heal and sk.mode not in ('self',):
        game.heal(round(sk.heal[0] + sk.heal[1] * r), show=True)
    if sk.fury:
        from . import mercs as MC
        bst = MC.with_you(game, 'beast')
        for bst in [b for b in (MC.with_you(game, 'beast'), MC.with_you(game, 'beast2')) if b]:
            bst.fury = max(bst.fury, sk.fury)
            game.msg(f'{bst.name} bristles and bares its teeth.', 'good')
    if kind == 'stamina' or sk.both:
        p.stamina -= cost
        p.strained = game.turn
    if kind == 'mana' or sk.both:
        p.mana -= cost
    p.cooldowns[sid] = sk.cd
    gain(game, sk.line, 3)
    if getattr(sk, 'quick', False):                 # half a turn: every second one costs none
        p.quick = not getattr(p, 'quick', False)
        if not p.quick:
            return 0
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
    if sk.line == 'nature':
        from . import spellmap as SM
        dmg = round(dmg * SM.nature_factor(game))
    return dmg


def _hit(game, mon, sk, r, ranged=False):
    """Apply one hit of this skill to a monster. Returns True if it died."""
    if mon.hp <= 0 or mon not in game.map.mons:
        return True
    from . import weapons as WP
    from . import weaponskills as WS
    crit = sk.crit or (not sk.weapon_skill and random.random() < WS.class_crit(game, mon) / 100)
    if sk.dtype == 'weapon':
        pct = sk.pct + sk.pct_r * r
        if sk.execute > 1 and mon.hp < mon.maxhp * .3:
            pct *= sk.execute
        if getattr(sk, 'armoured', 0) and WP.armoured(mon):
            pct *= sk.armoured
        if getattr(sk, 'unseen', 0) and not mon.awake:
            pct *= sk.unseen
        game._unblockable = getattr(sk, 'unblockable', False) or any(b[0] == 'feint' for b in game.player.buffs)
        before = mon.hp
        try:
            dead = game.weapon_strike(mon, pct, force_crit=crit, ranged=ranged, sunder=getattr(sk, 'sunder', False))
        finally:
            game._unblockable = False
        game.player.buffs = [b for b in game.player.buffs if b[0] != 'feint']
        if sk.weapon_skill and sk.mode in ('melee', 'leap', 'hook', 'bash', 'dervish') and not dead:
            WS.swing(game, [(mon.x, mon.y)])
        if getattr(sk, 'rune', False) and not dead:
            dead = WS.rune_extra(game, mon)
        if getattr(sk, 'push', 0) and not dead:
            WS.push(game, mon, sk.push)
        dealt = before - max(0, mon.hp)
    elif sk.dtype == 'spell':
        dmg = _spell_dmg(game, sk, r)
        game._area = sk.mode in ('around', 'chain', 'storm', 'target_area', 'volley')
        if sk.bonus_frozen > 1 and mon.hold > 0:
            dmg *= sk.bonus_frozen
        if sk.undead > 1 and not mon.is_npc and (mon.k in _D.UNDEAD or mon.tpl.get('family') == 'undead'):
            dmg *= sk.undead
        if sk.line == 'fire' and 'burn' in mon.effects:
            dmg *= sk.bonus_burning if sk.bonus_burning > 1 else 1.25      # the burning burn hotter
        if sk.line == 'storm':
            from . import spellmap as SM
            if SM.wet(game, mon):
                dmg *= 1.25                                                # water carries the arc
        before = mon.hp
        dead = game.damage_mon(mon, dmg, crit, col=sk.color, elem=LINE_ELEM.get(sk.line))
        game._area = False
        dealt = before - max(0, mon.hp)
        if sk.drain:
            game.heal(round(dealt * sk.drain))
            if dealt > 0:
                p = game.player
                path = game.cells_between((mon.x, mon.y), (p.x, p.y))[:-1]
                from . import anim as AN            # after the blow lands, your life flows back
                game.fx('drain', cells=path, col=(220, 60, 70), delay=AN.bolt_time(len(path) + 1))
    else:
        dead = False
    if not dead:
        apply_fx(game, mon, sk, r)
        if not sk.weapon_skill and sk.dtype != 'none':
            WS.class_hit(game, mon, sk)
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
            if k == 'bleed':
                game.fx('blood', x=mon.x, y=mon.y, src=(game.player.x, game.player.y))
    if 'ignite' in fx and random.random() < fx['ignite'][0]:
        _c, b, br, t = fx['ignite']
        mon.effects['burn'] = [t, max(1, round(b + br * r))]
    if 'swarm' in fx:
        b, br, t = fx['swarm']
        v = max(1, round((b + br * r) * (_nat(game) if sk.line == 'nature' else 1)))
        mon.effects['swarm'] = [t, v]
    for k in ('weaken', 'vuln', 'slow', 'fear', 'silence', 'sunder'):
        if k in fx:
            mon.effects[k] = [fx[k], 0]
    if 'plague' in fx:
        mon.effects['plague'] = [fx['plague'], max(1, round(4 + .3 * r))]
    mon.awake = True


def _nat(game):
    from . import spellmap as SM
    return SM.nature_factor(game)


def with_beast(game):
    """Your beast, if one stands with you on this map (the first of two)."""
    from . import mercs as MC
    for mc in (MC.with_you(game, 'beast'), MC.with_you(game, 'beast2')):
        if mc and mc.body is not None and mc.body in game.map.mons:
            return mc
    return None


def lay(game, sk, r, cells):
    """What the spell leaves on the ground: its own tile, ice on water for frost, a grass fire in a dry summer."""
    from . import spellmap as SM
    m = game.map
    if sk.field:
        tile, turns = sk.field
        power = max(2, round(2 + r / 8))
        n = SM.area(game, m, cells, tile, turns, power)
        if n and tile == _D.BURNING:
            SM.grass_fire(game, m, *cells[0])
    if sk.line == 'frost' and sk.mode in ('around', 'target_area', 'bolt'):
        SM.freeze_water(game, cells)


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
    if not sk.weapon_skill:
        game.flash([(t.x, t.y)], sk.color, '/', .14)
    for _ in range(sk.hits):
        if _hit(game, t, sk, r):
            break
    return True


def x_bash(game, sk, r):
    """Shield Bash: your shield drives the foe back a tile and stuns it."""
    p, m = game.player, game.map
    t = _melee_target(game)
    if not t:
        game.msg('No enemy within reach.')
        return False
    p.last_target = t.id
    if sk.need_shield:                              # Shield Bash: a grey ] on the foe, and it goes back a tile
        game.wear('shield', .3)
        game.flash([(t.x, t.y)], (200, 200, 205), ']', .14)
        from . import weaponskills as WS
        WS.push(game, t, 1)
    _hit(game, t, sk, r)                            # Push Back pushes after its blow (sk.push)
    return True


def x_adjacent(game, sk, r):
    p = game.player
    t = [o for o in game.visible_hostiles() if cheb(o.x, o.y, p.x, p.y) <= 1]
    if not t:
        game.msg('No enemies next to you.')
        return False
    if getattr(sk, 'spin', False):
        game.fx('spin', x=p.x, y=p.y, col=sk.color)
    else:
        _ring(game, sk, p.x, p.y, 1)
    for o in t:
        _hit(game, o, sk, r)
    return True


def x_around(game, sk, r):
    p = game.player
    t = [o for o in game.visible_hostiles() if cheb(o.x, o.y, p.x, p.y) <= sk.radius]
    if sk.only_undead:
        from . import spellmap as SM
        t = [o for o in t if SM.undead(o)]
    cells = []
    for rr in range(1, sk.radius + 1):
        cells += ring_cells(p.x, p.y, rr)
    _ring(game, sk, p.x, p.y, sk.radius)
    lay(game, sk, r, cells)
    if not t:
        game.msg('No undead in range.' if sk.only_undead else 'No enemies in range.')
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
    tx, ty = t.x, t.y
    if sk.id == 'meteor':                           # its shadow first, then it falls in at a slant
        from . import anim as AN
        game.fx('meteor', x=tx, y=ty, col=sk.color)
        late = AN.METEOR_SHADOW + AN.METEOR_FALL
    else:
        late = _fly(game, sk, game.path_to(t), (p.x, p.y), ranged)
    for k in range(sk.hits if ranged else 1):       # Quick Shot: a second arrow after the first
        if k and t in game.map.mons:
            _fly(game, sk, game.path_to(t), (p.x, p.y), ranged)
        if _hit(game, t, sk, r, ranged):
            break
    if not ranged and not sk.splash:
        _burst(game, sk, tx, ty, 0, late)
    if sk.splash:
        cells = []
        for rr in range(1, sk.splash + 1):
            cells += ring_cells(tx, ty, rr)
        if sk.id == 'meteor':                       # the crater, and brown dust that hangs a little longer
            game.fx('burst', x=tx, y=ty, r=sk.splash, col=sk.color, delay=late, dust=True)
        else:
            _burst(game, sk, tx, ty, sk.splash, late)
        lay(game, sk, r, [(tx, ty)] + cells)
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
        _fly(game, sk, game.path_to(o), (p.x, p.y), True)
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
    _fly(game, sk, cells, (p.x, p.y), True)
    for x, y in cells:
        o = m.mon_at(x, y)
        if o and not o.is_npc:
            _hit(game, o, sk, r, True)
    return True


def x_chain(game, sk, r):
    t = _projectile_target(game, sk)
    if not t:
        return False
    from . import spellmap as SM
    hit = set()
    frm = (game.player.x, game.player.y)
    jumps = 1 + sk.jumps + r // 25
    late = 0.0
    while t and jumps > 0:
        jumps -= 1
        game.fx('zap', cells=game.cells_between(frm, (t.x, t.y)), col=sk.color, delay=late)
        late = min(.2, late + .05)                      # it hops from one to the next
        hit.add(t.id)
        frm = (t.x, t.y)
        wet = SM.wet(game, t)
        if wet:
            jumps += 1                                  # water carries it on, and further
        _hit(game, t, sk, r)
        cand = [o for o in game.visible_hostiles() if o.id not in hit and cheb(o.x, o.y, *frm) <= (6 if wet else 4)]
        t = min(cand, key=lambda o: cheb(o.x, o.y, *frm)) if cand else None
    return True


def x_storm(game, sk, r):
    p = game.player
    t = [o for o in game.visible_hostiles() if cheb(o.x, o.y, p.x, p.y) <= sk.radius]
    if not t:
        game.msg('No targets in sight.')
        return False
    random.shuffle(t)
    from . import anim as AN
    game.fx('sky')                                      # one white frame of the sky, then it strikes
    for k, o in enumerate(t[:sk.jumps]):
        game.fx('zap', cells=[(o.x, o.y - 3), (o.x, o.y - 2), (o.x, o.y - 1), (o.x, o.y)], col=sk.color,
                delay=AN.SKY_TIME + min(.12, k * .04))  # struck from above
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
    _burst(game, sk, tx, ty, sk.radius)
    for o in [o for o in game.visible_hostiles() if cheb(o.x, o.y, tx, ty) <= sk.radius]:
        _hit(game, o, sk, r)
    lay(game, sk, r, cells)
    return True


def x_curse(game, sk, r):
    t = game.nearest_target(sk.range, False)
    if not t:
        game.miss_target('No target in sight.')
        return False
    game.fx('burst', x=t.x, y=t.y, r=0, col=sk.color, signs='*∙')
    apply_fx(game, t, sk, r)
    game.player.last_target = t.id
    game.msg(f'{sk.name} takes hold of {t.the()}.', 'info')
    return True


_DUST = (176, 156, 120)


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
        game.fx('trail', cells=[(p.x, p.y)] + game.cells_between((p.x, p.y), dst)[:-1], col=_DUST, ch='·')
        p.x, p.y = dst
        game.compute_fov()
    p.last_target = t.id
    _hit(game, t, sk, r)
    return True


def x_self(game, sk, r):
    p = game.player
    did = False
    if sk.heal:
        amt = round((sk.heal[0] + sk.heal[1] * r) * (_nat(game) if sk.line == 'nature' else 1))
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
        from . import weaponskills as WS
        t = WS.buff_turns(game, sk, t)               # a shield lengthens what guards you
        p.buffs = [x for x in p.buffs if x[0] != k] + [[k, v, t, sk.name]]
        if sk.buff2:
            k2, b2, br2, t2 = sk.buff2
            p.buffs = [x for x in p.buffs if x[0] != k2] + [[k2, round(b2 + br2 * r), t2, sk.name]]
        did = True
    if sk.heal:
        game.fx('rise', x=p.x, y=p.y, col=sk.color)
    else:
        _burst(game, sk, p.x, p.y, 1, hollow=True)          # a ward closing round you
    game.msg(f'You use {sk.name}.', 'good')
    return did or sk.cure


def _fly(game, sk, cells, src, ranged=False):
    """A bolt or an arrow flying along cells; returns how long it takes, so the impact can wait for it."""
    from . import anim as AN
    if not cells:
        return 0.0
    game.fx('bolt', cells=cells, src=src, col=sk.color, ch='-' if ranged else sk.glyph)
    return AN.bolt_time(len(cells))


def _burst(game, sk, x, y, r, delay=0.0, hollow=False, gather=True):
    game.fx('burst', x=x, y=y, r=r, col=sk.color, delay=delay, hollow=hollow, gather=gather and r >= 2 and not hollow)


# the schools' own hands for what spreads out from you: a ring of ice, a wave of !, a howl bending round as ( )
WAVES = {'nova': '*', 'flame_ring': '^', 'inferno': '^', 'turn_undead': 'o', 'dawnbreak': 'o', 'hallowed_ground': 'o',
         'dread': '∙', 'withering': '∙', 'soul_harvest': '*', 'feral_howl': 'sound', 'alpha_roar': 'sound',
         'warcry': '!', 'thunderclap': '!', 'wrath_of_oak': '♣', 'entangle': '"'}
BARGAIN_RED = (210, 40, 50)


def _ring(game, sk, x, y, r):
    """What opens out round you: the school's wave where it has one, else a burst closing round you."""
    from . import anim as AN
    if sk.id == 'morraks_bargain':                  # your own life goes out first, red; then all in sight falls in
        game.fx('wave', x=x, y=y, r=r, col=BARGAIN_RED, sign='•', dur=.14)
        game.fx('wave', x=x, y=y, r=r, col=(170, 90, 220), sign='*', delay=.12)
    elif sk.id in WAVES:
        game.fx('wave', x=x, y=y, r=r, col=sk.color, sign=WAVES[sk.id])
    else:
        _burst(game, sk, x, y, r, hollow=True)


def _rise_dead(game, cells, ch, col, delay=0.0):
    """Corpses that grey and get up, one a moment after the other."""
    for k, (x, y) in enumerate(cells):
        game.fx('raise', x=x, y=y, ch=ch, col=col, from_col=(180, 60, 50), delay=delay + min(.1, k * .03))


def ring_cells(x, y, r):
    return [(x + dx, y + dy) for dy in range(-r, r + 1) for dx in range(-r, r + 1) if max(abs(dx), abs(dy)) == r]


def x_summon(game, sk, r):
    from . import mercs as MC
    p, m = game.player, game.map
    k, n, t = sk.summon
    if k not in _D.MONSTERS:
        k = 'wolf'
    if sk.corpses:                                   # the dead get up where they lie
        from . import spellmap as SM
        cs = [c for c in SM.corpses(game) if not game.occupied(m, c[1], c[2])]
        if len(cs) < sk.corpses:
            game.msg(f'{sk.name} needs a corpse near you.', 'bad')
            return False
        for c in cs[:n]:
            m.slain.remove(c)
        spots = [(c[1], c[2]) for c in cs[:n]]
    else:
        spots = [c for c in free_around(game, m, p.x, p.y, 2) if c != (p.x, p.y)]
        random.shuffle(spots)
    if not spots:
        game.msg('There is no room.')
        return False
    name = {'skeleton': 'Risen Skeleton', 'wolf': 'Wolf of the Pack', 'war_dog': 'War Dog'}.get(sk.summon[0])
    for x, y in spots[:n]:
        o = MC.thrall(game, k, x, y, t + r // 2, name)
        if sk.summon[0] == 'war_dog':
            o.hp = o.maxhp = round(o.maxhp * 1.4)
            o.fg = (200, 170, 120)
    if sk.corpses:
        _rise_dead(game, spots[:n], o.ch, o.fg)
    else:
        game.flash(spots[:n], sk.color, sk.glyph, .25)
    game.msg({'skeleton': 'Bones knit together out of the ground and stand up for you.',
              'wolf': 'A howl answers from the dark, and wolves come loping to your side.' if n > 1 else
                      'A wolf answers your call and falls in at your side.',
              'war_dog': 'You whistle, and war dogs in spiked collars come running.'}.get(sk.summon[0], 'Help comes.'), 'good')
    return True


def x_raise(game, sk, r):
    from . import mercs as MC
    from . import spellmap as SM
    p, m = game.player, game.map
    slain = [c for c in SM.corpses(game)[::-1] if not _D.MONSTERS[c[0]].get('chief') and not _D.MONSTERS[c[0]].get('boss')]
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
    _rise_dead(game, [(x, y)], o.ch, o.fg)
    game.msg(f'You speak the word, and the {_D.MONSTERS[k]["name"].lower()} gets up again. It is yours, for a while.', 'good')
    return True


def x_burst(game, sk, r):
    from . import spellmap as SM
    m = game.map
    slain = SM.corpses(game)
    if not slain:
        game.msg('There is no corpse near you.')
        return False
    c = slain[0]
    m.slain.remove(c)
    tx, ty = c[1], c[2]
    cells = [(tx, ty)]
    for rr in range(1, sk.radius + 1):
        cells += ring_cells(tx, ty, rr)
    _burst(game, sk, tx, ty, sk.radius)
    game.msg('The corpse swells, and bursts.', 'good')
    for o in [o for o in game.visible_hostiles() if cheb(o.x, o.y, tx, ty) <= sk.radius]:
        _hit(game, o, sk, r)
    return True


def x_tame(game, sk, r):
    from . import mercs as MC
    p = game.player
    if not MC.beast_room(game):
        names = ' and '.join(b.name for b in MC.beasts(game))
        game.msg(f'You already have {names}. ' + ('Two beasts are all even a Packmaster can keep.' if 'packmaster' in p.known
                                                   else 'One beast at a time.'))
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


# ------------------------------------------------------------------ the schools' own ways
def _dir(a, b):
    return (b[0] > a[0]) - (b[0] < a[0]), (b[1] > a[1]) - (b[1] < a[1])


def x_wall(game, sk, r):
    """Ice Wall: three to five cells of ice across the way between you and the nearest enemy."""
    from . import spellmap as SM
    p, m = game.player, game.map
    t = game.nearest_target(sk.range, False)
    if not t:
        game.miss_target('No enemy to wall off.')
        return False
    sx, sy = _dir((p.x, p.y), (t.x, t.y))
    d = cheb(p.x, p.y, t.x, t.y)
    cx, cy = (p.x + sx * 2, p.y + sy * 2) if d > 2 else (p.x + sx, p.y + sy)
    px_, py_ = -sy, sx                                 # across the way
    n = 3 + (1 if r >= 30 else 0) + (1 if r >= 60 else 0)
    cells = [(cx + px_ * k, cy + py_ * k) for k in range(-(n // 2), n - n // 2)]
    placed = [c for c in cells if SM.place(game, m, c[0], c[1], _D.ICEWALL, 14 + r // 5)]
    if not placed:
        game.msg('There is no room for a wall there.')
        return False
    game.fx('trail', cells=placed, col=sk.color, ch='█', build=True)
    game.msg('Ice cracks up out of the ground and stands, a wall.', 'good')
    return True


def x_gust(game, sk, r):
    """Gust: every enemy within reach is thrown back a few tiles."""
    p, m = game.player, game.map
    t = sorted([o for o in game.visible_hostiles() if cheb(o.x, o.y, p.x, p.y) <= sk.radius],
               key=lambda o: -cheb(o.x, o.y, p.x, p.y))
    cells = []
    for rr in range(1, sk.radius + 1):
        cells += ring_cells(p.x, p.y, rr)
    game.fx('wave', x=p.x, y=p.y, r=sk.radius, col=sk.color, sign='~')
    if not t:
        game.msg('No enemies in range.')
        return True
    push = 2 + (1 if r >= 40 else 0)
    for o in t:
        sx, sy = _dir((p.x, p.y), (o.x, o.y))
        for _ in range(push):
            nx, ny = o.x + sx, o.y + sy
            if not m.inb(nx, ny) or not _D.TILES[m.tile(nx, ny)].walk or game.occupied(m, nx, ny):
                break
            o.x, o.y = nx, ny
        _hit(game, o, sk, r)
    return True


def x_ball(game, sk, r):
    """Ball Lightning: a ball of lightning that rolls on by itself, striking whatever is beside it."""
    from . import spellmap as SM
    p, m = game.player, game.map
    t = game.nearest_target(sk.range, False)
    spots = [c for c in ring_cells(p.x, p.y, 1) if not game.occupied(m, *c)]
    if t:
        spots.sort(key=lambda c: cheb(c[0], c[1], t.x, t.y))
    grow = round(r * sk.r + game.stats()['ene'] / 5)
    for c in spots:
        if SM.place(game, m, c[0], c[1], _D.BALL, 8 + r // 20, (sk.lo + grow, sk.hi + grow)):
            game.flash([c], sk.color, '¤', .25)
            game.msg('A ball of lightning hums into being and starts to roll.', 'good')
            return True
    game.msg('There is no room for it.')
    return False


def x_tempest(game, sk, r):
    p = game.player
    t = 5 + r // 20
    p.buffs = [b for b in p.buffs if b[0] != 'tempest'] + [['tempest', round(sk.hi + r * sk.r), t, sk.name]]
    game.flash(ring_cells(p.x, p.y, 1), sk.color, '~', .25)
    game.msg('The sky darkens over you, and the thunder answers.', 'good')
    return True


def x_tomb(game, sk, r):
    """Ice Tomb: shut in ice for a few turns; nothing touches you, you heal, you do nothing."""
    p = game.player
    t = 4 + r // 30
    p.buffs = [b for b in p.buffs if b[0] != 'tomb'] + [['tomb', 1, t + 1, sk.name]]
    game.flash(ring_cells(p.x, p.y, 1), sk.color, '█', .3)
    game.msg('Ice closes over you. Through it the world is blue and far away.', 'good')
    s = game.stats()
    for _ in range(t - 1):
        game.end_turn(1, True)
        if game.dead:
            return True
        p.life = min(s['max_life'], p.life + max(1, s['max_life'] // 16))
    p.life = min(s['max_life'], p.life + max(1, s['max_life'] // 16))
    return True


def x_pyre(game, sk, r):
    """Pyre: a burning enemy bursts, and its fire leaps to those beside it."""
    p = game.player
    burning = [o for o in game.visible_hostiles() if 'burn' in o.effects and cheb(o.x, o.y, p.x, p.y) <= sk.range]
    if not burning:
        game.msg('No burning enemy in sight.')
        return False
    t = min(burning, key=lambda o: cheb(o.x, o.y, p.x, p.y))
    fire = list(t.effects['burn'])
    tx, ty = t.x, t.y
    cells = [(tx, ty)]
    for rr in range(1, sk.radius + 1):
        cells += ring_cells(tx, ty, rr)
    game.fx('burst', x=tx, y=ty, r=0, col=sk.color)
    _hit(game, t, sk, r)
    for o in [o for o in game.visible_hostiles() if o is not t and cheb(o.x, o.y, tx, ty) <= sk.radius]:
        game.fx('bolt', cells=game.cells_between((tx, ty), (o.x, o.y)), src=(tx, ty), col=sk.color, ch='^', delay=.06)
        o.effects['burn'] = [max(fire[0], 4), fire[1]]
        o.awake = True
        game.num(o.x, o.y, '*', sk.color)
    game.msg('The fire bursts out of it and leaps to its neighbours.', 'good')
    return True


def x_mist(game, sk, r):
    """Grave Mist: the corpses near you breathe out poison on the enemies beside them."""
    from . import spellmap as SM
    cs = SM.corpses(game, 6)
    if not cs:
        game.msg('There is no corpse near you.')
        return False
    cells, hit = [], set()
    for c in cs:
        cells += [(c[1], c[2])] + ring_cells(c[1], c[2], 1)
        for o in game.visible_hostiles():
            if cheb(o.x, o.y, c[1], c[2]) <= 1 and o.id not in hit:
                hit.add(o.id)
                _hit(game, o, sk, r)
    game.flash(cells, sk.color, '░', .26)
    game.msg('A green mist seeps out of the dead.' if hit else 'A green mist seeps out of the dead, and finds nobody.', 'good')
    return True


def x_prison(game, sk, r):
    """Bone Prison: walls of bone close around an enemy."""
    from . import spellmap as SM
    m = game.map
    t = game.nearest_target(sk.range, False)
    if not t:
        game.miss_target('No target in sight.')
        return False
    turns = 5 + r // 15
    placed = [c for c in ring_cells(t.x, t.y, 1) if SM.place(game, m, c[0], c[1], _D.BONEWALL, turns)]
    t.hold = max(t.hold, turns - 1)
    t.awake = True
    game.fx('trail', cells=placed, col=sk.color, ch='#', build=True)
    game.msg(f'Bones burst up out of the ground and lock around {t.the()}.', 'good')
    return True


def x_army(game, sk, r):
    """Army of the Dead: every corpse near you gets up and fights for you a while."""
    from . import mercs as MC
    from . import spellmap as SM
    m = game.map
    k, n, t = sk.summon
    cs = [c for c in SM.corpses(game, sk.radius) if not game.occupied(m, c[1], c[2])][:n + r // 25]
    if not cs:
        game.msg('There is no corpse near you.')
        return False
    for c in cs:
        m.slain.remove(c)
        o = MC.thrall(game, k, c[1], c[2], t + r // 2, 'Risen Skeleton')
        o.fg = (230, 226, 210)
    _rise_dead(game, [(c[1], c[2]) for c in cs], 'z', (230, 226, 210))
    game.msg('You call, and the dead around you answer. They stand up, all of them.', 'good')
    return True


def x_awaken(game, sk, r):
    """Awaken the Wood: a tree beside you pulls its roots out of the ground and fights for you."""
    from . import mercs as MC
    p, m = game.player, game.map
    trees = [c for rr in (1, 2) for c in ring_cells(p.x, p.y, rr) if m.inb(*c) and m.tile(*c) in (_D.TREE, _D.FOREST)]
    if not trees:
        game.msg('No tree stands near you.')
        return False
    x, y = trees[0]
    m.set(x, y, _D.GRASS)
    o = MC.thrall(game, 'troll', x, y, 30 + r // 2, 'Awakened Oak')
    o.ch, o.fg = '♠', (110, 180, 80)
    o.hp = o.maxhp = round(o.maxhp * _nat(game))
    game.flash([(x, y)], sk.color, '♠', .3)
    game.msg('The tree shudders, tears its roots out of the earth and strides to your side.', 'good')
    return True


def x_sic(game, sk, r):
    """Sic 'Em: your beast springs at your target and knocks it down."""
    from . import mercs as MC
    m = game.map
    mc = with_beast(game)
    t = game.nearest_target(sk.range, False)
    if not t:
        game.miss_target('No target in sight.')
        return False
    b = mc.body
    if cheb(b.x, b.y, t.x, t.y) > 1:
        spots = [c for c in free_around(game, m, t.x, t.y, 1) if c != (t.x, t.y)]
        if not spots:
            game.msg(f'{mc.name} cannot get at it.')
            return False
        dst = min(spots, key=lambda c: cheb(c[0], c[1], b.x, b.y))
        game.fx('trail', cells=[(b.x, b.y)] + game.cells_between((b.x, b.y), dst)[:-1], col=_DUST, ch='·')
        b.x, b.y = dst
    MC.strike(game, mc, b, t, MC.stats(game, mc))
    if t in m.mons:
        apply_fx(game, t, sk, r)
    game.msg(f'{mc.name} springs at {t.the()}!', 'good')
    return True


def x_spirit(game, sk, r):
    """Spirit of the Pack: your beasts grow, for a while: more life, more bite."""
    from . import mercs as MC
    t = 15 + r // 5
    for mc in [b for b in (MC.with_you(game, 'beast'), MC.with_you(game, 'beast2')) if b]:
        mc.grown = t
        mc.hp = MC.stats(game, mc)['max_hp']
        MC.refresh_body(game, mc)
        if mc.body is not None:
            game.flash([(mc.body.x, mc.body.y)], sk.color, 'C', .3)
        game.msg(f'{mc.name} swells, bigger than any of its kind, and howls.', 'good')
    return True


def x_totem(game, sk, r):
    """Spirit Totem: a totem in the ground that heals you and your company beside it while it stands."""
    from . import spellmap as SM
    p, m = game.player, game.map
    heal = round((sk.heal[0] + sk.heal[1] * r) * _nat(game))
    for c in ring_cells(p.x, p.y, 1) + ring_cells(p.x, p.y, 2):
        if SM.place(game, m, c[0], c[1], _D.SPIRITTOTEM, 20, heal):
            game.flash([c], sk.color, '¶', .3)
            game.msg('You drive the totem into the ground. The spirits gather round it.', 'good')
            return True
    game.msg('There is no room for a totem here.')
    return False


def x_golem(game, sk, r):
    """Bone Golem: three corpses become one, and it stays with you until it falls."""
    from . import mercs as MC
    from . import spellmap as SM
    m = game.map
    cs = [c for c in SM.corpses(game) if not game.occupied(m, c[1], c[2])]
    if len(cs) < sk.corpses:
        game.msg(f'{sk.name} needs {sk.corpses} corpses near you.', 'bad')
        return False
    for c in cs[:sk.corpses]:
        m.slain.remove(c)
    x, y = cs[0][1], cs[0][2]
    o = MC.thrall(game, 'skeleton', x, y, 100000, 'Bone Golem')
    o.ch, o.fg = 'Z', (230, 226, 200)
    o.hp = o.maxhp = round(o.maxhp * (3 + r / 40))
    o.dmg = (round(o.dmg[0] * 1.5), round(o.dmg[1] * 1.5))
    from . import anim as AN                        # the other bones crawl to the first, and it stands up
    late = 0.0
    for c in cs[1:sk.corpses]:
        path = game.cells_between((c[1], c[2]), (x, y))[:-1]
        if path:
            game.fx('bolt', cells=[(c[1], c[2])] + path, src=(c[1], c[2]), col=(180, 170, 150), ch='%')
            late = max(late, AN.bolt_time(len(path) + 1))
    _rise_dead(game, [(x, y)], 'Z', o.fg, late)
    game.msg('The bones of the dead crawl together and stand up as one great shape.', 'good')
    return True


def x_passive(game, sk, r):
    return False


EXEC = {'summon': x_summon, 'raise': x_raise, 'burst': x_burst, 'tame': x_tame, 'rite': x_rite, 'shape': x_shape,
        'melee': x_melee, 'adjacent': x_adjacent, 'around': x_around, 'bolt': x_bolt, 'shot': x_shot, 'volley': x_volley,
        'pierce': x_pierce, 'chain': x_chain, 'storm': x_storm, 'target_area': x_target_area, 'curse': x_curse,
        'leap': x_leap, 'self': x_self, 'wall': x_wall, 'gust': x_gust, 'ball': x_ball, 'tempest': x_tempest,
        'tomb': x_tomb, 'pyre': x_pyre, 'mist': x_mist, 'prison': x_prison, 'army': x_army, 'awaken': x_awaken, 'sic': x_sic,
        'spirit': x_spirit, 'totem': x_totem, 'golem': x_golem, 'passive': x_passive, 'bash': x_bash}


from . import weaponskills as _WS  # noqa: E402  (the weapon skills, keys 1-2)
SKILLS.update(_WS.WSKILLS)
