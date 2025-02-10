### SHOCKFISH ##
# By MEMESCOEP


## IMPORTS ##
from datetime import datetime
import subprocess
import traceback
import platform
import shutil
import sys
import os


## VARIABLES ##
RemoveCompileDirs = True
BuildStartTime = datetime.now()
CurrentCWDPath = os.getcwd()
PythonEXEPath = os.path.abspath(sys.executable)
BuildDirPath = os.path.join(CurrentCWDPath, "Build")
DistDirPath = os.path.join(CurrentCWDPath, "Dist")
UPXProgPath = os.path.join(CurrentCWDPath, "UPX/upx")
EXEIconPath = os.path.join(CurrentCWDPath, "UI/Icon.bmp")
GenSpecTree = "    Tree('UI/', prefix='UI/'),\n"
EXEFilename = "Shockfish"
UPXCommand = [UPXProgPath, "-9", "-v", os.path.join(BuildDirPath, EXEFilename)]
CreateSpec = True
GenSpecCMD = [
    "pyi-makespec",
    "--onefile",
    "--name=Shockfish",
    "--optimize=2",
    "--add-data=UI/*:UI",
    "--collect-all=Pillow",
    f"--splash={EXEIconPath.split(CurrentCWDPath)[1].removeprefix("/")}",
    "Main.py",
]

BuildCMD = [
    PythonEXEPath,
    "-m",
    "PyInstaller",
    "--clean",
    f"--workpath={BuildDirPath}",
    f"--distpath={DistDirPath}",
    "Shockfish.spec",
]

ExitCode = 0
Debug = False


## FUNCTIONS ##
def RunProcess(ProcessArgList):
    try:
        NewProcess = subprocess.Popen(ProcessArgList)

        NewProcess.wait()

        assert NewProcess.returncode == 0, f"Build failed with exit code {NewProcess.returncode}."

    except Exception as EX:
        print(f"[ERROR] >> {EX}")

        if Debug == True:
            traceback.print_exc()

        print()
        return hex(id(EX))

    print()
    return 0


## MAIN CODE ##
if __name__ == "__main__":
    print("[== SHOCKFISH COMPILER ==]")
    print(f"[INFO] >> Running on \"{platform.version()}, {platform.system()} {platform.release()} ({platform.architecture()[0]})\".")

    if "debian" in platform.version().lower() or "ubuntu" in platform.version().lower():
        print("[INFO] >> Running on Debian or Ubuntu, checking for VENV...")
        
        if sys.prefix == sys.base_prefix:
            print("[ERROR] >> You are running this script on a Debian or Ubuntu system, but not in a virtual environment.\n  See https://nuitka.net/info/debian-dist-packages.html for more details.\n")
            sys.exit(-999)

    print(f"[INFO] >> Build started at {BuildStartTime}")
    print(f"[INFO] >> Python executable path is \"{PythonEXEPath}\".")
    print(f"[INFO] >> Build directory is \"{BuildDirPath}\".")
    print(f"[INFO] >> UPX abspath is \"{UPXProgPath}\".")
    print(f"[INFO] >> EXE file name is \"{EXEFilename}\".")

    match platform.system():
        case "Linux" | "Solaris" | "AIX" | "FreeBSD" | "Unix":
            print(f"[WARN] >> PyInstaller doesn't currently support setting an app icon on this platform (\"{platform.system()}\"). This is probably because most executables for this platform don't store icon data.")
            
        case "Windows":
            BuildCMD.append(f"--icon={EXEIconPath}")

        case "Darwin":
            BuildCMD.append(f"--icon={EXEIconPath}")

        case _:
            print(f"[WARN] >> No icon support is available yet for this platform (\"{platform.system()}\").")

    if RemoveCompileDirs == True:
        print(f"[INFO] >> Removing build directory \"{BuildDirPath}\"...")
        shutil.rmtree(BuildDirPath, ignore_errors=True)

        print(f"[INFO] >> Removing dist directory \"{DistDirPath}\"...")
        shutil.rmtree(DistDirPath, ignore_errors=True)
    
    if CreateSpec == True:
        print("[INFO] >> Generating SPEC file before building...")
        ExitCode = RunProcess(GenSpecCMD)

        if ExitCode == 0:
            with open("Shockfish.spec", "r+") as SpecFile:
                SpecData = SpecFile.readlines()

                for Line in SpecData:
                    if Line.lstrip().startswith("a.binaries,"):
                        SpecData.insert(SpecData.index(Line) + 1, GenSpecTree)
                        break

                SpecFile.seek(0)
                SpecFile.writelines(SpecData)


    if ExitCode == 0:
        print(f"[INFO] >> Running build command \"{BuildCMD}\".")
        ExitCode = RunProcess(BuildCMD)

    if ExitCode == 0:
        if os.path.exists(UPXProgPath) == True:
            print(f"[INFO] >> Running UPX command \"{UPXCommand}\".")
            ExitCode = RunProcess(UPXCommand)

        else:
            print(f"[WARN] >> UPX was not found at \"{UPXProgPath}\", so it will be skipped.")

    print(f"[INFO] >> Total operation time: {datetime.now() - BuildStartTime}")
    print(f"[INFO] >> Exiting with code {ExitCode}...")
    sys.exit(ExitCode)