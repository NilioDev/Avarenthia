"""Beasts and what they give the crafts, Monster Hunter's way (life skills part 2).

Every beast gives parts: fangs, claws, horn, tusks, antlers, feathers, chitin, scales, ivory. A part is the power a
maker chooses for a piece (crafts.make): fangs to hit, claws for damage, horn and tusks for armour, antlers for
stamina, feathers make it lighter, chitin keeps out poison, scales fire or cold, ivory gives life. The same part from
a stronger beast gives more (wolf fangs +5, winter wolf +10, sabretooth +15): better gear means hunting stronger
beasts. A part item is Item('part', '<part>:<beast>').

A named beast gives one or two parts of its own (Item('npart', trait)) that carry one of its traits: the only parts
with a power of found gear, so a piece made of them is a rare of the crafts ("Old Greyback's Hide Armor"). Taking
them off whole needs Skinning 15, 30 or 45 by its rank. A critical blow while a big beast is below half its life
breaks off a horn or a claw: one more part.

Every named beast but the legends keeps a den near its home, of the land's kind: a hollow tree, a thorn thicket, a
cave, a mud wallow, a ledge, a burrow. It shows on the world map only once you have found it; beaten, the beast
flees there. When it dies the den is gone with it.

Catching one alive (a lord's job): a sleeping draught when it is below a quarter of its life, then walk into it with
a rope. If it wakes first it is furious. Men with a cart take it to the lord's yard, where it sits in a cage."""
import random

from . import data as D
from .worldgen import cheb

# part: name, power (stat, per step), where it may go
PART = {
    'fangs': ('Fangs', 'hit', 5, 'hit'), 'claws': ('Claws', 'dmg_flat', 2, 'dmg'), 'horn': ('Horn', 'edef', 12, 'armour'),
    'tusks': ('Tusks', 'edef', 12, 'armour'), 'antlers': ('Antlers', 'stamina', 4, 'any'),
    'feathers': ('Feathers', 'light', 1, 'any'), 'chitin': ('Chitin', 'res_poison', 6, 'armour'),
    'scales': ('Scales', 'res_fire', 6, 'armour'), 'frostscale': ('Frost Scales', 'res_cold', 6, 'armour'),
    'ivory': ('Ivory', 'life', 8, 'armour'),
}
STEP = {'A': .6, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'T': 5}
WORTH = {'A': 2, 'B': 3, 'C': 6, 'D': 10, 'E': 18, 'T': 30}
# the beasts that are not hunted for meat: their tier for the parts
EXTRA_TIER = {'spider': 'A', 'wolf_spider': 'B', 'giant_spider': 'C', 'frost_spider': 'C', 'web_weaver': 'C',
              'brood_spider': 'D', 'broodmother': 'E', 'giant_scorpion': 'C', 'horn_beetle': 'B', 'mantis': 'C',
              'fire_beetle': 'C', 'centipede': 'B', 'frost_drake': 'E', 'swamp_drake': 'E', 'wyvern': 'D',
              'manticore': 'D', 'basilisk': 'D', 'clawbeak': 'C', 'troll': 'C'}
# the big beasts: a critical blow below half their life breaks a part off
BIG = {'brown_bear': 'claws', 'cave_bear': 'claws', 'aurochs': 'horn', 'mammoth': 'tusks', 'rhino': 'horn',
       'drake': 'scales', 'frost_drake': 'frostscale', 'swamp_drake': 'scales', 'wyvern': 'scales', 'elk': 'antlers',
       'sabretooth': 'fangs', 'manticore': 'claws', 'basilisk': 'scales', 'troll': 'claws'}
# a named beast's trait in its parts: the powers of found gear (stat, value at notable)
TRAIT_POWER = {
    'Venomous': ('res_poison', 30), 'Frost-touched': ('res_cold', 30), 'Fire-blooded': ('res_fire', 30),
    'Stone Skin': ('dr', 4), 'Thorny': ('thorns', 10), 'Vampiric': ('leech', 4), 'Regenerating': ('regen', 3),
    'Swift': ('dex', 8), 'Blink': ('dex', 6), 'Summoner': ('mpk', 3), 'Splitting': ('lpk', 3), 'Multishot': ('crit', 6),
    'Berserk': ('str', 8), 'Shielded': ('res_all', 8), 'Cursing': ('mana', 20), 'Warcry': ('str', 6),
}
RANK_MULT = {'notable': 1, 'notorious': 1.3, 'legendary': 1.7}
SKIN_NEED = {'notable': 15, 'notorious': 30, 'legendary': 45}
WORD = {'beast': ['hide', 'horn', 'claw', 'fang', 'pelt'], 'crawler': ['chitin', 'venom gland', 'mandible']}


