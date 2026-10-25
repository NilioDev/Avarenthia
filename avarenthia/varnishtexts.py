"""The words of the Varnish (round 12): loose fragments of the Empire, the books that lie in pieces across the world
and the five old riddles. Pure data; varnish.py puts them in the world and in the chronicle.

The Varnish counted their years from the Founding (FF); the Empire lasted 1400 years, and the Ruin fell in 1400 FF,
in the thirteenth month, Vaelmoon. Today's gods are the worn-down remains of theirs."""

# ------------------------------------------------------------------ loose fragments, by heading of the chronicle
FRAGS = {
    'Gods': [
        'Sol-Amarath, who lights the count of days: "Every dawn she counts us, and finds none missing." The Solmara of '
        'today is what is left of her.',
        'Eskelion, Measurer of Roads: "No road is laid that he has not walked first." He carried a measuring rod, not a '
        'staff. The grey wanderer Skell was once the surveyor.',
        'Valdrecht, who weighs: in every court of law hung his scales of black iron.',
        'Thessaly of the Sown Field had no temples, only fields: "Her temple is any field with a stone at its corner."',
        'Durnak is in no Varnish text at all. The dwarves say: "We did not lend them our god."',
        'The Counted Sky: no god with a face, but the stars themselves, each star a name and a number. Its priests were '
        'called tellers.',
        'Aerith of the Four Winds: on later stones she stands in chains; on older ones she is free. Someone bound her.',
        '"Count the stars before you sleep, child. If one is missing, wake your father."',
        '"Eskelion\'s mile is a thousand paces of a tired man. Do not argue with a god about his paces."',
        'A prayer on a sherd: "Sol-Amarath, I have done no great thing today. Count me anyway."',
        'A children\'s riddle: "What has a thousand names and no face?" The answer is the sky.',
    ],
    'The emperors': [
        'Fifty emperors in fourteen hundred years. Of most of them only a byname is known.',
        'Aes the Founder "measured the first league with his own feet, and rested at the end of it, and called the '
        'resting place the Empire."',
        'Caelum the Surveyor had every road in the Empire walked twice, "once to lay it, once to check it."',
        'Oros the Kind, of whom nothing bad is written, "which is why we know nothing of him."',
        'Taur the Short was emperor for nine days. His coins are the rarest in the world.',
        'Vess the Thrice-Crowned was deposed twice and crowned three times. "He was patient. The Empire was not."',
        'Mor the Silent spoke only through his scribes for thirty years. Some say he was dead for the last ten.',
        'Halun the Builder of Glass raised the upper Sky-Seat. "He wanted to see the stars closer. He did."',
        'Domna was the only empress who ruled alone. Her law of the open roads still stands in every realm, unread.',
        'Serrat the Last took the winds from the farms. His name is scratched off more stones than it is on.',
    ],
    'Daily life': [
        'A wax tablet, a shopping list: "Lamp oil. Two eels. Figs if Hessa has them. A new strap for the boy\'s sandal, '
        'AGAIN."',
        'A baker\'s stamp, pressed into every loaf: "Varro\'s. Weighed true."',
        'On a tavern wall: "Lucan owes me four coppers and a song. He knows which song."',
        'A dog\'s collar of bronze: "I am Bramble. I belong to the house of Ennis. If I am lost, I am also hungry."',
        'A list of household rules: "No wind-binding in the kitchen. No raising the dead in the kitchen. Ask your father '
        'why."',
        'A recipe: "Eels in honey and fish sauce, with leek. If you have no eels, you have no dinner."',
        'Sky bread: a flat loaf stamped with a star, baked on the longest night. Bakers in the north still make it and do '
        'not know why.',
        'On a wine jar: "From the slopes of Ithil. Year 1211 FF. A good year. Drink it before the next bad one."',
        'A soldier\'s ration list: "Hard bread, hard cheese, hard luck."',
        '"Never eat at an inn where the dead serve. They do not taste the food, and it shows."',
        'A feast menu for an emperor: "dormice in poppy seed, a peacock in its feathers, a swan in a goose in a duck, '
        'and for the guests from the provinces, bread."',
        'The Counting, at midwinter: every household counted its people and its stars. Whoever was missing was named '
        'aloud.',
        'Standing Night: the dead were brought out of their niches and stood in the streets, and the living walked among '
        'them and told them the news.',
        '"On the Day of Leagues every child walks one league with their father, and is given a pebble from the end of '
        'it."',
        'The Varnish had thirteen months, after the stars. A calendar in a library says: "There is no thirteenth month." '
        'An older one says: "In Vaelmoon we do not build."',
        '"For a cough: honey, onion, and patience. For a broken heart: the same."',
        'A surgeon\'s note: "Removed: one arrow, one tooth, one superstition. The patient will live; the superstition '
        'may come back."',
        'Leagues: a board game of roads and milestones; whoever reaches the Sky-Seat first wins. Pieces of it turn up in '
        'every ruin.',
        'On a ring: "Count on me."',
        'A gravestone for two: "They argued for fifty years and were buried together so they could go on."',
        '"Mother, the boy you warned me about is very kind and owns a vineyard. I am marrying him. You were wrong. '
        'Love, Hessa."',
    ],
    'Law and measure': [
        '"A league is a league in every province. Whoever shortens a league shortens the Empire."',
        '"The penalty for a false weight: the weight, hung about the neck, for a year."',
        '"No man may own a road. The road owns itself, and lends itself to all."',
        '"A citizen is one who has been counted. Count the newborn on the seventh day."',
        '"A coin is a promise from the Emperor. The bronze is only there to remind you."',
        '"Every province pays in what it has: the coast in fish, the hills in wool, the north in men."',
        '"A debt may not outlive the debtor. A grudge may." The dwarves like to quote it.',
        'A will: "To my son, the house. To my daughter, the house\'s debts, because she is the one who can pay them."',
        'A tablet of curses, thrown in a well: "Whoever stole my cloak at the baths: may your winds go still and your '
        'dead lie down."',
    ],
    'Mages and the binding': [
        '"First year: you learn the names of the winds. Second year: you learn they do not like their names. Third '
        'year: you learn to say them anyway."',
        'From a school\'s rules: "A student who binds a wind without a master present will be bound himself, to the '
        'library, for a season."',
        'A complaint to the Collegium: "The wind bound to my mill was released by your students as a prank. It is now '
        'in my house. It will not leave."',
        '"A bound dead man may carry, dig, row and stand guard. He may not cook. We have tried. Do not try."',
        '"Every bound dead man must wear the seal of the house that bound him, and the year. Unsealed dead are to be '
        'laid down at once."',
        '"The old masters asked the winds. The new masters tell them. I have heard the winds answer the old way and not '
        'the new."',
        'An exam question, on a tablet: "Explain why the dead should not be bound to their own graves. Give three '
        'reasons. (The third is the important one.)"',
        '"Do not let a bound wind into a sickroom. It carries the sickness further and it does not care."',
        'A mage\'s note: "The dead do what they are told. That is not the same as wanting to. I have stopped asking them '
        'what they want. They tell me."',
        'The first star-iron: "A star fell in the hills in the year 990 FF. The iron in it would not rust and would not '
        'cool. The smiths still say it hums."',
    ],
    'Songs and books': [
        'A love poem on a sherd: "I would bind the wind for you, if they let poets bind the wind. / They do not. So I '
        'send you this sherd instead, and it is only clay, and it is everything."',
        'A comedy, a scrap: "Enter the Tax Counter. Exit everyone else."',
        'A proverb: "Build as if the Empire will last. Bury as if it will not."',
        'A proverb: "Glass on the top, bronze in the middle, mud at the bottom. That is the Sky-Seat, and that is the '
        'world."',
        'Ithila the Younger, A History of the Provinces, the first line: "Every province says it joined the Empire '
        'willingly. This history will be short."',
        'The Comedy of the Two Milestones: two milestones argue for five acts about which of them is right. At the end '
        'the road is moved.',
        'A philosopher\'s last words, according to his students: "Count me." According to his wife: "Shut the window."',
        'Varro, Letters from the Provinces: "The people here have three words for rain and none for \'tax\'. I am '
        'teaching them."',
    ],
    'Soldiers and the wall': [
        'A legion\'s order: "Spears sharp, boots dry, mouths shut."',
        'A soldier\'s will: "My spear to my brother, my boots to whoever is cold, my debts to the Emperor."',
        '"If the north ever sends anything, light the beacons. If the beacons are lit, do not ask why. Run to the wall."',
        'A punishment list: "Sleeping on watch: the wall, a month, alone. Gambling on watch: the same, but with '
        'company."',
        'Written on the Northern Wall, many hands: "Day 1. Day 2. Day 3." It goes on for a long stretch of stone. It '
        'ends at Day 3,651.',
    ],
    'Trades and the sea': [
        '"The Guild of Road-Wardens: we walk so you need not."',
        'A glassblower\'s mark: a small eye. "If you can see through it, it is ours."',
        'A milestone cutter\'s apprentice, on the back of a stone: "This one is wrong. I have cut it backwards. Bury it '
        'face down."',
        '"Bronze-founders, the Street of: keep your doors shut. Your noise is a nuisance and your heat is worse. By '
        'order."',
        'The tellers, the star-priests, were also the Empire\'s clerks: "To count the sky is to count everything."',
        '"Ships of the Empire are painted with an eye at the bow. A ship that cannot see cannot go home."',
        '"The winds bound to the fleet are the oldest and the angriest. Do not whistle on board."',
        'A sailor\'s song: "Bronze on the mast and the wind in the jar, / and the Sky-Seat behind us, and home very far."',
        'A harbour sign: "No dead to be landed here without a seal. No live ones without a fee."',
    ],
    'Voices': [
        'On a milestone, scratched: "Gaius walked this. His feet hated it."',
        'A gravestone: "Here stands Ithila, midwife. She brought four hundred into the world and saw none of them leave '
        'it early. Count her."',
        'Under a bridge: "The engineer was right. Nobody listened. The bridge is still here."',
        'Scratched on a seat in a Sky Court: "Blue team is cheating. The wind is bound."',
        '"In the Street of Glass a woman sells bottled moonlight. It is water. It is very good water."',
        '"The statue of Halun in the forum turns its head a little each year. The tellers measured it. They have stopped '
        'measuring it."',
        '"There is a road in the south that no one built. It is straight, it is paved, it is on no map. The '
        'Road-Wardens will not walk it."',
        'A father\'s letter: "I am proud of you for the exam. I am less proud of you for the wind in the kitchen."',
        '"The dwarves have closed their doors. Our envoy knocked for three days. On the fourth, they opened a small '
        'window and said \'No.\'"',
        '"The elves agreed to the treaty, signed it, and then said the forest had not signed it. We are still '
        'discussing this."',
        'A merchant\'s note: "Halflings: will trade anything for pipeweed. Will not trade pipeweed for anything."',
        '"The gnomes do not exist. Report filed. (Something has been eating my report.)"',
        '"Kobolds took the bronze nails out of the eastern bridge one by one. The bridge fell. They were very sorry. '
        'They kept the nails."',
    ],
    'The uncounted': [
        '"A citizen is one who has been counted." Scratched under it, another hand: "And the rest of us are the floor '
        'you stand on."',
        '"The uncounted may not be buried standing. Lay them down, face to the ground, outside the walls."',
        '"The law says a slave may buy himself free for the price paid for him. The law does not say who sets the '
        'wage."',
        'Graffiti in a mine: "Every league of road in this Empire is paved with us."',
        'Scratched on many milestones: a small hand, open. The Road-Wardens were ordered to grind it off. It is on half '
        'the milestones still.',
        '"To the Emperor, from the bakers of the Street of Glass: we will weigh true when you do."',
        'A teller, struck from the rolls: "I have counted the stars for forty years. I will not count men to sell them."',
        'An inn sign: "Good beds. Clean dead. No uncounted."',
        '"I do not ask where the bronze comes from. I cast it."',
        '"Yes, it is a shame about the coast. Have you tried the eels in honey?"',
        'A wife to her husband: "You were at the Counting today. You came home and did not speak. Next time, do not go."',
        '"They took the neighbours on Restday. We kept the shutters closed. It was a quiet day after that."',
    ],
    'The bound dead': [
        'A mage, defending it: "Would you rather the living dug the mines? The dead feel no cold. Be grateful, and pay '
        'your tax."',
        'A preacher of Sol-Amarath, on a stone broken up and used in a wall: "The dawn counts the living. Who counts the '
        'dead who do not rest?"',
        '"Buy dead, sell work. The surest trade in the Empire." A merchant\'s motto, on his seal.',
    ],
    'Conquest': [
        'A list of a province\'s tribute: "Fish, wool, salt, forty young men a year for the legions, and silence."',
        'An old woman\'s song from the west, written down by a Varnish scholar who found it charming: "They came with '
        'straight roads / and a straight line through my village / and a straight line through my son."',
        '"The elves\' wood is to be cleared for the road. The elves object. The road does not." The quarrel at the edge '
        'of the wood began here.',
        '"Since the Counting I have never had a bad year. Taxes are certain, and so is my share of them." A tax farmer.',
        'A senator: "The poor complain of the roads. The roads bring them bread. Ingratitude is the only thing in the '
        'Empire that has no tax."',
        'Ithila the Younger again: "It is short because the long version was burned."',
    ],
    'The last days': [
        '"They have taken the winds off the farms and given them to the Sky-Seat. The fields are still. The sails are '
        'still."',
        '"The Emperor has ordered the Counting held twice this year. Nobody knows what he hopes to find."',
        '"The farms are still. No wind. The harvest rots in the field. The Sky-Seat has every wind in the world, and it '
        'is cold up there."',
        '"Tonight the tellers did not come down from the tower. Their lamps are lit. Nobody answers."',
        'On the last page of a Book of Leagues: "At the last league there is nothing. Go back."',
    ],
    'Why it fell': [
        'A priest: "Because it bound what should have rested."',
        'A mage: "Because the Emperor was greedy and took every wind. The binding was never the fault."',
        'A slave: "It did not fall. It stopped. For us it stopped."',
        'An elf, long after: "Your Empire was a long noise. Then it was quiet. We liked the quiet."',
        'A dwarf: "We wrote it down in the Grudge Book. The page is still open."',
    ],
}
HEADS = list(FRAGS) + ['Pages that belong together', 'Bound books']

