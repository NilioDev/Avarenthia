The drawn pieces of Avarenthia
==============================

Draw them in the Avarenthia Editor (python main.py --editor, or the editor in the test download), or by hand here.

Every *.des file here holds pieces, one after another. A piece is a small map of one room (a theme room, the
arrival room, the bottom room) that the dungeon makers set into a level. The game reads these files when it runs
from the source; a build carries them packed and sealed (tools/pack_pieces.py) and ignores a pack that was changed.

A piece
-------
    NAME:   shrine                      a name of its own, never used twice
    PART:   middle                      entrance, arrival, middle or bottom (default middle)
    KIND:   any                         the kinds of place it suits: any, or dungeon tags (crypt den mine deep ...);
                                        not:den keeps it out of one kind
    DEPTH:  3                           only from this level down (default 0)
    WEIGHT: 10                          how often it is picked against the others (default 10)
    SHAPE:  a nave with an apse         what it looks like, for whoever reads this file
    GATE:   door                        the way in: door, open, secret (a hidden door) or vault (locked; the key lies
                                        elsewhere on the level, with a guard)
    MOOD:   An old shrine. ...          the line in the messages the first time you step in (several: one is picked)
    SUBST:  1 = s:1 .:3                 each 1 on the map becomes a statue (weight 1) or floor (weight 3);
                                        none stands for nothing at all (rock)
    THING:  A = altar do:shrine         a telling thing: the tile it is, and what it does when you bump into it
                                        (or step on it, for a thing you can walk on)
    EVENT:  when=enter then=msg:"The bones stir." then=spawn:undead:4
    MAP
    ...the drawing...
    ENDMAP

Lines starting with ; are notes and are skipped.

The drawing
-----------
Draw only the inside of the room; the rock round it is the wall. The piece is turned and mirrored at random.
    (space) rock, outside the room          + the way in: exactly one, in a straight wall (two cells of floor
    .  floor                                  on each side of it, inside)
    #  rock inside the room (a pillar)      <  the stairs up (arrival pieces)   >  the stairs down or the boss
    ~  deep water      ,  shallow water     v  a chasm (a fall to the level below)   L  a river of fire
    s  statue    b  barrel    t  table    c  treasure chest    r  rubble    g  gravestone    m  mushrooms
    =  bridge    k  shelves of books    h  hearth    a  anvil    w  well    f  fountain    e  eggs
    j  iron bars    y  drying rack    o  bone wall    u  grasping roots    x  web    p  bed    n  a hidden door
    "  grass    i  ice    %  remains of a camp    _  altar    *  a heap of shiny things    q  cage
    A-Z  the piece's own telling things (THING lines), or marks for events
    0-9  substitutions (SUBST lines)

Things a THING line can name
----------------------------
altar statue shelves fountain anvil hearth well barrel chest mushrooms eggs rack cage rubble chasm grave secret,
vault door, plinth mirror gong lever dummy circle ward bier remains dice gears bars map web arch alchemy floor roots
water shallow fire table bones hallowed
and besides these, any tile of the game by its own name ("ivy on old stone", "Varnish wall"): it is that tile.

What a thing can do (do:...)
----------------------------
shrine library fountain forge cook alchemy fungus larder wishing training maptable wine choice armoury adventurer
circle statues bier nest gong cell mirror menagerie sanctuary arch gears dice herbs collapse plate echo
and the puzzle things' (puzzles.py; pieces/puzzles.des has an example room of each):
    pressure (a pressure plate)   block (a stone block, pushed)   lever   crystal (a red crystal switch)
    brazier (a cold fire bowl, or one that burns)   swivel (a mirror on a swivel)   shaft (a shaft of daylight)
    sundisc   bell   cracked (a cracked wall)   crumble (crumbling floor)   ice (slick ice)   spikes (spike holes)
    portal (two portal stones in a room)   idol (golden idol on a plinth)   keyhole (its key lies on the level)
    sluice (sluice gate)   riddle (riddle stone)   sarcophagus   offering (offering bowl)   scrying (scrying pool)
    book (chained book)   eyes (idol with gem eyes)   rope (rope down)   ladder (ladder up)
Things without a do: that the events work: red block, sunk red block, blue block, sunk blue block, arrow slit.

Events
------
    when=   enter (the room, the first time)   step (on a mark, at=)   bump (a mark, at=)   take (a find in the room)
            clear (the last foe in the room falls)   night (night falls while you are on the level)
    at=     the mark (a letter of the drawing) for step and bump
    if=     night, day, chance:50, has:<item key>; several with commas: all must hold
    then=   msg:"a line"   do:<what a thing can do>   spawn:<pack|undead|beasts|fire|vermin|monster key>:<how many>
            wake (every creature on the level)   open:<mark> (bars, rubble or a door there give way)
            shut:<mark> (bars drop there)   cavein:<mark> (rubble there)   flood:<mark> (water there)   reveal (the level)
    again=yes   the event can happen more than once (by default once)

Puzzle events
-------------
    when=   press / release (a pressure plate at=, under anything that stands on it)   lit (a brazier)
            sun (the sunbeam reaches a disc)   hit (a crystal)   break (a cracked wall)   solved (a riddle stone)
            unlock (a keyhole)   order:CAB (the bells marked C, A and B struck in that order)
    then=   arrows:<mark> (the slits there shoot along their line)   raise:red / raise:blue (that colour of blocks
            stands up, the other sinks)   water:down / water:up (the room's water)   become:<mark>:<tile name>
    A room with blocks needs a lever that sets it back: EVENT: when=bump at=R then=reset again=yes

Creatures, lists and more (the editor's Creatures layer)
--------------------------------------------------------
    CREATURE: skeleton at 4,2       this one, here, always (x and y count from 0, the top left of the MAP)
    CREATURE: ? at 6,3              one of the place, by its kind and level
    CREATURE: list:war band at 5,5  one from a list; a kind that may not live in the place becomes one of the place
    LIST:     war band = orc:6 orc_shaman:1 ogre:1     a list of the piece (before the first NAME: for every piece)
    MORE:     list:war band 0-2     0 to 2 more where there is room (also "? 1-3" or a creature key)

Switches, counters and timers (the editor's Events layer)
---------------------------------------------------------
    SWITCH:   gate = shut open      a switch and its states; the first is how it starts (on its own: off on)
    COUNTER:  plates 0              a counter and where it starts
    when=     switch:gate:open (the switch comes to that state)   count:plates:3 (the counter comes to 3)
    if=       switch:gate:open      count:plates:3 (at least 3)
    then=     set:gate:open   flip:gate (to its next state)   add:plates   sub:plates:2
              after:10:shut:Q (in ten turns, the rest is one more then)   reset (the room back as drawn)
    A wire in the editor is one of these events: when you bump A, flip the gate.

Dressing (Ctrl+D in the editor)
-------------------------------
    DRESS:    hall 3                dressed anew in every world from a set, how full 1 to 5 (dressing.py has the
                                    sets: war camp hall ruin library crypt cave storeroom forge temple barracks den)
