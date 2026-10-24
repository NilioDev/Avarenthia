"""The rooms of the classic dungeons (approved 22 October 2026): the mood line the first time you step into a room,
and the theme rooms, each with one telling thing you use with a bump (or by stepping on it).

The theme rooms are drawn pieces (pieces.py, `pieces/theme.des`); K5 sets them in behind a single entrance, 2 or 3 per
level, never the same twice on one level. gen_k5 puts their tiles down and records on the map:
  m.things  {(x, y): (action, room)}   a telling thing and what it does
  m.events  [{room, when, at, if, then, again, done}]   the pieces' own when / if / then rules
  m.theme_state {room: {...}}           what has been done in each theme room (its find taken, its altar prayed at)
setup() fills the rooms once the level has its creatures (a guard by the gong, a find on each plinth, beasts in the
cages), tick() keeps the moving parts going (gears, the gong guard, the circle's waves, the echo, the hidden door you
notice), and on_step()/bump() answer the player. Whatever you learn of a level (the rooms you have seen) lives on you."""
import random

from . import data as D
from . import events as EV
from .worldgen import cheb

# ------------------------------------------------------------------ mood lines of the ordinary rooms
SHAPE_MOODS = {
    'plain': ['A bare room, square and silent.', 'An empty chamber. Dust lies thick on the floor.',
              'A plain stone room. Someone swept it, once.'],
    'chamfer': ['A room with its corners cut away. The mason took care here.',
                'An eight-sided chamber, the walls dressed smooth.'],
    'round': ['A round chamber. Your footsteps circle back to you.', 'A round room under a low dome.'],
    'ell': ['The room turns a corner; you cannot see all of it at once.', 'A room bent like an elbow.'],
    'tee': ['A broad hall with a wing running off it.', 'A hall that opens into a second, narrower one.'],
    'cross': ['Two halls cross here.', 'A cross-shaped hall, high and cold.'],
    'overlap': ['Two rooms run into each other here, as if built at different times.',
                'A wide room of odd angles. The walls do not quite agree.'],
    'zed': ['A long room that steps sideways halfway along.', 'The room jogs aside, then goes on.'],
    'chunky': ['A lumpy chamber, half dug and half fallen.', 'A room of bulges and hollows, like a cave someone began to tidy.'],
    'pillars': ['A great hall of pillars. Plenty of room for a fight, and for hiding.',
                'Rows of pillars march into the dark.'],
    'rotunda': ['A round hall about a core of solid stone.', 'A ring of a hall, curving away round a great pillar of rock.'],
    'inner': ['A hall with a room built inside it. Its one door is somewhere round the side.',
              'A chamber within a chamber.'],
    'gallery': ['A long gallery with a row of pillars down the middle.', 'A gallery. The pillars throw long shadows.'],
    'bays': ['A hall with alcoves along both walls, deep enough to stand in.', 'Alcoves line this room, all of them dark.'],
    'cave': ['A cave. The walls here were never cut by hands.', 'Raw cave: wet rock and a cold draught.'],
}
SPAWN = {'undead': ('skeleton', 'zombie'), 'beasts': ('wolf', 'boar', 'brown_bear'), 'fire': ('imp', 'salamander',
         'fire_beetle'), 'vermin': ('rat',), 'bandit': ('bandit',)}
CAGED = ('wolf', 'boar', 'brown_bear', 'cave_bear', 'winter_wolf')


def _the(mon):
    t = mon.the()
    return t[0].upper() + t[1:]


def _seen(game):
    """The rooms you have stepped into: {level id: set of room numbers}. Yours, not the level's."""
    return game.player.__dict__.setdefault('rooms_seen', {})


def room_at(m, x, y):
    ro = getattr(m, 'room_of', None)
    if ro is None or not m.inb(x, y):
        return None
    r = ro[y * m.w + x]
    return None if r == 255 else r


def state(m, rid):
    return m.__dict__.setdefault('theme_state', {}).setdefault(rid, {})


def cells_of(m, rid):
    return [(i % m.w, i // m.w) for i, r in enumerate(m.room_of) if r == rid]


# ------------------------------------------------------------------ made with the level
def lay(m, plan, room_ids, piece_of):
    """Put the drawn pieces' tiles on the map, and remember their things and events (gen_k5 calls this)."""
    from . import pieces as PC
    m.things, m.events, m.theme_cells = {}, [], set()
    for (x, y), ch in plan.marks.items():
        rid = room_ids.get((x, y))
        pc = piece_of.get(rid)
        if pc is None:
            continue
        if ch in pc.things:
            tile, act = pc.things[ch]
            m.set(x, y, tile)
            if act:
                m.things[(x, y)] = (act, rid)
        elif ch in PC.LEGEND:
            m.set(x, y, PC.LEGEND[ch])
        m.__dict__.setdefault('marks', {})[(x, y)] = ch
    for rid, pc in piece_of.items():
        m.rooms[rid][2] = pc.name
        for i, r in enumerate(m.room_of):
            if r == rid:
                m.theme_cells.add(i)
        for ev in pc.events:
            at = None
            if ev['at']:
                at = [c for c, ch in m.marks.items() if ch == ev['at'] and room_ids.get(c) == rid]
            m.events.append(dict(room=rid, when=ev['when'], at=at, cond=list(ev['if']), then=list(ev['then']),
                                 again=ev['again'], done=False))


def gate(m, rid, kind):
    """The way into a theme room: a door, an open arch, a hidden door or a locked vault door."""
    cells = set(cells_of(m, rid))
    ring = {(x + dx, y + dy) for x, y in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))} - cells
    ways = [c for c in ring if m.inb(*c) and m.tile(*c) in (D.DOOR, D.ODOOR, D.FLOOR)]
    for c in ways:
        m.set(c[0], c[1], {'door': D.DOOR, 'open': D.FLOOR, 'secret': D.SECRET, 'vault': D.VAULTDOOR}[kind])
    if kind == 'vault' and ways:
        state(m, rid)['vault'] = ways[0]