# ------------------------------------------------------------------ the books in pieces
# where: the kinds of place a page may lie (varnish.py turns them into real places of this world)
THREADS = {'tam': 'Tam and his mother', 'winds': 'the winds', 'fall': 'the fall', 'uncounted': 'the uncounted',
           'dead': 'the bound dead', 'emperors': 'the emperors'}
BOOKS = [
    dict(key='ninth', title='Letters from the Ninth', thread='tam', noun='letter', where=('walltower',),
         pages=[
             '"Mother, I am on the wall. It is cold and nothing happens. The men call us the Watchers of Nothing. I think '
             'they are proud of it. Send the red socks."',
             '"Mother, the socks came. Do not send Aunt Pell\'s cake again; the men still talk of it. Corin from the next '
             'tower says his mother sends figs. I have told him we are poor. He shares them anyway."',
             '"Mother, today is Day 1,200 on the wall. We scratch them in the stone. Corin says that when we reach Day '
             '3,650 they must let us go home, it is the law. I have looked. It is not the law. I have not told him."',
             '"Mother, the tellers came up from the south to count the stars from our towers. They say the northern sky '
             'is the clearest. One of them asked me which stars were missing. I said none. He wrote something down '
             'anyway."',
             '"Mother, Corin is sick. The surgeon took one arrow and one tooth out of him and says he will live. I have '
             'been doing his watch and mine. I do not mind. Nothing happens."',
             '"Mother, the beacons to the south are lit. All of them. We are facing the wrong way."'],
         hidden='In the spine, in another hand: "Day 3,651. Corin went south to see. I stayed, because someone must '
                'watch the north, and the north has never sent anything. I have scratched the day in the stone. If '
                'someone reads this, I was here. Count me. Tam, of the Ninth."',
         chron='Tam of the Ninth kept watch on the Northern Wall the night the Sky-Seat fell.', effect=('place', 'walltower')),
    dict(key='jar', title='The Wind in the Jar', thread='winds', noun='diary leaf', where=('vcity', 'starhouse'),
         pages=[
             '"Today I bound my first wind. It was very small. It lives in a jar on my desk and rattles the lid when I am '
             'sad. I have called it Pip."',
             '"Father wrote. He is proud of me for the exam. He is less proud of me for the wind in the kitchen. Pip says '
             'nothing. Pip is a wind."',
             '"The Loosing is next week. Every bound wind goes free for a day so it remembers it is a wind. I will open '
             'Pip\'s jar on the roof. I am afraid he will not come back. Master Ennis says that is the point."',
             '"Pip came back. He went round the city three times and knocked every hat off in the Street of Glass, and '
             'then he came back to the jar on his own. Master Ennis was very quiet about it."',
             '"There will be no Loosing this year. By order of the Emperor. The winds are wanted at the Sky-Seat. All of '
             'them. The farm winds too. They came for the jars at the school today. I hid Pip in my boot."',
             '"It is very still everywhere. The windmills do not turn. You can hear people talking three streets away. '
             'Pip rattles the lid all night. I think he can hear the others, up there, and they are not happy."',
             '"I opened the jar. I told him to go north, away from the Sky-Seat, as far as he can. He went. Tonight there '
             'is a new star, very bright, and it is not far away at all."'],
         hidden='Pasted to the cover, in her hand, much later: "I was a mage in a free city for sixty years afterwards. '
                'Every spring, on the day that was the Loosing, a small wind comes in at my window and knocks the cups off '
                'the shelf. I do not bind it. Lessa, once of the Collegium."',
         chron='Under Serrat the Last every bound wind was taken to the Sky-Seat. Not all of them went.', effect=('riddle', 'king', 7)),
    dict(key='leagues', title='The Book of Leagues', thread='fall', noun='leaf', where=('road', 'deserted', 'gate'),
         pages=[
             '"At the first league from the sea there is an inn called the Wet Boot. The name is a warning. The fish is '
             'excellent."',
             '"At the fortieth league there is an inn with good bread and a bad roof. The innkeeper is honest. His '
             'brother is not. They take turns at the door; learn their faces."',
             '"At the hundredth league the road crosses the Ithil on a bridge of eleven arches. The engineer said it '
             'needed twelve. Count them as you cross, and walk quickly over the gap where the twelfth should be."',
             '"At the hundred and sixtieth league is the House of the Standing Host, where the dead serve the tables. The '
             'beds are clean. Do not thank the servers. It confuses them."',
             '"At the two hundredth league you will see the Sky-Seat for the first time, a spark of glass on the cliffs. '
             'Every traveller stops here. The innkeeper charges for the view."',
             '"At the two hundred and twelfth league the winds begin. They come down from the Sky-Seat in bound lanes; '
             'you can see the grass lie flat in a straight line. Do not stand in a lane. Do not pitch a tent in one."',
             '"At the last league is the Sky-Seat itself, and there is no inn, because no one who reaches it wants to '
             'sleep."'],
         hidden='On the inside of the cover, a later hand: "I walked it again, after. The Wet Boot is a ruin and the fish '
                'is still excellent. At the two hundred and twelfth league the grass still lies flat in a line, though '
                'there is no wind. I did not go to the last league. Varro\'s son."',
         chron='The old road of the Book of Leagues still runs across the land.', effect=('way',)),
    dict(key='walls', title='The Song of the Nine Walls', thread='fall', noun='canto', where=('walltower',),
         pages=[
             'The First, the Founders\' Spears: "They came first and built the first stone, / and set their spears in it, '
             'and were not sent home."',
             'The Second, the Salt-Eaters: "Their bread came over the sea and came wet, / so they ate it with salt and '
             'called it a feast."',
             'The Third, the Lantern-Bearers: "They lit a lamp on every tower at dusk / so the north might know the '
             'Empire was awake."',
             'The Fourth, the Silent: "Of the Fourth nothing is sung. / They did not want it."',
             'The Fifth, the Horse-Wardens: "Their horses grew old with them, and were buried / standing, as men are, the '
             'only horses so."',
             'The Sixth, the Builders: "They raised the wall a hand\'s breadth every year / for a hundred years, and then '
             'were told to stop."',
             'The Seventh, the Counters: "They counted the days in the stone, and the stars, / and when a star went out '
             'they said nothing."',
             'The Eighth, the Last Called: "They were boys when they came, the last ones called. / They were boys when it '
             'ended."',
             'The Ninth, the Watchers of Nothing, in another measure, short and halting: "And in the ninth year of the '
             'last emperor / the north sent something. / It was us. / We had been sent there, the uncounted, a thousand '
             'years ago, / and now we came back."'],
         hidden='"The ninth canto was written by a man of the north, in our tongue, badly. He asked me to put it with the '
                'others. He said the song was not finished until someone on the other side had sung." A scribe of the '
                'Wall, the year of the Ruin.',
         chron='On the night the Sky-Seat fell, the north did come over the wall, and they were not barbarians. They were '
               'the children of those the Empire had sent away.', effect=None),
    dict(key='hessa', title="Hessa's Kitchen", thread='tam', noun='recipe', where=('vcity', 'deserted'),
         pages=[
             '"Figs in honey. Mother\'s way. Do not let the honey boil or it turns bitter, like Mother when the honey '
             'boils."',
             '"Wedding bread, for a hundred guests. I made it for sixty. Forty were Aunt Pell\'s relatives and did not '
             'need feeding."',
             '"Grape must cake. Brennus says it is the best thing I make. Brennus says that about everything I make. I '
             'married well."',
             '"Porridge for a teething baby. Also for a teething husband: Brennus has lost a tooth at the vineyard. He '
             'says it was a stone in the bread. It was not my bread."',
             '"Soldier\'s bread, to send north. My boy is on the wall. Hard, so it travels. The rich mothers send jars of '
             'figs. I put one fig in the middle of each loaf. He will know."',
             '"There is no eel this year. There is no wind for the boats. Leek soup, then. Leek soup again."',
             '"Funeral cakes. Brennus. Small, round, with a star stamped on. I do not want him bound. I have paid the '
             'priest to lay him down."',
             '"For one person: whatever is left. Eat it at the window."'],
         hidden='In the cover, from her son: "Mother\'s bread came every winter on the wall, one fig in each loaf. Corin\'s '
                'mother sent jars; the men fought for ours. I have written down her last recipe, which she never wrote: '
                '\'Bread with a fig in it, for anyone who is far from home.\' Tam."',
         chron='Hessa of the kitchen was the mother of Tam of the Ninth.', effect=('recipe', 'fig_bread')),
    dict(key='court', title='The Court Sends for the Wind', thread='winds', noun='leaf', where=('vcity', 'library'),
         pages=[
             '"The farmer Bram says the wind was bound against his field, so that his wheat lay flat and the '
             'magistrate\'s did not."',
             '"The mage Orlen says the wind went where it liked. The court asks if winds like things. The mage says, under '
             'oath, that they do."',
             '"The court has sent for the wind."',
             '"The bailiff reports that he went to the field and stood in it all day and was blown over twice. He asks if '
             'this counts as the wind appearing."',
             '"The court rules that the wind has appeared, and asks it to state where it likes to go. Silence. The court '
             'notes that the wheat of the farmer Bram lies flat again, in the courtroom, in a basket the farmer brought."',
             '"Judgment deferred." Below, many years later: "Still deferred."'],
         hidden='The judgment, never spoken, in the judge\'s hand: "I find for the wind. It goes where it is sent, and it '
                'should not be. I will not say this aloud while I want to keep my seat. Let whoever binds this book say it '
                'for me."',
         chron='Even in the Empire\'s courts there were those who thought the binding was wrong. They did not say so.',
         effect=None),
    dict(key='teller', title="A Teller's Count", thread='fall', noun='leaf', where=('starhouse', 'windtower'),
         pages=[
             '"I am Ilo, the youngest teller. Tonight I counted four thousand and eleven stars. Master Vane counted four '
             'thousand and twelve. He is always one more. He says it is the one I have not learnt to see."',
             '"A star is missing. Master Vane says I miscounted. He counts himself. He says I miscounted. He counts again. '
             'He does not say anything."',
             '"Two missing. We sent word to the Court. The Court says the tellers have miscounted."',
             '"Nine missing, all in the north of the sky, in a line. Master Vane drew the line on the floor. It points at '
             'the Sky-Seat. He rubbed it out."',
             '"Tonight there is a new star. It is not in any of the books. It does not move with the others. It is '
             'getting bigger."',
             '"Master Vane has told us to go home. He is staying to count. He says someone must write down what happens."',
             '"Four thousand and twelve. Master Vane is right. I can see the one more now. It is very bright, and it is '
             'not far away at all."'],
         hidden='In Vane\'s hand: "The stars did not go out. They were taken. The Hollow King\'s mages pulled them down '
                'one by one, for their iron, to build something at the Sky-Seat. The last one they pulled was too big. I '
                'am writing this and it is coming. Ilo, you should have gone home."',
         chron='The tellers saw the stars go, one by one, and the Court would not hear it.', effect=('place', 'forge')),
    dict(key='bell', title="The Bronze Founder's Bell", thread='fall', noun='leaf', where=('vcity', 'harbour'),
         pages=[
             '"I am Dovic, bronze-founder of the Street of Glass. I have been asked to cast a bell for the Sky-Seat, the '
             'biggest ever cast."',
             '"The bell is cast. It is perfect. No one will ring it: the Sky-Seat has bound winds to ring its bells. '
             '\'The wind rings better,\' they say."',
             'The Lament of the Bronze Founder: "I cast a bell for the Sky-Seat that no one will ring, / for no one rings '
             'a bell that the wind can ring instead."',
             '"I have put my name inside the bell, where no one will see it, and my daughter\'s, and a small open hand."',
             '"The winds are taken. The bells of the Sky-Seat are silent. Mine too. It hangs there, perfect, and no one '
             'rings it."',
             '"Tonight a bell rang from the Sky-Seat. Not the wind\'s ringing. Someone is pulling the rope. It is ringing '
             'the old warning, over and over."'],
         hidden='From his daughter: "Father went up to the Sky-Seat the last night, through the gates, nobody stopped him. '
                'He rang his bell so that the lower city would run. Many ran. The bell is in the sea now. On storm nights '
                'it rings."',
         chron='The bell that rings under the sea on storm nights is Dovic\'s, the founder of the Street of Glass.',
         effect=None),
    dict(key='mor', title='Mor the Silent', thread='emperors', noun='letter', where=('vcity', 'library'),
         pages=[
             '"Year 1. The Emperor wishes it known that he will speak through his scribes from now on, as is his right." '
             'Pell, first scribe.',
             '"Year 4. The Emperor approves the new roads, the new taxes and the new bridge, and asks that his breakfast '
             'be served colder."',
             '"Year 12. The Emperor did not answer the petition of the western provinces. The scribes have answered it in '
             'his name. He was not displeased."',
             '"Year 19. The Emperor has not eaten his breakfast in a month. The scribes have stopped serving it."',
             '"Year 20. The scribes agree that the Emperor\'s will is clear in all matters, and that they will continue to '
             'express it."',
             '"Year 25. A scribe who asked to see the Emperor has left the service. His desk is empty. We do not speak of '
             'it."',
             '"Year 30. The Emperor Mor is dead, of age, peacefully, in his rooms. The scribes have prepared his tomb. It '
             'need not be opened."'],
         hidden='"He died in the nineteenth year. We were afraid. Then we were good at it. For eleven years we ruled the '
                'Empire well, and no one knew, and it was the best time the provinces ever had. Let it be known now, when '
                'it does not matter." The scribes, together.',
         chron='Mor the Silent died in his nineteenth year; his scribes ruled in his name for eleven more.',
         effect=('disprove', 'Mor the Silent spoke only')),
    dict(key='petition', title='The Petition of Hessa Var', thread='dead', noun='petition', where=('deadroad', 'library'),
         pages=[
             '"To the court: my son Aulus died at the wall. Now he rows a merchant\'s barge on the river. I ask that he be '
             'laid down." "Refused. He was bound lawfully; the merchant paid for him."',
             '"Second year. I offer to buy him back. I have sold the house." "Refused. The price has risen; the dead man '
             'is now trained."',
             '"Fifth year. I have found his seal: the merchant\'s house, the year. I ask the court to read the law on '
             'soldiers\' bodies." "Refused. The law was changed in the year he died. The court regrets the timing."',
             '"Ninth year. I am working on the barge as a cook, so I can see him. He rows well. I did not know he could '
             'row."',
             '"Fourteenth year. I am old. I ask, once more." "Granted."',
             'A clerk\'s note on the back: "Granted in the year 1400 FF, the 13th day of Vaelmoon. Not served: the court '
             'did not sit again."'],
         hidden='"She did not wait for the court. On the night the dead walked free, she was on the barge. He stopped '
                'rowing. He looked at her. That is all I saw; I was the helmsman, and I jumped." A nameless note in the '
                'binding.',
         chron='The Ruin fell on the 13th day of Vaelmoon, 1400 FF, the day a court at last granted a mother\'s petition.',
         effect=('riddle', 'dead', 3)),
    dict(key='buydead', title='Buy Dead, Sell Work', thread='dead', noun='ledger leaf', where=('vcity', 'mine', 'harbour'),
         pages=[
             '"Bought: forty dead from the plague pits of Lowmarket, lawfully sealed. Sold: forty to the salt mines. '
             'Profit: good. Note: buy dead, sell work."',
             '"Bought: the crew of a sunk galley, already wet. Sold: to the harbour, for diving. They do not need air. '
             'Profit: very good."',
             '"Bought: my own father, from the debt court. I could not let anyone else have him. Sold: nothing. Profit: '
             'none. He polishes the shop floor."',
             '"A good year. I am rich. My wife has left me; she says the house smells of the sea and the grave. It smells '
             'of money."',
             '"A priest of Sol-Amarath came to the shop and said nothing. He stood there an hour. I have doubled the '
             'guards."',
             '"I am old. I have written in my will that I am not to be bound. My sons have read it. They looked at each '
             'other."',
             '"My father has stopped polishing. He stands by my bed at night. I do not think anyone ordered it."'],
         hidden='His last will, sewn into the cover: "Let no one buy me. Lay me down with my father, both of us, facing the '
                'ground, as the uncounted are laid. We were the same, in the end, and I knew it."',
         chron='Corvan the dealer in dead asked to be laid down facing the ground, as the uncounted were.', effect=None),
    dict(key='lowfold', title='The Counting of Lowfold', thread='uncounted', noun='leaf', where=('deserted', 'road'),
         pages=[
             'A report: "Lowfold refuses the Counting. They say they are not a province, only a valley. Orders requested."',
             'A letter: "My love, it is a pretty valley. They gave us cheese. The children follow the soldiers about. I am '
             'to count them all."',
             'A report: "Orders received: count Lowfold, by any means."',
             'A letter: "I have asked the headman again. He says if they are counted, their sons go to the legions and '
             'their winds go to the Sky-Seat, and then they are a province, and then they are not a valley. I do not know '
             'what to say to him. He is right."',
             'A report: "The village refused the Counting. The village has been counted. The total is zero."',
             'A letter, never sent: "Do not ask me what we did. I counted. That is all I will say. I counted."'],
         hidden='"The total was not zero. Some of us left in the night and took the children over the hills, and Caius saw '
                'us go, and turned his back, and wrote zero. Lowfold is not empty. It is somewhere else." The headman\'s '
                'daughter.',
         chron='Lowfold refused the Counting. Its people went over the hills, and an officer wrote zero.',
         effect=('place', 'lowfold')),
    dict(key='play', title='The Banned Play', thread='uncounted', noun='role', where=('vcity', 'deserted', 'hermitage', 'road'),
         pages=[
             'The Teller: "I am asked to count the people of this street. I have counted the stars for forty years. I '
             'will count you too. Stand still."',
             'The Baker: "I will be counted. I weigh true; let the Empire weigh me true."',
             'The Slave, called Twelve: "Count me, then. As what? As twelve? I had a name before your number."',
             'The Mother: "Count my son, who is dead and still rows. Count him twice: once for the wall, once for the '
             'river."',
             'The Soldier: "I counted days on a wall. Nothing came. Now I count you. Something is coming."',
             'All, at the end: "Count me, then. Count all of us. You will run out of numbers before we run out of names."'],
         hidden='"The play was stopped after one night, and we were all taken. We had agreed beforehand: whoever got free '
                'would hide their part where no one would look, so the play could be put together again. If you are '
                'reading all six, we got free. All of us." The players of the Street of Glass.',
         chron='The Count was played once in the Street of Glass, and banned. Its players hid their parts.', effect=None),
    dict(key='hand', title='The Open Hand', thread='uncounted', noun='note', where=('road', 'gate', 'walltower'),
         pages=[
             '"Wherever you see the hand, there is a door that opens at night." Scratched beside a hand on a milestone.',
             '"I am a Road-Warden. I am ordered to grind off the hands. I grind off half. Nobody counts them."',
             '"A baker in the Street of Glass bakes an extra loaf every night and leaves it on the sill. It goes. Nobody '
             'sees who takes it."',
             '"Aru passed here. Go north." He was not the first.',
             '"A legion soldier on the Northern Wall looks the other way every night between the second and third watch."',
             '"The tellers know. They count the stars, and they count nothing else, and they write nothing down."',
             '"Who drew the first hand? I did, in the year 840 FF, on a milestone on the coast road, when they took my '
             'sister. I could not write. So I drew a hand, open, the way she waved."'],
         hidden='No words: a map of the milestones with the hand, joined by a line, a road that is on no Varnish map.',
         chron='The Hand\'s Road ran from milestone to milestone, for those who ran.', effect=('way',)),
    dict(key='twelve', title='Twelve', thread='uncounted', noun='leaf', where=('vcity', 'mine', 'road'),
         pages=[
             'A sale record: "One man from the coast, strong, no letters, speaks no Varnish. 300 coppers. Name: none '
             'given. Name assigned: Twelve."',
             'The householder, to his brother: "Twelve is a good worker and learns quickly. He has picked up our letters '
             'from watching the children\'s lessons. I have not stopped it. It seemed unkind."',
             'A tablet under a floor: "My name is Aru. They call me Twelve. If you find this, say Aru out loud once. Then '
             'I am counted."',
             'The householder: "Our Twelve has run. I do not understand it. We fed him well and never beat him without '
             'cause. I have sent Marcus after him. Marcus is not unkind either."',
             'Scratched in a mine, beside the small open hand: "Aru passed here. Go north. North of the wall they ask your '
             'name and use it."',
             'Marcus, to the householder: "I found where he crossed the wall. The legion let him through. The soldier on '
             'the tower said: \'If the north ever sends anything, I hope it is the people we sent there.\' I did not '
             'argue. I am coming home without him. Take it from my pay."',
             'The householder, years later: "The children ask about Twelve. I have told them his name was Aru. My wife '
             'says I am a fool. Perhaps. I said it out loud anyway."'],
         hidden='A sheet in a tongue that is not Varnish, with a child\'s translation under it: "Aru, of the coast, came to '
                'us across the ice. He taught our children his letters and theirs. He is buried lying down, as we do, '
                'facing the sea he came from."',
         chron='North of the Northern Wall, in the time of the Empire, there were people who took in those who ran.',
         effect=None),
    dict(key='chariot', title='The Charioteer', thread='winds', noun='scrap', where=('vcity',),
         pages=[
             'A betting slip: "Lucan, Blue, to win. Ten coppers. (Everyone is betting on Lucan. The odds are terrible.)"',
             'A fan\'s graffiti: "LUCAN 38. Next race: 39. Next year: 50. Next life: Emperor."',
             'Lucan, to his trainer: "The Greens have bound a wind to their team. I can feel it on the turns. I will win '
             'anyway, but I want it said."',
             'The race record: "Race 41. Lucan, Blue, leading by three lengths at the last turn, pulled his horses wide. A '
             'child had run onto the track. Green wins."',
             'A statue\'s base: "For Lucan, who lost one."'],
         hidden='From the child, as an old man: "I was seven. I ran out because the wind the Greens had bound blew my cap '
                'onto the track. Lucan saw it. He told me afterwards that he had always wanted to lose one, to see what it '
                'felt like. He said it felt fine."',
         chron='Lucan the charioteer lost one race in forty-one, to save a child; they built him a statue for it.',
         effect=None),
    dict(key='ninthday', title='The Ninth Day', thread='emperors', noun='leaf', where=('vcity', 'library'),
         pages=[
             '"Day 1. Taur is crowned. He is nineteen. He asks where the kitchens are."',
             '"Day 3. The Emperor has freed the bound winds of the Street of Glass, for a day, as in the old Loosing. The '
             'Senate is concerned."',
             '"Day 5. The Emperor orders new coins struck with his face. The mint says it takes a month. He asks them to '
             'hurry."',
             '"Day 7. The Emperor has asked to see the pits in the east. The mages say there is nothing to see. He says he '
             'will see it anyway."',
             '"Day 8. The Emperor came back from the east and did not speak at dinner."',
             '"Day 9. The Emperor is dead. A fall from a stair. The mint is asked to melt the new coins. It manages all '
             'but forty."'],
         hidden='"He wanted to stop it. He saw what they were making in the pits and he said, at dinner, \'Tomorrow it '
                'ends.\' Forty coins were struck. I hid them." The master of the mint.',
         chron='Taur the Short saw the pits in the east and meant to end what was done there. Forty of his coins were '
               'struck.', effect=('riddle', 'orcs', 3)),
    dict(key='lantern', title="The Lantern-Bearers' Watch", thread='tam', noun='leaf', where=('walltower',),
         pages=[
             '"Every dusk we light a lamp on every tower, from the sea to the mountains. It takes an hour to run the whole '
             'line. I run the middle."',
             '"There is a light in the north tonight, far off, beyond the wall. Someone over there has lit a lamp too."',
             '"It is there every night now. When we light ours, theirs comes on."',
             '"I have started to wave at it. My officer says I am a fool. Tonight he waved too."',
             '"We have been told to stop lighting the lamps. The Sky-Seat needs the oil. Tonight the north lit theirs and '
             'ours stayed dark. I hope they do not think we have gone."'],
         hidden='"We lit ours anyway, the last night, with lard and rags. Theirs came on. Then the sky went white."',
         chron='On one tower of the Northern Wall a lamp can still be lit.', effect=('lamp',)),
    dict(key='daughter', title="Letters to a Mage's Daughter", thread='winds', noun='letter', where=('vcity', 'starhouse'),
         pages=[
             '"My dear Lessa, the Sky-Seat is very beautiful and very cold. I am working on something important. I cannot '
             'tell you what. It is about the winds."',
             '"My dear Lessa, we are bringing all the winds here. It is for the good of the Empire. The farms will be fine; '
             'the Emperor says so."',
             '"My dear Lessa, your mother tells me you hid your wind. I am proud of you. Do not tell anyone I said so."',
             '"My dear Lessa, the winds are not happy here. You can hear them in the walls. Someone on the council says '
             'they can be made happy if we give them something to do. I asked what. He did not answer."',
             '"My dear Lessa, we are making something out of star-iron and the winds together. If it works the Empire will '
             'last forever. I think that is what frightens me."',
             '"My dear Lessa, do not come here. Whatever you hear, do not come here. Let your wind go north. Go with it."'],
         hidden='Lessa\'s own hand, old: "I went north with Pip. I never saw my father again. I do not know if he helped to '
                'make the thing or tried to stop it. I have decided he tried to stop it."',
         chron='At the Sky-Seat the mages made something of star-iron and the winds together.', effect=('riddle', 'king', 7)),
    dict(key='grain', title='The Grain Count', thread='dead', noun='leaf', where=('deserted', 'vcity'),
         pages=[
             '"The province owes the Empire four thousand measures of grain."',
             '"The harvest was three thousand. The winds were taken; the mills did not turn; much rotted."',
             '"The clerk Ferro is ordered to take four thousand. He takes three thousand. He writes four."',
             '"The next year the province owes five thousand. Ferro takes two. He writes five."',
             '"Ferro has been found out. He is to be bound to the granary for life and beyond, to count the grain '
             'forever."'],
         hidden='"The granary of Ferro stands still. The bound clerk inside still counts; he will tell you the number if you '
                'ask. It is always the number the people needed, not the number they owed."',
         chron='Ferro the clerk was bound to his granary for writing the numbers the people needed.', effect=None),
    dict(key='shape', title='On the Shape of Things', thread='dead', noun='leaf', where=('starhouse', 'library'),
         pages=[
             '"Everything that is straight was made by us. Everything that is round was made by the gods."',
             '"The road is straight. The river beside it is not. In a thousand years, the road will be gone and the river '
             'will be where it is."',
             '"We count. The gods do not count; they are the thing counted."',
             '"The mages say the winds can be bound because they have names. I say a thing with a name cannot be owned, '
             'only known."',
             '"I have been asked by the Collegium to stop teaching. I have been asked politely, which is how one knows it '
             'is serious."',
             '"The Empire is a square, and it will not last."'],
         hidden='"I am bound now. My students did it, for love, so I could go on teaching after death. I cannot tell them I '
                'do not want it. I teach. They write it down. Every word of this book after page four is mine, but not my '
                'will."',
         chron='Ennis, who wrote On the Shape of Things, was bound by his own students so he could go on teaching.',
         effect=('riddle', 'dead', 7)),
    dict(key='ferry', title='The Last Ferry', thread='dead', noun='tally', where=('river', 'road'),
         pages=[
             'A tally: "Four soldiers, two priests, one mage (did not pay, said the river owed him)."',
             'A tally: "Seventeen. Ninety. I have stopped counting what they pay."',
             '"The sky is white in the west. Everyone wants to cross. The dead on the other bank are standing up."',
             '"The dead want to cross too. They wait their turn. They are very patient. I take the living first. Then I '
             'take the dead."',
             '"I have made the last crossing. Everyone is over. I am tying the boat up. There is no one to pay me. The '
             'river owes me."'],
         hidden='"My father took everyone across, the living and the dead, all night. He said the dead had the same right to '
                'the other bank. We have kept the ferry ever since." The ferryman\'s family.',
         chron='One family of ferrymen has kept its ferry since the night of the Ruin, and owes the river nothing.',
         effect=('ferry',)),
    dict(key='census', title="The Tellers' Census", thread='uncounted', noun='leaf', where=('library', 'starhouse'),
         pages=[
             '"Province of the Coast: 410,000 counted. 40,000 uncounted (estimated; they hide)."',
             '"Province of the Hills: 220,000 counted. Of these, 30,000 bound dead (counted separately, as property)."',
             '"The Sky-Seat: 90,000 counted. Of these, 12,000 mages, 40,000 servants, 8,000 bound winds (counted, at the '
             'Emperor\'s order, as citizens)."',
             '"Province of the North: the legions only. The rest do not answer."',
             '"Total of the Empire: eleven million counted." One teller adds, in the margin: "and the stars, which are '
             'more."',
             '"The census of 1400 FF was never completed."'],
         hidden='"The winds were counted as citizens and the uncounted were not. I have written this down so that someone '
                'after us may laugh, or weep." Vane, teller.',
         chron='The Empire counted eleven million, and the bound winds among its citizens, and not the uncounted.',
         effect=('riddle', 'vaults', 5)),
    dict(key='gardener', title='The Gardener of the Sky-Seat', thread='fall', noun='leaf', where=('vcity', 'harbour'),
         pages=[
             '"I keep the hanging gardens of the Sky-Seat. Everything here grows in wind: the bound winds carry water up '
             'from the sea."',
             '"The winds are angry this year. The roses face away from the palace."',
             '"I have planted an apple from my village in the top garden. It will not grow here. I am trying anyway."',
             '"Everyone is leaving the upper city. They say something is coming down. I am staying with the apple. It has '
             'one leaf."',
             '"It has flowered."'],
         hidden='"In the ruins of the Sky-Seat there is an apple tree, very old, on a ledge no one can reach. Every spring '
                'it flowers." A traveller, long after.',
         chron='On a ledge of the Sky-Seat an old apple tree flowers every spring.', effect=('apple',)),
    dict(key='gods', title='The Uncounted Gods', thread='uncounted', noun='leaf', where=('hermitage', 'deserted', 'mine'),
         pages=[
             '"The masters pray to Sol-Amarath, who counts. We pray to the Unnamed, who does not."',
             '"The Unnamed has no temple. You pray by saying a name out loud that no one else remembers."',
             '"In the mines we pray to the Hand, who opens. It is not a god. It is us."',
             '"My grandmother prayed to the sea, because it was the only thing the Empire could not count."',
             '"A priest of Sol-Amarath came to the mine and prayed with us to the Unnamed. He was taken away the next day."',
             '"When the Empire falls, the Unnamed will remember all of us. That is the whole of the faith."'],
         hidden='"The priest who prayed with us was named Oswin. I say his name out loud each morning. Now you have read it, '
                'say it too."',
         chron='The uncounted prayed to the Unnamed, by saying aloud a name no one else remembered.', effect=None),
    dict(key='warden', title="The Road-Warden's Last Walk", thread='fall', noun='note', where=('road', 'gate'),
         pages=[
             '"I am the last Road-Warden of the eastern road. There is no pay any more. I walk it anyway."',
             '"League forty. The bridge has fallen. I have marked the ford with stones."',
             '"League ninety. A village has grown over the road. They use the milestones as doorsteps. I have not told '
             'them."',
             '"League one hundred and twenty. The road ends in a forest that was not there when I was young."',
             '"I have scratched the leagues fresh on every stone I passed, so the next one knows."',
             '"I am old. This is the last stone I will reach. It is a good stone."'],
         hidden='"I found him sitting against the last stone, in the year 31 AR. He had scratched one more line: \'League 0. '
                'Start here.\'" A shepherd.',
         chron='The last Road-Warden walked his road long after the Ruin, and marked it fresh for the next one.',
         effect=('way',)),
    dict(key='child', title="A Child's Year", thread='fall', noun='wax tablet', where=('vcity',),
         pages=[
             'The Counting: "Today we were counted. I am number four in our house. The dog is not counted. I think that is '
             'wrong."',
             'The Loosing: "Today the winds went free. Mine knocked over Father\'s wine. I said it was the wind. It was the '
             'wind."',
             'The Day of Leagues: "I walked a league with Father and got a pebble. It is grey. I wanted a red one."',
             'Standing Night: "We told Grandfather the news. He did not say anything but I think he liked the bit about the '
             'dog."',
             'Vaelmoon: "Teacher says there is no thirteenth month. Grandmother says in Vaelmoon we do not build. I asked '
             'why. She said because something else is building."',
             'A writing exercise, the same line ten times: "A road is straight because the Empire is straight." The last '
             'line reads: "A road is boring."'],
         hidden='A drawing: a house, a dog, three people and a very large star. Underneath: "MY FAMILY AND THE SKY." And '
                'under that, in a grown hand: "Found in the house of the Ennis family, on the 13th of Vaelmoon, 1400 FF. '
                'The house was empty. The dog was waiting."',
         chron='The Ruin fell in the thirteenth month, Vaelmoon.', effect=('riddle', 'king', 6)),
]
BOOK = {b['key']: b for b in BOOKS}
NOUN_OF = {'diary leaf': 'leaf', 'ledger leaf': 'leaf', 'wax tablet': 'tablet'}

