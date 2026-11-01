"""A piece as the editor holds it: a grid of the format's signs (rock is ' '), the piece's lines (name, part,
kinds...), its telling things {letter: (tile name, action)}, substitutions and events as the format has them.
Every change goes through Room.change(), which keeps the undo history."""
import copy
import os

from .. import data as D
from .. import pieces as P

MAX_W, MAX_H = 40, 30            # the most for a room (Nilio, 31 October 2026); bigger is a whole place
PARTS = P.PARTS
GATES = P.GATES
KINDS = ('any', 'crypt', 'dungeon', 'cave', 'den', 'mine', 'deep')
# a telling thing's tile when you pick what it does (the tile most pieces use for it)
DOES = {'shrine': 'altar', 'library': 'shelves', 'fountain': 'fountain', 'forge': 'anvil', 'cook': 'hearth',
        'alchemy': 'alchemy', 'fungus': 'mushrooms', 'larder': 'barrel', 'wishing': 'well', 'training': 'dummy',
        'maptable': 'map', 'wine': 'barrel', 'choice': 'plinth', 'armoury': 'rack', 'adventurer': 'remains',
        'circle': 'circle', 'statues': 'statue', 'bier': 'bier', 'nest': 'eggs', 'gong': 'gong', 'cell': 'bars',
        'mirror': 'mirror', 'menagerie': 'cage', 'sanctuary': 'ward', 'arch': 'arch', 'collapse': 'floor',
        'herbs': 'grass', 'gears': 'gears', 'dice': 'dice', 'plate': 'floor', 'echo': 'floor'}
WALKABLE_THINGS = {'floor', 'grass', 'shallow', 'hallowed'}
# the puzzle things (puzzles.py): (what it does, its tile); None does nothing itself, the room's events work it
PUZZLE_THINGS = [('pressure', 'pressure plate'), ('block', 'stone block'), ('lever', 'lever'),
                 ('crystal', 'red crystal switch'), (None, 'red block'), (None, 'sunk red block'), (None, 'blue block'),
                 (None, 'sunk blue block'), ('brazier', 'cold fire bowl'), ('brazier', 'fire bowl'),
                 ('swivel', 'mirror on a swivel'), ('shaft', 'shaft of daylight'), ('sundisc', 'sun disc'),
                 ('bell', 'bell'), ('cracked', 'cracked wall'), ('crumble', 'crumbling floor'), ('ice', 'slick ice'),
                 ('spikes', 'spike holes'), ('portal', 'portal stone'), ('idol', 'golden idol on a plinth'),
                 ('keyhole', 'keyhole'), ('sluice', 'sluice gate'), (None, 'arrow slit'), ('riddle', 'riddle stone'),
                 ('sarcophagus', 'sarcophagus'), ('offering', 'offering bowl'), ('scrying', 'scrying pool'),
                 ('book', 'chained book'), ('eyes', 'idol with gem eyes'), ('rope', 'rope down'),
                 ('ladder', 'ladder up'),
                 ('mimic', 'mirror statue'), ('mimicx', 'mirror statue'), ('stalker', 'pale statue'),
                 ('raft', 'raft'), ('vent', 'wind vent'), ('shift', 'shifting wall'),
                 ('shift', 'shifting wall, drawn back'), ('hole', 'hole in the floor'), ('oil', 'oil barrel'),
                 ('rune', 'rune tile'), ('lights', 'dark floor tile'), ('lights', 'lit floor tile'),
                 ('scale', 'scale pan'), ('rod', 'iron rod'), ('burnable', 'web'), ('burnable', 'roots'),
                 ('lure', 'gong'), ('guarded', 'keyhole'), ('shard', 'seal shard on a plinth'),
                 ('seal', 'sealed door'), ('moonshaft', 'shaft of moonlight')]


def tile_of(ch, things):
    """The game's tile for one sign of the drawing (None for rock and unknown signs)."""
    if ch in things:
        return P.tile_named(things[ch][0])
    if ch in "+'":
        return D.DOOR
    if ch == '<':
        return D.UP
    if ch == '>':
        return D.DOWN
    return P.LEGEND.get(ch)


