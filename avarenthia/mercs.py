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
a fee; if you die, he falls with you."""
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
}
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

    @property
    def tpl(self):
        return KINDS[self.kind]

    def title(self):
        return f'{self.name}, {self.tpl["name"].lower()}'


def get(game):
    mc = getattr(game, 'merc', None)
    return mc if mc and mc.state != 'gone' else None


def with_you(game):
    mc = get(game)
    return mc if mc and mc.state == 'alive' else None


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
    mc = with_you(game)
    if not mc:
        return
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
    b = make_npc(game, mc.name, 'merc_ally', '#f0e0b0', 0, 0, True, ch='☻')
    b.ally = True
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
    b.fg = D.hexrgb('#f0e0b0') if not mc.fleeing else D.hexrgb('#b0a080')


def is_body(o):
    return getattr(o, 'ally', False)


def on_watch(game):
    """A hireling who is with you keeps watch while you sleep in the open."""
    return with_you(game)


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
    """'p' for you, 'm' for the hireling. Sticky: it does not turn on a whim."""
    mc = with_you(game)
    b = mc.body if mc else None
    if not mc or b is None or b not in game.map.mons or mc.fleeing:
        return 'p'
    sp, sm = score(game, mon, 'p', b, mc), score(game, mon, 'm', b, mc)
    cur = getattr(mon, 'aim', 'p')
    if cur == 'p' and sm > sp * 1.3 + 3:
        cur = 'm'
    elif cur == 'm' and sp > sm * 1.3 + 3:
        cur = 'p'
    mon.aim = cur
    return cur


def mon_turn(game, mon, df):
    """A monster that has picked the hireling. Returns False to let it go for you as usual."""
    if pick(game, mon) != 'm':
        return False
    mc = with_you(game)
    b = mc.body
    d = cheb(mon.x, mon.y, b.x, b.y)
    t = mon.tpl
    if (t['ranged'] or t['caster']) and 2 <= d <= 7 and random.random() < .55:
        path = game.line_clear(mon.x, mon.y, b.x, b.y)
        if path:
            game.flash(path[:-1], (255, 122, 60) if t['caster'] else (216, 208, 176), '*' if t['caster'] else '-', .2)
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
    if mc.hp <= 0:
        fall(game, mc, mon.the() if mon else 'his wounds')
    elif mc.hp < s['max_hp'] * .25 and not mc.fleeing and random.random() > mc.tpl['courage'] * (.5 + mc.morale / 140):
        mc.fleeing = 14
        mc.flees += 1
        mc.morale -= 6
        game.msg(f'{mc.name} breaks and runs!', 'bad')


def fall(game, mc, cause):
    """Down. In hardcore, dead: his gear lies with his body. In softcore, a temple can raise him."""
    from .entities import Item
    b = mc.body
    m = game.map
    if b is not None and b in m.mons:
        m.mons.remove(b)
    if game.player.hardcore:
        game.msg(f'{mc.name} is dead, slain by {cause}.', 'bad')
        if b is not None:
            body = Item(game.new_id(), 'corpse', 'corpse')
            body.name = f'the body of {mc.name}'
            body.payload = dict(items=[it for it in mc.gear.values() if it], cargo={}, cost={}, gold=0)
            body.x, body.y = b.x, b.y
            m.items.append(body)
        mc.state = 'gone'
        game.merc = None
    else:
        game.msg(f'{mc.name} falls, slain by {cause}. A temple can raise him.', 'bad')
        mc.state = 'fallen'
        mc.hp = 0
    mc.body = None


def on_player_death(game):
    """When you fall, your hireling falls with you."""
    mc = with_you(game)
    if mc:
        b = mc.body
        if b is not None:
            for gm in game.maps.values():
                if b in gm.mons:
                    gm.mons.remove(b)
        mc.body = None
        mc.state = 'fallen'
        mc.hp = 0


def raise_fee(game):
    mc = get(game)
    return game.raise_fee(mc.lvl) // 2 if mc else 0


def raise_up(game):
    mc = get(game)
    if not mc or mc.state != 'fallen':
        return False
    fee = raise_fee(game)
    if game.player.gold < fee:
        return False
    game.player.gold -= fee
    mc.state = 'alive'
    mc.frail = 2 * D.DAY_LEN
    mc.hp = stats(game, mc)['max_hp'] // 2
    mc.fleeing = 0
    sync(game)
    game.msg(f'{mc.name} draws breath again. He will be weak for a day or two.', 'good')
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
    crit = random.random() < .06
    if crit:
        dmg = round(dmg * 1.6)
    wear(game, mc, 'weapon', .15)
    add_threat(mon, 'm', dmg * (1.6 if mc.kind == 'defender' else 1))
    mon.awake = True
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
    """One turn of the hireling."""
    mc = with_you(game)
    if not mc or mc.body is not b:
        if b in game.map.mons:
            game.map.mons.remove(b)
        return
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
                add_threat(o, 'm', amt * .5)
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
                    game.flash(path[:-1], col, '*' if mc.tpl.get('caster') else '-', .15)
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
                add_threat(tgt, 'm', 10)
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
    mc = get(game)
    if not mc or mc.state != 'alive':
        return
    p = game.player
    if p.gold >= mc.wage:
        p.gold -= mc.wage
        mc.paid = game.day
        mc.morale = min(100, mc.morale + 2)
    else:
        mc.morale -= 20
        game.msg(f'You cannot pay {mc.name} his {fmt(mc.wage)}. He says nothing, which is worse.', 'bad')
    food = [it for it in p.inv if it.k == 'food']
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


def leave(game, mc, why):
    b = mc.body
    if b is not None and b in game.map.mons:
        game.map.mons.remove(b)
    mc.state = 'gone'
    game.merc = None
    game.msg(f'{mc.name} has had enough. ' + ('"Find someone else to starve."' if why == 'unpaid' else
                                              '"This is no work for a living man."') + ' He leaves, and takes his gear.', 'bad')


def restock(game):
    """In a town he tops up his own potions, out of his wage."""
    mc = with_you(game)
    if mc:
        mc.potions = max(mc.potions, 2)


# ------------------------------------------------------------------ orders (h)
def menu(game):
    from . import events as EV
    from .money import fmt
    mc = get(game)
    if not mc:
        game.msg('You have no hireling. Sellswords are for hire in the barracks of the cities.', 'info')
        return
    if mc.state == 'fallen':
        game.msg(f'{mc.name} lies dead. A temple can raise him, for {fmt(raise_fee(game))}.', 'info')
        return
    s = stats(game, mc)
    gear = ', '.join(f'{it.name}' + (f' ({it.dur}/{it.mdur})' if getattr(it, 'mdur', 0) else '') for it in mc.gear.values() if it)
    mood = 'content' if mc.morale >= 60 else 'grumbling' if mc.morale >= 35 else 'close to walking out'
    text = (f'{mc.title()}, level {mc.lvl}. Life {max(0, mc.hp)}/{s["max_hp"]}, damage {s["dmg"][0]}-{s["dmg"][1]}, '
            f'armour {s["armour"]}. Wage {fmt(mc.wage)} a day; he is {mood}. Potions: {mc.potions}.\n\nGear: {gear or "none"}.')
    opts = [((('» ' if mc.order == k else '') + w), 'order:' + k) for k, w, _ in ORDERS]
    opts += [('Hand him gear from your pack', 'give'), ('Dismiss him', 'dismiss'), ('Close', 'bye')]
    EV.ask(game, 'merc', mc.name, text, opts)


def r_menu(game, choice, ctx):
    from . import events as EV
    mc = get(game)
    if not mc:
        return
    if choice.startswith('order:'):
        mc.order = choice[6:]
        game.msg(f'{mc.name}: "{ORDER_LINE[mc.order]}"', 'talk')
    elif choice == 'give':
        cands = [it for it in game.backpack() if it.k == 'gear' and D.BASES[it.base]['slot'] in SLOTS and fits(mc, it)]
        if not cands:
            game.msg(f'Nothing in your pack that {mc.name} can use.', 'info')
            return
        EV.ask(game, 'merc_give', mc.name, 'What do you hand him? He gives you back what he had.',
               [(it.display_name(), f'g:{it.id}') for it in cands[:10]] + [('Nothing', 'bye')])
    elif choice == 'dismiss':
        EV.ask(game, 'merc_dismiss', mc.name, f'Let {mc.name} go? He keeps his gear and his last wage.',
               [('Dismiss him', 'yes'), ('No', 'bye')])


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
    mc = get(game)
    if mc and choice == 'yes':
        b = mc.body
        if b is not None and b in game.map.mons:
            game.map.mons.remove(b)
        mc.state = 'gone'
        game.merc = None
        game.msg(f'{mc.name} nods, shoulders his pack and goes.', 'info')


def worn(game):
    mc = get(game)
    if not mc:
        return []
    return [it for it in mc.gear.values() if it and getattr(it, 'mdur', 0) and it.dur < it.mdur]


def register():
    from . import events as EV
    EV.RESOLVERS.update(merc=r_menu, merc_give=r_give, merc_dismiss=r_dismiss, merc_hire=r_hire)


register()
