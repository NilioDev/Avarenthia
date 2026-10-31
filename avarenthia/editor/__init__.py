"""The Avarenthia Editor (approved 31 October 2026; see "The Avarenthia Editor" in docs/plan.md): Nilio's own program
for drawing the game's special rooms. It reads and writes the pieces format (pieces/README.txt, pieces.py).

    model.py   a piece as the editor holds it: the drawing, its marks, its lines; undo
    files.py   reading and writing .des files (only the block of the piece you edit changes)
    tools.py   draw, line, rectangle, fill, select, copy and paste
    screen.py  the screen: palette, drawing, the piece, layers, the check (pure: drawn on any canvas)
    run.py     the window: tcod, the mouse, zoom

It is a tool, not part of the game: only in the test download and from the source with --editor; not in the
handbook."""
