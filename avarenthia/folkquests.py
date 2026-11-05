"""Folk in need (round 46, "Folk in need" in docs/plan.md, part A): ordinary people in the settlements with a need that
hangs on something real in this world, the steps to help, the rewards and the favours. The lists: `folkdata.py`.

- Who: 0 to 2 people with a need in each settlement (`world.needs`: sid -> [need]); on the map a giver stands about
  with the `!` of people who have work (role 'folk'); passing near, they say their need in the log; a bump talks.
- A need: who (name, trade, people), a motive, where it comes from (`src`: beasts, nest, named, news, season, scarce,
  realm, old, kin, trade, feast, people, watch) and 1-4 steps from verbs the game has: kill (a group on the world map),
  clear (the chief of a nest), hunt (a named enemy), find (a keepsake at the bottom of a dungeon), go (word to a
  settlement), seat (word to a lord's seat), watch (a night in the town), bring (goods), dish (something cooked).
- Taken, it is a Mission of kind 'folk' (the Jobs tab and layer show it); its steps are in `m.data['steps']`.
- Rewards: small coin and standing in the town (missions.complete), and one thing fitting the giver: a favour (a token
  in the pack, shown once in a window that exists already), something of their own, a rumour of a real place, or a
  step in the bestiary. Who you helped lives on the player (`p.folk`).
- Part B (round 47) adds the twists, who remembers you, follow-ups, what happens when nobody helps, and the seeds."""
import random

from . import data as D
from . import folkdata as FD
from .worldgen import cheb
_MON_NAMES = set()

NEAR_BEAST = 30
NEAR_PLACE = 45
OFFER_DAYS = (6, 10)


def store(game):
    return game.world.__dict__.setdefault('needs', {})


def helped(game):
    return game.player.__dict__.setdefault('folk', {})


def people_of(s):
    return 'dwarf' if s.kind == 'deephold' else getattr(s, 'race', 'human')


# ------------------------------------------------------------------ what the world gives to worry about
def _beasts(game, s):
    w = game.world
    return [wd for wd in w.wanderers if wd.kind == 'monsters' and getattr(wd, 'hostile', True) and wd.mission is None
            and wd.group and cheb(wd.x, wd.y, s.x, s.y) <= NEAR_BEAST]


def _nests(game, s):
    from . import jobs as JB
    tags = set(JB.NEST_TAGS) | {'warren', 'snakeruin', 'gloam', 'grotto'}
    return [d for d in game.world.dungeons.values() if d.tag in tags and d.boss and cheb(d.x, d.y, s.x, s.y) <= NEAR_PLACE
            and not getattr(d, 'site', None)]


def _named(game, s):
    from . import named as NM
    return [n for n in NM.alive(game) if cheb(n.x, n.y, s.x, s.y) <= NEAR_PLACE]


def _dungeons(game, s):
    return [d for d in game.world.dungeons.values() if d.relic is None and not d.main and getattr(d, 'site', None) is None
            and d.depth >= 1 and cheb(d.x, d.y, s.x, s.y) <= NEAR_PLACE]


def _towns(game, s):
    return [o for o in game.world.settlements if o.id != s.id and 6 <= cheb(o.x, o.y, s.x, s.y) <= NEAR_PLACE]


def _seats(game, s):
    return [h for h in game.world.holds if cheb(h.x, h.y, s.x, s.y) <= NEAR_PLACE]


def _taken(game, key, value):
    for lst in store(game).values():
        for nd in lst:
            if any(st.get(key) == value for st in nd['steps']):
                return True
    from . import missions as MS
    return any(m.kind == 'folk' and any(st.get(key) == value for st in m.data['steps']) for m in MS.active(game))


