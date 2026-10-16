"""The peoples of the vale: playable races, how they get along, and names for each of them."""
import random

RACES = {
    'human': dict(name='Human', plural='Humans', adj='human', fg=(226, 210, 180),
                  stats=dict(str=0, dex=0, vit=0, ene=0), xp=1.1,
                  learn={}, perks=['+10% experience', 'Disciplines grow 10% faster'],
                  desc='Restless, ambitious and everywhere. Nothing special, nothing lacking: humans learn quickly '
                       'and are welcome in most places.'),
    'elf': dict(name='Elf', plural='Elves', adj='elven', fg=(170, 230, 170),
                stats=dict(str=-2, dex=3, vit=-2, ene=3), xp=1.0,
                learn={'archery': 1.3, 'frost': 1.25, 'restoration': 1.25}, perks=['Sees further at night',
                                                                                  'Archery, frost and restoration grow faster'],
                desc='Long-lived folk of the old forests. Graceful archers and natural mages, but frail. '
                     'Dwarves and orcs do not trust them.'),
    'dwarf': dict(name='Dwarf', plural='Dwarves', adj='dwarven', fg=(220, 160, 110),
                  stats=dict(str=3, dex=-2, vit=3, ene=-2), xp=1.0,
                  learn={'axes': 1.3, 'warcraft': 1.2}, perks=['+20 cargo capacity', 'Poison lasts half as long',
                                                              'Axes, maces and warcraft grow faster'],
                  desc='Stout miners and smiths from the hills. Tough as stone and hard to poison, slow and '
                       'clumsy with a bow. Elves and goblinkin are old enemies.'),
    'halfling': dict(name='Halfling', plural='Halflings', adj='halfling', fg=(230, 200, 140),
                     stats=dict(str=-3, dex=4, vit=0, ene=0), xp=1.0,
                     learn={'daggers': 1.3, 'fishing': 1.3}, perks=['5% better prices', 'Fewer ambushes in the wild',
                                                                  'Daggers and fishing grow faster'],
                     desc='Small, quick and quiet, at home in the green farmlands. Weak arms, but merchants love them '
                          'and monsters overlook them.'),
    'orc': dict(name='Half-orc', plural='Half-orcs', adj='orcish', fg=(150, 200, 100),
                stats=dict(str=4, dex=0, vit=2, ene=-4), xp=1.0,
                learn={'axes': 1.25, 'warcraft': 1.3}, perks=['+10% melee damage', 'Orcish tribes may tolerate you',
                                                             'Many towns charge you more'],
                desc='Born between two peoples and trusted by neither. Brutally strong, but most townsfolk '
                     'eye you warily, and elves despise you.'),
    'gnome': dict(name='Gnome', plural='Gnomes', adj='gnomish', fg=(200, 170, 230),
                  stats=dict(str=-3, dex=1, vit=-1, ene=4), xp=1.0,
                  learn={'nature': 1.3, 'restoration': 1.25, 'shadow': 1.2}, perks=['Spells cost 15% less mana',
                                                                                  'Can enter the little gnome homes',
                                                                                  'Nature, restoration and shadow magic grow faster'],
                  desc='Little folk of the old woods, who dig their homes under the roots of great trees, far from the '
                       'big folk. They know every herb and beast; feeble in a brawl. Most folk find them odd but harmless.'),
    'goblin': dict(name='Goblin', plural='Goblins', adj='goblin', fg=(140, 200, 90),
                   stats=dict(str=-1, dex=4, vit=-1, ene=-1), xp=1.05,
                   learn={'daggers': 1.3, 'archery': 1.2}, perks=['Sees further in the dark', 'Fewer ambushes in the wild',
                                                                   'Daggers and archery grow faster', 'Many towns charge you more'],
                   desc='Wiry, sharp-eyed and quick, with sharper teeth. Goblins live at the edges of every land; '
                        'nobody quite trusts them, and dwarves hate them outright.'),
}
RACE_ORDER = ['human', 'elf', 'dwarf', 'halfling', 'gnome', 'orc', 'goblin']

