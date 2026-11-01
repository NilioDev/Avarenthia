"""The puzzle things of the drawn rooms (approved 31 October 2026, the editor's round B2; `puzzels.md` items 1-26).

Every one is a tile used by walking into it or stepping on it, never a new key. They tell the room's script
(themes.py: when / if / then, switches, counters, timers) what happened, with whens of their own:
  press / release   a pressure plate (do:pressure) goes down under anything that stands on it (you, a block, a creature, your hireling)
  lit               a brazier catches fire          sun        the sunbeam reaches a sun disc
  hit               a crystal switch is struck      break      a cracked wall gives way
  solved            a riddle stone is answered      unlock     the place's own key turns in a keyhole
  order:ABC         bells (or gongs) are struck in this order
and thens of their own: arrows:<mark> (the slits there shoot along their line), raise:red / raise:blue (one colour of
blocks up, the other down), water:down / water:up (the sluice's water), become:<mark>:<tile name>.

Fair to the player (roguelike): a room with blocks has a lever that sets it back (then=reset); the way on never hangs
on a puzzle; hints are in the world. The state of each room lives on the map (themes.state), so a gate you opened is
still open when you come back. Puzzle things 27-44 come with round C."""
import random

from . import data as D
from . import events as EV

ACTS = {}           # what each puzzle thing does when you walk into it or step on it: act -> fn(game, x, y, rid, st)
RIDDLES = [
    ('I have cities but no houses, forests but no trees, water but no fish. What am I?',
     ['A map', 'A dream', 'A painting'], 0),
    ('The more you take, the more you leave behind. What are they?', ['Coins', 'Footsteps', 'Breaths'], 1),
    ('What can run but never walks, has a mouth but never talks?', ['A river', 'A wolf', 'A bell'], 0),
    ('I am always hungry and must be fed; the finger I lick will soon turn red.', ['A blade', 'Fire', 'A leech'], 1),
    ('Feed me and I live, give me a drink and I die.', ['Fire', 'A seed', 'A thirst'], 0),
    ('What has roots nobody sees, is taller than trees, up it goes and yet never grows?',
     ['A mountain', 'A tower', 'A cloud'], 0),
]
BOOK_LINES = [
    'The page is foxed and the chain is cold. "Who sets the stones in their order sets the door in its frame."',
    'A builder\'s note: "The cellar floods at the sluice. Mind the low road."',
    'A hand of long ago: "The light falls from above at noon. The silver turns it where it is wanted."',
    'A prayer, half rubbed away: "...and what is taken from the god must be paid for in weight..."',
    'A list of the dead of this place, and beside each name a small cut mark.',
    'A warden\'s rule: "The red stands when the blue lies down. Strike the crystal and they change places."',
]


def act(name):
    def deco(fn):
        ACTS[name] = fn
        return fn
    return deco


def _room_cells(m, rid):
    from .themes import cells_of
    return set(cells_of(m, rid))


def _fire(game, when, rid, cell=None):
    """The room's events for this moment: those at this thing's mark (at=), and those of the whole room (no at=)."""
    from .themes import _holds, _then
    for ev in list(getattr(game.map, 'events', ())):
        if ev['done'] or ev['when'] != when or ev['room'] != rid:
            continue
        if ev['at'] and (cell is None or cell not in ev['at']):
            continue
        if not all(_holds(game, c, rid) for c in ev['cond']):
            continue
        if not ev['again']:
            ev['done'] = True
        for th in ev['then']:
            _then(game, th, rid)


def _set(m, c, tile, rid=None, act_name=None):
    m.set(c[0], c[1], tile)
    things = m.__dict__.setdefault('things', {})
    if act_name is None:
        things.pop(c, None)
    else:
        things[c] = (act_name, rid)


# ------------------------------------------------------------------ 1-2: plates and blocks
@act('pressure')
def a_plate(game, x, y, rid, st):
    return 0            # plates go down and up in tick(), for anything that stands on them


def _plate_load(game, m, c):
    return game.occupied(m, *c) or (game.player.x, game.player.y) == c or c in m.__dict__.get('blocks_on', {})


@act('block')
def a_block(game, x, y, rid, st):
    """Walk into a block and it slides one cell on, if the cell is free (no pulling: Sokoban)."""
    m, p = game.map, game.player
    dx, dy = x - p.x, y - p.y
    if abs(dx) + abs(dy) != 1:
        game.msg('The block will not move that way.')
        return 0
    to = (x + dx, y + dy)
    t = m.tile(*to)
    if not m.inb(*to) or game.occupied(m, *to) or t not in ROLL_ON + DROP_IN:
        game.msg('The block will not budge; something is in the way.')
        return 0
    name = m.things[(x, y)][0]
    move_block(game, (x, y), to, rid, m.tile(x, y), name)
    p.x, p.y = x, y
    if t in DROP_IN:
        return 1
    game.msg('You put your shoulder to the barrel. It rolls a step on.' if name == 'oil' else
             'You put your shoulder to the block. It grinds a step on.')
    return 1


ROLL_ON = (D.FLOOR, D.PLATE, D.PLATEDOWN, D.PORTAL, D.SPIKEHOLES, D.REDDOWN, D.BLUEDOWN, D.SLICK)
DROP_IN = (D.CHASM, D.WATER, D.HOLE)           # a block fills a chasm or deep water; through a hole it falls below
MOVERS = {D.SBLOCK: 'block', D.OILBARREL: 'oil', D.MIMIC: 'mimic', D.STALKER: 'stalker'}


def move_block(game, a, b, rid, tile=D.SBLOCK, name='block', m=None):
    """A block (or a barrel, or a statue) from a to b: the tile under it comes back at a, and a plate, portal or ice at
    b does its part. A block pushed into a chasm or deep water fills it; into a hole, it falls to the floor below."""
    m = m or game.map
    under = m.__dict__.setdefault('under', {})
    held = m.__dict__.setdefault('under_thing', {})        # the plate (or other thing) a block stands on
    on = m.__dict__.setdefault('blocks_on', {})
    back = under.pop(a, D.FLOOR)
    m.things.pop(a, None)
    if a in held:
        m.things[a] = held.pop(a)
    on.pop(a, None)
    if back == D.PLATE:                               # the plate it stood on comes up
        m.set(a[0], a[1], D.PLATE)
        _fire(game, 'release', m.things.get(a, ('', rid))[1], a)
    else:
        m.set(a[0], a[1], back)
    t = m.tile(*b)
    if t in (D.CHASM, D.WATER) and name in ('block', 'oil'):
        m.set(b[0], b[1], D.FLOOR)
        game.msg('The block topples in with a great splash. Its top stands level with the floor.' if t == D.WATER else
                 'The block topples into the chasm and jams there. You could walk on it.')
        return
    if t == D.HOLE:
        game.msg('The block drops through the hole. Far below, stone strikes stone.')
        fall_below(game, m, b, tile, name)
        return
    if t == D.PORTAL:                                 # through the portal with it
        other = _other_portal(m, b)
        if other and not game.occupied(m, *other) and other not in on:
            b = other
            t = m.tile(*b)
    if t == D.SLICK:                                  # it slides on over the ice
        d = (b[0] - a[0], b[1] - a[1])
        while m.tile(b[0] + d[0], b[1] + d[1]) in (D.SLICK, D.FLOOR) and not game.occupied(m, b[0] + d[0], b[1] + d[1]) \
                and m.tile(*b) == D.SLICK:
            b = (b[0] + d[0], b[1] + d[1])
        t = m.tile(*b)
    under[b] = t if t != D.PLATEDOWN else D.PLATE
    on[b] = True
    if b in m.things:
        held[b] = m.things[b]
    m.set(b[0], b[1], tile)
    m.things[b] = (name, rid)
    if t == D.PLATE:                                  # a plate goes down under the block
        _fire(game, 'press', held.get(b, ('', rid))[1], b)


