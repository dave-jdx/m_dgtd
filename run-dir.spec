# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

datas = [
    ('./icons/*.*','icons'),
    ('./stylesheets/*.*','stylesheets'),
    ('./stylesheets/gray/*.*','stylesheets/gray'),
        ]
datas += collect_data_files('debugpy')
datas += collect_data_files('spyder')
datas += collect_data_files('Crypto')

block_cipher = None


run_a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['Crypto'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
run_pyz = PYZ(run_a.pure, run_a.zipped_data, cipher=block_cipher)

exe = EXE(
    run_pyz,
    run_a.scripts,
    [],
    exclude_binaries=True,
    name='app',
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
    icon='icons/logo_xidian.png'
)

coll = COLLECT(
    exe,
    run_a.binaries,
    run_a.zipfiles,
    run_a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='app',
)