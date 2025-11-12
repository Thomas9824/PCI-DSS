# DOCX Workflow - Changes Documentation

## Vue d'ensemble

Ce document décrit les modifications apportées au système PCI-Scraper pour automatiser la génération de documents DOCX avec des tags basés sur les IDs de requirements extraits des PDFs.

## Flux de travail mis à jour

### Ancien flux
1. L'utilisateur clique sur "Liste ID" → Télécharge un JSON avec les IDs
2. L'utilisateur télécharge manuellement le DOCX depuis le site PCI
3. L'utilisateur exécute manuellement les scripts de transformation

### Nouveau flux (automatisé)
1. L'utilisateur clique sur "Docx with tags"
2. **Automatique**: Extraction des IDs depuis les requirements affichés
3. **Automatique**: Scraping du site PCI et téléchargement du DOCX dans la langue détectée
4. **Automatique**: Transformation des IDs (ajout des suffixes _yes, _cc, _na, _nt, _no)
5. **Automatique**: Remplacement des form fields dans le DOCX par les tags
6. **Automatique**: Téléchargement du DOCX tagué généré

## Fichiers modifiés

### 1. `templates/converter2/converter.js`
**Changements:**
- Renommé le bouton "Liste ID" en "Docx with tags"
- Remplacé `downloadIdList()` par `generateDocxWithTags()`
- Nouvelle fonction appelle l'API `/api/generate-docx-with-tags`
- Envoie les requirement IDs et la langue au backend
- Télécharge automatiquement le fichier généré

**Lignes modifiées:** 233-241, 673-777

### 2. `auto-fill/docx_scraping.py`
**Changements:**
- Script complètement réécrit pour automatiser le téléchargement
- Fonction `download_docx_from_pciwebsite(language_code, download_path, doc_type='SAQ_D_Merchant')`
- Utilise Selenium pour:
  - Naviguer vers le site PCI document library
  - Trouver le document SAQ D Merchant
  - Sélectionner la langue appropriée dans le dropdown
  - Cliquer sur le bouton de téléchargement
  - Attendre la fin du téléchargement
- Support pour 7 langues: EN, FR, DE, ES, PT, ZH, JA
- Mode headless pour exécution en arrière-plan

**Lignes:** Fichier entièrement réécrit (1-160)

### 3. `auto-fill/docx_all.py`
**Changements:**
- Ajout de la fonction principale `generate_docx_with_tags(requirement_ids, language_code, output_dir)`
- Orchestration complète du workflow:
  1. Sauvegarde des IDs en JSON
  2. Transformation des IDs (via transform_ids.py)
  3. Téléchargement du DOCX (via docx_scraping.py)
  4. Remplacement des form fields (via replace_form_fields.py)
  5. Nettoyage des fichiers intermédiaires
- Support de deux modes:
  - Mode 1: Nouveau workflow automatisé
  - Mode 2: Mode legacy (compatibilité arrière)

**Lignes:** 1-216

### 4. `auto-fill/transform_ids.py`
**Changements:**
- Mise à jour de la fonction `main()` pour supporter des chemins dynamiques
- Fallback sur le répertoire du script si les chemins hardcodés n'existent pas
- Amélioration de la portabilité

**Lignes:** 98-127

### 5. `auto-fill/replace_form_fields.py`
**Changements:**
- Mise à jour de la fonction `main()` pour supporter des chemins dynamiques
- Fallback sur le répertoire du script si les chemins hardcodés n'existent pas
- Amélioration de la portabilité

**Lignes:** 357-392

### 6. `app.py`
**Changements:**
- Ajout de la route `/api/generate-docx-with-tags` (POST)
  - Reçoit requirement_ids et language
  - Appelle docx_all.generate_docx_with_tags()
  - Retourne le chemin du fichier généré
- Ajout de la route `/api/download-tagged-docx/<filename>` (GET)
  - Permet le téléchargement du fichier généré
- Ajout des dépendances dans `check_and_install_all_dependencies_on_startup()`:
  - python-docx
  - lxml

**Lignes:** 1038-1144, 1154-1163

## Structure des données

### Request vers `/api/generate-docx-with-tags`
```json
{
  "requirement_ids": ["1.1.1", "1.1.2", "1.2.1", ...],
  "language": "FR"
}
```

### Response de `/api/generate-docx-with-tags`
```json
{
  "success": true,
  "message": "DOCX with tags generated successfully",
  "filename": "PCI-DSS-v4-0-1-SAQ-D-Merchant_tagged.docx",
  "download_url": "/api/download-tagged-docx/PCI-DSS-v4-0-1-SAQ-D-Merchant_tagged.docx",
  "file_path": "/path/to/output/file.docx"
}
```

## Dépendances ajoutées

- **python-docx**: Manipulation des fichiers Word .docx
- **lxml**: Parsing XML pour la manipulation avancée des documents Word
- **selenium**: Web scraping du site PCI
- **webdriver-manager**: Gestion automatique des webdrivers