def setup(game, m, lvl):
    """Fill the theme rooms once the level has its creatures."""
    from .entities import make_monster, make_npc, make_tome, random_gear, Item
    from .worldgen import choose_monster, free_around, rand_free
    for rid, (shape, _kind, name) in enumerate(getattr(m, 'rooms', [])):
        if not name:
            continue
        cells = cells_of(m, rid)
        inside = set(cells)
        st = state(m, rid)
        if name in ('sanctuary', 'circle', 'choice', 'chapel', 'deadcamp', 'shrine', 'menagerie', 'prison', 'gaming'):
            m.mons[:] = [o for o in m.mons if (o.x, o.y) not in inside]     # no one waits in these
        things = {c: a for c, (a, r) in m.things.items() if r == rid}
        marks = {c: ch for c, ch in getattr(m, 'marks', {}).items() if c in inside}
        if name == 'shrine' or name == 'chapel':
            st['defiled'] = random.random() < .25 and name == 'shrine'
        if 'choice' in things.values():
            st['finds'] = {}
            for c in [c for c, a in things.items() if a == 'choice']:
                r = random.random()
                it = random_gear(game, lvl + 2, 1.5) if r < .5 else Item(game.new_id(), 'potion', 'rejuv', 2) if r < .75 \
                    else make_tome(game, lvl)
                st['finds'][c] = it
        if 'statues' in things.values():
            c = random.choice([c for c, a in things.items() if a == 'statues'])
            m.set(c[0], c[1], D.FLOOR)
            del m.things[c]
            g = make_monster(game, 'gargoyle', c[0], c[1], lvl)
            g.true_look = (g.ch, g.fg)
            g.awake, g.ch, g.fg = False, 'ß', D.TILES[D.STATUE].fg
            g.still = True                          # stands like stone until you come close
            m.mons.append(g)
        if 'gong' in things.values():
            gc = next(c for c, a in things.items() if a == 'gong')
            sp = [c for c in free_around(game, m, gc[0], gc[1], 2) if c in inside and not game.occupied(m, *c)]
            if sp:
                k = choose_monster(lvl, getattr(m, 'dtag', 'crypt'))
                guard = make_monster(game, k, sp[0][0], sp[0][1], lvl)
                guard.awake, guard.gong = False, gc
                m.mons.append(guard)
        if 'cell' in things.values():
            pens = [c for c, ch in marks.items() if ch == 'Q']
            random.shuffle(pens)
            st['cells'] = {}
            for c in pens[:2]:
                who = 'captive' if random.random() < .55 else 'beast'
                st['cells'][c[0]] = who
                if who == 'captive':
                    g = random.choice(['male', 'female'])
                    from .races import random_name
                    npc = make_npc(game, random_name('human', g), 'captive', '#d8c8a0', c[0], c[1], True, gender=g, race='human')
                    m.mons.append(npc)
                else:
                    k = choose_monster(lvl + 1, getattr(m, 'dtag', 'crypt'))
                    o = make_monster(game, k, c[0], c[1], lvl + 1)
                    o.awake = False
                    m.mons.append(o)
        if 'menagerie' in things.values():
            pens = [c for c, ch in marks.items() if ch == 'Q']
            random.shuffle(pens)
            keys = [k for k in CAGED if k in D.MONSTERS]
            for c in pens[:random.randint(2, 4)]:
                o = make_monster(game, random.choice(keys), c[0], c[1], lvl)
                o.awake, o.caged = False, True
                m.mons.append(o)
        if 'plate' in things.values():
            from . import behave as BH
            for c in [c for c, a in things.items() if a == 'plate']:
                BH.traps(m)[c] = max(3, lvl * 2)
                m.__dict__.setdefault('trap_kind', {})[c] = 'plate'
                del m.things[c]
        if name == 'gaming':
            dc = next((c for c, a in things.items() if a == 'dice'), None)
            if dc:
                from .races import random_name
                for c in [c for c in free_around(game, m, dc[0], dc[1], 1) if c in inside][:3]:
                    g = random.choice(['male', 'female'])
                    m.mons.append(make_npc(game, random_name('human', g), 'gambler', '#c89060', c[0], c[1], True, gender=g,
                                           race='human'))
        if name == 'sanctuary':
            m.__dict__.setdefault('warded', set()).update(inside)
        if name in ('fungus', 'garden', 'rift', 'sanctuary'):         # what gives the light here: no torch to carry
            mx = sum(c[0] for c in cells) // len(cells)
            my = sum(c[1] for c in cells) // len(cells)
            col = {'fungus': (90, 200, 120), 'garden': (230, 220, 170), 'rift': (255, 120, 40), 'sanctuary': (240, 220, 150)}[name]
            m.lights.append((mx, my, col, 6))
        if st.get('vault'):
            far = rand_free(game, m, lambda t: t == D.FLOOR, (st['vault'][0], st['vault'][1], 25))
            if far:
                key = Item(game.new_id(), 'vkey', 'k5', 1)
                key.name, key.door = 'Heavy Iron Key', (m.key, st['vault'])
                key.x, key.y = far
                m.items.append(key)
                if random.random() < .7:            # often with a guard
                    sp = [c for c in free_around(game, m, far[0], far[1], 1) if not game.occupied(m, *c)]
                    if sp:
                        k = choose_monster(lvl, getattr(m, 'dtag', 'crypt'))
                        m.mons.append(make_monster(game, k, sp[0][0], sp[0][1], lvl + 1, 1))


