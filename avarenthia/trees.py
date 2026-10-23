"""The tree of each class (see "Classes, trees and the bar" in docs/plan.md): three branches of six knots, only
passives. A knot opens once the one above it has a point; some take two or three points. You get one point for every
five ranks in that school, spend them only where you rested (an inn's bed, your camp), and a temple takes them all
back for coin. The first knot of each school's "blade" branch is its imbue: cast a spell of the school and your
weapon carries it for a while. What you spent lives on the player (`p.tree`: {line: {knot: points}}).

Each knot is (id, name, steps, kind, arg, per, text): `per` points of `kind` for every point spent; `{n}` in the
text is what you have (or would have with the first point). The kinds are read where the game does that thing:
`tuned` makes the copy of a skill you cast, `stats` your numbers, the rest are small hooks named below."""
import copy
import random

from . import skills as SK
from .worldgen import cheb

EVERY = 5                       # ranks in a school for one point
IMBUE_TURNS = 10
RESPEC = 200                    # what a temple asks for each point it takes back (2 silver)
B = None                        # no argument

TREES = {
    'fire': [
        ('Pyromancer', 'your spells', [
            ('kindled_mind', 'Kindled Mind', 3, 'dmg', B, 5, 'Your fire spells do {n}% more damage.'),
            ('quick_spark', 'Quick Spark', 1, 'cd', 'searing_brand', 1, 'Searing Brand recharges {n} turn sooner.'),
            ('thrifty_flame', 'Thrifty Flame', 2, 'cost', 'fireball', 15, 'Fireball costs {n}% less mana.'),
            ('searing', 'Searing', 2, 'fxdur', 'burn', 30, 'The burning you cause lasts {n}% longer.'),
            ('inner_furnace', 'Inner Furnace', 1, 'kill_mana', B, 3, 'A foe slain by your fire spells gives you {n} mana.'),
            ('heart_of_fire', 'Heart of Fire', 1, 'flag', B, 1, 'The first fire spell you cast in each fight costs no mana.')]),
        ('Flameblade', 'your weapon', [
            ('flameblade', 'Flameblade', 1, 'imbue', 'burn', 1,
             'When you cast a fire spell, your weapon burns for 10 turns: about one blow in three sets the foe '
             'alight, a third as hot as Immolate. While it burns, no mana comes back.'),
            ('hot_steel', 'Hot Steel', 3, 'wdmg', 'fire_dmg', 2, 'While Flameblade burns, each blow does up to {n} '
             'more fire damage.'),
            ('ember_guard', 'Ember Guard', 2, 'softer', 'burn', 10, 'Burning foes hit you {n}% softer.'),
            ('brand_strike', 'Brand Strike', 2, 'wvs', 'burn', 10, 'Your weapon does {n}% more to a burning foe.'),
            ('fire_in_the_blood', 'Fire in the Blood', 1, 'flag', B, 1, 'Stamina comes back twice as fast while a '
             'burning foe stands beside you.'),
            ('pyre_blade', 'Pyre Blade', 1, 'flag', B, 1, 'A foe your weapon slays while Flameblade burns bursts into '
             'flame: the foes beside it catch fire.')]),
        ('Kindler', 'the burning ground', [
            ('fireproof', 'Fireproof', 3, 'res', 'res_fire', 8, '{n}% less damage from fire.'),
            ('long_burn', 'Long Burn', 2, 'field', B, 30, 'The burning ground of your spells lasts {n}% longer.'),
            ('walk_in_fire', 'Walk in Fire', 1, 'flag', B, 1, 'Burning ground does you no harm.'),
            ('smoke', 'Smoke', 1, 'softer', 'burning_ground', 15, 'Foes standing in burning ground choke on the '
             'smoke and hit you {n}% softer.'),
            ('wildfire', 'Wildfire', 2, 'leap_burn', B, 40, 'When a burning foe dies, its fire leaps to a foe beside '
             'it: a {n}% chance.'),
            ('ash_walker', 'Ash Walker', 1, 'flag', B, 1, 'Standing in burning ground, you heal 2 life a turn.')]),
    ],
    'frost': [
        ('Winter', 'your spells', [
            ('bitter_cold', 'Bitter Cold', 3, 'dmg', B, 5, 'Your frost spells do {n}% more damage.'),
            ('sharp_shards', 'Sharp Shards', 1, 'flag', B, 1, 'Frost Shard also strikes a second foe near the first.'),
            ('deep_chill', 'Deep Chill', 2, 'fxdur', 'slow', 30, 'The slowing you cause lasts {n}% longer.'),
            ('shatter', 'Shatter', 2, 'svs', 'frozen', 15, 'Your spells do {n}% more to a frozen foe.'),
            ('cold_heart', 'Cold Heart', 1, 'kill_mana', B, 3, 'A foe slain by your frost spells gives you {n} mana.'),
            ('absolute_zero', 'Absolute Zero', 1, 'flag', B, 1, 'Ice Lance always freezes its foe for 2 turns.')]),
        ('Rimeblade', 'your weapon', [
            ('rimeblade', 'Rimeblade', 1, 'imbue', 'slow', 1,
             'When you cast a frost spell, your weapon is rimed for 10 turns: about one blow in three slows the foe '
             'for 3 turns. While it lasts, no mana comes back.'),
            ('frozen_edge', 'Frozen Edge', 3, 'wdmg', 'cold_dmg', 2, 'While Rimeblade lasts, each blow does up to {n} '
             'more cold damage.'),
            ('frostbite', 'Frostbite', 2, 'wvs', 'slow', 10, 'Your weapon does {n}% more to a slowed foe.'),
            ('cold_snap', 'Cold Snap', 1, 'wproc', ('slow', 'freeze'), 20, 'A blow on a slowed foe freezes it for 2 '
             'turns: a {n}% chance.'),
            ('numbing', 'Numbing', 1, 'softer', 'slow', 15, 'Slowed foes hit you {n}% softer.'),
            ('winters_bite', "Winter's Bite", 1, 'fifth', 'freeze', 1, 'Every fifth blow of your weapon freezes the '
             'foe for 2 turns.')]),
        ('Glacier', 'ice and armour', [
            ('thick_ice', 'Thick Ice', 3, 'buffpow', 'frost_armor', 15, 'Frost Armor guards {n}% more.'),
            ('long_walls', 'Long Walls', 2, 'tdur', 'ice_wall', 30, 'Your Ice Walls stand {n}% longer.'),
            ('ice_road', 'Ice Road', 1, 'cd', 'ice_wall', 4, 'Ice Wall recharges {n} turns sooner.'),
            ('glacial_step', 'Glacial Step', 1, 'buffdur', 'glacial_ward', 30, 'Glacial Ward lasts {n}% longer.'),
            ('cold_blood', 'Cold Blood', 2, 'res', 'res_cold', 8, '{n}% less damage from cold.'),
            ('living_glacier', 'Living Glacier', 1, 'flag', B, 1, 'While Frost Armor is on you, you heal 1 life a '
             'turn.')]),
    ],
    'storm': [
        ('Tempest', 'your spells', [
            ('charged', 'Charged', 3, 'dmg', B, 5, 'Your storm spells do {n}% more damage.'),
            ('long_arc', 'Long Arc', 2, 'cd', 'chain', 1, 'Chain Lightning recharges {n} turn sooner.'),
            ('one_more_jump', 'One More Jump', 1, 'jumps', 'chain', 1, 'Chain Lightning leaps to {n} more foe.'),
            ('thunderhead', 'Thunderhead', 2, 'hold', B, 1, 'Your storm spells stun {n} turn longer.'),
            ('static_mind', 'Static Mind', 1, 'flag', B, 1, 'Each foe your lightning leaps to gives you 1 mana.'),
            ('eye_of_the_storm', 'Eye of the Storm', 1, 'cost', 'storm_call', 50, 'Call the Storm costs {n}% less '
             'mana.')]),
        ('Stormblade', 'your weapon', [
            ('stormblade', 'Stormblade', 1, 'imbue', 'spark', 1,
             'When you cast a storm spell, your weapon crackles for 10 turns: about one blow in three throws a spark '
             'at another foe near the one you strike, twice as hard if it is wet. While it lasts, no mana comes '
             'back.'),
            ('crackle', 'Crackle', 3, 'wdmg', 'light_dmg', 2, 'While Stormblade lasts, each blow does up to {n} more '
             'lightning damage.'),
            ('grounded', 'Grounded', 2, 'res', 'res_light', 8, '{n}% less damage from lightning.'),
            ('arc_step', 'Arc Step', 1, 'flag', B, 1, 'When your weapon slays a foe, a free spark leaps to the next.'),
            ('charged_steel', 'Charged Steel', 1, 'wvs', 'wet', 15, 'Your weapon does {n}% more to a wet foe.'),
            ('thunder_strike', 'Thunder Strike', 1, 'fifth', 'clap', 1, 'Every fifth blow of your weapon stuns the '
             'foes beside you for a turn.')]),
        ('Skies', 'wind and weather', [
            ('rain_caller', 'Rain Caller', 2, 'svs', 'wet', 10, 'Your spells do {n}% more to a wet foe.'),
            ('tailwind', 'Tailwind', 1, 'push', 'gust', 1, 'Gust drives foes {n} tile further.'),
            ('storm_sense', 'Storm Sense', 1, 'stat', 'sight', 1, 'You see {n} tile further.'),
            ('static_field', 'Static Field', 2, 'cd', 'static', 1, 'Static recharges {n} turn sooner.'),
            ('lightning_rod', 'Lightning Rod', 1, 'flag', B, 1, 'Lightning that strikes you gives you half of it back '
             'as mana.'),
            ('ball_master', 'Ball Master', 1, 'cost', 'ball_lightning', 50, 'Ball Lightning costs {n}% less mana.')]),
    ],
    'restoration': [
        ('Mending', 'your healing', [
            ('gentle_hands', 'Gentle Hands', 3, 'heal', B, 5, 'Your healing heals {n}% more.'),
            ('quick_mend', 'Quick Mend', 1, 'cd', 'mend', 1, 'Mend recharges {n} turn sooner.'),
            ('long_renewal', 'Renewal', 2, 'buffdur', 'renewal', 30, 'Renewal lasts {n}% longer.'),
            ('shared_light', 'Shared Light', 1, 'flag', B, 1, 'Your healing also heals your hireling and your beast.'),
            ('second_breath', 'Second Breath', 1, 'flag', B, 1, 'Healing yourself while under a third of your life '
             'heals half as much again.'),
            ('martyrs_peace', "Martyr's Peace", 1, 'cd', 'martyrs_grace', 30, "Martyr's Grace recharges {n} turns "
             'sooner.')]),
        ('Dawnblade', 'your weapon', [
            ('dawnblade', 'Dawnblade', 1, 'imbue', 'heal', 1,
             'When you cast a Restoration spell, your weapon shines for 10 turns: about one blow in three heals you a '
             'little, twice as much if the foe is undead. While it lasts, no mana comes back.'),
            ('holy_edge', 'Holy Edge', 3, 'stat', 'undead', 10, 'Your weapon does {n}% more to the undead.'),
            ('sear_the_dead', 'Sear the Dead', 2, 'wproc', ('undead', 'fear'), 15, 'An undead foe your weapon '
             'strikes may flee: a {n}% chance.'),
            ('bright_steel', 'Bright Steel', 1, 'flag', B, 1, 'Each blow you strike heals the friends beside you 2 '
             'life.'),
            ('steadfast', 'Steadfast', 1, 'softer', 'undead', 15, 'The undead hit you {n}% softer.'),
            ('dawns_wrath', "Dawn's Wrath", 1, 'flag', B, 1, 'An undead foe that falls to you gives you back a tenth '
             'of your life.')]),
        ('Sanctuary', 'wards', [
            ('strong_ward', 'Strong Ward', 3, 'buffpow', 'ward', 15, 'Ward holds {n}% more.'),
            ('long_sanctuary', 'Sanctuary', 2, 'buffdur', 'sanctuary', 30, 'Sanctuary lasts {n}% longer.'),
            ('purity', 'Purity', 1, 'cd', 'purify', 4, 'Purify recharges {n} turns sooner.'),
            ('shelter', 'Shelter', 1, 'res', 'res_all', 4, '{n}% less damage of every element.'),
            ('calm', 'Calm', 1, 'flag', B, 1, 'Stamina comes back twice as fast while Sanctuary is on you.'),
            ('unbreakable_faith', 'Unbreakable Faith', 1, 'flag', B, 1, 'Once a day, a blow that would kill you '
             'leaves you standing on 1 life.')]),
    ],
    'shadow': [
        ('Curses', 'your curses', [
            ('deep_curse', 'Deep Curse', 3, 'fxdur', ('weaken', 'vuln'), 20, 'Your curses last {n}% longer.'),
            ('weak_hands', 'Weakness', 2, 'cd', 'weakness', 2, 'Curse of Weakness recharges {n} turns sooner.'),
            ('spreading_doom', 'Spreading Doom', 1, 'flag', B, 1, 'When a foe under Mark of Doom dies, the mark leaps '
             'to the nearest foe.'),
            ('dread', 'Dread', 2, 'fxdur', 'fear', 30, 'The fear you cause lasts {n}% longer.'),
            ('plague_bearer', 'Plague Bearer', 1, 'radius', 'plague', 1, 'Plague reaches {n} tile further.'),
            ('doom', 'Doom', 1, 'flag', B, 1, 'A foe both weakened and marked dies when it falls under 15% of its '
             'life.')]),
        ('Duskblade', 'your weapon', [
            ('duskblade', 'Duskblade', 1, 'imbue', 'drain', 1,
             'When you cast a Shadow spell, your weapon darkens for 10 turns: about one blow in three steals a little '
             'life. While it lasts, no mana comes back.'),
            ('black_edge', 'Black Edge', 3, 'wvs', 'cursed', 10, 'Your weapon does {n}% more to a cursed foe.'),
            ('thirst', 'Thirst', 2, 'drain', B, 25, 'Your spells steal {n}% more life.'),
            ('hex_strike', 'Hex Strike', 1, 'wproc', ('any', 'weaken'), 15, 'A blow of your weapon weakens the foe: a '
             '{n}% chance.'),
            ('dark_vigour', 'Dark Vigour', 1, 'flag', B, 1, 'Life you steal gives you as much stamina too.'),
            ('soul_blade', 'Soul Blade', 1, 'flag', B, 1, 'A foe your weapon slays gives you 3 life and 3 mana.')]),
        ('Bargain', "Morrak's price", [
            ('morraks_due', "Morrak's Due", 2, 'lifecost', B, 25, 'Your spells take {n}% less of your life.'),
            ('blood_price', 'Blood Price', 1, 'flag', B, 1, 'A spell paid for in life does 10% more damage.'),
            ('hollow_strength', 'Hollow Strength', 1, 'flag', B, 1, 'Under half your life, your Shadow spells do 15% '
             'more damage.'),
            ('debt_collector', 'Debt Collector', 1, 'flag', B, 1, 'You steal half as much life again from a cursed '
             'foe.'),
            ('dark_pact', 'Dark Pact', 2, 'cd', 'morraks_bargain', 5, "Morrak's Bargain recharges {n} turns sooner."),
            ('morraks_favour', "Morrak's Favour", 1, 'flag', B, 1, 'Once a day, Morrak pays the life a spell would '
             'take from you.')]),
    ],
    'necromancy': [
        ('Bones', 'bone and corpses', [
            ('hard_bone', 'Hard Bone', 3, 'buffpow', 'bone_shield', 15, 'Bone Shield holds {n}% more.'),
            ('long_spear', 'Bone Spear', 2, 'sdmg', 'bone_spear', 15, 'Bone Spear does {n}% more damage.'),
            ('prison_walls', 'Prison Walls', 1, 'tdur', 'bone_prison', 40, 'Bone Prison stands {n}% longer.'),
            ('splinters', 'Splinters', 1, 'flag', B, 1, 'Bone Spear makes the foes it strikes bleed.'),
            ('marrow', 'Marrow', 1, 'flag', B, 1, 'Each corpse a spell uses up gives you 5 life.'),
            ('ossuary_wall', 'Ossuary Wall', 1, 'cd', 'bone_prison', 6, 'Bone Prison recharges {n} turns sooner.')]),
        ('Graveblade', 'your weapon', [
            ('graveblade', 'Graveblade', 1, 'imbue', 'grave', 1,
             'When you cast a Necromancy spell, your weapon goes cold for 10 turns: about one blow in three slows the '
             'foe, and a foe it slays may rise as your skeleton. While it lasts, no mana comes back.'),
            ('cold_grip', 'Cold Grip', 3, 'wdmg', 'cold_dmg', 2, 'While Graveblade lasts, each blow does up to {n} '
             'more cold damage.'),
            ('withering_touch', 'Withering Touch', 2, 'wproc', ('any', 'weaken'), 10, 'A blow of your weapon weakens '
             'the foe: a {n}% chance.'),
            ('grave_reach', 'Grave Reach', 1, 'cd', 'grave_touch', 1, 'Grave Touch recharges {n} turn sooner.'),
            ('deathly_calm', 'Deathly Calm', 1, 'flag', B, 1, 'With one of your dead beside you, blows hurt you 15% '
             'less.'),
            ('reapers_due', "Reaper's Due", 1, 'flag', B, 1, 'Every foe your weapon slays while Graveblade lasts rises '
             'as your skeleton.')]),
        ('Legion', 'your dead', [
            ('strong_dead', 'Strong Dead', 3, 'thrall_hp', B, 15, 'Your dead have {n}% more life.'),
            ('one_more', 'One More', 1, 'summon_n', 'raise_skeleton', 1, 'Raise Skeleton raises {n} more, if the '
             'corpses are there.'),
            ('grave_mist', 'Grave Mist', 2, 'fxdur', 'poison', 30, 'The poison of your spells lasts {n}% longer.'),
            ('bone_armour', 'Bone Armour', 1, 'thrall_dmg', B, 20, 'Your dead hit {n}% harder.'),
            ('command', 'Command', 1, 'sumdur', B, 30, 'Your dead stay {n}% longer.'),
            ('army_unbound', 'Army Unbound', 1, 'flag', B, 1, 'Army of the Dead raises three skeletons out of bare '
             'ground when no corpse lies near.')]),
    ],
    'nature': [
        ('Grove', 'roots and thorns', [
            ('thornblade', 'Thornblade', 1, 'imbue', 'roots', 1,
             'When you cast a Nature spell, thorns grow on your weapon for 10 turns: about one blow in three roots '
             'the foe to the spot for a turn. While they last, no mana comes back.'),
            ('deep_roots', 'Deep Roots', 2, 'hold', B, 1, 'Your Nature spells hold foes {n} turn longer.'),
            ('bramble', 'Bramble', 2, 'field', B, 30, 'Roots and brambles you grow last {n}% longer.'),
            ('sharp_thorns', 'Sharp Thorns', 3, 'dmg', B, 5, 'Your Nature spells do {n}% more damage.'),
            ('awakened_grove', 'Awakened Grove', 1, 'cd', 'awaken_the_wood', 15, 'Awaken the Wood recharges {n} '
             'turns sooner.'),
            ('oak_wrath', 'Wrath of the Oak', 1, 'radius', 'wrath_of_oak', 1, 'Wrath of the Oak reaches {n} tile '
             'further.')]),
        ('Rain', 'growth and healing', [
            ('long_rain', 'Healing Rain', 2, 'buffdur', 'healing_rain', 30, 'Healing Rain lasts {n}% longer.'),
            ('green_mend', 'Green Mend', 3, 'heal', B, 5, 'Your healing heals {n}% more.'),
            ('thick_bark', 'Barkskin', 2, 'buffpow', 'barkskin', 15, 'Barkskin guards {n}% more.'),
            ('great_swarm', 'Swarm', 2, 'fxdur', 'swarm', 30, 'Swarm stings {n}% longer.'),
            ('life_blooms', 'Life Blooms', 1, 'cd', 'healing_rain', 5, 'Healing Rain recharges {n} turns sooner.'),
            ('spring', 'Spring', 1, 'buffpow', 'healing_rain', 30, 'Healing Rain heals {n}% more each turn.')]),
        ('Shapeshifter', 'the shapes of beasts', [
            ('wolf_shape', 'Wolf Shape', 1, 'teach', 'wolf_shape', 1, 'Teaches Wolf Shape. As a wolf, keys 1 and 2 '
             'are Bite and Lunge.'),
            ('thick_hide', 'Thick Hide', 3, 'shape_life', B, 10, 'In the shape of a beast you have {n}% more life.'),
            ('bear_shape', 'Bear Shape', 1, 'teach', 'bear_shape', 1, 'Teaches Bear Shape: slow to anger, hard to '
             'fell. As a bear, keys 1 and 2 are Maul and Roar.'),
            ('hawk_shape', 'Hawk Shape', 1, 'teach', 'hawk_shape', 1, 'Teaches Hawk Shape: weak, but you see far. As '
             'a hawk, keys 1 and 2 are Talons and Dive.'),
            ('long_shape', 'Long Shape', 2, 'buffdur', 'shapes', 30, 'Your shapes last {n}% longer.'),
            ('untamed', 'Untamed', 1, 'flag', B, 1, 'In the shape of a beast you can still use keys 3 to 6.')]),
    ],
    'beastcraft': [
        ('Bond', 'your beast', [
            ('strong_bond', 'Strong Bond', 3, 'beast_hp', B, 10, 'Your beast has {n}% more life.'),
            ('lick_wounds', 'Lick the Wounds', 2, 'sheal', 'mend_beast', 20, 'Lick the Wounds heals {n}% more.'),
            ('blood_bond', 'Bond of Blood', 2, 'buffdur', 'bond_of_blood', 30, 'Bond of Blood lasts {n}% longer.'),
            ('loyal', 'Loyal', 1, 'beast_dmg', B, 10, 'Your beast bites {n}% harder.'),
            ('second_life', 'Thick Fur', 1, 'beast_hp', B, 15, 'Your beast has {n}% more life.'),
            ('one_spirit', 'One Spirit', 1, 'flag', B, 1, 'What your beast strikes teaches you Beastcraft as if you '
             'had struck it.')]),
        ('Wild Hunt', 'you and your beast', [
            ('hunters_call', "Hunter's Call", 1, 'imbue', 'beast', 1,
             'When you cast a Beastcraft spell, you and your beast hunt as one for 10 turns: about one blow in three, '
             'your beast leaps at the same foe. While it lasts, no mana comes back.'),
            ('pincer', 'Pincer', 3, 'wvs', 'beast_beside', 5, 'Your weapon does {n}% more to a foe your beast stands '
             'beside.'),
            ('long_howl', 'Feral Howl', 2, 'fxdur', 'weaken', 30, 'The weakness your howls cause lasts {n}% longer.'),
            ('drag_down', 'Drag Down', 1, 'flag', B, 1, 'Your beast\'s bite may hold a foe to the spot for a turn.'),
            ('scent', 'Scent', 1, 'stat', 'sight', 1, 'You see {n} tile further.'),
            ('kill_together', 'Kill Together', 1, 'flag', B, 1, 'A foe struck by you and your beast dies when it falls '
             'under 20% of its life.')]),
        ('Pack', 'the pack', [
            ('long_call', 'Call a Wolf', 2, 'sumdur', B, 30, 'The wolves you call stay {n}% longer.'),
            ('great_roar', 'Alpha Roar', 2, 'radius', 'alpha_roar', 1, 'Alpha Roar reaches {n} tile further.'),
            ('pack_tactics', 'Pack Tactics', 1, 'thrall_dmg', B, 20, 'The wolves you call hit {n}% harder.'),
            ('wild_feed', 'Wild Feed', 1, 'cost', 'call_wolf', 25, 'Call a Wolf costs {n}% less mana.'),
            ('tamers_eye', "Tamer's Eye", 1, 'tame', B, 15, 'Taming works {n}% more often.'),
            ('spirit_pack', 'Spirit of the Pack', 1, 'cd', 'spirit_of_the_pack', 15, 'Spirit of the Pack recharges '
             '{n} turns sooner.')]),
    ],
    'warcraft': [
        ('Shield', 'shield and guard', [
            ('far_bash', 'Shield Bash', 2, 'push', 'shield_bash', 1, 'Shield Bash drives the foe {n} tile further.'),
            ('firm_block', 'Block', 3, 'stat', 'shield_armor', 6, 'With a shield in hand you have {n} more armour.'),
            ('long_wall', 'Shield Wall', 2, 'buffdur', 'shield_wall', 30, 'Shield Wall lasts {n}% longer.'),
            ('wall_of_iron', 'Wall of Iron', 1, 'res', 'res_all', 4, '{n}% less damage of every element.'),
            ('bulwark', 'Bulwark', 1, 'flag', B, 1, 'With a shield in hand, nothing stuns you.'),
            ('unbroken_line', 'Unbroken Line', 1, 'flag', B, 1, 'With a shield in hand, once a day a blow that would '
             'kill you leaves you standing on 1 life.')]),
        ('Battle', 'shouts and rage', [
            ('loud_cry', 'War Cry', 2, 'radius', 'warcry', 1, 'War Cry reaches {n} tile further.'),
            ('battle_rage', 'Battle Rage', 3, 'buffpow', 'rage', 15, 'Rage gives {n}% more.'),
            ('long_charge', 'Charge', 2, 'range', 'charge', 1, 'You charge {n} tile further.'),
            ('loud_rally', 'Rally', 2, 'buffpow', 'rally', 15, 'Rally gives {n}% more.'),
            ('bloodlust', 'Bloodlust', 1, 'kill_stamina', B, 5, 'Every foe you slay gives you {n} stamina.'),
            ('warlord', 'Warlord', 1, 'cd', 'rally', 10, 'Rally recharges {n} turns sooner.')]),
        ('Endurance', 'staying up', [
            ('deep_wind', 'Second Wind', 2, 'sheal', 'second_wind', 20, 'Second Wind heals {n}% more.'),
            ('hard_skin', 'Iron Skin', 3, 'buffpow', 'iron_skin', 15, 'Iron Skin holds {n}% more.'),
            ('heavy_training', 'Heavy Training', 1, 'flag', B, 1, 'Stamina comes back at the full pace in chain or '
             'plate.'),
            ('tough', 'Tough', 3, 'stat', 'life_pct', 5, 'You have {n}% more life.'),
            ('last_breath', 'Last Breath', 1, 'flag', B, 1, 'Under a quarter of your life, stamina comes back twice '
             'as fast.'),
            ('long_unbroken', 'Unbroken', 1, 'buffdur', 'unbroken', 50, 'Unbroken lasts {n}% longer.')]),
    ],
    'cunning': [
        ('Stealth', 'not being seen', [
            ('soft_steps', 'Soft Steps', 3, 'sneak', B, 15, 'While you sneak, foes are {n}% slower to notice you.'),
            ('unseen_strike', 'Unseen Strike', 2, 'ambush', B, 25, 'A first blow unseen does {n}% more.'),
            ('long_step', 'Shadowstep', 2, 'range', 'shadowstep', 1, 'Shadowstep reaches {n} tile further.'),
            ('quick_vanish', 'Vanish', 1, 'cd', 'vanish', 15, 'Vanish recharges {n} turns sooner.'),
            ('pickpocket', 'Pickpocket', 1, 'flag', B, 1, 'An unseen first blow may lift a few coins off the foe.'),
            ('ghost', 'Ghost', 1, 'flag', B, 1, 'A foe you slay with an unseen blow does not give you away: you are '
             'unseen for your next blow too.')]),
        ('Poison', 'your venom', [
            ('long_envenom', 'Envenom', 2, 'buffdur', 'envenom', 30, 'Envenom lasts {n}% longer.'),
            ('strong_venom', 'Strong Venom', 3, 'venom', B, 2, 'Your poison does {n} more each turn.'),
            ('lingering', 'Lingering', 1, 'venom_t', B, 3, 'Your poison lasts {n} turns longer.'),
            ('weakening_poison', 'Weakening Poison', 1, 'softer', 'poisoned', 20, 'Poisoned foes hit you {n}% softer.'),
            ('immune', 'Immune', 1, 'flag', B, 1, 'Poison does nothing to you.'),
            ('black_lotus', 'Black Lotus', 1, 'flag', B, 1, 'Your poison spreads to the foes beside the one you '
             'strike.')]),
        ('Traps', 'snares and caltrops', [
            ('strong_snare', 'Set Snare', 2, 'snare', B, 1, 'Your snares hold {n} turn longer.'),
            ('wide_caltrops', 'Caltrops', 2, 'tdur', 'caltrops', 30, 'Your caltrops lie {n}% longer.'),
            ('quick_snares', 'Quick Hands', 1, 'cd', 'set_snare', 3, 'Set Snare recharges {n} turns sooner.'),
            ('two_snares', 'Two Snares', 1, 'flag', B, 1, 'Set Snare lays two snares at once.'),
            ('cheap_snares', 'Recover', 1, 'cost', 'set_snare', 50, 'Set Snare costs {n}% less stamina.'),
            ('killing_field', 'Killing Field', 1, 'flag', B, 1, 'Your snares and caltrops also cut and poison who '
             'springs them.')]),
    ],
    'arcane': [
        ('Runes', 'runes on the ground', [
            ('warding_rune', 'Rune of Warding', 2, 'rune_hold', B, 1, 'A foe your Rune of Warding throws back stands '
             'stunned {n} turn longer.'),
            ('snaring_rune', 'Rune of Snaring', 1, 'teach', 'rune_of_snaring', 1, 'Teaches Rune of Snaring: who steps '
             'on it is held fast for 3 turns.'),
            ('quick_runes', 'Quick Runes', 1, 'cd', 'rune_of_warding', 3, 'Rune of Warding recharges {n} turns '
             'sooner.'),
            ('inscribed_armour', 'Inscribed Armour', 2, 'res', 'res_all', 4, '{n}% less damage of every element.'),
            ('many_runes', 'Many Runes', 1, 'flag', B, 1, 'Three of your runes may lie at once, not two.'),
            ('runeward', 'Runeward', 1, 'flag', B, 1, 'Your runes work twice before they fade.')]),
        ('Space', 'blink and gate', [
            ('far_blink', 'Blink', 2, 'range', 'blink', 1, 'You blink {n} tile further.'),
            ('long_gate', 'Gate', 2, 'tdur', 'gate', 30, 'Your gates stand {n}% longer.'),
            ('displace', 'Displace', 1, 'cd', 'dispel', 3, 'Dispel recharges {n} turns sooner.'),
            ('blink_strike', 'Blink Strike', 1, 'flag', B, 1, 'After a Blink, your next spell costs half.'),
            ('fold', 'Fold', 1, 'flag', B, 1, 'Your hireling blinks with you.'),
            ('astral_step', 'Astral Step', 1, 'flag', B, 1, 'Under half your life, Blink costs nothing.')]),
        ('Time', 'slow and quick', [
            ('long_slow', 'Slow', 2, 'fxdur', 'slow', 30, 'Your Slow lasts {n}% longer.'),
            ('haste_knot', 'Haste', 1, 'teach', 'haste', 1, 'Teaches Haste: for 5 turns you do two things in each.'),
            ('quickened_mind', 'Quickened Mind', 3, 'cdpct', B, 5, 'All your skills recharge {n}% sooner.'),
            ('double_counter', 'Counterspell', 2, 'counter', B, 1, 'Counterspell catches {n} more spell.'),
            ('echo', 'Echo', 1, 'flag', B, 1, 'Arcane Bolt strikes twice, the second time at half strength.'),
            ('long_stop', 'Stop Time', 1, 'hold', B, 1, 'Stop Time holds them {n} turn longer.')]),
    ],
}
# the rule of a pure class (11) and of each pair (55): one fight rule each, given with the name (classes.py). Each is
# a list of effects in the trees' own kinds, as if it were a knot with one point: (kind, argument, amount, school)
R = lambda kind, arg=None, v=1, line=None: (kind, arg, v, line)      # noqa: E731
RULES = {
    'Pyromancer': ('The burning you cause lasts half as long again, and the fire of a burning foe that dies leaps to '
                   'one beside it half the time.', [R('fxdur', 'burn', 50, 'fire'), R('leap_burn', None, 50)]),
    'Rimecaller': ('Your ice walls stand twice as long, and a slowed foe your spells strike is sometimes frozen.',
                   [R('tdur', 'ice_wall', 100, 'frost'), R('sproc', ('slow', 'freeze'), 20)]),
    'Stormcaller': ('Chain Lightning leaps to one foe more, water or not.', [R('jumps', 'chain', 1, 'storm')]),
    'Cleric': ('Every healing you cast on yourself also lays a small Ward on you.', [R('flag', 'cleric')]),
    'Warlock': ('Morrak takes a quarter less of your life, and your spells steal a quarter more.',
                [R('lifecost', None, 25, 'shadow'), R('drain', None, 25, 'shadow')]),
    'Necromancer': ('Raise Skeleton raises one more, if the corpses are there.',
                    [R('summon_n', 'raise_skeleton', 1, 'necromancy')]),
    'Druid': ('Nature is never weaker for you: not in the desert, on ice or under the ground.', [R('flag', 'druid')]),
    'Beastmaster': ('Your beast has 15% more life and bites 15% harder.', [R('beast_hp', None, 15),
                                                                          R('beast_dmg', None, 15)]),
    'Warrior': ('Stamina comes back faster, at the full pace in chain or plate.', [R('flag', 'heavy_training'),
                                                                                  R('stamina_plus', None, 1)]),
    'Arcanist': ('What you take away with Dispel or Counterspell gives you 8 mana.', [R('flag', 'arcanist')]),
    'Rogue': ('A foe that does not see you coming takes your first blow three times over, not twice.',
              [R('flag', 'rogue')]),
    'Elementalist': ('Your spells do 30% more to a frozen foe: the ice cracks.', [R('svs', 'frozen', 30)]),
    'Stormbrand': ('Lightning on a burning foe bursts: the foes beside it take fire.', [R('flag', 'stormbrand')]),
    'Sunpriest': ('Your fire does double to the undead, as the light does.', [R('flag', 'sunpriest')]),
    'Hexblade': ('A foe both burning and cursed gives you life back from its burn.', [R('flag', 'hexblade')]),
    'Pyre Lord': ('A fire spell that strikes a foe beside a corpse sets the corpse off: fire bursts out round it.',
                  [R('flag', 'pyre_lord')]),
    'Ashwarden': ('Burning ground does you no harm, and heals you 2 life a turn.', [R('flag', 'walk_in_fire'),
                                                                                   R('flag', 'ash_walker')]),
    'Firetamer': ("Your beast's bite sets the foe alight.", [R('flag', 'firetamer')]),
    'Firebrand': ('While Rage or Battle Drill is on you, your blows burn.', [R('flag', 'firebrand')]),
    'Winterstorm': ('A frozen foe carries lightning as if it stood in water.', [R('flag', 'winterstorm')]),
    'Snowsaint': ('Who strikes you while your Ward holds is slowed.', [R('flag', 'snowsaint')]),
    'Rimehex': ('Your curses do not wear off on a slowed foe while it stays slowed, every other turn.',
                [R('flag', 'rimehex')]),
    'Lich': ("Your dead's blows slow the foe.", [R('flag', 'lich')]),
    'Rimewarden': ('Your roots and stuns hold a turn longer.', [R('hold', None, 1, 'nature')]),
    'Winterwolf': ("Your beast's bite slows the foe.", [R('flag', 'winterwolf')]),
    'Iceguard': ('With Brace and Frost Armor both on you, who you strike may freeze.', [R('flag', 'iceguard')]),
    'Stormsaint': ('Healing yourself throws a spark at the nearest foe.', [R('flag', 'stormsaint')]),
    'Darkstorm': ('A cursed foe passes your lightning on one leap further.', [R('flag', 'darkstorm')]),
    'Galvanist': ('Lightning that strikes beside a corpse makes it get up and fight for you a little while.',
                  [R('flag', 'galvanist')]),
    'Skyshaper': ('Healing Rain soaks the foes round you: they count as wet.', [R('flag', 'skyshaper')]),
    'Thunderhide': ('Where your beast bites, a spark leaps to another foe.', [R('flag', 'thunderhide')]),
    'Stormblade': ('Your Charge ends in a small Thunderclap: the foes beside you are stunned for a turn.',
                   [R('flag', 'stormblade_pair')]),
    'Penitent': ('Life you steal heals your hireling and your beast too, half as much.', [R('flag', 'penitent')]),
    'Gravekeeper': ('Each corpse a spell uses up gives you 4 mana.', [R('flag', 'gravekeeper')]),
    'Lifewarden': ('On grass and in the woods, the healing that comes over time heals twice as much.',
                   [R('flag', 'lifewarden')]),
    'Shepherd': ('Your healing also heals your beast and your hireling.', [R('flag', 'shared_light')]),
    'Paladin': ('War Cry heals you and your company a little.', [R('flag', 'paladin')]),
    'Dread Lord': ('A cursed foe that dies gets up again as your skeleton.', [R('flag', 'dread_lord')]),
    'Blightcaller': ('Foes in your brambles and roots catch the plague.', [R('flag', 'blightcaller')]),
    'Nightstalker': ("Your beast's bite steals life for it.", [R('flag', 'nightstalker')]),
    'Reaver': ('Your stamina skills steal a tenth of the harm they do as life.', [R('flag', 'reaver')]),
    'Rotwood': ('Where a foe of yours falls, brambles grow.', [R('flag', 'rotwood')]),
    'Bonetamer': ('Your dead and the beasts you call stay half as long again.', [R('sumdur', None, 50)]),
    'Bone Captain': ('War Cry and Rally make your dead hit a fifth harder.', [R('flag', 'bone_captain')]),
    'Wildkin': ('On grass and in the woods your beast is a fifth stronger.', [R('flag', 'wildkin')]),
    'Thornguard': ('With Barkskin and Iron Skin both on you, who strikes you is cut by thorns.',
                   [R('flag', 'thornguard')]),
    'Warhound': ('War Cry and Rally rouse your beast to fury.', [R('flag', 'warhound')]),
    'Firestarter': ('Your snares and caltrops set who springs them alight.', [R('flag', 'firestarter')]),
    'Rimeknife': ('Your poison slows as well.', [R('flag', 'rimeknife')]),
    'Sparkthief': ('A sprung snare or caltrop throws a spark at another foe.', [R('flag', 'sparkthief')]),
    'Hedge Doctor': ('Poison does nothing to you.', [R('flag', 'immune')]),
    'Shade': ('A cursed foe does not see you coming.', [R('flag', 'shade')]),
    'Graverobber': ('A foe you slay unseen gets up again as your skeleton.', [R('flag', 'graverobber')]),
    'Poisoner': ('Foes in your brambles and roots are poisoned.', [R('flag', 'poisoner')]),
    'Poacher': ('Your beast too strikes a foe that does not see it coming twice as hard.', [R('flag', 'poacher')]),
    'Cutthroat': ('A War Cry soon after an unseen blow sends the foes fleeing.', [R('flag', 'cutthroat')]),
    'Spellfire': ('A foe whose magic you dispel catches fire.', [R('flag', 'spellfire')]),
    'Rimeweaver': ('A slowed foe your spells strike is sometimes frozen.', [R('sproc', ('slow', 'freeze'), 20)]),
    'Stormweaver': ('Blink leaves a thunderclap where you stood.', [R('flag', 'stormweaver')]),
    'Sanctifier': ('While your Ward holds, it also catches the first spell cast at you.', [R('flag', 'sanctifier')]),
    'Voidcaller': ('A spell you catch with Counterspell gives you life.', [R('flag', 'voidcaller')]),
    'Soulbinder': ('Your dead come with you through your Blink and your Gate.', [R('flag', 'soulbinder')]),
    'Leywalker': ('A rune that goes off grows roots round it.', [R('flag', 'leywalker')]),
    'Spiritcaller': ('Your beast blinks with you.', [R('flag', 'spiritcaller')]),
    'Spellbreaker': ('Your Charge takes the magic off the foe it strikes.', [R('flag', 'spellbreaker')]),
    'Trickster': ('Blink takes you behind the nearest foe, and your next blow is unseen.', [R('flag', 'trickster')]),
}
KNOTS = {}                      # id -> (line, branch index, place in the branch, the knot)
for _line, _brs in TREES.items():
    for _b, (_bn, _what, _ks) in enumerate(_brs):
        for _i, _k in enumerate(_ks):
            assert _k[0] not in KNOTS, _k[0]
            KNOTS[_k[0]] = (_line, _b, _i, _k)
