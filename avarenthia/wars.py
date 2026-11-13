"""Wars that feel like wars (round 66): several hosts on each side, a front, raids and sieges, the seasons, levies
that go home, ransom, the peace by the war's score, magic, the peoples' ways, and the field battle.

The sums stay small: a war is a few signs on the map (at most MAX_SIGNS), each with a strength in hundreds, and the
player is one adventurer who sees what happens and can touch some of it.
- The forces: each side the king's host (a marshal, a priest, in a big one a battle mage, sometimes a holy banner)
  and a baron's host in his house's colours; the defender marches out to meet the attacker. Small war parties go
  between them (raiders that burn border villages, foragers, messengers, scouts), kind 'warparty'.
- Where two hosts of one war meet, they fight: the first time in a war a field battle (one day's warning, a place
  you can stand in, see field_*), later a skirmish rolled quietly.
- A host at the end of its march besieges the seat (camps.siege): the seat's stores run down, the engines make a
  breach, the garrison sallies; then the storm (realms.arrive, helped by the breach or the hunger). You can smuggle
  food in, open the postern, or slip in.
- Hosts march from spring to the harvest; in winter they go home. A baron's levies go home after LEVY_DAYS unless
  the king pays sellswords; a host that sits too long sickens; one worn down to nothing becomes deserters (robbers).
- Taken seats, won battles and captured lords make the score; enough of it forces the peace (realms.end_war).
- Captured lords are held for ransom: by a side (war['captives']) or by you (p.war['captives']).
The war's state lives on the world (R.wars); what you did in it on the player (p.war)."""
import random

from . import data as D
from .worldgen import cheb

MAX_SIGNS = 8
LEVY_DAYS = 40
PEACE_SCORE = 6
FIELD_W, FIELD_H = 90, 44
WINTER = ('winter',)
# how each people wars: speed (turns a step), whether it raids, besieges, how far it marches, its siege engines
WAYS = {
    'human': dict(speed=12, raid=True, siege=True, far=999, engines=1),
    'dwarf': dict(speed=16, raid=False, siege=True, far=45, engines=2),
    'elf': dict(speed=9, raid=False, siege=False, far=25, engines=0),
}
SCHOOLS = {'human': ('fire', 'frost', 'storm'), 'dwarf': ('runes',), 'elf': ('nature',), 'orc': ('curse',)}
# who works the art for each people: a court mage, a rune-smith, a druid of the Circle, a shaman
MAGE_NAME = {'fire': 'Their battle mage', 'frost': 'Their battle mage', 'storm': 'Their battle mage',
             'necromancy': 'Their necromancer', 'runes': 'Their rune-smith', 'nature': 'Their druid',
             'curse': 'Their shaman'}
PARTY = {
    'raid': dict(ch='k', name='raiders of {k}', keys=['soldier', 'soldier', 'crossbow'], speed=10),
    'forage': dict(ch='k', name='foragers of {k}', keys=['soldier', 'soldier'], speed=12),
    'message': dict(ch='m', name='a messenger of {k}', keys=['soldier'], speed=7),
    'scout': dict(ch='s', name='scouts of {k}', keys=['crossbow', 'soldier'], speed=8),
}
RANSOM = {'king': 600, 'baron': 200, 'lord': 90, 'heir': 120}        # in silver


# ------------------------------------------------------------------ state
def R(game):
    return game.world.realm


def wid(game, war):
    if 'id' not in war:
        war['id'] = game.new_id()
    for k, v in (('hosts', []), ('parties', []), ('captives', []), ('field', None), ('raids', [0, 0]),
                 ('front', []), ('dead', [])):
        war.setdefault(k, v)
    return war['id']


def war_of(game, i):
    return next((w_ for w_ in R(game).wars if w_.get('id') == i), None)


def mine(game):
    """What the player did in the wars: captives held, battles stood in, a line left."""
    p = game.player
    if not isinstance(getattr(p, 'war', None), dict):
        p.war = {}
    for k, v in (('captives', []), ('fields', []), ('fled', []), ('smuggled', 0)):
        p.war.setdefault(k, v)
    return p.war


def people_of(game, kg):
    try:
        return R(game).houses[R(game).lord(kg.king).house].people
    except Exception:
        return 'human'


def way(game, kg):
    return WAYS.get(people_of(game, kg), WAYS['human'])


def winter(game):
    from .calendar import season
    return season(game.day) in WINTER


def forces(game, war):
    """The war's signs on the map: its hosts and parties still walking."""
    ids = set(war.get('hosts', [])) | set(war.get('parties', []))
    return [wd for wd in game.world.wanderers if wd.id in ids]


def hosts(game, war, side=None):
    ids = set(war.get('hosts', [])) | ({war['host']} if war.get('host') is not None else set())
    return [wd for wd in game.world.wanderers if wd.id in ids and (side is None or wd.kingdom == side)]


def side_of(war, kid):
    return 1 if war['a'] == kid else -1


def might(wd):
    """A host's weight in a fight: its men, and a mage counts for three hundred."""
    return wd.strength + (3 if getattr(wd, 'mage', None) else 0) + (1 if getattr(wd, 'banner', None) == 'holy' else 0)


# ------------------------------------------------------------------ the front
def front(game, war):
    """The baronies on the border between the two realms."""
    Rl = R(game)
    out = set()
    for rid, b in Rl.baronies.items():
        if b.kingdom not in (war['a'], war['b']):
            continue
        other = war['b'] if b.kingdom == war['a'] else war['a']
        if any(o in Rl.baronies and Rl.baronies[o].kingdom == other for o in Rl.adj.get(rid, ())):
            out.add(rid)
    war['front'] = sorted(out)
    return out


def on_front(game, x, y):
    """The war whose front this world cell lies in, or None."""
    w = game.world
    try:
        rid = w.region_of[y * game.maps['over'].w + x]
    except (AttributeError, IndexError):
        return None
    for war in R(game).wars:
        if rid in war.get('front', ()):
            return war
    return None


# ------------------------------------------------------------------ raising the forces
def raise_host(game, war, kg, foe, role='king', lo=None, target_r=None, to=None, people=None):
    """A host sets out: the king's or a baron's, to a seat of the enemy (target_r) or to a cell (to: defending)."""
    from .wanderers import Wanderer
    from .world import dijkstra_path
    from . import realms as RL
    Rl = R(game)
    w = game.world
    wid(game, war)
    src = None
    if role == 'baron' and lo is not None:
        b = next((b for b in Rl.baronies.values() if b.lord == lo.id), None)
        src = RL.seat_pos(w, b.seat) if b and b.seat else None
    if src is None:
        src = RL.seat_pos(w, kg.seat) if kg.seat else None
    if src is None:
        return None
    if target_r is not None:
        tb = Rl.baronies.get(target_r)
        dst = RL.seat_pos(w, tb.seat) if tb and tb.seat else None
    else:
        dst = to
    if dst is None or src == tuple(dst):
        return None
    om = game.maps['over']
    path = dijkstra_path(om, src, tuple(dst), lambda t: D.TILES[t].cost if D.TILES[t].walk else None)
    if not path or len(path) < 3:
        return None
    pp = people or people_of(game, kg)
    wy = WAYS.get(pp, WAYS['human'])
    if len(path) > wy['far'] and target_r is not None:
        return None                                   # dwarves and elves do not march far from home
    wd = Wanderer(game.new_id(), 'host', src[0], src[1])
    wd.kingdom, wd.foe, wd.target_r = kg.id, foe.id, target_r
    wd.path = path[:-1] if target_r is not None else path
    wd.speed = wy['speed']
    wd.role, wd.war, wd.out_day, wd.people = role, war['id'], game.day, pp
    house = Rl.houses[lo.house] if lo is not None else Rl.houses[Rl.lord(kg.king).house]
    wealth = house.wealth
    if role == 'king':
        wd.strength = random.randint(8, 14) + wealth * 2
        wd.name = f'The host of {kg.short}'
        wd.fg = kg.fg
        wd.lord = kg.king
        wd.priest = pp == 'human'
        wd.mage = random.choice(SCHOOLS.get(pp, ())) if SCHOOLS.get(pp) and (wd.strength >= 14 or wealth >= 2) else None
        if wd.mage and pp == 'human' and random.random() < .05:
            wd.mage = 'necromancy'                    # forbidden: the Church will answer it
            necromancy(game, kg)
        wd.banner = 'holy' if pp == 'human' and random.random() < .3 else 'plain'
    else:
        wd.strength = random.randint(4, 7) + wealth
        wd.name = f'The men of House {house.name}'
        wd.fg = house.arms[1] if house.arms else kg.fg
        wd.lord = lo.id if lo is not None else kg.king
        wd.priest, wd.mage, wd.banner = False, None, 'plain'
    wd.ch = 'K'
    wd.group = dict(keys=['soldier', 'soldier', 'crossbow', 'knight'], lvl=max(4, w.danger_at(*dst) + 2), elite=0,
                    leader=None, faction='crown')
    wd.hostile = RL.hostile_host(game, wd)
    w.wanderers.append(wd)
    war['hosts'].append(wd.id)
    return wd


