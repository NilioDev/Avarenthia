"""Named enemies: an orc chief who burned a mill, an old she-wolf who takes the sheep every winter, a spider that
webbed a whole wood. Each has a name and an epithet, a rank, a few traits, a following, a habit, looks, a past, a
weakness you can hear about, and a trophy to bring back.

notable    one trait, a small following
notorious  two or three traits and a band
legendary  rare: its own lair (a dungeon level), its own loot

Left alone they grow: a trait, more followers, a higher bounty. Beaten badly they flee to lick their wounds, and come
back scarred, knowing your name. Kill you, and they take a piece of your gear and a new epithet.

Hunting them: no marker. A job gives a search area that grows as the report ages; in it you find signs (tracks, a
torn deer, a burnt cart, webs) that tell direction and age, and shrink the area. Close enough, you meet."""
import random

from . import data as D
from .worldgen import cheb

RANKS = ('notable', 'notorious', 'legendary')
RANK_WORD = {'notable': 'notable', 'notorious': 'notorious', 'legendary': 'legendary'}
TRAITS = ['Venomous', 'Frost-touched', 'Fire-blooded', 'Stone Skin', 'Thorny', 'Vampiric', 'Regenerating', 'Swift', 'Blink',
          'Summoner', 'Splitting', 'Multishot', 'Berserk', 'Shielded', 'Cursing', 'Warcry']
TRAIT_TEXT = {'Venomous': 'its blows poison', 'Frost-touched': 'its touch is cold and slows you', 'Fire-blooded': 'it burns',
              'Stone Skin': 'its hide turns blades', 'Thorny': 'it cuts whoever strikes it', 'Vampiric': 'it heals as it wounds',
              'Regenerating': 'its wounds close by themselves', 'Swift': 'it is quick', 'Blink': 'it steps through the air',
              'Summoner': 'it calls its kin', 'Splitting': 'cut it and it splits', 'Multishot': 'it looses two shots at once',
              'Berserk': 'it rages when hurt', 'Shielded': 'it turns the first blows aside', 'Cursing': 'it curses',
              'Warcry': 'its war cry drives its band on'}

# what can be named, by prey (who pays for it): beasts for the Wardens, the dead for the Dawn, warlords for the Iron Company,
# sorcerers for the Magi, gang bosses for the Thieves, the knights who hunt the Coven
PREY = {
    'beast': ['wolf', 'wolf_spider', 'troll', 'ogre', 'crocodile', 'giant_scorpion', 'mantis', 'hyena', 'web_weaver',
              'brood_spider', 'horn_beetle', 'drake', 'frost_spider', 'brown_bear', 'cave_bear', 'worg', 'winter_wolf',
              'sabretooth', 'panther', 'manticore', 'wyvern', 'clawbeak', 'boar', 'mammoth', 'basilisk'],
    'warlord': ['orc_chief', 'gob_boss', 'hob_captain', 'gnoll_packlord', 'orc_berserker', 'kob_chief', 'lizard_warrior'],
    'sorcerer': ['orc_warlock', 'orc_shaman', 'gob_shaman', 'kob_sorcerer', 'lizard_shaman', 'gnoll_caller', 'ice_witch',
                 'cultist'],
    'undead': ['wraith', 'skeleton', 'zombie', 'ghost', 'ghast', 'wight', 'draugr', 'vampire_spawn', 'banshee', 'mummy'],
    'gang': ['bandit'],
    'paladin': ['knight'],
}
PREY_OF = {k: p for p, ks in PREY.items() for k in ks}
GUILD_PREY = {'wardens': 'beast', 'dawn': 'undead', 'iron': 'warlord', 'magi': 'sorcerer', 'thieves': 'gang', 'coven': 'paladin',
              'moot': 'beast', 'chapter': 'undead', 'ossuary': 'paladin', 'stillhand': 'warlord', 'hound': 'beast'}
# who follows whom (those with a band in creatures.BANDS bring their band)
FOLLOW = {'wolf': ['wolf'], 'hyena': ['hyena'], 'wolf_spider': ['wolf_spider', 'jumping_spider'],
          'web_weaver': ['spider_swarm', 'wolf_spider'], 'brood_spider': ['spiderling'], 'frost_spider': ['frost_spider'],
          'wraith': ['skeleton', 'zombie'], 'skeleton': ['skeleton', 'skarcher'], 'zombie': ['zombie'], 'ghost': [],
          'cultist': ['zombie', 'skeleton'], 'ice_witch': ['wolf'], 'bandit': ['bandit', 'brigand'],
          'knight': ['soldier', 'crossbow'], 'drake': [],
          'troll': [], 'ogre': [], 'crocodile': [], 'giant_scorpion': [], 'mantis': [], 'horn_beetle': [],
          'banshee': [], 'mummy': ['skeleton'], 'vampire_spawn': ['ghoul'], 'brown_bear': [], 'cave_bear': [],
          'sabretooth': [], 'panther': [], 'manticore': [], 'wyvern': [], 'clawbeak': [], 'boar': ['boar'],
          'mammoth': ['mammoth'], 'basilisk': []}
RACE = {'orc_chief': 'orc', 'orc_berserker': 'orc', 'orc_warlock': 'orc', 'orc_shaman': 'orc', 'gob_boss': 'goblin',
        'gob_shaman': 'goblin', 'kob_chief': 'kobold', 'kob_sorcerer': 'kobold', 'hob_captain': 'hobgoblin',
        'gnoll_packlord': 'gnoll', 'gnoll_caller': 'gnoll', 'lizard_warrior': 'lizard', 'lizard_shaman': 'lizard',
        'bandit': 'human', 'knight': 'human', 'cultist': 'human', 'ice_witch': 'human'}
