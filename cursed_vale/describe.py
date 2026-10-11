"""Short descriptions of everything you can look at (the inspect key)."""
from . import data as D

TILE_DESC = {
    'wall': 'Solid stone, cold and damp to the touch.',
    'floor': 'A worn stone floor.',
    'closed door': 'A heavy wooden door. Walk into it to open it.',
    'open door': 'An open doorway.',
    'stairs down': 'Steps leading down into the dark. Press > to descend.',
    'stairs up': 'Steps leading back up. Press < to climb.',
    'water': 'Deep water. Too deep to wade, and you cannot swim in armour.',
    'grassland': 'Open grassland, good for walking.',
    'forest': 'Woods. Slow going, and things hide among the trees.',
    'mountains': 'Steep mountains. No way through on foot.',
    'swamp': 'Boggy ground, sucking at your boots. Very slow going.',
    'village': 'A village. Press > or Enter to go in.',
    'dungeon entrance': 'A dark opening into the ground. Press > to go down.',
    'tree': 'A tree. You cannot walk through it.',
    'path': 'A beaten dirt path.',
    'well': 'A stone well with cool, clear water.',
    'rock': 'Bare rock.',
    'road': 'A road. Patrolled and fairly safe, and the quickest way to travel.',
    'hills': 'Rolling hills. Slower than the road.',
    'sand': 'Sand and shingle along the water.',
    'city': 'A walled city. Press > or Enter to go in.',
    'field': 'A field of crops.',
    'fence': 'A wooden fence.',
    'table': 'A table.',
    'bed': 'A bed. It looks very inviting.',
    'market stall': 'A market stall, covered in wares.',
    'fountain': 'A fountain in the town square.',
    'castle': 'A castle. Press > to go in, or to storm it if they are your enemies.',
    'fort': 'A fort. Press > to go in, or to storm it if they are your enemies.',
    'anvil': 'An anvil, black with years of use.',
    'altar': 'An altar. Candles burn on it.',
    'barrel': 'A barrel. Smells of ale.',
    'wooden floor': 'Wooden floorboards.',
    'river (ford)': 'A river. You can wade across, slowly. Fish swim here.',
    'signpost': 'A signpost. Walk into it to read where the roads go.',
    'shallow water': 'Shallow water, ankle deep. Things might be swimming in it.',
    'statue': 'A statue of some forgotten hero, its face worn smooth.',
    'treasure chest': 'A treasure chest! Walk into it to open it.',
    'open chest': 'An open, empty chest.',
    'gravestone': 'A weathered gravestone. The name has worn away.',
}
DECO_DESC = {1: 'Damp moss grows here.', 2: 'Pale grass grows here in the dark.', 3: 'Glowing fungus casts an eerie light.',
             4: 'Old bones lie scattered about.', 5: 'Rubble and broken stone.', 6: 'Blood. Fresh, or nearly.',
             7: 'Thick cobwebs.', 8: 'A faded carpet.', 9: 'A torch burns in a bracket on the wall.',
             10: 'Crystals glitter in the rock.', 11: 'Ash and cinders.', 12: 'Green slime, faintly glowing.'}
ROLE_DESC = {
    'inn': 'The innkeeper. Jobs on the board, hot meals and a bed.',
    'market': 'A trader. Buys and sells goods by the cartload.',
    'shop': 'An outfitter. Weapons, armour, potions and supplies; identifies items.',
    'healer': 'A priest of the temple. Heals, identifies and lifts curses.',
    'stables': 'The stablemaster. Sells mules and carts to carry more cargo.',
    'elder': 'The village elder. Knows what troubles the village.',
    'castellan': 'The castellan of this stronghold. Has work for those loyal to the cause.',
    'guard': 'A guard, keeping the peace. Mostly.',
    'villager': 'One of the local folk, going about their day.',
    'dog': 'A dog. It seems friendly.',
    'client': 'Someone who is waiting for you.',
    'thane': 'The thane, lord of this dwarven hold.',
    'herbalist': 'A herbalist monk. Knows every plant that grows, and teaches the art of brewing.',
    'tower': 'The captain of the watchtower.',
    'livestock': 'Farm animals, grazing.',
    'escort': 'The caravan you are guarding.',
}


def health_word(mon):
    f = mon.hp / max(1, mon.maxhp)
    return 'unhurt' if f >= .99 else 'lightly wounded' if f > .7 else 'wounded' if f > .4 else 'badly wounded' if f > .15 else 'nearly dead'


def monster(game, mon):
    """(title, colour, lines)"""
    if mon.is_npc:
        return mon.name, mon.fg, [ROLE_DESC.get(mon.role, 'Someone from around here.'), 'Walk into them to talk.']
    d = D.MONSTERS[mon.k]
    lines = []
    lore = D.LORE.get(mon.k)
    known = mon.k in game.bestiary
    if lore and known:
        lines.append(lore[0])
    elif d.get('boss'):
        lines.append('A creature of legend. Be very careful.')
    else:
        lines.append(f"A {d['name'].lower()}.")
    tags = []
    if mon.elite == 1:
        tags.append('a champion: tougher than its kin')
    elif mon.elite == 2 or d.get('boss'):
        tags.append('unique and dangerous')
    if mon.mods:
        tags.append(', '.join(mon.mods).lower())
    lines.append(f'Level {mon.lvl}, {health_word(mon)}' + (f'; {"; ".join(tags)}' if tags else '') + '.')
    lvl_gap = mon.lvl - game.player.lvl
    lines.append('It looks far stronger than you.' if lvl_gap >= 4 else 'It looks tougher than you.' if lvl_gap >= 2
                 else 'An even match.' if lvl_gap >= -1 else 'It should be no match for you.')
    return mon.name, mon.fg, lines


