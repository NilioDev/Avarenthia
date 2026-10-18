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

KEY_RE = r'(\[[^\]]+\]|\{[^}]+\})'

# the colours of the signs the text names, as the map draws them
SIGN_COL = {
    '@': (255, 246, 220), '≡': (196, 170, 255), 'C': (170, 150, 130), '┬': (208, 160, 96), 'Π': (176, 166, 150),
    '†': (150, 210, 255), '∆': (232, 92, 72), 'Ψ': (196, 126, 255), '¤': (204, 164, 104), 'Σ': (200, 196, 170),
    '╥': (150, 160, 130), 'Φ': (150, 200, 190), '•': (190, 220, 160), '♠': (120, 200, 120), '■': (217, 165, 71),
    '□': (58, 46, 34), '!': (255, 214, 40), '?': (134, 196, 111), '⌂': (242, 196, 74), '>': (232, 96, 62),
    '≈': (70, 130, 200), '♣': (47, 128, 64), '▲': (163, 156, 142), '∩': (154, 138, 90), '·': (200, 164, 106),
    '%': (180, 60, 50), '¡': (236, 176, 84), '¥': (206, 206, 216), '○': (106, 162, 216), '☼': (255, 140, 50),
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
        ('p', 'The map on the left. The panel on the right: your life and mana, your money, and IN SIGHT, the '
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
              'to [5] show it in layers: Land, Danger, Factions, Jobs and Trade; [L] goes through them in turn. '
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
        ('k', '[1-6]', 'use a skill from your bar, at your target or else the nearest enemy. You start with none: '
                       'skills come from tomes, the sign {≡}.'),
        ('k', '[q] [w]', 'drink a health or a mana potion. It takes a turn.'),
        ('k', '[f]', 'shoot with a bow at your target.'),
        ('h', 'IN SIGHT'),
        ('p', 'The panel lists every enemy you can see, with a bar for its life and what it is doing: closing in, '
              'fleeing, stunned, unaware of you.'),
        ('h', 'Running away'),
        ('p', 'Wolves are fast; bandits are not. Walk off the edge of the field to get away, or onto a road: the '
              'patrols are there.'),
        ('h', 'Elements'),
        ('p', 'Fire, cold, lightning and poison. Monsters resist some and fear others; fight a kind to learn which. '
              'Your gear can give you resistance to each, up to 75%.'),
        ('h', 'Night'),
        ('p', 'Night brings the dead and bigger packs.'),
        ('n', 'Every kill teaches you about its kind. Know a kind well and you hit it harder, and it hits you less '
              'often. The bestiary [v] shows what you know.'),
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
        ('l', ['Strength: harder blows in melee, and the heavy gear asks for it.',
               'Dexterity: aim, defence and bows; the light gear asks for it.',
               'Vitality: more life.',
               'Energy: more mana, and stronger spells.']),
        ('h', 'Skills'),
        ('p', 'You start with none. Learn them from tomes, the sign {≡}, found on monsters, in ruins and at standing '
              'stones, or bought from peddlers and city outfitters. Disciplines grow as you use them, and decide which '
              'tomes you can understand. You carry six skills on your bar; change them in a town with [z].'),
        ('h', 'Life skills'),
        ('p', 'They grow by doing; [C] shows them all.'),
        ('l', ['Fishing: by water, with a pole: [a]. Strike when the float plunges, then keep the fish in the green '
               'while the line holds.',
               'Foraging: search the wild for food and herbs: [F].',
               'Herbalism: picking herbs and knowing them.',
               'Alchemy and brewing: potions, ale, wine and mead: [P].',
               'Mining: walk into an ore vein with a pick to dig it.']),
    ]


def ch_gear(g):
    rar = ' · '.join(f'{k}' for k in ('normal', 'magic', 'rare', 'unique'))
    return [
        ('h', 'Slots and grades'),
        ('p', 'Ten slots. Normal, exceptional and elite grades; some gear needs Strength or Dexterity. A two-handed '
              'weapon takes the off-hand as well.'),
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
        ('h', 'Signs over people'),
        ('s', [([('!', SIGN_COL['!'])], 'has work for you'),
               ([('?', SIGN_COL['?'])], 'is waiting for a job you can hand in')]),
        ('h', 'Sizes'),
        ('p', 'Hamlet, village, town, city, metropolis. The bigger the place, the more it has: barracks with '
              'sellswords and a deep harbour are only found in the cities. Farms along the roads share a '
              'meal with travellers; roadside inns offer a bed and the news.'),
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
              "map's Trade layer [5] shows it."),
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
              'where it is rare. A mule or a cart from the stablemaster carries more. The map\'s Trade layer [5] shows '
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
               'Under a roof you stay dry.']),
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
              'all do; an inn serves a hot meal.'),
        ('h', 'Resting'),
        ('p', '[R] rests until you are healed. In a town, rest in a bed. Out in the open you make camp: a fire keeps '
              'beasts off but draws robbers. A tent keeps you dry and safer, and a hireling keeps watch while you '
              'sleep.'),
    ]


