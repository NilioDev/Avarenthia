"""The words of the peoples (round 58b): each people's own books, its own telling of the dawn, and its voice in
everyday talk. Pure data; folkbooks.py puts the pages in the world and the books in the chronicle.

Every book names the chapter of The Counted Sky (countedsky.py) it leans on (`ch`), so a change to the story shows
which books to go over. Each people writes its own way, and the peoples contradict each other: that is the point."""

# ------------------------------------------------------------------ the peoples
# name: the heading in the chronicle; script: who can read it (None: anyone, in common letters or pictures);
# noun: one page; binder: who binds it (None: you lay it in order yourself)
PEOPLES = {
    'dwarf': dict(name='The dwarves', script='dwarf runes', noun='ledger leaf',
                  binder='the keeper of a dwarf hall'),
    'elf': dict(name='The elves', script='the elven hand', noun='ring', binder='an elf of the glades'),
    'halfling': dict(name='The halflings', script=None, noun='recipe', binder='a halfling mayor'),
    'gnome': dict(name='The gnomes', script='gnomish shorthand', noun='notebook page', binder='a gnome of the hamlets'),
    'kobold': dict(name='The kobolds', script=None, noun='slate', binder=None),
    'goblin': dict(name='The goblins', script=None, noun='swap leaf', binder='a goblin fixer in a city'),
    'gnoll': dict(name='The gnolls', script=None, noun='carved bone', binder=None),
    'lizard': dict(name='The lizardfolk', script=None, noun='notched bone', binder=None),
    'orc': dict(name='The orcs', script='the young orc letters', noun='leaf', binder='an orc of the towns'),
    'north': dict(name='The north', script=None, noun='name-roll', binder='a keeper of a northern hall'),
    'fey': dict(name='The fey', script=None, noun='leaf of thin gold', binder=None),
}
ORDER = list(PEOPLES)

# ------------------------------------------------------------------ each people's own dawn ("Before the Founding")
# told when you bind the first book of that people; four of them open the prologue of The Counted Sky
DAWN = {
    'dwarf': 'There was no question. There was a forge. Durnak struck his anvil once, under the roots of the world, '
             'and the sparks went up through rock and sea and stuck in the dark, and they are cooling still. That is why '
             'the stars are iron, and why they ring. Ask iron a question and it answers with a clang. Then he lay down '
             'under the mountains he had made, and we woke beside his fire, hot from it, and counted what we had. We '
             'have been counting since.',
    'elf': 'We woke first, under the Elder Tree, on the very spot where the first light of the first star touched the '
           'ground. We looked up through gold leaves at a singing sky and understood at once that the world had been '
           'made as a setting for us. Nothing since has given us cause to think otherwise. The Tree taught us the true '
           'names of the stars before we had names of our own. The others woke later. One cannot help that.',
    'halfling': 'We never woke, love. We were just here, in the green downs, from the start, and everyone else was '
                'late. (That is a tavern joke. In truth we came up in the first meadow Thessaly sowed, where she sat '
                'down to rest, the only rest she ever took. The sweetleaf grew from the last seed caught in the seam of '
                'her sack. Dropped by chance, they say. Ha.)',
    'gnome': 'We woke when nobody was looking, which is how we like it. The first thing we heard was the old trees '
             'gossiping. The first thing we did was take a stag-beetle apart to see how it went, and put it back so it '
             'went a little better. We counted the stars with our own astrolabes. We got another number than '
             'everyone else. We have kept it to ourselves.',
    'kobold': 'Dark, under the mountain, close to the Big Anvil. First thing seen: a spark, flying. Pretty. So pretty. '
              'Ever since: want the pretty. Then one of us went up the chimney-crack and saw the sky. All of it, full of '
              'sparks, and too high. She came down and told. Ever since: want the sky. Cannot have the sky. Polish '
              'what we have.',
    'goblin': 'Nobody saw us wake. We came out of the edges of everyone else\'s big story while the tall ones were busy '
              'being important. Suited us. Still does. The stars are cold eyes. Stay in the cracks and they cannot see '
              'you. Nobody watches the cracks of the world.',
    'gnoll': 'We were the moon\'s hunting pack before we stood on two legs. She ran, we ran. When she is full we sing '
             'to her, and she listens. Once there were two of her, the big one and the small quiet one in the north. The '
             'song says the small one would be dragged out of the sky. It was.',
    'lizard': 'Hatched in the warm fen, from eggs older than the peat. The wyrms are our elder brothers, of the same '
              'fire. They flew up into the cold wind. We sank into the warm mud. Ask which of us got the better bargain. '
              'We count the ages by the moons. We have counted very many.',
    'orc': 'We have no dawn. The others woke under trees and stones and gods. We came up the steps of a pit in the '
           'east, four hundred of us, and we had been people when we went down. That is our beginning, and we did not '
           'choose it. We choose everything after.',
    'north': 'Our grandmothers\' grandmothers came over the wall from the south, sent, with nothing. Why, nobody '
             'remembers. They learned the ice and the skin-boat and the long night, and they steered by the stars, '
             'because there was nothing else to steer by. We still ask a stranger\'s name, and we use it. It is only '
             'manners. Isn\'t it?',
    'fey': 'Between the lamp going down and the stars coming out there is an hour that belongs to no one. We stepped '
           'out of it. We are not elves, whatever they let you think. We were dancing on the hills long before the first '
           'elf opened an eye, and we have never let them forget it.',
}