NAMES = {
    'orc': (['Grukka', 'Ushna', 'Morga', 'Shagra', 'Vrasha', 'Kurza', 'Bolga', 'Rugash'],
            ['Drogmar', 'Urzag', 'Krull', 'Brokkar', 'Gazmuk', 'Hrothak', 'Thrak', 'Vorz']),
    'goblin': (['Snikka', 'Grizzle', 'Mopsy', 'Nettle', 'Skeeva', 'Wort'], ['Snagjaw', 'Grisk', 'Nob', 'Ratchet', 'Skulk', 'Fizzik']),
    'kobold': (['Yip', 'Skreeka', 'Tiksa', 'Mirri'], ['Kreel', 'Snik', 'Torvik', 'Zagg', 'Pip']),
    'hobgoblin': (['Varra', 'Kesh', 'Durana', 'Ilsk'], ['Marhok', 'Tavik', 'Garran', 'Voss']),
    'gnoll': (['Haaka', 'Rheeza', 'Kakka', 'Yeena'], ['Grukk', 'Hrakka', 'Kekkar', 'Yarl']),
    'lizard': (['Ssera', 'Thissa', 'Kessa'], ['Hsark', 'Rasskal', 'Tsuk', 'Vesh']),
    'human': (['Maeve', 'Agnes', 'Ysolde', 'Brenna', 'Corra', 'Hild', 'Sabine'], ['Corbin', 'Hal', 'Ulric', 'Joss', 'Osric', 'Garth']),
}
EPITHET = ['the Butcher', 'Ironjaw', 'the Red', 'Bonebreaker', 'the Burner', 'One-Ear', 'the Grinning', 'Skullsplitter',
           'Blacktooth', 'the Hungry']
BEAST_NAME = ['Greymuzzle', 'Blackback', 'Snagjaw', 'Ironhide', 'Bloodclaw', 'Longtooth', 'Scarneck', 'Ripfang', 'Mosshide',
              'Ashpelt', 'Splitlip', 'Nightmaw']
BEAST_TITLE = {'f': ['Widow', 'Mother', 'Grey Mare'], 'm': ['Old Lord', 'Terror', 'King'], None: ['Terror', 'Horror', 'Shadow']}
DEAD = {'f': (['Abbess', 'Lady', 'Dame'], ['Morwen', 'Ysolt', 'Edda', 'Hesper']),
        'm': (['Sir', 'Brother', 'Reeve', 'Lord'], ['Edric', 'Aldous', 'Wystan', 'Godric'])}
DEAD_EPITHET = ['the Hollow', 'the Restless', 'the Unburied', 'the Grey']
LOOKS = {
    'people': ['a brand scar across one cheek', 'armour of lashed bones', 'one milky eye', 'a necklace of ears',
               'a scalp-lock dyed red', 'a hook where one hand was', 'tattoos of every kill down both arms',
               'teeth filed to points', 'a cloak made of a bear'],
    'orc': ['a broken tusk', 'tusks capped with iron'],
    'human': ['a brand on the forehead', 'a scarred lip', 'fine stolen clothes', 'a red cloak'],
    'beast': ['a grey muzzle', 'a torn ear', 'a scorched hide', 'an old spear-head still in one shoulder', 'one eye gone white',
              'a pelt black as soot', 'a limp it does not seem to mind'],
    'crawler': ['a leg missing on one side', 'a shell scored by old blades', 'markings like a skull on its back',
                'eyes that shine red'],
    'dead': ['a rusted crown', 'a burial shroud still wound about it', 'a sword through its ribs it never pulled out',
             'eyes like two cold candles'],
}
PAST = {
    'people': ['burned the mill at {town}', 'raided the farms around {town} all autumn', 'killed the reeve of {town}',
               'ambushed a caravan on the road to {town}', 'drove the charcoal burners out of {region}',
               'carried off the sheep of {town}', 'broke the bridge near {town}'],
    'beast': ['took the sheep of {town} all last winter', 'killed two hunters from {town}',
              "savaged a caravan's horses near {town}", 'has been seen near {town} at dusk, watching'],
    'crawler': ['webbed the woods of {region} so thick that no one goes there', 'took a shepherd from {town}',
                'stripped the orchards of {town}'],
    'dead': ['has walked the barrows of {region} for a hundred years', 'rose from the graveyard of {town}',
             'was a knight of {town}, long ago'],
}
WEAK_TEXT = {'fire': '{he} hates fire', 'cold': 'the cold makes {him} slow and stupid', 'lightning': 'lightning is {his} bane'}
TROPHY = {'orc': 'tusk', 'goblin': 'ear', 'kobold': 'ear', 'hobgoblin': 'head', 'gnoll': 'mane', 'lizard': 'crest', 'human': 'head',
          'beast': 'fang', 'crawler': 'fangs', 'dead': 'skull'}
SIGNS = {
    'people': ['the ashes of a cookfire, still warm', 'boot prints of a dozen, heading', 'a broken arrow and a torn banner',
               'a burnt cart by the track', 'a farm dog, dead, with a spear wound'],
    'beast': ['tracks in the mud, big as dinner plates', 'a torn deer, half eaten', 'tufts of hair on a thorn bush',
              'claw marks on a tree, higher than your head'],
    'crawler': ['webs strung between the trees', 'a shed husk as big as a cloak', 'a trail of slime and broken stems',
                'a sheep wrapped in silk, drained dry'],
    'dead': ['a barrow broken open from inside', 'frost on the grass where nothing should be cold', 'grave dirt on the road',
             'crows that will not settle'],
}
HABITS = {'territorial': 'keeps to one place', 'roaming': 'roams far', 'raider': 'raids caravans and villages',
          'ambusher': 'lies in wait on one road', 'nocturnal': 'only comes out at night'}
