"""Folk in need (rounds 46-47, "Folk in need" in docs/plan.md): the lists the maker draws from. Who gives (by people),
what each trade asks for and gives back, the motives, the favours, and the lines people say. The maker is
`folkquests.py`; the Dutch proposal with examples: project files `quests/voorstel.md`."""

# the people who may have a need, by people: (trade, how they are named after their first name)
GIVERS = {
    'human': [('miller', "the miller's wife"), ('shepherd', 'the shepherd'), ('smith', 'the smith'),
              ('fisher', 'the fisherman'), ('inn', "the innkeeper's daughter"), ('priest', 'the sexton'),
              ('guard', 'a watchman'), ('carter', 'the carter'), ('weaver', 'the weaver'), ('baker', 'the baker'),
              ('herb', 'the herb-woman'), ('reeve', "the reeve's son"), ('hunter', 'the trapper'),
              ('sailor', 'an old sailor')],
    'halfling': [('baker', 'the pie-maker'), ('miller', 'the miller'), ('inn', 'the alewife'), ('herb', 'the gardener'),
                 ('shepherd', 'the goatherd'), ('fisher', 'the eel-catcher'), ('reeve', "the Thain's nephew"),
                 ('weaver', 'the quilter')],
    'dwarf': [('smith', 'the smith'), ('miner', 'the shift-boss'), ('inn', 'the brewer'), ('priest', 'the keeper of the book'),
              ('guard', 'a gate-warden'), ('carter', 'the cart-master'), ('reeve', "the hold-lord's steward")],
    'elf': [('herb', 'the tree-singer'), ('hunter', 'the warden'), ('weaver', 'the weaver of light'),
            ('priest', 'the song-keeper'), ('guard', 'an archer of the glade')],
    'gnome': [('tinker', 'the tinker'), ('herb', 'the mushroom-picker'), ('miner', 'the gem-cutter'), ('inn', 'the cook'),
              ('reeve', 'the elder of the burrows')],
    'orc': [('smith', 'the smith'), ('hunter', 'the boar-hunter'), ('guard', 'a sparring-master'), ('carter', 'the drover'),
            ('herb', 'the bone-setter')],
    'kobold': [('miner', 'the digger'), ('tinker', 'the trap-maker')],
    'goblin': [('carter', 'the scavenger'), ('cook', 'the pot-boy')],
    'lizard': [('fisher', 'the net-caster'), ('priest', 'the egg-keeper')],
}
PEOPLE_RACE = {'orc': 'orc', 'kobold': 'goblin', 'goblin': 'goblin', 'lizard': 'human'}   # for random_name

# what a trade asks for when its work stands still (a good from the markets), and the line that says so
TRADE_NEED = {
    'smith': ('ore', 'No ore since the carts stopped coming. My forge is cold.'),
    'miner': ('tools', 'Two picks broke this week, and the third is not long for this world.'),
    'fisher': ('cloth', 'My net is more hole than net. I need cloth and cord to mend it.'),
    'inn': ('ale', 'The cellar is dry, and folk will not sit in an inn without ale.'),
    'priest': ('honey', 'No wax for the candles. The dead are buried in the dark.'),
    'carter': ('timber', 'A wheel split on the stones. I need good wood for a new one.'),
    'weaver': ('wool', 'The loom stands idle. Not a fleece to be had.'),
    'baker': ('grain', 'No flour, no bread. The ovens are cold for the first time in years.'),
    'herb': ('herbs', 'A child in the lane is sick, and my shelves are bare.'),
    'miller': ('grain', 'The mill turns on nothing. Bring me grain to grind and folk can eat.'),
    'tinker': ('tools', 'My best contraption lacks a single piece. Any good tools would do.'),
    'shepherd': ('salt', 'The flock needs salt licks, or they sicken. The salt cart never came.'),
    'hunter': ('furs', 'A cold winter, and every pelt went to the market. My own children shiver.'),
    'reeve': ('medicine', 'Half the village has the cough. We need medicine before it spreads.'),
    'guard': ('arms', 'Half of the watch has no spear worth the name.'),
    'sailor': ('fish', 'My old legs will not take me to sea, and my pot is empty.'),
    'cook': ('spice', 'A feast without spice is a feast for nobody.'),
}

# the news that makes folk ask: event key -> (good, what happened)
NEWS_NEED = {'plague': ('medicine', 'Since the sickness came, half the street is abed.'),
             'famine': ('grain', 'We have eaten the seed corn. There is nothing left to sow.'),
             'fire': ('timber', 'The fire took our roof. Winter is coming, and we sleep under a cart.'),
             'war': ('arms', 'The raiders are coming, they say. My boy has only a hoe to fight with.'),
             'undead': ('medicine', 'The dead walk by night. Those they bit will not stop bleeding.'),
             'raid': ('arms', 'They came by night and took everything sharp. Next time we fight.')}

# the year: season -> (good, what is lacking)
SEASON_NEED = {'winter': [('timber', 'The woodpile is gone, and the frost gets in through the walls.'),
                          ('furs', 'My old mother cannot keep warm. A fur for her bed, if you can.')],
               'summer': [('ice', 'The heat spoils everything. A block of ice would save the larder.'),
                          ('ale', 'The harvest hands want ale, and the barrels are empty.')],
               'autumn': [('salt', 'The pig is killed, and there is no salt to keep the meat.')],
               'spring': [('wool', 'The lambs came early and the shearing late. I need wool for the spinning.')]}

# the feasts ask for: good, what for
FEAST_NEED = [('ale', 'a barrel for {feast}'), ('wine', 'wine for the table at {feast}'),
              ('honey', 'honey for the cakes of {feast}'), ('fruit', 'fruit for the garlands of {feast}')]

