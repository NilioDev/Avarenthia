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
    '░': (200, 204, 216), '#': (138, 154, 74),
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
              'to [7] show it in layers: Land, Danger, Factions, Realms, Jobs, Trade and Shadow; [L] goes through them in '
              'turn. '
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
              'fleeing, stunned, unaware of you. A boss stands at the top with a wide bar, marked where it will '
              'change; beside its name its phase, I to III, and under the bar what it does: charging a blow, spent, '
              'staggered, warded.'),
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
        ('h', 'Bosses'),
        ('p', 'The great foes fight in their own way. Before a great blow they wind up, and the ground it will strike '
              'turns red; a number on it counts the turns left. Step out in time: there is always a way. A purple '
              'number means the blow can be broken: hit it with a stunning or silencing skill, or hard enough while it '
              'winds up, and the blow is gone. Small blows come without warning, as always.'),
        ('p', 'A boss fights in a rhythm. Learn it: a snare or a wall of bone often comes before something worse. But '
              'it is never quite the same twice, and a look at it only tells you how it stands.'),
        ('p', 'At two thirds and at one third of its strength a boss changes: new moves, new helpers, and often the '
              'room itself changes round you. Your blows stop at that edge, unless a critical hit lands while it is '
              'spent or staggered: then the blow tears through, and the change never comes. After its heaviest blow '
              'it stands spent for a moment, and your blows land harder. Breaking its blows and striking its weakness '
              'fill three dots beside its name; when all three are full, it staggers. Its will shrugs off the first '
              'two stuns and holds, the two {♦}; after that they work, but shorter.'),
        ('p', 'Helpers come with a job, written beside them in IN SIGHT: a warder halves what the boss takes while it '
              'lives, a mender heals it, a channeler feeds its next great blow. Choose who falls first. Its great '
              'blows strike its own helpers too.'),
        ('p', 'An end boss waits behind a veil of mist, the sign {░}. Once you step through, the room shuts at the '
              'first blow: no rest inside and no portal, and one hard way out, a rotten wall, the sign {#}, that gives '
              'after five blows. A boss you flee from heals, and is ready for you next time.'),
        ('p', 'Gold ground is the other way round: stand in it. When a blow will fill the whole room, the cells by '
              'its stones of light, the sign {☼}, or up on a ledge or beside a chain in the wall, the sign {§}, stay '
              'safe, and they show gold.'),
        ('p', 'Your company plays it as you do: they step out of the red, better as they rank up, and a defender '
              'smashes his shield into a boss that winds up. Each of them beside you gives the boss one more small '
              'blow.'),
        ('p', 'Every boss has its own room and its own tricks. The Rat King\'s rats come out of holes in the walls: '
              'walk into a hole to stop it up. Grolm kicks out the props that hold up his roof, and no stone falls '
              'beside a prop that still stands. The Drowned King\'s water rises with every change; break the chains '
              'in the wall, two blows each, and it sinks. The Brood Mother\'s eggs hatch unless you tread on them, '
              'and her webs on the floor hold you fast.'),
        ('p', 'Some bosses take a stance: a shield of light that takes three blows, a wall of shields that only a '
              'flail or a war hammer gets past, a ward that eats your next spell, flames that burn whoever strikes '
              'them. Wait it out, or find what breaks it. Some throw images of themselves: one blow and an image '
              'is gone.'),
        ('p', 'Not every boss waits at the bottom. Some walk a level with their band: you hear them now and then, '
              'from where they are, and their tracks lie in the dust. Once one hunts you it follows you up or down '
              'the stair, and it does not heal while it hunts.'),
        ('p', 'When a great boss falls, three of its things lie there: a weapon, a piece of armour and a jewel. Take '
              'one; the other two break as you lift it.'),
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
               'Alchemy and brewing: draughts and oils from herbs, and drinks: [P].',
               'Mining: walk into an ore vein with a pick to dig it.',
               'Smithing: walk into an anvil.',
               'Hunting: reading tracks and stalking herds.',
               'Skinning: [Enter] on a carcass, with a knife or a dagger.',
               'Cooking: walk into a fire or a hearth.',
               'Leatherworking and Tailoring: walk into a workbench.',
               'Archaeology: walk into a dig spot at an old place, with a trowel.']),
        ('p', 'The chapter Crafts tells how they grow and what they make.'),
    ]


