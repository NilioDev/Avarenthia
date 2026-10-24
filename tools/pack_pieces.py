"""Pack the drawn pieces (pieces/*.des) into assets/pieces.pack, and seal it: the seal (a checksum) goes into the code,
avarenthia/pieces_seal.py, so a build ignores a pack that was changed afterwards. CI runs this before it builds.

    python tools/pack_pieces.py"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from avarenthia import pieces as PC  # noqa: E402


def main():
    texts = PC._source_texts()
    for f, t in texts.items():
        PC.parse(t, f)                          # a broken piece stops the build here, with its line
    raw, seal = PC.pack(texts)
    with open(os.path.join(ROOT, 'assets', 'pieces.pack'), 'wb') as fh:
        fh.write(raw)
    with open(os.path.join(ROOT, 'avarenthia', 'pieces_seal.py'), 'w', encoding='utf-8') as fh:
        fh.write('"""Written by tools/pack_pieces.py: the checksum of assets/pieces.pack."""\n')
        fh.write(f'SEAL = {seal!r}\n')
    n = sum(len(PC.parse(t, f)) for f, t in texts.items())
    print(f'packed {n} pieces from {len(texts)} files, seal {seal[:12]}')


if __name__ == '__main__':
    main()
