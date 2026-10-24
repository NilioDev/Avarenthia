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
WHEN = ('enter', 'step', 'bump', 'take', 'clear', 'night')
HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(os.path.dirname(HERE), 'pieces')


class Piece:
    __slots__ = ('name', 'part', 'kinds', 'depth', 'weight', 'moods', 'rows', 'subst', 'things', 'events', 'shape',
                 'gate', 'file')

    def __init__(self, name):
        self.name, self.part, self.kinds, self.depth, self.weight = name, 'middle', ['any'], 0, 10
        self.moods, self.rows, self.subst, self.things, self.events = [], [], {}, {}, []
        self.shape, self.gate, self.file = '', 'door', ''

    def suits(self, tag, depth):
        if depth < self.depth:
            return False
        if any(k == f'not:{tag}' for k in self.kinds):
            return False
        return 'any' in self.kinds or tag in self.kinds


class Bad(ValueError):
    pass


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
            if v not in WHEN:
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


def parse(text, file=''):
    """Read the pieces in one file. Raises Bad with the line when something is wrong."""
    out, cur, in_map = [], None, False
    for n, line in enumerate(text.split('\n'), 1):
        where = f'{file}:{n}'
        line = line.rstrip('\r')
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
        if key == 'NAME':
            cur = Piece(val)
            cur.file = file
            out.append(cur)
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
            if name not in TILE_NAMES:
                raise Bad(f'{where}: no such thing: {name}')
            cur.things[g.strip()] = (TILE_NAMES[name], act)
        elif key == 'EVENT':
            cur.events.append(_event(val, where))
        else:
            raise Bad(f'{where}: no such word: {key}')
    for p in out:
        check(p)
    return out


def check(p):
    """A piece must have a map with exactly one way in on its edge, and use only known glyphs."""
    where = f'{p.file}: {p.name}'
    if not p.rows:
        raise Bad(f'{where}: no MAP')
    gates = [(x, y) for y, row in enumerate(p.rows) for x, ch in enumerate(row) if ch == '+']
    if len(gates) != 1:
        raise Bad(f'{where}: a piece needs exactly one + (its way in), it has {len(gates)}')
    gx, gy = gates[0]

    def inside(x, y):
        return 0 <= y < len(p.rows) and 0 <= x < len(p.rows[y]) and p.rows[y][x] not in ' +#'
    ins = [(dx, dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if inside(gx + dx, gy + dy)]
    if len(ins) != 1:
        raise Bad(f'{where}: the way in must have the room on one side only')
    dx, dy = ins[0]
    side = (dy, dx)
    for k in (-2, -1, 1, 2):
        if not inside(gx + dx + k * side[0], gy + dy + k * side[1]) or inside(gx + k * side[0], gy + k * side[1]):
            raise Bad(f'{where}: the way in must sit in a straight wall, two cells of room on each side of it')
    for y, row in enumerate(p.rows):
        for x, ch in enumerate(row):
            if ch in ' +<>' or ch in LEGEND or ch in p.things or ch in p.subst:
                continue
            raise Bad(f'{where}: unknown glyph {ch!r} in row {y + 1}')
    for opts in p.subst.values():
        for ch, _w in opts:
            if ch not in LEGEND and ch not in p.things and ch != ' ':
                raise Bad(f'{where}: unknown glyph {ch!r} in a SUBST')
    floor = {(x, y) for y, row in enumerate(p.rows) for x, ch in enumerate(row) if ch not in ' +#'}
    for x, y in floor:
        for dx, dy in ((1, 0), (0, 1)):
            if (x + dx, y + dy) not in floor and (x + 2 * dx, y + 2 * dy) not in floor and (x + 3 * dx, y + 3 * dy) in floor:
                raise Bad(f'{where}: two walls side by side at row {y + 1}, column {x + 1}: make it one or three')
    marks = {e['at'] for e in p.events if e['at']}
    for m in marks:
        if not any(m in row for row in p.rows) and m not in p.things:
            raise Bad(f'{where}: an event is at {m}, which the map does not have')


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
    out = {}
    for (x, y), ch in cells.items():
        if flip:
            x = -x
        for _ in range(k):
            x, y = -y, x
        out[(x, y)] = ch
    mx, my = min(c[0] for c in out), min(c[1] for c in out)
    out = {(x - mx, y - my): ch for (x, y), ch in out.items()}
    gate = next(c for c, ch in out.items() if ch == '+')
    step = next(((-dx, -dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                 if out.get((gate[0] + dx, gate[1] + dy), '#') not in '#+'), (0, 1))
    return out, gate, step


# ------------------------------------------------------------------ the pack and its seal
def _source_texts():
    texts = {}
    if os.path.isdir(SOURCE):
        for f in sorted(os.listdir(SOURCE)):
            if f.endswith('.des'):
                with open(os.path.join(SOURCE, f), encoding='utf-8') as fh:
                    texts[f] = fh.read()
    return texts


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
    texts = None
    if not getattr(sys, 'frozen', False):
        texts = _source_texts() or None
    if texts is None:
        try:
            from .pieces_seal import SEAL
        except ImportError:
            SEAL = None
        try:
            with open(_pack_path(), 'rb') as fh:
                texts = unpack(fh.read(), SEAL)
        except OSError:
            texts = None
    out = []
    for f, t in sorted((texts or {}).items()):
        out += parse(t, f)
    _ALL = out
    return out


def pick(part, tag, depth, n, used=()):
    """Up to n different pieces for this part of a place, by weight."""
    pool = [p for p in load() if p.part == part and p.suits(tag, depth) and p.name not in used]
    out = []
    while pool and len(out) < n:
        p = random.choices(pool, [p.weight for p in pool])[0]
        out.append(p)
        pool.remove(p)
    return out


def by_name(name):
    return next((p for p in load() if p.name == name), None)