# ------------------------------------------------------------------ while you are there
def on_step(game):
    """Called after each step on a dungeon level: the mood line of a new room, and things you step on."""
    m, p = game.map, game.player
    rid = room_at(m, p.x, p.y)
    if rid is not None:
        seen = _seen(game).setdefault(getattr(m, 'made', m.key), set())
        if rid not in seen:
            seen.add(rid)
            mood(game, m, rid)
            fire(game, 'enter', room=rid)
    t = getattr(m, 'things', {}).get((p.x, p.y))
    if t and D.TILES[m.tile(p.x, p.y)].walk:
        ACTIONS[t[0]](game, p.x, p.y, t[1], state(m, t[1]))
    fire(game, 'step', cell=(p.x, p.y))
    if getattr(m, 'delve', None):
        from .delves import tick
        tick(game)


def mood(game, m, rid):
    shape, kind, name = m.rooms[rid]
    if name:
        from . import pieces as PC
        pc = PC.by_name(name)
        if pc and pc.moods:
            game.msg(random.choice(pc.moods), 'info')
        return
    if shape.startswith('delve:'):
        from .delves import MOODS
        lines = MOODS.get(shape[6:])
        if lines:
            game.msg(random.choice(lines), 'info')
        return
    lines = SHAPE_MOODS.get(shape) or SHAPE_MOODS['plain']
    if (rid * 7 + len(m.rooms)) % 3 == 0 or shape in ('pillars', 'rotunda', 'inner', 'gallery', 'cave', 'cross'):
        game.msg(random.choice(lines), 'info')         # not every plain room needs a word


def bump(game, x, y):
    """Bumping into a telling thing. Returns the turns it took, or None when (x, y) is no thing."""
    m = game.map
    t = m.tile(x, y)
    if t == D.SECRET:
        found_door(game, x, y)
        return 1
    if t == D.VAULTDOOR:
        return vault_door(game, x, y)
    th = getattr(m, 'things', {}).get((x, y))
    fire(game, 'bump', cell=(x, y))
    if not th:
        return None
    return ACTIONS[th[0]](game, x, y, th[1], state(m, th[1])) or 0


def fire(game, when, room=None, cell=None):
    """Run the pieces' events that answer this moment."""
    m = game.map
    for ev in getattr(m, 'events', ()):
        if ev['done'] or ev['when'] != when:
            continue
        if room is not None and ev['room'] != room:
            continue
        if cell is not None and (not ev['at'] or cell not in ev['at']):
            continue
        if not all(_holds(game, c) for c in ev['cond']):
            continue
        if not ev['again']:
            ev['done'] = True
        for th in ev['then']:
            _then(game, th, ev['room'])


def _holds(game, c):
    from . import towns as TW
    if c == 'night':
        return TW.is_night(game)
    if c == 'day':
        return not TW.is_night(game)
    if c.startswith('chance:'):
        return random.random() * 100 < int(c[7:])
    if c.startswith('has:'):
        return any(it.t == c[4:] or it.k == c[4:] for it in game.player.inv)
    return False


def _then(game, th, rid):
    from .entities import make_monster
    from .worldgen import choose_monster, free_around
    m, p = game.map, game.player
    verb, _, arg = th.partition(':')
    if verb == 'msg':
        game.msg(arg.strip('"'), 'info')
    elif verb == 'do':
        ACTIONS[arg](game, p.x, p.y, rid, state(m, rid))
    elif verb == 'spawn':
        what, _, n = arg.partition(':')
        n = int(n or 3)
        lvl = getattr(m, 'level', 1)
        cells = [c for c in cells_of(m, rid) if D.TILES[m.tile(*c)].walk and not game.occupied(m, *c)
                 and cheb(c[0], c[1], p.x, p.y) >= 3] or [c for c in free_around(game, m, p.x, p.y, 4)
                                                         if not game.occupied(m, *c)]
        random.shuffle(cells)
        for c in cells[:n]:
            if what == 'pack':
                k = choose_monster(lvl, getattr(m, 'dtag', 'crypt'))
            elif what in SPAWN:
                k = random.choice([k for k in SPAWN[what] if k in D.MONSTERS])
            else:
                k = what if what in D.MONSTERS else choose_monster(lvl, getattr(m, 'dtag', 'crypt'))
            o = make_monster(game, k, c[0], c[1], lvl)
            o.awake = True
            m.mons.append(o)
    elif verb == 'wake':
        wake_all(game)
    elif verb in ('open', 'shut', 'cavein', 'flood'):
        tile = {'open': D.FLOOR, 'shut': D.BARS, 'cavein': D.RUBBLE, 'flood': D.SHALLOW}[verb]
        inside = set(cells_of(m, rid))
        for c, ch in getattr(m, 'marks', {}).items():
            if ch == arg and c in inside and not game.occupied(m, *c):
                m.set(c[0], c[1], tile)
    elif verb == 'reveal':
        reveal(game)


def wake_all(game):
    for o in game.map.mons:
        if not o.is_npc and not getattr(o, 'caged', False):
            o.awake = True
            o.still = False