class Room:
    def __init__(self, name='new room', w=13, h=11):
        self.name, self.part, self.kinds, self.depth, self.weight = name, 'middle', ['any'], 0, 10
        self.shape, self.gate, self.moods = '', 'door', []
        self.grid = [[' '] * w for _ in range(h)]
        self.things = {}                  # letter -> (tile name, action or None)
        self.subst = {}                   # digit -> [(sign, weight)]
        self.events = []                  # as pieces._event makes them
        self.spots = {}                   # (x, y) -> creature key, '?' or 'list:<name>'
        self.lists = {}                   # name -> [(creature key, weight)]
        self.more = None                  # (what, least, most)
        self.switches = {}                # name -> [states]
        self.counters = {}                # name -> start
        self.dress = []                   # [(set, fullness)]: dressed in the game
        self.doors = ''                   # DOORS: how many ways in the game opens ('' = each +)
        self.file = ''
        self.whole = False                # a floor of a whole place: drawn whole, its rows never cut at the top
        self.max_w, self.max_h = MAX_W, MAX_H
        self.persons = []                 # a floor's people: [(name, (x, y), says)]
        self.items = []                   # a floor's fixed finds: [(what, (x, y))]
        self.undo, self.redo = [], []
        self.dirty = False

    # ------------------------------------------------------------ size and cells
    @property
    def w(self):
        return len(self.grid[0]) if self.grid else 0

    @property
    def h(self):
        return len(self.grid)

    def inb(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h

    def get(self, x, y):
        return self.grid[y][x] if self.inb(x, y) else ' '

    def set(self, x, y, ch):
        if self.inb(x, y):
            self.grid[y][x] = ch

    def resize(self, w, h):
        """The drawing made w x h (at most max_w x max_h): cut on the right and bottom, or grown with rock."""
        w, h = max(3, min(self.max_w, w)), max(3, min(self.max_h, h))
        g = [[self.get(x, y) for x in range(w)] for y in range(h)]
        self.grid = g
        self.spots = {c: v for c, v in self.spots.items() if self.inb(*c)}
        self.persons = [p for p in self.persons if self.inb(*p[1])]
        self.items = [i for i in self.items if self.inb(*i[1])]
        return w, h

    def shift(self, dx, dy):
        """Everything moved by dx, dy inside the same size (what falls off is lost)."""
        g = [[' '] * self.w for _ in range(self.h)]
        for y in range(self.h):
            for x in range(self.w):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.w and 0 <= ny < self.h:
                    g[ny][nx] = self.grid[y][x]
        self.grid = g
        self.spots = {(x + dx, y + dy): v for (x, y), v in self.spots.items() if self.inb(x + dx, y + dy)}
        self.persons = [(n, (x + dx, y + dy), s) for n, (x, y), s in self.persons if self.inb(x + dx, y + dy)]
        self.items = [(n, (x + dx, y + dy)) for n, (x, y) in self.items if self.inb(x + dx, y + dy)]

    # ------------------------------------------------------------ undo
    def _state(self):
        return (copy.deepcopy(self.grid), dict(self.things), copy.deepcopy(self.subst), copy.deepcopy(self.events),
                (self.name, self.part, list(self.kinds), self.depth, self.weight, self.shape, self.gate, list(self.moods)),
                copy.deepcopy((self.spots, self.lists, self.more, self.switches, self.counters, self.dress)),
                self.doors, (list(self.persons), list(self.items)))

    def _put_state(self, st):
        self.grid, self.things, self.subst, self.events = copy.deepcopy(st[0]), dict(st[1]), copy.deepcopy(st[2]), \
            copy.deepcopy(st[3])
        (self.name, self.part, kinds, self.depth, self.weight, self.shape, self.gate, moods) = st[4]
        self.kinds, self.moods = list(kinds), list(moods)
        self.spots, self.lists, self.more, self.switches, self.counters, self.dress = copy.deepcopy(st[5])
        self.doors = st[6]
        self.persons, self.items = list(st[7][0]), list(st[7][1])

    def change(self):
        """Call before a change (one stroke, one field): the state before it goes on the undo stack."""
        self.undo.append(self._state())
        if len(self.undo) > 400:
            self.undo.pop(0)
        self.redo.clear()
        self.dirty = True

    def step_back(self):
        if not self.undo:
            return False
        self.redo.append(self._state())
        self._put_state(self.undo.pop())
        self.dirty = True
        return True

    def step_forward(self):
        if not self.redo:
            return False
        self.undo.append(self._state())
        self._put_state(self.redo.pop())
        self.dirty = True
        return True

    # ------------------------------------------------------------ telling things
    def letter_for(self, tile_name, action):
        """The letter that stands for this thing in the file: the one it already has, or the first free one.
        None when all 26 are taken."""
        for g, v in self.things.items():
            if v == (tile_name, action):
                return g
        used = set(self.things) | {e['at'] for e in self.events if e['at']}
        for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            if c not in used and c not in P.LEGEND:
                self.things[c] = (tile_name, action)
                return c
        return None

    def tidy(self):
        """Things no longer on the map and not marks of an event are forgotten."""
        on = {ch for row in self.grid for ch in row}
        marks = {e['at'] for e in self.events if e['at']}
        for g in list(self.things):
            if g not in on and g not in marks and not any(g == o[0] for opts in self.subst.values() for o in opts):
                del self.things[g]

    # ------------------------------------------------------------ to and from the format
    @classmethod
    def from_piece(cls, p):
        r = cls(p.name)
        r.part, r.kinds, r.depth, r.weight = p.part, list(p.kinds), p.depth, p.weight
        r.shape, r.gate, r.moods = p.shape, p.gate, list(p.moods)
        w = max((len(row) for row in p.rows), default=1)
        r.grid = [list(row.ljust(w)) for row in p.rows] or [[' ']]
        names = {}
        for g, (tile, act) in p.things.items():
            names[g] = (_name_of(tile), act)
        r.things = names
        r.subst = {g: list(opts) for g, opts in p.subst.items()}
        r.events = copy.deepcopy(p.events)
        r.spots, r.lists, r.more = dict(p.spots), copy.deepcopy(p.lists), p.more
        r.switches, r.counters, r.dress = copy.deepcopy(p.switches), dict(p.counters), list(p.dress)
        r.doors = p.doors
        r.file = p.file
        return r

    def rows(self):
        """The drawing as the file has it: rock at the ends of rows and empty rows at the top and bottom cut (they
        are part of the piece's size only in the editor); rock on the left is kept as drawn."""
        rows = [''.join(r).rstrip() for r in self.grid]
        while rows and not rows[-1]:
            rows.pop()
        while rows and not rows[0] and not self.whole:
            rows.pop(0)
        return rows

    def top(self):
        """How many empty rows rows() cuts at the top (the creatures' y counts from the first row written)."""
        if self.whole:
            return 0
        n = 0
        while n < self.h and not ''.join(self.grid[n]).strip():
            n += 1
        return n if n < self.h else 0

    def to_piece(self):
        """A pieces.Piece of what is drawn now (not checked)."""
        t = self.text()
        if self.whole:                    # a floor: read as a piece of its own (people and finds left out)
            head, _, rest = t.partition('\nMAP\n')
            lines = [ln for ln in head.split('\n')[1:] if not ln.startswith(('PERSON:', 'ITEM:'))]
            t = '\n'.join([f'NAME:   {self.name}'] + lines) + '\nMAP\n' + rest
        return P.parse(t, self.file or 'editor', checked=False)[0]


def _name_of(tile):
    """The name a THING line uses for a tile: the short one of TILE_NAMES when there is one."""
    for k, v in P.TILE_NAMES.items():
        if v == tile:
            return k
    return D.TILES[tile].name


def _ev_text(e):
    words = [f"when={e['when']}"]
    if e['at']:
        words.append(f"at={e['at']}")
    if e['if']:
        words.append('if=' + ','.join(e['if']))
    words += [f'then={t}' for t in e['then']]
    if e['again']:
        words.append('again=yes')
    return ' '.join(words)


def _text(self):
    """The piece as a block of the format, from NAME to ENDMAP (a floor of a whole place: from FLOOR)."""
    if self.whole:
        out = [f'FLOOR:  {self.name}']
    else:
        out = [f'NAME:   {self.name}']
        if self.part != 'middle':
            out.append(f'PART:   {self.part}')
        if self.kinds != ['any']:
            out.append(f"KIND:   {' '.join(self.kinds)}")
        if self.depth:
            out.append(f'DEPTH:  {self.depth}')
        if self.weight != 10:
            out.append(f'WEIGHT: {self.weight}')
        if self.shape:
            out.append(f'SHAPE:  {self.shape}')
        if self.gate != 'door':
            out.append(f'GATE:   {self.gate}')
        if self.doors:
            out.append(f'DOORS:  {self.doors}')
    out += [f'MOOD:   {m}' for m in self.moods]
    for g, opts in self.subst.items():
        out.append(f"SUBST:  {g} = " + ' '.join(f"{'none' if c == ' ' else c}:{w}" for c, w in opts))
    for g, (name, act) in self.things.items():
        out.append(f'THING:  {g} = {name}' + (f' do:{act}' if act else ''))
    for name, states in self.switches.items():
        out.append(f"SWITCH: {name} = {' '.join(states)}")
    for name, n in self.counters.items():
        out.append(f'COUNTER: {name} {n}')
    out += [f'EVENT:  {_ev_text(e)}' for e in self.events]
    for name, opts in self.lists.items():
        out.append(f'LIST:   {name} = ' + ' '.join(f'{k}:{w}' for k, w in opts))
    top = self.top()
    for (x, y), what in sorted(self.spots.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        out.append(f'CREATURE: {what} at {x},{y - top}')
    if self.more:
        out.append(f'MORE:   {self.more[0]} {self.more[1]}-{self.more[2]}')
    out += [f'DRESS:  {name} {n}' for name, n in self.dress]
    for name, (x, y), says in self.persons:
        out.append(f'PERSON: {name} at {x},{y}' + (f' says="{says}"' if says else ''))
    out += [f'ITEM:   {what} at {x},{y}' for what, (x, y) in self.items]
    out.append('MAP')
    out += self.rows()
    out.append('ENDMAP')
    return '\n'.join(out) + '\n'


Room.text = _text


# ------------------------------------------------------------------ whole places (round C)
def _hex(rgb):
    return '#%02x%02x%02x' % tuple(rgb)


class PlaceDoc:
    """A whole place as the editor holds it: its own lines ("In the world") and a Room for each floor (whole=True,
    as big as the place). Written back as a PLACE block (drawnplaces.py reads it)."""

    def __init__(self, name='new place', size=(60, 34)):
        self.name, self.file, self.size = name, '', tuple(size)
        self.sign, self.fg = '±', (232, 224, 200)
        self.look, self.rumour, self.book, self.land = '', '', '', 'fitted'
        self.world = {'land': ['any'], 'road': 'any', 'level': 1, 'how': 'one', 'found': ['map']}
        self.floors = []
        self.dirty = False
        self.came_from = None

    @classmethod
    def new(cls, name, size):
        """A fresh place: on the ground floor a small hall in the middle of the land, its door to the west."""
        d = cls(name, size)
        w, h = size
        g = d.add_floor('ground')
        x0, y0 = w // 2 - 6, h // 2 - 4
        for y in range(y0, y0 + 9):
            for x in range(x0, x0 + 13):
                g.set(x, y, '#' if x in (x0, x0 + 12) or y in (y0, y0 + 8) else '.')
        g.set(x0, h // 2, '+')
        g.undo.clear()
        g.dirty = False
        return d

    def add_floor(self, name):
        r = Room(name, *self.size)
        r.whole, r.max_w, r.max_h = True, self.size[0], self.size[1]
        r.file = self.file
        self.floors.append(r)
        return r

    def floor(self, name):
        return next((f for f in self.floors if f.name == name), None)

    def order(self):
        """The floors from the top down."""
        def key(f):
            if f.name == 'ground':
                return 0
            way, _, n = f.name.partition(' ')
            return (-1 if way == 'up' else 1) * int(n or 1) if n.isdigit() or not n else 99
        return sorted(self.floors, key=key)

    def next_name(self, way):
        """The name of the next floor up or down: 'up 2', 'down 1'..."""
        n = 1
        while self.floor(f'{way} {n}'):
            n += 1
        return f'{way} {n}'

    def set_size(self, size):
        self.size = tuple(size)
        for f in self.floors:
            f.max_w, f.max_h = size
            f.resize(*size)

    @property
    def is_dirty(self):
        return self.dirty or any(f.dirty for f in self.floors)

    def saved(self):
        self.dirty = False
        for f in self.floors:
            f.dirty = False

    @classmethod
    def from_place(cls, pl, path=''):
        """From a drawnplaces.Place: each floor a Room drawn as big as the place."""
        d = cls(pl.name, pl.size)
        d.came_from = pl.name             # an edited copy of a place may keep its name: it replaces it
        d.file = path or pl.file
        d.sign, d.fg, d.look, d.rumour, d.book, d.land = pl.sign, pl.fg, pl.look, pl.rumour, pl.book, pl.land
        d.world = copy.deepcopy(pl.world)
        for fl in pl.floors:
            r = Room.from_piece(fl.piece)
            r.name, r.whole = fl.name, True
            r.max_w, r.max_h = max(pl.size[0], r.w), max(pl.size[1], r.h)
            r.resize(max(pl.size[0], r.w), max(pl.size[1], len(fl.rows)))
            r.persons, r.items = list(fl.persons), list(fl.items)
            r.file = d.file
            r.undo.clear()
            r.dirty = False
            d.floors.append(r)
        return d

    def text(self):
        w = self.world
        out = [f'PLACE:  {self.name}', f'SIZE:   {self.size[0]}x{self.size[1]}', f'SIGN:   {self.sign} {_hex(self.fg)}']
        if self.look:
            out.append(f'LOOK:   {self.look}')
        out.append(f"WORLD:  land={','.join(w['land']) or 'any'} road={w['road']} level={w['level']} how={w['how']} "
                   f"found={','.join(w['found']) or 'map'}")
        if self.rumour:
            out.append(f'RUMOUR: {self.rumour}')
        if self.book:
            out.append(f'BOOK:   {self.book}')
        if self.land != 'fitted':
            out.append(f'LAND:   {self.land}')
        for f in self.order():
            out.append('')
            out += f.text().rstrip('\n').split('\n')
        out.append('ENDPLACE')
        return '\n'.join(out) + '\n'

    def to_place(self):
        """A drawnplaces.Place of what is drawn now (raises drawnplaces.Bad)."""
        from .. import drawnplaces as DP
        return DP.parse(self.text(), os.path.basename(self.file) if self.file else 'editor')[0]