# ------------------------------------------------------------------ the books
# where: kinds of place a page may lie ('set:<race>' a settlement of that people, 'site:<kind>' a place on the land,
# 'north' a settlement of the far north, 'city' a human city, 'court' the court under the hill)
BOOKS = [
    # ---- the dwarves
    dict(key='bardin', people='dwarf', title='The Account of Bardin Coalhand', ch='III',
         where=('set:dwarf', 'site:grudgestone', 'site:dwarfroad'), pages=[
             '"Year 61 after the men began counting. Bardin Coalhand, master-smith of our hall, goes down to the town '
             'of Varn as a guest, with a wagon of good iron to sell. Entered: one guest, one wagon, iron of the best."',
             '"Bardin took a chill on the road home and died in a post-town of the men. Entered: one death, honest, of '
             'cold. His kin go down with a wagon to carry him home and lay him flat."',
             '"His kin found him standing. The men had bound him upright in a niche of their dead, a seal of lead on '
             'his beard, his eyes propped open. They said it was an honour. Entered: the Varnish, one grudge."',
             '"The men would not give him back. To lay a guest in the dirt would be an insult, they said. We turned the '
             'mules round. We shut the gates. Entered: no more trade with the surface. Not an ounce."',
             '"Year 760. A scout of ours passing a provincial town saw a short broad figure in a chain-gang, hauling '
             'stone for a bridge, an old seal on his chest. The town sold its antique dead to pay its debts. Bardin '
             'was in the lot. Entered: the grudge, again, in a larger hand."',
             '"After the Ruin an elf told us the Empire was sea-mud now, and surely the account was settled. The '
             'Lorekeeper looked at him a long time. Entered, in her words: a debt may not outlive the debtor. A grudge '
             'may."'],
         hidden='Under the last line, in a fresh hand: "Bardin is not yet home. The bridge he hauled for still stands, '
                'and so, they say, does he. Whoever brings him to a hall and lets us lay him flat: their name goes in '
                'this book too, on the other side of the page."',
         chron='The oldest open Varnish grudge is Bardin Coalhand\'s: a dwarf guest bound standing, later sold to work.',
         effect=('bardin',)),
    dict(key='deepdelve', people='dwarf', title='The Hold That Delved Too Deep', ch='before',
         where=('set:dwarf', 'site:oldmine'), pages=[
             '"Hall of Harrak, lowest gallery. The rock is warm here. Warmer each fathom. We are close to Him."',
             '"Struck a vein that sings when the pick touches it. The elders say go on. The young say go on louder."',
             '"Below the vein, the rock is not warm. It is hot, and it is angry. It is not Durnak\'s heat. Durnak\'s '
             'heat is kind."',
             '"We have gone past Him. We went down beside His sleep and past it, and the floor under us is the floor of '
             'the world, and something under that is knocking back."',
             '"Black fire up the shafts. This is written at the top of the lift. Nobody else came up."'],
         hidden='On the back, in the hand of the hold that took in Harrak\'s widows: "Since that day every hall has an '
                'iron door at its lowest depth, shut and barred by law. No dwarf digs below the Seal. No dwarf ever has. '
                'If you find one standing open, leave."',
         chron='A dwarf hold once dug below Durnak\'s sleep into the Ashen Deep; since then every hall has its Seal.',
         effect=('place', 'sealed')),
    dict(key='sparks', people='dwarf', title='The Sparks Owed', ch='before',
         where=('set:dwarf', 'site:grudgestone'), pages=[
             '"First entry of the first book. Against the kobolds: one sack of the Maker\'s sparks, still cooling, '
             'taken from beside the First Forge before the count was done. Open."',
             '"Sent three to the kobold crawl to ask for the sparks back. They came back with a basket of shiny '
             'pebbles and a drawing of a bow. Not sparks. Entry stands."',
             '"Year of the Long Hammer. Sent Hrolda Ironbrow down with a lamp and a sack, to ask politely. Hrolda came '
             'back with the lamp. The sack was returned the following spring, folded, with a button in it. The button '
             'is not a spark. Entry stands."',
             '"Year 990 of the men\'s count: a star fell in the hills, and the kobolds got to it first and took a '
             'piece. Not ours either. But noted, in the margin, with feeling."',
             '"The sack is at the bottom of the deepest hoard of all, the kobolds whisper. Which hoard is deepest, they '
             'do not whisper."'],
         hidden='Pressed between the leaves: a map of a kobold warren in charcoal, much rubbed out and drawn again, and '
                'one word in a dwarf\'s hand: "Here. Probably."',
         chron='The first entry of the oldest Grudge Book stands against the kobolds: a sack of Durnak\'s sparks.',
         effect=('place', 'kobolds')),
    dict(key='gates', people='dwarf', title='The Night the Gates Opened', ch='IX',
         where=('set:dwarf',), pages=[
             '"The mountain shook as if He had struck the anvil again. The elders went to the gate and opened it, the '
             'first time in a thousand years."',
             '"They came up the passes in the ash: fisher-folk, mud-folk from under the Sky-Seat, a baker with his '
             'loaves still under his arm. We took them down into the warm roads."',
             '"Entered: four thousand and some. Names: none. We did not ask. For once in this book, no names, by '
             'decision of the hall."',
             '"Also entered, on the other page: who had no need of our door that night, because they had brought the '
             'sky down. Their names we have."',
             '"The baker made bread for the hall for nine years and then went home. The bread was bad. Entered with '
             'gratitude anyway."'],
         hidden='Last line: "Whoever reads this to the end and is of the surface: you are owed a little of what we gave '
                'that night. Ask at any hall. Not much. A little."',
         chron='On the Night of the Ruin the dwarves opened their gates to the refugees and wrote down no names.',
         effect=('favour', 'dwarf')),
    # ---- the elves
    dict(key='firstpact', people='elf', title='The First Pact', ch='before',
         where=('set:elf', 'site:glade'), pages=[
             'The first ring: "We found that we had neighbours. The lords of the dusk informed us, smiling, that the '
             'woods were theirs as well. We did not draw. Bickering is for others."',
             'The second ring: "We asked them to sit with us under the Tree. They came. They love a form of words, '
             'and we gave them one."',
             'The third ring: "The pact: the forest by day to the elves, the hills by night to the fey, and neither to '
             'cross the other\'s threshold unbidden. They were enchanted by the phrasing."',
             'The fourth ring: "Some centuries later they sat down and reckoned how much of the year is day, and how '
             'much of the land was forest. They have not forgiven us. We consider it an early lesson in reading."',
             'The fifth ring: "The pact is the innermost ring of the Tree. Every bargain we have struck since is cut '
             'from the same wood."'],
         hidden='On the outer bark, small, in a later hand: "The hills by night to the fey. We have never asked which '
                'hills. One does not ask the fey a question one would not like to have answered."',
         chron='The elves\' first pact gave the forest by day to the elves and the hills by night to the fey.',
         effect=('lore',)),
    dict(key='rings', people='elf', title='The Rings of the Tree', ch='III',
         where=('set:elf', 'site:glade'), pages=[
             'Ring of the first wyrm\'s sleep: "Our lore-singers sang the last of the wyrms to sleep. It was a '
             'kindness. The wyrms, if anyone woke one to ask, might tell it otherwise. No one has."',
             'Ring of the dwarves: "The dwarves came up out of the stone and counted us. We have never been so '
             'thoroughly counted. It was not unpleasant, only loud."',
             'The four hundredth ring of the men\'s count: "In this ring the humans built a road. It was straight, '
             'which they seemed proud of. We let it go round us. They seemed proud of that too."',
             'Ring of the treaty: "We signed. The forest did not. We said so clearly, under the boughs. Human ears are '
             'not built for subtlety. That is not our failing."',
             'Ring of the Ruin: "In one hour the Tree let fall every golden leaf, and stood bare until the spring. We '
             'did not discuss it."',
             'This ring: "A human is reading this. How brave. Mind the roots."'],
         hidden='Between two rings, a pressed gold leaf and the path to a glade no human map has: "Since you have read '
                'so far, and quietly. Only this once."',
         chron='The elves reckon the ages by the rings of the Elder Tree; on the Night of the Ruin it dropped every leaf.',
         effect=('place', 'glade')),
    dict(key='ninenames', people='elf', title='The Nine Names', ch='III',
         where=('site:starhouse', 'site:windtower'), pages=[
             'Copied in a Varnish hand from an elven ring: "The mages asked us for the names of the stars. Human '
             'mouths cannot pull down a star by saying its name, any more than a dog can call the moon by barking."',
             '"We gave them nine. Small ones, in a ring round the small moon in the north. The price: that the road '
             'go round our wood for ever, and never show us its masonry."',
             '"They swore. We wrote the oath into the Tree. Two hundred years later their road came through the trees '
             'regardless. We answered the road-crews with arrows. We are answering them still."',
             '"The first of the nine went out. Then the second. We sat under the Tree and listened to the sky, and the '
             'sky did not say anything to us at all."',
             '"Nine. The ring round Vael is empty, and it is ours that emptied it. We underestimated the vulgarity of '
             'their ambition. We shall not mention this again."'],
         hidden='In the Varnish copyist\'s own hand at the foot: "They sold the names cheap, because they thought them '
                'worthless in our mouths. They were wrong once. I think it frightened them more than the falling did."',
         chron='The elves sold the Collegium the true names of the nine stars of the Crown of Vael; they do not speak of it.',
         effect=('riddle', 'fall', 2)),
    dict(key='starsong', people='elf', title='Starsong', ch='before',
         where=('set:elf', 'site:glade'), pages=[
             '"Once a year, on one breathless night, we gather in the glades and say the true names of the stars '
             'together. It is the only sound on earth the sky still cares to hear."',
             '"Each name is said once. Not louder than the one before. A voice that rises is a voice that has '
             'forgotten what it is for."',
             '"There are gaps in the song now. Nine in a ring in the north, and one in the middle of them. We sing '
             'round the gaps. It is harder than it sounds."',
             '"Humans may listen, at the edge of the glade, if they are quiet. They are seldom quiet."',
             '"When the song is done we do not clap. We are not that kind of people."'],
         hidden='Last ring: "If the gap in the middle is ever filled again, we shall sing that name first, and we shall '
                'not be too proud to be glad."',
         chron='On Starsong the elves say the true names of the stars together, and sing round the gaps in the north.',
         effect=('favour', 'elf')),
    # ---- the halflings
    dict(key='longtable', people='halfling', title='The Long Table Book', ch='before',
         where=('set:halfling', 'site:beehill'), pages=[
             '"Long Table, the year the river froze. Brought: four pies (Pansy), a ham (the Bracegirths, all of it, for '
             'once), cider (everyone), and a Big Person, lost, who was given the end seat and three helpings."',
             '"Long Table, the year of the wasps. Brought: honey (from the wasps, by Old Tam, who is now Young Tam\'s '
             'grandfather and very swollen). Gifts given away: eleven. Gifts given back: four. Fair."',
             '"Long Table, the year the Empire came. Brought: a clerk. Fed. Fed again. He stayed for pudding. He is '
             'still here, more or less."',
             '"It is very hard to murder someone who has just fed you second breakfast. Write that down. (Written.)"',
             '"Long Table, this year. Brought: whatever you have. Sit where there is a gap. There is always a gap."'],
         hidden='On the inside of the back cover, a recipe in a round brown hand: "Nut loaf, for when the Big Folk come. '
                'Make two. They always want the second."',
         chron='At the Long Table a whole halfling village dines as one and gives gifts away, in memory of Thessaly.',
         effect=('recipe', 'nut_loaf')),
    dict(key='pellam', people='halfling', title='Pellam\'s Ledger', ch='III',
         where=('set:halfling', 'site:pipeweed'), pages=[
             'The ledger itself, page one, in a clerk\'s best hand: "Census of the hill-folk of the green downs. Taken '
             'by Pellam, clerk of the third grade." Below it, the whole of the count: "A few; very content."',
             'A letter tucked inside: "Dear Mr Pellam, we hear you have been made Chief Clerk. Congratulations! We have '
             'sent a small bale for the occasion. Please do not count us. Love from all at Underbank."',
             'Another: "Dear Mr Pellam, the Emperor\'s chamberlain writes that his master was not himself without his '
             'evening pipe. We are so sorry to hear it. It must be the roads. Roads are so upsetting."',
             'Another: "Dear Mr Pellam, a man with a measuring rod has been round, counting doors. We are sure it is a '
             'mistake. No leaf will go down the hill until it is put right. Kind regards."',
             'Another: "Dear Mr Pellam, thank you. We hear he enjoys the herring. Underbank."'],
         hidden='On the last letter, in Pellam\'s own hand, much later: "I never counted them. I never meant to. I knew '
                'what the wink meant by the second spring. Best leaf in the world grows on the south slope past the '
                'hawthorn gate, and that is all the census anyone will get from me."',
         chron='A clerk named Pellam never counted the halflings; the Varnish court came to need their sweetleaf too much.',
         effect=('place', 'pipeweed')),
    dict(key='notjutting', people='halfling', title='The Almanac of Not Jutting', ch='before',
         where=('set:halfling', 'site:hedgegate'), pages=[
             '"First rule of building, from the age of the wyrms: do not jut. A wyrm burns what sticks up."',
             '"Dig in sideways. A round door, a turf roof, a wisp of smoke. From above you are a hill with a cold, and '
             'nobody burns a hill with a cold."',
             '"Second rule: make friends of anyone who might otherwise become a nuisance. A full guest burns nothing."',
             '"Third rule: a hedge is a wall that does not look like one. Grow them thick, and grow them round."',
             '"Fourth rule, added by the Empire: be overlooked. It is the same as not jutting, only with paperwork."'],
         hidden='Folded into the back: a sketch of a village that looks exactly like four hills and a hedge, and below it, '
                'in pencil: "This is us. You will walk past it. Most do."',
         chron='The halflings learned in the age of the wyrms never to jut: round doors, turf roofs, thick hedges.',
         effect=('place', 'hedgegate')),
    dict(key='breakfast', people='halfling', title='Second Breakfast', ch='III',
         where=('set:halfling',), pages=[
             '"First breakfast is for you. Second breakfast is for whoever has turned up."',
             '"Eggs, mushrooms, bread fried in what the bacon left. Do not hurry it. Nothing good was ever hurried, '
             'least of all a guest."',
             '"If the guest has a ledger, give him extra mushrooms. A man with his mouth full cannot count."',
             '"Elevenses is not a meal. It is a kindness to second breakfast, which was lonely."',
             '"Serve on the bench by the green door, in the sun, with a pipe after. The Empire fell. Second breakfast did '
             'not."'],
         hidden='The last page is only a recipe, with a gravy stain shaped like a hill.',
         chron='Second breakfast outlasted the Varnish Empire, by the halflings\' own account.',
         effect=('recipe', 'second_breakfast')),
    # ---- the gnomes
    dict(key='stake', people='gnome', title='The Stake Moved Four Paces', ch='III',
         where=('site:gnomes', 'site:mushwood'), pages=[
             '"Night one. Moved the surveyor\'s stake four paces west. Oak saved. Surveyor confused. Moved it back two, '
             'for fairness. Surveyor more confused. A good night."',
             '"Night nine. Tied one knot too many in the surveyor\'s chain. The league he measured came up short. They '
             'will cut the milestone wrong. We will go and look at it, later, often."',
             '"Night twenty. A teller left his astrolabe on the inn table. Took it apart. Put it back running a little '
             'smoother. Then, on reflection, backwards."',
             '"Full moon. Turned the mill-wheels the wrong way round. No reason. Practice."',
             '"The Empire says the East is an unruly country where no mason can lay a straight line. We say: thank '
             'you."'],
         hidden='A pencilled map in the back: a ditch, a milestone in it, and beside it, "still wrong, still lovely".',
         chron='The gnomes nudged the Empire out of the eastern woods with moved stakes and knotted chains.',
         effect=('place', 'wrongmile')),
    dict(key='oaks', people='gnome', title='What the Oaks Said', ch='III',
         where=('site:gnomes',), pages=[
             '"Ear to the bark, dusk. The big oak says: boots on the road, iron ones, many. Going east."',
             '"The beech by the ford says: they cut three of her cousins for a bridge. She is not speaking to the road."',
             '"The old oak says: the dead are walking the road at night, in a line, all leaning one way. She does not '
             'like it. Nor do we."',
             '"All the trees, one night, together: a great shudder from the west. Then nothing. Then the birds."',
             '"The road is empty now. The trees say the stones are growing moss, slowly, and they are in no hurry."'],
         hidden='A last note: "The trees remember where every road went, even the ones that go nowhere now. Ask a tree. '
                'Bring it a little water. It likes to be asked."',
         chron='The gnomes listened at the bark and the trees told them every iron boot on the Empire\'s roads.',
         effect=('way',)),
    dict(key='count', people='gnome', title='The Count Kept Private', ch='before',
         where=('site:gnomes', 'site:mushwood'), pages=[
             '"We counted the stars with our own instruments. We got a different number from everyone. It is ours. We '
             'shall not say it."',
             '"Counted again. Nine fewer, in a ring in the north. We knew before the tellers did. We did not tell the '
             'tellers. They do not like being told."',
             '"Counted again. Ten fewer. The middle of the ring is gone. It went west."',
             '"Our number is still our own. It is smaller now. We are sorry about that."'],
         hidden='Scratched very small inside the cover: "If ever the number grows again by one, ring every bell in every '
                'hamlet. We shall know why."',
         chron='The gnomes keep their own count of the stars and saw the ring in the north empty before anyone.',
         effect=('riddle', 'fall', 2)),
    dict(key='winter', people='gnome', title='The First Winter', ch='before',
         where=('site:gnomes',), pages=[
             '"On the first hard frost every shutter in the hamlet shuts. We know why."',
             '"We will not say why."',
             '"It was a long time ago. It walked through the woods in the frost. It was very tall and it did not leave '
             'footprints."',
             '"That is enough."'],
         hidden='Nothing. The last pages are blank, and someone has taken great care that they stay blank.',
         chron='On the first hard frost the gnome hamlets shut and vanish, on account of the First Winter.',
         effect=None),
    # ---- the kobolds
    dict(key='shine', people='kobold', title='The Shine Tally', ch='VI',
         where=('site:kobolds',), pages=[
             'Scratches on a slate: "Moon of the Small Rain. Polished: two buttons, one buckle. Good month."',
             '"Moon of the Big Rain. Polished: three buttons, one buckle, the Sky Piece. The Sky Piece is warm again. '
             'Polished it twice. It hummed. Nobody slept. Very good month."',
             '"Moon of the Long Dark. The dwarves sent one with a sack again. Gave her the lamp back. Kept the sack. '
             'Gave the sack back in spring, with a button in, to be nice."',
             '"Moon of the Shine. Whole clan, in the dark, buffing. The Sky Piece at the bottom of the heap. The sack of '
             'sparks under it. Nobody tell."',
             '"Moon of the Visitor. Someone tall is reading this. Hello. Do not take the Sky Piece. Polish something."'],
         hidden='On the back of the last slate, a careful drawing of a warren, with a heap at the bottom and a star '
                'scratched on the heap, very proud.',
         chron='The kobolds keep a piece of the star of 990 at the bottom of their deepest hoard, and polish it.',
         effect=('place', 'kobolds')),
    dict(key='sawsky', people='kobold', title='She Who Saw the Sky', ch='before',
         where=('site:kobolds',), pages=[
             '"Long ago, one of us went up the chimney-crack, up and up, to the top of the mountain."',
             '"She put her head out. Above: dark. In the dark: sparks. All of them. More than all of them."',
             '"Too high. Could not reach. Tried. Fell. Got up. Tried."',
             '"Came down and told us. Every one of us since is born wanting one. Cannot have one. Polish what we '
             'have."'],
         hidden='Under the last slate, a single bright pebble, buffed till it shines. Someone left it for the reader.',
         chron='Every kobold aches to hold a star since one of them climbed out and saw the sky.',
         effect=('lore',)),
    dict(key='spikes', people='kobold', title='The Bridge Spikes', ch='III',
         where=('site:kobolds',), pages=[
             '"Took the bronze spikes out of the soldiers\' bridge. Very shiny. All of them."',
             '"Bridge fell in the gorge. Very sorry. Kept the spikes."',
             '"Soldiers came into the tunnels to be angry. Swept the cave first, very clean, for guests. Left their '
             'buttons in a nice heap. Drew a bow on the wall. To say sorry."',
             '"Soldiers were more angry. Do not understand soldiers."'],
         hidden='A drawing of the bow from the wall, copied very carefully, so you can say sorry too if you need to.',
         chron='The kobolds once took every bronze spike out of an Imperial bridge, and were sorry, and kept the spikes.',
         effect=None),
    # ---- the goblins
    dict(key='swapday', people='goblin', title='The Honest Day Book', ch='before',
         where=('site:ravine', 'city'), pages=[
             '"Swap Day. One pot for one knife. Pot had a hole. Said so. Felt strange."',
             '"Swap Day. Map of a ruin for a cheese. Map was true. Cheese was true. Both of us very uneasy."',
             '"Swap Day. A man asked what we were doing. Told him the truth. He did not believe it. Normal."',
             '"Swap Day. Twenty-four hours, every trade square. Remind ourselves what it feels like. It feels like an '
             'itch."',
             '"Day after Swap Day. Back to normal. Relief all round."'],
         hidden='Last page: "If you are reading this, you got it fair. Probably. Today, anyway."',
         chron='On Swap Day the goblins trade honestly for a day and a night, so as not to forget what it is like.',
         effect=('lore',)),
    dict(key='collegium', people='goblin', title='What We Heard Under the Collegium', ch='IX',
         where=('site:ravine', 'city'), pages=[
             '"Under the mud-city, in the big drains. Over our heads the Collegium, chanting, every night, louder."',
             '"Same verse over and over. Old Snig says it is a pulling song. Pulling what, says Nib. Up, says Snig."',
             '"Up is where the small moon is. Nobody pulls a moon. Snig says watch them."',
             '"Snig says pack the pots. Nobody up top noticed. Nobody up top ever notices."',
             '"Went to the hills. Did not look back. Heard it anyway."'],
         hidden='Scratched under it, with a map: "The big drains still go up, where they did not fall. Narrow. Wet. Up '
                'into the underside of the hanging part. Nobody watches the cracks of the world."',
         chron='A week before the Ruin the goblins left the drains under the Sky-Seat, having heard what was chanted.',
         effect=('drains',)),
    dict(key='soldtwice', people='goblin', title='Sold Twice', ch='V',
         where=('site:ravine', 'city'), pages=[
             '"Sold the governor the plot against the governor. Sold the plotters the governor\'s guards\' rota. Good '
             'week."',
             '"Carried a love letter both ways across the river. Same price both ways. They married. We were not '
             'invited."',
             '"The law calls us the Small Uncounted. Means nobody locks us up. Means we hear everything."',
             '"A goblin in chains has already slipped them and sold the padlock. Put that on a milestone."'],
         hidden='The last leaf is a bill, itemised, for "secrets, assorted", made out to two different lords, both paid.',
         chron='The goblins sold the secrets of the Varnish to both sides at once, and nobody counted them.',
         effect=('lore',)),
    # ---- the gnolls
    dict(key='lastverse', people='gnoll', title='The Last Verse', ch='before',
         where=('site:gnolls',), pages=[
             'Cut in a thigh-bone: "Two moons ran over the grass. The big one led. The small one followed, in the north, '
             'and said nothing."',
             '"We sang to the big one. The small one did not need singing. She was older than singing."',
             '"Her crown had nine sparks. One night a spark went. Then another. We howled. The tall ones did not hear."',
             '"The verse says: the small one will be dragged down by those who count. The verse was right."',
             '"Now one moon. We still sing two parts. One part is a hole."'],
         hidden='The last bone has a second verse cut on its inside, very small: "Round the hill the wrong way round, '
                'when the moon is full and white. The dusk-folk have a door. Do not eat."',
         chron='The gnolls\' moon-song remembers two moons, and that the small one would be dragged down.',
         effect=('riddle_any', 'fall')),
    # ---- the lizardfolk
    dict(key='longbone', people='lizard', title='The Long Bone', ch='III',
         where=('site:stilts', 'site:eggmounds'), pages=[
             'A marsh-bull\'s femur, notched: "Our census of the Varnish. Not how many lived in their cities. How many '
             'walked into the fen and did not walk out."',
             '"First causeway: the fen ate it in one thaw. No notch; nobody on it."',
             '"Second causeway: same. One notch. A surveyor, curious."',
             '"Third causeway held. A legion came along it to count us. Many notches. It is a long bone."',
             '"After that they went round. They said they always meant to. One more notch, for the lie."'],
         hidden='Along the end of the bone, a line of small notches leads to a drawing: the third causeway, sunk but '
                'still there under the reeds, and where it goes.',
         chron='The lizardfolk counted the Varnish soldiers who went into the fens on a long bone.',
         effect=('place', 'causeway')),
    dict(key='peat', people='lizard', title='Pressed Into the Peat', ch='III',
         where=('site:stilts',), pages=[
             '"Dead men stood in the duckweed, waist-deep, waiting for orders. Nobody came with orders."',
             '"We waded out and pressed them down into the warm peat, faces to the sky, as we bury our own."',
             '"Not mercy. A dead man standing in the reeds startles the fish."',
             '"The peat keeps them. They do not get up. Good peat."'],
         hidden='A last notch, deep: "The fens have no standing dead now. Not one. Ask the fish."',
         chron='The lizardfolk alone gave the Empire\'s working dead rest, pressing them into the peat.',
         effect=('lore',)),
    # ---- the orcs
    dict(key='cameup', people='orc', title='When We Came Up', ch='VII',
         where=('set:orc', 'site:orcfarm'), pages=[
             '"There were four hundred who went down. We know because they told us, the ones who still remembered '
             'talking."',
             '"We do not know their names. The clerks did not write them. They wrote a number, and a kind of animal."',
             '"So we give each child one of the four hundred, and that child carries it. We have had to make up the '
             'names. We have made up good ones."',
             '"When the sky fell nobody came to the pits in the morning. We waited a day. Then we climbed out."',
             '"The Empire called us worse than brutes. The Empire is dust. We are not. That is the whole of our '
             'history, and it is enough."'],
         hidden='On the last leaf, four hundred names, each in a different hand, and at the bottom: "If you are not one '
                'of us and you read this: now you know. Do not say it to an orc unless an orc says it to you first."',
         chron='The orcs count their beginning from the morning they climbed out of the pits in the east.',
         effect=('riddle_any', 'orcs')),
    # ---- the north
    dict(key='names', people='north', title='The Names Kept', ch='IV',
         where=('north',), pages=[
             'A roll of names, very long, in many hands, older at the top: "Aru. Mena. Corr. Old Tasso and his '
             'daughters. Bel the smith."',
             'A note beside them: "These came over the wall. Who sent them, and why, the roll does not say. Only that '
             'they came, and their names."',
             '"Every child is told: ask a stranger\'s name, and use it. It is only manners. Nobody remembers why it '
             'matters so much."',
             '"The roll is read out at the Light-Feast, every name, all night. Nobody falls asleep. It would be rude to '
             'the names."'],
         hidden='At the very bottom, added in our own day: "And whoever reads this roll through: your name, too. Tell it '
                'at any hall of the north and it will be used."',
         chron='The folk of the north keep a roll of names of those who came over the wall, and do not know why.',
         effect=('north',)),
    dict(key='torches', people='north', title='The Torches on the Snow', ch='IX',
         where=('north',), pages=[
             '"The small moon came loose in the sky and fell south. The old ones knew at once what it was. The old ones '
             'always knew the stars."',
             '"Word had come up the roads of the scratched hand for years: our blood was still down there, in the mud."',
             '"We went south in our tens of thousands, over the snow, with torches. Not to burn. To warn, and to fetch '
             'them home."',
             '"On the wall a light answered us. Then the beacons behind them, all the way south. They were facing the '
             'wrong way. They let us through."',
             '"One stayed in his tower. We left him bread. We think he was counting."'],
         hidden='The last line is half rubbed away: "We brought our people home, and then we forgot why we had gone. '
                'That is how it is with the north. We keep the names, and lose the reasons."',
         chron='On the Night of the Ruin the north came over the wall with torches, to warn and to fetch its kin home.',
         effect=('lore',)),
    # ---- the fey: only in their court
    dict(key='feypact', people='fey', title='The First Pact, as the Fey Keep It', ch='before',
         where=('court',), pages=[
             'In letters that move when you are not looking at them: "The forest by day to the elves. Noted."',
             '"The hills by night to us. Noted. Every hill. Every night. They did not say which hills. We did not ask."',
             '"They think they had the better of us. They have the day. Days end."',
             '"We keep every bargain to the letter. The letter is the bargain. The spirit is what people say when they '
             'have read it too late."',
             '"You are here. The moon was full and you went round the wrong way. To the letter, you may stay as long as '
             'you like. To the letter, so may time."'],
         hidden='The last leaf of gold is blank until you close the book. Then it says your name, and the day you came '
                'in, and leaves the day you will go out empty.',
         chron='You found the court under the hill, and read the pact as the fey keep it.',
         effect=None),
]
BOOK = {b['key']: b for b in BOOKS}