def reveal(game):
    m = game.map
    for i, t in enumerate(m.t):
        td = D.TILES[t]
        if td.walk or td.door or any(0 <= i + o < len(m.t) and D.TILES[m.t[i + o]].walk for o in (1, -1, m.w, -m.w)):
            m.seen[i] = 1


def tick(game):
    """Each turn on a level with theme rooms: the moving parts."""
    m, p = game.map, game.player
    if not getattr(m, 'things', None) and not getattr(m, 'theme_cells', None):
        return
    for o in list(m.mons):
        if getattr(o, 'still', False) and cheb(o.x, o.y, p.x, p.y) <= 1:
            o.still, o.awake = False, True
            o.ch, o.fg = getattr(o, 'true_look', (o.ch, o.fg))
            game.msg(f'The statue moves! {_the(o)} steps down from its place.', 'bad')
        g = getattr(o, 'gong', None)
        if g and o.awake and game.visible(o.x, o.y) and not getattr(m, 'gonged', False) and random.random() < .3:
            m.gonged = True
            game.flash([g], (230, 180, 80), '*', .3)
            game.msg(f'{_the(o)} strikes the gong! The sound rolls through the halls, and everything wakes.', 'bad')
            wake_all(game)
    for (x, y), (act, rid) in list(m.things.items()):
        if act == 'gears' and game.turn % 4 == 0:
            st = state(m, rid)
            st['open'] = not st.get('open', True)
            for c, ch in m.marks.items():
                if ch == 'Q' and room_at(m, *c) == rid and not game.occupied(m, *c):
                    m.set(c[0], c[1], D.FLOOR if st['open'] else D.BARS)
            break
    for rid, st in getattr(m, 'theme_state', {}).items():
        if st.get('waves'):
            waves(game, rid, st)
        if st.get('echo') and not getattr(m, 'echoed', False) and room_at(m, p.x, p.y) == rid and any(
                not o.is_npc and o.awake and cheb(o.x, o.y, p.x, p.y) <= 1 for o in m.mons):
            m.echoed = True
            game.msg('The din of the fight rolls on and on through the halls. Everything on this level has heard it.', 'bad')
            wake_all(game)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):        # a hidden door you notice in passing
        x, y = p.x + dx, p.y + dy
        if m.inb(x, y) and m.tile(x, y) == D.SECRET and random.random() < .08 + p.dex / 400:
            found_door(game, x, y)


def found_door(game, x, y):
    game.map.set(x, y, D.DOOR)
    game.msg('You find a hidden door in the wall!', 'good')


def vault_door(game, x, y):
    m, p = game.map, game.player
    key = next((it for it in p.inv if it.k == 'vkey' and getattr(it, 'door', None) == (m.key, (x, y))), None)
    if not key:
        game.msg('A heavy door, banded with iron and locked. The key must be somewhere on this level.')
        return 0
    p.inv.remove(key)
    m.set(x, y, D.ODOOR)
    game.msg('The key turns, stiffly. The vault door swings open.', 'good')
    return 1


def sanctuary_here(game):
    """Standing among the warding signs, where nothing of the dark may come."""
    p, m = game.player, game.map
    return (p.x, p.y) in getattr(m, 'warded', ())


def after_rest(game):
    m = game.map
    if sanctuary_here(game) and m.warded:
        m.warded = set()
        game.msg('As you wake, the signs on the floor flicker and go out. They held for you, once.', 'info')


# ------------------------------------------------------------------ the telling things
def _once(game, st, key, text):
    if st.get(key):
        game.msg(text)
        return True
    st[key] = True
    return False


def a_shrine(game, x, y, rid, st):
    from . import behave as BH
    if _once(game, st, 'prayed', 'The altar is quiet now. Whatever listened here has heard you.'):
        return 0
    p = game.player
    if st.get('defiled'):
        BH.give(game, 'cursed', 80)
        game.msg('You kneel. The altar was defiled long ago, and what answers is not kind. You are cursed.', 'bad')
        return 3
    p.buffs.append(['def', 12, 400, 'Blessing of the shrine'])
    game.msg('You kneel and pray. A calm settles on you: the old shrine has blessed you.', 'good')
    return 3


def a_library(game, x, y, rid, st):
    from . import history as HI
    if _once(game, st, 'searched', 'You have been through these shelves already. Rot and mould, and nothing more.'):
        return 0
    m, p = game.map, game.player
    r = random.random()
    if r < .35 and HI.events(game.world):
        e = random.choice(HI.events(game.world))
        HI.learn(game, e, 'read', 'an old chronicle')
        game.msg(f'Among the rotten books, one can still be read: {e["text"]}', 'gold')
    elif r < .6:
        reveal(game)
        game.msg('You find a plan of this level, drawn in faded ink. You know your way now.', 'good')
    elif r < .75:
        from .entities import make_tome
        it = make_tome(game, getattr(m, 'level', 1))
        if game.add_to_inv(it):
            game.msg(f'Behind a row of rotten books: a tome that survived. You take the {it.name}.', 'gold')
        else:
            it.x, it.y = p.x, p.y
            m.items.append(it)
            game.msg(f'Behind a row of rotten books: a tome that survived. Your pack is full; you leave the {it.name} here.')
    else:
        game.msg('You search the shelves for a long while. Rot and mould; nothing worth reading.')
    return 10


