"""Items, monsters, the player and maps."""
import random

from . import data as D


# kinds kept by their own module: display(game, it), lines(game, it), value(game, it), glyph(it), color(it)
CRAFT = {'dish': 'cooking', 'cookbook': 'cooking', 'hide': 'hunting', 'part': 'hunting', 'carcass': 'hunting',
         'leather': 'hunting'}


def _craft(it):
    import importlib
    from . import foraging as FG
    return importlib.import_module('avarenthia.' + CRAFT[it.k]), getattr(FG, 'GAME', None)


class Item:
    def __init__(self, uid, k, t, n=1):
        self.id = uid
        self.k = k          # 'gear' | 'potion' | 'scroll' | 'gold' | 'orb'
        self.t = t          # base key, potion type, 'tp', ...
        self.n = n
        self.x = self.y = 0
        self.dropped = False
        # gear only
        self.base = None
        self.slot = None
        self.rar = 'normal'
        self.ilvl = 1
        self.aff = []       # list of [stat, value]
        self.req = 1
        self.dmg = None
        self.arm = None
        self.name = ''
        self.mission = None
        self.payload = None
        self.ided = True         # unidentified magic items hide their properties
        self.curse = []          # hidden negative properties: list of [stat, value]
        self.curse_known = False
        self.rstr = self.rdex = 0    # Strength and Dexterity needed
        self.set_key = None
        self.perfect = False
        self.dur = self.mdur = 0     # durability: wears down with use, 0 is broken (jewellery never wears)

    @property
    def cursed(self):
        return bool(getattr(self, 'curse', None))

    @property
    def identified(self):
        return getattr(self, 'ided', True)

    # ---------------------------------------------------------- presentation
    def display_name(self):
        if self.k in CRAFT:
            mod, g = _craft(self)
            return mod.display(g, self)
        if self.k == 'gold':
            from .money import fmt
            return fmt(self.n) + ' in coins'
        if self.k == 'potion':
            return (f'{self.n}x ' if self.n > 1 else '') + D.POTIONS[self.t]['name']
        if self.k == 'scroll':
            return (f'{self.n}x ' if self.n > 1 else '') + 'Scroll of Town Portal'
        if self.k == 'orb':
            return 'health orb'
        if self.k == 'tome':
            from .skills import SKILLS
            return f'Tome of {SKILLS[self.t].name}'
        if self.k == 'tool':
            if self.t == 'tent':
                return 'Tent and Bedroll'
            if self.t == 'pick':
                return 'Miner\'s Pick'
            if self.t in ('knife', 'frame', 'waterskin'):
                return {'knife': 'Skinning Knife', 'frame': 'Stretching Frame', 'waterskin': 'Waterskin'}[self.t]
            return (f'{self.n}x ' if self.n > 1 else '') + 'Repair Kit' if self.t == 'kit' else 'Fishing Pole'
        if self.k == 'food':
            from .hunger import FOODS
            return (f'{self.n}x ' if self.n > 1 else '') + FOODS[self.t][0]
        if self.k == 'plant':
            from . import foraging as FG
            return (f'{self.n}x ' if self.n > 1 else '') + FG.plant_name(FG.GAME, self.t)
        if self.k == 'fish':
            from .lifeskills import FISH
            return (f'{self.n}x ' if self.n > 1 else '') + FISH[self.t][0]
        if self.k in ('oldmap', 'vkey', 'trophy', 'star', 'oldbook', 'curio'):
            return self.name
        if self.k == 'gear' and not self.identified:
            return f"{D.BASES[self.base]['name']} (unidentified)"
        if self.k == 'gear' and self.cursed and self.curse_known:
            return self.name + ' (cursed)'
        if self.k == 'gear' and getattr(self, 'mdur', 0) and self.dur <= 0:
            return self.name + ' (broken)'
        if self.k == 'gear' and getattr(self, 'perfect', False):
            return self.name + ' (perfect)'
        return self.name

    def color(self):
        if self.k in CRAFT:
            return _craft(self)[0].color(self)
        if self.k == 'gear':
            return D.RARITY_COLOR[self.rar]
        if self.k == 'potion':
            return D.POTIONS[self.t]['col']
        if self.k == 'gold':
            return (242, 196, 67)
        if self.k == 'orb':
            return (255, 74, 74)
        if self.k == 'quest':
            return (255, 214, 92)
        if self.k == 'corpse':
            return (240, 240, 240)
        if self.k == 'tome':
            from .skills import SKILLS, DISC_COLOR
            return DISC_COLOR[SKILLS[self.t].line]
        if self.k == 'tool':
            return (190, 150, 100)
        if self.k == 'food':
            from .hunger import FOODS
            return FOODS[self.t][3]
        if self.k == 'plant':
            return (140, 200, 110)
        if self.k == 'fish':
            return (255, 214, 92) if self.t == 'golden' else (150, 200, 220)
        if self.k in ('oldmap', 'vkey'):
            return (200, 210, 170)
        if self.k == 'trophy':
            return (226, 190, 130)
        if self.k == 'star':
            return (196, 214, 255)
        if self.k == 'oldbook':
            return (176, 132, 88)
        if self.k == 'curio':
            from .nature import CURIO
            return CURIO[self.t][2]
        return (238, 228, 194)

    def glyph(self):
        if self.k in CRAFT:
            return _craft(self)[0].glyph(self)
        if self.k == 'gold':
            return '$'
        if self.k == 'orb':
            return '*'
        if self.k == 'potion':
            return '!'
        if self.k == 'scroll':
            return '?'
        if self.k == 'quest':
            return '§'
        if self.k == 'corpse':
            return '%'
        if self.k in ('tome', 'oldbook'):
            return '≡'
        if self.k == 'curio':
            return '*'
        if self.k == 'tool':
            return '/'
        if self.k == 'food':
            return '¡' if self.t in ('ale', 'wine', 'mead') else '%'
        if self.k == 'plant':
            return '"'
        if self.k == 'fish':
            return '~'
        if self.k == 'oldmap':
            return '?'
        if self.k == 'vkey':
            return '-'
        if self.k == 'trophy':
            return '%'
        if self.k == 'star':
            return '☼'
        return D.SLOTGLYPH[self.slot]

    def aff_sum(self, stat):
        return sum(v for s, v in self.aff if s == stat)

    def armor_value(self):
        return round(self.arm * (1 + self.aff_sum('edef') / 100)) if self.arm else 0

    def lines(self):
        out = []
        if self.k in CRAFT:
            mod, g = _craft(self)
            return mod.lines(g, self)
        if self.k != 'gear':
            if self.k == 'potion':
                out.append({'hp': 'Restores 45% of your life.', 'mp': 'Restores 50% of your mana.',
                            'rejuv': 'Restores 40% of life and mana.'}[self.t])
            elif self.k == 'scroll':
                out.append('Opens a portal to the last town you visited, and back.')
            elif self.k == 'quest':
                out.append('A relic someone is waiting for. Bring it back to claim your reward.')
            elif self.k == 'oldmap':
                out.append('A map of the Varnish Empire, the ink nearly gone. Read it to find one of the old ways.')
            elif self.k == 'vkey':
                out.append('A key of black Varnish iron. It opens a sealed vault.')
            elif self.k == 'curio':
                from .nature import CURIO
                out.append(CURIO[self.t][3])
            elif self.k == 'oldbook':
                out.append('An old book, its pages brown and brittle. Read it for your chronicle; a library pays '
                           'something for it.')
            elif self.k == 'star':
                out.append('Iron that fell from the sky, still faintly warm, shot through with silver. The Circle of Magi '
                           'pays for it, and smiths dream of it.')
            elif self.k == 'trophy':
                out.append('Proof of a kill. Bring it to a town that has a bounty on its owner: wherever the job came from, '
                           'or anywhere near where it lived.')
            elif self.k == 'plant':
                from . import foraging as FG
                if FG.known(FG.GAME, self.t):
                    name, grp, food, eff, _w = FG.PLANTS[self.t]
                    out.append({'deadly': 'Deadly poison. Do not eat.', 'poison': 'Poisonous.', 'sick': 'Makes you sick.',
                                'sleep': 'Puts you to sleep.', 'heal': 'A healing herb.', 'heal2': 'A strong healing herb.',
                                'mana': 'Restores a little mana.', 'cure': 'Settles the stomach and cures poison.'}.get(eff, 'Edible.'))
                    if self.t in FG.ALCHEMY:
                        out.append('Used in alchemy (P to brew potions).')
                    if self.t == 'oak_bark':
                        out.append('Tanners use it: rub it into a salted hide and the hide tans in your pack.')
                    if self.t == 'blackberry':
                        out.append('Brewers make berry wine from these.')
                else:
                    out.append('You do not know what this is. Eat it to find out, or show it to a herbalist.')
            elif self.k == 'food':
                from .hunger import FOODS
                out.append(f'Food. Eat it to still your hunger (+{FOODS[self.t][1]}).' if self.t not in ('ale', 'wine', 'mead')
                           else 'A drink. Cheers you up and heals a little; sells well.')
                if self.t in ('barley', 'honey'):
                    out.append('Brewers use it (P, at an inn or a monastery cellar).')
            elif self.k == 'tool' and self.t == 'tent':
                out.append('Sleep dry in the wild, and a little safer: rest (R) out in the open to make camp.')
            elif self.k == 'tool' and self.t == 'kit':
                out.append('Needle, thread, rivets and oil. Use it to mend all your gear a little, anywhere.')
            elif self.k == 'tool' and self.t == 'knife':
                out.append('A short, curved blade. Stand on a carcass and press Enter to skin it.')
            elif self.k == 'tool' and self.t == 'frame':
                out.append('Use it out in the land to set it up; walk into it with salt in your pack to salt your hides.')
            elif self.k == 'tool' and self.t == 'waterskin':
                out.append('Water at hand: heat wears on you less.')
            elif self.k == 'tool' and self.t == 'pick':
                out.append('Walk into an ore or gem vein to dig it out. What you dig goes on your cart, to sell.')
            elif self.k == 'tool':
                out.append('Stand next to water and press A to fish. Fishing grows the more you do it.')
            elif self.k == 'fish':
                from .lifeskills import FISH
                out.append(f'Eat it to heal {FISH[self.t][5]} life, or sell it.')
            elif self.k == 'tome':
                from .skills import SKILLS, DISCIPLINES, describe
                sk = SKILLS[self.t]
                out.append(f"A {DISCIPLINES[sk.line]['name']} skill. {sk.cost} mana, recharge {sk.cd} turns.")
                out.append(describe(sk, 0))
                out.append(f"Needs {DISCIPLINES[sk.line]['name']} {sk.unlock} to learn." if sk.unlock else 'Anyone can learn it.')
                out.append('Read it from your inventory to learn the skill.')
            return out
        b = D.BASES[self.base]
        if b.get('grade', 'normal') != 'normal':
            out.append(f"{b['grade'].capitalize()} {b['name'].lower()}")
        if self.dmg:
            out.append(f'Damage {self.dmg[0]}-{self.dmg[1]}' + (' · two hands' if b.get('two') else ''))
        if self.arm:
            out.append(f'Armor {self.armor_value()}')
        if b.get('hit'):
            out.append(f"+{b['hit']} to accuracy")
        if b.get('mana'):
            out.append(f"+{b['mana']} to mana")
        if getattr(self, 'mdur', 0):
            out.append(f'Durability {self.dur}/{self.mdur}' + (' (broken: it does nothing until repaired)' if self.dur <= 0 else
                                                                ' (badly worn)' if self.dur < self.mdur // 4 else ''))
        if not self.identified:
            out.append('Unidentified. Its powers are hidden until a sage, outfitter or priest in a town identifies it.')
            if self.cursed and self.curse_known:
                out.append('It is cursed!')
            return out
        u = unique_named(self.name) if self.rar in ('unique', 'rare', 'magic') else None
        for s, v in self.aff:
            line = D.AFFTXT[s].format(v)
            rng = u and u['aff'].get(s)
            if isinstance(rng, tuple) and rng[0] != rng[1]:
                line += f' [{rng[0]}-{rng[1]}]'
            out.append(line)
        if getattr(self, 'perfect', False):
            out.append('A perfect one: every power at the top of its range.')
        sk = getattr(self, 'set_key', None)
        if sk:
            st = D.SETS[sk]
            out.append(f"Part of {st['name']} ({len(st['pieces'])} pieces). {st['lore']}")
            out.append('2 pieces: ' + ', '.join(D.AFFTXT[k].format(v) for k, v in st['partial'].items()))
            out.append('Full set: ' + ', '.join(D.AFFTXT[k].format(v) for k, v in st['full'].items()))
        if self.cursed:
            out.append('CURSED: ' + ', '.join(D.CURSETXT[s].format(v) for s, v in self.curse) +
                       '. Once worn it cannot be removed until a priest lifts the curse.')
        return out

    def value(self):
        """Price in copper."""
        return round(self._value_silver() * 100)

    def _value_silver(self):
        if self.k in CRAFT:
            mod, g = _craft(self)
            return mod.value(g, self)
        if self.k == 'potion':
            return D.POTIONS[self.t]['val']
        if self.k == 'scroll':
            return 20
        if self.k == 'tome':
            from .skills import SKILLS, UNLOCKS
            return 90 + UNLOCKS.index(SKILLS[self.t].unlock) * 110
        if self.k == 'tool':
            return {'kit': 25, 'tent': 60, 'pick': 15, 'knife': 3, 'frame': 6, 'waterskin': 4}.get(self.t, 8)
        if self.k == 'food':
            from .hunger import FOODS
            return FOODS[self.t][2] / 100
        if self.k == 'plant':
            from .foraging import PLANTS
            return .5 if PLANTS[self.t][1] == 'herb' else .2
        if self.k == 'fish':
            from .lifeskills import FISH
            return FISH[self.t][4] * .5
        if self.k == 'oldmap':
            return 15
        if self.k == 'oldbook':
            return 12
        if self.k == 'curio':
            from .nature import CURIO
            return CURIO[self.t][1]
        if self.k == 'trophy':
            return 4
        if self.k == 'star':
            return 60
        if self.k != 'gear':
            return 0
        v = round(D.BASES[self.base]['val'] * D.RARITY_MULT[self.rar] + len(self.aff) * 10)
        if not self.identified:
            v = round(D.BASES[self.base]['val'] * (1 + (D.RARITY_MULT[self.rar] - 1) * .4))
        elif self.cursed:
            v //= 3
        return v

    def id_cost(self):
        return round((8 + self.ilvl * 2) * {'magic': 1, 'rare': 2, 'unique': 3}.get(self.rar, 1)) * 100

    def uncurse_cost(self):
        return (30 + self.ilvl * 5) * 100

    @property
    def stackable(self):
        return self.k in ('potion', 'scroll', 'fish', 'food', 'plant', 'dish', 'part', 'leather') or \
            (self.k == 'tool' and self.t == 'kit')


class Monster:
    def __init__(self, uid, k, x, y):
        self.id = uid
        self.k = k
        self.x, self.y = x, y
        self.lvl = 1
        self.awake = False
        self.elite = 0          # 0 normal, 1 champion, 2 unique
        self.mods = []
        self.name = ''
        self.ch = '?'
        self.fg = (255, 255, 255)
        self.hold = 0           # stunned / frozen turns
        self.hp = self.maxhp = 1
        self.dmg = (1, 2)
        self.df = 1
        self.hit_r = 10
        self.xp = 1
        self.pack = None
        self.summons = 0
        self.hit_flash = 0
        self.effects = {}       # burn / bleed / poison / weaken / vuln -> [turns, value]
        self.frozen = False
        self.faction = None
        # npc fields
        self.role = None
        self.stay = False

    @property
    def is_npc(self):
        return self.k == 'npc'

    @property
    def tpl(self):
        return D.MONSTERS[self.k]

    @property
    def is_boss(self):
        return not self.is_npc and self.tpl['boss']

    def the(self):
        if self.is_npc or self.elite == 2 or self.is_boss:
            return self.name
        if self.name.startswith('The '):                 # The Staring Dark, The Deep Mother
            return 'the ' + self.name[4:]
        return 'the ' + self.name


class Player:
    def __init__(self, name, hardcore=True):
        from .skills import DISC_ORDER, STARTING_BAR, BAR_SIZE, UNLOCKS, SKILL_LIST
        st = D.START_STATS
        self.name = name
        self.hardcore = hardcore
        self.x = self.y = 0
        self.lvl = 1
        self.xp = 0
        self.str, self.dex, self.vit, self.ene = st['str'], st['dex'], st['vit'], st['ene']
        self.stat_pts = 0
        self.disc = {k: [0, 0] for k in DISC_ORDER}      # rank, progress
        self.known = []                  # skills are learned from tomes found in the world
        self.bar = [None] * BAR_SIZE
        self.cooldowns = {}
        self.buffs = []          # [key, value, turns, source]
        self.inv = []
        self.eq = {}
        self.gold = 120            # money, in copper (see money.py)
        self.poison = None      # [turns, damage]
        self.burn = None
        self.cargo = {}         # trade good -> quantity
        self.cost_basis = {}    # trade good -> average purchase price
        self.parcels = []       # job cargo: dict(mid, name, w)
        self.mounts = []        # 'mule', 'cart'
        self.rep = {k: v['start'] for k, v in D.FACTIONS.items()}
        self.deaths = 0
        self.life_sk = {'fishing': [0, 0]}     # life skills: rank, progress
        self.food = 800                        # hunger: 0 starving .. 1000 full (lasts about a week)
        self.known_plants = set()              # plants you can recognise
        self.recipes = set()                   # alchemy recipes you know
        self.god, self.favor = None, 0         # the god you serve, and how fond of you they are
        self.race, self.gender = 'human', 'other'
        self.life = 1
        self.mana = 1
        self.last_target = None
        self.target = None          # the enemy picked with Tab


class GameMap:
    def __init__(self, key, kind, name, w, h, fill):
        self.key, self.kind, self.name, self.w, self.h = key, kind, name, w, h
        self.t = [fill] * (w * h)
        self.seen = bytearray(w * h)
        self.mons = []
        self.items = []
        self.radius = 7
        self.level = 1
        self.did = None
        self.depth = 0
        self.wall_fg = None
        self.entry = None
        self.portal_pos = None

    def __getstate__(self):
        st = self.__dict__.copy()
        st.pop('_look', None)          # drawing cache, rebuilt on demand
        st.pop('_look_t', None)
        st.pop('_light', None)
        st.pop('_light_dom', None)
        st.pop('_light_dyn', None)
        for k in ('_flow', '_cold', '_passes', '_bonfires', '_sl', '_sl_key'):
            st.pop(k, None)
        return st

    def inb(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h

    def tile(self, x, y):
        return self.t[y * self.w + x]

    def set(self, x, y, v):
        self.t[y * self.w + x] = v

    def mon_at(self, x, y):
        for m in self.mons:
            if m.x == x and m.y == y:
                return m
        return None


# ------------------------------------------------------------------ item creation
def _skill_line(it):
    """Which discipline a '+ to skill' affix raises on this item."""
    from .skills import WEAPON_LINE
    if it.slot == 'weapon':
        if D.BASES[it.base].get('mana'):          # staves raise magic
            return random.choice(['fire', 'frost', 'storm', 'shadow', 'restoration'])
        return WEAPON_LINE.get(D.FAMILY_OF.get(it.base, it.base)) or 'warcraft'
    if it.slot == 'shield' and not it.arm:
        return random.choice(['fire', 'frost', 'storm', 'shadow', 'restoration'])
    if it.slot == 'gloves':
        return random.choice(['swords', 'axes', 'daggers', 'archery', 'unarmed'])
    return random.choice(list(D.SKILL_PREFIX))


def roll_affix(it, pre, exclude):
    def fits(a):
        return it.slot in a['slots'] and a['stat'] not in exclude and a['tiers'][0][0] <= it.ilvl
    c = [a for a in D.AFFIXES if a['pre'] == pre and fits(a)]
    if not c:
        c = [a for a in D.AFFIXES if fits(a)]
    if not c:
        return None
    a = random.choice(c)
    ts = [t for t in a['tiers'] if t[0] <= it.ilvl]
    # the best tier the item level allows, now and then one lower
    t = ts[max(0, len(ts) - 1 - (1 if random.random() < .35 else 0) - (1 if random.random() < .12 else 0))]
    stat, name = a['stat'], t[1]
    if stat == 'skill':
        line = _skill_line(it)
        stat, name = 'skill_' + line, D.SKILL_PREFIX[line]
    return [stat, random.randint(t[2], t[3])], name, a['pre']


def base_for(family, ilvl, top=True):
    """The grade of a family that fits this item level: the best one it reaches, sometimes one lower."""
    ks = [k for k in D.grades(family) if D.BASES[k]['lvl'] <= ilvl + 1] or D.grades(family)[:1]
    if not top and len(ks) > 1 and random.random() < .4:
        return ks[-2]
    return ks[-1]


DURABILITY = {'weapon': 60, 'armor': 70, 'shield': 60, 'helm': 50, 'gloves': 40, 'boots': 45, 'belt': 40}


def _fill_base(it, bk):
    b = D.BASES[bk]
    it.base, it.slot, it.req = bk, b['slot'], b['lvl']
    md = DURABILITY.get(b['slot'], 0)
    md = round(md * {'normal': 1, 'exceptional': 1.25, 'elite': 1.5}.get(b.get('grade', 'normal'), 1))
    it.dur = it.mdur = md
    it.rstr, it.rdex = b.get('rstr', 0), b.get('rdex', 0)
    if 'dmg' in b:
        it.dmg = tuple(b['dmg'])
    if 'arm' in b:
        it.arm = random.randint(*b['arm'])


def make_gear(game, bk, rar, ilvl):
    if bk not in D.BASES:
        bk = base_for(bk, ilvl)
    b = D.BASES[bk]
    if b.get('magic_only') and rar == 'normal':
        rar = 'magic'
    it = Item(game.new_id(), 'gear', bk)
    it.rar, it.ilvl = rar, ilvl
    _fill_base(it, bk)
    if rar == 'magic':
        pn = sn = ''
        want_pre = random.random() < .65
        want_suf = (not want_pre) or random.random() < .6
        if want_pre:
            r = roll_affix(it, True, [])
            if r:
                it.aff.append(r[0])
                if r[2]:
                    pn = r[1] + ' '
                else:
                    sn = ' ' + r[1]
        if want_suf:
            r = roll_affix(it, False, [a[0] for a in it.aff])
            if r:
                it.aff.append(r[0])
                if r[2] and not pn:
                    pn = r[1] + ' '
                elif not r[2] and not sn:
                    sn = ' ' + r[1]
        it.name = pn + b['name'] + sn
    elif rar == 'rare':
        n = random.randint(3, 4 if ilvl < 10 else 5 if ilvl < 20 else 6)
        for _ in range(n):
            r = roll_affix(it, random.random() < .5, [a[0] for a in it.aff])
            if r:
                it.aff.append(r[0])
        it.name = random.choice(D.RARE_A) + ' ' + random.choice(D.RARE_B)
        it.req = max(b['lvl'], ilvl - 2)
    else:
        it.name = b['name']
    return it


def make_unique(game, u):
    """A unique: its powers roll within their ranges. All of them at the top makes a perfect one.
    A named piece can be of a lower grade too (rar='magic'): a small boss's own weapon, known by name."""
    it = make_gear(game, u['base'], 'normal', u['lvl'])
    it.rar = u.get('rar', 'unique')
    it.name = u['name']
    it.aff = []
    top = True
    for s, v in u['aff'].items():
        lo, hi = v if isinstance(v, tuple) else (v, v)
        val = random.randint(lo, hi)
        top = top and val == hi
        it.aff.append([s, val])
    it.perfect = top and any(isinstance(v, tuple) and v[0] != v[1] for v in u['aff'].values())
    it.req = max(u['lvl'], D.BASES[it.base]['lvl'])
    return it


def unique_named(name):
    return next((u for u in D.UNIQUES if u['name'] == name), None)


def make_set_item(game, set_key, piece):
    st = D.SETS[set_key]
    name, family, aff = st['pieces'][piece]
    lvl = max(D.BASES[family]['lvl'], 6)
    it = make_gear(game, family, 'normal', lvl)
    it.rar, it.name = 'set', name
    it.aff = [[k, v] for k, v in aff.items()]
    it.set_key = set_key
    it.req = max(lvl, D.BASES[it.base]['lvl'])
    return it


def add_curse(it):
    for st, lo, hi in random.sample(D.CURSES, random.randint(1, 2)):
        it.curse.append([st, random.randint(lo, hi) + it.ilvl // 3])


def _mf(game):
    try:
        mf = game.stats().get('mf', 0)
    except Exception:
        return 1
    return 1 + (mf * 250 / (mf + 250)) / 100          # diminishing returns, as in the old game


def random_gear(game, ilvl, boost=1, bases=None, src=None):
    """Loot. Magic items are rare, arrive unidentified, and now and then carry a hidden curse.
    bases: the families of items this source could have (what a monster actually uses); src: who drops it
    ('chest' for a chest or a hoard). Uniques and set pieces only come from those who would have them."""
    src = src or ('chest' if bases is None else None)
    boost *= _mf(game)
    r = random.random()
    it = None
    fam_ok = (lambda k: bases is None or D.FAMILY_OF.get(k, k) in bases)
    if r < .004 * boost:
        us = [u for u in D.UNIQUES if not u.get('boss') and src in u.get('src', ()) and u['lvl'] <= ilvl + 2 and fam_ok(u['base'])]
        if us:
            it = make_unique(game, random.choice(us))
    if it is None and random.random() < .005 * boost:
        opts = [(k, i) for k, st in D.SETS.items() if src in st['src'] for i, pc in enumerate(st['pieces'])
                if fam_ok(pc[1]) and D.BASES[pc[1]]['lvl'] <= ilvl + 3]
        if opts:
            it = make_set_item(game, *random.choice(opts))
    if it is None:
        rar = 'rare' if r < .008 * boost else 'magic' if r < .035 * boost else 'normal'     # magic is meant to be special
        pool = bases or [f for f in dict.fromkeys(D.FAMILY_OF.values())]
        fams = [f for f in pool if f in D.FAMILY_OF.values() and D.BASES[D.grades(f)[0]]['lvl'] <= ilvl + 1
                and not (rar == 'normal' and D.BASES[D.grades(f)[0]].get('magic_only'))]
        if not fams:
            fams = sorted((f for f in pool if f in D.FAMILY_OF.values()), key=lambda f: D.BASES[D.grades(f)[0]]['lvl'])[:1] or ['dagger']
            if rar == 'normal' and D.BASES[D.grades(fams[0])[0]].get('magic_only'):
                rar = 'magic'
        it = make_gear(game, base_for(random.choice(fams), ilvl, top=False), rar, ilvl)
    if it.rar != 'normal':
        it.ided = False
        if it.rar in ('magic', 'rare') and random.random() < (.1 if it.rar == 'magic' else .14):
            add_curse(it)
    elif random.random() < .03:
        add_curse(it)
        it.ided = False
    return it


def make_tome(game, lvl, line=None):
    """A skill tome suited to monsters of this level, preferring skills you do not know yet."""
    from .skills import SKILL_LIST, UNLOCKS
    top = min(4, max(0, lvl // 4))
    cands = [s for s in SKILL_LIST if UNLOCKS.index(s.unlock) <= top and (line is None or s.line == line)]
    known = set(game.player.known)
    wts = [(4 if s.id not in known else 1) * (3 if UNLOCKS.index(s.unlock) == 0 else 1) for s in cands]
    sk = random.choices(cands, wts)[0]
    it = Item(game.new_id(), 'tome', sk.id)
    it.name = f'Tome of {sk.name}'
    return it


def make_monster(game, k, x, y, lvl, elite=0):
    d = D.MONSTERS[k]
    if d['boss']:
        lvl = d.get('lvl_fix', lvl)
    hp = round((4 + lvl * 4.5) * d['hp'])
    dmg = [max(1, round((2 + lvl * 1.4) * d['dmg'])), max(2, round((4 + lvl * 2.8) * d['dmg']))]
    df = round((3 + lvl * 3) * d['df'])
    xp = round((5 + lvl * lvl * 1.6) * d['xp'])
    m = Monster(game.new_id(), k, x, y)
    m.lvl, m.elite, m.name, m.ch, m.fg = lvl, elite, d['name'], d['ch'], d['fg']
    if elite == 1:
        hp = round(hp * 2.5)
        dmg = [round(v * 1.25) for v in dmg]
        xp *= 3
        m.name = 'Champion ' + d['name']
        m.fg = D.CHAMPION_FG
    elif elite == 2:
        hp = round(hp * 3.5)
        xp *= 5
        a, b, c = D.UNIQUE_NAME
        m.name = random.choice(a) + random.choice(b) + ' ' + random.choice(c)
        m.fg = D.UNIQUE_FG
        m.mods = random.sample(D.ELITE_MODS, random.randint(1, 2))
        if 'Extra Strong' in m.mods:
            dmg = [round(v * 1.5) for v in dmg]
        if 'Stone Skin' in m.mods:
            df *= 2
            hp = round(hp * 1.3)
    m.hp = m.maxhp = hp
    m.dmg = tuple(dmg)
    m.df = df
    m.hit_r = 5 + lvl * 5
    m.xp = xp
    from .behave import on_spawn
    on_spawn(game, m)
    return m


def make_npc(game, name, role, fg, x, y, stay, ch='☺', race=None, gender=None):
    from .races import who
    m = Monster(game.new_id(), 'npc', x, y)
    if ch in ('@', 'h'):
        ch = '☺'           # everyone who is not out to kill you is a smiley
    m.name, m.role, m.fg, m.stay, m.ch = name, role, D.hexrgb(fg), stay, ch
    g, r = who(name)
    m.gender = gender or g
    m.race = race or r
    return m
