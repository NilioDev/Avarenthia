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
    'lamp post': 'An iron lamp post. The lamplighter comes by at dusk.',
}
DECO_DESC = {1: 'Damp moss grows here.', 2: 'Pale grass grows here in the dark.', 3: 'Glowing fungus casts an eerie light.',
             4: 'Old bones lie scattered about.', 5: 'Rubble and broken stone.', 6: 'Blood. Fresh, or nearly.',
             7: 'Thick cobwebs.', 8: 'A faded carpet.', 9: 'A torch burns in a bracket on the wall.',
             10: 'Crystals glitter in the rock.', 11: 'Ash and cinders.', 12: 'Green slime, faintly glowing.',
             13: 'Filth and scraps. It stinks.', 14: 'Trampled mud.', 15: 'A smoky cookfire, ringed with gnawed bones.'}
ROLE_DESC = {
    'inn': 'The innkeeper. Jobs on the board, hot meals, a bed and the local gossip.',
    'factor': "A factor of the Merchants' Guild. Trade work, and talk of prices on the roads near here.",
    'captain': 'A soldier of the garrison. Knows where the trouble is, and pays bounties.',
    'sailor': 'A sailor ashore. Brings news from far away, most of it old.',
    'merc': 'A sellsword looking for a contract.',
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
    'farmer': 'A farmer, hands like old leather. Farm folk share their table with travellers.',
    'roadinn': 'The keeper of a lonely roadside inn. Stew, a bed, and news from the road.',
    'fisher': 'An old fisherman, patient as a heron. Knows every fish in the pond by name.',
}


JOB_WORD = {'inn': 'innkeeper', 'market': 'trader', 'shop': 'outfitter', 'healer': 'priest', 'stables': 'stablemaster',
            'elder': 'village elder', 'castellan': 'castellan', 'guard': 'guard', 'thane': 'thane', 'herbalist': 'herbalist',
            'tower': 'captain of the watch', 'fisher': 'fisherman', 'client': 'client', 'farmer': 'farmer',
            'roadinn': 'innkeeper', 'factor': 'guild factor', 'captain': 'captain', 'sailor': 'sailor', 'merc': 'mercenary'}
NOUN = {'male': 'man', 'female': 'woman'}


def person(game, mon):
    """What you can tell about someone by looking at them: people, gender, trade and mood."""
    from .races import RACES, relation
    lines = []
    if mon.role in ('livestock', 'dog', 'escort') or mon.ch not in ('☺', '@', 'h'):
        return [ROLE_DESC.get(mon.role, 'An animal.')]
    race = getattr(mon, 'race', None)
    if not race:
        sid = getattr(game.map, 'sid', None)
        race = getattr(game.world.settlements[sid], 'race', 'human') if sid is not None else 'human'
    gender = getattr(mon, 'gender', None)
    rc = RACES.get(race, RACES['human'])
    child = getattr(mon, 'job', '') == 'child'
    noun = 'child' if child else NOUN.get(gender, 'person')
    if race == 'human' or child:
        who = f"{rc['adj'].capitalize()} {noun}"
    else:
        who = f"{rc['name']}" + (f", {'male' if gender == 'male' else 'female'}" if gender in NOUN else '')
    job = ('fisherwoman' if mon.role == 'fisher' and gender == 'female' else None) or JOB_WORD.get(mon.role) or (getattr(mon, 'job', '') if getattr(mon, 'job', 'any') not in ('any', 'child') else '')
    lines.append(f'People: {who}' + (f' · {job}' if job else '') + '.')
    lines.append(ROLE_DESC.get(mon.role, 'Someone from around here.'))
    god = getattr(mon, 'god', None)
    if not god and mon.role in ('healer', 'herbalist'):
        from .gods import temple_god
        god = temple_god(game)
    if god:
        from .gods import GODS
        lines.append(f"Wears the sign of {GODS[god]['name']}, {GODS[god]['title']}.")
    rel = relation(race, game.player.race)
    p = game.player
    if rel <= -15:
        lines.append(f"Eyes you coldly. Not many {rc['plural'].lower()} like {RACES[p.race]['plural'].lower()}.")
    elif rel >= 15:
        lines.append('Gives you a warm nod: one of their own.')
    elif rel >= 5:
        lines.append('Seems friendly enough.')
    lines.append('Walk into them to talk.')
    return lines


def health_word(mon):
    f = mon.hp / max(1, mon.maxhp)
    return 'unhurt' if f >= .99 else 'lightly wounded' if f > .7 else 'wounded' if f > .4 else 'badly wounded' if f > .15 else 'nearly dead'