# ------------------------------------------------------------------ ordinary parts
def split(t):
    part, _, src = t.partition(':')
    return part, src or None


def tier(t):
    from .hunting import GAME_TIER
    _part, src = split(t)
    return GAME_TIER.get(src) or EXTRA_TIER.get(src) or 'A'


def part_name(t):
    part, src = split(t)
    nm = PART.get(part, (part.capitalize(),))[0]
    return f"{D.MONSTERS[src]['name']} {nm}" if src in D.MONSTERS else nm


def power(t):
    """(stat, value) the part gives a piece; 'light' makes it lighter."""
    part, _src = split(t)
    _nm, stat, per, _where = PART[part]
    return stat, max(1, round(per * STEP[tier(t)]))


def fits(where, it):
    """May this power go on this piece?"""
    slot = it.slot
    if where == 'any':
        return True
    if where == 'hit':
        return slot in ('weapon', 'helm', 'gloves', 'ring', 'amulet')
    if where == 'dmg':
        return slot in ('weapon', 'gloves')
    return slot != 'weapon'


def make(game, part, src, n=1):
    from .entities import Item
    return Item(game.new_id(), 'part', f'{part}:{src}' if src else part, n)


def part_of(k):
    """The part a beast is known for: what breaks off it, and what a shed one is."""
    from .hunting import SKINS
    if k in BIG:
        return BIG[k]
    parts = [p for p, _c in SKINS.get(k, (0, 0, 0, 0, []))[4] if p in PART]
    if parts:
        return parts[0]
    fam = D.MONSTERS.get(k, {}).get('family', '')
    return 'chitin' if fam in ('spider', 'insect', 'crawler', 'ant', 'worm') else None


def on_kill(game, mon):
    """Spiders and beetles leave chitin."""
    fam = mon.tpl.get('family', mon.k)
    if fam in ('spider', 'insect', 'crawler', 'ant') and not getattr(mon, 'named', None) and random.random() < .3:
        game.spill(game.map, mon.x, mon.y, make(game, 'chitin', mon.k))


def on_blow(game, mon, crit):
    """A critical blow while a big beast is below half its life breaks off a horn or a claw."""
    if not crit or mon not in game.map.mons or getattr(mon, 'broken_part', False):
        return
    from .named import get, kind_of
    n = get(game, getattr(mon, 'named', None))
    if mon.k not in BIG and not (n and kind_of(n.k) in ('beast', 'crawler')):
        return
    if mon.hp > mon.maxhp / 2:
        return
    part = part_of(mon.k)
    if not part:
        return
    mon.broken_part = True
    game.spill(game.map, mon.x, mon.y, make(game, part, mon.k))
    game.msg(f'Your blow breaks off {"a horn" if part in ("horn", "antlers", "tusks") else "a piece"} of {mon.the()}! '
             f'It lies on the ground: {part_name(f"{part}:{mon.k}").lower()}.', 'gold')