def raise_party(game, war, kg, foe, kind):
    """A small war party: raiders for a border village, foragers, a messenger to the king's host, scouts."""
    from .wanderers import Wanderer
    from .world import dijkstra_path
    from . import realms as RL
    Rl = R(game)
    w = game.world
    fr = front(game, war)
    theirs = [s for s in w.settlements if s.region in fr and s.region in Rl.baronies
              and Rl.baronies[s.region].kingdom == foe.id and s.kind in ('hamlet', 'village') and s.id != 0]
    ours = [b for b in Rl.baronies.values() if b.kingdom == kg.id and b.rid in fr and b.seat]
    if not ours:
        return None
    sx, sy = RL.seat_pos(w, random.choice(ours).seat)
    if kind in ('raid', 'forage'):
        if not theirs:
            return None
        s = min(random.sample(theirs, min(3, len(theirs))), key=lambda q: cheb(q.x, q.y, sx, sy))
        dst = (s.x, s.y)
    elif kind == 'message':
        own = [h for h in hosts(game, war, kg.id)]
        if not own:
            return None
        h = random.choice(own)
        dst = (h.x, h.y)
    else:
        foes = hosts(game, war, foe.id)
        if not foes:
            return None
        h = random.choice(foes)
        dst = (h.x + random.randint(-3, 3), h.y + random.randint(-3, 3))
    om = game.maps['over']
    if not om.inb(*dst) or not D.TILES[om.tile(*dst)].walk:
        return None
    path = dijkstra_path(om, (sx, sy), dst, lambda t: D.TILES[t].cost if D.TILES[t].walk else None)
    if not path or len(path) < 3 or len(path) > 90:
        return None
    t = PARTY[kind]
    wd = Wanderer(game.new_id(), 'warparty', sx, sy)
    wd.ch, wd.fg = t['ch'], kg.fg
    wd.name = t['name'].format(k=kg.short)
    wd.name = wd.name[0].upper() + wd.name[1:]
    wd.path = path[:-1]
    wd.speed = t['speed']
    wd.role, wd.kingdom, wd.foe, wd.war = kind, kg.id, foe.id, war['id']
    wd.target = dst
    wd.strength = 1
    wd.group = dict(keys=list(t['keys']), lvl=max(3, w.danger_at(*dst) + 1), elite=0, leader=None, faction='crown')
    wd.hostile = RL.hostile_host(game, wd)
    w.wanderers.append(wd)
    war['parties'].append(wd.id)
    return wd


def border_baron(game, kg, foe, war):
    Rl = R(game)
    fr = front(game, war)
    cands = [Rl.lord(b.lord) for b in Rl.baronies.values() if b.kingdom == kg.id and b.rid in fr and b.lord is not None
             and b.seat and b.seat != kg.seat]
    cands = [lo for lo in cands if lo and lo.alive]
    return random.choice(cands) if cands else None


def target_for(game, kg, foe, war):
    Rl = R(game)
    fr = front(game, war)
    theirs = [rid for rid in fr if Rl.baronies[rid].kingdom == foe.id and Rl.baronies[rid].seat]
    if not theirs:
        theirs = [rid for rid, b in Rl.baronies.items() if b.kingdom == foe.id and b.seat]
    return random.choice(theirs) if theirs else None