RULE_KNOTS = {}                 # a rule's name -> its effects as knots: (id, name, 1, kind, arg, amount, text)
for _name, (_text, _fx) in RULES.items():
    _ks = []
    for _j, (_kind, _arg, _v, _ln) in enumerate(_fx):
        _kid = _arg if _kind == 'flag' else f'rule_{_name.lower().replace(" ", "_")}_{_j}'
        _ks.append((_kid, _name, 1, _kind, _arg if _kind != 'flag' else None, _v, _text))
        if _kind != 'flag':
            KNOTS[_kid] = (_ln, -1, -1, _ks[-1])
    RULE_KNOTS[_name] = _ks
IMBUES = {kid: (line, k[4]) for kid, (line, _b, _i, k) in KNOTS.items() if k[3] == 'imbue'}
SHAPE_SKILLS = ('wolf_shape', 'bear_shape', 'hawk_shape', 'wild_shape', 'wildheart')
CURSES = ('weaken', 'vuln', 'plague', 'fear')


# ------------------------------------------------------------------ points
def tree(game):
    return game.player.__dict__.setdefault('tree', {})


def pts(game, kid):
    line = KNOTS[kid][0]
    return tree(game).get(line, {}).get(kid, 0)


def earned(game, line):
    return game.player.disc.get(line, [0, 0])[0] // EVERY


