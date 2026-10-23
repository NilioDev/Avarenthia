"""The Adventurer's Handbook: how the game works, opened with ? at the page that fits where you are.

Every chapter is a list of blocks; the book screen (ui.BookScreen) lays them out. Text marks a key in square
brackets, [e], drawn as a gold keycap, and a map sign in braces, {≡}, drawn free in its own colour. What can come
from the data does (peoples, gods, months, rarity colours, money, the signs you have seen, every key in the menu),
so the book cannot go stale. Every change to the game changes this file in the same commit.

Blocks:
  ('p', text)             a paragraph            ('h', text)        a section heading (listed in the contents)
  ('k', keys, text)       a key and what it does ('n', text)        a tip in the margin
  ('l', [text...])        a list with dots       ('o', [text...])   a numbered list
  ('r', [(label, text)])  gold labels and text   ('t', [cells], [[cells]...])  a small table, the first row its head
  ('s', [(glyphs, text)]) map signs and what they mean ('map', caption)   a real piece of the map around you
"""
from . import calendar as CAL
from . import data as D
from . import gods as GODS
from . import races as RC
from . import skills as SK

KEY_RE = r'(\[[^\]]+\]|\{[^}]+\})'

# the colours of the signs the text names, as the map draws them
SIGN_COL = {
    '@': (255, 246, 220), '≡': (196, 170, 255), 'C': (170, 150, 130), '┬': (208, 160, 96), 'Π': (176, 166, 150),
    '†': (150, 210, 255), '∆': (232, 92, 72), 'Ψ': (196, 126, 255), '¤': (204, 164, 104), 'Σ': (200, 196, 170),
    '╥': (150, 160, 130), 'Φ': (150, 200, 190), '•': (190, 220, 160), '♠': (120, 200, 120), '■': (217, 165, 71),
    '□': (58, 46, 34), '!': (255, 214, 40), '?': (134, 196, 111), '⌂': (242, 196, 74), '>': (232, 96, 62),
    '≈': (70, 130, 200), '♣': (47, 128, 64), '▲': (163, 156, 142), '∩': (154, 138, 90), '·': (200, 164, 106),
    '%': (180, 60, 50), '¡': (236, 176, 84), '¥': (206, 206, 216), '○': (106, 162, 216), '☼': (255, 140, 50),
    'q': (160, 88, 58), 'Q': (160, 88, 58), ':': (190, 160, 116),
    '♦': (224, 190, 80), '╓': (220, 200, 150), '╦': (220, 200, 150), 'Æ': (214, 176, 120), '╪': (240, 236, 216),
    '╫': (160, 168, 186), '¶': (226, 184, 90), '‼': (210, 178, 110), 'º': (220, 200, 150),
}


def sign_col(ch):
    if ch in SIGN_COL:
        return SIGN_COL[ch]
    for t in D.TILES:
        if t.ch == ch:
            return t.fg
    return (217, 165, 71)


# ------------------------------------------------------------------ the chapters
def ch_first_steps(g):
    return [
        ('p', 'You are an adventurer in Avarenthia, a wide land of towns, roads, wilds and old ruins. There is no fixed '
              'story: you choose where to go and what to do. This handbook tells you how things work. You can open it '
              'at any time with [?].'),
        ('h', 'Your first day'),
        ('o', ['Walk with the arrow keys or the numpad. Walk into a door to open it.',
               'Talk to the priestess beside you in the temple, then find the inn in Thornfield and talk to the '
               'innkeeper: walk into them. Ask for work.',
               'Take a job. The journal [e] holds it; press [Enter] on it to follow it.',
               'Leave town by the gate. On the world map, an arrow at the edge points to your job.',
               'Keep to the roads at first. They are patrolled; the wilds are not.',
               'Come back to the inn to hand the job in, get paid, and sleep in a bed.']),
        ('h', 'The keys you need'),
        ('k', '[arrows]', 'move; walk into things to fight, talk or open them'),
        ('k', '[Enter]', 'do the obvious thing where you stand: go in, take the stairs, pick up, read'),
        ('k', '[Esc]', 'the menu: everything else you can do, each with its own key'),
        ('k', '[?]', 'this handbook, opened at the page that fits where you are'),
        ('p', 'That is all you need to play. Other keys you learn as you go: the first time something new turns up, a '
              'tip in the log names its key.'),
        ('h', 'What the screen shows'),
        ('p', 'The map on the left. The panel on the right: your life, stamina and mana, your money, and IN SIGHT, the '
              'enemies you can see. The line under the map: where you stand and how dangerous it is. The log at the '
              'bottom: what just happened.'),
        ('h', 'Saving'),
        ('p', 'There is one save, and it is made for you whenever you go from one place to another and when you quit '
              'from the menu: [Esc], Game, Save and quit. In Hardcore, death is final.'),
    ]


def ch_moving(g):
    return [
        ('h', 'Walking'),
        ('p', 'Every step is one turn, and the world moves only when you do. [Shift] with a direction runs until '
              'something interesting happens. Wait a turn with [.] or [5] on the numpad.'),
        ('h', 'Bumping'),
        ('p', 'Walking into something does what makes sense: you attack an enemy, talk to a person, open a door, dig '
              'an ore vein when you carry a pick. [Enter] does the obvious thing for what lies under your feet.'),
        ('h', 'Looking around'),
        ('p', '[o] lets you move a cursor over everything you can see. It lists what each sign in view means; [Enter] '
              'on a creature opens what you know of it.'),
        ('h', 'Exploring'),
        ('p', 'In a dungeon or a ruin, [x] walks by itself until something turns up. Any key stops it.'),
        ('h', 'The map'),
        ('p', '[m] opens the map of the realm. You only see the land you have walked or been told about. The keys [1] '
              'to [6] show it in layers: Land, Danger, Factions, Realms, Jobs and Trade; [L] goes through them in turn. '
              'In a town, [m] shows the town plan with every shop named, and [Tab] switches to the realm.'),
    ]


