# Cursed Vale

Een ASCII action-roguelike in Python met [python-tcod](https://python-tcod.readthedocs.io/) (libtcod).
Een ADOM-achtige wereld met Diablo-invloeden: klassen met skills, elite monsters en loot in vier zeldzaamheden.

## Installeren en starten

Je hebt Python 3.10 of nieuwer nodig.

```bash
cd cursed_vale
python -m venv .venv
# Windows:      .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Het spel opent een gemaximaliseerd venster van 110 bij 30 tekens in het 8×16-pixelfont Classic Console Neue,
op de grootste scherpe vergroting die op je scherm past (2× op een 1080p-scherm). F11 of Alt+Enter schakelt naar volledig scherm.
Je held wordt bewaard in `savegame.dat` naast `main.py`. Als je sterft, wordt die verwijderd.

## Eén los bestand maken (zonder Python te hoeven draaien)

Een uitvoerbaar bestand moet je bouwen op het besturingssysteem waarop het moet draaien.

**Windows:** dubbelklik op `build_windows.bat`. Na een paar minuten staat `dist\CursedVale.exe` klaar.
Dat bestand kun je overal neerzetten en starten. Je savegame komt ernaast te staan.

**macOS / Linux:** `bash build.sh`, daarna staat `dist/CursedVale` klaar.

**Via GitHub, zonder zelf iets te installeren:** zet deze map in een GitHub-repository.
De workflow in `.github/workflows/build.yml` bouwt bij elke push automatisch een versie voor
Windows, macOS en Linux. Je downloadt ze onder het tabblad *Actions*, bij de laatste run, onder *Artifacts*.

Windows SmartScreen kan waarschuwen omdat het bestand niet digitaal ondertekend is.
Kies dan *Meer info* en *Toch uitvoeren*.

## Besturing

| Toets | Actie |
|---|---|
| pijltjes, numpad, `hjklyubn` | lopen, tegen een monster aanlopen is aanvallen |
| Shift + richting | rennen |
| `1` `2` `3` | skills, richten automatisch op de dichtstbijzijnde vijand |
| `Q` / `W` | health- of manadrankje |
| `P` | Town Portal |
| `X` | automatisch verkennen |
| `T` | reizen door de vallei |
| `>` `<` of Enter | trap nemen, dorp of kerker in |
| `G` | oppakken |
| `I` / `D` / `C` | tas, iets laten vallen, karakterscherm |
| `R`, `5`, `.` | rusten, een beurt wachten |
| `?` of F1 | hulp |
| Esc | opslaan en afsluiten |
| muis | eroverheen bewegen om te bekijken, klikken om een stap te zetten |

`>` en `<` gaan uit van een Amerikaanse toetsenbordindeling (Shift + punt/komma). Enter werkt altijd.

## Projectstructuur

```
main.py                  venster, tileset, toetsenbord en muis (alles wat tcod-specifiek is)
cursed_vale/data.py      tegels, klassen, skills, items, affixen, monsters, kerkers
cursed_vale/entities.py  Item, Monster, Player, GameMap en het maken van loot en monsters
cursed_vale/worldgen.py  vallei, dorp, kerkers (kamers en grotten), wildernis, winkel
cursed_vale/engine.py    spelregels: beweging, gevechten, monster-AI, skills, verkennen, opslaan
cursed_vale/fov.py       zichtveld via libtcod (symmetric shadowcasting)
cursed_vale/ui.py        alle schermen en het tekenen, los van tcod
cursed_vale/canvas.py    dunne laag over de tcod-console
assets/glyphs_8x16.png   tekenset, gemaakt uit Classic Console Neue
assets/fonts/            het font zelf en zijn licentie
tools/make_tileset.py    maakt de tekenset opnieuw (Pillow nodig)
tests/                   headless test en een bot die het spel uitspeelt
```

## Tests

```bash
python tests/test_headless.py   # speelt met willekeurige toetsen en tekent alle schermen
python tests/bot.py 4           # een bot speelt 4 keer per klasse alle kerkers uit
```

De tests draaien zonder venster en zonder tcod.

De tekenset opnieuw maken, of met een ander 8×16-pixelfont:

```bash
pip install pillow
python tools/make_tileset.py pad/naar/lettertype.ttf
```

Het font is Classic Console Neue van DeeJayy (https://webdraft.hu/fonts/classic-console/), MIT-licentie,
zie `assets/fonts/LICENSE-ClassicConsoleNeue.txt`.
