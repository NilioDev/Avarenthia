"""The servants of the Hollow King: the kinds a world draws its three from (one light, one middle, one heavy). Each
sleeps or wakes in a lair in its own land and leaves its mark on the land around it: blight, ash, webs, war, flood,
hunger, wolves or swayed lords. It strikes at the villages in its shadow and, once the Hollow King's attention is on
you, sends hunters after you. Destroy one and its mark fades. How they grow, push the realms and break the seals
is shadow.py."""
import math
import random

from . import data as D
from .worldgen import cheb
from . import news as NW


def where(game, e):
    return e.x, e.y


EVILS = {
    'lich': dict(
        names=['Morvenna the Undying', 'Velgrath the Pale', 'Ysmeer the Bone Queen'], title='the Lich', boss='lich',
        lair='Crypt of {short}', style='rooms', tag='crypt', depth=5, base=7, wall='#7e869c', terrain=('swamp', 'forest'),
        taint='blight', taint_name='blight', fg=(196, 134, 255), event='undead',
        hunt=['skeleton', 'zombie', 'skarcher', 'ghost', 'wraith'], hunt_glyph='W',
        hunt_names=['Herald of {short}', "{short}'s Gravecaller", 'The Pale Rider', 'The Bone Shepherd'],
        cult=('The Cult of the Undying', 'Cult', ['cultist', 'skeleton', 'zombie', 'skarcher'], 'Black Spire', 'Bone Tower'),
        whispers=['Somewhere a grave bell rings once, though there is no church near.',
                  'You hear a woman singing, far away. No one else seems to hear it.',
                  'Frost creeps over your boots, though the night is mild.',
                  'Dry leaves blow across the path in a ring, and lie still.',
                  'A crow lands nearby and watches you with pale, dead eyes.',
                  'A fresh grave by the road has been dug open, from below.', 'Your shadow moves a heartbeat after you do.'],
        rumors=['The graves are restless lately. They say {short} is waking.',
                'Nothing grows near the old crypt any more. The blight spreads every season.',
                'My cousin saw the dead walking on the road at night. Walking, I tell you.'],
        lore='a sorceress who would not die. She raises the dead, and a grey blight spreads from her crypt.',
        omen='The birds fall silent. {name} grows stronger, and the blight creeps further over the land.',
        defeat='{name} shrieks and crumbles to dust. The blight begins to lift.'),
    'dragon': dict(
        names=['Vyrmathrax the Red', 'Calderyx the Burning', 'Ossarax the Ashen Wing'], title='the Dragon', boss='dragon',
        lair='Lair of {short}', style='cave', tag='lair_dragon', depth=4, base=9, wall='#8a5040', terrain=('hills',),
        taint='scorch', taint_name='scorched land', fg=(255, 110, 50), event='fire',
        hunt=['drake', 'drake', 'cultist'], hunt_glyph='d',
        hunt_names=['Wyrmlings of {short}', 'A brood of drakes', 'The Fire-scaled'],
        cult=('The Cult of the Wyrm', 'Wyrm Cult', ['cultist', 'cultist', 'drake'], 'Ember Keep', 'Ash Tower'),
        whispers=['A roar rolls over the hills, so deep you feel it in your chest.', 'Ash drifts down like grey snow.',
                  'Far away, the night sky glows red.', 'A great shadow passes over the moon.',
                  'The smell of smoke is everywhere today.'],
        rumors=['{short} took three cows from Hob\'s farm. And Hob.', 'They say the dragon sleeps on a bed of melted crowns.',
                'Another village burned. The sky was red all night.'],
        lore='an ancient dragon. It burns the villages near its lair and scorches the land black.',
        omen='Smoke on the horizon. {name} has woken hungry, and the scorched land spreads.',
        defeat='{name} crashes to the ground with a sound like a landslide. The fires die down.'),
    'spider': dict(
        names=['Ysolde the Brood Mother', 'Ixxiza, Mother of Webs', 'The Grey Queen'], title='the Brood Mother',
        boss='broodmother', lair='The Webbed Hollow', style='cave', tag='lair_spider', depth=4, base=6, wall='#6a6a78',
        terrain=('forest',), taint='web', taint_name='webbed woods', fg=(225, 225, 240), event='plague',
        hunt=['spider', 'spider', 'spider'], hunt_glyph='s', hunt_names=['A swarm of her brood', 'Children of {short}'],
        cult=('The Silk Sisters', 'Silk', ['cultist', 'spider', 'spider'], 'Silk Spire', 'Web Tower'),
        whispers=['You brush something sticky from your face. Webs, everywhere.', 'Something skitters just out of sight.',
                  'A thousand tiny legs patter on the leaves overhead.', 'You find a cocoon the size of a man. It twitches.'],
        rumors=['The woods are full of webs now. Woodcutters stopped going in.', 'Folk go missing near the old hollow.',
                'They say the Brood Mother lays a hundred eggs a night.'],
        lore='a monstrous spider queen. Her webs choke the forests and her brood carries sickness.',
        omen='The forests grow quiet and grey with silk. {name} is breeding.',
        defeat='{name} curls up and dies. Her brood scatters in panic.'),
    'warlord': dict(
        names=['Gruzzak Skullsplitter', 'Ulgrim Bloodtusk', 'Mogha the Red Fist'], title='the Warlord', boss='warlord',
        lair='{short}\'s Fortress', style='rooms', tag='lair_orc', depth=4, base=8, wall='#8a6a50', terrain=('hills', 'grass'),
        taint='warpath', taint_name='warpath', fg=(232, 84, 52), event='war',
        hunt=['orc', 'orc', 'gobarcher', 'ogre'], hunt_glyph='O', hunt_names=["{short}'s Raiders", 'A war party', 'The Skull Riders'],
        cult=('The Iron Warhost', 'Warhost', ['orc', 'orc', 'gobarcher', 'ogre'], 'War Keep', 'Skull Tower'),
        whispers=['War drums in the distance.', 'Smoke on the horizon: another farm burns.',
                  'You find a pike with a skull on it, planted by the road. A warning.',
                  'Crows follow you. They know where the battles are.'],
        rumors=['{short} has united the tribes. Nobody has done that in a hundred years.',
                'Refugees came through last night. Their village is ashes.', 'They say {short} wears the crowns of three kings.'],
        lore='a warlord who has united the goblin and orc tribes. His warbands burn everything in their path.',
        omen='War drums. {name} has gathered more warriors, and the warpath spreads.',
        defeat='{name} falls, and his warhost breaks apart into squabbling tribes.'),
    'drowned': dict(
        names=['The Drowned King', 'Old Mother Brine', 'Sargath of the Deep'], title='the Drowned One', boss='drowned_king',
        lair='The Sunken Abbey', style='rooms', tag='lair_drowned', depth=4, base=7, wall='#5a7a7a', terrain=('swamp', 'coast'),
        taint='mire', taint_name='rising mire', fg=(90, 196, 176), event='famine',
        hunt=['drowned', 'drowned', 'zombie'], hunt_glyph='z', hunt_names=['The Drowned Host', 'Bog-walkers of {short}'],
        cult=('The Tide Cult', 'Tide Cult', ['cultist', 'drowned', 'drowned'], 'Tide Spire', 'Bog Tower'),
        whispers=['Water seeps into your boots, cold as a grave.', 'You hear bells ringing under the water.',
                  'Wet footprints lead up to your camp, and stop.', 'The rain tastes of salt and rot.'],
        rumors=['The fields are flooding. The harvest rots in the mud.', 'Fishermen pull up the drowned in their nets. They still move.',
                'The marsh grows every year. Soon it will swallow us all.'],
        lore='something old that sleeps beneath a drowned abbey. The mire spreads, the fields flood and the drowned walk.',
        omen='The waters rise. {name} stirs in the deep, and the mire spreads.',
        defeat='{name} sinks back into the black water, never to rise again. The floods recede.'),
    'wendigo': dict(
        names=['The Wendigo', 'Hunger-in-the-Snow', 'Old Antlers'], title='the Wendigo', boss='wendigo',
        lair='The Bone Lodge', style='cave', tag='lair_wendigo', depth=4, base=6, wall='#8a9aa4', terrain=('cold', 'forest'),
        taint='hunger', taint_name='hungry woods', fg=(200, 220, 232), event='famine',
        hunt=['winter_wolf', 'ghoul', 'snow_ape'], hunt_glyph='W',
        hunt_names=['The Starved of {short}', 'Things that were hunters', 'The Hollow-bellied'],
        cult=('The Fasting Lodge', 'Fasters', ['cultist', 'ghoul', 'winter_wolf'], 'Bone Lodge', 'Antler Tower'),
        whispers=['Something calls your name from the trees, in your mother\'s voice.', 'You are hungry. You have never been this hungry.',
                  'Antlers move between the trunks, far too high up for any deer.', 'The snow by the path is full of tracks that end.'],
        rumors=['The hunters went up into the woods in autumn. None came back.', 'The deer are gone. The hares are gone. What eats them?',
                'They say it was a man once, who ate his own kin in a hard winter.'],
        lore='a hunger that walks on two legs in the cold woods. Hunters do not come back, and the game is gone.',
        omen='The woods go still. {name} is hungry, and the hungry woods spread.',
        defeat='{name} falls in the snow, and is only bones and old antlers. Far off, a deer calls.'),
    'wolf': dict(
        names=['Fenra the Great Wolf', 'Old Greymane', 'The Wolf of the Long Grass'], title='the Great Wolf', boss='great_wolf',
        lair='The Wolf Hollow', style='cave', tag='lair_wolf', depth=3, base=5, wall='#8a7a64', terrain=('grass', 'hills'),
        taint='wolfland', taint_name='wolf country', fg=(196, 190, 176), event='famine',
        hunt=['wolf', 'worg', 'winter_wolf'], hunt_glyph='C',
        hunt_names=['The pack of {short}', 'Grey runners', 'The Long Grass Pack'],
        cult=('The Wolf-Sworn', 'Wolf-Sworn', ['cultist', 'wolf', 'worg'], 'Grey Lodge', 'Howling Tower'),
        whispers=['A howl answers another, closer than the last.', 'Grey shapes run beside you in the long grass, then are gone.',
                  'The sheep in the fold all face the same way, and shake.', 'You find a lamb, or half of one.'],
        rumors=['The wolves are bigger this year, and cleverer. They wait until the dogs are asleep.',
                'Old Harl lost his whole flock in one night. Not a sheep left, and no blood.', 'The shepherds are leaving the plain.'],
        lore='a wolf as big as a horse, older than the roads. The packs follow it, the flocks die, the shepherds go.',
        omen='Howling all night. {name} calls the packs together, and wolf country spreads.',
        defeat='{name} lies still at last, grey and enormous. The packs break up and run.'),
    'mage': dict(
        names=['Azrael Vey the Fallen', 'Magister Oduran', 'Ysolt the Unbound'], title='the Fallen Mage', boss='fallen_mage',
        lair='The Unlit Tower', style='rooms', tag='lair_mage', depth=5, base=8, wall='#6a5a80', terrain=('forest', 'hills', 'grass'),
        taint='sway', taint_name='swayed land', fg=(176, 96, 224), event='war',
        hunt=['cultist', 'skel_mage', 'imp', 'animated_armour'], hunt_glyph='@',
        hunt_names=['The Grey Hands of {short}', 'Sworn Magisters', 'The Unlit'],
        cult=('The Circle of the Unlit', 'Unlit', ['cultist', 'cultist', 'skel_mage'], 'Unlit Tower', 'Black Library'),
        whispers=['For a moment you know exactly what to do, and it is not your thought.', 'Ink stains on your hands. You wrote nothing.',
                  'A letter lies on the road, sealed with no arms, addressed to no one.', 'Your shadow reads over your shoulder.'],
        rumors=['The baron has a new counsellor. Nobody saw him come.', 'They say the Circle threw one of its own out, and he did not go far.',
                'Lords who never agreed on anything all sign the same letters now.'],
        lore='a mage the Circle cast out. He does not raise armies; he takes the lords, one by one, from inside.',
        omen='Another lord bends the knee to no one you can see. {name} grows stronger, and the swayed land spreads.',
        defeat='{name} burns from the inside, like a page. The lords he held wake up and look at what they signed.'),
}
EVIL_KEYS = list(EVILS)
# what people notice before anyone knows what is behind it
SIGNS = {
    'blight': ['The birds have gone quiet in the far woods, and grey patches spread where nothing grows.',
               'A shepherd swears he saw his dead father walking the hills at night.',
               'The crops wither near the old graveyards. Nobody knows why.'],
    'scorch': ['Smoke on the far horizon again. Travellers speak of burned farms.',
               'Cattle go missing in the hills, whole herds at a time.',
               'A merchant swears the night sky glowed red over the mountains.'],
    'web': ['Woodcutters say the deep forest has gone quiet, and grey with silk.',
            'Hunters stopped going into the old woods. Some never came out.',
            'A child in the market found a spider the size of a dog. Dead, thank the gods.'],
    'warpath': ['Refugees on the road speak of raiders, more of them every season.',
                'The goblin tribes are quiet. Too quiet, the old soldiers say.',
                'Someone burned a farmstead in the hills and left a skull on a pike.'],
    'mire': ['The marshes are rising. Fields that were dry last year are under water.',
             'Fishermen pull strange things from the water lately, and will not say what.',
             'Bells ring under the marsh at night, they say. There is no church there.'],
    'hunger': ['Hunters in the north woods do not come back. The deer are gone too.',
               'A trapper came down out of the snow and would not stop eating.',
               'Something with antlers was seen at the edge of the trees, standing like a man.'],
    'wolfland': ['The wolves are bolder on the plain this year. Whole flocks lost.',
                 'Shepherds are driving their sheep to the towns and not going back.',
                 'A howl at night that the dogs will not answer.'],
    'sway': ['Barons who hated each other sign the same letters now.',
             'A new counsellor at a lord\'s side, and nobody knows where he came from.',
             'The Circle of Magi will not say why one of its towers stands empty.'],
}
# each servant's weight: a light one is awake from the start in its own land, a middle one wakes halfway and holds a
# few baronies or a coast, a heavy one wakes late and reaches a whole realm or more (shadow.py)
WEIGHT = {'spider': 'light', 'wendigo': 'light', 'wolf': 'light', 'dragon': 'middle', 'drowned': 'middle',
          'lich': 'heavy', 'warlord': 'heavy', 'mage': 'heavy'}