def spent(game, line):
    return sum(tree(game).get(line, {}).values())


def free(game, line):
    return max(0, earned(game, line) - spent(game, line))


def mine(game):
    """The knots you have points in, with their points: [(knot, points)], only of your classes; and the rule of
    your pure class or your pair, as knots with one point."""
    from . import classes as CL
    out = []
    for line in CL.classes(game):
        for kid, n in tree(game).get(line, {}).items():
            if n and kid in KNOTS:
                out.append((KNOTS[kid][3], n))
    name = CL.rule_name(game)
    out += [(k, 1) for k in RULE_KNOTS.get(name, ())]
    return out


def total(game, kind, arg=None):
    return sum(k[5] * n for k, n in mine(game) if k[3] == kind and (arg is None or k[4] == arg))


def has(game, kid):
    return any(k[0] == kid for k, _n in mine(game))


def line_of(k):
    """The school a knot (or a rule's effect) belongs to; None for a rule's own flags."""
    return KNOTS[k[0]][0] if k[0] in KNOTS else None


def can_rest_spend(game):
    """Points are spent where you rested: an inn's bed or your camp, until you move on."""
    p = game.player
    return getattr(p, 'rest_spot', None) == (game.cur, p.x, p.y)


def rested(game):
    p = game.player
    p.rest_spot = (game.cur, p.x, p.y)
    p.faith_day = p.__dict__.get('faith_day', -1)
    from . import classes as CL
    if any(free(game, line) for line in CL.classes(game)):
        from . import guide as GDE
        GDE.tip(game, 'tree')


