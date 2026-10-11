"""The characters in assets/glyphs.png, in tile order (16 per row).

The font is the IBM CGA 8x8 font (Px437 IBM CGA): square 8x8 cells.
All characters of the font are in the sheet, so any of them can be used in the game."""
# ASCII, then the characters the game already uses, then everything else the font has
EXTRA = '─│┌┐└┘┤├┬┴┼█▀▄▌▐░▒▓·…◄►▲▼×•♣♠■∩≈♦§⌂Ω☼♥↑↓→←√°±ⁿ═║π╬≡○¥▬☺Π†∆Ψ¤╔╗╚╝╠╣╦╩ß□Θ¡'
MORE = '\xa0¢£ª«¬²µ¶º»¼½¿ÄÅÆÇÉÑÖÜàáâäåæçèéêëìíîïñòóôö÷ùúûüÿƒΓΣΦαδεστφ‼₧↔↕↨∙∞∟≤≥⌐⌠⌡╒╓╕╖╘╙╛╜╞╟╡╢╤╥╧╨╪╫◘◙☻♀♂♪♫'
CHARS = ''.join(chr(c) for c in range(32, 127)) + EXTRA + MORE
CHARMAP = [ord(c) for c in CHARS]
COLUMNS = 16
ROWS = (len(CHARS) + COLUMNS - 1) // COLUMNS
TILE_W, TILE_H = 8, 8
SHEET = 'glyphs.png'
