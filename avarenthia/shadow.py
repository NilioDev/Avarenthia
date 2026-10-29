"""The shadow over the world (the great evils, part 1: the frame).

One ultimate evil, the Hollow King, the old shadow of the Varnish, sits in the piece of the Sky-Seat that never
fell. His land is the coast facing it, and it grows his as he wakes. Under him stand three servants in every world,
one of each weight (evils.py holds their kinds): a light one, awake from the start and only in its own land; a
middle one that wakes halfway and holds a few baronies or a coast; a heavy one that wakes late and reaches a whole
realm. Each wants one thing, and pushes the realms and powers that are already there to get it (at most one push
per realm a month); the realms push back. When one has what it wants, a seal breaks.

Two clocks. The slow one always runs. The attention clock runs only when you meddle (a lieutenant killed, a lair
entered, a weakness learnt, his hunters beaten): it brings hunters and faster plans and wakes the next servant
sooner; it cools when you leave him alone, and climbs one step at a time, each after a pause. It belongs to the
world, not to the player.

Each servant has three lieutenants with places of their own, one weakness found from two sources (a library, the
riddles, a fallen hero's journal, a lieutenant's papers), and a relic it leaves when it falls. Named heroes ride to
the lairs: now and then one kills a lieutenant; most do not come back, and their cairn keeps their journal.
State: world.shadow (the world's), p.shadow (what you know)."""
import math
import random

from . import data as D
from . import evils as EVL
from .worldgen import cheb

WAKE = {'light': (0, 0), 'middle': (100, 140), 'heavy': (250, 330)}       # the day each weight wakes, before you meddle
RATE = {'light': .11, 'middle': .14, 'heavy': .17}                        # how fast its goal fills, a day
REACH = {'light': 14, 'middle': 26, 'heavy': 42}                          # how far its mark reaches at the most
PUSH = {'light': .3, 'middle': .45, 'heavy': .6}                          # a push in a month
HOLDS = {'light': 0, 'middle': 2, 'heavy': 4}                             # baronies it may hold
WEIGHT_WORD = {'light': 'a lesser servant', 'middle': 'a greater servant', 'heavy': 'his right hand'}
ATT_MAX, ATT_STEP, ATT_PAUSE, ATT_COOL = 5, 3, 10, 20
ATTENTION = ['He does not know you.', 'He has glanced your way.', 'He watches you.', 'He is looking for you.',
             'He hunts you.', 'His whole will is on you.']
ATT_MSG = {1: 'For a moment the sky feels heavier, as if something far away has turned its head.',
           2: 'You feel watched, all day, from somewhere past the sea.',
           3: 'Something is looking for you. Birds go quiet when you pass.',
           4: 'The Hollow King hunts you now. His servants will send their hunters.',
           5: 'His whole will is on you. The air itself is cold.'}
LAND_R = 36
NIGHT_R = 54                  # how far his coast reaches in the Long Night
SKY = 'The Sky-Seat'

# what each servant wants, its lever on the world, its lieutenants (title, monster, place, a person), its weakness
# (the edge it gives you once known from two sources) and the relic it leaves
SERVANT = {
    'lich': dict(goal='the dead, for an army', lever='war',
                 lts=[('the Gravecaller', 'skel_mage', 'tower', True), ('the Pale Rider', 'wight', 'fort', True),
                      ('the Bone Shepherd', 'draugr', 'camp', True), ('the Lantern of Bones', 'wraith', 'tower', True),
                      ('the Ash Priest', 'cultist', 'tower', True)],
                 weak=('her phylactery', 'jar', 'Her life is kept in a black jar in her crypt, beside her. Break it, '
                       'or she rises again.'),
                 relic=('The Grave-Ring', 'res_cold', 5, 'A ring of grey bone, cold to the touch.')),
    'dragon': dict(goal='gold', lever='tribute',
                   lts=[('the Ash Herald', 'cultist', 'tower', True), ('the Wyvern Rider', 'wyvern', 'camp', False),
                        ('the Toll-Taker', 'robber_knight', 'fort', True), ('the Scale-Sworn', 'knight', 'fort', True)],
                   weak=('the old wound', 'blows', 'An old spear wound under the left wing never closed: blows of a '
                         'weapon find it, a quarter harder.'),
                   relic=('A Scale of the Old Wing', 'res_fire', 6, 'A red scale the size of a shield, still warm.')),
    'spider': dict(goal='to grow', lever='webs',
                   lts=[('the Silk Mother', 'web_weaver', 'camp', False), ('the Weaverborn Elder', 'weaverborn', 'camp', False),
                        ('the Cocoon Keeper', 'phase_spider', 'tower', False), ('the Webkin Chief', 'webkin', 'camp', False)],
                   weak=('fire', ('elem', 'fire'), 'Her nest is dry silk and so is she: fire hurts her half again as much.'),
                   relic=('The Silk Heart', 'res_poison', 6, 'A knot of grey silk that beats, slowly.')),
    'warlord': dict(goal='land', lever='gorvash',
                    lts=[('the Warchief', 'orc_chief', 'camp', True), ('the Skull-Taker', 'orc_berserker', 'camp', True),
                         ('the Iron Shaman', 'orc_warlock', 'tower', True), ('the Hob Captain', 'hob_captain', 'fort', True)],
                    weak=('the oath of the duel', 'nocall', 'The tribes\' oath: a warlord challenged in his own hall '
                          'fights alone. Name the oath, and his band stays back.'),
                    relic=('The Iron Torc of the Gorvash', 'str', 2, 'A torc of black iron, too heavy for its size.')),
    'drowned': dict(goal='the coast', lever='flood',
                    lts=[('the Tide Priest', 'cultist', 'tower', True), ('the Wrecker Lord', 'wrecker', 'fort', True),
                         ('the Sea Hag', 'sea_hag', 'camp', True), ('the Merrow King', 'merrow', 'camp', False)],
                    weak=('dry land', 'dry', 'The old charm against the sea: say it in his hall, and the water does not '
                          'rise for him.'),
                    relic=('The Drowned Bell', 'res_light', 5, 'A small green bell. It rings under water only.')),
    'wendigo': dict(goal='to eat', lever='hunger',
                    lts=[('the Starved Trapper', 'ghoul', 'camp', True), ('the Snow Ape Elder', 'snow_ape', 'camp', False),
                         ('the Frost Witch', 'ice_witch', 'tower', True), ('the Hungry Chief', 'ghast', 'camp', True)],
                    weak=('fire', ('elem', 'fire'), 'It was a man once, who died of the cold: fire hurts it half again '
                          'as much.'),
                    relic=('The Antler Crown', 'res_cold', 6, 'A ring of old antler, bound with sinew.')),
    'wolf': dict(goal='the plain', lever='wolves',
                 lts=[('the Pack Mother', 'winter_wolf', 'camp', False), ('the Worg Rider', 'worg', 'camp', False),
                      ('the Wolf-Sworn Chief', 'clan_warrior', 'fort', True), ('the Grey Shaman', 'druid', 'tower', True)],
                 weak=('its true name', 'nocall', 'The shepherds\' oldest song gives its true name: call it by that, and '
                       'no pack comes to it.'),
                 relic=("The Great Wolf's Tooth", 'dex', 2, 'A yellow tooth as long as your hand.')),
    'mage': dict(goal='to rule', lever='sway',
                 lts=[('the Black Scribe', 'cultist', 'tower', True), ('the Iron Warden', 'animated_armour', 'fort', False),
                      ('the Bound Captain', 'knight', 'fort', True), ('the Imp-Keeper', 'imp', 'tower', False)],
                 weak=('his struck name', 'weaker', 'The Circle struck his name from its book. Read it out to him, and '
                       'he starts the fight a quarter weaker.'),
                 relic=('The Unlit Page', 'mana', 8, 'A page of black paper. The writing on it moves.')),
}
PLACE_NOUN = {'fort': 'Fort', 'tower': 'Tower', 'camp': 'Camp'}
LOOK = {'lt': ('Ω', (200, 120, 220)), 'hgrave': ('▲', (200, 196, 180))}
WHAT = {'lt': "a lieutenant's stronghold", 'hgrave': "a hero's cairn"}
SOURCES = {'library': 'a library', 'riddle': 'the riddles', 'hero': "a fallen hero's journal", 'papers': "a lieutenant's papers"}
HERO_FIRST = ['Aldric', 'Bryn', 'Cedric', 'Edda', 'Gareth', 'Hild', 'Isolde', 'Marek', 'Oswin', 'Rowena', 'Tamsin',
              'Wulf', 'Yrsa', 'Leofric', 'Maud', 'Corin']