STAGES = ['Dreaming', 'Stirring', 'Restless', 'Watching', 'Searching', 'Hunting', 'Hunting', 'Wrathful', 'Wrathful',
          'Ascendant', 'Ascendant']
DIVE_COST = {'web': 6, 'mire': 6, 'hunger': 4}


class Evil:
    def __init__(self, key, name):
        self.key, self.name = key, name
        self.short = name.split()[0].rstrip(',') if not name.startswith(('The ', 'Old ')) else name
        self.did = None
        self.x = self.y = 0
        self.pace = 0
        self.lvl = 0
        self.defeated = False
        self.known = False
        self.weight = 'light'
        self.awake = False        # the slow clock: a light one from the start, the others later (shadow.py)
        self.wake_day = 0
        self.goal = 0.0           # 0..100: at 100 it has what it wants, and a seal breaks
        self.sealed = False
        self.lts = []             # its three lieutenants (dicts), each with a place of its own
        self.back = None          # the day the Lich rises again, if her phylactery was left whole

    @property
    def d(self):
        return EVILS[self.key]

    @property
    def fg(self):
        return self.d['fg']


def choose(n=None):
    """Three servants, one of each weight: the heavy one first (its cult is the world's cult), then the middle and
    the light one. A kind whose land the world turns out not to have is swapped when the lairs are placed."""
    out = []
    for wt in ('heavy', 'middle', 'light'):
        k = random.choice([k for k in EVIL_KEYS if WEIGHT[k] == wt])
        out.append(make(k))
    return out


