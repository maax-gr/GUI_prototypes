# SPEC: Interaktive Buchungsmaske (PoC)

---

## 1. Kontext & Ziel

Proof-of-concept für eine interaktive, generische Geld-Buchungsmaske im Kontext einer Bank. Es sollen Basisfunktionen (Buchung zwischen Konten, Suche von Belegen,...) erkennbar sein und Felder interaktiv sein. 

Zielgruppe: Softwarearchitekten und Business Analysten einer Bank. Erst-Präsentation als Dikussionsgrundlage in einem Meeting

---

## 2. Kernfunktionen

*Stichpunktartig, keine Prosa nötig.*

- [ ] Nutzer gibt eine Belegnummer ein, falls vorhanden
- [ ] Oberfläche zeigt bereits getätigte Buchungen und offene Beträge an, die zu der Belegnummer gehören
- [ ] Nutzer gibt Start- und Ziel-Konto, Betrag und Wertstellungsdatum ein
- [ ] Nutzer gibt zur Kontrolle frei

---

## 3. Out of Scope

- Keine Datenbank-Anbindung (Speicherung reicht als lokale Datei, z. B. JSON/CSV)
- Keine Benutzer-Authentifizierung
- Keine Mehrsprachigkeit
- Keine E-Mail-Benachrichtigungen

---

## 4. Technische Constraints

- **Sprache:** Python (Version: z. B. 3.11)
- **Paketverfügbarkeit:** eingeschränkt — nur Standardbibliothek verfügbar; externe Installation via pip nicht möglich

Wenn mit Standardbibliothek möglich:
- **GUI-Framework:** z. B. Tkinter (Standardbibliothek, kein Zusatzpaket nötig)
- **Zielplattform:** Windows
- **Datenhaltung:** lokale Datei (JSON/CSV), keine Serveranbindung

Wenn mit Standardbibliothek nicht möglich:
- weise mich sofort darauf hin!
- weitere Pakete dürfen importiert werden
- Endprodukt zu internen Verteilung als .exe bauen; Datei soll nicht von Anti-Virus Programm oder ähnlichem als schädlich klassifiziert werden; z.B. via PyInstaller/Nuitka

---

## 5. Beispiel-Ablauf ("So soll's sich anfühlen")

*Ein kurzer Walkthrough aus Nutzersicht — konkreter als jede abstrakte Beschreibung.*

1. Nutzer öffnet die App → sieht ein Feld "Belegnummer" und "Enter"
2. Nutzer klickt "Enter":
- Feld "Belegnummer" wird mit fortlaufender Zahl (logik im hintergrund) gefüllt
- es erscheinen weitere Felder: Start-Konto (freitext; zahl 8-stellig), Start-System (drop-down mit optionen: ORAG, KK, GNB), Ziel-Konto (wie Start-Konto), Ziel-Syste (wie Start-System), Wertstellung (Datum im Format DD.MM.YYYY; aktuelles Datum automatisch gefüllt; editierbar), Betrag, Leistungsart (freitext; zahl 1-3 stellig), 
- es erscheinen weiter Knöpfe: "Zur Kontrolle freigeben", "Weiteren Buchungsschritt buchen" und "Abbruch"
3. Nutzer füllt Felder aus
4. Nutzer klickt auf einen der Knöpfe:
- "Zur Kontrolle freigeben": Neue Oberfläche "Zusammenfassung". Alle Felder werden nicht-editierbar angezeigt. Eine Tabelle der Buchhaltung wird ergänzt, inkl. der beiden KOntonummern, Soll/Haben und dem Betrag. Ein Knopf "Freigeben" erscheint. Nutzer klickt auf "Freigeben". App geht der Logik nach zu schritt 1 zurück und zeigt unten eine Nachricht "Buchung freigegeben"
- "Weiteren Buchungsschritt buchen": Belegnummer wird beibehalten, Werte in Ziel-Konto und Ziel-System werden in Start-Konto und Start-System eingetragen, alle anderen Felder werden geleert; Programm geht bei Schritt 3 weiter 
- "Abbruch": App geht zu Anfangszustand (Schritt 1) zurück



