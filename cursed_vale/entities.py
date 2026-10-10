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

    # ---------------------------------------------------------- presentation
    def display_name(self):
        if self.k == 'gold':
            return f'{self.n} gold'
        if self.k == 'potion':
            return (f'{self.n}x ' if self.n > 1 else '') + D.POTIONS[self.t]['name']
        if self.k == 'scroll':
            return (f'{self.n}x ' if self.n > 1 else '') + 'Scroll of Town Portal'
        if self.k == 'orb':
            return 'health orb'
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
                out.append('Opens a portal to Thornfield and back.')
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
        for s, v in self.aff:
            out.append(D.AFFTXT[s].format(v))
        return out

    def value(self):
        if self.k == 'potion':
            return D.POTIONS[self.t]['val']
        if self.k == 'scroll':
            return 30
        if self.k != 'gear':
            return 0
        return round(D.BASES[self.base]['val'] * D.RARITY_MULT[self.rar] + len(self.aff) * 10)

    @property
    def stackable(self):
        return self.k in ('potion', 'scroll')


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
    def __init__(self, name, cls):
        c = D.CLASSES[cls]
        self.name = name
        self.cls = cls
        self.x = self.y = 0
        self.lvl = 1
        self.xp = 0
        self.str, self.dex, self.vit, self.ene = c['str'], c['dex'], c['vit'], c['ene']
        self.stat_pts = 0
        self.skill_pts = 0
        self.skills = {D.SKILLS[cls][0].id: 1}
        self.inv = []
        self.eq = {}
        self.gold = 50
        self.poison = None      # [turns, damage]
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


def random_gear(game, ilvl, boost=1):
    r = random.random()
    if r < .012 * boost:
        us = [u for u in D.UNIQUES if not u.get('boss') and u['lvl'] <= ilvl + 2]
        if us:
            return make_unique(game, random.choice(us))
    rar = 'rare' if r < .09 * boost else 'magic' if r < .34 * boost else 'normal'
    ks = [k for k, b in D.BASES.items() if b['lvl'] <= ilvl + 1]
    return make_gear(game, random.choice(ks), rar, ilvl)


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
