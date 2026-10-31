"""The editor's screen, in the game's own look: Tools and the Palette on the left, the drawing in the middle, the
piece, its layers and "Will the game take it?" on the right, a line of hints below and the status line at the bottom.

Pure: it draws on any canvas (the tests use FakeCanvas) and takes input as calls: key(tok, shift, ctrl),
text(s), mouse(kind, x, y, button) with x, y in screen cells (floats), wheel(dy, x, y). run.py feeds it from tcod
and draws the drawing zoomed in."""
import os
import re

from .. import data as D
from .. import pieces as P
from ..canvas import scale, wrap_text
from . import files as F
from . import layers as LY
from . import maker as MK
from . import tools as T
from .model import Room, MAX_W, MAX_H, PARTS, GATES, KINDS, DOES, PUZZLE_THINGS, tile_of

W, H = 110, 60
BG = (13, 11, 10)
PANEL = (22, 18, 15)
BAR = (34, 28, 22)
FIELD = (30, 25, 20)
SEL = (60, 46, 30)
LINE = (70, 60, 48)
ROCK = (24, 21, 19)
OUTSIDE = (16, 14, 13)
FG = (221, 211, 189)
DIM = (143, 133, 115)
GOLD = (217, 165, 71)
GOOD = (134, 196, 111)
BAD = (236, 106, 92)
INFO = (136, 182, 220)
WARN_BG = (110, 26, 20)

AX, AY, AW, AH = 25, 3, 53, 42            # the drawing area
RX = 80                                   # the right column
PAL_Y0, PAL_Y1 = 11, H - 3                # the palette's lines

TOOLS = [('d', 'Draw'), ('l', 'Line'), ('r', 'Rectangle'), ('f', 'Fill'), ('s', 'Select'), ('v', 'Variety')]
LAYERS = ('Ground', 'Things', 'Creatures', 'Events')
GROUND = ['.', '#', '"', 'r', 'v', '~', ',', 'L', '=', 'i']
WAYS = ['+', "'", 'n', '<', '>']
FURNITURE = [c for c in P.LEGEND if c not in GROUND and c not in WAYS and c != 'n']
HINTS = [
    'Left mouse draws with the picked sign, right mouse picks the sign under it. Wheel: zoom. Middle mouse, or '
    'Space and drag: move the view.',
    'The dim # round the room is the rock wall: drawn for you, never by hand. The + is the one way in.',
    'Drag the gold corner to make the room bigger or smaller, up to 40 x 30.',
]


def _tile(ch, things):
    t = tile_of(ch, things)
    return D.TILES[t] if t is not None else None


class Item:
    """One line of the palette: a sign of the format, or a thing (tile name, what it does)."""
    __slots__ = ('kind', 'ch', 'name', 'act', 'label')

    def __init__(self, kind, ch=None, name=None, act=None, label=''):
        self.kind, self.ch, self.name, self.act, self.label = kind, ch, name, act, label

    def tile(self):
        if self.kind == 'sign':
            return _tile(self.ch, {})
        t = P.tile_named(self.name)
        return D.TILES[t] if t is not None else None


def palette(layer):
    """[(header, [Item])] for a layer."""
    from .. import owntiles as OT
    mine = sorted(OT.OWN.values(), key=lambda o: o.name)
    if layer == 'Ground':
        own = [Item('thing', name=o.name, label=o.name) for o in mine if o.kind == 'TILE']
        return [('GROUND', [Item('sign', c, label=D.TILES[P.LEGEND[c]].name) for c in GROUND[:5]]),
                ('WATER AND FIRE', [Item('sign', c, label=D.TILES[P.LEGEND[c]].name) for c in GROUND[5:]]),
                ('WAYS', [Item('sign', '+', label='a way in, always'), Item('sign', "'", label='a door, maybe'),
                          Item('sign', 'n', label='a hidden door'),
                          Item('sign', '<', label='stairs up'), Item('sign', '>', label='stairs down')]),
                ('ROCK', [Item('sign', ' ', label='rock (rubber)')])] + ([('MY TILES', own)] if own else [])
    telling = [Item('thing', name=DOES[a], act=a, label=f'{a}') for a in sorted(DOES)]
    puzzle = [Item('thing', name=t, act=a, label=t) for a, t in PUZZLE_THINGS]
    named = set(P.TILE_NAMES)
    seen = {D.TILES[v].name for v in P.LEGEND.values()} | {D.TILES[v].name for v in P.TILE_NAMES.values()}
    more = [Item('thing', name=k, label=D.TILES[v].name) for k, v in sorted(P.TILE_NAMES.items())
            if v not in P.LEGEND.values()]
    seen |= {t for _a, t in PUZZLE_THINGS}
    for t in D.TILES:
        if t.name not in seen and t.name not in named:
            seen.add(t.name)
            more.append(Item('thing', name=t.name, label=t.name))
    own = [Item('thing', name=o.name, act=o.does, label=o.name) for o in mine if o.kind == 'OBJECT']
    more = [it for it in more if it.name not in OT.OWN]
    return [('THINGS', [Item('sign', c, label=D.TILES[P.LEGEND[c]].name) for c in FURNITURE])] + \
        ([('MY THINGS', own)] if own else []) + [('TELLING THINGS', telling), ('PUZZLE THINGS', puzzle),
                                                 ('MORE: EVERY TILE', more)]


def _is_ground(ch):
    return ch in GROUND or ch in WAYS or ch == ' '