# ------------------------------------------------------------------ a named beast's own parts
def named_parts(game, mon, n):
    """What comes off a dead named beast besides its trophy: one or two parts that carry its traits."""
    from .named import kind_of, poss
    from . import lifeskills as LS
    from .entities import Item
    from . import hunting as HT
    kk = kind_of(n.k)
    if kk not in ('beast', 'crawler'):
        return
    traits = [t for t in n.traits if t in TRAIT_POWER] or ['Stone Skin']
    count = 2 if n.rank == 'legendary' or (n.rank == 'notorious' and random.random() < .5) else 1
    r = LS.rank(game, 'skinning')
    need = SKIN_NEED[n.rank]
    if not HT.has_knife(game) or r < need:
        part = part_of(n.k)
        if part:
            game.spill(game.map, mon.x, mon.y, make(game, part, n.k))
        game.msg(f'You hack at {poss(n.name)} hide, but ' + ('without a knife' if not HT.has_knife(game) else
                 f'your skinning is not up to it (Skinning {need})') + ': what you get off it is torn. Only a common part '
                 'is worth keeping.', 'info')
        return
    for t in random.sample(traits, min(count, len(traits))):
        it = Item(game.new_id(), 'npart', t)
        it.beast, it.nid, it.rank, it.src = n.name, n.id, n.rank, n.k
        it.word = random.choice(WORD[kk])
        game.spill(game.map, mon.x, mon.y, it)
        game.msg(f'You take {poss(n.name)} {it.word} off whole. Whatever is made of it will carry its {t.lower()} nature.',
                 'unique')
    LS.gain(game, 'skinning', 6 + SKIN_NEED[n.rank] / 5, at=need, what=f'named:{n.id}')


def npower(it):
    stat, v = TRAIT_POWER[it.t]
    return stat, max(1, round(v * RANK_MULT.get(getattr(it, 'rank', 'notable'), 1)))


def apply(it, part):
    """Give a made piece the power of a part (an ordinary part's key, or a named part item)."""
    if hasattr(part, 'k') and part.k == 'npart':
        stat, v = npower(part)
        it.aff.append([stat, v])
        from .named import poss
        it.named_part = part.beast
        return
    stat, v = power(part)
    if stat == 'light':
        if getattr(it, 'rstr', 0):
            it.rstr = max(0, round(it.rstr * (1 - .12 * STEP[tier(part)])))
        it.light = getattr(it, 'light', 0) + 1
        return
    for a in it.aff:
        if a[0] == stat:
            a[1] += v
            return
    it.aff.append([stat, v])


def choices(game, it):
    """The parts in your pack that may go on this piece: [(label, key, item or None)]."""
    from .itemdata import AFFTXT
    out = []
    seen = set()
    for x in game.player.inv:
        if x.k == 'part' and x.t not in seen and split(x.t)[0] in PART:
            seen.add(x.t)
            stat, v = power(x.t)
            where = PART[split(x.t)[0]][3]
            if not fits(where, it):
                continue
            what = 'lighter' if stat == 'light' else AFFTXT.get(stat, stat + ' {}').format(v)
            out.append((f'{part_name(x.t)}: {what}', x.t, None))
        elif x.k == 'npart':
            stat, v = npower(x)
            out.append((f'{display(game, x)}: {AFFTXT.get(stat, stat + " {}").format(v)}', f'n{x.id}', x))
    return out


def take(game, key):
    """Take one part out of your pack by its choice key; returns what apply() wants."""
    p = game.player
    if key.startswith('n') and key[1:].isdigit():
        it = next((x for x in p.inv if x.k == 'npart' and x.id == int(key[1:])), None)
        if it:
            p.inv.remove(it)
        return it
    it = next((x for x in p.inv if x.k == 'part' and x.t == key), None)
    if it:
        game.remove_one(it)
        return key
    return None


# ------------------------------------------------------------------ the items
def display(game, it):
    if it.k == 'npart':
        from .named import poss
        return f"{poss(it.beast)} {it.word}"
    return (f'{it.n}x ' if it.n > 1 else '') + part_name(it.t)


def lines(game, it):
    from .itemdata import AFFTXT
    if it.k == 'npart':
        stat, v = npower(it)
        return [f'From a {it.rank} named beast. A piece made of it bears its name and carries its {it.t.lower()} nature: '
                + AFFTXT.get(stat, stat + ' {}').format(v) + '. Choose it at a workbench or an anvil when you make something.']
    part, _src = split(it.t)
    if part not in PART:
        return ['Traders buy it.']
    stat, v = power(it.t)
    what = 'makes a piece lighter' if stat == 'light' else AFFTXT.get(stat, stat + ' {}').format(v)
    return [f'Tier {tier(it.t)}. The power a maker gives a piece: {what}. Choose it when you make something, or sell it.']