def a_fountain(game, x, y, rid, st):
    from . import behave as BH
    if _once(game, st, 'drunk', 'You drank here already. The water tastes of nothing now.'):
        return 0
    p, s = game.player, game.stats()
    r = random.random()
    if r < .3:
        p.life = s['max_life']
        game.msg('You drink. Warmth runs through you, and your wounds close.', 'good')
    elif r < .5:
        p.mana = s['max_mana']
        game.msg('You drink. Your head clears, and your mana is full.', 'good')
    elif r < .7:
        p.buffs.append(['regen', 3, 200, 'Fountain water'])
        game.msg('You drink. You feel strong and well; your wounds will mend fast for a while.', 'good')
    elif r < .85:
        BH.cure(game)
        game.msg('You drink. It is bitter, but something in you that was wrong is right again.', 'good')
    else:
        game.hurt(max(3, round(s['max_life'] * .15)), 'foul water', 'poison')
        game.msg('You drink. The water is foul: you retch and shake.', 'bad')
    return 1


def a_forge(game, x, y, rid, st):
    if _once(game, st, 'used', 'The old anvil has given what it can; the hearth beside it is cold for good.'):
        return 0
    its = game.worn_gear()
    if not its:
        st['used'] = False
        game.msg('An anvil, still good. Your gear is in good order; there is nothing to mend.')
        return 0
    for it in its:
        it.dur = min(it.mdur, it.dur + max(1, round(it.mdur * .5)))
    game.msg('You work at the old anvil for a while, and mend what you can.', 'good')
    return 30


def a_cook(game, x, y, rid, st):
    from . import cooking as CK
    CK.at_fire(game, 'hearth')
    return 0


def a_alchemy(game, x, y, rid, st):
    from .entities import Item
    if _once(game, st, 'used', 'The flasks here are empty or broken now.'):
        return 0
    if random.random() < .65:
        k = random.choice(['hp', 'hp', 'mp', 'cure'])
        it = Item(game.new_id(), 'potion', k, random.randint(1, 2))
        if game.add_to_inv(it):
            game.msg(f'Among the stoppered jars, some are still good: {it.display_name()}.', 'good')
            return 5
    game.msg('The flasks are dry and cracked. Nothing here is fit to drink.')
    return 5


def a_fungus(game, x, y, rid, st):
    from . import behave as BH
    from . import foraging as FG
    picked = st.setdefault('picked', set())
    if (x, y) in picked:
        return 0
    picked.add((x, y))
    if random.random() < .25:
        BH.give(game, 'confused', 3, 'A cap bursts as you brush it, and spores puff into your face. The world tilts.')
        return 1
    it = FG.make_plant(game, random.choice(['chanterelle', 'chanterelle', 'sleepcap']), 1)
    if game.add_to_inv(it):
        game.msg(f'You gather {it.display_name().lower()}.', 'good')
    return 1


def a_larder(game, x, y, rid, st):
    from .entities import Item
    if _once(game, st, 'taken', 'The larder has nothing more to give.'):
        return 0
    k = random.choice(['bread', 'cheese', 'jerky', 'ration'])
    it = Item(game.new_id(), 'food', k, random.randint(2, 3))
    if game.add_to_inv(it):
        game.msg(f'In the barrel, still good: {it.display_name().lower()}.', 'good')
    return 2


def a_wishing(game, x, y, rid, st):
    from .money import fmt
    p = game.player
    opts = [(f'Throw a copper piece ({fmt(1)})', 'c' if p.gold >= 1 else None),
            (f'Throw a silver piece ({fmt(100)})', 's' if p.gold >= 100 else None),
            (f'Throw a gold piece ({fmt(10000)})', 'g' if p.gold >= 10000 else None), ('Walk on', 'bye')]
    EV.ask(game, 'k5_wish', 'The wishing well', 'Coins glint far down in the dark water. People wished here, once, '
           'and some say the well remembers.', opts)
    return 0


def r_wish(game, choice, ctx):
    p = game.player
    cost = {'c': 1, 's': 100, 'g': 10000}.get(choice)
    if not cost:
        return
    p.gold -= cost
    if any(b[3] == 'Luck of the well' for b in p.buffs):
        game.msg('The coin falls, and falls, and splashes. The well has already given you its luck.')
        return
    if choice == 'c':
        if random.random() < .2:
            p.buffs.append(['dmg', 5, 200, 'Luck of the well'])
            game.msg('The copper splashes far below. For a moment you feel lucky.', 'good')
        else:
            game.msg('The copper splashes far below. Nothing happens. It was only a copper.')
    elif choice == 's':
        p.buffs.append(['dmg', 8, 400, 'Luck of the well'])
        game.msg('The silver catches the light as it falls. You feel your luck turn.', 'good')
    else:
        p.buffs.append(['dmg', 12, 800, 'Luck of the well'])
        p.buffs.append(['def', 15, 800, 'Luck of the well'])
        game.msg('The gold piece sinks, glowing. The well remembers you. You feel truly lucky.', 'gold')


def a_training(game, x, y, rid, st):
    from . import skills as SK
    from . import weaponskills as WS
    if _once(game, st, 'trained', 'The dummies are in tatters now. There is nothing more to learn from them.'):
        return 0
    k = WS.KIT.get(WS.kit(game))
    line = WS.WSKILLS[k[0]].line if k else None
    if line is None or line not in game.player.disc:
        st['trained'] = False
        game.msg('Straw dummies, for weapon practice. Take up a weapon first.')
        return 0
    if game.hostile_visible():
        st['trained'] = False
        game.msg('Not with enemies about!', 'bad')
        return 0
    SK.gain(game, line, 15)
    game.msg('You drill against the dummies for a long while, until your arms ache.', 'good')
    return 40


def a_maptable(game, x, y, rid, st):
    reveal(game)
    if not st.get('read'):
        st['read'] = True
        game.msg('You study the map on the table. It shows this whole level: you know your way now.', 'good')
        return 3
    game.msg('The map of this level. You know it by heart now.')
    return 0


