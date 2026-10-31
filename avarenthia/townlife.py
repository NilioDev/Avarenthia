"""Round 27 (round 6 of old): livelier settlements, and the refugees of the great evils.

Everything shows as a tile or works with a bump. What it adds to the towns that already keep a day (work and home,
the watch, the lamps, the bells):
- Work you can see: woodpiles by the houses that grow through the year and shrink in winter; fields that change
  with the season (furrows in spring, green, gold, stubble, bare in winter).
- Market day brings travelling traders to the square.
- The town reacts to the world: raiders, a war or the mark of a great evil near it bring out more guards, shut the
  doors and send folk home; a war won brings a feast in the square.
- Small happenings to bump into: a brawl at the inn, a runaway pig, a funeral, a pickpocket.
- Each people in its own rhythm: halflings and their meals and hedge lanterns; elves awake at night, archers at the
  butts by day; gnomes diving into their root holes and picking mushrooms at dawn; dwarves by the shift bell; orcs
  sparring, goblins squabbling, the kobolds' hoard growing, lizardfolk basking by day and slow at night and in winter.
- The half-orcs and goblins of the human cities live in a poor quarter by the wall (beggars by day, a night trader
  after dark), and in shanty camps outside the walls.
- Refugees from the lands a great evil holds fill the cities near it: bump one to give a coin or hear their tale.
State: on the map (what is dressed, what happens today); what you were told lives on the player."""
import random

from . import data as D
from .worldgen import cheb

MEALS = (7, 9, 11, 13, 16, 18, 20)          # breakfast, second breakfast, elevenses, luncheon, tea, dinner, supper
SHIFTS = (6, 14, 22)
DAWN = (5, 8)
TRAVELLERS = [('A travelling spice seller', '#e8a050'), ('A pedlar of ribbons and pins', '#e0b0d0'),
              ('A drover with cheeses', '#e8d890'), ('A tinker with pots and pans', '#b8c0c8'),
              ('A cloth merchant from the coast', '#90b8e0'), ('A seller of honey and wax', '#f0c040')]
FEAR = ['They say raiders were seen on the road. Keep your door barred tonight.',
        'More guards on the gate today. Nobody tells us why.', 'My sister will not come to market. Too dangerous, she says.',
        'Shut the shutters, the captain said. So we shut them.']
FEAST = ['The war is won! The lord stands ale for the whole town.', 'A feast in the square tonight. Come and drink to the king!',
         'They say our lads are coming home. Some of them.']
REFUGEE_TALE = {
    'war': 'The dead came up out of the churchyard at {place}. We did not stay to see whose they were.',
    'tribute': 'It came at night for the gold of {place}. When the gold was gone it took the barns, and then the folk.',
    'webs': 'The woods round {place} are white with silk now. People went in after their children and did not come out.',
    'gorvash': 'The war-bands burned {place}. Our lord fled a day before we did.',
    'flood': 'The sea came up the fields at {place}, and something walked in with it.',
    'hunger': 'Folk went missing at {place} all winter. Then we heard it, out in the snow, calling with their voices.',
    'wolves': 'The wolves came off the plain into {place}, in packs as big as a war-band.',
    'sway': 'The new master of {place} hangs those who speak his name. We left in the night with what we could carry.'}
from . import servants as _SV  # noqa: E402
REFUGEE_TALE.update(_SV.TALES)
SHANTY_NAMES = ['Mudside', 'Rag Row', 'the Ditch', 'the Lean-tos', 'Tanners\' Bottom', 'the Gutter Camp', 'Ashpit Lane',
                'the Low Fields']
SLUM_FG = {'orc': '#96b46e', 'goblin': '#86b45a'}
FG = (150, 120, 76)


# ------------------------------------------------------------------ whose place is this
def people(game, m):
    """'human', 'halfling', 'elf', 'dwarf', 'orc', 'gnome', 'kobold', 'goblin', 'gnoll', 'lizard' or None."""
    w = game.world
    sid = getattr(m, 'sid', None)
    if sid is not None:
        s = w.settlements[sid]
        return 'dwarf' if s.kind == 'deephold' else getattr(s, 'race', 'human')
    site = getattr(m, 'site', None)
    if site is None:
        site = next((q.id for q in getattr(w, 'sites', ()) if q.map_key == m.key), None)
    if site is None:
        return None
    kind = w.sites[site].kind
    return {'glade': 'elf', 'gnomes': 'gnome', 'warcamp': 'orc', 'ravine': 'goblin', 'kobolds': 'kobold',
            'gnolls': 'gnoll', 'stilts': 'lizard', 'shanty': 'shanty'}.get(kind)


def _sett(game, m):
    sid = getattr(m, 'sid', None)
    return game.world.settlements[sid] if sid is not None else None


def _hour(game):
    from .towns import hour
    return hour(game)


def _walk(m, x, y):
    return m.inb(x, y) and D.TILES[m.tile(x, y)].walk and not m.mon_at(x, y)


def _ring_ok(m, x, y):
    """Blocking this cell keeps its walkable neighbours joined: they form one unbroken arc round it."""
    ring = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
    w = [m.inb(x + dx, y + dy) and D.TILES[m.tile(x + dx, y + dy)].walk for dx, dy in ring]
    if sum(w) < 3:
        return False
    runs = sum(1 for i in range(8) if w[i] and not w[i - 1])
    return runs <= 1


def _npc(game, m, name, role, fg, x, y, job='any', stay=False, ch='☺', race=None):
    from .entities import make_npc
    n = make_npc(game, name, role, fg, x, y, stay, ch=ch, race=race)
    n.home_pos, n.work_pos, n.job, n.path = (x, y), (x, y), job, []
    n.life = True                                   # one of ours: cleared again when it is over
    m.mons.append(n)
    return n


def _free_near(m, x, y, lo=0, hi=6, pred=None):
    cells = [(x + dx, y + dy) for dy in range(-hi, hi + 1) for dx in range(-hi, hi + 1)
             if lo <= max(abs(dx), abs(dy)) <= hi and _walk(m, x + dx, y + dy) and (pred is None or pred(x + dx, y + dy))]
    return random.choice(cells) if cells else None