def make(k):
    e = Evil(k, random.choice(EVILS[k]['names']))
    e.weight = WEIGHT[k]
    return e


def setup_monsters(world):
    """Give boss monsters the names they have in this world."""
    for e in world.evils:
        D.MONSTERS[e.d['boss']]['name'] = e.name


def info(e):
    """The dict used to build the cult faction."""
    d = e.d
    return dict(key=e.key, name=e.name, fg=d['fg'], cult=d['cult'])


# ------------------------------------------------------------------ strength and the mark on the land
def strength(game, e):
    """How strong it is now: from its own slow clock and the Hollow King's attention, never from your level
    (shadow.py)."""
    from . import shadow as SH
    return SH.power(game, e)


def active(game):
    return [e for e in game.world.evils if not e.defeated]


def stage(e):
    return 'Destroyed' if e.defeated else STAGES[min(len(STAGES) - 1, e.lvl)]


def strongest(game):
    act = active(game)
    return max(act, key=lambda e: (e.lvl, -e.pace)) if act else None


def _smooth_noise(x, y, cell=9, salt=17):
    from .look import _h
    gx, gy = x / cell, y / cell
    x0, y0 = int(gx), int(gy)
    fx, fy = gx - x0, gy - y0
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    v = [[_h(x0 + i, y0 + j, salt) / 65535 for i in (0, 1)] for j in (0, 1)]
    a = v[0][0] + (v[0][1] - v[0][0]) * fx
    b = v[1][0] + (v[1][1] - v[1][0]) * fx
    return a + (b - a) * fy


