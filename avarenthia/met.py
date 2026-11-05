"""What you met (round 41, "Playing it" in docs/plan.md): the first time the player meets each system or kind of
place, with the day. Nothing is shown in the game; the test build lists met and never met in F12 [M], and the note
for Claude carries the list, so the never-met rows show what may be hidden too well.

State on the player (`p.met`: key -> day). Keys: 'place: <kind>', 'job: <kind>', 'tip: <key>', 'chapter: <name>' and
the systems in SYSTEMS."""

SYSTEMS = {
    'ship': 'A voyage by ship',
    'ferry': 'A ferry crossing',
    'guild': 'A guild joined',
    'trade': 'A good sold on a market',
    'epic': "An epic's rumour heard",
    'raising': 'A raising at the temple',
}


def state(game):
    return game.player.__dict__.setdefault('met', {})


def saw(game, key):
    """Note the first meeting; True when it was new."""
    if getattr(game, 'player', None) is None or not hasattr(game, 'turn'):
        return False                            # the world is still being made
    m = state(game)
    if key in m:
        return False
    m[key] = game.day
    return True


def site_kind(world, s):
    from . import places as PL
    if PL.is_place(s):
        return f"{'abbey' if s.kind == 'monastery' else s.kind} ({PL.people_of(s)})"
    return s.kind


def visit(game, kind, ref):
    """From Game.mark_visit: the kind of the place you stand at."""
    w = game.world
    try:
        if kind == 's':
            k = w.settlements[ref].kind
        elif kind == 'd':
            d = w.dungeons[ref]
            if getattr(d, 'site', None) is not None:
                return
            k = f'dungeon ({d.style})'
        elif kind == 'site':
            k = site_kind(w, w.sites[ref])
        else:
            return
    except (IndexError, KeyError, AttributeError):
        return
    saw(game, 'place: ' + k)


def everything(game):
    """Every key this world could show: (key, label)."""
    from . import guide as GDE
    from . import chronicle as CH
    from . import jobs as JB
    w = game.world
    out = {}
    for s in w.settlements:
        out['place: ' + s.kind] = f'Settlement: {s.kind}'
    for d in w.dungeons.values():
        if getattr(d, 'site', None) is None:
            out[f'place: dungeon ({d.style})'] = f'Dungeon: {d.style}'
    for s in w.sites:
        k = site_kind(w, s)
        out['place: ' + k] = f'Place: {k}'
    for h in w.holds:
        out['place: ' + h.kind] = f'Hold: {h.kind}'
    for k in getattr(JB, 'KINDS', {}):
        out['job: ' + k] = f'Job: {k}'
    for k in GDE.TIPS:
        out['tip: ' + k] = f'Tip: {k}'
    for c in CH.CHAPTERS:
        out['chapter: ' + c] = f'Chronicle: {c}'
    for k, v in SYSTEMS.items():
        out[k] = v
    for k in state(game):
        out.setdefault(k, k)
    return sorted(out.items(), key=lambda kv: kv[1])


def rows(game):
    """(met?, day or None, label), met first by day, then the never met."""
    m = state(game)
    allk = everything(game)
    met = sorted(((True, m[k], lab) for k, lab in allk if k in m), key=lambda r: (r[1], r[2]))
    never = [(False, None, lab) for k, lab in allk if k not in m]
    return met + never


def text(game):
    r = rows(game)
    n = sum(1 for x in r if x[0])
    lines = [f'What you met: {n} of {len(r)}', '']
    lines += [f'day {d:>4}  {lab}' for ok, d, lab in r if ok]
    lines += ['', 'Never met:'] + [f'          {lab}' for ok, _d, lab in r if not ok]
    return '\n'.join(lines) + '\n'
