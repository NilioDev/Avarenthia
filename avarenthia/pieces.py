"""Hand-drawn pieces (approved 22 October 2026, the way of Dungeon Crawl Stone Soup's vaults): small ASCII maps in the
data files of `pieces/` (one piece after another, see `pieces/README.txt` for the format), with substitutions for
variety, tags (the part of a place, the kinds it suits), mood lines, telling things and events (when, if, then).

The game reads the drawn files straight from `pieces/` when it runs from the source. A build carries them packed
into one file, `assets/pieces.pack`, sealed with a checksum that lives in the code (`pieces_seal.py`, written by
`tools/pack_pieces.py` in CI); a pack that was changed afterwards is ignored.

A piece once read: name, part, kinds, depth, weight, moods, the map rows, the substitutions, the things
({mark: (tile, action)}) and the events. `drawn(piece)` makes one drawing of it: substitutions picked, turned and
mirrored at random; it returns {(x, y): glyph} for the cells inside the piece, and where its entrance is."""
import hashlib
import json
import os
import random
import sys
import zlib

from . import data as D
from . import owntiles as OT

PARTS = ('entrance', 'arrival', 'middle', 'bottom')
# the glyphs every piece may use; the uppercase letters are the piece's own telling things (THING lines)
LEGEND = {
    '.': D.FLOOR, '#': D.WALL, '~': D.WATER, ',': D.SHALLOW, 'v': D.CHASM, 'L': D.LAVA, 's': D.STATUE, 'b': D.BARREL,
    't': D.TABLE, 'c': D.CHEST, 'r': D.RUBBLE, 'g': D.GRAVE, 'm': D.SHROOM, '=': D.BRIDGE, 'k': D.SHELVES,
    'h': D.HEARTH, 'a': D.ANVIL, 'w': D.WELL, 'f': D.FOUNTAIN, 'e': D.EGGS, 'j': D.BARS, 'y': D.RACK, 'o': D.BONEWALL,
    'u': D.ROOTS, 'x': D.WEB, 'p': D.BED, 'n': D.SECRET, '"': D.GRASS, 'i': D.ICEWALL, '%': D.REMAINS, '_': D.ALTAR,
    '*': D.GLITTER, 'q': D.CAGE,
}
# what a THING line may name, besides the legend: the theme rooms' own tiles
TILE_NAMES = {
    'altar': D.ALTAR, 'statue': D.STATUE, 'shelves': D.SHELVES, 'fountain': D.FOUNTAIN, 'anvil': D.ANVIL,
    'hearth': D.HEARTH, 'well': D.WELL, 'barrel': D.BARREL, 'chest': D.CHEST, 'mushrooms': D.SHROOM, 'eggs': D.EGGS,
    'rack': D.RACK, 'cage': D.CAGE, 'rubble': D.RUBBLE, 'chasm': D.CHASM, 'grave': D.GRAVE, 'secret': D.SECRET,
    'vault door': D.VAULTDOOR, 'plinth': D.PLINTH, 'mirror': D.MIRROR, 'gong': D.GONG, 'lever': D.LEVER,
    'dummy': D.DUMMY, 'circle': D.CIRCLE, 'ward': D.WARD, 'bier': D.BIER, 'remains': D.REMAINS, 'dice': D.DICE,
    'gears': D.GEARS, 'bars': D.BARS, 'map': D.MAPTABLE, 'web': D.WEB, 'arch': D.ARCH, 'alchemy': D.ALCHEMY,
    'floor': D.FLOOR, 'roots': D.ROOTS, 'water': D.WATER, 'shallow': D.SHALLOW, 'fire': D.LAVA, 'table': D.TABLE,
    'bones': D.BONEWALL, 'hallowed': D.HALLOWED, 'grass': D.GRASS,
}
GATES = ('door', 'open', 'secret', 'vault')
WHEN = ('enter', 'step', 'bump', 'take', 'clear', 'night',
        'press', 'release', 'lit', 'sun', 'hit', 'break', 'solved', 'unlock',      # the last ones: puzzles.py
        'moon', 'charged', 'burnt')
