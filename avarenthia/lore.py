"""The lore of Avarenthia, and what people say.

Avarenthia is an old land on the ruins of an older one. Twelve hundred years ago the Varnish Empire ruled it
from the Sky-Seat, a city of glass and bronze on the cliffs above the sea, and its mages bound the winds and
the dead to their will. Then came the Ruin: in a single night the Sky-Seat fell, the sea came in over the
lowlands, and the dead the mages had bound walked free. Years are still counted from that night: this is
the year 1172 After the Ruin (AR). The empire broke into the kingdoms, leagues and clans of today, and its
ruins lie everywhere under the moss: towers, temples, roads that lead nowhere.

People talk. A villager has a line for the weather and the crops, a guard for the law, a priest for the gods;
but listen long enough and they tell you more: of a ruin in the hills, a ring of stones that hums at night, a
herb that kills a horse, the burnt farms to the north where something large has begun to hunt, the army on
the march. An attentive player learns where to go, and what is happening in the world, by listening."""
import random

from . import data as D
from .worldgen import cheb

# ------------------------------------------------------------------ the history, as people tell it
HISTORY = [
    'Twelve hundred years ago the Varnish Empire held all this land, from the Sky-Seat on the sea cliffs.',
    'They say the Sky-Seat was all glass and bronze, and on a clear day you could see it from three kingdoms.',
    'In one night the Sky-Seat fell and the sea came in. That was the Ruin. We count our years from it.',
    'The Varnish mages bound the winds and the dead. When the Sky-Seat fell, the dead walked free. Some still do.',
    'Every old road in Avarenthia was laid by the empire. You can tell: they run straight, and they go nowhere now.',
    'The towers on the hills are older than any kingdom. Nobody builds like that any more. Nobody can.',
    'My grandmother said the first temples were raised by the survivors of the Ruin, to give thanks they lived.',
    'The dwarves never bowed to the empire. They closed their gates under the mountains and waited it out.',
    'Before the Ruin there were no orcs in the east. Some say the Varnish mages made them. Do not say so to an orc.',
    'The elves remember the empire. They will not speak of it, but they remember.',
    'There was a war after the Ruin, the Hundred Winters. Every family lost someone. It is why we have so many temples.',
    'The coins we use were struck from the bronze of the old empire. That is why they are so few.',
    'Fortune, fame and folly: that is what the old tales are made of. Most heroes find the last one first.',
]
GOD_LORE = {
    'solmara': ['Solmara lit the first dawn after the Ruin. That is why her temples face the east.',
                'The Dawnmother heals the poor for nothing. Her priests are not always so generous.'],
    'valdric': ['Valdric wrote the first law on the walls of the first city. The Crown claims his blessing.',
                'An oath sworn before the Iron Judge cannot be broken. Not without a price.'],
    'thessa': ['Thessa walks the woods at night. If you find a ring of white flowers, step around it.',
               'The Green Mother does not care for walls. Her shrines stand out in the open, in the rain.'],
    'durnak': ['Durnak forged the mountains and sleeps under them. The dwarves say you can hear his hammer in the deep.',
               'The Deep Smith keeps the honoured dead. Rob a grave and you rob him.'],
    'skell': ['Skell walks every road. Leave a coin at a crossroads and he may walk beside you.',
              'Merchants pray to Skell, and so do thieves. He does not seem to mind which.'],
    'morrak': ['The Hollow King was the god of the Varnish mages. Some say he was the one who brought the Sky-Seat down.',
               'Do not speak the name of the Hollow King after dark. Just in case.'],
}
RACE_LORE = {
    'dwarf': ['Under the mountain we kept the old roads open when the world above burned. We remember who helped.',
              'A dwarf never forgets a debt, or a grudge. Mostly the grudge.'],
    'elf': ['The trees are older than your kingdoms. Some of them are older than the Ruin.',
            'We do not hurry. You humans hurry, and look where it got the empire.'],
    'halfling': ['A full pantry, a dry roof and a good pipe. What more do the big folk fight about?'],
    'gnome': ['The old trees remember the Varnish. Put your ear to the bark on a still night, and you hear them.'],
    'orc': ['They call us brutes. The empire called us worse, and the empire is dust.'],
    'goblin': ['Nobody watches the edges of things. That is where we live, and where we hear everything.'],
}