def sources(game, s, trade, pp):
    """(src, motive, steps, line) for each need this world gives this person now."""
    from . import calendar as CAL
    from . import jobs as JB
    out = []
    for wd in _beasts(game, s)[:1]:
        if not _taken(game, 'wd', wd.id):
            what = beast_name(wd.name)
            out.append(('beasts', 'safety', [dict(v='kill', wd=wd.id, x=wd.x, y=wd.y, name=wd.name)],
                        f'{what[0].upper() + what[1:]}, out to the {_dir(s, wd.x, wd.y)}. '
                        + random.choice(['It takes a sheep every night.', 'My son went after it and came back bleeding.',
                                         'Nobody dares go to the fields.'])))
    for d in _nests(game, s)[:1]:
        if not _taken(game, 'did', d.id):
            out.append(('nest', 'safety', [dict(v='clear', did=d.id, boss=d.boss, name=d.name)],
                        f"Things crawl out of {JB.the(d.name)} at night, more each week. Kill what rules down there, "
                        f"the {D.MONSTERS[d.boss]['name'].lower()}, and they will scatter."))
    for n in _named(game, s)[:2]:
        if not _taken(game, 'nid', n.id):
            out.append(('named', 'honour' if pp == 'dwarf' else 'safety', [dict(v='hunt', nid=n.id, name=n.name)],
                        f'{n.name} again. Everybody knows that name round here. Somebody has to finish it.'))
    ev = getattr(s, 'event', None)
    if ev and ev[0] in FD.NEWS_NEED:
        good, line = FD.NEWS_NEED[ev[0]]
        out.append(('news', 'health' if good == 'medicine' else 'safety', [dict(v='bring', good=good, qty=2)], line))
    se = CAL.season(game.day)
    for good, line in FD.SEASON_NEED.get(se, []):
        out.append(('season', 'health', [dict(v='bring', good=good, qty=random.randint(1, 2))], line))
    low = [g for g, v in s.market.items() if g in D.GOODS and v[1] and v[0] < v[1] * .35]
    if low:
        g = random.choice(low)
        out.append(('scarce', 'property', [dict(v='bring', good=g, qty=2)],
                    f"No {D.GOODS[g]['name'].lower()} on the market for weeks. Bring me some from another town, and I "
                    'will pay what I can.'))
    if trade in FD.TRADE_NEED:
        g, line = FD.TRADE_NEED[trade]
        out.append(('trade', 'tools', [dict(v='bring', good=g, qty=random.randint(1, 3))], line))
    fest = JB.next_festival(game.day)
    if fest and 0 <= fest[0] - game.day <= 12:
        g, what = random.choice(FD.FEAST_NEED)
        out.append(('feast', 'feast', [dict(v='bring', good=g, qty=1)],
                    f'{what.format(feast=fest[1])[0].upper() + what.format(feast=fest[1])[1:]}: that is all I ask. '
                    'Without it the feast is no feast.'))
    seats = _seats(game, s)
    if seats:
        h = random.choice(seats)
        out.append(('realm', 'family', [dict(v='seat', hid=h.id, name=h.title)],
                    f'My boy was taken for the levy, to {h.title}. Take him this word from his mother, and tell me how '
                    'he fares.'))
    ds = _dungeons(game, s)
    if ds:
        d = random.choice(ds)
        thing = random.choice(["grandfather's sword", 'a silver locket', 'my brother\'s ring', 'the old family seal'])
        out.append(('old', 'peace', [dict(v='find', did=d.id, relic=thing, name=d.name)],
                    f'{thing[0].upper() + thing[1:]} lies at the bottom of {JB.the(d.name)}, where it was lost. I cannot '
                    'rest while it lies there.'))
    ts = _towns(game, s)
    if ts:
        o = random.choice(ts)
        kin = random.choice(['my sister', 'my old father', 'my daughter', 'my brother'])
        out.append(('kin', 'family', [dict(v='go', sid=o.id, name=o.name, who=kin)],
                    f'{kin[0].upper() + kin[1:]} lives in {o.name} and has not written since the thaw. Go and see, and '
                    'tell me how things stand.'))
    if s.kind in ('hamlet', 'village', 'town') and pp in ('human', 'halfling', 'orc'):
        out.append(('watch', 'safety', [dict(v='watch')],
                    'Something takes the hens at night, and I never see what. Keep watch one night, will you?'))
    for verb, thing, line in FD.PEOPLE_NEED.get(pp, []):
        st = None
        if verb == 'find' and ds:
            d = random.choice(ds)
            st = dict(v='find', did=d.id, relic=thing, name=d.name)
            line = line.format(place=JB.the(d.name))
        elif verb == 'go' and ts:
            o = random.choice(ts)
            st = dict(v='go', sid=o.id, name=o.name, who='the keeper' if pp == 'elf' else 'the reeve')
            line = line.format(town=o.name)
        elif verb in ('hunt', 'kill'):
            ns, bs = _named(game, s), _beasts(game, s)
            if verb == 'hunt' and ns:
                n = ns[0]
                st, line = dict(v='hunt', nid=n.id, name=n.name), line.format(beast=n.name)
            elif bs:
                wd = bs[0]
                st, line = dict(v='kill', wd=wd.id, x=wd.x, y=wd.y, name=wd.name), line.format(beast=wd.name)
        elif verb == 'bring':
            st = dict(v='bring', good=thing, qty=1)
        elif verb == 'dish':
            st = dict(v='dish')
        if st:
            out.append(('people', 'family' if verb in ('find', 'go') else 'honour' if verb in ('hunt', 'kill') else 'skill',
                        [st], line))
    return out


def _dir(s, x, y):
    from .engine import dir_name
    return dir_name(x - s.x, y - s.y)


def journey(game, s, steps):
    """Now and then a need is a journey: first word to kin in another town who knows where the thing went."""
    if len(steps) == 1 and steps[0]['v'] in ('find', 'clear') and random.random() < .3:
        ts = _towns(game, s)
        if ts:
            o = min(ts, key=lambda t: cheb(t.x, t.y, s.x, s.y))
            return [dict(v='go', sid=o.id, name=o.name, who='a cousin who saw it last')] + steps
    return steps


def make(game, s, avoid=(), seed=None, twist=None):
    """A new need in this settlement, or None: now and then one of the world's seeds, else made from what is here."""
    from .races import random_name
    pp = people_of(s)
    givers = FD.GIVERS.get(pp) or FD.GIVERS['human']
    trade, title = random.choice(givers)
    sd = None
    if seed is not None or random.random() < .3:
        sd = from_seed(game, s, pp, seed)
    if sd:
        src, motive, steps, line, trade, title = 'seed', sd['motive'], sd['steps'], sd['line'], sd['trade'], sd['title']
        twist = twist or sd['twist']
    else:
        srcs = sources(game, s, trade, pp)
        srcs = [x for x in srcs if x[0] not in avoid] or srcs
        if not srcs:
            return None
        rare = {'beasts': 2, 'nest': 1, 'named': 2, 'news': 3, 'people': 3, 'trade': 2, 'season': 1.5, 'scarce': 1.5}
        src, motive, steps, line = random.choices(srcs, [rare.get(x[0], 1) for x in srcs])[0]
        steps = journey(game, s, steps)
        if twist is None and random.random() < .33:
            fit = [k for k, v in FD.TWISTS.items() if any(st['v'] in v[0] for st in steps)]
            twist = random.choice(fit) if fit else None
    gender = random.choice(['male', 'female'])
    if any(w in title for w in ('wife', 'daughter', 'woman', 'alewife')):
        gender = 'female'
    elif any(w in title for w in ("son", 'nephew', 'fisherman', 'watchman')):
        gender = 'male'
    first = random_name(FD.PEOPLE_RACE.get(pp, pp), gender, family=False)
    danger = sum({'kill': 2, 'clear': 3, 'hunt': 3, 'find': 2}.get(st['v'], 1) for st in steps)
    return dict(id=game.new_id(), sid=s.id, name=first, title=f'{first}, {title}', gender=gender, people=pp, trade=trade,
                motive=motive, src=src, line=line, steps=steps, made=game.day,
                until=game.day + random.randint(*OFFER_DAYS), coin=(4 + 5 * danger + random.randint(0, 6)) * 100,
                reward=FD.TRADE_REWARD.get(trade, 'rumour'), twist=twist, seed=sd['seed'] if sd else None,
                hint=FD.TWIST_HINT.get(twist) if twist and random.random() < .5 else None)


