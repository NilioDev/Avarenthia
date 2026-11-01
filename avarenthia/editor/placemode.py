"""Whole places in the editor (round C, mockup 6): a map drawn whole, its floors as tabs (PgUp / PgDn), "In the
world" on the right, people who live there and fixed finds on the Creatures layer, and the check of
drawnplaces.problems. The floor being drawn is the editor's room (a Room with whole=True); the place is self.place."""
import os
import re

from .. import data as D
from .. import drawnplaces as DP
from . import files as F
from .model import PlaceDoc, tile_of

FOUNDS = (['map'], ['rumour'], ['book'], ['map', 'rumour'], ['map', 'book'], ['rumour', 'book'],
          ['map', 'rumour', 'book'])
LABELS = {'p_name': 'Name', 'p_size': 'Size', 'p_sign': 'Sign', 'p_land': 'Terrain', 'p_road': 'Road',
          'p_level': 'Level', 'p_how': 'How many', 'p_found': 'Found by', 'p_round': 'Land',
          'p_look': 'Look', 'p_rumour': 'Rumour', 'p_book': 'Book', 'p_mood': 'Mood'}
CYCLES = ('p_size', 'p_road', 'p_level', 'p_how', 'p_found', 'p_round')
LONG = ('p_look', 'p_rumour', 'p_book', 'p_mood')
FLOOR_Y0, FLOOR_ROWS = 16, 5