GROW = {'territorial': .4, 'roaming': 1.5, 'raider': 1.0, 'ambusher': .4, 'nocturnal': .8}


class Named:
    def __init__(self, nid, k):
        self.id, self.k = nid, k
        self.name = ''
        self.epithet = ''
        self.gender = None
        self.rank = 'notable'
        self.traits = []
        self.following = []
        self.habit = 'territorial'
        self.looks = []
        self.past = ''
        self.weak = None
        self.trophy = 'head'
        self.fame = 0
        self.lvl = 1
        self.bounty = 0
        self.x = self.y = 0
        self.home = (0, 0)
        self.area = None           # [x, y, radius, day of the report]
        self.seen = False
        self.seen_traits = []
        self.alive = True
        self.back = None           # day it comes back from licking its wounds
        self.scarred = False
        self.knows_you = False
        self.slayer = None         # your name, if it killed you
        self.kept = None           # the piece of your gear it took
        self.did = self.depth = None
        self.boss = None           # the boss this one serves (a lieutenant)
        self.born = 0
        self.last_grow = 0
        self.fled_from = None      # the battle map it fled

    @property
    def full(self):
        t = f'{self.name} {self.epithet}'.strip()
        if self.scarred:
            t += ' the Scarred' if not self.epithet.startswith('the Scarred') else ''
        if self.slayer:
            t = f'{self.name}, Slayer of {self.slayer}'
        return t

    @property
    def Full(self):
        return self.full[0].upper() + self.full[1:]

    @property
    def kind(self):
        return kind_of(self.k)

    def what(self):
        """'an orc chief', 'a dire wolf'"""
        d = D.MONSTERS[self.k]
        word = d['name'].lower()
        return f"{'an' if word[0] in 'aeiou' else 'a'} {word}"

    def he(self):
        return {'f': 'she', 'm': 'he'}.get(self.gender, 'it')

    def his(self):
        return {'f': 'her', 'm': 'his'}.get(self.gender, 'its')

    def him(self):
        return {'f': 'her', 'm': 'him'}.get(self.gender, 'it')

    def weak_text(self):
        return WEAK_TEXT[self.weak].format(he=self.he(), his=self.his(), him=self.him()) if self.weak else ''


def place(reg):
    """A region's name to use in a sentence: 'the Greywood', 'the Vale of Thorns'."""
    name = reg.name
    if name.startswith('The '):
        return 'the ' + name[4:]
    if any(name in ns for ns in D.BIOME_NAMES.values()):
        return 'the ' + name
    return name


def poss(name):
    return name + ("'" if name.endswith('s') else "'s")


def kind_of(k):
    if k in RACE:
        return 'people'
    if k in D.UNDEAD or k in ('ghost',):
        return 'dead'
    fam = D.MONSTERS[k].get('family')
    if fam in ('spider', 'insect', 'crawler', 'ant', 'worm') or k in ('spider',):
        return 'crawler'
    return 'beast'


def store(game):
    return game.world.__dict__.setdefault('named', {})


def alive(game):
    return [n for n in store(game).values() if n.alive]


def get(game, nid):
    return store(game).get(nid)


def _near_town(game, x, y):
    ss = [s for s in game.world.settlements if s.kind != 'deephold']
    return min(ss, key=lambda s: cheb(s.x, s.y, x, y)) if ss else None


