"""Field of view. Uses libtcod's symmetric shadowcasting when tcod is installed,
with a pure-Python shadowcaster as a fallback (used by the headless tests)."""
from . import data as D

try:
    import numpy as np
    import tcod
    _OPAQUE = np.array([t.opaque for t in D.TILES], dtype=bool)
    _ALGO = getattr(tcod, 'FOV_SYMMETRIC_SHADOWCAST', None)
    if _ALGO is None:
        _ALGO = tcod.constants.FOV_SYMMETRIC_SHADOWCAST
    HAVE_TCOD = True
except Exception:  # pragma: no cover - depends on the environment
    HAVE_TCOD = False


def compute(m, px, py, radius):
    """Return a bytearray (index y*w+x) of visible cells and mark them as seen."""
    if HAVE_TCOD:
        tiles = np.asarray(m.t, dtype=np.int16).reshape(m.h, m.w)
        transparency = ~_OPAQUE[tiles]
        vis = tcod.map.compute_fov(transparency, (py, px), radius=radius, light_walls=True, algorithm=_ALGO)
        flat = vis.ravel()
        out = bytearray(flat.astype(np.uint8).tobytes())
    else:
        out = _shadowcast(m, px, py, radius)
    seen = m.seen
    for i, v in enumerate(out):
        if v:
            seen[i] = 1
    return out


_MULT = [[1, 0, 0, -1, -1, 0, 0, 1], [0, 1, -1, 0, 0, -1, 1, 0], [0, 1, 1, 0, 0, -1, -1, 0], [1, 0, 0, 1, -1, 0, 0, -1]]


def _shadowcast(m, px, py, r):
    w, h = m.w, m.h
    vis = bytearray(w * h)
    tiles = m.t
    opq = [t.opaque for t in D.TILES]

    def opaque(x, y):
        return not (0 <= x < w and 0 <= y < h) or opq[tiles[y * w + x]]

    def light(x, y):
        if 0 <= x < w and 0 <= y < h:
            vis[y * w + x] = 1

    def cast(row, start, end, xx, xy, yx, yy):
        if start < end:
            return
        r2 = r * r + r
        ns = 0.0
        for j in range(row, r + 1):
            dx, dy = -j - 1, -j
            blocked = False
            while dx <= 0:
                dx += 1
                X, Y = px + dx * xx + dy * xy, py + dx * yx + dy * yy
                ls, rs = (dx - .5) / (dy + .5), (dx + .5) / (dy - .5)
                if start < rs:
                    continue
                if end > ls:
                    break
                if dx * dx + dy * dy <= r2:
                    light(X, Y)
                if blocked:
                    if opaque(X, Y):
                        ns = rs
                        continue
                    blocked = False
                    start = ns
                elif opaque(X, Y) and j < r:
                    blocked = True
                    cast(j + 1, start, ls, xx, xy, yx, yy)
                    ns = rs
            if blocked:
                break

    light(px, py)
    for o in range(8):
        cast(1, 1.0, 0.0, _MULT[0][o], _MULT[1][o], _MULT[2][o], _MULT[3][o])
    return vis
