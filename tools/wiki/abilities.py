"""What each monster ability does, in plain words, for the wiki. Taken from the code: data.py's flags, ai.py's traits
and behave.py's behaviours (beh); rift.py for the Ashen Deep. Keep the numbers in step when those change."""

# flags on the monster (data.py) and how engine.py uses them
FLAGS = {
    'fast': ('Fast', 'Acts twice every other turn.'),
    'slow': ('Slow', 'Acts only every other turn.'),
    'erratic': ('Erratic', 'Half its turns it flutters about at random instead of coming at you.'),
    'ranged': ('Ranged', 'Shoots from 2-7 tiles away when it can see you.'),
    'caster': ('Caster', 'Casts a bolt from 2-7 tiles away; silence stops it.'),
    'poison': ('Venom', 'Its hits may poison you (40%), less with poison resistance.'),
    'regen': ('Regenerates', 'Heals a little every turn.'),
    'leech': ('Drinks life', 'Heals a third of the damage it deals you.'),
    'leap': ('Leap', 'Leaps at you from 2-5 tiles away and strikes for 1.4x damage.'),
    'nova': ('Nova', 'When you are within 2 tiles, sometimes bursts in a ring for 0.8x damage of its element.'),
    'summon': ('Summons', 'Calls a helper beside it now and then (chiefs up to 4, bosses up to 6).'),
    'chief': ('Chief', 'Leads a band: those near it hit 15% harder; when it falls, about half the band breaks and runs.'),
    'boss': ('Boss', 'Fixed level, unique, the end of its lair.'),
    'split': ('Bursts open', 'When it dies, two to four young spill out.'),
}
# the old traits (ai.py TRAITS); some behaviours below add kinds to them
TRAITS = {
    'coward': ('Coward', 'Below 30% life it runs, licking its wounds when far off; cornered, it fights.'),
    'pack': ('Pack hunter', 'Within 4 tiles the pack fans out around you instead of queuing up.'),
    'kite': ('Keeps its distance', 'An archer or caster: when you close in, it steps back to shoot again.'),
    'lurk': ('Lurker', 'Waits unseen until you come within 2 tiles, then drops on you.'),
    'howl': ('Howls', 'When it wakes it howls, and everything asleep within 14 tiles wakes too.'),
    'berserk': ('Berserk', 'Below 40% life it flies into a rage: 1.4x damage for the rest of the fight.'),
    'healer': ('Healer', 'Prays over a hurt friend within 6 tiles and heals a quarter of its life.'),
    'charge': ('Charge', 'From 3-6 tiles in a straight line it paws the ground (a turn of warning), then rushes up to '
                         '6 tiles for 1.6x damage. Step out of the line.'),
    'wander': ('Wanders', 'Roams about even before it has noticed you.'),
}
# the behaviours (beh) in creatures.py, menagerie.py, varnish.py...; ones the traits above already cover point there
BEH = {
    'acid': ('Acid', 'Its hits eat at your armour.'),
    'acidcloud': ('Acid cloud', 'Within 2 tiles it turns its back (a turn of warning), then sprays boiling acid over '
                                'everything within 2 tiles; it wears your armour.'),
    'acidspit': ('Acid spit', 'From 2-4 tiles it rears up (warning), then spits acid for 0.8x damage and wears your '
                              'armour twice. Step aside and it may miss.'),
    'ambush': ('Ambush', 'Hides until you are close; its first strike from hiding does 1.8x damage.'),
    'ash': ('Ash', 'Hit it up close and a puff of ash may blind you for 2 turns (40%).'),
    'babble': ('Babble', 'Within 4 tiles its babbling may confuse you for 3 turns.'),
    'backstab': ('Backstab', 'Strikes 1.5x harder when another creature stands beside you.'),
    'blur': ('Blur', '30% of your single-target blows strike only an image; area attacks always find it.'),
    'bomb': ('Fire pot', 'From 2-6 tiles it lights a fuse (warning), then throws a fire pot that bursts on the tile you '
                         'stood on. Move.'),
    'burrow': ('Burrows', 'Lies hidden in the ground and bursts out when you come close; its first strike does 1.8x.'),
    'charge': ('Charge', TRAITS['charge'][1]),
    'charm': ('Charm', 'Within 4 tiles it may charm you for 3-5 turns: you cannot bring yourself to strike it.'),
    'cinders': ('Dies into fire', 'Leaves burning ground where it dies.'),
    'climb': ('Climbs', 'Next to you it often scrambles up the wall and away, out of reach.'),
    'curse': ('Curse', 'Within 6 tiles it may curse you for 40 turns: 20% less damage, half the healing.'),
    'darkness': ('Darkness', 'From 2-7 tiles it gathers the shadows (warning), then a cloud blinds you for 5 turns if '
                             'you are still within 2 tiles of the spot.'),
    'disease': ('Disease', 'Its bite may make you diseased (30%): no natural healing for a long time, or until cured.'),
    'disguise': ('Disguise', 'Looks like a statue or a stone and wakes only when you step next to it; its first strike '
                             'does 1.8x.'),
    'drain': ('Drain', 'Its touch may weaken you (30%) for 40-70 turns: 15% less damage.'),
    'dust': ('Dust', 'Next to you it beats its wings and a choking dust hurts you.'),
    'eatfood': ('Eats your food', 'Its hits may get into your pack and eat a ration (35%).'),
    'enlarge': ('Grows', 'Once, within 3 tiles, it swells to twice its height: 1.3x life and damage.'),
    'formation': ('Formation', 'With a friend beside it: hits 10% harder, hits more often, and takes 20% less damage. '
                               'A flail swings over the shields.'),
    'gaoler': ('Runs for the gong', 'When it sees you it runs to the gong and wakes the whole level. Catch it first.'),
    'gaze': ('Gaze', 'From 2-7 tiles it fixes its eyes on you (warning), then paralyses, confuses or frightens you '
                     'if it still has a clear line. Break the line of sight.'),
    'glow': ('Glows', 'Lights up the dark around it, so you see it coming.'),
    'grab': ('Grab', 'Its hits may seize you (40%) for 3-5 turns: you cannot step away and it always hits you. '
                     'Each try to move is a strength roll to tear free.'),
    'greedy': ('Thief', 'Its hit may snatch 4-10% of your coin (30%) and it runs; kill it and the coin spills out.'),
    'hook': ('Hooked chain', 'From 2-5 tiles it throws a chain and drags you to it, over the river of fire if it can.'),
    'horde': ('Horde', 'Comes in big groups.'),
    'hunt': ('Hunter', 'Never waits: it roams and runs you down.'),
    'invis': ('Vanishes', 'Below half life it fades from sight for 6 turns.'),
    'kite': ('Keeps its distance', TRAITS['kite'][1]),
    'knockback': ('Knockback', 'Its hits may send you flying two tiles (40%); into a wall hurts, off a tower is a fall.'),
    'latch': ('Latches on', 'Once it hits, it clings to you and drinks your blood every turn, healing itself, and '
                            'follows when you step away.'),
    'leader': ('Leader', 'Leads its band: those near it hit 15% harder; when it falls, about half break and run.'),
    'lord': ('Lord of the gate', 'Heals from its burning fire bowls; at half strength it calls its hellhounds. Put out '
                                 'the bowls first.'),
    'metal': ('Rusts metal', 'Your weapon wears when you hit it, your armour when it hits you.'),
    'mindsip': ('Mind sip', 'Its hits may drink your mana (50%).'),
    'pack': ('Pack hunter', TRAITS['pack'][1]),
    'paralyse': ('Paralyse', 'Its hits may paralyse you for 1-2 turns (25%); everything hits a helpless target. '
                             'Afterwards a few turns of immunity.'),
    'phase': ('Phases', 'Flickers in and out of the world every few turns; while faded your blows pass through it.'),
    'pollen': ('Pollen', 'Within 2 tiles a cloud of pollen may put you to sleep for 2 turns; a blow wakes you. '
                         'Poison resistance helps.'),
    'pounce': ('Pounce', 'From 2-5 tiles it crouches (warning), then leaps to where you stood and strikes for 1.5x. '
                         'Step aside.'),
    'pull': ('Tongue', 'From 2-4 tiles its tongue drags you to it.'),
    'rage': ('Berserk', TRAITS['berserk'][1]),
    'rooted': ('Rooted', 'Never moves: it only bites what comes next to it.'),
    'shield': ('Shield', 'Turns the first three blows aside: each does only a quarter. A flail swings over it.'),
    'shriek': ('Shriek', 'Once, when it sees you, it shrieks and wakes everything within 30 tiles.'),
    'slag': ('Glowing slag', 'Burns you when you hit it up close; frost makes it brittle for 6 turns and then every '
                             'blow does double.'),
    'sleepdart': ('Sleep dart', 'Its shots may put you to sleep for 2 turns (25%).'),
    'slows': ('Chill', 'Its hits may slow you for 3-5 turns (35%).'),
    'split': ('Bursts open', 'When it dies, young spill out.'),
    'spores': ('Spores', 'Within 2 tiles a cloud of spores may confuse you for 3 turns; poison resistance helps.'),
    'stench': ('Stench', 'Next to you its stench may slow you for 3 turns.'),
    'still': ('Totem', 'Does not move or fight: it heals its band or drives them into a frenzy (1.3x damage).'),
    'stink': ('Stink pot', 'From 2-6 tiles it swings a pot (warning), which slows you for 4 turns if it breaks within '
                           '1 tile of you.'),
    'sulphur': ('Sulphur spit', 'From 2-4 tiles it spits sulphur: a little poison damage and it takes your stamina.'),
    'sunblind': ('Hates the sun', 'In daylight in the open it hits 30% softer and misses more.'),
    'swarm': ('Swarm', 'Weapons do half damage to it; fire and area attacks do double.'),
    'totem': ('Plants a totem', 'Once per fight it plants a healing or bloodlust totem by its band. Break the totem.'),
    'traps': ('Lays snares', 'Sets snares where you will walk; one holds you for 3 turns. You may spot them up close.'),
    'unseen': ('Unseen', 'Invisible until it hits you; when you back off it vanishes again.'),
    'wail': ('Wail', 'Within 6 tiles it draws breath (warning), then a wail frightens you for 6 turns: your blows '
                     'falter now and then.'),
    'walls': ('Walks through walls', 'Does not go round: it steps into the rock and out again, nearer to you.'),
    'web': ('Web', 'From 2-6 tiles it lifts its abdomen (warning), then spins a web that holds you for 3 turns. '
                   'Step aside and it may miss.'),
}
# your states (behave.py)
STATES = {
    'Held': 'You cannot step away until you tear free (a strength roll each try); its bites always land.',
    'Paralysed': 'You cannot act for a turn or two; then a few turns in which it cannot happen again.',
    'Asleep': 'As paralysed, but a blow wakes you.',
    'Slowed': 'Everything gets two moves to your one.',
    'Confused': '40% of your steps go a random way.',
    'Afraid': '35% of your attacks falter, and you deal 10% less damage.',
    'Blinded': 'You see only the tiles next to you.',
    'Diseased': 'No natural healing until cured or it passes.',
    'Cursed': '20% less damage dealt, half the healing.',
    'Weakened': '15% less damage dealt.',
    'Charmed': 'You cannot strike the one who charmed you.',
}
