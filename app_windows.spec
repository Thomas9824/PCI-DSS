# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Windows build

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('pci_change_scraper', 'pci_change_scraper'),
        ('new_pci_pdf_extractor', 'new_pci_pdf_extractor'),
    ],
    hiddenimports=[
        'flask',
        'selenium',
        'webdriver_manager',
        'pandas',
        'PyPDF2',
        'numpy',
        'threading',
        'webbrowser',
        'subprocess',
        'tempfile',
        'json',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PCITools',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