def compute_taint(game):
    w = game.world
    om = game.maps['over']
    tn = bytearray(om.w * om.h)
    for idx, e in enumerate(w.evils):
        from .shadow import reach
        r = 0 if e.defeated else reach(e)
        if not r:
            continue
        for y in range(max(0, e.y - r * 2), min(om.h, e.y + r * 2 + 1)):
            for x in range(max(0, e.x - r * 2), min(om.w, e.x + r * 2 + 1)):
                i = y * om.w + x
                if tn[i] or om.t[i] == D.WATER:
                    continue
                d = math.hypot(x - e.x, (y - e.y) * 1.4)
                if d < r * (.6 + .8 * _smooth_noise(x, y, 9, 17 + idx)):
                    tn[i] = idx + 1
    w.taint = tn


def taint_at(game, x, y):
    """The evil whose mark lies on this overworld cell, or None."""
    tn = getattr(game.world, 'taint', None)
    if not tn:
        return None
    v = tn[y * game.maps['over'].w + x]
    return game.world.evils[v - 1] if v else None


def update(game, announce=True):
    w = game.world
    changed = getattr(w, 'taint', None) is None
    for e in w.evils:
        old = e.lvl
        e.lvl = strength(game, e)
        if e.lvl != old:
            changed = True
        if announce and e.lvl > old and e.lvl >= 2:
            if e.known:
                game.msg(e.d['omen'].format(name=e.name, short=e.short), 'unique')
            else:
                NW.post(game, 'danger', random.choice(SIGNS[e.d['taint']]), *where(game, e))
        if e.lvl >= 4 and not e.known and not e.defeated:
            learn(game, e)
    if changed:
        compute_taint(game)


