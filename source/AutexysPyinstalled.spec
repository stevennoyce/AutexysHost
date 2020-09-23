# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['manager.py'],
             pathex=['/Users/jaydoherty/Documents/myWorkspaces/Research/Autexys/AutexysHost/source'],
             binaries=[],
             datas=[
             		('/Users/jaydoherty/Documents/myWorkspaces/Research/Autexys/AutexysHost/source/README.md','.'),
             		('/Users/jaydoherty/Documents/myWorkspaces/Research/Autexys/AutexysHost/source/ui','ui'),
             		('/Users/jaydoherty/Documents/myWorkspaces/Research/Autexys/AutexysHost/source/procedures','procedures'),
                    ('/Users/jaydoherty/Documents/myWorkspaces/Research/Autexys/AutexysHost/source/utilities/PlotDefinitions/GateSweep', 'utilities/PlotDefinitions/GateSweep'),
                    ('/Users/jaydoherty/Documents/myWorkspaces/Research/Autexys/AutexysHost/source/utilities/PlotDefinitions/DrainSweep', 'utilities/PlotDefinitions/DrainSweep'),
                    ('/Users/jaydoherty/Documents/myWorkspaces/Research/Autexys/AutexysHost/source/utilities/PlotDefinitions/StaticBias', 'utilities/PlotDefinitions/StaticBias'),
                    ('/Users/jaydoherty/Documents/myWorkspaces/Research/Autexys/AutexysHost/source/utilities/PlotDefinitions/RapidBias', 'utilities/PlotDefinitions/RapidBias'),
                    ('/Users/jaydoherty/Documents/myWorkspaces/Research/Autexys/AutexysHost/source/utilities/PlotDefinitions/Inverter',  'utilities/PlotDefinitions/Inverter'),
                    ('/Users/jaydoherty/Documents/myWorkspaces/Research/Autexys/AutexysHost/source/utilities/PlotDefinitions/Metrics',   'utilities/PlotDefinitions/Metrics'),
                    ('/Users/jaydoherty/Documents/myWorkspaces/Research/Autexys/AutexysHost/source/utilities/PlotDefinitions/Chip',      'utilities/PlotDefinitions/Chip'),
                    ],
             hiddenimports=['engineio.async_gevent'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='AutexysPyinstalled',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='AutexysPyinstalled')