# ------------------------------------------------------------------ the seeds
def world_seeds(game):
    """The 20 to 25 seeds this world has, by index into folkdata.SEEDS; those used are struck off."""
    w = game.world
    if 'folk_seeds' not in w.__dict__:
        rnd = random.Random(getattr(w, 'seed', 0) * 31 + 47)
        w.folk_seeds = rnd.sample(range(len(FD.SEEDS)), rnd.randint(20, 25))
        w.folk_seeds_used = []
    return [i for i in w.folk_seeds if i not in w.folk_seeds_used]


def seed_fits(game, s, pp, rule):
    words = rule.split()
    peoples = [x for x in words if x in FD.GIVERS]
    kinds = [x for x in words if x in ('hamlet', 'village', 'town', 'city', 'metropolis', 'deephold')]
    if peoples and pp not in peoples or kinds and s.kind not in kinds:
        return False
    from . import calendar as CAL
    seasons = [x for x in words if x in ('winter', 'spring', 'summer', 'autumn')]
    if seasons and CAL.season(game.day) not in seasons:
        return False
    if 'temple' in words and 'temple' not in s.services:
        return False
    if 'harbour' in words and not ('harbour' in s.services or getattr(s, 'harbour', None)):
        return False
    return True


def seed_steps(game, s, spec):
    """The steps of a seed made real in this world, or None when a target is missing."""
    out = []
    for tok in spec:
        v, _, rest = tok.partition(':')
        if v == 'kill':
            bs = [wd for wd in _beasts(game, s) if not _taken(game, 'wd', wd.id)]
            if not bs:
                return None
            wd = bs[0]
            out.append(dict(v='kill', wd=wd.id, x=wd.x, y=wd.y, name=wd.name))
        elif v == 'clear':
            ns = [d for d in _nests(game, s) if not _taken(game, 'did', d.id)]
            if not ns:
                return None
            out.append(dict(v='clear', did=ns[0].id, boss=ns[0].boss, name=ns[0].name))
        elif v == 'hunt':
            ns = [n for n in _named(game, s) if not _taken(game, 'nid', n.id)]
            if not ns:
                return None
            out.append(dict(v='hunt', nid=ns[0].id, name=ns[0].name))
        elif v == 'find':
            ds = [d for d in _dungeons(game, s) if not _taken(game, 'did', d.id)]
            if not ds:
                return None
            d = random.choice(ds)
            out.append(dict(v='find', did=d.id, relic=rest, name=d.name))
        elif v == 'go':
            ts = _towns(game, s)
            if not ts:
                return None
            o = random.choice(ts)
            out.append(dict(v='go', sid=o.id, name=o.name, who=rest))
        elif v == 'seat':
            hs = _seats(game, s)
            if not hs:
                return None
            h = random.choice(hs)
            out.append(dict(v='seat', hid=h.id, name=h.title))
        elif v == 'bring':
            g, _, n = rest.partition(':')
            out.append(dict(v='bring', good=g, qty=int(n or 1)))
        else:
            out.append(dict(v=v))
    return out


def from_seed(game, s, pp, want=None):
    """A seed that may fall here: {seed, title, line, steps, twist, trade, motive}, or None."""
    cands = world_seeds(game) if want is None else [want]
    random.shuffle(cands)
    for i in cands:
        title, rule, trade, line, spec, twist = FD.SEEDS[i]
        if want is None and not seed_fits(game, s, pp, rule):
            continue
        steps = seed_steps(game, s, spec)
        if not steps:
            continue
        givers = dict(FD.GIVERS.get(pp) or FD.GIVERS['human'])
        who = givers.get(trade) or dict(FD.GIVERS['human']).get(trade) or 'a local'
        motive = {'kill': 'safety', 'clear': 'safety', 'hunt': 'honour', 'find': 'property', 'go': 'family',
                  'seat': 'family', 'watch': 'safety', 'bring': 'tools', 'dish': 'feast'}[steps[-1]['v']]
        if want is None:
            game.world.folk_seeds_used.append(i)
        return dict(seed=title, line=line, steps=steps, twist=twist, trade=trade, title=who, motive=motive)
    return None


