# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path

# Get the directory containing this spec file
spec_root = os.path.dirname(os.path.abspath(SPEC))
src_path = os.path.join(spec_root, 'src')

# Define all the modules we need to include
hidden_imports = [
    'ui',
    'ui.main_window',
    'ui.theme',
    'ui.settings_dialog',
    'ui.progress_dialog',
    'ui.drag_drop_list',
    'core',
    'core.settings_manager',
    'core.db_manager',
    'core.rom_scanner',
    'core.dat_processor',
    'core.scanned_roms_manager',
    'PyQt6.QtCore',
    'PyQt6.QtWidgets',
    'PyQt6.QtGui',
    'sqlite3',
    'xml.etree.ElementTree',
    'hashlib',
    'pathlib',
    'logging',
    'json',
    'configparser',
    'setuptools',
    'pkg_resources',
    'pkg_resources.extern',
    'pkg_resources.extern.packaging',
    'pkg_resources.extern.packaging.version',
    'pkg_resources.extern.packaging.specifiers',
    'pkg_resources.extern.packaging.requirements'
]

# Data files to include
datas = [
    (os.path.join(src_path, 'ui', 'flags'), 'ui/flags'),
    (os.path.join(src_path, 'ui', 'texture'), 'ui/texture')
]

a = Analysis(
    ['main.py'],
    pathex=[spec_root, src_path],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pkg_resources.py2_warn'],
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
    name='Romplestiltskin',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    distpath='build/windows',
)