def ch_fighting(g):
    return [
        ('p', 'You fight by walking into an enemy. Every step and every blow is one turn, and the enemies move when '
              'you do: nothing happens while you think.'),
        ('map', 'fight'),
        ('h', 'Picking a target'),
        ('k', '[Tab]', 'the next enemy in sight; [Shift+Tab] the one before.'),
        ('k', '[Esc]', 'let go of your target.'),
        ('h', 'Skills and potions'),
        ('k', '[1-6]', 'use a skill from your bar, at your target or else the nearest enemy. [1] and [2] come with the '
                       'weapon in your hand, [3] to [6] are the ones you chose. Weapon skills and Warcraft cost '
                       'stamina, spells mana.'),
        ('k', '[q] [w]', 'drink a health or a mana potion. It takes a turn.'),
        ('k', '[f]', 'shoot with a bow, crossbow or sling at your target, throw a knife or your spear, or strike a foe two '
                     'tiles away with a spear or a staff.'),
        ('h', 'IN SIGHT'),
        ('p', 'The panel lists every enemy you can see, with a bar for its life and what it is doing: closing in, '
              'fleeing, stunned, unaware of you.'),
        ('h', 'Spells you can see'),
        ('p', 'A bolt flies to its foe and bursts where it strikes; lightning leaps from one foe to the next; life you '
              'drain flows back to you in red motes. The area of a spell is a square, as far every way, but it opens '
              'out round; the faint cloud beyond its edge harms nobody. Each school has its own hand: frost goes out '
              'from you in a ring of ice, a war cry in a wave of !, a howl bends out round you; a Meteor throws its '
              'shadow on the ground before it falls; a corpse you raise greys before it gets up; Morrak takes your own '
              'life out in red before his purple falls on all around you; and when you call the storm, the sky goes '
              'white for a moment. Arrows and the spells of monsters fly the same way, so you see what is coming. Any '
              'key skips an effect: the game never waits for one. On the main menu, Spell effects can be full, short '
              'or off.'),
        ('p', 'On a foe, burning flickers orange, poison pulses green, the frozen stand on pale blue ice and the '
              'weakened look dim.'),
        ('h', 'Running away'),
        ('p', 'Wolves are fast; bandits are not. Walk off the edge of the field to get away, or onto a road: the '
              'patrols are there.'),
        ('h', 'Elements'),
        ('p', 'Fire, cold, lightning and poison. Monsters resist some and fear others; fight a kind to learn which. '
              'Your gear can give you resistance to each, up to 75%.'),
        ('h', 'Night'),
        ('p', 'Night brings the dead and bigger packs.'),
        ('n', 'Every kind you kill or skin teaches you about it, in three steps: its weakness and resistances, then what '
              'it carries, then its weak spot, where your blows strike home more often. A library scribe can read you '
              'the first step for beasts you have met. Know a kind well and you hit it harder, and it hits you less '
              'often. The look line and the bestiary [v] show what you know.'),
    ]


def ch_hero(g):
    rows = [(RC.RACES[k]['name'], RC.RACES[k]['perks'][0] + '; ' + RC.RACES[k]['perks'][1].lower())
            for k in RC.RACE_ORDER]
    return [
        ('h', 'Your people'),
        ('r', rows),
        ('p', 'How a town sees your people changes its prices and how its faction greets you.'),
        ('h', 'Attributes'),
        ('p', f'Strength, Dexterity, Vitality and Energy. Every level gives you {D.LEVEL_STAT_POINTS} points to spend '
              'on the character sheet [c].'),
        ('l', ['Strength: harder blows in melee, more stamina, and the heavy gear asks for it.',
               'Dexterity: aim, defence and bows; the light gear asks for it.',
               'Vitality: more life, and more stamina.',
               'Energy: more mana, and stronger spells.']),
        ('h', 'Stamina and mana'),
        ('p', 'The weapon skills and Warcraft cost stamina; spells cost mana. Warcraft works with any weapon in hand '
              'and grows stronger with Strength. Stamina comes back quickly on every turn you do not strike, at half '
              'the pace in chain or plate, and not at all while you are starving. A fighter who also casts must '
              'choose where the points go.'),
        ('h', 'Skills'),
        ('p', 'Skills come from three places: the weapon in your hand, the tomes of your classes, and the guild masters. '
              'Tomes, the sign {≡}, are found on monsters, in ruins and at standing stones, or bought from peddlers '
              'and city outfitters. Disciplines grow as you use them, and decide which tomes you can understand. '
              'Who you become tells how classes and the bar work.'),
        ('p', 'Six weapon disciplines: Unarmed, Swordsmanship, Axes and Maces, Spears and Staves, Daggers, Bows and '
              'Crossbows. The weapon in your main hand decides which one grows.'),
        ('p', 'Each school of magic, and Warcraft, has eight tomes, at ranks 0, 5, 12, 20, 30, 42, 55 and 70. Three '
              'keys for so many: choose.'),
        ('h', 'The schools'),
        ('p', 'Each school has a rule of its own, and most of them show on the map.'),
        ('l', ['Fire: the hardest blows on one foe. The burning take more fire, and fire leaves burning ground; in '
               'a dry summer it can set the grass of the plain alight.',
               'Frost: walls of ice across a corridor, ice on water to walk over, snow that slows. They melt again.',
               'Storm: crowds. Water carries lightning: a foe in water or out in the rain takes more, and the arc '
               'leaps further from it. Ball Lightning rolls on by itself.',
               'Restoration: keeps you and your company whole. What it hurts, it hurts twice as hard if it is undead.',
               'Shadow: curses, and a price. From rank 30 Morrak takes life as well as mana. Shadow alone steals life '
               'back.',
               'Necromancy: the fallen leave a corpse, the sign {%}, where they died. The stronger spells use '
               'corpses up: to rise and fight for you, to shield you, to breathe out poison. Walls of bone hold a '
               'foe fast.',
               'Nature: roots that hold and brambles that cut grow on the ground. A quarter stronger in forest and '
               'grass, a quarter weaker in the desert, on ice and under the ground.',
               'Beastcraft: almost everything goes through your beast; Tame is a tome of its own.',
               'In the shape of a beast you stay the sign {@|255,246,220}, in the colours of a bear or a wolf.',
               'Warcraft: shouts and stances, with any weapon in hand. The Iron Company teaches Shield Bash, which drives '
               'a foe back a tile, and Block, which catches the first blow of each turn; both need a shield.']),
        ('p', 'What a spell leaves on the ground is named when you look with [o], and a foe standing in it says so '
              'under IN SIGHT.'),
        ('h', 'Life skills'),
        ('p', 'They grow by doing; [C] shows them all.'),
        ('l', ['Fishing: by water, with a pole: [a]. Strike when the float plunges, then keep the fish in the green '
               'while the line holds.',
               'Foraging: search the wild for food and herbs: [F].',
               'Herbalism: picking herbs and knowing them.',
               'Alchemy and brewing: potions, ale, wine and mead: [P].',
               'Mining: walk into an ore vein with a pick to dig it.',
               'Hunting: reading tracks and stalking herds.',
               'Skinning: [Enter] on a carcass, with a knife or a dagger.',
               'Cooking: walk into a fire or a hearth.',
               'Leatherworking: at a workbench, and tanning with oak bark.']),
    ]


