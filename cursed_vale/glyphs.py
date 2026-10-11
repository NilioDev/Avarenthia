"""The characters in assets/glyphs_8x16.png, in tile order (16 per row)."""
EXTRA = '─│┌┐└┘┤├┬┴┼█▀▄▌▐░▒▓·…◄►▲▼×•♣♠■∩≈♦§⌂Ω☼♥↑↓→←√°±ⁿ═║π╬≡○¥▬☺'
CHARS = ''.join(chr(c) for c in range(32, 127)) + EXTRA
CHARMAP = [ord(c) for c in CHARS]
COLUMNS = 16
ROWS = (len(CHARS) + COLUMNS - 1) // COLUMNS
TILE_W, TILE_H = 8, 16
SHEET = 'glyphs_8x16.png'
