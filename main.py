"""Cursed Vale - an ASCII action roguelike built on python-tcod.

Run:  python main.py
"""
import os
import sys
import warnings

import tcod

from cursed_vale import glyphs
from cursed_vale.canvas import TcodCanvas
from cursed_vale.ui import App, W, H

# When frozen by PyInstaller, bundled files live in sys._MEIPASS.
HERE = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))


def load_tileset():
    path = os.path.join(HERE, 'assets', glyphs.SHEET)
    return tcod.tileset.load_tilesheet(path, glyphs.COLUMNS, glyphs.ROWS, glyphs.CHARMAP)


# ------------------------------------------------------------------ keyboard
def _ks(name):
    v = getattr(tcod.event.KeySym, name, None)
    return int(v) if v is not None else None


NAMED = {}
for _name, _tok in [('UP', 'up'), ('DOWN', 'down'), ('LEFT', 'left'), ('RIGHT', 'right'),
                    ('HOME', 'home'), ('END', 'end'), ('PAGEUP', 'pageup'), ('PAGEDOWN', 'pagedown'),
                    ('KP_ENTER', 'np_enter'), ('KP_PERIOD', '.'), ('F1', 'f1'), ('F11', 'f11'), ('DELETE', 'delete'),
                    ('RETURN', 'enter'), ('ESCAPE', 'esc'), ('BACKSPACE', 'backspace'), ('TAB', 'tab'), ('SPACE', 'space')]:
    _v = _ks(_name)
    if _v is not None:
        NAMED[_v] = _tok
for _d in range(10):
    _v = _ks(f'KP_{_d}')
    if _v is not None:
        NAMED[_v] = f'np{_d}'

try:
    SHIFT = int(tcod.event.Modifier.SHIFT)
except AttributeError:
    SHIFT = 0x0003


def key_token(ev):
    """Turn a KeyDown event into a layout-independent token used by the UI."""
    sym = int(ev.sym)
    shift = bool(int(ev.mod) & SHIFT)
    if sym in NAMED:
        return NAMED[sym], shift
    if 97 <= sym <= 122:
        c = chr(sym)
        return (c.upper() if shift else c), shift
    if 48 <= sym <= 57:
        return chr(sym), shift
    if sym == 46:
        return ('>' if shift else '.'), False
    if sym == 44:
        return ('<' if shift else ','), False
    if sym == 47:
        return ('?' if shift else '/'), False
    if sym == 13:
        return 'enter', shift
    if sym == 27:
        return 'esc', shift
    if sym == 8:
        return 'backspace', shift
    if sym == 9:
        return 'tab', shift
    if sym == 32:
        return 'space', shift
    return None, shift


def tile_of(ctx, ev):
    """Tile coordinates of a mouse event, across tcod versions."""
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        conv = ctx.convert_event(ev)
        e = conv if conv is not None else ev
        pos = getattr(e, 'tile', None)
        if pos is None:
            pos = getattr(e, 'position', None)
    if pos is None:
        return None
    return int(pos[0]), int(pos[1])


def toggle_fullscreen(ctx):
    try:
        win = ctx.sdl_window
        win.fullscreen = not win.fullscreen
    except Exception:
        pass


def main():
    tileset = load_tileset()
    console = tcod.console.Console(W, H, order='F')
    app = App(TcodCanvas(console))
    # Open resizable and maximized: the 8x16 font is then drawn at the largest whole-number
    # scale that fits the screen (2x on a 1080p monitor), so pixels stay crisp.
    flags = getattr(tcod.context, 'SDL_WINDOW_RESIZABLE', 0x20) | getattr(tcod.context, 'SDL_WINDOW_MAXIMIZED', 0x80)
    with tcod.context.new(columns=W, rows=H, tileset=tileset, title='Cursed Vale', vsync=True,
                          sdl_window_flags=flags) as ctx:
        while app.running:
            app.render()
            ctx.present(console, keep_aspect=True, integer_scaling=True)
            timeout = 1 / 30 if app.animating() else None
            for ev in tcod.event.wait(timeout):
                if isinstance(ev, tcod.event.Quit):
                    app.quit()
                elif isinstance(ev, tcod.event.KeyDown):
                    tok, shift = key_token(ev)
                    if tok == 'f11' or (tok == 'enter' and int(ev.mod) & int(getattr(tcod.event.Modifier, 'ALT', 0x0300))):
                        toggle_fullscreen(ctx)
                    elif tok:
                        app.key(tok, shift)
                elif isinstance(ev, tcod.event.MouseMotion):
                    app.hover = tile_of(ctx, ev)
                elif isinstance(ev, tcod.event.MouseButtonDown):
                    t = tile_of(ctx, ev)
                    if t:
                        app.click(t[0], t[1], int(getattr(ev, 'button', 1)))
                if not app.running:
                    break


if __name__ == '__main__':
    sys.exit(main())