def ch_who(g):
    from . import classes as CL
    from . import weaponskills as WS
    pure = [f'{CL.school(k) if k in SK.DISCIPLINES else k.title()}: {n}' for k, n in CL.PURE.items()
            if k in CL.CLASS_LINES]
    rules = [f'{n}: {WS.RULE[k]}' for k, n in (('unarmed', 'Fists, cestus and claws'), ('swords', 'Swords'),
             ('axes', 'Axes, maces and hammers'), ('staves', 'Staves'), ('spears', 'Spears'),
             ('daggers', 'Daggers'), ('archery', 'Bows, crossbows and slings'), ('shield', 'A shield'),
             ('grimoire', 'A grimoire'))]
    return [
        ('h', 'A blank start'),
        ('p', 'You begin as nobody in particular: a weapon, your fists and what you can learn. The first tome of a '
              'school you read wakes a memory, and that school becomes your class. It asks you first. From then on '
              'only tomes of your class speak to you; any other tome you may sell or keep.'),
        ('h', 'A second class'),
        ('p', f'At rank {CL.SECOND_AT} in your class, one tome of another school may open to you. It asks you first, '
              'for it is for good: that school becomes your second class, and the two together give you a name of '
              'your own, a Paladin, a Lich or a Wildkin among fifty-five. There is no third. Who never takes a second '
              'stays pure:'),
        ('l', pure),
        ('h', 'The bar'),
        ('p', 'Six keys in three groups. [1] and [2] are your weapon\'s own two skills: they change when you take up '
              'another kind of weapon, and the second opens at rank 10 in its discipline. [3] to [5] are three skills '
              'of your classes. [6] is your elite, the sign {☼|255,214,90}: one technique a guild master taught you. '
              'Choose them in a town with [z]. The panel shows the three groups, with your name beside SKILLS.'),
        ('h', 'What your weapon adds'),
        ('p', 'Every kind of weapon also changes how your class skills work:'),
        ('l', rules),
    ]


def ch_gear(g):
    rar = ' · '.join(f'{k}' for k in ('normal', 'magic', 'rare', 'unique'))
    return [
        ('h', 'Slots and grades'),
        ('p', 'Ten slots. Normal, exceptional and elite grades; some gear needs Strength or Dexterity. A two-handed '
              'weapon takes the off-hand as well.'),
        ('h', 'Weapon kinds'),
        ('l', ['Spears, halberds, scythes and staves reach two tiles in a straight line, past a friend too. A spear '
               'can be thrown; it lies where it fell until you walk over it again. A scythe sweeps the tiles on either '
               'side of your blow.',
               'A scimitar cuts in passing: the first blow after a step does half again as much.',
               'A flail swings over a shield, a shield wall or a formation, but it is hard to aim.',
               'Heavy armour and hard shells take a quarter off a blow. A war hammer goes through and does a quarter '
               'more; a crossbow bolt goes through as well. An enemy hammer wears your armour fast.',
               'A crossbow shoots, then must be wound again: press [f] once more. The panel says loaded or unloaded.',
               'Throwing knives are thrown with [f]; walk over them to put them back in the set.',
               'A sling is cheap and its stones lie everywhere.',
               'A cestus or tiger claws go on your hands: with your weapon hand empty you fight unarmed with their '
               'damage. A cestus stuns on a critical hit; claws make a foe bleed, up to three times over. What has no '
               'blood does not bleed.']),
        ('h', 'Two weapons'),
        ('p', 'A light weapon, a dagger, short sword, scimitar or club, goes in the off-hand beside a one-handed '
              'weapon. One blow is then two: the second hand strikes for half, and its powers count for half. The '
              'price is the shield: no block and no shield skills.'),
        ('h', 'Rarity'),
        ('rar', rar),
        ('p', 'Magic is rare in Avarenthia, and the better it is the rarer. Uniques roll within a range; sets of 2 to 4 '
              'pieces give a bonus when worn together.'),
        ('h', 'Unknown and cursed'),
        ('p', 'Magic items are unidentified when you find them. Outfitters and priests name them for you. Some are '
              'cursed: once worn they stay on until a priest lifts the curse.'),
        ('h', 'Wear'),
        ('p', 'Gear wears with use and breaks when it is worn out. An outfitter mends it; a repair kit patches it up on '
              'the road.'),
        ('n', 'Only those who use gear drop it. A wolf carries no sword.'),
    ]


