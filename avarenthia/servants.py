"""The other sixteen servants of the Hollow King (great evils parts 3 and 4, rounds 31-32), on the frame of evils.py
and shadow.py: each kind's words and lair (KINDS, read into evils.EVILS), its weight, its goal, lever, lieutenants,
weakness and relic (read into shadow.SERVANT), its lever on the world (LEVERS), its boss and the boss's deck (BOSSES,
read into data.MONSTERS; KITS, read into bosses.KITS), how its mark looks on the land (TAINT) and what refugees tell
of it (TALES). Pure data at the top, so evils, shadow, data and bosses can read it without a circle; the levers import
what they need when they run.

Round 31 built the light and three middle ones: the Ifrit, the Nightmare, the Gorgon, the Wild Hunt, the Hag, the Rat
King, the Queen under the Hill, the Vampire Count. Round 32 the rest: the Keening Woman, the Thunderbird, the
Lindworm, the Sold King, the False Prophet, the Debt Lord, the Giant King, the Demon Prince."""
import random

WEIGHT = {'ifrit': 'light', 'mare': 'light', 'gorgon': 'light', 'wildhunt': 'light', 'hag': 'light',
          'ratking': 'middle', 'feyqueen': 'middle', 'vampire': 'middle', 'banshee': 'middle', 'thunderbird': 'middle',
          'lindworm': 'middle',
          'soldking': 'heavy', 'prophet': 'heavy', 'debtlord': 'heavy', 'giantking': 'heavy', 'demon': 'heavy'}


def _k(names, title, boss, lair, style, tag, depth, base, wall, terrain, taint, taint_name, fg, event, hunt, glyph,
       hunt_names, cult, whispers, rumors, lore, omen, defeat, here, signs):
    return dict(names=names, title=title, boss=boss, lair=lair, style=style, tag=tag, depth=depth, base=base, wall=wall,
                terrain=terrain, taint=taint, taint_name=taint_name, fg=fg, event=event, hunt=hunt, hunt_glyph=glyph,
                hunt_names=hunt_names, cult=cult, whispers=whispers, rumors=rumors, lore=lore, omen=omen, defeat=defeat,
                here=here, signs=signs)


