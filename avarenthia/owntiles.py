"""Nilio's own tiles and things (approved 31 October 2026, the editor's Ctrl+T). A TILE or OBJECT block in a pieces
file (any `pieces/*.des`, mostly `my tiles.des`) makes a tile of the game:

    TILE:   mossy flagstone           OBJECT: rusted cage
    SIGN:   .                         SIGN:   own
    FG:     #5f8a52                   PIXELS: ######## #..#..#. ... (8 rows of 8, # is drawn)
    BG:     #101a10                   FG:     #a08060
    LIKE:   floor                     BLOCKS: way
    LOOK:   Flagstones green...       DOES:   menagerie
    END                               LOOK:   An old cage, the bars red with rust.
                                      END

LIKE is how the tile behaves: floor, wall, water, shallow, chasm or fire (walking and sight). An object stands on the
floor and BLOCKS the way, sight, both or none; DOES is one of the things a telling thing can do (a new kind of doing
is built by Claude, never in the editor). SIGN is a sign of the tileset, or `own` with PIXELS: an 8 x 8 sign of its
own, added to the tileset when the game starts (codepoints from 0xE000, private use).

Own tiles come after the game's own, in the order they are read, by name. A save remembers their names, so when the
game gets new tiles or an own tile goes, loading moves every map to the new numbers (a tile that is gone becomes what
it was like)."""
from . import data as D

LIKES = {'floor': (True, False), 'wall': (False, True), 'water': (False, False), 'shallow': (True, False),
         'chasm': (False, False), 'fire': (False, False)}
LIKE_TILE = {'floor': D.FLOOR, 'wall': D.WALL, 'water': D.WATER, 'shallow': D.SHALLOW, 'chasm': D.CHASM,
             'fire': D.LAVA}
BLOCKS = ('none', 'way', 'sight', 'way sight')
SIGN0 = 0xE000
BASE = len(D.TILES)              # the game's own tiles; own ones come after
OWN = {}                         # name -> Own, as last read
IDS = {}                         # name -> tile index (this run)
SIGNS = {}                       # codepoint -> 8 rows of 8 ('#' drawn)
LOOKS = {}                       # tile index -> its look line


class Bad(ValueError):
    pass


class Own:
    __slots__ = ('kind', 'name', 'sign', 'pixels', 'fg', 'bg', 'like', 'blocks', 'does', 'look', 'file')

    def __init__(self, kind, name):
        self.kind, self.name = kind, name           # kind: 'TILE' or 'OBJECT'
        self.sign, self.pixels = '?', None
        self.fg, self.bg = '#c8c0b0', None
        self.like, self.blocks, self.does, self.look, self.file = 'floor', 'way', None, '', ''

    def walk_see(self):
        if self.kind == 'TILE':
            return LIKES.get(self.like, (True, False))
        return 'way' not in self.blocks or self.blocks == 'none', 'sight' in self.blocks

    def text(self):
        out = [f'{self.kind}:{" " * (8 - len(self.kind) - 1)}{self.name}', f'SIGN:   {self.sign}']
        if self.pixels:
            out.append('PIXELS: ' + ' '.join(self.pixels))
        out.append(f'FG:     {self.fg}')
        if self.bg:
            out.append(f'BG:     {self.bg}')
        if self.kind == 'TILE':
            out.append(f'LIKE:   {self.like}')
        else:
            out.append(f'BLOCKS: {self.blocks}')
            if self.does:
                out.append(f'DOES:   {self.does}')
        if self.look:
            out.append(f'LOOK:   {self.look}')
        out.append('END')
        return '\n'.join(out) + '\n'


