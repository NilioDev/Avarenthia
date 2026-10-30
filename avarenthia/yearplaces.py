"""More places of today (round 30), on the frame of landmarks.py: the land itself and what happened on it, people who
live apart, where the peoples meet, small secrets (poi/volken.md 45-64), and the places of the seasons (65-86).

The kinds are set down in landmarks' tables (LOOK, DESC, KINDS, THINGS, BUILD, ACT, TALK, CHOOSE, ON_ENTER, LINES,
STEP), so they are drawn, described and walked like the others; only where they lie is placed from here (PLACE),
after the places of round 29. A seasonal place is always on the map but does its thing only in its season, unless it
lives only part of the year (the drought, the travelling fair, the frost fair, the wolf winter): then `daily` hides it
(site.gone) out of season. Two old feasts are not places at all but days (`daily`): the Standing Night and the Loosing."""
import random

from . import data as D
from .data import GRASS, PATH, TREE, WALL, FLOOR, WATER, SHALLOW, SAND, FIELD, FENCE, BED, TABLE
from .worldgen import cheb
from . import landmarks as LM
from .landmarks import (kind, thing_kind, put, take, once, done, marks, land, clear, way, hut, tent, fence_ring, scatter,
                        river_through, sea_side, npc, beasts, finish, plain, say, chron, pay, give, food, curio, buff,
                        heal, hurt, rep, gossip, lore, cargo_buy, to_world, fight, night, season, scaled, ask)

PLACE = {}
BUILD, ACT, TALK, CHOOSE, STEP = LM.BUILD, LM.ACT, LM.TALK, LM.CHOOSE, LM.STEP
ON_ENTER, LINES = LM.ON_ENTER, LM.LINES

# the land itself
kind('scorch', '♦', (120, 100, 96), 'A dragon\'s scorch: a hill of black glass and old bones where no grass grows.')
kind('ltree', '♠', (220, 220, 160), 'A lightning tree: an oak struck so often it is more scar than bark.')
kind('sunkboat', '≈', (120, 200, 230), 'A clear lake with a sunken boat on the bottom, plain to see from the shore.')
kind('oldmine', '∩', (170, 150, 120), 'An old mine of men, not dwarves: a hole in the hill under a rotten winding wheel.')
kind('avalanche', '▲', (220, 230, 240), 'An avalanche field under a pass: rubble, broken trees, a cart half under the snow.')
kind('floodline', '≡', (150, 180, 200), 'A wall by the river, scratched with the heights of old floods and their years.')
# people who live apart
kind('wizard', '¡', (190, 150, 230), 'A hedge wizard\'s crooked little tower. No guild ever heard of him.')
kind('coalfam', '▲', (140, 120, 100), 'A charcoal family\'s hut deep in the wood. They never go to the village.')
kind('ferryhut', '≡', (170, 150, 110), 'A ferryman\'s hut on a river with no bridge, and a little boat.')
kind('beehill', '◘', (240, 200, 80), 'A beekeeper\'s hill: hives on a sunny slope, a beekeeper in a hood.')
kind('bothy', '⌂', (180, 170, 150), 'A shepherd\'s bothy on the heath: a stone hut to shelter in, with a hearth.')
kind('exiles', '⌂', (170, 160, 190), 'An exiles\' hamlet: three houses of those cast out of a city or a people.')
# where the peoples meet
kind('peacestone', '┴', (220, 220, 240), 'An old peace stone, where a peace between two peoples was sworn.')
kind('mixgrave', '+', (190, 190, 200), 'A graveyard of all peoples, from a village that once belonged to everyone.')
kind('tradebridge', '╬', (200, 180, 150), 'A trade bridge over a border river, half built by men and half by dwarves.')
kind('orcfarm', '⌂', (150, 170, 110), 'An orc farmstead outside the tribes, with a fence of skulls for show.')
# small secrets
kind('cache', '∙', (190, 170, 130), 'A marked stone where a robber buried what he took.')
kind('lovetree', '♣', (220, 160, 170), 'A lovers\' tree, its bark full of carved names, some of them centuries old.')
kind('still', '%', (190, 150, 110), 'A hidden still in a gully, which the baron has forbidden.')
kind('wrongmile', '╥', (180, 170, 150), 'A milestone that points the wrong way.')
# spring
kind('salmon', '≈', (230, 160, 140), 'A salmon leap below the falls. In spring and autumn the fish jump, and bears come.')
kind('floodlake', '≈', (140, 170, 200), 'A water meadow by the river. In spring it is a lake, and a farm stands in it.')
kind('lambfold', '○', (230, 230, 220), 'A lambing fold on the heath: a ring of stone where the ewes are brought in spring.')
kind('birdcliff', '▲', (230, 230, 230), 'Bird cliffs over the sea, white with birds and their nests.')
kind('orchard', '♣', (240, 210, 220), 'An orchard: white blossom in spring, apples in autumn.')
# summer
kind('drought', '≈', (190, 170, 120), 'A lake gone low in the drought, and something that stood under it.')
kind('tourney', '¶', (220, 120, 90), 'A tournament field by a baron\'s seat: tents and lists once a year, in summer.')
kind('harvest', '"', (230, 200, 100), 'A harvest camp on the great fields, where the day workers sleep.')
kind('fair', '♦', (240, 160, 200), 'A travelling fair: wagons, a beast tent, a fortune teller and a game with a prize.')
# autumn
kind('rut', '♠', (190, 140, 90), 'A rutting ground: an open glade where the stags fight in autumn.')
kind('mushwood', '♣', (200, 160, 120), 'An oak wood where the mushrooms come up in autumn, some in rings.')
kind('goosemarsh', '"', (170, 180, 140), 'A goose marsh, and a hunter\'s hut at its edge.')
kind('vineyard', '♣', (170, 90, 140), 'Vineyard slopes, with a press at the bottom.')
kind('pannage', '♣', (150, 130, 90), 'A pannage wood where the swine are turned out under the oaks in autumn.')
# winter
kind('frostfair', '*', (200, 230, 255), 'A frost fair on the frozen river: stalls on the ice, a week in the deep winter.')
kind('iceroad', '═', (200, 230, 250), 'An ice road over a frozen lake, marked with spruce boughs. Only in winter.')
kind('herdcamp', '▲', (210, 200, 180), 'The reindeer herders\' camp, where those who do not ride out stay the winter.')
kind('wolfwinter', '∩', (170, 170, 180), 'A wolves\' den near a village, in a hard winter.')
kind('snowinn', '╤', (220, 200, 170), 'An inn on a pass. When the snow shuts the pass, it fills with stranded travellers.')
# the old feasts
kind('harvstone', '■', (200, 220, 130), 'Thessa\'s harvest stone in a field, where the farmers lay the first sheaf.')

for _k, _n, _c, _f in [
    ('glass', 'black glass', '♦', (90, 80, 90)), ('dbones', 'dragon\'s bones', '%', (220, 210, 190)),
    ('stormoak', 'lightning oak', '♠', (230, 230, 170)), ('wreck', 'sunken boat', '▬', (140, 120, 90)),
    ('shaft', 'mine shaft', 'o', (90, 80, 70)), ('winch', 'winding wheel', '☼', (150, 120, 90)),
    ('cart', 'buried cart', '▀', (150, 120, 90)), ('fmarks', 'flood marks', '≡', (150, 190, 210)),
    ('wtower', 'tower door', '+', (190, 150, 230)), ('kettle', 'pot of strange things', 'o', (160, 200, 140)),
    ('boat', 'little boat', '▬', (170, 140, 100)), ('skep', 'bee hive', '◘', (240, 200, 80)),
    ('bhearth', 'hearth', '≈', (230, 140, 60)), ('note', 'note on the wall', '≡', (230, 220, 190)),
    ('pstone', 'peace stone', '┴', (230, 230, 250)), ('grave', 'grave', '+', (190, 190, 200)),
    ('seam', 'middle of the bridge', '╬', (210, 190, 150)), ('skulls', 'fence of skulls', '%', (220, 210, 186)),
    ('cstone', 'marked stone', '∙', (200, 180, 140)), ('ltrunk', 'carved trunk', '♣', (220, 160, 170)),
    ('kettle2', 'copper still', '%', (200, 140, 90)), ('milestone', 'milestone', '╥', (190, 180, 160)),
    ('leap', 'salmon leap', '≈', (230, 160, 140)), ('roof', 'roof of the farm', '^', (180, 120, 90)),
    ('fold', 'lambing fold', '○', (230, 230, 220)), ('nests', 'nests on the cliff', '∙', (240, 240, 230)),
    ('appletree', 'apple tree', '♣', (240, 210, 220)), ('mud', 'what the water left', '%', (170, 150, 110)),
    ('lists', 'the lists', '═', (220, 120, 90)), ('sheaves', 'sheaves', '"', (230, 200, 100)),
    ('beasttent', 'beast tent', '▲', (240, 160, 200)), ('fortune', 'fortune teller\'s wagon', '¤', (190, 140, 220)),
    ('game', 'ring toss', 'o', (240, 200, 120)), ('antler', 'shed antlers', 'Y', (210, 190, 150)),
    ('fring', 'ring of mushrooms', 'o', (220, 190, 160)), ('blind', 'hunter\'s blind', '#', (170, 160, 110)),
    ('press', 'wine press', 'o', (170, 90, 140)), ('pigs', 'swine under the oaks', '∙', (190, 150, 140)),
    ('stall', 'stall on the ice', 'π', (210, 230, 250)), ('bough', 'spruce bough on the ice', '♠', (110, 170, 120)),
    ('furs', 'stack of furs', '■', (190, 170, 140)), ('den', 'wolves\' den', 'o', (90, 90, 100)),
    ('hstone', 'harvest stone', '■', (200, 220, 130)),
]:
    thing_kind(_k, _n, _c, _f)


def register():
    from .nature import CURIO
    CURIO.update({
        'antlers': ('A stag\'s antlers', 12, (210, 190, 150), 'Shed antlers, many-pointed. Carvers buy them.'),
        'lovetoken': ('A carved name', 0, (220, 160, 170), 'A chip of bark with two names cut in it.'),
    })


def place(lay):
    for k, fn in PLACE.items():
        fn(lay)


def _on(game):
    """(year, month index, day of the month) today."""
    from . import calendar as CAL
    y, mo, d, _wd = CAL._split(game.day)
    return y, mo, d


def deep_winter(game):
    return _on(game)[1] in (11, 0)


def dry_summer(game):
    """One summer in three is a dry one (the mill stands still then too)."""
    return season(game) == 'summer' and (_on(game)[0] + game.seed) % 3 == 0


def hard_winter(game):
    return season(game) == 'winter' and (_on(game)[0] + game.seed) % 2 == 0


def storm(game):
    from . import weather as WX
    return WX.current(game) == 'storm'


def coins(game, n, text):
    game.player.gold += n
    game.msg(text, 'gold')


def gear(game, boost=1.2):
    from .entities import random_gear
    return give(game, random_gear(game, getattr(game.map, 'level', 2) + 1, boost))


def _near_kind(lay, kinds_, k, n, lo, hi, pred=None, name=None, **kw):
    srcs = [s for s in lay.w.sites if s.kind in kinds_]
    random.shuffle(srcs)
    made = 0
    for s in srcs:
        if made >= n:
            break
        spot = lay.around(s.x, s.y, lo, hi, 4, pred)
        if spot:
            lay.add(k, spot, name(s) if callable(name) else name, **kw)
            made += 1
    return made


def _anywhere(k, n, pred, name, gap=10, cells=None, **kw):
    def fn(lay):
        for _ in range(n):
            spot = lay.search(lambda x, y: pred(lay, x, y), gap, 6000, cells(lay) if cells else None)
            if spot:
                lay.add(k, spot, name() if callable(name) else name, **kw)
    return fn


def _t(m, x, y):
    return m.tile(x, y)


# ================================================================== the land itself
DRAGONS = ['Skarnveld', 'Oronthax', 'Vyrmalis', 'the Red Widow', 'Haelgrim', 'Ashkettle', 'Morrowfang', 'Ulvexa']