def learn(game, e):
    """The rumours finally get a name."""
    e.known = True
    om = game.maps['over']
    om.seen[e.y * om.w + e.x] = 1
    game.msg(f'The rumours have a name now: {e.name}, {e.d["lore"]} Its lair lies far to the {game.dir_to(e.did)}.', 'unique')
    if not game.flags.get('evil_dialog'):
        game.flags['evil_dialog'] = True
        game.request = ('dialog', 'A darkness with a name',
                        f'For a long time there were only rumours. Burned farms, empty villages, things seen at night. '
                        f'Now everyone speaks the same name: {e.name}.\n\n{e.name}, {e.d["lore"]}\n\n'
                        f'It grows stronger every season. Someone could try to stop it. Or not. The world will go on either way, '
                        f'for a while.')


def defeat(game, e):
    e.defeated = True
    e.lvl = 0
    game.msg(e.d['defeat'].format(name=e.name), 'unique')
    w = game.world
    idx = w.evils.index(e)
    w.wanderers = [x for x in w.wanderers if not (x.kind == 'hunt' and getattr(x, 'evil', None) == idx)]
    compute_taint(game)
    from . import shadow as SH
    SH.fallen(game, e)


def on_kill(game, mon):
    from . import shadow as SH
    from . import skyseat as SK
    if SH.on_kill(game, mon) or SK.on_kill(game, mon):
        return
    for e in game.world.evils:
        if not e.defeated and mon.k == e.d['boss']:
            if SH.returns(game, e, mon):
                return
            defeat(game, e)
            from . import chronicle as CH
            CH.deed(game, f'{e.name} destroyed', f'You destroyed {e.name} in its lair.', (e.x, e.y) if hasattr(e, 'x') else None)