KINDS = {
    # ------------------------------------------------------------ light: awake from the start, in its own land
    'ifrit': _k(
        ['Azhar of the Brass Lamp', 'Qarim the Smokeless', 'The Red Wind'], 'the Ifrit', 'ifrit', 'The Glass Tomb',
        'cave', 'lair_ifrit', 4, 6, '#c09050', ('desert',), 'sand', 'creeping sand', (240, 150, 70), 'famine',
        ['dune_rider', 'sand_scorpion', 'cinderling'], 'I', ['The Riders of {short}', 'The Smokeless Host'],
        ('The Brass Brotherhood', 'Brass', ['cultist', 'dune_rider', 'cinderling'], 'Brass Spire', 'Glass Tower'),
        ['The wind turns hot and smells of hot metal.', 'Sand hisses across the path, though the air is still.',
         'For a moment the horizon burns like a forge mouth.', 'A voice in the wind offers you three wishes. You say nothing.'],
        ['The wells of {short}\'s country are sand to the brim.', 'Another caravan never came in. Not even the camels.',
         'They say a man let {short} out of a lamp, and wished for the wrong thing.'],
        'a spirit of smokeless fire, freed from a brass lamp. The wells dry up, the sand creeps over the fields, and the '
        'caravans do not come in.',
        'A hot wind from the desert. {name} grows stronger, and the sand creeps further.',
        '{name} burns down to a curl of smoke, and the smoke goes back into the lamp. The wind drops.',
        'Sand over the fields, and the wells are dry.',
        ['The oasis wells are sinking. The camel men say the desert breathes out.',
         'Caravans from the south come in thin, or not at all.',
         'A sandstorm on a cloudless day, three days running.']),
    'mare': _k(
        ['The Mare of Morrow Moor', 'Old Nightmare', 'The Black Foal'], 'the Nightmare', 'nightmare', 'The Sleepless Barrow',
        'cave', 'lair_mare', 3, 5, '#5a5070', ('grass', 'hills'), 'dreams', 'sleepless land', (150, 130, 200), 'plague',
        ['shade', 'hungering_shade', 'wisp'], 'M', ['The Dreams of {short}', 'Sleepwalkers'],
        ('The Wakeful', 'Wakeful', ['cultist', 'shade', 'wisp'], 'Wakeful Spire', 'Dream Tower'),
        ['You blink, and an hour has gone.', 'Someone sits on your chest in the dark, and then no one does.',
         'You hear hooves outside the camp, slow, all night.', 'You dream you are awake. You are not sure which.'],
        ['Nobody in {short}\'s country has slept a night through since spring.', 'The inns out on the moor stand empty.',
         'They say she rides on the chests of the sleeping, and they wake grey.'],
        'the Mare, who rides the sleeping. In her land no rest is rest, the inns stand empty and folk go grey.',
        'Nobody slept last night. {name} grows stronger, and the sleepless land spreads.',
        '{name} rears and fades like a bad dream at cockcrow. That night, the whole country sleeps.',
        'The houses here are dark, but nobody inside is asleep.',
        ['Folk on the moor say they have not slept in weeks.', 'An innkeeper sold up and left: nobody slept in his beds.',
         'Children wake screaming every night, all of them at once.']),
    'gorgon': _k(
        ['Stheira the Gorgon', 'The Stone Widow', 'Medalla of the Grey Hill'], 'the Gorgon', 'gorgon', 'The Garden of Statues',
        'rooms', 'lair_gorgon', 4, 6, '#8a8a7a', ('hills', 'grass'), 'stone', 'stone country', (180, 186, 160), 'plague',
        ['basilisk', 'cockatrice', 'viper_warrior'], 'G', ['The Stone-Eyed', 'The Children of {short}'],
        ('The Silent Order', 'Silent', ['cultist', 'viper_warrior', 'basilisk'], 'Silent Spire', 'Stone Tower'),
        ['A statue by the road, of a man running. You do not remember it being there.', 'Something hisses in the rocks.',
         'Every bird on the hill is stone.', 'You catch your own face in a puddle and look away, quickly.'],
        ['The villages in {short}\'s hills are full of statues. Good likenesses, they say.',
         'Nobody takes the hill road any more.', 'They say she was beautiful once, and a goddess was jealous.'],
        'a woman with snakes for hair whose look turns flesh to stone. Her country fills with statues, and the roads go quiet.',
        'Another village is silent. {name} grows stronger, and stone country spreads.',
        '{name} falls, and the snakes go still. Down in the villages, a statue blinks.',
        'Statues stand in the fields here, all facing the same way.',
        ['A shepherd found his whole flock turned to stone.', 'The hill road is empty: the carters will not use it.',
         'Statues in the village square that nobody carved.']),
    'wildhunt': _k(
        ['The Wild Hunt', 'The Grey Huntsman', 'Herne of the Night Roads'], 'the Wild Hunt', 'huntmaster', 'The Hollow Oak',
        'cave', 'lair_hunt', 3, 6, '#5a6a50', ('forest',), 'hunt', 'hunted roads', (170, 200, 150), 'war',
        ['hellhound', 'hellhound', 'wraith'], 'H', ['The Hounds of {short}', 'The Riders of the Hunt'],
        ('The Horn-Sworn', 'Horn', ['cultist', 'hellhound', 'wraith'], 'Horn Spire', 'Antler Tower'),
        ['A horn, far off, in the middle of the night.', 'Hoofbeats overhead. You look up, and there is only cloud.',
         'Dogs bay somewhere in the wood, a great many of them.', 'A rider\'s cloak flaps past you in the dark, and nobody in it.'],
        ['The messengers do not get through any more. News comes late, or not at all.',
         'The Hunt rode over the high road last night. Two carters are gone.', 'They say {short} rides when the moon is dark.'],
        'a host of dead riders and their hounds who ride the night roads. Travellers vanish, messengers never arrive, and '
        'the trade over land stops.',
        'The horn sounds again. {name} grows stronger, and the hunted roads spread.',
        'The horn breaks. {name} and the hounds ride up into the clouds, and do not come down.',
        'The road here is empty, and no one travels it at night.',
        ['Messengers ride out and do not arrive.', 'Travellers keep to the inns after dark now, every one of them.',
         'A carter\'s horse came home with an empty cart and frost on its mane.']),
    'hag': _k(
        ['Grandmother Bonelegs', 'Old Mother Yaga', 'The Hag of the Walking Hut'], 'the Hag', 'hag', 'The Walking Hut',
        'cave', 'lair_hag', 3, 5, '#6a5a40', ('forest', 'swamp'), 'curse', 'cursed land', (170, 190, 120), 'famine',
        ['weald_hag', 'scarecrow', 'wisp'], 'h', ['The Crows of {short}', 'The Cursed'],
        ('The Coven of the Hut', 'Coven', ['cultist', 'weald_hag', 'scarecrow'], 'Crow Spire', 'Hag Tower'),
        ['The milk in your flask has turned.', 'Something on long thin legs walks across the far field.',
         'A crow says a word. It is your name.', 'Your boots are on the wrong feet. You put them on right this morning.'],
        ['The milk sours in {short}\'s country, and the cows lie down and die.', 'The hut walked past the mill last night.',
         'They say she eats the children who do not answer her riddles.'],
        'an old witch in a hut that walks on bird\'s legs. The milk sours, the cattle sicken, and the witches\' circles '
        'serve her.',
        'Sour milk in every pail. {name} grows stronger, and the cursed land spreads.',
        '{name} falls, and the hut sits down on its legs for good. The milk is sweet again.',
        'The grass here is yellow, and the cows will not eat it.',
        ['The cows are sick all down the valley.', 'Somebody saw a house walking at the edge of the wood.',
         'The witches\' circles are meeting every night.']),
    # ------------------------------------------------------------ middle: wakes halfway, a few baronies or a coast
    'ratking': _k(
        ['King Squeal', 'The Gnawing King', 'Old Seven-Tails'], 'the Rat King', 'rat_lord', 'The Undercity',
        'rooms', 'lair_rat', 4, 7, '#6a6050', ('city',), 'plague', 'plague streets', (170, 150, 110), 'plague',
        ['rat', 'rustgnawer', 'ghoul'], 'r', ['The Swarm of {short}', 'The Gnawing Host'],
        ('The Plague Brethren', 'Plague', ['cultist', 'rat', 'ghoul'], 'Plague Spire', 'Sewer Tower'),
        ['Something runs over your foot in the dark.', 'Scratching inside the walls, all night.',
         'A dead rat on the road, then another, then twenty.', 'Your bread has a bite out of it you did not take.'],
        ['Plague in the city. The markets are shut and the gates closed.', 'The rats are bold as dogs in {short}\'s streets.',
         'They say a hundred rats grew together by the tails, and one of them wears a crown.'],
        'a knot of a hundred rats grown together by the tails, under a city. Plague runs through the streets, the markets '
        'shut, the gates close.',
        'Plague again. {name} grows stronger, and the plague streets spread.',
        '{name} comes apart into a hundred dead rats. The streets above are quiet.',
        'Shut doors, chalk crosses on them, and rats in the gutters.',
        ['Rats in the granaries, more every week.', 'A fever in the city\'s poor quarter.',
         'The gates are closed to strangers: sickness.']),
    'feyqueen': _k(
        ['The Queen under the Hill', 'Lady Thistledown', 'The Erl-Queen'], 'the Queen under the Hill', 'fey_queen',
        'The Hollow Hill', 'cave', 'lair_fey', 4, 7, '#5a7a50', ('forest',), 'fey', 'fey wood', (150, 220, 160), 'famine',
        ['pixie', 'dryad', 'shimmercat'], 'f', ['The Court of {short}', 'The Fair Folk'],
        ('The Green Court', 'Court', ['cultist', 'pixie', 'dryad'], 'Thorn Spire', 'Green Tower'),
        ['Music under the ground, and laughter.', 'You walked an hour, and the sun has not moved.',
         'A ring of white mushrooms where you camped last night.', 'A child at the edge of the wood waves. She has no shadow.'],
        ['The wood came up to the village wall overnight.', 'A child of the miller\'s is not the miller\'s child any more.',
         'They say those who dance in her hill come out a hundred years later.'],
        'the queen of the fair folk under her hill, not elven and older than elves. The wood walks forward, children are '
        'changed, and time runs strangely near her hills.',
        'The wood is closer this morning. {name} grows stronger, and the fey wood spreads.',
        '{name} goes out like a will-o\'-the-wisp. The hill is only a hill, and the wood stands still.',
        'The trees here stand too close, and the light is green and wrong.',
        ['The forest is moving towards the fields.', 'A changeling child in the village, they say.',
         'Two woodcutters came back from the wood. They say it was a night. It was a year.']),
    'vampire': _k(
        ['Count Malvoren', 'Countess Drazha', 'The Pale Count'], 'the Vampire Count', 'vampire_count', 'Castle Pallor',
        'rooms', 'lair_vampire', 4, 8, '#6a4050', ('hills', 'forest'), 'pale', 'pale country', (200, 120, 140), 'undead',
        ['vampire_spawn', 'bat', 'wolf'], 'V', ['The Thralls of {short}', 'The Night Brides'],
        ('The Crimson Court', 'Crimson', ['cultist', 'vampire_spawn', 'bat'], 'Crimson Spire', 'Blood Tower'),
        ['A bat flies past, then a hundred bats.', 'A coach without a driver passes on the road. The horses are black.',
         'There is a wedding invitation in your pack. It is addressed to you.', 'Your reflection in the stream is late.'],
        ['The young lord married a lady from the east. Now he only rides at night.',
         'The heirs of the house are pale and strange, all of them.', 'They say {short} has been married seven times.'],
        'a dead lord who marries into the houses of the living. Heirs grow pale and strange, and a house belongs to him '
        'before anyone notices.',
        'Another wedding at night. {name} grows stronger, and the pale country spreads.',
        '{name} crumbles to ash in the light. Somewhere a young lord wakes as from a long fever.',
        'Garlic over every door, and no one out after dusk.',
        ['A lord\'s heir was married in the night, by torchlight.', 'Cattle found drained, with two marks on the neck.',
         'The young lady of the manor will not come out in the sun.']),
    'banshee': _k(
        ['The Keening Woman', 'The Washer at the Ford', 'Grey Moira'], 'the Keening Woman', 'keening_woman',
        'The Mourning Ford', 'cave', 'lair_banshee', 4, 7, '#7a8090', ('hills', 'grass', 'coast'), 'keening',
        'mourning land', (190, 200, 220), 'undead',
        ['ghost', 'banshee', 'wraith'], 'B', ['The Mourners of {short}', 'The Grey Wailers'],
        ('The Mourning Sisters', 'Mourning', ['cultist', 'ghost', 'banshee'], 'Grey Spire', 'Weeping Tower'),
        ['A woman wails somewhere in the night, on and on.', 'A grey figure washes a shirt at the ford. It is yours.',
         'The wind carries a name. Not yours, this time.', 'Every dog in the valley howls at once, and stops.'],
        ['She wailed outside the castle last night. The old lord was dead by morning.',
         'Three lords dead in one winter, and three children on their thrones.',
         'They say she washes the shirts of those who are going to die.'],
        'a grey woman who keens for the great. Where she wails a lord dies: then come the fights over who rules, and the '
        'child kings.',
        'She wailed again last night. {name} grows stronger, and the mourning land spreads.',
        '{name} gives one last cry, and is only mist on the water.',
        'Black cloth hangs on the doors here, for a lord who died.',
        ['A lord died in the night, for no reason anyone can name.', 'Someone heard a woman wailing on the castle walls.',
         'A child sits on the throne, and his uncles are counting.']),
    'thunderbird': _k(
        ['The Thunderbird', 'Wakinyan the Storm-Wing', 'Old Lightning'], 'the Thunderbird', 'thunderbird', 'The Storm Eyrie',
        'cave', 'lair_storm', 4, 7, '#6a7090', ('hills',), 'storm', 'storm country', (190, 200, 255), 'fire',
        ['storm_spirit', 'giant_hawk', 'thunderer'], 'T', ['The Storm-Wings of {short}', 'The Sky Hunters'],
        ('The Storm-Callers', 'Storm', ['cultist', 'storm_spirit', 'thunderer'], 'Storm Spire', 'Thunder Tower'),
        ['Thunder from a clear sky.', 'Your hair stands up. The air smells of iron.', 'A shadow with wings as wide as a '
         'field passes over the clouds.', 'Lightning strikes the same hill three times.'],
        ['Lightning burned the fields of the whole valley. The harvest is ash.', 'No ships leave the harbour: the storms.',
         'They say {short} beats its wings and the thunder comes.'],
        'a bird as big as a cloud whose wings beat the thunder. Lightning burns the fields, storms flatten the harvest, and '
        'ships stay in harbour.',
        'Thunder all night. {name} grows stronger, and the storm country spreads.',
        '{name} falls out of the sky like a dropped cloak, and the clouds break up behind it.',
        'Burnt fields, and the smell of a storm that never quite passes.',
        ['Summer storms every afternoon, and lightning in the fields.', 'The fishing boats stay in: the sea is wild.',
         'The haystacks of three villages burned in one night: lightning.']),
    'lindworm': _k(
        ['The Lindworm', 'Nidhogg the Gnawer', 'Old Coil-under-the-Mountain'], 'the Lindworm', 'lindworm', 'The Worm Road',
        'cave', 'lair_worm', 5, 8, '#7a6a50', ('dwarf',), 'deep', 'shaken ground', (190, 160, 110), 'collapse',
        ['tunnel_borer', 'burrowback', 'stonemaw'], 'L', ['The Burrowers of {short}', 'Things from below'],
        ('The Deep Sworn', 'Deep', ['cultist', 'grey_dwarf', 'tunnel_borer'], 'Deep Spire', 'Worm Tower'),
        ['The ground shivers under your feet, and is still.', 'A low grinding, deep below, like a millstone.',
         'Dust trickles from the rock above.', 'You find a tunnel in the hillside as round as a barrel, and still warm.'],
        ['The dwarves\' deep mine fell in. Forty under the stone.', 'The grudge-books of the holds are full this year.',
         'They say {short} gnaws at the roots of the mountains.'],
        'a wingless dragon that bores through the roots of the mountains. Mines fall in, the holds shake, and the dwarves\' '
        'grudge-books fill up.',
        'The mountain shook. {name} grows stronger, and the shaken ground spreads.',
        '{name} lies still at last in its own tunnel. The mountains are quiet.',
        'Cracks run through the ground here, and the wells taste of stone.',
        ['A mine fell in at the dwarf hold.', 'The ground shook under the hills, three times in a week.',
         'Dwarves are leaving the old galleries.']),
    # ------------------------------------------------------------ heavy: wakes late, a whole realm or more
    'soldking': _k(
        ['King Aldmar the Sold', 'King Corvin the Black Banner', 'Queen Hesse the Bought'], 'the Sold King', 'sold_king',
        'The Black Keep', 'rooms', 'lair_sold', 5, 8, '#5a5060', ('grass', 'hills'), 'banner', 'black banner',
        (150, 140, 170), 'war',
        ['knight', 'soldier', 'robber_knight'], 'K', ['The Black Lances of {short}', 'The Turncoats'],
        ('The Black Banner', 'Banner', ['knight', 'soldier', 'cultist'], 'Banner Keep', 'Black Tower'),
        ['A black banner on a far hill.', 'A herald reads a proclamation in a square. Nobody cheers.',
         'Soldiers on the road, wearing new colours.', 'Someone has painted out the old king\'s arms on a milestone.'],
        ['{short} sold his soul for the crown of the empire, they say.', 'His knights burn the villages of the loyal.',
         'The old oaths mean nothing to him now.'],
        'a king who sold himself for the crown of the empire. He breaks his oaths, makes war on his neighbours, and flies '
        'the black banner over what he takes.',
        'A black banner over another keep. {name} grows stronger.',
        '{name} falls, and the black banner falls with him. His own knights tear it down.',
        'Black banners on the towers here, and gallows at the crossroads.',
        ['A king called up his vassals, and nobody knows against whom.', 'Knights in black ride the border.',
         'The king\'s heralds read new oaths in every town.']),
    'prophet': _k(
        ['The Prophet Ezran', 'Mother Halde of the Ninth Sign', 'The Barefoot Saint'], 'the False Prophet',
        'false_prophet', 'The Tabernacle', 'rooms', 'lair_prophet', 5, 8, '#8a7a50', ('grass',), 'faith', 'zealot land',
        (240, 220, 140), 'war',
        ['cultist', 'holy_knight', 'berserker'], 'P', ['The Faithful of {short}', 'The Burning Brethren'],
        ('The Ninth Sign', 'Sign', ['cultist', 'cultist', 'holy_knight'], 'Sign Spire', 'Bell Tower'),
        ['A crowd sings in a field, all night.', 'Someone has nailed a sermon to a tree.',
         'Flagellants pass on the road, singing, bleeding.', 'Bells ring in a village with no church.'],
        ['The peasants have left the fields to follow {short}.', 'The Church is split: half the priests preach his word.',
         'His holy army burns the tithe barns.'],
        'a prophet with a false faith and a true following. The Church splits, the peasants rise, and his holy army burns '
        'what the old faith built.',
        'Another village burns its priest. {name} grows stronger, and the zealot land spreads.',
        '{name} falls, and his last sermon dies in his mouth. His followers stand in the field and do not know where to go.',
        'Sermons nailed to every door, and the old shrines broken.',
        ['A new preacher in the villages, and the priests do not like him.', 'Peasants walking off the fields to follow a man.',
         'A tithe barn burned, and singing round it.']),
    'debtlord': _k(
        ['Master Orsolo Pell', 'The Usurer of Ash Street', 'Lady Venna Coin'], 'the Debt Lord', 'debt_lord',
        'The Counting House', 'rooms', 'lair_debt', 5, 8, '#7a7050', ('grass', 'coast'), 'debt', 'pledged land',
        (230, 200, 90), 'famine',
        ['mercenary', 'crossbow', 'brigand'], '$', ['The Bailiffs of {short}', 'The Collectors'],
        ('The Ledger', 'Ledger', ['mercenary', 'crossbow', 'cultist'], 'Ledger House', 'Counting Tower'),
        ['A man with a ledger stands at a crossroads, writing down who passes.', 'Your purse feels lighter.',
         'A notice on a church door: this village is pledged.', 'Coins in the market ring false.'],
        ['The king borrowed from {short}. Now the king pays, and so do we.', 'Half the baronies are pledged to the counting house.',
         'They say he lends to both sides of every war.'],
        'a money-lender with no face who lends to kings and merchant houses. The coin loses its worth, the baronies are '
        'pledged, and the realms belong to the ledger.',
        'Another kingdom borrows. {name} grows stronger, and the pledged land spreads.',
        '{name} falls among the ledgers, and the ink runs. Somewhere a king finds his debt is gone.',
        'Bailiffs\' marks on the doors, and the fields fenced off for a debt.',
        ['The taxes doubled, to pay a loan nobody voted for.', 'A merchant house went under, owing everybody.',
         'Bailiffs in the villages, counting the cows.']),
    'giantking': _k(
        ['Ymmar the Frost Giant', 'King Hrungnir of the Rime', 'Old Winter'], 'the Giant King', 'giant_king',
        'The Rime Hall', 'cave', 'lair_giant', 5, 9, '#8aa0b4', ('cold',), 'frost', 'endless frost', (190, 220, 240), 'famine',
        ['ice_raider', 'snow_ape', 'winter_wolf'], 'J', ['The Rime-Sworn of {short}', 'The Winter Host'],
        ('The Rime-Sworn', 'Rime', ['ice_raider', 'snow_ape', 'cultist'], 'Rime Spire', 'Ice Tower'),
        ['Snow in summer, for an hour.', 'The ground shakes with steps far to the north.',
         'Your breath freezes on your beard at noon.', 'The river froze in a night, with the fish still in it.'],
        ['The winter came early and will not leave.', 'The passes are shut, and the north raiders march with {short}.',
         'They say he wants a winter that never ends.'],
        'a giant king of the frost who wants a winter that never ends. Winters grow long, the passes close, the harvests '
        'fail, and the northern raiders march with him.',
        'The frost bites deeper. {name} grows stronger, and the endless frost spreads.',
        '{name} falls like a mountain of ice, and the thaw comes after.',
        'Snow lies here out of season, and the fields are white.',
        ['The winter came a month early.', 'The passes are closed by snow, in autumn.',
         'Raiders from the north are coming earlier every year.']),
    'demon': _k(
        ['Prince Belathor', 'The Ember Prince', 'Asmodreth of the Ninth Gate'], 'the Demon Prince', 'demon_prince',
        'The Burning Gate', 'cave', 'lair_demon', 5, 9, '#8a4030', ('hills', 'grass'), 'brimstone', 'burning land',
        (230, 100, 60), 'fire',
        ['imp', 'hellhound', 'cinderling'], 'X', ['The Hounds of {short}', 'The Burning Host'],
        ('The Ninth Gate', 'Gate', ['cultist', 'imp', 'hellhound'], 'Gate Spire', 'Burning Tower'),
        ['The smell of brimstone on the wind.', 'A voice offers you anything you want. It knows what you want.',
         'Your shadow is red for a moment.', 'Fire runs along a crack in the road, and goes out.'],
        ['Cults in every city, and the Church burns heretics: some of them guilty.', 'A gate opened by the Rift.',
         'They say {short} buys souls, and pays in gold that burns.'],
        'a prince of the fire below who buys souls. Gates open, cults spread in the cities, and the Church burns heretics, '
        'some of them innocent.',
        'Brimstone on the wind. {name} grows stronger, and the burning land spreads.',
        '{name} howls and falls back through his gate, and the gate closes on him.',
        'The ground is warm here, and smells of brimstone.',
        ['Cultists caught in the city. The Church burned them.', 'The ground near the old hills smokes.',
         'People are selling things they cannot get back. Their sleep, their names.']),
}
for _k_ in KINDS:
    KINDS[_k_]['weight'] = WEIGHT[_k_]