def _outdoor(m):
    from .towns import INDOOR
    return lambda x, y: m.tile(x, y) not in INDOOR


# ------------------------------------------------------------------ the look of the year
def frame(game, m):
    """What the map looks like this hour: worked out once a frame."""
    from . import calendar as CAL
    from . import seasons as SE
    se, doy = CAL.season(game.day), SE.doy(game.day)
    start = {'winter': 11, 'spring': 2, 'summer': 5, 'autumn': 8}[se]
    into = ((doy // 30 - start) % 12) * 30 + doy % 30
    return dict(season=se, late=into >= 45, hour=_hour(game), people=getattr(m, 'people', None))


def tiles(fr):
    """The tiles whose look this frame changes."""
    out = {D.FIELD, WOODPILE}
    if fr['people'] == 'halfling':
        out.add(D.HEDGE)
    elif fr['people'] == 'elf':
        out.add(D.TREE)
    return out


def _h(x, y, salt):
    return ((x * 73856093) ^ (y * 19349663) ^ (salt * 83492791)) & 0xffff


def look(game, m, i, lk, fr):
    """Fields by the season, woodpiles by the year, hedge lanterns in a halfling evening, lights in the elves' trees."""
    t = m.t[i]
    ch, fg, bg = lk
    x, y = i % m.w, i // m.w
    se = fr['season']
    if t == D.FIELD:
        late = fr['late']                           # the second half of the season
        if se == 'winter':
            return ('.' if y % 2 else '·'), (150, 136, 116), (34, 28, 22)
        if se == 'spring':
            return (('"' if late else ',') if y % 2 else '.'), ((104, 184, 74) if late else (126, 150, 80)), (34, 28, 14)
        if se == 'summer':
            return ('ⁿ' if y % 2 else '"'), ((214, 190, 70) if late else (150, 190, 70)), (34, 30, 12)
        if not late:
            return ('ⁿ' if y % 2 else '.'), (222, 184, 70), (36, 28, 12)
        return (',' if y % 2 else '.'), (176, 150, 96), (36, 28, 16)
    if t == WOODPILE:
        k = stage(fr)
        return ('-', '=', '≡', '■')[k], (168, 120, 70), (40, 26, 14)
    pp = fr['people']
    if pp == 'halfling' and t == D.HEDGE and (fr['hour'] >= 18 or fr['hour'] < 1) and _h(x, y, 5) % 9 == 0:
        return '°', (255, 214, 120), (40, 34, 10)
    if pp == 'elf' and t == D.TREE and (fr['hour'] >= 20 or fr['hour'] < 4) and _h(x, y, 7) % 13 == 0:
        return '°', (200, 240, 190), bg
    return lk


def stage(fr):
    """How high the woodpile stands: low in spring, highest before winter, burnt down by its end."""
    se, late = fr['season'], fr['late']
    return {'spring': 0, 'summer': 1, 'autumn': 3 if late else 2, 'winter': 1 if late else 2}[se]


# ------------------------------------------------------------------ once per map: what stands there
def dress(game, m):
    if getattr(m, 'life_v', 0) >= 1:
        return
    m.life_v = 1
    pp = people(game, m)
    m.people = pp
    s = _sett(game, m)
    if pp in ('human', 'halfling', 'dwarf', 'orc') and s is not None and s.kind != 'deephold':
        _woodpiles(game, m)
    if pp == 'elf':
        _butts(game, m)
    if pp == 'human' and s is not None and s.is_city and getattr(m, 'grown', None):
        _slum(game, m, s)
    if pp == 'gnome':
        for o in m.mons:
            if o.is_npc and o.role == 'villager' and not hasattr(o, 'work_pos'):
                o.home_pos, o.work_pos, o.path = (o.x, o.y), (o.x, o.y), []


def _woodpiles(game, m):
    """A stack of split logs against the wall by some of the houses."""
    want = 14 if m.w * m.h > 20000 else 6
    cells = []
    for i, t in enumerate(m.t):
        if t != D.GRASS:
            continue
        x, y = i % m.w, i // m.w
        if any(m.inb(x + dx, y + dy) and m.tile(x + dx, y + dy) == D.WALL for dx, dy in ((0, -1), (1, 0), (-1, 0), (0, 1))) \
                and not any(m.inb(x + dx, y + dy) and m.tile(x + dx, y + dy) in (D.DOOR, D.ODOOR, WOODPILE)
                            for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2)):
            cells.append((x, y))
    random.shuffle(cells)
    n = 0
    for x, y in cells:
        if n >= want:
            break
        if _ring_ok(m, x, y) and not m.mon_at(x, y) and \
                not any(m.inb(x + dx, y + dy) and m.tile(x + dx, y + dy) == WOODPILE for dx in range(-6, 7) for dy in range(-6, 7)):
            m.set(x, y, WOODPILE)
            n += 1


def _butts(game, m):
    """Straw targets at the edge of the glade, and two archers who shoot at them by day."""
    cx, cy = getattr(m, 'centre', (m.w // 2, m.h // 2))
    from .towns import town_names
    names = town_names('elf')
    for k in range(2):
        for _ in range(200):
            x, y = cx + random.randint(-22, 22), cy + random.randint(-14, 14)
            if m.inb(x, y) and m.tile(x, y) == D.GRASS and _ring_ok(m, x, y) and not m.mon_at(x, y):
                stand = next(((x + dx, y) for dx in (6, -6, 5, -5, 7, -7) if _walk(m, x + dx, y)), None)
                if stand:
                    m.set(x, y, BUTTS)
                    a = _npc(game, m, f'{names.pop()} the archer', 'villager', '#a8e6a0', stand[0], stand[1], 'archer',
                             race='elf')
                    a.life = False
                    break


def _slum(game, m, s):
    """The poor quarter by the wall, where the half-orcs and goblins of the city live: patched walls, mud lanes."""
    from .towns import town_names
    from .tribes import _names
    cx, cy = getattr(m, 'centre', (m.w // 2, m.h // 2))
    folk = [o for o in m.mons if o.is_npc and o.role == 'villager' and getattr(o, 'job', '') in ('any', 'weaver', 'potter',
                                                                                                   'carter', 'baker')]
    folk.sort(key=lambda o: -cheb(o.home_pos[0], o.home_pos[1], cx, cy))
    far = folk[:max(4, len(folk) // 9)]
    if not far:
        return
    hx, hy = far[0].home_pos
    near = sorted(folk, key=lambda o: cheb(o.home_pos[0], o.home_pos[1], hx, hy))[:max(4, len(folk) // 9)]
    onames, gnames = town_names('orc'), _names('goblin')
    over = getattr(m, 'over', None)
    if over is None:
        m.over = over = {}
    cells = set()
    for k, o in enumerate(near):
        orc = k % 3 != 2
        o.race = 'orc' if orc else 'goblin'
        o.fg = D.hexrgb(SLUM_FG[o.race])
        o.name = (f'{onames.pop()}, a half-orc' if orc else f'{gnames.pop()}, a goblin') if k % 2 else \
            ('A half-orc beggar' if orc else 'A goblin beggar')
        o.job = 'nighttrader' if k == 1 else 'beggar'
        o.role = 'slum'
        if k == 1:
            o.name = f'{gnames.pop() if not orc else onames.pop()}, who trades at night'
        x0, y0 = o.home_pos
        for dy in range(-5, 6):
            for dx in range(-6, 7):
                x, y = x0 + dx, y0 + dy
                if m.inb(x, y):
                    cells.add((x, y))
    for x, y in cells:
        i = y * m.w + x
        t = m.t[i]
        if i in over:
            continue
        if t == D.WALL and _h(x, y, 3) % 3 == 0:
            over[i] = ('▒', (118, 98, 76), (34, 26, 18))
        elif t in (D.PATH, D.GRASS) and _h(x, y, 4) % 2:
            over[i] = (',' if _h(x, y, 6) % 2 else '~', (104, 88, 62), (28, 22, 14))
    m.slum = (hx, hy)
    m._look = None


# ------------------------------------------------------------------ each time you come in
def on_enter(game, m):
    dress(game, m)
    from . import feasts as FE
    FE.on_enter(game, m)
    pp = m.people
    day = game.day
    if getattr(m, 'life_day', None) == day:
        return
    m.life_day = day
    m.mons = [o for o in m.mons if not getattr(o, 'life', False)]
    m.mood = None
    s = _sett(game, m)
    if s is not None and pp in ('human', 'halfling', 'dwarf', 'orc'):
        m.mood = mood(game, s)
        if m.mood == 'fear':
            _call_up(game, m, s)
        refugees(game, m, s)
        from . import feasts as FE
        if FE.has_fair(game, s) and random.random() < .7:
            happening(game, m, s, 'pickpocket')     # the fair draws thieves
        elif random.random() < (.45 if s.is_city else .3):
            happening(game, m, s)
    if pp == 'kobold':
        _hoard(game, m)
    if pp == 'lizard':
        _bask(game, m)


def mood(game, s):
    """'fear' when danger is near, 'feast' after a war won, else None."""
    w = game.world
    if s.event and s.event[0] in ('war', 'raid', 'siege', 'plague', 'bandits'):
        return 'fear'
    if any(getattr(wd, 'hostile', False) and cheb(wd.x, wd.y, s.x, s.y) <= 14 for wd in w.wanderers):
        return 'fear'
    from . import evils as EVL
    for dx, dy in ((0, 0), (8, 0), (-8, 0), (0, 6), (0, -6)):
        x, y = s.x + dx, s.y + dy
        if 0 <= x < game.maps['over'].w and 0 <= y < game.maps['over'].h and EVL.taint_at(game, x, y) is not None:
            return 'fear'
    from . import realms as RL
    R = RL.get(game)
    if R is not None:
        kg = RL.kingdom_of_region(R, s.region)
        if kg is not None and game.day - getattr(kg, 'won_day', -99) <= 7:
            return 'feast'
    return None


def _call_up(game, m, s):
    """Danger near: more of the watch on the streets."""
    from .towns import town_names
    exits = getattr(m, 'exits', None) or [(m.entry[0], m.entry[1], None)]
    for k in range(3 if s.is_city else 2):
        ex, ey = exits[k % len(exits)][:2]
        c = _free_near(m, ex, ey, 1, 5)
        if c:
            gd = _npc(game, m, f'{town_names(getattr(s, "race", "human"))[0]}, called up to the watch', 'guard',
                      D.FACTIONS[s.faction]['fg'] if s.faction in D.FACTIONS else '#b0b8c8', c[0], c[1], 'guard')
            gd.fg = gd.fg if isinstance(gd.fg, tuple) else D.hexrgb(gd.fg)
    game.msg(f'{s.name} is uneasy: more guards on the streets, doors barred, folk keeping indoors.', 'bad')


# ------------------------------------------------------------------ the refugees
def refugee_lands(game, s):
    """The awake servants whose lands lie near this town: [(index, servant)]."""
    from . import shadow as SH
    w = game.world
    out = []
    for idx, e in enumerate(getattr(w, 'evils', ())):
        if e.defeated or not getattr(e, 'awake', False):
            continue
        d = cheb(s.x, s.y, e.x, e.y)
        if SH.reach(e) * 2 < d <= SH.reach(e) * 2 + 40:
            out.append((idx, e))
    return out


def refugees(game, m, s):
    lands = refugee_lands(game, s)
    if not lands or not (s.is_city or s.kind == 'town'):
        return
    from .towns import town_names
    from . import shadow as SH
    names = town_names(getattr(s, 'race', 'human'))
    cx, cy = getattr(m, 'centre', (m.w // 2, m.h // 2))
    n_all = 0
    for idx, e in lands:
        n = min(7, 1 + e.lvl // 2) + (2 if getattr(s, 'kind', '') == 'metropolis' else 0)
        n = n if s.is_city else min(2, n)
        rids = SH.regions_of(game, idx)
        vil = SH._villages(game, rids) if rids else []
        place = random.choice(vil).name if vil else 'home'
        for _ in range(n):
            c = _free_near(m, cx, cy, 2, 10, _outdoor(m))
            if not c:
                break
            r = _npc(game, m, f'{names.pop() if names else "A refugee"}, a refugee from {place}', 'refugee', '#9a96a0',
                     c[0], c[1], 'refugee')
            r.evil, r.place = idx, place
            n_all += 1
    if n_all and not getattr(m, 'refugees_told', None) == game.day:
        m.refugees_told = game.day
        game.msg(f'Refugees sleep in the square of {s.name}, with what they could carry.', 'info')


ROAD_REFUGEES = 6              # at most this many bands on the roads at once (scaled)


def road_refugees(game, s):
    """A village struck by a servant: a band of its folk takes the road to the nearest town or city (great evils
    part 3). Met on the road they talk as the refugees in the towns do."""
    from . import evils as EVL
    from .wanderers import Wanderer, road_path
    from .world import scaled
    w = game.world
    e = EVL.taint_at(game, s.x, s.y)
    if e is None or sum(1 for x in w.wanderers if getattr(x, 'refugee', None) is not None) >= scaled(ROAD_REFUGEES):
        return None
    to = sorted((t for t in w.settlements if t.id != s.id and (t.is_city or t.kind == 'town')),
                key=lambda t: cheb(t.x, t.y, s.x, s.y))
    for t in to[:3]:
        path = road_path(game, s.id, t.id)
        if path and len(path) > 3:
            break
    else:
        return None
    wd = Wanderer(game.new_id(), 'traveler', s.x, s.y)
    wd.ch, wd.fg = '☺', (154, 150, 160)
    wd.name = f'Refugees from {s.name}'
    wd.race = getattr(s, 'race', 'human')
    wd.origin, wd.dest = s.id, t.id
    wd.path, wd.path_i = list(path), 0
    wd.speed = 16
    wd.offer = None
    wd.refugee, wd.evil, wd.place = w.evils.index(e), w.evils.index(e), s.name
    w.wanderers.append(wd)
    return wd


def talk_refugee(game, npc, key='refugee'):
    from . import events as EV
    from . import shadow as SH
    from .money import fmt
    e = game.world.evils[npc.evil]
    lever = SH.SERVANT[e.key]['lever']
    p = game.player
    opts = []
    if not getattr(npc, 'given', False):
        opts.append((f'Give a silver ({fmt(100)})' if p.gold >= 100 else 'Give a silver (you have not got it)',
                     'give' if p.gold >= 100 else None))
    opts += [('Ask what drove them out', 'tale'), ('Go on', 'bye')]
    EV.ask(game, key, npc.name, f'"{REFUGEE_TALE[lever].format(place=npc.place)}"', opts, npc=npc.id)


def r_road_refugee(game, choice, ctx):
    """Refugees met on the road: the same talk, said to the road."""
    wd = next((x for x in game.world.wanderers if x.id == ctx.get('npc')), None)
    if wd is not None:
        r_refugee(game, choice, ctx, wd)


def r_refugee(game, choice, ctx, who=None):
    from . import shadow as SH
    from . import gods as GD
    npc = who or next((o for o in game.map.mons if o.id == ctx.get('npc')), None)
    if npc is None or choice == 'bye':
        return
    p = game.player
    say = (lambda t: game.msg(f'{npc.name}: "{t}"', 'info')) if who is not None else (lambda t: game.say(npc, t))
    if choice == 'give' and p.gold >= 100:
        p.gold -= 100
        npc.given = True
        say(random.choice(['The gods keep you. They have not kept us.', 'Bread for the little ones. Thank you.',
                           'You are kind. Not many are, this far from home.']))
        if getattr(p, 'god', None) == 'solmara':
            GD.gain(game, 1)
        return
    if choice == 'tale':
        e = game.world.evils[npc.evil]
        k = SH.know(game)
        told = p.__dict__.setdefault('refugee_told', set())
        lts = [(npc.evil, j) for j, lt in enumerate(e.lts) if not lt['dead'] and (npc.evil, j) not in k['lts']]
        if lts and npc.id not in told:
            told.add(npc.id)
            lt = random.choice(lts)
            k['lts'].add(lt)
            title = e.lts[lt[1]]['name']
            say(f'We passed the stronghold of {title} on the way. Its servants were on the walls. Keep away from it.')
            game.msg(f'You know where {title}, a lieutenant of {e.name}, keeps. It is marked on your map.', 'gold')
        else:
            say(f'{e.name}. That is what they call it. I hope I never hear the name again.')


# ------------------------------------------------------------------ small happenings
HAPPENINGS = ('brawl', 'pig', 'funeral', 'pickpocket')


def happening(game, m, s, kind=None):
    from .towns import town_names
    names = town_names(getattr(s, 'race', 'human'))
    blds = getattr(m, 'buildings', ())
    inn = next((b for b in blds if b['kind'] == 'inn'), None)
    temple = next((b for b in blds if b['kind'] in ('temple', 'healer')), None)
    kinds = [k for k in HAPPENINGS if (k != 'brawl' or inn) and (k != 'funeral' or temple)]
    kind = kind or random.choice(kinds)
    if kind not in kinds:
        return None
    cx, cy = getattr(m, 'centre', (m.w // 2, m.h // 2))
    if kind == 'brawl':
        x, y, w, h = inn['box']
        cells = [(xx, yy) for yy in range(y + 1, y + h - 1) for xx in range(x + 1, x + w - 1) if _walk(m, xx, yy)]
        if len(cells) < 2:
            return None
        a, b = random.sample(cells, 2)
        for c in (a, b):
            n = _npc(game, m, f'{names.pop()}, in a brawl', 'brawler', '#e07060', c[0], c[1], 'brawler')
            n.home_pos = n.work_pos = a
    elif kind == 'pig':
        c = _free_near(m, cx, cy, 3, 14, _outdoor(m))
        if not c:
            return None
        _npc(game, m, 'A runaway pig', 'runaway', '#f0a8a8', c[0], c[1], 'runaway', ch='p')
    elif kind == 'funeral':
        tx, ty, tw, th = temple['box']
        door = temple.get('door') or (tx + tw // 2, ty + th)
        start = _free_near(m, cx, cy, 8, 16, _outdoor(m)) or (cx, cy)
        for k in range(5):
            c = _free_near(m, start[0], start[1], 0, 2) or start
            n = _npc(game, m, 'The bier, carried' if k == 0 else 'A mourner in black', 'mourner', '#8a8a96',
                     c[0], c[1], 'mourner')
            n.work_pos = _free_near(m, door[0], door[1], 1, 3, _outdoor(m)) or tuple(door)
            n.home_pos = n.work_pos
            n.path = []
        game.msg('A bell tolls slowly: a funeral goes through the streets to the temple.', 'info')
    elif kind == 'pickpocket':
        c = _free_near(m, cx, cy, 4, 12, _outdoor(m))
        if not c:
            return None
        _npc(game, m, 'A quick-fingered lad', 'pickpocket', '#b0a890', c[0], c[1], 'pickpocket')
    m.happening = kind
    return kind


def _hap_tick(game, m):
    p = game.player
    for o in [o for o in m.mons if getattr(o, 'life', False)]:
        role = o.role
        if role == 'runaway':
            from . import ai as AI
            if cheb(o.x, o.y, p.x, p.y) <= 4:
                AI.step_away(game, o)
            elif random.random() < .5:
                game.random_step(o)
        elif role == 'brawler' and random.random() < .06 and game.visible(o.x, o.y):
            game.msg(random.choice(['A stool flies across the inn.', 'Two drinkers roll over a table, swinging.',
                                    '"Say that again!" Crash.']), 'info')
        elif role == 'pickpocket':
            _pickpocket(game, m, o)
        elif role == 'mourner' and (o.x, o.y) == tuple(o.work_pos) and random.random() < .01:
            m.mons = [q for q in m.mons if q.role != 'mourner']
            break


def _pickpocket(game, m, o):
    p = game.player
    if getattr(o, 'took', None) is None:
        if cheb(o.x, o.y, p.x, p.y) <= 1 and p.gold > 50:
            o.took = min(p.gold // 20, 400)
            p.gold -= o.took
            game.msg('Someone brushes past you. Your purse feels lighter.', 'bad')
            ex = getattr(m, 'exits', None) or [(m.entry[0], m.entry[1], None)]
            o.work_pos = o.home_pos = tuple(random.choice(ex)[:2])
            o.path = []
        else:
            o.work_pos = o.home_pos = (p.x, p.y)
    elif cheb(o.x, o.y, *o.work_pos) <= 1:
        m.mons.remove(o)                            # gone with your coin


def talk_life(game, npc):
    """Bumping into one of the happenings."""
    p = game.player
    m = game.map
    role = npc.role
    if role == 'brawler':
        m.mons = [o for o in m.mons if o.role != 'brawler']
        if not getattr(m, 'brawl_paid', None) == game.day:
            m.brawl_paid = game.day
            p.gold += 50
            p.food = min(p.food + 150, 1200) if hasattr(p, 'food') else 0
            game.msg('You pull the two apart and sit them down at different ends of the room. The innkeeper stands you '
                     'a bowl of stew and pushes a few coppers over: "for the furniture you saved".', 'good')
        return True
    if role == 'runaway':
        m.mons.remove(npc)
        p.gold += 100
        game.msg('You catch the pig by a hind leg. Its owner comes running, red in the face, and gives you a silver for '
                 'your trouble.', 'good')
        return True
    if role == 'mourner':
        from . import gods as GD
        if getattr(p, 'god', None) and not getattr(npc, 'bowed', False):
            npc.bowed = True
            GD.gain(game, 1)
        game.msg('You bow your head as the bier goes by. A woman in black presses a funeral cake into your hand.', 'info')
        if hasattr(p, 'food') and not getattr(m, 'cake', None) == game.day:
            m.cake = game.day
            p.food = min(p.food + 120, 1200)
        return True
    if role == 'pickpocket':
        took = getattr(npc, 'took', None)
        m.mons.remove(npc)
        if took:
            p.gold += took + 30
            game.msg('You grab the lad by the collar. Out comes your coin, and a little more he lifted from someone '
                     'else. He wriggles free and is gone.', 'good')
        else:
            game.msg('The lad gives you a hurt look and walks off whistling. You keep a hand on your purse.', 'info')
        return True
    return False


# ------------------------------------------------------------------ the slum: beggars and the night trader
def talk_slum(game, npc):
    from . import events as EV
    from . import tradegoods as TG
    from .money import fmt
    from .towns import is_night
    p = game.player
    if npc.job == 'nighttrader':
        if not is_night(game):
            game.say(npc, 'Not now. Come back after dark, and come alone.')
            return
        n = p.cargo.get('lotus', 0)
        price = round(TG.cove_price() * .6)
        opts = [(f'Sell your black lotus ({n} for {fmt(n * price)})', 'lotus')] if n else []
        EV.ask(game, 'slum', npc.name, '"Something the Watch would not like? I pay, not as well as the cove. But the cove is '
               'far."' if n else '"Nothing for me tonight? Then nothing."', opts + [('Go on', 'bye')], npc=npc.id, price=price)
        return
    opts = [(f'Give a few coppers ({fmt(10)})', 'give' if p.gold >= 10 else None), ('Go on', 'bye')]
    EV.ask(game, 'slum', npc.name, random.choice([
        '"Spare a copper? They do not let our sort work the docks any more."',
        '"A copper for an old soldier? Fought for the king, I did. Which one, I forget."',
        '"Coin? No? Then keep walking, the Watch does not like you stopping here."']), opts, npc=npc.id)


def r_slum(game, choice, ctx):
    p = game.player
    if choice == 'lotus':
        n = p.cargo.pop('lotus', 0)
        p.cost_basis.pop('lotus', None)
        got = n * ctx.get('price', 0)
        p.gold += got
        from .money import fmt
        game.msg(f'The trader weighs the lotus in his palm and counts out {fmt(got)} in mixed coin.', 'gold')
        from . import crime as CR
        CR.commit(game, 1, 'trading black lotus', witnessed=.15)
    elif choice == 'give' and p.gold >= 10:
        p.gold -= 10
        game.msg('The coppers vanish into a ragged sleeve. A nod, and nothing more.', 'info')
        if getattr(p, 'god', None) == 'solmara' and random.random() < .2:
            from . import gods as GD
            GD.gain(game, 1)


# ------------------------------------------------------------------ the peoples' rhythms: where to go
def target(game, npc):
    """A spot for this person this hour, by their people's rhythm; None leaves it to the town's own day."""
    m = game.map
    job = getattr(npc, 'job', 'any')
    if job in ('guard', 'lamplighter'):
        return None
    if job == 'feast':
        return npc.home_pos
    from . import feasts as FE
    spot = FE.target(game, npc)
    if spot:
        return spot
    h = _hour(game)
    if job == 'refugee':
        return npc.home_pos
    if job in ('mourner', 'brawler', 'pickpocket', 'runaway'):
        return npc.work_pos
    if job == 'beggar':
        if 8 <= h < 19:
            spot = getattr(npc, 'beg_pos', None)
            if spot is None:
                cx, cy = getattr(m, 'centre', (m.w // 2, m.h // 2))
                spot = npc.beg_pos = _free_near(m, cx, cy, 5, 12, _outdoor(m)) or npc.home_pos
            return spot
        return npc.home_pos
    if job == 'nighttrader':
        return _free_lane(m, npc) if (h >= 21 or h < 4) else npc.home_pos
    pp = getattr(m, 'people', None)
    if getattr(m, 'mood', None) == 'fear' and npc.id % 2 and job != 'archer':
        return npc.home_pos                         # danger near: half the town keeps indoors
    if getattr(m, 'mood', None) == 'feast' and 17 <= h < 23 and npc.id % 3:
        cx, cy = getattr(m, 'centre', (m.w // 2, m.h // 2))
        spot = getattr(npc, 'feast_pos', None)
        if spot is None:
            spot = npc.feast_pos = _free_near(m, cx, cy, 1, 7, _outdoor(m)) or npc.home_pos
        return spot
    if pp == 'halfling' and h in MEALS and job != 'child':
        from .towns import shelter
        return shelter(game, npc) if npc.id % 2 == 0 else npc.home_pos
    if pp == 'elf':
        if job == 'archer':
            return npc.work_pos if 7 <= h < 18 else npc.home_pos
        if h >= 20 or h < 3:                         # the elves wake at night: singing under the trees
            spot = getattr(npc, 'song_pos', None)
            if spot is None:
                cx, cy = getattr(m, 'centre', (m.w // 2, m.h // 2))
                spot = npc.song_pos = _free_near(m, cx, cy, 1, 8, _outdoor(m)) or npc.home_pos
            return spot
        if 9 <= h < 17:
            return npc.home_pos                      # the day is quiet in a glade
    if pp == 'gnome' and DAWN[0] <= h < DAWN[1]:
        spot = getattr(npc, 'shroom_pos', None)
        if spot is None:
            hx, hy = npc.home_pos
            spot = npc.shroom_pos = _free_near(m, hx, hy, 3, 10, lambda x, y: any(
                m.inb(x + a, y + b) and m.tile(x + a, y + b) == D.TREE for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))) or npc.home_pos
        return spot
    if pp == 'dwarf' and job not in ('child',):
        shift = npc.id % 3
        start = SHIFTS[shift]
        into = (h - start) % 24
        if into < 8:
            return npc.work_pos
        if into < 10:                                # after the shift: the ale hall
            from .towns import shelter
            return shelter(game, npc) if npc.id % 2 == 0 else npc.home_pos
        return npc.home_pos
    return None


def _free_lane(m, npc):
    spot = getattr(npc, 'lane_pos', None)
    if spot is None:
        hx, hy = npc.home_pos
        spot = npc.lane_pos = _free_near(m, hx, hy, 2, 6, _outdoor(m)) or npc.home_pos
    return spot


# ------------------------------------------------------------------ every turn in a settlement
def tick(game, m):
    pp = getattr(m, 'people', None)
    if pp is None and getattr(m, 'life_v', 0) == 0:
        return
    h = _hour(game)
    _hap_tick(game, m)
    if pp == 'dwarf' and h in SHIFTS and getattr(m, 'bell_hour', None) != (game.day, h):
        m.bell_hour = (game.day, h)
        game.msg('The shift bell rings down the halls: one shift goes down to the mine, the other comes up to the ale.',
                 'info')
    elif pp == 'halfling' and h in MEALS and getattr(m, 'meal_hour', None) != (game.day, h) and h != 7:
        m.meal_hour = (game.day, h)
        word = {9: 'second breakfast', 11: 'elevenses', 13: 'luncheon', 16: 'tea', 18: 'dinner', 20: 'supper'}[h]
        game.msg(f'Time for {word}: half the town hurries home or to the inn.', 'info')
    elif pp == 'halfling' and h >= 19 and random.random() < .2:
        for i, t in enumerate(m.t):                 # round doors shut early
            if t == D.ODOOR and random.random() < .2:
                x, y = i % m.w, i // m.w
                if not m.mon_at(x, y) and (x, y) != (game.player.x, game.player.y):
                    m.t[i] = D.DOOR
    elif pp == 'elf' and h == 20 and getattr(m, 'song_day', None) != game.day:
        m.song_day = game.day
        game.msg('Lights wake in the trees, and the elves begin to sing.', 'info')
    if pp == 'gnome':
        _shy(game, m)
    elif pp == 'orc' and getattr(m, 'site', None) is not None:
        _spar(game, m)
    elif pp == 'goblin':
        _squabble(game, m)
    if getattr(m, 'mood', None) == 'fear' and random.random() < .04:
        for i, t in enumerate(m.t):
            if t == D.ODOOR and random.random() < .15:
                x, y = i % m.w, i // m.w
                if not m.mon_at(x, y) and (x, y) != (game.player.x, game.player.y):
                    m.t[i] = D.DOOR
    if getattr(m, 'mood', None) and random.random() < .03:
        p = game.player
        near = [o for o in m.mons if o.is_npc and o.role == 'villager' and cheb(o.x, o.y, p.x, p.y) <= 6
                and game.visible(o.x, o.y)]
        if near:
            game.say(random.choice(near), random.choice(FEAR if m.mood == 'fear' else FEAST))
    if getattr(m, 'mood', None) == 'feast' and h == 17 and getattr(m, 'feast_told', None) != game.day:
        m.feast_told = game.day
        game.msg('Tables go up in the square, and the ale comes out: the town keeps a feast for the war won.', 'good')


def _shy(game, m):
    """Gnomes dive into their root holes when a big stranger comes near, and come out again later."""
    p = game.player
    if getattr(p, 'race', '') == 'gnome' or game.flags.get(f'gnomes{getattr(m, "site", -1)}'):
        return
    hid = m.__dict__.setdefault('hidden_gnomes', [])
    for o in [o for o in m.mons if o.is_npc and o.role == 'villager' and getattr(o, 'race', '') == 'gnome']:
        if cheb(o.x, o.y, p.x, p.y) <= 3 and random.random() < .5:
            m.mons.remove(o)
            hid.append((o, game.turn + random.randint(30, 60)))
            if game.visible(o.x, o.y):
                game.msg('A gnome squeaks and dives into a hole among the roots.', 'info')
    for pair in list(hid):
        o, back = pair
        if game.turn >= back and cheb(o.home_pos[0], o.home_pos[1], p.x, p.y) > 6 and _walk(m, *o.home_pos):
            o.x, o.y = o.home_pos
            m.mons.append(o)
            hid.remove(pair)


def _spar(game, m):
    if random.random() > .03:
        return
    folk = [o for o in m.mons if o.is_npc and o.role == 'tribe' and getattr(o, 'tjob', '') == 'folk' and o.foe
            and game.visible(o.x, o.y)]
    if len(folk) >= 2:
        a = random.choice(folk)
        b = min((o for o in folk if o is not a), key=lambda o: cheb(o.x, o.y, a.x, a.y))
        c = _free_near(m, a.x, a.y, 1, 1)
        if c and cheb(a.x, a.y, b.x, b.y) <= 10:
            b.x, b.y = c
            game.msg('Two orcs spar with blunted axes, roaring with laughter at every blow.', 'info')


def _squabble(game, m):
    if random.random() > .03:
        return
    folk = [o for o in m.mons if o.is_npc and o.role == 'tribe' and game.visible(o.x, o.y)]
    if len(folk) >= 2:
        a, b = random.sample(folk, 2)
        game.msg(random.choice(['Two goblins squabble over a shiny buckle; one bites the other.',
                                'A goblin snatches a bone from another, and the chase is on.',
                                'Goblins shriek at each other over a dented pot.']), 'info')
        game.random_step(a)
        game.random_step(b)


def _hoard(game, m):
    """The kobolds' hoard grows: more shiny things on the heap each time you come."""
    from .tribes import oval
    last = getattr(m, 'hoard_day', None)
    m.hoard_day = game.day
    if last is None:
        return
    grow = min(12, (game.day - last) // 3)
    if grow <= 0:
        return
    ring = [c for c in oval(50, 28, 13, 6) - oval(50, 28, 9, 4) if m.inb(*c) and m.tile(*c) == D.FLOOR and not m.mon_at(*c)]
    random.shuffle(ring)
    for x, y in ring[:grow]:
        m.set(x, y, D.GLITTER)
    if ring[:grow]:
        game.msg('The hoard has grown since you were here: more shiny things on the heap.', 'info')


def _bask(game, m):
    """By day the lizardfolk lie in the sun on the open ground; at night they are slow."""
    from .towns import is_night
    if is_night(game):
        return
    for o in m.mons:
        if o.is_npc and o.role == 'tribe' and getattr(o, 'tjob', '') == 'folk' and random.random() < .6:
            c = _free_near(m, o.x, o.y, 1, 6, lambda x, y: m.tile(x, y) in (D.GRASS, D.SAND, D.PATH))
            if c:
                o.x, o.y = c
                o.name = 'A lizardfolk, basking in the sun'


def sluggish(game):
    """Lizardfolk at night and in winter: cold blood, slow limbs."""
    from .towns import is_night
    from . import calendar as CAL
    return is_night(game) or CAL.season(game.day) == 'winter'


# ------------------------------------------------------------------ the market day's travellers
def market_day(game, m):
    """On market day, from eight to five, travelling traders stand in the square of a human town."""
    from .towns import day_kind
    from . import feasts as FE
    h = _hour(game)
    s = _sett(game, m)
    on = (day_kind(game) == 'market' or (s is not None and FE.has_fair(game, s))) and 8 <= h < 17
    have = [o for o in m.mons if getattr(o, 'traveller', False)]
    if on and not have and getattr(m, 'travel_day', None) != game.day:
        m.travel_day = game.day
        trader = next((o for o in m.mons if o.is_npc and o.role == 'market'), None)
        if trader is None:
            return
        s = _sett(game, m)
        k = 4 if s is not None and s.is_city else 2
        for nm, fg in random.sample(TRAVELLERS, k):
            c = _free_near(m, trader.x, trader.y, 2, 9, _outdoor(m))
            if not c:
                break
            t = _npc(game, m, nm, 'market', fg, c[0], c[1], 'trader', stay=True)
            t.traveller = True
            stall = _free_near(m, c[0], c[1], 1, 1, _outdoor(m))
            if stall:
                over = getattr(m, 'over', None)
                if over is None:
                    m.over = over = {}
                over[stall[1] * m.w + stall[0]] = ('▄', D.hexrgb(fg), (40, 30, 20))
                t.stall = stall
        m._look = None
    elif not on and have:
        for t in have:
            st_ = getattr(t, 'stall', None)
            if st_ and getattr(m, 'over', None):
                m.over.pop(st_[1] * m.w + st_[0], None)
        m.mons = [o for o in m.mons if not getattr(o, 'traveller', False)]
        m._look = None


# ------------------------------------------------------------------ shanty camps outside the cities
def place_shanties(game, m, world):
    """Outside each human city, a camp of lean-tos where the half-orcs and goblins live who are not let in."""
    from .sites import Site
    state = random.getstate()
    random.seed(game.seed * 7919 + 27)
    try:
        taken = {(s.x, s.y) for s in world.settlements} | {(q.x, q.y) for q in world.sites}
        names = SHANTY_NAMES[:]
        random.shuffle(names)
        for s in world.settlements:
            if not s.is_city or getattr(s, 'race', 'human') != 'human':
                continue
            cands = [(s.x + dx, s.y + dy) for dx in range(-5, 6) for dy in range(-5, 6) if 3 <= max(abs(dx), abs(dy))]
            random.shuffle(cands)
            for x, y in cands:
                if not m.inb(x, y) or (x, y) in taken:
                    continue
                t = m.tile(x, y)
                if t not in (D.GRASS, D.HILLS, D.SAND) or any(cheb(x, y, a, b) < 2 for a, b in taken):
                    continue
                nm = f'{names.pop() if names else "the Lean-tos"} by {s.name}'
                st_ = Site(len(world.sites), 'shanty', x, y, nm[0].upper() + nm[1:])
                st_.faction = s.faction
                st_.city = s.id
                world.sites.append(st_)
                taken.add((x, y))
                break
    finally:
        random.setstate(state)


def shanty_map(game, site):
    """Lean-tos of driftwood and hides round a fire, a midden, a few goats; half-orcs and goblins, a beggar, a trader
    who deals at night."""
    from .entities import GameMap
    from .towns import town_names, embed, place_lamps
    from .tribes import _names, round_hut, fire
    W, H = 60, 36
    m = GameMap(site.map_key, 'town', site.name, W, H, D.GRASS)
    m.radius, m.sid, m.hid, m.signs = 60, None, None, []
    m.site = site.id
    for i in range(len(m.t)):
        if random.random() < .04:
            m.t[i] = D.TREE
    cy = H // 2
    for x in range(0, W // 2 + 4):
        m.set(x, cy, D.PATH)
    m.entry = (0, cy)
    cx = W // 2
    huts = [(cx - 12, cy - 7), (cx - 2, cy - 9), (cx + 9, cy - 7), (cx - 12, cy + 7), (cx - 1, cy + 9), (cx + 10, cy + 6),
            (cx + 18, cy)]
    homes = []
    for hx, hy in huts:
        round_hut(m, hx, hy, 3, 2, D.HIDE, D.PLANK)
        door = (hx, hy + (2 if hy < cy else -2))
        m.set(*door, D.PLANK)
        for y in range(min(door[1], cy), max(door[1], cy) + 1):
            if m.tile(hx, y) in (D.GRASS, D.TREE):
                m.set(hx, y, D.PATH)
        homes.append((hx, hy))
    for x in range(cx - 14, cx + 20):
        if m.tile(x, cy) in (D.GRASS, D.TREE):
            m.set(x, cy, D.PATH)
    m.lights, m.glows = [], []
    fire(m, cx + 4, cy - 2)
    for x, y in ((cx - 6, cy + 3), (cx - 5, cy + 3), (cx - 6, cy + 4)):
        m.set(x, y, D.MIDDEN)
    onames, gnames = town_names('orc'), _names('goblin')
    folk = []
    for k, (hx, hy) in enumerate(homes):
        orc = k % 3 != 1
        nm = f'{onames.pop()}, a half-orc' if orc else f'{gnames.pop()}, a goblin'
        o = _npc(game, m, nm, 'villager', SLUM_FG['orc' if orc else 'goblin'], hx, hy, 'any', race='orc' if orc else 'goblin')
        o.life = False
        o.work_pos = (cx + random.randint(-8, 8), cy + random.choice((-1, 1)))
        folk.append(o)
    folk[0].role, folk[0].job, folk[0].name = 'slum', 'beggar', 'A half-orc beggar'
    folk[1].role, folk[1].job, folk[1].name = 'slum', 'nighttrader', f'{gnames.pop()}, who trades at night'
    from .entities import make_npc
    for x, y in ((cx + 14, cy + 4), (cx + 15, cy + 5)):
        if _walk(m, x, y):
            m.mons.append(make_npc(game, 'A goat', 'livestock', '#c8b890', x, y, False, ch='g'))
    m.centre = (cx, cy)
    m.portal_pos = (cx, cy)
    m.people = 'shanty'
    m.life_v = 1
    return embed(m, 96, 62)


def describe(site):
    return ('A shanty camp outside the city walls: lean-tos of hides and driftwood, where the half-orcs and goblins '
            'live whom the city does not let in.')


# ------------------------------------------------------------------ talking
def talk(game, npc):
    role = npc.role
    if role == 'refugee':
        talk_refugee(game, npc)
        return True
    if role == 'slum':
        talk_slum(game, npc)
        return True
    if role in ('brawler', 'runaway', 'mourner', 'pickpocket'):
        return talk_life(game, npc)
    if role == 'feast':
        from . import feasts as FE
        return FE.talk(game, npc)
    return False


def _register():
    from . import events as EV
    EV.RESOLVERS['refugee'] = r_refugee
    EV.RESOLVERS['roadrefugee'] = r_road_refugee
    EV.RESOLVERS['slum'] = r_slum


WOODPILE, BUTTS = D.WOODPILE, D.BUTTS
_register()
