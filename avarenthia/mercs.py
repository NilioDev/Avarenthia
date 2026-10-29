"""Hirelings. In the barracks of the great cities the Iron Company lets out its sellswords by the day, and now and
then one sits in an inn, between contracts. A hireling costs a fee to sign, a daily wage and his food; keep him paid
and fed or he grows sour, and in the end he walks.

Five kinds: the defender (shield, steps in front, takes the blows meant for you), the warrior (a two-handed weapon),
the archer, the healer and the mage. They carry four pieces of gear (weapon, armour, helm, shield) that wear out like
yours, and they grow with you.

Orders (h): follow, defend me, attack my target, hold position, stay out of it.

Who the monsters go for is not shown, but it is not random: each remembers who hurt it and who healed whom, lately;
who stands in its way; who looks soft (light armour, low on life); and how clever it is. A beast goes for the nearest
throat. A clever foe goes for the healer. An archer picks the weakest it can see. And none of them likes to turn
its back on what is hitting it hardest.

Death: in hardcore a fallen hireling is dead, and his gear lies with his body. In softcore a temple can raise him, for
a fee; if you die, he falls with you.

Whoever has learnt Tame from a Beastcraft tome may have a tamed beast as well: a wolf, a bear, a panther or a hawk
(a Packmaster of the Houndwardens' Lodge keeps two). It follows
the same rules (orders, threat, falling and raising), but it has no gear and takes no wage; it eats meat.
Thralls (the dead you raise, the wolves you call) fight for you a while, then fall away."""
import random

from . import data as D
from .worldgen import cheb

KINDS = {
    'defender': dict(name='Defender', hp=40, hpl=11, courage=.85, ranged=False, wage=1.2,
                     weapons=['shortsword', 'mace', 'longsword', 'waraxe'], shield=True, armour='heavy',
                     desc='Shield and sword. Steps in front of you, holds the corridor, takes the blows meant for you.'),
    'warrior': dict(name='Warrior', hp=34, hpl=9, courage=.75, ranged=False, wage=1.2,
                    weapons=['greatsword', 'greataxe', 'maul'], shield=False, armour='heavy',
                    desc='A two-handed weapon and no patience. Hits hard, guards nobody.'),
    'archer': dict(name='Archer', hp=26, hpl=7, courage=.55, ranged=True, wage=1.1,
                   weapons=['shortbow', 'longbow', 'warbow'], shield=False, armour='light',
                   desc='Keeps back and shoots. Never through you.'),
    'healer': dict(name='Healer', hp=24, hpl=6, courage=.45, ranged=True, wage=1.4,
                   weapons=['staff', 'warstaff'], shield=False, armour='light', caster='heal',
                   desc='Mends your wounds in a fight. The clever monsters know it.'),
    'mage': dict(name='Mage', hp=22, hpl=6, courage=.45, ranged=True, wage=1.4,
                 weapons=['staff', 'warstaff'], shield=False, armour='light', caster='bolt',
                 desc='Fire from a distance. Soft as butter up close.'),
    'beast': dict(name='Beast', hp=30, hpl=9, courage=.9, ranged=False, wage=0, weapons=[], shield=False, armour='light',
                  desc='Tamed in the wild. It knows you, and nobody else.'),
}
# what can be tamed, and what it becomes: (name, glyph, colour, life, damage, armour, from these kinds)
TAME = {
    'wolf': dict(name='wolf', ch='C', fg='#c8c8c8', hp=1.0, dmg=1.0, armour=4, kinds=('wolf', 'worg', 'winter_wolf', 'jackal')),
    'bear': dict(name='bear', ch='q', fg='#b08050', hp=1.5, dmg=1.15, armour=8, kinds=('brown_bear', 'cave_bear')),
    'panther': dict(name='panther', ch='f', fg='#8a80a0', hp=.9, dmg=1.3, armour=3, kinds=('panther', 'sabretooth')),
    'hawk': dict(name='hawk', ch='B', fg='#c0a070', hp=.6, dmg=.8, armour=1, kinds=('giant_hawk', 'vulture')),
}
TAME_OF = {k: sp for sp, d in TAME.items() for k in d['kinds']}
BEAST_NAMES = ['Grey', 'Ash', 'Bramble', 'Fang', 'Shadow', 'Tuft', 'Moss', 'Ember', 'Rook', 'Sorrel', 'Thistle', 'Brand']
ORDERS = [('follow', 'Follow me', 'stays close, fights what comes at you'),
          ('defend', 'Defend me', 'only fights what is next to you'),
          ('attack', 'Attack my target', 'goes for the one you have aimed at (Tab)'),
          ('hold', 'Hold position', 'stays where he stands, fights what comes in reach'),
          ('passive', 'Stay out of it', 'follows, never fights')]
ORDER_WORD = {k: w for k, w, _ in ORDERS}
SLOTS = ('weapon', 'armor', 'helm', 'shield')
NAMES = ['Bram', 'Odo', 'Garrick', 'Hild', 'Wenna', 'Tamsin', 'Rurik', 'Agna', 'Corwin', 'Edda', 'Falk', 'Ysolde',
         'Marek', 'Brenna', 'Torvin', 'Ilsa', 'Dunstan', 'Kaya', 'Osric', 'Liesel']
SURNAMES = ['Ironhand', 'of the Marches', 'Greycloak', 'Halfpenny', 'Stonebrook', 'the Quiet', 'Redbeard', 'Ashby',
            'Longstride', 'of Varn', 'Two-Knives', 'Holloway']
HEAVY = {'helm': ['cap', 'skullcap', 'fullhelm', 'greathelm'], 'armor': ['leather', 'ringmail', 'chainmail', 'platemail']}
LIGHT = {'helm': ['cap', 'circlet'], 'armor': ['quilted', 'leather']}
SHIELDS = ['buckler', 'roundshield', 'kiteshield', 'towershield']
FOOD_PER_DAY = 1


