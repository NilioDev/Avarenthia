# Cursed Vale

Een ASCII open-world RPG in Python met [python-tcod](https://python-tcod.readthedocs.io/) (libtcod).
Je wordt wakker zonder geheugen en bent niemand. Een willekeurige open wereld met snelle gevechten, handel tussen
dorpen en steden, facties in oorlog, banen op de prikborden, karavanen, patrouilles, bandieten en reizigers die
zichtbaar over de kaart trekken, en een wereld die op de achtergrond verandert.

## Je held

Je wordt wakker in de tempel van Thornfield, zonder geheugen en zonder wapens: goblins hebben je zwaard en schild
meegenomen naar de Hollow Den. Tot je die terughaalt vecht je met je vuisten (de discipline Unarmed groeit daarmee),
en bij hun aanvoerder Snagtooth ligt ook je eerste spreukenboek. Je bent niemand; wat je wordt, bepaal je zelf.

**Honger.** Je verbruikt voedsel; eet brood, rantsoenen, vis of vlees (`Shift+E`, of vanuit je tas) of neem een warme
maaltijd en een bed in een herberg (`M` bij de herbergier). Met honger word je zwakker en uiteindelijk verhonger je.

**Dwergenrijken.** In de bergen liggen ondergrondse dwergensteden (`▼` op de kaart) met hallen, smidsen, een troonzaal
en een trap naar de Deep Roads, de oude dwergentunnels die nu vol goblins en erger zitten.

**Inspecteren.** Met `O` of `;` beweeg je een cursor over de kaart en lees je wat er is: monsters, mensen, voorwerpen,
terrein en plaatsen. Tab springt naar het volgende.

Bij een nieuw spel kies je je volk (mens, elf, dwerg, halfling, gnoom, half-ork of goblin), je geslacht (man, vrouw of
ongedefinieerd) en je voor- en achternaam; met Tab krijg je een willekeurige naam die bij je volk past. Elk volk heeft eigen attributen, voordelen en
nadelen, en andere volkeren en facties reageren anders op je: andere prijzen en een andere beginreputatie.

De facties zijn in elke wereld anders: een rijk, kooplieden, woudvolk, vogelvrijen en een sekte, vaak aangevuld met
dwergenclans en orkenstammen, elk met een eigen volk, naam, kleur en vijanden.

Je kent aan het begin alleen de omgeving van Thornfield. Lees de **wegwijzer** (`┬`) in elk dorp om te weten waar de wegen
heen gaan, en praat met mensen: zij vertellen over andere plaatsen. De wereldkaart (`M`) kun je met de pijltjes scrollen;
`Z` wisselt tussen close-up en het hele rijk.

**Geld** is schaars: 100 koper is 1 zilver, 100 zilver is 1 goud. Beesten dragen geen geld, mensen een beetje,
handelaren veel. Munten vind je vooral in schatkisten (`■`) in kerkers en ruïnes.

**Misdaad.** Je kunt reizigers en karavanen beroven (loop ertegenaan). Elk dorp onthoudt wat er in de buurt gebeurt:
zakt je aanzien daar te ver, dan ben je er gezocht, in vijf niveaus (`*` in het paneel): eerst de dorpswacht, dan
de sheriff met zijn hulpsheriffs, dan de soldaten van de heer, dan ridders en ten slotte een heel leger. Er hangen
opsporingsberichten aan de prikborden en houden de wachters je aan bij de poort: boete betalen, drie dagen in de
schandpaal, of vluchten. Mensen vergeten langzaam.

**Life skills** groeien door ze te doen, zoals in Project Gorgon. De eerste is **vissen**: koop een hengel bij een outfitter
en druk `A` naast water (rivier, meer, zee of een poel in een grot). Hoe beter je wordt, hoe meer soorten vis toehappen.

## Geen klassen

Je kiest geen klasse. Je wordt wat je doet: tien disciplines (zwaard, bijl en knots, dolk, boog, vuur, ijs, storm,
genezing, schaduw, strijdkunst) stijgen door ze te gebruiken. Je begint met alleen een kort zwaard en een boog, zonder skills.
Skills (50 in totaal) leer je uit **boeken** (`≡`): van monsters, diep in ruïnes, bij staande stenen, van marskramers
en soms bij een outfitter in een stad. Moeilijkere boeken vragen een hogere discipline. Je neemt zes skills tegelijk mee
en wisselt ze alleen in een stad of burcht (`Z`). Wapenskills werken alleen met het bijpassende wapen in je handen.

Magische items zijn zeldzaam en **ongeïdentificeerd** als je ze vindt; hun krachten werken pas na identificatie bij een
outfitter of priester. Sommige zijn **vervloekt**: eenmaal aangetrokken krijg je ze niet meer af tot een priester de vloek opheft.

**Op de achtergrond** gebeurt meer dan je denkt. De wereld verandert langzaam, ook als jij ergens anders mee bezig
bent. Let op het nieuws en op wat mensen vertellen; pas na lang spelen wordt duidelijk wat er speelt, en wat je
ermee doet (of niet) is aan jou.

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
| `A` | vissen (naast water, met een hengel) |
| `Shift+E` | eten |
| `O` of `;` | inspecteren |
| `Z` | skills kiezen (in een stad of burcht) |
| `Q` / `W` | health- of manadrankje |
| `P` | Town Portal |
| `X` | automatisch verkennen (stap voor stap te zien, elke toets stopt) |
| `T` | reizen naar een bekende plaats of kerker |
| `M` | kaart van het rijk (pijltjes scrollen, `Z` heel rijk, `F` facties) |
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
cursed_vale/evils.py     wat er op de achtergrond gebeurt (spoilers!)
cursed_vale/crime.py     misdaad, aanzien per dorp, premiejagers
cursed_vale/money.py     koper, zilver en goud
cursed_vale/factions.py  facties, per wereld opnieuw gemaakt
cursed_vale/races.py     volkeren, hun verhoudingen en namen
cursed_vale/lifeskills.py life skills (vissen)
cursed_vale/look.py      hoe het land eruitziet (hoogte, vocht, klimaat)
cursed_vale/dress.py     aankleding en licht in kerkers
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
