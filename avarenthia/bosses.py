"""Boss fights, the kit (round 15): bosses fight like a turn-based soulslike.

A great blow is announced in the log and the ground it will strike turns dark red; a blow that loads for two or three
turns shows a number that counts down on every tile (red: step out; purple: it can be broken; gold: stand in it).
What is marked is always true, and every marked blow leaves a free tile you can reach in time (checked when it loads).
Small blows come unmarked, as before.

A boss fights in a rhythm drawn from a deck (Gloomhaven): each phase has a beat of roles (k small, V set-up, G great,
Z heaviest, B move, O summon) and a few cards per role; one card is drawn per beat, an empty pile is shuffled again,
and about one beat in five the rhythm breaks. At its thresholds (two thirds and one third, or one half) a blow stops,
and the boss spends its next turn on the phase's trick; a critical hit while it is spent or staggered breaks through.
After its heaviest blow it stands spent; breaks and hits with its weakness fill three dots and stagger it. Its
resolve shrugs off the first two holds. Helpers come with a job (warder, mender, channeler, guard, swarm). End
bosses wait behind a veil of mist; the room shuts at the first blow, with one hard way out, a rotten wall. Fled from,
a boss heals and makes ready against you, up to four times.

State: `mon.bs` (a kit boss), `mon.cast` (any boss loading a marked blow), `m.arena` (the boss's room)."""
import random

from . import data as D
from .worldgen import cheb, free_around

RED, PURPLE, GOLDN = (255, 104, 80), (206, 132, 255), (255, 214, 90)
MARK_BG, MARK_HOT, MARK_GOLD = (88, 18, 16), (140, 30, 22), (78, 62, 14)
ROMAN = ('I', 'II', 'III', 'IV')
JOBS = {'warder': 'warding', 'mender': 'mending', 'channeler': 'channelling', 'guard': 'guarding',
        'swarm': 'swarming', 'bearer': 'bearing'}
D8 = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1))
RESOLVE = 2
MAX_PREP = 4

# ------------------------------------------------------------------ the moves
# role: k small, V set-up, G great, Z heaviest, B move, O summon. A shaped move loads `load` turns and strikes the
# marked cells with `power` (a share of your full life at the boss's level). brk: it can be broken (default: a load
# of two or more). fx: what it does besides the blow. say: the announcement; hit: when it strikes you.
MOVES = {
    'jab': dict(role='k', name='Spear Jab', kind='melee'),
    'claw': dict(role='k', name='Claw', kind='melee'),
    'touch': dict(role='k', name='Grave Touch', kind='melee'),
    'bone_spear': dict(role='k', name='Bone Spear', kind='bolt'),
    'snare_line': dict(role='V', name='Snare Line', kind='snares',
                       say='{name} scatters snares across the floor, three in a row.'),
    'bone_prison': dict(role='V', name='Bone Prison', kind='prison',
                        say='{name} points at you. Bones burst from the floor all round you!'),
    'grave_mist': dict(role='V', name='Grave Mist', shape='circle', r=2, at='aim', load=1, power=.12, elem='cold',
                       fx=dict(sick=10), say='{name} breathes out a grey mist that crawls along the floor...',
                       hit='The grave mist sinks into you. Your wounds will not close.'),
    'wing_buffet': dict(role='V', name='Wing Buffet', shape='cone', len=3, load=1, power=.1, fx=dict(push=3),
                        say='{name} spreads {his} wings wide...', hit='A blast from the great wings throws you back!'),
    'coin_toss': dict(role='G', name='Coin Toss', shape='circle', r=1, at='aim', load=1, brk=False, power=.26, fx=dict(coins=3),
                      say='{name} digs into {his} hoard and swings back a fistful of coins and stones...',
                      hit='Coins and stones crack against your head!'),
    'shield_rush': dict(role='G', name='Shield Rush', shape='line', len=4, load=1, power=.3, fx=dict(rush=1, push=2),
                        say='{name} lowers {his} pot-lid shield and paws the ground...',
                        hit='{name} slams into you behind {his} shield!'),
    'frost_nova': dict(role='G', name='Frost Nova', shape='ring', r=2, load=1, power=.3, elem='cold', fx=dict(hold=2),
                       say='Frost spreads from {name} across the floor...', hit='The frost bursts up and locks you in ice!'),
    'corpse_burst': dict(role='G', name='Corpse Burst', shape='corpses', load=1, power=.32, elem='cold',
                         say='The dead on the floor swell and split...', hit='A corpse bursts beside you in a spray of bone!'),
    'breath': dict(role='G', name='Breath of Fire', shape='cone', len=7, load=1, power=.34, elem='fire', fx=dict(burn=5),
                   say='{name} rears back. Light glows deep in {his} throat...', hit='Fire pours over you!'),
    'breath_follow': dict(role='G', name='Breath of Fire', shape='cone', len=7, load=2, follow=True, brk=False,
                          power=.34, elem='fire', fx=dict(burn=5),
                          say='{name} rears back and turns {his} head after you, fire glowing in {his} throat...',
                          hit='Fire pours over you!'),
    'tail_sweep': dict(role='G', name='Tail Sweep', shape='tail', load=1, power=.3, fx=dict(push=1),
                       say='{name} coils {his} tail...', hit='The great tail sweeps you off your feet!'),
    'dive': dict(role='G', name='Dive', shape='circle', r=1, at='aim', load=2, follow=True, brk=False, power=.36,
                 fx=dict(land=1), say='', hit='{name} drops out of the dark on top of you!'),
    'mark_doom': dict(role='Z', name='Mark of Doom', shape='mark', load=3, power=.5,
                      say='{name} draws a sign in the air, and it burns cold above {aim}. Get out of {his} sight!',
                      hit='The Mark of Doom falls on you!'),
    'blizzard': dict(role='Z', name='Blizzard', shape='room', load=3, power=.45, elem='cold', fx=dict(slow=3),
                     say='{name} rises from the floor. Snow begins to whirl through the tomb. Find cover!',
                     hit='The blizzard tears at you!'),
    'inferno': dict(role='Z', name='Inferno', shape='room', load=3, power=.52, elem='fire', fx=dict(burn=8, pillar=1),
                    say='{name} draws in a breath that empties the cave of air. Get behind the stone!',
                    hit='The inferno rolls over you!'),
    'call_kobolds': dict(role='O', name='Call', kind='call', helpers=(('kobold', 'guard'), ('kob_sorcerer', 'mender')),
                         say='{name} shrieks for help. Kobolds come running!'),
    'raise_dead': dict(role='O', name='Raise Dead', kind='raise', n=3,
                       say='{name} lifts {his} hands. The dead on the floor get up.'),
    'call_drakes': dict(role='O', name='Call Drakes', kind='call', helpers=(('drake', 'channeler'), ('drake', 'guard')),
                        say='{name} roars, and drakes come gliding out of the dark.'),
    'take_wing': dict(role='B', name='Take Wing', kind='wing',
                      say='{name} beats {his} great wings and rises into the dark above you!'),
    # the moves of the other bosses, now announced (round 16 gives them their own kits)
    'nova': dict(role='G', name='Nova', shape='ring', r=2, load=1, power=.25),
    'leap': dict(role='G', name='Leap', shape='circle', r=1, at='aim', load=1, power=.3, fx=dict(land=1)),
}

from .bossmoves import LIBRARY as _LIBRARY  # noqa: E402
from . import bossmoves as BM  # noqa: E402

MOVES.update(_LIBRARY)

STANCE = {'R': '{He} settles, waiting for you.', 'k': '{He} watches your hands.', 'V': '{His} eyes go to the floor round your feet.',
          'G': '{He} draws {himself} up.', 'Z': 'Something gathers in {him}, slowly.', 'B': '{He} sets {his} feet.',
          'O': '{His} eyes go to the dark at the edges.'}

