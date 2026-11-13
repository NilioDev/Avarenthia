"""The screens of a home of your own (round 64): setting out your furniture over the map, and a chest's two lists.
The rules live in homes.py."""
from . import homes as HM
from . import ui as U
from .ui import Modal, PANEL, FG, DIM, GOLD, GOOD, BAD, INFO, LINE, DIRS, wrap_text

SEL = (52, 40, 28)


class FurnishScreen(Modal):
    """Furnish: a cursor on the floor of your home and, beside it, what you own and have not set out yet. Enter sets
    the chosen thing down where the cursor is, or takes up what stands there; Tab picks the next thing."""
    fullsize = True
    tall = False
    dim = False

    def __init__(self, app, hid):
        super().__init__(app)
        self.hid = hid
        p = self.game.player
        self.x, self.y = p.x, p.y
        self.sel = 0
        self.note = None
        h = HM.get(self.game, hid)
        if h is not None and HM.take_trophies(self.game, h):
            self.note = 'Your trophies are out of the bag, ready to hang.'

    @property
    def home(self):
        return HM.get(self.game, self.hid)

    def render(self, cv):
        g, h = self.game, self.home
        if h is None:
            return
        gs = self.app.screens[0]
        ox, oy = getattr(gs, 'origin', (0, 0))
        vx, vy = self.x - ox, self.y - oy
        cells = {tuple(c) for c in h['cells']}
        if 0 <= vx < U.MAP_W and 0 <= vy < U.MAP_H:
            cv.put_bg(vx, vy, (150, 120, 30) if (self.x, self.y) in cells else (110, 40, 30))
        _hh, here = HM.piece_at(g, self.x, self.y)
        bg = (24, 20, 16)
        cv.fill(0, U.LOG_Y, U.MAP_W, U.H - U.LOG_Y, ' ', FG, bg)
        if here:
            cv.text(1, U.LOG_Y, HM.piece_name(here), HM.piece_look(here)[1], bg, maxw=U.MAP_W - 2)
            what = 'Broken: walk into it to have it mended.' if here.get('broken') else HM.PIECES[here['k']][5]
            yy = U.LOG_Y + 1
            for part in wrap_text(what, U.MAP_W - 4):
                cv.text(2, yy, part, FG, bg)
                yy += 1
        elif (self.x, self.y) in cells:
            cv.text(1, U.LOG_Y, 'The floor of your home.', DIM, bg)
        else:
            cv.text(1, U.LOG_Y, 'Not your floor.', DIM, bg)
        if self.note:
            cv.text(2, U.H - 2, self.note, GOLD, bg, maxw=U.MAP_W - 4)
        cv.text(1, U.H - 1, 'arrows: cursor · Tab: next · Enter: set down or take up · c: dye · Esc: done', DIM, bg)
        self.draw_panel(cv, h)

    def draw_panel(self, cv, h):
        g = self.game
        x = U.PX
        cv.fill(U.MAP_W + 1, 0, U.W - U.MAP_W - 1, U.H, ' ', FG, PANEL)
        cv.text(x, 0, 'FURNISH', GOLD, PANEL)
        n = HM.comfort(g, h)
        cv.text_right(U.W - 2, 0, f'Comfort {HM.stars(n)}', GOLD if n else DIM, PANEL)
        yy = 1
        for part in wrap_text(h['name'], U.PW):
            cv.text(x, yy, part, FG, PANEL)
            yy += 1
        yy += 1
        cv.text(x, yy, 'TO SET OUT', DIM, PANEL)
        yy += 1
        store = h['store']
        self.sel = max(0, min(self.sel, len(store) - 1)) if store else 0
        if not store:
            for part in wrap_text('Nothing. A carpenter sells more.', U.PW - 1):
                cv.text(x + 1, yy, part, DIM, PANEL)
                yy += 1
        for i, pc in enumerate(store[:18]):
            on = i == self.sel
            if on:
                cv.fill(U.MAP_W + 1, yy, U.W - U.MAP_W - 2, 1, ' ', FG, SEL)
            ch, col = HM.piece_look(pc)
            cv.put(x, yy, '>' if on else ' ', GOLD, SEL if on else PANEL)
            cv.put(x + 2, yy, ch, col, SEL if on else PANEL)
            for j, part in enumerate(wrap_text(HM.piece_name(pc), U.PW - 4)):
                if on and j:
                    cv.fill(U.MAP_W + 1, yy, U.W - U.MAP_W - 2, 1, ' ', FG, SEL)
                cv.text(x + 4, yy, part, FG, SEL if on else PANEL)
                yy += 1
        if len(store) > 18:
            cv.text(x + 4, yy, f'and {len(store) - 18} more', DIM, PANEL)
            yy += 1
        yy += 1
        cv.text(x, yy, 'SET OUT', DIM, PANEL)
        yy += 1
        for pc in h['pieces']:
            if yy > U.H - 5:
                break
            ch, col = HM.piece_look(pc)
            cv.put(x + 2, yy, ch, col, PANEL)
            for part in wrap_text(HM.piece_name(pc), U.PW - 4):
                cv.text(x + 4, yy, part, DIM, PANEL)
                yy += 1
        if HM.dyes(g):
            parts = wrap_text('Dyes: ' + ', '.join(HM.dyes(g)), U.PW)
            for j, part in enumerate(parts):
                cv.text(x, U.H - 1 - len(parts) + j, part, DIM, PANEL)

    def on_key(self, tok, shift):
        g, h = self.game, self.home
        if h is None:
            self.app.pop()
            return
        d = DIRS.get(tok)
        if d:
            step = 5 if shift else 1
            m = g.map
            self.x = max(0, min(m.w - 1, self.x + d[0] * step))
            self.y = max(0, min(m.h - 1, self.y + d[1] * step))
            self.note = None
        elif tok == 'tab' and h['store']:
            self.sel = (self.sel + (-1 if shift else 1)) % len(h['store'])
        elif tok in ('enter', 'np_enter', 'space'):
            _hh, here = HM.piece_at(g, self.x, self.y)
            if here:
                why = HM.pick_up(g, h, here)
                if not why:
                    self.sel = len(h['store']) - 1
                self.note = why or f'You take up the {HM.piece_name(here).lower()}.'
            elif h['store']:
                pc = h['store'][self.sel]
                why = HM.place(g, h, pc, self.x, self.y)
                self.note = why or f'You set down the {HM.piece_name(pc).lower()}.'
        elif tok == 'c':
            _hh, here = HM.piece_at(g, self.x, self.y)
            self.note = HM.colour(g, h, here) if here else 'Put the cursor on a piece to dye it.'
        elif tok in ('esc', 'H'):
            g.compute_fov()
            g.request = ('save',)
            self.app.pop()


