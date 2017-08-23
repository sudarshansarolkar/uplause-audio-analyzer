import sys, os, traceback
from cx_Freeze import setup, Executable
import subprocess
import time
from shutil import copyfile, rmtree
import scipy
includefiles_list=[]
scipy_path = os.path.dirname(scipy.__file__)
#scipy_path = os.path.join(scipy_path, "signal")
includefiles_list.append(scipy_path)

print("Scipy path: " + scipy_path)

from cx_Freeze import hooks

def load_scipy_patched(finder, module):
    """the scipy module loads items within itself in a way that causes
        problems without the entire package and a number of other subpackages
        being present."""
    finder.IncludePackage("scipy._lib")  # Changed include from scipy.lib to scipy._lib
    finder.IncludePackage("scipy.misc")

hooks.load_scipy = load_scipy_patched

# set TCL_LIBRARY=C:\Program Files (x86)\Python35-32\tcl\tcl8.6
# set TK_LIBRARY=C:\Program Files (x86)\Python35-32\tcl\tk8.6

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"build_exe":"build",
#"include_files": os.path.join(scipy_path, "special/_ufuncs.pyd"),
"packages": ["os", "numpy", "scipy", "tkinter"],
#"path": ["C:\Python34\Lib\site-packages\scipy"],
#"include_files": includefiles_list,
#"excludes": ["tkinter"],
#"optimize": 2
}
#"include_files": [(sys.executable[:-10] + '\\Lib\\site-packages\\scipy\\special\\_ufuncs.pyd','_ufuncs.pyd')]}


# GUI applications require a different base on Windows (the default is for a
# console application).
base = 'Console'
#if sys.platform == "win32":
#    base = "Win32GUI"
#if sys.platform == "win32":
#    base = "Win32GUI"

date = time.strftime("%d.%m.%Y")

hg_hash = "Couldn't call to hg or not a hg repo"

try:
    hg_hash = subprocess.check_output(["hg", "id", "-i"]).decode("utf-8").strip()
except:
    pass

if not os.path.exists("build"):
    os.makedirs("build")

f = open('build_version_string','w')
f.write("Built: " + date + " (commit: " + hg_hash + ")\n") # python will convert \n to os.linesep
f.close() # you can omit in most cases as the destructor will call it

copyfile('build_version_string', 'build/build_version_string')

setup(  name = "Sound Analyzer 2.0",
        version = "1.99",
        description = "Sound Analyzer",
        options = {"build_exe": build_exe_options},
        executables = [Executable("main.py", base=base, targetName="SoundAnalyzer.exe"), Executable("test.py", base=base, targetName="SoundATester.exe")])

# Remove unneeded scipy files
dirs_to_remove = []

for scipy_dir in dirs_to_remove:
    rmtree("build/scipy/" + scipy_dir)