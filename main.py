"""Avarenthia - an ASCII action roguelike built on python-tcod.

Run:  python main.py
"""
import os
import sys
import time

import tcod

from avarenthia import glyphs
from avarenthia import debug as DBG
from avarenthia.canvas import TcodCanvas
from avarenthia import ui as UI
from avarenthia import engine as E
from avarenthia.ui import App

# When frozen by PyInstaller, bundled files live in sys._MEIPASS.
HERE = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))


def load_tileset():
    path = os.path.join(HERE, 'assets', glyphs.SHEET)
    ts = tcod.tileset.load_tilesheet(path, glyphs.COLUMNS, glyphs.ROWS, glyphs.CHARMAP)
    from avarenthia import owntiles, pieces
    pieces.load()                       # Nilio's own tiles and things, with their own signs
    owntiles.add_signs(ts)
    return ts


# ------------------------------------------------------------------ keyboard
def _ks(name):
    v = getattr(tcod.event.KeySym, name, None)
    return int(v) if v is not None else None


NAMED = {}
for _name, _tok in [('UP', 'up'), ('DOWN', 'down'), ('LEFT', 'left'), ('RIGHT', 'right'),
                    ('HOME', 'home'), ('END', 'end'), ('PAGEUP', 'pageup'), ('PAGEDOWN', 'pagedown'),
                    ('KP_ENTER', 'np_enter'), ('KP_PERIOD', '.'), ('F1', 'f1'), ('F2', 'f2'), ('F11', 'f11'), ('F12', 'f12'), ('DELETE', 'delete'),
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
    """The largest whole-number scale of the font (square 8x8 cells) whose window still fits on screen with room to spare."""
    tw, th = UI.BASE_W * glyphs.TILE_W, UI.BASE_H * glyphs.TILE_H
    size = screen_size()
    if not size:
        return 1
    sw, sh = size
    k = 1
    while tw * (k + 1) <= sw * .96 and th * (k + 1) <= sh * .94:
        k += 1
    return k


def main():
    if '--editor' in sys.argv[1:]:          # the Avarenthia Editor, from the source (the test download has its own)
        from avarenthia.editor.run import main as editor
        return editor()
    # the debug menu (F12): only in the test build, or from the source with --debug
    DBG.turn_on(sys.argv[1:], here=HERE, frozen=getattr(sys, 'frozen', False))
    tileset = load_tileset()
    # A normal window (not maximized), at the window size of the last run, or else sized to the largest
    # whole-number scale of the font that fits the screen so the pixels stay crisp. A bigger window shows more map
    # (up to 16:9), the rest of a very wide one is the margin; F11 goes fullscreen. Zoom (title screen) fixes the scale.
    st = E.load_settings()
    try:
        win_w, win_h = (int(v) for v in st.get('window', '').split('x'))
    except ValueError:
        k = window_scale()
        win_w, win_h = UI.BASE_W * glyphs.TILE_W * k, UI.BASE_H * glyphs.TILE_H * k
    console = tcod.console.Console(UI.BASE_W, UI.BASE_H, order='F')
    app = App(TcodCanvas(console))
    flags = getattr(tcod.context, 'SDL_WINDOW_RESIZABLE', 0x20)
    with tcod.context.new(columns=UI.BASE_W, rows=UI.BASE_H, width=win_w, height=win_h,
                          tileset=tileset, title='Avarenthia (test)' if DBG.ON else 'Avarenthia', vsync=True, sdl_window_flags=flags) as ctx:
        if st.get('fullscreen') == '1':
            toggle_fullscreen(ctx)
        console = fit(ctx, app)
        last_tick = 0.0
        while app.running:
            if app.want_window:            # the debug menu's Window size
                try:
                    ctx.sdl_window.fullscreen = False
                    ctx.sdl_window.size = app.want_window
                except Exception:
                    pass
                app.want_window = None
                app.relayout = True
            if app.relayout:
                console = fit(ctx, app)
            app.render()
            ctx.present(console, keep_aspect=True, integer_scaling=True)
            if app.shot:                   # a note for Claude asked for a picture of this frame
                try:
                    ctx.save_screenshot(app.shot)
                except Exception:
                    pass
                DBG.add_shot(app)
                app.shot = None
            timeout = app.frame_delay()
            if app.cv is not app.full:     # the margin drifts a cell a minute, also while nothing else moves
                timeout = min(timeout, 15.0) if timeout is not None else 15.0
            if app.auto:
                timeout = max(.005, app.auto_delay - (time.monotonic() - last_tick))
            pressed = False
            for ev in tcod.event.wait(timeout):
                if isinstance(ev, tcod.event.Quit):
                    app.quit()
                elif isinstance(ev, tcod.event.WindowResized) or getattr(ev, 'type', '') in ('WINDOWRESIZED', 'WINDOWSIZECHANGED'):
                    console = fit(ctx, app)
                elif isinstance(ev, tcod.event.KeyDown):
                    tok, shift = key_token(ev)
                    pressed = True
                    if tok == 'f11' or (tok == 'enter' and int(ev.mod) & int(getattr(tcod.event.Modifier, 'ALT', 0x0300))):
                        toggle_fullscreen(ctx)
                        console = fit(ctx, app)
                    elif tok:
                        app.key(tok, shift)
                if not app.running:
                    break
            if app.auto and not pressed and time.monotonic() - last_tick >= app.auto_delay * .9:
                last_tick = time.monotonic()
                app.tick()
        remember_window(ctx)


def pixel_size(ctx):
    """The window's drawing area in pixels (on a high-density screen more than its size in window units)."""
    for get in (lambda: ctx.sdl_renderer.output_size, lambda: ctx.sdl_window.size):
        try:
            w, h = get()
            if w > 0 and h > 0:
                return int(w), int(h)
        except Exception:
            pass
    return UI.BASE_W * glyphs.TILE_W, UI.BASE_H * glyphs.TILE_H


def fit(ctx, app):
    """A console of the window's size in cells at the chosen scale; the game in its middle part, the margin round it."""
    app.relayout = False
    pw, ph = pixel_size(ctx)
    k, cols, rows, rect = UI.layout(pw, ph, app.zoom, glyphs.TILE_W)
    console = tcod.console.Console(cols, rows, order='F')
    app.resize(TcodCanvas(console), rect)
    return console


def remember_window(ctx):
    """The window's size and fullscreen for the next start."""
    try:
        win = ctx.sdl_window
        full = bool(win.fullscreen)
        kw = {'fullscreen': int(full)}
        if not full:
            w, h = win.size
            kw['window'] = f'{int(w)}x{int(h)}'
        E.save_settings(**kw)
    except Exception:
        pass

if __name__ == '__main__':
    sys.exit(main())
