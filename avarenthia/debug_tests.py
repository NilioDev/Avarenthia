"""The Tests page of the debug menu (F12, T): every built line of docs/testing.md, set up with one key and ticked off.

A tool for testing, not part of the game (see "The test menu" in docs/plan.md); not in the handbook. The lines are
read from testing.md itself (packed beside the test build); what each line needs is a small recipe here, keyed by its
heading and its name. A recipe is a list of steps from the small set in STEPS, each one a debug action that exists.
Enter on a line runs its recipe; Enter again on the same line sets up the next one of its kind (the next temple, the
next theme room, the next boss...). What was ticked (right or wrong) is kept beside the save, with the build it was
ticked in."""
import json
import os
import re
import subprocess
import sys

from . import debug as DBG

# Headings of testing.md whose things are not built yet: their lines stay hidden. A round that builds one takes it out.
# A heading hides all its lines; 'heading :: name' hides one line.
NOT_BUILT = {'Wars that feel like wars'}


# ------------------------------------------------------------------ reading testing.md
def _here():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def source():
    """Where testing.md lies: packed beside the test build, or in docs/ of the source."""
    for d in (getattr(sys, '_MEIPASS', None), os.path.join(_here(), 'docs')):
        if d and os.path.exists(os.path.join(d, 'testing.md')):
            return os.path.join(d, 'testing.md')
    return None


def heading(h):
    return re.sub(r'\s*\([^()]*(\([^()]*\)[^()]*)*\)\s*$', '', h).strip()


def name_of(text):
    m = re.match(r'\*\*(.+?)\*\*', text)
    return m.group(1) if m else re.split(r'[.;:]| - ', text)[0][:50]


MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october',
          'november', 'december']
CHANGED = {}       # heading -> the day its thing last changed ('2026-11-13'), from its 'Changed: <date>' line


def iso(text):
    """'13 November 2026' (or '2026-11-13') as '2026-11-13'; None when it is not a date."""
    t = text.strip().rstrip('.')
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})$', t)
    if m:
        return t
    m = re.match(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})$', t)
    if m and m.group(2).lower() in MONTHS:
        return f'{m.group(3)}-{MONTHS.index(m.group(2).lower()) + 1:02d}-{int(m.group(1)):02d}'
    return None


def parse(text):
    """The lines of testing.md: [(group, key, name, what to check, what the debug menu offers)]. A line
    'Changed: <date>' under a heading says when its thing last changed (kept in CHANGED)."""
    out, sec, cur = [], None, None
    CHANGED.clear()
    for ln in text.split('\n'):
        if ln.startswith('## ') or ln.startswith('### '):
            sec, cur = heading(ln.lstrip('#').strip()), None
            continue
        if sec and ln.startswith('Changed:'):
            d = iso(ln[8:])
            if d:
                CHANGED[sec] = max(d, CHANGED.get(sec, d))
            continue
        if ln.startswith('- ') and sec:
            cur = [sec, ln[2:].strip()]
            out.append(cur)
            continue
        if cur and ln.startswith('  ') and ln.strip():
            cur[1] += ' ' + ln.strip()
            continue
        cur = None
    lines = []
    for sec, t in out:
        name = name_of(t)
        body = re.sub(r'^\*\*.+?\*\*\s*-?\s*', '', t)
        check, _, dbg = body.partition('Debug:')
        lines.append((sec, f'{sec} :: {name}', name, check.strip().rstrip('.') + '.', dbg.strip()))
    return lines


def lines(every=False):
    path = source()
    if not path:
        return []
    with open(path, encoding='utf-8') as f:
        rows = parse(f.read())
    return rows if every else [r for r in rows if r[0] not in NOT_BUILT and r[1] not in NOT_BUILT]


# ------------------------------------------------------------------ the build and the ticks
_COMMIT = []


def commit():
    """The build's commit: written into TESTBUILD by CI, or asked of git in the source."""
    if _COMMIT:
        return _COMMIT[0]
    c = 'source'
    tb = os.path.join(getattr(sys, '_MEIPASS', ''), 'TESTBUILD')
    try:
        if getattr(sys, 'frozen', False) and os.path.exists(tb):
            with open(tb, encoding='utf-8') as f:
                m = re.search(r'commit (\w+)', f.read())
            c = m.group(1)[:7] if m else 'test build'
        else:
            c = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=_here(), capture_output=True, text=True,
                               timeout=3).stdout.strip() or 'source'
    except Exception:
        pass
    _COMMIT.append(c)
    return c


def ticks_path():
    return os.path.join(DBG.folder(), 'debug_tests.txt')


def ticks():
    try:
        with open(ticks_path(), encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def tick(key, mark, note='', day=None):
    """Mark a line right ('ok') or wrong ('bad'), or take the mark off (None)."""
    t = ticks()
    if mark is None:
        t.pop(key, None)
    else:
        import datetime
        t[key] = {'mark': mark, 'commit': commit(), 'note': note, 'day': day,
                  'date': datetime.date.today().isoformat()}
    try:
        with open(ticks_path() + '.tmp', 'w', encoding='utf-8') as f:
            json.dump(t, f, indent=1, sort_keys=True)
        os.replace(ticks_path() + '.tmp', ticks_path())
    except OSError:
        pass
    return t


def state(row, t):
    """What a line is now: 'open' (never ticked), 'ok', 'bad', or 'stale' (ticked before its thing changed).
    A tick lasts across builds; only a newer 'Changed:' date under its heading opens it again."""
    if not t:
        return 'open'
    ch = CHANGED.get(row[0])
    if ch and (t.get('date') or '') < ch:
        return 'stale'
    return 'ok' if t.get('mark') == 'ok' else 'bad'


def is_open(row, t):
    return state(row, t) in ('open', 'bad', 'stale')


def counts(rows, ticks_now):
    """Per heading: (lines, right, wrong) for the overview '3/5 ✓ 1 ✗' (a stale tick counts as open)."""
    out = {}
    for r in rows:
        c = out.setdefault(r[0], [0, 0, 0])
        c[0] += 1
        st = state(r, ticks_now.get(r[1]))
        if st == 'ok':
            c[1] += 1
        elif st == 'bad':
            c[2] += 1
    return out


def first_words(note, n=4):
    words = (note or '').split()
    return ' '.join(words[:n]) + (' ...' if len(words) > n else '')


# ------------------------------------------------------------------ the steps
def _dist(game, x, y):
    wx, wy = game.world_pos()
    return max(abs(x - wx), abs(y - wy))


def _xy(game, act):
    w = game.world
    k = act[0]
    if k == 'xy':
        return act[1], act[2]
    obj = {'s': lambda: w.settlements[act[1]], 'd': lambda: w.dungeons[act[1]], 'site': lambda: w.sites[act[1]],
           'h': lambda: w.holds[act[1]]}[k]()
    return obj.x, obj.y


def _settlement_fits(game, act, where):
    if act[0] != 's':
        return True
    s = game.world.settlements[act[1]]
    if where in ('dwarf', 'halfling', 'orc', 'elf', 'human'):
        return getattr(s, 'race', 'human') == where and (where != 'human' or s.kind != 'deephold')
    if where == 'harbour':
        return getattr(s, 'harbour', False)
    if where in ('river', 'march'):
        from . import citygrow as CG
        try:
            _m, _h, fort, _f, river = CG.plan(game, s)
        except Exception:
            return False
        return bool(river) if where == 'river' else bool(fort)
    return True


def _north(game, act):
    _x, y = _xy(game, act)
    return y < game.maps['over'].h * .3


def matches(game, kind, name=None, where=None):
    """The places to teleport to whose kind starts with kind (and whose name holds name), nearest first."""
    kinds = kind if isinstance(kind, tuple) else (kind,)
    rows = []
    for k, nm, act in DBG.places(game):
        if not any(k == kd or k.startswith(kd + ' ') or (kd.endswith('(') and k.startswith(kd)) for kd in kinds) \
                or (name and name.lower() not in nm.lower()):
            continue
        if where == 'north':
            if not _north(game, act):
                continue
        elif where == 'fallen':
            if ', half' not in k and ', ruin' not in k:
                continue
        elif where == 'older':
            if 'older below' not in k:
                continue
        elif where and not _settlement_fits(game, act, where):
            continue
        rows.append((k, nm, act))
    rows.sort(key=lambda r: (_dist(game, *_xy(game, r[2])), r[1]))
    return rows


def s_to(game, n, kind, name=None, where=None):
    rows = matches(game, kind, name, where)
    if not rows:
        game.msg(f'Test: there is no {kind if isinstance(kind, str) else kind[0]}{" " + where if where else ""} in this world.', 'bad')
        return
    k, nm, act = rows[n % len(rows)]
    DBG.teleport(game, act)
    game.msg(f'Test: {nm} ({k}), {n % len(rows) + 1} of {len(rows)}.', 'info')


def s_near(game, n, kind, name=None, where=None):
    """Onto the world map beside a place, without going in."""
    rows = matches(game, kind, name, where)
    if not rows:
        game.msg(f'Test: there is no {kind} in this world.', 'bad')
        return
    k, nm, act = rows[n % len(rows)]
    x, y = _xy(game, act)
    om = game.maps['over']
    from . import data as D
    spot = next(((x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1))
                 if 0 <= x + dx < om.w and 0 <= y + dy < om.h and om.t[(y + dy) * om.w + x + dx] not in (D.WATER, D.MOUNTAIN)),
                (x, y))
    DBG.to_over(game, *spot)
    game.msg(f'Test: beside {nm} ({k}).', 'info')