def value(game, it):
    if it.k == 'npart':
        return {'notable': 40, 'notorious': 70, 'legendary': 120}.get(it.rank, 40)
    return WORTH[tier(it.t)] + (25 if split(it.t)[0] == 'ivory' else 0)


def glyph(it):
    return '\''


def color(it):
    return (236, 190, 110) if it.k == 'npart' else (226, 214, 180)


def use(game, it):
    game.msg(f'{display(game, it)}: ' + lines(game, it)[0], 'info')
    return 0


# ------------------------------------------------------------------ dens
DEN = {  # kind: name, ground, cover, look
    'hollow': ('Hollow Tree', D.GRASS, D.TREE, 'a hollow tree, its roots gnawed white'),
    'thicket': ('Thorn Thicket', D.GRASS, D.THORNS, 'a thicket of thorns with a beaten way in'),
    'cave': ('Den Cave', D.BAREROCK, D.ROCK, 'a low cave mouth that stinks of beast'),
    'wallow': ('Mud Wallow', D.GRASS, D.SWAMP, 'a wallow of black mud, churned by something heavy'),
    'ledge': ('High Ledge', D.SNOW, D.ROCK, 'a ledge high on the rock, white with droppings'),
    'burrow': ('Burrow', D.SAND, D.ROCK, 'a burrow under a rock, the sand dragged out in a fan'),
    'web': ('Webbed Hollow', D.GRASS, D.TREE, 'a hollow strung with webs, thick as sailcloth'),
}
LOOK = {'den': ('δ', (196, 120, 90))}


def den_kind(game, n, x, y):
    from . import cooking as CK
    from . import seasons as SE
    from .named import kind_of
    om = game.maps['over']
    lands = set(CK.lands_of(SE.biome(om, y * om.w + x)))
    if kind_of(n.k) == 'crawler':
        return 'web'
    if lands & {'peak', 'alpine'}:
        return 'ledge'
    if lands & {'mountain', 'karst', 'canyon', 'hills'}:
        return 'cave'
    if lands & {'marsh', 'mangrove'}:
        return 'wallow'
    if 'desert' in lands:
        return 'burrow'
    if 'forest' in lands:
        return 'hollow'
    return 'thicket'


def make_den(game, n):
    """A den near the beast's home, hidden until you find it."""
    from .named import kind_of, poss
    from .sites import Site, site_at
    if n.rank == 'legendary' or n.did is not None or kind_of(n.k) not in ('beast', 'crawler'):
        return None
    w = game.world
    om = game.maps['over']
    hx, hy = n.home
    spot = None
    for _ in range(80):
        x, y = hx + random.randint(-3, 3), hy + random.randint(-3, 3)
        if om.inb(x, y) and D.TILES[om.tile(x, y)].walk and not site_at(w, x, y) and \
                om.tile(x, y) not in (D.ROAD, D.TOWN, D.CITY, D.ENTR, D.CASTLE, D.FORT) and \
                not any(cheb(x, y, s.x, s.y) < 4 for s in w.settlements) and \
                not any(q.x == x and q.y == y for q in w.pois):
            spot = (x, y)
            break
    if not spot:
        return None
    kind = den_kind(game, n, *spot)
    site = Site(len(w.sites), 'den', spot[0], spot[1], f'{poss(n.name)} {DEN[kind][0]}')
    site.faction = w.region_at(*spot).faction
    site.den, site.nid = kind, n.id
    site.hidden, site.found = True, False
    w.sites.append(site)
    n.den = site.id
    n.home = spot
    return site


def den_of(game, n):
    sid = getattr(n, 'den', None)
    return game.world.sites[sid] if sid is not None else None


def den_gone(game, n):
    """The beast is dead or caught: its den is empty, and nobody finds it any more. A lord who wanted it alive is
    disappointed."""
    mi = catch_job(game, n)
    if mi and not getattr(n, 'caught', False):
        from . import missions as MS
        MS.fail(game, mi, f'{n.Full} is dead. The lord wanted it alive.')
    site = den_of(game, n)
    if site is None:
        return
    site.gone = True
    site.hidden, site.found = True, False
    if game.cur != site.map_key:
        game.maps.pop(site.map_key, None)


def is_den(site):
    return site.kind == 'den'