# each people's own worries (verb, line): find = a keepsake in a dungeon nearby, go = word to kin, hunt or kill = a
# beast that is really there, bring = a good, dish = something cooked
PEOPLE_NEED = {
    'halfling': [('find', "Granny's book of recipes", 'Granny lent her book of recipes to a cousin, and the cousin '
                  'took the wrong road. It was found in {place}, they say. Ninety years of pies!'),
                 ('dish', None, 'There is a feast in the next hill and I promised a dish. My oven broke. Cook something '
                  'for me, anything warm, and I will carry it over.')],
    'dwarf': [('hunt', None, 'There is a line in the grudge-book with my grandfather\'s name on it, and the beast that '
               'made it still walks: {beast}. Strike it out for us.'),
              ('find', 'a miner\'s lamp with a name on it', 'My grandson went down into {place}. We found his tracks and '
               'nothing more. Bring back his lamp, at least.')],
    'elf': [('bring', 'herbs', 'The old tree by the pool is sick. The bark weeps. I need herbs for a poultice.'),
            ('go', None, 'A song of ours was taken to {town} long ago. Tell the keeper there we would have it back.')],
    'gnome': [('bring', 'tools', 'My invention, the self-turning spit, lacks one part. Good tools, and I can make it.'),
              ('find', 'a cog of brass', 'A rival stole my best cog and dropped it running away, into {place}. Get it '
               'back before he does!')],
    'orc': [('go', None, 'They call my brother a thief in {town}. He is not. Tell the reeve there what I tell you.'),
            ('kill', None, 'Nobody gives a half-orc work but the dangerous kind. {beast} took my cart. Help me, and I '
             'am in your debt.')],
    'kobold': [('bring', 'gems', 'Shiny! The chief wants shiny for the hoard, and I have none. Bring a gem, any gem.')],
    'goblin': [('kill', None, 'The boss beats me when the hunt goes wrong. {beast} keeps eating our hunters. Kill it '
                'and I say I did.')],
    'lizard': [('find', 'an egg of speckled green', 'An egg of our clutch was taken. The thief fled into {place}. It must '
                'come home warm.')],
}

# what each trade gives back besides coin and standing: a favour (a token in the pack, used once in a window that
# already exists), something of its own, a rumour or knowledge of a beast
TRADE_REWARD = {'smith': 'repair', 'miner': 'own', 'fisher': 'ferry', 'inn': 'bed', 'priest': 'heal', 'carter': 'rumour',
                'weaver': 'own', 'baker': 'own', 'herb': 'own', 'miller': 'own', 'tinker': 'rumour', 'shepherd': 'guide',
                'hunter': 'bestiary', 'reeve': 'lord', 'guard': 'gate', 'sailor': 'ship', 'cook': 'own'}

# the favours: kind -> (the token's name with the giver in it, what it does, where you show it)
FAVOURS = {
    'ferry': ("{who}'s ferry token", 'A ferryman takes you over for nothing, once.', 'the ferry'),
    'ship': ("{who}'s chit for a skipper", 'One plain passage by ship for nothing.', 'a harbour'),
    'gate': ("{who}'s word at the gate", 'The guards of a town where you are wanted let you in, once.', 'a town gate'),
    'bed': ("{who}'s inn token", 'One night at an inn for nothing.', 'an inn'),
    'repair': ("{who}'s smith's mark", 'One mending of all your gear for nothing.', 'a smith'),
    'heal': ("{who}'s blessing", 'The temple raises you for nothing, once.', 'the temple'),
    'guide': ("{who}'s carved whistle", 'A herder\'s path over a pass the snow has shut, once.', 'a shut pass'),
    'lord': ("{who}'s letter of thanks", 'A lord thinks better of you when you hand it over.', "a lord's hall"),
}

# something the giver owns, by trade: (kind, type) as in the loot rule (only what such a person has)
OWN = {'miner': [('potion', 'hp_minor')], 'weaver': [('food', 'bread')], 'baker': [('food', 'bread')],
       'herb': [('potion', 'cure'), ('potion', 'hp')], 'miller': [('food', 'bread')], 'cook': [('food', 'bread')]}

MOTIVES = ['safety', 'health', 'family', 'knowledge', 'property', 'tools', 'honour', 'peace', 'skill', 'feast']

# the line said in passing, by motive, before the need itself
PASSING = {'safety': ['Has anyone seen it? It came again last night.', 'Lock your door tonight, friend.'],
           'health': ['If only someone could help...', 'Another one sick today.'],
           'family': ['Has anyone seen my kin? Please...', 'They should have been back by now.'],
           'property': ['It was here, and now it is gone.', 'Gone, all of it.'],
           'tools': ['Nothing works as it should.', 'How am I to work like this?'],
           'honour': ['It is a matter of honour.', 'They will not laugh at us for long.'],
           'peace': ['I cannot rest until it is done.', 'Somebody has to do it.'],
           'feast': ['The feast is coming, and nothing is ready!', 'What will we put on the table?'],
           'knowledge': ['Somebody must know.', 'If only I could read the signs.'],
           'skill': ['I cannot do it alone.', 'My hands are not what they were.']}
MOOD = {'safety': 'afraid', 'health': 'worried', 'family': 'anxious', 'property': 'upset', 'tools': 'fretting',
        'honour': 'grim', 'peace': 'sad', 'feast': 'flustered', 'knowledge': 'puzzled', 'skill': 'troubled'}
THANKS = ['"You did it! I will not forget this."', '"Thank you, friend. Truly."', '"The gods sent you, I think."',
          '"I did not think anyone would help. Thank you."']
