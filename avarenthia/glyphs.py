"""The characters in assets/glyphs.png, in tile order (16 per row).

The font is the IBM CGA 8x8 font (Px437 IBM CGA): square 8x8 cells. WIDE holds the rest of the signs of the same
font's larger cut, PxPlus IBM CGA (31 October 2026, for the editor's palette): letters of many alphabets and more
symbols, drawn by the same hand. They come after the others, so no tile's sign moves.
All characters are in the sheet, so any of them can be used in the game."""
# ASCII, then the characters the game already uses, then everything else the font has
EXTRA = '─│┌┐└┘┤├┬┴┼█▀▄▌▐░▒▓·…◄►▲▼×•♣♠■∩≈♦§⌂Ω☼♥↑↓→←√°±ⁿ═║π╬≡○¥▬☺Π†∆Ψ¤╔╗╚╝╠╣╦╩ß□Θ¡'
MORE = '\xa0¢£ª«¬²µ¶º»¼½¿ÄÅÆÇÉÑÖÜàáâäåæçèéêëìíîïñòóôö÷ùúûüÿƒΓΣΦαδεστφ‼₧↔↕↨∙∞∟≤≥⌐⌠⌡╒╓╕╖╘╙╛╜╞╟╡╢╤╥╧╨╪╫◘◙☻♀♂♪♫'
QUAD = '▖▗▘▝▙▛▜▟▚▞'       # quarter blocks, drawn by hand (tools/make_tileset.py): round globes
WIDE = '¦¨©®¯³´¸¹¾ÀÁÂÃÈÊËÌÍÎÏÐÒÓÔÕØÙÚÛÝÞãðõøýþĀāĂăĄąĆćĈĉĊċČčĎďĐđĒēĔĕĖėĘęĚěĜĝĞğĠġĢģĤĥĦħĨĩĪīĬĭĮįİıĲĳĴĵĶķĸĹĺĻļĽľĿŀŁłŃńŅņŇňŉŊŋŌōŎŏŐőŒœŔŕŖŗŘřŚśŜŝŞşŠšŢţŤťŦŧŨũŪūŬŭŮůŰűŲųŴŵŶŷŸŹźŻżŽžſơƷǺǻǼǽǾǿȘșȚțɑɸˆˇˉ˘˙˚˛˜˝;΄΅Ά·ΈΉΊΌΎΏΐΑΒΔΕΖΗΙΚΛΜΝΞΟΡΤΥΧΪΫάέήίΰβγζηθικλμνξορςυχψωϊϋόύώϐϴЀЁЂЃЄЅІЇЈЉЊЋЌЍЎЏАБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдежзийклмнопрстуфхцчшщъыьэюяѐёђѓєѕіїјљњћќѝўџҐґ־אבגדהוזחטיךכלםמןנסעףפץצקרשתװױײ׳״ᴛᴦᴨẀẁẂẃẄẅẟỲỳ‐‒–—―‗‘’‚‛“”„‟‡‧‰′″‵‹›‾‿⁀⁄⁔⁴⁵⁶⁷⁸⁹⁺⁻₁₂₃₄₅₆₇₈₉₊₋₣₤₪€℅ℓ№™Ω℮⅐⅑⅓⅔⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞∂∅∈∏∑−∕∫≠⊙⌀▁▪▫◊●◦✓ﬁﬂ'
CHARS = ''.join(chr(c) for c in range(32, 127)) + EXTRA + MORE + QUAD + WIDE
CHARMAP = [ord(c) for c in CHARS]
COLUMNS = 16
ROWS = (len(CHARS) + COLUMNS - 1) // COLUMNS
TILE_W, TILE_H = 8, 8
SHEET = 'glyphs.png'
