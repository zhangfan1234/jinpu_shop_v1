# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main_ui.py'],
    pathex=[],
    binaries=[],
    datas=[('config', 'config'), ('utils', 'utils'), ('scripts', 'scripts'), ('闲鱼管家类目.txt', '.'), ('./utils/闲鱼管家类目.txt', './utils')],
    hiddenimports=['PySide6.QtWidgets', 'PySide6.QtCore', 'PySide6.QtGui', 'pandas', 'openpyxl', 'DrissionPage'],
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
    name='商品上传工具',
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
    icon=['icon.png'],
)
