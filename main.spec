# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['can.py'],
             pathex=['F:\\李翔鹏\\任务交接\\任务交接\\代码\\源码\\EOL\\标定_250K_Dev_v2.2'],
             binaries=[],
             datas=[('ControlCAN.dll', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
			 
			 
exe1 = EXE(pyz,
          a.scripts,
          a.binaries,                          ###!!!注意点2
          a.zipfiles,                          ###!!!注意点2
          a.datas,                             ###!!!注意点2
          [],
          exclude_binaries=False,   ###!!!注意点3：这里是False
          name='can',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False)
			 
exe2 = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='can',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
		  
coll = COLLECT(exe2,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='can')