def wanted(game, s):
    """How many people in this settlement have a need: 0 to 2, steady for a few days."""
    h = (s.id * 7919 + game.day // 5 * 104729) % 100
    top = 2 if s.size >= 2 else 1
    return 0 if h < 25 else 1 if h < 75 or top == 1 else 2


def refresh(game, s):
    lst = store(game).setdefault(s.id, [])
    for nd in [nd for nd in lst if nd['until'] < game.day]:
        lapse(game, s, nd)
    lst[:] = [nd for nd in lst if nd['until'] >= game.day]
    ev = getattr(s, 'event', None)
    if ev and ev[0] in ('war', 'raid', 'undead', 'plague') and lst and random.random() < .15:
        nd = random.choice(lst)
        lst.remove(nd)
        died(game, s, nd)
    tries = 0
    while len(lst) < wanted(game, s) and tries < 3:
        tries += 1
        nd = make(game, s, avoid={x['src'] for x in lst})
        if nd:
            lst.append(nd)
    return lst


# ------------------------------------------------------------------ when nobody helps
WRONG = {'safety': ('{name} lost the last of the flock to it.', 'the flock gone'),
         'health': ('The sickness took {name} in the end.', None),
         'family': ('{name} never heard from their kin again.', None),
         'property': ('{name} gave up looking.', None),
         'tools': ('{name} closed the shop for good.', 'scarce'),
         'honour': ('{name} lost face before the whole town.', None),
         'peace': ('{name} mourns still.', None),
         'feast': ('The feast went ahead with an empty table.', None),
         'knowledge': ('Nobody learnt what it was.', None), 'skill': ('{name} could not do it alone.', None)}


def lapse(game, s, nd, failed=False):
    """A need runs out: the folk solved it themselves, or it went wrong; the news says which, the world shows it."""
    from . import news as NW
    if not failed and random.random() < .5:
        NW.post(game, 'folk', f"In {s.name}, {nd['title']} solved their trouble without help in the end.", s.x, s.y)
        return
    line, sign = WRONG.get(nd['motive'], ('It went badly for {name}.', None))
    NW.post(game, 'folk', f"In {s.name}: " + line.format(name=nd['title']), s.x, s.y)
    if sign == 'scarce':
        st = next((st for st in nd['steps'] if st['v'] == 'bring'), None)
        if st and st['good'] in s.market:
            s.market[st['good']][0] = 0                 # the shop shut: none of it on the market
    if nd['motive'] in ('health', 'safety') and random.random() < .3:
        died(game, s, nd)


def died(game, s, nd):
    """Givers can die: a grave with a name you may know."""
    from . import news as NW
    NW.post(game, 'folk', f"{nd['title']} of {s.name} is dead.", s.x, s.y)
    h = helped(game).get(nd.get('root', nd.get('nid', nd['id'])))
    if h:
        h['dead'] = True
    grave(game, s.id, f"Here lies {nd['title']}. {random.choice(['Missed by all.', 'Gone before their time.', 'At rest.'])}")
    from . import missions as MS
    m = mission_of(game, nd.get('nid', nd['id']))
    if m:
        MS.fail(game, m, f"{nd['title']} is dead.")


def grave(game, sid, text):
    game.world.__dict__.setdefault('folk_graves', {}).setdefault(sid, []).append(text)


def place_graves(game, m):
    """The graves of folk you knew, at the edge of the settlement; their names on the look (m.epitaphs)."""
    from .towns import INDOOR
    lst = game.world.__dict__.get('folk_graves', {}).get(m.sid, [])
    eps = m.__dict__.setdefault('epitaphs', {})
    have = set(eps.values())
    for text in lst:
        if text in have:
            continue
        cx, cy = m.entry
        for r in range(4, 14):
            cells = [(cx + dx, cy + dy) for dx in range(-r, r + 1) for dy in (-r, r)
                     if m.inb(cx + dx, cy + dy) and m.tile(cx + dx, cy + dy) in (D.GRASS, D.FLOOR, D.PATH)
                     and m.tile(cx + dx, cy + dy) not in INDOOR and not m.mon_at(cx + dx, cy + dy)]
            if cells:
                x, y = random.choice(cells)
                m.set(x, y, D.GRAVE)
                eps[y * m.w + x] = text
                break


def epitaph(m, x, y):
    return m.__dict__.get('epitaphs', {}).get(y * m.w + x)


def need(game, nid):
    for lst in store(game).values():
        for nd in lst:
            if nd['id'] == nid:
                return nd
    return None


def mission_of(game, nid):
    from . import missions as MS
    return next((m for m in MS.active(game) if m.kind == 'folk' and m.data.get('nid') == nid), None)


# ------------------------------------------------------------------ on the map
def on_enter(game, m):
    """A settlement's map: the people with a need stand about, and those who wait for you."""
    from . import missions as MS
    sid = getattr(m, 'sid', None)
    if sid is None or m.kind != 'town':
        return
    s = game.world.settlements[sid]
    offers = refresh(game, s)
    keep = {nd['id'] for nd in offers} | {mi.data['nid'] for mi in MS.active(game) if mi.kind == 'folk'
                                          and mi.giver == sid}
    m.mons = [o for o in m.mons if o.role != 'folk' or getattr(o, 'need', None) in keep]
    there = {getattr(o, 'need', None) for o in m.mons if o.role == 'folk'}
    for nd in offers + [mi.data for mi in MS.active(game) if mi.kind == 'folk' and mi.giver == sid
                        and not mi.data.get('guild')]:      # a guild job's giver is the master in the hall
        if nd.get('nid', nd['id']) not in there:
            place(game, m, nd)
    known = {getattr(o, 'helped', None) for o in m.mons if o.role == 'folk'}
    for hid, h in helped(game).items():
        if h['sid'] == sid and hid not in known and not h.get('dead') and hid not in keep and not h.get('guild'):
            npc = place(game, m, dict(id=None, title=h['title'], people=h.get('people', 'human'),
                                      gender=h.get('gender', 'male'), motive=h['motive']))
            if npc:
                npc.need, npc.helped, npc.job = None, hid, 'glad to see you'
    visit(game, s)
    place_graves(game, m)


def place(game, m, nd):
    from .entities import make_npc
    from .worldgen import free_around
    folk = [o for o in m.mons if o.role in ('villager', 'market') and o.ch == '☺']
    near = random.choice(folk) if folk else None
    cx, cy = (near.x, near.y) if near else m.entry
    spots = [c for c in free_around(game, m, cx, cy, 3) if D.TILES[m.tile(*c)].walk]
    if not spots:
        return None
    x, y = random.choice(spots)
    npc = make_npc(game, nd['title'], 'folk', '#d8c8a8', x, y, False, race=nd['people'] if nd['people'] != 'orc' else
                   'orc', gender=nd['gender'])
    npc.need = nd.get('nid', nd['id'])
    npc.job = FD.MOOD.get(nd['motive'], 'worried')
    npc.home_pos = npc.work_pos = (x, y)
    npc.path = []
    m.mons.append(npc)
    return npc


def tick(game, m):
    """Passing near, they say their need; at night a watch is kept."""
    if m.kind != 'town':
        return
    p = game.player
    for o in m.mons:
        if o.role != 'folk' or cheb(o.x, o.y, p.x, p.y) > 3 or not game.visible(o.x, o.y):
            continue
        hid = getattr(o, 'helped', None)
        if hid is not None:
            greet(game, o, hid)
            continue
        nd = need(game, getattr(o, 'need', None))
        if nd and nd.get('said') != game.day:
            nd['said'] = game.day
            game.say(o, random.choice(FD.PASSING[nd['motive']]))
            from . import guide as GDE
            GDE.tip(game, 'folk')
    _watch(game, m)


def greet(game, npc, hid):
    """Who you helped greets you, and now and then gives a small thing or a rumour."""
    h = helped(game).get(hid)
    if not h or h.get('greet') == game.day:
        return
    h['greet'] = game.day
    game.msg(random.choice(FD.GREET).format(name=npc.name.split(',')[0]), 'talk')
    if game.day - h.get('gift_day', 0) >= 10 and random.random() < .3:
        h['gift_day'] = game.day
        s = game.world.settlements[h['sid']]
        line = _rumour(game, s) if random.random() < .5 else None
        if line:
            game.msg(line, 'info')
        else:
            from .entities import Item
            it = Item(game.new_id(), 'food', 'bread')
            if game.add_to_inv(it):
                game.msg(f"{npc.name.split(',')[0]} gives you a loaf, still warm.", 'good')


def visit(game, s):
    """A follow-up that has come due for someone of this town: a new part of their story, up to three."""
    for hid, h in helped(game).items():
        if h['sid'] != s.id or not h.get('follow') or game.day < h.get('due', 0) or h.get('dead'):
            continue
        key = h.pop('follow')
        line, kind = FD.FOLLOW[key]
        first = h['title'].split(',')[0]
        if kind == 'need':
            nd = make(game, s)
            if nd:
                nd.update(name=first, title=h['title'], people=h.get('people', nd['people']), gender=h.get('gender'),
                          trade=h['trade'], motive='health', line=line.strip('"'), twist=None,
                          steps=[dict(v='bring', good='medicine', qty=1)], root=hid, src='follow')
                store(game).setdefault(s.id, []).append(nd)
            continue
        game.msg(f"{first}: {line}" if line.startswith('"') else line, 'talk')
        if kind == 'gift':
            from .entities import Item
            game.add_to_inv(Item(game.new_id(), 'food', 'bread'))
            from . import jobs as JB
            JB.effects(game, town=[(s.id, 3)])
        elif kind == 'beast':
            from . import bestiary as BE
            BE.study(game, 1)
        elif kind == 'rumour':
            r = _rumour(game, s)
            if r:
                game.msg(r, 'info')
        elif kind == 'rep':
            s.rep = min(100, s.rep + 2)
        if h.get('part', 1) < 3 and random.random() < .3:
            h['follow'] = random.choice(['thanks', 'apprentice'])
            h['due'] = game.day + random.randint(10, 40)
            h['part'] = h.get('part', 1) + 1


def mark(game, npc):
    """'!' over someone with a need, '?' when you can hand it in."""
    nd = need(game, getattr(npc, 'need', None))
    if nd:
        return '!'
    m = mission_of(game, getattr(npc, 'need', None))
    if m and (m.state == 'turnin' or _ready(game, m)):
        return '?'
    return None


# ------------------------------------------------------------------ talking
def say_need(nd):
    return f'"{nd["line"]}"'


def talk(game, npc):
    from . import events as EV
    nid = getattr(npc, 'need', None)
    nd = need(game, nid)
    if nd:
        from .money import fmt
        EV.ask(game, 'folk', npc.name, say_need(nd) + (f' {nd["hint"]}' if nd.get('hint') else '') + f'\n\n{brief(game, nd)} They offer {fmt(nd["coin"])}, and '
               f'{"a favour" if nd["reward"] in FD.FAVOURS else "something of their own" if nd["reward"] == "own" else "what they know"}.',
               [('I will help', 'take'), ('Not now', 'bye')], nid=nid, npc=npc.id)
        return True
    m = mission_of(game, nid)
    if not m:
        game.say(npc, random.choice(['Thank you again.', 'Good day to you.', 'All is well now, thanks to you.']))
        return True
    if m.state == 'turnin' or _ready(game, m):
        finish(game, m, npc)
        return True
    st = current(m)
    game.say(npc, {'bring': f"Did you find the {st.get('qty', 1)} {_good(st)}? Any market should have some.",
                   'dish': 'Something warm, cooked by your own hand. That is all.',
                   'watch': 'Tonight, then? Stay in the village until the small hours.'}.get(
        st['v'] if st else '', 'Any news? I can hardly sleep.'))
    return True


def _good(st):
    g = st.get('good')
    return D.GOODS[g]['name'].lower() if g in D.GOODS else 'goods'


def step_text(st):
    v = st['v']
    if v == 'kill':
        return f"kill {beast_name(st['name'])}"
    if v == 'clear':
        return f"kill the {D.MONSTERS[st['boss']]['name'].lower()} at the bottom of {st['name']}"
    if v == 'hunt':
        return f"hunt down {st['name']}"
    if v == 'find':
        return f"find {st['relic']} in {st['name']}"
    if v == 'go':
        return f"go to {st['name']} and speak with {st['who']}"
    if v == 'seat':
        return f"take word to {st['name']}"
    if v == 'watch':
        return 'keep watch here one night'
    if v == 'bring':
        return f"bring {st['qty']} {_good(st)}"
    if v == 'dish':
        return 'bring a dish you cooked'
    if v == 'piece':
        return f"bring {st['n']} {st['what']}"
    return v


def brief(game, nd):
    """The steps in one line."""
    s = ', then '.join(step_text(st) for st in nd['steps'])
    return s[0].upper() + s[1:] + (', and come back.' if nd['steps'][-1]['v'] not in ('bring', 'dish') else '.')


def r_folk(game, choice, ctx):
    if choice == 'take':
        take(game, ctx['nid'])


def take(game, nid):
    from . import missions as MS
    from . import calendar as CAL
    nd = need(game, nid)
    if not nd:
        return None
    if len(MS.active(game)) >= MS.MAX_ACTIVE:
        game.msg(f'You already have {MS.MAX_ACTIVE} jobs. Finish one first.', 'bad')
        return None
    w = game.world
    lst = store(game).get(nd['sid'], [])
    if nd in lst:
        lst.remove(nd)
    m = MS.Mission(game.new_id(), 'folk', nd['sid'])
    d = dict(nd)
    d['nid'] = nd['id']
    d['step'] = 0
    d['giver_name'] = nd['title']
    m.data = d
    m.title = _title(nd)
    m.reward = nd['coin']
    m.rep = random.randint(3, 6)
    m.deadline = game.day + 10 + 4 * len(nd['steps'])
    m.desc = f"{brief(game, nd)} {nd['name']} waits in {w.settlements[nd['sid']].name}. Before {CAL.short(m.deadline)}."
    m.state = 'active'
    m.faction = w.settlements[nd['sid']].faction
    game.missions.append(m)
    _start(game, m)
    from . import met as MET
    MET.saw(game, 'job: folk')
    game.msg(f'Job accepted: {m.title}.', 'gold')
    return m


def _title(nd):
    if nd.get('job_title'):
        return nd['job_title']
    st = nd['steps'][-1]
    v, who = st['v'], nd['name']
    if v == 'kill':
        return f"{beast_name(st['name'])[0].upper() + beast_name(st['name'])[1:]} troubles {who}"
    if v == 'clear':
        return f"{who} and {st['name']}"
    if v == 'hunt':
        return f"{who}'s grudge: {st['name']}"
    if v == 'find':
        return f"{st['relic'][0].upper() + st['relic'][1:]} for {who}"
    if v == 'go':
        return f"{who}'s kin in {st['name']}"
    if v == 'seat':
        return f"{who}'s word to the levy"
    if v == 'watch':
        return f"A night's watch for {who}"
    if v == 'bring':
        return f"{st['qty']} {_good(st)} for {who}"
    if v == 'dish':
        return f'A dish for {who}'
    return f'Help {who}'


def beast_name(n):
    """'the goblin pack', 'a dire wolf', 'Old Greytooth'."""
    if n.endswith(' pack'):
        return 'the ' + n.lower()
    if not _MON_NAMES:
        _MON_NAMES.update(v['name'] for v in D.MONSTERS.values())
    if n in _MON_NAMES:
        return 'a ' + n.lower()
    return n


def current(m):
    i = m.data.get('step', 0)
    steps = m.data['steps']
    return steps[i] if i < len(steps) else None


def _start(game, m):
    """Set up the step that is now current: a relic in its dungeon, a place on the map."""
    st = current(m)
    if not st:
        m.state = 'turnin'
        game.msg(f"Go back to {m.data['title']} in {game.world.settlements[m.giver].name}.", 'gold')
        return
    w = game.world
    if st['v'] == 'find':
        d = w.dungeons[st['did']]
        if d.relic is None:
            d.relic = m.id
            m.data['relic'], m.data['dungeon'] = st['relic'], d.id
            key = f'{d.id}:{d.depth}'
            if key in game.maps:
                from . import missions as MS
                MS.place_relic(game, game.maps[key], m)
        game.reveal_place(d.x, d.y, 1)
    elif st['v'] == 'clear':
        d = w.dungeons[st['did']]
        game.reveal_place(d.x, d.y, 1)
    elif st['v'] == 'go':
        o = w.settlements[st['sid']]
        game.reveal_place(o.x, o.y, 2)
    elif st['v'] == 'seat':
        h = w.holds[st['hid']]
        game.reveal_place(h.x, h.y, 1)


def advance(game, m, line=None):
    if line:
        game.msg(line, 'gold')
    st = current(m)
    m.data['step'] = m.data.get('step', 0) + 1
    tw = m.data.get('twist')
    if tw and not m.data.get('twisted') and st and (st['v'] in FD.TWISTS[tw][0] or current(m) is None):
        reveal(game, m)
        return
    _start(game, m)


# ------------------------------------------------------------------ the twists
def _fill(game, m, text):
    from . import jobs as JB
    w = game.world
    s = w.settlements[m.giver]
    ts = _towns(game, s)
    return text.format(rival=m.data.setdefault('twist_rival', random.choice(JB.RIVALS)),
                       town=(ts[0].name if ts else s.name),
                       other=m.data.setdefault('twist_other', random.choice(JB.NAMES) + ' ' + random.choice(['the fisher', 'the miller', 'the farmer'])))


def reveal(game, m):
    """What you find on the spot: one choice, 2 to 4 options (or none)."""
    from . import events as EV
    m.data['twisted'] = True
    tw = m.data['twist']
    _verbs, text, opts = FD.TWISTS[tw]
    p = game.player
    out = []
    for i, (lab, oc) in enumerate(opts):
        ok = p.gold >= oc.get('pay', 0) and (not oc.get('need_good') or p.cargo.get(oc['need_good'], 0) >= 1)
        out.append((_fill(game, m, lab), f'{m.id}:{i}' if ok else None))
    EV.ask(game, 'folktwist', m.data['title'], _fill(game, m, text), out, mid=m.id)


def r_twist(game, choice, ctx):
    from . import missions as MS
    m = MS.find(game, ctx.get('mid'))
    if not m or not choice or ':' not in choice:
        return
    i = int(choice.split(':')[1])
    _lab, oc = FD.TWISTS[m.data['twist']][2][i]
    outcome(game, m, oc)
    if m.state in ('active', 'turnin') and m.kind == 'folk':
        _start(game, m)


def outcome(game, m, oc):
    """What a twist's choice leaves: coin, standing, a new step, a later part."""
    from . import jobs as JB
    p = game.player
    d = m.data
    w = game.world
    if oc.get('pay'):
        p.gold -= oc['pay']
    if oc.get('need_good'):
        g = oc['need_good']
        p.cargo[g] -= 1
        if not p.cargo[g]:
            del p.cargo[g]
    d['coin_mult'] = d.get('coin_mult', 1) * oc.get('coin', 1)
    JB.effects(game, town=[(m.giver, oc.get('rep', 0) + oc.get('law', 0))], god=oc.get('god', 0))
    if oc.get('lose'):
        game.end_turn(oc['lose'] * D.DAY_LEN // 24, True)
    if oc.get('rumour'):
        line = _rumour(game, w.settlements[m.giver])
        if line:
            game.msg(line, 'info')
    if oc.get('friend'):
        d['friend'] = True
    if oc.get('follow'):
        d['follow'] = oc['follow']
    if oc.get('grave'):
        grave(game, m.giver, f"Here lies one of {d['name']}'s kin, who waited too long for news.")
    if oc.get('captive'):
        game.msg('The captive limps off towards home, weeping. Word of it will go before you.', 'good')
    if oc.get('step') and m.kind == 'folk':
        s = w.settlements[m.giver]
        if oc['step'] == 'go_temple':
            ts = [o for o in w.settlements if 'temple' in o.services and o.id != m.giver] or _towns(game, s)
            who = 'a priest'
        else:
            ts = _towns(game, s)
            who = 'the trader who has it'
        if ts:
            o = min(ts, key=lambda t: cheb(t.x, t.y, s.x, s.y))
            d['steps'].insert(d['step'], dict(v='go', sid=o.id, name=o.name, who=who))
    if oc.get('end') and m.kind == 'folk':
        d['step'] = len(d['steps'])


def board_twist(game, m):
    """A board job, now and then: one of the twists that fit any job, found as it ends."""
    from . import events as EV
    tw = m.data.get('twist')
    if not tw or m.data.get('twisted'):
        return
    m.data['twisted'] = True
    _v, text, opts = FD.TWISTS[tw]
    out = [(_fill(game, m, lab), f'{m.id}:{i}') for i, (lab, _oc) in enumerate(opts)]
    EV.ask(game, 'boardtwist', m.title, _fill(game, m, text), out, mid=m.id, reward=m.reward)


def r_board(game, choice, ctx):
    from . import missions as MS
    from . import jobs as JB
    m = MS.find(game, ctx.get('mid'))
    if not m or not choice:
        return
    _lab, oc = FD.TWISTS[m.data['twist']][2][int(choice.split(':')[1])]
    extra = round(ctx.get('reward', 0) * (oc.get('coin', 1) - 1))
    if extra:
        game.player.gold = max(0, game.player.gold + extra)
        from .money import fmt
        game.msg(f"{'You get' if extra > 0 else 'You give up'} {fmt(abs(extra))}.", 'info')
    if oc.get('pay'):
        game.player.gold = max(0, game.player.gold - oc['pay'])
    if m.giver is not None:
        JB.effects(game, town=[(m.giver, oc.get('rep', 0))], god=oc.get('god', 0))
    if oc.get('rumour'):
        line = _rumour(game, game.world.settlements[m.giver] if m.giver is not None else game.world.settlements[0])
        if line:
            game.msg(line, 'info')


def _ready(game, m):
    """A bring or dish step, done when you stand before the giver with it."""
    st = current(m)
    if not st:
        return m.state == 'turnin'
    p = game.player
    if st['v'] == 'bring':
        return p.cargo.get(st['good'], 0) >= st['qty']
    if st['v'] == 'dish':
        return any(it.k == 'dish' for it in p.inv)
    if st['v'] == 'piece':
        from . import craftguilds as CG
        return CG.has_pieces(game, st)
    return False


def finish(game, m, npc=None):
    from . import missions as MS
    p = game.player
    st = current(m)
    if st and st['v'] == 'bring':
        g, q = st['good'], st['qty']
        p.cargo[g] -= q
        if not p.cargo[g]:
            del p.cargo[g]
            p.cost_basis.pop(g, None)
    elif st and st['v'] == 'dish':
        it = next(it for it in p.inv if it.k == 'dish')
        game.remove_one(it)
    elif st and st['v'] == 'piece':
        from . import craftguilds as CG
        CG.take_pieces(game, st)
    d = m.data
    for key in ('dungeon',):
        dg = game.world.dungeons.get(d.get(key)) if d.get(key) else None
        if dg is not None and dg.relic == m.id:
            dg.relic = None
    m.reward = round(m.reward * d.get('coin_mult', 1))
    MS.complete(game, m, [m.giver])
    _people_standing(game, m)
    gift = reward(game, m)
    hp = helped(game)
    old = hp.get(d.get('root', d['nid']), {})
    part = old.get('part', 0) + 1
    follow = d.get('follow') or ('friend' if d.get('friend') else None)
    if follow is None and part < 3 and random.random() < .45:
        follow = random.choice(['wedding', 'thanks', 'apprentice'])
    hp[d.get('root', d['nid'])] = dict(name=d['name'], title=d['title'], sid=m.giver, day=game.day, motive=d['motive'],
                                      trade=d['trade'], people=d['people'], gender=d['gender'], part=part,
                                      follow=follow if part < 3 else None,
                                      due=game.day + random.randint(7, 30), gift_day=game.day, guild=d.get('guild'))
    if d.get('guild'):                  # a guild job: the hall remembers it, nobody comes to visit
        hp[d.get('root', d['nid'])]['follow'] = None
    if npc is not None:
        npc.need = None
        game.request = ('dialog', npc.name, random.choice(FD.THANKS) + (f' {gift}' if gift else ''))
    elif gift:
        game.msg(gift, 'good')


def _people_standing(game, m):
    """The giver's own people think better of you too, where it is not the town's own (a temple, a guild, the law)."""
    from . import jobs as JB
    d = m.data
    if d['trade'] == 'priest':
        JB.effects(game, god=2, quiet=True)
    elif d['trade'] == 'guard':
        s = game.world.settlements[m.giver]
        JB.effects(game, town=[(s.id, 2)], quiet=True)


def reward(game, m):
    """One thing fitting the giver; the line that says so."""
    from .entities import Item
    d = m.data
    kind = d['reward']
    p = game.player
    if kind in FD.FAVOURS:
        it = Item(game.new_id(), 'favour', kind)
        it.who = d['name']
        it.giver = d['title']
        if game.add_to_inv(it):
            return f"{d['name']} gives you {name_of(it)}: {FD.FAVOURS[kind][1][0].lower() + FD.FAVOURS[kind][1][1:]}"
        return None
    if kind == 'own':
        k, t = random.choice(FD.OWN.get(d['trade'], [('food', 'bread')]))
        it = Item(game.new_id(), k, t)
        if game.add_to_inv(it):
            return f"{d['name']} presses {it.display_name() if hasattr(it, 'display_name') else t} into your hands."
        return None
    if kind == 'guild':
        from . import craftguilds as CG
        return CG.reward(game, m)
    if kind == 'bestiary':
        from . import bestiary as BE
        names = BE.study(game, 2)
        if names:
            return f"{d['name']} tells you what the trappers know of the {' and the '.join(n.lower() for n in names)}."
    return _rumour(game, game.world.settlements[m.giver])


def _rumour(game, s):
    """A rumour that leads somewhere real: a place near this town you have not seen, marked on your map."""
    w = game.world
    om = game.maps['over']
    unseen = [x for x in list(w.dungeons.values()) + list(getattr(w, 'sites', ())) if hasattr(x, 'x')
              and not om.seen[x.y * om.w + x.x] and cheb(x.x, x.y, s.x, s.y) <= 50]
    if unseen:
        x = random.choice(unseen)
        game.reveal_place(x.x, x.y, 1)
        nm = getattr(x, 'name', None) or 'an old place'
        return f"\"There is a place I heard of: {nm}, to the {_dir(s, x.x, x.y)}.\" You mark it on your map."
    return None


# ------------------------------------------------------------------ the steps done in the world
def _steps_now(game, verb):
    from . import missions as MS
    for m in MS.active(game):
        if m.kind == 'folk' and m.state == 'active':
            st = current(m)
            if st and st['v'] == verb:
                yield m, st


def on_group_defeated(game, wd):
    for m, st in list(_steps_now(game, 'kill')):
        if st['wd'] == wd.id:
            advance(game, m, f"That was what troubled {m.data['name']}.")


def on_kill(game, mon):
    did = getattr(game.map, 'did', None)
    for m, st in list(_steps_now(game, 'clear')):
        if did == st['did'] and mon.k == st['boss']:
            advance(game, m, f"The {mon.name} is dead. {m.data['name']} will sleep tonight.")
    for m, st in list(_steps_now(game, 'hunt')):
        if getattr(mon, 'named', None) == st['nid']:
            advance(game, m, f"{st['name']} is dead. {m.data['name']} will want to know.")


def on_pickup(game, it):
    from . import missions as MS
    m = MS.find(game, getattr(it, 'mission', None))
    if m and m.kind == 'folk':
        st = current(m)
        if st and st['v'] == 'find':
            m.state = 'active'
            dg = game.world.dungeons.get(st['did'])
            if dg is not None and dg.relic == m.id:
                dg.relic = None
            advance(game, m)
            return True
    return False


def on_enter_town(game, sid):
    for m, st in list(_steps_now(game, 'go')):
        if st['sid'] == sid:
            advance(game, m, f"You find {st['who']} in {st['name']} and pass on {m.data['name']}'s word. "
                    + random.choice(['All is well, and they send their love.', 'They are well, only poor.',
                                     'They were ill, and are mending.']))


def on_enter_hold(game, hid):
    for m, st in list(_steps_now(game, 'seat')):
        if st['hid'] == hid:
            advance(game, m, f"You find {m.data['name']}'s boy among the levy and give him his mother's word. He sends his "
                    'back: he is cold and hungry, but whole.')


def _watch(game, m):
    from .towns import hour
    h = hour(game)
    if not 1 <= h <= 3:
        return
    for mi, st in list(_steps_now(game, 'watch')):
        if mi.giver == m.sid:
            advance(game, mi, random.choice(['In the small hours a fox slinks to the hen-house. You chase it off for good.',
                                             'Two boys from the next farm creep up to the hen-house with a sack. They run '
                                             'when they see you.']))


def target_pos(game, m):
    w = game.world
    st = current(m) if m.state == 'active' else None
    s = w.settlements[m.giver]
    if not st or st['v'] in ('bring', 'dish', 'watch'):
        return (s.x, s.y), s.name
    if st['v'] == 'kill':
        wd = next((x for x in w.wanderers if x.id == st['wd']), None)
        if wd is not None:
            st['x'], st['y'] = wd.x, wd.y
        return (st['x'], st['y']), st['name']
    if st['v'] in ('clear', 'find'):
        d = w.dungeons[st['did']]
        return (d.x, d.y), d.name
    if st['v'] == 'hunt':
        from . import named as NM
        n = NM.get(game, st['nid'])
        if n and n.alive:
            ax, ay, _r = NM.area(game, n)
            return (ax, ay), 'the search area'
        return (s.x, s.y), s.name
    if st['v'] == 'go':
        o = w.settlements[st['sid']]
        return (o.x, o.y), o.name
    if st['v'] == 'seat':
        h = w.holds[st['hid']]
        return (h.x, h.y), h.title
    return (s.x, s.y), s.name


def on_fail(game, m):
    dg = game.world.dungeons.get(m.data.get('dungeon')) if m.data.get('dungeon') else None
    if dg is not None and dg.relic == m.id:
        dg.relic = None
    if 'dead' not in m.data:
        m.data['dead'] = False
        lapse(game, game.world.settlements[m.giver], m.data, failed=True)


def daily(game):
    """A hunted group gone from the world: the step is done by others."""
    w = game.world
    ids = {x.id for x in w.wanderers}
    for m, st in list(_steps_now(game, 'kill')):
        if st['wd'] not in ids:
            advance(game, m, f"Word comes that {st['name'][0].lower() + st['name'][1:]} is gone. Go back to "
                    f"{m.data['name']}.")
    from . import named as NM
    for m, st in list(_steps_now(game, 'hunt')):
        n = NM.get(game, st['nid'])
        if not n or not n.alive:
            advance(game, m)


# ------------------------------------------------------------------ favours: tokens in the pack (Item 'favour')
def name_of(it):
    return FD.FAVOURS[it.t][0].format(who=getattr(it, 'who', 'A friend'))


def display(game, it):
    return name_of(it)


def lines(game, it):
    k = FD.FAVOURS[it.t]
    return [f"A favour from {getattr(it, 'giver', 'a friend')}. {k[1]} Show it at {k[2]}: it is gone once used."]


def value(game, it):
    return 0


def glyph(it):
    return '•'


def color(it):
    return (226, 200, 140)


def has(game, kind):
    return next((it for it in game.player.inv if it.k == 'favour' and it.t == kind), None)


def option(game, kind, label=None):
    """The extra option a window shows when you carry this favour, or []."""
    it = has(game, kind)
    return [(label or f'Show {name_of(it)}', 'favour:' + kind)] if it else []


def use(game, kind):
    it = has(game, kind)
    if not it:
        return False
    game.player.inv.remove(it)
    game.msg(f'You show {name_of(it)}. It is honoured, and the favour is spent.', 'good')
    return True


def _register():
    from . import events as EV
    EV.RESOLVERS['folk'] = r_folk
    EV.RESOLVERS['folktwist'] = r_twist
    EV.RESOLVERS['boardtwist'] = r_board


_register()
