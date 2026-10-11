# SPEC: Interaktive Buchungsmaske (PoC)

---

## 1. Kontext & Ziel

Proof-of-concept für eine interaktive, generische Geld-Buchungsmaske im Kontext einer Bank. Es sollen Basisfunktionen (Buchung zwischen Konten, Suche von Belegen,...) erkennbar sein und Felder interaktiv sein. 

Zielgruppe: Softwarearchitekten und Business Analysten einer Bank. Erst-Präsentation als Dikussionsgrundlage in einem Meeting

---

## 2. Kernfunktionen

- [ ] Nutzer gibt eine Belegnummer/Vorgangsnummer ein, falls vorhanden
- [ ] Nutzer gibt Start- und Ziel-Konto, Betrag und Wertstellungsdatum ein
- [ ] Nutzer bucht ggfs. weitere Schritte und/oder gibt zur Kontrolle frei

### Beleg 
- Ein Beleg besteht aus einer oder mehreren Buchungen mit derselben "Belegnummer". 
- Die erste Buchung eines Belegs erzeugt automatisch eine neue eindeutige Belegnummer. 

### Regel: Erste Buchung 
- Die erste Buchung eines Belegs besitzt keinen fachlichen Zusammenhang zu einem bestehenden Beleg. 
- Beispiel: 
| Start | Ziel | Betrag | 
|--------|------|--------| 
| X | A | 100 | 
Dadurch erhält Konto A innerhalb dieses Belegs ein verfügbares Guthaben von 100.


### Regel: Folgebuchungen 
- Jede weitere Buchung verwendet dieselbe Belegnummer. 
- Eine Buchung ist nur erlaubt, wenn das Startkonto innerhalb dieses Belegs mindestens den zu buchenden Betrag als verfügbares Guthaben besitzt. 
- Nach einer erfolgreichen Buchung: 
- - das verfügbare Guthaben des Startkontos wird um den Betrag reduziert 
- - das verfügbare Guthaben des Zielkontos wird um den Betrag erhöht 

### Beispiel: Erste Buchung
| Start | Ziel | Betrag | 
|--------|------|--------| |
 X | A | 100 | 
Verfügbare Guthaben: - A = 100 

---

Buchung:
| Start | Ziel | Betrag |
|--------|------|--------|
| A | B | 40 |

Verfügbare Guthaben:
- A = 60
- B = 40

---

Buchung:
| Start | Ziel | Betrag |
|--------|------|--------|
| A | C | 30 |

Verfügbare Guthaben:
- A = 30
- B = 40
- C = 30

---

Erlaubt:
| Start | Ziel | Betrag |
|--------|------|--------|
| B | D | 40 |

Danach:
- A = 30
- B = 0
- C = 30
- D = 40

---

Nicht erlaubt:
| Start | Ziel | Betrag |
|--------|------|--------|
| A | E | 40 |

Grund:
A besitzt innerhalb dieses Belegs nur noch ein verfügbares Guthaben von 30.

---

Nicht erlaubt:
| Start | Ziel | Betrag |
|--------|------|--------|
| C | F | 40 |

Grund:
C besitzt innerhalb dieses Belegs nur ein verfügbares Guthaben von 30.

### Wichtige Eigenschaft
- Die Prüfung erfolgt immer **pro Konto und pro Beleg**.
- Ein Konto darf innerhalb eines Belegs niemals mehr weiterbuchen, als es innerhalb desselben Belegs erhalten hat.




---

## 3. Out of Scope

- Keine Datenbank-Anbindung (Speicherung reicht als lokale Datei, z. B. JSON/CSV)
- Keine Benutzer-Authentifizierung
- Keine Mehrsprachigkeit
- Keine E-Mail-Benachrichtigungen
- Alle nicht-beschriebenen Funktionalitäten bei anklicken der Knöpfe

---

## 4. Technische Constraints