def opens(game, kid):
    """Whether a point may go in this knot now: None, or why not."""
    line, b, i, k = KNOTS[kid]
    if pts(game, kid) >= k[2]:
        return 'It is full.'
    if i and not pts(game, TREES[line][b][2][i - 1][0]):
        return f'First a point in {TREES[line][b][2][i - 1][1]}.'
    if not free(game, line):
        return f'No points left: one comes every {EVERY} ranks in {SK.DISCIPLINES[line]["name"]}.'
    if not can_rest_spend(game):
        return 'Points are spent where you rest: an inn\'s bed or your camp.'
    return None


def spend(game, kid):
    why = opens(game, kid)
    if why:
        return why
    line, _b, _i, k = KNOTS[kid]
    t = tree(game).setdefault(line, {})
    t[kid] = t.get(kid, 0) + 1
    if k[3] == 'teach' and k[4] not in game.player.known:
        SK.learn(game, k[4])
    game.clamp_vitals()
    return None


def unlearn_cost(game):
    return sum(spent(game, line) for line in tree(game)) * RESPEC


def unlearn(game):
    """A temple takes all your points back, for coin. The shapes a knot taught go with them."""
    p = game.player
    cost = unlearn_cost(game)
    if not cost or p.gold < cost:
        return False
    p.gold -= cost
    for line, t in tree(game).items():
        for kid in t:
            k = KNOTS.get(kid, (0, 0, 0, (0, 0, 0, '')))[3]
            if k[3] == 'teach' and k[4] in p.known:
                p.known.remove(k[4])
                p.bar = [None if s == k[4] else s for s in p.bar]
    p.tree = {}
    game.clamp_vitals()
    return True


