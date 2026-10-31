"""Ctrl+T in the editor: making an own tile or thing (owntiles.py). A tile has a name, a sign (one of the tileset, or
an own 8 x 8 drawn here), two colours, what it is like, and a look line; a thing blocks the way and/or sight and may
do one of the things a telling thing does. The preview shows it lit and remembered on a patch of floor. Saving writes
it into `my tiles.des` beside your pieces, and it joins the palette under MY TILES or MY THINGS."""
from .. import data as D
from .. import glyphs
from .. import owntiles as OT
from ..canvas import scale
from . import files as F
from .model import DOES

DX, DY = 4, 5                       # the dialog's corner
SX, SY, SCOLS = 40, 8, 64            # the tileset's signs: where, how many to a row


def _rgb(h, default=(200, 192, 176)):
    try:
        return D.hexrgb(h) if h else default
    except (ValueError, IndexError):
        return default


class Maker:
    def maker_dialog(self, o=None):
        """Open the maker on a new thing, or on an own one to change it."""
        if o is None:
            o = OT.Own('TILE', 'my tile')
            o.sign, o.fg = '.', '#7a9a6a'
        else:
            src = o
            o = OT.Own(src.kind, src.name)
            for k in OT.Own.__slots__:
                setattr(o, k, getattr(src, k))
            o.pixels = list(src.pixels) if src.pixels else None
        self.dialog = ('maker', {'own': o, 'old': o.name if o.name in OT.OWN else None, 'pixels': o.pixels or
                                 ['........'] * 8})

    def maker_warnings(self, o):
        out = []
        if o.sign != 'own' and o.sign.isalpha() and any(d['ch'] == o.sign for d in D.MONSTERS.values()):
            who = next(d['name'] for d in D.MONSTERS.values() if d['ch'] == o.sign)
            out.append(f'The sign {o.sign} is also a creature ({who} and more): a player may take it for one.')
        if o.name in {t.name for i, t in enumerate(D.TILES) if i < OT.BASE}:
            out.append('The game has a tile of that name already: pick another name.')
        if not o.name.strip():
            out.append('It needs a name.')
        return out

    def maker_click(self, x, y, button):
        st = self.dialog[1]
        o = st['own']
        y = int(y)
        if y == 8 and 6 <= x < 30:
            o.kind = 'TILE' if x < 14 else 'OBJECT'
        elif y == 10:
            self.ask_line('Its name', o.name, lambda s: self._maker_set('name', s.strip()))
        elif y == 12:
            if o.sign == 'own':
                o.sign = '?'
            else:
                o.sign = 'own'
                o.pixels = st['pixels']
        elif y == 14:
            self.ask_line('The sign\'s colour, #rrggbb', o.fg, lambda s: self._maker_set('fg', s.strip()))
        elif y == 15:
            self.ask_line('The colour behind it, #rrggbb (empty: none)', o.bg or '',
                          lambda s: self._maker_set('bg', s.strip() or None))
        elif y == 17:
            if o.kind == 'TILE':
                ks = list(OT.LIKES)
                o.like = ks[(ks.index(o.like) + (1 if button == 1 else -1)) % len(ks)]
            else:
                o.blocks = OT.BLOCKS[(OT.BLOCKS.index(o.blocks) + (1 if button == 1 else -1)) % len(OT.BLOCKS)]
        elif y == 18 and o.kind == 'OBJECT':
            self.ask_pick('What it does when you walk into it', [('nothing (its look line)', None)] +
                          [(a, a) for a in sorted(DOES)], lambda a: self._maker_set('does', a))
        elif 20 <= y <= 22:
            self.ask_line('Its look line', o.look, lambda s: self._maker_set('look', s.strip()))
        elif o.sign == 'own' and 29 <= y < 37 and 6 <= x < 22:
            r, c = y - 29, int(x - 6) // 2
            row = list(st['pixels'][r])
            row[c] = '.' if row[c] == '#' else '#'
            st['pixels'][r] = ''.join(row)
            o.pixels = st['pixels']
        elif SX <= x < SX + SCOLS and SY <= y < SY + 12:
            i = (y - SY) * SCOLS + int(x - SX)
            if i < len(glyphs.CHARS):
                o.sign = glyphs.CHARS[i]
        elif x >= SX and 24 <= y < 52:
            mine = sorted(OT.OWN.values(), key=lambda q: q.name)
            i = y - 24
            if 0 <= i < len(mine):
                self.maker_dialog(mine[i])
        elif y == 52 and 6 <= x < 30:
            self.maker_save()

    def _maker_set(self, key, v):
        st = self.dialog[1] if self.dialog and self.dialog[0] == 'maker' else self._maker_back
        setattr(st['own'], key, v)

    def ask_line(self, *a):                  # the maker comes back after a line or a pick
        self._remember_maker()
        super().ask_line(*a)

    def ask_pick(self, *a):
        self._remember_maker()
        super().ask_pick(*a)

    def _remember_maker(self):
        if self.dialog and self.dialog[0] == 'maker':
            self._maker_back = self.dialog[1]
        else:
            self._maker_back = None

    def after_small_dialog(self):
        """When a line or a pick closes, go back to the maker if it opened them."""
        back = getattr(self, '_maker_back', None)
        if back is not None and self.dialog is None:
            self.dialog = ('maker', back)
        self._maker_back = None

    def maker_save(self):
        st = self.dialog[1]
        o = st['own']
        if o.sign == 'own':
            o.pixels = list(st['pixels'])
        else:
            o.pixels = None
        bad = [w for w in self.maker_warnings(o) if 'pick another' in w or 'needs a name' in w]
        if bad:
            self.say(bad[0], True)
            return False
        try:
            OT.read(o.kind, o.name, o.text().split('\n')[1:-2], 'the maker')
        except ValueError as e:
            self.say(str(e).split(': ', 1)[-1], True)
            return False
        path = F.save_own(o, st.get('old'))
        st['old'] = o.name
        self.say(f'Saved in {path.rsplit("/", 1)[-1]}: {o.name} is under MY {"TILES" if o.kind == "TILE" else "THINGS"}.')
        return True

    # ------------------------------------------------------------ drawing it
    def render_maker(self, cv):
        from . import screen as S
        st = self.dialog[1]
        o = st['own']
        P = S.PANEL
        cv.frame(DX, DY, 102, 50, S.GOLD, P, 'Ctrl+T: make a tile or a thing', S.GOLD)
        cv.text(6, 7, 'MAKE A', S.DIM, P)
        cv.text(6, 8, ('■' if o.kind == 'TILE' else '□') + ' tile', S.GOLD if o.kind == 'TILE' else S.FG, P)
        cv.text(14, 8, ('■' if o.kind == 'OBJECT' else '□') + ' thing', S.GOLD if o.kind == 'OBJECT' else S.FG, P)
        rows = [(10, 'Name', o.name), (12, 'Sign', 'own, drawn below' if o.sign == 'own' else o.sign),
                (14, 'Colour', o.fg), (15, 'Behind it', o.bg or 'none')]
        if o.kind == 'TILE':
            rows.append((17, 'Is like', o.like))
        else:
            rows += [(17, 'Blocks', o.blocks), (18, 'Does', o.does or 'nothing')]
        for y, lab, val in rows:
            cv.text(6, y, lab, S.DIM, P)
            cv.fill(17, y, 20, 1, ' ', S.FG, S.FIELD)
            cv.text(17, y, val[:20], S.FG, S.FIELD)
        cv.text(6, 20, 'Look', S.DIM, P)
        cv.wrap(17, 20, 21, o.look or '(click to write it)', S.FG if o.look else S.DIM, P, 3)
        # the preview: lit, and remembered
        cv.text(6, 24, 'LIT      REMEMBERED', S.DIM, P)
        ch = chr(OT.sign_cp(o.name)) if o.sign == 'own' and o.name in OT.OWN and OT.OWN[o.name].sign == 'own' \
            else ('?' if o.sign == 'own' else o.sign)
        fl = D.TILES[D.FLOOR]
        fg, bg = _rgb(o.fg), _rgb(o.bg, (20, 18, 16))
        for k, f in ((6, 1), (15, .45)):
            for dy in range(3):
                for dx in range(5):
                    cv.put(k + dx, 25 + dy, fl.ch, scale(fl.fg, f), scale((20, 18, 16), f))
            cv.put(k + 2, 26, ch, scale(fg, f), scale(bg, f))
        if o.sign == 'own':
            cv.text(6, 28, 'ITS 8 X 8 SIGN: CLICK TO DRAW', S.DIM, P)
            for r, row in enumerate(st['pixels']):
                for c, px in enumerate(row):
                    cv.put(6 + c * 2, 29 + r, '█' if px == '#' else '·', fg if px == '#' else S.DIM, P)
                    cv.put(7 + c * 2, 29 + r, '█' if px == '#' else ' ', fg, P)
        y = 39
        for w in self.maker_warnings(o):
            y += cv.wrap(6, y, 32, '! ' + w, S.GOLD, P, 4)
        cv.text(6, 52, 'Enter', S.GOLD, P)
        cv.text(12, 52, 'save it', S.FG, P)
        cv.text(21, 52, 'Esc', S.GOLD, P)
        cv.text(25, 52, 'back', S.FG, P)
        cv.text(SX, 7, 'SIGNS OF THE TILESET: CLICK ONE', S.DIM, P)
        for i, c in enumerate(glyphs.CHARS):
            x, yy = SX + i % SCOLS, SY + i // SCOLS
            on = c == o.sign
            cv.put(x, yy, c, S.GOLD if on else S.FG, S.SEL if on else P)
        cv.text(SX, 22, 'MY TILES AND THINGS: CLICK ONE TO CHANGE IT', S.DIM, P)
        for i, q in enumerate(sorted(OT.OWN.values(), key=lambda q: q.name)[:28]):
            t = D.TILES[OT.IDS[q.name]]
            cv.put(SX, 24 + i, t.ch, t.fg, t.bg or P)
            cv.text(SX + 2, 24 + i, f"{q.name} ({'tile' if q.kind == 'TILE' else 'thing'})"[:60], S.FG, P)