def ch_towns(g):
    return [
        ('p', 'Towns are where you rest, buy, sell and find work. Walk into a person to talk to them, or stand next to '
              'them and press [t]. Doors open when you walk into them.'),
        ('map', 'town'),
        ('h', 'Who does what'),
        ('r', [('Innkeeper', 'a bed for the night, a meal, jobs, and gossip'),
               ('Trader', 'buys and sells goods; prices differ from town to town'),
               ('Outfitter', 'weapons and armour; names magic items and mends worn gear'),
               ('Temple', 'heals, lifts curses, raises the fallen, for a fee'),
               ('Stablemaster', 'mules and carts, to carry more'),
               ('Castellan', 'in strongholds only: war jobs'),
               ('Factor', "of the Merchants' Guild: prices, and trade work"),
               ('Captain', 'of the watch: where the trouble is, and bounties')]),
        ('p', 'Smoke rises from the chimneys of the houses where a fire is lit, and by day sparks fly at the '
              "outfitter's anvil."),
        ('h', 'The week'),
        ('p', 'A week has seven days, from Moonsday to Restday. In human towns Starsday is market day: the square '
              'fills with people, and traders and outfitters pay a little more for what you sell. Restday is the rest '
              'day: the temple bell rings, the townsfolk sit in the temple in the morning, and the shops, stalls and '
              'stables stay shut all day. The inn and the temple stay open. The line under the map says when it is '
              'market day or rest day.'),
        ('h', 'Signs over people'),
        ('s', [([('!', SIGN_COL['!'])], 'has work for you'),
               ([('?', SIGN_COL['?'])], 'is waiting for a job you can hand in')]),
        ('h', 'Sizes'),
        ('p', 'Hamlet, village, town, city, metropolis. The bigger the place, the more it has: barracks with '
              'sellswords and a deep harbour are only found in the cities. Farms along the roads share a '
              'meal with travellers; roadside inns offer a bed and the news.'),
        ('h', 'Names'),
        ('p', 'A name tells you where a place lies: a -ford or -bridge stands on a river, a -haven or a Port on the '
              'coast, a -fell, a Bryn- or a Dun- in the hills, a -holt or a Coed- in the woods. In the north the names '
              'sound old and Norse, in the west they sound Celtic. Every people names its homes in its own way.'),
        ('h', 'Rivers in town'),
        ('p', 'A stream is crossed by a bridge. Where a lane meets a broad or wild river there is a ferry instead, the '
              'sign {▬|200,154,98} on its rope: walk into the raft or the ferryman, and for a few copper you are on '
              'the other bank. At night he is home and the raft is tied up. The main roads always cross on a bridge.'),
        ('h', 'Inns and beds'),
        ('p', 'A night in an inn bed and a hot meal leave you full and Well rested: you heal faster for a day. Sleeping '
              'out in the open is cheaper, but not safe.'),
        ('h', 'Peoples'),
        ('p', 'Humans, elves, dwarves, halflings, gnomes, half-orcs and goblins each like some peoples and distrust '
              'others.'),
        ('h', 'News'),
        ('p', 'News travels on foot, about twenty-five leagues a day. Innkeepers hear everything, a little late; the '
              'factor knows the prices; the captain knows the trouble; travellers and sailors bring word from far '
              'away. What you hear of a far place is old, and may no longer be true.'),
        ('h', 'Factions'),
        ('p', 'Different in every world. Work for one to win its favour; hurt it and its gates close to you. The '
              'Standing tab of the journal shows where you stand with each.'),
        ('n', "Jobs pay modestly. Trade is where the money is: buy where a good is common, sell where it is rare. The "
              "map's Trade layer [6] shows it."),
    ]


def ch_jobs(g):
    return [
        ('h', 'Jobs'),
        ('p', 'Innkeepers, village elders, the factor, the captain, the castellan, the temple, the guilds and '
              'travellers on the road all have work. A job goes in your journal [e]. Press '
              '[Enter] on it there to follow it: an arrow on the edge of the map points the way, and the job is marked '
              "on the map's Jobs layer [4]."),
        ('p', 'Some jobs ask you to choose. What you choose is remembered: by a town, a faction, your god, '
              'your guild, the law, and your hireling.'),
        ('p', 'A traveller who gives you a job waits for you afterwards at the inn of the town they were going to.'),
        ('h', 'Money'),
        ('p', '100 copper make a silver, 100 silver make a gold. Jobs pay modestly; trade is where the money is. Coin '
              'goes on beds, meals, repairs, wages and the temple. What you cannot afford is shown in grey.'),
        ('h', 'Trade'),
        ('p', 'Every town has goods it makes cheaply and goods it wants. Buy where a good is common, carry it, sell '
              'where it is rare. A mule or a cart from the stablemaster carries more. The map\'s Trade layer [6] shows '
              'what each town you know offers and wants. Prices change with the seasons.'),
    ]


def ch_land(g):
    return [
        ('h', 'Roads and danger'),
        ('p', 'Roads are patrolled and fairly safe. The further you stray from them, the worse it gets. The line under '
              'the map shows the danger where you stand, {■■□□□}; the Danger layer of the map [2] shows it everywhere '
              'you know.'),
        ('h', 'Knowing the land'),
        ('p', 'At first you only know where Thornfield lies. Signposts {┬}, townsfolk and travellers tell you where '
              'places lie, but the land itself you only learn by walking it.'),
        ('h', 'Kinds of country'),
        ('p', 'Each kind of country does one thing you notice: on the moor you see far, but the morning mist hides '
              'wolves; under old forest you see almost nothing, but the rare herbs grow there; in a canyon robbers '
              'wait; in the mangroves the going is slow; sinkholes in the karst drop into caves; an oasis has water and '
              'a caravan camp.'),
        ('h', 'Places on the way'),
        ('s', [([('Π', SIGN_COL['Π'])], 'ruin: an old ruin with a way down. Small, with a skill tome at the bottom.'),
               ([('†', SIGN_COL['†'])], 'shrine: pray for a blessing; an offering makes it last longer.'),
               ([('∆', SIGN_COL['∆'])], 'camp: a bandit camp. Kill them all and the strongbox is yours.'),
               ([('Ψ', SIGN_COL['Ψ'])], 'stones: standing stones. Touch them to learn from old memories.'),
               ([('¤', SIGN_COL['¤'])], 'wagon: an abandoned wagon. Loot, or a trap.')]),
        ('p', 'Battlefields, where armies fought, keep the dead and what they carried, for a while.'),
        ('h', 'Falls and springs'),
        ('s', [([('≡', (236, 248, 255))], 'falls: a waterfall, a cascade or great falls. Fish bite better in the pool, '
                                          'a hollow may hide behind the falling water, and from the cairn on top of a '
                                          'cascade or on the rim of great falls you see the land for miles.'),
               ([('≈', (226, 242, 255))], 'rapids: cross on the stepping stones. A slip sweeps you downstream.'),
               ([('°', (190, 240, 228))], 'hot spring: step into the water to heal, once a day; it keeps the cold off.'),
               ([('╫', (190, 160, 112))], 'causeway: a path of poles out to an islet, only at low tide.')]),
        ('p', 'In the deep of winter some falls freeze. Walk into the ice to climb it.'),
        ('h', 'Wonders'),
        ('p', 'Rarer places out of the old tales, each one at most once in a world, each with one thing to do.'),
        ('s', [([('▀', (176, 196, 150))], 'the Drifting Isles: rocks hanging over a vale. Climb the chain to the top of one.'),
               ([('*', (200, 210, 255))], 'the Starwater: a lake with stars in it by day. Its stair leads to its twin, far away.'),
               ([('↑', (226, 222, 150))], 'the Thunder Anvil: leave a weapon at the spike; a storm blesses it.'),
               ([('∩', (120, 214, 100))], 'the Hollow Hill: at full moon, by night, a door opens. They take no coin.'),
               ([('♣', (150, 240, 150))], 'the Unwintering: spring in the snow, and Everbloom, which grows nowhere else.'),
               ([('▲', (255, 170, 60))], 'the Undying Flame: walk into it with a weapon in your hand, and its edge will hold.'),
               ([('Ω', (150, 176, 210))], 'the Drowned Bell: dive at the end of the jetty, but only in a storm.'),
               ([('o', (200, 215, 255))], 'the Star Well: a silver coin and a wish, once a day. Not always the wish you meant.'),
               ([('Π', (206, 196, 176))], 'the Singing Stones: rest in the ring at dusk or by night and dream of a hidden place.'),
               ([('∙', (140, 230, 210))], 'the Wisp Fen: follow the blue lights at night, to treasure or into the mire.'),
               ([('░', (240, 214, 140))], 'the Singing Sands: walk where the hum is loudest; something lies buried there.'),
               ([('≈', (110, 200, 255))], 'the Glowing Bay: on summer nights the fish bite better.'),
               ([('o', (110, 222, 170))], 'the Green Well: climb down the rope and dive for old offerings.'),
               ([('♣', (178, 168, 146))], 'the Stone Wood: dig amber out of the grit, and now and then a fossil.')]),
        ('p', 'Now and then a star falls on an ordinary night, not only at the Starfall. Trolls caught in the sunlight '
              'turn to stone.'),
        ('h', 'On the road'),
        ('p', 'Things happen on the road: wounded travellers, peddlers, tolls, storms, a rival band of adventurers who '
              'sometimes get to a dungeon before you. Walk into a traveller to talk.'),
        ('h', 'The old ways'),
        ('p', 'Hidden paths of the old Varnish Empire: a faint, broken grey-green line on the map. You only see what '
              'you have found: walk on one, hear a rumour, read an old map or buy a chart, or look out from a '
              'watchtower. They are faster than open land and never patrolled. They lead over passes, to waystations '
              '{Σ}, a safe rest; milestones {╥}; sealed vaults {Φ}; forgotten graveyards; and into hidden valleys {•}.'),
        ('h', 'Their own lands'),
        ('l', ['Halflings keep a green country of hills and hedges.',
               'Elven glades {♠} hide deep in the woods, off the map until you are close enough to see their lanterns. '
               'An elder knows the next glade, and the way to the elven city under the Elder Tree.',
               'Dwarves live in deepholds cut into the mountains, with mines below, and in villages in the hills '
               'before them.',
               'Gnomes live in hamlets under the roots of great trees.']),
    ]