def _p_scorch(lay):
    for _ in range(max(1, scaled(1))):
        spot = lay.search(lambda x, y: lay.m.tile(x, y) in (D.HILLS, D.MOUNTAIN) and lay.road(x, y) >= 6, 10)
        if spot:
            lay.add('scorch', spot, f'{random.choice(["The Black Hill", "Glasstop", "The Burnt Crown", "Wyrmrest"])}',
                    dragon=random.choice(DRAGONS), fate=random.choice(['dead', 'gone', 'alive']),
                    scale=random.random() < .5)


def _m_scorch(game, site):
    m = land(game, site, 52, 30)
    cx, cy = m.w // 2, m.h // 2
    for y in range(m.h):
        for x in range(m.w):
            if ((x - cx) / 14) ** 2 + ((y - cy) / 8) ** 2 < 1:
                m.set(x, y, D.BAREROCK if random.random() < .5 else D.GRIT)
    for _ in range(14):
        x, y = cx + random.randint(-11, 11), cy + random.randint(-6, 6)
        if m.tile(x, y) != MARK_T:
            put(m, x, y, 'glass')
    put(m, cx, cy, 'dbones')
    way(m, (0, cy), (cx - 3, cy), D.GRIT)
    return finish(m, (0, cy))


MARK_T = D.MARK


def _a_scorch(game, site, key, x, y):
    fate = {'dead': 'It is dead: the bones are its own.', 'gone': 'It flew north a hundred years ago, and no one has '
            'seen it since.', 'alive': 'The shepherds say it still lives, far off, and sleeps.'}[site.fate]
    if key == 'dbones':
        chron(game, site, f'{site.name}: the lair of the dragon {site.dragon}. {fate}')
        if site.scale and not done(game, f'scale:{site.id}'):
            once(game, f'scale:{site.id}')
            site.scale = False
            if give(game, curio(game, 'scale')):
                game.msg('Among the ribs lies one scale, as big as your hand and as hard as iron.', 'good')
            return 5
        game.msg(f'Ribs like the beams of a hall, half sunk in black glass. {site.dragon} lay here. {fate}')
        return 2
    game.msg('Sand melted into black glass, sharp as a knife. Nothing grows here, and nothing ever will.')
    return 0


PLACE['scorch'], BUILD['scorch'], ACT['scorch'] = _p_scorch, _m_scorch, _a_scorch
LINES['scorch'] = 'No grass, no birds. The ground crunches: it is glass, black and glossy, and among it lie bones.'


def _p_ltree(lay):
    for _ in range(scaled(3)):
        spot = lay.search(lambda x, y: lay.m.tile(x, y) in (D.GRASS, D.HILLS) and not lay.near_tile(x, y, (D.FOREST,), 1), 10)
        if spot:
            lay.add('ltree', spot, f'The {random.choice(["Thunder", "Scarred", "Black", "Old Struck", "Split"])} Oak')