def read(kind, name, lines, where=''):
    """An Own from the lines of its block (after the TILE / OBJECT line, up to END)."""
    o = Own(kind, name.strip())
    if not o.name:
        raise Bad(f'{where}: a {kind.lower()} needs a name')
    for ln in lines:
        if ':' not in ln:
            raise Bad(f'{where}: cannot read "{ln}"')
        k, v = ln.split(':', 1)
        k, v = k.strip().upper(), v.strip()
        if k == 'SIGN':
            o.sign = v if v == 'own' else (v[:1] or '?')
        elif k == 'PIXELS':
            rows = v.split()
            if len(rows) != 8 or any(len(r) != 8 or set(r) - {'#', '.'} for r in rows):
                raise Bad(f'{where}: PIXELS are 8 rows of 8, of # and .')
            o.pixels = rows
        elif k == 'FG':
            o.fg = v
        elif k == 'BG':
            o.bg = v or None
        elif k == 'LIKE':
            if v not in LIKES:
                raise Bad(f'{where}: LIKE is one of {", ".join(LIKES)}')
            o.like = v
        elif k == 'BLOCKS':
            if v not in BLOCKS:
                raise Bad(f'{where}: BLOCKS is none, way, sight or way sight')
            o.blocks = v
        elif k == 'DOES':
            o.does = v or None
        elif k == 'LOOK':
            o.look = v
        else:
            raise Bad(f'{where}: no such word: {k}')
    if o.sign == 'own' and not o.pixels:
        raise Bad(f'{where}: SIGN own needs PIXELS')
    for c in (o.fg, o.bg):
        if c is not None:
            try:
                D.hexrgb(c)
            except (ValueError, IndexError):
                raise Bad(f'{where}: a colour is written #rrggbb')
    return o


def register(o):
    """Make (or change) the game's tile of an own tile or thing; returns its index."""
    OWN[o.name] = o
    walk, opaque = o.walk_see()
    if o.sign == 'own':
        cp = sign_cp(o.name)
        SIGNS[cp] = list(o.pixels)
        ch = chr(cp)
    else:
        ch = o.sign
    t = D.Tile(ch, o.fg, walk, opaque, o.name, bg=o.bg)
    if o.name in IDS:
        D.TILES[IDS[o.name]] = t
    else:
        IDS[o.name] = len(D.TILES)
        D.TILES.append(t)
    if o.look:
        LOOKS[IDS[o.name]] = o.look
    return IDS[o.name]


_SIGN_OF = {}


def sign_cp(name):
    if name not in _SIGN_OF:
        _SIGN_OF[name] = SIGN0 + len(_SIGN_OF)
    return _SIGN_OF[name]


def add_signs(tileset):
    """Put the own 8 x 8 signs into a tcod tileset (the game's and the editor's windows)."""
    try:
        import numpy as np
    except ImportError:
        return
    for cp, rows in SIGNS.items():
        a = np.array([[255 if c == '#' else 0 for c in r] for r in rows], dtype=np.uint8)
        try:
            tileset.set_tile(cp, a)
        except Exception:
            pass


def like_of(index):
    """The game's own tile an own tile stands in for when it is gone."""
    for name, i in IDS.items():
        if i == index:
            o = OWN[name]
            return LIKE_TILE.get(o.like, D.FLOOR) if o.kind == 'TILE' else D.FLOOR
    return D.FLOOR


# ------------------------------------------------------------------ saves
def signature():
    """What a save keeps of the own tiles: the game's count, and each own tile's name and what it stands in for."""
    return (BASE, [(n, IDS[n], like_of(IDS[n])) for n in sorted(IDS, key=IDS.get)])


def remap(game, sig):
    """After loading: every map moved to this run's numbers for the own tiles (and the game's own grown)."""
    if not sig:
        sig = (BASE, [])
    base, own = sig
    if base == BASE and all(IDS.get(n) == i for n, i, _l in own):
        return False
    move = {}
    for n, i, like in own:
        move[i] = IDS.get(n, like)
    seen = set()
    maps = list(getattr(game, 'maps', {}).values()) + [getattr(game, 'map', None)]
    for m in maps:
        if m is None or id(m) in seen or not hasattr(m, 't'):
            continue
        seen.add(id(m))
        m.t = [move.get(t, t) if t >= base else t for t in m.t]
    return True