def season_rows():
    out = []
    for s in ('winter', 'spring', 'summer', 'autumn'):
        months = [CAL.MONTHS[i] for i in range(12) if CAL.SEASONS[i] == s]
        if s == 'winter':                      # the year turns in the middle of winter
            months = [CAL.MONTHS[11]] + months
        out.append([s.capitalize(), ', '.join(months)])
    return out


def ch_weather(g):
    start = CAL.short(1).split()
    return [
        ('h', 'Weather'),
        ('p', 'Each region has its own weather: the cold north and the mountains, the hot dry south, the marshes and '
              'the mild middle. It changes by steps: drizzle grows into rain before it pours.'),
        ('l', ['Rain, snow, mist and dust shorten your sight; thick fog and sandstorms a lot.',
               'Snow, storms and sand slow you down, and ambushes are likelier when you cannot see.',
               'Cold and scorching heat make you hungry sooner.',
               'Fire magic sputters in the wet and burns hotter in the heat; storm magic loves a storm.',
               'In a thunderstorm, open land is no place to be: lightning strikes.',
               'Under a roof you stay dry.',
               'Rain and snow send the townsfolk indoors: the streets empty and the inn fills.']),
        ('h', 'Omens'),
        ('p', 'Falling ash, a sickly miasma, smoke on the wind: a great evil is near.'),
        ('h', 'The year'),
        ('p', f'Twelve months of {CAL.DAYS_IN_MONTH} days, {len(CAL.WEEKDAYS)} days in a week, from '
              f'{CAL.WEEKDAYS[0]} to {CAL.WEEKDAYS[-1]}. Your story begins on the {CAL.ordinal(int(start[0]))} of '
              f'{start[1]}.'),
        ('t', ['Season', 'Months'], season_rows()),
        ('p', 'Each season lasts three months, 90 days. The date stands at the top of the panel.'),
        ('l', ['Winter: snow comes down from the north and the heights; lakes and rivers freeze, and the ice is a '
               'short cut until the thaw makes it thin. Passes fill with snow. Beasts leave tracks in the snow. Days '
               'are short.',
               'Spring: the dirt roads turn to mud, the fords run high, the flood meadows lie under water.',
               'Summer: small streams run dry late in the season and a fire can run through the dry grass. On '
               'Midsummer night fires burn on the hills.',
               'Autumn: the woods turn gold and red; berries and mushrooms wait to be picked.']),
    ]


def ch_travel(g):
    return [
        ('h', 'Walking the land'),
        ('p', 'The world map is for distance: one step there is a long stretch of country. [>] anywhere in open '
              'country takes you down into the land itself, a stretch of a few minutes across. Walk off its edge and '
              'you are in the next stretch; [<] brings you back up to the world map.'),
        ('p', 'Down there you see what the map only hints at: the river with its fords and bridges, the road, the '
              'fields round a village, the hill a dungeon mouth is cut into. Walk into a town, a site or a keep in '
              'the middle of its stretch and you are in; leave it by any edge and you come out on that side. Travellers '
              'and caravans on the road stand there too; bump them to talk.'),
        ('p', 'An ambush on the world map is fought down in the land where it falls on you. Win, and walk on. Or get '
              'away into the next stretch with no foe beside you, and they stay behind. Snow, ice and autumn leaves '
              'come and go there with the seasons, and what you leave lying stays where you left it.'),
        ('h', 'Travelling far'),
        ('p', 'On the map [m], [Tab] picks a place you have been to and shows the way; [Enter] sets out along the '
              'roads. Enemies, travellers, events, hunger, wounds or any key stop you on the way.'),
        ('h', 'Rivers'),
        ('p', 'Fords are where the road crosses. Ferrymen take you over for a few coppers, even when the fords run '
              'high.'),
        ('h', 'Sailing'),
        ('p', 'You cannot own a ship, but you can buy a passage from a skipper on the waterfront.'),
        ('l', ['A fishing boat takes you on short hops from any harbour.',
               'A coaster sails between villages and bigger places.',
               'A merchant ship sails only between the cities with a deep berth.']),
        ('p', 'Days pass on the voyage and your cargo comes along. In winter the boats stay in more often, and pack ice '
              'locks the northern harbours. Now and then pirates come alongside: fight them on deck, or hand over the '
              'cargo. Somewhere on the coast a pirate cove lies hidden.'),
    ]


