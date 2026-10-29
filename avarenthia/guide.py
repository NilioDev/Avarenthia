"""Keeping the game readable: what each sign means, and a tip the first time something new turns up.

Signs are never written by hand: they come from what you have seen, so the list is always right. The look mode (o)
shows the signs in view; the journal (Lore) shows every sign you have seen on the world map and the map you are on.
A tip is one line in the log, once per hero, the first time it is useful; it names the key, so the keys are learnt
by playing."""
from . import data as D
from . import look as LOOK
from . import missions as MS


def cell_name(m, i):
    """What a cell is called: the land's own name on the world map, the tile's name elsewhere."""
    t = m.t[i]
    bio = getattr(m, 'biome', None)
    if m.kind == 'over' and bio is not None and t in LAND:
        from .describe import BIOME_DESC
        b = m.biome_names[bio[i]]
        if b in BIOME_DESC:
            return BIOME_DESC[b][0]
    return D.TILES[t].name.capitalize()


LAND = {D.WATER, D.GRASS, D.FOREST, D.MOUNTAIN, D.SWAMP, D.HILLS, D.SAND, D.TREE, D.SHALLOW}


def legend(m, cells, out=None, most=4):
    """{name: [(glyph, colour)...]} for the cells given, a few glyphs each, in the order first met."""
    out = {} if out is None else out
    for i in cells:
        ch, fg, _bg = LOOK.get(m, i)
        if ch == ' ':
            continue
        row = out.setdefault(cell_name(m, i), [])
        if len(row) < most and all(c != ch for c, _f in row):
            row.append((ch, fg))
    return out


def in_view(g):
    """What you can see right now: (creatures, land, things), each a list of ([(glyph, colour)...], name)."""
    m, p = g.map, g.player
    r = 30
    cells = [y * m.w + x for y in range(max(0, p.y - r), min(m.h, p.y + r + 1))
             for x in range(max(0, p.x - r), min(m.w, p.x + r + 1)) if g.visible(x, y)]
    land = [(v, k) for k, v in legend(m, cells).items()]
    crs = {}
    if m.kind == 'over':
        from . import hunting as HT
        for wd in g.world.wanderers:
            if g.visible(wd.x, wd.y):
                row = crs.setdefault(wd.name, [wd.ch, wd.fg, 0])
                row[2] += 1
        for h in HT.herds(g):
            if HT.seen_herd(g, h):
                ch, fg = HT.look(g, h)
                row = crs.setdefault(HT.herd_name(h), [ch, fg, 0])
                row[2] += 1
    else:
        for o in m.mons:
            if g.visible(o.x, o.y) and not getattr(o, 'lurk', False) and not getattr(o, 'invis', 0):
                row = crs.setdefault(o.name, [o.ch, o.fg, 0])
                row[2] += 1
    creatures = [([(ch, fg)], nm + (f' x{n}' if n > 1 else '')) for nm, (ch, fg, n) in crs.items()]
    things = {}
    for it in m.items:
        if g.visible(it.x, it.y):
            things.setdefault(it.display_name(), (it.glyph(), it.color()))
    for c in getattr(m, 'slain', ()):
        if g.visible(c[1], c[2]):
            things.setdefault('Corpse', ('%', (150, 130, 110)))
    from . import bosses as BS
    if m.kind != 'over':
        mk = BS.marks(g)
        if any(g.visible(*c) and v[1] != BS.GOLDN for c, v in mk.items()):
            things.setdefault('Red ground: a great blow will land there', ('▒', (180, 40, 30)))
        if any(g.visible(*c) and v[1] == BS.GOLDN for c, v in mk.items()):
            things.setdefault('Gold ground: safe from the blow, stand in it', ('▒', (200, 170, 50)))
    if getattr(m, 'zone', None) is not None:
        from . import zones as ZN
        for (x, y), got in m.marks.items():
            lk = ZN.mark_look(g, *got) if g.visible(x, y) else None
            if lk:
                things.setdefault(ZN.mark_name(g, *got), (lk[0], lk[1]))
    return creatures, land, [([(ch, col)], nm) for nm, (ch, col) in things.items()]


def signs(g):
    """Every sign you have seen: the world map's land and places, then the map you stand on, as
    ([(glyph, colour)...], name); a heading (None, name) before the map you stand on."""
    om = g.maps['over']
    seen = [i for i, s in enumerate(om.seen) if s]
    rows = legend(om, seen)
    for poi in g.world.pois:
        if poi.found:
            rows.setdefault(NAMED_KIND.get(poi.kind, poi.name), [(poi.glyph[0], poi.glyph[1])])
    out = [(v, k) for k, v in sorted(rows.items())]
    m = g.map
    if m is not om and getattr(m, 'seen', None) is not None:
        here = legend(m, [i for i, s in enumerate(m.seen) if s])
        out.append((None, m.name))
        out += [(v, k) for k, v in sorted(here.items())]
    return out


