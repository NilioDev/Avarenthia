"""The debug menu's rules: a tool for testing, not part of the game (see "Debug menu and a test build" in
docs/plan.md). It is on only in the test build ("Avarenthia (test)") or from the source with --debug; the normal
download has no way to turn it on. Its screens are in debug_ui.py. Not in the handbook.

Whatever it switches on for you (god mode, sight off...) lives on the player, as everything of the player does."""
import os
import pickle
import time
import zlib
from collections import deque

from . import data as D

ON = False                      # set once at start by main.py
KEYS = deque(maxlen=200)        # the last keys pressed, for a bug report
SLOTS = 3
FLAGS = ('god', 'sight', 'ai', 'coords')
FLAG_NAME = {'god': 'God mode', 'sight': 'Sight off', 'ai': 'AI state on look', 'coords': 'Coordinates in the status line',
             'aurora': 'Northern lights in the sky', 'oldfind': 'Old finds: a blade, nothing breaks',
             'oldnight': 'The dead walk old fields every night', 'rhythm': "A boss's rhythm under IN SIGHT"}


def turn_on(argv=(), environ=None, here=None, frozen=False):
    """Decide whether the debug menu is on. A frozen build turns it on only when it was built as the test build
    (a TESTBUILD file packed with it); from the source --debug or AVARENTHIA_DEBUG=1 does."""
    global ON
    environ = os.environ if environ is None else environ
    if frozen:
        ON = bool(here) and os.path.exists(os.path.join(here, 'TESTBUILD'))
    else:
        ON = '--debug' in argv or environ.get('AVARENTHIA_DEBUG') == '1'
    return ON


def flags(game):
    p = game.player
    if not hasattr(p, 'dbg'):
        p.dbg = {'coords'}
    return p.dbg


def has(game, flag):
    return ON and flag in getattr(game.player, 'dbg', {'coords'} if flag == 'coords' else ())


def toggle(game, flag):
    f = flags(game)
    f.symmetric_difference_update({flag})
    on = flag in f
    game.msg(f"Debug: {FLAG_NAME[flag]} {'on' if on else 'off'}.", 'info')
    if flag == 'sight':
        game.compute_fov()
    return on


def record_key(tok):
    if ON:
        KEYS.append(tok)


# ------------------------------------------------------------------ files
def folder():
    from . import engine as E
    return os.path.dirname(E.save_path())


def snap_path(i):
    return os.path.join(folder(), f'debug_snap{i}.sav')


def write_game(game, path):
    from . import engine as E
    with open(path + '.tmp', 'wb') as f:
        f.write(E.SAVE_MAGIC + zlib.compress(pickle.dumps(game, protocol=pickle.HIGHEST_PROTOCOL), 6))
    os.replace(path + '.tmp', path)


def read_game(path):
    from . import engine as E
    with open(path, 'rb') as f:
        raw = f.read()
    g = pickle.loads(zlib.decompress(raw[len(E.SAVE_MAGIC):]) if raw.startswith(E.SAVE_MAGIC) else raw)
    if getattr(g, 'version', 0) != E.SAVE_VERSION:
        return None
    g.events, g.request = [], None
    return g


def place_line(game):
    p = game.player
    wx, wy = game.world_pos()
    return f'{game.loc_name()} ({p.x},{p.y}), world {wx},{wy}'


def snap_info(i):
    """One line about what lies in a snapshot slot, or None when it is empty."""
    try:
        with open(snap_path(i) + '.txt', encoding='utf-8') as f:
            return f.read().strip()
    except OSError:
        return None


def save_snapshot(game, i):
    write_game(game, snap_path(i))
    info = f'{game.player.name}, turn {game.turn}, {place_line(game)}'
    with open(snap_path(i) + '.txt', 'w', encoding='utf-8') as f:
        f.write(info + '\n')
    game.msg(f'Debug: snapshot {i} saved.', 'info')


def load_snapshot(i):
    if not os.path.exists(snap_path(i)):
        return None
    try:
        return read_game(snap_path(i))
    except Exception:
        return None