def tile(game, m, x, y):
    i = y * m.w + x
    t = D.TILES[m.t[i]]
    lines = [TILE_DESC.get(t.name, '')]
    deco = getattr(m, 'deco', None)
    if deco and deco[i] in DECO_DESC:
        lines.append(DECO_DESC[deco[i]])
    return t.name.capitalize(), t.fg, [ln for ln in lines if ln]


def over(game, x, y):
    """Things on the overworld: places, travellers, the land itself."""
    from .wanderers import wanderer_at
    from . import events as EV, evils as EVL
    w = game.world
    m = game.maps['over']
    wd = wanderer_at(game, x, y) if game.visible(x, y) else None
    if wd:
        return wd.name, wd.fg, [wd.describe(game), 'Hostile. They will attack if you come close.' if wd.hostile
                                else 'Walk into them to talk.']
    s = w.settlement_at(x, y)
    if s:
        f = D.FACTIONS[s.faction]
        from .races import RACES
        return s.name, (242, 196, 74), [f"A {s.kind_name} of {RACES[s.race]['plural'].lower()}, held by {f['name']}.",
                                         'Makes ' + ', '.join(D.GOODS[k]['name'].lower() for k in s.produce) + '; wants '
                                         + ', '.join(D.GOODS[k]['name'].lower() for k in s.demand) + '.']
    from .sites import site_at
    site = site_at(w, x, y)
    if site and m.seen[y * m.w + x]:
        return site.name, site.glyph[1], [{'temple': 'A temple. Priests heal the sick and lift curses; a place to wake if you fall.',
                                           'monastery': 'A walled monastery. Monks, a herb garden, a warm meal for travellers.',
                                           'watchtower': 'A watchtower. From the top you can see far over the land.'}[site.kind]]
    h = w.hold_at(x, y)
    if h:
        return h.title, D.FACTIONS[h.faction]['fg'], [f"A {h.kind} of {D.FACTIONS[h.faction]['name']}, garrison {h.garrison}."]
    poi = EV.poi_at(game, x, y)
    if poi and poi.found:
        if poi.kind in EV.RUIN_KINDS:
            return poi.name, poi.glyph[1], ['A ruin, long abandoned. A way leads down into the dark.']
        return poi.name, poi.glyph[1], [{
                                          'shrine': 'A wayside shrine. You could pray here.',
                                          'camp': 'A camp of outlaws, and their loot.',
                                          'stones': 'A ring of standing stones, humming with old power.',
                                          'wagon': 'An abandoned wagon.'}.get(poi.kind, '')]
    dg = w.dungeon_at(x, y)
    if dg:
        return dg.name, (232, 96, 62), ['A way down into the dark.', f'{dg.depth} levels deep.']
    title, col, lines = tile(game, m, x, y)
    lines.append(f'{w.region_at(x, y).name}, danger {w.danger_at(x, y)}.')
    ev = EVL.taint_at(game, x, y)
    if ev:
        lines.append({'blight': 'The land here is grey and dying.', 'scorch': 'The land here is burned black.',
                      'web': 'Webs hang from every branch.', 'warpath': 'Trampled, burned and bloodied ground.',
                      'mire': 'The ground is turning to bog.'}[ev.d['taint']])
    return title, col, lines


def at(game, x, y):
    """Describe whatever is at map cell (x, y)."""
    m = game.map
    p = game.player
    if not m.inb(x, y):
        return 'Nothing', (120, 120, 120), ['Beyond the edge of the map.']
    i = y * m.w + x
    if not game.visible(x, y) and not m.seen[i]:
        return 'Unknown', (120, 120, 120), ['You have not seen this place.']
    if (x, y) == (p.x, p.y):
        from .races import RACES
        return p.name, (255, 246, 220), [f"You. A {RACES[p.race]['name'].lower()} with no past, level {p.lvl}."]
    if m.kind == 'over':
        return over(game, x, y)
    if game.visible(x, y):
        mon = m.mon_at(x, y)
        if mon:
            return monster(game, mon)
        its = [it for it in m.items if it.x == x and it.y == y]
        if its:
            it = its[-1]
            lines = it.lines()[:2]
            if len(its) > 1:
                lines.append(f'And {len(its) - 1} more thing{"s" if len(its) > 2 else ""} beneath it.')
            return it.display_name(), it.color(), lines
    title, col, lines = tile(game, m, x, y)
    if not game.visible(x, y):
        lines.append('(You remember this from earlier.)')
    return title, col, lines