# ------------------------------------------------------------------ 3: the lever
@act('lever')
def a_lever(game, x, y, rid, st):
    """The handle goes over: ⌐ off, ¬ on. What it works is the room's script (when=bump at the lever)."""
    m = game.map
    m.set(x, y, D.LEVERON if m.tile(x, y) == D.LEVER else D.LEVER)
    game.msg('You throw the lever. Something clanks in the walls.' if m.tile(x, y) == D.LEVERON
             else 'You pull the lever back.')
    return 1


# ------------------------------------------------------------------ 4-5: crystal switches, red and blue blocks
@act('crystal')
def a_crystal(game, x, y, rid, st):
    game.msg('You strike the crystal. It rings, and changes colour.')
    flip_crystals(game, rid)
    _fire(game, 'hit', rid, (x, y))
    return 1


def flip_crystals(game, rid, to=None):
    m = game.map
    st = _state(m, rid)
    now = st.get('colour', 'red')
    st['colour'] = to or ('blue' if now == 'red' else 'red')
    raise_colour(game, rid, st['colour'])
    for c in _room_cells(m, rid) | _ring(m, rid):
        if m.tile(*c) in (D.REDCRYSTAL, D.BLUECRYSTAL):
            m.set(c[0], c[1], D.REDCRYSTAL if st['colour'] == 'red' else D.BLUECRYSTAL)


def raise_colour(game, rid, colour):
    """One colour of blocks stands up and closes the way, the other lies down. A block that should rise under
    someone waits until the cell is free (tick)."""
    m = game.map
    up, down = ((D.REDUP, D.REDDOWN), (D.BLUEUP, D.BLUEDOWN))
    if colour == 'blue':
        up, down = down, up
    wait = m.__dict__.setdefault('to_rise', {})
    for c in _room_cells(m, rid):
        t = m.tile(*c)
        if t == up[1]:                       # the risen colour's sunk blocks rise
            if game.occupied(m, *c) or (game.player.x, game.player.y) == c:
                wait[c] = up[0]
            else:
                m.set(c[0], c[1], up[0])
        elif t == down[0]:
            m.set(c[0], c[1], down[1])
            wait.pop(c, None)


# ------------------------------------------------------------------ 6: braziers
@act('brazier')
def a_brazier(game, x, y, rid, st):
    m, p = game.map, game.player
    if m.tile(x, y) == D.FIREBOWL:
        p.buffs = [b for b in p.buffs if b[0] != 'brand'] + [['brand', 1, 8, 'A burning brand']]
        game.msg('You take a burning brand from the brazier. It will not last long.')
        return 1
    if any(b[0] == 'brand' for b in p.buffs):
        light(game, (x, y), rid)
        p.buffs = [b for b in p.buffs if b[0] != 'brand']
        return 1
    game.msg('A cold brazier, full of old pitch. Fire would wake it: a spell, or a brand from one that burns.')
    return 0


def light(game, c, rid):
    m = game.map
    m.set(c[0], c[1], D.FIREBOWL)
    m.lights.append((c[0], c[1], (255, 150, 60), 4))
    game.msg('The brazier catches with a roar.', 'good')
    _fire(game, 'lit', rid, c)


# ------------------------------------------------------------------ 7: mirrors and the sun disc
@act('swivel')
def a_mirror(game, x, y, rid, st):
    m = game.map
    m.set(x, y, D.SWIVEL2 if m.tile(x, y) == D.SWIVEL else D.SWIVEL)
    game.msg('The mirror turns a quarter on its swivel.')
    beam(game)
    return 1


@act('sundisc')
def a_sundisc(game, x, y, rid, st):
    game.msg('A disc of beaten gold, set to catch the sun.' if not st.get('sunlit') else 'The disc blazes with light.')
    return 0


def beam(game, m=None):
    """The sunbeams of the level, from each shaft of daylight into its room, turned by the mirrors. With m given (the
    level being made) the beam is only drawn: a disc lit then answers on the first turn there."""
    made = m is not None
    m = m or game.map
    out = {}
    night = None
    for c, (a, rid) in list(getattr(m, 'things', {}).items()):
        if a not in ('shaft', 'moonshaft'):
            continue
        if a == 'moonshaft':                          # the moon shines in only by night
            if night is None:
                from .towns import is_night
                night = is_night(game)
            if not night and not made:            # (a level being made is checked as if by night)
                continue
        d = next(((dx, dy) for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0))
                  if D.TILES[m.tile(c[0] + dx, c[1] + dy)].walk), None)
        x, y = c
        steps = 0
        while d and steps < 200:
            steps += 1
            x, y = x + d[0], y + d[1]
            t = m.tile(x, y)
            if t in (D.SWIVEL, D.SWIVEL2) and made:
                m.__dict__.setdefault('_first_mirror', {}).setdefault(c, (x, y))
            if t == D.SWIVEL:
                d = (-d[1], -d[0])
                out[(x, y)] = '+'
                continue
            if t == D.SWIVEL2:
                d = (d[1], d[0])
                out[(x, y)] = '+'
                continue
            if t == D.SUNDISC:
                st = _state(m, rid)
                if made:
                    m.__dict__.setdefault('_solved_shafts', []).append(c)
                elif not st.get('sunlit'):
                    st['sunlit'] = True
                    game.msg('The beam strikes the golden disc. It blazes, and the room answers.' if a == 'shaft' else
                             'Moonlight strikes the disc. It shines white, and the room answers.', 'good')
                    _fire(game, 'sun' if a == 'shaft' else 'moon', rid, (x, y))
                break
            if not D.TILES[t].walk or not made and game.occupied(m, x, y) and (x, y) != (game.player.x, game.player.y):
                break
            out[(x, y)] = '│' if d[0] == 0 else '─'
    m.sunbeam = out


# ------------------------------------------------------------------ 8: bells in order
@act('bell')
def a_bell(game, x, y, rid, st):
    m = game.map
    mark = getattr(m, 'marks', {}).get((x, y))
    game.msg('The bell rings out, clear and long.' if m.tile(x, y) == D.BELL else 'The gong booms.')
    if not mark:
        return 1
    rung = st.setdefault('rung', [])
    rung.append(mark)
    del rung[:-12]
    s = ''.join(rung)
    for ev in getattr(m, 'events', ()):
        if ev['room'] == rid and ev['when'].startswith('order:') and s.endswith(ev['when'][6:]):
            _fire(game, ev['when'], rid)
            rung.clear()
    return 1


