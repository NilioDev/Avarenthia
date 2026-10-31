"""Reading and writing .des files for the editor. Saving changes only the block of the piece you edit (from its
NAME line to its ENDMAP); notes and the other pieces in the file stay as they are."""
import os
import sys

from .. import pieces as P
from .model import Room

MINE = 'My pieces.des'


def home():
    """Where your own files go: beside the editor when it is a built program, else the repo's folder 'my pieces'
    (not in git)."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(root, 'my pieces')


def source_dir():
    """The game's own pieces when run from the source (None in a built program: there they are packed)."""
    return P.SOURCE if os.path.isdir(P.SOURCE) and not getattr(sys, 'frozen', False) else None


def files():
    """Every .des file the editor can open: (label, path)."""
    out = []
    src = source_dir()
    if src:
        out += [(f, os.path.join(src, f)) for f in sorted(os.listdir(src)) if f.endswith('.des')]
    h = home()
    if os.path.isdir(h):
        out += [(f, os.path.join(h, f)) for f in sorted(os.listdir(h)) if f.endswith('.des')]
    return out


def read(path):
    """The rooms in one file (unchecked: a room still being drawn opens too)."""
    with open(path, encoding='utf-8') as f:
        text = f.read()
    rooms = []
    for p in P.parse(text, os.path.basename(path), checked=False):
        r = Room.from_piece(p)
        r.file = path
        rooms.append(r)
    return rooms


def game_pieces():
    """The game's own pieces as rooms, from the pack in a built program (saved to My pieces, never back)."""
    out = []
    for p in P.load():
        r = Room.from_piece(p)
        r.file = os.path.join(source_dir(), p.file) if source_dir() and p.file else ''
        out.append(r)
    return out


def blocks(text):
    """[(name, start line, end line)] of every piece in a file's text (end is the ENDMAP line)."""
    out, cur, start = [], None, 0
    lines = text.split('\n')
    for i, line in enumerate(lines):
        st = line.strip()
        if st.upper().startswith('NAME:'):
            cur, start = st.split(':', 1)[1].strip(), i
        elif st == 'ENDMAP' and cur is not None:
            out.append((cur, start, i))
            cur = None
    return out


def replace(text, old_name, block):
    """The file's text with the piece old_name's block replaced by block (or block added at the end)."""
    lines = text.split('\n')
    for name, a, b in blocks(text):
        if name == old_name:
            return '\n'.join(lines[:a] + block.rstrip('\n').split('\n') + lines[b + 1:])
    sep = '' if not text.strip() else ('\n' if text.endswith('\n') else '\n\n')
    return text + sep + ('\n' if text.strip() else '') + block


def save(room, path=None, old_name=None):
    """Write the room into its file (or path). Returns the path."""
    path = path or room.file or os.path.join(home(), MINE)
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    text = ''
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            text = f.read()
    text = replace(text, old_name or room.name, room.text())
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    room.file, room.dirty = path, False
    return path


_CACHE = None


def game_pieces_cached():
    """The game's pieces, read once (for the check that a name is used only once)."""
    global _CACHE
    if _CACHE is None:
        try:
            _CACHE = game_pieces()
        except (P.Bad, OSError, ValueError):
            _CACHE = []
    return _CACHE


def forget_cache():
    global _CACHE
    _CACHE = None
    P.load(force=True)


# ------------------------------------------------------------------ own tiles and things (Ctrl+T)
MY_TILES = 'my tiles.des'


def own_spans(text):
    """[(name, start line, end line)] of every TILE / OBJECT block in a file's text (end is the END line)."""
    out, cur, start = [], None, 0
    for i, line in enumerate(text.split('\n')):
        st = line.strip()
        head = st.split(':', 1)[0].strip().upper() if ':' in st else ''
        if head in ('TILE', 'OBJECT') and cur is None:
            cur, start = st.split(':', 1)[1].strip(), i
        elif st == 'END' and cur is not None:
            out.append((cur, start, i))
            cur = None
    return out


def save_own(o, old_name=None, path=None):
    """Write an own tile or thing into my tiles.des (its block replaced, or added) and make it in the game's list."""
    from .. import owntiles as OT
    path = path or os.path.join(home(), MY_TILES)
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    text = ''
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            text = f.read()
    lines = text.split('\n')
    for name, a, b in own_spans(text):
        if name == (old_name or o.name):
            text = '\n'.join(lines[:a] + o.text().rstrip('\n').split('\n') + lines[b + 1:])
            break
    else:
        text = text + ('\n' if text.strip() and not text.endswith('\n\n') else '') + o.text()
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    o.file = path
    OT.register(o)
    return path


def own_things():
    """Every own tile and thing the editor knows: the game's and those in your folder, made in the game's list."""
    from .. import owntiles as OT
    P.load()
    h = home()
    if os.path.isdir(h):
        for f in sorted(os.listdir(h)):
            if f.endswith('.des'):
                try:
                    with open(os.path.join(h, f), encoding='utf-8') as fh:
                        for o in P.own_blocks(fh.read(), f):
                            o.file = os.path.join(h, f)
                            OT.register(o)
                except (OSError, ValueError):
                    pass
    return list(OT.OWN.values())
