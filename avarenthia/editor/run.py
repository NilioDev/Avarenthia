"""The editor's window: tcod and SDL. The whole screen is one console like the game's; the drawing area is drawn a
second time from a small console and laid over it bigger, so zoom makes the signs themselves bigger. Mouse
positions are turned into screen cells (floats) here, so screen.py never sees a pixel."""
import os
import sys

import tcod
import tcod.render

from .. import glyphs
from ..canvas import TcodCanvas
from . import screen as S

TITLE = 'Avarenthia Editor'


def _ks(name):
    v = getattr(tcod.event.KeySym, name, None)
    return int(v) if v is not None else None


NAMED = {}
for _name, _tok in [('UP', 'up'), ('DOWN', 'down'), ('LEFT', 'left'), ('RIGHT', 'right'), ('RETURN', 'enter'),
                    ('KP_ENTER', 'np_enter'), ('ESCAPE', 'esc'), ('BACKSPACE', 'backspace'), ('TAB', 'tab'),
                    ('SPACE', 'space'), ('DELETE', 'delete'), ('PAGEUP', 'pageup'), ('PAGEDOWN', 'pagedown'),
                    ('F5', 'f5'), ('F11', 'f11'), ('MINUS', '-'), ('EQUALS', '='), ('PLUS', '+'), ('KP_PLUS', '+'),
                    ('KP_MINUS', '-')]:
    _v = _ks(_name)
    if _v is not None:
        NAMED[_v] = _tok


def _mod(name, default):
    try:
        return int(getattr(tcod.event.Modifier, name))
    except (AttributeError, TypeError):
        return default


SHIFT, CTRL, GUI = _mod('SHIFT', 0x0003), _mod('CTRL', 0x00C0), _mod('GUI', 0x0C00)


def key_token(ev):
    """(token, shift, ctrl) of a KeyDown: letters always lower case (shift is told apart)."""
    sym, mod = int(ev.sym), int(ev.mod)
    shift, ctrl = bool(mod & SHIFT), bool(mod & (CTRL | GUI))
    if sym in NAMED:
        return NAMED[sym], shift, ctrl
    if 97 <= sym <= 122 or 48 <= sym <= 57:
        return chr(sym), shift, ctrl
    return None, shift, ctrl


def here():
    return getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def load_tileset():
    from .. import owntiles
    path = os.path.join(here(), 'assets', glyphs.SHEET)
    ts = tcod.tileset.load_tilesheet(path, glyphs.COLUMNS, glyphs.ROWS, glyphs.CHARMAP)
    owntiles.add_signs(ts)
    return ts


