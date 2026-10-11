"""Coins. Everything is counted in copper: 100 copper make a silver, 100 silver make a gold.
Most folk never hold a gold coin in their life."""
import random

S = 100          # copper in a silver
G = 100 * S      # copper in a gold


def fmt(c, short=False):
    """'2g 15s 40c' (short: '2g15s', dropping copper once there is gold)."""
    c = int(round(c))
    neg = c < 0
    c = abs(c)
    g, rest = divmod(c, G)
    s, cc = divmod(rest, S)
    parts = []
    if g:
        parts.append(f'{g}g')
    if s:
        parts.append(f'{s}s')
    if cc and not (short and g):
        parts.append(f'{cc}c')
    out = ('' if short else ' ').join(parts) or '0c'
    return ('-' if neg else '') + out


def purse(lvl, mult=1.0):
    """A handful of coins carried by someone of this level."""
    return max(1, int(random.uniform(.4, 1.6) * (30 + lvl * 25) * mult))
