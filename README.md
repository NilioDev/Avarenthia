# Cursed Vale

Een ASCII open-world RPG in Python met [python-tcod](https://python-tcod.readthedocs.io/) (libtcod).
Een ADOM-achtige wereld met Diablo-gevechten en Privateer-achtige handel: klassen met skills, elite monsters,
loot in vier zeldzaamheden, zo'n 27 dorpen en steden met een levende economie, kastelen en forten van vijf facties, banen op de prikborden van de herbergen,
en karavanen, patrouilles en bandieten die zichtbaar over de kaart trekken.

## Geen klassen

Je kiest geen klasse. Je wordt wat je doet: tien disciplines (zwaard, bijl en knots, dolk, boog, vuur, ijs, storm,
genezing, schaduw, strijdkunst) stijgen door ze te gebruiken. Hogere rangen ontgrendelen nieuwe skills uit die
discipline, 50 in totaal. Je neemt er zes tegelijk mee en wisselt ze alleen in een stad of burcht (`Z`).
Wapenskills werken alleen met het bijpassende wapen in je handen. Levelen gaat langzaam en geeft attribuutpunten.

Bij een nieuw spel kies je **hardcore** (dood is definitief) of **softcore**: je ontwaakt in de dichtstbijzijnde tempel,
maar je rugzak, vracht en goud liggen bij je lijk, dat je terug moet halen. Je kunt ook een **seed** invoeren om
dezelfde wereld nog eens te spelen; zonder seed is elke wereld anders.

## Facties en oorlog

Vijf facties bezitten de regio's: de Kroon van Aldmark, de Handelsliga, de Kring van Doornen, de Zwarte Hand en de
Cultus van de Ondoden. Ze hebben kastelen (`Ω`) en forten (`╬`). Legertjes trekken zichtbaar over de kaart naar vijandige
burchten; een geslaagd beleg verovert de burcht en de regio, met de dorpen erin. Vijandige burchten kun je zelf
bestormen: dood de bevelhebber en geef de burcht aan een bondgenoot. Castellanen geven oorlogsbanen.
Je reputatie per factie bepaalt prijzen, welke poorten opengaan en wie je aanvalt. `M` en dan `F` toont de gebieden.

## Handel en banen

- Elke plaats maakt bepaalde goederen (`+`, goedkoop) en wil andere hebben (`!`, duur). Koop bij de handelaar en verkoop elders.
  Prijzen reageren op wat jij en de karavanen kopen en verkopen, en herstellen langzaam.
- Nieuws (hongersnood, feest, mijnramp, brand, oorlog, ziekte) verschuift prijzen een paar dagen.
- Je draagt 30 eenheden vracht. Een muilezel (+60) en een kar (+160) koop je bij de stalmeester.
- Op het prikbord van de herberg vind je koeriersklussen, vrachtritten, premiejachten, escortes en kerkertochten.
  Reputatie in een plaats geeft een bonus op beloningen en betere prijzen.
- Bandieten overvallen karavanen; patrouilles uit de steden jagen bandieten weg.

## De wildernis

- Op de wegen ben je redelijk veilig. Hoe verder je van de weg afdwaalt, hoe gevaarlijker het wordt: grotere roedels,
  sterkere monsters, meer champions. 's Nachts komen de doden tevoorschijn. Beweeg de muis over het land om het gevaar te zien.
- Verborgen plekken om te ontdekken: ruïnes (`Π`, kleine kerkers), heiligdommen (`†`, zegeningen), bandietenkampen (`∆`),
  staande stenen (`Ψ`) en verlaten wagens (`¤`).
- Onderweg gebeurt van alles: gewonde reizigers, marskramers, tolwegen van de Zwarte Hand, stormen, dwaallichtjes.
- Reizigers (`@` op de weg) kun je aanspreken door ertegenaan te lopen. Sommigen hebben een klus voor je
  (brief bezorgen, goederen halen, een beest doden, iets terughalen uit een ruïne). Daarna wachten ze op je in de herberg
  van de plaats waar ze heen liepen; dat staat in je dagboek en op de kaart.
- Het bestiarium (`V`) houdt bij welke monsters je hebt gezien. Elke kill leert je meer: hogere kennis geeft meer schade
  tegen dat soort monster en ze raken je minder vaak.

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

Het spel opent een gewoon venster van 110 bij 30 tekens in het 8×16-pixelfont Classic Console Neue,
op de grootste scherpe vergroting die op je scherm past (2× op een 1080p-scherm). F11 of Alt+Enter schakelt naar volledig scherm.
Je held wordt bewaard in `savegame.dat` naast `main.py`. Als je sterft, wordt die verwijderd.

## Starten op Windows met Smart App Control

Smart App Control blokkeert het `.exe`-bestand, omdat het niet digitaal ondertekend is. Speel het spel dan via Python:

1. Installeer Python 3.10 of nieuwer van [python.org](https://www.python.org/downloads/) en vink "Add python.exe to PATH" aan.
2. Download de broncode (op GitHub: *Code → Download ZIP*) en pak die uit.
3. Dubbelklik op `start_windows.bat`. De eerste keer installeert het de benodigdheden (ongeveer een minuut), daarna start het spel direct.

Blokkeert Windows ook het `.bat`-bestand, open dan een terminal in de map en typ:

```
py -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python main.py
```

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
| `1` - `6` | skills, richten automatisch op de dichtstbijzijnde vijand |
| `F` | schieten met een boog |
| `Z` | skills kiezen (in een stad of burcht) |
| `Q` / `W` | health- of manadrankje |
| `P` | Town Portal |
| `X` | automatisch verkennen |
| `T` | reizen naar een bekende plaats of kerker |
| `M` | kaart van het rijk |
| `E` of Tab | dagboek: banen, vracht en nieuws |
| `>` `<` of Enter | trap nemen, dorp of kerker in |
| `G` | oppakken |
| `I` / `D` / `C` | tas, iets laten vallen, karakterscherm |
| `R`, `5`, `.` | rusten, een beurt wachten |
| `V` of F2 | bestiarium |
| `?` of F1 | hulp (twee pagina's: toetsen en de wereld) |
| Esc | opslaan en afsluiten |
| muis | eroverheen bewegen om te bekijken, klikken om een stap te zetten |

`>` en `<` gaan uit van een Amerikaanse toetsenbordindeling (Shift + punt/komma). Enter werkt altijd.

## Projectstructuur

```
main.py                  venster, tileset, toetsenbord en muis (alles wat tcod-specifiek is)
cursed_vale/data.py      tegels, klassen, skills, items, affixen, monsters, kerkers
cursed_vale/entities.py  Item, Monster, Player, GameMap en het maken van loot en monsters
cursed_vale/worldgen.py  vallei, dorp, kerkers (kamers en grotten), wildernis, winkel
cursed_vale/events.py    ruïnes en andere plekken, gebeurtenissen onderweg, reizigers
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