NAMED_KIND = {'shrine': 'Shrine', 'camp': 'Outlaw camp', 'orccamp': 'Orc war camp', 'stones': 'Standing stones',
              'wagon': 'Abandoned wagon', 'waystation': 'Waystation', 'milestone': 'Milestone',
              'runestone': 'Rune stone', 'dwarfstone': 'Dwarf boundary stone', 'moonstone': 'Moonstone',
              'skullpole': 'Skull pole', 'scratch': 'Kobold scratches', 'cache': "Kobolds' hoard",
              'leaguestone': 'League stone'}


# ------------------------------------------------------------------ first-time tips
TIPS = {
    'foe': 'Tip: Tab picks a target, and the keys 1 to 6 use your skills on it.',
    'over': 'Tip: m opens the map; on it, the keys 1 to 7 show the land, danger, factions, realms, jobs, trade and the shadow.',
    'job': 'Tip: e opens the journal. Enter on a job follows it, and an arrow on the edge of the map points the way.',
    'merc': 'Tip: h gives orders to your company; there, 3 sends them at your target.',
    'dungeon': 'Tip: x explores by itself until something turns up.',
    'night': 'Tip: R rests. Out in the open you make camp: a fire keeps beasts off but draws robbers.',
    'many': 'Tip: o lets you look around; it shows what every sign in view means.',
    'land': 'Tip: > in open country takes you down into the land itself; walk on across its edges, and < brings you back up.',
    'herd': 'Tip: walk into a herd on the world map to hunt it.',
    'hunt': 'Tip: the arrow on the edge shows where the wind comes from. Keep it in your face, or they smell you.',
    'skin': 'Tip: Enter on a carcass skins it; with a knife or a dagger you get the hide too.',
    'knight': 'Tip: as a knight your liege may call you to the levy; the call comes as a job in your journal, e.',
    'realmjob': 'Tip: a lord remembers the work you do. Enough of it, with a good name in the empire, and you may swear fealty.',
    'library': 'Tip: what a scribe reads to you goes into your chronicle: e, the Lore tab, then Enter.',
    'cook': 'Tip: R in the open lets you light a fire and cook; a hearth or a fire pit works too, walk into it.',
    'class': 'Tip: Z in a town chooses the skills on keys 3 to 6; keys 1 and 2 come with the weapon in your hand.',
    'tree': 'Tip: you have a tree point to spend. Z, then Tab, while you are still where you rested.',
    'red': 'Tip: red ground shows where a great blow will land. A number counts the turns left.',
    'shut': 'Tip: the way is shut until it falls. Look for the one way out.',
    'skyseat': 'Tip: one skipper dares the whirlpool, on the harbour nearest his coast. Walk into him with a relic in your pack.',
    'shadow': 'Tip: e, then the Shadow tab, keeps what you know of the Hollow King and his servants; on the map, 7 shows their marks.',
}


def tip(g, key):
    """Say a tip once per hero."""
    done = g.__dict__.setdefault('tips', set())
    if key in done or key not in TIPS:
        return False
    done.add(key)
    g.msg(TIPS[key], 'info')
    return True


def check(g):
    """After every action: the first tip whose moment has come (one at a time, so the log stays calm)."""
    from . import mercs as MC
    from . import towns as TW
    from . import hunting as HT
    from . import cooking as CK
    m = g.map
    if g.dead:
        return
    foes = g.visible_hostiles()
    moments = [('foe', bool(foes)), ('many', len(foes) >= 3), ('over', m.kind == 'over'), ('land', m.kind == 'over' and g.turn > 600), ('job', bool(MS.active(g))),
               ('merc', bool(MC.party(g))), ('dungeon', m.kind == 'dungeon'),
               ('night', m.kind in ('over', 'wild') and TW.is_night(g)),
               ('herd', m.kind == 'over' and any(HT.seen_herd(g, h) for h in HT.herds(g))),
               ('skin', bool(HT.carcass_here(g))),
               ('cook', m.kind in ('over', 'wild') and g.turn > 900 and bool(CK.pot_items(g)) and not g.visible_hostiles())]
    for key, now in moments:
        if now and tip(g, key):
            return