class View:
    """Draws the editor through SDL and knows where each screen cell lands in the window."""

    def __init__(self, ctx, tileset):
        self.ctx = ctx
        self.ren = ctx.sdl_renderer
        self.atlas = tcod.render.SDLTilesetAtlas(self.ren, tileset)
        self.main = tcod.render.SDLConsoleRender(self.atlas)
        self.zoomed = tcod.render.SDLConsoleRender(self.atlas)
        self.console = tcod.console.Console(S.W, S.H, order='F')
        self.k, self.ox, self.oy = 1, 0, 0

    def place(self):
        ow, oh = self.ren.output_size
        cw, ch = S.W * glyphs.TILE_W, S.H * glyphs.TILE_H
        self.k = max(1, min(ow // cw, oh // ch))
        self.ox, self.oy = (ow - cw * self.k) // 2, (oh - ch * self.k) // 2

    def cell(self, px, py):
        """Screen cell (floats) of a window pixel."""
        return ((px - self.ox) / (glyphs.TILE_W * self.k), (py - self.oy) / (glyphs.TILE_H * self.k))

    def draw(self, ed, present=True):
        """One frame. With a dialog open the drawing stays at its plain size under it."""
        self.place()
        cv = TcodCanvas(self.console)
        z = 1 if ed.dialog else ed.zoom
        ed.render(cv, draw_area=(z == 1))
        self.ren.draw_color = (0, 0, 0, 255)
        self.ren.clear()
        tw, th = glyphs.TILE_W * self.k, glyphs.TILE_H * self.k
        self.ren.copy(_sharp(self.main.render(self.console)), dest=(self.ox, self.oy, S.W * tw, S.H * th))
        if z > 1:
            vw, vh = ed.zoom_size()
            small = tcod.console.Console(vw, vh, order='F')
            ed.render_drawing(TcodCanvas(small), vw, vh)
            self.ren.copy(_sharp(self.zoomed.render(small)),
                          dest=(self.ox + S.AX * tw, self.oy + S.AY * th, vw * z * tw, vh * z * th))
        if present:
            self.ren.present()


def _sharp(tex):
    """Scaled by whole pixels, never smudged."""
    try:
        import tcod.sdl.render as R
        tex.scale_mode = R.ScaleMode.NEAREST
    except Exception:
        pass
    return tex


def toggle_fullscreen(ctx):
    try:
        ctx.sdl_window.fullscreen = not ctx.sdl_window.fullscreen
    except Exception:
        pass


def main(room=None):
    tileset = load_tileset()
    ed = S.Editor(room)
    k = 2
    try:
        from main import window_scale    # the game's own: the largest whole scale that fits the screen
        k = window_scale()
    except Exception:
        pass
    flags = getattr(tcod.context, 'SDL_WINDOW_RESIZABLE', 0x20)
    with tcod.context.new(columns=S.W, rows=S.H, width=S.W * glyphs.TILE_W * k, height=S.H * glyphs.TILE_H * k,
                          tileset=tileset, title=TITLE, vsync=True, sdl_window_flags=flags) as ctx:
        view = View(ctx, tileset)
        from .. import owntiles
        ed.on_signs = lambda: owntiles.add_signs(tileset)
        try:
            ctx.sdl_window.start_text_input()
        except Exception:
            pass
        while ed.running:
            view.draw(ed)
            for ev in tcod.event.wait(.5):
                handle(ed, view, ctx, ev)
                if not ed.running:
                    break
            if ed.want_try:
                ed.want_try = False
                from . import trying

                def say(s):
                    ed.say(s)
                    view.draw(ed)
                say('Opening the game on the piece...')
                ed.say(trying.run(ctx, tileset, ed.place or ed.room, say))
    return 0


def handle(ed, view, ctx, ev):
    if isinstance(ev, tcod.event.Quit):
        if ed.dirty() and not ed.quit_asked:
            ed.quit_asked = True
            ed.say('Not saved. Ctrl+S saves; close the window again to leave without saving.', True)
        else:
            ed.running = False
    elif isinstance(ev, tcod.event.KeyDown):
        tok, shift, ctrl = key_token(ev)
        ed.set_shift(shift)
        if tok == 'f11':
            toggle_fullscreen(ctx)
        elif tok:
            ed.msg = '' if not ed.field else ed.msg
            ed.key(tok, shift, ctrl)
    elif isinstance(ev, tcod.event.KeyUp):
        tok, shift, _ctrl = key_token(ev)
        ed.set_shift(shift)
        if tok:
            ed.key_up(tok)
    elif isinstance(ev, tcod.event.TextInput):
        ed.text(ev.text)
    elif isinstance(ev, (tcod.event.MouseButtonDown, tcod.event.MouseButtonUp, tcod.event.MouseMotion)):
        x, y = view.cell(*ev.position)
        if isinstance(ev, tcod.event.MouseMotion):
            ed.mouse('move', x, y)
        else:
            ed.msg = ''
            ed.mouse('down' if isinstance(ev, tcod.event.MouseButtonDown) else 'up', x, y, int(ev.button))
    elif isinstance(ev, tcod.event.MouseWheel):
        mx, my = getattr(ed, '_last_mouse', (S.AX + 1, S.AY + 1))
        ed.wheel(ev.y, mx, my)
    if isinstance(ev, tcod.event.MouseMotion):
        ed._last_mouse = view.cell(*ev.position)


def shot(ed, path, scale=2):
    """A picture of the editor as the window shows it (for the tests and the reports); needs no screen."""
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
    os.environ.setdefault('SDL_VIDEO_DRIVER', 'dummy')
    tileset = load_tileset()
    with tcod.context.new(columns=S.W, rows=S.H, width=S.W * glyphs.TILE_W * scale,
                          height=S.H * glyphs.TILE_H * scale, tileset=tileset, title=TITLE) as ctx:
        view = View(ctx, tileset)
        view.draw(ed, present=False)
        px = view.ren.read_pixels()
    from PIL import Image
    Image.fromarray(px[..., :3]).save(path)
    return path
