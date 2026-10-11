"""Umbrathyn - an ASCII action roguelike built on python-tcod.

Run:  python main.py
"""
import os
import sys
import time

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
                    ('KP_ENTER', 'np_enter'), ('KP_PERIOD', '.'), ('F1', 'f1'), ('F2', 'f2'), ('F11', 'f11'), ('DELETE', 'delete'),
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
    if sym == 59:
        return (':' if shift else ';'), False
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


def toggle_fullscreen(ctx):
    try:
        win = ctx.sdl_window
        win.fullscreen = not win.fullscreen
    except Exception:
        pass


def screen_size():
    """Usable size of the main screen in window units, or None if it cannot be found."""
    if sys.platform == 'win32':
        try:
            import ctypes
            class RECT(ctypes.Structure):
                _fields_ = [('l', ctypes.c_long), ('t', ctypes.c_long), ('r', ctypes.c_long), ('b', ctypes.c_long)]
            r = RECT()
            if ctypes.windll.user32.SystemParametersInfoW(0x30, 0, ctypes.byref(r), 0):   # SPI_GETWORKAREA
                return r.r - r.l, r.b - r.t
        except Exception:
            pass
    try:
        import importlib
        tkinter = importlib.import_module('tkinter')   # not bundled into the executable; optional
        root = tkinter.Tk()
        root.withdraw()
        size = root.winfo_screenwidth(), root.winfo_screenheight() - 80
        root.destroy()
        return size
    except Exception:
        return None


def window_scale():
    """The largest whole-number scale of the 8x16 font whose window still fits on screen with room to spare."""
    tw, th = W * glyphs.TILE_W, H * glyphs.TILE_H
    size = screen_size()
    if not size:
        return 1
    sw, sh = size
    k = 1
    while tw * (k + 1) <= sw * .96 and th * (k + 1) <= sh * .94:
        k += 1
    return k


def main():
    tileset = load_tileset()
    console = tcod.console.Console(W, H, order='F')
    app = App(TcodCanvas(console))
    # A normal window (not maximized, not fullscreen), sized to the largest whole-number scale of the
    # 8x16 font that fits the screen so the pixels stay crisp. It can still be resized; F11 goes fullscreen.
    k = window_scale()
    flags = getattr(tcod.context, 'SDL_WINDOW_RESIZABLE', 0x20)
    with tcod.context.new(columns=W, rows=H, width=W * glyphs.TILE_W * k, height=H * glyphs.TILE_H * k,
                          tileset=tileset, title='Umbrathyn', vsync=True, sdl_window_flags=flags) as ctx:
        last_tick = 0.0
        while app.running:
            app.render()
            ctx.present(console, keep_aspect=True, integer_scaling=True)
            timeout = 1 / 30 if app.animating() else None
            if app.auto:
                timeout = max(.005, app.auto_delay - (time.monotonic() - last_tick))
            pressed = False
            for ev in tcod.event.wait(timeout):
                if isinstance(ev, tcod.event.Quit):
                    app.quit()
                elif isinstance(ev, tcod.event.KeyDown):
                    tok, shift = key_token(ev)
                    pressed = True
                    if tok == 'f11' or (tok == 'enter' and int(ev.mod) & int(getattr(tcod.event.Modifier, 'ALT', 0x0300))):
                        toggle_fullscreen(ctx)
                    elif tok:
                        app.key(tok, shift)
                if not app.running:
                    break
            if app.auto and not pressed and time.monotonic() - last_tick >= app.auto_delay * .9:
                last_tick = time.monotonic()
                app.tick()


if __name__ == '__main__':
    sys.exit(main())
