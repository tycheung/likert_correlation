import sys
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

a = Analysis(
    ['likert_correlation/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('likert_correlation/templates', 'likert_correlation/templates'),
        ('likert_correlation/static', 'likert_correlation/static')
    ],
    hiddenimports=[
        'plotly',
        'pandas',
        'numpy',
        'scipy.stats',
        'openpyxl',
        'pystray',
        'PIL',
        'webbrowser',
        'requests'
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
    name='likert_analyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Changed to False to hide console
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='likert_correlation/static/icon.ico'
)