def a_wine(game, x, y, rid, st):
    from . import behave as BH
    if _once(game, st, 'drunk', 'You have had enough of this wine.'):
        return 0
    p, s = game.player, game.stats()
    if random.random() < .5:
        p.life = min(s['max_life'], p.life + round(s['max_life'] * .2))
        game.msg('You draw a cup from a barrel. Old, strong and good: it warms you through.', 'good')
    else:
        BH.give(game, 'confused', 6, 'You draw a cup from a barrel. Old and very strong: your head swims.')
    return 2


def a_choice(game, x, y, rid, st):
    it = st.get('finds', {}).get((x, y))
    if not it:
        game.msg('An empty plinth.')
        return 0
    EV.ask(game, 'k5_choice', 'Take one', f'On this plinth: {it.display_name()}. Take it, and the others sink away.',
           [(f'Take the {it.display_name()}', 'take'), ('Look at the others first', 'bye')], rid=rid, cell=(x, y))
    return 0


def r_choice(game, choice, ctx):
    m = game.map
    st = state(m, ctx['rid'])
    finds = st.get('finds', {})
    it = finds.get(tuple(ctx['cell']))
    if choice != 'take' or not it:
        return
    if not game.add_to_inv(it):
        game.msg('Your pack is full.', 'bad')
        return
    game.msg(f'You take the {it.display_name()}. The other plinths sink into the floor with a grinding sound.', 'gold')
    for c in finds:
        m.set(c[0], c[1], D.FLOOR)
        m.things.pop(c, None)
    st['finds'] = {}
    fire(game, 'take', room=ctx['rid'])


def a_armoury(game, x, y, rid, st):
    from .entities import random_gear
    if _once(game, st, 'searched', 'Nothing else on these racks is worth carrying.'):
        return 0
    m = game.map
    if random.random() < .4:
        game.msg('You go through the racks. Rust and rot: nothing you could use.')
        return 5
    it = random_gear(game, max(1, getattr(m, 'level', 1) - 1), .6)
    if getattr(it, 'mdur', 0):
        it.dur = max(1, round(it.mdur * .3))
    if game.add_to_inv(it):
        game.msg(f'On the racks, one thing is still whole, if rusted: {it.display_name()}.', 'good')
    return 5


def a_adventurer(game, x, y, rid, st):
    from .entities import random_gear
    if _once(game, st, 'searched', 'You have taken all there was. Rest well, whoever you were.'):
        return 0
    m, p = game.map, game.player
    it = random_gear(game, getattr(m, 'level', 1), 1.0)
    if game.add_to_inv(it):
        game.msg(f'In the pack: {it.display_name()}.', 'good')
    else:
        it.x, it.y = p.x, p.y
        m.items.append(it)
    text = game.rumor()
    if text:
        game.msg(f'And a letter, never sent. Part of it can still be read: "{text}"', 'gold')
    return 3


def a_circle(game, x, y, rid, st):
    if st.get('waves') or st.get('won'):
        return 0
    EV.ask(game, 'k5_circle', 'The summoning circle', 'The red signs hum under your feet. Stand here, and something '
           'will come for you, again and again. Hold out to the end, and the circle pays.',
           [('Stand in the circle', 'in'), ('Step out of it', 'bye')], rid=rid)
    return 0


def r_circle(game, choice, ctx):
    if choice != 'in':
        return
    st = state(game.map, ctx['rid'])
    st['waves'], st['left'] = 1, []
    game.msg('You stand fast. The signs flare red, and the air tears open.', 'bad')
    _wave(game, ctx['rid'], st)


def _wave(game, rid, st):
    from .entities import make_monster
    from .worldgen import choose_monster
    m, p = game.map, game.player
    lvl = getattr(m, 'level', 1)
    cells = [c for c, ch in m.marks.items() if ch == 'O' and room_at(m, *c) == rid and not game.occupied(m, *c)]
    random.shuffle(cells)
    st['left'] = []
    for c in cells[:2 + st['waves']]:
        o = make_monster(game, choose_monster(lvl, getattr(m, 'dtag', 'crypt')), c[0], c[1], lvl)
        o.awake = True
        m.mons.append(o)
        st['left'].append(o.id)
    game.flash(cells[:2 + st['waves']], (230, 60, 60), '*', .3)


def waves(game, rid, st):
    m = game.map
    if any(o.id in st['left'] for o in m.mons):
        return
    if st['waves'] < 3:
        st['waves'] += 1
        game.msg('The circle flares again. More come.', 'bad')
        _wave(game, rid, st)
        return
    st['waves'], st['won'] = 0, True
    from .entities import random_gear
    it = random_gear(game, getattr(m, 'level', 1) + 2, 1.6)
    it.x, it.y = game.player.x, game.player.y
    m.items.append(it)
    game.msg('The signs go dark. Where the last of them fell, something is left: the circle pays what it owes.', 'gold')


def a_statues(game, x, y, rid, st):
    game.msg('Cold carved stone, a warrior with a blank face.')
    return 0


def a_bier(game, x, y, rid, st):
    game.msg('A stone bier. Whoever lay on it was carried off by the bones long ago.')
    return 0


def a_nest(game, x, y, rid, st):
    EV.ask(game, 'k5_nest', 'The nest', 'Eggs as big as your head, sticky and warm. Something moves inside them.',
           [('Smash the eggs', 'smash'), ('Leave them be', 'bye')], cell=(x, y))
    return 0