## Mapping des langues

Le système mappe les codes de langue aux options du site PCI:

| Code | Langue | Option Value |
|------|--------|--------------|
| EN   | English | 1 |
| FR   | French | 5 |
| DE   | German | 7 |
| ES   | Spanish | 13 |
| PT   | Portuguese | 11 |
| ZH   | Chinese | 3 |
| JA   | Japanese | 9 |

## Workflow de transformation des IDs

Les IDs sont transformés avec 5 variantes pour chaque requirement:

**Exemple:**
- Input: `1.5.1`
- Output:
  - `${1.5.1_yes}`
  - `${1.5.1_cc}`
  - `${1.5.1_na}`
  - `${1.5.1_nt}`
  - `${1.5.1_no}`

**Filtrage:**
- Les IDs à 2 niveaux (ex: `1.2`, `3.4`) sont exclus
- Seuls les IDs avec 3+ niveaux sont transformés

## Gestion des erreurs

Le système gère les erreurs à plusieurs niveaux:

1. **Frontend (converter.js)**:
   - Affichage de notifications utilisateur
   - Désactivation du bouton pendant le traitement
   - Réactivation après succès/échec

2. **Backend (app.py)**:
   - Validation des paramètres d'entrée
   - Gestion des exceptions avec traceback
   - Retour de messages d'erreur explicites

3. **Scraping (docx_scraping.py)**:
   - Timeout de 30 secondes pour le téléchargement
   - Vérification de l'existence du fichier téléchargé
   - Mode headless avec fallback

4. **Traitement DOCX (docx_all.py)**:
   - Nettoyage des fichiers temporaires
   - Gestion des erreurs à chaque étape
   - Rollback automatique en cas d'échec

## Répertoires de sortie

- **Fichiers téléchargés temporaires**: `tempfile.mkdtemp()`
- **Fichiers DOCX générés**: `Tools/PCI-Scraper/output/tagged_docx/`
- **Fichiers intermédiaires (JSON, logs)**: `Tools/PCI-Scraper/auto-fill/`

## Tests recommandés

1. **Test basique (EN)**:
   - Uploader un PDF SAQ D en anglais
   - Extraire les requirements
   - Cliquer sur "Docx with tags"
   - Vérifier le téléchargement du fichier tagué

2. **Test multilingue (FR)**:
   - Uploader un PDF SAQ D en français
   - Vérifier la détection automatique de la langue
   - Vérifier que le DOCX téléchargé est en français

3. **Test de gestion d'erreurs**:
   - Tester sans connexion Internet
   - Tester avec des IDs invalides
   - Vérifier les messages d'erreur

4. **Test de performance**:
   - Mesurer le temps de génération complet
   - Vérifier que le processus se termine même avec beaucoup d'IDs

## Notes techniques

### Selenium Headless Mode
Le script utilise Chrome en mode headless avec les options suivantes:
- `--headless`: Pas d'interface graphique
- `--no-sandbox`: Nécessaire pour certains environnements
- `--disable-dev-shm-usage`: Évite les problèmes de mémoire partagée

### Manipulation DOCX
Le remplacement des form fields utilise lxml pour:
- Trouver les éléments `w:fldChar` de type "begin"
- Supprimer tous les runs entre "begin" et "end"
- Insérer un nouveau run avec le tag de remplacement

### Sécurité
- Les fichiers temporaires sont nettoyés après traitement
- Les chemins sont validés avant utilisation
- Les inputs utilisateur sont échappés dans le HTML

## Compatibilité

- **Python**: 3.7+
- **Navigateurs**: Chrome/Chromium (via Selenium)
- **OS**: Windows, Linux, macOS
- **Flask**: 2.x+

## Migration

Pour migrer d'un ancien système:

1. Installer les nouvelles dépendances: `pip install python-docx lxml selenium webdriver-manager`
2. Vérifier que Chrome/Chromium est installé
3. Les anciens scripts restent compatibles (mode legacy)
4. Le nouveau workflow est accessible via le bouton "Docx with tags"

## Dépannage

### Problème: "WebDriver not found"
**Solution**: Installer webdriver-manager: `pip install webdriver-manager`

### Problème: "Download timeout"
**Solution**: Augmenter le timeout dans docx_scraping.py (ligne 116)

### Problème: "Form fields not replaced"
**Solution**: Vérifier que le DOCX téléchargé contient des form fields Word

### Problème: "Language not detected"
**Solution**: Vérifier que le PDF extrait contient la langue dans les métadonnées

## Maintenance future

- Mettre à jour les mappings de langue si le site PCI change
- Adapter les sélecteurs CSS/ID si la structure HTML du site PCI change
- Ajouter des logs plus détaillés pour le debugging
- Implémenter un cache pour éviter de re-télécharger les mêmes documents

## Contact

Pour toute question ou problème, consulter la documentation du projet ou contacter l'équipe de développement.

---

**Dernière mise à jour**: 2025-01-22
**Version**: 1.0.0