# ------------------------------------------------------------------ everyday lines, by trade
from .harbour import SAILOR_BARKS  # noqa: E402
BARKS = {
    'any': ['Lovely day, isn\'t it?', 'Prices keep going up, I swear.', 'Mind how you go.', 'The temple bell woke me again.',
            'My neighbour\'s goat ate my washing. Again.', 'You\'re not from round here, are you?',
            'They say the winters were warmer when I was young. They also say I was never young.',
            'Keep to the roads after dark. That\'s all I\'ll say.', 'Have you seen my cat? Grey, one ear, hates everyone.',
            'I had a dream about the sea last night. I have never seen the sea.'],
    'farmer': ['Rain is coming, I can smell it.', 'These turnips won\'t dig themselves.', 'The crows took half the seed again.',
               'Good soil here. Bad luck, but good soil.', 'If the frost holds off another week, we\'ll eat well this winter.',
               'My father ploughed this field, and his father, and his. Same stones every year.',
               'Wolves took a calf from the high pasture. Bold, this year.'],
    'shepherd': ['Come by, come by! Daft animals.', 'Wolves took two lambs last week.', 'Mind the gate, stranger.',
                 'A sheep has more sense than a soldier. That is not saying much.'],
    'baker': ['Fresh bread! Still warm!', 'Mind the flour, love.', 'Up before the cock, every day of my life.'],
    'weaver': ['Finest cloth this side of the river.', 'My loom has been clacking since dawn.',
               'Red dye comes from a beetle, did you know? Disgusting. Beautiful, but disgusting.'],
    'woodcutter': ['Wolves in the deep woods again.', 'My back aches like an old cart.',
                   'There are trees out there I will not cut. Old ones. You can feel them watching.'],
    'fisher': ['The nets came up empty this morning.', 'Smells like a storm out on the water.',
               'The big ones bite at dusk. Everyone knows that. Nobody listens.'],
    'tanner': ['Yes, it stinks. That is how you know it is good leather.'],
    'carter': ['The road east is all potholes. My axle will not last the season.', 'Bandits took a toll off me twice this month.'],
    'cooper': ['A good barrel outlives the man who made it.'],
    'miller': ['The wheel turns, the stones grind, the flour sells. Simple. I like simple.'],
    'potter': ['Clay remembers every thumbprint. Mine are on half the jugs in the province.'],
    'guard': ['Move along.', 'Keep your blade sheathed in town.', 'Quiet night. I like quiet nights.',
              'I have my eye on you. I have my eye on everyone. It is tiring.', 'No fighting, no thieving, no singing after midnight.',
              'The captain says double watch tonight. Nobody tells me why.'],
    'child': ['Are you an adventurer? Have you killed a dragon?', 'Tag! You\'re it!', 'Mum says I can\'t go past the fence.',
              'I found a frog. His name is Sir Hopsalot.', 'When I grow up I\'m going to find the Sky-Seat. And all its gold!'],
    'drinker': ['Another round!', 'I tell you, I saw a ghost on the old road.', 'Hic.',
                'I used to be an adventurer, you know. Then I found the ale.', 'Buy me a drink and I\'ll tell you a secret. Maybe.'],
    'acolyte': ['The light keeps us.', 'Have you prayed today, traveller?', 'The candles must never go out. Never.'],
    'monk': ['Silence is a prayer too.', 'The herb garden needs weeding again.', 'We copy the old books, so the old words are not lost.'],
    'lamplighter': ['One lamp at a time, and the night is kept at bay.', 'Oil is dear this year. Light is dearer.'],
    'farmhand': ['Up at dawn, bed at dusk, and still the work is never done.'],
}
BARKS['sailor'] = SAILOR_BARKS

# ------------------------------------------------------------------ hints: where things are, how the world goes
DIST = [(6, 'a short walk'), (14, 'a few hours\' walk'), (28, 'about a day\'s walk'), (999, 'a long way')]
POI_HINT = {
    'ruin': ['an old ruin with a stair going down into the dark', 'a broken old house with a cellar nobody dares open'],
    'ruined_temple': ['the ruins of a temple with its crypt still sealed', 'a fallen temple where the bells ring on their own'],
    'ruined_monastery': ['a burnt-out monastery the monks never came back to', 'an abandoned abbey with a library underneath'],
    'ruined_tower': ['a broken tower from the days of the empire', 'a half-fallen mage tower with lights in it at night'],
    'shrine': ['a wayside shrine where the candles never go out', 'an old shrine that makes you stronger if you pray there'],
    'camp': ['an outlaw camp with a strongbox they guard day and night', 'a bandit camp, rich on stolen goods'],
    'orccamp': ['an orc war camp, where they pile what they take from the farms', 'orcs camped under a banner of scalps'],
    'stones': ['a ring of standing stones that hums at night', 'a circle of old grey stones carved with runes'],
    'wagon': ['a wagon in a ditch that nobody has come back for', 'a merchant\'s cart turned over, its cargo still under the tarp'],
}
WHO = ['My cousin', 'A tinker who came through', 'Old Maud', 'The miller\'s boy', 'A pilgrim', 'My late husband',
       'A hunter at the inn', 'The shepherd', 'Some drunk', 'A soldier on leave', 'My grandmother']