def monster(game, mon):
    """(title, colour, lines)"""
    if mon.is_npc:
        return mon.name, mon.fg, person(game, mon)
    d = D.MONSTERS[mon.k]
    lines = []
    lore = D.LORE.get(mon.k)
    known = mon.k in game.bestiary
    rank = game.lore(mon.k)
    if getattr(mon, 'look', None):                 # what you see: this one, its sex and its looks
        lines.append(mon.look)
        if rank >= 1 and D.DOES.get(mon.k):
            lines.append(D.DOES[mon.k])
        if rank >= 2 and lore:
            lines.append(lore[2])
    elif lore and known:
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


BIOME_DESC = {
    'ocean': ('Open sea', 'Deep water, as far as the eye can see.'), 'sea': ('Sea', 'Grey-blue water, choppy and cold.'),
    'shallows': ('Shallows', 'Shallow water over sand and weed.'), 'lake': ('Lake', 'A lake, still and clear.'),
    'river': ('River', 'A river, running to the sea.'), 'beach': ('Shore', 'Sand and shingle along the water.'),
    'meadow': ('Grassland', 'Open grassland, good for grazing.'), 'steppe': ('Steppe', 'Dry grass to the horizon.'),
    'shrubland': ('Scrubland', 'Thorny bushes and hard ground.'), 'shrubland_cold': ('Moorland', 'Heather and cold wind.'),
    'forest': ('Forest', 'Oak and beech, deep shade.'), 'deep_forest': ('Old forest', 'Ancient trees, thick with moss.'),
    'conifer': ('Pinewood', 'Pine and fir, needles underfoot.'), 'taiga': ('Taiga', 'Dark spruce forest in the cold.'),
    'dry_forest': ('Dry woods', 'Sparse trees with hard leaves.'), 'jungle': ('Jungle', 'Hot, wet and green, alive with noise.'),
    'savanna': ('Savanna', 'Tall yellow grass and lonely trees.'), 'desert': ('Desert', 'Sand and heat. Little water.'),
    'badlands': ('Badlands', 'Red rock cut by dry gullies.'), 'tundra': ('Tundra', 'Frozen ground and lichen.'),
    'tundra_hills': ('Frozen hills', 'Bare hills under snow.'), 'glacier': ('Glacier', 'A river of ice.'),
    'hills': ('Hills', 'Rolling hills.'), 'mountain': ('Mountains', 'Steep rock; there is no way over.'),
    'peak': ('Peaks', 'Snow and ice; nothing lives up there.'), 'swamp': ('Swamp', 'Black water between the trees.'),
    'marsh': ('Marsh', 'Wet meadow, reeds and pools.'), 'pack_ice': ('Pack ice', 'Floes of ice grinding on the sea.'),
    'ice_shelf': ('Ice shelf', 'The ice of the far north, white without end.'),
}


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
    if site and m.seen[y * m.w + x] and not (getattr(site, 'hidden', False) and not getattr(site, 'found', True)):
        return site.name, site.glyph[1], [{'temple': 'A temple. Priests heal the sick and lift curses; a place to wake if you fall.',
                                           'monastery': 'A walled monastery. Monks, a herb garden, a warm meal for travellers.',
                                           'watchtower': 'A watchtower. From the top you can see far over the land.',
                                           'farm': 'A farmstead by the road. Farm folk often share a meal with travellers.',
                                           'roadinn': 'A roadside inn: stew, a bed and news from the road.',
                                           'valley': 'A hamlet hidden in a valley among the mountains. Nobody on the roads knows it.',
                                           'glade': 'An elven glade, hidden deep in the wood. Its path shows only to those who have walked it.'}[site.kind]]
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
                                          'orccamp': 'A war camp of orcs, with a chief and plunder.',
                                          'stones': 'A ring of standing stones, humming with old power.',
                                          'wagon': 'An abandoned wagon.', 'waystation': 'A Varnish waystation: shelter, and old words.',
                                          'milestone': 'A Varnish milestone, carved with leagues and names.'}.get(poi.kind, '')]
    dg = w.dungeon_at(x, y)
    if dg:
        return dg.name, (232, 96, 62), ['A way down into the dark.', f'{dg.depth} levels deep.']
    title, col, lines = tile(game, m, x, y)
    bio = getattr(m, 'biome', None)
    if bio is not None and m.t[y * m.w + x] != D.ROAD:
        b = m.biome_names[bio[y * m.w + x]]
        if b in BIOME_DESC:
            title, text = BIOME_DESC[b]
            lines = [text]
        if y * m.w + x in getattr(w, 'wonder_cells', ()) and getattr(w, 'wonders', None):
            name = min(w.wonders, key=lambda q: abs(q[1] - x) + abs(q[2] - y))[0]
            lines.insert(0, f'Part of {name}.')
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
        if mon and not getattr(mon, 'lurk', False):
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
