# PyInstaller spec for the BPI launcher.
# Build with:  pyinstaller build/bpi-launcher.spec   (run from project root on Windows)

# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

block_cipher = None

ROOT = Path(SPECPATH).parent  # project root

a = Analysis(
    [str(ROOT / 'src' / 'launcher' / 'app.py')],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        (str(ROOT / 'config' / 'scoring-weights.yaml'), 'config'),
    ],
    hiddenimports=[
        # Hub modules — pulled in via subprocess but PyInstaller
        # still needs to know they exist when the launcher imports them.
        'src.hub.db',
        'src.hub.ingest',
        'src.hub.recompute',
        'src.hub.watcher',
        'src.hub.dashboard',
        'src.hub.status',
        'src.main',
        'src.pipeline',
        'src.sources.rpdata_csv',
        'src.scoring.current_owner',
        'src.scoring.portfolio',
        'src.scoring.seller_lead',
        'src.scoring.rental_lead',
        'src.scoring.combined',
        'src.output.excel',
        'src.output.html_report',
        # Third-party imports that PyInstaller sometimes misses
        'watchdog.observers',
        'watchdog.observers.polling',
        'watchdog.events',
        'xlsxwriter',
        'jinja2',
        'yaml',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='bpi-launcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,        # windowed app — no console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
