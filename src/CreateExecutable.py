### SHOCKFISH ##
# By MEMESCOEP


## IMPORTS ##
from datetime import datetime
import subprocess
import platform
import Globals
import shutil
import sys
import os


## VARIABLES ##
RemoveBuildDirAfterCompile = True
WinBuildWithConsole = False
RemoveCompileDirs = True
CreateSpecFile = True
BuildStartTime = datetime.now()
CurrentCWDPath = os.getcwd()
BuildSpecPath = os.path.join(CurrentCWDPath, "Shockfish.spec")
PythonEXEPath = os.path.abspath(sys.executable)
BuildDirPath = os.path.join(CurrentCWDPath, "Build")
DistDirPath = os.path.join(CurrentCWDPath, "Dist")
UPXProgPath = os.path.join(CurrentCWDPath, f"UPX{Globals.PathSeparator}upx")
EXEIconPath = os.path.join(CurrentCWDPath, f"UI{Globals.PathSeparator}Icon.bmp")
GenSpecTree = "    Tree('UI/', prefix='UI/'),\n"
EXEFilename = "Shockfish"
UPXCommand = [UPXProgPath, "-9", "-v", os.path.join(BuildDirPath, EXEFilename)]
GenSpecCMD = [
    "--onefile",
    "--name=Shockfish",
    "--optimize=2",
    "--add-data=UI/*:UI",
    "--collect-all=Pillow",
    "Main.py",
]

BuildCMD = [
    PythonEXEPath,
    "-m",
    "PyInstaller",
    "--clean",
    f"--workpath={BuildDirPath}",
    f"--distpath={DistDirPath}",
    BuildSpecPath,
]

ExitCode = 0


## FUNCTIONS ##
def RunProcess(ProcessArgList):
    NewProcess = subprocess.Popen(ProcessArgList)

    NewProcess.wait()
    print()
    return NewProcess.returncode


## MAIN CODE ##
if __name__ == "__main__":
    try:
        print("[== SHOCKFISH COMPILER ==]")
        print(f"[INFO] >> Running on \"{platform.system()} {platform.release()}, {platform.version()} ({platform.architecture()[0]})\".")
        print(f"[INFO] >> The Windows console will be {"enabled" if WinBuildWithConsole == True else "disabled"}.")

        # Make sure a valid path for PyInstaller's pyi-makespec executable is provided via command line arguments
        if len(sys.argv) < 2 or os.path.exists(sys.argv[1]) == False or os.path.isdir(sys.argv[1]) == True:
            print("[ERROR] >> The path for pyi-makespec was not specified as a CMD argument, or it is invalid.")
            sys.exit(-999)

        GenSpecCMD.insert(0, sys.argv[1])

        # Specify an splash screen image's path, and if supported (Windows, MacOS), add a file icon
        if platform.system() != "Windows":
            GenSpecCMD.insert(len(GenSpecCMD) - 1, f"--splash={EXEIconPath}") #.split(CurrentCWDPath)[1].removeprefix("/")

            if platform.system() == "Darwin":
                GenSpecCMD.insert(len(GenSpecCMD) - 1, f"--icon={EXEIconPath.replace("bmp", "icns")}")

        else:
            GenSpecCMD.insert(len(GenSpecCMD) - 1, f"--splash={EXEIconPath}")
            GenSpecCMD.insert(len(GenSpecCMD) - 1, f"--icon={EXEIconPath.replace("bmp", "ico")}")

        print(f"[INFO] >> Build started at {BuildStartTime}")
        print(f"[INFO] >> Python executable path is \"{PythonEXEPath}\".")
        print(f"[INFO] >> Path of pyi-makespec is \"{sys.argv[1]}\".")
        print(f"[INFO] >> Build directory is \"{BuildDirPath}\".")
        print(f"[INFO] >> EXE file name is \"{EXEFilename}\".")
        print(f"[INFO] >> UPX abspath is \"{UPXProgPath}\".")

        # Remove PyInstaller's build directories if RemoveCompileDirs is true
        if RemoveCompileDirs == True:
            print(f"[INFO] >> Removing build directory \"{BuildDirPath}\"...")
            shutil.rmtree(BuildDirPath, ignore_errors=True)

            print(f"[INFO] >> Removing dist directory \"{DistDirPath}\"...")
            shutil.rmtree(DistDirPath, ignore_errors=True)
        
        if os.path.exists(BuildSpecPath) == False:
            print(f"[WARN] >> Spec file \"{BuildSpecPath}\" doesn't exist, it will be created now.")
            CreateSpecFile = True

        elif os.path.isdir(BuildSpecPath) == True:
            print(f"[ERROR] >> The spec file \"{BuildSpecPath}\" exists, but it is a directory. This folder could have user data in it, so to prevent data loss the build will be stopped.")
            sys.exit(-998)

        # Create a spec file that describes how the application should be created; only runs if CreateSpecFile is true, or if the spec file isn't found
        if CreateSpecFile == True:
            print("[INFO] >> Generating SPEC file before building...")
            ExitCode = RunProcess(GenSpecCMD)

            assert ExitCode == 0, f"A step returned a non-zero exite code of {ExitCode}"
            with open("Shockfish.spec", "r+") as SpecFile:
                SpecData = SpecFile.readlines()

                for Line in SpecData:
                    if Line.lstrip().startswith("a.binaries,"):
                        SpecData.insert(SpecData.index(Line) + 1, GenSpecTree)
                        break

                SpecFile.seek(0)
                SpecFile.writelines(SpecData)


        assert ExitCode == 0, f"A step returned a non-zero exite code of {ExitCode}"
        print(f"[INFO] >> Running build command \"{BuildCMD}\".")
        ExitCode = RunProcess(BuildCMD)

        assert ExitCode == 0, f"A step returned a non-zero exite code of {ExitCode}"

        if os.path.exists(UPXProgPath) == True:
            print(f"[INFO] >> Running UPX command \"{UPXCommand}\".")
            ExitCode = RunProcess(UPXCommand)

        else:
            print(f"[WARN] >> UPX was not found at \"{UPXProgPath}\", so it will be skipped.")

        if RemoveBuildDirAfterCompile == True:
            shutil.rmtree(BuildDirPath)

    except Exception as EX:
        print(f"[ERROR] >> Build failed: {EX}")

    print(f"[INFO] >> Total operation time: {datetime.now() - BuildStartTime}")
    print(f"[INFO] >> Exiting with code {ExitCode}...")
    sys.exit(ExitCode)