# Review: Excel Fertigungsliste (SQL, CRPlus)

Stand: 01.07.2026 · Basis: E-Mail-Thread „WG: Excel Fertigungsliste" (13.05.–21.05.2026, Mathias Jansen / Connedata)

## Versionshistorie im Thread

| Version | Datum | Änderung |
|---|---|---|
| V1 | 13.05. 15:36 | Erste Fassung mit Beistell-Spalten (Beistell-Pos, Beistell-Menge, Beistell-LS, Tat. Beistellung) |
| V2 | 18.05. 11:26 | „Heften am" matcht zusätzlich `%Schweißen%`; neue Spalten „Versandbereit am" (Datum) + `adt_nversandbereit` (Menge) |
| V3 | 21.05. 09:46 | `READ UNCOMMITTED` + `WITH (NOLOCK)` überall, wegen blockierter Prozesse |

## Befund 1 (kritisch): V3 basiert auf V1, nicht auf V2 — Fixes vom 18.05. fehlen

Die zuletzt gelieferte Version (21.05., die vermutlich produktiv läuft) enthält die
Änderungen vom 18.05. **nicht** mehr:

1. **„Heften am"** filtert wieder nur `arb_ckbez LIKE '%Heften%'`.
   Der Fix `OR arb_ckbez LIKE '%Schweißen%'` fehlt → Artikel, die nur einen
   Schweiß-Arbeitsschritt haben (Laser-/Kantteile, „Schweißen, Putzen" etc.),
   zeigen wieder kein Datum. Genau das war die Reklamation von Patrick am 18.05.
2. **Versandbereit-Menge** (`prodAdt.adt_nversandbereit`) fehlt wieder; es gibt
   nur noch das Datum `adt_dversandbereit`.

→ Korrigierte Fassung: [`fertigungsliste_korrigiert.sql`](fertigungsliste_korrigiert.sql)
(V3 mit NOLOCK **plus** den beiden V2-Fixes wieder eingebaut).

## Befund 2 (wahrscheinlich Ursache fehlender Zeilen): `ADZ_LRESTBESTAND = 0` hebelt den LEFT JOIN aus

```sql
LEFT JOIN adtzusatz ON ADZ_NADTID = verAdt.ADT_NID
...
WHERE ... AND ADZ_LRESTBESTAND = 0
```

Die Bedingung steht im `WHERE`, nicht im `JOIN`. Positionen **ohne**
`adtzusatz`-Datensatz (`ADZ_LRESTBESTAND` ist dann `NULL`) fallen dadurch komplett
aus der Liste. Für `prodAuf`/`prodAdt` wurde das korrekt mit `COALESCE(..., 0) = 0`
gelöst — hier fehlt es. Das ist ein plausibler Kandidat für Alex' Meldung vom
13.05. (Artikel 902153: nur 2 von 6 Lieferterminen sichtbar, obwohl CRPlus korrekt war).

Fix (in der korrigierten Fassung enthalten):

```sql
AND COALESCE(ADZ_LRESTBESTAND, 0) = 0
```

## Befund 3 (offen): Tatsächlich beigestellte Menge

Alex' Punkt vom 13.05. 13:47 ist fachlich noch nicht sauber gelöst:
`bdt_nmenge` (Beistell-Menge) ist die Menge laut Beistell-Lieferschein-**Position**.
Ob das die tatsächlich abgegebene Menge ist („Ich kann nicht davon ausgehen, dass
immer alles zu 100 % beigestellt worden ist"), hängt davon ab, ob im System beim
Beistell-LS die Ist-Menge gepflegt wird. Falls `bestelldetails` ein Feld für die
gelieferte Ist-Menge hat (analog `ADT_NGELIEFERT`, z. B. `BDT_NGELIEFERT`), sollte
das zusätzlich ausgegeben werden. → Bei Connedata nachfragen, das Schema ist von
außen nicht einsehbar.

## Befund 4 (Hinweis): NOLOCK = Dirty Reads

`READ UNCOMMITTED`/`NOLOCK` löst die Blockierungen, hat aber Nebenwirkungen:
Die Liste kann kurzzeitig **falsche Mengen, doppelte oder fehlende Zeilen** zeigen
(nicht committete Transaktionen, Page-Splits). Für eine Versand-Arbeitsliste, nach
der real ausgeliefert wird, ist das riskant — im Zweifel gegen CRPlus prüfen.
Sauberere Alternative, die ebenfalls nicht blockiert, aber konsistent liest:

```sql
-- statt READ UNCOMMITTED / NOLOCK (setzt READ_COMMITTED_SNAPSHOT bzw.
-- ALLOW_SNAPSHOT_ISOLATION auf der DB voraus – mit Connedata klären):
SET TRANSACTION ISOLATION LEVEL SNAPSHOT;
```

Außerdem: `SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED` und zusätzlich
`WITH (NOLOCK)` an jeder Tabelle ist doppelt — eines von beidem reicht.

## Befund 5 (Hinweis): Zeilenvervielfachung

Pro Produktionsposition wird je Beistell-Lieferschein **und** je Lohnschein
(`fertauftrag`) eine Zeile erzeugt. Hat eine Position mehrere Beistell-LS **und**
mehrere Lohnscheine, entsteht ein Kreuzprodukt (z. B. 2 × 2 = 4 Zeilen mit
identischen Mengen). Beim Summieren in Excel ist Vorsicht geboten; die
Mengenspalten wiederholen sich je Zeile.

## Kleinere Punkte

- Spaltenname-Tippfehler in V2: `[Verstandbereit]` → in der korrigierten Fassung
  `[Versandbereit Menge]`.
- „Beschichten am" (`TOP 1 … ORDER BY sol_dfert ASC`): Platzhalterdaten
  (01.01.1900 = noch nicht fertig) sortieren vor echten Daten, d. h. solange der
  erste Beschichtungsschritt offen ist, bleibt die Spalte leer, auch wenn ein
  späterer Schritt schon ein Datum hat. Vermutlich gewollt („erster Schritt zählt"),
  sollte aber bewusst so abgenommen sein.
- „Heften am" nutzt dagegen `MIN(...)`, das NULL/1900 ignoriert und das früheste
  **fertige** Datum zeigt — die beiden Spalten verhalten sich also unterschiedlich.
- Aktualisierungsintervall der Excel-Abfrage laut Connedata auf **mindestens
  10 Minuten** stellen (Vorgabe vom 21.05.).

## Empfehlung

1. Korrigierte Fassung (`fertigungsliste_korrigiert.sql`) an Connedata geben bzw.
   einspielen — sie enthält V3 + die verlorenen V2-Fixes + den `COALESCE`-Fix.
2. Artikel 902153 nach dem Einspielen erneut gegen CRPlus prüfen (Befund 2).
3. Frage nach der Ist-Beistellmenge (Befund 3) an Connedata stellen.
4. Refresh-Intervall in der Excel-Datenverbindung kontrollieren (≥ 10 min).
