import sys

from cx_Freeze import setup, Executable

build_exe_options = {"include_files":['data'],    
    #包含外围的ini、jpg文件，以及data目录下所有文件，以上所有的文件路径都是相对于cxsetup.py的路径。
    "packages": ["os","wx","matplotlib"],                #包含用到的包
    "includes": ["PIL","traceback"], 
    "path": sys.path}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

executable = Executable('windows.py', base=base)

setup(
        name = "windows",
        version = "0.2",
        description = "Check Image",
        options = {'build_exe': build_exe_options},
        executables = [executable])