- **Sprache:** Python (Version: z. B. 3.11)
- **Paketverfügbarkeit:** eingeschränkt — nur Standardbibliothek verfügbar; externe Installation via pip nicht möglich
- Daten doppelt speichern. Für Lesbarkeit in json format. Für convenience als csv Datei. Alle füllbaren Felder (inkl. Start- und Zielsystem) müssen vorhanden sein
- Pflichtfelder: Belegnummer (automatisch), Start-Hauptkonto, Ziel-Hauptkonto, Startsystem, Zielsystem, Betrag, Wertstellung. Außerdem muss entweder Leistungsart oder Verwendungszweck gefüllt sein
- Belegnummer soll eine eindeutige Nummer sein. 4-stellig reicht für Testzwecke

Wenn mit Standardbibliothek möglich:
- **GUI-Framework:** z. B. Tkinter (Standardbibliothek, kein Zusatzpaket nötig)
- **Zielplattform:** Windows
- **Datenhaltung:** lokale Datei (JSON/CSV), keine Serveranbindung

Wenn mit Standardbibliothek nicht möglich:
- weise mich sofort darauf hin!
- weitere Pakete dürfen importiert werden
- Endprodukt zu internen Verteilung als .exe bauen; Datei soll nicht von Anti-Virus Programm oder ähnlichem als schädlich klassifiziert werden; z.B. via PyInstaller/Nuitka


---

## 5. Ablauf, Allgemein

Happy-Path:
Start -> Eingabe -> Zur Kontrolle freigeben -> Buchung freigeben und speichern

Mehrere Buchungsschritte (Folgeschritt Buchen):
Start -> Eingabe [-> Folgeschitt buchen -> Eingabe (Ziel von vorherigem Schritt wird zu Start) ] repeat -> Zur Kontrolle freigeben -> Buchung freigeben und speichern

Abbruch: 
Start -> Eingabe -> Abbruch -> Oberfläche zum Ausgangszustand resetten


---

## 6. Ablauf, Details

1. Nutzer öffnet die App → sieht ein Feld "Belegnummer/Vorgangsnummer" (editable; Zahl 1-4 stellig) und Knöpfe: "Neuer Geschäftsvorgang" und "Beleg bearbeiten"
2. Zwei Möglichkeiten:
- Nutzer klickt "Neuer Geschäftsvorgang" -> siehe 6.1 Ablauf "Neuer Geschäftsvorgang"
- Nutzer gibt Belegnummer ein. Dann: Nutzer klickt auf "Beleg bearbeiten" -> siehe 6.2 Ablauf "Beleg bearbeiten"
- Das Eingabefeld ist nur dann relevant, wenn der Nutzer einen vorhandenen Beleg bearbeiten möchte. Bei Klick auf "Neuer Geschäftsvorgang" wird eine neue Belegnummer erzeugt und eine eventuell schon eingegebene Nummer überschrieben.
3. Es erscheinen weitere Felder und Knöpfe:
- weitere Felder: 
    * Start-Hauptkonto, Ziel-Hauptkonto, jeweils Unterkonto (freitext; zahl 1- bis 8-stellig)
    * Start-System und Ziel System (drop-down mit optionen: DaBu, ORAG, KK, GNB)
    * Wertstellung (Datum im Format DD.MM.YYYY; aktuelles Datum automatisch gefüllt; editierbar)
    * Betrag (Zahl, Darf Komma "," enthalten, kann aber auch ganzzahlig sein)
    * Leistungsart (freitext; zahl 1-3 stellig), 
    * Verwendungszweck (freitextfeld)
- weitere Knöpfe:
    * "Zur Kontrolle freigeben"
    * "Beleg weiter bearbeiten"
    * "Folgeschritt buchen" 
    * "Abbruch"
