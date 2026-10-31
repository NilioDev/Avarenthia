"""Round B1 of the editor: the Creatures and Events layers, the Variety tool, dressing (Ctrl+D), rolling (Ctrl+R),
and the small dialogs they share (a line to type, a list to pick from). A mixin of screen.Editor: it uses the
Editor's room, layer, tool, pick, dialog, say() and the colours of screen.py.

Events stay choices from lists: a WHEN, an AT, IFs and THENs, each field a list to pick from; only a message is typed.
A wire is an event made by dragging from one mark to another ("when you bump A, open Q")."""
import random

from .. import data as D
from .. import dressing as DR
from .. import pieces as P
from . import tools as T
from .model import DOES

# then-verbs as the pickers offer them: (verb, what it asks for next)
THEN_VERBS = [('msg', 'text'), ('do', 'does'), ('spawn', 'spawn'), ('wake', None), ('open', 'mark'), ('shut', 'mark'),
              ('cavein', 'mark'), ('flood', 'mark'), ('reveal', None), ('set', 'state'), ('flip', 'switch'),
              ('add', 'counter'), ('sub', 'counter'), ('after', 'turns'), ('reset', None)]
THEN_SAYS = {'msg': 'a line in the messages', 'do': 'what a thing can do', 'spawn': 'creatures come',
             'wake': 'every creature wakes', 'open': 'bars, rubble or a door give way', 'shut': 'bars drop',
             'cavein': 'rubble falls', 'flood': 'water comes', 'reveal': 'the level is known',
             'set': 'a switch to a state', 'flip': 'a switch to its next state', 'add': 'a counter one up',
             'sub': 'a counter one down', 'after': 'in some turns, one more then', 'reset': 'the room back as drawn'}
WHEN_SAYS = {'enter': 'you step in, the first time', 'step': 'you step on the mark', 'bump': 'you walk into the mark',
             'take': 'you take a find', 'clear': 'the last foe falls', 'night': 'night falls'}
SPAWNS = ('pack', 'undead', 'beasts', 'fire', 'vermin')
OPENS = {D.BARS, D.RUBBLE, D.DOOR, D.VAULTDOOR, D.SECRET}


def creatures_for(kinds):
    """The creatures that may live in places of these kinds (all but bosses when 'any')."""
    want = {k for k in kinds if not k.startswith('not:')}
    out = []
    for k, d in sorted(D.MONSTERS.items(), key=lambda kv: kv[1]['name']):
        if d['boss']:
            continue
        if 'any' in want or want & set(d['tags'].split()):
            out.append(k)
    return out


def marks_of(room):
    """{letter: [cells]} of the room's marks: its things' letters on the map."""
    out = {}
    for y in range(room.h):
        for x in range(room.w):
            ch = room.grid[y][x]
            if ch in room.things:
                out.setdefault(ch, []).append((x, y))
    return out


def then_mark(th):
    """The mark a then works on (open:Q, after:5:shut:Q), or None."""
    verb, _, arg = th.partition(':')
    if verb == 'after':
        return then_mark(arg.partition(':')[2])
    return arg if verb in ('open', 'shut', 'cavein', 'flood') else None


