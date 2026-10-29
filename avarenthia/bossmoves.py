"""The move library of the bosses (round 16): what you can learn, they can do.

Each move has a role (k small, V set-up, G great, Z heaviest, B move, O summon, R a stance of its own), a shape or a
kind, the turns it loads, its power (a share of your full life at the boss's level), what it does besides the blow
(fx), whether it can be broken (brk; by default a load of two or more), and the lines it says. The kits in
`bosses.py` draw their cards from here. The shapes are drawn in `bosses.cells_for`; the kinds that strike no ground
(a curse, a stance, a summons, a step) are done by `do` below, the extra things a blow does by `on_you` and
`after`, and the stances by `guard`.

Shapes: line, wide (three wide), cone, arc (the cells before it), ring (round it; `inner` leaves a hole), ringat (a
ring round you), circle (at you, `r` 0 is the one tile), cross (`at` aim: round you; else through the room from it),
strips (bands across the room), scatter (several circles), wave (all that a wave from its side can reach: stand
behind something), room (all it can see; `safe` tiles shelter, and show gold), corpses, tail, mark, self (no ground:
a spell it works on itself, broken like any other)."""
import random

from . import data as D
from .worldgen import cheb, free_around

M = dict  # noqa: E731

LIBRARY = {
    # ---- weapons: warriors, champions, beasts with claws
    'strike': M(role='k', name='Strike', kind='melee'),
    'bite': M(role='k', name='Bite', kind='melee'),
    'pick': M(role='k', name='Pick', kind='melee'),
    'spear_throw': M(role='k', name='Spear Throw', kind='bolt'),
    'cleave': M(role='G', name='Cleave', shape='arc', len=1, load=1, brk=False, power=.3,
                say='{name} swings {his} weapon far back for a wide cut...', hit='The wide cut catches you!'),
    'whirl': M(role='G', name='Whirling Blade', shape='ring', r=1, load=1, brk=False, power=.28,
               say='{name} spins, {his} blade a blur round {him}...', hit='The whirling blade cuts you!'),
    'smash': M(role='G', name='Overhead Smash', shape='cross', at='aim', len=1, load=1, brk=True, power=.32,
               fx=M(stun=1), say='{name} lifts {his} weapon high over {his} head...',
               hit='The great blow comes down on you and the floor shakes!'),
    'earthshaker': M(role='Z', name='Earthshaker', shape='ring', r=3, inner=1, load=2, power=.45, fx=M(stun=1),
                     say='{name} raises {his} weapon to strike the floor itself. Get close, or get far!',
                     hit='The ground heaves under you and throws you down!'),
    'charge': M(role='G', name='Charge', shape='line', len=8, load=1, brk=False, power=.3, fx=M(rush=1, push=2),
                say='{name} drops {his} head and digs in {his} heels...', hit='{name} runs you down!'),
    'hook': M(role='V', name='Hook', shape='line', len=3, load=1, brk=True, power=.08, fx=M(pull=3),
              say='{name} swings a hook on a chain round {his} head...', hit='The hook bites and drags you in!'),
    'sunder': M(role='V', name='Sunder', kind='curse', fx=M(sunder=10), reach=1,
                say='{name} brings {his} weapon down on your armour. Straps tear and plates split!'),
    'hamstring': M(role='V', name='Hamstring', kind='curse', fx=M(slow=4), reach=1,
                   say='{name} cuts low at your legs. You stumble.'),
    'riposte': M(role='R', name='Riposte', kind='guard', g='riposte', t=2,
                 say='{name} sets {his} feet and waits, blade low. Strike {him} now and {he} strikes back.'),
    'shield_wall': M(role='R', name='Shield Wall', kind='guard', g='wall', t=3,
                     say='{name} sets {his} shield and crouches behind it. Blades glance off.'),
    'war_cry': M(role='O', name='War Cry', kind='cry',
                 say='{name} roars a war cry. {His} followers answer and come on harder!'),
    'executioner': M(role='Z', name='Executioner', shape='circle', r=0, at='aim', load=2, power=.42, fx=M(execute=.25),
                     say="{name} raises {his} blade over {aim} for the killing stroke. Break it, or don't be there!",
                     hit='The executioner\'s stroke falls on you!'),
    'volley': M(role='G', name='Volley', shape='circle', r=2, at='aim', load=1, brk=False, power=.27,
                say='{name} calls the bows up. Arrows rise into the dark...', hit='Arrows rain down on you!'),
    'pinning_shot': M(role='V', name='Pinning Shot', kind='curse', fx=M(hold=2), reach=7,
                      say='{name} looses a heavy bolt at your foot. It pins you to the floor!'),
    # ---- fire
    'firebolt': M(role='k', name='Firebolt', kind='bolt', elem='fire'),
    'fireball': M(role='G', name='Fireball', shape='circle', r=1, at='aim', load=1, brk=True, power=.3, elem='fire',
                  fx=M(burn=2), say='{name} cups a growing ball of fire in {his} hands...', hit='The fireball bursts on you!'),
    'ring_of_fire': M(role='V', name='Ring of Fire', shape='ringat', r=2, at='aim', load=1, brk=True, power=.1, elem='fire',
                      fx=M(burn=6), say='A circle of sparks springs up round {aim}. Get out before it closes!',
                      hit='The ring of fire flares up round you!'),
    'meteor': M(role='Z', name='Meteor', shape='circle', r=2, at='aim', load=3, follow=True, power=.5, elem='fire',
                fx=M(crater=3, burn=3), say='{name} reaches up. Far above, something burns and falls towards {aim}...',
                hit='The meteor strikes!'),
    'pyre': M(role='R', name='Pyre', kind='guard', g='pyre', t=4,
              say='Flames climb {name}. Whoever strikes {him} up close will burn.'),
    'burning_lines': M(role='G', name='Burning Lines', shape='strips', n=3, load=1, brk=False, power=.25, elem='fire',
                       fx=M(burn=3), say='{name} rakes {his} hand through the air. Lines of fire run along the floor...',
                       hit='The burning line runs over you!'),
    'hellfire': M(role='Z', name='Hellfire', shape='cone', len=7, load=2, power=.48, elem='fire', fx=M(burn=4),
                  say='{name} opens {his} hands. Black fire gathers between them...', hit='Hellfire washes over you!'),
    # ---- ice
    'frost_shard': M(role='k', name='Frost Shard', kind='bolt', elem='cold'),
    'ice_wall': M(role='V', name='Ice Wall', kind='icewall',
                  say='{name} sweeps {his} arm. Walls of ice crack up out of the floor round you!'),
    'cone_cold': M(role='G', name='Cone of Cold', shape='cone', len=6, load=2, power=.34, elem='cold', fx=M(slow=3),
                   say='{name} draws the warmth out of the air. Frost runs out before {him} in a fan...',
                   hit='The cold cuts to the bone!'),
    'ice_lance': M(role='G', name='Ice Lance', shape='wide', len=6, load=1, brk=False, power=.3, elem='cold',
                   say='{name} lifts a lance of ice as long as a man...', hit='The ice lance drives through you!'),
    'ice_tomb': M(role='Z', name='Ice Tomb', shape='circle', r=0, at='aim', load=2, follow=True, power=.45, elem='cold',
                  fx=M(hold=2), say='Frost creeps over the floor towards {aim}, and walls of ice begin to grow...',
                  hit='The ice closes over you!'),
    'glacial_ward': M(role='R', name='Glacial Ward', kind='guard', g='glacial', t=8,
                      say='Ice grows over {name} like armour. Fire or a heavy blow will crack it.'),
    # ---- storm
    'spark': M(role='k', name='Spark', kind='bolt', elem='lightning'),
    'chain_lightning': M(role='G', name='Chain Lightning', shape='line', len=7, load=1, brk=True, power=.28,
                         elem='lightning', fx=M(chain=1), say='Light crackles between the fingers of {name}...',
                         hit='The lightning leaps into you!'),
    'thunderclap': M(role='G', name='Thunderclap', shape='ring', r=1, load=1, brk=True, power=.26, elem='lightning',
                     fx=M(stun=1, push=2), say='{name} brings {his} hands together slowly...', hit='The thunderclap throws you back!'),
    'gust': M(role='V', name='Gust', kind='gust', reach=1, say='{name} sweeps {his} arm, and the wind throws you back!'),
    'static_field': M(role='V', name='Static Field', shape='circle', r=2, at='aim', load=1, brk=False, power=.12,
                      elem='lightning', fx=M(slow=2), say='The hair on your arms stands up. The air round {aim} hums...',
                      hit='The air snaps and bites!'),
    'ball_lightning': M(role='G', name='Ball Lightning', shape='line', len=8, load=1, brk=False, power=.28, elem='lightning',
                        say='{name} rolls a ball of light along the floor towards {aim}...', hit='The ball of lightning bursts on you!'),
    'call_storm': M(role='Z', name='Call the Storm', shape='scatter', n=6, r=1, load=2, power=.45, elem='lightning',
                    fx=M(wet=1), say='{name} calls up into the dark. Lightning gathers over the floor in rings. Stand between them!',
                    hit='The lightning strikes you!'),
    'tempest': M(role='Z', name='Tempest', shape='room', load=3, power=.4, elem='lightning', fx=M(push=1),
                 say='{name} spreads {his} arms, and the wind begins to scream round the room. Find cover!',
                 hit='The tempest tears at you!'),
    # ---- shadow
    'shadow_bolt': M(role='k', name='Shadow Bolt', kind='bolt'),
    'curse_weak': M(role='V', name='Curse of Weakness', kind='curse', fx=M(curse=8), reach=7,
                    say='{name} speaks a word at you, and your arms go heavy.'),
    'dread': M(role='V', name='Dread', shape='ring', r=4, load=1, brk=True, power=.04, fx=M(fear=5),
               say='A cold fear spreads out from {name} across the floor...', hit='Dread grips you!'),
    'darkness': M(role='V', name='Darkness', shape='circle', r=2, at='aim', load=1, brk=True, power=.04, fx=M(blind=3),
                  say='{name} points at {aim}. The shadows there thicken like smoke...', hit='Darkness fills your eyes!'),
    'life_drain': M(role='G', name='Life Drain', shape='line', len=7, load=1, brk=True, power=.26, fx=M(drain=1),
                    say='{name} reaches towards {aim} as if to pull something out...', hit='Your life is torn out of you, into {name}!'),
    'morraks_hand': M(role='G', name="Morrak's Hand", shape='circle', r=1, at='aim', load=1, brk=False, power=.24,
                      fx=M(gather=1), say='The floor round {aim} bulges. Something reaches up from below...',
                      hit='A black hand closes on you and drags you down!'),
    # ---- the dead
    'withering': M(role='V', name='Withering', kind='curse', fx=M(weak=8), reach=7,
                   say='{name} closes {his} hand, and your strength drains out of you.'),
    'army_dead': M(role='Z', name='Army of the Dead', shape='self', load=2, fx=M(army=4),
                   say='{name} sinks {his} hands into the floor. All along the walls the ground begins to move...'),
    'soul_harvest': M(role='R', name='Soul Harvest', kind='harvest',
                      say='{name} breathes in. A pale light rises from the dead on the floor and flows into {him}.'),
    # ---- nature and beasts
    'roots': M(role='V', name='Grasping Roots', shape='circle', r=1, at='aim', load=1, brk=False, power=.06,
               fx=M(roots=1), say='The floor round {aim} cracks. Roots worm up out of it...', hit='Roots wind round your legs!'),
    'bramble': M(role='V', name='Bramble Patch', kind='bramble', say='{name} stamps, and thorns burst up across the floor.'),
    'wrath_oak': M(role='Z', name='Wrath of the Oak', shape='wide', len=7, load=2, power=.46, fx=M(stun=1),
                   say='{name} heaves up a whole trunk over {his} head...', hit='The great trunk crashes down on you!'),
    'maul': M(role='G', name='Maul', shape='line', len=2, load=1, brk=False, power=.32, fx=M(push=2),
              say='{name} rears up, claws spread...', hit='{name} mauls you!'),
    'roar': M(role='V', name='Roar', shape='ring', r=5, load=1, brk=False, power=.03, fx=M(fear=4),
              say='{name} fills {his} chest...', hit='The roar shakes you to the marrow!'),
    'pounce': M(role='B', name='Pounce', shape='circle', r=1, at='aim', load=1, brk=False, power=.3, fx=M(land=1),
                say='{name} crouches low, eyes on {aim}...', hit='{name} lands on you!'),
    'burrow': M(role='B', name='Burrow', kind='burrow', say='{name} tears into the floor and is gone. The ground trembles.'),
    'emerge': M(role='G', name='Burrow', shape='circle', r=1, at='aim', load=2, follow=True, brk=False, power=.34,
                fx=M(land=1), say='', hit='{name} bursts up out of the ground under you!'),
    'web_spray': M(role='V', name='Web Spray', shape='cone', len=4, load=1, brk=True, power=.06, fx=M(web=1),
                   say='{name} lifts {his} abdomen towards {aim}...', hit='Sticky web wraps round you!'),
    'egg_clutch': M(role='O', name='Egg Clutch', kind='eggs', say='{name} drops a clutch of eggs on the floor. They twitch.'),
    'venom_spit': M(role='G', name='Venom Spit', shape='line', len=7, load=1, brk=False, power=.24, elem='poison',
                    fx=M(poison=6), say='{name} draws back {his} head, venom running from {his} jaws...',
                    hit='Burning venom splashes over you!'),
    # ---- holy light and healing
    'smite': M(role='k', name='Smite', kind='bolt', elem='holy'),
    'holy_shield': M(role='R', name='Holy Shield', kind='guard', g='holy', t=3,
                     say='A shield of light closes round {name}. It will take three blows.'),
    'mend': M(role='R', name='Mend', shape='self', load=1, brk=True, fx=M(mend=.1),
              say='{name} lays a hand on {his} own wounds and begins to pray...'),
    'divine_light': M(role='G', name='Divine Light', shape='cross', len=9, load=1, brk=False, power=.3, elem='holy',
                      say='{name} lifts {his} arms. Light gathers in beams across the floor...', hit='The beam of light burns you!'),
    'sanctuary': M(role='R', name='Sanctuary', kind='guard', g='sanct', t=6,
                   say='The floor round {name} turns to hallowed ground. Inside it, your blows are weak.'),
    'martyr': M(role='O', name="Martyr's Grace", kind='martyr',
                say='{name} lifts {his} hands over {his} followers. Each who falls will heal {him}.'),
    'dawnbreak': M(role='Z', name='Dawnbreak', shape='room', safe='light', load=3, power=.5, elem='holy', fx=M(blind=2),
                   say='{name} sets two stones of light on the floor and begins to shine. Stand by a stone!',
                   hit='The light burns your eyes and your skin!'),
    # ---- arcane, cunning and dark craft
    'arcane_bolt': M(role='k', name='Arcane Bolt', kind='bolt'),
    'blink': M(role='B', name='Blink', kind='blink', say='{name} flickers and is gone, and stands somewhere else.'),
    'slow_spell': M(role='V', name='Slow', kind='curse', fx=M(slow=4), reach=7,
                    say='{name} draws a slow circle in the air. Your limbs go thick as honey.'),
    'mirror': M(role='R', name='Mirror Images', kind='mirror',
                say='{name} shimmers, and there are three of {him}. Only one is real.'),
    'spell_ward': M(role='R', name='Counterspell', kind='guard', g='spellward', t=6,
                    say='{name} weaves a ward against spells. The next one you cast at {him} will fail.'),
    'runes': M(role='V', name='Rune of Snaring', kind='runes', say='{name} traces runes, and three glow on the floor round you.'),
    'stop_time': M(role='Z', name='Stop Time', shape='self', load=2, fx=M(stoptime=3),
                   say='{name} closes {his} eyes. The world slows round {him}... Break it!'),
    'smoke_bomb': M(role='B', name='Smoke Bomb', kind='smoke', say='{name} hurls something at {his} feet. Smoke billows up!'),
    'shadowstep': M(role='B', name='Shadowstep', kind='step', say='{name} steps into a shadow, and out of the one beside you!'),
    'garrote': M(role='G', name='Garrote', shape='circle', r=0, at='aim', load=1, brk=True, power=.28, fx=M(hold=2),
                 say='{name} snaps a wire taut between {his} hands...', hit='The wire bites into your throat!'),
    'fan_knives': M(role='G', name='Fan of Knives', shape='ring', r=2, load=1, brk=False, power=.26,
                    say='{name} crosses {his} arms, a knife between every finger...', hit='Knives cut into you!'),
    'hex': M(role='V', name='Hex', shape='circle', r=0, at='aim', load=1, brk=True, power=.02, fx=M(hex=3),
             say='{name} points a crooked finger at {aim} and croaks a word...', hit='You shrink and swell. You are a toad!'),
    # ---- for any boss
    'call_guards': M(role='O', name='Call Guards', kind='call', helpers=(('soldier', 'guard'), ('crossbow', 'guard')),
                     say='{name} shouts for {his} guards!'),
    # ---- the Rat King
    'rats': M(role='O', name='Rat Holes', kind='holes', say='{name} squeals. Rats pour out of the holes in the walls!'),
    'tail_lash': M(role='G', name='Tail Lash', shape='ring', r=1, load=1, brk=False, power=.26,
                   say='The knot of tails behind {name} lashes...', hit='The tails lash you!'),
    'plague_cloud': M(role='V', name='Plague Cloud', shape='circle', r=2, at='aim', load=1, brk=False, power=.08,
                      fx=M(sick=12), say='{name} coughs up a yellow cloud that drifts towards {aim}...',
                      hit='You breathe in the plague cloud!'),
    'gnaw': M(role='G', name='Gnaw', shape='line', len=3, load=1, brk=False, power=.28, fx=M(rush=1),
              say='{name} hunches, teeth bared, and fixes on {aim}...', hit='{name} runs through you, gnawing!'),
    'knot_split': M(role='Z', name='The Knot Splits', shape='self', load=2, fx=M(split=3),
                    say='The knot of {name} strains and tears. It is coming apart! Break it!'),
    # ---- Grolm the Digger
    'undermine': M(role='G', name='Undermine', shape='wide', len=6, load=1, brk=False, power=.3, fx=M(crater=4),
                   say='{name} drives {his} pick into the floor. A crack runs out towards {aim}...',
                   hit='The floor splits under you!'),
    'kick_prop': M(role='V', name='Kick the Prop', kind='prop', say='{name} kicks out a prop. The roof groans!'),
    'stones': M(role='G', name='Falling Stones', shape='scatter', n=4, r=0, load=1, brk=False, power=.2,
                say='', hit='A stone from the roof strikes you!'),
    # ---- the Brood Mother
    'drop_above': M(role='B', name='Drop From Above', kind='drop',
                    say='{name} climbs up the wall into the dark above and is gone...'),
    'cocoon': M(role='Z', name='Cocoon', shape='circle', r=1, at='aim', load=2, power=.4, elem='poison', fx=M(cocoon=1),
                say='{name} spins silk between {his} legs and turns towards {aim}...', hit='Silk winds round you, tighter and tighter!'),
    # ---- the Drowned King
    'brine_lance': M(role='k', name='Lance of Brine', kind='bolt', elem='cold'),
    'tidal_wave': M(role='G', name='Tidal Wave', shape='wave', load=1, brk=False, power=.3, elem='cold', fx=M(push=2),
                    say='The water draws back from the walls. A wave is rising! Get behind something!',
                    hit='The wave smashes into you!'),
    'drag_under': M(role='V', name='Drag Under', shape='line', len=5, load=1, brk=True, power=.1, fx=M(pull=3),
                    say='{name} reaches out of the water towards {aim}...', hit='Cold hands drag you down into the water!'),
    'whirlpool': M(role='G', name='Whirlpool', shape='circle', r=2, at='aim', load=1, brk=False, power=.28, elem='cold',
                   fx=M(gather=1), say='The water round {aim} begins to turn...', hit='The whirlpool drags you round and under!'),
    'deep_calls': M(role='Z', name='The Deep Calls', shape='room', safe='ledge', load=3, power=.5, elem='cold',
                    say='{name} sinks beneath the water. The whole hall begins to shake. Get up out of the water!',
                    hit='The deep comes up over you!'),
    # ---- the hollow kinds of the Varnish and the beasts of the deep
    'wail': M(role='G', name='Wail', shape='ring', r=3, load=1, brk=True, power=.24, fx=M(fear=3),
              say='{name} opens {his} mouth wide. No sound yet...', hit='The wail goes through you!'),
    'gaze_ray': M(role='G', name='Gaze', shape='wide', len=8, load=1, brk=False, power=.28, fx=M(stun=1),
                  say='The great eye of {name} turns slowly towards {aim}...', hit='The gaze falls on you!'),
    'babble': M(role='V', name='Babble', shape='ring', r=4, load=1, brk=True, power=.03, fx=M(confuse=3),
                say='{name} begins to babble in many voices at once...', hit='The voices fill your head!'),
    'stench': M(role='V', name='Stench', shape='ring', r=2, load=1, brk=False, power=.06, fx=M(sick=8),
                say='{name} breathes out. The air turns thick and foul...', hit='You gag on the stench!'),
    'paralyse_claw': M(role='G', name='Paralysing Claw', shape='arc', len=1, load=1, brk=False, power=.24, fx=M(stun=1),
                       say='{name} spreads {his} grey claws...', hit='The claws rake you, and your limbs go stiff!'),
    'acid_spray': M(role='G', name='Acid Spray', shape='cone', len=4, load=1, brk=False, power=.26, elem='poison',
                    fx=M(sunder=8), say='{name} rears up, acid dripping from {his} jaws...', hit='Acid eats into you and your armour!'),
    'tunnel': M(role='O', name='Swarm Tunnel', kind='tunnel', say='The floor heaves in three places. Something is digging up!'),
    'bomb_volley': M(role='G', name='Bomb Volley', shape='scatter', n=3, r=1, load=1, brk=False, power=.26, elem='fire',
                     fx=M(burn=1), say='{name} shrieks an order. Lit bombs come sailing over the heads of the goblins...',
                     hit='A bomb bursts beside you!'),
    'coil': M(role='V', name='Coil', shape='circle', r=0, at='aim', load=1, brk=True, power=.1, fx=M(hold=3, bleed=3),
              say='{name} gathers {his} long body to coil round {aim}...', hit='The coils close round you and squeeze!'),
    'shed_skin': M(role='R', name='Shed Skin', kind='shed', say='{name} slides out of {his} skin, fresh and whole, and leaves it standing.'),
    'sting_dive': M(role='B', name='Sting', shape='circle', r=1, at='aim', load=1, brk=False, power=.3, elem='poison',
                    fx=M(land=1, poison=5), say='{name} rises, sting curled under {him}, and hangs over {aim}...',
                    hit='{name} drops on you, stinging!'),
    'starfall': M(role='G', name='Starfall', shape='scatter', n=4, r=1, load=2, brk=True, power=.3, elem='fire',
                  say='Points of light gather in the dark above, over the floor round you...', hit='A falling star strikes you!'),
    'boulder': M(role='G', name='Boulder Throw', shape='circle', r=1, at='aim', load=1, brk=False, power=.3, fx=M(stun=1),
                 say='{name} tears up a great stone and lifts it over {his} head...', hit='The boulder crashes into you!'),
    'rampage': M(role='Z', name='Rampage', shape='ring', r=2, load=2, power=.42, fx=M(push=2),
                 say='{name} froths and beats {his} chest. {He} is working {himself} into a rage...',
                 hit='{name} tears through everything round {him}!'),
}