def ch_who(g):
    from . import classes as CL
    from . import trees as TT
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
        ('p', 'Every name, pure or of two, has a rule of its own: a Pyromancer\'s fire burns longer, a Paladin\'s '
              'War Cry heals the company. The page of your tree shows yours.'),
        ('h', 'Cunning and Arcane'),
        ('p', 'Two classes owe nothing to gods or the land. Cunning is the craft of the dark and the knife: Sneak, '
              'Envenom, Garrote, Smoke Bomb, Shadowstep and Vanish, snares, the sign {^|200,170,120}, and caltrops, '
              'the sign {÷|180,180,180}. Smoke, the sign {▒|154,154,154}, hides what stands in it. A foe that does not '
              'see you coming, asleep, blinded or unaware, takes your first blow twice over; a Rogue\'s, three '
              'times. Who sneaks is seen far less often. Venom saps a foe\'s strength, and who steps out of the shadows '
              'is hard to hit for a moment.'),
        ('p', 'Arcane is the old learned magic: Arcane Bolt, Blink, Slow, Dispel, Counterspell and Stop Time, runes, '
              'the sign {Φ|190,150,255}, that wait on the ground for a foe, and gates, the sign {Ω|120,160,255}: step '
              'into one and come out of the other. Dispel takes a spell off the ground or the magic off a foe; '
              'Counterspell lets the next spell cast at you come to nothing.'),
        ('h', 'Your tree'),
        ('p', f'Each class has a tree of three branches, six knots in each. Every {TT.EVERY} ranks in a school give '
              'you one point for its tree. A knot opens once the one above it has a point; some take two or three, '
              'and the last of each branch, the sign {☼|255,214,90}, is the strongest. They change how your skills '
              'work, and never add one to your bar, but for the shapes of Nature. You cannot have everything.'),
        ('p', 'Points are spent only where you rested, an inn\'s bed or your camp, before you walk on: open the skills '
              'with [z], then [Tab]. A temple takes all your points back, for coin, and you may spend them anew.'),
        ('p', 'Every school of magic has one branch for your weapon. Its first knot is the imbue: cast a spell of '
              'the school, and your weapon carries it for ten turns, about one blow in three: Flameblade burns, '
              'Rimeblade slows, Stormblade throws sparks, Dawnblade heals you, Duskblade steals life, Graveblade raises '
              'the slain, Thornblade roots, and with Hunter\'s Call your beast leaps in. While it lasts, no mana comes '
              'back.'),
        ('p', 'The Shapeshifter branch of Nature teaches Wolf Shape, Bear Shape and Hawk Shape. In a beast\'s shape '
              '[1] and [2] are its teeth and claws, and [3] to [6] rest unless you are Untamed; the key of the shape '
              'lets it go.'),
        ('h', 'The bar'),
        ('p', 'Six keys in three groups. [1] and [2] are your weapon\'s own two skills: they change when you take up '
              'another kind of weapon, and the second opens at rank 10 in its discipline. [3] to [5] are three skills '
              'of your classes. [6] is your elite, the sign {☼|255,214,90}: one technique a guild master taught you, '
              'or an epic in its place. '
              'A technique of a weapon guild that fits the weapon in your hand may take the place of [1] or [2] '
              'instead. Choose them in a town with [z]. The panel shows the three groups, with your name beside SKILLS.'),
        ('h', 'Epics'),
        ('p', 'Above the elites stand the epics, two for each class. An epic goes on [6] in the elite\'s place, the '
              'sign {♦|255,214,90}, and costs no mana or stamina: it works once, then waits until you rest, an inn\'s '
              'bed or your camp. The panel says whether it is ready or spent.'),
        ('p', 'Epics are taught by teachers who live alone, far from the roads: an ash hermit in a burnt valley, a '
              'rime witch at a mountain pass, an old master thief outside a city. Every class has two in the world, '
              'each in another part of it, in a hut, the sign {î|232,200,120}. From rank 35 in a class you may hear '
              'of one of its teachers, and the hut is on your map. From rank 40 the teacher sets you a deed, a job '
              'in your jobs tab. Do it, and you may learn one of the two epics; later the teacher will trade it for '
              'the other. Teachers grow old and die. When both of a class are gone, after a season a pupil takes up '
              'the work somewhere else.'),
        ('p', 'Phoenix is the one that waits. While it is ready on [6], a blow that would kill you burns you up '
              'instead, and you rise with a fifth of your life. Four flames cling to you after and bite every turn; '
              'water or a Health Potion puts one out. Once a day.'),
        ('p', 'Under Time Stop only you move, for three turns, and the world goes grey. You cannot harm anyone in '
              'it: walk, drink, heal or guard yourself, lay runes and snares.'),
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
               ('Temple', 'heals, lifts curses, raises the fallen, takes back tree points, for a fee'),
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
        ('p', 'A market fills up as you sell to it, and empties as you buy: the dearer the good, the faster. Ten gems '
              'move the price more than ten sacks of grain, and a small town has only a few to sell. What you bought '
              'out comes back slowly, over weeks. A market also remembers you: sell the same good in the same town '
              'again and again, and it pays less each time, until it forgets. Trade pays well, but never for '
              'ever on one road.'),
    ]


