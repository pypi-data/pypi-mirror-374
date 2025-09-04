# -*- mode: python ; coding: utf-8 -*-

import sys

block_cipher = None



live_plot_a = Analysis(
    ['../examples/live-plot.py'],
    pathex=[],
    binaries=[('C:\\Windows\\System32\\libusb-1.0.dll', '.')] if sys.platform.startswith('win32') else [],
    datas=[],
    hiddenimports=['usb'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['rth-append-path.py'],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

range_doppler_a = Analysis(
    ['../examples/range-doppler.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['rth-append-path.py'],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

fw_upgrade_a = Analysis(
    ['../examples/fw-upgrade.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['rth-append-path.py'],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

fast_plot_a = Analysis(
    ['../examples/fast-plot.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['rth-append-path.py'],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

live_plot_pyz = PYZ(live_plot_a.pure, live_plot_a.zipped_data, cipher=block_cipher)
range_doppler_pyz = PYZ(range_doppler_a.pure, range_doppler_a.zipped_data, cipher=block_cipher)
fw_upgrade_pyz = PYZ(fw_upgrade_a.pure, fw_upgrade_a.zipped_data, cipher=block_cipher)
fast_plot_pyz = PYZ(fast_plot_a.pure, fast_plot_a.zipped_data, cipher=block_cipher)

live_plot_exe = EXE(
    live_plot_pyz,
    live_plot_a.scripts,
    [],
    exclude_binaries=True,
    name='live-plot',
    icon='logo-quadrat-2-32x32.ico',
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
)

range_doppler_exe = EXE(
    range_doppler_pyz,
    range_doppler_a.scripts,
    [],
    exclude_binaries=True,
    name='range-doppler',
    icon='logo-quadrat-2-32x32.ico',
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
)

fw_upgrade_exe = EXE(
    fw_upgrade_pyz,
    fw_upgrade_a.scripts,
    [],
    exclude_binaries=True,
    name='fw-upgrade',
    icon='logo-quadrat-2-32x32.ico',
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
)

fast_plot_exe = EXE(
    fast_plot_pyz,
    fast_plot_a.scripts,
    [],
    exclude_binaries=True,
    name='fast-plot',
    icon='logo-quadrat-2-32x32.ico',
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
)

coll = COLLECT(
    live_plot_exe,
    live_plot_a.binaries,
    live_plot_a.zipfiles,
    live_plot_a.datas,
    range_doppler_exe,
    range_doppler_a.binaries,
    range_doppler_a.zipfiles,
    range_doppler_a.datas,
    fw_upgrade_exe,
    fw_upgrade_a.binaries,
    fw_upgrade_a.zipfiles,
    fw_upgrade_a.datas,
    fast_plot_exe,
    fast_plot_a.binaries,
    fast_plot_a.zipfiles,
    fast_plot_a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='x1000-examples',
)