# ------------------------------------------------------------------ the kits
KITS = {
    'snagtooth': dict(weak=('cold',), things='hoard', phases=[
        dict(beat='kkG', cards=dict(k=['jab'], G=['coin_toss'])),
        dict(at=.5, beat='kVGO', cards=dict(k=['jab'], V=['snare_line'], G=['shield_rush', 'coin_toss'],
                                            O=['call_kobolds']), trick='call',
             say='{name} bangs {his} pot-lid shield and shrieks. The kobolds answer from the dark!')]),
    'lich': dict(weak=('fire',), things='tomb', phases=[
        dict(beat='kVGk', cards=dict(k=['bone_spear', 'bone_spear', 'touch'], V=['bone_prison'],
                                     G=['grave_mist', 'frost_nova'])),
        dict(at=.66, beat='kOGkZ', cards=dict(k=['bone_spear', 'touch'], O=['raise_dead'],
                                              G=['corpse_burst', 'frost_nova'], Z=['mark_doom']), trick='rise',
             say='{name} lifts {his} arms. All round the tomb the dead begin to stir.'),
        dict(at=.33, beat='kVGkZ', cards=dict(k=['bone_spear', 'touch'], V=['bone_prison', 'grave_mist'],
                                              G=['frost_nova', 'corpse_burst'], Z=['blizzard']), trick='dark',
             say='The grave-lights gutter and go out. {name} is only half there now, a cold shape in the dark.')]),
    'dragon': dict(weak=('cold',), things='lair', phases=[
        dict(beat='kGkVG', cards=dict(k=['claw'], G=['breath', 'tail_sweep'], V=['wing_buffet'])),
        dict(at=.66, beat='kGOkB', cards=dict(k=['claw'], G=['breath_follow', 'tail_sweep'], O=['call_drakes'],
                                              B=['take_wing']), trick='roar',
             say='{name} roars until the cave shakes. Far off in the dark, drakes answer.'),
        dict(at=.33, beat='kGkZ', cards=dict(k=['claw'], G=['breath_follow', 'tail_sweep'], Z=['inferno']),
             trick='burn', say='Fire runs in the cracks of the floor, and stone falls from the roof.')]),
    # ---- the other fixed bosses (round 16)
    'ratking': dict(weak=('fire',), things='holes', phases=[
        dict(beat='kkOG', cards=dict(k=['bite'], O=['rats'], G=['tail_lash'])),
        dict(at=.66, beat='kVGkO', cards=dict(k=['bite'], V=['plague_cloud'], G=['gnaw', 'tail_lash'], O=['rats']),
             say='{name} shrieks, and the whole sewer shrieks with {him}.'),
        dict(at=.33, beat='kGkZ', cards=dict(k=['bite'], G=['gnaw', 'tail_lash'], Z=['knot_split']), trick='water',
             say='Somewhere a sluice gives. Filthy water comes pouring into the sewer and begins to rise.')]),
    'grolm': dict(weak=('lightning',), things='props', phases=[
        dict(beat='kGkB', cards=dict(k=['pick'], G=['smash'], B=['burrow'])),
        dict(at=.66, beat='kVGkG', cards=dict(k=['pick'], V=['kick_prop'], G=['undermine', 'smash']),
             say='{name} spits and grins at the props that hold up the roof.'),
        dict(at=.33, beat='kGkZ', cards=dict(k=['pick'], G=['undermine', 'smash'], Z=['earthshaker']), trick='ceiling',
             say='The roof groans. Dust and stones begin to fall. Keep near a prop!')]),
    'broodmother': dict(weak=('fire',), things='nest', phases=[
        dict(beat='kVGk', cards=dict(k=['bite'], V=['web_spray'], G=['venom_spit', 'pounce'])),
        dict(at=.66, beat='kOGkB', cards=dict(k=['bite'], O=['egg_clutch', 'call_spiders'], G=['pounce', 'venom_spit'],
                                              B=['drop_above']), trick='webs',
             say='{name} shakes the whole web. Threads fall across the floor everywhere.'),
        dict(at=.33, beat='kVGkZ', cards=dict(k=['bite'], V=['web_spray'], G=['venom_spit', 'pounce'], Z=['cocoon']),
             say='{name} rears up over her nest, hissing.')]),
    'warlord': dict(weak=('lightning',), phases=[
        dict(beat='kGkGO', cards=dict(k=['strike'], G=['cleave', 'charge'], O=['call_band', 'war_cry'])),
        dict(at=.66, beat='kGOkZ', cards=dict(k=['strike'], G=['cleave', 'charge'], O=['war_cry', 'call_band'],
                                              Z=['earthshaker']), trick='banner',
             say='{name} bellows. A bearer runs up with his war banner, and the band takes heart.'),
        dict(at=.33, beat='kGkZ', cards=dict(k=['strike'], G=['cleave', 'smash'], Z=['executioner']), trick='duel',
             say='{name} waves his guard back. This is between you and him now.')]),
    'drowned_king': dict(weak=('lightning',), things='pool', phases=[
        dict(beat='kGOk', cards=dict(k=['brine_lance'], G=['tidal_wave'], O=['call_drowned'])),
        dict(at=.66, beat='kVGkO', cards=dict(k=['brine_lance'], V=['drag_under'], G=['whirlpool', 'tidal_wave'],
                                              O=['call_drowned']), trick='water',
             say='{name} lifts {his} arms, and the water rises with them.'),
        dict(at=.33, beat='kGkVZ', cards=dict(k=['brine_lance'], G=['whirlpool', 'tidal_wave'], V=['drag_under'],
                                              Z=['deep_calls']), trick='water',
             say='The water rises again, black and cold. Only the ledges and the chains stand above it.')]),
    'cinder_lord': dict(weak=('cold',), phases=[
        dict(beat='kGkO', cards=dict(k=['firebolt'], G=['fireball', 'burning_lines'], O=['call_hounds'])),
        dict(at=.66, beat='kGkVZ', cards=dict(k=['firebolt'], G=['burning_lines', 'fireball'], V=['ring_of_fire'],
                                              Z=['meteor']),
             say='{name} draws fire out of the gate behind {him}. The iron floor glows.'),
        dict(at=.33, beat='kGkZ', cards=dict(k=['firebolt'], G=['burning_lines'], Z=['meteor', 'hellfire']), trick='burn',
             say='The floor of the hall cracks and fire runs in the cracks.')]),
    # ---- the theme bosses at the bottom of their nests (two phases)
    'matriarch': dict(weak=('fire',), theme=True, things='nest', phases=[
        dict(beat='kVGk', cards=dict(k=['bite'], V=['web_spray'], G=['pounce', 'venom_spit'])),
        dict(at=.5, beat='kOGkV', cards=dict(k=['bite'], O=['egg_clutch'], G=['pounce'], V=['web_spray']), trick='webs',
             say='{name} shakes her web. Threads come down all over the floor.')]),
    'ant_queen': dict(weak=('fire',), theme=True, phases=[
        dict(beat='kOGk', cards=dict(k=['bite'], O=['call_ants'], G=['acid_spray'])),
        dict(at=.5, beat='kOGkG', cards=dict(k=['bite'], O=['tunnel'], G=['acid_spray']),
             say='{name} beats the floor with her legs. Far below, the nest answers.')]),
    'goblin_king': dict(weak=('cold',), theme=True, hide=True, phases=[
        dict(beat='kGOk', cards=dict(k=['strike'], G=['bomb_volley'], O=['call_goblins'])),
        dict(at=.5, beat='kGBkO', cards=dict(k=['strike'], G=['bomb_volley'], B=['smoke_bomb'], O=['call_goblins']),
             say='{name} screeches for more bombs, and keeps his goblins between you and him.')]),
    'viper_coil': dict(weak=('cold',), theme=True, phases=[
        dict(beat='kVGk', cards=dict(k=['bite'], V=['coil'], G=['venom_spit'])),
        dict(at=.5, beat='kRGkV', cards=dict(k=['bite'], R=['shed_skin'], G=['venom_spit'], V=['coil']),
             say='{name} hisses. {His} scales split down the back.')]),
    'ghast_lord': dict(weak=('fire',), theme=True, phases=[
        dict(beat='kVGk', cards=dict(k=['strike'], V=['stench'], G=['paralyse_claw'])),
        dict(at=.5, beat='kOGkZ', cards=dict(k=['strike'], O=['raise_dead', 'call_ghouls'], G=['paralyse_claw'],
                                             Z=['corpse_burst']),
             say='{name} howls for {his} pack. The dead on the floor twitch.')]),
    'staring_dark': dict(weak=('lightning',), theme=True, things='pillars', phases=[
        dict(beat='kVGk', cards=dict(k=['shadow_bolt'], V=['dread', 'darkness'], G=['gaze_ray'])),
        dict(at=.5, beat='kGkZ', cards=dict(k=['shadow_bolt'], G=['gaze_ray', 'life_drain'], Z=['mark_doom']), trick='dark',
             say='The great eye closes, and the room goes dark round it.')]),
    'deep_mother': dict(weak=('fire',), theme=True, phases=[
        dict(beat='kVGk', cards=dict(k=['shadow_bolt'], V=['babble', 'hex'], G=['morraks_hand'])),
        dict(at=.5, beat='kOGkV', cards=dict(k=['shadow_bolt'], O=['call_spawn'], G=['morraks_hand', 'life_drain'],
                                             V=['babble']),
             say='{name} swells, and things begin to crawl out of {his} folds.')]),
    'wasp_queen': dict(weak=('cold',), theme=True, phases=[
        dict(beat='kOGB', cards=dict(k=['bite'], O=['call_wasps'], G=['venom_spit'], B=['sting_dive'])),
        dict(at=.5, beat='kOBkG', cards=dict(k=['bite'], O=['call_wasps'], B=['sting_dive'], G=['venom_spit']),
             say='{name} buzzes so loud the air shakes. The swarm thickens.')]),
    # ---- the Varnish guardians in their hidden deeps (two phases)
    'iron_sentinel': dict(weak=('lightning',), phases=[
        dict(beat='kGkR', cards=dict(k=['strike'], G=['smash', 'charge'], R=['shield_wall'])),
        dict(at=.5, beat='kGkZ', cards=dict(k=['strike'], G=['smash'], Z=['earthshaker']),
             say='Something grinds inside {name}. It moves faster now.')]),
    'bound_gale': dict(weak=('cold',), things='pillars', phases=[
        dict(beat='kVGk', cards=dict(k=['spark'], V=['gust', 'static_field'], G=['chain_lightning', 'ball_lightning'])),
        dict(at=.5, beat='kGVkZ', cards=dict(k=['spark'], G=['ball_lightning', 'chain_lightning'], V=['gust', 'static_field'],
                                             Z=['tempest']), trick='wind',
             say='{name} howls round the room. The wind will not stop now.')]),
    'standing_legate': dict(weak=('fire',), phases=[
        dict(beat='kGOk', cards=dict(k=['strike'], G=['cleave'], O=['call_bound'])),
        dict(at=.5, beat='kGOkZ', cards=dict(k=['strike'], G=['life_drain', 'cleave'], O=['war_cry'], Z=['army_dead']),
             say='{name} raises the old standard. The bound dead stand straighter.')]),
    'hollow_echo': dict(weak=('fire',), things='pillars', phases=[
        dict(beat='kVGk', cards=dict(k=['shadow_bolt'], V=['dread', 'darkness'], G=['wail'])),
        dict(at=.5, beat='kVGkZ', cards=dict(k=['shadow_bolt'], V=['dread'], G=['wail'], Z=['mark_doom']), trick='fog',
             say='{name} comes apart into many voices. A grey fog fills the hall.')]),
    'chained_star': dict(weak=('cold',), phases=[
        dict(beat='kGkV', cards=dict(k=['arcane_bolt'], G=['starfall', 'morraks_hand'], V=['static_field'])),
        dict(at=.5, beat='kGkZ', cards=dict(k=['arcane_bolt'], G=['starfall'], Z=['meteor']),
             say='{name} strains at its chains, and the links glow white.')]),
    'hollow_shard': dict(weak=('fire',), phases=[
        dict(beat='kVGk', cards=dict(k=['shadow_bolt'], V=['curse_weak'], G=['life_drain'])),
        dict(at=.5, beat='kGVkZ', cards=dict(k=['shadow_bolt'], G=['life_drain'], V=['dread'], Z=['hellfire']),
             say='{name} cracks, and something cold looks out of the crack.')]),
    'first_uncounted': dict(weak=('cold',), phases=[
        dict(beat='kGOk', cards=dict(k=['strike'], G=['charge', 'cleave'], O=['call_band', 'war_cry'])),
        dict(at=.5, beat='kGkZ', cards=dict(k=['strike'], G=['cleave', 'charge'], Z=['executioner']), trick='enrage',
             say='{name} throws down {his} shield and takes {his} axe in both hands.')]),
    'name_keeper': dict(weak=('lightning',), phases=[
        dict(beat='kRGk', cards=dict(k=['smite'], R=['holy_shield'], G=['divine_light'])),
        dict(at=.5, beat='kVGkZ', cards=dict(k=['smite'], V=['hex'], G=['divine_light'], Z=['dawnbreak']),
             say='{name} begins to read the names aloud. The light in the hall grows.')]),
    'bound_magister': dict(weak=('fire',), phases=[
        dict(beat='kVGB', cards=dict(k=['arcane_bolt'], V=['runes', 'slow_spell'], G=['fireball'], B=['blink'])),
        dict(at=.5, beat='kRGkZ', cards=dict(k=['arcane_bolt'], R=['mirror', 'spell_ward'], G=['fireball', 'fan_knives'],
                                             Z=['stop_time']),
             say='{name} opens a book of chains. The words in it are moving.')]),
    # ---- roaming bosses: they walk a level with their band (two phases)
    'troll': dict(weak=('fire',), roam=True, phases=[
        dict(beat='kGkB', cards=dict(k=['strike'], G=['boulder', 'smash'], B=['pounce'])),
        dict(at=.5, beat='kGkZ', cards=dict(k=['strike'], G=['boulder', 'smash'], Z=['rampage']),
             say='{name} roars and beats the ground. {His} wounds are closing.')]),
    'ogre': dict(weak=('cold',), roam=True, phases=[
        dict(beat='kGkG', cards=dict(k=['strike'], G=['smash', 'charge'])),
        dict(at=.5, beat='kGkZ', cards=dict(k=['strike'], G=['smash', 'charge'], Z=['earthshaker']),
             say='{name} bellows and lifts {his} club with both hands.')]),
    'orc_chief': dict(weak=('cold',), roam=True, phases=[
        dict(beat='kGOk', cards=dict(k=['strike'], G=['cleave', 'charge'], O=['war_cry'])),
        dict(at=.5, beat='kGkZ', cards=dict(k=['strike'], G=['cleave', 'charge'], Z=['executioner']),
             say='{name} spits blood and laughs. {He} fights on harder.')]),
    'hob_captain': dict(weak=('lightning',), roam=True, phases=[
        dict(beat='kVGk', cards=dict(k=['strike'], V=['pinning_shot'], G=['volley'])),
        dict(at=.5, beat='kRGkZ', cards=dict(k=['strike'], R=['shield_wall'], G=['charge', 'volley'], Z=['executioner']),
             say='{name} barks an order. The line closes up round {him}.')]),
    'gnoll_packlord': dict(weak=('fire',), roam=True, phases=[
        dict(beat='kVGk', cards=dict(k=['bite'], V=['roar'], G=['maul'])),
        dict(at=.5, beat='kBGkZ', cards=dict(k=['bite'], B=['pounce'], G=['maul'], Z=['rampage']),
             say='{name} howls, and the howl is answered from every side.')]),
    # the Hollow King: the winds, the dead, himself (skyseat.py makes a phase lighter for every relic you bring)
    'hollow_king': dict(weak=('fire',), things='pillars', phases=[
        dict(beat='kVGkZ', cards=dict(k=['arcane_bolt'], V=['gust', 'static_field'], G=['chain_lightning', 'ball_lightning'],
                                      Z=['tempest'])),
        dict(at=.66, beat='kOGkZ', cards=dict(k=['bone_spear'], O=['call_bound'], G=['life_drain', 'wail'], Z=['army_dead']),
             trick='call', say='{name} lets the winds go. The bound dead come up through the floor, all of them at once.'),
        dict(at=.33, beat='kGVkZ', cards=dict(k=['strike'], G=['cleave', 'starfall'], V=['withering'], Z=['meteor', 'mark_doom']),
             trick='dark', say='{name} stands up from the throne. He is taller than you thought, and the lamps go out.')]),
    # three servants of the Hollow King (shadow.py)
    'wendigo': dict(weak=('fire',), phases=[
        dict(beat='kGkV', cards=dict(k=['claw'], G=['pounce', 'cone_cold'], V=['dread'])),
        dict(at=.66, beat='kOGkB', cards=dict(k=['claw'], O=['call_wolves'], G=['cone_cold', 'pounce'], B=['shadowstep']),
             trick='fog', say='{name} breathes out, and a freezing fog fills the lodge.'),
        dict(at=.33, beat='kGkZ', cards=dict(k=['claw'], G=['life_drain', 'pounce'], Z=['blizzard']),
             say='{name} howls with hunger. {His} wounds close as {he} feeds on the cold.')]),
    'great_wolf': dict(weak=('fire',), phases=[
        dict(beat='kBkV', cards=dict(k=['bite'], B=['pounce'], V=['roar'])),
        dict(at=.66, beat='kOBkG', cards=dict(k=['bite'], O=['call_wolves'], B=['pounce'], G=['maul']),
             say='{name} lifts {his} head and howls. The pack comes.'),
        dict(at=.33, beat='kBGkZ', cards=dict(k=['bite'], B=['pounce'], G=['maul', 'hamstring'], Z=['rampage']), trick='enrage',
             say='{name} bleeds, and does not slow down.')]),
    'fallen_mage': dict(weak=('lightning',), phases=[
        dict(beat='kVGkR', cards=dict(k=['shadow_bolt'], V=['hex', 'slow_spell'], G=['fireball'], R=['spell_ward'])),
        dict(at=.66, beat='kOGkV', cards=dict(k=['arcane_bolt'], O=['call_hounds'], G=['chain_lightning', 'fireball'],
                                              V=['mirror']), say='{name} laughs once, and there are three of {him}.'),
        dict(at=.33, beat='kGVkZ', cards=dict(k=['shadow_bolt'], G=['life_drain', 'chain_lightning'], V=['blink'],
                                              Z=['meteor']), trick='dark',
             say='{name} tears a page from the air. The lamps go out.')]),
}
from . import servants as _SV  # noqa: E402  (the decks of the sixteen other servants)
KITS.update(_SV.KITS)
ROAMERS = {'dungeon': ['troll', 'ogre'], 'deep': ['troll', 'ogre'], 'cave': ['troll', 'ogre'], 'wild': ['ogre'],
           'orccamp': ['orc_chief', 'hob_captain'], 'lair_orc': ['orc_chief', 'ogre'], 'warren': ['hob_captain'],
           'burrow': ['gnoll_packlord'], 'crypt': ['ghast_lord'], 'barrow': ['ghast_lord']}
HEARD = {'troll': ['Heavy steps, somewhere {dir} of you.', 'Something big grunts and sniffs, {dir} of you.'],
         'ogre': ['Heavy steps, somewhere {dir} of you.', 'A great club drags on stone, {dir} of you.'],
         'orc_chief': ['A war horn, {dir} of you.', 'Orcs laugh and shout, somewhere {dir}.'],
         'hob_captain': ['Boots in step, somewhere {dir} of you.', 'A captain barks an order, {dir} of you.'],
         'gnoll_packlord': ['Laughing howls, {dir} of you.', 'Claws click on stone, somewhere {dir}.'],
         'ghast_lord': ['A wet, hungry sound, {dir} of you.', 'The stink of the grave drifts from the {dir}.']}


def kit(mon):
    if mon.is_npc or not (mon.tpl.get('boss') or 'bs' in mon.__dict__):
        return None
    return mon.__dict__.get('kit_over') or KITS.get(mon.k)          # a lighter kit: the Hollow King (skyseat.py)


def st(mon):
    return mon.__dict__.get('bs')


def on_spawn(game, mon):
    """A kit boss gets its state when it is made; a theme boss or a roamer when it is set down as one (`arm`)."""
    if mon.k in KITS and mon.tpl.get('boss'):
        arm(mon)


def arm(mon):
    if mon.k in KITS and 'bs' not in mon.__dict__:
        mon.bs = dict(phase=0, pending=None, i=0, piles={}, spent=0, stag=0, dots=0, stun=0, resolve=RESOLVE,
                      seen_hold=0, sil=False, engaged=False, took={}, breaks=0, prep=[], weak_t=-1, fed=0)


def name_of(mon):
    from .behave import The
    return The(mon)


def fill(text, mon, aim=None):
    from .behave import his, him, PRON
    he = PRON[getattr(mon, 'gender', None)][0]
    import re
    out = re.sub(r'(^|[.!?] )\{name\}', lambda mt: mt.group(1) + name_of(mon), text)
    out = out.replace('{name}', mon.the()).replace('{his}', his(mon)).replace('{him}', him(mon))
    out = out.replace('{aim}', aim or 'you').replace('{He}', he.capitalize()).replace('{His}', his(mon).capitalize())
    out = out.replace('{he}', he)
    return out.replace('{himself}', him(mon) + 'self')


def phases(mon):
    k = kit(mon)
    return k['phases'] if k else []


def great_evil(game, mon):
    return any(getattr(e, 'd', {}).get('boss') == mon.k for e in getattr(game.world, 'evils', ()))


# ------------------------------------------------------------------ shapes
def _open(m, x, y):
    return m.inb(x, y) and not D.TILES[m.tile(x, y)].opaque


def clear_line(m, x0, y0, x1, y1):
    """Nothing that blocks sight between the two (creatures do not)."""
    from .engine import line
    return all(_open(m, x, y) for x, y in line(x0, y0, x1, y1)[:-1])


def area(game, mon):
    """The cells a room-wide blow can reach: its arena, or what lies round it."""
    m = game.map
    ar = arena_of(game, mon)
    if ar:
        return set(ar['cells'])
    return {(x, y) for x in range(mon.x - 8, mon.x + 9) for y in range(mon.y - 8, mon.y + 9) if _open(m, x, y)}