def dist_word(d):
    return next(w for lim, w in DIST if d <= lim)


def _origin(game):
    here = game.here
    p = game.player
    if here:
        return here.x, here.y
    return (p.x, p.y) if game.cur == 'over' else game.over_pos


def hint_place(game):
    """A hint about a hidden place nearby that you have not found yet."""
    from .engine import dir_name
    ox, oy = _origin(game)
    hidden = [q for q in game.world.pois if not q.found and cheb(q.x, q.y, ox, oy) < 40]
    if not hidden:
        return None
    q = min(hidden, key=lambda q: cheb(q.x, q.y, ox, oy) + random.randint(0, 12))
    global LAST_PLACE
    LAST_PLACE = (q.x, q.y)
    d = cheb(q.x, q.y, ox, oy)
    what = random.choice(POI_HINT.get(q.kind, ['something strange']))
    region = game.world.region_at(q.x, q.y).name
    way = dir_name(q.x - ox, q.y - oy)
    lines = [f'{random.choice(WHO)} swears they saw {what}, {dist_word(d)} to the {way}, in {region}.',
             f'If you go {way}, {dist_word(d)}, look out for {what}.',
             f'Out to the {way}, in {region}, there is {what}. I would not go there myself.']
    return random.choice(lines)


def hint_dungeon(game):
    """A hint about an old place below ground you have not been to."""
    from .engine import dir_name
    ox, oy = _origin(game)
    om = game.maps['over']
    cands = [d for d in game.world.dungeons.values() if not d.main and not om.seen[d.y * om.w + d.x] and getattr(d, 'site', None) is None
             and cheb(d.x, d.y, ox, oy) < 45]
    if not cands:
        return None
    d = random.choice(cands)
    dist = cheb(d.x, d.y, ox, oy)
    global LAST_PLACE
    LAST_PLACE = (d.x, d.y)
    return random.choice([f'They say there is a way down into {d.name}, {dist_word(dist)} to the {dir_name(d.x - ox, d.y - oy)}. '
                          'Treasure, they say. And worse.',
                          f'Nobody goes near {d.name} any more. It is to the {dir_name(d.x - ox, d.y - oy)}, if you must know.'])


def hint_plant(game):
    """Folk wisdom about the plants you might find."""
    from . import foraging as FG
    k = random.choice(list(FG.PLANTS))
    name, grp, food, eff, _w = FG.PLANTS[k]
    look = game.world.plant_look.get(k, 'a plant')
    say = {'deadly': f'Never eat {look}. Never. It killed my uncle\'s horse in an hour.',
           'poison': f'Eat {look} and you will see things. Not nice things.',
           'sick': f'{look.capitalize()}? Bitter as a tax collector. You will bring it up again.',
           'sleep': f'Eat {look} and you will sleep where you stand. Handy, some nights.',
           'heal': f'{look.capitalize()}: good for cuts. Chew it and put it on the wound.',
           'heal2': f'If you ever find {look}, keep it. It closes wounds like nothing else.',
           'mana': f'{look.capitalize()}: it clears the head. The monks brew it into something stronger.',
           'cure': f'{look.capitalize()}: it settles the stomach. Good against poison, too.'}.get(eff)
    are = 'are' if look.endswith('s') else 'is'
    return say or f'{look.capitalize()} {are} good eating, if you find any.'


def hint_war(game):
    """Armies on the march and strongholds changing hands."""
    w = game.world
    bands = [wd for wd in w.wanderers if wd.kind == 'warband']
    if bands:
        wd = random.choice(bands)
        h = w.holds[wd.target_hold]
        f = D.FACTIONS[wd.faction]
        return random.choice([f"{f['name']} is marching on {h.title}. Keep off the roads round there.",
                              f"Soldiers of {f['short']} went by yesterday, heading for {h.title}. A lot of them."])
    h = random.choice(w.holds) if w.holds else None
    if h:
        f = D.FACTIONS[h.faction]
        return f"{h.title} is held by {f['name']} these days. {random.choice(['For now.', 'Who knows for how long.', 'Fine by me.'])}"
    return None


