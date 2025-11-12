# PCI Requirements Comparison Module

## Description

Ce module permet de comparer les exports CSV des requirements PCI DSS avec une version de référence sauvegardée, pour identifier les changements (ajouts/suppressions de requirements).

## Structure

```
pci_compare/
├── __init__.py                 # Module initialization
├── compare_requirements.py     # Logic principale de comparaison
├── stored_references/          # Dossier contenant les références par langue
│   ├── reference_EN.csv       # Référence pour l'anglais
│   └── reference_FR.csv       # Référence pour le français
└── README.md                  # Ce fichier
```

## Fonctionnalités

### 1. Sauvegarde de référence

Sauvegarde l'export actuel comme référence pour les comparaisons futures:
- API Endpoint: `POST /api/save-reference/<language>`
- Stockage: `pci_compare/stored_references/reference_{language}.csv`

### 2. Comparaison

Compare l'export actuel avec la référence sauvegardée:
- API Endpoint: `POST /api/compare-requirements/<language>`
- Retourne:
  - `added`: Liste des IDs ajoutés
  - `removed`: Liste des IDs supprimés
  - `unchanged`: Liste des IDs inchangés
  - Statistiques: counts pour chaque catégorie

### 3. Information sur la référence

Obtenir des informations sur la référence stockée:
- API Endpoint: `GET /api/reference-info/<language>`
- Retourne: métadonnées du fichier de référence

## Utilisation dans l'interface

1. **Extraire les requirements** depuis un PDF PCI DSS
2. **Cliquer sur "Compare"**:
   - S'il n'y a pas de référence: propose de sauvegarder l'export actuel comme référence
   - S'il y a une référence: affiche les différences

3. **Résultats de comparaison** affichés sous les statistiques:
   - **IDs Ajoutés** (badges verts): Requirements présents dans l'export actuel mais pas dans la référence
   - **IDs Supprimés** (badges rouges): Requirements présents dans la référence mais pas dans l'export actuel
   - **IDs Inchangés** (info bleue): Nombre de requirements identiques

## Exemple de workflow

### Première utilisation
```
1. Upload PDF → Extract → Voir les results
2. Click "Compare" → Popup: "No reference found"
3. Accept → Référence sauvegardée
4. Message: "Reference saved successfully!"
```

### Comparaisons ultérieures
```
1. Upload nouveau PDF → Extract → Voir les résultats
2. Click "Compare" → Comparaison automatique
3. Voir les différences:
   - Added Requirements: 1.2.8, 3.5.1 (en vert)
   - Removed Requirements: 2.1.1 (en rouge)
   - Unchanged: 328 requirements
```

## API Python

### Utilisation directe du module

```python
from pci_compare.compare_requirements import RequirementsComparator

# Initialiser
comparator = RequirementsComparator()

# Sauvegarder une référence
result = comparator.save_reference('path/to/current.csv', 'EN')
print(result['message'])

# Comparer
result = comparator.compare('path/to/new_export.csv', 'EN')
if result['success']:
    print(f"Added: {result['comparison']['added']}")
    print(f"Removed: {result['comparison']['removed']}")
    print(f"Unchanged: {result['comparison']['unchanged_count']}")

# Vérifier l'existence d'une référence
has_ref = comparator.has_reference('EN')

# Obtenir des infos sur la référence
info = comparator.get_reference_info('EN')
```

## Format CSV attendu

Le CSV doit contenir au minimum:
- Une colonne `id` ou `req_num` avec les identifiants des requirements
- Format exemple: `1.1.1`, `1.1.2`, `2.1`, etc.

## Notes techniques

- Tri naturel des IDs (1.1, 1.2, 1.10 au lieu de 1.1, 1.10, 1.2)
- Support multi-langues (EN, FR, etc.)
- Comparaison basée uniquement sur les IDs (pas le contenu)
- Fichiers de référence stockés localement dans `stored_references/`

## Développé par

Vigitrust - PCI Tools Suite
