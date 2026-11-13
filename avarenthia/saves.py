"""Saves that last across new builds (round 38, "Playing it" in docs/plan.md).

A save from an older build loads: every field a newer build added to the game, the player, the world, the maps, the
creatures and the items is filled with its default, found by comparing each object with a fresh one of its class;
then the steps in MIGRATIONS run, one per version, for real changes of shape. Only a step marked breaking drops the
save, and the main menu then says so in one line. Things a new build adds to world making show only in a new world.

The rule for later builds (CLAUDE.md): bump SAVE_VERSION when saved data changes shape and add its step here."""
import copy
import inspect
import random

# The first version that lasts: saves of older builds were made before this and cannot be read.
FIRST = 64

# from version n to n+1: (what changed, the function that changes a loaded game or None, breaking?)
def _tally(g):
    """65: the kill count went from the game to the player's tally."""
    n = g.__dict__.pop('kills', 0)
    t = g.player.__dict__.setdefault('tally', {})
    t['kills'] = t.get('kills', 0) + (n or 0)


def _affixes(g):
    """66: the marks of creatures got their new names (Fast is Swift, Extra Strong is Brutal, Fire Enchanted is
    Fire-blooded)."""
    from .affixes import OLD
    for m in list(getattr(g, 'maps', {}).values()):
        for mon in getattr(m, 'mons', ()):
            mods = getattr(mon, 'mods', None)
            if mods:
                new = []
                for a in mods:
                    a = OLD.get(a, a)
                    if a not in new:
                        new.append(a)
                mon.mods = new


def _craftguilds(g):
    """68: the four crafts guilds get their halls in an old world; who already held a crafts guild rank keeps it."""
    w = getattr(g, 'world', None)
    if w is not None and 'hammer' not in getattr(w, 'guild_halls', {}):
        from .craftguilds import setup
        setup(w)
    from . import guilds as GU
    for k, s in getattr(g, 'guilds', {}).items():
        if k in GU.GUILDS and GU.GUILDS[k]['kind'] == 'life' and 'paid' not in s:
            s['paid'] = max(i for i, v in enumerate(GU.RANK_REP) if s.get('rep', 0) >= v)


def _homes(g):
    """76: a roof of your own (round 64): every market gets building stone; the homes start empty."""
    from .economy import stone_stock
    w = getattr(g, 'world', None)
    for s in getattr(w, 'settlements', ()):
        if 'stone' not in s.market:
            t = stone_stock(s)
            s.market['stone'] = [t, t, t]


def _story_land(g):
    """Round 58c: the story's places in a world made before them (with dice of their own)."""
    from . import storyland as SL
    SL.info(g)


def _counted_sky(g):
    """70: The Counted Sky (round 58): a Varnish book of this world that grew a page has the new page at a library."""
    from .varnish import fix_pages
    if getattr(g, 'world', None) is not None:
        fix_pages(g.world)


def _seven_keys(g):
    """Round 57b: the bar has seven places; an epic on old key 6 moves to key 7 and starts full, as it was."""
    from . import epics as EP
    p = g.player
    while len(p.bar) < 7:
        p.bar.append(None)
    if p.bar[5] in EP.EPICS:
        p.bar[6], p.bar[5] = p.bar[5], None
    s = EP.st(g)
    spent = s.pop('spent', False)
    s.setdefault('charge', 0.0 if spent else EP.CHARGE_FULL)