# ------------------------------------------------------------------ voices: everyday talk, in each people's own tone
VOICES = {
    'elf': [
        'A human. In the glade. How brave of you, and how loud.',
        'The price is fair. I know, because I set it.',
        'There is a ruin to the east. Your people built it. We watched.',
        'Do come back. Or do not. The Tree will remember you either way, for a while.',
        'Your Empire was a long, loud noise. Then it was quiet. We much prefer the quiet.',
        'You walk as if the ground owed you something. It is charming, in a way.',
        'We do not hurry. You hurry, and look where it got you.',
        'The stars in the north? What lovely boots. Did a dwarf make them? One can always tell.',
        'Another treaty? How kind. Do read it twice. Then read it again, slowly, and think of us.',
        'We were here before the hills had names. We named some of them. The good ones.',
        'Thank you. No, really. It is not often a human surprises us, and you did, a little.',
        'Your kings come and go so quickly. We have stopped learning their names. It saves time.',
    ],
    'dwarf': [
        'Entered. Go on.',
        'You owe nothing. Yet. Mind it stays that way.',
        'Surface folk. Always in a hurry, never in the ledger.',
        'A debt may not outlive the debtor. A grudge may.',
        'We did not lend them our god. We do not lend much.',
        'Ask iron a question and it answers with a clang. Ask me one and you will get less.',
    ],
    'halfling': [
        'Sit down, sit down. Have you eaten? You have not. I can tell.',
        'Count us? Oh, there are only a few of us. And all very content.',
        'A full guest burns nothing. Mother always said so.',
        'Second breakfast is ready when you are. It is always ready, really.',
        'Big Folk do worry so. Have a pipe. Things look rounder after a pipe.',
    ],
    'gnome': [
        'Hm? Oh. Hello. I was listening to the beech. She is in a mood.',
        'Have you tried taking it apart? It usually helps.',
        'No, we did not move the milestone. Which milestone?',
        'The trees say you came by the road. Everyone comes by the road. It is a road.',
        'Shh. The oak is about to say something about you.',
    ],
    'orc': [
        'You want something. Say it plainly.',
        'We came up out of the ground with nothing. Look what we have now. Mind your hands near it.',
        'Brute? Say it again. Slowly. So I can hear it properly.',
        'The Empire is dust. We are not. That is the whole of it.',
    ],
    'goblin': [
        'Nobody watches the cracks. That is where we live, and where we hear everything.',
        'Buying or selling? Both? A gentleman.',
        'Honest? Today? No, Swap Day is not for weeks.',
        'Tell nobody I told you. Then tell everybody. Costs extra.',
    ],
}
# what an elf says once you have read The Nine Names
ELF_KNOWN = 'You have read that one. Then you know the one thing we got wrong. Please do not mention it to the others.'