def s_crossing(game, n):
    """Onto a road where it crosses a river on the world map."""
    from . import data as D
    om = game.maps['over']
    spots = [i for i in range(len(om.t)) if om.t[i] == D.ROAD and om.river[i]]
    if not spots:
        game.msg('Test: no road crosses a river in this world.', 'bad')
        return
    wx, wy = game.world_pos()
    spots.sort(key=lambda i: max(abs(i % om.w - wx), abs(i // om.w - wy)))
    i = spots[(n * 7) % len(spots)]
    DBG.to_over(game, i % om.w, i // om.w)
    game.msg('Test: a road over a river; [>] goes into the land.', 'info')


def s_over(game, n):
    """Out onto the world map where you are."""
    if game.cur != 'over':
        DBG.to_over(game, *game.world_pos())


def s_deep(game, n, kind, depth=0):
    """Into a dungeon of this kind, on a level: depth, or its bottom when 0."""
    rows = [r for r in matches(game, kind) if r[2][0] == 'd']
    if not rows:
        game.msg(f'Test: there is no {kind} in this world.', 'bad')
        return
    _k, nm, act = rows[n % len(rows)]
    d = game.world.dungeons[act[1]]
    lvl = depth or d.depth
    DBG.to_over(game, d.x, d.y)
    game.enter_dungeon(act[1], min(lvl, d.depth), 'down')
    game.request = ('save',)
    game.msg(f'Test: {nm}, level {min(lvl, d.depth)} of {d.depth}.', 'info')


def s_boss_dungeon(game, n):
    from . import data as D
    w = game.world
    rows = sorted((d for d in w.dungeons.values() if d.boss and getattr(d, 'site', None) is None),
                  key=lambda d: (_dist(game, d.x, d.y), d.name))
    if not rows:
        return
    d = rows[n % len(rows)]
    DBG.to_over(game, d.x, d.y)
    game.enter_dungeon(d.id, d.depth, 'down')
    game.request = ('save',)
    game.msg(f'Test: {d.name}, the boss floor ({D.MONSTERS.get(d.boss, {}).get("name", d.boss)}).', 'info')


RUNS = {}          # how often each line was set up this session: the next one of its kind
FAST = []          # the test sets it: time does not really run on (it is the slow part)


def _time(game, days):
    if FAST:
        game.msg(f'Test: {days:g} days would pass.', 'info')
        return
    DBG.days_ahead(game, days)


def s_days(game, n, days):
    _time(game, days)


def s_month(game, n, mo, day=1):
    if FAST:
        _time(game, 30)
        return
    DBG.to_month(game, mo)
    if day > 1:
        DBG.days_ahead(game, day - 1)


def s_hour(game, n, hour):
    """On to the next time this hour of the day comes (0-23)."""
    from . import data as D
    now = (game.turn % D.DAY_LEN) * 24 / D.DAY_LEN
    _time(game, ((hour - now) % 24 or 24) / 24)


def s_weekday(game, n, wd, hour=None):
    from . import calendar as CAL
    days = next(k for k in range(1, 8) if CAL.weekday(game.day + k) == wd)
    _time(game, days)
    if hour is not None:
        s_hour(game, n, hour)


def s_feast(game, n):
    """The next feast in turn: its date, then the nearest town that keeps it."""
    from . import feasts as FE
    f = FE.FEASTS[n % len(FE.FEASTS)]
    mo, d0, _days = f['when']
    s_month(game, n, mo, d0)
    w = game.world
    towns = sorted((s for s in w.settlements if FE.keeps(game, s, f['who'])),
                   key=lambda s: (_dist(game, s.x, s.y), s.name))
    sites = [s for s in w.sites if FE.keeps_site(s, f['who'])]
    if towns:
        DBG.teleport(game, ('s', towns[0].id))
    elif sites:
        DBG.teleport(game, ('site', sites[0].id))
    game.msg(f"Test: {f['name']}, kept by {f['who']}.", 'info')


def s_fair(game, n):
    """A human city at the start of its fair week."""
    from . import feasts as FE
    cities = sorted((s for s in game.world.settlements if s.is_city and FE._human(s)),
                    key=lambda s: (_dist(game, s.x, s.y), s.name))
    if not cities:
        return
    s = cities[n % len(cities)]
    mo, d0 = FE.fair_week(s)
    s_month(game, n, mo, d0)
    DBG.teleport(game, ('s', s.id))
    game.msg(f'Test: the Fair of Skell in {s.name}.', 'info')


def s_weather(game, n, *kinds):
    DBG.set_weather(game, kinds[n % len(kinds)])


def s_spawn(game, n, *kinds, sleep=False):
    from . import data as D
    k = kinds[n % len(kinds)]
    if k not in D.MONSTERS:
        game.msg(f'Test: no creature {k}.', 'bad')
        return
    mon = DBG.spawn(game, k)
    if mon is not None and sleep:
        mon.awake = False


def _item(query):
    q = query.lower()
    rows = DBG.item_list()
    return next((r for r in rows if r[1].lower() == q), None) or next((r for r in rows if q in r[1].lower()), None)


def s_give(game, n, *queries, rar='normal'):
    for q in queries:
        r = _item(q)
        if r:
            DBG.give(game, r[2], rar)
        else:
            game.msg(f'Test: no item called {q}.', 'bad')


def s_tome(game, n, line=None, tier=0, other=False):
    """A tome: of a school (line), of your own class's school, or of another school than yours."""
    from . import skills as SK
    from . import classes as CL
    mine = CL.classes(game)
    schools = [k for k in SK.DISC_ORDER if CL.class_line(k)]
    if other:
        line = [k for k in schools if k not in mine][n % (len(schools) - len(mine))]
    elif line is None:
        line = mine[0] if mine else schools[n % len(schools)]
    sk = next((s for s in SK.SKILL_LIST if s.line == line and s.tier == tier), None)
    if sk:
        DBG.give(game, ('tome', sk.id))


def s_class(game, n, line=None, rank=None):
    """Wake a class at once, as its first tome would (no question), and set its rank."""
    from . import classes as CL
    from . import skills as SK
    p = game.player
    if not CL.classes(game):
        schools = [k for k in SK.DISC_ORDER if CL.class_line(k)]
        p.classes = [line or schools[n % len(schools)]]
    if rank is not None:
        DBG.set_rank(game, p.classes[0], 'disc', rank)


def s_rank(game, n, key, rank):
    kind = 'life' if key in __import__('avarenthia.lifeskills', fromlist=['LIFE']).LIFE else 'disc'
    if key == 'class':
        from . import classes as CL
        c = CL.classes(game)
        if not c:
            return
        key, kind = c[0], 'disc'
    DBG.set_rank(game, key, kind, rank)


def s_coin(game, n, copper):
    DBG.give_coin(game, copper)


def s_lvl(game, n, lvl):
    p = game.player
    if p.lvl < lvl:
        DBG.level_up(game, lvl - p.lvl)


def s_flag(game, n, flag, on=True):
    if DBG.has(game, flag) != on:
        DBG.toggle(game, flag)


def s_event(game, n, *kinds):
    DBG.force_event(game, kinds[n % len(kinds)])


def s_standing(game, n, faction, value):
    DBG.set_standing(game, faction, value)


def s_guild(game, n, key, rank):
    DBG.set_guild(game, key, rank)


def s_hall(game, n, *keys):
    """Into a town where a guild keeps a hall (the next one with Enter again)."""
    halls = [(k, i) for k in keys for i in getattr(game.world, 'guild_halls', {}).get(k, ())]
    if not halls:
        game.msg('Test: no such hall in this world.', 'bad')
        return
    k, sid = halls[n % len(halls)]
    DBG.teleport(game, ('s', sid))
    game.msg(f'Test: {game.world.settlements[sid].name}, a hall of {k} ({n % len(halls) + 1} of {len(halls)}).', 'info')


def s_inn(game, n, who=None):
    """Beside the gaming table of an inn: of the next people each time, or of the next master of Vigil."""
    from . import inngames as IG
    from . import data as D
    w = game.world
    if who == 'master':
        sids = list(IG.masters(game))
    else:
        by = {}
        for st in w.settlements:
            if 'inn' in getattr(st, 'services', ()) or st.kind == 'deephold':
                by.setdefault('dwarf' if st.kind == 'deephold' else st.race, []).append(st.id)
        sids = [v[0] for k, v in sorted(by.items())]
    for k in range(len(sids)):
        sid = sids[(n + k) % len(sids)]
        DBG.teleport(game, ('s', sid))
        m = game.map
        gt = getattr(m, 'gametable', None)
        if gt is None:
            continue
        p = game.player
        p.x, p.y = next(((gt[0] + dx, gt[1] + dy) for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (1, -1),
                                                                  (-1, -1))
                         if game.map.inb(gt[0] + dx, gt[1] + dy) and game.map.tile(gt[0] + dx, gt[1] + dy) != IG.GAMETABLE
                         and D.TILES[m.tile(gt[0] + dx, gt[1] + dy)].walk
                         and not m.mon_at(gt[0] + dx, gt[1] + dy)), (p.x, p.y))
        game.compute_fov()
        master = IG.master_here(game)
        game.msg(f'Test: the gaming table of {w.settlements[sid].name} ({IG.people(game)})'
                 + (f', where {master} plays.' if master else '.'), 'info')
        return
    game.msg('Test: no inn with a gaming table found.', 'bad')


def s_maker(game, n, kinds=None, state=None, enter=True, depth=1):
    """A place of the more makers (makers.py): the next kind each time, or of these kinds; in a state when given
    ('cycle': the next of the 14 states each time, then a place with a break-in, at its bottom)."""
    from . import makers as MK
    ds = sorted((d for d in game.world.dungeons.values() if getattr(d, 'maker', None)
                 and (kinds is None or d.maker in ((kinds,) if isinstance(kinds, str) else kinds))),
                key=lambda d: (d.maker, d.id))
    if state == 'cycle':
        k = n % (len(MK.STATES) + 1)
        if k == len(MK.STATES):
            br = [d for d in ds if getattr(d, 'breakin', None)] or \
                [d for d in game.world.dungeons.values() if getattr(d, 'breakin', None)]
            if not br:
                game.msg('Test: no place breaks into another in this world.', 'bad')
                return
            d = br[0]
            DBG.to_over(game, d.x, d.y)
            game.enter_dungeon(d.id, d.depth, 'down')
            game.msg(f'Test: the bottom of {d.name}; its cracked wall gives onto '
                     f'{game.world.dungeons[d.breakin].name}.', 'info')
            game.request = ('save',)
            return
        ds = [d for d in ds if not d.boss] or ds
        state, ds = MK.STATES[k], ds[:1]
    if not ds:
        game.msg('Test: no such place in this world.', 'bad')
        return
    if kinds is None and state is None:                    # each kind once, in turn
        kinds_ = sorted({d.maker for d in ds})
        kind = kinds_[n % len(kinds_)]
        d = next(d for d in ds if d.maker == kind)
    else:
        d = ds[n % len(ds)]
    if state:
        MK.shift(game, d, state)
    DBG.to_over(game, d.x, d.y)
    if not enter:
        game.msg(f'Test: you stand at {d.name} ({d.maker}, {getattr(d, "state", "")}); [>] goes in.', 'info')
        return
    game.enter_dungeon(d.id, min(depth, d.depth), 'down')
    game.request = ('save',)
    game.msg(f'Test: {d.name}: {d.maker}, {getattr(d, "state", "")}, level {min(depth, d.depth)} of {d.depth}.', 'info')


def s_hire(game, n, *kinds):
    DBG.add_hireling(game, kinds[n % len(kinds)])


def s_job(game, n, *kinds):
    DBG.make_job(game, kinds[n % len(kinds)])


def s_dbg(game, n, fn, *args):
    """Any action of the debug menu by its name in debug.py."""
    getattr(DBG, fn)(game, *args)


def s_cycle_dbg(game, n, fn, *choices):
    """A debug action with the next of its choices each time."""
    getattr(DBG, fn)(game, choices[n % len(choices)])


def s_theme(game, n, part='middle'):
    from . import pieces as PC
    pcs = [pc for pc in PC.load() if pc.part == part]
    if pcs:
        pc = pcs[n % len(pcs)]
        DBG.theme_level(game, pc.name)
        game.msg(f'Test: the theme room {pc.name}, {n % len(pcs) + 1} of {len(pcs)}.', 'info')


def s_people_room(game, n):
    """The next theme room of a people (pieces with KIND people:...)."""
    from . import pieces as PC
    pcs = [pc for pc in PC.load() if pc.part == 'middle' and any(k.startswith('people:') for k in pc.kinds)]
    if not pcs:
        game.msg('Test: no rooms of a people among the pieces.', 'bad')
        return
    pc = pcs[n % len(pcs)]
    DBG.theme_level(game, pc.name)
    game.msg(f'Test: the theme room {pc.name}, {n % len(pcs) + 1} of {len(pcs)}.', 'info')


def s_entry(game, n):
    """The first level of the next kind of place with a way in of its own (delves.ENTRY)."""
    from . import delves as DV
    ds = {}
    for d in sorted(game.world.dungeons.values(), key=lambda d: d.id):
        k = DV.plan_for(d, 1)
        if k in DV.ENTRY and k not in ds:
            ds[k] = d
    if not ds:
        game.msg('Test: no place with a way in of its own in this world.', 'bad')
        return
    k = sorted(ds)[n % len(ds)]
    d = ds[k]
    DBG.to_over(game, d.x, d.y)
    game.maps.pop(f'{d.id}:1', None)
    game.enter_dungeon(d.id, 1, 'down')
    game.msg(f'Test: the way into {d.name} ({k}), {n % len(ds) + 1} of {len(ds)}.', 'info')
    game.request = ('save',)


def s_puzzle(game, n, wired=False):
    """The next example puzzle room (pieces/puzzles.des); wired: only rooms with switches or counters."""
    from . import pieces as PC
    pcs = [pc for pc in PC.load() if str(pc.file).endswith('puzzles.des') and (not wired or pc.switches or pc.counters)]
    pcs = pcs or [pc for pc in PC.load() if pc.part == 'middle']
    pc = pcs[n % len(pcs)]
    DBG.theme_level(game, pc.name)
    game.msg(f'Test: {pc.name}, {n % len(pcs) + 1} of {len(pcs)}.', 'info')


def s_boss(game, n, which='fixed'):
    from . import bosses as BS
    keys = [k for k in BS.KITS if bool(BS.KITS[k].get('roam')) == (which == 'roam')
            and (which != 'fixed' or not BS.KITS[k].get('theme'))]
    k = keys[n % len(keys)]
    s_deep(game, 0, 'dungeon')
    DBG.boss(game, ('roam:' if which == 'roam' else '') + k)


def s_note(game, n, text):
    """Only a line in the log: what to do by hand."""
    game.msg(f'Test: {text}', 'info')


def s_first(game, n, *stages):
    """The first steps (round 40), at a stage: the temple, the den, the letter, the city, the word, the war."""
    from . import firststeps as FS
    w, f = game.world, game.flags
    stage = stages[n % len(stages)]
    st = FS.st(game)
    if stage == 'temple':
        DBG.teleport(game, ('site', w.start_temple))
    elif stage == 'den':
        d = w.dungeons['den']
        DBG.to_over(game, d.x, d.y)
        game.enter_dungeon('den', d.depth, 'down')
    elif stage == 'letter':
        f['den'] = True
        st.pop('letter', None)
        DBG.teleport(game, ('s', 0))
    elif stage == 'guild':
        DBG.teleport(game, ('s', FS.letter_city(game).id))
        game.msg('Test: walk into a guild master of a fighting guild.', 'info')
    else:                                   # the city, the word, the war
        f['den'] = True
        if not st.get('letter'):
            FS.give_letter(game, None)
        DBG.teleport(game, ('s', FS.letter_city(game).id))
        if stage in ('word', 'war') and st.get('letter') == 'carried':
            trader = next((o for o in game.map.mons if getattr(o, 'role', '') == 'market'), None)
            if trader:
                FS.merchant(game, trader)
        if stage == 'war':
            DBG.force_event(game, 'realmwar')
    game.request = ('save',)
    game.msg(f'Test: the first steps, {stage}.', 'info')


def s_marked(game, n, k='orc', elite=1, every=True):
    """A champion or a unique beside you; with every, the next of the twenty affixes each time (with a fitting kind)."""
    from . import affixes as AF
    from . import data as D
    a = AF.AFFIXES[n % len(AF.AFFIXES)]
    kind = k
    if every:
        kind = next((c for c in (k, 'kob_slinger', 'skeleton', 'wolf', 'spider', 'orc_chief') if c in D.MONSTERS
                     and (AF.fits(c, a) or a == 'Warcry' and AF.leader(c))), k)
    mon = DBG.spawn(game, kind, elite)
    if mon is None:
        return
    if every:
        rest = [x for x in mon.mods if x != a and not {x, a} == {'Frost-touched', 'Fire-blooded'}]
        AF.apply(mon, [a] + rest[:elite])
    game.msg(f"Test: {mon.name}: {AF.label(mon)}.", 'info')


STEPS = {'to': s_to, 'near': s_near, 'crossing': s_crossing, 'over': s_over, 'deep': s_deep, 'bossfloor': s_boss_dungeon,
         'days': s_days, 'month': s_month, 'hour': s_hour, 'weekday': s_weekday, 'feast': s_feast, 'fair': s_fair,
         'weather': s_weather, 'spawn': s_spawn, 'give': s_give, 'tome': s_tome, 'class': s_class, 'rank': s_rank,
         'coin': s_coin, 'lvl': s_lvl, 'flag': s_flag, 'event': s_event, 'standing': s_standing, 'guild': s_guild,
         'hire': s_hire, 'job': s_job, 'dbg': s_dbg, 'dbgnext': s_cycle_dbg, 'theme': s_theme, 'peopleroom': s_people_room, 'entry': s_entry, 'puzzle': s_puzzle,
         'boss': s_boss, 'note': s_note, 'first': s_first, 'marked': s_marked, 'hall': s_hall,
         'maker': s_maker, 'inn': s_inn}

GOLD = 10 * 100 * 100
SCHOOLS_NOTE = ('note', 'Enter again for the next one.')

# ------------------------------------------------------------------ the recipes, one per line of testing.md
R = {
    # Heard, lit and seen
    'Heard, lit and seen :: Noise': [('deep', 'dungeon (rooms)', 1), ('dbg', 'foe_behind_wall'), ('give', 'Plate Mail'),
                                     ('note', 'walk, fight, cast, open doors; watch the ring and Quiet/Soft/Loud.')],
    'Heard, lit and seen :: What you hear': [('deep', 'dungeon (cave)', 1), ('dbg', 'foe_behind_wall', True),
                                             ('rank', 'cunning', 30), ('note', 'wait (5) and listen: the log, the sign.')],
    'Heard, lit and seen :: Noticing': [('deep', 'dungeon', 1), ('class', 'cunning', 20), ('tome', 'cunning', 1),
                                        ('spawn', 'goblin', 'skeleton', 'wolf', {'sleep': True}),
                                        ('note', 'sneak near it in the dark and in torchlight.')],
    'Heard, lit and seen :: Light that lives': [('deep', 'dungeon (rooms)', 1), ('class', 'fire', 20),
                                                ('tome', 'fire', 1), ('spawn', 'goblin'),
                                                ('note', 'cast fire in a dark hall; a storm tome puts out torches.')],
    'Heard, lit and seen :: Last seen': [('deep', 'dungeon (rooms)', 1), ('spawn', 'goblin'),
                                         ('note', 'step back round a corner: its dim letter stays.')],
    # The land tells
    'The land tells, and an inn in every town :: Signs on the land': [
        ('near', 'village'), ('hour', 11), ('dbg', 'ambush'),
        ('note', 'smoke over the village; walk on for the ambush; F12 [e] raid, then Time (days) for vultures and paths.')],
    'The land tells, and an inn in every town :: Villages rebuilt': [
        ('near', 'village'), ('dbgnext', 'burn_nearest', 0, 14, 30),
        ('note', 'go in: burnt; Enter again: fresh timber; again: whole.')],
    'The land tells, and an inn in every town :: An inn in every town': [('to', ('city', 'town', 'metropolis', 'deephold')),
                                                                         SCHOOLS_NOTE],
    # A roof of your own
    'A roof of your own :: A town house': [('to', ('hamlet', 'village', 'town', 'city', 'metropolis')), ('coin', 60 * GOLD),
                                           ('note', 'find the $ door and walk into it; Time (a season on) for the tax. '
                                                    'Enter again: the next people.')],
    'A roof of your own :: Building anywhere': [('dbg', 'home_stake'), ('coin', 200 * GOLD), ('dbg', 'home_goods'),
                                                ('note', 'use the stake (i), go in (>), the doorpost chest builds; '
                                                         'Time (days on). Enter again: elsewhere.')],
    'A roof of your own :: The risk': [('dbgnext', 'home_roll', 'theft', 'broken', 'squatters', 'fire', 'flood', 'snow', 'raid', 'evil'),
                                       ('note', 'go home and see; Enter again: the next outcome. Build a home first.')],
    'A roof of your own :: A seat': [('dbg', 'home_seat'), ('dbg', 'home_goods'),
                                     ('note', 'go in (>), buy it, restore it at the doorpost chest; a war: Realms.')],
    'A roof of your own :: Furnishing': [('dbg', 'home_furniture'), ('coin', 20 * GOLD),
                                         ('note', 'in your home press H; walk into each piece.')],
    # Camps on the road
    "Camps on the road :: A host's camp": [('dbgnext', 'camp_here', 'host', 'siege'), ('dbg', 'force_event', 'realmwar'),
                                           ('note', '[>] by it goes in; Time: Six hours for the dawn and the fire rings.')],
    "Camps on the road :: A traders' camp": [('dbg', 'camp_in', 'traders'), ('coin', 20 * GOLD),
                                             ('note', 'talk to the caravan master; sleep by the fire until robbers come.')],
    "Camps on the road :: Each people's camp": [('dbgnext', 'camp_here', 'host', 'siege', 'dwarf', 'elf', 'gorvash',
                                                 'sea', 'riders', 'traders'),
                                                ('note', 'Enter again for the next people; the elves show only from one cell.')],
    "Camps on the road :: Inside the tents": [('dbgnext', 'camp_try', 'host/friend', 'host/foe', 'dwarf/foe', 'gorvash/foe',
                                                           'sea/stranger', 'riders/foe', 'elf/friend'),
                                              ('note', 'walk into every tent; as a foe: the orders, the stores, the pen, a tent.')],
    # A first sight of a town
    'A first sight of a town :: The skyline card': [('dbg', 'forget_sights'),
                                                    ('to', ('hamlet', 'village', 'town', 'city', 'metropolis',
                                                            'deephold', 'glade', 'gnomes')),
                                                    ('note', 'Enter again for the next settlement; Time for the night.')],
    # The older rounds (lines added 13 November 2026)
    'Rounds 1-5: the first world :: Monsters of each kind': [('deep', 'dungeon', 1),
                                                             ('spawn', 'goblin', 'orc', 'skeleton', 'wolf', 'spider'),
                                                             SCHOOLS_NOTE],
    'Rounds 1-5: the first world :: Named enemies': [('to', 'lieutenant'), SCHOOLS_NOTE],
    'Rounds 1-5: the first world :: Guilds': [('to', 'city', None, 'human'), ('guild', 'magi', 2), ('coin', GOLD)],
    'Rounds 1-5: the first world :: Jobs': [('to', 'town', None, 'human'), ('job', 'bounty', 'courier'), SCHOOLS_NOTE],
    'Rounds 1-5: the first world :: Seasons on the world map': [('over',), ('month', 1), SCHOOLS_NOTE],
    'Rounds 1-5: the first world :: Sailing': [('to', 'city', None, 'harbour'), ('event', 'pirates')],
    'Weapons and the bestiary :: Each weapon kind': [('give', 'Spear', 'Light Crossbow', 'Dagger', 'Dagger'),
                                                     ('deep', 'dungeon', 1), ('spawn', 'goblin')],
    'Weapons and the bestiary :: The bestiary grows': [('deep', 'dungeon', 1), ('spawn', 'wolf'),
                                                       ('note', 'kill it, Enter again for another.')],
    'Magic :: The schools': [('tome', None), ('class', None, 20), SCHOOLS_NOTE],
    'Magic :: Spell effects on the ground': [('give', 'Tome of Firebolt', 'Tome of Frost Shard'), ('class', 'fire', 20),
                                             ('deep', 'dungeon', 1), ('spawn', 'goblin', 'orc')],
    'Magic :: Stamina': [('give', 'Plate Mail', 'Heavy Boots'), ('deep', 'dungeon', 1), ('spawn', 'goblin')],
    'Realms and the land :: Realms and wars': [('event', 'realmwar'), ('over',), ('days', 60)],
    'Realms and the land :: Walking the land': [('crossing',)],
    'Realms and the land :: Herds and hunting': [('rank', 'hunting', 30), ('rank', 'skinning', 30), ('over',),
                                                 ('days', 2)],
    'Realms and the land :: Nature and wonders': [('to', 'wonder'), SCHOOLS_NOTE],
    'Realms and the land :: Place names': [('over',), ('dbg', 'reveal_map')],
    'Realms and the land :: Ferries': [('to', 'ferryhut'), SCHOOLS_NOTE],
    'Realms and the land :: Keeping it clear': [('dbg', 'reset_tips'), ('deep', 'dungeon', 1), ('spawn', 'goblin')],
    'Realms and the land :: The handbook and the chronicle': [('note', 'press [?] for the handbook, [e] for the chronicle.')],
    'Life on the road :: Hirelings': [('hire', 'defender', 'warrior', 'archer', 'healer', 'mage'), ('coin', GOLD),
                                      SCHOOLS_NOTE],
    'Life on the road :: Hunger and cooking': [('rank', 'cooking', 20), ('give', 'plant'), ('over',), ('days', 2)],
    'Life on the road :: Fishing': [('give', 'Fishing Rod'), ('rank', 'fishing', 10), ('to', 'village')],
    'Life on the road :: Crime and the Watch': [('to', 'town', None, 'human'), ('hour', 23)],
    'Life on the road :: The temple and the gods': [('to', 'temple'), ('coin', GOLD), SCHOOLS_NOTE],
    'Life on the road :: Weather': [('over',), ('weather', 'rain'), ('note', 'F12, [w] for each other kind.')],
    'Life on the road :: Day and night': [('over',), ('hour', 21)],
    'Life on the road :: Death and the chronicle': [('dbgnext', 'tally_look', 'tally', 'death')],
    'Life on the road :: Trade at a market': [('coin', GOLD), ('to', 'city', None, 'human')],
    'Life on the road :: Herbs and potions at a shop': [('coin', GOLD), ('give', 'plant'), ('to', 'town', None, 'human')],
    'Life on the road :: Factions': [('standing', 'league', 60), ('standing', 'blackhand', 60), ('to', 'city', None, 'human')],
    'Life on the road :: Hostile camps of the tribes': [('to', ('poi orccamp', 'kobolds', 'gnolls')), SCHOOLS_NOTE],
    'Life on the road :: Dwarf holds and mines': [('rank', 'mining', 30), ('to', ('deephold', 'oldmine')), SCHOOLS_NOTE],
    "Life on the road :: The peoples' lands": [('to', ('glade', 'gnomes', 'town')), SCHOOLS_NOTE],
    'Life on the road :: Old ways': [('over',), ('dbg', 'reveal_map')],
    'Life on the road :: The harbour': [('to', 'city', None, 'harbour')],
    'Life on the road :: News through people': [('event', 'raid'), ('days', 3), ('to', 'town', None, 'human')],
    'Life on the road :: Libraries and the made history': [('to', 'city', None, 'human')],
    'Life on the road :: The underground rivers': [('dbgnext', 'theme_level', 'river:water', 'river:fire')],
    'Life on the road :: The Sky-Seat': [('dbg', 'shadow', 'reveal'), ('dbg', 'shadow', 'chain')],
    "Life on the road :: Ships on the land's waters": [('event', 'ship', 'rivals')],
    'Life on the road :: Arts of Cunning and Arcane': [('class', 'cunning', 20), ('tome', 'cunning', 1),
                                                       ('deep', 'dungeon', 1), ('spawn', 'goblin', {'sleep': True})],
    'The Varnish and the great evils :: The Varnish on the land': [('dbg', 'varnish_places'), ('to', 'vcity')],
    'The Varnish and the great evils :: The great evils': [('dbg', 'shadow', 'name'), ('dbg', 'shadow', 'wake'),
                                                           ('dbg', 'shadow', 'lairs')],
    # Games at the inn
    'Games at the inn :: Bones': [('inn',), ('hour', 19), ('coin', GOLD), ('class', 'cunning', 30),
                                  ('note', 'Enter again for the inn of the next people.')],
    'Games at the inn :: Vigil': [('inn', 'master'), ('note', 'Enter again for the next master; any inn plays too.')],
    'Games at the inn :: The Count': [('inn',), ('hour', 19), ('coin', GOLD), ('class', 'cunning', 30)],
    # Classes
    'Classes :: First class': [('tome', None)],
    'Classes :: Second class': [('class', None, 20), ('tome', None, 0, True)],
    'Classes :: Trees': [('class', None, 30), ('dbg', 'rested'), ('coin', GOLD)],
    'Classes :: Weapon skills': [('give', 'Long Sword'), ('rank', 'swords', 10)],
    'Classes :: Cunning and Arcane': [('class', 'cunning', 10), ('tome', 'cunning', 1), ('tome', 'cunning', 2),
                                      ('deep', 'dungeon', 1), ('spawn', 'goblin', {'sleep': True})],
    'Classes :: Pair and pure rules': [('class', None, 20), ('tome', None, 0, True)],
    'Classes :: Elites and weapon-guild skills': [('guild', 'magi', 4), ('guild', 'iron', 4), ('coin', GOLD)],
    'Classes :: Epics': [('class', None, 40), ('dbg', 'epics'), ('dbg', 'rested'), ('month', 11), ('hour', 22)],
    # The bar of seven keys
    'The bar of seven keys :: Four class keys': [('class', None, 30), ('tome', None, 1), ('tome', None, 2),
                                                 ('guild', 'magi', 4), ('guild', 'iron', 4), ('coin', GOLD),
                                                 ('to', 'town', None, 'human')],
    'The bar of seven keys :: The epic on key 7': [('class', None, 40), ('dbg', 'epics'), ('deep', 'dungeon', 1),
                                                   ('spawn', 'goblin')],
    'The bar of seven keys :: The bar after a rest': [('class', None, 20), ('tome', None, 1), ('tome', None, 2),
                                                      ('dbg', 'rested')],
    'The bar of seven keys :: Casting from the book': [('class', None, 20), ('tome', None, 1), ('tome', None, 2),
                                                       ('deep', 'dungeon', 1), ('spawn', 'goblin', {'sleep': True})],
    'The bar of seven keys :: The balance measure': [('note', 'run python tests/balance.py: it prints the table.')],
    # Cities that grew
    'Cities that grew, part 1 :: The heart': [('to', 'metropolis'), SCHOOLS_NOTE],
    'Cities that grew, part 1 :: Streets, lanes, rows, the wall': [('to', 'city', None, 'human')],
    'Cities that grew, part 1 :: The river and its bridges': [('to', 'city', None, 'river')],
    'Cities that grew, part 1 :: Canal and fortress towns': [('to', 'city', None, 'harbour')],
    'Cities that grew, part 1 :: Who lives where': [('to', 'city', None, 'human'), ('hour', 19)],
    'Cities that grew, part 2 :: Dwarf cities': [('to', 'city', None, 'dwarf')],
    'Cities that grew, part 2 :: Halfling towns': [('to', 'town', None, 'halfling')],
    'Cities that grew, part 2 :: Half-orc towns': [('to', 'town', None, 'orc')],
    'Cities that grew, part 2 :: Bridges on the land': [('crossing',)],
    # Feast days
    'Feast days :: Each feast where it is kept': [('feast',), SCHOOLS_NOTE],
    'Feast days :: The mask, the boot, the Light-Feast': [('feast',), SCHOOLS_NOTE],
    'Feast days :: The Fair of Skell': [('fair',)],
    # Round 6
    'Round 6: livelier settlements :: Work you can see': [('to', 'village'), ('days', 30)],
    'Round 6: livelier settlements :: Market day': [('to', 'town', None, 'human'), ('weekday', 'Starsday', 9)],
    'Round 6: livelier settlements :: The mood': [('event', 'raid'), ('to', 'town', None, 'human')],
    'Round 6: livelier settlements :: Happenings': [('to', 'town', None, 'human'), ('event', 'happening')],
    "Round 6: livelier settlements :: Each people's day": [('to', 'town', None, 'halfling'), ('hour', 12), SCHOOLS_NOTE],
    'Round 6: livelier settlements :: The poor quarter and shanty camps': [('event', 'lotus'), ('to', 'city', None, 'human'),
                                                                           ('hour', 23)],
    'Round 6: livelier settlements :: Refugees': [('dbg', 'shadow', 'wake'), ('dbg', 'shadow', 'month')],
    # Caravans
    'Trade part 3: caravans :: Your wagons': [('to', 'town', None, 'human'), ('event', 'wagons'), ('coin', GOLD)],
    'Trade part 3: caravans :: The road': [('event', 'wagons'), ('over',), ('month', 2)],
    'Trade part 3: caravans :: Raids and the land': [('event', 'wagons'), ('over',), ('event', 'wagonraid')],
    'Trade part 3: caravans :: The NPC caravans': [('to', 'town', None, 'human'), ('event', 'league')],
    # The boss maker
    'Boss fights part C: the boss maker :: Job bosses': [('lvl', 12), ('to', 'town', None, 'human'), ('job', 'bounty')],
    'Boss fights part C: the boss maker :: The end of it': [('lvl', 12), ('to', 'town', None, 'human'), ('job', 'bounty'),
                                                            ('note', 'follow the job to its end.')],
    'Boss fights part C: the boss maker :: Fixed bosses': [('bossfloor',)],
    # Trade part 2
    'Trade part 2: goods and ways :: Named goods and master works': [('coin', GOLD), ('to', 'city', None, 'human'),
                                                                     ('month', 0)],
    'Trade part 2: goods and ways :: Far goods, barter, monster goods': [('coin', GOLD), ('give', 'pelt'),
                                                                         ('to', 'city', None, 'harbour')],
    'Trade part 2: goods and ways :: Spoiling, need, war, contraband': [('event', 'realmwar'), ('month', 11),
                                                                        ('to', 'village')],
    'Trade part 2: goods and ways :: News and the League': [('coin', GOLD), ('to', 'city', None, 'human')],
    # Archaeology
    'Archaeology :: Dig spots': [('give', "Digger's Trowel"), ('rank', 'archaeology', 30), ('to', 'oldfield')],
    'Archaeology :: What the earth gives': [('flag', 'oldfind'), ('give', "Digger's Trowel"), ('rank', 'archaeology', 25),
                                            ('dbg', 'shadow', 'name'), ('to', 'oldfield')],
    'Archaeology :: Mending old pieces': [('give', 'Old piece, tier C', 'Varnish piece', 'star-iron'),
                                          ('rank', 'smithing', 40), ('to', 'town', None, 'human')],
    # Life skills part 2
    'Life skills part 2 :: Parts and powers': [('rank', 'skinning', 40), ('rank', 'smithing', 40),
                                               ('rank', 'leatherworking', 40), ('give', 'fang', 'Iron bar'),
                                               ('deep', 'dungeon', 1), ('spawn', 'brown_bear')],
    'Life skills part 2 :: Named beasts': [('rank', 'skinning', 45), ('rank', 'hunting', 50),
                                           ('give', 'Named beast part'), ('to', 'named beast')],
    'Life skills part 2 :: Catching alive': [('give', 'Coil of Rope'), ('rank', 'alchemy', 30), ('to', 'seat')],
    'Life skills part 2 :: Unmake and mending': [('rank', 'smithing', 50), ('give', 'Long Sword', {'rar': 'magic'}),
                                                 ('to', 'town', None, 'human')],
    'Life skills part 2 :: Masters': [('rank', 'fishing', 50), ('rank', 'mining', 50), ('give', 'Fey Silk', 'star-iron'),
                                      ('month', 0), ('weather', 'storm')],
    'Life skills part 2 :: The road': [('give', 'leather'), ('rank', 'leatherworking', 40), ('to', 'village')],
    # Life skills part 1
    'Life skills part 1 :: The curve and the colours': [('rank', 'smithing', 20), ('lvl', 20), ('give', 'Iron ore')],
    'Life skills part 1 :: Herbs and alchemy': [('rank', 'foraging', 20), ('rank', 'alchemy', 20), ('give', 'plant'),
                                                ('over',), ('hour', 22)],
    'Life skills part 1 :: Brewing': [('rank', 'brewing', 30), ('give', 'honey', 'barley', 'apple'),
                                      ('to', 'town', None, 'human')],
    'Life skills part 1 :: Fish by tier': [('rank', 'fishing', 40), ('to', 'village'), ('weather', 'storm')],
    'Life skills part 1 :: Smithing and Tailoring': [('rank', 'mining', 30), ('rank', 'smithing', 30),
                                                     ('rank', 'tailoring', 30), ('give', 'Iron ore', 'Iron bar', 'cloth'),
                                                     ('to', 'town', None, 'human')],
    # K5
    'The K5 maker :: Theme rooms': [('theme', 'middle'), SCHOOLS_NOTE],
    'The K5 maker :: Arrival and bottom rooms': [('theme', 'bottom'), SCHOOLS_NOTE],
    'The K5 maker :: Rivers underground': [('dbgnext', 'theme_level', 'river:water', 'river:fire')],
    'The K5 maker :: Rock you can see, mood lines of plain rooms, sizes': [('deep', 'dungeon', 1), SCHOOLS_NOTE],
    'The K5 maker :: Rooms of a people': [('peopleroom',)],
    'The K5 maker :: The way in': [('entry',)],
    # Places part 1
    'Places on their own land, part 1 :: Temples of every people': [('to', 'temple'), SCHOOLS_NOTE],
    'Places on their own land, part 1 :: The older bottom': [('dbg', 'old_tale'), ('to', 'temple', None, 'older')],
    'Places on their own land, part 1 :: Towers': [('to', 'tower'), ('hour', 22), SCHOOLS_NOTE],
    'Places on their own land, part 1 :: Fallen towers, edges and falls': [('to', 'tower', None, 'fallen'), SCHOOLS_NOTE],
    'Places on their own land, part 1 :: Barrows': [('to', 'barrow'), SCHOOLS_NOTE],
    # Places part 2
    'Places on their own land, part 2 :: Abbeys, forts and manors of every people': [('to', 'abbey'), SCHOOLS_NOTE],
    'Places on their own land, part 2 :: Who holds a fort': [('to', 'fort'), ('dbg', 'fort_holder')],
    'Places on their own land, part 2 :: The ways in': [('standing', 'crown', -50), ('to', 'fort'), SCHOOLS_NOTE],
    'Places on their own land, part 2 :: Underground kinds': [('deep', 'dungeon', 1), SCHOOLS_NOTE],
    'Places on their own land, part 2 :: The goblin village': [('to', 'ravine')],
    # Northern lights
    "The northern lights' gift :: Rune stones and milestones": [('flag', 'aurora'), ('to', 'poi runestone'), ('hour', 22)],
    "The northern lights' gift :: Frost and Storm": [('flag', 'aurora'), ('class', 'frost', 20), ('tome', 'frost', 1)],
    "The northern lights' gift :: Barrow spirits": [('flag', 'aurora'), ('to', 'barrow', None, 'north'), ('hour', 22)],
    "The northern lights' gift :: The glow": [('flag', 'aurora'), ('deep', 'dungeon', 1), ('spawn', 'ghost', 'imp')],
    # The Rift
    'The Rift and the Ashen Deep :: The rift on the land': [('dbg', 'open_rift'), ('days', 60)],
    'The Rift and the Ashen Deep :: Under a deep dungeon': [('dbg', 'open_rift'), ('deep', 'dungeon', 0)],
    'The Rift and the Ashen Deep :: The levels': [('dbg', 'open_rift'), ('deep', 'dungeon (rift)', 1)],
    'The Rift and the Ashen Deep :: The creatures': [('deep', 'dungeon', 1), ('spawn', 'cinderling', 'chain_warden', 'ashwalker', 'brimstone_toad', 'slag_brute', 'gaoler')],
    'The Rift and the Ashen Deep :: The Lord of Cinders and the gate': [('dbg', 'open_rift'), ('flag', 'god'),
                                                                        ('deep', 'dungeon (rift)', 0)],
    # Old places, part A
    'Part A: the old, lived-in world :: Old battlefield': [('flag', 'oldnight'), ('flag', 'oldfind'), ('to', 'oldfield'),
                                                           ('hour', 23)],
    'Part A: the old, lived-in world :: Deserted village': [('to', 'deserted')],
    'Part A: the old, lived-in world :: Broken bridge': [('to', 'oldbridge')],
    'Part A: the old, lived-in world :: Memorials': [('to', ('namestone', 'fallenking', 'gallows', 'mixgrave')), SCHOOLS_NOTE],
    'Part A: the old, lived-in world :: Old quarry': [('to', 'quarry')],
    'Part A: the old, lived-in world :: Shipwreck': [('to', 'wreck'), ('hour', 6)],
    'Part A: the old, lived-in world :: Hermitage': [('to', 'hermitage')],
    'Part A: the old, lived-in world :: Leper colony': [('to', 'colony'), ('job', 'alms')],
    'Part A: the old, lived-in world :: Marks of the peoples': [('to', ('bstone', 'poi moonstone', 'poi skullpole', 'poi scratch', 'poi dwarfstone')), SCHOOLS_NOTE],
    # The Varnish
    'The Varnish :: Varnish ruins in the wild': [('dbg', 'varnish_places'), ('to', 'vcity')],
    'The Varnish :: Hidden dungeons': [('dbg', 'varnish_places'), ('to', 'vcity')],
    'The Varnish :: The Varnish places': [('dbg', 'varnish_places'), ('to', ('walltower', 'windtower', 'deadroad', 'forge', 'gate', 'sluice', 'fallensky', 'starhouse', 'poi leaguestone')), SCHOOLS_NOTE],
    'Archaeology :: Dig spots seen by rank': [('give', "Digger's Trowel"), ('rank', 'archaeology', 50),
                                              ('to', 'oldfield')],
    'Archaeology :: Gives lore fragments (the five riddles), star-iron': [('dbg', 'varnish_places'),
                                                                          ('give', 'Varnish piece', 'star-iron'),
                                                                          ('rank', 'smithing', 40)],
    "The Varnish' own lore and books :: Fragments": [('dbg', 'varnish_places'), ('to', 'vcity')],
    "The Varnish' own lore and books :: Books bound from pages": [('dbg', 'varnish_places'), ('dbg', 'varnish_pages'),
                                                                  ('coin', GOLD), ('to', 'city', None, 'human')],
    "The Varnish' own lore and books :: What some books add": [('dbg', 'varnish_places'), ('dbg', 'varnish_pages'),
                                                               ('coin', GOLD), ('to', 'city', None, 'human')],
    'Part B: newer places :: Logging camp, charcoal burners, peat cutters, salt': [('to', ('logcamp', 'charcoal', 'peat', 'saltpan', 'lighthouse', 'tollbridge', 'lodge', 'beacon', 'shanty')), SCHOOLS_NOTE],
    "Places of today's peoples and powers :: Realms, Church, the Watch, companies, revolt and p": [('to', ('othershrine', 'watchtree', 'duelring', 'dwarfroad', 'witchcot', 'orderkeep', 'watchfort', 'outlaws', 'tithe', 'pcross', 'gravetree', 'hedgegate', 'orcfarm', 'blockhouse')), SCHOOLS_NOTE],
    'More places :: The land itself, people who live apart, where peop': [('to', ('hotspring', 'cenote', 'airshaft', 'bothy', 'exiles', 'loneinn', 'waymarket', 'peacestone', 'cache', 'still', 'lure')), SCHOOLS_NOTE],
    'Seasonal places :: Each only in its season': [('days', 90), ('over',)],
    'Feast days :: Each feast only in its own region, people or faith': [('feast',), SCHOOLS_NOTE],
    "Feast days :: Wanderer's Eve": [('month', 11, 5), ('to', 'town', None, 'human')],
    'Feast days :: The Masking': [('feast',), SCHOOLS_NOTE],
    'The five riddles :: Each riddle in The Old Days under its title, with ': [('dbg', 'varnish_places'),
                                                                               ('dbg', 'varnish_pages'), ('to', 'vdeep')],
    # The Counted Sky in the game
    'The Counted Sky in the game :: The made-even lore': [('dbg', 'varnish_places'), ('dbg', 'varnish_pages'),
                                                          ('coin', GOLD), ('to', 'city', None, 'human')],
    "The Counted Sky in the game :: The peoples' books": [('dbg', 'folk_pages'), ('to', 'town', None, 'dwarf'),
                                                          ('note', 'Enter again for the next dwarf town; Teleport to '
                                                                   'a glade, a gnome hamlet, a northern hall.')],
    "The Counted Sky in the game :: The peoples' voices": [('to', 'town', None, 'elf'), SCHOOLS_NOTE],
    "The Counted Sky in the game :: Bardin, the altar stone, Ferro, Tam's tally": [
        ('dbg', 'story_places'), ('to', ('granary', 'altarstone', 'vcity', 'walltower')), SCHOOLS_NOTE],
    'The Counted Sky in the game :: The dark ring, Aerith, the goblin drains': [
        ('dbg', 'story_places'), ('dbg', 'varnish_places'), ('dbg', 'shadow', 'reveal'), ('to', 'starhouse')],
    'The Counted Sky in the game :: The Wall on the world map': [('dbg', 'varnish_places'), ('over',)],
    'The Counted Sky in the game :: The court under the hill': [('dbg', 'fey', 'hill'), ('dbg', 'fey', 'night'),
                                                                ('dbg', 'fey', 'door')],
    # The great evils
    'The great evils as storyteller :: The servants': [('dbg', 'shadow', 'name'), ('dbg', 'shadow', 'wake'),
                                                       ('dbg', 'shadow', 'lairs')],
    'The great evils as storyteller :: The two clocks': [('dbg', 'shadow', 'up'), ('dbg', 'shadow', 'month')],
    'The great evils as storyteller :: The realms': [('dbg', 'shadow', 'wake'), ('dbg', 'shadow', 'month'),
                                                     ('dbg', 'shadow', 'month')],
    'The great evils as storyteller :: The quest': [('dbg', 'shadow', 'reveal'), ('dbg', 'shadow', 'relic'),
                                                    ('dbg', 'shadow', 'chain')],
    'The great evils as storyteller :: Dying there': [('dbg', 'shadow', 'reveal'), ('dbg', 'shadow', 'f1')],
    'The great evils as storyteller :: The ends': [('note', 'the Shadow page: "Let him win" or "Kill him".')],
    # Trade as a way to play
    'Trade as a way to play :: The money': [('coin', GOLD), ('to', 'town', None, 'human')],
    'Trade as a way to play :: Goods with a name': [('coin', GOLD), ('to', 'city', None, 'human')],
    'Trade as a way to play :: Master makers': [('coin', GOLD), ('to', 'city', None, 'human')],
    'Trade as a way to play :: The other ways': [('coin', GOLD), ('event', 'lotus'), ('to', 'city', None, 'human')],
    'Trade as a way to play :: Your caravan': [('to', 'town', None, 'human'), ('event', 'wagons'), ('coin', GOLD)],
    'Trade as a way to play :: The NPC caravans': [('to', 'town', None, 'human'), ('event', 'league')],
    # Boss fights
    'Boss fights :: A fixed boss': [('flag', 'god'), ('boss', 'fixed'), SCHOOLS_NOTE],
    'Boss fights :: A made boss': [('lvl', 12), ('to', 'town', None, 'human'), ('job', 'bounty')],
    'Boss fights :: The rhythm': [('flag', 'rhythm'), ('boss', 'fixed')],
    'Boss fights :: Marks and fairness': [('boss', 'fixed'), ('dbg', 'boss', 'fair'), SCHOOLS_NOTE],
    'Boss fights :: Spent, staggered, breaking, Resolve, breaking through a phase': [('boss', 'fixed'),
                                                                                     ('dbg', 'boss', 'spent')],
    'Boss fights :: Helpers and twins': [('boss', 'fixed'), ('dbg', 'boss', 'twin')],
    'Boss fights :: The arena': [('boss', 'fixed'), ('dbg', 'boss', 'seal')],
    'Boss fights :: Roaming bosses': [('boss', 'roam'), SCHOOLS_NOTE],
    'Boss fights :: Arenas by place and ways out': [('flag', 'god'), ('bossfloor',), ('dbg', 'reveal_map'), SCHOOLS_NOTE],
    'Boss fights :: The place answers': [('flag', 'god'), ('bossfloor',),
                                         ('note', 'kill the boss, then go up and out into the daylight.')],
    'Boss fights :: Won another way': [('lvl', 10), ('to', 'town', None, 'human'), ('job', 'shrine', 'boats', 'missing'),
                                       SCHOOLS_NOTE],
    'Boss fights :: The big one and the relic': [('lvl', 10), ('to', 'town', None, 'human'), ('job', 'bigone', 'relic'),
                                                 ('give', 'Fishing Rod'), SCHOOLS_NOTE],
    'Boss fights :: Hirelings in a boss fight': [('hire', 'defender', 'warrior', 'archer', 'healer', 'mage'),
                                                 ('boss', 'fixed')],
    # Places of today
    'Places of today :: Each place': [('to', 'serai'), SCHOOLS_NOTE],
    'Places of today :: Toll bridge, serai, beacons': [('event', 'realmwar'), ('to', 'tollbridge'), ('hour', 22)],
    'Places of today :: Coming and going': [('event', 'realmwar'), ('event', 'star'), ('event', 'raid')],
    # Odd corners
    "Odd corners and the seasons' places :: Each place": [('to', ('mill', 'hwell', 'ltree', 'lovetree', 'stump', 'boneyard', 'wcairn', 'beehill', 'beegarden', 'midden', 'burntgrove', 'harvstone')), SCHOOLS_NOTE],
    "Odd corners and the seasons' places :: Part of the year": [('month', 6), ('over',)],
    "Odd corners and the seasons' places :: The cache": [('to', 'wrongmile')],
    "Odd corners and the seasons' places :: The Standing Night, the Loosing": [('month', 11, 21), ('hour', 22)],
    # The editor
    'The Avarenthia Editor :: The editor itself': [('note', 'open the Avarenthia Editor of the test download.')],
    'The Avarenthia Editor :: Puzzle things': [('puzzle',), SCHOOLS_NOTE],
    'The Avarenthia Editor :: Creatures from lists, dressing in the game': [('theme', 'middle'), SCHOOLS_NOTE],
    'The Avarenthia Editor :: Switches, counters, timers, "back as drawn"': [('puzzle', True), SCHOOLS_NOTE],
    'The Avarenthia Editor :: Own tiles and things': [('note', 'F5 Try in the editor on a room with own tiles.')],
    'The Avarenthia Editor :: More doors': [('theme', 'middle'), SCHOOLS_NOTE],
    'The Avarenthia Editor :: Whole places': [('to', 'drawn'), ('dbg', 'reveal_map')],
    'The Avarenthia Editor :: Whole places in the editor': [('note', 'in the editor: Ctrl+N, "A whole place".')],
    'A window that fits :: Sizes and Zoom': [('note', 'resize the window or F12, [r] Window size; Zoom on the title screen.')],
    'A window that fits :: The margin': [('note', 'F12, [r] Window size 5120 x 1440; [G] for a new stretch of the margin.')],
    'The Avarenthia Editor :: Makers in the editor': [('note', 'in the editor: Ctrl+G; a rectangle first for a maker area.')],
    # Playing it
    'Playing it :: A note for Claude': [('note', 'F12, [N]: write one line, and find the zip beside the save.')],
    'Playing it :: Saves that last': [('note', "keep a save of the build before this one and load it here.")],
    'Playing it :: The money check': [('note', 'python tests/money.py prints the three tables.')],
    'Playing it :: What you met': [('note', "F12, [M]: met with the day, then never met; the note's zip holds met.txt.")],
    'Playing it :: The first tome': [('first', 'den', 'temple'), ('coin', 2000)],
    'Playing it :: The Eleven Ways': [('first', 'temple', 'guild'), ('coin', 2000)],
    'Playing it :: A letter for the city': [('first', 'letter', 'city')],
    "Playing it :: The baron's word": [('first', 'word', 'war')],
    # A finer look
    'A finer look, not busier :: Remembered land and roads': [('to', ('town', 'city')), ('dbg', 'reveal_map'),
                                                              ('hour', 12)],
    "A finer look, not busier :: Each level's tint": [('deep', ('dungeon (cave)', 'dungeon (rooms)', 'dungeon (rift)',
                                                                'dungeon (barrow)'), 1),
                                                       ('note', 'walk away from what you saw: it keeps the tint of its kind.')],
    'A finer look, not busier :: Fade-in': [('deep', 'dungeon (cave)', 1),
                                            ('note', 'take the stairs with Spell effects full, short and off (Esc menu).')],
    'A finer look, not busier :: Names and panel': [('to', ('town', 'city')), ('dbg', 'reveal_map'),
                                                    ('spawn', 'goblin', 'orc', 'kobold')],
    'A finer look, not busier :: Names in the log': [('spawn', 'goblin', 'orc'), ('give', 'Greater Health Potion'),
                                                     ('give', 'Long Sword', {'rar': 'magic'})],
    # The belt and the tally
    'The belt and the tally :: Potion grades': [('give', 'Minor Health Potion'), ('give', 'Greater Health Potion'),
                                                ('give', 'Superior Mana Potion'), ('to', ('village', 'town', 'city'))],
    'The belt and the tally :: The belt': [('give', 'Sash'), ('give', 'Plated Belt'), ('give', 'Greater Health Potion'),
                                           ('give', 'Mana Potion'), ('spawn', 'goblin', {'sleep': True})],
    'The belt and the tally :: Drinking from the pack': [('give', 'Health Potion'), ('give', 'Minor Health Potion'),
                                                         ('give', 'Minor Mana Potion'), ('spawn', 'goblin', {'sleep': True}),
                                                         ('note', 'drink the pockets dry with Shift+1, 2: then q rummages.')],
    'The belt and the tally :: The tally': [('dbgnext', 'tally_look', 'tally', 'death', 'win')],
    # Folk in need
    'Folk in need :: Folk with a need': [('to', ('village', 'town', 'city')),
                                         ('dbgnext', 'folk_need', 'beasts', 'nest', 'named', 'news', 'season', 'scarce',
                                          'realm', 'old', 'kin', 'trade', 'feast', 'people', 'watch'), SCHOOLS_NOTE],
    'Folk in need :: Twists and seeds': [('to', ('village', 'town', 'city')),
                                         ('dbgnext', 'folk_twist', 'young', 'worse', 'child', 'stay', 'liar', 'rival',
                                          'sold', 'cursed', 'late', 'wrong', 'bewitched', 'weather', 'opposite', 'hidden',
                                          'captive', 'sick', 'danger', 'more'), ('dbg', 'folk_seed', 0),
                                         ('dbg', 'folk_next'), SCHOOLS_NOTE],
    'Folk in need :: Rewards and favours': [('to', ('village', 'town')), ('dbg', 'folk_need'),
                                            ('give', 'Favour: Hob\'s ferry token'), ('give', "Favour: Hob's word at the gate"),
                                            ('give', "Favour: Hob's letter of thanks"), ('give', "Favour: Hob's carved whistle"),
                                            ('note', 'a ferry, a town where you are wanted (crime), a lord, a shut pass.')],
    # Marked creatures
    'Marked creatures :: Each affix': [('deep', 'dungeon', 1), ('marked', 'orc', 1), ('marked', 'orc', 2),
                                       ('give', 'Flail'), ('give', 'War Hammer'), ('give', 'Short Bow'), SCHOOLS_NOTE],
    'Marked creatures :: Fit and rarity': [('deep', ('dungeon (rift)', 'dungeon (cave)'), 1), ('month', 1),
                                           ('marked', 'wolf', 2, False), ('dbg', 'reveal_map'), SCHOOLS_NOTE],
    'Marked creatures :: Seen and told': [('deep', 'dungeon', 1), ('dbg', 'reset_tips'), ('marked', 'goblin', 2, False)],
    # Crafts guilds
    'Crafts guilds :: The four new guilds': [('hall', 'hammer', 'lodge', 'needle', 'ladle'), ('rank', 'smithing', 22),
                                             ('coin', GOLD), SCHOOLS_NOTE],
    'Crafts guilds :: Bench, test and mark': [('hall', 'hammer'), ('guild', 'hammer', 2), ('rank', 'smithing', 25),
                                              ('give', 'Iron Bar'), ('give', 'Deepiron Bar'), ('coin', GOLD)],
    'Crafts guilds :: Board, secrets, day': [('hall', 'hammer', 'lodge', 'needle', 'ladle'), ('guild', 'hammer', 3),
                                             ('guild', 'lodge', 3), ('guild', 'needle', 3), ('guild', 'ladle', 3),
                                             ('rank', 'smithing', 30), ('event', 'guildday'), ('coin', GOLD)],
    'Crafts guilds :: Streets and happenings': [('hall', 'hammer', 'lodge', 'needle'), ('event', 'happening'),
                                                ('note', 'look by the hall door: hides on racks, the dyers\' vats.')],
    'Crafts guilds :: Guild jobs': [('hall', 'hammer', 'lodge', 'needle', 'ladle'), ('guild', 'hammer', 3),
                                    ('guild', 'lodge', 2), ('guild', 'needle', 2), ('guild', 'ladle', 3),
                                    ('rank', 'smithing', 30), ('rank', 'leatherworking', 15), ('rank', 'tailoring', 15),
                                    ('note', 'ask the master for guild work of the hall; the tanners\' or the dyers\' '
                                             'master for the quarrel.')],
    # More makers
    'More makers :: Each new maker': [('maker',), ('dbg', 'reveal_map'), SCHOOLS_NOTE],
    'More makers :: States and break-ins': [('maker', None, 'cycle'), ('dbg', 'reveal_map'),
                                            ('note', 'Enter again for the next state; the 15th is a cracked wall '
                                                     'at the bottom of a place: walk into it.')],
    'More makers :: States shifting': [('maker', ('fallenhold', 'castle'), 'besieged', False), ('days', 22),
                                       ('note', 'a siege nobody broke: go in, the plunderers have it now.')],
    'More makers :: Time and season places': [('maker', ('tidecave', 'drowned', 'feyhill'), None, False),
                                              ('note', 'the tide cave: wait for the tide (Time); the drowned village '
                                                       'opens only in summer (Time, month 7); out of the fey hill a '
                                                       'week has gone by. Enter again for the next one.')],
    # The test menu
    'The test menu :: Tests page': [('note', 'tick this line with [y], restart, and see it kept.')],
    'The test menu :: Note for Claude and ✗': [('note', 'F12, [N]: write one line, and find the zip beside the save.')],
}
RECIPES = R


def recipe(key):
    return RECIPES.get(key)


def run(game, key, n=0):
    """Set a line up: run each step of its recipe (n picks the next of its kind)."""
    rec = recipe(key)
    if rec is None:
        game.msg('Test: this line has no setup yet.', 'bad')
        return False
    for step in rec:
        fn, args = STEPS[step[0]], list(step[1:])
        kw = {}
        if args and isinstance(args[-1], dict):
            kw = args.pop()
        fn(game, n, *args, **kw)
    return True


def show_check(game, row):
    """The line's what-to-check, in the log, so it stands over the game when the menu closes."""
    from .canvas import wrap_text
    for i, ln in enumerate(wrap_text(f'Check: {row[3]}', 100)):
        game.msg(ln, 'gold')