HERO_EPI = ['the Bold', 'of the Lantern', 'Oakheart', 'the Grey', 'Redcloak', 'of the White Ford', 'the Younger',
            'Stormborn', 'the Patient']


def st(world):
    return getattr(world, 'shadow', None)


def know(game):
    """What this hero knows of the shadow: weakness clues per servant, lieutenants heard of, the Hollow King."""
    p = game.player
    if not hasattr(p, 'shadow'):
        p.shadow = dict(src={}, lts=set(), king=False, read=set())
    return p.shadow


def idx_of(game, e):
    return game.world.evils.index(e) if e in game.world.evils else None


# ------------------------------------------------------------------ making the world
def place_lairs(m, world, reach, dist, choose, Dungeon):
    """Each servant's lair: far from home, far from the other lairs and from the Hollow King's coast, in its own
    land. A light or middle kind whose land this world lacks gives way to another of its weight."""
    from .world import LINEAR
    from .powers import COLD
    w = m.w
    names = getattr(m, 'biome_names', [])
    cold = {k for k, n in enumerate(names) if n in COLD}
    terr = {'swamp': (D.SWAMP,), 'forest': (D.FOREST,), 'hills': (D.HILLS,), 'grass': (D.GRASS,), 'coast': (D.SAND, D.SWAMP)}
    sky = next(((x, y) for nm, x, y in world.wonders if nm == SKY), None)
    far = [i for i in reach if 30 * LINEAR <= dist[i] <= 60 * LINEAR and
           (sky is None or math.hypot(i % w - sky[0], i // w - sky[1]) > 60)] or reach
    taken = []

    def fits(k):
        d = EVL.EVILS[k]
        want = {t for key in d['terrain'] if key != 'cold' for t in terr[key]}
        if 'cold' in d['terrain']:
            return [i for i in far if m.biome[i] in cold and m.t[i] in (D.FOREST, D.GRASS, D.HILLS, D.SNOW)]
        return [i for i in far if m.t[i] in want]

    for e in world.evils:
        cands = fits(e.key)
        if not cands and e.weight != 'heavy':
            others = [k for k, wt in EVL.WEIGHT.items() if wt == e.weight and k != e.key and fits(k)]
            if others:
                ne = EVL.make(random.choice(others))
                e.__dict__.update(ne.__dict__)
                cands = fits(e.key)
        cands = cands or far
        apart = [i for i in cands if all(cheb(i % w, i // w, a, b) >= 70 * LINEAR for a, b in taken)] or \
            [i for i in cands if all(cheb(i % w, i // w, a, b) >= 40 * LINEAR for a, b in taken)] or cands
        x, y = choose(apart, reach[len(reach) // 3])
        taken.append((x, y))
        d = e.d
        did = 'crypt' if e.key == 'lich' else f'lair_{e.key}'
        world.dungeons[did] = Dungeon(did, d['lair'].format(short=e.short), d['depth'], d['base'], d['style'], d['tag'],
                                      d['boss'], D.hexrgb(d['wall']), x, y, True)
        e.did, e.x, e.y = did, x, y


def setup(game, m, world, reach_set):
    """The Hollow King's coast, the clocks, and three lieutenants' places per servant; with dice of their own."""
    state = random.getstate()
    random.seed(game.seed * 7717 + 23)
    try:
        _setup(game, m, world, reach_set)
    finally:
        random.setstate(state)


def _setup(game, m, world, reach_set):
    w = m.w
    sky = next(((x, y) for nm, x, y in world.wonders if nm == SKY), None)
    coast, land = None, {}
    if sky:
        land_cells = [i for i in reach_set if m.t[i] != D.WATER]
        if land_cells:
            ci = min(land_cells, key=lambda i: math.hypot(i % w - sky[0], (i // w - sky[1]) * 1.4))
            coast = (ci % w, ci // w)
            for y in range(max(0, coast[1] - NIGHT_R), min(m.h, coast[1] + NIGHT_R + 1)):
                for x in range(max(0, coast[0] - NIGHT_R * 2), min(w, coast[0] + NIGHT_R * 2 + 1)):
                    i = y * w + x
                    if i in reach_set and m.t[i] != D.WATER:
                        d = math.hypot((x - coast[0]) * .7, y - coast[1])
                        if d <= NIGHT_R:
                            land[i] = int(d)
    world.shadow = dict(sky=sky, coast=coast, land=land, wake=0.0, seals=[], att=0, pts=0.0, step_day=-99,
                        meddled=-99, cooled=0, held={}, month=-1, heroes=[], night=False, torn=False, last=None,
                        lairs=set())
    for idx, e in enumerate(world.evils):
        lo, hi = WAKE[e.weight]
        e.wake_day = random.randint(lo, hi)
        e.awake = e.weight == 'light'
        e.goal = random.uniform(0, 8) if e.awake else 0.0
        pool = random.sample(SERVANT[e.key]['lts'], 3)
        e.lts = []
        for j, (title, mk, place, person) in enumerate(pool):
            lt = dict(title=title, k=mk, place=place, person=person, dead=None, scars=0, site=None,
                      name=_lt_name(e, title, person))
            e.lts.append(lt)
            spot = _lt_spot(m, world, e, reach_set)
            if spot:
                from .sites import Site
                s = Site(len(world.sites), 'lt', spot[0], spot[1], f"{lt['name']}'s {PLACE_NOUN[place]}")
                s.faction = world.region_at(*spot).faction
                s.lt = (idx, j)
                s.hidden, s.found = False, True
                world.sites.append(s)
                lt['site'] = s.id
    from . import skyseat as SK
    SK.setup(game, m, world)


def _lt_name(e, title, person):
    if not person:
        return title[0].upper() + title[1:]
    from .races import random_name
    race = 'orc' if e.key == 'warlord' else 'human'
    return f'{random_name(race, family=False)} {title}'


def _lt_spot(m, world, e, reach_set):
    w = m.w
    taken = [(s.x, s.y) for s in world.settlements] + [(d.x, d.y) for d in world.dungeons.values()] + \
            [(s.x, s.y) for s in world.sites]
    r = min(REACH[e.weight], 30)
    for _t in range(600):
        a = random.random() * math.tau
        dd = random.uniform(7, r)
        x, y = int(e.x + math.cos(a) * dd), int(e.y + math.sin(a) * dd * .6)
        if not m.inb(x, y) or y * w + x not in reach_set or m.t[y * w + x] in (D.WATER, D.ROAD, D.RIVER, D.MOUNTAIN):
            continue
        if y * w + x in getattr(world, 'wonder_cells', ()):
            continue
        if any(cheb(x, y, a_, b_) < 5 for a_, b_ in taken):
            continue
        return x, y
    return None


# ------------------------------------------------------------------ strength
def power(game, e):
    if e.defeated or not getattr(e, 'awake', False):
        return 0
    sh = st(game.world)
    att = sh['att'] if sh else 0
    dead = sum(1 for lt in e.lts if lt['dead'])
    base = {'light': 2, 'middle': 3, 'heavy': 4}[e.weight] + int(e.goal / 14) + att // 2 - dead
    return max(1, min(10, base))


def reach(e):
    """How far its mark lies on the land."""
    if e.defeated:
        return 0
    if not getattr(e, 'awake', False):
        return 3
    return int(min(REACH[e.weight], 5 + e.lvl * 2 + e.goal / 6))


def land_r(world):
    sh = st(world)
    if not sh or sh.get('won'):
        return 0
    return NIGHT_R if sh.get('night') else min(LAND_R, 10 + sh['wake'] * .26)


def his_land(game, x, y):
    """True on the coast the Hollow King has made his."""
    sh = st(game.world)
    if not sh or not sh['land']:
        return False
    d = sh['land'].get(y * game.maps['over'].w + x)
    return d is not None and d <= land_r(game.world)


def held_by(world, rid):
    sh = st(world)
    return None if not sh else sh['held'].get(rid)


# ------------------------------------------------------------------ the clocks
def daily(game):
    w = game.world
    sh = st(w)
    if not sh:
        return
    from . import skyseat as SK
    from . import economy as ECO
    SK.check(game)
    ECO.NIGHT[0] = SK.price_mult(w)
    if sh.get('won'):
        return
    day = game.day
    att = sh['att']
    before = [reach(e) for e in w.evils]
    for idx, e in enumerate(w.evils):
        if e.defeated:
            continue
        if e.back is not None and day >= e.back:
            rise_again(game, e)
        if not e.awake:
            e.wake_day -= att * .5                       # meddling wakes the next one sooner
            if day >= e.wake_day:
                wake(game, e)
            continue
        dead = sum(1 for lt in e.lts if lt['dead'])
        e.goal = min(100.0, e.goal + RATE[e.weight] * (1 + att / 4) * max(.4, 1 - .15 * dead))
        if e.goal >= 100 and not e.sealed:
            seal(game, e)
    sh['wake'] = min(100.0, sh['wake'] + .02 + .01 * att)
    if att and day - sh['meddled'] > ATT_COOL and day - sh['cooled'] >= 15:
        sh['att'] -= 1                                  # left alone, he looks away again
        sh['cooled'] = day
    _hunters(game, sh)
    _his_coast(game, sh)
    _scars(game)
    heroes_day(game)
    for e in w.evils:
        e.lvl = power(game, e)
    if [reach(e) for e in w.evils] != before:
        EVL.compute_taint(game)


def wake(game, e):
    e.awake = True
    from . import news as NW
    NW.post(game, 'danger', random.choice(EVL.SIGNS[e.d['taint']]), e.x, e.y)
    if e.key == 'warlord':
        _gorvash(game, e)


def seal(game, e):
    """It has what it wants: a seal breaks, and the glow over the sea grows."""
    sh = st(game.world)
    e.sealed = True
    sh['seals'].append(e.key)
    sh['wake'] = min(100.0, sh['wake'] + 20)
    sh['torn'] = True                                   # the mist round the Sky-Seat can part now (part 2)
    who = e.name if e.known else 'Something in the far country'
    game.msg(f'Far away a great bell tolls once, and the ground shivers. {who} has what it wanted. '
             'Out over the sea the sky glows, and stays lit.', 'unique')
    from . import news as NW
    NW.post(game, 'danger', 'Fishermen say the sky over the sea glows at night now, and they hear bells under the '
                            'water.', *(sh['coast'] or (e.x, e.y)))
    if len(sh['seals']) >= 3 and not sh['night']:
        sh['night'] = True
        from . import skyseat as SK
        SK.night_falls(game)


def meddle(game, n, e=None, why=''):
    """You meddled: the attention clock moves. One step at a time, each after a pause."""
    sh = st(game.world)
    if not sh:
        return
    sh['pts'] += n
    sh['meddled'] = game.day
    if e is not None:
        sh['last'] = idx_of(game, e)
    if sh['pts'] >= ATT_STEP and sh['att'] < ATT_MAX and game.day - sh['step_day'] >= ATT_PAUSE:
        sh['att'] += 1
        sh['pts'] = 0.0
        sh['step_day'] = game.day
        game.msg(ATT_MSG[sh['att']], 'bad')
        from . import guide as GDE
        GDE.tip(game, 'shadow')


def _hunters(game, sh):
    """Once he looks for you, the servant you angered last sends its hunters."""
    w = game.world
    p = game.player
    att = max(sh['att'], 2 if game.cur == 'over' and his_land(game, p.x, p.y) else 0)     # on his coast he sees you
    if att < 2:
        return
    act = [i for i, e in enumerate(w.evils) if not e.defeated and e.awake]
    if not act:
        return
    idx = sh['last'] if sh['last'] in act else max(act, key=lambda i: w.evils[i].lvl)
    hunts = [x for x in w.wanderers if x.kind == 'hunt']
    if len(hunts) < att // 2 + (att >= 5) and random.random() < .04 * att:
        EVL.spawn_hunt(game, idx)


def _his_coast(game, sh):
    """The villages on his coast suffer: the dead walk, the fishers leave."""
    if not sh['land'] or random.random() > .05 + .05 * len(sh['seals']):
        return
    w = game.world
    cands = [s for s in w.settlements if s.event is None and his_land(game, s.x, s.y) and s.id != 0]
    if cands:
        s = random.choice(cands)
        _strike(game, s, 'undead' if 'undead' in D.EVENTS else 'famine',
                f'The dead came up out of the sea at {s.name}. Half the fishers have left.')


def _strike(game, s, key, text):
    ev = D.EVENTS[key]
    s.event = (key, random.randint(4, 7))
    for g in (ev['good'], ev.get('also')):
        if g:
            s.market[g][1] = ev['target']
            s.market[g][0] = min(s.market[g][0], ev['target'] * 2)
    from . import news as NW
    NW.post(game, 'danger', text, s.x, s.y)


# ------------------------------------------------------------------ the levers: once a month
def monthly(game):
    w = game.world
    sh = st(w)
    R = getattr(w, 'realm', None)
    if not sh or R is None:
        return
    pushed = {}
    for idx, e in enumerate(w.evils):
        if e.defeated or not e.awake or random.random() > PUSH[e.weight] * (1 + sh['att'] / 5):
            continue
        rids = regions_of(game, idx)
        kgs = [k for k in {R.baronies[r].kingdom for r in rids if r in R.baronies and R.baronies[r].kingdom is not None
                           and R.baronies[r].kingdom >= 0} if k not in pushed]
        kid = random.choice(kgs) if kgs else None
        LEVERS[SERVANT[e.key]['lever']](game, idx, e, [r for r in rids if kid is None or
                                                     (r in R.baronies and R.baronies[r].kingdom == kid)])
        if kid is not None:
            pushed[kid] = idx
    _push_back(game, pushed)
    heroes_month(game)


def regions_of(game, idx):
    w = game.world
    tn = getattr(w, 'taint', None) or ()
    return sorted({w.region_of[i] for i, v in enumerate(tn) if v == idx + 1})


def _villages(game, rids, coast=False, kind=None):
    w = game.world
    om = game.maps['over']
    out = [s for s in w.settlements if s.region in rids and s.id != 0 and s.event is None and not s.is_city
           and (kind is None or s.kind in kind)]
    if coast:
        out = [s for s in out if any(om.inb(s.x + dx, s.y + dy) and om.tile(s.x + dx, s.y + dy) == D.WATER
                                     for dx in range(-2, 3) for dy in range(-2, 3))]
    return out


def _news(game, text, x, y):
    from . import realms as RL
    RL.news(game, text[0] + text[1:].replace(' The ', ' the '), x, y, 'The Shadow')


def _hold(game, idx, e, rids):
    """It takes a barony for itself: its colour on the realms layer."""
    sh = st(game.world)
    mine = [r for r, i in sh['held'].items() if i == idx]
    R = game.world.realm
    free = [r for r in rids if r in R.baronies and r not in sh['held']]
    if len(mine) >= HOLDS[e.weight] or not free:
        return None
    rid = random.choice(free)
    sh['held'][rid] = idx
    from . import realms as RL
    RL.refresh(game.world)
    b = R.baronies[rid]
    rg = game.world.regions[rid]
    _news(game, f'{b.name} is lost: it answers to {e.name if e.known else "a darkness nobody will name"} now.', rg.cx, rg.cy)
    return rid


def lever_war(game, idx, e, rids):
    """The Lich: every battle feeds her army. She sets the realms on each other."""
    from . import realms as RL
    R = game.world.realm
    kgs = {R.baronies[r].kingdom for r in rids if r in R.baronies and R.baronies[r].kingdom is not None}
    at_war = {k for wr in R.wars for k in (wr['a'], wr['b'])}
    for kid in kgs:
        if kid in at_war or kid < 0:
            continue
        others = [k for k in R.kingdoms if k.id != kid and k.id not in at_war]
        if others:
            RL.start_war(game, R.kingdoms[kid], random.choice(others), random.choice(['a dead envoy', 'whispers at court',
                                                                                     'an old grave opened']))
            return
    if e.lvl >= 5:
        _hold(game, idx, e, rids)


def lever_tribute(game, idx, e, rids):
    """The Dragon wants gold: a barony pays, or burns."""
    from . import realms as RL
    R = game.world.realm
    bs = [r for r in rids if r in R.baronies]
    if not bs:
        return
    rid = random.choice(bs)
    b = R.baronies[rid]
    rg = game.world.regions[rid]
    who = e.name if e.known else 'the dragon'
    if random.random() < .5:
        if b.kingdom is not None and b.kingdom >= 0:
            R.kingdoms[b.kingdom].burden += 1
        _news(game, f'{b.name} paid {who} its tribute in gold. The taxes go up to pay for it.', rg.cx, rg.cy)
        if e.lvl >= 4 and random.random() < .5:
            _hold(game, idx, e, [rid])
    else:
        _news(game, f'{b.name} would not pay {who}. The fire came at night.', rg.cx, rg.cy)
        RL.burn_village(game, rid, who)


def lever_webs(game, idx, e, rids):
    vs = _villages(game, rids)
    if vs:
        s = random.choice(vs)
        _strike(game, s, e.d['event'], f'The woodcutters of {s.name} will not go into the woods any more. Webs, '
                                       'and things in the webs.')


def lever_gorvash(game, idx, e, rids):
    _gorvash(game, e)
    from . import war as WAR
    if 'horde' in D.FACTIONS and random.random() < .5:
        WAR.launch(game, 'horde')
    _hold(game, idx, e, rids)


def _gorvash(game, e):
    """The Warlord is the Gorvash: the tribes follow him out of the badlands for as long as he lives."""
    from . import powers as PW
    PWS = PW.P(game.world)
    if PWS.get('gorvash') or not PWS.get('tribes') or 'horde' not in D.FACTIONS:
        return
    t = max(PWS['tribes'], key=lambda q: q['strength'])
    t['chief'], t['chief_g'] = e.name, 'male'
    PW.gorvash(game, t)
    PWS['gorvash']['lasts'] = 10 ** 6
    PWS['gorvash']['servant'] = idx_of(game, e)


def lever_flood(game, idx, e, rids):
    vs = _villages(game, rids, coast=True) or _villages(game, rids)
    if vs:
        s = random.choice(vs)
        _strike(game, s, e.d['event'], f'The sea came into {s.name} with the spring tide and did not go back. The '
                                       'boats are gone.')
    ships = [x for x in game.world.wanderers if x.kind == 'ship' and game.world.taint and
             game.world.taint[x.y * game.maps['over'].w + x.x] == idx + 1]
    if ships:
        sh_ = random.choice(ships)
        game.world.wanderers.remove(sh_)
        _news(game, f'{sh_.name} went down off the coast with all hands, in a calm sea.', sh_.x, sh_.y)


def lever_hunger(game, idx, e, rids):
    vs = _villages(game, rids)
    if vs:
        s = random.choice(vs)
        _strike(game, s, e.d['event'], f'The hunters of {s.name} went into the woods and did not come back. There is '
                                       'no meat this winter.')


def lever_wolves(game, idx, e, rids):
    vs = _villages(game, rids)
    if vs:
        s = random.choice(vs)
        _strike(game, s, e.d['event'], f'Wolves took the flocks of {s.name}, a hundred sheep in one night. The '
                                       'shepherds are leaving.')


def lever_sway(game, idx, e, rids):
    """The Fallen Mage takes the lords from inside: a baron's loyalty goes, and his barony is the mage's."""
    from . import realms as RL
    R = game.world.realm
    lords = [R.lord(R.baronies[r].lord) for r in rids if r in R.baronies and R.baronies[r].lord is not None]
    lords = [lo for lo in lords if lo and lo.alive and lo.title in ('baron', 'lord') and getattr(lo, 'swayed', None) is None]
    if not lords:
        return
    lo = random.choice(lords)
    lo.swayed = idx
    lo.loyalty = min(lo.loyalty, 10)
    rid = next(r for r in rids if r in R.baronies and R.baronies[r].lord == lo.id)
    rg = game.world.regions[rid]
    _news(game, f'{RL.style(R, lo, False)} has a new counsellor, and signs whatever he is given.', rg.cx, rg.cy)
    _hold(game, idx, e, [rid])


LEVERS = {'war': lever_war, 'tribute': lever_tribute, 'webs': lever_webs, 'gorvash': lever_gorvash,
          'flood': lever_flood, 'hunger': lever_hunger, 'wolves': lever_wolves, 'sway': lever_sway}


def _push_back(game, pushed):
    """The realms push back: a levy against it, the Church's order rides; it is held back, never stopped."""
    from . import realms as RL
    from . import powers as PW
    w = game.world
    R = w.realm
    sh = st(w)
    for kid, idx in pushed.items():
        e = w.evils[idx]
        if random.random() > .3:
            continue
        kg = R.kingdoms[kid]
        king = R.lord(kg.king)
        e.goal = max(0.0, e.goal - 4)
        x, y = RL.place_of(game, king) if king else (e.x, e.y)
        od = PW.P(w)['church'].get('order') if 'church' in PW.P(w) else None
        if od and random.random() < .4:
            _news(game, f'{od["name"]} rides against {e.name if e.known else "the darkness in the far country"}, '
                        f'at the High Priest\'s word.', x, y)
        else:
            _news(game, f'{RL.style(R, king, False) if king else kg.short} calls the realm to stand against '
                        f'{e.name if e.known else "the darkness"}. The levy marches.', x, y)
            kg.burden += 1
        mine = [r for r, i in sh['held'].items() if i == idx and r in R.baronies and R.baronies[r].kingdom == kid]
        if mine and random.random() < .25:
            rid = random.choice(mine)
            del sh['held'][rid]
            RL.refresh(w)
            rg = w.regions[rid]
            _news(game, f'{R.baronies[rid].name} is free again: the levy of {kg.short} took it back.', rg.cx, rg.cy)


# ------------------------------------------------------------------ heroes of the world
def heroes_month(game):
    w = game.world
    sh = st(w)
    if any(h['state'] == 'riding' for h in sh['heroes']) or random.random() > .3:
        return
    act = [i for i, e in enumerate(w.evils) if not e.defeated and e.awake]
    cities = [s for s in w.settlements if s.is_city] or w.settlements
    if not act or not cities:
        return
    idx = random.choice(act)
    e = w.evils[idx]
    g = random.choice(['male', 'female'])
    name = f'{"Ser" if g == "male" else "Dame"} {random.choice(HERO_FIRST)} {random.choice(HERO_EPI)}'
    s = random.choice(cities)
    sh['heroes'].append(dict(name=name, g=g, sv=idx, day=game.day, arrive=game.day + random.randint(15, 40),
                             state='riding', home=s.id))
    _news(game, f'{name} rides out of {s.name} to face {e.name if e.known else "the darkness in the far country"}.',
          s.x, s.y)


def heroes_day(game):
    w = game.world
    sh = st(w)
    for h in sh['heroes']:
        if h['state'] != 'riding' or game.day < h['arrive']:
            continue
        e = w.evils[h['sv']]
        he = 'he' if h['g'] == 'male' else 'she'
        alive = [lt for lt in e.lts if not lt['dead']]
        r = random.random()
        if e.defeated:
            h['state'] = 'home'
            continue
        if r < .3 and alive:
            lt = random.choice(alive)
            lt['dead'] = 'hero'
            lt['by'] = h['name']
            _news(game, f'{h["name"]} killed {lt["name"]}, who served {e.name if e.known else "the darkness"}.', e.x, e.y)
            h['state'] = 'home'
            if random.random() < .5:
                continue
        if r < .8:
            h['state'] = 'dead'
            site = _grave(game, h, e)
            if site:
                _news(game, f'{h["name"]} did not come back. They say {he} lies under a cairn near '
                            f'{w.dungeons[e.did].name}, with everything {he} learnt.', site.x, site.y)
        else:
            h['state'] = 'home'
            s = w.settlements[h['home']]
            _news(game, f'{h["name"]} came home to {s.name}, white-haired, and will not say what {he} saw.', s.x, s.y)


def _grave(game, h, e):
    from .sites import Site
    w = game.world
    om = game.maps['over']
    for _t in range(300):
        x, y = e.x + random.randint(-12, 12), e.y + random.randint(-8, 8)
        if not om.inb(x, y) or cheb(x, y, e.x, e.y) < 3 or not D.TILES[om.tile(x, y)].walk or \
                om.tile(x, y) in (D.ROAD, D.WATER, D.RIVER, D.ENTR, D.TOWN, D.CITY):
            continue
        if any(q.x == x and q.y == y for q in w.sites) or w.settlement_at(x, y) or w.dungeon_at(x, y):
            continue
        s = Site(len(w.sites), 'hgrave', x, y, f"{h['name'].split(' ', 1)[1].split(' ')[0]}'s Cairn")
        s.faction = w.region_at(x, y).faction
        s.hero, s.sv, s.hg = h['name'], h['sv'], h['g']
        s.hidden, s.found = False, True
        w.sites.append(s)
        return s
    return None


# ------------------------------------------------------------------ the weakness
def clue(game, e, src, where=''):
    """A source tells you of its weakness; two make it known. Learning it is meddling too."""
    k = know(game)
    got = k['src'].setdefault(e.key, set())
    if src in got:
        return False
    got.add(src)
    name, _edge, text = SERVANT[e.key]['weak']
    from . import chronicle as CH
    if len(got) >= 2:
        game.msg(f'You know the weakness of {e.name} now: {name}. {text}', 'unique')
        CH.add(game, 'The Shadow', f'{e.name}: {text}', 'read', who=SOURCES[src], where=where, key=f'sw:{e.key}',
               title=f'The weakness of {e.name}')
    else:
        game.msg(f'{SOURCES[src][0].upper() + SOURCES[src][1:]} speaks of {e.name} and of {name}. One more source, '
                 'and you will know what to do with it.', 'gold')
    meddle(game, 1, e, 'weakness')
    return True


def weak_known(game, e):
    return len(know(game)['src'].get(e.key, ())) >= 2


def on_level(game, m, did):
    """A servant's lair: you meddle by going in; at the bottom the weakness you know changes the fight."""
    w = game.world
    sh = st(w)
    e = next((q for q in w.evils if q.did == did and not q.defeated), None)
    if not e or not sh:
        return
    if (did, game.day) not in sh['lairs']:
        sh['lairs'] = {q for q in sh['lairs'] if q[1] >= game.day - 2}
        sh['lairs'].add((did, game.day))
        meddle(game, 1, e, 'lair')
    boss = next((o for o in m.mons if o.k == e.d['boss']), None)
    if not boss:
        return
    edge = SERVANT[e.key]['weak'][1]
    if edge == 'jar' and not getattr(m, 'jar', None):
        spot = _near_free(m, boss.x, boss.y, 3, 6)
        if spot:
            m.set(*spot, D.JAR)
            m.jar = spot
    if not weak_known(game, e) or getattr(boss, 'edge', None):
        return
    boss.edge = edge
    if edge == 'weaker':
        boss.hp = int(boss.maxhp * .75)
    elif edge == 'nocall':
        boss.no_call = True
    elif edge == 'dry':
        boss.no_trick = 'water'
    game.msg(f'You know what {e.name} fears. {SERVANT[e.key]["weak"][2]}', 'gold')


def _near_free(m, x, y, lo, hi):
    for r in range(lo, hi + 1):
        cells = [(x + dx, y + dy) for dx in range(-r, r + 1) for dy in range(-r, r + 1) if max(abs(dx), abs(dy)) == r]
        random.shuffle(cells)
        for c in cells:
            if m.inb(*c) and m.tile(*c) == D.FLOOR and not m.mon_at(*c):
                return c
    return None


def edge_mult(game, mon, weapon, elem):
    edge = mon.__dict__.get('edge')
    if not edge:
        return 1
    if edge == 'blows' and weapon:
        return 1.25
    if isinstance(edge, tuple) and edge[0] == 'elem' and elem == edge[1]:
        return 1.5
    return 1


def bump(game, x, y, t):
    m = game.map
    if t == D.JAR:
        m.set(x, y, D.TILES.index(next(tt for tt in D.TILES if tt.name == 'broken shard')))
        m.jar_broken = True
        e = next((q for q in game.world.evils if q.key == 'lich'), None)
        if e:
            e.jar = True
            e.back = None
        game.msg('You smash the black jar. Something inside it screams, very far away, and then nothing.', 'unique')
        game.shake()
        return 1
    if t == D.HCAIRN:
        site = game.world.sites[m.site] if getattr(m, 'site', None) is not None else None
        if not site or site.kind != 'hgrave':
            return 0
        e = game.world.evils[site.sv]
        he, his = ('he', 'his') if site.hg == 'male' else ('she', 'her')
        if site.id in know(game)['read']:
            game.msg(f'The stones over {site.hero}. You have read what {he} left.', 'info')
            return 0
        know(game)['read'].add(site.id)
        game.request = ('dialog', f'The journal of {site.hero}',
                        f'Under the top stones, wrapped in oilcloth, is {his} journal. The last pages are written fast.'
                        f'\n\n"Of {e.name}: {SERVANT[e.key]["weak"][2]} I know it now. I do not think I will get '
                        'home to say it."')
        clue(game, e, 'hero', game.loc_name())
        return 1
    return None


def returns(game, e, mon):
    """The Lich falls, but her jar is whole: she rises again, after a while."""
    if SERVANT[e.key]['weak'][1] != 'jar' or getattr(e, 'jar', False):
        return False
    e.back = game.day + 40
    e.goal = max(0.0, e.goal - 25)
    game.msg(f'{e.name} falls to dust. But the cold stays in the room, and somewhere close, something she left '
             'behind is still beating.', 'unique')
    meddle(game, 2, e, 'fight')
    return True


def rise_again(game, e):
    e.back = None
    key = f'{e.did}:{game.world.dungeons[e.did].depth}'
    if game.cur != key:
        game.maps.pop(key, None)                        # her crypt fills again
    from . import news as NW
    NW.post(game, 'danger', f'They say {e.name} walks again. The graves near her crypt are open.', e.x, e.y)


# ------------------------------------------------------------------ a servant falls, a lieutenant dies
def fallen(game, e):
    """After a servant falls: its relic, the baronies it held freed (and fought over), its lair a ruin, your name in
    the chronicle; the Gorvash breaks up if it was the Warlord."""
    w = game.world
    sh = st(w)
    if not sh:
        return
    idx = idx_of(game, e)
    from . import realms as RL
    held = [r for r, i in sh['held'].items() if i == idx]
    for r in held:
        del sh['held'][r]
    if held:
        RL.refresh(w)
        rg = w.regions[held[0]]
        _news(game, f'The lands {e.name} held are free, and the barons are already fighting over them.', rg.cx, rg.cy)
    if e.key == 'warlord':
        from . import powers as PW
        if PW.P(w).get('gorvash') and PW.P(w)['gorvash'].get('servant') == idx:
            PW.end_gorvash(game, 'was slain in his own hall')
    w.wanderers = [x for x in w.wanderers if not (x.kind == 'hunt' and getattr(x, 'evil', None) == idx)]
    give_relic(game, e)
    meddle(game, 3, e, 'servant')


def give_relic(game, e):
    from .entities import Item
    name, stat, v, text = SERVANT[e.key]['relic']
    it = Item(game.new_id(), 'relic', e.key)
    it.name = name
    it.servant = e.key
    if not game.add_to_inv(it):
        game.spill(game.map, game.player.x, game.player.y, it)
    game.msg(f'{name} is left where {e.name} fell. You take it: one of the keys, the old letters say.', 'rare')


def lt_of(game, mon):
    t = mon.__dict__.get('lt')
    if not t:
        return None, None
    e = game.world.evils[t[0]]
    return e, e.lts[t[1]]


def on_kill(game, mon):
    """A lieutenant dies: its servant is weaker, its papers tell of the weakness, the realm is grateful."""
    e, lt = lt_of(game, mon)
    if not lt:
        return False
    lt['dead'] = 'you'
    game.msg(f'{lt["name"]} is dead. {e.name if e.known else "Whatever it served"} is weaker for it.', 'unique')
    from . import chronicle as CH
    CH.deed(game, f'{lt["name"]} slain', f'You killed {lt["name"]}, who served {e.name}.')
    if lt['person'] or random.random() < .5:
        clue(game, e, 'papers', game.loc_name())
    from . import realms as RL
    R = getattr(game.world, 'realm', None)
    site = game.world.sites[lt['site']] if lt['site'] is not None else None
    if R is not None and site is not None:
        b = R.baronies.get(game.world.region_of[site.y * game.maps['over'].w + site.x])
        if b is not None and b.kingdom is not None and b.kingdom >= 0:
            RL.add_favour(game, b.kingdom, 2)
            game.msg(f'The lords of {R.kingdoms[b.kingdom].short} will hear of it.', 'good')
    meddle(game, 2, e, 'lieutenant')
    e.lvl = power(game, e)
    return True


def _scars(game):
    """One who survived you heals, comes back scarred and promoted; he does not talk."""
    for e in game.world.evils:
        for lt in e.lts:
            if lt['dead'] or lt['site'] is None:
                continue
            site = game.world.sites[lt['site']]
            m = game.maps.get(site.map_key)
            if m is None or game.cur == site.map_key:
                continue
            o = next((x for x in m.mons if x.__dict__.get('lt')), None)
            if o and o.hp < o.maxhp:
                lt['scars'] += 1
                del game.maps[site.map_key]


# ------------------------------------------------------------------ a lieutenant's place
def is_shadow(site):
    return site.kind in LOOK


def site_map(game, site):
    state = random.getstate()
    random.seed(game.seed * 3301 + site.x * 977 + site.y * 37 + 5)
    try:
        m = _grave_map(game, site) if site.kind == 'hgrave' else _lt_map(game, site)
    finally:
        random.setstate(state)
    if site.kind == 'lt':
        _lt_folk(game, site, m)
    return m


def _base(game, site, w, h, ground=D.GRASS):
    from .entities import GameMap
    m = GameMap(site.map_key, 'town', site.name, w, h, ground)
    m.glows, m.lights = [], []
    m.radius, m.sid, m.hid, m.signs = 60, None, None, []
    m.site = site.id
    m.deco = bytearray(w * h)
    m.level = game.world.danger_at(site.x, site.y) + 3
    om = game.maps['over']
    land = om.tile(site.x, site.y)
    for i in range(w * h):
        if random.random() < (.08 if land == D.FOREST else .03):
            m.t[i] = D.TREE
    return m


def _done(m, entry):
    m.entry = entry
    for x in range(0, 6):
        if m.tile(x, entry[1]) == D.TREE:
            m.set(x, entry[1], D.GRASS)
    for i in range(len(m.seen)):
        m.seen[i] = 1
    return m


def _lt_map(game, site):
    from . import tribes as TR
    e = game.world.evils[site.lt[0]]
    lt = e.lts[site.lt[1]]
    w, h = 60, 34
    m = _base(game, site, w, h)
    cy = h // 2
    TR.trail(m, [(0, cy), (24, cy)])
    if lt['place'] == 'camp':
        cells = TR.oval(38, cy, 14, 9) - TR.oval(38, cy, 13, 8)
        for x, y in cells:
            if m.inb(x, y) and not (x < 38 and abs(y - cy) <= 1):
                m.set(x, y, D.FENCE)
        for x, y in TR.oval(38, cy, 12.6, 7.6):
            if m.tile(x, y) == D.TREE:
                m.set(x, y, D.GRASS)
        for hx, hy in ((32, cy - 4), (44, cy - 4), (32, cy + 4), (44, cy + 4)):
            TR.round_hut(m, hx, hy, 3, 1)
            m.set(hx, hy + (2 if hy < cy else -2), D.DOOR)
        TR.fire(m, 38, cy)
        m.hall = (46, cy)
    elif lt['place'] == 'fort':
        TR.box(m, 26, cy - 9, 26, 19, D.WALL, D.FLOOR)
        m.set(26, cy, D.DOOR)
        for x, y in ((26, cy - 9), (51, cy - 9), (26, cy + 9), (51, cy + 9)):
            m.set(x, y, D.WALL)
        TR.box(m, 40, cy - 5, 10, 11, D.WALL, D.FLOOR)
        m.set(40, cy, D.DOOR)
        m.set(47, cy - 3, D.CHEST)
        m.hall = (45, cy)
    else:
        TR.round_hut(m, 40, cy, 8, 6, D.WALL, D.FLOOR)
        m.set(32, cy, D.DOOR)
        m.hall = (43, cy)
    for x in range(0, 26):
        if m.tile(x, cy) == D.TREE:
            m.set(x, cy, D.PATH)
    m.lt = site.lt
    return _done(m, (0, cy))


def _lt_folk(game, site, m):
    from .entities import make_monster
    e = game.world.evils[site.lt[0]]
    lt = e.lts[site.lt[1]]
    if lt['dead']:
        return
    lvl = m.level + 2 + 2 * lt['scars']
    o = make_monster(game, lt['k'], m.hall[0], m.hall[1], max(lvl, D.MONSTERS[lt['k']]['min_l']))
    o.name = lt['name'] + (', scarred' if lt['scars'] == 1 else f', scarred {lt["scars"]} times' if lt['scars'] else '')
    o.maxhp = o.hp = int(o.maxhp * (3 + lt['scars']))
    o.lt = site.lt
    o.elite = 2
    from . import bosses as BS
    BS.arm(o)
    m.mons.append(o)
    pool = e.d['hunt']
    for _ in range(3 + random.randint(0, 2)):
        spot = _near_free_any(m, m.hall[0], m.hall[1], 2, 9)
        if spot:
            k = random.choice([k for k in pool if D.MONSTERS[k]['min_l'] <= lvl + 2] or pool[:1])
            m.mons.append(make_monster(game, k, *spot, lvl))


def _near_free_any(m, x, y, lo, hi):
    cells = [(x + dx, y + dy) for dx in range(-hi, hi + 1) for dy in range(-hi, hi + 1) if lo <= max(abs(dx), abs(dy))]
    random.shuffle(cells)
    for c in cells:
        if m.inb(*c) and D.TILES[m.tile(*c)].walk and not m.mon_at(*c) and m.tile(*c) != D.DOOR:
            return c
    return None


def _grave_map(game, site):
    w, h = 40, 24
    m = _base(game, site, w, h)
    cy = h // 2
    from . import tribes as TR
    TR.trail(m, [(0, cy), (19, cy)])
    m.set(20, cy, D.HCAIRN)
    for x, y in ((19, cy - 1), (21, cy - 1), (19, cy + 1), (21, cy + 1)):
        if m.tile(x, y) == D.TREE:
            m.set(x, y, D.GRASS)
    m.signs.append((17, cy - 2, site.hero.upper()[:22]))
    return _done(m, (0, cy))


def on_enter(game, site, m):
    if site.kind == 'hgrave':
        game.msg(f'Stones piled over {site.hero}. A sword is pushed into the ground at the head of them.', 'info')
    elif site.kind == 'lt':
        e, lt = game.world.evils[site.lt[0]], game.world.evils[site.lt[0]].lts[site.lt[1]]
        know(game)['lts'].add(site.lt)
        if lt['dead']:
            game.msg(f'{site.name} stands empty. {lt["name"]} is dead.', 'info')
        else:
            game.msg(f'This is the place of {lt["name"]}, who serves {e.name if e.known else "something far away"}.',
                     'bad')


def describe(game, site):
    if site.kind == 'hgrave':
        return f'A cairn of stones over {site.hero}, who rode out against the darkness and did not come back.'
    e, lt = game.world.evils[site.lt[0]], game.world.evils[site.lt[0]].lts[site.lt[1]]
    if lt['dead']:
        return f'The {lt["place"]} of {lt["name"]}, empty now.'
    return f'The {lt["place"]} of {lt["name"]}, who serves {e.name if e.known else "a darkness with no name yet"}.'


# ------------------------------------------------------------------ the library and the riddles
def scribe_opts(game, opt):
    known = [e for e in game.world.evils if e.known and not e.defeated]
    from .history import PRICE
    return [opt('The dark powers', 'shadow', PRICE)] if known else []


def r_scribe(game, npc, choice):
    if choice != 'shadow':
        return False
    from .history import PRICE, HOUR, price
    p = game.player
    cost = price(game, PRICE)
    if p.gold < cost:
        game.msg('You cannot pay for that.', 'bad')
        return True
    s_id = getattr(game.map, 'sid', None)
    k = know(game)
    pool = [e for e in game.world.evils if e.known and not e.defeated and ('library', e.key, s_id) not in k['read']]
    if not pool:
        game.say(npc, '"We have nothing more on them here. Another library may have."')
        return True
    p.gold -= cost
    game.end_turn(HOUR * 3, True)
    e = random.choice(pool)
    k['read'].add(('library', e.key, s_id))
    if 'library' in k['src'].get(e.key, ()):
        alive = [lt for lt in e.lts if not lt['dead'] and lt['site'] is not None]
        if alive:
            lt = random.choice(alive)
            site = game.world.sites[lt['site']]
            k['lts'].add(site.lt)
            game.maps['over'].seen[site.y * game.maps['over'].w + site.x] = 1
            game.say(npc, f'"Of {e.name}: they say {lt["name"]} holds {site.name} for it. It is on your map now."')
        else:
            game.say(npc, f'"Of {e.name} we have only what you have read already."')
        return True
    game.say(npc, f'"Of {e.name} we keep one page, very old. Here."')
    clue(game, e, 'library', game.loc_name())
    return True


def riddle_whole(game, rk):
    """A Varnish riddle made whole: the Hollow King's truth, and a servant's weakness among the answers."""
    k = know(game)
    if rk == 'king':
        k['king'] = True
    pool = [e for e in game.world.evils if not e.defeated and 'riddle' not in k['src'].get(e.key, ())]
    if pool:
        clue(game, random.choice(pool), 'riddle', game.loc_name())
    from . import varnish as VN
    from . import varnishtexts as VT
    from . import skyseat as SK
    if len(VN.st(game)['whole']) == len(VT.RIDDLES):
        SK.star_key(game)
    SK.check(game)


# ------------------------------------------------------------------ the land, the line under the map, rumours
def wild_keys(game, x, y, lvl):
    """An ambush on his coast: the bound dead."""
    if not his_land(game, x, y) or random.random() > .5:
        return None
    pool = [k for k in ('bound_dead', 'drowned', 'skeleton', 'wight') if D.MONSTERS[k]['min_l'] <= lvl + 2] or ['skeleton']
    return [random.choice(pool) for _ in range(random.randint(2, 3 + lvl // 4))]


def where_line(game, x, y):
    if his_land(game, x, y):
        return "The Hollow King's coast"
    rid = game.world.region_of[y * game.maps['over'].w + x]
    i = held_by(game.world, rid)
    if i is not None:
        e = game.world.evils[i]
        return f'Held by {e.name}' if e.known else 'A land that answers to no king'
    return None


def stats(game, s):
    """A relic you carry: one small power."""
    seen = set()
    for it in game.player.inv:
        if it.k == 'relic' and it.t not in seen:
            seen.add(it.t)
            _n, stat, v, _t = relic_of(it.t)
            s[stat] = s.get(stat, 0) + v


def relic_of(t):
    if t == 'starkey':
        from .skyseat import STARKEY
        return STARKEY
    return SERVANT[t]['relic']


def layer_look(game, x, y):
    """The Shadow layer of the world map: his coast, each servant's mark, the baronies they hold; None elsewhere."""
    w = game.world
    if his_land(game, x, y):
        return (150, 60, 200)
    om = game.maps['over']
    i = y * om.w + x
    tn = getattr(w, 'taint', None)
    if tn and tn[i]:
        e = w.evils[tn[i] - 1]
        return e.fg if e.known else (120, 100, 110)
    if held_by(w, w.region_of[i]) is not None:
        e = w.evils[held_by(w, w.region_of[i])]
        return tuple(c * 6 // 10 for c in e.fg)
    return None


def legend(game):
    w = game.world
    out = [('■', (150, 60, 200), 'his coast')]
    for e in w.evils:
        if e.known and not e.defeated:
            out.append(('■', e.fg, e.short))
    out.append(('Ω', LOOK['lt'][1], 'lieutenant'))
    return out


# ------------------------------------------------------------------ the relic as an item (entities.CRAFT)
def display(game, it):
    return it.name


def lines(game, it):
    name, stat, v, text = relic_of(it.t)
    word = {'res_all': 'to all resistances', 'res_cold': 'resist cold', 'res_fire': 'resist fire', 'res_poison': 'resist poison',
            'res_light': 'resist lightning', 'str': 'strength', 'dex': 'dexterity', 'mana': 'mana'}[stat]
    return [text, f'While you carry it: +{v}{"%" if stat.startswith("res") else ""} {word}.',
            'One of the keys through the mist round the Sky-Seat, the old letters say.' if it.t == 'starkey' else
            'A relic of a fallen servant of the Hollow King: one of the keys through the mist, the old letters say.']


def value(game, it):
    return 0


def glyph(it):
    return '*'


def color(it):
    return (220, 160, 255)


def register():
    from . import entities as EN
    EN.CRAFT.update({'relic': 'shadow'})
    for k, tag in (('winter_wolf', 'lair_wendigo'), ('snow_ape', 'lair_wendigo'), ('ghoul', 'lair_wendigo'),
                   ('frost_spider', 'lair_wendigo'), ('wolf', 'lair_wolf'), ('worg', 'lair_wolf'),
                   ('winter_wolf', 'lair_wolf'), ('jackal', 'lair_wolf'), ('cultist', 'lair_mage'),
                   ('skel_mage', 'lair_mage'), ('imp', 'lair_mage'), ('animated_armour', 'lair_mage'),
                   ('gargoyle', 'lair_mage')):
        if k in D.MONSTERS and tag not in D.MONSTERS[k]['tags'].split():
            D.MONSTERS[k]['tags'] += ' ' + tag


register()