def on_step(game):
    """On the world map: come within a step of a den and you see it."""
    from . import folk as FK
    p = game.player
    for st in game.world.sites:
        if st.kind == 'den' and FK.unfound(st) and not getattr(st, 'gone', False) and cheb(st.x, st.y, p.x, p.y) <= 1:
            FK.discover(game, st, None)
            game.msg(f'Bones in the grass, a beaten track, the stink of a beast: {DEN[st.den][3]}. '
                     f'You have found {st.name}. It is on your map now.', 'unique')


def reveal(game, n):
    """Hunting 50: the den shows as soon as you find the beast's track."""
    from . import folk as FK
    site = den_of(game, n)
    if site and FK.unfound(site) and not getattr(site, 'gone', False):
        FK.discover(game, site, None)
        game.msg(f'You know where a track like this leads: {site.name}. It is on your map now.', 'gold')


def site_map(game, site):
    from .entities import GameMap
    state = random.getstate()
    random.seed(game.seed * 3307 + site.x * 977 + site.y * 37 + 3)
    try:
        name, ground, cover, _look = DEN[site.den]
        w, h = 44, 26
        m = GameMap(site.map_key, 'town', site.name, w, h, ground)
        m.glows, m.lights, m.signs = [], [], []
        m.radius, m.sid, m.hid = 60, None, None
        m.site = site.id
        m.level = game.world.danger_at(site.x, site.y) + 2
        cy = h // 2
        nx, ny = 33, cy
        for y in range(h):
            for x in range(w):
                d = ((x - nx) / 9) ** 2 + ((y - ny) / 6) ** 2
                if d > 1 and random.random() < (.55 if d > 1.6 else .3):
                    m.set(x, y, cover)
        from .nature import path
        path(m, (0, cy), (nx - 6, cy), D.PATH if site.den != 'ledge' else D.BAREROCK, (cover, ground))
        for y in range(ny - 3, ny + 4):
            for x in range(nx - 5, nx + 6):
                if m.inb(x, y) and ((x - nx) / 5.5) ** 2 + ((y - ny) / 3.5) ** 2 < 1:
                    m.set(x, y, ground)
        for _ in range(10):
            x, y = nx + random.randint(-4, 4), ny + random.randint(-2, 2)
            if m.tile(x, y) == ground:
                m.set(x, y, 169)                        # gnawed bones and the leavings of its prey
        for _ in range(3):
            x, y = nx + random.randint(-5, 5), ny + random.choice((-3, 3))
            if m.inb(x, y):
                m.set(x, y, D.BONES)
        if site.den == 'web':
            for _ in range(14):
                x, y = nx + random.randint(-7, 7), ny + random.randint(-4, 4)
                if m.inb(x, y) and m.tile(x, y) == ground:
                    m.set(x, y, D.WEB)
        m.nook = (nx, ny)
        m.entry = (0, cy)
        for i in range(len(m.seen)):
            m.seen[i] = 1
        if random.random() < .35:                       # now and then a shed scale or a broken claw
            from .named import get
            n = get(game, site.nid)
            part = part_of(n.k) if n else None
            if part:
                it = make(game, part, n.k)
                game.spill(m, nx + random.randint(-3, 3), ny + random.randint(-1, 1), it)
    finally:
        random.setstate(state)
    return m


def home(game, n):
    """Is the beast in its den now? Always when it fled there to lick its wounds; otherwise one day in three."""
    return n.alive and (n.back is not None or (game.day + n.id) % 3 == 0)


def on_enter(game, site, m):
    if not is_den(site):
        return
    from .named import get, apply as named_apply
    from .entities import make_monster
    from .worldgen import free_around
    n = get(game, site.nid)
    if not n or not n.alive or getattr(site, 'gone', False):
        game.msg('The den is empty and cold. Whatever lived here is gone.', 'info')
        return
    if any(getattr(o, 'named', None) == n.id for o in m.mons):
        return
    if not home(game, n):
        game.msg(f'{DEN[site.den][3].capitalize()}. The smell is fresh, but it is out roaming.', 'info')
        return
    nx, ny = m.nook
    boss = make_monster(game, n.k, nx, ny, n.lvl)
    named_apply(game, boss, n)
    if n.back is not None:
        boss.hp = max(1, round(boss.maxhp * .6))        # still licking its wounds
    pid = game.new_id()
    boss.pack = pid
    m.mons.append(boss)
    for (x, y), k in zip(free_around(game, m, nx, ny, 2), n.following[:2]):
        o = make_monster(game, k, x, y, max(1, n.lvl - 1))
        o.pack = pid
        m.mons.append(o)
    game.named_fight = n.id
    game.msg(f'{DEN[site.den][3].capitalize()}. Something big shifts in the dark of it. {n.Full} is at home.', 'bad')


