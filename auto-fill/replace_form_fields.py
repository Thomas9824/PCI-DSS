#!/usr/bin/env python3
"""
Script pour remplacer les zones de remplissage Word par des balises depuis un fichier JSON.
Les balises sont utilisées dans l'ordre de la liste JSON.
"""

import re
import json
import zipfile
import shutil
import os
from docx import Document
from lxml import etree
import sys

def extract_id_from_text(text):
    """
    Extrait un ID au format X.X.X, X.X.X.X ou AX.X.X du texte.
    Retourne un tuple (id_string, tuple_for_sorting) ou None si pas trouvé.
    """
    if not text:
        return None

    # Pattern pour matcher les IDs type A1.1.1, A2.3.4, A3.1.1.1, etc.
    pattern_a = r'\b(A\d+(?:\.\d+){1,})\b'
    match_a = re.search(pattern_a, text)

    if match_a:
        id_str = match_a.group(1)
        # Retirer le 'A' et convertir en tuple d'entiers
        numbers_str = id_str[1:]  # Enlever le 'A'
        parts = tuple(map(int, numbers_str.split('.')))
        # Ajouter un grand nombre au début pour que les IDs 'A' soient triés après les IDs numériques
        # (1000, ...) garantit que A1.1.1 vient après 12.2.3, 13.4.3, etc.
        sort_key = (1000,) + parts
        return (id_str, sort_key)

    # Pattern pour matcher les IDs type 1.1.1, 2.3.4, 4.3.2.4, 12.4.3, etc.
    pattern_num = r'\b(\d+(?:\.\d+){1,})\b'
    match_num = re.search(pattern_num, text)

    if match_num:
        id_str = match_num.group(1)
        # Convertir en tuple d'entiers pour le tri
        parts = tuple(map(int, id_str.split('.')))
        return (id_str, parts)

    return None

def get_table_id(table):
    """
    Extrait l'ID d'un tableau en cherchant dans toutes ses cellules.
    Retourne (id_string, tuple_for_sorting) ou None.
    """
    for row in table.rows:
        for cell in row.cells:
            result = extract_id_from_text(cell.text)
            if result:
                return result
    return None

def count_ids_in_table(table):
    """
    Compte le nombre d'IDs différents dans un tableau.
    Retourne le nombre d'IDs trouvés.
    """
    ids_found = set()
    for row in table.rows:
        for cell in row.cells:
            result = extract_id_from_text(cell.text)
            if result:
                ids_found.add(result[0])  # Ajouter l'ID string au set
    return len(ids_found)

def find_and_replace_form_fields_in_paragraph(paragraph, replacement_text):
    """
    Trouve et remplace un champ de formulaire (fldChar) dans un paragraphe.
    Retourne True si un champ a été trouvé et remplacé, False sinon.
    """
    namespaces = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    }

    # Chercher tous les fldChar avec type="begin"
    fld_begins = paragraph._element.findall('.//w:fldChar[@w:fldCharType="begin"]', namespaces)

    if not fld_begins:
        return False

    # Remplacer le premier champ trouvé
    fld_begin = fld_begins[0]

    # Trouver le run parent du fldChar begin
    begin_run = fld_begin.getparent()

    # Chercher les autres éléments du champ (separate et end)
    # On doit parcourir les runs suivants dans le paragraphe
    paragraph_element = paragraph._element
    runs = paragraph_element.findall('.//w:r', namespaces)

    begin_index = None
    separate_index = None
    end_index = None

    # Trouver les indices des runs contenant begin, separate et end
    for i, run in enumerate(runs):
        fld_chars = run.findall('.//w:fldChar', namespaces)
        for fld_char in fld_chars:
            fld_type = fld_char.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fldCharType')
            if fld_type == 'begin' and begin_index is None:
                begin_index = i
            elif fld_type == 'separate' and begin_index is not None and separate_index is None:
                separate_index = i
            elif fld_type == 'end' and begin_index is not None:
                end_index = i
                break

        if end_index is not None:
            break

    if begin_index is None or end_index is None:
        return False

    # Supprimer tous les runs entre begin et end (inclus)
    for i in range(end_index, begin_index - 1, -1):
        paragraph_element.remove(runs[i])

    # Créer un nouveau run avec le texte de remplacement
    new_run = etree.Element('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r')

    # Copier les propriétés du run original si possible
    if begin_index < len(runs):
        original_rPr = runs[begin_index].find('.//w:rPr', namespaces)
        if original_rPr is not None:
            new_run.append(etree.fromstring(etree.tostring(original_rPr)))

    new_text = etree.SubElement(new_run, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t')
    new_text.text = replacement_text

    # Insérer le nouveau run à la place
    if begin_index < len(paragraph_element):
        paragraph_element.insert(begin_index, new_run)
    else:
        paragraph_element.append(new_run)

    return True

def count_form_fields_in_cell(cell):
    """
    Compte le nombre de champs de formulaire dans une cellule.
    """
    namespaces = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    }

    fld_begins = cell._element.findall('.//w:fldChar[@w:fldCharType="begin"]', namespaces)
    return len(fld_begins)