def ch_company(g):
    return [
        ('h', 'Hirelings'),
        ('p', 'Sellswords sign on in the barracks of the cities, and now and then in an inn. They cost a fee to sign, a '
              'daily wage and their food. Unpaid or unfed, they grow sour, and in the end they walk. Five kinds: '
              'defender, warrior, archer, healer and mage. They carry four pieces of gear that wear like yours, and '
              'they grow with you.'),
        ('h', 'A beast'),
        ('p', 'A beastmaster of the Houndwardens\' Lodge can tame a beast: a wolf, a bear, a panther or a hawk. It '
              'takes no wage and wears no gear, but it eats meat every day.'),
        ('h', 'Orders'),
        ('p', '[h] opens your company. The keys [1] to [5] give an order to one of them or to both: follow, defend me, '
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
              'who have earned them.'),
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
        ('p', 'The human lands are an empire: an emperor in the great city, kings under him, a baron in every '
              'region, and under each baron a few lesser houses with a seat of their own. Every lord has a name, an '
              'age, a nature and an heir. Dwarves, elves and the orc tribes live outside the empire, each by their own '
              'law. The Realms layer of the map [4] shows the realms as they are now.'),
        ('h', 'What happens'),
        ('p', 'Lords die and their heirs quarrel, barons rebel, marriages bind houses and murders break them. Wars '
              'start, and they end: in peace, a region changing hands, tribute or a hostage. You hear of it late, '
              'through the news.'),
        ('h', 'Your part'),
        ('p', 'You never rule and you hold no land. You are a piece in their game: carry letters, back a claimant, '
              'save or kill an heir, guard a wedding. The lesser houses give most of the small work. Lords pay '
              'little; treason pays well and makes enemies.'),
        ('h', 'The other peoples'),
        ('l', ['Each dwarf hold keeps a grudge book of wrongs. A full book means a feud that ends only when the debt '
               'is paid, in gold or in blood.',
               'The elves defend their wood. Logging pushes the forest edge back, and if it goes too far they close '
               'the wood.',
               'The orc tribes fight one another, until one warlord grows strong enough to unite them in the Gorvash, '
               'all spears, and march.']),
        ('h', 'Raiders'),
        ('p', 'Two or three raiding peoples live in every world, where their land is big enough: sea raiders from the '
              'fjords, barbarians of the hills and steppe, desert riders, ice raiders, pass clans, wreckers, canyon '
              'riders, the mist folk, island voyagers. They raid and trade, keep guest right under their own roof, and '
              'a strong leader may take a barony.'),
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
        ('h', 'Your deeds'),
        ('p', 'The named enemies you bring down and the evils you destroy are kept under Your deeds, and remembered '
              'when you fall.'),
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
    ('[1-6]', 'use a skill'),
    ('[q] [w]', 'health potion, mana potion'),
    ('[>] [<]', 'go in or down; climb up'),
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
    ('Your hero', ch_hero), ('Gear', ch_gear), ('Towns and people', ch_towns), ('Jobs and money', ch_jobs),
    ('The land', ch_land), ('Weather and seasons', ch_weather), ('Travel and sailing', ch_travel),
    ('Camp, food and rest', ch_camp), ('Your company', ch_company), ('Guilds', ch_guilds), ('Gods', ch_gods),
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
    if g.visible_hostiles() and m.kind != 'town':
        return NAMES.index('Fighting'), 'you are in a fight'
    if getattr(m, 'deck', False):
        return NAMES.index('Travel and sailing'), 'you are at sea'
    if m.kind == 'town':
        return NAMES.index('Towns and people'), f'you are in {m.name}'
    return None, ''