class Merc:
    def __init__(self, kind, name, lvl):
        self.kind, self.name, self.lvl = kind, name, lvl
        self.gear = {s: None for s in SLOTS}
        self.hp = 1
        self.order = 'follow'
        self.state = 'alive'            # alive / fallen (softcore, waits for a temple) / gone
        self.morale = 70
        self.flees = 0
        self.fleeing = 0                 # turns left running
        self.away = 0                    # turns since he ran out of sight
        self.paid = 0                    # the last day he was paid
        self.hungry = False
        self.potions = 2
        self.cd = 0                      # cooldown of his special move
        self.frail = 0                   # turns weakened after being raised
        self.wage = 0
        self.body = None                 # the Monster that stands for him on the current map
        self.body_map = None
        self.idle = 0
        self.slot = 'merc'               # 'merc' (game.merc), 'beast' (game.beast) or 'beast2' (Packmaster's second)
        self.species = None
        self.fury = 0                    # turns of Pack Fury
        self.grown = 0                   # turns of Spirit of the Pack

    @property
    def tpl(self):
        return KINDS[self.kind]

    @property
    def who(self):
        """Its key in the monsters' threat tables."""
        return {'beast': 'b', 'beast2': 'b2'}.get(getattr(self, 'slot', 'merc'), 'm')

    def title(self):
        if self.kind == 'beast':
            return f'{self.name}, your {TAME[self.species]["name"]}'
        return f'{self.name}, {self.tpl["name"].lower()}'

    def he(self):
        return 'it' if self.kind == 'beast' else 'he'

    def his(self):
        return 'its' if self.kind == 'beast' else 'his'

    def him(self):
        return 'it' if self.kind == 'beast' else 'him'


def get(game, slot='merc'):
    mc = getattr(game, slot, None)
    return mc if mc and mc.state != 'gone' else None


def with_you(game, slot='merc'):
    mc = get(game, slot)
    return mc if mc and mc.state == 'alive' else None


COMPANY = ('merc', 'beast', 'beast2')


def party(game):
    """Your companions who are with you: the hireling and the tamed beast (two, for a Packmaster)."""
    return [mc for mc in (with_you(game, s_) for s_ in COMPANY) if mc]


def beasts(game):
    """Your tamed beasts, alive or fallen."""
    return [mc for mc in (get(game, 'beast'), get(game, 'beast2')) if mc]


def beast_room(game):
    """The slot a newly tamed beast goes to, or None when you have as many as you may keep."""
    if not get(game, 'beast'):
        return 'beast'
    if 'packmaster' in game.player.known and not get(game, 'beast2'):
        return 'beast2'
    return None


def fallen(game):
    """The first of your companions who lies dead and can still be raised."""
    for slot in COMPANY:
        mc = get(game, slot)
        if mc and mc.state == 'fallen':
            return mc
    return None


def drop(game, mc):
    """It is gone for good: free its place."""
    mc.state = 'gone'
    if getattr(game, getattr(mc, 'slot', 'merc'), None) is mc:
        setattr(game, getattr(mc, 'slot', 'merc'), None)


def of_body(game, b):
    return next((mc for mc in party(game) if mc.body is b), None)


# ------------------------------------------------------------------ numbers
def level_for(game):
    return max(1, game.player.lvl - 1)


def wage_for(kind, lvl):
    """Copper a day. A sellsword is not cheap, but he is not a lord either."""
    return round((40 + lvl * 14) * KINDS[kind]['wage'])


def fee_for(kind, lvl):
    return wage_for(kind, lvl) * 8