def _a_ltree(game, site, key, x, y):
    if storm(game):
        hurt(game, max(4, game.stats()['max_life'] // 4), 'struck by lightning under an oak')
        game.msg('White light and a crack like the world splitting: the oak is hit again, and you with it.', 'bad')
        return 2
    if once(game, f'wood:{site.id}', 60):
        if give(game, curio(game, 'stormwood')):
            game.msg('You cut a billet from a limb the last storm brought down. The wood is hard as horn and smells of '
                     'rain. Staff makers pay well for it.', 'good')
        return 10
    game.msg('Scar on scar, down to the roots. No fallen wood today.')
    return 0


def _s_ltree(game, site, m):
    p = game.player
    if storm(game) and random.random() < .08 and any(m.tells.get((p.y + b) * m.w + p.x + a) == 'stormoak'
                                                     for a in (-1, 0, 1) for b in (-1, 0, 1)):
        hurt(game, max(4, game.stats()['max_life'] // 4), 'struck by lightning under an oak')
        game.msg('The lightning finds the oak, and you beside it.', 'bad')


PLACE['ltree'], BUILD['ltree'], ACT['ltree'] = _p_ltree, LM._m_simple([(0, 0, 'stormoak')], size=(44, 26)), _a_ltree
STEP['ltree'] = _s_ltree
LINES['ltree'] = 'A lone oak on open ground, split and black, and still alive. Nothing else stands as tall for miles.'


def _p_sunkboat(lay):
    m = lay.m
    for _ in range(scaled(2)):
        spot = lay.search(lambda x, y: m.tile(x, y) in (D.GRASS, D.FOREST) and lay.near_tile(x, y, (D.WATER,), 1)
                          and not lay.river_near(x, y, 2) and lay.bio(x, y) not in ('beach', 'mangrove'), 10)
        if spot:
            lay.add('sunkboat', spot, f'{random.choice(["Clearwater", "Glass Mere", "Stillwater", "Fisher\'s Mere"])}',
                    dives=3)


def _m_sunkboat(game, site):
    m = land(game, site, 52, 30)
    cx, cy = m.w // 2 + 6, m.h // 2
    for y in range(m.h):
        for x in range(m.w):
            d = ((x - cx) / 13) ** 2 + ((y - cy) / 8) ** 2
            if d < 1:
                m.set(x, y, WATER if d < .7 else SHALLOW)
    for x in range(cx - 16, cx - 7):
        m.set(x, cy, PATH)
    put(m, cx - 8, cy, 'wreck')
    way(m, (0, cy), (cx - 16, cy))
    return finish(m, (0, cy))


def _a_sunkboat(game, site, key, x, y):
    if getattr(site, 'dives', 0) <= 0:
        game.msg('You dive down to the old boat again. Weed, a broken oar, nothing more.')
        game.end_turn(10)
        return 0
    if deep_winter(game):
        game.msg('The lake is frozen over. You see the boat under the ice, and that is all.')
        return 0
    site.dives -= 1
    r = random.random()
    game.msg('You dive into the clear cold water, down to the boat on the bottom.', 'info')
    if r < .45:
        coins(game, random.randint(20, 90), 'In the bilge, a fisherman\'s purse. The leather is rotten; the coins are not.')
    elif r < .7:
        gear(game)
        game.msg('Under the thwart lies something someone lost a long time ago.', 'good')
    elif r < .85:
        from .lifeskills import make_fish
        give(game, make_fish(game, 'pike'))
        game.msg('A pike lives in the boat now. It is less pleased about it than you are.', 'good')
    else:
        game.msg('Only weed and an old net, and the cold drives you up gasping.')
    return 20


PLACE['sunkboat'], BUILD['sunkboat'], ACT['sunkboat'] = _p_sunkboat, _m_sunkboat, _a_sunkboat
LINES['sunkboat'] = 'The water is so clear you see the bottom, and on it, the dark shape of a boat.'


def _p_oldmine(lay):
    for _ in range(scaled(3)):
        spot = lay.search(lambda x, y: lay.m.tile(x, y) == D.HILLS and 3 <= lay.road(x, y) <= 14, 10)
        if spot:
            lay.add('oldmine', spot, f'The {random.choice(["Copper", "Old Tin", "Widow\'s", "Gallows", "Deep Hope"])} Mine')


def _m_oldmine(game, site):
    m = land(game, site, 52, 30)
    cx, cy = m.w // 2, m.h // 2
    clear(m, cx, cy, 8, 5, D.GRIT)
    put(m, cx, cy - 1, 'shaft')
    put(m, cx + 3, cy - 1, 'winch')
    way(m, (0, cy + 2), (cx - 2, cy + 1))
    for _ in range(6):
        x, y = cx + random.randint(-7, 7), cy + random.randint(-4, 4)
        if m.tile(x, y) == D.GRIT:
            m.set(x, y, D.RUBBLE)
    if random.random() < .6:
        beasts(game, m, random.choice((['brown_bear'], ['bat', 'bat', 'bat'], ['wolf', 'wolf'])), (cx, cy - 2), r=3)
    return finish(m, (0, cy + 2))


def _a_oldmine(game, site, key, x, y):
    if key == 'winch':
        game.msg('A winding wheel of oak, rotten through. The rope hangs in rags into the dark.')
        return 0
    if game.hostile_visible():
        game.msg('Not with that beast about.', 'bad')
        return 0
    if once(game, f'vein:{site.id}', 30):
        from . import economy as ECO
        p = game.player
        if ECO.free_cargo(p) >= D.GOODS['ore']['w'] and random.random() < .6:
            p.cargo['ore'] = p.cargo.get('ore', 0) + 1
            game.msg('Men dug this hill empty, they thought. A pick in the right place finds a last thin vein: a load '
                     'of ore.', 'good')
        else:
            coins(game, random.randint(5, 30), 'Only spoil, and a miner\'s copper in the dust.')
        return 30
    game.msg('Spoil and dark. The vein you found is spent; come back another month.')
    return 0


PLACE['oldmine'], BUILD['oldmine'], ACT['oldmine'] = _p_oldmine, _m_oldmine, _a_oldmine
LINES['oldmine'] = 'A black hole in the hillside, a heap of grey spoil, and a winding wheel that has not turned in years.'


def _p_avalanche(lay):
    m = lay.m
    for _ in range(scaled(2)):
        spot = lay.search(lambda x, y: m.tile(x, y) in (D.HILLS, D.SNOW, D.GRASS) and lay.near_tile(x, y, (D.MOUNTAIN,), 2)
                          and lay.road(x, y) <= 6, 10)
        if spot:
            lay.add('avalanche', spot, 'The Fallen Slope')


def _m_avalanche(game, site):
    m = land(game, site, 52, 30)
    cx, cy = m.w // 2, m.h // 2
    for y in range(m.h):
        for x in range(m.w):
            if abs(x - cx - (y - cy)) < 9 and random.random() < .5:
                m.set(x, y, D.RUBBLE if random.random() < .5 else D.SNOW)
    put(m, cx, cy, 'cart')
    way(m, (0, cy), (cx - 2, cy), D.SNOW)
    return finish(m, (0, cy))


def _a_avalanche(game, site, key, x, y):
    y_, mo, _d = _on(game)
    if season(game) == 'spring' and once(game, f'thaw:{site.id}:{y_}'):
        game.msg('The spring sun has eaten the snow off the cart. Under the canvas, what the carter never came back '
                 'for.', 'good')
        coins(game, random.randint(60, 200), 'A strongbox, its lock rusted through.')
        gear(game, 1.3)
        return 20
    game.msg('A cart, half under the snow and the stones. Whatever it carried is still under there, waiting for the '
             'thaw.' if season(game) != 'spring' else 'The cart is empty now. The snow will come again next winter.')
    return 0


PLACE['avalanche'], BUILD['avalanche'], ACT['avalanche'] = _p_avalanche, _m_avalanche, _a_avalanche
LINES['avalanche'] = 'Broken trees all pointing downhill, boulders, and the wheel of a cart sticking out of the snow.'


def _p_floodline(lay):
    w = lay.w
    vs = [s for s in w.settlements if not s.is_city and lay.river_near(s.x, s.y, 2)]
    random.shuffle(vs)
    for s in vs[:scaled(2)]:
        spot = lay.around(s.x, s.y, 2, 4, 3)
        if spot:
            lay.add('floodline', spot, f'The Flood Wall of {s.name}', village=s.id)


def _a_floodline(game, site, key, x, y):
    from . import calendar as CAL
    v = game.world.settlements[site.village]
    y0 = CAL.YEAR
    years = sorted(random.Random(site.id * 7 + game.seed).sample(range(y0 - 300, y0), 5))
    text = (f'Lines cut in the stone of the wall, each with a year: {", ".join(str(y) for y in years)}. The highest is '
            f'above your head. In those years the river came into {v.name}.')
    chron(game, site, f'{site.name}: the river flooded {v.name} in {", ".join(str(y) for y in years)}.')
    if once(game, f'marker:{site.id}'):
        give(game, curio(game, 'flood'))
        text += ' A brass marker lies in the mud below the wall, washed off by the last flood.'
    say(game, site, text)
    return 1


PLACE['floodline'], BUILD['floodline'], ACT['floodline'] = _p_floodline, LM._m_simple([(0, 0, 'fmarks')]), _a_floodline
LINES['floodline'] = 'An old stone wall by the river, grey to the height of a man and green above it.'


# ================================================================== people who live apart
def _p_wizard(lay):
    for _ in range(scaled(2)):
        spot = lay.search(lambda x, y: lay.m.tile(x, y) in (D.FOREST, D.HILLS, D.GRASS) and 4 <= lay.road(x, y) <= 14, 12)
        if spot:
            from .races import random_name
            lay.add('wizard', spot, f'{random.choice(["Crooked", "Leaning", "Owl", "Toad"])} Tower',
                    wizard=random_name('human', 'male'))


def _m_wizard(game, site):
    m = land(game, site, 50, 28)
    cx, cy = m.w // 2, m.h // 2
    clear(m, cx, cy, 8, 5)
    hut(m, cx - 2, cy - 3, 5, 5, 's')
    take(m, cx, cy + 1)
    put(m, cx, cy + 1, 'wtower')
    put(m, cx + 4, cy + 1, 'kettle')
    way(m, (0, cy + 2), (cx - 1, cy + 2))
    npc(game, m, site.wizard, '#be96e6', cx - 3, cy + 2)
    return finish(m, (0, cy + 2))


def _t_wizard(game, site, o):
    opts = [('See what he sells', 'shop'), ('Ask about the old empire', 'varnish')]
    if any(i.k == 'food' and i.t == 'frog_legs' for i in game.player.inv):
        opts.insert(0, ('Give him the frog legs he wants', 'frog'))
    ask(game, site, o.name, '"No guild, no masters, no fees! Just me, and the owls. I need a frog. Not for eating. '
        'Well. Not only for eating."', opts + [('Goodbye', 'bye')])


def _c_wizard(game, site, choice, ctx):
    from .entities import Item
    if choice == 'shop':
        k = f'lm{site.id}w'
        if k not in game.shops or once(game, f'wstock:{site.id}', 10):
            game.shops[k] = [Item(game.new_id(), 'scroll', 'tp', 2), Item(game.new_id(), 'potion', 'mp', 2),
                             Item(game.new_id(), 'potion', 'cure', 1)]
        game.request = ('shop', k)
    elif choice == 'varnish':
        from . import varnish as VA
        if once(game, f'wlore:{site.id}', 30) and VA.give_lore(game, 'told', site.wizard, site.name):
            game.msg('He talks of the old empire for an hour, and most of it is true.', 'info')
        else:
            game.msg('"I told you all I know this month. Come back when I have read more."', 'talk')
    elif choice == 'frog':
        it = next(i for i in game.player.inv if i.k == 'food' and i.t == 'frog_legs')
        game.remove_one(it)
        give(game, Item(game.new_id(), 'scroll', 'tp', 1))
        game.msg('"Splendid!" He gives you a rolled scroll with the ink still wet, and you never ask what the frog was for.',
                 'good')


PLACE['wizard'], BUILD['wizard'], TALK['wizard'], CHOOSE['wizard'] = _p_wizard, _m_wizard, _t_wizard, _c_wizard
ACT['wizard'] = lambda game, site, key, x, y: game.msg('A pot of things that should not be in a pot: a newt, a little '
                                                         'wind in a jar, a sock.' if key == 'kettle' else
                                                         'The door is shut. A sign: "OUT. Or IN. Knock."') or 0
LINES['wizard'] = 'A narrow tower of piled stone, leaning like a drunk, with smoke of three colours from the chimney.'


def _p_coalfam(lay):
    for _ in range(scaled(2)):
        spot = lay.search(lambda x, y: lay.m.tile(x, y) == D.FOREST and lay.road(x, y) >= 6, 10)
        if spot:
            lay.add('coalfam', spot, f'The {random.choice(["Sooty", "Blackhand", "Ashby", "Smoke"])} Hut')


def _t_coalfam(game, site, o):
    ask(game, site, o.name, '"We never go to the village. But we see all that comes through the wood."',
        [('What came through the wood?', 'seen'), ('Goodbye', 'bye')])


def _c_coalfam(game, site, choice, ctx):
    if choice == 'seen':
        if once(game, f'seen:{site.id}', 14):
            o = next((x for x in game.map.mons if getattr(x, 'lm', None) == 'coalfam'), None)
            if o is not None:
                lore(game, o)
            else:
                gossip(game)
        else:
            game.msg('"Nothing new since you were here. A fox, a deer. The wind."', 'talk')


PLACE['coalfam'], TALK['coalfam'], CHOOSE['coalfam'] = _p_coalfam, _t_coalfam, _c_coalfam
BUILD['coalfam'] = LM._m_simple([(-3, 0, 'clamp'), (3, -1, 'clamp')],
                                who=(('The collier\'s wife', '#a08870', 0, 2), ('A sooty child', '#a08870', 2, 2)))
ACT['coalfam'] = lambda game, site, key, x, y: game.msg('A stack of turf over smouldering wood. It will burn a week.') or 0
LINES['coalfam'] = 'A hut of bark and a smoking stack in a clearing. Children with black faces watch you from the trees.'


def _p_ferryhut(lay):
    m = lay.m
    made = 0
    cells = [i for i, v in enumerate(lay.riv) if v and lay.w.road_dist[i] >= 4]
    random.shuffle(cells)
    for i in cells:
        if made >= scaled(3):
            break
        x, y = i % m.w, i // m.w
        if any(s.kind in ('tollbridge', 'tradebridge') and cheb(s.x, s.y, x, y) < 15 for s in lay.w.sites):
            continue
        spot = lay.around(x, y, 1, 1, 8)
        if not spot:
            continue
        far = (x + (x - spot[0]), y + (y - spot[1]))
        if not (m.inb(*far) and D.TILES[m.tile(*far)].walk and m.tile(*far) != D.RIVER):
            continue
        lay.add('ferryhut', spot, 'The Ferryman\'s Hut', far=far)
        made += 1


def _m_ferryhut(game, site):
    m = land(game, site, 52, 28)
    rx = river_through(m, m.w // 2 + 6)
    cy = m.h // 2
    hut(m, rx - 14, cy - 3, 5, 4, 's')
    put(m, rx - 4, cy, 'boat')
    way(m, (0, cy), (rx - 5, cy))
    npc(game, m, 'The ferryman', '#aa966e', rx - 6, cy + 1)
    return finish(m, (0, cy))


def _t_ferryhut(game, site, o):
    ask(game, site, o.name, '"No bridge for a day\'s walk either way. Eight coppers and I row you over."',
        [('Be rowed over (8c)', 'cross'), ('Goodbye', 'bye')])


def _c_ferryhut(game, site, choice, ctx):
    if choice == 'cross' and pay(game, 8, 'The crossing'):
        to_world(game, *site.far, 20, 'He rows you over, slow and steady, and the far bank is under your feet.')


PLACE['ferryhut'], BUILD['ferryhut'], TALK['ferryhut'], CHOOSE['ferryhut'] = _p_ferryhut, _m_ferryhut, _t_ferryhut, _c_ferryhut
ACT['ferryhut'] = lambda game, site, key, x, y: game.msg('A flat little boat, tarred, with one pair of oars. Ask the ferryman.') or 0
LINES['ferryhut'] = 'A hut on the bank, nets drying, and a little boat pulled up on the mud.'


def _p_beehill(lay):
    for _ in range(scaled(2)):
        spot = lay.search(lambda x, y: lay.m.tile(x, y) in (D.HILLS, D.GRASS) and lay.bio(x, y) in ('meadow', 'heath', 'moor', 'grassland', 'hills', '')
                          and lay.road(x, y) <= 8, 10)
        if spot:
            lay.add('beehill', spot, f'{random.choice(["Hum", "Honey", "Clover", "Sunny"])} Hill')


def _t_beehill(game, site, o):
    ask(game, site, o.name, '"Mind the bees. They mind you." Honey, a pot for a few coppers, or by the load if you have a '
        'wagon.', [('A pot of honey (6c)', 'pot'), ('A load of honey for the wagons (40c)', 'load'), ('Goodbye', 'bye')])


def _c_beehill(game, site, choice, ctx):
    if choice == 'pot' and pay(game, 6, 'A pot'):
        give(game, food(game, 'honey'))
    elif choice == 'load':
        cargo_buy(game, 'honey', 1, 40)


PLACE['beehill'], TALK['beehill'], CHOOSE['beehill'] = _p_beehill, _t_beehill, _c_beehill
BUILD['beehill'] = LM._m_simple([(-4, -2, 'skep'), (-1, -3, 'skep'), (2, -2, 'skep'), (5, -3, 'skep')],
                                who=(('The beekeeper', '#e6c050', 0, 1),))
ACT['beehill'] = lambda game, site, key, x, y: game.msg('The hive hums. A bee looks at you, and decides.') or 0
LINES['beehill'] = 'Straw hives in rows on a sunny slope, and the air humming.'


def _p_bothy(lay):
    for _ in range(scaled(3)):
        spot = lay.search(lambda x, y: lay.bio(x, y) in ('moor', 'heath', 'shrubland_cold', 'tundra') and lay.road(x, y) >= 3, 10)
        if spot:
            lay.add('bothy', spot, f'{random.choice(["The Shepherd\'s", "Windy", "Cold Cairn", "Last"])} Bothy')


NOTES = ['"Slept here two nights out of the rain. Left the peat stacked. Took nothing. A. the drover"',
         '"Wolves on the north side of the hill, three of them. Go round by the stream."',
         '"Whoever took my good knife: I hope it cuts you."',
         '"Mended the roof. You are welcome."',
         '"The ewes are down at the fold. If you see a grey one with a torn ear, she is mine."']


def _a_bothy(game, site, key, x, y):
    if key == 'note':
        game.msg(random.Random(site.id + game.day // 10).choice(NOTES), 'talk')
        return 1
    if game.hostile_visible():
        game.msg('Not with enemies about.', 'bad')
        return 0
    if not once(game, f'rest:{site.id}', 1):
        game.msg('You rested here today already.')
        return 0
    heal(game, 1.0, poison=False)
    game.player.__dict__.pop('cold', None)
    game.msg('You light the peat in the hearth and sleep warm and dry, out of the wind.', 'good')
    return D.DAY_LEN // 3


PLACE['bothy'], ACT['bothy'] = _p_bothy, _a_bothy
BUILD['bothy'] = LM._m_simple([(0, 0, 'bhearth'), (2, -1, 'note')], size=(44, 26))
LINES['bothy'] = 'A stone hut on the heath, a turf roof, a door that shuts against the wind.'


EXILES = [('Thrain, who has no clan', 'dwarf', '#d6b06e', 'My clan cut my name off the stone. For a debt that was not mine. '
           'Ask me about the holds.'),
          ('Aelindra, out of the wood', 'elf', '#96e6aa', 'The elders sent me out of the wood for loving a man. He is '
           'dead now. I am still out.'),
          ('Old Marta, banished', 'human', '#d0c0a0', 'The city sent me out for a witch. I only knew which herbs to pick.')]


def _p_exiles(lay):
    for _ in range(max(1, scaled(1))):
        spot = lay.search(lambda x, y: lay.m.tile(x, y) in (D.FOREST, D.HILLS) and lay.road(x, y) >= 8, 12)
        if spot:
            lay.add('exiles', spot, f'{random.choice(["Outcast", "Lost", "Lonely", "Far"])} Hamlet')


def _m_exiles(game, site):
    m = land(game, site, 56, 30)
    cx, cy = m.w // 2, m.h // 2
    clear(m, cx, cy, 12, 6)
    for k, (name, race, fg, _line) in enumerate(EXILES):
        hut(m, cx - 11 + k * 8, cy - 5, 5, 4, 's')
        npc(game, m, name, fg, cx - 9 + k * 8, cy + 1, race=race)
    way(m, (0, cy + 2), (cx - 2, cy + 2))
    return finish(m, (0, cy + 2))


def _t_exiles(game, site, o):
    line = next((ln for nm, _r, _f, ln in EXILES if nm == o.name), 'We do not talk to strangers. You, we talk to.')
    ask(game, site, o.name, f'"{line}"', [('Listen to them', 'tale'), ('See what they can spare', 'shop'), ('Goodbye', 'bye')])


def _c_exiles(game, site, choice, ctx):
    if choice == 'tale':
        if once(game, f'tale:{site.id}', 20):
            o = next((x for x in game.map.mons if getattr(x, 'lm', None) == 'exiles'), None)
            lore(game, o) if o is not None else gossip(game)
            chron(game, site, f'{site.name}: three exiles, a clanless dwarf, an elf sent out of the wood, a woman '
                              'banished for a witch. They talk to no one else.')
        else:
            game.msg('"You heard my tale. It does not get better for telling."', 'talk')
    elif choice == 'shop':
        LM.shop(game, site, 'ex', 5)


PLACE['exiles'], BUILD['exiles'], TALK['exiles'], CHOOSE['exiles'] = _p_exiles, _m_exiles, _t_exiles, _c_exiles
LINES['exiles'] = 'Three houses in a clearing, each built its own way: one of stone, one of woven branches, one of mud.'


# ================================================================== where the peoples meet
PEOPLES = [('crown', 'clan', 'men', 'dwarves'), ('crown', 'circle', 'men', 'elves'), ('clan', 'circle', 'dwarves', 'elves'),
           ('crown', 'horde', 'men', 'orcs')]


def _p_peacestone(lay):
    for _ in range(scaled(2)):
        spot = lay.search(lambda x, y: lay.m.tile(x, y) in (D.GRASS, D.HILLS) and lay.road(x, y) <= 10, 12)
        if spot:
            from . import calendar as CAL
            a, b, an, bn = random.choice(PEOPLES)
            lay.add('peacestone', spot, f'The Peace Stone of {random.choice(["Ash Ford", "Two Rivers", "the Meeting", "Oath Hill"])}',
                    sides=(a, b), names=(an, bn), year=CAL.YEAR - random.randint(80, 600))


def _a_peacestone(game, site, key, x, y):
    an, bn = site.names
    chron(game, site, f'{site.name}: in {site.year} AR {an} and {bn} swore peace here. Blood spilt here breaks it a little.')
    say(game, site, f'A grey stone with two hands cut in it, one of {an}, one of {bn}, clasped. Under it: "Here in {site.year} '
                    f'the peace was sworn. Let no blood be spilt at this stone." Old flowers lie at its foot.')
    return 1


def _k_peacestone(game, site, mon):
    if getattr(mon, 'k', '') in LM.GAME_BEASTS or not getattr(mon, 'role', None) and getattr(mon, 'faction', None) is None:
        return
    a, b = site.sides
    rep(game, a, -2)
    rep(game, b, -2)
    game.msg(f'Blood at the peace stone. {site.names[0].capitalize()} and {site.names[1]} will both hear of it.', 'bad')


PLACE['peacestone'], ACT['peacestone'] = _p_peacestone, _a_peacestone
BUILD['peacestone'] = LM._m_simple([(0, 0, 'pstone')], size=(44, 26))
LINES['peacestone'] = 'A grey stone in the grass, older than the road, and flowers at its foot that someone keeps fresh.'

EPITAPHS = ['"Hild Ironsdaughter, smith. She mended the ploughs of the whole valley."',
            '"Bramble Underhill. He ate well and laughed often."',
            '"Here lies Oswin the miller, who gave short weight to no one."',
            '"Dorn, son of Dorn. His beard reached his belt. His word reached further."',
            '"Rosie Goodbarrel. Seven children, twenty grandchildren, and the best pie in the shire."',
            '"Two friends, a man and a dwarf, buried side by side as they asked."']


def _p_mixgrave(lay):
    for _ in range(max(1, scaled(1))):
        spot = lay.search(lambda x, y: lay.m.tile(x, y) in (D.GRASS, D.HILLS) and 2 <= lay.road(x, y) <= 8, 12)
        if spot:
            lay.add('mixgrave', spot, f'The {random.choice(["Old", "Common", "Mingled", "Kindred"])} Graveyard')


def _m_mixgrave(game, site):
    m = land(game, site, 50, 28)
    cx, cy = m.w // 2, m.h // 2
    clear(m, cx, cy, 10, 6)
    fence_ring(m, cx - 9, cy - 5, cx + 9, cy + 5, (cx - 9, cy))
    for k in range(6):
        put(m, cx - 6 + (k % 3) * 6, cy - 2 + (k // 3) * 4, 'grave')
    way(m, (0, cy), (cx - 10, cy))
    return finish(m, (0, cy))


def _a_mixgrave(game, site, key, x, y):
    i = (y * 31 + x) % len(EPITAPHS)
    game.msg(f'A grave in the way of its people. On the stone: {EPITAPHS[i]}', 'talk')
    if once(game, f'graves:{site.id}', 30):
        chron(game, site, f'{site.name}: men, dwarves and halflings lie side by side, from a village that once was everyone\'s.')
        buff(game, 'regen', 1, 400, 'The peace of the old graveyard')
    return 1


PLACE['mixgrave'], BUILD['mixgrave'], ACT['mixgrave'] = _p_mixgrave, _m_mixgrave, _a_mixgrave
LINES['mixgrave'] = 'Graves of all shapes inside a low wall: stone slabs, little round doors in the turf, runes.'


def _p_tradebridge(lay):
    m = lay.m
    made = 0
    cells = [i for i, v in enumerate(lay.riv) if v and 2 <= lay.w.road_dist[i] <= 8]
    random.shuffle(cells)
    holds = lay.w.holds
    for i in cells:
        if made >= max(1, scaled(1)):
            break
        x, y = i % m.w, i // m.w
        if holds and min(cheb(x, y, h.x, h.y) for h in holds) > 40:
            continue
        spot = lay.around(x, y, 1, 1, 10)
        if not spot:
            continue
        far = (x + (x - spot[0]), y + (y - spot[1]))
        if not (m.inb(*far) and D.TILES[m.tile(*far)].walk and m.tile(*far) != D.RIVER):
            continue
        lay.add('tradebridge', spot, f'The {random.choice(["Handshake", "Two-Halves", "Crooked", "Kinship"])} Bridge', far=far)
        made += 1


def _m_tradebridge(game, site):
    m = land(game, site, 54, 30)
    rx = river_through(m)
    cy = m.h // 2
    for x in range(rx - 4, rx + 5):
        m.set(x, cy, D.BRIDGE)
        m.set(x, cy + (1 if x > rx else 0), D.BRIDGE)
    put(m, rx, cy - 1, 'seam')
    way(m, (0, cy), (rx - 5, cy))
    way(m, (rx + 5, cy + 1), (m.w - 1, cy + 1))
    return finish(m, (0, cy))


def _a_tradebridge(game, site, key, x, y):
    ask(game, site, site.name, 'In the middle the two halves meet: rough-cut human stone on this side, dwarf masonry on '
        'the other, a hand\'s width lower. A brass plate says the men built from the west, the dwarves from the east, '
        'and both swore the other measured wrong.', [('Cross the river', 'cross'), ('Leave it', 'bye')])
    return 0


def _c_tradebridge(game, site, choice, ctx):
    if choice == 'cross':
        to_world(game, *site.far, 4, 'You cross, and step down a hand\'s width in the middle like everyone does.')


PLACE['tradebridge'], BUILD['tradebridge'], ACT['tradebridge'], CHOOSE['tradebridge'] = \
    _p_tradebridge, _m_tradebridge, _a_tradebridge, _c_tradebridge
LINES['tradebridge'] = 'A broad stone bridge, and in the middle of it a step that should not be there.'


def _p_orcfarm(lay):
    m = lay.m
    for _ in range(scaled(2)):
        spot = lay.search(lambda x, y: m.tile(x, y) in (D.GRASS, D.HILLS) and lay.bio(x, y) in ('steppe', 'grassland', 'meadow', 'shrubland', 'hills', '')
                          and lay.road(x, y) >= 5, 12)
        if spot:
            lay.add('orcfarm', spot, f'{random.choice(["Grukk", "Mogha", "Tusk", "Borla"])}\'s Farm')


def _m_orcfarm(game, site):
    m = land(game, site, 54, 30)
    cx, cy = m.w // 2, m.h // 2
    clear(m, cx, cy, 13, 7)
    fence_ring(m, cx - 11, cy - 6, cx + 11, cy + 6, (cx - 11, cy))
    hut(m, cx - 3, cy - 4, 7, 5, 's')
    for x in range(cx + 3, cx + 10):
        for y in range(cy + 1, cy + 5):
            m.set(x, y, FIELD)
    put(m, cx - 11, cy - 3, 'skulls')
    way(m, (0, cy), (cx - 11, cy))
    npc(game, m, f'{site.name[:-7]} the farmer', '#96aa6e', cx - 2, cy + 2, race='half-orc')
    return finish(m, (0, cy))


def _t_orcfarm(game, site, o):
    ask(game, site, o.name, '"No raids. No chief. Cows, cabbage, cheese. The skulls are for show. Mostly. You buying?"',
        [('Buy a cheese (8c)', 'cheese'), ('Goodbye', 'bye')])


def _c_orcfarm(game, site, choice, ctx):
    if choice == 'cheese' and pay(game, 8, 'A cheese'):
        give(game, food(game, 'goat_cheese'))
        game.msg('A round hard cheese with a rind like boot leather. It is very good.', 'good')


PLACE['orcfarm'], BUILD['orcfarm'], TALK['orcfarm'], CHOOSE['orcfarm'] = _p_orcfarm, _m_orcfarm, _t_orcfarm, _c_orcfarm
ACT['orcfarm'] = lambda game, site, key, x, y: game.msg('Skulls on the fence posts: cow, goat, one that might be a '
                                                          'troll\'s. A sign under them: "FOR SHOW."') or 0
LINES['orcfarm'] = 'A tidy farm behind a fence of skulls, cabbages in rows, and a cow that looks at you.'


# ================================================================== small secrets
def _p_cache(lay):
    """A robber's cache, hidden; a wrong milestone on a road a way off points at it."""
    m = lay.m
    for _ in range(scaled(2)):
        spot = lay.search(lambda x, y: m.tile(x, y) in (D.FOREST, D.HILLS, D.GRASS) and 5 <= lay.road(x, y) <= 14, 10)
        if not spot:
            continue
        st = lay.add('cache', spot, 'A Marked Stone', hidden=True)
        mile = lay.search(lambda x, y: lay.road(x, y) == 1 and 8 <= cheb(x, y, *spot) <= 20, 4, 4000, lay.by_road())
        if mile:
            lay.add('wrongmile', mile, 'The Wrong Milestone', cache=st.id)


def _a_cache(game, site, key, x, y):
    if not once(game, f'cache:{site.id}'):
        game.msg('The hole is still there, and empty. You emptied it.')
        return 0
    take(game.map, x, y, D.GRIT)
    coins(game, random.randint(150, 400), 'Under the stone, a sack gone black with damp: a robber\'s silver.')
    gear(game, 1.4)
    chron(game, site, f'{site.name}: a robber\'s cache under a stone with a cut mark. Emptied by you.')
    return 20


def _e_cache(game, site, m):
    if not getattr(site, 'found', True):
        from .folk import discover
        discover(game, site, None)
    return None


PLACE['cache'], ACT['cache'] = _p_cache, _a_cache
BUILD['cache'] = LM._m_simple([(0, 0, 'cstone')], size=(40, 24), clearing=(5, 3))
ON_ENTER['cache'] = _e_cache
LINES['cache'] = 'A flat stone with a mark cut in it: a crow\'s foot. Not the kind of mark a farmer makes.'


def _a_wrongmile(game, site, key, x, y):
    c = game.world.sites[site.cache] if getattr(site, 'cache', None) is not None else None
    if c is None:
        game.msg('A milestone pointing into the fields.')
        return 0
    from .engine import dir_name
    d = dir_name(c.x - site.x, c.y - site.y)
    if not getattr(c, 'found', True):
        from .folk import discover
        discover(game, c, f'The milestone points {d}, off the road, where no town lies. You follow its line.')
    else:
        game.msg(f'The milestone points {d}, to the robber\'s stone.')
    chron(game, site, f'{site.name}: it points {d}, to a robber\'s cache, not to a town.')
    return 1


PLACE['wrongmile'] = lambda lay: None
ACT['wrongmile'] = _a_wrongmile
BUILD['wrongmile'] = LM._m_simple([(0, 0, 'milestone')], size=(40, 24), clearing=(5, 3))
LINES['wrongmile'] = 'A milestone like any other, but its arrow points into the fields, where no town lies.'


NAMES2 = [('Aldo', 'Merin'), ('Kettil', 'Yrsa'), ('Lucan', 'Vespera'), ('Oswy', 'Brann'), ('Pell', 'Ida'), ('Tamsin', 'Rook')]
VNAMES = [('Cassian', 'Livia'), ('Aurex', 'Selene'), ('Marcan', 'Iuna')]


def _p_lovetree(lay):
    for _ in range(scaled(2)):
        spot = lay.search(lambda x, y: lay.m.tile(x, y) in (D.GRASS, D.FOREST) and 2 <= lay.road(x, y) <= 6, 10)
        if spot:
            lay.add('lovetree', spot, 'The Lovers\' Tree')


def _a_lovetree(game, site, key, x, y):
    r = random.Random(site.id * 13 + game.seed)
    a, b = r.choice(NAMES2)
    va, vb = r.choice(VNAMES)
    text = (f'Hearts and names, hundreds, one over the other. Fresh ones: {a} and {b}. Low down, grown over with bark, '
            f'in the old letters of the Varnish: {va} and {vb}.')
    chron(game, site, f'{site.name}: the oldest names on it are of the Varnish, {va} and {vb}.')
    if once(game, f'carve:{site.id}'):
        text += ' You find a bare place and cut your own name in it.'
        give(game, curio(game, 'lovetoken'))
    say(game, site, text)
    return 2


PLACE['lovetree'], ACT['lovetree'] = _p_lovetree, _a_lovetree
BUILD['lovetree'] = LM._m_simple([(0, 0, 'ltrunk')], size=(42, 24))
LINES['lovetree'] = 'An old beech by the lane, its smooth grey bark cut with names from the root to as high as an arm reaches.'


def _p_still(lay):
    for _ in range(scaled(2)):
        spot = lay.search(lambda x, y: lay.m.tile(x, y) in (D.HILLS, D.FOREST) and lay.near_tile(x, y, (D.MOUNTAIN, D.HILLS), 1)
                          and lay.road(x, y) >= 4, 10)
        if spot:
            lay.add('still', spot, 'A Gully', hidden=True)


def _t_still(game, site, o):
    ask(game, site, o.name, '"You did not see this. Nobody sees this. A jar of the white, for a friend: ten coppers."',
        [('A jar of spirits (10c)', 'buy'), ('Tell him the Watch is looking', 'warn'), ('Goodbye', 'bye')])


def _c_still(game, site, choice, ctx):
    if choice == 'buy' and pay(game, 10, 'A jar'):
        give(game, food(game, 'juniper_spirits'))
    elif choice == 'warn' and once(game, f'warn:{site.id}', 30):
        coins(game, 30, '"Then they will find a cold pot." He presses some coppers on you and starts packing.')


def _e_still(game, site, m):
    if not getattr(site, 'found', True):
        from .folk import discover
        discover(game, site, None)
    return None


PLACE['still'], TALK['still'], CHOOSE['still'] = _p_still, _t_still, _c_still
BUILD['still'] = LM._m_simple([(0, -1, 'kettle2')], who=(('A stillman', '#c89660', 2, 1),), size=(44, 24), clearing=(6, 4))
ACT['still'] = lambda game, site, key, x, y: game.msg('A copper still over a small hot fire. It drips. It smells like '
                                                        'the end of an evening.') or 0
ON_ENTER['still'] = _e_still
LINES['still'] = 'Down in the gully, a thin smoke and a smell of mash. A copper pot, and a man who wishes you were not here.'


# ================================================================== spring
def _p_salmon(lay):
    _near_kind(lay, ('falls', 'cascade', 'rapids', 'greatfalls'), 'salmon', scaled(3), 1, 3, None,
               lambda s: f'The Leap below {s.name}')


def _m_salmon(game, site):
    m = land(game, site, 52, 30)
    rx = river_through(m, m.w // 2 + 4, 2)
    cy = m.h // 2
    for y in range(cy - 1, cy + 2):
        for x in range(rx - 3, rx + 4):
            m.set(x, y, D.RUBBLE if (x + y) % 2 else SHALLOW)
    put(m, rx - 4, cy, 'leap')
    way(m, (0, cy), (rx - 5, cy))
    if season(game) in ('spring', 'autumn'):
        beasts(game, m, ['brown_bear'], (rx + 4, cy - 4), r=3)
    return finish(m, (0, cy))


def _a_salmon(game, site, key, x, y):
    if season(game) not in ('spring', 'autumn'):
        game.msg('The river runs over the stones. No fish leap now: come in spring, or in autumn.')
        return 0
    if game.hostile_visible():
        game.msg('The bear was here first, and it wants the leap to itself.', 'bad')
        return 0
    if not once(game, f'leap:{site.id}', 1):
        game.msg('You took your share today. Let the bears have the rest.')
        return 0
    from .lifeskills import make_fish
    give(game, make_fish(game, 'salmon', random.randint(2, 3)))
    game.msg('The salmon throw themselves up the falls, silver in the spray. You scoop them out by hand.', 'good')
    return 15


PLACE['salmon'], BUILD['salmon'], ACT['salmon'] = _p_salmon, _m_salmon, _a_salmon
ON_ENTER['salmon'] = lambda game, site, m: ('Silver fish leap up the falls, and on the far bank a bear stands in the '
                                            'water, waiting.' if season(game) in ('spring', 'autumn') else None)
LINES['salmon'] = 'Water rushing white over a step of stones below the falls.'


def _p_floodlake(lay):
    m = lay.m
    made = 0
    cells = [i for i, v in enumerate(lay.riv) if v and lay.w.road_dist[i] <= 10]
    random.shuffle(cells)
    for i in cells:
        if made >= scaled(2):
            break
        x, y = i % m.w, i // m.w
        spot = lay.around(x, y, 2, 4, 10, lambda a, b: m.tile(a, b) == D.GRASS)
        if spot:
            lay.add('floodlake', spot, f'{random.choice(["Low", "Willow", "Wet", "Reed"])} Meadow')
            made += 1


def _m_floodlake(game, site):
    m = land(game, site, 54, 30)
    cx, cy = m.w // 2 + 4, m.h // 2
    flood = season(game) == 'spring'
    if flood:
        for y in range(m.h):
            for x in range(14, m.w):
                m.set(x, y, WATER if x > 18 else SHALLOW)
        hut(m, cx - 2, cy - 2, 5, 4, 's')
        for x in range(14, cx - 2):
            m.set(x, cy, SHALLOW)
        put(m, cx, cy - 1, 'roof')
    else:
        for y in range(m.h):
            for x in range(14, m.w):
                if random.random() < .5:
                    m.set(x, y, FIELD)
        hut(m, cx - 2, cy - 2, 5, 4, 's')
        npc(game, m, 'The farmer', '#c8aa80', cx, cy + 3)
    way(m, (0, cy), (14, cy))
    return finish(m, (0, cy))


def _a_floodlake(game, site, key, x, y):
    y_ = _on(game)[0]
    if season(game) == 'spring' and once(game, f'rescue:{site.id}:{y_}'):
        game.msg('You wade out to the farm, the water to your chest, and bring them off the roof one by one: a farmer, '
                 'his wife, three children, a goat.', 'good')
        coins(game, 50, 'On dry land the farmer presses half a silver on you, all he has left.')
        rep(game, 'crown', 1, quiet=True)
        chron(game, site, f'{site.name}: in the spring flood you brought a family off the roof of their farm.')
        return 40
    game.msg('The roof of the farm, just above the water. Nobody on it now.')
    return 0


def _t_floodlake(game, site, o):
    game.say(o, 'Every spring the river comes in. Every summer we plough again. What else would we do?')


PLACE['floodlake'], BUILD['floodlake'], ACT['floodlake'], TALK['floodlake'] = _p_floodlake, _m_floodlake, _a_floodlake, _t_floodlake
ON_ENTER['floodlake'] = lambda game, site, m: ('The meadow is a lake. Out in it stands a farm up to its windows, and on '
                                               'the roof, people waving.' if season(game) == 'spring' else None)
LINES['floodlake'] = 'Flat green fields by the river, a farm, and a tide mark of old reeds on its walls.'


def _p_lambfold(lay):
    for _ in range(scaled(2)):
        spot = lay.search(lambda x, y: lay.bio(x, y) in ('moor', 'heath', 'meadow', 'hills', 'shrubland_cold') and 2 <= lay.road(x, y) <= 10, 10)
        if spot:
            lay.add('lambfold', spot, f'{random.choice(["Ewe", "Lamb", "Grey Stone", "High"])} Fold')


def _t_lambfold(game, site, o):
    if season(game) != 'spring':
        game.say(o, 'Come back at lambing. Then I could use two more hands. Now it is only me and the wind.')
        return
    ask(game, site, o.name, '"Forty ewes and every one lambing tonight. Give me a day, and I pay what I can."',
        [('Help for a day', 'help'), ('Goodbye', 'bye')])


def _c_lambfold(game, site, choice, ctx):
    if choice == 'help':
        if not once(game, f'lamb:{site.id}', 3):
            game.msg('"You did your share. Rest your back."', 'talk')
            return
        game.end_turn(D.DAY_LEN // 2)
        game.player.gold += 30
        give(game, food(game, 'goat_cheese'))
        game.msg('A long day and a longer night, cold to the elbows. At dawn: thirty coppers, a cheese, and every bit '
                 'of news from the heath.', 'good')
        gossip(game)


PLACE['lambfold'], TALK['lambfold'], CHOOSE['lambfold'] = _p_lambfold, _t_lambfold, _c_lambfold
BUILD['lambfold'] = LM._m_simple([(0, 0, 'fold')], who=(('The shepherd', '#d0d0c0', 2, 2),))
ACT['lambfold'] = lambda game, site, key, x, y: game.msg('Ewes and wobbling lambs in the fold, steaming in the cold.'
                                                           if season(game) == 'spring' else 'An empty ring of stone.') or 0
LINES['lambfold'] = 'A round fold of dry stone on the heath, and a shepherd\'s crook leaning on it.'


def _p_birdcliff(lay):
    m = lay.m
    for _ in range(scaled(2)):
        spot = lay.search(lambda x, y: m.tile(x, y) in (D.HILLS, D.MOUNTAIN, D.GRASS) and lay.near_tile(x, y, (D.WATER,), 1)
                          and not lay.river_near(x, y, 3), 10)
        if spot:
            lay.add('birdcliff', spot, f'{random.choice(["Gull", "Puffin", "White", "Screaming"])} Cliffs')


def _m_birdcliff(game, site):
    m = land(game, site, 52, 30)
    sea_side(m, 12)
    cx, cy = m.w - 18, m.h // 2
    for y in range(m.h):
        m.set(cx + 1, y, D.ROCK)
    put(m, cx, cy, 'nests')
    put(m, cx, cy - 6, 'nests')
    way(m, (0, cy), (cx - 1, cy))
    return finish(m, (0, cy))


def _a_birdcliff(game, site, key, x, y):
    if season(game) != 'spring':
        game.msg('Empty ledges, white with old droppings. The birds come back in spring.')
        return 0
    if not once(game, f'eggs:{site.id}:{x}:{y}', 7):
        game.msg('You took eggs from these ledges this week.')
        return 0
    if random.random() < .2:
        hurt(game, max(3, game.stats()['max_life'] // 6), 'a fall from the bird cliffs')
        game.msg('A ledge breaks under your foot. You slide, and catch a root, and climb on with skinned hands.', 'bad')
    give(game, food(game, 'eggs', 3))
    game.msg('You climb down the cliff, the birds screaming round your head, and fill your shirt with eggs.', 'good')
    return 15


PLACE['birdcliff'], BUILD['birdcliff'], ACT['birdcliff'] = _p_birdcliff, _m_birdcliff, _a_birdcliff
LINES['birdcliff'] = 'Cliffs over the sea, every ledge a nest, and the noise of ten thousand birds.'


def _p_orchard(lay):
    for _ in range(scaled(3)):
        spot = lay.search(lambda x, y: lay.m.tile(x, y) in (D.GRASS, D.HILLS) and 1 <= lay.road(x, y) <= 4, 10)
        if spot:
            lay.add('orchard', spot, f'{random.choice(["Old", "Abbot\'s", "Long", "Red"])} Orchard')


def _m_orchard(game, site):
    m = land(game, site, 50, 28)
    cx, cy = m.w // 2, m.h // 2
    clear(m, cx, cy, 12, 7)
    for y in range(cy - 5, cy + 6, 3):
        for x in range(cx - 10, cx + 11, 4):
            put(m, x, y, 'appletree')
    way(m, (0, cy + 1), (cx - 11, cy + 1))
    return finish(m, (0, cy + 1))


def _a_orchard(game, site, key, x, y):
    s = season(game)
    if s == 'spring':
        if once(game, f'blossom:{site.id}', 30):
            buff(game, 'regen', 1, 300, 'Apple blossom', 'You sit a while under the white blossom, the bees busy over '
                 'your head. Something in you mends.')
        else:
            game.msg('White blossom and bees.')
        return 5
    if s == 'autumn' and once(game, f'apples:{site.id}', 7):
        give(game, food(game, 'apple', 4))
        game.msg('The tree is heavy with apples. Nobody minds a few.', 'good')
        return 5
    game.msg('An apple tree. ' + {'summer': 'The apples are small and green.', 'winter': 'Bare branches.'}.get(s, 'Picked.'))
    return 0


PLACE['orchard'], BUILD['orchard'], ACT['orchard'] = _p_orchard, _m_orchard, _a_orchard
ON_ENTER['orchard'] = lambda game, site, m: {'spring': 'The orchard is white with blossom, and humming.',
                                              'autumn': 'The trees bend under the apples.'}.get(season(game))
LINES['orchard'] = 'Old apple trees in rows, the grass long between them.'


# ================================================================== summer
def _p_drought(lay):
    m = lay.m
    for _ in range(scaled(2)):
        spot = lay.search(lambda x, y: m.tile(x, y) in (D.GRASS, D.SAND, D.HILLS) and lay.near_tile(x, y, (D.WATER,), 1)
                          and lay.road(x, y) <= 12, 10)
        if spot:
            lay.add('drought', spot, f'The Drowned {random.choice(["Village", "Quay", "Wreck"])}', gone=True)


def _m_drought(game, site):
    m = land(game, site, 52, 30)
    cx, cy = m.w // 2 + 4, m.h // 2
    for y in range(m.h):
        for x in range(16, m.w):
            m.set(x, y, D.GRIT if x < m.w - 8 else SHALLOW)
    for k in range(4):
        hut(m, cx - 8 + k * 5, cy - 6 + (k % 2) * 7, 4, 4, 'w', D.RUBBLE, D.GRIT)
        put(m, cx - 7 + k * 5, cy - 5 + (k % 2) * 7, 'mud')
    way(m, (0, cy), (16, cy))
    return finish(m, (0, cy))


def _a_drought(game, site, key, x, y):
    y_ = _on(game)[0]
    if not once(game, f'mud:{site.id}:{x}:{y}:{y_}'):
        game.msg('You dug here already. The mud has given what it had.')
        return 0
    r = random.random()
    if r < .4:
        coins(game, random.randint(20, 80), 'In the cracked mud, a little hoard of old coins.')
    elif r < .7:
        give(game, curio(game, 'offering')) and game.msg('Out of the mud, something given to the water long ago.', 'good')
    else:
        game.msg('Mud, a broken pot, a fish skeleton.')
    return 20


PLACE['drought'], BUILD['drought'], ACT['drought'] = _p_drought, _m_drought, _a_drought
LINES['drought'] = 'The lake has shrunk back to a pond, and where its water was stand the walls of houses, black with mud.'


def _p_tourney(lay):
    seats = [s for s in lay.w.settlements if s.is_city]
    random.shuffle(seats)
    made = 0
    for s in seats:
        if made >= scaled(2):
            break
        spot = lay.around(s.x, s.y, 3, 7, 4, lambda a, b: lay.m.tile(a, b) in (D.GRASS, D.HILLS))
        if spot:
            lay.add('tourney', spot, f'The Lists of {s.name}', town=s.id)
            made += 1


def _m_tourney(game, site):
    m = land(game, site, 56, 30)
    cx, cy = m.w // 2, m.h // 2
    clear(m, cx, cy, 16, 8)
    if season(game) == 'summer':
        for k in range(5):
            tent(m, cx - 12 + k * 6, cy - 6)
        for x in range(cx - 10, cx + 11):
            m.set(x, cy + 3, FENCE)
        put(m, cx, cy + 2, 'lists')
        npc(game, m, 'The herald', '#dc785a', cx - 4, cy)
    way(m, (0, cy), (cx - 6, cy))
    return finish(m, (0, cy))


def _t_tourney(game, site, o):
    if season(game) != 'summer':
        game.say(o, 'The lists open in summer.')
        return
    ask(game, site, o.name, '"Knights of every barony! One bout a day. The winner of a bout takes the purse, and the '
        'baron remembers his name."', [('Ride in the lists', 'joust'), ('Goodbye', 'bye')])


def _c_tourney(game, site, choice, ctx):
    if choice == 'joust':
        if not once(game, f'bout:{site.id}', 1):
            game.msg('"One bout a day, friend. Come back tomorrow."', 'talk')
            return
        p = game.player
        kn = fight(game, ['knight'], (p.x, p.y + 2), line='A knight in a painted shield steps into the lists and '
                   'salutes you with his sword.')
        for k in kn:
            k.tourney = site.id


def _k_tourney(game, site, mon):
    if getattr(mon, 'tourney', None) == site.id:
        game.player.gold += 300
        rep(game, 'crown', 2)
        chron(game, site, f'{site.name}: you won a bout in the lists.')
        game.msg('The knight yields. The crowd roars, and the herald counts three silver into your hand.', 'gold')


PLACE['tourney'], BUILD['tourney'], TALK['tourney'], CHOOSE['tourney'] = _p_tourney, _m_tourney, _t_tourney, _c_tourney
ACT['tourney'] = lambda game, site, key, x, y: game.msg('The lists: a long fence down the middle, and churned grass.') or 0
ON_ENTER['tourney'] = lambda game, site, m: ('Pennants, tents, horses, a crowd: the tournament is on.'
                                             if season(game) == 'summer' else None)
LINES['tourney'] = 'A wide field by the town, trampled, with posts where the lists stood. They come back in summer.'


def _p_harvest(lay):
    for _ in range(scaled(3)):
        spot = lay.search(lambda x, y: lay.m.tile(x, y) == D.GRASS and lay.bio(x, y) in ('meadow', 'grassland', 'steppe', '')
                          and 1 <= lay.road(x, y) <= 4, 10)
        if spot:
            lay.add('harvest', spot, f'The {random.choice(["Great", "Long", "Gold", "Wide"])} Fields')


def _t_harvest(game, site, o):
    if not (_on(game)[1] in (7, 8)):
        game.say(o, 'Come at the harvest, Goldfield and Harvestmoon. Then we need every back we can get.')
        return
    ask(game, site, o.name, '"Twenty coppers a day and your bread. Sickle\'s by the sheaves."',
        [('Work a day in the fields (20c)', 'work'), ('Ask about the road', 'news'), ('Goodbye', 'bye')])


def _c_harvest(game, site, choice, ctx):
    if choice == 'work':
        if not once(game, f'reap:{site.id}', 1):
            game.msg('"One day\'s pay a day. Come back tomorrow."', 'talk')
            return
        game.end_turn(D.DAY_LEN // 3)
        game.player.gold += 20
        give(game, food(game, 'bread'))
        game.msg('A day of sun and sweat and stubble. Twenty coppers and a loaf.', 'good')
        if random.random() < .2:
            game.msg('At the pay table the workers shout: the overseer has docked them all. It ends in shoving, and he '
                     'pays.', 'info')
    elif choice == 'news':
        gossip(game)


PLACE['harvest'], TALK['harvest'], CHOOSE['harvest'] = _p_harvest, _t_harvest, _c_harvest
BUILD['harvest'] = LM._m_simple([(-3, 1, 'sheaves'), (3, 1, 'sheaves')], who=(('The overseer', '#e6c864', 0, -1),),
                                size=(56, 30), clearing=(14, 7))
ACT['harvest'] = lambda game, site, key, x, y: game.msg('Sheaves stood up in stooks to dry.') or 0
LINES['harvest'] = 'Fields to the edge of sight, and in a corner of them, a camp of rough shelters.'


def _p_fair(lay):
    """The travelling fair: a list of stops between two towns; it is at one of them each week of summer."""
    w = lay.w
    towns = [s for s in w.settlements if s.is_city]
    for k in range(max(1, scaled(1))):
        if len(towns) < 2:
            return
        a, b = random.sample(towns, 2)
        stops = []
        for f in (.25, .5, .75):
            x, y = int(a.x + (b.x - a.x) * f), int(a.y + (b.y - a.y) * f)
            spot = lay.around(x, y, 0, 6, 4, lambda u, v: lay.m.tile(u, v) in (D.GRASS, D.HILLS))
            if spot:
                stops.append(spot)
        if len(stops) >= 2:
            lay.add('fair', stops[0], f'{random.choice(["Old Mother Pell", "The Brothers Varga", "Zandor"])}\'s Fair',
                    stops=stops, gone=True)
            lay.taken += stops[1:]


def _m_fair(game, site):
    m = land(game, site, 54, 30)
    cx, cy = m.w // 2, m.h // 2
    clear(m, cx, cy, 13, 7)
    put(m, cx - 6, cy - 3, 'beasttent')
    put(m, cx + 6, cy - 3, 'fortune')
    put(m, cx, cy + 3, 'game')
    npc(game, m, 'The fortune teller', '#be8cdc', cx + 6, cy - 1)
    npc(game, m, 'A trader of the fair', '#f0a0c8', cx - 2, cy)
    way(m, (0, cy), (cx - 4, cy))
    return finish(m, (0, cy))


def _a_fair(game, site, key, x, y):
    if key == 'beasttent':
        game.msg('In the tent: a sleepy bear on a chain, a two-headed calf in a jar, and a parrot that swears in dwarvish.')
        return 1
    if key == 'game':
        if not pay(game, 5, 'A throw'):
            return 0
        if random.random() < .15:
            give(game, curio(game, random.choice(['junk', 'pilgtoken'])))
            game.msg('Ring on the peg! The man sighs and hands you a prize.', 'good')
        else:
            game.msg('The ring bounces off the peg. "So close!" says the man, as always.')
        return 1
    game.msg('A painted wagon with stars on it, and a bead curtain.')
    return 0


def _t_fair(game, site, o):
    if o.name == 'The fortune teller':
        ask(game, site, o.name, '"Cross my palm with silver, and I tell you what lies ahead. Or behind. Or beside."',
            [('Have your fortune told (1s)', 'fortune'), ('Goodbye', 'bye')])
    else:
        ask(game, site, o.name, '"Wonders from the four corners! Well. From two of them."', [('See the goods', 'shop'), ('Goodbye', 'bye')])


def _c_fair(game, site, choice, ctx):
    if choice == 'fortune' and pay(game, 100, 'A fortune'):
        o = next((x for x in game.map.mons if x.name == 'The fortune teller'), None)
        lore(game, o) if o is not None else gossip(game)
    elif choice == 'shop':
        LM.shop(game, site, 'fair', 6)


PLACE['fair'], BUILD['fair'], ACT['fair'], TALK['fair'], CHOOSE['fair'] = _p_fair, _m_fair, _a_fair, _t_fair, _c_fair
LINES['fair'] = 'Painted wagons in a ring, music, a smell of fried dough, and children running everywhere.'


# ================================================================== autumn
def _p_rut(lay):
    for _ in range(scaled(2)):
        spot = lay.search(lambda x, y: lay.m.tile(x, y) == D.GRASS and lay.near_tile(x, y, (D.FOREST,), 1) and lay.road(x, y) >= 4, 10)
        if spot:
            lay.add('rut', spot, f'{random.choice(["Stag", "Roaring", "Hart\'s", "Antler"])} Glade')


def _m_rut(game, site):
    m = land(game, site, 52, 30)
    cx, cy = m.w // 2, m.h // 2
    clear(m, cx, cy, 11, 6)
    put(m, cx + 3, cy + 2, 'antler')
    way(m, (0, cy), (cx - 6, cy))
    if season(game) == 'autumn':
        beasts(game, m, ['red_deer', 'red_deer', 'red_deer'], (cx + 2, cy), r=5)
    return finish(m, (0, cy))


def _a_rut(game, site, key, x, y):
    if once(game, f'antler:{site.id}', 120):
        give(game, curio(game, 'antlers'))
        game.msg('Antlers in the grass, shed last winter. Twelve points.', 'good')
        return 2
    game.msg('Trampled grass and gouged earth where the stags fought.')
    return 0


PLACE['rut'], BUILD['rut'], ACT['rut'] = _p_rut, _m_rut, _a_rut
ON_ENTER['rut'] = lambda game, site, m: ('A roar like a cow in pain, and another answering: the stags are fighting. Keep '
                                         'your distance, or bring a bow.' if season(game) == 'autumn' else None)
LINES['rut'] = 'An open glade in the wood, the turf torn up as if by ploughs.'


def _p_mushwood(lay):
    for _ in range(scaled(3)):
        spot = lay.search(lambda x, y: lay.m.tile(x, y) == D.FOREST and lay.bio(x, y) in ('forest', 'deep_forest', 'birch', '')
                          and lay.road(x, y) <= 10, 10)
        if spot:
            lay.add('mushwood', spot, f'{random.choice(["Toadstool", "Mossy", "Damp", "Fairy"])} Wood')


def _a_mushwood(game, site, key, x, y):
    if season(game) != 'autumn':
        game.msg('Leaf mould and moss. The mushrooms come up in autumn.')
        return 0
    if not once(game, f'mush:{site.id}', 3):
        game.msg('You picked this wood clean for now.')
        return 0
    from .foraging import make_plant
    give(game, make_plant(game, random.choice(['chanterelle', 'cep']), 3))
    if random.random() < .25:
        give(game, make_plant(game, 'ghostcap'))
        game.msg('In the middle of the ring, pale as a candle: a ghostcap.', 'good')
    else:
        game.msg('Mushrooms everywhere, golden and brown. You fill your hat.', 'good')
    return 20


PLACE['mushwood'], ACT['mushwood'] = _p_mushwood, _a_mushwood
BUILD['mushwood'] = LM._m_simple([(0, 0, 'fring')], size=(50, 28))
ON_ENTER['mushwood'] = lambda game, site, m: ('The wood smells of earth and rain, and mushrooms stand everywhere.'
                                              if season(game) == 'autumn' else None)
LINES['mushwood'] = 'Old oaks, deep leaf mould, and a ring in the grass where nothing else grows.'


def _p_goosemarsh(lay):
    for _ in range(scaled(2)):
        spot = lay.search(lambda x, y: lay.m.tile(x, y) in (D.SWAMP, D.GRASS) and lay.near_tile(x, y, (D.SWAMP, D.WATER), 1), 10)
        if spot:
            lay.add('goosemarsh', spot, f'{random.choice(["Goose", "Grey", "Long Reed", "Honking"])} Marsh')


def _a_goosemarsh(game, site, key, x, y):
    if season(game) != 'autumn':
        game.msg('An empty marsh. The geese gather here in autumn, before they fly south.')
        return 0
    if not once(game, f'geese:{site.id}', 2):
        game.msg('The flock is up and wheeling; they will not come down near the blind again today.')
        return 0
    give(game, food(game, 'duck', 2))
    game.msg('Ten thousand geese on the water. A shot from the blind, two birds, and the whole sky goes up '
             'screaming. Nothing else will come near for an hour.', 'good')
    return 30


def _t_goosemarsh(game, site, o):
    game.say(o, 'They come every autumn from the north, and every spring they go back. I have never seen where.')


PLACE['goosemarsh'], ACT['goosemarsh'], TALK['goosemarsh'] = _p_goosemarsh, _a_goosemarsh, _t_goosemarsh
BUILD['goosemarsh'] = LM._m_simple([(2, 0, 'blind')], who=(('The goose hunter', '#aab48c', -2, 1),))
LINES['goosemarsh'] = 'Reeds, black water, and a hunter\'s hut of reeds at the edge.'


def _p_vineyard(lay):
    for _ in range(scaled(2)):
        spot = lay.search(lambda x, y: lay.m.tile(x, y) == D.HILLS and lay.bio(x, y) in ('dry_forest', 'shrubland', 'hills', 'meadow', '')
                          and lay.road(x, y) <= 5, 10)
        if spot:
            lay.add('vineyard', spot, f'{random.choice(["Sunward", "Red", "Abbey", "Long"])} Slopes')


def _t_vineyard(game, site, o):
    if season(game) != 'autumn':
        game.say(o, 'The grapes are not ready. Come in autumn, when we pick.')
        return
    last = _on(game)[1] == 10 and _on(game)[2] >= 25
    ask(game, site, o.name, '"Pickers wanted! Fifteen coppers a day."' + (' And tonight the new wine: you are welcome to '
        'it.' if last else ''), [('Pick for a day (15c)', 'pick')] + ([('Drink the new wine', 'wine')] if last else [])
        + [('Goodbye', 'bye')])


def _c_vineyard(game, site, choice, ctx):
    if choice == 'pick':
        if not once(game, f'pick:{site.id}', 1):
            game.msg('"Your basket is full for today."', 'talk')
            return
        game.end_turn(D.DAY_LEN // 3)
        game.player.gold += 15
        game.msg('Up and down the rows with a basket, sticky to the elbows. Fifteen coppers.', 'good')
    elif choice == 'wine' and once(game, f'newwine:{site.id}:{_on(game)[0]}'):
        give(game, food(game, 'wine', 2))
        buff(game, 'regen', 1, 300, 'The new wine')
        game.msg('Torches, fiddles, dancing on the pressed skins. They give you two flasks to take with you.', 'good')


PLACE['vineyard'], TALK['vineyard'], CHOOSE['vineyard'] = _p_vineyard, _t_vineyard, _c_vineyard
BUILD['vineyard'] = LM._m_simple([(0, 2, 'press')], who=(('The vintner', '#aa5a8c', 3, 1),))
ACT['vineyard'] = lambda game, site, key, x, y: game.msg('A great wooden press. It smells of last year\'s wine.') or 0
LINES['vineyard'] = 'Rows of vines on a sunny slope, and at the bottom a stone house with a press.'


def _p_pannage(lay):
    for _ in range(scaled(2)):
        spot = lay.search(lambda x, y: lay.m.tile(x, y) == D.FOREST and 2 <= lay.road(x, y) <= 8, 10)
        if spot:
            lay.add('pannage', spot, f'{random.choice(["Acorn", "Swine", "Oak", "Mast"])} Wood')


def _t_pannage(game, site, o):
    if season(game) != 'autumn':
        game.say(o, 'The swine go into the wood in autumn, for the acorns. Then I know all that happens under these oaks.')
        return
    ask(game, site, o.name, '"The pigs and I go everywhere in this wood. Want to know what we found?"',
        [('Ask what they found', 'found'), ('Goodbye', 'bye')])


def _c_pannage(game, site, choice, ctx):
    if choice == 'found':
        if once(game, f'pan:{site.id}', 14):
            o = next((x for x in game.map.mons if getattr(x, 'lm', None) == 'pannage'), None)
            lore(game, o) if o is not None else gossip(game)
        else:
            game.msg('"Acorns. Lots of acorns."', 'talk')


PLACE['pannage'], TALK['pannage'], CHOOSE['pannage'] = _p_pannage, _t_pannage, _c_pannage
BUILD['pannage'] = LM._m_simple([(2, 1, 'pigs'), (-3, 2, 'pigs')], who=(('The swineherd', '#be968c', 0, -1),))
ACT['pannage'] = lambda game, site, key, x, y: game.msg('Swine rooting under the oaks, fat and busy.' if season(game) ==
                                                          'autumn' else 'Rooted-up ground under the oaks.') or 0
LINES['pannage'] = 'An oak wood with the ground turned over, and a swineherd\'s hut of branches.'


# ================================================================== winter
def _p_frostfair(lay):
    w = lay.w
    cs = [s for s in w.settlements if s.is_city and lay.river_near(s.x, s.y, 3)]
    random.shuffle(cs)
    for s in cs[:max(1, scaled(1))]:
        spot = lay.around(s.x, s.y, 2, 5, 3)
        if spot:
            lay.add('frostfair', spot, f'The Frost Fair of {s.name}', town=s.id, gone=True)


def _m_frostfair(game, site):
    m = land(game, site, 54, 30)
    cy = m.h // 2
    for y in range(m.h):
        for x in range(14, 40):
            m.set(x, y, D.SNOW)
    for k in range(4):
        put(m, 18 + k * 6, cy - 3, 'stall')
    npc(game, m, 'A stallholder on the ice', '#c8e6ff', 24, cy)
    way(m, (0, cy), (14, cy))
    return finish(m, (0, cy))


def _a_frostfair(game, site, key, x, y):
    if pay(game, 4, 'A hot chestnut'):
        give(game, food(game, 'bread'))
        game.msg('Roast chestnuts, hot cider, a gingerbread king. You stamp your feet on the ice and eat.', 'good')
    return 1


def _t_frostfair(game, site, o):
    ask(game, site, o.name, '"Once in ten winters the river is thick enough. Buy while it lasts!"',
        [('See the goods', 'shop'), ('Goodbye', 'bye')])


def _c_frostfair(game, site, choice, ctx):
    if choice == 'shop':
        LM.shop(game, site, 'ff', 6)


def _s_frostfair(game, site, m):
    """Late in winter the ice cracks."""
    p = game.player
    if _on(game)[1] == 0 and _on(game)[2] > 20 and m.tile(p.x, p.y) != PATH and random.random() < .04 and 14 <= p.x < 40:
        hurt(game, max(3, game.stats()['max_life'] // 5), 'through the ice of a frost fair')
        game.msg('A crack like a whip, and the ice opens under you. You haul yourself out, freezing.', 'bad')


PLACE['frostfair'], BUILD['frostfair'], ACT['frostfair'], TALK['frostfair'], CHOOSE['frostfair'] = \
    _p_frostfair, _m_frostfair, _a_frostfair, _t_frostfair, _c_frostfair
STEP['frostfair'] = _s_frostfair
LINES['frostfair'] = 'Stalls and braziers on the frozen river, skaters, a roast ox, the whole town on the ice.'


def _p_iceroad(lay):
    m = lay.m
    made = 0
    for _ in range(scaled(2) * 2):
        if made >= scaled(2):
            break
        spot = lay.search(lambda x, y: lay.bio(x, y) in ('taiga', 'tundra', 'shrubland_cold', 'conifer', 'birch')
                          and lay.near_tile(x, y, (D.WATER,), 1) and not lay.river_near(x, y, 2), 10)
        if not spot:
            continue
        x, y = spot
        far = None
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            for n in range(2, 12):
                a, b = x + dx * n, y + dy * n
                if not m.inb(a, b):
                    break
                if m.tile(a, b) != D.WATER and D.TILES[m.tile(a, b)].walk and n > 2:
                    far = (a, b)
                    break
                if m.tile(a, b) != D.WATER:
                    break
            if far:
                break
        if far:
            lay.add('iceroad', spot, 'The Ice Road', far=far)
            made += 1


def _a_iceroad(game, site, key, x, y):
    if season(game) != 'winter':
        game.msg('Open water, grey and cold. The boughs that mark the ice road lie stacked on the shore till winter.')
        return 0
    thin = _on(game)[1] == 1 and _on(game)[2] > 15
    ask(game, site, site.name, 'Spruce boughs stuck in the ice, a line of them across the lake.' +
        (' The ice is grey and wet at the edges: the thaw is near.' if thin else ''),
        [('Follow the boughs over the ice', 'cross'), ('Leave it', 'bye')], thin=thin)
    return 0


def _c_iceroad(game, site, choice, ctx):
    if choice == 'cross':
        if ctx.get('thin') and random.random() < .3:
            hurt(game, max(3, game.stats()['max_life'] // 5), 'through the ice of a lake')
            game.msg('Near the far shore the ice gives. You go in to the waist and crawl out on your belly.', 'bad')
        to_world(game, *site.far, 30, 'You walk out over the ice, from bough to bough, and the far shore comes up out of '
                 'the white.')


PLACE['iceroad'], ACT['iceroad'], CHOOSE['iceroad'] = _p_iceroad, _a_iceroad, _c_iceroad
BUILD['iceroad'] = LM._m_simple([(3, 0, 'bough')], size=(44, 24))
LINES['iceroad'] = 'A lake under snow and ice, flat and white to the far shore.'


def _p_herdcamp(lay):
    rds = [r for r in lay.w.powers.get('raiders', []) if r.get('kind') == 'ice']
    for rd in rds[:2]:
        spot = lay.around(rd['x'], rd['y'], 6, 20, 6)
        if spot:
            lay.add('herdcamp', spot, f'The Winter Camp of the {rd["name"]}', raiders=rd['name'])
    if not rds:
        _anywhere('herdcamp', 1, lambda l, x, y: l.bio(x, y) == 'tundra', lambda: 'The Herders\' Camp')(lay)


def _t_herdcamp(game, site, o):
    if season(game) != 'winter':
        ask(game, site, o.name, '"Summer. The herds graze, the men are home, nobody rides out. Reindeer meat?"',
            [('Buy reindeer meat (6c)', 'meat'), ('Goodbye', 'bye')])
        return
    ask(game, site, o.name, '"The young men rode out with the first snow. We old ones stay with the herd, and sell furs."',
        [('A load of furs for the wagons (90c)', 'furs'), ('Ask where the riders went', 'where'), ('Goodbye', 'bye')])


def _c_herdcamp(game, site, choice, ctx):
    if choice == 'meat' and pay(game, 6, 'The meat'):
        give(game, food(game, 'reindeer_meat'))
    elif choice == 'furs':
        cargo_buy(game, 'furs', 1, 90)
    elif choice == 'where':
        from .engine import dir_name
        p = game.player
        raid = [wd for wd in game.world.wanderers if getattr(wd, 'kind', '') == 'raid']
        if raid:
            wd = min(raid, key=lambda r: cheb(r.x, r.y, site.x, site.y))
            game.msg(f'"South and {dir_name(wd.x - site.x, wd.y - site.y)}, with their sledges. Forty miles, maybe more."', 'talk')
        else:
            game.msg('"Nowhere yet. They sit in the long tent and sharpen things."', 'talk')
        del p


PLACE['herdcamp'], TALK['herdcamp'], CHOOSE['herdcamp'] = _p_herdcamp, _t_herdcamp, _c_herdcamp
BUILD['herdcamp'] = LM._m_simple([(-3, -1, 'furs'), (3, -1, 'tent')], who=(('An old herder', '#d2c8b4', 0, 1),))
ACT['herdcamp'] = lambda game, site, key, x, y: game.msg('Furs stacked high: reindeer, fox, wolf.' if key == 'furs'
                                                           else 'A tent of hides.') or 0
LINES['herdcamp'] = 'Hide tents in the snow, smoke, dogs, and the herd moving like a grey sea beyond.'


def _p_wolfwinter(lay):
    vs = [s for s in lay.w.settlements if not s.is_city and s.id and lay.bio(s.x, s.y) in
          ('taiga', 'conifer', 'birch', 'forest', 'tundra', 'shrubland_cold', 'hills', 'moor')]
    random.shuffle(vs)
    for s in vs[:scaled(2)]:
        spot = lay.around(s.x, s.y, 3, 7, 4)
        if spot:
            lay.add('wolfwinter', spot, f'The Wolf Den of {s.name}', village=s.id, gone=True)


def _m_wolfwinter(game, site):
    m = land(game, site, 52, 30)
    cx, cy = m.w // 2 + 6, m.h // 2
    clear(m, cx, cy, 6, 4, D.SNOW if m.tile(cx, cy) == D.SNOW else GRASS)
    put(m, cx, cy - 1, 'den')
    npc(game, m, 'The reeve', '#c8c0b0', 6, cy + 1)
    way(m, (0, cy), (cx - 4, cy))
    beasts(game, m, ['wolf', 'wolf', 'great_wolf'], (cx, cy), r=3)
    return finish(m, (0, cy))


def _t_wolfwinter(game, site, o):
    n = marks(game).get(f'wolves:{site.id}', 0)
    if n:
        marks(game)[f'wolves:{site.id}'] = 0
        game.player.gold += 40 * n
        game.msg(f'"{n} pelts!" The reeve counts out {40 * n} coppers from the village box.', 'gold')
        return
    game.say(o, 'They take a sheep a night, and last week a dog from the yard. The village pays forty coppers a pelt.')


def _k_wolfwinter(game, site, mon):
    if getattr(mon, 'k', '') in ('wolf', 'great_wolf', 'winter_wolf'):
        mk = marks(game)
        mk[f'wolves:{site.id}'] = mk.get(f'wolves:{site.id}', 0) + 1


PLACE['wolfwinter'], BUILD['wolfwinter'], TALK['wolfwinter'] = _p_wolfwinter, _m_wolfwinter, _t_wolfwinter
ACT['wolfwinter'] = lambda game, site, key, x, y: game.msg('A hole under the roots, the snow round it trampled and '
                                                             'red.') or 0
LINES['wolfwinter'] = 'Tracks in the snow, many of them, all leading to a hole under a fallen spruce.'


def _p_snowinn(lay):
    m = lay.m
    for _ in range(scaled(2)):
        spot = lay.search(lambda x, y: lay.near_tile(x, y, (D.MOUNTAIN,), 1) and lay.road(x, y) <= 2
                          and m.tile(x, y) in (D.HILLS, D.SNOW, D.GRASS), 12)
        if spot:
            lay.add('snowinn', spot, f'The {random.choice(["Pass", "Last Fire", "High Hearth", "Shut Door"])} Inn')


def _m_snowinn(game, site):
    m = LM._m_loneinn(game, site)
    if season(game) == 'winter':
        cx, cy = m.w // 2, m.h // 2
        for k, (nm, fg) in enumerate([('A stranded merchant', '#d0b080'), ('A pilgrim', '#e0d8c0'),
                                      ('A quiet traveller', '#a0a0a0')]):
            npc(game, m, nm, fg, cx - 4 + k * 3, cy - 2)
    return m


def _t_snowinn(game, site, o):
    if o.name == 'A quiet traveller':
        ask(game, site, o.name, 'He keeps his hand on his pack and his eyes on everyone else\'s.',
            [('Call him a thief', 'accuse'), ('Leave him be', 'bye')])
        return
    if o.name in ('A stranded merchant', 'A pilgrim'):
        game.say(o, random.choice(['Snowed in three days. The ale is running out, and so is my patience.',
                                   'I have heard every story in this room twice. Tell me a new one.',
                                   'Someone went through my purse last night. Not you, I hope.']))
        return
    LM.TALK['loneinn'](game, site, o)


def _c_snowinn(game, site, choice, ctx):
    if choice == 'accuse':
        if once(game, f'thief:{site.id}:{_on(game)[0]}'):
            if (site.id + _on(game)[0]) % 2:
                coins(game, 60, 'In his pack: four purses that are not his. The merchant gives you a reward from his.')
            else:
                game.msg('He empties his pack on the table: bread, socks, a letter to his mother. The room glares at you.',
                         'bad')
        else:
            game.msg('Leave the poor man alone now.', 'talk')
    else:
        LM.CHOOSE['loneinn'](game, site, choice, ctx)


PLACE['snowinn'], BUILD['snowinn'], TALK['snowinn'], CHOOSE['snowinn'] = _p_snowinn, _m_snowinn, _t_snowinn, _c_snowinn
ON_ENTER['snowinn'] = lambda game, site, m: ('The pass is shut by snow, and the inn is full to the rafters with those '
                                             'who could not cross.' if season(game) == 'winter' else None)
LINES['snowinn'] = 'A low stone inn under the pass, its roof weighed with stones against the wind.'


# ================================================================== the old feasts
def _p_harvstone(lay):
    for _ in range(scaled(2)):
        spot = lay.search(lambda x, y: lay.m.tile(x, y) == D.GRASS and 1 <= lay.road(x, y) <= 5, 10)
        if spot:
            lay.add('harvstone', spot, 'Thessa\'s Stone')


def _a_harvstone(game, site, key, x, y):
    from . import gods as GD
    if season(game) != 'autumn':
        game.msg('A flat stone in the field, worn smooth. In autumn the farmers lay the first sheaf on it, for Thessa.')
        return 0
    y_ = _on(game)[0]
    if done(game, f'sheaf:{site.id}:{y_}'):
        game.msg('Your gift lies on the stone with the farmers\' sheaf.')
        return 0
    it = next((i for i in game.player.inv if i.k in ('food', 'plant', 'fish')), None)
    if it is None:
        game.msg('The first sheaf lies on the stone. You have nothing to lay beside it.')
        if night(game) and once(game, f'watch:{site.id}:{y_}'):
            game.msg('Something comes out of the dark to eat from the stone: a hare as big as a dog, with eyes like '
                     'acorns. It looks at you, and goes.', 'info')
            chron(game, site, f'{site.name}: at night something comes out of the field to eat from Thessa\'s stone.')
        return 0
    once(game, f'sheaf:{site.id}:{y_}')
    game.remove_one(it)
    if getattr(game.player, 'god', None) == 'thessa':
        GD.gain(game, 3, 'a gift on her stone')
    game.msg(f'You lay {it.name.lower() if hasattr(it, "name") else "it"} beside the first sheaf. The wind moves over the '
             'field like a hand.', 'good')
    buff(game, 'regen', 1, 600, 'Thessa\'s stone')
    return 2


PLACE['harvstone'], ACT['harvstone'] = _p_harvstone, _a_harvstone
BUILD['harvstone'] = LM._m_simple([(0, 0, 'hstone')], size=(44, 26))
ON_ENTER['harvstone'] = lambda game, site, m: ('The first sheaf of the year lies on the stone.'
                                               if season(game) == 'autumn' else None)
LINES['harvstone'] = 'A flat stone in the middle of a field. The plough goes round it.'


STANDING = (11, 21)     # the longest night: 21 Longnight
LOOSING = (2, 14)       # the day of the Loosing: 14 Seedwake


def standing_night(game):
    _y, mo, d = _on(game)
    return (mo, d) == STANDING and night(game)


def loosing_day(game):
    _y, mo, d = _on(game)
    return (mo, d) == LOOSING


def old_feasts(game):
    """The Standing Night on the road of the bound dead, and the Loosing in a wind tower. Called each turn on the
    world map or in a place: cheap, both are a date and a spot."""
    p = game.player
    w = game.world
    y_ = _on(game)[0]
    if standing_night(game):
        here = (p.x, p.y) if game.cur == 'over' else game.over_pos
        road = next((s for s in w.sites if s.kind == 'deadroad' and cheb(s.x, s.y, *here) <= 3), None)
        if road and once(game, f'standing:{y_}'):
            sky = w.dungeons.get('skyseat')
            from .engine import dir_name
            d = dir_name(sky.x - road.x, sky.y - road.y) if sky else 'north'
            game.msg(f'On the longest night, in all their niches, the standing dead turn their heads, all at once, to the '
                     f'{d}. Toward the Sky-Seat.', 'unique')
            chron(game, road, f'{road.name}: on the longest night the bound dead all turn their heads {d}, toward the '
                              'Sky-Seat.', key=f'standing:{road.id}', chapter='The Varnish')
    if loosing_day(game) and getattr(game.map, 'site', None) is not None:
        st = w.sites[game.map.site] if game.map.site < len(w.sites) else None
        if st is not None and st.kind == 'windtower' and once(game, f'loosing:{y_}'):
            from . import varnish as VA
            game.msg('Every wind tower in the land whistles at once. Through the howl in this one, a voice, very small: '
                     'a child laughing at a wind let go.', 'unique')
            VA.give_lore(game, 'heard', 'the voice in the wind tower', st.name)


# ================================================================== who is here today
def daily(game):
    """Seasonal places that live part of the year; the travelling fair moves on each week."""
    w = game.world
    _y, mo, d = _on(game)
    s = season(game)
    for st in w.sites:
        k = st.kind
        if k == 'drought':
            st.gone = not dry_summer(game)
        elif k == 'frostfair':
            st.gone = not deep_winter(game)
        elif k == 'wolfwinter':
            st.gone = not hard_winter(game)
        elif k == 'fair':
            st.gone = s != 'summer'
            if not st.gone:
                stop = st.stops[(game.day // 7) % len(st.stops)]
                if (st.x, st.y) != tuple(stop):
                    game.maps.pop(st.map_key, None)
                    st.x, st.y = stop


def on_kill(game, mon):
    m = game.map
    k = getattr(m, 'lm', None)
    site = game.world.sites[m.site] if k else None
    if k == 'peacestone':
        _k_peacestone(game, site, mon)
    elif k == 'tourney':
        _k_tourney(game, site, mon)
    elif k == 'wolfwinter':
        _k_wolfwinter(game, site, mon)


register()