# ------------------------------------------------------------------ 10-13: cracked walls, crumbling floor, ice, spikes
@act('cracked')
def a_cracked(game, x, y, rid, st):
    from .weapons import wielded
    if wielded(game) in ('warhammer', 'mace', 'maul') or game.stats().get('str', 0) >= 60:
        game.map.set(x, y, D.FLOOR)
        game.map.things.pop((x, y), None)
        game.msg('The cracked wall gives under your blow and falls in. A way lies behind it.', 'good')
        _fire(game, 'break', rid, (x, y))
        return 1
    game.msg('The wall is cracked right through. A heavy blow would bring it down: a war hammer, a mace, or a '
             'strong arm.')
    return 0


@act('crumble')
def a_crumble(game, x, y, rid, st):
    game.msg('The floor shifts under your feet. It will not bear you twice.', 'bad')
    return 0


@act('ice')
def a_ice(game, x, y, rid, st):
    """You slide on until something stops you."""
    m, p = game.map, game.player
    prev = getattr(m, '_ppos', None)
    if not prev or prev == (x, y):
        return 0
    d = (x - prev[0], y - prev[1])
    if abs(d[0]) + abs(d[1]) != 1:
        return 0
    slid = 0
    while m.tile(p.x, p.y) == D.SLICK and slid < 60:
        n = (p.x + d[0], p.y + d[1])
        if not D.TILES[m.tile(*n)].walk or game.occupied(m, *n):
            break
        p.x, p.y = n
        slid += 1
    if slid:
        game.msg('You slide across the ice.')
        game.compute_fov()
    m._ppos = (p.x, p.y)
    return 0