class ChestScreen(Modal):
    """A chest of your own: your bag on the left, the chest on the right. Enter moves the chosen thing across."""
    BW, BH = 96, 30
    title = 'A chest'

    def __init__(self, app, hid, at):
        super().__init__(app)
        self.hid, self.at = hid, tuple(at)
        self.side = 0
        self.sel = [0, 0]
        self.note = None

    def lists(self):
        g = self.game
        h, pc = HM.piece_at(g, *self.at)
        p = g.player
        bag = [it for it in p.inv if it.id not in p.eq.values()]
        return h, pc, [bag, pc['items'] if pc else []]

    def render(self, cv):
        g = self.game
        h, pc, ls = self.lists()
        if not pc:
            return
        x, y = self.box(cv, self.BW, self.BH, HM.piece_name(pc))
        half = self.BW // 2
        heads = ['YOUR BAG', f'IN THE CHEST · {len(pc["items"])} of {HM.chest_room(h, pc)}']
        for s in (0, 1):
            cx = x + 2 + s * half
            cv.text(cx, y + 2, heads[s], GOLD if s == self.side else DIM, PANEL)
            self.sel[s] = max(0, min(self.sel[s], len(ls[s]) - 1)) if ls[s] else 0
            top = max(0, self.sel[s] - (self.BH - 8))
            for i, it in enumerate(ls[s][top:top + self.BH - 7]):
                yy = y + 4 + i
                on = s == self.side and top + i == self.sel[s]
                if on:
                    cv.fill(cx - 1, yy, half - 2, 1, ' ', FG, SEL)
                cv.put(cx, yy, it.glyph(), it.color(), SEL if on else PANEL)
                cv.text(cx + 2, yy, it.display_name(), FG if on else U.scale(FG, .85), SEL if on else PANEL, maxw=half - 5)
            if not ls[s]:
                cv.text(cx, y + 4, 'Empty.', DIM, PANEL)
        if self.note:
            cv.text_center(U.W // 2, y + self.BH - 2, self.note, BAD if 'full' in self.note or 'first' in self.note else INFO, PANEL)
        cv.text_center(U.W // 2, y + self.BH - 1, ' ↑↓ thing · ←→ Tab: bag or chest · Enter: move it · Esc: close ', DIM, PANEL)

    def on_key(self, tok, shift):
        g = self.game
        h, pc, ls = self.lists()
        if not pc or tok == 'esc':
            g.request = ('save',)
            self.app.pop()
            return
        if tok in ('up', 'np8'):
            self.sel[self.side] = max(0, self.sel[self.side] - 1)
        elif tok in ('down', 'np2'):
            self.sel[self.side] = min(max(0, len(ls[self.side]) - 1), self.sel[self.side] + 1)
        elif tok in ('tab', 'left', 'right', 'np4', 'np6'):
            self.side = 1 - self.side
        elif tok in ('enter', 'np_enter', 'space') and ls[self.side]:
            it = ls[self.side][self.sel[self.side]]
            why = HM.put_in(g, h, pc, it) if self.side == 0 else HM.take_out(g, h, pc, it)
            self.note = why


def furnish(app):
    """The furnish key, in a home of your own."""
    g = app.game
    h = HM.here(g)
    if h is None:
        g.msg('You can set out furniture only in a home of your own.', 'info')
        return
    if h.get('squat_on'):
        g.msg('Not with squatters in the house.', 'bad')
        return
    app.push(FurnishScreen(app, h['id']))


def journal_rows(js):
    """The journal's Homes tab: each home, its state, its chests."""
    g = js.game
    hs = HM.homes(g)
    up = HM.upkeep(g)
    out = [js.head(f'YOUR HOMES · {len(hs)}' + (f' · upkeep about {HM._fmt(up)} a day' if up else ''))]
    if not hs:
        return out + js.para('None yet. A house for sale has a $ on its door; a carpenter sells a stake to build out '
                             'on the land.', DIM)
    from .worldgen import cheb
    from . import engine as E
    ox, oy = g.world_pos()
    for h in hs:
        line = HM.state_line(g, h)
        bad = h['state'] not in ('quiet',) or (h['kind'] == 'town' and HM.owed(g, h))
        d = cheb(h['x'], h['y'], ox, oy)
        where = f'{d} {E.DIR_SHORT[E.dir_name(h["x"] - ox, h["y"] - oy)]}' if d else 'here'
        out.append({'parts': [(3, HM.HOME_SIGN, HM.YOU), (5, h['name'], FG), (-3, where, INFO)]})
        n = HM.comfort(g, h)
        out.append({'parts': [(5, line, BAD if bad else GOOD), (-3, f'Comfort {HM.stars(n)}', GOLD if n else DIM)]})
        things = [it.display_name() for pc in h['pieces'] + h['store'] for it in pc.get('items', [])]
        if things:
            out += js.para('In the chests: ' + ', '.join(things[:12]) + (f' and {len(things) - 12} more' if len(things) > 12 else ''), DIM, 5, 90)
        if h.get('deliver'):
            out += js.para('On the way: ' + ', '.join(HM.piece_name(dv['piece']) for dv in h['deliver']), DIM, 5, 90)
        out.append({'parts': []})
    return out
