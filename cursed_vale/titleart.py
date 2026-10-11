"""The title picture, as ANSI art: a lone wanderer with a sword on a cliff, looking out over a wide valley at dawn.
A river winds to the sea, mountains catch the first light, a ruined tower stands in the mist.

The picture is painted on a pixel grid two pixels per cell high (half blocks: ▀ with the top pixel as the
foreground colour and the bottom one as the background), then dithered with ░▒▓ where colours blend,
the way ANSI art did it."""
import math

from .look import _h

# a dawn sky, from night at the top to a warm glow at the horizon
SKY = [(0, (6, 8, 26)), (.28, (18, 22, 58)), (.5, (54, 40, 90)), (.68, (140, 72, 96)), (.82, (222, 128, 88)),
       (.93, (250, 186, 112)), (1.0, (255, 222, 150))]
DITHER = ' ░▒▓'

# the wanderer: hood, a cloak blowing to the left, a sword held low on the right ('#' body, 'r' rim light, 's' blade)
WANDERER = [
    '....##....',
    '...####...',
    '...####...',
    '...###r...',
    '...###r...',
    '....##....',
    '...####...',
    '..#####r..',
    '.######r..',
    '.######r..',
    '#######r..',
    '##.####r..',
    '#..####s..',
    '#..####s..',
    '...####.s.',
    '...####.s.',
    '...####..s',
    '...####..s',
    '...####...',
    '...####...',
    '...#.##...',
    '...#.##...',
    '...#..#...',
    '...#..#...',
    '...#..#...',
    '...#..#...',
    '..##..##..',
]


def _lerp(a, b, t):
    return (round(a[0] + (b[0] - a[0]) * t), round(a[1] + (b[1] - a[1]) * t), round(a[2] + (b[2] - a[2]) * t))


def _grad(stops, t):
    t = max(0.0, min(1.0, t))
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        if t <= t1:
            return _lerp(c0, c1, (t - t0) / max(1e-6, t1 - t0))
    return stops[-1][1]


def _noise(x, s=0):
    """Smooth 1-d noise in -1..1."""
    i = math.floor(x)
    f = x - i
    a = (_h(i, 0, s) / 65535) * 2 - 1
    b = (_h(i + 1, 0, s) / 65535) * 2 - 1
    f = f * f * (3 - 2 * f)
    return a + (b - a) * f