@act('spikes')
def a_spikes(game, x, y, rid, st):
    if game.map.tile(x, y) == D.SPIKESUP:
        game.hurt(max(3, game.stats()['max_life'] // 8), 'the spikes')
        game.msg('Spikes drive up through your feet!', 'bad')
    return 0


# ------------------------------------------------------------------ 14: portals
def _other_portal(m, c):
    rid = _rid(m, c)
    return next((o for o in _room_cells(m, rid) if o != c and m.tile(*o) == D.PORTAL), None)


@act('portal')
def a_portal(game, x, y, rid, st):
    m, p = game.map, game.player
    if getattr(m, '_ported', None) == (x, y):
        return 0
    other = _other_portal(m, (x, y))
    if other and not game.occupied(m, *other):
        p.x, p.y = other
        m._ported = other                      # you arrive on the other stone: it does not send you straight back
        game.msg('The world folds. You stand on the other stone.')
        game.compute_fov()
    return 0


# ------------------------------------------------------------------ 15: the idol on its plinth
@act('idol')
def a_idol(game, x, y, rid, st):
    p = game.player
    swaps = [it for it in p.inv if it.k not in ('gold', 'quest')]
    opts = [('Take the idol', 'take')]
    opts.append(('Put something of yours in its place, and take the idol', 'swap' if swaps else None))
    opts.append(('Leave it', 'leave'))
    EV.ask(game, 'pz_idol', 'The golden idol', 'A small god of gold, alone on its plinth. The plinth sits a finger '
           'proud of the floor, as if it would rise.', opts, x=x, y=y, rid=rid)
    return 0


def r_idol(game, choice, ctx):
    from .entities import Item
    if choice not in ('take', 'swap'):
        return
    m, p = game.map, game.player
    x, y, rid = ctx['x'], ctx['y'], ctx['rid']
    if choice == 'swap':
        it = max((i for i in p.inv if i.k not in ('gold', 'quest')), key=lambda i: i.value())
        p.inv.remove(it)
        game.msg(f'You set {it.display_name()} on the plinth as you lift the idol. The plinth does not stir.', 'good')
    idol = Item(game.new_id(), 'trophy', 'idol')
    idol.name, idol.worth = 'Golden Idol', 40
    p.inv.append(idol)
    _set(m, (x, y), D.PLINTH)
    _fire(game, 'take', rid)
    if choice == 'take':
        game.msg('The plinth rises with a click. The ceiling answers: stone comes down all round you!', 'bad')
        cells = [c for c in _room_cells(m, rid) if m.tile(*c) == D.FLOOR and not game.occupied(m, *c)
                 and c != (p.x, p.y)]
        random.shuffle(cells)
        for c in cells[:max(3, len(cells) // 6)]:
            m.set(c[0], c[1], D.RUBBLE)
        game.hurt(max(4, game.stats()['max_life'] // 6), 'falling stone')


EV.RESOLVERS['pz_idol'] = r_idol


# ------------------------------------------------------------------ 16: the keyhole and the place's own key
@act('keyhole')
def a_keyhole(game, x, y, rid, st):
    m, p = game.map, game.player
    key = next((it for it in p.inv if it.k == 'vkey' and getattr(it, 'door', None) == (m.key, ('hole', x, y))), None)
    if not key:
        game.msg('A keyhole, worn smooth. Its key must lie somewhere in this place.')
        return 0
    p.inv.remove(key)
    _set(m, (x, y), D.WALL)
    game.msg('The key turns with a deep sound somewhere behind the stone.', 'good')
    _fire(game, 'unlock', rid, (x, y))
    return 1


def hide_key(game, m, c, lvl):
    """The keyhole's key, somewhere far off on the level, often with a guard."""
    from .entities import Item, make_monster
    from .worldgen import rand_free, free_around, choose_monster
    far = rand_free(game, m, lambda t: t == D.FLOOR, (c[0], c[1], 25))
    if not far:
        return
    key = Item(game.new_id(), 'vkey', 'k5', 1)
    key.name, key.door = 'Worn Bronze Key', (m.key, ('hole', c[0], c[1]))
    key.x, key.y = far
    m.items.append(key)
    if random.random() < .6:
        sp = [s for s in free_around(game, m, far[0], far[1], 1) if not game.occupied(m, *s)]
        if sp:
            m.mons.append(make_monster(game, choose_monster(lvl, getattr(m, 'dtag', 'crypt')), sp[0][0], sp[0][1], lvl))


# ------------------------------------------------------------------ 17: the sluice
@act('sluice')
def a_sluice(game, x, y, rid, st):
    m = game.map
    if (game.player.x, game.player.y) == (x, y):
        return 0                                     # standing in the open sluice works nothing
    low = m.tile(x, y) == D.SLUICE
    m.set(x, y, D.OPENSLUICE if low else D.SLUICE)
    water(game, rid, 'down' if low else 'up')
    return 1


def water(game, rid, way):
    """The room's water a step lower (deep to shallow, shallow to dry) or back as it was."""
    m = game.map
    st = _state(m, rid)
    first = st.setdefault('water0', {f'{c[0]},{c[1]}': m.tile(*c) for c in _room_cells(m, rid)
                                     if m.tile(*c) in (D.WATER, D.SHALLOW)})
    if way == 'down':
        for k, t in first.items():
            c = tuple(int(v) for v in k.split(','))
            m.set(c[0], c[1], D.SHALLOW if t == D.WATER else D.FLOOR)
        game.msg('Water drains away through the sluice. The floor of the room comes up out of it.')
    else:
        for k, t in first.items():
            c = tuple(int(v) for v in k.split(','))
            if not game.occupied(m, *c):
                m.set(c[0], c[1], t)
        game.msg('The sluice shuts. Water comes back into the room.')


# ------------------------------------------------------------------ 18: arrow slits
def arrows(game, rid, mark):
    """Each slit with this mark shoots along its line into the room: the first in the way is hit; a block stops it."""
    m, p = game.map, game.player
    lvl = getattr(m, 'level', 1)
    for c, ch in getattr(m, 'marks', {}).items():
        if ch != mark:
            continue
        d = next(((dx, dy) for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0))
                  if D.TILES[m.tile(c[0] + dx, c[1] + dy)].walk), None)
        if not d:
            continue
        x, y = c
        for _ in range(30):
            x, y = x + d[0], y + d[1]
            if not D.TILES[m.tile(x, y)].walk:
                break
            if (x, y) == (p.x, p.y):
                game.msg('Arrows hiss out of the wall!', 'bad')
                game.hurt(4 + lvl * 2, 'an arrow trap')
                break
            o = next((o for o in m.mons if (o.x, o.y) == (x, y)), None)
            if o:
                o.hp -= 4 + lvl * 2
                game.msg(f'Arrows from the wall strike {o.name}!')
                if o.hp <= 0:
                    game.kill(o)
                break


# ------------------------------------------------------------------ 19: the riddle stone
@act('riddle')
def a_riddle(game, x, y, rid, st):
    if st.get('solved'):
        game.msg('The stone is silent. You answered it.')
        return 0
    i = st.setdefault('riddle', random.randrange(len(RIDDLES)))
    q, answers, _ok = RIDDLES[i]
    EV.ask(game, 'pz_riddle', 'The riddle stone', f'Letters cut deep in the stone: "{q}"',
           [(a, n) for n, a in enumerate(answers)] + [('Walk on', 'bye')], x=x, y=y, rid=rid)
    return 0


def r_riddle(game, choice, ctx):
    if choice == 'bye':
        return
    m = game.map
    st = _state(m, ctx['rid'])
    if choice == RIDDLES[st['riddle']][2]:
        st['solved'] = True
        game.msg('The letters fill with light, and fade. Stone grinds on stone somewhere near.', 'good')
        _fire(game, 'solved', ctx['rid'], (ctx['x'], ctx['y']))
    else:
        game.hurt(3, 'the riddle stone')
        game.msg('A cold spark leaps from the stone. That was not the answer.', 'bad')


EV.RESOLVERS['pz_riddle'] = r_riddle


# ------------------------------------------------------------------ 20-26: dungeon things
@act('sarcophagus')
def a_sarcophagus(game, x, y, rid, st):
    from .entities import Item, make_monster
    m = game.map
    if m.tile(x, y) != D.SARCO:
        game.msg('The sarcophagus lies open and empty.')
        return 0
    _set(m, (x, y), D.SARCOOPEN, rid, 'sarcophagus')
    r = random.random()
    lvl = getattr(m, 'level', 1)
    if r < .3:
        sp = [(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
              if D.TILES[m.tile(x + dx, y + dy)].walk and not game.occupied(m, x + dx, y + dy)]
        if sp:
            o = make_monster(game, random.choice(('skeleton', 'zombie')), sp[0][0], sp[0][1], lvl)
            o.awake = True
            m.mons.append(o)
            game.msg('You heave the lid aside. What lies inside sits up.', 'bad')
            return 1
    if r < .55:
        coin = Item(game.new_id(), 'gold', 'gold', random.randint(5, 20) * max(1, lvl))
        coin.x, coin.y = game.player.x, game.player.y
        m.items.append(coin)
        game.msg('You heave the lid aside. Bones, and a few old coins among them.', 'good')
    else:
        game.msg('You heave the lid aside. Only dust and bones, long at rest.')
    return 1


@act('offering')
def a_offering(game, x, y, rid, st):
    from .money import fmt
    p = game.player
    if st.get('given'):
        game.msg('Your coin still lies in the bowl.')
        return 0
    EV.ask(game, 'pz_offer', 'The offering bowl', 'A bowl of beaten bronze before an old god\'s niche. Coins of '
           'every age lie green in it.', [(f'Give {fmt(100)}', 'give' if p.gold >= 100 else None),
                                          ('Walk on', 'bye')], rid=rid)
    return 0


def r_offer(game, choice, ctx):
    if choice != 'give':
        return
    p = game.player
    p.gold -= 100
    _state(game.map, ctx['rid'])['given'] = True
    p.buffs = [b for b in p.buffs if b[0] != 'luck'] + [['luck', 1, D.DAY_LEN, 'The old god\'s favour']]
    game.msg('The coin rings on the others. For a moment you feel watched, kindly. (Lucky for a day)', 'good')


EV.RESOLVERS['pz_offer'] = r_offer


@act('scrying')
def a_scrying(game, x, y, rid, st):
    m = game.map
    if st.get('seen'):
        game.msg('The pool shows only your own face now.')
        return 0
    st['seen'] = True
    rid2 = random.choice([i for i in range(len(m.rooms)) if i != rid] or [rid])
    from .themes import cells_of
    near = set()
    for cx, cy in cells_of(m, rid2):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                near.add((cx + dx, cy + dy))
    for c in near:
        if m.inb(*c):
            m.seen[c[1] * m.w + c[0]] = 1
    game.msg('The still water clouds, then clears: you see another hall of this place, as if you stood in it.', 'good')
    return 1


@act('book')
def a_book(game, x, y, rid, st):
    i = st.setdefault('page', random.randrange(len(BOOK_LINES)))
    game.msg(BOOK_LINES[i], 'info')
    return 0


@act('eyes')
def a_eyes(game, x, y, rid, st):
    m, p = game.map, game.player
    if m.tile(x, y) == D.GEMIDOL:
        EV.ask(game, 'pz_eyes', 'The idol with gem eyes', 'Two green stones stare out of a face of old wood. They '
               'would come out with a knife.', [('Pry out the gems', 'take'), ('Leave it', 'bye')], x=x, y=y, rid=rid)
        return 0
    gems = next((it for it in p.inv if it.k == 'trophy' and it.t == 'gemeyes'), None)
    if gems:
        p.inv.remove(gems)
        p.buffs = [b for b in p.buffs if len(b) < 4 or b[3] != CURSE]
        _set(m, (x, y), D.GEMIDOL, rid, 'eyes')
        game.msg('You press the stones back into the wooden face. The weight on you lifts.', 'good')
        return 1
    game.msg('A blind idol of old wood, its eyes cut out.')
    return 0


CURSE = "The idol's curse"


def r_eyes(game, choice, ctx):
    from .entities import Item
    if choice != 'take':
        return
    m, p = game.map, game.player
    gems = Item(game.new_id(), 'trophy', 'gemeyes')
    gems.name, gems.worth = 'Two Green Gem Eyes', 30
    p.inv.append(gems)
    _set(m, (ctx['x'], ctx['y']), D.BLINDIDOL, ctx['rid'], 'eyes')
    p.buffs = [b for b in p.buffs if len(b) < 4 or b[3] != CURSE] + [['hit', -10, D.DAY_LEN * 30, CURSE]]
    game.msg('The gems come free. Something cold settles on your shoulders: the idol\'s curse, until the eyes go '
             'back or a priest lifts it.', 'bad')


EV.RESOLVERS['pz_eyes'] = r_eyes


@act('rope')
def a_rope(game, x, y, rid, st):
    m = game.map
    if getattr(m, 'last', False):
        game.msg('The rope hangs down into the dark, and ends in nothing.')
        return 0
    game.msg('You climb down the rope.')
    game.enter_dungeon(m.did, m.depth + 1, 'up')
    return 1


@act('ladder')
def a_ladder(game, x, y, rid, st):
    m = game.map
    if m.depth <= 1:
        game.msg('The ladder ends at a trapdoor that will not open.')
        return 0
    game.msg('You climb the ladder.')
    game.enter_dungeon(m.did, m.depth - 1, 'down')
    return 1


@act('shaft')
def a_shaft(game, x, y, rid, st):
    game.msg('Daylight falls in through a shaft in the stone.')
    return 0


# ================================================================== 27-44: more puzzle things (the editor's round C)
# ------------------------------------------------------------------ 27: mirror statues
def mimics(game):
    """Mirror statues copy the step you just took in their room: 'mimic' the same way, 'mimicx' mirrored left to
    right. Plates go down under them as under a block."""
    m, p = game.map, game.player
    prev = getattr(m, '_ppos', None)
    if not prev or prev == (p.x, p.y):
        return
    d = (p.x - prev[0], p.y - prev[1])
    if max(abs(d[0]), abs(d[1])) != 1:
        return
    here = _rid(m, (p.x, p.y))
    if here is None:
        return
    movers = [(c, a, rid) for c, (a, rid) in list(m.things.items()) if a in ('mimic', 'mimicx') and rid == here]
    for c, a, rid in movers:
        dd = d if a == 'mimic' else (-d[0], d[1])
        to = (c[0] + dd[0], c[1] + dd[1])
        if to in _room_cells(m, rid) and m.tile(*to) in ROLL_ON and not game.occupied(m, *to) and \
                to != (p.x, p.y) and m.things.get(to, ('',))[0] not in MOVER_NAMES:
            move_block(game, c, to, rid, D.MIMIC, a)


MOVER_NAMES = ('block', 'oil', 'mimic', 'mimicx', 'stalker')


@act('mimic')
def a_mimic(game, x, y, rid, st):
    game.msg('A statue of a traveller, like you. It stands as you stand, one step behind.')
    return 0


ACTS['mimicx'] = a_mimic


# ------------------------------------------------------------------ 28: the pale statue
@act('stalker')
def a_stalker(game, x, y, rid, st):
    game.msg('A pale statue, its hands over its face. You are sure it stood further off a moment ago.')
    return 0


def stalkers(game):
    """A pale statue comes a step nearer each turn you cannot see it, inside its own room."""
    m, p = game.map, game.player
    for c, (a, rid) in list(m.things.items()):
        if a != 'stalker' or game.visible(*c):
            continue
        if _rid(m, (p.x, p.y)) != rid:
            continue
        cells = _room_cells(m, rid)
        best = None
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            to = (c[0] + dx, c[1] + dy)
            if to in cells and m.tile(*to) in ROLL_ON and not game.occupied(m, *to) and to != (p.x, p.y) \
                    and m.things.get(to, ('',))[0] not in MOVER_NAMES:
                dist = abs(to[0] - p.x) + abs(to[1] - p.y)
                if best is None or dist < best[0]:
                    best = (dist, to)
        if best and best[0] < abs(c[0] - p.x) + abs(c[1] - p.y):
            move_block(game, c, best[1], rid, D.STALKER, 'stalker')


# ------------------------------------------------------------------ 29: the raft
@act('raft')
def a_raft(game, x, y, rid, st):
    """Step onto the raft and the current takes it the way you stepped, until it runs aground."""
    m, p = game.map, game.player
    prev = getattr(m, '_ppos', None)
    if not prev or prev == (x, y):
        return 0
    d = (x - prev[0], y - prev[1])
    if abs(d[0]) + abs(d[1]) != 1:
        return 0
    c, went = (x, y), 0
    while went < 60:
        n = (c[0] + d[0], c[1] + d[1])
        if m.tile(*n) != D.WATER or game.occupied(m, *n):
            break
        m.set(c[0], c[1], D.WATER)
        m.things.pop(c, None)
        m.set(n[0], n[1], D.RAFT)
        m.things[n] = ('raft', rid)
        c = n
        went += 1
    if went:
        p.x, p.y = c
        m._ppos = c
        game.msg('The current takes the raft and carries you across.')
        game.compute_fov()
    return 0


# ------------------------------------------------------------------ 30: wind in a passage
def winds(game):
    """Each vent blows along its line: the first one in the way is pushed a step on, unless a block shields it."""
    m, p = game.map, game.player
    for c, (a, rid) in list(m.things.items()):
        if a != 'vent':
            continue
        d = next(((dx, dy) for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0))
                  if D.TILES[m.tile(c[0] + dx, c[1] + dy)].walk), None)
        if not d:
            continue
        x, y = c
        for _ in range(20):
            x, y = x + d[0], y + d[1]
            if not D.TILES[m.tile(x, y)].walk:
                break
            o = next((o for o in m.mons if (o.x, o.y) == (x, y)), None)
            if (x, y) == (p.x, p.y) or o:
                n = (x + d[0], y + d[1])
                if D.TILES[m.tile(*n)].walk and not game.occupied(m, *n) and n != (p.x, p.y):
                    if o:
                        o.x, o.y = n
                    else:
                        p.x, p.y = n
                        m._ppos = n
                        if not getattr(m, '_wind_said', False):
                            m._wind_said = True
                            game.msg('A gale out of the wall pushes you back.', 'bad')
                break


@act('vent')
def a_vent(game, x, y, rid, st):
    game.msg('Cold wind roars out of a vent in the wall. A block in its way would break it.')
    return 0


# ------------------------------------------------------------------ 31: shifting walls
SHIFT_EVERY = 4


def shifts(game):
    m = game.map
    if game.turn % SHIFT_EVERY:
        return
    moved = False
    for c, (a, rid) in list(m.things.items()):
        if a != 'shift':
            continue
        t = m.tile(*c)
        if t == D.SHIFTWALL:
            m.set(c[0], c[1], D.SHIFTGAP)
            moved = True
        elif t == D.SHIFTGAP and not game.occupied(m, *c) and (game.player.x, game.player.y) != c:
            m.set(c[0], c[1], D.SHIFTWALL)
            moved = True
    if moved and any(game.visible(*c) for c, (a, _r) in m.things.items() if a == 'shift'):
        game.msg('Stone grinds on stone: the walls shift.')


@act('shift')
def a_shift(game, x, y, rid, st):
    game.msg('The wall stands in a groove in the floor. It moves on a rhythm, like the spikes.')
    return 0


# ------------------------------------------------------------------ 32-33: blocks into chasms and holes
def below_key(game, m):
    """The map key of the floor under this one, or None."""
    dg = game.world.dungeons.get(getattr(m, 'did', None)) if getattr(m, 'did', None) is not None else None
    if getattr(m, 'site', None) is not None and m.kind != 'dungeon':
        b = getattr(game.world.sites[m.site], 'below', None)
        return f'{b}:1' if b else None
    if dg is None:
        return None
    if getattr(dg, 'rise', False):
        if m.depth == 1:
            return game.world.sites[dg.site].map_key if getattr(dg, 'site', None) is not None else None
        return f'{dg.id}:{m.depth - 1}'
    return f'{dg.id}:{m.depth + 1}' if m.depth < dg.depth else None


def fall_below(game, m, c, tile, name):
    """A block through a hole lands on the floor below, on the same spot, and presses a plate there."""
    key = below_key(game, m)
    if key is None:
        return
    falls = game.__dict__.setdefault('falls', {})
    falls.setdefault(key, []).append((c, tile, name))
    if key in game.maps:
        land_falls(game, game.maps[key], key)


def land_falls(game, m, key):
    for c, tile, name in game.__dict__.get('falls', {}).pop(key, []):
        spot = c if m.inb(*c) and m.tile(*c) in ROLL_ON and not game.occupied(m, *c) else None
        if spot is None:
            continue
        rid = _rid(m, spot)
        t = m.tile(*spot)
        m.__dict__.setdefault('under', {})[spot] = D.PLATE if t == D.PLATEDOWN else t
        m.__dict__.setdefault('blocks_on', {})[spot] = True
        things = m.__dict__.setdefault('things', {})
        if spot in things:
            m.__dict__.setdefault('under_thing', {})[spot] = things[spot]
        m.set(spot[0], spot[1], tile)
        things[spot] = (name, rid)
        if t == D.PLATE:
            m.__dict__.setdefault('pending', []).append(('press', rid, spot))


@act('hole')
def a_hole(game, x, y, rid, st):
    game.msg('A square hole in the floor. Far below, the dark. Something heavy would go through it.')
    return 0


# ------------------------------------------------------------------ 34: the oil barrel
@act('oil')
def a_oil(game, x, y, rid, st):
    p = game.player
    if any(b[0] == 'brand' for b in p.buffs):
        p.buffs = [b for b in p.buffs if b[0] != 'brand']
        fuse(game, (x, y))
        return 1
    return a_block(game, x, y, rid, st)


def fuse(game, c):
    m = game.map
    if c in m.__dict__.setdefault('fuses', {}):
        return
    m.fuses[c] = 2
    game.msg('The oil catches. Get away from the barrel!', 'bad')


def blow(game, c):
    """The barrel bursts: fire round it, a blow to all beside it, and cracked walls fall in."""
    from . import spellmap as SM
    m, p = game.map, game.player
    lvl = getattr(m, 'level', 1)
    m.set(c[0], c[1], m.__dict__.get('under', {}).pop(c, D.FLOOR))
    m.things.pop(c, None)
    m.__dict__.get('blocks_on', {}).pop(c, None)
    game.msg('The barrel bursts in a ball of fire!', 'bad')
    game.shake()
    near = [(c[0] + dx, c[1] + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    for n in near:
        if m.tile(*n) == D.CRACKWALL:
            rid = _rid(m, n) if _rid(m, n) is not None else _ring_room(m, n)
            m.set(n[0], n[1], D.FLOOR)
            m.things.pop(n, None)
            game.msg('The cracked wall is blown in.', 'good')
            _fire(game, 'break', rid, n)
        elif m.tile(*n) == D.OILBARREL and n != c:
            fuse(game, n)
    for o in list(m.mons):
        if (o.x, o.y) in near:
            o.hp -= 10 + lvl * 2
            if o.hp <= 0:
                game.kill(o)
    if (p.x, p.y) in near:
        game.hurt(10 + lvl * 2, 'a bursting barrel', 'fire')
    SM.area(game, m, [n for n in near if D.TILES[m.tile(*n)].walk], D.BURNING)


def _ring_room(m, c):
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        r = _rid(m, (c[0] + dx, c[1] + dy))
        if r is not None:
            return r
    return None


# ------------------------------------------------------------------ 35: runes in order
@act('rune')
def a_rune(game, x, y, rid, st):
    """Step on the runes in the order cut somewhere in the place. A wrong one bites, and the row goes dark."""
    m = game.map
    if (game.player.x, game.player.y) != (x, y):
        game.msg('A rune is cut in the floor tile.')
        return 0
    mark = getattr(m, 'marks', {}).get((x, y))
    wants = [ev['when'][6:] for ev in getattr(m, 'events', ()) if ev['room'] == rid and ev['when'].startswith('order:')]
    if not mark or not wants:
        return 0
    seq = st.setdefault('runes', '') + mark
    done = next((w for w in wants if seq.endswith(w)), None)
    if done:
        st['runes'] = ''
        m.set(x, y, D.RUNELIT)
        game.msg('The last rune flares, and the whole row shines.', 'good')
        _fire(game, f'order:{done}', rid)
    elif any(w.startswith(seq) for w in wants):
        st['runes'] = seq
        m.set(x, y, D.RUNELIT)
        game.msg('The rune glows under your foot.')
    else:
        st['runes'] = ''
        for c in _room_cells(m, rid):
            if m.tile(*c) == D.RUNELIT:
                m.set(c[0], c[1], D.RUNE_T)
        game.hurt(3, 'a wrong rune')
        game.msg('A cold spark bites your foot, and the runes go dark.', 'bad')
    return 0


# ------------------------------------------------------------------ 36: the light floor
@act('lights')
def a_lights(game, x, y, rid, st):
    """Each tile you step on turns, and its four neighbours with it. All lit, and the room answers."""
    m = game.map
    if (game.player.x, game.player.y) != (x, y):
        return 0
    for c in ((x, y), (x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
        t = m.tile(*c)
        if t in (D.LIGHTOFF, D.LIGHTON) and m.things.get(c, ('',))[0] == 'lights':
            m.set(c[0], c[1], D.LIGHTON if t == D.LIGHTOFF else D.LIGHTOFF)
    tiles = [c for c, (a, r) in m.things.items() if a == 'lights' and r == rid]
    if tiles and all(m.tile(*c) == D.LIGHTON for c in tiles) and not st.get('alllit'):
        st['alllit'] = True
        game.msg('Every tile of the floor shines. Somewhere a bolt slides back.', 'good')
        _fire(game, 'solved', rid)
    return 0


# ------------------------------------------------------------------ 37: the scale
def weight(it):
    """How heavy a thing is on the scale."""
    if it.k == 'gear':
        return {'weapon': 3, 'body': 5, 'shield': 4, 'head': 2}.get(getattr(it, 'slot', ''), 1)
    return {'tome': 2, 'oldbook': 2, 'trophy': 2}.get(it.k, 1)


@act('scale')
def a_scale(game, x, y, rid, st):
    p = game.player
    if 'counter' not in st:
        st['counter'] = random.randint(4, 7)
    pan = st.setdefault('pan', [])
    on = sum(weight(i) for i in pan)
    text = (f'A great scale. On one pan lies a bronze weight with {st["counter"]} notches cut in it. On the other '
            + (f'lie {len(pan)} things of yours, weighing {on} notches.' if pan else 'lies nothing.'))
    opts = [(f'Put on {i.display_name()} ({weight(i)})', f'put:{i.id}') for i in p.inv
            if i.k not in ('gold', 'quest') and not game.is_equipped(i)][:10]
    if pan:
        opts.append(('Take your things back', 'back'))
    opts.append(('Walk on', 'bye'))
    EV.ask(game, 'pz_scale', 'The scale', text, opts, rid=rid, x=x, y=y)
    return 0


def r_scale(game, choice, ctx):
    m, p = game.map, game.player
    st = _state(m, ctx['rid'])
    pan = st.setdefault('pan', [])
    if choice == 'back':
        p.inv.extend(pan)
        pan.clear()
        game.msg('You take your things off the pan.')
        return
    if not str(choice).startswith('put:'):
        return
    it = next((i for i in p.inv if f'put:{i.id}' == choice), None)
    if it is None:
        return
    p.inv.remove(it)
    pan.append(it)
    on = sum(weight(i) for i in pan)
    if on == st['counter'] and not st.get('balanced'):
        st['balanced'] = True
        game.msg('The pans swing, and come to rest level. A latch clicks.', 'good')
        _fire(game, 'solved', ctx['rid'])
    elif on > st['counter']:
        game.msg('Your pan sinks to the floor. Too much.')
    else:
        game.msg('Your pan dips, but the bronze weight is heavier still.')


EV.RESOLVERS['pz_scale'] = r_scale


# ------------------------------------------------------------------ 38: spells as a key (always with another way)
@act('rod')
def a_rod(game, x, y, rid, st):
    game.msg('An iron rod stands out of the floor, wired into the wall. It hums when a storm is near.'
             if game.map.tile(x, y) == D.RODLIT else 'An iron rod stands out of the floor, wired into the wall.')
    return 0


@act('burnable')
def a_burnable(game, x, y, rid, st):
    game.msg('Old and dry. It would burn.')
    return 0


def on_spell(game, line):
    """A spell of Storm or Fire was cast: rods in sight hum, and webs, roots, braziers and barrels in sight within
    a few steps catch."""
    m, p = game.map, game.player
    if line not in ('storm', 'fire') or not getattr(m, 'things', None):
        return
    for c, (a, rid) in list(m.things.items()):
        if max(abs(c[0] - p.x), abs(c[1] - p.y)) > 7 or not game.visible(*c):
            continue
        if line == 'storm' and a == 'rod' and m.tile(*c) == D.ROD:
            m.set(c[0], c[1], D.RODLIT)
            game.msg('Lightning leaps to the iron rod. It hums, and something in the wall answers.', 'good')
            _fire(game, 'charged', rid, c)
        elif line == 'fire' and a == 'burnable':
            burn(game, c, rid)
        elif line == 'fire' and a == 'brazier' and m.tile(*c) == D.BOWLOUT:
            light(game, c, rid)
        elif line == 'fire' and a == 'oil':
            fuse(game, c)


def burn(game, c, rid):
    m = game.map
    m.set(c[0], c[1], D.FLOOR)
    m.things.pop(c, None)
    game.msg('It burns away to ash.')
    _fire(game, 'burnt', rid, c)


# ------------------------------------------------------------------ 40: the lure
@act('lure')
def a_lure(game, x, y, rid, st):
    """Strike it, and those who guard this place go to see what it was; then they settle again."""
    m, p = game.map, game.player
    n = 0
    for o in m.mons:
        if o.is_npc or max(abs(o.x - x), abs(o.y - y)) > 24:
            continue
        o.lured = [x, y, 14]
        o.awake = True
        n += 1
    game.msg('The gong booms through the halls.' + (' Feet shuffle, coming to see.' if n else ''))
    return 1


def lured(game, mon):
    """A creature that heard the lure walks to it, unless it sees you close by. Returns True when it did."""
    lu = getattr(mon, 'lured', None)
    if not lu:
        return False
    p = game.player
    if game.visible(mon.x, mon.y) and max(abs(mon.x - p.x), abs(mon.y - p.y)) <= 2:
        mon.lured = None
        return False
    lu[2] -= 1
    m = game.map
    if lu[2] <= 0 or max(abs(mon.x - lu[0]), abs(mon.y - lu[1])) <= 1:
        mon.lured = None
        mon.awake = False                        # it looks about, and settles there
        return True
    best = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            n = (mon.x + dx, mon.y + dy)
            if (dx or dy) and D.TILES[m.tile(*n)].walk and not game.occupied(m, *n) and n != (p.x, p.y):
                d = max(abs(n[0] - lu[0]), abs(n[1] - lu[1]))
                if best is None or d < best[0]:
                    best = (d, n)
    if best:
        mon.x, mon.y = best[1]
    return True


# ------------------------------------------------------------------ 41: the key a creature carries
@act('guarded')
def a_guarded(game, x, y, rid, st):
    """A keyhole whose key one of the place's creatures carries."""
    return a_keyhole(game, x, y, rid, st)


def give_key(game, m, c, lvl):
    """The keyhole's key goes to the strongest creature on the level away from the hole (it drops it when it falls)."""
    from .entities import Item
    key = Item(game.new_id(), 'vkey', 'k5', 1)
    key.name, key.door = 'Worn Bronze Key', (m.key, ('hole', c[0], c[1]))
    mons = [o for o in m.mons if not o.is_npc and max(abs(o.x - c[0]), abs(o.y - c[1])) > 8]
    if not mons:
        key.x, key.y = c[0], c[1]
        hide_key(game, m, c, lvl)
        return
    o = max(mons, key=lambda o: (o.maxhp, o.lvl))
    o.carries = key


# ------------------------------------------------------------------ 42: three shards of a seal
SHARDS = 3


def seal_of(m):
    return getattr(m, 'seal_id', None) or m.key


@act('shard')
def a_shard(game, x, y, rid, st):
    from .entities import Item
    m, p = game.map, game.player
    it = Item(game.new_id(), 'trophy', 'shard')
    it.name, it.worth, it.seal = 'Shard of a Seal', 1, seal_of(m)
    p.inv.append(it)
    _set(m, (x, y), D.PLINTH)
    have = sum(1 for i in p.inv if i.t == 'shard' and getattr(i, 'seal', None) == it.seal)
    game.msg(f'You lift a shard of violet stone from the plinth. It is warm. ({have} of {SHARDS})', 'good')
    return 1


@act('seal')
def a_seal(game, x, y, rid, st):
    m, p = game.map, game.player
    mine = [i for i in p.inv if i.t == 'shard' and getattr(i, 'seal', None) == seal_of(m)]
    if len(mine) < SHARDS:
        game.msg(f'A door sealed with a disc of violet stone, broken in {SHARDS}. The shards are gone; '
                 f'you carry {len(mine)} of them.')
        return 0
    for i in mine[:SHARDS]:
        p.inv.remove(i)
    _set(m, (x, y), D.FLOOR)
    game.msg('You fit the shards into the seal. It flares, and the door is simply gone.', 'good')
    _fire(game, 'unlock', rid, (x, y))
    return 1


# ------------------------------------------------------------------ 44: the moon shaft (and the tide in IFs)
@act('moonshaft')
def a_moonshaft(game, x, y, rid, st):
    from .towns import is_night
    game.msg('Moonlight falls in through a shaft in the stone.' if is_night(game) else
             'A narrow shaft in the stone. By day only grey light comes down it.')
    return 0


# ------------------------------------------------------------------ the rest of each turn
def tick_more(game):
    m = game.map
    if getattr(m, 'pending', None):
        for when, rid, c in m.pending:
            _fire(game, when, rid, c)
        m.pending = []
    things = m.things
    acts = {a for a, _r in things.values()}
    if 'stalker' in acts:
        stalkers(game)
    if 'vent' in acts:
        winds(game)
    if 'shift' in acts:
        shifts(game)
    for c, n in list(getattr(m, 'fuses', {}).items()):
        if n <= 1:
            del m.fuses[c]
            blow(game, c)
        else:
            m.fuses[c] = n - 1
    if acts & {'burnable', 'oil'}:
        for c, (a, rid) in list(things.items()):
            if a in ('burnable', 'oil') and any(m.tile(c[0] + dx, c[1] + dy) == D.BURNING
                                                for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                if a == 'burnable':
                    burn(game, c, rid)
                else:
                    fuse(game, c)


# ------------------------------------------------------------------ the thens of the puzzles (themes._then)
def then(game, verb, arg, rid):
    """Returns True when the verb was one of the puzzles'."""
    m = game.map
    if verb == 'arrows':
        arrows(game, rid, arg)
    elif verb == 'raise':
        flip_crystals(game, rid, arg if arg in ('red', 'blue') else None)
    elif verb == 'water':
        water(game, rid, arg)
    elif verb == 'become':
        mark, _, name = arg.partition(':')
        from .pieces import tile_named
        t = tile_named(name)
        if t is not None:
            for c, ch in getattr(m, 'marks', {}).items():
                if ch == mark and _rid(m, c) == rid and not game.occupied(m, *c):
                    m.set(c[0], c[1], t)
    else:
        return False
    return True


# ------------------------------------------------------------------ each turn
def tick(game):
    m, p = game.map, game.player
    things = getattr(m, 'things', {})
    st_of = {}
    mimics(game)
    for c, (a, rid) in list(things.items()):
        t = m.tile(*c)
        if a == 'pressure':
            down = _plate_load(game, m, c)
            if down and t == D.PLATE:
                m.set(c[0], c[1], D.PLATEDOWN)
                _fire(game, 'press', rid, c)
            elif not down and t == D.PLATEDOWN:
                m.set(c[0], c[1], D.PLATE)
                _fire(game, 'release', rid, c)
        elif a == 'spikes':
            up = (game.turn + c[0] + c[1]) % 3 == 0
            m.set(c[0], c[1], D.SPIKESUP if up else D.SPIKEHOLES)
            if up:
                for o in list(m.mons):
                    if (o.x, o.y) == c:
                        o.hp -= 6
                        if o.hp <= 0:
                            game.kill(o)
                if (p.x, p.y) == c:
                    a_spikes(game, c[0], c[1], rid, None)
        elif a == 'brazier' and t == D.BOWLOUT:
            if any(m.tile(c[0] + dx, c[1] + dy) == D.BURNING for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                light(game, c, rid)
        elif a == 'crystal':
            hit = any(m.tile(c[0] + dx, c[1] + dy) in SPELLS for dx in (-1, 0, 1) for dy in (-1, 0, 1))
            key = st_of.setdefault(rid, _state(m, rid))
            was = key.setdefault('struck', {})
            k = f'{c[0]},{c[1]}'
            if hit and not was.get(k):
                game.msg('A spell strikes the crystal. It rings, and changes colour.')
                flip_crystals(game, rid)
            was[k] = hit
    prev = getattr(m, '_ppos', None)                 # the crumbling floor gives way behind you
    if prev and prev != (p.x, p.y) and m.tile(*prev) == D.CRUMBLE:
        m.set(prev[0], prev[1], D.CHASM)
        m.things.pop(prev, None)
        game.msg('Behind you the floor falls away into the dark.')
    if getattr(m, '_ported', None) and m._ported != (p.x, p.y):
        m._ported = None
    for c, t in list(getattr(m, 'to_rise', {}).items()):
        if not game.occupied(m, *c) and (p.x, p.y) != c:
            m.set(c[0], c[1], t)
            del m.to_rise[c]
    if any(a in ('shaft', 'moonshaft') for a, _r in things.values()):
        beam(game)
    tick_more(game)
    m._ppos = (p.x, p.y)


SPELLS = {D.BURNING, D.SPELLICE, D.BALL, D.ICEWALL}


def setup(game, m, lvl):
    """What the puzzle things need once the level is made: the keyhole's key, the crystals' first colour, the
    sunbeams."""
    for c, (a, rid) in list(getattr(m, 'things', {}).items()):
        if a == 'keyhole':
            hide_key(game, m, c, lvl)
        elif a == 'guarded':
            give_key(game, m, c, lvl)
        elif a in ('block', 'oil', 'mimic', 'mimicx', 'stalker'):
            m.__dict__.setdefault('things0', {})[c] = a
            m.__dict__.setdefault('blocks_on', {})[c] = True
            m.__dict__.setdefault('under', {})[c] = D.FLOOR
        elif a == 'crystal' and 'colour' not in _state(m, rid):
            _state(m, rid)['colour'] = 'red'
    beam(game, m)
    for c in m.__dict__.pop('_solved_shafts', []):          # turned and mirrored, a room may come out solved:
        mc = m.__dict__.get('_first_mirror', {}).get(c)     # its first mirror is turned the other way
        if mc:
            m.set(mc[0], mc[1], D.SWIVEL2 if m.tile(*mc) == D.SWIVEL else D.SWIVEL)
    m.__dict__.pop('_first_mirror', None)
    beam(game, m)
    m.__dict__.pop('_solved_shafts', None)
    m.__dict__.pop('_first_mirror', None)
    land_falls(game, m, m.key)                               # a block that fell through a hole before this was made


def reset(game, rid, after=False):
    """then=reset in a puzzle room: the blocks lifted off where they were pushed (before the room is laid again as
    drawn), then set where they were drawn, the crystals red, the bells unrung, the disc dark (after)."""
    m = game.map
    inside = _room_cells(m, rid)
    on = m.__dict__.setdefault('blocks_on', {})
    under = m.__dict__.setdefault('under', {})
    if not after:
        held = m.__dict__.setdefault('under_thing', {})
        for c in [c for c in on if c in inside]:
            m.set(c[0], c[1], under.pop(c, D.FLOOR))
            on.pop(c, None)
            m.things.pop(c, None)
            if c in held:
                m.things[c] = held.pop(c)
        for c in [c for c in getattr(m, 'to_rise', {}) if c in inside]:
            del m.to_rise[c]
        return
    for c, t in getattr(m, 'laid', {}).items():
        if c in inside and t in MOVERS and m.tile(*c) == t:
            on[c], under[c] = True, D.FLOOR
            m.things[c] = (m.__dict__.get('things0', {}).get(c, MOVERS[t]), rid)
    st = _state(m, rid)
    for k in ('sunlit', 'rung', 'struck', 'solved'):
        st.pop(k, None)
    if 'colour' in st:
        st['colour'] = 'red'
    if 'water0' in st:
        water(game, rid, 'up')
    beam(game)


# ------------------------------------------------------------------ helpers
def _state(m, rid):
    from .themes import state
    return state(m, rid)


def _rid(m, c):
    from .themes import room_at
    return room_at(m, *c)


def _ring(m, rid):
    cells = _room_cells(m, rid)
    return {(x + dx, y + dy) for x, y in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))} - cells