class PlaceTools:
    place = None

    # ------------------------------------------------------------ opening and floors
    def open_place(self, doc, floor=None):
        self.place = doc
        self.room = doc.floor(floor or 'ground') or doc.floors[0]
        self.saved_name = doc.name
        self.offer_place = False
        self.center()

    def go_floor(self, step):
        """PgUp (step -1) goes a floor up, PgDn (+1) a floor down."""
        order = self.place.order()
        i = order.index(self.room) + step
        if 0 <= i < len(order):
            self.room = order[i]
            self.say(f'The floor {self.room.name}.')
        else:
            self.say('No floor ' + ('above' if step < 0 else 'below') + ' this one: + up or + down makes one.')

    def add_floor(self, way):
        """A new floor above the top one or below the bottom one, with a small room round the twin stair."""
        d = self.place
        order = d.order()
        name = d.next_name(way)
        near = order[0] if way == 'up' else order[-1]
        want = '<' if way == 'up' else '>'
        f = d.add_floor(name)
        at = next(((x, y) for y in range(near.h) for x in range(near.w) if near.get(x, y) == want), None)
        cx, cy = at or (d.size[0] // 2, d.size[1] // 2)
        cx, cy = max(3, min(d.size[0] - 4, cx)), max(2, min(d.size[1] - 3, cy))
        for y in range(cy - 2, cy + 3):
            for x in range(cx - 3, cx + 4):
                f.set(x, y, '.')
        f.set(cx, cy, '>' if way == 'up' else '<')
        f.undo.clear()
        d.dirty = True
        self.room = f
        self.say(f'A new floor, {name}.' + ('' if at else f' Draw {want} on {near.name} for its twin stair.'))

    def remove_floor(self, name):
        d = self.place
        f = d.floor(name)
        if f is None or name == 'ground':
            return
        d.floors.remove(f)
        d.dirty = True
        if self.room is f:
            self.room = d.floor('ground') or d.floors[0]
        self.say(f'The floor {name} is gone (Save to keep it so).')

    def make_whole(self):
        """The room as the ground floor of a new whole place, its rock wall drawn as wall."""
        r = self.room
        size = next((s for s in DP.SIZES if s[0] >= r.w + 4 and s[1] >= r.h + 4), DP.SIZES[-1])
        d = PlaceDoc(r.name, size)
        d.file = os.path.join(F.home(), F.MY_PLACES)
        g = d.add_floor('ground')
        g.file = d.file
        ox, oy = (size[0] - r.w) // 2, (size[1] - r.h) // 2
        inside = {(x, y) for y in range(r.h) for x in range(r.w) if r.get(x, y) not in ' #'}
        for y in range(-1, r.h + 1):
            for x in range(-1, r.w + 1):
                ch = r.get(x, y)
                if ch == ' ' and any((x + a, y + b) in inside for a in (-1, 0, 1) for b in (-1, 0, 1)):
                    ch = '#'
                if ch != ' ':
                    g.set(ox + x, oy + y, ch)
        g.things, g.subst, g.events = dict(r.things), dict(r.subst), list(r.events)
        g.spots = {(x + ox, y + oy): v for (x, y), v in r.spots.items()}
        g.lists, g.more, g.switches, g.counters = r.lists, r.more, r.switches, r.counters
        g.moods = list(r.moods)
        d.dirty = True
        self.open_place(d)
        self.say(f'{d.name} is now a whole place of {size[0]} x {size[1]}: the room is its ground floor.')

    # ------------------------------------------------------------ the fields on the right
    def place_rows(self):
        return [(n, y) for y, n in enumerate(('p_name', 'p_size', 'p_sign', 'p_land', 'p_road', 'p_level', 'p_how',
                                              'p_found', 'p_round', 'p_look', 'p_rumour', 'p_book', 'p_mood'), 2)]

    def place_value(self, name):
        d, w = self.place, self.place.world
        return {'p_name': d.name, 'p_size': f'{d.size[0]} x {d.size[1]}', 'p_sign': f'{d.sign} #%02x%02x%02x' % d.fg,
                'p_land': ' '.join(w['land']) or 'any', 'p_road': w['road'], 'p_level': str(w['level']),
                'p_how': 'every world' if w['how'] == 'one' else 'half the worlds',
                'p_found': ', '.join(w['found']), 'p_round': 'as the world has it' if d.land == 'fitted' else 'as drawn',
                'p_look': d.look, 'p_rumour': d.rumour, 'p_book': d.book,
                'p_mood': self.room.moods[0] if self.room.moods else ''}.get(name, '')

    def place_click(self, name, button):
        d, w = self.place, self.place.world
        step = 1 if button == 1 else -1
        if name not in CYCLES:
            self.field = (name, self.place_value(name))
            return
        d.dirty = True
        if name == 'p_size':
            i = DP.SIZES.index(d.size) if d.size in DP.SIZES else 0
            new = DP.SIZES[(i + step) % len(DP.SIZES)]
            if any(f.get(x, y) != ' ' for f in d.floors for y in range(f.h) for x in range(f.w)
                   if x >= new[0] or y >= new[1]):
                self.say(f'{new[0]} x {new[1]} would cut off what is drawn: make the drawing smaller first.', True)
                return
            d.set_size(new)
        elif name == 'p_road':
            w['road'] = DP.ROADS[(DP.ROADS.index(w['road']) + step) % 3] if w['road'] in DP.ROADS else 'any'
        elif name == 'p_level':
            w['level'] = (w['level'] - 1 + step) % 5 + 1
        elif name == 'p_how':
            w['how'] = 'half' if w['how'] == 'one' else 'one'
        elif name == 'p_found':
            i = FOUNDS.index(w['found']) if w['found'] in FOUNDS else -1
            w['found'] = list(FOUNDS[(i + step) % len(FOUNDS)])
        elif name == 'p_round':
            d.land = 'drawn' if d.land == 'fitted' else 'fitted'

    def place_done(self, name, val):
        d, w = self.place, self.place.world
        d.dirty = True
        if name == 'p_name' and val:
            d.name = val
        elif name == 'p_sign':
            ch, _, col = val.partition(' ')
            if ch:
                d.sign = ch[0]
            if col.strip():
                try:
                    d.fg = D.hexrgb(col.strip())
                except (ValueError, KeyError, IndexError):
                    self.say('Write the colour as #e8e0c8.', True)
        elif name == 'p_land':
            w['land'] = [x for x in re.split(r'[,\s]+', val.lower()) if x] or ['any']
        elif name == 'p_look':
            d.look = val
        elif name == 'p_rumour':
            d.rumour = val
        elif name == 'p_book':
            d.book = val
        elif name == 'p_mood':
            r = self.room
            r.change()
            if val:
                r.moods[:1] = [val]
            elif r.moods:
                r.moods.pop(0)

    def floor_click(self, x, y, button):
        """A click on the FLOORS list: a floor (right mouse: take it away), or + up / + down."""
        from .screen import RX
        order = self.place.order()
        top = max(0, min(order.index(self.room) - 2, len(order) - FLOOR_ROWS))
        if FLOOR_Y0 <= y < FLOOR_Y0 + FLOOR_ROWS:
            i = top + y - FLOOR_Y0
            if i < len(order):
                f = order[i]
                if button == 3 and f.name != 'ground':
                    self.ask_pick(f'Take the floor {f.name} away?', [(f'Yes, take {f.name} away', f.name),
                                                                    ('No, keep it', None)],
                                  lambda v: v and self.remove_floor(v))
                else:
                    self.room = f
            return True
        if y == FLOOR_Y0 + FLOOR_ROWS:
            if RX + 2 <= x < RX + 8:
                self.add_floor('up')
            elif RX + 10 <= x < RX + 18:
                self.add_floor('down')
            return True
        return False

    # ------------------------------------------------------------ people and finds (the Creatures layer)
    def place_palette(self):
        people = [self._Item('person', name='person', label='a person who lives here'),
                  self._Item('find', name='find', label='a fixed find')]
        bosses = [self._Item('spot', ch=k, label=d['name']) for k, d in sorted(D.MONSTERS.items(),
                                                                                key=lambda kv: kv[1]['name'])
                  if d['boss']]
        return [('PEOPLE AND FINDS', people), ('A BOSS', bosses)]

    def place_spot_click(self, c, button):
        """People and finds on the Creatures layer. True when the click was theirs."""
        r = self.room
        if button == 3:
            had = len(r.persons) + len(r.items)
            if any(p[1] == c for p in r.persons) or any(i[1] == c for i in r.items):
                r.change()
                r.persons = [p for p in r.persons if p[1] != c]
                r.items = [i for i in r.items if i[1] != c]
            return had != len(r.persons) + len(r.items)
        it = self.pick['Creatures']
        if it.kind not in ('person', 'find'):
            return False
        if r.get(*c) in " #+'":
            self.say('People and finds stand on the floor.', True)
            return True
        if it.kind == 'person':
            def done(s, c=c):
                name, _, says = s.partition(':')
                if name.strip():
                    r.change()
                    r.persons = [p for p in r.persons if p[1] != c] + [(name.strip(), c, says.strip())]
            self.ask_line('A person: the name, then what they say', 'Brother Anselm: The dead sleep badly here.',
                          done)
        else:
            opts = [('a tome of a school', 'tome')] + [(f"{b['name']}", k) for k, b in D.BASES.items()
                                                      if b.get('grade', 'normal') == 'normal']

            def done(v, c=c):
                r.change()
                r.items = [i for i in r.items if i[1] != c] + [(v, c)]
            self.ask_pick('A fixed find: what lies here', opts, done)
        return True

    # ------------------------------------------------------------ the check
    def place_problems(self):
        d = self.place
        out = []
        try:
            pl = d.to_place()
        except (DP.Bad, ValueError) as e:
            return [(False, re.sub(r'^[^:]*:\d+: ', '', str(e)), [])], {}
        floor_of = {}
        for msg, fl in DP.problems(pl):
            m = msg[0].upper() + msg[1:] + '.'
            out.append((False, m, []))
            floor_of[m] = fl
        for f in d.floors:
            for y in range(f.h):
                for x in range(f.w):
                    ch = f.get(x, y)
                    if ch not in ' ?' and ch not in f.subst and tile_of(ch, f.things) is None:
                        m = f'{f.name}: the sign {ch} is not one the game knows.'
                        if m not in floor_of:
                            out.append((False, m, [(x, y)] if f is self.room else []))
                            floor_of[m] = f.name
            for what, xy in f.items:
                if what != 'tome' and what not in D.BASES:
                    m = f'{f.name}: the find "{what}" is not one the game knows.'
                    out.append((False, m, [xy] if f is self.room else []))
                    floor_of[m] = f.name
        others = [q for q in DP.load() if q.name == d.name and d.name != d.came_from
                  and (not d.file or os.path.basename(q.file) != os.path.basename(d.file))]
        if others or not d.name.strip():
            out.append((False, 'The name is used by another place: every place needs its own.' if others
                        else 'The place needs a name.', []))
        if not any(ok is False for ok, _m, _c in out):
            out.append((True, 'Every stair has its twin, and every floor reaches its stairs.', []))
            out.append((True, 'The way in is on the ground floor.', []))
        n = len(d.floors)
        out.append((True, f"{n} floor{'s' if n != 1 else ''}; found by {', '.join(d.world['found'])}.", []))
        people = sum(len(f.persons) for f in d.floors)
        finds = sum(len(f.items) for f in d.floors)
        if people or finds:
            out.append((True, f"{people} {'person lives' if people == 1 else 'people live'} here; "
                        f"{finds} fixed find{'s' if finds != 1 else ''}.", []))
        slots = sum(len(DP._slots([''.join(r) for r in f.grid])) for f in d.floors)
        if slots:
            out.append((True, f"{slots} room slot{'s' if slots != 1 else ''}: a theme room in each, anew in every "
                        'world.', []))
        if not d.look:
            out.append((None, 'No look line yet: the map says only its name.', []))
        return out, floor_of

    # ------------------------------------------------------------ the panel
    def render_place(self, cv, colours):
        FG, DIM, GOLD, PANEL, FIELD, SEL, LINE, W, RX = colours
        d = self.place
        x = RX
        cv.frame(x, 1, W - x, 22, LINE, PANEL, 'The place: in the world', GOLD)
        for name, y in self.place_rows():
            cv.text(x + 2, y, LABELS[name], DIM, PANEL)
            typing = self.field and self.field[0] == name
            val = self.field[1] + '_' if typing else self.place_value(name)
            bg = SEL if typing else FIELD
            vw = W - x - 14 if name in CYCLES else W - x - 13      # the value, clear of the ▼
            cv.fill(x + 11, y, W - x - 13, 1, ' ', FG, bg)
            if name == 'p_sign' and not typing:
                cv.put(x + 11, y, d.sign, d.fg, bg)
                cv.text(x + 13, y, val[2:], DIM, bg)
            else:
                cv.text(x + 11, y, val[-vw:] if typing else val[:vw],
                        GOLD if name == 'p_size' else FG, bg)
            if name in CYCLES:
                cv.put(W - 3, y, '▼', DIM, bg)
        cv.text(x + 2, FLOOR_Y0 - 1, 'FLOORS', DIM, PANEL)
        cv.text(x + 10, FLOOR_Y0 - 1, 'PgUp PgDn', GOLD, PANEL)
        order = d.order()
        top = max(0, min(order.index(self.room) - 2, len(order) - FLOOR_ROWS))
        for i, f in enumerate(order[top:top + FLOOR_ROWS]):
            y = FLOOR_Y0 + i
            on = f is self.room
            bg = SEL if on else PANEL
            cv.fill(x + 1, y, W - x - 2, 1, ' ', FG, bg)
            cv.text(x + 2, y, '►' if on else ' ', GOLD, bg)
            cv.text(x + 4, y, f.name, GOLD if on else FG, bg)
            bits = []
            if any('<' in ''.join(r) for r in f.grid):
                bits.append('<')
            if any('>' in ''.join(r) for r in f.grid):
                bits.append('>')
            if f.persons:
                bits.append(f'{len(f.persons)} people' if len(f.persons) > 1 else '1 person')
            cv.text(x + 13, y, ' '.join(bits), DIM, bg, maxw=W - x - 15)
        y = FLOOR_Y0 + FLOOR_ROWS
        cv.text(x + 2, y, '+ up', GOLD, PANEL)
        cv.text(x + 10, y, '+ down', GOLD, PANEL)