# whens with a name: a switch comes to a state, a counter comes to a number (the editor's switches and counters)
WHEN_NAMED = ('switch', 'count', 'order')      # order:ABC  bells struck in this order
LISTS = {}                       # the lists of creatures every piece may use (LIST lines before the first NAME)
HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(os.path.dirname(HERE), 'pieces')


class Piece:
    __slots__ = ('name', 'part', 'kinds', 'depth', 'weight', 'moods', 'rows', 'subst', 'things', 'events', 'shape',
                 'gate', 'file', 'spots', 'lists', 'more', 'switches', 'counters', 'dress', 'doors')

    def __init__(self, name):
        self.name, self.part, self.kinds, self.depth, self.weight = name, 'middle', ['any'], 0, 10
        self.moods, self.rows, self.subst, self.things, self.events = [], [], {}, {}, []
        self.shape, self.gate, self.file = '', 'door', ''
        self.spots = {}          # (x, y) -> a creature key, '?' (one of the place) or 'list:<name>'
        self.lists = {}          # name -> [(creature key, weight)]
        self.more = None         # (what, least, most): extra creatures where there is room
        self.switches = {}       # name -> [states], the first is how it starts
        self.counters = {}       # name -> start
        self.dress = []          # [(set, how full 1-5)]: dressed anew in every world
        self.doors = ''          # DOORS: how many ways in the game opens ('1', '1-2', '2-3', 'all'); '' = each +

    def door_count(self):
        """(least, most) doors the game opens, counting every + (which always opens)."""
        plus = sum(row.count('+') for row in self.rows)
        maybe = sum(row.count("'") for row in self.rows)
        if not self.doors:
            n = max(1, plus)
            return n, n
        if self.doors == 'all':
            return plus + maybe, plus + maybe
        lo, _, hi = self.doors.partition('-')
        return int(lo), int(hi or lo)

    def list_of(self, name):
        return self.lists.get(name) or LISTS.get(name)

    def suits(self, tag, depth):
        if depth < self.depth:
            return False
        if any(k == f'not:{tag}' for k in self.kinds):
            return False
        return 'any' in self.kinds or tag in self.kinds


class Bad(ValueError):
    pass


OT.Bad = Bad


def _event(text, where):
    """when=bump at=A if=night,chance:50 then=msg:"..." then=wake: one rule of a piece."""
    ev = {'when': None, 'at': None, 'if': [], 'then': [], 'again': False}
    rest = text.strip()
    while rest:
        if '=' not in rest:
            raise Bad(f'{where}: cannot read "{rest}"')
        k, rest = rest.split('=', 1)
        k = k.strip()
        if rest.startswith('"') or ':"' in rest.split(' ', 1)[0]:
            q = rest.index('"')
            end = rest.index('"', q + 1)
            v, rest = rest[:end + 1], rest[end + 1:].strip()
        else:
            v, _, rest = rest.partition(' ')
            rest = rest.strip()
        if k == 'when':
            if v not in WHEN and v.split(':')[0] not in WHEN_NAMED:
                raise Bad(f'{where}: no such "when": {v}')
            ev['when'] = v
        elif k == 'at':
            ev['at'] = v
        elif k == 'if':
            ev['if'] += [c for c in v.split(',') if c]
        elif k == 'then':
            ev['then'].append(v)
        elif k == 'again':
            ev['again'] = v in ('yes', 'true', '1')
        else:
            raise Bad(f'{where}: no such word: {k}')
    if not ev['when'] or not ev['then']:
        raise Bad(f'{where}: an event needs a when and a then')
    return ev


