# -*- mode: python ; coding: utf-8 -*-
import os
import glob
import sys
from PyInstaller.utils.hooks import collect_all

datas = [('VirtualRadiosonde/core', 'core'), ('VirtualRadiosonde/ui', 'ui'), ('VirtualRadiosonde/assets', 'assets')]
binaries = []
hiddenimports = [
    'pyexpat', 'xml.parsers.expat', 'plistlib',
    'ctypes', '_ctypes', 'tempfile'
]

# Comprehensive dynamic discovery of Python C extensions (.pyd) and Conda DLLs
py_dir = os.path.dirname(sys.executable)

# 1. Collect all standard C-extension .pyd files (pyexpat, _ctypes, _ssl, _sqlite3, etc.)
dlls_dir = os.path.join(py_dir, 'DLLs')
if os.path.exists(dlls_dir):
    for pyd_file in glob.glob(os.path.join(dlls_dir, '*.pyd')):
        binaries.append((pyd_file, '.'))

# 2. Collect core dependency DLLs from Conda Library/bin (libexpat, expat, ffi, zlib, etc.)
lib_bin_dir = os.path.join(py_dir, 'Library', 'bin')
if os.path.exists(lib_bin_dir):
    for dll_file in glob.glob(os.path.join(lib_bin_dir, '*.dll')):
        base_name = os.path.basename(dll_file).lower()
        if any(keyword in base_name for keyword in ['expat', 'ffi', 'zlib', 'bz2', 'sqlite', 'ssl', 'crypto']):
            binaries.append((dll_file, '.'))

tmp_ret = collect_all('metpy')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('matplotlib')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pint')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['VirtualRadiosonde\\app.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PyQt6', 'PyQt5', 'PySide2',
        'tensorflow', 'torch', 'xgboost', 'sklearn',
        'IPython', 'jupyter', 'notebook', 'tkinter', 'PIL._tkinter_finder'
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='VirtualRadiosondePlotter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VirtualRadiosondePlotter',
)
