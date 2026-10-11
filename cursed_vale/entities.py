"""Items, monsters, the player and maps."""
import random

from . import data as D


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

    @property
    def cursed(self):
        return bool(getattr(self, 'curse', None))

    @property
    def identified(self):
        return getattr(self, 'ided', True)

    # ---------------------------------------------------------- presentation
    def display_name(self):
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
            return 'Fishing Pole'
        if self.k == 'food':
            from .hunger import FOODS
            return (f'{self.n}x ' if self.n > 1 else '') + FOODS[self.t][0]
        if self.k == 'plant':
            from . import foraging as FG
            return (f'{self.n}x ' if self.n > 1 else '') + FG.plant_name(FG.GAME, self.t)
        if self.k == 'fish':
            from .lifeskills import FISH
            return (f'{self.n}x ' if self.n > 1 else '') + FISH[self.t][0]
        if self.k == 'gear' and not self.identified:
            return f"{D.BASES[self.base]['name']} (unidentified)"
        if self.k == 'gear' and self.cursed and self.curse_known:
            return self.name + ' (cursed)'
        return self.name

    def color(self):
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
        return (238, 228, 194)

    def glyph(self):
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
        if self.k == 'tome':
            return '≡'
        if self.k == 'tool':
            return '/'
        if self.k == 'food':
            return '%'
        if self.k == 'plant':
            return '"'
        if self.k == 'fish':
            return '~'
        return D.SLOTGLYPH[self.slot]

    def aff_sum(self, stat):
        return sum(v for s, v in self.aff if s == stat)

    def armor_value(self):
        return round(self.arm * (1 + self.aff_sum('edef') / 100)) if self.arm else 0

    def lines(self):
        out = []
        if self.k != 'gear':
            if self.k == 'potion':
                out.append({'hp': 'Restores 45% of your life.', 'mp': 'Restores 50% of your mana.',
                            'rejuv': 'Restores 40% of life and mana.'}[self.t])
            elif self.k == 'scroll':
                out.append('Opens a portal to the last town you visited, and back.')
            elif self.k == 'quest':
                out.append('A relic someone is waiting for. Bring it back to claim your reward.')
            elif self.k == 'plant':
                from . import foraging as FG
                if FG.known(FG.GAME, self.t):
                    name, grp, food, eff, _w = FG.PLANTS[self.t]
                    out.append({'deadly': 'Deadly poison. Do not eat.', 'poison': 'Poisonous.', 'sick': 'Makes you sick.',
                                'sleep': 'Puts you to sleep.', 'heal': 'A healing herb.', 'heal2': 'A strong healing herb.',
                                'mana': 'Restores a little mana.', 'cure': 'Settles the stomach and cures poison.'}.get(eff, 'Edible.'))
                    if grp == 'herb':
                        out.append('Used in herbalism (P to brew).')
                else:
                    out.append('You do not know what this is. Eat it to find out, or show it to a herbalist.')
            elif self.k == 'food':
                from .hunger import FOODS
                out.append(f'Food. Eat it to still your hunger (+{FOODS[self.t][1]}).')
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
        if self.dmg:
            out.append(f'Damage {self.dmg[0]}-{self.dmg[1]}')
        if self.arm:
            out.append(f'Armor {self.armor_value()}')
        if b.get('hit'):
            out.append(f"+{b['hit']} to accuracy")
        if b.get('mana'):
            out.append(f"+{b['mana']} to mana")
        if not self.identified:
            out.append('Unidentified. Its powers are hidden until a sage, outfitter or priest in a town identifies it.')
            if self.cursed and self.curse_known:
                out.append('It is cursed!')
            return out
        for s, v in self.aff:
            out.append(D.AFFTXT[s].format(v))
        if self.cursed:
            out.append('CURSED: ' + ', '.join(D.CURSETXT[s].format(v) for s, v in self.curse) +
                       '. Once worn it cannot be removed until a priest lifts the curse.')
        return out

    def value(self):
        """Price in copper."""
        return round(self._value_silver() * 100)

    def _value_silver(self):
        if self.k == 'potion':
            return D.POTIONS[self.t]['val']
        if self.k == 'scroll':
            return 20
        if self.k == 'tome':
            from .skills import SKILLS, UNLOCKS
            return 90 + UNLOCKS.index(SKILLS[self.t].unlock) * 110
        if self.k == 'tool':
            return 8
        if self.k == 'food':
            from .hunger import FOODS
            return FOODS[self.t][2] / 100
        if self.k == 'plant':
            from .foraging import PLANTS
            return .5 if PLANTS[self.t][1] == 'herb' else .2
        if self.k == 'fish':
            from .lifeskills import FISH
            return FISH[self.t][4] * .5
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
        return self.k in ('potion', 'scroll', 'fish', 'food', 'plant')


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
        self.food = 450                        # hunger: 0 starving .. 1000 full
        self.known_plants = set()              # plants you can recognise
        self.recipes = set()                   # herbalism recipes you know
        self.race, self.gender = 'human', 'other'
        self.life = 1
        self.mana = 1
        self.last_target = None


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
def roll_affix(it, pre, exclude):
    c = [a for a in D.AFFIXES if a['pre'] == pre and it.slot in a['slots'] and a['stat'] not in exclude and a['tiers'][0][0] <= it.ilvl]
    if not c:
        c = [a for a in D.AFFIXES if it.slot in a['slots'] and a['stat'] not in exclude and a['tiers'][0][0] <= it.ilvl]
    if not c:
        return None
    a = random.choice(c)
    ts = [t for t in a['tiers'] if t[0] <= it.ilvl]
    t = ts[max(0, len(ts) - 1 - (1 if random.random() < .35 else 0))]
    return [a['stat'], random.randint(t[2], t[3])], t[1], a['pre']


