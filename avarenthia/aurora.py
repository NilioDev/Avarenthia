"""The northern lights' gift (round 8). While the lights are in the sky (weather.py 'aurora': the cold lands, autumn
and winter nights) they give four things: old rune stones glow and point the way to a hidden place (hidden.py);
Frost and Storm cost less mana (skills.cost_of); at a barrow in the north a spirit rises and gives an errand, and
woe to whoever digs into or robs its barrow; and the glow itself: a wan blue-green light round ghostly creatures
(brighter and restless when they are angry) and a faint red fire glow round fiends."""
import math
import random

from . import data as D
from .worldgen import cheb

GLOW = (60, 190, 190)              # wan blue-green
ANGRY = (120, 255, 210)            # brighter, colder, restless
CORE = (225, 255, 250)
FIRE = (220, 84, 40)
RUNE = (110, 235, 210)
GHOSTLY = {'ghost', 'wraith', 'banshee', 'shade', 'wight', 'barrow_spirit'}
CHEAPER = .75                      # Frost and Storm under the lights
LINES = ('frost', 'storm')
SPIRIT_FG = '#bfeee8'


def lit(game):
    """Are the northern lights in the sky over you now?"""
    from . import weather as WX
    return WX.shown(game) == 'aurora'


def northern(world, x, y):
    """Does this spot of the world map lie in the cold north?"""
    from . import weather as WX
    from .world import WORLD_W
    return WX.climate(world, world.region_of[y * WORLD_W + x]) == 'cold'


def mana_mult(game, sk):
    return CHEAPER if sk.line in LINES and lit(game) else 1.0


# ------------------------------------------------------------------ the glow
def aura_of(o):
    """(colour, strength) of the light round a creature, or None."""
    if getattr(o, 'spirit', False) or (not o.is_npc and o.k in GHOSTLY):
        return (ANGRY, .9) if getattr(o, 'wrath', False) else (GLOW, .55)
    if not o.is_npc and o.tpl.get('family') == 'fiend':
        return FIRE, .4
    return None


def auras(game, m, t):
    """The glow on the tiles round the ghostly and the fiends you can see: {(x, y): (colour, k)}, and the faint wisp
    below a spirit: {(x, y): (sign, colour, k)}."""
    glow, wisps = {}, {}
    for o in m.mons:
        if getattr(o, 'lurk', False) or getattr(o, 'invis', 0) or not game.visible(o.x, o.y):
            continue
        a = aura_of(o)
        if not a:
            continue
        col, power = a
        if getattr(o, 'wrath', False):
            power *= .75 + .3 * math.sin(t * 7.3 + o.id) * math.sin(t * 2.9 + o.id * .7)    # restless
        r = 2.6
        for dy in range(-3, 4):
            for dx in range(-4, 5):
                d = math.hypot(dx * .8, dy)
                if d > r:
                    continue
                k = power * (1 - d / r) ** 1.6
                c = (o.x + dx, o.y + dy)
                if k > glow.get(c, (None, 0))[1]:
                    glow[c] = (col, k)
        if col is not FIRE and power > .3:
            for i in (1, 2):
                wisps[(o.x, o.y + i)] = ('∙' if i == 1 else '·', col, power * (.7 - i * .25))
    return glow, wisps


def flicker(o, bg, t):
    """A spirit's own sign: half there, half not."""
    col, power = aura_of(o)
    if col is FIRE:
        return o.fg
    from .canvas import mix
    f = .55 + .45 * math.sin(t * 9 + o.id * 2.1) * math.sin(t * 3.3 + o.id)
    return mix(bg, mix(CORE, col, .25), .35 + .65 * max(0, f) * min(1, power * 1.4))


def rune_look(game, t, x, y):
    """A rune stone on the world map: grey by day, glowing under the lights."""
    if not lit(game):
        return (128, 132, 138), None
    k = .75 + .25 * math.sin(t * 1.7 + x * .3 + y * .2)
    from .canvas import mix
    return mix((40, 70, 70), RUNE, k), mix((20, 30, 34), GLOW, .35 * k)


# ------------------------------------------------------------------ the barrow spirits
def heard(game):
    """The barrows whose spirit has spoken to you (yours, not the world's)."""
    return game.player.__dict__.setdefault('spirits_heard', set())