def ch_camp(g):
    return [
        ('h', 'Hunger'),
        ('p', 'You burn food slowly. A full belly lasts about a week: after a day or two you are hungry, after four or '
              'so weak: you heal no more and hit softer. Then you faint, and only after six or seven days without a '
              'bite do you starve. [E] eats the food that fits your hunger best. Bread, rations, cheese, fish and meat '
              'all do; an inn serves a hot meal. Raw meat may upset your stomach; cooked, it never does.'),
        ('h', 'Resting'),
        ('p', '[R] rests until you are healed. In a town, rest in a bed. Out in the open you make camp: a fire keeps '
              'beasts off but draws robbers. A tent keeps you dry and safer, and a hireling keeps watch while you '
              'sleep.'),
    ]


def ch_hunt(g):
    return [
        ('h', 'Herds'),
        ('p', 'Game lives in every stretch of wild country, but you rarely see it. Where a herd passed you find hoof '
              'tracks, the sign {:}, that fade in a day or two. The herd itself, the sign {q}, shows only when you '
              'are a few steps away; further on open land and with more Hunting, less in the woods.'),
        ('p', 'A few great herds of reindeer, aurochs or wildebeest travel with the seasons: north and up to the high '
              'pastures in summer, south and down in winter. Wolves and gnolls follow them.'),
        ('p', 'Walk onto tracks and you may read them: how fresh, which animal, which way.'),
        ('h', 'The hunt'),
        ('p', 'Walk into a herd on the world map and you stand at the edge of its grazing ground. The leader, the '
              'sign {Q}, keeps watch. The wind is named in the log, and an arrow on the edge of the map shows where it '
              'comes from: keep it in your face, or they smell you. Trees and rocks hide you; the closer and the more '
              'open, the sooner they see you.'),
        ('p', 'Shoot with a bow, [Tab] to aim, or close in with a spear. A hit animal runs on a few steps, leaving '
              'blood, and falls. The rest of the herd flees. An aurochs bull or a boar may charge; an elk kicks. '
              'Hunting a herd sends it on, and the game there is thin for a while.'),
        ('n', 'Small game, hares and grouse, never shows on the world map. You meet it on the hunting ground, or '
              'snare it while you forage.'),
        ('h', 'Skinning'),
        ('p', 'Stand on a carcass and press [Enter]. With a knife or a dagger you get cuts of meat named by the animal, '
              'a hide, and sometimes antlers, horn or tusks; without one, only some raw meat. Beasts you fight can be '
              'skinned too: a wolf pelt, a bear fur, a crocodile hide. The better your Skinning, the fewer torn '
              'hides.'),
        ('h', 'Hides and leather'),
        ('o', ['A fresh hide rots in two days. Its name says how long it has left.',
               'Set up a stretching frame out in the land and walk into it with salt in your pack: an hour of '
               'scraping, and the hide is salted. A salted hide keeps.',
               'A tanner in a village or town tans it for a fee; come back for the leather three days later. Or rub '
               'oak bark into a salted hide and it tans in your pack in five days.',
               'Work the leather at a workbench in the tanner\'s shop: leather armour, gloves, boots, a belt, a '
               'waterskin. Better Leatherworking, sturdier work.']),
        ('p', 'Plain hides sell for little. Fine fur, fox, ermine, bear, fetches much more in the cities and the cold '
              'north.'),
        ('h', 'Cooking'),
        ('p', 'You know two dishes at the start: Roast Meat and Grilled Fish. Walk into a fire, a fire pit or an inn\'s '
              'hearth, or choose to cook when you make camp with [R]. You see the dishes you have everything for, '
              'and Try something new: put up to three things from your pack in the pot.'),
        ('l', ['The right things teach you the dish, and you will remember how.',
               'One thing short, and the cook in you says what it wants: something sharp, sweet, green.',
               'Nothing right gives Camp Mush. It fills a hole.']),
        ('p', 'Cooking never teaches recipes by itself. It burns fewer dishes, gives more portions and stronger '
              'effects, and at a high rank you taste what is in the inn\'s stew. Dishes warm you, heal, strengthen '
              'or keep you going; most go bad after some days, a few keep long.'),
        ('p', 'Now and then an innkeeper shares the dish of the house, and herders, hunters and fishers on the road '
              'tell you theirs. The peoples share their own kitchen only with friends. The finest dishes nobody '
              'teaches: you find them in the pot, or in a rare old cookbook.'),
        ('p', 'Every land has its own herbs, fruit and catch: foraging there finds them, and its village outfitter '
              'sells some. Salt, eggs, milk and butter come from the villages.'),
        ('p', 'Hang meat or fish on a drying rack overnight: Dried Meat and Smoked Fish keep, longer with salt.'),
    ]


def ch_company(g):
    return [
        ('h', 'Hirelings'),
        ('p', 'Sellswords sign on in the barracks of the cities, and now and then in an inn. They cost a fee to sign, a '
              'daily wage and their food. Unpaid or unfed, they grow sour, and in the end they walk. Five kinds: '
              'defender, warrior, archer, healer and mage. They carry four pieces of gear that wear like yours, and '
              'they grow with you.'),
        ('h', 'A beast'),
        ('p', 'Learn Tame from a Beastcraft tome and you can tame a beast: a wolf, a bear, a panther or a hawk, beside '
              'you and best when it is hurt. It takes no wage and wears no gear, but it eats meat every day. One '
              'beast at a time; a Packmaster of the Houndwardens\' Lodge keeps two.'),
        ('h', 'Orders'),
        ('p', '[h] opens your company. The keys [1] to [5] give an order to one of them or to all: follow, defend me, '
              'attack my target, hold position, stay out of it.'),
        ('h', 'Who gets hit'),
        ('p', 'Monsters choose whom they go for: who hurt them lately, who stands in their way, who looks soft. A beast '
              'goes for the nearest; a clever foe for the healer. A defender takes the blows meant for you. Badly hurt, '
              'a hireling may run, and come back when it is over.'),
    ]


