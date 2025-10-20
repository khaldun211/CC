#!/usr/bin/env python3
"""
List Comparator App
===================
Eine Python-Anwendung zum Vergleichen von zwei Listen.
"""

def compare_lists(list1, list2):
    """
    Vergleicht zwei Listen und gibt detaillierte Informationen zurück.

    Args:
        list1: Erste Liste
        list2: Zweite Liste

    Returns:
        Dictionary mit Vergleichsergebnissen
    """
    set1 = set(list1)
    set2 = set(list2)

    results = {
        'gemeinsame_elemente': list(set1 & set2),
        'nur_in_liste1': list(set1 - set2),
        'nur_in_liste2': list(set2 - set1),
        'alle_eindeutigen': list(set1 | set2),
        'sind_identisch': list1 == list2,
        'haben_gleiche_elemente': set1 == set2,
        'anzahl_liste1': len(list1),
        'anzahl_liste2': len(list2)
    }

    return results


def print_results(results):
    """Gibt die Vergleichsergebnisse formatiert aus."""
    print("\n" + "="*60)
    print("VERGLEICHSERGEBNISSE")
    print("="*60)

    print(f"\n📊 Statistiken:")
    print(f"   Anzahl Elemente in Liste 1: {results['anzahl_liste1']}")
    print(f"   Anzahl Elemente in Liste 2: {results['anzahl_liste2']}")

    print(f"\n✓ Listen sind identisch: {results['sind_identisch']}")
    print(f"✓ Listen haben gleiche Elemente: {results['haben_gleiche_elemente']}")

    print(f"\n🔗 Gemeinsame Elemente ({len(results['gemeinsame_elemente'])}):")
    if results['gemeinsame_elemente']:
        for item in sorted(results['gemeinsame_elemente'], key=str):
            print(f"   - {item}")
    else:
        print("   (keine)")

    print(f"\n⚡ Nur in Liste 1 ({len(results['nur_in_liste1'])}):")
    if results['nur_in_liste1']:
        for item in sorted(results['nur_in_liste1'], key=str):
            print(f"   - {item}")
    else:
        print("   (keine)")

    print(f"\n⚡ Nur in Liste 2 ({len(results['nur_in_liste2'])}):")
    if results['nur_in_liste2']:
        for item in sorted(results['nur_in_liste2'], key=str):
            print(f"   - {item}")
    else:
        print("   (keine)")

    print(f"\n🌟 Alle eindeutigen Elemente ({len(results['alle_eindeutigen'])}):")
    for item in sorted(results['alle_eindeutigen'], key=str):
        print(f"   - {item}")

    print("\n" + "="*60 + "\n")


def parse_input(input_str):
    """Konvertiert Benutzereingabe in eine Liste."""
    # Entfernt Klammern falls vorhanden
    input_str = input_str.strip()
    if input_str.startswith('[') and input_str.endswith(']'):
        input_str = input_str[1:-1]

    # Teilt bei Kommas und bereinigt
    items = [item.strip().strip('"\'') for item in input_str.split(',')]

    # Versucht Zahlen zu konvertieren
    result = []
    for item in items:
        if item:
            try:
                # Versucht Integer
                result.append(int(item))
            except ValueError:
                try:
                    # Versucht Float
                    result.append(float(item))
                except ValueError:
                    # Bleibt String
                    result.append(item)

    return result


def main():
    """Hauptfunktion der Anwendung."""
    print("\n" + "="*60)
    print("       📋 LISTEN-VERGLEICHER")
    print("="*60)
    print("\nGib zwei Listen ein, um sie zu vergleichen.")
    print("Format: Elemente mit Komma getrennt (z.B. 1, 2, 3 oder a, b, c)")
    print("-"*60)

    # Liste 1 eingeben
    list1_input = input("\n📝 Liste 1: ")
    list1 = parse_input(list1_input)
    print(f"   → Erkannt: {list1}")

    # Liste 2 eingeben
    list2_input = input("\n📝 Liste 2: ")
    list2 = parse_input(list2_input)
    print(f"   → Erkannt: {list2}")

    # Listen vergleichen
    results = compare_lists(list1, list2)

    # Ergebnisse ausgeben
    print_results(results)


if __name__ == "__main__":
    # Beispiel-Demo wenn direkt ausgeführt
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        print("\n🎯 DEMO-MODUS\n")

        # Beispiel 1: Zahlen
        print("Beispiel 1: Zahlenlisten")
        liste1 = [1, 2, 3, 4, 5]
        liste2 = [4, 5, 6, 7, 8]
        print(f"Liste 1: {liste1}")
        print(f"Liste 2: {liste2}")
        results = compare_lists(liste1, liste2)
        print_results(results)

        # Beispiel 2: Strings
        print("\nBeispiel 2: Textlisten")
        liste1 = ["Apfel", "Banane", "Orange", "Kirsche"]
        liste2 = ["Banane", "Erdbeere", "Orange", "Mango"]
        print(f"Liste 1: {liste1}")
        print(f"Liste 2: {liste2}")
        results = compare_lists(liste1, liste2)
        print_results(results)

        # Beispiel 3: Gemischte Liste
        print("\nBeispiel 3: Gemischte Liste")
        liste1 = [1, "zwei", 3.0, "vier"]
        liste2 = ["zwei", 2, 3.0, 4]
        print(f"Liste 1: {liste1}")
        print(f"Liste 2: {liste2}")
        results = compare_lists(liste1, liste2)
        print_results(results)
    else:
        main()
