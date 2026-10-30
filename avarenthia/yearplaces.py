"""More places of today (round 30), on the frame of landmarks.py: the land itself and what happened on it, people who
live apart, where the peoples meet, small secrets (poi/volken.md 45-64), and the places of the seasons (65-86)."""
import random

from . import data as D
from .worldgen import cheb
from . import landmarks as LM

PLACE, BUILD, ACT, TALK, CHOOSE, STEP = {}, {}, {}, {}, {}, {}


def place(lay):
    for k, fn in PLACE.items():
        fn(lay)


def daily(game):
    pass