def ch_guilds(g):
    return [
        ('p', 'You may fight for at most two combat guilds, and rivals will not have you both; the guilds of the '
              'crafts take anyone. Each guild has five ranks, earned with its own jobs. Members buy cheaper from the '
              'quartermaster, sleep in the hall for little or nothing, have their gear mended cheaper, and are paid '
              'better the higher they rise. Only a guild master teaches the advanced techniques, and only to those '
              'who have earned them. A technique goes on [6] as your elite; one of your own schools may also go on '
              '[3] to [5].'),
        ('p', 'Who serves two guilds may learn a technique of both. One that mixes weapon and spell costs stamina and '
              'mana alike; the Hollow Coven\'s techniques cost life as well.'),
        ('p', 'Standing with a guild fades slowly if you do nothing for it, but never below your rank.'),
        ('p', 'Some guilds hang out no sign. Listen for rumours, and watch for chalk marks on the walls.'),
    ]


def ch_gods(g):
    rows = [(f"{GODS.GODS[k]['name']}", f"{GODS.GODS[k]['title']}: {GODS.GODS[k]['domain']}.") for k in GODS.GOD_ORDER]
    return [
        ('gods', rows),
        ('h', 'Devotion'),
        ('p', 'At a temple you can swear yourself to its god. Pray there once a day, leave offerings and do what your '
              'god likes, and their favour grows. When you are favoured, and later chosen, they bless you, and prayer '
              'at their temples heals you.'),
        ('h', 'Rivals'),
        ('p', 'Solmara and Morrak, Valdric and Skell, Thessa and Durnak are old enemies. Factions that worship a rival '
              'of your god trust you less, and the priests of a rival temple will not tend to you. Choose with care, '
              'or choose no god at all.'),
    ]


def ch_realms(g):
    return [
        ('p', 'The human lands are an empire: an emperor in the great city, three to five kings under him, a baron in '
              'every region, and under each baron two or three lesser houses. Every lord has a name, an age, a nature '
              'and an heir; every house has arms, colours and a motto. Dwarves, elves and the orc tribes live outside '
              'the empire, each by their own law.'),
        ('h', 'The Realms layer'),
        ('p', 'Press [4] on the map. Each realm washes the land in its colour, with a bright edge where two realms '
              'meet and a faint one between baronies. {♦} is a king\'s seat, {·} a baron\'s. The borders follow the '
              'rivers and the ridges, and they move when a war is lost.'),
        ('h', 'Lords and their seats'),
        ('p', 'A baron or a king sits in the finest house of his town, or in the keep of his castle. A lesser house '
              'has a seat beside the village it holds: {╓} a fortified farm, {╥} a tower house, {╦} a walled manor. '
              'The seat of a fallen house stands empty, the sign {:}. The great cities also have rich merchant '
              'families. Walk into a lord to talk: work, the news of the court, fealty.'),
        ('h', 'What happens'),
        ('p', 'Every month each court has its small event. Lords die and their heirs quarrel, a child heir rules '
              'through a regent, barons rebel or claim a neighbour\'s land, marriages bind houses and murders break '
              'them. Wars start and they end: in peace, a barony changing hands, tribute or a hostage. Hosts march '
              'across the map between the seats. You hear of it late, through the news, and not always right.'),
        ('h', 'Your part'),
        ('p', 'You never rule and you hold no land. You are a piece in their game: carry letters, back a claimant, '
              'save or kill an heir, open a gate, guard a wedding, bring back a hostage. Lords pay modestly; treason '
              'pays well and makes enemies. A lord remembers the work you do for his realm.'),
        ('h', 'Knighthood'),
        ('p', 'With a good name in the empire and enough work done for one realm, a baron, a king or the emperor '
              'will take your oath. You become Sir or Dame, and people call you my lord or my lady. Your liege may '
              'call the levy: the call comes as a job in your journal. Stay away twice and your name is struck from '
              'the roll. You can renounce your oath in your liege\'s hall.'),
        ('h', 'The other powers'),
        ('l', ['The Church has a holy order with a keep, the sign {╪}. Its knights hunt necromancers and witches.',
               'Where raiders come from the north, the Border Watch holds its forts, the sign {╫}.',
               'A war brings mercenary companies, who camp near the front, the sign {¶}, and serve whoever pays.',
               'Heavy taxes and levies raise the villages, the sign {‼}: a free commune if they win, gallows if not.',
               'A lord who lost a crown may wait in exile for his moment, in a hidden camp, the sign {º}.',
               'Witches keep hidden circles on the moors and in the marshes, the sign {○}.']),
        ('h', 'Raiders'),
        ('p', 'Two or three raiding peoples live in every world, where their land fits them: sea raiders, highland '
              'and steppe clans, desert riders, ice raiders, pass clans, wreckers, canyon riders, the mist folk, '
              'island voyagers. Each has a hall, the sign {Æ}, where guest right keeps you safe. They raid in their '
              'own months, and a strong chief may take a barony. Village boards ask for help against them; their '
              'chiefs have their own work, some of it betrayal.'),
        ('h', 'The other peoples'),
        ('l', ['Each dwarf hold keeps a Grudge Book of wrongs, with a keeper beside the High Seat who reads it to '
               'you. A full book means a feud, until the debt is paid in gold or in blood.',
               'The elves defend their wood. When the woodcutters push the edge back too far they close it, and the '
               'wood grows dangerous for everyone.',
               'The orc tribes each have a name and a chief, and fight one another until one warlord unites them in '
               'a Gorvash and they march. Then half-orcs and goblins are watched in other peoples\' towns and pay '
               'more.']),
    ]


def ch_wild_peoples(g):
    return [
        ('p', 'Orcs, goblins, kobolds, gnolls and lizardfolk have homes of their own: a war camp behind a palisade, a '
              'goblin ravine, kobold caves, a gnoll hunting camp that moves with the game, a lizardfolk village on '
              'stilts. They are not dungeons full of monsters but places where people live.'),
        ('l', ['The guards warn a stranger off before they fight. Turn back and nothing happens.',
               'Go too far and the whole place rises against you.',
               'The young, the old and the workers run when there is trouble.',
               'Some will trade with those they trust. The kobolds love shiny things: a toll in gems buys a welcome.',
               'Captives are sometimes kept there, waiting for someone to free them.']),
    ]