def parse(text, file='', checked=True):
    """Read the pieces in one file. Raises Bad with the line when something is wrong. checked=False leaves out the
    check of each map (the editor reads a piece still being drawn and lists its problems itself)."""
    out, cur, in_map, own, place = [], None, False, None, False
    for n, line in enumerate(text.split('\n'), 1):
        where = f'{file}:{n}'
        line = line.rstrip('\r')
        if place:                               # a whole place (drawnplaces.py reads it), up to ENDPLACE
            place = line.strip() != 'ENDPLACE'
            continue
        if not in_map and line.strip().upper().startswith('PLACE:'):
            place, cur = True, None
            continue
        if own is not None:                     # an own tile or thing (owntiles.py), up to END
            if line.strip() == 'END':
                o = OT.read(own[0], own[1], own[2], own[3])
                o.file = file
                OT.register(o)
                own = None
            elif line.strip() and not line.strip().startswith(';'):
                own[2].append(line.strip())
            continue
        if in_map:
            if line.strip() == 'ENDMAP':
                in_map = False
                continue
            cur.rows.append(line.rstrip())
            continue
        st = line.strip()
        if not st or st.startswith(';'):
            continue
        if st == 'MAP':
            if cur is None:
                raise Bad(f'{where}: MAP before NAME')
            in_map = True
            continue
        if ':' not in st:
            raise Bad(f'{where}: cannot read "{st}"')
        key, val = st.split(':', 1)
        key, val = key.strip().upper(), val.strip()
        if key in ('TILE', 'OBJECT'):
            own, cur = (key, val, [], where), None
            continue
        if key == 'NAME':
            cur = Piece(val)
            cur.file = file
            out.append(cur)
            continue
        if cur is None and key == 'LIST':
            name, opts = _list(val, where)
            LISTS[name] = opts
            continue
        if cur is None:
            raise Bad(f'{where}: {key} before NAME')
        if key == 'PART':
            if val not in PARTS:
                raise Bad(f'{where}: no such part: {val}')
            cur.part = val
        elif key == 'KIND':
            cur.kinds = val.split()
        elif key == 'DEPTH':
            cur.depth = int(val)
        elif key == 'WEIGHT':
            cur.weight = int(val)
        elif key == 'SHAPE':
            cur.shape = val
        elif key == 'GATE':
            if val not in GATES:
                raise Bad(f'{where}: no such gate: {val}')
            cur.gate = val
        elif key == 'MOOD':
            cur.moods.append(val)
        elif key == 'SUBST':                    # SUBST: p = t:2 .:1
            g, opts = val.split('=', 1)
            g = g.strip()
            choice = []
            for o in opts.split():
                ch, _, w = o.rpartition(':') if ':' in o[1:] else (o, '', '1')
                ch = ch or o
                choice.append((' ' if ch == 'none' else ch, int(w or 1)))
            cur.subst[g] = choice
        elif key == 'THING':                    # THING: A = altar do:shrine
            g, rest = val.split('=', 1)
            words = rest.split()
            act = next((w[3:] for w in words if w.startswith('do:')), None)
            name = ' '.join(w for w in words if not w.startswith('do:'))
            tile = tile_named(name)
            if tile is None:
                raise Bad(f'{where}: no such thing: {name}')
            cur.things[g.strip()] = (tile, act)
        elif key == 'EVENT':
            cur.events.append(_event(val, where))
        elif key == 'CREATURE':                 # CREATURE: skeleton at 4,2   (or ? or list:<name>)
            what, _, at = val.rpartition(' at ')
            try:
                x, y = (int(v) for v in at.split(','))
            except ValueError:
                raise Bad(f'{where}: write a creature as "skeleton at 4,2"')
            cur.spots[(x, y)] = what.strip()
        elif key == 'LIST':                     # LIST: war band = orc:6 orc_shaman:1
            name, opts = _list(val, where)
            cur.lists[name] = opts
        elif key == 'MORE':                     # MORE: list:war band 0-2
            what, _, span = val.rpartition(' ')
            try:
                lo, hi = (int(v) for v in span.split('-'))
            except ValueError:
                raise Bad(f'{where}: write MORE as "? 0-2" or "list:war band 1-3"')
            cur.more = (what.strip(), lo, hi)
        elif key == 'SWITCH':                   # SWITCH: gate = shut open
            name, _, states = val.partition('=')
            cur.switches[name.strip()] = states.split() or ['off', 'on']
        elif key == 'COUNTER':                  # COUNTER: plates 0
            name, _, start = val.rpartition(' ')
            if not name:
                name, start = start, '0'
            try:
                cur.counters[name.strip()] = int(start)
            except ValueError:
                cur.counters[val.strip()] = 0
        elif key == 'DOORS':                    # DOORS: 1-2   (how many of the ways in the game opens)
            if val != 'all' and not all(v.isdigit() for v in val.split('-')):
                raise Bad(f'{where}: DOORS is 1, 1-2, 2-3 or all')
            cur.doors = val
        elif key == 'DRESS':                    # DRESS: hall 3
            name, _, full = val.rpartition(' ')
            try:
                cur.dress.append((name.strip(), int(full)))
            except ValueError:
                cur.dress.append((val.strip(), 3))
        else:
            raise Bad(f'{where}: no such word: {key}')
    if checked:
        for p in out:
            check(p)
    return out


