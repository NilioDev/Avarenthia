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


# ------------------------------------------------------------------ the twists (round 47)
# key -> (the verbs it may hang on, what you find, [(option, outcome)]). An outcome: coin (times the reward), rep (the
# giver's town), god (your god), law (+ clears, - a mark), end (the need is done now), fail (it is lost), step (a new
# step first: go_temple, go_town), follow (a later part), friend (a beast that remembers you), owner (a second person)
TWISTS = {
    # round 49: the false mark, found when you reach the forger (a guild job; no step has this verb, so it comes last)
    'forger': ({'forger'}, 'In a back room of the poor quarter you find the forger: ink on his fingers, and a box of '
               'seals cut just like the guild\'s. "Half of what I made is yours," he says, "if you never saw me."',
               [('Take him to the Watch', dict(law=3, rep=1)), ('Take a share and keep quiet', dict(coin=2.2, law=-4))]),
    'young': ({'kill', 'clear'}, 'Behind it, in the hollow, small ones squeal: it was guarding its young.',
              [('Kill the young too', dict(coin=1, god=-1)), ('Let them go', dict(coin=.5, friend=True, god=1)),
               ('Take them alive for the lord\'s menagerie', dict(coin=1.6, rep=-1))]),
    'worse': ({'kill', 'clear'}, 'Its hide is torn with claw-marks bigger than its own. Something worse drove it here.',
              [('Tell the giver what you saw', dict(coin=1, rep=1, rumour=True))]),
    'child': ({'watch'}, 'The thief is a child, all ribs and eyes, with a hen under each arm.',
              [('Hand the child over', dict(coin=1, god=-1)), ('Pay for the hens yourself and let it go',
                                                                dict(coin=0, pay=300, god=2, rep=1)),
               ('Take the child to the temple', dict(coin=.5, god=1, rep=2))]),
    'stay': ({'go'}, 'They are well, and in love, and will not come home.',
             [('Make them come home', dict(coin=1, rep=-1)), ('Let them be', dict(coin=.5, rep=1)),
              ('Have them write a letter home', dict(coin=1, rep=1))]),
    'liar': ({'find'}, 'A woman stops you on the way back: "That is mine. Ask anyone. It was stolen from my house."',
             [('Give it to her', dict(end=True, coin=.6, rep=1, god=1)), ('Keep your word to the giver', dict(coin=1, god=-1)),
              ('Ask the reeve to judge', dict(coin=.5, rep=2))]),
    'rival': ({'find', 'kill', 'clear', 'hunt'}, 'Another is after the same thing: {rival}, who got there a day before you.',
              [('Share it with them', dict(coin=.5, rep=1)), ('Pay them off', dict(coin=1, pay=1000)),
               ('Let them have it', dict(end=True, coin=0, rep=-1))]),
    'sold': ({'find'}, 'Gone: a trader took it out a week ago, and sold it on in {town}.',
             [('Go and buy it back', dict(step='go_town', pay=800)), ('Tell the giver it is gone', dict(end=True, coin=.3))]),
    'cursed': ({'find'}, 'It is cold in your hand, colder than it should be. There is a curse on it.',
               [('Bring it as it is', dict(coin=1, follow='sick')), ('Take it to a temple first', dict(step='go_temple')),
                ('Break it and tell them', dict(end=True, coin=.4, god=2))]),
    'late': ({'find', 'go'}, 'You are too late. There is a grave, and a letter for whoever came looking.',
             [('Bring the letter back', dict(coin=.6, grave=True))]),
    'wrong': ({'watch', 'kill'}, 'It was never what they blamed. The real mischief is someone in the town itself.',
              [('Name them before the reeve', dict(coin=1, rep=2, law=1)), ('Keep it to yourself', dict(coin=1))]),
    'bewitched': ({'kill'}, 'It does not fight like a beast. It looks at you, and there is a person behind its eyes.',
                  [('Finish it', dict(coin=1, god=-1)), ('Find a priest to break the spell', dict(step='go_temple', coin=1.5))]),
    'weather': ({'go', 'seat'}, 'The weather turns on the road: you lose half a day in a ditch, soaked through.',
                [('Press on', dict(coin=1, lose=12))]),
    'opposite': ({'kill', 'bring'}, '{other} catches your sleeve: "Do not. Half the village wants the opposite of what '
                 'they asked you."', [('Do what the giver asked', dict(coin=1, rep=-1)),
                                      ('Side with {other}', dict(end=True, coin=.8, rep=1))]),
    'hidden': ({'find', 'clear'}, 'The trail goes on past where it should end: to a place nobody has marked.',
               [('Mark it on your map', dict(coin=1, rumour=True))]),
    'captive': ({'clear', 'find'}, 'In the dark someone calls for help: a captive, bound and starving.',
                [('Cut them loose and take them home', dict(coin=1, rep=2, captive=True))]),
    'sick': ({'kill'}, 'It is sick, starving and lame. That is why it came so close to people.',
             [('End it quickly', dict(coin=1)), ('Heal it with herbs', dict(coin=.5, need_good='herbs', friend=True, god=1))]),
    'danger': ({'go', 'seat', 'find'}, 'Word reaches you: while you were away, trouble came to the giver\'s door.',
               [('Hurry back', dict(coin=1, rep=1, lose=0))]),
    'more': ({'kill', 'hunt'}, 'In the mud, among its tracks, are the prints of bare human feet.',
             [('Keep it in mind', dict(coin=1, rumour=True))]),
}
TWIST_HINT = {'young': 'They say it has been carrying food away.', 'worse': 'Something howls further off at night.',
              'child': 'Small footprints by the hen-house, they say.', 'stay': 'There was talk of a sweetheart.',
              'liar': 'Not everyone agrees whose it was.', 'sold': 'A trader came by not long ago.',
              'cursed': 'The old folk do not like to speak of it.', 'rival': 'Somebody else was asking about it.',
              'bewitched': 'A witch was seen on the moor this spring.', 'sick': 'It limps, the shepherd says.'}