# goal, lever, lieutenants (title, monster, place, a person), weakness (name, edge, text), relic (name, stat, v, text)
SERVANT = {
    'ifrit': dict(goal='the sand', lever='sand',
                  lts=[('the Dune Khan', 'dune_rider', 'camp', True), ('the Glass Witch', 'viper_sorcerer', 'tower', True),
                       ('the Ember Vizier', 'cultist', 'tower', True), ('the Scorpion Queen', 'giant_scorpion', 'camp', False)],
                  weak=('cold water', ('elem', 'cold'), 'It is smokeless fire. Cold puts it out: frost hurts it half again as much.'),
                  relic=('The Brass Lamp', 'res_fire', 6, 'A small brass lamp, warm, and empty now.')),
    'mare': dict(goal='the sleep', lever='sleep',
                 lts=[('the Sleepwalker', 'ghost', 'tower', True), ('the Lullaby Witch', 'weald_hag', 'tower', True),
                      ('the Black Foal', 'hellhound', 'camp', False), ('the Dream-Eater', 'staring_dark', 'camp', False)],
                 weak=('the iron under the pillow', 'blows', 'Iron drives her off: the blows of a weapon find her a quarter '
                       'harder.'),
                 relic=('The Hag-Stone', 'sight', 1, 'A grey stone with a hole through it. Look through it and you see true.')),
    'gorgon': dict(goal='the silence', lever='stone',
                   lts=[('the Sculptor', 'cultist', 'tower', True), ('the Viper Priestess', 'viper_sorcerer', 'tower', True),
                        ('the Cockatrice Keeper', 'cockatrice', 'camp', False), ('the Stone Warden', 'clay_golem', 'fort', False)],
                   weak=('her own face', 'weaker', 'Show her her own face in polished bronze: she starts the fight a quarter '
                         'weaker.'),
                   relic=('The Gorgon\'s Veil', 'res_poison', 5, 'A veil of grey silk, heavy as chain.')),
    'wildhunt': dict(goal='the roads', lever='roads',
                     lts=[('the Horn-Blower', 'wraith', 'camp', True), ('the Hound-Master', 'hellhound', 'camp', False),
                          ('the Grey Rider', 'wight', 'fort', True), ('the Lost Squire', 'draugr', 'camp', True)],
                     weak=('bread and salt', 'nocall', 'No hound of the Hunt crosses a line of salt: say the old words, and '
                           'his hounds stay back.'),
                     relic=('The Hunter\'s Horn', 'dex', 2, 'A horn of black antler. You do not blow it.')),
    'hag': dict(goal='the curse', lever='curse',
                lts=[('the Scarecrow King', 'scarecrow', 'camp', False), ('the Toad Witch', 'weald_hag', 'tower', True),
                     ('the Black Cat', 'shimmercat', 'camp', False), ('the Crow-Wife', 'weald_hag', 'tower', True)],
                weak=('her riddle answered', 'weaker', 'Answer the riddle she asks at the door: she starts the fight a quarter '
                      'weaker.'),
                relic=('The Bone Distaff', 'mana', 8, 'A distaff of yellow bone, with black thread still on it.')),
    'ratking': dict(goal='the cities', lever='plague',
                    lts=[('the Plague Doctor', 'cultist', 'tower', True), ('the Sewer Captain', 'bandit', 'fort', True),
                         ('the Flea-Queen', 'blood_tick', 'camp', False), ('the Gnawer', 'rustgnawer', 'camp', False)],
                    weak=('the piper\'s tune', 'nocall', 'The old piper\'s tune: play it, and no rat comes when he calls.'),
                    relic=('The Rat Crown', 'res_poison', 6, 'A crown of gnawed tin, too small for a man.')),
    'feyqueen': dict(goal='the wood', lever='wood',
                     lts=[('the Thorn Knight', 'knight', 'fort', True), ('the Changeling', 'shade_elf', 'tower', True),
                          ('the Bramble King', 'strangle_vine', 'camp', False), ('the Pixie Court', 'pixie', 'camp', False)],
                     weak=('cold iron', 'blows', 'The fair folk cannot abide cold iron: the blows of a weapon find her a '
                           'quarter harder.'),
                     relic=('The Hollow-Hill Ring', 'res_light', 5, 'A ring of green gold. Time feels slower near it.')),
    'vampire': dict(goal='the houses', lever='house',
                    lts=[('the Pale Bride', 'vampire_spawn', 'tower', True), ('the Steward', 'cultist', 'fort', True),
                         ('the Bat-Swarm', 'bat', 'camp', False), ('the Grave-Knight', 'wight', 'fort', True)],
                    weak=('fire', ('elem', 'fire'), 'Old dead flesh burns: fire hurts him half again as much.'),
                    relic=('The Count\'s Signet', 'res_cold', 5, 'A heavy ring with a bat on the seal, cold as a grave.')),
    'banshee': dict(goal='the courts', lever='courts',
                    lts=[('the Shroud-Sewer', 'ghost', 'tower', True), ('the Mourning Knight', 'wight', 'fort', True),
                         ('the Washer at the Ford', 'banshee', 'camp', False), ('the Coffin-Bearer', 'draugr', 'camp', True)],
                    weak=('her first grief', 'weaker', 'Name the one she first wept for: she starts the fight a quarter '
                          'weaker.'),
                    relic=('The Silver Comb', 'res_cold', 5, 'A silver comb with a grey hair still in it.')),
    'thunderbird': dict(goal='the storm', lever='storm',
                        lts=[('the Storm-Caller', 'druid', 'tower', True), ('the Thunderer', 'thunderer', 'camp', False),
                             ('the Sky-Hawk', 'giant_hawk', 'camp', False), ('the Lightning Priest', 'cultist', 'tower', True)],
                        weak=('wet feathers', ('elem', 'cold'), 'Ice in its feathers brings it down: frost hurts it half '
                              'again as much.'),
                        relic=('A Thunder Feather', 'res_light', 6, 'A feather as long as your arm that crackles when you '
                               'touch it.')),
    'lindworm': dict(goal='the deep', lever='deep',
                     lts=[('the Grey Delver', 'grey_dwarf', 'camp', True), ('the Stonemaw', 'stonemaw', 'camp', False),
                          ('the Gloomdigger', 'gloomdigger', 'camp', False), ('the Slag King', 'slag_brute', 'fort', False)],
                     weak=('the dwarves\' old song', 'nocall', 'Sing the dwarves\' old digging song, and nothing below answers '
                           'when it calls.'),
                     relic=('A Lindworm Scale', 'armor', 12, 'A scale like a grey shield, heavy and cold.')),
    'soldking': dict(goal='the emperor\'s crown', lever='crown',
                     lts=[('the Black Marshal', 'knight', 'fort', True), ('the Spymaster', 'cultist', 'tower', True),
                          ('the Turncoat Captain', 'soldier', 'fort', True), ('the Hangman', 'robber_knight', 'camp', True)],
                     weak=('his broken oath', 'weaker', 'Read him the oath he swore at his crowning: he starts the fight a '
                           'quarter weaker.'),
                     relic=('The Sold Crown', 'str', 2, 'A crown of black iron with the gold scraped off.')),
    'prophet': dict(goal='a faith', lever='faith',
                    lts=[('the First Apostle', 'cultist', 'tower', True), ('the Flagellant Captain', 'berserker', 'camp', True),
                         ('the Burning Deacon', 'cultist', 'tower', True), ('the Sworn Knight', 'holy_knight', 'fort', True)],
                    weak=('his first sermon', 'weaker', 'His first sermon, where he wrote that he knew it was a lie: read it '
                          'out, and he starts the fight a quarter weaker.'),
                    relic=('The Prophet\'s Rod', 'mana', 8, 'A rod of plain wood, worn smooth by many hands.')),
    'debtlord': dict(goal='the gold', lever='debt',
                     lts=[('the Bailiff', 'mercenary', 'fort', True), ('the Ledger-Keeper', 'cultist', 'tower', True),
                          ('the Collector', 'brigand', 'camp', True), ('the Iron Purse', 'animated_armour', 'fort', False)],
                     weak=('the forged ledger', 'weaker', 'His ledger is forged, and you can prove it: he starts the fight '
                           'a quarter weaker.'),
                     relic=('The Golden Scale', 'mf', 10, 'A little set of gold scales that never quite balance.')),
    'giantking': dict(goal='an endless winter', lever='winter',
                      lts=[('the Frost Jarl', 'ice_raider', 'camp', True), ('the Rime Witch', 'ice_witch', 'tower', True),
                           ('the Mammoth Rider', 'mammoth', 'camp', False), ('the Hill Giant', 'troll', 'fort', False)],
                      weak=('fire', ('elem', 'fire'), 'He is the winter: fire hurts him half again as much.'),
                      relic=('The Rime Crown', 'res_cold', 6, 'A crown of ice that does not melt.')),
    'demon': dict(goal='souls', lever='souls',
                  lts=[('the Pit Herald', 'cultist', 'tower', True), ('the Hound-Keeper', 'hellhound', 'camp', False),
                       ('the Brimstone Toad', 'brimstone_toad', 'camp', False), ('the Soul-Broker', 'cultist', 'fort', True)],
                  weak=('his true name', 'nocall', 'His true name, spoken in his hall: none of his host comes when he calls.'),
                  relic=('The Brass Seal', 'res_fire', 6, 'A seal of brass with a name on it you cannot read twice.')),
}