# helpers each summons brings
CALLS = {
    'call_ants': (('ant_soldier', 'guard'), ('ant_worker', 'swarm'), ('ant_worker', 'swarm')),
    'call_goblins': (('gob_bomber', 'guard'), ('gob_shaman', 'mender'), ('gob_sneak', 'swarm')),
    'call_drowned': (('drowned', 'guard'), ('drowned', 'swarm')),
    'call_hounds': (('hellhound', 'swarm'), ('imp', 'channeler')),
    'call_spiders': (('brood_spider', 'swarm'), ('web_weaver', 'guard')),
    'call_wasps': (('bloodwasp', 'swarm'), ('bloodwasp', 'swarm'), ('needlewing', 'swarm')),
    'call_band': (('orc', 'guard'), ('orc_shaman', 'mender')),
    'call_ghouls': (('ghoul', 'swarm'), ('ghast', 'guard')),
    'call_spawn': (('gibberflesh', 'swarm'), ('skullsipper', 'channeler')),
    'call_bound': (('bound_dead', 'guard'), ('bound_dead', 'warder')),
    'call_hobs': (('hob_legionary', 'guard'), ('hob_archer', 'swarm')),
    'call_gnolls': (('gnoll_hunter', 'swarm'), ('gnoll_caller', 'mender')),
}
for _k, _h in CALLS.items():
    LIBRARY[_k] = M(role='O', name='Call', kind='call', helpers=_h, say='{name} calls, and {his} kind come out of the dark!')