# ------------------------------------------------------------------ the evils at work
def whisper(game):
    act = [e for e in active(game) if e.lvl]
    if not act:
        return
    from .towns import is_night
    p = game.player
    here = taint_at(game, p.x, p.y) if game.cur == 'over' else None
    if not (is_night(game) or here):
        return
    lvl = max(e.lvl for e in act)
    if lvl >= 3 and random.random() < lvl * .0008 + (.003 if here else 0):
        e = here if here else random.choices(act, [x.lvl for x in act])[0]
        game.msg(random.choice(e.d['whispers']), 'unique')


def daily(game):
    from . import shadow as SH
    SH.daily(game)
    update(game)
    w = game.world
    for idx, e in enumerate(w.evils):
        if e.defeated or not e.lvl:
            continue
        for s in w.settlements:
            if e.lvl >= 2 and s.event is None and taint_at(game, s.x, s.y) is e and random.random() < .04 + e.lvl * .015:
                key = e.d['event']
                ev = D.EVENTS[key]
                s.event = (key, random.randint(4, 7))
                for g in (ev['good'], ev.get('also')):
                    if g:
                        s.market[g][1] = ev['target']
                        s.market[g][0] = min(s.market[g][0], ev['target'] * 2)
                who = e.name if e.known else 'Something'
                NW.post(game, 'danger', f'{who} struck at {s.name}! ' + ev['text'].format(town=s.name), s.x, s.y)


def spawn_hunt(game, idx):
    from .wanderers import make_group, wanderer_at, passable
    w = game.world
    e = w.evils[idx]
    om = game.maps['over']
    p = game.player
    ox, oy = (p.x, p.y) if game.cur == 'over' else game.over_pos
    for _ in range(300):
        a = random.random() * math.tau
        dd = random.randint(24, 40)
        x, y = int(ox + math.cos(a) * dd), int(oy + math.sin(a) * dd * .6)
        if not om.inb(x, y) or not passable(game, x, y, True) or wanderer_at(game, x, y):
            continue
        if any(cheb(x, y, s.x, s.y) < 6 for s in w.settlements):
            continue
        lvl = p.lvl + 1
        pool = [k for k in e.d['hunt'] if D.MONSTERS[k]['min_l'] <= lvl + 2] or e.d['hunt'][:1]
        keys = [random.choice(pool) for _ in range(random.randint(3, 4 + e.lvl // 3))]
        leader = random.choice(e.d['hunt_names']).format(short=e.short)
        wd = make_group(game, 'monsters', x, y, lvl, keys, 2, leader)
        wd.kind = 'hunt'
        wd.evil = idx
        wd.fg = e.fg
        wd.ch = e.d['hunt_glyph']
        wd.name = f'{leader}, sent by {e.name}'
        wd.speed = 12
        wd.warned = False
        w.wanderers.append(wd)
        return wd
    return None


def sense(game):
    if game.cur != 'over':
        return
    p = game.player
    for wd in game.world.wanderers:
        if wd.kind == 'hunt' and not getattr(wd, 'warned', True) and cheb(wd.x, wd.y, p.x, p.y) <= 16:
            wd.warned = True
            e = game.world.evils[wd.evil]
            game.msg(f'The air turns cold. You feel eyes upon you: {e.name} has found you.', 'bad')


def wild_keys(game, x, y, lvl):
    """Monsters for an ambush on land marked by an evil, or None."""
    e = taint_at(game, x, y)
    if not e or random.random() > .6:
        return None
    pool = [k for k in e.d['hunt'] if D.MONSTERS[k]['min_l'] <= lvl + 2] or e.d['hunt'][:1]
    return [random.choice(pool) for _ in range(random.randint(2, 3 + lvl // 4))]


def rumor(game):
    act = [e for e in active(game) if e.lvl >= 2]
    if not act:
        return None
    e = random.choice(act)
    if not e.known:
        return random.choice(SIGNS[e.d['taint']])
    return random.choice(e.d['rumors']).format(short=e.short, name=e.name)


def describe(game, e):
    if e.defeated:
        return 'Destroyed.'
    return {0: 'Asleep in its lair. Its mark on the land is small, for now.',
            1: 'Stirring. Its mark on the land begins to spread.',
            2: 'Restless. The villages near its lair suffer.',
            3: 'Watching you.',
            4: 'Searching for you. Its servants roam the land.'}.get(e.lvl, 'Hunting you, and swallowing the land.')
