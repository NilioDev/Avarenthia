"""F5 in the editor: Try. The game opens in its test mode (the debug menu on F12) on a classic dungeon level with the
piece in it, the hero standing at its way in. Esc (on the map itself) or death goes back to the editor.

A level cannot be made without a world, so Try makes one small test world the first time and keeps it beside your
pieces (`try world.sav`); every Try starts again from that same world, never from your own save, which Try never
touches (what the game saves while you try goes to `try play.sav`)."""
import os
import pickle
import zlib

from .. import engine as E
from .. import pieces as P
from . import files as F

WORLD = 'try world.sav'
PLAY = 'try play.sav'
SEED = 4711


def piece_of(room):
    """The room as a piece the game can set into a level: a theme room (its own part only matters in a world)."""
    p = P.parse(room.text(), 'try', checked=True)[0]
    p.part = 'middle'
    p.depth = 0
    p.kinds = ['any']
    return p


def world(say=None):
    """The kept test world (made once). say(text) tells what is going on while it is made."""
    path = os.path.join(F.home(), WORLD)
    try:
        with open(path, 'rb') as f:
            raw = f.read()
        g = pickle.loads(zlib.decompress(raw[len(E.SAVE_MAGIC):]))
        if getattr(g, 'version', 0) == E.SAVE_VERSION:
            return g
    except Exception:
        pass
    if say:
        say('Making a small test world, once (it is kept for the next Try)...')
    g = E.Game('Tester', False, SEED, 'human', 'male')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(E.SAVE_MAGIC + zlib.compress(pickle.dumps(g, protocol=pickle.HIGHEST_PROTOCOL), 6))
    return g


def start_place(doc, say=None):
    """A game standing at the west edge of the whole place, on its ground floor, or (None, why not)."""
    from .. import debug as DBG
    from .. import drawnplaces as DP
    from ..sites import Site
    try:
        pl = doc.to_place()
    except (DP.Bad, P.Bad, ValueError) as e:
        return None, str(e).split(': ', 2)[-1]
    DP._ALL = [q for q in DP.load() if q.name != pl.name] + [pl]     # until the editor reads the places again
    for fl in pl.floors:
        P.EXTRA[fl.piece.name] = fl.piece
    g = world(say)
    g.hook()
    DBG.ON = True
    w, m = g.world, g.maps['over']
    taken = {(q.x, q.y) for q in w.sites} | {(q.x, q.y) for q in w.settlements} | \
        {(d.x, d.y) for d in w.dungeons.values()}
    p = g.player
    px, py = (p.x, p.y) if g.cur == 'over' else getattr(g, 'over_pos', (p.x, p.y))
    from .. import data as D
    spot = next(((x, y) for r in range(1, 30) for x in range(px - r, px + r + 1) for y in range(py - r, py + r + 1)
                 if m.inb(x, y) and (x, y) not in taken and D.TILES[m.tile(x, y)].walk
                 and m.tile(x, y) not in (D.ROAD, D.TOWN, D.CITY, D.RIVER)), None)
    if spot is None:
        return None, 'no free cell in the test world for the place'
    st = Site(len(w.sites), 'drawn', spot[0], spot[1], pl.name)
    st.place = pl.name
    w.sites.append(st)
    DP.setup(g, w, st, pl)
    DBG.to_over(g, *spot)
    g.enter_site(st.id)
    return g, ''


def start(room, say=None):
    """A game standing at the piece's door, or (None, why not)."""
    from .model import PlaceDoc
    if isinstance(room, PlaceDoc):
        return start_place(room, say)
    from .. import debug as DBG
    try:
        pc = piece_of(room)
    except P.Bad as e:
        return None, str(e).split(': ', 2)[-1]
    P._ALL = [q for q in P.load() if q.name != pc.name] + [pc]     # until the editor reads the pieces again
    g = world(say)
    g.hook()
    DBG.ON = True
    DBG.theme_level(g, pc.name)
    m = g.map
    if not any(r[2] == pc.name for r in getattr(m, 'rooms', [])):
        return None, 'the level would not take the piece this time; press F5 again'
    return g, ''


class SaveElsewhere:
    """While trying, the game saves into try play.sav, never into your own save."""

    def __enter__(self):
        self.real = E.save_path
        E.save_path = lambda: os.path.join(F.home(), PLAY)
        return self

    def __exit__(self, *a):
        E.save_path = self.real


def run(ctx, tileset, room, say=None):
    """Play the piece in the editor's window until Esc on the map or death. Returns a line for the status bar."""
    try:
        with SaveElsewhere():
            return _play(ctx, room, say)
    finally:
        P.load(force=True)                       # the game's pieces again, without the one tried
        from .. import drawnplaces as DP
        DP.load(force=True)


def _play(ctx, room, say):
    import tcod
    from ..canvas import TcodCanvas
    from .. import ui as U
    from main import key_token
    g, why = start(room, say)
    if g is None:
        return f'Try: {why}.'
    console = tcod.console.Console(U.W, U.H, order='F')
    app = U.App(TcodCanvas(console))
    app.start_game(g)
    while app.running:
        app.render()
        ctx.present(console, keep_aspect=True, integer_scaling=True)
        if app.game is None or app.game.dead:
            return 'Try: the hero died. Back in the editor.'
        for ev in tcod.event.wait(app.frame_delay()):
            if isinstance(ev, tcod.event.Quit):
                return 'Back from Try.'
            if isinstance(ev, tcod.event.KeyDown):
                tok, shift = key_token(ev)
                if tok == 'esc' and isinstance(app.top, U.GameScreen):
                    return 'Back from Try.'
                if tok:
                    app.key(tok, shift)
        if app.auto:
            app.tick()
    return 'Back from Try.'