4. Nutzer füllt Felder aus
5. Nutzer klickt auf einen der Knöpfe:
- "Zur Kontrolle freigeben": 
    * check: sind alle pflichfelder ausgefüllt. Sonst: Fehlermeldung am unteren Bildschirmrand "Nicht alle Pflichtfelder sind ausgefüllt". Hier keine weiteren Schritte bis Nutzer ein Feld ausfüllt oder wieder auf einen Knopf drückt
    * Neue Oberfläche "Zusammenfassung":
    * Alle Felder werden nicht-editierbar angezeigt. 
    * Eine Tabelle der Buchhaltung wird ergänzt, inkl. der beiden Kontonummern, Soll/Haben und dem Betrag
    * Ein Knopf "Freigeben" erscheint. 
    * Nutzer klickt auf "Freigeben". App geht der Logik nach zu schritt 1 zurück und zeigt unten eine Nachricht "Buchung freigegeben"
    * Daten werden in ausgelagerter Datei gespeichert
- "Beleg weiter bearbeiten":
    * check: sind alle pflichfelder ausgefüllt. Sonst: Fehlermeldung am unteren Bildschirmrand "Nicht alle Pflichtfelder sind ausgefüllt". Hier keine weiteren Schritte bis Nutzer ein Feld ausfüllt oder wieder auf einen Knopf drückt
    * Belegnummer wird beibehalten, Start-Konto, Start-Unterkonto und Start-System bleiben stehen, alle anderen Felder werden geleert.
    * Ansicht "Historie" öffnet sich. Siehe 6.2 Ablauf "Beleg bearbeiten"
    * Alle bisherigen Buchungsschritte zum Beleg müssen in der Historie erhalten bleiben und sichtbar sein.
    * Jeder neue Buchungsschritt bleibt Bestandteil des Belegs und soll später freigegeben werden.
    * Programm geht weiter bei Schritt 4
- "Folgeschritt buchen": 
    * check: sind alle pflichfelder ausgefüllt. Sonst: Fehlermeldung am unteren Bildschirmrand "Nicht alle Pflichtfelder sind ausgefüllt". Hier keine weiteren Schritte bis Nutzer ein Feld ausfüllt oder wieder auf einen Knopf drückt
    * Belegnummer wird beibehalten, Werte in Ziel-Konto, Ziel-Unterkonto und Ziel-System werden in Start-Konto, Start-Unterkonto und Start-System eingetragen, alle anderen Felder werden geleert
    * Die entsprechende Folgebuchung soll in der Historie gekennzeichnet werden, zum Beispiel mit einem Pfeil vor dem Betrag: "->10"
    * Programm geht bei Schritt 4 weiter 
- "Abbruch": App geht zu Anfangszustand (Schritt 1) zurück

### 6.1 Ablauf "Neuer Geschäftsvorgang"
- Feld "Belegnummer/Vorgangsnummer" wird mit fortlaufender Zahl (logik im hintergrund) gefüllt
- Wenn das Feld vorher gefüllt war, wird die Zahl ersetzt. Das Feld ist nicht mehr editierbar, bis Ablauf wieder bei Schritt 1 anfängt (z.B. durch Abbruch oder Buchung freigegeben)
- Eine manuelle Eingabe vor dem Klick auf "Neuer Geschäftsvorgang" wird in diesem Ablauf nicht weiterverwendet; sie wird durch die generierte Nummer überschrieben.

### 6.2 Ablauf "Beleg bearbeiten"
- Es wird geprüft, ob die Belegnummer in den gespeicherten Daten vorhanden ist:
    * wenn Nein: Hinweis: Die Belegnummer ist nicht vorhanden. Reset der Maske zu Schritt 1. von 6.Ablauf, Details
    Wenn Ja: Feld ist nicht mehr editierbar, bis Ablauf wieder bei Schritt 1 anfängt (z.B. durch Abbruch oder Buchung freigegeben) 
- Eingeschobene Ansicht "Historie" öffnet sich (oberfläche aktualisieren):
    * rechteckiger Bereich, blauer Rahmen
    * Überschrift: Historie
    * 5 spalten: Betrag; Währung; Leistungsart - Verwendungszweck (Zahl, Bindestrich, text; Wenn Leistungsart oder Verwendungszweck nicht eingegeben wurde, bleibt der Teil des Feldes leer); Konto (Zielkonto); Wertstellungsdatum