def ch_dungeons(g):
    return [
        ('h', 'Rooms of every shape'),
        ('p', 'A dungeon level is rooms of many shapes, round, cross-shaped, pillared, a room inside a room, joined by '
              'main ways three wide and narrow ways one wide, where a horde must come at you one by one. Most '
              'levels are big; a kobold den is smaller. The first time you step into a room, the log says what it is.'),
        ('p', 'The rock beyond the walls shows faintly round what you have seen: grey stone, brown earth, or dark '
              'basalt deep down, and in a mine now and then a glint of ore.'),
        ('h', 'Theme rooms'),
        ('p', 'Two or three rooms on a level hold one telling thing: an altar to pray at, shelves to search, a '
              'fountain, an anvil, a well, a gong, a mirror, a lever, a dice table. Walk into it to use it; a thing '
              'you can stand on, such as a summoning circle, the sign {·|224,72,72}, works when you step on it. Most '
              'give only once, and some are better left alone.'),
        ('p', 'Some rooms keep their find: a vault behind a locked door, the sign {+|224,176,64}, whose key lies '
              'elsewhere on the level, often with a guard; a hidden door, which you notice as you pass; three '
              'plinths, the sign {º|200,192,176}, where you may take one thing and the rest sink away. Among warding '
              'signs, {∞|240,224,160}, nothing of the dark comes in, and you may rest there once.'),
        ('h', 'Who made it'),
        ('p', 'Caves, nests and dens are shaped by whoever made them. Water grinds long halls along a stream; ants hang '
              'their chambers on tunnels like grapes; spiders fill whole halls with web; gnolls scrape round dens; '
              'goblins dig narrow ways braced with props, with a watch and an alarm gong by the way in; the dead lie '
              'in galleries of niches. Each room has its use, and the folk stand where they belong: a watch by the way '
              'in, sleepers in the dens, the leader at the bottom.'),
        ('p', 'Kill a goblin watch before it strikes the gong, or the whole hole wakes. Tripwires rattle tins and wake '
              'the nearest den; a covered pit drops you to the level below. Smash a nest\'s eggs and the nest comes '
              'for you. Push the slab off a sealed tomb for what was buried with the dead.'),
        ('h', 'Rivers underground'),
        ('p', 'A river of water or of fire may run through a level, in at one edge and out at another. Cross it by a '
              'bridge, {=|176,128,80}, a ford, or a crust of cooled rock, {▒|110,90,78}: each is a choke point.'),
        ('p', 'You can swim the water, slowly. Heavy armour or a heavy pack pulls you under: you are asked first, and '
              'every stroke then hurts. Most creatures stay on the bank, but some swim after you.'),
        ('p', 'The river of fire, {≈|255,138,40}, burns badly, and you are asked before you step in. Shove a foe into '
              'it and it burns; shove one over the edge of a chasm and it falls to the level below.'),
        ('h', 'The Ashen Deep'),
        ('p', 'Now and then a rift tears open in the world: a red glow on the map, and the land round it burning slowly '
              'to ash. At night fiends come out of it and raid the villages near it; you hear of it in the inns. '
              'Sometimes the bottom of a very deep dungeon breaks through into it instead, a crack going down.'),
        ('p', 'Below lie three to five levels of black basalt and ash, lit by the fire itself. A river of fire runs '
              'through each, crossed by bridges of chains, {≡|154,150,160}. Brimstone vents, {°|232,208,80}, puff choking '
              'smoke every few turns. On the fields of bones, {,|216,204,176}, the dead rise when you step in. The '
              'taken hang in cages, {╫|160,150,140}: break one open to free them, before the gaoler reaches the gong. '
              'Nobody can rest down there.'),
        ('p', 'At the bottom, in a hall of black iron, the Lord of Cinders keeps court before the burning gate, '
              '{Ω|255,112,48}. While its fire bowls, {☼|255,160,64}, burn, the gate heals it: tip them over first. '
              'Break the gate and the rift closes, and the land heals, slowly.'),
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
        ('h', 'Temples and towers'),
        ('p', 'Every people builds its own temple, the sign {π|240,230,200}, and its own tower, the sign {¡|240,230,200}, '
              'drawn in that people\'s colour; the dead of old lie in barrows, the sign {∩|240,230,200}. Each stands '
              'on its own stretch of land: you walk in from the edge, and stairs lead up or down from there.'),
        ('p', 'How far in you may go depends on your name with that people. A friend walks everywhere; a stranger may '
              'see the open parts, and a warden stops you at the rest. Push past and it is a crime. The temples and '
              'towers of the hostile peoples you fight your way through.'),
        ('p', 'Below every temple lies its own deep place, older and rougher the deeper you go. Some temples were '
              'built over something older still. A tale may tell you which: then a loose flagstone at the very bottom '
              'lifts for you.'),
        ('p', 'From the top of a tower you mark the land round about on your map: the higher the tower, the further, '
              'and further still on a hill. Fog and rain halve it; by night you see only lights. Up there the land '
              'lies faded far below, and the tower throws its shadow across it.'),
        ('p', 'A fallen tower has broken floors with open edges. Stepping off asks you first and says how far down it '
              'is; a fall hurts by the number of floors. A foe that knocks you back can throw you over, and your own '
              'shove sends a foe the same way.'),
        ('p', 'In the burial chamber of a barrow lies the bier, heaped with grave goods. Walk into it to take from it, '
              'and whoever lies there wakes, with the whole barrow.'),
        ('h', 'Abbeys, forts, manors'),
        ('p', 'Every people also has its abbey, the sign {Θ|240,230,200}, where its devout live and keep their lore; '
              'its fort, the sign {╩|240,230,200}, built to hold the ground; and the manors of those who matter, the '
              'sign {Å|240,230,200}. Each is built the way of its people, and the same rule of names holds: a friend '
              'goes everywhere, a stranger only so far.'),
        ('p', 'Each has its telling things. Shelves and rune stones keep a page of the past; a still pool or a lens '
              'shows you a far place; a map in a goblin warren marks a way down; at a halfling long table a friend is '
              'fed once a day; letters on a desk give you a lead; a portrait or a seat says who lives there. Walk into '
              'them.'),
        ('p', 'A fort may be taken by bandits, left empty, or fallen to a ruin. Seen by its foes, a keep drops its '
              'portcullis; look for the postern. Lizardfolk pull in their plank walkway and you wade, the kobolds\' '
              'way in is trapped every few steps, the gnomes\' hill hides its door, and the elves\' gate of woven '
              'branches opens only for their friends.'),
        ('h', 'Old places'),
        ('p', 'The land remembers its history. What the records tell of, you can walk up to.'),
        ('s', [([('×', (176, 132, 104))], 'old battlefield: grassy mounds over the dead, and a cairn that names the '
                                          'battle and its day. Dig a mound for rust, an old coin, now and then a blade '
                                          'that kept. On the night of the battle, the dead walk their field.'),
               ([('⌂', (146, 140, 130))], 'deserted village, emptied by plague, war or a dragon. Bandits, a hermit or '
                                          'a ghost may live there now.'),
               ([('╧', (168, 160, 144))], 'broken bridge of the old Empire: piers in the river, a ford beside it. '
                                          'From it you can make out where an old way ran on.'),
               ([('┴', (204, 198, 180))], 'stone of names by the road, for the fallen of a battle.'),
               ([('ß', (176, 172, 160))], 'a fallen statue of the first emperor, its head in the grass.'),
               ([('Γ', (160, 118, 82))], 'gallows hill where roads meet. The Watch nails up who it hanged, and who '
                                         'it wants.'),
               ([('□', (186, 176, 156))], 'old quarry: half-cut blocks, a giant never finished. Split a block, '
                                          'and once in a while a stone shell is inside.'),
               ([('▬', (170, 128, 88))], 'shipwreck: walk out to it at low tide and search the sea chest, once. '
                                         'Often the wreckers came first.'),
               ([('╓', (196, 180, 140))], 'hermitage: a hermit who knows the country tells you of a place now '
                                          'and then.'),
               ([('±', (190, 196, 156))], 'leper colony outside a city. Leave food at the gate; the temple sends '
                                          'bread there, and pays who carries it.')]),
        ('p', 'Small marks show whose land it was. Dwarves set boundary stones, the sign {┬|214,176,110}, round their '
              'holds. Moonstones, the sign {·|214,226,255}, each show the next, on toward a hidden elven place. Orcs '
              'hang skull poles, the sign {ⁿ|220,210,186}, near their camps, and kobold scratches, the sign '
              '{«|204,182,110}, point at a hoard of shiny things, the sign {*|236,210,120}. Walk onto them.'),
        ('h', 'The Varnish'),
        ('p', 'The empire before the Ruin built in iron and to the stars, and measured everything in leagues. Its '
              'ruins are on no map. You find a city by walking its land: columns between the trees, old paving under '
              'the moss or the sand, a gate of star-iron with no wall, stones with letters that say its name. Once '
              'you have seen it, it is on your map.'),
        ('s', [([('╩', (176, 190, 224))], 'a Varnish city, round its Sky Court and the round sky well. Somewhere in the '
                                          'court lies a way down that no map shows: a stone that tells you where to '
                                          'press, a well that draws air, a flagstone that sounds hollow, a lever '
                                          'behind a statue. Below waits a deep with a guardian of its own.'),
               ([('▐', (168, 176, 196))], 'a tower of the Northern Wall, where the nine legions watched the north. '
                                          'The wall runs on between the towers.'),
               ([('⌠', (176, 200, 220))], 'a wind tower: from the top you see the land round. It howls in a storm.'),
               ([('Ö', (196, 188, 168))], 'a road of the standing dead. Break a seal, and the dead one steps down.'),
               ([('◘', (150, 170, 220))], 'a star-iron forge; a smith needs a shard of star-iron to mend Varnish work.'),
               ([('╦', (180, 196, 236))], 'a Gate of Leagues: its star map shows the nearest city and the other '
                                          'gates.'),
               ([('╟', (150, 180, 200))], 'a sluice hall: open the sluice, and the drowned hall runs dry.'),
               ([('♦', (140, 150, 190))], 'the fallen sky: black stones and glassy sand.'),
               ([('☼', (190, 206, 255))], 'a star house: your feet sweep the dust off an iron floor of stars.'),
               ([('╢', (150, 176, 196))], 'a sunken harbour, with old coins in the shallows.')]),
        ('p', 'League stones, the sign {│|196,200,214}, count down IV, III, II, I toward a city; once you can read the '
              'old letters, each shows the next. Walk into the telling things of these places.'),
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
              'you have found: walk on one, hear a rumour, read an old map or buy a chart, or look out from the '
              'top of a tower. They are faster than open land and never patrolled. They lead over passes, to waystations '
              '{Σ}, a safe rest; milestones {╥}; sealed vaults {Φ}; forgotten graveyards; and into hidden valleys {•}.'),
        ('h', 'The northern lights'),
        ('p', 'On clear autumn and winter nights the northern lights hang over the cold lands. While they are in the '
              'sky, the old magic stirs. Some grey stones out on the snow are rune stones {╨|110,235,210}: by day plain '
              'rock, under the lights they glow and point to a hidden place, and a milestone shows more than it did. '
              'Frost and Storm spells cost less mana.'),
        ('p', 'Over the barrows of the north a spirit rises, a pale {G|191,238,232} in a wan blue-green light. Speak to it and it '
              'asks one thing of you: an old grave set right, a lost sword brought back, a deed paid for. Then go back '
              'to the barrow. Dig into its barrow under its eyes, or rob the bier, and the dead wake: their light burns '
              'brighter and restless, and they come for you.'),
        ('p', 'All ghostly things carry that cold light about them; fiends a faint red glow, like embers.'),
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
        ('p', 'Falling ash, a sickly miasma, smoke on the wind: a great evil is near, or a rift has opened.'),
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
        ('p', 'Elk, ibex and their like want Hunting 10, aurochs and wild horses 20: below that a herd is too wary '
              'for you yet, and you cannot get close.'),
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
        ('p', 'Every beast gives parts: fangs, claws, horn, tusks, antlers, feathers, scales, ivory; spiders and '
              'beetles leave chitin. A crafter sets them in a piece for its power. Below the beast\'s tier in '
              'Skinning they tear more often. A critical blow while a big beast, a bear, an aurochs, a mammoth or a '
              'drake, is below half its life breaks a part off.'),
        ('h', 'Named beasts'),
        ('p', 'A named beast gives one or two parts of its own, besides its trophy. They carry its nature, a frost '
              'touch, a stone skin, a venom, and a piece made of them bears its name: the rares of the crafts. '
              'Taking them off whole wants Skinning 15 for a notable beast, 30 for a notorious one, 45 for a legend.'),
        ('p', 'Every named beast but the legends keeps a den near where it lives: a hollow tree, a thorn thicket, a '
              'cave, a mud wallow, a ledge, a burrow. You find it only by walking right up to it; then it is on your '
              'map, the sign {δ|196,120,90}. [>] goes in. Beaten, a beast runs for its den to lick its wounds. When it '
              'dies, its den is empty for good.'),
        ('p', 'Now and then a lord wants one alive. Wear it down below a quarter of its life, put it to sleep with a '
              'flask, and walk into it with a rope in your pack. If it wakes first, it is furious. The lord keeps it '
              'in a cage in his yard, and you can see it there.'),
        ('h', 'Hides and leather'),
        ('o', ['A fresh hide rots in two days. Its name says how long it has left.',
               'Set up a stretching frame out in the land and walk into it with salt in your pack: an hour of '
               'scraping, and the hide is salted. A salted hide keeps.',
               'A tanner in a village or town tans it for a fee; come back for the leather three days later. Or rub '
               'oak bark into a salted hide and it tans in your pack in five days.',
               'Work the leather at a workbench in the tanner\'s shop: leather armour, gloves, boots, a belt, a '
               'waterskin. A hide gives the leather of its beast: a deer plain leather, an elk sturdy leather, a '
               'wolf warm fur, a crocodile a hide that turns blows.']),
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


