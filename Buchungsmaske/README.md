# Buchungsmaske (PoC)

## Deutsch

Ein Windows-Desktop-Prototyp zur Erfassung mehrstufiger Buchungen mit lokaler JSON- und CSV-Speicherung. Gedacht als Diskussionsgrundlage für eine erste fachliche Präsentation, nicht für den produktiven Bankbetrieb.

### Start

Voraussetzung: Python 3.11 mit Tkinter (Standardbibliothek). Im Projektordner ausführen:

```powershell
python Buchungsmaske.py
```

Die Anwendung unterstützt neue Vorgänge mit automatisch erzeugter Belegnummer, das Bearbeiten vorhandener Belege, Buchungsschritte, eine Historie sowie eine Zusammenfassung vor der Freigabe. Freigegebene Buchungen werden in `bookings.json` und `bookings.csv` gespeichert.

**Einschränkung:** Die im Konzept beschriebene Prüfung des verfügbaren Guthabens pro Konto und Beleg ist noch nicht implementiert. Eingaben werden außerdem nur auf Pflichtfelder geprüft. Daher ist die Anwendung ausschließlich ein PoC.

## English

A Windows desktop prototype for entering multi-step transactions and storing them locally in JSON and CSV. It is intended as a discussion aid for an initial business presentation, not for production banking.

### Run

Requirement: Python 3.11 with Tkinter (standard library). Run from the project directory:

```powershell
python Buchungsmaske.py
```

The app supports new transactions with automatically generated voucher numbers, editing existing vouchers, adding transaction steps, viewing history, and reviewing a summary before release. Released transactions are saved to `bookings.json` and `bookings.csv`.

**Limitation:** The per-account, per-voucher available-balance check described in the specification is not implemented. Input validation currently checks required fields only, so this remains a proof of concept.