def r_nest(game, choice, ctx):
    from .entities import make_monster
    from .worldgen import free_around
    if choice != 'smash':
        return
    m = game.map
    x, y = ctx['cell']
    m.set(x, y, D.FLOOR)
    m.things.pop((x, y), None)
    if random.random() < .5:
        sp = [c for c in free_around(game, m, x, y, 1) if not game.occupied(m, *c)]
        for c in sp[:2]:
            o = make_monster(game, 'spiderling' if 'spiderling' in D.MONSTERS else 'spider', c[0], c[1],
                             getattr(m, 'level', 1))
            o.awake = True
            m.mons.append(o)
        game.msg('You smash the eggs, but some were ready to hatch: things scuttle out at you!', 'bad')
    else:
        game.msg('You smash the eggs. Nothing will hatch from these now.', 'good')


def a_gong(game, x, y, rid, st):
    EV.ask(game, 'k5_gong', 'The gong', 'A great bronze gong. One stroke would wake everything on this level.',
           [('Strike it', 'strike'), ('Leave it', 'bye')])
    return 0


def r_gong(game, choice, ctx):
    if choice == 'strike':
        game.map.gonged = True
        game.msg('BOOOM. The sound rolls through the halls, and everything wakes.', 'bad')
        wake_all(game)


def a_cell(game, x, y, rid, st):
    m = game.map
    who = st.get('cells', {}).get(x)
    if who == 'captive' and any(o.is_npc and o.x == x for o in m.mons):
        text = 'Behind the bars, a prisoner grips them and begs you to open the cell.'
    elif who == 'beast' and any(not o.is_npc and o.x == x for o in m.mons):
        text = 'Behind the bars, something big shifts in the dark and growls. Better left locked, perhaps.'
    else:
        game.msg('An empty cell. Old straw, and marks scratched on the wall.')
        return 0
    EV.ask(game, 'k5_cell', 'A cell', text, [('Open the cell', 'open'), ('Leave it shut', 'bye')], rid=rid, cell=(x, y))
    return 0


def r_cell(game, choice, ctx):
    if choice != 'open':
        return
    m, p = game.map, game.player
    x, y = ctx['cell']
    m.set(x, y, D.FLOOR)
    m.things.pop((x, y), None)
    st = state(m, ctx['rid'])
    who = st.get('cells', {}).pop(x, None)
    if who == 'captive':
        npc = next((o for o in m.mons if o.is_npc and o.x == x), None)
        if npc:
            m.mons.remove(npc)
            game.gain_xp(20 + getattr(m, 'level', 1) * 6)
            text = game.rumor()
            game.msg(f'{npc.name} stumbles out, weeping with thanks. "Bless you. Listen: {text}" '
                     'Then they hurry off towards the stairs.' if text else
                     f'{npc.name} stumbles out, weeping with thanks, and hurries off towards the stairs.', 'good')
    elif who == 'beast':
        for o in m.mons:
            if not o.is_npc and o.x == x:
                o.awake = True
        game.msg('The cell door creaks open, and what was inside comes out.', 'bad')


def a_mirror(game, x, y, rid, st):
    from .entities import make_monster
    from .worldgen import free_around
    if _once(game, st, 'looked', 'The mirror is cracked across now, and shows nothing.'):
        return 0
    m, p = game.map, game.player
    sp = [c for c in free_around(game, m, p.x, p.y, 1) if not game.occupied(m, *c)]
    if not sp:
        st['looked'] = False
        return 0
    k = 'shade' if 'shade' in D.MONSTERS else 'ghost'
    o = make_monster(game, k, sp[0][0], sp[0][1], getattr(m, 'level', 1) + 2)
    s = game.stats()
    o.name, o.ch, o.fg, o.awake = 'Double', '@', (150, 150, 170), True
    o.hp = o.maxhp = max(o.maxhp, round(s['max_life'] * .6))
    m.mons.append(o)
    game.msg('You look into the mirror. Your reflection smiles, which you did not, and steps out.', 'bad')
    return 1


def a_menagerie(game, x, y, rid, st):
    if st.get('pulled'):
        game.msg('The lever is down. The cages stand open.')
        return 0
    EV.ask(game, 'k5_lever', 'The lever', 'One pull would open every cage at once. The beasts would go for whoever is '
           'nearest: you, or anything else that lives down here.', [('Pull the lever', 'pull'), ('Leave it', 'bye')], rid=rid)
    return 0


def r_lever(game, choice, ctx):
    if choice != 'pull':
        return
    m, p = game.map, game.player
    st = state(m, ctx['rid'])
    st['pulled'] = True
    inside = set(cells_of(m, ctx['rid']))
    for c, ch in m.marks.items():
        if ch == 'J' and c in inside:
            m.set(c[0], c[1], D.FLOOR)
    beasts = [o for o in m.mons if getattr(o, 'caged', False)]
    game.msg('Chains rattle, and the cage doors fly up. The beasts are out!', 'bad')
    for b in beasts:
        b.caged, b.awake = False, True
        prey = [o for o in m.mons if not o.is_npc and o not in beasts and cheb(o.x, o.y, b.x, b.y) <= 8]
        if prey and min(cheb(o.x, o.y, b.x, b.y) for o in prey) < cheb(p.x, p.y, b.x, b.y):
            o = min(prey, key=lambda q: cheb(q.x, q.y, b.x, b.y))
            game.msg(f'{_the(b)} falls on {o.the()}!', 'info')
            dealt = sum(random.randint(*b.dmg) for _ in range(3))
            o.hp -= dealt
            b.hp -= sum(random.randint(*o.dmg) for _ in range(2))
            if o.hp <= 0:
                game.kill(o)
            if b.hp <= 0:
                game.kill(b)