def muster(game, war, att, dfd):
    """A season's forces: the attacker's king's host and a baron's host for an enemy seat, the defender's host
    marching out to meet them, and a few war parties; never more than MAX_SIGNS at once."""
    wid(game, war)
    n = len(forces(game, war))
    made = []
    if not hosts(game, war, att.id) and n < MAX_SIGNS:
        tr = target_for(game, att, dfd, war)
        if tr is not None:
            k = raise_host(game, war, att, dfd, 'king', target_r=tr)
            if k:
                made.append(k)
                war['host'] = k.id                    # the old single host (realms.arrive finds the war by it)
            lo = border_baron(game, att, dfd, war)
            if lo and len(forces(game, war)) < MAX_SIGNS:
                b = raise_host(game, war, att, dfd, 'baron', lo=lo, target_r=tr)
                if b:
                    made.append(b)
    if not hosts(game, war, dfd.id) and hosts(game, war, att.id) and len(forces(game, war)) < MAX_SIGNS:
        a = hosts(game, war, att.id)[0]
        mid = a.path[len(a.path) * 2 // 3] if len(a.path) > 3 else (a.x, a.y)
        d = raise_host(game, war, dfd, att, 'king', to=mid)
        if d:
            d.defending = True
            made.append(d)
    for kg, foe in ((att, dfd), (dfd, att)):
        if not way(game, kg)['raid']:
            continue
        for kind in random.sample(list(PARTY), 2):
            if len(forces(game, war)) >= MAX_SIGNS:
                break
            if random.random() < .5:
                p_ = raise_party(game, war, kg, foe, kind)
                if p_:
                    made.append(p_)
    if made:
        from . import realms as RL
        k = made[0]
        RL.news(game, f'{k.name} marches. The war of {R(game).kingdoms[war["a"]].short} and '
                      f'{R(game).kingdoms[war["b"]].short} comes to the border.', k.x, k.y)
    return made


# ------------------------------------------------------------------ a month of war
def month(game, war):
    """Replaces the old one-host month (realms.war_month): the peace by score, winter, the musters."""
    from . import realms as RL
    Rl = R(game)
    wid(game, war)
    a, b = Rl.kingdoms[war['a']], Rl.kingdoms[war['b']]
    age = game.day - war['since']
    front(game, war)
    if abs(war['score']) >= PEACE_SCORE or age > 360 or \
            (age > 60 and random.random() < .04 + age / 2400 + abs(war['score']) * .05):
        RL.end_war(game, war)
        return
    if winter(game):
        home(game, war)
        return
    att, dfd = (a, b) if random.random() < .5 + war['score'] * .05 else (b, a)
    muster(game, war, att, dfd)
    if age > 90 and random.random() < .25:
        worn(game, war)
    if random.random() < .3:
        sellswords(game, war, random.choice((a, b)))


def home(game, war):
    """Winter: the hosts go home; the war is quiet till spring."""
    from .world import dijkstra_path
    from . import realms as RL
    w = game.world
    sent = 0
    for wd in hosts(game, war):
        if getattr(wd, 'homebound', False):
            continue
        kg = R(game).kingdoms[wd.kingdom]
        pos = RL.seat_pos(w, kg.seat) if kg.seat else None
        if not pos:
            continue
        path = dijkstra_path(game.maps['over'], (wd.x, wd.y), pos, lambda t: D.TILES[t].cost if D.TILES[t].walk else None)
        wd.path, wd.path_i, wd.homebound, wd.target_r = (path or [])[:-1], 0, True, None
        wd.siege_until = None
        sent += 1
    for wd in [x for x in forces(game, war) if x.kind == 'warparty']:
        w.wanderers.remove(wd)
    if sent:
        RL.news(game, f'Winter: the hosts of {R(game).kingdoms[war["a"]].short} and {R(game).kingdoms[war["b"]].short} '
                      f'go home. The war waits for the spring.', *RL.place_of(game, R(game).lord(R(game).kingdoms[war['a']].king)))


def sellswords(game, war, kg):
    """A rich king pays a mercenary company, or dwarves hire out a hammer band."""
    from . import powers as PW
    from . import realms as RL
    Rl = R(game)
    wealth = Rl.houses[Rl.lord(kg.king).house].wealth
    if wealth >= 2 and random.random() < .4 and len(forces(game, war)) < MAX_SIGNS:
        foe = Rl.kingdoms[war['b'] if war['a'] == kg.id else war['a']]
        tr = target_for(game, kg, foe, war)
        if tr is not None:
            h = raise_host(game, war, kg, foe, 'baron', lo=Rl.lord(kg.king), target_r=tr, people='dwarf')
            if h:
                h.name = f'A dwarf hammer band in the pay of {kg.short}'
                h.fg = (200, 170, 120)
                h.people = 'dwarf'
                RL.news(game, f'{kg.short} has hired a dwarf hammer band. Their shields shine on the road to the border.',
                        h.x, h.y)
                return
    war['paid'] = war.get('paid', []) + [kg.id]
    PW.company(game, dict(a=kg.id, b=war['b'] if war['a'] == kg.id else war['a']))


def necromancy(game, kg):
    """A king who lets a necromancer march with his host: the Church's order rides out against him."""
    from . import realms as RL
    kg.burden += 1
    RL.news(game, f'Whispers from the camp of {kg.short}: a necromancer marches with the host. The Church\'s order '
                  f'calls it an abomination and sends its knights.', *RL.place_of(game, R(game).lord(kg.king)))
    for war in R(game).wars:
        if kg.id in (war['a'], war['b']):
            war['score'] -= side_of(war, kg.id)


def worn(game, war):
    """The Gorvash smell weakness on a worn border."""
    from . import powers as PW
    w = game.world
    tr = w.powers.get('tribes') or []
    if w.powers.get('gorvash') or not tr:
        return
    t = max(tr, key=lambda q: q['strength'])
    t['strength'] += 3
    if t['strength'] >= 10 and 'horde' in D.FACTIONS:
        PW.gorvash(game, t)


# ------------------------------------------------------------------ every day
def daily(game):
    """Levies going home, sickness in the siege lines, the sieges' stores and breaches, the risen dead."""
    from . import realms as RL
    Rl = getattr(game.world, 'realm', None)
    if Rl is None:
        return
    w = game.world
    for war in list(Rl.wars):
        wid(game, war)
        war['hosts'] = [i for i in war['hosts'] if any(x.id == i for x in w.wanderers)]
        war['parties'] = [i for i in war['parties'] if any(x.id == i for x in w.wanderers)]
        for wd in hosts(game, war):
            out = game.day - getattr(wd, 'out_day', game.day)
            paid = wd.kingdom in war.get('paid', [])
            if out > LEVY_DAYS and wd.role == 'baron' and not paid and (out - LEVY_DAYS) % 5 == 0:
                wd.strength -= 1                      # the levies go home to the harvest
            if getattr(wd, 'siege_until', None):
                siege_day(game, war, wd)
            if getattr(wd, 'people', None) == 'dwarf' and out > 30 and not getattr(wd, 'homebound', False):
                retreat(game, wd)                     # the debt paid in full, the dwarves go home
                RL.news(game, f'{wd.name} has done what it was paid for, and goes home to the hills.', wd.x, wd.y)
            ambush(game, wd)
            if wd.strength <= 2:
                melt(game, war, wd)
    risen(game)


def ambush(game, wd):
    """The elves defend their closed wood: a host that marches under its trees is shot at from the leaves."""
    from . import realms as RL
    w = game.world
    fo = (w.powers or {}).get('forest') if isinstance(getattr(w, 'powers', None), dict) else None
    if not fo or not fo.get('closed') or getattr(wd, 'ambushed', False):
        return
    om = game.maps['over']
    i = wd.y * om.w + wd.x
    try:
        r = w.regions[w.region_of[i]]
    except (AttributeError, IndexError):
        return
    if r.faction != 'circle' or om.t[i] not in (D.FOREST, D.TREE):
        return
    wd.ambushed = True
    wd.strength = max(1, wd.strength - 2)
    RL.news(game, f'Arrows out of the leaves: the elves fell on {wd.name.replace("The ", "the ")} in their wood and were '
                  f'gone before a sword was drawn.', wd.x, wd.y, 'Peoples')


def siege_day(game, war, wd):
    """A day of a siege: the stores run down, the engines work, the garrison may sally; sickness in the lines."""
    from . import realms as RL
    Rl = R(game)
    wd.stores = getattr(wd, 'stores', None)
    if wd.stores is None:
        tb = Rl.baronies.get(wd.target_r)
        lo = Rl.lord(tb.lord) if tb else None
        wealth = Rl.houses[lo.house].wealth if lo else 1
        wd.stores = random.randint(6, 10) + wealth * 4
        wd.breach = 0
        wd.siege_day0 = game.day
    wd.stores -= 1
    wd.breach = getattr(wd, 'breach', 0) + WAYS.get(getattr(wd, 'people', 'human'), WAYS['human'])['engines']
    if (game.day - getattr(wd, 'siege_day0', game.day)) % (8 if getattr(wd, 'priest', False) else 4) == 3:
        wd.strength -= 1                              # sickness in the lines
    if random.random() < .08:
        wd.strength -= 1
        tb = Rl.baronies.get(wd.target_r)
        if tb:
            RL.news(game, f'The garrison of the {tb.name} sallied by night and burned an engine.', wd.x, wd.y)
        wd.breach = max(0, wd.breach - 2)
    if wd.breach >= 12 or wd.stores <= 0:
        wd.storm = 'breach' if wd.breach >= 12 else 'hunger'
        wd.siege_until = game.day                     # the storm, on its next step


def storm_bonus(wd):
    """How the siege ended weighs in the storm: a breach, or a starved garrison."""
    return {'breach': 1.3, 'hunger': 1.5}.get(getattr(wd, 'storm', None), 1.0)


def melt(game, war, wd):
    """A host worn to nothing breaks up; its deserters take to the roads as robbers."""
    from . import realms as RL
    from .wanderers import make_group
    w = game.world
    if wd in w.wanderers:
        w.wanderers.remove(wd)
    keys = ['bandit', 'bandit', 'brigand'][:random.randint(2, 3)]
    g = make_group(game, 'bandits', wd.x, wd.y, max(3, w.danger_at(wd.x, wd.y) + 1), keys)
    g.name = f'Deserters of {R(game).kingdoms[wd.kingdom].short}'
    w.wanderers.append(g)
    RL.news(game, f'{wd.name} has melted away: the levies gone home, the rest deserters on the roads.', wd.x, wd.y)


def risen(game):
    """On a battlefield in the Lich's land the dead rise by night."""
    from . import evils as EVL
    from .wanderers import make_group
    w = game.world
    keep = []
    for f in getattr(w, 'war_dead', []):
        if game.day - f['day'] > 20:
            continue
        keep.append(f)
        e = EVL.taint_at(game, f['x'], f['y'])
        if e is None or e.k != 'lich' or e.defeated:
            continue
        if sum(1 for x in w.wanderers if getattr(x, 'risen', False)) < 3 and random.random() < .3:
            g = make_group(game, 'monsters', f['x'], f['y'], max(4, w.danger_at(f['x'], f['y']) + 2),
                           ['skeleton', 'zombie', 'skeleton'])
            g.risen = True
            g.name = 'The dead of the battlefield'
            w.wanderers.append(g)
    w.war_dead = keep


# ------------------------------------------------------------------ when forces meet
def tick(game):
    """From the wanderers' tick: hosts of one war that meet fight; parties that arrive do their work."""
    Rl = getattr(game.world, 'realm', None)
    if Rl is None:
        return
    for war in list(Rl.wars):
        if 'id' not in war:
            continue
        hs = hosts(game, war)
        for a in hs:
            for b in hs:
                if a.kingdom == war['a'] and b.kingdom == war['b'] and cheb(a.x, a.y, b.x, b.y) <= 1 \
                        and a in game.world.wanderers and b in game.world.wanderers:
                    meet(game, war, a, b)


def meet(game, war, a, b):
    """Two hosts meet: the war's one field battle (a day's warning, a place to stand), or a skirmish."""
    from . import realms as RL
    fd = war.get('field')
    if fd is None:
        x, y = (a.x + b.x) // 2, (a.y + b.y) // 2
        om = game.maps['over']
        if not D.TILES[om.tile(x, y)].walk:
            x, y = a.x, a.y
        war['field'] = dict(state='pending', day=game.day, x=x, y=y, a=a.id, b=b.id)
        for h in (a, b):
            h.halt = game.day + 1
        RL.news(game, f'{a.name} and {b.name} face each other across a field: battle at first light.', x, y,
                title=f'A battle on the border of {R(game).kingdoms[war["a"]].short}')
        call_to_field(game, war)
        return
    if fd.get('state') == 'pending':
        return
    skirmish(game, war, a, b)


def call_to_field(game, war):
    """A knight of either side, or one close by, hears of it: a job to the field."""
    from . import missions as MS
    from . import realmjobs as RJ
    p = game.player
    fd = war['field']
    kn = getattr(p, 'knight', None) or {}
    near = game.cur == 'over' and cheb(p.x, p.y, fd['x'], fd['y']) <= 15
    if kn.get('kid') not in (war['a'], war['b']) and not near:
        return
    if any(x.kind == 'realm' and x.data.get('task') == 'field' for x in MS.active(game)):
        return
    Rl = R(game)
    kid = kn.get('kid') if kn.get('kid') in (war['a'], war['b']) else None
    lo = Rl.lord(Rl.kingdoms[kid].king) if kid is not None else None
    from . import realms as RL
    g = dict(kind='lord', lid=lo.id, house=lo.house, name=RL.style(Rl, lo, False)) if lo else \
        dict(kind='road', name='the news of the road')
    m = RJ.mission(game, g, 'field', 'A battle at first light',
                   'Two hosts face each other across a field. Whoever stands in the line tomorrow will be remembered. '
                   'Be there at first light.', 30, 2, 'crown', spot=[fd['x'], fd['y']], reach=1, where='the field',
                   war=war['id'], kid=kid)
    m.state = 'active'
    game.missions.append(m)
    game.reveal_place(fd['x'], fd['y'])
    game.msg('Word on the road: two hosts face each other across a field, and the battle is at first light. (Journal: Jobs.)', 'gold')


def skirmish(game, war, a, b, bonus=0.0, big=False, you=None):
    """A fight settled by the hosts' strength: the loser loses more, a lord may be taken, the score moves."""
    from . import realms as RL
    from .living import battle
    Rl = R(game)
    w = game.world
    pa = might(a) / max(1, might(a) + might(b)) + bonus
    pa = max(.05, min(.95, pa))
    win, lose = (a, b) if random.random() < pa else (b, a)
    lose.strength = max(0, lose.strength - max(2, round(lose.strength * (.5 if big else .3))))
    win.strength = max(1, win.strength - max(1, round(win.strength * (.2 if big else .1))))
    war['score'] += (2 if big else 1) * side_of(war, win.kingdom)
    x, y = (a.x + b.x) // 2, (a.y + b.y) // 2
    battle(game, x, y, f'the hosts of {Rl.kingdoms[a.kingdom].short} and {Rl.kingdoms[b.kingdom].short}')
    w.war_dead = getattr(w, 'war_dead', []) + [dict(x=x, y=y, day=game.day)]
    taken = None
    if random.random() < (.6 if big else .25):
        taken = capture(game, war, lose.kingdom, win.kingdom)
    text = f'{win.name} beat {lose.name.replace("The ", "the ")} in the field' + \
           (f', and took {taken} for ransom.' if taken else '.')
    if you:
        text += ' ' + you
    RL.news(game, text, x, y)
    if lose.strength <= 2:
        melt(game, war, lose)
    else:
        retreat(game, lose)
    return win


def retreat(game, wd):
    from .world import dijkstra_path
    from . import realms as RL
    kg = R(game).kingdoms[wd.kingdom]
    pos = RL.seat_pos(game.world, kg.seat) if kg.seat else None
    if not pos:
        return
    path = dijkstra_path(game.maps['over'], (wd.x, wd.y), pos, lambda t: D.TILES[t].cost if D.TILES[t].walk else None)
    wd.path, wd.path_i, wd.homebound, wd.target_r = (path or [])[:-1], 0, True, None


def capture(game, war, kid, by):
    """A lord of the losing side taken in the field: held for ransom by the winners."""
    from . import realms as RL
    Rl = R(game)
    kg = Rl.kingdoms[kid]
    cands = [lo for lo in RL.lords_of(Rl, kg) if lo.id != kg.king and lo.id not in war['captives']
             and not getattr(lo, 'held', None)]
    if not cands:
        return None
    lo = random.choice(cands)
    lo.held = by
    war['captives'].append(lo.id)
    war['score'] += side_of(war, by)
    return RL.style(Rl, lo, False)


# ------------------------------------------------------------------ the war parties
def step(game, wd):
    """A war party walks its road; at its end it does its work."""
    from .wanderers import greedy_step, wanderer_at
    p = game.player
    if wd.hostile and game.cur == 'over' and wd.cooldown == 0 and cheb(wd.x, wd.y, p.x, p.y) <= 4 \
            and wd.role in ('raid', 'scout') and game.visible(wd.x, wd.y):
        greedy_step(game, wd, p.x, p.y)
        return
    if wd.path_i < len(wd.path):
        nx, ny = wd.path[wd.path_i]
        if game.cur == 'over' and (nx, ny) == (p.x, p.y):
            return
        if not wanderer_at(game, nx, ny) or random.random() < .5:
            wd.x, wd.y = nx, ny
            wd.path_i += 1
        return
    arrived(game, wd)


def arrived(game, wd):
    from . import realms as RL
    from .living import plundered
    w = game.world
    if wd in w.wanderers:
        w.wanderers.remove(wd)
    war = war_of(game, getattr(wd, 'war', None))
    if war is None:
        return
    s = w.settlement_at(*wd.target) if wd.role in ('raid', 'forage') else None
    if wd.role == 'raid' and s and not plundered(game, s):
        RL.burn_village(game, s.region, R(game).kingdoms[wd.kingdom].short)
        i = 0 if war['a'] == wd.kingdom else 1
        war['raids'][i] += 1
        if war['raids'][i] % 2 == 0:
            war['score'] += side_of(war, wd.kingdom)  # raiding shames the other lord
    elif wd.role == 'forage' and s:
        for g in ('grain', 'ale'):
            if g in s.market:
                s.market[g][0] = max(1, s.market[g][0] - 6)
        h = next(iter(hosts(game, war, wd.kingdom)), None)
        if h:
            h.strength += 1
    elif wd.role == 'message':
        h = next(iter(hosts(game, war, wd.kingdom)), None)
        if h:
            h.strength += 1


def describe(wd, game):
    if wd.kind != 'warparty':
        return None
    what = {'raid': 'out to burn a village of the enemy', 'forage': 'out to strip the enemy\'s fields',
            'message': 'riding hard with orders', 'scout': 'watching the enemy\'s host'}[wd.role]
    return f'{wd.name}, {what}' + (', hostile to you.' if wd.hostile else '.')


def talk(game, wd):
    """Walking into a war party that is not after you: catch it, or let it be."""
    from . import events as EV
    EV.ask(game, 'war_party', wd.name, describe(wd, game),
           [('Fall on them', 'fight'), ('Let them pass', 'leave')], wd=wd.id)
    return 0


def r_party(game, choice, ctx):
    wd = next((x for x in game.world.wanderers if x.id == ctx['wd']), None)
    if wd is None or choice != 'fight':
        return
    game.start_encounter(wd)


def beaten(game, wd):
    """A war party or host you beat: the other side is glad of it."""
    from . import realms as RL
    war = war_of(game, getattr(wd, 'war', None))
    if war is None:
        return
    other = war['b'] if war['a'] == wd.kingdom else war['a']
    RL.add_favour(game, other, 4 if wd.kind == 'warparty' else 8)
    if wd.kind == 'warparty' and wd.role == 'message':
        game.msg(f'The messenger carried orders for {R(game).kingdoms[wd.kingdom].short}: '
                 f'{R(game).kingdoms[other].short} will pay for them in favour.', 'good')
    war['score'] += side_of(war, other) if wd.kind == 'host' or random.random() < .3 else 0


# ------------------------------------------------------------------ sieges and you
def besieging(game, x, y):
    """The host besieging the seat on this cell, or None."""
    from . import realms as RL
    Rl = getattr(game.world, 'realm', None)
    if Rl is None:
        return None
    for wd in game.world.wanderers:
        if wd.kind == 'host' and getattr(wd, 'siege_until', None) and wd.target_r in Rl.baronies:
            tb = Rl.baronies[wd.target_r]
            if tb.seat and RL.seat_pos(game.world, tb.seat) == (x, y):
                return wd
    return None


def at_seat(game, x, y):
    """[>] on a besieged seat: smuggle food in, open the postern, slip in, or leave it."""
    from . import events as EV
    wd = besieging(game, x, y)
    if wd is None:
        return None
    p = game.player
    food = sum(p.cargo.get(g, 0) for g in ('grain', 'fish', 'ale', 'meat') if g in D.GOODS)
    kn = getattr(p, 'knight', None) or {}
    Rl = R(game)
    tb = Rl.baronies[wd.target_r]
    opts = [(f'Smuggle food in by night: {food} loads', 'food' if food else None),
            ('Open the postern for the besiegers', 'postern' if kn.get('kid') == wd.kingdom else None),
            ('Slip in through the postern', 'in'), ('Leave it', 'leave')]
    EV.ask(game, 'war_siege', f'The siege of the {tb.name}',
           f'{wd.name} lies round the walls. The stores inside last {max(0, getattr(wd, "stores", 9))} more days, '
           f'they say, and the engines have {"made a breach" if getattr(wd, "breach", 0) >= 8 else "not broken through yet"}. '
           'By night a postern on the far side still opens for those who know the knock.',
           opts, wd=wd.id, at=(x, y))
    return 0


def r_siege(game, choice, ctx):
    from . import realms as RL
    from . import tally as TY
    from .money import fmt
    wd = next((x for x in game.world.wanderers if x.id == ctx['wd']), None)
    p = game.player
    if wd is None or choice in (None, 'leave'):
        return
    tb = R(game).baronies.get(wd.target_r)
    defender = tb.kingdom if tb else wd.foe
    night = not _day(game)
    if choice == 'food':
        loads = 0
        for g in ('grain', 'fish', 'ale', 'meat'):
            loads += p.cargo.pop(g, 0)
            if isinstance(getattr(p, 'cost_basis', None), dict):
                p.cost_basis.pop(g, None)
        if not night and random.random() < .5:
            game.msg('A sentry of the besiegers sees the wagon in the daylight. You lose the load and run.', 'bad')
            return
        days = max(1, loads // 4)
        wd.stores = getattr(wd, 'stores', 8) + days
        if getattr(wd, 'siege_until', None):
            wd.siege_until = max(wd.siege_until, game.day + min(wd.stores, 30))
        pay = loads * 300
        p.gold += pay
        TY.add(game, 'earned_trade', pay)
        RL.add_favour(game, defender, 3 + days)
        mine(game)['smuggled'] += loads
        game.msg(f'You bring {loads} loads of food in through the postern: the {tb.name if tb else "seat"} holds '
                 f'{days} days longer. The steward pays {fmt(pay)}.', 'good')
    elif choice == 'postern':
        wd.breach = 99
        wd.storm = 'breach'
        wd.siege_until = game.day
        RL.add_favour(game, wd.kingdom, 8)
        game.msg('In the dark you lift the bar of the postern. Your liege\'s men pour in behind you.', 'good')
    elif choice == 'in':
        s = game.world.settlement_at(*ctx['at'])
        if s:
            game.msg('You slip in through the postern, past a hungry sentry.', 'info')
            game.enter_town(s.id)


def _day(game):
    from . import camps as CM
    return not CM.camping(game)


# ------------------------------------------------------------------ ransom
def ransom_worth(lo):
    return RANSOM.get(lo.title, 90) * 100


def take_captive(game, lo, kid):
    """You hold a lord for ransom (taken in the field)."""
    lo.held = 'you'
    if not any(c['lid'] == lo.id for c in mine(game)['captives']):      # one lord, one ransom
        mine(game)['captives'].append(dict(lid=lo.id, kid=kid, day=game.day))


def ransom_options(game, lo_here):
    """At a lord of a kingdom: the captives of yours he would buy back."""
    from . import realms as RL
    Rl = R(game)
    kg = RL.kingdom_of_lord(Rl, lo_here)
    if kg is None:
        return []
    out = []
    for c in mine(game)['captives']:
        if c['kid'] == kg.id:
            lo = Rl.lord(c['lid'])
            if lo and lo.alive:
                out.append((lo, ransom_worth(lo)))
    return out


def ransom(game, lid):
    from . import realms as RL
    from .money import fmt
    from . import tally as TY
    Rl = R(game)
    c = next((c for c in mine(game)['captives'] if c['lid'] == lid), None)
    lo = Rl.lord(lid)
    if c is None or lo is None:
        return 0
    mine(game)['captives'].remove(c)
    lo.held = None
    pay = ransom_worth(lo)
    game.player.gold += pay
    TY.add(game, 'earned_jobs', pay)
    game.msg(f'{RL.style(Rl, lo, False)} is bought back for {fmt(pay)}, and rides home without a word to you.', 'good')
    return pay


def free_held(game, war):
    """The peace sends the captives of a war home."""
    Rl = R(game)
    for lid in war.get('captives', []):
        lo = Rl.lord(lid)
        if lo:
            lo.held = None


def peace_how(war):
    """The peace by the score: land for a crushing war, a hostage for a clear one, tribute for the rest."""
    s = abs(war['score'])
    return 'land' if s >= PEACE_SCORE else 'hostage' if s >= 4 else 'tribute'


# ------------------------------------------------------------------ the field battle
def field_at(game, x, y):
    Rl = getattr(game.world, 'realm', None)
    if Rl is None:
        return None
    for war in Rl.wars:
        fd = war.get('field')
        if fd and fd.get('state') == 'pending' and cheb(fd['x'], fd['y'], x, y) <= 1:
            return war
    return None


def ask_field(game, war):
    """At the field before the battle: choose your side."""
    from . import events as EV
    Rl = R(game)
    a, b = Rl.kingdoms[war['a']], Rl.kingdoms[war['b']]
    kn = getattr(game.player, 'knight', None) or {}
    opts = []
    for kg in (a, b):
        if kn.get('kid') in (a.id, b.id) and kn.get('kid') != kg.id:
            continue
        opts.append((f'Stand in the line of {kg.short}', f'side:{kg.id}'))
    EV.ask(game, 'war_field', 'The field', 'Banners, horses, the smoke of a thousand fires. At first light the lines '
           'will close. Where do you stand?', opts + [('Not today', 'leave')], war=war['id'])
    return 0


def r_field(game, choice, ctx):
    war = war_of(game, ctx['war'])
    if war is None or not choice or not choice.startswith('side:'):
        return
    enter_field(game, war, int(choice[5:]))


def is_mage(game):
    """A sorcerer, an elementalist and their like: the captain gives them a mage's task."""
    from . import classes as CL
    return any(c in ('fire', 'frost', 'storm', 'shadow', 'necromancy', 'nature', 'arcane') for c in CL.classes(game))


def your_tasks(game, enemy):
    mage = is_mage(game)
    theirs = getattr(enemy, 'mage', None)
    if mage:
        opts = ([('Meet their mage', 'mage')] if theirs else []) + [('Break their front', 'front')]
    else:
        opts = [('Hold the flank', 'flank'), ('Save the banner', 'banner'), ('Cut down their captain', 'captain')]
        if theirs:
            opts.append(('Take out their mage', 'mage'))
    return opts + [('Just fight', 'fight')], mage


def enter_field(game, war, kid):
    """Into the battle's own map, in one corner of your line; your captain gives you a task."""
    from . import events as EV
    p = game.player
    fd = war['field']
    ids = (fd['a'], fd['b'])
    hs = {x.id: x for x in game.world.wanderers if x.id in ids}
    own = next((x for x in hs.values() if x.kingdom == kid), None)
    foe = next((x for x in hs.values() if x.kingdom != kid), None)
    if own is None or foe is None:
        game.msg('The hosts are gone from the field.', 'info')
        war['field']['state'] = 'done'
        return
    if game.cur == 'over':
        game.over_pos = (p.x, p.y)
    key = f'field:{war["id"]}'
    game.maps[key] = gen_field(game, war, own, foe)
    game.cur = key
    m = game.map
    p.x, p.y = m.entry
    game.compute_fov()
    fd['state'] = 'fighting'
    from . import guide as GD
    GD.tip(game, 'field')
    opts, mage = your_tasks(game, foe)
    EV.ask(game, 'war_task', 'Your captain', f'"{foe.name} stands across the field. ' +
           ('You have the art: our line needs it where it counts.' if mage else 'I need every sword.') + ' Here is your part."',
           opts, war=war['id'])
    return 1


def r_task(game, choice, ctx):
    m = game.map
    bt = getattr(m, 'battle', None)
    if not bt:
        return
    bt['task'] = choice or 'fight'
    game.msg({'flank': 'You take the far left of the line, where their horse will come.',
              'banner': 'You stand by the banner. If it falls, the line breaks.',
              'captain': 'Their captain rides behind their line. Find him.',
              'mage': 'Their mage stands behind their line with a bodyguard. Get to him.',
              'front': 'Break their front: the more fall to you, the sooner they waver.',
              'fight': 'You take your place in the line.'}.get(bt['task'], ''), 'info')


def gen_field(game, war, own, foe):
    from .entities import GameMap
    from . import camps as CM
    fd = war['field']
    ground = CM._ground(game, fd['x'], fd['y'])
    m = GameMap(f'field:{war["id"]}', 'town', 'The field', FIELD_W, FIELD_H, ground)
    m.sid = m.hid = m.site = None
    m.signs, m.tint = [], {}
    m.radius = 60                                     # a whole field under the open sky
    rnd = random.Random(war['id'])
    for _ in range(120):
        x, y = rnd.randrange(FIELD_W), rnd.randrange(FIELD_H)
        if 6 < y < FIELD_H - 6:
            m.set(x, y, rnd.choice([D.TREE, D.BUSH if hasattr(D, 'BUSH') else D.TREE, ground]) if rnd.random() < .15 else ground)
    m.entry = (8, FIELD_H - 7)
    bx, by = 12, FIELD_H // 2 + 4
    m.set(bx, by, D.BANNER)
    m.battle = dict(war=war['id'], own=own.id, foe=foe.id, kid=own.kingdom, n=0, phase='arrows', task='fight',
                    front=[FIELD_H // 2] * FIELD_W, kills=0, captain=None, mage=None, banner=(bx, by), threat=0,
                    result=None, waves=0, flank=None, own_fg=tuple(own.fg), foe_fg=tuple(foe.fg),
                    own_mage=getattr(own, 'mage', None), foe_mage=getattr(foe, 'mage', None), done=False)
    for i in range(len(m.seen)):
        m.seen[i] = 1
    draw_lines(game, m)
    return m


def draw_lines(game, m):
    """The battle far from you: two lines of signs along the front, your men below it and theirs above."""
    bt = m.battle
    m.tint = {}
    p = game.player
    near = p.x if game.cur == m.key else m.entry[0]
    for x in range(m.w):
        if abs(x - near) <= 9:
            continue
        f = bt['front'][x]
        for dy in (1, 2, 3):
            y = f + dy
            if 0 <= y < m.h:
                m.tint[(x, y)] = ('☺' if (x + dy) % 3 else '¶' if (x % 12 == 0 and dy == 3) else '☺',
                                  tuple(int(c * (.85 - dy * .1)) for c in bt['own_fg']))
            y = f - dy
            if 0 <= y < m.h:
                m.tint[(x, y)] = ('@' if (x + dy) % 3 else '¶' if (x % 12 == 0 and dy == 3) else '@',
                                  tuple(int(c * (.85 - dy * .1)) for c in bt['foe_fg']))
        if bt['phase'] == 'clash' and (x + bt['n']) % 4 == 0:
            m.tint[(x, f)] = ('x', (200, 80, 60))           # where the lines meet


def _spawn(game, m, keys, cells, lvl, name=None, tag=None):
    from .entities import make_monster
    out = []
    for k in keys:
        cs = [c for c in cells if m.inb(*c) and D.TILES[m.tile(*c)].walk and not m.mon_at(*c)
              and c != (game.player.x, game.player.y)]
        if not cs:
            break
        x, y = random.choice(cs)
        mon = make_monster(game, k, x, y, lvl)
        mon.awake = True
        mon.battle = tag or 'foe'
        if tag in (None, 'foe', 'flank', 'banner', 'risen'):   # levies: worn by the march, they hit softer
            mon.dmg = tuple(max(1, round(v * .7)) for v in mon.dmg)
        if name:
            mon.name = name
        m.mons.append(mon)
        out.append(mon)
    return out


def _lvl(game):
    """The common soldier of a host is a levy, well below an adventurer; captains and mages stand above him."""
    return max(1, game.player.lvl * 2 // 3)


def wave(game, m, kind='line'):
    """Their men come at your corner of the line."""
    bt = m.battle
    p = game.player
    f = bt['front'][max(0, min(m.w - 1, p.x))]
    lvl = _lvl(game)
    cells = [(x, y) for x in range(max(0, p.x - 8), min(m.w, p.x + 9)) for y in range(max(0, f - 6), max(1, f - 1))]
    if kind == 'flank':
        cells = [(x, y) for x in range(0, 6) for y in range(max(0, f - 4), min(m.h, f + 6))]
        return _spawn(game, m, ['clan_rider', 'soldier', 'crossbow'], cells, lvl, tag='flank')
    if kind == 'banner':
        bx, by = bt['banner']
        cells = [(x, y) for x in range(bx - 6, bx + 7) for y in range(by - 9, by - 4)]
        return _spawn(game, m, ['soldier', 'soldier', 'crossbow'], cells, lvl, tag='banner')
    bt['waves'] += 1
    return _spawn(game, m, random.sample(['soldier', 'soldier', 'soldier', 'crossbow'], 2 + min(1, bt['waves'] // 3)),
                  cells, lvl)


def task_targets(game, m):
    """At the clash: whom your task is about."""
    from . import realms as RL
    bt = m.battle
    p = game.player
    f = bt['front'][p.x]
    lvl = _lvl(game)
    Rl = R(game)
    behind = [(x, y) for x in range(max(0, p.x - 12), min(m.w, p.x + 13)) for y in range(max(1, f - 12), max(2, f - 7))]
    if bt['task'] == 'captain':
        foe_k = next((x.kingdom for x in game.world.wanderers if x.id == bt['foe']), None)
        lords = [lo for lo in RL.lords_of(Rl, Rl.kingdoms[foe_k]) if lo.id != Rl.kingdoms[foe_k].king] if foe_k is not None else []
        lo = random.choice(lords) if lords else None
        cap = _spawn(game, m, ['knight'], behind, lvl + 1, name=f'Captain {lo.first}' if lo else 'Their captain', tag='captain')
        if cap:
            cap[0].elite = 1 if hasattr(cap[0], 'elite') else None
            cap[0].maxhp = cap[0].hp = cap[0].hp * 2
            bt['captain'] = cap[0].id
            bt['captain_lord'] = lo.id if lo else None
            _spawn(game, m, ['soldier', 'soldier'], behind, lvl, tag='guard')
    elif bt['task'] == 'mage' and bt.get('foe_mage'):
        mg = _spawn(game, m, ['cultist'], behind, lvl + 1, name=MAGE_NAME.get(bt['foe_mage'], 'Their battle mage'),
                    tag='mage')
        if mg:
            bt['mage'] = mg[0].id
            _spawn(game, m, ['knight', 'soldier'], behind, lvl, tag='guard')
    elif bt['task'] == 'flank':
        bt['flank'] = [o.id for o in wave(game, m, 'flank')]
    elif bt['task'] == 'banner':
        bt['flank'] = [o.id for o in wave(game, m, 'banner')]


def magic(game, m):
    """A mage of either side does what his school does to the ground near you."""
    from . import spellmap as SM
    bt = m.battle
    p = game.player
    f = bt['front'][p.x]
    for who, school in (('foe', bt.get('foe_mage')), ('own', bt.get('own_mage'))):
        if not school or (who == 'foe' and bt.get('mage_dead')):
            continue
        y = f + 2 if who == 'foe' else f - 2
        cells = [(x, y) for x in range(max(0, p.x - 7), min(m.w, p.x + 8))]
        if school == 'fire':
            SM.area(game, m, cells[::2], D.BURNING, 12, 4)
            game.msg(('Their' if who == 'foe' else 'Your') + ' mage sets a stretch of the front burning!', 'bad' if who == 'foe' else 'good')
        elif school == 'frost':
            SM.area(game, m, cells[:9], D.ICEWALL, 30)
            game.msg(('Their' if who == 'foe' else 'Your') + ' mage draws a wall of ice across the line.', 'info')
        elif school == 'nature':
            SM.area(game, m, cells, D.ROOTS, 15, 2)
            game.msg('Roots and thorns burst from the field.', 'info')
        elif school == 'runes':
            for o in [o for o in m.mons if not o.is_npc] if who == 'foe' else []:
                if not getattr(o, 'runed', False):
                    o.df = o.df * 1.3
                    o.runed = True
            game.msg('The rune-smith strikes his runes: their shields glow, and blows glance off.' if who == 'foe'
                     else 'Our rune-smith strikes his runes: our shields glow.', 'info')
        elif school == 'curse':
            if who == 'foe':
                game.player.buffs.append(['dmg', -10, 30, 'A shaman\'s curse'])
            game.msg('The drums beat and the shaman howls a curse over the field.', 'bad' if who == 'foe' else 'info')
        elif school == 'necromancy':
            if who == 'foe':
                _spawn(game, m, ['skeleton', 'zombie'], cells, _lvl(game), tag='risen')
            game.msg('The fallen of the field stand up again. Even their own men turn away.', 'bad')
        elif school == 'storm':
            game.msg('Lightning cracks down on the press!', 'bad' if who == 'foe' else 'good')
            if who == 'foe' and random.random() < .4:
                game.hurt(max(3, game.stats()['max_life'] // 10), 'a bolt of the battle mage', 'lightning')
        if who == 'own':
            for o in [o for o in m.mons if not o.is_npc and abs(o.y - y) <= 1 and abs(o.x - p.x) <= 8][:2]:
                o.hp -= max(1, o.maxhp // 3)
                if o.hp <= 0:
                    game.kill(o)


def turn(game):
    """One of your actions on the field: the phases, the waves, your line's help, the task, the end."""
    m = game.map
    bt = getattr(m, 'battle', None)
    if not bt or bt['done']:
        return
    bt['n'] += 1
    n = bt['n']
    war = war_of(game, bt['war'])
    if bt['phase'] == 'arrows':
        if n == 1:
            game.msg('Their archers loose: the sky goes dark with arrows. Keep your head down.', 'bad')
        if n % 6 == 0 and random.random() < .35:
            game.hurt(max(1, game.stats()['max_life'] // 20), 'an arrow out of the sky', None)
        if n >= 30:
            bt['phase'] = 'clash'
            game.msg('Trumpets! The lines close with a roar.', 'bad')
            wave(game, m)
            task_targets(game, m)
    elif bt['phase'] == 'clash':
        foes = [o for o in m.mons if not o.is_npc and getattr(o, 'battle', None)]
        if len(foes) < 3 and n % 12 == 0:
            wave(game, m)
        if n % 25 == 0:
            magic(game, m)
        for o in foes:                                # your line's spears reach the ones that come too near it
            if o.y > bt['front'][max(0, min(m.w - 1, o.x))] + 1 and random.random() < .35:
                o.hp -= max(1, o.maxhp // 4)
                if o.hp <= 0:
                    game.kill(o)
        if n % 10 == 0:
            ratio = _ratio(game, bt)
            for x in range(m.w):
                bt['front'][x] = max(8, min(m.h - 9, bt['front'][x] + (1 if random.random() > ratio else -1) *
                                            (1 if random.random() < .5 else 0)))
        if bt['task'] == 'banner':
            bx, by = bt['banner']
            near = any(not o.is_npc and cheb(o.x, o.y, bx, by) <= 1 for o in m.mons)
            bt['threat'] = bt['threat'] + 1 if near else 0
            if bt['threat'] >= 6 and not bt.get('lost'):
                bt['lost'] = True
                m.set(bx, by, D.GRASS)
                game.msg('The banner goes down! A groan runs along your line.', 'bad')
        if n >= 150 or (n >= 90 and task_done(game, m) is not None):
            decide(game, m, war)
    elif bt['phase'] == 'rout':
        if n - bt.get('rout_n', n) >= 40:
            bt['done'] = True
            game.msg('The field is quiet but for the crows. Walk off its edge when you are ready.', 'info')
    draw_lines(game, m)


def _ratio(game, bt):
    hs = {x.id: x for x in game.world.wanderers}
    own, foe = hs.get(bt['own']), hs.get(bt['foe'])
    if own is None or foe is None:
        return .5
    return might(own) / max(1, might(own) + might(foe))


def task_done(game, m):
    """True when your task is done, False when it failed, None while it is open."""
    bt = m.battle
    alive = {o.id for o in m.mons}
    t = bt['task']
    if t == 'captain':
        return None if bt['captain'] is None else bt['captain'] not in alive
    if t == 'mage':
        if bt['mage'] is None:
            return None
        if bt['mage'] not in alive:
            bt['mage_dead'] = True
            return True
        return None
    if t == 'banner':
        if bt.get('lost'):
            return False
        return None if not bt['flank'] else not any(i in alive for i in bt['flank'])
    if t == 'flank':
        return None if not bt['flank'] else not any(i in alive for i in bt['flank'])
    if t == 'front':
        return True if bt['kills'] >= 8 else None
    return None


def bonus(game, m):
    """What your part weighs: at most about 15%."""
    bt = m.battle
    ok = task_done(game, m)
    if bt['task'] == 'fight':
        return min(.05, bt['kills'] * .005)
    if ok:
        return .15
    if ok is False:
        return -.05
    return min(.04, bt['kills'] * .004)


def decide(game, m, war, fled=False):
    """The battle is settled by the hosts' strength, and your part."""
    from . import realms as RL
    bt = m.battle
    if bt['result'] is not None:
        return
    hs = {x.id: x for x in game.world.wanderers}
    own, foe = hs.get(bt['own']), hs.get(bt['foe'])
    b = 0.0 if fled else bonus(game, m)
    if bt.get('mage_dead') and foe is not None:
        foe.mage = None
    you = _your_line(game, bt, fled)
    if own is None or foe is None or war is None:
        bt['result'] = 'none'
        bt['done'] = True
        return
    win = skirmish(game, war, own, foe, bonus=b, big=True, you=you)
    war['field']['state'] = 'done'
    bt['result'] = 'won' if win is own else 'lost'
    mine(game)['fields'].append(dict(war=war['id'], day=game.day, task=bt['task'], ok=task_done(game, m),
                                     result=bt['result']))
    field_job_done(game, war, not fled)
    if fled:
        return
    bt['phase'] = 'rout'
    bt['rout_n'] = bt['n']
    if bt['result'] == 'won':
        game.msg('Their line wavers, then breaks. They run!', 'good')
        for o in [o for o in m.mons if not o.is_npc and getattr(o, 'battle', None)]:
            if cheb(o.x, o.y, game.player.x, game.player.y) > 4:
                m.mons.remove(o)
            else:
                o.effects['fear'] = [40, 0]           # the ones near you run too
        RL.add_favour(game, own.kingdom, 6)
        if bt['task'] == 'captain' and task_done(game, m) and bt.get('captain_lord'):
            lo = R(game).lord(bt['captain_lord'])
            if lo and lo.alive and not getattr(lo, 'held', None):
                take_captive(game, lo, foe.kingdom)
                game.msg(f'Their captain lives, barely: {RL.style(R(game), lo, False)} is your prisoner, worth a ransom.', 'gold')
    else:
        game.msg('Your line breaks! Their riders come after the runners. Get to the edge of the field!', 'bad')
        p = game.player
        cells = [(x, y) for x in range(max(0, p.x - 12), min(m.w, p.x + 13)) for y in range(max(0, p.y - 12), max(1, p.y - 6))]
        _spawn(game, m, ['clan_rider'] * 3, cells, _lvl(game), name='A rider of the enemy', tag='rider')


def _your_line(game, bt, fled):
    if fled:
        return 'An adventurer who stood in the line left it before the end.'
    ok = task_done(game, game.map)
    what = {'flank': 'held the flank', 'banner': 'saved the banner', 'captain': 'cut down their captain',
            'mage': 'took out their mage', 'front': 'broke into their front', 'fight': 'fought in the line'}[bt['task']]
    if bt['task'] == 'fight' or ok:
        return f'{game.player.name} {what}.'
    return None


def leave(game):
    """Off the edge of the field: before the end your lord remembers it."""
    m = game.map
    bt = getattr(m, 'battle', None)
    war = war_of(game, bt['war']) if bt else None
    if bt and bt['result'] is None and war is not None:
        decide(game, m, war, fled=True)
        mine(game)['fled'].append(dict(war=war['id'], day=game.day))
        from . import realms as RL
        RL.add_favour(game, bt['kid'], -10)
        game.msg('You walk off the field before the end. Your lord will remember it.', 'bad')
    fd = war.get('field') if war else None
    game.over_pos = (fd['x'], fd['y']) if fd else game.over_pos
    game.maps.pop(m.key, None)


def after_kill(game, mon):
    m = game.map
    bt = getattr(m, 'battle', None)
    if bt and getattr(mon, 'battle', None):
        bt['kills'] += 1


def resolve_pending(game):
    """A field battle whose day has come with no one in it: the strength decides alone."""
    Rl = getattr(game.world, 'realm', None)
    if Rl is None:
        return
    for war in list(Rl.wars):
        fd = war.get('field')
        if not fd or fd.get('state') not in ('pending', 'fighting'):
            continue
        if fd['state'] == 'pending' and game.day < fd['day'] + 1:
            continue
        if game.cur == f'field:{war["id"]}':
            continue
        game.maps.pop(f'field:{war["id"]}', None)        # you fell there, or went off another way
        hs = {x.id: x for x in game.world.wanderers}
        a, b = hs.get(fd['a']), hs.get(fd['b'])
        fd['state'] = 'done'
        if a and b:
            skirmish(game, war, a, b, big=True)


# ------------------------------------------------------------------ the lines under the map
def line(game):
    if game.cur != 'over':
        bt = getattr(game.map, 'battle', None)
        if bt:
            return {'arrows': 'Arrows', 'clash': 'The clash', 'rout': 'The rout'}[bt['phase']] + \
                (f' · {bt["kills"]} fell to you' if bt['kills'] else '')
        return None
    p = game.player
    if field_at(game, p.x, p.y):
        return 'Two hosts camp across this field: battle at first light.'
    wd = besieging(game, p.x, p.y)
    if wd:
        return f'Besieged by {wd.name[0].lower() + wd.name[1:]}.'
    if on_front(game, p.x, p.y):
        return 'The front: smoke on the skyline, empty fields.'
    return None


def arrive_field(game, m):
    war = war_of(game, m.data.get('war'))
    if war is None or not war.get('field') or war['field'].get('state') != 'pending':
        return ('The field is empty but for the crows. You came too late.', [('Go', 'late')])
    return ('Banners, horses, the smoke of a thousand fires. At first light the lines will close.',
            [('Find your place', 'go')])


def do_field(game, m, choice):
    from . import missions as MS
    war = war_of(game, m.data.get('war'))
    if choice == 'late' or war is None:
        MS.fail(game, m, 'The battle was fought without you.')
        return
    kid = m.data.get('kid')
    if kid is None:
        ask_field(game, war)
    else:
        enter_field(game, war, kid)


def field_job_done(game, war, ok):
    from . import missions as MS
    for m in [x for x in MS.active(game) if x.kind == 'realm' and x.data.get('task') == 'field'
              and x.data.get('war') == war['id']]:
        if ok:
            MS.complete(game, m, [])
        else:
            MS.fail(game, m, 'You left the line.')


def make_warletter(game, g):
    """A lord at war sends orders to his host in the field: through the front, where the enemy's scouts ride."""
    from . import realms as RL
    from . import realmjobs as RJ
    Rl = R(game)
    lo = Rl.lord(g['lid'])
    kg = RL.kingdom_of_lord(Rl, lo) if lo else None
    if kg is None:
        return None
    war = next((x for x in Rl.wars if kg.id in (x['a'], x['b'])), None)
    if war is None:
        return None
    hs = hosts(game, war, kg.id)
    if not hs:
        return None
    h = hs[0]
    pay = 20 + cheb(h.x, h.y, *RL.place_of(game, lo)) // 4
    return RJ.mission(game, g, 'warletter', f'Orders for {h.name.replace("The ", "the ")}',
                      f'{RL.style(Rl, lo, False)} gives you sealed orders for {h.name.replace("The ", "the ")}, in the '
                      f'field to the {RJ.dirto(RL.place_of(game, lo), h.x, h.y)}. The enemy\'s scouts ride between.',
                      pay, 15, 'crown', spot=[h.x, h.y], reach=3, where='the host in the field', host=h.id, war=war['id'],
                      kid=kg.id)


def arrive_warletter(game, m):
    return ('Riders on the skyline: the enemy\'s scouts, between you and the host.',
            [('Ride through them', 'ride'), ('Go round by the long way', 'round')])


def do_warletter(game, m, choice):
    from . import realmjobs as RJ
    from . import missions as MS
    h = next((x for x in game.world.wanderers if x.id == m.data.get('host')), None)
    if h is not None:
        h.strength += 1                               # the orders arrive: the host knows where to go
    if choice == 'ride' and random.random() < .6:
        RJ.fight(game, m, ['crossbow', 'soldier', 'clan_rider'], RJ.lvl_at(game, *m.data['spot']), 0,
                 'They have seen you. The scouts wheel round and come at you.')
        return
    if choice == 'round':
        game.end_turn(D.DAY_LEN // 4, True)
    RJ.favour(game, m.data.get('kid'), 4)
    game.msg('You hand the orders to the marshal. He reads them and nods.', 'good')
    MS.complete(game, m, [])


def won_warletter(game, m):
    from . import realmjobs as RJ
    from . import missions as MS
    RJ.favour(game, m.data.get('kid'), 5)
    game.msg('The scouts are down. You ride on and hand the orders to the marshal.', 'good')
    MS.complete(game, m, [])


def init():
    from . import realmjobs as RJ
    RJ.TASKS['warletter'] = dict(giver='lord', title='Orders through the front', make=make_warletter)
    RJ.SCENES['warletter'] = (arrive_warletter, do_warletter, won_warletter)
    RJ.SCENES['field'] = (arrive_field, do_field, None)
    from . import events as EV
    EV.RESOLVERS.update({'war_party': r_party, 'war_siege': r_siege, 'war_field': r_field, 'war_task': r_task})