# ------------------------------------------------------------------ catching one alive
def has_rope(game):
    return any(i.k == 'tool' and i.t == 'rope' for i in game.player.inv)


def catch_job(game, n):
    from . import missions as MS
    return next((m for m in MS.active(game) if m.kind == 'realm' and m.data.get('task') == 'catch'
                 and m.data.get('nid') == n.id and m.state == 'active'), None)


def try_bind(game, mon):
    """Walking into a sleeping named beast below a quarter of its life, with a rope: you bind it. True if done."""
    from .named import get
    n = get(game, getattr(mon, 'named', None))
    if not n or not catch_job(game, n):
        return False
    if not getattr(mon, 'hold', 0) or not getattr(mon, 'slept', False):
        return False
    if mon.hp > mon.maxhp / 4:
        game.msg(f'{n.Full} sleeps, but a rope will not hold it yet. Wear it down first, below a quarter of its life.', 'info')
        return False
    if not has_rope(game):
        game.msg(f'{n.Full} sleeps, and you have no rope to bind it.', 'bad')
        return False
    p = game.player
    rope = next(i for i in p.inv if i.k == 'tool' and i.t == 'rope')
    game.remove_one(rope)
    m = game.map
    m.mons.remove(mon)
    n.alive = False
    n.caught = True
    den_gone(game, n)
    mi = catch_job(game, n)
    mi.state = 'turnin'
    seat = mi.data.get('seat')
    if seat and seat[0] not in ('hold', 's'):
        add_cage(game, seat[1], n)
    from . import lifeskills as LS
    LS.gain(game, 'hunting', 8, what=f'caught:{n.id}')
    game.msg(f'You bind {n.full} fast while it sleeps. Men with a cart will come for it; the lord will want to hear.',
             'gold')
    return True


def wake(game, mon):
    """It slept off the draught before you bound it: now it is furious."""
    if getattr(mon, 'slept', False) and not getattr(mon, 'hold', 0) and not getattr(mon, 'furious', False):
        mon.slept = False
        mon.furious = True
        mon.dmg = tuple(round(v * 1.3) + 1 for v in mon.dmg)
        from .behave import The
        game.msg(f'{The(mon)} wakes from the draught, and it is furious!', 'bad')


def cages(game):
    return game.world.__dict__.setdefault('cages', {})


def add_cage(game, seat, n):
    """The lord keeps the beast in a cage in his yard: one cage for each beast you brought."""
    cages(game).setdefault(seat, []).append(f'{n.full}, the {D.MONSTERS[n.k]["name"].lower()} you caught')


def sync_cages(game, site, m):
    """Put the cages in a seat's yard (outside, near the gate)."""
    want = cages(game).get(site.id, [])
    have = getattr(m, 'cages', {})
    if len(have) >= len(want):
        return
    m.cages = have
    ex, ey = m.entry
    spots = [(x, y) for y in range(max(1, ey - 8), min(m.h - 1, ey + 9)) for x in range(ex + 3, min(m.w - 1, ex + 20))
             if m.tile(x, y) in (D.GRASS, D.PATH, D.FLOOR, D.EARTH) and (x, y) not in have and not m.mon_at(x, y)
             and abs(y - ey) >= 2]
    random.shuffle(spots)
    for text in want[len(have):]:
        if not spots:
            break
        x, y = spots.pop()
        m.set(x, y, D.CAGE)
        have[(x, y)] = text


def at_cage(game, m, x, y):
    text = getattr(m, 'cages', {}).get((x, y))
    if text:
        game.msg(f'In the cage: {text}. It watches you through the bars.', 'info')
        return True
    return False