def remove_document_protection(docx_path):
    """
    Enlève la protection/sécurité du document Word.
    Manipule directement le fichier ZIP du document Word pour supprimer la protection.
    Retourne le chemin du fichier modifié.
    """
    try:
        # Créer un répertoire temporaire
        temp_dir = docx_path + "_temp"
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

        # Extraire le document Word (qui est un fichier ZIP)
        with zipfile.ZipFile(docx_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Chemin du fichier settings.xml
        settings_path = os.path.join(temp_dir, 'word', 'settings.xml')

        if os.path.exists(settings_path):
            # Lire et parser le fichier settings.xml
            tree = etree.parse(settings_path)
            root = tree.getroot()

            # Namespace Word
            namespaces = {
                'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
            }

            # Chercher et supprimer l'élément de protection du document
            protection = root.find('.//w:documentProtection', namespaces)
            if protection is not None:
                root.remove(protection)
                # Sauvegarder le fichier modifié
                tree.write(settings_path, encoding='utf-8', xml_declaration=True)
                print("  Protection du document supprimée depuis settings.xml")
            else:
                print("  Aucune protection détectée dans settings.xml")

        # Créer un nouveau fichier docx sans protection
        output_path = docx_path.replace('.docx', '_unprotected.docx')
        if os.path.exists(output_path):
            os.remove(output_path)

        # Re-créer le fichier ZIP avec les modifications
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
            for root_dir, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root_dir, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zip_out.write(file_path, arcname)

        # Nettoyer le répertoire temporaire
        shutil.rmtree(temp_dir)

        print(f"  Document sans protection créé: {output_path}")
        return output_path

    except Exception as e:
        print(f"  Avertissement: Impossible d'enlever la protection: {e}")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        return docx_path

def load_tags_from_json(json_path):
    """
    Charge la liste des balises depuis un fichier JSON.
    """
    print(f"Chargement des balises depuis: {json_path}")
    with open(json_path, 'r', encoding='utf-8') as f:
        tags = json.load(f)
    print(f"Total de balises chargées: {len(tags)}")
    return tags

def process_document(input_path, output_path, tags_list):
    """
    Traite le document Word pour remplacer les zones de remplissage dans les tableaux.
    Utilise les balises de tags_list dans l'ordre.
    """
    # Supprimer la protection du document
    print("Suppression de la protection du document...")
    unprotected_path = remove_document_protection(input_path)

    print(f"\nOuverture du document: {unprotected_path}")
    doc = Document(unprotected_path)

    # Étape 1: Identifier tous les tableaux avec leurs IDs
    print("\nÉtape 1: Identification des tableaux avec IDs...")
    tables_with_ids = []

    for i, table in enumerate(doc.tables):
        result = get_table_id(table)
        if result:
            id_str, sort_key = result

            # Compter le nombre d'IDs dans le tableau
            num_ids = count_ids_in_table(table)

            # Ne prendre en compte que les tableaux avec au moins 3 IDs
            if num_ids >= 3:
                tables_with_ids.append({
                    'index': i,
                    'table': table,
                    'id': id_str,
                    'sort_key': sort_key
                })
                print(f"  Tableau {i}: ID trouvé = {id_str} ({num_ids} IDs dans le tableau)")
            else:
                print(f"  Tableau {i}: ID trouvé = {id_str} mais exclu (seulement {num_ids} ID(s), minimum requis: 3)")

    print(f"\nTotal de tableaux avec IDs (minimum 3 IDs): {len(tables_with_ids)}")

    # Étape 2: Trier les tableaux par ID
    print("\nÉtape 2: Tri des tableaux par ordre des IDs...")
    tables_with_ids.sort(key=lambda x: x['sort_key'])

    print("Ordre des tableaux après tri:")
    for item in tables_with_ids:
        print(f"  ID: {item['id']}")

    # Étape 3: Remplacer les zones de remplissage par des balises
    print("\nÉtape 3: Remplacement des zones de remplissage...")

    tag_index = 0
    replacements = []
    total_fields_count = 0  # Count total fields in tables with IDs

    # First pass: count total fields in all tables with IDs
    for table_info in tables_with_ids:
        table = table_info['table']
        for row in table.rows:
            for cell in row.cells:
                total_fields_count += count_form_fields_in_cell(cell)

    print(f"Total de champs trouvés dans les tableaux avec IDs: {total_fields_count}")
    print()

    for table_info in tables_with_ids:
        table = table_info['table']
        table_id = table_info['id']


        # Parcourir toutes les cellules du tableau dans l'ordre
        for row_idx, row in enumerate(table.rows):
            for cell_idx, cell in enumerate(row.cells):
                # Compter combien de champs de formulaire il y a dans cette cellule
                field_count = count_form_fields_in_cell(cell)

                # Remplacer chaque champ de formulaire
                for field_num in range(field_count):
                    # Vérifier qu'il reste des balises dans la liste
                    if tag_index >= len(tags_list):
                        print(f"\n⚠ ATTENTION: Plus de balises disponibles! {tag_index} champs traités, mais il en reste.")
                        print(f"  Champ non remplacé: Tableau {table_id}, ligne {row_idx + 1}, cellule {cell_idx + 1}")
                        continue

                    tag = tags_list[tag_index]

                    # Parcourir les paragraphes de la cellule
                    replaced = False
                    for para in cell.paragraphs:
                        if find_and_replace_form_fields_in_paragraph(para, tag):
                            replacements.append({
                                'number': tag_index + 1,
                                'tag': tag,
                                'table_id': table_id,
                                'position': f"ligne {row_idx + 1}, cellule {cell_idx + 1}"
                            })
                            tag_index += 1
                            replaced = True
                            break

                    if not replaced and tag_index < len(tags_list):
                        print(f"  Avertissement: Impossible de remplacer le champ dans ligne {row_idx + 1}, cellule {cell_idx + 1}")

    # Sauvegarder le document modifié
    print(f"\nÉtape 4: Sauvegarde du document modifié...")
    doc.save(output_path)
    print(f"Document sauvegardé: {output_path}")

    # Afficher un résumé
    print(f"\n{'='*60}")
    print(f"RÉSUMÉ")
    print(f"{'='*60}")
    print(f"Total de zones de remplissage remplacées: {tag_index}")
    print(f"Total de tableaux traités: {len(tables_with_ids)}")
    print(f"Total de balises disponibles dans le JSON: {len(tags_list)}")
    if tag_index < len(tags_list):
        print(f"⚠ Balises non utilisées: {len(tags_list) - tag_index}")
    elif tag_index > len(tags_list):
        print(f"⚠ ATTENTION: Pas assez de balises! {tag_index - len(tags_list)} champs n'ont pas pu être remplacés.")

    # Sauvegarder la liste des remplacements dans un fichier
    mapping_file = output_path.replace('.docx', '_mapping.txt')
    with open(mapping_file, 'w', encoding='utf-8') as f:
        f.write("MAPPING DES BALISES\n")
        f.write("="*60 + "\n\n")
        for r in replacements:
            f.write(f"{r['tag']}: Tableau {r['table_id']} - {r['position']}\n")

    print(f"Fichier de mapping créé: {mapping_file}")

    # Nettoyer le fichier temporaire non protégé si différent de l'input
    if unprotected_path != input_path and os.path.exists(unprotected_path):
        os.remove(unprotected_path)
        print(f"Fichier temporaire nettoyé: {unprotected_path}")

    # Return both replaced count and total fields count
    return (tag_index, total_fields_count)

def main():
    # Use script directory as default
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_input = os.path.join(script_dir, "PCI-DSS-v4-0-1-SAQ-D-Merchant.docx")
    default_output = os.path.join(script_dir, "PCI-DSS-v4-0-1-SAQ-D-Merchant_tagged.docx")
    default_tags = os.path.join(script_dir, "requirement_ids_transformed.json")

    # Check if old hardcoded paths exist, otherwise use script directory
    old_input = r"c:\project\auto-fill\PCI-DSS-v4-0-1-SAQ-D-Merchant.docx"
    old_output = r"c:\project\auto-fill\PCI-DSS-v4-0-1-SAQ-D-Merchant_tagged.docx"
    old_tags = r"c:\project\auto-fill\requirement_ids_transformed.json"

    if os.path.exists(old_input):
        input_file = old_input
        output_file = old_output
        tags_file = old_tags
    else:
        input_file = default_input
        output_file = default_output
        tags_file = default_tags

    try:
        # Charger les balises depuis le JSON
        tags_list = load_tags_from_json(tags_file)

        # Traiter le document
        total_replaced = process_document(input_file, output_file, tags_list)
        print(f"\n✓ Succès! {total_replaced} zones de remplissage ont été remplacées.")
    except Exception as e:
        print(f"\n✗ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
