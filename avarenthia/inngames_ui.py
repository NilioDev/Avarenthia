"""The screens of the games at the inn (round 59): Bones, The Count and Vigil, each in its own window over the game
like fishing. Arrows, Enter and Esc only. The rules live in inngames.py."""
from . import inngames as IG
from .canvas import scale, mix
from .ui import Modal, LINE, PANEL, FG, DIM, GOLD, GOOD, BAD, BLOOD

WOOD, WOOD2 = (58, 38, 22), (46, 30, 17)
FLOOR_BG = (26, 21, 17)
BONE = (226, 214, 186)
YOU = (255, 246, 220)
REG = (200, 160, 120)


def keys(cv, x, y, w, h, s):
    cv.text_center(x + w // 2, y + h - 1, f' {s} ', DIM, PANEL)


def rule(cv, x, w, y):
    for xx in range(x + 1, x + w - 1):
        cv.put(xx, y, '─', LINE, PANEL)


def table(cv, x0, y0, w, h):
    for yy in range(h):
        for xx in range(w):
            edge = yy in (0, h - 1) or xx in (0, w - 1)
            bg = WOOD2 if edge else (WOOD if (xx + yy * 3) % 7 else scale(WOOD, 1.08))
            cv.put(x0 + xx, y0 + yy, '─' if edge and yy in (0, h - 1) else '│' if edge else ' ', scale(WOOD, 1.7), bg)


def floor(cv, x0, y0, w, h):
    for yy in range(h):
        for xx in range(w):
            cv.put(x0 + xx, y0 + yy, '.' if (xx * 7 + yy * 13) % 11 == 0 else ' ', (60, 50, 40), FLOOR_BG)


def lines(cv, x, y, w, rows, col=FG, n=3):
    """The last few lines of a game's log, wrapped, newest last and brightest."""
    out = []
    for k, s in enumerate(rows[-n:]):
        c = col if k == len(rows[-n:]) - 1 else DIM
        out.append((s, c))
    yy = y
    for s, c in out:
        yy += cv.wrap(x, yy, w, s, c, PANEL, 2) or 1
    return yy


def first(name):
    return name.split()[0] if name else name


# ====================================================================== Bones
PIPS = {1: [(1, 1)], 2: [(0, 0), (2, 2)], 3: [(0, 0), (1, 1), (2, 2)], 4: [(0, 0), (2, 0), (0, 2), (2, 2)],
        5: [(0, 0), (2, 0), (1, 1), (0, 2), (2, 2)]}


def bone(cv, x, y, face, kept=False, cur=False, bg=WOOD):
    body = scale(BONE, .55) if kept else BONE
    edge = GOLD if cur else scale(body, .6)
    for k in range(1, 4):
        cv.put(x + k, y, '─', edge, bg)
        cv.put(x + k, y + 4, '─', edge, bg)
        cv.put(x, y + k, '│', edge, bg)
        cv.put(x + 4, y + k, '│', edge, bg)
    for (cx, cy), ch in (((0, 0), '┌'), ((4, 0), '┐'), ((0, 4), '└'), ((4, 4), '┘')):
        cv.put(x + cx, y + cy, ch, edge, bg)
    face_bg = scale(body, .35)
    for yy in range(3):
        for xx in range(3):
            cv.put(x + 1 + xx, y + 1 + yy, ' ', None, face_bg)
    if face == 0:
        cv.put(x + 2, y + 2, '☻', BLOOD, face_bg)
    else:
        for px, py in PIPS[face]:
            cv.put(x + 1 + px, y + 1 + py, '•', body, face_bg)


class BonesScreen(Modal):
    tall = False
    BW, BH = 76, 36

    def __init__(self, app, ctx):
        super().__init__(app)
        g = self.game
        self.ctx = ctx
        self.kind = IG.bones_kind(IG.people(g))
        self.name, self.twist = IG.BONES[self.kind]
        self.place = _place(g)
        self.cun = IG.cunning(g)
        self.stakes = [c for c in IG.STAKES if c <= IG.stake_room(g) and c <= g.player.gold] or [IG.STAKES[0]]
        self.si = 0
        self.loaded = False
        self.g = None
        self.sel = 0
        self.settled = False

    # the keys
    def on_key(self, tok, shift):
        gm = self.g
        if gm is None:                          # choosing the stake
            if tok in ('left', 'np4'):
                self.si = max(0, self.si - 1)
            elif tok in ('right', 'np6'):
                self.si = min(len(self.stakes) - 1, self.si + 1)
            elif tok in ('up', 'np8') and self.cun:
                self.loaded = not self.loaded
            elif tok in ('enter', 'np_enter'):
                st = self.stakes[self.si]
                IG.put_stake(self.game, st)
                self.g = IG.Bones(self.kind, [first(self.ctx.get('a')), first(self.ctx.get('b'))], st,
                                  cunning=self.cun, loaded=self.loaded)
                self.after()                    # the cup may start with one of them
            elif tok == 'esc':
                self.app.pop()
            return
        if gm.phase == 'over':
            if tok in ('enter', 'np_enter', 'esc'):
                self.settle()
                self.app.pop()
            return
        if tok == 'esc':
            g = self.game
            if gm.seen:
                g.player.gold += gm.stake
                g.msg(f'You push your stake back across the table. "Not with that bone, {gm.seen}." Nobody argues.',
                      'info')
            else:
                g.msg('You get up from the game. Your stake stays in the pot.')
            g.end_turn(10)
            self.settled = True
            self.app.pop()
            return
        if gm.phase == 'throw':
            if tok in ('enter', 'np_enter'):
                gm.throw()
                self.sel = 0
                self.after()
            return
        if gm.phase == 'pick':
            n = len(gm.thrown)
            if tok in ('left', 'np4'):
                self.sel = (self.sel - 1) % n
            elif tok in ('right', 'np6'):
                self.sel = (self.sel + 1) % n
            elif tok in ('up', 'np8'):
                gm.toggle(self.sel)
            elif tok in ('enter', 'np_enter'):
                if not any(gm.marked):
                    gm.say('Set at least one bone aside first.')
                else:
                    gm.throw_rest()
                    self.sel = 0
                    self.after()
            elif tok in ('down', 'np2'):
                if not any(gm.marked):
                    gm.say('Set at least one bone aside first.')
                else:
                    gm.bank()
                    self.after()

    def after(self):
        gm = self.g
        if gm.phase != 'over' and not gm.players[gm.cur]['you']:
            gm.ai()

    def settle(self):
        if not self.settled and self.g is not None:
            self.settled = True
            IG.bones_over(self.game, self.g)

    # the picture
    def render(self, cv):
        g = self.game
        gm = self.g
        x, y = self.box(cv, self.BW, self.BH, f' {self.name} · {self.place} ')
        px, py, pw = x + 2, y + 2, self.BW - 4
        floor(cv, px, py, pw, 17)
        tx, ty, tw, th = px + 10, py + 3, pw - 20, 11
        table(cv, tx, ty, tw, th)
        a, b = first(self.ctx.get('a')), first(self.ctx.get('b'))
        cv.put(tx - 1, ty + th // 2, '☺', REG, FLOOR_BG)
        cv.text(tx - 2 - len(a), ty + th // 2 + 1, a, DIM, FLOOR_BG)
        cv.put(tx + tw, ty + th // 2, '☺', (170, 150, 130), FLOOR_BG)
        cv.text(tx + tw + 2, ty + th // 2 + 1, b, DIM, FLOOR_BG)
        cv.put(tx + tw // 2, ty + th, '@', YOU, FLOOR_BG)
        sx = x + 4
        ly = py + 18
        rule(cv, x, self.BW, ly)
        if gm is None:
            cv.text(tx + 3, ty + 2, 'Your stake', DIM, WOOD)
            for k, c in enumerate(self.stakes):
                on = k == self.si
                cv.text(tx + 3 + k * 6, ty + 4, f'{c}c', GOLD if on else DIM, WOOD)
                if on:
                    cv.put(tx + 3 + k * 6, ty + 5, '▲', GOLD, WOOD)
            if self.cun:
                cv.text(tx + 3, ty + 7, ('[x]' if self.loaded else '[ ]') + ' a loaded bone of your own', GOLD if self.loaded else DIM, WOOD)
            cv.wrap(sx, ly + 1, self.BW - 8, f'{a} and {b} make room for you. Each puts the stake in the pot; the first to '
                    f'bank {IG.WIN_AT} takes it all. Throw three bones, set one or more aside, throw the rest or bank. '
                    f'A skull ends your round with nothing, unless it is your first throw.', FG, PANEL, 4)
            cv.wrap(sx, ly + 6, self.BW - 8, self.twist, DIM, PANEL, 2)
            cv.text(sx, ly + 9, f'Tonight {IG.staked(g)}c of {IG.limit(g)}c', DIM, PANEL)
            keys(cv, x, y, self.BW, self.BH, '← →: stake · Enter: sit down · Esc: leave' +
                 (' · ↑: loaded bone' if self.cun else ''))
            return
        cv.text(tx + 3, ty + 1, 'Pot', DIM, WOOD)
        cv.text(tx + 3, ty + 2, f'{gm.pot}c', GOLD, WOOD)
        turn = gm.players[gm.cur]
        bx = tx + tw // 2 - 10
        if gm.thrown:
            for k, f in enumerate(gm.thrown):
                bone(cv, bx + k * 7, ty + 3, f, kept=gm.marked[k], cur=(k == self.sel and gm.phase == 'pick'))
                if gm.marked[k]:
                    cv.text(bx + k * 7, ty + 8, 'aside', GOLD, WOOD)
        elif gm.phase == 'throw':
            cv.text_center(tx + tw // 2, ty + 5, f'{gm.free} bone{"s" if gm.free > 1 else ""} in your hand', DIM, WOOD)
        if gm.phase != 'over':
            cv.text(tx + tw - 14, ty + 1, 'This round', DIM, WOOD)
            cv.text(tx + tw - 14, ty + 2, str(gm.round), FG, WOOD)
        ly2 = lines(cv, sx, ly + 1, self.BW - 8, gm.log, FG, 3)
        yy = max(ly + 5, ly2 + 1)
        cols = [(pl['name'], pl['banked']) for pl in gm.players]
        for k, (nm, v) in enumerate(cols):
            cv.text(sx + k * 16, yy, nm, GOLD if gm.players[k] is turn else DIM, PANEL)
            cv.text(sx + k * 16 + 8, yy, str(v), FG, PANEL)
        cv.text(sx + 50, yy, f'first to {IG.WIN_AT}', DIM, PANEL)
        cv.wrap(sx, yy + 2, self.BW - 8, self.twist, DIM, PANEL, 2)
        if gm.seen:
            cv.wrap(sx, yy + 5, self.BW - 8, f'{gm.seen}\'s bone lies a hair too still after each throw. Weighted.',
                    GOLD, PANEL, 2)
        cv.text(sx, yy + 8, f'Stake {gm.stake}c', FG, PANEL)
        cv.text(sx + 12, yy + 8, f'Tonight {IG.staked(g)}c of {IG.limit(g)}c', DIM, PANEL)
        if gm.phase == 'over':
            k = 'Enter: take your leave'
        elif gm.phase == 'throw':
            k = 'Enter: throw · Esc: leave'
        else:
            k = '← →: pick · ↑: aside · Enter: throw the rest · ↓: bank · Esc: leave'
        keys(cv, x, y, self.BW, self.BH, k)


def _place(g):
    m = g.map
    s = IG.settlement(g)
    inn = next((b.get('name') for b in getattr(m, 'buildings', ()) if isinstance(b, dict) and b.get('kind') == 'inn'
                and b.get('name')), None)
    where = s.name if s is not None else m.name
    return f'{inn}, {where}' if inn else where


# ====================================================================== The Count
SUITS = {'Stars': ('*', (200, 215, 255), (60, 70, 130)), 'Iron': ('■', (160, 160, 170), (70, 70, 80)),
         'Water': ('≈', (110, 170, 230), (40, 80, 140))}
CARD = (214, 202, 176)


def card(cv, x, y, n=None, suit=None, down=False):
    bg = (40, 52, 70) if down else CARD
    edge = (70, 90, 120) if down else (150, 138, 112)
    for yy in range(5):
        for xx in range(5):
            cv.put(x + xx, y + yy, ' ', None, bg)
    for k in range(5):
        cv.put(x + k, y, '▀', edge, bg)
        cv.put(x + k, y + 4, '▄', edge, bg)
    if down:
        for yy in (1, 2, 3):
            for xx in range(1, 4):
                cv.put(x + xx, y + yy, '≈' if (xx + yy) % 2 else '~', (80, 120, 170), bg)
        cv.put(x + 2, y + 2, '?', (210, 230, 255), bg)
        return
    sg, _col, ink = SUITS[suit]
    cv.text(x + 1, y + 1, str(n), (40, 30, 20), bg)
    cv.put(x + 2, y + 2, sg, ink, bg)
    cv.text_right(x + 4, y + 3, str(n), (40, 30, 20), bg)


class CountScreen(Modal):
    tall = False
    BW, BH = 76, 36

    def __init__(self, app, ctx):
        super().__init__(app)
        self.ctx = ctx
        self.place = _place(self.game)
        self.dealer = ctx.get('dealer') or 'the dealer'
        self.cun = IG.cunning(self.game)
        self.g = IG.Count()
        self.si = 0
        self.settled = True
        self.closed = False

    def stakes(self):
        g = self.game
        return [c for c in IG.STAKES if c <= IG.stake_room(g) and c <= g.player.gold]

    def on_key(self, tok, shift):
        gm, g = self.g, self.game
        if tok == 'esc':
            if gm.phase == 'play':
                g.msg('You throw in your hand. The stake stays with the dealer.')
                g.end_turn(3)
            self.app.pop()
            return
        if self.closed:
            if tok in ('enter', 'np_enter'):
                self.app.pop()
            return
        if gm.phase in ('stake', 'done'):
            st = self.stakes()
            if not st:
                if tok in ('enter', 'np_enter'):
                    self.app.pop()
                return
            self.si = min(self.si, len(st) - 1)
            if tok in ('left', 'np4'):
                self.si = max(0, self.si - 1)
            elif tok in ('right', 'np6'):
                self.si = min(len(st) - 1, self.si + 1)
            elif tok in ('enter', 'np_enter'):
                IG.put_stake(g, st[self.si])
                gm.deal(st[self.si])
                self.settled = False
                self.check()
            return
        if gm.phase == 'play':
            if tok in ('enter', 'np_enter'):
                gm.draw()
            elif tok in ('down', 'np2'):
                gm.stop()
            self.check()

    def check(self):
        gm = self.g
        if gm.phase == 'done' and not self.settled:
            self.settled = True
            if IG.count_hand(self.game, gm, bool(self.cun)) == 'barred':
                self.closed = True

    def render(self, cv):
        g, gm = self.game, self.g
        x, y = self.box(cv, self.BW, self.BH, f' The Count · {self.place} ')
        px, py, pw = x + 2, y + 2, self.BW - 4
        floor(cv, px, py, pw, 19)
        tx, ty, tw, th = px + 6, py + 2, pw - 12, 15
        table(cv, tx, ty, tw, th)
        cv.put(tx + tw // 2, ty - 1, '☺', REG, FLOOR_BG)
        cv.text(tx + tw // 2 + 2, ty - 1, f'{self.dealer} deals', DIM, FLOOR_BG)
        cv.put(tx + tw // 2, ty + th, '@', YOU, FLOOR_BG)
        show = gm.phase == 'done'
        dx = tx + tw - 10
        card(cv, dx, ty + 1, down=True)
        cv.text(dx - 1, ty + 6, 'the deck', DIM, WOOD)
        cv.text(dx, ty + 7, f'{len(gm.deck)} left', DIM, WOOD)
        if gm.dealer:
            cv.text(tx + 3, ty + 2, first(self.dealer), DIM, WOOD)
            cv.text(tx + 3, ty + 3, str(gm.total(gm.dealer)) if show else
                    _sum(gm.dealer[:1]) + ' + ?', FG, WOOD)
            for k, (n, s) in enumerate(gm.dealer[:6]):
                down = not show and (k == 1 or s == 'Water')
                card(cv, tx + 14 + k * 6, ty + 1, n, s, down)
        if gm.you:
            cv.text(tx + 3, ty + 9, 'You', GOLD, WOOD)
            cv.text(tx + 3, ty + 10, str(gm.total(gm.you)) if show else _sum(gm.you), FG, WOOD)
            for k, (n, s) in enumerate(gm.you[:6]):
                card(cv, tx + 14 + k * 6, ty + 8, n, s, not show and s == 'Water')
        sx = x + 4
        ly = py + 20
        rule(cv, x, self.BW, ly)
        st = self.stakes()
        if gm.phase in ('stake', 'done') and not self.closed:
            cv.text(dx - 2, ty + 9, 'Stake', DIM, WOOD)
            if st:
                self.si = min(self.si, len(st) - 1)
                cv.text(dx - 2, ty + 10, '  '.join(f'{c}c' for c in st), DIM, WOOD)
                off = sum(len(f'{c}c') + 2 for c in st[:self.si])
                cv.text(dx - 2 + off, ty + 10, f'{st[self.si]}c', GOLD, WOOD)
        elif gm.stake:
            cv.text(dx - 2, ty + 9, 'Stake', DIM, WOOD)
            cv.text(dx - 2, ty + 10, f'{gm.stake}c', GOLD, WOOD)
        yy = lines(cv, sx, ly + 1, self.BW - 8, gm.log or [f'{self.dealer} cuts the deck and waits for your stake.'], FG, 2)
        cv.wrap(sx, max(yy, ly + 3) + 1, self.BW - 8, 'Get as near to 21 as you dare; over it and the stake is the '
                'dealer\'s. Water cards lie face down until both of you stop: nobody counts the water.', DIM, PANEL, 3)
        if self.cun:
            by, high = gm.left()
            cv.wrap(sx, ly + 8, self.BW - 8, f'You have kept count: in the deck are {by["Stars"]} Stars, {by["Iron"]} '
                    f'Iron, {by["Water"]} Water; {high} high cards.', GOLD, PANEL, 2)
        cv.text(sx, ly + 11, f'Tonight {IG.staked(g)}c of {IG.limit(g)}c', DIM, PANEL)
        for k, (nm, (sg, col, _ink)) in enumerate(SUITS.items()):
            cv.put(sx + 22 + k * 10, ly + 11, sg, col, PANEL)
            cv.text(sx + 24 + k * 10, ly + 11, nm, DIM, PANEL)
        if self.closed:
            k = 'Enter: go'
        elif gm.phase == 'play':
            k = 'Enter: draw · ↓: stop · Esc: throw in'
        elif st:
            k = '← →: stake · Enter: deal · Esc: leave the table'
        else:
            k = 'No more stakes tonight · Esc: leave the table'
        keys(cv, x, y, self.BW, self.BH, k)


def _sum(hand):
    k = IG.Count.known(hand)
    h = IG.Count.hidden(hand)
    return ' + '.join(([str(k)] if k or not h else []) + ['?'] * h)


# ====================================================================== Vigil
IRON, WATCH, VAEL = (140, 140, 150), (190, 210, 240), (255, 214, 110)
N, CW, CH = IG.N, 4, 2


class VigilScreen(Modal):
    tall = False
    BW, BH = 76, 38

    def __init__(self, app, ctx):
        super().__init__(app)
        g = self.game
        self.ctx = ctx
        self.master = ctx.get('master')
        self.who = self.master or ctx.get('a') or 'a regular'
        self.strength = IG.strength(g, self.master)
        kind = IG.board_kind(IG.people(g))
        self.board_name, self.dark, self.light, self.rim, self.hearth = IG.BOARDS[kind]
        self.side_i = 0
        self.v = None
        self.cur = (4, 6)
        self.held = None
        self.settled = False

    def start(self):
        you = 'W' if self.side_i == 0 else 'I'
        self.v = IG.Vigil(you=you, strength=self.strength)
        self.cur = (4, 6) if you == 'W' else (4, 7)
        if self.v.turn != you:
            self.v.play(self.v.best())

    def on_key(self, tok, shift):
        v = self.v
        if v is None:
            if tok in ('left', 'np4', 'right', 'np6'):
                self.side_i = 1 - self.side_i
            elif tok in ('enter', 'np_enter'):
                self.start()
            elif tok == 'esc':
                self.app.pop()
            return
        if v.winner:
            if tok in ('enter', 'np_enter', 'esc'):
                self.settle()
                self.app.pop()
            return
        if tok == 'esc':
            v.winner = 'I' if v.you == 'W' else 'W'
            v.say('You tip over your Vael.' if v.you == 'W' else 'You sweep your Iron from the board.')
            return
        d = {'left': (-1, 0), 'np4': (-1, 0), 'right': (1, 0), 'np6': (1, 0), 'up': (0, -1), 'np8': (0, -1),
             'down': (0, 1), 'np2': (0, 1)}.get(tok)
        if d:
            self.cur = (max(0, min(N - 1, self.cur[0] + d[0])), max(0, min(N - 1, self.cur[1] + d[1])))
            return
        if tok in ('enter', 'np_enter'):
            c, r = self.cur
            i = r * N + c
            p = v.b[i]
            if self.held is not None and i in v.legal_from(*self.held):
                f = self.held[1] * N + self.held[0]
                self.held = None
                v.play((f, i))
                if not v.winner:
                    mv = v.best()
                    if mv:
                        v.play(mv)
            elif p != '.' and IG.Vigil.side(p) == v.you:
                self.held = None if self.held == (c, r) else (c, r)
            else:
                self.held = None

    def settle(self):
        if not self.settled and self.v is not None:
            self.settled = True
            IG.vigil_over(self.game, self.v, self.master)

    def render(self, cv):
        v = self.v
        x, y = self.box(cv, self.BW, self.BH, f' Vigil · {self.board_name} · {self.who} ')
        bx, by = x + 4, y + 3
        dots = set(v.legal_from(*self.held)) if v is not None and self.held else set()
        b = v.b if v is not None else IG.Vigil().b
        for r in range(N):
            cv.text(bx - 2, by + r * CH, str(N - r), DIM, PANEL)
            cv.put(bx + r * CW + 1, by + N * CH, 'abcdefghi'[r], DIM, PANEL)
        for r in range(N):
            for c in range(N):
                base = self.dark if (r + c) % 2 else self.light
                if r in (0, N - 1) or c in (0, N - 1):
                    base = mix(base, self.rim, .45)
                if (c, r) == IG.HEARTH:
                    base = self.hearth
                if (c, r) == self.held:
                    base = scale(base, 1.6)
                if v is not None and (c, r) == self.cur and not v.winner:
                    base = mix(base, (120, 100, 50), .55)
                for yy in range(CH):
                    for xx in range(CW):
                        cv.put(bx + c * CW + xx, by + r * CH + yy, ' ', None, base)
                p = b[r * N + c]
                ch, fg = {'V': ('☼', VAEL), 'W': ('○', WATCH), 'I': ('●', IRON)}.get(p, (None, None))
                if ch is None and (r * N + c) in dots:
                    ch, fg = '·', GOLD
                if ch:
                    cv.put(bx + c * CW + 1, by + r * CH, ch, fg, base)
        sx = bx + N * CW + 4
        you = 'W' if (v.you if v else ('W' if self.side_i == 0 else 'I')) == 'W' else 'I'
        cnt = {'W': sum(1 for p in b if p == 'W'), 'I': sum(1 for p in b if p == 'I')}
        for k, (side, nm) in enumerate((('W', 'the Watch'), ('I', 'the Iron'))):
            yy = by + k * 6
            cv.text(sx, yy, 'You' if side == you else first(self.who), GOLD, PANEL)
            cv.text(sx, yy + 1, nm, FG, PANEL)
            if side == 'W':
                cv.put(sx, yy + 2, '○', WATCH, PANEL)
                cv.text(sx + 2, yy + 2, f'{cnt["W"]} of 8', DIM, PANEL)
                cv.put(sx, yy + 3, '☼', VAEL, PANEL)
                cv.text(sx + 2, yy + 3, 'Vael', DIM, PANEL)
            else:
                cv.put(sx, yy + 2, '●', IRON, PANEL)
                cv.text(sx + 2, yy + 2, f'{cnt["I"]} of 16', DIM, PANEL)
            if side != you:
                cv.text(sx, yy + 4, {1: 'plays loosely', 2: 'plays steady', 3: 'plays like a master'}[self.strength],
                        DIM, PANEL)
        if v is not None:
            cv.text(sx, by + 12, 'Moves', DIM, PANEL)
            for k, s in enumerate(v.log[-5:]):
                cv.text(sx, by + 13 + k, s[:24], FG if k == len(v.log[-5:]) - 1 else DIM, PANEL)
        ly = by + N * CH + 2
        rule(cv, x, self.BW, ly)
        tx = x + 4
        if v is None:
            cv.text(tx, ly + 1, 'Play which side?', FG, PANEL)
            for k, nm in enumerate(IG.SIDES):
                on = k == self.side_i
                cv.text(tx + 20 + k * 16, ly + 1, nm, GOLD if on else DIM, PANEL)
            cv.wrap(tx, ly + 3, self.BW - 8, 'The Watch holds when Vael ☼ reaches the rim of the board. The Iron wins '
                    'when Vael is closed in on four sides. A piece caught between two foes is taken. The Iron moves first.',
                    DIM, PANEL, 4)
            keys(cv, x, y, self.BW, self.BH, '← →: side · Enter: begin · Esc: leave')
            return
        if v.winner:
            text = {True: 'You win. ' + ('The master looks at the board a long time, then nods.' if self.master else
                                         'They set the pieces up again, shaking their heads.'),
                    False: 'You lose. ' + ('"Again, some other night."' if self.master else '"Good game. Nearly."')}
            msg = 'A draw: the night runs out.' if v.winner == 'draw' else text[v.winner == v.you]
            cv.text(tx, ly + 1, msg, GOOD if v.winner == v.you else BAD if v.winner != 'draw' else FG, PANEL)
            keys(cv, x, y, self.BW, self.BH, 'Enter: done')
            return
        if self.held:
            cv.text(tx, ly + 1, 'Where can it go: the gold dots.', FG, PANEL)
        else:
            cv.text(tx, ly + 1, 'Your move.' if v.turn == v.you else 'They think.', FG, PANEL)
        cv.wrap(tx, ly + 3, self.BW - 8, ('Bring Vael ☼ to the rim and the Watch holds.' if v.you == 'W' else
                                         'Close Vael ☼ in on four sides; the hearth counts as yours.'), DIM, PANEL, 2)
        keys(cv, x, y, self.BW, self.BH, 'Arrows: move · Enter: pick up / set down · Esc: give up')


def screen(app, kind, ctx):
    return {'bones': BonesScreen, 'count': CountScreen, 'vigil': VigilScreen}[kind](app, ctx)

