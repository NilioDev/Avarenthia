"""Ctrl+G in the editor (round 55): the window that makes with a maker. The makers on the left in groups, what one
made in the middle (arrows move it, PgUp / PgDn go from floor to floor, drag a frame to take only a part), the
choices under it, R another, Enter takes it. With a rectangle selected in a whole place it makes a maker area instead:
the game fills that area anew in every world (generate.py, drawnplaces.fill_area)."""
import os

from .. import data as D
from . import files as F
from . import generate as G
from .model import PlaceDoc

BOX = (4, 5, 102, 50)
LX, LY, LWID, LROWS = 6, 7, 25, 46            # the list of makers
PX, PY, PW, PH = 33, 7, 71, 39               # the map
LAND_SIZES = ((80, 51), (120, 80), (160, 102))
DIM = (143, 133, 115)
FG = (221, 211, 189)
GOLD = (217, 165, 71)
BAD = (236, 106, 92)
PANEL = (22, 18, 15)
SEL = (60, 46, 30)
BG = (13, 11, 10)
FRAME = (52, 58, 96)
AREA_BG = (24, 30, 46)


class GenTools:
    gen_game = None                           # the Try world the makers run on, made or read once

    # ------------------------------------------------------------ opening
    def gen_dialog(self):
        area = None
        if self.place and self.sel:
            (ax, ay), (bx, by) = self.sel
            x0, y0 = max(0, min(ax, bx)), max(0, min(ay, by))
            x1, y1 = min(self.room.w - 1, max(ax, bx)), min(self.room.h - 1, max(ay, by))
            area = (x0, y0, x1 - x0 + 1, y1 - y0 + 1)
        if self.gen_game is None:
            from . import trying as TR
            self.say('Making a small test world for the makers, once (it is kept)...')
            g = TR.world(self.say)
            g.hook()
            GenTools.gen_game = g
        ms = [m for m in G.makers(self.gen_game) if m.area or not area]
        if area:
            ms = [m for m in ms if m.how in ('area', 'land')]
        st = {'makers': ms, 'i': 0, 'n': 0, 'floors': 1, 'state': 'as made', 'creatures': 'as ?', 'dressing': True,
              'land': 0, 'made': None, 'error': '', 'floor': 0, 'pan': [0, 0], 'frame': None, 'drag': None,
              'scroll': 0, 'area': area}
        self.dialog = ('gen', st)
        self.gen_make()

    def gen_maker(self):
        st = self.dialog[1]
        return st['makers'][st['i']] if st['makers'] else None

    def gen_make(self):
        st = self.dialog[1]
        mk = self.gen_maker()
        st['made'], st['error'], st['frame'], st['floor'], st['pan'] = None, '', None, 0, [0, 0]
        if mk is None:
            st['error'] = 'No maker here.'
            return
        try:
            if st['area']:
                m = G.area_preview(self.gen_game, mk.id, st['area'][2], st['area'][3], st['n'])
                if m is None:
                    raise ValueError(f'the {mk.label} maker cannot fill this area')
                st['made'] = G.Made([('area', m)], None, f'{mk.label} in the area')
            else:
                st['made'] = G.make(self.gen_game, mk, st['n'], st['floors'], st['state'], LAND_SIZES[st['land']])
        except ValueError as e:
            st['error'] = str(e)
            return
        fl = st['made'].floors
        st['floor'] = next((i for i, (n, _m) in enumerate(fl) if n == 'ground'), 0)

    # ------------------------------------------------------------ the choices under the map
    def gen_buttons(self):
        """[(x, y, text, what)] of the choices and buttons, as drawn."""
        st = self.dialog[1]
        mk = self.gen_maker()
        out = []
        x, y = PX, PY + PH + 3
        row = []
        if st['area']:
            row = []
        else:
            if mk and mk.floors > 1:
                row.append((f' Floors: {st["floors"]} ', 'floors'))
            if mk and mk.states:
                row.append((f' State: {st["state"]} ', 'state'))
            if mk and mk.how == 'land':
                row.append((' Size: %d x %d ' % LAND_SIZES[st['land']], 'land'))
            row.append((f' Creatures: {st["creatures"]} ', 'creatures'))
            row.append((f' Dressing: {"on" if st["dressing"] else "off"} ', 'dressing'))
        for text, what in row:
            out.append((x, y, text, what))
            x += len(text) + 1
        y += 2
        x = PX
        take = ' Make the area (Enter) ' if st['area'] else ' Take it (Enter) '
        for text, what in ((' Another (R) ', 'again'), (take, 'take')) + \
                (((' The whole map ', 'whole'),) if st['frame'] else ()):
            out.append((x, y, text, what))
            x += len(text) + 2
        return out

    def gen_choose(self, what, back=False):
        st = self.dialog[1]
        mk = self.gen_maker()
        step = -1 if back else 1
        if what == 'floors':
            st['floors'] = (st['floors'] - 1 + step) % mk.floors + 1
            self.gen_make()
        elif what == 'state':
            st['state'] = G.STATES[(G.STATES.index(st['state']) + step) % len(G.STATES)]
            self.gen_make()
        elif what == 'land':
            st['land'] = (st['land'] + step) % len(LAND_SIZES)
            self.gen_make()
        elif what == 'creatures':
            st['creatures'] = G.CREATURES[(G.CREATURES.index(st['creatures']) + step) % len(G.CREATURES)]
        elif what == 'dressing':
            st['dressing'] = not st['dressing']
        elif what == 'again':
            st['n'] += 1
            self.gen_make()
        elif what == 'take':
            self.gen_take()
        elif what == 'whole':
            st['frame'] = None

    # ------------------------------------------------------------ the list
    def gen_lines(self):
        """The list's lines: (text, index of the maker or None for a group's name)."""
        st = self.dialog[1]
        out, group = [], None
        for i, mk in enumerate(st['makers']):
            if mk.group != group:
                group = mk.group
                if out:
                    out.append(('', None))
                out.append((group, None))
            out.append((mk.label, i))
        return out

    # ------------------------------------------------------------ input
    def gen_key(self, tok, shift):
        st = self.dialog[1]
        if tok == 'esc':
            self.dialog = None
        elif tok in ('enter', 'np_enter'):
            self.gen_take()
        elif tok == 'r':
            self.gen_choose('again')
        elif tok in ('pageup', 'pagedown') and st['made']:
            st['floor'] = max(0, min(len(st['made'].floors) - 1, st['floor'] + (-1 if tok == 'pageup' else 1)))
        elif tok in ('left', 'right', 'up', 'down'):
            dx, dy = {'left': (-1, 0), 'right': (1, 0), 'up': (0, -1), 'down': (0, 1)}[tok]
            st['pan'][0] += dx * (16 if shift else 4)
            st['pan'][1] += dy * (16 if shift else 4)
            self.gen_clamp()

    def gen_clamp(self):
        st = self.dialog[1]
        m = self.gen_map()
        if m is None:
            st['pan'] = [0, 0]
            return
        st['pan'][0] = max(0, min(max(0, m.w - PW), st['pan'][0]))
        st['pan'][1] = max(0, min(max(0, m.h - PH), st['pan'][1]))

    def gen_map(self):
        st = self.dialog[1]
        if not st['made']:
            return None
        return st['made'].floors[st['floor']][1]

    def gen_cell(self, x, y):
        st = self.dialog[1]
        m = self.gen_map()
        if m is None or not (PX <= x < PX + PW and PY <= y < PY + PH):
            return None
        c = (st['pan'][0] + int(x - PX), st['pan'][1] + int(y - PY))
        return c if m.inb(*c) else None

    def gen_mouse(self, kind, x, y, button):
        st = self.dialog[1]
        c = self.gen_cell(x, y)
        if kind == 'move':
            if st['drag'] is not None and c is not None:
                st['frame'] = (st['drag'], c)
            return
        if kind == 'up':
            if st['drag'] is not None and (c is None or c == st['drag']) and st['frame'] and \
                    st['frame'][0] == st['frame'][1]:
                st['frame'] = None
            st['drag'] = None
            return
        bx, by, bw, bh = BOX
        if not (bx <= x < bx + bw and by <= y < by + bh):
            self.dialog = None
            return
        if c is not None and not st['area']:
            st['drag'] = c
            st['frame'] = (c, c)
            return
        yy = int(y)
        if LX <= x < LX + LWID and LY <= yy < LY + LROWS:
            lines = self.gen_lines()
            k = yy - LY + st['scroll']
            if 0 <= k < len(lines) and lines[k][1] is not None and lines[k][1] != st['i']:
                st['i'], st['n'], st['floors'], st['state'] = lines[k][1], 0, 1, 'as made'
                st['floors'] = min(self.gen_maker().floors, 3)
                self.gen_make()
            return
        for bx0, by0, text, what in self.gen_buttons():
            if yy == by0 and bx0 <= x < bx0 + len(text):
                self.gen_choose(what, button == 3)
                return

    # ------------------------------------------------------------ taking it
    def gen_take(self):
        st = self.dialog[1]
        mk = self.gen_maker()
        if not st['made']:
            self.say(st['error'] or 'Nothing made yet.', True)
            return
        if st['area']:
            r = self.room
            r.change()
            r.makers.append((mk.id, st['area']))
            self.dialog = None
            self.sel = None
            x0, y0, w, h = st['area']
            free = sum(r.get(x, y) == ' ' for y in range(y0, y0 + h) for x in range(x0, x0 + w))
            self.say(f'A maker area: {mk.label}, laid anew in every world.' if free else
                     'A maker area, but all of it is drawn: rub out where the maker may lay.', not free)
            return
        opts = {'creatures': st['creatures'], 'dressing': st['dressing']}
        frame = None
        if st['frame']:
            frame = st['frame']
        d, line = G.to_drawing(st['made'], opts, frame, self.gen_name(mk.label))
        self.dialog = None
        if isinstance(d, PlaceDoc):
            d.file = os.path.join(F.home(), F.MY_PLACES)
            for f in d.floors:
                f.file = d.file
            self.open_place(d)
            self.say(line)
        else:
            d.file = os.path.join(F.home(), F.MINE)
            d.dirty = True
            self.room, self.saved_name, self.place = d, d.name, None
            self.center()
            self.say(line)

    def gen_name(self, label):
        try:
            from .. import drawnplaces as DP
            names = {q.name for q in F.game_pieces_cached()} | {q.name for q in self._mine()} | \
                {q.name for q in DP.load()}
        except Exception:
            names = set()
        name, n = f'made {label}', 1
        while name in names:
            n += 1
            name = f'made {label} {n}'
        return name

    # ------------------------------------------------------------ drawing it
    def render_gen(self, cv):
        st = self.dialog[1]
        title = 'Ctrl+G: a maker area, filled anew in every world' if st['area'] else 'Ctrl+G: make with a maker'
        cv.frame(*BOX, GOLD, PANEL, title, GOLD)
        lines = self.gen_lines()
        st['scroll'] = max(0, min(max(0, len(lines) - LROWS), st['scroll']))
        for k in range(LROWS):
            j = k + st['scroll']
            if j >= len(lines):
                break
            text, i = lines[j]
            if i is None:
                cv.text(LX, LY + k, text[:LWID], GOLD, PANEL)
            else:
                on = i == st['i']
                cv.fill(LX, LY + k, LWID, 1, ' ', FG, SEL if on else PANEL)
                cv.text(LX + 1, LY + k, text[:LWID - 1], GOLD if on else FG, SEL if on else PANEL)
        m = self.gen_map()
        if m is None:
            cv.text(PX, PY + 2, st['error'] or 'Nothing made.', BAD, PANEL)
        else:
            self.render_gen_map(cv, m)
        made = st['made']
        if made:
            names = [n for n, _m in made.floors]
            cv.text(PX, PY + PH + 1, f'{made.line}. {m.w} x {m.h}.', DIM, PANEL)
            if len(names) > 1:
                cv.text(PX, PY + PH + 2, f'Floor {names[st["floor"]]} of {len(names)}: PgUp, PgDn.', DIM, PANEL)
        for x, y, text, what in self.gen_buttons():
            hot = what in ('take', 'again', 'whole')
            cv.text(x, y, text, BG if hot else FG, GOLD if what == 'take' else (SEL if not hot else (120, 96, 60)))
        hint = 'Arrows move the map; drag a frame on it to take a part.' if not st['area'] else \
            'Laid where nothing is drawn, joined to the rest.'
        if st['error'] and m is not None:
            hint = st['error']
        cv.text(PX, PY + PH + 7, hint, BAD if st['error'] else DIM, PANEL)

    def render_gen_map(self, cv, m):
        st = self.dialog[1]
        ox, oy = st['pan']
        fr = None
        if st['frame']:
            (ax, ay), (bx, by) = st['frame']
            fr = (min(ax, bx), min(ay, by), max(ax, bx), max(ay, by))
        mons = {} if st['creatures'] == 'none' else {(q.x, q.y): q for q in m.mons}
        for j in range(PH):
            for i in range(PW):
                x, y = ox + i, oy + j
                if not m.inb(x, y):
                    cv.put(PX + i, PY + j, ' ', FG, (16, 14, 13))
                    continue
                t = D.TILES[m.tile(x, y)]
                bg = t.bg or (20, 18, 16)
                if fr and fr[0] <= x <= fr[2] and fr[1] <= y <= fr[3]:
                    bg = FRAME
                q = mons.get((x, y))
                if q is not None:
                    cv.put(PX + i, PY + j, q.ch, q.fg, bg)
                else:
                    cv.put(PX + i, PY + j, t.ch, t.fg, bg)


def area_cells(room):
    """{cell: maker} of a floor's maker areas (the editor shades them)."""
    out = {}
    for what, (x0, y0, w, h) in getattr(room, 'makers', []):
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                out[(x, y)] = what
    return out


def drop_areas(room, a, b):
    """The maker areas that lie in the rectangle a-b are taken away; how many."""
    x0, x1 = min(a[0], b[0]), max(a[0], b[0])
    y0, y1 = min(a[1], b[1]), max(a[1], b[1])
    keep = [(w, r) for w, r in room.makers
            if not (x0 <= r[0] <= x1 and y0 <= r[1] <= y1 and r[0] + r[2] - 1 <= x1 and r[1] + r[3] - 1 <= y1)]
    n = len(room.makers) - len(keep)
    room.makers = keep
    return n