def _spot(game, cx, cy, lo, hi):
    """A walkable cell off the road, between lo and hi cells from (cx, cy)."""
    over = game.maps['over']
    w = game.world
    for _ in range(400):
        x, y = cx + random.randint(-hi, hi), cy + random.randint(-hi * 2 // 3, hi * 2 // 3)
        if not over.inb(x, y) or cheb(x, y, cx, cy) < lo:
            continue
        t = over.tile(x, y)
        if not D.TILES[t].walk or t in (D.ROAD, D.TOWN, D.CITY, D.ENTR, D.CASTLE, D.FORT):
            continue
        if any(cheb(x, y, s.x, s.y) < 5 for s in w.settlements):
            continue
        return x, y
    return None


def _pick_key(game, x, y, prey):
    reg = game.world.region_at(x, y)
    biome = set(D.BIOME_MONSTERS[reg.biome]) | set(D.CLIMATE_MONSTERS.get(getattr(reg, 'climate', None), []))
    danger = game.world.danger_at(x, y)
    pool = PREY[prey] if prey else [k for ks in (PREY['beast'], PREY['warlord'], PREY['sorcerer'], PREY['gang']) for k in ks]
    fit = [k for k in pool if D.MONSTERS[k]['min_l'] <= danger + 4]
    local = [k for k in fit if k in biome]
    return random.choice(local if local and random.random() < .6 else fit or pool)


def make(game, x=None, y=None, prey=None, rank=None, boss=None, k=None):
    """A new named enemy somewhere near (x, y)."""
    from .creatures import BANDS, NEW
    w = game.world
    if x is None:
        s = random.choice([s for s in w.settlements if s.kind != 'deephold'])
        x, y = s.x, s.y
    spot = _spot(game, x, y, 8, 34)
    if not spot:
        return None
    k = k or _pick_key(game, spot[0], spot[1], prey)
    danger = w.danger_at(*spot)
    if rank is None:
        r = random.random()
        rank = 'legendary' if r < .07 and danger >= 3 else 'notorious' if r < .38 else 'notable'
    n = Named(game.new_id(), k)
    n.born = n.last_grow = game.day
    n.rank = rank
    d = D.MONSTERS[k]
    g = NEW[k].get('gender') if k in NEW else 'mf' if k in RACE or kind_of(k) in ('beast', 'dead') else None
    n.gender = random.choice('fm') if g == 'mf' else g if g in ('f', 'm') else None
    _name(game, n, spot)
    n.lvl = danger + {'notable': 2, 'notorious': 3, 'legendary': 5}[rank]
    nt = {'notable': 1, 'notorious': random.randint(2, 3), 'legendary': random.randint(3, 4)}[rank]
    pool = [t for t in TRAITS if (t != 'Multishot' or d['ranged']) and (t != 'Splitting' or k not in RACE)]
    n.traits = random.sample(pool, nt)
    size = {'notable': random.randint(0, 2), 'notorious': random.randint(3, 5), 'legendary': random.randint(4, 6)}[rank]
    if k in BANDS:
        n.following = [random.choice(BANDS[k]) for _ in range(size)]
    else:
        f = FOLLOW.get(k, [k])
        n.following = [random.choice(f) for _ in range(size)] if f else []
    n.following = [f for f in n.following if not D.MONSTERS[f].get('chief')]
    beast = kind_of(k) in ('beast', 'crawler')
    habits = ['territorial', 'roaming', 'nocturnal'] if beast else ['territorial', 'roaming', 'raider', 'ambusher']
    if kind_of(k) == 'dead':
        habits = ['territorial', 'nocturnal']
    n.habit = random.choice(habits)
    kk = kind_of(k)
    looks = LOOKS['beast'] if kk == 'beast' else LOOKS['crawler'] if kk == 'crawler' else LOOKS['dead'] if kk == 'dead' else \
        LOOKS['people'] + LOOKS.get(RACE.get(k), [])
    n.looks = random.sample(looks, 2 if rank != 'notable' else 1)
    town = _near_town(game, *spot)
    n.past = random.choice(PAST[kk]).format(town=town.name if town else 'the vale', region=place(w.region_at(*spot)))
    res = d['res']
    n.weak = random.choice([e for e in ('fire', 'cold', 'lightning') if res.get(e, 0) <= 25] or ['fire'])
    n.trophy = TROPHY.get(RACE.get(k), TROPHY.get(kk, 'head'))
    n.x, n.y = spot
    n.home = spot
    n.bounty = bounty(n)
    n.boss = boss
    if rank == 'legendary':
        lair(game, n)
    store(game)[n.id] = n
    # the big ones have lieutenants: hunt them first, then where the boss hides
    if rank in ('notorious', 'legendary') and k in RACE and boss is None and random.random() < .6:
        for _ in range(random.randint(1, 2)):
            lt = make(game, n.x, n.y, None, 'notable', n.id, k=random.choice([q for q in BANDS.get(k, [k]) if q in RACE] or [k]))
            if lt:
                lt.habit = 'raider' if lt.habit == 'ambusher' else lt.habit
    return n


def _name(game, n, spot):
    k, g = n.k, n.gender
    race = RACE.get(k)
    kk = kind_of(k)
    w = game.world
    where = place(w.region_at(*spot))
    town = _near_town(game, *spot)
    if race in NAMES:
        n.name = random.choice(NAMES[race][0 if g == 'f' else 1])
        ep = random.choice(EPITHET + [f'the Butcher of {town.name}' if town else 'the Butcher', f'Scourge of {where}'])
        if g == 'f' and ep == 'the Hungry':
            ep = 'the Widow'
        n.epithet = ep
    elif kk == 'dead':
        titles, names = DEAD[g or 'm']
        n.name = f'{random.choice(titles)} {random.choice(names)}'
        n.epithet = random.choice(DEAD_EPITHET)
    elif kk == 'crawler' and random.random() < .6:
        t = random.choice(BEAST_TITLE['f' if g == 'f' else None])
        n.name, n.epithet = f'the {t}', f'of {where}'
    else:
        n.name = ('Old ' if random.random() < .4 else '') + random.choice(BEAST_NAME)
        n.epithet = ''
        if random.random() < .3:
            n.name, n.epithet = f"the {random.choice(BEAST_TITLE.get(g, BEAST_TITLE[None]))}", f'of {where}'


def bounty(n):
    """Modest: a named beast is worth a good week's work, a legend a little more."""
    base = {'notable': 25, 'notorious': 45, 'legendary': 80}[n.rank]
    return round((base + n.lvl * 6) * (1 + .25 * n.fame)) * 100


def lair(game, n):
    """A legend keeps its own lair: the deepest level of a dungeon nobody owns."""
    w = game.world
    ds = [d for d in w.dungeons.values() if not d.main and getattr(d, 'town', None) is None
          and not any(o.alive and o.did == d.id for o in store(game).values())]
    if not ds:
        return
    d = min(ds, key=lambda d: cheb(d.x, d.y, n.x, n.y))
    n.did, n.depth = d.id, d.depth
    n.x, n.y = d.x, d.y
    n.home = (d.x, d.y)
    n.habit = 'territorial'


# ------------------------------------------------------------------ the search area
def area(game, n):
    """(x, y, radius) of where it is thought to be. It grows as the report ages."""
    if n.area is None:
        report(game, n, age=random.randint(1, 4))
    x, y, r, day = n.area
    return x, y, int(min(24, r + max(0, game.day - day) * GROW.get(n.habit, 1)))


def report(game, n, age=0, r=None):
    """Fresh word of it: the area centres near where it was, and shrinks."""
    if n.did:
        n.area = [n.x, n.y, 1, game.day]
        return
    base = {'territorial': 5, 'roaming': 9, 'raider': 8, 'ambusher': 5, 'nocturnal': 7}.get(n.habit, 7)
    r = r if r is not None else base
    jx, jy = random.randint(-r // 2, r // 2), random.randint(-r // 2, r // 2)
    n.area = [n.x + jx, n.y + jy, r, game.day - age]


def in_area(game, n, x, y):
    ax, ay, r = area(game, n)
    return cheb(x, y, ax, ay) <= r


# ------------------------------------------------------------------ days
def daily(game):
    w = game.world
    if not hasattr(w, 'regions'):
        return
    al = alive(game)
    # new ones appear as the world turns
    from .world import scaled
    want = scaled(4) + min(scaled(4), game.day // 10)
    if len([n for n in al if n.boss is None]) < want and random.random() < .5:
        make(game)
    for n in al:
        if n.back is not None:
            if game.day >= n.back:
                n.back = None
                if not n.scarred:
                    n.scarred = True
                n.fame += 1
                n.bounty = bounty(n)
                from . import news as NW
                NW.post(game, 'danger', f'{n.Full} is back, and hunting for the one who scarred {n.his()} hide.', n.x, n.y)
            continue
        if n.did:
            continue
        # moving about
        step = {'roaming': 4, 'raider': 3, 'nocturnal': 2}.get(n.habit, 1)
        if random.random() < .7:
            sp = _spot(game, n.x, n.y, 0, step) if step > 1 else None
            if sp and cheb(sp[0], sp[1], *n.home) <= (40 if n.habit == 'roaming' else 14):
                n.x, n.y = sp
        # raiders: news, and prices that move
        if n.habit == 'raider' and random.random() < .15:
            s = _near_town(game, n.x, n.y)
            if s and cheb(s.x, s.y, n.x, n.y) < 30:
                from . import news as NW
                NW.post(game, 'danger', f"{n.Full} and {n.his()} band raided the farms around {s.name}.", s.x, s.y)
                for g in s.produce:
                    s.market[g][0] *= .7
                report(game, n)
        # grudges: it comes for you on the road
        if n.knows_you and game.cur == 'over' and random.random() < .25:
            p = game.player
            dx, dy = (p.x > n.x) - (p.x < n.x), (p.y > n.y) - (p.y < n.y)
            for _ in range(6):
                nx, ny = n.x + dx, n.y + dy
                if game.maps['over'].inb(nx, ny) and D.TILES[game.maps['over'].tile(nx, ny)].walk:
                    n.x, n.y = nx, ny
        # fame: left alone too long, it grows
        if game.day - n.last_grow >= 10:
            n.last_grow = game.day
            grow(game, n)


def grow(game, n):
    n.fame += 1
    left = [t for t in TRAITS if t not in n.traits and (t != 'Multishot' or D.MONSTERS[n.k]['ranged'])
            and (t != 'Splitting' or n.k not in RACE)]
    if random.random() < .5 and left and len(n.traits) < 5:
        n.traits.append(random.choice(left))
    else:
        f = FOLLOW.get(n.k)
        from .creatures import BANDS
        pool = BANDS.get(n.k) or f
        if pool:
            n.following.append(random.choice([q for q in pool if not D.MONSTERS[q].get('chief')] or pool))
    n.lvl += 1 if n.fame % 2 == 0 else 0
    n.bounty = bounty(n)


# ------------------------------------------------------------------ out in the land
def step(game):
    """A step on the overworld: signs of the hunted, and meeting them."""
    if game.cur != 'over' or game.pending:
        return False
    from . import missions as MS
    from . import towns as TW
    p = game.player
    night = TW.is_night(game)
    hunted = {m.data.get('nid') for m in MS.active(game) if m.kind == 'hunt' and m.state == 'active'}
    for n in alive(game):
        if n.back is not None or n.did:
            continue
        near = 2 if n.habit != 'ambusher' else 3
        if cheb(n.x, n.y, p.x, p.y) <= near and (n.habit != 'nocturnal' or night):
            meet(game, n)
            return True
        if n.id in hunted and in_area(game, n, p.x, p.y):
            sign(game, n, night)
    return False


def sign_chance(game, n, night):
    from . import lifeskills as LS
    from . import guilds as GU
    from . import weather as WX
    c = .05 + .015 * LS.rank(game, 'foraging')
    if GU.state(game).get('wardens', {}).get('joined'):
        c += .03
    fam = WX.KINDS.get(WX.shown(game), ('', 'clear', 0))[1]
    if fam == 'rain':
        c *= .5                       # the rain washes the tracks away
    elif fam == 'snow':
        c *= 1.6                      # fresh snow shows them
    if n.habit == 'nocturnal' and night:
        c *= 1.5
    return c


def sign(game, n, night=False):
    if random.random() >= sign_chance(game, n, night):
        return
    from .engine import dir_name
    p = game.player
    d = cheb(n.x, n.y, p.x, p.y)
    age = 0 if d <= 6 else 1 if d <= 14 else 2
    what = random.choice(SIGNS[n.kind])
    way = dir_name(n.x - p.x, n.y - p.y)
    fresh = ['fresh', 'a day old', 'two days old'][age]
    if what.endswith('heading'):
        text = f'You find {what} {way}. {fresh.capitalize()}.'
    else:
        text = f'You find {what}, {fresh}. The trail leads {way}.'
    game.msg(text, 'info')
    # the area shrinks and moves towards it
    ax, ay, r = area(game, n)
    r2 = max(3, int(r * .6))
    n.area = [(n.x + p.x) // 2 + random.randint(-1, 1), (n.y + p.y) // 2 + random.randint(-1, 1), r2, game.day]
    n.sign_day = game.day


def meet(game, n, surprise=None):
    """Close enough: an encounter. You surprise it, or it surprises you."""
    p = game.player
    over = game.maps['over']
    keys = [n.k] + list(n.following)
    if surprise is None:
        fresh = getattr(n, 'sign_day', -9) >= game.day - 1
        surprise = 'you' if fresh and random.random() < .5 else 'it' if n.habit == 'ambusher' or n.knows_you else None
    game.start_encounter(None, over.tile(p.x, p.y), n.lvl, keys, 0, intro='')
    m = game.fight_map()
    boss = next((o for o in m.mons if o.k == n.k and not o.is_npc), None)
    if not boss:
        return
    apply(game, boss, n)
    game.named_fight = n.id
    if surprise == 'you':
        for o in m.mons:
            if not o.is_npc:
                o.awake = False
        game.msg(f"You come on {n.what()} and {'her' if n.gender == 'f' else 'his' if n.gender == 'm' else 'its'} band "
                 f"before they see you." if n.following else f'You come on {n.what()} before it sees you.', 'good')
    elif surprise == 'it':
        game.msg('They were waiting for you!' if n.following else 'It was waiting for you!', 'bad')
    else:
        game.msg(f'{n.Full} attacks!' if n.seen else f"{n.what()[0].upper() + n.what()[1:]} attacks!", 'bad')
    if n.knows_you:
        game.msg(f'{n.Full} knows you. {n.he().capitalize()} roars your name across the field: "{p.name.upper()}!"', 'bad')
    game.msg(game.escape_hint())
    from . import jobs as JB
    JB.on_named_meet(game, n)


def apply(game, mon, n):
    """Make a monster this named enemy."""
    mult = {'notable': (3.0, 1.2), 'notorious': (4.0, 1.3), 'legendary': (6.0, 1.45)}[n.rank]
    mon.named = n.id
    mon.elite = 2
    mon.name = n.full
    mon.fg = D.UNIQUE_FG
    mon.gender = n.gender
    mon.lvl = n.lvl
    mon.hp = mon.maxhp = round(mon.maxhp * mult[0])
    mon.dmg = tuple(round(v * mult[1]) for v in mon.dmg)
    mon.mods = list(n.traits)
    if 'Stone Skin' in n.traits:
        mon.df *= 2
        mon.hp = mon.maxhp = round(mon.maxhp * 1.2)
    if 'Shielded' in n.traits:
        mon.shield = 4
    if 'Swift' in n.traits:
        mon.mods.append('Fast')
    mon.weak_res = {n.weak: -50}
    base = getattr(mon, 'look', None) or f"{n.what()[0].upper() + n.what()[1:]}."
    mon.look = base.rstrip('.') + ', with ' + ' and '.join(n.looks) + '.'


def on_seen(game, mon):
    n = get(game, getattr(mon, 'named', None))
    if n and not n.seen:
        n.seen = True
        game.msg(f'This is {n.full}, who {n.past}.', 'unique')


def mon_turn(game, mon, df):
    """Its own habits: running when badly beaten, blinking, rage, calling its kin. True if the turn is used."""
    n = get(game, getattr(mon, 'named', None))
    if not n:
        return False
    p, m = game.player, game.map
    from .behave import The
    from .worldgen import free_around
    if game.visible(mon.x, mon.y):
        on_seen(game, mon)
        for t in mon.mods:
            if t in TRAIT_TEXT and t not in n.seen_traits:
                n.seen_traits.append(t)
    hp = mon.hp / max(1, mon.maxhp)
    if hp < .25 and not getattr(mon, 'tried_flee', False) and n.rank != 'legendary' or hp < .15 and n.rank == 'legendary' \
            and not getattr(mon, 'tried_flee', False):
        mon.tried_flee = True
        if random.random() < .55:
            flee(game, mon, n)
            return True
    if 'Berserk' in mon.mods and hp < .4 and not getattr(mon, 'enraged', False):
        mon.enraged = True
        mon.dmg = tuple(round(v * 1.4) + 1 for v in mon.dmg)
        game.msg(f'{The(mon)} flies into a rage!', 'bad')
        return True
    d = cheb(mon.x, mon.y, p.x, p.y)
    if 'Blink' in mon.mods and d >= 3 and random.random() < .15:
        sp = free_around(game, m, p.x, p.y, 1)
        if sp:
            mon.x, mon.y = random.choice(sp)
            game.msg(f'{The(mon)} steps through the air and is beside you!', 'bad')
            return True
    if 'Summoner' in mon.mods and mon.summons < 3 and random.random() < .1 and (n.following or FOLLOW.get(n.k)):
        sp = free_around(game, m, mon.x, mon.y, 1)
        if sp:
            from .entities import make_monster
            x, y = random.choice(sp)
            o = make_monster(game, random.choice(n.following or FOLLOW[n.k]), x, y, max(1, mon.lvl - 2))
            o.awake, o.pack = True, mon.pack
            m.mons.append(o)
            mon.summons += 1
            game.msg(f'{The(mon)} calls, and {o.the()} answers!', 'bad')
            return True
    return False


def flee(game, mon, n):
    """Beaten, it runs for its lair to heal, leaving a fresh blood trail. It will be back, scarred."""
    from .behave import The
    from .dress import add_blood
    m = game.map
    add_blood(m, mon.x, mon.y, 3)
    game.msg(f'{The(mon)} breaks away and flees, leaving a trail of blood!', 'gold')
    if mon in m.mons:
        m.mons.remove(mon)
    n.back = game.day + random.randint(5, 10)
    n.knows_you = True
    n.x, n.y = n.home
    report(game, n, r=3)


def on_kill(game, mon):
    n = get(game, getattr(mon, 'named', None))
    if not n:
        return
    from .entities import Item, make_gear
    from . import news as NW
    m = game.map
    n.alive = False
    n.seen = True
    t = Item(game.new_id(), 'trophy', n.trophy)
    t.name = f"{poss(n.full)} {n.trophy}"
    t.named = n.id
    game.spill(m, mon.x, mon.y, t)
    if n.kept:
        game.spill(m, mon.x, mon.y, n.kept)
        game.msg(f'{n.Full} still had your {n.kept.name}.', 'good')
        n.kept = None
    if n.rank == 'legendary' and mon.k in D.GEAR_USERS:
        it = make_gear(game, random.choice(D.GEAR_USERS[mon.k]), 'rare', n.lvl + 2)
        game.spill(m, mon.x, mon.y, it)
        game.announce(it)
    ox, oy = game.over_pos if game.cur != 'over' else (game.player.x, game.player.y)
    NW.post(game, 'danger', f'{n.Full} is dead. Someone brought down {n.his()} {n.rank} hide at last.', ox, oy)
    game.msg(f'You take {t.name}. Anyone who posted a bounty on {n.his()} head will pay for it.', 'gold')
    from . import chronicle as CH
    CH.deed(game, f'{n.Full} slain', f'You brought down {n.Full}, the {n.rank} {D.MONSTERS[mon.k]["name"].lower()}, '
                                     f'in {m.name}.', (ox, oy))
    # a lieutenant's body tells where the boss hides
    if n.boss is not None:
        b = get(game, n.boss)
        if b and b.alive and not any(o.alive and o.boss == b.id for o in store(game).values()):
            report(game, b, r=3)
            game.msg(f"On {n.his()} body, a scrawled map: {b.full} hides near {place(game.world.region_at(b.x, b.y))}.", 'unique')
            from . import missions as MS
            for mi in MS.active(game):
                if mi.kind == 'hunt' and mi.data.get('nid') == n.id:
                    nm = hunt_mission(game, b, mi.giver, mi.hold)
                    if nm and len(MS.active(game)) < MS.MAX_ACTIVE:
                        nm.state = 'active'
                        game.missions.append(nm)
                        game.msg(f'New job: {nm.title}.', 'gold')
    from . import missions as MS
    for mi in MS.active(game):
        if mi.kind == 'hunt' and mi.data.get('nid') == n.id and mi.state == 'active':
            mi.state = 'turnin'


def on_player_death(game):
    """It killed you: it takes a piece of your gear, and a new name."""
    p = game.player
    m = game.map
    for o in m.mons:
        n = get(game, getattr(o, 'named', None))
        if n and n.alive:                      # it, or its band: the name is its
            n.slayer = p.name
            n.knows_you = True
            n.fame += 2
            n.bounty = bounty(n)
            gear = [it for it in p.inv if game.is_equipped(it) and it.k == 'gear']
            if gear and not n.kept:
                it = random.choice(gear)
                slot = next((s for s in D.SLOTS if game.eq_item(s) is it), None)
                if slot:
                    game.unequip(slot)
                if it in p.inv:
                    p.inv.remove(it)
                n.kept = it
                game.msg(f'{n.name} took your {it.name}. Kill {"her" if n.gender == "f" else "him" if n.gender == "m" else "it"} '
                         f'to get it back.', 'bad')
            return


def after_fight(game):
    """The battle map is left: a named enemy still on it slips away, healed a little."""
    nid = getattr(game, 'named_fight', None)
    game.named_fight = None
    n = get(game, nid)
    if not n or not n.alive:
        return
    n.seen = True
    n.knows_you = n.knows_you or n.back is not None
    report(game, n, r=4)


def on_enter_level(game, m):
    """A legend in its lair."""
    did, depth = getattr(m, 'did', None), getattr(m, 'depth', None)
    for n in alive(game):
        if n.did == did and n.depth == depth and n.back is None and not any(getattr(o, 'named', None) == n.id for o in m.mons):
            from .entities import make_monster
            from .worldgen import rand_free, free_around
            from .data import FLOOR
            up = m.t.index(D.UP) if D.UP in m.t else 0
            best = None
            for _ in range(200):
                c = rand_free(game, m, lambda t: t == FLOOR)
                if c and (best is None or cheb(*c, up % m.w, up // m.w) > cheb(*best, up % m.w, up // m.w)):
                    best = c
            if not best:
                return
            boss = make_monster(game, n.k, best[0], best[1], n.lvl)
            apply(game, boss, n)
            pid = game.new_id()
            boss.pack = pid
            m.mons.append(boss)
            for (x, y), k in zip(free_around(game, m, best[0], best[1], 2), n.following):
                o = make_monster(game, k, x, y, max(1, n.lvl - 1))
                o.pack = pid
                m.mons.append(o)


# ------------------------------------------------------------------ jobs and bounties
def hunt_mission(game, n, giver, hold=None):
    from . import missions as MS
    from . import calendar as CAL  # noqa: F401
    mi = MS.Mission(game.new_id(), 'hunt', giver)
    mi.hold = hold
    mi.data = dict(nid=n.id)
    mi.reward = n.bounty
    mi.rep = random.randint(6, 10)
    w = game.world
    if giver is not None:
        mi.faction = w.settlements[giver].faction
    mi.title = f'WANTED: {n.full if len(n.full) <= 32 else n.name}'
    mi.desc = describe_job(game, n, giver)
    return mi


def describe_job(game, n, giver):
    w = game.world
    if n.area is None:
        report(game, n, age=random.randint(1, 4))
    ax, ay, r = area(game, n)
    age = max(0, game.day - n.area[3])
    when = 'today' if age == 0 else 'yesterday' if age == 1 else f'{age} days ago'
    reg = place(w.region_at(ax, ay))
    lead = ''
    if n.boss is not None:
        b = get(game, n.boss)
        if b and b.alive:
            lead = f' {n.he().capitalize()} rides for {b.full}; kill {n.his()} lieutenants and one of them will lead you to {b.name}.'
    sub = [o for o in alive(game) if o.boss == n.id]
    if sub:
        lead = (f" Nobody knows where {n.he()} hides. {n.his().capitalize()} lieutenant{'s' if len(sub) > 1 else ''} "
                f"{' and '.join(o.full for o in sub)} might.")
    where = (f'{n.he().capitalize()} keeps to the deepest hall of {w.dungeons[n.did].name}.' if n.did else
             f'Last seen in {reg}, {when}.')
    return (f"{n.Full}, {n.what()}, who {n.past}. {where} "
            f"{'Rumour has it that ' + n.weak_text() + '. ' if n.weak else ''}Bring back {n.his()} {n.trophy}.{lead}")


def offer(game, s, prey=None, max_rank=None):
    """A hunt job for the board of s: a named enemy within reach, or a new one."""
    cands = [n for n in alive(game) if cheb(n.x, n.y, s.x, s.y) <= 70 and n.back is None
             and (prey is None or PREY_OF.get(n.k) == prey)
             and (max_rank is None or RANKS.index(n.rank) <= max_rank)
             and not any(m.kind == 'hunt' and m.data.get('nid') == n.id and m.state in ('active', 'turnin') for m in game.missions)]
    # a boss whose lieutenants live is offered through them
    cands = [n for n in cands if not any(o.alive and o.boss == n.id for o in store(game).values())] or cands
    n = random.choice(cands) if cands and random.random() < .75 else None
    if not n:
        r = None if max_rank is None else RANKS[min(max_rank, 2)] if random.random() < .4 else 'notable'
        n = make(game, s.x, s.y, prey, r)
        if n and n.boss is None:
            sub = [o for o in alive(game) if o.boss == n.id]
            if sub:
                n = random.choice(sub)
    if not n:
        return None
    report(game, n, age=max(0, cheb(n.x, n.y, s.x, s.y) // 25))
    return hunt_mission(game, n, s.id)


def posted(game, n, s):
    """Is there a bounty on it here? Wherever it is known: within a long walk of where it lives."""
    return cheb(n.home[0], n.home[1], s.x, s.y) <= 70


def hand_in(game, s):
    """In a town: hand in trophies for hunts, or for bounties posted here."""
    from . import missions as MS
    from .money import fmt
    p = game.player
    for t in [it for it in p.inv if it.k == 'trophy']:
        n = get(game, getattr(t, 'named', None))
        if not n:
            continue
        mi = next((m for m in MS.active(game) if m.kind == 'hunt' and m.data.get('nid') == n.id), None)
        if mi and (mi.giver == s.id or posted(game, n, s)):
            p.inv.remove(t)
            mi.state = 'turnin'
            MS.complete(game, mi, [s.id] + ([mi.giver] if mi.giver is not None and mi.giver != s.id else []))
            continue
        if not mi and posted(game, n, s) and not getattr(t, 'paid', False):
            p.inv.remove(t)
            p.gold += n.bounty
            s.rep = min(100, s.rep + 4)
            game.msg(f"There is a bounty on {n.full} posted here. The reeve pays you {fmt(n.bounty)} for the {n.trophy}.", 'gold')


# ------------------------------------------------------------------ the journal
def journal(game):
    """Lines about the ones you hunt: (title, text)."""
    from . import missions as MS
    out = []
    for mi in MS.active(game):
        if mi.kind != 'hunt':
            continue
        n = get(game, mi.data.get('nid'))
        if not n:
            continue
        if not n.alive:
            out.append((n.full, f'Dead. Bring {n.his()} {n.trophy} to {MS.giver_name(game, mi)} for {fmt_c(mi.reward)}.'))
            continue
        ax, ay, r = area(game, n)
        age = game.day - n.area[3]
        seen = ', '.join(TRAIT_TEXT[t] for t in n.seen_traits) or 'none seen yet'
        where = (f'in {game.world.dungeons[n.did].name}' if n.did else
                 f"near {place(game.world.region_at(ax, ay))}, {'today' if age <= 0 else f'{age} days ago'} ({r} leagues around)")
        out.append((n.full, f"{n.what()[0].upper() + n.what()[1:]} with {' and '.join(n.looks)}; {n.past}. "
                    f"Last seen {where}. {HABITS[n.habit].capitalize()}. Traits: {seen}. "
                    f"{'Back from licking its wounds soon. ' if n.back else ''}Reward {fmt_c(mi.reward)}."))
    return out


def job_line(game, mi):
    """One or two lines for the journal: where it was last seen, and what you know of it."""
    n = get(game, mi.data.get('nid'))
    if not n:
        return ''
    if not n.alive:
        return f'Dead. Bring {n.his()} {n.trophy} to a town that pays for it.'
    if n.did:
        where = f'in the deepest hall of {game.world.dungeons[n.did].name}'
    else:
        ax, ay, r = area(game, n)
        age = game.day - n.area[3]
        where = f"near {place(game.world.region_at(ax, ay))}, {'today' if age <= 0 else '1 day ago' if age == 1 else f'{age} days ago'}" \
                f' ({r} leagues around)'
    seen = '; '.join(TRAIT_TEXT[t] for t in n.seen_traits) or 'none seen yet'
    back = ' Gone to ground to lick its wounds.' if n.back else ''
    return f'{n.what().capitalize()}, {HABITS[n.habit]}. Last seen {where}. Traits: {seen}.{back}'


def fmt_c(v):
    from .money import fmt
    return fmt(v)
