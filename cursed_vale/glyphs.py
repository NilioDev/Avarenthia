"""The characters in assets/glyphs_12x24.png, in tile order (16 per row)."""
EXTRA = '─│┌┐└┘┤├┬┴┼█▀▄▌▐░▒▓·…◄►×•'
CHARS = ''.join(chr(c) for c in range(32, 127)) + EXTRA
CHARMAP = [ord(c) for c in CHARS]
COLUMNS = 16
ROWS = (len(CHARS) + COLUMNS - 1) // COLUMNS
TILE_W, TILE_H = 12, 24