def make_gear(game, bk, rar, ilvl):
    b = D.BASES[bk]
    if b.get('magic_only') and rar == 'normal':
        rar = 'magic'
    it = Item(game.new_id(), 'gear', bk)
    it.base, it.slot, it.rar, it.ilvl, it.req = bk, b['slot'], rar, ilvl, b['lvl']
    if 'dmg' in b:
        it.dmg = tuple(b['dmg'])
    if 'arm' in b:
        it.arm = random.randint(*b['arm'])
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
        for _ in range(random.randint(3, 5)):
            r = roll_affix(it, random.random() < .5, [a[0] for a in it.aff])
            if r:
                it.aff.append(r[0])
        it.name = random.choice(D.RARE_A) + ' ' + random.choice(D.RARE_B)
        it.req = max(b['lvl'], ilvl - 2)
    else:
        it.name = b['name']
    return it


def make_unique(game, u):
    it = make_gear(game, u['base'], 'normal', u['lvl'])
    it.rar = 'unique'
    it.name = u['name']
    it.aff = [[s, v] for s, v in u['aff'].items()]
    it.req = u['lvl']
    return it


def add_curse(it):
    for st, lo, hi in random.sample(D.CURSES, random.randint(1, 2)):
        it.curse.append([st, random.randint(lo, hi) + it.ilvl // 3])


def random_gear(game, ilvl, boost=1, bases=None):
    """Loot. Magic items are rare, arrive unidentified, and now and then carry a hidden curse.
    bases: the kinds of items this source could have (what a monster actually uses)."""
    r = random.random()
    it = None
    if r < .004 * boost and bases is None:
        us = [u for u in D.UNIQUES if not u.get('boss') and u['lvl'] <= ilvl + 2]
        if us:
            it = make_unique(game, random.choice(us))
    if it is None:
        rar = 'rare' if r < .025 * boost else 'magic' if r < .1 * boost else 'normal'
        pool = bases or list(D.BASES)
        ks = [k for k in pool if D.BASES[k]['lvl'] <= ilvl + 1 and not (rar == 'normal' and D.BASES[k].get('magic_only'))]
        if not ks:
            ks = sorted(pool, key=lambda k: D.BASES[k]['lvl'])[:1]
            if rar == 'normal' and D.BASES[ks[0]].get('magic_only'):
                rar = 'magic'
        it = make_gear(game, random.choice(ks), rar, ilvl)
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
        lvl = d['lvl_fix']
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
    return m


def make_npc(game, name, role, fg, x, y, stay, ch='@'):
    m = Monster(game.new_id(), 'npc', x, y)
    m.name, m.role, m.fg, m.stay, m.ch = name, role, D.hexrgb(fg), stay, ch
    return m
