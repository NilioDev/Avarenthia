"""Morvenna the Undying: an unseen enemy whose shadow grows as you grow.

Her strength rises with your level and with time. The blight spreads from her crypt over the land
(more danger, undead day and night), she whispers to you at night, the dead rise near villages in
her shadow, and from a certain point she sends hunters after you. It all ends when she is destroyed."""
import math
import random

from . import data as D
from .worldgen import cheb

STAGES = ['Dreaming', 'Stirring', 'Restless', 'Watching', 'Searching', 'Hunting', 'Hunting', 'Wrathful', 'Wrathful',
          'Ascendant', 'Ascendant']
WHISPERS = [
    'A cold voice brushes your thoughts: "I see you, little one."',
    'You hear a woman laughing, far away. No one else seems to hear it.',
    'For a moment every shadow points the same way.',
    'Frost creeps over your boots, though the night is mild.',
    '"Come to me," whispers a voice like dry leaves. "Come, and rest."',
    'A crow lands nearby and watches you with pale, dead eyes.',
    'You dream of a crypt, and of a throne, and of a crown of bone.',
    'The wind carries the smell of turned earth.',
    '"Every one you kill, I will raise again."',
    'Your shadow moves a heartbeat after you do.',
]
HUNT_LEADERS = ["Herald of Morvenna", "Morvenna's Gravecaller", 'The Pale Rider', 'The Bone Shepherd',
                'Widow of the Crypt', 'The Hollow Knight']
HUNT_FG = (196, 134, 255)


def strength(game):
    if game.flags.get('lich'):
        return 0
    return min(10, max(0, (game.player.lvl - 1) // 2) + (game.day - 1) // 20)


def stage(game):
    return STAGES[min(len(STAGES) - 1, getattr(game.world, 'curse_lvl', 0))]


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


def compute_blight(game):
    w = game.world
    om = game.maps['over']
    lvl = w.curse_lvl
    crypt = w.dungeons['crypt']
    r = 0 if game.flags.get('lich') else 6 + lvl * 4
    w.blight_r = r
    bl = bytearray(om.w * om.h)
    if r:
        for y in range(max(0, crypt.y - r * 2), min(om.h, crypt.y + r * 2 + 1)):
            for x in range(max(0, crypt.x - r * 2), min(om.w, crypt.x + r * 2 + 1)):
                d = math.hypot(x - crypt.x, (y - crypt.y) * 1.4)
                if d < r * (.6 + .8 * _smooth_noise(x, y)) and om.t[y * om.w + x] != D.WATER:
                    bl[y * om.w + x] = 1
    w.blight = bl


def blighted(game, x, y):
    bl = getattr(game.world, 'blight', None)
    return bool(bl and bl[y * game.maps['over'].w + x])


def update(game, announce=True):
    w = game.world
    old = getattr(w, 'curse_lvl', 0)
    new = strength(game)
    w.curse_lvl = new
    if new != old or getattr(w, 'blight', None) is None:
        compute_blight(game)
    if announce and new > old:
        game.msg(random.choice([
            'Far to the ' + game.dir_to('crypt') + ', something old turns in its sleep. The blight spreads.',
            'The birds fall silent. Morvenna grows stronger, and the blight creeps further over the land.',
            'A chill runs through the vale. Morvenna knows your name now.' if new >= 3 else
            'You shiver for no reason. The dead grow restless.',
        ]), 'unique')
        if new == 4:
            game.msg('Morvenna has sent her servants to hunt you. Watch the horizon.', 'bad')


def whisper(game):
    """Night-time voices, more often the stronger she is."""
    w = game.world
    lvl = getattr(w, 'curse_lvl', 0)
    if not lvl or game.flags.get('lich'):
        return
    from .towns import is_night
    p = game.player
    near = game.cur == 'over' and blighted(game, p.x, p.y)
    if not (is_night(game) or near):
        return
    if random.random() < lvl * .0012 + (.004 if near else 0):
        game.msg(random.choice(WHISPERS), 'unique')


def daily(game):
    update(game)
    w = game.world
    lvl = w.curse_lvl
    if not lvl:
        return
    # the dead rise near villages in her shadow
    for s in w.settlements:
        if s.event is None and blighted(game, s.x, s.y) and random.random() < .08 + lvl * .02:
            ev = D.EVENTS['undead']
            s.event = ('undead', random.randint(4, 7))
            for g in (ev['good'], ev.get('also')):
                s.market[g][1] = ev['target']
                s.market[g][0] = min(s.market[g][0], ev['target'] * 2)
            game.msg('News: ' + ev['text'].format(town=s.name), 'bad')
    # her hunters
    hunts = [x for x in w.wanderers if x.kind == 'hunt']
    if lvl >= 4 and len(hunts) < 1 + (lvl - 4) // 2 and random.random() < .2 + lvl * .04:
        spawn_hunt(game)


def spawn_hunt(game):
    from .wanderers import make_group, wanderer_at, passable
    w = game.world
    om = game.maps['over']
    p = game.player
    ox, oy = (p.x, p.y) if game.cur == 'over' else game.over_pos
    for _ in range(300):
        a = random.random() * math.tau
        d = random.randint(24, 40)
        x, y = int(ox + math.cos(a) * d), int(oy + math.sin(a) * d * .6)
        if not om.inb(x, y) or not passable(game, x, y, True) or wanderer_at(game, x, y):
            continue
        if any(cheb(x, y, s.x, s.y) < 6 for s in w.settlements):
            continue
        lvl = p.lvl + 1
        pool = [k for k in ('skeleton', 'zombie', 'skarcher', 'ghost', 'wraith') if D.MONSTERS[k]['min_l'] <= lvl + 2] or ['skeleton']
        keys = [random.choice(pool) for _ in range(random.randint(3, 4 + game.world.curse_lvl // 3))]
        leader = random.choice(HUNT_LEADERS)
        wd = make_group(game, 'monsters', x, y, lvl, keys, 2, leader)
        wd.kind = 'hunt'
        wd.fg = HUNT_FG
        wd.ch = 'W'
        wd.name = f'{leader} and the restless dead'
        wd.speed = 12
        wd.warned = False
        w.wanderers.append(wd)
        return wd
    return None


def sense(game):
    """Let the player feel a hunter closing in."""
    if game.cur != 'over':
        return
    p = game.player
    for wd in game.world.wanderers:
        if wd.kind == 'hunt' and not getattr(wd, 'warned', True) and cheb(wd.x, wd.y, p.x, p.y) <= 16:
            wd.warned = True
            game.msg('The air turns cold. You feel eyes upon you: something is hunting you.', 'bad')


def describe(game):
    w = game.world
    lvl = getattr(w, 'curse_lvl', 0)
    if game.flags.get('lich'):
        return 'Morvenna is destroyed. The curse is broken.'
    return {0: 'Morvenna dreams in her crypt. The blight is small, for now.',
            1: 'Morvenna stirs. The dead grow restless.',
            2: 'The blight spreads. Her whispers reach the living.',
            3: 'She is watching you.',
            4: 'She is searching for you. The dead rise near the villages in her shadow.'}.get(
        lvl, 'Morvenna hunts you. Her servants roam the land, and the blight swallows the vale.')
