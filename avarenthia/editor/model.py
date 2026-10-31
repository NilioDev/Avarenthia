"""A piece as the editor holds it: a grid of the format's signs (rock is ' '), the piece's lines (name, part,
kinds...), its telling things {letter: (tile name, action)}, substitutions and events as the format has them.
Every change goes through Room.change(), which keeps the undo history."""
import copy

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


def tile_of(ch, things):
    """The game's tile for one sign of the drawing (None for rock and unknown signs)."""
    if ch in things:
        return P.tile_named(things[ch][0])
    if ch == '+':
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
        self.file = ''
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
        """The drawing made w x h (at most MAX_W x MAX_H): cut on the right and bottom, or grown with rock."""
        w, h = max(3, min(MAX_W, w)), max(3, min(MAX_H, h))
        g = [[self.get(x, y) for x in range(w)] for y in range(h)]
        self.grid = g
        self.spots = {c: v for c, v in self.spots.items() if self.inb(*c)}
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

    # ------------------------------------------------------------ undo
    def _state(self):
        return (copy.deepcopy(self.grid), dict(self.things), copy.deepcopy(self.subst), copy.deepcopy(self.events),
                (self.name, self.part, list(self.kinds), self.depth, self.weight, self.shape, self.gate, list(self.moods)),
                copy.deepcopy((self.spots, self.lists, self.more, self.switches, self.counters, self.dress)))

    def _put_state(self, st):
        self.grid, self.things, self.subst, self.events = copy.deepcopy(st[0]), dict(st[1]), copy.deepcopy(st[2]), \
            copy.deepcopy(st[3])
        (self.name, self.part, kinds, self.depth, self.weight, self.shape, self.gate, moods) = st[4]
        self.kinds, self.moods = list(kinds), list(moods)
        self.spots, self.lists, self.more, self.switches, self.counters, self.dress = copy.deepcopy(st[5])

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
        r.file = p.file
        return r

    def rows(self):
        """The drawing as the file has it: rock at the ends of rows and empty rows at the top and bottom cut (they
        are part of the piece's size only in the editor); rock on the left is kept as drawn."""
        rows = [''.join(r).rstrip() for r in self.grid]
        while rows and not rows[-1]:
            rows.pop()
        while rows and not rows[0]:
            rows.pop(0)
        return rows

    def top(self):
        """How many empty rows rows() cuts at the top (the creatures' y counts from the first row written)."""
        n = 0
        while n < self.h and not ''.join(self.grid[n]).strip():
            n += 1
        return n if n < self.h else 0

    def to_piece(self):
        """A pieces.Piece of what is drawn now (not checked)."""
        return P.parse(self.text(), self.file or 'editor', checked=False)[0]


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
    """The piece as a block of the format, from NAME to ENDMAP."""
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
    out.append('MAP')
    out += self.rows()
    out.append('ENDMAP')
    return '\n'.join(out) + '\n'


Room.text = _text