def ch_crafts(g):
    return [
        ('h', 'How a craft grows'),
        ('p', 'A life skill grows slowly, by doing, up to 50. Work far below your rank teaches nothing, a little below '
              'it little, at or above it most. In a craft list the colour of a name says which: grey nothing, green '
              'little, yellow good, orange the most. The first time you make or catch something counts double.'),
        ('p', 'Everything you gather has a rank: herbs, ore, fish, game. Above your rank it is too hard for you yet. '
              'The better things lie where the land is more dangerous: far from the roads, in the wild country, '
              'deeper under the earth. So you go further out as you grow.'),
        ('p', 'Foes far below you teach your weapons and schools little too.'),
        ('h', 'Herbs'),
        ('p', 'Every herb has two properties: Heal, Mana, Stamina, Regen, Cure, Staunch, Ward Fire, Ward Cold, Ward '
              'Poison, Sight, Calm, Swift, Strength, Sleep, Venom, Flame or Silver. Taste a herb to learn its first; '
              'from Foraging 15 you see the second when you pick it; a brew that works teaches both. What you do not '
              'know shows as ?. The herbalist monks in the monasteries name what you bring them.'),
        ('p', 'Each land has its herbs: arnica on the mountains, bloodmoss in the marsh, myrrh in the desert, '
              'ghostcap in old forest only at night. Starmoss grows only by the wonders and in the elven glades.'),
        ('h', 'Alchemy'),
        ('p', '[P] shows the herbs you carry. Pick two or three: what they share becomes the brew. Three that share one '
              'property make it stronger; nothing shared is a ruined brew. Better herbs and a higher rank make '
              'stronger brews.'),
        ('l', ['A shared Venom, Flame or Silver makes an oil: use it on your weapon and your blows poison, burn or '
               'sear the dead for a while.',
               'A shared Sleep makes a flask: throw it at a foe within six steps and it sleeps a few turns.',
               'Starmoss in a brew doubles it. Alone it makes the Starlight Elixir: +5 life for good, once in a '
               'hero\'s life.',
               'Brewed on strong spirits, a draught is a tincture: it lasts twice as long.']),
        ('h', 'Brewing'),
        ('p', 'At an inn or in a monastery cellar, [P] and then [Tab]: ale, berry wine and mead at first. Each people '
              'has its drink: halfling cider, dwarf stout, gnome cordial, elven wine; the north its juniper spirits, '
              'the south spiced spirits. Taste one, or hear it from an innkeeper there, and you can brew it once your '
              'rank allows. Royal mead nobody teaches.'),
        ('p', 'A drink sells best far from where it was brewed. From Brewing 30 every batch also fills a barrel for '
              'your cart. At a fire or a hearth you can pour a round for the company: your companions take heart. '
              'Bring a people their own drink and their innkeeper will remember you, and tell you of a place.'),
        ('p', 'Strong spirits warm you and give you courage. A third cup in a short while, or a second of spirits, '
              'and your aim goes.'),
        ('h', 'Mining and smithing'),
        ('p', 'An ore vein holds iron, or better ore where the land allows: silver in the hills, bog iron in the '
              'marsh, deepiron four floors down, bloodstone in the canyons, frostvein in the cold mountains, '
              'moonsilver in karst caves, sunstone in the desert, adamant in the deepest tunnels. Iron goes on your '
              'cart; the rest in your pack. A star that fell from the sky is star-iron.'),
        ('p', 'Walk into an anvil to smelt ore into bars, to forge, to mend your metal gear for a bar or a load of ore, '
              'or to hone your blade for a while. Smithing makes every metal weapon, mail and plate, helms, shields, '
              'gauntlets and greaves, and tools: a pick, a skinning knife, fish hooks.'),
        ('h', 'Tailoring and leather'),
        ('p', 'At a workbench, Tailoring makes quilted armour, robes, caps, hoods, sashes, wraps and soft shoes, '
              'each warm or cool as you choose; and bandages, rope and a fishing net. Warm clothes keep the cold '
              'from eating your food, cool ones the heat. Cloth comes from the villages: linen from the farms, wool '
              'from the herders, cotton in the south; spider silk from spiders, Fey Silk at night by the wisp fens.'),
        ('p', 'Leatherworking makes leather armour, gloves, boots, a belt and a waterskin from the leather of the '
              'beasts you hunt; and goods for the road: marsh, sand, snow and mountain boots that make the world map '
              'quicker over their own land, a bedroll and a tent for nights in the open, and barding for your beast. '
              'Use barding from your pack to buckle it on. Smithing makes mail barding.'),
        ('h', 'What you make'),
        ('p', 'The material decides the grade: the first two tiers make normal pieces, the middle two exceptional, '
              'the highest elite. It adds a property of its own: silver sears the dead, deepiron wears slower, '
              'moonsilver is lighter, sunstone wards fire, spider silk holds mana, snakeskin wards poison. Your rank '
              'decides the work: crude, fine or masterwork.'),
        ('p', 'The power of a piece is yours to choose: a part of a beast. Fangs to hit, claws for damage, horn and '
              'tusks for armour, antlers for stamina, feathers make it lighter, chitin wards poison, scales fire or '
              'cold, ivory gives life. The same part from a stronger beast gives more: wolf fangs +5, winter wolf +10, '
              'sabretooth +15. From rank 40 a piece takes two parts.'),
        ('p', 'Mend at the anvil or the bench for a bar, a bolt or a piece of leather: your own gear and your '
              'hireling\'s. You can hand a hireling what you make. In a town you can spend a morning mending for the '
              'townsfolk, for a few coins.'),
        ('h', 'Unmake'),
        ('p', 'From rank 40, at the anvil or the bench: take a found piece apart and move one of its powers onto a '
              'piece you made. The found piece is lost whatever happens. One moved power per piece, at two thirds of '
              'its worth; at 50 the whole of it. It can always fail: about 40 in 100 at rank 40, 70 at 50, never more '
              'than 80, and less for a strong power. One failure in four ruins or curses your own piece too. The '
              'chance shows before you choose. Uniques and pieces of a set cannot be unmade.'),
        ('h', 'Archaeology'),
        ('p', 'Old places and Varnish ruins hide dig spots, the sign {÷|214,176,110}. You see one only once you have '
              'the eye for it: the higher your Archaeology, the more spots a place shows, and the fewer finds you '
              'break. Walk into a spot with a trowel; a pick will do, but breaks more. Each place is as hard as its '
              'land, and a spot far below you teaches nothing, so you learn at places of your own height.'),
        ('p', 'What the earth gives: a piece of a Varnish riddle, or what happened on a battlefield or in a deserted '
              'village; from rank 20 now and then an old warning of a great evil\'s weakness; old pieces of arms and '
              'armour; shards of star-iron; old coins and finds. A smith mends an old piece at the anvil, and an old '
              'power comes back with it; Varnish work wants a shard of star-iron as well. A city library pays half '
              'again what a trader gives for coins and finds.'),
        ('h', 'Masters'),
        ('p', 'At rank 25 and again at 40 a life skill stops until a master has seen your work. A job in your journal '
              'tells you who and where, and what to bring. Town boards ask for orders at your own height too: they pay '
              'little and teach well. From rank 30 every skill has a master\'s perk at 30, 40 and 50; [C] shows them.'),
        ('p', 'Somewhere far from the roads live the three great masters: a smith, a leatherworker and a tailor. '
              'Nobody marks them on a map, but an innkeeper or a tanner may have heard of one, and then the hut is on '
              'yours, the sign {Φ|232,196,120}. Their test has three '
              'parts: a top find of their craft, a part of a notorious or legendary named beast, and the workshop they '
              'lost, won back. Then they unmake for you, one power a visit, for gold, half the time.'),
        ('h', 'Fish'),
        ('p', 'Fresh and salt water hold different fish. The big ones want their own water: grayling in mountain '
              'streams, sturgeon in broad rivers, ice char in the northern lakes, ghost pike in forest lakes at '
              'night, the thunderfin only in a storm at sea. A fish too strong for you yet snaps your line. A net '
              'takes small fish from shallow water without a cast; fish hooks land more.'),
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
              '[3] to [5], and one of a weapon guild on [1] or [2] while you hold its weapon. Below the highest ranks, '
              'a master will not teach a technique of a school that is not yours: you could never use it.'),
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