LIBRARY['call_drowned']['say'] = '{name} lifts a hand out of the water. Drowned ones rise beside {him}.'
LIBRARY['call_hounds']['say'] = '{name} howls into the fire. Hellhounds come running out of it.'
LIBRARY['call_bound']['say'] = '{name} calls the bound dead. They come in step, chains dragging.'

GUARDS = {'riposte': 'Riposte', 'wall': 'Shield Wall', 'glacial': 'Glacial Ward', 'holy': 'Holy Shield',
          'pyre': 'Pyre', 'sanct': 'Sanctuary', 'spellward': 'Counterspell', 'enrage': 'Enraged'}


def _BS():
    from . import bosses as BS
    return BS


def _fill(text, mon, aim=None):
    return _BS().fill(text, mon, aim)


# ------------------------------------------------------------------ the kinds that strike no ground
def do(game, mon, mv):
    """A move that is not a marked blow. True if it was done; None if it is not one of these kinds."""
    BS = _BS()
    m, p = game.map, game.player
    kind = mv.get('kind')
    d = cheb(mon.x, mon.y, p.x, p.y)
    seen = game.visible(mon.x, mon.y)
    bs = BS.st(mon)
    if kind == 'curse':
        if d > mv.get('reach', 7) or not game.line_clear(mon.x, mon.y, p.x, p.y):
            return False
        game.msg(_fill(mv['say'], mon), 'bad')
        on_you(game, mon, mv.get('fx', {}))
        return True
    if kind == 'guard':
        g = mv['g']
        cd = bs.setdefault('gcd', {})
        if g in bs.setdefault('guard', {}) or not seen or game.turn < cd.get(g, 0):
            return False
        bs['guard'][g] = mv.get('t', 3) if g != 'holy' else 3
        cd[g] = game.turn + 12                               # a stance cannot be taken again at once
        game.msg(_fill(mv['say'], mon), 'bad')
        game.flash([(mon.x, mon.y)], (160, 200, 255) if g != 'pyre' else (255, 140, 60), '*', .3)
        return True
    if kind == 'cry':
        hs = BS.helpers(game, mon)
        if not hs:
            return False
        for o in hs:
            o.effects['frenzy'] = [6, 0]
        game.msg(_fill(mv['say'], mon), 'bad')
        return True
    if kind == 'icewall':
        from . import spellmap as SM
        if d > 8:
            return False
        ring = [(p.x + a, p.y + b) for a, b in BS.D8]
        random.shuffle(ring)
        if sum(1 for c in ring[3:] if SM.place(game, m, c[0], c[1], D.ICEWALL, 18)) == 0:
            return False
        game.msg(_fill(mv['say'], mon), 'bad')
        return True
    if kind == 'bramble':
        from . import spellmap as SM
        if d > 9:
            return False
        own = BS.area(game, mon)
        row = p.y + random.choice((-2, 2))
        cells = [c for c in own if c[1] == row and abs(c[0] - p.x) <= 5]
        if sum(1 for c in cells if SM.place(game, m, c[0], c[1], D.BRAMBLE, 14, max(2, mon.lvl // 3))) == 0:
            return False
        game.msg(_fill(mv['say'], mon), 'bad')
        return True
    if kind == 'runes':
        from .behave import traps
        tr = traps(m)
        spots = [c for c in free_around(game, m, p.x, p.y, 2) if cheb(*c, p.x, p.y) == 2 and m.tile(*c) == D.FLOOR
                 and c not in tr]
        random.shuffle(spots)
        if d > 8 or len(spots) < 3:
            return False
        for c in spots[:3]:
            tr[c] = max(2, mon.dmg[0])
        m.known_traps = getattr(m, 'known_traps', set()) | set(spots[:3])
        game.msg(_fill(mv['say'], mon), 'bad')
        return True
    if kind in ('blink', 'smoke'):
        own = [c for c in BS.area(game, mon) if 4 <= cheb(*c, mon.x, mon.y) <= 8 and not game.occupied(m, *c)
               and D.TILES[m.tile(*c)].walk and cheb(*c, p.x, p.y) >= 3]
        if not own or not seen:
            return False
        if kind == 'smoke':
            from . import spellmap as SM
            SM.area(game, m, [(mon.x + a, mon.y + b) for a in (-1, 0, 1) for b in (-1, 0, 1)], D.SMOKE, 6)
        game.msg(_fill(mv['say'], mon), 'bad')
        game.flash([(mon.x, mon.y)], (206, 132, 255), '*', .2)
        mon.x, mon.y = random.choice(own)
        mon.cast = None
        return True
    if kind == 'step':
        if d > 8 or not seen:
            return False
        dx, dy = (p.x > mon.x) - (p.x < mon.x), (p.y > mon.y) - (p.y < mon.y)
        spots = [(p.x + dx, p.y + dy)] + [c for c in free_around(game, m, p.x, p.y, 1)]
        spots = [c for c in spots if m.inb(*c) and D.TILES[m.tile(*c)].walk and not game.occupied(m, *c)
                 and BS.may_stand(game, mon, *c)]
        if not spots:
            return False
        game.msg(_fill(mv['say'], mon), 'bad')
        mon.x, mon.y = spots[0]
        return True
    if kind in ('burrow', 'drop'):
        if d > 10 or bs.get('air'):
            return False
        if not BS.start(game, mon, 'emerge' if kind == 'burrow' else 'dive', say=mv['say']):
            return False
        mon.invis = 99
        bs['air'] = True
        return True
    if kind == 'eggs':
        spots = [c for c in free_around(game, m, mon.x, mon.y, 3) if m.tile(*c) == D.FLOOR and cheb(*c, p.x, p.y) >= 2]
        if len(eggs(game)) >= 6 or len(spots) < 3:
            return False
        random.shuffle(spots)
        for c in spots[:3]:
            m.set(c[0], c[1], D.EGGS)
            eggs(game)[c] = [5, mon.id]
        game.msg(_fill(mv['say'], mon), 'bad')
        return True
    if kind == 'holes':
        ar = BS.arena_of(game, mon)
        open_ = [c for c in (ar or {}).get('holes', ()) if m.tile(*c) == D.RATHOLE]
        if not open_ or len(BS.helpers(game, mon)) >= 6:
            return False
        from .entities import make_monster
        n = 0
        for c in open_:
            sp = [s for s in free_around(game, m, *c, 1) if s in set(map(tuple, ar['cells']))]
            if sp:
                o = make_monster(game, 'rat', sp[0][0], sp[0][1], max(1, mon.lvl - 2))
                o.awake = o.called = True
                o.job, o.boss_of = 'swarm', mon.id
                m.mons.append(o)
                n += 1
        if not n:
            return False
        game.msg(_fill(mv['say'], mon), 'bad')
        return True
    if kind == 'prop':
        ar = BS.arena_of(game, mon)
        props = [c for c in (ar or {}).get('props', ()) if m.tile(*c) == D.PROP]
        if not props:
            return False
        c = min(props, key=lambda c: cheb(*c, mon.x, mon.y))
        m.set(c[0], c[1], D.FALLEN)
        game.msg(_fill(mv['say'], mon), 'bad')
        game.shake()
        BS.start(game, mon, 'stones', say='Stones begin to fall from the roof. Look up!')
        return True
    if kind == 'mirror':
        if not seen or any(getattr(o, 'image_of', None) == mon.id for o in m.mons):
            return False
        from .entities import make_monster
        spots = [c for c in free_around(game, m, mon.x, mon.y, 3) if BS.may_stand(game, mon, *c)]
        if len(spots) < 2:
            return False
        random.shuffle(spots)
        for c in spots[:2]:
            o = make_monster(game, mon.k, c[0], c[1], mon.lvl)
            o.__dict__.pop('bs', None)
            o.name, o.gender = mon.name, getattr(mon, 'gender', None)
            o.hp = o.maxhp = 1
            o.awake = o.called = True
            o.image_of = mon.id
            m.mons.append(o)
        a, b = spots[0], (mon.x, mon.y)
        mon.x, mon.y = a[0], a[1]
        img = next(o for o in m.mons if getattr(o, 'image_of', None) == mon.id and (o.x, o.y) == a)
        img.x, img.y = b
        game.msg(_fill(mv['say'], mon), 'bad')
        return True
    if kind == 'harvest':
        sl = getattr(m, 'slain', [])
        own = BS.area(game, mon)
        here = [s for s in sl if (s[1], s[2]) in own]
        if not here or mon.hp >= BS.cap_hp(mon):
            return False
        for s in here:
            sl.remove(s)
        mon.hp = min(BS.cap_hp(mon), mon.hp + round(mon.maxhp * .03 * len(here)))
        game.msg(_fill(mv['say'], mon), 'bad')
        return True
    if kind == 'martyr':
        if bs.get('martyr') or not BS.helpers(game, mon):
            return False
        bs['martyr'] = True
        game.msg(_fill(mv['say'], mon), 'bad')
        return True
    if kind == 'gust':
        if d > mv.get('reach', 4) or not game.line_clear(mon.x, mon.y, p.x, p.y):
            return False
        game.msg(_fill(mv['say'], mon), 'bad')
        BS.push(game, mon, p, 2)
        return True
    if kind == 'tunnel':
        if len(BS.helpers(game, mon)) >= 5:
            return False
        return BS.start(game, mon, 'tunnel_up', say=mv['say'])
    if kind == 'shed':
        if mon.hp >= BS.cap_hp(mon) * .8 or bs.get('shed'):
            return False
        bs['shed'] = True
        from .entities import make_monster
        o = make_monster(game, mon.k, mon.x, mon.y, mon.lvl)
        o.__dict__.pop('bs', None)
        o.name = f'the shed skin of {mon.name}'
        o.hp = o.maxhp = max(3, mon.maxhp // 20)
        o.image_of, o.skin = mon.id, True
        own = [c for c in free_around(game, m, mon.x, mon.y, 4) if cheb(*c, mon.x, mon.y) >= 3 and BS.may_stand(game, mon, *c)]
        if not own:
            return False
        m.mons.append(o)
        mon.x, mon.y = random.choice(own)
        mon.hp = min(BS.cap_hp(mon), mon.hp + round(mon.maxhp * .15))
        game.msg(_fill(mv['say'], mon), 'bad')
        return True
    return None


LIBRARY['tunnel_up'] = M(role='O', name='Swarm Tunnel', shape='scatter', n=3, r=0, load=2, brk=False, power=.12,
                         fx=M(ants=1), say='', hit='Ants boil up out of the ground under you!')


def eggs(game):
    return game.map.__dict__.setdefault('boss_eggs', {})


# ------------------------------------------------------------------ what a blow does to you besides the hurt
def on_you(game, mon, fx):
    """The states a move leaves on you (you were in it, or it was cast at you)."""
    from .behave import give
    p = game.player
    if fx.get('stun'):
        give(game, 'paralysed', fx['stun'])
    if fx.get('slow'):
        give(game, 'slowed', fx['slow'])
    if fx.get('hold'):
        give(game, 'held', fx['hold'])
        p.held_by = None
    if fx.get('fear'):
        give(game, 'afraid', fx['fear'])
    if fx.get('blind'):
        give(game, 'blinded', fx['blind'])
    if fx.get('confuse'):
        give(game, 'confused', fx['confuse'])
    if fx.get('curse'):
        give(game, 'cursed', fx['curse'])
    if fx.get('weak'):
        give(game, 'weakened', fx['weak'])
    if fx.get('sick'):
        give(game, 'diseased', fx['sick'])
    if fx.get('hex'):
        give(game, 'hexed', fx['hex'])
    if fx.get('poison'):
        p.poison = [fx['poison'], max(1, round(mon.lvl / 2))]
    if fx.get('bleed'):
        p.poison = [fx['bleed'], max(1, round(mon.lvl / 3))]
    if fx.get('sunder'):
        p.buffs = [b for b in p.buffs if b[3] != 'Sundered'] + [['def', -max(5, mon.lvl * 2), fx['sunder'], 'Sundered']]
    if fx.get('web') or fx.get('roots') or fx.get('cocoon'):
        give(game, 'held', 3 if fx.get('cocoon') else 2)
        p.held_by = None


def hit_more(game, mon, mv, dmg):
    """When the blow hit you: what it does beyond the hurt and your states."""
    BS = _BS()
    p = game.player
    fx = mv.get('fx', {})
    if fx.get('pull'):
        pull(game, mon, p, fx['pull'])
    if fx.get('drain'):
        mon.hp = min(BS.cap_hp(mon), mon.hp + round(dmg))
    if fx.get('cocoon'):
        mon.hp = min(BS.cap_hp(mon), mon.hp + round(mon.maxhp * .08))
        game.msg(f'{BS.name_of(mon)} feeds while you hang there.', 'bad')


def power(game, mon, mv, base):
    """The share of your life it takes: the executioner kills the weak; the storm finds the wet."""
    fx = mv.get('fx', {})
    p = game.player
    s = game.stats()
    if fx.get('execute') and p.life < s['max_life'] * fx['execute']:
        return base * 3
    if fx.get('wet') and game.map.tile(p.x, p.y) in (D.SHALLOW, D.WATER):
        return base * 2
    return base


def after(game, mon, mv, cells, c):
    """What the blow leaves on the floor, and what it calls up."""
    BS = _BS()
    from . import spellmap as SM
    m, p = game.map, game.player
    fx = mv.get('fx', {})
    if fx.get('crater'):
        spots = [c for c in cells if m.tile(*c) == D.FLOOR and c != (p.x, p.y) and not game.occupied(m, *c)]
        random.shuffle(spots)
        for x, y in spots[:fx['crater']]:
            m.set(x, y, D.FALLEN)
    if fx.get('roots'):
        SM.area(game, m, list(cells), D.ROOTS, 6)
    if fx.get('web'):
        SM.area(game, m, [c for c in cells if c != (p.x, p.y)][:6], D.WEBS, 30)
    if fx.get('gather') and (p.x, p.y) in cells:
        mid = (c['tx'], c['ty'])
        if not game.occupied(m, *mid) and D.TILES[m.tile(*mid)].walk:
            p.x, p.y = mid
    if fx.get('chain'):
        from . import mercs as MC
        if (p.x, p.y) in cells:
            for mc in MC.party(game):
                b = mc.body
                if b is not None and b in m.mons and cheb(b.x, b.y, p.x, p.y) <= 2 and (b.x, b.y) not in cells:
                    game.flash([(b.x, b.y)], (200, 220, 255), '*', .2)
                    game.msg(f'The lightning leaps from you to {mc.name}!', 'bad')
                    MC.hurt(game, mc, max(1, random.randint(*mon.dmg)), mon)
    if fx.get('ants'):
        from .entities import make_monster
        for x, y in cells:
            if not game.occupied(m, x, y) and D.TILES[m.tile(x, y)].walk:
                o = make_monster(game, 'ant_soldier', x, y, max(1, mon.lvl - 2))
                o.awake = o.called = True
                o.job, o.boss_of = 'swarm', mon.id
                m.mons.append(o)


def on_self(game, mon, mv):
    """A spell it works on itself, when it was not broken."""
    BS = _BS()
    from .entities import make_monster
    m = game.map
    fx = mv.get('fx', {})
    bs = BS.st(mon)
    if fx.get('mend'):
        mon.hp = min(BS.cap_hp(mon), mon.hp + round(mon.maxhp * fx['mend']))
        game.flash([(mon.x, mon.y)], (120, 240, 140), '+', .3)
        game.msg(f'The wounds of {mon.the()} close.', 'bad')
    if fx.get('army'):
        ar = BS.arena_of(game, mon)
        room = list(map(tuple, ar['cells'])) if ar else list(BS.area(game, mon))
        edge = [c for c in room if any((c[0] + a, c[1] + b) not in set(room) for a, b in BS.D8)
                and not game.occupied(m, *c) and D.TILES[m.tile(*c)].walk]
        random.shuffle(edge)
        for i, c in enumerate(edge[:fx['army']]):
            o = make_monster(game, 'skeleton', c[0], c[1], max(1, mon.lvl - 3))
            o.awake = o.called = True
            o.job, o.boss_of = ('warder' if i == 0 else 'swarm'), mon.id
            m.mons.append(o)
        game.msg('The dead climb out of the floor all along the walls. One of them stands guard over its master.', 'bad')
    if fx.get('stoptime'):
        bs['stopped'] = fx['stoptime']
        game.msg(f'Time stops for you. {BS.name_of(mon)} moves on alone!', 'bad')
    if fx.get('split'):
        split(game, mon, fx['split'])


def split(game, mon, n):
    """The Rat King comes apart: three smaller kings share what life it had left."""
    BS = _BS()
    from .entities import make_monster
    m = game.map
    spots = [c for c in free_around(game, m, mon.x, mon.y, 2) if BS.may_stand(game, mon, *c)]
    random.shuffle(spots)
    part = max(1, mon.hp // n)
    mon.hp = part
    mon.knot = mon.id
    for c in spots[:n - 1]:
        o = make_monster(game, mon.k, c[0], c[1], mon.lvl)
        o.name = mon.name
        o.hp, o.maxhp = part, max(1, mon.maxhp // n)
        o.awake = True
        o.knot = mon.id
        if BS.st(o) is not None:
            o.bs['phase'] = len(BS.phases(o)) - 1
            o.bs['engaged'] = True
        m.mons.append(o)
    game.msg(f'The knot tears apart into {n} smaller kings!', 'bad')
    game.shake()


# ------------------------------------------------------------------ the stances it takes
def pull(game, mon, who, n):
    m = game.map
    for _ in range(n):
        dx, dy = (mon.x > who.x) - (mon.x < who.x), (mon.y > who.y) - (mon.y < who.y)
        nx, ny = who.x + dx, who.y + dy
        if (nx, ny) == (mon.x, mon.y) or not D.TILES[m.tile(nx, ny)].walk or game.occupied(m, nx, ny):
            break
        who.x, who.y = nx, ny


def guard(game, mon, dmg, weapon, elem, near):
    """Your blow against its stance. Returns the damage that gets through."""
    BS = _BS()
    bs = BS.st(mon)
    g = bs.get('guard') or {}
    p = game.player
    if not g:
        return dmg
    if 'riposte' in g and weapon and near:
        g.pop('riposte')
        game.msg(f'{BS.name_of(mon)} turns your blade and strikes back!', 'bad')
        game.hurt(max(1, random.randint(*mon.dmg) * 1.3), mon.the())
        return max(1, round(dmg * .3))
    if 'wall' in g and weapon:
        from . import weapons as WP
        if not WP.over_shield(game) and WP.wielded(game) != 'warhammer':
            game.msg('Your blow glances off the shield wall.', 'info')
            return max(1, round(dmg * .3))
    if 'glacial' in g:
        if elem == 'fire' or dmg >= mon.maxhp * .06:
            g.pop('glacial')
            game.msg('The ward of ice cracks and falls away!', 'good')
        else:
            return max(1, round(dmg * .5))
    if 'holy' in g:
        g['holy'] -= 1
        if g['holy'] <= 0:
            g.pop('holy')
            game.msg('The shield of light breaks!', 'good')
        else:
            game.msg('The shield of light takes the blow.', 'info')
        return 0
    if 'spellward' in g and not weapon:
        g.pop('spellward')
        game.msg('Your spell breaks on the ward and is gone.', 'info')
        return 0
    if 'pyre' in g and weapon and near:
        game.msg('The flames on it burn you as you strike.', 'bad')
        game.hurt(max(1, mon.lvl // 2), mon.the(), 'fire')
    if 'sanct' in g and cheb(p.x, p.y, mon.x, mon.y) <= 2:
        return max(1, round(dmg * .5))
    return dmg


def wear(mon):
    """Each of its turns, its stances wear down."""
    bs = _BS().st(mon)
    g = bs.get('guard') if bs else None
    if not g:
        return
    for k in list(g):
        if k == 'holy':
            continue
        g[k] -= 1
        if g[k] <= 0:
            g.pop(k)
