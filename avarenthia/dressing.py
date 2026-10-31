"""Dressing a room (approved 31 October 2026, the editor's Ctrl+D): the background things of a room laid at random
from one or more sets, by plain rules: shelves and racks against the wall, barrels in the corners, tables in
pairs, furs round the fire, rubbish anywhere. A dressed room never cuts the way: every free floor cell stays
reachable from the way in, and nothing is laid on or beside a cell that must stay free (the way in, stairs, telling
things, creatures).

The editor uses it to dress a room "now" (what it lays is drawn into the piece) and the game uses it for a piece with
a DRESS line, dressed anew in every world. Both give the room as plain sets of cells and get back
[((x, y), tile name)]; each turns the names into its own signs or tiles."""
from collections import deque

from . import data as D

# a set: [(tile name, rule, weight)]. Rules: 'wall' (beside a wall), 'corner' (two walls), 'middle' (no wall near),
# 'scatter' (anywhere), 'pairs' (two side by side, away from the wall), 'by:<tile name>' (beside one already laid),
# 'once' after the rule: at most one in the room.
SETS = {
    'war camp': [('fire pit', 'middle once', 3), ('bed of furs', 'by:fire pit', 4), ('midden', 'scatter', 3),
                 ('drying rack', 'wall', 2), ('barrel', 'corner', 2), ('totem', 'wall once', 1)],
    'hall': [('table', 'pairs', 5), ('barrel', 'corner', 3), ('hearth', 'wall once', 2), ('high seat', 'wall once', 1),
             ('pew', 'wall', 1)],
    'ruin': [('rubble', 'scatter', 5), ('heap of bones', 'corner', 2), ('web', 'corner', 3), ('old column', 'middle', 2),
             ('remains of a camp', 'scatter once', 1)],
    'library': [('shelves of books', 'wall', 8), ('table', 'middle', 2), ('workbench', 'wall once', 1)],
    'crypt': [('gravestone', 'scatter', 4), ('bier', 'middle once', 1), ('heap of bones', 'corner', 2),
              ('web', 'corner', 2), ('statue', 'wall', 1)],
    'cave': [('mushrooms', 'scatter', 4), ('rubble', 'scatter', 3), ('web', 'corner', 2), ('heap of bones', 'wall', 1)],
    'storeroom': [('barrel', 'corner', 4), ('barrel', 'wall', 4), ('workbench', 'wall', 1), ('cart', 'wall once', 1)],
    'forge': [('hearth', 'wall once', 3), ('anvil', 'by:hearth', 3), ('heap of slag', 'corner', 2),
              ('workbench', 'wall', 2), ('barrel', 'corner', 1)],
    'temple': [('pew', 'pairs', 5), ('fire bowl', 'wall', 2), ('statue', 'wall', 2), ('altar', 'wall once', 1)],
    'barracks': [('bed', 'wall', 5), ('table', 'middle', 2), ('barrel', 'corner', 2), ('straw dummy', 'middle once', 1)],
    'den': [('heap of bones', 'scatter', 4), ('midden', 'scatter', 3), ('bed of furs', 'corner', 2), ('web', 'corner', 1)],
}
# how much of the free floor a fullness of 1-5 lays things on
FULL = {1: .03, 2: .06, 3: .10, 4: .14, 5: .18}
ORTH = ((1, 0), (-1, 0), (0, 1), (0, -1))
AROUND = ORTH + ((1, 1), (1, -1), (-1, 1), (-1, -1))


def tile(name):
    """The game's tile of a set's thing (by its name in data.TILES)."""
    return next(i for i, t in enumerate(D.TILES) if t.name == name)


def walks(name):
    return D.TILES[tile(name)].walk


def check_sets():
    """Every thing of every set is a tile of the game (the tests call it)."""
    for opts in SETS.values():
        for name, _rule, _w in opts:
            tile(name)


def dress(free, walk, wall, start, sets, rng, keep=()):
    """Lay the sets' things on the room. free: the floor cells that may be dressed; walk: every cell one can walk on
    (free included); wall: cells that count as wall for the rules; start: the cell inside the way in; sets: [(name,
    fullness 1-5)]; keep: cells that must stay free with a free cell beside them. Returns [((x, y), tile name)]."""
    walk, free = set(walk), set(free)
    keep = set(keep) | {start}
    near_keep = {(x + dx, y + dy) for x, y in keep for dx, dy in ORTH}
    free -= keep | near_keep
    out, laid = [], {}

    def walls(c):
        return [d for d in ORTH if (c[0] + d[0], c[1] + d[1]) in wall]

    def fits(c, rule):
        if c not in free:
            return False
        w = walls(c)
        if rule == 'wall':
            return len(w) >= 1
        if rule == 'corner':
            return len(w) >= 2 and any(a[0] != b[0] for a in w for b in w)
        if rule == 'middle':
            return not any((c[0] + dx, c[1] + dy) in wall for dx, dy in AROUND)
        if rule == 'pairs':
            return not w
        if rule.startswith('by:'):
            return any(laid.get((c[0] + dx, c[1] + dy)) == rule[3:] for dx, dy in AROUND)
        return True

    def still_open(cells):
        """Every walkable cell still reached from the way in once these cells are taken."""
        gone = set(cells)
        left = walk - gone
        if start not in left:
            return False
        seen, todo = {start}, deque([start])
        while todo:
            x, y = todo.popleft()
            for dx, dy in ORTH:
                n = (x + dx, y + dy)
                if n in left and n not in seen:
                    seen.add(n)
                    todo.append(n)
        return len(seen) == len(left)

    def lay(cells, name):
        if not walks(name):
            if not still_open(cells):
                return False
            walk.difference_update(cells)
        for c in cells:
            free.discard(c)
            laid[c] = name
            out.append((c, name))
        return True

    for set_name, full in sets:
        opts = SETS.get(set_name)
        if not opts:
            continue
        aim = max(1, round(len(free) * FULL.get(max(1, min(5, full)), .10)))
        done, used, tries = 0, set(), 0
        while done < aim and tries < aim * 12:
            tries += 1
            name, rule, _w = _pick(rng, opts)
            once = rule.endswith(' once')
            rule = rule.replace(' once', '')
            if once and name in used:
                continue
            spots = sorted(c for c in free if fits(c, rule))
            if not spots:
                continue
            c = rng.choice(spots)
            cells = [c]
            if rule == 'pairs':
                nxt = [(c[0] + dx, c[1]) for dx in (1, -1) if fits((c[0] + dx, c[1]), 'pairs')]
                if nxt:
                    cells.append(rng.choice(nxt))
            if lay(cells, name):
                used.add(name)
                done += len(cells)
    return out


def _pick(rng, opts):
    total = sum(w for _n, _r, w in opts)
    k = rng.random() * total
    for o in opts:
        k -= o[2]
        if k < 0:
            return o
    return opts[-1]