def hint_evil(game):
    from . import evils as EVL
    return EVL.rumor(game)


def hint_trade(game):
    w = game.world
    s = random.choice(w.settlements)
    if random.random() < .5:
        g = random.choice(s.demand)
        return f"They say {s.name} pays well for {D.GOODS[g]['name'].lower()}."
    g = random.choice(s.produce)
    return f"{D.GOODS[g]['name']} is cheap in {s.name}, they make plenty of it there."


def hint_news(game):
    ev = [s for s in game.world.settlements if s.event]
    if not ev:
        return None
    s = random.choice(ev)
    return D.EVENTS[s.event[0]]['text'].format(town=s.name)


def hint_lore(game, npc=None):
    from .gods import temple_god
    race = getattr(npc, 'race', None)
    if npc is not None and getattr(npc, 'role', '') in ('healer', 'herbalist') and random.random() < .7:
        return random.choice(GOD_LORE.get(temple_god(game), HISTORY))
    if race in RACE_LORE and random.random() < .4:
        return random.choice(RACE_LORE[race])
    if random.random() < .25:
        return random.choice(random.choice(list(GOD_LORE.values())))
    return random.choice(HISTORY)


# the wonders of the world: what you see when you first come upon one, and how people speak of it
WONDERS = {
    'The Sky-Seat': ('Far out over the sea a broken city hangs in the empty air, and beneath it the water turns '
                     'and turns. The Sky-Seat. It did not all fall.',
                     ['Sailors will not go near the place where the sea turns. They say a city hangs over it, and it '
                      'is lit at night.', 'Blue glass washes up on the beaches. My grandfather said it comes from the '
                      'Sky-Seat, and that it never fell, not all of it.', 'A fisherman swore he heard bells under the '
                      'water, far out. The bells of the old capital, he said.']),
    'The Burning Isle': ('An island smoulders out at sea, its mountain leaking fire into the waves.',
                         ['On clear nights you can see the Burning Isle glow, out on the water.']),
    'Starfall Crater': ('A ring of broken hills around a still, round lake: the scar of a star that fell.',
                        ['A star fell, long before the Ruin. The lake it made is perfectly round.']),
    'The Elder Tree': ('One tree stands above all the forest, old beyond counting, its leaves touched with gold.',
                       ['The priests of Thessa walk a long way to see the Elder Tree. They come back quiet.']),
    'The Sundering': ('The ground simply ends. A canyon cuts across the land, so deep you cannot see the bottom.',
                      ['There is a crack in the earth in the dry country. They call it the Sundering. Drop a stone '
                       'and you never hear it land.']),
    'The White Waste': ('A plain of salt, flat and white and dead, shimmers in the heat.',
                        ['Far to the south there is a plain as white as bone. Nothing grows there. The salt traders '
                         'go anyway.']),
    'The Sea of Sand': ('The dunes roll away like a frozen sea.', ['Past the last wells the sand goes on in waves, '
                                                                    'for days. The Sea of Sand, they call it.']),
    'The Steaming Fields': ('Steam rises from pools in the snow, and now and then the ground spits boiling water.',
                            ['Up north the earth breathes steam. Hunters winter there, by the hot pools.']),
    'The Glass Hills': ('Crystals as tall as a man break out of the hillside, purple and blue.',
                        ['There are hills where the stone grows into glass. Dwarves would kill for it, they say.']),
    'The Stone Wood': ('A forest turned to stone: every trunk and branch grey and cold.',
                       ['There is a wood where the trees are stone. Do not sleep there.']),
    'The Black Mire': ('Black pools bubble in the grass, and the bones of beasts lie in them.',
                       ['The black mire takes a cow a year. Sometimes a herdsman.']),
    'The Glimmering': ('Mushrooms taller than you glow blue-green in the gloom.',
                       ['In the deep wet woods the mushrooms shine at night. The Glimmering. Pretty. Do not eat them.']),
    'The Smoking Vale': ('Steam drifts over the snow from a dozen vents, and the ground is warm underfoot.',
                         ['There is a second place up north where the earth smokes. Trappers call it the Smoking Vale.']),
    'The Shardfells': ('Shards of crystal stick out of the fellside like broken glass, catching the light.',
                       ['In the Shardfells the stone grows sharp and clear. Boots do not last long there.']),
    'The Grey Grove': ('A grove of grey stone trees, every leaf a flake of rock.',
                       ['They say a whole village slept in the Grey Grove once, and turned to stone with it.']),
    'The Pitch Hollows': ('Hollows full of black pitch, warm and stinking in the sun.',
                          ['The Pitch Hollows swallowed a wagon whole last summer. Horses and all.']),
    'The Lantern Wood': ('Pale mushrooms light the wood from below, like lanterns left on the ground.',
                         ['In the Lantern Wood you need no torch at night. You may wish you could not see, though.']),
    'The Fjords': ('The sea runs far inland between walls of rock, still and dark.',
                   ['In the cold north the sea cuts into the land like knife cuts. Good harbours, if you can bear the cold.']),
    'The Ashen Scar': ('The land is burnt black for miles, and at its heart the ground still glows.',
                       ['There is a burnt place where nothing grows back. Some say that is where it all began.']),
    "The Wyrm's Bones": ('In the sand lie the bones of something enormous: a spine, a cage of ribs, a skull with horns.',
                         ['Out in the desert lie the bones of a wyrm. Bigger than a ship, they say.']),
}


