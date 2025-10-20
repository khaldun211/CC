# Listen-Vergleicher App 📋

Eine Python-Anwendung zum Vergleichen von zwei Listen mit detaillierten Analysefunktionen.

## Features

- ✅ Vergleicht zwei Listen beliebiger Typen (Zahlen, Text, gemischt)
- ✅ Zeigt gemeinsame Elemente
- ✅ Zeigt eindeutige Elemente in jeder Liste
- ✅ Zeigt alle eindeutigen Elemente
- ✅ Statistiken über die Listen
- ✅ Benutzerfreundliche Eingabe und Ausgabe
- ✅ Demo-Modus mit Beispielen

## Installation

Keine zusätzlichen Abhängigkeiten erforderlich - nur Python 3.x

## Verwendung

### Interaktiver Modus

```bash
python3 list_comparator.py
```

Dann einfach die Listen eingeben, getrennt durch Kommas:

```
📝 Liste 1: 1, 2, 3, 4, 5
📝 Liste 2: 4, 5, 6, 7, 8
```

### Demo-Modus

Um Beispiele zu sehen:

```bash
python3 list_comparator.py --demo
```

## Beispiel-Ausgabe

```
============================================================
VERGLEICHSERGEBNISSE
============================================================

📊 Statistiken:
   Anzahl Elemente in Liste 1: 5
   Anzahl Elemente in Liste 2: 5

✓ Listen sind identisch: False
✓ Listen haben gleiche Elemente: False

🔗 Gemeinsame Elemente (2):
   - 4
   - 5

⚡ Nur in Liste 1 (3):
   - 1
   - 2
   - 3

⚡ Nur in Liste 2 (3):
   - 6
   - 7
   - 8

🌟 Alle eindeutigen Elemente (8):
   - 1
   - 2
   - 3
   - 4
   - 5
   - 6
   - 7
   - 8
```

## Unterstützte Eingabeformate

- Zahlen: `1, 2, 3`
- Text: `Apfel, Banane, Orange`
- Gemischt: `1, zwei, 3.0, vier`
- Mit Klammern: `[1, 2, 3]`

Die App erkennt automatisch den Typ der Elemente!