# how the people of one race regard a player of another (added to starting reputation)
RELATIONS = {
    'human': {'human': 5, 'elf': 0, 'dwarf': 0, 'halfling': 5, 'gnome': 0, 'orc': -15, 'goblin': -15},
    'elf': {'human': 0, 'elf': 15, 'dwarf': -10, 'halfling': 5, 'gnome': 5, 'orc': -25, 'goblin': -20},
    'dwarf': {'human': 0, 'elf': -10, 'dwarf': 15, 'halfling': 5, 'gnome': 10, 'orc': -20, 'goblin': -25},
    'halfling': {'human': 5, 'elf': 5, 'dwarf': 5, 'halfling': 15, 'gnome': 5, 'orc': -15, 'goblin': -15},
    'gnome': {'human': 0, 'elf': 5, 'dwarf': 10, 'halfling': 5, 'gnome': 15, 'orc': -10, 'goblin': -15},
    'orc': {'human': -10, 'elf': -20, 'dwarf': -15, 'halfling': -10, 'gnome': -5, 'orc': 20, 'goblin': 10},
    'goblin': {'human': -10, 'elf': -15, 'dwarf': -20, 'halfling': -5, 'gnome': -10, 'orc': 10, 'goblin': 20},
}
GENDERS = ['male', 'female', 'other']
GENDER_NAME = {'male': 'Man', 'female': 'Woman', 'other': 'Undefined'}


def relation(townsfolk, player):
    """Starting attitude of townsfolk of race a towards the player's race."""
    return RELATIONS.get(townsfolk, {}).get(player, 0)


def price_factor(game, town_race):
    """Price multiplier for buying in a town of this race."""
    p = game.player
    k = 1.0
    if getattr(p, 'race', 'human') == 'halfling':
        k *= .95
    rel = relation(town_race, getattr(p, 'race', 'human'))
    if rel < 0:
        k *= 1 - rel / 200          # -20 -> 10% dearer
    return k


# ------------------------------------------------------------------ names
_SYL = {
    'human': dict(
        male=(['Al', 'Bran', 'Cor', 'Ed', 'Gar', 'Hal', 'Os', 'Ro', 'Wil', 'Ber', 'Dun', 'Ger', 'Leo', 'Tob', 'Ald'],
              ['ric', 'win', 'mund', 'wald', 'bert', 'ard', 'ric', 'stan', 'old', 'fric', 'an', 'ias']),
        female=(['Ed', 'Mau', 'Ag', 'Ros', 'El', 'Wen', 'Hil', 'Is', 'Mar', 'Bea', 'Gwen', 'Tam', 'Lyn', 'Ced'],
                ['da', 'na', 'ris', 'wyn', 'eth', 'beth', 'ilde', 'sin', 'ora', 'elle', 'ith', 'a']),
        family=['Ashford', 'Brook', 'Carver', 'Dunmore', 'Fletcher', 'Hale', 'Marsh', 'Thatcher', 'Underhill', 'Wright',
                'Cooper', 'Blackwood', 'Greaves', 'Holt', 'Redmane']),
    'elf': dict(
        male=(['Ae', 'Cael', 'Ela', 'Fae', 'Ith', 'Lae', 'Mir', 'Sil', 'Thal', 'Va', 'Ere', 'Gal'],
              ['rion', 'dor', 'lith', 'thas', 'ndil', 'mir', 'rel', 'vain', 'ion', 'las']),
        female=(['Ae', 'Ela', 'Ili', 'Lia', 'Mae', 'Nim', 'Sae', 'Thia', 'Yll', 'Ari', 'Cele', 'Fen'],
                ['wen', 'riel', 'lith', 'nara', 'thiel', 'ssa', 'via', 'lyn', 'diel', 'aris']),
        family=['Silverleaf', 'Moonwhisper', 'Starbough', 'Dawnmere', 'Nightbloom', 'Windsong', 'Ashgrove', 'Brightwater']),
    'dwarf': dict(
        male=(['Bal', 'Dur', 'Gim', 'Thor', 'Bof', 'Grun', 'Kil', 'Mor', 'Nor', 'Dain', 'Brok', 'Tor'],
              ['in', 'ur', 'grim', 'dak', 'rik', 'gar', 'nar', 'li', 'bur', 'drum']),
        female=(['Dis', 'Hel', 'Bry', 'Thor', 'Gun', 'Ing', 'Kat', 'Mag', 'Ris', 'Sig'],
                ['a', 'ga', 'hild', 'dis', 'ra', 'unn', 'vor', 'rid', 'na']),
        family=['Ironfist', 'Stonebeard', 'Deepdelver', 'Hammerhand', 'Copperkettle', 'Anvilborn', 'Coalbrow', 'Granitehelm']),
    'halfling': dict(
        male=(['Bil', 'Fro', 'Mer', 'Pip', 'Sam', 'Tod', 'Wil', 'Bun', 'Hal', 'Os', 'Per', 'Mil'],
              ['bo', 'do', 'ry', 'pin', 'wise', 'kin', 'ford', 'bur', 'o', 'ny']),
        female=(['Ro', 'Dai', 'Lil', 'Pri', 'Mar', 'Bel', 'Cam', 'Ely', 'Pop', 'Tan'],
                ['sie', 'sy', 'ly', 'mrose', 'igold', 'la', 'ellia', 'py', 'na', 'ie']),
        family=['Goodbarrel', 'Underbough', 'Tealeaf', 'Brandyfoot', 'Hilltopple', 'Greenhand', 'Puddifoot', 'Honeypot']),
    'orc': dict(
        male=(['Gro', 'Ugg', 'Kar', 'Mog', 'Thra', 'Zug', 'Dur', 'Grim', 'Ruk', 'Nag', 'Bol', 'Skar'],
              ['nak', 'ruk', 'gash', 'thak', 'mok', 'bag', 'grat', 'dush', 'zog', 'kul']),
        female=(['Sha', 'Ur', 'Gra', 'Mog', 'Zul', 'Ag', 'Bash', 'Kra', 'Yaz', 'Ogh'],
                ['ra', 'za', 'gha', 'nash', 'bra', 'eth', 'ka', 'ura', 'ma']),
        family=['Skullsplitter', 'Bonegnawer', 'Ironjaw', 'Bloodtusk', 'Ashborn', 'Halfblood', 'Stonefist', 'Grimscar']),
    'gnome': dict(
        male=(['Fenn', 'Bim', 'Nim', 'Wren', 'Orryn', 'Tobb', 'Moss', 'Gim', 'Bod', 'Fen', 'Pell', 'Quill'],
              ['wick', 'ble', 'bo', 'nock', 'dle', 'kin', 'pip', 'zel', 'stan', 'ger']),
        female=(['Bree', 'Lini', 'Nissa', 'Tana', 'Ella', 'Zan', 'Roy', 'Mina', 'Orla', 'Pip'],
                ['wyn', 'bell', 'ra', 'tink', 'ella', 'zie', 'pa', 'na', 'li', 'ette']),
        family=['Mosswhistle', 'Rootfoot', 'Acornbottom', 'Fernhollow', 'Toadstool', 'Barkbuckle', 'Hazelpot', 'Burrowby']),
    'goblin': dict(
        male=(['Snik', 'Grib', 'Nog', 'Skab', 'Rikk', 'Zit', 'Gob', 'Krag', 'Wort', 'Mug', 'Skrit', 'Nub'],
              ['nik', 'bit', 'gle', 'snot', 'tooth', 'rat', 'gak', 'iz', 'ub', 'ik']),
        female=(['Ziz', 'Grit', 'Neek', 'Skag', 'Wiz', 'Rat', 'Mog', 'Snee', 'Tik', 'Yag'],
                ['zy', 'ka', 'ra', 'git', 'na', 'ix', 'sha', 'ib', 'la']),
        family=['Rustknife', 'Ratbiter', 'Muckfoot', 'Snaggletooth', 'Mudlark', 'Grubfinder', 'Knucklebones', 'Sootear']),
}


