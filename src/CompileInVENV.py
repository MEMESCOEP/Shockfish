### SHOCKFISH ##
# By MEMESCOEP


## IMPORTS ##
import subprocess
import shutil
import venv
import sys
import os


## VARIABLES ##
CWD = os.getcwd()
ExecutableFileExtension = ".exe" if sys.platform == "win32" else ""
VENVActivatorExtension = ".bat" if sys.platform == "win32" else ""
VENVEXEDir = "Scripts" if sys.platform == "win32" else "bin"
DeleteVENV = False
VENVDir = os.path.join(CWD, "CompileVENV")


## MAIN CODE ##
if DeleteVENV == True:
    print(f"[INFO] >> Removing VENV at \"{VENVDir}\"...")
    shutil.rmtree(VENVDir)

print(f"[INFO] >> Creating VENV at \"{VENVDir}\"...")
venv.create(VENVDir, with_pip=True)

print("[INFO] >> Entering VENV...")
ActivationScriptPath = (os.path.join(VENVDir, VENVEXEDir, "activate")) + VENVActivatorExtension

if not os.path.exists(ActivationScriptPath):
    print(f"[ERROR] >> Activation script \"{ActivationScriptPath}\" wasn't found.")
    sys.exit(-999)

print("[INFO] >> Installing pip packages...")
subprocess.run([ActivationScriptPath], shell=True)
subprocess.run([os.path.join(VENVDir, VENVEXEDir, 'pip') + ExecutableFileExtension, 'install', '-r', os.path.join(CWD, "CompilerRequirements.txt"), '-r', os.path.join(CWD, "MainRequirements.txt")])

print("\n[INFO] >> Running compilation script...")
print(os.path.join(VENVDir, VENVEXEDir, 'python') + ExecutableFileExtension)
subprocess.run([
    os.path.join(VENVDir, VENVEXEDir, 'python') + ExecutableFileExtension,
    os.path.join(CWD, "CreateExecutable.py"),
    os.path.join(VENVDir, VENVEXEDir, 'pyi-makespec') + ExecutableFileExtension,
    os.path.join(VENVDir, VENVEXEDir, 'pyinstaller') + ExecutableFileExtension
])