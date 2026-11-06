"""The margin: what fills a window wider (or taller) than the game at its largest 16:9 size.

A faint sepia old map: patches of water, hills, woods and fields in scattered signs, laid out anew from a seed when
you enter a zone or a new day starts, so nothing stands still long enough to burn into a screen. It does not move in
between (Nilio, 6 November 2026: the drift was restless to watch). Never brighter than a quarter; no text or signs to
read in it. A clear double line marks where the game's screen ends.
"""
import random
import zlib

INK = (58, 46, 34)            # the signs: under a quarter of full light
PAPER = (16, 13, 11)          # the ground
FRAME = (150, 118, 64)        # the clear edge where the game's screen ends (Nilio, 6 November 2026)
PATCHES = ('≈~', '^∩', '♣♠', '.,"', '·.')     # water, hills, woods, fields, open land
PATCH_W, PATCH_H = 6, 4

_cache = {}
EXTRA = 0                     # the debug menu's "new stretch now"


def seed_for(game):
    """A new layout for each zone and each day; the title screen keeps one per run of the game."""
    if not game:
        return 1 + EXTRA
    return zlib.crc32(f'{getattr(game, "cur", "")}|{int(getattr(game, "day", 0))}|{EXTRA}'.encode())


def art(cols, rows, seed):
    """cols x rows cells of the old map as a list of signs, row by row (one colour: INK on PAPER)."""
    key = (cols, rows, seed)
    if key in _cache:
        return _cache[key]
    rnd = random.Random(seed)
    gw, gh = cols // PATCH_W + 2, rows // PATCH_H + 2
    kinds = [PATCHES[rnd.randrange(len(PATCHES))] for _ in range(gw * gh)]
    out = []
    for y in range(rows):
        for x in range(cols):
            jx, jy = x + rnd.randint(-2, 2), y + rnd.randint(-1, 1)          # ragged edges between patches
            kind = kinds[max(0, min(gh - 1, jy // PATCH_H)) * gw + max(0, min(gw - 1, jx // PATCH_W))]
            out.append(rnd.choice(kind) if rnd.random() < .55 else ' ')
    if len(_cache) > 8:
        _cache.clear()
    _cache[key] = out
    return out


def draw(cv, rect, seed, shift=0):
    """Fill every cell of cv outside rect (x, y, w, h) with the old map, moved `shift` cells to the left."""
    rx, ry, rw, rh = rect
    if rx <= 0 and ry <= 0 and rw >= cv.w and rh >= cv.h:
        return
    cols, rows = cv.w, cv.h
    signs = art(cols, rows, seed)
    con = getattr(cv, 'con', None)
    if con is not None:                   # the real console: all at once (a few thousand cells every frame)
        import numpy as np
        codes = np.roll(np.array([ord(c) for c in signs]).reshape(rows, cols), -shift, axis=1).T
        out = np.ones((cols, rows), bool)
        out[max(0, rx):rx + rw, max(0, ry):ry + rh] = False
        con.ch[out] = codes[out]
        con.fg[out] = INK
        con.bg[out] = PAPER
    else:
        for y in range(rows):
            inside = ry <= y < ry + rh
            for x in range(cols):
                if inside and rx <= x < rx + rw:
                    continue
                cv.put(x, y, signs[y * cols + (x + shift) % cols], INK, PAPER)
    frame(cv, rect)


def frame(cv, rect):
    """A double line in the margin's first cells round the game, so it is clear where the game's screen ends."""
    rx, ry, rw, rh = rect
    left, right, top, bottom = rx - 1, rx + rw, ry - 1, ry + rh
    has_l, has_r, has_t, has_b = left >= 0, right < cv.w, top >= 0, bottom < cv.h
    for y in range(max(0, top), min(cv.h, bottom + 1)):
        if has_l:
            cv.put(left, y, '║', FRAME, PAPER)
        if has_r:
            cv.put(right, y, '║', FRAME, PAPER)
    for x in range(max(0, left), min(cv.w, right + 1)):
        if has_t:
            cv.put(x, top, '═', FRAME, PAPER)
        if has_b:
            cv.put(x, bottom, '═', FRAME, PAPER)
    for ok, x, y, ch in ((has_l and has_t, left, top, '╔'), (has_r and has_t, right, top, '╗'),
                         (has_l and has_b, left, bottom, '╚'), (has_r and has_b, right, bottom, '╝')):
        if ok:
            cv.put(x, y, ch, FRAME, PAPER)