def spirit_site(game):
    """The northern barrow whose land you stand on, or None."""
    m = game.map
    if getattr(m, 'place', None) != 'barrow' or getattr(m, 'site', None) is None:
        return None
    site = game.world.sites[m.site]
    return site if northern(game.world, site.x, site.y) else None


def on_barrow(game):
    """On a northern barrow's land: the spirit rises with the lights and fades with them; errands are handed in."""
    m = game.map
    if getattr(m, 'place', None) != 'barrow' or getattr(m, 'site', None) is None:
        return
    site = game.world.sites[m.site]
    hand_in(game, site)
    if not northern(game.world, site.x, site.y):
        return
    sp = next((o for o in m.mons if getattr(o, 'spirit', False)), None)
    if lit(game):
        if not sp and not getattr(site, 'spirit_laid', False):
            rise(game, site, m)
    elif sp and not getattr(sp, 'wrath', False):
        m.mons.remove(sp)
        if game.visible(sp.x, sp.y):
            game.msg('The lights fade from the sky, and the pale shape on the mound fades with them.', 'info')


def _mound(m):
    i = m.t.index(D.DOWN) if D.DOWN in m.t else None
    return (i % m.w, i // m.w) if i is not None else m.centre


def rise(game, site, m):
    from .worldgen import free_around
    from .temples import npc
    from .entities import make_monster
    x, y = _mound(m)
    spots = [c for c in free_around(game, m, x, y, 3) if not game.occupied(m, *c) and m.tile(*c) not in (D.DOWN, D.UP)
             and cheb(c[0], c[1], x, y) >= 2]
    if not spots:
        return None
    c = random.choice(spots)
    if getattr(site, 'wrath', False):
        o = make_monster(game, 'barrow_spirit', c[0], c[1], game.world.danger_at(site.x, site.y) + 3)
        o.awake, o.wrath = True, True
        m.mons.append(o)
        text = 'Over the mound the spirit rises again in the light of the sky, burning cold and bright. It has not forgiven you.'
    else:
        o = npc(game, m, f'The spirit of {site.name}', 'barrow_spirit', SPIRIT_FG, c[0], c[1], ch='G')
        text = 'Over the mound a pale shape rises in the light of the sky: the spirit of the barrow, half there, half not.'
    o.spirit, o.site = True, site.id
    if game.visible(*c) or cheb(c[0], c[1], game.player.x, game.player.y) < 20:
        game.msg(text, 'unique' if not getattr(o, 'wrath', False) else 'bad')
    return o


def wake(game, site, why):
    """Digging into or robbing a northern barrow: the dead wake, their glow brighter and restless."""
    if getattr(site, 'wrath', False) or not northern(game.world, site.x, site.y):
        return False
    site.wrath = True
    for key, m in game.maps.items():
        if getattr(m, 'site', None) == site.id or (getattr(m, 'did', None) is not None and m.did == getattr(site, 'below', None)):
            for o in list(m.mons):
                if getattr(o, 'spirit', False) and o.is_npc:
                    m.mons.remove(o)
                    if m is game.map:
                        rise(game, site, m)
                elif not o.is_npc:
                    o.awake = True
                    if o.k in GHOSTLY or D.MONSTERS[o.k].get('family') == 'undead':
                        o.wrath = True
    game.msg(why, 'bad')
    return True


def on_level(game, m, dg):
    """A level of a barrow whose dead are already awake."""
    site = game.world.sites[dg.site] if getattr(dg, 'site', None) is not None else None
    if site is None or not getattr(site, 'wrath', False):
        return
    for o in m.mons:
        if not o.is_npc:
            o.awake = True
            if o.k in GHOSTLY or D.MONSTERS[o.k].get('family') == 'undead':
                o.wrath = True


def guard_down(game, site):
    """The spirit stands over the way down while the lights are up: asks first. Returns True when it asked."""
    from . import events as EV
    m = game.map
    sp = next((o for o in m.mons if getattr(o, 'spirit', False) and o.is_npc), None)
    if not sp or getattr(m, 'dug_in', False):
        return False
    EV.ask(game, 'spirit_dig', sp.name, '"Go no further, living one. Under this mound we sleep. Dig into it, and we will '
           'not sleep again."', [('Go down all the same', 'go'), ('Leave the dead in peace', 'bye')], site=site.id)
    return True


def r_dig(game, choice, ctx):
    if choice != 'go':
        game.msg('You step back from the way down. The spirit watches you go.', 'info')
        return
    site = game.world.sites[ctx['site']]
    game.map.dug_in = True
    wake(game, site, 'The spirit\'s light flares cold and bright, and from under the mound comes the sound of the dead '
                     'getting up.')
    game.enter_dungeon(site.below, 1, 'up')


def on_kill(game, mon):
    if getattr(mon, 'spirit', False) and getattr(mon, 'site', None) is not None:
        game.world.sites[mon.site].spirit_laid = True
        game.msg('The spirit comes apart like mist in the wind. This barrow will not rise again.', 'info')


# ------------------------------------------------------------------ the errands
GRAVE_WHO = ['my shield-bearer', 'my daughter', 'the singer who made my song', 'my hound-keeper', 'my first wife',
             'the boy who carried my banner', 'my sworn brother']
SWORDS = ['Frostbite', 'Oathkeeper', 'the Grey Tooth', 'Wolfsbane', 'Night-Edge', 'the Long Wake', 'Ice-in-the-Hand']
LINES_SAID = ['"The lights will not hold long. Go."', '"Do what I asked, and we will sleep."',
              '"The cold does not trouble me. The waiting does."', '"I remember the songs. No one sings them now."']


def talk(game, npc):
    from . import missions as MS
    site = game.world.sites[npc.site]
    if site.id in heard(game):
        open_one = any(m.kind == 'spirit' and m.data.get('barrow') == site.id and m.state in ('active', 'turnin')
                       for m in MS.active(game))
        game.say(npc, random.choice(LINES_SAID) if open_one else '"We sleep easier now. Go well, under the lights."')
        return
    if len(MS.active(game)) >= MS.MAX_ACTIVE:
        game.say(npc, f'"You carry too many errands already, living one. Come back lighter." ({MS.MAX_ACTIVE} jobs at most.)')
        return
    m = make_job(game, site)
    if not m:
        game.say(npc, random.choice(LINES_SAID))
        return
    heard(game).add(site.id)
    m.state = 'active'
    game.missions.append(m)
    accept(game, m)
    game.request = ('dialog', npc.name, m.data['said'])
    game.msg(f'Job accepted: {m.title}.', 'gold')


def make_job(game, site):
    from . import missions as MS
    from . import jobs as JB
    w = game.world
    subs = ['grave', 'deed']
    ds = [d for d in w.dungeons.values() if d.relic is None and not d.main and getattr(d, 'site', None) is None
          and getattr(d, 'mine', None) is None and not getattr(d, 'poi', False) and 12 <= cheb(d.x, d.y, site.x, site.y) <= 80]
    if ds:
        subs.append('sword')
    sub = random.choice(subs)
    m = MS.Mission(game.new_id(), 'spirit', None)
    m.faction = None
    lvl = w.danger_at(site.x, site.y) + 2
    d = m.data = dict(sub=sub, barrow=site.id, giver_name=f'the spirit of {JB.the(site.name)}')
    from .engine import dir_name
    if sub == 'sword':
        dg = min(ds, key=lambda d: (d.tag not in ('crypt', 'barrow'), cheb(d.x, d.y, site.x, site.y)))
        sword = random.choice(SWORDS)
        d.update(dungeon=dg.id, did=dg.id, relic=f'{sword}, a barrow-sword')
        m.title = 'A spirit\'s errand: the lost sword'
        m.desc = (f'The spirit of {JB.the(site.name)} wants back its sword, {sword}, lost in {JB.the(dg.name)} to the '
                  f'{dir_name(dg.x - site.x, dg.y - site.y)}. Bring it to the barrow.')
        d['said'] = (f'"My sword, {sword}. It was not laid with me. A thief took it down into {JB.the(dg.name)}, to the '
                     f'{dir_name(dg.x - site.x, dg.y - site.y)}, and died there with it. Bring it to me."')
        m.reward = 30 + (dg.base + dg.depth) * 5
    else:
        spot = JB._spot(game, site.x, site.y, 12, 40)
        if not spot:
            return None
        way = dir_name(spot[0] - site.x, spot[1] - site.y)
        where = JB._region(game, *spot)
        d.update(spot=spot, reach=1)
        if sub == 'grave':
            who = random.choice(GRAVE_WHO)
            d.update(where='an old grave', who=who)
            m.title = 'A spirit\'s errand: an old grave'
            m.desc = (f'Find the grave of the spirit\'s {who.split(" ", 1)[1] if who.startswith("my ") else who} in {where}, '
                      f'to the {way}, and set its stones right. Then go back to the barrow.')
            d['said'] = (f'"They laid {who} far from me, in {where}, to the {way}. The stones have fallen, and the wind '
                         'gets in. Set them right."')
            m.reward = 20 + lvl * 3
        else:
            from . import data as DD
            leader = random.choice(DD.BANDIT_LEADERS)
            d.update(where='the grave robbers', keys=['bandit'] + ['brigand'] * random.randint(2, 3), lvl=lvl, leader=leader,
                     intro=f'{leader} and the grave robbers look up from their fire, shovels beside them.')
            m.title = 'A spirit\'s errand: a deed undone'
            m.desc = (f'Grave robbers led by {leader} dug into a barrow and were never punished. They camp in {where}, to '
                      f'the {way}. Then go back to the barrow.')
            d['said'] = (f'"Men dug into my brother\'s mound and carried him out in pieces. {leader} leads them still. '
                         f'They camp in {where}, to the {way}. It was never paid for."')
            m.reward = 30 + lvl * 4
    m.reward = round(m.reward) * 100
    m.rep = 0
    return m


def accept(game, m):
    from . import missions as MS
    w, d = game.world, m.data
    if d['sub'] == 'sword':
        dg = w.dungeons[d['dungeon']]
        dg.relic = m.id
        game.reveal_place(dg.x, dg.y)
        key = f'{dg.id}:{dg.depth}'
        if key in game.maps:
            MS.place_relic(game, game.maps[key], m)
    elif d.get('spot'):
        game.reveal_place(*d['spot'])


def arrive(game, m):
    """At the place the spirit sent you to."""
    from . import jobs as JB
    d = m.data
    if d['sub'] == 'grave':
        d['reached'] = True
        game.request = ('dialog', 'An old grave', 'Under the snow and the moss you find it: a low mound, its ring of '
                        'stones tipped over by frost. You set them upright one by one. When the last stands, the wind drops.')
        JB._turnin(game, m, 'The grave is whole again.')
        return True
    if d['sub'] == 'deed':
        return JB._arrive_fight(game, m)
    return False


def won(game, m, won_):
    from . import jobs as JB
    if not won_:
        m.data['cool'] = game.turn + 60
        return
    JB._turnin(game, m, 'The grave robbers are dead. What they did is paid for.')


def target_pos(game, m):
    w, d = game.world, m.data
    if m.state == 'turnin':
        site = w.sites[d['barrow']]
        return (site.x, site.y), site.name
    if d['sub'] == 'sword':
        dg = w.dungeons[d['dungeon']]
        from .jobs import the
        return (dg.x, dg.y), the(dg.name)
    return tuple(d['spot']), d['where']


def hand_in(game, site):
    from . import missions as MS
    for m in MS.active(game):
        if m.kind == 'spirit' and m.state == 'turnin' and m.data.get('barrow') == site.id:
            game.msg('You come back to the barrow. Something like a sigh goes over the mound, and the snow on it lies '
                     'still: the dead are at peace.', 'unique')
            game.gain_xp(20 + game.world.danger_at(site.x, site.y) * 6)
            MS.complete(game, m, [])


def on_fail(game, m):
    dg = game.world.dungeons.get(m.data.get('dungeon'))
    if dg is not None and dg.relic == m.id:
        dg.relic = None


def register():
    from . import events as EV
    from . import jobs as JB
    EV.RESOLVERS['spirit_dig'] = r_dig
    JB.LABEL['spirit'] = 'A spirit\'s errand'
    JB.KINDS.add('spirit')
    JB.ARRIVE['spirit'] = arrive
    JB.WON['spirit'] = won


register()