def hint_wonder(game):
    """Talk of one of the great sights of the world that you have not seen yet."""
    from .engine import dir_name
    ox, oy = _origin(game)
    om = game.maps['over']
    cands = [(n, x, y) for n, x, y in getattr(game.world, 'wonders', ()) if n in WONDERS
             and not (om.inb(x, y) and om.seen[y * om.w + x])]
    if not cands:
        return None
    n, x, y = random.choice(cands)
    global LAST_PLACE
    LAST_PLACE = (x, y)
    line = random.choice(WONDERS[n][1])
    if random.random() < .5:
        line += f' It lies {dist_word(cheb(x, y, ox, oy))} to the {dir_name(x - ox, y - oy)}.'
    return line


def hint_history(game, npc=None):
    """An event of the last two hundred years, near here; the old folk sometimes get it wrong (history.py)."""
    from . import history as HI
    return HI.hint(game, npc)


def hint_varnish(game, npc=None):
    from . import varnish as VN
    return VN.rumour(game, npc)


HINTS = [(hint_varnish, 1), (hint_wonder, 1.5), (hint_place, 4), (hint_dungeon, 2), (hint_plant, 2), (hint_evil, 3), (hint_war, 1.5), (hint_trade, 2),
         (hint_news, 1.5), (hint_lore, 2.5), (hint_history, 2)]


LAST_PLACE = None         # where the last hint pointed, for the chronicle


def hint(game, npc=None):
    """Something worth hearing: a hidden place, a herb, a war, a great evil, the price of grain, the old days."""
    from . import chronicle as CH
    global LAST_PLACE
    for _ in range(6):
        fn = random.choices([h for h, _w in HINTS], [w for _h, w in HINTS])[0]
        LAST_PLACE = None
        line = fn(game, npc) if fn in (hint_lore, hint_history, hint_varnish) else fn(game)
        if line:
            if fn in (hint_history, hint_varnish):
                return line
            if fn not in (hint_lore, hint_trade):
                remember(game, line)
            if fn is hint_lore:
                CH.heard_lore(game, line, npc)
            elif fn in (hint_place, hint_dungeon, hint_wonder):
                CH.heard_place(game, line, LAST_PLACE, npc, 'Wonders' if fn is hint_wonder else 'Places')
            return line
    return random.choice(HISTORY)


def remember(game, line):
    """The journal keeps the last things you heard that might matter."""
    heard = getattr(game, 'rumours', None)
    if heard is None:
        heard = game.rumours = []
    if line in heard:
        return
    heard.append(line)
    del heard[:-8]


def chatter(game, npc):
    """What someone says when you talk to them, or as you pass: their trade, the old days, or a hint."""
    job = getattr(npc, 'job', 'any')
    from .guilds import rumor
    secret = rumor(game) if random.random() < .15 else None
    if secret:
        return secret
    if random.random() < .04:
        from .hidden import rumor as old_way
        said = old_way(game)
        if said:
            return said
    r = random.random()
    if r < .4:
        pool = BARKS.get(job, []) + BARKS['any']
        return random.choice(pool)
    if r < .55:
        from . import chronicle as CH
        line = hint_lore(game, npc)
        CH.heard_lore(game, line, npc)
        return line
    return hint(game, npc)