def ch_death(g):
    return [
        ('p', 'Softcore: the priests raise you, for a fee from your purse. Your pack stays with your body, and you are '
              'weak for a day or two. No coin for the temple: your tale ends there.'),
        ('p', 'Hardcore: death is final. There is one save, and it is gone.'),
        ('p', 'When you fall, the death screen names the deeds you are remembered for.'),
        ('p', 'A fallen hireling: in Hardcore they are dead, their gear on their body. In Softcore a temple raises them '
              'for a fee. When you fall, they fall with you.'),
    ]


def ch_chronicle(g):
    return [
        ('p', 'The handbook says how the world works. The chronicle says what your hero knows of this world: open the '
              'journal [e], go to the Lore tab, pick a chapter and press [Enter].'),
        ('h', 'Where it comes from'),
        ('s', [([('·', (217, 165, 71))], 'heard: from someone, somewhere; it may be wrong or old'),
               ([('≡', SIGN_COL['≡'])], 'read: in a book or on a stone'),
               ([('☼', (255, 226, 120))], 'seen: you were there')]),
        ('p', 'Under each line stands who told it, where and on which day. When you later see or read better, a red '
              'line under an old rumour says so. A dot marks what you have not read yet.'),
        ('h', 'Stones and old books'),
        ('p', 'Inscribed stones, the sign {Θ}, stand in some ruins: walk into one to read it. Some are cut in Varnish '
              'letters you cannot read until a scribe has taught you them, and those name the old roads. A few old '
              'books lie in the deepest dungeons: read one from your bag, and it may name a place you did not know.'),
        ('h', 'Libraries'),
        ('p', 'Every city has a library, with shelves of books and a scribe. Walk into the scribe and choose: The old '
              'days, The realms, A lord or house, This city, Beasts you have met, or the Varnish letters. A subject costs a few silver and '
              'a few hours, the letters a day; members of the Circle of Magi read for free. A library is true but '
              'slow: its own realm it knows well, far realms late. It also buys the old books you find.'),
        ('p', 'The dwarves keep their Grudge Book, and under the Elder Tree a loremaster sings of the old days.'),
        ('h', 'Two hundred years'),
        ('p', 'The old folk tell of the founding of the empire, its wars and the houses that fell, where it happened '
              'near them. Some of them have it wrong; what you read later puts it right. A record may name the ruin '
              'where a fallen house had its seat, and it goes on your map. Walk past an old battlefield and you find '
              'the bones still in the grass.'),
        ('h', 'Your deeds'),
        ('p', 'The named enemies you bring down and the evils you destroy are kept under Your deeds, and remembered '
              'when you fall.'),
        ('p', 'The dishes you know, and what goes in them, are under The kitchen.'),
        ('n', '[Enter] on a page of the chronicle shows its place on the map, if it has one.'),
    ]


def ch_signs(g):
    from . import guide as GD
    rows = []
    for glyphs, name in GD.signs(g):
        rows.append((glyphs, name))
    return [
        ('p', 'Every sign you have met so far, and what it means. The list grows as you travel; press [o] in the game '
              'to ask about a sign in front of you.'),
        ('signs', rows),
    ]


BASIC_KEYS = [
    ('[arrows] [numpad]', 'move; with [Shift]: run'),
    ('[.] [5]', 'wait a turn'),
    ('[Enter] [Space]', 'do the obvious thing here'),
    ('[Esc]', 'let go of the target; else the menu'),
    ('[Tab] [Shift+Tab]', 'next, previous target'),
    ('[1-6]', 'use a skill: 1 and 2 your weapon, 3 to 6 your choice'),
    ('[q] [w]', 'health potion, mana potion'),
    ('[>] [<]', 'go in, down or into the land; climb up'),
]


def menu_keys():
    """Every key of the menu, so the book never misses one."""
    from . import ui
    out = []
    for _g, items in ui.MenuScreen.GROUPS:
        for k, name, desc in items:
            if k in ('quit', 'travel'):
                continue
            out.append((f'[{k}]', f'{name.lower() if name != "Help" else "this handbook"}: {desc}'))
    return out


def ch_keys(g):
    rows = BASIC_KEYS + menu_keys() + [('[F11] [Alt+Enter]', 'fullscreen')]
    return [('keys', rows), ('p', 'A capital letter means: with [Shift].')]


CHAPTERS = [
    ('First steps', ch_first_steps), ('Moving and looking', ch_moving), ('Fighting', ch_fighting),
    ('Your hero', ch_hero), ('Who you become', ch_who), ('Gear', ch_gear), ('Towns and people', ch_towns), ('Jobs and money', ch_jobs),
    ('The land', ch_land), ('Weather and seasons', ch_weather), ('Travel and sailing', ch_travel),
    ('Camp, food and rest', ch_camp), ('Hunting and cooking', ch_hunt), ('Your company', ch_company),
    ('Guilds', ch_guilds), ('Gods', ch_gods), ('Realms and lords', ch_realms),
    ('Wild peoples', ch_wild_peoples), ('Death', ch_death), ('The chronicle', ch_chronicle), ('Signs', ch_signs),
    ('All the keys', ch_keys),
]
NAMES = [n for n, _f in CHAPTERS]


def blocks(g, i):
    return CHAPTERS[i][1](g)


def sections(g, i):
    return [b[1] for b in blocks(g, i) if b[0] == 'h']


def opening(g):
    """The page that fits where you are, and why: (chapter, words)."""
    m = g.map
    if g.turn < D.DAY_LEN // 2 and not g.__dict__.get('book_read'):
        return 0, 'a new hero'
    if getattr(m, 'hunt', None) is not None and all(getattr(o, 'prey', None) is not None for o in g.visible_hostiles()):
        return NAMES.index('Hunting and cooking'), 'you are on the hunt'
    if g.visible_hostiles() and m.kind != 'town':
        return NAMES.index('Fighting'), 'you are in a fight'
    if getattr(m, 'deck', False):
        return NAMES.index('Travel and sailing'), 'you are at sea'
    if m.kind == 'town':
        return NAMES.index('Towns and people'), f'you are in {m.name}'
    return None, ''