# the bosses, read into data.MONSTERS before the kinds are made whole
BOSSES = {
    'ifrit': dict(ch='I', fg='#f09040', name='The Ifrit', boss=True, lvl_fix=11, hp=4.3, dmg=1.5, df=1.3, xp=13, caster=True,
                  nova=True, summon='cinderling', tags='', bolt='bolt of smokeless fire', nova_col=(240, 150, 70),
                  summon_msg='{name} breathes on the sand, and it stands up as fire.',
                  nova_msg='{name} becomes a whirlwind of fire!', res=dict(fire=90, cold=-50, poison=50), elem='fire'),
    'nightmare': dict(ch='M', fg='#9a82c8', name='The Nightmare', boss=True, lvl_fix=10, hp=4.2, dmg=1.4, df=1.3, xp=12,
                      fast=True, caster=True, summon='shade', tags='', bolt='bolt of bad dreams',
                      summon_msg='{name} shakes her mane, and a dream steps out of it.',
                      res=dict(cold=40, poison=100), elem='cold'),
    'gorgon': dict(ch='G', fg='#b4ba9a', name='The Gorgon', boss=True, lvl_fix=11, hp=4.5, dmg=1.4, df=1.5, xp=13, caster=True,
                   poison=True, summon='viper_warrior', tags='', bolt='stony gaze',
                   summon_msg='{name} hisses, and her serpents answer from the dark.', res=dict(poison=75)),
    'huntmaster': dict(ch='H', fg='#aac896', name='The Huntmaster', boss=True, lvl_fix=11, hp=4.4, dmg=1.6, df=1.3, xp=13,
                       fast=True, leap=True, ranged=True, summon='hellhound', tags='',
                       summon_msg='{name} winds the horn, and the hounds come.', leap_msg='{name} rides you down!',
                       res=dict(cold=50, poison=100)),
    'hag': dict(ch='h', fg='#aabe78', name='The Hag', boss=True, lvl_fix=10, hp=4.2, dmg=1.3, df=1.3, xp=12, caster=True,
                summon='scarecrow', tags='', bolt='crooked curse', summon_msg='{name} cackles, and a scarecrow gets down off '
                'its pole.', res=dict(poison=60, cold=20)),
    'rat_lord': dict(ch='r', fg='#aa966e', name='The Rat King', boss=True, lvl_fix=13, hp=4.6, dmg=1.4, df=1.4, xp=14,
                     poison=True, summon='rat', tags='', summon_msg='{name} squeals, and the walls pour out rats.',
                     res=dict(poison=90)),
    'fey_queen': dict(ch='Q', fg='#96dca0', name='The Queen under the Hill', boss=True, lvl_fix=14, hp=4.6, dmg=1.4, df=1.5,
                      xp=15, caster=True, nova=True, summon='pixie', tags='', bolt='bolt of green fire',
                      nova_col=(150, 220, 160), summon_msg='{name} laughs, and the fair folk come out of the grass.',
                      nova_msg='{name} sings a note that bends the room!', res=dict(lightning=40, cold=25)),
    'vampire_count': dict(ch='V', fg='#c87890', name='The Vampire Count', boss=True, lvl_fix=14, hp=4.8, dmg=1.5, df=1.5,
                          xp=15, fast=True, leech=True, summon='vampire_spawn', tags='',
                          summon_msg='{name} spreads his cloak, and his brides step out of it.',
                          res=dict(cold=60, poison=100, fire=-40)),
    'keening_woman': dict(ch='B', fg='#bec8dc', name='The Keening Woman', boss=True, lvl_fix=14, hp=4.5, dmg=1.4, df=1.4,
                          xp=15, caster=True, nova=True, summon='ghost', tags='', bolt='wail of grief',
                          nova_col=(190, 200, 220), summon_msg='{name} keens, and the dead she mourned come to her.',
                          nova_msg='{name} screams, and the room shakes!', res=dict(cold=75, poison=100)),
    'thunderbird': dict(ch='T', fg='#bec8ff', name='The Thunderbird', boss=True, lvl_fix=15, hp=4.8, dmg=1.6, df=1.4, xp=16,
                        fast=True, caster=True, nova=True, summon='storm_spirit', tags='', bolt='bolt of lightning',
                        nova_col=(190, 200, 255), summon_msg='{name} beats its wings, and the storm comes alive.',
                        nova_msg='{name} spreads its wings, and the lightning comes down!',
                        res=dict(lightning=90, cold=-40), elem='lightning'),
    'lindworm': dict(ch='L', fg='#bea06e', name='The Lindworm', boss=True, lvl_fix=16, hp=5.4, dmg=1.6, df=1.7, xp=17,
                     poison=True, summon='tunnel_borer', tags='', summon_msg='The rock cracks, and something bores out of it.',
                     res=dict(poison=75, fire=40)),
    'sold_king': dict(ch='K', fg='#968cac', name='The Sold King', boss=True, lvl_fix=17, hp=5.2, dmg=1.6, df=1.8, xp=18,
                      summon='knight', tags='', summon_msg='{name} raises his sword, and his knights close in.',
                      res=dict(cold=20, fire=20)),
    'false_prophet': dict(ch='P', fg='#f0dc8c', name='The False Prophet', boss=True, lvl_fix=16, hp=4.8, dmg=1.4, df=1.5,
                          xp=17, caster=True, nova=True, summon='cultist', tags='', bolt='bolt of false light',
                          nova_col=(240, 220, 140), summon_msg='{name} preaches, and the faithful come running.',
                          nova_msg='{name} calls down fire on the unbeliever!', res=dict(fire=40)),
    'debt_lord': dict(ch='$', fg='#e6c85a', name='The Debt Lord', boss=True, lvl_fix=16, hp=4.8, dmg=1.3, df=1.6, xp=17,
                      caster=True, summon='mercenary', tags='', bolt='bolt of golden fire',
                      summon_msg='{name} rings a little bell, and the bailiffs come in.', res=dict(poison=50, cold=25)),
    'giant_king': dict(ch='J', fg='#bedcf0', name='The Giant King', boss=True, lvl_fix=18, hp=6, dmg=1.8, df=1.7, xp=19,
                       leap=True, nova=True, summon='snow_ape', tags='', nova_col=(190, 220, 240),
                       summon_msg='{name} roars, and the snow gets up and walks.', leap_msg='{name} brings down his fist!',
                       nova_msg='{name} stamps, and the ice breaks up round him!', res=dict(cold=90, fire=-40), elem='cold'),
    'demon_prince': dict(ch='X', fg='#e6643c', name='The Demon Prince', boss=True, lvl_fix=18, hp=5.6, dmg=1.7, df=1.7,
                         xp=19, caster=True, nova=True, summon='imp', tags='', bolt='bolt of hellfire',
                         nova_col=(230, 100, 60), summon_msg='{name} opens a hand, and imps fall out of the fire.',
                         nova_msg='{name} lets the fire below come up!', res=dict(fire=90, poison=60, cold=-20), elem='fire'),
}
BOSS_LORE = {
    'ifrit': ('A man of smokeless fire, out of a brass lamp.', 'A glass tomb under the desert.',
              'Frost hurts it badly; fire does nothing. Do not stand in the whirlwind.'),
    'nightmare': ('A black mare with a woman\'s face, and no sleep in her eyes.', 'A barrow on the moor.',
                  'She is fast and calls bad dreams. Keep your blade out.'),
    'gorgon': ('A woman with serpents for hair, whose look is stone.', 'A garden of statues in the hills.',
               'Her gaze slows you; her serpents bite. Close in quickly.'),
    'huntmaster': ('An antlered rider of the dead, with a horn and a pack.', 'A hollow oak in the deep wood.',
                   'He rides you down and calls his hounds. Keep a wall at your back.'),
    'hag': ('A hunched old woman with iron teeth.', 'A hut that walks on bird\'s legs.',
            'Her curses weaken you; kill her scarecrows first.'),
    'rat_lord': ('A hundred rats grown together, wearing a crown.', 'The undercity below a great city.',
                 'He calls rats without end and his bite poisons. Kill him fast.'),
    'fey_queen': ('A queen of the fair folk, tall and green-eyed and not quite there.', 'Under her hollow hill.',
                  'Her song bends the room. Cold iron finds her.'),
    'vampire_count': ('A pale lord in black, who drinks.', 'His castle in the hills.',
                      'He heals from every bite. Fire hurts him.'),
    'keening_woman': ('A grey woman whose wail kills.', 'A ford in the mist.',
                      'Her scream strikes the whole room. Stay close and strike.'),
    'thunderbird': ('A bird as big as a cloud, made of storm.', 'An eyrie on the high crags.',
                    'Lightning from everywhere. Frost brings it down.'),
    'lindworm': ('A wingless dragon that bores through stone.', 'Its own tunnel under the dwarf holds.',
                 'Huge and poisonous. Fight it where it cannot coil.'),
    'sold_king': ('A king in black armour who sold himself for a crown.', 'His black keep.',
                  'His knights close round him. Break the line first.'),
    'false_prophet': ('A prophet in a plain robe, with a voice like a bell.', 'His tabernacle.',
                      'He calls the faithful and calls down fire. Silence him.'),
    'debt_lord': ('A thin man with a ledger and no face.', 'His counting house.',
                  'He hires blades to stand between you. Do not let him buy time.'),
    'giant_king': ('A giant of ice and old stone, crowned with rime.', 'His hall of rime in the north.',
                   'His fist breaks the ice round him. Fire melts him.'),
    'demon_prince': ('A prince of the fire below, smiling.', 'Behind his burning gate.',
                     'His fire is everywhere and his imps without end. Do not bargain.'),
}

