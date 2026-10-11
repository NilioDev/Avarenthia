"""Dwarven deepholds: great cities carved into the roots of the mountains, with halls, forges and a throne,
and stairs down into the Deep Roads, the old dwarven tunnels that the dark things took back."""
import random

from . import data as D
from .data import FLOOR, ROCK, DOOR, DOWN, STALL, ANVIL, ALTAR, BED, TABLE, BARREL, PLANK
from .entities import GameMap, make_npc

DEEP_NAMES = ['Khaz Durim', 'Karak Varn', 'Dun Ithrand', 'Barazgund', 'Erebkar', 'Gundholm', 'Zirak Thorn', 'Thrumgard Deep']
THANE_LINES = [
    'Welcome to {hold}, surface-dweller. Mind the forges, and mind your manners.',
    'Our fathers dug these halls when your kind still lived in trees. The Deep Roads below were ours too, once.',
    'The Deep Roads run for a hundred leagues under the mountains. Goblins and worse live there now.',
    "Grolm? A disgrace. He dug where we forbade digging, found something in the dark, and it ate his mind. "
    "We cast him out. Now he holds the old mine near Thornfield, they say.",
    'Bring us grain and ale and timber, and we will pay in good iron. The mountain gives stone, not bread.',
]


def gen_deephold(game, s):
    from .towns import town_names, townsfolk
    from .dress import TORCH, CARPET
    w, h = 72, 26
    m = GameMap(s.map_key, 'town', s.name, w, h, ROCK)
    m.radius, m.sid, m.hid, m.signs = 60, s.id, None, []
    m.underground = True
    m.did, m.depth = getattr(s, 'deep_did', None), 0
    m.deco = bytearray(w * h)
    m.lights = []
    m.ambient = .3
    names = town_names('dwarf')

    def room(x0, y0, x1, y1, t=FLOOR):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                m.set(x, y, t)

    # the great hall with its pillars, and the gate tunnel
    room(8, 9, 63, 16)
    for x in range(12, 62, 6):
        m.set(x, 10, ROCK)
        m.set(x, 15, ROCK)
    room(0, 12, 8, 13)
    m.entry = (0, 12)
    # halls off the great hall: (x0, x1, top?, kind)
    halls = [(10, 20, True, 'inn'), (24, 34, True, 'temple'), (38, 54, True, 'throne'),
             (10, 20, False, 'smithy'), (24, 34, False, 'forge'), (40, 50, False, 'deep'), (54, 62, False, 'homes')]
    centers = {}
    for x0, x1, top, kind in halls:
        y0, y1 = (2, 6) if top else (19, 23)
        room(x0, y0, x1, y1, PLANK if kind in ('inn', 'homes') else FLOOR)
        door_y = 7 if top else 18
        dx = (x0 + x1) // 2
        m.set(dx, door_y, DOOR if kind in ('inn', 'temple', 'homes') else FLOOR)
        m.set(dx, 8 if top else 17, FLOOR)
        centers[kind] = ((x0 + x1) // 2, (y0 + y1) // 2, x0, y0, x1, y1)
    labels = {'inn': 'INN', 'temple': 'TEMPLE', 'throne': 'THRONE', 'smithy': 'SMITHY', 'forge': 'FORGE', 'deep': 'DEEP ROADS'}
    for k, (cx, cy, x0, y0, x1, y1) in centers.items():
        if k in labels:
            ty = 8 if y0 < 9 else 17
            m.signs.append((cx - len(labels[k]) // 2, ty, labels[k]))
    # furniture
    cx, cy, x0, y0, x1, y1 = centers['inn']
    for x in range(x0 + 1, x1, 3):
        m.set(x, y0 + 1, TABLE)
    m.set(x1, y1, BARREL)
    m.set(x0, y1, BARREL)
    cx, cy, x0, y0, x1, y1 = centers['temple']
    m.set(cx, y0, ALTAR)
    cx, cy, x0, y0, x1, y1 = centers['throne']
    for x in range(x0 + 2, x1 - 1):
        for y in range(y0 + 1, y1 + 1):
            m.deco[y * w + x] = CARPET
    m.set(cx, y0, D.STATUE)
    cx, cy, x0, y0, x1, y1 = centers['forge']
    for x in range(x0 + 1, x1, 3):
        m.set(x, y0 + 1, ANVIL)
        m.lights.append((x, y0 + 1, (255, 120, 40), 4))
    cx, cy, x0, y0, x1, y1 = centers['deep']
    m.set(cx, y1, DOWN)
    m.lights.append((cx, y1, (90, 140, 255), 3))
    cx, cy, x0, y0, x1, y1 = centers['homes']
    for x in range(x0, x1 + 1, 2):
        m.set(x, y1, BED)
    for x in range(30, 46, 3):
        m.set(x, 13, STALL)
    # braziers along the great hall and torches in every room
    for x in range(12, 62, 6):
        m.lights.append((x, 10, (255, 170, 80), 5))
        m.deco[10 * w + x] = TORCH
        m.deco[15 * w + x] = TORCH
        m.lights.append((x, 15, (255, 170, 80), 5))
    for k, (cx, cy, x0, y0, x1, y1) in centers.items():
        m.lights.append((cx, cy, (255, 180, 100), 6))
    # the people of the hold
    staff = [('inn', 'inn', 'Innkeeper {n}', '#e0a060'), ('temple', 'healer', 'Brother {n}', '#f4f0e6'),
             ('smithy', 'shop', '{n} the Smith', '#d8d0b0')]
    for k, role, title, col in staff:
        if role == 'shop' and 'shop' not in s.services:
            continue
        cx, cy, x0, y0, x1, y1 = centers[k]
        m.mons.append(make_npc(game, title.format(n=names.pop()), role, col, cx, y0 + (2 if k != 'temple' else 1), True, ch='h'))
    m.mons.append(make_npc(game, f'{names.pop()} the Trader', 'market', '#f2c44a', 36, 14, True, ch='h'))
    cx, cy, x0, y0, x1, y1 = centers['throne']
    thane = make_npc(game, f'Thane {names.pop()}', 'thane', '#ffd860', cx, y0 + 1, True, ch='h')
    m.mons.append(thane)
    for gx, gy in ((9, 11), (9, 14), (cx - 2, y1), (cx + 2, y1)):
        townsfolk(game, m, [(gx, gy)], (gx, gy), names, 'guard', '#b0b8c8', ch='h', role='guard')
    jobs = ['miner', 'miner', 'smith', 'smith', 'brewer', 'mason', 'miner', 'stonecutter']
    hx = centers['homes']
    for j in jobs:
        home = (random.randint(hx[2], hx[4]), random.randint(hx[3], hx[5] - 1))
        work_room = centers['forge'] if j == 'smith' else centers['deep'] if j == 'miner' else centers['inn'] if j == 'brewer' else None
        work = (random.randint(work_room[2], work_room[4]), work_room[3] + 2) if work_room else (random.randint(14, 58), random.choice((11, 12, 13, 14)))
        if m.tile(*work) != FLOOR and m.tile(*work) != PLANK:
            work = (random.randint(14, 58), 12)
        townsfolk(game, m, [home], work, names, j, '#c8a070', ch='h')
    m.set(9, 9, D.SIGNPOST)
    m.signpost = (9, 9)
    return m


def thane_talk(game, npc):
    hold = game.here.name if game.here else 'the hold'
    line = random.choice(THANE_LINES).format(hold=hold)
    game.request = ('dialog', npc.name, f'"{line}"')