# ------------------------------------------------------------------ the five riddles
# src: 'stone' (a stone with the old letters), 'library' (the scribes), 'rumour' (heard), 'place:<kind>' (a telling
# thing at a Varnish place), 'page:<book>:<n>' (that page of a book, when you read it). A false fragment carries why.
RIDDLES = [
    dict(key='fall', title='How the Sky-Seat fell',
         gap='How the Sky-Seat fell, no one you have met can say. The tellers counted the sky; what they saw, they wrote '
             'down somewhere.',
         frags=[
             ('A stone: "The last order: seal the vaults. The sky is falling."', 'stone', None),
             ('"Nine missing, all in the north of the sky, in a line. It points at the Sky-Seat."', 'page:teller:3', None),
             ('A star floor of iron: the star map has holes where stars were, hammered out and filled with lead.',
              'place:starhouse', None),
             ('At a forge: "Iron from the ninth star. It came down warm and singing. The masters want more."',
              'place:forge', None),
             ('A mage\'s treatise: "A star is only iron that has not been asked. We have learnt to ask."', 'library', None),
             ('"The Sky-Seat fell because the Emperor angered Sol-Amarath."', 'rumour',
              'the priests of today say it; the Varnish never did.'),
             ('Under the glassy sand of the fallen sky: a chain of star-iron as thick as a man, snapped.',
              'place:fallensky', None),
             ('"Tonight there is a new star, very bright, and it is not far away at all."', 'page:jar:6', None)],
         answer='The mages pulled the stars down for their iron, one by one, with chains and bound winds. The last one '
                'they pulled was too great to hold. It came down on the Sky-Seat.',
         place='anchor'),
    dict(key='king', title='Who the Hollow King was',
         gap='Who the Hollow King was, no stone older than the last two hundred years will tell. Before him, the mages '
             'prayed to someone else.',
         frags=[
             ('"The Hollow King was the god of the Varnish mages. Some say he brought the Sky-Seat down."', 'rumour', None),
             ('On a temple floor: "Here the winds were asked. Here, later, the winds were told."', 'stone', None),
             ('The Hollow King is on no stone older than 1200 FF. Before that the mages prayed to Aerith of the Four '
              'Winds.', 'library', None),
             ('In a Collegium ruin: "Something to give the winds to do. Something to hold them all. Something that will '
              'not tire."', 'place:windtower', None),
             ('A mage\'s warning, burnt into a door: "Whatever answers when you call the thirteenth wind, it is not a '
              'wind."', 'stone', None),
             ('"In Vaelmoon we do not build, because something else is building."', 'page:child:4', None),
             ('"The Hollow King was an emperor who would not die."', 'rumour', 'no emperor is missing from the list.'),
             ('"We are making something out of star-iron and the winds together. If it works the Empire will last '
              'forever."', 'page:daughter:4', None)],
         answer='The Hollow King was not a god the Varnish found. The mages made him, of star-iron, every bound wind and '
                'an army of the dead, to rule for an Empire that would never end. He was hollow because nothing was born '
                'in him. He was called the thirteenth wind, and he was finished in the thirteenth month.',
         place='throne'),
    dict(key='orcs', title='Where the orcs came from',
         gap='Where the orcs came from, the orcs do not say to strangers. The Empire wrote it down, and did not want it '
             'read.',
         frags=[
             ('"Before the Ruin there were no orcs in the east. Some say the Varnish mages made them."', 'rumour', None),
             ('A stone: "In the east the mages are working on something in the pits. The tellers will not count it."',
              'stone', None),
             ('A stone: "The things from the pits have been counted as beasts, not as men. Let it be written."', 'stone',
              None),
             ('The boy-emperor Taur went to see the pits in the east, and died on a stair the next day.',
              'page:ninthday:5', None),
             ('In the pits: chains for men, not for beasts. Scratched in the wall, the small open hand.', 'place:pits',
              None),
             ('An orc\'s words: "They call us brutes. The Empire called us worse, and the Empire is dust."', 'library',
              None),
             ('"Orcs come out of the ground like mushrooms after rain."', 'rumour', 'they do not.'),
             ('A Collegium ledger: "Uncounted, 400, from the coast and the hills. Returned from the pits: 400, changed. '
              'Strong, tireless, hungry. Fit to feed the work."', 'library', None)],
         answer='The first orcs were people: the uncounted, sent to the pits in the east and changed by the mages to be '
                'strong and tireless servants for the Hollow King. When the Sky-Seat fell they walked free with the dead. '
                'Whatever orcs are now, the Empire made them, and the Empire is dust.',
         place='pits'),
    dict(key='vaults', title='What lies in the vaults',
         gap='What the vaults hold, no one you have met can say. A scribe of the Collegium might have written it down.',
         frags=[
             ('A stone: "Seal the vaults. Let whoever comes after not open them."', 'stone', None),
             ('A key of black Varnish iron opens a sealed vault.', 'library', None),
             ('On a vault door, half ground away: "Here lie the names."', 'place:sluice', None),
             ('"Seal it. Seal all of it. Let them think we were only an empire."', 'stone', None),
             ('On a vault floor: jars, all empty but one, with the lid tied down. It rattles.', 'place:sluice', None),
             ('"Eleven million counted." On the back: "and the uncounted, whom we also wrote down, in the other book."',
              'library', None),
             ('"The vaults are full of gold."', 'rumour', 'few vaults hold any.'),
             ('A scribe\'s note: "We could not burn them. Names do not burn. We could only shut them in."', 'library',
              None)],
         answer='The vaults hold what the mages could not destroy: the Book of the Counting with every name, the counted '
                'and the uncounted, the last jars of bound winds, and pieces of the Hollow King. They were sealed so that '
                'no one would build him again.',
         place='vault'),
    dict(key='dead', title='Why the dead were bound',
         gap='Why the Varnish bound their dead, the dead do not say. The roads where they stand may.',
         frags=[
             ('Funeral words: "He stood all his life. Let him stand now."', 'stone', None),
             ('The law: "Debtors who die in debt are bound to the house they owe until the debt is worked off. Interest '
              'continues."', 'library', None),
             ('A farmer: "My grandfather ploughs my field. He was a good man. He is a good plough."', 'library', None),
             ('A mother asked the court, year after year, to lay her bound son down. She was refused.',
              'page:petition:0', None),
             ('A stone: "My lord, the dead in the eastern road no longer stand straight. They lean. All of them. Towards '
              'the Sky-Seat."', 'place:deadroad', None),
             ('A mage: "The dead are the King\'s hands. The winds are his breath. The stars are his bones."', 'stone',
              None),
             ('"The dead were bound to keep the plague in them."', 'rumour', 'it was not for the plague.'),
             ('"I teach. They write it down. Every word is mine, but not my will."', 'page:shape:5', None)],
         answer='First the Varnish bound their dead out of love, to stand among the living. Then for work, because the dead '
                'feel no cold. At the end, for the Hollow King: every bound dead man was one of his hands. When he broke, '
                'they walked free, and some still walk.',
         place='hall'),
]
RIDDLE = {r['key']: r for r in RIDDLES}
WHOLE = 6                 # true fragments that make a riddle whole
LAST = ('The Ruin, as it was', 'The mages of the Varnish built a god. They pulled stars down for his iron and bound every '
        'wind and an army of the dead into him, and fed the work with the uncounted, whom they changed into the first '
        'orcs. The last star they pulled was too great: it fell on the Sky-Seat, and the Hollow King broke apart. What '
        'is left of him is the hunger people now call Morrak. What they could not destroy, they sealed in the vaults. '
        'You know it now, and nobody else does.')

# ------------------------------------------------------------------ names
CITY_NAMES = ['Aes Varnath', 'Caelumbra', 'Ithil Vess', 'Orosgard', 'Halunmere', 'Domnaris', 'Serratum', 'Ennisford',
              'Taurvale', 'Mor Ithila', 'Vessamar', 'Eskel Reach']
PLACE_NAMES = {
    'walltower': ['The Tower of the {n} Legion'], 'windtower': ['The Wind Tower of {v}'],
    'deadroad': ['The Road of the Standing Dead'], 'forge': ['The Star Forge of {v}'], 'gate': ['The Gate of Leagues'],
    'sluice': ['The Sluice Hall of {v}'], 'fallensky': ['The Fallen Sky'], 'starhouse': ['The Star House of {v}'],
    'harbour': ['The Sunken Harbour of {v}'],
}
LEGIONS = ['First', 'Second', 'Third', 'Fourth', 'Fifth', 'Sixth', 'Seventh', 'Eighth', 'Ninth']
DEEP_NAMES = {'anchor': 'The Anchor', 'throne': 'The Hollow Throne', 'pits': 'The Pits of the East',
              'vault': 'The Last Vault', 'hall': 'The Standing Hall'}