# the decks of the bosses (bosses.py)
KITS = {
    'ifrit': dict(weak=('cold',), phases=[
        dict(beat='kGkV', cards=dict(k=['firebolt'], G=['fireball', 'burning_lines'], V=['dread'])),
        dict(at=.66, beat='kOGkB', cards=dict(k=['firebolt'], O=['call_hounds'], G=['ring_of_fire'], B=['blink']),
             trick='burn', say='{name} spins into a whirlwind, and the sand on the floor turns to glass.'),
        dict(at=.33, beat='kGkZ', cards=dict(k=['firebolt'], G=['ring_of_fire', 'fireball'], Z=['inferno']),
             say='{name} burns white. The air is too hot to breathe.')]),
    'nightmare': dict(weak=('fire',), phases=[
        dict(beat='kVkB', cards=dict(k=['bite'], V=['dread', 'hex'], B=['shadowstep'])),
        dict(at=.66, beat='kVGkB', cards=dict(k=['bite'], V=['darkness'], G=['life_drain'], B=['pounce']), trick='dark',
             say='{name} shakes her mane, and the room goes dark as sleep.'),
        dict(at=.33, beat='kGkZ', cards=dict(k=['bite'], G=['life_drain', 'pounce'], Z=['mark_doom']), trick='fog',
             say='{name} rears, and a grey fog of bad dreams rolls out of her.')]),
    'gorgon': dict(weak=('fire',), phases=[
        dict(beat='kVkG', cards=dict(k=['venom_spit'], V=['gaze_ray'], G=['coil'])),
        dict(at=.66, beat='kVOkG', cards=dict(k=['bite'], V=['gaze_ray', 'slow_spell'], O=['call_guards'], G=['venom_spit']),
             say='{name} lifts her veil.'),
        dict(at=.33, beat='kGkZ', cards=dict(k=['bite'], G=['gaze_ray', 'tail_lash'], Z=['stop_time']), trick='enrage',
             say='{name} screams, and every serpent on her head screams with her.')]),
    'huntmaster': dict(weak=('fire',), phases=[
        dict(beat='kBkG', cards=dict(k=['strike'], B=['charge'], G=['spear_throw', 'pinning_shot'])),
        dict(at=.66, beat='kOBkG', cards=dict(k=['strike'], O=['call_hounds'], B=['charge'], G=['volley']), trick='call',
             say='{name} winds the horn. The hounds of the Hunt pour in.'),
        dict(at=.33, beat='kBGkZ', cards=dict(k=['strike'], B=['leap'], G=['cleave', 'hamstring'], Z=['rampage']),
             trick='enrage', say='{name} lowers his antlers and charges.')]),
    'hag': dict(weak=('fire',), phases=[
        dict(beat='kVkG', cards=dict(k=['touch'], V=['hex', 'curse_weak'], G=['withering'])),
        dict(at=.66, beat='kVOkG', cards=dict(k=['touch'], V=['curse_weak'], O=['call_ghouls'], G=['life_drain']),
             trick='call', say='{name} cackles, and things come up out of her garden.'),
        dict(at=.33, beat='kGkZ', cards=dict(k=['touch'], G=['withering', 'plague_cloud'], Z=['mark_doom']), trick='fog',
             say='{name} stirs her pot, and a green fog comes out of it.')]),
    'rat_lord': dict(weak=('fire',), phases=[
        dict(beat='kGkV', cards=dict(k=['bite'], G=['gnaw'], V=['stench'])),
        dict(at=.66, beat='kOGkV', cards=dict(k=['bite'], O=['rats'], G=['gnaw', 'plague_cloud'], V=['stench']),
             say='{name} squeals, and the walls pour out rats.'),
        dict(at=.33, beat='kGkZ', cards=dict(k=['bite'], G=['plague_cloud', 'gnaw'], Z=['rampage']), trick='enrage',
             say='{name} comes apart and together again, bigger.')]),
    'fey_queen': dict(weak=('fire',), phases=[
        dict(beat='kVkG', cards=dict(k=['arcane_bolt'], V=['hex', 'slow_spell'], G=['roots'])),
        dict(at=.66, beat='kVGkB', cards=dict(k=['arcane_bolt'], V=['mirror'], G=['bramble', 'roots'], B=['blink']),
             say='{name} laughs, and there are three of her.'),
        dict(at=.33, beat='kGkZ', cards=dict(k=['arcane_bolt'], G=['wrath_oak', 'bramble'], Z=['stop_time']), trick='dark',
             say='{name} sings, and the light turns green and goes out.')]),
    'vampire_count': dict(weak=('fire',), phases=[
        dict(beat='kGkB', cards=dict(k=['bite'], G=['life_drain'], B=['shadowstep'])),
        dict(at=.66, beat='kOGkB', cards=dict(k=['bite'], O=['call_ghouls'], G=['life_drain', 'garrote'], B=['blink']),
             trick='dark', say='{name} wraps himself in his cloak, and the candles die.'),
        dict(at=.33, beat='kGkZ', cards=dict(k=['bite'], G=['life_drain', 'pounce'], Z=['soul_harvest']), trick='enrage',
             say='{name} bares his teeth. There is nothing of a lord left in his face.')]),
    'keening_woman': dict(weak=('fire',), phases=[
        dict(beat='kVkG', cards=dict(k=['shadow_bolt'], V=['dread'], G=['wail'])),
        dict(at=.66, beat='kVOkG', cards=dict(k=['shadow_bolt'], V=['dread'], O=['call_bound'], G=['wail', 'life_drain']),
             trick='fog', say='{name} keens, and a grey mist comes up off the water.'),
        dict(at=.33, beat='kGkZ', cards=dict(k=['shadow_bolt'], G=['wail', 'withering'], Z=['mark_doom']), trick='dark',
             say='{name} screams your name.')]),
    'thunderbird': dict(weak=('cold',), phases=[
        dict(beat='kGkV', cards=dict(k=['spark'], G=['chain_lightning'], V=['gust'])),
        dict(at=.66, beat='kGVkB', cards=dict(k=['spark'], G=['ball_lightning', 'chain_lightning'], V=['wing_buffet'],
                                              B=['take_wing']), trick='wind', say='{name} beats its wings. The wind howls.'),
        dict(at=.33, beat='kGkZ', cards=dict(k=['spark'], G=['thunderclap', 'chain_lightning'], Z=['tempest']),
             say='{name} screams, and the storm breaks inside the eyrie.')]),
    'lindworm': dict(weak=('cold',), phases=[
        dict(beat='kGkV', cards=dict(k=['bite'], G=['coil', 'tail_lash'], V=['venom_spit'])),
        dict(at=.66, beat='kGBkO', cards=dict(k=['bite'], G=['tail_sweep', 'coil'], B=['burrow'], O=['call_ants']),
             trick='ceiling', say='{name} strikes the wall, and the roof begins to crack.'),
        dict(at=.33, beat='kGkZ', cards=dict(k=['bite'], G=['tail_sweep', 'venom_spit'], Z=['earthshaker']),
             trick='enrage', say='{name} rears up out of the ground, all of it.')]),
    'sold_king': dict(weak=('lightning',), phases=[
        dict(beat='kRGk', cards=dict(k=['strike'], R=['shield_wall'], G=['cleave'])),
        dict(at=.66, beat='kOGkR', cards=dict(k=['strike'], O=['call_guards'], G=['charge', 'cleave'], R=['riposte']),
             trick='banner', say='{name} raises the black banner. His knights close in.'),
        dict(at=.33, beat='kGkZ', cards=dict(k=['strike'], G=['cleave', 'sunder'], Z=['executioner']), trick='duel',
             say='{name} throws down his helm. "Alone, then."')]),
    'false_prophet': dict(weak=('cold',), phases=[
        dict(beat='kVkG', cards=dict(k=['smite'], V=['dread'], G=['divine_light'])),
        dict(at=.66, beat='kOVkG', cards=dict(k=['smite'], O=['call_guards'], V=['hex'], G=['pyre']), trick='call',
             say='{name} preaches, and the faithful come running.'),
        dict(at=.33, beat='kGkZ', cards=dict(k=['smite'], G=['pyre', 'divine_light'], Z=['martyr']), trick='burn',
             say='{name} calls down fire on the unbeliever.')]),
    'debt_lord': dict(weak=('fire',), phases=[
        dict(beat='kVkR', cards=dict(k=['arcane_bolt'], V=['curse_weak', 'slow_spell'], R=['spell_ward'])),
        dict(at=.66, beat='kOVkG', cards=dict(k=['coin_toss'], O=['call_guards'], V=['hex'], G=['fan_knives']),
             trick='call', say='{name} rings his little bell. The bailiffs come in.'),
        dict(at=.33, beat='kGkZ', cards=dict(k=['arcane_bolt'], G=['life_drain', 'fan_knives'], Z=['mark_doom']),
             trick='dark', say='{name} closes his ledger. The lamps go out.')]),
    'giant_king': dict(weak=('fire',), phases=[
        dict(beat='kGkV', cards=dict(k=['smash'], G=['boulder', 'cone_cold'], V=['roar'])),
        dict(at=.66, beat='kGBkO', cards=dict(k=['smash'], G=['ice_lance', 'boulder'], B=['leap'], O=['call_wolves']),
             trick='roar', say='{name} roars, and the walls of ice crack.'),
        dict(at=.33, beat='kGkZ', cards=dict(k=['smash'], G=['earthshaker', 'ice_tomb'], Z=['blizzard']), trick='enrage',
             say='{name} tears his crown off and throws it at you.')]),
    'demon_prince': dict(weak=('cold',), phases=[
        dict(beat='kGkV', cards=dict(k=['firebolt'], G=['hellfire'], V=['dread'])),
        dict(at=.66, beat='kOGkV', cards=dict(k=['firebolt'], O=['call_hounds'], G=['burning_lines', 'hellfire'],
                                              V=['hex']), trick='burn', say='{name} opens his hands, and the floor burns.'),
        dict(at=.33, beat='kGkZ', cards=dict(k=['firebolt'], G=['hellfire', 'meteor'], Z=['soul_harvest']), trick='enrage',
             say='{name} stops smiling.')]),
}