NAME_INFO = {}       # generated first name -> (gender, race), so people know who they are
NAME_FULL = {}       # generated full name -> (gender, race)
TITLE_GENDER = {'Sister': 'female', 'Brother': 'male', 'Abbot': 'male', 'Abbess': 'female', 'Mother': 'female',
                'Father': 'male', 'Lady': 'female', 'Lord': 'male', 'Berend': 'male', 'Ilse': 'female', 'Dorien': 'male'}


def who(name):
    """(gender, race) guessed from a person's name; either may be None."""
    g = r = None
    words = name.replace(',', ' ').split()
    for i in range(len(words) - 1):
        hit = NAME_FULL.get(f'{words[i]} {words[i + 1]}')
        if hit:
            g, r = hit
            break
    for wd in words:
        if wd in TITLE_GENDER and not g:
            g = TITLE_GENDER[wd]
        if wd in NAME_INFO:
            g2, r2 = NAME_INFO[wd]
            g, r = g or g2, r or r2
    return g, r


def random_name(race='human', gender='other', family=True):
    t = _SYL.get(race, _SYL['human'])
    g = gender if gender in ('male', 'female') else random.choice(['male', 'female'])
    a, b = t[g]
    first = random.choice(a) + random.choice(b)
    first = first[0].upper() + first[1:].lower()
    NAME_INFO.setdefault(first, (g, race))
    if family:
        full = f'{first} {random.choice(t["family"])}'
        NAME_FULL[full] = (g, race)
        return full
    return first


def names_for(race, n):
    """n distinct full names for townsfolk of a race (mixed genders)."""
    out = set()
    for _ in range(n * 6):
        if len(out) >= n:
            break
        out.add(random_name(race, random.choice(['male', 'female'])))
    return list(out)


def address(game):
    """How strangers address the player."""
    g = getattr(game.player, 'gender', 'other')
    return {'male': 'lad', 'female': 'lass'}.get(g, 'friend')
