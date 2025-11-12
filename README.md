# PCI-Scraper

> [English version below](#english) | [Version française ci-dessous](#français)

---

<a id="english"></a>
## English

### Description

Tool suite for managing and tracking PCI DSS (Payment Card Industry Data Security Standard) and SAQ (Self-Assessment Questionnaire) documents.

Flask web application that allows you to:
- **Automatically detect** changes on the official PCI Security Standards Council website
- **Extract and structure** requirements from PCI DSS PDFs (English and French)
- **Track the history** of all detected changes
- **Expose a REST API** for automation

---

### 🚀 Quick Start

#### Did you receive the `PCITools.exe` executable?

**Simple and standalone** - No installation required:

1. Double-click on `PCITools.exe`
2. Your browser automatically opens at http://localhost:5001

**Minimum requirements:**
- Windows 10 or 11
- Chrome or Edge (for web scraping)

> **Note**: The executable contains Python and all dependencies. No Python installation is required.

---

### 📋 Prerequisites

#### For Windows executable

- ✅ Windows 10/11
- ✅ Chrome or Edge installed
- ✅ Internet connection (to scrape the PCI SSC website)
- ❌ **NO Python needed**

#### For installation from sources

- ✅ Python 3.8 or higher (3.12 recommended)

---

### 📦 Detailed Installation from Git

#### Step 1: Clone the repository

```bash
git clone <REPOSITORY_URL>
cd vigitrust-global/Tools/PCI-Scraper
```

#### Step 2: Create a virtual environment

**Why?** Isolates project dependencies from your system Python.

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: Install dependencies

**Option A: Automatic installation (recommended)**

Simply launch the application:
```bash
python app.py
```

Missing dependencies will be automatically detected and installed on first launch.

**Option B: Manual installation**

```bash
pip install -r requirements.txt
python app.py
```

#### Installed dependencies

| Package | Version | Usage |
|---------|---------|-------|
| Flask | 3.1.2 | Web server and REST API |
| Selenium | 4.36.0 | Dynamic scraping of PCI SSC website |
| webdriver-manager | 4.0.2 | Automatic browser driver management |
| pandas | 2.3.3 | Data manipulation and analysis |
| numpy | 2.3.3 | Numerical computing |
| PyPDF2 | 3.0.1 | Text extraction from PDF |

---

### 🏗️ Project Structure

```
vigitrust-global/Tools/PCI-Scraper/
│
├── app.py                          # Flask entry point
├── requirements.txt                # Python dependencies
├── start.bat                       # Quick launch (Windows)
│
├── pci_change_scraper/             # Scraper module
│   ├── pci_scraper.py              # Scraping logic
│   ├── pci_documents.csv           # Current state of documents
│   ├── changes.json                # Latest detected changes
│   ├── historic.json               # Complete history
│   └── pci_documents_backup_*.csv  # Automatic backups
│
├── new_pci_pdf_extractor/          # PDF extractor module
│   ├── pdf_extractor_EN.py         # English extractor
│   └── pdf_extractor_FR.py         # French extractor
│
└── templates/                      # Web interface
    ├── index.html                  # Home page
    ├── styles.css                  # Global styles
    ├── animations.js               # Animations
    │
    ├── change/                     # Change detection module
    │   ├── index.html
    │   ├── historic.html
    │   ├── styles.css
    │   ├── changes.js
    │   └── historic.js
    │
    ├── converter2/                 # PDF extraction module
    │   ├── index.html
    │   ├── styles.css
    │   └── converter.js
    │
    └── automation/                 # Automation module (future)
        ├── index.html
        ├── styles.css
        └── automation.js
```

#### Build files (for developers only)

```
├── app_windows.spec                # PyInstaller configuration
├── build_windows.bat               # Windows build script
│
├── venv/                           # Virtual environment (not versioned)
├── build_env_win/                  # Build environment (not versioned)
├── build/                          # PyInstaller temp files (not versioned)
├── dist/                           # Compiled executable (not versioned)
└── __pycache__/                    # Python cache (not versioned)
```

---

### 🖥️ Usage

#### Launch the application

**Method 1: Python**
```bash
python app.py
```

**Method 2: Windows batch script**
```bash
start.bat
```

**Method 3: Executable**
```bash
dist\PCITools.exe
```

The application starts on **http://localhost:5001** and automatically opens your browser.

#### Web interface

##### Home page (`/`)
Navigation to the 3 main modules.

##### Change Detection Module (`/change`)

**Function**: Scrapes the PCI SSC website and detects document changes.

**Usage:**
1. Click on "Launch scraper"
2. The scraper analyzes the website in real-time (progress displayed)
3. Changes are detected by comparison with `pci_documents.csv`
4. Results saved in `changes.json` and `historic.json`

**Types of changes detected:**
- Newly published documents
- Updated versions
- Retired documents

##### Change History (`/historic`)

**Function**: Displays the complete history of all changes.

**Features:**
- Filtering by type (new / updated / retired)
- Chronological view with timestamps
- Exportable data

##### PDF Extractor (`/converter2`)

**Function**: Extracts structured requirements from PCI DSS PDFs.

**Usage:**
1. Select language (EN or FR)
2. (Optional) Upload a custom PDF
3. Click on "Launch extraction"
4. Results exportable in JSON or CSV

#### REST API

**Base URL**: `http://localhost:5001/api`

##### Scraping Endpoints

| Method | Endpoint | Description | Response |
|---------|----------|-------------|---------|
| GET | `/documents` | List of current PCI documents | JSON array |
| POST | `/run-scraper` | Launches scraper in background | `{status: "started"}` |
| GET | `/scraper-status` | Scraper status | `{status: "running\|completed\|error"}` |
| GET | `/changes` | Latest detected changes | JSON array |
| GET | `/historic` | Complete history | JSON array |

##### PDF Extraction Endpoints

| Method | Endpoint | Description | Parameters |
|---------|----------|-------------|------------|
| POST | `/run-pdf-extractor` | Launch extraction | `language` (EN/FR), `file` (PDF, optional) |
| GET | `/pdf-extractor-results/<lang>` | Retrieve results | `lang` = EN or FR |
| GET | `/download-pdf-results/<lang>/csv` | Download CSV | `lang` = EN or FR |

**Example usage with curl:**

```bash
# Launch scraper
curl -X POST http://localhost:5001/api/run-scraper

# Check status
curl http://localhost:5001/api/scraper-status

# Retrieve changes
curl http://localhost:5001/api/changes
```

---

### 🔨 Building the Windows Executable

**For developers only** - Create a standalone .exe executable

#### Prerequisites

- **Python 3.12** (PyInstaller 6.16.0 does not support Python 3.13)
- Windows 10/11

Check your version:
```bash
py -3.12 --version
```

#### Automatic build

```bash
build_windows.bat
```

**What the script does:**
1. Verifies Python 3.12
2. Creates a temporary virtual environment `build_env_win`
3. Installs all dependencies + PyInstaller
4. Compiles with PyInstaller according to `app_windows.spec`
5. Generates `dist/PCITools.exe` (~100 MB)

#### Manual build

```bash
# 1. Python 3.12 virtual environment
py -3.12 -m venv build_env_win
.\build_env_win\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Compile
pyinstaller app_windows.spec --clean
```

#### Result

- **File**: `dist/PCITools.exe`
- **Size**: ~100 MB
- **Content**: Python 3.12 + all dependencies + templates + scripts
- **Distribution**: Share only the .exe, no installer needed

#### Important

- The `dist/` folder is **NOT versioned** in Git (see `.gitignore`)
- The executable is **Windows-specific** (recompile on Linux/Mac for those OS)
- Requires **Python 3.12** for build (not 3.13)

---

### Architecture

**Pattern**: Flask MVC (Model-View-Controller)

- **Model**: `pci_change_scraper/`, `new_pci_pdf_extractor/`
- **View**: `templates/` (HTML/CSS/JS)
- **Controller**: `app.py` (Flask routes)

**Technical specificities:**
- Auto-installation of dependencies at startup (dev mode only, not in .exe)
- Scraping in separate thread to avoid blocking Flask
- PyInstaller support with dynamic paths (`sys._MEIPASS` in frozen mode)
- Automatic cleanup of temporary CSVs after 1h

---

### 🐛 Troubleshooting

#### Application won't start

**Check Python:**
```bash
python --version  # Must be >= 3.8
```

**Check Internet connection:**
Automatic installation requires Internet.

**Install manually:**
```bash
pip install -r requirements.txt
python app.py
```

**Check logs:**
Error messages display in the console.

---

#### "Module not found" or ImportError

**Cause**: Dependency not properly installed.

**Solution:**
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

---

#### Scraper doesn't work

**Selenium/ChromeDriver error:**

1. Verify that **Chrome or Edge is installed**
2. Check your **firewall** (allow Python)
3. Check your **Internet connection**
4. Restart the scraper via the interface

**The PCI SSC website may be temporarily unavailable.**

---

#### Build fails

**Clean and restart:**
```bash
rmdir /s /q build dist build_env_win
py -3.12 --version  # Check version
build_windows.bat
```

**Common error**: PyInstaller 6.16.0 does **NOT support Python 3.13**. Use Python 3.12.

---

### 📚 Technologies

| Category | Technology | Version | Usage |
|-----------|-------------|---------|-------|
| **Backend** | Flask | 3.1.2 | Python web framework |
| | Python | 3.8+ | Language (3.12 recommended) |
| **Scraping** | Selenium | 4.36.0 | Browser automation |
| | webdriver-manager | 4.0.2 | Driver management |
| **Data** | pandas | 2.3.3 | Data manipulation |
| | numpy | 2.3.3 | Numerical computing |
| | PyPDF2 | 3.0.1 | PDF extraction |
| **Build** | PyInstaller | 6.16.0 | Executable creation |
| **Frontend** | HTML5/CSS3 | - | Interface |
| | JavaScript | ES6+ | Client logic |

---

### 📄 License

**Internal Vigitrust use only**

This project is proprietary and intended for internal use by Vigitrust teams.

---

### 👥 Support

**Author**: Thomas Mionnet
**Organization**: Vigitrust
**Version**: 2.0
**Last update**: October 2025
**Compatibility**: Windows 10/11, Linux, Mac (Python 3.8-3.12)

---
---

<a id="français"></a>
## Français

### Description

Suite d'outils pour la gestion et le suivi des documents PCI DSS (Payment Card Industry Data Security Standard) et SAQ (Self-Assessment Questionnaire).

Application web Flask permettant de :
- **Détecter automatiquement** les changements sur le site officiel PCI Security Standards Council
- **Extraire et structurer** les requirements depuis les PDF PCI DSS (anglais et français)
- **Suivre l'historique** de toutes les modifications détectées
- **Exposer une API REST** pour l'automatisation

---

## 🚀 Démarrage rapide

### Vous avez reçu l'exécutable `PCITools.exe` ?

**Simple et autonome** - Aucune installation nécessaire :

1. Double-cliquez sur `PCITools.exe`
2. Le navigateur s'ouvre automatiquement sur http://localhost:5001

**Prérequis minimum :**
- Windows 10 ou 11
- Chrome ou Edge (pour le scraping web)

> **Note** : L'exécutable contient Python et toutes les dépendances. Aucune installation Python n'est requise.

---

## 📋 Prérequis

### Pour l'exécutable Windows

- ✅ Windows 10/11
- ✅ Chrome ou Edge installé
- ✅ Connexion Internet (pour scraper le site PCI SSC)
- ❌ **PAS besoin de Python**

### Pour l'installation depuis les sources

- ✅ Python 3.8 ou supérieur (3.12 recommandé)

---

## 📦 Installation détaillée depuis Git

### Étape 1 : Cloner le dépôt

```bash
git clone <URL_DU_DEPOT>
cd vigitrust-global/Tools/PCI-Scraper
```

### Étape 2 : Créer un environnement virtuel

**Pourquoi ?** Isole les dépendances du projet de votre système Python.

**Windows :**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**Linux/Mac :**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Étape 3 : Installer les dépendances

**Option A : Installation automatique (recommandée)**

Lancez simplement l'application :
```bash
python app.py
```

Les dépendances manquantes seront détectées et installées automatiquement au premier lancement.

**Option B : Installation manuelle**

```bash
pip install -r requirements.txt
python app.py
```

### Dépendances installées

| Package | Version | Usage |
|---------|---------|-------|
| Flask | 3.1.2 | Serveur web et API REST |
| Selenium | 4.36.0 | Scraping dynamique du site PCI SSC |
| webdriver-manager | 4.0.2 | Gestion automatique des drivers navigateur |
| pandas | 2.3.3 | Manipulation et analyse de données |
| numpy | 2.3.3 | Calculs numériques |
| PyPDF2 | 3.0.1 | Extraction de texte depuis PDF |

---

## 🏗️ Structure du projet

```
vigitrust-global/Tools/PCI-Scraper/
│
├── app.py                          # Point d'entrée Flask
├── requirements.txt                # Dépendances Python
├── start.bat                       # Lancement rapide (Windows)
│
├── pci_change_scraper/             # Module scraper
│   ├── pci_scraper.py              # Logique de scraping
│   ├── pci_documents.csv           # État actuel des documents
│   ├── changes.json                # Derniers changements détectés
│   ├── historic.json               # Historique complet
│   └── pci_documents_backup_*.csv  # Sauvegardes automatiques
│
├── new_pci_pdf_extractor/          # Module extracteur PDF
│   ├── pdf_extractor_EN.py         # Extracteur anglais
│   └── pdf_extractor_FR.py         # Extracteur français
│
└── templates/                      # Interface web
    ├── index.html                  # Page d'accueil
    ├── styles.css                  # Styles globaux
    ├── animations.js               # Animations
    │
    ├── change/                     # Module détection changements
    │   ├── index.html
    │   ├── historic.html
    │   ├── styles.css
    │   ├── changes.js
    │   └── historic.js
    │
    ├── converter2/                 # Module extraction PDF
    │   ├── index.html
    │   ├── styles.css
    │   └── converter.js
    │
    └── automation/                 # Module automation (futur)
        ├── index.html
        ├── styles.css
        └── automation.js
```

### Fichiers de build (pour développeurs uniquement)

```
├── app_windows.spec                # Configuration PyInstaller
├── build_windows.bat               # Script de compilation Windows
│
├── venv/                           # Environnement virtuel (non versionné)
├── build_env_win/                  # Environnement de build (non versionné)
├── build/                          # Fichiers temporaires PyInstaller (non versionné)
├── dist/                           # Exécutable compilé (non versionné)
└── __pycache__/                    # Cache Python (non versionné)
```

---

## 🖥️ Utilisation

### Lancer l'application

**Méthode 1 : Python**
```bash
python app.py
```

**Méthode 2 : Script batch Windows**
```bash
start.bat
```

**Méthode 3 : Exécutable**
```bash
dist\PCITools.exe
```

L'application démarre sur **http://localhost:5001** et ouvre automatiquement votre navigateur.

### Interface web

#### Page d'accueil (`/`)
Navigation vers les 3 modules principaux.

#### Module Détection de changements (`/change`)

**Fonction** : Scrape le site PCI SSC et détecte les modifications de documents.

**Utilisation :**
1. Cliquez sur "Lancer le scraper"
2. Le scraper analyse le site en temps réel (progression affichée)
3. Les changements sont détectés par comparaison avec `pci_documents.csv`
4. Résultats enregistrés dans `changes.json` et `historic.json`

**Types de changements détectés :**
- Nouveaux documents publiés
- Versions mises à jour
- Documents retirés

#### Historique des modifications (`/historic`)

**Fonction** : Affiche l'historique complet de tous les changements.

**Fonctionnalités :**
- Filtrage par type (nouveau / mis à jour / retiré)
- Vue chronologique avec horodatage
- Export possible des données

#### Extracteur PDF (`/converter2`)

**Fonction** : Extrait les requirements structurés depuis les PDF PCI DSS.

**Utilisation :**
1. Sélectionnez la langue (EN ou FR)
2. (Optionnel) Uploadez un PDF personnalisé
3. Cliquez sur "Lancer l'extraction"
4. Résultats exportables en JSON ou CSV

### API REST

**Base URL** : `http://localhost:5001/api`

#### Endpoints - Scraping

| Méthode | Endpoint | Description | Réponse |
|---------|----------|-------------|---------|
| GET | `/documents` | Liste des documents PCI actuels | JSON array |
| POST | `/run-scraper` | Lance le scraper en arrière-plan | `{status: "started"}` |
| GET | `/scraper-status` | Statut du scraper | `{status: "running\|completed\|error"}` |
| GET | `/changes` | Derniers changements détectés | JSON array |
| GET | `/historic` | Historique complet | JSON array |

#### Endpoints - Extraction PDF

| Méthode | Endpoint | Description | Paramètres |
|---------|----------|-------------|------------|
| POST | `/run-pdf-extractor` | Lance l'extraction | `language` (EN/FR), `file` (PDF, optionnel) |
| GET | `/pdf-extractor-results/<lang>` | Récupère les résultats | `lang` = EN ou FR |
| GET | `/download-pdf-results/<lang>/csv` | Télécharge le CSV | `lang` = EN ou FR |

**Exemple d'utilisation avec curl :**

```bash
# Lancer le scraper
curl -X POST http://localhost:5001/api/run-scraper

# Vérifier le statut
curl http://localhost:5001/api/scraper-status

# Récupérer les changements
curl http://localhost:5001/api/changes
```

---

## 🔨 Compiler l'exécutable Windows

**Pour les développeurs uniquement** - Créer un exécutable autonome .exe

### Prérequis

- **Python 3.12** (PyInstaller 6.16.0 ne supporte pas Python 3.13)
- Windows 10/11

Vérifiez votre version :
```bash
py -3.12 --version
```

### Compilation automatique

```bash
build_windows.bat
```

**Ce que fait le script :**
1. Vérifie Python 3.12
2. Crée un environnement virtuel temporaire `build_env_win`
3. Installe toutes les dépendances + PyInstaller
4. Compile avec PyInstaller selon `app_windows.spec`
5. Génère `dist/PCITools.exe` (~100 MB)


### Compilation manuelle

```bash
# 1. Environnement virtuel Python 3.12
py -3.12 -m venv build_env_win
.\build_env_win\Scripts\activate

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Compiler
pyinstaller app_windows.spec --clean
```

### Résultat

- **Fichier** : `dist/PCITools.exe`
- **Taille** : ~100 MB
- **Contenu** : Python 3.12 + toutes dépendances + templates + scripts
- **Distribution** : Partagez uniquement le .exe, aucun installeur nécessaire

### Important

- Le dossier `dist/` **n'est PAS versionné** dans Git (voir `.gitignore`)
- L'exécutable est **spécifique à Windows** (recompiler sur Linux/Mac pour ces OS)
- Nécessite **Python 3.12** pour le build (pas 3.13)

---

### Architecture

**Pattern** : Flask MVC (Model-View-Controller)

- **Modèle** : `pci_change_scraper/`, `new_pci_pdf_extractor/`
- **Vue** : `templates/` (HTML/CSS/JS)
- **Contrôleur** : `app.py` (routes Flask)

**Particularités techniques :**
- Installation auto des dépendances au démarrage (mode dev uniquement, pas dans le .exe)
- Scraping en thread séparé pour ne pas bloquer Flask
- Support PyInstaller avec chemins dynamiques (`sys._MEIPASS` en mode frozen)
- Nettoyage automatique des CSV temporaires après 1h

---

## 🐛 Dépannage

### L'application ne démarre pas

**Vérifier Python :**
```bash
python --version  # Doit être >= 3.8
```

**Vérifier la connexion Internet :**
L'installation automatique nécessite Internet.

**Installer manuellement :**
```bash
pip install -r requirements.txt
python app.py
```

**Consulter les logs :**
Les messages d'erreur s'affichent dans la console.

---

### Erreur "Module not found" ou ImportError

**Cause** : Dépendance mal installée.

**Solution :**
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

---

### Le scraper ne fonctionne pas

**Erreur Selenium/ChromeDriver :**

1. Vérifiez que **Chrome ou Edge est installé**
2. Vérifiez votre **pare-feu** (autoriser Python)
3. Vérifiez votre **connexion Internet**
4. Relancez le scraper via l'interface

**Le site PCI SSC peut être temporairement indisponible.**

---

### Le build échoue

**Nettoyer et recommencer :**
```bash
rmdir /s /q build dist build_env_win
py -3.12 --version  # Vérifier version
build_windows.bat
```

**Erreur courante** : PyInstaller 6.16.0 ne supporte **PAS Python 3.13**. Utilisez Python 3.12.


---

## 📚 Technologies

| Catégorie | Technologie | Version | Usage |
|-----------|-------------|---------|-------|
| **Backend** | Flask | 3.1.2 | Framework web Python |
| | Python | 3.8+ | Langage (3.12 recommandé) |
| **Scraping** | Selenium | 4.36.0 | Automatisation navigateur |
| | webdriver-manager | 4.0.2 | Gestion drivers |
| **Data** | pandas | 2.3.3 | Manipulation données |
| | numpy | 2.3.3 | Calculs numériques |
| | PyPDF2 | 3.0.1 | Extraction PDF |
| **Build** | PyInstaller | 6.16.0 | Création exécutables |
| **Frontend** | HTML5/CSS3 | - | Interface |
| | JavaScript | ES6+ | Logique client |

---

## 📄 Licence

**Usage interne Vigitrust uniquement**

Ce projet est propriétaire et destiné à un usage interne par les équipes Vigitrust.

---

## 👥 Support

**Auteur** : Thomas Mionnet
**Organisation** : Vigitrust
**Version** : 2.0
**Dernière mise à jour** : Octobre 2025
**Compatibilité** : Windows 10/11, Linux, Mac (Python 3.8-3.12)