# how each mark looks on the land: (fg tint, bg tint, ground glyphs, tree glyph, tree colour), as look.TAINT
TAINT = {
    'sand': ((220, 190, 120), (34, 26, 10), [(50, '.'), (25, ','), (15, '~'), (10, '·')], '♣', (170, 150, 100)),
    'dreams': ((150, 130, 190), (18, 14, 28), [(50, '.'), (25, ','), (15, '·'), (10, "'")], '♠', (110, 96, 140)),
    'stone': ((170, 170, 160), (24, 24, 22), [(45, '.'), (25, ','), (15, '·'), (15, 'o')], '♠', (140, 140, 130)),
    'hunt': ((140, 170, 130), (14, 20, 14), [(45, '"'), (25, ','), (15, '.'), (15, "'")], '♠', (90, 120, 90)),
    'curse': ((170, 180, 110), (24, 26, 12), [(45, ','), (25, '"'), (15, '.'), (15, '%')], '♣', (130, 140, 90)),
    'plague': ((160, 140, 110), (26, 20, 14), [(45, '.'), (25, ','), (15, '%'), (15, '·')], '♠', (120, 104, 84)),
    'fey': ((140, 210, 150), (12, 30, 18), [(40, '"'), (25, ','), (20, 'o'), (15, '.')], '♣', (100, 180, 110)),
    'pale': ((200, 150, 160), (30, 14, 20), [(50, '.'), (25, ','), (15, '·'), (10, '+')], '♠', (140, 110, 120)),
    'keening': ((180, 190, 210), (20, 22, 30), [(50, '.'), (25, ','), (15, '~'), (10, "'")], '♠', (130, 140, 150)),
    'storm': ((150, 160, 210), (16, 18, 34), [(45, '.'), (25, ','), (15, '`'), (15, '·')], '♠', (90, 90, 110)),
    'deep': ((180, 150, 110), (28, 20, 12), [(45, '.'), (25, ','), (15, '/'), (15, '\\')], '♠', (130, 110, 90)),
    'banner': ((140, 130, 160), (20, 16, 26), [(50, '.'), (25, ','), (15, 'x'), (10, '·')], '♠', (110, 100, 120)),
    'faith': ((220, 200, 130), (30, 24, 10), [(45, '.'), (25, ','), (15, '+'), (15, '·')], '♣', (160, 150, 100)),
    'debt': ((210, 190, 100), (26, 22, 10), [(50, '.'), (25, ','), (15, '#'), (10, '·')], '♣', (150, 140, 90)),
    'frost': ((210, 230, 245), (24, 30, 38), [(45, '.'), (25, ','), (15, '*'), (15, '°')], '♠', (170, 190, 200)),
    'brimstone': ((210, 100, 60), (36, 12, 6), [(45, '.'), (25, ','), (15, '·'), (15, '`')], '♠', (90, 50, 40)),
}