class Editor(MK.Maker, LY.LayerTools):
    _Item = Item

    def __init__(self, room=None):
        try:
            F.own_things()            # your own tiles and things, made in the game's list of tiles
        except (P.Bad, OSError, ValueError):
            pass
        self.room = room or self.blank()
        self.tool = 'Draw'
        self.layer = 'Ground'
        self.pick = {'Ground': Item('sign', '.', label='floor'), 'Things': Item('sign', 's', label='statue'),
                     'Creatures': Item('spot', '?', label='one of the place'), 'Events': Item('none'),
                     'Variety': None}
        self.pal_scroll = {k: 0 for k in self.pick}
        self.want_try = False         # F5: run.py opens the game on the piece
        self.ev_sel = None            # the event picked on the Events layer
        self.ev_scroll = 0
        self.dressed = set()          # cells just dressed (Ctrl+D, now): light green until the next stroke
        self.zoom = 2
        self.view = [0, 0]
        self.center()
        self.drag = None              # what the mouse is doing: ('paint'|'line'|'rect'|'select'|'pan'|'size', ...)
        self.hover = None             # the drawing cell under the mouse
        self.sel = None               # (a, b) a selected rectangle
        self.clip = None
        self.pasting = False
        self.field = None             # the field being typed in: (name, text)
        self.dialog = None            # None, ('open', state) or ('new', state) or ('kinds',)
        self.msg = ''
        self.msg_bad = False
        self.space = False
        self.quit_asked = False
        self.running = True
        self.saved_name = self.room.name

    @staticmethod
    def blank():
        r = Room('new room', 13, 11)
        for y in range(1, 10):
            for x in range(1, 12):
                r.set(x, y, '.')
        r.set(6, 10, '+')
        r.dirty = False
        return r

    # ------------------------------------------------------------ helpers
    def zoom_size(self):
        return AW // self.zoom, AH // self.zoom

    def center(self):
        vw, vh = self.zoom_size()
        self.view = [(self.room.w - vw) // 2, (self.room.h - vh) // 2]

    def say(self, s, bad=False):
        self.msg, self.msg_bad = s, bad

    def cell_at(self, x, y):
        """The drawing cell under screen cell x, y (floats), or None outside the drawing area."""
        if not (AX <= x < AX + AW and AY <= y < AY + AH):
            return None
        z = self.zoom
        return (self.view[0] + int((x - AX) // z), self.view[1] + int((y - AY) // z))

    def piece(self):
        return self.room.to_piece()

    def problems(self):
        """The check: [(ok, message, cells)], the game's own rules first, then the editor's warnings. Worked out
        once for each state of the room."""
        key = (self.room.text(), self.room.file)
        if getattr(self, '_probs_key', None) != key:
            self._probs_key, self._probs = key, self._problems()
        return self._probs

    def _problems(self):
        empty = [i + 1 for i, e in enumerate(self.room.events) if not e['then']]
        if empty:
            return [(False, f'Event {n} needs a THEN: click its + to give it one, or × to take it away.', [])
                    for n in empty]
        try:
            p = self.piece()
        except P.Bad as e:
            return [(False, re.sub(r'^[^:]*:\d+: ', '', str(e)), [])]
        out = [(False, m[0].upper() + m[1:] + '.', cells) for m, cells in P.problems(p)]
        if not out:
            out.append((True, 'One way in, in a straight wall, two cells of room on each side.', []))
            out.append((True, 'No two walls side by side.', []))
            out.append((True, 'Every sign is one the game knows.', []))
        others = [q for q in F.game_pieces_cached() if q.name == self.room.name and q.file != self.room.file]
        if others or not self.room.name.strip():
            out.append((False, 'The name is used by another piece: every piece needs its own.' if others
                        else 'The piece needs a name.', []))
        for g, (name, act) in sorted(self.room.things.items()):
            if act and any(g in row for row in self.room.grid):
                out.append((True, f'The {name} does: {act}.', []))
        r = self.room
        if r.spots or r.more:
            n = len(r.spots)
            out.append((True, f"{n} creature{'s' if n != 1 else ''} drawn" +
                        (f', and {r.more[1]} to {r.more[2]} more.' if r.more else '.'), []))
        if r.events:
            out.append((True, f"{len(r.events)} event{'s' if len(r.events) > 1 else ''}.", []))
        if r.dress:
            out.append((True, 'Dressed in the game: ' + ', '.join(f'{n} {k}' for n, k in r.dress) + '.', []))
        if not self.room.moods:
            out.append((None, 'No mood line yet: write one, or the game says nothing when you step in.', []))
        else:
            out.append((True, f"{len(self.room.moods)} mood line{'s' if len(self.room.moods) > 1 else ''}.", []))
        return out

    def can_save(self):
        return all(ok is not False for ok, _m, _c in self.problems())

    # ------------------------------------------------------------ drawing on the grid
    def current(self):
        """The sign the picked palette line draws (a letter for a thing, made on first use), or None."""
        it = self.pick[self.layer]
        if it.kind == 'sign':
            return it.ch
        g = self.room.letter_for(it.name, it.act)
        if g is None:
            self.say('All 26 letters for things are in use in this piece.', True)
        return g

    def pal(self):
        """[(header, [Item])] of the palette as it stands: the Variety groups while that tool is picked."""
        if self.tool == 'Variety':
            return self.variety_palette()
        if self.layer == 'Creatures':
            return self.creature_palette()
        if self.layer == 'Events':
            return self.event_palette()
        return palette(self.layer)

    def _pal_key(self):
        return 'Variety' if self.tool == 'Variety' else self.layer

    def apply(self, cells, ch=None):
        self.dressed = set()
        if self.tool == 'Variety' and ch is None:
            self.variety_paint(cells)
            return
        ch = self.current() if ch is None else ch
        if ch is None:
            return
        T.paint(self.room, cells, ch)
        self.room.spots = {c: v for c, v in self.room.spots.items() if self.room.get(*c) not in " #+'"}
        self.room.tidy()

    def pick_under(self, c):
        """Right mouse: take the sign under the mouse into the palette of its layer."""
        ch = self.room.get(*c)
        if ch in self.room.things:
            name, act = self.room.things[ch]
            self.layer = 'Things'
            self.pick['Things'] = Item('thing', name=name, act=act, label=act or name)
        elif _is_ground(ch):
            self.layer = 'Ground'
            t = _tile(ch, {})
            self.pick['Ground'] = Item('sign', ch, label=t.name if t else 'rock (rubber)')
        else:
            self.layer = 'Things'
            self.pick['Things'] = Item('sign', ch, label=D.TILES[P.LEGEND[ch]].name)

    # ------------------------------------------------------------ input
    def key(self, tok, shift=False, ctrl=False):
        r = self.room
        if self.field:
            return self.field_key(tok)
        if self.dialog:
            return self.dialog_key(tok, shift, ctrl)
        if ctrl:
            if tok == 'z':
                self.say('Undone.' if r.step_back() else 'Nothing to undo.')
            elif tok == 'y':
                self.say('Redone.' if r.step_forward() else 'Nothing to redo.')
            elif tok == 's':
                self.save()
            elif tok == 'o':
                self.open_dialog()
            elif tok == 'n':
                self.new_dialog()
            elif tok in ('c', 'x') and self.sel:
                self.clip = T.copy_cells(r, *self.sel)
                if tok == 'x':
                    r.change()
                    T.paint(r, T.rect_cells(*self.sel, filled=True), ' ')
                    r.tidy()
                self.say('Copied. Ctrl+V and click to set it down.' if tok == 'c' else 'Cut. Ctrl+V and click to set it down.')
            elif tok == 'v' and self.clip:
                self.pasting = True
                self.say('Click where its top left corner goes; Esc to stop.')
            elif tok == 'd':
                self.dress_dialog()
            elif tok == 't':
                self.maker_dialog()
            elif tok == 'r':
                self.roll_dialog()
            return
        if tok == 'esc':
            if self.pasting or self.sel:
                self.pasting, self.sel = False, None
            return
        if tok == 'tab':
            self.layer = LAYERS[(LAYERS.index(self.layer) + (-1 if shift else 1)) % len(LAYERS)]
            return
        if tok == 'delete' and self.sel:
            r.change()
            T.paint(r, T.rect_cells(*self.sel, filled=True), ' ')
            r.tidy()
            return
        if tok == 'space':
            self.space = True
            return
        if tok == 'f5':
            if self.can_save():
                self.want_try = True
            else:
                self.say('Try waits until the game takes it: fix the red lines first.', True)
            return
        if self.layer == 'Creatures' and self.creature_key(tok):
            return
        for k, name in TOOLS:
            if tok == k:
                self.tool = name
                if self.layer in ('Creatures', 'Events'):
                    self.layer = 'Ground'
                if name != 'Select':
                    self.sel = None
                return
        if tok in ('=', '+'):
            self.set_zoom(self.zoom + 1)
        elif tok == '-':
            self.set_zoom(self.zoom - 1)
        elif tok in ('left', 'right', 'up', 'down'):
            dx, dy = {'left': (-1, 0), 'right': (1, 0), 'up': (0, -1), 'down': (0, 1)}[tok]
            self.view[0] += dx * (4 if shift else 1)
            self.view[1] += dy * (4 if shift else 1)

    def key_up(self, tok):
        if tok == 'space':
            self.space = False

    def set_zoom(self, z, at=None):
        z = max(1, min(4, z))
        if z == self.zoom:
            return
        vw, vh = self.zoom_size()
        c = at or (self.view[0] + vw // 2, self.view[1] + vh // 2)
        self.zoom = z
        vw, vh = self.zoom_size()
        self.view = [c[0] - vw // 2, c[1] - vh // 2]

    def wheel(self, dy, x, y):
        if self.dialog:
            st = self.dialog[1] if len(self.dialog) > 1 else None
            if isinstance(st, dict):
                st['scroll'] = max(0, st.get('scroll', 0) - dy * 3)
            return
        if x < 24 and y >= PAL_Y0:
            n = sum(1 + len(items) + 1 for _h, items in self.pal())
            k = self._pal_key()
            self.pal_scroll[k] = max(0, min(n - (PAL_Y1 - PAL_Y0), self.pal_scroll[k] - dy * 3))
        elif self.layer == 'Events' and y >= AY + AH + 1:
            self.ev_scroll = max(0, min(len(self.room.events) - 1, self.ev_scroll - dy))
        elif self.cell_at(x, y) is not None:
            self.set_zoom(self.zoom + (1 if dy > 0 else -1), self.cell_at(x, y))

    def mouse(self, kind, x, y, button=1):
        """kind: 'down', 'move' or 'up'; button 1 left, 2 middle, 3 right."""
        r = self.room
        c = self.cell_at(x, y)
        if kind == 'move':
            self.hover = c
        if self.dialog:
            if kind == 'down':
                self.dialog_click(x, y, button)
            return
        if kind == 'down' and self.field and not self.field_hit(x, y):
            self.field_done()
        # an ongoing drag
        if self.drag:
            what = self.drag[0]
            if kind == 'move':
                if what == 'pan':
                    sx, sy, vx, vy = self.drag[1:]
                    self.view = [vx - int((x - sx) // self.zoom), vy - int((y - sy) // self.zoom)]
                elif what == 'size':
                    cx, cy = self.view[0] + int((x - AX) // self.zoom), self.view[1] + int((y - AY) // self.zoom)
                    w, h = self.drag[1], self.drag[2]
                    nw = cx if self.drag[3] in ('corner', 'right') else w
                    nh = cy if self.drag[3] in ('corner', 'bottom') else h
                    if nw > MAX_W or nh > MAX_H:
                        self.say('40 x 30 is the most for a room; bigger: make it a whole place.', True)
                    r.resize(nw, nh)
                elif c is not None:
                    if what == 'paint':
                        last = self.drag[1]
                        self.apply(T.line_cells(last, c))
                        self.drag = ('paint', c)
                    elif what in ('line', 'rect', 'select'):
                        self.drag = (what, self.drag[1], c)
                        if what == 'select':
                            self.sel = (self.drag[1], c)
            elif kind == 'up':
                if what == 'wire':
                    if c is not None and c != self.drag[1] and self.wire(self.drag[1], c):
                        self.say('A wire: an event is made. Change what it does in the list below.')
                    elif c == self.drag[1]:
                        self.event_click(c, 1)
                    self.drag = None
                    return
                if what in ('line', 'rect'):
                    a, b = self.drag[1], self.drag[2]
                    cells = T.line_cells(a, b) if what == 'line' else T.rect_cells(a, b, filled=self.drag[3] if len(self.drag) > 3 else False)
                    self.apply(cells)
                elif what == 'select':
                    self.sel = (self.drag[1], self.drag[2])
                self.drag = None
            return
        if kind != 'down':
            return
        # a click
        if y < 1:
            return self.top_click(x)
        if 1 <= y < 2 and AX <= x < AX + AW:
            for _lab, x0, x1, act in self._bar_buttons():
                if x0 <= x < x1:
                    act()
            return
        if button == 2 or (button == 1 and self.space):
            self.drag = ('pan', x, y, self.view[0], self.view[1])
            return
        if c is not None:
            h = self.handle_at(c)
            if h and button == 1:
                r.change()
                self.drag = ('size', r.w, r.h, h)
                return
            if self.pasting and button == 1:
                r.change()
                T.paste_cells(r, self.clip, c)
                r.tidy()
                self.pasting = False
                return
            if r.inb(*c) and self.layer == 'Creatures':
                self.creature_click(c, button)
                return
            if r.inb(*c) and self.layer == 'Events':
                if button == 1 and r.get(*c) in r.things:
                    self.drag = ('wire', c)
                else:
                    self.event_click(c, button)
                return
            if button == 3:
                if r.inb(*c):
                    self.pick_under(c)
                return
            if not r.inb(*c):
                return
            if self.tool in ('Draw', 'Variety'):
                r.change()
                self.apply([c])
                self.drag = ('paint', c)
            elif self.tool == 'Fill':
                r.change()
                self.apply(T.fill_cells(r, c))
            elif self.tool == 'Variety':
                r.change()
                self.apply([c])
                self.drag = ('paint', c)
            elif self.tool in ('Line', 'Rectangle'):
                r.change()
                self.drag = ('line' if self.tool == 'Line' else 'rect', c, c, self._shift)
            elif self.tool == 'Select':
                self.drag = ('select', c, c)
                self.sel = (c, c)
            return
        if x < 24:
            return self.left_click(x, y, button)
        if x >= RX:
            return self.right_click(x, y, button)
        if y >= AY + AH:
            return self.bottom_click(x, y, button)

    _shift = False

    def set_shift(self, on):
        self._shift = on

    def handle_at(self, c):
        r = self.room
        return {(r.w, r.h): 'corner', (r.w, r.h // 2): 'right', (r.w // 2, r.h): 'bottom'}.get(tuple(c))

    # ------------------------------------------------------------ the panels' clicks
    def top_click(self, x):
        for lab, x0, x1, act in self._top_buttons():
            if x0 <= x < x1:
                act()

    def _top_buttons(self):
        out, x = [], 58
        for k, lab, act in (('Ctrl+N', 'New', self.new_dialog), ('Ctrl+O', 'Open', self.open_dialog),
                            ('Ctrl+S', 'Save', self.save)):
            w = len(k) + 1 + len(lab)
            out.append((f'{k} {lab}', x, x + w, act))
            x += w + 2
        return out

    def _bar_buttons(self):
        """The buttons over the drawing: what Ctrl+D, Ctrl+R, Ctrl+T and F5 do, for the mouse."""
        out, x = [], AX
        for k, lab, act in (('Ctrl+D', 'Dress', self.dress_dialog), ('Ctrl+R', 'Roll', self.roll_dialog),
                            ('Ctrl+T', 'Tile', self.maker_dialog), ('F5', 'Try', lambda: self.key('f5'))):
            w = len(k) + 1 + len(lab)
            out.append((f'{k} {lab}', x, x + w, act))
            x += w + 2
        return out

    def left_click(self, x, y, button):
        if 2 <= y < 2 + len(TOOLS):
            self.tool = TOOLS[int(y) - 2][1]
            if self.layer in ('Creatures', 'Events'):
                self.layer = 'Ground'
            return
        if PAL_Y0 <= y < PAL_Y1:
            line = int(y) - PAL_Y0 + self.pal_scroll[self._pal_key()]
            for kind, it in self._pal_lines():
                if line == 0:
                    if kind == 'item' and not self.palette_click(it, button):
                        self.pick[self._pal_key()] = it
                    return
                line -= 1

    def _pal_lines(self):
        out = []
        for head, items in self.pal():
            out.append(('head', head))
            out += [('item', it) for it in items]
            out.append(('gap', None))
        return out

    def right_click(self, x, y, button):
        y = int(y)
        for name, yy in self._field_rows():
            if y == yy:
                return self.field_click(name, button)
        for i, lay in enumerate(LAYERS):
            if y == 24 + i:
                self.layer = lay
                if self.tool == 'Variety' and lay in ('Creatures', 'Events'):
                    self.tool = 'Draw'
                return
        for ok, msg, cells, yy, n in self._check_rows():
            if yy <= y < yy + n and cells:
                vw, vh = self.zoom_size()
                cx, cy = cells[0]
                self.view = [cx - vw // 2, cy - vh // 2]
                return

    def bottom_click(self, x, y, button=1):
        if self.layer != 'Events':
            return
        for bx, by, s, _k, act, _i in self.event_rows(AX + 1, AY + AH + 2, AW - 2, H - AY - AH - 4):
            if by == int(y) and bx <= x < bx + len(s) and act:
                if act[0] == 'sel':
                    self.ev_sel = act[1]
                else:
                    self.event_act(act, button)
                return

    # ------------------------------------------------------------ fields of the piece
    def _field_rows(self):
        rows = [('name', 2), ('part', 3), ('kinds', 4), ('depth', 5), ('weight', 6), ('gate', 7), ('doors', 8),
                ('shape', 9), ('size', 10)]
        y = 12
        for i, m in enumerate(self.room.moods):
            rows.append((f'mood{i}', y))
            y += len(wrap_text('"' + m + '"', W - RX - 4)[:4])
        if len(self.room.moods) < 4:
            rows.append(('mood+', y))
        return rows

    def field_value(self, name):
        r = self.room
        return {'name': r.name, 'part': r.part, 'kinds': ' '.join(r.kinds), 'depth': str(r.depth),
                'weight': str(r.weight), 'gate': r.gate, 'shape': r.shape, 'size': f'{r.w} x {r.h}',
                'doors': r.doors or 'each +'}.get(name, '')

    def field_click(self, name, button):
        r = self.room
        if name == 'part':
            r.change()
            r.part = PARTS[(PARTS.index(r.part) + (1 if button == 1 else -1)) % len(PARTS)]
        elif name == 'gate':
            r.change()
            r.gate = GATES[(GATES.index(r.gate) + (1 if button == 1 else -1)) % len(GATES)]
        elif name == 'doors':
            r.change()
            opts = ['', '1', '1-2', '2-3', 'all']
            r.doors = opts[(opts.index(r.doors) + (1 if button == 1 else -1)) % len(opts)] if r.doors in opts else ''
        elif name == 'kinds':
            self.dialog = ('kinds', {})
        elif name.startswith('mood'):
            i = len(r.moods) if name == 'mood+' else int(name[4:])
            if button == 3 and name != 'mood+':
                r.change()
                r.moods.pop(i)
                return
            self.field = (name, r.moods[i] if i < len(r.moods) else '')
        else:
            self.field = (name, self.field_value(name))

    def field_hit(self, x, y):
        return x >= RX and any(int(y) == yy and n == self.field[0] for n, yy in self._field_rows())

    def text(self, s):
        if self.dialog and self.dialog[0] == 'line':
            st = self.dialog[1]
            st['text'] = (st['text'] + s)[:120]
            return
        if self.field:
            name, val = self.field
            limit = 120 if name.startswith('mood') else 40
            self.field = (name, (val + s)[:limit])
        elif self.dialog and self.dialog[0] == 'new' and self.dialog[1].get('typing'):
            st = self.dialog[1]
            st['size'] = (st['size'] + s)[:7]

    def field_key(self, tok):
        name, val = self.field
        if tok == 'backspace':
            self.field = (name, val[:-1])
        elif tok == 'esc':
            self.field = None
        elif tok in ('enter', 'np_enter', 'tab'):
            self.field_done()

    def field_done(self):
        name, val = self.field
        self.field = None
        r = self.room
        val = val.strip()
        r.change()
        if name == 'name' and val:
            r.name = val
        elif name in ('depth', 'weight'):
            try:
                setattr(r, name, max(0 if name == 'depth' else 1, int(val)))
            except ValueError:
                self.say('A number, please.', True)
        elif name == 'shape':
            r.shape = val
        elif name == 'size':
            try:
                w, h = (int(v) for v in val.lower().replace('x', ' ').split())
                if w > MAX_W or h > MAX_H:
                    self.say('40 x 30 is the most for a room; bigger: make it a whole place.', True)
                r.resize(w, h)
            except ValueError:
                self.say('Write the size as 20 x 14.', True)
        elif name.startswith('mood'):
            i = len(r.moods) if name == 'mood+' else int(name[4:])
            if val:
                if i < len(r.moods):
                    r.moods[i] = val
                else:
                    r.moods.append(val)
            elif i < len(r.moods):
                r.moods.pop(i)

    # ------------------------------------------------------------ files
    def save(self):
        if not self.can_save():
            n = sum(1 for ok, _m, _c in self.problems() if ok is False)
            self.say(f'Not saved: {n} thing{"s" if n > 1 else ""} to fix first (the red lines).', True)
            return False
        path = F.save(self.room, old_name=self.saved_name)
        self.saved_name = self.room.name
        F.forget_cache()
        self.say(f'Saved in {os.path.basename(path)}.')
        return True

    def open_dialog(self):
        st = {'files': F.files(), 'file': 0, 'scroll': 0}
        if not st['files']:
            st['files'] = [('the game\'s pieces', None)]
        self.dialog = ('open', st)
        self._load_dialog_rooms(st)

    def _load_dialog_rooms(self, st):
        label, path = st['files'][st['file']]
        try:
            st['rooms'] = F.read(path) if path else F.game_pieces()
            st['error'] = ''
        except (P.Bad, OSError, ValueError) as e:
            st['rooms'], st['error'] = [], str(e)

    def new_dialog(self):
        self.dialog = ('new', {'part': 'middle', 'kinds': ['any'], 'size': '13 x 11', 'typing': False})

    def make_new(self, st):
        try:
            w, h = (int(v) for v in st['size'].lower().replace('x', ' ').split())
        except ValueError:
            w, h = 13, 11
        w, h = max(5, min(MAX_W, w)), max(5, min(MAX_H, h))
        r = Room('new room', w, h)
        for y in range(1, h - 1):
            for x in range(1, w - 1):
                r.set(x, y, '.')
        r.set(w // 2, h - 1, '+')
        r.part, r.kinds = st['part'], list(st['kinds'])
        r.file = os.path.join(F.home(), F.MINE)
        r.dirty = False
        names = {q.name for q in F.game_pieces_cached()} | {q.name for q in self._mine()}
        n = 1
        while r.name in names:
            n += 1
            r.name = f'new room {n}'
        self.room, self.saved_name = r, r.name
        self.center()
        self.dialog = None
        self.field = ('name', r.name)

    def _mine(self):
        path = os.path.join(F.home(), F.MINE)
        try:
            return F.read(path) if os.path.exists(path) else []
        except (P.Bad, OSError, ValueError):
            return []

    # ------------------------------------------------------------ dialogs
    def dialog_key(self, tok, shift, ctrl):
        kind, st = self.dialog[0], self.dialog[1] if len(self.dialog) > 1 else {}
        if kind == 'line':
            if tok == 'backspace':
                st['text'] = st['text'][:-1]
            elif tok == 'esc':
                self.dialog = None
            elif tok in ('enter', 'np_enter'):
                self.dialog = None
                st['done'](st['text'])
            self.after_small_dialog()
            return
        if kind == 'maker' and tok in ('enter', 'np_enter'):
            if self.maker_save() and getattr(self, 'on_signs', None):
                self.on_signs()
            return
        if kind == 'dress' and tok in ('n', 'g', 'r'):
            if tok == 'n':
                self.dress_now()
            elif tok == 'g':
                self.dress_in_game()
            elif st.get('laid'):
                self.dress_now(again=True)
            return
        if kind == 'roll' and tok == 'r':
            self.roll_dialog()
            return
        if tok == 'esc':
            if kind == 'new' and st.get('typing'):
                st['typing'] = False
            else:
                self.dialog = None
                if kind == 'pick':
                    self.after_small_dialog()
            return
        if kind == 'new':
            if st.get('typing'):
                if tok == 'backspace':
                    st['size'] = st['size'][:-1]
                elif tok in ('enter', 'np_enter'):
                    st['typing'] = False
                return
            if tok in ('enter', 'np_enter'):
                self.make_new(st)
            elif tok in ('up', 'down'):
                parts = PARTS[1:]
                i = parts.index(st['part']) if st['part'] in parts else 1
                st['part'] = parts[(i + (1 if tok == 'down' else -1)) % len(parts)]
        elif kind == 'open':
            if tok in ('up', 'down'):
                st['file'] = (st['file'] + (1 if tok == 'down' else -1)) % len(st['files'])
                st['scroll'] = 0
                self._load_dialog_rooms(st)
        elif kind == 'kinds' and tok in ('enter', 'np_enter'):
            self.dialog = None

    def _dialog_box(self):
        """(x, y, w, h) of the open window."""
        kind, st = self.dialog[0], self.dialog[1] if len(self.dialog) > 1 else {}
        if kind == 'line':
            return 20, 24, 70, 7
        if kind == 'pick':
            return 18, 5, 74, 50
        if kind == 'new':
            return 28, 14, 54, 18
        if kind == 'kinds':
            return RX + 1, 4, W - RX - 2, len(KINDS) + 6
        if kind == 'variety':
            return 28, 14, 56, len(self.room.subst.get(st['group'], [])) + len(self._variety_adds()) + 8
        if kind == 'dress':
            return 28, 13, 56, len(LY.DR.SETS) + 9
        return 4, 5, 102, 50

    def dialog_click(self, x, y, button):
        kind, st = self.dialog[0], self.dialog[1] if len(self.dialog) > 1 else {}
        y = int(y)
        box = self._dialog_box()
        if box and not (box[0] <= x < box[0] + box[2] and box[1] <= y < box[1] + box[3]):
            self.dialog = None                      # a click outside a window closes it, as Esc does
            if kind in ('pick', 'line'):
                self.after_small_dialog()
            return
        if kind == 'line' and y == 28:
            if 22 <= x < 26:
                self.dialog = None
                st['done'](st['text'])
                self.after_small_dialog()
            elif 28 <= x < 34:
                self.dialog = None
                self.after_small_dialog()
            return
        if kind == 'roll' and y == 53:
            self.roll_dialog()
            return
        if kind == 'maker' and y == 52 and 21 <= x < 30:
            self.dialog = None
            return
        if kind == 'pick':
            i = y - 8 + st.get('scroll', 0)
            if 20 <= x < 90 and 8 <= y < 52 and 0 <= i < len(st['options']):
                self.dialog = None
                st['done'](st['options'][i][1])
                self.after_small_dialog()
            return
        if kind == 'maker':
            return self.maker_click(x, y, button)
        if kind == 'lists':
            return self.lists_click(x, y, button)
        if kind == 'variety':
            return self.variety_click(x, y, button)
        if kind == 'dress':
            return self.dress_click(x, y, button)
        if kind in ('line', 'roll'):
            return
        if kind == 'open':
            fx0, rx0, y0 = 6, 34, 8
            if fx0 <= x < rx0 - 1 and y0 <= y < y0 + len(st['files']):
                st['file'] = y - y0
                st['scroll'] = 0
                self._load_dialog_rooms(st)
            elif rx0 <= x < 104 and y0 <= y < y0 + 44:
                i = y - y0 + st.get('scroll', 0)
                if 0 <= i < len(st['rooms']):
                    r = st['rooms'][i]
                    if not r.file:
                        r.file = os.path.join(F.home(), F.MINE)
                    self.room, self.saved_name = r, r.name
                    self.center()
                    self.dialog = None
                    self.say(f'Opened {r.name}.')
        elif kind == 'new':
            nx, ny = 28, 14
            parts = PARTS[1:]
            for i, part in enumerate(parts):
                if y == ny + 3 + i:
                    st['part'] = part
            if y == ny + 9:
                xx = nx + 2
                for k in KINDS:
                    if xx <= x < xx + len(k) + 2:
                        self._toggle_kind(st['kinds'], k)
                    xx += len(k) + 4
            if y == ny + 12 and nx + 2 <= x < nx + 12:
                st['typing'] = True
                st['size'] = ''
            if y == ny + 15:
                if nx + 2 <= x < nx + 14:
                    self.make_new(st)
                elif nx + 16 <= x < nx + 26:
                    self.dialog = None
        elif kind == 'kinds':
            kx, ky = RX + 2, 5
            for i, k in enumerate(KINDS):
                if y == ky + i:
                    self.room.change()
                    self._toggle_kind(self.room.kinds, k, button == 3)
            if y == ky + len(KINDS) + 1:
                self.dialog = None

    @staticmethod
    def _toggle_kind(kinds, k, keep_out=False):
        if k == 'any':
            kinds[:] = ['any']
            return
        if 'any' in kinds:
            kinds.remove('any')
        tag = f'not:{k}' if keep_out else k
        other = k if keep_out else f'not:{k}'
        if other in kinds:
            kinds.remove(other)
        if tag in kinds:
            kinds.remove(tag)
        else:
            kinds.append(tag)
        if not [q for q in kinds if not q.startswith('not:')]:
            kinds.insert(0, 'any')

    # ------------------------------------------------------------ drawing the screen
    def render(self, cv, draw_area=True):
        cv.clear(BG)
        self.render_top(cv)
        self.render_bar(cv)
        self.render_left(cv)
        self.render_ruler(cv)
        if draw_area:
            z = self.zoom
            if self.dialog:
                self.zoom = 1
            self.render_drawing(_Offset(cv, AX, AY), AW // self.zoom, AH // self.zoom, self.zoom == 1)
            self.zoom = z
        self.render_right(cv)
        self.render_bottom(cv)
        self.render_status(cv)
        if self.dialog:
            {'open': self.render_open, 'new': self.render_new, 'kinds': self.render_kinds, 'line': self.render_line,
             'pick': self.render_pick, 'lists': self.render_lists, 'variety': self.render_variety,
             'dress': self.render_dress, 'roll': self.render_roll, 'maker': self.render_maker}[self.dialog[0]](cv)

    def render_top(self, cv):
        cv.fill(0, 0, W, 1, ' ', FG, BAR)
        cv.text(1, 0, 'Avarenthia Editor', GOLD, BAR)
        f = os.path.basename(self.room.file) if self.room.file else F.MINE
        cv.text(20, 0, f'{f} » {self.room.name}' + (' •' if self.room.dirty else ''), FG, BAR, maxw=37)
        for lab, x0, _x1, _a in self._top_buttons():
            k, word = lab.split(' ')
            greyed = word == 'Save' and not self.can_save()
            cv.text(x0, 0, k, scale(GOLD, .5) if greyed else GOLD, BAR)
            cv.text(x0 + len(k) + 1, 0, word, DIM if greyed else FG, BAR)

    def render_bar(self, cv):
        for lab, x0, _x1, _a in self._bar_buttons():
            k, word = lab.split(' ')
            cv.text(x0, 1, k, GOLD, BG)
            cv.text(x0 + len(k) + 1, 1, word, FG, BG)

    def render_left(self, cv):
        cv.fill(0, 1, 24, H - 2, ' ', FG, PANEL)
        cv.frame(0, 1, 24, len(TOOLS) + 3, LINE, PANEL, 'Tools', GOLD)
        for i, (k, lab) in enumerate(TOOLS):
            on = lab == self.tool
            bg = SEL if on else PANEL
            cv.fill(1, 2 + i, 22, 1, ' ', FG, bg)
            cv.text(2, 2 + i, k.upper(), GOLD, bg)
            cv.text(4, 2 + i, lab, GOLD if on else FG, bg)
        cv.text(2, 2 + len(TOOLS), 'Ctrl+Z undo · Ctrl+Y', DIM, PANEL)
        cv.frame(0, PAL_Y0 - 1, 24, H - PAL_Y0, LINE, PANEL, 'Palette', GOLD)
        lines = self._pal_lines()[self.pal_scroll[self._pal_key()]:]
        pick = self.pick[self._pal_key()] or Item('none')
        for i, (kind, it) in enumerate(lines[:PAL_Y1 - PAL_Y0]):
            y = PAL_Y0 + i
            if kind == 'head':
                cv.text(2, y, it, DIM, PANEL, maxw=21)
            elif kind == 'item':
                on = it.kind == pick.kind and it.ch == pick.ch and it.name == pick.name and it.act == pick.act
                bg = SEL if on else PANEL
                cv.fill(1, y, 22, 1, ' ', FG, bg)
                t = it.tile() if it.kind in ('sign', 'thing') else None
                if it.kind == 'sign' and it.ch == ' ':
                    cv.put(2, y, '·', DIM, ROCK)
                elif it.kind == 'spot':
                    ch, fg = self.spot_look(it.ch)
                    cv.put(2, y, ch, fg, bg)
                elif it.kind == 'mark':
                    cv.put(2, y, it.ch, GOLD, bg)
                elif it.kind == 'group':
                    cv.put(2, y, it.ch, (120, 200, 220), (16, 34, 40))
                elif t:
                    cv.put(2, y, t.ch, t.fg, t.bg or bg)
                cv.text(4, y, it.label[:19], GOLD if on else FG, bg)
        if len(lines) > PAL_Y1 - PAL_Y0:
            cv.text(2, PAL_Y1, '▼ wheel: more', DIM, PANEL)

    def render_ruler(self, cv):
        z = self.zoom
        for i in range(AW // z):
            n = self.view[0] + i
            ch, col = (str(n % 10), DIM) if n % 5 == 0 else ('·', scale(DIM, .5))
            cv.put(AX + i * z, AY - 1, ch, col, BG)
        for j in range(AH // z):
            n = self.view[1] + j
            if n % 5 == 0:
                cv.text(AX - 3, AY + j * z, f'{n:>2}'[-2:], DIM, BG)

    def render_drawing(self, cv, vw, vh, cursor=True):
        """The drawing as the view shows it, on cv from 0, 0 (vw x vh cells)."""
        r = self.room
        bad = {c for ok, _m, cells in self.problems() if ok is False for c in cells}
        preview = {}
        if self.drag and self.drag[0] in ('line', 'rect') and len(self.drag) > 2:
            a, b = self.drag[1], self.drag[2]
            cells = T.line_cells(a, b) if self.drag[0] == 'line' else T.rect_cells(a, b, self.drag[3])
            ch = self._preview_sign()
            preview = {c: ch for c in cells if r.inb(*c)}
        if self.pasting and self.clip and self.hover:
            preview.update({(self.hover[0] + dx, self.hover[1] + dy): ch for (dx, dy), ch in self.clip.items()
                            if r.inb(self.hover[0] + dx, self.hover[1] + dy)})
        inside = {(x, y) for y in range(r.h) for x in range(r.w) if r.get(x, y) not in " #+'"}
        for j in range(vh):
            for i in range(vw):
                x, y = self.view[0] + i, self.view[1] + j
                c = (x, y)
                ch = preview.get(c, r.get(x, y))
                if not r.inb(x, y):
                    if any((x + dx, y + dy) in inside for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                        cv.put(i, j, '#', scale(D.TILES[D.WALL].fg, .55), (26, 23, 20))
                    else:
                        cv.put(i, j, ' ', FG, OUTSIDE)
                elif ch == ' ':
                    near = any((x + dx, y + dy) in inside for dx in (-1, 0, 1) for dy in (-1, 0, 1))
                    if near:
                        cv.put(i, j, '#', scale(D.TILES[D.WALL].fg, .55), (26, 23, 20))
                    else:
                        cv.put(i, j, '·' if (x % 2 == 0 and y % 2 == 0) else ' ', (44, 40, 36), ROCK)
                elif ch in r.subst:
                    dim = .45 if self.layer in ('Creatures', 'Events') else 1
                    cv.put(i, j, ch, scale((120, 200, 220), dim), scale((16, 34, 40), dim))
                else:
                    t = _tile(ch, r.things)
                    if t is None:
                        cv.put(i, j, '?', BAD, WARN_BG)
                    else:
                        fg, bg = t.fg, t.bg or (20, 18, 16)
                        if self.layer == 'Ground' and not _is_ground(ch):
                            fg = scale(fg, .7)
                        elif self.layer in ('Creatures', 'Events'):
                            fg, bg = scale(fg, .45), scale(bg, .6)
                        if self.layer == 'Events' and ch in r.things:
                            on = self.ev_sel is not None and self.ev_sel < len(r.events) and \
                                r.events[self.ev_sel]['at'] == ch
                            cv.put(i, j, ch, (255, 220, 120) if on else GOLD, (70, 50, 16) if on else (40, 30, 12))
                        else:
                            cv.put(i, j, t.ch, fg, bg)
                if ch == "'":                       # a door the game may use: a dim door
                    cv.put(i, j, '+', scale(D.TILES[D.DOOR].fg, .55), (20, 18, 16))
                if c in r.spots and ch not in " #+'":
                    sch, sfg = self.spot_look(r.spots[c])
                    cv.put(i, j, sch, sfg if self.layer == 'Creatures' else scale(sfg, .6), None)
                if c in self.dressed:
                    cv.put_bg(i, j, (40, 70, 34))
                if c in bad:
                    cv.put_bg(i, j, WARN_BG)
                if self.sel and _in_rect(c, *self.sel):
                    cv.put_bg(i, j, (60, 60, 90))
        if self.layer == 'Events':
            LY.draw_wires(cv, self, vw, vh, GOLD)
        # the size handles
        for (hx, hy) in ((r.w, r.h), (r.w, r.h // 2), (r.w // 2, r.h)):
            i, j = hx - self.view[0], hy - self.view[1]
            if 0 <= i < vw and 0 <= j < vh:
                cv.put(i, j, '◘', GOLD, (60, 46, 20))
        if cursor and self.hover and not self.drag and not self.dialog:
            i, j = self.hover[0] - self.view[0], self.hover[1] - self.view[1]
            if 0 <= i < vw and 0 <= j < vh and r.inb(*self.hover):
                cv.put_bg(i, j, (80, 64, 40))

    def _preview_sign(self):
        it = self.pick[self.layer]
        if it.kind == 'sign':
            return it.ch
        return self.room.letter_for(it.name, it.act) or '?'

    def render_right(self, cv):
        r = self.room
        x = RX
        cv.fill(x, 1, W - x, H - 2, ' ', FG, PANEL)
        cv.frame(x, 1, W - x, 22, LINE, PANEL, 'The piece', GOLD)
        labels = {'name': 'Name', 'part': 'Part', 'kinds': 'Suits', 'depth': 'From level', 'weight': 'How often',
                  'gate': 'Way in', 'doors': 'Doors open', 'shape': 'Shape', 'size': 'Size'}
        for name, y in self._field_rows():
            if name.startswith('mood'):
                continue
            cv.text(x + 2, y, labels[name], DIM, PANEL)
            typing = self.field and self.field[0] == name
            val = self.field[1] + '_' if typing else self.field_value(name)
            bg = SEL if typing else FIELD
            cv.fill(x + 13, y, W - x - 15, 1, ' ', FG, bg)
            cv.text(x + 13, y, val[-(W - x - 15):] if typing else val[:W - x - 15], GOLD if name == 'size' else FG, bg)
            if name in ('part', 'gate', 'kinds', 'doors'):
                cv.put(W - 3, y, '▼', DIM, bg)
        cv.text(x + 2, 11, 'MOOD LINES', DIM, PANEL)
        for name, y in self._field_rows():
            if not name.startswith('mood'):
                continue
            typing = self.field and self.field[0] == name
            if name == 'mood+':
                if typing:
                    cv.wrap(x + 2, y, W - x - 4, self.field[1] + '_', FG, SEL, 3)
                elif y < 22:
                    cv.text(x + 2, y, '+ a mood line', GOLD, PANEL)
                continue
            i = int(name[4:])
            s = (self.field[1] + '_') if typing else '"' + r.moods[i] + '"'
            cv.wrap(x + 2, y, W - x - 4, s, FG, SEL if typing else PANEL, 4)
        cv.frame(x, 23, W - x, 7, LINE, PANEL, 'Layers', GOLD)
        counts = {'Creatures': len(r.spots), 'Events': len(r.events)}
        for i, lay in enumerate(LAYERS):
            on = lay == self.layer
            bg = SEL if on else PANEL
            cv.fill(x + 1, 24 + i, W - x - 2, 1, ' ', FG, bg)
            cv.text(x + 2, 24 + i, '√', GOOD, bg)
            cv.text(x + 4, 24 + i, lay, GOLD if on else FG, bg)
            if counts.get(lay):
                cv.text(x + 15, 24 + i, str(counts[lay]), DIM, bg)
        cv.text(x + 2, 28, 'Tab: next layer', DIM, PANEL)
        cv.frame(x, 30, W - x, H - 32, LINE, PANEL, 'Will the game take it?', GOLD)
        for ok, msg, cells, y, n in self._check_rows():
            sign, col = ('√', GOOD) if ok else ('×', BAD) if ok is False else ('!', GOLD)
            cv.put(x + 2, y, sign, col, PANEL)
            cv.wrap(x + 4, y, W - x - 6, msg, FG if ok else BAD if ok is False else GOLD, PANEL, n)

    def _check_rows(self):
        out, y = [], 31
        for ok, msg, cells in self.problems():
            n = len(wrap_text(msg, W - RX - 6))
            if y + n > H - 3:
                break
            out.append((ok, msg, cells, y, n))
            y += n
        return out

    def render_bottom(self, cv):
        cv.frame(AX - 1, AY + AH + 1, AW + 2, H - AY - AH - 2, LINE, BG,
                 'Events' if self.layer == 'Events' and not self.field else 'Hints', DIM)
        y = AY + AH + 2
        if self.field:
            lines = ['Type, then Enter. Esc leaves it as it was.']
            if self.field[0].startswith('mood'):
                lines.append('A mood line is what the messages say the first time you step in. Empty it to take it '
                             'away.')
        elif self.pasting:
            lines = ['Click where the top left corner of what you copied goes. Esc stops.']
        elif self.tool == 'Select':
            lines = ['Drag to choose. Ctrl+C copies, Ctrl+X cuts, Ctrl+V sets it down, Delete makes it rock.']
        elif self.layer == 'Events':
            return self.render_events(cv)
        elif self.tool == 'Variety':
            lines = ['Paint cells with a group: in every world the game picks one of its signs, by weight.',
                     'Right mouse on a group in the palette changes its signs and weights.']
        elif self.layer == 'Creatures':
            more = self.room.more
            lines = ['Left mouse sets the picked creature down, right mouse takes it away. ? is one of the place; '
                     '1-9 one from your own lists.',
                     'And more: ' + (f'{more[0]}, {more[1]} to {more[2]}, where there is room.' if more else
                                     'none. Set it under + lists, and more.')]
        elif self.layer == 'Things':
            lines = ['A telling thing does something when you walk into it; pick what it does under TELLING THINGS. '
                     'MORE has every tile of the game.', HINTS[0]]
        else:
            lines = HINTS
        for s in lines:
            n = cv.wrap(AX + 1, y, AW - 2, s, DIM, BG, 3)
            y += n + 1
            if y >= H - 2:
                break

    def render_events(self, cv):
        y0 = AY + AH + 2
        cols = {'n': DIM, 'k': DIM, 'v': FG, 'g': GOLD, 'b': BAD}
        for x, y, s, kind, _act, i in self.event_rows(AX + 1, y0, AW - 2, H - AY - AH - 4):
            on = i == self.ev_sel and i >= 0
            col = cols[kind]
            if on and kind == 'n':
                col = GOLD
            cv.text(x, y, s, col, SEL if (on and kind == 'v') else BG)
        if not self.room.events:
            cv.wrap(AX + 1, y0 + 2, AW - 2, 'Click a thing to give it an event, click the floor to make a mark, or '
                    'drag from one mark to another for a wire.', DIM, BG, 3)

    def render_status(self, cv):
        cv.fill(0, H - 1, W, 1, ' ', FG, BAR)
        if self.msg:
            cv.text(1, H - 1, self.msg, BAD if self.msg_bad else GOLD, BAR, maxw=W - 2)
            return
        bits = []
        if self.hover and self.room.inb(*self.hover):
            ch = self.room.get(*self.hover)
            t = _tile(ch, self.room.things)
            bits.append(f'x {self.hover[0]} y {self.hover[1]}')
            bits.append('rock' if ch == ' ' else t.name if t else f'variety group {ch}' if ch in self.room.subst else '?')
            what = self.room.spots.get(tuple(self.hover))
            if what:
                bits.append('one of the place' if what == '?' else f'one of {what[5:]}' if what.startswith('list:')
                            else D.MONSTERS.get(what, {}).get('name', what))
        bits += [self.tool, f'layer {self.layer}', f'zoom {self.zoom}', f'{self.room.w} x {self.room.h}',
                 'not saved' if self.room.dirty else 'saved']
        cv.text(1, H - 1, ' · '.join(bits), DIM, BAR, maxw=W - 2)

    def render_open(self, cv):
        st = self.dialog[1]
        cv.frame(4, 5, 102, 50, GOLD, PANEL, 'Ctrl+O: open a piece', GOLD)
        cv.text(6, 7, 'FILES', DIM, PANEL)
        cv.text(34, 7, 'PIECES IN IT', DIM, PANEL)
        for i, (label, _p) in enumerate(st['files'][:44]):
            on = i == st['file']
            bg = SEL if on else PANEL
            cv.fill(5, 8 + i, 28, 1, ' ', FG, bg)
            cv.text(6, 8 + i, label, GOLD if on else FG, bg, maxw=26)
        if st.get('error'):
            cv.wrap(34, 8, 70, st['error'], BAD, PANEL, 4)
        rooms = st['rooms'][st.get('scroll', 0):]
        for i, r in enumerate(rooms[:44]):
            cv.text(34, 8 + i, r.name, FG, PANEL, maxw=24)
            extra = f"{r.part} · {' '.join(r.kinds)} · {r.w} x {r.h}"
            cv.text(60, 8 + i, extra, DIM, PANEL, maxw=44)
        if self.room.dirty:
            cv.text(6, 53, f'Your changes to {self.room.name} are not saved; opening another piece drops them.',
                    BAD, PANEL, maxw=96)
        else:
            cv.text(6, 53, 'Click a piece to open it. Up and Down: the files. Esc: back.', DIM, PANEL)

    def render_new(self, cv):
        st = self.dialog[1]
        nx, ny = 28, 14
        cv.frame(nx, ny, 54, 18, GOLD, PANEL, 'Ctrl+N: a new piece', GOLD)
        cv.text(nx + 2, ny + 2, 'WHAT IS IT?', DIM, PANEL)
        texts = {'arrival': ('An arrival room', 'the stairs from above'), 'middle': ('A theme room', 'one telling thing'),
                 'bottom': ('A bottom room', 'the boss, the way down')}
        for i, part in enumerate(PARTS[1:]):
            on = st['part'] == part
            bg = SEL if on else PANEL
            cv.fill(nx + 1, ny + 3 + i, 52, 1, ' ', FG, bg)
            cv.text(nx + 2, ny + 3 + i, '►' if on else ' ', GOLD, bg)
            cv.text(nx + 4, ny + 3 + i, texts[part][0], GOLD if on else FG, bg)
            cv.text(nx + 22, ny + 3 + i, texts[part][1], DIM, bg)
        cv.text(nx + 2, ny + 8, 'FOR WHICH PLACES?', DIM, PANEL)
        xx = nx + 2
        for k in KINDS:
            on = k in st['kinds']
            cv.text(xx, ny + 9, ('■ ' if on else '□ ') + k, GOLD if on else FG, PANEL)
            xx += len(k) + 4
        cv.text(nx + 2, ny + 11, 'SIZE TO START WITH', DIM, PANEL)
        typing = st.get('typing')
        cv.fill(nx + 2, ny + 12, 10, 1, ' ', FG, SEL if typing else FIELD)
        cv.text(nx + 2, ny + 12, st['size'] + ('_' if typing else ''), FG, SEL if typing else FIELD)
        cv.text(nx + 14, ny + 12, 'up to 40 x 30; you can change it later', DIM, PANEL)
        cv.text(nx + 2, ny + 15, 'Enter', GOLD, PANEL)
        cv.text(nx + 8, ny + 15, 'make it', FG, PANEL)
        cv.text(nx + 16, ny + 15, 'Esc', GOLD, PANEL)
        cv.text(nx + 20, ny + 15, 'back', FG, PANEL)

    def render_line(self, cv):
        st = self.dialog[1]
        cv.frame(20, 24, 70, 7, GOLD, PANEL, st['title'], GOLD)
        cv.fill(22, 26, 66, 1, ' ', FG, SEL)
        cv.text(22, 26, (st['text'] + '_')[-66:], FG, SEL)
        cv.text(22, 28, ' OK ', BG, GOLD)
        cv.text(28, 28, ' Back ', FG, SEL)
        cv.text(36, 28, 'or Enter, Esc', DIM, PANEL)

    def render_pick(self, cv):
        st = self.dialog[1]
        cv.frame(18, 5, 74, 50, GOLD, PANEL, st['title'], GOLD)
        opts = st['options'][st.get('scroll', 0):]
        for i, (label, _v) in enumerate(opts[:44]):
            cv.text(20, 8 + i, label[:70], FG, PANEL)
        if len(opts) > 44:
            cv.text(20, 52, 'wheel: more', DIM, PANEL)
        cv.text(20, 53, 'Click one. Esc: back.', DIM, PANEL)

    def render_lists(self, cv):
        st = self.dialog[1]
        r = self.room
        cv.frame(4, 5, 102, 50, GOLD, PANEL, 'My lists of creatures, and more', GOLD)
        cv.text(6, 7, 'MY LISTS (KEYS 1-9)', DIM, PANEL)
        names = list(r.lists)
        for i, n in enumerate(names):
            on = n == st.get('list')
            cv.fill(5, 8 + i, 25, 1, ' ', FG, SEL if on else PANEL)
            cv.text(6, 8 + i, f'{i + 1} {n}'[:23], GOLD if on else FG, SEL if on else PANEL)
        if len(names) < 9:
            cv.text(6, 8 + len(names), '+ a new list', GOLD, PANEL)
        cv.text(6, 47, 'AND MORE, WHERE THERE IS ROOM', DIM, PANEL)
        m = r.more
        cv.text(6, 48, (f'{m[0]}, {m[1]} to {m[2]}' if m else 'none')[:23], GOLD, PANEL)
        cur = st.get('list')
        cv.text(32, 7, 'IN THE LIST: LEFT +1, RIGHT -1', DIM, PANEL)
        if cur in r.lists:
            for i, (k, w) in enumerate(r.lists[cur][:40]):
                d = D.MONSTERS.get(k)
                cv.put(32, 8 + i, d['ch'] if d else '?', d['fg'] if d else BAD, PANEL)
                cv.text(34, 8 + i, (d['name'] if d else k)[:22], FG, PANEL)
                cv.text(58, 8 + i, f'{w:>3}', GOLD, PANEL)
            cv.text(64, 7, 'MAY LIVE HERE: CLICK TO ADD', DIM, PANEL)
            mons = LY.creatures_for(r.kinds)[st.get('scroll', 0):]
            for i, k in enumerate(mons[:44]):
                d = D.MONSTERS[k]
                cv.put(64, 8 + i, d['ch'], d['fg'], PANEL)
                cv.text(66, 8 + i, d['name'][:36], FG, PANEL)
        cv.text(6, 52, 'Right mouse on a list takes it away. Esc: back.', DIM, PANEL)
        cv.text(6, 53, 'Only kinds that may live in the place come; the others become one of the place.', DIM, PANEL)

    def render_variety(self, cv):
        st = self.dialog[1]
        g = st['group']
        opts = self.room.subst.get(g, [])
        h = len(opts) + len(self._variety_adds()) + 8
        cv.frame(28, 14, 56, h, GOLD, PANEL, f'Variety group {g}', GOLD)
        cv.text(30, 16, 'ONE OF THESE, BY WEIGHT: LEFT +1, RIGHT -1', DIM, PANEL)
        for i, (c, w) in enumerate(opts):
            cv.text(30, 18 + i, self._sign_name(c)[:40], FG, PANEL)
            cv.text(76, 18 + i, f'{w:>3}', GOLD, PANEL)
        for j, (label, _c) in enumerate(self._variety_adds()):
            cv.text(30, 19 + len(opts) + j, label[:52], GOLD, PANEL)
        cv.text(30, 14 + h - 2, 'Esc: back.', DIM, PANEL)

    def render_dress(self, cv):
        st = self.dialog[1]
        names = list(LY.DR.SETS)
        x0, y0 = 30, 16
        cv.frame(28, 13, 56, len(names) + 9, GOLD, PANEL, 'Ctrl+D: dress the room', GOLD)
        cv.text(x0, 14, 'SETS AND HOW FULL', DIM, PANEL)
        for i, n in enumerate(names):
            on = n in st['sets']
            cv.text(x0, y0 + i, ('■ ' if on else '□ ') + n, GOLD if on else FG, PANEL)
            if on:
                for k in range(5):
                    cv.put(x0 + 22 + k * 2, y0 + i, '■' if k < st['sets'][n] else '□', GOLD, PANEL)
        y = y0 + len(names) + 2
        cv.text(x0, y, 'N', GOLD, PANEL)
        cv.text(x0 + 2, y, 'Now', FG, PANEL)
        cv.text(x0 + 12, y, 'G', GOLD, PANEL)
        cv.text(x0 + 14, y, 'In the game', FG, PANEL)
        if st.get('laid'):
            cv.text(x0 + 30, y, 'R', GOLD, PANEL)
            cv.text(x0 + 32, y, 'Roll again', FG, PANEL)
        cv.text(x0, y + 1, 'Now draws it in, light green. In the game: anew in every world.', DIM, PANEL)

    def render_roll(self, cv):
        st = self.dialog[1]
        cv.frame(4, 5, 102, 50, GOLD, PANEL, 'Ctrl+R: as the game draws it', GOLD)
        for n, dr in enumerate(st['draws']):
            ox, oy = 6 + n * 50, 8
            for (x, y), ch in dr.items():
                if x >= 48 or y >= 44:
                    continue
                t = P.dressed_tile(ch)
                t = D.TILES[t] if t is not None else _tile(ch, self.room.things)
                if t is None:
                    cv.put(ox + x, oy + y, '?', BAD, PANEL)
                else:
                    cv.put(ox + x, oy + y, t.ch, t.fg, t.bg or (20, 18, 16))
            for (x, y), what in dr.spots.items():
                if x < 48 and y < 44:
                    ch, fg = self.spot_look(what)
                    cv.put(ox + x, oy + y, ch, fg, None)
        cv.text(6, 53, 'Turned, mirrored, variety picked and dressed, as in a world.', DIM, PANEL)
        cv.text(70, 53, ' Roll again (R) ', BG, GOLD)

    def render_kinds(self, cv):
        kx, ky = RX + 2, 5
        cv.frame(RX + 1, ky - 1, W - RX - 2, len(KINDS) + 6, GOLD, PANEL, 'Suits', GOLD)
        for i, k in enumerate(KINDS):
            on = k in self.room.kinds
            out = f'not:{k}' in self.room.kinds
            cv.text(kx, ky + i, ('■ ' if on else '× ' if out else '□ ') + k, GOLD if on else BAD if out else FG, PANEL)
        cv.text(kx, ky + len(KINDS) + 1, 'Done', GOLD, PANEL)
        cv.text(kx, ky + len(KINDS) + 3, 'right mouse: keep it out', DIM, PANEL)


def _in_rect(c, a, b):
    return min(a[0], b[0]) <= c[0] <= max(a[0], b[0]) and min(a[1], b[1]) <= c[1] <= max(a[1], b[1])


class _Offset:
    """A canvas seen from (ox, oy): what is drawn at 0, 0 lands there."""

    def __init__(self, cv, ox, oy):
        self.cv, self.ox, self.oy = cv, ox, oy

    def put(self, x, y, ch, fg=None, bg=None):
        self.cv.put(self.ox + x, self.oy + y, ch, fg, bg)

    def put_bg(self, x, y, bg):
        self.cv.put_bg(self.ox + x, self.oy + y, bg)
