@echo off
REM Script de build pour Windows
REM Executer ce fichier sur une machine Windows

echo ============================================
echo Build de PCITools pour Windows
echo ============================================
echo.

REM Vérifier Python 3.12
echo [1/6] Verification de Python 3.12...
py -3.12 --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python 3.12 n'est pas installe!
    echo PyInstaller ne supporte pas encore Python 3.13
    echo Telechargez Python 3.12 depuis: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Créer un environnement virtuel avec Python 3.12
echo [2/6] Creation de l'environnement virtuel avec Python 3.12...
py -3.12 -m venv build_env_win

REM Mettre à jour pip
echo.
echo [3/6] Mise a jour de pip...
build_env_win\Scripts\python.exe -m pip install --upgrade pip

REM Installer les dépendances
echo.
echo [4/6] Installation des dependances...
build_env_win\Scripts\pip.exe install -r requirements.txt

REM Compiler l'exécutable
echo.
echo [5/6] Compilation de l'executable...
build_env_win\Scripts\pyinstaller.exe app_windows.spec --clean

REM Nettoyage optionnel de l'environnement de build
echo.
echo [6/6] Nettoyage (optionnel)...
echo Pour supprimer l'environnement de build et gagner de l'espace:
echo   rmdir /s /q build_env_win
echo   rmdir /s /q build

echo.
echo ============================================
echo Build termine!
echo L'executable se trouve dans: dist\PCITools.exe
echo ============================================
echo.

pause