# what the refugees tell of it (townlife.py), by lever
TALES = {
    'sand': 'The wells of {place} filled with sand in a night. We walked out with what water we had.',
    'sleep': 'Nobody in {place} had slept in a month. We left before we went mad.',
    'stone': 'Half of {place} is stone now. Good likenesses. My brother is by the well.',
    'roads': 'The Hunt rode through {place}. In the morning half the men were gone.',
    'curse': 'The cows of {place} all died in a week, and then the children took sick.',
    'plague': 'Plague in {place}. They shut the gates with us outside them.',
    'wood': 'The wood walked up to {place} and in. You cannot live in a house with a tree in it.',
    'house': 'Our lord at {place} married a lady from nowhere. The first to go missing were the maids.',
    'courts': 'The lord of {place} died, and his uncles fought over the child. Their men burned us out.',
    'storm': 'Lightning burned {place} three times in one summer. There is nothing left to burn.',
    'deep': 'The ground opened under {place}. Half the street went down into it.',
    'crown': 'The king\'s black knights came to {place} for those loyal to the old oaths. That was everyone.',
    'faith': 'The prophet\'s people came to {place} and burned the priest. Then the mill. Then us.',
    'debt': '{place} was pledged for a debt. The bailiffs took the seed corn.',
    'winter': 'Winter never left {place} this year. We ate the seed corn, then the dogs.',
    'souls': 'There is a cult in {place} now, and the Church came for them. It did not ask who was who.',
}

# the monsters of each lair (their dungeon's tag)
LAIR_FOLK = {
    'lair_ifrit': ['cinderling', 'sand_scorpion', 'dune_rider', 'salamander'],
    'lair_mare': ['shade', 'wisp', 'hungering_shade', 'ghost'],
    'lair_gorgon': ['viper_warrior', 'basilisk', 'cockatrice', 'viper_sorcerer'],
    'lair_hunt': ['hellhound', 'wraith', 'draugr', 'wolf'],
    'lair_hag': ['scarecrow', 'weald_hag', 'wisp', 'giant_frog'],
    'lair_rat': ['rat', 'rustgnawer', 'ghoul', 'blood_tick'],
    'lair_fey': ['pixie', 'dryad', 'shimmercat', 'strangle_vine'],
    'lair_vampire': ['vampire_spawn', 'bat', 'wolf', 'ghoul'],
    'lair_banshee': ['ghost', 'banshee', 'wraith', 'draugr'],
    'lair_storm': ['storm_spirit', 'giant_hawk', 'thunderer', 'wyvern'],
    'lair_worm': ['tunnel_borer', 'burrowback', 'stonemaw', 'grey_dwarf'],
    'lair_sold': ['knight', 'soldier', 'robber_knight', 'crossbow'],
    'lair_prophet': ['cultist', 'holy_knight', 'berserker', 'soldier'],
    'lair_debt': ['mercenary', 'crossbow', 'brigand', 'animated_armour'],
    'lair_giant': ['snow_ape', 'winter_wolf', 'ice_raider', 'troll'],
    'lair_demon': ['imp', 'hellhound', 'cinderling', 'brimstone_toad'],
}
FEMALE = {'nightmare', 'gorgon', 'hag', 'fey_queen', 'keening_woman'}
DESERT = {'desert', 'dune', 'bone_sand', 'salt_edge', 'badlands', 'canyon'}


# ================================================================== the levers, once a month (shadow.monthly)
def _sh():
    from . import shadow as SH
    return SH


def _villages_strike(game, e, rids, key, text, kind=None, coast=False):
    SH = _sh()
    vs = SH._villages(game, rids, coast=coast, kind=kind)
    if not vs:
        return None
    s = random.choice(vs)
    SH._strike(game, s, key, text.format(v=s.name, who=e.name if e.known else 'something'))
    return s


def lever_sand(game, idx, e, rids):
    """The Ifrit: the wells dry, the caravans vanish."""
    _villages_strike(game, e, rids, 'famine', 'The wells of {v} are sand to the brim. The village is leaving.')
    w = game.world
    cars = [x for x in w.wanderers if x.kind == 'caravan' and not getattr(x, 'rival', False) and w.taint and
            w.taint[x.y * game.maps['over'].w + x.x] == idx + 1]
    if cars:
        c = random.choice(cars)
        w.wanderers.remove(c)
        _sh()._news(game, f'{c.name} never came in out of the desert. Not even the camels.', c.x, c.y)


def lever_sleep(game, idx, e, rids):
    _villages_strike(game, e, rids, 'plague', 'Nobody in {v} has slept for a week. The inn has shut its doors.')


def lever_stone(game, idx, e, rids):
    s = _villages_strike(game, e, rids, 'plague', 'The folk of {v} were found in the morning as statues, in the middle '
                                                  'of what they were doing.')
    if s is None and e.lvl >= 4:
        _sh()._hold(game, idx, e, rids)


def lever_roads(game, idx, e, rids):
    """The Wild Hunt: travellers vanish on the night roads."""
    w = game.world
    om = game.maps['over']
    on = [x for x in w.wanderers if x.kind in ('caravan', 'traveler') and not getattr(x, 'rival', False) and w.taint and
          w.taint[x.y * om.w + x.x] == idx + 1]
    if on:
        x = random.choice(on)
        w.wanderers.remove(x)
        _sh()._news(game, f'{x.name} took the night road and was not seen again.', x.x, x.y)
    else:
        _villages_strike(game, e, rids, 'war', 'The Hunt rode over {v} in the night. In the morning, men were missing.')


def lever_curse(game, idx, e, rids):
    """The Hag: sour milk and sick cattle; and her hut walks."""
    _villages_strike(game, e, rids, 'famine', 'The milk soured in every pail of {v}, and the cattle lay down and died.')
    walk(game, e)


def walk(game, e):
    """The Hag's hut walks a little way through her land."""
    from .worldgen import cheb
    from . import data as D
    w = game.world
    om = game.maps['over']
    dg = w.dungeons.get(e.did)
    if not dg or game.cur.startswith(f'{e.did}:'):
        return False
    taken = [(s.x, s.y) for s in w.settlements] + [(s.x, s.y) for s in w.sites] + \
            [(d.x, d.y) for d in w.dungeons.values() if d is not dg] + [(q.x, q.y) for q in w.pois]
    for _ in range(80):
        x, y = e.x + random.randint(-6, 6), e.y + random.randint(-4, 4)
        if not om.inb(x, y) or (x, y) == (e.x, e.y) or om.tile(x, y) not in (D.FOREST, D.GRASS, D.SWAMP, D.HILLS):
            continue
        if any(cheb(x, y, a, b) < 3 for a, b in taken):
            continue
        e.x, e.y = dg.x, dg.y = x, y
        from . import evils as EVL
        EVL.compute_taint(game)
        return True
    return False