MIGRATIONS = {
    64: ('the kill count moved to the tally', _tally, False),
    65: ('the marks of creatures renamed', _affixes, False),
    66: ('folk in need: their needs on the world, who you helped on the player', None, False),
    67: ('folk in need: twists, seeds, follow-ups and graves', None, False),
    68: ('the crafts guilds: four new guilds, their halls, ranks raised by the master', _craftguilds, False),
    69: ('more makers: places with their own plans, their states and break-ins (new worlds)', None, False),
    70: ('The Counted Sky: books that grew a page wait at a library', _counted_sky, False),
    71: ('The story on the land (round 58c)', _story_land, False),
    72: ('The bar of seven keys: an epic on key 7, filled by fighting', _seven_keys, False),
    73: ('Games at the inn: a gaming table by the innkeeper, your games on the player', None, False),
    74: ('A first sight of a town: the settlements you saw, on the player', None, False),
    75: ('A roof of your own: homes on the player, building stone in every market', _homes, False),
    76: ('Camps on the road: camps of the world, what each camp makes of you on the player', None, False),
}

NOTE = []          # the one line the main menu shows when a save could not be kept (set by load)


def note():
    return NOTE[-1] if NOTE else None


def say(text):
    NOTE[:] = [text]


# ------------------------------------------------------------------ fresh objects of each class
_FRESH = {}
SKIP = {'Game'}          # the game itself: its fields come from Game.fields(), not from a whole new world


def fresh(cls, like):
    """The __dict__ of a fresh object of cls, made with the loaded object's own values for its arguments (or None
    when it cannot be made)."""
    if cls in _FRESH:
        return _FRESH[cls]
    out = None
    if cls.__name__ == 'Game' and hasattr(cls, 'fields'):
        obj = cls.__new__(cls)
        obj.fields()
        out = dict(obj.__dict__)
    elif cls.__name__ not in SKIP:
        try:
            sig = inspect.signature(cls.__init__)
            args = []
            for name, prm in list(sig.parameters.items())[1:]:
                if prm.kind in (prm.VAR_POSITIONAL, prm.VAR_KEYWORD):
                    continue
                if prm.default is not prm.empty:
                    break
                args.append(getattr(like, name, 0))
            state = random.getstate()
            try:
                obj = cls(*args)
            finally:
                random.setstate(state)
            out = dict(obj.__dict__)
        except Exception:
            out = None
    _FRESH[cls] = out
    return out


def fill(root):
    """Walk everything a save holds and give each object of the game's own classes the fields it lacks."""
    seen = set()
    stack = [root]
    filled = 0
    while stack:
        o = stack.pop()
        if id(o) in seen:
            continue
        seen.add(id(o))
        if isinstance(o, dict):
            stack.extend(v for v in o.values() if not isinstance(v, (int, float, str, bytes, bytearray, bool)))
            stack.extend(k for k in o.keys() if isinstance(k, tuple))
            continue
        if isinstance(o, (list, tuple, set, frozenset)):
            stack.extend(v for v in o if not isinstance(v, (int, float, str, bytes, bytearray, bool)))
            continue
        cls = type(o)
        if not cls.__module__.startswith('avarenthia') or not hasattr(o, '__dict__'):
            continue
        tpl = fresh(cls, o)
        if tpl:
            for k, v in tpl.items():
                if k not in o.__dict__:
                    o.__dict__[k] = copy.deepcopy(v)
                    filled += 1
        stack.extend(v for v in o.__dict__.values() if not isinstance(v, (int, float, str, bytes, bytearray, bool)))
    return filled


# ------------------------------------------------------------------ loading
def upgrade(g, version_now):
    """Bring a loaded game up to this build: fill new fields, run the steps. Returns the game, or None when it
    cannot be kept (then note() says why)."""
    v = getattr(g, 'version', 0)
    if v > version_now:
        say('Your save is from a newer build than this one; play it with that build.')
        return None
    if v < FIRST:
        say('Your save is from a build before saves lasted; it cannot be read. Start a new game.')
        return None
    _FRESH.clear()
    fill(g)
    for n in range(v, version_now):
        step = MIGRATIONS.get(n)
        if step is None or step[2]:
            say(f'Your save is from an older build that this one cannot read ({step[0] if step else "version " + str(n)}). '
                'Start a new game.')
            return None
        if step[1]:
            step[1](g)
    g.version = version_now
    return g