def cells_for(game, mon, mv, tx, ty):
    """The cells a shaped move strikes, aimed at (tx, ty)."""
    m = game.map
    shape = mv.get('shape')
    bx, by = mon.x, mon.y
    out = set()
    if shape == 'circle':
        r = mv.get('r', 1)
        out = {(x, y) for x in range(tx - r, tx + r + 1) for y in range(ty - r, ty + r + 1)}
    elif shape == 'ring':
        r, inner = mv.get('r', 2), mv.get('inner', 0)
        out = {(x, y) for x in range(bx - r, bx + r + 1) for y in range(by - r, by + r + 1)
               if cheb(x, y, bx, by) > inner}
    elif shape == 'ringat':                                 # a ring round you: get out before it closes
        r = mv.get('r', 2)
        out = {(x, y) for x in range(tx - r, tx + r + 1) for y in range(ty - r, ty + r + 1) if cheb(x, y, tx, ty) == r}
    elif shape == 'arc':                                    # the cells before it, towards whom it wants
        dx, dy = tx - bx, ty - by
        n = max(1, (dx * dx + dy * dy) ** .5)
        ln = mv.get('len', 1)
        for x in range(bx - ln, bx + ln + 1):
            for y in range(by - ln, by + ln + 1):
                vx, vy = x - bx, y - by
                d = (vx * vx + vy * vy) ** .5
                if d and (vx * dx + vy * dy) / (d * n) >= .5:
                    out.add((x, y))
    elif shape == 'cross':                                  # round you (at aim), or through the room from it
        cx, cy = (tx, ty) if mv.get('at') == 'aim' else (bx, by)
        ln = mv.get('len', 1)
        out = {(cx + k * a, cy + k * b) for k in range(0 if mv.get('at') == 'aim' else 1, ln + 1)
               for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))}
        if mv.get('at') != 'aim':
            out = {c for c in out if clear_line(m, bx, by, *c)}
    elif shape == 'strips':                                 # bands of floor across the room, one through you
        own = area(game, mon)
        n = mv.get('n', 3)
        rows = sorted({y for _x, y in own})
        flip = (tx + ty + game.turn) % 2 == 0
        key = (lambda c: c[1]) if flip else (lambda c: c[0])
        mine = ty if flip else tx
        lines = {mine + 3 * k for k in range(-(n // 2), n - n // 2)} if rows else set()
        out = {c for c in own if key(c) in lines}
    elif shape == 'scatter':                                # rings or single stones over the floor, one on you
        own = sorted(area(game, mon))
        r, n = mv.get('r', 1), mv.get('n', 4)
        rnd = random.Random(game.turn * 7 + tx * 31 + ty)
        pts = [(tx, ty)]
        rnd.shuffle(own)
        for c in own:
            if len(pts) >= n:
                break
            if all(cheb(*c, *q) >= 2 * r + 2 for q in pts):
                pts.append(c)
        out = {(x + a, y + b) for x, y in pts for a in range(-r, r + 1) for b in range(-r, r + 1)}
    elif shape == 'wave':                                   # a wave from its side of the room: behind cover is dry
        own = {c for c in area(game, mon) if _open(m, *c)}
        horiz = abs(tx - bx) >= abs(ty - by)
        step = ((1 if tx >= bx else -1), 0) if horiz else (0, (1 if ty >= by else -1))
        for c in own:
            x, y = c
            ok = True
            while True:
                x, y = x - step[0], y - step[1]
                if (x, y) not in own:
                    if m.inb(x, y) and D.TILES[m.tile(x, y)].opaque and (x - step[0], y - step[1]) in own:
                        ok = False                         # a pillar or a wall in the room stands before it
                    break
            if ok:
                out.add(c)
        out = {c for c in out if c != (bx, by)}
    elif shape in ('line', 'cone', 'wide'):
        dx, dy = tx - bx, ty - by
        n = max(1, (dx * dx + dy * dy) ** .5)
        ux, uy = dx / n, dy / n
        ln = mv.get('len', 4)
        for x in range(bx - ln, bx + ln + 1):
            for y in range(by - ln, by + ln + 1):
                vx, vy = x - bx, y - by
                d = (vx * vx + vy * vy) ** .5
                if not d or d > ln + .5:
                    continue
                along = vx * ux + vy * uy
                if along <= 0:
                    continue
                side = abs(vx * uy - vy * ux)
                if (shape == 'line' and side <= .75) or (shape == 'wide' and side <= 1.6) \
                        or (shape == 'cone' and along >= d * .7):
                    out.add((x, y))
    elif shape == 'tail':                                   # the half behind it: where you are not
        dx, dy = tx - bx, ty - by
        for x in range(bx - 2, bx + 3):
            for y in range(by - 2, by + 3):
                if (x, y) != (bx, by) and (x - bx) * dx + (y - by) * dy <= 0:
                    out.add((x, y))
    elif shape == 'room':
        out = {c for c in area(game, mon) if clear_line(m, bx, by, c[0], c[1])} - shelter(game, mon, mv)
    elif shape == 'corpses':
        own = area(game, mon)
        for k, x, y, _l in getattr(m, 'slain', ()):
            if (x, y) in own:
                out |= {(x + a, y + b) for a in (-1, 0, 1) for b in (-1, 0, 1)}
    elif shape in ('mark', 'self'):
        return set()
    out = {c for c in out if _open(m, *c)}
    if shape not in ('room', 'circle', 'corpses', 'ringat', 'strips', 'scatter', 'wave') \
            and not (shape == 'cross' and mv.get('at') == 'aim'):
        out = {c for c in out if clear_line(m, bx, by, c[0], c[1])}
    return out


def shelter(game, mon, mv):
    """The cells a room-wide blow spares: by a stone of light, on a ledge, by a chain that still holds."""
    safe = mv.get('safe')
    if not safe:
        return set()
    m = game.map
    tiles = {'light': (D.LIGHTSTONE,), 'ledge': (D.BLEDGE, D.BCHAIN)}[safe]
    out = set()
    for c in area(game, mon):
        if m.tile(*c) in tiles or any(m.inb(c[0] + a, c[1] + b) and m.tile(c[0] + a, c[1] + b) in tiles
                                      and (safe == 'light' or m.tile(c[0] + a, c[1] + b) == D.BCHAIN) for a, b in D8):
            out.add(c)
    return out


def need(game, mon, mv, cells, tx, ty, cap=3):
    """How many steps you need to get out of it (0: you are not in it); None if no free tile lies within `cap`.
    A blow loads at least that long, so there is always a way out in time."""
    m, p = game.map, game.player
    if mv.get('shape') == 'self':
        return 0
    if mv.get('shape') == 'mark':
        safe = lambda c: not clear_line(m, mon.x, mon.y, c[0], c[1]) or m.tile(*c) == D.HALLOWED  # noqa: E731
        start = (tx, ty)
    else:
        if (p.x, p.y) not in cells and (tx, ty) not in cells:
            return 0
        safe = lambda c: c not in cells  # noqa: E731
        start = (p.x, p.y) if (p.x, p.y) in cells else (tx, ty)
    if safe(start):
        return 0
    ar = arena_of(game, mon)
    room = set(map(tuple, ar['cells'])) if ar and ar.get('sealed') else None
    seen, edge = {start}, [start]
    for k in range(1, cap + 1):
        nxt = []
        for x, y in edge:
            for a, b in D8:
                c = (x + a, y + b)
                if c in seen or not m.inb(*c) or not D.TILES[m.tile(*c)].walk or (room and c not in room):
                    continue
                o = m.mon_at(*c)
                if o is not None and o is not mon and not getattr(o, 'ally', False):
                    continue
                seen.add(c)
                if safe(c):
                    return k
                nxt.append(c)
        edge = nxt
    return None


def fair(game, mon, mv, cells, tx, ty):
    """Is there a way out in the turns it loads?"""
    n = need(game, mon, mv, cells, tx, ty, 4 if mv['role'] == 'Z' else 3)
    return n is not None and n <= max(mv.get('load', 1), 3)


# ------------------------------------------------------------------ who it aims at
def aim(game, mon):
    """(who, x, y): who it goes for, by threat (mercs.py)."""
    from . import mercs as MC
    p = game.player
    w = MC.pick(game, mon)
    if w != 'p':
        mc = next((c for c in MC.party(game) if c.who == w and c.body is not None and c.body in game.map.mons), None)
        if mc:
            return mc, mc.body.x, mc.body.y
    return 'p', p.x, p.y


def ref_life(game, lvl, full):
    """What a great blow is measured against: your full life, but no more than a hero of its level has."""
    return min(full, 40 + 10 * lvl)


# ------------------------------------------------------------------ the deck
def beat(game, mon):
    """The role of this beat, and whether the beat moves on after it."""
    bs = st(mon)
    ph = phases(mon)[bs['phase']]
    pat = ph['beat']
    role = pat[bs['i'] % len(pat)]
    if bs.get('wild') and role == 'V':
        role = 'k'                                           # the beast gone wild: no more set-ups
    if bs.get('stolen') and role == 'k' and random.random() < .15:
        return 'Z'
    if bs['i'] and random.random() < .2:                    # the rhythm breaks
        nxt = pat[(bs['i'] + 1) % len(pat)]
        if role == 'k' and nxt in 'GZ':
            bs['i'] += 1
            return nxt
        if role in 'GZV':
            bs['i'] -= 1                                     # an extra small one first
            return 'k'
    return role


def draw(mon, role):
    bs = st(mon)
    if role == 'Z' and bs.get('stolen') and random.random() < .5:
        return bs['stolen']
    ph = phases(mon)[bs['phase']]
    cards = ph['cards'].get(role) or ph['cards']['k']
    pile = bs['piles'].get(role)
    if not pile:
        pile = bs['piles'][role] = list(cards) * (2 if len(cards) < 3 else 1)     # the shuffle card: all back in
        random.shuffle(pile)
    return pile.pop()


# ------------------------------------------------------------------ a boss's turn
def turn(game, mon, df):
    """Before its usual moves. True if it used its turn."""
    if mon.is_npc:
        return False
    if mon.__dict__.get('image_of') is not None:
        if not mon.__dict__.get('skin') and cheb(mon.x, mon.y, game.player.x, game.player.y) > 1:
            game.step_toward(mon)                              # an image only shows itself; it never strikes
        return True
    bs = st(mon)
    if bs is None and not mon.tpl.get('boss'):
        return False
    c = mon.__dict__.get('cast')
    if c:
        _go_on(game, mon, c)
        return True
    if bs is None:
        return _plain(game, mon)
    crossed(mon)
    BM.wear(mon)
    if mon.__dict__.get('roam') and not hunting(game, mon):
        patrol(game, mon)
        return True
    if bs.get('pending') is not None:
        _phase(game, mon, bs.pop('pending'), True)
        bs['pending'] = None
        return True
    p = game.player
    if (not bs['engaged'] and mon.awake and game.visible(mon.x, mon.y) and cheb(mon.x, mon.y, p.x, p.y) <= 9) or bs['engaged']:
        engage(game, mon)
    role = beat(game, mon)
    mvid = draw(mon, role)
    if mon.__dict__.get('no_call') and MOVES[mvid].get('kind') == 'call':
        role, mvid = 'k', draw(mon, 'k')                     # its weakness named: no one comes to it (shadow.py)
    if do(game, mon, mvid, df):
        bs['i'] += 1
        return True
    if role != 'k':
        mvid = draw(mon, 'k')
    return _small(game, mon, mvid, df)


def crossed(mon):
    """Blows that went round `blow` (a hireling's, a beast's) can take it past a threshold: the change comes now."""
    bs = st(mon)
    if bs.get('pending') is not None:
        return
    ph = phases(mon)
    nxt = bs['phase'] + 1
    if nxt < len(ph) and mon.hp <= round(mon.maxhp * ph[nxt]['at']):
        bs['pending'] = nxt


def _small(game, mon, mvid, df):
    """A small blow by the threat: a bolt, or a blow when it stands beside whom it wants."""
    from . import mercs as MC
    bs = st(mon)
    mv = MOVES[mvid]
    who, tx, ty = aim(game, mon)
    d = cheb(mon.x, mon.y, tx, ty)
    if mv.get('kind') == 'bolt' and 2 <= d <= 8 and 'silence' not in mon.effects:
        if who == 'p':
            if game.mon_shoot(mon, True, df):
                bs['i'] += 1
                return True
        elif game.line_clear(mon.x, mon.y, tx, ty):
            game.fx('bolt', cells=game.line_clear(mon.x, mon.y, tx, ty), src=(mon.x, mon.y), col=(220, 220, 255), ch='*')
            MC.hurt(game, who, random.randint(*mon.dmg) * .85, mon)
            bs['i'] += 1
            return True
    if d <= 1:
        bs['i'] += 1                                         # the engine strikes (mercs.py picks whom)
    return False


def _plain(game, mon):
    """The other bosses: their nova and their leap now come marked (round 16 gives them a kit)."""
    d, p = mon.tpl, game.player
    if not mon.awake or not game.visible(mon.x, mon.y):
        return False
    dist = cheb(mon.x, mon.y, p.x, p.y)
    if d.get('nova') and dist <= 2 and random.random() < .22:
        return start(game, mon, 'nova', say=d.get('nova_say', '{name} draws the air in round {him}. The ground about {him} darkens...'))
    if d.get('leap') and 2 <= dist <= 5 and game.line_clear(mon.x, mon.y, p.x, p.y) and random.random() < .3:
        return start(game, mon, 'leap', say='{name} crouches, eyes on the ground where you stand...')
    return False


def do(game, mon, mvid, df):
    """Use a card. False if it cannot be done now (it then makes a small move instead)."""
    mv = MOVES[mvid]
    kind = mv.get('kind')
    if kind in ('melee', 'bolt'):
        return False
    if mv.get('shape'):
        return start(game, mon, mvid)
    m, p = game.map, game.player
    if kind == 'snares':
        from .behave import traps
        tr = traps(m)
        line_ = list(game.cells_between((mon.x, mon.y), (p.x, p.y))[1:-1])
        spots = [c for c in line_ if m.tile(*c) == D.FLOOR and c not in tr][:3]
        if len(spots) < 3:
            spots += [c for c in free_around(game, m, p.x, p.y, 2) if m.tile(*c) == D.FLOOR and c not in tr
                      and c not in spots and cheb(*c, p.x, p.y) == 2][:3 - len(spots)]
        if not spots or cheb(mon.x, mon.y, p.x, p.y) > 9:
            return False
        for c in spots:
            tr[c] = max(2, mon.dmg[0])
        m.known_traps = getattr(m, 'known_traps', set()) | set(spots)
        game.msg(fill(mv['say'], mon), 'bad')
        return True
    if kind == 'prison':
        from . import spellmap as SM
        if cheb(mon.x, mon.y, p.x, p.y) > 8:
            return False
        ring = [(p.x + a, p.y + b) for a, b in D8]
        random.shuffle(ring)
        got = sum(1 for c in ring[2:] if SM.place(game, m, c[0], c[1], D.BONEWALL, 6))
        if not got:
            return False
        game.msg(fill(mv['say'], mon), 'bad')
        return True
    if kind == 'call':
        return call(game, mon, mv['helpers'], mv['say'])
    if kind == 'raise':
        return raise_dead(game, mon, mv['n'], mv['say'])
    if kind == 'wing':
        if cheb(mon.x, mon.y, p.x, p.y) > 10:
            return False
        if not start(game, mon, 'dive', say=mv['say']):
            return False
        mon.invis = 99
        st(mon)['air'] = True
        return True
    got = BM.do(game, mon, mv)
    return bool(got)


def start(game, mon, mvid, say=None):
    """Load a marked blow: its cells go red. False if it would leave you no way out."""
    mv = MOVES[mvid]
    if mv.get('shape') == 'mark':
        who, tx, ty = aim(game, mon)
    elif mv.get('at') == 'aim' or mv.get('shape') in ('line', 'cone', 'tail'):
        who, tx, ty = aim(game, mon)
    else:
        who, tx, ty = 'p', game.player.x, game.player.y
    if mv.get('shape') not in ('ring', 'room', 'corpses', 'self', 'wave', 'strips') \
            and cheb(mon.x, mon.y, tx, ty) > max(9, mv.get('len', 0)):
        return False
    if mv.get('fx', {}).get('split') and mon.__dict__.get('knot') is not None:
        return False                                         # a knot comes apart only once
    stones = lightstones(game, mon, mv)
    cells = cells_for(game, mon, mv, tx, ty)
    if mv.get('shape') not in ('mark', 'self') and not cells:
        unlight(game, stones)
        return False
    n = need(game, mon, mv, cells, tx, ty, 4 if mv['role'] == 'Z' else 3)
    if n is None:
        unlight(game, stones)
        return False                                         # no way out: it picks another move
    bs = st(mon)
    load = mv.get('load', 1) - (1 if bs and bs.get('enrage') and mv.get('load', 1) >= 2 else 0)
    load = max(load, n, 1)                                   # never faster than you can get out
    brk = mv.get('brk', load >= 2)
    if bs and 'unbroken' in bs['prep'] and bs['phase'] == len(phases(mon)) - 1:
        brk = False
    mon.cast = dict(mv=mvid, left=load, load=load, cells=sorted(cells), who=who if who == 'p' else who.who,
                    tx=tx, ty=ty, taken=0, brk=brk, told=[], stones=stones,
                    gold=sorted(shelter(game, mon, mv) & {c for c in area(game, mon) if D.TILES[game.map.tile(*c)].walk}))
    text = say if say is not None else mv.get('say', '')
    if text:
        aim_name = 'you' if who == 'p' else who.name
        game.msg(fill(text, mon, aim_name), 'bad')
    from . import guide as GD
    if game.visible(mon.x, mon.y):
        GD.tip(game, 'red')
    return True


def lightstones(game, mon, mv):
    """Dawnbreak: it sets down two stones of light first, one near you; by them the light does no harm."""
    if mv.get('safe') != 'light':
        return []
    m, p = game.map, game.player
    own = [c for c in area(game, mon) if m.tile(*c) == D.FLOOR and not game.occupied(m, *c)]
    near = [c for c in own if 2 <= cheb(*c, p.x, p.y) <= 3]
    far = [c for c in own if cheb(*c, p.x, p.y) >= 5 and cheb(*c, mon.x, mon.y) >= 3]
    out = []
    for pool in (near, far):
        if pool:
            c = random.choice(pool)
            m.set(c[0], c[1], D.LIGHTSTONE)
            out.append(c)
    return out


def unlight(game, stones):
    for c in stones or ():
        if game.map.tile(*c) == D.LIGHTSTONE:
            game.map.set(c[0], c[1], D.FLOOR)


def _target_xy(game, mon, c):
    from . import mercs as MC
    if c['who'] == 'p':
        return game.player.x, game.player.y
    mc = next((x for x in MC.party(game) if x.who == c['who'] and x.body is not None and x.body in game.map.mons), None)
    return (mc.body.x, mc.body.y) if mc else (c['tx'], c['ty'])


def _go_on(game, mon, c):
    """One turn of a loading blow: it counts down; one that follows you moves along; at nought it strikes."""
    c['left'] -= 1
    mv = MOVES[c['mv']]
    if c['left'] <= 0:
        mon.cast = None
        release(game, mon, c)
        return
    if mv.get('follow'):                                     # it follows you, as long as you can still get out
        tx, ty = _target_xy(game, mon, c)
        cells = cells_for(game, mon, mv, tx, ty)
        n = need(game, mon, mv, cells, tx, ty, c['left'])
        if cells and n is not None and n <= c['left']:
            c['tx'], c['ty'] = tx, ty
            c['cells'] = sorted(cells)


def release(game, mon, c):
    """The blow lands on every cell that was marked: you, your company, and its own helpers too."""
    from . import spellmap as SM
    from . import mercs as MC
    m, p = game.map, game.player
    mv = MOVES[c['mv']]
    bs = st(mon)
    fx = mv.get('fx', {})
    cells = set(map(tuple, c['cells']))
    if bs and bs.get('air'):
        bs['air'] = False
        mon.invis = 0
    if fx.get('land'):                                       # it comes down where the circle was
        spot = (c['tx'], c['ty'])
        if not D.TILES[m.tile(*spot)].walk or game.occupied(m, *spot):
            near = [s for s in free_around(game, m, *spot, 1)] or free_around(game, m, mon.x, mon.y, 1)
            spot = near[0] if near else (mon.x, mon.y)
        if may_stand(game, mon, *spot):
            mon.x, mon.y = spot
    if fx.get('rush'):                                       # along the line, until something stops it
        from .engine import line
        for x, y in line(mon.x, mon.y, c['tx'], c['ty'])[:mv.get('len', 4)]:
            if (x, y) not in cells or not D.TILES[m.tile(x, y)].walk or game.occupied(m, x, y) or not may_stand(game, mon, x, y):
                break
            mon.x, mon.y = x, y
    col = {'fire': (255, 120, 40), 'cold': (160, 216, 255), 'lightning': (220, 230, 255), 'poison': (150, 220, 90),
           'holy': (255, 240, 170)}.get(mv.get('elem'), (255, 80, 60))
    if mv.get('shape') == 'mark':
        tx, ty = _target_xy(game, mon, c)
        safe = not clear_line(m, mon.x, mon.y, tx, ty) or m.tile(tx, ty) == D.HALLOWED
        cells = set() if safe else {(tx, ty)}
        if safe:
            game.msg('The Mark of Doom falls, and finds nothing: it cannot see its mark.', 'good')
    game.flash([cc for cc in cells if game.visible(*cc)], col, '*', .3)
    if c['mv'] in ('nova', 'leap') and game.visible(mon.x, mon.y):
        game.msg(mon.tpl.get(c['mv'] + '_msg', '{name} strikes!').format(name=name_of(mon)), 'bad')
    if mv.get('shape') == 'self':
        BM.on_self(game, mon, mv)
        if bs and mv['role'] == 'Z' and mon in m.mons:
            bs['spent'] = 1
            game.msg(f'{name_of(mon)} stands spent, {fill("{his}", mon)} strength gone for a moment. Now!', 'gold')
        return
    power = mv.get('power', .3) * (1 + (bs['fed'] if bs and mv['role'] == 'Z' else 0))
    power = BM.power(game, mon, mv, power)
    if bs and mv['role'] == 'Z':
        bs['fed'] = 0
    lvl = mon.lvl
    s = game.stats()
    if (p.x, p.y) in cells and not game.dead:
        dmg = power * ref_life(game, lvl, s['max_life']) * random.uniform(.9, 1.1)
        if mv.get('hit'):
            game.msg(fill(mv['hit'], mon), 'bad')
        game.spare_full = True                               # a marked blow never kills from full life
        game.hurt(dmg, mon.the(), mv.get('elem'))
        game.__dict__.pop('spare_full', None)
        if not game.dead:
            BM.on_you(game, mon, fx)
            if fx.get('push'):
                push(game, mon, p, fx['push'])
            BM.hit_more(game, mon, mv, dmg)
    elif c['who'] == 'p' and cells and mv.get('shape') != 'mark' and min(cheb(*cc, p.x, p.y) for cc in cells) <= 2:
        game.msg('The blow lands where you stood a moment ago.', 'info')
    for mc in MC.party(game):
        b = mc.body
        if b is None or b not in m.mons or (b.x, b.y) not in cells:
            continue
        mx = MC.stats(game, mc)['max_hp']
        dmg = power * ref_life(game, lvl, mx) * random.uniform(.9, 1.1) * (.5 if getattr(b, 'braced', False) else 1)
        if mc.hp >= mx:
            dmg = min(dmg, mc.hp - 1)
        b.braced = False
        MC.hurt(game, mc, max(1, dmg), mon)
    for o in [o for o in m.mons if o is not mon and not o.is_npc and (o.x, o.y) in cells]:
        dmg = max(1, round(o.maxhp * power * 1.6))
        o.hp -= dmg
        game.num(o.x, o.y, str(dmg), (240, 200, 150))
        if o.hp <= 0:
            if getattr(o, 'job', None) and game.visible(o.x, o.y):
                game.msg(f"{name_of(o)} is caught in {mon.the()}'s own blow!", 'good')
            game.kill(o)
    if fx.get('burn'):
        spots = [cc for cc in cells if D.TILES[m.tile(*cc)].walk]
        random.shuffle(spots)
        for cc in spots[:fx['burn'] * 2]:
            SM.place(game, m, cc[0], cc[1], D.BURNING, fx['burn'], max(2, lvl // 2))
    if fx.get('coins'):
        from .entities import Item
        spots = [cc for cc in cells if D.TILES[m.tile(*cc)].walk and cc != (p.x, p.y)]
        random.shuffle(spots)
        for cc in spots[:fx['coins']]:
            it = Item(game.new_id(), 'gold', 'gold', random.randint(1, 3))
            it.x, it.y = cc
            m.items.append(it)
    if fx.get('pillar'):
        break_pillar(game, mon)
    BM.after(game, mon, mv, cells, c)
    unlight(game, c.get('stones'))
    if bs and mv['role'] == 'Z' and not game.dead and mon in m.mons:
        bs['spent'] = 2 if random.random() < .25 else 1
        game.msg(f'{name_of(mon)} stands spent, {fill("{his}", mon)} strength gone for a moment. Now!', 'gold')


def push(game, mon, who, n):
    m = game.map
    dx, dy = (who.x > mon.x) - (who.x < mon.x), (who.y > mon.y) - (who.y < mon.y)
    if not dx and not dy:
        dx = 1
    for _ in range(n):
        nx, ny = who.x + dx, who.y + dy
        if not m.inb(nx, ny) or not D.TILES[m.tile(nx, ny)].walk or game.occupied(m, nx, ny):
            break
        ar = game.map.__dict__.get('arena')
        if ar and ar.get('sealed') and (nx, ny) not in ar['cells']:
            break
        who.x, who.y = nx, ny


# ------------------------------------------------------------------ helpers with a job
def helpers(game, mon):
    return [o for o in game.map.mons if getattr(o, 'boss_of', None) == mon.id]


def call(game, mon, which, say):
    from .entities import make_monster
    m = game.map
    if len(helpers(game, mon)) >= 4:
        return False
    ar = arena_of(game, mon)
    room = ar['cells'] if ar else None
    spots = [c for c in free_around(game, m, mon.x, mon.y, 5) if cheb(*c, mon.x, mon.y) >= 2 and (room is None or c in room)]
    if not spots:
        return False
    random.shuffle(spots)
    have = {o.job for o in helpers(game, mon)}
    for (k, job), c in zip(which, spots):
        if k not in D.MONSTERS or (job in ('mender', 'warder', 'channeler', 'bearer') and job in have):
            continue                                         # one of each such job at a time
        have.add(job)
        o = make_monster(game, k, c[0], c[1], max(1, mon.lvl - 1))
        o.awake = o.called = True
        o.job, o.boss_of = job, mon.id
        m.mons.append(o)
        game.flash([c], (255, 214, 90), '*', .2)
    if say:
        game.msg(fill(say, mon), 'bad')
    return True


def raise_dead(game, mon, n, say):
    from .entities import make_monster
    m = game.map
    own = area(game, mon)
    sl = getattr(m, 'slain', [])
    here = [s for s in sl if (s[1], s[2]) in own and not game.occupied(m, s[1], s[2])][:n]
    if not here or len(helpers(game, mon)) >= 5:
        return False
    for s in here:
        sl.remove(s)
        o = make_monster(game, 'skeleton', s[1], s[2], max(1, mon.lvl - 3))
        o.awake = o.called = True
        o.job, o.boss_of = 'swarm', mon.id
        m.mons.append(o)
        game.flash([(s[1], s[2])], (196, 134, 255), '*', .2)
    if say:
        game.msg(fill(say, mon), 'bad')
    return True


def warded(game, mon):
    m = game.map
    if getattr(mon, 'lord', False) and getattr(m, 'gate', None) and m.tile(*m.gate) == D.FIREGATE and D.FIREBOWL in m.t:
        return True                                          # the burning gate is his warder while a bowl burns
    return any(o.job == 'warder' for o in helpers(game, mon))


def helper_turn(game, mon, df):
    """A helper does its job: the warder and the mender keep near their master; the channeler feeds its next blow."""
    boss = next((o for o in game.map.mons if o.id == getattr(mon, 'boss_of', None)), None)
    if boss is None:
        return False
    job = mon.job
    p = game.player
    if getattr(mon, 'watching', False):
        return True                                          # the duel: the guard stands back and watches
    if boss.__dict__.get('roam') and not hunting(game, boss):
        if cheb(mon.x, mon.y, boss.x, boss.y) > 2:
            step_to(game, mon, boss.x, boss.y)
        return True                                          # the band keeps to its leader
    if job == 'bearer':
        if cheb(mon.x, mon.y, boss.x, boss.y) > 2:
            return False
        return cheb(mon.x, mon.y, p.x, p.y) > 1
    if job in ('warder', 'mender', 'channeler') and cheb(mon.x, mon.y, p.x, p.y) > 1:
        if job == 'mender' and game.turn % 4 == 0 and boss.hp < boss.maxhp and clear_line(game.map, mon.x, mon.y, boss.x, boss.y):
            cap = cap_hp(boss)
            boss.hp = min(cap, boss.hp + max(2, boss.maxhp // 40))
            game.flash([(boss.x, boss.y)], (120, 240, 140), '+', .25)
            return True
        if job == 'channeler':
            bs = st(boss)
            if bs:
                bs['fed'] = min(.5, bs['fed'] + .05)
                if game.turn % 4 == 0:
                    game.flash([(mon.x, mon.y), (boss.x, boss.y)], (255, 160, 60), '~', .2)
            return True
        if cheb(mon.x, mon.y, boss.x, boss.y) > 2:
            return False                                     # it walks back to its master
        return True
    return False


def cap_hp(mon):
    """No healing past the threshold it has already crossed."""
    bs = st(mon)
    if not bs:
        return mon.maxhp
    ph = phases(mon)
    return mon.maxhp if bs['phase'] == 0 else round(mon.maxhp * ph[bs['phase']]['at'])


# ------------------------------------------------------------------ phases, spent, stagger, breaking
def _phase(game, mon, i, trick):
    bs = st(mon)
    bs['phase'], bs['i'], bs['piles'] = i, 0, {}
    mon.threat = {}                                          # who it wants is open again
    mon.cast = None
    if st(mon).get('air'):
        bs['air'] = False
        mon.invis = 0
    ph = phases(mon)[i]
    if not trick:
        return
    game.msg(fill(ph.get('say', '{name} changes.'), mon), 'bad')
    game.shake()
    t = ph.get('trick')
    if t and t in (mon.__dict__.get('no_trick'), 'call' if mon.__dict__.get('no_call') else None):
        t = None
    ar = arena_of(game, mon)
    m = game.map
    if t == 'call':
        o = next((MOVES[c] for c in ph['cards'].get('O', ()) if MOVES[c].get('kind') == 'call'), MOVES['call_kobolds'])
        call(game, mon, o['helpers'], '')
    elif t == 'water' and ar:
        ar['water'] = ar.get('water', 0) + 1
        flood(game, ar)
    elif t == 'ceiling' and ar:
        ar['ceiling'] = 0
    elif t == 'collapse' and ar:
        for c in ar.get('pillars', ()):
            if m.tile(*c) == D.PILLAR:
                m.set(c[0], c[1], D.FALLEN)
    elif t == 'webs':
        from . import spellmap as SM
        own = [c for c in area(game, mon) if m.tile(*c) == D.FLOOR and cheb(*c, game.player.x, game.player.y) >= 2]
        random.shuffle(own)
        SM.area(game, m, own[:max(6, len(own) // 7)], D.WEBS, 80)
    elif t == 'wind' and ar:
        ar['wind'] = random.choice(D8[:4])
    elif t == 'fog' and ar:
        ar['fog'] = True
    elif t == 'enrage':
        bs['enrage'] = True
        mon.effects['frenzy'] = [999, 0]
    elif t == 'banner':
        call(game, mon, (('orc', 'bearer'),), '')
    elif t == 'duel':
        bs['duel'] = True
        bs['enrage'] = True
        for o in helpers(game, mon):
            o.watching = True
            o.cast = None
    elif t == 'rise':
        raise_dead(game, mon, 3, '')
        call(game, mon, (('wraith', 'warder'),), '')
        game.msg('A wraith takes its place beside her and spreads its cold over her: it wards her.', 'bad')
    elif t == 'dark':
        bs['lichcraft'] = True
        if ar:
            ar['dark'] = True
    elif t == 'roar':
        call(game, mon, MOVES['call_drakes']['helpers'], '')
    elif t == 'burn':
        if ar:
            ar['dance'] = 0
        break_pillar(game, mon)


def add_dot(game, mon):
    bs = st(mon)
    bs['dots'] += 1
    if bs['dots'] >= 3:
        bs['dots'] = 0
        bs['stag'] = 2
        mon.cast = None
        game.msg(f'{name_of(mon)} staggers! Strike now!', 'gold')
        game.shake()


def do_break(game, mon, how):
    """A loading blow broken: gone, and it reels a turn."""
    c = mon.__dict__.get('cast')
    bs = st(mon)
    mon.cast = None
    if bs is not None:
        bs['stun'] = max(bs['stun'], 1)
        bs['breaks'] += 1
        if bs.get('air'):
            bs['air'] = False
            mon.invis = 0
        add_dot(game, mon)
    if c:
        unlight(game, c.get('stones'))
        if c['mv'] in ('emerge', 'dive'):
            mon.invis = 0
    name = MOVES[c['mv']]['name'] if c else 'blow'
    game.flash([(mon.x, mon.y)], (206, 132, 255), '!', .35)
    game.msg(f"{how}{name_of(mon)}'s {name} breaks! {fill('{He}', mon)} reels.", 'gold')


def pre(game, mon):
    """Before a boss acts: new holds break its blow or meet its resolve; spent, staggered or reeling, it does nothing."""
    if mon.__dict__.get('twin'):
        twin_turn(game, mon)
    bs = st(mon)
    if bs is None:
        return False
    if mon.__dict__.get('maker'):
        from . import bossmaker as MK
        MK.on_turn(game, mon)
    c = mon.__dict__.get('cast')
    if mon.hold > bs['seen_hold']:
        if c and c['brk']:
            mon.hold, mon.frozen = 0, False
            do_break(game, mon, '')
        elif bs['resolve'] > 0:
            bs['resolve'] -= 1
            mon.hold, mon.frozen = 0, False
            game.msg(f'{name_of(mon)} shrugs it off.', 'info')
        else:
            mon.hold = max(1, mon.hold // 2)
    sil = 'silence' in mon.effects
    if sil and not bs['sil'] and c and c['brk']:
        do_break(game, mon, '')
    bs['sil'] = sil
    if 'fear' in mon.effects:                                # it does not run; the light of the dawn breaks its spell
        del mon.effects['fear']
        c = mon.__dict__.get('cast')
        if c and c['brk'] and (mon.k in D.UNDEAD or mon.k == 'lich'):
            do_break(game, mon, 'The holy light tears through the spell. ')
        elif bs['resolve'] > 0:
            bs['resolve'] -= 1
            game.msg(f'{name_of(mon)} shrugs it off.', 'info')
    bs['seen_hold'] = max(0, mon.hold - 1)
    for k in ('stun', 'spent', 'stag'):
        if bs[k] > 0:
            bs[k] -= 1
            return True
    return False


def extra(game, mon, df):
    """One more small blow for each of your company beside you (D&D's legendary actions)."""
    from . import mercs as MC
    if st(mon) is None or mon.__dict__.get('cast') or mon not in game.map.mons:
        return
    p = game.player
    n = sum(1 for mc in MC.party(game) if mc.body is not None and mc.body in game.map.mons
            and cheb(mc.body.x, mc.body.y, p.x, p.y) <= 1)
    for _ in range(min(2, n)):
        if game.dead:
            return
        if cheb(mon.x, mon.y, p.x, p.y) <= 1:
            game.mon_attack(mon, df)
            continue
        mc = next((c for c in MC.party(game) if c.body is not None and c.body in game.map.mons
                   and cheb(c.body.x, c.body.y, mon.x, mon.y) <= 1), None)
        if mc:
            MC.hurt(game, mc, random.randint(*mon.dmg), mon)


# ------------------------------------------------------------------ your blows on it
def engage(game, mon):
    bs = st(mon)
    if bs is None:
        return
    if bs['engaged']:                                   # it saw you from outside: the room shuts once you are in
        ar = arena_of(game, mon)
        if ar and not ar.get('sealed') and (game.player.x, game.player.y) in set(map(tuple, ar['cells'])):
            seal(game, ar)
        return
    bs['engaged'] = True
    game.banner = [mon.name.upper(), None]
    from . import bossmaker as MK
    MK.boon_edge(game, mon)
    ar = arena_of(game, mon)
    if ar:
        if 'helper' in bs['prep'] and not helpers(game, mon):
            o = next((MOVES[c] for ph in phases(mon) for cs in ph['cards'].values() for c in cs
                      if MOVES[c].get('kind') == 'call'), None)
            if o:
                call(game, mon, o['helpers'][:1], '{name} is not alone this time.')
        p = game.player
        if (p.x, p.y) in ar['cells']:
            seal(game, ar)


def silvered(game):
    """Silver, fire or holy light: what still bites a lich that is half spirit."""
    from . import trees as TT
    s = game.stats()
    im = TT.imbue(game)
    return s.get('undead', 0) > 0 or s.get('fire_dmg', 0) > 0 or (im is not None and im[1] in ('burn', 'heal'))


def blow(game, mon, dmg, crit, weapon, elem):
    """Your blow on a kit boss: warded halves, spent and staggered take more; it stops at a threshold, unless a
    critical hit while it is spent or staggered breaks through."""
    if mon.is_npc:
        return dmg
    if mon.__dict__.get('image_of') is not None and not mon.__dict__.get('skin'):
        vanish(game, mon)
        return 0
    dmg = twin_blow(game, mon, dmg, weapon)
    bs = st(mon)
    if bs is None:
        return dmg
    if bs.get('air'):
        return 0
    engage(game, mon)
    p = game.player
    near = cheb(p.x, p.y, mon.x, mon.y) <= 1
    if bs.get('duel') and not near:
        break_duel(game, mon, 'You strike from afar. The duel is broken, and the guard comes on!')
    dmg = BM.guard(game, mon, dmg, weapon, elem, near)
    if not dmg:
        return 0
    mult = 1.0
    if warded(game, mon):
        mult *= .5
    if kit(mon).get('hide') and any(cheb(o.x, o.y, mon.x, mon.y) <= 1 for o in helpers(game, mon)):
        mult *= .5                                           # he keeps a goblin between you and him
    if bs['spent'] or bs['stag']:
        mult *= 1.5
    if bs.get('lichcraft') and weapon and not silvered(game):
        mult *= .5
    dmg = max(1, round(dmg * mult))
    key = elem or ('weapon' if weapon else 'other')
    bs['took'][key] = bs['took'].get(key, 0) + dmg
    k = kit(mon)
    if elem and elem in k.get('weak', ()) and bs['weak_t'] != game.turn:
        bs['weak_t'] = game.turn
        game.msg({'cold': 'The cold bites deep!', 'fire': 'The fire bites deep!'}.get(elem, 'That bites deep!'), 'good')
        add_dot(game, mon)
    c = mon.__dict__.get('cast')
    if c and c['brk']:
        c['taken'] += dmg
        if c['taken'] >= mon.maxhp * .1:
            do_break(game, mon, 'Your blows shake it loose. ')
    ph = phases(mon)
    cur = bs['pending'] if bs.get('pending') is not None else bs['phase']
    nxt = cur + 1
    if nxt < len(ph):
        thr = round(mon.maxhp * ph[nxt]['at'])
        if mon.hp > thr >= mon.hp - dmg:
            last = nxt == len(ph) - 1
            if crit and (bs['spent'] or bs['stag']) and bs.get('pending') is None and not (last and great_evil(game, mon)):
                floor = round(mon.maxhp * ph[nxt + 1]['at']) + 1 if nxt + 1 < len(ph) else 1
                dmg = max(0, min(dmg, mon.hp - floor))
                _phase(game, mon, nxt, False)
                bs['stun'] = max(bs['stun'], 1)
                game.msg(f'Your blow tears through! {name_of(mon)} reels, and the change that was coming in '
                         f'{fill("{him}", mon)} never comes.', 'gold')
                game.shake()
                game.flash([(mon.x, mon.y)], (255, 214, 90), '*', .4)
                from . import chronicle as CH
                CH.add(game, 'Your deeds', f'You broke through {mon.name} in one blow, and the change in '
                       f'{fill("{him}", mon)} never came.', 'seen', quiet=True)
                bs['broke_through'] = True
            else:
                dmg = mon.hp - thr
                bs['pending'] = nxt
    return max(0, dmg)


def vanish(game, mon):
    m = game.map
    if mon in m.mons:
        m.mons.remove(mon)
    game.flash([(mon.x, mon.y)], (206, 132, 255), '*', .2)
    game.msg('It was only an image. It breaks like a reflection in water.', 'info')


def break_duel(game, mon, text):
    bs = st(mon)
    if not bs.get('duel'):
        return
    bs['duel'] = False
    for o in helpers(game, mon):
        o.watching = False
        o.awake = True
    game.msg(text, 'bad')


def spare(game, mon):
    """It would die: but a threshold not yet crossed holds it, or a phylactery shard raises it again."""
    bs = st(mon)
    if bs is None or mon.hp > 0:
        return False
    if mon.__dict__.get('knot') is not None:                 # one of the knot falls; the last one is the real death
        m = game.map
        rest = [o for o in m.mons if o is not mon and o.__dict__.get('knot') == mon.knot and o.hp > 0]
        if rest:
            m.mons.remove(mon)
            ar = m.__dict__.get('arena')
            if ar and ar.get('boss') == mon.id:
                ar['boss'] = rest[0].id
            game.msg(f'One of the kings falls. {len(rest)} still {"fights" if len(rest) == 1 else "fight"}.', 'good')
            return True
        return False
    ph = phases(mon)
    cur = bs['pending'] if bs.get('pending') is not None else bs['phase']
    if cur + 1 < len(ph):
        mon.hp = max(1, round(mon.maxhp * ph[cur + 1]['at']))
        bs['pending'] = cur + 1
        return True
    if mon.__dict__.get('maker'):
        from . import bossmaker as MK
        if MK.yields(game, mon):
            return True
    ar = arena_of(game, mon)
    if ar and any(game.map.tile(*c) == D.SHARD for c in ar.get('shards', ())):
        m = game.map
        if mon in m.mons:
            m.mons.remove(mon)
        mon.cast = None
        ar['rising'] = [3, mon]
        game.msg(f'{name_of(mon)} falls to dust... and the dust does not lie still. A shard ¤ glows in the dark.', 'bad')
        return True
    return False


def felled(game, mon):
    """It is dead: FOE FELLED, the way opens. A fallen helper may heal its master, or drop its banner."""
    m = game.map
    if getattr(mon, 'boss_of', None) is not None:
        boss = next((o for o in m.mons if o.id == mon.boss_of), None)
        if boss is not None and (st(boss) or {}).get('martyr'):
            boss.hp = min(cap_hp(boss), boss.hp + round(boss.maxhp * .08))
            game.msg(f'As it falls, light flows from it into {boss.the()}.', 'bad')
        if getattr(mon, 'job', None) == 'bearer' and m.tile(mon.x, mon.y) == D.FLOOR:
            m.set(mon.x, mon.y, D.BANNER)
            ar = m.__dict__.get('arena')
            if ar:
                ar['banner'] = (mon.x, mon.y)
            game.msg('The bearer falls, and the war banner stands where he planted it. Hack it down!', 'info')
    if mon.__dict__.get('twin'):
        twin_fell(game, mon)
        if twin_of(game, mon)[1] is not None and twin_of(game, mon)[1] in game.map.mons:
            return
    if st(mon) is None:
        return
    game.banner = ['FOE FELLED', None]
    if mon.__dict__.get('maker'):
        from . import bossmaker as MK
        MK.felled(game, mon)
    ar = game.map.__dict__.get('arena')
    if ar and ar.get('boss') == mon.id:
        open_up(game, ar, True)


# ------------------------------------------------------------------ the arena
def arena_of(game, mon):
    ar = game.map.__dict__.get('arena')
    return ar if ar and ar.get('boss') == mon.id else None


def may_stand(game, mon, x, y):
    """A boss with a room never leaves it."""
    ar = arena_of(game, mon)
    return not ar or (x, y) in ar['cells']


def boss_of(game):
    """The boss the bar is for: one that fights you now, or rises again."""
    m = game.map
    ar = m.__dict__.get('arena')
    if ar and ar.get('rising'):
        return ar['rising'][1]
    for o in m.mons:
        bs = st(o)
        if bs is not None and (bs['engaged'] or game.visible(o.x, o.y)) and (bs['engaged'] or not getattr(o, 'invis', 0)):
            if bs['engaged'] and not (ar and ar.get('boss') == o.id and ar.get('sealed')) and not game.visible(o.x, o.y) \
                    and not bs.get('air'):
                continue
            return o
    return None


def on_level(game, m):
    """The bottom of a place with a kit boss: its room becomes an arena behind a veil of mist. A theme boss at the
    bottom of its nest fights with its kit too."""
    d = game.world.dungeons.get(getattr(m, 'did', None))
    for o in m.mons:
        if d is not None and o.k == d.boss and o.k in KITS and not o.is_npc:
            arm(o)
    boss = next((o for o in m.mons if st(o) is not None and not o.__dict__.get('roam')), None)
    if boss is None:
        return
    if getattr(m, 'hall_cells', None):
        hall(game, m, boss)
        return
    build(game, m, boss)


def hall(game, m, boss):
    """The Lord of Cinders' hall of black iron is its own arena: the door shuts behind you."""
    cells = {(i % m.w, i // m.w) for i in m.hall_cells if D.TILES[m.t[i]].walk}
    ring = {(x + a, y + b) for x, y in cells for a, b in D8} - cells
    gates = sorted(c for c in ring if m.inb(*c) and D.TILES[m.tile(*c)].walk)
    if not gates:
        return
    orig = {c: m.tile(*c) for c in gates}
    for c in gates:
        m.set(c[0], c[1], D.VEIL)
    m.arena = dict(boss=boss.id, cells=sorted(cells), gates=gates, orig=orig, sealed=False, rotten=None, hits=0,
                   home=(boss.x, boss.y), shards=[], pillars=[c for c in cells if m.tile(*c) == D.PILLAR], dark=False,
                   dance=None, flees=0, rising=None, done=False)


def build(game, m, boss):
    from . import worldgen as W
    cells = None
    rof = getattr(m, 'room_of', None)
    if rof is not None:
        rid = rof[boss.y * m.w + boss.x]
        if rid != 255:
            cells = {(i % m.w, i // m.w) for i, r in enumerate(rof) if r == rid and D.TILES[m.t[i]].walk}
            if not 30 <= len(cells) <= 1400 or any(m.tile(*c) in (D.UP, D.DOWN) for c in cells):
                cells = None
    if cells is None:                                       # no room: a chamber round it, dug out
        blob = {(x, y) for y in range(boss.y - 4, boss.y + 5) for x in range(boss.x - 6, boss.x + 7)
                if 2 <= x < m.w - 2 and 2 <= y < m.h - 2 and ((x - boss.x) / 6.5) ** 2 + ((y - boss.y) / 4.5) ** 2 <= 1}
        near = {(x + a, y + b) for x, y in blob for a in (-1, 0, 1) for b in (-1, 0, 1)}
        if any(m.inb(*c) and m.tile(*c) in (D.UP, D.DOWN) for c in near):
            return None
        for x, y in blob:
            if not D.TILES[m.tile(x, y)].walk:
                m.set(x, y, D.FLOOR)
        cells = {c for c in blob if D.TILES[m.tile(*c)].walk}
    ring = {(x + a, y + b) for x, y in cells for a, b in D8} - cells
    gates = sorted(c for c in ring if m.inb(*c) and (D.TILES[m.tile(*c)].walk or D.TILES[m.tile(*c)].door))
    if not gates:
        return
    ups = [i for i, t in enumerate(m.t) if t == D.UP]
    if not ups:
        return
    ux, uy = ups[0] % m.w, ups[0] // m.w
    orig = {}
    for c in gates:
        orig[c] = m.tile(*c)
        m.set(c[0], c[1], D.VEIL)
    for o in [o for o in m.mons if (o.x, o.y) in gates]:
        sp = [s for s in free_around(game, m, o.x, o.y, 2) if s not in gates]
        if sp:
            o.x, o.y = sp[0]
    ar = dict(boss=boss.id, cells=sorted(cells), gates=gates, orig=orig, sealed=False, rotten=None, hits=0,
              home=(boss.x, boss.y), shards=[], pillars=[], dark=False, dance=None, flees=0, rising=None, done=False)
    m.arena = ar
    # the one hard way out: a rotten wall, with a short way dug behind it to the rest of the level
    from collections import deque
    dist = W.bfs(m, ux, uy, lambda t: D.TILES[t].walk or D.TILES[t].door or t == D.VEIL)
    shut = cells | ring
    srcs = [c for c in ring if c not in gates and m.inb(*c) and 1 <= c[0] < m.w - 1 and 1 <= c[1] < m.h - 1
            and min(cheb(*c, *g) for g in gates) >= 4
            and any((c[0] + a, c[1] + b) in cells for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    random.shuffle(srcs)
    par = {c: None for c in srcs}
    q = deque((c, 0) for c in srcs)
    end_ = None
    while q:
        (x, y), k = q.popleft()
        if k >= 16:
            continue
        for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            c = (x + a, y + b)
            if c in par or c in shut or not (1 <= c[0] < m.w - 1 and 1 <= c[1] < m.h - 1):
                continue
            par[c] = (x, y)
            if dist[c[1] * m.w + c[0]] >= 0 and D.TILES[m.tile(*c)].walk:
                end_ = c
                q.clear()
                break
            if m.tile(*c) in (D.UP, D.DOWN) or D.TILES[m.tile(*c)].door:
                continue
            q.append((c, k + 1))
    if end_ is not None:
        c = par[end_]
        while par[c] is not None:
            m.set(c[0], c[1], D.FLOOR)
            c = par[c]
        m.set(c[0], c[1], D.ROTTEN)
        ar['rotten'] = c
    furnish(game, m, boss, ar)


def _inner(m, ar, c, room, gap=2):
    x, y = c
    return all((x + a, y + b) in room for a in range(-gap, gap + 1) for b in range(-gap, gap + 1)) \
        and m.tile(x, y) == D.FLOOR and min(cheb(x, y, *g) for g in ar['gates']) > 2


def furnish(game, m, boss, ar):
    """What the kit's room holds: the hoard, the shards of the phylactery, the pillars of the dragon's cave."""
    room = set(ar['cells'])
    things = kit(boss).get('things')
    bx, by = boss.x, boss.y
    inner = [c for c in ar['cells'] if _inner(m, ar, c, room, 1) and cheb(*c, bx, by) >= 2]
    random.shuffle(inner)
    if things == 'hoard':
        for c in inner[:3]:
            m.set(c[0], c[1], D.GLITTER)
    elif things in ('holes', 'pool'):                       # rat holes or chains in the walls round the room
        ring = sorted({(x + a, y + b) for x, y in room for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))} - room)
        ring = [c for c in ring if m.inb(*c) and m.tile(*c) in (D.WALL, D.ROCK) and c not in ar['gates']
                and c != (tuple(ar['rotten']) if ar['rotten'] else None)]
        random.shuffle(ring)
        got = []
        for c in ring:
            if len(got) >= 4:
                break
            if all(cheb(*c, *q) >= 5 for q in got):
                got.append(c)
        for c in got:
            m.set(c[0], c[1], D.RATHOLE if things == 'holes' else D.BCHAIN)
        ar['holes' if things == 'holes' else 'chains'] = got
        if things == 'pool':
            edge = [c for c in inner if any((c[0] + a, c[1] + b) not in room for a, b in D8)] or inner
            ledges = []
            for c in sorted(edge, key=lambda c: -cheb(*c, bx, by)):
                if len(ledges) >= 4:
                    break
                if all(cheb(*c, *q) >= 4 for q in ledges):
                    ledges.append(c)
            for c in ledges:
                m.set(c[0], c[1], D.BLEDGE)
            ar['water'] = 1
            flood(game, ar, m)
    elif things == 'props':
        pts = []
        for c in inner:
            if all(cheb(*c, *q) >= 4 for q in pts) and cheb(*c, bx, by) >= 2 and _inner(m, ar, c, room, 1):
                pts.append(c)
        for c in pts[:8]:
            m.set(c[0], c[1], D.PROP)
        ar['props'] = pts[:8]
    elif things == 'nest':
        from . import spellmap as SM
        SM.area(game, m, inner[:max(4, len(inner) // 10)], D.WEBS, 400)
        for c in [c for c in inner if 2 <= cheb(*c, bx, by) <= 3][:2]:
            m.set(c[0], c[1], D.EGGS)
            BM.eggs(game, m)[c] = [40, boss.id]
    elif things in ('tomb', 'lair', 'pillars'):
        # cover spread over the room, so that from anywhere a pillar or a shard is a few steps away
        for gap in (5, 4, 3):                               # a small room: the cover stands closer together
            pts = []
            for c in sorted(inner, key=lambda c: (c[0] // 6 + c[1] // 5) % 2):
                if all(cheb(*c, *q) >= gap for q in pts) and cheb(*c, bx, by) >= 3 and _inner(m, ar, c, room, 1):
                    pts.append(c)
            if len(pts) >= 6:
                break
        pts = pts[:12]
        random.shuffle(pts)
        if things == 'tomb':
            shards = sorted(pts, key=lambda c: -cheb(*c, bx, by))[:4]
            for c in shards:
                m.set(c[0], c[1], D.SHARD)
            ar['shards'] = shards
            pillars = [c for c in pts if c not in shards]
            sl = m.__dict__.setdefault('slain', [])
            for c in [c for c in inner if c not in pts][:3]:
                sl.append(('skeleton', c[0], c[1], boss.lvl))
        else:
            pillars = pts
            for c in [c for c in inner if cheb(*c, bx, by) == 2 and c not in pts][:2 if things == 'lair' else 0]:
                m.set(c[0], c[1], D.GLITTER)
        for c in pillars:
            m.set(c[0], c[1], D.PILLAR)
        ar['pillars'] = pillars
    # nothing in the room may cut the way through it
    from . import worldgen as W
    ups = [i for i, t in enumerate(m.t) if t == D.UP]
    if ups:
        dist = W.bfs(m, ups[0] % m.w, ups[0] // m.w, lambda t: D.TILES[t].walk or D.TILES[t].door or t == D.VEIL)
        for c in ar['cells']:
            if m.tile(*c) in (D.GLITTER, D.PILLAR, D.SHARD, D.PROP, D.BLEDGE) and not any(
                    dist[g[1] * m.w + g[0]] >= 0 for g in ar['gates']):
                m.set(c[0], c[1], D.FLOOR)


def seal(game, ar):
    m = game.map
    if ar['sealed'] or ar['done']:
        return
    ar['sealed'] = True
    room = set(ar['cells'])
    for c in ar['gates']:
        o = m.mon_at(*c)
        if o is not None:
            sp = [s for s in free_around(game, m, *c, 2) if s in room]
            if sp:
                o.x, o.y = sp[0]
        m.set(c[0], c[1], D.SEALED)
    game.msg('Behind you the way crashes shut. Stones fill it from floor to roof!', 'bad')
    game.shake()
    from . import guide as GD
    GD.tip(game, 'shut')


def open_up(game, ar, fell):
    """The veil lifts when it falls (or the room opens again when you fled)."""
    m = game.map
    ar['sealed'] = False
    for c in ar['gates']:
        if m.tile(*c) in (D.SEALED, D.VEIL):
            m.set(c[0], c[1], ar['orig'].get(tuple(c), D.FLOOR) if fell else D.VEIL)
    if fell:
        ar['done'] = True
        ar['dark'] = ar['fog'] = False
        ar['dance'] = ar['ceiling'] = ar['wind'] = None
        ar['falling'] = []
        game.msg('The stones in the way crumble, and the mist is gone.', 'info')
    elif ar['rotten'] and m.tile(*ar['rotten']) == D.FLOOR and not game.occupied(m, *ar['rotten']):
        m.set(ar['rotten'][0], ar['rotten'][1], D.ROTTEN)
        ar['hits'] = 0


def no_rest(game):
    ar = game.map.__dict__.get('arena')
    p = game.player
    return bool(ar and ar['sealed'] and (p.x, p.y) in set(map(tuple, ar['cells'])))


def sight(game, r):
    ar = game.map.__dict__.get('arena')
    if ar and ar.get('fog') and ar['sealed']:
        return min(r, 2)
    if ar and ar.get('dark') and ar['sealed']:
        return min(r, 3)
    return r


def bump(game, x, y, t):
    """The veil asks once; the rotten wall gives after five blows; a shard breaks."""
    from . import events as EV
    m = game.map
    ar = m.__dict__.get('arena')
    if not ar:
        return None
    if t == D.VEIL:
        if (game.player.x, game.player.y) in set(map(tuple, ar['cells'])):
            return None                                       # from the inside it is only mist
        if ar.get('asked'):
            return None
        EV.ask(game, 'boss_veil', 'A veil of mist', 'A grey mist hangs in the way, still as a curtain, and the air '
               'beyond it is cold. Something waits on the other side. Once through, there may be no way back.',
               [('Step through the mist', 'go'), ('Stay back', 'bye')], cell=(x, y))
        return 0
    if t == D.ROTTEN:
        if not ar['sealed']:
            game.msg('The wall here is soft and black with rot.', 'info')
            return 0
        ar['hits'] += 1
        if ar['hits'] >= 5:
            m.set(x, y, D.FLOOR)
            game.msg('The rotten wall gives way! There is a way out.', 'good')
        else:
            game.msg(f'You hammer at the rotten wall. It gives a little. ({ar["hits"]}/5)', 'info')
        return 1
    if t == D.SHARD:
        m.set(x, y, D.DARKSHARD)
        game.msg('You smash the phylactery shard. Somewhere in the tomb a voice cries out.', 'good')
        game.shake()
        return 1
    if t == D.SEALED:
        game.msg('Fallen stones fill the way. It will not open while the fight goes on.', 'info')
        return 0
    if t == D.RATHOLE:
        m.set(x, y, D.RUBBLE)
        game.msg('You kick stones into the rat hole until it is stopped up.', 'good')
        return 1
    if t == D.BCHAIN:
        ar['chain_hits'] = ar.get('chain_hits', 0) + 1
        if ar['chain_hits'] % 2:
            game.msg('You strike the great chain. A link cracks.', 'info')
        else:
            m.set(x, y, D.WALL)
            ar['water'] = max(0, ar.get('water', 0) - 1)
            flood(game, ar)
            game.msg('The chain breaks with a sound like a bell! Somewhere a sluice opens, and the water sinks.', 'good')
            game.shake()
        return 1
    if t == D.BANNER:
        m.set(x, y, D.FLOOR)
        game.msg('You hack the war banner down. The band falters.', 'good')
        return 1
    if t == D.PROP:
        game.msg('A pit prop. It holds up the roof here.', 'info')
        return 0
    return None


def r_veil(game, choice, ctx):
    if choice != 'go':
        return
    m, p = game.map, game.player
    ar = m.__dict__.get('arena')
    x, y = ctx['cell']
    if ar is None or game.occupied(m, x, y):
        return
    ar['asked'] = True
    p.x, p.y = x, y
    boss = next((o for o in m.mons if o.id == ar['boss']), None)
    if boss is not None and st(boss) and st(boss)['prep']:
        game.msg(f'{name_of(boss)} is waiting for you. {fill("{He}", boss)} has made ready this time.', 'bad')
    else:
        game.msg('You step through the mist. It closes behind you like cold water.', 'info')
    game.end_turn(1)


def tick(game):
    """Each turn on a map with an arena: fled from, the boss heals and makes ready; the dead lich rises; the floor
    burns in strips."""
    m, p = game.map, game.player
    floor_things(game)
    roamers(game)
    ar = m.__dict__.get('arena')
    if not ar or ar['done']:
        return
    room = set(map(tuple, ar['cells']))
    if ar['sealed'] and (p.x, p.y) not in room and (p.x, p.y) not in set(map(tuple, ar['gates'])) \
            and (p.x, p.y) != (tuple(ar['rotten']) if ar['rotten'] else None):
        fled(game, ar)
        return
    if ar.get('rising'):
        rs = ar['rising']
        rs[0] -= 1
        if rs[0] <= 0:
            mon = rs[1]
            ar['rising'] = None
            shard = next((c for c in ar['shards'] if m.tile(*c) == D.SHARD), None)
            spot = ar['home'] if not game.occupied(m, *ar['home']) else (free_around(game, m, *ar['home'], 3) or [ar['home']])[0]
            mon.x, mon.y = spot
            m.mons.append(mon)
            if shard:
                m.set(shard[0], shard[1], D.DARKSHARD)
                mon.hp = max(1, mon.maxhp // 4)
                game.msg(f'The dust gathers and stands. {name_of(mon)} rises again! A shard goes dark.', 'bad')
                game.shake()
            else:
                mon.hp = 0
                game.msg('The dust stirs, and falls still. There is nothing left to call it back.', 'good')
                game.kill(mon)
    if ar.get('dance') is not None and ar['sealed']:
        _dance(game, ar, room)
    if not ar['sealed']:
        return
    boss = next((o for o in m.mons if o.id == ar['boss']), None)
    if ar.get('ceiling') is not None:
        _ceiling(game, ar, room)
    if ar.get('wind') and not game.dead:
        _wind(game, ar, room)
    if boss is not None and st(boss) is not None:
        bs = st(boss)
        if bs.get('duel'):
            from . import mercs as MC
            if any(mc.body is not None and mc.body in m.mons and mc.order not in ('hold', 'passive')
                   and cheb(mc.body.x, mc.body.y, boss.x, boss.y) <= 1 for mc in MC.party(game)):
                break_duel(game, boss, 'Your company steps in. The duel is broken, and the guard comes on!')
        flag = [o for o in helpers(game, boss) if o.job == 'bearer'] or \
            ([] if not ar.get('banner') or m.tile(*ar['banner']) != D.BANNER else [ar['banner']])
        if flag:
            fx, fy = (flag[0].x, flag[0].y) if not isinstance(flag[0], tuple) else flag[0]
            for o in helpers(game, boss):
                if cheb(o.x, o.y, fx, fy) <= 4 and not getattr(o, 'watching', False):
                    o.effects['frenzy'] = [2, 0]


def floor_things(game):
    """Webs that hold, thorns that cut, eggs that hatch unless you tread on them."""
    from . import spellmap as SM
    from .behave import give
    m, p = game.map, game.player
    t = m.tile(p.x, p.y)
    if t == D.WEBS:
        SM.clear(m, (p.x, p.y))
        if give(game, 'held', 2):
            p.held_by = None
            game.msg('You walk into a web on the floor. It holds you fast!', 'bad')
    elif t == D.BRAMBLE and getattr(m, 'arena', None) and m.arena.get('sealed'):
        fd = SM.fields(m).get((p.x, p.y))
        game.hurt(max(1, fd[3] if fd else 2), 'thorns')
    eg = m.__dict__.get('boss_eggs')
    if not eg:
        return
    from .entities import make_monster
    for c, v in list(eg.items()):
        if (p.x, p.y) == tuple(c):
            eg.pop(c)
            m.set(c[0], c[1], D.FLOOR)
            game.msg('You tread the eggs into the floor. They burst with a wet crunch.', 'good')
            continue
        v[0] -= 1
        if v[0] > 0:
            continue
        eg.pop(c)
        m.set(c[0], c[1], D.FLOOR)
        boss = next((o for o in m.mons if o.id == v[1]), None)
        lvl = boss.lvl if boss else getattr(m, 'level', 3)
        for sp in [c] + free_around(game, m, c[0], c[1], 1)[:1]:
            if not game.occupied(m, *sp):
                o = make_monster(game, 'spiderling', sp[0], sp[1], max(1, lvl - 3))
                o.awake = o.called = True
                if boss is not None:
                    o.job, o.boss_of = 'swarm', boss.id
                m.mons.append(o)
        if game.visible(*c):
            game.msg('The eggs split open. Spiderlings spill out!', 'bad')


def flood(game, ar, m=None):
    """The water stands as high as `ar['water']` says: bands of the room from its low side, shallow, then deep.
    m: the map, when the room is made before you stand on it."""
    here = m is None
    m = m or game.map
    lv = ar.get('water', 0)
    room = [tuple(c) for c in ar['cells']]
    if not room:
        return
    dry = ar.setdefault('dry', {})
    if not ar.get('low'):
        hx, hy = ar['home']
        xs, ys = [c[0] for c in room], [c[1] for c in room]
        sides = {'n': hy - min(ys), 's': max(ys) - hy, 'w': hx - min(xs), 'e': max(xs) - hx}
        ar['low'] = max(sides, key=sides.get)
    lo = ar['low']
    xs, ys = [c[0] for c in room], [c[1] for c in room]
    edge = {'n': min(ys), 's': max(ys), 'w': min(xs), 'e': max(xs)}[lo]
    for c in room:
        t = m.tile(*c)
        if c not in dry:
            if t != D.FLOOR:
                continue
            dry[c] = t
        if t not in (D.FLOOR, D.SHALLOW, D.WATER):
            continue
        i = abs((c[1] if lo in 'ns' else c[0]) - edge)
        want = D.WATER if i < 2 * (lv - 2) else D.SHALLOW if lv and i < 2 * lv + 1 else dry[c]
        o = m.mon_at(*c)
        if want == D.WATER and (o is not None or (here and (game.player.x, game.player.y) == c)):
            want = D.SHALLOW
        if t != want:
            m.set(c[0], c[1], want)


def _ceiling(game, ar, room):
    """The falling roof: two stones marked one turn, falling the next, never beside a prop that still stands."""
    m, p = game.map, game.player
    ar['ceiling'] += 1
    if ar['ceiling'] % 2 == 1:
        props = [c for c in ar.get('props', ()) if m.tile(*c) == D.PROP]
        ok = [c for c in room if m.tile(*c) == D.FLOOR and not any(cheb(*c, *q) <= 1 for q in props)]
        near = [c for c in ok if cheb(*c, p.x, p.y) <= 2]
        pick = random.sample(near, 1) if near else []
        rest = [c for c in ok if c not in pick]
        pick += random.sample(rest, min(1, len(rest)))
        ar['falling'] = pick
        return
    lvl = getattr(m, 'level', 8)
    for c in ar.get('falling', ()):
        if m.tile(*c) == D.FLOOR and not game.occupied(m, *c):
            m.set(c[0], c[1], D.FALLEN)
        if (p.x, p.y) == tuple(c) and not game.dead:
            game.msg('A stone falls from the roof on to you!', 'bad')
            game.spare_full = True
            game.hurt(.12 * ref_life(game, lvl, game.stats()['max_life']), 'a falling stone')
            game.__dict__.pop('spare_full', None)
    game.flash([tuple(c) for c in ar.get('falling', ()) if game.visible(*c)], (180, 160, 130), '*', .2)
    ar['falling'] = []


def _wind(game, ar, room):
    """A wind that will not stop pushes you a step, unless you stand by something that breaks it."""
    m, p = game.map, game.player
    dx, dy = ar['wind']
    if any(m.inb(p.x + a, p.y + b) and D.TILES[m.tile(p.x + a, p.y + b)].opaque for a, b in D8):
        return
    nx, ny = p.x + dx, p.y + dy
    if (nx, ny) in room and D.TILES[m.tile(nx, ny)].walk and not game.occupied(m, nx, ny):
        p.x, p.y = nx, ny
        if game.turn % 4 == 0:
            game.msg('The wind shoves you along the floor.', 'bad')


def _dance(game, ar, room):
    """The burning floor: every other turn a strip of the floor is marked, and the next turn it burns."""
    from . import spellmap as SM
    m = game.map
    ar['dance'] += 1
    k = ar['dance']
    rows = sorted({c[1] for c in room})
    if not rows:
        return
    if k % 2 == 1:
        band = (k // 2) % 3
        ar['strip'] = [c for c in room if (c[1] - rows[0]) % 3 == band and D.TILES[m.tile(*c)].walk]
    else:
        lvl = getattr(m, 'level', 10)
        for c in ar.get('strip', ()):
            SM.place(game, m, c[0], c[1], D.BURNING, 1, 3 + lvl // 3)
        ar['strip'] = []


def fled(game, ar):
    """You got out. It heals, and makes ready against what you did (Shadow of Mordor), up to four times."""
    m = game.map
    boss = next((o for o in m.mons if o.id == ar['boss']), None)
    open_up(game, ar, False)
    ar['asked'] = False
    ar['flees'] += 1
    ar['dark'] = ar['fog'] = False
    ar['dance'] = ar['ceiling'] = ar['wind'] = None
    ar['falling'] = []
    if boss is None:
        return
    bs = st(boss)
    boss.hp = boss.maxhp
    boss.cast = None
    boss.threat = {}
    boss.x, boss.y = ar['home'] if not game.occupied(m, *ar['home']) else (boss.x, boss.y)
    bs.update(phase=0, pending=None, i=0, piles={}, spent=0, stag=0, dots=0, stun=0, resolve=RESOLVE, engaged=False,
              lichcraft=False, air=False, fed=0, guard={}, duel=False, enrage=False, martyr=False, shed=False)
    if ar.get('water') is not None and 'chains' in ar:
        ar['water'] = 1
        flood(game, ar)
    boss.invis = 0
    if len(bs['prep']) < MAX_PREP:
        took = bs['took']
        tot = sum(took.values()) or 1
        el = max((k for k in took if k in ('fire', 'cold', 'lightning', 'poison')), key=lambda k: took[k], default=None)
        if el and took[el] / tot >= .4 and f'res:{el}' not in bs['prep']:
            bs['prep'].append(f'res:{el}')
            boss.weak_res = dict(getattr(boss, 'weak_res', {}), **{el: 50})
        elif bs['breaks'] >= 2 and 'unbroken' not in bs['prep']:
            bs['prep'].append('unbroken')
        elif 'helper' not in bs['prep']:
            bs['prep'].append('helper')
        elif 'phase2' not in bs['prep']:
            bs['prep'].append('phase2')
    if 'phase2' in bs['prep'] and len(phases(boss)) > 2:
        _phase(game, boss, 1, False)
    bs['took'], bs['breaks'] = {}, 0
    game.msg(f'You hear {boss.the()} behind you, and then nothing. {fill("{He}", boss)} will be ready for you.', 'bad')


def break_pillar(game, mon):
    m = game.map
    ar = arena_of(game, mon)
    if not ar:
        return
    left = [c for c in ar['pillars'] if m.tile(*c) == D.PILLAR]
    if not left:
        return
    c = random.choice(left)
    m.set(c[0], c[1], D.FALLEN)
    game.msg('With a crack like thunder a pillar breaks and falls.', 'bad')
    game.shake()


# ------------------------------------------------------------------ your company in a boss fight
def marked(game):
    """Every cell a loading blow will strike, on this map."""
    out = set()
    for o in game.map.mons:
        c = o.__dict__.get('cast')
        if c:
            out |= set(map(tuple, c['cells']))
    return out


def ally_turn(game, mc, b):
    """Your hireling or beast plays it like you: out of the red, a shield into a loading boss. Better with rank."""
    m = game.map
    if mc.order in ('hold', 'passive'):
        return False
    red = marked(game)
    rank = getattr(mc, 'lvl', 1)
    good = min(.95, (.45 if mc.kind == 'beast' else .55) + rank * .04)
    if red and (b.x, b.y) in red:
        if mc.kind == 'defender' and mc.gear.get('shield') and cheb(b.x, b.y, game.player.x, game.player.y) <= 1 \
                and random.random() < .4:
            b.braced = True
            game.msg(f'{mc.name} sets {mc.his()} shield and braces.', 'info')
            return True
        if random.random() < good:
            room = m.__dict__.get('arena')
            cells = set(map(tuple, room['cells'])) if room and room.get('sealed') else None
            spots = [c for c in free_around(game, m, b.x, b.y, 1) if c not in red and (cells is None or c in cells)]
            if spots:
                b.x, b.y = random.choice(spots)
                game.msg(f'{mc.name} steps out of the red.', 'info')
                return True
        game.msg(f'{mc.name} does not move in time.', 'bad')
        return False
    for o in m.mons:
        c = o.__dict__.get('cast')
        if c and c['brk'] and cheb(o.x, o.y, b.x, b.y) <= 1 and mc.kind == 'defender' and mc.gear.get('shield') \
                and mc.cd == 0 and random.random() < good * .6:
            mc.cd = 5
            game.msg(f'{mc.name} smashes {mc.his()} shield into {o.the()}.', 'good')
            do_break(game, o, '')
            return True
    return False


def ally_target(game, mc, b, foes):
    """A spent or staggered boss first; then the warder, the mender, the channeler."""
    if mc.order in ('passive', 'hold', 'defend', 'attack'):
        return None
    for o in foes:
        bs = st(o)
        if bs and (bs['spent'] or bs['stag']) and cheb(o.x, o.y, b.x, b.y) <= 8:
            return o
    for job in ('warder', 'mender', 'channeler'):
        hs = [o for o in foes if getattr(o, 'job', None) == job and cheb(o.x, o.y, b.x, b.y) <= 8]
        if hs:
            return min(hs, key=lambda o: cheb(o.x, o.y, b.x, b.y))
    return None


# ------------------------------------------------------------------ what you see
def marks(game):
    """{(x, y): (number or None, its colour, hot)} for the map: the red ground, and the count where it loads long."""
    out = {}
    for o in game.map.mons:
        c = o.__dict__.get('cast')
        if not c:
            continue
        mv = MOVES[c['mv']]
        col = PURPLE if c['brk'] else RED
        num = str(c['left']) if c.get('load', mv.get('load', 1)) >= 2 else None
        hot = c['left'] <= 1
        cells = c['cells']
        if mv.get('shape') == 'mark':
            cells = [_target_xy(game, o, c)]
        for cc in cells:
            out[tuple(cc)] = (num, col, hot)
        for cc in c.get('gold', ()):
            out[tuple(cc)] = (num, GOLDN, False)
    ar = game.map.__dict__.get('arena')
    if ar:
        for cc in list(ar.get('strip') or ()) + list(ar.get('falling') or ()):
            out.setdefault(tuple(cc), (None, RED, True))
    return out


def casting(o):
    return bool(o.__dict__.get('cast'))


def bar(game, mon):
    """What the bar under its name says: (phase, thresholds, state, colour, resolve, dots)."""
    bs = st(mon)
    ph = phases(mon)
    c = mon.__dict__.get('cast')
    ar = arena_of(game, mon)
    if ar and ar.get('rising'):
        state, col = f'Rising: {ar["rising"][0]}', RED
    elif c:
        left = c['left']
        state, col = f'Charging: {MOVES[c["mv"]]["name"]} {left}', PURPLE if c['brk'] else RED
    elif bs['stag']:
        state, col = 'Staggered', GOLDN
    elif bs['spent']:
        state, col = 'Spent', GOLDN
    elif bs.get('air'):
        state, col = 'Aloft', RED
    elif warded(game, mon):
        state, col = 'Warded', (160, 200, 255)
    else:
        state, col = '', None
    return dict(phase=ROMAN[min(bs['phase'], 3)], marks=[p_['at'] for p_ in ph[1:]], state=state, col=col,
                resolve=bs['resolve'], dots=bs['dots'])


def stance(game, mon):
    """A line in the look about how it stands: it changes with the next beat. It never says what it means."""
    bs = st(mon)
    if bs is None:
        return None
    if mon.__dict__.get('cast'):
        return None
    ph = phases(mon)[bs['phase']]
    role = ph['beat'][bs['i'] % len(ph['beat'])]
    return fill(STANCE.get(role, STANCE['k']), mon)


def rhythm(mon):
    """For the test build: the beat of its phase, and where it stands in it."""
    bs = st(mon)
    if bs is None:
        return ''
    pat = phases(mon)[bs['phase']]['beat']
    i = bs['i'] % len(pat)
    return f'{pat[:i]}[{pat[i]}]{pat[i + 1:]}'


# ------------------------------------------------------------------ twins
# Two bosses in one fight (Twin Emperors, Ornstein and Smough, the Swine Prince): mon.twin = dict(kind, other, role).
TWINS = {'shared': 'one life for two', 'survivor': 'the survivor takes all', 'opposites': 'opposites',
         'swap': 'they swap places', 'bound': 'bound together', 'master': 'master and beast'}


def link(a, b, kind):
    a.twin = dict(kind=kind, other=b.id, role='a')
    b.twin = dict(kind=kind, other=a.id, role='b')


def twin_of(game, mon):
    tw = mon.__dict__.get('twin')
    if not tw:
        return None, None
    return tw, next((o for o in game.map.mons if o.id == tw['other']), None)


def twin_blow(game, mon, dmg, weapon):
    """Opposites: one shrugs off weapons, the other spells. Shared life: the blow is felt by both."""
    tw, other = twin_of(game, mon)
    if not tw:
        return dmg
    if tw['kind'] == 'opposites' and (weapon if tw['role'] == 'a' else not weapon):
        dmg = max(1, round(dmg * .5))
    if tw['kind'] == 'shared' and other is not None:
        other.hp = max(1, other.hp - dmg)
    return dmg


def twin_turn(game, mon):
    """Bound together they mend each other, far apart they rage; every sixth turn the pair may swap places."""
    tw, other = twin_of(game, mon)
    if not tw or other is None:
        return
    if tw['kind'] == 'bound':
        if cheb(mon.x, mon.y, other.x, other.y) <= 1:
            mon.hp = min(cap_hp(mon), mon.hp + max(1, mon.maxhp // 100))
        elif cheb(mon.x, mon.y, other.x, other.y) > 6:
            mon.effects['frenzy'] = [2, 0]
    elif tw['kind'] == 'swap' and tw['role'] == 'a':
        if game.turn % 6 == 5:
            game.flash([(mon.x, mon.y), (other.x, other.y)], (206, 132, 255), '!', .4)
        elif game.turn % 6 == 0:
            mon.x, mon.y, other.x, other.y = other.x, other.y, mon.x, mon.y
            for o in helpers(game, mon) + helpers(game, other):
                o.awake = True
            if game.visible(mon.x, mon.y) or game.visible(other.x, other.y):
                game.msg(f'{name_of(mon)} and {other.the()} swap places in a flicker!', 'bad')


def twin_fell(game, mon):
    """One of the pair is dead: what becomes of the other."""
    tw, other = twin_of(game, mon)
    if not tw or other is None:
        return
    ar = game.map.__dict__.get('arena')
    if ar and ar.get('boss') == mon.id and tw['kind'] != 'shared':
        ar['boss'] = other.id                                # the room is the survivor's now
    k = tw['kind']
    if k == 'shared':
        other.hp = 0
        other.twin = None
        game.kill(other)
    elif k == 'survivor':
        other.hp = other.maxhp
        bo = st(other)
        z = next((c for ph in phases(mon) for c in ph['cards'].get('Z', ())), None)
        if bo is not None and z:
            bo['stolen'] = z
        game.msg(f'{other.the()[0].upper() + other.the()[1:]} takes up the strength of the fallen, and is whole again!', 'bad')
    elif k == 'master':
        if tw['role'] == 'b':
            other.effects['frenzy'] = [999, 0]
            game.msg(f'{other.the()[0].upper() + other.the()[1:]} howls over the body, mad with rage!', 'bad')
        else:
            other.effects['frenzy'] = [999, 0]
            if st(other) is not None:
                st(other)['wild'] = True
            game.msg(f'{other.the()[0].upper() + other.the()[1:]} goes wild, with no one to hold it back.', 'bad')
    other.twin = None


# ------------------------------------------------------------------ roaming bosses
COMPASS = {(0, -1): 'north', (1, -1): 'north-east', (1, 0): 'east', (1, 1): 'south-east', (0, 1): 'south',
           (-1, 1): 'south-west', (-1, 0): 'west', (-1, -1): 'north-west'}


def place_roamer(game, m, d, lvl, up):
    """Halfway down a place that is not small, now and then a boss walks the level with its band."""
    from .entities import make_monster
    from . import worldgen as W
    kinds = [k for k in ROAMERS.get(d.tag, ()) if k in D.MONSTERS]
    if not kinds:
        return None
    k = random.choice(kinds)
    c = W.rand_free(game, m, lambda t: t == D.FLOOR, (up[0], up[1], 20))
    if not c:
        return None
    o = make_monster(game, k, c[0], c[1], lvl + 1)
    arm(o)
    o.roam = dict(seen=-999, goal=None, path=[], heard=0, hunted=False)
    m.mons.append(o)
    band = W.band_keys(k, 3) if D.MONSTERS[k].get('chief') else [W.choose_monster(lvl, d.tag) for _ in range(2)]
    for bk, sp in zip(band, free_around(game, m, c[0], c[1], 2)):
        if bk in D.MONSTERS and not D.MONSTERS[bk].get('boss'):
            b = make_monster(game, bk, sp[0], sp[1], lvl)
            b.job, b.boss_of = 'guard', o.id
            m.mons.append(b)
    return o


def hunting(game, mon):
    """It knows where you are: it saw you, or heard you close by, not long ago."""
    r = mon.roam
    p = game.player
    if game.visible(mon.x, mon.y) or cheb(mon.x, mon.y, p.x, p.y) <= 5:
        if not r.get('hunted'):
            r['hunted'] = True
            mon.awake = True
            for o in helpers(game, mon):
                o.awake = True
        r['seen'] = game.turn
    on = game.turn - r.get('seen', -999) < 300
    if not on and r.get('hunted'):                          # it lost you: it heals, and waits by the stair
        r['hunted'] = False
        mon.hp = mon.maxhp
        bs = st(mon)
        bs.update(phase=0, pending=None, i=0, piles={}, engaged=False, guard={})
        stairs = [i for i, t in enumerate(game.map.t) if t in (D.UP, D.DOWN)]
        if stairs:
            i = random.choice(stairs)
            r['goal'], r['path'] = (i % game.map.w, i // game.map.w), []
    return on


def patrol(game, mon):
    """It walks from hall to hall, and leaves its tracks."""
    from . import worldgen as W
    m = game.map
    r = mon.roam
    if r.get('t') == game.turn:
        return
    r['t'] = game.turn
    heard(game, mon)
    if not r.get('path'):
        goal = r.get('goal')
        if goal is None or cheb(mon.x, mon.y, *goal) <= 1:
            goal = W.rand_free(game, m, lambda t: t == D.FLOOR, (mon.x, mon.y, 15))
        r['goal'] = goal
        r['path'] = path_to(m, (mon.x, mon.y), goal) if goal else []
        r['goal'] = None if not r['path'] else goal
        return
    if game.turn % 2:
        return                                               # it walks slowly when it does not hunt
    nx, ny = r['path'][0]
    if game.occupied(m, nx, ny) or not D.TILES[m.tile(nx, ny)].walk:
        if D.TILES[m.tile(nx, ny)].door or m.tile(nx, ny) == D.DOOR:
            m.set(nx, ny, D.ODOOR)
        r['path'] = []
        return
    r['path'].pop(0)
    ox, oy = mon.x, mon.y
    mon.x, mon.y = nx, ny
    if m.kind == 'dungeon' and random.random() < .5:
        if getattr(m, 'deco', None) is None:
            m.deco = bytearray(m.w * m.h)
        i = oy * m.w + ox
        if not m.deco[i] and m.tile(ox, oy) == D.FLOOR:
            from .dress import TRACKS
            m.deco[i] = TRACKS


def path_to(m, a, b):
    from collections import deque
    if a == b:
        return []
    prev = {a: None}
    q = deque([a])
    while q:
        c = q.popleft()
        if c == b:
            break
        for dx, dy in D8:
            n = (c[0] + dx, c[1] + dy)
            if n in prev or not m.inb(*n):
                continue
            t = m.tile(*n)
            if not (D.TILES[t].walk or D.TILES[t].door):
                continue
            prev[n] = c
            q.append(n)
        if len(prev) > 6000:
            return []
    if b not in prev:
        return []
    out = []
    c = b
    while c != a:
        out.append(c)
        c = prev[c]
    return out[::-1][:200]


def heard(game, mon):
    """Now and then you hear it, from where it walks."""
    r = mon.roam
    p = game.player
    d = cheb(mon.x, mon.y, p.x, p.y)
    if game.visible(mon.x, mon.y) or d > 40 or game.turn < r.get('heard', 0):
        return
    r['heard'] = game.turn + random.randint(25, 45)
    dx, dy = (mon.x > p.x) - (mon.x < p.x), (mon.y > p.y) - (mon.y < p.y)
    where = COMPASS.get((dx, dy), 'somewhere')
    game.msg(random.choice(HEARD.get(mon.k, HEARD['troll'])).format(dir=where), 'info')


def step_to(game, mon, x, y):
    m = game.map
    best = None
    for dx, dy in D8:
        nx, ny = mon.x + dx, mon.y + dy
        if m.inb(nx, ny) and D.TILES[m.tile(nx, ny)].walk and not game.occupied(m, nx, ny) and may_stand(game, mon, nx, ny):
            d = cheb(nx, ny, x, y)
            if best is None or d < best[0]:
                best = (d, nx, ny)
    if best and best[0] < cheb(mon.x, mon.y, x, y):
        mon.x, mon.y = best[1], best[2]
        return True
    return False


def roamers(game):
    """Roamers walk their rounds, asleep to you or not; one that followed you down or up the stair comes after a
    few turns."""
    m = game.map
    for o in [o for o in m.mons if o.__dict__.get('roam')]:
        if not hunting(game, o):
            patrol(game, o)
    come = m.__dict__.get('coming')
    if not come:
        return
    for row in list(come):
        row[0] -= 1
        if row[0] > 0:
            continue
        come.remove(row)
        mon, at = row[1], tuple(row[2])
        sp = [at] if not game.occupied(m, *at) else free_around(game, m, at[0], at[1], 2)
        if not sp:
            continue
        mon.x, mon.y = sp[0]
        mon.roam['seen'] = game.turn
        mon.awake = True
        m.mons.append(mon)
        game.msg(f'{name_of(mon)} comes after you down the stair!' if m.depth > row[3] else
                 f'{name_of(mon)} comes up the stair after you!', 'bad')
        game.shake()


def leaving(game):
    """You take the stair: a roamer that hunts you and is not far behind follows (it knows where you went)."""
    m, p = game.maps.get(game.cur), game.player
    if m is None or m.kind != 'dungeon':                     # the level you left is already gone
        return []
    out = []
    for o in list(m.mons):
        r = o.__dict__.get('roam')
        if r and game.turn - r.get('seen', -999) < 40 and cheb(o.x, o.y, p.x, p.y) <= 20 and o.hp > 0:
            m.mons.remove(o)
            o.cast = None
            out.append([max(2, cheb(o.x, o.y, p.x, p.y) // 2), o, None, m.depth])
    return out


def arrive(game, follow):
    m, p = game.map, game.player
    if not follow or m.kind != 'dungeon':
        return
    for row in follow:
        row[2] = (p.x, p.y)
    m.__dict__.setdefault('coming', []).extend(follow)


# ------------------------------------------------------------------ what a great boss leaves: three things, one whole
def offer(game, mon, us):
    """Three named things lie where it fell. Take one: the other two broke in the fall."""
    from . import events as EV
    random.shuffle(us)
    us = us[:3]
    EV.ask(game, 'boss_loot', f'What {mon.name} leaves', f'Three things of {mon.name} lie where {fill("{he}", mon)} '
           'fell. One you can take; the other two break as you lift it.',
           [(u['name'] + ', ' + D.BASES[u['base']]['name'].lower(), u['name']) for u in us], at=(mon.x, mon.y))


def r_loot(game, choice, ctx):
    from .entities import make_unique, unique_named
    u = unique_named(choice)
    if u is None:
        return
    it = make_unique(game, u)
    game.spill(game.map, ctx['at'][0], ctx['at'][1], it)
    game.announce(it)
    game.msg('The other two crack and fall apart.', 'info')


# ------------------------------------------------------------------ the test build (debug.py)
def spawn(game, k):
    """Set a kit boss down beside you, with its room if the map has none."""
    from .entities import make_monster
    m, p = game.map, game.player
    sp = free_around(game, m, p.x, p.y, 3)
    if not sp:
        return None
    x, y = sp[-1]
    o = make_monster(game, k, x, y, D.MONSTERS[k].get('lvl_fix', max(p.lvl, D.MONSTERS[k]['min_l'])))
    arm(o)
    o.awake = True
    m.mons.append(o)
    return o


def set_phase(game, mon, i):
    ph = phases(mon)
    i = max(0, min(len(ph) - 1, i))
    mon.hp = round(mon.maxhp * ph[i]['at']) if i else mon.maxhp
    _phase(game, mon, i, True)


def check_fair(game, mon):
    """Every shaped move of its kit, from here: which would leave no way out."""
    bad = []
    for ph in phases(mon):
        for cs in ph['cards'].values():
            for c in cs:
                mv = MOVES[c]
                if mv.get('shape'):
                    who, tx, ty = aim(game, mon)
                    cells = cells_for(game, mon, mv, tx, ty)
                    if (cells or mv['shape'] == 'mark') and need(game, mon, mv, cells, tx, ty) is None:
                        bad.append(mv['name'])
    return sorted(set(bad))


from . import events as _EV  # noqa: E402

_EV.RESOLVERS['boss_veil'] = r_veil
_EV.RESOLVERS['boss_loot'] = r_loot