def text(k, n):
    return k[6].format(n=k[5] * max(1, n))


# ------------------------------------------------------------------ what a skill becomes
def tuned(game, sk):
    """The skill as your tree makes it: a copy with its numbers changed, or the skill itself."""
    ks = [(k, n) for k, n in mine(game)]
    if not ks or sk.weapon_skill:
        return sk
    c = copy.copy(sk)
    c.fx = dict(sk.fx)
    line = sk.line
    own = [(k, n) for k, n in ks if line_of(k) == line]

    def of(kind, arg=B, mine_=own):
        return sum(k[5] * n for k, n in mine_ if k[3] == kind and (arg is B or k[4] == arg))
    c.cd = max(1, round((sk.cd - of('cd', sk.id)) * (1 - total(game, 'cdpct') / 100)))
    c.cost = sk.cost * (1 - of('cost', sk.id) / 100)
    for kind, arg, pct in [(k[3], k[4], k[5] * n) for k, n in own if k[3] == 'fxdur']:
        for fk in ((arg,) if isinstance(arg, str) else arg):
            v = c.fx.get(fk)
            if v is None:
                continue
            if isinstance(v, tuple):
                c.fx[fk] = v[:-1] + (max(1, round(v[-1] * (1 + pct / 100))),)
            else:
                c.fx[fk] = max(1, round(v * (1 + pct / 100)))
    hold = of('hold')
    for fk in ('stun', 'freeze'):
        if hold and fk in c.fx:
            c.fx[fk] += hold
    if sk.buff:
        k_, b_, br_, t_ = sk.buff
        if k_ == 'counter':
            b_ += total(game, 'counter')
        pw, du = of('buffpow', sk.id) / 100, of('buffdur', sk.id) / 100
        if sk.id in SHAPE_SKILLS:
            du += of('buffdur', 'shapes') / 100
        c.buff = (k_, b_ * (1 + pw), br_ * (1 + pw), round(t_ * (1 + du)))
    if sk.shape:
        nm, dp, dr_, t_ = sk.shape
        c.shape = (nm, dp, dr_, round(t_ * (1 + of('buffdur', 'shapes') / 100)))
    if sk.field:
        c.field = (sk.field[0], round(sk.field[1] * (1 + of('field') / 100)))
    c.tdur = 1 + of('tdur', sk.id) / 100
    c.radius = sk.radius + of('radius', sk.id)
    c.jumps = sk.jumps + of('jumps', sk.id)
    c.range = sk.range + of('range', sk.id)
    c.push_more = of('push', sk.id)
    if sk.summon:
        k_, n_, t_ = sk.summon
        c.summon = (k_, n_ + of('summon_n', sk.id), round(t_ * (1 + total(game, 'sumdur') / 100)))
    if sk.heal:
        h = (total(game, 'heal') + of('sheal', sk.id)) / 100
        c.heal = (sk.heal[0] * (1 + h), sk.heal[1] * (1 + h))
    less = of('lifecost') / 100
    c.life_cost = round(sk.life_cost * (1 - less))
    c.life_frac = sk.life_frac * (1 - less)
    c.drain = sk.drain * (1 + of('drain') / 100)
    c.tmul = (1 + of('dmg') / 100) * (1 + of('sdmg', sk.id) / 100)
    return c


