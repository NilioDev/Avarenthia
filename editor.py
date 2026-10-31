"""The Avarenthia Editor: draw the game's special rooms (see "The Avarenthia Editor" in docs/plan.md).

Run:  python editor.py   (or: python main.py --editor)
It comes with the test download only, never with the game for players."""
import sys

from avarenthia.editor.run import main

if __name__ == '__main__':
    sys.exit(main())