- am Rechten Ende von jeder Spalte: Knopf "i". Aktuell ohne Funktion!
- erste Zeile zeigt immer die erste Buchung mit der Belegnummer an.  Das Datum muss älteste in der Liste sein. Darunter ist ein Strich über die gesamte Breite des rechteckigen Bereichs

#### Beispiel 6.2.1:
Hier wird nur von Konto A zu anderen Konten gebucht
- erste Zeile: 1000; EUR; - Geldeingang; A; 03.08.2026 
- zweite Zeile: 700; EUR; 3 - Tilgung; B; 03.08.2026
- dritte Zeile: 200; EUR; 10 - Mehrzinsen; C; 04.08.2026
- vierte Zeile: 100; EUR; A; ungeklärt/offen; --------
- Die letzte Zeile (vierte Zeile im Beispiel 6.2.1) wird immer automatisch generiert/berechnet und entspricht dem übrigen Guthaben auf Konto A (Ursprungsbetrag minus Betrag, der auf andere Konten gebucht wurde). Diese Zeile zeigt damit immer das verbleibende Guthaben auf dem ersten Startkonto des Belegs.

#### Beispiel 6.2.2:
Hier gibt es auch Buchungen mit folgeschritten (zB A-> B->C)
- erste Zeile: 1000; EUR; - Geldeingang; A; 03.08.2026 
- zweite Zeile: 700; EUR; 3 - Tilgung; B; 03.08.2026
- dritte Zeile: -> 200; EUR; 3 - Tilgung wg. xy; C; 03.08.2026 (dies zeigt eine Folgebuchung an, bei der ein Teil des Geldes von B -> C gebucht wurde)
- vierte Zeile: 200; EUR; 10 - Mehrzinsen; D; 04.08.2026
- fünfte Zeile: 100; EUR; A; ungeklärt/offen; --------
- Die letzte Zeile (fünfte Zeile im Beispiel 6.2.2) wird immer automatisch generiert/berechnet und entspricht dem übrigen Guthaben auf Konto A (Ursprungsbetrag minus Betrag, der auf andere Konten gebucht wurde)

Beispiel für eine einfache Folgebuchungs-Anzeige:
- 200; EUR; Zweck; B; Wertstellung
- ->10; EUR; Zweck; C; Wertstellung


## 7. Layout und Farben

optische Aspekte:
- weißer Hintergrund
- blaue Linie/Rahmen etwa 0.5cm von Rand entfernt
- Ausfüllbare Felder in hellblau hinterlegt
- Dropdown fenster in hellblau hinterlegt
- Fixierte Felder (nach "Zur Kontrollle freigeben"), werden hellgrau hinterlegt
- alle Knöpfe blau (selbe farbe wie rahmen)
- Die Beschreibung zu jedem Feld, steht immer über dem Feld
- Ein Knopf ist so hoch wie ein Feld inklusive Beschreibung
- lange Texte in Knöpfen (z.B. "Weiteren Buchungsschritt buchen") auf mehrere Zeilen verteilen

Layout: 
Die Oberfläche hat ein Layout von 4 gedachten Spalten. Das gedachte Grid wird mit Koordinaten beschrieben. Von (1,1) links oben bis (6,4) rechts unten. Alle nicht belegten Positionen sind leer
Von oben nach unten sind die Reihen folgendermaßen:
- Feld Belegnummer/Vorgangsnummer (1,1) , Knopf "Beleg bearbeiten" (1,3) und "Neuer Geschäftsvorgang" (1,4)
- Start-Hauptkonto (2,1), Start-systen (2,2), Ziel-Hauptkonto(2,3), Ziel-system (2,4)
- Unterkonto (3,1), Unterkonto (3,3)
- Betrag (4,1), Wertstellungsdatum (4,2)
- Leistungsart (5,1), Verwendungszweck (5,2)
- Knöpfe "Beleg weiter bearbeiten" (6,1), "Folgeschritt buchen" (6,2), "Zur Kontrolle freigeben" (6,3) und "Abbruch" (6,4)