def bug_report(app, note=''):
    """A folder with all it takes to replay a bug: what you wrote, the seed, the place, the turn, the last 200 lines of
    the log and keys, the screen as text (and as a picture, saved by main.py on the next frame) and the save."""
    from . import calendar as CAL
    game = app.game
    stamp = time.strftime('%Y%m%d-%H%M%S')
    base = os.path.join(folder(), 'bug-reports', stamp)
    path, k = base, 1
    while True:                                     # two reports in one second each get a folder of their own
        try:
            os.makedirs(path)
            break
        except FileExistsError:
            k += 1
            path = f'{base}-{k}'
    p = game.player
    lines = [f'What went wrong: {note or "(nothing written)"}',
             f'When: {time.strftime("%Y-%m-%d %H:%M:%S")}',
             f'Seed: {game.seed}', f'Save version: {game.version}',
             f'Hero: {p.name}, {p.race}, level {p.lvl}, life {p.life}, {"hardcore" if p.hardcore else "softcore"}',
             f'Place: {place_line(game)}', f'Map: {game.cur} ({game.map.kind}, {game.map.w}x{game.map.h})',
             f'Turn: {game.turn}, day {game.day}, {CAL.long(game.day)}',
             f'Debug flags: {", ".join(sorted(flags(game))) or "none"}']
    with open(os.path.join(path, 'report.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    with open(os.path.join(path, 'log.txt'), 'w', encoding='utf-8') as f:
        f.writelines(f'{t}\n' for t, _c in game.log[-200:])
    with open(os.path.join(path, 'keys.txt'), 'w', encoding='utf-8') as f:
        f.write(' '.join(KEYS) + '\n')
    with open(os.path.join(path, 'screen.txt'), 'w', encoding='utf-8') as f:
        f.write(screen_text(app) + '\n')
    write_game(game, os.path.join(path, 'save.dat'))
    app.shot = os.path.join(path, 'screen.png')
    game.msg(f'Debug: bug report written to {path}', 'info')
    return path


def screen_text(app):
    """The screen as text, drawn without the debug menu on top."""
    from .canvas import FakeCanvas
    from . import debug_ui as DU
    keep_cv, keep_screens = app.cv, app.screens
    app.cv = FakeCanvas(keep_cv.w, keep_cv.h)
    app.screens = [s for s in keep_screens if not isinstance(s, DU.DebugScreen)] or keep_screens
    try:
        app.render()
        return app.cv.dump()
    except Exception as ex:
        return f'(the screen could not be drawn: {ex})'
    finally:
        app.cv, app.screens = keep_cv, keep_screens


# ------------------------------------------------------------------ the world
def reveal_map(game):
    om = game.maps['over']
    for i in range(len(om.seen)):
        om.seen[i] = 1
    game.msg('Debug: the whole world map is known.', 'info')


def places(game):
    """Every place you can teleport to: (kind label, name, action) where action is ('s', id) and so on."""
    w = game.world
    out = []
    for s in w.settlements:
        out.append((s.kind, s.name, ('s', s.id)))
    for did, d in w.dungeons.items():
        if getattr(d, 'site', None) is not None:      # a place's floors and deeps: reached through the place
            continue
        out.append((f'dungeon ({d.style})', d.name, ('d', did)))
    from . import places as PL
    for s in w.sites:
        kind = s.kind
        if PL.is_place(s):                      # temples, towers, barrows, abbeys, forts, manors by people and state
            bits = [PL.people_of(s)]
            if getattr(s, 'state', 'whole') != 'whole':
                bits.append(s.state)
            if getattr(w.dungeons.get(getattr(s, 'below', None)), 'older', False):
                bits.append('older below')
            kind = f"{'abbey' if s.kind == 'monastery' else s.kind} ({', '.join(bits)})"
        out.append((kind, s.name, ('site', s.id)))
    for h in w.holds:
        out.append((h.kind, getattr(h, 'title', h.name), ('h', h.id)))
    for q in w.pois:
        out.append((f'poi {q.kind}', q.name, ('xy', q.x, q.y)))
    for name, x, y in w.wonders:
        out.append(('wonder', name, ('xy', x, y)))
    for nb in getattr(w, 'named', {}).values():
        if nb.alive and nb.x is not None:
            out.append(('named beast', nb.name, ('xy', nb.x, nb.y)))
    for e in w.evils:
        out.append(('great evil', e.name, ('xy', e.x, e.y)))
        for lt in e.lts:
            if lt['site'] is not None:
                out.append(('lieutenant', lt['name'], ('site', lt['site'])))
    sh = getattr(w, 'shadow', None)
    if sh and sh['coast']:
        out.append(('great evil', "The Hollow King's coast", ('xy', *sh['coast'])))
    return out


def to_over(game, x, y):
    """Straight onto a cell of the world map, from wherever you are."""
    from . import zones as ZN
    p = game.player
    if game.cur != 'over':
        if game.encounter is not None or getattr(game, 'zone_fight', False):
            try:
                game.resolve_encounter()
            except Exception:
                pass
        ZN.leave(game)
        game.maps.pop('wild', None)
        game.encounter, game.zone_fight = None, False
    game.pending = None
    game.cur = 'over'
    p.x, p.y = x, y
    game.over_pos = (x, y)
    game._over_last = None
    om = game.maps['over']
    om.seen[y * om.w + x] = 1
    game.compute_fov()


def teleport(game, act):
    w = game.world
    kind = act[0]
    if kind == 'xy':
        to_over(game, act[1], act[2])
        game.msg(f'Debug: you stand at {act[1]},{act[2]}.', 'info')
    elif kind == 's':
        s = w.settlements[act[1]]
        to_over(game, s.x, s.y)
        game.enter_town(s.id)
    elif kind == 'd':
        d = w.dungeons[act[1]]
        to_over(game, d.x, d.y)
        game.enter_dungeon(act[1], 1, 'down')
    elif kind == 'site':
        s = w.sites[act[1]]
        to_over(game, s.x, s.y)
        game.enter_site(s.id)
    elif kind == 'h':
        h = w.holds[act[1]]
        to_over(game, h.x, h.y)
        game.enter_hold(h.id)
    game.request = ('save',)


def old_tale(game):
    """Hear the tale of the nearest temple built over something older: its loose flagstone will lift for you."""
    from . import places as PL
    tale = PL.rumour(game)
    game.msg(f'Debug: {tale}' if tale else 'Debug: no older place you have not heard of lies near enough.', 'info')


def varnish_places(game):
    """The Varnish letters, and every Varnish city and place on your map."""
    from . import varnish as VN
    from . import folk as FK
    game.varnish_letters = True
    VN.learnt_letters(game)
    n = 0
    for s in game.world.sites:
        if VN.is_varnish(s):
            if FK.unfound(s):
                FK.discover(game, s, None)
            n += 1
    game.msg(f'Debug: you know the Varnish letters, and all {n} Varnish places are on your map.', 'info')


def varnish_pages(game):
    """Every page of this world's books, read if you have the letters."""
    from . import varnish as VN
    s = VN.st(game)
    for key in VN.info(game).get('pages', {}):
        s['pages'].add(key)
    if VN.letters(game):
        VN.read_carried(game)
    game.msg(f'Debug: you carry all {len(s["pages"])} pages of this world\'s {len(VN.info(game).get("books", ()))} '
             'books.', 'info')


def epics(game):
    """Rank 40 in your classes, every teacher of them on your map, and their deeds done."""
    from . import epics as EP
    from . import classes as CL
    from . import folk as FK
    p = game.player
    s = EP.st(game)
    lines = CL.classes(game)
    for line in lines:
        if p.disc[line][0] < EP.TEACH_AT:
            p.disc[line][:] = [EP.TEACH_AT, 0]
        s['deeds'][line] = True
    n = 0
    for t in EP.teachers(game):
        if t.cls in lines:
            s['heard'].add(t.id)
            if FK.unfound(t):
                FK.discover(game, t, None)
            n += 1
    s['spent'], s['phoenix_day'] = False, -1
    game.msg(f'Debug: rank {EP.TEACH_AT} in your classes, their deeds done, and {n} teachers on your map.' if lines else
             'Debug: you have no class yet. Read a tome first.', 'info')


def boss(game, what):
    """The Bosses page: set a kit boss down, change its phase, close or open its room, check the fairness of its moves,
    kill its helpers, make it spent, or play that you fled from it."""
    from . import bosses as BS
    m = game.map
    if what.startswith('roam:'):
        k = what[5:]
        p = game.player
        spots = [c for c in BS.free_around(game, m, p.x, p.y, 20) if BS.cheb(*c, p.x, p.y) >= 10] if m.kind != 'over' else []
        spots.sort(key=lambda c: (not game.visible(*c), BS.cheb(*c, p.x, p.y)))     # out of sight first, then far
        spots = [c for c in spots[-12:] if BS.path_to(m, (p.x, p.y), c)][-1:] or spots     # one that can walk to you
        if not spots:
            game.msg('Debug: no room for a roamer ten steps off.', 'bad')
            return None
        from .entities import make_monster
        o = make_monster(game, k, *spots[-1], max(p.lvl, D.MONSTERS[k]['min_l']))
        BS.arm(o)
        o.roam = dict(seen=-999, goal=None, path=[], heard=0, hunted=False)
        m.mons.append(o)
        game.msg(f'Debug: {o.name} walks this level now, out of sight. Listen.', 'info')
        return o
    if what in BS.KITS:
        if m.kind == 'over':
            game.msg('Debug: bosses are set down on a play map, not on the world map.', 'bad')
            return None
        o = BS.spawn(game, what)
        if o is None:
            game.msg('Debug: no room beside you.', 'bad')
            return None
        if getattr(m, 'arena', None) is None:
            BS.build(game, m, o)
        game.compute_fov()
        game.msg(f'Debug: {o.name} (level {o.lvl}) appears' + (' in its room.' if getattr(m, 'arena', None) else '.'), 'info')
        return o
    b = next((o for o in m.mons if BS.st(o) is not None), None)
    if b is None:
        game.msg('Debug: no boss with a kit on this map.', 'bad')
        return None
    ar = m.__dict__.get('arena')
    if what in ('p1', 'p2', 'p3'):
        BS.set_phase(game, b, int(what[1]) - 1)
        game.msg(f'Debug: {b.name} in phase {BS.ROMAN[BS.st(b)["phase"]]}.', 'info')
    elif what == 'seal' and ar:
        BS.seal(game, ar)
    elif what == 'open' and ar:
        BS.open_up(game, ar, False)
        game.msg('Debug: the room is open again.', 'info')
    elif what == 'fair':
        bad = BS.check_fair(game, b)
        game.msg('Debug: every move leaves a way out from here.' if not bad else
                 f'Debug: no way out from here for: {", ".join(bad)}.', 'info' if not bad else 'bad')
    elif what == 'helpers':
        hs = BS.helpers(game, b)
        for o in hs:
            game.kill(o)
        game.msg(f'Debug: {len(hs)} helpers slain.', 'info')
    elif what == 'spent':
        BS.st(b)['spent'] = 2
        b.cast = None
        game.msg(f'Debug: {b.name} is spent for two turns.', 'info')
    elif what == 'stagger':
        BS.st(b)['dots'] = 2
        BS.add_dot(game, b)
    elif what == 'flee' and ar:
        BS.fled(game, ar)
    elif what == 'twin':
        kinds = list(BS.TWINS)
        k = kinds[(game.__dict__.get('dbg_twin', -1) + 1) % len(kinds)]
        game.dbg_twin = kinds.index(k)
        o = BS.spawn(game, b.k)
        if o is not None:
            BS.link(b, o, k)
            game.compute_fov()
            game.msg(f'Debug: a twin of {b.name}: {BS.TWINS[k]}.', 'info')
    return b


def open_rift(game):
    """A rift tears open a little way off (rift.py), or says where the open one is."""
    from . import rift as RF
    r = RF.active(game.world)
    if not r:
        p = game.player
        near = (p.x, p.y) if game.cur == 'over' else game.over_pos
        r = RF.open_rift(game, spot=RF.find_spot(game, near, 4, 14) or RF.find_spot(game))
    if r:
        game.reveal_place(r['x'], r['y'], 2)
        game.msg(f'Debug: the rift lies at {r["x"]}, {r["y"]}; its Deep is {game.world.dungeons[r["did"]].depth} levels.', 'info')
    else:
        game.msg('Debug: no place for a rift was found.', 'info')


def fort_holder(game):
    """On a fort's own map: the next holder in turn (its people, bandits, nobody, a ruin), and the fort made again."""
    m = game.map
    site = game.world.sites[m.site] if getattr(m, 'site', None) is not None else None
    if site is None or site.kind != 'fort':
        game.msg('Debug: stand on the land of a fort first.', 'info')
        return
    order = ('whole', 'taken', 'abandoned', 'ruin')
    site.state = order[(order.index(getattr(site, 'state', 'whole')) + 1) % len(order)]
    site.holder = 'bandits' if site.state == 'taken' else None
    game.maps.pop(site.map_key, None)
    fl = getattr(site, 'floors', None) or f'tw{site.id}'
    for k in [k for k in game.maps if k.startswith(f'{fl}:')]:
        del game.maps[k]
    game.enter_site(site.id)
    game.msg(f'Debug: {site.name} is now {site.state}.', 'info')


def theme_level(game, what):
    """A fresh classic dungeon level made round one drawn piece (its name), or with a river ('river:water' or
    'river:fire'); you stand at the theme room's door, or on the river bank."""
    from . import pieces as PC, themes as TH, underground as UG
    w = game.world
    did = next(k for k, d in w.dungeons.items() if d.style != 'cave' and d.tag != 'den' and d.depth >= 3)
    d = w.dungeons[did]
    real = PC.pick, UG.CHANCE, UG.FIRE_SHARE, UG.FIRE_FROM
    pc = PC.by_name(what)
    try:
        if pc is not None:
            PC.pick = lambda part, tag, depth, n, used=(): [pc] if part == pc.part else []
        else:
            UG.CHANCE, UG.FIRE_FROM, UG.FIRE_SHARE = 1.0, 0, 1.0 if what == 'river:fire' else 0.0
        for _ in range(6):
            game.maps.pop(f'{did}:3', None)
            to_over(game, d.x, d.y)
            game.enter_dungeon(did, 3, 'down')
            m = game.map
            rid = next((i for i, r in enumerate(m.rooms) if r[2] == what), None) if pc else None
            if (pc and rid is not None) or (not pc and getattr(m, 'river', None)):
                break
    finally:
        PC.pick, UG.CHANCE, UG.FIRE_SHARE, UG.FIRE_FROM = real
    m, p = game.map, game.player
    if pc and rid is not None:
        cells = set(TH.cells_of(m, rid))
        ring = [(x + dx, y + dy) for x, y in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                if (x + dx, y + dy) not in cells and m.tile(x + dx, y + dy) != D.WALL]
        door = ring[0] if ring else next(iter(cells))
        out = [(door[0] + dx, door[1] + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
               if (door[0] + dx, door[1] + dy) not in cells and D.TILES[m.tile(door[0] + dx, door[1] + dy)].walk]
        p.x, p.y = out[0] if out else door
        game.msg(f'Debug: the theme room "{what}" lies right beside you.', 'info')
    elif getattr(m, 'river', None):
        i = next(i for i in m.river_flow if any(0 <= i + o < len(m.t) and m.t[i + o] == D.FLOOR for o in (1, -1, m.w, -m.w)))
        j = next(i + o for o in (1, -1, m.w, -m.w) if m.t[i + o] == D.FLOOR)
        p.x, p.y = j % m.w, j // m.w
        game.msg(f'Debug: a river of {m.river} runs beside you.', 'info')
    else:
        game.msg('Debug: that did not come out this time; try again.', 'bad')
    game.compute_fov()


def days_ahead(game, n):
    """Time runs on n days (a fraction for hours); the days pass as they would (markets, news, seasons)."""
    game.turn += round(n * D.DAY_LEN)
    game.end_turn(0, quiet=True)
    game.msg(f'Debug: {n:g} days later, day {game.day}.', 'info')


def to_month(game, mo):
    from . import calendar as CAL
    days = 1
    while CAL._split(game.day + days)[1] != mo or CAL._split(game.day + days)[2] != 1:
        days += 1
    days_ahead(game, days)


def set_weather(game, kind):
    from . import weather as WX
    loc = WX.where(game)
    if not loc:
        game.msg('Debug: there is no weather underground.', 'bad')
        return
    wet = 1.0 if WX._family(kind) == 'rain' else 0.0
    game.world.weather[loc[0]] = [kind, game.turn + 600, kind, wet]
    game.msg(f'Debug: the weather here is {WX.KINDS[kind][0].lower()}.', 'info')


def spawn(game, k, elite=0):
    from .entities import make_monster
    from .worldgen import free_around
    m, p = game.map, game.player
    if m.kind == 'over':
        game.msg('Debug: creatures are spawned on a play map, not on the world map.', 'bad')
        return None
    spot = free_around(game, m, p.x, p.y, 3)
    if not spot:
        game.msg('Debug: no room beside you.', 'bad')
        return None
    lvl = max(1, getattr(m, 'level', 1) or game.world.danger_at(*game.world_pos()) or p.lvl)
    o = make_monster(game, k, spot[0][0], spot[0][1], lvl, elite)
    o.awake = True
    m.mons.append(o)
    game.compute_fov()
    game.msg(f'Debug: {o.name} (level {lvl}) appears.', 'info')
    return o


def kill_in_sight(game):
    foes = [o for o in game.map.mons if not o.is_npc and game.visible(o.x, o.y)]
    for o in foes:
        game.kill(o)
    game.msg(f'Debug: {len(foes)} slain.', 'info')


# ------------------------------------------------------------------ the player
def full_health(game):
    p = game.player
    s = game.stats()
    p.life, p.mana, p.stamina = s['max_life'], s['max_mana'], s['max_stamina']
    p.poison = p.burn = None
    p.food = max(p.food, 800)
    p.buffs = [b for b in p.buffs if b[1] >= 0 or b[0] in ('mregen',)]
    game.msg('Debug: whole again.', 'info')


def god_tick(game):
    """God mode: no harm, and life, mana and stamina never run out."""
    if not has(game, 'god'):
        return False
    p = game.player
    s = game.stats()
    p.life, p.mana, p.stamina = s['max_life'], s['max_mana'], s['max_stamina']
    return True


def give_coin(game, copper):
    game.player.gold += copper
    from .money import fmt
    game.msg(f'Debug: +{fmt(copper)}.', 'info')


def level_up(game, n=1):
    from .engine import xp_for
    p = game.player
    want = p.lvl + n
    while p.lvl < want:
        p.xp = max(p.xp, xp_for(p.lvl) - 1)
        game.gain_xp(1)
    game.msg(f'Debug: level {p.lvl}.', 'info')


def rested(game):
    """As if you had slept here: tree points may be spent until you move."""
    from . import trees as TT
    TT.rested(game)
    game.msg('Debug: you count as rested here.', 'info')


def skill_lines():
    """Every rank you can set: the disciplines and the life skills, as (key, name, kind)."""
    from . import skills as SK
    from . import lifeskills as LS
    out = [(k, SK.DISCIPLINES[k]['name'], 'disc') for k in SK.DISC_ORDER]
    out += [(k, LS.LIFE[k]['name'], 'life') for k in LS.LIFE_ORDER if k in LS.LIFE]
    return out


def set_rank(game, key, kind, rank):
    p = game.player
    rank = max(0, min(100, rank))
    if kind == 'disc':
        p.disc.setdefault(key, [0, 0])[:] = [rank, 0]
    else:
        rank = min(50, rank)
        p.life_sk.setdefault(key, [0, 0])[:] = [rank, 0]
        tests = p.__dict__.setdefault('life_tests', set())
        for lvl in (25, 40):                          # a rank set past a master's test counts the test as passed
            if rank > lvl:
                tests.add((key, lvl))
    game.msg(f'Debug: {key} rank {rank}.', 'info')


RARITIES = ('normal', 'magic', 'rare')


def item_list():
    """Everything you can be given: (kind label, name, recipe)."""
    from . import skills as SK
    from . import hunger as HU
    from . import foraging as FG
    from . import lifeskills as LS
    out = []
    for k, b in D.BASES.items():
        out.append((D.SLOTNAME.get(b['slot'], b['slot']).lower(), b['name'], ('gear', k)))
    for u in D.UNIQUES:
        out.append(('named', u['name'], ('unique', u['name'])))
    for sk, st in D.SETS.items():
        for i, piece in enumerate(st['pieces']):
            out.append(('set piece', piece[0], ('set', sk, i)))
    for k, pd in D.POTIONS.items():
        out.append(('potion', pd['name'], ('potion', k)))
    for s in SK.SKILL_LIST:
        out.append(('tome', f'Tome of {s.name}', ('tome', s.id)))
    for k, v in HU.FOODS.items():
        out.append(('food', v[0], ('food', k)))
    for k, v in FG.PLANTS.items():
        out.append(('plant', v[0], ('plant', k)))
    for k, v in LS.FISH.items():
        out.append(('fish', v[0], ('fish', k)))
    from . import crafts as CRF
    for m in CRF.METALS:
        out.append(('ore', CRF.ORE_NAME[m], ('mat', 'ore_' + m)))
        out.append(('bar', CRF.mat_name('bar_' + m), ('mat', 'bar_' + m)))
    for c in CRF.CLOTHS:
        out.append(('cloth', CRF.CLOTHS[c][0], ('mat', 'cloth_' + c)))
    for k, v in CRF.LEATHERS.items():
        out.append(('leather', v[0], ('leather', k)))
    from . import beastparts as BP
    from .hunting import SKINS
    for beast, row in SKINS.items():
        for part, _c in row[4]:
            if part in BP.PART:
                out.append(('part', BP.part_name(f'{part}:{beast}'), ('part', f'{part}:{beast}')))
    for trait in BP.TRAIT_POWER:
        out.append(('named part', f'Named beast part: {trait}', ('npart', trait)))
    for t, nm in (('rope', 'Coil of Rope'), ('bedroll', 'Bedroll'), ('tent', 'Tent and Bedroll'), ('kit', 'Repair Kit'),
                  ('trowel', "Digger's Trowel")):
        out.append(('tool', nm, ('tool', t)))
    out += [('old piece', 'Old piece, tier C', ('oldpiece', False, 25)), ('old piece', 'Varnish piece, tier D', ('oldpiece', True, 35)),
            ('curio', 'A shard of star-iron', ('curio', 'stariron'))]
    return out


def give(game, recipe, rar='normal'):
    from . import entities as EN
    from . import hunger as HU
    from . import foraging as FG
    from . import lifeskills as LS
    from .skills import SKILLS
    p = game.player
    kind = recipe[0]
    if kind == 'gear':
        it = EN.make_gear(game, recipe[1], rar, max(p.lvl, D.BASES[recipe[1]]['lvl']))
    elif kind == 'unique':
        it = EN.make_unique(game, EN.unique_named(recipe[1]))
    elif kind == 'set':
        it = EN.make_set_item(game, recipe[1], recipe[2])
    elif kind == 'potion':
        it = EN.Item(game.new_id(), 'potion', recipe[1], 5)
    elif kind == 'tome':
        it = EN.Item(game.new_id(), 'tome', recipe[1])
        it.name = f'Tome of {SKILLS[recipe[1]].name}'
    elif kind == 'food':
        it = HU.make_food(game, recipe[1], 5)
    elif kind == 'plant':
        it = FG.make_plant(game, recipe[1], 5)
    elif kind == 'mat':
        from . import crafts as CRF
        it = CRF.make_mat(game, recipe[1], 8)
    elif kind == 'leather':
        it = EN.Item(game.new_id(), 'leather', recipe[1], 8)
    elif kind == 'part':
        it = EN.Item(game.new_id(), 'part', recipe[1], 4)
    elif kind == 'npart':
        it = EN.Item(game.new_id(), 'npart', recipe[1])
        it.beast, it.nid, it.rank, it.src, it.word = 'Old Greyback', None, 'notorious', 'wolf', 'pelt'
    elif kind == 'tool':
        it = EN.Item(game.new_id(), 'tool', recipe[1], 3 if recipe[1] in ('rope', 'kit') else 1)
    elif kind == 'curio':
        from .nature import curio
        it = curio(game, recipe[1])
    elif kind == 'oldpiece':
        from . import archaeology as AR
        it = AR.make_piece(game, recipe[1], recipe[2])
    else:
        it = LS.make_fish(game, recipe[1], 3)
    if it.k == 'gear':
        it.ided = True
    if game.add_to_inv(it):
        game.msg(f'Debug: you have {it.display_name()}.', 'info')
    else:
        it.x, it.y = p.x, p.y
        game.map.items.append(it)
        game.msg(f'Debug: your pack is full; {it.display_name()} lies at your feet.', 'info')
    return it


# ------------------------------------------------------------------ the rest
def job_kinds():
    from . import jobs as JB
    return sorted({'courier', 'freight', 'bounty', 'escort', 'hunt', 'fetch'} | set(JB.KINDS) | set(JB.EXTRA))


def nearest_settlement(game):
    s = game.here
    if s:
        return s
    from .worldgen import cheb
    x, y = game.world_pos()
    return min(game.world.settlements, key=lambda q: cheb(q.x, q.y, x, y))


def make_job(game, kind):
    from . import missions as MS
    s = nearest_settlement(game)
    for _ in range(12):
        try:
            mi = MS.make_offer(game, s, kinds=[kind])
        except Exception:
            mi = None
        if mi and mi.kind == kind:
            break
    else:
        game.msg(f'Debug: no {kind} job could be made from {s.name}.', 'bad')
        return None
    if getattr(s, 'board', None) is None:
        s.board = []
    s.board.append(mi)                  # taken from the board, as a job is
    if MS.accept(game, s, mi):
        game.msg(f'Debug: you took the job "{mi.title}" from {s.name}.', 'info')
        return mi
    if mi in s.board:
        s.board.remove(mi)
    return None


def finish_job(game, mi, ok=True):
    from . import missions as MS
    if ok:
        MS.complete(game, mi, [mi.giver] if mi.giver is not None else [])
    else:
        MS.fail(game, mi, 'You let it go (debug).')


EVENTS = [('pirates', 'A pirate ship sets sail'), ('ship', 'A merchant ship sets sail'),
          ('raid', 'A war party of the raiders sets out'), ('rivals', 'Rival adventurers set out'),
          ('warband', 'A warband marches on a hold'), ('wagons', 'Three wagons of your own join you'),
          ('wagonraid', 'Robbers fall on your wagons'), ('league', 'A League caravan races you'),
          ('happening', 'Something happens in this town'), ('lotus', 'Five black lotus in your cargo')]


def force_event(game, kind):
    import random
    from . import living as LV
    w = game.world
    wd = None
    if kind in ('pirates', 'ship'):
        wd = LV.spawn_ship(game, pirate=kind == 'pirates')
    elif kind == 'raid':
        from . import powers as PW
        rds = PW.raiders(w)
        if rds:
            n = len(w.wanderers)
            for _ in range(8):
                idx = random.randrange(len(rds))
                PW.raid(game, idx, rds[idx])
                if len(w.wanderers) > n:
                    wd = w.wanderers[-1]
                    break
    elif kind == 'rivals':
        w.rivals_back = 0
        w.wanderers = [x for x in w.wanderers if x.kind != 'rivals']
        LV.spawn_rivals(game)
        wd = next((x for x in w.wanderers if x.kind == 'rivals'), None)
    elif kind in ('wagons', 'wagonraid'):
        from . import caravan as CV
        p = game.player
        for k in ('mule', 'cart'):
            if k not in p.mounts:
                p.mounts.append(k)
        if not CV.get(p) or kind == 'wagons':
            p.gold += 3 * (CV.WAGON_PRICE + CV.BEASTS['ox']['price'])
            p.caravan = None
            for b in ('mule', 'ox', 'mule'):
                CV.buy_wagon(game, b)
        if game.here is not None:
            CV.on_enter_town(game, game.here)
        if kind == 'wagonraid' and game.cur == 'over':
            CV.raid(game)
        game.msg('Debug: your wagons.', 'info')
        return None
    elif kind == 'happening':
        from . import townlife as TL
        s = game.here
        got = TL.happening(game, game.map, s) if s is not None else None
        game.msg(f'Debug: {got}.' if got else 'Debug: not in a town.', 'info')
        return None
    elif kind == 'lotus':
        game.player.cargo['lotus'] = game.player.cargo.get('lotus', 0) + 5
        game.msg('Debug: five black lotus.', 'info')
        return None
    elif kind == 'league':
        from . import caravan as CV
        s = game.here or (w.settlements[0] if game.cur != 'over' else game.world.settlement_at(*game.over_pos))
        if s and s.market:
            g = next((k for k in s.market if any(k in o.demand for o in w.settlements if o.id != s.id)), None)
            if g:
                CV.race(game, s, g, 25, anywhere=True)
                wd = next((x for x in w.wanderers if getattr(x, 'rival', False) and x.origin == s.id), None)
    elif kind == 'warband':
        from . import war as WAR
        n = len(w.wanderers)
        for f in random.sample(list(D.FACTIONS), len(D.FACTIONS)):
            WAR.launch(game, f)
            if len(w.wanderers) > n:
                wd = w.wanderers[-1]
                break
    if wd:
        game.msg(f'Debug: {wd.name} at {wd.x},{wd.y}.', 'info')
    else:
        game.msg('Debug: it did not happen (nothing fitting in this world).', 'bad')
    return wd


def set_standing(game, f, value):
    from . import war as WAR
    game.player.rep[f] = value
    WAR.refresh_hostility(game)
    game.msg(f"Debug: {D.FACTIONS[f]['short']} standing {value}.", 'info')


def set_guild(game, key, rank):
    """Join a guild at a rank (0-4), past its rivals and its secrecy."""
    from . import guilds as GU
    st = GU.state(game)[key]
    st.update(joined=True, found=True, left=False, rep=GU.RANK_REP[rank], last=game.day)
    game.msg(f"Debug: {GU.GUILDS[key]['short']}, {GU.rank_name(game, key)}.", 'info')


def add_hireling(game, kind):
    import random
    from . import mercs as MC
    old = MC.get(game)
    if old:
        game.merc = None
        old.state = 'gone'
    lvl = game.player.lvl
    mc = MC.Merc(kind, f'{random.choice(MC.NAMES)} {random.choice(MC.SURNAMES)}', lvl)
    MC.outfit(game, mc)
    mc.hp = MC.stats(game, mc)['max_hp']
    mc.paid = game.day
    mc.wage = MC.wage_for(kind, lvl)
    mc.body, mc.body_map = None, None
    game.merc = mc
    MC.sync(game)
    game.msg(f'Debug: {mc.name} signs on.', 'info')
    return mc


def ai_lines(game, x, y):
    """What a creature under the look cursor is thinking: its numbers and its state."""
    m = game.map
    if m.kind == 'over' or not has(game, 'ai'):
        return []
    o = m.mon_at(x, y)
    if not o:
        return []
    skip = {'name', 'ch', 'fg', 'hit_flash', 'k', 'x', 'y', 'id'}
    bits = []
    for k, v in sorted(vars(o).items()):
        if k in skip or k.startswith('_'):
            continue
        if isinstance(v, (int, float, str, bool, type(None), tuple)) or (isinstance(v, (list, dict, set)) and len(str(v)) < 60):
            bits.append(f'{k}={v}')
    return [f'[debug] {o.k} id {o.id}: ' + ', '.join(bits)]


def status_bits(game):
    """The debug line under the map: where exactly you are, the turn and the seed."""
    p = game.player
    wx, wy = game.world_pos()
    return f' {p.x},{p.y} · w {wx},{wy} · t {game.turn} · seed {game.seed} '


def shadow(game, what):
    """The shadow (great evils part 1): his attention, the servants' clocks, what you know of them."""
    import random
    from . import shadow as SH
    from . import evils as EVL
    w = game.world
    sh = SH.st(w)
    if not sh:
        return
    if what == 'up':
        sh['step_day'] = -99
        SH.meddle(game, SH.ATT_STEP)
    elif what == 'zero':
        sh['att'], sh['pts'] = 0, 0.0
        game.msg('Debug: he looks away.', 'info')
    elif what == 'name':
        for e in w.evils:
            if not e.known:
                EVL.learn(game, e)
    elif what == 'wake':
        for e in w.evils:
            if not e.awake and not e.defeated:
                SH.wake(game, e)
        game.msg('Debug: every servant is awake.', 'info')
    elif what == 'seal':
        e = next((e for e in w.evils if not e.sealed and not e.defeated), None)
        if e:
            e.awake, e.goal = True, 100.0
            SH.seal(game, e)
    elif what == 'weak':
        for e in w.evils:
            for src in ('library', 'hero'):
                SH.know(game)['src'].setdefault(e.key, set()).add(src)
        game.msg('Debug: you know every weakness.', 'info')
    elif what == 'lts':
        om = game.maps['over']
        for i, e in enumerate(w.evils):
            for j, lt in enumerate(e.lts):
                if lt['site'] is not None:
                    s = w.sites[lt['site']]
                    SH.know(game)['lts'].add((i, j))
                    om.seen[s.y * om.w + s.x] = 1
        game.msg('Debug: every lieutenant is on your map.', 'info')
    elif what == 'hero':
        for h in sh['heroes']:
            if h['state'] == 'riding':
                h['arrive'] = game.day
        if not any(h['state'] == 'riding' for h in sh['heroes']):
            keep = random.random
            random.random = lambda: 0.0
            try:
                SH.heroes_month(game)
            finally:
                random.random = keep
            for h in sh['heroes']:
                if h['state'] == 'riding':
                    h['arrive'] = game.day
        SH.heroes_day(game)
        game.msg('Debug: a hero rode out, and the news will come.', 'info')
    elif what in ('reveal', 'relic', 'chain', 'under', 'f1', 'f3', 'f5', 'night', 'won'):
        _skyseat(game, what)
    elif what == 'month':
        for _ in range(30):
            SH.daily(game)
        SH.monthly(game)
        EVL.compute_taint(game)
        game.msg('Debug: a month went by for the servants.', 'info')


def _skyseat(game, what):
    from . import skyseat as SK
    from . import shadow as SH
    sh = SH.st(game.world)
    if what == 'reveal':
        if not sh.get('seen'):
            SK.reveal(game)
    elif what == 'relic':
        from .entities import Item
        e = next((e for e in game.world.evils if not any(it.k == 'relic' and it.t == e.key for it in game.player.inv)), None)
        if e:
            name = SH.SERVANT[e.key]['relic'][0]
            it = Item(game.new_id(), 'relic', e.key)
            it.name = name
            game.add_to_inv(it)
            game.msg(f'Debug: {name} is in your pack.', 'info')
    elif what in ('chain', 'under'):
        if not sh.get('seen'):
            SK.reveal(game)
        if game.cur != 'over' and not SK.in_seat(game):
            game.over_pos = game.world_pos()
        SK.to_chain(game, top=what == 'under', ask=False)
    elif what.startswith('f'):
        if not sh.get('seen'):
            SK.reveal(game)
        if game.cur != 'over' and not SK.in_seat(game):
            game.over_pos = game.world_pos()
        SK.enter_floor(game, int(what[1]))
    elif what == 'night':
        for e in game.world.evils:
            if not e.sealed and not e.defeated:
                e.awake, e.goal = True, 100.0
                SH.seal(game, e)
    elif what == 'won':
        SK.won(game)