def free_cast(game, sk):
    """Heart of Fire: the first fire spell of a fight costs nothing."""
    return sk.line == 'fire' and has(game, 'heart_of_fire') and getattr(game.player, 'fire_free', True)


def on_cast(game, sk):
    """After a skill is used: the imbue of its school wakes on your weapon; Heart of Fire is spent; the pair rules
    that ride on a shout, a charge or the rain."""
    p = game.player
    if free_cast(game, sk):
        p.fire_free = False
    r = p.disc.get(sk.line, [0, 0])[0]
    near = [o for o in game.visible_hostiles() if cheb(o.x, o.y, p.x, p.y) <= 1]
    if sk.id == 'charge' and has(game, 'stormblade_pair'):
        for o in near:
            o.hold = max(o.hold, 1)
        game.fx('burst', x=p.x, y=p.y, r=1, col=SK.STORM, signs='+∙')
    if sk.id == 'charge' and has(game, 'spellbreaker'):
        from . import arts as ART
        for o in near:
            o.mods = [md for md in o.mods if md not in ART.MAGIC_MODS]
    if sk.id in ('warcry', 'rally'):
        if has(game, 'paladin') and sk.id == 'warcry':
            game.heal(5 + r // 5, show=True)
            heal_party(game, 5 + r // 5)
        if has(game, 'bone_captain'):
            for o in getattr(game, 'thralls', []):
                if o in game.map.mons and not getattr(o, 'rallied', False):
                    o.rallied = True
                    o.dmg = (round(o.dmg[0] * 1.2), round(o.dmg[1] * 1.2))
        if has(game, 'warhound'):
            from . import mercs as MC
            for mc in MC.beasts(game):
                mc.fury = max(mc.fury, 10)
        if has(game, 'cutthroat') and getattr(p, 'ambush_turn', -9) >= game.turn - 3 and sk.id == 'warcry':
            for o in [o for o in game.visible_hostiles() if cheb(o.x, o.y, p.x, p.y) <= 3]:
                o.effects['fear'] = [4, 0]
    if sk.id == 'healing_rain' and has(game, 'skyshaper'):
        for o in [o for o in game.visible_hostiles() if cheb(o.x, o.y, p.x, p.y) <= 5]:
            o.effects['soaked'] = [10, 0]
    if SK.pool(sk) != 'mana':
        return
    for kid, (line, _what) in IMBUES.items():
        if line == sk.line and has(game, kid):
            name = KNOTS[kid][3][1]
            p.buffs = [b for b in p.buffs if b[0] != 'imbue'] + [['imbue', 0, IMBUE_TURNS, name]]


def imbue(game):
    """The imbue on your weapon now: (knot, what it does), or None."""
    b = next((b for b in game.player.buffs if b[0] == 'imbue'), None)
    if not b:
        return None
    kid = next((k for k in IMBUES if KNOTS[k][3][1] == b[3]), None)
    return (kid, IMBUES[kid][1]) if kid else None


# ------------------------------------------------------------------ your numbers
def stats(game, s):
    for k, n in mine(game):
        kind, arg, v = k[3], k[4], k[5] * n
        if kind == 'res':
            s[arg] = s.get(arg, 0) + v
        elif kind == 'stat' and arg == 'shield_armor':
            from . import weapons as WP
            if WP.has_shield(game):
                s['armor'] += v
        elif kind == 'stat':
            s[arg] = s.get(arg, 0) + v
    from . import anim as AN
    p = game.player
    if AN.shape_of(p) == 'hawk':
        s['sight'] = s.get('sight', 0) + 3
    labels = {b[3] for b in p.buffs}
    if has(game, 'firebrand') and labels & {'Rage', 'Battle Drill'}:
        s['fire_dmg'] = s.get('fire_dmg', 0) + 4 + p.disc['fire'][0] // 8
    if has(game, 'thornguard') and {'Barkskin', 'Iron Skin'} <= labels:
        s['thorns'] = s.get('thorns', 0) + 5 + p.disc['nature'][0] // 8
    if has(game, 'lifewarden') and s.get('regen') and _green(game):
        s['regen'] *= 2
    im = imbue(game)
    if im:
        line = KNOTS[im[0]][0]
        for k, n in mine(game):
            if k[3] == 'wdmg' and line_of(k) == line:
                s[k[4]] = s.get(k[4], 0) + k[5] * n


def life_mult(game):
    from . import anim as AN
    m = 1 + total(game, 'stat', 'life_pct') / 100
    if AN.shape_of(game.player):
        m += total(game, 'shape_life') / 100
    return m


# ------------------------------------------------------------------ in a fight
def spell_mult(game, sk, mon):
    m = getattr(sk, 'tmul', 1)
    for k, n in mine(game):
        if k[3] == 'svs' and _is(game, mon, k[4]):
            m *= 1 + k[5] * n / 100
    p = game.player
    if (sk.life_cost or sk.life_frac) and has(game, 'blood_price'):
        m *= 1.1
    if sk.line == 'shadow' and has(game, 'hollow_strength') and p.life < game.stats()['max_life'] / 2:
        m *= 1.15
    if sk.line == 'fire' and has(game, 'sunpriest') and _is(game, mon, 'undead'):
        m *= 2
    return m


def weapon_mult(game, mon):
    m = 1
    for k, n in mine(game):
        if k[3] == 'wvs' and _is(game, mon, k[4]):
            m *= 1 + k[5] * n / 100
    return m


def softer(game, mon):
    """What is left of a foe's blow, by the knots that soften it."""
    m = 1
    for k, n in mine(game):
        if k[3] == 'softer' and _is(game, mon, k[4]):
            m *= 1 - k[5] * n / 100
    return m


def _is(game, mon, cond):
    from . import spellmap as SM
    if cond == 'burn':
        return 'burn' in mon.effects
    if cond == 'slow':
        return 'slow' in mon.effects
    if cond == 'frozen':
        return getattr(mon, 'frozen', False) and mon.hold > 0
    if cond == 'wet':
        return SM.wet(game, mon)
    if cond == 'cursed':
        return any(c in mon.effects for c in CURSES)
    if cond == 'undead':
        return SM.undead(mon)
    if cond == 'burning_ground':
        from . import data as D
        return game.map.tile(mon.x, mon.y) == D.BURNING
    if cond == 'poisoned':
        return 'poison' in mon.effects
    if cond == 'beast_beside':
        return any(cheb(b.x, b.y, mon.x, mon.y) <= 1 for b in _beasts(game))
    return cond == 'any'


def _beasts(game):
    from . import mercs as MC
    return [mc.body for mc in MC.beasts(game) if mc.state == 'alive' and mc.body is not None
            and mc.body in game.map.mons]


def on_weapon_hit(game, mon, dead):
    """After a blow of your weapon: the imbue, the knots that ride on a blow, every fifth blow."""
    p = game.player
    if not mine(game):
        return
    r_ = lambda line: p.disc.get(line, [0, 0])[0]      # noqa: E731
    im = imbue(game)
    if dead:
        _weapon_kill(game, mon, im)
        return
    if im and random.random() < 1 / 3:
        _imbue_blow(game, mon, im[1], r_(KNOTS[im[0]][0]))
    if has(game, 'iceguard') and {'Brace', 'Frost Armor'} <= {b[3] for b in p.buffs} and random.random() < .25:
        _effect(game, mon, 'freeze')
    for k, n in mine(game):
        if k[3] == 'wproc' and mon in game.map.mons and _is(game, mon, k[4][0]) and random.random() < k[5] * n / 100:
            _effect(game, mon, k[4][1])
    if has(game, 'bright_steel'):
        from . import mercs as MC
        for mc in MC.party(game):
            if mc.body is not None and cheb(mc.body.x, mc.body.y, p.x, p.y) <= 1:
                mx = MC.stats(game, mc)['max_hp']
                mc.hp = min(mx, mc.hp + 2)
                MC.refresh_body(game, mc)
    fifth = [k for k, n in mine(game) if k[3] == 'fifth']
    if fifth:
        p.blows = getattr(p, 'blows', 0) + 1
        if p.blows % 5 == 0 and mon in game.map.mons:
            for k in fifth:
                if k[4] == 'freeze':
                    _effect(game, mon, 'freeze')
                else:
                    for o in [o for o in game.visible_hostiles() if cheb(o.x, o.y, p.x, p.y) <= 1]:
                        o.hold = max(o.hold, 1)
                    game.fx('burst', x=p.x, y=p.y, r=1, col=SK.STORM, signs='+∙')


def _effect(game, mon, what):
    if what == 'freeze':
        mon.hold = max(mon.hold, 2)
        mon.frozen = True
        game.num(mon.x, mon.y, '*', (159, 216, 255))
    elif what in ('fear', 'weaken', 'slow'):
        mon.effects[what] = [3, 0]
        game.num(mon.x, mon.y, what, (176, 110, 255) if what != 'slow' else (159, 216, 255))


def _imbue_blow(game, mon, what, r):
    p = game.player
    if what == 'burn':
        mon.effects['burn'] = [4, max(1, round((4 + .35 * r) / 3))]
        game.num(mon.x, mon.y, '*', SK.FIRE)
    elif what == 'slow':
        _effect(game, mon, 'slow')
    elif what == 'spark':
        from . import spellmap as SM
        near = [o for o in game.visible_hostiles() if o is not mon and cheb(o.x, o.y, mon.x, mon.y) <= 2]
        if near:
            o = random.choice(near)
            dmg = (2 + r // 6) * (2 if SM.wet(game, o) else 1)
            game.fx('zap', cells=game.cells_between((mon.x, mon.y), (o.x, o.y)), col=SK.STORM)
            game.damage_mon(o, dmg, col=SK.STORM, elem='lightning')
    elif what == 'heal':
        from . import spellmap as SM
        game.heal((2 + r // 15) * (2 if SM.undead(mon) else 1), show=True)
    elif what == 'drain':
        n = 2 + r // 15
        game.damage_mon(mon, n, col=SK.DARK)
        game.heal(n, show=True)
        stolen(game, n)
    elif what == 'grave':
        _effect(game, mon, 'slow')
    elif what == 'roots':
        mon.hold = max(mon.hold, 1)
        game.num(mon.x, mon.y, '"', SK.LEAF)
    elif what == 'beast':
        from . import mercs as MC
        for b in _beasts(game):
            if cheb(b.x, b.y, mon.x, mon.y) <= 4 and mon in game.map.mons:
                mc = MC.of_body(game, b)
                if mc:
                    MC.strike(game, mc, b, mon, MC.stats(game, mc))


def _weapon_kill(game, mon, im):
    p = game.player
    if im and im[1] == 'burn' and has(game, 'pyre_blade'):
        for o in [o for o in game.visible_hostiles() if cheb(o.x, o.y, mon.x, mon.y) <= 1]:
            o.effects['burn'] = [4, 3]
        game.fx('burst', x=mon.x, y=mon.y, r=1, col=SK.FIRE, signs='*∙')
    if im and im[1] == 'grave' and (has(game, 'reapers_due') or random.random() < .25):
        from . import mercs as MC
        if not game.occupied(game.map, mon.x, mon.y):
            sl = getattr(game.map, 'slain', [])
            if sl and sl[-1][1:3] == (mon.x, mon.y):
                sl.pop()
            o = MC.thrall(game, 'skeleton', mon.x, mon.y, 20, 'Risen Skeleton')
            thrall_made(game, o)
            game.msg(f'{mon.name} gets up again, and it is yours.', 'good')
    if has(game, 'soul_blade'):
        game.heal(3)
        s = game.stats()
        p.mana = min(s['max_mana'], p.mana + 3)
    if has(game, 'arc_step'):
        near = [o for o in game.visible_hostiles() if cheb(o.x, o.y, mon.x, mon.y) <= 4]
        if near:
            o = min(near, key=lambda o: cheb(o.x, o.y, mon.x, mon.y))
            game.fx('zap', cells=game.cells_between((mon.x, mon.y), (o.x, o.y)), col=SK.STORM)
            game.damage_mon(o, 4 + p.disc['storm'][0] // 5, col=SK.STORM, elem='lightning')


def after_spell_hit(game, mon, sk):
    if mon not in game.map.mons:
        return
    r = game.player.disc.get(sk.line, [0, 0])[0]
    for k, n in mine(game):
        if k[3] == 'sproc' and _is(game, mon, k[4][0]) and random.random() < k[5] / 100:
            _effect(game, mon, k[4][1])
    if sk.line == 'storm' and has(game, 'stormbrand') and 'burn' in mon.effects:
        game.fx('burst', x=mon.x, y=mon.y, r=1, col=SK.FIRE, signs='*∙')
        for o in [o for o in game.visible_hostiles() if o is not mon and cheb(o.x, o.y, mon.x, mon.y) <= 1]:
            game.damage_mon(o, 3 + r // 8, col=SK.FIRE, elem='fire')
    if (sk.line == 'fire' and has(game, 'pyre_lord')) or (sk.line == 'storm' and has(game, 'galvanist')):
        _corpse_by(game, mon, sk.line, r)
    if mon not in game.map.mons:
        return
    if sk.id == 'ice_lance' and has(game, 'absolute_zero'):
        _effect(game, mon, 'freeze')
    if sk.id == 'bone_spear' and has(game, 'splinters'):
        mon.effects['bleed'] = [4, 2 + game.player.disc['necromancy'][0] // 15]
    if sk.line == 'storm' and has(game, 'static_mind') and sk.mode == 'chain':
        p = game.player
        p.mana = min(game.stats()['max_mana'], p.mana + 1)


def second_shard(game, sk, t, r):
    """Sharp Shards: Frost Shard strikes a second foe near the first. Echo: Arcane Bolt strikes again."""
    if sk.id == 'arcane_bolt' and has(game, 'echo') and t in game.map.mons:
        game.damage_mon(t, max(1, SK._spell_dmg(game, sk, r) // 2), col=sk.color)
        return
    if sk.id != 'frost_shard' or not has(game, 'sharp_shards'):
        return
    near = [o for o in game.visible_hostiles() if o is not t and cheb(o.x, o.y, t.x, t.y) <= 2]
    if near:
        o = random.choice(near)
        game.fx('trail', cells=game.cells_between((t.x, t.y), (o.x, o.y)), col=sk.color)
        SK._hit(game, o, sk, r)


def drain_mult(game, mon):
    return 1.5 if has(game, 'debt_collector') and _is(game, mon, 'cursed') else 1


def stolen(game, n):
    """Dark Vigour: life you steal gives you stamina too."""
    if n > 0 and has(game, 'dark_vigour'):
        p = game.player
        p.stamina = min(game.stats()['max_stamina'], p.stamina + n)
    if n > 1 and has(game, 'penitent'):
        heal_party(game, n // 2)


def marrow(game, n):
    """Marrow: each corpse a spell uses up gives you life."""
    if n and has(game, 'marrow'):
        game.heal(5 * n, show=True)
    if n and has(game, 'gravekeeper'):
        p = game.player
        p.mana = min(game.stats()['max_mana'], p.mana + 4 * n)


def heal_mult(game):
    p = game.player
    if has(game, 'second_breath') and p.life < game.stats()['max_life'] / 3:
        return 1.5
    return 1


def on_kill(game, mon):
    """A foe falls: mana from the school that slew it, stamina, and curses and fire that leap on."""
    p = game.player
    if not mine(game):
        return
    sk = getattr(game, '_skill', None)
    s = game.stats()
    if sk is not None:
        n = sum(k[5] * c for k, c in mine(game) if k[3] == 'kill_mana' and line_of(k) == sk.line)
        if n:
            p.mana = min(s['max_mana'], p.mana + n)
    n = total(game, 'kill_stamina')
    if n:
        p.stamina = min(s['max_stamina'], p.stamina + n)
    near = [o for o in game.map.mons if not o.is_npc and not getattr(o, 'ally', False) and o is not mon
            and cheb(o.x, o.y, mon.x, mon.y) <= 3]
    if 'vuln' in mon.effects and has(game, 'spreading_doom') and near:
        o = min(near, key=lambda o: cheb(o.x, o.y, mon.x, mon.y))
        o.effects['vuln'] = list(mon.effects['vuln'])
        game.num(o.x, o.y, 'doom', SK.DARK)
    n = total(game, 'leap_burn')
    if 'burn' in mon.effects and n and random.random() < n / 100:
        close = [o for o in near if cheb(o.x, o.y, mon.x, mon.y) <= 1 and 'burn' not in o.effects]
        if close:
            o = random.choice(close)
            o.effects['burn'] = list(mon.effects['burn'])
            game.num(o.x, o.y, '*', SK.FIRE)
    from . import spellmap as SM
    if has(game, 'dawns_wrath') and SM.undead(mon):
        game.heal(max(1, s['max_life'] // 10), show=True)
    unseen = getattr(mon, 'ambushed', False) and getattr(p, 'ambush_turn', -9) == game.turn
    if (has(game, 'dread_lord') and any(c in mon.effects for c in CURSES)) or (has(game, 'graverobber') and unseen):
        rise(game, mon)
    if has(game, 'ghost') and unseen:
        p.buffs = [b for b in p.buffs if b[0] != 'ambush'] + [['ambush', 1, 5, 'Ghost']]
    if has(game, 'rotwood') and not mon.is_npc:
        from . import data as D
        SM.place(game, game.map, mon.x, mon.y, D.BRAMBLE, 8, 2)


def finish(game, mon):
    """Doom and Kill Together: a foe brought low enough simply dies. Returns True if it did."""
    if mon.hp <= 0 or mon not in game.map.mons or getattr(mon, 'is_boss', False):
        return False
    low = 0
    if has(game, 'doom') and 'weaken' in mon.effects and 'vuln' in mon.effects:
        low = .15
    if has(game, 'kill_together') and getattr(mon, 'beast_hit', -9) >= game.turn - 3 and \
            getattr(mon, 'you_hit', -9) >= game.turn - 3:
        low = max(low, .2)
    if low and mon.hp < mon.maxhp * low:
        game.msg(f'{mon.the()[0].upper() + mon.the()[1:]} has nothing left.', 'gold')
        game.kill(mon)
        return True
    return False


def last_stand(game):
    """Unbreakable Faith, Unbroken Line: once a day a killing blow leaves you on one life."""
    p = game.player
    from . import weapons as WP
    ok = has(game, 'unbreakable_faith') or (has(game, 'unbroken_line') and WP.has_shield(game))
    if not ok or getattr(p, 'faith_day', -1) == game.day:
        return False
    p.faith_day = game.day
    p.life = 1
    game.flash([(p.x, p.y)], (255, 240, 200), '+', .3)
    game.msg('A blow that should have killed you does not. You stand, on nothing but will.', 'gold')
    return True


def hurt(game, dmg, elem):
    """Deathly Calm takes some off a blow; Lightning Rod turns lightning to mana."""
    p = game.player
    if has(game, 'deathly_calm') and any(getattr(o, 'thrall', 0) and cheb(o.x, o.y, p.x, p.y) <= 1
                                         for o in game.map.mons):
        dmg *= .85
    if elem == 'lightning' and has(game, 'lightning_rod'):
        p.mana = min(game.stats()['max_mana'], p.mana + round(dmg / 2))
    return dmg


def no_stun(game):
    from . import weapons as WP
    return has(game, 'bulwark') and WP.has_shield(game)


def free_life(game):
    """Morrak's Favour: once a day, a spell's life is paid for you."""
    p = game.player
    if has(game, 'morraks_favour') and getattr(p, 'favour_day', -1) != game.day:
        p.favour_day = game.day
        game.msg('Morrak takes nothing this time. He is in a giving mood.', 'gold')
        return True
    return False


def tick(game):
    """Each turn: the imbue holds the mana back, the fire heals the Ash Walker, the glacier mends."""
    p = game.player
    if not mine(game):
        return
    from . import data as D
    s = None
    if has(game, 'ash_walker') and game.map.tile(p.x, p.y) == D.BURNING:
        game.heal(2)
    if has(game, 'living_glacier') and any(b[0] == 'def' and b[3] == 'Frost Armor' for b in p.buffs):
        s = s or game.stats()
        p.life = min(s['max_life'], p.life + 1)
    if has(game, 'heart_of_fire') and not game.hostile_visible():
        p.fire_free = True


def stamina_mult(game):
    p = game.player
    m = 1
    if has(game, 'fire_in_the_blood') and any('burn' in o.effects and cheb(o.x, o.y, p.x, p.y) <= 1
                                              for o in game.visible_hostiles()):
        m = 2
    if has(game, 'calm') and any(b[3] == 'Sanctuary' for b in p.buffs):
        m = 2
    if has(game, 'last_breath') and p.life < game.stats()['max_life'] / 4:
        m = 2
    return m


def stamina_plus(game):
    return total(game, 'stamina_plus')


def mana_held(game):
    return imbue(game) is not None


def heavy_ok(game):
    return has(game, 'heavy_training')


def walk_in_fire(game):
    return has(game, 'walk_in_fire')


def tame_bonus(game):
    return total(game, 'tame') / 100


# ------------------------------------------------------------------ your beast and your dead
def beast_stats(game, s):
    k = 1 + total(game, 'beast_hp') / 100
    s['max_hp'] = round(s['max_hp'] * k)
    d = 1 + total(game, 'beast_dmg') / 100
    if has(game, 'wildkin') and _green(game):
        d *= 1.2
    s['dmg'] = (max(1, round(s['dmg'][0] * d)), max(2, round(s['dmg'][1] * d)))


def beast_mult(game, mon):
    """Poacher: your beast too strikes the unaware twice as hard."""
    return 2 if has(game, 'poacher') and not mon.awake else 1


def beast_struck(game, mon, mc=None, dmg=0):
    """Your beast bit: One Spirit, Drag Down, the mark for Kill Together, and what the pair rules add."""
    mon.beast_hit = game.turn
    if mon.hp > 0 and mon in game.map.mons:
        if has(game, 'firetamer'):
            mon.effects['burn'] = [3, 2 + game.player.disc['fire'][0] // 10]
        if has(game, 'winterwolf'):
            mon.effects['slow'] = [3, 0]
        if has(game, 'thunderhide'):
            near = [o for o in game.visible_hostiles() if o is not mon and cheb(o.x, o.y, mon.x, mon.y) <= 2]
            if near:
                o = random.choice(near)
                game.fx('zap', cells=game.cells_between((mon.x, mon.y), (o.x, o.y)), col=SK.STORM)
                game.damage_mon(o, 3 + game.player.disc['storm'][0] // 8, col=SK.STORM, elem='lightning')
    if mc is not None and dmg and has(game, 'nightstalker'):
        from . import mercs as MC
        mc.hp = min(MC.stats(game, mc)['max_hp'], mc.hp + max(1, dmg // 4))
    if has(game, 'one_spirit'):
        SK.gain(game, 'beastcraft', 1)
    if has(game, 'drag_down') and random.random() < .2 and mon.hp > 0:
        mon.hold = max(mon.hold, 1)


def _green(game):
    from . import spellmap as SM
    return SM.nature_factor(game) > 1


def thrall_hit(game, mon):
    """Lich: the blows of your dead slow."""
    if has(game, 'lich') and mon.hp > 0:
        mon.effects['slow'] = [3, 0]


def rise(game, mon):
    """A fallen foe gets up again as your skeleton, if there is room where it fell."""
    from . import mercs as MC
    m = game.map
    if mon.is_npc or game.occupied(m, mon.x, mon.y):
        return
    sl = getattr(m, 'slain', [])
    if sl and tuple(sl[-1][1:3]) == (mon.x, mon.y):
        sl.pop()
    MC.thrall(game, 'skeleton', mon.x, mon.y, 20, 'Risen Skeleton')
    game.msg(f'{mon.name} gets up again, and it is yours.', 'good')


def _corpse_by(game, mon, line, r):
    """Pyre Lord and Galvanist: a corpse beside the foe your spell struck bursts into fire, or gets up."""
    from . import spellmap as SM
    from . import mercs as MC
    m = game.map
    c = next((c for c in SM.corpses(game) if cheb(c[1], c[2], mon.x, mon.y) <= 1), None)
    if not c:
        return
    m.slain.remove(c)
    if line == 'fire':
        game.fx('burst', x=c[1], y=c[2], r=1, col=SK.FIRE, signs='*∙')
        for o in [o for o in game.visible_hostiles() if cheb(o.x, o.y, c[1], c[2]) <= 1]:
            game.damage_mon(o, 6 + r // 5, col=SK.FIRE, elem='fire')
    elif not game.occupied(m, c[1], c[2]):
        MC.thrall(game, c[0], c[1], c[2], 6, 'Risen ' + game_name(c[0]), c[3] if len(c) > 3 else None)
        game.msg('The lightning jerks a corpse to its feet.', 'good')


def game_name(k):
    from . import data as D
    return D.MONSTERS[k]['name'] if k in D.MONSTERS else 'Dead'


def heal_party(game, n):
    from . import mercs as MC
    for mc in MC.party(game):
        mx = MC.stats(game, mc)['max_hp']
        if mc.hp < mx:
            mc.hp = min(mx, mc.hp + n)
            MC.refresh_body(game, mc)


def on_self_heal(game, sk, r):
    """Cleric: a small Ward with every healing; Stormsaint: a spark at the nearest foe."""
    p = game.player
    if has(game, 'cleric') and not any(b[0] == 'ward' for b in p.buffs):
        p.buffs.append(['ward', 4 + r // 8, 10, 'Ward'])
    if has(game, 'stormsaint'):
        t = game.nearest_target(6, True)
        if t:
            game.fx('zap', cells=game.cells_between((p.x, p.y), (t.x, t.y)), col=SK.STORM)
            game.damage_mon(t, 4 + r // 6, col=SK.STORM, elem='lightning')


def conducts(game, mon):
    """Darkstorm: a cursed foe passes the lightning on further."""
    return has(game, 'darkstorm') and any(c in mon.effects for c in CURSES)


def struck_by(game, mon):
    """A foe struck you: a Snowsaint's Ward slows it."""
    if has(game, 'snowsaint') and any(b[0] == 'ward' for b in game.player.buffs) and mon in game.map.mons:
        mon.effects['slow'] = [3, 0]


def dot(game, mon, k, v):
    """A foe's burn, bleed or poison ticks: a Hexblade drinks the burn of a cursed foe."""
    if k == 'burn' and v and has(game, 'hexblade') and any(c in mon.effects for c in CURSES):
        game.heal(max(1, v // 2))


def keeps(game, mon, k):
    """Rimehex: a curse does not wear off on a slowed foe, every other turn."""
    return k in CURSES and has(game, 'rimehex') and 'slow' in mon.effects and game.turn % 2 == 0


def thorns_on(game, o, tile):
    """Blightcaller and Poisoner: who stands in your brambles and roots catches the plague, or your poison."""
    if has(game, 'blightcaller'):
        o.effects.setdefault('plague', [6, 3])
    if has(game, 'poisoner'):
        o.effects['poison'] = [4, 3 + game.player.disc['cunning'][0] // 10]


def reaver(game, sk, dealt):
    if dealt > 0 and SK.pool(sk) == 'stamina' and has(game, 'reaver'):
        game.heal(max(1, round(dealt / 10)))


def poison_free(game):
    return has(game, 'immune')


def thrall_made(game, o):
    hp = 1 + total(game, 'thrall_hp') / 100
    dm = 1 + total(game, 'thrall_dmg') / 100
    if hp > 1 or dm > 1:
        o.hp = o.maxhp = round(o.maxhp * hp)
        o.dmg = (max(1, round(o.dmg[0] * dm)), max(1, round(o.dmg[1] * dm)))


def shape_keys_locked(game):
    """In the shape of a beast, keys 3 to 6 rest, unless you are Untamed."""
    from . import anim as AN
    return AN.shape_of(game.player) is not None and not has(game, 'untamed')


def tidy(game):
    """Points in a school that is not (or no longer) yours count for nothing; drop knots that no longer exist."""
    t = tree(game)
    for line in list(t):
        t[line] = {k: n for k, n in t[line].items() if k in KNOTS}


assert all(len(brs) == 3 and all(len(ks) == 6 for _n, _w, ks in brs) for brs in TREES.values())
assert all(k[6].count('{n}') <= 1 for _l, _b, _i, k in KNOTS.values())
