"""Balance check: a scripted bot plays through all three dungeons.
Run from the project folder:  python tests/bot.py [games_per_class]
"""
import os
import random
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cursed_vale import engine as E, data as D, worldgen as WG  # noqa: E402
from cursed_vale.entities import Item  # noqa: E402

E.save_path = lambda: os.path.join(tempfile.gettempdir(), 'cursed_vale_bot.dat')
ORDER = [('rat', 3), ('mine', 4), ('crypt', 5)]


def score(it):
    s = 0
    if it.dmg:
        s += (it.dmg[0] + it.dmg[1]) * 3
    if it.arm:
        s += it.arm
    return s + len(it.aff) * 8


def manage(g):
    p = g.player
    while p.stat_pts > 0:
        main = {'sorceress': 'ene', 'rogue': 'dex', 'barbarian': 'str'}[p.cls]
        g.add_stat('vit' if p.stat_pts % 2 else main)
    sk = D.SKILLS[p.cls]
    while p.skill_pts > 0:
        c = [k for k in sk if p.lvl >= k.lvl and p.skills.get(k.id, 0) < 10]
        if not c:
            break
        k = min(c, key=lambda k: p.skills.get(k.id, 0))
        g.learn_skill(sk.index(k))
    for it in p.inv:
        if it.k != 'gear' or it.req > p.lvl:
            continue
        cur = g.eq_item(it.slot)
        if not cur or score(it) > score(cur):
            p.eq[it.slot] = it.id
    if len(p.inv) > 20:
        for x in [i for i in p.inv if i.k == 'gear' and not g.is_equipped(i)][:5]:
            p.inv.remove(x)


def potions(g, t):
    return g.count('potion', t) + g.count('potion', 'rejuv')


def town_run(g):
    p = g.player
    if not g.town_portal():
        return
    for it in [i for i in p.inv if i.k == 'gear' and not g.is_equipped(i)]:
        p.gold += 10
        p.inv.remove(it)
    s = g.stats()
    p.life, p.mana = s['max_life'], s['max_mana']
    while p.gold >= 25 and potions(g, 'hp') < 8:
        p.gold -= 25
        g.add_to_inv(Item(g.new_id(), 'potion', 'hp'))
    while p.gold >= 25 and potions(g, 'mp') < 4 and p.cls != 'barbarian':
        p.gold -= 25
        g.add_to_inv(Item(g.new_id(), 'potion', 'mp'))
    if p.gold >= 30 and not g.count('scroll'):
        p.gold -= 30
        g.add_to_inv(Item(g.new_id(), 'scroll', 'tp'))
    m = g.map
    p.x, p.y = m.portal_pos[0], m.portal_pos[1] + 1
    g.try_move(0, -1)
    g.end_turn(1, True)


def step_to(g, tx, ty):
    m, p = g.map, g.player
    d = WG.bfs(m, tx, ty, lambda t: D.TILES[t].walk or D.TILES[t].door)
    best, bd = None, d[p.y * m.w + p.x]
    for dx, dy in WG.D8:
        nx, ny = p.x + dx, p.y + dy
        if m.inb(nx, ny):
            v = d[ny * m.w + nx]
            if v >= 0 and (bd < 0 or v < bd):
                bd, best = v, (dx, dy)
    return best


def act(g, fn):
    used = fn()
    if used and not g.dead:
        g.end_turn(used, True)
    g.events.clear()
    return used


def turn(g):
    p, s = g.player, g.stats()
    if p.life < s['max_life'] * .4 and potions(g, 'hp'):
        return act(g, lambda: g.drink('hp'))
    if p.mana < 12 and potions(g, 'mp') and p.cls == 'sorceress':
        return act(g, lambda: g.drink('mp'))
    hs = g.visible_hostiles()
    if hs:
        adj = [o for o in hs if WG.cheb(o.x, o.y, p.x, p.y) <= 1]
        sk = D.SKILLS[p.cls]
        for i in (2, 1, 0):
            k = sk[i]
            if p.skills.get(k.id, 0) and p.mana >= k.cost:
                if k.id == 'cleave' and len(adj) < 2:
                    continue
                if k.id in ('fan', 'warcry', 'nova') and len([o for o in hs if WG.cheb(o.x, o.y, p.x, p.y) <= 2]) < 2:
                    continue
                if act(g, lambda: g.use_skill(i)):
                    return 1
        if adj:
            o = adj[0]
            return act(g, lambda: g.try_move(o.x - p.x, o.y - p.y))
        o = min(hs, key=lambda o: WG.cheb(o.x, o.y, p.x, p.y))
        st = step_to(g, o.x, o.y)
        if st:
            return act(g, lambda: g.try_move(*st))
        return act(g, lambda: 1)
    if p.life < s['max_life'] * .7:
        g.rest()
        g.events.clear()
        return 1
    st = g.explore_step()
    if st:
        return act(g, lambda: g.try_move(*st))
    return 'done'


def play(cls):
    g = E.Game('Bot', cls)
    for did, depth in ORDER:
        for lv in range(1, depth + 1):
            g.enter_dungeon(did, lv, 'up')
            for _ in range(3000):
                manage(g)
                if potions(g, 'hp') < 2 and g.player.gold >= 100 and not g.visible_hostiles():
                    town_run(g)
                g.request = None
                r = turn(g)
                if g.dead:
                    return f'died {did}{lv} L{g.player.lvl} by {g.cause}', g
                if g.flags.get('lich'):
                    return 'WIN', g
                if r == 'done':
                    m = g.map
                    if lv == depth:
                        boss = next((o for o in m.mons if o.is_boss), None)
                        if boss:
                            st = step_to(g, boss.x, boss.y)
                            if st:
                                act(g, lambda: g.try_move(*st))
                                continue
                        break
                    i2 = m.t.index(D.DOWN)
                    x, y = i2 % m.w, i2 // m.w
                    if (g.player.x, g.player.y) == (x, y):
                        break
                    st = step_to(g, x, y)
                    if not st:
                        break
                    act(g, lambda: g.try_move(*st))
    return ('WIN' if g.flags.get('lich') else 'stuck'), g


if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    for cls in D.CLASS_ORDER:
        res = []
        for _ in range(n):
            out, g = play(cls)
            res.append(f'{out} (lvl {g.player.lvl}, {g.turn} turns, {g.kills} kills)')
        print(cls)
        for r in res:
            print('  ', r)