def _list(val, where):
    name, _, opts = val.partition('=')
    out = []
    for o in opts.split():
        k, _, w = o.rpartition(':')
        try:
            out.append((k or o, int(w) if k else 1))
        except ValueError:
            raise Bad(f'{where}: write a list as "war band = orc:6 ogre:1"')
    return name.strip(), out


def tile_named(name):
    """The tile a THING line names: one of TILE_NAMES, or any tile of the game by its own name (the editor's More)."""
    if name in TILE_NAMES:
        return TILE_NAMES[name]
    return next((i for i, t in enumerate(D.TILES) if t.name == name), None)


def problems(p):
    """Everything wrong with a piece, in plain words: [(message, [cells])], cells (x, y) in the drawing. The editor
    shows them all; check() raises the first."""
    out = []
    if not p.rows:
        return [('no MAP', [])]
    plus = [(x, y) for y, row in enumerate(p.rows) for x, ch in enumerate(row) if ch == '+']
    maybe = [(x, y) for y, row in enumerate(p.rows) for x, ch in enumerate(row) if ch == "'"]
    gates = plus + maybe

    def inside(x, y):
        return 0 <= y < len(p.rows) and 0 <= x < len(p.rows[y]) and p.rows[y][x] not in " +#'"
    if not gates:
        out.append(("a piece needs a way in: a + (always used) or a ' (a door the game may use)", []))
    if not maybe and not p.doors and len(plus) > 1:
        out.append((f'a piece has one + (its way in), it has {len(plus)}: more ways in are drawn as \' with DOORS',
                    plus))
    for g in gates:
        gx, gy = g
        ins = [(dx, dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if inside(gx + dx, gy + dy)]
        if len(ins) != 1:
            out.append(('a way in must have the room on one side only', [g]))
            continue
        dx, dy = ins[0]
        side = (dy, dx)
        for k in (-2, -1, 1, 2):
            if not inside(gx + dx + k * side[0], gy + dy + k * side[1]) or inside(gx + k * side[0], gy + k * side[1]):
                out.append(('a way in must sit in a straight wall, two cells of room on each side of it', [g]))
                break
    if gates:
        try:
            lo, hi = p.door_count()
        except ValueError:
            lo, hi = 1, 1
        if len(plus) > hi:
            out.append((f'DOORS lets the game open {hi}, but {len(plus)} + always open', plus))
        if hi >= 2 and len(gates) >= 2:
            out += _through(p, gates)
    bad = [(x, y) for y, row in enumerate(p.rows) for x, ch in enumerate(row)
           if not (ch in " +<>'" or ch in LEGEND or ch in p.things or ch in p.subst)]
    for x, y in bad:
        out.append((f'unknown glyph {p.rows[y][x]!r} in row {y + 1}', [(x, y)]))
    for opts in p.subst.values():
        for ch, _w in opts:
            if ch not in LEGEND and ch not in p.things and ch != ' ':
                out.append((f'unknown glyph {ch!r} in a SUBST', []))
    floor = {(x, y) for y, row in enumerate(p.rows) for x, ch in enumerate(row) if ch not in " +#'"}
    for x, y in sorted(floor, key=lambda c: (c[1], c[0])):
        for dx, dy in ((1, 0), (0, 1)):
            if (x + dx, y + dy) not in floor and (x + 2 * dx, y + 2 * dy) not in floor and (x + 3 * dx, y + 3 * dy) in floor:
                out.append((f'two walls side by side at row {y + 1}, column {x + 1}: make it one or three',
                            [(x + dx, y + dy), (x + 2 * dx, y + 2 * dy)]))
    marks = {e['at'] for e in p.events if e['at']}
    for m in sorted(marks):
        if not any(m in row for row in p.rows) and m not in p.things:
            out.append((f'an event is at {m}, which the map does not have', []))
    for (x, y), what in sorted(p.spots.items()):
        if (x, y) not in floor:
            out.append((f'a creature stands in the rock at row {y + 1}, column {x + 1}', [(x, y)]))
        if what != '?' and not (what.startswith('list:') and p.list_of(what[5:])) and what not in D.MONSTERS:
            out.append((f'no such creature or list: {what}', [(x, y)]))
    for name, opts in p.lists.items():
        for k, _w in opts:
            if k not in D.MONSTERS:
                out.append((f'the list {name} has a creature the game does not know: {k}', []))
    if p.more and p.more[0] != '?' and not (p.more[0].startswith('list:') and p.list_of(p.more[0][5:])) \
            and p.more[0] not in D.MONSTERS:
        out.append((f'no such creature or list: {p.more[0]}', []))
    from . import dressing as DR
    for name, _n in p.dress:
        if name not in DR.SETS:
            out.append((f'no such set to dress the room with: {name}', []))
    for e in p.events:
        words = [e['when']] + e['if'] + list(e['then'])
        words += [t.split(':', 2)[2] for t in e['then'] if t.startswith('after:') and t.count(':') >= 2]
        for word in words:
            verb, _, rest = word.partition(':')
            if verb in ('switch', 'set', 'flip') and rest.split(':')[0] not in p.switches:
                out.append((f'an event uses the switch "{rest.split(":")[0]}", which the piece does not have', []))
            if verb in ('switch', 'set') and rest.count(':') and rest.split(':')[0] in p.switches \
                    and rest.split(':')[1] not in p.switches[rest.split(':')[0]]:
                out.append((f'the switch "{rest.split(":")[0]}" has no state "{rest.split(":")[1]}"', []))
            if verb in ('count', 'add', 'sub') and rest.split(':')[0] not in p.counters:
                out.append((f'an event uses the counter "{rest.split(":")[0]}", which the piece does not have', []))
    return out


SHUTS = ('open', 'shut', 'cavein', 'flood')


def _through(p, gates):
    """With two doors or more a room can be a way through: the way from door to door may not hang on anything that
    can shut (bars, rubble, a mark an event opens or shuts)."""
    worked = {t.split(':')[1] for e in p.events for t in e['then'] + [x.split(':', 2)[2] for x in e['then']
              if x.startswith('after:') and x.count(':') >= 2] if t.split(':')[0] in SHUTS and ':' in t}
    can = set()
    for y, row in enumerate(p.rows):
        for x, ch in enumerate(row):
            if ch in " #":
                continue
            if ch in worked:
                continue
            if ch in "+'" or _walks(ch, p) or ch in p.subst:
                can.add((x, y))
    seen, todo = {gates[0]}, [gates[0]]
    while todo:
        x, y = todo.pop()
        for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if n in can and n not in seen:
                seen.add(n)
                todo.append(n)
    cut = [g for g in gates if g not in seen]
    if cut:
        return [('with two doors or more the room can be a way through: the way from door to door may not pass '
                 'what can shut (bars, rubble, a mark an event works); set DOORS to 1', cut)]
    return []


def check(p):
    """A piece must have a map with exactly one way in on its edge, and use only known glyphs."""
    bad = problems(p)
    if bad:
        raise Bad(f'{p.file}: {p.name}: {bad[0][0]}')


class Drawing(dict):
    """One drawing of a piece: {(x, y): sign}, with .spots {(x, y): creature} turned along with it."""

    def __init__(self, *a):
        super().__init__(*a)
        self.spots = {}
        self.doors = []           # the other doors this time: [(cell, step out)]; K5 joins them to the level


def drawn(p):
    """One drawing of a piece: substitutions picked, turned and mirrored. Returns (cells, gate, out): cells
    {(x, y): glyph} for what lies inside the piece, gate the cell of its way in, out the step from it into the rock."""
    cells = {}
    for y, row in enumerate(p.rows):
        for x, ch in enumerate(row):
            if ch == ' ':
                continue
            if ch in p.subst:
                opts = p.subst[ch]
                ch = random.choices([o[0] for o in opts], [o[1] for o in opts])[0]
                if ch == ' ':
                    continue
            cells[(x, y)] = ch
    k, flip = random.randint(0, 3), random.random() < .5
    if any(a == 'mimicx' for _t, a in p.things.values()):
        k = random.choice((0, 2))           # a mirror statue mirrors left and right: keep the room's axes

    def turn(x, y):
        if flip:
            x = -x
        for _ in range(k):
            x, y = -y, x
        return x, y
    out = {turn(x, y): ch for (x, y), ch in cells.items()}
    mx, my = min(c[0] for c in out), min(c[1] for c in out)
    out = Drawing({(x - mx, y - my): ch for (x, y), ch in out.items()})
    for c, what in p.spots.items():
        tx, ty = turn(*c)
        out.spots[(tx - mx, ty - my)] = what
    plus = [c for c, ch in out.items() if ch == '+']
    maybe = [c for c, ch in out.items() if ch == "'"]
    chosen = plus
    if maybe:                                   # doors the game may use (DOORS): some this time, the rest wall
        lo, hi = p.door_count()
        n = max(len(plus), min(len(plus) + len(maybe), random.randint(lo, hi)), 1)
        random.shuffle(maybe)
        chosen = plus + maybe[:n - len(plus)]
        for c in maybe[n - len(plus):]:
            out[c] = '#'
        random.shuffle(chosen)
        for c in chosen:
            out[c] = '+'

    def out_step(g):
        return next(((-dx, -dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                     if out.get((g[0] + dx, g[1] + dy), '#') not in '#+'), (0, 1))
    gate = chosen[0]
    step = out_step(gate)
    out.doors = [(g, out_step(g)) for g in chosen[1:]]
    if p.dress:
        dress_drawing(p, out, gate)
    return out, gate, step


DRESSED = 0x100000          # a dressed thing rides in a drawing as chr(DRESSED + its tile)


def dressed_tile(ch):
    """The tile of a dressed thing's sign in a drawing, or None."""
    return ord(ch) - DRESSED if len(ch) == 1 and ord(ch) >= DRESSED else None


def dress_drawing(p, out, gate, rng=None):
    """Dress a drawing by the piece's DRESS lines (dressing.py): the things laid ride in it as signs of their own."""
    from . import dressing as DR
    walk = {c for c, ch in out.items() if ch not in '#+' and _walks(ch, p)}
    free = {c for c, ch in out.items() if ch == '.'}
    wall = {(x + dx, y + dy) for x, y in out for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
            if out.get((x + dx, y + dy), '#') == '#'}
    start = next((c for c in ((gate[0] + dx, gate[1] + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                  if c in walk), None)
    if start is None:
        return []
    marks = {e['at'] for e in p.events if e['at']}
    keep = {c for c, ch in out.items() if ch in p.things or ch in '<>' or ch in marks} | set(out.spots)
    keep |= {(x + dx, y + dy) for (x, y), ch in out.items() if ch == '+'
             for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if (x + dx, y + dy) in walk}
    laid = DR.dress(free, walk, wall, start, p.dress, rng or random, keep)
    for c, name in laid:
        out[c] = chr(DRESSED + DR.tile(name))
    return laid


def _walks(ch, p):
    if ch in p.things:
        return D.TILES[p.things[ch][0]].walk
    t = LEGEND.get(ch)
    return t is None or D.TILES[t].walk


# ------------------------------------------------------------------ the pack and its seal
PLACES = os.path.join(os.path.dirname(HERE), 'places')     # the whole places (drawnplaces.py)


def _source_texts():
    texts = {}
    for d, pre in ((SOURCE, ''), (PLACES, 'places/')):
        if os.path.isdir(d):
            for f in sorted(os.listdir(d)):
                if f.endswith('.des'):
                    with open(os.path.join(d, f), encoding='utf-8') as fh:
                        texts[pre + f] = fh.read()
    return texts


_TEXTS = None


def texts(force=False):
    """The text of every drawn file, pieces and places: from the source, else from the sealed pack."""
    global _TEXTS
    if _TEXTS is not None and not force:
        return _TEXTS
    t = None
    if not getattr(sys, 'frozen', False):
        t = _source_texts() or None
    if t is None:
        try:
            from .pieces_seal import SEAL
        except ImportError:
            SEAL = None
        try:
            with open(_pack_path(), 'rb') as fh:
                t = unpack(fh.read(), SEAL)
        except OSError:
            t = None
    _TEXTS = t or {}
    return _TEXTS


def pack(texts):
    """The bytes of a pack, and its seal."""
    raw = zlib.compress(json.dumps(texts, sort_keys=True, ensure_ascii=False).encode('utf-8'), 9)
    return raw, hashlib.sha256(raw).hexdigest()


def unpack(raw, seal):
    """The files in a pack, or None when it does not match its seal (changed after the build)."""
    if not seal or hashlib.sha256(raw).hexdigest() != seal:
        return None
    return json.loads(zlib.decompress(raw).decode('utf-8'))


def _pack_path():
    base = getattr(sys, '_MEIPASS', os.path.dirname(HERE))
    return os.path.join(base, 'assets', 'pieces.pack')


_ALL = None


def load(force=False):
    """All pieces: from the drawn files when running from the source, else from the sealed pack."""
    global _ALL
    if _ALL is not None and not force:
        return _ALL
    all_texts = texts(force=force)
    out = []
    for f, t in sorted(all_texts.items()):        # the own tiles and things first: any piece may use them
        for o in own_blocks(t, f):
            OT.register(o)
    for f, t in sorted(all_texts.items()):
        out += parse(t, f)
    _ALL = out
    return out


def own_blocks(text, file=''):
    """The own tiles and things (TILE / OBJECT blocks) of one file, read but not made."""
    out, own = [], None
    for n, line in enumerate(text.split('\n'), 1):
        st = line.strip()
        if own is not None:
            if st == 'END':
                o = OT.read(*own)
                o.file = file
                out.append(o)
                own = None
            elif st and not st.startswith(';'):
                own[2].append(st)
            continue
        if ':' in st and st.split(':', 1)[0].strip().upper() in ('TILE', 'OBJECT'):
            k, v = st.split(':', 1)
            own = (k.strip().upper(), v.strip(), [], f'{file}:{n}')
    return out


def pick(part, tag, depth, n, used=()):
    """Up to n different pieces for this part of a place, by weight."""
    tags = tag if isinstance(tag, (tuple, list)) else (tag,)
    pool = [p for p in load() if p.part == part and any(p.suits(t, depth) for t in tags if t) and p.name not in used]
    out = []
    while pool and len(out) < n:
        p = random.choices(pool, [p.weight for p in pool])[0]
        out.append(p)
        pool.remove(p)
    return out


EXTRA = {}           # the floors of the whole places, by name (drawnplaces.py): found by by_name too


def by_name(name):
    return next((p for p in load() if p.name == name), None) or EXTRA.get(name)
