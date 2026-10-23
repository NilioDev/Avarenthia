"""Balance check: a scripted bot plays through the story dungeons and the evil lairs.
Run from the project folder:  python tests/bot.py [games_per_class]
"""
import os
import random
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from avarenthia import engine as E, data as D, worldgen as WG  # noqa: E402
from avarenthia.entities import Item  # noqa: E402
from avarenthia import skills as SK  # noqa: E402

E.save_path = lambda: os.path.join(tempfile.gettempdir(), 'avarenthia_bot.dat')
ORDER = [('rat', 3), ('mine', 4)]   # followed by the lairs of this world's great evils


def score(it):
    s = 0
    if it.dmg:
        s += (it.dmg[0] + it.dmg[1]) * 3
    if it.arm:
        s += it.arm
    return s + len(it.aff) * 8


def manage(g):
    from avarenthia import skills as SK
    p = g.player
    while p.stat_pts > 0:
        g.add_stat('vit' if p.stat_pts % 2 else 'str')
    # the bot reads every tome it finds, and pretends it found the skills its disciplines allow
    # a Pyromancer, and a Sunpriest once Fire reaches rank 20
    p.classes = ['fire', 'restoration'] if p.disc['fire'][0] >= 20 else ['fire']
    for it in [i for i in p.inv if i.k == 'tome' and SK.SKILLS[i.t].line in p.classes]:
        g.read_tome(it)
    for sk in SK.SKILL_LIST:
        if sk.line in p.classes and p.disc[sk.line][0] >= sk.unlock and sk.id not in p.known \
                and (sk.unlock == 0 or p.lvl >= 4):
            p.known.append(sk.id)
    for it in p.inv:
        if it.k == 'gear' and not it.identified and not it.cursed:
            it.ided = True
    # keep the strongest known sword, fire and restoration skills on the bar
    want = [k for k in p.known if SK.SKILLS[k].line in p.classes and not SK.SKILLS[k].guild]
    want.sort(key=lambda k: -SK.SKILLS[k].unlock)
    p.bar = [None, None] + (want + [None] * 3)[:3] + [None]
    for it in p.inv:
        if it.k != 'gear' or it.req > p.lvl:
            continue
        if it.slot == 'weapon' and SK.WEAPON_LINE.get(it.base) != 'swords':
            continue
        cur = g.eq_item(g.slot_for(it))
        if not cur or score(it) > score(cur):
            p.eq[g.slot_for(it)] = it.id
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
    while p.gold >= 25 and potions(g, 'mp') < 3:
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
    if p.mana < 6 and potions(g, 'mp'):
        return act(g, lambda: g.drink('mp'))
    hs = g.visible_hostiles()
    if hs:
        adj = [o for o in hs if WG.cheb(o.x, o.y, p.x, p.y) <= 1]
        from avarenthia import skills as SK
        from avarenthia import classes as CL
        for i in range(6):
            sid = CL.slot_skill(g, i)
            if not sid:
                continue
            k = SK.SKILLS[sid]
            if k.mode == 'self' and k.heal and p.life > s['max_life'] * .6:
                continue
            if k.mode in ('adjacent',) and len(adj) < 2:
                continue
            if not SK.can_pay(g, k) or p.cooldowns.get(sid):
                continue
            g.msg_quiet = True
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
    g = E.Game('Bot', True)
    order = ORDER + [(e.did, g.world.dungeons[e.did].depth) for e in g.world.evils]
    for did, depth in order:
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
                if g.flags.get('saved'):
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
    return ('WIN' if g.flags.get('saved') else 'stuck'), g


if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    for cls in ['classless']:
        res = []
        for _ in range(n):
            out, g = play(cls)
            res.append(f'{out} (lvl {g.player.lvl}, {g.turn} turns, {g.kills} kills)')
        print(cls)
        for r in res:
            print('  ', r)