def stats(game, mc):
    k = mc.tpl
    lvl = mc.lvl = level_for(game)
    if mc.kind == 'beast':
        return beast_stats(game, mc, lvl)
    s = {}
    s['max_hp'] = k['hp'] + lvl * k['hpl']
    armour = sum(it.armor_value() for slot, it in mc.gear.items() if it and slot != 'weapon' and not broken(it))
    s['armour'] = armour
    s['dr'] = min(55, round(armour * 100 / (armour + 50 + lvl * 6)))
    s['df'] = armour + 6 + lvl * 3
    w = mc.gear['weapon'] if mc.gear['weapon'] and not broken(mc.gear['weapon']) else None
    bd = w.dmg if w else (1 + lvl // 3, 3 + lvl // 2)
    mul = 1 + lvl * .07
    s['dmg'] = (max(1, int(bd[0] * mul)), max(2, int(bd[1] * mul)))
    if k.get('caster') == 'bolt':
        s['dmg'] = (2 + lvl, 5 + lvl * 2)
    s['hit'] = 24 + lvl * 6 + (D.BASES[w.base].get('hit', 0) if w else 0)
    s['block'] = .3 if (mc.gear['shield'] and not broken(mc.gear['shield'])) else 0
    if mc.frail > 0:
        s['max_hp'] = round(s['max_hp'] * .75)
        s['dmg'] = (max(1, round(s['dmg'][0] * .75)), max(1, round(s['dmg'][1] * .75)))
    if mc.hungry:
        s['dmg'] = (max(1, round(s['dmg'][0] * .85)), max(1, round(s['dmg'][1] * .85)))
    return s


def beast_stats(game, mc, lvl):
    sp = TAME[mc.species]
    craft = game.player.disc.get('beastcraft', [0, 0])[0]
    k = 1 + craft / 100                                    # a beastmaster's beast grows with the craft
    s = dict(max_hp=round((30 + lvl * 9) * sp['hp'] * k), armour=sp['armour'] + lvl // 2)
    s['dr'] = min(45, round(s['armour'] * 100 / (s['armour'] + 40 + lvl * 6)))
    s['df'] = s['armour'] + 8 + lvl * 3
    lo, hi = (2 + lvl // 2) * sp['dmg'] * k, (5 + lvl) * sp['dmg'] * k
    if mc.fury > 0:
        lo, hi = lo * 1.4, hi * 1.4
    if getattr(mc, 'grown', 0) > 0:                         # Spirit of the Pack: it grows, for a while
        lo, hi = lo * 1.4, hi * 1.4
        s['max_hp'] = round(s['max_hp'] * 1.4)
    s['dmg'] = (max(1, round(lo)), max(2, round(hi)))
    s['hit'] = 28 + lvl * 6 + craft // 2
    s['block'] = 0
    if mc.frail > 0:
        s['max_hp'] = round(s['max_hp'] * .75)
    if mc.hungry:
        s['dmg'] = (max(1, round(s['dmg'][0] * .85)), max(1, round(s['dmg'][1] * .85)))
    from . import trees as TT
    TT.beast_stats(game, s)
    return s


def tame(game, mon, species=None):
    """A wild beast becomes yours."""
    sp = species or TAME_OF.get(mon.k)
    slot = beast_room(game) or 'beast'
    taken = {b.name for b in beasts(game)}
    mc = Merc('beast', random.choice([n for n in BEAST_NAMES if n not in taken]), level_for(game))
    mc.slot, mc.species = slot, sp
    mc.hp = stats(game, mc)['max_hp']
    mc.paid, mc.potions = game.day, 0
    if mon is not None and mon in game.map.mons:
        game.map.mons.remove(mon)
    setattr(game, slot, mc)
    sync(game)
    if mc.body is not None and mon is not None:
        mc.body.x, mc.body.y = mon.x, mon.y
    return mc


def broken(it):
    return getattr(it, 'mdur', 0) and it.dur <= 0


def wear(game, mc, slot, chance):
    it = mc.gear.get(slot) if slot else random.choice([g for g in mc.gear.values() if g] or [None])
    if not it or not getattr(it, 'mdur', 0) or it.dur <= 0 or random.random() >= chance:
        return
    it.dur -= 1
    if it.dur == 0:
        game.msg(f"{mc.name}'s {it.name} breaks.", 'bad')


# ------------------------------------------------------------------ hiring
def make_offer(game, rng=random):
    kind = rng.choice(['defender', 'defender', 'warrior', 'archer', 'archer', 'healer', 'mage'])
    lvl = max(1, game.player.lvl - 1 + rng.choice([-1, 0, 0, 1]))
    return dict(kind=kind, lvl=lvl, name=f'{rng.choice(NAMES)} {rng.choice(SURNAMES)}', fee=fee_for(kind, lvl),
                wage=wage_for(kind, lvl))


def outfit(game, mc):
    """What a sellsword owns when you sign him: plain, worn-in gear of his trade."""
    from .entities import make_gear
    k = mc.tpl
    lvl = mc.lvl

    def best(keys):
        ok = [b for b in keys if b in D.BASES and D.BASES[b]['lvl'] <= lvl + 1]
        return ok[-1] if ok else keys[0]
    mc.gear['weapon'] = make_gear(game, best(k['weapons']), 'normal', lvl)
    table = HEAVY if k['armour'] == 'heavy' else LIGHT
    mc.gear['armor'] = make_gear(game, best(table['armor']), 'normal', lvl)
    if random.random() < .7:
        mc.gear['helm'] = make_gear(game, best(table['helm']), 'normal', lvl)
    if k['shield']:
        mc.gear['shield'] = make_gear(game, best(SHIELDS), 'normal', lvl)
    for it in mc.gear.values():
        if it is not None:
            it.ided = True
            if getattr(it, 'mdur', 0):
                it.dur = max(1, round(it.mdur * random.uniform(.6, .9)))


def talk_recruit(game, npc):
    from . import events as EV
    from .money import fmt
    o = getattr(npc, 'offer', None)
    if not o:
        game.say(npc, 'Not looking for work. Not from you.')
        return
    k = KINDS[o['kind']]
    if get(game):
        cur = get(game)
        EV.ask(game, 'merc_hire', npc.name, f'"I fight alone or not at all, and you already have {cur.name}." '
               f'(One hireling at a time.)', [('Fair enough', 'bye')], npc=npc.id)
        return
    text = (f'"{o["name"]}. {k["name"]}, level {o["lvl"]}. {k["desc"]} {fmt(o["fee"])} to sign, then {fmt(o["wage"])} a day, '
            f'and I eat what you eat. Miss a wage or a meal and I will remember it."')
    EV.ask(game, 'merc_hire', npc.name, text, [(f'Hire {o["name"].split()[0]} ({fmt(o["fee"])})', 'hire'), ('Not today', 'bye')],
           npc=npc.id)


def r_hire(game, choice, ctx):
    from .money import fmt
    npc = next((o for o in game.map.mons if o.id == ctx.get('npc')), None)
    if choice != 'hire' or not npc or not getattr(npc, 'offer', None) or get(game):
        return
    o = npc.offer
    if game.player.gold < o['fee']:
        game.msg(f'Signing {o["name"]} costs {fmt(o["fee"])}.', 'bad')
        return
    game.player.gold -= o['fee']
    mc = Merc(o['kind'], o['name'], o['lvl'])
    outfit(game, mc)
    mc.hp = stats(game, mc)['max_hp']
    mc.paid = game.day
    mc.wage = o['wage']
    game.merc = mc
    game.map.mons.remove(npc)
    mc.body, mc.body_map = None, None
    sync(game)
    game.msg(f'{mc.name} signs on. Orders: h.', 'gold')


def place_recruits(game, m, s, buildings, names):
    """Sellswords for hire: a few in the barracks of a city, and now and then one in an inn."""
    from .towns import free_inside
    from .entities import make_npc
    rng = random.Random(s.id * 7919 + game.day // 7)
    spots = []
    barracks = [p for p in buildings if p.kind == 'barracks']
    inns = [p for p in buildings if p.kind == 'inn']
    if s.kind in ('city', 'metropolis') and barracks:
        n = 3 if s.kind == 'metropolis' else 2
        for _ in range(n):
            spots.append(random.choice(barracks))
    elif inns and random.random() < .12:
        spots.append(inns[0])
    for pl in spots:
        cells = free_inside(m, pl)
        if not cells:
            continue
        o = make_offer(game, rng)
        npc = make_npc(game, f'{o["name"]}, sellsword', 'recruit', '#d8c8a0', cells[0][0], cells[0][1], True)
        npc.offer = o
        m.mons.append(npc)


# ------------------------------------------------------------------ being there
def sync(game):
    """Keep the hireling's body next to you: through stairs, doors, towns and the wilds. On the world map he simply
    walks with you."""
    for mc in party(game):
        _sync(game, mc)
    th = getattr(game, 'thralls', None)
    if th:                                            # thralls do not follow you off the map they were raised on
        game.thralls = [b for b in th if b in game.map.mons]
    from . import epics as EP
    EP.keep_king(game)                                # but the barrow king walks with you until you rest


def _sync(game, mc):
    m = game.map
    b = mc.body
    if b is not None and mc.body_map != game.cur:
        old = game.maps.get(mc.body_map)
        if old is not None and b in old.mons:
            old.mons.remove(b)
        b = mc.body = None
    if m.kind == 'over':
        return
    if b is not None and b in m.mons:
        if cheb(b.x, b.y, game.player.x, game.player.y) > 14 and not mc.fleeing:
            place(game, mc, b)
        return
    from .entities import make_npc
    if mc.kind == 'beast':
        sp = TAME[mc.species]
        b = make_npc(game, mc.name, 'merc_ally', sp['fg'], 0, 0, True, ch=sp['ch'])
    else:
        b = make_npc(game, mc.name, 'merc_ally', '#f0e0b0', 0, 0, True, ch='☻')
    b.ally = True
    b.comp = mc.slot
    b.awake = True
    mc.body, mc.body_map = b, game.cur
    refresh_body(game, mc)
    if place(game, mc, b):
        m.mons.append(b)


def place(game, mc, b):
    from . import worldgen as W
    p = game.player
    spots = W.free_around(game, game.map, p.x, p.y, 2)
    spots = [c for c in spots if c != (p.x, p.y)]
    if not spots:
        return False
    b.x, b.y = min(spots, key=lambda c: cheb(c[0], c[1], p.x, p.y))
    return True


def refresh_body(game, mc):
    b = mc.body
    if b is None:
        return
    s = stats(game, mc)
    b.maxhp = s['max_hp']
    b.hp = mc.hp = min(mc.hp, s['max_hp'])
    b.df, b.dmg, b.hit_r, b.lvl = s['df'], s['dmg'], s['hit'], mc.lvl
    base = TAME[mc.species]['fg'] if mc.kind == 'beast' else '#f0e0b0'
    b.fg = D.hexrgb(base) if not mc.fleeing else D.hexrgb('#b0a080')


def is_body(o):
    return getattr(o, 'ally', False)


def on_watch(game):
    """A hireling (or a beast) who is with you keeps watch while you sleep in the open."""
    pt = party(game)
    return pt[0] if pt else None


# ------------------------------------------------------------------ who the monsters go for
def smart(mon):
    t = mon.tpl
    return t['ch'] in '@hKk' or t['caster'] or 'faction' in t.get('tags', '') or mon.k in ('goblin', 'gobarcher', 'kobold', 'orc', 'cultist')


def add_threat(mon, who, amount):
    th = mon.__dict__.setdefault('threat', {})
    th[who] = th.get(who, 0) + amount


def decay(m):
    for o in m.mons:
        th = getattr(o, 'threat', None)
        if th:
            for k in th:
                th[k] *= .9


def score(game, mon, who, b, mc):
    p = game.player
    x, y = (p.x, p.y) if who == 'p' else (b.x, b.y)
    who = 'p' if who == 'p' else mc.who
    d = cheb(mon.x, mon.y, x, y)
    s = mon.__dict__.get('threat', {}).get(who, 0)
    beast = not smart(mon)
    s += (14 if d <= 1 else -2.5 * d) * (2 if beast else 1)
    if who == 'm' and mc.kind == 'defender' and d <= 1 and b.hp > b.maxhp * .4:
        s += 8                                           # he is in the way, shield up
    if not beast:
        if who == 'p':
            ps = game.stats()
            frac = p.life / max(1, ps['max_life'])
            soft = ps['def'] < 15 + p.lvl * 3
        else:
            frac = b.hp / max(1, b.maxhp)
            soft = mc.tpl['armour'] == 'light'
        s += (1 - frac) * 8 + (5 if soft else 0)
        if who == 'm' and mc.kind in ('healer', 'mage'):
            s += 6                                       # kill the healer first
        if (mon.tpl['ranged'] or mon.tpl['caster']) and not game.line_clear(mon.x, mon.y, x, y):
            s -= 10
    return s


def pick(game, mon):
    """'p' for you, 'm' for the hireling, 'b' for the beast. Sticky: it does not turn on a whim."""
    cands = {mc.who: mc for mc in party(game) if mc.body is not None and mc.body in game.map.mons and not mc.fleeing}
    if not cands:
        return 'p'
    sc = {'p': score(game, mon, 'p', None, None)}
    for w, mc in cands.items():
        sc[w] = score(game, mon, 'c', mc.body, mc)
    cur = getattr(mon, 'aim', 'p')
    if cur not in sc:
        cur = 'p'
    best = max(sc, key=sc.get)
    if best != cur and sc[best] > sc[cur] * 1.3 + 3:
        cur = best
    mon.aim = cur
    return cur


def mon_turn(game, mon, df):
    """A monster that has picked the hireling or the beast (or stands next to a thrall). Returns False to let it go for
    you as usual."""
    w = pick(game, mon)
    if w == 'p':
        return thrall_fight(game, mon)
    mc = next(c for c in party(game) if c.who == w)
    b = mc.body
    d = cheb(mon.x, mon.y, b.x, b.y)
    t = mon.tpl
    if (t['ranged'] or t['caster']) and 2 <= d <= 7 and random.random() < .55:
        path = game.line_clear(mon.x, mon.y, b.x, b.y)
        if path:
            game.fx('bolt', cells=path, src=(mon.x, mon.y), col=(255, 122, 60) if t['caster'] else (216, 208, 176),
                    ch='*' if t['caster'] else '-')
            if t['caster'] or random.random() < game.mon_hit_chance(mon, b.df):
                hurt(game, mc, random.randint(*mon.dmg) * .85, mon)
            else:
                game.num(b.x, b.y, 'miss', (150, 150, 150))
            return True
    if d <= 1:
        if random.random() < game.mon_hit_chance(mon, b.df):
            hurt(game, mc, random.randint(*mon.dmg), mon)
        else:
            game.num(b.x, b.y, 'miss', (150, 150, 150))
        return True
    return step_to(game, mon, b.x, b.y)


def intercept(game, mon):
    """The defender throws himself between you and the blow."""
    mc = with_you(game)
    if not mc or mc.kind != 'defender' or mc.fleeing or mc.order == 'passive':
        return False
    b = mc.body
    if b is None or b not in game.map.mons or b.hp < b.maxhp * .35:
        return False
    p = game.player
    if cheb(b.x, b.y, p.x, p.y) > 1 or cheb(b.x, b.y, mon.x, mon.y) > 1 or random.random() > .3:
        return False
    game.msg(f'{mc.name} takes the blow on his shield.', 'good')
    hurt(game, mc, random.randint(*mon.dmg), mon, block=.5)
    add_threat(mon, 'm', 6)
    return True


def hurt(game, mc, dmg, mon=None, block=0.0):
    b = mc.body
    s = stats(game, mc)
    if s['block'] and random.random() < s['block'] + (.15 if mc.kind == 'defender' else 0):
        block = max(block, .6)
        wear(game, mc, 'shield', .4)
    dmg = max(1, round(dmg * (1 - s['dr'] / 100) * (1 - block)))
    mc.hp -= dmg
    if b is not None:
        b.hp = mc.hp
        game.num(b.x, b.y, f'-{dmg}', (236, 140, 92))
    wear(game, mc, None, .3)
    from . import epics as EP
    if mc.hp <= 0 and EP.one_blood(game, mc):         # One Blood: your beast cannot die now
        mc.hp = 1
        if b is not None:
            b.hp = 1
    if mc.hp <= 0:
        fall(game, mc, mon.the() if mon else f'{mc.his()} wounds')
    elif mc.hp < s['max_hp'] * .25 and not mc.fleeing and random.random() > mc.tpl['courage'] * (.5 + mc.morale / 140):
        mc.fleeing = 14
        mc.flees += 1
        mc.morale -= 6
        game.msg(f'{mc.name} breaks and runs!', 'bad')


def fall(game, mc, cause):
    """Down. In hardcore, dead: his gear lies with his body. In softcore, a temple can raise him."""
    from .entities import Item
    from . import epics as EP
    b = mc.body
    m = game.map
    mc.fell_turn = game.turn                          # for Return, the restorer's epic
    EP.st(game)['fell'] = (getattr(mc, 'slot', 'merc'), mc)
    if b is not None and b in m.mons:
        m.mons.remove(b)
    if game.player.hardcore:
        game.msg(f'{mc.name} is dead, slain by {cause}.', 'bad')
        if b is not None and mc.kind != 'beast':
            body = Item(game.new_id(), 'corpse', 'corpse')
            body.name = f'the body of {mc.name}'
            body.payload = dict(items=[it for it in mc.gear.values() if it], cargo={}, cost={}, gold=0)
            body.x, body.y = b.x, b.y
            m.items.append(body)
        drop(game, mc)
    else:
        game.msg(f'{mc.name} falls, slain by {cause}. A temple can raise {mc.him()}.', 'bad')
        mc.state = 'fallen'
        mc.hp = 0
    mc.body = None


def on_player_death(game):
    """When you fall, your hireling (and your beast) fall with you."""
    game.thralls = []
    for mc in party(game):
        b = mc.body
        if b is not None:
            for gm in game.maps.values():
                if b in gm.mons:
                    gm.mons.remove(b)
        mc.body = None
        mc.state = 'fallen'
        mc.hp = 0


def raise_fee(game, mc=None):
    mc = mc or fallen(game) or get(game)
    if not mc:
        return 0
    from . import guilds as GU
    return round(game.raise_fee(mc.lvl) // 2 * GU.temple_mult(game))


def raise_up(game, mc=None, free=False):
    mc = mc or fallen(game)
    if not mc or mc.state != 'fallen':
        return False
    fee = 0 if free else raise_fee(game, mc)
    if game.player.gold < fee:
        return False
    game.player.gold -= fee
    mc.state = 'alive'
    mc.frail = 2 * D.DAY_LEN
    mc.hp = stats(game, mc)['max_hp'] // 2
    mc.fleeing = 0
    sync(game)
    game.msg(f'{mc.name} draws breath again. {mc.he().capitalize()} will be weak for a day or two.', 'good')
    return True


# ------------------------------------------------------------------ his turn
def free(game, x, y):
    m = game.map
    return m.inb(x, y) and D.TILES[m.tile(x, y)].walk and not game.occupied(m, x, y)


def step_to(game, who, tx, ty, away=False):
    m = game.map
    best = None
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
        nx, ny = who.x + dx, who.y + dy
        if not m.inb(nx, ny):
            continue
        t = m.tile(nx, ny)
        if t == D.DOOR and not game.occupied(m, nx, ny):
            d = cheb(nx, ny, tx, ty)
            if best is None or (d > best[0] if away else d < best[0]):
                best = (d, nx, ny, True)
            continue
        if not free(game, nx, ny):
            continue
        if not who.is_npc and getattr(who, 'bs', None) is not None:
            from . import bosses as BS
            if not BS.may_stand(game, who, nx, ny):
                continue
        d = cheb(nx, ny, tx, ty)
        if best is None or (d > best[0] if away else d < best[0]):
            best = (d, nx, ny, False)
    here = cheb(who.x, who.y, tx, ty)
    if not best or (best[0] <= here if away else best[0] >= here):
        return False
    if best[3]:
        m.set(best[1], best[2], D.ODOOR)
        return True
    who.x, who.y = best[1], best[2]
    return True


def follow_step(game, b):
    """Down the distance map towards you, the way the monsters come."""
    m, dist = game.map, getattr(game, 'dist', None)
    if dist is None or len(dist) != m.w * m.h:
        return step_to(game, b, game.player.x, game.player.y)
    cd = dist[b.y * m.w + b.x]
    best = None
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
        nx, ny = b.x + dx, b.y + dy
        if not m.inb(nx, ny) or game.occupied(m, nx, ny):
            continue
        di = dist[ny * m.w + nx]
        if di < 0 or (cd >= 0 and di >= cd):
            continue
        if best is None or di < best[0]:
            best = (di, nx, ny)
    if not best:
        return step_to(game, b, game.player.x, game.player.y)
    if m.tile(best[1], best[2]) == D.DOOR:
        m.set(best[1], best[2], D.ODOOR)
        return True
    b.x, b.y = best[1], best[2]
    return True


def hostiles(game):
    return [o for o in game.map.mons if not o.is_npc and o.awake and game.visible(o.x, o.y) and not getattr(o, 'lurk', False)]


def choose(game, mc, b, foes):
    p = game.player
    if mc.order == 'passive' or not foes:
        return None
    from . import bosses as BS
    first = BS.ally_target(game, mc, b, foes)          # a spent boss, then the warder first
    if first is not None:
        return first
    if mc.order == 'attack':
        t = game.target()
        if t is not None and t in foes:
            return t
    if mc.order == 'defend':
        near = [o for o in foes if cheb(o.x, o.y, p.x, p.y) <= 2]
        return min(near, key=lambda o: cheb(o.x, o.y, b.x, b.y)) if near else None
    if mc.order == 'hold':
        reach = 7 if mc.tpl['ranged'] else 1
        near = [o for o in foes if cheb(o.x, o.y, b.x, b.y) <= reach]
        return min(near, key=lambda o: o.hp) if near else None
    near = [o for o in foes if cheb(o.x, o.y, p.x, p.y) <= 7 or cheb(o.x, o.y, b.x, b.y) <= 2]
    if not near:
        return None
    # the ones going for you, or for him, first; then the closest
    return min(near, key=lambda o: (getattr(o, 'aim', 'p') not in ('p', 'm'), cheb(o.x, o.y, b.x, b.y)))


def strike(game, mc, b, mon, s, ranged=False):
    acc = s['hit'] / (s['hit'] + mon.df * .8)
    if random.random() >= max(.25, min(.95, acc)):
        game.num(mon.x, mon.y, 'miss', (150, 150, 150))
        mon.awake = True
        return
    dmg = random.randint(*s['dmg'])
    if mc.kind == 'beast':
        from . import trees as TT
        dmg = round(dmg * TT.beast_mult(game, mon))
    crit = random.random() < .06
    if crit:
        dmg = round(dmg * 1.6)
    wear(game, mc, 'weapon', .15)
    add_threat(mon, mc.who, dmg * (1.6 if mc.kind == 'defender' else 1))
    mon.awake = True
    if mc.kind == 'beast':
        from . import trees as TT
        TT.beast_struck(game, mon, mc, dmg)
    if mon.hp - dmg <= 0:
        game.msg(f'{mc.name} kills {mon.the()}.', 'good')
        mon.hp = 0
        game.kill(mon)
        return
    mon.hp -= dmg
    game.num(mon.x, mon.y, str(dmg), (240, 220, 150))


def shoots_clear(game, b, mon):
    path = game.line_clear(b.x, b.y, mon.x, mon.y)
    if not path:
        return None
    p = game.player
    if any((x, y) == (p.x, p.y) for x, y in path[:-1]):
        return None                                  # never through you
    return path


def act(game, b):
    """One turn of the hireling, the beast or a thrall."""
    if getattr(b, 'thrall', 0):
        return thrall_act(game, b)
    mc = of_body(game, b)
    if not mc:
        if b in game.map.mons:
            game.map.mons.remove(b)
        return
    if mc.fury > 0:
        mc.fury -= 1
    if getattr(mc, 'grown', 0) > 0:
        mc.grown -= 1
    p = game.player
    s = stats(game, mc)
    refresh_body(game, mc)
    if mc.frail > 0:
        mc.frail -= 1
    if mc.cd > 0:
        mc.cd -= 1
    if b.hold > 0:
        b.hold -= 1
        return
    from . import bosses as BS
    if BS.ally_turn(game, mc, b):                    # out of the red, a shield into a loading boss
        return
    foes = hostiles(game)
    if mc.fleeing:
        mc.fleeing -= 1
        if foes:
            near = min(foes, key=lambda o: cheb(o.x, o.y, b.x, b.y))
            step_to(game, b, near.x, near.y, away=True)
        if not mc.fleeing:
            game.msg(f'{mc.name} comes back, not meeting your eye.', 'info')
        return
    if not foes:
        mc.idle += 1
        if mc.idle % 3 == 0 and mc.hp < s['max_hp']:
            mc.hp = min(s['max_hp'], mc.hp + 1 + s['max_hp'] // 40)
    else:
        mc.idle = 0
    # drink when hurt
    if foes and mc.hp < s['max_hp'] * .35 and mc.potions > 0:
        mc.potions -= 1
        mc.hp = min(s['max_hp'], mc.hp + s['max_hp'] // 2)
        game.num(b.x, b.y, 'drinks', (120, 240, 140))
        return
    # the healer: you first, then himself
    if mc.kind == 'healer' and mc.cd == 0 and mc.order != 'passive':
        ps = game.stats()
        if p.life < ps['max_life'] * .6 and cheb(b.x, b.y, p.x, p.y) <= 7:
            amt = 8 + mc.lvl * 4
            game.heal(amt, True)
            mc.cd = 4
            for o in foes:
                add_threat(o, mc.who, amt * .5)
            return
        if mc.hp < s['max_hp'] * .5:
            mc.hp = min(s['max_hp'], mc.hp + 6 + mc.lvl * 3)
            mc.cd = 4
            game.num(b.x, b.y, 'healed', (120, 240, 140))
            return
    tgt = choose(game, mc, b, foes)
    if tgt is not None:
        d = cheb(b.x, b.y, tgt.x, tgt.y)
        if mc.tpl['ranged']:
            if d <= 1 and mc.order != 'hold' and step_to(game, b, tgt.x, tgt.y, away=True):
                return
            if 1 <= d <= 8:
                path = shoots_clear(game, b, tgt)
                if path:
                    col = (255, 130, 60) if mc.kind == 'mage' else (240, 240, 180) if mc.kind == 'healer' else (216, 208, 176)
                    game.fx('bolt', cells=path, src=(b.x, b.y), col=col, ch='*' if mc.tpl.get('caster') else '-')
                    strike(game, mc, b, tgt, s, True)
                    return
            if mc.order != 'hold':
                # find a clear shot: step aside, or closer
                if d > 6:
                    step_to(game, b, tgt.x, tgt.y)
                else:
                    follow_step(game, b) if cheb(b.x, b.y, p.x, p.y) > 2 else step_to(game, b, p.x, p.y)
            return
        if d <= 1:
            if mc.kind == 'defender' and mc.cd == 0 and mc.gear['shield'] and random.random() < .3:
                mc.cd = 5
                tgt.hold = max(tgt.hold, 1)
                add_threat(tgt, mc.who, 10)
                game.msg(f'{mc.name} slams his shield into {tgt.the()}.', 'good')
                return
            strike(game, mc, b, tgt, s)
            return
        if mc.order != 'hold':
            step_to(game, b, tgt.x, tgt.y) or follow_step(game, b)
        return
    if mc.order == 'hold':
        return
    gap = cheb(b.x, b.y, p.x, p.y)
    if gap > 2 or (gap > 1 and game.map.kind == 'dungeon'):
        follow_step(game, b)


# ------------------------------------------------------------------ pay and food
def daily(game):
    """A day's wage, a day's food. Short him either and his mood sours; let it sour far enough and he walks."""
    from .money import fmt
    for bst in [with_you(game, s_) for s_ in ('beast', 'beast2')]:
        if bst:
            feed_beast(game, bst)
    mc = get(game)
    if not mc or mc.state != 'alive':
        return
    p = game.player
    if getattr(mc, 'free_days', 0) > 0:
        mc.free_days -= 1                            # a week for a vanilla cream
        mc.paid = game.day
    elif p.gold >= mc.wage:
        p.gold -= mc.wage
        mc.paid = game.day
        mc.morale = min(100, mc.morale + 2)
    else:
        mc.morale -= 20
        game.msg(f'You cannot pay {mc.name} his {fmt(mc.wage)}. He says nothing, which is worse.', 'bad')
    from .hunger import food_value
    food = [it for it in p.inv if it.k in ('food', 'dish') and food_value(it) >= 60 and it.t not in ('drake_egg', 'elder_sap')]
    if food:
        it = min(food, key=lambda f: f.value())
        game.remove_one(it)
        mc.hungry = False
    else:
        mc.hungry = True
        mc.morale -= 12
        game.msg(f'{mc.name} goes hungry. Carry food for two.', 'bad')
    if mc.morale < 15 or mc.flees >= 5:
        leave(game, mc, 'unpaid' if mc.morale < 15 else 'afraid')


def feed_beast(game, mc):
    """No wage: meat. Without it the beast grows thin and sour, and in the end it goes back to the wild."""
    p = game.player
    food = [it for it in p.inv if it.k == 'food']
    from .hunger import RAW
    meat = [it for it in food if getattr(it, 't', '') in RAW | {'jerky', 'fish', 'smoked_fish'}]
    if meat:
        game.remove_one(min(meat, key=lambda f: f.value()))
        mc.hungry = False
        mc.morale = min(100, mc.morale + 3)
    else:
        mc.hungry = True
        mc.morale -= 15
        game.msg(f'{mc.name} goes hungry. A beast needs meat.', 'bad')
    if mc.morale < 15:
        b = mc.body
        if b is not None and b in game.map.mons:
            game.map.mons.remove(b)
        drop(game, mc)
        game.msg(f'{mc.name} looks at you a long while, then turns and lopes off into the wild.', 'bad')


def leave(game, mc, why):
    b = mc.body
    if b is not None and b in game.map.mons:
        game.map.mons.remove(b)
    drop(game, mc)
    game.msg(f'{mc.name} has had enough. ' + ('"Find someone else to starve."' if why == 'unpaid' else
                                              '"This is no work for a living man."') + ' He leaves, and takes his gear.', 'bad')


def restock(game):
    """In a town he tops up his own potions, out of his wage."""
    mc = with_you(game)
    if mc:
        mc.potions = max(mc.potions, 2)


# ------------------------------------------------------------------ thralls: the raised dead, the called pack
def thrall(game, k, x, y, turns, name=None, lvl=None):
    """Something that fights at your side for a while: a corpse you raised, a wolf that answered your call."""
    from .entities import make_monster, make_npc
    src = make_monster(game, k, x, y, lvl or game.player.lvl)        # its strength, in the shape of an ally
    o = make_npc(game, name or src.name, 'thrall', '#c8c8c8', x, y, False, ch=src.ch)
    o.fg, o.hp, o.maxhp, o.dmg, o.df, o.lvl = src.fg, src.hp, src.maxhp, src.dmg, src.df, src.lvl
    o.ally, o.awake, o.thrall, o.thrall_k = True, True, turns, k
    game.map.mons.append(o)
    game.__dict__.setdefault('thralls', []).append(o)
    from . import trees as TT
    TT.thrall_made(game, o)
    return o


def thrall_act(game, b):
    b.thrall -= 1
    if b.thrall <= 0 or b.hp <= 0:
        if b in game.map.mons:
            game.map.mons.remove(b)
        if game.visible(b.x, b.y):
            k = getattr(b, 'thrall_k', 'wolf')
            game.msg(f'{b.name} ' + ('crumbles to dust.' if D.MONSTERS[k].get('family') == 'undead' or k in D.UNDEAD
                                     else 'falls still, and is only a corpse again.' if b.name.startswith('Risen')
                                     else 'slips away into the wild.'), 'info')
        return
    foes = hostiles(game)
    if not foes:
        if cheb(b.x, b.y, game.player.x, game.player.y) > 2:
            follow_step(game, b)
        return
    t = min(foes, key=lambda o: cheb(o.x, o.y, b.x, b.y))
    if cheb(t.x, t.y, b.x, b.y) <= 1:
        acc = (b.lvl * 6 + 30) / (b.lvl * 6 + 30 + t.df * .8)
        if random.random() < max(.3, min(.9, acc)):
            dmg = random.randint(*b.dmg)
            add_threat(t, 'p', dmg * .5)
            t.awake = True
            from . import trees as TT
            TT.thrall_hit(game, t)
            if t.hp - dmg <= 0:
                game.msg(f'{b.name} kills {t.the()}.', 'good')
                t.hp = 0
                game.kill(t)
            else:
                t.hp -= dmg
                game.num(t.x, t.y, str(dmg), (200, 200, 160))
        else:
            game.num(t.x, t.y, 'miss', (150, 150, 150))
        return
    step_to(game, b, t.x, t.y) or follow_step(game, b)


def thrall_fight(game, mon):
    """A monster with a thrall at its throat and you out of reach turns on the thrall."""
    p = game.player
    if cheb(mon.x, mon.y, p.x, p.y) <= 1:
        return False
    near = [b for b in getattr(game, 'thralls', []) if b in game.map.mons and cheb(b.x, b.y, mon.x, mon.y) <= 1]
    if not near or random.random() < .3:
        return False
    b = near[0]
    if random.random() < game.mon_hit_chance(mon, b.df):
        dmg = random.randint(*mon.dmg)
        b.hp -= dmg
        game.num(b.x, b.y, f'-{dmg}', (236, 140, 92))
        if b.hp <= 0:
            b.thrall = 0
            thrall_act(game, b)
    return True


# ------------------------------------------------------------------ orders (h)
def menu(game, slot=None):
    """h, or walking into your companion: the company screen (ui.CompanyScreen), opened on that companion."""
    from .money import fmt
    mcs = [mc for mc in (get(game, s_) for s_ in COMPANY) if mc]
    if not mcs:
        game.msg('You have no hireling. Sellswords are for hire in the barracks of the cities.', 'info')
        return
    if all(mc.state == 'fallen' for mc in mcs):
        mc = mcs[0]
        game.msg(f'{mc.name} lies dead. A temple can raise {mc.him()}, for {fmt(raise_fee(game, mc))}.', 'info')
        return
    game.request = ('company', slot)


def set_order(game, mc, k):
    """Give one companion an order; it answers in the log."""
    mc.order = k
    if mc.kind == 'beast':
        game.msg(f'{mc.name} ' + {'follow': 'falls in at your heel.', 'defend': 'keeps close, hackles up.',
                                  'attack': 'fixes its eyes on your target.', 'hold': 'sits, and stays.',
                                  'passive': 'lies down, ears flat.'}[k], 'talk')
    else:
        game.msg(f'{mc.name}: "{ORDER_LINE[k]}"', 'talk')


def give_menu(game, slot):
    """Hand the hireling something for one of his four slots, from your pack."""
    from . import events as EV
    mc = get(game, 'merc')
    if not mc or mc.state != 'alive':
        return
    cands = [it for it in game.backpack() if it.k == 'gear' and D.BASES[it.base]['slot'] == slot and fits(mc, it)]
    if not cands:
        game.msg(f'Nothing in your pack that {mc.name} can use there.', 'info')
        return
    EV.ask(game, 'merc_give', mc.name, 'What do you hand him? He gives you back what he had.',
           [(it.display_name(), f'g:{it.id}') for it in cands[:10]] + [('Nothing', 'bye')])


def dismiss_menu(game, slot):
    from . import events as EV
    mc = get(game, slot)
    if not mc:
        return
    if mc.kind == 'beast':
        EV.ask(game, 'merc_dismiss', mc.name, f'Set {mc.name} free? It will go back to the wild.',
               [('Set it free', 'yes'), ('No', 'bye')], slot=slot)
    else:
        EV.ask(game, 'merc_dismiss', mc.name, f'Let {mc.name} go? He keeps his gear and his last wage.',
               [('Dismiss him', 'yes'), ('No', 'bye')])


def mood(mc):
    if mc.kind == 'beast':
        return 'content' if mc.morale >= 60 else 'restless' if mc.morale >= 35 else 'close to going back to the wild'
    return 'content' if mc.morale >= 60 else 'grumbling' if mc.morale >= 35 else 'close to walking out'


ORDER_LINE = {'follow': 'Right behind you.', 'defend': 'Nothing gets to you.', 'attack': 'Point, and I go.',
              'hold': 'I hold here.', 'passive': 'As you say. I keep out of it.'}


def fits(mc, it):
    b = D.BASES[it.base]
    if b['slot'] == 'weapon':
        if mc.tpl['ranged'] and mc.kind == 'archer':
            return bool(b.get('ranged'))
        if mc.kind in ('healer', 'mage'):
            return b['family'] in ('staff', 'warstaff')
        if b.get('ranged'):
            return False
        return bool(b.get('two')) if mc.kind == 'warrior' else not b.get('two')
    if b['slot'] == 'shield':
        return mc.kind == 'defender' and b['family'] != 'grimoire'
    return True


def r_give(game, choice, ctx):
    mc = get(game)
    if not mc or not choice.startswith('g:'):
        return
    it = next((x for x in game.player.inv if x.id == int(choice[2:])), None)
    if not it:
        return
    slot = D.BASES[it.base]['slot']
    old = mc.gear.get(slot)
    game.player.inv.remove(it)
    mc.gear[slot] = it
    if old:
        game.add_to_inv(old)
    refresh_body(game, mc)
    game.msg(f'{mc.name} takes {it.name}' + (f' and hands you his {old.name}.' if old else '.'), 'info')


def r_dismiss(game, choice, ctx):
    mc = get(game, ctx.get('slot', 'merc'))
    if mc and choice == 'yes':
        b = mc.body
        if b is not None and b in game.map.mons:
            game.map.mons.remove(b)
        drop(game, mc)
        game.msg(f'{mc.name} looks back once, and lopes off into the wild.' if mc.kind == 'beast' else
                 f'{mc.name} nods, shoulders his pack and goes.', 'info')


def worn(game):
    mc = get(game)
    if not mc:
        return []
    return [it for it in mc.gear.values() if it and getattr(it, 'mdur', 0) and it.dur < it.mdur]


def register():
    from . import events as EV
    EV.RESOLVERS.update(merc_give=r_give, merc_dismiss=r_dismiss, merc_hire=r_hire)


register()
