#!/usr/bin/env python3
"""
Script pour transformer les IDs du fichier JSON:
- Enlève les IDs qui n'ont que deux numéros (ex: 1.2, 3.4)
- Transforme les autres IDs en 5 variantes: _yes, _cc, _na, _nt, _no
"""

import json
import re
import sys

def count_levels(id_str):
    """
    Compte le nombre de niveaux dans un ID.
    Exemples:
    - "1.2" -> 2 niveaux
    - "1.2.3" -> 3 niveaux
    - "3.3.1.1" -> 4 niveaux
    - "A2.1.1" -> 3 niveaux (le A ne compte pas comme niveau)
    """
    # Retirer le préfixe 'A' s'il existe
    clean_id = id_str[1:] if id_str.startswith('A') else id_str

    # Compter les points + 1 = nombre de niveaux
    # Ignorer les lettres à la fin (comme .a, .b, .c)
    # Extraire seulement la partie numérique
    parts = clean_id.split('.')

    # Compter seulement les parties numériques
    numeric_parts = 0
    for part in parts:
        # Si la partie est entièrement numérique, on la compte
        if part.isdigit():
            numeric_parts += 1
        # Sinon on s'arrête (pour gérer les .a, .b, .c, .d)
        else:
            break

    return numeric_parts

def transform_id(id_str):
    """
    Transforme un ID en 5 variantes avec les suffixes:
    _yes, _cc, _na, _nt, _no

    Exemple: "1.5.1" -> ["${1.5.1_yes}", "${1.5.1_cc}", "${1.5.1_na}", "${1.5.1_nt}", "${1.5.1_no}"]
    """
    suffixes = ['yes', 'cc', 'na', 'nt', 'no']
    return [f"${{{id_str}_{suffix}}}" for suffix in suffixes]

def process_ids(input_file, output_file):
    """
    Traite le fichier JSON d'entrée et génère le fichier de sortie.
    """
    print(f"Lecture du fichier: {input_file}")

    # Lire le fichier JSON
    with open(input_file, 'r', encoding='utf-8') as f:
        ids = json.load(f)

    print(f"Total d'IDs dans le fichier: {len(ids)}")

    # Filtrer et transformer les IDs
    result = []
    filtered_count = 0
    transformed_count = 0

    for id_str in ids:
        levels = count_levels(id_str)

        # Filtrer les IDs à 2 niveaux
        if levels == 2:
            print(f"  Filtré: {id_str} (2 niveaux)")
            filtered_count += 1
            continue

        # Transformer les IDs avec 3+ niveaux
        if levels >= 3:
            transformed = transform_id(id_str)
            result.extend(transformed)
            transformed_count += 1

    print(f"\n{'='*60}")
    print(f"RÉSUMÉ")
    print(f"{'='*60}")
    print(f"IDs filtrés (2 niveaux): {filtered_count}")
    print(f"IDs transformés (3+ niveaux): {transformed_count}")
    print(f"Total de variantes générées: {len(result)}")

    # Sauvegarder le résultat
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\nFichier de sortie créé: {output_file}")

    return len(result)

def main():
    import os

    # Use script directory as default if hardcoded paths don't exist
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_input = os.path.join(script_dir, "requirement_ids.json")
    default_output = os.path.join(script_dir, "requirement_ids_transformed.json")

    # Check if old hardcoded paths exist, otherwise use script directory
    old_input = r"c:\Users\ThomasMionnet\OneDrive - Vigitrust\Desktop\auto-fill\requirement_ids.json"
    old_output = r"c:\Users\ThomasMionnet\OneDrive - Vigitrust\Desktop\auto-fill\requirement_ids_transformed.json"

    if os.path.exists(old_input):
        input_file = old_input
        output_file = old_output
    else:
        input_file = default_input
        output_file = default_output

    try:
        total = process_ids(input_file, output_file)
        print(f"\n✓ Succès! {total} variantes ont été générées.")
    except Exception as e:
        print(f"\n✗ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
