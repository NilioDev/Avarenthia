"""A thin drawing layer over a tcod console, plus a pure-Python stand-in for tests."""

BLACK = (0, 0, 0)


def scale(c, f):
    return (int(c[0] * f), int(c[1] * f), int(c[2] * f))


def mix(a, b, f):
    return (int(a[0] + (b[0] - a[0]) * f), int(a[1] + (b[1] - a[1]) * f), int(a[2] + (b[2] - a[2]) * f))


class Canvas:
    """Common drawing helpers. Subclasses implement put/clear/dim."""
    w = h = 0

    def put_bg(self, x, y, bg):
        """Change only the background colour of a cell."""
        raise NotImplementedError

    def text(self, x, y, s, fg=None, bg=None, maxw=None):
        if maxw is not None and len(s) > maxw:
            s = s[:max(0, maxw - 1)] + '…' if maxw > 0 else ''
        for i, ch in enumerate(s):
            self.put(x + i, y, ch, fg, bg)
        return len(s)

    def text_center(self, cx, y, s, fg=None, bg=None):
        self.text(cx - len(s) // 2, y, s, fg, bg)

    def text_right(self, rx, y, s, fg=None, bg=None):
        self.text(rx - len(s) + 1, y, s, fg, bg)

    def fill(self, x, y, w, h, ch=' ', fg=None, bg=None):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.put(xx, yy, ch, fg, bg)

    def frame(self, x, y, w, h, fg, bg=None, title=None, title_fg=None):
        self.fill(x, y, w, h, ' ', fg, bg)
        for xx in range(x + 1, x + w - 1):
            self.put(xx, y, '─', fg, bg)
            self.put(xx, y + h - 1, '─', fg, bg)
        for yy in range(y + 1, y + h - 1):
            self.put(x, yy, '│', fg, bg)
            self.put(x + w - 1, yy, '│', fg, bg)
        self.put(x, y, '┌', fg, bg)
        self.put(x + w - 1, y, '┐', fg, bg)
        self.put(x, y + h - 1, '└', fg, bg)
        self.put(x + w - 1, y + h - 1, '┘', fg, bg)
        if title:
            t = f' {title} '
            self.text(x + 2, y, t, title_fg or fg, bg)

    def wrap(self, x, y, w, s, fg=None, bg=None, max_lines=99):
        lines = wrap_text(s, w)
        for i, ln in enumerate(lines[:max_lines]):
            self.text(x, y + i, ln, fg, bg)
        return min(len(lines), max_lines)


# what the lower half of a doubled row shows, so lines and boxes stay joined
_DOWN = {'│': '│', '┌': '│', '┐': '│', '├': '│', '┤': '│', '┼': '│', '┬': '│', '║': '║', '╔': '║', '╗': '║',
         '╠': '║', '╣': '║', '╬': '║', '╦': '║', '█': '█', '▌': '▌', '▐': '▐', '░': '░', '▒': '▒', '▓': '▓'}


class TallCanvas(Canvas):
    """Draws on another canvas with every row two rows tall. Screens laid out in rows of text (menus, sheets,
    dialogs) look roomy this way with the square 8x8 font: each line of text gets a blank line under it."""

    def __init__(self, base):
        self.base = base
        self.w, self.h = base.w, base.h // 2

    def put(self, x, y, ch, fg=None, bg=None):
        b = self.base
        b.put(x, y * 2, ch, fg, bg)
        low = _DOWN.get(ch)
        if low:
            b.put(x, y * 2 + 1, low, fg, bg)
        elif bg is not None:
            b.put(x, y * 2 + 1, ' ', fg, bg)

    def put_bg(self, x, y, bg):
        self.base.put_bg(x, y * 2, bg)
        self.base.put_bg(x, y * 2 + 1, bg)

    def clear(self, bg=BLACK):
        self.base.clear(bg)

    def dim(self, f):
        self.base.dim(f)


def wrap_text(s, w):
    out = []
    for para in s.split('\n'):
        if not para:
            out.append('')
            continue
        cur = ''
        for word in para.split(' '):
            if not cur:
                cur = word
            elif len(cur) + 1 + len(word) <= w:
                cur += ' ' + word
            else:
                out.append(cur)
                cur = word
        out.append(cur)
    return out


class TcodCanvas(Canvas):
    def __init__(self, console):
        self.con = console
        self.w, self.h = console.width, console.height

    def put(self, x, y, ch, fg=None, bg=None):
        if 0 <= x < self.w and 0 <= y < self.h:
            c = self.con
            c.ch[x, y] = ord(ch)
            if fg is not None:
                c.fg[x, y] = fg
            if bg is not None:
                c.bg[x, y] = bg

    def put_bg(self, x, y, bg):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.con.bg[x, y] = bg

    def clear(self, bg=BLACK):
        self.con.clear(ch=ord(' '), fg=(255, 255, 255), bg=bg)

    def dim(self, f):
        c = self.con
        c.fg[...] = (c.fg * f).astype(c.fg.dtype)
        c.bg[...] = (c.bg * f).astype(c.bg.dtype)

    def get(self, x, y):
        """(ch, fg, bg) of a cell, for effects drawn over what is already there."""
        c = self.con
        return chr(c.ch[x, y]), tuple(int(v) for v in c.fg[x, y]), tuple(int(v) for v in c.bg[x, y])


from .glyphs import CHARS as _GLYPHS  # noqa: E402


class FakeCanvas(Canvas):
    """Pure-Python canvas used by the headless tests. dump() returns the screen as text."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.clear()

    def put(self, x, y, ch, fg=None, bg=None):
        if ch not in _GLYPHS:
            raise ValueError(f'character {ch!r} is not in the tileset')
        if 0 <= x < self.w and 0 <= y < self.h:
            i = y * self.w + x
            self.ch[i] = ch
            if fg is not None:
                self.fg[i] = fg
            if bg is not None:
                self.bg[i] = bg

    def put_bg(self, x, y, bg):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.bg[y * self.w + x] = bg

    def clear(self, bg=BLACK):
        n = self.w * self.h
        self.ch = [' '] * n
        self.fg = [(255, 255, 255)] * n
        self.bg = [bg] * n

    def dim(self, f):
        self.fg = [scale(c, f) for c in self.fg]
        self.bg = [scale(c, f) for c in self.bg]

    def get(self, x, y):
        i = y * self.w + x
        return self.ch[i], tuple(self.fg[i]), tuple(self.bg[i])

    def dump(self):
        return '\n'.join(''.join(self.ch[y * self.w:(y + 1) * self.w]) for y in range(self.h))
