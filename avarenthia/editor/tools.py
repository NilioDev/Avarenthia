"""The drawing tools on a Room's grid: a cell, a line, a rectangle, a fill, and a selection to copy and paste.
Pure functions over the grid; the screen calls Room.change() before each stroke so one stroke is one undo."""


def line_cells(a, b):
    """The cells of a straight line from a to b (Bresenham), both ends included."""
    (x0, y0), (x1, y1) = a, b
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err, out = dx + dy, []
    while True:
        out.append((x0, y0))
        if (x0, y0) == (x1, y1):
            return out
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def rect_cells(a, b, filled=False):
    x0, x1 = sorted((a[0], b[0]))
    y0, y1 = sorted((a[1], b[1]))
    return [(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)
            if filled or x in (x0, x1) or y in (y0, y1)]


def fill_cells(room, start):
    """The cells joined to start (four ways) that have the same sign, inside the drawing."""
    if not room.inb(*start):
        return []
    want = room.get(*start)
    seen, todo = {start}, [start]
    while todo:
        x, y = todo.pop()
        for c in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if c not in seen and room.inb(*c) and room.get(*c) == want:
                seen.add(c)
                todo.append(c)
    return sorted(seen)


def paint(room, cells, ch):
    n = 0
    for x, y in cells:
        if room.inb(x, y) and room.get(x, y) != ch:
            room.set(x, y, ch)
            n += 1
    return n


def copy_cells(room, a, b):
    """What lies in the rectangle a-b: {(dx, dy): sign} from its top left."""
    x0, x1 = sorted((a[0], b[0]))
    y0, y1 = sorted((a[1], b[1]))
    return {(x - x0, y - y0): room.get(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)}


def paste_cells(room, clip, at):
    for (dx, dy), ch in clip.items():
        room.set(at[0] + dx, at[1] + dy, ch)