def lever_plague(game, idx, e, rids):
    """The Rat King: plague in a city: the market shut, prices up."""
    SH = _sh()
    w = game.world
    cs = [s for s in w.settlements if s.region in rids and s.is_city and s.event is None] or \
        [s for s in w.settlements if s.is_city and s.event is None and w.taint and
         w.taint[s.y * game.maps['over'].w + s.x] == idx + 1]
    if cs:
        s = random.choice(cs)
        SH._strike(game, s, 'plague', f'Plague in {s.name}. The market is shut and the gates are closed to strangers.')
    else:
        _villages_strike(game, e, rids, 'plague', 'Rats in the granaries of {v}, and a fever in every house.')


def lever_wood(game, idx, e, rids):
    _villages_strike(game, e, rids, 'famine', 'The wood came up to the walls of {v} overnight, and a child there is not '
                                              'the child it was.')
    if e.lvl >= 4:
        _sh()._hold(game, idx, e, rids)


def _a_lord(game, rids, pred=None):
    from . import realms as RL
    R = game.world.realm
    lords = [R.lord(R.baronies[r].lord) for r in rids if r in R.baronies and R.baronies[r].lord is not None]
    lords = [lo for lo in lords if lo and lo.alive and (pred is None or pred(lo))]
    if not lords:
        return None, None
    lo = random.choice(lords)
    rid = next(r for r in rids if r in R.baronies and R.baronies[r].lord == lo.id)
    del RL
    return lo, rid


def lever_house(game, idx, e, rids):
    """The Vampire Count marries into a house: the heir is his, and so the barony."""
    from . import realms as RL
    R = game.world.realm
    lo, rid = _a_lord(game, rids, lambda q: q.title in ('baron', 'lord') and getattr(q, 'swayed', None) is None)
    if lo is None:
        return
    lo.swayed = idx
    rg = game.world.regions[rid]
    _sh()._news(game, f'{RL.style(R, lo, False)} is married, by torchlight, at midnight. Nobody saw the bride\'s face.',
                rg.cx, rg.cy)
    _sh()._hold(game, idx, e, [rid])


def lever_courts(game, idx, e, rids):
    """The Keening Woman wails, and a lord dies: the heir follows, a child heir makes trouble (realms.die)."""
    from . import realms as RL
    lo, rid = _a_lord(game, rids, lambda q: q.title in ('baron', 'lord', 'king', 'duke', 'count'))
    if lo is None:
        return
    RL.die(game, lo, 'after a woman was heard wailing on the walls')


def lever_storm(game, idx, e, rids):
    _villages_strike(game, e, rids, 'fire', 'Lightning set the fields of {v} alight. The harvest is ash.')
    w = game.world
    om = game.maps['over']
    ships = [x for x in w.wanderers if x.kind == 'ship' and w.taint and w.taint[x.y * om.w + x.x] == idx + 1]
    if ships:
        sh_ = random.choice(ships)
        w.wanderers.remove(sh_)
        _sh()._news(game, f'{sh_.name} went down in a storm that came out of a clear sky.', sh_.x, sh_.y)


def lever_deep(game, idx, e, rids):
    """The Lindworm: a mine falls in under a dwarf hold, and the grudge-book fills."""
    SH = _sh()
    w = game.world
    holds = [s for s in w.settlements if s.kind == 'deephold' and s.event is None and w.taint and
             w.taint[s.y * game.maps['over'].w + s.x] == idx + 1] or \
        [s for s in w.settlements if s.kind == 'deephold' and s.event is None and s.region in rids]
    if holds:
        s = random.choice(holds)
        SH._strike(game, s, 'collapse', f'The deep galleries of {s.name} fell in. The dwarves are counting their dead, '
                                        'and writing in the grudge-book.')
    else:
        _villages_strike(game, e, rids, 'collapse', 'The ground opened under {v}, and half a street went into it.')


def lever_crown(game, idx, e, rids):
    """The Sold King: a king turns. He makes war and takes baronies under the black banner."""
    SH = _sh()
    from . import realms as RL
    R = game.world.realm
    kgs = sorted({R.baronies[r].kingdom for r in rids if r in R.baronies and R.baronies[r].kingdom is not None
                  and R.baronies[r].kingdom >= 0})
    if not kgs:
        return
    kid = getattr(e, 'king_of', None)
    if kid is None or kid not in [k.id for k in R.kingdoms]:
        kid = e.king_of = kgs[0]
        kg = R.kingdoms[kid]
        SH._news(game, f'The king of {kg.short} has taken the black banner. His oaths mean nothing now.', e.x, e.y)
    at_war = {k for wr in R.wars for k in (wr['a'], wr['b'])}
    if kid not in at_war:
        others = [k for k in R.kingdoms if k.id != kid and k.id not in at_war]
        if others:
            RL.start_war(game, R.kingdoms[kid], random.choice(others), 'the black banner')
            return
    SH._hold(game, idx, e, rids)


def lever_faith(game, idx, e, rids):
    """The False Prophet: the peasants rise, the Church splits, his holy army burns the tithe barns."""
    s = _villages_strike(game, e, rids, 'war', 'The folk of {v} burned their priest and walked off the fields to '
                                               'follow the Prophet.')
    if s is not None and random.random() < .5:
        _sh()._news(game, 'The Church is split: half the priests of the land preach the Prophet\'s word now.', s.x, s.y)
    if e.lvl >= 4:
        _sh()._hold(game, idx, e, rids)


def lever_debt(game, idx, e, rids):
    """The Debt Lord lends to a king: the burden grows, the barony is pledged to him."""
    SH = _sh()
    R = game.world.realm
    bs = [r for r in rids if r in R.baronies and R.baronies[r].kingdom is not None and R.baronies[r].kingdom >= 0]
    if not bs:
        return
    rid = random.choice(bs)
    kg = R.kingdoms[R.baronies[rid].kingdom]
    kg.burden += 1
    rg = game.world.regions[rid]
    SH._news(game, f'{kg.short} borrowed from the counting house again, and pledged {R.baronies[rid].name} for it. The '
                   'taxes go up.', rg.cx, rg.cy)
    if e.lvl >= 4:
        SH._hold(game, idx, e, [rid])


def lever_winter(game, idx, e, rids):
    """The Giant King: winter does not leave; the north raiders march with him."""
    _villages_strike(game, e, rids, 'famine', 'Snow still lies on the fields of {v}. They are eating the seed corn.')
    from . import powers as PW
    w = game.world
    ice = [(i, rd) for i, rd in enumerate(PW.raiders(w)) if rd['kind'] == 'ice']
    if ice and random.random() < .5:
        i, rd = random.choice(ice)
        PW.raid(game, i, rd)
    if e.lvl >= 5:
        _sh()._hold(game, idx, e, rids)


def lever_souls(game, idx, e, rids):
    """The Demon Prince: cults in the cities, and the Church burns heretics, not all of them guilty."""
    SH = _sh()
    w = game.world
    cs = [s for s in w.settlements if s.is_city and s.event is None and (s.region in rids or random.random() < .2)]
    if cs:
        s = random.choice(cs)
        SH._strike(game, s, 'war', f'A cult of the Ninth Gate was found in {s.name}. The Church burned them in the '
                                   'square, and a baker\'s boy who had only been watching.')
    if e.lvl >= 4:
        SH._hold(game, idx, e, rids)


LEVERS = {'sand': lever_sand, 'sleep': lever_sleep, 'stone': lever_stone, 'roads': lever_roads, 'curse': lever_curse,
          'plague': lever_plague, 'wood': lever_wood, 'house': lever_house, 'courts': lever_courts,
          'storm': lever_storm, 'deep': lever_deep, 'crown': lever_crown, 'faith': lever_faith, 'debt': lever_debt,
          'winter': lever_winter, 'souls': lever_souls}


def sleepless(game):
    """In the Nightmare's land no rest is rest: True where you stand."""
    from . import evils as EVL
    p = game.player
    x, y = (p.x, p.y) if game.cur == 'over' else game.over_pos
    e = EVL.taint_at(game, x, y)
    return e is not None and e.key == 'mare' and not e.defeated


# ================================================================== into the frame
def into_evils(EVL):
    for k, d in KINDS.items():
        EVL.EVILS[k] = {kk: v for kk, v in d.items() if kk not in ('weight', 'signs')}
        EVL.SIGNS[d['taint']] = d['signs']
        EVL.WEIGHT[k] = d['weight']
        if k not in EVL.EVIL_KEYS:
            EVL.EVIL_KEYS.append(k)


def into_shadow(SH):
    SH.SERVANT.update(SERVANT)
    SH.LEVERS.update(LEVERS)


def into_data(D):
    D.MONSTERS.update({k: dict(v) for k, v in BOSSES.items()})
    for k, fam in (('keening_woman', 'undead'), ('vampire_count', 'undead'), ('demon_prince', 'fiend'),
                   ('fey_queen', 'fey'), ('hag', 'hag'), ('lindworm', 'worm')):
        D.MONSTERS[k].setdefault('family', fam)


def into_world(D):
    """After the monsters are whole: the folk of each lair, the lore of the bosses."""
    for tag, ks in LAIR_FOLK.items():
        for k in ks:
            if k in D.MONSTERS and tag not in D.MONSTERS[k]['tags'].split():
                D.MONSTERS[k]['tags'] += ' ' + tag
    D.LORE.update(BOSS_LORE)