BOARD_TWISTS = ['rival', 'worse', 'hidden', 'captive', 'late', 'wrong']   # the twists a board job may get

# the follow-ups: (what the giver says, what they give)
FOLLOW = {
    'wedding': ('"I am to be married, and I want you at the wedding! Come before the week is out."', 'gift'),
    'friend': ('The beast you spared comes to the edge of the firelight, and does not run.', 'beast'),
    'apprentice': ('"My boy wants to see the world. He says he would carry your pack for nothing."', 'rumour'),
    'sick': ('"Since you brought it, I cannot get warm. Bring medicine, I beg you."', 'need'),
    'thanks': ('"I told everyone what you did. The whole street knows your name."', 'rep'),
}
GREET = ['{name} waves to you.', '{name} nods: "Good to see you again."', '"There is the one who helped me!" says {name}.']


# ------------------------------------------------------------------ the seeds (round 47): 120 small stories by hand
# (title, where it may fall, the giver's trade, what they say, the steps, the twist). Where: the peoples (any of human
# halfling dwarf elf gnome orc kobold goblin lizard; none named = any), settlement kinds (hamlet village town city
# metropolis deephold), and needs: temple, harbour, winter, summer, autumn, spring. Steps: kill (a group out on the
# land), clear (the chief of a nest), hunt (a named enemy), find:<thing> (a dungeon near), go:<who> (a town near),
# seat (a lord's seat), watch, bring:<good>:<n>, dish. Each world gets 20 to 25 of them.
SEEDS = [
    ('The bell that rings at night', 'human village temple', 'priest', 'The chapel bell rings at midnight, and nobody '
     'is in the tower. Watch it with me one night, and if it is what I fear, find the old bell-rope that was buried with '
     'the last ringer.', ['watch', 'find:the bell-ringer\'s rope'], 'wrong'),
    ('Two brothers, one field', 'human hamlet village', 'reeve', 'My father left one field to two sons, and they '
     'will kill each other over it. Our uncle in the next town knows what father truly wanted. Ask him.',
     ['go:our uncle'], 'opposite'),
    ('The goose that lays copper', 'human halfling village town', 'miller', 'My goose lays eggs with copper in them. '
     'I swear it. Something stole her in the night, and the tracks go out to the moor.', ['kill'], 'young'),
    ('A wedding without a fiddler', 'human halfling village town', 'inn', 'The wedding is in a week, and the fiddler '
     'broke his arm. His cousin in the next town plays as well. Fetch him, and bring ale for the guests.',
     ['go:the fiddler\'s cousin', 'bring:ale:2'], 'stay'),
    ('The drowned ring', 'human town harbour', 'sailor', 'I threw my ring into the sea the day she left me. Now she '
     'is back, and I want it. A diver says the current took it to an old wreck-hole nearby.',
     ['find:a ring with a blue stone'], 'liar'),
    ('Salt for the winter', 'human village autumn', 'shepherd', 'The pig is killed and the salt cart never came. '
     'Two loads of salt and we eat this winter.', ['bring:salt:2'], None),
    ('Grandfather\'s sword', 'human village town', 'smith', 'My grandfather fell in the old war. His sword was never '
     'found. They say a barrow-thing keeps it in the deep places.', ['find:grandfather\'s sword'], 'cursed'),
    ('The lost lamb', 'human halfling hamlet village spring', 'shepherd', 'One lamb strayed, a black one, my '
     'daughter\'s. Something big lives out there now. She cries every night.', ['kill'], 'sick'),
    ('The sexton\'s fear', 'human village town temple', 'priest', 'The graves are dug up from below. From below! '
     'Keep watch in the churchyard tonight.', ['watch'], 'more'),
    ('The reeve\'s seal', 'human village town', 'reeve', 'The reeve\'s seal is gone, and without it no tax can be '
     'sealed and the lord will think we cheat him. It was last seen with a pedlar who went down into the ruins.',
     ['find:the reeve\'s seal', 'seat'], 'sold'),
    ('Bread for the sick house', 'human town city', 'baker', 'The sick house on the hill has no bread. Grain, two '
     'sacks, and I will bake for them for a month.', ['bring:grain:2'], None),
    ('Wool for the orphans', 'human town city winter', 'weaver', 'The orphans at the temple have no blankets. Bring '
     'wool and I will weave them.', ['bring:wool:2'], None),
    ('The carter\'s debt', 'human village town', 'carter', 'I owe a man in the next town, and he will take my horse. '
     'Take him this word: I will pay at harvest.', ['go:the moneylender'], 'danger'),
    ('A song for the dead', 'human village', 'priest', 'Old Wat died, and wanted to be buried with the song of his '
     'own village. Only his sister knows it. She lives in the next town.', ['go:Wat\'s sister'], 'late'),
    ('The watchman\'s shame', 'human town city', 'guard', 'I slept on watch, and something got in. If I kill it, '
     'nobody need know.', ['kill'], 'wrong'),
    ('Ale for the harvest', 'human halfling village summer autumn', 'inn', 'The harvest hands drink like fish, and '
     'my barrels are dry. Three barrels and the harvest is saved.', ['bring:ale:3'], None),
    ('The miller\'s wheel', 'human halfling village', 'miller', 'The wheel cracked, and the mill is still. Timber, '
     'good oak, and the village eats again.', ['bring:timber:2'], None),
    ('The boy in the ruin', 'human village town', 'reeve', 'My son went to the ruins on a dare. He has not come '
     'back. Please.', ['find:a boy\'s wooden sword'], 'captive'),
    ('The levy letter', 'human village town', 'reeve', 'My son marched with the levy. Take him his mother\'s '
     'letter, and tell me he lives.', ['seat'], 'weather'),
    ('The thing in the well', 'human village', 'herb', 'The well tastes of iron and rot. Something died down there, or '
     'something lives. The healer in town knows the herbs to clean it.', ['go:the healer', 'bring:herbs:1'], None),
    ('Fish for the feast', 'human village harbour', 'fisher', 'The feast is near, and the fish will not bite. A '
     'basket of fish from the market will do, and nobody need know.', ['bring:fish:2'], 'opposite'),
    ('The broken plough', 'human hamlet village spring', 'reeve', 'The plough broke on a stone. Tools, and we sow '
     'this spring after all.', ['bring:tools:1'], None),
    ('The knight\'s horse', 'human town city', 'guard', 'A knight\'s horse ran from the stables on my watch. Beasts '
     'took it out past the fields. Bring back what is left of the saddle at least.', ['kill'], 'rival'),
    ('A cradle for the twins', 'human village town', 'carter', 'Twins! And no cradle. Good timber and I will make '
     'one.', ['bring:timber:1'], None),
    ('The old map', 'human town city', 'carter', 'My father drew a map before he died, of a place under the hills. '
     'Go and see if it is true.', ['find:a box of old coins'], 'hidden'),
    ('Honey for the abbey', 'human village temple', 'priest', 'The bees died in the cold. Without honey there is no '
     'wax, and without wax no candles for the dead.', ['bring:honey:2'], None),
    ('The stolen ox', 'human hamlet village', 'shepherd', 'My ox is gone. The tracks lead to the woods, and there '
     'are bones there already.', ['kill'], 'young'),
    ('The healer\'s rival', 'human town city', 'herb', 'A quack sells poison as medicine at the market. Bring me '
     'real medicine to give away, and folk will see the difference.', ['bring:medicine:2'], 'opposite'),
    ('The inn sign', 'human village town', 'inn', 'Somebody stole our inn sign, the Golden Goose. The young bloods '
     'of the next town, I would wager. Go and ask their reeve.', ['go:the reeve'], 'wrong'),
    ('A fur for grandmother', 'human hamlet village winter', 'hunter', 'Grandmother shivers all night. A good fur, '
     'that is all.', ['bring:furs:1'], None),
    ('The drowned bell', 'human town harbour', 'priest', 'The harbour bell fell in the storm. Without it, ships '
     'miss the rocks. A diver says the sea dragged it to a cave nearby.', ['find:the harbour bell\'s clapper'], 'hidden'),
    ('The swan maiden', 'human village', 'fisher', 'A white swan comes to the mill-pond at dusk, and my son '
     'follows it. Kill the thing on the moor that hunts it, and maybe it will stay.', ['kill'], 'bewitched'),
    ('The dowry chest', 'human village town', 'weaver', 'My daughter\'s dowry chest was taken on the road. Thieves '
     'or beasts, I do not know. It went down into the old place.', ['find:a painted dowry chest'], 'rival'),
    ('Spice for the lord', 'human town city', 'cook', 'The lord dines here tomorrow, and I have no spice. None!',
     ['bring:spice:1'], None),
    ('The ferryman\'s son', 'human village town', 'fisher', 'My son poles the ferry now, and something in the river '
     'pulls at the rope at night. Watch the landing with me.', ['watch'], 'child'),
    ('The cracked anvil', 'human dwarf village town', 'smith', 'My anvil cracked in the cold. Ore enough for a new '
     'face, and I work again.', ['bring:ore:3'], None),
    ('The lost will', 'human town city', 'reeve', 'My uncle\'s will was sent to his lawyer in the next town and '
     'never came. Go and ask.', ['go:the lawyer'], 'liar'),
    ('A grave in the woods', 'human village', 'herb', 'My husband died in the woods, and I never found him. The '
     'beasts there know where. Kill them, and look.', ['kill', 'find:a man\'s wedding ring'], 'late'),
    ('The scarecrow', 'human hamlet village summer', 'shepherd', 'The scarecrow moves. I swear it moves. Keep watch '
     'one night and tell me I am mad.', ['watch'], 'more'),
    ('The cold forge', 'human village winter', 'smith', 'No charcoal, no fire, no work. Timber for the kiln, two '
     'loads.', ['bring:timber:2'], None),
    ('The bridge troll', 'human village town', 'carter', 'Something lives under the old bridge and wants a toll. '
     'Last week it took my mule.', ['kill'], 'sick'),
    ('The pilgrim\'s staff', 'human town temple', 'priest', 'A pilgrim died here and asked that his staff go back to '
     'his own temple, in the next town.', ['go:the pilgrim\'s abbot'], 'weather'),
    ('The lady\'s glove', 'human town city', 'guard', 'The lord\'s daughter lost a glove in the ruins, on a ride '
     'she should never have made. Find it before her father asks.', ['find:a lady\'s riding glove'], 'opposite'),
    ('Salt for the sea-folk', 'human town harbour', 'sailor', 'We owe the salt-makers up the coast. Take them our '
     'word, and bring back two loads.', ['go:the salt-makers', 'bring:salt:2'], None),
    ('The weeping stone', 'human village', 'priest', 'The standing stone weeps red since the war. Hallow it: find '
     'the stone\'s old charm in the barrow and bring it back.', ['find:a stone charm'], 'cursed'),
    ('The pie for the next hill', 'halfling', 'baker', 'There is a feast in the next hill and I promised my pie. My '
     'oven broke. Cook something, anything warm, and carry word I am not coming myself.', ['dish', 'go:my aunt'], None),
    ('Granny\'s recipes', 'halfling', 'baker', 'Granny lent her book of recipes to a cousin, and the cousin took the '
     'wrong road. Ninety years of pies, in some hole!', ['find:Granny\'s book of recipes'], 'sold'),
    ('The missing smial key', 'halfling hamlet village', 'reeve', 'The key to the old smial is lost, and the will '
     'is inside. My nephew had it last, in the next hill.', ['go:my nephew'], 'liar'),
    ('Mushrooms at midnight', 'halfling gnome', 'herb', 'The best mushrooms grow by the old stones, and something '
     'eats them before I can. Watch with me.', ['watch'], 'child'),
    ('The best pipe-weed', 'halfling village town', 'inn', 'My best pipe-weed went with a trader, and I want it back. '
     'He went under the hill, the fool.', ['find:a jar of pipe-weed'], 'rival'),
    ('Second breakfast', 'halfling', 'cook', 'A guest is coming for second breakfast and I have nothing. A warm dish '
     'and honey, quickly!', ['dish', 'bring:honey:1'], None),
    ('The bounder\'s horn', 'halfling', 'guard', 'The bounders lost their horn on the border, and wolves are near. '
     'Kill the wolves and look for the horn where they lair.', ['kill'], 'young'),
    ('The hedge that grew', 'halfling village', 'herb', 'The hedge grows over the lane in one night, twice now. My '
     'cousin in the next hill knows hedge-craft.', ['go:my cousin'], 'bewitched'),
    ('Apples for the fair', 'halfling village autumn', 'baker', 'The orchard failed, and the fair is coming. Fruit, '
     'two baskets!', ['bring:fruit:2'], None),
    ('The quilt of names', 'halfling', 'weaver', 'Every family\'s name is stitched on our quilt, and it is not '
     'finished without the far-cousins. Carry it to them to stitch.', ['go:the far-cousins'], 'stay'),
    ('A line in the grudge-book', 'dwarf', 'priest', 'There is a line in the grudge-book with my grandfather\'s name on '
     'it, and the beast that made it still walks. Strike it out.', ['hunt'], 'more'),
    ('The grandson in the mine', 'dwarf', 'miner', 'My grandson went down into the old workings. We found his '
     'tracks, nothing more.', ['find:a miner\'s lamp with a name on it'], 'captive'),
    ('The ale of the hold', 'dwarf', 'inn', 'Our brew-stone cracked, and the hold has no ale. Bring ale from the '
     'surface, three barrels, and they will sing of you.', ['bring:ale:3'], None),
    ('The lost runes', 'dwarf', 'priest', 'A rune-stone of our fathers was carried off by goblins. It lies in their '
     'hole, if it lies anywhere.', ['clear'], 'hidden'),
    ('Ore from the old seam', 'dwarf deephold', 'smith', 'The good seam ran out. There is ore in the markets above, '
     'poor stuff, but it will do.', ['bring:ore:3'], None),
    ('The beard-oath', 'dwarf', 'guard', 'I swore on my beard to kill the thing that killed my brother. My beard '
     'grows grey. Help me.', ['kill'], 'worse'),
    ('A word to the cousins', 'dwarf', 'reeve', 'Our cousins in another hold owe us a cart of tools. Remind them.',
     ['go:the hold-lord\'s steward', 'bring:tools:1'], 'opposite'),
    ('The sealed door', 'dwarf deephold', 'miner', 'A door opened in the deep, a door that was sealed by our king. '
     'What came out must go back.', ['clear'], 'young'),
    ('The singing anvil', 'dwarf', 'smith', 'My anvil sang when my master died. Now it is silent. His hammer lies '
     'in the old forge-hall, they say.', ['find:a master\'s hammer'], 'cursed'),
    ('The cart-line', 'dwarf deephold', 'carter', 'Something gnaws the cart-line\'s ropes at night. Watch the '
     'cart-head with me.', ['watch'], 'wrong'),
    ('The sick tree', 'elf', 'herb', 'The old tree by the pool is sick. The bark weeps. Herbs, and a song, and '
     'maybe it lives.', ['bring:herbs:2'], None),
    ('The taken song', 'elf', 'priest', 'A song of ours was taken to a human town long ago. Tell the keeper there we '
     'would have it back.', ['go:the keeper of songs'], 'liar'),
    ('The white hart', 'elf', 'hunter', 'The white hart is hunted by something that is not a hunter. Kill it before '
     'the hart is gone.', ['kill'], 'bewitched'),
    ('Moon-silver', 'elf', 'weaver', 'For the moon-cloak I need silver thread, and the silver is in a barrow the '
     'humans robbed.', ['find:a coil of moon-silver'], 'cursed'),
    ('The archer\'s debt', 'elf', 'guard', 'I owe a life to a human in the next town. Take him this arrow; he will '
     'know.', ['go:an old forester'], 'late'),
    ('The cold glade', 'elf winter', 'herb', 'The glade freezes, and the young ones sicken. Furs, from the humans\' '
     'markets. Do not tell the elders I asked.', ['bring:furs:2'], None),
    ('The grove watch', 'elf', 'guard', 'Axes in the night, at the edge of the glade. Watch with me.', ['watch'],
     'child'),
    ('The missing part', 'gnome', 'tinker', 'My self-turning spit lacks one part. Good tools and I can make it.',
     ['bring:tools:1'], None),
    ('The rival\'s cog', 'gnome', 'tinker', 'A rival stole my best cog and dropped it running away, into a hole. Get '
     'it before he does!', ['find:a cog of brass'], 'rival'),
    ('The gem that hums', 'gnome', 'miner', 'A gem I cut hums at night, and the burrow cannot sleep. Take it to a '
     'temple, or take it far away.', ['go:a priest'], 'cursed'),
    ('Mushrooms for the burrow', 'gnome', 'herb', 'The mushroom beds are bare and the burrow hungry. Grain from the '
     'big folk will do, two sacks.', ['bring:grain:2'], None),
    ('The tunnel thief', 'gnome', 'reeve', 'Something takes our tools from the tunnels at night. Watch the deep '
     'tunnel with me.', ['watch'], 'child'),
    ('A flying machine', 'gnome', 'tinker', 'My flying machine needs cloth for the wings! Cloth, three bolts, and '
     'history is made.', ['bring:cloth:3'], 'opposite'),
    ('A brother in the cell', 'orc', 'guard', 'They call my brother a thief in the next town. He is not. Tell the '
     'reeve there what I tell you.', ['go:the reeve'], 'wrong'),
    ('Work for a half-orc', 'orc town city', 'carter', 'Nobody gives a half-orc work but the dangerous kind. Beasts '
     'took my cart. Help me, and I am in your debt.', ['kill'], 'rival'),
    ('The clean name', 'orc town city', 'smith', 'My father was hanged for a deed he did not do. The proof lies with '
     'the lord. Take my word to him.', ['seat'], 'danger'),
    ('The boar of the hills', 'orc', 'hunter', 'The great boar killed my hunting brother. His tusks belong on my '
     'wall.', ['hunt'], 'sick'),
    ('A blade for the sparring', 'orc', 'guard', 'Our blades are rust and pride. Arms, two loads, and the young ones '
     'learn properly.', ['bring:arms:2'], None),
    ('The bone-setter\'s herbs', 'orc', 'herb', 'Too many broken bones this season. Herbs for poultices.',
     ['bring:herbs:2'], None),
    ('Shiny for the hoard', 'kobold', 'miner', 'Shiny! The chief wants shiny, and I have none. Bring a gem.',
     ['bring:gems:1'], 'opposite'),
    ('The boss\'s fear', 'goblin', 'carter', 'The boss beats me when the hunt goes wrong. Kill what eats our '
     'hunters and I say I did.', ['kill'], 'worse'),
    ('The speckled egg', 'lizard', 'priest', 'An egg of our clutch was taken. The thief fled into a hole. It must '
     'come home warm.', ['find:an egg of speckled green'], 'captive'),
    ('A net for the eel-run', 'lizard', 'fisher', 'The eel-run is coming and our nets rotted. Cloth and cord.',
     ['bring:cloth:2'], None),
    ('The beacon', 'human town harbour', 'sailor', 'The beacon on the point went out, and nobody will go up there: '
     'something lives in the old tower now.', ['kill'], 'hidden'),
    ('The pressed men', 'human town city harbour', 'sailor', 'A captain pressed my son onto his ship. The lord of the '
     'coast can free him with a word.', ['seat'], 'stay'),
    ('The cook\'s revenge', 'human city metropolis', 'cook', 'A rival cook spread word that my pies are rat. Make a '
     'dish to set before the guild, and we shall see.', ['dish'], 'opposite'),
    ('The midwife', 'human village hamlet', 'herb', 'A baby comes too early in the next village and the midwife '
     'there is sick. Medicine, and tell them I am coming.', ['bring:medicine:1', 'go:the mother'], 'late'),
    ('The scholar\'s book', 'human city metropolis', 'reeve', 'A scholar left a book of mine in a ruin. A rare book. '
     'He says it is still there, on a lectern.', ['find:a book bound in green'], 'sold'),
    ('The gallows', 'human town city', 'guard', 'A man hangs tomorrow, and I think he is innocent. The one who saw '
     'it lives in the next town.', ['go:the witness'], 'wrong'),
    ('The empty larder', 'human hamlet village winter', 'baker', 'It is a long winter and the larder is bare. Grain, '
     'and we live till spring.', ['bring:grain:3'], None),
    ('The swarm', 'human halfling village summer', 'herb', 'The bees swarmed into the old ruin. Where the bees go, '
     'the honey goes. Bring the queen\'s comb back.', ['find:a comb of wild honey'], 'young'),
    ('The cursed coin', 'human town', 'inn', 'A stranger paid with a black coin, and since then the beer sours. Take '
     'it to a temple.', ['go:a priest'], 'cursed'),
    ('The wolf-mother', 'human village winter', 'shepherd', 'A she-wolf takes a lamb every night. I have no heart to '
     'kill a mother, but I must.', ['kill'], 'young'),
    ('The last of the line', 'human village town', 'reeve', 'An old knight\'s house died out, and the land falls to '
     'the lord. Take him the last knight\'s ring.', ['find:a knight\'s signet', 'seat'], 'liar'),
    ('Ice for the larder', 'human town summer', 'cook', 'The heat spoils the meat. Ice, from the north, before the '
     'feast.', ['bring:ice:1'], None),
    ('The shrine thief', 'human village temple', 'priest', 'The offering bowl is stolen, every week. Keep watch at '
     'the shrine.', ['watch'], 'child'),
    ('The haunted barn', 'human hamlet village', 'shepherd', 'Lights in the old barn, and the cattle will not go '
     'near it. Keep watch.', ['watch'], 'more'),
    ('A mother\'s locket', 'human village town', 'weaver', 'My mother\'s locket was buried with her, and robbers '
     'opened the grave. They went to the ruins.', ['find:a silver locket'], 'liar'),
    ('Arms for the militia', 'human village town', 'guard', 'Raiders on the roads, and the militia drills with '
     'sticks. Arms, two loads.', ['bring:arms:2'], None),
    ('The poisoned stream', 'human village', 'fisher', 'The fish float belly-up. Something poisons the stream from '
     'its nest upriver.', ['clear'], 'worse'),
    ('The ghost at the crossing', 'human village', 'carter', 'A ghost stands at the crossing and stops the carts. '
     'It asks for its brother in the next town. Take him word.', ['go:the ghost\'s brother'], 'late'),
    ('The runaway apprentice', 'human town city', 'smith', 'My apprentice ran off to the next town with my best '
     'tongs. Bring him back, or the tongs.', ['go:my apprentice'], 'stay'),
    ('Wine for the vows', 'human town temple', 'priest', 'A wedding at the temple, and the altar wine has turned. '
     'Wine, one cask.', ['bring:wine:1'], None),
    ('The giant\'s tooth', 'human village', 'herb', 'A giant\'s tooth cures the fever, everyone knows. There is a '
     'giant thing in the hills.', ['hunt'], 'sick'),
    ('The salt road', 'human village town', 'carter', 'The salt road is closed by beasts. Clear it and the village '
     'can trade again.', ['kill', 'bring:salt:1'], 'rival'),
    ('A bed for a stranger', 'human halfling village town', 'inn', 'A stranger fell at my door, half dead. He asks '
     'for his sister in the next town.', ['go:his sister'], 'danger'),
    ('The green knight\'s challenge', 'human town city', 'guard', 'A knight in green armour challenges all comers '
     'at the crossroads, and nobody beats him. Our lord\'s honour asks for a champion.', ['hunt'], 'bewitched'),
    ('The lantern-men', 'human village', 'fisher', 'Lights over the marsh lead folk astray. My brother followed '
     'them. Watch the marsh with me.', ['watch'], 'late'),
    ('The cooper\'s oak', 'human village town', 'carter', 'The cooper needs oak for barrels, and the oak wood is full '
     'of beasts.', ['kill', 'bring:timber:1'], None),
    ('Medicine for the cough', 'human dwarf halfling', 'herb', 'The cough goes through the street like fire. '
     'Medicine, two jars.', ['bring:medicine:2'], None),
    ('The lord\'s hound', 'human town city', 'hunter', 'The lord\'s best hound ran after a stag and never came back. '
     'Beasts got it, or worse.', ['kill'], 'young'),
    ('The flood stone', 'human village spring', 'reeve', 'The river rises every spring since the flood stone was '
     'stolen. It lies in the ruins downriver.', ['find:a carved flood stone'], 'hidden'),
    ('The tinker\'s cart', 'human gnome village town', 'tinker', 'Robbers took my cart into their hole, with all '
     'my wares.', ['clear'], 'captive'),
    ('A coat of feathers', 'human village', 'weaver', 'I wove a coat of feathers, and my daughter flew away in it. '
     'I am not mad. Find her in the next town.', ['go:my daughter'], 'bewitched'),
    ('The old soldier', 'human village town', 'guard', 'An old soldier in the lane lost his medal in the war. The '
     'battlefield ruin still has its dead.', ['find:a soldier\'s medal'], 'late'),
    ('The bridge toll', 'human orc town', 'carter', 'The lord set a new toll on the bridge, and we cannot pay. Take '
     'our word to his hall.', ['seat'], 'opposite'),
    ('The baker\'s oven', 'human halfling town city', 'baker', 'My oven cracked in the frost. Ore for the iron door, '
     'and timber for the frame.', ['bring:ore:1', 'bring:timber:1'], None),
    ('The cat\'s king', 'human halfling village', 'inn', 'The cats of the village gather every night at the old '
     'stone. Watch, and tell me why.', ['watch'], 'more'),
    ('The lost pilgrims', 'human dwarf town temple', 'priest', 'Pilgrims went to the old shrine under the hills and '
     'never came out.', ['find:a pilgrim\'s badge'], 'captive'),
    ('A bride for the miller', 'human halfling village', 'miller', 'The miller loves a girl in the next town, and '
     'is too shy to say. Carry his word, and a gift of honey.', ['bring:honey:1', 'go:the girl'], 'stay'),
    ('The beehives', 'human halfling hamlet village', 'shepherd', 'Something smashes the beehives for the honey. Big '
     'paws.', ['kill'], 'sick'),
    ('The deep well', 'dwarf gnome', 'miner', 'A deep well went dry, and in the dry well there is a door. Find what '
     'is behind it.', ['find:an old dwarven key'], 'hidden'),
    ('The thief-taker', 'human city metropolis', 'guard', 'A thief works the market every day and I never catch him. '
     'Watch with me.', ['watch'], 'child'),
]