def a_sanctuary(game, x, y, rid, st):
    if getattr(game.map, 'warded', None) and not st.get('told'):
        st['told'] = True
        game.msg('The warding signs are whole. No creature of the dark will come in here; you could rest.', 'info')
    return 0


def a_arch(game, x, y, rid, st):
    from . import hidden as HD
    if not HD.known(game):
        game.msg('An arch of the old ways. It hums faintly, but you do not know its word.')
        return 0
    EV.ask(game, 'k5_arch', 'The old arch', 'The arch hums. You know a word of the old ways: spoken here, it would '
           'take you up and out, to the land above.', [('Speak the word', 'go'), ('Keep silent', 'bye')])
    return 0


def r_arch(game, choice, ctx):
    if choice != 'go':
        return
    game.msg('You speak the word. The arch fills with grey light, and you step through.', 'gold')
    game.leave_to_over()


def a_collapse(game, x, y, rid, st):
    from . import deephold as DH
    m = game.map
    m.things.pop((x, y), None)
    d = game.world.dungeons.get(getattr(m, 'did', None))
    if d is None or getattr(m, 'depth', 0) >= d.depth or random.random() < .5:
        game.msg('The floor creaks under you, but holds.', 'info')
        return 0
    m.set(x, y, D.CHASM)
    game.msg('The floor gives way under you!', 'bad')
    DH.r_chasm(game, 'down', {})
    return 1


def a_herbs(game, x, y, rid, st):
    from . import foraging as FG
    picked = st.setdefault('picked', set())
    if (x, y) in picked:
        return 0
    picked.add((x, y))
    key = random.choices(['yarrow', 'moonpetal', 'feverfew', 'kingsfoil'], [4, 3, 3, 1])[0]
    it = FG.make_plant(game, key, 1)
    if game.add_to_inv(it):
        game.msg(f'In the pale light something grows that you can use: {it.display_name().lower()}.', 'good')
    return 1


def a_gears(game, x, y, rid, st):
    game.msg('Gears as tall as you turn in the wall. The bars beyond rise and fall with them: wait for the right moment.')
    return 0


def a_dice(game, x, y, rid, st):
    from .money import fmt
    m, p = game.map, game.player
    if not any(o.is_npc and getattr(o, 'role', '') == 'gambler' for o in m.mons):
        game.msg('An empty dice table. The game is over.')
        return 0
    EV.ask(game, 'k5_dice', 'The dice table', 'Three bandits look up from their dice. "In or out, stranger? One silver a '
           'throw."', [(f'Play a round ({fmt(100)})', 'play' if p.gold >= 100 else None),
                       ('Watch their hands closely', 'watch'), ('Walk away', 'bye')], rid=rid)
    return 0


def r_dice(game, choice, ctx):
    from .entities import make_monster
    from .money import purse
    m, p = game.map, game.player
    if choice == 'play':
        p.gold -= 100
        st = state(m, ctx['rid'])
        st['played'] = st.get('played', 0) + 1
        if random.random() < .38:
            p.gold += 250
            game.msg('The dice fall your way. They grumble and push the pot over to you.', 'good')
        else:
            game.msg('The dice fall against you. Again. They grin.', 'bad')
        game.end_turn(5)
    elif choice == 'watch':
        game.end_turn(3)
        if random.random() < .3 + p.dex / 200:
            game.msg('There: a loaded die, palmed and swapped. "Cheats!" They go for their knives. The pot is yours, '
                     'if you live.', 'bad')
            gamblers = [o for o in m.mons if o.is_npc and getattr(o, 'role', '') == 'gambler']
            for o in gamblers:
                m.mons.remove(o)
                b = make_monster(game, 'bandit', o.x, o.y, getattr(m, 'level', 1))
                b.awake = True
                m.mons.append(b)
            from .entities import Item
            it = Item(game.new_id(), 'gold', 'gold', purse(getattr(m, 'level', 1), .8))
            it.x, it.y = p.x, p.y
            m.items.append(it)
        else:
            game.msg('You watch closely. If they cheat, they are better at it than you are at seeing it.')


def a_plate(game, x, y, rid, st):
    return 0


def a_echo(game, x, y, rid, st):
    st['echo'] = True
    return 0


ACTIONS = {
    'shrine': a_shrine, 'library': a_library, 'fountain': a_fountain, 'forge': a_forge, 'cook': a_cook,
    'alchemy': a_alchemy, 'fungus': a_fungus, 'larder': a_larder, 'wishing': a_wishing, 'training': a_training,
    'maptable': a_maptable, 'wine': a_wine, 'choice': a_choice, 'armoury': a_armoury, 'adventurer': a_adventurer,
    'circle': a_circle, 'statues': a_statues, 'bier': a_bier, 'nest': a_nest, 'gong': a_gong, 'cell': a_cell,
    'mirror': a_mirror, 'menagerie': a_menagerie, 'sanctuary': a_sanctuary, 'arch': a_arch, 'collapse': a_collapse,
    'herbs': a_herbs, 'gears': a_gears, 'dice': a_dice, 'plate': a_plate, 'echo': a_echo,
}
EV.RESOLVERS.update({'k5_wish': r_wish, 'k5_choice': r_choice, 'k5_circle': r_circle, 'k5_nest': r_nest,
                     'k5_gong': r_gong, 'k5_cell': r_cell, 'k5_lever': r_lever, 'k5_arch': r_arch, 'k5_dice': r_dice})