def paint(w, h):
    """Return a list of (ch, fg, bg) for a w x h cell screen."""
    ph = h * 2                                # pixel rows
    hz = round(ph * .62)                      # the horizon
    sunx, suny = w * .66, hz - 1
    px = [[(0, 0, 0)] * w for _ in range(ph)]
    kind = [[''] * w for _ in range(ph)]

    def sky_t(y):
        return y / hz

    # -- sky, sun, rays and clouds
    for y in range(min(hz + 2, ph)):
        for x in range(w):
            c = _grad(SKY, sky_t(y))
            dx, dy = (x - sunx) * 2, (y - suny)
            d = math.hypot(dx, dy)
            ang = math.atan2(dy, dx)
            if y < hz and d > 9:                     # rays of light fanning up from the sun
                band = math.sin(ang * 11 + 1.3)
                if band > .55:
                    c = _lerp(c, (255, 214, 150), .16 * (1 - min(1, d / (ph * .9))))
            glow = max(0.0, 1 - d / 46)
            c = _lerp(c, (255, 226, 160), glow ** 2 * .75)
            if d < 7:
                c = (255, 244, 200)
            px[y][x] = c
            kind[y][x] = 'sky'
    # long, thin clouds lit from below
    for cy, cx, cw, s in ((hz * .40, w * .18, 26, 1), (hz * .52, w * .52, 34, 2), (hz * .30, w * .78, 22, 3),
                          (hz * .66, w * .30, 30, 4), (hz * .72, w * .86, 18, 5), (hz * .20, w * .40, 16, 6)):
        for y in range(int(cy - 3), int(cy + 3)):
            for x in range(int(cx - cw), int(cx + cw)):
                if not (0 <= x < w and 0 <= y < hz):
                    continue
                dy = (y - cy) / 3.2
                span = cw * max(.05, 1 - dy * dy) * (1 + .3 * _noise(y * 1.7 + x * .02, s + 40))
                edge = abs(x - cx - dy * 6) / span + _noise(x * .3 + y * 5, s) * .15
                if edge < 1:
                    under = y > cy
                    base = _grad(SKY, sky_t(y) + .12)
                    lit = _lerp(base, (255, 200, 150), .5 if under else .2)
                    px[y][x] = _lerp(px[y][x], lit, .85 - edge * .4)
                    kind[y][x] = 'cloud'
    # birds
    for bx, by in ((w * .44, hz * .34), (w * .47, hz * .30), (w * .50, hz * .36), (w * .41, hz * .39)):
        x, y = int(bx), int(by)
        if 0 <= x < w and 0 <= y < ph:
            kind[y][x] = 'bird'

    # -- far mountains, backlit, snow on the high peaks (a ridged noise gives sharp peaks)
    def ridge(x):
        v = 0.0
        for f, amp, sd in ((.045, 1.0, 11), (.11, .5, 12), (.27, .22, 13)):
            n = 1 - abs(_noise(x * f, sd))
            v += n * n * amp
        return v / 1.72
    far = [hz - 6 - 30 * ridge(x) for x in range(w)]
    snowline = hz - 24
    for x in range(w):
        top = int(far[x])
        slope = far[min(w - 1, x + 1)] - far[max(0, x - 1)]
        for y in range(max(0, top), hz + 1):
            lit = slope > 0                          # faces turned towards the sun
            col = _lerp((96, 82, 138) if lit else (66, 56, 104), (52, 46, 86), min(1, (y - top) / 14))
            if y < snowline + 2 * _noise(x * .4, 14) and y - top < 6:
                col = (226, 214, 234) if lit else (168, 160, 200)
            if y - top < 1:
                col = _lerp(col, (255, 190, 150), .5)   # rim light on the ridge
            haze = max(0, (y - (hz - 8)) / 8)
            px[y][x] = _lerp(col, (236, 170, 130), haze * .75)
            kind[y][x] = 'mount'

    # -- the sea on the right, the valley on the left, and a river between
    for y in range(hz, ph):
        for x in range(w):
            depth = (y - hz) / (ph - hz)
            px[y][x] = _lerp((70, 104, 60), (24, 46, 32), depth)
            kind[y][x] = 'land'
    sea_left = [w * .50 + 6 * _noise(y * .3, 21) + (y - hz) * 1.8 for y in range(ph)]
    for y in range(hz, min(ph, hz + 14)):
        for x in range(int(sea_left[y]), w):
            t = (y - hz) / 14
            c = _lerp((250, 196, 130), (60, 90, 140), t ** .6)
            if abs(x - sunx) < 3 + (y - hz) * .5 and (_h(x, y, 7) % 3):
                c = _lerp(c, (255, 236, 180), .7)    # the sun on the water
            px[y][x] = c
            kind[y][x] = 'water'
    # the river: from the sea it winds down and to the left, widening towards us
    for y in range(hz + 2, ph):
        t = (y - hz) / (ph - hz)
        cx = w * .52 - t * w * .22 + 7 * math.sin(t * 7.5)
        half = .8 + t * 4.5
        for x in range(int(cx - half), int(cx + half) + 1):
            if 0 <= x < w and kind[y][x] == 'land':
                px[y][x] = _lerp((246, 196, 140), (70, 110, 150), t ** .7)
                kind[y][x] = 'river'
    # forests on the valley floor
    for y in range(hz + 3, ph):
        for x in range(w):
            if kind[y][x] != 'land':
                continue
            n = _noise(x * .12, 31) + _noise(y * .25, 32) * .7 + _noise((x + y) * .07, 33) * .5
            if n > .35:
                d = (y - hz) / (ph - hz)
                px[y][x] = _lerp((40, 76, 46), (14, 32, 22), d)
                kind[y][x] = 'forest'
    # rolling hills: lighter crests catching the sun
    for x in range(w):
        crest = hz + 9 + 5 * _noise(x * .07, 41)
        for y in range(int(crest), int(crest) + 2):
            if 0 <= y < ph and kind[y][x] in ('land', 'forest'):
                px[y][x] = _lerp(px[y][x], (190, 170, 90), .35)

    # -- a ruined tower on a knoll, in the mist
    tx, ty = int(w * .74), hz + 1
    for y in range(ty - 4, ty + 2):                 # the knoll
        for x in range(tx - 9, tx + 10):
            if abs(x - tx) < 9 - (ty + 2 - y) * 1.6 and 0 <= y < ph:
                px[y][x] = _lerp((60, 70, 60), (236, 170, 130), .2)
                kind[y][x] = 'land'
    height = 22
    for k in range(height):
        y = ty - 4 - k
        half = 2 if k < 14 else 1
        for x in range(tx - half, tx + half + 1):
            gone = (k > 17 and x == tx + 1) or (k > 19 and x == tx) or (k == 21 and x == tx - 1 and _h(x, y, 5) % 2)
            if 0 <= y < ph and not gone:
                lit = x > tx
                px[y][x] = _lerp((96, 80, 100) if lit else (64, 54, 76), (236, 170, 130), .2)
                kind[y][x] = 'tower'
    for wy in (ty - 12, ty - 18):
        if 0 <= wy < ph:
            px[wy][tx] = (34, 26, 40)

    # mist along the foot of the mountains
    for y in range(hz - 5, hz + 5):
        for x in range(w):
            k = (1 - abs(y - hz) / 5) * (.35 + .25 * _noise(x * .15, 51))
            if k > 0 and 0 <= y < ph:
                px[y][x] = _lerp(px[y][x], (240, 196, 160), k)

    # -- the cliff in front, on the left, and a dark crag framing the right
    cliff = [hz + 14 + 3 * _noise(x * .3, 61) + max(0, (x - w * .34)) * 2.2 for x in range(w)]
    for x in range(w):
        for y in range(max(0, int(cliff[x])), ph):
            dd = y - cliff[x]
            r = _h(x, y, 63)
            col = (58, 54, 64) if r % 5 else (76, 70, 80)
            col = _lerp(col, (30, 28, 36), min(1, dd / 26))
            if dd < 1.5:
                col = _lerp(col, (236, 160, 100), .7)      # dawn light on the rim
            px[y][x] = col
            kind[y][x] = 'rock'
    tree_x = w - 3
    for y in range(ph):                              # the trunk
        wob = 1.5 * _noise(y * .15, 74)
        for x in range(int(tree_x - 3 + wob - (y > ph - 10) * (ph - 10 - y) * -.4), w):
            if 0 <= x < w:
                px[y][x] = (24, 20, 22) if _h(x, y, 75) % 5 else (40, 32, 30)
                kind[y][x] = 'trunk'
    for cx, cy, r in ((w - 4, 6, 16), (w - 16, 2, 11), (w - 2, 26, 12), (w - 26, 0, 8)):
        for y in range(0, min(ph, cy + r + 4)):
            for x in range(max(0, cx - r * 2 - 6), w):
                d = math.hypot((x - cx) * 1.0, (y - cy) * 1.0) / r + _noise(x * .5 + y * .3, 76) * .22
                if d < 1:
                    px[y][x] = (18, 30, 24) if _h(x, y, 77) % 3 else (28, 46, 34)
                    kind[y][x] = 'leaves'
                    if d > .82 and y > cy:
                        px[y][x] = _lerp(px[y][x], (180, 110, 70), .25)   # dawn on the lower leaves

    # -- the wanderer, standing on the rim of the cliff
    fx = int(w * .23)
    base = int(cliff[fx + 6]) + 1
    top = base - len(WANDERER)
    for j, row in enumerate(WANDERER):
        for i, c in enumerate(row):
            x, y = fx + i, top + j
            if c == '.' or not (0 <= x < w and 0 <= y < ph):
                continue
            px[y][x] = {'#': (14, 12, 20), 'r': (178, 104, 70), 's': (220, 214, 200)}[c]
            kind[y][x] = 'hero'

    # -- to cells
    out = []
    for cy in range(h):
        for cx in range(w):
            t, b = px[cy * 2][cx], px[cy * 2 + 1][cx]
            kt, kb = kind[cy * 2][cx], kind[cy * 2 + 1][cx]
            r = _h(cx, cy, 81)
            if kt == kb == 'sky' and not (_h(cx, cy, 82) % 41) and cy * 2 < hz * .45:
                out.append(('·' if r % 3 else '+', _lerp(t, (255, 255, 255), .6), t))     # a few last stars
                continue
            if kt == 'bird' or kb == 'bird':
                out.append(('v', (40, 28, 46), t if kt != 'bird' else b))
                continue
            if t == b:
                if kt == 'rock' and r % 3 == 0:
                    out.append(('░▒'[r % 2], _lerp(t, (110, 104, 116), .5), t))
                elif kt == 'forest' and r % 2:
                    out.append(('♠' if r % 5 else '♣', _lerp(t, (60, 100, 60), .5), t))
                elif kt in ('water', 'river') and r % 4 == 0:
                    out.append(('≈' if r % 3 else '~', _lerp(t, (255, 236, 190), .45), t))
                elif kt == 'leaves' and r % 3 == 0:
                    out.append(('♣' if r % 2 else '♠', (44, 64, 48), t))
                elif kt == 'trunk' and r % 4 == 0:
                    out.append(('│', (52, 42, 38), t))
                else:
                    out.append((' ', t, t))
                continue
            if kt == kb and kt in ('sky', 'mount', 'cloud'):
                # blend two shades with a dither, the ANSI way
                lt = sum(t) > sum(b)
                hi, lo = (t, b) if lt else (b, t)
                diff = abs(sum(t) - sum(b))
                ch = DITHER[min(3, 1 + diff // 40)]
                out.append((ch, hi, lo))
                continue
            out.append(('▀', t, b))
    return out