def ch_shadow(g):
    return [
        ('p', 'Out past the sea a piece of the Sky-Seat never fell, and in it sits the Hollow King, the old shadow of '
              'the Varnish. He wants to come back. The world lives round that, whether you meddle or not.'),
        ('h', 'His servants'),
        ('p', 'Three servants work for him in every world, each in a land of its own: a lesser one, awake from the '
              'start, that keeps to its own country; a greater one that wakes later and reaches a few baronies or a '
              'coast; and his right hand, who wakes last and reaches a whole realm. First you hear only rumours and see '
              'marks on the land: blight, ash, webs, empty woods. Then the rumours get a name.'),
        ('p', 'Each servant wants one thing, and gets it through the realms: wars, tribute, hunger, a baron who signs '
              'whatever he is given. A barony a servant holds takes its colour on the Realms layer. The realms push back '
              'with levies and the Church\'s order; that holds a servant back, but never stops it. Only you can kill one. '
              'When a servant has what it wants, a seal breaks, and the sky over the sea glows at night.'),
        ('h', 'His attention'),
        ('p', 'The Hollow King does not notice you until you meddle: kill a lieutenant, go into a lair, learn a '
              'weakness, beat his hunters. Then his attention grows, one step at a time. With it come hunters, faster '
              'plans, and the next servant wakes sooner. Leave him alone for a while, and he looks away again.'),
        ('h', 'Lieutenants'),
        ('p', 'Each servant has three lieutenants, each in a fort, a camp or a tower of their own, the sign {Ω|200,120,220}. '
              'You need not kill them, but each one dead makes its servant weaker, and a lord whose land you freed will '
              'remember. One who survives you heals, and comes back scarred and stronger.'),
        ('h', 'Weaknesses and relics'),
        ('p', 'Every servant has one weakness. Two sources tell it: a city library, a lieutenant\'s papers, the old '
              'riddles, the earth of an old place, or the journal of a hero who rode out against it. Named heroes do ride out; now and then one '
              'kills a lieutenant, and most never come back. A cairn, the sign {▲|200,196,180}, marks where one fell: '
              'walk into it to read what they knew. Once you know a weakness, it changes the fight in the lair. The '
              'Lich keeps her life in a black jar beside her, the sign {Φ|196,134,255}: break it, or she rises again.'),
        ('p', 'A fallen servant leaves a relic. Carried, it gives one small power; the old letters call the relics keys.'),
        ('h', 'The Sky-Seat'),
        ('p', 'Mist and storm hide the Sky-Seat out over the sea. The mist tears when you know the truth of the '
              'Hollow King, from the riddle of his name, or when the first seal breaks. The relics are the keys '
              'through it; whoever makes all five riddles whole finds the Star-Iron Key as well.'),
        ('p', 'No road you can travel by goes through his coast: you walk it, and his hunters find you there. One '
              'skipper, on the harbour nearest his coast, dares the whirlpool, for twenty silver and a relic to show '
              'the mist. Your company cannot come in a boat that small.'),
        ('p', 'The Varnish chained the city down with star-iron. You climb a chain, the sign {§|200,204,216}, with the '
              'sea far below. When the chain sings, a gust is coming: stand by a handhold, the chain bound to the '
              'rock, or it throws you off. A broken link, the sign {:|160,96,60}, and cracked glass, the sign '
              '{░|216,238,244}, give way if you stand on them. A fall goes into the sea, and the skipper hauls you out.'),
        ('p', 'The city has five floors of glass and bronze, from the Under-City to the throne. Walk into the beacon '
              'on each floor, the sign {¥|136,144,160}, to light it: a lit floor stays calm, and from the rocks a rope '
              'of light takes you up to the highest one you lit.'),
        ('h', 'The last fight'),
        ('p', 'The Hollow King fights in three phases: the winds, the dead, and himself. Every relic you carry makes '
              'one of them lighter, without its heaviest blow. A town portal will not open in his city.'),
        ('h', 'Dying there'),
        ('p', 'He keeps those who die in his city: the priests must fight for you, the raising costs twice as much, '
              'and you wake on the mainland. Your body rises as your shade, with your backpack: weaker than you, and it '
              'does not heal. Beat it to get your things back. The same happens in the barrows, the crypts and the '
              'Rift. What you opened stays open and the slain stay dead, but on every floor without a lit beacon he '
              'sends new bound dead.'),
        ('h', 'The ends'),
        ('p', 'If three seals break, the Long Night comes: the sky stays dark, his coast spreads, the cities shut their '
              'gates and everything is a fifth dearer. He can still be beaten, only harder. If you beat him, the '
              'world heals and goes on, and the chronicle keeps your name. There is no second Hollow King.'),
        ('h', 'Where it shows'),
        ('p', 'The journal\'s Shadow tab keeps what you know of him, his servants and their lieutenants. On the map, '
              '[7] shows his coast, each servant\'s mark and the lands they hold. The line under the map says when you '
              'stand on his coast, or in a land a servant holds.'),
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
        ('p', 'At the end of a goblin ravine a carved gate leads into their village, cut deep into the rock: a market '
              'hall, a forge, family halls, cells and wolf pens along a wide gallery, and the chief\'s hall at the back. '
              'Below lie the mine and the deep halls. Kill the chief and sit in the high seat, and the village bows to '
              'you, for a while.'),
    ]


