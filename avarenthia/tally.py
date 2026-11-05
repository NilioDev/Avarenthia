"""The tally (round 42, "The belt and the tally" in docs/plan.md): the counters of a life, on the player (`p.tally`),
and the page "The tally of <name>" in four blocks, a ledger with dotted leaders. Opened from the menu (Esc, Hero)
and shown after the win and the death screens."""
from .money import fmt


def state(game):
    return game.player.__dict__.setdefault('tally', {})


def add(game, key, n=1):
    if getattr(game, 'player', None) is None:
        return
    t = state(game)
    t[key] = t.get(key, 0) + n


def most(game, key, n):
    """Keep the highest value seen."""
    if getattr(game, 'player', None) is None:
        return
    t = state(game)
    if n > t.get(key, 0):
        t[key] = n


def get(game, key, default=0):
    return state(game).get(key, default)


def kill(game, mon):
    t = state(game)
    t['kills'] = t.get('kills', 0) + 1
    slain = t.setdefault('slain', {})
    slain[mon.name] = slain.get(mon.name, 0) + 1
    if getattr(mon, 'is_boss', False):
        t['bosses'] = t.get('bosses', 0) + 1


def hurt(game, dmg, life_after, max_life):
    """A blow taken: the hardest, and the closest call (the least life you lived through, as a share)."""
    t = state(game)
    most(game, 'hit_taken', dmg)
    if life_after > 0:
        share = round(life_after * 100 / max(1, max_life))
        if share < t.get('closest', 101):
            t['closest'] = share
            t['closest_life'] = life_after


def dealt(game, dmg):
    most(game, 'hit_dealt', round(dmg))


def sale(game, got, kind):
    """Coin from a sale: trade goods or loot."""
    add(game, 'earn_' + kind, got)
    most(game, 'best_sale', got)


def every_turn(game):
    most(game, 'richest', game.player.gold)


def blocks(game):
    """The four blocks: (title, [(label, value)])."""
    t = state(game)
    p = game.player
    slain = t.get('slain', {})
    top = max(slain.items(), key=lambda kv: (kv[1], kv[0])) if slain else None
    road = [('Days', game.day), ('Turns', game.turn), ('Steps', t.get('steps', 0)),
            ('Leagues on land', t.get('leagues_land', 0)), ('Leagues at sea', t.get('leagues_sea', 0)),
            ('Places found', len(game.__dict__.get('visited', ()))), ('Deepest floor', t.get('deepest', 0)),
            ('Nights in a bed', t.get('bed_nights', 0)), ('Nights under the sky', t.get('sky_nights', 0))]
    fights = [('Foes slain', t.get('kills', 0)), ('Slain most', f'{top[0]} ({top[1]})' if top else 'none'),
              ('Bosses felled', t.get('bosses', 0)), ('Times you fell', getattr(p, 'deaths', 0)),
              ('Closest call', f"{t['closest_life']} life ({t['closest']}%)" if 'closest' in t else 'none'),
              ('Hardest blow dealt', t.get('hit_dealt', 0)), ('Hardest blow taken', t.get('hit_taken', 0)),
              ('Potions drunk', t.get('potions', 0)), ('Hirelings lost', t.get('hirelings_lost', 0))]
    coin = [('Earned from jobs', fmt(t.get('earn_jobs', 0))), ('Earned from trade', fmt(t.get('earn_trade', 0))),
            ('Earned from loot', fmt(t.get('earn_loot', 0))), ('Spent on beds', fmt(t.get('spent_beds', 0))),
            ('Spent on repairs', fmt(t.get('spent_repairs', 0))), ('Spent on wages', fmt(t.get('spent_wages', 0))),
            ('Spent at the temple', fmt(t.get('spent_temple', 0))), ('Best single sale', fmt(t.get('best_sale', 0))),
            ('Richest you were', fmt(max(t.get('richest', 0), p.gold)))]
    life = [('Jobs done', t.get('jobs', 0)), ('Fish caught', t.get('fish', 0)), ('Meals eaten', t.get('meals', 0)),
            ('Brews made', t.get('brews', 0)), ('Ore dug', t.get('ore', 0)), ('Books read', t.get('books', 0)),
            ('Rumours heard', t.get('rumours', 0)), ('Feasts', t.get('feasts', 0))]
    return [('The Road', road), ('Fights', fights), ('Coin', coin), ('A Life', life)]


def leader(label, value, width):
    v = str(value)
    dots = max(2, width - len(label) - len(v) - 2)
    return f'{label} {"." * dots} {v}'
