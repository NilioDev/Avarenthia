The drawn pieces of Avarenthia
==============================

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

What a thing can do (do:...)
----------------------------
shrine library fountain forge cook alchemy fungus larder wishing training maptable wine choice armoury adventurer
circle statues bier nest gong cell mirror menagerie sanctuary arch gears dice herbs collapse plate echo

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