def ch_death(g):
    return [
        ('p', 'Softcore: the priests raise you, for a fee from your purse. Your pack stays with your body, and you are '
              'weak for a day or two. No coin for the temple: your tale ends there.'),
        ('p', 'Where the dead are bound, in the barrows, the crypts, the Rift and the Sky-Seat, your body does not lie '
              'still: it rises as your shade, with your pack. Beat it to get your things back.'),
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
              'days, The realms, A lord or house, This city, Beasts you have met, the Varnish letters, or The Varnish. A subject costs a few silver and '
              'a few hours, the letters a day; members of the Circle of Magi read for free. A library is true but '
              'slow: its own realm it knows well, far realms late. It also buys the old books you find.'),
        ('p', 'The dwarves keep their Grudge Book, and under the Elder Tree a loremaster sings of the old days.'),
        ('h', 'The Varnish'),
        ('p', 'What is left of the empire before the Ruin goes in its own chapter, The Varnish, by subject: its gods, '
              'its emperors, its daily life, its uncounted, its bound dead. Pieces of it are cut on stones in its '
              'ruins, heard now and then, and kept on a library\'s Varnish shelf.'),
        ('p', 'Some of its books lie in pieces across the world, a letter or a leaf in each place. You keep a page '
              'with your papers, not in your bag, and read it once you have the letters. From the second page the '
              'chronicle sees which belong together, and which are still missing, never where. With every page of a '
              'book, a scribe binds it for a few silver and an hour, and finds what only the whole shows. Read the '
              'bound book from your bag, or sell it to a library, once, and well.'),
        ('p', 'Five old riddles grow in The Old Days, each under its own heading: how the Sky-Seat fell, who the '
              'Hollow King was, where the orcs came from, what lies in the vaults, why the dead were bound. With six '
              'true pieces a riddle is whole; then what was false shows up red, and the riddle points to a place.'),
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
    ('The land', ch_land), ('Dungeons', ch_dungeons), ('Weather and seasons', ch_weather), ('Travel and sailing', ch_travel),
    ('Camp, food and rest', ch_camp), ('Hunting and cooking', ch_hunt), ('Crafts', ch_crafts), ('Your company', ch_company),
    ('Guilds', ch_guilds), ('Gods', ch_gods), ('Realms and lords', ch_realms), ('The shadow', ch_shadow),
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
