# SPEC: Interaktive Buchungsmaske (PoC)

---

## 1. Kontext & Ziel

Proof-of-concept für eine interaktive, generische Geld-Buchungsmaske im Kontext einer Bank. Es sollen Basisfunktionen (Buchung zwischen Konten, Suche von Belegen,...) erkennbar sein und Felder interaktiv sein. 

Zielgruppe: Softwarearchitekten und Business Analysten einer Bank. Erst-Präsentation als Dikussionsgrundlage in einem Meeting

---

## 2. Kernfunktionen

*Stichpunktartig, keine Prosa nötig.*

- [ ] Nutzer gibt eine Belegnummer/Vorgangsnummer ein, falls vorhanden
- [ ] Nutzer gibt Start- und Ziel-Konto, Betrag und Wertstellungsdatum ein
- [ ] Nutzer bucht ggfs. weitere Schritte und/oder gibt zur Kontrolle frei

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

1. Nutzer öffnet die App → sieht ein Feld "Belegnummer/Vorgangsnummer" und "Neuer Geschäftsvorgang"
2. Nutzer klickt "Neuer Geschäftsvorgang":
- Feld "Belegnummer/Vorgangsnummer" wird mit fortlaufender Zahl (logik im hintergrund) gefüllt
- es erscheinen weitere Felder: 
    * Start-Hauptkonto, Ziel-Hauptkonto, jeweils Unterkonto (freitext; zahl 1- bis 8-stellig)
    * Start-System und Ziel System (drop-down mit optionen: DaBu, ORAG, KK, GNB)
    * Wertstellung (Datum im Format DD.MM.YYYY; aktuelles Datum automatisch gefüllt; editierbar)
    * Betrag (Zahl, Darf Komma "," enthalten, aber nicht required)
    * Leistungsart (freitext; zahl 1-3 stellig), 
    * Verwendungszweck (freitextfeld)
- es erscheinen weitere Knöpfe:
    * "Zur Kontrolle freigeben"
    * "Beleg weiter bearbeiten"
    * "Folgeschritt buchen" 
    * "Abbruch"
3. Nutzer füllt Felder aus
4. Nutzer klickt auf einen der Knöpfe:
- "Zur Kontrolle freigeben": 
    * check: sind alle pflichfelder ausgefüllt. Sonst: Fehlermeldung am unteren Bildschirmrand "Nicht alle Pflichtfelder sind ausgefüllt". Hier keine weiteren Schritte bis Nutzer ein Feld ausfüllt oder wieder auf einen Knopf drückt
    * Neue Oberfläche "Zusammenfassung":
    * Alle Felder werden nicht-editierbar angezeigt. 
    * Eine Tabelle der Buchhaltung wird ergänzt, inkl. der beiden Kontonummern, Soll/Haben und dem Betrag
    * Ein Knopf "Freigeben" erscheint. 
    * Nutzer klickt auf "Freigeben". App geht der Logik nach zu schritt 1 zurück und zeigt unten eine Nachricht "Buchung freigegeben"
    * Daten werden in ausgelagerter Datei gespeichert
- "Folgeschritt buchen": 
    * check: sind alle pflichfelder ausgefüllt. Sonst: Fehlermeldung am unteren Bildschirmrand "Nicht alle Pflichtfelder sind ausgefüllt". Hier keine weiteren Schritte bis Nutzer ein Feld ausfüllt oder wieder auf einen Knopf drückt
    * Belegnummer wird beibehalten, Werte in Ziel-Konto und Ziel-System werden in Start-Konto und Start-System eingetragen, alle anderen Felder werden geleert
    * Programm geht bei Schritt 3 weiter 
- "Abbruch": App geht zu Anfangszustand (Schritt 1) zurück


## 7. Layout und Farben

optische Aspekte:
- weißer Hintergrund
- blaue Linie/Rahmen etwa 0.5cm von Rand entfernt
- Ausfüllbare Felder in hellblau hinterlegt
- Fixierte Felder (nach "Zur Kontrollle freigeben"), werden hellgrau hinterlegt
- Knöpfe blau (selbe farbe wie rahmen)

Layout: 
von oben nach unten in Reihen:
- Feld Belegnummer/Vorgangsnummer, Knopf "Offene Vorgänge anzeigen" und "Neuer Geschäftsvorgang"
- Start-Hauptkonto, Start-systen, Ziel-Hauptkonto, Ziel-system
- Unterkonto                Unterkonto
- Betrag, Wertstellung
- Leistungsart, Verwendungszweck
- Knöpfe "Beleg weiter bearbeiten", "Folgeschritt buchen", "Zur Kontrolle freigeben" und "Abbruch"
- lange Texte in Knöpfen (z.B. "Weiteren Buchungsschritt buchen") auf mehrere Zeilen verteilen