class LayerTools:
    # ------------------------------------------------------------ the small dialogs
    def ask_line(self, title, text, done):
        self.dialog = ('line', {'title': title, 'text': text, 'done': done})

    def ask_pick(self, title, options, done):
        """options [(label, value)]; done(value)."""
        self.dialog = ('pick', {'title': title, 'options': options, 'done': done, 'scroll': 0})

    # ------------------------------------------------------------ palettes of the new layers
    def creature_palette(self):
        r = self.room
        lists = [self._Item('spot', ch=f'list:{n}', label=n) for n in r.lists]
        lists.append(self._Item('action', name='lists', label='+ lists, and more'))
        mons = [self._Item('spot', ch=k, label=D.MONSTERS[k]['name']) for k in creatures_for(r.kinds)]
        return [('OF THE PLACE', [self._Item('spot', ch='?', label='one of the place')]),
                ('MY LISTS: KEYS 1-9', lists), ('CREATURES', mons)]

    def event_palette(self):
        r = self.room
        sw = [self._Item('switch', name=n, label=f"{n}: {' '.join(s)}") for n, s in r.switches.items()]
        sw.append(self._Item('action', name='switch+', label='+ a switch'))
        ct = [self._Item('counter', name=n, label=f'{n} from {v}') for n, v in r.counters.items()]
        ct.append(self._Item('action', name='counter+', label='+ a counter'))
        marks = [self._Item('mark', ch=g, label=r.things[g][0]) for g in sorted(marks_of(r))]
        return [('MARKS', marks), ('SWITCHES', sw), ('COUNTERS', ct)]

    def variety_palette(self):
        r = self.room
        groups = []
        for g in '123456789':
            if g in r.subst:
                opts = ' : '.join(f"{self._sign_name(c)} {w}" for c, w in r.subst[g])
                groups.append(self._Item('group', ch=g, label=f'{g} {opts}'))
        free = next((g for g in '123456789' if g not in r.subst), None)
        if free:
            groups.append(self._Item('action', name='group+', label=f'+ group {free}'))
        return [('VARIETY GROUPS', groups)]

    def _sign_name(self, ch):
        if ch == ' ':
            return 'none'
        if ch in self.room.things:
            return self.room.things[ch][0]
        t = P.LEGEND.get(ch)
        return D.TILES[t].name if t is not None else ch

    def palette_click(self, it, button):
        """A click on one of the new palettes' lines. Returns True when it was one."""
        r = self.room
        if it.kind == 'action':
            if it.name == 'lists':
                self.lists_dialog()
            elif it.name == 'switch+':
                self.ask_line('A switch: its name, then its states', 'gate = shut open', self._add_switch)
            elif it.name == 'counter+':
                self.ask_line('A counter: its name and where it starts', 'plates 0', self._add_counter)
            elif it.name == 'group+':
                g = next(g for g in '123456789' if g not in r.subst)
                r.change()
                r.subst[g] = [('.', 1)]
                self.pick['Variety'] = self._Item('group', ch=g, label=g)
                self.variety_dialog(g)
            return True
        if it.kind in ('switch', 'counter'):
            if button == 3:
                r.change()
                (r.switches if it.kind == 'switch' else r.counters).pop(it.name, None)
            elif it.kind == 'switch':
                self.ask_line('The switch: its name, then its states', f"{it.name} = {' '.join(r.switches[it.name])}",
                              lambda s, old=it.name: self._add_switch(s, old))
            else:
                self.ask_line('The counter: its name and where it starts', f'{it.name} {r.counters[it.name]}',
                              lambda s, old=it.name: self._add_counter(s, old))
            return True
        if it.kind == 'group':
            if button == 3:
                self.variety_dialog(it.ch)
            else:
                self.pick['Variety'] = it
            return True
        if it.kind == 'mark':
            evs = [i for i, e in enumerate(r.events) if e['at'] == it.ch]
            if evs:
                self.ev_sel = evs[0]
            return True
        return False

    def _add_switch(self, s, old=None):
        name, _, states = s.partition('=')
        name, states = name.strip(), states.split() or ['off', 'on']
        if not name:
            return
        self.room.change()
        if old and old != name:
            self.room.switches.pop(old, None)
        self.room.switches[name] = states

    def _add_counter(self, s, old=None):
        name, _, start = s.strip().rpartition(' ')
        if not name:
            name, start = start, '0'
        try:
            n = int(start)
        except ValueError:
            name, n = s.strip(), 0
        if not name:
            return
        self.room.change()
        if old and old != name:
            self.room.counters.pop(old, None)
        self.room.counters[name] = n

    # ------------------------------------------------------------ the Creatures layer
    def creature_click(self, c, button):
        r = self.room
        if button == 3:
            if c in r.spots:
                r.change()
                del r.spots[c]
            return
        it = self.pick['Creatures']
        if it.kind != 'spot':
            return
        if r.get(*c) in ' #+':
            self.say('A creature stands on the floor of the room.', True)
            return
        r.change()
        r.spots[c] = it.ch

    def creature_key(self, tok):
        if tok.isdigit() and tok != '0':
            names = list(self.room.lists)
            i = int(tok) - 1
            if i < len(names):
                self.pick['Creatures'] = self._Item('spot', ch=f'list:{names[i]}', label=names[i])
            else:
                self.say(f'No list {tok} yet: make one under MY LISTS.', True)
            return True
        return False

    def spot_look(self, what):
        """(sign, colour) a creature spot shows."""
        if what == '?':
            return '?', (217, 165, 71)
        if what.startswith('list:'):
            names = list(self.room.lists)
            n = what[5:]
            return (str(names.index(n) + 1) if n in names else '*'), (136, 182, 220)
        d = D.MONSTERS.get(what)
        return (d['ch'], d['fg']) if d else ('?', (236, 106, 92))

    def lists_dialog(self):
        self.dialog = ('lists', {'list': next(iter(self.room.lists), None), 'scroll': 0})

    def lists_click(self, x, y, button):
        st = self.dialog[1]
        r = self.room
        names = list(r.lists)
        x0, y0 = 6, 8
        if x0 <= x < 30:                                   # the lists
            i = y - y0
            if 0 <= i < len(names):
                if button == 3:
                    r.change()
                    del r.lists[names[i]]
                    st['list'] = next(iter(r.lists), None)
                else:
                    st['list'] = names[i]
            elif i == len(names) and len(names) < 9:
                self.ask_line('A new list: its name', 'war band', self._new_list)
            elif y == 48:                                  # and more
                self.more_pick()
            return
        cur = st.get('list')
        if 32 <= x < 62 and cur in r.lists:                # the chosen list: weights
            i = y - y0
            opts = r.lists[cur]
            if 0 <= i < len(opts):
                r.change()
                k, w = opts[i]
                w += -1 if button == 3 else 1
                if w <= 0:
                    opts.pop(i)
                else:
                    opts[i] = (k, w)
            return
        if 64 <= x < 104 and cur in r.lists:               # every creature that may live here: add one
            mons = creatures_for(r.kinds)
            i = y - y0 + st.get('scroll', 0)
            if 0 <= i < len(mons) and y < 52:
                r.change()
                opts = r.lists[cur]
                for j, (k, w) in enumerate(opts):
                    if k == mons[i]:
                        opts[j] = (k, w + 1)
                        break
                else:
                    opts.append((mons[i], 1))

    def _new_list(self, name):
        name = name.strip()
        if not name or name in self.room.lists:
            return
        self.room.change()
        self.room.lists[name] = []
        self.dialog = ('lists', {'list': name, 'scroll': 0})

    def more_pick(self):
        r = self.room
        opts = [('none', None), ('? one of the place', '?')] + [(f'list {n}', f'list:{n}') for n in r.lists]

        def what(v):
            if v is None:
                r.change()
                r.more = None
                self.lists_dialog()
                return
            self.ask_pick('How many more, where there is room?',
                          [(f'{a} to {b}', (a, b)) for a, b in ((0, 1), (0, 2), (1, 2), (1, 3), (2, 4), (3, 6))],
                          lambda n: self._set_more(v, n))
        self.ask_pick('And more: what?', opts, what)

    def _set_more(self, v, n):
        self.room.change()
        self.room.more = (v, n[0], n[1])
        self.lists_dialog()

    # ------------------------------------------------------------ the Events layer
    def event_click(self, c, button):
        """A click on the drawing in the Events layer: a mark's events, or a new mark on the floor."""
        r = self.room
        ch = r.get(*c)
        if button == 3:
            if ch in r.things:
                r.change()
                r.events = [e for e in r.events if e['at'] != ch]
                if r.things[ch] == ('floor', None):
                    for cc in [cc for cc in marks_of(r).get(ch, [])]:
                        r.set(cc[0], cc[1], '.')
                r.tidy()
                self.ev_sel = None
            return
        if ch in r.things:
            evs = [i for i, e in enumerate(r.events) if e['at'] == ch]
            if evs:
                self.ev_sel = evs[(evs.index(self.ev_sel) + 1) % len(evs)] if self.ev_sel in evs else evs[0]
                return
            r.change()
            walk = D.TILES[P.tile_named(r.things[ch][0])].walk
            r.events.append({'when': 'step' if walk else 'bump', 'at': ch, 'if': [], 'then': [], 'again': False})
            self.ev_sel = len(r.events) - 1
            return
        if ch == '.':
            r.change()
            g = r.letter_for('floor', None)
            if g is None:
                self.say('All 26 letters for things are in use in this piece.', True)
                return
            r.set(c[0], c[1], g)
            r.events.append({'when': 'step', 'at': g, 'if': [], 'then': [], 'again': False})
            self.ev_sel = len(r.events) - 1

    def wire(self, a, b):
        """A wire from mark a to mark b: when you bump (or step on) a, b gives way, or a switch turns."""
        r = self.room
        ga, gb = r.get(*a), r.get(*b)
        if ga not in r.things or gb not in r.things or ga == gb:
            return False
        r.change()
        walk = D.TILES[P.tile_named(r.things[ga][0])].walk
        tb = P.tile_named(r.things[gb][0])
        if tb in OPENS:
            th = f'open:{gb}'
        elif r.switches:
            th = f'flip:{next(iter(r.switches))}'
        else:
            th = f'msg:"Something moves by the {r.things[gb][0]}."'
        r.events.append({'when': 'step' if walk else 'bump', 'at': ga, 'if': [], 'then': [th], 'again': True})
        self.ev_sel = len(r.events) - 1
        return True

    def wires(self):
        """[(from cell, to cell)] for every event that works on a mark: the lines drawn on the Events layer."""
        r = self.room
        mk = marks_of(r)
        setters = {}
        for e in r.events:
            for th in e['then']:
                v, _, a = th.partition(':')
                if v in ('set', 'flip') and e['at']:
                    setters.setdefault(a.split(':')[0], []).append(e['at'])
        out = []
        for e in r.events:
            froms = [e['at']] if e['at'] else []
            if e['when'].startswith('switch:'):
                froms += setters.get(e['when'].split(':')[1], [])
            for th in e['then']:
                m = then_mark(th)
                if not m or m not in mk:
                    continue
                for f in froms:
                    if f in mk and f != m:
                        a = mk[f][0]
                        b = min(mk[m], key=lambda c: abs(c[0] - a[0]) + abs(c[1] - a[1]))
                        out.append((a, b))
        return out

    def event_rows(self, x0, y0, width, rows):
        """The events as rows of clickable bits: [(x, y, text, colour key, action)], action (kind, index, n)."""
        out = []
        y = y0
        r = self.room
        first = getattr(self, 'ev_scroll', 0)
        for i, e in enumerate(r.events[first:], first):
            if y + 1 >= y0 + rows:
                break
            x = x0
            bits = [('n', f'{i + 1}', ('sel', i, 0)), ('k', 'WHEN', None), ('v', e['when'], ('when', i, 0))]
            if e['when'] in ('step', 'bump') or e['at']:
                bits += [('k', 'AT', None), ('v', e['at'] or '-', ('at', i, 0))]
            bits += [('k', 'IF', None)] + [('v', c, ('if', i, j)) for j, c in enumerate(e['if'])] + \
                [('g', '+', ('if+', i, 0)), ('v', 'again' if e['again'] else 'once', ('again', i, 0)),
                 ('b', '×', ('del', i, 0))]
            for kind, s, act in bits:
                if x + len(s) > x0 + width:
                    break
                out.append((x, y, s, kind, act, i))
                x += len(s) + 1
            y += 1
            x = x0 + 2
            bits = [('k', 'THEN', None)] + [('v', t, ('then', i, j)) for j, t in enumerate(e['then'])] + \
                [('g', '+', ('then+', i, 0))]
            for kind, s, act in bits:
                if x + len(s) > x0 + width:
                    s = s[:max(1, x0 + width - x - 1)]
                    if len(s) < 2:
                        break
                out.append((x, y, s, kind, act, i))
                x += len(s) + 1
            y += 1
        if y < y0 + rows:
            out.append((x0, y, '+ a new event (or click a mark, or drag from one mark to another)', 'g',
                        ('new', 0, 0), -1))
        return out

    def event_act(self, act, button):
        kind, i, j = act
        r = self.room
        if kind == 'new':
            r.change()
            r.events.append({'when': 'enter', 'at': None, 'if': [], 'then': [], 'again': False})
            self.ev_sel = len(r.events) - 1
            return
        if not (0 <= i < len(r.events)):
            return
        e = r.events[i]
        self.ev_sel = i
        if kind == 'del':
            r.change()
            r.events.pop(i)
            self.ev_sel = None
        elif kind == 'again':
            r.change()
            e['again'] = not e['again']
        elif kind == 'when':
            opts = [(f'{w}: {WHEN_SAYS[w]}', w) for w in P.WHEN]
            for n, states in r.switches.items():
                opts += [(f'switch:{n}:{s}: the switch {n} comes to {s}', f'switch:{n}:{s}') for s in states]
            for n in r.counters:
                opts += [(f'count:{n}:{k}: the counter {n} comes to {k}', f'count:{n}:{k}') for k in range(1, 7)]
            self.ask_pick('WHEN', opts, lambda v: self._set_ev(i, 'when', v))
        elif kind == 'at':
            opts = [('- no mark', None)] + [(f'{g} {r.things[g][0]}', g) for g in sorted(marks_of(r))]
            self.ask_pick('AT which mark', opts, lambda v: self._set_ev(i, 'at', v))
        elif kind in ('if', 'if+'):
            if kind == 'if' and button == 3:
                r.change()
                e['if'].pop(j)
                return
            opts = [('night', 'night'), ('day', 'day')] + [(f'chance:{n} (in a hundred)', f'chance:{n}')
                                                           for n in (10, 25, 50, 75)]
            for n, states in r.switches.items():
                opts += [(f'switch:{n}:{s}', f'switch:{n}:{s}') for s in states]
            for n in r.counters:
                opts += [(f'count:{n}:{k} (at least)', f'count:{n}:{k}') for k in range(1, 7)]
            opts.append(('has: an item you carry (type its key)', 'has:'))
            self.ask_pick('IF', opts, lambda v: self._set_if(i, j if kind == 'if' else None, v))
        elif kind in ('then', 'then+'):
            if kind == 'then' and button == 3:
                r.change()
                e['then'].pop(j)
                return
            self.pick_then(lambda v: self._set_then(i, j if kind == 'then' else None, v))

    def _set_ev(self, i, key, v):
        self.room.change()
        self.room.events[i][key] = v

    def _set_if(self, i, j, v):
        if v == 'has:':
            return self.ask_line('Has: the key of an item', 'vkey', lambda s: self._set_if(i, j, 'has:' + s.strip()))
        self.room.change()
        e = self.room.events[i]
        if j is None:
            e['if'].append(v)
        else:
            e['if'][j] = v

    def _set_then(self, i, j, v):
        self.room.change()
        e = self.room.events[i]
        if j is None:
            e['then'].append(v)
        else:
            e['then'][j] = v

    def pick_then(self, done, prefix=''):
        """The then-pickers: first the verb, then what it asks for. done(then text)."""
        r = self.room
        mk = sorted(marks_of(r))

        def verb(v):
            ask = dict(THEN_VERBS)[v]
            if ask is None:
                return done(prefix + v)
            if ask == 'text':
                return self.ask_line('The line in the messages', 'The bones stir.',
                                     lambda s: done(prefix + 'msg:"' + s.replace('"', "'") + '"'))
            if ask == 'does':
                return self.ask_pick('Do what a thing can do', [(a, a) for a in sorted(DOES)],
                                     lambda a: done(prefix + f'do:{a}'))
            if ask == 'spawn':
                kinds = [(k, k) for k in SPAWNS] + [(D.MONSTERS[k]['name'], k) for k in creatures_for(r.kinds)]
                return self.ask_pick('Spawn what', kinds, lambda k: self.ask_pick(
                    'How many', [(str(n), n) for n in range(1, 7)], lambda n: done(prefix + f'spawn:{k}:{n}')))
            if ask == 'mark':
                if not mk:
                    return self.say('Draw a mark first (a thing, or click the floor on this layer).', True)
                return self.ask_pick('At which mark', [(f'{g} {r.things[g][0]}', g) for g in mk],
                                     lambda g: done(prefix + f'{v}:{g}'))
            if ask == 'state':
                opts = [(f'{n} to {s}', f'{n}:{s}') for n, states in r.switches.items() for s in states]
                if not opts:
                    return self.say('Make a switch first, under SWITCHES.', True)
                return self.ask_pick('Set which switch', opts, lambda a: done(prefix + f'set:{a}'))
            if ask == 'switch':
                if not r.switches:
                    return self.say('Make a switch first, under SWITCHES.', True)
                return self.ask_pick('Flip which switch', [(n, n) for n in r.switches],
                                     lambda n: done(prefix + f'flip:{n}'))
            if ask == 'counter':
                if not r.counters:
                    return self.say('Make a counter first, under COUNTERS.', True)
                return self.ask_pick('Which counter', [(n, n) for n in r.counters],
                                     lambda n: done(prefix + f'{v}:{n}'))
            if ask == 'turns':
                return self.ask_pick('In how many turns', [(str(n), n) for n in (2, 3, 5, 10, 20, 50)],
                                     lambda n: self.pick_then(done, prefix + f'after:{n}:'))
        verbs = [(f'{v}: {THEN_SAYS[v]}', v) for v, _a in THEN_VERBS if not (prefix and v == 'after')]
        self.ask_pick('THEN', verbs, verb)

    # ------------------------------------------------------------ Variety
    def variety_paint(self, cells):
        g = self.pick['Variety'].ch if self.pick.get('Variety') else None
        if not g or g not in self.room.subst:
            self.say('Pick a group under VARIETY GROUPS first (or make one).', True)
            return
        for c in cells:
            if self.room.inb(*c) and self.room.get(*c) not in ' +':
                self.room.set(c[0], c[1], g)

    def variety_dialog(self, g):
        self.dialog = ('variety', {'group': g})

    def variety_click(self, x, y, button):
        st = self.dialog[1]
        r = self.room
        g = st['group']
        opts = r.subst.setdefault(g, [])
        y0 = 18
        i = y - y0
        if 0 <= i < len(opts):
            r.change()
            c, w = opts[i]
            w += -1 if button == 3 else 1
            if w <= 0:
                opts.pop(i)
            else:
                opts[i] = (c, w)
            return
        adds = self._variety_adds()
        j = y - (y0 + len(opts) + 1)
        if 0 <= j < len(adds):
            r.change()
            ch = adds[j][1]
            for k, (c, w) in enumerate(opts):
                if c == ch:
                    opts[k] = (c, w + 1)
                    break
            else:
                opts.append((ch, 1))

    def _variety_adds(self):
        out = []
        for lay in ('Ground', 'Things'):
            it = self.pick[lay]
            ch = it.ch if it.kind == 'sign' else self.room.letter_for(it.name, it.act)
            if ch and ch not in '+<>':
                out.append((f'+ the picked {lay.lower()} sign: {self._sign_name(ch)}', ch))
        out.append(('+ none (rock: the cell is left out)', ' '))
        return out

    # ------------------------------------------------------------ Ctrl+D: dressing
    def dress_dialog(self):
        sets = dict(self.room.dress)
        self.dialog = ('dress', {'sets': sets or {'ruin': 2}, 'laid': []})

    def dress_click(self, x, y, button):
        st = self.dialog[1]
        names = list(DR.SETS)
        x0, y0 = 30, 16
        i = y - y0
        if 0 <= i < len(names):
            name = names[i]
            if x0 + 22 <= x < x0 + 32:
                st['sets'][name] = max(1, min(5, int(x - (x0 + 22)) // 2 + 1))
            elif name in st['sets']:
                del st['sets'][name]
            else:
                st['sets'][name] = 3
            return
        if y == y0 + len(names) + 2:
            if x0 <= x < x0 + 10:
                self.dress_now()
            elif x0 + 12 <= x < x0 + 28:
                self.dress_in_game()
            elif x0 + 30 <= x < x0 + 40 and st['laid']:
                self.dress_now(again=True)

    def dress_now(self, again=False, rng=None):
        """Dress the room now, in the editor: what is laid is drawn in, shown light green until the next stroke."""
        st = self.dialog[1] if self.dialog and self.dialog[0] == 'dress' else {'sets': dict(self.room.dress), 'laid': []}
        r = self.room
        if again and st.get('laid'):
            r.step_back()
        sets = list(st['sets'].items())
        if not sets:
            self.say('Pick a set first.', True)
            return []
        r.change()
        out = P.Drawing({(x, y): r.get(x, y) for y in range(r.h) for x in range(r.w) if r.get(x, y) != ' '})
        out.spots = dict(r.spots)
        gate = next((c for c, ch in out.items() if ch == '+'), None)
        if gate is None:
            self.say('The room needs its way in (+) before it can be dressed.', True)
            return []
        try:
            p = P.parse(r.text(), 'editor', checked=False)[0]
        except P.Bad as e:
            self.say(str(e), True)
            return []
        p.dress = sets
        laid = P.dress_drawing(p, out, gate, rng or random)
        legend = {v: k for k, v in P.LEGEND.items()}
        for c, name in laid:
            t = DR.tile(name)
            ch = legend.get(t)
            if ch is None:
                ch = r.letter_for(_short(name), None)
            if ch:
                r.set(c[0], c[1], ch)
        st['laid'] = [c for c, _n in laid]
        self.dressed = set(st['laid'])
        self.say(f'Dressed: {len(laid)} things laid. R rolls again; Ctrl+Z takes it away.')
        return laid

    def dress_in_game(self):
        st = self.dialog[1]
        self.room.change()
        self.room.dress = list(st['sets'].items())
        self.dialog = None
        self.say('The game dresses this room anew in every world.')

    # ------------------------------------------------------------ Ctrl+R: rolling
    def roll_dialog(self):
        try:
            p = P.parse(self.room.text(), 'editor', checked=False)[0]
            draws = [P.drawn(p)[0] for _ in range(2)]
        except (P.Bad, StopIteration, ValueError) as e:
            self.say(f'Cannot roll it yet: {e or "the way in is missing"}.', True)
            return
        self.dialog = ('roll', {'draws': draws})


def _short(name):
    """The name a THING line uses for a tile (the short one when there is one)."""
    t = DR.tile(name)
    return next((k for k, v in P.TILE_NAMES.items() if v == t), name)


def in_dialog_line(cv, x, y, w, s, fg, bg):
    cv.fill(x, y, w, 1, ' ', fg, bg)
    cv.text(x, y, s[:w], fg, bg)


def draw_wires(cv, ed, vw, vh, gold):
    """The wires of the Events layer: a dotted gold line from a mark to what it works on."""
    for a, b in ed.wires():
        for c in T.line_cells(a, b)[1:-1]:
            i, j = c[0] - ed.view[0], c[1] - ed.view[1]
            if 0 <= i < vw and 0 <= j < vh and ed.room.get(*c) not in ' #':
                cv.put(i, j, '·', gold, None)
